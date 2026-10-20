'''Tests for cli.py: exit codes, which inputs each subcommand reads, each
`baseline` subcommand's write set, and the manual bookkeeping that brings
check to exit 0 (drift spec R5, R6.1, R7; Validation 1).'''
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

import baseline
import cli
import notice
import state
from cc_fixtures import (DOCS, GUIDE_IDS, GUIDE_PATH, MANIFEST_TOML, MARKDOWN_PAGE, MDX_PAGE, docs_dir,  # noqa: F401
                         drift_repo, fixture_repo, git, guide_text, isolated_home, prime_cache, write_tree)
from guide import HASH_FORM, STAMP_CLOSE, STAMP_OPEN


@pytest.fixture
def world(tmp_path, docs_dir, monkeypatch):
    '''A committed fixture repo, a primed cache, and cli pointed at both.'''
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    cache = tmp_path / 'cache'
    prime_cache(cache, docs_dir)
    monkeypatch.setattr(cli, 'REPO', repo)
    return repo, cache, docs_dir


def main(cache, *argv, today=date(2026, 9, 5)):
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


@pytest.mark.usefixtures('world')  # the committed repo, with cli pointed at it
def test_a_label_newer_than_the_cached_changelog_is_a_note_not_a_violation(tmp_path, capsys):
    '''With only the bootstrap snapshot cached, a changelog that ends before the
    guide's labels, lint called each of them "not a changelog release label" and
    exited 1, so every local commit was refused. Such a label cannot be judged:
    it is a note on stderr and the exit stays 0 (owner, plan 43 final review,
    2026-10-12).'''
    snapshot_only = tmp_path / 'snapshot-only-cache'
    write_tree(state.snapshot_docs(snapshot_only, '2.1.288'), {
        'changelog.md': '<Update label="2.1.899" description="August 1, 2026">\n  * A bullet\n</Update>\n'})
    assert main(snapshot_only, 'lint') == 0
    note = "note: guide line {}: 2.1.900 is newer than the changelog's newest release 2.1.899; not checked\n"
    assert capsys.readouterr() == ('', note.format(6) * 2 + note.format(9))  # line 6 names 2.1.900 twice


def test_an_unlisted_label_below_the_cached_changelogs_newest_release_is_still_a_violation(world, capsys):
    repo, cache, _ = world
    guide = repo / GUIDE_PATH
    guide.write_text(guide.read_text().replace('First verified at 2.1.900.', 'First verified at 2.1.899.'))
    assert main(cache, 'lint') == 1
    assert capsys.readouterr() == ('guide line 9: 2.1.899 is not a changelog release label\n', '')


def test_help_shows_the_module_docstring_and_the_rebaseline_refusal(capsys):
    outs = []
    for argv in (['--help'], ['baseline', 'rebaseline', '--help']):
        with pytest.raises(SystemExit) as stop:
            cli.main(argv)
        assert stop.value.code == 0
        outs.append(capsys.readouterr().out)
    for out in (' '.join(o.split()) for o in outs):
        assert 'unlisted baselined block' in out
        assert 'also changed or gone' in out
        assert 'the whole page' in out
        assert 'it refuses when the latest fetch is at another release' in out
    assert '  lint [--ref REF]\n' in outs[0]  # the docstring's line breaks survive
    assert 'Offline gate over the guide, manifest.toml, baseline.json and every' in outs[0]
    assert '  baseline cite FILE [FILE ...]\n' in outs[0]
    assert '  baseline rehash\n' in outs[0]
    assert ('A three-part guide release label newer than the cached changelog'
            in ' '.join(outs[0].split()))  # the label note is for a release only


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


HOOK_NOW = datetime(2026, 9, 27, 9, 0, tzinfo=timezone.utc)


def hook(cache, *argv, today=date(2026, 9, 27)):
    '''check --hook as notice.sh refresh runs it, at HOOK_NOW.'''
    return cli.main(['--cache', str(cache), 'check', '--hook', *argv], today=today, now=HOOK_NOW)


