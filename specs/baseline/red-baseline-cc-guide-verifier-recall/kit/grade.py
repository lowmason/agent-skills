'''Grade plan 102's reps blind, under Python 3.13 (Task 7; plan 45's V1 to
V8 and DF15, as plan 102's Pre-registration amends them):

    grade.py <batch>        a sheet for each rep of the batch that has results
    grade.py stop <batch>   gate A's first-wave stop: continue, stop: UNSETTLED or stop: FAIL
    grade.py unblind A|F    the gate's tables, once every sheet of the gate has its verdicts

A sheet, $K/sheets/<rid>.txt, names no arm. It holds the VOID checks V1 to
V8 (each `ok`, `void` with its reasons, `pending` until $K/pilot.json gives
the value the check needs, or for V3 `hits` to trace by hand), the calls
the read fence refused (V2 counts the rep's own session tool-results folder
as inside), the main session's V3 hits, the cost and duration,
and settle's lines for the rep's report. Settle runs on a copy of the
packet in $K/settle/<rid>/packet/ with the report as report.md. Every audit
rep, of either arm, settles against the copy of $K/fixtures/audit-changed/
(DF15), whose `docs` and `quotes.docs` name $K/fixtures/docs, since the
rep's own docs copy has moved to $K/homes/. Settle's folder becomes
`<packet copy>` on the sheet, and its closing commands and a files packet's
hold line are left out. An audit sheet then lists the B rows on
changelog.md:1288, :1702 and :224, every row that names deniedModels, every
kept correction and C row with its guide line and section, the listed-item
counts and the B-row counts. A files sheet lists every kept contradicts row
(a precision rep's with whether it overlaps an entry of
$K/precision-key.tsv), whether a kept row names a covered file, and every
row on hooks/README.md lines 85 to 93. $K/sheets/<rid>.json holds the
sheet's measures for unblind. The report is a finished Agent result that is
no launch notice, else the verifier's last SubagentHandback; never the
verifier's own last text. It is saved as $K/reports/<rid>.md.

$K/RESULTS.md holds the hand verdicts, one a line: `<rid> valid` or `<rid>
void`; for a valid audit rep `<rid> P11 yes|no`, `<rid> P8 yes|no`, `<rid>
hits P1 P3 ...` or `<rid> hits none` (P1 to P14 but P8 and P11) and `<rid>
unsupported <n>`; for a valid readme rep `<rid> readme89 yes|no` and `<rid>
unsupported <n>`; for a valid precision rep `<rid> reach yes|no`, `<rid>
keymiss <n>` and `<rid> unsupported <n>`. A line that starts with a rep id
must be one of these; every other line is skipped. `stop` and `unblind`
refuse, naming rep ids only, until each rep has its verdicts, a sheet and
its measures file (a void rep needs none), and while a valid verdict sits on
a sheet whose V1, V2 or V4 to V8 is void or pending. `stop` also refuses
while either arm has fewer than 2 valid reps, naming the void reps that no
valid spare replaces. `grade.py <batch>` reads both arm files first and
refuses the whole batch, naming nothing, when one is missing or unreadable.
Nothing but unblind's tables names an arm, and no command prints a count
per arm before it.

Exit 0 on success, 1 on a refusal or a rep that could not be graded, 2 on a
usage error or a failure. A failure prints its exception's type, never its
message, which may name an arm's file.'''
import json
import os
import re
import shutil
import statistics
import sys
from pathlib import Path
from typing import NamedTuple

import common
import postprocess
import probe_checks
import probes
import run
import settle
from report_grammar import CHANGELOG_REF_RE, FILES_QUOTES, LINE_REF_RE, VERIFY_QUOTES, report_lines, split_row

# V1, V7, V8 (Pre-registration)
VERIFIER = 'cc-guide-verifier'
MODEL = 'claude-sonnet-5-5'
ADVISOR_MODEL = 'claude-opus-5-5'
AGENT_KEYS = frozenset({'description', 'subagent_type', 'prompt', 'model'})
AGENT_MODEL = 'sonnet'
LAUNCH_NOTICE = 'Async agent launched'  # a background Agent call's result, not the report
HANDBACK = 'SubagentHandback'
# V2: the fenced tools, and the two names of /private/tmp
FENCED_TOOLS = ('Read', 'Grep', 'Glob')
PRIVATE_TMP = '/private/tmp'
TMP_ALIASES = ('/tmp', '/System/Volumes/Data/private/tmp')
TOOL_RESULTS = 'tool-results'  # the rep's own session folder that V2 counts as inside (plan 45's ruling 6)
# the sheet
AUDIT_FIXTURE = 'audit-changed'  # every audit rep settles against it, of either arm (DF15)
DISCARDS = ('unparseable: ', 'quote not found, discarded: ', 'no proposed wording, discarded: ')
STEPS = 'then, in this order'  # settle's closing commands start here
FILES_HOLD = 'held, not cited:'
FOLDER_TOKEN = '<packet copy>'
CHANGELOG_LINES = (1288, 1702, 224)  # the bullets behind P11, P8 and P7
DENIED = 'deniedModels'
README_FILE = 'hooks/README.md'
README_LINES = (85, 93)
FILE_SPAN_RE = re.compile(r'(.+):(\d+)(?:-(\d+))?')
VOLUME_RE = re.compile(r'report: \d+ (?:confirmed|consistent), (\d+) (?:correction|contradiction)\(s\)')
# stop and unblind (Decision rules; plan 45's DF7, DF8)
GATES = {'A': ('audit',), 'F': ('readme', 'precision')}
GATE_ROLES = ('counted', 'spare')
STOP_COUNT = 2
A_HITS_MIN = 4
A_CONTROL_P11_MAX = 1
DF7_MARGIN = 3
UNSUPPORTED_MAX = 2
DF8_SLACK = 1
REACH_MIN = 2
RETENTION = ('P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P9', 'P13', 'P14')
SECONDARY = ('P7', 'P10', 'P12')
HIT_LABELS = tuple(f'P{n}' for n in range(1, 15) if n not in (8, 11))
BLOCKING = ('V1', 'V2', 'V4', 'V5', 'V6', 'V7', 'V8')  # a void or pending one refuses a valid verdict (not V3)
REQUIRED = {'audit': ('P11', 'P8', 'hits', 'unsupported'), 'readme': ('readme89', 'unsupported'),
            'precision': ('reach', 'keymiss', 'unsupported')}
VERDICT_RE = re.compile(r'(?:[-*] +)?(r\d{3,})\b(.*)')
NAME_RE = re.compile(r'[A-Za-z0-9][A-Za-z0-9-]*')
USAGE = 'usage: grade.py <batch> | stop <batch> | unblind A|F'


