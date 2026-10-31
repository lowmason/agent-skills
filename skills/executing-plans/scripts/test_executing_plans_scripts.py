"""Tests for task-start and task-done -- run from this directory.

cd skills/executing-plans/scripts && uv run --with pytest python -m pytest -q

The scripts are bash, so each test drives one as a subprocess and asserts on
exit code, stdout, stderr and written files. The scripts call the sibling
skill's helpers by relative path, so the tests reach those only through them.
The cases adapt upstream's tests/claude-code/test-executing-plans-scripts.sh.
"""

import os
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent
TASK_START = SCRIPTS / 'task-start'
TASK_DONE = SCRIPTS / 'task-done'

# Sanitised so the suite ignores the user's global and system git config
# (commit.gpgsign, core.hooksPath, init.templateDir, ...).
GIT_ENV = {**os.environ, 'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_NOSYSTEM': '1'}

PLAN = """\
# Demo Plan

## Global Constraints

- Single quotes over double.

### Task 1: First thing

- [ ] **Step 1: do it**

### Task 2: Second thing

- [ ] **Step 1: other**
"""

OK_CMD = ['sh', '-c', 'echo "Ran 3 tests"; echo OK']


def run(*argv, cwd=None, env=None):
    return subprocess.run(
        [str(a) for a in argv],
        cwd=cwd,
        capture_output=True,
        text=True,
        env=GIT_ENV if env is None else env,
    )


def git(*argv, cwd):
    """Run a git command that arranges test state and assert it succeeded."""
    result = run('git', *argv, cwd=cwd)
    assert result.returncode == 0, result.stderr
    return result


def head(cwd):
    return git('rev-parse', 'HEAD', cwd=cwd).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    """A throwaway git repo with the demo plan committed."""
    git('init', '-q', tmp_path, cwd=tmp_path)
    git('config', 'user.email', 't@example.invalid', cwd=tmp_path)
    git('config', 'user.name', 'T', cwd=tmp_path)
    (tmp_path / 'plan.md').write_text(PLAN)
    git('add', 'plan.md', cwd=tmp_path)
    git('commit', '-q', '-m', 'plan', cwd=tmp_path)
    return tmp_path


def workspace(repo):
    return repo / '.sdd' / 'plan'


def commit_work(repo, name='work.txt'):
    (repo / name).write_text('x\n')
    git('add', name, cwd=repo)
    git('commit', '-q', '-m', 'work', cwd=repo)


# -- task-start --------------------------------------------------------------


@pytest.mark.parametrize('argv', [('plan.md',), ('plan.md', 1, 'x')])
def test_task_start_rejects_bad_arguments(repo, argv):
    assert run(TASK_START, *argv, cwd=repo).returncode == 2


def test_task_start_prints_brief_path_and_writes_it(repo):
    result = run(TASK_START, 'plan.md', 1, cwd=repo)
    assert result.returncode == 0, result.stderr
    line = next(l for l in result.stdout.splitlines() if l.startswith('brief: '))
    printed = Path(line[len('brief: '):])
    assert printed.resolve() == (workspace(repo) / 'task-1-brief.md').resolve()
    assert printed.read_text().strip()


def test_task_start_prints_head_as_base(repo):
    result = run(TASK_START, 'plan.md', 1, cwd=repo)
    assert result.returncode == 0, result.stderr
    assert f'base: {head(repo)}' in result.stdout


def test_task_start_fails_on_a_missing_task(repo):
    result = run(TASK_START, 'plan.md', 9, cwd=repo)
    assert result.returncode == 3
    assert 'task 9 not found' in result.stderr
    assert 'base:' not in result.stdout


def test_task_start_handles_a_plan_path_with_a_space(repo):
    (repo / 'my plan.md').write_text(PLAN)
    result = run(TASK_START, 'my plan.md', 1, cwd=repo)
    assert result.returncode == 0, result.stderr
    line = next(l for l in result.stdout.splitlines() if l.startswith('brief: '))
    expected = repo / '.sdd' / 'my plan' / 'task-1-brief.md'
    assert Path(line[len('brief: '):]).resolve() == expected.resolve()


# -- task-done ---------------------------------------------------------------


