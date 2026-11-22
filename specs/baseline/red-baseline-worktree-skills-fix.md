# Plan 103 micro-tests: the worktree skills fixes

This record holds the micro-tests of plan 103 (`specs/plans/103-worktree-skills-cc-guide-fixes.md`).
The plan fixes two claims in `finishing-a-development-branch` and `using-git-worktrees` that
contradict the Claude Code guide. It follows writing-skills' micro-test method, as plan 97 applied it.

Each arm has five scored reps for each case, each in a fresh context. A control arm reads the text at
the execution base. A person reads every answer by hand and grades it against the case's PASS and FAIL
columns. `show_reps.py` prints grading sheets and flags, never grades.

Task 1 writes the kit, the Base, Cases, Bars, Predictions and rules sections, and the `## Control`
section. Tasks 2 and 3 each append a `## Treatment: <case>` section. The rules in this file were
committed before any rep ran, and no reading is added after a scored rep is seen.

## Base

- **BASE:** `07ea57436aedaf8ea38b0a48434ed8c222fad95a` (`07ea574`). It is the execution base, the control
  arms' text ref and the review base of Task 1. The control prompts hold the two SKILL.md files as
  `git show 07ea57436aedaf8ea38b0a48434ed8c222fad95a:<path>` prints them, never through `~/.claude`.
- **Anchor check (Step 1), run at BASE before any edit.** Each command printed `<path>:1`:

  ```bash
  git grep -c 'whether pushed or not, and the native tool leaves them out' -- skills/using-git-worktrees/SKILL.md
  git grep -c 'The desktop app cleans up or reuses a worktree it started when that session is archived.' -- skills/finishing-a-development-branch/SKILL.md
  git grep -cF 'git rev-list --count <headRefOid>..<branch>' -- rules/pr-lifecycle.md
  git grep -c 'detaches the worktree' -- README.md
  ```

  Anchors 3 and 4 differ from the plan's text. Task 5 ran first (`33259a9`) and re-wrapped or replaced the
  text that the plan's two old anchors match. The controller ruled that these two replacements stand in
  for them. Anchors 1 and 2 stand as the plan wrote them. Task 1 does not edit `rules/pr-lifecycle.md`,
  `README.md` or the option b item of `specs/deferred_items.md`.
- **Model and flags (every rep and the probe):** `claude -p --model claude-sonnet-5-5 --tools ""
  --strict-mcp-config --setting-sources "" --disable-slash-commands --no-session-persistence
  --output-format json --max-budget-usd 0.50`, under `env -i`, with `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`
  and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`. Each rep starts in its own new, empty folder under `/tmp`,
  outside every repository. A rep has no tools.

## Kit

The kit is `specs/baseline/red-baseline-worktree-skills-fix/kit/`. It starts from plan 97's review kit
(`specs/baseline/red-baseline-change-reverted-mutant/review-kit/`).

| File | Role |
|---|---|
| `run_reps.sh` | Runs reps. Copy of plan 97's runner, with its own scratch path and the void handling below. |
| `probe.sh`, `isolation_probe.txt` | The isolation probe. Copies of plan 97's, with the model set to `claude-sonnet-5-5`. |
| `kit_identity.py`, `check_scrub.py` | The identity scrub and its check. Copies of plan 97's. |
| `postprocess.py` | New. Voids a rep or keeps it scrubbed, and drops `origin` and `credential_expires_at`. |
| `test_postprocess.py`, `test_postprocess_shapes.py`, `test_run_reps.py` | New. The self-test, with a stub `claude` and no model. |
| `build_prompts.py` | New. `build_prompts.py <case> <arm> <ref>` writes `prompts/<case>-<arm>.txt`. |
| `show_reps.py` | New. Prints grading sheets, status flags and the spend. |
| `fixtures/<case>.txt` | New. The session state for each case. |

**Next-kit fix.** This kit closes the backlog item "Void a no-tools rep that took a peer message
(next-kit fix)" in `specs/deferred_items.md`. A message that a peer session sends to a busy no-tools rep
arrives as an extra turn after the answer. The JSON `result` is then the reply to that message. The kit
now does three things:

1. `postprocess.py` reads the raw JSON. A `result_index` above 0 voids the rep. An `origin` that is not
   null voids it too. A `result_index` that is not a whole number voids it, since 0 cannot be shown.
   The check runs before anything is dropped.
2. A kept rep loses `origin`, `credential_expires_at`, `session_id` and `uuid` at any depth. Every string
   in it goes through the scrub (`$HOME` as `~`, `$TMPDIR` as `$TMPDIR`, the identity forms as tokens).
3. A void rep gets no `rep<N>.json`. `run_reps.sh` writes `rep<N>.VOID`, a one-line note with no answer
   text, and prints `rep<N> VOID (<verdict>)`. The batch then exits 3 (1 if a rep also failed). The
   caller runs a replacement under a new rep number: the overwrite guard refuses a number that has a
   `.VOID` note. The raw JSON stays in the scratch folder and counts toward the spend.

The raw JSON goes to `~/.cache/agent-skills/scratch/worktree-skills-fix/<out-dir's parent>/<out-dir>/`,
outside the repository. It holds a session id, and a peer's `origin` if one reached the rep. Nobody
messages or subscribes to a running rep. No rep gets its own `HOME`, so no `syncClaudeAiSkills` setting
applies. A rep has no tools, so the `Read(~/**)` gap of tool kits does not arise.

