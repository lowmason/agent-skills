"""Tests for the five bundled bash scripts — run from this directory.

cd skills/subagent-driven-development/scripts && uv run --with pytest \
  python -m pytest -q

These are bash, not Python, so each test drives the script as a subprocess and
asserts on exit code, stdout, and written files. That keeps this repo on one test
runner instead of adding bats/shunit2 for five files.
"""

import os
import re
import signal
import subprocess
import time
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent
SDD_REPO = SCRIPTS / 'sdd-repo'
WORKSPACE = SCRIPTS / 'sdd-workspace'
TASK_BRIEF = SCRIPTS / 'task-brief'
REVIEW_PACKAGE = SCRIPTS / 'review-package'
TEST_RUN = SCRIPTS / 'test-run'

# Sanitised so the suite doesn't inherit the user's global/system git config
# (commit.gpgsign, core.hooksPath, init.templateDir, ...). Without this, a
# setup `git commit` can fail silently and the real cause surfaces as a
# confusing downstream assertion on the script under test.
GIT_ENV = {**os.environ, 'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_NOSYSTEM': '1'}

NEW_PROJECT = "If this is a new project, run 'git init' and make a first commit, then rerun."

PLAN = """\
# Demo Plan

## Global Constraints

- Python 3.13 via uv.
- Single quotes over double.

---

### Task 1: First thing

- [ ] **Step 1: do it**

```markdown
### Task 99: this heading is inside a fence and is content, not a boundary
```

#### Sub-step detail

A heading deeper than the task's own is content, not a boundary.

### Task 2: Second thing

- [ ] **Step 1: other**

### Notes

A same-level heading that is not a Task still ends Task 2's brief.

## Verification

This trailing section must not leak into Task 2's brief.
"""

# Global Constraints with ### subsections and plan-wide ## siblings after it:
# the shape of a real plan whose spec quotes, decisions and project rules sat
# under seven ### headings that every brief lost.
SUBSECTIONED_PLAN = """\
# Subsectioned Plan

## Global Constraints

Every task's requirements include this section.

### Global Constraints from the spec, verbatim

- Window size is 128 tokens.

```markdown
## 4. Design
```

### Project rules

- Single quotes over double.

## Workspace

Worktree path for this plan.

## Pre-flight

- [ ] **Step 1: Confirm the workspace**

### Task 1: First thing

- [ ] **Step 1: do it**
"""


def run(*argv, cwd=None, env=GIT_ENV):
    return subprocess.run(
        [str(a) for a in argv], cwd=cwd, capture_output=True, text=True, env=env
    )


def outside_env(path):
    '''GIT_ENV with git's upward search stopped at path, so no repository above it is found.'''
    return {**GIT_ENV, 'GIT_CEILING_DIRECTORIES': str(path)}


def git(*argv, cwd):
    """Run a git command that arranges test state (not the call under test)
    and assert it succeeded — a silent failure here must not surface as a
    confusing assertion failure against sdd-workspace/task-brief/review-package."""
    result = run('git', *argv, cwd=cwd)
    assert result.returncode == 0, result.stderr
    return result


@pytest.fixture
def repo(tmp_path):
    """A throwaway git repo containing the demo plan."""
    git('init', '-q', tmp_path, cwd=tmp_path)
    git('config', 'user.email', 't@example.invalid', cwd=tmp_path)
    git('config', 'user.name', 'T', cwd=tmp_path)
    (tmp_path / 'plan.md').write_text(PLAN)
    return tmp_path


# ── sdd-repo ─────────────────────────────────────────────────────────────


def test_sdd_repo_prints_the_top_level_from_a_subdirectory(repo):
    (repo / 'sub').mkdir()
    result = run(SDD_REPO, cwd=repo / 'sub')
    assert result.returncode == 0, result.stderr
    assert Path(result.stdout.strip()).resolve() == repo.resolve()


def test_sdd_repo_with_commit_refuses_a_repository_with_no_commit(repo):
    assert run(SDD_REPO, cwd=repo).returncode == 0
    result = run(SDD_REPO, '--with-commit', cwd=repo)
    assert result.returncode == 2
    first, second = result.stderr.splitlines()[:2]
    assert first.startswith('SDD scripts must run from inside the git working tree')
    assert first.endswith(NEW_PROJECT)
    assert second.startswith('git said: fatal:')


def test_sdd_repo_refuses_outside_a_working_tree(tmp_path):
    result = run(SDD_REPO, cwd=tmp_path, env=outside_env(tmp_path))
    assert result.returncode == 2
    assert NEW_PROJECT in result.stderr
    assert 'git said: fatal: not a git repository' in result.stderr


