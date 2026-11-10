'''Blind panel and tallies for plan 86's T7 micro-test.

Usage, from the repository root:
  uv run python <kit>/panel.py run --rule <rule.txt> --request <prompt.txt> --out <dir> --votes 3 \
      --seed <int> <arm>=<rep-dir> [<arm>=<rep-dir> ...]
  uv run python <kit>/panel.py tally <out-dir>/panel-verdicts.json [--hand <hand-scores.json>] \
      [--compare <armA> <armB>]
  uv run python <kit>/panel.py selftest

run gathers the reply text of each rep<N>.json in each arm's folder, labels the replies R01 to
Rnn in a shuffled order (one seed for each vote: --seed plus the vote number) and asks one
`claude -p` voter for each vote to score every reply under the rule. The voter sees the rule, the
request and the replies, never the arm, the rep number or any skill text. Each vote writes
vote<k>-input.txt, vote<k>-labels.json (label to <arm>-rep<N>) and vote<k>-output.json.
run then writes panel-verdicts.json: for each <arm>-rep<N>, the votes and the majority.
Each voter runs like run_reps.sh's reps: env -i, no tools, no settings, from a new folder in /tmp.
'''
import argparse
import json
import math
import os
import random
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

KIT = Path(__file__).resolve().parent
HEADER_SOURCE = KIT.parent.parent / 'red-baseline-brainstorming-2026-10-28' / 't7-confirm-panel' / 'vote1-input.txt'
MODEL = 'claude-opus-5-5'
VOTE_BUDGET_USD = '1.00'
Z95 = 1.959963984540054
BAR = 0.8  # a case passes at 4 of 5 (20 of 25) scored reps
KEPT_ENV = ('HOME', 'USER', 'LOGNAME', 'PATH', 'SHELL')


def fisher_one_sided(a_pass: int, a_n: int, b_pass: int, b_n: int) -> float:
    '''One-sided Fisher exact p that arm A's pass rate is above arm B's.

    The upper tail of the hypergeometric: with the margins fixed, the chance that arm A
    holds a_pass or more of the a_pass + b_pass passes.
    '''
    passes, total = a_pass + b_pass, a_n + b_n
    denom = math.comb(total, a_n)
    top = min(passes, a_n)
    return sum(math.comb(passes, k) * math.comb(total - passes, a_n - k)
               for k in range(a_pass, top + 1)) / denom


def wilson(passes: int, n: int) -> tuple[float, float]:
    '''95% Wilson score interval for passes out of n.'''
    p = passes / n
    z2 = Z95 * Z95
    centre = (p + z2 / (2 * n)) / (1 + z2 / n)
    half = Z95 * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / (1 + z2 / n)
    return (centre - half, centre + half)


def gather(arms: list[tuple[str, Path]]) -> dict[str, str]:
    replies = {}
    for arm, folder in arms:
        paths = sorted(folder.glob('rep*.json'), key=lambda p: int(p.stem[3:]))
        if not paths:
            raise SystemExit(f'no rep*.json in {folder}')
        for path in paths:
            replies[f'{arm}-{path.stem}'] = str(json.loads(path.read_text()).get('result', '')).strip()
    return replies


def header(count: int) -> str:
    text = HEADER_SOURCE.read_text()
    head = text[:text.index('=== RULE ===')]
    last = f'R{count:02d}'
    for old, new in (('50 replies labelled R01 to R50', f'{count} replies labelled R01 to {last}'),
                     ('the labels R01 to R50', f'the labels R01 to {last}')):
        if head.count(old) != 1:
            raise SystemExit(f'header source changed: {old!r} not found once')
        head = head.replace(old, new)
    return head


def vote_input(head: str, rule: str, request: str, labelled: list[tuple[str, str]]) -> str:
    parts = [head, '=== RULE ===\n', rule.strip('\n'), '\n=== REQUEST THAT EACH REPLY ANSWERS ===\n',
             request.rstrip('\n'), '\n\n=== REPLIES ===\n\n']
    parts += [f'--- {label} ---\n{reply}\n\n' for label, reply in labelled]
    parts.append('=== END. Output the JSON object now. ===\n')
    return ''.join(parts)