def shown(cache):
    return json.loads((cache / notice.NOTICE).read_text())['systemMessage']


def test_check_hook_prints_nothing_and_leaves_the_notice_then_the_record(world, capsys):
    repo, cache, docs = world
    assert hook(cache, '--run', 'r1', '--docs', str(docs)) == 1
    assert capsys.readouterr() == ('', '')
    assert shown(cache) == 'cc-guide · 2 releases untriaged (last triage 25 d ago) → /cc-guide'
    record = notice.read_last_check(cache)
    assert (record['run'], record['exit'], record['ok_epoch']) == ('r1', 1, int(HOOK_NOW.timestamp()))
    assert hook(cache, '--run', 'r2', '--docs', str(docs), today=date(2026, 9, 5)) == 0
    assert capsys.readouterr() == ('', '')
    assert (cache / notice.NOTICE).read_text() == ''
    assert git(repo, 'status', '--porcelain') == ''


def test_check_hook_turns_a_setup_error_into_the_error_line(tmp_path, docs_dir, monkeypatch, capsys):
    '''A setup error raised before check() returns still leaves the notice
    and the record, so the hook never shows a stale report's outcome
    (deferred item "check's report and inputs", part a).'''
    repo = fixture_repo(tmp_path / 'repo', {GUIDE_PATH: guide_text()})
    monkeypatch.setattr(cli, 'REPO', repo)
    cache = tmp_path / 'cache'
    earlier = HOOK_NOW - timedelta(days=3)
    notice.record_check(cache, 0, earlier, 'r0')
    assert hook(cache, '--run', 'r1', '--docs', str(docs_dir)) == 2
    assert capsys.readouterr() == ('', '')
    assert shown(cache) == (f'cc-guide · check failed: {state.MANIFEST}: not found in main · '
                            'last good check 3 d ago → run build/cc_guide/cli.py check')
    record = notice.read_last_check(cache)
    assert (record['run'], record['exit'], record['ok_epoch']) == ('r1', 2, int(earlier.timestamp()))


def test_check_hook_turns_a_crash_into_the_error_line(world, monkeypatch, capsys):
    _, cache, docs = world

    def boom(*args, **kwargs):
        raise RuntimeError('boom')
    monkeypatch.setattr(cli, 'check', boom)
    assert hook(cache, '--run', 'r1', '--docs', str(docs)) == 2
    assert capsys.readouterr() == ('', '')
    assert shown(cache) == ('cc-guide · check failed: RuntimeError: boom · no good check yet'
                            ' → run build/cc_guide/cli.py check')
    assert notice.read_last_check(cache)['run'] == 'r1'


def test_run_goes_with_hook(world, capsys):
    _, cache, docs = world
    assert main(cache, 'check', '--run', 'r1', '--docs', str(docs)) == 2
    assert capsys.readouterr() == ('', 'cc-guide: --run goes with --hook\n')


def test_check_hook_writes_only_its_cache_files(world):
    '''R6.10: the report, the notice, its digest and the record, all in the
    cache, and nothing in the repo.'''
    repo, cache, docs = world

    def files():
        return {p.relative_to(cache).as_posix() for p in cache.rglob('*') if p.is_file()}
    before = files()
    hook(cache, '--run', 'r1', '--docs', str(docs))
    added = files() - before
    reports = {name for name in added if name.startswith('reports/')}
    assert len(reports) == 1
    assert sorted(added - reports) == [notice.LAST_CHECK, notice.DIGEST, notice.NOTICE]
    assert git(repo, 'status', '--porcelain') == ''


