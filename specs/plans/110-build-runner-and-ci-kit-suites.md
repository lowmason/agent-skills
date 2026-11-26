# Build Runner, Shared Git Module and CI Kit Suites Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** One stdlib-only git module replaces the git helper copies in `build/`, `build/run_suites.py` gets the plan 55 hardening and its missing tests, and the weekly `versions-drift` job stops failing the three kit suites on its 3.13 pass.

**Architecture:** A new `build/git_listing.py` holds `git_env`, `git_reason`, the `git ls-files --cached --others --exclude-standard -z` listing and one error type. `run_suites.py`, `check_conformance.py` and `versions_check.py` import it, and each keeps its own filter and its own error text. `install.py` keeps its own copy, because it must run standalone. The kit failures have two causes, both outside the kits: the drift workflow's shallow checkout, and Linux's real `/tmp`. So the fix is two lines in `.github/workflows/versions-drift.yml`, pinned by a test, and no frozen kit changes.

**Tech Stack:** Python (the dev Python in `build/versions.toml`), stdlib only in the runner and the new module, pytest, git, GitHub Actions.

**Spec:** none. The requirements are five items in `specs/deferred_items.md`:
- section `55-test-suite-registry`: "Harden `build/run_suites.py`…" (the hardening item, parts (a) to (f)), "Close the test gaps in `build/test_run_suites.py`…" (the test-gaps item) and "Share the git helpers that `build/run_suites.py`, `build/check_conformance.py` and `install.py`…" (the share item);
- section `66-package-versions — 2026-10-27`: "A fourth copy of the git file listing now exists…" (the fourth-copy item);
- section `deferred-2026-11-26-parallel`: "**Three kit suites fail in the weekly `versions-drift` job…**" (the kit item).

## Global Constraints

- `build/run_suites.py` and `build/git_listing.py` import only the standard library (and `run_suites.py` its sibling `versions`). The runner is the commit lint's entry point, and `check_conformance.py` imports pyyaml.
- Module and test basenames stay unique across `build/`, `build/cc_guide/` included (`build/CLAUDE.md`, last line): `git_listing.py`, `test_git_listing.py`.
- `check_conformance.py` keeps `SetupError`, the names `git_env` and `kept_files`, and its error texts (`cannot list the files git keeps under {root} (…)`, `cannot read the git index modes under {root} (…)`).
- The runner call that `build/versions.py:392` builds (`run_suites.py --all --extras` with `--pin`, `--python` or `--no-freeze`) keeps working: `build/test_versions.py::test_verify_passes_when_every_step_passes` stays green.
- `install.py` keeps its own `git_env` and `kept_files`.
- The shell form of a run stays character for character the same: no `--with=dep`.
- Files outside this plan's set are not touched. The set: `build/git_listing.py`, `build/test_git_listing.py`, `build/run_suites.py`, `build/test_run_suites.py`, `build/check_conformance.py`, `build/versions_check.py`, `build/test_versions_check.py` (one import line), `build/test_commit_lints.py` (one precondition line, one new test), `build/CLAUDE.md` (one sentence), `.github/workflows/versions-drift.yml`, and `specs/deferred_items.md` at completion. Lane 1 owns `skills/classification-codes/**`, `skills/geographic-codes/**`, `skills/bls-data-context/**`, and may edit `build/suites.toml`, `NOTICE` and `README.md`. Lane 2 owns `build/cc_guide/**` and may edit the probes paragraph of `build/CLAUDE.md`.
- No edit inside `specs/baseline/red-baseline-cc-guide-verifier-recall/kit`, `specs/baseline/red-baseline-completion-triage/guard-kit` or `specs/baseline/red-baseline-handoff-rerun/kit` without the owner's word (an owner gate). Task 4 needs none.
- Test counts are stated as deltas (`+N`), never as absolute totals.
- `build/test_commit_lints.py` clones HEAD and copies only the runner and the hook from the working tree. Commit the new module before running that suite, or its results mislead.

## Review Focus

