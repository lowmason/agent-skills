'''Tests for build/versions_check.py, the lint behind `versions.py check`. Every rule has a positive
control: a seeded stale literal, citation or floor that must fail. The seeded flag text is built from
parts, because the lint reads this file too.'''
import subprocess
import textwrap
from pathlib import Path

import pytest

import versions
import versions_check as vc
from run_suites import git_env

TOML = '''\
[python]
dev = '3.13'
[freeze]
date = 2026-10-19
[packages]
arviz = '1.3.0'
polars = '2.0.0'
numpyro = '0.22.0'
arviz-stats = '1.3.3'
orbax-checkpoint = '0.12.8'
jaxlib = '0.12.0.1'
[cited]
altair = '6.2'
great-docs = '0.17.0'
[gates]
snippets = ['numpyro', 'arviz-stats', 'arviz']
jax-cpu = ['jaxlib', 'orbax-checkpoint']
'''
V = versions.parse(TOML)
FLAG = '--python'


def skill_tree(tmp_path, files):
    for rel, text in files.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(text))
    return tmp_path


def cite(tmp_path, text, historical=None):
    root = skill_tree(tmp_path, {'skills/demo/SKILL.md': text})
    return vc.check_citations(root, V, historical or {})


# ---- equality ------------------------------------------------------------------------------

def test_an_equal_citation_passes_at_its_own_precision(tmp_path):
    text = 'Verified on Polars 2, Polars 2.0, Polars 2.0.0, NumPyro 0.22 and `numpyro==0.22.0`.\n'
    assert cite(tmp_path, text) == []


def test_a_stale_equality_citation_fails(tmp_path):
    findings = cite(tmp_path, 'line one\nThese are verified on Polars 1.42.\n')
    assert len(findings) == 1
    assert findings[0].startswith("skills/demo/SKILL.md:2: 'Polars 1.42': the file says 2.0.0")


def test_a_citation_more_precise_than_the_file_fails(tmp_path):
    assert len(cite(tmp_path, 'Altair 6.2.1 works.\n')) == 1
    assert cite(tmp_path, 'Altair 6.2 works.\n') == []


@pytest.mark.parametrize('text', [
    '**Altair 6.2, Polars 1.42**', 'orbax checkpoint 0.12.6', 'Orbax checkpoint 0.12.6', 'ORBAX-CHECKPOINT 0.12.6',
    'JAXlib 0.11.2', '`polars` 1.42', 'Polars\n  1.42',
])
def test_name_forms_and_line_breaks_are_still_found(tmp_path, text):
    assert cite(tmp_path, text + '\n'), text


def test_a_name_without_a_version_next_to_it_is_ignored(tmp_path):
    assert cite(tmp_path, 'Polars is fast. narwhals 2.x is a library the file does not list.\n') == []


# ---- ranges --------------------------------------------------------------------------------

@pytest.mark.parametrize('text', [
    'polars>=1.0', 'polars >= 2.0', 'polars≥2.0', 'Polars ≥ 2', 'numpyro >= 0.22', 'Python 3.11+', 'Python ≥ 3.11',
    'Python 3.12 or later', 'great-docs>=0.17.0,<0.18', 'great-docs >=0.17.0,<0.18', 'polars<3', 'arviz-stats < 2.0.0',
])
def test_a_range_that_holds_the_files_version_passes(tmp_path, text):
    assert cite(tmp_path, text + '\n') == []


@pytest.mark.parametrize('text', [
    'polars>=2.1', 'numpyro >= 0.23', 'Python 3.14+', 'Python ≥ 3.14', 'great-docs>=0.17.0,<0.17.0', 'polars<2',
    'arviz-stats < 1.0.0', 'polars>2.0',
])
def test_a_range_that_misses_the_files_version_fails(tmp_path, text):
    findings = cite(tmp_path, text + '\n')
    assert len(findings) == 1 and 'outside this range' in findings[0], text


def test_python_is_checked_against_the_dev_interpreter(tmp_path):
    assert cite(tmp_path, 'Needs Python 3.13.\n') == []
    assert len(cite(tmp_path, 'Verified under Python 3.13.8.\n')) == 1


# ---- history -------------------------------------------------------------------------------

