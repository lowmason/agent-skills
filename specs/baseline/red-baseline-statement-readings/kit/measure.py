'''Score the statement-readings probe's reps (plan 83), rewritten from plan 81's measure.py.

Usage, from the repository root:
  uv run python <kit>/measure.py score <runs-dir> <arm> <copy-or-spec-id>   writes SCORE.txt; a step arm also
                                                                           writes results/rep<k>.json
  uv run python <kit>/measure.py table <runs-dir>      one row per arm and copy, the bar lines and the PD9 line
  uv run python <kit>/measure.py residual <run-dir> <prompt-file>   the Codex log lines that no known part explains
  uv run python <kit>/measure.py selftest
A rep is VOID (PD6), and never a miss, when its JSON is unreadable (`unreadable`), it errored (`error`) or
stopped on its budget (`budget`), it ran more than one turn (`turns`), or its reply lacks the closing tag of its
block (`no-block`). A Claude rep whose modelUsage names a second model is VOID (`model`). A Codex rep is VOID
when its log names another model (`model`), or shows a line that is not the header, the prompt, the reply or
a known status line (`residual`): plan 81's residual check runs inside the VOID check (the watch item at
specs/deferred_items.md:6103). An adjudicator rep is also VOID when a case has no ruling or a ruling names no
case (`cases`). The arm's prefix picks the kind of rep: reader-, standin-, control- or step-.
Tokens (PD10) are matched in flattened text: on an argued plant, in the four slots joined; on a two-reading
plant, as a whole word in its one slot. CLASSIFY.txt lines read `rep<k> <outcome|finding|fidelity><j> <label>
<reason>` (PD11): false-alarm or real for a p55-clean conflict (DF-AMEND: an `amendment:` reason), ambiguous
or false for a p55-clean unclear case, near-catch or near-miss for a near catch, and faithful, spec-value or
other for an unmatched fidelity. Outcome indices count from 0, in a step rep's results/rep<k>.json order;
finding indices count from 1, in the reply's order. `table` counts a near-catch as a catch, as plan 81's did.
'''
import json
import re
import statistics
import sys
import tempfile
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compare import (Entry, Outcome, Slots, check_quotes, normalize_slot, parse_rulings, parse_statement,  # noqa: E402
                     phase_from_json, resolve)
from make_copies import amended_sentences, planted_sentence  # noqa: E402
from number import flatten, number  # noqa: E402
from plants import COPIES, Copy  # noqa: E402

KIT = Path(__file__).resolve().parent
REPO = KIT.parents[2]
COPIES_DIR = KIT.parent / 'copies'
REPS = 5
BAR_CATCHES = 4
BAR_CONTROL = 2
BAR_MEAN = 1.0
CLEAN = 'p55-clean'
TREATMENT_PREFIX = 'step-pair-'
CLAUDE_ARM = 'step-claude'
PD9_MODEL = 'gpt-6-sol'
MIN_PLAN_QUOTE = 8
BLOCK_TAGS = ('statement', 'rulings', 'findings')
FINDINGS_RE = re.compile(r'<findings>(.*?)</findings>', re.S)
FINDING_RE = re.compile(r'<finding\b([^>]*)>(.*?)</finding>', re.S)
MODEL_RE = re.compile(r'^model:\s*(\S+)\s*$', re.M)
TOKENS_RE = re.compile(r'^tokens used\n([\d,]+)$', re.M)
LOG_RULE = '--------\n'
KNOWN_LINE_RE = re.compile(r'^(user|codex|tokens used|[\d,]+|warning: .*)$')
REP_RE = re.compile(r'^rep(\d+)$')
CLASSIFY_RE = re.compile(r'^(rep\d+)\s+(outcome|finding|fidelity)(\d+)\s+(\S+)\s*(.*)$')
LABELS = {'conflict': ('false-alarm', 'real'), 'unclear': ('ambiguous', 'false'),
          'near': ('near-catch', 'near-miss'), 'fidelity': ('faithful', 'spec-value', 'other')}
AMENDMENT = 'amendment:'


@dataclass
class StepScore:
    catch: bool
    near: list[int]
    conflict_on_plant: bool
    conflicts: int
    unclear: int
    missing: int
    unchecked: int
    skipped: int
    returned: int
    returned_on_plant: bool
    miss_reason: str


def load(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) and data else None


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


def codex_model(log: str) -> str | None:
    match = MODEL_RE.search(log)
    return match.group(1) if match else None


def codex_residual(log: str, prompt: str, reply_text: str) -> list[str]:
    '''The log lines that are not the header, the prompt's echo, the reply or a known event line (plan 81).'''
    body = log.split(LOG_RULE, 2)[-1] if log.count(LOG_RULE) >= 2 else log
    body = body.replace(prompt.strip('\n'), '', 1)
    if reply_text.strip():
        body = body.replace(reply_text.strip('\n'), '')
    return [line for line in body.split('\n') if line.strip() and not KNOWN_LINE_RE.match(line)]


def _complete(text: str, kind: str) -> bool:
    return re.search(rf'<{kind}>.*?</{kind}>', text, re.S) is not None


def void_reason(path: Path, kind: str, model: str | None = None, prompt: str | None = None) -> str | None:
    '''None for a scored rep, or the reason it is VOID (PD6).'''
    if path.suffix == '.md':
        text = path.read_text() if path.exists() else ''
        log_path = path.with_suffix('.log')
        log = log_path.read_text() if log_path.exists() else ''
        if model is not None and codex_model(log) != model:
            return 'model'
        if prompt is not None and codex_residual(log, prompt, text):
            return 'residual'
        if not text.strip():
            return 'error'
        return None if _complete(text, kind) else 'no-block'
    data = load(path)
    if data is None:
        return 'unreadable'
    if data.get('subtype') == 'error_max_budget_usd':
        return 'budget'
    if data.get('is_error') or data.get('subtype', 'success') != 'success':
        return 'error'
    if data.get('num_turns') != 1:
        return 'turns'
    if len(data.get('modelUsage') or {}) > 1:
        return 'model'
    return None if _complete(str(data.get('result', '')), kind) else 'no-block'