class Refusal(Exception):
    '''A stop or unblind this script declines; its message names rep ids only.'''


class GradeError(Exception):
    '''A rep that cannot be graded; its message names the rep id only.'''


class Check(NamedTuple):
    status: str  # ok, void, pending, or hits (V3: trace each by hand)
    detail: str = ''

    def line(self, name: str) -> str:
        return f'{name}: {self.status}' + (f': {self.detail}' if self.detail else '')


def found(reasons: list[str]) -> Check:
    return Check('void', '; '.join(dict.fromkeys(reasons))) if reasons else Check('ok')


# --- records --------------------------------------------------------------------------------------------------


def content(record: dict) -> list[dict]:
    body = (record.get('message') or {}).get('content')
    return [b for b in body if isinstance(b, dict)] if isinstance(body, list) else []


def tool_uses(records: list[dict]) -> list[dict]:
    return [b for r in records if r.get('type') == 'assistant' for b in content(r) if b.get('type') == 'tool_use']


def tool_results(records: list[dict]) -> dict[str, tuple[str, bool]]:
    '''Each tool result's text and whether it is an error (a refusal is one), by tool_use_id.'''
    return {b.get('tool_use_id', ''): (probe_checks.result_body(b), bool(b.get('is_error')))
            for r in records if r.get('type') == 'user' for b in content(r) if b.get('type') == 'tool_result'}


def attachments(records: list[dict], kind: str) -> list[dict]:
    return [r['attachment'] for r in records if r.get('type') == 'attachment'
            and isinstance(r.get('attachment'), dict) and r['attachment'].get('type') == kind]


def main_calls(events: list[dict]) -> list[dict]:
    '''The main session's tool calls: no forwarded subagent message, no server tool.'''
    return [b for e in events if e.get('type') == 'assistant' and not e.get('parent_tool_use_id')
            for b in content(e) if b.get('type') == 'tool_use']


# --- V1 to V8 -------------------------------------------------------------------------------------------------


def check_v1(events: list[dict], verifiers: int, prompt: str, extra: tuple[str, ...] = ()) -> Check:
    '''One Agent call and no other main-session tool call; the call names the
    verifier, passes the exact dispatch, model `sonnet` if any, and no other
    parameter but those the pilot ruled in; one verifier transcript.'''
    calls = main_calls(events)
    agents = [c for c in calls if c.get('name') in probe_checks.DISPATCH_TOOLS]
    reasons = [f"a main-session {c.get('name')} call" for c in calls if c not in agents]
    if len(agents) != 1:
        reasons.append(f'{len(agents)} Agent calls')
    for call in agents:
        inp = call.get('input') or {}
        if inp.get('subagent_type') != VERIFIER:
            reasons.append(f"subagent_type {inp.get('subagent_type')!r}")
        if inp.get('prompt') != prompt:
            reasons.append('the dispatch prompt differs')
        if 'model' in inp and inp['model'] != AGENT_MODEL:
            reasons.append(f"model {inp['model']!r}")
        more = sorted(set(inp) - AGENT_KEYS - set(extra))
        if more:
            reasons.append(f"Agent parameters: {', '.join(more)}")
    if verifiers != 1:
        reasons.append(f'{verifiers} verifier transcripts')
    return found(reasons)


def resolve(path: str, root: str) -> str:
    '''A tool path as the fence sees it: `~` expanded, a relative path taken
    from the rep's work folder, symlinks followed, and /tmp and
    /System/Volumes/Data/private/tmp both read as /private/tmp.'''
    if path == '~' or path.startswith('~/'):
        path = os.environ['HOME'] + path[1:]
    real = os.path.realpath(os.path.join(root, path))
    for alias in TMP_ALIASES:
        if real == alias or real.startswith(alias + '/'):
            return PRIVATE_TMP + real[len(alias):]
    return real


def outside(path: str, root: str, inside: tuple[str, ...] = ()) -> bool:
    '''Whether a tool path falls outside the rep's work folder and outside
    each folder of `inside`. Both sides are resolved first, so a `..` that
    leaves a folder leaves it.'''
    if not path:
        return False
    p = resolve(path, root)
    return not any(p == f or p.startswith(f + '/') for f in (resolve(folder, root) for folder in (root, *inside)))


def paths_used(use: dict) -> list[str]:
    '''The paths a Read, Grep or Glob call names, with the fixed start of a
    Glob pattern that opens at /, ~ or ..'''
    inp = use.get('input') or {}
    if use.get('name') == 'Read':
        return [str(inp.get('file_path') or '')]
    out = [str(inp['path'])] if inp.get('path') else []
    pattern = str(inp.get('pattern') or '')
    if use.get('name') == 'Glob' and pattern.startswith(('/', '~', '..')):
        out.append(re.split(r'[*?\[{]', pattern)[0])
    return out


def listed_tokens(text: str) -> list[str]:
    '''The paths a Grep or Glob result lists that could leave the folder: each
    line, up to its first colon, that starts with /, ~ or .., or holds /../.
    Lines end at newlines only: a matched line's own text may hold a form
    feed, U+2028 or U+0085, and none of those starts a listed path.'''
    tokens = (line.split(':', 1)[0].strip() for line in text.split('\n'))
    return [t for t in tokens if t.startswith(('/', '~', '..')) or '/../' in t]


def check_v2(records: list[dict], root: str, inside: tuple[str, ...] = ()) -> tuple[Check, list[str]]:
    '''V2: each verifier Read, Grep or Glob that named a path outside the work
    folder and returned, or whose result listed one; and, logged only, each
    such call the fence refused. `inside` holds the rep's own session
    tool-results folder (plan 45's ruling 6), which counts as inside.'''
    results = tool_results(records)
    void, refused = [], []
    for use in tool_uses(records):
        name = use.get('name')
        if name not in FENCED_TOOLS:
            continue
        text, error = results.get(use.get('id', ''), ('', False))
        for path in paths_used(use):
            if outside(path, root, inside):
                (refused if error else void).append(f'{name} {path}')
        if name != 'Read' and not error:
            void += [f'{name} result lists {t}' for t in listed_tokens(text) if outside(t, root, inside)]
    return found(void), refused


def own_tool_results(project: Path, session: str | None) -> tuple[str, ...]:
    '''The rep's own session tool-results folder, as the rep saw it:
    $HOME/.claude/projects/<slug>/<session>/tool-results, for each slug whose
    folder in the rep's results holds <session>.jsonl, the session's own
    transcript. Another session, another slug, or another folder of the
    session (subagents/, the transcript itself) is not in it.'''
    if not session:
        return ()
    projects = Path(os.environ['HOME']) / '.claude' / 'projects'
    slugs = sorted({p.parent.name for p in project.glob(f'*/{session}.jsonl')})
    return tuple(str(projects / slug / session / TOOL_RESULTS) for slug in slugs)