1. A git hook or shell that exports `GIT_DIR` or `GIT_INDEX_FILE` for another repository: the listing still names the files of `root`. Pinned by `test_kept_paths_ignores_a_foreign_git_dir` (Task 1).
2. A test folder that sits under a folder pytest skips while it recurses (`skills/x/scripts/build/`): `--check` names it, instead of passing a test that never runs. Pinned by `test_check_flags_a_test_directory_that_pytest_skips` (Task 2).
3. A suite whose own `dir` is named like a skipped folder (the real `build` suite): it is still collected, and `--check` stays clean. Pinned by `test_a_suite_dir_named_like_a_skipped_folder_is_collected` (Task 2).
4. `--all` with an inner suite under a folder the outer suite skips: the inner suite runs, because the outer one never collects it. Pinned by `test_all_runs_an_inner_suite_the_outer_one_skips` (Task 2).
5. The drift job on a clean Linux runner: full history for `git archive` of old kit commits, and a temp root outside `/tmp`. Pinned by `test_versions_drift_fetches_full_history_and_keeps_tmp_off_slash_tmp` (Task 4), and checked by a dispatched run (Task 4, Task 5).

## Decisions

- **D1** (owner, brief, 2026-11-26): this plan covers exactly the five items above. The kit item is its own task (Task 4), so the owner can drop it at plan review. Tasks avoid lane 1's and lane 2's files. Applied in: Global Constraints, Task 4.

## Planning findings

Reproduced on 2026-11-26 from `main` at `4449060`, in throwaway clones under `/tmp`, and read from the log of run 45125177458.

- **Kit causes (a) and (d) are one cause.** In a `git clone --depth 1` clone, `handoff-rerun-kit` fails 22 tests and `completion-triage-guard-kit` 25, all in `test_rerun_runner.py`, with `fatal: not a tree object`. `test_unstripped_field_fails_the_rep` is among them. The run log shows the same text under its `assert 2 == 4`. In a full clone all three kits pass (288, 301 and 325 tests). The commits that the runner tests archive (`92f6a379`, `d778c3e5`, `7137e5ec`) are on `origin/main`, so `fetch-depth: 0` reaches them.
- **Kit causes (b) and (c) are one cause, and it is not letter case.** The kit item's guess for (b) was a Linux case problem. The cause is `/tmp`. On Linux, pytest's `tmp_path` is under a real `/tmp`. (b): `extract.spelled()` maps only a lower-case `/tmp` to `/private/tmp`, so `classify('/TMP/…/REAL/.ssh', …)` with a real home under `/tmp` returns `None` (checked by a direct call). (c): the kit's autouse fixture sets `HOME` under `tmp_path`. `grade.resolve('~/a')` maps `/tmp/…` to `/private/tmp/…`, while the expected value from `Path.resolve()` keeps `/tmp` (the log's diff at `test_vr_grade.py:1057`). On macOS, `tmp_path` is under `/private/var/folders`, so neither test can fail. With `TMPDIR` set to the runner's temp folder, `tmp_path` leaves `/tmp` on Linux too. All three kits pass with a temp root under `$HOME` (the analog of `$RUNNER_TEMP`, under `/home/runner`).
- **The test-gaps item's last point is out of date.** `test_unregistered_suite_is_refused` (`build/test_commit_lints.py:186`) now plants its file in `tools/scan`, not in `skills/tech-debt/scripts`. The risk is the same, so Task 3 adds the precondition for `tools/scan`.
- **No test folder is hidden today.** Checked against pytest 9.2.0's default `norecursedirs`, no registered suite has a test folder below a skipped name, and no suite sets its own `norecursedirs`.

## Plan review asks

1. **Kit fix (b) and (c).** Recommended: `TMPDIR: ${{ runner.temp }}` on the drift step (Task 4), no kit edits. It changes the temp folder of every suite in the drift job, not only the kits. Fallback, an owner gate: a platform condition in `test_rerun_extract.py` of the two rerun kits (`upper` form) and in `test_vr_grade.py` (line 1057), with no new freeze.
2. **Hardening (a).** Recommended: a new `--check` finding for a test folder under a skipped name, matched only below the containing suite's `dir` (Task 2). The other option is a docstring note only.
3. **Order.** Recommended, from the brief: the shared module first (Task 1), then the hardening (Task 2), then the test gaps (Task 3), then the workflow (Task 4).
4. **Kit item's Done check.** Recommended: a dispatched run of the branch's workflow before the merge (`gh workflow run versions-drift.yml --ref <branch>`) as the evidence for the tick, then one dispatch on `main` after the execution PR merges, as confirmation (Task 5). The brief's default was the post-merge dispatch only.

