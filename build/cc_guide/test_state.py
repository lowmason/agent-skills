'''Tests for state.py: the manifest, the baseline, PROBES.md, the repo
source and the cache layout (drift spec R2, R6.1).'''
import json
import tomllib
from datetime import date

import pytest

import state
from cc_fixtures import (MANIFEST_TOML, fixture_repo, git, guide_text,  # noqa: F401
                         isolated_home)

STAMP = {'release': '2.1.900', 'date': '2026-09-02'}
SECTION = {'checked': STAMP, 'changed': '2.1.900', 'audited': STAMP, 'text_hash': 'sha256:' + 'a' * 64}


def baseline_text(**changes):
    raw = {'sections': {'alpha.overview': dict(SECTION)},
           'groups': {'alpha': {'blocks': {'tools': {'1' * 16: '0' * 16}}, 'snapshot': {'tools': '2.1.900'}}},
           'llms': ['tools']}
    raw.update(changes)
    return json.dumps(raw)


def test_the_fixture_manifest_parses_in_manifest_order():
    m = state.parse_manifest(MANIFEST_TOML)
    assert list(m.groups) == ['alpha', 'beta']
    assert m.groups['beta'] == state.Group(['beta.overview', 'beta.reference'],
                                           {'events': 'all', 'env-vars': 'terms', 'platform:pricing': 'terms'})
    assert m.pages() == ['tools', 'env-vars', 'events', 'platform:pricing']
    assert m.group_of()['alpha.reference'] == 'alpha'
    assert m.cadence == {'changelog_days': 7, 'probe_days': 7, 'audit_days': 30}
    assert (m.terms, m.probes) == ({}, {})
    assert m.exclusions == [('whats-new/*', 'Duplicates the changelog.')]


def test_every_manifest_problem_is_reported_at_once():
    text = (MANIFEST_TOML.replace('changelog_days = 7', 'changelog_days = 0')
            .replace("llms = 'https://", "llms = 'http://")
            .replace("all = ['events']", "all = ['events', 'whats-new/2026-w40']")
            .replace("sections = ['beta.overview', 'beta.reference']",
                     "sections = ['beta.overview', 'alpha.reference']")
            + "\n[stray]\nkey = 1\n")
    with pytest.raises(state.SetupError) as err:
        state.parse_manifest(text)
    assert str(err.value).split('\n') == [
        f'{state.MANIFEST}: unknown table or key {"stray"!r}',
        f'{state.MANIFEST}: [sources] llms must be an https URL',
        f'{state.MANIFEST}: [cadence] changelog_days must be a positive integer',
        f'{state.MANIFEST}: [groups.beta] alpha.reference is already in group alpha',
        f"{state.MANIFEST}: page whats-new/2026-w40 is mapped but matches exclusion 'whats-new/*'",
    ]
    shapes = (MANIFEST_TOML.replace('[guide]\npath = ', 'guide = ').replace('[[exclusion]]', '[exclusion]')
              + "\n[sections]\n'alpha.overview' = 1\n\n[probe]\nid = 'x'\n")
    with pytest.raises(state.SetupError) as err:
        state.parse_manifest(shapes)
    assert str(err.value).split('\n') == [
        f'{state.MANIFEST}: [guide] must be a table',
        f'{state.MANIFEST}: [guide] path must be a non-empty string',
        f"{state.MANIFEST}: [sections.'alpha.overview'] holds only extra_terms and exclude_terms, as lists",
        f'{state.MANIFEST}: [[exclusion]] must be an array of tables',
        f'{state.MANIFEST}: [[probe]] must be an array of tables',
    ]


def test_a_page_listed_under_both_marks_is_a_problem():
    text = MANIFEST_TOML.replace("terms = ['env-vars']", "terms = ['env-vars', 'tools']")
    with pytest.raises(state.SetupError) as err:
        state.parse_manifest(text)
    assert str(err.value) == f'{state.MANIFEST}: [groups.alpha] tools is listed twice'


def test_invalid_toml_is_a_setup_error():
    with pytest.raises(tomllib.TOMLDecodeError) as cause:
        tomllib.loads('[guide\n')
    with pytest.raises(state.SetupError) as err:
        state.parse_manifest('[guide\n')
    assert str(err.value) == f'{state.MANIFEST}: not valid TOML ({cause.value})'


def test_section_terms_and_the_probe_registry_parse():
    text = MANIFEST_TOML + '\n'.join([
        "[sections.'alpha.overview']", "extra_terms = ['alpha-mode']", "exclude_terms = ['ALPHA_TOOL']",
        '', '[[probe]]', "id = 'agent-tools'", "sections = ['beta.reference']", "files = ['agents/a.md']", ''])
    m = state.parse_manifest(text)
    assert m.terms == {'alpha.overview': (['alpha-mode'], ['ALPHA_TOOL'])}
    assert m.probes == {'agent-tools': (['beta.reference'], ['agents/a.md'])}


