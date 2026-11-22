'''Tools for plan 104's micro-test runner. run_reps.sh and probe.sh call them; the tests call them too.

Usage, from the kit folder:
  rep_tools.py check-copy <manifest> [<prompt>]
  rep_tools.py strip <file> ...
  rep_tools.py summarize --stream S --err E --dest D --orig O --fixture F --role R --arm A --rep N
                         --rep-dir DIR --base SHA --prompt P --status X --wall W --manifest M --venv V
                         --model MODEL --cap CAP --start FILE --seeded FILE

check-copy compares the skill copy with MANIFEST.txt: every `skill-copy <rel> <sha256> <source>` file
is there with that sha256, the copy holds no other file, and the prompt, when given, has its
`prompt <name> <sha256>` sha256. It prints each difference and exits 1 on any.

strip removes the key credential_expires_at, at any depth, from each .json and .jsonl file given. A
.jsonl line that is not JSON keeps its bytes.

summarize reads one rep's stream and repository and writes <dest>/: final.diff, commits.txt, a copy
of each workspace file whose name starts with task-1- and of progress.md, and summary.json last.
- The stream is split at newlines only. Claude Code leaves U+2028, U+2029 and U+0085 raw inside JSON
  strings, and str.splitlines() would cut a record there. A blank line is skipped. Any other line
  that is not strict UTF-8, not JSON, or JSON that is not an object, is a kit error (the record's
  VOID case 3): a skipped line could hide a peer `origin`. The summary still holds what was read.
- The raw stream is rewritten with the field stripped. The copies, final.diff, commits.txt and
  summary.json write the real home as `<REAL-HOME>` (a rep's `~` is its own HOME), the rep's TMPDIR
  as `$TMPDIR`, `pytest-of-<user>` as `pytest-of-$USER`, and the user's identity forms as tokens
  (kit_identity.py). Unscrubbed copies of
  final.diff and the workspace files go to <orig>/, beside the raw stream, outside the repository.
- commits.txt is `git log --format='%H%n%(trailers:key=Mutant-step,valueonly)%n%B' BASE..HEAD`.
  summary.json's `commits` gives each commit after BASE, oldest first: sha, subject, message, its
  Mutant-step trailer values, its changed paths, and whether setup.sh made it (`seeded`).
- `run_files` gives each task-1-mutants*.log and task-1-screen*.log: its header lines, its mutant
  lines (number, verdict, sha256, carried field), its mtime, whether setup.sh wrote it, and the test
  functions in the test files at its `head:` commit. `final_tests` gives those of the final tree.
- `skill_copy_changed` lists check-copy's differences after the rep (the record's VOID case 8).
'''
import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit_identity  # noqa: E402

FIELD = 'credential_expires_at'
# The rep's own HOME is inside its folder, so its `~` is not the real home: the real one gets its own token.
REAL_HOME = '<REAL-HOME>'
INIT_KEYS = ('cwd', 'tools', 'mcp_servers', 'model', 'permissionMode', 'slash_commands', 'skills', 'agents',
             'plugins', 'output_style', 'claude_code_version')
RESULT_KEYS = ('subtype', 'is_error', 'num_turns', 'duration_ms', 'total_cost_usd', 'modelUsage')
RUN_FILE = re.compile(r'^task-1-(mutants|screen)(?:-([1-9][0-9]*))?\.log$')
MUTANT_LINE = re.compile(r'^mutant ([1-9][0-9]*): (CAUGHT|SURVIVED|INVALID) exit (\S+) sha256 ([0-9a-f]+)(.*)$')
HEADER_KEYS = ('command:', 'head:', 'base:', 'tree:', 'result:', 'screen:', 'note:', 'revert:')
RESULT_MARKS = ('run: ', 'result: ', 'screen: ', 'revert: ')
WORKSPACE_EXTRA = ('progress.md',)


# --- check-copy ------------------------------------------------------------------------------------------


