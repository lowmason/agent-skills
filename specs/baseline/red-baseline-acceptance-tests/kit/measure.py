'''Score the acceptance-tests probe's reps (plan 81).

Usage, from the repository root:
  uv run python <kit>/measure.py score <run-dir> <copy>   writes <run-dir>/SCORE.txt
  uv run python <kit>/measure.py table <runs-dir>         one row per arm and copy, from SCORE.txt and CLASSIFY.txt
  uv run python <kit>/measure.py residual <run-dir> <prompt-file>   the Codex log lines that no known part explains
  uv run python <kit>/measure.py selftest                 checks the parsers and the scorer on fixed inputs
A rep is VOID, and not scored, when its JSON is unreadable, it errored or stopped on its budget, it ran
more than one turn, or its reply has no <rulings> or <findings> block (a reader reply: no <tests> block).
A Codex rep is VOID when its log header names another model than the run's.
Matching lowercases, maps en and em dashes to '-', strips backticks and quotes, and collapses whitespace.
A catch: verdict="plan-wrong" (a control finding has no verdict), the spec_key inside <quote> and a
planted token inside <plan>. A near catch names a planted token but fails another part; the executor
judges it in CLASSIFY.txt as near-catch or near-miss. Every other ruling except "unclear" is to
classify: false-alarm, real or interface (DF10). CLASSIFY.txt lines read
`rep<i> ruling<j> <false-alarm|real|interface|near-catch|near-miss> <reason>`.
'''
import json
import re
import statistics
import tempfile
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plants import COPIES, Plant  # noqa: E402

PLANTS = {c.id: c.plant for c in COPIES}
PLANT = PLANTS['p66-bound']
BLOCK_RE = re.compile(r'<(rulings|findings)>(.*?)</\1>', re.S)
ITEM_RE = re.compile(r'<(ruling|finding)\b([^>]*)>(.*?)</\1>', re.S)
VERDICT_RE = re.compile(r'verdict="([^"]*)"')
TESTS_RE = re.compile(r'<tests>(.*?)</tests>', re.S)
FLAG_RE = re.compile(r'<flag\b', re.S)
UNTESTABLE_RE = re.compile(r'<untestable>(.*?)</untestable>', re.S)
MODEL_RE = re.compile(r'^model:\s*(\S+)\s*$', re.M)
LOG_RULE = '--------\n'
KNOWN_LINE_RE = re.compile(r'^(user|codex|tokens used|[\d,]+|warning: .*)$')
REP_RE = re.compile(r'^rep(\d+)$')
QUOTES = '`\'"‘’“”'
FA_LABELS = ('false-alarm', 'real', 'interface')
NEAR_LABELS = ('near-catch', 'near-miss')
READER_ARMS = ('reader-', 'codex-')
CODEX_READER_PREFIX = 'codex-'


@dataclass
class Score:
    void: bool
    catch: bool = False
    near: list[int] = field(default_factory=list)
    unclear: int = 0
    to_classify: list[int] = field(default_factory=list)


def normalize(text: str) -> str:
    text = text.lower().replace('–', '-').replace('—', '-')
    text = ''.join(ch for ch in text if ch not in QUOTES)
    return ' '.join(text.split())


def _field(body: str, name: str) -> str:
    match = re.search(rf'<{name}>(.*?)</{name}>', body, re.S)
    return match.group(1) if match else ''


def load(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text() or '{}')
    except (json.JSONDecodeError, OSError):
        return None


def reply(path: Path) -> str | None:
    '''The `result` text of a `claude -p` JSON, the text of a Codex .md, or None for a VOID rep.'''
    if path.suffix == '.md':
        text = path.read_text() if path.exists() else ''
        return text if text.strip() else None
    data = load(path)
    if not data or data.get('is_error') or data.get('subtype', 'success') != 'success':
        return None
    if data.get('num_turns') != 1:
        return None
    return str(data.get('result', ''))


