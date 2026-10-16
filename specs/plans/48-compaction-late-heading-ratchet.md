# Late-Heading Ratchet Implementation Plan

**Status: COMPLETE (2026-10-16)** — executed via executing-plans; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the hole where exception `writing-skills-late-critical-headings` hides a new critical heading that starts past the compaction window in `skills/writing-skills/SKILL.md`. The existing `critical_placement` commit lint will also run a test that pins the two accepted late headings by text, and the coupling test will cover every `compaction-window` exception.

**Architecture:** `apply_waivers` in `build/check_conformance.py` waives per (check, file), so the writing-skills waiver hides heading findings along with the length finding, and nothing guards it. Plan 47's lint runs `pytest -k test_real_skill`, so every new test in `build/test_check_conformance.py` named `test_real_skill_…` joins it with no runner edit. Task 1 adds an `ACKNOWLEDGED_LATE` table beside `CRITICAL_SPANS`, an equality test against the check's own findings, and a clone-based refusal test. Task 2 generalises the coupling test from one exception id to all `compaction-window` exceptions, and refreshes the register and doc text. The waiver semantics do not change.

**Tech Stack:** Python 3.13 + pytest (`build/test_check_conformance.py`, `build/test_commit_lints.py`); TOML (`build/cc_guide/conformance.toml`); Markdown (`CLAUDE.md`, `specs/deferred_items.md`).

**Spec:** `specs/compaction-late-heading-ratchet.md` (approved 2026-10-16). Requirements R1 to R7 map to the tasks as follows: R1, R2 and R5 to Task 1; R3 holds throughout (the existing tests stay as they are); R4, R6 and R7 to Task 2.

## Global Constraints

- **Execute in a worktree, never the main checkout.**
- **Run every command from the worktree root.** Use `uv run --directory build …`, not `cd build && …`. A Bash `cd` persists and moves the session's working directory, and guarded worktree sessions refuse compound shell commands, runtime-computed `$VAR` paths and pipes.
- **The lint is unchanged:** its name is `critical_placement` and its selection is `-k test_real_skill`. Every new test in `build/test_check_conformance.py` starts with `test_real_skill_`, so the same selection picks it up. The count of commit lints stays eight.
- **Do not edit `skills/writing-skills/SKILL.md`** except for the temporary mutation in Task 1 Step 6, which is restored with `git checkout -- skills/writing-skills/SKILL.md` and checked with `git diff --quiet`. Moving the STOP section inside the window is portability Stage D's work.
- **Do not change** `apply_waivers`, `parse_exceptions`, `check_compaction_window`, the `compaction-window` check's parameters, or any exception's `id`, `check`, `sections`, `artifacts`, `guide`, `evidence` or `tracked_in`. Only the `reason` of exception `writing-skills-late-critical-headings` changes (Task 2).
- **Leave `build/run_commit_lints.sh` and `.github/workflows/lints.yml` unedited.**
- **The `clone` fixture in `build/test_commit_lints.py` clones `HEAD` and copies only the runner and hook from the working tree.** A clone-based test sees `build/test_check_conformance.py` as committed, not as edited. This fixes Task 1's order: commit the ratchet (Step 9) before the end-to-end test can go green (Step 10).
- **Assert on exit codes and failure lines, never on a check's name appearing in the output.** `build/run_commit_lints.sh` echoes `== <name>` for every check, so a name-in-output assertion passes vacuously. Use `failed_names()`, which reads only the `commit lints failed:` line.
- **Every mutation is restored exactly** and checked: `git diff --quiet <file>` exits 0 for a file with no other edits, and `git diff <file>` shows only the intended additions otherwise.
- **Test counts are deltas** (+N), never absolute pytest totals. The absolute figures in this plan are the planning session's observations at `281b453`, for comparing against your own baselines.
- **`CLAUDE.md` stays under 200 lines** (check `claude-md-size`). It has 192 lines at `6fa8959`; Task 2 adds 1.
- **Do not `cli.py baseline cite`** any edited file. `CLAUDE.md` and `build/cc_guide/conformance.toml` carry drift citations. The STALE lines `cli.py lint` prints are pre-existing and never fail it.
- **Run `bash build/run_commit_lints.sh` before each commit.** It runs eight lints, and the pre-commit hook runs it again.
- **Leave the `## 47-placement-lint` item in `specs/deferred_items.md` unticked** (the one this plan implements). The Plan Completion Protocol ticks it.
- **Commit trailer:** use the executing session's own `Co-Authored-By:` line. Subagent-authored commits keep that same line. Check it with `git log -1 --format=%B`.