def manifest_entries(manifest: Path) -> dict:
    entries = {'files': {}, 'prompts': {}}
    for line in manifest.read_text().splitlines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] == 'skill-copy-root':
            entries['root'] = parts[1]
        elif parts[0] == 'skill-copy':
            entries['files'][parts[1]] = parts[2]
        elif parts[0] == 'prompt':
            entries['prompts'][parts[1]] = parts[2]
        elif parts[0] == 'role':
            entries['role'] = parts[1]
    return entries


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_problems(manifest: Path, prompt: Path | None = None) -> list[str]:
    entries = manifest_entries(manifest)
    if 'root' not in entries:
        return ['MANIFEST.txt names no skill-copy-root']
    root = Path(entries['root'])
    problems = []
    for rel, want in sorted(entries['files'].items()):
        path = root / rel
        if not path.is_file():
            problems.append(f'skill copy file missing: {path}')
        elif file_sha(path) != want:
            problems.append(f'skill copy file changed: {path}')
    present = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() or p.is_symlink()} \
        if root.is_dir() else set()
    problems += [f'skill copy holds a file MANIFEST.txt does not list: {root / rel}'
                 for rel in sorted(present - set(entries['files']))]
    if prompt is not None:
        want = entries['prompts'].get(prompt.name)
        if want is None:
            problems.append(f'MANIFEST.txt lists no prompt {prompt.name}')
        elif file_sha(prompt) != want:
            problems.append(f'prompt changed: {prompt}')
    return problems


# --- strip -----------------------------------------------------------------------------------------------


def strip(obj):
    '''A copy of obj with the key credential_expires_at removed at any depth.'''
    if isinstance(obj, dict):
        return {k: strip(v) for k, v in obj.items() if k != FIELD}
    if isinstance(obj, list):
        return [strip(v) for v in obj]
    return obj


def strip_jsonl(data: bytes) -> bytes:
    out = []
    for raw in data.split(b'\n'):
        if FIELD.encode() in raw:
            try:
                raw = json.dumps(strip(json.loads(raw.decode('utf-8'))), ensure_ascii=False).encode()
            except (UnicodeDecodeError, ValueError):
                pass
        out.append(raw)
    return b'\n'.join(out)


def strip_file(path: Path) -> None:
    data = path.read_bytes()
    if FIELD.encode() not in data:
        return
    if path.suffix == '.jsonl':
        path.write_bytes(strip_jsonl(data))
        return
    try:
        obj = json.loads(data.decode('utf-8'))
    except (UnicodeDecodeError, ValueError):
        return
    path.write_text(json.dumps(strip(obj), ensure_ascii=False, indent=2) + '\n')


# --- the stream ------------------------------------------------------------------------------------------


def read_stream(data: bytes) -> tuple[list[dict], list[int]]:
    '''The stream's records, and the numbers of its lines that are not JSON objects (blank lines aside).'''
    records, bad = [], []
    for number, raw in enumerate(data.split(b'\n'), 1):
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
    return records, bad


def result_body(block: dict) -> str:
    body = block.get('content')
    if isinstance(body, list):
        return '\n'.join(b.get('text', '') for b in body if isinstance(b, dict))
    return str(body or '')


def read_records(records: list[dict]) -> dict:
    init, result, calls, texts, results = None, None, [], [], {}
    for record in records:
        kind = record.get('type')
        content = (record.get('message') or {}).get('content') if kind in ('assistant', 'user') else None
        if kind == 'system' and record.get('subtype') == 'init' and init is None:
            init = {key: record.get(key) for key in INIT_KEYS}
        elif kind == 'assistant':
            for item in content if isinstance(content, list) else []:
                if item.get('type') == 'tool_use':
                    calls.append({'id': item.get('id'), 'name': item.get('name'), 'input': item.get('input')})
                elif item.get('type') == 'text':
                    texts.append(item.get('text', ''))
        elif kind == 'user':
            for item in content if isinstance(content, list) else []:
                if isinstance(item, dict) and item.get('type') == 'tool_result':
                    results[item.get('tool_use_id')] = item
        elif kind == 'result':
            result = {key: record.get(key) for key in RESULT_KEYS}
            usage = record.get('usage') or {}
            result['iterations'] = [it.get('type') for it in usage.get('iterations') or []]
            result['permission_denials'] = [{'tool_name': d.get('tool_name'), 'tool_input': d.get('tool_input')}
                                            for d in record.get('permission_denials') or []]
            result['final_message'] = record.get('result')
    for call in calls:
        command = (call.get('input') or {}).get('command') or '' if call['name'] == 'Bash' else ''
        block = results.get(call['id'])
        if 'mutant-run' in command and block is not None:
            body = result_body(block)
            call['result_lines'] = [line for line in body.split('\n') if line.startswith(RESULT_MARKS)]
            call['result_is_error'] = bool(block.get('is_error'))
    return {'init': init, 'result': result, 'calls': calls, 'texts': texts,
            'inits': sum(1 for r in records if r.get('type') == 'system' and r.get('subtype') == 'init'),
            'results': sum(1 for r in records if r.get('type') == 'result')}


# --- the repository --------------------------------------------------------------------------------------


def git(repo: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=True, env=env)


