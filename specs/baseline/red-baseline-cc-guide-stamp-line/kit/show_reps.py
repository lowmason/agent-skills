'''Print each rep's reply, cost and model from the run_reps.sh JSON files.

Usage: python3 <kit>/show_reps.py <out-dir>
A rep is VOID when its file is empty or not a JSON object, when the run is an error, or when a
tool or the advisor ran: more than one turn, an iteration that is not a message, or more than one
model. A VOID rep does not count, and later reps still print.
'''
import json
import sys
from pathlib import Path


def void_reason(data: object) -> str:
    if not isinstance(data, dict) or not data:
        return 'empty or not a JSON object'
    if data.get('is_error'):
        return 'the run is an error'
    iterations = (data.get('usage') or {}).get('iterations')
    kinds = {str(i.get('type')) for i in iterations if isinstance(i, dict)} if isinstance(iterations, list) else set()
    if data.get('num_turns') != 1 or kinds - {'message'} or len(data.get('modelUsage') or {}) > 1:
        return 'a tool or the advisor ran'
    return ''


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    total = 0.0
    for path in sorted(Path(sys.argv[1]).glob('rep*.json'), key=lambda p: int(p.stem[3:])):
        try:
            data = json.loads(path.read_text() or '{}')
        except json.JSONDecodeError:
            print(f'===== {path.name}  VOID (unreadable JSON)\n')
            continue
        reason = void_reason(data)
        record = data if isinstance(data, dict) else {}
        cost = float(record.get('total_cost_usd') or 0)
        total += cost
        models = ', '.join(record.get('modelUsage') or {})
        flag = f'  VOID ({reason})' if reason else ''
        print(f'===== {path.name}  ${cost:.3f}  {models}  turns={record.get("num_turns")}{flag}')
        print(record.get('result', ''))
        print()
    print(f'total ${total:.3f}')


if __name__ == '__main__':
    main()
