'''Tests for guard.py, the kit's PreToolUse real-home guard (plan 100, Task 1).

Each test runs guard.py under /usr/bin/python3, the interpreter the hook runs
on in production, with HOME set to a temporary rep home. That home holds a
Library/Keychains symlink into a temporary "real home".
'''

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

import pytest

GUARD = Path(__file__).resolve().parent / 'guard.py'
PREFIX = 'blocked by the workspace path guard:'
INTERNAL = PREFIX + ' internal error'


@pytest.fixture
def homes(tmp_path: Path) -> tuple[Path, Path]:
    real = tmp_path / 'real'
    (real / 'Library' / 'Keychains').mkdir(parents=True)
    (real / '.claude' / 'skills').mkdir(parents=True)
    rep = tmp_path / 'rep'
    (rep / 'Library').mkdir(parents=True)
    (rep / 'Library' / 'Keychains').symlink_to(real / 'Library' / 'Keychains')
    (rep / 'work' / 'r281').mkdir(parents=True)
    skill = rep / '.claude' / 'skills' / 'prepare-handoff' / 'SKILL.md'
    skill.parent.mkdir(parents=True)
    skill.write_text('kit copy\n')
    return rep, real


def run_guard(stdin: str, rep: Path, real: Path, args: list[str] | None = None,
              extra_env: dict | None = None) -> subprocess.CompletedProcess:
    argv = ['--real-home', str(real)] if args is None else args
    done = subprocess.run(
        ['/usr/bin/python3', str(GUARD), *argv],
        input=stdin, capture_output=True, text=True,
        env={'HOME': str(rep), 'PATH': '/usr/bin:/bin', **(extra_env or {})}, check=False,
    )
    assert done.returncode == 0, done.stderr
    return done


def decide(tool: str, tool_input: dict, rep: Path, real: Path, cwd: Path | None = None,
           extra_env: dict | None = None) -> str | None:
    payload = {
        'hook_event_name': 'PreToolUse', 'tool_name': tool, 'tool_input': tool_input,
        'cwd': str(cwd or rep / 'work' / 'r281'),
    }
    done = run_guard(json.dumps(payload), rep, real, extra_env=extra_env)
    if not done.stdout.strip():
        return None
    out = json.loads(done.stdout)['hookSpecificOutput']
    assert out['hookEventName'] == 'PreToolUse'
    assert out['permissionDecision'] == 'deny'
    return out['permissionDecisionReason']


def assert_denied(reason: str | None, cause: str) -> None:
    assert reason is not None
    assert reason.startswith(PREFIX)
    assert not reason.startswith(INTERNAL), reason
    assert cause in reason, reason


def test_denies_for_loop_absolute_real_home(homes):
    rep, real = homes
    reason = decide('Bash', {'command': f'for d in a b; do ls {real}/.claude/skills 2>/dev/null; done'}, rep, real)
    assert_denied(reason, 'real home')


def test_denies_system_volumes_form(homes):
    rep, real = homes
    reason = decide('Bash', {'command': f'cat /System/Volumes/Data{real}/x'}, rep, real)
    assert_denied(reason, 'real home')


def test_denies_through_keychain_link(homes):
    rep, real = homes
    reason = decide('Bash', {'command': 'ls ~/Library/Keychains/../..'}, rep, real)
    assert_denied(reason, 'Library/Keychains')
    reason = decide('Read', {'file_path': f'{rep}/Library/Keychains/x'}, rep, real)
    assert_denied(reason, 'Library/Keychains')


def test_denies_keychains_name(homes):
    rep, real = homes
    reason = decide('Bash', {'command': 'for d in Library/Keychains; do ls ~/$d; done'}, rep, real)
    assert_denied(reason, 'Library/Keychains')


def test_allows_tilde_kit_read(homes):
    rep, real = homes
    assert decide('Bash', {'command': 'for d in .claude/skills; do ls ~/$d; done'}, rep, real) is None
    assert decide('Read', {'file_path': '~/.claude/skills/prepare-handoff/SKILL.md'}, rep, real) is None


def test_allows_repo_relative(homes):
    rep, real = homes
    assert decide('Bash', {'command': 'git status && ls ../'}, rep, real, cwd=rep / 'work' / 'r281') is None


def test_malformed_payload_denies(homes):
    rep, real = homes
    done = run_guard('not json', rep, real)
    out = json.loads(done.stdout)['hookSpecificOutput']
    assert out['permissionDecision'] == 'deny'
    assert out['permissionDecisionReason'].startswith(INTERNAL)


