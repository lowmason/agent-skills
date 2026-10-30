'''Score one plan 73 F1 rep: hidden acceptance tests, plan-to-spec ratio, cost and isolation audit.

Usage, from the repository root:
  uv run --with pytest python <f1>/score_f1.py <scratch> <out-dir> <hidden-test-file>
Prints one JSON object and writes it to <out-dir>/score.json. `handled` maps each hidden test to
true when it passed. `cost` sums both sessions' total_cost_usd, and `execute_models` lists the
models the execution session's result record names. `audit_hits` lists every transcript line
that names a path outside the scratch repository that a run must not touch, written as an
absolute path or under `~/`, `$HOME/` or `${HOME}/`, or that names the hidden test file
(`test_hidden`, `F1_REPO`); read each one by hand under the VOID rule. `audit_error` is set when
the transcripts the audit needs are missing, so an empty `audit_hits` never passes for want of
files. The plan-to-spec ratio uses the committed fixture spec, since the plan-completion protocol
may move the scratch copy to `specs/completed/`. The scorer exits with an error, and writes no
score.json, when pytest reports a hidden test as neither passed nor failed.
'''
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HOME = Path.home()
FORBIDDEN_UNDER_HOME = ('Projects', '.cache/agent-skills', '.claude/skills', '.claude/agents')
FORBIDDEN = [form for rel in FORBIDDEN_UNDER_HOME
             for form in (str(HOME / rel), f'~/{rel}', f'$HOME/{rel}', f'${{HOME}}/{rel}')]
HIDDEN_MARKERS = ('test_hidden', 'F1_REPO')
TESTS = ('test_refund_in_parentheses_counts_negative', 'test_export_with_byte_order_mark_is_read',
         'test_missing_file_is_a_clean_error')
TAIL_LINES = 20


def hidden_results(scratch: Path, hidden: Path) -> dict[str, bool]:
    '''Pass or fail of each hidden test; exits when pytest reports a test as neither.'''
    with tempfile.TemporaryDirectory() as tmp:
        run = subprocess.run([sys.executable, '-m', 'pytest', '-q', '-rA', '-p', 'no:cacheprovider', str(hidden)],
                             capture_output=True, text=True, cwd=tmp, env={**os.environ, 'F1_REPO': str(scratch)})
    passed = {name: bool(re.search(rf'^PASSED \S*::{name}\b', run.stdout, re.M)) for name in TESTS}
    failed = {name: bool(re.search(rf'^FAILED \S*::{name}\b', run.stdout, re.M)) for name in TESTS}
    unscored = [name for name in TESTS if not passed[name] and not failed[name]]
    if unscored:
        stdout_tail = '\n'.join(run.stdout.splitlines()[-TAIL_LINES:])
        stderr_tail = '\n'.join(run.stderr.splitlines()[-TAIL_LINES:])
        sys.exit(f'score_f1: pytest reported neither PASSED nor FAILED for {", ".join(unscored)}; '
                 f'no score.json written (exit {run.returncode}).\n'
                 f'--- pytest stdout, last {TAIL_LINES} lines ---\n{stdout_tail}\n'
                 f'--- pytest stderr, last {TAIL_LINES} lines ---\n{stderr_tail}')
    return passed


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
            for marker in [*FORBIDDEN, *HIDDEN_MARKERS]:
                if marker in line:
                    hits.append(f'{path}:{n}: {marker}')
    return hits, error


def main() -> None:
    scratch, out, hidden = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()
    spec = (Path(__file__).resolve().parent / 'fixture' / 'expense-tally.md').read_text()
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
