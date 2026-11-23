'''Audit plan 105's tools reps: the stream audit, the path audit, the read check and the VOID reasons.

Usage, from the repository root:
  uv run python <kit>/audit.py <rep-dir> ...
Each <rep-dir> is a rep<N>/ folder that run_tool_reps.sh wrote, under <case>/<arm>/<model>/; a model
folder stands for each rep<N>/ in it. The raw stream is read from the scratch folder,
WSL_SCRATCH/<case>/<arm>/<model>/rep<N>.jsonl (WSL_SCRATCH defaults to
~/.cache/agent-skills/scratch/plan105/tools). For each rep it prints:
- the stream audit, read from the raw stream whatever summary.json holds: each line that is not a JSON
  object, the record counts, and V9 (plan 104's check, from plan 102): a peer `origin` at any depth of
  any record, or a cross-session tool in the init record. A second result record is a peer turn too;
- the run (exit, subtype, cost, turns), the init record's tools, and a skill copy that changed during
  the rep;
- the path audit: each Read, Edit or Write file_path, each Grep path and each Glob path and pattern,
  outside the rep folder and the skill copy (each in its /tmp and /private/tmp forms), with each `..`
  resolved first; an Edit or Write into the skill copy; any spelling of the real home; any path through
  $HOME/Library in any case, a `..` after a point in it included (its Keychains folder is a link). A
  relative path (file_path, or a Grep or Glob path) is joined to the rep's repository first, the
  working directory. A Glob
  pattern counts when it is absolute or climbs with `..`: its literal part, up to the last `/` before
  its first wildcard, is judged, and a `..` after a wildcard is a hit, since it cannot be resolved.
  Plan 104's audit covers Read, Edit, Write and Bash only; these reps have Grep and Glob, so the audit
  also checks their path arguments. The Bash part is plan 104's, kept for a call no rep should make;
- each Read of the case's moved file (cases.MOVED), marked partial when it has `offset` or `limit` and
  marked error when its tool result is an error, the first Edit or Write of the case's target
  (cases.TARGET, under the rep's repository; a relative file_path is joined to it), and the read check: PASS when such a Read comes before
  that first Edit or Write, or when the rep never edits or writes the target and has such a Read;
- the VOID reasons (void_reasons), or `VOID: none`.
It gives no verdict on the marker: the blind grader reads that from the sheets (sheets.py).
'''
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases  # noqa: E402
import rep_tools  # noqa: E402

CROSS_SESSION_TOOLS = ('ListAgents', 'SendMessage', 'PushNotification', 'RemoteTrigger')
REP_TOOLS = ('Read', 'Glob', 'Grep', 'Edit', 'Write')
ORIGIN, PEER = 'origin', 'peer'
BUDGET = 'error_max_budget_usd'
REAL_HOME_TOKEN = '<REAL-HOME>'
PATH_IN_COMMAND = re.compile(r'''(?<![\w.\-/])(/[^\s'"`;|&<>(){}]*|~[^\s'"`;|&<>(){}]*|\$\{?HOME\}?[^\s'"`;|&<>(){}]*)''')
HOME_VAR = re.compile(r'^\$\{?HOME\}?')
# /Users, //Users or /System/Volumes/Data/Users as a path's root, and a ~user path.
USERS_ROOT = re.compile(r'''(?:^|[\s'"=:(])/+(?:system/volumes/data/+)?users(?:/|$|[\s'"])''', re.I)
TILDE_USER = re.compile(r'''(?:^|[\s'"=:(])~[A-Za-z_$]''')
WILDCARD = re.compile(r'[*?\[{]')


def scratch() -> Path:
    return Path(os.environ.get('WSL_SCRATCH') or Path.home() / '.cache/agent-skills/scratch/plan105/tools')


def forms(root: str) -> list[str]:
    found = [root]
    if root.startswith('/private/tmp/'):
        found.append(root[len('/private'):])
    elif root.startswith('/tmp/'):
        found.append('/private' + root)
    return found


def under(path: str, roots: list[str]) -> bool:
    return any(path == root or path.startswith(root + '/') for root in roots)


