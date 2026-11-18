'''Tests for guard.py, the kit's PreToolUse real-home guard (plan 100, Task 1).

Each test runs guard.py under /usr/bin/python3, the interpreter the hook runs
on in production, with HOME set to a temporary rep home. That home holds a
Library/Keychains symlink into a temporary "real home".
'''

from __future__ import annotations

import json
import subprocess
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


def run_guard(stdin: str, rep: Path, real: Path) -> subprocess.CompletedProcess:
    done = subprocess.run(
        ['/usr/bin/python3', str(GUARD), '--real-home', str(real)],
        input=stdin, capture_output=True, text=True,
        env={'HOME': str(rep), 'PATH': '/usr/bin:/bin'}, check=False,
    )
    assert done.returncode == 0, done.stderr
    return done


def decide(tool: str, tool_input: dict, rep: Path, real: Path, cwd: Path | None = None) -> str | None:
    payload = {
        'hook_event_name': 'PreToolUse', 'tool_name': tool, 'tool_input': tool_input,
        'cwd': str(cwd or rep / 'work' / 'r281'),
    }
    done = run_guard(json.dumps(payload), rep, real)
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
