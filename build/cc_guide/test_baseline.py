'''Tests for baseline.py: R2.4's stamp rule, R11.1's derivation, and each
`baseline` subcommand's effect on the state (drift spec R7). The write sets
on disk are test_cli.py's.'''
import subprocess
from pathlib import Path

import pytest

import baseline
import blocks
import guide
import state
from cc_fixtures import (DOCS, FIXTURE_CHANGED, GUIDE_IDS, MANIFEST_TOML, docs_dir,  # noqa: F401
                         fixture_snapshot, fixture_state, guide_text, isolated_home, write_tree)

REPO = Path(__file__).resolve().parents[2]
MANIFEST = state.parse_manifest(MANIFEST_TOML)
ENV = 'Environment variables'


def hashed(*keys):
    '''Block keys as baseline.json stores them (R2.3).'''
    return [blocks.key_hash(k) for k in keys]


def unanchored(text):
    return '\n'.join(line for line in text.split('\n') if not line.startswith('<!-- cc: '))


@pytest.mark.parametrize('newest, citers, expected', [
    ('2.1.300', [], '2.1.300'),
    ('2.1.300', ['2.1.299'], '2.1.300'),
    ('2.1.300', ['2.1.300'], '2.1.300.1'),
    ('2.1.300', ['2.1.299', '2.1.300.1'], '2.1.300.2'),
    ('2.1.300', ['2.1.301'], '2.1.301.1'),
])
def test_a_new_changed_exceeds_every_citer_stamp(newest, citers, expected):
    assert baseline.next_changed(newest, citers) == expected


def test_derive_changed_aligns_by_parent_and_heading():
    refresh = unanchored(guide_text())
    july = refresh.replace('Set `ALPHA_ENV`;', 'Set `OLD_ENV`;')
    assert july != refresh
    assert baseline.derive_changed(july, refresh, guide_text()) == {
        'alpha.overview': '2.1.219', 'alpha.reference': '2.1.288',
        'beta.overview': '2.1.219', 'beta.reference': '2.1.219'}


def test_derive_changed_refuses_a_section_the_refresh_lacks():
    current = guide_text().replace('### Reference ⚠\n<!-- cc: beta.reference', '### Renamed\n<!-- cc: beta.reference')
    with pytest.raises(state.SetupError) as err:
        baseline.derive_changed(unanchored(guide_text()), unanchored(guide_text()), current)
    assert str(err.value) == "R11.1: section beta.reference ('### Renamed') is not in the c33bc99 guide"


def history(ref):
    '''The guide at ref, read where it lived before 79ad04f moved it. A clone
    without ref (a shallow one) skips; any other git failure fails.'''
    present = subprocess.run(['git', 'cat-file', '-e', f'{ref}^{{commit}}'], cwd=REPO, capture_output=True)
    if present.returncode != 0:
        pytest.skip(f'{ref} is not in this clone (a shallow clone?)')
    proc = subprocess.run(['git', 'show', f'{ref}:{baseline.OLD_GUIDE_PATH}'], cwd=REPO,
                          capture_output=True, encoding='utf-8')
    if proc.returncode != 0:
        pytest.fail(f'git show {ref}:{baseline.OLD_GUIDE_PATH} failed: {proc.stderr.strip()}')
    return proc.stdout


def test_history_skips_only_for_a_commit_this_clone_lacks(monkeypatch):
    '''A missing path at a present commit fails rather than hiding as a skip.'''
    with pytest.raises(pytest.skip.Exception):
        history('0' * 40)
    monkeypatch.setattr(baseline, 'OLD_GUIDE_PATH', 'no/such/guide.md')
    with pytest.raises((pytest.skip.Exception, pytest.fail.Exception)) as err:
        history('HEAD')
    assert err.type is pytest.fail.Exception
    assert 'no/such/guide.md' in str(err.value)


def test_r11_derivation_from_the_real_history():
    changed = baseline.derive_changed(history(baseline.JULY[0]), history(baseline.REFRESH[0]),
                                      (REPO / 'specs/guides/claude-code-customization-guide.md').read_text())
    assert sorted(sid for sid, release in changed.items() if release == '2.1.219') == [
        'lean.ceremony', 'lean.overview', 'rules.auto-memory', 'rules.overview',
        'skills.description', 'skills.overview']
    assert sum(1 for release in changed.values() if release == '2.1.288') == 32


