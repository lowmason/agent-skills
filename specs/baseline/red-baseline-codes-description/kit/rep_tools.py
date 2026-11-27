'''Tools for plan 111's trigger runner. run_trigger_reps.sh calls them; the tests call them too.

Copy of plan 107's rep_tools.py (specs/baseline/red-baseline-writing-skills-tests/kit/rep_tools.py). Its
changes: the case-rep parts are cut (check-copy, place-copy, the archive reader, final.diff, the R3 check and
the skill-copy fields), strip also drops `origin`, and summarize runs rule 4's check (peer_check) on the raw
stream before it strips anything.

Usage, from the kit folder:
  rep_tools.py strip <file> ...
  rep_tools.py summarize --stream S --err E --dest D --prompt-id ID --arm A --model M --cap CAP --rep N
                         --rep-dir DIR --prompt P --status X --wall W

strip removes the keys credential_expires_at and origin, at any depth, from each .json and .jsonl file given.
A .jsonl line that is not JSON keeps its bytes. `origin` holds the sender's session title, session id and
socket path when a peer session reaches a rep, so no saved file keeps it.

summarize reads one rep's raw stream and writes <dest>/summary.json.
- The stream is split at newlines only. Claude Code leaves U+2028, U+2029 and U+0085 raw inside JSON
  strings, and str.splitlines() would cut a record there. A blank line is skipped. Any other line that is
  not strict UTF-8, not JSON, or JSON that is not an object, is a kit error: a skipped line could hide a peer
  `origin`. The summary still holds what was read.
- Rule 4 runs first, on the raw records. `peer_check` lists each record that holds a `result_index` above 0,
  or an `origin` whose `kind` is `peer`, at any depth. A `result_index` that is not an integer, or is a
  boolean, cannot be compared with 0, so it is listed too. A record with no `result_index` counts as 0. The
  list holds reason strings only, never an origin's text.
- Then the raw stream is rewritten with both keys stripped. summary.json is written with both keys
  stripped, the real home as `<REAL-HOME>` (a rep's `~` is its own HOME), the rep's TMPDIR as `$TMPDIR`, and
  the user's identity forms as tokens (kit_identity.py).
- `tool_calls` gives each tool call in stream order, with `is_error` from its tool result (None when no
  result came back).
'''
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit_identity  # noqa: E402

FIELD = 'credential_expires_at'
ORIGIN = 'origin'
DROPPED = (FIELD, ORIGIN)
RESULT_INDEX = 'result_index'
PEER = 'peer'
# The rep's own HOME is inside its folder, so its `~` is not the real home: the real one gets its own token.
REAL_HOME = '<REAL-HOME>'
INIT_KEYS = ('cwd', 'tools', 'mcp_servers', 'model', 'permissionMode', 'slash_commands', 'skills', 'agents',
             'plugins', 'output_style', 'claude_code_version')
RESULT_KEYS = ('subtype', 'is_error', 'num_turns', 'duration_ms', 'total_cost_usd', 'modelUsage')


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --- strip -----------------------------------------------------------------------------------------------


def strip(obj):
    '''A copy of obj with the keys credential_expires_at and origin removed at any depth.'''
    if isinstance(obj, dict):
        return {k: strip(v) for k, v in obj.items() if k not in DROPPED}
    if isinstance(obj, list):
        return [strip(v) for v in obj]
    return obj


def holds_a_dropped_key(raw: bytes) -> bool:
    return FIELD.encode() in raw or f'"{ORIGIN}"'.encode() in raw


def strip_jsonl(data: bytes) -> bytes:
    out = []
    for raw in data.split(b'\n'):
        if holds_a_dropped_key(raw):
            try:
                raw = json.dumps(strip(json.loads(raw.decode('utf-8'))), ensure_ascii=False).encode()
            except (UnicodeDecodeError, ValueError):
                pass
        out.append(raw)
    return b'\n'.join(out)


def strip_file(path: Path) -> None:
    data = path.read_bytes()
    if not holds_a_dropped_key(data):
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


def values_of(record, key: str) -> list:
    '''Every value of `key` in record, at any depth.'''
    found, stack = [], [record]
    while stack:
        obj = stack.pop()
        if isinstance(obj, dict):
            if key in obj:
                found.append(obj[key])
            stack.extend(obj.values())
        elif isinstance(obj, list):
            stack.extend(obj)
    return found