---

### Task 1: Shared git module

Closes the share item and the fourth-copy item. No behavior changes, except that `versions_check.py` now decodes paths with `os.fsdecode` instead of a strict `.decode()`.

**Files:**
- Create: `build/git_listing.py`, `build/test_git_listing.py`
- Modify: `build/run_suites.py:178-200` (drop `git_env`, `pytest_dirs` uses the module), `build/check_conformance.py:259-286` (drop the copies, import them), `build/versions_check.py:21,45-51`, `build/test_versions_check.py:13`, `build/test_run_suites.py:165`, `build/CLAUDE.md` (one sentence)

**Interfaces:**
- Produces, in `build/git_listing.py`:
  - `class GitError(Exception)`: the listing failed. `str(exc)` is git's own stderr when git ran, else the text of the `OSError`.
  - `git_env() -> dict[str, str]`: moved unchanged from `check_conformance.py:259`.
  - `git_reason(exc: Exception) -> str`: moved unchanged from `check_conformance.py:267`.
  - `kept_paths(root: Path) -> list[str]`: the repo-relative POSIX paths that `git ls-files --cached --others --exclude-standard -z` prints under `root`, in git's order, decoded with `os.fsdecode`, tracked files deleted from the working tree included. Run with `cwd=root, env=git_env()`. Raises `GitError(git_reason(exc))` on `OSError` or `subprocess.CalledProcessError`, from `git_env()` too.
- The callers keep their filters: `check_conformance.kept_files` keeps `exists() or is_symlink()`, sorts, and raises `SetupError(f'cannot list the files git keeps under {root} ({exc})')`. `run_suites.pytest_dirs` keeps `is_file()` and still returns `None` on `GitError` (Task 2 changes that). `versions_check.live_files` keeps `is_file()` and its other filters, and lets `GitError` propagate.
- `check_conformance` imports `git_env` and `git_reason` from the module, so `cc.git_env` and `cc.git_reason` stay importable.

- [ ] **Step 1: Write the failing tests in `build/test_git_listing.py`** (+7)
  - `test_git_env_drops_repo_local_variables`: with `GIT_DIR`, `GIT_INDEX_FILE` and `LANE3_KEEP` set, `git_env()` has `LANE3_KEEP` and neither git variable.
  - `test_git_reason_prefers_gits_stderr`: `CalledProcessError(128, ['git'], stderr=b'fatal: x\n')` gives `'fatal: x'`. `OSError('no git')` gives `'no git'`.
  - `test_kept_paths_lists_tracked_untracked_and_deleted_but_not_ignored`: a repo with tracked `a.md`, tracked-then-deleted `gone.md`, untracked `b.md` and ignored `c.log` (`.gitignore`: `*.log`). `sorted(kept_paths(root)) == ['.gitignore', 'a.md', 'b.md', 'gone.md']`.
  - `test_kept_paths_ignores_a_foreign_git_dir`: `GIT_DIR` and `GIT_INDEX_FILE` point at a second repo, and `kept_paths(root)` still lists `root`'s files.
  - `test_kept_paths_outside_a_repo_raises_with_gits_reason`: `GIT_CEILING_DIRECTORIES=tmp_path.parent`, `LC_ALL=C`. `pytest.raises(GitError, match='not a git repository')`.
  - `test_kept_paths_without_git_raises`: `PATH` set to an empty folder. `pytest.raises(GitError)`.
  - `test_the_module_imports_only_the_standard_library`: every top-level name that an `ast.Import` or `ast.ImportFrom` in `git_listing.py` names is in `sys.stdlib_module_names`.

  Every test that runs git sets `GIT_CONFIG_GLOBAL=os.devnull` and `GIT_CONFIG_NOSYSTEM=1`, through a module-level autouse fixture.

- [ ] **Step 2: Run them and see them fail**

  Run: `cd build && uv run --with pytest python -m pytest -q test_git_listing.py`
  Expected: collection error, `ModuleNotFoundError: No module named 'git_listing'`.

- [ ] **Step 3: Create `build/git_listing.py`** with the Interfaces above. Its docstring says who imports it, and that `install.py` keeps its own copy because it runs standalone.

- [ ] **Step 4: Run the new tests**

  Run: `cd build && uv run --with pytest python -m pytest -q test_git_listing.py`
  Expected: `7 passed`.