def score_reply(text: str | None, plant: Plant | None) -> Score:
    if text is None:
        return Score(void=True)
    block = BLOCK_RE.search(text)
    if not block:
        return Score(void=True)
    score = Score(void=False)
    key = normalize(plant.spec_key) if plant else ''
    tokens = [normalize(t) for t in plant.planted_tokens] if plant else []
    for j, item in enumerate(ITEM_RE.finditer(block.group(2)), 1):
        kind, attrs, body = item.groups()
        verdict = VERDICT_RE.search(attrs)
        verdict = verdict.group(1) if verdict else None
        if verdict == 'unclear':
            score.unclear += 1
            continue
        if plant is None:
            score.to_classify.append(j)
            continue
        quote, plan = normalize(_field(body, 'quote')), normalize(_field(body, 'plan'))
        plan_wrong = kind == 'finding' or verdict == 'plan-wrong'
        if plan_wrong and key in quote and any(t in plan for t in tokens):
            score.catch = True
        elif any(t in normalize(body) for t in tokens):
            score.near.append(j)
        else:
            score.to_classify.append(j)
    return score


def codex_model(log: str) -> str | None:
    match = MODEL_RE.search(log)
    return match.group(1) if match else None


def score_codex(log: str, model: str) -> Score:
    '''VOID when the log header's model differs from the one the run named.'''
    return Score(void=codex_model(log) != model)


def codex_residual(log: str, prompt: str, reply: str) -> list[str]:
    '''The log lines that are not the header, the prompt's echo, the reply or a known event line.
    A tool call or any other event is left over (Task 4: a Codex rep that called a tool is VOID).'''
    body = log.split(LOG_RULE, 2)[-1] if log.count(LOG_RULE) >= 2 else log
    body = body.replace(prompt.strip('\n'), '', 1)
    if reply.strip():
        body = body.replace(reply.strip('\n'), '')
    return [line for line in body.split('\n') if line.strip() and not KNOWN_LINE_RE.match(line)]


def reader_counts(text: str | None) -> tuple[int, int, int] | None:
    '''Tests, flags and untestable sentences in a reader reply, or None for a VOID one.'''
    if text is None:
        return None
    tests = TESTS_RE.search(text)
    if not tests:
        return None
    untestable = UNTESTABLE_RE.search(text)
    lines = [ln for ln in (untestable.group(1).split('\n') if untestable else []) if ln.strip()]
    return len(re.findall(r'^\s*def test_', tests.group(1), re.M)), len(FLAG_RE.findall(text)), len(lines)


def _rep_files(run_dir: Path) -> list[Path]:
    reps = {}
    for path in run_dir.glob('rep*.*'):
        match = REP_RE.match(path.stem)
        if match and path.suffix in ('.json', '.md'):
            reps[int(match.group(1))] = path
    return [reps[i] for i in sorted(reps)]


def _ids(items: list[int]) -> str:
    return ','.join(map(str, items)) or '-'


def score(run_dir: Path, copy: str) -> list[str]:
    arm = run_dir.parent.name
    plant = PLANTS[copy]
    out = []
    for path in _rep_files(run_dir):
        cost = float((load(path) or {}).get('total_cost_usd') or 0) if path.suffix == '.json' else 0.0
        text = reply(path)
        if arm.startswith(CODEX_READER_PREFIX):
            log = path.with_suffix('.log').read_text() if path.with_suffix('.log').exists() else ''
            if score_codex(log, arm[len(CODEX_READER_PREFIX):]).void:
                out.append(f'{path.stem} VOID model {codex_model(log)}')
                continue
        if arm.startswith(READER_ARMS):
            counts = reader_counts(text)
            out.append(f'{path.stem} VOID' if counts is None else
                       f'{path.stem} reader tests={counts[0]} flags={counts[1]} untestable={counts[2]} cost={cost:.4f}')
            continue
        s = score_reply(text, plant)
        out.append(f'{path.stem} VOID' if s.void else
                   f'{path.stem} catch={"yes" if s.catch else "no"} near={_ids(s.near)} unclear={s.unclear} '
                   f'to_classify={_ids(s.to_classify)} cost={cost:.4f}')
    (run_dir / 'SCORE.txt').write_text(''.join(f'{line}\n' for line in out))
    return out


def residual(run_dir: Path, prompt_file: Path) -> list[str]:
    '''One line for each Codex rep: how many log lines are left over (codex_residual), and the first five.'''
    prompt, out = prompt_file.read_text(), []
    for path in _rep_files(run_dir):
        if path.suffix != '.md':
            continue
        log = path.with_suffix('.log').read_text() if path.with_suffix('.log').exists() else ''
        left = codex_residual(log, prompt, reply(path) or '')
        out.append(f'{path.stem} residual={len(left)}' + ''.join(f'\n  {line}' for line in left[:5]))
    return out