@pytest.mark.parametrize('failure, code', [
    pytest.param(None, 1, id='normal-exit'),
    pytest.param(state.SetupError('no manifest'), 2, id='setup-error'),
    pytest.param(RuntimeError('boom'), 2, id='crash'),
])
def test_check_hook_renames_the_record_into_place_after_the_notice_and_its_digest(world, monkeypatch, failure, code):
    '''The handshake: last-check.json is written last of all, on every exit.'''
    _, cache, docs = world
    if failure is not None:
        def fail(*args, **kwargs):
            raise failure
        monkeypatch.setattr(cli, 'check', fail)
    order = []
    real = notice.os.replace  # the global os module: other renames land here too

    def replace(src, dst):
        order.append(Path(dst).name)
        real(src, dst)
    monkeypatch.setattr(notice.os, 'replace', replace)
    assert hook(cache, '--run', 'r1', '--docs', str(docs)) == code
    written = (notice.NOTICE, notice.DIGEST, notice.LAST_CHECK)
    assert [name for name in order if name in written] == list(written)


def history_repo(tmp_path, monkeypatch):
    '''A repo holding R11.1's two old guides, then the anchored guide and its
    manifest but no baseline, with cli and baseline pointed at it.'''
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
    return repo


def test_init_derives_changed_and_refuses_to_overwrite_without_force(tmp_path, docs_dir, monkeypatch, capsys):
    repo = history_repo(tmp_path, monkeypatch)
    cache = tmp_path / 'cache'
    argv = ('baseline', 'init', '--docs', str(docs_dir), '--release', '2.1.900', '--date', '2026-09-02')
    assert main(cache, *argv) == 0
    assert capsys.readouterr() == (f'wrote {state.BASELINE} from {docs_dir}; next: baseline stamp\n', '')
    assert dirty(repo) == [state.BASELINE]
    written = load(repo)
    assert {i: s['changed'] for i, s in written['sections'].items()} == {
        'alpha.overview': '2.1.219', 'alpha.reference': '2.1.288',
        'beta.overview': '2.1.219', 'beta.reference': '2.1.219'}
    assert main(cache, *argv) == 2
    assert capsys.readouterr() == ('', f'cc-guide: {state.BASELINE} exists; init rebuilds it from scratch'
                                       ' only with --force\n')
    assert main(cache, *argv, '--force') == 0


def test_init_without_docs_needs_the_bootstrap_snapshot_directory(tmp_path, monkeypatch, capsys):
    repo = history_repo(tmp_path, monkeypatch)
    cache = tmp_path / 'cache'
    assert main(cache, 'baseline', 'init') == 2
    assert capsys.readouterr() == ('', f"cc-guide: {state.snapshot_docs(cache, '2.1.288')}: no snapshot directory\n")
    assert dirty(repo) == []


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


def test_advance_writes_only_the_named_sections_checked_and_says_when_the_stamp_is_stale(world, capsys):
    repo, cache, _ = world
    before = load(repo)
    assert main(cache, 'baseline', 'advance', 'beta.overview', '--to', '2.1.902') == 0
    assert dirty(repo) == [state.BASELINE]
    assert changed_fields(before, load(repo)) == {'sections.beta.overview.checked'}
    assert capsys.readouterr() == (f'updated {state.BASELINE}\n', '')  # the oldest checked is unchanged
    assert main(cache, 'baseline', 'advance', *GUIDE_IDS, '--to', '2.1.902') == 0
    assert capsys.readouterr() == (f'updated {state.BASELINE}\n',
                                   'the stamp region is now stale: run baseline stamp\n')


def test_audited_writes_only_the_groups_audited_and_checked(world, capsys):
    repo, cache, _ = world
    before = load(repo)
    assert main(cache, 'baseline', 'audited', 'alpha', today=date(2026, 10, 4)) == 0
    assert dirty(repo) == [state.BASELINE]
    assert changed_fields(before, load(repo)) == {
        'sections.alpha.overview.audited', 'sections.alpha.overview.checked',
        'sections.alpha.reference.audited', 'sections.alpha.reference.checked'}
    assert capsys.readouterr() == (f'updated {state.BASELINE}\n', '')  # beta's sections still hold the oldest dates
    assert main(cache, 'baseline', 'audited', 'beta', today=date(2026, 10, 4)) == 0
    assert capsys.readouterr() == (f'updated {state.BASELINE}\n',
                                   'the stamp region is now stale: run baseline stamp\n')


