'''Tools for plan 108's case-rep runner. run_tool_reps.sh and probe_tools.sh call them; the tests call them too.

Copy of plan 107's rep_tools.py (specs/baseline/red-baseline-writing-skills-tests/kit/rep_tools.py), changed
for plan 108: the skill copy root is plan 108's, and the trigger rep's `--manifest -` and `--condition` and
the R3 tree check are gone.

Usage, from the kit folder:
  rep_tools.py check-copy <manifest> [<prompt>]
  rep_tools.py strip <file> ...
  rep_tools.py place-copy <ref>
  rep_tools.py summarize --stream S --err E --dest D --orig O --case C --arm A --model M --cap CAP --rep N
                         --rep-dir DIR --base SHA --prompt P --status X --wall W --manifest M

check-copy compares the skill copy with MANIFEST.txt: every `skill-copy <rel> <sha256> <source>` file
is there with that sha256, the copy root holds no other file, and the prompt, when given, has its
`prompt <name> <sha256>` sha256. It prints each difference and exits 1 on any.

strip removes the key credential_expires_at, at any depth, from each .json and .jsonl file given. A
.jsonl line that is not JSON keeps its bytes.

place-copy writes `git archive <ref> skills/writing-skills` under the skill copy root, as
<root>/writing-skills/, with each file's mode. The root is WST_SKILL_ROOT (default
/private/tmp/wst108-skill). It refuses (exit 3) when the root holds anything, so no file of another
arm or build stays beside the copy. The repository is WST_REPO, or else the one that holds this kit.
build_prompts.py hashes the same archive for MANIFEST.txt, so the copy and the manifest cannot differ.

summarize reads one rep's stream and repository and writes <dest>/: final.diff, then summary.json last.
- The stream is split at newlines only. Claude Code leaves U+2028, U+2029 and U+0085 raw inside JSON
  strings, and str.splitlines() would cut a record there. A blank line is skipped. Any other line
  that is not strict UTF-8, not JSON, or JSON that is not an object, is a kit error: a skipped line
  could hide a peer `origin`. The summary still holds what was read.
- The raw stream is rewritten with the field stripped. final.diff and summary.json write the real home
  as `<REAL-HOME>` (a rep's `~` is its own HOME), the rep's TMPDIR as `$TMPDIR`, `pytest-of-<user>` as
  `pytest-of-$USER`, and the user's identity forms as tokens (kit_identity.py). An unscrubbed copy of
  final.diff goes to <orig>/, beside the raw stream, outside the repository.
- final.diff is the diff from BASE to the rep's final tree, new files included.
- `tool_calls` gives each tool call in stream order, with `is_error` from its tool result (None when no
  result came back).
- `skill_copy_changed` lists check-copy's differences after the rep.
'''
import argparse
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit_identity  # noqa: E402

KIT = Path(__file__).resolve().parent
FIELD = 'credential_expires_at'
# The rep's own HOME is inside its folder, so its `~` is not the real home: the real one gets its own token.
REAL_HOME = '<REAL-HOME>'
INIT_KEYS = ('cwd', 'tools', 'mcp_servers', 'model', 'permissionMode', 'slash_commands', 'skills', 'agents',
             'plugins', 'output_style', 'claude_code_version')
RESULT_KEYS = ('subtype', 'is_error', 'num_turns', 'duration_ms', 'total_cost_usd', 'modelUsage')
SKILL_DIR = 'skills/writing-skills'
DEFAULT_SKILL_ROOT = '/private/tmp/wst108-skill'


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
        elif parts[0] == 'arm':
            entries['arm'] = parts[1]
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


# --- the archive and place-copy --------------------------------------------------------------------------


def repo_root() -> Path:
    '''The repository the skill text is read from: WST_REPO, or else the one that holds this kit.'''
    if os.environ.get('WST_REPO'):
        return Path(os.environ['WST_REPO'])
    found = subprocess.run(['git', '-C', str(KIT), 'rev-parse', '--show-toplevel'], capture_output=True, text=True)
    if found.returncode != 0:
        raise SystemExit(f'refusing: {KIT} is not inside a git repository')
    return Path(found.stdout.strip())


def skill_root() -> Path:
    return Path(os.environ.get('WST_SKILL_ROOT') or DEFAULT_SKILL_ROOT)


def resolve(ref: str) -> str:
    '''The full sha of the commit that ref names.'''
    found = subprocess.run(['git', '-C', str(repo_root()), 'rev-parse', '--verify', '--quiet', f'{ref}^{{commit}}'],
                           capture_output=True, text=True)
    if found.returncode != 0 or not found.stdout.strip():
        raise SystemExit(f'refusing: {ref} names no commit')
    return found.stdout.strip()


