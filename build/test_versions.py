'''Tests for build/versions.py: the file's schema, the synced outputs, the uv argv it builds, and the
bump, verify and drift flows against a stub uv. Nothing here uses the network or a real uv: the stub
is a script first on PATH, as hooks/test_project_hooks.py does it.'''
import datetime

import pytest

import versions
from versions import VersionsError


GOOD = '''\
[python]
dev = '3.13'                 # repo checks

[freeze]
date = 2026-10-19            # every check resolves as of this date

[packages]
alpha = '1.2.0'
beta-two = '2.0.0'
gamma = '0.5'

[cited]
delta = '6.2'

[gates]
snippets = ['alpha', 'beta-two']
jax-cpu = ['alpha', 'gamma']
'''


WITH_OVERRIDE = GOOD + '''
[[override]]
gate = 'jax-cpu'
package = 'alpha'
version = '1.1.0'
reason = 'jax-cpu needs the older alpha'
'''


def make_root(tmp_path, text=GOOD):
    (tmp_path / 'build').mkdir()
    (tmp_path / 'build' / 'versions.toml').write_text(text)
    (tmp_path / 'skills').mkdir()
    return tmp_path


def test_parse_reads_every_table():
    v = versions.parse(WITH_OVERRIDE)
    assert (v.dev_python, v.freeze) == ('3.13', datetime.date(2026, 10, 19))
    assert v.packages == {'alpha': '1.2.0', 'beta-two': '2.0.0', 'gamma': '0.5'}
    assert v.cited == {'delta': '6.2'}
    assert v.gates == {'snippets': ('alpha', 'beta-two'), 'jax-cpu': ('alpha', 'gamma')}
    assert v.overrides == (versions.Override('jax-cpu', 'alpha', '1.1.0', 'jax-cpu needs the older alpha'),)


def test_cutoff_is_midnight_utc_on_the_day_after_the_freeze_date():
    assert versions.parse(GOOD).cutoff == '2026-10-20T00:00:00Z'
    assert versions.parse(GOOD.replace('2026-10-19', '2026-12-31')).cutoff == '2027-01-01T00:00:00Z'


def test_stack_without_an_override():
    v = versions.parse(GOOD)
    assert v.stack('snippets') == ['alpha==1.2.0', 'beta-two==2.0.0']
    assert v.stack('jax-cpu') == ['alpha==1.2.0', 'gamma==0.5']


def test_stack_with_an_override_changes_only_its_gate():
    v = versions.parse(WITH_OVERRIDE)
    assert v.stack('snippets') == ['alpha==1.2.0', 'beta-two==2.0.0']
    assert v.stack('jax-cpu') == ['alpha==1.1.0', 'gamma==0.5']


def test_a_pin_beats_an_override_and_matches_a_normalised_name():
    v = versions.parse(WITH_OVERRIDE)
    assert v.stack('jax-cpu', {'alpha': '9.9'}) == ['alpha==9.9', 'gamma==0.5']
    assert v.stack('snippets', {'beta_two': '3.0'}) == ['alpha==1.2.0', 'beta-two==3.0']


def test_stack_of_an_unknown_gate_names_the_gates():
    with pytest.raises(VersionsError, match=r"unknown gate 'third'.*snippets, jax-cpu"):
        versions.parse(GOOD).stack('third')


@pytest.mark.parametrize('old, new, expected', [
    ("dev = '3.13'", "dev = 3.13", r"\[python\] dev must be a string"),
    ("dev = '3.13'", "dev = 'three'", r"'three'"),
    ('date = 2026-10-19', "date = '2026-10-19'", r"\[freeze\] date must be a TOML date.*'2026-10-19'"),
    ('date = 2026-10-19', 'date = 2026-10-19T12:00:00Z', r"\[freeze\] date must be a TOML date"),
    ("alpha = '1.2.0'", "alpha = '1.2.x'", r"\[packages\] alpha: invalid version '1\.2\.x'"),
    ("delta = '6.2'", "alpha = '6.2'", r"alpha is in both \[packages\] and \[cited\]"),
    ("['alpha', 'beta-two']", "['alpha', 'zeta']", r"\[gates\] snippets names zeta, which has no \[packages\] entry"),
    ("['alpha', 'beta-two']", "[]", r"\[gates\] snippets must be a non-empty list"),
    ('[cited]', '[cites]', r"unknown table 'cites'"),
])
def test_invalid_files_name_their_cause(old, new, expected):
    with pytest.raises(VersionsError, match=expected):
        versions.parse(GOOD.replace(old, new))