def call_voter(input_text: str) -> dict:
    env = {key: os.environ[key] for key in KEPT_ENV if key in os.environ}
    env |= {'TMPDIR': os.environ.get('TMPDIR', '/tmp'), 'LANG': os.environ.get('LANG', 'en_US.UTF-8'),
            'CLAUDE_CODE_DISABLE_ADVISOR_TOOL': '1', 'CLAUDE_CODE_DISABLE_AUTO_MEMORY': '1'}
    with tempfile.TemporaryDirectory(prefix='plan86-panel-', dir='/tmp') as run_dir:
        done = subprocess.run(
            ['claude', '-p', '--model', MODEL, '--tools', '', '--strict-mcp-config', '--setting-sources', '',
             '--no-session-persistence', '--output-format', 'json', '--max-budget-usd', VOTE_BUDGET_USD],
            input=input_text, capture_output=True, text=True, cwd=run_dir, env=env, check=False)
    try:
        return json.loads(done.stdout)
    except json.JSONDecodeError:
        return {'is_error': True, 'result': '', 'stdout': done.stdout, 'stderr': done.stderr}


def parse_scores(result: str) -> dict[str, list[str]]:
    start, end = result.find('{'), result.rfind('}')
    if start < 0 or end < start:
        return {}
    try:
        return json.loads(result[start:end + 1])
    except json.JSONDecodeError:
        return {}


def majority(votes: list[str]) -> str:
    '''P or F when it holds more than half of all configured votes, missing ones included; else U.'''
    for verdict in ('P', 'F'):
        if 2 * votes.count(verdict) > len(votes):
            return verdict
    return 'U'


def run(args: argparse.Namespace) -> None:
    out = Path(args.out)
    if (out / 'panel-verdicts.json').exists():
        raise SystemExit(f'refusing: {out}/panel-verdicts.json exists')
    arms = []
    for spec in args.arms:
        arm, _, folder = spec.partition('=')
        arms.append((arm, Path(folder)))
    replies = gather(arms)
    keys = list(replies)
    head = header(len(keys))
    rule, request = Path(args.rule).read_text(), Path(args.request).read_text()
    out.mkdir(parents=True, exist_ok=True)
    jobs = []
    for k in range(1, args.votes + 1):
        order = keys[:]
        random.Random(args.seed + k).shuffle(order)
        labels = {f'R{i:02d}': key for i, key in enumerate(order, 1)}
        text = vote_input(head, rule, request, [(label, replies[key]) for label, key in labels.items()])
        (out / f'vote{k}-input.txt').write_text(text)
        (out / f'vote{k}-labels.json').write_text(json.dumps(labels, indent=1) + '\n')
        jobs.append((k, labels, text))
    with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
        outputs = list(pool.map(lambda job: call_voter(job[2]), jobs))
    verdicts = {key: {'votes': [], 'reasons': []} for key in keys}
    cost = 0.0
    for (k, labels, _), output in zip(jobs, outputs):
        (out / f'vote{k}-output.json').write_text(json.dumps(output, indent=1) + '\n')
        cost += float(output.get('total_cost_usd') or 0)
        scores = parse_scores(str(output.get('result', '')))
        for label, key in labels.items():
            verdict, reason = (scores.get(label) or ['-', 'missing'])[:2]
            verdicts[key]['votes'].append(verdict if verdict in ('P', 'F') else '-')
            verdicts[key]['reasons'].append(reason)
    for entry in verdicts.values():
        entry['panel'] = majority(entry['votes'])
    (out / 'panel-verdicts.json').write_text(json.dumps(verdicts, indent=1) + '\n')
    missing = sum(entry['votes'].count('-') for entry in verdicts.values())
    print(f'wrote {out}/panel-verdicts.json: {len(keys)} replies, {args.votes} votes, '
          f'{missing} missing vote(s), cost ${cost:.2f}')


def arm_of(key: str) -> str:
    return key.rsplit('-rep', 1)[0]


def counts(scores: dict[str, str]) -> dict[str, tuple[int, int]]:
    out: dict[str, tuple[int, int]] = {}
    for key, verdict in scores.items():
        passes, n = out.get(arm_of(key), (0, 0))
        out[arm_of(key)] = (passes + (verdict == 'P'), n + 1)
    return out


def meets_bar(passes: int, n: int) -> bool:
    return passes >= math.ceil(BAR * n)


