'''Tests for packets.py and `cli.py packets`: what each packet holds, the
index settle reads back, the triage split by release range, and the
snapshot copy verify and audit make (drift spec R6.11, R8.4-R8.7).'''
import json
from datetime import date, datetime, timedelta, timezone

import pytest

import blocks
import check
import cli
import packets
import settle
import state
import test_check
from cc_fixtures import (DOCS, FIXTURE_RELEASE, GUIDE_PATH, MANIFEST_TOML, docs_dir, fixture_repo,  # noqa: F401
                         fixture_state, git, guide_text, isolated_home, prime_cache, write_tree)

NOW = datetime(2026, 10, 4, 12, 0, tzinfo=timezone.utc)
ALL = ['alpha.overview', 'alpha.reference', 'beta.overview', 'beta.reference']
# Two tracked citing files: gate.sh's stamp is below alpha.overview's changed
# (2.1.900), so it is stale; fresh.md is not.
CITERS = {'hooks/gate.sh': '#!/bin/sh\n' + '#' + ' cc-guide: alpha.overview @2.1.899\nexit 0\n',
          'notes/fresh.md': '<!-- cc-guide: beta.overview @2.1.900 -->\nNotes.\n'}


@pytest.fixture
def world(tmp_path, docs_dir):
    '''A committed fixture repo with two citing files, and a cache holding
    the baseline's 2.1.900 snapshot and a latest fetch at 2.1.902.'''
    repo = fixture_repo(tmp_path / 'repo', {GUIDE_PATH: guide_text(), state.MANIFEST: MANIFEST_TOML,
                                            state.BASELINE: state.dump_baseline(fixture_state(docs_dir)), **CITERS})
    cache = tmp_path / 'cache'
    write_tree(state.snapshot_docs(cache, FIXTURE_RELEASE), DOCS)
    prime_cache(cache, docs_dir)
    return repo, cache


def load(world):
    repo, cache = world
    return packets.load(state.Source(repo), cache, NOW)


def swap_after_record_read(cache, tmp_path, monkeypatch):
    '''Make packets.load's record read be followed by a check that swaps
    latest/ to a 2.1.903 fetch with an edited page.'''
    newer = tmp_path / 'newer'
    write_tree(newer, DOCS)
    write_tree(newer, {'tools.md': DOCS['tools.md'].replace('alpha jobs', 'alpha gamma'),
                       'changelog.md': DOCS['changelog.md'].replace(
                           '<Update label="2.1.902"', '<Update label="2.1.903" description="October 3, 2026">\n'
                           '</Update>\n<Update label="2.1.902"')})
    real = packets.read_fetch_at

    def read_then_swap(root):
        record = real(root)
        check.live_docs(test_check.MANIFEST, cache, test_check.serving(newer), test_check.NOW)
        return record

    monkeypatch.setattr(packets, 'read_fetch_at', read_then_swap)


def test_load_reads_the_record_and_the_pages_from_one_generation(world, tmp_path, monkeypatch):
    '''Plan 109's D11: a check that swaps latest/ right after load read the
    record leaves load with the old fetch's head, changelog and pages.'''
    _, cache = world
    old = state.latest_dir(cache)
    swap_after_record_read(cache, tmp_path, monkeypatch)
    loaded = load(world)
    assert state.latest_dir(cache) != old
    assert loaded.head == '2.1.902'
    assert loaded.releases[0].label == '2.1.902'
    assert 'alpha gamma' not in json.dumps(loaded.docs.pages)


def test_load_names_the_pinned_generation_in_a_changelog_error(world, tmp_path, monkeypatch):
    _, cache = world
    old = state.latest_dir(cache)
    (old / 'docs' / 'changelog.md').write_text('no releases here\n')
    swap_after_record_read(cache, tmp_path, monkeypatch)
    with pytest.raises(state.SetupError) as raised:
        load(world)
    assert str(old / 'docs' / 'changelog.md') in str(raised.value)


def latest(world, files):
    write_tree(state.latest_docs(world[1]), files)


def index(folder):
    return json.loads((folder / packets.INDEX).read_text())


def test_a_triage_packet_holds_the_guide_and_every_bullet_of_each_untriaged_release(world, tmp_path):
    out = packets.triage(load(world), tmp_path / 'p', None)
    assert sorted(p.name for p in out.iterdir()) == ['blocks.md', 'guide.md', 'index.json', 'releases.md']
    assert (out / 'guide.md').read_text() == guide_text()
    i = index(out)
    assert {k: i[k] for k in ('mode', 'inputs', 'head', 'newest', 'blocks', 'held', 'owner')} == {
        'mode': 'triage', 'inputs': 'the working tree', 'head': '2.1.902', 'newest': '2.1.902',
        'blocks': [], 'held': [], 'owner': []}
    assert i['quotes'] == {'guide': ['guide.md'], 'source': ['blocks.md', 'releases.md']}
    assert i['groups'] == {'alpha': ['alpha.overview', 'alpha.reference'], 'beta': ['beta.overview', 'beta.reference']}
    assert i['releases'] == [
        {'label': '2.1.901', 'pending': ALL, 'hits': ['alpha.reference'],
         'bullets': [{'item': '2.1.901#1', 'hints': ['alpha.reference'],
                      'text': 'Added `ALPHA_ENV` to the alpha tools'}]},
        {'label': '2.1.902', 'pending': ALL, 'hits': ['beta.overview'],
         'bullets': [{'item': '2.1.902#1', 'hints': ['beta.overview'], 'text': 'Changed how `BETA_ENV` is read'},
                     {'item': '2.1.902#2', 'hints': [], 'text': 'Fixed a crash in the fixture tool'}]}]
    assert (out / 'releases.md').read_text().split('\n') == [
        '# Untriaged releases', '',
        '## 2.1.901', '',
        'Untriaged for 4 section(s); term hits, as hints only: alpha.reference.', '',
        '- 2.1.901#1 · hints: alpha.reference · Added `ALPHA_ENV` to the alpha tools', '',
        '## 2.1.902', '',
        'Untriaged for 4 section(s); term hits, as hints only: beta.overview.', '',
        '- 2.1.902#1 · hints: beta.overview · Changed how `BETA_ENV` is read',
        '- 2.1.902#2 · hints: none · Fixed a crash in the fixture tool', '', '']
    assert (out / 'blocks.md').read_text() == '# Block findings\n\nNone.\n\n'


