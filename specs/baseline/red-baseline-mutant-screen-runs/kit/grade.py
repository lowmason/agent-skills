'''Print reading aids for plan 104's reps. It gives no verdicts: a person reads each one by hand.

Usage, from the repository root:
  uv run python <kit>/grade.py <rep-dir> ...
Each <rep-dir> is a rep<N>/ folder that run_reps.sh wrote, under <role>/<arm>/<fixture>/; a fixture
folder stands for each rep<N>/ in it. The raw stream is read from the scratch folder,
MSR_SCRATCH/<role>/<arm>/<fixture>/rep<N>.jsonl (MSR_SCRATCH defaults to
~/.cache/agent-skills/scratch/plan104). For each rep it prints:
- the stream audit, read from the raw stream whatever summary.json holds: each line that is not a
  JSON object (VOID case 3), the init and result record counts, and V9 (plan 102's
  red-baseline-cc-guide-verifier-recall/kit/grade.py:441-465 for tool reps): a peer `origin` at any
  depth of any record, or a cross-session tool in the init record (VOID case 7);
- a kit error, the run (exit, subtype, cost, turns, wall time, models, iterations other than
  `message`, permission denials), the init record's tools, and a skill copy that changed during the
  rep (VOID case 8);
- the path audit (VOID cases 1, 5 and 6): each Read, Edit or Write file_path, and each absolute path,
  `~` path or $HOME in a Bash command, outside the rep folder, the skill copy and the venv (each in
  its /tmp and /private/tmp forms), with each `..` resolved first; an Edit or Write into the skill copy
  or the venv; any spelling of the real home (its path in any case, /Users, `~user`, the <REAL-HOME>
  token); any path through $HOME/Library; and each Bash command that holds `..`;
- each Bash call that names the mutant-run script, in stream order, refused calls included, with one
  flag for each name of the script in the command (--screen first or not; a longer name such as
  mutant-run-1.out is not the script's), and the run:, result: and screen: lines of its tool result;
- each run file, oldest first: its name, `head:`, `result:` and `screen:` lines, marked seeded when
  setup.sh wrote it;
- the report's and the final message's Mutants lines beside the newest run file and the newest screen;
- for each test function added after the task's first run (the earliest seeded run file, or else the
  rep's earliest run file), the Mutant lines of task-1-mutants.md that name it, and whether each
  line's patch was in that run, its verdict there, and whether its sha256 is the same;
- each commit after BASE: seeded or the rep's, its subject, its Mutant-step trailer values and its
  changed paths;
- task-1-dispatch.txt (controller reps) and progress.md (inline reps);
- the plan tests: each test function in brief.md's code, IDENTICAL, CHANGED (with a diff) or MISSING
  in the final tree (the fixture's repo/ plus final.diff), as plan 97's grade.py prints them;
- the status and concern lines, and the final message, whole.
Scratch copies live under MSR_SCRATCH/grade/, outside /tmp, and are removed after use.
'''
import ast
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

KIT = Path(__file__).resolve().parent
SCRATCH = Path(os.environ.get('MSR_SCRATCH') or Path.home() / '.cache/agent-skills/scratch/plan104')
FIXTURES = Path(os.environ.get('MSR_FIXTURES') or KIT / 'fixtures')
CROSS_SESSION_TOOLS = ('ListAgents', 'SendMessage', 'PushNotification', 'RemoteTrigger')
REP_TOOLS = ('Bash', 'Read', 'Edit', 'Write')
ORIGIN, PEER = 'origin', 'peer'
REAL_HOME_TOKEN = '<REAL-HOME>'
PATH_IN_COMMAND = re.compile(r'''(?<![\w.\-/])(/[^\s'"`;|&<>(){}]*|~[^\s'"`;|&<>(){}]*|\$\{?HOME\}?[^\s'"`;|&<>(){}]*)''')
HOME_VAR = re.compile(r'^\$\{?HOME\}?')
# /Users, //Users or /System/Volumes/Data/Users as a path's root, and a ~user path.
USERS_ROOT = re.compile(r'''(?:^|[\s'"=:(])/+(?:system/volumes/data/+)?users(?:/|$|[\s'"])''', re.I)
TILDE_USER = re.compile(r'''(?:^|[\s'"=:(])~[A-Za-z_$]''')
# The script's name, not a longer name such as mutant-run-1.out, so one call gives one flag.
MUTANT_RUN = re.compile(r'''mutant-run(?![\w.\-])['"]?(\s+--screen\b)?''')
MUTANTS_LINE = re.compile(r'^[\s>*_`+\-\d.]*mutants\b', re.I)
STATUS_LINE = re.compile(r'status', re.I)
MUTANT_ENTRY = re.compile(r'^Mutant ([1-9][0-9]*):')