def _rep_files(run_dir: Path) -> list[Path]:
    reps = {}
    for path in run_dir.glob('rep*.*'):
        match = REP_RE.match(path.stem)
        if match and path.suffix in ('.json', '.md'):
            reps[int(match.group(1))] = path
    return [reps[k] for k in sorted(reps)]


def scored_reps(run_dir: Path, kind: str, model: str | None = None, prompt: str | None = None) -> list[Path]:
    '''The first five scored reps, in rep order. A renamed VOID reply, rep<k>.void<j>.json, is skipped.'''
    return [p for p in _rep_files(run_dir) if void_reason(p, kind, model, prompt) is None][:REPS]


def _joined(slots: Slots | None) -> str:
    return '' if slots is None else flatten(' '.join((slots.value, slots.unit, slots.edge, slots.default)))


def _has(slots: Slots | None, tokens: tuple[str, ...]) -> bool:
    '''An argued plant's token occurs in the four slots joined.'''
    text = _joined(slots)
    return any(token in text for token in tokens)


def _has_word(slots: Slots | None, slot: str, tokens: tuple[str, ...]) -> bool:
    '''A two-reading plant's token occurs as a whole word in its one slot.'''
    text = '' if slots is None else flatten(getattr(slots, slot))
    return any(re.search(rf'(?<![\w.]){re.escape(token)}(?![\w.])', text) for token in tokens)


def score_step(outcomes: list[Outcome], copy: Copy, planted_n: int | None, listed: bool | None = None) -> StepScore:
    '''One step rep. A catch on an argued plant is a plan-conflict on the planted sentence whose agreed reading
    holds a spec token and no plant token, and whose planner slots hold a plant token. A catch on a two-reading
    plant is an unclear outcome on the planted sentence. `listed` says whether any reader listed the planted
    sentence, to tell `agreed` from `absent` when no outcome falls on it.'''
    on = [(i, o) for i, o in enumerate(outcomes) if planted_n is not None and o.sentence == planted_n]
    kinds = Counter(o.kind for o in outcomes)
    catch, near = False, []
    if copy.plant is not None:
        for i, o in on:
            if (o.kind == 'plan-conflict' and _has(o.agreed, copy.plant.spec_tokens)
                    and not _has(o.agreed, copy.plant.plant_tokens) and _has(o.planner, copy.plant.plant_tokens)):
                catch = True
            elif o.kind in ('plan-conflict', 'unclear'):
                near.append(i)
    elif copy.two is not None:
        catch = any(o.kind == 'unclear' for _, o in on)
    on_kinds = {o.kind for _, o in on}
    if (copy.plant is None and copy.two is None) or catch:
        reason, near = '', []
    elif 'returned' in on_kinds:
        reason = 'returned'
    elif 'amended-skip' in on_kinds:
        reason = 'amended'
    elif on_kinds & {'missing', 'unchecked'} or (not on and listed is False):
        reason = 'absent'
    elif not on:
        reason = 'agreed'
    else:
        reason = 'other'
    return StepScore(catch, near, 'plan-conflict' in on_kinds, kinds['plan-conflict'], kinds['unclear'],
                     kinds['missing'], kinds['unchecked'], kinds['amended-skip'], kinds['returned'],
                     'returned' in on_kinds, reason)


def fidelity(planner: list[Entry], copy: Copy, planted_n: int) -> str:
    '''The stand-in's outcome on the planted sentence (PD10): the first of amended, absent, faithful, spec value
    (argued plants), other (two-reading plants) and unmatched that applies.'''
    on = [e for e in planner if e.sentence == planted_n]
    if any(normalize_slot(e.amended) != 'none' for e in on):
        return 'amended'
    if not on:
        return 'absent'
    if copy.plant is not None:
        planted = any(_has(e.slots, copy.plant.plant_tokens) for e in on)
        spec = any(_has(e.slots, copy.plant.spec_tokens) for e in on)
        if planted and not spec:
            return 'faithful'
        if spec and not planted:
            return 'spec value'
    else:
        a = any(_has_word(e.slots, copy.two.slot, copy.two.a_tokens) for e in on)
        b = any(_has_word(e.slots, copy.two.slot, copy.two.b_tokens) for e in on)
        if a and not b:
            return 'faithful'
        if b and not a:
            return 'other'
    return 'unmatched'


def amend_marks(planner: list[Entry], amended: set[int]) -> tuple[int, int]:
    '''The entries on a key sentence without a mark, and the marked entries off the key.'''
    marked = [normalize_slot(e.amended) != 'none' for e in planner]
    return (sum(1 for e, m in zip(planner, marked) if e.sentence in amended and not m),
            sum(1 for e, m in zip(planner, marked) if e.sentence not in amended and m))


def _ids(items) -> str:
    return ','.join(map(str, items)) or '-'


def _yn(flag: bool) -> str:
    return 'yes' if flag else 'no'


def step_line(rep: str, s: StepScore, label_conflict: list[int], label_unclear: list[int], amended_ids: list[int],
              cost: float) -> str:
    return (f'{rep} catch={_yn(s.catch)} near={_ids(s.near)} conflict_on_plant={_yn(s.conflict_on_plant)} '
            f'conflicts={s.conflicts} unclear={s.unclear} missing={s.missing} unchecked={s.unchecked} '
            f'skipped={s.skipped} returned={s.returned} returned_on_plant={_yn(s.returned_on_plant)} '
            f'miss={s.miss_reason or "-"} to_label_conflict={_ids(label_conflict)} '
            f'to_label_unclear={_ids(label_unclear)} amended_sentence={_ids(amended_ids)} cost={cost:.4f}')