def test_task_done_records_a_passing_task(repo):
    base = head(repo)
    commit_work(repo)
    result = run(TASK_DONE, 'plan.md', 1, base, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 0, result.stderr
    expected = (
        f'Task 1: complete (commits {base[:7]}..{head(repo)[:7]}, '
        f'tests: sh -c \'echo "Ran 3 tests"; echo OK\' → OK)'
    )
    assert (workspace(repo) / 'progress.md').read_text().splitlines()[1:] == [expected]
    assert 'OK' in result.stdout
    assert 'Ran 3 tests' in (workspace(repo) / 'task-1-tests.log').read_text()


def test_task_done_records_nothing_for_a_failing_task(repo):
    base = head(repo)
    cmd = ['sh', '-c', 'echo "FAILED (errors=1)"; exit 1']
    result = run(TASK_DONE, 'plan.md', 2, base, '--', *cmd, cwd=repo)
    assert result.returncode == 1
    ledger = workspace(repo) / 'progress.md'
    assert not ledger.exists() or 'Task 2: complete' not in ledger.read_text()
    assert 'FAILED' in result.stdout + result.stderr
    assert 'Task 2 NOT recorded' in result.stderr


def test_task_done_records_a_silent_pass_as_no_output(repo):
    result = run(TASK_DONE, 'plan.md', 1, head(repo), '--', 'true', cwd=repo)
    assert result.returncode == 0, result.stderr
    ledger = (workspace(repo) / 'progress.md').read_text()
    assert ledger.splitlines()[-1].endswith('→ (no output))')


def test_task_done_treats_blank_only_output_as_no_output(repo):
    cmd = ['sh', '-c', "printf '\\n  \\n'"]
    result = run(TASK_DONE, 'plan.md', 1, head(repo), '--', *cmd, cwd=repo)
    assert result.returncode == 0, result.stderr
    ledger = (workspace(repo) / 'progress.md').read_text()
    assert ledger.splitlines()[-1].endswith('→ (no output))')


def test_task_done_starts_a_new_ledger_with_the_plan_line(repo):
    result = run(TASK_DONE, 'plan.md', 1, head(repo), '--', 'true', cwd=repo)
    assert result.returncode == 0, result.stderr
    first = (workspace(repo) / 'progress.md').read_text().splitlines()[0]
    assert first == 'Plan: plan.md'


def test_task_done_matches_an_absolute_plan_line_against_a_relative_argument(repo):
    ws = workspace(repo)
    ws.mkdir(parents=True)
    (ws / 'progress.md').write_text(f'Plan: {(repo / "plan.md").resolve()}\n')
    result = run(TASK_DONE, 'plan.md', 1, head(repo), '--', 'true', cwd=repo)
    assert result.returncode == 0, result.stderr
    assert 'Task 1: complete' in (ws / 'progress.md').read_text()


def test_task_done_matches_from_a_subdirectory(repo):
    sub = repo / 'sub'
    sub.mkdir()
    ws = workspace(repo)
    ws.mkdir(parents=True)
    (ws / 'progress.md').write_text('Plan: plan.md\n')
    result = run(TASK_DONE, '../plan.md', 1, head(repo), '--', 'true', cwd=sub)
    assert result.returncode == 0, result.stderr
    assert 'Task 1: complete' in (ws / 'progress.md').read_text()


def test_task_done_matches_through_a_symlinked_repo_path(repo, tmp_path_factory):
    base = head(repo)
    first = run(TASK_DONE, 'plan.md', 1, base, '--', 'true', cwd=repo)
    assert first.returncode == 0, first.stderr
    link = tmp_path_factory.mktemp('links') / 'link'
    link.symlink_to(repo)
    # Bash keeps an inherited PWD only when it names the cwd, so set it to the
    # symlinked path; otherwise the shell would silently use the physical path.
    env = {**GIT_ENV, 'PWD': str(link)}
    second = run(TASK_DONE, 'plan.md', 2, base, '--', 'true', cwd=link, env=env)
    assert second.returncode == 0, second.stderr
    lines = (workspace(repo) / 'progress.md').read_text().splitlines()
    assert sum(l.startswith('Task ') and 'complete' in l for l in lines) == 2


def test_task_done_refuses_a_same_basename_plan_in_a_subdirectory(repo):
    sub = repo / 'sub'
    sub.mkdir()
    (sub / 'plan.md').write_text(PLAN.replace('Demo', 'Other'))
    ws = workspace(repo)
    ws.mkdir(parents=True)
    ledger = ws / 'progress.md'
    ledger.write_text('Plan: plan.md\n')
    before = ledger.read_bytes()
    cmd = ['sh', '-c', 'touch ran']
    result = run(TASK_DONE, 'plan.md', 1, head(repo), '--', *cmd, cwd=sub)
    assert result.returncode == 3
    assert ledger.read_bytes() == before
    assert not (sub / 'ran').exists()


def test_task_done_refuses_when_the_ledger_plan_has_moved(repo):
    sub = repo / 'sub'
    sub.mkdir()
    (sub / 'plan.md').write_text(PLAN.replace('Demo', 'Other'))
    ws = workspace(repo)
    ws.mkdir(parents=True)
    ledger = ws / 'progress.md'
    log = ws / 'task-1-tests.log'
    ledger.write_text('Plan: plan.md\n')
    log.write_text('old\n')
    base = head(repo)
    (repo / 'plan.md').unlink()
    before = (ledger.read_bytes(), log.read_bytes())
    cmd = ['sh', '-c', 'touch ran']
    result = run(TASK_DONE, 'plan.md', 1, base, '--', *cmd, cwd=sub)
    assert result.returncode == 3
    assert (ledger.read_bytes(), log.read_bytes()) == before
    assert not (sub / 'ran').exists()


def test_task_done_matches_a_plan_reached_through_a_file_symlink(repo):
    (repo / 'specs').mkdir()
    (repo / 'plan.md').rename(repo / 'specs' / 'plan.md')
    (repo / 'alias').mkdir()
    (repo / 'alias' / 'plan.md').symlink_to(Path('..') / 'specs' / 'plan.md')
    # Both paths share the basename, so both map to the workspace .sdd/plan.
    ws = workspace(repo)
    ws.mkdir(parents=True)
    ledger = ws / 'progress.md'
    ledger.write_text('Plan: specs/plan.md\n')
    result = run(TASK_DONE, 'alias/plan.md', 1, head(repo), '--', 'true', cwd=repo)
    assert result.returncode == 0, result.stderr
    assert 'Task 1: complete' in ledger.read_text()


def test_task_done_resolves_a_file_symlink_beneath_a_directory_symlink(repo):
    # alias -> real/nested, and real/nested/plan.md -> ../plan.md: the target is
    # real/plan.md, a different plan from the root plan.md that owns the ledger.
    (repo / 'real' / 'nested').mkdir(parents=True)
    (repo / 'real' / 'plan.md').write_text(PLAN)
    (repo / 'real' / 'nested' / 'plan.md').symlink_to(Path('..') / 'plan.md')
    (repo / 'alias').symlink_to(Path('real') / 'nested')
    ws = workspace(repo)
    ws.mkdir(parents=True)
    ledger = ws / 'progress.md'
    ledger.write_text('Plan: plan.md\n')
    result = run(TASK_DONE, 'alias/plan.md', 1, head(repo), '--', 'true', cwd=repo)
    assert result.returncode == 3, result.stderr


def test_task_done_refuses_another_plans_ledger(repo):
    ws = workspace(repo)
    ws.mkdir(parents=True)
    ledger = ws / 'progress.md'
    log = ws / 'task-1-tests.log'
    ledger.write_text('Plan: specs/other.md\n')
    log.write_text('old\n')
    before = (ledger.read_bytes(), log.read_bytes())
    cmd = ['sh', '-c', 'touch ran']
    result = run(TASK_DONE, 'plan.md', 1, head(repo), '--', *cmd, cwd=repo)
    assert result.returncode == 3
    assert (ledger.read_bytes(), log.read_bytes()) == before
    assert not (repo / 'ran').exists()
    assert 'specs/other.md' in result.stderr
    assert 'plan.md' in result.stderr


def test_task_done_handles_a_plan_path_with_a_space(repo):
    (repo / 'my plan.md').write_text(PLAN)
    result = run(TASK_DONE, 'my plan.md', 1, head(repo), '--', 'true', cwd=repo)
    assert result.returncode == 0, result.stderr
    ledger = repo / '.sdd' / 'my plan' / 'progress.md'
    assert ledger.read_text().splitlines()[0] == 'Plan: my plan.md'


@pytest.mark.parametrize(
    'argv',
    [
        ('plan.md', 1, 'HEAD', 'true', 'x'),  # no '--'
        ('plan.md', 1, 'HEAD', '--'),  # fewer than 5 args
        ('plan.md', 1, 'HEAD'),
    ],
)
def test_task_done_rejects_bad_arguments(repo, argv):
    assert run(TASK_DONE, *argv, cwd=repo).returncode == 2


def test_task_done_rejects_a_bad_base(repo):
    result = run(TASK_DONE, 'plan.md', 1, 'nope', '--', 'true', cwd=repo)
    assert result.returncode == 2
    assert 'bad BASE' in result.stderr
