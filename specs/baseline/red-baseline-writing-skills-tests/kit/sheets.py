'''Write the blind grading sheets of plan 107's case reps, and unblind the grades.

Copy of plan 105's sheets.py (specs/baseline/red-baseline-writing-skills-layout/kit/sheets.py), changed for
plan 107: the cases are M1, T2 and R3, there is no W case and no read check that scores, R3 is scored
mechanically and has no sheet, and the bars are RED and GREEN (below) in place of plan 105's guard.

Usage, from the repository root:
  uv run python <kit>/sheets.py build <runs-root> <sheet-dir> <seed>
  uv run python <kit>/sheets.py unblind <grades.tsv> <key.json>

build reads <runs-root>/<case>/<arm>/<model>/rep<N>/ (run_tool_reps.sh's folders). It skips a rep that audit.py
gives a VOID reason. For M1 and T2 it writes one sheet per scored rep to <sheet-dir>/<id>.txt, where <id> is a
6-hex id drawn from <seed>, so the same seed gives the same ids. A sheet holds the case, its PASS and FAIL
columns (cases.COLUMNS) and the rep's final message and final.diff. It never names the arm, the model or the
rep. In the answer, every path that ends in a writing-skills file name becomes <skill>/<basename>, whatever
its root or arm. The name itself stays: a GREEN answer that names micro-tests.md shows its arm, a limit the
record reports. R3 reps get no sheet: audit.r3_check scores them from the parked final tree, and the key holds
that verdict (`mechanical`). The key, each id with its case, arm, model, rep, whether the rep Read the case's
reference file (`reads`, descriptive) and the mechanical verdict, goes to <sheet-dir>/../key.json. build
refuses an existing <sheet-dir> or key.json, and a <sheet-dir> inside a git repository, so neither the sheets
nor the key can be committed. Read the key only after every sheet is graded.

unblind reads grades.tsv, one `<id><TAB>PASS|FAIL` line per sheet (more columns, a header line that starts
with `id`, blank lines and `#` lines are ignored), and refuses a missing, extra, repeated or unknown grade. A
rep's verdict is its grade, or for R3 its mechanical verdict. It prints each rep's verdict, then for each case
and model the old and new pass counts with RED and GREEN, then each case's verdict. RED is shown on a model
when `old` passes at most RED_MAX of 5. GREEN is met on a model where RED is shown when `new` passes at least
GREEN_MIN and at least `old` + GREEN_GAP. A case's RED is shown when it is shown on at least one model. It is
null only when each of the plan's two models (MODELS) has `old` reps and none shows RED, and it is incomplete
when a model has none. Its GREEN is n/a unless RED is shown. When RED is shown, GREEN is missed when a graded
model misses, else incomplete when a model where RED is shown has no `new` reps, else not run when none has
them, else incomplete when a plan model has no `old` reps (RED was never checked there), else met on every
model where RED is shown.
'''
import json
import random
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit  # noqa: E402
import cases  # noqa: E402

CASE_NAMES = sorted(cases.CASES)
# Every file of writing-skills, in either arm, other than the three that every skill holds.
NAMES = ('micro-tests.md', 'discovery.md', 'claude-code.md', 'bulletproofing.md', 'flowcharts.md',
         'persuasion-principles.md', 'testing-skills-with-subagents.md', 'graphviz-conventions.dot',
         'render_graphs.py', 'test_render_graphs.py')
MODELS = ('claude-opus-5-5', 'claude-sonnet-5-5')
SHARED = ('LICENSE-superpowers', 'LICENSE', 'SKILL.md')
MASK = '<skill>/'
# The characters that end a path token in prose, Markdown, JSON or a diff line.
DELIM = r'''\s'"`()\[\]{}<>,;:|*=+!?#&“”‘’'''
END = r'(?![\w-]|\.\w)'


def _names(names: tuple[str, ...]) -> str:
    return '|'.join(re.escape(name) for name in sorted(names, key=len, reverse=True))


PATH = re.compile(rf'(?<![^{DELIM}])(?:<skill>/)?(?:[^{DELIM}]*/)?(?P<name>{_names(NAMES)}){END}')
SHARED_PATH = re.compile(rf'(?<![^{DELIM}])(?:[^{DELIM}]*/)?writing-skills/(?P<name>{_names(SHARED)}){END}')
REP_FOLDER = re.compile(r'^rep([1-9][0-9]*)$')
ID_BITS = 24
GRADES = ('PASS', 'FAIL')
REPS = 5
RED_MAX = 2
GREEN_MIN = 4
GREEN_GAP = 2