def test_audited_to_records_the_named_release_and_refuses_one_the_changelog_lacks(world, capsys):
    '''m7 (final review): settle names the audit packet's head with --to, so
    a fetch after the packet was built never moves the audit past what the
    verifier saw.'''
    repo, cache, _ = world
    assert main(cache, 'baseline', 'audited', 'alpha', '--to', '2.1.901', today=date(2026, 10, 4)) == 0
    written = load(repo)['sections']
    assert [written[sid][k] for sid in ('alpha.overview', 'alpha.reference') for k in ('audited', 'checked')] == [
        {'release': '2.1.901', 'date': '2026-10-04'}] * 4
    capsys.readouterr()
    before = (repo / state.BASELINE).read_bytes()
    assert main(cache, 'baseline', 'audited', 'beta', '--to', '2.1.950') == 2
    assert capsys.readouterr() == ('', 'cc-guide: 2.1.950 is not a release in the newest cached changelog\n')
    assert (repo / state.BASELINE).read_bytes() == before


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


def test_rebaseline_overwrites_an_mdx_snapshot_page_with_the_same_blocks(world):
    '''The 2.1.304 case (owner, 2026-10-20): the snapshot holds a page's MDX
    export and latest/ its Markdown export at the same release.'''
    repo, cache, _ = world
    write_tree(state.latest_docs(cache), {'tools.md': MARKDOWN_PAGE})
    held = state.snapshot_docs(cache, '2.1.902') / 'tools.md'
    write_tree(held.parent, {'tools.md': MDX_PAGE})
    assert main(cache, 'baseline', 'rebaseline', 'alpha', 'tools') == 0
    assert held.read_text() == MARKDOWN_PAGE
    assert dirty(repo) == [state.BASELINE]


def test_rebaseline_names_a_gone_block_from_the_cached_snapshot(world, capsys):
    repo, cache, _ = world
    write_tree(state.snapshot_docs(cache, '2.1.900'), {'tools.md': DOCS['tools.md']})
    write_tree(state.latest_docs(cache), {'tools.md': DOCS['tools.md'].replace('## Options', '## Flags')})
    assert main(cache, 'baseline', 'rebaseline', 'alpha', 'tools › Tools › Options › `--fast`') == 2
    assert capsys.readouterr() == ('', 'cc-guide: tools: also changed or gone since the baseline:'
                                       ' tools › Tools › Options; list them too, or rebaseline the whole page\n')
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


def test_rehash_reads_the_cached_snapshots_and_writes_only_the_baseline(world, capsys):
    repo, cache, folder = world
    assert main(cache, 'baseline', 'rehash') == 2
    assert capsys.readouterr() == ('', 'cc-guide: tools in alpha: no 2.1.900 snapshot to re-derive its blocks'
                                       ' from\n')
    snapshot = state.snapshot_docs(cache, '2.1.900')
    write_tree(snapshot, {**DOCS, 'tools.md': MDX_PAGE})
    assert main(cache, 'baseline', 'rehash') == 2
    assert capsys.readouterr().err == ('cc-guide: tools in alpha (2.1.900 snapshot): 3 baselined block(s) match'
                                       ' neither parse of the snapshot; rebaseline the page instead\n')
    write_tree(snapshot, DOCS)
    assert main(cache, 'baseline', 'rehash') == 0
    assert capsys.readouterr() == (f'updated {state.BASELINE}\n', '')
    assert dirty(repo) == []
    assert sorted(p.name for p in snapshot.iterdir()) == sorted(DOCS)


def test_rebaseline_without_a_fetch_is_one_error_line(world, tmp_path, capsys):
    repo, _, _ = world
    assert main(tmp_path / 'empty-cache', 'baseline', 'rebaseline', 'alpha') == 2
    assert capsys.readouterr() == ('', 'cc-guide: no latest fetch: run check first\n')
    assert dirty(repo) == []


