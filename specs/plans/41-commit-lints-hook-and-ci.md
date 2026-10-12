# Commit Lints from a Hook and CI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run this repository's six before-commit lints automatically, and retire conformance exception `commit-lints-in-prose`. A versioned git pre-commit hook gives fast local feedback. A GitHub Actions workflow is the authority on what reaches `main`.

**Architecture:** One bash runner, `build/run_commit_lints.sh`, runs all six checks from the repository root, reports every failure, and fails closed.

- **The hook:** `build/githooks/pre-commit` first checks that uv can run. If uv is missing, or a sandbox stops it from running, the hook warns on stderr and exits 0. Otherwise it hands off to the runner, so any lint failure blocks the commit. The hook is enabled per clone with `git config core.hooksPath build/githooks`.
- **CI:** `.github/workflows/lints.yml` runs the same runner on every pull request and on pushes to `main`.
- **Tests:** a pytest file drives the hook through throwaway clones of the repository.

**Tech Stack:** bash; git hooks (`core.hooksPath`); GitHub Actions (`actions/checkout`, `astral-sh/setup-uv`, pinned by SHA); Python 3.13 with pytest and PyYAML through `uv run`.

**Spec:** none. The source is `specs/deferred_items.md` § `35-claude-code-guide-conformance — 2026-10-04`, item "Run the before-commit lints from a hook or CI (plan 35 audit rows C-31, C-32)", which the 2026-10-11 `/deferred` pass selected for a plan. Its closure condition:

> a hook or CI runs `check_frontmatter.py`, `check_provenance.py`, `check_snippets.py` Tier 1, `check_conformance.py`, the `declared_dependencies` test and `sync_runtime_assets.py --check`, and exception `commit-lints-in-prose` is removed from `build/cc_guide/conformance.toml` in the same change, with `build/check_conformance.py` passing.

The audit rows are C-31 and C-32 in `specs/claude-code-conformance-audit-2026-10-04.md`. The guide's `mechanisms.overview` row says that deterministic, machine-checkable guidance goes in a hook, which "runs every time, costs no tokens, can't be ignored".

## Global Constraints

- **The six checks are exactly the closure condition's, and run from the repository root.** These are their commands:
  - `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py`
  - `uv run --python 3.13 python build/check_provenance.py`
  - `uv run --python 3.13 python build/check_snippets.py skills/`
  - `uv run --python 3.13 --with pyyaml python build/check_conformance.py`
  - `cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies`
  - `uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py --check`
- **The runner fails closed.** It runs all six even after one fails, then exits 1 and names every failed check on stderr. A missing `uv` fails every check, so the runner exits nonzero there too. CI depends on this.
- **The hook fails open only when uv itself cannot run.** That means `command -v uv` fails, or `uv run --no-project --python 3.13 python -c pass` fails. It then prints a line containing `commit lints skipped` to stderr and exits 0. Every other path hands off to the runner, so a lint failure blocks the commit. The hook mentions `git commit --no-verify` as the deliberate bypass.
- **The hook lints the working tree, not the staged snapshot.** `check_provenance.py` and `check_conformance.py` call `git ls-files` and `git check-ignore`, and the dependency test builds git repositories, so the checks need a real checkout. **Never use `git stash`** to isolate the staged content: every session and worktree of this repository shares one stash stack.
- **Unset git's environment before running checks.** Git exports `GIT_DIR`, `GIT_INDEX_FILE` and similar variables to hooks, and a check that runs git in another repository must not inherit them. The runner unsets `$(git rev-parse --local-env-vars)` before its first check.
- **Paths:**
  - runner: `build/run_commit_lints.sh`
  - hook: `build/githooks/pre-commit`
  - workflow: `.github/workflows/lints.yml`
  - tests: `build/test_commit_lints.py`

  The hook stays out of `hooks/`, because conformance's `hooks` kind (`hooks/*.sh`, `hooks/*.py`) means Claude Code hooks.
