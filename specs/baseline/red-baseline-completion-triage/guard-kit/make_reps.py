#!/usr/bin/python3
'''Register new reps of one arm, ready for run_rep.sh (plan 100 kit, adapted for plan 101).

Usage: KIT_COMMIT=<sha> make_reps.py ARM PHASE COUNT BATCH

It appends one row per rep to $PHR_CTL/registry.tsv (header
`rep arm phase template kit_commit prompts extra`) and the rep ids to
$PHR_CTL/batches/BATCH.txt. Ids continue from r501 and are never reused. It
refuses an id whose $PHR_CTL/results/<id> or $PHR_CTL/homes/<id> exists. It
builds nothing: run_rep.sh builds each rep's HOME when the rep runs. Arms come
from arms.tsv beside this file. Runs on the system Python 3.9.
'''

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
ARMS = KIT / 'arms.tsv'
HEADER = 'rep\tarm\tphase\ttemplate\tkit_commit\tprompts\textra\n'
FIRST_ID = 501
COMMIT = re.compile(r'[0-9a-f]{40}')
NAME = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]*')


def control_dir() -> Path:
    return Path(os.environ.get('PHR_CTL') or Path.home() / '.cache/agent-skills/handoffs/guard101')


def arms() -> dict[str, tuple[str, str, str]]:
    '''arm: (template, comma-joined prompt files, extra), from arms.tsv. The extra is - for none.'''
    rows = [line.split('\t') for line in ARMS.read_text().splitlines()[1:] if line.strip()]
    return {arm: (template, prompts, extra) for arm, template, prompts, extra in rows}


def next_ids(registry: Path, count: int) -> list[str]:
    used = [int(line.split('\t', 1)[0][1:]) for line in registry.read_text().splitlines()[1:] if line.strip()]
    first = max(used, default=FIRST_ID - 1) + 1
    return [f'r{n:03d}' for n in range(first, first + count)]


def make(arm: str, phase: str, count: int, batch: str, kit_commit: str) -> list[str]:
    table = arms()
    if arm not in table:
        sys.exit(f'make_reps.py: unknown arm {arm}; arms.tsv has {", ".join(table)}')
    if not COMMIT.fullmatch(kit_commit):
        sys.exit(f'make_reps.py: KIT_COMMIT must be a full 40-hex SHA, got {kit_commit!r}')
    if count < 1:
        sys.exit('make_reps.py: COUNT must be at least 1')
    for value, what in ((phase, 'PHASE'), (batch, 'BATCH')):
        if not NAME.fullmatch(value):
            sys.exit(f'make_reps.py: bad {what} {value!r}')
    template, prompts, extra = table[arm]
    ctl = control_dir()
    ctl.mkdir(parents=True, exist_ok=True)
    registry = ctl / 'registry.tsv'
    if not registry.exists():
        registry.write_text(HEADER)
    reps = next_ids(registry, count)
    for rep in reps:
        taken = [p for p in (ctl / 'results' / rep, ctl / 'homes' / rep) if p.exists()]
        if taken:
            sys.exit(f'make_reps.py: {rep} is taken: {taken[0]} exists')
    with registry.open('a') as f:
        f.write(''.join('\t'.join((rep, arm, phase, template, kit_commit, prompts, extra)) + '\n' for rep in reps))
    (ctl / 'batches').mkdir(exist_ok=True)
    with (ctl / 'batches' / f'{batch}.txt').open('a') as f:
        f.write(''.join(f'{rep}\n' for rep in reps))
    return reps


def main(argv: list[str]) -> int:
    if len(argv) != 4 or not argv[2].isdigit():
        print(__doc__, file=sys.stderr)
        return 2
    kit_commit = os.environ.get('KIT_COMMIT', '')
    if not kit_commit:
        print('make_reps.py: KIT_COMMIT is required', file=sys.stderr)
        return 2
    arm, phase, count, batch = argv
    reps = make(arm, phase, int(count), batch, kit_commit)
    print(f'{arm} ({phase}): {" ".join(reps)} -> batches/{batch}.txt')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