def test_rebaseline_never_writes_the_bootstrap_snapshot(world, capsys):
    repo, cache, folder = world
    prime_cache(cache, folder, head='2.1.288')
    snapshot = state.snapshot_docs(cache, '2.1.288')
    assert main(cache, 'baseline', 'rebaseline', 'alpha') == 2
    assert capsys.readouterr() == ('', f'cc-guide: {snapshot} is the bootstrap snapshot, which is never'
                                       ' written (R2.6): run check to fetch a newer release first\n')
    assert not snapshot.exists()
    assert dirty(repo) == []


def test_rebaseline_head_refuses_a_latest_fetch_at_another_release(world, capsys):
    '''Plan 49's decision D2: a session start's refresh, or any other check,
    can refetch latest/ after a packet was built. settle passes the packet's
    head as --head, so rebaseline refuses to hash docs no review read: it
    names both releases and writes nothing. At the packet's own head it runs
    as before, with the flag after the refs, as settle prints it.'''
    repo, cache, _ = world
    write_tree(state.latest_docs(cache), {'tools.md': DOCS['tools.md'].replace('alpha jobs', 'alpha batches')})
    before = (repo / state.BASELINE).read_bytes()
    assert main(cache, 'baseline', 'rebaseline', 'alpha', 'tools › Tools', '--head', '2.1.901') == 2
    assert capsys.readouterr() == ('', 'cc-guide: rebaseline --head 2.1.901: the latest fetch is at 2.1.902, so'
                                       ' latest/ no longer holds the docs reviewed at 2.1.901; skip this rebaseline,'
                                       ' and the next check compares its blocks again\n')
    assert (repo / state.BASELINE).read_bytes() == before
    assert not state.snapshot_docs(cache, '2.1.901').exists()
    assert not state.snapshot_docs(cache, '2.1.902').exists()
    assert main(cache, 'baseline', 'rebaseline', 'alpha', 'tools › Tools', '--head', '2.1.902') == 0
    assert dirty(repo) == [state.BASELINE]
    assert (state.snapshot_docs(cache, '2.1.902') / 'tools.md').is_file()


def test_a_malformed_or_empty_cached_changelog_exits_two(world, capsys):
    _, cache, _ = world
    changelog = state.latest_docs(cache) / 'changelog.md'
    changelog.write_text(changelog.read_text().replace('label="2.1.902"', 'label="2.1.x"'))
    assert main(cache, 'lint') == 2
    assert capsys.readouterr() == ('', f"cc-guide: {changelog}: line 8: not a release label: '2.1.x'\n")
    changelog.write_text('# Changelog\n')
    assert main(cache, 'lint') == 2
    assert capsys.readouterr() == ('', f'cc-guide: {changelog}: no releases\n')


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


def test_packets_with_nothing_to_triage_exits_zero_and_writes_nothing(world, capsys):
    '''m5 (final review): every section checked through the head and no
    block finding is no packet, and exit 0.'''
    repo, cache, _ = world
    s = state.parse_baseline((repo / state.BASELINE).read_text())
    for section in s['sections'].values():
        section['checked'] = {'release': '2.1.902', 'date': '2026-10-04'}
    (repo / state.BASELINE).write_text(state.dump_baseline(s))
    assert main(cache, 'packets', '--triage') == 0
    assert capsys.readouterr() == ('nothing to triage: no untriaged release and no block finding\n', '')
    assert not (cache / 'packets').exists()


def test_the_repo_lints_clean(capsys):
    '''R5: the suite enforces the lint on the repo itself. HOME is isolated,
    so no changelog is cached and the release-label check is skipped.'''
    assert cli.main(['lint']) == 0, capsys.readouterr().out


def cited(repo, files):
    write_tree(repo, files)
    git(repo, 'add', '-A')
    git(repo, 'commit', '-qm', 'cite the guide')