def archive_files(sha: str) -> dict[str, tuple[bytes, int]]:
    '''Each file of `git archive <sha> skills/writing-skills`, as writing-skills/<rel>: (bytes, mode).'''
    archive = subprocess.run(['git', '-C', str(repo_root()), 'archive', '--format=tar', sha, SKILL_DIR],
                             capture_output=True)
    if archive.returncode != 0:
        raise SystemExit(f'refusing: git archive failed: {archive.stderr.decode(errors="replace").strip()}')
    files = {}
    with tarfile.open(fileobj=io.BytesIO(archive.stdout), mode='r:') as tar:
        for member in tar.getmembers():
            if member.isdir():
                continue
            if not member.isfile() or not member.name.startswith(f'{SKILL_DIR}/'):
                raise SystemExit(f'refusing: the archive holds {member.name}, which is not a file of {SKILL_DIR}')
            files[member.name[len('skills/'):]] = (tar.extractfile(member).read(), member.mode)
    if not files:
        raise SystemExit(f'refusing: {SKILL_DIR} is empty at {sha}')
    return files


def place_copy(ref: str) -> int:
    root = skill_root()
    sha = resolve(ref)
    files = archive_files(sha)
    root.mkdir(parents=True, exist_ok=True)
    if any(root.iterdir()):
        print(f'refusing: {root} is not empty; empty it first')
        return 3
    for rel, (data, mode) in sorted(files.items()):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.chmod(mode & 0o777)
    print(f'placed {len(files)} file(s) of {SKILL_DIR} at {sha} in {root}')
    return 0


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
        block = results.get(call['id'])
        call['is_error'] = bool(block.get('is_error')) if block is not None else None
    return {'init': init, 'result': result, 'calls': calls, 'texts': texts,
            'inits': sum(1 for r in records if r.get('type') == 'system' and r.get('subtype') == 'init'),
            'results': sum(1 for r in records if r.get('type') == 'result')}


# --- summarize -------------------------------------------------------------------------------------------


def git(repo: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=True, env=env)


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

    index = Path(rep_dir) / 'final.index'
    shutil.copy(repo / '.git' / 'index', index)
    env = dict(os.environ, GIT_INDEX_FILE=str(index))
    git(repo, 'add', '-A', env=env)
    diff = git(repo, 'diff', '--cached', '--binary', args.base, env=env).stdout
    index.unlink()
    (orig / 'final.diff').write_text(diff)
    (dest / 'final.diff').write_text(scrub(diff))

    err_lines = Path(args.err).read_text(errors='replace').splitlines() if Path(args.err).exists() else []
    result = read['result']
    summary = {
        'case': args.case, 'rep': int(args.rep), 'arm': args.arm, 'model': args.model, 'cap': args.cap,
        'rep_dir': rep_dir, 'skill_root': manifest_entries(Path(args.manifest)).get('root'),
        'base': args.base,
        'stream': str(stream), 'prompt_sha256': file_sha(Path(args.prompt)), 'claude_exit': int(args.status),
        'wall_seconds': int(args.wall), 'init': read['init'], 'records': len(records), 'init_records': read['inits'],
        'result_records': read['results'], 'bad_stream_lines': bad, 'result': result,
        'final_message': result['final_message'] if result else (read['texts'][-1] if read['texts'] else None),
        'tool_calls': read['calls'],
        'status_porcelain': git(repo, 'status', '--porcelain', '--untracked-files=normal').stdout.splitlines(),
        'skill_copy_changed': copy_problems(Path(args.manifest)),
        'stderr_tail': err_lines[-20:],
    }
    if result:
        del result['final_message']
    if bad:
        summary['kit_error'] = f'stream line(s) {", ".join(map(str, bad))} are not JSON'
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
    if command == 'place-copy':
        if len(rest) != 1:
            raise SystemExit(__doc__)
        return place_copy(rest[0])
    if command == 'summarize':
        parser = argparse.ArgumentParser(prog='rep_tools.py summarize')
        for name in ('stream', 'err', 'dest', 'orig', 'case', 'arm', 'model', 'cap', 'rep', 'rep-dir', 'base',
                     'prompt', 'status', 'wall', 'manifest'):
            parser.add_argument(f'--{name}', required=True)
        return summarize(parser.parse_args(rest))
    raise SystemExit(__doc__)


if __name__ == '__main__':
    sys.exit(main())
