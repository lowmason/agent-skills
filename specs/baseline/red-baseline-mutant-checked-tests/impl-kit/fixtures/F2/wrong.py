import sys
from pathlib import Path

KNOWN_KEYS = {'name', 'port', 'debug'}


def main(argv: list[str]) -> int:
    for line in Path(argv[0]).read_text().splitlines():
        if not line.strip():
            continue
        key = line.split('=', 1)[0].strip()
        if key not in KNOWN_KEYS:
            print(f'unknown key: {key}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