def is_test_file(path: str) -> bool:
    name = path.rsplit('/', 1)[-1]
    return name.endswith('.py') and (name.startswith('test_') or name.endswith('_test.py')) \
        and not path.startswith(('.sdd/', '.git/'))


def test_names(source: str) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return sorted(set(re.findall(r'^\s*(?:async\s+)?def (test\w*)', source, re.M)))
    names = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith('test'):
            names.append(node.name)
        elif isinstance(node, ast.ClassDef):
            names += [item.name for item in node.body
                      if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name.startswith('test')]
    return names


def tests_at(repo: Path, sha: str) -> list[str]:
    listing = git(repo, 'ls-tree', '-r', '--name-only', sha)
    if listing.returncode != 0:
        return []
    names = []
    for path in listing.stdout.splitlines():
        if is_test_file(path):
            names += test_names(git(repo, 'show', f'{sha}:{path}').stdout)
    return sorted(set(names))


def final_tests(repo: Path) -> list[str]:
    names = []
    for path in repo.rglob('*.py'):
        rel = str(path.relative_to(repo))
        if is_test_file(rel):
            names += test_names(path.read_text(errors='replace'))
    return sorted(set(names))


def read_run_file(text: str) -> dict:
    lines = text.split('\n')
    header, mutants, inside = {}, [], False
    for line in lines[1:]:
        if line.startswith('--- '):
            inside = line == '--- mutants ---'
            if mutants and not inside:
                break
            continue
        if inside:
            match = MUTANT_LINE.match(line)
            if match:
                rest = match.group(5)
                carried = re.search(r' carried: (\S+)', rest)
                mutants.append({'k': int(match.group(1)), 'verdict': match.group(2), 'sha256': match.group(4),
                                'carried': carried.group(1) if carried else None, 'line': line})
        elif not mutants:
            for key in HEADER_KEYS:
                if line.startswith(key) and key[:-1] not in header:
                    header[key[:-1]] = line[len(key):].strip()
    return {'first_line': lines[0] if lines else '', 'header': header, 'mutants': mutants}


def commits_of(repo: Path, base: str, start: str) -> list[dict]:
    shas = git(repo, 'rev-list', '--reverse', f'{base}..HEAD').stdout.split()
    found = []
    for sha in shas:
        trailers = git(repo, 'log', '-1', '--format=%(trailers:key=Mutant-step,valueonly)', sha).stdout
        paths = git(repo, 'show', '--name-only', '--format=', sha).stdout
        found.append({
            'sha': sha,
            'subject': git(repo, 'log', '-1', '--format=%s', sha).stdout.strip(),
            'message': git(repo, 'log', '-1', '--format=%B', sha).stdout,
            'trailers': [line.strip() for line in trailers.splitlines() if line.strip()],
            'paths': [line for line in paths.splitlines() if line.strip()],
            'seeded': git(repo, 'merge-base', '--is-ancestor', sha, start).returncode == 0,
        })
    return found


# --- summarize -------------------------------------------------------------------------------------------


class Scrub:
    def __init__(self, rep_dir: str) -> None:
        home = str(Path.home())
        self.pairs = [(f'{rep_dir}/tmp', '$TMPDIR')]
        if rep_dir.startswith('/private/tmp/'):
            self.pairs.append((f'{rep_dir[len("/private"):]}/tmp', '$TMPDIR'))
        self.pairs += [(os.path.realpath(home), REAL_HOME), (home, REAL_HOME)]
        self.user = os.environ.get('USER', '')
        self.identity = kit_identity.forms()

    def __call__(self, text: str) -> str:
        for value, token in self.pairs:
            text = text.replace(value, token)
        if self.user:
            text = text.replace(f'pytest-of-{self.user}', 'pytest-of-$USER')
        return kit_identity.scrub(text, self.identity)