def test_sdd_repo_rejects_any_other_argument(repo):
    result = run(SDD_REPO, '-C', repo, cwd=repo)
    assert result.returncode == 2
    assert 'usage: sdd-repo [--with-commit]' in result.stderr


# ── sdd-workspace ────────────────────────────────────────────────────────


def test_workspace_is_created_inside_the_working_tree(repo):
    """Not under .git/ — Claude Code denies agent writes to that protected path,
    which would block an implementer subagent from writing its report."""
    result = run(WORKSPACE, repo / 'plan.md', cwd=repo)
    assert result.returncode == 0
    printed = Path(result.stdout.strip())
    assert printed.resolve() == (repo / '.sdd' / 'plan').resolve()
    assert '.git' not in printed.parts


def test_workspace_ignores_itself_so_artifacts_never_reach_git_status(repo):
    run(WORKSPACE, repo / 'plan.md', cwd=repo)
    assert (repo / '.sdd' / '.gitignore').read_text() == '*\n'
    # The guard sits at the .sdd parent, not inside the per-plan directory,
    # so one guard covers every sibling plan's workspace.
    assert not (repo / '.sdd' / 'plan' / '.gitignore').exists()
    (repo / '.sdd' / 'plan' / 'task-1-brief.md').write_text('scratch')
    status = run('git', 'status', '--short', cwd=repo).stdout
    assert '.sdd' not in status


def test_workspace_leaves_a_committed_gitignore_alone(repo):
    """A repository may commit its own .sdd/.gitignore, for instance to keep
    progress ledgers under version control. Writing '*' on every run
    reverted that file in the working tree."""
    own = '*\n!.gitignore\n!*/\n!*/progress.md\n'
    (repo / '.sdd').mkdir()
    (repo / '.sdd' / '.gitignore').write_text(own)
    git('add', '.sdd/.gitignore', 'plan.md', cwd=repo)
    git('commit', '-qm', 'version the ledgers', cwd=repo)
    result = run(WORKSPACE, repo / 'plan.md', cwd=repo)
    assert result.returncode == 0
    assert (repo / '.sdd' / '.gitignore').read_text() == own
    status = run('git', 'status', '--porcelain', '--', '.sdd/.gitignore', cwd=repo)
    assert status.stdout == ''


def test_workspace_separates_two_plans_in_one_working_tree(repo):
    """The bug this change exists to fix: a flat workspace let a second plan
    read the first plan's ledger as its own progress and skip live tasks."""
    (repo / 'other.md').write_text(PLAN)
    first = Path(run(WORKSPACE, repo / 'plan.md', cwd=repo).stdout.strip())
    second = Path(run(WORKSPACE, repo / 'other.md', cwd=repo).stdout.strip())
    assert first.resolve() != second.resolve()
    (first / 'progress.md').write_text('Task 1: complete\n')
    assert not (second / 'progress.md').exists()


def test_workspace_is_stable_for_one_plan(repo):
    """Same plan, same directory — a resuming controller must find its ledger."""
    first = run(WORKSPACE, repo / 'plan.md', cwd=repo).stdout.strip()
    second = run(WORKSPACE, repo / 'plan.md', cwd=repo).stdout.strip()
    assert Path(first).resolve() == Path(second).resolve()


def test_workspace_is_named_from_the_plan_basename_alone(repo):
    """Real plans live at specs/plans/<id>-<name>.md, but every other workspace
    test passes a root-level plan.md — where stripping the directory is a no-op.
    A regression that kept the path components would resolve the workspace to
    .sdd/specs/plans/<id>-<name>/ and still pass all of them."""
    nested = repo / 'specs' / 'plans' / '22-sdd-hardening.md'
    nested.parent.mkdir(parents=True)
    nested.write_text(PLAN)
    # Relative, the form a controller running from the repo root actually
    # types: an absolute path would fail a path-leaking bug for the wrong
    # reason (a doubled absolute path), not on the slug.
    result = run(WORKSPACE, 'specs/plans/22-sdd-hardening.md', cwd=repo)
    assert result.returncode == 0
    printed = Path(result.stdout.strip())
    assert printed.resolve() == (repo / '.sdd' / '22-sdd-hardening').resolve()
    # Asserted separately because this is the half that fails when the
    # directory components survive into the workspace name.
    assert printed.resolve().parent == (repo / '.sdd').resolve()


