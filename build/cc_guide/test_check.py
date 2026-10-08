'''Tests for check.py: compare, the changelog, every due rule, the fetch gate,
the report and exit codes (drift spec R6, R12.3's row fixture).'''
import http.client
import json
import urllib.error
from datetime import date, datetime, timezone

import pytest

import blocks
import check
import docs
import state
from cc_fixtures import (DOCS, ENV_PAGE, MANIFEST_TOML, docs_dir, drift_repo,  # noqa: F401
                         fixture_snapshot, fixture_state, git, guide_text, isolated_home, write_tree)

MANIFEST = state.parse_manifest(MANIFEST_TOML)
TERMS = state.group_terms(MANIFEST, guide_text())
ENV = 'Environment variables'
NOW = datetime(2026, 10, 4, 12, 0, tzinfo=timezone.utc)
URLS = {docs.page_url(p, MANIFEST.sources): docs.page_file(p) for p in MANIFEST.pages()}
URLS.update({MANIFEST.sources['changelog']: 'changelog.md', MANIFEST.sources['llms']: 'llms.txt'})


def offline(folder):
    return check.offline_docs(MANIFEST, folder)


def findings(folder, s=None, terms=TERMS, snapshot=fixture_snapshot):
    found, deselected = check.compare(MANIFEST, s or fixture_state(folder), terms, offline(folder), snapshot)
    return [(f.group, f.kind, f.ref(), f.candidates) for f in found], deselected


def test_unchanged_docs_give_no_findings(docs_dir):
    assert findings(docs_dir) == ([], {'alpha': [], 'beta': []})


def test_changed_missing_and_new_blocks_name_their_candidate_sections(tmp_path, docs_dir):
    s = fixture_state(docs_dir)
    write_tree(docs_dir, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')
                          .replace('## Options', '## Flags'),
                          'events.md': DOCS['events.md'] + '## Retry\n\nRetries reuse `BetaEvent`.\n'})
    assert findings(docs_dir, s)[0] == [
        ('alpha', 'changed', 'tools › Tools', ['alpha.overview']),
        ('alpha', 'missing', 'tools › Tools › Options', ['alpha.overview', 'alpha.reference']),
        ('alpha', 'missing', 'tools › Tools › Options › `--fast`', ['alpha.overview', 'alpha.reference']),
        ('alpha', 'new', 'tools › Tools › Flags', ['alpha.overview', 'alpha.reference']),
        ('alpha', 'new', 'tools › Tools › Flags › `--fast`', ['alpha.overview', 'alpha.reference']),
        ('beta', 'new', 'events › Events › Retry', ['beta.reference']),
    ]


def test_a_missing_block_is_named_from_its_snapshot_else_by_its_key_hash(docs_dir):
    '''R2.3 commits block keys only as hashes, so a block gone from the page
    is named by reading its key back from the page's snapshot. Without one it
    goes by its key hash, which rebaseline takes as a ref too.'''
    s = fixture_state(docs_dir)
    write_tree(docs_dir, {'events.md': DOCS['events.md'].replace('## Payload', '## Body')})
    body = ('beta', 'new', 'events › Events › Body', ['beta.overview'])
    gone = ['beta.overview', 'beta.reference']
    assert findings(docs_dir, s)[0] == [('beta', 'missing', 'events › Events › Payload', gone), body]
    payload = blocks.key_hash('Events › Payload')
    unnamed = ('beta', 'missing', 'events › ' + payload, gone)
    assert findings(docs_dir, s, snapshot=state.no_snapshot)[0] == [unnamed, body]
    # A hash names no term, even when a term happens to be hex digits of it.
    hex_term = dict(TERMS, beta={**TERMS['beta'], 'beta.overview': TERMS['beta']['beta.overview'] | {payload[:6]}})
    assert findings(docs_dir, s, hex_term, state.no_snapshot)[0] == [unnamed, body]