- **CI is minimal, because the repository is public.**
  - It declares `permissions: contents: read`.
  - It triggers on `push` to `main` and on `pull_request`, never on `pull_request_target`.
  - Each action is pinned by its full commit SHA, with the tag in a comment: `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` (v7.0.1) and `astral-sh/setup-uv@1c37ad07a6a961277cf70c0d37d6f313000f5884` (v10.3.0). These were resolved on 2026-10-11.
- **Enabling the hook is an owner step, after merge.** `git config core.hooksPath build/githooks` writes shared repository config, so it switches every sibling session and worktree at once. No task runs it outside a throwaway clone.
- **`CLAUDE.md` stays under the `claude-md-size` limit of 200 lines** (177 at plan time).
- **Python style:** single quotes, Python 3.13. Tests run from inside `build/` with bare imports.
- **State test changes as +N deltas**, never absolute totals.
- **Work in a worktree** created with the using-git-worktrees skill, and commit from it.

## Decisions

- **D1** (owner, plan writing, 2026-10-11): use a git hook plus CI, rather than either alone or a Claude Code hook. The hook fails open only when uv cannot run, for example in a sandbox that cannot reach the uv cache; CI is the authority. Applied in: Global Constraints, Tasks 1–3.

---

### Task 1: The runner and the pre-commit hook

**Files:**
- Create: `build/run_commit_lints.sh`
- Create: `build/githooks/pre-commit`
- Create: `build/test_commit_lints.py`

**Interfaces:**
- Produces:
  - `bash build/run_commit_lints.sh` exits 0 when all six checks pass. Otherwise it exits 1, after printing `commit lints failed: <names>` to stderr. The names are drawn from `check_frontmatter check_provenance check_snippets check_conformance declared_dependencies sync_runtime_assets`.
  - `build/githooks/pre-commit` prints `pre-commit: ... commit lints skipped (CI still runs them)` and exits 0 when uv cannot run. Otherwise it hands off to the runner.
  - Task 2 consumes the runner's invocation string, `bash build/run_commit_lints.sh`.

- [ ] **Step 1: Write the failing tests**

Create `build/test_commit_lints.py`:

```python
'''Tests for the commit-lint runner, its pre-commit hook and its CI workflow.

Each hook test clones this repository's HEAD into a temporary directory,
copies in the working-tree runner and hook (so the tests exercise the files
under edit), points core.hooksPath at the hook, and commits. Each clone runs
the full lint set, so this file takes about a minute.
'''
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
RUNNER = Path('build/run_commit_lints.sh')
HOOK = Path('build/githooks/pre-commit')
GENERATED = Path('runtimes/gemini/agents/code-reviewer.md')


def clean_env(**extra):
    '''os.environ without git's GIT_* variables, plus extra.'''
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(extra)
    return env


def git(repo, *args, env=None, check=True):
    return subprocess.run(['git', '-C', str(repo), *args], capture_output=True,
                          text=True, env=env or clean_env(), check=check)


def head(repo):
    return git(repo, 'rev-parse', 'HEAD').stdout.strip()


def commit(repo, *args, env=None):
    return git(repo, 'commit', '--quiet', *args, env=env, check=False)


def no_uv_path(tmp_path):
    '''A PATH directory holding git and bash but not uv.'''
    bindir = tmp_path / 'bin'
    bindir.mkdir()
    for tool in ('git', 'bash'):
        (bindir / tool).symlink_to(shutil.which(tool))
    return str(bindir)


@pytest.fixture
def clone(tmp_path):
    dst = tmp_path / 'repo'
    subprocess.run(['git', 'clone', '--quiet', '--no-checkout', str(REPO), str(dst)],
                   check=True, env=clean_env())
    git(dst, 'checkout', '--quiet', head(REPO))
    for rel in (RUNNER, HOOK):
        (dst / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / rel, dst / rel)
    git(dst, 'config', 'user.name', 'lint-test')
    git(dst, 'config', 'user.email', 'lint-test@example.invalid')
    git(dst, 'config', 'core.hooksPath', 'build/githooks')
    return dst


def test_runner_and_hook_are_executable():
    assert os.access(REPO / RUNNER, os.X_OK)
    assert os.access(REPO / HOOK, os.X_OK)


def test_clean_commit_passes(clone):
    before = head(clone)
    result = commit(clone, '--allow-empty', '-m', 'clean')
    assert result.returncode == 0, result.stdout + result.stderr
    assert head(clone) != before


def test_frontmatter_violation_is_refused(clone):
    skill = clone / 'skills' / 'explore-data' / 'SKILL.md'
    text = skill.read_text()
    skill.write_text(re.sub(r'^description:.*$', 'description: ""', text,
                            count=1, flags=re.MULTILINE))
    before = head(clone)
    result = commit(clone, '-am', 'bad frontmatter')
    assert result.returncode != 0
    assert head(clone) == before
    assert 'check_frontmatter' in result.stdout + result.stderr


def test_runtimes_hand_edit_is_refused(clone):
    target = clone / GENERATED
    target.write_text(target.read_text() + '\nhand edit\n')
    before = head(clone)
    result = commit(clone, '-am', 'hand edit')
    assert result.returncode != 0
    assert head(clone) == before
    assert 'sync_runtime_assets' in result.stdout + result.stderr


def test_hook_fails_open_without_uv(clone, tmp_path):
    env = clean_env(PATH=no_uv_path(tmp_path))
    before = head(clone)
    result = commit(clone, '--allow-empty', '-m', 'no uv', env=env)
    assert result.returncode == 0, result.stderr
    assert head(clone) != before
    assert 'commit lints skipped' in result.stderr


def test_runner_fails_closed_without_uv(clone, tmp_path):
    env = clean_env(PATH=no_uv_path(tmp_path))
    result = subprocess.run(['bash', str(clone / RUNNER)], cwd=clone,
                            capture_output=True, text=True, env=env)
    assert result.returncode != 0
```

