'''Write the blind grading sheets of plan 105's guard run, and unblind the grades.

Usage, from the repository root:
  uv run python <kit>/sheets.py build <runs-root> <sheet-dir> <seed>
  uv run python <kit>/sheets.py unblind <grades.tsv> <key.json>

build reads <runs-root>/<case>/<arm>/<model>/: rep<N>.json for a W rep (run_json_reps.sh's kept copy) and
rep<N>/ for a T rep (run_tool_reps.sh's folder). It skips a void rep: a W rep with a rep<N>.VOID note and
no rep<N>.json, a W rep whose kept JSON shows a run error (a subtype other than success, or is_error
true), and a T rep that audit.py gives a VOID reason. It writes one sheet per scored rep to
<sheet-dir>/<id>.txt, where <id> is a 6-hex id drawn from <seed>, so the same seed gives the same ids. A
sheet holds the case, its PASS and FAIL columns (cases.COLUMNS) and the rep's answer: for a W rep its
result text, and for a T rep its final message and final.diff. It never names the arm, the model or the
rep. In the answer, every path that ends in a writing-skills file name becomes <skill>/<basename>, so a
path that a moved file changes reads the same in both arms. SKILL.md, LICENSE and LICENSE-superpowers
become <skill>/<basename> only after `writing-skills/`, because each T2 and T3 target is a SKILL.md too
and those three files do not move. The key, each sheet id with its case, arm, model, rep and (T reps)
audit.py's read check, goes to <sheet-dir>/../key.json. build refuses an existing <sheet-dir> or
key.json, and a <sheet-dir> inside a git repository, so neither the sheets nor the key can be committed.
Read the key only after every sheet is graded.

unblind reads grades.tsv, one `<id><TAB>PASS|FAIL` line per sheet (more columns, a header line that
starts with `id`, blank lines and `#` lines are ignored), and refuses a missing, extra, repeated or
unknown grade. A W rep's verdict is its grade. A T rep passes when both parts of the reading rule hold:
the read check in the key and the grader's PASS for the marker. It prints each rep's verdict, then for
each case and model with both arms the old and new pass counts against the bars (new >= old - 1, and
new >= 4 for a W case), then the guard. The guard is PASS when all 12 cells (6 cases x 2 models) are
there with 5 reps in each arm and each meets its bars, FAIL when one of them misses, and incomplete
when a cell is missing or has another count.
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

CASE_NAMES = sorted(cases.W_TARGET) + sorted(cases.TARGET)
# The writing-skills file names in either arm, other than the three that never move.
NAMES = ('testing-skills-with-subagents.md', 'persuasion-principles.md', 'graphviz-conventions.dot',
         'bulletproofing.md', 'claude-code.md', 'discovery.md', 'flowcharts.md', 'test_render_graphs.py',
         'render_graphs.py')
SHARED = ('LICENSE-superpowers', 'LICENSE', 'SKILL.md')
MASK = '<skill>/'
# The characters that end a path token in prose, Markdown, JSON or a diff line.
DELIM = r'''\s'"`()\[\]{}<>,;:|*=+!?#&“”‘’'''
END = r'(?![\w-]|\.\w)'


def _names(names: tuple[str, ...]) -> str:
    return '|'.join(re.escape(name) for name in sorted(names, key=len, reverse=True))


PATH = re.compile(rf'(?<![^{DELIM}])(?:<skill>/)?(?:[^{DELIM}]*/)?(?P<name>{_names(NAMES)}){END}')
SHARED_PATH = re.compile(rf'(?<![^{DELIM}])(?:[^{DELIM}]*/)?writing-skills/(?P<name>{_names(SHARED)}){END}')
REP_JSON = re.compile(r'^rep([1-9][0-9]*)\.json$')
REP_VOID = re.compile(r'^rep([1-9][0-9]*)\.VOID$')
REP_FOLDER = re.compile(r'^rep([1-9][0-9]*)$')
ID_BITS = 24
GRADES = ('PASS', 'FAIL')
REPS = 5
W_BAR = 4
MODELS = ('claude-opus-5-5', 'claude-sonnet-5-5')
# Every case and model: the guard passes only when each one meets its bars.
CELLS = {(case, model) for case in CASE_NAMES for model in MODELS}


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


def w_answer(path: Path) -> str:
    try:
        rep = json.loads(path.read_text())
    except (OSError, ValueError) as error:
        raise SystemExit(f'refusing: {path} is not a kept rep: {error}') from None
    return mask(str(rep.get('result') or ''))


def w_run_error(path: Path) -> str | None:
    '''Why a kept W rep is void: its run errored, so it gave no answer to grade, as for a T rep.'''
    try:
        rep = json.loads(path.read_text())
    except (OSError, ValueError) as error:
        raise SystemExit(f'refusing: {path} is not a kept rep: {error}') from None
    if not isinstance(rep, dict):
        raise SystemExit(f'refusing: {path} is not a kept rep: not a JSON object')
    if rep.get('subtype') != 'success':
        return f'a run error: subtype {rep.get("subtype")}'
    if rep.get('is_error'):
        return 'a run error: is_error true'
    return None


def t_answer(rep: Path, summary: dict) -> str:
    diff = rep / 'final.diff'
    return (f'--- final message ---\n{mask(summary.get("final_message") or "")}\n'
            f'--- final.diff ---\n{mask(diff.read_text() if diff.is_file() else "")}')


