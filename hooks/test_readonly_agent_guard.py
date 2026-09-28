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


def test_backslash_is_literal_inside_single_quotes():
    # Where a quote closes must match shlex exactly: if the split thinks a quote
    # is still open when shlex does not, a newline folds a mutator into a word.
    assert guard.split_subcommands("echo 'a\\'\nrm x") == [['echo', 'a\\'], ['rm', 'x']]


def test_backslash_newline_continues_the_command():
    assert guard.split_subcommands(
        'uv run --python 3.13 --with pytest \\\n  python -m pytest -q') == [[
            'uv', 'run', '--python', '3.13', '--with', 'pytest',
            'python', '-m', 'pytest', '-q']]
    # Splitting at the continuation instead would strand the verb or the flag in
    # a subcommand of its own, where nothing classifies it.
    assert 'stash' in guard.classify('git \\\n  stash')
    assert 'sed -i' in guard.classify('sed \\\n  -i s/a/b/ f')


def test_escaped_backslash_before_a_newline_is_not_a_continuation():
    # `a\\` ends in a literal backslash, so the newline after it still ends the
    # command. Taking it as a continuation would glue `rm` onto `echo`'s word.
    assert guard.split_subcommands('echo a\\\\\nrm x') == [['echo', 'a\\'], ['rm', 'x']]


def test_comment_text_is_not_tokenized():
    # An apostrophe in a comment is not a quote to the shell, so it must not be
    # one to the tokenizer. Agents annotate multi-line commands this way.
    assert guard.split_subcommands("# what's changed\ngit diff main..HEAD") == [
        ['git', 'diff', 'main..HEAD']]
    assert guard.split_subcommands("git log  # don't page\ngit status") == [
        ['git', 'log'], ['git', 'status']]
    assert guard.split_subcommands("git log;# don't\nrm x") == [
        ['git', 'log'], ['rm', 'x']]


def test_comment_cannot_hide_a_mutator():
    # Tokenized, the apostrophes in these two comments would pair into one
    # quoted word and swallow the `git stash` between them.
    assert 'stash' in guard.classify("# what's here\ngit stash\n# let's see")
    # A backslash in a comment is literal: the comment ends at its newline
    # rather than continuing into the next line.
    assert '`rm`' in guard.classify('# note \\\nrm x')


def test_hash_that_does_not_start_a_word_is_not_a_comment():
    assert guard.split_subcommands("git log --grep '# x'") == [
        ['git', 'log', '--grep', '# x']]
    # An escaped space keeps the `#` mid-word, like `foo#` below.
    assert guard.split_subcommands('echo a\\ #b') == [['echo', 'a #b']]


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