def injected_hits(records: list[dict]) -> list[str]:
    '''V3's screen: each marker in an attachment or a system record. A
    prompt snapshot is screened but for its first part, the contract, which
    V5 checks.'''
    hits = []
    for r in records:
        if r.get('type') == 'attachment':
            att = r['attachment'] if isinstance(r.get('attachment'), dict) else {}
            if att.get('type') == 'prompt_snapshot':
                parts = att.get('systemPrompt') if isinstance(att.get('systemPrompt'), list) else []
                text = json.dumps(att | {'systemPrompt': parts[1:]}, ensure_ascii=False)
            else:
                text = json.dumps({'attachment': att, 'rendered': r.get('rendered')}, ensure_ascii=False)
            where = f"attachment {att.get('type')}"
        elif r.get('type') == 'system':
            where, text = 'system record', json.dumps(r, ensure_ascii=False)
        else:
            continue
        hits += [f'{where}: {m}' for m in common.MARKERS if m in text]
    return sorted(set(hits))


def check_v3(records: list[dict]) -> Check:
    hits = injected_hits(records)
    return Check('hits', '; '.join(hits) + ' (trace each by hand)') if hits else Check('ok')


def check_v4(records: list[dict]) -> Check:
    reasons = ['an instructions attachment'] if attachments(records, 'instructions') else []
    contexts = [json.dumps({'attachment': r['attachment'], 'rendered': r.get('rendered')}) for r in records
                if r.get('type') == 'attachment' and isinstance(r.get('attachment'), dict)
                and r['attachment'].get('type') == 'session_context']
    if any('gitStatus' in text for text in contexts):
        reasons.append('a session_context that holds gitStatus')
    return found(reasons)


def arm_body(text: str) -> str:
    '''An agent file's body, as Claude Code puts it in the system prompt:
    the text after the frontmatter, stripped.'''
    if text.startswith('---\n'):
        end = text.find('\n---\n', 3)
        if end >= 0:
            text = text[end + len('\n---\n'):]
    return text.strip()


def check_v5(records: list[dict], body: str) -> Check:
    snapshots = attachments(records, 'prompt_snapshot')
    if not snapshots:
        return found(['no prompt snapshot'])
    firsts = [(s.get('systemPrompt') or [None])[0] if isinstance(s.get('systemPrompt'), list) else None
              for s in snapshots]
    bad = sum(1 for first in firsts if first != body)
    return found([f"{bad} of {len(snapshots)} prompt snapshot(s) open with a part that is not the arm's body"]
                 if bad else [])


def check_v6(events: list[dict] | None, result: dict | None, status: dict | None, folder: Path,
             report: str | None, bad_lines: int = 0) -> Check:
    '''V6: the run failed or no report arrived, a verifier transcript line
    does not parse, or the rep's files still hold credential_expires_at.'''
    reasons = [] if events is not None else ['the stream does not parse']
    if bad_lines:
        reasons.append(f'{bad_lines} transcript line(s) do not parse')
    results = [e for e in events or [] if e.get('type') == 'result']
    if result is not None and result not in results:
        results.append(result)
    if not results:
        reasons.append('no result record')
    for r in results:
        stats = r.get('subagent_stats') if isinstance(r.get('subagent_stats'), dict) else {}
        refused = stats.get('refused') if isinstance(stats.get('refused'), dict) else {}
        killed = stats.get('killed') if isinstance(stats.get('killed'), dict) else {}
        if r.get('is_error'):
            reasons.append('a result is an error')
        if ('budget' in str(r.get('subtype') or '') or 'budget' in str(r.get('terminal_reason') or '')
                or count_of(refused.get('budget')) > 0):
            reasons.append('a budget stop')
        if count_of(stats.get('failed')) > 0 or sum(count_of(v) for v in killed.values()) > 0:
            reasons.append('a subagent failed or was killed')
    if status is None:
        reasons.append('no status.json')
    else:
        stopped = bool(status.get('interrupted') or status.get('timed_out'))
        reasons += ['interrupted'] if status.get('interrupted') else []
        reasons += ['timed out'] if status.get('timed_out') else []
        if status.get('exit') is None and not stopped:
            reasons.append('no exit code')
        elif status.get('exit') not in (None, 0):
            reasons.append(f"exit {status.get('exit')}")
        if status.get('strip_ok') is False:
            reasons.append('credential_expires_at survived the strip')
    left = run.leftovers(folder) if folder.is_dir() else []
    if left:
        reasons.append(f'credential_expires_at remains in {len(left)} file(s)')
    if report is None:
        reasons.append('no report: neither a finished Agent result nor a handback')
    return found(reasons)


def count_of(value) -> int:
    '''A subagent_stats count; `true` counts as one, since it says the thing happened.'''
    return int(value) if isinstance(value, int) else 0


def check_v7(records: list[dict], pilot: dict | None, is_pilot: bool, served: list[dict] | None = None) -> Check:
    '''V7: every verifier record on MODEL, at the pilot's effort and version.
    `served` is probes.read_transcripts' model and effort per record; the
    records give the version. The pilot itself sets the effort and version,
    so for it the check needs one of each.'''
    assistant = [r for r in records if r.get('type') == 'assistant']
    if not assistant:
        return found(['no assistant record'])
    if not served:
        served = [{'model': (r.get('message') or {}).get('model'), 'effort': r.get('effort')} for r in assistant]
    models = sorted({str(s.get('model')) for s in served} - {MODEL})
    efforts = sorted({str(s.get('effort')) for s in served})
    versions = sorted({str(r.get('version')) for r in assistant})
    reasons = [f"model {', '.join(models)}"] if models else []
    if is_pilot:
        if len(efforts) != 1 or len(versions) != 1:
            reasons.append(f"effort or version varies: {', '.join(efforts)}; {', '.join(versions)}")
        return found(reasons) if reasons else Check('ok', f'effort {efforts[0]}, version {versions[0]}')
    if reasons:
        return found(reasons)
    if not pilot or not {'effort', 'version'} <= pilot.keys():
        return Check('pending', 'pilot.json gives no effort and version yet')
    for kind, seen in (('effort', efforts), ('version', versions)):
        other = [value for value in seen if value != str(pilot[kind])]
        if other:
            reasons.append(f"{kind} {', '.join(other)} where the pilot had {pilot[kind]}")
    return found(reasons)


