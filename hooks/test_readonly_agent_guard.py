"""Gate A for hooks/readonly-agent-guard.py — run from this directory, both ways.

cd hooks
uv run --python 3.13 --with pytest python -m pytest -q
uv run --python /usr/bin/python3 --with pytest python -m pytest -q

Two layers, per spec Verification: unit tests import the classifier directly,
contract tests drive the script as a subprocess with real payloads on stdin.
Each contract test runs twice — see guard_env. The second command runs the
unit tests under the 3.9 floor too, so this file stays 3.9-compatible as well.
Stdlib plus pytest; the guard itself is stdlib only.
"""

import copy
import functools
import importlib.util
import json
import os
import random
import shlex
import subprocess
from pathlib import Path

import pytest

HOOKS = Path(__file__).resolve().parent
GUARD = HOOKS / 'readonly-agent-guard.py'

# The oldest python3 the guard must run under: macOS's system python3 (Xcode
# Command Line Tools). Bump it only alongside the guard's own docstring.
FLOOR_PYTHON = (3, 9)
# launchd's default PATH. An app launched from the Dock may hand its hooks only
# this, and on it the guard's `#!/usr/bin/env python3` resolves to
# /usr/bin/python3 — the floor interpreter, whatever the developer's shell has.
LAUNCHD_PATH = '/usr/bin:/bin:/usr/sbin:/sbin'

# Recorded from Claude Code 2.1.259 on 2026-09-03 by the plan-24 Task 1 probe,
# via the production path: an Agent-tool dispatch of Explore from a `claude -p`
# session. This is the observed payload shape, not an invented one — every stdin
# fixture below derives from it, so Gate A cannot pass against a shape Claude
# Code never sends.
#
# Volatile identifiers are trimmed: session_id, prompt_id, tool_use_id,
# transcript_path, and agent_id (a per-dispatch hex string that accompanies
# agent_type on the dispatch route but is absent on the `--agent` route).
RECORDED_PAYLOAD = {
    'agent_type': 'Explore',
    'cwd': '/Users/lowell/Projects/agent-skills',
    'hook_event_name': 'PreToolUse',
    'permission_mode': 'auto',
    'tool_input': {'command': 'git status --porcelain'},
    'tool_name': 'Bash',
}

# The same event from the main session: no agent_type, no agent_id, and an
# `effort` key the agent payload does not carry. Recorded in the same run; the
# command string is substituted for a short one (the original was a heredoc),
# which changes nothing — every test overwrites it via payload_for().
RECORDED_MAIN_SESSION_PAYLOAD = {
    'cwd': '/Users/lowell/Projects/agent-skills',
    'effort': {'level': 'xhigh'},
    'hook_event_name': 'PreToolUse',
    'permission_mode': 'auto',
    'tool_input': {'command': 'git status --porcelain'},
    'tool_name': 'Bash',
}


def test_recorded_payload_carries_the_agent_identity():
    assert RECORDED_PAYLOAD['agent_type'] == 'Explore'
    assert 'agent_type' not in RECORDED_MAIN_SESSION_PAYLOAD
    assert RECORDED_PAYLOAD['tool_name'] == 'Bash'
    assert isinstance(RECORDED_PAYLOAD['tool_input']['command'], str)


