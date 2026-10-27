'''Tests for lint.py: every R5 rule, the citation rules included, and STALE.'''
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
CLI = 'uv run python build/cc_guide/cli.py'


def run(text, s, labels=LABELS, manifest=MANIFEST, files=None):
    return lint.lint(text, manifest, s, labels, files or {})


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
        f'`{CLI} baseline accept alpha.overview --substantive` (flags its citers) or '
        f'`{CLI} baseline accept alpha.overview --editorial`']


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


@pytest.mark.parametrize('prose, flagged, noted', [
    ('Fixed in 2.1.899.', ['2.1.899'], []),
    ('Since 2.1.901, and 2.1.902.', [], []),
    # A fourth part is the baseline's own counter (R2.4): the shape it writes into stamps, never a
    # release. Such a token, and any longer one, is a violation whatever the changelog's head, 2.1.902.
    ('A stamp 2.1.901.1 is no label.', ['2.1.901.1'], []),
    ('A stamp 2.1.902.1 is no label.', ['2.1.902.1'], []),
    ('Five parts, 2.1.950.1.1, are no label either.', ['2.1.950.1.1'], []),
    # A three-part label newer than the changelog's newest release: a note, not a violation.
    ('Fixed in 2.1.950.', [], ['2.1.950']),
    ('Not 12.1.900 or 2.1.9001x.', [], ['2.1.9001']),
    ('Fixed in 2.1.899, shipped in 2.1.950.', ['2.1.899'], ['2.1.950']),
])
def test_an_unlisted_label_is_a_violation_unless_it_is_a_newer_three_part_release(docs_dir, prose, flagged, noted):
    '''R5: a 2.1.NNN the changelog lacks is a violation, unless it is a
    three-part label newer than the changelog's newest release. An older
    changelog cannot say whether that release exists, so the label is a note
    (owner, plan 43 final review, 2026-10-12).'''
    text = guide_text() + prose + '\n'
    line = len(text.split('\n')) - 1
    assert run(text, synced(text, fixture_state(docs_dir))) == (
        [f'guide line {line}: {v} is not a changelog release label' for v in flagged],
        [f"guide line {line}: {v} is newer than the changelog's newest release 2.1.902; not checked"
         for v in noted])


def test_the_newest_release_is_compared_by_version_not_as_text():
    '''2.1.100 is newer than 2.1.99, though it sorts before it as text.'''
    lines = ['Since 2.1.100, not 2.1.98, and 2.1.101.']
    labels = {'2.1.99', '2.1.100'}
    assert lint.label_problems(lines, labels) == ['guide line 1: 2.1.98 is not a changelog release label']
    assert lint.label_notes(lines, labels) == [
        "guide line 1: 2.1.101 is newer than the changelog's newest release 2.1.100; not checked"]


def test_every_table_row_keeps_its_headers_cell_count(docs_dir):
    text = guide_text().replace('| `BETA_ENV` | on |', '| `BETA_ENV` | on | extra |\n| `a\\|b` | on |')
    line = text.split('\n').index('| `BETA_ENV` | on | extra |') + 1
    assert run(text, synced(text, fixture_state(docs_dir)))[0] == [
        f'guide line {line}: table row has 3 cells; its header has 2']


def test_pipe_lines_without_a_separator_row_or_inside_a_fence_are_no_table(docs_dir):
    '''A table starts at a | line followed by a separator row (plan 38,
    decision 12), and fenced lines are code.'''
    text = guide_text() + f'| a | b |\n| c |\n\n{FENCE}\n| a | b |\n|---|---|\n| c |\n{FENCE}\n'
    assert run(text, synced(text, fixture_state(docs_dir)))[0] == []


def test_a_row_ending_in_an_escaped_pipe_counts_its_cells():
    assert lint.cell_count('| x | y\\|') == 2
    assert lint.cell_count('| x | y\\| |') == 2


def test_an_unclosed_json_block_runs_to_the_end(docs_dir):
    text = guide_text() + f'{FENCE}json\n{{"a": 1,}}\n'
    line = len(text.split('\n')) - 2
    assert run(text, synced(text, fixture_state(docs_dir)))[0] == [
        f'guide line {line}: json block does not parse (Illegal trailing comma before end of object)']


def test_a_section_missing_from_the_manifest_alone_is_named(docs_dir):
    manifest = state.parse_manifest(MANIFEST_TOML.replace("'beta.overview', 'beta.reference'", "'beta.overview'"))
    violations, _ = run(guide_text(), fixture_state(docs_dir), manifest=manifest)
    assert violations == ['section beta.reference: missing from manifest.toml']


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


def test_citation_problems_fail_the_lint_after_the_guide_checks(docs_dir):
    '''R5: every citation parses, cites guide sections, sits where R4.1 puts
    it and appears once per file; each file's problems come together, files
    in path order.'''
    files = {'hooks/b.sh': '#!/bin/sh\nexit 0\n# cc-guide: alpha.overview @2.1.900\n',
             'agents/a.md': '---\nname: a\n# cc-guide: alpha.overview gamma.overview @2.1.900\n---\n'}
    assert run(guide_text(), fixture_state(docs_dir), files=files)[0] == [
        'agents/a.md:3: cites gamma.overview, which is not a guide section',
        'hooks/b.sh:3: a citation goes on a line before the first line of code (R4.1)']


def test_well_placed_citations_lint_clean_and_stale_ones_are_reported_apart(docs_dir):
    '''R5: a stamp below a cited section's `changed` is STALE, which is no
    violation. Stamps compare as versions, so 2.1.900.1 is not stale against
    2.1.900.'''
    s = fixture_state(docs_dir)
    files = {'hooks/old.sh': '# cc-guide: alpha.overview alpha.reference beta.overview @2.1.899\n',
             'hooks/new.sh': '# cc-guide: alpha.overview @2.1.900.1\n',
             'CLAUDE.md': '<!-- cc-guide: beta.reference @2.1.900 -->\n# Notes\n'}
    assert run(guide_text(), s, files=files) == ([], [])
    citations, _ = guide.read_citations(files)
    assert lint.stale_lines(citations, s) == ['STALE hooks/old.sh alpha.overview beta.overview']
    assert lint.stale_by_section(citations, s) == {'alpha.overview': ['hooks/old.sh'],
                                                   'beta.overview': ['hooks/old.sh']}


def test_a_citation_of_a_section_the_baseline_lacks_is_never_stale(docs_dir):
    s = fixture_state(docs_dir)
    del s['sections']['beta.reference']
    citations, _ = guide.read_citations({'hooks/a.sh': '# cc-guide: beta.reference @2.1.800\n'})
    assert lint.stale_citations(citations, s) == []
