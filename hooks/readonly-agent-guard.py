#!/usr/bin/env python3
"""PreToolUse(Bash) guard enforcing the read-only agents' Bash contract.

Five agents (see READONLY_AGENTS) declare that they will not mutate the working
tree, the index, HEAD, branch state, or the worktree list. Their `tools:`
frontmatter already denies Write/Edit; nothing enforced the Bash half. This hook
does, by classifying the command and returning a `deny` decision for mutators.

Payloads without a guarded agent — the main session, `debugger`, `docs-writer`,
every built-in agent — are allowed untouched and as early as possible.

Design and rationale: specs/completed/readonly-agent-guard.md.

Runs under whatever `python3` is first on PATH (Python 3.9 on macOS system
Python), so keep this file 3.9-compatible: stdlib only, no `match`, and
annotations deferred via __future__.
"""
from __future__ import annotations

import json
import shlex
import sys

# Keyed on each agent's frontmatter `name`, which is what Claude Code reports as
# the agent type — note the capital E in Explore. build/check_frontmatter.py
# imports this and asserts it against the `## Read-only contract` heading in
# agents/*.md in both directions, so drift fails the lint at commit time.
READONLY_AGENTS = frozenset({
    'code-reviewer',
    'task-reviewer',
    'security-auditor',
    'Explore',
    'test-runner',
})

# Confirmed against Claude Code 2.1.259 by the probe in hooks/README.md.
AGENT_TYPE_KEY = 'agent_type'

CONTRACT_CLAUSE = (
    'you must not mutate the working tree, the index, HEAD, branch state, '
    'or the worktree list via Bash'
)

# Subcommand separators. '>' and '<' are deliberately absent: redirection stays
# inside its subcommand so `git log > /tmp/f` classifies as a `git log`.
OPERATORS = frozenset({'&&', '||', ';', '|', '&'})

DENIED_COMMANDS = {
    'rm': '`rm` deletes files.',
    'mv': '`mv` moves or renames files.',
    'truncate': '`truncate` rewrites file contents in place.',
    'shred': '`shred` destroys file contents.',
    'sudo': '`sudo` escalates privileges and can mutate anything.',
}

# git's read-only vocabulary is small and enumerable, so this is an allowlist
# and anything not on it is denied — including verbs git adds in the future.
GIT_READONLY_VERBS = frozenset({
    'log', 'show', 'diff', 'diff-tree', 'status', 'grep', 'blame', 'ls-files',
    'ls-tree', 'ls-remote', 'cat-file', 'rev-parse', 'rev-list', 'describe',
    'shortlog', 'whatchanged', 'name-rev', 'merge-base', 'for-each-ref',
    'count-objects', 'verify-commit', 'check-ignore', 'check-attr', 'var',
    'help', 'version',
})

# Print-and-exit flags: allow immediately, there is no verb behind them.
GIT_INFO_FLAGS = frozenset({
    '--version', '--help', '-h', '--html-path', '--man-path', '--info-path',
})

# Global options skipped while locating the verb.
GIT_GLOBAL_FLAGS = frozenset({
    '-p', '--paginate', '-P', '--no-pager', '--bare', '--literal-pathspecs',
    '--no-literal-pathspecs', '--glob-pathspecs', '--noglob-pathspecs',
    '--icase-pathspecs', '--no-replace-objects', '--no-optional-locks',
    '--no-lazy-fetch', '--no-advice',
})
GIT_GLOBAL_WITH_VALUE = frozenset({
    '-C', '-c', '--git-dir', '--work-tree', '--namespace', '--exec-path',
    '--config-env', '--attr-source',
})

# A read-only route to what the denied verb was probably reaching for. Naming it
# lets the agent report accurately to its controller instead of retrying blind.
# Only consulted for verbs that reach the fail-closed default, so do NOT add keys
# for verbs in GIT_SUBCOMMAND_ALLOWED / GIT_FLAG_ALLOWED — those are handled
# earlier in _classify_git, and an entry here would be dead code.
GIT_ALTERNATIVES = {
    'checkout': 'To read a file at another revision use `git show <SHA>:<path>`; '
                'to compare, `git diff <SHA>..HEAD`.',
    'switch': 'To read a file at another revision use `git show <SHA>:<path>`.',
    'restore': 'To read a file at another revision use `git show <SHA>:<path>`.',
    'reset': 'To compare against another revision use `git diff <SHA>..HEAD`.',
    'clean': 'To see what is untracked use `git status --porcelain`.',
    'add': 'Nothing in a read-only review touches the index.',
    'commit': 'Nothing in a read-only review creates a commit.',
    'fetch': 'Denied deliberately, not by fall-through: a fetch part-way through a '
             'review silently changes what a later `git diff origin/main...` shows, '
             'so the artifact moves while it is being reviewed. If you need a base '
             'ref that is not local, report that to your controller so it can fetch '
             'before dispatching.',
    'pull': 'Denied deliberately, not by fall-through: `git pull` merges into HEAD. '
            'Report a missing base ref to your controller instead of fetching it '
            'yourself.',
}