def test_deselection_is_informational_only_while_the_block_is_unchanged(docs_dir):
    '''R3.7: a baselined block its group's terms no longer select is
    deselected only while its text is unchanged. A docs edit that drops a
    block's last watched term is a finding: changed when the term was in the
    block's text, missing when it was in its key.'''
    s = fixture_state(docs_dir)
    rates = 'platform:pricing › Rates'
    # The guide drops `BetaEvent`, the only beta term in Rates' text.
    unwatched = state.group_terms(MANIFEST, guide_text().replace('`BetaEvent` fires.', 'It fires.'))
    assert findings(docs_dir, s, unwatched) == ([], {'alpha': [], 'beta': [rates]})
    # The docs drop it instead, then both do.
    write_tree(docs_dir, {'platform_pricing.md': DOCS['platform_pricing.md']
                          .replace('with `BetaEvent`', 'with demand')})
    changed = ([('beta', 'changed', rates, ['beta.overview', 'beta.reference'])], {'alpha': [], 'beta': []})
    assert findings(docs_dir, s) == changed
    assert findings(docs_dir, s, unwatched) == changed
    # A row renamed off its term leaves its old key missing.
    write_tree(docs_dir, {'platform_pricing.md': DOCS['platform_pricing.md'],
                          'env-vars.md': ENV_PAGE.replace('see [events](/docs/en/events)', 'see events')
                          .replace('| `BETA_ENV` |', '| `GAMMA_ENV` |')})
    assert findings(docs_dir, s)[0] == [('beta', 'missing', f'env-vars › {ENV} › `BETA_ENV`', ['beta.overview'])]


def test_a_page_missing_from_llms_or_the_docs_is_one_finding(docs_dir):
    s = fixture_state(docs_dir)
    write_tree(docs_dir, {'llms.txt': DOCS['llms.txt'].replace('/tools.md', '/tools-moved.md')})
    (docs_dir / 'platform_pricing.md').unlink()
    assert findings(docs_dir, s)[0] == [
        ('alpha', 'missing-page', 'tools', ['alpha.overview', 'alpha.reference']),
        ('beta', 'missing-page', 'platform:pricing', ['beta.overview', 'beta.reference'])]


def test_editing_one_row_flags_only_the_groups_whose_terms_match_it(docs_dir):
    '''R12.3's row fixture: env-vars is a terms page of both groups.'''
    s = fixture_state(docs_dir)
    write_tree(docs_dir, {'env-vars.md': ENV_PAGE.replace('Turns on beta;', 'Turns on beta at once;')})
    assert findings(docs_dir, s)[0] == [
        ('beta', 'changed', f'env-vars › {ENV} › `BETA_ENV`', ['beta.overview'])]
    write_tree(docs_dir, {'env-vars.md': ENV_PAGE.replace('Turns on alpha.', 'Turns alpha off.')})
    assert findings(docs_dir, s)[0] == [
        ('alpha', 'changed', f'env-vars › {ENV} › `ALPHA_ENV`', ['alpha.reference'])]


def test_each_section_lists_the_releases_after_its_checked_oldest_first(docs_dir):
    s = fixture_state(docs_dir)
    s['sections']['beta.reference']['checked']['release'] = '2.1.901'
    releases = docs.parse_changelog(DOCS['changelog.md'])
    pending = check.untriaged(s, releases)
    assert pending['alpha.overview'] == ['2.1.901', '2.1.902']
    assert pending['beta.reference'] == ['2.1.902']
    notes = check.release_notes(releases, {'2.1.901', '2.1.902'}, TERMS)
    assert list(notes) == ['2.1.901', '2.1.902']
    assert notes['2.1.902']['bullets'] == [
        {'text': 'Changed how `BETA_ENV` is read', 'hints': ['beta.overview']},
        {'text': 'Fixed a crash in the fixture tool', 'hints': []}]


@pytest.mark.parametrize('today, due', [(date(2026, 9, 26), False), (date(2026, 9, 27), True)])
def test_the_changelog_batch_is_due_once_its_oldest_release_is_a_week_old(docs_dir, today, due):
    releases = docs.parse_changelog(DOCS['changelog.md'])
    assert check.due_changelog(fixture_state(docs_dir), releases, 7, today) == {
        'releases': 2, 'oldest': '2.1.901', 'oldest_date': '2026-09-20', 'due_from': '2026-09-27', 'due': due}