def test_a_changed_block_shows_its_text_and_a_diff_against_its_snapshot(world, tmp_path):
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = packets.triage(load(world), tmp_path / 'p', None)
    # lines: blocks.md's lines that hold the block's own text, the only lines
    # its source quote may come from.
    assert index(out)['blocks'] == [{'item': 'B1', 'group': 'alpha', 'kind': 'changed', 'ref': 'tools › Tools',
                                     'page': 'tools', 'key_hash': blocks.key_hash('Tools'),
                                     'candidates': ['alpha.overview'], 'lines': [[9, 10], [15, 20]]}]
    assert (out / 'blocks.md').read_text().split('\n') == [
        '# Block findings', '',
        '## B1 · changed · [alpha] tools › Tools', '',
        'Candidate sections: alpha.overview', '',
        'Current text:', '```', '# Tools', 'The `ALPHA_TOOL` runs alpha batches.', '```', '',
        'Diff against the 2.1.900 snapshot:', '```',
        '--- the 2.1.900 snapshot', '+++ now', '@@ -1,2 +1,2 @@', ' # Tools',
        '-The `ALPHA_TOOL` runs alpha jobs.', '+The `ALPHA_TOOL` runs alpha batches.', '```', '', '']


def test_a_missing_block_shows_its_baselined_text_read_by_key_hash(world, tmp_path):
    '''A block gone from the page has no current text, so the packet reads
    its baselined text from the page's snapshot by key hash, the lookup
    check uses to name it (deferred: Carry each missing block's key hash).'''
    latest(world, {'events.md': DOCS['events.md'].replace('## Payload', '## Body')})
    out = packets.triage(load(world), tmp_path / 'p', None)
    payload = blocks.key_hash('Events › Payload')
    assert [(b['kind'], b['ref'], b['key_hash']) for b in index(out)['blocks']] == [
        ('missing', 'events › Events › Payload', payload),
        ('new', 'events › Events › Body', blocks.key_hash('Events › Body'))]
    text = (out / 'blocks.md').read_text()
    assert ('Baselined text, from the 2.1.900 snapshot (the block has left the page):\n```\n'
            '## Payload\nThe payload carries `BETA_ENV`.\n```\n') in text
    assert 'Current text:\n```\n## Body\nThe payload carries `BETA_ENV`.\n```\n' in text


def test_without_its_snapshot_a_missing_block_goes_by_key_hash_and_says_so(world, tmp_path):
    latest(world, {'events.md': DOCS['events.md'].replace('## Payload', '## Body')})
    (state.snapshot_docs(world[1], FIXTURE_RELEASE) / 'events.md').unlink()
    out = packets.triage(load(world), tmp_path / 'p', None)
    payload = blocks.key_hash('Events › Payload')
    assert index(out)['blocks'][0]['ref'] == f'events › {payload}'
    assert f'## B1 · missing · [beta] events › {payload}\n\nCandidate sections: beta.overview, beta.reference\n\n' \
           'No cached snapshot holds its baselined text.\n' in (out / 'blocks.md').read_text()


def test_a_fence_in_a_block_gets_a_longer_outer_fence():
    assert packets.fenced('a\n```json\n{}\n```') == ['````', 'a', '```json', '{}', '```', '````']
    assert packets.fenced('plain') == ['```', 'plain', '```']


def test_every_release_range_carries_the_block_findings(world, tmp_path):
    '''R8.4's split: block findings ride in the range being triaged, the
    oldest first, so they are settled there against the current docs.'''
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    early = index(packets.triage(load(world), tmp_path / 'early', '2.1.901'))
    assert (early['newest'], [b['item'] for b in early['blocks']], early['held']) == ('2.1.901', ['B1'], [])
    assert [r['label'] for r in early['releases']] == ['2.1.901']
    with pytest.raises(state.SetupError) as err:
        packets.triage(load(world), tmp_path / 'bad', '2.1.950')
    assert str(err.value) == '--through 2.1.950: not an untriaged release (2.1.901, 2.1.902)'


def test_more_releases_than_a_range_name_the_first_ranges_through_and_each_range_the_next(world, tmp_path):
    '''The tool names the ranges, so a session never has to: the first
    range ends at the size-th oldest untriaged release, and each range's
    index names the next, the size-th untriaged release after its own.'''
    with pytest.raises(state.SetupError) as err:
        packets.triage(load(world), tmp_path / 'p', None, size=1)
    assert str(err.value) == ('2 untriaged releases after 2.1.900: take them in ranges of 1, the first with '
                              '--through 2.1.901, or all at once with --through 2.1.902')
    assert not (tmp_path / 'p').exists()
    assert index(packets.triage(load(world), tmp_path / 'a', '2.1.901', size=1))['next_through'] == '2.1.902'
    assert index(packets.triage(load(world), tmp_path / 'b', '2.1.902', size=1))['next_through'] is None


