'''Score plan 73's planner reps and sum the micro-test spend.

Usage, from the repository root:
  uv run python <kit>/measure.py ratio <case> <dir> [<dir> ...]   per rep: plan chars, plan-to-spec ratio, fence share
  uv run python <kit>/measure.py verbatim <dir> [<dir> ...]       per rep: whether each P3 exact text is in the plan
  uv run python <kit>/measure.py spend <root>                     total_cost_usd over every rep*.json under <root>
  uv run python <kit>/measure.py selftest                         checks the parsers on fixed inputs
A rep is VOID, and not scored, when its JSON is unreadable, it errored or stopped on its budget,
a tool or the advisor ran, or its reply has no <plan> block.
'''
import json
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases  # noqa: E402

PLAN_RE = re.compile(r'<plan\b[^>]*>\n?(.*?)</plan>', re.S)
FENCE_RE = re.compile(r'^\s*(```|~~~)')


def plan_text(reply: str) -> str | None:
    match = PLAN_RE.search(reply)
    return match.group(1) if match else None


def fence_share(text: str) -> float:
    '''Fenced lines over all lines; fence marker lines count as fenced, and an unclosed fence runs to the end.'''
    lines = text.split('\n')
    inside, marker, fenced = False, '', 0
    for line in lines:
        match = FENCE_RE.match(line)
        if match and (not inside or match.group(1) == marker):
            fenced += 1
            inside, marker = not inside, match.group(1)
            continue
        fenced += inside
    return fenced / len(lines)


def normalize(text: str) -> str:
    lines = [re.sub(r'^\s*>\s?', '', line) for line in text.split('\n')]
    return ' '.join(' '.join(lines).split())


def load(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text() or '{}')
    except json.JSONDecodeError:
        return None


def rep_reply(path: Path) -> str | None:
    data = load(path)
    if not data or data.get('is_error') or data.get('subtype', 'success') != 'success':
        return None
    iterations = (data.get('usage') or {}).get('iterations') or []
    kinds = {str(i.get('type')) for i in iterations if isinstance(i, dict)}
    if data.get('num_turns') != 1 or kinds - {'message'} or len(data.get('modelUsage') or {}) > 1:
        return None
    return str(data.get('result', ''))


def rep_plan(path: Path) -> str | None:
    reply = rep_reply(path)
    return None if reply is None else plan_text(reply)


def reps(d: Path) -> list[Path]:
    return sorted(d.glob('rep*.json'), key=lambda p: int(p.stem[3:]))


def ratio(case: str, dirs: list[str]) -> None:
    spec_chars = len(cases.CASES[case]['spec'])
    for d in map(Path, dirs):
        ratios, shares = [], []
        for path in reps(d):
            plan = rep_plan(path)
            if plan is None:
                print(f'{d.name}/{path.stem}: VOID')
                continue
            ratios.append(len(plan) / spec_chars)
            shares.append(fence_share(plan))
            print(f'{d.name}/{path.stem}: plan chars {len(plan)} ratio {ratios[-1]:.2f} '
                  f'fence share {shares[-1]:.2f}')
        if ratios:
            print(f'{d.name}: scored {len(ratios)} median ratio {statistics.median(ratios):.2f} '
                  f'median fence share {statistics.median(shares):.2f}')


def verbatim(dirs: list[str]) -> None:
    wanted = [normalize(text) for text in cases.P3_EXACT]
    for d in map(Path, dirs):
        for path in reps(d):
            plan = rep_plan(path)
            if plan is None:
                print(f'{d.name}/{path.stem}: VOID')
                continue
            found = ' '.join(f'text{i}={"yes" if w in normalize(plan) else "no"}' for i, w in enumerate(wanted, 1))
            print(f'{d.name}/{path.stem}: {found}')


def spend(root: str) -> None:
    total = sum(float((load(p) or {}).get('total_cost_usd') or 0) for p in Path(root).rglob('rep*.json'))
    print(f'total ${total:.2f}')


def selftest() -> None:
    assert plan_text('no block here') is None
    assert plan_text('<plan path="a.md">\n# A\n</plan>\nThanks') == '# A\n'
    assert fence_share('a\n```py\nx\n```\nb') == 3 / 5
    assert fence_share('a\n~~~\nx\n~~~') == 3 / 4
    assert fence_share('a\n```\nx\ny') == 3 / 4
    assert normalize('> Run the formatter\n> before you stage.') == 'Run the formatter before you stage.'
    print('selftest passed')


def main() -> None:
    command, args = sys.argv[1], sys.argv[2:]
    if command == 'ratio':
        ratio(args[0], args[1:])
    elif command == 'verbatim':
        verbatim(args)
    elif command == 'spend':
        spend(args[0])
    elif command == 'selftest':
        selftest()
    else:
        raise SystemExit(f'unknown command {command!r}')


if __name__ == '__main__':
    main()
