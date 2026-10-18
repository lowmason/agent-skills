# Entry-Check File Overlaps Implementation Plan

**Status: COMPLETE (2026-10-18)** — executed via executing-plans; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make writing-plans' entry check report which live plans edit the same files, so two plans written in parallel learn about a shared file at planning time instead of at merge time.

**Architecture:** `skills/writing-plans/scripts/entry_check.py` already scans every branch, remote-tracking ref and worktree for `specs/plans/`. Task 1 keeps each copy it finds (a blob on a ref, a file in a worktree), reads the live plans' copies, collects the repo paths each one names, and prints a second field, `overlapping files:`, with a `live plans:` line (each plan and how many paths it names) and a `shared:` list (each path that two or more of them name). An optional `--plan PATH` adds a plan file saved where the scan does not look. Task 2 makes the planner rerun the check before the plan review and put the shared files in the review message, but only if a no-guidance control shows that planners do not already do it.

**Tech Stack:** Python 3.13 standard library (`argparse`, `re`, `subprocess`, `dataclasses`, `pathlib`), pytest through `uv run`, `git`, and `claude -p` for the Task 2 micro-test.

**Spec:** none. The requirements are the session brief that plan 52's planning session wrote on 2026-10-18: on that day plans 50, 52 and 53 were written in parallel, they overlapped on `CLAUDE.md`, `NOTICE` and `README.md`, and someone found the overlap by hand late, then had to check the edit anchors in both merge orders.

**Design choices beyond the brief** (your human partner may overrule any of them at review):

