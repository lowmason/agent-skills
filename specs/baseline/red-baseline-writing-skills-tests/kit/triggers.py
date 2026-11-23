'''Read plan 107's trigger reps: did the rep load writing-skills, what did the listing hold, and the tally.

Usage, from the repository root:
  uv run python <kit>/triggers.py loads <rep-dir>      prints `load` or `no-load`, then each Skill call
  uv run python <kit>/triggers.py listing <rep-dir>    prints the skills in the stream's init record
  uv run python <kit>/triggers.py tally <runs-root>    prints the counts, the floor, the bars and the prediction
<rep-dir> is a rep<N>/ folder under <prompt>/<arm>/<condition>/<model>/ (run_trigger_reps.sh). The stream is
read from WST_TRIGGER_SCRATCH (audit.py's layout). <runs-root> holds <prompt>/<arm>/<condition>/<model>/rep<N>/.

A rep loads when its stream has any `tool_use` named `Skill` whose `skill` input is exactly `writing-skills`,
whatever comes before it: a later call counts, and so does a rep that stopped on --max-turns or on its budget.
The listing is the init record's `skills` field, as names (a string, or an object with a `name`).

tally counts, for each prompt, arm, condition and model, the reps that audit.py does not void, and how many
of them loaded the skill. judge() applies the registered rules to the counts. A cell holds 3 reps, and a
full run holds every prompt, arm, condition and model:
- floor, per model: the `old` should-load loads (P1 to P5) in `full` are at least FLOOR of 15. Below it the
  verdict is uninformative;
- no-loss bars, per model and condition: `new` should-load loads >= `old` - 2, and `new` near-miss loads
  (N1 to N3) <= `old` + 1;
- prediction, descriptive and never failing the verdict: in `cut150`, `new` >= `old` on P1 to P3.
'''
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rep_tools  # noqa: E402
import trigger_prompts  # noqa: E402

SKILL = 'writing-skills'
MODELS = ('claude-opus-5-5', 'claude-sonnet-5-5')
CONDITIONS = ('full', 'cut150')
ARMS = ('old', 'new')
REPS_PER_CELL = 3
FLOOR = 8
SHOULD_LOSS = 2
NEAR_MISS_GAIN = 1


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
    '''The registered rules on tally cells: {(prompt, arm, condition, model): {'reps', 'loads', 'void'}}.'''
    def total(arm: str, condition: str, model: str, prompts: tuple[str, ...]) -> int:
        return sum(cells.get((prompt, arm, condition, model), {}).get('loads', 0) for prompt in prompts)

    models = sorted({key[3] for key in cells})
    floor = {model: {'old_loads': total('old', 'full', model, trigger_prompts.SHOULD_LOAD)} for model in models}
    for entry in floor.values():
        entry['ok'] = entry['old_loads'] >= FLOOR
    bars = []
    for model in models:
        for condition in CONDITIONS:
            old = total('old', condition, model, trigger_prompts.SHOULD_LOAD)
            new = total('new', condition, model, trigger_prompts.SHOULD_LOAD)
            bars.append({'kind': 'should-load', 'model': model, 'condition': condition, 'old': old, 'new': new,
                         'ok': new >= old - SHOULD_LOSS})
            old = total('old', condition, model, trigger_prompts.NEAR_MISS)
            new = total('new', condition, model, trigger_prompts.NEAR_MISS)
            bars.append({'kind': 'near-miss', 'model': model, 'condition': condition, 'old': old, 'new': new,
                         'ok': new <= old + NEAR_MISS_GAIN})
    prediction = {}
    for model in models:
        old = total('old', 'cut150', model, trigger_prompts.TESTING)
        new = total('new', 'cut150', model, trigger_prompts.TESTING)
        prediction[model] = {'old': old, 'new': new, 'holds': new >= old}
    wanted = {(prompt, arm, condition, model) for prompt in trigger_prompts.PROMPTS for arm in ARMS
              for condition in CONDITIONS for model in MODELS}
    complete = bool(cells) and all(cells.get(key, {}).get('reps') == REPS_PER_CELL for key in wanted)
    ok = complete and all(entry['ok'] for entry in floor.values()) and all(bar['ok'] for bar in bars)
    return {'floor': floor, 'bars': bars, 'prediction': prediction, 'complete': complete, 'ok': ok}


def tally(runs_root: Path) -> dict:
    '''The counts of every rep under runs_root, with a line for each void rep, and judge's verdict on them.'''
    import audit
    cells, voids = {}, []
    for prompt_dir in sorted(p for p in runs_root.iterdir() if not p.name.startswith('.')):
        if prompt_dir.name not in trigger_prompts.PROMPTS or not prompt_dir.is_dir():
            raise SystemExit(f'refusing: {prompt_dir} is not a prompt folder ({", ".join(trigger_prompts.PROMPTS)})')
        for arm_dir in sorted(p for p in prompt_dir.iterdir() if p.is_dir()):
            for condition_dir in sorted(p for p in arm_dir.iterdir() if p.is_dir()):
                for model_dir in sorted(p for p in condition_dir.iterdir() if p.is_dir()):
                    key = (prompt_dir.name, arm_dir.name, condition_dir.name, model_dir.name)
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
    for model, entry in sorted(result['floor'].items()):
        print(f'floor {model}: old should-load loads in full {entry["old_loads"]} of 15, '
              f'{"ok" if entry["ok"] else "BELOW the floor of " + str(FLOOR)}')
    for bar in result['bars']:
        print(f'bar {bar["kind"]} {bar["model"]} {bar["condition"]}: old {bar["old"]}, new {bar["new"]}, '
              f'{"ok" if bar["ok"] else "MISSED"}')
    for model, entry in sorted(result['prediction'].items()):
        print(f'prediction {model} (cut150, P1-P3): old {entry["old"]}, new {entry["new"]}, '
              f'{"holds" if entry["holds"] else "does not hold"}')
    print(f'verdict: {"incomplete" if not result["complete"] else "pass" if result["ok"] else "fail"}')


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