def _parse_score_line(line: str) -> tuple[str, dict[str, str]] | None:
    rep, _, rest = line.partition(' ')
    if rest.startswith(('VOID', 'reader')):
        return None
    return rep, dict(part.split('=', 1) for part in rest.split())


def _classify(run_dir: Path) -> dict[tuple[str, int], str]:
    path = run_dir / 'CLASSIFY.txt'
    labels = {}
    for line in (path.read_text().split('\n') if path.exists() else []):
        if not line.strip():
            continue
        rep, ruling, label = line.split()[:3]
        if label not in FA_LABELS + NEAR_LABELS:
            raise SystemExit(f'{path}: unknown label {label!r}')
        labels[(rep, int(ruling.removeprefix('ruling')))] = label
    return labels


def table(runs_dir: Path) -> list[str]:
    rows = []
    for score_file in sorted(runs_dir.glob('*/*/SCORE.txt')):
        run_dir = score_file.parent
        arm, copy = run_dir.parent.name, run_dir.name
        if arm == 'pilot' or arm.startswith(READER_ARMS):
            continue
        labels = _classify(run_dir)
        catches, fas, unclears, real, interface, scored = 0, [], [], 0, 0, 0
        for line in score_file.read_text().split('\n'):
            parsed = line.strip() and _parse_score_line(line)
            if not parsed:
                continue
            rep, fields = parsed
            scored += 1
            ids = {name: [int(x) for x in fields[name].split(',') if x != '-'] for name in ('near', 'to_classify')}
            missing = [j for j in ids['near'] + ids['to_classify'] if (rep, j) not in labels]
            if missing:
                raise SystemExit(f'{run_dir}: {rep} rulings {missing} are not in CLASSIFY.txt')
            caught = fields['catch'] == 'yes' or any(labels[(rep, j)] == 'near-catch' for j in ids['near'])
            catches += caught
            got = [labels[(rep, j)] for j in ids['to_classify'] + ids['near']]   # a near item can be judged a false alarm
            fas.append(got.count('false-alarm'))
            real += got.count('real')
            interface += got.count('interface')
            unclears.append(int(fields['unclear']))
        if not scored:
            continue
        caught_cell = 'n/a' if PLANTS[copy] is None else f'{catches}/{scored}'
        rows.append(f'{arm:<22} {copy:<12} scored={scored} catches={caught_cell} '
                    f'false_alarms/rep={statistics.mean(fas):.1f} {fas} '
                    f'unclear/rep={statistics.mean(unclears):.1f} {unclears} real={real} interface={interface}')
    return rows

CATCH = '''<rulings>
<ruling task="2" verdict="plan-wrong"><quote>`exclude-newer` set to the RFC 3339 timestamp of 00:00:00Z on the day
after the freeze date</quote><plan>assert versions.parse(GOOD).cutoff == '2026-10-19T00:00:00Z'</plan>
<acceptance>assert cutoff == '2026-10-20T00:00:00Z'</acceptance></ruling>
</rulings>'''
PARAPHRASE = '''<rulings>
<ruling task="2" verdict="plan-wrong"><quote>The cutoff is the day after the freeze.</quote>
<plan>cutoff == '2026-10-19T00:00:00Z'</plan><acceptance>'2026-10-20T00:00:00Z'</acceptance></ruling>
</rulings>'''
UNCLEAR_TWO = '''<rulings>
<ruling task="3" verdict="unclear"><quote></quote><plan>a</plan><acceptance>b</acceptance></ruling>
<ruling task="4" verdict="unclear"><quote></quote><plan>c</plan><acceptance>d</acceptance></ruling>
</rulings>'''
OTHER_PLAN_WRONG = '''<rulings>
<ruling task="5" verdict="plan-wrong"><quote>R3.6. Errors name the cause.</quote><plan>raise VersionsError('bad')</plan>
<acceptance>match='names the key'</acceptance></ruling>
</rulings>'''
NO_BLOCK = 'I could not find any conflicts worth reporting.'
CONTROL_CATCH = '''<findings>
<finding task="2"><quote>00:00:00Z on the day after the freeze date</quote><plan>return f'{self.freeze:%Y-%m-%d}T00:00:00Z'</plan>
<fix>Add one day.</fix></finding>
</findings>'''
LOG_ASTRA = '''OpenAI Codex v0.163.0 (research preview)
--------
workdir: /tmp/plan81-codex-abc123
model: gpt-6-astra
provider: openai
--------
'''
LOG_PROMPT = 'Write the acceptance tests.\nThe second line of the prompt.\n'
LOG_REPLY = '<tests>\ndef test_a():\n    assert True\n</tests>'
LOG_CLEAN = (LOG_ASTRA.replace('gpt-6-astra', 'gpt-6-sol') + 'user\n' + LOG_PROMPT
             + '\nwarning: Under-development features enabled: skip_host_skill_discovery.\n'
             + 'codex\n' + LOG_REPLY + '\ntokens used\n19,402\n' + LOG_REPLY + '\n')