def test_a_range_counts_from_the_newest_checked_release_so_a_deferral_never_repeats_it(world, tmp_path):
    '''A section deferred in an earlier range keeps its old `checked`, so a
    later session counts the range from the newest release any section is
    checked through: the deferred section's earlier releases ride along
    without counting, and the first range is never named again.'''
    repo, _ = world
    s = state.parse_baseline((repo / state.BASELINE).read_text())
    for sid in ('alpha.overview', 'alpha.reference'):
        s['sections'][sid]['checked'] = {'release': '2.1.901', 'date': '2026-10-04'}
    (repo / state.BASELINE).write_text(state.dump_baseline(s))
    i = index(packets.triage(load(world), tmp_path / 'p', None, size=1))
    assert ([r['label'] for r in i['releases']], i['newest'], i['next_through']) == (
        ['2.1.901', '2.1.902'], '2.1.902', None)
    assert i['releases'][0]['pending'] == ['beta.overview', 'beta.reference']


def test_a_missing_page_is_an_owner_item_whose_sections_are_held(world, tmp_path):
    (state.latest_docs(world[1]) / 'events.md').unlink()
    i = index(packets.triage(load(world), tmp_path / 'p', None))
    assert (i['owner'], i['held']) == (['missing page events in group beta: drop or remap it in manifest.toml'],
                                       ['beta.overview', 'beta.reference'])


def test_nothing_to_triage_writes_no_packet(world, tmp_path):
    repo, _ = world
    s = state.parse_baseline((repo / state.BASELINE).read_text())
    for sid in s['sections'].values():
        sid['checked'] = {'release': '2.1.902', 'date': '2026-10-04'}
    (repo / state.BASELINE).write_text(state.dump_baseline(s))
    assert packets.triage(load(world), tmp_path / 'p', None) is None
    assert not (tmp_path / 'p').exists()


def test_a_packet_never_writes_over_an_earlier_one(world, tmp_path):
    write_tree(tmp_path / 'p', {'report.md': 'old'})
    with pytest.raises(state.SetupError) as err:
        packets.triage(load(world), tmp_path / 'p', None)
    assert str(err.value) == f"{tmp_path / 'p'}: not an empty directory; packets never write over an earlier packet"


def test_packets_need_a_latest_fetch(world, tmp_path):
    state.fetch_record(world[1]).unlink()
    with pytest.raises(state.SetupError) as err:
        load(world)
    assert str(err.value) == 'no latest fetch: run check --worktree first'


def test_the_cli_writes_a_triage_packet_under_the_cache_by_default(world, monkeypatch, capsys):
    repo, cache = world
    monkeypatch.setattr(cli, 'REPO', repo)
    assert cli.main(['--cache', str(cache), 'packets', '--triage'], now=NOW) == 0
    out = cache / 'packets' / '20261004T120000-triage'
    assert capsys.readouterr() == (f'wrote triage packet {out}\n', '')
    assert index(out)['mode'] == 'triage'
    assert cli.main(['--cache', str(cache), 'packets', '--audit', '--through', '2.1.901'], now=NOW) == 2
    assert capsys.readouterr() == ('', 'cc-guide: --through goes with --triage\n')


def test_a_verify_packet_per_group_copies_the_groups_pages_to_the_head_snapshot(world, tmp_path):
    '''R8.5: one verifier per group, which greps the head release's snapshot,
    copied from latest/.'''
    made = packets.verify(load(world), tmp_path / 'v', ['beta.reference', 'alpha.overview'], None)
    assert made == [tmp_path / 'v' / 'alpha', tmp_path / 'v' / 'beta']
    head = state.snapshot_docs(world[1], '2.1.902')
    assert sorted(p.name for p in head.iterdir()) == ['env-vars.md', 'events.md', 'platform_pricing.md', 'tools.md']
    assert (head / 'tools.md').read_text() == DOCS['tools.md']
    i = index(made[0])
    # checked: each section's checked release, so settle never advances one
    # past the triage's target backwards (second review, finding 6).
    assert {k: i[k] for k in ('mode', 'group', 'sections', 'lines', 'checked', 'docs', 'advance_to', 'cleared',
                              'held', 'blocks')} == {
        'mode': 'verify', 'group': 'alpha', 'sections': ['alpha.overview'], 'lines': {'alpha.overview': [11, 15]},
        'checked': {'alpha.overview': '2.1.900'}, 'docs': str(head), 'advance_to': None, 'cleared': [], 'held': [],
        'blocks': []}
    # A doc quote comes from the snapshot's pages or the packet's changelog,
    # never from the report, the guide copy or the index.
    assert i['quotes'] == {'guide': ['guide.md'], 'changelog': ['changelog.md'], 'docs': [str(head)]}
    assert sorted(p.name for p in made[0].iterdir()) == ['blocks.md', 'changelog.md', 'guide.md', 'index.json',
                                                         'sections.md']
    assert (made[1] / 'sections.md').read_text() == (
        '# Sections\n\n## beta.reference · guide lines 37-41\n\nNo triage row sent it here.\n\n')


def swap_latest_to_newer(cache, tmp_path):
    '''A check that swaps latest/ to a 2.1.903 fetch with an edited page.'''
    newer = tmp_path / 'newer'
    write_tree(newer, DOCS)
    write_tree(newer, {'tools.md': DOCS['tools.md'].replace('alpha jobs', 'alpha gamma'),
                       'changelog.md': DOCS['changelog.md'].replace(
                           '<Update label="2.1.902"', '<Update label="2.1.903" description="October 3, 2026">\n'
                           '</Update>\n<Update label="2.1.902"')})
    check.live_docs(test_check.MANIFEST, cache, test_check.serving(newer), test_check.NOW)