@pytest.mark.parametrize(
    'argv, message',
    [
        ([], 'usage: sdd-workspace'),
        (['plan.md', 'extra'], 'usage: sdd-workspace'),
        (['nosuch.md'], 'no such plan file'),
        # A directory reaches the same rejection as a missing file: [ -f ]
        # is false for both. This is the case that makes the slug guard for
        # '.' unreachable, and it is the behavior worth pinning — a caller
        # who passes a directory must not get a workspace named after it.
        (['.'], 'no such plan file'),
    ],
)
def test_workspace_rejects_bad_arguments(repo, argv, message):
    result = run(WORKSPACE, *argv, cwd=repo)
    assert result.returncode == 2
    assert message in result.stderr


def test_workspace_refuses_outside_a_working_tree_and_writes_nothing(tmp_path):
    (tmp_path / 'plan.md').write_text(PLAN)
    result = run(WORKSPACE, 'plan.md', cwd=tmp_path, env=outside_env(tmp_path))
    assert result.returncode == 2
    assert NEW_PROJECT in result.stderr
    assert not (tmp_path / '.sdd').exists()


# ── task-brief ───────────────────────────────────────────────────────────


def test_task_brief_prepends_global_constraints(repo):
    out = repo / 'brief.md'
    result = run(TASK_BRIEF, repo / 'plan.md', 1, out, cwd=repo)
    assert result.returncode == 0
    body = out.read_text()
    assert body.index('## Global Constraints') < body.index('### Task 1')
    assert 'Single quotes over double.' in body


def test_task_brief_keeps_global_constraints_subsections(repo):
    """Global Constraints may hold ### subsections: only a heading at its own
    level or shallower ends it. An any-heading terminator kept the first four
    lines of a real plan's section and dropped all seven subsections from
    every brief. The second subsection carries two more
    checks: the fenced '## 4. Design' before it must not end the section,
    and the first subsection's title, which also says 'Global Constraints',
    must not restart the section at the deeper level."""
    (repo / 'subsectioned.md').write_text(SUBSECTIONED_PLAN)
    out = repo / 'brief.md'
    result = run(TASK_BRIEF, repo / 'subsectioned.md', 1, out, cwd=repo)
    assert result.returncode == 0
    body = out.read_text()
    assert '### Global Constraints from the spec, verbatim' in body
    assert 'Window size is 128 tokens.' in body
    assert '### Project rules' in body
    assert 'Single quotes over double.' in body
    # A same-level sibling ends the section, so the plan-wide ## sections
    # after it stay out. Without these, a terminator that never fired would pass.
    assert 'Worktree path' not in body
    assert 'Confirm the workspace' not in body
    assert body.count('### Task 1') == 1
    assert body.index('Single quotes over double.') < body.index('### Task 1')


def test_task_brief_ends_flat_global_constraints_at_a_deeper_task_heading(repo):
    """The writing-plans template puts '### Task 1' directly under a flat
    '## Global Constraints'. A level-only terminator would run the section
    through every task into each brief, so any Task heading also ends it.
    Task 2's brief is the sharp case: Task 1 must be absent, and Task 2 must
    appear once, not once from the section and again as the task itself."""
    out = repo / 'brief.md'
    result = run(TASK_BRIEF, repo / 'plan.md', 2, out, cwd=repo)
    assert result.returncode == 0
    body = out.read_text()
    assert 'Single quotes over double.' in body
    assert '### Task 1' not in body
    assert body.count('### Task 2') == 1


def test_task_brief_keeps_a_fenced_task_heading_as_content(repo):
    """A ```-fenced '### Task 99' is example text, not a section boundary.
    If fence tracking breaks, Task 1's brief is truncated mid-step."""
    out = repo / 'brief.md'
    run(TASK_BRIEF, repo / 'plan.md', 1, out, cwd=repo)
    body = out.read_text()
    assert 'Task 99' in body
    assert '### Task 2' not in body


def test_task_brief_keeps_a_deeper_sub_heading_as_content(repo):
    """A '#### Sub-step' under a '### Task' is content: only a heading at the
    task's own level or shallower ends the section. Unlike the fenced
    '### Task 99', this exercises the heading-level comparison itself, not
    the fence tracker. The sub-heading's body is asserted alongside the
    heading and the next task's boundary: a truncation that printed the
    sub-heading and stopped there would satisfy the other two on its own."""
    out = repo / 'brief.md'
    run(TASK_BRIEF, repo / 'plan.md', 1, out, cwd=repo)
    body = out.read_text()
    assert '#### Sub-step detail' in body
    assert "A heading deeper than the task's own" in body
    assert '### Task 2' not in body