def test_nothing_untriaged_means_no_batch(docs_dir):
    s = fixture_state(docs_dir)
    for sec in s['sections'].values():
        sec['checked']['release'] = '2.1.902'
    assert check.due_changelog(s, docs.parse_changelog(DOCS['changelog.md']), 7, date(2026, 12, 1)) is None


def rows(*specs):
    return [state.ProbeRow(date.fromisoformat(d), v, 'p1', o) for d, v, o in specs]


@pytest.mark.parametrize('history, today, why', [
    ([], date(2026, 10, 4), 'never run'),
    ([('2026-10-01', '2.1.902', 'PASS')], date(2026, 10, 4), None),
    ([('2026-09-20', '2.1.901', 'PASS')], date(2026, 9, 26), None),
    ([('2026-09-20', '2.1.901', 'PASS')], date(2026, 9, 27), 'last run 2026-09-20 at 2.1.901'),
    ([('2026-09-20', '2.1.902', 'PASS')], date(2026, 12, 1), None),
    ([('2026-10-01', '2.1.902', 'DIVERGES')], date(2026, 10, 1), 'DIVERGES with no later PASS'),
    ([('2026-10-01', '2.1.902', 'DIVERGES'), ('2026-10-02', '2.1.902', 'ERROR')], date(2026, 10, 2),
     'DIVERGES with no later PASS'),
    ([('2026-10-01', '2.1.902', 'DIVERGES'), ('2026-10-02', '2.1.902', 'PASS')], date(2026, 10, 2), None),
])
def test_probe_due_rules(history, today, why):
    manifest = MANIFEST._replace(probes={'p1': (['beta.reference'], [])})
    due = check.due_probes(manifest, rows(*history), '2.1.902', 7, today)
    assert due == ([] if why is None else [{'probe': 'p1', 'why': why}])


def test_an_empty_registry_has_no_probe_due():
    assert check.due_probes(MANIFEST, [], '2.1.902', 7, date(2027, 1, 1)) == []


def test_the_audit_clock_is_shared_and_targets_the_oldest_group(docs_dir):
    s = fixture_state(docs_dir)
    assert check.due_audit(MANIFEST, s, 30, date(2026, 10, 1)) == {
        'group': 'alpha', 'last_audit': '2026-09-02', 'due_from': '2026-10-02', 'due': False}
    assert check.due_audit(MANIFEST, s, 30, date(2026, 10, 2)) == {
        'group': 'alpha', 'last_audit': '2026-09-02', 'due_from': '2026-10-02', 'due': True}
    for sid in ('alpha.overview', 'alpha.reference'):
        s['sections'][sid]['audited'] = {'release': '2.1.902', 'date': '2026-10-02'}
    assert check.due_audit(MANIFEST, s, 30, date(2026, 10, 3)) == {
        'group': 'beta', 'last_audit': '2026-10-02', 'due_from': '2026-11-01', 'due': False}


def test_http_get_retries_once_and_reports_any_other_failure(monkeypatch):
    '''R6.4: a 30-second timeout, one retry and the tool's User-Agent. A 404
    is an answer; any other failure ends as a FetchError.'''
    url = 'https://docs.example.invalid/en/tools.md'
    sent, outcomes = [], []

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self):
            return b'body'

    def urlopen(request, timeout):
        sent.append((request.full_url, request.get_header('User-agent'), timeout))
        outcome = outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    monkeypatch.setattr(check.urllib.request, 'urlopen', urlopen)
    outcomes[:] = [urllib.error.HTTPError(url, 404, 'Not Found', {}, None)]
    assert check.http_get(url) == (404, b'')
    outcomes[:] = [http.client.IncompleteRead(b'par'), Response()]
    assert check.http_get(url) == (200, b'body')
    outcomes[:] = [urllib.error.HTTPError(url, 503, 'Unavailable', {}, None), http.client.IncompleteRead(b'')]
    with pytest.raises(check.FetchError) as err:
        check.http_get(url)
    assert str(err.value) == f'{url}: IncompleteRead(0 bytes read)'
    assert sent == [(url, 'agent-skills-cc-guide/1 (Claude Code docs drift check)', 30)] * 5


