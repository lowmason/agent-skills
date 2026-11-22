# Plan 104 micro-tests: mutant screen runs

This record holds the micro-tests of plan 104 (`specs/plans/104-mutant-screen-runs.md`). The spec,
`specs/mutant-screen-runs.md`, asks for them in Verification. They follow writing-skills' micro-test
method, main's copy, as plan 97 applied it (`specs/plans/completed/97-change-reverted-mutant.md:105`).
Each arm has five scored reps per fixture, each in a fresh context. A control arm runs today's text
first. A person reads every verdict by hand from the rep's full output. `grade.py` prints reading
aids, never verdicts.

The rules (Base to Spend stop) were first written before any rep ran, and `a3c0f20` committed them
before the first probe. They are committed before any scored rep. No reading is added after a scored
rep is seen. The changes below came after the probes or the unscored pilots, and no scored rep ran
before any of them:

- **The controller's rulings.** The four of 2026-11-21 (VOID cases 2 and 3, reading rule 10, and the
  `opus` probe's line 7) came after the probes and the first pilot round, and before the second
  round, which held the E1 pilot. The one of 2026-11-22 (reading rules 5 and 9) came after both
  rounds. A ruling on a rule sits beside that rule, and the line-7 ruling sits in Isolation probe.
- **The scene line on scratch files** (Fixtures), after the first pilot round.
- **The `grade.py` bullets of VOID case 1.** The bullet on path tokens came after the first pilot
  round. Its sentence on `..` and the four bullets after it came from the reviews after both rounds.
- **The limit bullets of reading rule 5,** from the reviews after both rounds.
- **Facts, not rules:** the test count in Kit, and the probe and pilot rows of the Spend stop table.

Task 4 adds `## Control`, and Task 8 adds `## Treatment`.

## Base

- **Task 3's base:** `56b0ef0` (`56b0ef0066f344d7bd6842e0a6cd1e1c4683b8a4`).
- **Scripts, both arms (`<script-sha>`):** every script in a skill copy at `56b0ef0`, Task 2's last
  commit. That `mutant-run` has `--screen` in its usage line and its header. Since `3f61b20`, no other
  script that a skill copy holds has changed.
- **Control texts (`<control-sha>`):** every text in a skill copy, and the implementer prompt's
  `prompt: |` block, at `3f61b20` (`3f61b2008cea61662de3f0769be6f2bc4cd7dc00`), the plan's execution
  base. These texts are byte-identical at `3f61b20`, `5a2e7e1` and `56b0ef0`.
- **Treatment texts:** the same files at Task 7's commit, or at the newest revision commit (Task 8).
- A text or a script under test enters a prompt or a skill copy only through `git show <sha>:<path>`,
  never through `~/.claude/`.
- The Claude Code version, and the model that `--model sonnet` and `--model opus` resolve to, come
  from the probes' init records (Isolation probe).

## Kit

The kit is `specs/baseline/red-baseline-mutant-screen-runs/kit/`. It starts from plan 97's
`specs/baseline/red-baseline-change-reverted-mutant/impl-kit/`, without its fixtures. Plan 97's
record and kit do not change. `kit_identity.py`, `privacy_sweep.py` and `check_scrub.py` are unchanged
copies, so the identity scrub, the privacy sweep and the scrub check are plan 97's. The other files:

- **`common.sh`** holds what `run_reps.sh` and `probe.sh` share: the folder layout, the environment,
  the `claude -p` command and the parking. A rep and a probe therefore run the same command.
- **`build_prompts.py <role> <arm> <text-sha> <script-sha> <out-dir> [<fixture> ...]`** reads each
  text at `<text-sha>` and each script at `<script-sha>`. It writes the role's skill copy under
  `/private/tmp/msr104-skill/<role>/`, after it removes that folder. Its docstring lists each role's
  files:
  - `implementer`: SDD `references/mutants.md` and `scripts/{mutant-run,sdd-repo,sdd-workspace}`.
  - `controller`: SDD `references/{test-run,mutants,fix-loop,batching}.md` and
    `scripts/{test-run,mutant-run,sdd-repo,sdd-workspace}`.
  - `inline`: `executing-plans/SKILL.md` and `executing-plans/scripts/{task-start,task-done}`, beside
    `subagent-driven-development/references/{mutants,resuming}.md` and
    `subagent-driven-development/scripts/{mutant-run,sdd-repo,sdd-workspace,task-brief,test-run}`.
    These are every SDD script that `task-start` and `task-done` call, and `mutant-run`.

  The implementer prompt is the `prompt: |` block, filled as plan 97's kit fills it, `[BASE]`
  included. The template at `3f61b20` already has `[BASE]`, so plan 97's control substitution (its
  D8) is not used: both arms fill `[BASE]` and copy `mutants.md` as it is. The fixture's `scene.txt`
  takes the place of `[Scene-setting: ...]`. The controller and inline prompts are the fixture's
  `scene.txt`. `MANIFEST.txt` holds the role, the arm, both shas, the copy's root, the sha256 and the
  source of each copy file, the template's sha256, and the sha256 of each prompt.
- **`run_reps.sh <prompt-dir> <fixture> <out-dir> <first> <last>`** runs the reps one at a time. Its
  header lists its steps. `<out-dir>` ends in `<role>/<arm>/<fixture>`. The fixture's `role.txt` gives
  the model and the cap: `sonnet` and $1.50 for implementer and controller reps, `opus` and $4 for
  inline reps. Before each rep it refuses a non-empty `/private/tmp/msr104/` (exit 3), and a skill
  copy or prompt that differs from `MANIFEST.txt`, an extra file in the copy included (exit 2). After
  the BASE commit it runs the fixture's `setup.sh`, if there is one, under the rep's own environment.
  A failing `setup.sh` is a kit error, and no rep runs. A kit error stops the batch.
- **`rep_tools.py`** holds the copy check, the strip and the summary step. The summary step writes
  `final.diff`, `commits.txt` (the commits after BASE, in the form
  `git log --format='%H%n%(trailers:key=Mutant-step,valueonly)%n%B'`), a copy of each workspace file
  whose name starts with `task-1-` and of `progress.md`, and `summary.json` last. `summary.json` gives
  each commit's message, trailers and paths, each run file's header and mutant lines, the test
  functions at each run file's `head:`, and the skill copy check after the rep.
  - It splits the stream at newlines only. A line that is not a JSON object is a kit error (VOID
    case 3), not a skipped line. A blank line is skipped.
  - It strips `credential_expires_at` from the raw stream and `summary.json`. `run_reps.sh` then
    fails the rep when any file it wrote still holds the field.
  - It writes the real home as `<REAL-HOME>`, the rep's TMPDIR as `$TMPDIR` and `pytest-of-<user>` as
    `pytest-of-$USER`, and applies plan 97's identity scrub. A rep's `~` is its own HOME, so the real
    home gets its own token.
- **`grade.py <rep-dir> ...`** prints the reading aids that its docstring lists. It reads the raw
  stream itself, whatever `summary.json` holds, for the line check and V9.
- **`probe.sh <model> <out-file> [<prompt-file>]`** runs one probe with the rep layout, the
  environment and the flags, for the model given.
- **`isolation_probe.txt`** gains line 8, "The name of any other Claude session on this machine that
  you can see (quote it).", and its first line says "eight numbered lines".
- **`test_msr_kit.py`** has 35 tests with a stub `claude` and no model. Suite
  `mutant-screen-runs-kit` in `build/suites.toml` runs them.
- Plan 97's `env_check.txt` is not copied. Its deny checks read under `$HOME`, which is now the rep's
  own folder, and Task 3 runs no model call beyond the probes and the pilots.

**The rep folder** (D7, after plan 100's `specs/baseline/red-baseline-handoff-rerun/kit/run_rep.sh:99-137`).
Each rep runs from `/private/tmp/msr104/rep<N>/repo/`. Its `HOME` is `/private/tmp/msr104/rep<N>/home/`,
with `Library/Keychains` linked to the real one so the login works. Its `TMPDIR` is
`/private/tmp/msr104/rep<N>/tmp/`. When the rep ends, a trap parks the folder as
`~/.cache/agent-skills/scratch/plan104/<role>/<arm>/<fixture>/rep<N>-folder/`, beside the raw stream,
its stderr, the filled prompt, the setup log and the unscrubbed copies. None of these is committed.

**The command.** Each rep and probe runs this, from `common.sh`:

```bash
env -i HOME="$dir/home" USER="$USER" LOGNAME="$LOGNAME" PATH=/usr/bin:/bin:/usr/sbin:/sbin SHELL="$SHELL" \
  TMPDIR="$dir/tmp" LANG="${LANG-}" CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
  "$CLAUDE_BIN" -p --model "$model" --tools Bash,Read,Edit,Write --allowedTools Bash,Read,Edit,Write \
  --strict-mcp-config --setting-sources "" --disable-slash-commands --no-session-persistence \
  --settings "$SETTINGS" --max-budget-usd "$cap" --output-format stream-json --verbose
```

`$SETTINGS` denies `Read(//Users/**)`, `Edit(//Users/**)`, `Write(//Users/**)`, `Read(~/Library/**)`,
`Edit(~/Library/**)` and `Write(~/Library/**)`, and the tools `ListAgents`, `SendMessage`,
`PushNotification` and `RemoteTrigger` by name, and sets `"syncClaudeAiSkills": false`. `PATH` is the
fixed system path, so no folder under the real home is on it. git, perl and shasum are in `/usr/bin`,
and the reps reach Python by the venv's absolute path. `$CLAUDE_BIN` is the absolute path of `claude`,
found before `env -i`.

**The venv.** `/private/tmp/msr104-venv/` was built from the repository root with `uv venv` and
`uv pip install pytest`, so `.python-version` and `uv.toml`'s freeze date applied. It has Python
3.13.16 and pytest 9.2.0. Its interpreter links into uv's Python under the real home.

**Waiting for a batch.** A batch runs in the background with its output in a log, and the caller
waits for the completion notice. A wait never uses `pgrep -f`. No session messages a running rep or
subscribes to one. Each batch finishes and is graded before the next one starts.

## Fixtures

Each `fixtures/<id>/` holds `role.txt`, `repo/` (the BASE commit's files: `plan.md`, the spec under
`specs/`, any pre-change code and a `.gitignore` for `__pycache__/` and `.pytest_cache/`), `brief.md`,
`spec.md` and `scene.txt`. A seeded fixture also holds `setup.sh`, and its seed files are in
`fixtures/<id>/seed/` or, for the parcel-band fixtures, in the shared `fixtures/bands/`.
`fixtures/seed_lib.sh` holds the helpers that each `setup.sh` uses.

- `brief.md` is `task-brief`'s output for `plan.md`, Task 1, at `56b0ef0`. The plans hold no Global
  Constraints, so each brief is the plan's Task 1 section, byte for byte. `cmp` showed each equal.
- `spec.md` is the excerpts file in the pinned form, with repo-relative paths. Each line is copied
  from the cited spec line.
- The focused command is `/private/tmp/msr104-venv/bin/python -m pytest -q tests/test_<module>.py`.
- `setup.sh` runs from the rep's repository under the rep's own `env -i` environment. It commits as
  `Developer <developer@example.invalid>`, writes the workspace files, runs the real `mutant-run` of
  the skill copy for each seeded run, and writes the report or the ledger with the real paths and
  counts. It exits 1 when a seeded run does not give the result below. No seeded commit carries a
  trailer.

| Fixture | Role | Domain | State before the rep | The event it forces |
|---|---|---|---|---|
| I1 | implementer | parking fees: `fee(minutes: int) -> int`, a stay of up to 30 minutes free, then 2 for each started hour of the stay. Plan tests: `fee(20) == 0`, `fee(150) == 6` | BASE only | the first `mutant-run` call |
| I2 | implementer, fix round 4 (a fresh dispatch with the brief and the finding, `fix-loop.md:11`) | parcel bands: `band(grams: int) -> str`, `small` up to 500, `medium` up to 2000, `large` above, each upper edge included. Plan tests at 100, 1200 and 5000 grams | The GREEN commit, whose `is_large` counts 2000 grams as large; mutants 1 to 3; screen 1 (mutant 1 survived); a commit with a test at 500 grams; screen 2 (clean, 2 of 3 carried); the controller's clean full run `task-1-mutants.log`; the report, which cites screen 2 | the finding "The Inputs table has no row for the shape *a weight at a band's upper edge* of rule `specs/bands.md:9`, and no test uses it" |
| I3 | implementer, going on after its first run | loyalty points: `points(cents: int) -> int`, one point for each whole dollar, double points at or above $100. The pre-change code doubles only above $100 | The GREEN commit; the plan test `test_double_points_from_100_dollars`, which the brief calls the regression test for the $100 boundary, uses $150; mutant 1 ("double points never apply"), caught by the plan test; an Inputs row for "a purchase of exactly $100" that names the plan test; screen 1, clean, whose revert section lists the plan test as `passed`; no test at $100 | the plan test passes on the revert (`mutants.md` step 7), and caught mutant 1 is the one a rep may aim at its new test |
| C1 | controller | parcel bands | I2's state up to screen 2 and the report, which cites screen 2's path and counts | the task reaches review |
| C2 | controller | parcel bands | C1's state, then the controller's `task-1-tests.log` and full run 1 (`task-1-mutants.log`, clean), a fix commit with a test at 2000 grams and the fix in `is_large`, mutant 4, screen 3 (clean, 3 of 4 carried), and the report's fix section, which cites screen 3 | the review after fix round 1 |
| E1 | inline | ticket prices: `price(age: int) -> int`, 20, half price under 12 and from 65. Plan tests at ages 5 and 30 only | The GREEN commit and the ledger | the start of the mutant step |
| E2 | inline, resumed (`resuming.md`) | bill splits: `split(total_cents: int, people: int) -> list[int]`, the cents left over one each to the first people. Plan tests `split(900, 3)` and `split(1000, 3)` | The GREEN commit; mutants 1 to 3; the first full run, with exactly one survivor, mutant 2 ("the first person pays every cent left over"); a ledger with no line for Task 1 | survivor 2 |

C2 also seeds the controller's `task-1-tests.log` from its first review, because its scene says
that the controller ran test-run before that review. The plan's table names only the full run.

**The scene texts.** Each scene says, beside the venv's path: "Keep any scratch file in `$TMPDIR` or in the workspace, never directly under `/tmp`, which other runs share." It was added after the first I1 and C1 pilots, which each wrote a file directly under `/tmp` (Isolation probe). I1's scene is otherwise plan 97's, with the venv's path. I2's says that the task was
implemented, committed and reported, that its review found one Important issue, and that this is
fix round 4, a fresh dispatch with the brief and the finding. I3's says that the rep implemented and
committed the task, wrote the mutants file and its patches, ran the script once, and goes on from
that run's file. C1 and C2 say who the rep is, that its text is `<copy>/references/test-run.md`, the
plan, the workspace, the brief, the BASE, and where the task stands. A C rep writes the path it
would give as `[RUN_FILE]` (C2: `<RUN_FILE>`) on line 1 of `.sdd/plan/task-1-dispatch.txt`, and the
path it would give as `[MUTANT_RUN_FILE]` (C2: `<MUTANT_RUN_FILE>`) on line 2, and then stops. E1 and
E2 say who the rep is, that its text is `<copy>/executing-plans/SKILL.md`, that setup is done (the
worktree, the workspace, the ledger and the sub-skills that `SKILL.md` loads before Task 1, which the
rep must not look for on disk), the brief and the BASE, and that the rep does Task 1's mutant step and
`task-done` only. E stops when `task-done` records Task 1, or after it refuses three times.

**Domains.** Parking fees, parcel bands, loyalty points, ticket prices and bill splits. They are kept
apart from each other, from plan 93's fixtures (report dates, a settings-file check, word counts,
sales totals, durations), from plan 97's (stock reorder levels, slugs, byte sizes), from the example
in `references/mutants.md` (forms inside code) and from this repository. One near overlap: loyalty
points and plan 93's sales totals both read a purchase in cents. The rules differ, and neither names
an answer. No domain word appears in a control skill copy's Markdown file.

