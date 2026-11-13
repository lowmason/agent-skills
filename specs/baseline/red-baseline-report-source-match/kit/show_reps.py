'''Print each rep's reply, cost and model from the run_reps.sh JSON files.

Usage: python3 <kit>/show_reps.py <out-dir>
'''
import json
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    total = 0.0
    for path in sorted(Path(sys.argv[1]).glob('rep*.json'), key=lambda p: int(p.stem[3:])):
        data = json.loads(path.read_text())
        cost = data.get('total_cost_usd', 0.0)
        total += cost
        models = ', '.join(data.get('modelUsage', {}))
        print(f'===== {path.name}  ${cost:.3f}  {models}  is_error={data.get("is_error")}')
        print(data.get('result', ''))
        print()
    print(f'total ${total:.3f}')


if __name__ == '__main__':
    main()