def test_init_baselines_each_groups_selected_blocks(docs_dir):
    s = fixture_state(docs_dir)
    assert list(s['sections']) == GUIDE_IDS
    assert s['sections']['alpha.reference']['changed'] == '2.1.899'
    assert s['sections']['alpha.overview']['checked'] == {'release': '2.1.900', 'date': '2026-09-02'}
    assert {p: list(keys) for p, keys in s['groups']['alpha']['blocks'].items()} == {
        'tools': hashed('Tools', 'Tools › Options', 'Tools › Options › `--fast`'),
        'env-vars': hashed(f'{ENV} › `ALPHA_ENV`', f'{ENV} › `ALPHA_ENV`#2', f'{ENV} › Examples')}
    assert {p: list(keys) for p, keys in s['groups']['beta']['blocks'].items()} == {
        'events': hashed('Events', 'Events › Payload'),
        'env-vars': hashed(f'{ENV} › `BETA_ENV`'),
        'platform:pricing': hashed('(intro)', 'Rates')}
    assert s['groups']['beta']['snapshot'] == {'events': '2.1.900', 'env-vars': '2.1.900',
                                               'platform:pricing': '2.1.900'}
    assert s['llms'] == ['env-vars', 'events', 'plugins/components', 'tools']


def test_init_leaves_a_page_the_snapshot_lacks_unbaselined(docs_dir):
    (docs_dir / 'events.md').unlink()
    s = fixture_state(docs_dir)
    assert 'events' not in s['groups']['beta']['blocks']
    assert 'events' not in s['groups']['beta']['snapshot']


def test_init_refuses_anchors_that_disagree_with_the_manifest(docs_dir):
    text = guide_text().replace('<!-- cc: beta.reference -->', '<!-- cc: beta.other -->')
    with pytest.raises(state.SetupError) as err:
        baseline.init(MANIFEST, text, docs_dir, '2.1.900', '2026-09-02', FIXTURE_CHANGED)
    assert str(err.value) == ('section beta.reference is in manifest.toml but not the guide\n'
                              'section beta.other is in the guide but not manifest.toml')


def test_accept_records_the_hash_and_substantive_also_sets_changed(docs_dir):
    s = fixture_state(docs_dir)
    edited = guide_text().replace('Alpha uses', 'Alpha now uses')
    editorial = baseline.accept(s, edited, ['alpha.overview'], False, '2.1.902')
    by_id = {x.id: x for x in guide.sections(edited)}
    assert editorial['sections']['alpha.overview']['text_hash'] == guide.text_hash(by_id['alpha.overview'].text)
    assert editorial['sections']['alpha.overview']['changed'] == '2.1.900'
    substantive = baseline.accept(s, edited, ['alpha.overview'], True, '2.1.902')
    assert substantive['sections']['alpha.overview']['changed'] == '2.1.902'
    assert (substantive['sections']['alpha.overview']['text_hash']
            == editorial['sections']['alpha.overview']['text_hash'])
    bumped = baseline.accept(s, edited, ['alpha.overview'], True, '2.1.902', {'alpha.overview': ['2.1.902']})
    assert bumped['sections']['alpha.overview']['changed'] == '2.1.902.1'
    assert s == fixture_state(docs_dir)


def test_known_names_a_repeated_unknown_id_once(docs_dir):
    with pytest.raises(state.SetupError) as err:
        baseline.known(fixture_state(docs_dir), ['beta.zzz', 'beta.zzz'])
    assert str(err.value) == 'unknown section IDs: beta.zzz'


def test_check_forward_names_a_repeated_id_once(docs_dir):
    s = baseline.advance(fixture_state(docs_dir), ['beta.overview'], '2.1.902', {'2.1.902'}, '2026-10-04')
    with pytest.raises(state.SetupError) as err:
        baseline.check_forward(s, ['beta.overview', 'beta.overview'], '2.1.901')
    assert str(err.value) == '2.1.901 is older than the checked release of beta.overview'


def test_accept_names_a_repeated_absent_id_once(docs_dir):
    without = guide_text().replace('<!-- cc: alpha.overview -->', '')
    with pytest.raises(state.SetupError) as err:
        baseline.accept(fixture_state(docs_dir), without, ['alpha.overview', 'alpha.overview'], False, None)
    assert str(err.value) == 'section IDs not in the guide: alpha.overview'


