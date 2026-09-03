"""Tests for the three bundled bash scripts — run from this directory.

cd skills/subagent-driven-development/scripts && uv run --python 3.13 --with pytest \
  python -m pytest -q

These are bash, not Python, so each test drives the script as a subprocess and
asserts on exit code, stdout, and written files. That keeps this repo on one test
runner instead of adding bats/shunit2 for three files.
"""

import os
import re
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent
WORKSPACE = SCRIPTS / "sdd-workspace"
TASK_BRIEF = SCRIPTS / "task-brief"
REVIEW_PACKAGE = SCRIPTS / "review-package"

# Sanitised so the suite doesn't inherit the user's global/system git config
# (commit.gpgsign, core.hooksPath, init.templateDir, ...). Without this, a
# setup `git commit` can fail silently and the real cause surfaces as a
# confusing downstream assertion on the script under test.
GIT_ENV = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}

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

### Task 2: Second thing

- [ ] **Step 1: other**

## Verification

This trailing section must not leak into Task 2's brief.
"""


def run(*argv, cwd=None):
    return subprocess.run(
        [str(a) for a in argv], cwd=cwd, capture_output=True, text=True, env=GIT_ENV
    )


def git(*argv, cwd):
    """Run a git command that arranges test state (not the call under test)
    and assert it succeeded — a silent failure here must not surface as a
    confusing assertion failure against sdd-workspace/task-brief/review-package."""
    result = run("git", *argv, cwd=cwd)
    assert result.returncode == 0, result.stderr
    return result


@pytest.fixture
def repo(tmp_path):
    """A throwaway git repo containing the demo plan."""
    git("init", "-q", tmp_path, cwd=tmp_path)
    git("config", "user.email", "t@example.invalid", cwd=tmp_path)
    git("config", "user.name", "T", cwd=tmp_path)
    (tmp_path / "plan.md").write_text(PLAN)
    return tmp_path


# ── sdd-workspace ────────────────────────────────────────────────────────


def test_workspace_is_created_inside_the_working_tree(repo):
    """Not under .git/ — Claude Code denies agent writes to that protected path,
    which would block an implementer subagent from writing its report."""
    result = run(WORKSPACE, cwd=repo)
    assert result.returncode == 0
    printed = Path(result.stdout.strip())
    assert printed.resolve() == (repo / ".sdd").resolve()
    assert ".git" not in printed.parts


def test_workspace_ignores_itself_so_artifacts_never_reach_git_status(repo):
    run(WORKSPACE, cwd=repo)
    assert (repo / ".sdd" / ".gitignore").read_text() == "*\n"
    (repo / ".sdd" / "task-1-brief.md").write_text("scratch")
    status = run("git", "status", "--short", cwd=repo).stdout
    assert ".sdd" not in status


# ── task-brief ───────────────────────────────────────────────────────────


def test_task_brief_prepends_global_constraints(repo):
    out = repo / "brief.md"
    result = run(TASK_BRIEF, repo / "plan.md", 1, out, cwd=repo)
    assert result.returncode == 0
    body = out.read_text()
    assert body.index("## Global Constraints") < body.index("### Task 1")
    assert "Single quotes over double." in body


def test_task_brief_keeps_a_fenced_task_heading_as_content(repo):
    """A ```-fenced '### Task 99' is example text, not a section boundary.
    If fence tracking breaks, Task 1's brief is truncated mid-step."""
    out = repo / "brief.md"
    run(TASK_BRIEF, repo / "plan.md", 1, out, cwd=repo)
    body = out.read_text()
    assert "Task 99" in body
    assert "### Task 2" not in body


def test_task_brief_excludes_trailing_plan_sections(repo):
    """The last task must not absorb '## Verification' and everything after it.

    Also asserts Task 2's own body (not just its heading) survived: a
    regression that truncated the brief right after printing the heading
    would otherwise leave this test green. Not hypothetical — task-brief
    truncated a real 234-line brief to 70 lines earlier during this plan's
    execution, because a fence nested inside another fence closed the outer
    fence early.
    """
    out = repo / "brief.md"
    run(TASK_BRIEF, repo / "plan.md", 2, out, cwd=repo)
    body = out.read_text()
    assert "### Task 2: Second thing" in body
    assert "Step 1: other" in body
    assert "must not leak" not in body


def test_task_brief_exits_3_on_a_missing_task(repo):
    result = run(TASK_BRIEF, repo / "plan.md", 42, repo / "brief.md", cwd=repo)
    assert result.returncode == 3
    assert "task 42 not found" in result.stderr


def test_task_brief_exits_2_on_bad_arguments(repo):
    assert run(TASK_BRIEF, repo / "plan.md", cwd=repo).returncode == 2
    missing = run(TASK_BRIEF, repo / "nope.md", 1, repo / "b.md", cwd=repo)
    assert missing.returncode == 2
    assert "no such plan file" in missing.stderr


def test_task_brief_writes_to_and_prints_the_default_workspace_path(repo):
    """No OUTFILE given — the production path every real invocation takes,
    and the only place task-brief actually calls sdd-workspace. Untested
    until now: all other task-brief tests pass an explicit OUTFILE."""
    result = run(TASK_BRIEF, repo / "plan.md", 2, cwd=repo)
    assert result.returncode == 0

    match = re.match(r"^wrote (.+): \d", result.stdout.strip())
    assert match, f"unexpected stdout: {result.stdout!r}"
    printed = Path(match.group(1))
    expected = repo / ".sdd" / "task-2-brief.md"
    assert printed.resolve() == expected.resolve()

    body = expected.resolve().read_text()
    assert "### Task 2: Second thing" in body
    assert "Step 1: other" in body

    assert (repo / ".sdd" / ".gitignore").read_text() == "*\n"


# ── review-package ───────────────────────────────────────────────────────


def test_review_package_carries_commits_stat_and_diff(repo):
    (repo / "a.txt").write_text("one\n")
    git("add", "a.txt", "plan.md", cwd=repo)
    git("commit", "-qm", "first", cwd=repo)
    (repo / "a.txt").write_text("one\ntwo\n")
    git("add", "a.txt", cwd=repo)
    git("commit", "-qm", "second", cwd=repo)

    out = repo / "package.diff"
    result = run(REVIEW_PACKAGE, "HEAD~1", "HEAD", out, cwd=repo)
    assert result.returncode == 0
    assert "1 commit(s)" in result.stdout
    body = out.read_text()
    for heading in ("# Review package:", "## Commits", "## Files changed", "## Diff"):
        assert heading in body
    assert "second" in body
    assert "+two" in body
    assert "first" not in body.split("## Commits")[1].split("## Files changed")[0]


def test_review_package_rejects_an_unresolvable_revision(repo):
    (repo / "a.txt").write_text("one\n")
    git("add", "a.txt", "plan.md", cwd=repo)
    git("commit", "-qm", "first", cwd=repo)
    result = run(REVIEW_PACKAGE, "nosuchrev", "HEAD", repo / "p.diff", cwd=repo)
    assert result.returncode == 2
    assert "bad BASE" in result.stderr


def test_review_package_writes_to_and_prints_the_default_workspace_path(repo):
    """No OUTFILE given — the production path every real invocation takes,
    and the only place review-package actually calls sdd-workspace. Untested
    until now: the other review-package tests pass an explicit OUTFILE."""
    (repo / "a.txt").write_text("one\n")
    git("add", "a.txt", "plan.md", cwd=repo)
    git("commit", "-qm", "first", cwd=repo)
    (repo / "a.txt").write_text("one\ntwo\n")
    git("add", "a.txt", cwd=repo)
    git("commit", "-qm", "second", cwd=repo)

    shortbase = run("git", "rev-parse", "--short", "HEAD~1", cwd=repo).stdout.strip()
    shorthead = run("git", "rev-parse", "--short", "HEAD", cwd=repo).stdout.strip()

    result = run(REVIEW_PACKAGE, "HEAD~1", "HEAD", cwd=repo)
    assert result.returncode == 0

    match = re.match(r"^wrote (.+): \d", result.stdout.strip())
    assert match, f"unexpected stdout: {result.stdout!r}"
    printed = Path(match.group(1))
    expected = repo / ".sdd" / f"review-{shortbase}..{shorthead}.diff"
    assert printed.resolve() == expected.resolve()

    body = expected.resolve().read_text()
    assert "## Diff" in body
    assert "second" in body

    assert (repo / ".sdd" / ".gitignore").read_text() == "*\n"