def test_task_brief_excludes_trailing_plan_sections(repo):
    """The last task must not absorb '## Verification' and everything after it.

    Also asserts Task 2's own body (not just its heading) survived: a
    regression that truncated the brief right after printing the heading
    would otherwise leave this test green. Not hypothetical — task-brief
    truncated a real 234-line brief to 70 lines earlier during this plan's
    execution, because a fence nested inside another fence closed the outer
    fence early.
    """
    out = repo / 'brief.md'
    run(TASK_BRIEF, repo / 'plan.md', 2, out, cwd=repo)
    body = out.read_text()
    assert '### Task 2: Second thing' in body
    assert 'Step 1: other' in body
    assert 'must not leak' not in body


def test_task_brief_ends_at_a_same_level_heading_that_is_not_a_task(repo):
    """'### Notes' sits at Task 2's own level but is not a Task heading. Only the
    `<=` in task-brief's heading-level test ends the section there: with `<` the
    heading and its text leak into the brief, and nothing else in this suite
    notices, because '## Verification' is shallower and ends it either way."""
    out = repo / 'brief.md'
    run(TASK_BRIEF, repo / 'plan.md', 2, out, cwd=repo)
    body = out.read_text()
    assert 'Step 1: other' in body
    assert '### Notes' not in body
    assert 'still ends Task 2' not in body


def test_task_brief_exits_3_on_a_missing_task(repo):
    result = run(TASK_BRIEF, repo / 'plan.md', 42, repo / 'brief.md', cwd=repo)
    assert result.returncode == 3
    assert 'task 42 not found' in result.stderr


def test_task_brief_exits_2_on_bad_arguments(repo):
    assert run(TASK_BRIEF, repo / 'plan.md', cwd=repo).returncode == 2
    missing = run(TASK_BRIEF, repo / 'nope.md', 1, repo / 'b.md', cwd=repo)
    assert missing.returncode == 2
    assert 'no such plan file' in missing.stderr


def test_task_brief_exits_2_on_too_many_arguments(repo):
    """The other half of the arity guard: a fourth argument is a caller bug,
    not something to silently drop on the way to a default OUTFILE."""
    result = run(TASK_BRIEF, repo / 'plan.md', 1, repo / 'b.md', 'extra', cwd=repo)
    assert result.returncode == 2
    assert 'usage: task-brief' in result.stderr


def test_task_brief_writes_to_and_prints_the_default_workspace_path(repo):
    """No OUTFILE given — the production path every real invocation takes,
    and the only place task-brief actually calls sdd-workspace. Untested
    until now: all other task-brief tests pass an explicit OUTFILE."""
    result = run(TASK_BRIEF, repo / 'plan.md', 2, cwd=repo)
    assert result.returncode == 0

    match = re.match(r'^wrote (.+): \d', result.stdout.strip())
    assert match, f'unexpected stdout: {result.stdout!r}'
    printed = Path(match.group(1))
    expected = repo / '.sdd' / 'plan' / 'task-2-brief.md'
    assert printed.resolve() == expected.resolve()

    body = expected.resolve().read_text()
    assert '### Task 2: Second thing' in body
    assert 'Step 1: other' in body

    assert (repo / '.sdd' / '.gitignore').read_text() == '*\n'


IDS_PLAN = """\
# Ids Plan

### Task 2: Two

Body of 2.

### Task 2.1: Two point one

Body of 2.1.

### Task 6: Six

Body of 6.

### Task 6b: Six b

Body of 6b.

### Task A1: A one

Body of A1.

### Task 7: Seven

Body of 7.

#### Task 7a: Seven a

Body of 7a.

#### Task 7b: Seven b

Body of 7b.
"""

TAREA_PLAN = """\
# Tarea Plan

### Tarea 1: Uno

Cuerpo.
"""

LETTER_GC_PLAN = """\
# Letter Plan

## Global Constraints

- Rule X.

### Task A1: First

Body of A1.

### Task A2: Second

Body of A2.
"""

# Line 9 opens a fence inside Task 2 that never closes.
UNCLOSED_PLAN = """\
# Unclosed Plan

### Task 1: First

Body of 1.

### Task 2: Second

```bash
echo open

### Task 3: Third

Body of 3.
"""

# Line 11, the last line, opens a fence that hides no task heading.
STRAY_PLAN = """\
# Stray Plan

### Task 1: First

Body of 1.

### Task 2: Second

Body of 2.

```
"""


def brief(repo, name, text, n, out=None):
    '''Write text to repo/name and run task-brief on it, with out as OUTFILE when given.'''
    (repo / name).write_text(text)
    return run(TASK_BRIEF, repo / name, n, *([out] if out else []), cwd=repo)