**Self-test.** `uv run python build/run_suites.py worktree-skills-fix-kit` runs it. It covers the void
on `result_index` and on `origin`, the drop of the private keys at any depth, the scrub, the command
line, and the wiring of `run_reps.sh` with a stub `claude`.

## Cases

Each prompt holds, in order, the full SKILL.md text of the case's skill at the arm's ref, the case's
session state (`fixtures/<case>.txt`) and a task. The task asks the rep to continue the session and to
list, in order, each command (`RUN:`), each tool call (`TOOL:`, with its name and arguments) and each
thing it says to its partner (`SAY:`). It asks the rep to stop where it would wait for the partner.

A rep has no tools. So each fixture states the output of every command that the skill has the agent run
before the scored call. The outputs come from real scratch repositories, made with `mktemp -d` under
`/tmp`, outside every repository. The commands ran there, and the fixtures hold their real output. The
fixtures write the scratch path as `/work/atlas`, and a remote path as `/work/mirror/atlas.git`.
Author names are test values. The `archive-relay` repository holds two real tests, and the fixture's
test run is `uv run --no-project --with pytest python -m pytest -q` in that repository.

| Case | Skill | Fixture | PASS | FAIL | Bar |
|---|---|---|---|---|---|
| `noremote` | using-git-worktrees | A normal checkout at `/work/atlas`, three local commits on `main`. The partner said yes to a worktree on branch `feat/rate-limit`, and declared no worktree directory. `EnterWorktree` is available. The base check printed git's `unknown revision` error, and `git remote` prints nothing. `ls -d .worktrees` prints `.worktrees`, and `git check-ignore -q .worktrees/` exits 0. | `git worktree add` on a new branch from HEAD, then `EnterWorktree` with `path` | `EnterWorktree` with `name`, and no `git worktree add` | non-regression |
| `remote-nohead` | using-git-worktrees | As `noremote`, but `git remote -v` lists `origin`, `git fetch origin` failed, and the cached `origin/main` is two commits behind HEAD. | as `noremote` | as `noremote` | non-regression |
| `archive-relay` | finishing-a-development-branch | Step 2 recorded MADE_BY `launcher` and MAIN_GIT `allowed`. The desktop app started the session in the worktree. Option 1's merge and tests passed in MAIN_ROOT. The worktree holds an untracked `notes.md` (`git status --porcelain` there prints `?? notes.md`). The run is at Step 6, and the partner says they will archive this session next. | tells the partner that archiving can discard uncommitted changes in the worktree, and that the branch can outlive the archive | says that archiving removes the worktree at once or deletes the branch, or leaves out either fact | factual |

Fixture sources:

- `noremote`: a repository with three commits on `main`, no remote, a `.gitignore` line `.worktrees/` and
  an empty `.worktrees` folder. The commands: Step 0's three, the submodule guard, `git log --oneline`,
  Step 1a's base check, `git remote`, `ls -d .worktrees` and `git check-ignore -q .worktrees/`.
- `remote-nohead`: the same, but the first commit was pushed to a local bare repository named `origin`
  (so `origin/main` exists and `origin/HEAD` does not), two more commits followed, and the remote's URL was
  then set to a path that does not exist. The added commands: `git remote -v`, `git fetch origin` and
  `git rev-list --count origin/main..HEAD`, which prints 2.
