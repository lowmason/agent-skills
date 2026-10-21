'''Tests for report_grammar.py: how a verifier report splits into rows, and
which of its lines are no rows (drift spec R8.4-R8.8).'''
import pytest

import report_grammar


@pytest.mark.parametrize('line, count, quoted, fields', [
    ('B1 | NOISE | - | - | - | "a | b "c"" | why | it has a pipe', 7, report_grammar.TRIAGE_QUOTES,
     ['B1', 'NOISE', '-', '-', '-', '"a | b "c""', 'why | it has a pipe']),
    ('| B1 | TOUCHES | x.y | 4 | "g" | "s" | why |', 7, report_grammar.TRIAGE_QUOTES,
     ['B1', 'TOUCHES', 'x.y', '4', '"g"', '"s"', 'why']),
    ('2.1.901 | none', 2, (), ['2.1.901', 'none']),
    ('B1 | NOISE | why', 7, report_grammar.TRIAGE_QUOTES, None),
    ('B1 | NOISE | - | - | "unclosed | why', 7, report_grammar.TRIAGE_QUOTES, None),
    # A free-text field that opens with a quote ends at the next pipe, as in
    # the 2026-10-12 skill probe's files row.
    ('a.md:22 | "no edit tools": no Write | x.y | "a | b" | consistent', 5, report_grammar.FILES_QUOTES,
     ['a.md:22', '"no edit tools": no Write', 'x.y', '"a | b"', 'consistent']),
])
def test_a_row_splits_on_pipes_but_a_quote_field_holds_pipes_and_quotes(line, count, quoted, fields):
    assert report_grammar.split_row(line, count, quoted) == fields


def test_a_quote_field_drops_its_outer_quotes_and_a_dash_is_no_quote():
    assert [report_grammar.unquote(f) for f in ('"a "b" c"', '-', '', 'bare')] == ['a "b" c', '', '', 'bare']


def test_table_separators_header_rows_and_prose_are_no_rows():
    text = '\n'.join(['# Report', 'Prose without a pipe.', report_grammar.TRIAGE_ROW, '|---|---|',
                      '| item | verdict |', 'B1 | NOISE | - | - | - | "s" | why'])
    assert report_grammar.report_lines(text) == ['B1 | NOISE | - | - | - | "s" | why']