1. **A plan retired anywhere is not live.** A plan with a copy under `specs/plans/completed/` on any ref or in any worktree is not live, because a merged planning branch keeps a live copy after `main` retires the plan: `claude/agent-skills-handoff-plan-3a6a7b` still holds plan 45 outside `completed/`. A live plan's paths are the union over all its copies, so an uncommitted edit in a worktree counts. *Superseded at the final review by D5.*
2. **What names a path.** On a Files line, only backticked spans outside parentheses count, because parentheses hold identifiers (plan 53 writes `` `build/check_frontmatter.py` (module docstring; `ALLOWED_KEYS` becomes `SPEC_KEYS` …) ``). An Edit header gives only the span right after `Edit `, because a second span is often code (`` insert before the line `def make_agent(…) -> Path:` ``). An `extract-edit` key splits on its last colon, as plan 52's `extract_plan_files.py` does. Fenced code is skipped, so test fixtures and examples name nothing, and a fence closes only on a run of its own character at least as long as the one that opened it, so a four-backtick block can hold three-backtick ones.
3. **A path without a slash counts only when a ref or worktree has that name at its root.** That keeps `NOTICE`, `CLAUDE.md` and `README.md`, and drops a bare `SKILL.md` ("the 13 superpowers `SKILL.md` files") and identifiers outside parentheses (plan 51's `` `rebaseline` ``). The cost is that a new root file that two plans would both create is not seen until one of them commits it. *Superseded at the final review by D6, which applies the same root test to every path's first component.*
4. **A `live plans:` line counts each plan's paths.** A plan written in a style the parser does not read shows 0 paths instead of hiding behind `shared: none`.
5. **Matching is exact,** after a `:LINE` or `:START-END` suffix is dropped. A file set named only in prose ("the 15 header-less runnable scripts") is not seen. The docstring says so, and so must every report of a run: `shared: none` does not prove that two plans are disjoint.
6. **`--plan` names a plan, not a second copy.** Given a file with the filename of a live plan, it is that plan, so a plan never overlaps itself.

## Global Constraints

- **Work in this worktree,** `/Users/lowell/Projects/agent-skills/.claude/worktrees/superpowers-spec-staleness-f6b72d` (branch `claude/inspiring-cannon-7e3ec9`), never the shared checkout: `~/.claude/skills` resolves to the shared checkout, and this plan edits a skill that sessions load. Run every command from the worktree root; use `uv run --directory`, never a bare `cd`, because a Bash `cd` persists and moves the session.
- **`entry_check.py` stays a read-only, stdlib-only reporter:** exit 0 whenever it prints a report, exit 2 only when it cannot run.
- **Tests** are subprocess-driven over throwaway git repositories, in `skills/writing-plans/scripts/test_entry_check.py`. Run them with `uv run --directory skills/writing-plans/scripts --python 3.13 --with pytest python -m pytest -q`. State test counts as deltas (+N), never as totals.
- **Assert on the whole `overlapping files:` field** (`overlaps(out) == [...]`), never on its header alone: the header prints on every run.
- **Plan 53 couplings, safe in both merge orders.** Plan 53 (`specs/plans/53-agent-skills-portability.md`, on `main`, not yet executed) touches three of this plan's files:
  - (a) Its Task 10 helper writes a PEP 723 header after line 1 of `entry_check.py`. Keep lines 1-5 (the shebang, the docstring's first line, the blank line, `Run from the repo root:` and the blank line after it) byte-identical, so the two changes never touch adjacent lines.
  - (b) Its Task 11 replaces the **Save plans to** paragraph and the `deferred_stats.py` invocation in `skills/writing-plans/SKILL.md` by exact text. Leave both as they are.
  - (c) Its Task 11 lint counts the bundled-script invocations in skill markdown (two in writing-plans' SKILL.md). Add no `python …/scripts/…` or `uv run …/scripts/…` invocation: refer to the check by name.
  - (d) Plans 52 and 53 anchor their `NOTICE` edits on other text: line 4, line 16, line 78, the deferred_stats path bullet that ends near line 329, and line 443. Edit only the entry_check bullet, lines 356-362.
  - Plan 53's Task 10 also names `writing-plans/scripts/entry_check.py` inside a code block, which the report cannot see. So a run will list `skills/writing-plans/SKILL.md` and `NOTICE` as shared with plan 53, but not `entry_check.py`, which it shares too.
- **`CLAUDE.md` is not touched.** It is at 199 of 200 lines (check `claude-md-size`), and its Commands comment already covers these tests.
- **Edit `skills/writing-plans/SKILL.md` only after a RED control shows the failure** (writing-skills' Iron Law), from a micro-test that runs outside the repository.
- **Run `bash build/run_commit_lints.sh` before each commit;** it must print `commit lints passed`.
- **Python style:** single quotes, f-strings, 4-space indentation.
- **Commit messages end with** `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Decisions

- **D1** (owner, brief, 2026-10-18): The report prints each path that two or more live plans name, with those plans. A live plan is one not under `specs/plans/completed/`. Its paths come from its `- Create:`, `- Modify:` and `- Test:` lines, its "Edit `PATH`" headers, and its `<!-- extract-edit: PATH:LABEL -->` and `<!-- extract-file: PATH -->` markers. Applied in: Task 1.
- **D2** (owner, brief, 2026-10-18): The check also accepts a plan file to compare against the others (`--plan PATH`), because at entry the plan being written may not exist yet. Applied in: Task 1.
- **D3** (owner, brief, 2026-10-18): The script stays read-only and stdlib-only, and its tests go in `skills/writing-plans/scripts`. Applied in: Global Constraints.
- **D4** (owner, brief, 2026-10-18): A change to writing-plans' SKILL.md text follows the writing-skills skill, and this small, well-specified change gets a plan but no spec. Applied in: Task 2.
- **D5** (owner, final review, 2026-10-18): Only on default branch: a plan is retired only when the default branch (origin/HEAD's target, else main or master) has it under `completed/`. Plan 45 stays excluded; a plan retired on an open PR stays listed. Applied in: Task 1 (review fix acb0047), in place of design choice 1.
- **D6** (owner, final review, 2026-10-18): First part at a root: a path counts only when its first component is an entry at some ref's or worktree's root. Drops `KIT/…`, keeps `rules/…`; a plan's brand-new top-level directory would be missed. Applied in: Task 1 (review fix acb0047), in place of design choice 3.
- **D7** (owner, final review, 2026-10-18): Defer it: `- Rename:`, `- Delete:` and `- Move:` lines are logged in `specs/deferred_items.md`, because adding the verbs as-is would also pick up the skill-relative paths those lines carry. Applied in: plan completion (deferred items).
- **D8** (owner, finishing, 2026-10-18): Leave it: NOTICE's entry_check bullet stays as it is. It records provenance (an original MIT work), not a feature list, and SKILL.md is unchanged. Applied in: Task 2 (Step 5 not run); the final review's NOTICE finding was not applied.

---

### Task 1: The overlapping-files report

**Files:**
- Modify: `skills/writing-plans/scripts/entry_check.py` (the docstring from line 6 on; `git`; new `Sighting`, `live_plan_texts`, `root_names`, `named_paths` and their helpers; `plan_sightings`, `plans_by_id`, `report` and `main`)
- Test: `skills/writing-plans/scripts/test_entry_check.py` (+13; one test renamed)

**Interfaces:**
- Consumes: nothing from another task.
- Produces: the report's second field, which Task 2's skill text names:

  ```text
  overlapping files:
    live plans: <plan> (<n> paths); <plan> (<n> paths)
    shared:
      <path>: <plan>, <plan>
  ```

  `live plans: none` when there is none, `shared: none` when no path is shared, and `(1 path)` for one. Plans sort by id, then filename; a `--plan` file whose name has no id sorts last. Paths sort as strings. The CLI is `entry_check.py [SPEC] [--plan PLAN]`; a `--plan` path that does not exist exits 2 with `no such plan: <path>`, and a directory exits 2 with `not a file: <path>`.

- [x] **Step 1: Write the failing tests**

> Deviation: the final review added 9 tests (acb0047). The repo fixture now commits `src/` and `tests/`, which D6 needs, and `test_a_plan_retired_on_any_ref_is_not_live` became `test_a_plan_retired_on_the_default_branch_is_not_live`.

In `skills/writing-plans/scripts/test_entry_check.py`, add these two helpers after `check` (before the `repo` fixture):

```python
def plan(*lines: str) -> str:
    '''A plan's text: a title, then the given lines.'''
    return '\n'.join(['# Plan', '', *lines, ''])


def overlaps(out: str) -> list[str]:
    '''The lines of the report's last field, overlapping files:, after its header.'''
    return out.split('overlapping files:\n', 1)[1].splitlines()
```

Replace the first test, whose name is no longer true:

```python
def test_without_a_spec_only_plan_ids_print(repo):
    done = check(repo)
    assert done.returncode == 0
    assert done.stdout.startswith('plan ids:\n')
    assert 'status:' not in done.stdout
```

with:

```python
def test_without_a_spec_plan_ids_then_overlapping_files_print(repo):
    done = check(repo)
    assert done.returncode == 0
    assert done.stdout.startswith('plan ids:\n')
    assert '\noverlapping files:\n' in done.stdout
    assert 'status:' not in done.stdout
```

Append these tests to the end of the file:

```python
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
```

- [x] **Step 2: Run the tests to verify they fail**

Run: `uv run --directory skills/writing-plans/scripts --python 3.13 --with pytest python -m pytest -q`

Expected: 14 failed, every other test passes. Read each failure's reason: the renamed test fails its `'\noverlapping files:\n'` assertion; the tests that call `overlaps` fail with `IndexError` (no such field), the two `--plan` comparison tests because argparse rejects `--plan` and prints nothing; `test_missing_plan_exits_2` and `test_plan_that_is_a_directory_exits_2` fail on stderr, which reads `unrecognized arguments`. A test that fails for any other reason is not RED: fix the test first.

- [x] **Step 3: Write the implementation**

> Deviation: the final review changed the code (acb0047): D5's default-branch retirement (a new `default_branch_refs`, a `ref` field on `Sighting`), D6's root-anchored paths, a blob-text cache shared by every plan name in place of `Sighting.text` (Codex P2), `OSError` tolerance for worktree copies and worktree roots, and no fence opened by a line that starts with an inline triple-backtick span. The docstring follows the code.

Replace the whole of `skills/writing-plans/scripts/entry_check.py` with the following. Lines 1-5 are unchanged (Global Constraints, coupling (a)):

````python
#!/usr/bin/env python3
'''Report what a planning session checks before it plans a spec.

Run from the repo root:

    uv run --no-project --python 3.13 python <this-skill-dir>/scripts/entry_check.py [SPEC] [--plan PLAN]

It reads every branch and remote-tracking ref (symbolic refs such as
``origin/HEAD`` skipped) and every worktree's ``specs/plans/``, untracked
plans included, and prints two fields.

``plan ids:`` gives the highest id and where it occurs, the next free id, any
id used by two different plan filenames, and, given a spec path, any plan
whose name ends in the spec's stem.

``overlapping files:`` lists the live plans, each with the number of repo
paths it names, then each path that two or more of them name. A plan is live
when no copy of it, on any ref or in any worktree, sits under
``specs/plans/completed/``; its paths are the union over its copies. Outside
fenced code, a plan names a path with a backticked span outside parentheses
on a ``- Create:``, ``- Modify:`` or ``- Test:`` line, with the first span of
an Edit header (``**Edit `PATH`: replace**``), and with the PATH of an
``<!-- extract-file: PATH -->`` or ``<!-- extract-edit: PATH:LABEL -->``
line. A ``:LINE`` or ``:START-END`` suffix is dropped, and a path without a
slash counts only when some ref or worktree has an entry of that name at its
root. Paths match as written, and a file set named only in prose ("the 13
superpowers SKILL.md files") is not seen, so ``shared: none`` does not prove
that two plans touch different files. ``--plan`` adds a plan saved outside
``specs/plans/``; given the filename of a live plan, it is that plan.

A reporter, like deferred_stats.py: it is read-only and exits 0 whenever it
prints a report. It exits 2 only when it cannot run: outside a git
repository, given a spec or plan path that does not exist or is not a file,
or given a spec outside this repository.
'''

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

CANNOT_RUN = 2
PLAN_RE = re.compile(r'^(?P<id>\d+)-(?P<name>.+)\.md$')
RETIRED = 'specs/plans/completed/'
FILES_LINE_RE = re.compile(r'^\s*- (?:Create|Modify|Test)\b[^:]*:(?P<rest>.*)$')
EDIT_HEADER_RE = re.compile(r'^\s*(?:#+\s+)?(?:\*\*)?Edit `(?P<span>[^`]+)`')
# A marker is a whole line, as the extract_plan_files.py helper that applies them reads it.
MARKER_RE = re.compile(r'^<!-- extract-(?P<kind>file|edit): (?P<key>\S+) -->$')
FENCE_RE = re.compile(r'^\s*(?P<fence>`{3,}|~{3,})(?P<info>.*)$')
SPAN_OR_PAREN_RE = re.compile(r'(?P<ticks>`+)(?P<span>.+?)(?P=ticks)|[()]')
LINE_SUFFIX_RE = re.compile(r':\d+(?:-\d+)?$')


class CannotRun(Exception):
    '''The report cannot be produced; main() prints the reason and exits 2.'''


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ['git', '-C', str(root), *args], capture_output=True, encoding='utf-8', errors='replace', check=False,
    )


def git_out(root: Path, *args: str) -> str:
    done = git(root, *args)
    if done.returncode != 0:
        raise CannotRun(done.stderr.strip() or f'git {" ".join(args)} failed')
    return done.stdout


def repo_root(cwd: Path) -> Path:
    done = git(cwd, 'rev-parse', '--show-toplevel')
    if done.returncode != 0:
        raise CannotRun('not inside a git repository')
    return Path(done.stdout.strip())


@dataclass
class Plan:
    name: str
    locations: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Sighting:
    '''One copy of a file under specs/plans: a blob on a ref, or a file in a worktree.'''
    path: str
    where: str
    blob: str = ''
    file: Path | None = None

    @property
    def name(self) -> str:
        return PurePosixPath(self.path).name

    def text(self, root: Path) -> str:
        if self.file is not None:
            return self.file.read_text(encoding='utf-8', errors='replace')
        return git_out(root, 'cat-file', 'blob', self.blob)


def ref_names(root: Path) -> list[str]:
    '''Every branch and remote-tracking ref, skipping symbolic ones like origin/HEAD.'''
    out = git_out(root, 'for-each-ref', '--format=%(refname)%09%(symref)', 'refs/heads', 'refs/remotes')
    refs = []
    for line in out.splitlines():
        ref, _, symref = line.partition('\t')
        if ref and not symref:
            refs.append(ref)
    return refs


def worktree_paths(root: Path) -> list[Path]:
    out = git_out(root, 'worktree', 'list', '--porcelain')
    return [Path(line.removeprefix('worktree ')) for line in out.splitlines() if line.startswith('worktree ')]


def plan_sightings(root: Path, refs: list[str], trees: list[Path]) -> list[Sighting]:
    '''Every file under specs/plans on every ref and in every worktree.'''
    seen = []
    for ref in refs:
        short = ref.removeprefix('refs/heads/').removeprefix('refs/remotes/')
        listing = git(root, 'ls-tree', '-r', ref, '--', 'specs/plans')
        for line in listing.stdout.splitlines():
            meta, _, path = line.partition('\t')
            seen.append(Sighting(path, short, blob=meta.split()[-1]))
    for tree in trees:
        plans = tree / 'specs' / 'plans'
        if plans.is_dir():
            seen.extend(
                Sighting(path.relative_to(tree).as_posix(), f'worktree {tree}', file=path)
                for path in sorted(plans.rglob('*.md'))
            )
    return seen


def plans_by_id(sightings: list[Sighting]) -> dict[int, list[Plan]]:
    by_id: dict[int, dict[str, Plan]] = {}
    for sighting in sightings:
        m = PLAN_RE.match(sighting.name)
        if not m:
            continue
        plan = by_id.setdefault(int(m['id']), {}).setdefault(sighting.name, Plan(sighting.name))
        if sighting.where not in plan.locations:
            plan.locations.append(sighting.where)
    return {pid: list(plans.values()) for pid, plans in by_id.items()}


def describe(plans: list[Plan]) -> str:
    return '; '.join(f'{p.name} ({", ".join(p.locations)})' for p in plans)


def names_spec(plan: Plan, stem: str) -> bool:
    # A trailing -spec is a filename convention, not part of the spec's name, so a
    # plan named before a spec gained the suffix still counts.
    name = PLAN_RE.match(plan.name)['name']
    return any(name == s or name.endswith(f'-{s}') for s in {stem, stem.removesuffix('-spec')})


def format_plan_ids(by_id: dict[int, list[Plan]], stem: str | None) -> list[str]:
    lines = ['plan ids:']
    if by_id:
        top = max(by_id)
        lines += [f'  highest: {top} — {describe(by_id[top])}', f'  next free: {top + 1}']
    else:
        lines += ['  highest: none', '  next free: 1']
    collisions = [(pid, by_id[pid]) for pid in sorted(by_id) if len(by_id[pid]) > 1]
    if collisions:
        lines.append('  collisions:')
        lines += [f'    {pid}: {describe(plans)}' for pid, plans in collisions]
    else:
        lines.append('  collisions: none')
    if stem is not None:
        mine = [p for pid in sorted(by_id) for p in by_id[pid] if names_spec(p, stem)]
        lines.append(f'  plans for this spec: {describe(mine) if mine else "none"}')
    return lines


def live_plan_texts(root: Path, sightings: list[Sighting]) -> dict[str, set[str]]:
    '''The texts of each live plan's copies, by filename. A plan is live when no copy
    of it sits under specs/plans/completed/: a merged planning branch keeps a live
    copy of a plan that main has since retired.'''
    retired = {s.name for s in sightings if s.path.startswith(RETIRED)}
    texts: dict[str, set[str]] = {}
    blobs_read: set[str] = set()
    for s in sightings:
        if s.name in retired or not PLAN_RE.match(s.name):
            continue
        if s.blob:
            if s.blob in blobs_read:
                continue
            blobs_read.add(s.blob)
        texts.setdefault(s.name, set()).add(s.text(root))
    return texts


def root_names(root: Path, refs: list[str], trees: list[Path]) -> set[str]:
    '''The names at the root of every ref and every worktree.'''
    names = set()
    for ref in refs:
        names.update(git(root, 'ls-tree', '--name-only', ref).stdout.splitlines())
    for tree in trees:
        if tree.is_dir():
            names.update(path.name for path in tree.iterdir())
    return names


def unfenced_lines(text: str) -> list[str]:
    '''The lines outside fenced code. A fence closes only on a bare run of its own
    character at least as long as the opening run, so a four-backtick block can
    hold three-backtick ones.'''
    lines, fence = [], ''
    for line in text.splitlines():
        m = FENCE_RE.match(line)
        if not fence:
            if m:
                fence = m['fence']
            else:
                lines.append(line)
        elif m and m['fence'][0] == fence[0] and len(m['fence']) >= len(fence) and not m['info'].strip():
            fence = ''
    return lines


def spans_outside_parens(text: str) -> list[str]:
    '''The backticked spans in text that sit outside parentheses.'''
    spans, depth = [], 0
    for m in SPAN_OR_PAREN_RE.finditer(text):
        if m['span'] is not None:
            if depth == 0:
                spans.append(m['span'])
        elif m[0] == '(':
            depth += 1
        else:
            depth = max(depth - 1, 0)
    return spans


def repo_path(span: str, names_at_root: set[str]) -> str | None:
    '''The repo path a span names, or None. A span without a slash names one only
    when it is an entry at some tree's root: NOTICE does, a bare SKILL.md does not.'''
    path = LINE_SUFFIX_RE.sub('', span.strip()).removeprefix('./')
    if not path or path.startswith(('/', '~')) or any(c.isspace() for c in path):
        return None
    if '/' not in path and path not in names_at_root:
        return None
    return path


def named_paths(text: str, names_at_root: set[str]) -> set[str]:
    '''The repo paths a plan names on its Files lines, Edit headers and extract markers.'''
    spans = []
    for line in unfenced_lines(text):
        if m := FILES_LINE_RE.match(line):
            spans += spans_outside_parens(m['rest'])
        elif m := EDIT_HEADER_RE.match(line):
            spans.append(m['span'])
        elif m := MARKER_RE.match(line):
            spans.append(m['key'].rsplit(':', 1)[0] if m['kind'] == 'edit' else m['key'])
    return {path for span in spans if (path := repo_path(span, names_at_root))}


def plan_order(name: str) -> tuple[bool, int, str]:
    '''By id, then filename; a --plan file whose name has no id comes last.'''
    m = PLAN_RE.match(name)
    return (m is None, int(m['id']) if m else 0, name)


def path_count(n: int) -> str:
    return f'{n} path' if n == 1 else f'{n} paths'


def format_overlaps(paths_by_plan: dict[str, set[str]]) -> list[str]:
    names = sorted(paths_by_plan, key=plan_order)
    counts = [f'{name} ({path_count(len(paths_by_plan[name]))})' for name in names]
    lines = ['overlapping files:', f'  live plans: {"; ".join(counts) if counts else "none"}']
    planned: dict[str, list[str]] = {}
    for name in names:
        for path in paths_by_plan[name]:
            planned.setdefault(path, []).append(name)
    shared = sorted(path for path, plans in planned.items() if len(plans) > 1)
    if shared:
        lines.append('  shared:')
        lines += [f'    {path}: {", ".join(planned[path])}' for path in shared]
    else:
        lines.append('  shared: none')
    return lines


def report(root: Path, spec: Path | None, plan: Path | None) -> list[str]:
    refs, trees = ref_names(root), worktree_paths(root)
    sightings = plan_sightings(root, refs, trees)
    texts = live_plan_texts(root, sightings)
    if plan is not None:
        texts.setdefault(plan.name, set()).add(plan.read_text(encoding='utf-8', errors='replace'))
    names_at_root = root_names(root, refs, trees)
    paths = {
        name: set().union(*(named_paths(text, names_at_root) for text in copies))
        for name, copies in texts.items()
    }
    stem = spec.stem if spec is not None else None
    return format_plan_ids(plans_by_id(sightings), stem) + format_overlaps(paths)


def require_file(path: Path, kind: str) -> None:
    if path.is_dir():
        raise CannotRun(f'not a file: {path}')
    if not path.is_file():
        raise CannotRun(f'no such {kind}: {path}')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Report what a planning session checks before it plans a spec.')
    parser.add_argument('spec', nargs='?', type=Path, help='the spec about to be planned')
    parser.add_argument('--plan', type=Path, help='a plan saved outside specs/plans/, to compare with the live plans')
    args = parser.parse_args(argv)
    try:
        root = repo_root(Path.cwd())
        spec = None
        if args.spec is not None:
            require_file(args.spec, 'spec')
            try:
                spec = args.spec.resolve().relative_to(root.resolve())
            except ValueError:
                raise CannotRun(f'spec is outside this repository: {args.spec}') from None
        if args.plan is not None:
            require_file(args.plan, 'plan')
        print('\n'.join(report(root, spec, args.plan)))
    except CannotRun as e:
        print(f'entry_check: {e}', file=sys.stderr)
        return CANNOT_RUN
    return 0


if __name__ == '__main__':
    sys.exit(main())
````

Check coupling (a) before going on:

```bash
git diff -U0 skills/writing-plans/scripts/entry_check.py | head -8
```

Expected: the first hunk header starts at line 6 (`@@ -6 +6 @@` or later), so lines 1-5 are untouched.

- [x] **Step 4: Run the tests to verify they pass**

> Deviation: 40 passed (+13) at 52b72ff, 49 (+22 in all) after the review fixes, and 51 (+24 in all) after the finishing-gate fix (c399b65).

Run: `uv run --directory skills/writing-plans/scripts --python 3.13 --with pytest python -m pytest -q`

Expected: every test passes, +13 over the count before Step 1.

- [x] **Step 5: Run the report against this repository**

Run: `uv run --no-project --python 3.13 python skills/writing-plans/scripts/entry_check.py`

Expected: exit 0, and an `overlapping files:` field whose `live plans:` line names every live plan, each with a nonzero count. On 2026-10-18 those were 51 (`51-claude-code-drift-automation.md`, worktree `suspicious-ptolemy-161633`), 52 (`52-write-with-asd-ste100.md`, branch `claude/elegant-bassi-20474d`), 53 (`53-agent-skills-portability.md`, `main`) and this plan, 54. Plan 45, retired on `main` but outside `completed/` on `claude/agent-skills-handoff-plan-3a6a7b`, must not be listed. The `shared:` list must include `CLAUDE.md`, `NOTICE` and `README.md` for plans 52 and 53 (the known 2026-10-18 overlaps), and `NOTICE` and `skills/writing-plans/SKILL.md` for plans 53 and 54. Read every other `shared:` line against the two plans it names, and record the run's `overlapping files:` field in the completion notes. If a known overlap is missing, stop: the parser has missed a style that a real plan uses.

Then compare a plan saved outside `specs/plans/`:

```bash
cp specs/plans/54-entry-check-file-overlaps.md /tmp/plan54-copy.md
uv run --no-project --python 3.13 python skills/writing-plans/scripts/entry_check.py --plan /tmp/plan54-copy.md
```

Expected: `plan54-copy.md` has no leading id, so it is listed last as a plan of its own, with the same path count as plan 54, and every path plan 54 names is shared by both. That shows `--plan` reads a file the scan cannot see. Delete the copy afterwards: `rm /tmp/plan54-copy.md`.

- [x] **Step 6: Commit**

```bash
bash build/run_commit_lints.sh
```

Expected: `commit lints passed`.

```bash
git add skills/writing-plans/scripts/entry_check.py skills/writing-plans/scripts/test_entry_check.py
git commit -m "feat(writing-plans): entry_check reports the files two or more live plans name

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: The plan review lists files other live plans also edit

**Files:**
- Modify: `skills/writing-plans/SKILL.md` (Execution Handoff, "### 1. Plan review"), only if Step 3 shows the failure
- Modify: `NOTICE` (the entry_check bullet, lines 356-362), only if `skills/writing-plans/SKILL.md` changes
- Create, outside the repository: `/tmp/plan54-micro/scenario.md`, `/tmp/plan54-micro/build_prompt.py`

**Interfaces:**
- Consumes: Task 1's `overlapping files:` field (`live plans:` and `shared:`) and its `--plan PATH` option.
- Produces: nothing that a later task reads.

The failure under test: after the plan is saved, the planner hands it to the human partner without checking whether another live plan edits the same files. At entry the new plan does not exist yet, so the entry check cannot report its overlaps. Only a rerun after the plan is saved can. writing-skills' Match the Form to the Failure classes this as an element omitted from output the agent already produces (the plan-review message), so the fix is structural: a slot in the message template, filled from a rerun that a conditional keyed to an observable predicate (where the plan is saved) sets up.

- [x] **Step 1: Build the micro-test kit outside the repository**

`/tmp/plan54-micro/run` is the working directory for every rep. It is never the repository, and each rep runs `claude -p --tools ""`, which cannot read files. Write `/tmp/plan54-micro/scenario.md`:

````markdown
You are a planning session in the agent-skills repository, in the worktree /Users/lowell/Projects/agent-skills/.claude/worktrees/widget-plan (branch claude/widget-plan). You are following the writing-plans skill, loaded below in full.

<skill name="writing-plans">
Base directory for this skill: /Users/lowell/.claude/skills/writing-plans

{SKILL}
</skill>

Where the session stands:

1. At the start, you ran `entry_check.py` from the repo root, as Save plans to says. It printed:

```text
plan ids:
  highest: 53 — 53-report-cache.md (claude/report-cache, worktree /Users/lowell/Projects/agent-skills/.claude/worktrees/report-cache)
  next free: 54
  collisions: none
overlapping files:
  live plans: 52-lint-runner.md (6 paths); 53-report-cache.md (9 paths)
  shared: none
```

2. You wrote the plan for specs/widget-export.md and saved it as specs/plans/54-widget-export.md. Its tasks' Files lines name skills/widget/SKILL.md, skills/widget/scripts/export.py, skills/widget/scripts/test_export.py, NOTICE and README.md.
3. You ran Self-Review and fixed what it found. The plan is committed.

What do you do next? Reply with the steps you take, in order, up to and including your next message to your human partner. Put each command you would run in its own fenced bash block, and quote the message in full. You cannot see any command's output in this reply: where the message depends on output you do not have yet, write it with a placeholder for that output.
````

Write `/tmp/plan54-micro/build_prompt.py`:

```python
'''Build a micro-test prompt: scenario.md with a writing-plans SKILL.md body inline.

Usage: python3 build_prompt.py SKILL_MD OUT
'''
import sys
from pathlib import Path

scenario = Path(__file__).with_name('scenario.md').read_text(encoding='utf-8')
skill = Path(sys.argv[1]).read_text(encoding='utf-8')
body = skill.split('\n---\n', 1)[1] if skill.startswith('---\n') else skill
Path(sys.argv[2]).write_text(scenario.replace('{SKILL}', body.strip()), encoding='utf-8')
```

Then build the control prompt from the committed, unedited skill:

```bash
mkdir -p /tmp/plan54-micro/run
git show HEAD:skills/writing-plans/SKILL.md > /tmp/plan54-micro/skill-control.md
uv run --no-project --python 3.13 python /tmp/plan54-micro/build_prompt.py /tmp/plan54-micro/skill-control.md /tmp/plan54-micro/prompt-control.md
grep -c 'entry_check\|overlapping files' /tmp/plan54-micro/prompt-control.md
```

Expected: the count is 3: the skill's **Save plans to** line, the scenario's line that says the check ran, and the scenario's `overlapping files:` line. Nothing else names the check. No line of either prompt may name the expected behavior ("rerun", "shared with", "other live plans"): `grep -n -i 'rerun\|shared with\|other live plans' /tmp/plan54-micro/prompt-control.md` prints nothing.

- [x] **Step 2: Run the RED control: five reps**

Run in the background. The reps are independent, so they run in parallel:

```bash
for i in 1 2 3 4 5; do (cd /tmp/plan54-micro/run && claude -p --model opus --tools "" --output-format json < ../prompt-control.md > ../control-$i.json) & done; wait
```

Then print each reply and its cost:

```bash
for f in /tmp/plan54-micro/control-*.json; do echo "== $f"; uv run --no-project --python 3.13 python -c "import json, sys; d = json.load(open(sys.argv[1])); print(d['result']); print('COST', d['total_cost_usd'])" "$f"; done
```

- [x] **Step 3: Score the control by hand**

Read every reply in full. These rules are fixed before any reply is read:

- **PASS:** before it quotes the plan-review message, the reply reruns the entry check (`entry_check.py`, with any arguments) or runs another command that compares this plan's files with other live plans' files (reading or searching plans 52 and 53, or other branches and worktrees, for these paths). The reply also passes if the message says which of the plan's files another live plan edits, or holds a placeholder for that.
- **FAIL:** anything else.
- **VOID:** an empty reply or an error result. Replace a void rep, and record that you did.

If the control passes in 4 or 5 reps, planners already do this unprompted: skip Steps 4-8, change no skill text, and record the five results in the completion notes. Otherwise go on.

- [ ] **Step 4: Edit the skill**

> Skipped: Step 3's rule. The RED control passed 5 of 5, so no skill text changed; nothing is deferred.

**Edit `skills/writing-plans/SKILL.md`: replace**

```markdown
### 1. Plan review

**"Plan complete and saved to `specs/plans/<id>-<spec-name>.md`. Please review
it before anything runs."**
```

**with**

```markdown
### 1. Plan review

Rerun `entry_check.py` as Save plans to runs it, and add `--plan <file>` when
the plan is saved outside `specs/plans/`. Each line under its `shared:` that
names your plan is a file that another live plan also edits. Put those lines
in the message:

**"Plan complete and saved to `specs/plans/<id>-<spec-name>.md`. Files other
live plans also edit: <the `shared:` lines that name this plan, or none>.
Please review it before anything runs."**
```

- [ ] **Step 5: Record the change in NOTICE**

> Skipped: Step 3's rule. The RED control passed 5 of 5, so no skill text changed; nothing is deferred.

The plan-review stage is a part that NOTICE says was adopted from upstream, and the entry check is an original work. NOTICE records the plan-review addition with the reporter, as it records prepare-handoff's addition to the same stage in a bullet of its own.

**Edit `NOTICE`: replace**

```text
    (writing-plans/scripts/test_entry_check.py), which report the plan
    ids in use on every branch, remote-tracking ref and worktree, and
    the next free one. Both are original works by Lowell Mason under
    the same MIT terms, as deferred_stats.py is (above). The skill's
    id rule now takes the next free id from that report.
```

**with**

```text
    (writing-plans/scripts/test_entry_check.py), which report the plan
    ids in use on every branch, remote-tracking ref and worktree, and
    the next free one, and the files that two or more live plans name.
    Both are original works by Lowell Mason under the same MIT terms,
    as deferred_stats.py is (above). The skill's id rule now takes the
    next free id from that report, and its plan-review message lists
    the files that the saved plan shares with other live plans.
```

- [ ] **Step 6: Run the GREEN arm: five reps**

> Skipped: Step 3's rule. The RED control passed 5 of 5, so no skill text changed; nothing is deferred.

```bash
uv run --no-project --python 3.13 python /tmp/plan54-micro/build_prompt.py skills/writing-plans/SKILL.md /tmp/plan54-micro/prompt-green.md
diff /tmp/plan54-micro/prompt-control.md /tmp/plan54-micro/prompt-green.md
```

Expected: the diff is exactly the Step 4 edit. Then run the reps in the background:

```bash
for i in 1 2 3 4 5; do (cd /tmp/plan54-micro/run && claude -p --model opus --tools "" --output-format json < ../prompt-green.md > ../green-$i.json) & done; wait
```

```bash
for f in /tmp/plan54-micro/green-*.json; do echo "== $f"; uv run --no-project --python 3.13 python -c "import json, sys; d = json.load(open(sys.argv[1])); print(d['result']); print('COST', d['total_cost_usd'])" "$f"; done
```

- [ ] **Step 7: Score GREEN by hand**

> Skipped: Step 3's rule. The RED control passed 5 of 5, so no skill text changed; nothing is deferred.

Read every reply under Step 3's rules. GREEN passes when:

- at least 4 of 5 reps PASS;
- each passing rep's message carries the files-other-live-plans-also-edit line, as a placeholder or `none`;
- every rep still asks the partner to review the plan before anything runs, and none starts executing.

Also record whether the passing reps converge on one rerun command. Five different command shapes mean that the wording does not bind. If GREEN fails, revise the Step 4 wording once, rebuild `prompt-green.md` and rerun the five reps. If it fails again, stop and bring both rounds to your human partner.

- [ ] **Step 8: Check and commit**

> Skipped: Step 3's rule. The RED control passed 5 of 5, so no skill text changed; nothing is deferred.

```bash
bash build/run_commit_lints.sh
```

Expected: `commit lints passed`.

```bash
git add skills/writing-plans/SKILL.md NOTICE
git commit -m "feat(writing-plans): the plan review lists files that other live plans also edit

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

Record both arms in the completion notes: each rep's verdict with a one-line quote of the deciding text, the costs and the date.

## Completion notes

**Task 1, Step 5 (2026-10-18, at `52b72ff`).** The run against this repository printed:

```text
overlapping files:
  live plans: 51-claude-code-drift-automation.md (9 paths); 52-write-with-asd-ste100.md (27 paths); 53-agent-skills-portability.md (31 paths); 54-entry-check-file-overlaps.md (4 paths)
  shared:
    CLAUDE.md: 52-write-with-asd-ste100.md, 53-agent-skills-portability.md
    NOTICE: 52-write-with-asd-ste100.md, 53-agent-skills-portability.md, 54-entry-check-file-overlaps.md
    README.md: 52-write-with-asd-ste100.md, 53-agent-skills-portability.md
    build/cc_guide/conformance.toml: 52-write-with-asd-ste100.md, 53-agent-skills-portability.md
    skills/writing-plans/SKILL.md: 53-agent-skills-portability.md, 54-entry-check-file-overlaps.md
```

Every known overlap is listed, and plan 45 is not. `build/cc_guide/conformance.toml` (plans 52 and 53) is an overlap that the 2026-10-18 hand check did not name. Plan 52's count includes seven `KIT/…` scratch-kit paths and two kit-relative `rules/*.md` markers. Plan 53's count includes the templated `specs/red-baseline-description-openings-<run-date>.md`. The report cannot see two things: `skills/writing-plans/scripts/entry_check.py`, which plan 53's Task 10 changes through a code block, and plan 53's new root file `LICENSE-andorra`. With `--plan` on a copy saved as `/tmp/plan54-copy.md`, the copy came last with 4 paths and shared all four with plan 54. A run took 0.45 s.

**Task 2, the RED control (2026-10-18).** Five reps of `claude -p --model opus --tools ""` (Claude Code 2.1.302, model `claude-opus-5-5`) ran from `/tmp/plan54-micro/run`. Each was one decision-only turn with the unedited SKILL.md body inline. All five PASS. Each reran `entry_check.py` before the plan-review message and put a shared-files line in that message:

1. PASS: "The run at session start happened before plan 54 existed, so its `shared: none` doesn't cover the files this plan touches."
2. PASS: "That first run also couldn't compare files: it reported `shared: none` while my plan had no Files lines."
3. PASS: "I ran `entry_check.py` before plan 54 existed, so its `shared: none` couldn't compare plan 54's files with anything."
4. PASS: "Its `shared: none` was worked out without plan 54's Files lines, so it couldn't have caught any overlap with them."
5. PASS: "When I first ran `entry_check.py`, plan 54 didn't exist yet. So its `shared: none` result couldn't check whether my files overlap with plans 52 and 53."

All five also rechecked the id for a collision. The five reps cost $1.61, and a one-line smoke test cost $0.23. Under Step 3's rule (4 or 5 of 5), Steps 4-8 were skipped, so `skills/writing-plans/SKILL.md` and `NOTICE` are unchanged. The reps keyed on Task 1's own output, a `shared: none` computed before their plan existed. Each rep saw that output next to the question. A long session, where the entry output is many turns back, was not tested.

**Process.** The plan was executed inline (executing-plans) in the session that wrote it, without the Execution Handoff's separate plan-review stop. The session brief's done-criteria called for the implementation. The owner chose a PR, and the PR is the review point.

**Final review (2026-10-18, base `456e3fb`, head `52b72ff`).** Two seats ran. The code-reviewer (Opus) returned "With fixes". Codex ran with `-m gpt-6-astra -c model_reasoning_effort=xhigh`, the owner's per-run choice because the config still names `gpt-6.1-sol`, exited 0 on its first launch and returned one P2 (`Codex reviewed 52b72ff`). The dispositions, all in `acb0047` unless stated:

- Codex P2: two differently named plans with identical text on a ref shared one blob read, so the second dropped out. Fixed: a blob's text is cached and added to every plan name.
- Review 1: NOTICE no longer describes the script fully. Not applied, because the owner had ruled to leave NOTICE as it is (D8).
- Review 2: a plan retired on an unmerged branch dropped out. Fixed per D5, with tests for a side-branch retirement, for `origin/HEAD` naming the default branch, and for the fallback when no default branch exists.
- Review 3: scratch-kit paths were counted. Fixed per D6. Plan 52's kit-relative `rules/short.md` and `rules/listed.md` still count, because `rules/` exists at the root.
- Review 4: `- Rename:`, `- Delete:` and `- Move:` lines are not read. Deferred per D7.
- Review 5: a new root entry is missed until some ref or worktree has it. Accepted as the cost of D6.
- Review 6: an `OSError` on a vanished or dangling worktree copy crashed the report. Fixed: such a copy adds no paths.
- Review 7: the docstring understated the accepted forms and the exit-2 cases. Fixed.
- Review 8: a line that starts with an inline triple-backtick span opened a fence. Fixed.
- Review 9: some behaviour was untested. Tests added for tilde fences, a heading Edit line, the `./`, `/`, `~` and whitespace spellings, `(0 paths)`, and id order with an id-less `--plan` file last.
- Review 10: the cross-plan notes, below.

**After the review fixes (`acb0047`), the real run printed:**

```text
overlapping files:
  live plans: 51-claude-code-drift-automation.md (9 paths); 52-write-with-asd-ste100.md (20 paths); 53-agent-skills-portability.md (31 paths); 54-entry-check-file-overlaps.md (4 paths); 54-test-suite-registry.md (9 paths)
  shared:
    CLAUDE.md: 52-write-with-asd-ste100.md, 53-agent-skills-portability.md, 54-test-suite-registry.md
    NOTICE: 52-write-with-asd-ste100.md, 53-agent-skills-portability.md, 54-entry-check-file-overlaps.md
    README.md: 52-write-with-asd-ste100.md, 53-agent-skills-portability.md
    build/CLAUDE.md: 51-claude-code-drift-automation.md, 54-test-suite-registry.md
    build/cc_guide/conformance.toml: 52-write-with-asd-ste100.md, 53-agent-skills-portability.md
    skills/writing-plans/SKILL.md: 53-agent-skills-portability.md, 54-entry-check-file-overlaps.md
```

Plan 52's count fell from 27 to 20 when D6 dropped its seven `KIT/…` paths.

**Finishing gate (2026-10-18, base `52b72ff`, head `240b9c7`).** Codex ran with the same per-run flags, exited 0 on its first launch and returned one P2 (`Codex reviewed 240b9c7`). Without `-z`, `git ls-tree` C-quotes a name with non-ASCII bytes, so D6's root filter missed a root directory such as `café/` that only a ref holds. Fixed in `c399b65` (+2 tests): both `ls-tree` calls now pass `-z`. The plan-file listing had the same gap: a plan whose filename has such bytes was dropped wherever only a ref held it, in the plan-ids scan since before this branch. The real run's `overlapping files:` field is unchanged.

**Cross-plan notes.**

- **Plan id 54 collides.** `54-test-suite-registry.md` (branch `claude/sweet-shamir-525703`, worktree `exciting-ritchie-bd33d6`) was committed while this plan was in its final review, and the `plan ids:` field reports the collision. It is the owner's call, settled at integration.
- **This plan names two files that no commit here edits.** Its Task 2 names `skills/writing-plans/SKILL.md` and `NOTICE`, but the edits to them were skipped. Under D5 the plan stays live until its branch merges, so until then the report lists both files as shared with plans 52 and 53.
- **Plan 53's suite count is stale.** Plan 53's Task 10 Step 6 records 27 tests for the writing-plans suite. After this branch merges the suite has 51. Plan 53 compares against "the count it had before this task", so its executor should take the count at that point.