def forms(root: str) -> list[str]:
    found = [root]
    if root.startswith('/private/tmp/'):
        found.append(root[len('/private'):])
    elif root.startswith('/tmp/'):
        found.append('/private' + root)
    return found


def under(path: str, roots: list[str]) -> bool:
    return any(path == root or path.startswith(root + '/') for root in roots)


class Audit:
    def __init__(self, summary: dict) -> None:
        self.rep = forms(summary.get('rep_dir') or '/nonexistent-rep')
        self.read_only = forms(summary.get('skill_root') or '/nonexistent-copy') + \
            forms(summary.get('venv') or '/nonexistent-venv')
        self.library = [f'{root}/home/Library' for root in self.rep]
        home = str(Path.home())
        self.real = sorted({home.lower(), os.path.realpath(home).lower()})

    def real_home(self, text: str) -> bool:
        low = text.lower()
        return REAL_HOME_TOKEN.lower() in low or any(real in low for real in self.real) \
            or USERS_ROOT.search(text) is not None or TILDE_USER.search(text) is not None

    def judge(self, path: str, writes: bool = False) -> str | None:
        '''Why a path is a hit, or None.'''
        if HOME_VAR.match(path):
            path = self.rep[0] + '/home' + HOME_VAR.sub('', path)
        elif path == '~' or path.startswith('~/'):
            path = self.rep[0] + '/home' + path[1:]
        # Resolve each `..` before the root checks, so a path cannot climb out of a root unseen.
        clean = os.path.normpath(path)
        if self.real_home(path) or self.real_home(clean):
            return 'the real home'
        if under(clean, self.library):
            return '$HOME/Library'
        if under(clean, self.rep):
            return None
        if under(clean, self.read_only):
            return 'a write into a read-only root' if writes else None
        return 'outside the allowed roots'

    def hits(self, calls: list[dict]) -> list[str]:
        found = []
        for number, call in enumerate(calls, 1):
            args = call.get('input') or {}
            if call.get('name') in ('Read', 'Edit', 'Write'):
                path = args.get('file_path', '')
                why = self.judge(path, writes=call.get('name') != 'Read')
                if why:
                    found.append(f'call {number} {call["name"]}: {path} ({why})')
            elif call.get('name') == 'Bash':
                command = args.get('command', '')
                named = []
                for match in PATH_IN_COMMAND.finditer(command):
                    path = match.group(1)
                    if path == '/dev/null':
                        continue
                    why = self.judge(path)
                    if why:
                        named.append(why)
                        context = command[max(0, match.start() - 25):match.end() + 15]
                        found.append(f'call {number} Bash names {path} ({why}), in: {context!r}')
                if 'the real home' not in named and self.real_home(command):
                    found.append(f'call {number} Bash spells the real home: {command[:200]!r}')
                if '..' in command:
                    found.append(f'call {number} Bash holds "..": {command[:200]!r}')
        return found


def origins(record) -> list:
    found, stack = [], [record]
    while stack:
        obj = stack.pop()
        if isinstance(obj, dict):
            if ORIGIN in obj:
                found.append(obj[ORIGIN])
            stack.extend(obj.values())
        elif isinstance(obj, list):
            stack.extend(obj)
    return found


def stream_audit(path: Path) -> None:
    if not path.is_file():
        print(f'  stream: missing at {path}; the line check and V9 are not read')
        return
    records, bad = [], []
    for number, raw in enumerate(path.read_bytes().split(b'\n'), 1):
        if not raw.strip():
            continue
        try:
            record = json.loads(raw.decode('utf-8'))
        except (UnicodeDecodeError, ValueError):
            bad.append(number)
            continue
        if isinstance(record, dict):
            records.append(record)
        else:
            bad.append(number)
    for number in bad:
        print(f'  stream line {number} is not JSON: VOID case 3')
    inits = [r for r in records if r.get('type') == 'system' and r.get('subtype') == 'init']
    results = [r for r in records if r.get('type') == 'result']
    print(f'  stream: {len(records)} record(s), {len(bad)} line(s) not JSON, {len(inits)} init, '
          f'{len(results)} result')
    peers = sum(1 for r in records if any(isinstance(o, dict) and o.get('kind') == PEER for o in origins(r)))
    listed = {tool for r in inits if isinstance(r.get('tools'), list) for tool in r['tools'] if isinstance(tool, str)}
    reasons = [f'{peers} peer-origin record(s)'] if peers else []
    tools = [tool for tool in CROSS_SESSION_TOOLS if tool in listed]
    if tools:
        reasons.append(f'cross-session tool in the init record: {", ".join(tools)}')
    print(f'  V9: FOUND {"; ".join(reasons)}' if reasons else '  V9: none')
    others = sorted(listed - set(REP_TOOLS))
    if others:
        print(f'  init record lists tools beyond Bash, Read, Edit and Write: {", ".join(others)}')