def _copy(copy_id: str) -> Copy:
    return next(c for c in COPIES if c.id == copy_id)


def _spec_sentences(ident: str):
    '''The numbered sentences of a copy, or of the first copy with that spec id.'''
    copy = next(c for c in COPIES if ident in (c.id, c.spec_id))
    return copy, number((COPIES_DIR / copy.id / 'spec.md').read_text())


def _cost(path: Path) -> str:
    if path.suffix == '.md':
        log = path.with_suffix('.log')
        found = TOKENS_RE.findall(log.read_text()) if log.exists() else []
        return f'tokens={found[-1].replace(",", "") if found else 0}'
    return f'cost={float((load(path) or {}).get("total_cost_usd") or 0):.4f}'


def _score_reader(runs_dir: Path, run_dir: Path, arm: str, spec_id: str) -> list[str]:
    model = arm.removeprefix('reader-')
    _copy_, sentences = _spec_sentences(spec_id)
    by_n = {s.n: s.text for s in sentences}
    prompt_file = runs_dir / 'prompts' / f'reader-{spec_id}.txt'
    out = []
    for path in _rep_files(run_dir):
        codex = path.suffix == '.md'
        prompt = prompt_file.read_text() if codex else None
        reason = void_reason(path, 'statement', model if codex else None, prompt)
        if reason:
            out.append(f'{path.stem} VOID {reason}')
            continue
        entries = parse_statement(reply(path))
        returned = check_quotes(entries, by_n)[1]
        out.append(f'{path.stem} entries={len(entries)} other={sum(e.other is not None for e in entries)} '
                   f'returned={len(returned)} {_cost(path)}')
    return out


def _score_standin(run_dir: Path, copy_id: str) -> list[str]:
    copy, sentences = _spec_sentences(copy_id)
    by_n = {s.n: s.text for s in sentences}
    planted_n = planted_sentence(copy, sentences).n if (copy.plant or copy.two) else None
    amended = amended_sentences(copy, sentences)
    out, notes = [], []
    for path in _rep_files(run_dir):
        reason = void_reason(path, 'statement')
        if reason:
            out.append(f'{path.stem} VOID {reason}')
            continue
        entries = parse_statement(reply(path))
        fid = fidelity(entries, copy, planted_n) if planted_n else 'n/a'
        missing, extra = amend_marks(entries, amended)
        noted = [e for e in entries if e.note.strip()]
        notes += [f'{path.stem} S{e.sentence}: {" ".join(e.note.split())}' for e in noted]
        out.append(f'{path.stem} fidelity={fid.replace(" ", "-")} amended_missing={missing} amended_extra={extra} '
                   f'entries={len(entries)} returned={len(check_quotes(entries, by_n)[1])} notes={len(noted)} '
                   f'notes_on_plant={sum(e.sentence == planted_n for e in noted)} {_cost(path)}')
    (run_dir / 'NOTES.txt').write_text(''.join(f'{line}\n' for line in notes))
    return out


def control_score(text: str, copy: Copy, plan: str) -> tuple[bool, list[int], int]:
    '''Plan 81's catch rule on an argued plant. On a two-reading plant (PD10): a finding whose <quote> holds the
    edit's spec_key is a catch, and one whose <plan> text comes from one of the edit's plan lines is near.'''
    block = FINDINGS_RE.search(text)
    catch, near, count = False, [], 0
    lines = plan.split('\n')
    for j, (_attrs, body) in enumerate(FINDING_RE.findall(block.group(1) if block else ''), 1):
        count += 1
        quote = flatten(_tag(body, 'quote'))
        plan_text = flatten(_tag(body, 'plan'))
        if copy.plant is not None:
            tokens = [flatten(t) for t in copy.plant.planted_tokens]
            if flatten(copy.plant.spec_key) in quote and any(t in plan_text for t in tokens):
                catch = True
            elif any(t in flatten(body) for t in tokens):
                near.append(j)
        elif copy.two is not None:
            if flatten(copy.two.spec_key) in quote:
                catch = True
            else:
                sources = [flatten(lines[n - 1]) for n in copy.two.plan_lines]
                if len(plan_text) >= MIN_PLAN_QUOTE and any(plan_text in s or s in plan_text for s in sources):
                    near.append(j)
    return catch, ([] if catch else near), count


def _tag(body: str, name: str) -> str:
    match = re.search(rf'<{name}>(.*?)</{name}>', body, re.S)
    return match.group(1) if match else ''


def _score_control(run_dir: Path, copy_id: str) -> list[str]:
    copy = _copy(copy_id)
    plan = (COPIES_DIR / copy_id / 'plan.md').read_text()
    out = []
    for path in _rep_files(run_dir):
        reason = void_reason(path, 'findings')
        if reason:
            out.append(f'{path.stem} VOID {reason}')
            continue
        catch, near, count = control_score(reply(path), copy, plan)
        out.append(f'{path.stem} catch={_yn(catch)} near={_ids(near)} findings={count} {_cost(path)}')
    return out


def _inputs(path: Path) -> dict[str, str]:
    return dict(line.split(': ', 1) for line in path.read_text().split('\n') if ': ' in line)