@pytest.mark.parametrize('n, own, other', [('2', 'Body of 2.', 'Task 2.1'), ('6', 'Body of 6.', 'Task 6b')])
def test_task_brief_does_not_take_a_same_level_task_whose_id_extends_the_number(repo, n, own, other):
    out = repo / 'brief.md'
    result = brief(repo, 'ids.md', IDS_PLAN, n, out)
    assert result.returncode == 0, result.stderr
    assert own in out.read_text()
    assert other not in out.read_text()


@pytest.mark.parametrize('n', ['A1', '6b', '2.1'])
def test_task_brief_finds_every_id_form(repo, n):
    out = repo / 'brief.md'
    result = brief(repo, 'ids.md', IDS_PLAN, n, out)
    assert result.returncode == 0, result.stderr
    body = out.read_text()
    assert f'Body of {n}.' in body
    assert body.count('### Task') == 1


def test_task_brief_reads_the_task_number_as_a_string_not_a_regex(repo):
    out = repo / 'brief.md'
    result = brief(repo, 'ids.md', IDS_PLAN, '6.', out)
    assert result.returncode == 3
    assert 'task 6. not found' in result.stderr
    assert not out.exists()


def test_task_brief_keeps_a_deeper_sub_task_in_its_brief(repo):
    out = repo / 'brief.md'
    result = brief(repo, 'ids.md', IDS_PLAN, '7', out)
    assert result.returncode == 0, result.stderr
    assert '#### Task 7a: Seven a' in out.read_text()
    assert 'Body of 7a.' in out.read_text()
    assert 'Body of 7b.' in out.read_text()


def test_task_brief_lists_headings_shaped_like_tasks_when_none_say_task(repo):
    result = brief(repo, 'tarea.md', TAREA_PLAN, '1', repo / 'brief.md')
    assert result.returncode == 3
    assert '  ### Tarea 1: Uno' in result.stderr
    assert result.stderr.index('no task headings found') < result.stderr.index('task 1 not found')


def test_task_brief_ends_global_constraints_at_a_letter_first_task_heading(repo):
    out = repo / 'brief.md'
    result = brief(repo, 'letter.md', LETTER_GC_PLAN, 'A2', out)
    assert result.returncode == 0, result.stderr
    body = out.read_text()
    assert 'Rule X.' in body
    assert 'Body of A1.' not in body
    assert body.count('### Task A2') == 1


def test_task_brief_refuses_a_task_that_an_unclosed_fence_runs_past(repo):
    stale = repo / '.sdd' / 'unclosed' / 'task-2-brief.md'
    stale.parent.mkdir(parents=True)
    stale.write_text('stale brief\n')
    result = brief(repo, 'unclosed.md', UNCLOSED_PLAN, '2')
    assert result.returncode == 4
    assert 'the code fence opened at line 9 of' in result.stderr
    assert 'close that fence in the plan and rerun' in result.stderr
    assert not stale.exists()
    assert 'wrote' not in result.stdout


def test_task_brief_names_an_unclosed_fence_that_hides_the_requested_task(repo):
    result = brief(repo, 'unclosed.md', UNCLOSED_PLAN, '3', repo / 'brief.md')
    assert result.returncode == 3
    assert 'line 9' in result.stderr
    assert result.stderr.index('never closes') < result.stderr.index('task 3 not found')


def test_task_brief_is_unaffected_by_an_unclosed_fence_after_the_task(repo):
    out = repo / 'brief.md'
    result = brief(repo, 'unclosed.md', UNCLOSED_PLAN, '1', out)
    assert result.returncode == 0, result.stderr
    assert 'never closes' not in result.stderr
    assert 'Body of 1.' in out.read_text()


def test_task_brief_warns_on_a_stray_fence_that_hides_no_task(repo):
    out = repo / 'brief.md'
    result = brief(repo, 'stray.md', STRAY_PLAN, '2', out)
    assert result.returncode == 0, result.stderr
    assert 'warning: the code fence opened at line 11 of' in result.stderr
    assert 'it hides no Task heading, so this brief is complete' in result.stderr
    assert 'Body of 2.' in out.read_text()


# ── review-package ───────────────────────────────────────────────────────


def test_review_package_carries_commits_stat_and_diff(repo):
    (repo / 'a.txt').write_text('one\n')
    git('add', 'a.txt', 'plan.md', cwd=repo)
    git('commit', '-qm', 'first', cwd=repo)
    (repo / 'a.txt').write_text('one\ntwo\n')
    git('add', 'a.txt', cwd=repo)
    git('commit', '-qm', 'second', cwd=repo)

    out = repo / 'package.diff'
    result = run(REVIEW_PACKAGE, repo / 'plan.md', 'HEAD~1', 'HEAD', out, cwd=repo)
    assert result.returncode == 0
    assert '1 commit(s)' in result.stdout
    body = out.read_text()
    for heading in ('# Review package:', '## Commits', '## Files changed', '## Diff'):
        assert heading in body
    assert 'second' in body
    assert '+two' in body
    assert 'first' not in body.split('## Commits')[1].split('## Files changed')[0]