# Verbs whose read-only forms are named by a subcommand: (allowed subcommands,
# whether the bare verb is itself read-only). `git stash` bare is NOT — it
# stashes the caller's uncommitted work, which is the exact damage this guard
# exists to prevent.
GIT_SUBCOMMAND_ALLOWED = {
    'stash': (frozenset({'list', 'show'}), False),
    'worktree': (frozenset({'list'}), False),
    'submodule': (frozenset({'status', 'summary'}), False),
    'notes': (frozenset({'list', 'show'}), False),
    'bisect': (frozenset({'log', 'view'}), False),
    'sparse-checkout': (frozenset({'list'}), False),
    'remote': (frozenset({'show', 'get-url'}), True),
    'reflog': (frozenset({'show'}), True),
}

# Verbs whose read-only forms are named by flags. `value_flags` take an argument,
# which must not be mistaken for a positional. A positional is allowed only
# alongside a `list_flag`, because `git branch foo` and `git tag v1` create.
# `required` (config only) means at least one of these must be present.
GIT_FLAG_ALLOWED = {
    'branch': {
        'flags': frozenset({'-l', '--list', '-a', '-r', '-v', '-vv', '--contains',
                            '--merged', '--no-merged', '--show-current',
                            '--format', '--sort'}),
        'value_flags': frozenset({'--contains', '--merged', '--no-merged',
                                  '--format', '--sort'}),
        'list_flags': frozenset({'-l', '--list'}),
        'required': frozenset(),
    },
    'tag': {
        'flags': frozenset({'-l', '--list', '--contains', '--points-at',
                            '--sort', '--format'}),
        'value_flags': frozenset({'--contains', '--points-at', '--sort',
                                  '--format'}),
        'list_flags': frozenset({'-l', '--list'}),
        'required': frozenset(),
    },
    'config': {
        'flags': frozenset({'--get', '--get-all', '--get-regexp', '--list', '-l'}),
        'value_flags': frozenset(),
        'list_flags': frozenset({'--get', '--get-all', '--get-regexp',
                                 '--list', '-l'}),
        'required': frozenset({'--get', '--get-all', '--get-regexp',
                               '--list', '-l'}),
    },
}