def test_advance_sets_checked_on_the_day_of_the_check(docs_dir):
    s = fixture_state(docs_dir)
    labels = {'2.1.900', '2.1.901', '2.1.902'}
    moved = baseline.advance(s, ['beta.overview'], '2.1.902', labels, '2026-10-04')
    assert moved['sections']['beta.overview']['checked'] == {'release': '2.1.902', 'date': '2026-10-04'}
    assert moved['sections']['beta.reference'] == s['sections']['beta.reference']
    with pytest.raises(state.SetupError) as err:
        baseline.advance(s, ['beta.overview'], '2.1.950', labels, '2026-10-04')
    assert str(err.value) == '2.1.950 is not a release in the newest cached changelog'
    with pytest.raises(state.SetupError) as err:
        baseline.advance(moved, ['beta.overview'], '2.1.901', labels, '2026-10-05')
    assert str(err.value) == '2.1.901 is older than the checked release of beta.overview'
    with pytest.raises(state.SetupError) as err:
        baseline.advance(s, ['beta.zzz'], '2.1.902', labels, '2026-10-04')
    assert str(err.value) == 'unknown section IDs: beta.zzz'


def test_audited_sets_audited_and_checked_for_the_groups_sections(docs_dir):
    s = fixture_state(docs_dir)
    done = baseline.audited(s, MANIFEST, 'alpha', '2.1.902', '2026-10-04')
    for sid in ('alpha.overview', 'alpha.reference'):
        assert done['sections'][sid]['audited'] == {'release': '2.1.902', 'date': '2026-10-04'}
        assert done['sections'][sid]['checked'] == {'release': '2.1.902', 'date': '2026-10-04'}
    assert done['sections']['beta.overview'] == s['sections']['beta.overview']
    with pytest.raises(state.SetupError) as err:
        baseline.audited(s, MANIFEST, 'gamma', '2.1.902', '2026-10-04')
    assert str(err.value) == 'unknown group gamma'


def test_audited_never_moves_checked_backwards(docs_dir):
    s = baseline.advance(fixture_state(docs_dir), ['alpha.reference'], '2.1.902', {'2.1.902'}, '2026-10-04')
    with pytest.raises(state.SetupError) as err:
        baseline.audited(s, MANIFEST, 'alpha', '2.1.901', '2026-10-05')
    assert str(err.value) == '2.1.901 is older than the checked release of alpha.reference'


def latest_from(tmp_path, **edits):
    folder = tmp_path / 'latest'
    write_tree(folder, {**DOCS, **edits})
    return folder


def test_a_full_rebaseline_rehashes_drops_deselected_and_refreshes_llms(tmp_path, docs_dir):
    s = fixture_state(docs_dir)
    s['groups']['alpha']['blocks']['env-vars'][blocks.key_hash(ENV)] = '0' * 16
    latest = latest_from(tmp_path, **{
        'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches'),
        'llms.txt': DOCS['llms.txt'] + '- [New](https://code.claude.com/docs/en/new-page.md): New.\n'})
    new, pages, notes = baseline.rebaseline(s, MANIFEST, guide_text(), 'alpha', [], latest, '2.1.902')
    fresh = fixture_state(latest)
    assert new['groups']['alpha']['blocks'] == fresh['groups']['alpha']['blocks']
    tools = blocks.key_hash('Tools')
    assert new['groups']['alpha']['blocks']['tools'][tools] != s['groups']['alpha']['blocks']['tools'][tools]
    assert new['groups']['alpha']['snapshot'] == {'tools': '2.1.902', 'env-vars': '2.1.902'}
    assert new['groups']['beta'] == s['groups']['beta']
    assert (pages, notes) == (['tools', 'env-vars'], [])
    assert new['llms'] == ['env-vars', 'events', 'new-page', 'plugins/components', 'tools']


