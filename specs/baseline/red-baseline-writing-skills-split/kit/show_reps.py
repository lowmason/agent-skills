'''Print plan 72 reps for reading: status, cost, ACTION lines, reading aids and the full reply.

Usage, from the repository root: uv run python <kit>/show_reps.py <dir> [<dir> ...]
Each <dir> holds rep<N>.json files from run_reps.sh. The aids flag replies for the reader;
they are not verdicts. Every verdict is read by hand. The header fields turns, extra-iters and
models flag a rep in which a tool or the advisor ran.
'''
import json
import re
import sys
from pathlib import Path

AIDS = {
    'discovery': re.compile(r'discovery\.md'),
    'flowcharts': re.compile(r'flowcharts\.md'),
    'bulletproofing': re.compile(r'bulletproofing\.md'),
    'edit': re.compile(r'^ACTION:.*\b(?:edit|chang|replac|writ|creat|add)', re.I | re.M),
    'use-when': re.compile(r'description:\s*>?\s*["\']?use when', re.I),
    'excuse-table': re.compile(r'\|\s*Excuse\s*\|\s*Reality\s*\|', re.I),
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
            print(f'== {d.name}/{path.stem}: is_error={data.get("is_error")} cost=${cost:.3f} '
                  f'turns={data.get("num_turns")} extra-iters={",".join(extra) or "-"} models={models}'
                  f'{" VOID(tool or advisor ran)" if ran_tool else ""} '
                  f'first={first_line(reply)!r} aids={",".join(aids) or "-"}')
            for line in reply.splitlines():
                if line.startswith('ACTION:'):
                    print(f'   {line}')
            print(reply)
            print()
    print(f'total cost ${total:.2f}')


if __name__ == '__main__':
    main()