def test_a_historical_phrase_passes_whatever_its_case_or_markup(tmp_path):
    text = 'The classic ArviZ 0.23 stack, the `arviz` 0.23 names and arviz-stats < 1.0.0.\n'
    history = {'ArviZ 0.23': 'classic stack', 'arviz-stats < 1.0.0': 'old releases'}
    assert cite(tmp_path, text, history) == []
    assert len(cite(tmp_path, text)) == 3   # without the allowlist all three fail


def test_a_historical_entry_that_matches_nothing_is_reported(tmp_path):
    findings = cite(tmp_path, 'No versions here.\n', {'ArviZ 0.23': 'classic stack'})
    assert findings == ["HISTORICAL entry 'ArviZ 0.23' matches no text under skills/; remove it"]


# ---- scope ---------------------------------------------------------------------------------

def test_only_the_script_header_of_a_python_file_is_read(tmp_path):
    root = skill_tree(tmp_path, {'skills/demo/scripts/tool.py': '''\
        # /// script
        # requires-python = '>=3.11'
        # dependencies = ['polars>=1.0', 'numpyro==0.21.0']
        # ///
        # In the body a comment may say Polars 1.42 without a finding.
        x = 'numpyro 0.21'
        '''})
    findings = vc.check_citations(root, V, {})
    assert len(findings) == 1 and findings[0].startswith("skills/demo/scripts/tool.py:3: 'numpyro==0.21.0'")


def test_test_files_and_files_outside_skills_are_not_read(tmp_path):
    root = skill_tree(tmp_path, {
        'skills/demo/scripts/test_tool.py': "# /// script\n# dependencies = ['polars==1.0']\n# ///\n",
        'specs/plan.md': 'Polars 1.42\n', 'build/notes.md': 'Polars 1.42\n'})
    assert vc.check_citations(root, V, {}) == []


def test_data_directories_fixtures_and_license_files_are_not_read(tmp_path):
    stale = 'Polars 1.0 is stale.\n'
    root = skill_tree(tmp_path, {'skills/demo/data/notes.md': stale, 'skills/demo/fixtures/page.md': stale,
                                 'skills/demo/LICENSE.md': stale, 'skills/demo/SKILL.md': stale})
    assert [f.split(':')[0] for f in vc.check_citations(root, V, {})] == ['skills/demo/SKILL.md']


# ---- floors --------------------------------------------------------------------------------

def skill(compat, floor=None, name='demo'):
    files = {f'skills/{name}/SKILL.md': f'---\nname: {name}\ndescription: Use when testing.\n{compat}\n---\nbody\n'}
    if floor:
        files[f'skills/{name}/scripts/tool.py'] = f"# /// script\n# requires-python = '>={floor}'\n# ///\n"
    return files


def test_a_script_floor_above_the_promised_floor_fails(tmp_path):
    root = skill_tree(tmp_path, skill('compatibility: Requires uv; Python 3.11+.', '3.12'))
    assert vc.check_floors(root, V) == ['skills/demo/scripts/tool.py: requires Python 3.12, but SKILL.md promises 3.11']


def test_a_script_floor_at_or_below_the_promise_passes(tmp_path):
    assert vc.check_floors(skill_tree(tmp_path, skill('compatibility: Python 3.12+.', '3.12')), V) == []
    assert vc.check_floors(skill_tree(tmp_path / 'b', skill('compatibility: Python 3.12+.', '3.11')), V) == []


def test_a_script_without_a_promise_is_not_compared(tmp_path):
    assert vc.check_floors(skill_tree(tmp_path, skill('license: MIT', '3.11')), V) == []


def test_a_folded_compatibility_value_is_read(tmp_path):
    compat = 'compatibility: >\n  Requires uv to run bundled scripts; Python\n  3.11+. Also requires git.'
    root = skill_tree(tmp_path, skill(compat, '3.12'))
    assert 'promises 3.11' in vc.check_floors(root, V)[0]


def test_a_floor_above_the_dev_python_fails_twice_over(tmp_path):
    root = skill_tree(tmp_path, skill('compatibility: Python 3.14+.', '3.14'))
    findings = vc.check_floors(root, V)
    assert any('promises Python 3.14, above the dev Python 3.13' in f for f in findings)
    assert any('requires Python 3.14, above the dev Python 3.13' in f for f in findings)


# ---- interpreter literals ------------------------------------------------------------------