def serving(folder, log=None, fail=()):
    '''A fake fetch serving folder's files by URL; unknown URLs are 404.'''
    def fetch(url):
        if log is not None:
            log.append(url)
        if url in fail:
            raise check.FetchError(f'{url}: timed out')
        path = folder / URLS.get(url, 'absent')
        return (200, path.read_bytes()) if path.is_file() else (404, b'')
    return fetch


def test_the_fetch_gate_refetches_every_page_only_when_the_head_moves(tmp_path, docs_dir):
    cache, log = tmp_path / 'cache', []
    check.live_docs(MANIFEST, cache, serving(docs_dir, log), NOW)
    assert len(log) == 2 + len(MANIFEST.pages())
    assert json.loads((cache / 'latest' / 'fetch.json').read_text())['changelog_head'] == '2.1.902'
    log.clear()
    (state.latest_docs(cache) / 'events.md').unlink()
    check.live_docs(MANIFEST, cache, serving(docs_dir, log), NOW)
    assert log == [MANIFEST.sources['changelog'], MANIFEST.sources['llms'],
                   docs.page_url('events', MANIFEST.sources)]
    log.clear()
    write_tree(docs_dir, {'changelog.md': DOCS['changelog.md'].replace(
        '<Update label="2.1.902"', '<Update label="2.1.903" description="October 3, 2026">\n</Update>\n'
        '<Update label="2.1.902"')})
    check.live_docs(MANIFEST, cache, serving(docs_dir, log), NOW)
    assert len(log) == 2 + len(MANIFEST.pages())


def test_a_page_unmapped_by_a_head_move_is_refetched_when_mapped_again(tmp_path, docs_dir):
    '''R6.3: runs on main and on --worktree share one cache with different manifests, so a
    page left unmapped by a head move must not come back as current, with the old head's text.'''
    cache, log = tmp_path / 'cache', []
    narrow = state.parse_manifest(MANIFEST_TOML.replace("'env-vars', 'platform:pricing'", "'env-vars'"))
    check.live_docs(MANIFEST, cache, serving(docs_dir, log), NOW)
    cached = state.latest_docs(cache) / 'platform_pricing.md'
    assert cached.is_file()
    head_b = DOCS['changelog.md'].replace(
        '<Update label="2.1.902"', '<Update label="2.1.903" description="October 3, 2026">\n</Update>\n'
        '<Update label="2.1.902"')
    write_tree(docs_dir, {'changelog.md': head_b, 'platform_pricing.md': 'Pricing text at head B.\n'})
    check.live_docs(narrow, cache, serving(docs_dir, log), NOW)
    assert not cached.exists()
    assert (state.latest_docs(cache) / 'changelog.md').is_file()
    log.clear()
    got = check.live_docs(MANIFEST, cache, serving(docs_dir, log), NOW)
    assert log == [MANIFEST.sources['changelog'], MANIFEST.sources['llms'],
                   docs.page_url('platform:pricing', MANIFEST.sources)]
    assert got.pages['platform:pricing'] == 'Pricing text at head B.\n'


def test_a_corrupt_fetch_record_is_a_setup_error(tmp_path, docs_dir):
    cache = tmp_path / 'cache'
    record = state.fetch_record(cache)
    record.parent.mkdir(parents=True)
    record.write_text('[]')
    with pytest.raises(state.SetupError) as err:
        check.live_docs(MANIFEST, cache, serving(docs_dir), NOW)
    assert str(err.value) == f'{record}: names no changelog_head release; delete it and run check'


