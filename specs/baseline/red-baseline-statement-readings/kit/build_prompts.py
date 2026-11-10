'''Fill the statement-readings probe's prompts (plan 83), rewritten from plan 81's build_prompts.py.

Usage, from the repository root:
  uv run python <kit>/build_prompts.py reader <spec-id> <out-file>
  uv run python <kit>/build_prompts.py standin <copy> <out-file>
  uv run python <kit>/build_prompts.py control <copy> <out-file> <sha>
  uv run python <kit>/build_prompts.py adjudicator <runs-dir> <arm> <copy>
  uv run python <kit>/build_prompts.py selftest
A reader gets reader.txt with one numbered spec, and nothing from any plan (D9). The stand-in gets standin.txt
with the numbered spec and its copy's plan, each plan line prefixed `<n>| ` (D13). The control gets plan 81's
control.txt with writing-plans' SKILL.md at <sha>, the copy's spec.md and its plan.md: one sha for all control
prompts. `adjudicator` reads, for each k up to 5 for which every input has a k-th scored rep, that rep of the
arm's readers and of standin-opus/<copy>/, runs compare.reader_phase, and writes step-<arm>/<copy>/cases/
rep<k>.json and rep<k>.inputs.txt, and either prompts/rep<k>.txt or, with no case, prompts/rep<k>.skip. The arm
is `pair-<model>` (both readers), `claude` or `codex-<model>`. The adjudicator's prompt holds the numbered spec
and the arm's reader entries only, named Reader A and Reader B, never by model (PD8). `guard` refuses a reader or
adjudicator prompt that holds a copy folder or a source plan path, a PD1 defense line, or a plant or edit token
that the spec text lacks; the reader entries in an adjudicator prompt are the readers' own text and are
exempt from the token check. Every built prompt appends one line to SOURCES.txt.
'''
import hashlib
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compare import Case, Entry, Phase, parse_statement, phase_to_json, reader_phase  # noqa: E402
from measure import reply, scored_reps  # noqa: E402
from number import flatten, number  # noqa: E402
from plants import COPIES, Copy  # noqa: E402

KIT = Path(__file__).resolve().parent
REPO = KIT.parents[3]
COPIES_DIR = KIT.parent / 'copies'
PROMPTS = KIT / 'prompts'
SKILL_PATH = 'skills/writing-plans/SKILL.md'
FRONTMATTER_RE = re.compile(r'^---\n.*?\n---\n', re.S)
REPS = 5
CODEX_SENTINEL = 'zeta-codex-sentinel'
PLANNER_SENTINEL = 'omega-planner-sentinel'
CLAUDE_READER = 'reader-opus'
STANDIN = 'standin-opus'
INTRO_TWO = ('Two readers each stated, from the spec alone, what the spec asks. Each case below is a sentence where '
             'they differ, where one reader alone states a value, or where a reader names another reading.')
INTRO_ONE = ('A reader stated, from the spec alone, what the spec asks. Each case below is a sentence where the '
             'reader states a value that needs a ruling, or where the reader names another reading.')


def git(*args: str) -> str:
    return subprocess.run(['git', *args], cwd=REPO, check=True, capture_output=True, text=True).stdout


def _manifest() -> dict[str, str]:
    out = {}
    for line in (COPIES_DIR / 'MANIFEST.txt').read_text().split('\n'):
        if line.strip():
            digest, path, _origin = line.split('  ')
            out[path] = digest
    return out


def _checked(copy_id: str, name: str) -> tuple[str, str]:
    '''A copy file's text and sha256, checked against MANIFEST.txt.'''
    path = COPIES_DIR / copy_id / name
    text = path.read_text()
    digest = hashlib.sha256(text.encode('utf-8')).hexdigest()
    if digest != _manifest()[str(path.relative_to(REPO))]:
        raise SystemExit(f'refusing: {path} differs from MANIFEST.txt')
    return text, digest


def _spec_copy(spec_id: str) -> Copy:
    return next(c for c in COPIES if c.spec_id == spec_id)


def numbered(spec_id: str) -> str:
    return _checked(_spec_copy(spec_id).id, 'numbered.txt')[0].strip('\n')


def fill(template: str, **parts: str) -> str:
    text = (PROMPTS / template).read_text()
    for key, value in parts.items():
        text = text.replace(f'@@{key.upper()}@@', value)
    if '@@' in text:
        raise SystemExit(f'refusing: {template} has an unfilled marker')
    return text


