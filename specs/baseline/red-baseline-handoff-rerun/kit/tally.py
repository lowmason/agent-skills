#!/usr/bin/python3
'''Check scores against extracts, then report each arm's verdict (plan 100).

Usage: tally.py PHASE

A fork of plan 40's $RED/tools/tally.py that reads $PHR_CTL (default
~/.cache/agent-skills/handoffs/rerun100). It reads scores/PHASE/<arm>.tsv
(columns: rep, criterion, verdict, quote; verdict PASS, FAIL, NA or VOID) and
each scored rep's results/<rep>/audit.json and extract.md. Exits 1, listing the
lines, when a PASS, FAIL or VOID line's quote is empty or not found in its
rep's extract (whitespace runs compared as one space): rescore those.
The reps an arm counts come from the audits, not the score file: the first 5
by id whose audit is valid, has that arm and has PHASE as its phase, less any
rep the score file marks VOID. So a probe or pilot rep never counts in another
phase. Exits 1, naming the gap, when a counted rep has no rows, or has no row
for a criterion that the arm's other rows use. Otherwise prints, per arm, the
valid reps counted, the failures per criterion, and the verdict by the plan's
Thresholds: `v1` and `b2` pass when at least 4 of their first 5 valid reps
pass every criterion, `c4a-neg` when at most 1 of its first 5 valid reps fails
F-brief. Runs on the system Python 3.9.
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


def rep_id(rep: str) -> int:
    return int(rep[1:])


def counted_reps(rows: list[dict], expected: list[str]) -> list[str]:
    '''The first COUNTED of the arm's valid reps (from the audits), less the
    reps the score file marks VOID.'''
    void = {r['rep'] for r in rows if r['criterion'] == 'VOID'}
    return [rep for rep in sorted(expected, key=rep_id) if rep not in void][:COUNTED]


def gaps(arm: str, rows: list[dict], reps: list[str]) -> list[str]:
    '''A line for each counted rep with no rows, or with no row for a
    criterion that the other counted reps' rows use.'''
    criteria = {r['criterion'] for r in rows if r['rep'] in reps} - {'VOID'}
    out = []
    for rep in reps:
        has = {r['criterion'] for r in rows if r['rep'] == rep}
        if not has:
            out.append(f'{arm} {rep}: no rows')
        out += [f'{arm} {rep}: no row for {c}' for c in sorted(criteria - has) if has]
    return out


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
    extracts = {}
    for rep in reps:
        out = CTL / 'results' / rep
        extracts[rep] = squash((out / 'extract.md').read_text()) if (out / 'extract.md').exists() else ''
    expected: dict[str, list[str]] = {}  # arm -> its valid reps of this phase, by the audits
    for path in sorted((CTL / 'results').glob('*/audit.json')):
        audit = json.loads(path.read_text())
        if audit.get('valid') is True and audit.get('phase') == phase:
            expected.setdefault(str(audit.get('arm')), []).append(path.parent.name)
    bad = [line for rows in table.values() for line in bad_quotes(rows, extracts)]
    if bad:
        print('\n'.join(bad))
        return 1
    counts = {arm: counted_reps(rows, expected.get(arm, [])) for arm, rows in table.items()}
    missing = [line for arm, rows in table.items() for line in gaps(arm, rows, counts[arm])]
    if missing:
        print('\n'.join(missing))
        return 1
    for arm, rows in table.items():
        counted = counts[arm]
        fails = failures(rows, counted)
        detail = ' '.join(f'{c}:{len(rs)}' for c, rs in sorted(fails.items())) or '-'
        print(f'{arm:10} counted {",".join(counted) or "-":30} fails {detail:40} {verdict(phase, arm, rows, counted)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
