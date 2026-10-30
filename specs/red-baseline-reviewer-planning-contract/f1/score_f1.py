'''Score one plan 73 F1 rep: hidden acceptance tests, plan-to-spec ratio, cost and isolation audit.

Usage, from the repository root:
  uv run --with pytest python <f1>/score_f1.py <scratch> <out-dir> <hidden-test-file>
Prints one JSON object and writes it to <out-dir>/score.json. `handled` maps each hidden test to
true when it passed. `cost` sums both sessions' total_cost_usd, and `execute_models` lists the
models the execution session's result record names. `audit_hits` lists every transcript line
that names a path outside the scratch repository that a run must not touch; read each one by
hand under the VOID rule. `audit_error` is set when the transcripts the audit needs are missing,
so an empty `audit_hits` never passes for want of files.
'''
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HOME = Path.home()
FORBIDDEN = [str(HOME / 'Projects'), str(HOME / '.cache' / 'agent-skills'), str(HOME / '.claude' / 'skills'),
             str(HOME / '.claude' / 'agents')]
TESTS = ('test_refund_in_parentheses_counts_negative', 'test_export_with_byte_order_mark_is_read',
         'test_missing_file_is_a_clean_error')


def hidden_results(scratch: Path, hidden: Path) -> dict[str, bool]:
    with tempfile.TemporaryDirectory() as tmp:
        run = subprocess.run([sys.executable, '-m', 'pytest', '-q', '-rA', '-p', 'no:cacheprovider', str(hidden)],
                             capture_output=True, text=True, cwd=tmp, env={**os.environ, 'F1_REPO': str(scratch)})
    return {name: bool(re.search(rf'^PASSED \S*::{name}\b', run.stdout, re.M)) for name in TESTS}


def results(out: Path) -> dict[str, dict]:
    '''The last `type: result` record of each session's stream, by stream name.'''
    found = {}
    for name in ('plan.jsonl', 'execute.jsonl'):
        path = out / name
        for line in path.read_text().splitlines() if path.is_file() else []:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get('type') == 'result':
                found[name] = record
    return found


def sessions_dir(scratch: Path) -> Path:
    '''Where Claude Code persists the sessions run from <scratch>.'''
    return HOME / '.claude' / 'projects' / re.sub(r'[^A-Za-z0-9]', '-', os.path.realpath(scratch))


def audit(scratch: Path, out: Path) -> tuple[list[str], str | None]:
    '''Forbidden-path hits in every stream and transcript, and an error when the transcripts are missing.'''
    sessions = sessions_dir(scratch)
    transcripts = sorted(sessions.rglob('*.jsonl')) if sessions.is_dir() else []
    error = None
    if not transcripts:
        error = f'no session transcripts under {sessions}: the audit cannot run'
    elif not any('subagents' in p.parts for p in transcripts):
        error = f'no subagent transcripts under {sessions}: the audit cannot see the subagents'
    hits = []
    for path in [out / 'plan.jsonl', out / 'execute.jsonl', *transcripts]:
        if not path.is_file():
            continue
        for n, line in enumerate(path.read_text().splitlines(), 1):
            for forbidden in FORBIDDEN:
                if forbidden in line:
                    hits.append(f'{path}:{n}: {forbidden}')
    return hits, error


def main() -> None:
    scratch, out, hidden = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()
    spec = (scratch / 'specs' / 'expense-tally.md').read_text()
    plan = (out / 'plan.md').read_text()
    records = results(out)
    hits, error = audit(scratch, out)
    result = {'handled': hidden_results(scratch, hidden), 'ratio': round(len(plan) / len(spec), 2),
              'cost': round(sum(float(r.get('total_cost_usd') or 0) for r in records.values()), 2),
              'execute_models': sorted((records.get('execute.jsonl') or {}).get('modelUsage') or {}),
              'audit_error': error, 'audit_hits': hits}
    (out / 'score.json').write_text(json.dumps(result, indent=1) + '\n')
    print(json.dumps(result, indent=1))


if __name__ == '__main__':
    main()
