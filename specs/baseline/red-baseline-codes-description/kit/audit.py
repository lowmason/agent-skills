'''Audit plan 111's trigger reps: the stream check, the run, the listing, the quarantine and the VOID reasons.

Copy of plan 107's audit.py (specs/baseline/red-baseline-writing-skills-tests/kit/audit.py). Its changes:
- every rep is a trigger rep, at <prompt>/<arm>/<model>/rep<N> (one condition, so no condition folder);
- the path audit, the Glob limits, the Bash audit, the reference reads and the R3 tree check are cut. Plan 111
  registers no VOID reason for them: rule 2's deny list and read fence refuse those calls instead, and plan
  107's record showed that its path-audit VOID dropped reps that had loaded the skill;
- rule 4 reads the check that rep_tools.py summarize ran on the raw stream (summary.json's peer_check), since
  the saved stream no longer holds `origin`, and it checks the saved stream again;
- rules 3 and 5 are new, and the listing check names this repository's three codes skills.

Usage, from the repository root:
  uv run python <kit>/audit.py <rep-dir> ...
Each <rep-dir> is a rep<N>/ folder that run_trigger_reps.sh wrote, under <prompt>/<arm>/<model>/. A model
folder stands for each rep<N>/ in it. The saved stream is read from
CD_TRIGGER_SCRATCH/<prompt>/<arm>/<model>/rep<N>.jsonl (default ~/.cache/agent-skills/scratch/plan111/triggers).
For each rep it prints the stream counts, the run (exit, subtype, cost, turns), the init record's tools and listing, whether the rep
loaded classification-codes, and its VOID reasons or `VOID: none`.

The VOID reasons, as the write-up registers them:
- a kit error: no summary.json, a kit_error in it, no peer_check in it, no saved stream, a stream line that is
  not a JSON object, no result record, or a second one. A rep that cannot be read whole cannot show rules 3
  to 5 or its result;
- rule 3: `credential_expires_at` still in summary.json or in the saved stream;
- rule 4: an entry of summary.json's peer_check, or, in the saved stream, a `result_index` above 0 (or one that
  is not an integer) or an `origin` whose `kind` is `peer` (rep_tools.peer_check);
- rule 5: a Read, Grep or Glob call whose file_path or path (or a Glob pattern) names a file of
  cases.QUARANTINE, in any case, and whose tool result came back without an error. A refused call, or one
  with no result, read nothing;
- an error result: a result subtype other than success, or is_error true. The subtypes error_max_turns and
  error_max_budget_usd are a normal end for a trigger rep (plan 107's reading), not an error result;
- a listing (the init record's skills) that lacks a name of cases.REQUIRED_LISTING.
'''
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases  # noqa: E402
import rep_tools  # noqa: E402
import triggers  # noqa: E402

DEFAULT_SCRATCH = '.cache/agent-skills/scratch/plan111/triggers'
CROSS_SESSION_TOOLS = ('ListAgents', 'SendMessage', 'PushNotification', 'RemoteTrigger')
TRIGGER_TOOLS = ('Read', 'Glob', 'Grep', 'Skill')
SEARCH_TOOLS = ('Read', 'Grep', 'Glob')
BUDGET = 'error_max_budget_usd'
MAX_TURNS = 'error_max_turns'
NORMAL_ENDS = (BUDGET, MAX_TURNS)


def trigger_scratch() -> Path:
    return Path(os.environ.get('CD_TRIGGER_SCRATCH') or Path.home() / DEFAULT_SCRATCH)


def rep_layout(rep: Path) -> dict:
    '''A rep is <prompt>/<arm>/<model>/rep<N>.'''
    return {'prompt': rep.parent.parent.parent.name, 'arm': rep.parent.parent.name, 'model': rep.parent.name}


def stream_path(rep: Path) -> Path:
    where = rep_layout(rep)
    return trigger_scratch() / where['prompt'] / where['arm'] / where['model'] / f'{rep.name}.jsonl'


def stream_audit(path: Path) -> dict:
    '''The saved stream's line check, record counts, rule 4 check, tool calls, listing and first result record.'''
    found = {'missing': not path.is_file(), 'bad': [], 'records': 0, 'inits': 0, 'results': 0, 'peer_check': [],
             'cross_tools': [], 'other_tools': [], 'calls': [], 'result': None, 'listing': [], 'field_left': False}
    if found['missing']:
        return found
    data = path.read_bytes()
    records, bad = rep_tools.read_stream(data)
    inits = [r for r in records if r.get('type') == 'system' and r.get('subtype') == 'init']
    results = [r for r in records if r.get('type') == 'result']
    listed = {tool for r in inits if isinstance(r.get('tools'), list) for tool in r['tools'] if isinstance(tool, str)}
    found.update({
        'bad': bad, 'records': len(records), 'inits': len(inits), 'results': len(results),
        'peer_check': rep_tools.peer_check(records), 'field_left': rep_tools.FIELD.encode() in data,
        'cross_tools': [tool for tool in CROSS_SESSION_TOOLS if tool in listed],
        'other_tools': sorted(listed - set(TRIGGER_TOOLS)),
        'calls': rep_tools.read_records(records)['calls'], 'result': results[0] if results else None,
        'listing': triggers.listing(records),
    })
    return found