def test_review_package_rejects_an_unresolvable_revision(repo):
    (repo / 'a.txt').write_text('one\n')
    git('add', 'a.txt', 'plan.md', cwd=repo)
    git('commit', '-qm', 'first', cwd=repo)
    result = run(REVIEW_PACKAGE, repo / 'plan.md', 'nosuchrev', 'HEAD', repo / 'p.diff', cwd=repo)
    assert result.returncode == 2
    assert 'bad BASE' in result.stderr


def test_review_package_rejects_an_unresolvable_head(repo):
    """BASE and HEAD are verified separately and report separately: a valid
    BASE must not excuse an unresolvable HEAD."""
    (repo / 'a.txt').write_text('one\n')
    git('add', 'a.txt', 'plan.md', cwd=repo)
    git('commit', '-qm', 'first', cwd=repo)
    result = run(REVIEW_PACKAGE, repo / 'plan.md', 'HEAD', 'nosuchrev', repo / 'p.diff', cwd=repo)
    assert result.returncode == 2
    assert 'bad HEAD' in result.stderr


def test_review_package_writes_to_and_prints_the_default_workspace_path(repo):
    """No OUTFILE given — the production path every real invocation takes,
    and the only place review-package actually calls sdd-workspace. Untested
    until now: the other review-package tests pass an explicit OUTFILE."""
    (repo / 'a.txt').write_text('one\n')
    git('add', 'a.txt', 'plan.md', cwd=repo)
    git('commit', '-qm', 'first', cwd=repo)
    (repo / 'a.txt').write_text('one\ntwo\n')
    git('add', 'a.txt', cwd=repo)
    git('commit', '-qm', 'second', cwd=repo)

    shortbase = run('git', 'rev-parse', '--short', 'HEAD~1', cwd=repo).stdout.strip()
    shorthead = run('git', 'rev-parse', '--short', 'HEAD', cwd=repo).stdout.strip()

    result = run(REVIEW_PACKAGE, repo / 'plan.md', 'HEAD~1', 'HEAD', cwd=repo)
    assert result.returncode == 0

    match = re.match(r'^wrote (.+): \d', result.stdout.strip())
    assert match, f'unexpected stdout: {result.stdout!r}'
    printed = Path(match.group(1))
    expected = repo / '.sdd' / 'plan' / f'review-{shortbase}..{shorthead}.diff'
    assert printed.resolve() == expected.resolve()

    body = expected.resolve().read_text()
    assert '## Diff' in body
    assert 'second' in body

    assert (repo / '.sdd' / '.gitignore').read_text() == '*\n'


def test_review_package_rejects_a_missing_plan_file(repo):
    """PLAN_FILE is argument 1. A caller still passing the old
    BASE HEAD OUTFILE form must fail loudly, not write a package into the
    wrong plan's workspace."""
    (repo / 'a.txt').write_text('one\n')
    git('add', 'a.txt', 'plan.md', cwd=repo)
    git('commit', '-qm', 'first', cwd=repo)
    result = run(REVIEW_PACKAGE, 'HEAD', 'HEAD', repo / 'p.diff', cwd=repo)
    assert result.returncode == 2
    assert 'no such plan file' in result.stderr


def test_review_package_refuses_a_repository_with_no_commit(repo):
    out = repo / 'p.diff'
    result = run(REVIEW_PACKAGE, repo / 'plan.md', 'HEAD', 'HEAD', out, cwd=repo)
    assert result.returncode == 2
    assert NEW_PROJECT in result.stderr
    assert 'bad BASE' not in result.stderr
    assert not out.exists()


def test_review_package_rejects_an_empty_range(repo):
    """BASE == HEAD passes the ancestry guard (a commit is its own ancestor),
    so only the count guard stands between it and a "0 commit(s)" package a
    reviewer could pass as clean work."""
    (repo / 'a.txt').write_text('one\n')
    git('add', 'a.txt', 'plan.md', cwd=repo)
    git('commit', '-qm', 'first', cwd=repo)
    out = repo / 'p.diff'
    result = run(REVIEW_PACKAGE, repo / 'plan.md', 'HEAD', 'HEAD', out, cwd=repo)
    assert result.returncode == 3
    assert 'empty commit range' in result.stderr
    assert not out.exists()