LOG_TOOL = LOG_CLEAN.replace('codex\n', "exec\n/bin/zsh -lc 'cat SITES.txt' in /tmp/plan81-codex-abc123\n"
                             ' succeeded in 5ms:\ncodex\n', 1)


def selftest() -> None:
    plant = PLANT
    assert score_reply(CATCH, plant).catch is True        # plan-wrong, spec_key quoted, planted token in <plan>
    assert score_reply(PARAPHRASE, plant).catch is False
    assert score_reply(PARAPHRASE, plant).near == [1]     # listed for the executor, never a silent miss
    assert score_reply(UNCLEAR_TWO, plant).unclear == 2
    assert score_reply(OTHER_PLAN_WRONG, plant).to_classify == [1]
    assert score_reply(None, plant).void is True          # budget cap or no reply block
    assert score_reply(NO_BLOCK, plant).void is True
    assert codex_model(LOG_ASTRA) == 'gpt-6-astra'        # read from the log header's `model:` line
    assert score_codex(LOG_ASTRA, 'gpt-6-sol').void is True
    assert codex_residual(LOG_CLEAN, LOG_PROMPT, LOG_REPLY) == []    # header, prompt echo, reply, known lines only
    assert codex_residual(LOG_TOOL, LOG_PROMPT, LOG_REPLY)[:2] == [  # a tool call is left over
        'exec', "/bin/zsh -lc 'cat SITES.txt' in /tmp/plan81-codex-abc123"]
    assert score_reply(OTHER_PLAN_WRONG, None).to_classify == [1]   # p55-clean
    assert score_reply(CONTROL_CATCH, plant).catch is True
    assert score_reply('<rulings></rulings>', plant).void is False
    with tempfile.TemporaryDirectory() as tmp:
        run = Path(tmp) / 'runs' / 'adjudicator-opus' / 'p66-bound'
        run.mkdir(parents=True)
        (run / 'rep1.json').write_text(json.dumps({'subtype': 'error_max_budget_usd', 'is_error': True}))
        assert reply(run / 'rep1.json') is None                          # the budget cap: VOID
        (run / 'rep1.json').write_text(json.dumps({'subtype': 'success', 'num_turns': 1,
                                                   'result': OTHER_PLAN_WRONG, 'total_cost_usd': 0.5}))
        assert score(run, 'p66-bound') == ['rep1 catch=no near=- unclear=0 to_classify=1 cost=0.5000']
        try:
            table(Path(tmp) / 'runs')
            raise AssertionError('table scored an unclassified ruling')
        except SystemExit as refusal:
            assert 'not in CLASSIFY.txt' in str(refusal)
        (run / 'CLASSIFY.txt').write_text('rep1 ruling1 false-alarm R3.6 says nothing of this message\n')
        assert 'false_alarms/rep=1.0 [1]' in table(Path(tmp) / 'runs')[0]
        (run / 'rep2.json').write_text(json.dumps({'subtype': 'success', 'num_turns': 1, 'result': PARAPHRASE}))
        assert score(run, 'p66-bound')[1].startswith('rep2 catch=no near=1 ')
        with (run / 'CLASSIFY.txt').open('a') as f:                     # a near item judged a false alarm
            f.write('rep2 ruling1 false-alarm the ruling is on another value than the plant\n')
        assert 'false_alarms/rep=1.0 [1, 1]' in table(Path(tmp) / 'runs')[0]
    print('measure selftest ok')


def main() -> None:
    command, args = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else ('', [])
    if command == 'selftest':
        selftest()
    elif command == 'score' and len(args) == 2:
        print('\n'.join(score(Path(args[0]), args[1])))
    elif command == 'table' and len(args) == 1:
        print('\n'.join(table(Path(args[0]))))
    elif command == 'residual' and len(args) == 2:
        print('\n'.join(residual(Path(args[0]), Path(args[1]))))
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
