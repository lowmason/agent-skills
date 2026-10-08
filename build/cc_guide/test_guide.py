'''Tests for guide.py: sections and anchors, text hashes, terms and the
stamp region (drift spec R1, R2.3, R3.6). Two tests read the real guide.'''
from pathlib import Path

import pytest

import guide
from cc_fixtures import FENCE, FIXTURE_STAMP, GUIDE_IDS, guide_text, isolated_home  # noqa: F401

REPO = Path(__file__).resolve().parents[2]
REAL_GUIDE = REPO / 'specs/guides/claude-code-customization-guide.md'


def by_id(text):
    return {s.id: s for s in guide.sections(text)}


def test_sections_are_the_unfenced_level_two_and_three_headings():
    found = guide.sections(guide_text())
    assert [s.id for s in found] == GUIDE_IDS
    assert [s.parent for s in found] == [None, '## 1. Alpha', None, '## 2. Beta']


def test_a_level_two_section_runs_to_its_first_subsection_without_its_anchor():
    assert by_id(guide_text())['alpha.overview'].text == (
        '## 1. Alpha\n\nAlpha uses `ALPHA_TOOL`, `if` and `true`.\n')


def test_a_fenced_hash_line_stays_inside_its_section():
    reference = by_id(guide_text())['alpha.reference']
    assert '## not a heading inside a fence' in reference.text
    assert '## not a heading inside a fence' not in reference.prose


def test_anchor_problems_name_missing_malformed_repeated_and_stray_anchors():
    text = '\n'.join(['## A', '<!-- cc: a.one -->', '### B', 'body', '### C',
                      '<!-- cc: Bad_ID -->', '### D', '<!-- cc: a.one -->', '',
                      '<!-- cc: a.two -->'])
    assert guide.anchor_problems(text) == [
        "guide line 3: heading '### B' has no anchor on its next line",
        "guide line 6: malformed anchor '<!-- cc: Bad_ID -->'",
        'guide line 8: anchor a.one repeats line 2',
        'guide line 10: anchor is not directly under a heading',
    ]


def test_a_repeated_anchor_ids_only_its_first_heading():
    '''Every reader keys sections by ID, so a repeat must not merge two
    sections into one entry (owner ruling, plan 39).'''
    text = '\n'.join(['## A', '<!-- cc: a.one -->', 'Alpha.', '## B', '<!-- cc: a.one -->', 'Beta.'])
    found = guide.sections(text)
    assert [(s.heading, s.id) for s in found] == [('## A', 'a.one'), ('## B', None)]
    assert found[1].text == '## B\nBeta.'


def test_scan_returns_the_sections_and_each_problems_line_and_id():
    text = '\n'.join(['## A', '<!-- cc: a.one -->', '### B', 'body', '### C',
                      '<!-- cc: Bad_ID -->', '### D', '<!-- cc: a.one -->', '',
                      '<!-- cc: a.two -->'])
    found, problems = guide.scan(text)
    assert [s.id for s in found] == ['a.one', None, None, None]
    assert problems == [
        guide.AnchorProblem(3, None, "heading '### B' has no anchor on its next line"),
        guide.AnchorProblem(6, None, "malformed anchor '<!-- cc: Bad_ID -->'"),
        guide.AnchorProblem(8, 'a.one', 'anchor a.one repeats line 2'),
        guide.AnchorProblem(10, None, 'anchor is not directly under a heading'),
    ]


def test_the_fixture_guide_has_no_anchor_problems():
    assert guide.anchor_problems(guide_text()) == []


def test_text_hash_ignores_rewrapping_but_not_words():
    h = guide.text_hash('## A\nOne two\nthree.')
    assert h.startswith('sha256:') and len(h) == len('sha256:') + 64
    assert guide.text_hash('## A   One\n\ntwo three.') == h
    assert guide.text_hash('## A\nOne two\nfour.') != h


@pytest.mark.parametrize('line, spans', [
    ('`if` and `foo`', ['if', 'foo']),
    ('| `shell` | `bash` or `powershell` for `` !`command` `` preprocessing |',
     ['shell', 'bash', 'powershell', '!`command`']),
    ('`` !`command` `` (inline) or a ```` ```! ```` fenced block runs',
     ['!`command`', '```!']),
    ('an unmatched `` run, then `x`', ['x']),
])
def test_code_spans_pair_backtick_runs_as_commonmark_does(line, spans):
    assert guide.code_spans(line) == spans


def test_terms_keep_three_to_sixty_characters_and_drop_stop_terms():
    assert guide.section_terms(by_id(guide_text())['alpha.overview']) == {'ALPHA_TOOL'}


def test_terms_skip_fenced_code_and_apply_extra_and_exclude_terms():
    reference = by_id(guide_text())['alpha.reference']
    assert guide.section_terms(reference) == {'ALPHA_ENV', 'a `tick` inside'}
    assert guide.section_terms(reference, extra=['alpha-mode'], exclude=['a `tick` inside']) == {
        'ALPHA_ENV', 'alpha-mode'}


def test_the_stamp_region_reads_and_rewrites_between_its_markers():
    text = guide_text()
    assert guide.stamp_content(text) == FIXTURE_STAMP
    rewritten = guide.with_stamp(text, '> New stamp.')
    assert guide.stamp_content(rewritten) == '> New stamp.'
    assert rewritten.replace('> New stamp.', FIXTURE_STAMP) == text


@pytest.mark.parametrize('broken', [
    lambda t: t.replace(guide.STAMP_CLOSE, ''),
    lambda t: t.replace(guide.STAMP_OPEN, guide.STAMP_OPEN + '\n' + guide.STAMP_OPEN),
    lambda t: t.replace(guide.STAMP_OPEN, '\0').replace(guide.STAMP_CLOSE, guide.STAMP_OPEN).replace('\0', guide.STAMP_CLOSE),
    lambda t: t.replace(guide.STAMP_OPEN, FENCE + '\n' + guide.STAMP_OPEN + '\n' + FENCE),
])
def test_a_missing_doubled_reversed_or_fenced_marker_means_no_region(broken):
    assert guide.stamp_content(broken(guide_text())) is None


def test_render_stamp_names_the_oldest_checked_and_audited():
    states = {
        'a.one': {'checked': {'release': '2.1.10', 'date': '2026-09-05'},
                  'audited': {'release': '2.1.9', 'date': '2026-08-01'}},
        'a.two': {'checked': {'release': '2.1.9', 'date': '2026-09-09'},
                  'audited': {'release': '2.1.10', 'date': '2026-09-05'}},
    }
    assert guide.render_stamp(states) == (
        '> Checked against the Claude Code docs and changelog through 2.1.9 on 2026-09-09; '
        'oldest full re-verification 2026-08-01, at 2.1.9.')


def test_real_guide_has_no_anchor_problems():
    '''build/test_check_conformance.py pins the guide's 38 IDs in order,
    read with this module's grammar (R1.2); this suite imports nothing from
    build/ (R12.1).'''
    assert guide.anchor_problems(REAL_GUIDE.read_text(encoding='utf-8')) == []