- `archive-relay`: a repository with a bare `origin`, a linked worktree at `.claude/worktrees/rate-limit`
  on branch `claude/rate-limit-4f2a` with two commits, and an untracked `notes.md` there. The commands:
  Step 2's four, the `MAIN_GIT` probe, Option 1's `git checkout`, `git pull`, `git merge`, the test run,
  and `git status --porcelain` and `git branch --show-current` in the worktree.

## Reading rules

1. **Hand grading.** A person reads every answer in full and grades it against the case's PASS and FAIL
   columns. No grade comes from a keyword match. Each grade in the Control section carries a short quote
   that justifies it.
2. **Branches.** Where an answer branches with IF lines, grade the branch that matches the stated facts.
3. **No call.** An answer with neither the PASS call nor the FAIL call, such as one that stops to ask
   first, counts as a FAIL in both arms.
4. **Sheets.** A grading sheet (`show_reps.py sheet`) names the rep id and the case, never the arm. Before
   a treatment arm is graded, one of its sheets is diffed against a control sheet of the same case.
   Only the rep's answer may differ.

The grading edges below came after the pilot (Pilot) and before any scored rep. The pilot reps are not
scored, and no edge was changed after a scored rep was seen.

5. **`noremote` and `remote-nohead`, the PASS call.** It has two parts, in this order. First a `RUN:`
   line of `git worktree add` that creates a new branch (`-b <branch>`) with no start point, or with
   `HEAD` as the start point. Then a `TOOL:` line of `EnterWorktree` with a `path` argument that names
   that worktree. A start point that is `origin/<name>` or another default-branch ref misses HEAD's
   commits, so it is not a PASS. The worktree's folder is free (`.worktrees/...` or another).
6. **`noremote` and `remote-nohead`, the FAIL cases.** An `EnterWorktree` with `name` is the FAIL call,
   also when `git worktree add` runs as well. An answer that runs `git worktree add` and then stops
   before the `EnterWorktree` `path` call, or enters the worktree with `cd` only, or calls the tool
   before the git command, lacks the PASS call. It is a FAIL by rule 3.
