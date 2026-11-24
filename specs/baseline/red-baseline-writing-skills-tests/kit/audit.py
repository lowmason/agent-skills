'''Audit plan 107's reps: the stream audit, the path audit, the Bash audit, the reference reads, the R3 tree
check and the VOID reasons.

Copy of plan 105's audit.py (specs/baseline/red-baseline-writing-skills-layout/kit/audit.py). Its changes:
the three Glob limits that plan 105 recorded are closed (Glob, below), a Bash call is audited, the read check
became descriptive reference reads, R3 has a tree check, and a trigger rep (run_trigger_reps.sh) is audited
too, with a listing check.

Usage, from the repository root:
  uv run python <kit>/audit.py <rep-dir> ...
Each <rep-dir> is a rep<N>/ folder that a runner wrote, under <case>/<arm>/<model>/ for a case rep or
<prompt>/<arm>/<condition>/<model>/ for a trigger rep (condition `full` or `cut150`). A model folder stands
for each rep<N>/ in it. The raw stream is read from the scratch folder: WST_SCRATCH/<case>/<arm>/<model>/
rep<N>.jsonl (default ~/.cache/agent-skills/scratch/plan107/cases) for a case rep, and
WST_TRIGGER_SCRATCH/<prompt>/<arm>/<condition>/<model>/rep<N>.jsonl (default .../plan107/triggers) for a
trigger rep. For each rep it prints:
- the stream audit, read from the raw stream whatever summary.json holds: each line that is not a JSON
  object, the record counts, and V9 (plan 104's check, from plan 102): a peer `origin` at any depth of
  any record, or a cross-session tool in the init record. A second result record is a peer turn too;
- the run (exit, subtype, cost, turns), the init record's tools, and a skill copy that changed during
  the rep;
- the path audit: each Read, Edit or Write file_path, each Grep path and each Glob path and pattern,
  outside the rep folder and the skill copy (each in its /tmp and /private/tmp forms), with each `..`
  resolved first; an Edit or Write into the skill copy; any spelling of the real home; any path through
  $HOME/Library in any case, a `..` after a point in it included (its Keychains folder is a link). A
  relative path is joined to the rep's repository first, the working directory.
  Glob (plan 107 closes plan 105's three recorded limits). A pattern's braces are expanded: each concrete
  pattern is judged on its own, so a brace alternative is joined to the text before it (limit 2: an
  absolute prefix, limit 3: a `$HOME`, `~` or home/ prefix) and to the text after it. More than
  MAX_EXPANSIONS expansions is a hit. A pattern is judged by the directory its wildcard part searches from
  (the search root): its literal part, up to the last `/` before the first wildcard, joined to the Glob
  `path` (or the repository) when it is relative. A `..` after a wildcard is a hit, since it cannot be
  resolved, and so is a `..` in a brace alternative, and so is a brace alternative that is a path of its
  own outside the allowed roots. Limit 1: a wildcard search that can list a name under the rep's
  home/Library, whose Keychains folder links to the real one, is a hit: its search root is the rep folder,
  its home/ or an ancestor of home/Library, and a `**`, or a run of wildcard segments that match `home`
  and `Library`, reaches it. A single `*` counts too (`*/Library/Keychains/*` from the rep folder).
  Grep is judged by its path only, not by its pattern: ripgrep does not follow the link;
- the Bash audit: a Bash call is clean only when its command is one `git mv <src> <dst>`, with plain path
  words (no quote, `$`, `~`, wildcard, brace, `;`, `&`, `|` or redirect) and both paths inside the rep's
  repo/. A flag is not tested: `git mv -f a` reads as a move of `-f` to `a`, is clean, and moves nothing.
  Any other Bash call is a hit, whether or not it succeeded;
- the reads of the case's reference file (cases.REFERENCE), marked partial when a Read has `offset` or
  `limit` and marked error when its tool result is an error. This is descriptive and never scores a rep;
- for R3, the tree check (r3_check) of the parked final repository, and whether the final message names
  the near collision `sniffing-csv-headers` (descriptive);
- the VOID reasons (void_reasons), or `VOID: none`. A trigger rep is also void when its init record's skill
  listing lacks `writing-skills`, `skill-development` or `skill-creator`. The subtypes `error_max_turns` and
  `error_max_budget_usd` are a normal end for a trigger rep, not a VOID reason.
It gives no verdict on a graded case: the blind grader reads that from the sheets (sheets.py).
'''
import fnmatch
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases  # noqa: E402
import rep_tools  # noqa: E402
import triggers  # noqa: E402

