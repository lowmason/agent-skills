'''Tests for baseline.py: R2.4's stamp rule, R11.1's derivation, and each
`baseline` subcommand's effect on the state (drift spec R7). The write sets
on disk are test_cli.py's.'''
import subprocess
from pathlib import Path

import pytest

import baseline
import guide
import state
from cc_fixtures import (DOCS, FIXTURE_CHANGED, GUIDE_IDS, MANIFEST_TOML, docs_dir,  # noqa: F401
                         fixture_state, guide_text, isolated_home, write_tree)

REPO = Path(__file__).resolve().parents[2]
MANIFEST = state.parse_manifest(MANIFEST_TOML)
ENV = 'Environment variables'


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
    with pytest.raises(state.SetupError, match='beta.reference'):
        baseline.derive_changed(unanchored(guide_text()), unanchored(guide_text()), current)


def history(ref):
    proc = subprocess.run(['git', 'show', f'{ref}:{baseline.OLD_GUIDE_PATH}'], cwd=REPO,
                          capture_output=True, encoding='utf-8')
    if proc.returncode != 0:
        pytest.skip(f'{ref} is not in this clone (a shallow clone?)')
    return proc.stdout


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
        'tools': ['Tools', 'Tools › Options', 'Tools › Options › `--fast`'],
        'env-vars': [f'{ENV} › `ALPHA_ENV`', f'{ENV} › `ALPHA_ENV`#2', f'{ENV} › Examples']}
    assert {p: list(keys) for p, keys in s['groups']['beta']['blocks'].items()} == {
        'events': ['Events', 'Events › Payload'],
        'env-vars': [f'{ENV} › `BETA_ENV`'],
        'platform:pricing': ['(intro)', 'Rates']}
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
    with pytest.raises(state.SetupError, match='beta.reference is in manifest.toml but not the guide'):
        baseline.init(MANIFEST, text, docs_dir, '2.1.900', '2026-09-02', FIXTURE_CHANGED)


def test_accept_records_the_hash_and_substantive_also_sets_changed(docs_dir):
    s = fixture_state(docs_dir)
    edited = guide_text().replace('Alpha uses', 'Alpha now uses')
    editorial = baseline.accept(s, edited, ['alpha.overview'], False, '2.1.902')
    by_id = {x.id: x for x in guide.sections(edited)}
    assert editorial['sections']['alpha.overview']['text_hash'] == guide.text_hash(by_id['alpha.overview'].text)
    assert editorial['sections']['alpha.overview']['changed'] == '2.1.900'
    substantive = baseline.accept(s, edited, ['alpha.overview'], True, '2.1.902')
    assert substantive['sections']['alpha.overview']['changed'] == '2.1.902'
    bumped = baseline.accept(s, edited, ['alpha.overview'], True, '2.1.902', {'alpha.overview': ['2.1.902']})
    assert bumped['sections']['alpha.overview']['changed'] == '2.1.902.1'
    assert s == fixture_state(docs_dir)


def test_advance_sets_checked_on_the_day_of_the_check(docs_dir):
    s = fixture_state(docs_dir)
    labels = {'2.1.900', '2.1.901', '2.1.902'}
    moved = baseline.advance(s, ['beta.overview'], '2.1.902', labels, '2026-10-04')
    assert moved['sections']['beta.overview']['checked'] == {'release': '2.1.902', 'date': '2026-10-04'}
    assert moved['sections']['beta.reference'] == s['sections']['beta.reference']
    with pytest.raises(state.SetupError, match='not a release'):
        baseline.advance(s, ['beta.overview'], '2.1.950', labels, '2026-10-04')
    with pytest.raises(state.SetupError, match='older than the checked release of beta.overview'):
        baseline.advance(moved, ['beta.overview'], '2.1.901', labels, '2026-10-05')
    with pytest.raises(state.SetupError, match='unknown section IDs: beta.zzz'):
        baseline.advance(s, ['beta.zzz'], '2.1.902', labels, '2026-10-04')