def literal_part(pattern: str) -> str:
    '''A Glob pattern up to the last `/` before its first wildcard, or the whole pattern when it has none.'''
    first = WILDCARD.search(pattern)
    if first is None:
        return pattern
    head = pattern[:first.start()]
    return head[:head.rfind('/') + 1]


def climbs_after_wildcard(pattern: str) -> bool:
    parts = pattern.split('/')
    wild = next((index for index, part in enumerate(parts) if WILDCARD.search(part)), len(parts))
    return '..' in parts[wild:]


class Audit:
    def __init__(self, summary: dict) -> None:
        self.rep = forms(summary.get('rep_dir') or '/nonexistent-rep')
        self.repo = self.rep[0] + '/repo'
        self.read_only = forms(summary.get('skill_root') or '/nonexistent-copy')
        # Lowercased: the volume is case-insensitive, so home/library/keychains reaches the same link.
        self.library = [f'{root}/home/Library'.lower() for root in self.rep]
        home = str(Path.home())
        self.real = sorted({home.lower(), os.path.realpath(home).lower()})

    def real_home(self, text: str) -> bool:
        low = text.lower()
        return REAL_HOME_TOKEN.lower() in low or any(real in low for real in self.real) \
            or USERS_ROOT.search(text) is not None or TILDE_USER.search(text) is not None

    def in_library(self, path: str) -> bool:
        '''True when the resolved path is in $HOME/Library, in any case.'''
        return under(os.path.normpath(path or '/').lower(), self.library)

    def climbs_from_library(self, path: str) -> bool:
        '''True when a `..` follows a point in $HOME/Library. Its Keychains folder links to the real
        home's, and the kernel resolves a `..` after a link from the link's target, not from the text.'''
        parts = path.split('/')
        return any(part == '..' and self.in_library('/'.join(parts[:index])) for index, part in enumerate(parts))

    def judge(self, path: str, writes: bool = False) -> str | None:
        '''Why a path is a hit, or None.'''
        if HOME_VAR.match(path):
            path = self.rep[0] + '/home' + HOME_VAR.sub('', path)
        elif path == '~' or path.startswith('~/'):
            path = self.rep[0] + '/home' + path[1:]
        # Resolve each `..` before the root checks, so a path cannot climb out of a root unseen.
        clean = os.path.normpath(path)
        if self.real_home(path) or self.real_home(clean):
            return 'the real home'
        if self.climbs_from_library(path) or self.in_library(clean):
            return '$HOME/Library'
        if under(clean, self.rep):
            return None
        if under(clean, self.read_only):
            return 'a write into a read-only root' if writes else None
        return 'outside the allowed roots'

    def joined(self, path: str, base: str | None = None) -> str:
        '''A relative path joined to base, or to the rep's repository (the working directory).'''
        if path.startswith(('/', '~')) or HOME_VAR.match(path):
            return path
        return f'{base or self.repo}/{path}'

    def search_hits(self, number: int, name: str, args: dict) -> list[str]:
        found = []
        base = args.get('path')
        if base:
            why = self.judge(self.joined(base))
            if why:
                found.append(f'call {number} {name} path: {base} ({why})')
        pattern = args.get('pattern') or ''
        if name == 'Glob' and pattern:
            if climbs_after_wildcard(pattern):
                found.append(f'call {number} Glob pattern: {pattern} (a `..` after a wildcard)')
            elif pattern.startswith(('/', '~')) or HOME_VAR.match(pattern) or '..' in pattern.split('/'):
                why = self.judge(self.joined(literal_part(pattern) or '.', self.joined(base) if base else None))
                if why:
                    found.append(f'call {number} Glob pattern: {pattern} ({why})')
        return found

    def hits(self, calls: list[dict]) -> list[str]:
        found = []
        for number, call in enumerate(calls, 1):
            args = call.get('input') or {}
            if call.get('name') in ('Read', 'Edit', 'Write'):
                path = args.get('file_path', '')
                why = self.judge(self.joined(path) if path else path, writes=call.get('name') != 'Read')
                if why:
                    found.append(f'call {number} {call["name"]}: {path} ({why})')
            elif call.get('name') in ('Grep', 'Glob'):
                found += self.search_hits(number, call['name'], args)
            elif call.get('name') == 'Bash':
                command = args.get('command', '')
                named = []
                for match in PATH_IN_COMMAND.finditer(command):
                    path = match.group(1)
                    if path == '/dev/null':
                        continue
                    why = self.judge(path)
                    if why:
                        named.append(why)
                        context = command[max(0, match.start() - 25):match.end() + 15]
                        found.append(f'call {number} Bash names {path} ({why}), in: {context!r}')
                if 'the real home' not in named and self.real_home(command):
                    found.append(f'call {number} Bash spells the real home: {command[:200]!r}')
                if '..' in command:
                    found.append(f'call {number} Bash holds "..": {command[:200]!r}')
        return found