def check_v8(records: list[dict], pilot: dict | None) -> Check:
    '''V8: the verifier's advisor attachments match the production comparison
    the pilot recorded: present, available and on ADVISOR_MODEL, or absent.'''
    if not pilot or 'advisor' not in pilot:
        return Check('pending', 'pilot.json gives no production advisor fact yet')
    advisors = attachments(records, 'advisor_tool')
    if pilot['advisor']:
        if not advisors:
            return found(['no advisor attachment, where production had one'])
        if any(not a.get('available') or a.get('model') != ADVISOR_MODEL for a in advisors):
            return found([f'an advisor attachment is unavailable or not {ADVISOR_MODEL}'])
    elif advisors:
        return found(['an advisor attachment, where production had none'])
    return Check('ok')


def report_of(events: list[dict] | None, records: list[dict]) -> str | None:
    '''The verifier's report: the main session's finished Agent result that is
    no launch notice and no error, else the verifier's last handback.'''
    events = events or []
    for uid, kind in probe_checks.dispatches(events).items():
        text = probe_checks.tool_result_text(events, uid) if kind == VERIFIER else None
        if (text and text.strip() and not any(probe_checks.tool_result_errors(events, [uid]))
                and not text.lstrip().startswith(LAUNCH_NOTICE)):
            return text
    handbacks = [(u.get('input') or {}).get('message') for u in tool_uses(records) if u.get('name') == HANDBACK]
    last = handbacks[-1] if handbacks else None
    return last if isinstance(last, str) and last.strip() else None


# --- a rep's files --------------------------------------------------------------------------------------------


class Evidence(NamedTuple):
    events: list[dict] | None  # the stream, or None when it does not parse or is missing
    result: dict | None
    status: dict | None
    main: list[dict]  # the main session's transcript
    agents: list[tuple[str, list[dict]]]  # each subagent transcript, with its agent type
    served: list[dict] | None  # probes.read_transcripts' model and effort for the verifier
    inside: tuple[str, ...]  # the rep's own session tool-results folder, which V2 counts as inside
    bad_lines: int  # the verifier transcripts' lines that do not parse (V6)


def results_dir(rid: str) -> Path:
    return common.k_dir() / 'results' / rid


def read_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    obj = postprocess.parsed(path.read_text(encoding='utf-8', errors='replace'))
    return obj if isinstance(obj, dict) else None


def load_jsonl(path: Path) -> tuple[list[dict], int]:
    '''A transcript's records, and the count of its lines that do not parse:
    not strict UTF-8, not JSON, or JSON that is no object. A blank line is
    not counted. It splits at newlines only: Claude Code leaves U+2028,
    U+2029 and U+0085 raw inside JSON strings, and splitlines() would cut a
    record there.'''
    records, bad = [], 0
    for raw in path.read_bytes().split(b'\n'):
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError:
            bad += 1
            continue
        if not text.strip():
            continue
        obj = postprocess.parsed(text)
        if isinstance(obj, dict):
            records.append(obj)
        else:
            bad += 1
    return records, bad


def evidence(rid: str) -> Evidence:
    folder = results_dir(rid)
    stream = folder / 'stream.jsonl'
    events = probe_checks.parse_stream(stream.read_text(encoding='utf-8', errors='replace')) if stream.is_file() else None
    session = next((e.get('session_id') for e in events or [] if probe_checks.is_init(e)), None)
    if not (isinstance(session, str) and run.SESSION_RE.fullmatch(session)):
        session = None
    project = folder / 'project'
    main, agents, served, bad = [], [], None, 0
    if session:
        for path in sorted(project.glob(f'*/{session}.jsonl')):
            main += load_jsonl(path)[0]
        for meta in sorted(project.glob(f'*/{session}/subagents/agent-*.meta.json')):
            lines = meta.with_name(meta.name.removesuffix('.meta.json') + '.jsonl')
            kind = str((read_json(meta) or {}).get('agentType'))
            recs, n = load_jsonl(lines) if lines.is_file() else ([], 0)
            agents.append((kind, recs))
            bad += n if kind == VERIFIER else 0
        try:
            served = probes.read_transcripts(project, session).get(VERIFIER) or None
        except Exception:  # a line that is no JSON object, which V6 counts; V7 then reads the records
            served = None
    return Evidence(events, read_json(folder / 'result.json'), read_json(folder / 'status.json'), main, agents,
                    served, own_tool_results(project, session), bad)


def read_bodies() -> dict[str, str]:
    '''Every arm file's body, read before any rep is graded, so a missing or
    unreadable arm file refuses the whole batch and grades no rep. The
    refusal names no arm and no rep.'''
    try:
        return {arm: arm_body((common.k_dir() / 'arms' / f'{arm}.md').read_text(encoding='utf-8'))
                for arm in common.ARMS}
    except (OSError, UnicodeDecodeError):
        raise Refusal('an arm file is missing or unreadable') from None


def money(cost) -> str:
    return f'${cost:.2f}' if isinstance(cost, int | float) and not isinstance(cost, bool) else 'none'


def duration(seconds) -> str:
    return f'{seconds:.0f} s' if isinstance(seconds, int | float) and not isinstance(seconds, bool) else 'none'


# --- settle and the report's rows -----------------------------------------------------------------------------


class Row(NamedTuple):
    line: str
    kind: str  # A, B, C, F, or ? for any other line
    n: int  # A: the guide line; B: the changelog line; F: the first file line
    last: int  # F: the last file line
    file: str  # F: the file
    section: str  # A: the guide section of its line; F: the cited section
    verdict: str
    fate: str  # kept, unparseable, quote not found, or no proposed wording