def test_the_verify_snapshot_holds_the_pages_load_pinned_when_latest_swaps(world, tmp_path):
    '''Plan 109 R6.4: the head and the pages come from one generation.'''
    loaded = load(world)
    old = state.latest_dir(world[1])
    swap_latest_to_newer(world[1], tmp_path)
    assert state.latest_dir(world[1]) != old
    packets.verify(loaded, tmp_path / 'v', ['alpha.overview'], None)
    held = state.snapshot_docs(world[1], '2.1.902') / 'tools.md'
    assert held.read_text() == DOCS['tools.md']


def test_the_audit_snapshot_holds_the_pages_load_pinned_when_latest_swaps(world, tmp_path):
    loaded = load(world)
    swap_latest_to_newer(world[1], tmp_path)
    packets.audit(loaded, tmp_path / 'a', 'alpha')
    held = state.snapshot_docs(world[1], '2.1.902') / 'tools.md'
    assert held.read_text() == DOCS['tools.md']


def test_the_snapshot_skips_a_page_the_pinned_generation_lacks_though_latest_has_it(world, tmp_path):
    (state.latest_dir(world[1]) / 'docs' / 'events.md').unlink()
    loaded = load(world)
    swap_latest_to_newer(world[1], tmp_path)
    assert (state.latest_docs(world[1]) / 'events.md').is_file()
    packets.audit(loaded, tmp_path / 'a', 'beta')
    held = state.snapshot_docs(world[1], '2.1.902')
    assert not (held / 'events.md').exists()


def test_a_verify_packet_from_a_settled_triage_carries_its_rows_and_bookkeeping(world, tmp_path):
    write_tree(tmp_path / 't', {packets.SETTLED: json.dumps(
        {'mode': 'triage', 'advance_to': '2.1.902', 'verify': ['alpha.overview'], 'cleared': ['alpha.reference'],
         'held': ['alpha.overview'], 'rows': {'alpha.overview': ['B1: TOUCHES']}})})
    made = packets.verify(load(world), tmp_path / 'v', [], tmp_path / 't' / packets.SETTLED)
    i = index(made[0])
    assert (i['sections'], i['advance_to'], i['cleared'], i['held']) == (
        ['alpha.overview'], '2.1.902', ['alpha.reference'], ['alpha.overview'])
    assert (made[0] / 'sections.md').read_text() == (
        '# Sections\n\n## alpha.overview · guide lines 11-15\n\nTriage rows that sent it here:\n- B1: TOUCHES\n\n')


def test_the_snapshot_copy_never_overwrites_other_text_or_the_bootstrap(world, tmp_path, docs_dir):
    head = state.snapshot_docs(world[1], '2.1.902')
    write_tree(head, {'tools.md': DOCS['tools.md']})  # the same bytes: copied again
    packets.verify(load(world), tmp_path / 'v', ['alpha.overview'], None)
    write_tree(head, {'tools.md': 'other text\n'})
    with pytest.raises(state.SetupError) as err:
        packets.verify(load(world), tmp_path / 'w', ['alpha.overview'], None)
    assert str(err.value) == (f"tools: {head / 'tools.md'} already holds different text, which another group may "
                              'have baselined; it is never overwritten')
    assert not (tmp_path / 'w').exists()
    prime_cache(world[1], docs_dir, head='2.1.288')
    with pytest.raises(state.SetupError) as err:
        packets.verify(load(world), tmp_path / 'x', ['alpha.overview'], None)
    assert str(err.value) == (f"{state.snapshot_docs(world[1], '2.1.288')} is the bootstrap snapshot, which is never "
                              'written (R2.6): run check to fetch a newer release first')


def test_verify_refuses_an_unknown_section_and_a_missing_or_foreign_settled_file(world, tmp_path):
    with pytest.raises(state.SetupError) as err:
        packets.verify(load(world), tmp_path / 'v', ['gamma.overview'], None)
    assert str(err.value) == 'unknown section IDs: gamma.overview'
    with pytest.raises(state.SetupError) as err:
        packets.verify(load(world), tmp_path / 'v', ['alpha.overview'], tmp_path / 't' / packets.SETTLED)
    assert str(err.value) == f"{tmp_path / 't' / packets.SETTLED}: not found; run settle on the triage packet first"
    write_tree(tmp_path / 't', {packets.SETTLED: json.dumps({'mode': 'verify'})})
    with pytest.raises(state.SetupError) as err:
        packets.verify(load(world), tmp_path / 'v', ['alpha.overview'], tmp_path / 't' / packets.SETTLED)
    assert str(err.value) == f"{tmp_path / 't' / packets.SETTLED}: not a settled triage"


def test_verify_and_audit_hold_a_missing_pages_sections(world, tmp_path):
    (state.latest_docs(world[1]) / 'events.md').unlink()
    assert index(packets.audit(load(world), tmp_path / 'a', 'beta'))['held'] == ['beta.overview', 'beta.reference']
    made = packets.verify(load(world), tmp_path / 'v', ['beta.reference', 'alpha.overview'], None)
    assert [index(m)['held'] for m in made] == [[], ['beta.overview', 'beta.reference']]


def test_verify_needs_section_ids_or_a_triage_that_sent_some(world, tmp_path):
    with pytest.raises(state.SetupError) as err:
        packets.verify(load(world), tmp_path / 'v', [], None)
    assert str(err.value) == '--verify needs section IDs, or --from a settled triage'
    write_tree(tmp_path / 't', {packets.SETTLED: json.dumps({'mode': 'triage', 'verify': []})})
    with pytest.raises(state.SetupError) as err:
        packets.verify(load(world), tmp_path / 'v', [], tmp_path / 't' / packets.SETTLED)
    assert str(err.value) == f"{tmp_path / 't' / packets.SETTLED}: its triage sent no section to verify"