# --- shapes beyond the plan's seven tests (mutant step) ---


def test_home_forms_climbing_out_deny(homes):
    rep, real = homes
    for form in ('~', '$HOME', '${HOME}'):
        reason = decide('Bash', {'command': f'ls {form}/../real/.claude'}, rep, real)
        assert_denied(reason, 'real home')
    assert decide('Bash', {'command': 'ls $HOME/.claude/skills ${HOME}/work'}, rep, real) is None


def test_heredoc_body_is_content(homes):
    rep, real = homes
    assert decide('Bash', {'command': f'cat > notes.md <<EOF\nsee {real}/x\nEOF'}, rep, real) is None
    reason = decide('Bash', {'command': f'cat {real}/x <<EOF\nhi\nEOF'}, rep, real)
    assert_denied(reason, 'real home')


def test_denies_each_path_field(homes):
    rep, real = homes
    assert_denied(decide('Grep', {'pattern': 'x', 'path': str(real)}, rep, real), 'real home')
    assert_denied(decide('NotebookEdit', {'notebook_path': f'{real}/n.ipynb'}, rep, real), 'real home')
    assert_denied(decide('Glob', {'pattern': f'{real}/**/*.md'}, rep, real), 'real home')
    assert_denied(decide('Glob', {'pattern': '**/*.md', 'path': str(real.parent)}, rep, real), 'real home')
    assert decide('Glob', {'pattern': '**/*.md', 'path': str(rep)}, rep, real) is None
    assert decide('Glob', {'pattern': '**/*.md'}, rep, real) is None


def test_grep_pattern_is_not_a_path(homes):
    rep, real = homes
    assert decide('Grep', {'pattern': str(real), 'path': str(rep)}, rep, real) is None


def test_relative_file_path_resolves_against_cwd(homes):
    rep, real = homes
    assert_denied(decide('Read', {'file_path': 'notes.md'}, rep, real, cwd=real), 'real home')
    assert decide('Read', {'file_path': 'notes.md'}, rep, real) is None


def test_case_and_variable_forms_deny(homes):
    rep, real = homes
    assert_denied(decide('Bash', {'command': f'ls {str(real).upper()}'}, rep, real), 'real home')
    reason = decide('Bash', {'command': f'ls {real.parent}/$WHO/.claude'}, rep, real, extra_env={'WHO': 'real'})
    assert_denied(reason, 'real home')


def test_glob_above_real_home_denies(homes):
    rep, real = homes
    assert_denied(decide('Bash', {'command': f'ls {real.parent}/*/.claude'}, rep, real), 'real home')
    assert decide('Bash', {'command': 'ls docs/**/*.md ~/.claude/skills/*'}, rep, real) is None
    assert decide('Bash', {'command': 'ls /*'}, rep, real) is None


def test_internal_errors_deny(homes):
    rep, real = homes
    payload = json.dumps({'tool_name': 'Bash', 'tool_input': {'command': 'ls'}, 'cwd': str(rep)})
    for args in ([], ['--real-home'], ['--other', str(real)]):
        out = json.loads(run_guard(payload, rep, real, args=args).stdout)['hookSpecificOutput']
        assert out['permissionDecisionReason'].startswith(INTERNAL)
    bad = json.dumps({'tool_name': 'Read', 'tool_input': ['x'], 'cwd': str(rep)})
    out = json.loads(run_guard(bad, rep, real).stdout)['hookSpecificOutput']
    assert out['permissionDecisionReason'].startswith(INTERNAL)


def test_symlink_and_sibling_resolve(homes):
    rep, real = homes
    (rep / 'work' / 'door').symlink_to(real)
    (real.parent / 'real2').mkdir()
    assert_denied(decide('Bash', {'command': 'ls ../door/.claude'}, rep, real), 'real home')
    assert_denied(decide('Read', {'file_path': f'{rep}/work/door/x'}, rep, real), 'real home')
    assert decide('Bash', {'command': f'ls {real.parent}/real2/x'}, rep, real) is None


def test_real_home_argument_resolves(homes):
    rep, real = homes
    alias = real.parent / 'alias'
    alias.symlink_to(real)
    payload = json.dumps({'tool_name': 'Bash', 'tool_input': {'command': f'ls {real}/.claude'}, 'cwd': str(rep)})
    out = json.loads(run_guard(payload, rep, real, args=['--real-home', str(alias)]).stdout)['hookSpecificOutput']
    assert_denied(out['permissionDecisionReason'], 'real home')


