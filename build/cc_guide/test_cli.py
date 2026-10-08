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
from guide import STAMP_CLOSE, STAMP_OPEN


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
        ' (flags its citers) or'
        ' `uv run --python 3.13 python build/cc_guide/cli.py baseline accept alpha.overview --editorial`\n', '')
    assert main(cache, 'lint', '--ref', 'main') == 0
    (repo / state.BASELINE).unlink()
    assert main(cache, 'lint') == 2
    assert capsys.readouterr() == ('', f'cc-guide: {state.BASELINE}: not found in the working tree\n')


def test_help_shows_the_module_docstring_and_the_rebaseline_refusal(capsys):
    for argv in (['--help'], ['baseline', 'rebaseline', '--help']):
        with pytest.raises(SystemExit) as stop:
            cli.main(argv)
        assert stop.value.code == 0
        out = ' '.join(capsys.readouterr().out.split())
        assert 'unlisted baselined block' in out
        assert 'the whole page' in out
    with pytest.raises(SystemExit):
        cli.main(['--help'])
    out = capsys.readouterr().out
    assert '  lint [--ref REF]\n' in out  # the docstring's line breaks survive
    assert 'Offline gate over the guide, manifest.toml and baseline.json (R5)' in out


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


@pytest.mark.parametrize('flag, value, message', [
    ('--release', '2.1.x', "--release '2.1.x' is not a release label"),
    ('--date', '20260902', "--date '20260902' is not a YYYY-MM-DD date"),
    ('--date', '2026-W36-3', "--date '2026-W36-3' is not a YYYY-MM-DD date"),
])
def test_init_refuses_a_bad_release_or_date_up_front(world, capsys, flag, value, message):
    repo, cache, folder = world
    (repo / state.BASELINE).unlink()  # so the --force guard is not what refuses
    assert main(cache, 'baseline', 'init', '--docs', str(folder), flag, value) == 2
    assert capsys.readouterr() == ('', f'cc-guide: baseline init: {message}\n')
    assert not (repo / state.BASELINE).exists()


def test_init_without_docs_takes_only_the_bootstrap_release(world, capsys):
    repo, cache, _ = world
    (repo / state.BASELINE).unlink()
    assert main(cache, 'baseline', 'init', '--release', '2.1.902') == 2
    assert capsys.readouterr() == ('', 'cc-guide: baseline init: without --docs it reads the 2.1.288 bootstrap'
                                       ' snapshot, so --release must be 2.1.288\n')


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


def test_an_editorial_accept_needs_no_cached_changelog_but_a_substantive_one_does(world, tmp_path, capsys):
    repo, _, _ = world
    guide = repo / GUIDE_PATH
    guide.write_text(guide.read_text().replace('Alpha uses', 'Alpha now uses'))
    git(repo, 'commit', '-qam', 'edit the guide')
    empty = tmp_path / 'empty-cache'
    assert main(empty, 'baseline', 'accept', 'alpha.overview', '--substantive') == 2
    assert capsys.readouterr() == ('', 'cc-guide: no cached changelog: run check, or restore the 2.1.288 snapshot\n')
    assert dirty(repo) == []
    assert main(empty, 'baseline', 'accept', 'alpha.overview', '--editorial') == 0
    assert dirty(repo) == [state.BASELINE]
    assert main(empty, 'lint') == 0


def test_rebaseline_writes_the_baseline_and_a_cache_snapshot_only(world):
    repo, cache, folder = world
    write_tree(state.latest_docs(cache), {'tools.md': DOCS['tools.md'].replace('alpha jobs', 'alpha batches')})
    before = load(repo)
    assert main(cache, 'baseline', 'rebaseline', 'alpha') == 0
    assert dirty(repo) == [state.BASELINE]
    assert changed_fields(before, load(repo)) == {'groups.alpha'}
    snapshot = state.snapshot_docs(cache, '2.1.902')
    assert sorted(p.name for p in snapshot.iterdir()) == ['env-vars.md', 'tools.md']
    assert (snapshot / 'tools.md').read_bytes() == (state.latest_docs(cache) / 'tools.md').read_bytes()


