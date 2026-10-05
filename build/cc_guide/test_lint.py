'''Tests for lint.py: every R5 rule but the citation rules (Stage 2's).'''
import pytest

import baseline
import docs
import guide
import lint
import state
from cc_fixtures import (CHANGELOG_TEXT, FENCE, GUIDE_IDS, MANIFEST_TOML, docs_dir,  # noqa: F401
                         fixture_state, guide_text, isolated_home)

MANIFEST = state.parse_manifest(MANIFEST_TOML)
LABELS = {r.label for r in docs.parse_changelog(CHANGELOG_TEXT)}
CLI = 'uv run --python 3.13 python build/cc_guide/cli.py'


def run(text, s, labels=LABELS, manifest=MANIFEST):
    return lint.lint(text, manifest, s, labels)


def synced(text, s):
    '''The state with every text_hash re-accepted for text, so a test sees
    only the rule it breaks.'''
    return baseline.accept(s, text, GUIDE_IDS, False, '2.1.902')


def test_the_fixture_inputs_lint_clean(docs_dir):
    assert run(guide_text(), fixture_state(docs_dir)) == ([], [])


def test_without_a_changelog_the_label_check_is_skipped_with_a_note(docs_dir):
    assert run(guide_text(), fixture_state(docs_dir), None) == (
        [], ['release-label check skipped: no changelog to read'])


def test_the_three_id_sets_must_agree(docs_dir):
    s = fixture_state(docs_dir)
    del s['sections']['beta.reference']
    manifest = state.parse_manifest(MANIFEST_TOML.replace("'beta.reference']", "'beta.reference', 'beta.extra']"))
    violations, _ = run(guide_text(), s, manifest=manifest)
    assert violations == ['section beta.extra: missing from the guide and baseline.json',
                          'section beta.reference: missing from baseline.json']


def test_a_text_change_names_both_accept_commands(docs_dir):
    violations, _ = run(guide_text().replace('Alpha uses', 'Alpha now uses'), fixture_state(docs_dir))
    assert violations == [
        f'section alpha.overview: text differs from its text_hash; record it with '
        f'`{CLI} baseline accept alpha.overview --substantive` (flags its citers) or `... --editorial`']


def test_a_rewrap_is_not_a_text_change(docs_dir):
    text = guide_text().replace('Alpha uses `ALPHA_TOOL`, `if`', 'Alpha uses `ALPHA_TOOL`,\n`if`')
    assert run(text, fixture_state(docs_dir)) == ([], [])


def test_a_stale_stamp_names_the_stamp_command(docs_dir):
    s = baseline.advance(fixture_state(docs_dir), GUIDE_IDS, '2.1.902', {'2.1.902'}, '2026-10-04')
    violations, _ = run(guide_text(), s)
    assert violations == [f'guide: the stamp region does not match baseline.json; run `{CLI} baseline stamp`']


def test_the_stamp_region_must_exist_and_precede_the_first_section(docs_dir):
    s = fixture_state(docs_dir)
    missing = guide_text().replace(guide.STAMP_CLOSE + '\n', '')
    assert run(missing, s)[0] == [
        f'guide: needs one stamp region, a {guide.STAMP_OPEN} line then a {guide.STAMP_CLOSE} line']
    region = '\n'.join([guide.STAMP_OPEN, guide.render_stamp(s['sections']), guide.STAMP_CLOSE, ''])
    late = guide_text().replace(region, '') + region
    assert run(late, synced(late, s))[0] == ['guide: the stamp region must sit before the first section']


@pytest.mark.parametrize('prose, flagged', [
    ('Fixed in 2.1.950.', ['2.1.950']),
    ('Since 2.1.901, and 2.1.902.', []),
    ('Not 12.1.900 or 2.1.9001x.', ['2.1.9001']),
    ('A stamp 2.1.902.1 is no label.', ['2.1.902.1']),
])
def test_every_2_1_version_must_be_a_release_label(docs_dir, prose, flagged):
    text = guide_text() + prose + '\n'
    line = len(text.split('\n')) - 1
    assert run(text, synced(text, fixture_state(docs_dir)))[0] == [
        f'guide line {line}: {v} is not a changelog release label' for v in flagged]


def test_every_table_row_keeps_its_headers_cell_count(docs_dir):
    text = guide_text().replace('| `BETA_ENV` | on |', '| `BETA_ENV` | on | extra |\n| `a\\|b` | on |')
    line = text.split('\n').index('| `BETA_ENV` | on | extra |') + 1
    assert run(text, synced(text, fixture_state(docs_dir)))[0] == [
        f'guide line {line}: table row has 3 cells; its header has 2']


def test_every_json_block_must_parse(docs_dir):
    text = guide_text().replace('{"beta": true}', '{"beta": true,}')
    line = text.split('\n').index(FENCE + 'json') + 1
    assert run(text, synced(text, fixture_state(docs_dir)))[0] == [
        f'guide line {line}: json block does not parse (Illegal trailing comma before end of object)']


def test_an_anchor_problem_fails_the_lint(docs_dir):
    text = guide_text().replace('<!-- cc: beta.reference -->\n', '')
    heading = '### Reference ⚠'
    lines = text.split('\n')
    line = lines.index(heading, lines.index(heading) + 1) + 1  # beta's, the second
    violations, _ = run(text, fixture_state(docs_dir))
    assert violations == [f"guide line {line}: heading '{heading}' has no anchor on its next line",
                          'section beta.reference: missing from the guide']