CROSS_SESSION_TOOLS = ('ListAgents', 'SendMessage', 'PushNotification', 'RemoteTrigger')
REP_TOOLS = ('Read', 'Glob', 'Grep', 'Edit', 'Write')
ORIGIN, PEER = 'origin', 'peer'
BUDGET = 'error_max_budget_usd'
MAX_TURNS = 'error_max_turns'
TRIGGER_NORMAL_ENDS = (BUDGET, MAX_TURNS)
CONDITIONS = ('full', 'cut150')
REQUIRED_LISTING = ('writing-skills', 'skill-development', 'skill-creator')
REAL_HOME_TOKEN = '<REAL-HOME>'
HOME_VAR = re.compile(r'^\$\{?HOME\}?')
# /Users, //Users or /System/Volumes/Data/Users as a path's root, and a ~user path.
USERS_ROOT = re.compile(r'''(?:^|[\s'"=:(])/+(?:system/volumes/data/+)?users(?:/|$|[\s'"])''', re.I)
TILDE_USER = re.compile(r'''(?:^|[\s'"=:(])~[A-Za-z_$]''')
WILDCARD = re.compile(r'[*?\[{]')
# More brace expansions than this is a hit: no honest search needs more, and the count grows fast.
MAX_EXPANSIONS = 64
# One `git mv <src> <dst>`: plain path words only, and spaces or tabs between the words. A leading `-` is allowed in a word.
GIT_MV = re.compile(r'^git[ \t]+mv[ \t]+([A-Za-z0-9_./@%+:,=-]+)[ \t]+([A-Za-z0-9_./@%+:,=-]+)$')
OLD_NAME, NEW_NAME = 'csv-dialect-sniff', 'sniffing-csv-dialects'
NEIGHBOR = 'sniffing-csv-headers'


def scratch() -> Path:
    return Path(os.environ.get('WST_SCRATCH') or Path.home() / '.cache/agent-skills/scratch/plan107/cases')


def trigger_scratch() -> Path:
    return Path(os.environ.get('WST_TRIGGER_SCRATCH') or Path.home() / '.cache/agent-skills/scratch/plan107/triggers')


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


def brace_alternatives(pattern: str) -> list[str]:
    '''Each comma-split alternative of each {...} group in a Glob pattern, nested groups included.'''
    found, starts = [], []
    for index, char in enumerate(pattern):
        if char == '{':
            starts.append(index + 1)
        elif char == ',' and starts:
            found.append(pattern[starts[-1]:index])
            starts[-1] = index + 1
        elif char == '}' and starts:
            found.append(pattern[starts.pop():index])
    return found


def split_top_level(inner: str) -> list[str]:
    '''The comma-split parts of a brace group's text, outside any nested group.'''
    parts, depth, begin = [], 0, 0
    for index, char in enumerate(inner):
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
        elif char == ',' and depth == 0:
            parts.append(inner[begin:index])
            begin = index + 1
    return parts + [inner[begin:]]


def expand_braces(pattern: str, limit: int = MAX_EXPANSIONS) -> list[str] | None:
    '''Every concrete pattern that the braces of a Glob pattern expand to, in order, or None when there are more
    than `limit`. An alternative is joined to the text before its group and the text after it. A `{` with no
    matching `}` stays literal.'''
    start = pattern.find('{')
    if start == -1:
        return [pattern]
    depth, end = 0, -1
    for index in range(start, len(pattern)):
        if pattern[index] == '{':
            depth += 1
        elif pattern[index] == '}':
            depth -= 1
            if depth == 0:
                end = index
                break
    if end == -1:
        return [pattern]
    prefix, suffix = pattern[:start], pattern[end + 1:]
    found = []
    for alternative in split_top_level(pattern[start + 1:end]):
        sub = expand_braces(prefix + alternative + suffix, limit)
        if sub is None:
            return None
        found += sub
        if len(found) > limit:
            return None
    return found