def test_an_interpreter_literal_fails_and_paths_do_not(tmp_path):
    root = skill_tree(tmp_path, {'CLAUDE.md': f'run uv run {FLAG} 3.13 python x.py\n'
                                 f'and uv run {FLAG}=3.12 python y.py\n'
                                 f'and uv run {FLAG} /usr/bin/python3 python z.py\n'
                                 f'and uv pip compile {FLAG}-version 3.13\n'})
    findings = vc.check_literals(root, [root / 'CLAUDE.md'])
    assert [f.split(': ')[0] for f in findings] == ['CLAUDE.md:1', 'CLAUDE.md:2']
    assert "drop the flag, since uv reads .python-version" in findings[0]


def git(repo, *args):
    subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True, env=git_env())


def test_live_files_are_the_listed_files_and_directories_that_git_keeps(tmp_path):
    git(tmp_path, 'init', '-q')
    skill_tree(tmp_path, {'CLAUDE.md': 'x', 'README.md': 'x', 'build/a.py': 'x', 'build/.scratch/b.py': 'x',
                          'skills/s/SKILL.md': 'x', 'specs/plans/p.md': 'x', 'hooks/h.sh': 'x',
                          '.claude/skills/c/SKILL.md': 'x', '.claude/worktrees/w/CLAUDE.md': 'x',
                          '.gitignore': 'build/.scratch/\n.claude/worktrees/\n'})
    git(tmp_path, 'add', 'CLAUDE.md', 'build/a.py', 'skills/s/SKILL.md')   # tracked and untracked files both count
    got = sorted(str(p.relative_to(tmp_path)) for p in vc.live_files(tmp_path))
    assert got == ['.claude/skills/c/SKILL.md', 'CLAUDE.md', 'build/a.py', 'hooks/h.sh', 'skills/s/SKILL.md']


def test_live_files_leave_out_data_fixtures_and_license_files(tmp_path):
    git(tmp_path, 'init', '-q')
    skill_tree(tmp_path, {'skills/s/data/d.md': 'x', 'skills/s/scripts/fixtures/f.md': 'x', 'skills/s/LICENSE': 'x',
                          'skills/s/SKILL.md': 'x'})
    assert [str(p.relative_to(tmp_path)) for p in vc.live_files(tmp_path)] == ['skills/s/SKILL.md']


# ---- the whole lint ------------------------------------------------------------------------

def clean_root(tmp_path):
    git(tmp_path, 'init', '-q')
    root = skill_tree(tmp_path, {'build/versions.toml': TOML, **skill('compatibility: Python 3.11+.', '3.11')})
    (root / 'skills' / 'demo' / 'SKILL.md').write_text(
        '---\nname: demo\ndescription: Use when testing.\ncompatibility: Python 3.11+.\n---\nVerified on Polars 2.0.\n')
    versions.sync(root)
    return root


def test_a_consistent_tree_has_no_findings(tmp_path):
    assert vc.check(clean_root(tmp_path), {}) == []


def test_each_rule_fails_on_its_seeded_defect(tmp_path):
    root = clean_root(tmp_path)
    (root / '.python-version').write_text('3.12\n')
    (root / 'CLAUDE.md').write_text(f'uv run {FLAG} 3.13 python x.py\n')
    (root / 'skills/demo/SKILL.md').write_text(
        '---\nname: demo\ndescription: Use when testing.\ncompatibility: Python 3.10+.\n---\nVerified on Polars 1.42.\n')
    findings = vc.check(root, {})
    assert any(f.startswith('.python-version: differs') for f in findings)
    assert any(f.startswith('CLAUDE.md:1:') for f in findings)
    assert any("'Polars 1.42'" in f for f in findings)
    assert any('requires Python 3.11, but SKILL.md promises 3.10' in f for f in findings)


def test_an_invalid_versions_file_is_one_finding(tmp_path):
    (tmp_path / 'build').mkdir()
    (tmp_path / 'build' / 'versions.toml').write_text("[python]\ndev = 'x'\n")
    assert len(vc.check(tmp_path, {})) == 1 and 'dev must be a string' in vc.check(tmp_path, {})[0]


def test_the_check_command_prints_ok_or_each_finding(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(vc, 'HISTORICAL', {})
    root = clean_root(tmp_path)
    assert versions.main(['check'], root=root) == 0
    assert capsys.readouterr().out == 'versions ok\n'
    (root / 'CLAUDE.md').write_text(f'uv run {FLAG} 3.13 python x.py\n')
    assert versions.main(['check'], root=root) == 1
    out = capsys.readouterr().out.splitlines()
    assert out[0].startswith('CLAUDE.md:1:') and out[-1] == '1 problem(s)'