def collect(runs_root: Path) -> tuple[list[dict], list[str]]:
    '''Each scored rep under runs_root, with its answer, and a line for each void rep skipped.'''
    reps, skipped = [], []
    for case_dir in sorted(p for p in runs_root.iterdir() if not p.name.startswith('.')):
        if case_dir.name not in CASE_NAMES or not case_dir.is_dir():
            raise SystemExit(f'refusing: {case_dir} is not a case folder ({", ".join(CASE_NAMES)})')
        case = case_dir.name
        for arm_dir in sorted(p for p in case_dir.iterdir() if p.is_dir()):
            for model_dir in sorted(p for p in arm_dir.iterdir() if p.is_dir()):
                where = {'case': case, 'arm': arm_dir.name, 'model': model_dir.name}
                for path in sorted(model_dir.iterdir()):
                    if case in cases.W_TARGET and REP_JSON.match(path.name):
                        why = w_run_error(path)
                        if why:
                            skipped.append(f'{case} {arm_dir.name} {model_dir.name} {path.stem}: {why}')
                            continue
                        reps.append({**where, 'rep': int(REP_JSON.match(path.name)[1]), 'read': None,
                                     'answer': w_answer(path)})
                    elif case in cases.W_TARGET and REP_VOID.match(path.name):
                        skipped.append(f'{case} {arm_dir.name} {model_dir.name} {path.stem}: VOID note')
                    elif case in cases.TARGET and REP_FOLDER.match(path.name) and path.is_dir():
                        found = audit.audit_rep(path)
                        if found['void']:
                            skipped.append(f'{case} {arm_dir.name} {model_dir.name} {path.name}: '
                                           f'{"; ".join(found["void"])}')
                            continue
                        reps.append({**where, 'rep': int(REP_FOLDER.match(path.name)[1]),
                                     'read': found['read']['verdict'], 'answer': t_answer(path, found['summary'])})
    return reps, skipped


def sheet_text(case: str, answer: str) -> str:
    pass_line, fail_line = cases.COLUMNS[case]
    head = f'Case: {case}\n\nPASS: {pass_line}\nFAIL: {fail_line}\n\n'
    body = answer if case in cases.TARGET else f'--- answer ---\n{answer}'
    return head + body.rstrip('\n') + '\n'


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
        key[sheet] = {name: rep[name] for name in ('case', 'arm', 'model', 'rep', 'read')}
        texts[sheet] = sheet_text(rep['case'], rep['answer'])
    sheet_dir.mkdir(parents=True)
    for sheet, text in texts.items():
        (sheet_dir / f'{sheet}.txt').write_text(text)
    key_path.write_text(json.dumps(key, indent=2, sort_keys=True) + '\n')
    for line in skipped:
        print(f'skipped (void): {line}')
    print(f'wrote {len(texts)} sheet(s) to {sheet_dir} and the key to {key_path}; skipped {len(skipped)} void rep(s)')
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


def unblind(grades_path: Path, key_path: Path) -> dict:
    key = json.loads(key_path.read_text())
    grades = read_grades(grades_path)
    missing, extra = sorted(set(key) - set(grades)), sorted(set(grades) - set(key))
    if missing:
        raise SystemExit(f'refusing: no grade for sheet(s) {", ".join(missing)}')
    if extra:
        raise SystemExit(f'refusing: sheet(s) {", ".join(extra)} are in no key entry')
    rows = []
    for sheet, entry in key.items():
        grade = grades[sheet]
        if entry['case'] in cases.TARGET:
            verdict = 'PASS' if entry.get('read') == 'PASS' and grade == 'PASS' else 'FAIL'
        else:
            verdict = grade
        rows.append({**entry, 'sheet': sheet, 'grade': grade, 'verdict': verdict})
    rows.sort(key=lambda row: (row['case'], row['arm'], row['model'], row['rep']))
    cells = {}
    for row in rows:
        cells.setdefault((row['case'], row['model']), {}).setdefault(row['arm'], []).append(row['verdict'])
    bars = []
    for (case, model), arms in sorted(cells.items()):
        if 'old' not in arms or 'new' not in arms:
            continue
        old, new = (sum(verdict == 'PASS' for verdict in arms[arm]) for arm in ('old', 'new'))
        meets = new >= old - 1 and (case not in cases.W_TARGET or new >= W_BAR)
        bars.append({'case': case, 'model': model, 'old': old, 'new': new, 'old_n': len(arms['old']),
                     'new_n': len(arms['new']), 'meets': meets})
    if {(cell['case'], cell['model']) for cell in bars} != CELLS \
            or any(cell['old_n'] != REPS or cell['new_n'] != REPS for cell in bars):
        guard = 'incomplete'
    else:
        guard = 'PASS' if all(cell['meets'] for cell in bars) else 'FAIL'
    return {'rows': rows, 'bars': bars, 'guard': guard}


def main() -> None:
    if len(sys.argv) == 5 and sys.argv[1] == 'build':
        build(Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4])
        return
    if len(sys.argv) == 4 and sys.argv[1] == 'unblind':
        result = unblind(Path(sys.argv[2]), Path(sys.argv[3]))
        for row in result['rows']:
            parts = f' (read {row["read"]}, use {row["grade"]})' if row['case'] in cases.TARGET else ''
            print(f'{row["case"]} {row["arm"]} {row["model"]} rep{row["rep"]}: {row["verdict"]}{parts}')
        for cell in result['bars']:
            print(f'{cell["case"]} {cell["model"]}: old {cell["old"]}/{cell["old_n"]}, new {cell["new"]}/'
                  f'{cell["new_n"]}: {"meets" if cell["meets"] else "misses"} the bars')
        print(f'guard: {result["guard"]} ({len(result["bars"])} case and model cell(s); a full run has 12)')
        return
    raise SystemExit(__doc__)


if __name__ == '__main__':
    main()