def _load_guard():
    spec = importlib.util.spec_from_file_location('readonly_agent_guard', GUARD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


guard = _load_guard()


def test_roster_is_the_five_readonly_agents():
    assert guard.READONLY_AGENTS == frozenset(
        {'code-reviewer', 'task-reviewer', 'security-auditor', 'Explore', 'test-runner'}
    )


def test_tokenizer_splits_on_shell_operators():
    assert guard.split_subcommands('git log && rm -rf x') == [
        ['git', 'log'], ['rm', '-rf', 'x']]
    assert guard.split_subcommands('cat a|grep b') == [['cat', 'a'], ['grep', 'b']]
    assert guard.split_subcommands('a; b & c || d') == [['a'], ['b'], ['c'], ['d']]


def test_tokenizer_splits_on_newlines():
    # shlex treats a newline as plain whitespace, so 'a\nb' would collapse into
    # one subcommand and hide b's leading token. Splitting at every unquoted
    # newline is load-bearing.
    assert guard.split_subcommands('git log\nrm x') == [['git', 'log'], ['rm', 'x']]


# Observed 2026-09-28: a code-reviewer's calibration probe, denied because the
# guard cut the command at every newline and shlex then raised on the half-open
# quote in the first line.
MULTILINE_PYTHON_C = (
    'uv run --python 3.13 --with numpy python -c "\n'
    'import numpy as np\n'
    'print(np.mean([1, 2]))\n'
    '"'
)


def test_newline_inside_quotes_stays_in_its_word():
    assert guard.split_subcommands(MULTILINE_PYTHON_C) == [[
        'uv', 'run', '--python', '3.13', '--with', 'numpy', 'python', '-c',
        '\nimport numpy as np\nprint(np.mean([1, 2]))\n']]
    assert guard.split_subcommands('python -c "a\nb"\nrm x') == [
        ['python', '-c', 'a\nb'], ['rm', 'x']]
    assert guard.split_subcommands("python -c 'a\nb'\nrm x") == [
        ['python', '-c', 'a\nb'], ['rm', 'x']]
    # An escaped double quote does not close the string.
    assert guard.split_subcommands('echo "say \\"hi\\"\n"\nrm x') == [
        ['echo', 'say "hi"\n'], ['rm', 'x']]


def test_hash_inside_a_multiline_quote_is_data():
    # `python -c` scripts carry comments; inside the quote they are not shell.
    assert guard.split_subcommands('python -c "\n# mean\nprint(1)\n"') == [
        ['python', '-c', '\n# mean\nprint(1)\n']]


def test_trailing_backslash_fails_closed():
    with pytest.raises(ValueError):
        guard.classify('git log \\')


def test_backslash_is_literal_inside_single_quotes():
    # Where a quote closes must match shlex exactly: if the split thinks a quote
    # is still open when shlex does not, a newline folds a mutator into a word.
    assert guard.split_subcommands("echo 'a\\'\nrm x") == [['echo', 'a\\'], ['rm', 'x']]


def test_backslash_newline_fails_closed_as_before_multiline_support():
    # Continuations are not joined, in or out of quotes: the command is split at
    # every newline, and the line ending in `\` raises, as it always did.
    for command in ('uv run --python 3.13 --with pytest \\\n  python -m pytest -q',
                    'git \\\n  stash',
                    'echo "a\\\nb"\nrm x'):
        with pytest.raises(ValueError):
            guard.split_subcommands(command)


# Syntax whose quoting the scan does not model. Beside any of it, a multi-line
# quote gets the split from before multi-line support, and so fails closed.
UNMODELED_SYNTAX = ['$(', '`', "$'", '${', '$[', '((', '<<', '\\\n']


@pytest.mark.parametrize('syntax', UNMODELED_SYNTAX)
def test_multiline_quote_fails_closed_beside_unmodeled_syntax(syntax):
    with pytest.raises(ValueError):
        guard.split_subcommands('echo ' + syntax + ' "a\nb"')


def test_escaped_backslash_before_a_newline_is_not_a_continuation():
    # `a\\` ends in a literal backslash, so the newline after it still ends the
    # command. Taking it as a continuation would glue `rm` onto `echo`'s word.
    assert guard.split_subcommands('echo a\\\\\nrm x') == [['echo', 'a\\'], ['rm', 'x']]


def test_comments_are_tokenized_not_stripped():
    # Where a `#` starts a comment depends on the shell and the context, so the
    # guard never decides it: comment text is tokenized like any other.
    assert guard.split_subcommands('# check it\ngit status') == [
        ['#', 'check', 'it'], ['git', 'status']]
    assert guard.split_subcommands('git log  # show\ngit status') == [
        ['git', 'log', '#', 'show'], ['git', 'status']]
    assert guard.split_subcommands("git log --grep '# x'") == [
        ['git', 'log', '--grep', '# x']]
    assert guard.split_subcommands('echo a\\ #b') == [['echo', 'a #b']]


def test_no_quote_spans_lines_after_an_unquoted_hash():
    # If that `#` starts a comment, its apostrophe is no quote to the shell, and
    # pairing it with a later one would swallow the lines between. Fails closed,
    # as every comment with an apostrophe did before multi-line support.
    for command in ("# what's changed\ngit diff main..HEAD",
                    "git log  # don't page\ngit status"):
        with pytest.raises(ValueError):
            guard.split_subcommands(command)


def test_every_physical_line_is_also_classified_on_its_own():
    # The backstop: whatever the multi-line reading misses, a line that begins
    # with a mutator is denied, exactly as it was before multi-line support.
    # Its cost is this false positive inside a quoted script.
    assert guard.classify('python -c "\nrm = 1\nprint(rm)\n"') is not None


def _guard_denies(command):
    # main() denies a guarded agent both a classified mutator and a ValueError.
    try:
        return guard.classify(command) is not None
    except ValueError:
        return True


# Every entry runs `rm x` or `git stash` in zsh (checked with `echo` in its
# place) and was denied before multi-line support. Sources: the 2026-09-28
# code-reviewer and Codex reviews of this change, and the probes that followed.
MULTILINE_BYPASSES = [
    pytest.param('echo `echo a #b`; rm x', id='hash-in-backticks'),
    pytest.param('echo ${x// #/y}; rm x', id='hash-in-param-pattern'),
    pytest.param('echo ${x:-a #b}; rm x', id='hash-in-param-default'),
    pytest.param('(( 1 #2 )) ; rm x', id='hash-in-arithmetic'),
    pytest.param('echo $(( 1 + ##A )) ; rm x', id='zsh-char-code'),
    pytest.param('echo ${x:-a\n#b}; rm x', id='hash-in-param-across-lines'),
    pytest.param('echo `echo a\n#b`; rm x', id='hash-in-backticks-across-lines'),
    pytest.param("echo $'\\''\nrm x\necho \\'", id='ansi-c-quote'),
    pytest.param('echo "$(printf \'"\')"\nrm x\necho \\\'', id='quote-in-substitution'),
    pytest.param("cat <<EOF\nit's\nEOF\nrm x\necho \\'", id='quote-in-heredoc'),
    pytest.param('echo "$(printf \'"\')"\nrm x\necho "$(printf \'"\')"',
                 id='quote-in-substitution-twice'),
    pytest.param('echo "`printf \'"\'`"\nrm x\necho "`printf \'"\'`"',
                 id='quote-in-backticks-twice'),
    pytest.param("echo \"${x#\"'\"}\"\nrm x\necho \"${x#\"'\"}\"",
                 id='quote-in-param-twice'),
    pytest.param('echo *(e: #:N) ; rm x', id='zsh-hash-in-glob-qualifier'),
    pytest.param("(cd /tmp)#'\nrm x #'", id='zsh-comment-after-paren'),
    pytest.param("# what's here\ngit stash\n# let's see", id='apostrophes-in-comments'),
    pytest.param('# note \\\nrm x', id='backslash-in-comment'),
    pytest.param("echo $'it\\'s'\ngit stash\necho $'don\\'t'", id='ansi-c-escaped-quote'),
    pytest.param('ls (#i)readme*; git stash', id='zsh-glob-flag'),
    pytest.param('echo ${(#)x}; git stash', id='zsh-param-flag'),
]


@pytest.mark.parametrize('command', MULTILINE_BYPASSES)
def test_known_multiline_and_comment_bypasses_are_denied(command):
    assert _guard_denies(command)


# Leading-token bypasses, found 2026-09-28 by a code review and the probes that
# followed. Each hides its mutator behind syntax around the command, and each
# runs `rm x` or `git stash` in zsh as Claude Code's Bash tool runs it (checked
# with a marker-writing stand-in in its place) where classify returned None.

# shlex merges adjacent punctuation into one token, so `);` was never `;`, and a
# parenthesis could hide a command or lead one.
PAREN_AND_OPERATOR_BYPASSES = [
    pytest.param('echo $(git rev-parse HEAD); rm x', id='substitution-then-semicolon'),
    pytest.param('(cd /tmp); rm x', id='subshell-then-semicolon'),
    pytest.param('(cd /tmp)&& rm x', id='subshell-then-and'),
    pytest.param('(cd /tmp)|rm x', id='subshell-then-pipe'),
    pytest.param('git log;(rm x)', id='semicolon-then-subshell'),
    pytest.param('(rm x)', id='subshell'),
    pytest.param('echo $(rm x)', id='command-substitution'),
    pytest.param('cat <(rm x)', id='process-substitution'),
    pytest.param('case a in a) rm x;; esac', id='case-arm'),
    pytest.param('case a in (a) rm x;; esac', id='case-arm-open-paren'),
    pytest.param('f() rm x; f', id='function-short-body'),
    pytest.param('for f (a) rm x', id='zsh-for-short-body'),
    pytest.param('git log |& rm x', id='pipe-with-stderr'),
    pytest.param('git log &| rm x', id='zsh-disown'),
    pytest.param('git log &; rm x', id='background-then-semicolon'),
]

# A word that leads the subcommand without being its command.
RESERVED_WORD_BYPASSES = [
    pytest.param('git log && { rm x; }', id='brace-group'),
    pytest.param('! { rm x; }', id='bang-brace-group'),
    pytest.param('function f { rm x; }; f', id='function-keyword'),
    pytest.param('! rm x', id='bang'),
    pytest.param('git log &! rm x', id='zsh-disown-bang'),
    pytest.param('if rm x; then :; fi', id='if'),
    pytest.param('if true; then rm x; fi', id='then'),
    pytest.param('if false; then :; elif rm x; then :; fi', id='elif'),
    pytest.param('if false; then :; else rm x; fi', id='else'),
    pytest.param('while rm x; do break; done', id='while'),
    pytest.param('until rm x; do :; done', id='until'),
    pytest.param('for f in a; do rm x; done', id='do'),
    pytest.param('if [[ -n a ]] rm x', id='zsh-if-short-test'),
    pytest.param('if (( 1 )) rm x', id='zsh-if-short-arithmetic'),
    pytest.param('coproc rm x', id='coproc'),
    pytest.param('repeat 1 rm x', id='repeat'),
    pytest.param('noglob rm x', id='noglob'),
    pytest.param('nocorrect rm x', id='nocorrect'),
    pytest.param('zmodload zsh/files; builtin rm x', id='builtin'),
]

# Words before the command: assignments, redirections, a path, and utilities
# that run the command after their own options.
PREFIX_BYPASSES = [
    pytest.param('X=1 rm x', id='assignment'),
    pytest.param('GIT_PAGER=cat git stash', id='assignment-before-git'),
    pytest.param('2>/dev/null rm x', id='leading-redirection'),
    pytest.param('> out rm x', id='leading-redirection-without-fd'),
    pytest.param('git log |> out rm x', id='pipe-into-leading-redirection'),
    pytest.param('/bin/rm x', id='path'),
    pytest.param('/usr/bin/git stash', id='path-to-git'),
    pytest.param('env rm x', id='env'),
    pytest.param('env -i FOO=1 rm x', id='env-option-and-assignment'),
    pytest.param('command rm x', id='command'),
    pytest.param('command -p rm x', id='command-option'),
    pytest.param('exec rm x', id='exec'),
    pytest.param('exec -a foo rm x', id='exec-value-option'),
    pytest.param('time rm x', id='time'),
    pytest.param('nohup rm x', id='nohup'),
    pytest.param('nice rm x', id='nice'),
    pytest.param('nice -n 5 rm x', id='nice-value-option'),
    pytest.param('time env GIT_PAGER=cat git stash', id='prefix-chain'),
]


@pytest.mark.parametrize('command', PAREN_AND_OPERATOR_BYPASSES)
def test_parenthesis_and_operator_bypasses_are_denied(command):
    assert guard.classify(command) is not None


@pytest.mark.parametrize('command', RESERVED_WORD_BYPASSES)
def test_reserved_word_bypasses_are_denied(command):
    assert guard.classify(command) is not None


@pytest.mark.parametrize('command', PREFIX_BYPASSES)
def test_prefix_bypasses_are_denied(command):
    assert guard.classify(command) is not None


def test_the_command_after_its_prefixes_is_the_one_classified():
    # The stripped command reaches the checks a bare one does: git's allowlist,
    # the denylist, and sed's in-place flag.
    assert 'git stash' in guard.classify('time env GIT_PAGER=cat git stash')
    assert '`rm`' in guard.classify('/bin/rm x')
    assert 'sed -i' in guard.classify('nice -n 5 sed -i s/a/b/ f')


def test_parentheses_nest_so_the_command_around_them_continues():
    # Nested, a group is a subcommand of its own and the one it interrupted
    # resumes after it, so git's verb is still found past a substitution.
    assert guard.split_subcommands('echo $(ls); rm x') == [
        ['ls'], ['echo', '$'], ['rm', 'x']]
    assert guard.split_subcommands('git -C $(pwd) stash') == [
        ['pwd'], ['git', '-C', '$', 'stash']]


def test_a_process_substitution_is_one_word():
    # zsh passes `<(…)` as one path, never a redirection, and glues it to the
    # word it touches: `2<(true)` is the single word `2/dev/fd/11`.
    assert guard.split_subcommands('cat <(git show a:f)') == [
        ['git', 'show', 'a:f'], ['cat', '<()']]
    assert guard.split_subcommands('git branch --format 2<(true) newbr') == [
        ['true'], ['git', 'branch', '--format', '<()', 'newbr']]


def test_a_word_glued_to_a_group_is_part_of_its_word():
    # `*(.)`, `$(pwd)/.git` and `<(x)y` are each one word to zsh.
    assert guard.split_subcommands('ls *(.) x') == [['.'], ['ls', '()', 'x']]
    assert guard.split_subcommands('echo $(pwd)/.git x') == [['pwd'], ['echo', '$', 'x']]
    assert guard.split_subcommands('cat <(true)y x') == [['true'], ['cat', '<()', 'x']]


def test_a_substitution_or_a_glob_group_may_be_many_words():
    # zsh splits an unquoted $(…) into as many words as it prints, and a glob
    # group matches any number of files. A quoted "$(…)" stays one word.
    tokens = guard._tokenize('git -C $(pwd) "$(pwd)" log')
    assert [(str(t), t.expands) for t in tokens if not t.syntax] == [
        ('git', False), ('-C', False), ('$', True), ('pwd', False),
        ('$(pwd)', False), ('log', False)]
    assert guard.split_subcommands('ls (a|b)')[-1][-1].expands


def test_a_nested_group_holds_its_place_in_the_command_around_it():
    # zsh globs `(stash)` to a file named stash, and `git (stash)` then runs
    # `git stash`. Git's verb slot fails closed on a group, as it did before
    # nesting, unless a `$` already stands in for it.
    assert guard.classify('git (stash)') is not None
    assert guard.classify('git branch (x)') is not None
    # A glob flag and its pattern are one word.
    assert guard.split_subcommands('ls (#i)readme*') == [['#i'], ['ls', '()']]
    # A group left open closes at the end of its line, the same way.
    assert guard.split_subcommands('git (stash') == [['stash'], ['git', '()']]


def test_redirections_are_not_arguments():
    # A redirection, its target and its file descriptor are dropped before a
    # command is classified, so `2` is not read as a subcommand or a branch.
    for command in ('git branch --show-current 2>/dev/null', 'git remote -v 2>&1',
                    'git reflog 2>/dev/null',
                    'B=$(git branch --show-current 2>/dev/null); echo "$B"'):
        assert guard.classify(command) is None, command


def test_parentheses_read_flat_end_the_command():
    # Flat, every parenthesis ends a subcommand: the reading for one that
    # stands before a command, as a case pattern does.
    assert guard.split_subcommands('case a in (a) rm x;; esac', nest=False) == [
        ['case', 'a', 'in'], ['a'], ['rm', 'x'], ['esac']]


def test_unbalanced_parentheses_do_not_raise():
    # An unmatched `)` ends the subcommand, as after a case pattern, and a `(`
    # left open closes with its line, so a subshell may span lines.
    assert guard.split_subcommands('a) rm x') == [['a'], ['rm', 'x']]
    assert guard.split_subcommands('(\n  git log\n)') == [['git', 'log']]


def test_merged_punctuation_is_cut_into_separators_and_redirections():
    assert guard.split_subcommands('cat x 2>&1 |& grep y') == [
        ['cat', 'x', '2', '>&', '1'], ['grep', 'y']]
    assert guard.split_subcommands('a &| b &; c') == [['a'], ['b'], ['c']]
    assert guard.split_subcommands('a |> f') == [['a'], ['>', 'f']]
    assert guard.split_subcommands('a &> f; b >| g') == [
        ['a', '&>', 'f'], ['b', '>|', 'g']]


def test_braces_and_the_end_of_a_test_end_a_command():
    assert guard.split_subcommands('{ git log; } && git status') == [
        ['git', 'log'], ['git', 'status']]
    assert guard.split_subcommands('if [[ -n a ]] git log') == [
        ['if', '[[', '-n', 'a'], ['git', 'log']]


def test_syntax_around_a_read_only_command_stays_allowed():
    for command in (
            'command -v rm', 'command -V rm', 'command -pv rm',  # describe, not run
            'for rm in a b; do echo $rm; done',  # a loop variable, not a command
            'ls *(.)', 'ls (#i)readme*',  # zsh glob qualifier and flag
            "git log --format='%(refname)'",
            'time -p git log', 'exec 3>&1', 'env | grep PATH',
            'cat x 2>&1', 'echo a &> f', 'echo a >| f',
            'GIT_PAGER=cat git log', '/usr/bin/git status', '2>/dev/null git log',
            'cd $(git rev-parse --show-toplevel) && git status',
            'if git diff --quiet; then echo clean; fi',
            'while read -r f; do git log -1 -- "$f"; done < files',
            '(\n  git log\n)'):
        assert guard.classify(command) is None, command


def test_a_substitution_where_git_takes_a_value_fails_closed():
    # zsh splits an unquoted $(…) into as many words as it prints, so one in a
    # value slot can hand git its verb, and one among branch's arguments a
    # name to create: `git -C $(echo . stash)` stashes. Quoted, it stays one
    # word, and git's verb is classified as usual.
    for command in ('git -C $(pwd) log', 'git --git-dir=$(pwd)/.git log',
                    'git branch --contains $(git rev-parse HEAD)'):
        detail = guard.classify(command)
        assert detail is not None and 'quote' in detail, command
    for command in ('git -C "$(pwd)" log',
                    'git -C "$(git rev-parse --show-toplevel)" status',
                    'git branch --contains "$(git rev-parse HEAD)"',
                    'git log --oneline $(git merge-base main HEAD)..HEAD'):
        assert guard.classify(command) is None, command


def test_git_after_a_substitution_is_still_denied_when_the_verb_writes():
    # If `)` only ended the subcommand, the verb would lead one of its own,
    # where git's allowlist never sees it.
    for command in ('git -C $(pwd) stash',
                    'git -C $(git rev-parse --show-toplevel) checkout main',
                    'git --git-dir=$(pwd)/.git stash'):
        assert guard.classify(command) is not None, command


# Found 2026-09-28 by the review of the leading-token fix, and the probes that
# followed. Each creates or deletes a ref, stashes, edits a file in place, or
# runs `rm x` in zsh as Claude Code's Bash tool runs it (checked in a scratch
# repo, with a marker-writing stand-in for `rm x`), except the one whose id
# ends in `gnu`: BSD sed reads an option after a file name as a file.

# Quoting makes a word of anything, and shlex drops the quotes, so a quoted `>`
# or `)` was read as syntax: a redirection took the next word as its target, and
# a parenthesis, separator or brace ended the command.
QUOTED_SYNTAX_BYPASSES = [
    pytest.param("git branch '>'", id='quoted-redirection-as-branch'),
    pytest.param('git branch ">"', id='double-quoted-redirection-as-branch'),
    pytest.param('git branch \\>', id='escaped-redirection-as-branch'),
    pytest.param("git tag '>'", id='quoted-redirection-as-tag'),
    pytest.param("git branch '<' HEAD", id='quoted-input-redirection-as-branch'),
    pytest.param("git branch ')'", id='quoted-paren-as-branch'),
    pytest.param("git branch ')' -D feature", id='quoted-paren-hides-a-delete'),
    pytest.param("git branch ';' -D feature", id='quoted-separator-hides-a-delete'),
    pytest.param("git --namespace '>' stash", id='quoted-redirection-as-namespace'),
    pytest.param("git --namespace ')' stash", id='quoted-paren-as-namespace'),
    pytest.param("git --namespace '(' stash", id='quoted-open-paren-as-namespace'),
    pytest.param("git --namespace ';' stash", id='quoted-separator-as-namespace'),
    pytest.param("git -C ')' stash", id='quoted-paren-as-directory'),
    pytest.param("sed -e '/start/,/end/{' -e 'd' -e '}' -i.bak notes.md",
                 id='quoted-brace-in-a-sed-script'),
    pytest.param("sed -e ';;' -e 's/body/X/' -i '' f", id='quoted-separators-as-a-sed-script'),
    pytest.param("exec -a '>' rm x", id='quoted-redirection-as-exec-name'),
    pytest.param("env -u '>' rm x", id='quoted-redirection-as-env-variable'),
]

# Unquoted, `{` and `]]` are syntax only where a command could start. Anywhere
# else they are words, unlike `}`, which zsh reads as syntax wherever it stands.
ARGUMENT_BRACE_BYPASSES = [
    pytest.param('git branch { HEAD', id='open-brace-as-branch'),
    pytest.param('git branch ]] HEAD', id='test-end-as-branch'),
    pytest.param('git --namespace ]] stash', id='test-end-as-namespace'),
    pytest.param('sed -e p ]] -i f', id='test-end-before-sed-i-gnu'),
]

# zsh reads a file descriptor only as one unquoted digit touching its `<`, `>`
# or `&>`; any other digit is an argument. A `{name}` before a redirection names
# one whether or not a space comes between.
FILE_DESCRIPTOR_BYPASSES = [
    pytest.param('git branch 5 >/dev/null', id='spaced-digit-as-branch'),
    pytest.param('git tag 1 >/dev/null', id='spaced-digit-as-tag'),
    pytest.param('git branch 5 &>/dev/null', id='spaced-digit-before-and-redirection'),
    pytest.param('git branch 12>/dev/null', id='two-digits-as-branch'),
    pytest.param("git branch '5'>/dev/null", id='quoted-digit-as-branch'),
    pytest.param('git branch \\5>/dev/null', id='escaped-digit-as-branch'),
    pytest.param('exec {fd}>/dev/null rm x', id='named-fd-before-exec-command'),
    pytest.param('noglob {fd}>/dev/null rm x', id='named-fd-before-a-command'),
    pytest.param('noglob {fd} >/dev/null rm x', id='spaced-named-fd'),
    pytest.param('exec {fd}>/dev/null git checkout main', id='named-fd-before-git'),
]

# zsh's `-` precommand modifier. The snapshot the Bash tool sources aliases a
# bare `-` to `cd -`, so only a quoted or escaped one reaches the modifier.
DASH_MODIFIER_BYPASSES = [
    pytest.param('\\- rm x', id='escaped-dash'),
    pytest.param("'-' rm x", id='quoted-dash'),
    pytest.param('"-" git stash', id='double-quoted-dash-before-git'),
    pytest.param('true; \\- rm x', id='escaped-dash-after-a-separator'),
]


@pytest.mark.parametrize('command', QUOTED_SYNTAX_BYPASSES)
def test_a_quoted_word_is_never_syntax(command):
    assert guard.classify(command) is not None


@pytest.mark.parametrize('command', ARGUMENT_BRACE_BYPASSES)
def test_a_brace_or_test_end_among_arguments_is_a_word(command):
    assert guard.classify(command) is not None


@pytest.mark.parametrize('command', FILE_DESCRIPTOR_BYPASSES)
def test_only_a_file_descriptor_leaves_with_its_redirection(command):
    assert guard.classify(command) is not None


@pytest.mark.parametrize('command', DASH_MODIFIER_BYPASSES)
def test_the_dash_modifier_leads_a_command_like_a_keyword(command):
    assert guard.classify(command) is not None


# Found 2026-09-28 by the second review, and the probes that followed. Main
# denies each, and the first fix allowed it by dropping a word zsh passes to the
# command: taken for a file descriptor, for a redirection or its target, or
# folded into one placeholder. Each creates or deletes a ref, stashes, or edits
# a file in place in zsh as the Bash tool runs it, checked in a scratch repo,
# with files for the globs to match (`3`, `stash`, `a`, `b`). Two exceptions:
# the id ending in `gnu` edits only under GNU sed, and `{é}` is a word only in
# the C locale; under UTF-8 zsh reads it as a name.
DROPPED_ARGUMENT_BYPASSES = [
    # zsh names a descriptor only with an ASCII identifier.
    pytest.param('git --namespace {²}>/dev/null stash', id='superscript-in-braces-as-namespace'),
    pytest.param('git --namespace {é}>/dev/null stash', id='accent-in-braces-as-namespace'),
    pytest.param('git branch {é}>/dev/null', id='accent-in-braces-as-branch'),
    # A word glued to a process substitution is part of the same word.
    pytest.param('git branch 2<(true)', id='digit-glued-to-a-process-substitution'),
    pytest.param('git tag 1>(cat)', id='digit-glued-to-an-output-process-substitution'),
    pytest.param('git branch {x}<(true)', id='braces-glued-to-a-process-substitution'),
    pytest.param('git branch --format 2<(true) newbr',
                 id='glued-process-substitution-as-a-value'),
    # A process substitution is a word, never a redirection with a target.
    pytest.param('git branch --format <(true) newbr', id='process-substitution-as-a-value'),
    pytest.param('git tag --format >(true) v9', id='output-process-substitution-as-a-value'),
    pytest.param('git branch --sort <(true) newbr', id='process-substitution-as-a-sort-key'),
    # An unquoted $(…) is as many words as it prints.
    pytest.param('git -C $(echo . stash)', id='substitution-as-directory-and-verb'),
    pytest.param('git --namespace $(echo x stash)', id='substitution-as-namespace-and-verb'),
    pytest.param('git --git-dir $(echo .git stash)', id='substitution-as-git-dir-and-verb'),
    pytest.param('git --work-tree $(echo . stash)', id='substitution-as-work-tree-and-verb'),
    pytest.param('git branch --format $(echo x -D feature)', id='substitution-hides-a-delete'),
    pytest.param('git tag --format $(echo x v9)', id='substitution-as-a-value-and-a-tag'),
    pytest.param('sed $(echo -i.bak) s/body/X/ f', id='substitution-as-sed-in-place'),
    # zsh globs: a numeric range, and a group that may match more than one file.
    pytest.param('git branch <-> newb', id='numeric-glob-as-branch'),
    pytest.param('git tag <1-5> v1', id='numeric-range-glob-as-tag'),
    pytest.param('git branch --format <-> newb', id='numeric-glob-as-a-value'),
    pytest.param('sed -e p <-> -i f', id='numeric-glob-before-sed-i-gnu'),
    pytest.param('git --namespace $ (stash)', id='spaced-group-after-a-dollar-as-verb'),
    pytest.param('git branch --format (a|b)', id='glob-alternation-as-a-value-and-a-branch'),
]


@pytest.mark.parametrize('command', DROPPED_ARGUMENT_BYPASSES)
def test_every_word_zsh_passes_reaches_the_classifier(command):
    assert guard.classify(command) is not None


def test_a_numeric_glob_is_words_not_redirections():
    # zsh's `<->` and `<1-5>` match files named by numbers, so their `<` and
    # `>` redirect nothing, and the word after them stays an argument.
    [words] = guard.split_subcommands('git tag <1-5> v1')
    assert [(str(t), t.syntax) for t in words] == [
        ('git', False), ('tag', False), ('<', False), ('1-5', False), ('>', False),
        ('v1', False)]


def test_a_quoted_word_stays_a_word_in_the_default_reading():
    assert guard.split_subcommands("git branch ')' -D feature") == [
        ['git', 'branch', ')', '-D', 'feature']]
    assert guard.split_subcommands("sed -e 'x{' -e '}' -i f") == [
        ['sed', '-e', 'x{', '-e', '}', '-i', 'f']]


def test_braces_read_as_words_do_not_end_a_command():
    assert guard.split_subcommands('git branch { HEAD', braces=False) == [
        ['git', 'branch', '{', 'HEAD']]
    assert guard.split_subcommands('if [[ -n a ]] git log', braces=False) == [
        ['if', '[[', '-n', 'a', ']]', 'git', 'log']]
    # A `}` alone is syntax wherever it stands in zsh, so it ends one either way.
    assert guard.split_subcommands('{ git log }', braces=False) == [['{', 'git', 'log']]


def test_the_quote_blind_reading_splits_at_a_quoted_separator():
    # How zsh reads a quoted separator once eval hands it back to the shell.
    assert guard.split_subcommands('eval echo \\; rm x', quoting=False) == [
        ['eval', 'echo'], ['rm', 'x']]
    # Only a whole word of punctuation splits, so `sh -c '…'` is still one word.
    assert guard.split_subcommands("sh -c 'git log; rm x'", quoting=False) == [
        ['sh', '-c', 'git log; rm x']]


def test_a_quoted_separator_still_splits_for_eval():
    # eval joins its words and hands them back to the shell, where a quoted `;`
    # separates again. Denied before quoting was tracked, by a split blind to
    # it; still denied by the reading that stays blind to it.
    for command in ('eval echo \\; rm x', "eval echo ';' rm x",
                    "eval 'git log' '&&' git stash"):
        assert guard.classify(command) is not None, command


def test_a_quoted_command_word_is_still_its_command():
    for command in ('"rm" x', '\\rm x', "r''m x", "'git' stash", "g'i't stash"):
        assert guard.classify(command) is not None, command


def test_a_git_option_missing_its_value_fails_closed():
    # The backstop under every reading: wherever one cuts a command between a
    # global option and its value, the verb git would run lies past the cut.
    # Bare --exec-path takes no value; it prints the path and exits.
    for command in ('git -C', 'git -c', 'git --namespace', 'git --git-dir',
                    '{ git --namespace ]] stash; }'):
        assert guard.classify(command) is not None, command
    assert guard.classify('git --exec-path') is None


def test_quoted_and_brace_arguments_to_read_only_commands_stay_allowed():
    for command in ("git grep ';'", "git log --grep '>'", "git grep -e '(' -- src",
                    "git log --format='%H {' -1", "git branch --list '>'",
                    'find . -name x -exec grep -l y {} \\;',
                    'git log -n 2 >/dev/null', 'git branch --show-current 2>/dev/null',
                    'exec {fd}>/dev/null', 'git --exec-path',
                    '{ git log; } 2>&1', 'if [[ -n a ]]; then git status; fi'):
        assert guard.classify(command) is None, command


def test_tokenizer_leaves_redirection_intact():
    # '2>&1' lexes as ['2', '>&', '1'] and '>' is not an operator we split on —
    # redirection stays inside its subcommand, per spec D2.
    assert guard.split_subcommands('cat x 2>&1') == [['cat', 'x', '2', '>&', '1']]
    assert guard.split_subcommands('git log > /tmp/f') == [
        ['git', 'log', '>', '/tmp/f']]


def test_tokenizer_does_not_treat_hash_as_a_comment():
    # A real shell only starts a comment at a word boundary; shlex's default
    # commenters would swallow the rest of the line mid-word and hide a mutator.
    assert guard.split_subcommands('foo#;rm -rf x') == [['foo#'], ['rm', '-rf', 'x']]


def test_quoted_arguments_survive_tokenization():
    assert guard.split_subcommands("git log --grep='a && b'") == [
        ['git', 'log', '--grep=a && b']]


def _shlex_tokens(line):
    lexer = shlex.shlex(line, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    lexer.commenters = ''
    return list(lexer)


def _tokenized(tokenize, line):
    try:
        return [str(token) for token in tokenize(line)]
    except ValueError as exc:
        return 'ValueError: ' + str(exc)


# The guard reads words exactly as shlex does, so every rule built on shlex's
# reading holds; its tokenizer only keeps what shlex drops.
SHLEX_EDGE_LINES = [
    '', ' ', 'a b', ' a\tb\r\nc ', "''", '""', "a''", "'' ''", "'a b'", '"a b"',
    "'a\\'", '"a\\"b"', '"a\\\\b"', '"a\\b"', '"a\\$b"', '\\a', '\\\\', '\\ x',
    '\\;', 'a\\', '"a\\', "'a", '"a', "a'b'c", 'a"b"c', "a'>'b", "'>'", '\\>',
    ';', ';;&', '2>&1', 'a>b', 'a >b', '>(rm x)', '$(ls)', ');', ')&&', ';(',
    '{ a; }', '{fd}>f', 'x="a;b"c', 'a#b', "it's", '"it\'s"', "'\\\\'", '\\\n',
    'a\n\nb', '\x0b', 'é b',
]


def test_tokenizer_reads_edge_cases_as_shlex_does():
    for line in SHLEX_EDGE_LINES:
        assert _tokenized(guard._tokenize, line) == _tokenized(_shlex_tokens, line), line


def test_tokenizer_reads_random_lines_as_shlex_does():
    rng = random.Random(20260928)
    alphabet = ' \t\n\'"\\;&|<>(){}]$#a2-'
    for _ in range(4000):
        line = ''.join(rng.choice(alphabet) for _ in range(rng.randrange(14)))
        assert _tokenized(guard._tokenize, line) == _tokenized(_shlex_tokens, line), line


def _flags(line):
    return [(str(t), t.syntax, t.quoted, t.spaced) for t in guard._tokenize(line)]


def test_tokens_keep_what_shlex_drops():
    # (text, syntax, quoted, spaced): an unquoted run of punctuation; any of it
    # quoted or escaped; whitespace or the line's start before it.
    assert _flags('\\;') == [(';', False, True, True)]
    assert _flags('"\\>"') == [('\\>', False, True, True)]
    assert _flags("a'>'b") == [('a>b', False, True, True)]
    assert _flags('2\\>f') == [('2>f', False, True, True)]
    assert _flags(">'f'") == [('>', True, False, True), ('f', False, True, False)]
    assert _flags("''>f") == [
        ('', False, True, True), ('>', True, False, False), ('f', False, False, False)]
    assert _flags("'2'>f") == [
        ('2', False, True, True), ('>', True, False, False), ('f', False, False, False)]
    assert _flags('2>f') == [
        ('2', False, False, True), ('>', True, False, False), ('f', False, False, False)]
    assert _flags('2 >f')[1] == ('>', True, False, True)
    assert _flags('{fd}>f')[1] == ('>', True, False, False)
    assert _flags('{fd} >f')[1] == ('>', True, False, True)


def test_non_git_denylist_entries_are_denied():
    for command in ('rm -rf build', 'mv a b', 'truncate -s 0 f', 'shred f', 'sudo ls'):
        assert guard.classify(command) is not None, command


def test_sed_in_place_is_denied_in_every_spelling():
    for command in ("sed -i 's/a/b/' f", "sed --in-place 's/a/b/' f",
                    "sed -i.bak 's/a/b/' f", "sed -ne 'p' f && sed -i 's/a/b/' f"):
        assert guard.classify(command) is not None, command


def test_read_only_shell_passes():
    for command in ('cat f', 'grep -r x .', 'jq . f.json', 'find . -name "*.py"',
                    "sed -n '1,10p' f", 'uv run pytest -q', 'echo rm', 'ls -la'):
        assert guard.classify(command) is None, command


def test_excluded_mutators_still_pass_per_spec_D2():
    # Consciously excluded: the heuristic cannot separate a /tmp write from a
    # repo write without real path analysis. Documented, not an oversight.
    for command in ('echo x > /tmp/f', 'mkdir -p /tmp/d', 'touch /tmp/f',
                    'cp a b', 'chmod +x s.sh', 'tee /tmp/f'):
        assert guard.classify(command) is None, command


def test_mutator_is_caught_when_it_is_not_the_first_subcommand():
    assert guard.classify('git log --oneline && rm -rf .git') is not None
    assert guard.classify('cat f | grep x ; sudo reboot') is not None


ALWAYS_ALLOWED_GIT_VERBS = [
    'log', 'show', 'diff', 'diff-tree', 'status', 'grep', 'blame', 'ls-files',
    'ls-tree', 'ls-remote', 'cat-file', 'rev-parse', 'rev-list', 'describe',
    'shortlog', 'whatchanged', 'name-rev', 'merge-base', 'for-each-ref',
    'count-objects', 'verify-commit', 'check-ignore', 'check-attr', 'var',
    'help', 'version',
]


def test_every_readonly_git_verb_is_allowed():
    for verb in ALWAYS_ALLOWED_GIT_VERBS:
        assert guard.classify('git ' + verb) is None, verb
    assert guard.classify('git show abc123:src/x.py') is None
    assert guard.classify('git diff --stat main..HEAD') is None


def test_write_verbs_are_denied():
    for verb in ('commit', 'add', 'checkout', 'switch', 'restore', 'reset',
                 'revert', 'merge', 'rebase', 'cherry-pick', 'am', 'apply',
                 'push', 'clone', 'init', 'clean', 'gc', 'prune', 'mv', 'rm'):
        assert guard.classify('git ' + verb + ' x') is not None, verb


def test_mutating_plumbing_is_denied():
    # No recognizable write verb in the name; caught only by failing closed.
    for verb in ('update-ref', 'update-index', 'write-tree', 'commit-tree',
                 'hash-object', 'fast-import', 'filter-branch', 'replace',
                 'symbolic-ref'):
        assert guard.classify('git ' + verb + ' x') is not None, verb


def test_unknown_verb_fails_closed():
    detail = guard.classify('git frobnicate --wat')
    assert detail is not None
    assert 'frobnicate' in detail


def test_fetch_and_pull_are_denied_deliberately_not_incidentally():
    # Spec D7: fetch touches neither the working tree, the index, HEAD, local
    # branch state, nor the worktree list — it is denied for reproducibility
    # (a mid-review fetch moves the artifact under review) and because the
    # controller prepares the diff before dispatching. The denial message must
    # say so, or a future reader "fixes" this as an oversight.
    for verb in ('fetch', 'pull'):
        detail = guard.classify('git ' + verb + ' origin main')
        assert detail is not None, verb
        assert 'deliberate' in detail.lower(), detail
        assert 'controller' in detail.lower(), detail


def test_global_options_are_skipped_when_locating_the_verb():
    assert guard.classify('git -C /other/repo log --oneline') is None
    assert guard.classify('git --no-pager diff') is None
    assert guard.classify('git --git-dir=/x/.git status') is None
    assert guard.classify('git -c core.pager=cat log') is None


def test_global_options_do_not_smuggle_a_write_past_the_guard():
    # -C is exactly how an agent would step outside a guard that only looked at
    # the working directory. This case is load-bearing, not incidental.
    assert guard.classify('git -C /other/repo commit -m x') is not None
    assert guard.classify('git --git-dir=/x/.git push') is not None
    assert guard.classify('git -c user.name=x commit -m y') is not None


def test_bare_git_and_info_flags_are_allowed():
    assert guard.classify('git') is None
    assert guard.classify('git --version') is None
    assert guard.classify('git --help') is None


def test_unknown_global_option_fails_closed():
    assert guard.classify('git --wat log') is not None


def test_git_denial_names_a_read_only_alternative_where_one_exists():
    detail = guard.classify('git checkout main -- src/x.py')
    assert detail is not None
    assert 'git show' in detail


MODE_DEPENDENT_PAIRS = [
    # (allowed command, denied command)
    ('git stash list', 'git stash'),
    ('git stash show', 'git stash pop'),
    ('git worktree list', 'git worktree add ../wt main'),
    ('git submodule status', 'git submodule update --init'),
    ('git notes list', 'git notes add -m x'),
    ('git bisect log', 'git bisect start'),
    ('git sparse-checkout list', 'git sparse-checkout set src'),
    ('git remote -v', 'git remote add origin url'),
    ('git remote show origin', 'git remote remove origin'),
    ('git remote get-url origin', 'git remote set-url origin url'),
    ('git reflog', 'git reflog delete HEAD@{0}'),
    ('git reflog show HEAD', 'git reflog expire --all'),
    ('git branch', 'git branch new-feature'),
    ('git branch -v', 'git branch -d old'),
    ('git branch -a', 'git branch -m old new'),
    ('git branch --show-current', 'git branch -f main HEAD~1'),
    ("git branch --list 'f*'", 'git branch --edit-description'),
    ('git branch --merged main', 'git branch --unset-upstream'),
    ('git tag -l', 'git tag v1.0'),
    ("git tag --list 'v*'", 'git tag -a v1 -m x'),
    ('git tag --points-at HEAD', 'git tag -d v1'),
    ('git config --get user.name', 'git config user.name Someone'),
    ('git config --list', 'git config --unset user.name'),
    ('git config --get-regexp "^remote"', 'git config --add k v'),
]


def test_mode_dependent_verbs_allow_the_read_only_form():
    for allowed, _ in MODE_DEPENDENT_PAIRS:
        assert guard.classify(allowed) is None, allowed


def test_mode_dependent_verbs_deny_every_other_form():
    for _, denied in MODE_DEPENDENT_PAIRS:
        assert guard.classify(denied) is not None, denied


def test_bare_stash_is_denied_because_it_mutates():
    # The one case where the bare verb is the dangerous one: `git stash` with no
    # subcommand stashes the caller's uncommitted work.
    detail = guard.classify('git stash')
    assert detail is not None
    assert 'stash list' in detail


def test_positional_without_a_list_flag_denies_for_branch_and_tag():
    assert guard.classify('git branch foo') is not None
    assert guard.classify('git tag v1') is not None
    assert guard.classify("git branch --list 'f*'") is None
    assert guard.classify("git tag -l 'v*'") is None


def test_config_requires_a_read_mode_flag():
    assert guard.classify('git config a b') is not None
    assert guard.classify('git config --get a') is None
    # Faithful to the spec table: only the five read-mode flags are listed, so a
    # scope flag denies. Documented in hooks/README.md as a known false positive.
    assert guard.classify('git config --global --list') is not None


def test_value_taking_flags_do_not_look_like_positionals():
    for command in ('git branch --contains HEAD', 'git branch --no-merged main',
                    'git branch --sort=-committerdate', 'git tag --sort refname',
                    'git tag --format="%(refname)"'):
        assert guard.classify(command) is None, command


def run_hook(stdin_text, env=None):
    """Drive the hook exactly as Claude Code does: through its own shebang.

    Not [sys.executable, GUARD]. The shebang resolves to the first python3 on
    the child's PATH, and with env=None that is this test's PATH — under
    `uv run` it is uv's pinned interpreter, never reliably the 3.9 floor. The
    floor is checked by passing guard_env's launchd PATH, not by PATH order.
    """
    return subprocess.run([str(GUARD)], input=stdin_text, capture_output=True,
                          text=True, env=env)


def run_guard(payload, env=None):
    return run_hook(json.dumps(payload), env)


@functools.lru_cache(maxsize=None)
def floor_python_skip_reason():
    """Why the launchd-PATH python3 cannot stand in for the floor, or None."""
    probe = subprocess.run(
        ['/usr/bin/env', 'python3', '-c',
         'import sys; print(sys.executable, *sys.version_info[:2])'],
        capture_output=True, text=True, env=dict(os.environ, PATH=LAUNCHD_PATH))
    if probe.returncode != 0:
        # macOS without the Command Line Tools ships /usr/bin/python3 as a stub
        # that exits non-zero, so a present path is not a runnable interpreter.
        return (f'no runnable python3 on PATH={LAUNCHD_PATH} '
                f'(exit {probe.returncode}: {probe.stderr.strip()[:200]})')
    executable, major, minor = probe.stdout.split()
    if (int(major), int(minor)) != FLOOR_PYTHON:
        # A newer system python3 would pass silently while the docs still
        # promise the floor; skip loudly so the floor gets revisited instead.
        return (f'python3 on PATH={LAUNCHD_PATH} is {executable} {major}.{minor}, '
                f'not the {FLOOR_PYTHON[0]}.{FLOOR_PYTHON[1]} floor')
    return None


@pytest.fixture(params=['test-path', 'launchd-path'])
def guard_env(request):
    """Run each contract test on this test's PATH, then on launchd's.

    The launchd-path run is the check that the guard still works under the
    FLOOR_PYTHON system python3; it skips, naming the reason, where that
    interpreter is missing or is not the floor.
    """
    if request.param == 'test-path':
        return None
    reason = floor_python_skip_reason()
    if reason is not None:
        pytest.skip(reason)
    return dict(os.environ, PATH=LAUNCHD_PATH)


def payload_for(command, agent='Explore'):
    p = copy.deepcopy(RECORDED_PAYLOAD)
    p['tool_input']['command'] = command
    if agent is None:
        p.pop('agent_type', None)
    else:
        p['agent_type'] = agent
    return p


def test_malformed_stdin_allows(guard_env):
    proc = run_hook('not json at all', guard_env)
    assert proc.returncode == 0
    assert proc.stdout.strip() == ''


def test_empty_stdin_allows(guard_env):
    proc = run_hook('', guard_env)
    assert proc.returncode == 0
    assert proc.stdout.strip() == ''


def test_main_session_is_never_blocked(guard_env):
    # The property everything else rests on.
    proc = run_guard(payload_for('git stash', agent=None), guard_env)
    assert proc.returncode == 0
    assert proc.stdout.strip() == ''
    main = run_guard(copy.deepcopy(RECORDED_MAIN_SESSION_PAYLOAD), guard_env)
    assert main.returncode == 0
    assert main.stdout.strip() == ''


def test_unguarded_agents_are_allowed(guard_env):
    for agent in ('debugger', 'docs-writer', 'general-purpose', 'explore'):
        proc = run_guard(payload_for('git commit -m x', agent=agent), guard_env)
        assert proc.returncode == 0, agent
        assert proc.stdout.strip() == '', agent


def test_guarded_agent_running_a_readonly_command_is_allowed(guard_env):
    for agent in sorted(guard.READONLY_AGENTS):
        proc = run_guard(payload_for('git diff main..HEAD', agent=agent), guard_env)
        assert proc.returncode == 0
        assert proc.stdout.strip() == '', agent


def test_guarded_agent_running_a_mutator_is_denied(guard_env):
    for agent in sorted(guard.READONLY_AGENTS):
        proc = run_guard(payload_for('git stash', agent=agent), guard_env)
        assert proc.returncode == 0, agent
        out = json.loads(proc.stdout)
        assert out['hookSpecificOutput']['permissionDecision'] == 'deny', agent


def test_deny_payload_has_the_exact_documented_shape(guard_env):
    proc = run_guard(payload_for('git checkout main'), guard_env)
    out = json.loads(proc.stdout)
    assert set(out) == {'hookSpecificOutput'}
    inner = out['hookSpecificOutput']
    assert set(inner) == {'hookEventName', 'permissionDecision',
                          'permissionDecisionReason'}
    assert inner['hookEventName'] == 'PreToolUse'
    assert inner['permissionDecision'] == 'deny'


def test_denial_reason_names_agent_command_clause_and_alternative(guard_env):
    proc = run_guard(payload_for('git checkout main', agent='task-reviewer'), guard_env)
    reason = json.loads(proc.stdout)['hookSpecificOutput']['permissionDecisionReason']
    assert 'task-reviewer' in reason
    assert 'git checkout main' in reason
    assert 'worktree list' in reason          # the quoted contract clause
    assert 'git show' in reason               # the read-only alternative


def test_denial_reason_offers_no_escape_hatch(guard_env):
    # Spec D5: the constrained party reads this message. A documented bypass
    # string here would make the guard advisory.
    proc = run_guard(payload_for('rm -rf build'), guard_env)
    reason = json.loads(proc.stdout)['hookSpecificOutput']['permissionDecisionReason']
    lowered = reason.lower()
    for word in ('bypass', 'override', 'escape hatch', 'disable', 'skip this'):
        assert word not in lowered, word


def test_classification_failure_fails_closed_for_a_guarded_agent(guard_env):
    # Unbalanced quote: shlex raises, and after identification the guard denies.
    proc = run_guard(payload_for('git log "unterminated'), guard_env)
    assert proc.returncode == 0
    out = json.loads(proc.stdout)
    assert out['hookSpecificOutput']['permissionDecision'] == 'deny'
    assert 'ValueError' in out['hookSpecificOutput']['permissionDecisionReason']


def test_multiline_quoted_script_from_a_guarded_agent_is_allowed(guard_env):
    for agent in sorted(guard.READONLY_AGENTS):
        proc = run_guard(payload_for(MULTILINE_PYTHON_C, agent=agent), guard_env)
        assert proc.returncode == 0, agent
        assert proc.stdout.strip() == '', agent


def test_unbalanced_quote_spanning_lines_still_fails_closed(guard_env):
    proc = run_guard(payload_for('git log "a\nb'), guard_env)
    out = json.loads(proc.stdout)
    assert out['hookSpecificOutput']['permissionDecision'] == 'deny'
    assert 'ValueError' in out['hookSpecificOutput']['permissionDecisionReason']


def test_classification_failure_still_allows_the_main_session(guard_env):
    proc = run_guard(payload_for('git log "unterminated', agent=None), guard_env)
    assert proc.returncode == 0
    assert proc.stdout.strip() == ''


def test_missing_command_does_not_block(guard_env):
    p = copy.deepcopy(RECORDED_PAYLOAD)
    p['tool_input'] = {}
    proc = run_guard(p, guard_env)
    assert proc.returncode == 0
    assert proc.stdout.strip() == ''