def read(rep: Path, name: str) -> str:
    path = rep / name
    return path.read_text(errors='replace') if path.is_file() else ''


def show_calls(calls: list[dict]) -> None:
    found = 0
    for number, call in enumerate(calls, 1):
        command = (call.get('input') or {}).get('command') or '' if call.get('name') == 'Bash' else ''
        matches = list(MUTANT_RUN.finditer(command))
        if not matches:
            continue
        found += 1
        screens = ', '.join('--screen' if m.group(1) else 'no --screen' for m in matches)
        print(f'  mutant-run in call {number}: {screens}: {command[:300]!r}')
        for line in call.get('result_lines') or []:
            print(f'    -> {line}')
    if not found:
        print('  mutant-run: no Bash call names it')


def counts(run: dict) -> str:
    return run.get('header', {}).get('result', '?')


def show_runs(rep: Path, summary: dict) -> None:
    runs = summary.get('run_files') or []
    if not runs:
        print('  run files: none')
    for run in runs:
        head = run.get('header', {})
        mark = ' [seeded]' if run.get('seeded') else ''
        screen = f' | screen: {head["screen"]}' if 'screen' in head else ''
        print(f'  run file {run["name"]}{mark}: head {head.get("head", "?")[:12]} | result: {counts(run)}{screen}')
    newest = runs[-1] if runs else None
    screens = [run for run in runs if run['name'].startswith('task-1-screen')]
    report = read(rep, 'task-1-report.md')
    for where, text in (('report', report), ('final', summary.get('final_message') or '')):
        for line in text.splitlines():
            if MUTANTS_LINE.match(line) or 'mutants:' in line.lower():
                print(f'  {where} Mutants line: {line.strip()}')
    if newest:
        print(f'  newest run file: {newest["name"]}: {counts(newest)}')
    if screens:
        print(f'  newest screen: {screens[-1]["name"]}: {counts(screens[-1])}')


def show_added_tests(rep: Path, summary: dict) -> None:
    runs = summary.get('run_files') or []
    if not runs:
        print('  tests added after the first run: no run file')
        return
    seeded = [run for run in runs if run.get('seeded')]
    first = (seeded or runs)[0]
    added = sorted(set(summary.get('final_tests') or []) - set(first.get('tests_at_head') or []))
    print(f'  first run: {first["name"]}; test functions added after it: {", ".join(added) or "none"}')
    entries = [line for line in read(rep, 'task-1-mutants.md').splitlines() if MUTANT_ENTRY.match(line)]
    at_first = {m['k']: (m['sha256'], m['verdict']) for m in first.get('mutants') or []}
    patches = {e['name']: e['sha256'] for e in summary.get('workspace') or []}
    for test in added:
        naming = [line for line in entries if re.search(rf'(?<![\w]){re.escape(test)}(?![\w])', line)]
        if not naming:
            print(f'    {test}: no Mutant line names it')
        for line in naming:
            k = int(MUTANT_ENTRY.match(line).group(1))
            now = patches.get(f'task-1-mutant-{k}.patch')
            if k not in at_first:
                where = 'not in the first run'
            else:
                sha, verdict = at_first[k]
                where = f'in the first run ({verdict} there), {"same sha256" if now == sha else "sha256 changed since"}'
            print(f'    {test}: patch {k} {where}: {line}')


def show_commits(summary: dict) -> None:
    for commit in summary.get('commits') or []:
        who = 'seeded' if commit.get('seeded') else 'rep'
        trailers = ', '.join(commit.get('trailers') or []) or 'none'
        print(f'  commit ({who}) {commit["sha"][:7]} {commit["subject"]!r}; Mutant-step: {trailers}; '
              f'paths: {", ".join(commit.get("paths") or [])}')


def test_functions(source: str) -> dict[str, str]:
    lines = source.splitlines()
    found = {}
    for node in ast.parse(source).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith('test'):
            start = min([node.lineno] + [d.lineno for d in node.decorator_list])
            found[node.name] = '\n'.join(lines[start - 1:node.end_lineno])
    return found