def _score_step_arm(run_dir: Path, copy_id: str) -> list[str]:
    copy, sentences = _spec_sentences(copy_id)
    planted_n = planted_sentence(copy, sentences).n if (copy.plant or copy.two) else None
    amended = amended_sentences(copy, sentences)
    out = []
    for k in range(1, REPS + 1):
        cases_file = run_dir / 'cases' / f'rep{k}.json'
        if not cases_file.exists():
            continue
        phase = phase_from_json(cases_file.read_text())
        planner = parse_statement(reply(REPO / _inputs(run_dir / 'cases' / f'rep{k}.inputs.txt')['standin']))
        cost = 0.0
        if (run_dir / 'prompts' / f'rep{k}.skip').exists():
            rulings = []
        else:
            path = run_dir / f'rep{k}.json'
            reason = void_reason(path, 'rulings') if path.exists() else 'not run'
            rulings = None if reason else parse_rulings(reply(path), phase.cases)
            if reason or rulings is None:
                out.append(f'rep{k} VOID {reason or "cases"}')
                continue
            cost = float((load(path) or {}).get('total_cost_usd') or 0)
        outcomes = resolve(phase, rulings, planner)
        flagged = [{**asdict(o), 'index': i, 'flags': ['amended-sentence'] if o.sentence in amended else []}
                   for i, o in enumerate(outcomes)]
        (run_dir / 'results').mkdir(exist_ok=True)
        (run_dir / 'results' / f'rep{k}.json').write_text(json.dumps(flagged, indent=1, ensure_ascii=False))
        listed = planted_n is not None and (any(r.sentence == planted_n for r in phase.agreed)
                                            or any(c.sentence == planted_n for c in phase.cases))
        s = score_step(outcomes, copy, planted_n, listed)
        clean = copy.id == CLEAN
        out.append(step_line(f'rep{k}', s,
                             [i for i, o in enumerate(outcomes) if clean and o.kind == 'plan-conflict'],
                             [i for i, o in enumerate(outcomes) if clean and o.kind == 'unclear'],
                             [i for i, o in enumerate(outcomes) if o.sentence in amended], cost))
    return out


def score(runs_dir: Path, arm: str, ident: str) -> list[str]:
    run_dir = runs_dir / arm / ident
    if arm.startswith('reader-'):
        out = _score_reader(runs_dir, run_dir, arm, ident)
    elif arm.startswith('standin-'):
        out = _score_standin(run_dir, ident)
    elif arm.startswith('control-'):
        out = _score_control(run_dir, ident)
    elif arm.startswith('step-'):
        out = _score_step_arm(run_dir, ident)
    else:
        raise SystemExit(f'unknown arm {arm!r}')
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


def _lines(score_file: Path) -> list[tuple[str, dict[str, str]]]:
    parsed = []
    for line in score_file.read_text().split('\n'):
        rep, _, rest = line.strip().partition(' ')
        if rep and not rest.startswith('VOID'):
            parsed.append((rep, dict(part.split('=', 1) for part in rest.split())))
    return parsed


def _classify(run_dir: Path) -> dict[tuple[str, str, int], tuple[str, str]]:
    path = run_dir / 'CLASSIFY.txt'
    labels = {}
    for line in (path.read_text().split('\n') if path.exists() else []):
        if not line.strip():
            continue
        match = CLASSIFY_RE.match(line.strip())
        if not match:
            raise SystemExit(f'{path}: unreadable line {line!r}')
        rep, kind, j, label, reason = match.groups()
        if not any(label in allowed for allowed in LABELS.values()):
            raise SystemExit(f'{path}: unknown label {label!r}')
        labels[(rep, kind, int(j))] = (label, reason)
    return labels


def _label(labels, run_dir: Path, rep: str, kind: str, j: int, allowed: tuple[str, ...]) -> tuple[str, str]:
    got = labels.get((rep, kind, j))
    if got is None or got[0] not in allowed:
        raise SystemExit(f'{run_dir}: {rep} {kind}{j} needs a CLASSIFY.txt label in {allowed}')
    return got


def _idlist(cell: str) -> list[int]:
    return [int(x) for x in cell.split(',') if x != '-']


def _mean(values) -> float:
    return statistics.mean(values) if values else 0.0


def _step_stats(run_dir: Path, ident: str, parsed, labels) -> dict:
    stats = {'scored': len(parsed), 'catches': 0, 'near': [], 'on_plant': 0, 'fa': [], 'fa_noamend': [],
             'unclear': [], 'ambiguous': 0, 'false': 0, 'load': [], 'missing': [], 'unchecked': [], 'skipped': [],
             'returned': [], 'returned_on_plant': 0, 'cost': 0.0, 'miss': Counter()}
    for rep, f in parsed:
        near = _idlist(f['near'])
        near_labels = [_label(labels, run_dir, rep, 'outcome', j, LABELS['near'])[0] for j in near]
        caught = f['catch'] == 'yes' or 'near-catch' in near_labels
        stats['catches'] += caught
        stats['near'] += [f'{rep}:{j}' for j in near]
        stats['on_plant'] += f['conflict_on_plant'] == 'yes'
        conflict = [_label(labels, run_dir, rep, 'outcome', j, LABELS['conflict']) for j in _idlist(f['to_label_conflict'])]
        unclear = [_label(labels, run_dir, rep, 'outcome', j, LABELS['unclear'])[0] for j in _idlist(f['to_label_unclear'])]
        stats['fa'].append(sum(label == 'false-alarm' for label, _ in conflict))
        stats['fa_noamend'].append(sum(label == 'false-alarm' and not reason.startswith(AMENDMENT)
                                       for label, reason in conflict))
        stats['ambiguous'] += unclear.count('ambiguous')
        stats['false'] += unclear.count('false')
        stats['unclear'].append(int(f['unclear']))
        stats['load'].append(int(f['unclear']) + int(f['conflicts']))
        for name in ('missing', 'unchecked', 'skipped', 'returned'):
            stats[name].append(int(f[name]))
        stats['returned_on_plant'] += f['returned_on_plant'] == 'yes'
        stats['cost'] += float(f['cost'])
        if not caught and f['miss'] != '-':
            stats['miss'][f['miss']] += 1
    return stats