def git_mv_paths(command: str) -> tuple[str, str] | None:
    '''The two paths of a command that is exactly one `git mv <src> <dst>`, or None.'''
    found = GIT_MV.match(command.strip())
    return (found[1], found[2]) if found else None


class Audit:
    def __init__(self, summary: dict) -> None:
        self.rep = forms(summary.get('rep_dir') or '/nonexistent-rep')
        self.repo = self.rep[0] + '/repo'
        self.repos = [f'{root}/repo' for root in self.rep]
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

    def home_mapped(self, path: str) -> str:
        '''A path with a leading `$HOME` or `~` written as the rep's own home/.'''
        if HOME_VAR.match(path):
            return self.rep[0] + '/home' + HOME_VAR.sub('', path)
        if path == '~' or path.startswith('~/'):
            return self.rep[0] + '/home' + path[1:]
        return path

    def judge(self, path: str, writes: bool = False) -> str | None:
        '''Why a path is a hit, or None.'''
        path = self.home_mapped(path)
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

    def reaches_library(self, root: str, rest: str) -> bool:
        '''True when a wildcard search that starts at root, with the pattern text `rest` after it, can list a
        name at or under the rep's home/Library (limit 1). root must be an ancestor of home/Library.'''
        start = os.path.normpath(self.home_mapped(root) or '/').lower()
        segments = [segment.lower() for segment in rest.split('/') if segment]
        for library in self.library:
            if library != start and not library.startswith(start.rstrip('/') + '/'):
                continue
            below = [part for part in library[len(start):].split('/') if part]
            if wildcard_matches(segments, below):
                return True
        return False

    def pattern_hit(self, pattern: str, root: str) -> str | None:
        '''Why one concrete (brace-free) Glob pattern is a hit, searched from root, or None.'''
        if climbs_after_wildcard(pattern):
            return 'a `..` after a wildcard'
        literal = literal_part(pattern)
        if pattern.startswith(('/', '~')) or HOME_VAR.match(pattern):
            search = literal
        else:
            search = self.joined(literal or '.', root)
        why = self.judge(search)
        if why:
            return why
        if self.reaches_library(search, pattern[len(literal):]):
            return 'a wildcard search that can list $HOME/Library'
        return None

    def glob_hit(self, pattern: str, root: str) -> str | None:
        '''Why a Glob pattern is a hit, searched from root, or None. Each brace alternative is a path of its
        own, and the expansion joins each one to the text around its group.'''
        if climbs_after_wildcard(pattern):
            return 'a `..` after a wildcard'
        for alternative in brace_alternatives(pattern):
            if '..' in alternative.split('/'):
                return 'a `..` in a brace alternative'
            if alternative.startswith(('/', '~')) or HOME_VAR.match(alternative):
                why = self.judge(literal_part(alternative) or '/')
                if why:
                    return why
        expanded = expand_braces(pattern)
        if expanded is None:
            return f'more than {MAX_EXPANSIONS} brace alternatives'
        for concrete in expanded:
            why = self.pattern_hit(concrete, root)
            if why:
                return why
        return None

    def search_hits(self, number: int, name: str, args: dict) -> list[str]:
        base = args.get('path')
        root = self.joined(base) if base else self.repo
        if base:
            why = self.judge(root)
            if why:
                return [f'call {number} {name} path: {base} ({why})']
        pattern = args.get('pattern') or ''
        if name == 'Glob' and pattern:
            why = self.glob_hit(pattern, root)
            if why:
                return [f'call {number} Glob pattern: {pattern} ({why})']
        return []

    def bash_hit(self, command: str) -> str | None:
        '''Why a Bash command is a hit, or None: it must be one `git mv` between two paths inside repo/.'''
        paths = git_mv_paths(command)
        if paths is None:
            return 'not one git mv between plain paths'
        for path in paths:
            clean = os.path.normpath(self.joined(path))
            if not any(clean.startswith(repo + '/') for repo in self.repos):
                return f'a git mv path outside the rep repo: {path}'
        return None

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
                why = self.bash_hit(command)
                if why:
                    found.append(f'call {number} Bash: {command[:200]!r} ({why})')
        return found