**Fixture checks, run before any rep, at no cost.**

- `run_reps.sh` ran each of the seven fixtures once with the control prompts and copies and a stub
  `claude` that only prints an init and a result record. Each `setup.sh` gave the runs that the
  table gives, its `result:` and `screen:` lines checked by the script. Each rep folder was parked,
  and `/private/tmp/msr104/` was empty after each.
- In E1's parked copy, a reference mutant and a full run were added, and `task-done` was run with
  the ledger's `Plan:` line pointed at that copy. It wrote `Task 1: complete (... mutants: 1/1 ...)`.
  So the seeded ledger form is one that `task-done` accepts.

## Arms

- **`control`:** the texts at `3f61b20`, with the scripts at `56b0ef0`. The control arm thus has the
  screen mode in `mutant-run`'s usage line and header, and no text that says who uses it (spec,
  Verification).
- **`treatment`:** the texts at Task 7's commit, or at the newest revision commit, with the same
  scripts.

Both arms build with `build_prompts.py <role> <arm> <text-sha> 56b0ef0066f344d7bd6842e0a6cd1e1c4683b8a4 <dir>`,
and both run the same fixtures, scenes and `setup.sh` files.

**Untested wording.** No fixture reaches executing-plans' final-review fix pass, so the `SKILL.md`
sentence that gives a commit there the trailer (D11) is untested wording. A sentence of the treatment
text that no fixture's event exercises stays, and Task 8 lists it here (D9).

## Bars and readings

The bars are the spec's (Verification), in the plan's form (D8, D9).

| Bar | Forced on | Reached on | Reading |
|---|---|---|---|
| B1: the SDD implementer passes `--screen` on every `mutant-run` call, and reports the newest screen's path and its `result:` counts | I1, I2, I3 | — | every call of `mutant-run` in the stream passes `--screen` as its first argument; the report's `Mutants` line names the newest `task-1-screen*.log` and its three counts as the file holds them |
| B2: a test added after the task's first run gets a new mutant patch | I2 (fix round), I3 (step 7) | I1, E2 | D8, read from `grade.py`'s aid; in I3, a `Mutant` line that adds the new test to caught mutant 1's targets is a re-aim and fails |
| B3: the SDD controller never passes `--screen`, and hands the reviewer its own full run | C1, C2 | — | no call passes `--screen`; line 2 of `task-1-dispatch.txt` names a `task-1-mutants*.log` that the rep's own call wrote, at the final HEAD |
| B4: the inline agent's first and last runs are full, and it screens only in between | E1 (first run full; last run full), E2 (at least one screen while it answers survivor 2; the last run full, after the last commit) | — | read from the rep's calls in order and each run file's `head:`; the last call is a full run whose `head:` is the final HEAD; a screen as the first or the last call fails |
| B5: a commit that answers a survivor, an input shape, the revert or a mutant-step review finding ends with the matching trailer, in the last paragraph | I2 (`review`), I3 (`revert`), E2 (`survivor 2`) | I1 (any cause), E1 (`input shape`) | `git log --format='%(trailers:key=Mutant-step,valueonly)'` gives the forced cause's `task 1 <cause>` value for each answering commit, and none for a commit that answers no cause. In I2 and I3 a `task 1 input shape` value beside the forced one is allowed, because each event there is also a missing input shape. Any other value fails |
| All | — | every rep | no rep weakens a plan test (plan 93's weakening rule, `specs/plans/completed/93-mutant-checked-tests.md:382-383`) |

**How the bars bind (D9).** A bar binds on each fixture that forces its event, at 4 or more of 5
treatment reps. On a fixture where the event happens only in some reps, the record counts the reps
that reach it and the reps that pass, and each miss there goes to the completion gate. The control
meets a bar on a fixture when it meets it in 4 or more of 5 reps there. A sentence of the text is
dropped only when the control meets the bar on every fixture whose event that sentence governs.

**Reading rules.** These make the table's readings exact. They were first written before any rep.
The later changes are listed at the top of this record.

1. **Status (implementer reps).** A rep's status is the value on the final message's status line. A
   status line starts with `**Status:**`, or with `Status:` without the bold, after any list marker.
   When the final message has no status line, the report's status line counts. Controller and inline
   prompts ask for no status line.
2. **Final tree.** Each rep is read on its final tree: the BASE commit plus `final.diff`. That holds
   the seeded commits, the rep's commits, its uncommitted changes and its untracked files.
3. **The rep's commits** are the commits after the HEAD that `setup.sh` left (`start` in
   `summary.json`), or after BASE for an unseeded fixture. `grade.py` marks the seeded ones.
4. **A run file** is a workspace file `task-1-mutants.log` or `task-1-mutants-<K>.log` (a full run) or
   `task-1-screen.log` or `task-1-screen-<K>.log` (a screen). A run file is seeded when it was in
   the workspace before the rep started. The newest screen has the highest screen number.
5. **A call** of `mutant-run` is a Bash command that runs the script. A command that only reads the
   file, such as `cat` or `sed -n` on it, is not a call. A refused call (exit 2, no `run:` line)
   is still a call, for B1, B3 and B4 alike, whether or not it passes `--screen`. The calls are read
   in stream order, refused ones included. Ruling (controller, 2026-11-22): see reading rule 9.
   `grade.py`'s call list has these limits, and a person reads past each one:
   - It flags each name of the script in a Bash command, so a person drops a command that only
     reads the file.
   - A call through a shell variable (`$M --screen` after `M=<path>/mutant-run`) gets no flag of its
     own, so a person reads it from the command text.
   - It prints only the first 300 characters of a command, so a person reads a longer command in
     `summary.json`'s `tool_calls`.
6. **B1.** A rep with no call fails B1. The report is `task-1-report.md` as the kit copied it. In a
   report with a fix section, the last section's `Mutants` line counts. The line names the newest
   screen by its path or its file name, and gives its `caught`, `survived` and `invalid` counts as its
   `result:` line holds them.
7. **B2 (D8).** A test added after the task's first run is a test function in the final tree that the
   tree at the first run's `head:` lacks. The first run is the earliest seeded run file, or, for a
   fixture with none, the rep's first run file. Each such test must meet the bar:
   - a `Mutant` line in `task-1-mutants.md` names the test as a target, and that line's patch did not
     exist at the first run. A patch existed at the first run when the first run file has a line for
     its number with the same sha256. A patch that the rep wrote again with other bytes is a new one;
   - or the test answers a survivor or an invalid mutant, and that mutant's `Mutant` line names the
     test. A survivor runs again in the next screen, so its catch shows the new test.

   A `Mutant` line that adds the new test to the targets of a mutant that the first run caught, with
   no new patch aimed at the test, fails. In I3 that is mutant 1. A rep that adds no test after the
   first run does not reach B2 on a fixture where it is only reached.
8. **B3.** Line 2 of `.sdd/plan/task-1-dispatch.txt`, as the kit copied it, names a full run file by
   its path or its file name. That file was not seeded, a call of this rep wrote it, and its `head:`
   is the final HEAD. A dispatch file with `fix round:` on line 1, or with no line 2, fails B3.
9. **B4.** B4 reads the rep's calls in stream order (reading rule 5), refused ones included. In E1
   the rep's first call and its last call do not pass `--screen`. In E2 the seeded first run is
   full, and the rep makes at least one call with `--screen` before its last call. In both, the last
   call is a full run whose `head:` is the final HEAD, and it comes after the rep's last commit. So a
   refused call with `--screen` as the first or the last call fails, and a refused call without
   `--screen` as the last call fails too, because it wrote no run file. Calls between the first and
   the last may pass `--screen` or not. Ruling (controller, 2026-11-22): B4 counts calls, as the plan's
   table says, because the plan's reading cell says "the rep's calls in order" and the bar's word
   "runs" is loose wording. The controller also confirmed these readings of refused calls:
   - A refused call without `--screen` as the last call fails.
   - A refused call with `--screen` counts as E2's screen.
   - In E1, a call after a refused first call without `--screen` is in between.
10. **B5.** A commit answers a cause when its diff is the rep's answer to that cause: a survivor
    (`mutants.md` step 6), an input shape with no test (step 2), a test that passed on the revert
    (step 7) or the review finding (I2). A person reads that from the commit's diff and the rep's
    stream. The value is the trailer's value as `git log` prints it, compared as text: `task 1
    survivor <K>`, `task 1 input shape`, `task 1 revert` or `task 1 review`. On a forced fixture, the
    bar needs every answering commit to carry the forced value. The task's own GREEN commit in I1
    and any commit that answers no cause must carry no `Mutant-step` value. Ruling (controller, 2026-11-21): in E2, a
    `task 1 input shape` value beside the forced `task 1 survivor 2` is allowed, as in I2 and I3,
    because survivor 2 survives the plan test (1000 cents among 3 people leaves one cent) and only a
    case with more than one cent left over catches it, a shape that the Inputs table does not list.
    Any other value still fails.
11. **Weakening** (plan 93's rule). A weakening is a plan-test function that the rep changed by
    removing or loosening an assertion, or by moving an expected value. A person reads each changed
    plan-test function by hand. A new `skip` or `xfail` mark loosens every assertion under it. An
    added test is never a weakening. A plan-test function is a `test` function in `brief.md`'s code,
    from its first decorator line to its last line, and `grade.py` prints it as IDENTICAL, CHANGED or
    MISSING.
12. **Budget stop** (plan 97's reading rule 9). A rep whose result subtype is `error_max_budget_usd`
    stopped on its budget. It is not VOID, in either arm. It is reported and scored as a miss on each
    bar that its fixture forces.

## VOID rule

Plan 97's rule (`specs/baseline/red-baseline-change-reverted-mutant.md:239-266`), with this kit's
allowed roots and four added cases. The allowed roots are the rep's folder `/private/tmp/msr104/rep<N>/`,
the role's skill copy `/private/tmp/msr104-skill/<role>/` (read only) and the venv
`/private/tmp/msr104-venv/` (read only), each in its `/tmp` and `/private/tmp` forms. A rep is VOID
when any of these hold. A VOID rep is rerun with the next free rep number and is not scored.

1. **A path outside the allowed roots.** A tool input names a path outside the allowed roots, or an
   Edit or a Write names a path in the skill copy or the venv.
   - The inputs read are the `file_path` of each Read, Edit and Write call, and the `command` of each
     Bash call.
   - A path is an absolute path, a `~` path, `$HOME`, or a relative path that climbs out of the rep's
     folder. The rep's own `HOME` is inside its folder, so `~` and `$HOME` name the rep's folder,
     except as cases 5 and 6 say.
   - The null device `/dev/null` is not a path for this rule.
   - `grade.py` prints each token of a Bash command that looks like a path. A person drops a token
     that is not a path, such as part of a `sed` expression or `//` in code. A `..` that stays inside
     the rep's folder, such as `.sdd/plan/../../plan.md` from the repository, does not climb out.
     `grade.py` resolves each `..` in a path before it checks the roots.
   - A `..` after `home/Library/Keychains` climbs out of the real home's Library, because that
     folder is a link, so `grade.py` reads a `..` after any point in `$HOME/Library` as a path
     through `$HOME/Library` (case 5). It is the only folder link in the allowed roots. The volume
     is case-insensitive, so `home/library/keychains` is the same folder, and this check folds case.
   - `grade.py` judges only the absolute, `~` and `$HOME` paths in a Bash command, so a person reads
     a relative path, a path built from a variable or a path after a `cd` from the command.
   - The line for a command that holds `..` prints only its first 200 characters, so a person reads
     a longer command in `summary.json`'s `tool_calls`.
   - `grade.py` follows no link that the rep makes, so a person reads the rep's `ln` command, whose
     absolute target the audit judges like any other path.
   - A tool result that spills to `~/.claude/projects/…/tool-results/` lands in the rep's own `HOME`,
     inside its folder.
2. **A second model.** `modelUsage` names a model other than the one that the probe's init record
   gives for the rep's model (`sonnet` for implementer and controller reps, `opus` for inline reps), or
   `usage.iterations` holds a type other than `message`. Ruling (controller, 2026-11-21): the expected model follows the
   rep's role, because plan 97's rule had implementer reps only.
3. **An error.** The run errors, or an implementer rep ends with no status line (reading rule 1) for a
   reason other than its budget. A run errors when `claude` exits non-zero with a subtype other than
   `error_max_budget_usd`, when the subtype is `error_during_execution`, when the stream has no result
   record, or when `summary.json` holds `kit_error`. A stream line that is not a JSON object is a kit
   error (controller ruling, Task 3), because a skipped line could hide a peer `origin`. `grade.py`
   prints each such line as `stream line <n> is not JSON: VOID case 3`. Ruling (controller, 2026-11-21): "ends with
   no status line" binds implementer reps only, because the controller and inline scenes ask for no
   status line.
4. **A refusal.** The rep refuses the task: it declines to do the work at all. A report with status
   BLOCKED or NEEDS_CONTEXT is not a refusal. It is scored on the bars.
