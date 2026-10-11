'''Tests for entry_check.py — the writing-plans entry-check reporter.

Every fixture is a throwaway git repository under pytest's tmp_path.
'''
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).with_name('entry_check.py')
GIT = [
    'git', '-c', 'commit.gpgsign=false', '-c', 'init.defaultBranch=main',
    '-c', 'core.hooksPath=/dev/null', '-c', 'user.name=t', '-c', 'user.email=t@example.invalid',
]


def git(cwd: Path, *args: str, date: str | None = None) -> str:
    env = dict(os.environ)
    if date is not None:
        env['GIT_AUTHOR_DATE'] = env['GIT_COMMITTER_DATE'] = f'{date}T12:00:00'
    return subprocess.run([*GIT, *args], cwd=cwd, env=env, capture_output=True, text=True, check=True).stdout


def write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def commit(root: Path, message: str, date: str = '2026-09-01') -> None:
    git(root, 'add', '-A')
    git(root, 'commit', '-q', '-m', message, date=date)


def check(cwd: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], cwd=cwd, capture_output=True, text=True,
        env={**os.environ, **(env or {})}, check=False,
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / 'repo'
    root.mkdir()
    git(root, 'init', '-q')
    write(root, 'specs/plans/completed/1-first.md', '# Plan 1\n')
    write(root, 'specs/plans/2-second.md', '# Plan 2\n')
    commit(root, 'plans 1 and 2')
    return root


def test_without_a_spec_only_plan_ids_print(repo):
    done = check(repo)
    assert done.returncode == 0
    assert done.stdout.startswith('plan ids:\n')
    assert 'status:' not in done.stdout


def test_highest_and_next_free(repo):
    out = check(repo).stdout
    assert '  highest: 2 — 2-second.md (main, worktree ' in out
    assert '  next free: 3' in out
    assert '  collisions: none' in out


def test_plan_on_another_branch_counts(repo):
    git(repo, 'checkout', '-q', '-b', 'side')
    write(repo, 'specs/plans/3-third.md', '# Plan 3\n')
    commit(repo, 'plan 3 on a side branch')
    git(repo, 'checkout', '-q', 'main')
    out = check(repo).stdout
    assert '  highest: 3 — 3-third.md (side)' in out
    assert '  next free: 4' in out


def test_symbolic_refs_are_skipped(repo):
    git(repo, 'update-ref', 'refs/remotes/origin/main', 'HEAD')
    git(repo, 'symbolic-ref', 'refs/remotes/origin/HEAD', 'refs/remotes/origin/main')
    done = check(repo)
    assert done.returncode == 0
    assert '2-second.md (main, origin/main, worktree ' in done.stdout
    assert 'origin/HEAD' not in done.stdout


def test_untracked_plan_in_a_second_worktree(repo, tmp_path):
    other = tmp_path / 'other'
    git(repo, 'worktree', 'add', '-q', '-b', 'wt', str(other))
    write(other, 'specs/plans/4-fourth.md', '# Plan 4, not committed anywhere\n')
    out = check(repo).stdout
    assert '  highest: 4 — 4-fourth.md (worktree ' in out
    assert '  next free: 5' in out


def test_id_collision_is_reported(repo):
    git(repo, 'checkout', '-q', '-b', 'side')
    write(repo, 'specs/plans/2-other.md', '# Another plan 2\n')
    commit(repo, 'a second plan 2')
    git(repo, 'checkout', '-q', 'main')
    out = check(repo).stdout
    assert '  collisions:\n    2: 2-second.md (main, side, worktree ' in out
    assert '; 2-other.md (side)' in out


def test_plan_named_for_the_spec_is_listed(repo):
    write(repo, 'specs/widget-export.md', '# Widget export\n')
    write(repo, 'specs/plans/3-widget-export.md', '# Plan 3\n')
    commit(repo, 'spec and its plan')
    out = check(repo, 'specs/widget-export.md').stdout
    assert '  plans for this spec: 3-widget-export.md (main, worktree ' in out


def test_spec_with_no_plan_reads_none(repo):
    write(repo, 'specs/gadget.md', '# Gadget\n')
    commit(repo, 'a spec with no plan')
    out = check(repo, 'specs/gadget.md').stdout
    assert '  plans for this spec: none' in out


def test_no_plans_for_spec_line_without_a_spec(repo):
    out = check(repo).stdout
    assert 'plan ids:' in out
    assert 'plans for this spec' not in out


def test_outside_a_repo_exits_2(tmp_path):
    outside = tmp_path / 'outside'
    outside.mkdir()
    done = check(outside, env={'GIT_CEILING_DIRECTORIES': str(tmp_path)})
    assert done.returncode == 2
    assert 'not inside a git repository' in done.stderr


def test_missing_spec_exits_2(repo):
    done = check(repo, 'specs/nope.md')
    assert done.returncode == 2
    assert 'no such spec: specs/nope.md' in done.stderr


def test_repo_without_plans_starts_at_1(tmp_path):
    root = tmp_path / 'empty'
    root.mkdir()
    git(root, 'init', '-q')
    write(root, 'README.md', '# Empty\n')
    commit(root, 'readme only')
    out = check(root).stdout
    assert '  highest: none' in out
    assert '  next free: 1' in out
