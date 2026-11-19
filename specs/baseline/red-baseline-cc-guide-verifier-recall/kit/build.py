'''Plan the reps of plan 102's verifier-recall kit in $K/plan.json, under
Python 3.13 (Task 6; plan 45's DF15 for the blinding):

    build.py batch <name> <packet> <pairs>   <pairs> (control, changed) pairs of one packet
    build.py spare <rid>                     one rep with void rep <rid>'s packet and arm
    build.py probe                           the probe rep, uncounted, and a new $K/canary.txt
    build.py pilot                           the pilot, uncounted: one changed-arm audit rep

Rep ids run r001, r002 and on, across every command, and are never reused.
Each pair's two arms take a random order from `secrets`, so neither a rep id
nor a batch file names an arm. $K/batches/<name>.txt lists a batch's rep ids,
one a line, in run order. A spare joins its void rep's batch file, the probe
joins probe.txt and the pilot pilot.txt, so `run.py <batch>` runs it next.
plan.json is the one file here that names an arm. Nothing this script prints
names one; a refusal of a third spare says only that the packet and arm have
had their two.

Exit 0 on success, 1 on a refusal, 2 on a usage error.'''
import json
import re
import secrets
import sys
from pathlib import Path

import common

NAME_RE = re.compile(r'[a-z0-9][a-z0-9-]{0,39}')
PROBE_BATCH, PILOT_BATCH = 'probe', 'pilot'
USAGE = 'usage: build.py batch <name> <packet> <pairs> | spare <rid> | probe | pilot'


class Refusal(Exception):
    '''A request this script declines; its message names no arm.'''


def load_plan() -> dict:
    path = common.k_dir() / 'plan.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'reps': []}


def save(plan: dict, batch: str, new: list[dict]) -> None:
    '''Write plan.json with the new reps, and append their ids to the batch file.'''
    k = common.k_dir()
    k.mkdir(parents=True, exist_ok=True)
    plan['reps'] += new
    tmp = k / 'plan.json.tmp'
    tmp.write_text(json.dumps(plan, indent=1) + '\n', encoding='utf-8')
    tmp.replace(k / 'plan.json')
    (k / 'batches').mkdir(exist_ok=True)
    with (k / 'batches' / f'{batch}.txt').open('a', encoding='utf-8') as f:
        f.writelines(rep['rid'] + '\n' for rep in new)
    for rep in new:
        print(f"{rep['rid']} {rep['packet']} in batch {batch}")


def next_ids(plan: dict, count: int) -> list[str]:
    '''The next count rep ids, after the highest id plan.json has ever held.'''
    top = max((int(rep['rid'][1:]) for rep in plan['reps']), default=0)
    return [f'r{n:03d}' for n in range(top + 1, top + 1 + count)]


def rep(rid: str, batch: str, packet: str, arm: str, role: str) -> dict:
    return {'rid': rid, 'batch': batch, 'packet': packet, 'arm': arm, 'role': role}


def add_batch(name: str, packet: str, pairs: int) -> None:
    if not NAME_RE.fullmatch(name) or name in (PROBE_BATCH, PILOT_BATCH):
        raise Refusal(f'{name}: not a batch name (lower-case letters, digits and hyphens; not probe or pilot)')
    if (common.k_dir() / 'batches' / f'{name}.txt').exists():
        raise Refusal(f'batch {name}: exists; a batch name is used once')
    if packet not in common.PACKETS:
        raise Refusal(f"{packet}: not a packet ({', '.join(common.PACKETS)})")
    plan = load_plan()
    ids = iter(next_ids(plan, 2 * pairs))
    new = []
    for _ in range(pairs):
        first = secrets.randbelow(2)
        arms = common.ARMS if first == 0 else common.ARMS[::-1]
        new += [rep(next(ids), name, packet, arm, 'counted') for arm in arms]
    save(plan, name, new)


def add_spare(rid: str) -> None:
    '''One replacement for void rep rid, with its packet and arm, in its batch.
    A packet and arm get at most common.MAX_SPARES.'''
    plan = load_plan()
    old = next((r for r in plan['reps'] if r['rid'] == rid), None)
    if old is None:
        raise Refusal(f'{rid}: no such rep')
    if old['role'] not in ('counted', 'spare'):
        raise Refusal(f'{rid}: a spare replaces a counted rep only')
    used = sum(1 for r in plan['reps']
               if r['role'] == 'spare' and (r['packet'], r['arm']) == (old['packet'], old['arm']))
    if used >= common.MAX_SPARES:
        raise Refusal(f'{rid}: its packet and arm have had {common.MAX_SPARES} spares, so that result is UNSETTLED')
    [new_id] = next_ids(plan, 1)
    save(plan, old['batch'], [rep(new_id, old['batch'], old['packet'], old['arm'], 'spare') | {'replaces': rid}])


def add_probe() -> None:
    '''The probe rep (Task 8 Step 5), and a fresh random token in $K/canary.txt.'''
    plan = load_plan()
    [new_id] = next_ids(plan, 1)
    common.k_dir().mkdir(parents=True, exist_ok=True)
    (common.k_dir() / 'canary.txt').write_text(secrets.token_hex(16) + '\n', encoding='utf-8')
    save(plan, PROBE_BATCH, [rep(new_id, PROBE_BATCH, common.PROBE, 'control', 'probe')])


def add_pilot() -> None:
    '''The pilot (PC8): one changed-arm audit rep.'''
    plan = load_plan()
    [new_id] = next_ids(plan, 1)
    save(plan, PILOT_BATCH, [rep(new_id, PILOT_BATCH, 'audit', 'changed', 'pilot')])


def main(argv: list[str]) -> int:
    try:
        match argv:
            case ['batch', name, packet, pairs] if pairs.isdigit() and int(pairs) > 0:
                add_batch(name, packet, int(pairs))
            case ['spare', rid]:
                add_spare(rid)
            case ['probe']:
                add_probe()
            case ['pilot']:
                add_pilot()
            case _:
                print(USAGE, file=sys.stderr)
                return 2
    except Refusal as refusal:
        print(f'build.py: refused: {refusal}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