def test_a_packet_never_lands_inside_a_checkout(world, tmp_path):
    '''Review finding 10, and the second review's finding 4: packets hold
    docs text, so a destination inside any checkout is refused (spec
    Decision 10), through a symlink too: the repo's own, the main checkout
    a worktree sits in, and a sibling worktree, whose `.git` is a file.'''
    repo, _ = world
    (tmp_path / 'link').symlink_to(repo)
    for out in (repo / 'packets', tmp_path / 'link' / 'packets'):
        with pytest.raises(state.SetupError) as err:
            packets.triage(load(world), out, None)
        assert str(err.value) == (f'{out}: inside the checkout {repo.resolve()}; packets hold docs text, so they '
                                  'live outside every checkout')
    assert not (repo / 'packets').exists()
    main = tmp_path / 'main'
    (main / '.git').mkdir(parents=True)
    worktree, sibling = main / 'wt' / 'one', main / 'wt' / 'two'
    for root in (worktree, sibling):
        root.mkdir(parents=True)
        (root / '.git').write_text(f'gitdir: {main}/.git/worktrees/{root.name}\n')
    for out, checkout in ((main / 'packets', main), (sibling / 'packets', sibling)):
        with pytest.raises(state.SetupError) as err:
            packets.new_dir(out, worktree)
        assert str(err.value) == (f'{out}: inside the checkout {checkout.resolve()}; packets hold docs text, so '
                                  'they live outside every checkout')
        assert not out.exists()
    assert packets.new_dir(tmp_path / 'cache' / 'packets', worktree).is_dir()


def test_an_audit_packet_holds_every_section_its_untriaged_releases_and_its_blocks(world, tmp_path):
    latest(world, {'events.md': DOCS['events.md'].replace('on beta', 'on every beta')})
    out = packets.audit(load(world), tmp_path / 'a', 'beta')
    i = index(out)
    assert (i['mode'], i['group'], i['sections']) == ('audit', 'beta', ['beta.overview', 'beta.reference'])
    assert [(r['label'], r['pending'], r['hits']) for r in i['releases']] == [
        ('2.1.901', ['beta.overview', 'beta.reference'], []),
        ('2.1.902', ['beta.overview', 'beta.reference'], ['beta.overview'])]
    assert [b['ref'] for b in i['blocks']] == ['events › Events']
    assert sorted(p.name for p in out.iterdir()) == ['blocks.md', 'changelog.md', 'guide.md', 'index.json',
                                                     'releases.md', 'sections.md']
    with pytest.raises(state.SetupError) as err:
        packets.audit(load(world), tmp_path / 'b', 'gamma')
    assert str(err.value) == 'unknown group gamma'


def test_a_files_packet_per_stale_file_marks_the_sections_changed_since_its_stamp(world, tmp_path):
    made = packets.files(load(world), tmp_path / 'f', [])
    assert made == [tmp_path / 'f' / 'hooks__gate.sh']
    i = index(made[0])
    assert {k: i[k] for k in ('mode', 'file', 'copy', 'stamp', 'sections', 'lines', 'changed', 'quotes')} == {
        'mode': 'files', 'file': 'hooks/gate.sh', 'copy': 'cited_gate.sh', 'stamp': '2.1.899',
        'sections': ['alpha.overview'], 'lines': {'alpha.overview': [11, 15]}, 'changed': ['alpha.overview'],
        'quotes': {'guide': ['guide.md']}}
    assert (made[0] / 'cited_gate.sh').read_text() == CITERS['hooks/gate.sh']
    assert (made[0] / 'sections.md').read_text().split('\n')[:9] == [
        '# Sections', '', '## alpha.overview · guide lines 11-15', '',
        'Changed after @2.1.899: now @2.1.900.', '', '```', '## 1. Alpha', '']


def test_files_takes_named_citing_files_and_refuses_any_the_lint_never_reads(world, tmp_path):
    fresh = packets.files(load(world), tmp_path / 'f', ['notes/fresh.md'])
    assert index(fresh[0])['changed'] == []
    assert 'Unchanged since @2.1.900.' in (fresh[0] / 'sections.md').read_text()
    write_tree(world[0], {'specs/x.md': '<!-- cc-guide: beta.overview @2.1.900 -->\n'})
    with pytest.raises(state.SetupError) as err:
        packets.files(load(world), tmp_path / 'g', ['specs/x.md', 'hooks/gate.sh'])
    assert str(err.value) == 'not a citing file the lint reads: specs/x.md'


def commit_tree(world, files):
    write_tree(world[0], files)
    git(world[0], 'add', '-A')
    git(world[0], 'commit', '-qm', 'tree')


def skill_md(name):
    return f'---\nname: {name}\ndescription: Use when a fixture needs it.\n# cc-guide: alpha.overview @2.1.900\n---\n'


def with_skill(world, folder='skills/demo'):
    commit_tree(world, {f'{folder}/SKILL.md': skill_md(folder), f'{folder}/beside.md': f'{folder} beside\n',
                        f'{folder}/references/a.md': f'{folder} a\n', f'{folder}/references/deep/b.md': f'{folder} b\n',
                        f'{folder}/README.md': 'readme\n', f'{folder}/scripts/notes.md': 'notes\n'})