@pytest.mark.parametrize(
    'base, head',
    [
        # BASE on a sibling branch: HEAD is a commit past the fork point, so
        # the range is non-empty and only the ancestry guard can fire. The
        # package would show the sibling's file as a phantom deletion.
        ('sibling', 'HEAD'),
        # BASE and HEAD swapped, the audit's case.
        ('HEAD', 'HEAD~1'),
    ],
)
def test_review_package_rejects_a_base_that_is_not_an_ancestor(repo, base, head):
    (repo / 'a.txt').write_text('one\n')
    git('add', 'a.txt', 'plan.md', cwd=repo)
    git('commit', '-qm', 'first', cwd=repo)
    git('checkout', '-qb', 'sibling', cwd=repo)
    (repo / 'sibling.txt').write_text('only on the sibling\n')
    git('add', 'sibling.txt', cwd=repo)
    git('commit', '-qm', 'sibling work', cwd=repo)
    git('checkout', '-q', '-', cwd=repo)
    (repo / 'a.txt').write_text('one\ntwo\n')
    git('add', 'a.txt', cwd=repo)
    git('commit', '-qm', 'second', cwd=repo)
    out = repo / 'p.diff'
    result = run(REVIEW_PACKAGE, repo / 'plan.md', base, head, out, cwd=repo)
    assert result.returncode == 3
    assert 'not a descendant' in result.stderr
    assert not out.exists()


OK_CMD = ['sh', '-c', 'echo "Ran 3 tests"; echo OK']


@pytest.fixture
def committed(repo):
    '''The demo repo with plan.md committed, so HEAD resolves.'''
    git('add', 'plan.md', cwd=repo)
    git('commit', '-qm', 'plan', cwd=repo)
    return repo


def run_file(repo, name):
    return repo / '.sdd' / 'plan' / name


def test_test_run_records_a_passing_run(committed):
    result = run(TEST_RUN, 'plan.md', 1, '--', *OK_CMD, cwd=committed)
    assert result.returncode == 0, result.stderr
    sha = git('rev-parse', 'HEAD', cwd=committed).stdout.strip()
    path = run_file(committed, 'task-1-tests.log')
    assert path.read_text().splitlines() == [
        'test-run: Task 1, run 1',
        'command: sh -c \'echo "Ran 3 tests"; echo OK\'',
        f'head: {sha}',
        'tree: clean',
        'exit: 0',
        '--- output ---',
        'Ran 3 tests',
        'OK',
    ]
    out = result.stdout.splitlines()
    assert out[:-1] == ['Ran 3 tests', 'OK']
    assert Path(out[-1].removeprefix('run: ')).resolve() == path.resolve()


def test_test_run_keeps_a_failing_run_and_exits_with_its_status(committed):
    result = run(TEST_RUN, 'plan.md', 2, '--', 'sh', '-c', 'echo "1 failed"; exit 3', cwd=committed)
    assert result.returncode == 3
    lines = run_file(committed, 'task-2-tests.log').read_text().splitlines()
    assert lines[4] == 'exit: 3'
    assert lines[6:] == ['1 failed']
    assert result.stdout.splitlines()[-1].startswith('run: ')


def test_test_run_writes_a_new_file_for_each_run(committed):
    run(TEST_RUN, 'plan.md', 1, '--', 'sh', '-c', 'echo first; exit 1', cwd=committed)
    first = run_file(committed, 'task-1-tests.log').read_bytes()
    result = run(TEST_RUN, 'plan.md', 1, '--', 'sh', '-c', 'echo second', cwd=committed)
    assert result.returncode == 0, result.stderr
    assert run_file(committed, 'task-1-tests.log').read_bytes() == first
    second = run_file(committed, 'task-1-tests-2.log').read_text().splitlines()
    assert second[0] == 'test-run: Task 1, run 2'
    assert second[6:] == ['second']


def test_test_run_records_an_empty_output(committed):
    result = run(TEST_RUN, 'plan.md', 1, '--', 'true', cwd=committed)
    assert result.returncode == 0, result.stderr
    lines = run_file(committed, 'task-1-tests.log').read_text().splitlines()
    assert lines[1] == 'command: true'
    assert lines[5:] == ['--- output ---']
    assert len(result.stdout.splitlines()) == 1


def test_test_run_ends_stdout_with_the_run_line_when_the_output_has_no_final_newline(committed):
    result = run(TEST_RUN, 'plan.md', 1, '--', 'sh', '-c', 'printf "no newline"', cwd=committed)
    assert result.returncode == 0, result.stderr
    out = result.stdout.splitlines()
    assert out[:-1] == ['no newline']
    assert out[-1].startswith('run: ')
    assert run_file(committed, 'task-1-tests.log').read_text().splitlines()[6:] == ['no newline']