def test_denied_maps_home_forms_to_its_home_argument(homes):
    '''An in-process caller (such as an audit) may run with HOME at the real
    home: denied must map ~, $HOME and ${HOME} to its home argument, not HOME.'''
    rep, real = homes
    code = (
        'import json, sys; sys.path.insert(0, sys.argv[1]); import guard; '
        'print(json.dumps([guard.denied("Bash", {"command": c}, sys.argv[2], sys.argv[2], sys.argv[3]) '
        'for c in ("ls ~/.claude/skills", "ls $HOME/work", "ls ${HOME}/work")]))'
    )
    done = subprocess.run(
        ['/usr/bin/python3', '-I', '-c', code, str(GUARD.parent), str(rep), str(real)],
        capture_output=True, text=True, env={'HOME': str(real), 'PATH': '/usr/bin:/bin'}, check=False,
    )
    assert done.returncode == 0, done.stderr
    assert json.loads(done.stdout) == [None, None, None]


def test_split_keychains_name_denies(homes):
    rep, real = homes
    reason = decide('Bash', {'command': 'for d in Library; do ls ~/$d/Keychains/../..; done'}, rep, real)
    assert_denied(reason, 'Keychains')
    reason = decide('Bash', {'command': 'cd ~/Library && ls Keychains/../../.claude/skills'}, rep, real)
    assert_denied(reason, 'Keychains')


def test_casefolded_keychains_name_denies(homes):
    rep, real = homes
    reason = decide('Bash', {'command': 'for d in library/keychains; do ls ~/$d; done'}, rep, real)
    assert_denied(reason, 'Keychains')


def test_rep_library_folder_denies(homes):
    rep, real = homes
    reason = decide('Bash', {'command': 'cd ~/Library && ls'}, rep, real)
    assert_denied(reason, 'Library folder')


def test_glob_through_keychain_link_denies(homes):
    rep, real = homes
    reason = decide('Bash', {'command': 'ls ~/Library/*/../..'}, rep, real)
    assert_denied(reason, 'real home')


def test_glob_inside_a_name_above_real_home_denies(homes):
    rep, real = homes
    reason = decide('Bash', {'command': f'ls {real.parent}/re*/nothing'}, rep, real)
    assert_denied(reason, 'real home')


def test_quoted_or_escaped_keychains_name_denies(homes):
    rep, real = homes
    reason = decide('Bash', {'command': 'cd ~ && cd Library && cd Key""chains && cat ../../.claude/x'}, rep, real)
    assert_denied(reason, 'Keychains')
    reason = decide('Bash', {'command': 'cat ~/Library/Key\\chains/../../.claude/x'}, rep, real)
    assert_denied(reason, 'Keychains')


def call_denied(rep: Path, real: Path, setup: str, command: str) -> str | None:
    '''Run denied in-process under /usr/bin/python3 after a setup line that
    shrinks a limit, so a limit test stays fast.'''
    code = (
        'import json, sys, time; sys.path.insert(0, sys.argv[1]); import guard; ' + setup + '; '
        'print(json.dumps(guard.denied("Bash", {"command": sys.argv[4]}, sys.argv[2], sys.argv[2], sys.argv[3])))'
    )
    done = subprocess.run(
        ['/usr/bin/python3', '-I', '-c', code, str(GUARD.parent), str(rep), str(real), command],
        capture_output=True, text=True, env={'HOME': str(rep), 'PATH': '/usr/bin:/bin'}, check=False,
    )
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


def test_glob_over_the_match_cap_denies(homes):
    rep, real = homes
    many = rep / 'many'
    many.mkdir()
    for n in range(5):
        (many / f'f{n}').write_text('')
    assert call_denied(rep, real, 'guard.GLOB_LIMIT = 5', 'ls ~/many/*') is None
    assert_denied(call_denied(rep, real, 'guard.GLOB_LIMIT = 4', 'ls ~/many/*'), 'too many matches')


def test_glob_past_the_deadline_denies(homes):
    rep, real = homes
    slow = 'guard.GLOB_SECONDS = 0.2; guard.glob.iglob = lambda p: (time.sleep(2), iter([]))[1]'
    started = time.monotonic()
    assert_denied(call_denied(rep, real, slow, 'ls ~/work/*'), 'took too long')
    assert time.monotonic() - started < 1.5
    assert call_denied(rep, real, 'guard.GLOB_SECONDS = 0.2', 'ls ~/work/*') is None