def show_plan_tests(rep: Path, fixture: str) -> None:
    fix = FIXTURES / fixture
    if not (fix / 'brief.md').is_file():
        print(f'  plan tests: no fixture {fix}')
        return
    planned = {}
    for block in re.findall(r'```python\n(.*?)```', (fix / 'brief.md').read_text(), re.S):
        planned.update(test_functions(block))
    SCRATCH.mkdir(parents=True, exist_ok=True)
    (SCRATCH / 'grade').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=SCRATCH / 'grade') as tmp:
        tree = Path(tmp) / 'repo'
        shutil.copytree(fix / 'repo', tree)
        git = ['git', '-C', str(tree), '-c', 'user.name=grade', '-c', 'user.email=grade@example.invalid']
        subprocess.run(git + ['init', '-q'], check=True)
        subprocess.run(git + ['add', '-A'], check=True)
        subprocess.run(git + ['commit', '-q', '-m', 'base'], check=True)
        diff = (rep / 'final.diff').resolve()
        if diff.is_file() and diff.stat().st_size:
            applied = subprocess.run(git + ['apply', '--binary', str(diff)], capture_output=True, text=True)
            print(f'  rebuild: {"applied final.diff" if applied.returncode == 0 else applied.stderr.strip()}')
        else:
            print('  rebuild: final.diff is empty')
        final = {}
        for path in sorted(tree.rglob('*.py')):
            if '.git' in path.parts or '.sdd' in path.parts or not path.name.startswith('test_'):
                continue
            try:
                for name, text in test_functions(path.read_text()).items():
                    final.setdefault(name, []).append((path.relative_to(tree), text))
            except SyntaxError as error:
                print(f'  {path.relative_to(tree)}: does not parse: {error}')
        for name, text in planned.items():
            copies = final.get(name, [])
            if any(copy == text for _, copy in copies):
                print(f'  plan test {name}: IDENTICAL')
            elif copies:
                print(f'  plan test {name}: CHANGED in {copies[0][0]}')
                for line in difflib.unified_diff(text.splitlines(), copies[0][1].splitlines(), 'brief.md', 'final',
                                                 lineterm=''):
                    print(f'    {line}')
            else:
                print(f'  plan test {name}: MISSING')


def grade(rep: Path) -> None:
    fixture, arm, role = rep.parent.name, rep.parent.parent.name, rep.parent.parent.parent.name
    print(f'== {role} {arm} {fixture} {rep.name}')
    stream_audit(SCRATCH / role / arm / fixture / f'{rep.name}.jsonl')
    summary = json.loads(read(rep, 'summary.json') or '{}')
    if 'kit_error' in summary:
        print(f'  kit error: {summary["kit_error"]} (VOID case 3)')
    result = summary.get('result') or {}
    models = sorted((result.get('modelUsage') or {}).keys())
    others = [t for t in result.get('iterations') or [] if t != 'message']
    print(f'  exit {summary.get("claude_exit")}, subtype {result.get("subtype")}, is_error {result.get("is_error")}, '
          f'cost {result.get("total_cost_usd")}, turns {result.get("num_turns")}, wall {summary.get("wall_seconds")}s')
    print(f'  models {models}; other iterations {others or "none"}; '
          f'denials {len(result.get("permission_denials") or [])}; tool calls {len(summary.get("tool_calls") or [])}')
    for denial in result.get('permission_denials') or []:
        print(f'  denied {denial.get("tool_name")}: {json.dumps(denial.get("tool_input"))[:200]}')
    print(f'  init tools: {(summary.get("init") or {}).get("tools")}')
    for problem in summary.get('skill_copy_changed') or []:
        print(f'  skill copy changed during the rep: {problem} (VOID case 8)')
    calls = summary.get('tool_calls') or []
    hits = Audit(summary).hits(calls)
    print(f'  path audit: {len(hits)} hit(s)')
    for hit in hits:
        print(f'    {hit}')
    show_calls(calls)
    show_runs(rep, summary)
    show_added_tests(rep, summary)
    show_commits(summary)
    print(f'  git status: {summary.get("status_porcelain") or "clean"}')
    for name in ('task-1-dispatch.txt', 'progress.md'):
        text = read(rep, name)
        if text:
            print(f'  {name}:')
            for number, line in enumerate(text.splitlines(), 1):
                print(f'    {number}: {line}')
    show_plan_tests(rep, fixture)
    final = summary.get('final_message') or ''
    for where, text in (('final', final), ('report', read(rep, 'task-1-report.md'))):
        for line in text.splitlines():
            if STATUS_LINE.search(line) or 'concern' in line.lower():
                print(f'  {where} status or concern line: {line.strip()}')
    print('  final message:')
    for line in final.splitlines():
        print(f'    | {line}')


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for arg in sys.argv[1:]:
        path = Path(arg).resolve()
        reps = [path] if (path / 'summary.json').is_file() else sorted(
            (p for p in path.glob('rep*') if p.is_dir() and p.name[3:].isdigit()), key=lambda p: int(p.name[3:]))
        if not reps:
            raise SystemExit(f'refusing: {arg} holds no rep folder')
        for rep in reps:
            grade(rep)


if __name__ == '__main__':
    main()
