# cc-guide: hooks.events hooks.exit-codes hooks.pitfalls @2.1.306
"""Contract tests for the project tooling hook templates — run from this directory, both ways.

cd hooks
uv run --python 3.13 --with pytest python -m pytest -q
uv run --python /usr/bin/python3 --with pytest python -m pytest -q

Each test drives a template as Claude Code does: through its own
`#!/usr/bin/env bash` shebang, with a hook payload on stdin. The child PATH is
a shim directory, then /usr/bin:/bin. The shim holds `bash`, `jq` and, where a
test wants one, a stub `uv` that logs its arguments and exits as told, so no
test runs a real uv or ruff or needs the network. Each test runs twice: with
the bash on this test's PATH, then with /bin/bash, macOS's bash 3.2, which
`#!/usr/bin/env bash` reaches on launchd's PATH.

A hook that exits 1 is a non-blocking error, so a crashed hook allows
everything: allow-path tests assert the exit code, and block tests also assert
the stderr marker, since a bash syntax error exits 2 too. Stdlib plus pytest,
and 3.9-compatible: the suite also runs under /usr/bin/python3.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

HOOKS = Path(__file__).resolve().parent
RUFF_CHECK = HOOKS / 'ruff-check.sh'
RUFF_FIX = HOOKS / 'ruff-fix.sh'
UV_GUARD = HOOKS / 'uv-guard.sh'

JQ = shutil.which('jq')
# Every child PATH ends with these. The shim, not they, decides whether uv exists.
SYSTEM_PATH = '/usr/bin:/bin'
# macOS's bash 3.2: the bash `#!/usr/bin/env bash` finds on launchd's PATH.
SYSTEM_BASH = '/bin/bash'

pytestmark = pytest.mark.skipif(
    JQ is None, reason='the project hooks read their payload with jq, and jq is not on PATH')


@pytest.fixture(params=['path-bash', 'system-bash'])
def shim(request, tmp_path):
    """A directory with bash and jq that goes first on each hook's PATH."""
    bash = shutil.which('bash') if request.param == 'path-bash' else SYSTEM_BASH
    if bash is None or not Path(bash).is_file():
        pytest.skip(f'no bash for {request.param}')
    bin_dir = tmp_path / 'bin'
    bin_dir.mkdir()
    (bin_dir / 'bash').symlink_to(bash)
    (bin_dir / 'jq').symlink_to(JQ)
    return bin_dir


@pytest.fixture
def ruff_shim(shim):
    """The shim, for hooks that call uv: only a stub may answer for it."""
    if shutil.which('uv', path=SYSTEM_PATH) is not None:
        pytest.skip(f'{SYSTEM_PATH} holds a uv, so a test cannot control which uv runs')
    return shim


def child_env(shim):
    return dict(os.environ, PATH=f'{shim}:{SYSTEM_PATH}')


def run_hook(script, payload, shim):
    return subprocess.run([str(script)], input=json.dumps(payload), capture_output=True,
                          text=True, env=child_env(shim), cwd=str(shim.parent))


def write_uv_stub(shim, check_status=0, check_output='', version_status=0):
    """A stub uv that appends its arguments to uv.log, one call per line.

    `uv run ruff --version` exits version_status. Any other call prints
    check_output and exits check_status.
    """
    (shim / 'check.out').write_text(check_output)
    stub = shim / 'uv'
    stub.write_text(
        '#!/bin/sh\n'
        f'printf \'%s\\n\' "$*" >> "{shim}/uv.log"\n'
        f'[ "$*" = "run ruff --version" ] && exit {version_status}\n'
        f'cat "{shim}/check.out"\n'
        f'exit {check_status}\n')
    stub.chmod(0o755)


def uv_calls(shim):
    log = shim / 'uv.log'
    return log.read_text().splitlines() if log.exists() else []


def test_the_shebang_runs_the_shim_bash(shim, tmp_path):
    probe = tmp_path / 'bash-version.sh'
    probe.write_text('#!/usr/bin/env bash\necho "$BASH_VERSION"\n')
    probe.chmod(0o755)
    want = subprocess.run([str(shim / 'bash'), '-c', 'echo "$BASH_VERSION"'],
                          capture_output=True, text=True, check=True).stdout
    got = subprocess.run([str(probe)], capture_output=True, text=True,
                         env=child_env(shim), check=True).stdout
    assert got == want


# --- ruff-check.sh (Stop) -------------------------------------------------------

LINT = 'bad.py:1:8: F401 [*] `os` imported but unused\nFound 1 error.\n'


def stop_payload(active=False):
    return {'hook_event_name': 'Stop', 'stop_hook_active': active}


def test_ruff_check_skips_a_hook_driven_continuation(ruff_shim):
    write_uv_stub(ruff_shim, check_status=1, check_output=LINT)
    proc = run_hook(RUFF_CHECK, stop_payload(active=True), ruff_shim)
    assert proc.returncode == 0, proc.stderr
    assert uv_calls(ruff_shim) == []


def test_ruff_check_passes_a_clean_tree(ruff_shim):
    write_uv_stub(ruff_shim, check_status=0)
    proc = run_hook(RUFF_CHECK, stop_payload(), ruff_shim)
    assert proc.returncode == 0, proc.stderr
    assert proc.stderr == ''
    assert uv_calls(ruff_shim) == ['run ruff check .']


def test_ruff_check_blocks_on_lint(ruff_shim):
    write_uv_stub(ruff_shim, check_status=1, check_output=LINT)
    proc = run_hook(RUFF_CHECK, stop_payload(), ruff_shim)
    assert proc.returncode == 2, proc.stderr
    assert proc.stderr.startswith('ruff check found issues')
    assert 'F401' in proc.stderr


def test_ruff_check_confirms_an_exit_1_with_ruff_version(ruff_shim):
    write_uv_stub(ruff_shim, check_status=1, check_output=LINT)
    run_hook(RUFF_CHECK, stop_payload(), ruff_shim)
    assert uv_calls(ruff_shim) == ['run ruff check .', 'run ruff --version']


@pytest.mark.parametrize('check_status, version_status, calls', [
    # uv run cannot sync the project, so both calls exit 1.
    pytest.param(1, 1, ['run ruff check .', 'run ruff --version'], id='sync-failure'),
    # ruff's own exit 2 (a bad config, an internal error), or uv cannot spawn ruff.
    pytest.param(2, 2, ['run ruff check .'], id='exit-2'),
])
def test_ruff_check_reports_a_ruff_that_cannot_run(ruff_shim, check_status, version_status, calls):
    write_uv_stub(ruff_shim, check_status=check_status, check_output='error: stub failure\n',
                  version_status=version_status)
    proc = run_hook(RUFF_CHECK, stop_payload(), ruff_shim)
    assert proc.returncode == 1, proc.stderr
    assert proc.stderr.splitlines()[0] == (
        f'ruff-check: ruff unavailable (exit {check_status}), so lint was not checked.')
    assert 'error: stub failure' in proc.stderr
    assert uv_calls(ruff_shim) == calls


def test_ruff_check_reports_a_missing_uv(ruff_shim):
    proc = run_hook(RUFF_CHECK, stop_payload(), ruff_shim)  # no stub, so no uv on PATH
    assert proc.returncode == 1, proc.stderr
    assert proc.stderr.splitlines()[0] == (
        'ruff-check: ruff unavailable (exit 127), so lint was not checked.')
