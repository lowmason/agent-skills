'''Tests for cli.py: exit codes, which inputs each subcommand reads, each
`baseline` subcommand's write set, and the manual bookkeeping that brings
check to exit 0 (drift spec R5, R6.1, R7; Validation 1).'''
import json
from datetime import date, datetime

import pytest

import baseline
import cli
import state
from cc_fixtures import (DOCS, GUIDE_IDS, GUIDE_PATH, MANIFEST_TOML, docs_dir, drift_repo,  # noqa: F401
                         fixture_repo, git, guide_text, isolated_home, prime_cache, write_tree)


@pytest.fixture
def world(tmp_path, docs_dir, monkeypatch):
    '''A committed fixture repo, a primed cache, and cli pointed at both.'''
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    cache = tmp_path / 'cache'
    prime_cache(cache, docs_dir)
    monkeypatch.setattr(cli, 'REPO', repo)
    return repo, cache, docs_dir


def main(cache, *argv, today=date(2026, 9, 10)):
    return cli.main(['--cache', str(cache), *argv], today=today)


def load(repo):
    return json.loads((repo / state.BASELINE).read_text())


def dirty(repo):
    return sorted(line[3:] for line in git(repo, 'status', '--porcelain').splitlines())


def test_lint_exits_zero_clean_one_on_a_violation_and_two_on_a_setup_error(world, capsys):
    repo, cache, _ = world
    assert main(cache, 'lint') == 0
    guide = repo / GUIDE_PATH
    guide.write_text(guide.read_text().replace('Alpha uses', 'Alpha now uses'))
    assert main(cache, 'lint') == 1
    assert capsys.readouterr() == (
        'section alpha.overview: text differs from its text_hash; record it with'
        ' `uv run --python 3.13 python build/cc_guide/cli.py baseline accept alpha.overview --substantive`'
        ' (flags its citers) or `... --editorial`\n', '')
    assert main(cache, 'lint', '--ref', 'main') == 0
    (repo / state.BASELINE).unlink()
    assert main(cache, 'lint') == 2
    assert capsys.readouterr() == ('', f'cc-guide: {state.BASELINE}: not found in the working tree\n')


def test_check_reads_main_unless_told_otherwise(tmp_path, docs_dir, monkeypatch, capsys):
    repo = fixture_repo(tmp_path / 'repo', {GUIDE_PATH: guide_text()})
    write_tree(repo, {state.MANIFEST: MANIFEST_TOML,
                      state.BASELINE: state.dump_baseline(baseline.init(
                          state.parse_manifest(MANIFEST_TOML), guide_text(), docs_dir, '2.1.900', '2026-09-02',
                          {i: '2.1.900' for i in GUIDE_IDS}))})
    monkeypatch.setattr(cli, 'REPO', repo)
    cache = tmp_path / 'cache'
    assert main(cache, 'check', '--docs', str(docs_dir)) == 2
    assert capsys.readouterr() == ('', f'cc-guide: {state.MANIFEST}: not found in main\n')
    assert main(cache, 'check', '--worktree', '--docs', str(docs_dir)) == 0


