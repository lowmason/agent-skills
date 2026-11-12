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
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases  # noqa: E402

PLAN_RE = re.compile(r'<plan\b[^>]*>\n?(.*?)</plan>', re.S)
FENCE_RE = re.compile(r'^\s*(`{3,}|~{3,})(.*)$')


def plan_text(reply: str) -> str | None:
    match = PLAN_RE.search(reply)
    return match.group(1) if match else None


def closes(match: re.Match | None, opener: str) -> bool:
    '''A fence closes on a run of the opener's character at least as long as the opener, with no info string.'''
    return bool(match) and match.group(1)[0] == opener[0] and len(match.group(1)) >= len(opener) \
        and not match.group(2).strip()


def fence_share(text: str) -> float:
    '''Fenced lines over all lines; fence marker lines count as fenced, and an unclosed fence runs to the end.'''
    lines = text.split('\n')
    opener, fenced = '', 0
    for line in lines:
        match = FENCE_RE.match(line)
        if opener:
            fenced += 1
            opener = '' if closes(match, opener) else opener
        elif match:
            fenced += 1
            opener = match.group(1)
    return fenced / len(lines)


def normalize(text: str) -> str:
    lines = [re.sub(r'^\s*>\s?', '', line) for line in text.split('\n')]
    return ' '.join(' '.join(lines).split())


def load(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text() or '{}')
    except json.JSONDecodeError:
        return None


def void_reasons(data: dict) -> list[str]:
    '''Why a rep is VOID, or [] when it scores. The one VOID rule: show_reps.py imports it.'''
    reasons = []
    if data:
        iterations = (data.get('usage') or {}).get('iterations')
        kinds = {str(i.get('type')) for i in iterations if isinstance(i, dict)} if isinstance(iterations, list) else set()
        if data.get('num_turns') != 1 or kinds - {'message'} or len(data.get('modelUsage') or {}) > 1:
            reasons.append('tool or advisor ran')
    if not data or data.get('is_error') or data.get('subtype', 'success') != 'success':
        reasons.append('error or budget stop')
    return reasons


def rep_reply(path: Path) -> str | None:
    data = load(path)
    if data is None or void_reasons(data):
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
    assert fence_share('a\n````md\n```py\nx\n```\n````\nb') == 5 / 7  # an inner fence does not close the outer one
    assert fence_share('a\n```\nx\n```py\ny\n```') == 5 / 6          # a closing fence carries no info string
    assert normalize('> Run the formatter\n> before you stage.') == 'Run the formatter before you stage.'
    void_selftest()
    print('selftest passed')


def void_selftest() -> None:
    '''measure.py and show_reps.py share one VOID rule, and both apply it to the same reps.'''
    ok = {'subtype': 'success', 'num_turns': 1, 'result': '<plan>\nx\n</plan>',
          'usage': {'iterations': [{'type': 'message'}]}, 'modelUsage': {'claude-opus-5-5': {}}}
    tool, budget = 'tool or advisor ran', 'error or budget stop'
    cases = {
        'ok': (ok, []),
        'turns': ({**ok, 'num_turns': 2}, [tool]),
        'advisor': ({**ok, 'usage': {'iterations': [{'type': 'message'}, {'type': 'advisor_message'}]}}, [tool]),
        'models': ({**ok, 'modelUsage': {'claude-opus-5-5': {}, 'claude-haiku-5-5': {}}}, [tool]),
        'error': ({**ok, 'is_error': True}, [budget]),
        'budget': ({**ok, 'subtype': 'error_max_budget_usd'}, [budget]),
        'both': ({**ok, 'num_turns': 3, 'is_error': True}, [tool, budget]),
        'empty': ({}, [budget]),
    }
    for name, (data, want) in cases.items():
        assert void_reasons(data) == want, (name, void_reasons(data))
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        for n, (data, _) in enumerate(cases.values(), 1):
            (d / f'rep{n}.json').write_text(json.dumps(data))
        (d / f'rep{len(cases) + 1}.json').write_text('{not json')
        shown = subprocess.run([sys.executable, str(Path(__file__).with_name('show_reps.py')), str(d)],
                               capture_output=True, text=True, check=True).stdout
        headers = dict(re.findall(r'^== \S+/(rep\d+):(.*)$', shown, re.M))
        for path in reps(d):
            assert (rep_reply(path) is None) == ('VOID' in headers[path.stem]), (path.stem, headers[path.stem])


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
