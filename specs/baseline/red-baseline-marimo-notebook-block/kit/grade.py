'''Print reading aids for plan 98's tool-enabled reps. It gives no verdicts.

Usage, from the repository root:
  uv run python <kit>/grade.py <out-dir> ...
Each <out-dir> holds the rep<N>/ folders that run_reps.sh wrote, such as runs/control/explore.
For each rep it prints:
- the run: arm, case, exit, result subtype, cost, turns, wall time, the models in its usage, any
  iteration that is not a message (the advisor), its permission denials, the init record's tools,
  skills, MCP servers and output style, and whether its CLAUDE.md matches its arm;
- the cells of the final notebook in file order, each tagged base or new against the case's
  starting notebook by source text, with its name, markdown, code or function (`@app.function`),
  and first line; the full text
  of each new markdown cell; the last statement of each new code cell, which is what it displays;
  and the starting cells that no longer appear unchanged;
- each Write or Edit call on the notebook, and each Bash command that names the notebook with
  --fix, sed -i, a redirect, tee or a write call, or that runs ruff --fix, ruff format, sed -i or
  marimo convert anywhere; whether final.diff changes the notebook;
- each Bash command that runs the notebook (python on it, marimo export or run, app.run) or checks
  it (marimo check), with its call number and whether its result was an error, and the call number
  of the last notebook write. A call that both writes and runs the notebook is flagged, because
  reading note 7 then turns on the order of the two inside the command;
- conclusion phrases in new markdown cells and in the final message;
- model-fit calls in new code cells, and in Bash commands as a separate note;
- each tool input that names agent-skills, specs/, /Users/, a `~` path or $HOME. The summaries
  write $HOME as `~`, so a `~` path in a summary was a path under /Users/; and, as a separate
  note, each input that names a /tmp/mnb98/ path other than the rep's own and the venv, or `../`;
- the final message, whole.
'''
import ast
import json
import re
import sys
import textwrap
from pathlib import Path

KIT = Path(__file__).resolve().parent
NOTEBOOKS = {
    'explore': KIT / 'fixture/repo/notebooks/explore.py',
    'override': KIT / 'fixture/repo/notebooks/explore.py',
    'lint': KIT / 'fixture/lint/explore.py',
    'tidy': KIT / 'fixture/lint/explore.py',
    'verdict': KIT / 'fixture/verdict/explore.py',
}
NOTEBOOK_NAME = re.compile(r'explore\.py')
NOTEBOOK_WRITE = re.compile(r'--fix|sed\s+-i|>\s*\S*explore\.py|\btee\b|write_text|\.write\(|open\(')
ANYWHERE_WRITE = re.compile(r'ruff\s+(check\s+[^|;&]*--fix|format)|sed\s+-i|marimo\s+convert')
NOTEBOOK_RUN = re.compile(r'python\S*\s+(-\S+\s+)*\S*explore\.py|marimo\s+(export|run)\b|app\.run\(')
NOTEBOOK_CHECK = re.compile(r'marimo\s+check')
PHRASES = re.compile(r'confirm\w*|support\w*|holds?\s+true|as\s+expected|consistent\s+with|therefore|'
                     r'conclu\w*|\bnot\s+met\b|\bmet\b|reject\w*', re.IGNORECASE)
MODEL_FITS = re.compile(r'\.fit\(|LinearRegression|\bols\b|\bglm\b', re.IGNORECASE)
VOID_PATHS = re.compile(r'agent-skills|specs/|/Users/|(?<![\w~])~(?=/|\s|$|[\'"])|\$\{?HOME')
OTHER_PATHS = re.compile(r'/tmp/mnb98/(?!rep-XXXXXX/|venv/)[^\s\'"]*|\.\./')
CONTEXT = 60
COMMAND_SHOWN = 300


def is_cell_decorator(node: ast.expr) -> bool:
    target = node.func if isinstance(node, ast.Call) else node
    return (isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name)
            and target.value.id == 'app' and target.attr in ('cell', 'function', 'class_definition'))


def markdown_text(body: list[ast.stmt]) -> str | None:
    statements = [s for s in body if not isinstance(s, ast.Return)]
    if len(statements) != 1 or not isinstance(statements[0], ast.Expr):
        return None
    call = statements[0].value
    if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == 'md'
            and isinstance(call.func.value, ast.Name) and call.func.value.id == 'mo' and call.args):
        return None
    argument = call.args[0]
    if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
        return argument.value
    return f'(f-string or expression) {ast.unparse(argument)}'