def index_voids(value) -> bool:
    '''True for a result_index above 0, and for one that is not an integer (a boolean, a string, a float
    or null), which cannot be compared with 0.'''
    return isinstance(value, bool) or not isinstance(value, int) or value > 0


def peer_check(records: list[dict]) -> list[str]:
    '''Rule 4 on records: a reason for each record with a result_index above 0 or a peer origin.'''
    found = []
    for number, record in enumerate(records, 1):
        for value in values_of(record, RESULT_INDEX):
            if index_voids(value):
                found.append(f'record {number}: {RESULT_INDEX} {json.dumps(value)[:40]}')
        if any(isinstance(origin, dict) and origin.get('kind') == PEER for origin in values_of(record, ORIGIN)):
            found.append(f'record {number}: a peer origin')
    return found


def result_texts(records: list[dict]) -> dict[str, str]:
    '''Each tool result's text, by tool_use_id: the tool_result block's content (a string, or a list of blocks),
    and the user record's tool_use_result (Grep and Glob put their filenames there), as JSON.'''
    found = {}
    for record in records:
        content = (record.get('message') or {}).get('content') if record.get('type') == 'user' else None
        for item in content if isinstance(content, list) else []:
            if not (isinstance(item, dict) and item.get('type') == 'tool_result'):
                continue
            body = item.get('content')
            if isinstance(body, str):
                parts = [body]
            elif isinstance(body, list):
                parts = [json.dumps(block, ensure_ascii=False) for block in body]
            else:
                parts = []
            if record.get('tool_use_result') is not None:
                parts.append(json.dumps(record['tool_use_result'], ensure_ascii=False))
            key = item.get('tool_use_id')
            found[key] = '\n'.join(([found[key]] if key in found else []) + parts)
    return found


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


class Scrub:
    def __init__(self, rep_dir: str) -> None:
        home = str(Path.home())
        self.pairs = [(f'{rep_dir}/tmp', '$TMPDIR')]
        if rep_dir.startswith('/private/tmp/'):
            self.pairs.append((f'{rep_dir[len("/private"):]}/tmp', '$TMPDIR'))
        self.pairs += [(os.path.realpath(home), REAL_HOME), (home, REAL_HOME)]
        self.identity = kit_identity.forms()

    def __call__(self, text: str) -> str:
        for value, token in self.pairs:
            text = text.replace(value, token)
        return kit_identity.scrub(text, self.identity)


def summarize(args: argparse.Namespace) -> int:
    stream, dest = Path(args.stream), Path(args.dest)
    scrub = Scrub(args.rep_dir)
    data = stream.read_bytes() if stream.exists() else b''
    records, bad = read_stream(data)
    checked = peer_check(records)
    if holds_a_dropped_key(data):
        stream.write_bytes(strip_jsonl(data))
    read = read_records(records)
    err_lines = Path(args.err).read_text(errors='replace').splitlines() if Path(args.err).exists() else []
    result = read['result']
    summary = {
        'prompt': args.prompt_id, 'rep': int(args.rep), 'arm': args.arm, 'model': args.model, 'cap': args.cap,
        'rep_dir': args.rep_dir, 'stream': str(stream), 'prompt_sha256': file_sha(Path(args.prompt)),
        'claude_exit': int(args.status), 'wall_seconds': int(args.wall), 'peer_check': checked, 'init': read['init'],
        'records': len(records), 'init_records': read['inits'], 'result_records': read['results'],
        'bad_stream_lines': bad, 'result': result,
        'final_message': result['final_message'] if result else (read['texts'][-1] if read['texts'] else None),
        'tool_calls': read['calls'], 'stderr_tail': err_lines[-20:],
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
          + (f' peer_check={len(checked)}' if checked else '') + (f' kit_error={summary["kit_error"]}' if bad else ''))
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    command, rest = sys.argv[1], sys.argv[2:]
    if command == 'strip':
        for name in rest:
            strip_file(Path(name))
        return 0
    if command == 'summarize':
        parser = argparse.ArgumentParser(prog='rep_tools.py summarize')
        for name in ('stream', 'err', 'dest', 'prompt-id', 'arm', 'model', 'cap', 'rep', 'rep-dir', 'prompt',
                     'status', 'wall'):
            parser.add_argument(f'--{name}', required=True)
        return summarize(parser.parse_args(rest))
    raise SystemExit(__doc__)


if __name__ == '__main__':
    sys.exit(main())
