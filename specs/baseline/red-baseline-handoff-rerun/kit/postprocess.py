#!/usr/bin/python3
'''Split a rep turn's stream and strip credential_expires_at (plan 100, C7).

Usage:
  postprocess.py split <stream.jsonl | -> <out-dir> <n>
  postprocess.py strip-tree <dir>

split writes turn<n>.jsonl (every stream line, stripped), turn<n>.json (the
last `result` record) and turn<n>.init.json (the `system`/`init` record).
A line that is not JSON passes through to turn<n>.jsonl unchanged.
strip-tree strips every .json and .jsonl file under a folder in place.
Runs on the system Python 3.9 with the stdlib only.
'''

from __future__ import annotations

import json
import sys
from pathlib import Path

FIELD = 'credential_expires_at'


def strip(obj):
    '''A copy of obj with the key credential_expires_at removed at any depth.'''
    if isinstance(obj, dict):
        return {k: strip(v) for k, v in obj.items() if k != FIELD}
    if isinstance(obj, list):
        return [strip(v) for v in obj]
    return obj


def strip_line(line: str) -> tuple[str, object]:
    '''The stripped text of one JSONL line, and its parsed value (None when not JSON).
    A line that does not hold the field keeps its own bytes.'''
    try:
        obj = strip(json.loads(line))
    except ValueError:
        return line, None
    return (json.dumps(obj, ensure_ascii=False) if FIELD in line else line), obj


def dump(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def split(stream: str, out: Path, n: int) -> int:
    text = sys.stdin.read() if stream == '-' else Path(stream).read_text(errors='replace')
    lines, result, init = [], None, None
    for raw in text.splitlines():
        if not raw.strip():
            continue
        line, obj = strip_line(raw)
        lines.append(line)
        if isinstance(obj, dict) and obj.get('type') == 'result':
            result = obj
        if isinstance(obj, dict) and obj.get('type') == 'system' and obj.get('subtype') == 'init' and init is None:
            init = obj
    out.mkdir(parents=True, exist_ok=True)
    (out / f'turn{n}.jsonl').write_text(''.join(line + '\n' for line in lines))
    if result is not None:
        dump(out / f'turn{n}.json', result)
    if init is not None:
        dump(out / f'turn{n}.init.json', init)
    return 0


def strip_file(path: Path) -> None:
    text = path.read_text(errors='replace')
    if FIELD not in text:
        return
    if path.suffix == '.jsonl':
        new = ''.join(strip_line(raw)[0] + '\n' for raw in text.splitlines())
    else:
        try:
            obj = json.loads(text)
        except ValueError:
            return
        new = json.dumps(strip(obj), ensure_ascii=False, indent=2) + '\n'
    if new != text:
        path.write_text(new)


def strip_tree(root: Path) -> int:
    for path in sorted(root.rglob('*')):
        if path.is_file() and not path.is_symlink() and path.suffix in ('.json', '.jsonl'):
            strip_file(path)
    return 0


def main(argv: list[str]) -> int:
    if len(argv) == 4 and argv[0] == 'split':
        return split(argv[1], Path(argv[2]), int(argv[3]))
    if len(argv) == 2 and argv[0] == 'strip-tree':
        return strip_tree(Path(argv[1]))
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