- [ ] **Step 5: Re-point the three callers and two test imports.** In `check_conformance.py`, `run_suites.py` and `versions_check.py`, replace each copy with the module, as Interfaces says. In `test_versions_check.py:13` and `test_run_suites.py:165`, take `git_env` from `git_listing`. Add one sentence to `build/CLAUDE.md`, after the `suites.toml` paragraph: "`git_listing.py` holds the stdlib-only git helpers (`git_env`, `git_reason`, the kept-files listing) that `run_suites.py`, `check_conformance.py` and `versions_check.py` share; `install.py` keeps its own copy, since it runs standalone."

- [ ] **Step 6: Confirm that no copy is left**

  Run: `command grep -rn -e 'ls-files.*--cached' -e 'local-env-vars' build/*.py`
  Expected: only `build/git_listing.py` lines.

- [ ] **Step 7: Run the affected suites**

  Run: `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_git_listing.py test_run_suites.py test_check_conformance.py test_versions_check.py test_versions.py`
  Expected: all pass. The counts change only by the +7 of Step 1.

- [ ] **Step 8: Commit**

  ```bash
  git add build/git_listing.py build/test_git_listing.py build/run_suites.py build/check_conformance.py build/versions_check.py build/test_versions_check.py build/test_run_suites.py build/CLAUDE.md
  git commit -m "refactor(build): share the git helpers in one stdlib module"
  ```

### Task 2: Harden `build/run_suites.py`

Closes the hardening item, parts (a) to (f).

**Files:**
- Modify: `build/run_suites.py`, `build/test_run_suites.py`

**Interfaces:**
- Consumes: `git_listing.kept_paths`, `git_listing.GitError` (Task 1).
- Produces, in `run_suites.py`:
  - `NORECURSE: tuple[str, ...] = ('*.egg', '.*', '_darcs', 'build', 'CVS', 'dist', 'node_modules', 'venv', '{arch}')`: pytest's default `norecursedirs`, pinned by a test against the installed pytest.
  - `skipped_part(path: str, suite_dir: str) -> str | None`: the first path part below `suite_dir` that matches a `NORECURSE` pattern (`fnmatchcase`), else `None`. `suite_dir`'s own parts never count.
  - `pytest_dirs(root: Path) -> set[str]`: as now, but raises `GitError` instead of returning `None`.
  - `EXIT_OK = 0`, `EXIT_FAILED = 1`, `EXIT_USAGE = 2`, used by every `return` of an exit status.

- [ ] **Step 1: Write the failing tests** (+8, and one changed test)
  - (a) `test_check_flags_a_test_directory_that_pytest_skips`: `COVERED` plus `skills/alpha/scripts/build/test_y.py`. `findings(root) == ["skills/alpha/scripts/build: holds pytest files, but pytest skips 'build' below skills/alpha/scripts, so no suite collects it"]`.
  - (a) `test_a_suite_dir_named_like_a_skipped_folder_is_collected`: a registry with a suite `name = 'build'`, `dir = 'build'`, and the file `build/test_b.py`. `findings(root) == []`.
  - (a) `test_all_runs_an_inner_suite_the_outer_one_skips`: `container()` returns `None` for a suite with `dir = 'tools/build'` inside `tools`, so `--all` runs it.
  - (a) `test_norecurse_is_pytests_default(request)`: `set(rs.NORECURSE) == set(request.config.getini('norecursedirs'))`.
  - (b) three new `test_validate_refuses` cases: `with = ['pytest', '--index-url=x']`, `extras = ['-e.']` and `pythons = ['-p']`. Each gives `"suite 1 (a): '<key>' entries must not start with '-'"`.
  - (c) `test_an_option_between_suite_names_applies_to_all`: `main(['alpha', '--extras', 'outer'], …)` runs `alpha` with `--with arviz>=1.0`, then `outer`.
  - (d) change `test_check_fails_closed_outside_a_git_repository`: with `GIT_CEILING_DIRECTORIES=tmp_path.parent` and `LC_ALL=C`, the one finding starts with `'build/suites.toml: git ls-files failed ('`, contains `'not a git repository'` and ends with `'), so the test directories are unknown'`.