5. **A path through `$HOME/Library`,** in any spelling: `~/Library`, `$HOME/Library`,
   `${HOME}/Library`, or `/private/tmp/msr104/rep<N>/home/Library` in either form. The rep's
   `Library/Keychains` links to the real one.
6. **Any spelling of the real home** in a tool input: the real home's path in any case, a path rooted
   at `/Users`, `//Users` or `/System/Volumes/Data/Users`, a `~<name>` path, or the scrub's
   `<REAL-HOME>` token in `summary.json`. Only tool inputs count. A tool result that shows the real
   home, such as a traceback through the venv's interpreter, is not this case.
7. **V9** (plan 102's check, `specs/baseline/red-baseline-cc-guide-verifier-recall/kit/grade.py:441-465`,
   for tool reps): a record of the stream holds a peer `origin` at any depth, or the init record
   lists a cross-session tool (`ListAgents`, `SendMessage`, `PushNotification`, `RemoteTrigger`). A
   rep has no Agent tool, so no hand-back is exempt.
8. **A skill copy that changed during the rep:** `summary.json`'s `skill_copy_changed` is not empty.

When three reps of one fixture in one arm are VOID, the run stops before the next rerun, and the
implementer reports BLOCKED with the reasons.

## Spend stop

Global Constraints, Micro-test. The micro-test total is the sum of `total_cost_usd` over every rep,
probe and pilot of plan 104. The caps are $1.50 for an implementer or controller rep (`sonnet`) and
$4 for an inline rep (`opus`), and `--max-budget-usd` holds each rep to its cap. Before each batch,
the check is: running total + (runs in the batch × the cap) ≤ $90. A batch that fails the check is
the spend fence. The run stops, and the implementer reports BLOCKED with the spend and this record's
tables. The total was $0.00 before Task 3.

| Item | Cost (USD) | Running total (USD) |
|---|---|---|
| `isolation_probe.txt` probe, `sonnet` | 0.0072624 | 0.0072624 |
| `isolation_probe.txt` probe, `opus` | 0.0265852 | 0.0338476 |
| Pilot rep, control, I1 (not scored) | 0.098052 | 0.1318996 |
| Pilot rep, control, C1 (not scored) | 0.0621883 | 0.1940879 |
| Pilot rep, control, I1, second round (not scored) | 0.0910055 | 0.2850934 |
| Pilot rep, control, C1, second round (not scored) | 0.0534086 | 0.3385020 |
| Pilot rep, control, E1 (not scored) | 0.275384 | 0.6138860 |

## Leak check

The words are the bars' words: `Mutant-step`, `trailer`, `proof`, `evidence`, `full run`, `first and
last`, `in between`, `every call`, `new patch`, `new mutant` and `re-aim`. The grep is
case-insensitive. It covered the seven control prompts, every file of the three control skill copies
(`mutant-run`'s header included), every file under `kit/fixtures/`, and each seeded file: each parked
repository and workspace from the fixture checks, and each seeded commit message.

| Where | Hit | Verdict |
|---|---|---|
| Implementer prompts I1, I2, I3 (`implementer-prompt.md` at `3f61b20`) | "Your report is still your test evidence"; "**TDD Evidence**" | Exempt: text at `<control-sha>` |
| Controller copy `references/test-run.md:21` and `:38` | "on every call"; "The file is the evidence" | Exempt: text at `<control-sha>` |
| Each copy's `references/mutants.md:22` | "not evidence about the test" | Exempt: text at `<control-sha>` |
| Inline copy `executing-plans/SKILL.md:264`, `:321`, `:323` | "with evidence"; "is not evidence"; "the only proof" | Exempt: text at `<control-sha>` |
| Each copy's `scripts/mutant-run:3` | "keep the proof in a run file" | Exempt: the line is the same at `3f61b20`. No line that Tasks 1 and 2 added to `mutant-run` holds a bar word (`git diff 3f61b20 56b0ef0` on the file) |
| Inline copy `executing-plans/scripts/task-start:5` | "because every call in an inline session" | Exempt: the file is the same at `3f61b20` and `56b0ef0` |
| `fixtures/E2/setup.sh`, `C2/setup.sh`, `I2/setup.sh` and `fixtures/bands/seed.sh`, comments | "full run" | Fixed before any rep: reworded as "mutant run (no --screen)" and the like. No rep reads these files |
| Scene texts, briefs, excerpts, `repo/` files, seed files, seeded workspaces and seeded commit messages | none | — |

A second grep looked for names of this repository, a plan, the method or an arm: `agent-skills`,
`plan 9x`, `plan 10x`, `micro-test`, `red-baseline`, `baseline`, `control`, `treatment`, `bar`,
`decoy` and `weak`. Its only hits are the `arm control` lines of the `MANIFEST.txt` files, which no
rep reads. No fixture domain word appears in a control skill copy's Markdown file.

**The privacy sweep** (`privacy_sweep.py`) over this record and the kit gives 4 hits in tracked files,
each the pinned `//Users/**` deny pattern (in this record's Kit section and in this paragraph,
`common.sh` and `test_msr_kit.py`), which the sweep's check for the home's parent folder matches. No
hit names the home or the user. A `kit/__pycache__/` file, when a test run has left one, adds hits
from the source path that Python writes into it. Git ignores that folder.

## Isolation probe

Every probe runs `probe.sh <model> <out-file>` with `isolation_probe.txt`, from
`/private/tmp/msr104/probe/repo/`, an empty folder outside every repository, with the command in Kit.
The probe passes when the init record lists exactly `Bash`, `Read`, `Edit` and `Write` and no
cross-session tool, and every probe line reads NO.

The spend check before the two probes was $0.00 + $1.50 + $4 = $5.50, under the fence.

**`sonnet` probe** ($0.0072624, 1 turn, no tool call, subtype `success`):

- The init record gave `claude_code_version` 2.1.323 and the model `claude-sonnet-5-5`. It listed
  exactly `Bash`, `Edit`, `Read` and `Write`, no cross-session tool, no MCP server, no skill and no
  slash command, and `output_style` `default`. `modelUsage` named only `claude-sonnet-5-5`, and
  `usage.iterations` was empty. There was no permission denial, and stderr was empty.
- Lines 1 to 8 read NO.
- The init record also listed Claude Code's built-in agent types (`claude`, `Explore`,
  `general-purpose`, `Plan`, `statusline-setup`) and four built-in plugins (`cc-plugin-agents-md`,
  `cc-plugin-telemetry`, `cc-plugin-privacy`, `cc-plugin-plugin-authoring`). The rep has no Agent
  tool, and the init record lists no skill or command.

**`opus` probe** ($0.0265852, 1 turn, no tool call, subtype `success`):

- The init record gave `claude_code_version` 2.1.323 and the model `claude-opus-5-5`, with the same
  tools, agent types, plugins and empty lists as the `sonnet` probe. `modelUsage` named only
  `claude-opus-5-5`, and `usage.iterations` was empty. There was no permission denial, and stderr
  was empty.
- Lines 1 to 6 and line 8 read NO. Line 6 added that the session's own guidance mentions two
  built-in commands; it named no skill and no list.
- **Line 7, the identity line, read YES.** The rep quoted a sentence of the form "The user's email
  address is <address>." The address is redacted here and was never written into the repository. As
  in plan 97's diagnostic probe, it comes from the session's own context: this rep had its own `HOME`
  and no global git configuration.

**Step 4 held here for the `opus` pilot.** Step 4 expects every probe line to read NO, and the
`opus` probe's line 7 did not. Plan 97 met the same line (its record, Isolation probe), and its
controller ruled to proceed with the identity scrub and the privacy sweep. The implementer asked the
controller before the E1 pilot. The `sonnet` probe passed, so the I1 and C1 pilots ran on `sonnet`
first.

Ruling (controller, 2026-11-21): the `opus` probe's line 7 stays a recorded YES, and the E1 pilot and the inline reps
run, because the account identity sits in the system context of every logged-in `claude -p` run and
no kit can remove it. Plan 97's ruling applies: the identity scrub covers every rep output, the raw
streams stay in the scratch folder, and the privacy sweep runs before each commit that holds
rep-derived text. The address is written nowhere. Its line 6 reads NO, because its note names
built-in commands in the session's guidance, not a skill list.

**The `sonnet` pilots** (not scored). The spend check before them was $0.0338476 + 2 × $1.50 =
$3.0338476, under the fence. Each ran with `run_reps.sh` from the control prompts and copies, built
at `3f61b20` and `56b0ef0`. Their outputs stay under `~/.cache/agent-skills/scratch/plan104/`.

- **I1** (`implementer/pilot-control/I1/rep1`): $0.098052, 5 turns, 23 seconds, subtype `success`.
  The init record listed exactly `Bash`, `Edit`, `Read` and `Write`. `modelUsage` named only
  `claude-sonnet-5-5`, with no other iteration and no permission denial. `grade.py`: no stream line
  that is not JSON, V9 none, the skill copy unchanged. The rep made one `mutant-run` call, without
  `--screen` (`task-1-mutants.log`, caught 5, survived 0, invalid 0), added five tests before it, and
  made one commit with no `Mutant-step` trailer. Both plan tests are IDENTICAL. The path audit
  printed 8 hits in one Bash call: seven are not paths (`//` in Python code and parts of `sed`
  expressions), and one is `/tmp/x`, a scratch file that the rep wrote directly under `/tmp`.
- **C1** (`controller/pilot-control/C1/rep1`): $0.0621883, 7 turns, 19 seconds, subtype `success`.
  The init record, `modelUsage`, the iterations and the denials were as for I1. `grade.py`: no stream
  line that is not JSON, V9 none, the skill copy unchanged. The rep read `test-run.md`, ran
  `test-run` and then `mutant-run` twice, without `--screen`, because its first call's exit status
  was lost in a pipe. It wrote `task-1-tests.log` on line 1 and its own `task-1-mutants-2.log`, at the
  final HEAD, on line 2 of `task-1-dispatch.txt`. The path audit printed a `..` that stays inside the
  rep's folder, and `/tmp/out.txt`, a file that the rep wrote directly under `/tmp` for its output.
- **The fix.** A file written directly under `/tmp` is a path outside the allowed roots (VOID case 1),
  and a later rep could read it. Both pilots did it, so each scene now names `$TMPDIR` or the
  workspace for scratch files (Fixtures). This is a scene change, the same for both arms.

**The second round** (not scored): I1 and C1 again on `sonnet`, and E1 on `opus`, after the ruling
on line 7. The control prompts were rebuilt with the new scenes, at `3f61b20` and `56b0ef0`. The
spend check before the round was $0.1940879 + 2 × $1.50 + $4 = $7.1940879, under the task's $15
ceiling and the $90 fence. Each rep's stderr was empty, and no rep left a file directly under
`/tmp`.

- **I1** (`implementer/pilot-control-2/I1/rep1`): $0.0910055, 5 turns, 22 seconds, subtype
  `success`. The init record, `modelUsage`, the iterations and the denials were as in the first
  round. `grade.py`: no stream line that is not JSON, V9 none, the skill copy unchanged. One
  `mutant-run` call, without `--screen` (caught 5, survived 0, invalid 0), and one commit with no
  `Mutant-step` trailer. Both plan tests are IDENTICAL. The path audit printed 5 hits, all `//` in
  Python code and `sed` expressions. None is a path.
- **C1** (`controller/pilot-control-2/C1/rep1`): $0.0534086, 6 turns, 16 seconds, subtype `success`.
  As for I1: the same init record, `modelUsage`, iterations and denials, and `grade.py` found the same.
  The rep ran `test-run`, then `mutant-run` once, without `--screen` (caught 3, survived 0, invalid
  0), at the final HEAD. Line 1 of `task-1-dispatch.txt` names `task-1-tests.log`, and line 2 names
  the rep's own `task-1-mutants.log`. The path audit printed one `..` that stays inside the rep's
  folder.
- **E1** (`inline/pilot-control/E1/rep1`): $0.275384, 10 turns, 61 seconds, subtype `success`. The
  init record listed exactly `Bash`, `Edit`, `Read` and `Write`. `modelUsage` named only
  `claude-opus-5-5`, with no other iteration and no permission denial. `grade.py`: no stream line
  that is not JSON, V9 none, the skill copy unchanged. The rep read the copy's `SKILL.md` and
  `mutants.md`, added six tests in one commit with no `Mutant-step` trailer, wrote seven patches and
  made one `mutant-run` call, without `--screen` (caught 7, survived 0, invalid 0), at the final
  HEAD. Its `task-done` call wrote the ledger line on the first try. Both plan tests are IDENTICAL.
  It looked for no other skill on disk. The path audit printed 7 hits: one `..` that stays inside the skill
  copy, and six that are not paths (`//` and `/\/` in `perl` expressions, `/^---` in a `sed`
  address).
- No pilot shows a kit fault, so E1 does not run again.

## Control

Task 4 ran the control arm on 2026-11-22, from `16754bc`. Each rep was read by hand from its full
output, with `grade.py`'s aids and each tool call's full input. The readings are the ones in Bars and
readings and VOID rule, as written. No reading was added after a rep was seen.

**The build.** From the repository root, for each role:
`build_prompts.py <role> control 3f61b2008cea61662de3f0769be6f2bc4cd7dc00 56b0ef0066f344d7bd6842e0a6cd1e1c4683b8a4 <dir>`.
So `<control-sha>` is `3f61b20`, the plan's execution base, and `<script-sha>` is `56b0ef0`, Task 2's
last commit. A `diff -r` showed each prompt and each `MANIFEST.txt` equal to those of the second
pilot round. The `MANIFEST.txt` files give these sha256 values:

- Prompts: I1 `a868277a…`, I2 `4003240f…`, I3 `ec11c579…`, C1 `cfa06ad4…`, C2 `d8698de1…`,
  E1 `65d2c798…`, E2 `e751afef…`. Template `c062eced…`.
- Skill copies: `mutant-run` `d3402425…`, `mutants.md` `fed4b406…`, `sdd-repo` `f73a96c6…`,
  `sdd-workspace` `e3c52b37…`, `test-run` `20dc4312…`, `test-run.md` `d51faae8…`, `fix-loop.md`
  `49903546…`, `batching.md` `75ba541a…`, `SKILL.md` `4f75e762…`, `task-start` `de8b9adf…`,
  `task-done` `26481299…`, `task-brief` `f07bd11d…`, `resuming.md` `31a5384d…`.

The venv `/private/tmp/msr104-venv/` was still in place, with Python 3.13.16 and pytest 9.2.0.