- [ ] **Step 2: Run the tests and watch them fail**

Run: `cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q -rfE test_commit_lints.py`
Expected: no test passes. `test_runner_and_hook_are_executable` fails, and the five clone tests error in the fixture with `FileNotFoundError` for `build/run_commit_lints.sh`. Read each failure line. A test that errors for any other reason is a test bug: fix it before going on.

- [ ] **Step 3: Write the runner**

Create `build/run_commit_lints.sh`:

```bash
#!/usr/bin/env bash
# The six commit lints that CLAUDE.md lists under Commands. Fails closed: exit 1
# when any check fails or cannot run. Runs every check, then names the failures.
# Run by build/githooks/pre-commit and by .github/workflows/lints.yml.
set -uo pipefail
root="$(git rev-parse --show-toplevel)" || exit 1
cd "$root" || exit 1
# Git exports GIT_DIR, GIT_INDEX_FILE and the like to hooks; a check that runs
# git in another repository must not inherit them.
unset $(git rev-parse --local-env-vars)
failed=()
run() {
  local name="$1"
  shift
  echo "== $name"
  if ! "$@"; then
    failed+=("$name")
  fi
}
run check_frontmatter uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
run check_provenance uv run --python 3.13 python build/check_provenance.py
run check_snippets uv run --python 3.13 python build/check_snippets.py skills/
run check_conformance uv run --python 3.13 --with pyyaml python build/check_conformance.py
run declared_dependencies bash -c 'cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies'
run sync_runtime_assets uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py --check
if [ "${#failed[@]}" -gt 0 ]; then
  echo "commit lints failed: ${failed[*]}" >&2
  exit 1
fi
echo 'commit lints passed'
```

- [ ] **Step 4: Write the hook**

Create `build/githooks/pre-commit`:

