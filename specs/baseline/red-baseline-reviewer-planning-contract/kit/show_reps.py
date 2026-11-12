'''Print plan 73 reps for reading: status, cost, reading aids and the full reply.

Usage, from the repository root: uv run python <kit>/show_reps.py <dir> [<dir> ...]
Each <dir> holds rep<N>.json files from run_reps.sh. The aids flag replies for the reader;
they are not verdicts. Every verdict is read by hand. A rep is VOID when a tool or the advisor
ran (turns, extra-iters, models), or when it errored or stopped on its budget cap (is_error,
subtype); a VOID rep is rerun and never scored. The rule is measure.py's `void_reasons`, so
both scripts VOID the same reps; `measure.py selftest` checks that they do.
'''
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from measure import void_reasons  # noqa: E402

AIDS = {
    'minor': re.compile(r'\bminor\b', re.I),
    'nit': re.compile(r'\bnit(?:pick)?s?\b', re.I),
    'recommend': re.compile(r'\brecommendation', re.I),
    'declined': re.compile(r'declined to judge', re.I),
    'plan-block': re.compile(r'<plan\b'),
    'review-focus': re.compile(r'review focus', re.I),
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
            void = ''.join(f' VOID({reason})' for reason in void_reasons(data))
            print(f'== {d.name}/{path.stem}: is_error={data.get("is_error")} subtype={data.get("subtype")} '
                  f'cost=${cost:.3f} turns={data.get("num_turns")} extra-iters={",".join(extra) or "-"} '
                  f'models={models}{void} first={first_line(reply)!r} aids={",".join(aids) or "-"}')
            print(reply)
            print()
    print(f'total cost ${total:.2f}')


if __name__ == '__main__':
    main()