def test_a_bare_page_ref_rebaselines_that_whole_page_and_refreshes_llms(tmp_path, docs_dir):
    '''A listed run may name a whole page, so its two changed blocks need no
    listing. Like every run it refreshes the llms.txt slugs; unlike a full
    run it keeps a page the group no longer maps.'''
    s = fixture_state(docs_dir)
    s['groups']['alpha']['blocks']['retired'] = {blocks.key_hash('Retired'): '1' * 16}
    tools = DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches').replace('Runs fast.', 'Runs faster.')
    latest = latest_from(tmp_path, **{
        'tools.md': tools,
        'llms.txt': DOCS['llms.txt'] + '- [New](https://code.claude.com/docs/en/new-page.md): New.\n'})
    new, pages, notes = baseline.rebaseline(s, MANIFEST, guide_text(), 'alpha', ['tools'], latest, '2.1.902')
    old, alpha = s['groups']['alpha'], new['groups']['alpha']
    assert alpha['blocks']['tools'] == fixture_state(latest)['groups']['alpha']['blocks']['tools']
    assert alpha['blocks']['tools'] != old['blocks']['tools']
    assert (alpha['blocks']['env-vars'], alpha['blocks']['retired']) == (old['blocks']['env-vars'],
                                                                          old['blocks']['retired'])
    assert alpha['snapshot'] == {'tools': '2.1.902', 'env-vars': '2.1.900'}
    assert (pages, notes) == (['tools'], [])
    assert new['llms'] == ['env-vars', 'events', 'new-page', 'plugins/components', 'tools']


@pytest.mark.parametrize('group, refs, fetched, message', [
    ('gamma', [], True, 'unknown group gamma'),
    ('alpha', ['nowhere'], True, 'nowhere is neither mapped to nor baselined in alpha'),
    ('alpha', [], False, '{llms}: no latest fetch; run check first'),
])
def test_rebaseline_refuses_an_unknown_group_or_page_and_a_missing_fetch(tmp_path, docs_dir, group, refs,
                                                                         fetched, message):
    latest = latest_from(tmp_path)
    if not fetched:
        (latest / 'llms.txt').unlink()
    with pytest.raises(state.SetupError) as err:
        baseline.rebaseline(fixture_state(docs_dir), MANIFEST, guide_text(), group, refs, latest, '2.1.902')
    assert str(err.value) == message.format(llms=latest / 'llms.txt')


def test_a_listed_rebaseline_touches_only_listed_blocks_and_refuses_other_changes(tmp_path, docs_dir):
    s = fixture_state(docs_dir)
    # `--slow` is a new selected row the run does not list, so it stays out.
    faster = DOCS['tools.md'].replace('Runs fast.', 'Runs faster.') + '| `--slow` | Runs slow. |\n'
    latest = latest_from(tmp_path, **{'tools.md': faster})
    row = 'Tools › Options › `--fast`'
    new, pages, _ = baseline.rebaseline(s, MANIFEST, guide_text(), 'alpha', ['tools › ' + row], latest, '2.1.902')
    old_tools, new_tools = s['groups']['alpha']['blocks']['tools'], new['groups']['alpha']['blocks']['tools']
    row_hash, tools = hashed(row, 'Tools')
    assert new_tools[row_hash] != old_tools[row_hash]
    assert new_tools[tools] == old_tools[tools]
    assert list(new_tools) == list(old_tools)
    assert pages == ['tools']
    assert new['groups']['alpha']['snapshot']['tools'] == '2.1.902'
    # An unlisted baselined block that also changed would leave the snapshot
    # pointer naming text that is not baselined (R2.3), so the run refuses.
    latest = latest_from(tmp_path, **{'tools.md': faster.replace('runs alpha jobs', 'runs alpha batches')})
    with pytest.raises(state.SetupError) as err:
        baseline.rebaseline(s, MANIFEST, guide_text(), 'alpha', ['tools › ' + row], latest, '2.1.902')
    assert str(err.value) == ('tools: also changed or gone since the baseline: tools › Tools;'
                              ' list them too, or rebaseline the whole page')


def test_an_empty_key_ref_rebaselines_that_block_not_its_page(tmp_path, docs_dir):
    '''Check prints a block keyed '' (a bare `#` heading) as `page + SEP`; that
    ref names the block, so the refusal for other changed blocks still runs.'''
    s = fixture_state(docs_dir)
    row = 'Tools › Options › `--fast`'
    faster = DOCS['tools.md'].replace('Runs fast.', 'Runs faster.') + '\n#\n\nBare.\n'
    latest = latest_from(tmp_path, **{'tools.md': faster})
    bare = 'tools' + baseline.SEP
    with pytest.raises(state.SetupError) as err:
        baseline.rebaseline(s, MANIFEST, guide_text(), 'alpha', [bare], latest, '2.1.902')
    assert str(err.value) == ('tools: also changed or gone since the baseline: tools › ' + row + ';'
                              ' list them too, or rebaseline the whole page')
    new, pages, _ = baseline.rebaseline(s, MANIFEST, guide_text(), 'alpha', [bare, 'tools › ' + row], latest,
                                        '2.1.902')
    assert pages == ['tools']
    assert blocks.key_hash('') in new['groups']['alpha']['blocks']['tools']


