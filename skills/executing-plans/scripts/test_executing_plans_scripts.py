"""Tests for task-start and task-done -- run from this directory.

cd skills/executing-plans/scripts && uv run --with pytest python -m pytest -q

The scripts are bash, so each test drives one as a subprocess and asserts on
exit code, stdout, stderr and written files. The scripts call the sibling
skill's helpers by relative path, so the tests reach those only through them.
One test is the exception: it runs two of them directly, by that same
relative path, to write a real mutant run. sdd-workspace writes the
self-ignoring .sdd/.gitignore, and mutant-run, which task-done never runs,
writes the run file that task-done reads.
The cases adapt upstream's tests/claude-code/test-executing-plans-scripts.sh.
The mutant gate's cases are local.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent
TASK_START = SCRIPTS / 'task-start'
TASK_DONE = SCRIPTS / 'task-done'
# The sibling skill's scripts, by the relative path task-done uses.
SDD_SCRIPTS = SCRIPTS / '..' / '..' / 'subagent-driven-development' / 'scripts'
MUTANT_RUN = SDD_SCRIPTS / 'mutant-run'
SDD_WORKSPACE = SDD_SCRIPTS / 'sdd-workspace'

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
# A task that is not a mutant task passes the mutant gate with a reason.
NO_MUTANTS = ('--no-mutants', 'demo task')


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


def recorded(repo, task=1):
    '''Whether the ledger holds a completion line for the task.'''
    ledger = workspace(repo) / 'progress.md'
    if not ledger.exists():
        return False
    return any(line.startswith(f'Task {task}: complete') for line in ledger.read_text().splitlines())


def write_mutants(repo, numbers, withdrawn=()):
    '''Write task-1-mutants.md: a Mutant line per number, a Withdrawn line per withdrawn number.'''
    lines = [
        '# Task 1 mutants',
        '',
        '## Inputs',
        '',
        '| Rule | Shape | Test |',
        '|---|---|---|',
        '| brief: demo rule | a demo input | test_demo |',
        '',
        '## Mutants',
        '',
        *[f'Mutant {k}: brief: demo rule, test_demo — wrong version {k} — task-1-mutant-{k}.patch' for k in numbers],
        *[f'Withdrawn: {k} — demo' for k in withdrawn],
    ]
    ws = workspace(repo)
    ws.mkdir(parents=True, exist_ok=True)
    (ws / 'task-1-mutants.md').write_text('\n'.join(lines) + '\n')


# The revert: line of a run whose task changed no file outside the tests and the project config.
NONE_REVERT = 'revert: none: no file outside the tests and the project config changed'


def write_run(repo, name, run_head, run_base, result, numbers, revert=NONE_REVERT):
    '''Write a mutant run file in mutant-run's layout, each numbered mutant CAUGHT.

    run_base=None or revert=None leaves that header line out.
    '''
    task, _, rest = name.removeprefix('task-').partition('-mutants')
    run_number = rest.removeprefix('-').removesuffix('.log') or '1'
    zeros = '0' * 64
    caught = ' '.join(str(k) for k in numbers)
    lines = [
        f'mutant-run: Task {task}, run {run_number}',
        'command: sh -c true',
        f'head: {run_head}',
        *([f'base: {run_base}'] if run_base is not None else []),
        'tree: clean',
        f'result: {result}',
        *([revert] if revert is not None else []),
        '--- mutants ---',
        *[f'mutant {k}: CAUGHT exit 1 sha256 {zeros} tests: t::a' for k in numbers],
        '--- tests ---',
        f'test t::a: caught {caught}',
        '--- output: baseline ---',
        '1 passed',
    ]
    for k in numbers:
        lines += [f'--- output: mutant {k} ---', '1 failed']
    ws = workspace(repo)
    ws.mkdir(parents=True, exist_ok=True)
    (ws / name).write_text('\n'.join(lines) + '\n')


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


def test_task_start_refuses_a_repository_with_no_commit(tmp_path):
    git('init', '-q', tmp_path, cwd=tmp_path)
    (tmp_path / 'plan.md').write_text(PLAN)
    result = run(TASK_START, 'plan.md', 1, cwd=tmp_path)
    assert result.returncode == 2
    assert 'make a first commit' in result.stderr
    assert 'base:' not in result.stdout
    assert not (tmp_path / '.sdd' / 'plan' / 'task-1-brief.md').exists()


def test_task_start_passes_an_unclosed_fence_refusal_through(repo):
    (repo / 'unclosed.md').write_text('# P\n\n### Task 1: One\n\n```bash\necho open\n\n### Task 2: Two\n')
    result = run(TASK_START, 'unclosed.md', 1, cwd=repo)
    assert result.returncode == 4
    assert 'never closes' in result.stderr
    assert 'base:' not in result.stdout


# -- task-done ---------------------------------------------------------------


def test_task_done_records_a_passing_task(repo):
    base = head(repo)
    commit_work(repo)
    result = run(TASK_DONE, 'plan.md', 1, base, *NO_MUTANTS, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 0, result.stderr
    expected = (
        f'Task 1: complete (commits {base[:7]}..{head(repo)[:7]}, mutants: none: demo task, '
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
    result = run(TASK_DONE, 'plan.md', 1, head(repo), *NO_MUTANTS, '--', 'true', cwd=repo)
    assert result.returncode == 0, result.stderr
    ledger = (workspace(repo) / 'progress.md').read_text()
    assert ledger.splitlines()[-1].endswith('→ (no output))')


def test_task_done_treats_blank_only_output_as_no_output(repo):
    cmd = ['sh', '-c', "printf '\\n  \\n'"]
    result = run(TASK_DONE, 'plan.md', 1, head(repo), *NO_MUTANTS, '--', *cmd, cwd=repo)
    assert result.returncode == 0, result.stderr
    ledger = (workspace(repo) / 'progress.md').read_text()
    assert ledger.splitlines()[-1].endswith('→ (no output))')


def test_task_done_starts_a_new_ledger_with_the_plan_line(repo):
    result = run(TASK_DONE, 'plan.md', 1, head(repo), *NO_MUTANTS, '--', 'true', cwd=repo)
    assert result.returncode == 0, result.stderr
    first = (workspace(repo) / 'progress.md').read_text().splitlines()[0]
    assert first == 'Plan: plan.md'


def test_task_done_matches_an_absolute_plan_line_against_a_relative_argument(repo):
    ws = workspace(repo)
    ws.mkdir(parents=True)
    (ws / 'progress.md').write_text(f'Plan: {(repo / "plan.md").resolve()}\n')
    result = run(TASK_DONE, 'plan.md', 1, head(repo), *NO_MUTANTS, '--', 'true', cwd=repo)
    assert result.returncode == 0, result.stderr
    assert 'Task 1: complete' in (ws / 'progress.md').read_text()


def test_task_done_matches_from_a_subdirectory(repo):
    sub = repo / 'sub'
    sub.mkdir()
    ws = workspace(repo)
    ws.mkdir(parents=True)
    (ws / 'progress.md').write_text('Plan: plan.md\n')
    result = run(TASK_DONE, '../plan.md', 1, head(repo), *NO_MUTANTS, '--', 'true', cwd=sub)
    assert result.returncode == 0, result.stderr
    assert 'Task 1: complete' in (ws / 'progress.md').read_text()


def test_task_done_matches_through_a_symlinked_repo_path(repo, tmp_path_factory):
    base = head(repo)
    first = run(TASK_DONE, 'plan.md', 1, base, *NO_MUTANTS, '--', 'true', cwd=repo)
    assert first.returncode == 0, first.stderr
    link = tmp_path_factory.mktemp('links') / 'link'
    link.symlink_to(repo)
    # Bash keeps an inherited PWD only when it names the cwd, so set it to the
    # symlinked path; otherwise the shell would silently use the physical path.
    env = {**GIT_ENV, 'PWD': str(link)}
    second = run(TASK_DONE, 'plan.md', 2, base, *NO_MUTANTS, '--', 'true', cwd=link, env=env)
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
    result = run(TASK_DONE, 'alias/plan.md', 1, head(repo), *NO_MUTANTS, '--', 'true', cwd=repo)
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
    result = run(TASK_DONE, 'alias/plan.md', 1, head(repo), *NO_MUTANTS, '--', 'true', cwd=repo)
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
    result = run(TASK_DONE, 'my plan.md', 1, head(repo), *NO_MUTANTS, '--', 'true', cwd=repo)
    assert result.returncode == 0, result.stderr
    ledger = repo / '.sdd' / 'my plan' / 'progress.md'
    assert ledger.read_text().splitlines()[0] == 'Plan: my plan.md'


@pytest.mark.parametrize(
    'argv',
    [
        ('plan.md', 1, 'HEAD', 'true', 'x'),  # no '--'
        ('plan.md', 1, 'HEAD', '--'),  # fewer than 5 args
        ('plan.md', 1, 'HEAD'),
        ('plan.md', 1, 'HEAD', '--no-mutants', 'why', 'true', 'x'),  # no '--' after the reason
        ('plan.md', 1, 'HEAD', '--no-mutants', 'why', '--'),  # no command
    ],
)
def test_task_done_rejects_bad_arguments(repo, argv):
    assert run(TASK_DONE, *argv, cwd=repo).returncode == 2


def test_task_done_rejects_a_bad_base(repo):
    result = run(TASK_DONE, 'plan.md', 1, 'nope', '--', 'true', cwd=repo)
    assert result.returncode == 2
    assert 'bad BASE' in result.stderr


def test_task_done_refuses_a_repository_with_no_commit(tmp_path):
    git('init', '-q', tmp_path, cwd=tmp_path)
    (tmp_path / 'plan.md').write_text(PLAN)
    result = run(TASK_DONE, 'plan.md', 1, 'HEAD', '--', 'sh', '-c', 'touch ran', cwd=tmp_path)
    assert result.returncode == 2
    assert 'bad BASE' in result.stderr
    assert not (tmp_path / 'ran').exists()
    assert not (tmp_path / '.sdd').exists()


def test_task_done_runs_its_command_through_test_run(repo):
    base = head(repo)
    commit_work(repo)
    result = run(TASK_DONE, 'plan.md', 1, base, *NO_MUTANTS, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 0, result.stderr
    log = workspace(repo) / 'task-1-tests.log'
    lines = log.read_text().splitlines()
    assert lines[0] == 'test-run: Task 1, run 1'
    assert lines[4] == 'exit: 0'
    runs = [line for line in result.stdout.splitlines() if line.startswith('run: ')]
    assert [Path(r.removeprefix('run: ')).resolve() for r in runs] == [log.resolve()]


def test_task_done_keeps_a_failed_run_and_records_the_retry(repo):
    base = head(repo)
    fail = run(TASK_DONE, 'plan.md', 1, base, *NO_MUTANTS, '--', 'sh', '-c', 'echo boom; exit 1', cwd=repo)
    assert fail.returncode == 1
    ok = run(TASK_DONE, 'plan.md', 1, base, *NO_MUTANTS, '--', *OK_CMD, cwd=repo)
    assert ok.returncode == 0, ok.stderr
    ws = workspace(repo)
    assert 'exit: 1' in (ws / 'task-1-tests.log').read_text().splitlines()
    assert 'exit: 0' in (ws / 'task-1-tests-2.log').read_text().splitlines()
    ledger = (ws / 'progress.md').read_text().splitlines()
    assert [line for line in ledger if line.startswith('Task 1:')] == [ledger[-1]]
    assert ledger[-1].endswith('→ OK)')


def test_task_done_refuses_a_task_number_that_is_not_an_id(repo):
    result = run(TASK_DONE, 'plan.md', '../x', head(repo), '--', 'sh', '-c', 'touch ran', cwd=repo)
    assert result.returncode == 2
    assert 'test-run: bad task number' in result.stderr
    assert 'NOT recorded' not in result.stderr
    assert not (repo / 'ran').exists()
    assert not (workspace(repo) / 'progress.md').exists()


def test_task_done_keeps_a_multi_line_command_whole_in_its_ledger_line(repo):
    base = head(repo)
    commit_work(repo)
    result = run(TASK_DONE, 'plan.md', 1, base, *NO_MUTANTS, '--', 'sh', '-c', 'echo a\necho b', cwd=repo)
    assert result.returncode == 0, result.stderr
    ledger = (workspace(repo) / 'progress.md').read_text()
    assert "tests: sh -c 'echo a\necho b' → b)" in ledger


# -- task-done: the mutant gate ----------------------------------------------

CLEAN = 'caught 1, survived 0, invalid 0'


def test_task_done_records_a_task_whose_mutant_run_is_clean(repo):
    base = head(repo)
    commit_work(repo)
    write_mutants(repo, [1, 2], withdrawn=[2])
    write_run(repo, 'task-1-mutants.log', head(repo), base, CLEAN, [1])
    result = run(TASK_DONE, 'plan.md', 1, base, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 0, result.stderr
    last = (workspace(repo) / 'progress.md').read_text().splitlines()[-1]
    assert ', mutants: 1/2, tests: ' in last


def test_task_done_blocks_a_task_with_no_mutant_run(repo):
    base = head(repo)
    commit_work(repo)
    write_mutants(repo, [1])
    result = run(TASK_DONE, 'plan.md', 1, base, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 4
    assert 'no mutant run for Task 1' in result.stderr
    assert 'Task 1 NOT recorded' in result.stderr
    assert not recorded(repo)


def test_task_done_blocks_a_stale_mutant_run(repo):
    base = head(repo)
    commit_work(repo)
    write_mutants(repo, [1])
    write_run(repo, 'task-1-mutants.log', base, base, CLEAN, [1])
    result = run(TASK_DONE, 'plan.md', 1, base, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 4
    assert 'Task 1 NOT recorded' in result.stderr
    assert not recorded(repo)


@pytest.mark.parametrize(
    'outcome',
    ['caught 1, survived 1, invalid 0', 'caught 1, survived 0, invalid 1', 'baseline failed, exit 1'],
)
def test_task_done_blocks_a_run_that_is_not_all_caught(repo, outcome):
    base = head(repo)
    commit_work(repo)
    write_mutants(repo, [1])
    write_run(repo, 'task-1-mutants.log', head(repo), base, outcome, [1])
    result = run(TASK_DONE, 'plan.md', 1, base, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 4
    assert not recorded(repo)


def test_task_done_blocks_a_listed_mutant_the_run_lacks(repo):
    base = head(repo)
    commit_work(repo)
    write_mutants(repo, [1, 2])
    write_run(repo, 'task-1-mutants.log', head(repo), base, CLEAN, [1])
    result = run(TASK_DONE, 'plan.md', 1, base, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 4
    assert 'mutant 2' in result.stderr
    assert not recorded(repo)


def test_task_done_blocks_a_task_with_no_mutants_file(repo):
    base = head(repo)
    commit_work(repo)
    write_run(repo, 'task-1-mutants.log', head(repo), base, CLEAN, [1])
    result = run(TASK_DONE, 'plan.md', 1, base, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 4
    assert 'task-1-mutants.md' in result.stderr
    assert not recorded(repo)


def test_task_done_blocks_a_withdrawn_mutant_whose_patch_is_still_live(repo):
    # A withdrawn mutant's patch is renamed .patch.withdrawn. A Withdrawn line
    # beside a live patch is a stray line that could excuse a mutant never run.
    base = head(repo)
    commit_work(repo)
    write_mutants(repo, [1, 2], withdrawn=[2])
    write_run(repo, 'task-1-mutants.log', head(repo), base, CLEAN, [1])
    (workspace(repo) / 'task-1-mutant-2.patch').write_text('a demo patch\n')
    result = run(TASK_DONE, 'plan.md', 1, base, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 4
    assert 'task-1-mutant-2.patch' in result.stderr
    assert 'Task 1 NOT recorded' in result.stderr
    assert not recorded(repo)


def test_task_done_reads_the_newest_mutant_run_by_number(repo):
    base = head(repo)
    commit_work(repo)
    write_mutants(repo, [1])
    write_run(repo, 'task-1-mutants-2.log', head(repo), base, CLEAN, [1])
    write_run(repo, 'task-1-mutants-10.log', head(repo), base, 'caught 0, survived 1, invalid 0', [1])
    result = run(TASK_DONE, 'plan.md', 1, base, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 4
    assert 'task-1-mutants-10.log' in result.stderr
    assert not recorded(repo)


def test_task_done_ignores_another_tasks_mutant_run(repo):
    base = head(repo)
    commit_work(repo)
    write_mutants(repo, [1])
    write_run(repo, 'task-10-mutants.log', head(repo), base, CLEAN, [1])
    result = run(TASK_DONE, 'plan.md', 1, base, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 4
    assert 'no mutant run for Task 1' in result.stderr
    assert not recorded(repo)


def insert_after(repo, name, anchor, *lines):
    '''Add lines to a run file, right after its first line that equals the anchor.'''
    run_file = workspace(repo) / name
    out = []
    done = False
    for line in run_file.read_text().splitlines():
        out.append(line)
        if not done and line == anchor:
            out.extend(lines)
            done = True
    assert done, f'no {anchor!r} line in {name}'
    run_file.write_text('\n'.join(out) + '\n')


def test_task_done_blocks_a_run_with_no_base_line(repo):
    base = head(repo)
    commit_work(repo)
    write_mutants(repo, [1])
    write_run(repo, 'task-1-mutants.log', head(repo), None, CLEAN, [1])
    result = run(TASK_DONE, 'plan.md', 1, base, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 4
    assert 'the mutant run has no base: line' in result.stderr
    assert not recorded(repo)


def test_task_done_blocks_a_run_at_another_base(repo):
    base = head(repo)
    commit_work(repo)
    write_mutants(repo, [1])
    write_run(repo, 'task-1-mutants.log', head(repo), head(repo), CLEAN, [1])
    result = run(TASK_DONE, 'plan.md', 1, base, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 4
    assert f'the mutant run is at base {head(repo)}, not BASE {base}' in result.stderr
    assert not recorded(repo)


def test_task_done_blocks_a_run_with_no_revert_line(repo):
    base = head(repo)
    commit_work(repo)
    write_mutants(repo, [1])
    write_run(repo, 'task-1-mutants.log', head(repo), base, CLEAN, [1], revert=None)
    result = run(TASK_DONE, 'plan.md', 1, base, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 4
    assert 'the mutant run has no revert: line' in result.stderr
    assert not recorded(repo)


def test_task_done_records_a_run_whose_revert_ran(repo):
    base = head(repo)
    commit_work(repo)
    write_mutants(repo, [1])
    revert = 'revert: ran, exit 1, failed 1, not loaded 0, skipped 0, passed 3'
    write_run(repo, 'task-1-mutants.log', head(repo), base, CLEAN, [1], revert=revert)
    result = run(TASK_DONE, 'plan.md', 1, base, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 0, result.stderr
    assert recorded(repo)


def test_task_done_matches_a_short_base(repo):
    base = head(repo)
    commit_work(repo)
    write_mutants(repo, [1])
    write_run(repo, 'task-1-mutants.log', head(repo), base, CLEAN, [1])
    result = run(TASK_DONE, 'plan.md', 1, base[:7], '--', *OK_CMD, cwd=repo)
    assert result.returncode == 0, result.stderr
    assert recorded(repo)


def test_task_done_reads_base_and_revert_from_the_header_only(repo):
    base = head(repo)
    commit_work(repo)
    write_mutants(repo, [1])
    write_run(repo, 'task-1-mutants.log', head(repo), None, CLEAN, [1], revert=None)
    insert_after(repo, 'task-1-mutants.log', '1 passed', f'base: {base}', NONE_REVERT)
    result = run(TASK_DONE, 'plan.md', 1, base, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 4
    assert 'no base: line' in result.stderr
    assert not recorded(repo)


# The plan's tests above pin the three refusals. The tests below add the
# shapes the spec's rules also cover.


def test_task_done_matches_a_short_base_in_the_run(repo):
    base = head(repo)
    commit_work(repo)
    write_mutants(repo, [1])
    write_run(repo, 'task-1-mutants.log', head(repo), base[:7], CLEAN, [1])
    result = run(TASK_DONE, 'plan.md', 1, base, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 0, result.stderr
    assert recorded(repo)


def test_task_done_reads_the_revert_line_from_the_header_only(repo):
    # The base: line is right, so only the revert: reader can be fooled.
    base = head(repo)
    commit_work(repo)
    write_mutants(repo, [1])
    write_run(repo, 'task-1-mutants.log', head(repo), base, CLEAN, [1], revert=None)
    insert_after(repo, 'task-1-mutants.log', '1 passed', NONE_REVERT)
    result = run(TASK_DONE, 'plan.md', 1, base, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 4
    assert 'the mutant run has no revert: line' in result.stderr
    assert not recorded(repo)


@pytest.mark.parametrize('missing', ['base', 'revert'])
def test_task_done_ignores_base_and_revert_lines_inside_the_command(repo, missing):
    # A command that spans lines puts its lines between command: and head:.
    # The header lacks one line and the command holds a correct one.
    base = head(repo)
    commit_work(repo)
    write_mutants(repo, [1])
    if missing == 'base':
        write_run(repo, 'task-1-mutants.log', head(repo), None, CLEAN, [1])
        insert_after(repo, 'task-1-mutants.log', 'command: sh -c true', f'base: {base}')
    else:
        write_run(repo, 'task-1-mutants.log', head(repo), base, CLEAN, [1], revert=None)
        insert_after(repo, 'task-1-mutants.log', 'command: sh -c true', NONE_REVERT)
    result = run(TASK_DONE, 'plan.md', 1, base, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 4
    assert f'the mutant run has no {missing}: line' in result.stderr
    assert not recorded(repo)


@pytest.mark.parametrize(
    'revert',
    [
        'revert: ran, exit 1, no report',
        'revert: timeout after 300s',
        'revert: not applied: the revert patch does not apply',
        NONE_REVERT,
    ],
)
def test_task_done_records_a_run_with_any_revert_form(repo, revert):
    # task-done checks that the line is there and never reads what it says.
    base = head(repo)
    commit_work(repo)
    write_mutants(repo, [1])
    write_run(repo, 'task-1-mutants.log', head(repo), base, CLEAN, [1], revert=revert)
    result = run(TASK_DONE, 'plan.md', 1, base, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 0, result.stderr
    assert recorded(repo)


UNCAUGHT = 'caught 1, survived 1, invalid 0'


@pytest.mark.parametrize(
    ('stale_head', 'run_base', 'revert', 'result', 'refusal'),
    [
        (True, None, None, CLEAN, 'not HEAD'),
        (False, None, None, CLEAN, 'the mutant run has no base: line'),
        (False, 'other', None, CLEAN, 'the mutant run is at base'),
        (False, 'base', None, UNCAUGHT, 'the mutant run has no revert: line'),
        (False, None, NONE_REVERT, UNCAUGHT, 'the mutant run has no base: line'),
        (False, 'other', NONE_REVERT, UNCAUGHT, 'the mutant run is at base'),
    ],
    ids=[
        'head-before-base',
        'no-base-before-no-revert',
        'other-base-before-no-revert',
        'no-revert-before-result',
        'no-base-before-result',
        'other-base-before-result',
    ],
)
def test_task_done_refuses_in_the_order_head_base_revert_result(repo, stale_head, run_base, revert, result, refusal):
    base = head(repo)
    commit_work(repo)
    write_mutants(repo, [1])
    run_base = {None: None, 'base': base, 'other': head(repo)}[run_base]
    write_run(repo, 'task-1-mutants.log', base if stale_head else head(repo), run_base, result, [1], revert=revert)
    done = run(TASK_DONE, 'plan.md', 1, base, '--', *OK_CMD, cwd=repo)
    assert done.returncode == 4
    assert refusal in done.stderr
    assert not recorded(repo)


@pytest.mark.parametrize('refusal', ['no-base', 'other-base', 'no-revert'])
def test_task_done_names_the_run_in_each_new_refusal(repo, refusal):
    # Each goes through refuse: the reason, then the run's path, and no record.
    base = head(repo)
    commit_work(repo)
    write_mutants(repo, [1])
    run_base = {'no-base': None, 'other-base': head(repo), 'no-revert': base}[refusal]
    revert = None if refusal == 'no-revert' else NONE_REVERT
    write_run(repo, 'task-1-mutants.log', head(repo), run_base, CLEAN, [1], revert=revert)
    result = run(TASK_DONE, 'plan.md', 1, base, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 4
    assert '; Task 1 NOT recorded (mutant run: ' in result.stderr
    assert result.stderr.rstrip().endswith('/task-1-mutants.log)')
    assert not recorded(repo)


def test_task_done_refuses_a_base_that_is_not_a_commit(repo):
    # A tree passes the early BASE check, but it names no commit to compare.
    base = head(repo)
    commit_work(repo)
    write_mutants(repo, [1])
    write_run(repo, 'task-1-mutants.log', head(repo), base, CLEAN, [1])
    tree = git('rev-parse', 'HEAD^{tree}', cwd=repo).stdout.strip()
    result = run(TASK_DONE, 'plan.md', 1, tree, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 4
    assert f'the mutant run is at base {base}, not BASE {tree}' in result.stderr
    assert not recorded(repo)


def test_task_done_refuses_a_run_base_that_names_no_commit(repo):
    base = head(repo)
    commit_work(repo)
    write_mutants(repo, [1])
    write_run(repo, 'task-1-mutants.log', head(repo), 'not-a-commit', CLEAN, [1])
    result = run(TASK_DONE, 'plan.md', 1, base, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 4
    assert f'the mutant run is at base not-a-commit, not BASE {base}' in result.stderr
    assert not recorded(repo)


def test_task_done_names_a_short_base_in_full_when_it_refuses(repo):
    base = head(repo)
    commit_work(repo)
    write_mutants(repo, [1])
    write_run(repo, 'task-1-mutants.log', head(repo), head(repo), CLEAN, [1])
    result = run(TASK_DONE, 'plan.md', 1, base[:7], '--', *OK_CMD, cwd=repo)
    assert result.returncode == 4
    assert f'the mutant run is at base {head(repo)}, not BASE {base};' in result.stderr
    assert not recorded(repo)


def test_task_done_refuses_when_neither_base_names_a_commit(repo):
    # Two names that resolve to nothing are not two names for one commit.
    base = head(repo)
    commit_work(repo)
    write_mutants(repo, [1])
    write_run(repo, 'task-1-mutants.log', head(repo), 'not-a-commit', CLEAN, [1])
    tree = git('rev-parse', 'HEAD^{tree}', cwd=repo).stdout.strip()
    result = run(TASK_DONE, 'plan.md', 1, tree, '--', *OK_CMD, cwd=repo)
    assert result.returncode == 4
    assert 'the mutant run is at base not-a-commit' in result.stderr
    assert not recorded(repo)


def test_task_done_rejects_no_mutants_without_a_reason(repo):
    cmd = ['sh', '-c', 'touch ran']
    result = run(TASK_DONE, 'plan.md', 1, head(repo), '--no-mutants', '', '--', *cmd, cwd=repo)
    assert result.returncode == 2
    assert '[--no-mutants REASON]' in result.stderr
    assert not (repo / 'ran').exists()
    assert not recorded(repo)


# Task 1's demo module and tests from the subagent-driven-development suite.
PY_ENV = {**GIT_ENV, 'PYTHONDONTWRITEBYTECODE': '1'}
PYTEST = [sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', 'test_calc.py']

CALC = 'def add(a, b):\n    return a + b\n\n\ndef neg(a):\n    return -a\n'
TEST_CALC = '''from calc import add, neg


def test_add_small():
    assert add(1, 2) == 3


def test_add_large():
    assert add(100, 200) == 300


def test_neg():
    assert neg(2) == -2
'''


def test_task_done_accepts_a_run_that_mutant_run_wrote(repo):
    base = head(repo)
    (repo / 'calc.py').write_text(CALC)
    (repo / 'test_calc.py').write_text(TEST_CALC)
    git('add', 'calc.py', 'test_calc.py', cwd=repo)
    git('commit', '-q', '-m', 'calc', cwd=repo)
    # sdd-workspace writes the self-ignoring .sdd/.gitignore, so the patch is
    # never an untracked file and mutant-run finds a clean tree.
    made = run(SDD_WORKSPACE, 'plan.md', cwd=repo)
    assert made.returncode == 0, made.stderr
    (repo / 'calc.py').write_text(CALC.replace('return a + b', 'return a - b'))
    patch = git('diff', '--', 'calc.py', cwd=repo).stdout
    assert patch
    git('checkout', '--', 'calc.py', cwd=repo)
    (workspace(repo) / 'task-1-mutant-1.patch').write_text(patch)
    mutants = run(MUTANT_RUN, 'plan.md', 1, base, '--', *PYTEST, cwd=repo, env=PY_ENV)
    assert mutants.returncode == 0, mutants.stdout + mutants.stderr
    write_mutants(repo, [1])
    result = run(TASK_DONE, 'plan.md', 1, base, '--', *PYTEST, cwd=repo, env=PY_ENV)
    assert result.returncode == 0, result.stdout + result.stderr
    last = (workspace(repo) / 'progress.md').read_text().splitlines()[-1]
    assert 'mutants: 1/1' in last