## Decisions

None.

---

### Task 1: Ratchet the accepted late headings

**Files:**
- Test: `build/test_commit_lints.py` (a new test after `test_late_critical_section_is_refused`, before `test_hook_fails_open_without_uv` at line 185)
- Modify: `build/test_check_conformance.py` (the `ACKNOWLEDGED_LATE` table after the `CRITICAL_SPANS` dict, line 1129; `_late_headings` and the equality test after `test_real_skill_critical_spans_end_inside_the_compaction_window`, before `PERSON_PARAMS` at line 1169)

**Interfaces:**
- Consumes: the `clone` fixture, `head(repo)`, `commit(repo, *args)` and `failed_names(result) -> set[str]` in `build/test_commit_lints.py`. `_window_params()`, `cc.check_compaction_window(root, files, params)` and the already-imported `ast` in `build/test_check_conformance.py`. The check's message form `line N: heading '<text>' starts past the first 5000 tokens, so compaction drops it`.
- Produces: `ACKNOWLEDGED_LATE` (dict, file to a list of heading texts), `_late_headings(skill) -> list[str]` (the sorted late heading texts of a skill), and `test_real_skill_late_headings_match_the_acknowledged_set(skill)`, which the existing `-k test_real_skill` selection picks up by name. Task 2 consumes `ACKNOWLEDGED_LATE`.

- [x] **Step 1: Record the baselines**

Run each and write the counts down; later steps are checked against them.

- `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_commit_lints.py`: the planning session saw `13 passed`.
- `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py`: the planning session saw `362 passed`.
- `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py -k test_real_skill`: the planning session saw `5 passed, 357 deselected`.

- [x] **Step 2: Write the failing end-to-end test**

In `build/test_commit_lints.py`, insert this test after `test_late_critical_section_is_refused` and before `def test_hook_fails_open_without_uv(clone, tmp_path):`, with two blank lines on each side:

```python
def test_late_heading_in_acknowledged_file_is_refused(clone):
    '''The writing-skills waiver is per file, so check_conformance alone passes a new
    critical heading past the compaction window; the placement tests catch it.'''
    skill = clone / 'skills' / 'writing-skills' / 'SKILL.md'
    skill.write_text(skill.read_text() + '\n## Warning\n\nA late critical heading.\n')
    before = head(clone)
    result = commit(clone, '-am', 'late warning')
    assert result.returncode != 0, result.stderr
    assert head(clone) == before
    assert failed_names(result) == {'critical_placement'}, result.stderr
    assert ('FAILED test_check_conformance.py::test_real_skill_late_headings_match_the_acknowledged_set'
            '[skills/writing-skills/SKILL.md]') in result.stderr, result.stderr
```

- [x] **Step 3: Run it to verify it fails for the right reason**

Run: `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_commit_lints.py -k late_heading_in_acknowledged`

Expected: `1 failed, 13 deselected`. The test fails at `assert result.returncode != 0`, showing `assert 0 != 0`, and the captured stderr ends with `5 passed, 357 deselected` under `== critical_placement` and then `commit lints passed`. The commit succeeded: that is the hole. If it fails at any other line, stop. The RED is not demonstrating the hole, so find out why before going on.

- [x] **Step 4: Add the table, the helper and the equality test**

In `build/test_check_conformance.py`, insert this after the `CRITICAL_SPANS` dict and before `def _window_params():`, with one blank line above it and two below:

```python
# Late critical headings the owner accepted past the compaction window, by exact
# text. The register's writing-skills waiver is per file, so it hides a new late
# heading too; the equality test below fails on one, and on a heading that is
# gone. Moving the STOP section inside the window is portability Stage D's work.
ACKNOWLEDGED_LATE = {
    'skills/writing-skills/SKILL.md': ['### Create Red Flags List', '## STOP: Before Moving to Next Skill'],
}
```