def split_subcommands(command):
    """Tokenize `command` and split it into subcommands on shell operators.

    Newlines are pre-split because shlex treats them as ordinary whitespace,
    which would otherwise fold a second line into the first subcommand and hide
    its leading token from classification.
    """
    subcommands = []
    for line in command.split('\n'):
        lexer = shlex.shlex(line, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        lexer.commenters = ''  # a shell comment only starts at a word boundary
        current = []
        for token in lexer:
            if token in OPERATORS:
                if current:
                    subcommands.append(current)
                current = []
            else:
                current.append(token)
        if current:
            subcommands.append(current)
    return subcommands


def _sed_edits_in_place(args):
    for token in args:
        if token == '--in-place' or token.startswith('--in-place='):
            return True
        if token.startswith('-') and not token.startswith('--') and 'i' in token[1:]:
            return True
    return False


def _classify_non_git(tokens):
    head = tokens[0]
    if head in DENIED_COMMANDS:
        return DENIED_COMMANDS[head] + ' This agent inspects; it does not modify.'
    if head == 'sed' and _sed_edits_in_place(tokens[1:]):
        return ('`sed -i` edits files in place; drop `-i` to write the result to '
                'stdout instead.')
    return None


def _classify_subcommand(tokens):
    if not tokens:
        return None
    if tokens[0] == 'git':
        return _classify_git(tokens[1:])
    return _classify_non_git(tokens)


def classify(command):
    """Return None if `command` is read-only, else a reason fragment for denial.

    git is an allowlist that fails closed on unknown verbs; non-git is a
    denylist of unambiguous mutators, so unlisted commands pass. The asymmetry
    is deliberate — read-only shell is unbounded, read-only git is not.
    """
    for tokens in split_subcommands(command):
        detail = _classify_subcommand(tokens)
        if detail is not None:
            return detail
    return None


def _readable_forms(verb, subcommands):
    return ' / '.join('`git ' + verb + ' ' + s + '`' for s in sorted(subcommands))


def _classify_git_subcommand_verb(verb, rest):
    allowed, bare_is_readonly = GIT_SUBCOMMAND_ALLOWED[verb]
    subcommand = None
    for token in rest:
        if not token.startswith('-'):
            subcommand = token
            break
    if subcommand is None:
        if bare_is_readonly:
            return None
        return ('bare `git ' + verb + '` mutates state; only '
                + _readable_forms(verb, allowed) + ' are read-only.')
    if subcommand in allowed:
        return None
    return ('`git ' + verb + ' ' + subcommand + '` is not a read-only form; only '
            + _readable_forms(verb, allowed) + ' are allowed.')


def _classify_git_flag_verb(verb, rest):
    """Classify a flag-keyed verb (branch / tag / config).

    Two structural notes:
    * A value flag consumes the next token, so `git branch --contains <ref>` and
      `git branch --merged <ref>` never register a positional. That is the right
      resolution for a read-only check — those arguments are commit-ish, not new
      branch names — but it does mean the positional guard below cannot fire
      alongside them.
    * For `config`, `list_flags == required`, so the positional branch is
      unreachable: anything carrying a positional has already satisfied the
      required check via the same flag set. Kept uniform with branch/tag rather
      than special-cased.
    """
    rule = GIT_FLAG_ALLOWED[verb]
    seen = set()
    has_positional = False
    i = 0
    while i < len(rest):
        token = rest[i]
        if token.startswith('-'):
            name, sep, _value = token.partition('=')
            if name not in rule['flags']:
                return ('`git ' + verb + ' ' + token + '` is not one of the '
                        'read-only forms of `git ' + verb + '`.')
            seen.add(name)
            i += 1 if sep else (2 if name in rule['value_flags'] else 1)
            continue
        has_positional = True
        i += 1
    if rule['required'] and not (seen & rule['required']):
        return ('`git ' + verb + '` is read-only only in its query forms ('
                + ', '.join('`' + f + '`' for f in sorted(rule['required']))
                + '); any other form writes.')
    if has_positional and not (seen & rule['list_flags']):
        return ('`git ' + verb + '` with a bare argument creates or moves a '
                + verb + '; use `git ' + verb + ' --list` to read.')
    return None


def _locate_git_verb(args):
    """Return (index of the verb, None), or (None, reason) if we should stop.

    A reason of '' means "allow, there is no verb" — bare `git` or an info flag.
    An unknown leading option denies rather than being treated as a verb, so
    `git --wat log` cannot slip a verb past the scan.
    """
    i = 0
    while i < len(args):
        token = args[i]
        if token in GIT_INFO_FLAGS:
            return None, ''
        if token in GIT_GLOBAL_FLAGS:
            i += 1
            continue
        if token in GIT_GLOBAL_WITH_VALUE:
            i += 2  # the option's value is the next token
            continue
        if '=' in token and token.partition('=')[0] in GIT_GLOBAL_WITH_VALUE:
            i += 1
            continue
        if token.startswith('-'):
            return None, ('`git ' + token + '` is not a recognized read-only git '
                          'global option, and this guard fails closed on options '
                          'it cannot account for.')
        return i, None
    return None, ''  # ran out of tokens: bare `git`, which only prints usage


def _classify_git(args):
    index, reason = _locate_git_verb(args)
    if index is None:
        return reason or None
    verb = args[index]
    rest = args[index + 1:]
    if verb in GIT_READONLY_VERBS:
        return None
    if verb in GIT_SUBCOMMAND_ALLOWED:
        return _classify_git_subcommand_verb(verb, rest)
    if verb in GIT_FLAG_ALLOWED:
        return _classify_git_flag_verb(verb, rest)
    alternative = GIT_ALTERNATIVES.get(verb)
    if alternative:
        return '`git ' + verb + '` is denied by the read-only allowlist. ' + alternative
    return ('`git ' + verb + '` is not on the read-only allowlist — it either mutates '
            'git state or is unrecognized, and this guard fails closed on both.')


if __name__ == '__main__':
    sys.exit(0)  # Task 5 replaces this with main()