def _word(token: str, text: str) -> bool:
    lead = r'(?<![\w.])' if token[:1].isalnum() else ''
    tail = r'(?![\w.])' if token[-1:].isalnum() else ''
    return re.search(lead + re.escape(token) + tail, text) is not None


def _tokens() -> list[str]:
    out = []
    for c in COPIES:
        if c.plant:
            out += [*c.plant.plant_tokens, *c.plant.planted_tokens]
        if c.two:
            out += [*c.two.a_tokens, *c.two.b_tokens, *c.two.edit]
    return sorted({flatten(t) for t in out})


def guard(text: str, spec_id: str, allowed: tuple[str, ...] = ()) -> None:
    '''Refuse a reader or adjudicator prompt that holds plan text (spec anti-goals 1 and 2).'''
    for c in COPIES:
        for path in (str((COPIES_DIR / c.id).relative_to(REPO)), f'copies/{c.id}', c.plan_path):
            if path in text:
                raise SystemExit(f'refusing: the prompt names {path}')
        if c.plant and c.plant.defense[1] in text:
            raise SystemExit(f'refusing: the prompt holds the {c.id} defense line')
    rest = text
    for part in allowed:
        rest = rest.replace(part, '')
    spec, rest = flatten(numbered(spec_id)), flatten(rest)
    for token in _tokens():
        if _word(token, rest) and not _word(token, spec):
            raise SystemExit(f'refusing: the prompt holds {token!r}, which the spec text lacks')


def run_dir_of(out: Path) -> Path:
    return out.parent.parent if out.parent.name == 'prompts' else out.parent


def record(run_dir: Path, line: str) -> None:
    sources = run_dir / 'SOURCES.txt'
    have = sources.read_text().split('\n') if sources.exists() else []
    if line not in have:
        with sources.open('a') as f:
            f.write(f'{line}\n')


def reader(spec_id: str) -> str:
    text = fill('reader.txt', spec=numbered(spec_id))
    guard(text, spec_id)
    return text


def standin(copy_id: str) -> str:
    copy = next(c for c in COPIES if c.id == copy_id)
    plan = _checked(copy_id, 'plan.md')[0]
    lines = plan.split('\n')
    if lines and lines[-1] == '':
        lines.pop()
    return fill('standin.txt', spec=numbered(copy.spec_id), plan='\n'.join(f'{n}| {line}' for n, line in enumerate(lines, 1)))


def control(copy_id: str, sha: str) -> str:
    spec, plan = _checked(copy_id, 'spec.md')[0], _checked(copy_id, 'plan.md')[0]
    skill = FRONTMATTER_RE.sub('', git('show', f'{sha}:{SKILL_PATH}'), count=1).strip()
    source = f'<!-- writing-plans {SKILL_PATH} at {sha} -->'
    return fill('control.txt', source=source, skill=skill, spec=spec.strip(), plan=plan.strip())


def _entry_xml(e: Entry) -> str:
    other = 'none' if e.other is None else (f'<value>{e.other.value}</value><unit>{e.other.unit}</unit>'
                                            f'<edge>{e.other.edge}</edge><default>{e.other.default}</default>')
    return (f'<entry sentence="S{e.sentence}"><quote>{e.quote}</quote><subject>{e.subject}</subject>'
            f'<value>{e.slots.value}</value><unit>{e.slots.unit}</unit><edge>{e.slots.edge}</edge>'
            f'<default>{e.slots.default}</default><other_reading>{other}</other_reading></entry>')


def _names(phase: Phase) -> dict[str, str]:
    readers = sorted({name for c in phase.cases for name in c.entries}, key=('claude', 'codex').index)
    return dict(zip(readers, ('Reader A', 'Reader B')))


def _case_xml(case: Case, names: dict[str, str]) -> str:
    '''The entries the case rules on under each reader's name, then the readers' other entries on its sentence as
    context (PD12). A case with no `asked` (built before it existed) shows all its entries under the names.'''
    asked = case.asked or case.entries
    parts, context = [f'<case id="{case.id}" sentence="S{case.sentence}">'], []
    for reader_name, label in names.items():
        own = asked.get(reader_name, [])
        parts.append(f'{label}:')
        parts += [_entry_xml(e) for e in own] or ['(no entry)']
        others = list(case.entries.get(reader_name, []))
        for e in own:
            if e in others:
                others.remove(e)
        context += [f'{label}: {_entry_xml(e)}' for e in others]
    if context:
        parts.append(f'Context, other entries on S{case.sentence}:')
        parts += context
    parts.append('</case>')
    return '\n'.join(parts)