def settled(rid: str, packet: str, report: str) -> tuple[list[str], list[str], settle.Packet]:
    '''Settle the report on a fresh copy of the packet: the lines the sheet
    shows, all of settle's lines, and the packet as settle read it.'''
    src = common.k_dir() / 'fixtures' / (AUDIT_FIXTURE if packet == 'audit' else packet)
    if not src.is_dir():
        raise GradeError(f'{rid}: its packet copy is missing')
    scratch = common.k_dir() / 'settle' / rid / 'packet'
    shutil.rmtree(scratch.parent, ignore_errors=True)
    shutil.copytree(src, scratch, ignore=run.skip_top(src))
    (scratch / settle.REPORT).write_text(report, encoding='utf-8')
    if packet == 'audit':
        index_path = scratch / settle.INDEX
        index = json.loads(index_path.read_text(encoding='utf-8'))
        docs = str(common.docs_fixture())
        index['docs'] = docs
        index['quotes']['docs'] = [docs]
        index_path.write_text(json.dumps(index, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    lines = settle.settle(scratch).lines
    shown = []
    for line in lines:
        if line.startswith(STEPS):
            break
        if not line.startswith(FILES_HOLD):
            shown.append(line.replace(str(scratch), FOLDER_TOKEN))
    return shown, lines, settle.read_packet(scratch)


def fate(line: str, lines: list[str]) -> str:
    for prefix in DISCARDS:
        if f'  {prefix}{line}' in lines:
            return prefix.split(',')[0].rstrip(': ')
    return 'kept'


def rows(report: str, lines: list[str], p: settle.Packet) -> list[Row]:
    '''Each report line that may be a row, read as settle reads it.'''
    mode, sections = p.index['mode'], p.index.get('sections', [])

    def files_fit(rest: list[str]) -> bool:
        return rest[0] in sections and rest[2].strip().lower() in settle.FILES_VERDICTS

    out = []
    for line in report_lines(report):
        first = (split_row(line, 2) or [''])[0]
        kind, n, last, file, section, verdict = '?', 0, 0, '', '', ''
        if mode == 'audit' and first in ('B', 'C'):
            kind = first
            row = split_row(line, 4) if first == 'B' else None
            if row and CHANGELOG_REF_RE.fullmatch(row[3]):
                n = int(row[3].rpartition(':')[2])
        elif mode == 'audit' and (m := LINE_REF_RE.fullmatch(first)):
            row = split_row(line, 6, VERIFY_QUOTES, settle.review_fits)
            kind, n = 'A', int(m.group(1))
            verdict = settle.review_verdict(row[2]) if row else ''
            section = settle.section_at(p, n) or 'no section'
        elif mode == 'files' and (m := FILE_SPAN_RE.fullmatch(first)):
            row = split_row(line, 5, FILES_QUOTES, files_fit)
            kind, file, n, last = 'F', m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
            if row:
                section, verdict = row[2], row[4].strip().lower()
        out.append(Row(line, kind, n, last if kind == 'F' else n, file, section, verdict, fate(line, lines)))
    return out


def tag(r: Row) -> str:
    if r.kind == 'A':
        return f'A L{r.n} {r.section} {r.verdict or "-"} {r.fate}'
    if r.kind == 'F':
        return f'F {r.verdict or "-"} {r.fate}'
    return f'{r.kind} {r.fate}'


def indented(items: list[str]) -> list[str]:
    return [f'  {item}' for item in items] or ['  none']


def audit_lines(found_rows: list[Row], lines: list[str]) -> tuple[list[str], dict]:
    b_rows = [r for r in found_rows if r.kind == 'B']
    kept_b = sum(1 for r in b_rows if r.fate == 'kept')
    listed = next((line for line in lines if line.startswith('listed items: ')), None)
    candidates = [r for r in found_rows if r.fate == 'kept'
                  and (r.kind == 'C' or r.kind == 'A' and r.verdict in settle.CORRECTIONS)]
    out = ['B rows on changelog.md:1288, :1702 or :224:']
    out += indented([f'[{tag(r)}] {r.line}' for r in b_rows if r.n in CHANGELOG_LINES])
    out += ['rows naming deniedModels:'] + indented([f'[{tag(r)}] {r.line}' for r in found_rows if DENIED in r.line])
    out += ['kept corrections and C rows (P1 to P14 candidates):']
    out += indented([f'[{tag(r)}] {r.line}' for r in candidates])
    out += [listed or 'listed items: none listed', f'B rows: {kept_b} kept, {len(b_rows) - kept_b} unparseable']
    return out, {'b_rows': kept_b, 'b_unparseable': len(b_rows) - kept_b, 'listed': listed}


def read_key() -> list[tuple[str, int, int]] | None:
    '''$K/precision-key.tsv's entries, (file, first line, last line), or None
    without the file. Blank lines and `#` lines are skipped.'''
    path = common.k_dir() / 'precision-key.tsv'
    if not path.is_file():
        return None
    entries = []
    for n, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), start=1):
        if not raw.strip() or raw.lstrip().startswith('#'):
            continue
        m = FILE_SPAN_RE.fullmatch(raw.split('\t', 1)[0].strip())
        if m is None:
            raise GradeError(f'precision-key.tsv line {n} has no file:line in its first column')
        entries.append((m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))))
    return entries


def files_lines(found_rows: list[Row], p: settle.Packet, packet: str) -> list[str]:
    covered = set(p.index.get('covered') or {})
    key = read_key() if packet == 'precision' else None

    def note(r: Row) -> str:
        span = str(r.n) if r.last == r.n else f'{r.n}-{r.last}'
        parts = [f'F {r.file}:{span} {r.section}, contradicts'] + (['covered file'] if r.file in covered else [])
        if packet == 'precision':
            on = key is not None and any(f == r.file and a <= r.last and r.n <= b for f, a, b in key)
            parts.append('key missing' if key is None else 'on key' if on else 'not on key')
        return ', '.join(parts)

    kept = [r for r in found_rows if r.kind == 'F' and r.fate == 'kept']
    reach = [r for r in kept if r.file in covered]
    near = [r for r in found_rows if r.kind == 'F' and r.file == README_FILE
            and r.n <= README_LINES[1] and r.last >= README_LINES[0]]
    out = ['kept contradicts rows:'] + indented([f'[{note(r)}] {r.line}' for r in kept if r.verdict == 'contradicts'])
    out += [f"a kept row names a covered file: {'yes' if reach else 'no'}"] + [f'  [{tag(r)}] {r.line}' for r in reach]
    out += ['rows on hooks/README.md lines 85 to 93:'] + indented([f'[{tag(r)}] {r.line}' for r in near])
    return out


# --- sheets ---------------------------------------------------------------------------------------------------