def test_a_files_packet_for_a_skill_copies_each_covered_file(world, tmp_path):
    with_skill(world)
    out = packets.files(load(world), tmp_path / 'f', ['skills/demo/SKILL.md', 'hooks/gate.sh'])
    skill, gate = (index(folder) for folder in out)
    assert skill['covered'] == {'skills/demo/beside.md': 'covered/beside.md',
                                'skills/demo/references/a.md': 'covered/references/a.md',
                                'skills/demo/references/deep/b.md': 'covered/references/deep/b.md'}
    assert sorted(str(p.relative_to(out[0])) for p in (out[0] / 'covered').rglob('*.md')) == sorted(
        skill['covered'].values())
    for repo_path, copy in skill['covered'].items():
        assert (out[0] / copy).read_text() == (world[0] / repo_path).read_text()
    assert gate['covered'] == {} and not (out[1] / 'covered').exists()


def test_each_skill_in_one_run_gets_only_its_own_covered_files(world, tmp_path):
    with_skill(world)
    with_skill(world, '.claude/skills/local')
    out = packets.files(load(world), tmp_path / 'f', ['.claude/skills/local/SKILL.md', 'skills/demo/SKILL.md'])
    local, demo = (index(folder) for folder in out)
    assert local['covered'] == {'.claude/skills/local/beside.md': 'covered/beside.md',
                                '.claude/skills/local/references/a.md': 'covered/references/a.md',
                                '.claude/skills/local/references/deep/b.md': 'covered/references/deep/b.md'}
    assert demo['covered'] == {'skills/demo/beside.md': 'covered/beside.md',
                               'skills/demo/references/a.md': 'covered/references/a.md',
                               'skills/demo/references/deep/b.md': 'covered/references/deep/b.md'}
    assert (out[0] / 'covered/beside.md').read_text() == '.claude/skills/local beside\n'
    assert (out[1] / 'covered/beside.md').read_text() == 'skills/demo beside\n'


def test_a_skill_with_nothing_covered_gets_no_covered_folder(world, tmp_path):
    commit_tree(world, {'skills/bare/SKILL.md': skill_md('bare'), 'skills/bare/README.md': 'r\n',
                        'skills/bare/scripts/n.md': 'n\n', 'skills/bare/data.txt': 'd\n'})
    (out,) = packets.files(load(world), tmp_path / 'f', ['skills/bare/SKILL.md'])
    assert index(out)['covered'] == {} and not (out / 'covered').exists()


def test_a_skill_with_many_covered_files_still_gets_one_packet_holding_all_of_them(world, tmp_path):
    with_skill(world)
    commit_tree(world, {f'skills/demo/references/more/n{n:02d}.md': f'{n}\n' for n in range(40)})
    out = packets.files(load(world), tmp_path / 'f', ['skills/demo/SKILL.md'])
    assert len(out) == 1
    covered = index(out[0])['covered']
    assert len(covered) == 43
    assert all((out[0] / copy).is_file() for copy in covered.values())


def test_a_files_packet_leaves_out_a_covered_file_removed_from_disk(world, tmp_path):
    with_skill(world)
    (world[0] / 'skills/demo/beside.md').unlink()  # plain rm: the index still lists it
    (out,) = packets.files(load(world), tmp_path / 'f', ['skills/demo/SKILL.md'])
    assert index(out)['covered'] == {'skills/demo/references/a.md': 'covered/references/a.md',
                                     'skills/demo/references/deep/b.md': 'covered/references/deep/b.md'}
    assert sorted(str(p.relative_to(out)) for p in (out / 'covered').rglob('*.md')) == [
        'covered/references/a.md', 'covered/references/deep/b.md']


def test_a_covered_file_removed_from_one_skill_stops_no_other_skills_packet(world, tmp_path):
    with_skill(world)
    with_skill(world, '.claude/skills/local')
    (world[0] / 'skills/demo/beside.md').unlink()
    both = ['skills/demo/SKILL.md', '.claude/skills/local/SKILL.md']
    for n, targets in enumerate((both, both[::-1])):  # the skill with the removed file first, then last
        out = packets.files(load(world), tmp_path / f'f{n}', targets)
        by_file = {index(folder)['file']: index(folder)['covered'] for folder in out}
        assert sorted(by_file) == sorted(both)
        assert sorted(by_file['skills/demo/SKILL.md']) == ['skills/demo/references/a.md',
                                                         'skills/demo/references/deep/b.md']
        assert sorted(by_file['.claude/skills/local/SKILL.md']) == [
            '.claude/skills/local/beside.md', '.claude/skills/local/references/a.md',
            '.claude/skills/local/references/deep/b.md']


def test_a_files_packet_copies_the_covered_files_of_the_source_it_reads(world, tmp_path):
    with_skill(world)
    write_tree(world[0], {'skills/demo/beside.md': 'edited\n', 'skills/demo/untracked.md': 'u\n',
                          'skills/demo/staged.md': 's\n'})
    git(world[0], 'add', 'skills/demo/staged.md')
    (now,) = packets.files(load(world), tmp_path / 'w', ['skills/demo/SKILL.md'])
    assert sorted(index(now)['covered']) == ['skills/demo/beside.md', 'skills/demo/references/a.md',
                                            'skills/demo/references/deep/b.md', 'skills/demo/staged.md']
    assert (now / 'covered/beside.md').read_text() == 'edited\n'
    committed = packets.load(state.Source(world[0], 'main'), world[1], NOW)
    (then,) = packets.files(committed, tmp_path / 'r', ['skills/demo/SKILL.md'])
    assert sorted(index(then)['covered']) == ['skills/demo/beside.md', 'skills/demo/references/a.md',
                                             'skills/demo/references/deep/b.md']
    assert (then / 'covered/beside.md').read_text() == 'skills/demo beside\n'
    assert not (then / 'covered/untracked.md').exists() and not (now / 'covered/untracked.md').exists()


