'''Drop `credential_expires_at` from a rep's JSON file.

Usage: python3 scrub_json.py <file>, which rewrites <file> in place. run_reps.sh calls it on each
rep<N>.json after the rep ends, so the claude CLI's login-expiry field never lands in a committed
rep file (plan 101, D8). `scrub` is the same step on a string, for kit_selftest.py's reading and
for any caller that holds the text.
'''
import json
import sys
from pathlib import Path

KEY = 'credential_expires_at'


def drop_key(value):
    '''The value without any `credential_expires_at` key, at any depth, through dicts and lists.'''
    if isinstance(value, dict):
        return {k: drop_key(v) for k, v in value.items() if k != KEY}
    if isinstance(value, list):
        return [drop_key(v) for v in value]
    return value


def scrub(text: str) -> str:
    '''The JSON in `text` without any `credential_expires_at` key, dumped with ensure_ascii=False.

    Text that does not parse as JSON comes back with each line that holds the key removed. It stays
    unreadable, so show_reps.py still reads that rep as VOID.
    '''
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return ''.join(line for line in text.splitlines(keepends=True) if KEY not in line)
    return json.dumps(drop_key(data), ensure_ascii=False)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit('usage: python3 scrub_json.py <file>')
    path = Path(sys.argv[1])
    text = path.read_text(encoding='utf-8')
    scrubbed = scrub(text)
    if text.endswith('\n') and scrubbed and not scrubbed.endswith('\n'):
        scrubbed += '\n'
    path.write_text(scrubbed, encoding='utf-8')


if __name__ == '__main__':
    main()
