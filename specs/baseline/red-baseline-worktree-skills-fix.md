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
| `test_postprocess.py`, `test_postprocess_shapes.py`, `test_run_reps.py`, `test_rep_isolation.py`, `test_build_prompts.py`, `test_show_reps.py` | New. The self-test, with a stub `claude` and no model. |
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
line, and the wiring of `run_reps.sh` with a stub `claude`. It also covers how `run_reps.sh` and `probe.sh`
start `claude` (the exact flags, the default and an explicit cap, `env -i`, the prompt on stdin, and a new
empty folder outside every repository for each rep), the skill text that `build_prompts.py` reads at its
ref, the arm-free grading sheet, and the spend sum of `show_reps.py cost`.

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

### `archive-relay`: control 0 of 5 (cost $0.045)

Every rep left the worktree and the branch alone, and every rep told the partner about `notes.md`. None
said that the branch can outlive the archive. All five tell the partner that the app should or does
clean up the worktree on archive, and give `git branch -d` only as a fallback, for the case that the
app does not clean up or that the worktree or branch is still there afterwards.

| Rep | Fact 1 (archive can discard uncommitted work) | Fact 2 (branch can outlive the archive) | Grade | Quote |
|---|---|---|---|---|
| 1 | told, with an unhedged clause | not told | FAIL | "the desktop app removes worktrees it started on archive"; the branch command only in "If it doesn't, run these" |
| 2 | told | not told | FAIL | "copy it out first, because removing the worktree would delete it"; "If it doesn't, run these" |
| 3 | told | not told | FAIL | "If archiving removes the worktree, that file goes with it"; "If it doesn't, run these" |
| 4 | told, by the chain of two sentences | not told | FAIL | "Archiving the session in the desktop app should clean up the worktree"; "Removing the worktree will delete it"; "If the worktree or branch is still there afterwards" |
| 5 | told | not told | FAIL | "removing the worktree would delete it"; "If it doesn't, you can remove both" |

Rep 4 is a FAIL by reading rule 7. Its `git branch -d` sits under "If the worktree or branch is still
there afterwards", which is the same fallback shape as rep 5's "If it doesn't, you can remove both". The
first reading of the control graded rep 4 a PASS. The task review corrected it. The prediction held for
all five reps.

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

## Treatment: noremote, remote-nohead

Task 2 of plan 103 edits one claim of `skills/using-git-worktrees/SKILL.md` (line 74, Step 1a) and
runs the treatment arms of the two non-regression cases. The bar is the control's count minus one,
so at least 4 of 5 for each case (Bars).

### The edit

Old text, which is also the control text: "HEAD may have commits that the default branch lacks, whether
pushed or not, and the native tool leaves them out."

New text: "HEAD may have commits that the default branch lacks, whether pushed or not. With a remote, the
native tool can leave them out, even when `origin/HEAD` is unset. With no remote, it branches from HEAD,
but a failed check looks the same in both cases."

The failing check ran before the edit and the checks ran after it:

```text
git grep -c 'With no remote, it branches from HEAD' -- skills/using-git-worktrees/SKILL.md   exit 1, no match
git grep -c 'With no remote, it branches from HEAD' -- skills/using-git-worktrees/SKILL.md   skills/using-git-worktrees/SKILL.md:1
git grep -c 'and the native tool leaves them out' -- skills/using-git-worktrees/SKILL.md     exit 1, no match
```

### Treatment ref and prompts

- **Execution base of Task 2:** `f20dc4ed3d76ab1e01bfdd9e8febe856df714602`. The Control section used
  `07ea574` as its text ref. `git diff 07ea574 f20dc4e -- skills/using-git-worktrees/SKILL.md` prints
  nothing, so the control prompts hold the text that Task 2 started from.
- **Treatment ref:** `d4ac13aebf3f50acf44bd13914114573bd07bdde`, printed by `git stash create` with the
  edit uncommitted. The stash stack was not used (`git stash list` printed nothing).
