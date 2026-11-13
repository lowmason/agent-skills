'''Print reading aids for plan 93's implementer reps. It gives no verdicts.

Usage, from the repository root:
  uv run python <kit>/grade.py <out-dir> ...
Each <out-dir> is a fixture directory, such as implementer/control/F1, that holds the rep<N>/
folders run_reps.sh wrote. For each rep it prints:
- the run: exit, result subtype, cost, turns, wall time, the models in its usage, any iteration
  that is not a message (the advisor), and its permission denials;
- the lines that name a status, in the final message and in the report;
- the path audit: each Read, Edit or Write file_path, and each absolute path, `~` path or $HOME
  in a Bash command, that lies outside the rep directory, /tmp/mt-skill/ and /tmp/mt-venv/ (both
  the /tmp and /private/tmp forms), and each Bash command that holds `..`;
- the commits and the final `git status`;
- the plan tests: each test function in brief.md's code, IDENTICAL, CHANGED (with a diff) or
  MISSING in the rep's final tree, and the test functions the rep added;
- F1-F3, the kill check: in a scratch copy of the rep's final tree (the fixture's repo/ plus
  final.diff), the rep's final test files run with the focused command, first with the rep's
  module, then with wrong.py in its place, and each run's failing test IDs;
- F4, the lines of the final message and the report that hold `no rows for` or `^no rows$`;
- the lines that hold `concern`, and the final message, whole.
Scratch copies live under ~/.cache/agent-skills/scratch/plan93/grade/, outside /tmp, and are
removed after use.
'''
import ast
import difflib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

KIT = Path(__file__).resolve().parent
PY = '/tmp/mt-venv/bin/python'
MODULES = {'F1': 'latest', 'F2': 'checkconf', 'F3': 'wordcount', 'F4': 'monthly', 'F5': 'duration'}
KILL_FIXTURES = ('F1', 'F2', 'F3')
SHARED_ROOTS = ('/tmp/mt-skill', '/tmp/mt-venv')
SCRATCH = Path.home() / '.cache/agent-skills/scratch/plan93/grade'
PATH_IN_COMMAND = re.compile(r'''(?<![\w.\-/])(/[^\s'"`;|&<>(){}]*|~[^\s'"`;|&<>(){}]*|\$\{?HOME\}?)''')
STATUS_LINE = re.compile(r'status', re.I)
F4_MARKS = ('no rows for', '^no rows$')
TEST_TIMEOUT = 120


def roots(rep_dir: str) -> list[str]:
    forms = []
    for root in (rep_dir, *SHARED_ROOTS):
        forms += [root, root.replace('/tmp/', '/private/tmp/', 1)]
    return forms


def outside(path: str, allowed: list[str]) -> bool:
    return not any(path == root or path.startswith(root + '/') for root in allowed)


def path_audit(summary: dict) -> list[str]:
    allowed = roots(summary['rep_dir'])
    hits = []
    for number, call in enumerate(summary.get('tool_calls') or [], 1):
        args = call.get('input') or {}
        if call.get('name') in ('Read', 'Edit', 'Write'):
            path = args.get('file_path', '')
            if outside(path, allowed):
                hits.append(f'call {number} {call["name"]}: {path}')
        elif call.get('name') == 'Bash':
            command = args.get('command', '')
            for path in PATH_IN_COMMAND.findall(command):
                if outside(path.rstrip('/'), allowed):
                    note = ' (null device)' if path == '/dev/null' else ''
                    hits.append(f'call {number} Bash names {path}{note}')
            if '..' in command:
                hits.append(f'call {number} Bash holds "..": {command[:200]}')
    return hits


def test_functions(source: str) -> dict[str, str]:
    lines = source.splitlines()
    found = {}
    for node in ast.parse(source).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith('test'):
            start = min([node.lineno] + [d.lineno for d in node.decorator_list])
            found[node.name] = '\n'.join(lines[start - 1:node.end_lineno])
    return found


def plan_tests(fixture: str) -> dict[str, str]:
    brief = (KIT / 'fixtures' / fixture / 'brief.md').read_text()
    found = {}
    for block in re.findall(r'```python\n(.*?)```', brief, re.S):
        found.update(test_functions(block))
    return found


def test_files(tree: Path) -> list[Path]:
    files = [p for p in tree.rglob('*.py') if p.name.startswith('test_') or p.name.endswith('_test.py')]
    return sorted(p for p in files if '.git' not in p.parts and '.sdd' not in p.parts)


def rebuild(fixture: str, rep: Path, tree: Path) -> str:
    shutil.copytree(KIT / 'fixtures' / fixture / 'repo', tree)
    git = ['git', '-C', str(tree), '-c', 'user.name=grade', '-c', 'user.email=grade@example.invalid']
    subprocess.run(git + ['init', '-q'], check=True)
    subprocess.run(git + ['add', '-A'], check=True)
    subprocess.run(git + ['commit', '-q', '-m', 'base'], check=True)
    diff = (rep / 'final.diff').resolve()
    if not diff.exists() or diff.stat().st_size == 0:
        return 'final.diff is empty'
    applied = subprocess.run(git + ['apply', '--binary', str(diff)], capture_output=True, text=True)
    return 'applied final.diff' if applied.returncode == 0 else f'git apply failed: {applied.stderr.strip()}'