def rep_sheet(rep: dict, bodies: dict[str, str]) -> tuple[list[str], dict]:
    '''A counted, spare or pilot rep's sheet and its measures.'''
    rid, packet = rep['rid'], rep['packet']
    ev = evidence(rid)
    records = [r for kind, recs in ev.agents if kind == VERIFIER for r in recs]
    verifiers = sum(1 for kind, _ in ev.agents if kind == VERIFIER)
    pilot = read_json(common.k_dir() / 'pilot.json')
    body = bodies[rep['arm']]
    mode = common.PACKETS[packet]['mode']
    prompt = common.DISPATCH.format(mode=mode, packet=common.R / rid / 'work' / 'packet')
    extra = tuple(map(str, (pilot or {}).get('agent_params') or ()))
    report = report_of(ev.events, records)
    v2, refused = check_v2(records, str(common.R / rid / 'work'), ev.inside)
    checks = {'V1': check_v1(ev.events or [], verifiers, prompt, extra), 'V2': v2, 'V3': check_v3(records),
              'V4': check_v4(records), 'V5': check_v5(records, body),
              'V6': check_v6(ev.events, ev.result, ev.status, results_dir(rid), report, ev.bad_lines),
              'V7': check_v7(records, pilot, rep['role'] == 'pilot', ev.served), 'V8': check_v8(records, pilot)}
    void = [name for name, c in checks.items() if c.status == 'void']
    pending = [name for name, c in checks.items() if c.status == 'pending']
    cost, seconds = (ev.result or {}).get('total_cost_usd'), (ev.status or {}).get('seconds')
    out = [f"== {rid} {packet} {rep['role']}", *(c.line(name) for name, c in checks.items()),
           'V2 refused (logged, not void): ' + ('; '.join(refused) or 'none'),
           'V3 main session (recorded only): ' + ('; '.join(injected_hits(ev.main)) or 'none'),
           'void: ' + (', '.join(void) or 'none'), 'pending: ' + (', '.join(pending) or 'none'),
           f'cost: {money(cost)}', f'duration: {duration(seconds)}']
    measures = {'rid': rid, 'packet': packet, 'role': rep['role'], 'void': void, 'pending': pending, 'cost': cost,
                'seconds': seconds, 'volume': None, 'b_rows': None, 'b_unparseable': None, 'listed': None}
    if report is None:
        return out + ['report: none', 'settle:', '  no report, so nothing to settle'], measures
    (common.k_dir() / 'reports').mkdir(parents=True, exist_ok=True)
    (common.k_dir() / 'reports' / f'{rid}.md').write_text(report, encoding='utf-8')
    shown, lines, p = settled(rid, packet, report)
    out += [f'report: reports/{rid}.md', 'settle:'] + [f'  {line}' for line in shown]
    volume = next((VOLUME_RE.match(line) for line in lines if VOLUME_RE.match(line)), None)
    measures['volume'] = int(volume.group(1)) if volume else None
    found_rows = rows(report, lines, p)
    if mode == 'audit':
        more, counts = audit_lines(found_rows, lines)
        return out + more, measures | counts
    return out + files_lines(found_rows, p, packet), measures


def target(use: dict) -> str:
    inp = use.get('input') or {}
    if use.get('name') == 'Bash':
        return str(inp.get('command') or '')
    if use.get('name') in probe_checks.DISPATCH_TOOLS:
        return str(inp.get('subagent_type') or '')
    return ' '.join(paths_used(use)) or str(inp.get('pattern') or '')


def probe_sheet(rep: dict) -> tuple[list[str], dict]:
    '''The probe's short sheet: each call of the main session and of every
    subagent, refused or returned, and the files that hold the canary token.'''
    rid = rep['rid']
    ev = evidence(rid)
    out = [f'== {rid} probe', f"cost: {money((ev.result or {}).get('total_cost_usd'))}",
           f"duration: {duration((ev.status or {}).get('seconds'))}", 'tool calls:']
    for who, records, uses in [('main', ev.events or [], main_calls(ev.events or []))] + [
            (kind, recs, tool_uses(recs)) for kind, recs in ev.agents]:
        results = tool_results(records)
        for use in uses:
            error = results.get(use.get('id', ''), ('', False))[1]
            out.append(f"  {who} {use.get('name')} {target(use)}: {'refused' if error else 'returned'}")
    canary = common.k_dir() / 'canary.txt'
    token = canary.read_text(encoding='utf-8').strip().encode() if canary.is_file() else b''
    folder = results_dir(rid)
    seen = [str(p.relative_to(folder)) for p in sorted(folder.rglob('*')) if p.is_file() and token in p.read_bytes()]
    out.append('canary token seen in: ' + (', '.join(seen) or 'none') if token else 'canary token: no canary.txt')
    return out, {'rid': rid, 'packet': rep['packet'], 'role': rep['role'], 'void': [], 'pending': []}


def write_sheet(rep: dict, bodies: dict[str, str]) -> dict:
    lines, measures = probe_sheet(rep) if rep['packet'] == common.PROBE else rep_sheet(rep, bodies)
    sheets = common.k_dir() / 'sheets'
    sheets.mkdir(parents=True, exist_ok=True)
    (sheets / f"{rep['rid']}.txt").write_text('\n'.join(lines) + '\n', encoding='utf-8')
    (sheets / f"{rep['rid']}.json").write_text(json.dumps(measures, indent=1) + '\n', encoding='utf-8')
    return measures


# --- plan, batches and verdicts -------------------------------------------------------------------------------


def load_plan() -> dict[str, dict]:
    path = common.k_dir() / 'plan.json'
    if not path.is_file():
        raise Refusal('no plan.json; run build.py first')
    return {rep['rid']: rep for rep in json.loads(path.read_text(encoding='utf-8'))['reps']}


def batch_rids(batch: str) -> list[str]:
    path = common.k_dir() / 'batches' / f'{batch}.txt'
    if not NAME_RE.fullmatch(batch) or not path.is_file():
        raise Refusal(f'no batch {batch}; run build.py first')
    return [line.strip() for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def parse_verdict(words: list[str]) -> tuple[str, object] | None:
    match words:
        case ['valid' | 'void' as value]:
            return 'validity', value
        case ['P11' | 'P8' | 'readme89' | 'reach' as key, 'yes' | 'no' as value]:
            return key, value == 'yes'
        case ['unsupported' | 'keymiss' as key, number] if number.isdigit():
            return key, int(number)
        case ['hits', 'none']:
            return 'hits', frozenset()
        case ['hits', *labels] if labels and set(labels) <= set(HIT_LABELS) and len(set(labels)) == len(labels):
            return 'hits', frozenset(labels)
    return None


def read_verdicts() -> dict[str, dict]:
    '''$K/RESULTS.md's verdicts, by rep id. A line that starts with a rep id
    and is no verdict, or a verdict given twice, is refused by its line.'''
    path = common.k_dir() / 'RESULTS.md'
    out: dict[str, dict] = {}
    if not path.is_file():
        return out
    for n, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), start=1):
        m = VERDICT_RE.fullmatch(raw.strip())
        if m is None:
            continue
        verdict = parse_verdict(m.group(2).split())
        if verdict is None:
            raise Refusal(f'RESULTS.md line {n} is not a verdict')
        key, value = verdict
        mine = out.setdefault(m.group(1), {})
        if key in mine:
            raise Refusal(f'RESULTS.md line {n}: {m.group(1)} has its {key} verdict twice')
        mine[key] = value
    return out


