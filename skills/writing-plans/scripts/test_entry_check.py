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


def plan(*lines: str) -> str:
    '''A plan's text: a title, then the given lines.'''
    return '\n'.join(['# Plan', '', *lines, ''])


def overlaps(out: str) -> list[str]:
    '''The lines of the report's last field, overlapping files:, after its header.'''
    return out.split('overlapping files:\n', 1)[1].splitlines()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / 'repo'
    root.mkdir()
    git(root, 'init', '-q')
    write(root, 'specs/plans/completed/1-first.md', '# Plan 1\n')
    write(root, 'specs/plans/2-second.md', '# Plan 2\n')
    commit(root, 'plans 1 and 2')
    return root


def test_without_a_spec_plan_ids_then_overlapping_files_print(repo):
    done = check(repo)
    assert done.returncode == 0
    assert done.stdout.startswith('plan ids:\n')
    assert '\noverlapping files:\n' in done.stdout
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


def test_plan_named_before_a_spec_suffix_rename_is_listed(repo):
    write(repo, 'specs/widget-export-spec.md', '# Widget export\n')
    write(repo, 'specs/plans/completed/3-widget-export.md', '# Plan 3\n')
    commit(repo, 'a -spec spec and the plan named before its rename')
    out = check(repo, 'specs/widget-export-spec.md').stdout
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


def test_spec_outside_repo_exits_2(repo, tmp_path):
    spec = write(tmp_path, 'elsewhere/spec.md', '# Elsewhere\n')
    done = check(repo, str(spec))
    assert done.returncode == 2
    assert 'spec is outside this repository' in done.stderr


def test_repo_without_plans_starts_at_1(tmp_path):
    root = tmp_path / 'empty'
    root.mkdir()
    git(root, 'init', '-q')
    write(root, 'README.md', '# Empty\n')
    commit(root, 'readme only')
    out = check(root).stdout
    assert '  highest: none' in out
    assert '  next free: 1' in out


def test_a_path_two_live_plans_name_is_shared(repo):
    write(repo, 'specs/plans/2-second.md', plan('- Modify: `src/app.py`', '- Test: `tests/test_app.py`'))
    commit(repo, 'plan 2 names its files')
    git(repo, 'checkout', '-q', '-b', 'side')
    write(repo, 'specs/plans/3-third.md', plan('- Modify: `src/app.py`', '- Create: `src/new.py`'))
    commit(repo, 'plan 3 on a side branch')
    git(repo, 'checkout', '-q', 'main')
    assert overlaps(check(repo).stdout) == [
        '  live plans: 2-second.md (2 paths); 3-third.md (2 paths)',
        '  shared:',
        '    src/app.py: 2-second.md, 3-third.md',
    ]


def test_a_plan_retired_on_any_ref_is_not_live(repo):
    write(repo, 'specs/plans/2-second.md', plan('- Modify: `src/app.py`'))
    commit(repo, 'plan 2 names src/app.py')
    git(repo, 'branch', 'planning')
    git(repo, 'mv', 'specs/plans/2-second.md', 'specs/plans/completed/2-second.md')
    write(repo, 'specs/plans/3-third.md', plan('- Modify: `src/app.py`'))
    commit(repo, 'retire plan 2; plan 3 names src/app.py too')
    assert overlaps(check(repo).stdout) == ['  live plans: 3-third.md (1 path)', '  shared: none']


def test_spans_in_parentheses_name_no_paths(repo):
    write(repo, 'specs/plans/2-second.md', plan('- Modify: `src/app.py` (`main`, and `src/util.py` for its helper)'))
    write(repo, 'specs/plans/3-third.md', plan('- Modify: `src/app.py`, `src/util.py`'))
    commit(repo, 'two plans')
    assert overlaps(check(repo).stdout) == [
        '  live plans: 2-second.md (1 path); 3-third.md (2 paths)',
        '  shared:',
        '    src/app.py: 2-second.md, 3-third.md',
    ]


def test_line_suffixes_drop_and_a_qualified_modify_counts(repo):
    write(repo, 'specs/plans/2-second.md', plan(
        '- Modify: `src/app.py:10-20`',
        '- Modify, on one branch only: `src/flag.py`',
    ))
    write(repo, 'specs/plans/3-third.md', plan('- Test: `src/app.py:7`', '- Create: `src/flag.py`'))
    commit(repo, 'two plans')
    assert overlaps(check(repo).stdout) == [
        '  live plans: 2-second.md (2 paths); 3-third.md (2 paths)',
        '  shared:',
        '    src/app.py: 2-second.md, 3-third.md',
        '    src/flag.py: 2-second.md, 3-third.md',
    ]