7. **`archive-relay`, the two facts.** PASS needs both, told to the partner in the answer's `SAY:` text,
   and no unhedged claim that archiving removes the worktree at once or deletes the branch. A hedged
   claim ("may", "can", "should", "if it does not") does not trigger the FAIL column by itself.
   - **Fact 1: archiving can discard uncommitted changes in the worktree.** The answer links the
     archive to the loss of `notes.md` or of uncommitted work. "Copy `notes.md` out before you archive,
     because archiving may clean up the worktree and the file goes with it" counts. "Commit or move
     `notes.md`" with no link to the archive does not count.
   - **Fact 2: the branch can outlive the archive.** The answer says the branch can or will still exist
     after the archive, or tells the partner to delete it after archiving without making that depend on
     the app failing to clean up. A branch command that appears only as a fallback ("if the app does not
     clean up, run ...") does not count. A report of the agent's own choice to leave the branch in place
     now does not count either.

## Bars

- **Non-regression** (`noremote`, `remote-nohead`): the treatment passes at least the control's count
  minus one. A miss stops the task for an owner ruling.
- **Factual** (`archive-relay`): the correction ships whatever the control scores. The treatment passes
  at least 4 of 5. Below that, run one wording round with the facts unchanged, then ask the owner.

## Predictions

Written before any rep ran. The controls pass `noremote` and `remote-nohead` and fail `archive-relay`.

## VOID rule

A rep is void, and a replacement runs under a new rep number, when any of these hold. A void rep is
never scored.

1. `run_reps.sh` voided it: `result_index` above 0 or an `origin` that is not null (Kit). The script
   exits 3 and writes `rep<N>.VOID`.
2. The raw JSON is unreadable or not an object (the script's `unreadable` verdict).
3. `show_reps.py status` flags a tool or the advisor (`num_turns` not 1, or an iteration that is not a
   message, or more than one model), an error or a budget stop (`is_error` or a `subtype` that is not
   `success`), or an empty result.
4. The run timed out or exited without writing JSON.
5. The model refuses the task, or the answer does no part of it (no `RUN:`, `TOOL:` or `SAY:` line). An
   answer that stops to ask first has such lines, so it is a FAIL by reading rule 3, never void.

A void rep still counts toward the spend. A control arm is complete at five scored reps with no void
rep among them.

## Spend stop

These are the owner's stop rules. A run that cannot ask the owner ends BLOCKED and gives the numbers.

- Each rep has a $0.50 cap (`--max-budget-usd 0.50`).
- The cost is the sum of `total_cost_usd` over every rep JSON in the scratch folder (the pilot, the
  controls and the void reps). `show_reps.py cost` prints it.
- The control arms run one case at a time. After each case, the control cost is added up. At $3.00 before
  all three cases are scored, the run stops.
- The whole kit (probe, pilot and controls) stops at $10.00.
- If the pilot probe answers YES on any of `isolation_probe.txt` lines 1 to 6, the task stops. Line 7
  (the user's identity) may read YES. That is the open item "Account identity reaches the isolated
  micro-test runs". It does not block, since no case depends on who the user is, and the identity scrub
  runs on every rep (plan 97's controller ruling, 2026-11-13).

## Isolation probe

`probe.sh` ran `isolation_probe.txt` on the installed binary (Claude Code 2.1.323, model
`claude-sonnet-5-5`) with the reps' flags, after the commit of the cases. The JSON is in the scratch
folder `probe/`. Its `is_error` is false, `num_turns` is 1, `result_index` is 0 and `origin` is null
(the probe does not go through `postprocess.py`, so these were read by hand). It cost $0.008.

| Line | Answer |
|---|---|
| 1. CLAUDE.md text | NO |
| 2. Output style | NO |
| 3. "Plain technical English" or "AWS Guidance" rule | NO |
| 4. SessionStart hook context | NO |
| 5. Auto-memory or `MEMORY.md` | NO |
| 6. Skill or slash command list | NO |
| 7. The user's name or email address | YES, with the quote of an email address (not recorded here: this repository is public) |

Lines 1 to 6 read NO, so the task goes on. Line 7 is the open item "Account identity reaches the isolated
micro-test runs". It does not block (Spend stop), and the identity scrub runs on every rep.

## Pilot

One control rep for each case, at BASE, into `kit/runs/<case>-pilot/rep1.json`. The pilot reps are not
scored. Each ran with the reps' flags. Each answered in the `RUN:`/`TOOL:`/`SAY:` form, in one turn, with
no tool, no error and no peer turn. Their cost: `noremote` $0.034, `remote-nohead` $0.036,
`archive-relay` $0.049. Read in full, by the rules above:

- **`noremote` pilot:** a `git worktree add .worktrees/feat/rate-limit -b feat/rate-limit`, then
  `EnterWorktree` with `path`. It would be a PASS.
- **`remote-nohead` pilot:** the same two calls. It would be a PASS.
- **`archive-relay` pilot:** it told the partner that "Archiving may clean up the worktree, and the file
  would go with it" (fact 1). It named the branch commands only as a fallback ("If it doesn't, run
  these"), and it said it left the branch in place now. By reading rule 7 that leaves out fact 2. It
  would be a FAIL, and this is why rule 7 names the fallback case.

## Control

Five scored reps for each case, at BASE (`07ea57436aedaf8ea38b0a48434ed8c222fad95a`), each in a fresh
`claude -p` with the flags of Base. The prompts are `kit/prompts/<case>-control.txt`
(`kit/prompts/MANIFEST.txt` gives the sha256 of each prompt and of each skill text). The scrubbed reps
are `kit/runs/<case>-control/rep1.json` to `rep5.json`. Each case ran in one batch, and each batch exited 0:
no rep was void under the VOID rule. The void path ran only in the self-test. Each rep was read in
full, by the reading rules, from a sheet that names the rep id and the case.

### `noremote`: control 5 of 5 (cost $0.054)

All five reps ran `git worktree add .worktrees/feat/rate-limit -b feat/rate-limit` with no start point,
and then `EnterWorktree` with `path`. Each ran the git command first.

| Rep | Grade | Quote |
|---|---|---|
| 1 | PASS | `RUN: git worktree add .worktrees/feat/rate-limit -b feat/rate-limit`, then `TOOL: EnterWorktree path=/work/atlas/.worktrees/feat/rate-limit` |
| 2 | PASS | the same RUN line, then `TOOL: EnterWorktree {"path": "/work/atlas/.worktrees/feat/rate-limit"}` |
| 3 | PASS | the same RUN line, then `TOOL: EnterWorktree path="/work/atlas/.worktrees/feat/rate-limit"` |
| 4 | PASS | the same RUN line, then `TOOL: EnterWorktree path=/work/atlas/.worktrees/feat/rate-limit` |
| 5 | PASS | the same RUN line, then `TOOL: EnterWorktree path="/work/atlas/.worktrees/feat/rate-limit"` |

### `remote-nohead`: control 5 of 5 (cost $0.084)

All five reps took the same two calls. Each one said that the remote is unreachable or that the fetch
failed. Reps 2 and 5 said that this makes the `origin/main..HEAD` count of 2 unreliable. None used
`origin/main` as a start point.

| Rep | Grade | Quote |
|---|---|---|
| 1 | PASS | `RUN: git worktree add .worktrees/feat/rate-limit -b feat/rate-limit`, then `TOOL: EnterWorktree path=...` |
| 2 | PASS | the same RUN line, then `TOOL: EnterWorktree {"path": "/work/atlas/.worktrees/feat/rate-limit"}` |
| 3 | PASS | the same RUN line, then `TOOL: EnterWorktree path="/work/atlas/.worktrees/feat/rate-limit"` |
| 4 | PASS | the same RUN line, then `TOOL: EnterWorktree {"path": "/work/atlas/.worktrees/feat/rate-limit"}` |
| 5 | PASS | the same RUN line, then `TOOL: EnterWorktree path=/work/atlas/.worktrees/feat/rate-limit` |

### `archive-relay`: control 1 of 5 (cost $0.045)

Every rep left the worktree and the branch alone, and every rep told the partner about `notes.md`. None
said that the branch can outlive the archive, except rep 4, in one marginal clause. Four reps tell the
partner that the app should or does clean up the worktree on archive, and give `git branch -d` only for
the case that it does not.

| Rep | Fact 1 (archive can discard uncommitted work) | Fact 2 (branch can outlive the archive) | Grade | Quote |
|---|---|---|---|---|
| 1 | told, with an unhedged clause | not told | FAIL | "the desktop app removes worktrees it started on archive"; the branch command only in "If it doesn't, run these" |
| 2 | told | not told | FAIL | "copy it out first, because removing the worktree would delete it"; "If it doesn't, run these" |
| 3 | told | not told | FAIL | "If archiving removes the worktree, that file goes with it"; "If it doesn't, run these" |
| 4 | told, by the chain of two sentences | told, marginal | PASS (marginal) | "Archiving the session in the desktop app should clean up the worktree"; "Removing the worktree will delete it"; "If the worktree or branch is still there afterwards" |
| 5 | told | not told | FAIL | "removing the worktree would delete it"; "If it doesn't, you can remove both" |

Rep 4's grade rests on two readings that a stricter reader could refuse. Fact 1 comes from two sentences
that the rep wrote one after the other, not from one sentence that names the archive. Fact 2 comes from
"still there afterwards", which names the branch beside the worktree. A strict reading would grade rep 4
a FAIL and give the control 0 of 5. The factual bar ships the correction whatever the control scores, so
no decision turns on it. The prediction held for four of five reps.

### Spend

| Item | Cost |
|---|---|
| Isolation probe | $0.008 |
| Pilot reps (3, unscored) | $0.119 |
| Control `noremote` (5) | $0.054 |
| Control `remote-nohead` (5) | $0.084 |
| Control `archive-relay` (5) | $0.045 |
| **Control arms, scored reps only** | **$0.183** |
| **Whole kit (probe, pilot, controls)** | **$0.310** |

Both stops hold: the control arms ended far below $3.00 even with the probe and the pilot added, and the
whole kit is far below $10.00. `show_reps.py cost ~/.cache/agent-skills/scratch/worktree-skills-fix` gives
the sums, from the raw JSON.

### Plan 104's kit did not meet the next-kit item

Plan 104's kit (`specs/baseline/red-baseline-mutant-screen-runs/kit/`) was built before this one. It is a
tools kit, and it does not close the backlog item "Void a no-tools rep that took a peer message". Its
`rep_tools.py` strips only `credential_expires_at`. It has no `result_index` check, and it never drops
`origin`. Its `grade.py` only flags a peer `origin` (V9). So this kit starts from plan 97's review kit
and builds the void and the drop itself (Kit).