def test_rebaseline_refuses_to_overwrite_a_snapshot_page_holding_other_text(world, capsys):
    repo, cache, _ = world
    latest = state.latest_docs(cache)
    write_tree(latest, {'tools.md': DOCS['tools.md'].replace('alpha jobs', 'alpha batches')})
    held = state.snapshot_docs(cache, '2.1.902') / 'tools.md'
    write_tree(state.snapshot_docs(cache, '2.1.902'), {'tools.md': DOCS['tools.md']})
    before = (repo / state.BASELINE).read_bytes()
    assert main(cache, 'baseline', 'rebaseline', 'alpha') == 2
    assert capsys.readouterr() == ('', f'cc-guide: tools: {held} already holds different text, which another'
                                       ' group may have baselined; it is never overwritten\n')
    assert held.read_text() == DOCS['tools.md']
    assert not (held.parent / 'env-vars.md').exists()  # nothing of the run was written
    assert (repo / state.BASELINE).read_bytes() == before
    write_tree(state.snapshot_docs(cache, '2.1.902'), {'tools.md': (latest / 'tools.md').read_text()})
    assert main(cache, 'baseline', 'rebaseline', 'alpha') == 0  # identical bytes are not a conflict
    assert (held.parent / 'env-vars.md').is_file()


def test_rebaseline_names_a_gone_block_from_the_cached_snapshot(world, capsys):
    repo, cache, _ = world
    write_tree(state.snapshot_docs(cache, '2.1.900'), {'tools.md': DOCS['tools.md']})
    write_tree(state.latest_docs(cache), {'tools.md': DOCS['tools.md'].replace('## Options', '## Flags')})
    assert main(cache, 'baseline', 'rebaseline', 'alpha', 'tools › Tools › Options › `--fast`') == 2
    assert capsys.readouterr() == ('', 'cc-guide: tools: also changed since the baseline: tools › Tools › Options;'
                                       ' list them too, or rebaseline the whole page\n')
    assert dirty(repo) == []


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


def test_stamp_without_a_stamp_region_is_one_error_line(world, capsys):
    repo, cache, _ = world
    guide = repo / GUIDE_PATH
    guide.write_text(guide.read_text().replace(STAMP_OPEN + '\n', '').replace(STAMP_CLOSE + '\n', ''))
    assert main(cache, 'baseline', 'stamp') == 2
    assert capsys.readouterr() == ('', f'cc-guide: guide: needs one stamp region, a {STAMP_OPEN} line'
                                       f' then a {STAMP_CLOSE} line\n')


def test_an_emptied_baseline_is_one_error_line(world, capsys):
    repo, cache, _ = world
    emptied = load(repo)
    emptied['sections'] = {}
    (repo / state.BASELINE).write_text(json.dumps(emptied))
    assert main(cache, 'lint') == 2
    assert capsys.readouterr() == ('', f'cc-guide: {state.BASELINE}: sections must hold at least one section\n')


def test_accepting_a_section_the_guide_no_longer_has_is_one_error_line(world, capsys):
    repo, cache, _ = world
    guide = repo / GUIDE_PATH
    guide.write_text(guide.read_text().replace('<!-- cc: alpha.overview -->', '<!-- cc: alpha.renamed -->'))
    assert main(cache, 'baseline', 'accept', 'alpha.overview', '--editorial') == 2
    assert capsys.readouterr() == ('', 'cc-guide: section IDs not in the guide: alpha.overview\n')
    assert dirty(repo) == [GUIDE_PATH]


def test_a_corrupt_fetch_record_is_one_error_line(world, capsys):
    _, cache, _ = world
    record = state.fetch_record(cache)
    record.write_text('{')
    with pytest.raises(json.JSONDecodeError) as cause:
        json.loads('{')
    assert main(cache, 'baseline', 'rebaseline', 'alpha') == 2
    assert capsys.readouterr() == ('', f'cc-guide: {record}: not valid JSON ({cause.value}); delete it and run check\n')
    record.write_text('{}')
    assert main(cache, 'baseline', 'rebaseline', 'alpha') == 2
    assert capsys.readouterr() == ('', f'cc-guide: {record}: names no changelog_head release;'
                                       ' delete it and run check\n')


def test_non_utf8_cached_docs_are_one_error_line(world, capsys):
    repo, cache, _ = world
    page = state.latest_docs(cache) / 'tools.md'
    page.write_bytes(b'\xff\xfe')
    assert main(cache, 'baseline', 'rebaseline', 'alpha') == 2
    assert capsys.readouterr() == ('', f'cc-guide: {page}: not UTF-8 text (invalid start byte at byte 0)\n')
    changelog = state.latest_docs(cache) / 'changelog.md'
    changelog.write_bytes(b'\xff\xfe')
    assert main(cache, 'lint') == 2
    assert capsys.readouterr() == ('', f'cc-guide: {changelog}: not UTF-8 text (invalid start byte at byte 0)\n')
    assert dirty(repo) == []


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
    monkeypatch.setattr(cli, 'default_cache', crash)
    assert cli.main(['lint']) == 2
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


def test_the_repo_lints_clean(capsys):
    '''R5: the suite enforces the lint on the repo itself. HOME is isolated,
    so no changelog is cached and the release-label check is skipped.'''
    assert cli.main(['lint']) == 0, capsys.readouterr().out