Then insert this after `test_real_skill_critical_spans_end_inside_the_compaction_window` and before `PERSON_PARAMS = {`, with two blank lines on each side:

```python
def _late_headings(skill):
    found = cc.check_compaction_window(cc.REPO, [skill], _window_params())
    return sorted(ast.literal_eval(f.message.split('heading ', 1)[1].rsplit(' starts past', 1)[0])
                  for f in found if 'starts past' in f.message)


@pytest.mark.parametrize('skill', sorted(ACKNOWLEDGED_LATE))
def test_real_skill_late_headings_match_the_acknowledged_set(skill):
    late, acknowledged = _late_headings(skill), sorted(ACKNOWLEDGED_LATE[skill])
    assert late == acknowledged, (f'{skill} has late critical headings {late}, but ACKNOWLEDGED_LATE lists '
                                  f'{acknowledged}: a new late heading belongs inside the compaction window; '
                                  'a heading that is gone comes off the list, and the exception goes once none remain')
```

> Deviation: after the whole-plan review (`ad4c5d7`), the equality message ends "and the row and its exception go once the body fits the window". The exception also waives the length finding, so an emptied list does not free it; spec R2's wording ("removing the exception once no row remains") is not followed there.

- [x] **Step 5: Run the placement selection**

Run: `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py -k test_real_skill`

Expected: `6 passed, 357 deselected`: +1 relative to Step 1. The test guards a state that is already correct, so it passes at once. Steps 6 to 8 give it real REDs.

- [x] **Step 6: Mutation RED, a new late heading**

In `skills/writing-skills/SKILL.md`, temporarily append this after the last line (a blank line, then the heading and one body line):

```markdown
## Warning

Late.
```

Run the Step 5 command. Expected: `1 failed, 5 passed, 357 deselected`. `test_real_skill_late_headings_match_the_acknowledged_set[skills/writing-skills/SKILL.md]` fails with `late critical headings ['## STOP: Before Moving to Next Skill', '## Warning', '### Create Red Flags List']`, against the two acknowledged ones. Restore with `git checkout -- skills/writing-skills/SKILL.md`, then run `git diff --quiet skills/writing-skills/SKILL.md` and expect exit 0.

- [x] **Step 7: Mutation RED, a row removed**

In `build/test_check_conformance.py`, temporarily change the `ACKNOWLEDGED_LATE` row to drop its second heading:

```python
    'skills/writing-skills/SKILL.md': ['### Create Red Flags List'],
```

Run the Step 5 command. Expected: `1 failed, 5 passed`. The equality test fails with the late headings `['## STOP: Before Moving to Next Skill', '### Create Red Flags List']` against `['### Create Red Flags List']`. Restore the row exactly as Step 4 wrote it.

- [x] **Step 8: Mutation RED, a row for a heading that is gone**

In the same row, temporarily add a heading the file does not have:

```python
    'skills/writing-skills/SKILL.md': ['### Create Red Flags List', '## STOP: Before Moving to Next Skill', '## Gone'],
```

Run the Step 5 command. Expected: `1 failed, 5 passed`, with `'## Gone'` among the acknowledged headings in the message. This proves the test is an equality, not a subset check. Restore the row exactly as Step 4 wrote it, then run `git diff build/test_check_conformance.py` and confirm it shows only the table, `_late_headings` and the new test.

- [x] **Step 9: Commit the ratchet**

Run `bash build/run_commit_lints.sh`: exit 0, last line `commit lints passed`, and under `== critical_placement` the line `6 passed, 357 deselected`. Then:

```bash
git add build/test_check_conformance.py
git commit -m "test(conformance): ratchet the accepted late headings in writing-skills" -m "The writing-skills waiver is per file, so a new late critical heading passed every lint. ACKNOWLEDGED_LATE pins the two accepted ones by text, and test_real_skill_late_headings_match_the_acknowledged_set fails unless exactly those start past the window."
```

Before running it, append one more `-m` argument to that `git commit`: the executing session's own `Co-Authored-By:` line, as Global Constraints says. This commit comes before the end-to-end test is committed because the `clone` fixture reads `HEAD`.

