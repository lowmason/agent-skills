'''Print plan 97 reviewer reps for reading: status, cost, reading aids and the full reply.

Usage, from the repository root: uv run python <kit>/show_reps.py <dir> [<dir> ...]
Each <dir> holds the rep<N>.json copies that run_reps.sh writes. The aids flag replies for the
reader; they are not verdicts. Every verdict is read by hand. A rep is VOID when a tool or the
advisor ran (turns, extra-iters, models), or when it errored or stopped on its budget cap
(is_error, subtype); a VOID rep is rerun and never scored. The printed text goes through
kit_identity.scrub, so no identity form reaches the output.
'''
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit_identity  # noqa: E402

AIDS = {
    # Each aid ignores letter case. An aid only points the reader at a reply; it is never a verdict.
    'revert': re.compile(r'revert', re.I),
    'pre-change': re.compile(r'pre-?change|pre-?fix|old code|original code|buggy code|before the (fix|change|task)'
                             r'|\bat base\b|on base\b', re.I),
    'keeps': re.compile(r'keeps:', re.I),
    'strengthened': re.compile(r'strengthen', re.I),
    'end-date-test': re.compile(r'test_window_includes_end_date', re.I),
    'start-test': re.compile(r'test_window_starts_on_start_date', re.I),
    'not-loaded': re.compile(r'not loaded', re.I),
    'import-error': re.compile(r'ImportError|ModuleNotFoundError', re.I),
    'mar-30': re.compile(r'\b(2026, 3, 30|march 30|mar 30|30th)\b|3-30', re.I),
}


def first_line(text: str) -> str:
    line = next((l for l in text.strip().splitlines() if l.strip()), '')
    return line.strip().strip('`*"\' .').lower()


def main() -> None:
    forms = kit_identity.forms()
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
            print(kit_identity.scrub(
                f'== {d.name}/{path.stem}: is_error={data.get("is_error")} subtype={data.get("subtype")} '
                f'cost=${cost:.3f} turns={data.get("num_turns")} extra-iters={",".join(extra) or "-"} '
                f'models={models}{void} first={first_line(reply)!r} aids={",".join(aids) or "-"}', forms))
            print(kit_identity.scrub(reply, forms))
            print()
    print(f'total cost ${total:.2f}')


if __name__ == '__main__':
    main()