def first_line(source: str) -> str:
    lines = source.splitlines()
    for number, line in enumerate(lines):
        if line.lstrip().startswith(('def ', 'class ', 'with ')):
            for rest in lines[number + 1:]:
                if rest.strip():
                    return rest.strip()
    return lines[0].strip() if lines else ''


def displayed(body: list[ast.stmt]) -> str:
    statements = [s for s in body if not isinstance(s, ast.Return)]
    if statements and isinstance(statements[-1], ast.Expr):
        return ast.unparse(statements[-1].value)[:200]
    return '(no display: the last statement is not an expression)'


def cells(source: str) -> list[dict]:
    tree = ast.parse(source)
    found = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and any(map(is_cell_decorator, node.decorator_list)):
            start = min(d.lineno for d in node.decorator_list)
            text = '\n'.join(source.splitlines()[start - 1:node.end_lineno])
            markdown = markdown_text(node.body) if isinstance(node, ast.FunctionDef) else None
            kind = 'markdown' if markdown is not None else 'code'
            if not any(is_cell_decorator(d) and 'app.cell' in ast.unparse(d) for d in node.decorator_list):
                kind = 'function'
            found.append({'name': node.name, 'source': text, 'markdown': markdown, 'kind': kind, 'body': node.body})
        elif isinstance(node, ast.With) and 'app.setup' in ast.unparse(node.items[0].context_expr):
            text = '\n'.join(source.splitlines()[node.lineno - 1:node.end_lineno])
            found.append({'name': 'app.setup', 'source': text, 'markdown': None, 'kind': 'setup', 'body': node.body})
    return found


def show_cells(case: str, rep: Path) -> list[dict]:
    final_path = rep / 'notebook.py'
    if not final_path.exists():
        print('  notebook.py: MISSING')
        return []
    try:
        final = cells(final_path.read_text())
    except SyntaxError as error:
        print(f'  notebook.py does not parse: {error}')
        return []
    base = cells(NOTEBOOKS[case].read_text())
    base_sources = [c['source'].rstrip() for c in base]
    remaining = list(base_sources)
    new = []
    print('  cells, in file order:')
    for number, cell in enumerate(final, 1):
        key = cell['source'].rstrip()
        if key in remaining:
            remaining.remove(key)
            tag = 'base'
        else:
            tag = 'NEW '
            new.append(cell)
        print(f'    {number:2} {tag} {cell["kind"]:8} {cell["name"]}: {first_line(cell["source"])[:100]}')
    for key in remaining:
        cell = next(c for c in base if c['source'].rstrip() == key)
        print(f'    starting cell {cell["name"]} ({cell["kind"]}) is not in the final notebook unchanged')
    for cell in new:
        if cell['kind'] == 'markdown':
            print(f'  new markdown cell {cell["name"]}, full text:')
            for line in textwrap.dedent(cell['markdown']).strip().splitlines():
                print(f'      | {line}')
        elif cell['kind'] == 'code':
            print(f'  new code cell {cell["name"]} displays: {displayed(cell["body"])}')
    return new


def notebook_writes(calls: list[dict], diff: str) -> int:
    last = 0
    for number, call in enumerate(calls, 1):
        args = call.get('input') or {}
        if call.get('name') in ('Write', 'Edit') and NOTEBOOK_NAME.search(args.get('file_path', '')):
            print(f'  write: call {number} {call["name"]} {args.get("file_path")} error={call.get("is_error")}')
            last = number
        elif call.get('name') == 'Bash':
            command = args.get('command', '')
            named = NOTEBOOK_NAME.search(command) and NOTEBOOK_WRITE.search(command)
            if named or ANYWHERE_WRITE.search(command):
                print(f'  write?: call {number} Bash error={call.get("is_error")}: {command[:COMMAND_SHOWN]!r}')
                last = number
    changed = re.search(r'^diff --git a/notebooks/explore\.py ', diff, re.MULTILINE) is not None
    print(f'  final.diff changes notebooks/explore.py: {"yes" if changed else "no"}')
    return last


def notebook_runs(calls: list[dict], last_write: int) -> None:
    print(f'  last notebook write or possible write: call {last_write or "none"}')
    for number, call in enumerate(calls, 1):
        if call.get('name') != 'Bash':
            continue
        command = (call.get('input') or {}).get('command', '')
        if NOTEBOOK_RUN.search(command):
            label = 'run'
        elif NOTEBOOK_CHECK.search(command):
            label = 'check (static)'
        else:
            continue
        if number == last_write:
            order = 'in the same call as the last write: read the order in its text, note 7'
        else:
            order = f'{"after" if number > last_write else "before"} the last write'
        print(f'  {label}: call {number} ({order}) error={call.get("is_error")}: {command[:COMMAND_SHOWN]!r}')
        tail = (call.get('result_tail') or '').strip().splitlines()[-3:]
        for line in tail:
            print(f'      > {line[:160]}')


