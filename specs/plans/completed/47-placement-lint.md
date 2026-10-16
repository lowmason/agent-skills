# Placement Lint Implementation Plan

**Status: COMPLETE (2026-10-16)** — executed via executing-plans; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the hole where exception `skill-body-past-compaction` hides a critical section moved past the compaction window. An eighth commit lint, `critical_placement`, will run the placement tests. A new test will tie those tests to the exception's artifacts.

**Architecture:** `apply_waivers` in `build/check_conformance.py` waives per (check, file). So the length waiver for `skills/subagent-driven-development/SKILL.md` and `skills/bayesian-workflow/SKILL.md` also waives their critical-heading findings. The `test_real_skill_*` tests in `build/test_check_conformance.py` pin the placement, but no commit lint runs them. Task 1 adds them to `build/run_commit_lints.sh`, following the `declared_dependencies` precedent (`pytest -k`), and updates every "seven lints" text. Those tests also check span ends and the bold `**A roadmap stage**` paragraph, which the heading check cannot see. A `-k` that selects nothing exits 5, so the lint fails closed if the tests are renamed. Task 2 adds a test that fails when the exception's artifacts and `CRITICAL_SPANS` diverge, or when the exception is gone. The waiver semantics do not change.

**Tech Stack:** Bash (`build/run_commit_lints.sh`, `build/githooks/pre-commit`); Python 3.13 + pytest (`build/test_commit_lints.py`, `build/test_check_conformance.py`); TOML (`build/cc_guide/conformance.toml`); Markdown (`CLAUDE.md`, `build/CLAUDE.md`, `specs/deferred_items.md`).

**Spec:** none. The requirement is the `specs/deferred_items.md` item "Run the placement tests in a commit lint (plan 46 review)", the second `- [ ]` under `## 46-sdd-bundle — 2026-10-15`. Its closure condition: "a test that moves Red Flags past 20,000 characters fails a commit lint or the conformance check with the exception in place".

## Global Constraints

- **Execute in a worktree, never the main checkout.**
- **Run every command from the worktree root.** Use `uv run --directory build …`, not `cd build && …`. A Bash `cd` persists and moves the session's working directory, and guarded worktree sessions refuse compound shell commands.
- **The lint's name is `critical_placement`, and its selection is `-k test_real_skill`, exactly.** Task 2's test name must start with `test_real_skill_` so the same selection picks it up.
- **Leave `.github/workflows/lints.yml` unedited.** It runs `bash build/run_commit_lints.sh`, so it picks up the eighth lint unchanged. The backlog item lists the workflow among the files to touch; reading it shows no edit is needed.
- **Do not change the waiver semantics** (`apply_waivers`, `parse_exceptions`) or exception `skill-body-past-compaction`'s `artifacts`. Fitting the bodies inside the window (the sibling item "Fit the subagent-driven-development and bayesian-workflow bodies inside the compaction window") is out of scope.
- **Assert on exit codes and failure lines, never on a check's name appearing in the output.** `build/run_commit_lints.sh` echoes `== <name>` for every check, so a name-in-output assertion passes vacuously. Use `failed_names()`, which reads only the `commit lints failed:` line.
- **Test counts are deltas** (+N), never absolute pytest totals.
- **`CLAUDE.md` stays under 200 lines** (check `claude-md-size`). Task 1 adds 5 lines to the 187 at `cb9398e`.
- **Do not `cli.py baseline cite`** any edited file. `CLAUDE.md` and `build/cc_guide/conformance.toml` carry drift citations. The STALE lines `cli.py lint` prints are pre-existing and never fail it.
- **Run `bash build/run_commit_lints.sh` before each commit.** From Task 1's runner edit on, it runs eight lints.
- **Commit trailer:** use the executing session's own `Co-Authored-By:` line. Subagent-authored commits keep that same line. Check it with `git log -1 --format=%B`.

## Decisions

- **D1** (owner, plan scoping, 2026-10-16): fix (a). An eighth commit lint, `critical_placement`, runs the `test_real_skill_*` tests. The register does not learn to waive only the length finding, because that would gate heading starts but not span ends or the bold roadmap-stage paragraph. Applied in: Task 1.
- **D2** (owner, plan scoping, 2026-10-16): tie the placement tests to the register. A test fails when exception `skill-body-past-compaction`'s `artifacts` differ from `CRITICAL_SPANS`' keys, or when the exception is gone. Applied in: Task 2.