def origins(record) -> list:
    found, stack = [], [record]
    while stack:
        obj = stack.pop()
        if isinstance(obj, dict):
            if ORIGIN in obj:
                found.append(obj[ORIGIN])
            stack.extend(obj.values())
        elif isinstance(obj, list):
            stack.extend(obj)
    return found


def stream_path(rep: Path) -> Path:
    model, arm, case = rep.parent.name, rep.parent.parent.name, rep.parent.parent.parent.name
    return scratch() / case / arm / model / f'{rep.name}.jsonl'


def stream_audit(path: Path) -> dict:
    '''The raw stream's line check, record counts, V9 findings, tool calls and first result record.'''
    found = {'missing': not path.is_file(), 'bad': [], 'records': 0, 'inits': 0, 'results': 0, 'peers': 0,
             'cross_tools': [], 'other_tools': [], 'calls': [], 'result': None}
    if found['missing']:
        return found
    records, bad = rep_tools.read_stream(path.read_bytes())
    inits = [r for r in records if r.get('type') == 'system' and r.get('subtype') == 'init']
    results = [r for r in records if r.get('type') == 'result']
    listed = {tool for r in inits if isinstance(r.get('tools'), list) for tool in r['tools'] if isinstance(tool, str)}
    found.update({
        'bad': bad, 'records': len(records), 'inits': len(inits), 'results': len(results),
        'peers': sum(1 for r in records if any(isinstance(o, dict) and o.get('kind') == PEER for o in origins(r))),
        'cross_tools': [tool for tool in CROSS_SESSION_TOOLS if tool in listed],
        'other_tools': sorted(listed - set(REP_TOOLS) - set(CROSS_SESSION_TOOLS)),
        'calls': rep_tools.read_records(records)['calls'], 'result': results[0] if results else None,
    })
    return found


def read_check(calls: list[dict], case: str, rep_dir: str) -> dict:
    '''The reading rule's Read part: a Read of the moved file before the first Edit or Write of the target.'''
    moved, target = cases.MOVED[case], cases.TARGET[case]
    roots = forms(rep_dir or '/nonexistent-rep')
    targets = {os.path.normpath(f'{root}/repo/{target}') for root in roots}
    reads, first_write = [], None
    for number, call in enumerate(calls, 1):
        args = call.get('input') or {}
        path = args.get('file_path') or ''
        if call.get('name') == 'Read' and path.endswith('/' + moved):
            reads.append({'call': number, 'path': path, 'error': bool(call.get('is_error')),
                          'partial': args.get('offset') is not None or args.get('limit') is not None})
        elif call.get('name') in ('Edit', 'Write') and first_write is None and path:
            full = path if path.startswith('/') else f'{roots[0]}/repo/{path}'
            if os.path.normpath(full) in targets:
                first_write = number
    before = [read for read in reads if first_write is None or read['call'] < first_write]
    return {'moved': moved, 'target': target, 'reads': reads, 'first_write': first_write,
            'verdict': 'PASS' if before else 'FAIL'}


def load_summary(rep: Path) -> dict | None:
    try:
        summary = json.loads((rep / 'summary.json').read_text())
    except (OSError, ValueError):
        return None
    return summary if isinstance(summary, dict) else None