def quarantine_hits(calls: list[dict]) -> list[str]:
    '''Rule 5: each Read, Grep or Glob call that names a quarantined file and whose result came back clean.'''
    names = [name.lower() for name in cases.QUARANTINE]
    found = []
    for number, call in enumerate(calls, 1):
        if call.get('name') not in SEARCH_TOOLS or call.get('is_error') is not False:
            continue
        args = call.get('input') or {}
        keys = ('file_path', 'path', 'pattern') if call['name'] == 'Glob' else ('file_path', 'path')
        paths = [args[key].lower() for key in keys if isinstance(args.get(key), str)]
        if any(name in path for name in names for path in paths):
            found.append(f'call {number} {call["name"]} names a quarantined file')
    return found


def load_summary(rep: Path) -> dict | None:
    try:
        summary = json.loads((rep / 'summary.json').read_text())
    except (OSError, ValueError):
        return None
    return summary if isinstance(summary, dict) else None


def run_end_void(result: dict) -> str | None:
    '''Why a result record is an error result, or None. A turn or budget stop is a normal end.'''
    subtype = result.get('subtype')
    if subtype in NORMAL_ENDS:
        return None
    if subtype != 'success':
        return f'error result: subtype {subtype}'
    if result.get('is_error'):
        return 'error result: is_error true'
    return None


def audit_rep(rep: Path) -> dict:
    '''Everything audit.py prints for one rep, with its VOID reasons.'''
    where = rep_layout(rep)
    summary = load_summary(rep)
    stream = stream_audit(stream_path(rep))
    void = []
    if summary is None:
        void.append('kit error: no summary.json')
    elif 'kit_error' in summary:
        void.append(f'kit error: {summary["kit_error"]}')
    elif not isinstance(summary.get('peer_check'), list):
        void.append('kit error: no peer_check in summary.json')
    if stream['missing']:
        void.append('kit error: no saved stream')
    if stream['bad']:
        void.append(f'kit error: stream line(s) {", ".join(map(str, stream["bad"]))} not JSON')
    if not stream['missing'] and not stream['results']:
        void.append('kit error: no result record')
    if stream['results'] > 1:
        void.append('kit error: a second result record')
    if summary is not None and rep_tools.FIELD in (rep / 'summary.json').read_text():
        void.append(f'rule 3: {rep_tools.FIELD} left in summary.json')
    if stream['field_left']:
        void.append(f'rule 3: {rep_tools.FIELD} left in {rep.name}.jsonl')
    if summary is not None and isinstance(summary.get('peer_check'), list):
        void += [f'rule 4: {reason} (before the scrub)' for reason in summary['peer_check']]
    void += [f'rule 4: {reason}' for reason in stream['peer_check']]
    void += [f'rule 5: {hit}' for hit in quarantine_hits(stream['calls'])]
    if stream['results']:
        ended = run_end_void(stream['result'])
        if ended:
            void.append(ended)
    if not stream['missing']:
        lacking = [name for name in cases.REQUIRED_LISTING if name not in stream['listing']]
        if lacking:
            void.append(f'listing lacks {", ".join(lacking)}')
    return {'summary': summary or {}, 'stream': stream, 'void': void, 'where': where}


def void_reasons(rep: Path) -> list[str]:
    return audit_rep(rep)['void']


def show(rep: Path) -> None:
    found = audit_rep(rep)
    where, stream, summary = found['where'], found['stream'], found['summary']
    print(f'== {where["prompt"]} {where["arm"]} {where["model"]} {rep.name}')
    if stream['missing']:
        print(f'  stream: missing at {stream_path(rep)}')
    print(f'  stream: {stream["records"]} record(s), {len(stream["bad"])} line(s) not JSON, {stream["inits"]} init, '
          f'{stream["results"]} result')
    if stream['other_tools']:
        print(f'  init record lists tools beyond {", ".join(TRIGGER_TOOLS)}: {", ".join(stream["other_tools"])}')
    if stream['cross_tools']:
        print(f'  init record lists a cross-session tool: {", ".join(stream["cross_tools"])}')
    result = stream['result'] or {}
    print(f'  exit {summary.get("claude_exit")}, subtype {result.get("subtype")}, is_error {result.get("is_error")}, '
          f'cost {result.get("total_cost_usd")}, turns {result.get("num_turns")}, tool calls {len(stream["calls"])}')
    print(f'  listing: {", ".join(stream["listing"]) or "none"}')
    print(f'  loads {cases.SKILL}: {"yes" if triggers.is_load_in(stream["calls"]) else "no"}')
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