def test_docs_read_as_other_than_utf8_are_a_setup_error_or_a_fetch_error(tmp_path, docs_dir):
    '''A local or cached file is a SetupError naming it; a fetched one is a
    fetch error, so a page is left unread and uncached, as on a failed fetch.'''
    (docs_dir / 'tools.md').write_bytes(b'\xff\xfe')
    with pytest.raises(state.SetupError) as err:
        offline(docs_dir)
    assert str(err.value) == f"{docs_dir / 'tools.md'}: not UTF-8 text (invalid start byte at byte 0)"
    cache = tmp_path / 'cache'
    got = check.live_docs(MANIFEST, cache, serving(docs_dir), NOW)
    assert (got.errors, got.unread) == ([f"{docs.page_url('tools', MANIFEST.sources)}: not UTF-8 text"], {'tools'})
    assert not (state.latest_docs(cache) / 'tools.md').exists()
    (docs_dir / 'changelog.md').write_bytes(b'\xff\xfe')
    with pytest.raises(check.FetchError) as err:
        check.live_docs(MANIFEST, cache, serving(docs_dir), NOW)
    assert str(err.value) == f"{MANIFEST.sources['changelog']}: not UTF-8 text"


def test_a_404_removes_the_stale_copy_and_reads_as_a_missing_page(tmp_path, docs_dir):
    cache = tmp_path / 'cache'
    s = fixture_state(docs_dir)
    check.live_docs(MANIFEST, cache, serving(docs_dir), NOW)
    (docs_dir / 'platform_pricing.md').unlink()
    write_tree(docs_dir, {'changelog.md': DOCS['changelog.md'].replace(
        '<Update label="2.1.902"', '<Update label="2.1.903" description="October 3, 2026">\n</Update>\n'
        '<Update label="2.1.902"')})
    got = check.live_docs(MANIFEST, cache, serving(docs_dir), NOW)
    assert not (state.latest_docs(cache) / 'platform_pricing.md').exists()
    found, _ = check.compare(MANIFEST, s, TERMS, got)
    assert [(f.kind, f.page) for f in found] == [('missing-page', 'platform:pricing')]


def run_check(repo, cache, folder=None, today=date(2026, 9, 10), fetch=None):
    return check.check(state.Source(repo), cache, docs_dir=folder, today=today, now=NOW, fetch=fetch)


@pytest.mark.parametrize('today, code', [(date(2026, 9, 10), 0), (date(2026, 9, 27), 1)])
def test_exit_zero_when_nothing_is_due_and_one_when_something_is(tmp_path, docs_dir, today, code):
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    assert run_check(repo, tmp_path / 'cache', docs_dir, today)[0] == code


@pytest.mark.parametrize('manifest, today, audit, probes', [
    # The audit clock came due on 2026-10-02. A 60-day changelog cadence keeps
    # the batch, oldest release 2026-09-20, from coming due until 2026-11-19.
    (MANIFEST_TOML.replace('changelog_days = 7', 'changelog_days = 60'), date(2026, 10, 4), True, []),
    # A registered probe with no row is due at once (R6.7); on 2026-09-10
    # nothing else is.
    (MANIFEST_TOML + "\n[[probe]]\nid = 'p1'\nsections = ['beta.reference']\n", date(2026, 9, 10), False,
     [{'probe': 'p1', 'why': 'never run'}]),
], ids=['audit', 'probe'])
def test_a_due_audit_or_a_due_probe_alone_exits_one(tmp_path, docs_dir, manifest, today, audit, probes):
    '''With every other term clear, the one due term alone must make check exit 1.'''
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    write_tree(repo, {state.MANIFEST: manifest})
    code, report, _ = run_check(repo, tmp_path / 'cache', docs_dir, today)
    due = report['due']
    assert (code, due['lint'], due['blocks'], due['changelog']['due'], due['audit']['due'], due['probes']) == (
        1, 0, 0, False, audit, probes)