def test_lint_prints_stale_on_stderr_and_lints_the_citations_at_its_ref(world, capsys):
    '''R5: STALE lines go to stderr and never change the exit; a misplaced
    citation is a violation; --ref reads the committed citations.'''
    repo, cache, _ = world
    cited(repo, {'hooks/gate.sh': '#!/bin/sh\n# cc-guide: alpha.overview alpha.reference @2.1.899\nexit 0\n'})
    assert main(cache, 'lint') == 0
    assert capsys.readouterr() == ('', 'STALE hooks/gate.sh alpha.overview\n')
    write_tree(repo, {'hooks/gate.sh': '#!/bin/sh\nexit 0\n# cc-guide: alpha.overview @2.1.899\n'})
    assert main(cache, 'lint') == 1
    assert capsys.readouterr().out == 'hooks/gate.sh:3: a citation goes on a line before the first line of code (R4.1)\n'
    assert main(cache, 'lint', '--ref', 'main') == 0


def test_cite_stamps_each_file_at_its_sections_highest_changed_and_writes_only_those_files(world, capsys):
    '''R7 cite: alpha.overview changed at 2.1.900 and alpha.reference at
    2.1.899, so a file citing both is stamped @2.1.900. Paths are read from
    the repo root, so a symlink is stamped at its target.'''
    repo, cache, _ = world
    cited(repo, {'hooks/gate.sh': '#!/bin/sh\n# cc-guide: alpha.overview alpha.reference @2.1.219\nexit 0\n',
                 'rules/style.md': '---\npaths: x\n# cc-guide: alpha.reference @2.1.219\n---\n'})
    (repo / '.claude').mkdir()
    (repo / '.claude' / 'style.md').symlink_to('../rules/style.md')
    git(repo, 'add', '-A')
    git(repo, 'commit', '-qm', 'link the rule')
    assert main(cache, 'baseline', 'cite', 'hooks/gate.sh', str(repo / '.claude' / 'style.md')) == 0
    assert capsys.readouterr().out == 'stamped hooks/gate.sh @2.1.900\nstamped rules/style.md @2.1.899\n'
    assert dirty(repo) == ['hooks/gate.sh', 'rules/style.md']
    assert (repo / 'hooks/gate.sh').read_text() == (
        '#!/bin/sh\n# cc-guide: alpha.overview alpha.reference @2.1.900\nexit 0\n')
    assert main(cache, 'lint') == 0
    assert capsys.readouterr() == ('', '')


def test_cite_refuses_a_file_the_lint_never_reads_and_stamps_a_symlink_and_its_target_once(world, capsys):
    '''A stamp on a file the lint's scan skips would never be checked
    (deferred: `baseline cite` stamps files `lint` never reads).'''
    repo, cache, _ = world
    cited(repo, {'rules/style.md': '---\npaths: x\n# cc-guide: alpha.reference @2.1.219\n---\n',
                 'specs/notes.md': '<!-- cc-guide: alpha.overview @2.1.219 -->\n'})
    (repo / '.claude').mkdir()
    (repo / '.claude' / 'style.md').symlink_to('../rules/style.md')
    write_tree(repo, {'hooks/new.sh': '#!/bin/sh\n# cc-guide: alpha.overview @2.1.219\n'})
    assert main(cache, 'baseline', 'cite', 'rules/style.md', '.claude/style.md') == 0
    assert capsys.readouterr().out == 'stamped rules/style.md @2.1.899\n'
    for name in ('hooks/new.sh', 'specs/notes.md'):
        assert main(cache, 'baseline', 'cite', 'rules/style.md', name) == 2
        assert capsys.readouterr() == ('', f'cc-guide: {name}: the lint never reads it (untracked, or under specs/,'
                                           ' runtimes/ or review/), so its stamp would never be checked\n')
    assert main(cache, 'baseline', 'cite', '../outside.sh') == 2
    assert capsys.readouterr() == ('', f'cc-guide: ../outside.sh: not a file in {repo}\n')