def test_init_derives_changed_and_refuses_to_overwrite_without_force(tmp_path, docs_dir, monkeypatch):
    old = '\n'.join(line for line in guide_text().split('\n') if not line.startswith('<!-- cc: '))
    repo = fixture_repo(tmp_path / 'repo', {baseline.OLD_GUIDE_PATH: old.replace('Set `ALPHA_ENV`', 'Set `OLD`')})
    july = git(repo, 'rev-parse', 'HEAD').strip()
    write_tree(repo, {baseline.OLD_GUIDE_PATH: old})
    git(repo, 'commit', '-qam', 'refresh')
    refresh = git(repo, 'rev-parse', 'HEAD').strip()
    write_tree(repo, {GUIDE_PATH: guide_text(), state.MANIFEST: MANIFEST_TOML})
    git(repo, 'add', '-A')
    git(repo, 'commit', '-qm', 'the anchored guide and its manifest')
    monkeypatch.setattr(cli, 'REPO', repo)
    monkeypatch.setattr(baseline, 'JULY', (july, '2.1.219'))
    monkeypatch.setattr(baseline, 'REFRESH', (refresh, '2.1.288'))
    cache = tmp_path / 'cache'
    argv = ('baseline', 'init', '--docs', str(docs_dir), '--release', '2.1.900', '--date', '2026-09-02')
    assert main(cache, *argv) == 0
    assert dirty(repo) == [state.BASELINE]
    written = load(repo)
    assert {i: s['changed'] for i, s in written['sections'].items()} == {
        'alpha.overview': '2.1.219', 'alpha.reference': '2.1.288',
        'beta.overview': '2.1.219', 'beta.reference': '2.1.219'}
    assert main(cache, *argv) == 2
    assert main(cache, *argv, '--force') == 0


def changed_fields(old, new):
    out = {f'sections.{i}.{k}' for i in old['sections'] for k in old['sections'][i]
           if old['sections'][i][k] != new['sections'][i][k]}
    out |= {f'groups.{g}' for g in old['groups'] if old['groups'][g] != new['groups'][g]}
    return out | ({'llms'} if old['llms'] != new['llms'] else set())


def test_advance_writes_only_the_named_sections_checked(world):
    repo, cache, _ = world
    before = load(repo)
    assert main(cache, 'baseline', 'advance', 'beta.overview', '--to', '2.1.902') == 0
    assert dirty(repo) == [state.BASELINE]
    assert changed_fields(before, load(repo)) == {'sections.beta.overview.checked'}


def test_audited_writes_only_the_groups_audited_and_checked(world, capsys):
    repo, cache, _ = world
    before = load(repo)
    assert main(cache, 'baseline', 'audited', 'alpha', today=date(2026, 10, 4)) == 0
    assert dirty(repo) == [state.BASELINE]
    assert changed_fields(before, load(repo)) == {
        'sections.alpha.overview.audited', 'sections.alpha.overview.checked',
        'sections.alpha.reference.audited', 'sections.alpha.reference.checked'}
    assert capsys.readouterr().err == ''  # beta's sections still hold the oldest dates
    assert main(cache, 'baseline', 'audited', 'beta', today=date(2026, 10, 4)) == 0
    assert capsys.readouterr().err == 'the stamp region is now stale: run baseline stamp\n'


def test_accept_writes_only_the_named_sections_hash_and_changed(world):
    repo, cache, _ = world
    guide = repo / GUIDE_PATH
    guide.write_text(guide.read_text().replace('Alpha uses', 'Alpha now uses'))
    git(repo, 'commit', '-qam', 'edit the guide')
    before = load(repo)
    assert main(cache, 'baseline', 'accept', 'alpha.overview', '--editorial') == 0
    assert changed_fields(before, load(repo)) == {'sections.alpha.overview.text_hash'}
    assert main(cache, 'baseline', 'accept', 'alpha.overview', '--substantive') == 0
    assert changed_fields(before, load(repo)) == {'sections.alpha.overview.text_hash',
                                                  'sections.alpha.overview.changed'}
    assert load(repo)['sections']['alpha.overview']['changed'] == '2.1.902'
    assert dirty(repo) == [state.BASELINE]


def test_rebaseline_writes_the_baseline_and_a_cache_snapshot_only(world):
    repo, cache, folder = world
    write_tree(state.latest_docs(cache), {'tools.md': DOCS['tools.md'].replace('alpha jobs', 'alpha batches')})
    before = load(repo)
    assert main(cache, 'baseline', 'rebaseline', 'alpha') == 0
    assert dirty(repo) == [state.BASELINE]
    assert changed_fields(before, load(repo)) == {'groups.alpha'}
    assert sorted(p.name for p in state.snapshot_docs(cache, '2.1.902').iterdir()) == ['env-vars.md', 'tools.md']