- [x] **Step 10: Run the end-to-end test and time the suite**

Run: `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_commit_lints.py -k late_heading_in_acknowledged`

Expected: `1 passed, 13 deselected`. The commit is now refused with only `critical_placement` failing, and stderr holds the `FAILED …test_real_skill_late_headings_match_the_acknowledged_set[skills/writing-skills/SKILL.md]` line.

Then run the whole file twice and note the second run's time (the first can be slow on a cold uv cache; the planning session saw 22.79 s then 15.15 s): `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_commit_lints.py`. Expected: `14 passed` both times, +1 relative to Step 1. Round the second run's seconds to the nearest 5. The docs say "about 15": if your figure is 15, edit nothing. Otherwise replace `about 15 s warm` in `CLAUDE.md` (line 134) and `about 15 seconds` in the module docstring of `build/test_commit_lints.py` (line 10) with your figure, and add both files to Step 11's commit.

- [x] **Step 11: Verify and commit the end-to-end test**

Run `bash build/run_commit_lints.sh` (exit 0, `commit lints passed`). Then:

```bash
git add build/test_commit_lints.py
git commit -m "test(commit-lints): refuse a new late heading in writing-skills" -m "test_late_heading_in_acknowledged_file_is_refused appends a Warning section to writing-skills in a clone and expects only critical_placement to fail."
```

Before running it, append the executing session's own `Co-Authored-By:` line as one more `-m` argument.

---

### Task 2: Guard every compaction-window waiver and refresh the text