@pytest.mark.parametrize('files, args, message', [
    ({'hooks/gate.sh': '#!/bin/sh\nexit 0\n'}, ['hooks/gate.sh'], 'hooks/gate.sh: carries no citation'),
    ({'hooks/gate.sh': '#!/bin/sh\n# cc-guide: gamma.overview @2.1.219\n'}, ['hooks/gate.sh'],
     'hooks/gate.sh: unknown section IDs: gamma.overview'),
    ({'hooks/gate.sh': '#!/bin/sh\nexit 0\n# cc-guide: alpha.overview @2.1.219\n'}, ['hooks/gate.sh'],
     'hooks/gate.sh:3: a citation goes on a line before the first line of code (R4.1)'),
    ({}, ['hooks/none.sh'], 'hooks/none.sh: not found in the working tree'),
    ({}, ['/etc/hosts'], '/etc/hosts: not a file in {repo}'),
], ids=['uncited', 'unknown-id', 'misplaced', 'absent', 'outside'])
def test_cite_refuses_with_one_error_line_and_writes_nothing(world, capsys, files, args, message):
    repo, cache, _ = world
    good = {'hooks/ok.sh': '#!/bin/sh\n# cc-guide: alpha.overview @2.1.219\n'}
    cited(repo, {**good, **files})
    assert main(cache, 'baseline', 'cite', 'hooks/ok.sh', *args) == 2
    assert capsys.readouterr() == ('', f'cc-guide: {message.format(repo=repo)}\n')
    assert dirty(repo) == []


def test_a_substantive_accept_keeps_changed_above_every_citers_stamp(world):
    '''R2.4: a citer already stamped at the newest release forces a fourth
    component, so the new `changed` still flags it.'''
    repo, cache, _ = world
    cited(repo, {'hooks/gate.sh': '#!/bin/sh\n# cc-guide: alpha.overview @2.1.902\n'})
    guide = repo / GUIDE_PATH
    guide.write_text(guide.read_text().replace('Alpha uses', 'Alpha now uses'))
    assert main(cache, 'baseline', 'accept', 'alpha.overview', '--substantive') == 0
    assert load(repo)['sections']['alpha.overview']['changed'] == '2.1.902.1'


def test_a_substantive_accept_refuses_while_a_citation_is_broken(world, capsys):
    '''R2.4: a citation that does not parse yields no stamp for `changed` to
    exceed, so the accept refuses until the lint passes, and writes nothing.'''
    repo, cache, _ = world
    cited(repo, {'hooks/gate.sh': '#!/bin/sh\nexit 0\n# cc-guide: alpha.overview @2.1.902\n'})
    guide = repo / GUIDE_PATH
    guide.write_text(guide.read_text().replace('Alpha uses', 'Alpha now uses'))
    assert main(cache, 'baseline', 'accept', 'alpha.overview', '--substantive') == 2
    assert capsys.readouterr() == ('', (
        'cc-guide: a substantive accept needs every citation to parse (R2.4); fix these first:\n'
        'hooks/gate.sh:3: a citation goes on a line before the first line of code (R4.1)\n'))
    assert dirty(repo) == [GUIDE_PATH]


def test_a_two_part_stamp_is_a_lint_violation_so_no_accept_reaches_it(world, capsys):
    '''R2.4: a stamp of two parts parsed and linted clean, then crashed a
    substantive accept: next_changed, given 3.0 above every release, indexes a
    fourth part it lacks. The stamp is malformed now, so lint names it and the
    accept refuses with one error and writes nothing but the edit.'''
    repo, cache, _ = world
    cited(repo, {'hooks/gate.sh': '#!/bin/sh\n# cc-guide: alpha.overview @3.0\nexit 0\n'})
    malformed = f'hooks/gate.sh:2: malformed citation; the form is {HASH_FORM}\n'
    assert main(cache, 'lint') == 1
    assert capsys.readouterr() == (malformed, '')
    guide = repo / GUIDE_PATH
    guide.write_text(guide.read_text().replace('Alpha uses', 'Alpha now uses'))
    assert main(cache, 'baseline', 'accept', 'alpha.overview', '--substantive') == 2
    assert capsys.readouterr() == ('', 'cc-guide: a substantive accept needs every citation to parse (R2.4);'
                                       f' fix these first:\n{malformed}')
    assert dirty(repo) == [GUIDE_PATH]
