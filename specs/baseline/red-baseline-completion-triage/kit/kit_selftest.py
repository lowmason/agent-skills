'''No-model self-test of plan 101's run_reps.sh.

Usage, from the repository root: uv run python <kit>/kit_selftest.py
It prints `kit self-test passed`, or raises on the first check that fails.

A stub `claude` goes first on PATH, so no model runs and nothing is billed. The stub ignores its
arguments, writes a file `marker-<its pid>` into its working directory and prints one JSON object
that holds `credential_expires_at` twice, at the top level and inside `usage`. The test runs
run_reps.sh for reps 1 and 2 on a one-line prompt and checks three things:
  1. neither rep file holds `credential_expires_at` any more, and both still parse with
     `type`, `result` and `total_cost_usd` intact;
  2. each rep lists exactly one name, a `marker-` file, and the two markers differ, so each rep
     sees only its own folder;
  3. the two working directories differ and both sit under /tmp/plan101-rep-.
A second stub prints bytes that are not UTF-8 and hold the key, so scrub_json.py cannot read the
file. The test runs rep 3 with it and checks a fourth thing:
  4. run_reps.sh exits 3, and names the rep that still holds `credential_expires_at`.
The test imports no other kit file. It reaches the runner by its own path and nothing else.
'''
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RUNNER = Path(__file__).resolve().parent / 'run_reps.sh'
KEY = 'credential_expires_at'
REP_PREFIXES = ('/tmp/plan101-rep-', '/private/tmp/plan101-rep-')
RUN_TIMEOUT_SECONDS = 60

STUB = '''#!/usr/bin/env python3
import json
import os

cwd = os.getcwd()
open(f'marker-{os.getpid()}', 'w').close()
names = sorted(os.listdir(cwd))
print(json.dumps({
    'type': 'result',
    'result': '\\n'.join([cwd, *names]),
    'total_cost_usd': 0,
    'num_turns': 1,
    'credential_expires_at': 1790000000,
    'usage': {'input_tokens': 1, 'credential_expires_at': 1790000000},
}))
'''

BAD_STUB = '''#!/usr/bin/env python3
import os
import sys

sys.stderr.write(os.getcwd())
sys.stdout.buffer.write(b'\\xff {"credential_expires_at": 1790000000}\\n')
'''


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def stub_path(stub_dir: Path) -> str:
    '''A PATH built from scratch: the stub first, then the running Python's folder, then the system.

    The running Python's folder supplies `python3` for the stub's shebang and for scrub_json.py.
    The inherited PATH is left out, so a stub that failed to land can never fall through to a real
    `claude`.
    '''
    return os.pathsep.join([str(stub_dir), str(Path(sys.executable).parent), '/usr/bin', '/bin'])


def check_rep(name: str, text: str, data: dict) -> None:
    check(KEY not in text, f'{name} still holds {KEY}')
    check(
        all(k in data for k in ('type', 'result', 'total_cost_usd')),
        f'{name} lost type, result or total_cost_usd: {sorted(data)}',
    )


def split_result(data: dict) -> tuple[str, list[str]]:
    lines = str(data['result']).split('\n')
    return lines[0], lines[1:]


def check_unreadable_rep(root: Path, prompt: Path) -> None:
    '''A rep file that scrub_json.py cannot read keeps the key: the runner must exit 3 and name it.'''
    bad_dir = root / 'badbin'
    bad_dir.mkdir()
    bad = bad_dir / 'claude'
    bad.write_text(BAD_STUB)
    bad.chmod(0o755)
    search_path = stub_path(bad_dir)
    check(shutil.which('claude', path=search_path) == str(bad), 'the bad stub is not the first claude on PATH')
    out = root / 'out-bad'
    run = subprocess.run(
        ['bash', str(RUNNER), str(prompt), str(out), '3', '3', 'stub-model', '0.01'],
        capture_output=True, text=True, timeout=RUN_TIMEOUT_SECONDS,
        env={**os.environ, 'PATH': search_path},
    )
    try:
        check(KEY in (out / 'rep3.json').read_text(errors='replace'), 'rep3.json lost the key: the scrub should not have read it')
        check(run.returncode == 3, f'run_reps.sh should exit 3 for a rep file that still holds {KEY}, got {run.returncode}: {run.stdout}{run.stderr}')
        check('rep3' in run.stdout and KEY in run.stdout, f'the runner should name rep3 and {KEY}: {run.stdout}')
    finally:
        cwd = (out / 'rep3.err').read_text() if (out / 'rep3.err').exists() else ''
        if cwd.startswith(REP_PREFIXES) and Path(cwd).is_dir():
            shutil.rmtree(cwd)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix='plan101-selftest-') as tmp:
        root = Path(tmp)
        stub_dir = root / 'bin'
        stub_dir.mkdir()
        stub = stub_dir / 'claude'
        stub.write_text(STUB)
        stub.chmod(0o755)
        search_path = stub_path(stub_dir)
        check(shutil.which('claude', path=search_path) == str(stub), 'the stub is not the first claude on PATH')
        check(shutil.which('python3', path=search_path) is not None, 'no python3 on the stub PATH')
        prompt = root / 'prompt.txt'
        prompt.write_text('one-line prompt\n')
        out = root / 'out'
        run = subprocess.run(
            ['bash', str(RUNNER), str(prompt), str(out), '1', '2', 'stub-model', '0.01'],
            capture_output=True, text=True, timeout=RUN_TIMEOUT_SECONDS,
            env={**os.environ, 'PATH': search_path},
        )
        check(run.returncode == 0, f'run_reps.sh exited {run.returncode}: {run.stdout}{run.stderr}')
        work_dirs = []
        try:
            texts = [(out / f'rep{n}.json').read_text() for n in (1, 2)]
            datas = [json.loads(text) for text in texts]
            parsed = [split_result(data) for data in datas]
            work_dirs = [cwd for cwd, _ in parsed]
            for n, (text, data) in enumerate(zip(texts, datas), start=1):
                check_rep(f'rep{n}.json', text, data)
            for n, (cwd, names) in enumerate(parsed, start=1):
                check(len(names) == 1 and names[0].startswith('marker-'),
                      f'rep{n} should list exactly one marker- name in its folder, got {names}')
            check(parsed[0][1] != parsed[1][1], f'both reps made the same marker: {parsed[0][1]}')
            check(parsed[0][0] != parsed[1][0], f'both reps ran in the same folder: {parsed[0][0]}')
            for n, (cwd, _) in enumerate(parsed, start=1):
                check(cwd.startswith(REP_PREFIXES), f'rep{n} ran in {cwd}, not under {REP_PREFIXES[0]}')
        finally:
            # run_reps.sh never removes its folders: remove the two this test made, by exact path.
            for cwd in work_dirs:
                if cwd.startswith(REP_PREFIXES) and Path(cwd).is_dir():
                    shutil.rmtree(cwd)
        check_unreadable_rep(root, prompt)
    print('kit self-test passed')


if __name__ == '__main__':
    main()
