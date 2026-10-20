'''The session-start notice (drift spec R9): the line `check --hook` leaves
for notice.sh to show, and the record it leaves for notice.sh refresh.

The cache files the two languages share, under ~/.cache/agent-skills/cc-guide/:
- notice.json: empty when nothing is due, else one ASCII JSON line holding
  {"systemMessage": ...}. Written here, or by refresh for its own two errors;
  show prints it as it stands.
- notice.digest: one line that changes whenever notice.json does: a sha256
  here, cksum's checksum from refresh. Always written after notice.json, and
  show reads it before notice.json, so a notice replaced between the two
  reads is shown once more, never skipped.
- notice-shown: "<YYYY-MM-DD> <digest>", written by show alone.
- last-check.json: written here alone, last of all, so a run ID in it means
  the notice is in place. refresh reads two of its lines without a JSON
  parser: ` "run": "<id>",` and ` "ok_epoch": <seconds>`, the last good check.
- unfinished: refresh's count of runs in a row that have not written
  last-check.json, raised as each run starts; a finished run removes it,
  and so does a good check under a day old.
- lock/: refresh's lock directory.
Each file is replaced by renaming a temporary file over it, in both
languages, so no reader sees a partial file.'''
import hashlib
import json
import os
from datetime import date, datetime
from pathlib import Path

NOTICE = 'notice.json'
DIGEST = 'notice.digest'
LAST_CHECK = 'last-check.json'
LIMIT = 300                 # R9.4: a notice line stays under 300 characters
DAY = 86400                 # seconds; notice.sh measures a day the same way
HEAD = 'cc-guide'
SEP = ' · '
TO_SKILL = ' → /cc-guide'
TO_CHECK = ' → run build/cc_guide/cli.py check'


def plural(count: int, noun: str) -> str:
    return f'{count} {noun}' + ('' if count == 1 else 's')


def named_sections(report: dict) -> list[str]:
    '''The candidate sections of the report's block findings, the most named
    first, ties by ID.'''
    counts: dict[str, int] = {}
    for findings in report.get('findings', {}).values():
        for finding in findings:
            for sid in finding['candidates']:
                counts[sid] = counts.get(sid, 0) + 1
    return sorted(counts, key=lambda sid: (-counts[sid], sid))


def fitted(names: list[str], room: int) -> str:
    '''As many of names as fit in room characters, comma-separated, with
    "+N more" for the rest.'''
    for shown in range(len(names), 0, -1):
        rest = len(names) - shown
        text = ', '.join(names[:shown]) + (f', +{rest} more' if rest else '')
        if len(text) <= room:
            return text
    return f'+{len(names)} more'


def due_message(report: dict, today: date) -> str | None:
    '''R9.4: one line under LIMIT characters naming every due item, or None
    when nothing is due. The block item names its candidate sections as far
    as the line has room.'''
    due = report['due']
    before, after = [], []
    if due.get('lint'):
        before.append(plural(due['lint'], 'lint violation'))
    batch = due.get('changelog') or {}
    if batch.get('due'):
        days = (today - date.fromisoformat(batch['last_triage'])).days
        after.append(f"{plural(batch['releases'], 'release')} untriaged (last triage {days} d ago)")
    if due.get('probes'):
        after.append(f"probes due {len(due['probes'])}")
    audit = due.get('audit') or {}
    if audit.get('due'):
        after.append(f"audit due: {audit['group']}")
    blocks = due.get('blocks') or 0
    if not (before or blocks or after):
        return None
    if blocks:
        words = f"{plural(blocks, 'docs block')} changed"
        frame = SEP.join([HEAD, *before, f'{words} ()', *after]) + TO_SKILL
        before.append(f'{words} ({fitted(named_sections(report), LIMIT - 1 - len(frame))})')
    return SEP.join([HEAD, *before, *after]) + TO_SKILL


def age_words(ok_epoch: int | None, now_epoch: int) -> str:
    '''The age of the last good check, in whole days, as notice.sh words it.'''
    if ok_epoch is None:
        return 'no good check yet'
    return f'last good check {(now_epoch - ok_epoch) // DAY} d ago'


def error_message(reason: str, ok_epoch: int | None, now_epoch: int) -> str:
    '''R9.4: an error line with the age of the last good check, the reason
    flattened to one line and cut to keep the line under LIMIT characters.'''
    reason = ' '.join(reason.split())
    age = age_words(ok_epoch, now_epoch)
    room = LIMIT - 1 - len(f'{HEAD}{SEP}check failed: {SEP}{age}{TO_CHECK}')
    if len(reason) > room:
        reason = reason[:room - 1] + '…'
    return f'{HEAD}{SEP}check failed: {reason}{SEP}{age}{TO_CHECK}'


def replace(path: Path, text: str) -> None:
    '''Write text to path by renaming a temporary file over it.'''
    tmp = path.with_name(f'.{path.name}.{os.getpid()}.tmp')
    tmp.write_text(text, encoding='utf-8')
    os.replace(tmp, path)


def write_notice(cache: Path, message: str | None) -> None:
    '''notice.json, then its digest: one ASCII JSON line holding the message
    as systemMessage, or an empty file when nothing is due.'''
    cache.mkdir(parents=True, exist_ok=True)
    text = '' if message is None else json.dumps({'systemMessage': message}) + '\n'
    replace(cache / NOTICE, text)
    replace(cache / DIGEST, hashlib.sha256(text.encode('utf-8')).hexdigest() + '\n')


def read_last_check(cache: Path) -> dict | None:
    '''The record check --hook last wrote, or None when there is none or it
    does not parse.'''
    try:
        data = json.loads((cache / LAST_CHECK).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def last_ok(cache: Path) -> int | None:
    '''The epoch second of the last good check, or None.'''
    value = (read_last_check(cache) or {}).get('ok_epoch')
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def record_check(cache: Path, code: int, now: datetime, run: str | None) -> dict:
    '''last-check.json: this run's ID and exit, and the last good check. An
    exit 0 or 1 is a good check; an exit 2 carries the previous one over.'''
    previous = read_last_check(cache) or {}
    good = code in (0, 1)
    stamp = now.isoformat(timespec='seconds')
    record = {'run': run, 'finished_at': stamp, 'exit': code,
              'ok_at': stamp if good else previous.get('ok_at'),
              'ok_epoch': int(now.timestamp()) if good else last_ok(cache)}
    cache.mkdir(parents=True, exist_ok=True)
    replace(cache / LAST_CHECK, json.dumps(record, indent=1) + '\n')
    return record


def after_check(cache: Path, code: int, report: dict, now: datetime, today: date, run: str | None) -> None:
    '''check --hook once check() returned: the notice for its exit, then the
    record (R9.3, R9.4).'''
    if code == 2:
        reason = report['errors'][0] if report.get('errors') else 'check exited 2'
        message = error_message(reason, last_ok(cache), int(now.timestamp()))
    else:
        message = due_message(report, today) if code == 1 else None
    write_notice(cache, message)
    record_check(cache, code, now, run)


def after_failure(cache: Path, reason: str, now: datetime, run: str | None) -> None:
    '''check --hook on a setup error or a crash: the error line, then the
    record, as for an exit 2.'''
    write_notice(cache, error_message(reason, last_ok(cache), int(now.timestamp())))
    record_check(cache, 2, now, run)
