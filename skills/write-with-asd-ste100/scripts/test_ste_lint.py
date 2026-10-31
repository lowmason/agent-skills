'''Tests for the vendored ste-lint.py. The file is danyuchn's linter, copied unchanged
from the commit that ../LICENSE-write-with-asd-ste100-sources pins, so these tests pin
its bytes and run its own self-test instead of testing its internals.

Run from this directory: uv run --with pytest python -m pytest -q
'''
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

LINTER = Path(__file__).resolve().parent / 'ste-lint.py'
PINNED_SHA256 = '90a1d6b84c7708b56a8e6ad139e303c8e668af122a5140fe57614444eeff1ff7'
SYSTEM_PYTHON = Path('/usr/bin/python3')
FENCE = '`' * 3


def lint(*args: str, stdin: str = '', python: Path = Path(sys.executable)) -> subprocess.CompletedProcess:
    return subprocess.run([str(python), str(LINTER), *args], input=stdin, capture_output=True, text=True)


def test_the_copy_matches_the_pinned_upstream_bytes():
    assert hashlib.sha256(LINTER.read_bytes()).hexdigest() == PINNED_SHA256


def test_selftest_passes():
    result = lint('--selftest')
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == 'selftest OK'


@pytest.mark.skipif(not SYSTEM_PYTHON.exists(), reason='no /usr/bin/python3 here')
def test_selftest_passes_under_the_system_python():
    result = lint('--selftest', python=SYSTEM_PYTHON)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == 'selftest OK'


def test_json_report_names_the_rules_and_counts_words():
    result = lint('--json', stdin='The panel is removed; spin up the job.\n')
    report = json.loads(result.stdout)
    assert result.returncode == 1
    assert {'semicolon', 'phrasal-verb', 'passive-voice'} <= {v['rule'] for v in report['violations']}
    assert report['words'] == 8


def test_hedges_and_fenced_code_are_never_flagged():
    text = f'The request may have failed.\n\n{FENCE}\nx = 1; y = 2\n{FENCE}\n'
    result = lint('--json', stdin=text)
    assert result.returncode == 0, result.stdout
    assert json.loads(result.stdout)['violations'] == []


def test_a_hedge_with_an_adverb_before_have_is_never_flagged():
    text = 'The job might already have run. It could not possibly have stopped.\n'
    result = lint('--json', stdin=text)
    assert json.loads(result.stdout)['violations'] == []


def test_skill_front_matter_is_not_read_as_prose():
    description = ' '.join(['word'] * 30)
    text = f'---\nname: x\ndescription: {description}.\n---\nThe job runs.\n'
    result = lint('--json', stdin=text)
    assert json.loads(result.stdout)['violations'] == []