def test_a_listed_rebaseline_takes_checks_refs_for_blocks_gone_from_the_page(tmp_path, docs_dir):
    '''A block gone from the page is listed as check names it: by the key
    read back from its snapshot, or by its key hash when there is none. The
    refusal names an unlisted gone block the same way.'''
    s = fixture_state(docs_dir)
    latest = latest_from(tmp_path, **{'tools.md': DOCS['tools.md'].replace('## Options', '## Flags')})
    options, row = 'Tools › Options', 'Tools › Options › `--fast`'
    for snapshot, name in ((fixture_snapshot, options), (state.no_snapshot, blocks.key_hash(options))):
        with pytest.raises(state.SetupError) as err:
            baseline.rebaseline(s, MANIFEST, guide_text(), 'alpha', ['tools › ' + row], latest, '2.1.902',
                                snapshot=snapshot)
        assert str(err.value) == (f'tools: also changed or gone since the baseline: tools › {name};'
                                  ' list them too, or rebaseline the whole page')
    refs = ['tools › ' + row, 'tools › ' + blocks.key_hash(options)]
    new, pages, _ = baseline.rebaseline(s, MANIFEST, guide_text(), 'alpha', refs, latest, '2.1.902')
    assert list(new['groups']['alpha']['blocks']['tools']) == hashed('Tools')
    assert pages == ['tools']


def test_rebaseline_keeps_a_missing_page_and_drops_an_unmapped_one(tmp_path, docs_dir):
    s = fixture_state(docs_dir)
    s['groups']['beta']['blocks']['retired'] = {blocks.key_hash('Retired'): '1' * 16}
    latest = latest_from(tmp_path)
    (latest / 'events.md').unlink()
    new, pages, notes = baseline.rebaseline(s, MANIFEST, guide_text(), 'beta', [], latest, '2.1.902')
    assert new['groups']['beta']['blocks']['events'] == s['groups']['beta']['blocks']['events']
    assert 'retired' not in new['groups']['beta']['blocks']
    assert pages == ['env-vars', 'platform:pricing']
    assert notes == ['events: missing page; kept its entries. Drop or remap it in manifest.toml first',
                     'retired: no longer mapped to beta; dropped its baselined blocks']


def test_a_listed_ref_to_an_unmapped_page_drops_the_page_or_only_its_listed_blocks(tmp_path, docs_dir):
    s = fixture_state(docs_dir)
    retired, kept = hashed('Retired', 'Retired › Kept')
    s['groups']['beta']['blocks']['retired'] = {retired: '1' * 16, kept: '2' * 16}
    s['groups']['beta']['snapshot']['retired'] = '2.1.900'
    latest = latest_from(tmp_path)
    new, pages, notes = baseline.rebaseline(s, MANIFEST, guide_text(), 'beta', ['retired › Retired'], latest,
                                            '2.1.902')
    assert new['groups']['beta']['blocks']['retired'] == {kept: '2' * 16}
    assert new['groups']['beta']['snapshot']['retired'] == '2.1.900'
    assert (pages, notes) == ([], ['retired: no longer mapped to beta; dropped the listed blocks'])
    new, pages, notes = baseline.rebaseline(s, MANIFEST, guide_text(), 'beta', ['retired'], latest, '2.1.902')
    assert ('retired' in new['groups']['beta']['blocks'], 'retired' in new['groups']['beta']['snapshot']) == (
        False, False)
    assert (pages, notes) == ([], ['retired: no longer mapped to beta; dropped its baselined blocks'])


def test_stamp_regenerates_only_the_region(docs_dir):
    s = baseline.advance(fixture_state(docs_dir), GUIDE_IDS, '2.1.902', {'2.1.902'}, '2026-10-04')
    stamped = baseline.stamp(guide_text(), s)
    assert guide.stamp_content(stamped) == guide.render_stamp(s['sections'])
    assert stamped == guide_text(guide.render_stamp(s['sections']))