def test_a_files_packet_keeps_the_names_of_covered_files_with_odd_characters(world, tmp_path):
    commit_tree(world, {'skills/odd name/SKILL.md': skill_md('odd'), 'skills/odd name/r\u00e9f/\u00e9 notes.md': 'a\n',
                        'skills/odd name/a[1]*.md': 'b\n', "skills/odd name/q'uote.md": 'c\n"'})
    for ref in (None, 'main'):
        world_here = packets.load(state.Source(world[0], ref), world[1], NOW)
        (out,) = packets.files(world_here, tmp_path / f'f-{ref}', ['skills/odd name/SKILL.md'])
        assert index(out)['covered'] == {
            "skills/odd name/a[1]*.md": 'covered/a[1]*.md', "skills/odd name/q'uote.md": "covered/q'uote.md",
            'skills/odd name/r\u00e9f/\u00e9 notes.md': 'covered/r\u00e9f/\u00e9 notes.md'}
        assert (out / 'covered/r\u00e9f/\u00e9 notes.md').read_text() == 'a\n'


def test_a_files_packet_marks_a_section_whose_text_changed_since_the_file_was_cited(world, docs_dir, tmp_path):
    # fresh.md's stamp is not behind beta.overview's changed release, so only
    # the hash that `baseline cite` recorded shows that the text moved under it.
    s = fixture_state(docs_dir)
    s['cited'] = {'notes/fresh.md': {'beta.overview': 'sha256:' + '0' * 64}}
    write_tree(world[0], {state.BASELINE: state.dump_baseline(s)})
    made = packets.files(load(world), tmp_path / 'f', [])
    fresh = tmp_path / 'f' / 'notes__fresh.md'
    assert fresh in made
    assert index(fresh)['changed'] == ['beta.overview']
    assert (fresh / 'sections.md').read_text().split('\n')[4] == (
        'Changed after @2.1.900: its text differs from the text the file was cited against.')


def test_files_with_no_stale_citation_and_no_paths_is_an_error(world, tmp_path):
    repo, _ = world
    write_tree(repo, {'hooks/gate.sh': CITERS['hooks/gate.sh'].replace('@2.1.899', '@2.1.900')})
    with pytest.raises(state.SetupError) as err:
        packets.files(load(world), tmp_path / 'f', [])
    assert str(err.value) == 'no stale citation: name the files to review'


def test_the_cli_writes_verify_audit_and_files_packets(world, monkeypatch, capsys, tmp_path):
    repo, cache = world
    monkeypatch.setattr(cli, 'REPO', repo)
    base = ['--cache', str(cache), 'packets']
    assert cli.main([*base, '--verify', 'beta.overview', '--out', str(tmp_path / 'v')], now=NOW) == 0
    assert cli.main([*base, '--audit', '--out', str(tmp_path / 'a')], now=NOW, today=NOW.date()) == 0
    assert cli.main([*base, '--files', str(repo / 'hooks/gate.sh'), '--out', str(tmp_path / 'f')], now=NOW) == 0
    assert capsys.readouterr() == (f"wrote verify packet {tmp_path / 'v' / 'beta'}\n"
                                   f"wrote audit packet {tmp_path / 'a'}\n"
                                   f"wrote files packet {tmp_path / 'f' / 'hooks__gate.sh'}\n", '')
    assert index(tmp_path / 'a')['group'] == 'alpha'  # the due group, oldest audited in manifest order
    assert cli.main([*base, '--files', '--from', str(tmp_path)], now=NOW) == 2
    assert capsys.readouterr() == ('', 'cc-guide: --from goes with --verify\n')
    # Due from 2026-10-02, 30 days after the fixture's audits: before then,
    # only a named group is audited.
    early = date(2026, 9, 30)
    assert cli.main([*base, '--audit', '--out', str(tmp_path / 'b')], now=NOW, today=early) == 2
    assert capsys.readouterr() == ('', 'cc-guide: no audit is due before 2026-10-02: name a group to audit one '
                                       'anyway\n')
    assert cli.main([*base, '--audit', 'beta', '--out', str(tmp_path / 'b')], now=NOW, today=early) == 0
    write_tree(tmp_path / 't', {packets.SETTLED: json.dumps({'mode': 'triage', 'verify': ['beta.overview']})})
    assert cli.main([*base, '--verify', '--from', str(tmp_path / 't'), '--out', str(tmp_path / 'w')], now=NOW) == 0
    assert capsys.readouterr()[0].split('\n')[-2] == f"wrote verify packet {tmp_path / 'w' / 'beta'}"


def test_a_refused_out_leaves_the_head_snapshot_unwritten(world, tmp_path):
    '''m4 (final review): verify and audit check --out before they copy the
    groups' pages to the head release's snapshot, so a refused --out leaves
    the cache as it was.'''
    repo, cache = world
    write_tree(tmp_path / 'full', {'report.md': 'old'})
    refusals = {tmp_path / 'full': f"{tmp_path / 'full'}: not an empty directory; packets never write over an "
                                   'earlier packet',
                repo / 'packets': f"{repo / 'packets'}: inside the checkout {repo.resolve()}; packets hold docs text, "
                                  'so they live outside every checkout'}
    for out, message in refusals.items():
        for make in (lambda: packets.verify(load(world), out, ['alpha.overview'], None),
                     lambda: packets.audit(load(world), out, 'alpha')):
            with pytest.raises(state.SetupError) as err:
                make()
            assert str(err.value) == message
    assert not state.snapshot_docs(cache, '2.1.902').exists()
    assert not (repo / 'packets').exists()