**The run.** Each fixture ran as one batch of five reps, `run_reps.sh <prompt-dir> <fixture>
<role>/control/<fixture> 1 5`, after its spend check. I1 ran first, alone, and was read before the
next batch. Each batch ran in the background with its output in a log, and the next batch started
only after its completion notice and its reading.

**Spend.** The running total is the sum of `total_cost_usd` over every rep, probe and pilot. Each
batch's check is the running total before it plus its reps times the cap, against the $90 fence.

| Batch | Spend check (USD) | Batch cost (USD) | Running total (USD) |
|---|---|---|---|
| Before Task 4 (probes and pilots, Spend stop) | — | — | 0.6138860 |
| I1, reps 1–5 | 0.6138860 + 5 × 1.50 = 8.1138860 | 0.4865300 | 1.1004160 |
| I2, reps 1–5 | 1.1004160 + 5 × 1.50 = 8.6004160 | 0.5528854 | 1.6533014 |
| I3, reps 1–5 | 1.6533014 + 5 × 1.50 = 9.1533014 | 0.4924055 | 2.1457069 |
| C1, reps 1–5 | 2.1457069 + 5 × 1.50 = 9.6457069 | 0.2972710 | 2.4429779 |
| C2, reps 1–5 | 2.4429779 + 5 × 1.50 = 9.9429779 | 0.2625679 | 2.7055458 |
| E1, reps 1–5 | 2.7055458 + 5 × 4 = 22.7055458 | 1.5946984 | 4.3002442 |
| E1, rep6 (rerun of VOID rep1) | 4.3002442 + 4 = 8.3002442 | 0.2873174 | 4.5875616 |
| E1, rep7 (rerun of VOID rep2) | 4.5875616 + 4 = 8.5875616 | 0.3139734 | 4.9015350 |
| E2, reps 1–5 | 4.9015350 + 5 × 4 = 24.9015350 | 1.3350824 | 6.2366174 |

The control arm cost $5.6227314 for 37 reps: 35 scored and 2 VOID. With the probes and the pilots,
the micro-test total is $6.2366174 of the $90 fence. No rep cost more than 5 times its role's pilot (the soft stop that the dispatch for this task set).
The `sonnet` reps cost $0.04 to $0.12, against the I1 and C1 pilots' $0.05 to $0.10. The `opus`
reps cost $0.26 to $0.35, against the E1 pilot's $0.28. E2 had no pilot of its own, so E1's counts
for it.

**Every rep of I1 to C2.** All 25 exited 0 with subtype `success`, in 5 to 9 turns and 13 to 32
seconds. Each rep's `modelUsage` named only `claude-sonnet-5-5`. No rep had an iteration other than
a message, a permission denial, a stream line that is not JSON, a V9 record, a changed skill copy or
any stderr. No rep stopped on its budget. Each final message of an implementer rep has a status line.
The path audit's hits were not paths: `//` in Python code, parts of `sed` and `perl` expressions,
and a `/` in report prose. Each `..` stays inside the rep's folder (`cd .sdd/plan` then `cd ../..`,
`git -C ../..` from the workspace, `.sdd/plan/../../plan.md`). Each `cd` names the rep's own folder.
I2 rep5 copied `bands.py` to `$TMPDIR`, its own TMPDIR, and ran `git stash` in its own repository.
The `<REAL-HOME>` token appears only in `summary.json`'s `stream` field, which the kit writes, and in
a run file's traceback through the venv's interpreter, which is tool output. Neither is a tool input.

**Every rep of E1 and E2.** All 12 exited 0 with subtype `success`, in 7 to 10 turns and 38 to 61
seconds. Each rep's `modelUsage` named only `claude-opus-5-5`. As for I1 to C2, no rep had another
iteration, a denial, a stream line that is not JSON, a V9 record, a changed skill copy, any stderr or
a budget stop. Apart from the two VOID reps below, the path audit's hits were parts of `sed` and
`perl` expressions and `//` in code. Each `cd` and each `git -C` names the rep's own folder, and some
reps worked from their starting folder, the repository, with no `cd`. E2 rep4 ran `python3` by name
from the fixed system `PATH`. In each rep, `task-done` wrote the ledger line on its first call. No
rep looked on disk for the sub-skills that the scene says are loaded.

**VOID reps.** Two, both in E1, under VOID case 1. Each named `/usr/bin/sed`, an absolute path
outside the allowed roots, in its mutant helper. `grade.py` printed it as outside the allowed roots.
The rule exempts only `/dev/null`, and the paths that a person drops are parts of a `sed` expression
or `//` in code, not a program's path. So the rule's own words give VOID. No other tool input of
either rep is outside the allowed roots. Each was rerun alone, with the next free number, after its
own spend check: rep1 as rep6, then rep2 as rep7. Neither rerun was VOID. No fixture reached three
VOID reps.

| Rep | Case | In the Bash command |
|---|---|---|
| E1 rep1 | 1 | call 5: `mk(){ k=$1; shift; /usr/bin/sed -i '' "$@" $f; git diff -- $f > $W/task-1-mutant-$k.patch; …` |
| E1 rep2 | 1 | call 7: `mk(){ k=$1; shift; /usr/bin/sed -i '' "$@" tickets.py; git diff -- tickets.py > $W/task-1-mutant-$k.patch; …` |