def wildcard_matches(segments: list[str], below: list[str]) -> bool:
    '''True when a wildcard pattern's segments, matched from an ancestor, reach the path `below` it (the names
    of each folder down to home/Library, lowercase) or go past it. A `**` reaches it, and so does a run of
    segments that match each name in turn.'''
    if not below:
        return True
    if not segments:
        return False
    if segments[0] == '**':
        return True
    return fnmatch.fnmatchcase(below[0], segments[0]) and wildcard_matches(segments[1:], below[1:])


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


def rep_layout(rep: Path) -> dict:
    '''A case rep is <case>/<arm>/<model>/rep<N>, a trigger rep <prompt>/<arm>/<condition>/<model>/rep<N>.'''
    model, mid = rep.parent.name, rep.parent.parent.name
    if mid in CONDITIONS:
        return {'kind': 'trigger', 'case': rep.parent.parent.parent.parent.name, 'arm': rep.parent.parent.parent.name,
                'condition': mid, 'model': model}
    return {'kind': 'case', 'case': rep.parent.parent.parent.name, 'arm': mid, 'condition': None, 'model': model}


def stream_path(rep: Path) -> Path:
    where = rep_layout(rep)
    if where['kind'] == 'trigger':
        return trigger_scratch() / where['case'] / where['arm'] / where['condition'] / where['model'] / f'{rep.name}.jsonl'
    return scratch() / where['case'] / where['arm'] / where['model'] / f'{rep.name}.jsonl'


def parked_repo(rep: Path) -> Path:
    '''The finished repository of a rep: the runner parks the rep folder beside the raw stream.'''
    return stream_path(rep).with_name(f'{rep.name}-folder') / 'repo'


def stream_audit(path: Path) -> dict:
    '''The raw stream's line check, record counts, V9 findings, tool calls, listing and first result record.'''
    found = {'missing': not path.is_file(), 'bad': [], 'records': 0, 'inits': 0, 'results': 0, 'peers': 0,
             'cross_tools': [], 'other_tools': [], 'calls': [], 'result': None, 'listing': []}
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
        'listing': triggers.listing(records),
    })
    return found


def reference_reads(calls: list[dict], case: str) -> list[dict]:
    '''Each Read of the case's reference file (cases.REFERENCE): descriptive, never a verdict. A Read whose result
    is an error is marked, since it gave the rep no content.'''
    reference = cases.REFERENCE[case]
    reads = []
    for number, call in enumerate(calls, 1):
        args = call.get('input') or {}
        path = args.get('file_path') or ''
        if call.get('name') == 'Read' and path.endswith('/' + reference):
            reads.append({'call': number, 'path': path, 'error': bool(call.get('is_error')),
                          'partial': args.get('offset') is not None or args.get('limit') is not None})
    return reads


def skill_name(text: str) -> str | None:
    '''The `name:` of a SKILL.md's frontmatter, or None when it has none.'''
    if not text.startswith('---\n') or '\n---' not in text[4:]:
        return None
    for line in text[4:text.index('\n---', 4)].splitlines():
        if line.startswith('name:'):
            return line[len('name:'):].strip().strip('\'"')
    return None