def test_audited_sets_audited_and_checked_for_the_groups_sections(docs_dir):
    s = fixture_state(docs_dir)
    done = baseline.audited(s, MANIFEST, 'alpha', '2.1.902', '2026-10-04')
    for sid in ('alpha.overview', 'alpha.reference'):
        assert done['sections'][sid]['audited'] == {'release': '2.1.902', 'date': '2026-10-04'}
        assert done['sections'][sid]['checked'] == {'release': '2.1.902', 'date': '2026-10-04'}
    assert done['sections']['beta.overview'] == s['sections']['beta.overview']
    with pytest.raises(state.SetupError, match='unknown group gamma'):
        baseline.audited(s, MANIFEST, 'gamma', '2.1.902', '2026-10-04')


def latest_from(tmp_path, **edits):
    folder = tmp_path / 'latest'
    write_tree(folder, {**DOCS, **edits})
    return folder


def test_a_full_rebaseline_rehashes_drops_deselected_and_refreshes_llms(tmp_path, docs_dir):
    s = fixture_state(docs_dir)
    s['groups']['alpha']['blocks']['env-vars']['Environment variables'] = '0' * 16
    latest = latest_from(tmp_path, **{
        'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches'),
        'llms.txt': DOCS['llms.txt'] + '- [New](https://code.claude.com/docs/en/new-page.md): New.\n'})
    new, pages, notes = baseline.rebaseline(s, MANIFEST, guide_text(), 'alpha', [], latest, '2.1.902')
    fresh = fixture_state(latest)
    assert new['groups']['alpha']['blocks'] == fresh['groups']['alpha']['blocks']
    assert new['groups']['alpha']['blocks']['tools']['Tools'] != s['groups']['alpha']['blocks']['tools']['Tools']
    assert new['groups']['alpha']['snapshot'] == {'tools': '2.1.902', 'env-vars': '2.1.902'}
    assert new['groups']['beta'] == s['groups']['beta']
    assert (pages, notes) == (['tools', 'env-vars'], [])
    assert new['llms'] == ['env-vars', 'events', 'new-page', 'plugins/components', 'tools']


def test_a_listed_rebaseline_touches_only_the_listed_blocks(tmp_path, docs_dir):
    s = fixture_state(docs_dir)
    latest = latest_from(tmp_path, **{'tools.md': DOCS['tools.md'].replace('Runs fast.', 'Runs faster.')
                                      .replace('runs alpha jobs', 'runs alpha batches')})
    row = 'Tools › Options › `--fast`'
    new, pages, _ = baseline.rebaseline(s, MANIFEST, guide_text(), 'alpha', ['tools › ' + row], latest, '2.1.902')
    old_tools, new_tools = s['groups']['alpha']['blocks']['tools'], new['groups']['alpha']['blocks']['tools']
    assert new_tools[row] != old_tools[row]
    assert new_tools['Tools'] == old_tools['Tools']
    assert list(new_tools) == list(old_tools)
    assert pages == ['tools']


def test_rebaseline_keeps_a_missing_page_and_drops_an_unmapped_one(tmp_path, docs_dir):
    s = fixture_state(docs_dir)
    s['groups']['beta']['blocks']['retired'] = {'Retired': '1' * 16}
    latest = latest_from(tmp_path)
    (latest / 'events.md').unlink()
    new, pages, notes = baseline.rebaseline(s, MANIFEST, guide_text(), 'beta', [], latest, '2.1.902')
    assert new['groups']['beta']['blocks']['events'] == s['groups']['beta']['blocks']['events']
    assert 'retired' not in new['groups']['beta']['blocks']
    assert pages == ['env-vars', 'platform:pricing']
    assert notes == ['events: missing page; kept its entries. Drop or remap it in manifest.toml first',
                     'retired: no longer mapped to beta; dropped its baselined blocks']


def test_stamp_regenerates_only_the_region(docs_dir):
    s = baseline.advance(fixture_state(docs_dir), GUIDE_IDS, '2.1.902', {'2.1.902'}, '2026-10-04')
    stamped = baseline.stamp(guide_text(), s)
    assert guide.stamp_content(stamped) == guide.render_stamp(s['sections'])
    assert stamped == guide_text(guide.render_stamp(s['sections']))