def test_a_valid_baseline_parses_and_a_broken_one_is_a_setup_error():
    assert state.parse_baseline(baseline_text())['llms'] == ['tools']
    broken = {'sections': {'alpha.overview': {**SECTION, 'changed': '2.1.x'}}}
    with pytest.raises(state.SetupError) as err:
        state.parse_baseline(baseline_text(**broken))
    assert str(err.value) == (f'{state.BASELINE}: section alpha.overview: needs checked, changed,'
                              ' audited and text_hash')
    # A bad block hash, then a readable key: docs text R2.3 keeps out of the repo.
    for entries in ({'1' * 16: 'xyz'}, {'Tools': '0' * 16}):
        with pytest.raises(state.SetupError) as err:
            state.parse_baseline(baseline_text(groups={'alpha': {'blocks': {'tools': entries}, 'snapshot': {}}}))
        assert str(err.value) == (f'{state.BASELINE}: group alpha: needs blocks (page -> key hash -> block hash)'
                                  ' and snapshot (page -> release)')
    with pytest.raises(json.JSONDecodeError) as cause:
        json.loads('{')
    with pytest.raises(state.SetupError) as err:
        state.parse_baseline('{')
    assert str(err.value) == f'{state.BASELINE}: not valid JSON ({cause.value})'


def test_dump_baseline_keeps_insertion_order_and_utf8():
    raw = {'sections': {}, 'groups': {'g': {'blocks': {'p': {'T › b': '1' * 16, 'T › a': '2' * 16}},
                                            'snapshot': {}}}, 'llms': []}
    text = state.dump_baseline(raw)
    assert text.index('T › b') < text.index('T › a')
    assert text.endswith('}\n')


def test_probe_rows_are_read_by_header_and_an_absent_file_has_none():
    assert state.parse_probes(None) == []
    text = '\n'.join(['# Probe log', '',
                      '| Date | Version | Binary | Probe | Outcome | Finding | Flags |',
                      '|---|---|---|---|---|---|---|',
                      '| 2026-10-10 | 2.1.290 | ~/.local/bin/claude | agent-tools | pass | ok | |',
                      '| 2026-10-11 | 2.1.290 | ~/.local/bin/claude | agent-tools | DIVERGES | no Grep | |', ''])
    assert state.parse_probes(text) == [
        state.ProbeRow(date(2026, 10, 10), '2.1.290', 'agent-tools', 'PASS'),
        state.ProbeRow(date(2026, 10, 11), '2.1.290', 'agent-tools', 'DIVERGES')]


def test_an_unreadable_probe_row_is_a_setup_error():
    text = '| Date | Version | Probe | Outcome |\n|---|---|---|---|\n| soon | 2.1.290 | x | PASS |\n'
    with pytest.raises(state.SetupError) as err:
        state.parse_probes(text)
    assert str(err.value) == f"{state.PROBES}: unreadable row '| soon | 2.1.290 | x | PASS |'"


def test_a_source_reads_the_working_tree_or_a_commit(tmp_path):
    repo = fixture_repo(tmp_path / 'repo', {'a.txt': 'committed\n'})
    (repo / 'a.txt').write_text('edited\n')
    assert state.Source(repo).read('a.txt') == 'edited\n'
    assert state.Source(repo, 'main').read('a.txt') == 'committed\n'
    assert state.Source(repo, 'main').read('absent.txt') is None
    with pytest.raises(state.SetupError) as err:
        state.Source(repo, 'main').require('absent.txt')
    assert str(err.value) == 'absent.txt: not found in main'
    with pytest.raises(state.SetupError) as err:
        state.Source(repo, 'no-such-ref')
    assert str(err.value) == f'no-such-ref: not a commit in {repo}'


def test_group_terms_join_the_manifest_and_the_guide():
    m = state.parse_manifest(MANIFEST_TOML + "[sections.'alpha.overview']\nextra_terms = ['alpha-mode']\n")
    assert state.group_terms(m, guide_text()) == {
        'alpha': {'alpha.overview': {'ALPHA_TOOL', 'alpha-mode'},
                  'alpha.reference': {'ALPHA_ENV', 'a `tick` inside'}},
        'beta': {'beta.overview': {'BETA_ENV'}, 'beta.reference': {'BetaEvent'}},
    }


def test_the_newest_changelog_is_latest_else_the_bootstrap_snapshot(tmp_path):
    assert state.newest_changelog(tmp_path) is None
    boot = state.snapshot_docs(tmp_path, '2.1.288') / 'changelog.md'
    boot.parent.mkdir(parents=True)
    boot.write_text('x')
    assert state.newest_changelog(tmp_path) == boot
    latest = state.latest_docs(tmp_path) / 'changelog.md'
    latest.parent.mkdir(parents=True)
    latest.write_text('y')
    assert state.newest_changelog(tmp_path) == latest


def test_the_default_cache_follows_home(isolated_home):
    assert state.default_cache() == isolated_home / '.cache' / 'agent-skills' / 'cc-guide'
