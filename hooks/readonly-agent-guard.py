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


def _classify_git(args):
    return None  # Tasks 3 and 4 replace this


if __name__ == '__main__':
    sys.exit(0)  # Task 5 replaces this with main()
