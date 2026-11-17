'''Grade the cc-guide stamp-line reps: does each rep cite or hold each fixture file?

Usage: python3 <kit>/grade.py <out-dir>
Reads only the ACTION lines of each rep's reply. A file is CITE when an ACTION line runs
`baseline cite <file>`, HOLD when one runs settle with `--hold <file>` and none cites it, and NONE
otherwise. Prose that only mentions a command is not an action. Read every reply by hand too:
show_reps.py prints them. VOID reps (see show_reps.py) are left out of the counts.
'''
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from show_reps import void_reason  # noqa: E402

FILES = {'A': 'commands/release-notes.md', 'B': 'agents/style-checker.md'}


def verdict(actions: list[str], path: str) -> str:
    if any(re.search(rf'baseline cite\s+{re.escape(path)}', a) for a in actions):
        return 'CITE'
    if any(re.search(rf'--hold\s+{re.escape(path)}', a) for a in actions):
        return 'HOLD'
    return 'NONE'


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    counts: dict[str, dict[str, int]] = {k: {} for k in FILES}
    for path in sorted(Path(sys.argv[1]).glob('rep*.json'), key=lambda p: int(p.stem[3:])):
        try:
            data = json.loads(path.read_text() or '{}')
        except json.JSONDecodeError:
            print(f'{path.name}: VOID (unreadable JSON)')
            continue
        reason = void_reason(data)
        if reason:
            print(f'{path.name}: VOID ({reason})')
            continue
        actions = [line for line in str(data.get('result', '')).splitlines()
                   if line.lstrip('`* -').startswith('ACTION:')]
        row = {k: verdict(actions, p) for k, p in FILES.items()}
        for k, v in row.items():
            counts[k][v] = counts[k].get(v, 0) + 1
        print(f"{path.name}: A={row['A']} B={row['B']}")
    for k, p in FILES.items():
        print(f'{k} {p}: ' + ', '.join(f'{v} {n}' for v, n in sorted(counts[k].items())))


if __name__ == '__main__':
    main()
