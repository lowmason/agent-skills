'''Read plan 111's trigger reps: did the rep load classification-codes, what did the listing hold, and the tally.

Copy of plan 107's triggers.py (specs/baseline/red-baseline-writing-skills-tests/kit/triggers.py). Its
changes: the skill under test is classification-codes, a rep folder is <prompt>/<arm>/<model>/rep<N> (one
condition, so no condition folder), and judge() applies plan 111's PASS rule in place of plan 107's floor,
bars and prediction.

Usage, from the repository root:
  uv run python <kit>/triggers.py loads <rep-dir>      prints `load` or `no-load`, then each Skill call
  uv run python <kit>/triggers.py listing <rep-dir>    prints the skills in the stream's init record
  uv run python <kit>/triggers.py tally <runs-root>    prints the counts, the bars and the verdict
<rep-dir> is a rep<N>/ folder under <prompt>/<arm>/<model>/ (run_trigger_reps.sh). The stream is read from
CD_TRIGGER_SCRATCH (audit.py's layout). <runs-root> holds <prompt>/<arm>/<model>/rep<N>/ for the nine prompts,
the arms old and new, and the two models only. tally refuses any other name, so a probe or a pilot goes in a
root of its own.

A rep loads when its stream has any `tool_use` named `Skill` whose `skill` input is exactly
`classification-codes`, whatever comes before it: a later call counts, and so does a rep that stopped on
--max-turns or on its budget. The listing is the init record's `skills` field, as names (a string, or an
object with a `name`).

tally counts, for each prompt, arm and model, the reps that audit.py does not void, and how many of them loaded
the skill. judge() applies the registered PASS rule to the counts. On each model:
- `new` loads on P1 + P2 >= `old` loads there (the ind bar);
- `new` loads on P1 to P5 >= `old` loads there (the should-load bar);
- `new` loads on N1 to N4 <= `old` loads there (the near-miss bar).
The verdict is pass when the three bars hold on both models and fail when one does not. It is incomplete
unless every cell (9 prompts x 2 arms x 2 models) holds exactly 3 valid reps, whatever the bars say.
'''
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases  # noqa: E402
import rep_tools  # noqa: E402
import trigger_prompts  # noqa: E402

SKILL = cases.SKILL
BARS = (('ind', trigger_prompts.IND, 'at least'), ('should-load', trigger_prompts.SHOULD_LOAD, 'at least'),
        ('near-miss', trigger_prompts.NEAR_MISS, 'at most'))


def skill_calls(records: list[dict]) -> list[str]:
    '''The `skill` input of each Skill tool call, in stream order.'''
    found = []
    for call in rep_tools.read_records(records)['calls']:
        if call.get('name') == 'Skill':
            name = (call.get('input') or {}).get('skill')
            found.append(name if isinstance(name, str) else '')
    return found


def is_load_in(calls: list[dict]) -> bool:
    return any(call.get('name') == 'Skill' and (call.get('input') or {}).get('skill') == SKILL for call in calls)


def is_load(records: list[dict]) -> bool:
    return SKILL in skill_calls(records)


def listing(records: list[dict]) -> list[str]:
    '''The skills in the first init record, as names.'''
    for record in records:
        if record.get('type') == 'system' and record.get('subtype') == 'init':
            found = []
            for item in record.get('skills') if isinstance(record.get('skills'), list) else []:
                name = item.get('name') if isinstance(item, dict) else item
                if isinstance(name, str):
                    found.append(name)
            return found
    return []


def load_records(rep: Path) -> list[dict]:
    import audit
    path = audit.stream_path(rep)
    if not path.is_file():
        raise SystemExit(f'refusing: no stream at {path}')
    return rep_tools.read_stream(path.read_bytes())[0]


def judge(cells: dict) -> dict:
    '''The registered PASS rule on tally cells: {(prompt, arm, model): {'reps', 'loads', 'void'}}.'''
    def total(arm: str, model: str, prompts: tuple[str, ...]) -> int:
        return sum(cells.get((prompt, arm, model), {}).get('loads', 0) for prompt in prompts)

    bars = []
    for model in cases.MODELS:
        for kind, prompts, side in BARS:
            old, new = total('old', model, prompts), total('new', model, prompts)
            bars.append({'kind': kind, 'model': model, 'old': old, 'new': new,
                         'ok': new >= old if side == 'at least' else new <= old})
    wanted = {(prompt, arm, model) for prompt in trigger_prompts.PROMPTS for arm in cases.ARMS for model in cases.MODELS}
    complete = all(cells.get(key, {}).get('reps') == cases.REPS_PER_CELL for key in wanted)
    return {'bars': bars, 'complete': complete, 'ok': complete and all(bar['ok'] for bar in bars)}


def verdict(result: dict) -> str:
    '''incomplete without exactly the planned valid reps in each cell, fail on a missed bar, else pass.'''
    if not result['complete']:
        return 'incomplete'
    return 'pass' if result['ok'] else 'fail'


def folders(parent: Path, allowed, what: str) -> list[Path]:
    '''The folders in parent, each of whose names must be in allowed. A hidden name is skipped.'''
    found = []
    for path in sorted(p for p in parent.iterdir() if not p.name.startswith('.')):
        if path.name not in allowed or not path.is_dir():
            raise SystemExit(f'refusing: {path} is not a {what} folder ({", ".join(allowed)})')
        found.append(path)
    return found


def tally(runs_root: Path) -> dict:
    '''The counts of every rep under runs_root, with a line for each void rep, and judge's verdict on them.'''
    import audit
    cells, voids = {}, []
    for prompt_dir in folders(runs_root, tuple(trigger_prompts.PROMPTS), 'prompt'):
        for arm_dir in folders(prompt_dir, cases.ARMS, 'arm'):
            for model_dir in folders(arm_dir, cases.MODELS, 'model'):
                key = (prompt_dir.name, arm_dir.name, model_dir.name)
                cell = cells.setdefault(key, {'reps': 0, 'loads': 0, 'void': 0})
                reps = sorted((p for p in model_dir.glob('rep*') if p.is_dir() and p.name[3:].isdigit()),
                              key=lambda p: int(p.name[3:]))
                for rep in reps:
                    found = audit.audit_rep(rep)
                    if found['void']:
                        cell['void'] += 1
                        voids.append(f'{" ".join(key)} {rep.name}: {"; ".join(found["void"])}')
                        continue
                    cell['reps'] += 1
                    cell['loads'] += 1 if is_load_in(found['stream']['calls']) else 0
    return {'cells': cells, 'voids': voids, **judge(cells)}


def show_tally(result: dict) -> None:
    for key, cell in sorted(result['cells'].items()):
        print(f'{" ".join(key)}: {cell["loads"]} of {cell["reps"]} (void {cell["void"]})')
    for line in result['voids']:
        print(f'void: {line}')
    for bar in result['bars']:
        print(f'bar {bar["kind"]} {bar["model"]}: old {bar["old"]}, new {bar["new"]}, '
              f'{"ok" if bar["ok"] else "MISSED"}')
    print(f'verdict: {verdict(result)}')


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[1] not in ('loads', 'listing', 'tally'):
        raise SystemExit(__doc__)
    command, arg = sys.argv[1], Path(sys.argv[2]).resolve()
    if command == 'tally':
        show_tally(tally(arg))
        return
    records = load_records(arg)
    if command == 'loads':
        print('load' if is_load(records) else 'no-load')
        print(f'Skill calls: {", ".join(skill_calls(records)) or "none"}')
    else:
        for name in listing(records):
            print(name)


if __name__ == '__main__':
    main()
