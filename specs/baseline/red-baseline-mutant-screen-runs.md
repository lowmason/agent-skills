# Plan 104 micro-tests: mutant screen runs

This record holds the micro-tests of plan 104 (`specs/plans/104-mutant-screen-runs.md`). The spec,
`specs/mutant-screen-runs.md`, asks for them in Verification. They follow writing-skills' micro-test
method, main's copy, as plan 97 applied it (`specs/plans/completed/97-change-reverted-mutant.md:105`).
Each arm has five scored reps per fixture, each in a fresh context. A control arm runs today's text
first. A person reads every verdict by hand from the rep's full output. `grade.py` prints reading
aids, never verdicts.

The rules (Base to Spend stop) were written before any rep ran, the probes and pilots included.
They are committed before any scored rep. No reading is added after a rep is seen. Task 4 adds
`## Control`, and Task 8 adds `## Treatment`.

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
- **`test_msr_kit.py`** has 16 tests with a stub `claude` and no model. Suite
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

**The scene texts.** I1's scene is plan 97's, with the venv's path. I2's says that the task was
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

**Reading rules.** These make the table's readings exact. They were written before any rep.

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
   is still a call for B1 and B3. A **run**, for B4, is a call that wrote a run file. The calls are
   read in stream order.
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
9. **B4.** In E1 the first run and the last run are full runs. In E2 the seeded first run is full,
   and the rep makes at least one screen before its last run. In both, the last run is a full run
   whose `head:` is the final HEAD, and it comes after the rep's last commit. Runs between the first
   and the last may be full runs or screens.
10. **B5.** A commit answers a cause when its diff is the rep's answer to that cause: a survivor
    (`mutants.md` step 6), an input shape with no test (step 2), a test that passed on the revert
    (step 7) or the review finding (I2). A person reads that from the commit's diff and the rep's
    stream. The value is the trailer's value as `git log` prints it, compared as text: `task 1
    survivor <K>`, `task 1 input shape`, `task 1 revert` or `task 1 review`. On a forced fixture, the
    bar needs every answering commit to carry the forced value. The task's own GREEN commit in I1
    and any commit that answers no cause must carry no `Mutant-step` value.
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
   - A tool result that spills to `~/.claude/projects/…/tool-results/` lands in the rep's own `HOME`,
     inside its folder.
2. **A second model.** `modelUsage` names a model other than the one that the probe's init record
   gives for the rep's model (`sonnet` for implementer and controller reps, `opus` for inline reps), or
   `usage.iterations` holds a type other than `message`.
3. **An error.** The run errors, or an implementer rep ends with no status line (reading rule 1) for a
   reason other than its budget. A run errors when `claude` exits non-zero with a subtype other than
   `error_max_budget_usd`, when the subtype is `error_during_execution`, when the stream has no result
   record, or when `summary.json` holds `kit_error`. A stream line that is not a JSON object is a kit
   error (controller ruling, Task 3), because a skipped line could hide a peer `origin`. `grade.py`
   prints each such line as `stream line <n> is not JSON: VOID case 3`.
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

## Isolation probe

Every probe runs `probe.sh <model> <out-file>` with `isolation_probe.txt`, from
`/private/tmp/msr104/probe/repo/`, an empty folder outside every repository, with the command in Kit.
The probe passes when the init record lists exactly `Bash`, `Read`, `Edit` and `Write` and no
cross-session tool, and every probe line reads NO.
