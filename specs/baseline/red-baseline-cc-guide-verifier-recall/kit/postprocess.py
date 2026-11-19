'''Strip the key `credential_expires_at` from a rep's saved files (plan 102,
PC2; plan 100's C7), under Python 3.13:

    postprocess.py strip-tree <dir>

It rewrites, in place, each .json and .jsonl file under <dir>, at any depth,
that holds the key at any depth. A .jsonl file is read line by line: a line
that holds the key is written again without it, and every other line, one
that does not parse as JSON included, keeps its bytes. A file that does not
hold the key is not rewritten, and a file of any other type is never read.

Plan 100's kit was not on origin/main (1deb0ec) when plan 102's Task 6 ran,
so this file is written to Task 6's Interfaces block, not copied from it.'''
import json
import sys
from pathlib import Path

KEY = 'credential_expires_at'
SUFFIXES = ('.json', '.jsonl')


def strip(obj):
    '''obj without KEY, at any depth, as a new object; obj is not changed.'''
    if isinstance(obj, dict):
        return {k: strip(v) for k, v in obj.items() if k != KEY}
    if isinstance(obj, list):
        return [strip(v) for v in obj]
    return obj


def holds(obj) -> bool:
    '''Whether KEY is a key of obj at any depth.'''
    if isinstance(obj, dict):
        return KEY in obj or any(holds(v) for v in obj.values())
    if isinstance(obj, list):
        return any(holds(v) for v in obj)
    return False


def parsed(text: str):
    '''text as JSON, or None when it does not parse. JSON null also gives
    None, which holds no key, so the caller leaves it alone either way.'''
    try:
        return json.loads(text)
    except ValueError:
        return None


def strip_jsonl(text: str) -> str:
    lines = []
    for line in text.splitlines(keepends=True):
        body = line.rstrip('\r\n')
        obj = parsed(body)
        if holds(obj):
            line = json.dumps(strip(obj), ensure_ascii=False, separators=(',', ':')) + line[len(body):]
        lines.append(line)
    return ''.join(lines)


def strip_file(path: Path) -> bool:
    '''Strip one file in place; True when it was rewritten.'''
    try:
        text = path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        return False
    if path.suffix == '.jsonl':
        new = strip_jsonl(text)
    else:
        obj = parsed(text)
        new = json.dumps(strip(obj), indent=1, ensure_ascii=False) + '\n' if holds(obj) else text
    if new == text:
        return False
    path.write_text(new, encoding='utf-8')
    return True


def strip_tree(root: Path) -> list[Path]:
    '''Strip every .json and .jsonl file under root; the files rewritten.'''
    files = sorted(p for p in root.rglob('*') if p.suffix in SUFFIXES and p.is_file() and not p.is_symlink())
    return [p for p in files if strip_file(p)]


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[0] != 'strip-tree':
        print('usage: postprocess.py strip-tree <dir>', file=sys.stderr)
        return 2
    root = Path(argv[1])
    if not root.is_dir():
        print(f'postprocess.py: {root}: not a folder', file=sys.stderr)
        return 2
    print(f'stripped {len(strip_tree(root))} file(s)')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
