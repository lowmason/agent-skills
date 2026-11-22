'''Void or keep one rep's raw JSON. run_reps.sh calls this on each rep; the self-test calls it too.

Usage, from the kit folder:
  postprocess.py <raw-json> <dest-json> <dest-void>

postprocess(raw) reads two fields of the raw JSON that `claude -p --output-format json` writes:
- `result_index`: 0 for the answer a kit scores. A message that a peer session sends to a busy no-tools
  rep arrives as an extra turn after the answer, and the JSON `result` then holds the reply to that
  message. Then `result_index` is above 0, and `num_turns` stays 1.
- `origin`: null for a rep that no peer reached. A peer's turn sets it to the sender's session title,
  session id and socket path.
Either one marks the rep void. The check reads the raw JSON, before anything is dropped. A rep with no
`result_index` key counts as 0, and one with no `origin` key counts as null. A `result_index` that is
not a whole number, or one that is a boolean, cannot be shown to be 0, so it voids the rep too.
A void rep gets `{'void': True, 'reason': 'result_index' | 'origin'}` and nothing else: its answer
text is the reply to a peer, so no copy of it is kept. `result_index` is checked first.

A kept rep gets `'void': False` and its other fields, minus the keys in DROPPED_KEYS at any depth:
`origin` and `credential_expires_at` (both private), and `session_id` and `uuid`. Every string in it
then goes through the scrub: $TMPDIR written as `$TMPDIR`, $HOME as `~`, and the user's identity forms
as tokens (kit_identity.py).

The command line prints one verdict line and exits 0 for each of them:
- `kept`: <dest-json> holds the rep, with `void` removed, so the file is the raw JSON minus the dropped
  keys, scrubbed.
- `void <reason>`: <dest-void> holds a one-line note and no answer text. The file name has no `.json`
  ending, so nothing that reads `rep*.json` can take a void rep for a scored answer.
- `unreadable`: the raw file is missing, empty, not JSON or not an object. <dest-void> holds a note, and
  the rep is void, since an unreadable file could hold a peer's origin.
'''
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit_identity  # noqa: E402

DROPPED_KEYS = frozenset({'origin', 'credential_expires_at', 'session_id', 'uuid'})
TMPDIR_TOKEN = '$TMPDIR'
HOME_TOKEN = '~'


def void_reason(raw: dict) -> str | None:
    '''Return 'result_index' or 'origin' when the raw JSON shows a peer turn, else None.'''
    index = raw.get('result_index', 0)
    if isinstance(index, bool) or not isinstance(index, int) or index > 0:
        return 'result_index'
    if raw.get('origin') is not None:
        return 'origin'
    return None


def _scrub_text(text: str, pairs: list[tuple[str, str]]) -> str:
    tmpdir = os.environ.get('TMPDIR', '').rstrip('/')
    if tmpdir:
        text = text.replace('/private' + tmpdir, TMPDIR_TOKEN).replace(tmpdir, TMPDIR_TOKEN)
    home = os.environ.get('HOME', '')
    if home:
        text = text.replace(home, HOME_TOKEN)
    return kit_identity.scrub(text, pairs)


def _clean(value, pairs: list[tuple[str, str]]):
    if isinstance(value, dict):
        return {_scrub_text(key, pairs): _clean(item, pairs) for key, item in value.items()
                if key not in DROPPED_KEYS}
    if isinstance(value, list):
        return [_clean(item, pairs) for item in value]
    if isinstance(value, str):
        return _scrub_text(value, pairs)
    return value


def postprocess(raw: dict) -> dict:
    '''Return the void marker for a peer-turn rep, else the rep without its private keys, scrubbed.'''
    reason = void_reason(raw)
    if reason is not None:
        return {'void': True, 'reason': reason}
    return {'void': False, **_clean(raw, kit_identity.forms())}


def _write(dest: Path, text: str) -> None:
    temp = dest.with_name(dest.name + '.tmp')
    temp.write_text(text)
    os.replace(temp, dest)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    raw_path, dest, void_dest = Path(argv[0]), Path(argv[1]), Path(argv[2])
    try:
        raw = json.loads(raw_path.read_text(errors='replace'))
    except (OSError, json.JSONDecodeError):
        raw = None
    if not isinstance(raw, dict):
        _write(void_dest, 'VOID: the raw JSON is missing, empty or not an object. Run a replacement rep.\n')
        print('unreadable')
        return 0
    rep = postprocess(raw)
    if rep['void']:
        _write(void_dest, f"VOID: {rep['reason']} showed a peer turn. No answer is kept. Run a replacement rep.\n")
        print(f"void {rep['reason']}")
        return 0
    del rep['void']
    _write(dest, json.dumps(rep, indent=2, ensure_ascii=False) + '\n')
    print('kept')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