**Files:**
- Modify: `build/test_check_conformance.py` (`test_real_skill_spans_match_the_compaction_waiver`, lines 1137-1145; the comment above `CRITICAL_SPANS`, lines 1120-1125)
- Modify: `build/cc_guide/conformance.toml` (exception `writing-skills-late-critical-headings`'s `reason`, line 863)
- Modify: `CLAUDE.md` (the placement block, lines 148-149)
- Modify: `specs/deferred_items.md` (the note in the item "Fit the subagent-driven-development and bayesian-workflow bodies inside the compaction window", lines 3580-3587, first `- [ ]` under `## 46-sdd-bundle — 2026-10-15`)

**Interfaces:**
- Consumes: `CRITICAL_SPANS`, `ACKNOWLEDGED_LATE` (Task 1) and `cc.load_register(root) -> dict` in `build/test_check_conformance.py`. Task 1's `-k test_real_skill` selection.
- Produces: `test_real_skill_spans_match_the_compaction_waiver`, keeping its name, now comparing all `compaction-window` exceptions to both tables. No new test names, so the lint's selection count stays at 6.

- [x] **Step 1: Record the baselines**

After Task 1: `-k test_real_skill` selects `6 passed, 357 deselected`; `test_check_conformance.py` runs `363 passed`; `test_commit_lints.py` runs `14 passed`. Task 2 changes none of these counts.

- [x] **Step 2: Replace the coupling test**

In `build/test_check_conformance.py`, replace:

```python
def test_real_skill_spans_match_the_compaction_waiver():
    '''The critical_placement lint guards exactly the files the exception waives:
    adding a file to the waiver without a CRITICAL_SPANS entry fails here.'''
    exceptions = cc.load_register(cc.REPO)['exception']
    waived = next((e['artifacts'] for e in exceptions if e.get('id') == 'skill-body-past-compaction'), None)
    assert waived is not None, ('exception skill-body-past-compaction is gone: if it was renamed, update this id; '
                                'if the bodies now fit the window, retire the critical_placement commit lint '
                                'and the test_real_skill_* tests with it')
    assert sorted(waived) == sorted(CRITICAL_SPANS)
```

with:

```python
def test_real_skill_spans_match_the_compaction_waiver():
    '''The critical_placement lint guards exactly the files the compaction-window
    exceptions waive: a waived file in neither CRITICAL_SPANS nor ACKNOWLEDGED_LATE
    fails here, and so does a row whose exception is gone.'''
    exceptions = cc.load_register(cc.REPO)['exception']
    waived = sorted({a for e in exceptions if e.get('check') == 'compaction-window' for a in e.get('artifacts', [])})
    assert waived, ('no compaction-window exception remains: retire the critical_placement commit lint, '
                    'CRITICAL_SPANS, ACKNOWLEDGED_LATE and the test_real_skill_* tests with it')
    assert not set(CRITICAL_SPANS) & set(ACKNOWLEDGED_LATE), 'a file is in both CRITICAL_SPANS and ACKNOWLEDGED_LATE'
    guarded = sorted([*CRITICAL_SPANS, *ACKNOWLEDGED_LATE])
    assert waived == guarded, (f'compaction-window exceptions waive {waived}, but the placement tests guard {guarded}: '
                               'add each missing file to CRITICAL_SPANS or ACKNOWLEDGED_LATE, and remove a row '
                               'whose exception is gone')
```

> Deviation: after the whole-plan review (`ad4c5d7`), the coupling test's messages name the file and the side that lacks it, as spec R4 requires: `both`, `unguarded` and `orphaned` replace the single `waived == guarded` comparison. The failures it covers are unchanged, and Steps 4 and 5 were re-run against the new messages, plus a deleted-row mutation for `unguarded`.

- [x] **Step 3: Run it on the real files**

Run: `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py -k test_real_skill`

Expected: `6 passed, 357 deselected`. The test guards a state that is already correct, so it passes at once. Steps 4 to 6 give it real REDs.

- [x] **Step 4: Mutation RED, a file nothing waives**

In `build/test_check_conformance.py`, temporarily add a row to `ACKNOWLEDGED_LATE` for a skill that fits the window (an empty list, so the equality test still passes for it):

```python
    'skills/brainstorming/SKILL.md': [],
```

Run the Step 3 command. Expected: `1 failed, 6 passed, 357 deselected`. Only `test_real_skill_spans_match_the_compaction_waiver` fails, and its message lists `skills/brainstorming/SKILL.md` among the files the tests guard but no exception waives. Remove the row exactly.

- [x] **Step 5: Mutation RED, a file in both tables**

Temporarily add this row to `ACKNOWLEDGED_LATE`:

```python
    'skills/bayesian-workflow/SKILL.md': [],
```

Run the Step 3 command. Expected: `1 failed, 6 passed`. The coupling test fails with `a file is in both CRITICAL_SPANS and ACKNOWLEDGED_LATE`. Remove the row exactly.

- [x] **Step 6: Mutation RED, no exception left**

Confirm `git diff --quiet build/cc_guide/conformance.toml` exits 0. Then temporarily replace both occurrences of `check = 'compaction-window'` in `build/cc_guide/conformance.toml` with `check = 'compaction-window-x'` (one replace-all), and run the Step 3 command. Expected: `1 failed, 5 passed, 357 deselected`. The coupling test fails with `no compaction-window exception remains: retire the critical_placement commit lint, …`. Restore with `git checkout -- build/cc_guide/conformance.toml`, confirm `git diff --quiet build/cc_guide/conformance.toml` exits 0, then rerun the Step 3 command and expect `6 passed, 357 deselected`. Run `git diff build/test_check_conformance.py` and confirm it shows only the replaced coupling test.

- [x] **Step 7: Refresh the register and the text**

`build/test_check_conformance.py`, the comment above `CRITICAL_SPANS`. Replace:

```python
# these inside the compaction window. The register's exception waives
# compaction-window per file, heading findings included, so the
# critical_placement commit lint (build/run_commit_lints.sh) runs the
# test_real_skill_* tests below to pin the placement.
```

with:

```python
# these inside the compaction window. The register's exceptions waive
# compaction-window per file, heading findings included, so the
# critical_placement commit lint (build/run_commit_lints.sh) runs the
# test_real_skill_* tests below to pin the placement: these spans, and the
# accepted late headings in ACKNOWLEDGED_LATE.
```

`build/cc_guide/conformance.toml`, exception `writing-skills-late-critical-headings`. Replace:

```toml
reason = 'The body is about 7,177 tokens, and STOP: Before Moving to Next Skill (line 630) starts past the first 5,000. Create Red Flags List (line 544) is also flagged, but it is authoring advice, a false positive of the heading heuristic.'
```

with:

```toml
reason = 'The body is about 7,200 tokens, and two headings start past the first 5,000: STOP: Before Moving to Next Skill, a real critical section the owner accepted there, and Create Red Flags List, which is authoring advice and a false positive of the heading heuristic. The waiver is per check and file, so it also hides a new late heading; the critical_placement commit lint runs test_real_skill_late_headings_match_the_acknowledged_set in build/test_check_conformance.py, which fails unless exactly those two start past the window.'
```

`CLAUDE.md`, lines 148-149. Replace:

```bash
# Critical-section placement: exception skill-body-past-compaction waives compaction-window per file, heading findings
# included, so these tests pin the critical sections of the two skills in test_check_conformance.py's CRITICAL_SPANS
```

with:

```bash
# Critical-section placement: compaction-window exceptions waive per file, heading findings included, so these tests
# pin the critical sections of two skills (CRITICAL_SPANS) and the late headings the owner accepted in writing-skills
# (ACKNOWLEDGED_LATE), both in test_check_conformance.py
```

`specs/deferred_items.md`, the note in the "Fit the subagent-driven-development and bayesian-workflow bodies" item. Replace:

```markdown
      the exception fails `test_real_skill_spans_match_the_compaction_waiver` by design
      (plan 47): in the same change, retire the `critical_placement` commit lint (its
      runner line, its `CHECKS` entry and `test_late_critical_section_is_refused` in
      `build/test_commit_lints.py`, and the "Critical-section placement" block in
      `CLAUDE.md`), the `test_real_skill_*` tests and `CRITICAL_SPANS` in
      `build/test_check_conformance.py`, and set the lint count back to seven where plan 47
      raised it. Size: plan.
```

with:

```markdown
      the exception fails `test_real_skill_spans_match_the_compaction_waiver` by design
      (plan 47): in the same change, remove the two files' rows from `CRITICAL_SPANS` in
      `build/test_check_conformance.py` and `test_late_critical_section_is_refused` from
      `build/test_commit_lints.py`. While `writing-skills-late-critical-headings` stays, so
      does the `critical_placement` commit lint (plan 48). When the last `compaction-window`
      exception goes, retire the lint too: its runner line, its `CHECKS` entry and the other
      refusal test in `build/test_commit_lints.py`, the "Critical-section placement" block
      in `CLAUDE.md`, the `test_real_skill_*` tests and `ACKNOWLEDGED_LATE`, and set the
      lint count back to seven. Size: plan.
```

> Deviation: after the whole-plan review (`ad4c5d7`), the `CRITICAL_SPANS` comment and the `CLAUDE.md` block also say that removing an exception removes its files' rows and that the lint retires with the last `compaction-window` exception, since spec R7 asks all three texts for both; `CLAUDE.md` is therefore 194 lines, not 193. The backlog note names `test_late_heading_in_acknowledged_file_is_refused` where the replacement text says "the other refusal test".

- [x] **Step 8: Verify**

Run each and check its result:
- `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py`: `363 passed`, the same count as after Task 1.
- `wc -l CLAUDE.md`: `193` (below the 200-line `claude-md-size` limit).
- `bash build/run_commit_lints.sh`: exit 0, last line `commit lints passed`, and under `== critical_placement` the line `6 passed, 357 deselected`.

- [x] **Step 9: Commit**

```bash
git add build/test_check_conformance.py build/cc_guide/conformance.toml CLAUDE.md specs/deferred_items.md
git commit -m "test(conformance): guard every compaction-window waiver, not one exception id" -m "The coupling test compared one exception's artifacts to CRITICAL_SPANS. It now compares every compaction-window exception to CRITICAL_SPANS plus ACKNOWLEDGED_LATE, so a third waiver without a guard fails, and a row outlives neither its file nor its exception. The writing-skills exception's reason and the retirement guidance are refreshed."
```

Before running it, append the executing session's own `Co-Authored-By:` line as one more `-m` argument.

- [x] **Step 10: Confirm the clones see the committed coupling test**

The refusal tests clone `HEAD`, so run them against the commit you just made: `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_commit_lints.py` Expected: `14 passed`. If a refusal test now fails, the coupling test or a table disagrees with the register: fix that before the review.