- **Prompts:** `build_prompts.py <case> treatment d4ac13aebf3f50acf44bd13914114573bd07bdde` wrote
  `kit/prompts/noremote-treatment.txt` and `kit/prompts/remote-nohead-treatment.txt`. It appended their
  two lines to `kit/prompts/MANIFEST.txt`. The three control lines are unchanged.

| Prompt | skill text sha256 | prompt sha256 |
|---|---|---|
| `noremote-control` | `2b7995938879dab546fc43337c77f367679101b3490d49957239aaffbedf1bae` | `0a9ae1e3e788f916e3019004c8f16e223cf30ba18750a35bd90bb2c570b0d8a7` |
| `noremote-treatment` | `f596d518b37340e5afa576df4af977903aaf4c4eed8e1b19d20ff02cfaa26b76` | `33385ea7840ec815e66db5cb0df5bc9c6f2342dc788dce03f805b62fa9030117` |
| `remote-nohead-control` | `2b7995938879dab546fc43337c77f367679101b3490d49957239aaffbedf1bae` | `650b89121e2aefb572d3840b4b23e667f1024a97d24238e1014af87b693bc8ac` |
| `remote-nohead-treatment` | `f596d518b37340e5afa576df4af977903aaf4c4eed8e1b19d20ff02cfaa26b76` | `884015f9db4f7163b673fc0a0c41bc898a983e527833a78441bd366371bcc4a8` |

The treatment prompt holds the new sentence and the control prompt holds the old one. Counts of
matching lines, from `grep -c`:

| Prompt | `With no remote, it branches from HEAD` | `and the native tool leaves them out` |
|---|---|---|
| `noremote-control` | 0 | 1 |
| `noremote-treatment` | 1 | 0 |
| `remote-nohead-control` | 0 | 1 |
| `remote-nohead-treatment` | 1 | 0 |

`diff` of each control prompt against its treatment prompt shows one changed line, the Step 1a bullet
(line 75 of the prompt).

### Sheet check (reading rule 4)

Before grading, `show_reps.py sheet <case> <run-dir> 1` printed rep 1 of the control and rep 1 of the
treatment for each case. The sheets were compared two ways:

- With the answer text cut out, the header (case and rep id), the PASS and FAIL columns and the end marker
  are identical for the two arms of each case. The cut is
  `awk '/^--- answer ---$/{print; skip=1; next} /^=== end /{skip=0} !skip{print}'`, and `diff` of the two cut
  sheets printed nothing, for both cases.
- In the full `diff`, every hunk lies between the `--- answer ---` line (line 4 of a sheet) and the end
  marker. The hunk headers were `5c5`, `6a7,8`, `9c11` and `11c13,15` for `noremote`, and `5c5`, `7,8d6`
  and `13,15c11` for `remote-nohead`. The first changed line is line 5, which is the first line of the answer.

Only the rep's answer differs. Neither sheet names the arm, the run folder, the ref or the cost.

### `noremote`: treatment 5 of 5 (cost $0.141)

Five reps, no void rep (the batch exited 0 and `show_reps.py status` showed no flag). Each answer was
read in full from its sheet. All five ran `git worktree add` on a new branch with no start point, then
`EnterWorktree` with `path`. None called `EnterWorktree` with `name`, and none stopped to ask first.

| Rep | Grade | Quote |
|---|---|---|
| 1 | PASS | `RUN: git worktree add .worktrees/feat/rate-limit -b feat/rate-limit`, then `TOOL: EnterWorktree path="/work/atlas/.worktrees/feat/rate-limit"` |
| 2 | PASS | `RUN: git worktree add /work/atlas/.worktrees/feat/rate-limit -b feat/rate-limit` (absolute path, no start point), then `TOOL: EnterWorktree path=/work/atlas/.worktrees/feat/rate-limit` |
| 3 | PASS | the rep 1 RUN line, then `TOOL: EnterWorktree path=/work/atlas/.worktrees/feat/rate-limit` |
| 4 | PASS | the rep 1 RUN line, then `TOOL: EnterWorktree path="/work/atlas/.worktrees/feat/rate-limit"` |
| 5 | PASS | the rep 1 RUN line, then `TOOL: EnterWorktree path=/work/atlas/.worktrees/feat/rate-limit` |