def audit_rep(rep: Path) -> dict:
    '''Everything audit.py prints for one rep, with its VOID reasons and its read check.'''
    summary = load_summary(rep)
    stream = stream_audit(stream_path(rep))
    void = []
    if summary is None:
        void.append('kit error: no summary.json')
    elif 'kit_error' in summary:
        void.append(f'kit error: {summary["kit_error"]}')
    if stream['missing']:
        void.append('kit error: no raw stream')
    if stream['bad']:
        void.append(f'stream line(s) {", ".join(map(str, stream["bad"]))} not JSON')
    if stream['peers']:
        void.append(f'V9: {stream["peers"]} peer-origin record(s)')
    if stream['cross_tools']:
        void.append(f'V9: cross-session tool in the init record: {", ".join(stream["cross_tools"])}')
    if stream['results'] > 1:
        void.append('a second result record')
    result = stream['result'] or {}
    if not stream['missing'] and not stream['results']:
        void.append('no result record')
    elif result.get('subtype') == BUDGET:
        void.append(f'subtype {BUDGET}')
    elif result and result.get('subtype') != 'success':
        void.append(f'a run error: subtype {result.get("subtype")}')
    elif result.get('is_error'):
        void.append('a run error: is_error true')
    hits = Audit(summary or {}).hits(stream['calls'])
    if hits:
        void.append(f'path audit: {len(hits)} hit(s)')
    if summary and summary.get('skill_copy_changed'):
        void.append('skill copy changed during the rep')
    case = rep.parent.parent.parent.name
    read = read_check(stream['calls'], case, (summary or {}).get('rep_dir')) if case in cases.MOVED else None
    return {'summary': summary or {}, 'stream': stream, 'hits': hits, 'read': read, 'void': void}


def void_reasons(rep: Path) -> list[str]:
    return audit_rep(rep)['void']


def show(rep: Path) -> None:
    model, arm, case = rep.parent.name, rep.parent.parent.name, rep.parent.parent.parent.name
    print(f'== {case} {arm} {model} {rep.name}')
    found = audit_rep(rep)
    stream, summary = found['stream'], found['summary']
    if stream['missing']:
        print(f'  stream: missing at {stream_path(rep)}')
    for number in stream['bad']:
        print(f'  stream line {number} is not JSON')
    print(f'  stream: {stream["records"]} record(s), {len(stream["bad"])} line(s) not JSON, {stream["inits"]} init, '
          f'{stream["results"]} result')
    v9 = [reason for reason in found['void'] if reason.startswith('V9')]
    print(f'  V9: FOUND {"; ".join(reason[4:] for reason in v9)}' if v9 else '  V9: none')
    if stream['other_tools']:
        print(f'  init record lists tools beyond {", ".join(REP_TOOLS)}: {", ".join(stream["other_tools"])}')
    result = stream['result'] or {}
    print(f'  exit {summary.get("claude_exit")}, subtype {result.get("subtype")}, is_error {result.get("is_error")}, '
          f'cost {result.get("total_cost_usd")}, turns {result.get("num_turns")}, tool calls {len(stream["calls"])}')
    for problem in summary.get('skill_copy_changed') or []:
        print(f'  skill copy changed during the rep: {problem}')
    print(f'  path audit: {len(found["hits"])} hit(s)')
    for hit in found['hits']:
        print(f'    {hit}')
    read = found['read']
    if read is not None:
        marks = [f'call {r["call"]}' + (' (partial)' if r['partial'] else '') + (' (error)' if r['error'] else '')
                 for r in read['reads']]
        print(f'  reads of {read["moved"]}: {", ".join(marks) or "none"}')
        first = f'call {read["first_write"]}' if read['first_write'] else 'none'
        print(f'  first Edit or Write of {read["target"]}: {first}')
        print(f'  read check: {read["verdict"]}')
    print(f'  VOID: {"; ".join(found["void"]) or "none"}')


def rep_folders(arg: str) -> list[Path]:
    path = Path(arg).resolve()
    if path.is_dir() and path.name[:3] == 'rep' and path.name[3:].isdigit():
        return [path]
    reps = sorted((p for p in path.glob('rep*') if p.is_dir() and p.name[3:].isdigit()), key=lambda p: int(p.name[3:]))
    if not reps:
        raise SystemExit(f'refusing: {arg} holds no rep folder')
    return reps


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for arg in sys.argv[1:]:
        for rep in rep_folders(arg):
            show(rep)


if __name__ == '__main__':
    main()