def adjudicator_prompt(phase: Phase, spec_id: str) -> str:
    names = _names(phase)
    intro = INTRO_TWO if len(names) == 2 else INTRO_ONE
    text = fill('adjudicator.txt', intro=intro, spec=numbered(spec_id),
                cases='\n\n'.join(_case_xml(c, names) for c in phase.cases))
    allowed = tuple(_entry_xml(e) for c in phase.cases for es in c.entries.values() for e in es)
    guard(text, spec_id, allowed)
    return text


def arm_readers(arm: str) -> dict[str, tuple[str, str | None]]:
    '''The arm's readers: name -> (run folder, Codex model or None).'''
    if arm == 'claude':
        return {'claude': (CLAUDE_READER, None)}
    if arm.startswith('pair-'):
        model = arm.removeprefix('pair-')
        return {'claude': (CLAUDE_READER, None), 'codex': (f'reader-{model}', model)}
    if arm.startswith('codex-'):
        model = arm.removeprefix('codex-')
        return {'codex': (f'reader-{model}', model)}
    raise SystemExit(f'unknown arm {arm!r}')


def _rel(path: Path) -> Path:
    '''The path from the repository root, or the absolute path outside it.'''
    path = path.resolve()
    return path.relative_to(REPO) if path.is_relative_to(REPO) else path


def adjudicator(runs_dir: Path, arm: str, copy_id: str) -> list[str]:
    runs_dir = runs_dir.resolve()
    copy = next(c for c in COPIES if c.id == copy_id)
    sentences = {s.n: s.text for s in number(_checked(copy_id, 'spec.md')[0])}
    reader_prompt = (runs_dir / 'prompts' / f'reader-{copy.spec_id}.txt').read_text()
    reps = {name: scored_reps(runs_dir / folder / copy.spec_id, 'statement', model,
                              reader_prompt if model else None)
            for name, (folder, model) in arm_readers(arm).items()}
    standins = scored_reps(runs_dir / STANDIN / copy_id, 'statement')
    step = runs_dir / f'step-{arm}' / copy_id
    (step / 'cases').mkdir(parents=True, exist_ok=True)
    (step / 'prompts').mkdir(parents=True, exist_ok=True)
    out = []
    for k in range(1, REPS + 1):
        if k > len(standins) or any(k > len(r) for r in reps.values()):
            break
        stated = {name: parse_statement(reply(r[k - 1])) for name, r in reps.items()}
        planner = parse_statement(reply(standins[k - 1]))
        phase = reader_phase(sentences, stated.get('claude'), stated.get('codex'), planner)
        (step / 'cases' / f'rep{k}.json').write_text(phase_to_json(phase))
        inputs = {'standin': standins[k - 1], **{name: r[k - 1] for name, r in reps.items()}}
        (step / 'cases' / f'rep{k}.inputs.txt').write_text(
            ''.join(f'{name}: {_rel(path)}\n' for name, path in inputs.items()))
        if phase.cases:
            prompt = adjudicator_prompt(phase, copy.spec_id)
            (step / 'prompts' / f'rep{k}.txt').write_text(prompt)
            out.append(f'rep{k}: {len(phase.cases)} cases, {len(prompt)} chars')
        else:
            (step / 'prompts' / f'rep{k}.skip').write_text('no case\n')
            out.append(f'rep{k}: no case')
        record(step, f'rep{k}: copy {copy_id}, numbered.txt sha256 {_checked(copy.id, "numbered.txt")[1]}; '
                     + '; '.join(f'{name} {_rel(path)}' for name, path in inputs.items()))
    return out


def _sentinel_phases():
    '''A pair phase and a Claude-only phase on the p55 spec, from statements that carry sentinels.'''
    from number import number
    sentences = {s.n: s.text for s in number((COPIES_DIR / 'p55-clean' / 'spec.md').read_text())}
    n = next(k for k, text in sentences.items() if "Default `['3.13']`" in text)
    entry = ('<entry sentence="S{n}"><quote>Default `[\'3.13\']`</quote><subject>pythons</subject><value>{v}</value>'
             '<unit>none</unit><edge>n/a</edge><default>none</default>{extra}</entry>')
    claude = parse_statement('<statement>' + entry.format(n=n, v="['3.13']", extra='<other_reading>none</other_reading>')
                             + '</statement>')
    codex = parse_statement('<statement>' + entry.format(n=n, v=CODEX_SENTINEL, extra='<other_reading>none</other_reading>')
                            + '</statement>')
    planner = parse_statement('<statement>' + entry.format(n=n, v=PLANNER_SENTINEL,
                                                           extra='<plan_lines>1</plan_lines><amended>none</amended>')
                              + '</statement>')
    return reader_phase(sentences, claude, codex, planner), reader_phase(sentences, claude, None, planner)