- [ ] **Step 2: Run them and see them fail**

  Run: `cd build && uv run --with pytest python -m pytest -q test_run_suites.py`
  Expected: the new tests and the changed one fail. (c) fails with `SystemExit: 2` (argparse: "unrecognized arguments").

- [ ] **Step 3: Implement (a) to (d) in `build/run_suites.py`**
  - (a) In `check()`, a found folder counts as covered only when some containing suite has `skipped_part(d, suite.dir) is None`. When every containing suite skips it, report it with the deepest containing suite (longest `dir`) and its skipped part, in the text of Step 1. `container()` also requires `skipped_part(suite.dir, other.dir) is None`. The `NORECURSE` comment says that no suite sets its own `norecursedirs` today.
  - (b) In `validate()`, refuse an entry of `with`, `extras` or `pythons` that starts with `-`.
  - (c) `parser.parse_intermixed_args(argv)`, in place of `parse_args`.
  - (d) `check()` catches `GitError` and reports `f'{REGISTRY}: git ls-files failed ({exc}), so the test directories are unknown'`.

- [ ] **Step 4: Run the tests**

  Run: `cd build && uv run --with pytest python -m pytest -q test_run_suites.py`
  Expected: all pass.

- [ ] **Step 5: Implement (e) and (f)**, which no test drives
  - (e) The three `EXIT_*` constants replace the bare exit literals. Add docstrings to `list_suites()` and `main()`. Add a comment on the `[:1]`: only the first out-of-order pair is reported, since one line is enough to point at the fix.
  - (f) The module docstring says "From the repo root:", not "From any directory in the repo:".

- [ ] **Step 6: Run the runner's suites, its caller and the lint**

  Run: `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_run_suites.py test_versions.py test_versions_check.py && cd .. && uv run python build/run_suites.py --check && uv run python build/run_suites.py --list hooks`
  Expected: all pass, `suite registry ok`, and the `hooks` command line unchanged from before this task.

- [ ] **Step 7: Commit**

  ```bash
  git add build/run_suites.py build/test_run_suites.py
  git commit -m "fix(build): harden run_suites.py (plan 55 review minors)"
  ```

### Task 3: Close the test gaps of `build/test_run_suites.py`

Closes the test-gaps item. These tests are written against correct code, so they pass at once. Each one names the mutant it kills, and Step 2 shows that it does.

**Files:**
- Modify: `build/test_run_suites.py`, `build/test_commit_lints.py:186-199` (one precondition line)

**Interfaces:**
- Consumes: `rs.validate`, `rs.check`, `rs.main`, `rs.run_subprocess`, `rs.Run`, `rs.Suite` (unchanged names).

- [ ] **Step 1: Write the tests** (+14)
  - An autouse fixture sets `GIT_CEILING_DIRECTORIES=str(tmp_path.parent)`, `GIT_CONFIG_GLOBAL=os.devnull` and `GIT_CONFIG_NOSYSTEM=1`, as `clean_env` in `build/test_commit_lints.py` does.
  - `test_check_skips_a_tracked_file_deleted_from_the_work_tree`: commit `skills/alpha/scripts/test_a.py`, delete it, and add `skills/alpha/scripts/tool.py`. `findings(root) == ['build/suites.toml: alpha: skills/alpha/scripts holds no pytest file']`. Mutant: delete the `is_file()` guard.
  - Seven new `test_validate_refuses` cases. `suite = 'x'` gives `'no [[suite]] tables'`. `suite = [1]` gives `'suite 1: not a table'`. `dir = '/abs'` gives `"suite 1 (a): 'dir' must be a normalised path below the repo root"`. `name = 1` gives `"suite 1: 'name' must be a non-empty string"`. `dir = 1` gives `"suite 1 (a): 'dir' must be a non-empty string"`. `extras = [1]` and `pythons = [1]` give `"suite 1 (a): '<key>' must be a list of non-empty strings"`. Mutant: delete each branch.
  - `test_notes_print_once_after_the_first_header_and_before_the_run`: `FakeRuns` prints `run <label>` when called. A registry where `alpha` has `pythons = ['dev', '/usr/bin/python3']` gives the lines `== alpha (<dev>)`, `note: …`, `run alpha (<dev>)`, `== alpha (/usr/bin/python3)`, `run alpha (/usr/bin/python3)`. Mutants: print the notes after `run_one`, or on every run.
  - `test_list_with_extras_shows_the_extras_deps`, `test_list_with_pytest_args_appends_them` and `test_list_with_no_names_lists_every_suite_in_file_order`. Mutant: `list_suites` drops `extras` or `pytest_args`, or `--list` with no names lists nothing.
  - `test_run_subprocess_runs_in_the_suite_dir_with_this_environment`: a `Run` whose argv is `(sys.executable, '-c', <print os.getcwd() and os.environ['LANE3_PROBE'], exit 3>)`, with `LANE3_PROBE=seen`. The return value is `3`, and the output lines are `str((tmp_path / 'sub').resolve())` and `seen`. Mutant: drop `cwd=`.
  - `test_a_malformed_registry_exits_2_for_a_run_and_1_for_check`: `build/suites.toml` reads `name = [`. `main(['alpha'])` returns `2` and `main(['--check'])` returns `1`, both with `build/suites.toml: cannot read` on stderr.
  - In `build/test_commit_lints.py::test_unregistered_suite_is_refused`, one line before the file is planted: assert that no `dir` in the clone's `build/suites.toml` contains `tools/scan`.