def summarize(args: argparse.Namespace) -> int:
    stream, dest, orig, repo = Path(args.stream), Path(args.dest), Path(args.orig), Path(args.rep_dir) / 'repo'
    rep_dir = args.rep_dir
    scrub = Scrub(rep_dir)
    orig.mkdir(parents=True, exist_ok=True)
    data = stream.read_bytes() if stream.exists() else b''
    records, bad = read_stream(data)
    if FIELD.encode() in data:
        stream.write_bytes(strip_jsonl(data))
    read = read_records(records)
    start = Path(args.start).read_text().strip()
    seeded = set(Path(args.seeded).read_text().split())

    index = Path(rep_dir) / 'final.index'
    shutil.copy(repo / '.git' / 'index', index)
    env = dict(os.environ, GIT_INDEX_FILE=str(index))
    git(repo, 'add', '-A', env=env)
    diff = git(repo, 'diff', '--cached', '--binary', args.base, env=env).stdout
    index.unlink()
    (orig / 'final.diff').write_text(diff)
    (dest / 'final.diff').write_text(scrub(diff))
    log = git(repo, 'log', '--format=%H%n%(trailers:key=Mutant-step,valueonly)%n%B', f'{args.base}..HEAD').stdout
    (dest / 'commits.txt').write_text(scrub(log))

    workspace = repo / '.sdd' / 'plan'
    copied, entries, run_files = [], [], []
    paths = sorted(p for p in workspace.iterdir() if p.is_file()
                   and (p.name.startswith('task-1-') or p.name in WORKSPACE_EXTRA)) if workspace.is_dir() else []
    for path in paths:
        raw = path.read_bytes()
        (orig / path.name).write_bytes(raw)
        (dest / path.name).write_text(scrub(raw.decode('utf-8', errors='replace')))
        copied.append(path.name)
        stat = path.stat()
        entries.append({'name': path.name, 'sha256': hashlib.sha256(raw).hexdigest(), 'mtime_ns': stat.st_mtime_ns,
                        'seeded': path.name in seeded})
        if RUN_FILE.match(path.name):
            run = read_run_file(raw.decode('utf-8', errors='replace'))
            head = run['header'].get('head', '')
            run.update({'name': path.name, 'mtime_ns': stat.st_mtime_ns, 'seeded': path.name in seeded,
                        'tests_at_head': tests_at(repo, head) if head else []})
            run_files.append(run)
    run_files.sort(key=lambda run: run['mtime_ns'])

    err_lines = Path(args.err).read_text(errors='replace').splitlines() if Path(args.err).exists() else []
    result = read['result']
    summary = {
        'fixture': args.fixture, 'rep': int(args.rep), 'role': args.role, 'arm': args.arm, 'model': args.model,
        'cap': args.cap, 'rep_dir': rep_dir, 'skill_root': manifest_entries(Path(args.manifest)).get('root'),
        'venv': args.venv, 'base': args.base, 'start': start, 'stream': str(stream),
        'prompt_sha256': file_sha(Path(args.prompt)), 'claude_exit': int(args.status), 'wall_seconds': int(args.wall),
        'init': read['init'], 'records': len(records), 'init_records': read['inits'],
        'result_records': read['results'], 'bad_stream_lines': bad, 'result': result,
        'final_message': result['final_message'] if result else (read['texts'][-1] if read['texts'] else None),
        'tool_calls': read['calls'], 'commits': commits_of(repo, args.base, start),
        'status_porcelain': git(repo, 'status', '--porcelain', '--untracked-files=normal').stdout.splitlines(),
        'copied': copied, 'workspace': entries, 'run_files': run_files, 'final_tests': final_tests(repo),
        'skill_copy_changed': copy_problems(Path(args.manifest)), 'stderr_tail': err_lines[-20:],
    }
    if result:
        del result['final_message']
    if bad:
        summary['kit_error'] = f'stream line(s) {", ".join(map(str, bad))} are not JSON (VOID case 3)'
    text = scrub(json.dumps(strip(summary), indent=2)) + '\n'
    (dest / 'summary.json.tmp').write_text(text)
    os.replace(dest / 'summary.json.tmp', dest / 'summary.json')
    cost = result['total_cost_usd'] if result else None
    print(f'rep{args.rep} exit={args.status} subtype={result and result["subtype"]} cost={cost} wall={args.wall}s'
          + (f' kit_error={summary["kit_error"]}' if bad else ''))
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    command, rest = sys.argv[1], sys.argv[2:]
    if command == 'check-copy':
        problems = copy_problems(Path(rest[0]), Path(rest[1]) if len(rest) > 1 else None)
        for problem in problems:
            print(problem)
        return 1 if problems else 0
    if command == 'strip':
        for name in rest:
            strip_file(Path(name))
        return 0
    if command == 'summarize':
        parser = argparse.ArgumentParser(prog='rep_tools.py summarize')
        for name in ('stream', 'err', 'dest', 'orig', 'fixture', 'role', 'arm', 'rep', 'rep-dir', 'base', 'prompt',
                     'status', 'wall', 'manifest', 'venv', 'model', 'cap', 'start', 'seeded'):
            parser.add_argument(f'--{name}', required=True)
        return summarize(parser.parse_args(rest))
    raise SystemExit(__doc__)


if __name__ == '__main__':
    sys.exit(main())