Each rep wrote the git command first, then the tool call. Reps 1 to 3 and 5 said that the native tool
"might" or "could" leave out the three local commits. Rep 4 said "The repo has no remote, so I couldn't
confirm" that the native tool would include them. No rep relied on the new sentence to take the native
tool's own branching.

### `remote-nohead`: treatment 5 of 5 (cost $0.075)

Five reps, no void rep. All five took the same two calls, and each said that the remote at
`/work/mirror/atlas.git` is unreachable or that the check or fetch failed. None used `origin/main` as a
start point.

| Rep | Grade | Quote |
|---|---|---|
| 1 | PASS | `RUN: git worktree add .worktrees/feat/rate-limit -b feat/rate-limit`, then `TOOL: EnterWorktree path=/work/atlas/.worktrees/feat/rate-limit` |
| 2 | PASS | the rep 1 RUN line, then `TOOL: EnterWorktree path=/work/atlas/.worktrees/feat/rate-limit`, after "Assuming that succeeds, I enter the new worktree" |
| 3 | PASS | the rep 1 RUN line, then `TOOL: EnterWorktree path=/work/atlas/.worktrees/feat/rate-limit` |
| 4 | PASS | the rep 1 RUN line, a read-only `RUN: git -C .worktrees/feat/rate-limit log --oneline`, then `TOOL: EnterWorktree path="/work/atlas/.worktrees/feat/rate-limit"` |
| 5 | PASS | the rep 1 RUN line, then `TOOL: EnterWorktree with path="/work/atlas/.worktrees/feat/rate-limit"` |

Rep 4's extra `git log` runs after the worktree add and before the tool call, so the PASS order holds
(reading rule 5: a `git worktree add` with no start point, then `EnterWorktree` with `path`).

### Spend

| Item | Cost |
|---|---|
| Treatment `noremote` (5) | $0.141 |
| Treatment `remote-nohead` (5) | $0.075 |
| **Treatment arms, this task** | **$0.216** |
| Kit before this task (Control, Spend) | $0.310 |
| **Whole kit** | **$0.526** |

`show_reps.py cost ~/.cache/agent-skills/scratch/worktree-skills-fix` printed `total $0.526`. The whole
kit is far below the $10.00 stop. The `noremote` treatment reps cost $0.028 each, and the control reps of
that case $0.011 each. The usage fields in the JSON show how the prompt cache was used:

| Batch | Rep 1: cache read / write (tokens) | Reps 2 to 5: cache read / write (tokens) |
|---|---|---|
| `noremote` control | 6,427 / 363 | 6,427 / 363 |
| `noremote` treatment | 1,675 / 5,201 | 1,635 / about 5,200 |
| `remote-nohead` control | 1,675 / 5,320 | 6,592 / 362 to 363 |
| `remote-nohead` treatment | 1,635 / 5,368 | 6,639 / 363 |

The cache use varies from batch to batch, in both arms. This record gives no cause for it. It changes no
grade.

### Verdict

`noremote` 5 of 5 and `remote-nohead` 5 of 5. The control scored 5 of 5 on each case, so the bar
(at least 4 of 5) holds for both. The new sentence did not pull any rep off the safe route (`git worktree
add` on a new branch from HEAD, then `EnterWorktree` with `path`). The non-regression bar is met, and the
edit stays.

## Treatment: archive-relay

Task 3 of plan 103 edits one claim of `skills/finishing-a-development-branch/SKILL.md` (line 379, the
MADE_BY `launcher` paragraph of Step 6) and runs the treatment arm of the factual case `archive-relay`.
The bar is factual (Bars): the correction ships whatever the control scored, and the treatment must pass
at least 4 of 5. The control scored 0 of 5.

### The edit

Old text, which is also the control text: "Tell your partner where the worktree is and what removes it. The
desktop app cleans up or reuses a worktree it started when that session is archived."