def test_edit_headers_and_extract_markers_name_paths(repo):
    write(repo, 'NOTICE', 'Notice\n')
    write(repo, 'specs/plans/2-second.md', plan(
        '**Edit `src/app.py`: replace the block that `src/lib/mirror.py` copies**',
        '<!-- extract-edit: NOTICE:credits -->',
        '<!-- extract-file: src/new.py -->',
    ))
    write(repo, 'specs/plans/3-third.md', plan('- Modify: `src/app.py`, `NOTICE`, `src/new.py`, `src/lib/mirror.py`'))
    commit(repo, 'two plans and a NOTICE')
    assert overlaps(check(repo).stdout) == [
        '  live plans: 2-second.md (3 paths); 3-third.md (4 paths)',
        '  shared:',
        '    NOTICE: 2-second.md, 3-third.md',
        '    src/app.py: 2-second.md, 3-third.md',
        '    src/new.py: 2-second.md, 3-third.md',
    ]


def test_fenced_code_names_no_paths(repo):
    write(repo, 'specs/plans/2-second.md', plan(
        '````markdown',
        '```python',
        '- Modify: `src/inner.py`',
        '```',
        '- Modify: `src/still-fenced.py`',
        '<!-- extract-file: src/fenced-marker.py -->',
        '````',
        '- Modify: `src/after.py`',
    ))
    write(repo, 'specs/plans/3-third.md', plan(
        '- Modify: `src/inner.py`, `src/still-fenced.py`, `src/fenced-marker.py`, `src/after.py`',
    ))
    commit(repo, 'a plan with nested fences')
    assert overlaps(check(repo).stdout) == [
        '  live plans: 2-second.md (1 path); 3-third.md (4 paths)',
        '  shared:',
        '    src/after.py: 2-second.md, 3-third.md',
    ]


def test_a_path_without_a_slash_counts_only_at_a_root(repo):
    write(repo, 'NOTICE', 'Notice\n')
    write(repo, 'specs/plans/2-second.md', plan('- Modify: the 13 `SKILL.md` files, `NOTICE`, `LICENSE-extra`'))
    write(repo, 'specs/plans/3-third.md', plan('- Modify: every `SKILL.md`, `NOTICE`, `LICENSE-extra`'))
    commit(repo, 'two plans and a NOTICE')
    git(repo, 'checkout', '-q', '-b', 'side')
    write(repo, 'LICENSE-extra', 'License\n')
    commit(repo, 'a root file on a side branch only')
    git(repo, 'checkout', '-q', 'main')
    assert overlaps(check(repo).stdout) == [
        '  live plans: 2-second.md (2 paths); 3-third.md (2 paths)',
        '  shared:',
        '    LICENSE-extra: 2-second.md, 3-third.md',
        '    NOTICE: 2-second.md, 3-third.md',
    ]


def test_a_plans_copies_are_unioned(repo, tmp_path):
    write(repo, 'specs/plans/2-second.md', plan('- Modify: `src/a.py`'))
    write(repo, 'specs/plans/3-third.md', plan('- Modify: `src/b.py`'))
    commit(repo, 'plans 2 and 3')
    other = tmp_path / 'other'
    git(repo, 'worktree', 'add', '-q', '-b', 'wt', str(other))
    write(other, 'specs/plans/3-third.md', plan('- Modify: `src/a.py`'))
    assert overlaps(check(repo).stdout) == [
        '  live plans: 2-second.md (1 path); 3-third.md (2 paths)',
        '  shared:',
        '    src/a.py: 2-second.md, 3-third.md',
    ]


def test_a_plan_given_with_plan_is_compared(repo, tmp_path):
    write(repo, 'specs/plans/2-second.md', plan('- Modify: `src/app.py`'))
    commit(repo, 'plan 2')
    draft = write(tmp_path, 'drafts/4-draft.md', plan('- Modify: `src/app.py`'))
    assert overlaps(check(repo, '--plan', str(draft)).stdout) == [
        '  live plans: 2-second.md (1 path); 4-draft.md (1 path)',
        '  shared:',
        '    src/app.py: 2-second.md, 4-draft.md',
    ]


def test_a_live_plan_given_with_plan_does_not_overlap_itself(repo):
    write(repo, 'specs/plans/2-second.md', plan('- Modify: `src/app.py`'))
    commit(repo, 'plan 2')
    out = check(repo, '--plan', 'specs/plans/2-second.md').stdout
    assert overlaps(out) == ['  live plans: 2-second.md (1 path)', '  shared: none']


def test_missing_plan_exits_2(repo):
    done = check(repo, '--plan', 'specs/plans/nope.md')
    assert done.returncode == 2
    assert 'no such plan: specs/plans/nope.md' in done.stderr


def test_plan_that_is_a_directory_exits_2(repo):
    done = check(repo, '--plan', 'specs')
    assert done.returncode == 2
    assert 'not a file: specs' in done.stderr


def test_repo_without_plans_has_no_live_plans(tmp_path):
    root = tmp_path / 'empty'
    root.mkdir()
    git(root, 'init', '-q')
    write(root, 'README.md', '# Empty\n')
    commit(root, 'readme only')
    assert overlaps(check(root).stdout) == ['  live plans: none', '  shared: none']