def _step_row(arm: str, ident: str, s: dict) -> str:
    planted = ident != CLEAN
    catches = f'{s["catches"]}/{s["scored"]}' if planted else 'n/a'
    fa = (f'{_mean(s["fa"]):.1f}/{_mean(s["fa_noamend"]):.1f} {s["fa"]}' if not planted else '-')
    miss = ','.join(f'{k}:{v}' for k, v in sorted(s['miss'].items())) or '-'
    return (f'{arm:<24} {ident:<12} scored={s["scored"]} catches={catches} near={",".join(s["near"]) or "-"} '
            f'conflicts_on_plant={s["on_plant"]} false_alarms/rep={fa} unclear/rep={_mean(s["unclear"]):.1f} '
            f'(ambiguous={s["ambiguous"]} false={s["false"]}) owner_load/rep={_mean(s["load"]):.1f} '
            f'missing/rep={_mean(s["missing"]):.1f} unchecked/rep={_mean(s["unchecked"]):.1f} '
            f'skipped/rep={_mean(s["skipped"]):.1f} returned/rep={_mean(s["returned"]):.1f} '
            f'returned_on_plant={s["returned_on_plant"]} misses={miss} cost=${s["cost"]:.2f}')


def _control_stats(run_dir: Path, parsed, labels) -> dict:
    stats = {'scored': len(parsed), 'catches': 0, 'near': [], 'findings': [], 'cost': 0.0}
    for rep, f in parsed:
        near = _idlist(f['near'])
        near_labels = [_label(labels, run_dir, rep, 'finding', j, LABELS['near'])[0] for j in near]
        stats['catches'] += f['catch'] == 'yes' or 'near-catch' in near_labels
        stats['near'] += [f'{rep}:{j}' for j in near]
        stats['findings'].append(int(f['findings']))
        stats['cost'] += float(f.get('cost', 0))
    return stats


def _standin_stats(run_dir: Path, parsed, labels) -> dict:
    stats = {'scored': len(parsed), 'fidelity': Counter(), 'amended_missing': [], 'amended_extra': [],
             'notes': 0, 'notes_on_plant': 0, 'returned': [], 'cost': 0.0}
    for rep, f in parsed:
        fid = f['fidelity']
        if fid == 'unmatched':
            fid = _label(labels, run_dir, rep, 'fidelity', 1, LABELS['fidelity'])[0] + ' (label)'
        stats['fidelity'][fid] += 1
        stats['amended_missing'].append(int(f['amended_missing']))
        stats['amended_extra'].append(int(f['amended_extra']))
        stats['notes'] += int(f['notes'])
        stats['notes_on_plant'] += int(f['notes_on_plant'])
        stats['returned'].append(int(f['returned']))
        stats['cost'] += float(f.get('cost', 0))
    return stats


def _reader_stats(parsed) -> dict:
    return {'scored': len(parsed), 'entries': [int(f['entries']) for _, f in parsed],
            'other': [int(f['other']) for _, f in parsed], 'returned': [int(f['returned']) for _, f in parsed],
            'cost': sum(float(f.get('cost', 0)) for _, f in parsed),
            'tokens': sum(int(f.get('tokens', 0)) for _, f in parsed)}


def _bars(results: dict) -> list[str]:
    lines = []
    planted = [c.id for c in COPIES if c.plant or c.two]
    steps = sorted({arm for arm, _ in results if arm.startswith('step-')})
    controls = {ident: s for (arm, ident), s in results.items() if arm.startswith('control-')}
    for arm in steps:
        for ident in planted:
            s = results.get((arm, ident))
            if s is None:
                lines.append(f'catch bar {ident}: not run [{arm}]')
                continue
            c = controls.get(ident)
            control = f'{c["catches"]}/{c["scored"]}' if c else 'not run'
            met = s['catches'] >= BAR_CATCHES and c is not None and c['catches'] <= BAR_CONTROL
            lines.append(f'catch bar {ident}: step {s["catches"]}/{s["scored"]}, control {control}: '
                         f'{"met" if met else "missed"} [{arm}]')
        clean = results.get((arm, CLEAN))
        if clean is None:
            lines.append(f'clean bars {CLEAN}: not run [{arm}]')
            continue
        fa, fa_noamend, unclear = _mean(clean['fa']), _mean(clean['fa_noamend']), _mean(clean['unclear'])
        lines.append(f'false-alarm bar {CLEAN}: {fa:.1f} literal, {fa_noamend:.1f} without amendment per rep: '
                     f'{"met" if fa <= BAR_MEAN else "missed"} literal, '
                     f'{"met" if fa_noamend <= BAR_MEAN else "missed"} without amendment [{arm}]')
        lines.append(f'unclear bar {CLEAN}: {unclear:.1f} per rep (ambiguous {clean["ambiguous"]}, false '
                     f'{clean["false"]}): {"met" if unclear <= BAR_MEAN else "missed"} [{arm}]')
    for arm in steps:
        if arm.startswith(TREATMENT_PREFIX):
            lines.append(_second_reader(results, arm))
    lines.append(_pd9(results))
    return lines


def _beats(results: dict, pair: str) -> tuple[bool, str]:
    claude = CLAUDE_ARM
    planted = [c.id for c in COPIES if c.plant or c.two]
    cp = sum(results.get((pair, i), {}).get('catches', 0) for i in planted)
    cc = sum(results.get((claude, i), {}).get('catches', 0) for i in planted)
    pc, cl = results.get((pair, CLEAN)), results.get((claude, CLEAN))
    if pc is None or cl is None:
        return cp > cc, f'catches pair {cp} vs claude {cc}; clean copy not run'
    pf, pf2, cf, cf2 = _mean(pc['fa']), _mean(pc['fa_noamend']), _mean(cl['fa']), _mean(cl['fa_noamend'])
    beats = cp > cc or pf < cf or pf2 < cf2
    return beats, (f'catches pair {cp} vs claude {cc}; clean false alarms pair {pf:.1f}/{pf2:.1f} vs claude '
                   f'{cf:.1f}/{cf2:.1f}')