```bash
#!/usr/bin/env bash
# Pre-commit: run the six commit lints (build/run_commit_lints.sh) on the working
# tree. Enable once per clone: git config core.hooksPath build/githooks
# Fails open, with a warning, only when uv itself cannot run here (missing, or a
# sandbox that blocks its cache); .github/workflows/lints.yml still gates what
# reaches main. A lint failure blocks the commit; git commit --no-verify skips
# the hook deliberately.
root="$(git rev-parse --show-toplevel)" || exit 1
if ! command -v uv >/dev/null 2>&1; then
  echo 'pre-commit: uv not found; commit lints skipped (CI still runs them)' >&2
  exit 0
fi
if ! (cd "$root" && uv run --no-project --python 3.13 python -c pass) >/dev/null 2>&1; then
  echo 'pre-commit: uv cannot run here; commit lints skipped (CI still runs them)' >&2
  exit 0
fi
exec bash "$root/build/run_commit_lints.sh"
```

Then make both executable: `chmod +x build/run_commit_lints.sh build/githooks/pre-commit`

- [ ] **Step 5: Run the tests and watch them pass**

Run: `cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q -rfE test_commit_lints.py`
Expected: 6 passed. If `test_clean_commit_passes` fails, read the runner's `== <name>` sections in the failure output to find the check that failed on a clean clone, and report it: the committed HEAD should pass all six.

- [ ] **Step 6: Run the runner on the worktree, and time it**

Run, from the worktree root: `time bash build/run_commit_lints.sh`
Expected: `commit lints passed` and exit 0. Record the wall time in the ledger. If it is over 60 s, stop and report: a slower hook is an owner decision on scoping.

- [ ] **Step 7: Commit**

```bash
git add build/run_commit_lints.sh build/githooks/pre-commit build/test_commit_lints.py
git commit -m "feat(build): run the six commit lints from a pre-commit hook"
```

This commit is the first one made after `build/githooks/pre-commit` exists, but this clone's `core.hooksPath` is unset, so the hook does not run on it. That is expected.

---

### Task 2: The CI workflow

**Files:**
- Create: `.github/workflows/lints.yml`
- Modify: `build/test_commit_lints.py` (append two tests)

**Interfaces:**
- Consumes: `bash build/run_commit_lints.sh` (Task 1).
- Produces: a workflow job that runs the runner on `pull_request` and on `push` to `main`.

- [ ] **Step 1: Write the failing tests**

Append to `build/test_commit_lints.py`. The import goes with the file's other imports at the top; the rest goes at the end:

```python
import yaml
```

```python
WORKFLOW = REPO / '.github' / 'workflows' / 'lints.yml'
PINNED = re.compile(r'^[\w.-]+/[\w.-]+@[0-9a-f]{40}$')


def workflow():
    return yaml.safe_load(WORKFLOW.read_text())


def test_workflow_triggers_and_permissions():
    wf = workflow()
    on = wf.get('on', wf.get(True))  # YAML 1.1 reads a bare `on` key as True
    assert set(on) == {'push', 'pull_request'}
    assert on['push']['branches'] == ['main']
    assert wf['permissions'] == {'contents': 'read'}


def test_workflow_pins_actions_and_runs_the_runner():
    steps = [step for job in workflow()['jobs'].values() for step in job['steps']]
    uses = [step['uses'] for step in steps if 'uses' in step]
    assert uses and all(PINNED.match(u) for u in uses), uses
    assert any(step.get('run') == f'bash {RUNNER}' for step in steps)
```

- [ ] **Step 2: Run them and watch them fail**

Run: `cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q -rfE test_commit_lints.py -k workflow`
Expected: 2 failed, each with `FileNotFoundError` for `.github/workflows/lints.yml`.

- [ ] **Step 3: Write the workflow**

Create `.github/workflows/lints.yml`:

```yaml
name: lints

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  commit-lints:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: astral-sh/setup-uv@1c37ad07a6a961277cf70c0d37d6f313000f5884 # v10.3.0
      - run: bash build/run_commit_lints.sh
```

- [ ] **Step 4: Run the tests and watch them pass**