def mask(text: str) -> str:
    '''Every path that ends in a writing-skills file name, as <skill>/<basename>.'''
    text = SHARED_PATH.sub(lambda match: MASK + match['name'], text)
    return PATH.sub(lambda match: MASK + match['name'], text)


def inside_git(path: Path) -> bool:
    probe = path
    while not probe.exists():
        probe = probe.parent
    found = subprocess.run(['git', '-C', str(probe), 'rev-parse', '--is-inside-work-tree'], capture_output=True,
                           text=True)
    return found.returncode == 0 and found.stdout.strip() == 'true'


def answer(rep: Path, summary: dict) -> str:
    diff = rep / 'final.diff'
    return (f'--- final message ---\n{mask(summary.get("final_message") or "")}\n'
            f'--- final.diff ---\n{mask(diff.read_text() if diff.is_file() else "")}')


def collect(runs_root: Path) -> tuple[list[dict], list[str]]:
    '''Each scored rep under runs_root, with its answer (None for R3), and a line for each void rep skipped.'''
    reps, skipped = [], []
    for case_dir in sorted(p for p in runs_root.iterdir() if not p.name.startswith('.')):
        if case_dir.name not in CASE_NAMES or not case_dir.is_dir():
            raise SystemExit(f'refusing: {case_dir} is not a case folder ({", ".join(CASE_NAMES)})')
        case = case_dir.name
        for arm_dir in sorted(p for p in case_dir.iterdir() if p.is_dir()):
            for model_dir in sorted(p for p in arm_dir.iterdir() if p.is_dir()):
                for path in sorted(model_dir.iterdir()):
                    if not (REP_FOLDER.match(path.name) and path.is_dir()):
                        continue
                    found = audit.audit_rep(path)
                    if found['void']:
                        skipped.append(f'{case} {arm_dir.name} {model_dir.name} {path.name}: '
                                       f'{"; ".join(found["void"])}')
                        continue
                    entry = {'case': case, 'arm': arm_dir.name, 'model': model_dir.name,
                             'rep': int(REP_FOLDER.match(path.name)[1]), 'mechanical': None, 'answer': None,
                             'reads': any(not read['error'] for read in found['reads'] or [])}
                    if case == 'R3':
                        if found['r3'] is None:
                            raise SystemExit(f'refusing: no R3 tree check for {case} {arm_dir.name} {model_dir.name} '
                                             f'{path.name}: its parked folder is missing and its summary holds none')
                        entry['mechanical'] = found['r3']['verdict']
                    else:
                        entry['answer'] = answer(path, found['summary'])
                    reps.append(entry)
    return reps, skipped


def sheet_text(case: str, text: str) -> str:
    pass_line, fail_line = cases.COLUMNS[case]
    head = f'Case: {case}\n\nPASS: {pass_line}\nFAIL: {fail_line}\n\n'
    return head + text.rstrip('\n') + '\n'


def build(runs_root: Path, sheet_dir: Path, seed: str) -> dict:
    key_path = sheet_dir.parent / 'key.json'
    for path in (sheet_dir, key_path):
        if path.exists():
            raise SystemExit(f'refusing: {path} exists')
    if inside_git(sheet_dir):
        raise SystemExit(f'refusing: {sheet_dir} is inside a git repository; put the sheets and the key in scratch')
    reps, skipped = collect(runs_root)
    reps.sort(key=lambda rep: (rep['case'], rep['arm'], rep['model'], rep['rep']))
    rng = random.Random(seed)
    rng.shuffle(reps)
    key, texts = {}, {}
    for rep in reps:
        sheet = f'{rng.getrandbits(ID_BITS):06x}'
        while sheet in key:
            sheet = f'{rng.getrandbits(ID_BITS):06x}'
        key[sheet] = {name: rep[name] for name in ('case', 'arm', 'model', 'rep', 'reads', 'mechanical')}
        if rep['answer'] is not None:
            texts[sheet] = sheet_text(rep['case'], rep['answer'])
    sheet_dir.mkdir(parents=True)
    for sheet, text in texts.items():
        (sheet_dir / f'{sheet}.txt').write_text(text)
    key_path.write_text(json.dumps(key, indent=2, sort_keys=True) + '\n')
    for line in skipped:
        print(f'skipped (void): {line}')
    print(f'wrote {len(texts)} sheet(s) to {sheet_dir} and the key to {key_path}; '
          f'{len(key) - len(texts)} mechanical rep(s) without a sheet; skipped {len(skipped)} void rep(s)')
    return key