def run_tests(tree: Path, files: list[Path], label: str) -> str:
    report = tree.parent / f'{label}.xml'
    command = [PY, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', f'--basetemp={tree.parent / (label + "-tmp")}',
               f'--junitxml={report}', *[str(f.relative_to(tree)) for f in files]]
    try:
        result = subprocess.run(command, cwd=tree, capture_output=True, text=True, timeout=TEST_TIMEOUT,
                                env={'PATH': '/usr/bin:/bin', 'PYTHONDONTWRITEBYTECODE': '1'})
    except subprocess.TimeoutExpired:
        return f'{label}: timeout after {TEST_TIMEOUT}s'
    last = (result.stdout.strip().splitlines() or ['(no output)'])[-1]
    failed = []
    if report.exists():
        for case in ET.parse(report).getroot().iter('testcase'):
            if case.find('failure') is not None or case.find('error') is not None:
                failed.append(f'{case.get("classname")}::{case.get("name")}')
    return f'{label}: exit {result.returncode}, {last}; failing: {", ".join(failed) or "none"}'


def show_tests(fixture: str, rep: Path, tree: Path) -> None:
    final = {}
    for path in test_files(tree):
        try:
            for name, text in test_functions(path.read_text()).items():
                final.setdefault(name, []).append((path.relative_to(tree), text))
        except SyntaxError as error:
            print(f'  {path.relative_to(tree)}: does not parse: {error}')
    planned = plan_tests(fixture)
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
    added = [f'{name} ({copies[0][0]})' for name, copies in final.items() if name not in planned]
    print(f'  added test functions: {", ".join(added) or "none"}')
    if fixture in KILL_FIXTURES:
        files = test_files(tree)
        print('  kill check, ' + run_tests(tree, files, 'own-module'))
        shutil.copy(KIT / 'fixtures' / fixture / 'wrong.py', tree / f'{MODULES[fixture]}.py')
        print('  kill check, ' + run_tests(tree, files, 'wrong-py'))


def marked_lines(text: str, marks) -> list[str]:
    return [line.strip() for line in text.splitlines() if any(m(line) for m in marks)]


def grade(rep: Path, fixture: str) -> None:
    print(f'== {fixture} {rep.name}')
    summary = json.loads((rep / 'summary.json').read_text())
    if 'kit_error' in summary:
        print(f'  kit error: {summary["kit_error"]}')
        return
    result = summary.get('result') or {}
    models = sorted((result.get('modelUsage') or {}).keys())
    others = [t for t in result.get('iterations') or [] if t != 'message']
    print(f'  exit {summary["claude_exit"]}, subtype {result.get("subtype")}, is_error {result.get("is_error")}, '
          f'cost {result.get("total_cost_usd")}, turns {result.get("num_turns")}, wall {summary["wall_seconds"]}s')
    print(f'  models {models}; other iterations {others or "none"}; '
          f'denials {len(result.get("permission_denials") or [])}; tool calls {len(summary.get("tool_calls") or [])}')
    for denial in result.get('permission_denials') or []:
        print(f'  denied {denial["tool_name"]}: {json.dumps(denial["tool_input"])[:200]}')
    final = summary.get('final_message') or ''
    report_path = rep / 'task-1-report.md'
    report = report_path.read_text() if report_path.exists() else ''
    for where, text in (('final', final), ('report', report)):
        for line in marked_lines(text, [STATUS_LINE.search]):
            print(f'  {where} status line: {line}')
    print(f'  report file: {"present" if report else "absent"}; copied: {summary.get("copied")}')
    hits = path_audit(summary)
    print(f'  path audit: {len(hits)} hit(s)')
    for hit in hits:
        print(f'    {hit}')
    print(f'  commits: {summary.get("commits")}')
    print(f'  git status: {summary.get("status_porcelain") or "clean"}')
    SCRATCH.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        tree = Path(tmp) / 'repo'
        print(f'  rebuild: {rebuild(fixture, rep, tree)}')
        show_tests(fixture, rep, tree)
    if fixture == 'F4':
        for where, text in (('final', final), ('report', report)):
            for line in marked_lines(text, [lambda s, m=m: m in s for m in F4_MARKS]):
                print(f'  F4 {where}: {line}')
    for where, text in (('final', final), ('report', report)):
        for line in marked_lines(text, [lambda s: 'concern' in s.lower()]):
            print(f'  concern line, {where}: {line}')
    print('  final message:')
    for line in final.splitlines():
        print(f'    | {line}')


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for arg in sys.argv[1:]:
        out_dir = Path(arg)
        fixture = out_dir.name
        if fixture not in MODULES:
            raise SystemExit(f'refusing: {out_dir} is not a fixture directory (F1-F5)')
        reps = sorted((p for p in out_dir.glob('rep*') if p.is_dir()), key=lambda p: int(p.name[3:]))
        for rep in reps:
            grade(rep, fixture)


if __name__ == '__main__':
    main()