def test_test_run_marks_a_dirty_tree(committed):
    (committed / 'scratch.txt').write_text('x\n')
    result = run(TEST_RUN, 'plan.md', 1, '--', 'true', cwd=committed)
    assert result.returncode == 0, result.stderr
    lines = run_file(committed, 'task-1-tests.log').read_text().splitlines()
    assert lines[3] == 'tree: dirty, changed or untracked paths: 1'


def test_test_run_marks_untracked_files_whatever_the_git_config_says(committed):
    git('config', 'status.showUntrackedFiles', 'no', cwd=committed)
    (committed / 'scratch.txt').write_text('x\n')
    result = run(TEST_RUN, 'plan.md', 1, '--', 'true', cwd=committed)
    assert result.returncode == 0, result.stderr
    lines = run_file(committed, 'task-1-tests.log').read_text().splitlines()
    assert lines[3] == 'tree: dirty, changed or untracked paths: 1'


def test_test_run_records_a_command_that_cannot_start(committed):
    result = run(TEST_RUN, 'plan.md', 1, '--', 'no-such-command-plan84', cwd=committed)
    assert result.returncode == 127
    text = run_file(committed, 'task-1-tests.log').read_text()
    assert 'exit: 127' in text.splitlines()
    assert 'no-such-command-plan84' in text.split('--- output ---\n', 1)[1]


def test_test_run_leaves_no_temporary_file_after_a_finished_run(committed):
    result = run(TEST_RUN, 'plan.md', 1, '--', 'sh', '-c', 'echo done; exit 1', cwd=committed)
    assert result.returncode == 1
    assert sorted(p.name for p in run_file(committed, '').iterdir()) == ['task-1-tests.log']


KILL_WAIT_SECONDS = 10


def test_test_run_keeps_a_killed_runs_partial_output_in_the_workspace(committed):
    # A tool timeout kills the whole process group, test-run included. No run
    # file is written then, so the output so far must stay in the temporary file.
    proc = subprocess.Popen(
        [str(TEST_RUN), 'plan.md', '1', '--', 'sh', '-c', 'echo partial-line; sleep 30'],
        cwd=committed, env=GIT_ENV, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    workspace = run_file(committed, '')
    deadline = time.monotonic() + KILL_WAIT_SECONDS
    while time.monotonic() < deadline:
        if any('partial-line' in p.read_text() for p in workspace.glob('test-run.*')):
            break
        time.sleep(0.05)
    else:
        os.killpg(proc.pid, signal.SIGKILL)
        pytest.fail('the command never wrote its first line')
    os.killpg(proc.pid, signal.SIGTERM)
    proc.wait(timeout=KILL_WAIT_SECONDS)
    assert not list(workspace.glob('task-1-tests*.log'))
    left = list(workspace.glob('test-run.*'))
    assert [p.read_text() for p in left] == ['partial-line\n']


@pytest.mark.parametrize('task', ['6b', '2.1', 'A1'])
def test_test_run_accepts_letter_and_dotted_task_ids(committed, task):
    result = run(TEST_RUN, 'plan.md', task, '--', 'true', cwd=committed)
    assert result.returncode == 0, result.stderr
    assert run_file(committed, f'task-{task}-tests.log').is_file()


@pytest.mark.parametrize('task', ['../x', 'a/b', 'x', '.1', '1.', ''])
def test_test_run_refuses_a_task_number_that_is_not_an_id(committed, task):
    result = run(TEST_RUN, 'plan.md', task, '--', 'sh', '-c', 'touch ran', cwd=committed)
    assert result.returncode == 2
    assert 'test-run: bad task number' in result.stderr
    assert not (committed / 'ran').exists()
    assert not (committed / '.sdd').exists()


def test_test_run_refuses_a_repository_with_no_commit(repo):
    result = run(TEST_RUN, 'plan.md', 1, '--', 'sh', '-c', 'touch ran', cwd=repo)
    assert result.returncode == 2
    assert NEW_PROJECT in result.stderr
    assert not (repo / 'ran').exists()
    assert not (repo / '.sdd').exists()


@pytest.mark.parametrize('argv', [
    [], ['plan.md'], ['plan.md', 1], ['plan.md', 1, '--'], ['plan.md', 1, 'x', 'true'],
])
def test_test_run_rejects_bad_arguments(committed, argv):
    result = run(TEST_RUN, *argv, cwd=committed)
    assert result.returncode == 2
    assert 'usage: test-run PLAN_FILE TASK_NUMBER -- TEST_COMMAND [ARGS...]' in result.stderr
