'''Tests for deferred_stats.py — the deferred-backlog health reporter.'''
from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

from deferred_stats import compute_stats, format_report, parse_sections

SCRIPT = Path(__file__).with_name('deferred_stats.py')
TODAY = dt.date(2026, 9, 8)

SAMPLE = '''# Deferred items

## 11-delegation-frontmatter-rollout — 2026-07-19
- [x] Shipped item, done in plan 12.
- [ ] Open and old: needs a prod decision.
      Continuation line that is not an item.

## 26-distill-sessions-hardening — 2026-09-04
- [ ] Open and fresh.
- [ ] Also open and fresh.
- [x] Closed here.
'''


def test_parse_sections_counts_open_and_closed():
    sections = parse_sections(SAMPLE)
    assert [s['name'] for s in sections] == [
        '11-delegation-frontmatter-rollout',
        '26-distill-sessions-hardening',
    ]
    assert sections[0]['date'] == dt.date(2026, 7, 19)
    assert (sections[0]['open'], sections[0]['closed']) == (1, 1)
    assert (sections[1]['open'], sections[1]['closed']) == (2, 1)


def test_preamble_and_continuation_lines_are_not_items():
    stats = compute_stats(parse_sections(SAMPLE), TODAY)
    assert stats['total'] == 5


def test_undated_section_counts_items_but_not_age():
    text = SAMPLE + '\n## Aged-backlog acknowledgements\n- 2026-09-08 — carried 1 item.\n'
    text += '\n## Hand-written section with no date\n- [ ] Undated open item.\n'
    stats = compute_stats(parse_sections(text), TODAY)
    assert stats['undated_open'] == 1
    assert stats['open'] == 4
    # The acknowledgement bullet is not a checkbox, so it never enters the counts.
    assert stats['total'] == 6


def test_closure_rate_and_empty_backlog():
    stats = compute_stats(parse_sections(SAMPLE), TODAY)
    assert stats['closed'] == 2
    assert stats['closure_rate'] == 0.4
    empty = compute_stats(parse_sections('# Deferred items\n'), TODAY)
    assert empty['total'] == 0
    assert empty['closure_rate'] is None


def test_aged_open_uses_section_date():
    stats = compute_stats(parse_sections(SAMPLE), TODAY, aged_days=45)
    assert stats['aged_open'] == 1
    assert stats['aged_days'] == 45
    loose = compute_stats(parse_sections(SAMPLE), TODAY, aged_days=90)
    assert loose['aged_open'] == 0


def test_oldest_open_reports_days_and_section():
    stats = compute_stats(parse_sections(SAMPLE), TODAY)
    assert stats['oldest_open_days'] == 51
    assert stats['oldest_open_section'] == '11-delegation-frontmatter-rollout'


def test_age_histogram_buckets_open_items_only():
    stats = compute_stats(parse_sections(SAMPLE), TODAY)
    buckets = {b['label']: b['count'] for b in stats['age_histogram']}
    assert buckets['0-14d'] == 2
    assert buckets['46-90d'] == 1
    assert sum(b['count'] for b in stats['age_histogram']) == 3


def test_missing_file_reports_absent(tmp_path):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), '--file', str(tmp_path / 'nope.md'), '--json'],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload['exists'] is False
    assert payload['open'] == 0


def test_json_output_carries_the_full_contract(tmp_path):
    target = tmp_path / 'deferred_items.md'
    target.write_text(SAMPLE, encoding='utf-8')
    result = subprocess.run(
        [sys.executable, str(SCRIPT), '--file', str(target), '--json'],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    for key in (
        'exists', 'open', 'closed', 'total', 'closure_rate', 'aged_days',
        'aged_open', 'undated_open', 'oldest_open_days', 'oldest_open_section',
        'age_histogram',
    ):
        assert key in payload, f'missing contract key: {key}'
    assert payload['exists'] is True


def test_format_report_names_the_two_thresholds():
    stats = compute_stats(parse_sections(SAMPLE), TODAY)
    report = format_report(stats)
    assert '3 open' in report
    assert '40%' in report
    assert 'aged >45d: 1' in report