---

### Task 1: Run the placement tests as the eighth commit lint

**Files:**
- Test: `build/test_commit_lints.py` (`CHECKS` at lines 29-30; a new test after `test_misplaced_drift_citation_is_refused`, before `test_hook_fails_open_without_uv` at line 162; module docstring lines 5-10)
- Modify: `build/run_commit_lints.sh` (header line 2; a new `run` line after line 26)
- Modify: `build/githooks/pre-commit` (line 2)
- Modify: `CLAUDE.md` (the commit-lints paragraph at lines 123-127; the commit-lint test comment at line 132; a new command block after the dependency-drift block at lines 143-145)
- Modify: `build/CLAUDE.md` (line 23)
- Modify: `build/test_check_conformance.py` (the comment above `CRITICAL_SPANS`, lines 1120-1124)
- Modify: `build/cc_guide/conformance.toml` (exception `skill-body-past-compaction`'s `reason`, line 695)

**Interfaces:**
- Consumes: the `clone` fixture, `head(repo)`, `commit(repo, *args)` and `failed_names(result) -> set[str]` in `build/test_commit_lints.py`. The parametrised tests `test_real_skill_has_no_critical_heading_past_the_compaction_window` and `test_real_skill_critical_spans_end_inside_the_compaction_window` in `build/test_check_conformance.py`.
- Produces: the runner check named `critical_placement`. It runs `pytest -q test_check_conformance.py -k test_real_skill` from `build/`. Task 2's test joins that selection by name.

- [x] **Step 1: Write the failing tests**

In `build/test_commit_lints.py`, replace the `CHECKS` set (lines 29-30):

```python
CHECKS = {'check_frontmatter', 'check_provenance', 'check_snippets',
          'check_conformance', 'declared_dependencies', 'sync_runtime_assets', 'cc_guide_lint'}
```

with:

```python
CHECKS = {'check_frontmatter', 'check_provenance', 'check_snippets',
          'check_conformance', 'declared_dependencies', 'sync_runtime_assets', 'cc_guide_lint',
          'critical_placement'}
```

Insert this test after `test_misplaced_drift_citation_is_refused`, before `def test_hook_fails_open_without_uv(clone, tmp_path):`, with two blank lines on each side. Red Flags runs from about 1.6k to 3.7k characters of a body of about 29.6k. The test moves it after the last section, so it starts near 27.5k, past the 20,000-character window.

```python
def test_late_critical_section_is_refused(clone):
    '''The eighth lint runs the placement tests. Exception skill-body-past-compaction
    waives compaction-window per file, heading findings included, so check_conformance
    alone passes a Red Flags section moved past the compaction window.'''
    skill = clone / 'skills' / 'subagent-driven-development' / 'SKILL.md'
    text = skill.read_text()
    start = text.index('\n## Red Flags\n') + 1
    end = text.index('\n## ', start) + 1
    skill.write_text(text[:start] + text[end:] + '\n' + text[start:end])
    before = head(clone)
    result = commit(clone, '-am', 'late red flags')
    assert result.returncode != 0, result.stderr
    assert head(clone) == before
    assert failed_names(result) == {'critical_placement'}, result.stderr
    assert ('FAILED test_check_conformance.py::test_real_skill_has_no_critical_heading_past_the_'
            'compaction_window[skills/subagent-driven-development/SKILL.md]') in result.stderr, result.stderr
```

> Deviation: after the whole-plan review (`431e037`), `test_late_critical_section_is_refused` also asserts the span-end test's `FAILED` line. `-k test_real_skill` exits 0 while any test matches, so renaming `test_real_skill_critical_spans_end_inside_the_compaction_window` alone dropped its gate without a failure (observed: `3 passed`, exit 0).

- [x] **Step 2: Run the tests to verify they fail for the right reasons**

Run: `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_commit_lints.py -k "late_critical or fails_closed_without_uv"`

Expected: `2 failed`, each for the reason below. The planning session observed both reasons with these exact edits at `cb9398e`.
- `test_late_critical_section_is_refused` fails at `assert result.returncode != 0`, showing `assert 0 != 0`, and the captured stderr ends `commit lints passed`. The commit succeeded: that is the hole. If it fails at any other line, stop. The RED is not demonstrating the hole, so find out why before going on.
- `test_runner_fails_closed_without_uv` fails at `assert failed_names(result) == CHECKS`. Its `commit lints failed:` line lists the seven current names, without `critical_placement`.

- [x] **Step 3: Add the lint to the runner**

In `build/run_commit_lints.sh`, replace line 2:

```bash
# The seven commit lints that CLAUDE.md lists under Commands. Fails closed: exit 1
```

with:

```bash
# The eight commit lints that CLAUDE.md lists under Commands. Fails closed: exit 1
```

and replace line 26:

```bash
run cc_guide_lint uv run --python 3.13 python build/cc_guide/cli.py lint
```

with:

```bash
run cc_guide_lint uv run --python 3.13 python build/cc_guide/cli.py lint
run critical_placement bash -c 'cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py -k test_real_skill'
```

- [x] **Step 4: Run the tests to verify they pass**

Run: `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_commit_lints.py -k "late_critical or fails_closed_without_uv or clean_commit"`

Expected: `3 passed`. `test_clean_commit_passes` proves that the eighth lint passes on the unedited repo.

- [x] **Step 5: Run the whole commit-lint suite and note its time**

Run: `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_commit_lints.py`

Expected: every test passes, with +1 passed relative to the suite before this task. Note the seconds on pytest's summary line: Step 6 writes them into two docs. The planning session measured 17.3 s before this task, so expect about 20 s. Round the observed figure to the nearest 5 s, and write that figure wherever Step 6 says `about 20`.

- [x] **Step 6: Update the text that counts or describes the lints**

`build/githooks/pre-commit`, line 2. Replace:

```bash
# Pre-commit: run the seven commit lints (build/run_commit_lints.sh) on the working
```

with:

```bash
# Pre-commit: run the eight commit lints (build/run_commit_lints.sh) on the working
```

`build/CLAUDE.md`, line 23. Replace:

```markdown
`run_commit_lints.sh` runs the seven commit lints that the root `CLAUDE.md`
```

with:

```markdown
`run_commit_lints.sh` runs the eight commit lints that the root `CLAUDE.md`
```

`CLAUDE.md`, lines 123-127. Replace:

```bash
# Commit lints: these three, the dependency-drift test, snippet Tier 1, sync_runtime_assets.py --check and the drift
# lint (cli.py lint, below) make seven. build/run_commit_lints.sh runs all seven; build/githooks/pre-commit runs it on
# each commit once enabled (an owner step: git config core.hooksPath build/githooks writes repo config every worktree
# reads); the hook lints the working tree, untracked drafts included except by the drift lint, which reads tracked
# files only. .github/workflows/lints.yml runs them on PRs and main as an advisory check; the hook is the gate.
```

with:

```bash
# Commit lints: these three, the dependency-drift test, snippet Tier 1, sync_runtime_assets.py --check, the drift
# lint (cli.py lint, below) and the placement tests (below) make eight. build/run_commit_lints.sh runs all eight;
# build/githooks/pre-commit runs it on each commit once enabled (an owner step: git config core.hooksPath build/githooks
# writes repo config every worktree reads); the hook lints the working tree, untracked drafts included except by the
# drift lint, which reads tracked files only. .github/workflows/lints.yml runs them on PRs and main as an advisory
# check; the hook is the gate.
```

`CLAUDE.md`, line 132. The old count was already stale: four tests run the full lint set before this task, and five after it. Replace:

```bash
# Commit-lint runner, hook and workflow tests: three of them run the full lint set in a throwaway clone (about 10 s warm)
```

with (using Step 5's figure for `20`):

```bash
# Commit-lint runner, hook and workflow tests: the clean and refusal tests run the full lint set in clones (about 20 s warm)
```

`CLAUDE.md`, after the dependency-drift block. Replace:

```bash
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies

```

with:

```bash
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies

# Critical-section placement: exception skill-body-past-compaction waives compaction-window per file, heading findings
# included, so these tests pin the critical sections of the two skills in test_check_conformance.py's CRITICAL_SPANS
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py -k test_real_skill

```

`build/test_commit_lints.py`, module docstring. The "two refusal tests" count was already stale, as above. Replace:

```python
under edit), points core.hooksPath at the hook, and commits. Only the clean
commit and the two refusal tests run the full lint set in their clone; the two
no-uv tests and the broken-uv test stop before any lint runs. The mode and
workflow tests read the repository's files without cloning, and the workflow
tests parse .github/workflows/lints.yml statically. With a warm uv cache the
file takes about 10 seconds.
```

with (using Step 5's figure for `20`):

```python
under edit), points core.hooksPath at the hook, and commits. Only the clean
commit and the refusal tests run the full lint set in their clone; the two
no-uv tests and the broken-uv test stop before any lint runs. The mode and
workflow tests read the repository's files without cloning, and the workflow
tests parse .github/workflows/lints.yml statically. With a warm uv cache the
file takes about 20 seconds.
```

`build/test_check_conformance.py`, the comment above `CRITICAL_SPANS`. Replace:

```python
# Each critical span starts at its marker and runs to the next `## ` heading
# (or the paragraph's blank line, for a bold-led paragraph). Plan 46 moved
# these inside the compaction window. The register's exception waives
# compaction-window per file, heading findings included, and no commit lint
# runs this file, so these tests pin the placement when the suite runs.
```

with:

```python
# Each critical span starts at its marker and runs to the next `## ` heading
# (or the paragraph's blank line, for a bold-led paragraph). Plan 46 moved
# these inside the compaction window. The register's exception waives
# compaction-window per file, heading findings included, so the
# critical_placement commit lint (build/run_commit_lints.sh) runs the
# test_real_skill_* tests below to pin the placement.
```

`build/cc_guide/conformance.toml`, exception `skill-body-past-compaction`. Replace:

```toml
reason = 'Both bodies run past the first 5,000 tokens. Plan 46 moved their critical sections inside it, pinned by test_real_skill_* in build/test_check_conformance.py, which no commit lint runs. The waiver is per check and file, so it also covers a heading finding in these two files.'
```

with:

```toml
reason = 'Both bodies run past the first 5,000 tokens. Plan 46 moved their critical sections inside it. The waiver is per check and file, so it also covers a heading finding in these two files; the critical_placement commit lint runs test_real_skill_* in build/test_check_conformance.py to keep those sections inside the window.'
```

> Deviation: the observed suite time was 12.68 s (10.31 s before the task), which rounds to 15 s by Step 5's rule, so `CLAUDE.md` and the `test_commit_lints.py` docstring say "about 15" where the text above shows 20.

- [x] **Step 7: Verify**

Run each and check its result:
- `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py`: every test passes, with the same count as before (the edit is a comment).
- `git grep -n -w seven -- CLAUDE.md build/CLAUDE.md build/githooks/pre-commit build/run_commit_lints.sh`: no output. The command exits 1 when nothing matches.
- `wc -l CLAUDE.md`: 192 (below the 200-line `claude-md-size` limit).
- `bash build/run_commit_lints.sh`: exit 0, last line `commit lints passed`. Under `== critical_placement`, pytest's summary line reads `passed, … deselected`, with no `failed` and no error.

- [x] **Step 8: Commit**

```bash
git add build/test_commit_lints.py build/run_commit_lints.sh build/githooks/pre-commit CLAUDE.md build/CLAUDE.md build/test_check_conformance.py build/cc_guide/conformance.toml
git commit -m "build: run the placement tests as the eighth commit lint" -m "Exception skill-body-past-compaction waives compaction-window per file, so a critical section moved past the window passed every lint. critical_placement runs the test_real_skill_* tests; test_late_critical_section_is_refused moves Red Flags past the window and expects only that lint to fail."
```

Before running it, append one more `-m` argument to that `git commit`: the executing session's own `Co-Authored-By:` line, as Global Constraints says.

---

### Task 2: Tie the placement tests to the exception

**Files:**
- Test: `build/test_check_conformance.py` (a new test after `_window_params()`, before `test_real_skill_has_no_critical_heading_past_the_compaction_window`)
- Modify: `specs/deferred_items.md` (the sibling item "Fit the subagent-driven-development and bayesian-workflow bodies inside the compaction window", first `- [ ]` under `## 46-sdd-bundle — 2026-10-15`)

**Interfaces:**
- Consumes: `CRITICAL_SPANS` (dict, file → list of markers) and `cc.load_register(root) -> dict` in `build/test_check_conformance.py`. Task 1's `critical_placement` lint, which selects tests by the `test_real_skill` substring.
- Produces: `test_real_skill_spans_match_the_compaction_waiver`. Under `-k test_real_skill` it is selected, so the eighth lint runs it.

- [x] **Step 1: Write the test**

Insert after the `_window_params()` function, before `@pytest.mark.parametrize('skill', sorted(CRITICAL_SPANS))`, with two blank lines on each side:

```python
def test_real_skill_spans_match_the_compaction_waiver():
    '''The critical_placement lint guards exactly the files the exception waives:
    adding a file to the waiver without a CRITICAL_SPANS entry fails here.'''
    exceptions = cc.load_register(cc.REPO)['exception']
    waived = next((e['artifacts'] for e in exceptions if e.get('id') == 'skill-body-past-compaction'), None)
    assert waived is not None, ('exception skill-body-past-compaction is gone: retire the '
                                'critical_placement commit lint and the test_real_skill_* tests with it')
    assert sorted(waived) == sorted(CRITICAL_SPANS)
```

> Deviation: after the review (`431e037`), the failure message also covers a renamed exception ("if it was renamed, update this id; if the bodies now fit the window, retire …"), since "retire the lint" would reopen the hole after a rename. The `exception skill-body-past-compaction is gone` text is unchanged.

- [x] **Step 2: Run it on the real files**

Run: `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py -k test_real_skill`

Expected: all pass, with +1 selected relative to Task 1's run of the same command. This test guards a state that is already correct, so it passes at once. Steps 3 and 4 give it a real RED.

- [x] **Step 3: Mutation RED, the spans side**

In `build/test_check_conformance.py`, temporarily delete this line from `CRITICAL_SPANS`:

```python
    'skills/bayesian-workflow/SKILL.md': ['## Critical rules', '## Common gotchas'],
```

Run the Step 2 command. Expected: `test_real_skill_spans_match_the_compaction_waiver` FAILS with a list diff naming `'skills/bayesian-workflow/SKILL.md'`. Restore the line exactly, then rerun Step 2's command and expect all to pass again.

- [x] **Step 4: Mutation RED, the register side**

Confirm `git diff --quiet build/cc_guide/conformance.toml` exits 0, since Task 1 committed it. Then temporarily change `id = 'skill-body-past-compaction'` to `id = 'skill-body-past-compaction-x'` in `build/cc_guide/conformance.toml`, and run Step 2's command. Expected: `test_real_skill_spans_match_the_compaction_waiver` FAILS, and its message includes `exception skill-body-past-compaction is gone`. Restore with `git checkout -- build/cc_guide/conformance.toml`. Then rerun Step 2's command and expect all to pass.

- [x] **Step 5: Record the coupling in the sibling deferred item**

In `specs/deferred_items.md`, in the item that begins `- [ ] Fit the subagent-driven-development and bayesian-workflow bodies inside the`, replace:

```markdown
      is a discipline skill, so its moves are micro-tested under writing-skills. Size: plan.
```

with:

```markdown
      is a discipline skill, so its moves are micro-tested under writing-skills. Removing
      the exception fails `test_real_skill_spans_match_the_compaction_waiver` by design
      (plan 47): in the same change, retire the `critical_placement` commit lint, the
      `test_real_skill_*` tests and `CRITICAL_SPANS` in `build/test_check_conformance.py`,
      and set the lint count back to seven where plan 47 raised it. Size: plan.
```

Leave this plan's own item (the second `- [ ]` in that section) unticked. The Plan Completion Protocol ticks it.

> Deviation: after the review (`431e037`), the retirement list also names `build/test_commit_lints.py`'s `CHECKS` entry and `test_late_critical_section_is_refused`, and the "Critical-section placement" block in `CLAUDE.md`.

- [x] **Step 6: Verify**

- `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py`: every test passes, +1 relative to Task 1's Step 7 run.
- `git diff --quiet build/cc_guide/conformance.toml`: exits 0 (the mutation is restored).
- `bash build/run_commit_lints.sh`: exit 0, last line `commit lints passed`.

- [x] **Step 7: Commit**

```bash
git add build/test_check_conformance.py specs/deferred_items.md
git commit -m "test(conformance): tie the placement tests to the compaction waiver" -m "test_real_skill_spans_match_the_compaction_waiver fails when exception skill-body-past-compaction's artifacts and CRITICAL_SPANS diverge, or when the exception is gone, so the critical_placement lint cannot fall behind the waiver."
```

Before running it, append one more `-m` argument to that `git commit`: the executing session's own `Co-Authored-By:` line, as Global Constraints says.