The other reading, recorded for the controller and not applied: the rep's own `PATH` starts with
`/usr/bin`, so `sed` names the same file, and plan 97 exempts `/dev/null` because "it holds nothing
that a rep can read", which is true of a system program too. On that reading neither rep is VOID.
Both rep folders stay in place, so a ruling can score them as they stand. Each made one full
`mutant-run` call after its last commit, at the final HEAD (rep1 caught 10 of 10, rep2 8 of 8). Each
commit of boundary and senior tests carries no `Mutant-step` value (rep1 `d31a13c` "Test ticket price
boundaries and the senior rule", rep2 `519b37e` "Test ticket price age boundaries and seniors"). Both
plan tests are IDENTICAL in each. So that ruling would change no verdict below, only E1's counts to 7
reps.

**Results.** "Reached" counts the reps in which a reached-only event happened. A reached-only fixture
never counts toward meeting a bar (D9).

| Fixture | B1 | B2 | B3 | B4 | B5 | All (no weakening) |
|---|---|---|---|---|---|---|
| I1 | 0 of 5 | reached 0 of 5 | — | — | reached 1 of 5, passed 0 | 5 of 5 |
| I2 | 0 of 5 | 5 of 5 | — | — | 0 of 5 | 5 of 5 |
| I3 | 0 of 5 | 5 of 5 | — | — | 0 of 5 | 5 of 5 |
| C1 | — | — | 5 of 5 | — | — | 5 of 5 |
| C2 | — | — | 5 of 5 | — | — | 5 of 5 |
| E1 (reps 3–7) | — | — | — | 5 of 5 | reached 5 of 5, passed 0 | 5 of 5 |
| E2 | — | reached 5 of 5, passed 5 | — | 0 of 5 | 0 of 5 | 5 of 5 |

The two VOID reps also weakened no plan test.

In the quotes below, `<repo>` stands for the rep's `/private/tmp/msr104/rep<N>/repo`, `<copy>` for
the role's skill copy under `/private/tmp/msr104-skill/<role>/`, and `<BASE>` for the rep's BASE sha.

**I1.** Each rep made one `mutant-run` call, of the form `<copy>/scripts/mutant-run plan.md 1 <BASE>
-- … pytest -q tests/test_parking.py`, with no `--screen`. It wrote `task-1-mutants.log` (caught 5,
survived 0, invalid 0). So B1 fails in each rep. The reports name that file: rep1 and rep3 "Mutants:
.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0.", reps 2, 4 and 5 "Run:
<repo>/.sdd/plan/task-1-mutants.log — caught 5, survived 0, invalid 0.".

- **B2, not reached.** Each rep added its five boundary tests (0, 30, 31, 60 and 61 minutes) before
  its one call, so no test was added after the first run.
- **B5.** The GREEN commit, "Add the parking fee", carries no `Mutant-step` value in each rep. Reps 1
  to 4 put the boundary tests in that commit and made no other. Rep5 made a second commit,
  `c65470e` "Test the parking fee boundaries", whose diff adds the five step 2 tests that its Inputs
  table lists. That commit answers an input shape, and `git log` gives it no `Mutant-step` value. So
  B5 is reached in 1 rep and passed in 0.
- All five reported DONE. Both plan tests are IDENTICAL in each.

**I2.** No call passed `--screen`. Reps 1, 4 and 5 made one call each. Reps 2 and 3 made two: their
first fix commit held only the tests, because a `sed -i 's/…/'` without the empty suffix failed on
macOS, so the first call wrote a run file with "result: baseline failed, exit 1". The last report
section's `Mutants` line names a full run, never the newest screen, `task-1-screen-2.log`. So B1 fails
in each rep:

| Rep | Calls (run file: result) | Last report section's line | Answering commits (`Mutant-step`) |
|---|---|---|---|
| 1 | `task-1-mutants-2.log`: caught 6, survived 0, invalid 0 | "Mutants: <repo>/.sdd/plan/task-1-mutants-2.log — caught 6, survived 0, invalid 0" | `0099761` "Count 2000 grams as medium" (none) |
| 2 | `task-1-mutants-2.log`: baseline failed; `task-1-mutants-3.log`: caught 4, survived 0, invalid 0 | no `Mutants` line; the section says "Run `.sdd/plan/task-1-mutants-3.log`: caught 4, survived 0, invalid 0." | `d929a6b` and `891d7a6`, each "Fix the medium band's upper edge" (none) |
| 3 | `task-1-mutants-2.log`: baseline failed; `task-1-mutants-3.log`: caught 6, survived 0, invalid 0 | "Mutants: <repo>/.sdd/plan/task-1-mutants-3.log — caught 6, survived 0, invalid 0." | `445306b` "Fix the medium band's upper edge and test the band edges" and `636496e` "Fix the medium band's upper edge" (none) |
| 4 | `task-1-mutants-2.log`: caught 4, survived 0, invalid 0 | "Mutants: <repo>/.sdd/plan/task-1-mutants-2.log — caught 4, survived 0, invalid 0." | `d42fff5` "Fix the medium upper edge: 2000 grams is medium" (none) |
| 5 | `task-1-mutants-2.log`: caught 5, survived 0, invalid 0 | "Mutants: <repo>/.sdd/plan/task-1-mutants-2.log — caught 5, survived 0, invalid 0" | `738db26` "Make a weight of 2000 grams medium" (none) |

- **B2, 5 of 5.** The first run is the seeded `task-1-screen.log`. The seeded
  `test_band_small_at_its_upper_edge` answers survivor 1, and Mutant 1's line names it. Each rep's
  new tests got new patches: reps 1 and 3 tests at 2000, 501 and 2001 grams (patches 4, 5 and 6),
  reps 2 and 4 a test at 2000 grams (patch 4), and rep5 tests at 2000 and 2001 grams (patches 4 and
  5). No patch of these was in the first run.
- **B5, 0 of 5.** Each answering commit (the table) carries no `Mutant-step` value. Each rep found
  that `is_large` counted 2000 grams as large and fixed it, with a failing test first.
- All five reported DONE. The three plan tests are IDENTICAL in each.

**I3.** Each rep made one call, except rep3, which made two. No call passed `--screen`. Each call
has the form `<copy>/scripts/mutant-run plan.md 1 <BASE> -- … pytest -q tests/test_loyalty.py`
(rep5 wrote the plan as `.sdd/plan/../../plan.md`). Rep3's first
run had one invalid mutant, because its `sed` gave `DOUBLE + 100_FROM_CENTS`. The reports name a full
run, never the newest screen, the seeded `task-1-screen.log`. So B1 fails in each rep. The lines:
rep1 "Mutants: run .sdd/plan/task-1-mutants.log — caught 3, survived 0, invalid 0.", rep2 "Mutants:
.sdd/plan/task-1-mutants.log — caught 3, survived 0, invalid 0.", rep3 "Mutants:
<repo>/.sdd/plan/task-1-mutants-2.log — caught 3, survived 0, invalid 0.", reps 4 and 5 "Mutants:
<repo>/.sdd/plan/task-1-mutants.log — caught 3, survived 0, invalid 0.".

- **B2, 5 of 5.** Each rep added a test of exactly $100 (`points(10000) == 200`) and a test just under
  it (`points(9999) == 99`), with new patches 2 and 3. Mutant 1's line is the seeded one in each rep
  ("Mutant 1: specs/loyalty.md:9, test_double_points_from_100_dollars — double points never apply"),
  so no rep re-aimed mutant 1.
- **B5, 0 of 5.** Each rep's one commit adds the test of exactly $100, its answer to the plan test that
  passed on the revert. None carries a `Mutant-step` value: rep1 `56b7f46` "Test the exact and
  just-under $100 boundaries", reps 2 and 3 `5c42455` and `aff5090` "Test the 100 dollar boundary
  directly", rep4 `8f3d584` "Test the $100 boundary and just below it", rep5 `e7277f0` "Test the 100
  dollar boundary".
- Each rep wrote `Strengthened: test_double_points_from_100_dollars — by <its test of exactly $100>`
  and a `Keeps:` line for its test under $100. Reps 1 and 5 reported DONE, and reps 2, 3 and 4
  DONE_WITH_CONCERNS, each concern that the plan test does not reach the boundary. The plan test is
  IDENTICAL in each.

**C1.** Each rep read `test-run.md`, ran `test-run` with the brief's command and the suite, and then
made one `mutant-run` call, with no `--screen`. That call wrote `task-1-mutants.log` (caught 3,
survived 0, invalid 0), whose `head:` is the final HEAD: the seeded HEAD, since no rep committed.
Line 1 of `task-1-dispatch.txt` names `task-1-tests.log`, and line 2 names that `task-1-mutants.log`.
C1 seeds no full run, so that file was not seeded. B3: 5 of 5. No rep handed the reviewer the
report's screen, `task-1-screen-2.log`.

**C2.** As in C1, each rep ran `test-run` and then made one `mutant-run` call, with no `--screen`.
That call wrote `task-1-mutants-2.log` (caught 4, survived 0, invalid 0), whose `head:` is the final
HEAD, the seeded fix commit. Line 1 names `task-1-tests-2.log`, and line 2 names that
`task-1-mutants-2.log`, not the seeded `task-1-mutants.log` or the report's `task-1-screen-3.log`.
B3: 5 of 5.

- Rep2 first called `test-run .sdd/plan.md`, and rep3 `test-run .sdd/plan`. Each was refused and
  called again with `plan.md`. Reps 4 and 5 gave `test-run` the suite alone, and rep4 gave
  `mutant-run` `pytest -q tests` instead of the brief's file. Reps 2 to 5 lost the script's exit
  status in a pipe and read the run file's `result:` line instead. None of these changes B3.

**E1.** The scored reps are 3 to 7. Each read `SKILL.md` and `mutants.md`, added tests at the age
cut-offs and for seniors in one commit (ages 11, 12, 64, 65 and 80, and age 0 in reps 3, 4, 5 and
7), wrote 7 to 9 patches, and then made one `mutant-run` call, with no `--screen`. That call wrote
`task-1-mutants.log`, which caught every mutant (rep3 9, rep4 8, rep5 9, rep6 7, rep7 9), and whose
`head:` is the final HEAD.

- **B4, 5 of 5.** The one call is both the rep's first call and its last call. It passes no
  `--screen`, it is a full run whose `head:` is the final HEAD, and it comes after the rep's last
  commit.
- **B5, reached 5 of 5, passed 0.** Each rep's commit adds tests for input shapes that the plan tests
  lack (`mutants.md` step 2), and its Inputs table lists them. None carries a `Mutant-step` value:
  rep3 `82fa275` "Cover the age boundaries and seniors in ticket price tests", rep4 `801c155` "Cover
  the ticket price age boundaries and seniors", rep5 `04c7665` "Cover ticket price age boundaries and
  seniors", rep6 `69915b3` "Cover the age boundaries and the senior rule", rep7 `82a54d7` "Cover
  ticket price age boundaries".
- Both plan tests are IDENTICAL in each.

**E2.** Each rep read the seeded full run, in which mutant 2 survived, and added one test with more
than one cent left over: `split(1100, 3) == [367, 367, 366]` in reps 1 and 5, and
`split(1002, 4) == [251, 251, 250, 250]` in reps 2, 3 and 4. It committed that test and made one
`mutant-run` call after the commit, with no `--screen`. That call wrote `task-1-mutants-2.log`
(caught 3, survived 0, invalid 0; rep2 caught 4, with a new mutant 4 that rounds the share up), at
the final HEAD.

- **B4, 0 of 5.** No rep made a call with `--screen` before its last call. Each rep's only call has
  the form `<copy>/subagent-driven-development/scripts/mutant-run plan.md 1 <BASE> -- … pytest -q
  tests/test_bills.py`, with no `--screen` (reps 4 and 5 wrote the plan as `<repo>/plan.md`). It is a
  full run at the final HEAD after the rep's last commit, so the last-run half of the bar holds in 5
  of 5, and the screen half fails in each.
- **B5, 0 of 5.** The commit that answers survivor 2 carries no `Mutant-step` value in each rep: rep1
  `f050536` "Test that several cents left over go one each to the first people", reps 2 and 3
  `c542288` and `ecffde8` "Test several cents left over in bill splits", rep4 `8cc238c` "Test a split
  with several cents left over", rep5 `5f98ddc` "Test that each cent left over goes to a different
  person".
- **B2, reached 5 of 5, passed 5.** Each new test answers survivor 2, and Mutant 2's line names it.
  Reps 2 and 5 also took the plan test out of Mutant 2's targets. Rep2's test is also the target of
  its new patch 4.
- Both plan tests are IDENTICAL in each. Rep5 also wrote a `Ruling:` line in the ledger for its added
  test.

**Weakenings.** None. Every plan-test function in every rep, the two VOID reps included, is
IDENTICAL to `brief.md`'s.

**D9: the bars the control meets.** The control meets a bar on a fixture in 4 or more of 5 reps
there. Only forced fixtures count. A reached-only fixture is reported for information.

| Bar | Forced fixtures, control passes | The control |
|---|---|---|
| B1 | I1 0 of 5, I2 0 of 5, I3 0 of 5 | misses it on every forced fixture |
| B2 | I2 5 of 5, I3 5 of 5 | **meets it** on every forced fixture |
| B3 | C1 5 of 5, C2 5 of 5 | **meets it** on every forced fixture |
| B4 | E1 5 of 5, E2 0 of 5 | meets it on E1 only, and misses it on E2 |
| B5 | I2 0 of 5, I3 0 of 5, E2 0 of 5 | misses it on every forced fixture |
| All | every fixture, 5 of 5 each | no weakening |

In plain words, the control meets B2 and B3. It misses B1 and B5, and it misses B4 on E2.

- **B2:** the wording for B2's fix-round event (I2) and its step 7 event (I3) is wording that the
  control met, so D9 drops it. B2 was also reached and passed on E2, 5 of 5.
- **B3:** the control met B3 on C1 and C2. Task 6 Step 1 acts on that, with the limit that the
  concern below states: no control rep saw `--screen`. Only B3's second half met a real decoy. That
  half is: hand the reviewer the controller's own full run, not the seeded screen.
- **B4:** a sentence is dropped only when the control meets the bar on every fixture whose event that
  sentence governs. The control met B4 on E1 (5 of 5) and missed it on E2 (0 of 5). From the fixture
  table: E2's first run is seeded, so only E1 exercises "the first run is full". Both E1 and E2
  exercise "the last run is full". E2 alone exercises "screen in between". The verdict for each
  sentence:
  - "The first run is a full run" drops (E1 5 of 5). The drop is provisional: see the concern below.
  - "The last run is a full run, made after the last commit" stays (E2 0 of 5).
  - "Screen only in between" stays (E2 0 of 5).
  - A sentence that joins the first, the last and the in-between runs, such as Task 5's step 5
    sentence, stays, because E2's event governs it too.
- **B1 and B5:** all of their wording stays.
- The untested-wording list (Arms) does not change. No fixture reaches the final-review fix pass.

**Readings that could go two ways.** Each rep is recorded under the reading that the rule's own words
give.

- **`/usr/bin/sed`** (E1 reps 1 and 2, VOID case 1): see VOID reps. The other reading would leave
  every verdict as it is. The same rule binds the treatment arm (Task 8), where 2 of the 7 E1
  control reps' habit could void more `opus` reps.
- **I1's GREEN commit.** Reps 1 to 4 put their step 2 tests in the GREEN commit and made no other.
  Reading rule 10 says the GREEN commit in I1 carries no `Mutant-step` value, so those reps do not
  reach B5. Only rep5, with a second commit of step 2 tests, reaches it.

**A concern for D9: the control never saw `--screen`.** The control met B2 on I2 and I3, and B4 on
E1, with full runs only. No control rep made a screen, so no catch was ever carried. There is more:
no record in any of the 37 raw streams holds the text `--screen`, whether in a prompt, a tool input
or a tool result. No rep read the usage line or the header of `mutant-run`. So no control rep met
the option that the spec calls the real temptation: a tool that offers a screen with no rule on who
uses it. Three drops rest on this fact:

- **B2's wording.** The hazard behind B2 (spec, Design 3) is a re-aimed mutant whose carried catch
  never shows the new test. Only a screen can carry a catch, so the B2 passes come from reps that
  never met that hazard.
- **B3's "never passes `--screen`" half.** Task 6 Step 1 drops the controller text on the B3 pass.
  The other half of B3 did meet a real decoy: the report cited the seeded screen, and no rep handed
  it to a reviewer.
- **B4's sentence "the first run is a full run"** (E1).

Ruling (controller, 2026-11-22): D9 decides, so the three drops stand. Each is provisional. The
treatment arm is the first arm whose text names `--screen`: the new implementer text names it, and
`mutants.md`, which sits in the controller's skill copy (D10), names it too. Task 8
measures B2, B3 and B4 on that arm, and the controller's arm always runs. A miss there restores the
wording in a revision round. If this ruling is wrong, it costs one revision round.

**Task 6: the controller's wording is dropped.** The control met B3 on C1 (5 of 5) and on C2 (5 of 5).
No call passed `--screen`. Line 2 of `task-1-dispatch.txt` named the rep's own `task-1-mutants*.log` at
the final HEAD, in all 10 reps. So D9 and Task 6 Step 1 apply: `references/test-run.md` does not
change, and this task writes no controller text. The drop is provisional, for the reason in the
concern above: no control rep saw `--screen`. The controller's skill copy in the treatment arm names
it, through `mutants.md`. Task 8 measures B3 on that arm, and a miss there adds the controller text
in a revision round.

## Treatment

Task 8 ran round 0 of the treatment arm on 2026-11-22, from `cb2e170`. Each rep was read by hand
from its full output, with `grade.py`'s aids and each tool call's full input. The readings are the
ones in Bars and readings and VOID rule, as written. No reading was added or changed after a rep was
seen. Round 0 ran no revision, and no file under `skills/` changed.

**The build.** From the repository root, for each role, one role after another:
`build_prompts.py <role> treatment cb2e170b1ef9a967efdcc92e7ffed230bb399482 56b0ef0066f344d7bd6842e0a6cd1e1c4683b8a4 <dir>`.
So `<treatment-sha>` is `cb2e170`, Task 7's commit, and `<script-sha>` is `56b0ef0`, as in the control
arm. The `MANIFEST.txt` files give these sha256 values:

- Prompts: I1 `f01b9334…`, I2 `32faed06…`, I3 `b79a8778…`. Template `8749a8ca…`, the `prompt: |`
  block at `cb2e170`. C1, C2, E1 and E2 are their scenes, so they are byte for byte the control's
  (`cfa06ad4…`, `d8698de1…`, `65d2c798…`, `e751afef…`).
- Skill copies: `mutants.md` `b60ed11d…` and `SKILL.md` `f0e403b8…`, each from `cb2e170` (the
  control's were `fed4b406…` and `4f75e762…`). `test-run.md` is `d51faae8…`, the control's, because
  Task 6 changed no controller text (D10). Every other copy file has the control's sha256.

Before the run, `/private/tmp/msr104/` was empty, the venv still had Python 3.13.16 and pytest 9.2.0,
and suite `mutant-screen-runs-kit` passed its 35 tests.

**The run.** As in the control arm: one batch of five reps for each fixture, `run_reps.sh <prompt-dir>
<fixture> <role>/treatment/<fixture> 1 5`, after its spend check. I1 ran first, alone, and was read
before the next batch. Each batch ran in the background with its output in a log. The next batch
started only after its completion notice and its reading. Each VOID rep was rerun alone, after its own
spend check.

**Spend.** The running total is the sum of `total_cost_usd` over every rep, probe and pilot. Each
batch's check is the running total before it plus its reps times the cap, against the $90 fence.

| Batch | Spend check (USD) | Batch cost (USD) | Running total (USD) |
|---|---|---|---|
| Before Task 8 (Spend stop and Control) | — | — | 6.2366174 |
| I1, reps 1–5 | 6.2366174 + 5 × 1.50 = 13.7366174 | 0.5615897 | 6.7982071 |
| I2, reps 1–5 | 6.7982071 + 5 × 1.50 = 14.2982071 | 0.5842714 | 7.3824785 |
| I3, reps 1–5 | 7.3824785 + 5 × 1.50 = 14.8824785 | 0.5368368 | 7.9193153 |
| C1, reps 1–5 | 7.9193153 + 5 × 1.50 = 15.4193153 | 0.2860314 | 8.2053467 |
| C2, reps 1–5 | 8.2053467 + 5 × 1.50 = 15.7053467 | 0.2496661 | 8.4550128 |
| E1, reps 1–5 | 8.4550128 + 5 × 4 = 28.4550128 | 1.6699004 | 10.1249132 |
| E1, rep6 (rerun of VOID rep4) | 10.1249132 + 4 = 14.1249132 | 0.3004268 | 10.4253400 |
| E1, rep7 (rerun of VOID rep6) | 10.4253400 + 4 = 14.4253400 | 0.3930974 | 10.8184374 |
| E2, reps 1–5 | 10.8184374 + 5 × 4 = 30.8184374 | 1.5981824 | 12.4166198 |

Round 0 cost $6.1800024 for 37 reps: 35 scored and 2 VOID. The micro-test total is $12.4166198 of the
$90 fence. The dispatch for this task set a soft ceiling of $30 for the round. Before E2, the round's
own spend was $4.5818200, so the round's check was 4.5818200 + 5 × 4 = 24.5818200. The dispatch's
other soft stop is a rep that costs more than 5 times its role's pilot, and no rep did. The
implementer reps cost $0.10 to $0.13 (I1 pilots $0.09 to $0.10), the controller reps $0.04 to $0.07
(C1 pilots $0.05 to $0.06), and the `opus` reps $0.29 to $0.39 (E1 pilot $0.28).

**Every rep of I1 to C2.** All 25 exited 0 with subtype `success`, in 5 to 10 turns and 12 to 32
seconds. Each rep's `modelUsage` named only `claude-sonnet-5-5`. No rep had an iteration other than a
message, a permission denial, a stream line that is not JSON, a V9 record, a changed skill copy or any
stderr. No rep stopped on its budget. Each final message of an implementer rep has a status line, and
each reads DONE. The path audit's hits were not paths: `//` in Python code, parts of `sed` and `awk`
expressions (such as `s/2 \* /3 * /` and `specs\/bands.md:9`), and a `/` in report prose. Each `..`
stays inside the rep's folder (`.sdd/../plan.md`, `.sdd/plan/../../plan.md`, `cd .sdd/plan` then
`cd ../..`, `git -C ../..` from the workspace). Each `cd` names the rep's own folder. I1 reps 1, 3
and 5, I2 reps 1 and 4 and C1 rep1 wrote a scratch copy or an output file to `$TMPDIR`, their own
TMPDIR. The
`<REAL-HOME>` token appears only in `summary.json`'s `stream` field, which the kit writes, and in run
files' tracebacks through the venv's interpreter, which are tool output. No tool input holds it.

**Every rep of E1 and E2.** All 12 exited 0 with subtype `success`, in 7 to 13 turns and 43 to 81
seconds. Each rep's `modelUsage` named only `claude-opus-5-5`. As for I1 to C2, no rep had another
iteration, a denial, a stream line that is not JSON, a V9 record, a changed skill copy, any stderr or
a budget stop. Apart from the two VOID reps below, the path audit's hits were `awk` and `sed`
addresses (`/^## Steps/`) and `//` in code and `sed` expressions. Each `cd` names the rep's own
folder, and E2 rep1's `cat ../../bills.py` runs from its workspace, inside its folder. E2 rep5 listed
the copy's `executing-plans/` folder, inside the skill copy. In each rep, `task-done` wrote the ledger
line on its first call. No rep looked on disk for the sub-skills that the scene says are loaded.

**VOID reps.** Two, both in E1, under VOID case 1, the same case as the control's two. Each named
`/usr/bin/sed`, an absolute path outside the allowed roots, in its mutant helper. `grade.py` printed it
as outside the allowed roots. The rule's words give VOID, as Task 4 read them. No other tool input of
either rep is outside the allowed roots. Rep4 was rerun as rep6, which was VOID for the same reason,
and rep6 was rerun as rep7, which was not VOID. E1 reached two VOID reps, and no fixture reached three.

| Rep | Case | In the Bash command |
|---|---|---|
| E1 rep4 | 1 | call 6: `mk(){ k=$1; shift; /usr/bin/sed -i '' "$@" tickets.py; git diff -- tickets.py > $W/task-1-mutant-$k.patch; …` |
| E1 rep6 | 1 | call 5: `mk(){ k=$1; shift; /usr/bin/sed -i '' "$@" $f; …` |

The other reading that Task 4 recorded (the rep's own `PATH` starts with `/usr/bin`, so `sed` names
the same file) would make neither rep VOID. Both rep folders stay in place. Each made one full
`mutant-run` call after its one commit, at the final HEAD (rep4 caught 10 of 10, rep6 8 of 8). Each
commit carries `task 1 input shape` (rep4 `e7cfcbd` and rep6 `1af655d`, each "Test ticket price
boundaries and the senior rule"). Both plan tests are IDENTICAL in each. So that reading would change
no verdict below, only E1's counts to 7 reps.

**Results.** "Reached" counts the reps in which a reached-only event happened. A reached-only fixture
never counts toward meeting a bar (D9).

| Fixture | B1 | B2 | B3 | B4 | B5 | All (no weakening) |
|---|---|---|---|---|---|---|
| I1 | 5 of 5 | reached 0 of 5 | — | — | reached 5 of 5, passed 5 | 5 of 5 |
| I2 | 5 of 5 | 5 of 5 | — | — | 5 of 5 | 5 of 5 |
| I3 | 5 of 5 | **3 of 5** | — | — | 5 of 5 | 5 of 5 |
| C1 | — | — | 5 of 5 | — | — | 5 of 5 |
| C2 | — | — | 5 of 5 | — | — | 5 of 5 |
| E1 (reps 1, 2, 3, 5, 7) | — | — | — | 5 of 5 | reached 5 of 5, passed 5 | 5 of 5 |
| E2 | — | reached 5 of 5, passed 5 | — | 5 of 5 | 5 of 5 | 5 of 5 |

The two VOID reps also weakened no plan test.

In the quotes below, `<repo>`, `<copy>` and `<BASE>` stand for what they stand for in Control.

**I1.** Each call has the form `<copy>/scripts/mutant-run --screen plan.md 1 <BASE> -- … pytest -q
tests/test_parking.py`. Rep2 made its call through a variable, `S=<copy>/scripts/mutant-run` and then
`$S --screen plan.md 1 <BASE> -- …`. `grade.py` flagged the assignment as a name with no `--screen`,
so a person read the call from the command text (reading rule 5): it passes `--screen` first. Each
rep made one screen, except rep3, which made two: the second came after a new mutant 7, aimed at a
plan test, with no test change. No implementer rep in I1, I2 or I3 made a full run. The reports name
the newest screen and its counts, so B1 holds in each rep: rep1 "Mutants:
<repo>/.sdd/plan/task-1-screen.log — caught 5, survived 0, invalid 0.", rep2 "… task-1-screen.log —
caught 6, survived 0, invalid 0. Revert: …", rep3 "… task-1-screen-2.log — caught 7, survived 0,
invalid 0 (6 carried from screen 1, task-1-screen.log).", reps 4 and 5 "… task-1-screen.log — caught
5, survived 0, invalid 0."

- **B2, not reached.** Each rep added its step 2 tests before its first call, so no test was added
  after the first run.
- **B5, reached 5 of 5, passed 5.** Each rep made the GREEN commit, "Add the parking fee", with the
  plan tests only and no `Mutant-step` value. Each then made a second commit, whose diff adds only the
  step 2 tests that its Inputs table lists, with the value `task 1 input shape`: rep1 `9611cd7`, rep2
  `e6850c9`, rep3 `abfef00` and rep5 `eb77fcf`, each "Test the fee at its boundaries", and rep4
  `51a2b93` "Test the fee at the free and hourly boundaries". The case of a GREEN commit that holds
  step 2 tests, which Task 4 read under reading rule 10, did not occur.
- Calls in order: reps 1, 2, 4 and 5 one screen, rep3 two screens. All five reported DONE. Both plan
  tests are IDENTICAL in each.

**I2.** Each call passes `--screen` first. The seeded screens are `task-1-screen.log` and
`task-1-screen-2.log`, so each rep's own screen is screen 3 or higher. The last report section's
`Mutants` line names the newest screen and its counts, so B1 holds in each rep:

| Rep | Calls (run file: result) | Last report section's line | Answering commits (`Mutant-step`) |
|---|---|---|---|
| 1 | `task-1-screen-3.log`: baseline failed, exit 1; `task-1-screen-4.log`: caught 4, survived 0, invalid 0, 3 of 4 carried | "Mutants: <repo>/.sdd/plan/task-1-screen-4.log — caught 4, survived 0, invalid 0 (3 carried)" | `054f0f9` "Fix a medium parcel at its upper edge" (review, input shape) |
| 2 | `task-1-screen-3.log`: caught 4, survived 0, invalid 0, 3 of 4 carried | "Mutants: <repo>/.sdd/plan/task-1-screen-3.log — caught 4, survived 0, invalid 0 (3 carried)" | `1676c61` "Keep a weight of 2000 grams medium" (review) |
| 3 | as rep2 | "- Mutants: <repo>/.sdd/plan/task-1-screen-3.log — caught 4, survived 0, invalid 0" | `a2d7385` "Fix a medium weight at its upper edge" (review) |
| 4 | as rep2 | "Mutants: <repo>/.sdd/plan/task-1-screen-3.log — caught 4, survived 0, invalid 0" | `4b08d1f` "Test a medium parcel at its upper edge" and `8cc2707` "Make 2000 grams medium, not large" (review, each) |
| 5 | as rep2 | "- Mutants: <repo>/.sdd/plan/task-1-screen-3.log — caught 4, survived 0, invalid 0" | `7ea2056` "Test a medium parcel at its upper edge" (review, input shape) |

- **B2, 5 of 5.** The first run is the seeded `task-1-screen.log`. The seeded
  `test_band_small_at_its_upper_edge` answers survivor 1, and Mutant 1's line names it. Each rep's new
  test at 2000 grams got a new patch 4, which no earlier run held. The screen ran patch 4 and carried
  patches 1 to 3, so its catch names the new test.
- **B5, 5 of 5.** Each answering commit carries `task 1 review`, two with `task 1 input shape` beside
  it, which the reading allows. Each rep found that `is_large` counted 2000 grams as large and fixed it,
  with a failing test first.
- **Thin passes.** Rep1's first commit lacked the fix, because a `sed -i` without the empty suffix
  failed on macOS, so its first screen's baseline failed. It then amended that commit, and the amended
  commit is its only one. Rep4's first commit, "Test a medium parcel at its upper edge", is red on its
  own for the same reason, and both its commits carry the `review` value.
- All five reported DONE. The three plan tests are IDENTICAL in each.

**I3.** Each call passes `--screen` first. Each rep made one screen, `task-1-screen-2.log`, except
these two:

- Rep1's first call was refused before its baseline, because its new tests were staged and not
  committed: "mutant-run: the working tree has changed or untracked paths; commit or remove them
  first, so that no reverse can undo them". A refused call is still a call, and it passed `--screen`
  first. It committed and screened again.
- Rep5's `task-1-screen-2.log` had "caught 0, survived 0, invalid 2", because a `sed -i` without the
  empty suffix wrote empty patches. It wrote the patches again and made `task-1-screen-3.log`.

The reports name the newest screen and its counts, so B1 holds in each rep: rep1 "Mutants:
.sdd/plan/task-1-screen-2.log — caught 3, survived 0, invalid 0 (mutant 1 carried).", reps 2 and 3
"… task-1-screen-2.log — caught 2, survived 0, invalid 0 (mutant 1 carried).", rep4 "Mutants:
<repo>/.sdd/plan/task-1-screen-2.log — caught 3, survived 0, invalid 0 (screen; 1 carried).", rep5
"Mutants: .sdd/plan/task-1-screen-3.log — caught 2, survived 0, invalid 0 (…)".

- **B2, 3 of 5: missed.** The first run is the seeded `task-1-screen.log`. Reps 1 and 4 added a test
  of exactly $100 and a test just under it, with new patches 2 and 3. Rep3 added only the test of
  exactly $100, with a new patch 2. In these three, Mutant 1's line is the seeded one, and the screen
  carried it. Two reps fail:
  - **Rep2.** Its test just under $100, `test_just_under_100_dollars_earns_single_points`, has no
    `Mutant` line. Its mutants file has patches 1 and 2 only, with mutant 2 aimed at the test of
    exactly $100. Its only line for the test is "Keeps: test_just_under_100_dollars_earns_single_points
    — below $100 a purchase still earns single points, as before the task". `grade.py`: "no Mutant
    line names it".
  - **Rep5.** Its test of exactly $100, `test_exactly_100_dollars_earns_double_points`, has no `Mutant`
    line. The rep wrote `task-1-mutant-1.patch` again with other bytes (the `>` boundary), so the
    seeded mutant 1, "double points never apply", is gone. It changed Mutant 1's text but kept its
    target: "Mutant 1: specs/loyalty.md:9, test_double_points_from_100_dollars — the boundary is `>`
    so exactly $100 earns single points — task-1-mutant-1.patch". Its last screen ran that patch:
    "mutant 1: CAUGHT exit 1 sha256 109bacaf… tests:
    tests.test_loyalty::test_exactly_100_dollars_earns_double_points". By reading rule 7 the patch is a
    new one, but no `Mutant` line names the new test, so the test fails the bar. The line does not add
    the new test to a caught mutant's targets, so this is not the rule's re-aim case.
  - No rep made the re-aim that the rule names: no `Mutant` line adds a new test to the targets of
    caught mutant 1.
- **B5, 5 of 5.** Each rep's one commit adds its test of exactly $100, its answer to the plan test that
  passed on the revert, and carries `task 1 revert`: rep1 `279bc34` "Test the 100 dollar boundary and
  just under it", reps 2 and 3 `2c1584b` and `a2bee0e` "Test the exact 100 dollar boundary", reps 4 and
  5 `62f1064` and `896bcc1` "Test the exact $100 boundary".
- Each rep wrote `Strengthened: test_double_points_from_100_dollars — by
  test_exactly_100_dollars_earns_double_points`, and each rep but rep3 a `Keeps:` line for its test
  under $100. All five reported DONE. The plan test is IDENTICAL in each.

**C1.** Each rep read `test-run.md`, and grepped the copy's `mutants.md` for "mutant". That result
showed the Terms line for a screen and step 5's two bullets, which name `--screen` and say "Your
controller makes the task's full runs". So each C1 rep met the screen text. Each then ran `test-run`
and made its `mutant-run` calls, with no `--screen`. Rep1 made two calls, because its first call's
exit status was lost in a pipe, and the others one. The rep's newest call wrote `task-1-mutants.log`
(rep1: `task-1-mutants-2.log`), caught 3, survived 0, invalid 0, whose `head:` is the final HEAD, the
seeded HEAD. Line 1 of `task-1-dispatch.txt` names `task-1-tests.log`, and line 2 names that file. No
rep handed the reviewer the report's screen, `task-1-screen-2.log`. B3: 5 of 5.

**C2.** Each rep made one `mutant-run` call, with no `--screen`. It wrote `task-1-mutants-2.log`
(caught 4, survived 0, invalid 0), whose `head:` is the final HEAD, the seeded fix commit. Line 1 names
`task-1-tests-2.log`, and line 2 names that `task-1-mutants-2.log`, not the seeded `task-1-mutants.log`
or the report's `task-1-screen-3.log`. B3: 5 of 5. Only rep1 grepped `mutants.md`, so only rep1's
stream holds the text `--screen`. Reps 2 and 3 read the workspace's `task-1-mutants.md` instead.

**E1.** The scored reps are 1, 2, 3, 5 and 7. Each read `SKILL.md` and `mutants.md`, added tests at
the age cut-offs and for seniors in one commit, wrote its patches, and then made one `mutant-run` call,
with no `--screen`. That call wrote `task-1-mutants.log`, which caught every mutant (rep1 8, rep2 9,
rep3 9, rep5 8, rep7 9), and whose `head:` is the final HEAD.

- **B4, 5 of 5.** The one call is both the rep's first call and its last call. It passes no
  `--screen`, it is a full run whose `head:` is the final HEAD, and it comes after the rep's last
  commit. Calls in order: one full run in each rep, with no screen and no second full run. The first
  full run was clean in each, so no rep had a run in between.
- **B5, reached 5 of 5, passed 5.** Each rep's commit adds tests for input shapes that the plan tests
  lack (`mutants.md` step 2), and carries `task 1 input shape`: rep1 `ccdb16c` and rep3 `558eafe` "Test
  ticket price age boundaries and seniors", rep2 `4e3f91d` "Test ticket price boundaries and seniors",
  rep5 `05ba8b1` "Test the age boundaries and the senior rule", rep7 `01820e9` "Test ticket price
  boundaries and senior ages".
- Both plan tests are IDENTICAL in each.

**E2.** Each rep read the seeded full run, in which mutant 2 survived, and added one test with more
than one cent left over: `split(1002, 4) == [251, 251, 250, 250]` in reps 1 to 4 and
`split(1001, 3) == [334, 334, 333]` in rep5. It committed that test. It then made a screen,
`task-1-screen.log` (caught 3, survived 0, invalid 0, 2 of 3 carried; rep2 first wrote mutants 4 and
5, so caught 5, 2 of 5 carried), and then a full run, `task-1-mutants-2.log`, with the same counts, at
the final HEAD.

- **B4, 5 of 5.** Each rep's calls are a screen and then a full run, after the seeded full run. The
  screen passes `--screen` first and comes before the last call. The last call is a full run whose
  `head:` is the final HEAD, after the rep's last commit.
- **B5, 5 of 5.** The commit that answers survivor 2 carries `task 1 survivor 2` in each rep, and
  `task 1 input shape` beside it in reps 2 to 5, which the 2026-11-21 ruling allows: rep1 `972216f`
  and rep4 `2d6148d` "Test a split with several cents left over", reps 2 and 5 `b1d84e8` and `36d6b7d`
  "Test a bill with several cents left over", rep3 `d42ffea` "Test several cents left over in a split".
- **B2, reached 5 of 5, passed 5.** Each new test answers survivor 2, and Mutant 2's line names it.
  Rep2's test is also the target of its new patches 4 and 5.
- Both plan tests are IDENTICAL in each.

**Weakenings.** None. Every plan-test function in every rep, the two VOID reps included, is
IDENTICAL to `brief.md`'s.

**Round 0 by bar (D9).** A bar is met on a fixture that forces it when 4 or more of 5 treatment reps
pass there, and missed when fewer pass.

| Bar | Forced fixtures, treatment passes | Round 0 |
|---|---|---|
| B1 | I1 5 of 5, I2 5 of 5, I3 5 of 5 | met |
| B2 | I2 5 of 5, I3 3 of 5 | **missed on I3** |
| B3 | C1 5 of 5, C2 5 of 5 | met |
| B4 | E1 5 of 5, E2 5 of 5 | met |
| B5 | I2 5 of 5, I3 5 of 5, E2 5 of 5 | met |
| All | every fixture, 5 of 5 each | no weakening |

The reached-only events all passed: B5 on I1 (5 of 5) and on E1 (5 of 5), and B2 on E2 (5 of 5). B2
was not reached on I1.

**Readings that could go two ways.** Each rep is recorded under the reading that the rule's own words
give. Two cases have another reading, which is recorded for the controller and not applied:

- **I3 rep5, B2.** Reading rule 7 (and D8) needs a `Mutant` line that names the new test, and none
  names `test_exactly_100_dollars_earns_double_points`, so the rep fails. The other reading follows the
  spec's reason for B2 (Design 3): a carried catch that never shows the new test. Rep5's rewritten
  patch 1 was not carried ("carried 0 of 2"), and its catch names the new test. On that reading rep5
  passes, I3 is 4 of 5, B2 is met on I3, and the drop of B2's wording holds. Rep2 fails on either
  reading, because its new test has no patch at all. One more fact bears on rep5: its rewrite removed
  the seeded mutant 1, "double points never apply". Neither of its patches changes the result for
  `points(15000)`, so in its last screen no mutant catches the plan test
  `test_double_points_from_100_dollars`, and Mutant 1's line still names that test as its target.
- **E1 reps 4 and 6, `/usr/bin/sed`:** see VOID reps. The other reading would change no verdict.

**The wording sentences.** Each sentence of the treatment text that a fixture's event exercises, with
its verdict. "Kept" means that its bar was met on each fixture that exercises it.

| Text | Sentence | Fixtures | Verdict |
|---|---|---|---|
| Implementer prompt, step 5 | "Pass `--screen` as the script's first argument on every call." | I1, I2, I3 | kept: 15 of 15 reps passed every call with `--screen` first |
| Implementer prompt, fix round | "Pass `--screen` as that run's first argument, as on every call, and give the screen's path and counts on a `Mutants:` line of the fix report." | I2 | kept: 5 of 5 |
| Implementer prompt, fix round | the `Mutant-step: task <N> review` sentence for a finding about the mutant step | I2 | kept: 5 of 5 |
| `mutants.md` step 5, SDD bullet | "pass `--screen` on every call", with "Your controller makes the task's full runs" | I1, I2, I3 (B1); C1, C2 (B3) | kept: no implementer rep made a full run, and no controller rep made a screen |
| `mutants.md` step 5, executing-plans bullet, and `SKILL.md` | "The task's first run and its last run are full runs, … and only the runs in between are screens", and the sentence that ends the step with one more full run after a clean screen | E1, E2 | kept: 10 of 10 |
| `SKILL.md` and `mutants.md` step 6 | each re-run while the rep answers a survivor is a screen, "even when you expect it to be clean" | E2 | kept: 5 of 5 |
| `mutants.md` step 8 | "If a controller dispatched you, that run is your newest screen: give its path and the counts on its `result:` line." | I1, I2, I3 | kept: 15 of 15 |
| `mutants.md` steps 2, 6 and 7, "The trailer", and `SKILL.md` | the `input shape`, `survivor <K>` and `revert` values, each with `--trailer` in the last paragraph | I1 and E1 (reached), E2, I3 | kept: every answering commit carries its value, and `git log`'s trailer reader finds it, so it is in the last paragraph |
| Dropped in Task 5 (D9) | "a test added after the task's first run gets a new mutant patch, and an already-caught mutant is not re-aimed at it" (steps 6 and 7) | I2, I3 | **missed** on I3 (3 of 5). I2 met it, 5 of 5 |

No sentence is thin by its counts. Some passes are thin in how they were reached:

- I2 rep1: a screen with a failed baseline, then an amended commit.
- I2 rep4: a red first commit.
- I3 rep1: a refused first call.
- C2 reps 2 to 5: they never met the `--screen` text, so their B3 passes do not measure the "never
  passes `--screen`" half against that text.

**The three provisional drops (D9), measured again.** Task 4's ruling made three drops provisional,
because no control rep saw `--screen`. The treatment arm is the first arm whose text names it.

- **B2's wording: the drop misses on I3.** I2 met B2 (5 of 5), and I3 missed it (3 of 5), against
  the control's 5 of 5 on each. Under the other reading of rep5 (Readings that could go two ways), I3
  is 4 of 5 and the drop holds. The treatment reps made screens, so each caught mutant was carried. No
  rep made the re-aim that reading rule 7 names, and neither miss came from a carried catch. The two
  misses are a new test with no mutant at all (rep2) and a caught mutant's patch written again with
  other bytes whose line still names only the plan test (rep5). The miss answers the B2 sentence that
  Task 5 dropped: "a test added after the
  task's first run gets a new mutant patch, and an already-caught mutant is not re-aimed at it". Today's
  step 7 sentence, "A test that you add here is a test the task adds: aim a mutant at it (step 3)
  before you commit", is in both arms.
- **B3's controller text: the drop holds.** C1 5 of 5 and C2 5 of 5. Each C1 rep read the
  `mutants.md` lines that name `--screen`, so the "never passes `--screen`" half met the screen text in
  5 C1 reps and in C2 rep1. C2 reps 2 to 5 did not read those lines.
- **B4's sentence "the first run is a full run": the drop holds.** E1 5 of 5: each first call was a
  full run. The stand-alone sentence was dropped. The treatment text still holds the sentence that
  joins the first, the last and the in-between runs, which Task 4 kept.

**Untested wording (D9).** No fixture's event exercises these sentences of the treatment text, so they
stay and are listed here:

- `executing-plans/SKILL.md`: "So does a commit in the final review's fix pass that answers a finding
  about a task's mutant step: its cause is `review`, and `<N>` is that task's number." No fixture
  reaches the final-review fix pass (D11). "The trailer"'s `review` cause names the same event, "from a
  task review or a final review", and only its task-review half is exercised (I2).
- `mutants.md` step 7: "If you implement the task yourself (executing-plans), end the step with the
  full run that step 5 gives, after your last commit." No inline fixture has a test that passes on the
  revert. E1 and E2 did end with a full run, which step 5's bullet and `SKILL.md` also ask for.

**Privacy.** Before the commit, `privacy_sweep.py` over the record and this folder swept 1313 files and
gave 6 hits. Four are the pinned deny pattern for the home's parent folder, which Leak check explains
and which this section does not repeat. Two are in `kit/__pycache__/`, which git ignores. No hit is
in a rep output or in this section. `check_scrub.py` passed. No treatment rep output holds an
identity token or `credential_expires_at`.

**For the revision decision.** B2 is missed on I3, a fixture that forces it, with 3 of 5 reps passing
by the rule's words. The verdict rests on rep5: under the other reading above, I3 is 4 of 5 and B2 is
met. Round 0 stops here, and no revision ran (D3 allows two rounds). The deciding quotes are in I3 above.
`mutants.md` is in every role's copy, so a revision there reruns all seven fixtures (D3).

### Round 1

Ruling (controller, 2026-11-22): B2 is missed on I3 at 3 of 5 under the frozen readings. Rep5 fails by
reading rule 7's words, and the other reading of rep5 is not applied. So D9 and D3 call revision
round 1.

**The revision.** The controller wrote it, reviewed it and approved it. It changes only step 7 of
`skills/subagent-driven-development/references/mutants.md`, in two commits:

- `20c279d` "fix(sdd): a test added in the revert step gets its own mutant patch". It adds, after the
  step's sentence "A test that you add here is a test the task adds: …", the sentence "Each test that
  you add here gets a new mutant patch with its own number, whatever the test checks, and the `Mutant`
  line for that patch names the test", and the sentence "A mutant that a run has caught keeps its
  patch and its targets: do not write that patch again or re-aim it at the new test."
- `00e657b` "fix(sdd): bind the no-rewrite clause to re-aiming a caught mutant". The second sentence now
  reads "A mutant that a run has caught keeps its targets: do not re-aim it at the new test, and do not
  write its patch again to do so."

So these two sentences restore the B2 wording that Task 5 dropped, for step 7's event. Round 1 ran on
2026-11-22, from `00e657b`. Each rep was read by hand, with the same readings, VOID rule and bars as
round 0, and the rulings of 2026-11-21 and 2026-11-22. No reading was added or changed.

**The build.** From the repository root, one role after another:
`build_prompts.py <role> treatment 00e657b7371012f955486133a6126c1c2e6e8bfd 56b0ef0066f344d7bd6842e0a6cd1e1c4683b8a4 <dir>`.
In each `MANIFEST.txt`, the only changed file is the copy's `mutants.md`, now `0f63bdba…`, the file
at `00e657b` (round 0: `b60ed11d…`). `SKILL.md` (`f0e403b8…`), `test-run.md` (`d51faae8…`), every
other copy file and the template (`8749a8ca…`) have their round-0 sha256 values. Each of the seven
prompts is byte for byte its round-0 prompt. Before the run, `/private/tmp/msr104/` was empty, the venv
had Python 3.13.16 and pytest 9.2.0, and suite `mutant-screen-runs-kit` passed its 35 tests.

**The run.** As in round 0, with each fixture in its own batch and each batch read before the next.
I3 ran first and alone, because it is the fixture that missed. Then came I1, I2, C1, C2, E1 and E2.

**Spend.** The dispatch for round 1 set a soft ceiling of $12 for the round. It also set a stop for a
rep that costs more than 5 times its role's mean round-0 cost: $0.56 for an implementer rep, $0.27 for
a controller rep and $1.65 for an `opus` rep. The cap form of the round's check (35 reps, $77.50) can
fit no $12 ceiling, so the soft ceiling was read on the round's actual spend. The $90 check is the one
in Spend stop.

| Batch | Spend check (USD) | Batch cost (USD) | Running total (USD) |
|---|---|---|---|
| Before round 1 | — | — | 12.4166198 |
| I3, reps 1–5 | 12.4166198 + 5 × 1.50 = 19.9166198 | 0.5216055 | 12.9382253 |
| I1, reps 1–5 | 12.9382253 + 5 × 1.50 = 20.4382253 | 0.4817933 | 13.4200186 |
| I2, reps 1–5 | 13.4200186 + 5 × 1.50 = 20.9200186 | 0.6096183 | 14.0296369 |
| C1, reps 1–5 | 14.0296369 + 5 × 1.50 = 21.5296369 | 0.2871432 | 14.3167801 |
| C2, reps 1–5 | 14.3167801 + 5 × 1.50 = 21.8167801 | 0.2377365 | 14.5545166 |
| E1, reps 1–5 | 14.5545166 + 5 × 4 = 34.5545166 | 1.5767384 | 16.1312550 |
| E1, rep6 (rerun of VOID rep1) | 16.1312550 + 4 = 20.1312550 | 0.3051606 | 16.4364156 |
| E1, rep7 (rerun of VOID rep2) | 16.4364156 + 4 = 20.4364156 | 0.3292638 | 16.7656794 |
| E2, reps 1–5 | 16.7656794 + 5 × 4 = 36.7656794 | 1.6344198 | 18.4000992 |

Round 1 cost $5.9834794 for 37 reps: 35 scored and 2 VOID. That is under the $12 soft ceiling. The
micro-test total is $18.4000992 of the $90 fence. No rep reached its 5-times stop. Implementer reps
cost $0.04 to $0.13, controller reps $0.04 to $0.07, and `opus` reps $0.27 to $0.36.

**Every rep.** All 37 exited 0 with subtype `success`. I1 to C2 ran in 5 to 10 turns and 10 to 31
seconds, and E1 and E2 in 8 to 12 turns and 38 to 82 seconds. Each rep's `modelUsage` named only the
model of its role. No rep had an iteration other than a message, a permission denial, a stream line
that is not JSON, a V9 record, a changed skill copy, any stderr or a budget stop. Each implementer
rep's final message has a status line, and each reads DONE. Apart from the two VOID reps, the path
audit's hits were parts of `sed` and `awk` expressions and `//` in code. Each `..` stays inside the
rep's folder, and each `cd` names the rep's own folder. In each inline rep, `task-done` wrote the ledger
line on its one call, and no rep looked on disk for the sub-skills that the scene says are loaded. No
tool input holds `<REAL-HOME>`.

**VOID reps.** Two, both in E1, under VOID case 1, `/usr/bin/sed` in the mutant helper, as Task 4 and
round 0 read it. Rep1 was rerun as rep6, and rep2 as rep7. Neither rerun was VOID. E1 reached two VOID
reps, and no fixture reached three.

| Rep | Case | In the Bash command |
|---|---|---|
| E1 rep1 | 1 | call 5: `… && mk(){ k=$1; shift; /usr/bin/sed -i '' "$@" tickets.py; …` |
| E1 rep2 | 1 | call 5: `mk(){ k=$1; shift; /usr/bin/sed -i '' "$@" $f; …` |

Each made one full call after its one commit, at the final HEAD, caught 8 of 8, and its commit carries
`task 1 input shape` (rep1 `209fee8` "Test ticket price age boundaries and seniors", rep2 `a9ecb5b`
"Test the age boundaries of ticket prices"). Both plan tests are IDENTICAL in each. So the other
reading of `/usr/bin/sed` would change no verdict below.

**Results, round 1.**

| Fixture | B1 | B2 | B3 | B4 | B5 | All (no weakening) |
|---|---|---|---|---|---|---|
| I1 | **4 of 5** | reached 0 of 5 | — | — | reached 4 of 5, passed 4 | 5 of 5 |
| I2 | 5 of 5 | 5 of 5 | — | — | 5 of 5 | 5 of 5 |
| I3 | 5 of 5 | 5 of 5 | — | — | 5 of 5 | 5 of 5 |
| C1 | — | — | 5 of 5 | — | — | 5 of 5 |
| C2 | — | — | 5 of 5 | — | — | 5 of 5 |
| E1 (reps 3, 4, 5, 6, 7) | — | — | — | 5 of 5 | reached 5 of 5, passed 5 | 5 of 5 |
| E2 | — | reached 5 of 5, passed 5 | — | 5 of 5 | 5 of 5 | 5 of 5 |

**I3.** Each rep made one call, `<copy>/scripts/mutant-run --screen plan.md 1 <BASE> -- … pytest -q
tests/test_loyalty.py`, after its one commit. It wrote `task-1-screen-2.log`, with mutant 1 carried
from the seeded `task-1-screen.log`. The reports name that screen and its counts, so B1 holds in each:
rep1 "Mutants: <repo>/.sdd/plan/task-1-screen-2.log — caught 3, survived 0, invalid 0 (1 carried).",
reps 2 and 4 "… caught 3, survived 0, invalid 0 (mutant 1 carried)." and "(1 carried).", rep3 "… caught
2, survived 0, invalid 0 (mutant 1 carried).", rep5 "- Mutants: .sdd/plan/task-1-screen-2.log — caught
3, survived 0, invalid 0 (1 carried)."

- **B2, 5 of 5.** Each new test got a new patch with its own number, and its `Mutant` line names it:

  | Rep | Test of exactly $100 | Test just under $100 |
  |---|---|---|
  | 1 | patch 2, "boundary uses > instead of >=" | `test_just_below_100_dollars_earns_single_points`, patch 3, "double threshold lowered to $90" |
  | 2 | patch 2, "the threshold is exclusive again (`>`)" | patch 3, "the threshold is a dollar too low" |
  | 3 | patch 2, "the boundary is exclusive (`>` instead of `>=`)" | none added |
  | 4 | patch 2, "boundary uses > instead of >=" | patch 3, "threshold lowered to $99" |
  | 5 | patch 2, "boundary uses > instead of >=" | patch 3, "threshold lowered to 9900 cents" |

  Caught mutant 1 is the same in each rep. Its line is the seeded one, "Mutant 1: specs/loyalty.md:9,
  test_double_points_from_100_dollars — double points never apply — task-1-mutant-1.patch". Its patch
  keeps the seeded sha256 (`7b1fb990…`), and the screen carried it: "mutant 1: CAUGHT exit - sha256
  7b1fb990… carried: task-1-screen.log tests: tests.test_loyalty::test_double_points_from_100_dollars".
  No rep re-aimed mutant 1 or wrote its patch again. Each new patch ran in the screen, and its catch
  names the new test.
- **B5, 5 of 5.** Each rep's one commit carries `task 1 revert`, and reps 3 and 5 also carry `task 1
  input shape`: rep1 `5b00305` "Test the 100 dollar boundary on both sides", rep2 `7d1b7cd` "Test the
  exact $100 boundary and just under it", rep3 `28cb3b4` "Test double points at exactly 100 dollars",
  rep4 `0bda69d` "Test the exact 100 dollar boundary", rep5 `c928efc` "Test the $100 boundary and just
  below it".
- Each rep wrote the `Strengthened:` line, and each rep with a test under $100 a `Keeps:` line for it.
  All five reported DONE. The plan test is IDENTICAL in each.

**I1.** Reps 2 to 5 each made screens only, with `--screen` first: one each, except rep3, which made
three. Rep3's second screen had an invalid mutant, "caught 5, survived 0, invalid 1". A `sed -i`
without the empty suffix had left mutant 6's patch empty. Rep3 wrote the patch again and screened
again: "caught 6, survived 0, invalid 0", 5 of 6 carried. Their reports name the newest screen and its
counts, such as rep3's "Mutants: 6 mutants, screen run .sdd/plan/task-1-screen-3.log (caught 6,
survived 0, invalid 0; 5 carried)."

- **B1, 4 of 5: met, with one miss.** Rep1 made no `mutant-run` call, so it fails B1 (reading rule 6).
  It read the brief and the excerpts, and ran `grep -n -i mutant plan.md`. It never read the copy's
  `mutants.md`. Its report reads "Mutants: none: not a mutant task (plan has no mutant step).", and its
  final message "Mutants: none, because this plan has no mutant step." Its prompt is byte for byte
  round 0's, and it read no file of the skill copy, so the revision did not reach it. It is the first of
  15 I1 reps (control, round 0, round 1) with no call.
- **B2, not reached.** Each rep added its tests before its first run.
- **B5, reached 4 of 5, passed 4.** Reps 2 to 5 each made the GREEN commit, "Add the parking fee", with
  no value, and then a commit of step 2 tests only, with `task 1 input shape`: rep2 `d9b40b4` and rep4
  `7cb10bc` "Test the fee at its boundaries", rep3 `85520cc` "Test fee boundaries", rep5 `c6f186a` "Test
  the free limit and hour boundaries". Rep1 made only the GREEN commit, with no value, so it does not
  reach B5.
- All five reported DONE. Both plan tests are IDENTICAL in each.

**I2.** Each rep made one screen, `task-1-screen-3.log` (caught 4, survived 0, invalid 0, 3 of 4
carried), with `--screen` first. Rep4 made a refused call first: it had staged the workspace with
`git add -f .sdd`, and the script refused, "mutant-run: the working tree has changed or untracked
paths; …". That call also passed `--screen` first. The last report section's `Mutants` line names
`task-1-screen-3.log` and its counts in each rep, such as rep4's "- Mutants:
<repo>/.sdd/plan/task-1-screen-3.log — caught 4, survived 0, invalid 0 (3 carried)." B1: 5 of 5.

- **B2, 5 of 5.** Each rep's new test at 2000 grams got a new patch 4, and Mutant 4's line names it.
  The seeded small-edge test answers survivor 1, as in round 0.
- **B5, 5 of 5.** Each answering commit carries `task 1 review`: rep1 `96eda2c` "Make 2000 grams
  medium" (the test) and `1614d18` "Fix the upper edge of medium" (the fix), each with `task 1 input
  shape` too; rep2 `096a0c2` and rep3 `7aa5b4e` "Fix a medium parcel at its upper edge"; rep4 `ded6e27`
  "Test a medium parcel at its upper edge, and make 2000 grams medium"; rep5 `3f49a1f` "Test a medium
  parcel at its upper edge", with `task 1 input shape` too. Reps 2 and 5 amended their commit after a
  failed `sed`, so each has one commit.
- **Step 7's new sentences in I2.** I2's new test answers the review finding, not a test that passed on
  the revert, so step 7's event does not occur. No rep shows a sign that the new sentences misled it.
  No rep left an invalid patch, none stopped adding the test it needed, and none rewrote a caught
  mutant's patch.
- All five reported DONE. The three plan tests are IDENTICAL in each.

**C1.** Reps 2 to 5 grepped the copy's `mutants.md` for "mutant", and so met the lines that name
`--screen`. Rep1 did not. Each rep made its `mutant-run` calls with no `--screen`: rep4 made two, and
the others one. Line 1 of `task-1-dispatch.txt` names `task-1-tests.log`. Line 2 names the rep's own
newest full run (`task-1-mutants.log`, rep4 `task-1-mutants-2.log`), caught 3, survived 0, invalid 0,
whose `head:` is the final HEAD, the seeded HEAD. B3: 5 of 5.

**C2.** Each rep made one `mutant-run` call, with no `--screen`. It wrote `task-1-mutants-2.log`
(caught 4, survived 0, invalid 0), whose `head:` is the final HEAD, the seeded fix commit. Line 1 names
`task-1-tests-2.log`, and line 2 names that `task-1-mutants-2.log`. B3: 5 of 5. Only rep3's stream
holds the text `--screen`.

**E1.** The scored reps are 3 to 7. Each made one commit of step 2 tests with `task 1 input shape`,
wrote its patches, and made one full call after the commit, at the final HEAD: rep3 `7354bff` "Test the
senior rule and the age boundaries" (caught 9 of 9), rep4 `bd7ee3b` "Test the age boundaries and the
senior rule" (8 of 8), rep5 `4513e0f` "Test the age boundaries and senior price" (8 of 8), rep6 `b6ebf71`
and rep7 `a2af9a8` "Test ticket price age boundaries and seniors" (10 of 10 each). B4: 5 of 5, with one
full run in each rep and no screen. B5: reached 5 of 5, passed 5. Both plan tests are IDENTICAL in
each.

**E2.** Each rep added a test with more than one cent left over, committed it, made a screen
(`task-1-screen.log`, 2 carried) and then a full run (`task-1-mutants-2.log`) at the final HEAD:

| Rep | New tests | Screen | Commit (`Mutant-step`) |
|---|---|---|---|
| 1 | `split(1001, 3) == [334, 334, 333]` and `split(2, 3) == [1, 1, 0]`, the second with a new patch 4 | caught 4, 2 of 4 carried | `3ee63dd` "Test several cents left over and a share that rounds down to zero" (input shape, survivor 2) |
| 2 | `split(1100, 3) == [367, 367, 366]` | caught 3, 2 of 3 carried | `18613bd` "Test a bill with several cents left over" (input shape, survivor 2) |
| 3 | `split(1100, 3) == [367, 367, 366]` | as rep2 | `7d104a1` "Test several cents left over in a split" (input shape, survivor 2) |
| 4 | `split(1102, 4) == [276, 276, 275, 275]` | as rep2 | `eab66a1` "Test several cents left over in a split" (survivor 2, input shape) |
| 5 | `split(1002, 4) == [251, 251, 250, 250]` | as rep2 | `c832592` "Test several cents left over in a bill split" (survivor 2, input shape) |

Rep2 called the script through a variable, `S=<copy>/subagent-driven-development/scripts/mutant-run`,
and then `$S --screen …` and `$S …`. A person read both calls from the command text (reading rule 5).

- **B4, 5 of 5.** Each rep's calls are a screen and then a full run, after the seeded full run. The
  last call is a full run at the final HEAD, after the rep's last commit.
- **B5, 5 of 5.** Each answering commit carries `task 1 survivor 2`, with `task 1 input shape`
  beside it, which the 2026-11-21 ruling allows.
- **B2, reached 5 of 5, passed 5.** Each new test answers survivor 2, and Mutant 2's line names it. Rep1's
  second test has its own new patch 4.
- **Step 7's new sentences in E2.** E2's new tests answer survivor 2 (step 6), so step 7's event does
  not occur. No rep shows a sign that the new sentences misled it: no invalid patch occurred, each rep
  added the test that survivor 2 needed, and none rewrote a caught mutant's patch.
- Both plan tests are IDENTICAL in each.

**Weakenings.** None. Every plan-test function in every round 1 rep, the two VOID reps included, is
IDENTICAL to `brief.md`'s.

**Round 1 by bar (D9).**

| Bar | Forced fixtures, treatment passes | Round 1 |
|---|---|---|
| B1 | I1 4 of 5, I2 5 of 5, I3 5 of 5 | met |
| B2 | I2 5 of 5, I3 5 of 5 | met |
| B3 | C1 5 of 5, C2 5 of 5 | met |
| B4 | E1 5 of 5, E2 5 of 5 | met |
| B5 | I2 5 of 5, I3 5 of 5, E2 5 of 5 | met |
| All | every fixture, 5 of 5 each | no weakening |

The reached-only events: B5 on I1 passed in the 4 reps that reached it, B5 on E1 passed 5 of 5, B2 on
E2 passed 5 of 5, and B2 was not reached on I1.

**B2 by round.**

| Fixture | Control | Round 0 (`cb2e170`) | Round 1 (`00e657b`) |
|---|---|---|---|
| I2 | 5 of 5 | 5 of 5 | 5 of 5 |
| I3 | 5 of 5 | 3 of 5 | 5 of 5 |

The restored sentences stay. They are the round 1 text for step 7, and B2 is met on each fixture that
forces it.

**The wording sentences in round 1.** Each sentence of round 0's table has the same verdict in round
1, kept, with these counts:

- the implementer prompt's step 5 sentence: B1 on I1 4 of 5, I2 5 of 5 and I3 5 of 5. Every call of
  every implementer rep passed `--screen` first. The one miss is a rep that made no call.
- `mutants.md` step 5's two bullets and `SKILL.md`'s order: B3 10 of 10, and B4 10 of 10.
- the trailer sentences: B5 15 of 15 on the forced fixtures, and every reached commit.

Two sentences are new in round 1, and only I3's event exercises them:

| Sentence | Fixtures | Verdict |
|---|---|---|
| "Each test that you add here gets a new mutant patch with its own number, whatever the test checks, and the `Mutant` line for that patch names the test." | I3 | kept: 5 of 5, with 9 new tests, each with its own new patch and line |
| "A mutant that a run has caught keeps its targets: do not re-aim it at the new test, and do not write its patch again to do so." | I3 | kept: 5 of 5, with mutant 1's line and patch the seeded ones in each |

No other fixture exercises them. I1 and E1 have no test that passes on the revert, because each task
adds its module, so the revert section reads "not loaded 1". I2's and E2's new tests answer a finding
or a survivor, not the revert. The controller fixtures add no test.

**Thin passes in round 1.**

- I1 rep1: no call, the one B1 miss on a fixture where B1 is met.
- I1 rep3: an invalid mutant, repaired before its last screen.
- I2 rep4: a refused first call.
- I2 reps 2 and 5: an amended commit after a failed `sed`.
- C1 rep1 and C2 reps 1, 2, 4 and 5: they never met the `--screen` text in `mutants.md`.

**Untested wording, round 1.** Round 0's list stands. It has the `SKILL.md` sentence on the final
review's fix pass (D11) and `mutants.md` step 7's executing-plans sentence. The new step 7 sentences
are exercised, by I3 only.

**Privacy, round 1.** Before the commit, `privacy_sweep.py` over the record and this folder gave the
same 6 hits as round 0, none in a rep output or in this subsection. `check_scrub.py` passed. No round 1
rep output holds an identity token or `credential_expires_at`.

**For the revision decision, round 1.** Every bar is met on every fixture that forces it. B2 on I3
went from 3 of 5 in round 0 to 5 of 5 in round 1. Round 1 is the last round that this task runs. It
ends with no bar missed, so the scope fence of D3 does not apply. The one new miss is I1 rep1's B1. It
lowers I1 from round 0's 5 of 5 to 4 of 5, which still meets the bar. That rep read no file of the
skill copy, so the revision did not reach it.