def test_verify_from_a_triage_refuses_a_section_the_triage_cleared(world, tmp_path):
    '''m8 (final review): the triage's own commands advance the sections it
    cleared, so --from never takes one into a verify again (S24).'''
    out = packets.triage(load(world), tmp_path / 'p', None)
    (out / packets.REPORT).write_text('2.1.901 | alpha.overview\n2.1.902 | none\n')
    settle.settle(out)
    with pytest.raises(state.SetupError) as err:
        packets.verify(load(world), tmp_path / 'v', ['alpha.overview', 'alpha.reference'], out / packets.SETTLED)
    assert str(err.value) == (f'{out / packets.SETTLED}: its triage cleared alpha.reference, which its own commands '
                              'advance; verify without --from')
    assert not (tmp_path / 'v').exists()


def test_a_settled_file_that_is_no_settled_triage_is_one_error_line(world, tmp_path):
    '''m5 (final review): never a JSONDecodeError or an AttributeError.'''
    path = tmp_path / 't' / packets.SETTLED
    write_tree(tmp_path / 't', {packets.SETTLED: '{'})
    with pytest.raises(json.JSONDecodeError) as cause:
        json.loads('{')
    with pytest.raises(state.SetupError) as err:
        packets.verify(load(world), tmp_path / 'v', [], path)
    assert str(err.value) == f'{path}: not valid JSON ({cause.value}); settle the triage packet again'
    path.write_text('[]')
    with pytest.raises(state.SetupError) as err:
        packets.verify(load(world), tmp_path / 'v', [], path)
    assert str(err.value) == f'{path}: not a settled triage'


@pytest.mark.parametrize('renamed, cited', [(False, 'gamma.overview'), (True, 'beta.renamed'),
                                            (True, 'beta.reference')],
                         ids=['in-neither', 'guide-only', 'baseline-only'])
def test_files_refuses_a_citer_naming_a_section_the_baseline_or_the_guide_lacks(world, tmp_path, renamed, cited):
    '''m5 (final review): a cited ID the lint would flag is one error line
    naming it, never a KeyError, and no packet is written.'''
    repo, _ = world
    write_tree(repo, {'hooks/bad.sh': '#!/bin/sh\n' + '#' + f' cc-guide: {cited} @2.1.900\nexit 0\n'})
    git(repo, 'add', '-A')
    git(repo, 'commit', '-qm', 'cite')
    if renamed:
        guide = repo / GUIDE_PATH
        guide.write_text(guide.read_text().replace('<!-- cc: beta.reference -->', '<!-- cc: beta.renamed -->'))
    with pytest.raises(state.SetupError) as err:
        packets.files(load(world), tmp_path / 'f', ['hooks/bad.sh'])
    assert str(err.value) == f'hooks/bad.sh: cites section IDs the baseline or the guide lacks: {cited}; run lint'
    assert not (tmp_path / 'f').exists()


def changelog(count: int) -> str:
    '''A changelog of 2.1.900 and the `count` releases after it, newest
    first, one day apart, each with one bullet that hits no section's terms.'''
    days = [date(2026, 9, 1) + timedelta(days=n) for n in range(count + 1)]
    return '\n'.join(f'<Update label="2.1.{900 + n}" description="{d:%B} {d.day}, {d.year}">\n  * Fixed item {n}\n'
                     '</Update>\n' for n, d in reversed(list(enumerate(days))))


def test_a_range_takes_twenty_releases_and_the_twenty_first_needs_through(world, tmp_path):
    '''m5 (final review): RANGE is 20, and a range of exactly 20 needs no
    --through.'''
    latest(world, {'changelog.md': changelog(20)})
    i = index(packets.triage(load(world), tmp_path / 'a', None))
    assert (len(i['releases']), i['newest'], i['next_through']) == (20, '2.1.920', None)
    latest(world, {'changelog.md': changelog(21)})
    with pytest.raises(state.SetupError) as err:
        packets.triage(load(world), tmp_path / 'b', None)
    assert str(err.value) == ('21 untriaged releases after 2.1.900: take them in ranges of 20, the first with '
                              '--through 2.1.920, or all at once with --through 2.1.921')
    assert index(packets.triage(load(world), tmp_path / 'c', '2.1.920'))['next_through'] == '2.1.921'


def test_each_range_names_the_next_ranges_through(world, tmp_path):
    '''m5 (final review): once a range's commands advance its sections, the
    next triage counts from there, and each range names the next one's end.'''
    repo, _ = world
    latest(world, {'changelog.md': changelog(5)})
    with pytest.raises(state.SetupError) as err:
        packets.triage(load(world), tmp_path / 'a', None, size=2)
    assert str(err.value) == ('5 untriaged releases after 2.1.900: take them in ranges of 2, the first with '
                              '--through 2.1.902, or all at once with --through 2.1.905')
    assert index(packets.triage(load(world), tmp_path / 'b', '2.1.902', size=2))['next_through'] == '2.1.904'
    s = state.parse_baseline((repo / state.BASELINE).read_text())
    for section in s['sections'].values():
        section['checked'] = {'release': '2.1.902', 'date': '2026-10-04'}
    (repo / state.BASELINE).write_text(state.dump_baseline(s))
    with pytest.raises(state.SetupError) as err:
        packets.triage(load(world), tmp_path / 'c', None, size=2)
    assert str(err.value) == ('3 untriaged releases after 2.1.902: take them in ranges of 2, the first with '
                              '--through 2.1.904, or all at once with --through 2.1.905')
    i = index(packets.triage(load(world), tmp_path / 'd', '2.1.904', size=2))
    assert ([r['label'] for r in i['releases']], i['next_through']) == (['2.1.903', '2.1.904'], '2.1.905')