def _second_reader(results: dict, pair: str) -> str:
    beats, detail = _beats(results, pair)
    return f'second reader [{pair}]: {detail}: {"pair beats claude alone" if beats else "pair does not beat claude alone"}'


def _pd9(results: dict) -> str:
    pair = f'{TREATMENT_PREFIX}{PD9_MODEL}'
    if not any(arm == pair for arm, _ in results):
        return f'PD9 trigger: no (no {pair} arm scored)'
    fails = []
    for c in COPIES:
        if c.plant or c.two:
            s = results.get((pair, c.id))
            if s is None or s['catches'] < BAR_CATCHES:
                fails.append(f'catch {c.id} {s["catches"] if s else 0}/{s["scored"] if s else 0}')
    clean = results.get((pair, CLEAN))
    if clean is None:
        fails.append('clean copy not run')
    else:
        if _mean(clean['fa']) > BAR_MEAN or _mean(clean['fa_noamend']) > BAR_MEAN:
            fails.append(f'false alarms {_mean(clean["fa"]):.1f}/{_mean(clean["fa_noamend"]):.1f}')
        if _mean(clean['unclear']) > BAR_MEAN:
            fails.append(f'unclear {_mean(clean["unclear"]):.1f}')
    if not _beats(results, pair)[0]:
        fails.append('does not beat claude alone')
    return f'PD9 trigger: {"yes" if fails else "no"} ({"; ".join(fails) or "the four PD9 bars met"})'


def table(runs_dir: Path) -> list[str]:
    rows, results = [], {}
    for score_file in sorted(runs_dir.glob('*/*/SCORE.txt')):
        run_dir = score_file.parent
        arm, ident = run_dir.parent.name, run_dir.name
        if arm in ('pilot', 'prompts'):
            continue
        parsed, labels = _lines(score_file), _classify(run_dir)
        if arm.startswith('step-'):
            s = _step_stats(run_dir, ident, parsed, labels)
            rows.append(_step_row(arm, ident, s))
        elif arm.startswith('control-'):
            s = _control_stats(run_dir, parsed, labels)
            rows.append(f'{arm:<24} {ident:<12} scored={s["scored"]} catches={s["catches"]}/{s["scored"]} '
                        f'near={",".join(s["near"]) or "-"} findings/rep={_mean(s["findings"]):.1f} '
                        f'cost=${s["cost"]:.2f}')
        elif arm.startswith('standin-'):
            s = _standin_stats(run_dir, parsed, labels)
            fid = ','.join(f'{k}:{v}' for k, v in sorted(s['fidelity'].items()))
            rows.append(f'{arm:<24} {ident:<12} scored={s["scored"]} fidelity={fid} '
                        f'amended_missing/rep={_mean(s["amended_missing"]):.1f} '
                        f'amended_extra/rep={_mean(s["amended_extra"]):.1f} notes={s["notes"]} '
                        f'notes_on_plant={s["notes_on_plant"]} returned/rep={_mean(s["returned"]):.1f} '
                        f'cost=${s["cost"]:.2f}')
        elif arm.startswith('reader-'):
            s = _reader_stats(parsed)
            spend = f'tokens={s["tokens"]:,}' if s['tokens'] else f'cost=${s["cost"]:.2f}'
            rows.append(f'{arm:<24} {ident:<12} scored={s["scored"]} entries/rep={_mean(s["entries"]):.1f} '
                        f'other/rep={_mean(s["other"]):.1f} returned/rep={_mean(s["returned"]):.1f} {spend}')
        else:
            continue
        results[(arm, ident)] = s
    return rows + _bars(results)


PROMPT = 'State what the spec asks.\nThe second line of the prompt.\n'
STATEMENT = '<statement>\n<entry sentence="S1"><quote>q</quote><subject>s</subject><value>1</value><unit>none</unit>' \
    '<edge>n/a</edge><default>none</default><other_reading>none</other_reading></entry>\n</statement>'
LOG_HEAD = '''OpenAI Codex v0.163.0
--------
workdir: /tmp/plan83-codex-abc123
model: gpt-6-sol
provider: openai
--------
'''
LOG_CLEAN = (LOG_HEAD + 'user\n' + PROMPT + '\nwarning: Under-development features enabled: skip_host_skill_discovery.\n'
             + 'codex\n' + STATEMENT + '\ntokens used\n19,402\n' + STATEMENT + '\n')
LOG_TOOL = LOG_CLEAN.replace('codex\n', "exec\n/bin/zsh -lc 'cat SITES.txt' in /tmp/plan83-codex-abc123\n"
                             ' succeeded in 5ms:\ncodex\n', 1)


def _json(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))
    return path