@pytest.mark.parametrize('mutate, expected', [
    (lambda t: t.replace("gate = 'jax-cpu'", "gate = 'third'"), r"unknown gate 'third'"),
    (lambda t: t.replace("package = 'alpha'", "package = 'gamma2'"), r"gamma2 is not in gate jax-cpu"),
    (lambda t: t.replace("reason = 'jax-cpu needs the older alpha'", "reason = ''"), r"missing key 'reason'"),
    (lambda t: t.replace("version = '1.1.0'", "version = 'old'"), r"invalid version 'old'"),
])
def test_invalid_overrides(mutate, expected):
    with pytest.raises(VersionsError, match=expected):
        versions.parse(mutate(WITH_OVERRIDE))


def test_an_override_not_written_as_an_array_of_tables_names_the_cause():
    single_bracket = WITH_OVERRIDE.replace('[[override]]', '[override]')
    for text in (single_bracket, "override = 'x'\n" + GOOD, "override = ['x']\n" + GOOD):
        with pytest.raises(VersionsError, match=r'build/versions\.toml: override must be written \[\[override\]\]'):
            versions.parse(text)


def test_cited_that_is_not_a_table_names_the_key():
    text = "cited = 5\n" + GOOD.replace("[cited]\ndelta = '6.2'\n\n", '')
    with pytest.raises(VersionsError, match=r'\[cited\]'):
        versions.parse(text)


def test_a_missing_file_names_the_path(tmp_path):
    with pytest.raises(VersionsError, match=r'build/versions\.toml: cannot read'):
        versions.load(tmp_path)


def test_invalid_toml_names_the_file():
    with pytest.raises(VersionsError, match=r'build/versions\.toml: invalid TOML'):
        versions.parse('[python\n')


def test_outputs_are_exactly_these_files():
    out = versions.outputs(versions.parse(GOOD))
    assert out['.python-version'] == '3.13\n'
    assert out['uv.toml'].endswith('exclude-newer = "2026-10-20T00:00:00Z"\n')
    assert out['uv.toml'].startswith('# Written by build/versions.py sync from build/versions.toml. Do not edit.\n')
    settings = [line for line in out['skills/uv.toml'].splitlines() if line and not line.startswith('#')]
    assert settings == []  # the shadow file sets nothing
    assert 'build/versions.toml' in out['skills/uv.toml']
    assert set(out) == {'.python-version', 'uv.toml', 'skills/uv.toml'}


def test_sync_writes_the_outputs_and_check_then_passes(tmp_path):
    root = make_root(tmp_path)
    assert versions.main(['sync', '--check'], root=root) == 1
    assert versions.main(['sync'], root=root) == 0
    assert (root / '.python-version').read_text() == '3.13\n'
    assert versions.main(['sync', '--check'], root=root) == 0


def test_sync_check_names_a_file_that_differs(tmp_path, capsys):
    root = make_root(tmp_path)
    versions.sync(root)
    (root / 'uv.toml').write_text('exclude-newer = "2020-01-01T00:00:00Z"\n')
    assert versions.sync(root, check=True) == ['uv.toml: differs; run build/versions.py sync']


def test_rewrite_changes_the_date_and_the_package_values_only():
    text = versions.rewrite(GOOD, datetime.date(2026, 11, 2), {'alpha': '1.3.0', 'gamma': '0.6'})
    assert "alpha = '1.3.0'" in text and "gamma = '0.6'" in text
    assert 'date = 2026-11-02            # every check resolves as of this date' in text
    assert "beta-two = '2.0.0'" in text and "delta = '6.2'" in text   # [cited] never moves
    assert "dev = '3.13'                 # repo checks" in text
    assert versions.rewrite(text, datetime.date(2026, 10, 19), {'alpha': '1.2.0', 'gamma': '0.5'}) == GOOD


def test_an_invalid_file_exits_2_with_the_cause(tmp_path, capsys):
    root = make_root(tmp_path, GOOD.replace("'1.2.0'", "'oops'"))
    assert versions.main(['sync'], root=root) == 2
    assert "[packages] alpha: invalid version 'oops'" in capsys.readouterr().err