def print_counts(name: str, tallies: dict[str, tuple[int, int]]) -> None:
    for arm, (passes, n) in tallies.items():
        low, high = wilson(passes, n)
        print(f'{name} {arm}: {passes} of {n} ({passes / n:.0%}), Wilson 95% [{low:.2f}, {high:.2f}], '
              f'bar {math.ceil(BAR * n)} {"met" if meets_bar(passes, n) else "missed"}')


def print_compare(name: str, tallies: dict[str, tuple[int, int]], a: str, b: str) -> None:
    (ap, an), (bp, bn) = tallies[a], tallies[b]
    print(f'{name} fisher_one_sided({a}, {b}) = {fisher_one_sided(ap, an, bp, bn):.3f}')
    print(f'{name} fisher_one_sided({b}, {a}) = {fisher_one_sided(bp, bn, ap, an):.3f}')


def tally(args: argparse.Namespace) -> None:
    verdicts = json.loads(Path(args.verdicts).read_text())
    panel = {key: entry['panel'] for key, entry in verdicts.items()}
    unresolved = [key for key, verdict in panel.items() if verdict not in ('P', 'F')]
    if unresolved:
        print(f'no panel majority: {", ".join(unresolved)}')
    panel_counts = counts(panel)
    print_counts('panel', panel_counts)
    hand_counts = {}
    if args.hand:
        hand = json.loads(Path(args.hand).read_text())
        hand = {key: value for key, value in hand.items() if key in panel}
        hand_counts = counts(hand)
        print_counts('hand', hand_counts)
        for key in panel:
            if key in hand and hand[key] != panel[key]:
                print(f'differ {key}: hand {hand[key]}, panel {panel[key]} (votes {"".join(verdicts[key]["votes"])})')
        for arm in panel_counts:
            if arm in hand_counts and meets_bar(*panel_counts[arm]) != meets_bar(*hand_counts[arm]):
                print(f'FLAG {arm}: hand and panel put the arm on different sides of the bar')
    if args.compare:
        a, b = args.compare
        print_compare('panel', panel_counts, a, b)
        if hand_counts:
            print_compare('hand', hand_counts, a, b)


def selftest() -> None:
    assert round(fisher_one_sided(20, 25, 13, 25), 3) == 0.036, fisher_one_sided(20, 25, 13, 25)
    assert round(fisher_one_sided(19, 25, 13, 25), 3) == 0.070, fisher_one_sided(19, 25, 13, 25)
    assert round(fisher_one_sided(13, 25, 12, 25), 3) == 0.5, fisher_one_sided(13, 25, 12, 25)
    assert round(fisher_one_sided(13, 25, 8, 25), 3) == 0.126, fisher_one_sided(13, 25, 8, 25)
    assert tuple(round(x, 2) for x in wilson(13, 25)) == (0.33, 0.70), wilson(13, 25)
    # A majority is more than half of the configured votes; a missing vote ('-') counts against both.
    assert majority(['P', '-', '-']) == 'U', majority(['P', '-', '-'])
    assert majority(['F', '-', '-']) == 'U', majority(['F', '-', '-'])
    assert majority(['P', 'F', '-']) == 'U', majority(['P', 'F', '-'])
    assert majority(['P', 'P', '-']) == 'P', majority(['P', 'P', '-'])
    assert majority(['F', 'F', 'P']) == 'F', majority(['F', 'F', 'P'])
    print('selftest ok')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = parser.add_subparsers(dest='cmd', required=True)
    run_p = sub.add_parser('run')
    run_p.add_argument('--rule', required=True)
    run_p.add_argument('--request', required=True)
    run_p.add_argument('--out', required=True)
    run_p.add_argument('--votes', type=int, default=3)
    run_p.add_argument('--seed', type=int, required=True)
    run_p.add_argument('arms', nargs='+', metavar='<arm>=<rep-dir>')
    tally_p = sub.add_parser('tally')
    tally_p.add_argument('verdicts')
    tally_p.add_argument('--hand')
    tally_p.add_argument('--compare', nargs=2, metavar=('A', 'B'))
    sub.add_parser('selftest')
    args = parser.parse_args()
    {'run': run, 'tally': tally, 'selftest': lambda _: selftest()}[args.cmd](args)


if __name__ == '__main__':
    main()