def r3_check(repo: Path) -> dict:
    '''The R3 pass rule on a finished repository: the new skill exists with the new name, the old folder is
    gone, and the old name is in no file. Every file counts, untracked and ignored ones and dotfiles included;
    only a folder named .git is skipped, as `grep -r --exclude-dir=.git` skips it, and a symlink is not
    followed. A git command would miss an untracked or ignored file, so this walks the folder.'''
    problems = []
    skill = repo / 'skills' / NEW_NAME / 'SKILL.md'
    if not skill.is_file():
        problems.append(f'skills/{NEW_NAME}/SKILL.md is missing')
    else:
        name = skill_name(skill.read_text(errors='replace'))
        if name != NEW_NAME:
            problems.append(f'skills/{NEW_NAME}/SKILL.md has name {name!r}, not {NEW_NAME!r}')
    if (repo / 'skills' / OLD_NAME).exists():
        problems.append(f'skills/{OLD_NAME}/ still exists')
    for folder, names, files in os.walk(repo):
        names[:] = [name for name in names if name != '.git']
        for file in sorted(files):
            path = Path(folder) / file
            if not path.is_symlink() and OLD_NAME.encode() in path.read_bytes():
                problems.append(f'{path.relative_to(repo)} holds {OLD_NAME}')
    return {'verdict': 'FAIL' if problems else 'PASS', 'problems': sorted(problems)}


def load_summary(rep: Path) -> dict | None:
    try:
        summary = json.loads((rep / 'summary.json').read_text())
    except (OSError, ValueError):
        return None
    return summary if isinstance(summary, dict) else None


def run_end_void(result: dict, trigger: bool) -> str | None:
    '''Why a result record makes a rep void, or None. A trigger rep ends normally on its turn or budget limit.'''
    subtype = result.get('subtype')
    if trigger and subtype in TRIGGER_NORMAL_ENDS:
        return None
    if subtype == BUDGET:
        return f'subtype {BUDGET}'
    if result and subtype != 'success':
        return f'a run error: subtype {subtype}'
    if result.get('is_error'):
        return 'a run error: is_error true'
    return None


def audit_rep(rep: Path) -> dict:
    '''Everything audit.py prints for one rep, with its VOID reasons, its reference reads and its R3 check.'''
    where = rep_layout(rep)
    trigger = where['kind'] == 'trigger'
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
    else:
        ended = run_end_void(result, trigger)
        if ended:
            void.append(ended)
    hits = Audit(summary or {}).hits(stream['calls'])
    if hits:
        void.append(f'path audit: {len(hits)} hit(s)')
    if summary and summary.get('skill_copy_changed'):
        void.append('skill copy changed during the rep')
    if trigger and not stream['missing']:
        lacking = [name for name in REQUIRED_LISTING if name not in stream['listing']]
        if lacking:
            void.append(f'listing lacks {", ".join(lacking)}')
    case = where['case']
    reads, r3, flagged = None, None, None
    if not trigger and case in cases.REFERENCE:
        reads = reference_reads(stream['calls'], case)
    if not trigger and case == 'R3':
        tree = parked_repo(rep)
        r3 = r3_check(tree) if tree.is_dir() else (summary or {}).get('r3_check')
        flagged = NEIGHBOR in ((summary or {}).get('final_message') or '')
    return {'summary': summary or {}, 'stream': stream, 'hits': hits, 'reads': reads, 'r3': r3, 'flagged': flagged,
            'void': void, 'where': where}


def void_reasons(rep: Path) -> list[str]:
    return audit_rep(rep)['void']


def show(rep: Path) -> None:
    found = audit_rep(rep)
    where = found['where']
    names = [where['case'], where['arm']] + ([where['condition']] if where['condition'] else []) + [where['model']]
    print(f'== {" ".join(names)} {rep.name}')
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
    if found['reads'] is not None:
        reference = cases.REFERENCE[where['case']]
        marks = [f'call {r["call"]}' + (' (partial)' if r['partial'] else '') + (' (error)' if r['error'] else '')
                 for r in found['reads']]
        print(f'  reads of {reference}: {", ".join(marks) or "none"}')
    if found['r3'] is not None:
        print(f'  r3 check: {found["r3"]["verdict"]}')
        for problem in found['r3']['problems']:
            print(f'    {problem}')
        print(f'  names {NEIGHBOR} in the final message: {"yes" if found["flagged"] else "no"}')
    if where['kind'] == 'trigger':
        print(f'  listing: {", ".join(stream["listing"]) or "none"}')
        print(f'  loads writing-skills: {"yes" if triggers.is_load_in(stream["calls"]) else "no"}')
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