def phrases(label: str, text: str) -> None:
    for match in PHRASES.finditer(text or ''):
        start, end = max(0, match.start() - CONTEXT), match.end() + CONTEXT
        print(f'  phrase in {label}: {match.group(0)!r} in {text[start:end]!r}')


def model_fits(new: list[dict], calls: list[dict]) -> None:
    for cell in new:
        for match in MODEL_FITS.finditer(cell['source'] if cell['kind'] == 'code' else ''):
            print(f'  model fit in new cell {cell["name"]}: {match.group(0)!r}')
    for number, call in enumerate(calls, 1):
        command = (call.get('input') or {}).get('command', '') if call.get('name') == 'Bash' else ''
        for match in MODEL_FITS.finditer(command):
            print(f'  model fit in Bash call {number} (outside the notebook): {match.group(0)!r}')


def void_paths(calls: list[dict]) -> None:
    for number, call in enumerate(calls, 1):
        args = call.get('input') or {}
        for key in ('command', 'file_path', 'path', 'pattern'):
            value = args.get(key)
            if not isinstance(value, str):
                continue
            for match in VOID_PATHS.finditer(value):
                start, end = max(0, match.start() - 30), match.end() + 30
                print(f'  VOID path?: call {number} {call.get("name")} {key} names {match.group(0)!r}: '
                      f'{value[start:end]!r}')
            for match in OTHER_PATHS.finditer(value):
                start, end = max(0, match.start() - 30), match.end() + 30
                print(f'  outside path?: call {number} {call.get("name")} {key} names {match.group(0)!r}: '
                      f'{value[start:end]!r}')


def show_run(summary: dict) -> None:
    result = summary.get('result') or {}
    init = summary.get('init') or {}
    models = sorted((result.get('modelUsage') or {}).keys())
    other = [it for it in result.get('iterations') or [] if it != 'message']
    print(f'  {summary.get("arm")} {summary.get("case")}: exit={summary.get("claude_exit")} '
          f'subtype={result.get("subtype")} is_error={result.get("is_error")} '
          f'cost={result.get("total_cost_usd")} turns={result.get("num_turns")} wall={summary.get("wall_seconds")}s')
    print(f'  models={models} non-message iterations={other} '
          f'permission denials={result.get("permission_denials")}')
    print(f'  init: tools={init.get("tools")} skills={init.get("skills")} mcp={init.get("mcp_servers")} '
          f'output_style={init.get("output_style")} version={init.get("claude_code_version")}')
    print(f'  CLAUDE.md matches arm: {summary.get("claude_md_matches_arm")} '
          f'(sha256 {str(summary.get("claude_md_sha256"))[:12]}, block {str(summary.get("block_sha256"))[:12]})')


def grade(rep: Path) -> None:
    print(f'== {rep}')
    path = rep / 'summary.json'
    if not path.exists():
        print('  summary.json: MISSING')
        return
    summary = json.loads(path.read_text())
    if 'kit_error' in summary:
        print(f'  kit_error: {summary["kit_error"]}')
        return
    show_run(summary)
    calls = summary.get('tool_calls') or []
    print(f'  tool calls: {len(calls)}')
    new = show_cells(summary['case'], rep)
    diff = (rep / 'final.diff').read_text() if (rep / 'final.diff').exists() else ''
    last_write = notebook_writes(calls, diff)
    notebook_runs(calls, last_write)
    for cell in new:
        if cell['kind'] == 'markdown':
            phrases(f'new markdown cell {cell["name"]}', cell['markdown'])
    phrases('the final message', summary.get('final_message') or '')
    model_fits(new, calls)
    void_paths(calls)
    print('  final message:')
    for line in (summary.get('final_message') or '(none)').splitlines():
        print(f'      | {line}')


def rep_number(path: Path) -> int:
    return int(path.name[3:]) if path.name[3:].isdigit() else 0


def main(out_dirs: list[str]) -> None:
    for out_dir in out_dirs:
        reps = sorted((p for p in Path(out_dir).glob('rep*') if p.is_dir()), key=rep_number)
        if not reps:
            print(f'== {out_dir}: no rep folders')
        for rep in reps:
            grade(rep)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('usage: grade.py <out-dir> ...')
    main(sys.argv[1:])