def read_grades(path: Path) -> dict[str, str]:
    grades = {}
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip() or line.startswith('#'):
            continue
        fields = [field.strip() for field in line.split('\t')]
        if fields[0] == 'id':
            continue
        grade = fields[1].upper() if len(fields) > 1 else ''
        if grade not in GRADES:
            raise SystemExit(f'refusing: {path.name} line {number}: grade {grade or "(none)"!r} is not PASS or FAIL')
        if fields[0] in grades:
            raise SystemExit(f'refusing: {path.name} grades {fields[0]} twice')
        grades[fields[0]] = grade
    return grades


def judge_cells(rows: list[dict]) -> list[dict]:
    '''Each (case, model) cell's old and new pass counts, with RED and GREEN.'''
    cells = {}
    for row in rows:
        cells.setdefault((row['case'], row['model']), {}).setdefault(row['arm'], []).append(row['verdict'])
    found = []
    for (case, model), arms in sorted(cells.items()):
        old = sum(verdict == 'PASS' for verdict in arms.get('old', []))
        new = sum(verdict == 'PASS' for verdict in arms.get('new', []))
        old_n, new_n = len(arms.get('old', [])), len(arms.get('new', []))
        red = old <= RED_MAX if old_n else None
        green = (new >= GREEN_MIN and new >= old + GREEN_GAP) if red and new_n else None
        found.append({'case': case, 'model': model, 'old': old, 'new': new, 'old_n': old_n, 'new_n': new_n,
                      'red': red, 'green': green, 'complete': old_n == REPS and new_n == REPS})
    return found


def judge_cases(cells: list[dict]) -> dict:
    '''Each case's RED and GREEN verdict from its cells, which need both plan models to be conclusive.'''
    verdicts = {}
    for case in sorted({cell['case'] for cell in cells}):
        mine = [cell for cell in cells if cell['case'] == case]
        shown = [cell for cell in mine if cell['red']]
        if not shown:
            graded = {cell['model'] for cell in mine if cell['old_n']}
            verdicts[case] = {'red': 'null' if graded >= set(MODELS) else 'incomplete', 'green': 'n/a'}
            continue
        graded = [cell for cell in shown if cell['new_n']]
        if any(cell['green'] is False for cell in graded):
            green = 'missed'
        elif len(graded) < len(shown):
            green = 'incomplete' if graded else 'not run'
        else:
            checked = {cell['model'] for cell in mine if cell['old_n']}
            green = 'met' if checked >= set(MODELS) else 'incomplete'
        verdicts[case] = {'red': 'shown', 'green': green}
    return verdicts


def unblind(grades_path: Path, key_path: Path) -> dict:
    key = json.loads(key_path.read_text())
    grades = read_grades(grades_path)
    graded = {sheet for sheet, entry in key.items() if entry.get('mechanical') is None}
    missing, extra = sorted(graded - set(grades)), sorted(set(grades) - graded)
    if missing:
        raise SystemExit(f'refusing: no grade for sheet(s) {", ".join(missing)}')
    if extra:
        raise SystemExit(f'refusing: sheet(s) {", ".join(extra)} are in no key entry that takes a grade')
    rows = []
    for sheet, entry in key.items():
        grade = grades.get(sheet)
        rows.append({**entry, 'sheet': sheet, 'grade': grade, 'verdict': entry.get('mechanical') or grade})
    rows.sort(key=lambda row: (row['case'], row['arm'], row['model'], row['rep']))
    cells = judge_cells(rows)
    return {'rows': rows, 'cells': cells, 'verdicts': judge_cases(cells)}


def show_unblind(result: dict) -> None:
    for row in result['rows']:
        how = ' (mechanical)' if row.get('mechanical') else ''
        reads = '' if row.get('reads') is None else f', read the reference: {"yes" if row["reads"] else "no"}'
        print(f'{row["case"]} {row["arm"]} {row["model"]} rep{row["rep"]}: {row["verdict"]}{how}{reads}')
    for cell in result['cells']:
        red = 'n/a' if cell['red'] is None else 'shown' if cell['red'] else 'not shown'
        green = 'n/a' if cell['green'] is None else 'met' if cell['green'] else 'missed'
        print(f'{cell["case"]} {cell["model"]}: old {cell["old"]}/{cell["old_n"]}, new {cell["new"]}/{cell["new_n"]}: '
              f'RED {red}, GREEN {green}{"" if cell["complete"] else " (not 5 and 5 reps)"}')
    for case, verdict in result['verdicts'].items():
        print(f'{case}: RED {verdict["red"]}, GREEN {verdict["green"]}')


def main() -> None:
    if len(sys.argv) == 5 and sys.argv[1] == 'build':
        build(Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4])
        return
    if len(sys.argv) == 4 and sys.argv[1] == 'unblind':
        show_unblind(unblind(Path(sys.argv[2]), Path(sys.argv[3])))
        return
    raise SystemExit(__doc__)


if __name__ == '__main__':
    main()
