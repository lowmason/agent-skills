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
PINNED_SHA256 = '66c454b94dea0f81334f36b222775b62b6ec24e25c0e62308f23c550ef3eaa3d'
SYSTEM_PYTHON = Path('/usr/bin/python3')
FENCE = '`' * 3
USAGE_ERROR = 2  # the exit status of argparse's parser.error()


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


def test_a_contracted_or_negated_modal_hedge_is_never_flagged():
    text = 'The job cannot have run. It won\'t have stopped. It can\'t very well have failed.\n'
    result = lint('--json', stdin=text)
    assert json.loads(result.stdout)['violations'] == []


def test_skill_front_matter_keys_other_than_the_description_are_not_read_as_prose():
    value = ' '.join(['word'] * 30)
    text = f'---\nname: {value}.\nlicense: x; y\ndescription: Use it.\n---\nThe job runs.\n'
    result = lint('--json', stdin=text)
    assert json.loads(result.stdout)['violations'] == []


def test_a_literal_star_after_a_period_does_not_end_the_sentence():
    # 14 words, then `file.*`, then 14 words: one 29-word sentence over the 25-word cap.
    half = ' '.join(['word'] * 14)
    result = lint('--json', stdin=f'{half} file.* {half}.\n')
    violations = json.loads(result.stdout)['violations']
    assert [v['rule'] for v in violations] == ['long-sentence']


def test_a_bold_closer_after_a_period_still_ends_the_sentence():
    half = ' '.join(['word'] * 14)
    result = lint('--json', stdin=f'**{half}.** {half}.\n')
    assert json.loads(result.stdout)['violations'] == []


def test_a_file_name_is_not_read_as_a_rotated_verb():
    # "verify" inside the script name names no action, so "check" has no rival.
    result = lint('--json', stdin='Check the cache. Then run verify-geometry.py on it.\n')
    assert json.loads(result.stdout)['violations'] == []


def test_a_file_that_is_not_utf8_exits_with_the_usage_error(tmp_path):
    bad = tmp_path / 'latin1.md'
    bad.write_bytes('Café menu.\n'.encode('latin-1'))
    result = lint(str(bad))
    assert result.returncode == USAGE_ERROR
    assert f'cannot read {bad}' in result.stderr
    assert 'Traceback' not in result.stderr


def test_skill_front_matter_description_is_read_as_prose():
    description = ' '.join(['word'] * 30)
    text = f'---\nname: x\ndescription: {description}.\n---\nThe job runs.\n'
    result = lint('--json', stdin=text)
    violations = json.loads(result.stdout)['violations']
    assert [(v['rule'], v['line']) for v in violations] == [('long-sentence', 3)]


def test_bare_url_semicolon_is_not_prose():
    inside = json.loads(lint('--json', stdin='See https://x.io/a;b for it.\n').stdout)
    assert [v for v in inside['violations'] if v['rule'] == 'semicolon'] == []
    after = json.loads(lint('--json', stdin='See https://x.io/a; then go.\n').stdout)
    assert [v['col'] for v in after['violations'] if v['rule'] == 'semicolon'] == [19]


def test_wrapped_phrasal_verb_is_found():
    report = json.loads(lint('--json', stdin='Next we spin\nup the server.\n').stdout)
    found = [(v['line'], v['col']) for v in report['violations'] if v['rule'] == 'phrasal-verb']
    assert found == [(1, 9)]
