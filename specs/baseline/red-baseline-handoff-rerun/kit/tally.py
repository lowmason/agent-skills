#!/usr/bin/python3
'''Check scores against extracts, then report each arm's verdict (plan 100).

Usage: tally.py PHASE

A fork of plan 40's $RED/tools/tally.py that reads $PHR_CTL (default
~/.cache/agent-skills/handoffs/rerun100). It reads scores/PHASE/<arm>.tsv
(columns: rep, criterion, verdict, quote; verdict PASS, FAIL, NA or VOID) and
each scored rep's results/<rep>/audit.json and extract.md. Exits 1, listing the
lines, when a PASS, FAIL or VOID line's quote is empty or not found in its
rep's extract (whitespace runs compared as one space): rescore those.
Otherwise prints, per arm, the valid reps counted, the failures per criterion,
and the verdict by the plan's Thresholds: `v1` and `b2` pass when at least 4
of their first 5 valid reps pass every criterion, `c4a-neg` when at most 1 of
its first 5 valid reps fails F-brief. Only the first 5 valid reps by id count,
and a pilot rep never counts. Runs on the system Python 3.9.
'''

from __future__ import annotations

import csv
import json
import os
import re
import sys
from pathlib import Path

CTL = Path(os.environ.get('PHR_CTL') or Path.home() / '.cache/agent-skills/handoffs/rerun100')
POSITIVE = ('v1', 'b2')
NEGATIVE = {'c4a-neg': 1}  # most failing reps a negative arm allows
COUNTED = 5
PASS_AT = 4


def squash(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def read_scores(path: Path) -> list[dict]:
    with path.open(newline='') as f:
        return list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE))


def bad_quotes(rows: list[dict], extracts: dict[str, str]) -> list[str]:
    bad = []
    for row in rows:
        if row['verdict'] == 'NA':
            continue
        quote = squash(row.get('quote') or '')
        if not quote or quote not in extracts.get(row['rep'], ''):
            bad.append(f'{row["rep"]} {row["criterion"]} {row["verdict"]}: quote not found')
    return bad


def counted_reps(rows: list[dict], valid: dict[str, bool]) -> list[str]:
    void = {r['rep'] for r in rows if r['criterion'] == 'VOID'}
    reps = sorted({r['rep'] for r in rows} - void, key=lambda rep: int(rep[1:]))
    return [rep for rep in reps if valid.get(rep, False)][:COUNTED]


def failures(rows: list[dict], reps: list[str]) -> dict[str, set[str]]:
    '''criterion -> reps failing it, among the counted reps.'''
    out: dict[str, set[str]] = {}
    for r in rows:
        if r['rep'] in reps and r['verdict'] == 'FAIL':
            out.setdefault(r['criterion'], set()).add(r['rep'])
    return out


def verdict(phase: str, arm: str, rows: list[dict], reps: list[str]) -> str:
    if phase == 'pilot':
        return 'pilot (not counted)'
    if arm not in POSITIVE and arm not in NEGATIVE:
        return 'recorded'
    if len(reps) < COUNTED:
        return f'UNSETTLED ({len(reps)} of {COUNTED} valid)'
    failing = set().union(*failures(rows, reps).values())
    ok = len(failing) <= NEGATIVE[arm] if arm in NEGATIVE else COUNTED - len(failing) >= PASS_AT
    return f'{"PASS" if ok else "FAIL"} ({len(failing)} of {COUNTED} failing)'


def main() -> int:
    if len(sys.argv) != 2:
        print('usage: tally.py PHASE', file=sys.stderr)
        return 2
    phase = sys.argv[1]
    files = sorted((CTL / 'scores' / phase).glob('*.tsv'))
    if not files:
        print(f'tally.py: no scores/{phase}/*.tsv', file=sys.stderr)
        return 2
    table = {f.stem: read_scores(f) for f in files}
    reps = {r['rep'] for rows in table.values() for r in rows}
    extracts, valid = {}, {}
    for rep in reps:
        out = CTL / 'results' / rep
        extracts[rep] = squash((out / 'extract.md').read_text()) if (out / 'extract.md').exists() else ''
        audit = json.loads((out / 'audit.json').read_text()) if (out / 'audit.json').exists() else {}
        valid[rep] = bool(audit.get('valid')) and audit.get('phase') != 'pilot'  # pilot reps never count
    bad = [line for rows in table.values() for line in bad_quotes(rows, extracts)]
    if bad:
        print('\n'.join(bad))
        return 1
    for arm, rows in table.items():
        counted = counted_reps(rows, valid)
        fails = failures(rows, counted)
        detail = ' '.join(f'{c}:{len(rs)}' for c, rs in sorted(fails.items())) or '-'
        print(f'{arm:10} counted {",".join(counted) or "-":30} fails {detail:40} {verdict(phase, arm, rows, counted)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