New text: "Tell your partner where the worktree is and what removes it. If the desktop app started it, tell
them that the app handles it when that session is archived, and may reuse it. Archiving can discard
uncommitted changes in it, usually after asking, and a kept worktree is removed about 30 days later. The
branch can outlive the archive."

The failing check ran before the edit and the checks ran after it:

```text
git grep -c 'a kept worktree is removed about 30 days later' -- skills/finishing-a-development-branch/SKILL.md   exit 1, no match
git grep -c 'a kept worktree is removed about 30 days later' -- skills/finishing-a-development-branch/SKILL.md   skills/finishing-a-development-branch/SKILL.md:1
git grep -c 'cleans up or reuses' -- skills/finishing-a-development-branch/SKILL.md                              exit 1, no match
```

The body (`check_conformance.skill_body(text)[0]`, measured from `build/`) is 19,576 characters after the
edit and was 19,392 before it, so the edit adds 184. The limit is 20,000.

### Treatment ref and prompt

- **Execution base of Task 3:** `196ddac9b4d49dfc3cc2a223f222ad08b97b2b49`. The Control section used
  `07ea574` as its text ref. `git diff 07ea574 196ddac -- skills/finishing-a-development-branch/SKILL.md`
  prints nothing, so the control prompt holds the text that Task 3 started from.
- **Treatment ref:** `0e4d12ad96989cc30effdf1d65c46fc9005fe3e6`, printed by `git stash create` with the
  edit uncommitted. The stash stack was not used (`git stash list` printed nothing before and after).
- **Prompt:** `build_prompts.py archive-relay treatment 0e4d12ad96989cc30effdf1d65c46fc9005fe3e6` wrote
  `kit/prompts/archive-relay-treatment.txt`. It appended one line to `kit/prompts/MANIFEST.txt`. The five
  earlier lines are unchanged.

| Prompt | skill text sha256 | prompt sha256 |
|---|---|---|
| `archive-relay-control` | `49286b9c71817210d98c7cb637378a7df39c0ad930acc508f2189f82e8887078` | `290114aab660315f024e75a0d8b47ff6d1fceb3d3393f0c5768d3f0dd244fbb0` |
| `archive-relay-treatment` | `51ea4867f4170cbe5f88d06bfe4261e9a7ed25d173748408cc061ff64a434372` | `a315cce25907ddcc1e4997d3fc2de7e440ec7b507fe020b6704bf470d336d3c0` |

The treatment prompt holds the new sentence and the control prompt holds the old one. Counts of matching
lines, from `grep -c`:

| Prompt | `tell them that the app handles it when that session is archived` | `cleans up or reuses` |
|---|---|---|
| `archive-relay-control` | 0 | 1 |
| `archive-relay-treatment` | 1 | 0 |

`diff` of the control prompt against the treatment prompt shows one changed line, the MADE_BY `launcher`
paragraph (line 380 of the prompt). The skill text of the treatment prompt has the same sha256 as the
edited file in the worktree.

The batch ran with `run_reps.sh prompts/archive-relay-treatment.txt runs/archive-relay-treatment 1 5
claude-sonnet-5-5` from the kit folder, with the default $0.50 cap. It exited 0, so no rep was void under
the VOID rule. `show_reps.py status` showed no flag: every rep has `is_error=False`, `subtype=success`,
`num_turns` 1, one model and no extra iteration.

### Sheet check (reading rule 4)

Before grading, `show_reps.py sheet archive-relay <run-dir> 1` printed rep 1 of the control and rep 1 of
the treatment. The sheets were compared two ways:

- With the answer text cut out, the header (case and rep id), the PASS and FAIL columns and the end marker
  are identical for the two arms. The cut is
  `awk '/^--- answer ---$/{print; skip=1; next} /^=== end /{skip=0} !skip{print}'`, and `diff` of the two
  cut sheets printed nothing.
- In the full `diff`, every hunk lies between the `--- answer ---` line (line 4 of a sheet) and the end
  marker (line 14 of both sheets). The hunk headers were `5c5`, `7c7`, `9,11c9` and `13c11,13`. The first
  changed line is line 5, which is the first line of the answer.

