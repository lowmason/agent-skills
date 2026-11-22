'''Print a rep's grading sheet, its status flags, or the spend. Reads the scrubbed copies run_reps.sh writes.

Usage, from the repository root:
  uv run python <kit>/show_reps.py sheet <case> <run-dir> [<rep> ...]
  uv run python <kit>/show_reps.py status <run-dir> [<rep> ...]
  uv run python <kit>/show_reps.py cost <scratch-dir>

sheet prints, for each rep, a grading sheet: a header with the case and the rep id, the case's PASS and
FAIL columns, and the rep's answer (its `result`). A sheet names the rep id and the case, never the arm,
the folder or the cost, so a sheet of one arm can be diffed against a sheet of the other: only the
answer may differ. The text goes through kit_identity.scrub.
status prints each rep's is_error, subtype, num_turns, cost and the VOID flags that the record's VOID rule
names (a rep that ran a tool or the advisor, errored, stopped on its budget, or has an empty result). A
flag is a prompt to read the rep, never a verdict. A rep<N>.VOID note is listed as void.
cost sums total_cost_usd over every .json file below <scratch-dir> (reps, voided reps and probes) and
prints the sum for each folder and the total. The raw JSON in the scratch folder is the cost record, since
a void rep keeps no copy in the repository.
'''
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_prompts  # noqa: E402
import kit_identity  # noqa: E402


def rep_paths(directory: Path, wanted: list[str]) -> list[Path]:
    paths = sorted(directory.glob('rep*.json'), key=lambda p: int(p.stem[3:]))
    if wanted:
        paths = [p for p in paths if p.stem[3:] in wanted]
    return paths


def load(path: Path) -> dict:
    try:
        data = json.loads(path.read_text() or '{}')
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def sheet(case: str, directory: Path, wanted: list[str]) -> None:
    forms = kit_identity.forms()
    for path in rep_paths(directory, wanted):
        data = load(path)
        print(kit_identity.scrub(
            f'=== case {case}, {path.stem} ===\n'
            f'PASS: {build_prompts.CASES[case]["pass"]}\n'
            f'FAIL: {build_prompts.CASES[case]["fail"]}\n'
            f'--- answer ---\n{data.get("result", "")}\n=== end {path.stem} ===\n', forms))


def status(directory: Path, wanted: list[str]) -> None:
    for note in sorted(directory.glob('rep*.VOID')):
        print(f'{directory.name}/{note.stem}: void note: {note.read_text().strip()}')
    for path in rep_paths(directory, wanted):
        data = load(path)
        iterations = (data.get('usage') or {}).get('iterations')
        kinds = {str(i.get('type')) for i in iterations if isinstance(i, dict)} if isinstance(iterations, list) else set()
        extra = sorted(kinds - {'message'})
        models = len(data.get('modelUsage') or {})
        flags = []
        if not data:
            flags.append('unreadable')
        if data.get('num_turns') != 1 or extra or models > 1:
            flags.append('tool or advisor ran')
        if data.get('is_error') or data.get('subtype', 'success') != 'success':
            flags.append('error or budget stop')
        if not str(data.get('result', '')).strip():
            flags.append('empty result')
        print(f'{directory.name}/{path.stem}: is_error={data.get("is_error")} subtype={data.get("subtype")} '
              f'turns={data.get("num_turns")} extra-iters={",".join(extra) or "-"} models={models} '
              f'cost=${float(data.get("total_cost_usd") or 0):.3f} flags={";".join(flags) or "-"}')


def cost(root: Path) -> None:
    total = 0.0
    folders: dict[str, float] = {}
    for path in sorted(root.rglob('*.json')):
        amount = float(load(path).get('total_cost_usd') or 0)
        folder = str(path.parent.relative_to(root))
        folders[folder] = folders.get(folder, 0.0) + amount
        total += amount
    for folder, amount in sorted(folders.items()):
        print(f'{folder}: ${amount:.3f}')
    print(f'total ${total:.3f}')


def main() -> None:
    args = sys.argv[1:]
    if len(args) >= 3 and args[0] == 'sheet' and args[1] in build_prompts.CASES:
        sheet(args[1], Path(args[2]), args[3:])
    elif len(args) >= 2 and args[0] == 'status':
        status(Path(args[1]), args[2:])
    elif len(args) == 2 and args[0] == 'cost':
        cost(Path(args[1]))
    else:
        raise SystemExit(__doc__)


if __name__ == '__main__':
    main()