def _codex(path: Path, log: str, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    path.with_suffix('.log').write_text(log)
    return path


def _ok(text: str, cost: float = 0.25) -> dict:
    return {'subtype': 'success', 'is_error': False, 'num_turns': 1, 'result': text, 'total_cost_usd': cost,
            'modelUsage': {'claude-opus-5-5': {}}}


def _stand(n: int, value: str, unit: str = 'none', default: str = 'none', amended: str = 'none') -> Entry:
    return Entry(n, 'q', 's', Slots(value, unit, 'n/a', default), None, '12', amended, '')


def _planted_n(copy_id: str) -> int:
    from make_copies import planted_sentence
    from number import number
    copy = next(c for c in COPIES if c.id == copy_id)
    return planted_sentence(copy, number((COPIES_DIR / copy_id / 'spec.md').read_text())).n


def selftest() -> None:
    P66_BOUND, P66_TODAY, P55_EXIT = (next(c for c in COPIES if c.id == i) for i in ('p66-bound', 'p66-today',
                                                                                   'p55-exit'))
    PLANTED_N, EDIT_N, TODAY_N = _planted_n('p66-bound'), _planted_n('p55-exit'), _planted_n('p66-today')
    spec_slots = Slots('00:00:00Z on the day after the freeze date', 'none', 'in', 'none')
    plant_slots = Slots('00:00:00Z on the freeze date', 'none', 'in', 'none')
    CATCH_OUTCOMES = [Outcome('missing', 3, 'x', Slots('1', 'none', 'n/a', 'none'), None, ''),
                      Outcome('plan-conflict', PLANTED_N, 'exclude-newer', spec_slots, plant_slots, '')]
    TOKENLESS_CONFLICT = [Outcome('plan-conflict', PLANTED_N, 'exclude-newer',
                                  Slots('2026-10-20T00:00:00Z', 'none', 'n/a', 'none'),
                                  Slots('2026-10-19T00:00:00Z', 'none', 'n/a', 'none'), '')]
    RETURNED_ON_PLANT = [Outcome('returned', PLANTED_N, 'exclude-newer', None, None, 'claude#4: quote not in S1'),
                         Outcome('missing', PLANTED_N, 'exclude-newer', spec_slots, None, '')]
    UNCLEAR_ON_EDIT = [Outcome('unclear', EDIT_N, 'output', None, None, 'C1 rule 2; quote: ')]
    CONFLICT_ON_EDIT = [Outcome('plan-conflict', EDIT_N, 'output', Slots('2', 'none', 'n/a', 'none'),
                                Slots('1', 'none', 'n/a', 'none'), '')]
    PLANTED_P = [_stand(PLANTED_N, '00:00:00Z on the freeze date')]
    SPEC_P = [_stand(PLANTED_N, '00:00:00Z on the day after the freeze date')]
    AMENDED_P = [_stand(PLANTED_N, '00:00:00Z on the freeze date', amended='Task 1')]
    UTC_P = [_stand(TODAY_N, 'the freeze date', default='today (UTC)')]
    LOCAL_P = [_stand(TODAY_N, 'the freeze date', default="today's local date")]
    MARKS_P = [_stand(4, 'a', amended='Task 1'), _stand(5, 'b'), _stand(6, 'c', amended='Task 2'), _stand(7, 'd')]
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        CUT_JSON = _json(tmp / 'cut' / 'rep1.json', _ok(STATEMENT.replace('</statement>', '')))
        BUDGET_JSON = _json(tmp / 'budget' / 'rep1.json', {'subtype': 'error_max_budget_usd', 'is_error': True})
        CODEX_TOOL_MD = _codex(tmp / 'tool' / 'rep1.md', LOG_TOOL, STATEMENT)
        CODEX_OTHER_MODEL_MD = _codex(tmp / 'model' / 'rep1.md', LOG_CLEAN.replace('gpt-6-sol', 'gpt-6-astra'),
                                      STATEMENT)
        DIR_REP2_VOID = tmp / 'void'
        for k, data in ((1, _ok(STATEMENT)), (2, _ok('no block')), (3, _ok(STATEMENT)), (4, _ok(STATEMENT))):
            _json(DIR_REP2_VOID / f'rep{k}.json', data)
        _json(DIR_REP2_VOID / 'rep2.void1.json', _ok(STATEMENT))
        assert void_reason(CUT_JSON, 'statement') == 'no-block'                  # cut off at the output limit
        assert void_reason(BUDGET_JSON, 'statement') == 'budget'
        assert void_reason(CODEX_TOOL_MD, 'statement', 'gpt-6-sol', PROMPT) == 'residual'   # the watch item
        assert void_reason(CODEX_OTHER_MODEL_MD, 'statement', 'gpt-6-sol', PROMPT) == 'model'
        assert void_reason(_codex(tmp / 'clean' / 'rep1.md', LOG_CLEAN, STATEMENT), 'statement', 'gpt-6-sol',
                           PROMPT) is None
        assert [p.name for p in scored_reps(DIR_REP2_VOID, 'statement')][:2] == ['rep1.json', 'rep3.json']
        assert score_step(CATCH_OUTCOMES, P66_BOUND, PLANTED_N).catch
        assert score_step(TOKENLESS_CONFLICT, P66_BOUND, PLANTED_N).near == [0]
        miss = score_step(RETURNED_ON_PLANT, P66_BOUND, PLANTED_N)
        assert not miss.catch and miss.returned_on_plant and miss.miss_reason == 'returned'   # Review Focus 5
        assert score_step(UNCLEAR_ON_EDIT, P55_EXIT, EDIT_N).catch
        edit = score_step(CONFLICT_ON_EDIT, P55_EXIT, EDIT_N)
        assert edit.conflict_on_plant and not edit.catch
        assert [fidelity(p, P66_BOUND, PLANTED_N) for p in (PLANTED_P, SPEC_P, AMENDED_P, [])] == [
            'faithful', 'spec value', 'amended', 'absent']
        assert fidelity(UTC_P, P66_TODAY, TODAY_N) == 'faithful' and fidelity(LOCAL_P, P66_TODAY, TODAY_N) == 'other'
        assert amend_marks(MARKS_P, {4, 5}) == (1, 1)
        _table_selftest(tmp / 'runs')
        _control_selftest()
        _step_selftest(tmp / 'step-runs')
    print('measure selftest ok')


def _control_selftest() -> None:
    '''The control's catch on a two-reading copy quotes the edited sentence; a finding whose <plan> comes from
    one of the edit's plan lines is near (PD10). Plan 81's rule holds on an argued plant.'''
    exit_copy, bound = _copy('p55-exit'), _copy('p66-bound')
    plan = (COPIES_DIR / 'p55-exit' / 'plan.md').read_text()
    finding = '<finding task="{t}"><quote>{q}</quote><plan>{p}</plan><fix>f</fix></finding>'
    text = '<findings>' + ''.join(finding.format(t=t, q=q, p=p) for t, q, p in (
        (3, 'R3.6 Errors name their cause.', 'raise RegistryError'),
        (4, 'R4.1 The check runs.', "assert rs.main(['--check'], root=tmp_path) == 1"),
        (0, 'or one line per finding and an error exit.', 'exit 1'))) + '</findings>'
    assert control_score(text, exit_copy, plan) == (True, [], 3)
    assert control_score(text.replace('an error exit', 'exit 0'), exit_copy, plan) == (False, [2], 3)
    caught = ('<findings><finding task="2"><quote>00:00:00Z on the day after the freeze date</quote>'
              '<plan>cutoff == \'2026-10-19T00:00:00Z\'</plan><fix>f</fix></finding></findings>')
    assert control_score(caught, bound, '')[0] is True


def _step_selftest(runs: Path) -> None:
    '''score on a step arm: an adjudicated rep resolves its cases, a skipped rep runs none, and a p55-clean
    plan-conflict is listed to label.'''
    from compare import parse_statement as statement, phase_to_json, reader_phase
    _copy_, sentences = _spec_sentences(CLEAN)
    by_n = {s.n: s.text for s in sentences}
    n = next(s.n for s in sentences if "Default `['3.13']`" in s.text)
    entry = ('<entry sentence="S{n}"><quote>Default `[\'3.13\']`</quote><subject>pythons</subject><value>{v}</value>'
             '<unit>none</unit><edge>n/a</edge><default>{d}</default>{x}</entry>')
    claude = statement('<statement>' + entry.format(n=n, v='list of strings', d="['3.13']",
                                                    x='<other_reading>none</other_reading>') + '</statement>')
    planner_text = '<statement>' + entry.format(n=n, v='list of strings', d="['3.11']",
                                                x='<plan_lines>40</plan_lines><amended>none</amended>') + '</statement>'
    standin = _json(runs / 'standin-opus' / CLEAN / 'rep1.json', _ok(planner_text))
    step = runs / 'step-claude' / CLEAN
    for k, claude_k in ((1, claude), (2, statement('<statement></statement>'))):
        phase = reader_phase(by_n, claude_k, None, statement(planner_text))
        (step / 'cases').mkdir(parents=True, exist_ok=True)
        (step / 'prompts').mkdir(parents=True, exist_ok=True)
        (step / 'cases' / f'rep{k}.json').write_text(phase_to_json(phase))
        (step / 'cases' / f'rep{k}.inputs.txt').write_text(f'standin: {standin}\n')
        if phase.cases:
            (step / 'prompts' / f'rep{k}.txt').write_text('prompt')
        else:
            (step / 'prompts' / f'rep{k}.skip').write_text('no case\n')
    _json(step / 'rep1.json', _ok('<rulings><ruling case="C1" verdict="reading"><quote>Default `[\'3.13\']`</quote>'
                                  "<value>list of strings</value><unit>none</unit><edge>n/a</edge>"
                                  "<default>['3.13']</default></ruling></rulings>", 0.3))
    lines = score(runs, 'step-claude', CLEAN)
    assert lines[0].startswith('rep1 catch=no near=- conflict_on_plant=no conflicts=1 ') and \
        'to_label_conflict=0 ' in lines[0] and lines[0].endswith('cost=0.3000'), lines
    assert lines[1].startswith('rep2 catch=no near=- conflict_on_plant=no conflicts=0 unclear=0 missing=0 '
                               'unchecked=1 '), lines
    assert json.loads((step / 'results' / 'rep1.json').read_text())[0]['kind'] == 'plan-conflict'


def _table_selftest(runs: Path) -> None:
    '''`table` refuses an unlabeled p55-clean conflict, counts false alarms with and without `amendment:`
    reasons, and prints the catch bar.'''
    clean = runs / 'step-pair-gpt-6-sol' / 'p55-clean'
    clean.mkdir(parents=True)
    conflict = StepScore(False, [], False, 1, 0, 0, 0, 0, 0, False, '')
    (clean / 'SCORE.txt').write_text(step_line('rep1', conflict, [0], [], [], 0.5) + '\n'
                                     + step_line('rep2', conflict, [0], [], [], 0.5) + '\n')
    try:
        table(runs)
        raise AssertionError('table scored an unlabeled p55-clean conflict')
    except SystemExit as refusal:
        assert 'CLASSIFY.txt' in str(refusal), refusal
    (clean / 'CLASSIFY.txt').write_text('rep1 outcome0 false-alarm amendment: Q1 renames the suite\n'
                                        'rep2 outcome0 false-alarm the plan matches the spec\n')
    text = '\n'.join(table(runs))
    assert 'false_alarms/rep=1.0/0.5' in text, text
    bound = runs / 'step-pair-gpt-6-sol' / 'p66-bound'
    bound.mkdir(parents=True)
    caught = StepScore(True, [], True, 1, 0, 0, 0, 0, 0, False, '')
    missed = StepScore(False, [], False, 0, 0, 0, 0, 0, 0, False, 'agreed')
    (bound / 'SCORE.txt').write_text(''.join(step_line(f'rep{k}', caught if k < 5 else missed, [], [], [], 0.5) + '\n'
                                             for k in range(1, 6)))
    control = runs / 'control-opus' / 'p66-bound'
    control.mkdir(parents=True)
    (control / 'SCORE.txt').write_text(''.join(f'rep{k} catch={"yes" if k == 1 else "no"} near=- findings=2 '
                                               'cost=0.9000\n' for k in range(1, 6)))
    text = '\n'.join(table(runs))
    assert 'catch bar p66-bound: step 4/5, control 1/5: met' in text, text


def main() -> None:
    command, args = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else ('', [])
    if command == 'selftest':
        selftest()
    elif command == 'score' and len(args) == 3:
        print('\n'.join(score(Path(args[0]), args[1], args[2])))
    elif command == 'table' and len(args) == 1:
        print('\n'.join(table(Path(args[0]))))
    elif command == 'residual' and len(args) == 2:
        print('\n'.join(residual(Path(args[0]), Path(args[1]))))
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