def _duo_phase() -> Phase:
    '''A Claude-only phase with two lone entries on one p55 sentence, so two cases on that sentence.'''
    sentences = {s.n: s.text for s in number((COPIES_DIR / 'p55-clean' / 'spec.md').read_text())}
    n = next(k for k, text in sentences.items() if "Default `['3.13']`" in text)
    entry = ('<entry sentence="S{n}"><quote>Default `[\'3.13\']`</quote><subject>{s}</subject><value>{v}</value>'
             '<unit>none</unit><edge>n/a</edge><default>none</default><other_reading>none</other_reading></entry>')
    claude = parse_statement('<statement>' + entry.format(n=n, s='pythons', v="['3.13']")
                             + entry.format(n=n, s='interpreters', v='list of strings') + '</statement>')
    return reader_phase(sentences, claude, None, [])


def selftest() -> None:
    for spec_id in ('p53', 'p66', 'p55', 'p66-today', 'p55-exit'):
        text = reader(spec_id)
        rest = text.replace(numbered(spec_id), '')                              # the spec's own words may name a path
        assert '@@' not in text and 'copies/' not in text and 'specs/plans/' not in rest, spec_id
        assert not any(c.plan_path in text for c in COPIES), spec_id
        assert not any(c.plant and c.plant.defense[1] in text for c in COPIES), spec_id
    PAIR_PHASE, CLAUDE_ONLY_PHASE = _sentinel_phases()
    pair = adjudicator_prompt(PAIR_PHASE, 'p55')                               # the positive control
    assert 'Reader A' in pair and 'Reader B' in pair and CODEX_SENTINEL in pair and PLANNER_SENTINEL not in pair
    adj = adjudicator_prompt(CLAUDE_ONLY_PHASE, 'p55')                          # a one-reader arm
    assert 'Reader B' not in adj and CODEX_SENTINEL not in adj and PLANNER_SENTINEL not in adj
    duo = _duo_phase()                                                          # two cases on one sentence (PD12)
    xml = [_case_xml(c, _names(duo)) for c in duo.cases]
    assert len(xml) == 2 and xml[0] != xml[1] and all('\nContext, ' in x for x in xml), xml
    assert all(x.index('pythons') < x.index('interpreters') for x in xml[:1]) and \
        xml[1].index('interpreters') < xml[1].index('pythons'), xml
    assert '\nContext, ' in adjudicator_prompt(duo, 'p55')
    try:
        guard(reader('p53') + COPIES[1].plant.defense[1], 'p53')
        raise AssertionError('guard passed a defense line')
    except SystemExit:
        pass
    for leak in ('specs/baseline/red-baseline-statement-readings/copies/p55-clean', COPIES[0].plan_path, '3.12'):
        try:
            guard(reader('p55') + leak, 'p55')
            raise AssertionError(f'guard passed {leak!r}')
        except SystemExit:
            pass
    print('build_prompts selftest ok')


def main() -> None:
    args = sys.argv[1:]
    if args == ['selftest']:
        selftest()
        return
    if len(args) == 4 and args[0] == 'adjudicator':
        print('\n'.join(adjudicator(Path(args[1]), args[2], args[3])))
        return
    if len(args) == 3 and args[0] == 'reader':
        _, spec_id, out = args
        text = reader(spec_id)
        line = f'reader-{spec_id}: numbered.txt sha256 {_checked(_spec_copy(spec_id).id, "numbered.txt")[1]}'
    elif len(args) == 3 and args[0] == 'standin':
        _, copy_id, out = args
        text = standin(copy_id)
        line = (f'standin-{copy_id}: numbered.txt sha256 {_checked(copy_id, "numbered.txt")[1]}, '
                f'plan.md sha256 {_checked(copy_id, "plan.md")[1]}')
    elif len(args) == 4 and args[0] == 'control':
        _, copy_id, out, sha = args
        text = control(copy_id, sha)
        line = (f'control-{copy_id}: spec.md sha256 {_checked(copy_id, "spec.md")[1]}, plan.md sha256 '
                f'{_checked(copy_id, "plan.md")[1]}, writing-plans {SKILL_PATH} at {sha}')
    else:
        sys.exit(__doc__)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    record(run_dir_of(out), line)
    print(f'wrote {out}: {len(text)} chars')


if __name__ == '__main__':
    main()