Run: `cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q -rfE test_commit_lints.py`
Expected: 8 passed (+2).

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/lints.yml build/test_commit_lints.py
git commit -m "ci: run the commit lints on pull requests and on main"
```

The workflow first runs when the branch's pull request opens. finishing-a-development-branch reads that run; a check that fails only in CI is fixed on this branch before merge.

---

### Task 3: Document the hook, and retire the exception

**Files:**
- Modify: `build/cc_guide/conformance.toml:843-852` (delete the `commit-lints-in-prose` exception)
- Modify: `CLAUDE.md:122` (the comment above the lint commands) and `CLAUDE.md:126` (a test command after them)
- Modify: `build/CLAUDE.md:21` (a paragraph after the runtime-support paragraph)

**Interfaces:**
- Consumes: the runner, hook and workflow paths (Tasks 1–2).
- Produces: the closure condition: the exception is gone and `check_conformance.py` passes.

- [ ] **Step 1: Delete the exception**

In `build/cc_guide/conformance.toml`, delete this block and the blank line after it:

```toml
[[exception]]
id = 'commit-lints-in-prose'
type = 'gap'
sections = ['mechanisms.overview']
artifacts = ['CLAUDE.md', 'build/CLAUDE.md']
guide = 'A deterministic, machine-checkable rule belongs in a hook, not in prose.'
reason = 'The before-commit lints and the rule against hand-editing runtimes/ are prose that no hook or CI enforces.'
evidence = 'Audit rows C-31, C-32; owner gate 2026-10-04.'
tracked_in = 'deferred item: run the before-commit lints from a hook or CI'
```

Run: `uv run --python 3.13 --with pyyaml python build/check_conformance.py`
Expected: exit 0. If it fails, read the finding before going on: a check that needs the exception means the gap is not closed.

- [ ] **Step 2: Document the hook in `CLAUDE.md`**

In `CLAUDE.md`, replace this line:

```text
# Frontmatter, provenance and guide-conformance lints (run before committing any Claude Code artifact)
```

with these four lines:

```text
# Commit lints: these three, the dependency-drift test, snippet Tier 1 and sync_runtime_assets.py --check make six.
# build/run_commit_lints.sh runs all six; build/githooks/pre-commit runs it on each commit once enabled (once per
# clone: git config core.hooksPath build/githooks); .github/workflows/lints.yml runs it on pull requests and main.
# Frontmatter, provenance and guide-conformance lints (run before committing any Claude Code artifact)
```

Then, directly after the line `uv run --python 3.13 --with pyyaml python build/check_conformance.py` that follows them, insert a blank line and these two lines:

```text
# Commit-lint runner, hook and workflow tests: throwaway clones, each running the full lint set (about a minute)
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_commit_lints.py
```

- [ ] **Step 3: Document the files in `build/CLAUDE.md`**

In `build/CLAUDE.md`, after the paragraph ending `so a skill edit can fail it.` (line 21), insert a blank line and this paragraph:

```text
`run_commit_lints.sh` runs the six commit lints that the root `CLAUDE.md`
lists and fails closed. `githooks/pre-commit` runs it as a git hook, failing
open only when uv cannot run, and `../.github/workflows/lints.yml` runs it in
CI. `test_commit_lints.py` drives both through throwaway clones.
```

- [ ] **Step 4: Run the gates**

Run, from the worktree root:
- `wc -l CLAUDE.md`. Expected: under 200 (177 at plan time plus 6).
- `bash build/run_commit_lints.sh`. Expected: `commit lints passed`.
- `cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q -rfE test_commit_lints.py test_runtime_support.py`. Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add build/cc_guide/conformance.toml CLAUDE.md build/CLAUDE.md
git commit -m "docs: document the commit-lint hook and CI, and retire commit-lints-in-prose"
```

---

## After merge (owner)

1. Enable the hook in the main checkout. This writes shared repository config, so every worktree and sibling session picks it up at once. A branch cut before the merge has no `build/githooks/`, and git runs no hook there.

   ```bash
   git -C ~/Projects/agent-skills config core.hooksPath build/githooks
   ```

2. Check that the pull request's `lints` workflow run passed, and that the first push to `main` after the merge passes too.