def require_complete(reps: list[dict], verdicts: dict[str, dict]) -> None:
    '''Refuse, naming rep ids only, until every rep has its verdicts and a
    sheet with its measures file; a void rep needs neither. A valid verdict
    also needs a sheet whose V1, V2 and V4 to V8 are neither void nor
    pending: a check the grader decides overrules the hand. V3 stays a hand
    check, so its line never blocks.'''
    problems = []
    for rep in sorted(reps, key=lambda r: r['rid']):
        rid, mine = rep['rid'], verdicts.get(rep['rid'], {})
        sheets = common.k_dir() / 'sheets'
        measures = read_json(sheets / f'{rid}.json') if (sheets / f'{rid}.txt').is_file() else None
        if mine.get('validity') == 'void':
            continue
        if measures is None or not all(isinstance(measures.get(k), list) for k in ('void', 'pending')):
            problems.append(f'{rid} (no sheet)')
            continue
        missing = [key for key in ('validity', *REQUIRED[rep['packet']]) if key not in mine]
        if missing:
            problems.append(f"{rid} ({', '.join(missing)})")
        elif set(measures['void'] + measures['pending']) & set(BLOCKING):
            problems.append(f'{rid} (a valid verdict, but its sheet has a void or pending check)')
    if problems:
        raise Refusal('these reps are not ready: ' + '; '.join(problems))


def valid_by_arm(reps: list[dict], verdicts: dict[str, dict]) -> dict[str, list[dict]]:
    return {arm: [verdicts[r['rid']] for r in reps if r['arm'] == arm and verdicts[r['rid']]['validity'] == 'valid']
            for arm in common.ARMS}


def unspared(reps: list[dict], verdicts: dict[str, dict]) -> list[str]:
    '''The void reps that no valid spare replaces, directly or through a
    spare that is itself void, in id order.'''
    spares: dict[str, list[str]] = {}
    for r in reps:
        if r.get('replaces'):
            spares.setdefault(r['replaces'], []).append(r['rid'])

    def spared(rid: str, seen: frozenset) -> bool:
        return any(verdicts[s]['validity'] == 'valid' or (s not in seen and spared(s, seen | {s}))
                   for s in spares.get(rid, []))

    return sorted(r['rid'] for r in reps if verdicts[r['rid']]['validity'] == 'void'
                  and not spared(r['rid'], frozenset({r['rid']})))


def stop(batch: str) -> str:
    '''Gate A's first-wave stop rules, over the batch's valid reps.'''
    plan, rids = load_plan(), batch_rids(batch)
    reps = [plan[rid] for rid in rids if rid in plan]
    if not reps or len(reps) != len(rids) or any(r['packet'] != 'audit' or r['role'] not in GATE_ROLES for r in reps):
        raise Refusal(f'{batch}: stop reads a gate A batch, of counted and spare audit reps only')
    verdicts = read_verdicts()
    require_complete(reps, verdicts)
    control, changed = valid_by_arm(reps, verdicts).values()
    if min(len(control), len(changed)) < STOP_COUNT:
        # The first-wave rules need STOP_COUNT valid reps on each side. This
        # holds exactly when a void rep has no valid spare, so naming those
        # reps, in id order, shows nothing the sheets do not.
        named = unspared(reps, verdicts)
        raise Refusal(f"{batch}: these void reps have no valid spare yet: {', '.join(named)}" if named
                      else f'{batch}: too few valid reps for the first-wave rules')
    if sum(v['P11'] for v in control) >= STOP_COUNT:
        return 'stop: UNSETTLED'
    if sum(not v['P11'] for v in changed) >= STOP_COUNT or sum(not v['P8'] for v in changed) >= STOP_COUNT:
        return 'stop: FAIL'
    return 'continue'


# --- unblind --------------------------------------------------------------------------------------------------


def clause(name: str, arm: str, requirement: str, observed: str, met: bool | None) -> str:
    return f"{name} | {arm} | {requirement} | {observed} | {'-' if met is None else 'met' if met else 'not met'}"


def unblind_a(reps: list[dict], verdicts: dict[str, dict], measures: dict[str, dict]) -> list[str]:
    control_arm, changed_arm = common.ARMS
    goal = common.PACKETS['audit']['reps']
    valid = valid_by_arm(reps, verdicts)
    n = {arm: len(valid[arm]) for arm in common.ARMS}

    def count(arm: str, test) -> int:
        return sum(1 for v in valid[arm] if test(v))

    x11, x8 = count(changed_arm, lambda v: v['P11']), count(changed_arm, lambda v: v['P8'])
    c11, c8 = count(control_arm, lambda v: v['P11']), count(control_arm, lambda v: v['P8'])
    c_total = sum(v['unsupported'] for v in valid[control_arm])
    x_total = sum(v['unsupported'] for v in valid[changed_arm])
    x_max = max((v['unsupported'] for v in valid[changed_arm]), default=0)
    gated = [clause('P11', changed_arm, f'at least {A_HITS_MIN} of {goal} valid reps', f'{x11} of {n[changed_arm]}',
                    x11 >= A_HITS_MIN),
             clause('P8', changed_arm, f'at least {A_HITS_MIN} of {goal} valid reps', f'{x8} of {n[changed_arm]}',
                    x8 >= A_HITS_MIN),
             clause('P11', control_arm, f'at most {A_CONTROL_P11_MAX} of {goal} valid reps',
                    f'{c11} of {n[control_arm]}', c11 <= A_CONTROL_P11_MAX),
             clause('DF7 total', changed_arm, f"at most the control's {c_total} + {DF7_MARGIN}", str(x_total),
                    x_total <= c_total + DF7_MARGIN),
             clause('DF7 per rep', changed_arm, f'no rep above {UNSUPPORTED_MAX}', f'at most {x_max}',
                    x_max <= UNSUPPORTED_MAX)]
    for label in RETENTION:
        c, x = (count(arm, lambda v: label in v['hits']) for arm in common.ARMS)
        gated.append(clause(f'DF8 {label}', changed_arm, f"at least the control's {c} - {DF8_SLACK}", str(x),
                            x >= c - DF8_SLACK))
    reported = [clause('P8', control_arm, 'reported', f'{c8} of {n[control_arm]}', None),
                clause('DF7 total', control_arm, 'reported', str(c_total), None)]
    reported += [clause(label, arm, 'reported', f"{count(arm, lambda v: label in v['hits'])} of {n[arm]}", None)
                 for label in SECONDARY for arm in common.ARMS]
    out = ['Gate A (audit): rep, arm, validity'] + [
        f"{r['rid']} {r['arm']} {verdicts[r['rid']]['validity']}" for r in reps]
    out += ['clause | arm | requirement | observed | met'] + gated + reported
    out += ['per valid rep (reported):'] + [
        f"{r['rid']} {r['arm']}: B rows {m.get('b_rows', '?')} kept, {m.get('b_unparseable', '?')} unparseable; "
        f"{m.get('listed') or 'listed items: none listed'}; corrections {m.get('volume', '?')}"
        for r in reps if verdicts[r['rid']]['validity'] == 'valid' for m in [measures[r['rid']]]]
    out += volume_lines('corrections (DF21)', [(arm, [r for r in reps if r['arm'] == arm]) for arm in common.ARMS],
                        verdicts, measures)
    short = [f'{arm} {n[arm]} of {goal}' for arm in common.ARMS if n[arm] < goal]
    if not short:
        result = 'PASS' if not [line for line in gated if line.endswith('| not met')] else 'FAIL'
    elif c11 >= STOP_COUNT:
        result = f'UNSETTLED (first wave: the control meets P11 in {STOP_COUNT} valid reps)'
    elif min(n[control_arm], n[changed_arm]) >= STOP_COUNT and (n[changed_arm] - x11 >= STOP_COUNT
                                                                or n[changed_arm] - x8 >= STOP_COUNT):
        # The first-wave FAIL holds only in the state `stop` accepts: each arm
        # has STOP_COUNT valid reps. Short of that it is UNSETTLED (plan:171).
        result = f'FAIL (first wave: the changed arm misses P11 or P8 in {STOP_COUNT} valid reps)'
    else:
        result = f"UNSETTLED (too few valid reps: {', '.join(short)})"
    return out + [f'result: {result}']