def test_a_changed_block_or_a_lint_failure_is_due_at_once(tmp_path, docs_dir):
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    write_tree(docs_dir, {'events.md': DOCS['events.md'].replace('fires on beta', 'fires on gamma')})
    assert run_check(repo, tmp_path / 'cache', docs_dir)[0] == 1
    write_tree(docs_dir, DOCS)
    guide = repo / 'specs/guides/claude-code-customization-guide.md'
    guide.write_text(guide.read_text().replace('Alpha uses', 'Alpha now uses'))
    code, report, _ = run_check(repo, tmp_path / 'cache', docs_dir)
    assert (code, report['due']['lint']) == (1, 1)


def test_check_names_a_missing_block_from_the_cached_snapshot(tmp_path, docs_dir):
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    cache = tmp_path / 'cache'
    write_tree(state.snapshot_docs(cache, '2.1.900'), {'events.md': DOCS['events.md']})
    write_tree(docs_dir, {'events.md': DOCS['events.md'].replace('## Payload', '## Body')})
    _, report, _ = run_check(repo, cache, docs_dir)
    assert [(f['kind'], f['key']) for f in report['findings']['beta']] == [
        ('missing', 'Events › Payload'), ('new', 'Events › Body')]


def test_a_network_failure_exits_two_and_is_reported(tmp_path, docs_dir):
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    code, report, path = run_check(repo, tmp_path / 'cache',
                                   fetch=serving(docs_dir, fail={MANIFEST.sources['changelog']}))
    assert code == 2
    assert report['errors'] == [f"{MANIFEST.sources['changelog']}: timed out"]
    assert json.loads(path.read_text())['exit'] == 2


def test_a_failed_page_fetch_exits_two_without_comparing_that_page(tmp_path, docs_dir):
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    url = docs.page_url('tools', MANIFEST.sources)
    code, report, _ = run_check(repo, tmp_path / 'cache', fetch=serving(docs_dir, fail={url}))
    assert (code, report['errors'], report['findings']['alpha']) == (2, [f'{url}: timed out'], [])


def test_a_malformed_changelog_is_a_setup_error(tmp_path, docs_dir):
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    write_tree(docs_dir, {'changelog.md': DOCS['changelog.md'].replace('October 1, 2026', '2026-10-01')})
    with pytest.raises(ValueError) as cause:
        datetime.strptime('2026-10-01', '%B %d, %Y')
    with pytest.raises(state.SetupError) as err:
        run_check(repo, tmp_path / 'cache', docs_dir)
    assert str(err.value) == f'changelog: line 8: {cause.value}'


def test_the_report_is_keyed_by_the_baseline_hash_and_check_writes_only_its_cache_files(tmp_path, docs_dir):
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    cache = tmp_path / 'cache'

    def written():
        return sorted(p.relative_to(cache).as_posix() for p in cache.rglob('*') if p.is_file())
    _, report, path = run_check(repo, cache, docs_dir)
    baseline_sha = report['hashes']['baseline']
    assert path == cache / 'reports' / f'{baseline_sha[:12]}.json'
    assert set(report) == {'generated_at', 'inputs', 'docs', 'hashes', 'lint', 'latest_release', 'findings',
                           'deselected', 'llms', 'untriaged', 'releases', 'due', 'errors', 'exit'}
    assert git(repo, 'status', '--porcelain') == ''
    assert written() == [f'reports/{baseline_sha[:12]}.json']
    run_check(repo, cache, fetch=serving(docs_dir))
    assert git(repo, 'status', '--porcelain') == ''
    assert written() == ['latest/docs/changelog.md', 'latest/docs/env-vars.md', 'latest/docs/events.md',
                         'latest/docs/llms.txt', 'latest/docs/platform_pricing.md', 'latest/docs/tools.md',
                         'latest/fetch.json', f'reports/{baseline_sha[:12]}.json']


def test_llms_slugs_added_and_removed_since_the_baseline_are_listed(tmp_path, docs_dir):
    repo = drift_repo(tmp_path / 'repo', docs_dir)
    write_tree(docs_dir, {'llms.txt': DOCS['llms.txt'].replace('plugins/components', 'plugins/parts')})
    _, report, _ = run_check(repo, tmp_path / 'cache', docs_dir)
    assert report['llms'] == {'added': ['plugins/parts'], 'removed': ['plugins/components']}