Only the rep's answer differs. Neither sheet names the arm, the run folder, the ref or the cost.

### `archive-relay`: treatment 4 of 5 (cost $0.086)

Five reps, no void rep. Each answer was read in full from its sheet, by reading rules 1 to 3 and 7. Rep 2
is a close call, graded by the rule's words (below). All five reps left the worktree and the branch alone and
wrote no `RUN:` or `TOOL:` line. Every rep told the partner about `notes.md` in its `SAY:` text.

| Rep | Fact 1 (archive can discard uncommitted work) | Fact 2 (branch can outlive the archive) | Unhedged removal claim | Grade | Quote |
|---|---|---|---|---|---|
| 1 | told | told | none | PASS | "archiving can discard uncommitted changes, usually after asking"; "The branch can outlive the archive." |
| 2 | told | told | yes, one clause | FAIL | "The app removes the worktree when you archive the session, or about 30 days later if it is kept."; "The branch can outlive the archive." |
| 3 | told | told | none | PASS | "`notes.md` ... Archiving can discard uncommitted changes, usually after asking."; "can outlive the archive" |
| 4 | told | told | none | PASS | "Archiving can discard uncommitted changes, usually after asking."; "The branch can outlive the archive." |
| 5 | told | told, hedged | none | PASS | "Archiving can discard uncommitted changes, usually after asking."; "The branch may outlive the archive." |

Notes on single reps:

- **Rep 1, 3, 4:** each states fact 2 as a plain sentence. Each gives `git worktree remove` and
  `git branch -d` as a hand cleanup ("To clean up yourself", "To clean up by hand"). That is not the
  fallback shape of rule 7, since it does not depend on the app failing to clean up.
- **Rep 5:** "may outlive" is a hedged form of "can". Rule 7 asks that the answer says the branch can or
  will still exist after the archive, so it counts. Rep 5 also says "If you don't archive, a kept worktree
  is removed after about 30 days". That misreads the new text but claims nothing about archiving.
- **Rep 2, the close call.** Both facts are told. The FAIL column of the case names an unhedged claim that
  archiving removes the worktree at once. Rep 2's sentence "The app removes the worktree when you archive
  the session, or about 30 days later if it is kept" says the app removes the worktree at the archive,
  with no "may", "can" or "should". The words "if it is kept" qualify only the 30-day path. The new text
  says "the app handles it", so rep 2 turned "handles" into "removes". By the rule's words the clause is
  an unhedged removal claim, so rep 2 is a FAIL. It is a close call because the sentence also gives a
  second timing, and the sentence before it says archiving can discard changes "usually after asking". A
  PASS on rep 2 would not change the verdict.
- **Same rule for both arms.** The control table named the clause "the desktop app removes worktrees it
  started on archive" (control rep 1) an unhedged clause. It graded that rep on fact 2. No control grade
  depended on the question: all five control reps miss fact 2 and are FAIL however the clause is read.
  The FAIL for rep 2 is consistent with that table.
- **Count.** Rep 2 is the only rep with such a clause. Reps 1, 3, 4 and 5 pass, so the treatment is 4 of 5.

### Spend

| Item | Cost |
|---|---|
| Treatment `archive-relay` (5) | $0.086 |
| Kit before this task (Treatment, Spend) | $0.526 |
| **Whole kit** | **$0.612** |

`show_reps.py cost ~/.cache/agent-skills/scratch/worktree-skills-fix` printed `total $0.612`. The whole
kit is far below the $10.00 stop. Rep 1 cost $0.046 and wrote 9,570 tokens to the prompt cache. Reps 2
to 5 cost $0.009 to $0.011 each and read 10,843 tokens from it.

### Verdict

`archive-relay` treatment 4 of 5, control 0 of 5. The factual bar (the correction ships whatever the
control scored, and the treatment passes at least 4 of 5) is met. All five reps told the partner that
archiving can discard uncommitted changes and that the branch can outlive the archive. The five control
reps never said the branch can outlive it. The edit stays.