def volume_lines(name: str, groups: list[tuple[str, list[dict]]], verdicts: dict[str, dict],
                 measures: dict[str, dict]) -> list[str]:
    '''DF21: each group's correction or contradiction counts over its valid reps, median and total.'''
    out = []
    for label, reps in groups:
        counts = [measures[r['rid']].get('volume') for r in reps if verdicts[r['rid']]['validity'] == 'valid']
        counts = [c for c in counts if isinstance(c, int)]
        median = f'{statistics.median(counts):g}' if counts else '-'
        out.append(f'{name} | {label} | median {median}, total {sum(counts)}')
    return out


def unblind_f(reps: list[dict], verdicts: dict[str, dict], measures: dict[str, dict]) -> list[str]:
    control_arm, changed_arm = common.ARMS
    by = {(packet, arm): [verdicts[r['rid']] for r in reps if (r['packet'], r['arm']) == (packet, arm)
                          and verdicts[r['rid']]['validity'] == 'valid']
          for packet in GATES['F'] for arm in common.ARMS}
    goal = {packet: common.PACKETS[packet]['reps'] for packet in GATES['F']}
    out = ['Gate F (files): rep, packet, arm, validity'] + [
        f"{r['rid']} {r['packet']} {r['arm']} {verdicts[r['rid']]['validity']}" for r in reps]
    out.append('clause | arm | requirement | observed | met')
    gated, reported = [], []
    for arm in common.ARMS:
        mine = arm == changed_arm
        readme, precision = by[('readme', arm)], by[('precision', arm)]
        on_89 = sum(1 for v in readme if v['readme89'])
        reach = sum(1 for v in precision if v['reach'])
        lines = [
            clause('readme89', arm, 'no valid readme rep keeps a contradicts row on hooks/README.md:89'
                   if mine else 'reported', f'{on_89} of {len(readme)}', on_89 == 0 if mine else None),
            *(clause(f'{packet} unsupported', arm, f'no rep above {UNSUPPORTED_MAX}' if mine else 'reported',
                     f"total {sum(v['unsupported'] for v in vs)}, at most "
                     f"{max((v['unsupported'] for v in vs), default=0)}",
                     max((v['unsupported'] for v in vs), default=0) <= UNSUPPORTED_MAX if mine else None)
              for packet, vs in (('readme', readme), ('precision', precision))),
            clause('reach', arm, f"at least {REACH_MIN} of {goal['precision']} valid precision reps"
                   if mine else 'reported', f'{reach} of {len(precision)}', reach >= REACH_MIN if mine else None),
            clause('keymiss', arm, 'reported', f"total {sum(v['keymiss'] for v in precision)}", None)]
        (gated if mine else reported).extend(lines)
    out += gated + reported
    out += volume_lines('contradictions (DF21)', [(f'{packet} {arm}', [r for r in reps if (r['packet'], r['arm'])
                                                                       == (packet, arm)])
                                                  for packet in GATES['F'] for arm in common.ARMS], verdicts, measures)
    short = [f'{packet} {arm} {len(by[(packet, arm)])} of {goal[packet]}' for packet in GATES['F']
             for arm in common.ARMS if len(by[(packet, arm)]) < goal[packet]]
    if short:
        result = f"UNSETTLED (too few valid reps: {', '.join(short)})"
    else:
        result = 'PASS' if not [line for line in gated if line.endswith('| not met')] else 'FAIL'
    return out + [f'result: {result}']


def unblind(gate: str) -> list[str]:
    '''The gate's tables, joined with plan.json, once every sheet has its verdicts.'''
    reps = sorted((r for r in load_plan().values() if r['packet'] in GATES[gate] and r['role'] in GATE_ROLES),
                  key=lambda r: r['rid'])
    if not reps:
        raise Refusal(f'gate {gate} has no reps yet')
    verdicts = read_verdicts()
    require_complete(reps, verdicts)
    measures = {r['rid']: read_json(common.k_dir() / 'sheets' / f"{r['rid']}.json") or {} for r in reps}
    return (unblind_a if gate == 'A' else unblind_f)(reps, verdicts, measures)


# --- the commands ---------------------------------------------------------------------------------------------


def grade_batch(batch: str) -> int:
    try:
        rids, plan = batch_rids(batch), load_plan()
    except Refusal as refusal:
        print(f'grade.py: {refusal}', file=sys.stderr)
        return 2
    bodies = read_bodies()  # a Refusal here grades no rep (main prints it, exit 1)
    code = 0
    for rid in rids:
        rep = plan.get(rid)
        if rep is None:
            print(f'grade.py: {rid}: not in plan.json', file=sys.stderr)
            code = 1
        elif not results_dir(rid).is_dir():
            print(f'{rid}: no results yet')
        else:
            try:
                measures = write_sheet(rep, bodies)
            except GradeError as error:
                print(f'grade.py: {error}', file=sys.stderr)
                code = 1
            except Exception as error:  # its message may name an arm's file
                print(f'grade.py: {rid}: not graded ({type(error).__name__})', file=sys.stderr)
                code = 1
            else:
                print(f"{rid}: sheets/{rid}.txt; void: {', '.join(measures['void']) or 'none'}; "
                      f"pending: {', '.join(measures['pending']) or 'none'}")
    return code


def main(argv: list[str]) -> int:
    try:
        match argv:
            case ['stop', batch]:
                print(stop(batch))
            case ['unblind', gate] if gate in GATES:
                print('\n'.join(unblind(gate)))
            case [batch] if batch not in ('stop', 'unblind'):
                return grade_batch(batch)
            case _:
                print(USAGE, file=sys.stderr)
                return 2
    except Refusal as refusal:
        print(f'grade.py: refused: {refusal}', file=sys.stderr)
        return 1
    except Exception as error:  # its message may name an arm's file
        print(f'grade.py: failed ({type(error).__name__})', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