- [ ] **Step 2: Apply each named mutant by hand, run the suite, and see the test go red; then revert it**

  Run, per mutant: `cd build && uv run --with pytest python -m pytest -q test_run_suites.py -k <test>`
  Expected: FAIL with the mutant applied, PASS once it is reverted. `git diff build/run_suites.py` is empty at the end.

- [ ] **Step 3: Run both suites**

  Run: `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_run_suites.py test_commit_lints.py`
  Expected: all pass. `test_commit_lints.py` takes about 15 s.

- [ ] **Step 4: Commit**

  ```bash
  git add build/test_run_suites.py build/test_commit_lints.py
  git commit -m "test(build): close the run_suites.py test gaps (plan 55)"
  ```

### Task 4: Fix the drift job's kit suites

Closes the kit item, once Task 5 sees its Done.

**Files:**
- Modify: `.github/workflows/versions-drift.yml`, `build/test_commit_lints.py`

- [ ] **Step 1: Write the failing test** (+1)

  `test_versions_drift_fetches_full_history_and_keeps_tmp_off_slash_tmp`: in `drift_workflow()`, the `actions/checkout@` step has `with['fetch-depth'] == 0`, and the step whose `run` holds `build/versions.py drift` has `env['TMPDIR'] == '${{ runner.temp }}'`.

- [ ] **Step 2: Run it and see it fail**

  Run: `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_commit_lints.py -k fetches_full_history`
  Expected: FAIL, a `KeyError` on `fetch-depth`.

- [ ] **Step 3: Edit the workflow.** Add `fetch-depth: 0` under the checkout's `with`. Add `env: TMPDIR: ${{ runner.temp }}` to the `Report drift` step. Add a comment above each that names its cause: the kits `git archive` old commits, and the kits' path rules expect a temp folder outside `/tmp`, as on macOS.

- [ ] **Step 4: Run the workflow tests**

  Run: `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_commit_lints.py -k workflow`
  Expected: all pass.

- [ ] **Step 5: Commit, push the branch and dispatch the branch's workflow**

  ```bash
  git add .github/workflows/versions-drift.yml build/test_commit_lints.py
  git commit -m "fix(ci): full history and a temp root off /tmp for the drift job's kit suites"
  git push -u origin HEAD
  gh workflow run versions-drift.yml --ref "$(git branch --show-current)"
  ```

  Expected: the run starts. Its result is read in Task 5.

### Task 5: Check the kit item's Done

- [ ] **Step 1: Read the branch run's 3.13 pass.** When the run from Task 4 ends, run `gh run view <id> --log | command grep -a 'suite runs failed'`.
  Expected: the 3.13 line names none of `cc-guide-verifier-recall-kit`, `completion-triage-guard-kit` or `handoff-rerun-kit`. The 3.15 pass may still fail on missing cp315 wheels (section `66-package-versions`). That is another item. If a kit suite still fails, stop and report the log lines. This is the owner gate on kit edits.

- [ ] **Step 2: After the execution PR merges, dispatch once on `main`**

  Run: `gh workflow run versions-drift.yml --ref main`
  Expected: the same 3.13 result. Record the run id in the completion report.
