'''Print plan 93 reviewer reps for reading: status, cost, reading aids and the full reply.

Usage, from the repository root: uv run python <kit>/show_reps.py <dir> [<dir> ...]
Each <dir> holds rep<N>.json files from run_reps.sh. The aids flag replies for the reader;
they are not verdicts. Every verdict is read by hand. A rep is VOID when a tool or the advisor
ran (turns, extra-iters, models), or when it errored or stopped on its budget cap (is_error,
subtype); a VOID rep is rerun and never scored.
'''
import json
import re
import sys
from pathlib import Path

AIDS = {
    # Each aid ignores letter case. An aid only points the reader at a reply; it is never a verdict.
    'mutant': re.compile(r'mutant', re.I),
    'withdraw': re.compile(r'withdraw', re.I),
    'inputs-table': re.compile(r'inputs?\s+table', re.I),
    'tab': re.compile(r'\btab\b|\btabs\b|tab-indented|\\t', re.I),
    'return-0': re.compile(r'returns?\s+0\b', re.I),
    'rule-7': re.compile(r'wordcount\.md:7', re.I),
    'rule-8': re.compile(r'wordcount\.md:8|whitespace rule', re.I),
    'unproven': re.compile(r'unproven', re.I),
    'unreachable': re.compile(r'unreachable', re.I),
}


def first_line(text: str) -> str:
    line = next((l for l in text.strip().splitlines() if l.strip()), '')
    return line.strip().strip('`*"\' .').lower()


def main() -> None:
    total = 0.0
    for d in map(Path, sys.argv[1:]):
        for path in sorted(d.glob('rep*.json'), key=lambda p: int(p.stem[3:])):
            try:
                data = json.loads(path.read_text() or '{}')
            except json.JSONDecodeError:
                print(f'== {d.name}/{path.stem}: unreadable JSON, a VOID rep\n')
                continue
            reply = str(data.get('result', ''))
            cost = float(data.get('total_cost_usd') or 0)
            total += cost
            aids = [name for name, rx in AIDS.items() if rx.search(reply)]
            iterations = (data.get('usage') or {}).get('iterations')
            kinds = {str(i.get('type')) for i in iterations if isinstance(i, dict)} if isinstance(iterations, list) else set()
            extra = sorted(kinds - {'message'})
            models = len(data.get('modelUsage') or {})
            ran_tool = bool(data) and (data.get('num_turns') != 1 or bool(extra) or models > 1)
            failed = not data or bool(data.get('is_error')) or data.get('subtype', 'success') != 'success'
            void = ' VOID(tool or advisor ran)' if ran_tool else ''
            void += ' VOID(error or budget stop)' if failed else ''
            print(f'== {d.name}/{path.stem}: is_error={data.get("is_error")} subtype={data.get("subtype")} '
                  f'cost=${cost:.3f} turns={data.get("num_turns")} extra-iters={",".join(extra) or "-"} '
                  f'models={models}{void} first={first_line(reply)!r} aids={",".join(aids) or "-"}')
            print(reply)
            print()
    print(f'total cost ${total:.2f}')


if __name__ == '__main__':
    main()
