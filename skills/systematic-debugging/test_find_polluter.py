"""Tests for find-polluter.sh — run from this directory.

cd skills/systematic-debugging && uv run --with pytest python -m pytest -q

The script is bash, so each test drives it as a subprocess in a throwaway git
project and asserts on the exit code, stdout, and the files a stub test runner
was handed. TEST_CMD points at that stub: it logs every file it is given and
creates the pollution marker only for the file a test names as the polluter.
Every test runs under each distinct bash found, because /bin/bash is 3.2 on
macOS while the shebang's `env bash` may resolve to a newer one.
"""

import os
import shlex
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent / 'find-polluter.sh'
MARKER = 'pollution.marker'
BASHES = sorted(
    {os.path.realpath(b) for b in ('/bin/bash', shutil.which('bash')) if b and os.path.exists(b)}
)

# Sanitised so `git init` doesn't inherit the user's global/system git config
# (init.templateDir and the like).
GIT_ENV = {**os.environ, 'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_NOSYSTEM': '1'}


@pytest.fixture
def project(tmp_path):
    """A throwaway git project: a top-level and a nested TypeScript test, and
    a pytest file at the top level and one a directory down."""
    root = tmp_path / 'project'
    (root / 'src' / 'sub').mkdir(parents=True)
    (root / 'tests').mkdir()
    (root / 'src' / 'top.test.ts').write_text("test('top')\n")
    (root / 'src' / 'sub' / 'b.test.ts').write_text("test('nested')\n")
    (root / 'test_root.py').write_text('def test_root():\n    pass\n')
    (root / 'tests' / 'test_a.py').write_text('def test_a():\n    pass\n')
    subprocess.run(['git', 'init', '-q', str(root)], check=True, env=GIT_ENV)
    return root


def make_runner(tmp_path, polluter=None):
    """Write a TEST_CMD stub outside the project. It appends each file it is
    handed to a log and, for the polluter, creates the marker in the working
    directory, as a polluting test would."""
    log = tmp_path / 'ran.log'
    runner = tmp_path / 'bin' / 'fake-test-runner'
    runner.parent.mkdir(exist_ok=True)
    lines = ['#!/bin/sh', f'printf "%s\\n" "$1" >> {shlex.quote(str(log))}']
    if polluter:
        lines.append(f'case "$1" in */{polluter}) touch {MARKER} ;; esac')
    runner.write_text('\n'.join(lines) + '\n')
    runner.chmod(0o755)
    return runner, log


def find_polluter(bash, project, pattern, runner):
    return subprocess.run(
        [bash, str(SCRIPT), MARKER, pattern],
        cwd=project,
        capture_output=True,
        text=True,
        env={**os.environ, 'TEST_CMD': str(runner)},
    )


def ran(log):
    """The files the stub runner was handed, sorted; none if it never ran."""
    return sorted(log.read_text().split()) if log.exists() else []


@pytest.mark.parametrize('bash', BASHES)
@pytest.mark.parametrize('pattern', ['src/**/*.test.ts', './src/**/*.test.ts'])
def test_globstar_pattern_runs_top_level_and_nested_tests(bash, project, tmp_path, pattern):
    """The header's own example. find prints ./-prefixed paths, and its -path
    cannot match '**/' against zero directories, so before the fix the bare
    form matched nothing and the ./ form skipped src/top.test.ts. The count
    line is printed from a variable; the runner's log proves each file ran."""
    runner, log = make_runner(tmp_path)
    result = find_polluter(bash, project, pattern, runner)
    assert 'Found 2 test files' in result.stdout
    assert ran(log) == ['./src/sub/b.test.ts', './src/top.test.ts']
    assert result.returncode == 0


@pytest.mark.parametrize('bash', BASHES)
def test_documented_pytest_pattern_still_matches(bash, project, tmp_path):
    """root-cause-tracing.md's '*/test_*.py' worked before the fix, top-level
    files included: its leading '*' takes the '.' of ./test_root.py. That is
    why the bug hid on a pytest stack, and why the ./ prefix alone, which
    makes '*/' mean "at least one directory", would drop top-level tests."""
    runner, log = make_runner(tmp_path)
    result = find_polluter(bash, project, '*/test_*.py', runner)
    assert 'Found 2 test files' in result.stdout
    assert ran(log) == ['./test_root.py', './tests/test_a.py']
    assert result.returncode == 0


@pytest.mark.parametrize('bash', BASHES)
def test_unmatched_pattern_says_nothing_ran_instead_of_all_clear(bash, project, tmp_path):
    """An empty find result counted as one line: "Found 1 test files", no
    test run, then "No polluter found - all tests clean!" and exit 0, a
    false all-clear on any typo. Upstream's fix reports "Found 0" and still
    leaves through that clean line; this port says no test ran and exits 2."""
    runner, log = make_runner(tmp_path)
    result = find_polluter(bash, project, 'nomatch/**/*.test.ts', runner)
    assert 'Found 0 test files' in result.stdout
    assert 'No test files match' in result.stdout
    assert 'No polluter found' not in result.stdout
    assert 'all tests clean' not in result.stdout
    assert ran(log) == []
    assert result.returncode == 2


@pytest.mark.parametrize('bash', BASHES)
def test_names_the_polluter_after_running_clean_tests_first(bash, project, tmp_path):
    """The bisection itself, over the corrected list: b.test.ts sorts first
    and runs clean, then top.test.ts, a top-level file the old pattern
    handling never reached, creates the marker."""
    runner, log = make_runner(tmp_path, polluter='top.test.ts')
    result = find_polluter(bash, project, 'src/**/*.test.ts', runner)
    assert 'FOUND POLLUTER' in result.stdout
    assert 'Test: ./src/top.test.ts' in result.stdout
    assert ran(log) == ['./src/sub/b.test.ts', './src/top.test.ts']
    assert result.returncode == 1


@pytest.mark.parametrize('bash', BASHES)
def test_pollution_that_exists_before_the_first_test_is_not_an_all_clear(bash, project, tmp_path):
    """A '.git' check run from a repository root, the documented example until
    2026-10-19, hits this: the marker is there before any test runs. Before the fix every test was
    skipped with a warning and the run ended on "No polluter found - all
    tests clean!" with exit 0, the same all-clear a typo'd pattern once got.
    No test can be blamed for a marker it did not create, so the script
    stops before running any test, says why, and exits 3."""
    (project / MARKER).write_text('left over\n')
    runner, log = make_runner(tmp_path)
    result = find_polluter(bash, project, 'src/**/*.test.ts', runner)
    assert 'already exists' in result.stdout
    assert 'No polluter found' not in result.stdout
    assert 'all tests clean' not in result.stdout
    assert ran(log) == []
    assert result.returncode == 3
    # The marker may belong there (a repository's own .git at its root), so the
    # message must not tell the reader to delete it outright.
    assert 'Remove it and run again' not in result.stdout
    assert 'before you remove it' in result.stdout