def test_stamp_writes_only_the_guides_stamp_region(world):
    repo, cache, _ = world
    main(cache, 'baseline', 'advance', *GUIDE_IDS, '--to', '2.1.902', today=date(2026, 10, 4))
    git(repo, 'commit', '-qam', 'advance')
    assert main(cache, 'baseline', 'stamp') == 0
    assert dirty(repo) == [GUIDE_PATH]
    diff = [l for l in git(repo, 'diff', '-U0').splitlines() if l[:1] in '+-' and l[:3] not in ('+++', '---')]
    assert diff == ['-> Checked against the Claude Code docs and changelog through 2.1.900 on 2026-09-02; '
                    'oldest full re-verification 2026-09-02, at 2.1.900.',
                    '+> Checked against the Claude Code docs and changelog through 2.1.902 on 2026-10-04; '
                    'oldest full re-verification 2026-09-02, at 2.1.900.']


def test_rebaseline_never_writes_the_bootstrap_snapshot(world, capsys):
    repo, cache, folder = world
    prime_cache(cache, folder, head='2.1.288')
    snapshot = state.snapshot_docs(cache, '2.1.288')
    assert main(cache, 'baseline', 'rebaseline', 'alpha') == 2
    assert capsys.readouterr() == ('', f'cc-guide: {snapshot} is the bootstrap snapshot, which is never'
                                       ' written (R2.6): run check to fetch a newer release first\n')
    assert not snapshot.exists()
    assert dirty(repo) == []


def test_a_malformed_or_empty_cached_changelog_exits_two(world, capsys):
    _, cache, _ = world
    changelog = state.latest_docs(cache) / 'changelog.md'
    changelog.write_text(changelog.read_text().replace('October 1, 2026', '2026-10-01'))
    assert main(cache, 'lint') == 2
    with pytest.raises(ValueError) as cause:
        datetime.strptime('2026-10-01', '%B %d, %Y')
    assert capsys.readouterr() == ('', f'cc-guide: {changelog}: changelog line 8: {cause.value}\n')
    changelog.write_text('# Changelog\n')
    assert main(cache, 'lint') == 2
    assert capsys.readouterr() == ('', f'cc-guide: {changelog}: no <Update> release blocks\n')


def test_a_crash_exits_two_never_one(world, monkeypatch, capsys):
    '''R6.9: an unexpected exception must not read as 1, "due".'''
    _, cache, _ = world

    def crash(*args):
        raise RuntimeError('boom')
    monkeypatch.setattr(cli, 'run_lint', crash)
    assert main(cache, 'lint') == 2
    out, err = capsys.readouterr()
    lines = err.splitlines()
    assert (out, lines[0], lines[-1]) == ('', 'Traceback (most recent call last):', 'RuntimeError: boom')


def test_bookkeeping_alone_brings_check_to_exit_zero(world):
    '''Validation 1: after a manual review, the Stage 1 subcommands clear
    every due item, in R8.8's order, with no Stage 3 skill.'''
    repo, cache, folder = world
    write_tree(folder, {'events.md': DOCS['events.md'].replace('fires on beta', 'fires on gamma')})
    prime_cache(cache, folder)
    today = date(2026, 10, 5)
    check_args = ('check', '--worktree', '--docs', str(folder))
    assert main(cache, *check_args, today=today) == 1
    assert main(cache, 'baseline', 'rebaseline', 'beta', today=today) == 0
    assert main(cache, 'baseline', 'advance', *GUIDE_IDS, '--to', '2.1.902', today=today) == 0
    assert main(cache, 'baseline', 'audited', 'alpha', today=today) == 0
    assert main(cache, 'baseline', 'stamp', today=today) == 0
    assert main(cache, 'lint', today=today) == 0
    assert main(cache, *check_args, today=today) == 0
    assert main(cache, 'check', '--docs', str(folder), today=today) == 1
