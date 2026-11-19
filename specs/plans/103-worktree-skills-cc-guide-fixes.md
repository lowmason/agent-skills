# Worktree Skills Guide Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the two claims in finishing-a-development-branch and using-git-worktrees that contradict the Claude Code guide, cite both files, and apply the result of the option b live check to `rules/pr-lifecycle.md`.

**Architecture:** Five tasks, each the only task that edits its files. Task 1 builds a micro-test kit and runs the control arms. Tasks 2 and 3 each fix one claim and run its treatment arm. Task 4 writes the NOTICE bullet and runs `baseline cite`. Task 5 reads the option b live check that the planning session ran on its own cleanup, and changes the rule only on a pass.

**Tech Stack:** Markdown skill and rule text, the `claude -p` micro-test kit, `build/cc_guide/cli.py`, pytest through `build/run_suites.py`.

**Spec:** none. The requirement is three open items in `specs/deferred_items.md`, named by their opening words:
- "Rule on the held `/cc-guide files` reviews of the two worktree skills, then cite them", with its owner ruling of 2026-11-17: fix `skills/finishing-a-development-branch/SKILL.md` line 379 (what archiving a desktop session does) and `skills/using-git-worktrees/SKILL.md` line 74 (the native tool branches from local HEAD when there is no remote). No action on the two line-76 judgment calls or the not-covered rows. Then run `baseline cite` on both files. Tasks 1–4.
- "Free a desktop-app worktree's branch before the archive". Task 5.
- "Void a no-tools rep that took a peer message (next-kit fix)". Task 1's kit closes it.

## Global Constraints

- **Anchors.** Line numbers were taken at `7233aa3`. The old text in each step is the match key. Task 1 Step 1 checks for drift.
- **One owner per file.** A task edits only its listed files. Task 1 creates the record, and Tasks 2 and 3 each append their case's section to it. `NOTICE` and `build/cc_guide/baseline.json` change only in Task 4. `rules/pr-lifecycle.md` and `README.md` change only in Task 5.
- **Machinery stream.** finishing-a-development-branch is execution machinery. Execution starts only when no other plan execution runs in this repository (owner ruling, 2026-11-17). Plans 101 and 102 were executing when this plan was written.
- **Self-modifying run.** The executor finishes through finishing-a-development-branch, and `~/.claude/skills` links to the main checkout. Execute from a worktree, so the live skill keeps main's text until the merge. Call controller scripts through `~/.claude/skills/<skill>/scripts/`.
- **Compaction window.** A SKILL.md body stays at most 20,000 characters, measured at execution with `check_conformance.skill_body(text)[0]` (`build/check_conformance.py`). At `7233aa3` finishing-a-development-branch's body is 19,392.
- **Adapted skills.** Both skills are adapted superpowers skills, so their fixes get one NOTICE bullet (Task 4). New text names no other skill's path, file or section, so `install.py`'s `DEPENDENCIES` does not change.
- **Commit gate.** Before each commit, `bash build/run_commit_lints.sh` prints `commit lints passed`. Messages follow Conventional Commits, use plain technical English and end with the attribution trailer that the executing session is given. State test counts as deltas.
- **Micro-tests (Tasks 1–3).** The kit lives at `specs/baseline/red-baseline-worktree-skills-fix/kit/`, the record at `specs/baseline/red-baseline-worktree-skills-fix.md`. Start from plan 97's committed kit, `specs/baseline/red-baseline-change-reverted-mutant/review-kit/`: copy `run_reps.sh`, `probe.sh`, `isolation_probe.txt`, `kit_identity.py` and `check_scrub.py`. Each rep is a fresh `claude -p --model claude-sonnet-5-5 --tools "" --strict-mcp-config --setting-sources ""` under `env -i`, with `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`, a $0.50 cap, and its own new, empty folder outside every repository. Five scored reps per arm. The control arm reads the text at the execution base (Task 1 Step 1). Build a treatment arm from `git stash create`. Never run `git stash push` or `git stash pop`. Stop and ask the owner at $10 for the whole kit, or at $3 for the control arms.
- **Next-kit fixes.** The kit drops `origin` and `credential_expires_at` from every rep's JSON. It voids a rep whose JSON has `result_index` above 0 or an `origin` that is not null, checked before the drop, and runs a replacement rep. Nobody messages or subscribes to a running rep. If a rep gets its own `HOME`, set `syncClaudeAiSkills` false there. The reps have no tools, so the `Read(~/**)` gap of tool kits does not arise. Grade by hand, every answer, against the case's PASS and FAIL columns. A grading sheet names the rep id and the case, never the arm. Before grading a treatment arm, diff one of its sheets against a control sheet of the same case: only the rep's answer may differ.
- **Public repository.** The plan, kit, record and commits name no private repository and carry no packet or report text. Packets stay in `~/.cache/agent-skills/cc-guide/`.
- **Leave alone.** The rows that the 2026-11-17 ruling left without action, the "reuses" claim of line 379 among them. The line-76 sentences of using-git-worktrees. The branches of plans 101 and 102. `specs/findings/mutant-cost-benefit.md`.

## Review Focus

1. **A repository with a remote but no `origin/HEAD`.** An agent reads line 74's new no-remote fact as leave to call `EnterWorktree` by name, and the worktree misses HEAD's unpushed commits. Expected: Step 1b's commands, then `EnterWorktree` with `path`. Pinned in Task 1's case `remote-nohead`, run in Task 2 Step 4.
2. **A repository with no remote.** An agent leaves the F1 route because the native tool would now keep the commits. Expected: the same route as item 1. Pinned in case `noremote`, Task 2 Step 4.
3. **A partner archives a launcher worktree that holds uncommitted work.** Expected: the partner hears that archiving can discard it, and that the branch can outlive the archive. Pinned in case `archive-relay`, Task 3 Step 4.
4. **A later session runs option b on a squash-merged branch.** Expected: the rule checks the branch against the merged PR's `headRefOid`, never ancestry against `origin/<default>`. Pinned in Task 5 Step 3a.
5. **The rule gains option b although the live check failed, did not run, or the archive has not happened.** Expected: `rules/pr-lifecycle.md` and `README.md` stay as they are. Pinned in Task 5 Step 1 and Step 2b.

## Decisions

- **D1** (owner, brief, 2026-11-19): the planning session's own cleanup, after this plan's PR merges, is the live check of option b. `rules/pr-lifecycle.md` step 3 runs as written, except in case 3 (a worktree the desktop app made). There the session asks the owner first (Gate A). On a yes it checks its branch against the merged PR's `headRefOid`, runs `git switch --detach` in its worktree, then `git branch -D <branch>`, and records what it ran and saw in the execution handoff brief. Applied in: the section "The option b record" below.
- **D2** (owner, brief, 2026-11-19): the plan's last task reads that record and checks the archive. If the planning session is not archived yet, it stops and asks, and records no failure. On a pass it rewrites step 3 case 3 and the `README.md` rules row for option b, and closes the option b item. On a failure, or if option b did not run, it adds a `→ progress` note to that item and leaves step 3 as it is. Applied in: Task 5.
- **D3** (owner, brief, 2026-11-19): on a pass, only the rule changes. The skill's local-merge and discard flows keep the branch under MADE_BY `launcher` (`skills/finishing-a-development-branch/SKILL.md` lines 343, 379 and 390), since they are not the post-PR cleanup. The option b item's closing note says so. No extra micro-test. Applied in: Task 5 Step 4a.
- **D4** (owner, plan review, 2026-11-19): approve every default in "Open for plan review", items 1–7, as proposed. Applied in: Global Constraints (Micro-tests, Next-kit fixes), Tasks 1–5.

## Open for plan review

Resolved at plan review on 2026-11-19: the owner approved each default as proposed (D4). Each item carries the default this plan uses.

1. **Line 379's archive wording** (brief Q1). Default: rewrite only the archive claim, in the line's own voice ("Tell your partner …"). Use the facts of `rules/pr-lifecycle.md` lines 47–50, add that the branch can outlive the archive, keep "reuse", and drop "(step 4)". The exact text is in Task 3 Step 2.
2. **Step 6's single `launcher` case** (brief Q2). Default: do not split it into "the desktop app made it" and "another launcher made it". Line 379 already says "Anywhere else, your partner can run `git worktree remove`".
3. **What counts as a pass** (brief Q3). Default: all four conditions in Task 5 Step 1. After the archive, a missing `worktreePath` is expected. One change from the brief: its "`git worktree list` marks nothing `prunable`" becomes "the recorded folder's entry is not `prunable`". This repository has several worktrees, and a stale one would fail the check for a reason that has nothing to do with option b.
4. **A partial failure** (brief Q4). Default: if `git switch --detach` succeeds and `git branch -D` fails, the planning session stops and reports both outputs. It leaves the worktree detached and runs no other form of either command. Task 5 reads that as a failure.
5. **Which fixes get a micro-test.** The item asks for writing-skills' micro-test on each fix. Default: three cases. Two non-regression cases cover line 74 (`noremote`, `remote-nohead`), since its new fact could pull an agent off the F1 route. One factual case covers line 379 (`archive-relay`), and it ships whatever the control scores (plan 60's D6). Cheaper: line 74's two cases only, by plan 76's D1 rule (test only a fix that can change what an agent chooses).
6. **Line 74 keeps the F1 route for a repository with no remote.** Default: yes. The failed check prints the same error with no remote and with a remote that lacks `origin/HEAD`. In the second case the probe saw unpushed commits left out (`specs/guides/claude-code-customization-guide.md` line 262). The new text says so.
7. **The kit closes the next-kit item.** Default: yes. The item's done-when is the next kit built after 2026-11-18, with a self-test that covers the void and the drop. Task 1 builds that self-test.

## The option b record

The planning session writes this into the execution handoff brief, under the heading `Option b live check`. It is not a task. Task 5 reads it.

- **Ran:** the planning session's id, its branch, its worktree path and its PR number. Each command (`gh pr view <n> --json headRefOid`, `git rev-list --count <headRefOid>..<branch>`, `git switch --detach`, `git branch -D <branch>`) with its exit status and full output. `git worktree list` before and after.
- **Did not run:** the reason. `get_session` with `self` showed no `worktreePath`, the owner said no at Gate A, or the count was above 0.

---

### Task 1: Micro-test kit and control arms

**Files:**
- Create: `specs/baseline/red-baseline-worktree-skills-fix.md` (record: cases, bars, predictions, control results)
- Create: `specs/baseline/red-baseline-worktree-skills-fix/kit/` (the plan 97 files named in Global Constraints, plus `postprocess.py`, `test_postprocess.py` and `build_prompts.py`)
- Create: `kit/prompts/<case>-control.txt` and `kit/runs/<case>-control/` (the scrubbed rep JSONs), for each case
- Modify: `build/suites.toml` (register suite `worktree-skills-fix-kit`, dir the kit, `with = ['pytest']`)

**Interfaces:**
- Produces: `postprocess(raw: dict) -> dict` in `kit/postprocess.py`. It returns `{'void': True, 'reason': 'result_index' | 'origin'}` for a void rep, else the rep with `'void': False`, without `origin` and `credential_expires_at`, and with `kit_identity`'s scrub applied to its text. `run_reps.sh` calls it on each raw JSON.
- Produces: `build_prompts.py <case> <arm> <ref>` writes the prompt file for one case and arm. The full SKILL.md text at `<ref>` comes first, then the case's fixture.
- Produces: the record's sections `Cases`, `Control`, and a `Treatment: <case>` section that Tasks 2 and 3 append.

- [ ] **Step 1: Check the anchors and record the base**

Run from the worktree root, on the execution branch before any edit. Record `git rev-parse HEAD` as BASE in the record.

```bash
git grep -c 'whether pushed or not, and the native tool leaves them out' -- skills/using-git-worktrees/SKILL.md
git grep -c 'The desktop app cleans up or reuses a worktree it started when that session is archived.' -- skills/finishing-a-development-branch/SKILL.md
git grep -c 'handles the worktree when the session is archived (step 4)' -- rules/pr-lifecycle.md
git grep -c "It leaves a desktop-app worktree and its branch for the app's archive, and reports them." -- README.md
```

Expected: each prints `<path>:1`. A miss means the text moved: stop and report.

- [ ] **Step 2: Write the failing self-test**

`kit/test_postprocess.py`, three tests on synthetic dicts:
- `test_a_peer_turn_voids_the_rep`: `result_index` 1 and `origin` None. Expect `void` True, `reason` `'result_index'`.
- `test_an_origin_voids_the_rep`: `result_index` 0 and `origin` `{'kind': 'peer'}`. Expect `void` True, `reason` `'origin'`.
- `test_a_clean_rep_is_kept_without_origin_or_credential_expiry`: `result_index` 0, `origin` None, `credential_expires_at` set, `result` `'ok'`. Expect `void` False, neither key present, `result` `'ok'`.

Run: `uv run python build/run_suites.py worktree-skills-fix-kit`. Expected: FAIL, `postprocess` not found.

- [ ] **Step 3: Implement `postprocess` and wire it into `run_reps.sh`**

- [ ] **Step 4: Run the self-test and the scrub check**

Run: `uv run python build/run_suites.py worktree-skills-fix-kit`, then `uv run python specs/baseline/red-baseline-worktree-skills-fix/kit/check_scrub.py`. Expected: `suite runs passed` (+3 tests), and `PASS`.

- [ ] **Step 5: Write the cases into the record, then commit before any rep runs**

Each rep's prompt asks it to list, in order, each command (`RUN:`), each tool call (`TOOL:` name and arguments) and each thing it says to its partner (`SAY:`), and to stop where it would wait for the partner. A rep has no tools, so the fixture states the output of every command the skill has it run before the scored call. Build that output from a real scratch repository, outside every repository, and paste it in.

| Case | Skill | Fixture | PASS | FAIL | Bar |
|---|---|---|---|---|---|
| `noremote` | using-git-worktrees | A normal checkout at `/work/atlas`, three local commits on `main`. The partner said yes to a worktree on branch `feat/rate-limit`, and declared no worktree directory. `EnterWorktree` is available. The base check printed git's `unknown revision` error, and `git remote` prints nothing. `ls -d .worktrees` prints `.worktrees`, and `git check-ignore -q .worktrees/` exits 0. | `git worktree add` on a new branch from HEAD, then `EnterWorktree` with `path` | `EnterWorktree` with `name`, and no `git worktree add` | non-regression |
| `remote-nohead` | using-git-worktrees | As `noremote`, but `git remote -v` lists `origin`, `git fetch origin` failed, and the cached `origin/main` is two commits behind HEAD. | as `noremote` | as `noremote` | non-regression |
| `archive-relay` | finishing-a-development-branch | Step 2 recorded MADE_BY `launcher` and MAIN_GIT `allowed`. The desktop app started the session in the worktree. Option 1's merge and tests passed in MAIN_ROOT. The worktree holds an untracked `notes.md` (`git status --porcelain` there prints `?? notes.md`). The run is at Step 6, and the partner says they will archive this session next. | tells the partner that archiving can discard uncommitted changes in the worktree, and that the branch can outlive the archive | says that archiving removes the worktree at once or deletes the branch, or leaves out either fact | factual |

Grading rules:
- Where an answer branches with IF lines, grade the branch that matches the stated facts.
- An answer with neither the PASS call nor the FAIL call, such as one that stops to ask first, counts as a FAIL in both arms.

Bars:
- **Non-regression:** the treatment passes at least the control's count minus one. A miss stops the task for an owner ruling.
- **Factual:** the correction ships whatever the control scores. The treatment passes at least 4 of 5. Below that, run one wording round with the facts unchanged, then ask the owner.

Predictions: the controls pass `noremote` and `remote-nohead` and fail `archive-relay`.

```bash
git add build/suites.toml specs/baseline/red-baseline-worktree-skills-fix.md specs/baseline/red-baseline-worktree-skills-fix/
git commit -m "test(baseline): add the worktree skills fix kit and its cases"
```

- [ ] **Step 6: Pilot**

Run `probe.sh` with `isolation_probe.txt` on the installed binary, then one control rep per case. Read each rep in full. Expected: the probe's lines 1 to 6 read NO, and each rep answers in the `RUN:`/`TOOL:`/`SAY:` form. Line 7, the user's identity, may read YES. That is the open item "Account identity reaches the isolated micro-test runs", and it does not block: no case depends on who the user is, and the identity scrub runs on every rep (plan 97's controller ruling, 2026-11-13). Any other YES stops the task.

- [ ] **Step 7: Run the control arms**

Five scored reps per case at BASE. Record each score and the cost in the record's `Control` section.

- [ ] **Step 8: Commit**

```bash
git add specs/baseline/red-baseline-worktree-skills-fix.md specs/baseline/red-baseline-worktree-skills-fix/
git commit -m "test(baseline): record the worktree skills fix control arms"
```

### Task 2: using-git-worktrees — the no-remote fact at Step 1a

**Files:**
- Modify: `skills/using-git-worktrees/SKILL.md:74`
- Modify: `specs/baseline/red-baseline-worktree-skills-fix.md` (append `Treatment: noremote, remote-nohead`)
- Create: `kit/prompts/<case>-treatment.txt` and `kit/runs/<case>-treatment/`, for both cases

**Interfaces:**
- Consumes: Task 1's kit, cases `noremote` and `remote-nohead`, and their control scores.

- [ ] **Step 1: Run the failing check**

Run: `git grep -c 'With no remote, it branches from HEAD' -- skills/using-git-worktrees/SKILL.md`
Expected: exit 1, no match.

- [ ] **Step 2: Replace the claim**

Old (match key): `HEAD may have commits that the default branch lacks, whether pushed or not, and the native tool leaves them out. Create the worktree`

New: ``HEAD may have commits that the default branch lacks, whether pushed or not. With a remote, the native tool can leave them out, even when `origin/HEAD` is unset. With no remote, it branches from HEAD, but a failed check looks the same in both cases. Create the worktree``

- [ ] **Step 3: Run the check again**

Run the Step 1 command, then `git grep -c 'and the native tool leaves them out' -- skills/using-git-worktrees/SKILL.md`.
Expected: `skills/using-git-worktrees/SKILL.md:1`, then exit 1.

- [ ] **Step 4: Run the treatment arms**

Five scored reps each for `noremote` and `remote-nohead`, with the edited text from `git stash create`. Apply the non-regression bar. Append the scores, the cost and the verdict to the record.

- [ ] **Step 5: Commit**

```bash
git add skills/using-git-worktrees/SKILL.md specs/baseline/red-baseline-worktree-skills-fix.md
git commit -m "fix(using-git-worktrees): say the native tool keeps HEAD with no remote"
```

### Task 3: finishing-a-development-branch — what archiving does, at Step 6

**Files:**
- Modify: `skills/finishing-a-development-branch/SKILL.md:379`
- Modify: `specs/baseline/red-baseline-worktree-skills-fix.md` (append `Treatment: archive-relay`)
- Create: `kit/prompts/archive-relay-treatment.txt` and `kit/runs/archive-relay-treatment/`

**Interfaces:**
- Consumes: Task 1's kit, case `archive-relay`, and its control score.

- [ ] **Step 1: Run the failing check**

Run: `git grep -c 'a kept worktree is removed about 30 days later' -- skills/finishing-a-development-branch/SKILL.md`
Expected: exit 1, no match.

- [ ] **Step 2: Replace the claim**

Old (match key): `Tell your partner where the worktree is and what removes it. The desktop app cleans up or reuses a worktree it started when that session is archived.`

New: `Tell your partner where the worktree is and what removes it. If the desktop app started it, tell them that the app handles it when that session is archived, and may reuse it. Archiving can discard uncommitted changes in it, usually after asking, and a kept worktree is removed about 30 days later. The branch can outlive the archive.`

- [ ] **Step 3: Run the check again, and measure the body**

Run the Step 1 command, then `git grep -c 'cleans up or reuses' -- skills/finishing-a-development-branch/SKILL.md`, then, from `build/`:

```bash
uv run --with pyyaml python -c "import check_conformance as c; print(len(c.skill_body(open('../skills/finishing-a-development-branch/SKILL.md').read())[0]))"
```

Expected: `skills/finishing-a-development-branch/SKILL.md:1`, then exit 1, then a number of at most 20,000.

- [ ] **Step 4: Run the treatment arm**

Five scored reps for `archive-relay`, from `git stash create`. Apply the factual bar. Append the scores, the cost and the verdict to the record.

- [ ] **Step 5: Commit**

```bash
git add skills/finishing-a-development-branch/SKILL.md specs/baseline/red-baseline-worktree-skills-fix.md
git commit -m "fix(finishing-a-development-branch): say what archiving a desktop session does"
```

### Task 4: NOTICE bullet and citation stamps

**Files:**
- Modify: `NOTICE` (a new bullet after the one that starts "finishing-a-development-branch's and using-git-worktrees' SKILL.md files gained one `# cc-guide: subagents.worktrees` YAML comment")
- Modify: `skills/finishing-a-development-branch/SKILL.md:15`, `skills/using-git-worktrees/SKILL.md:13` (the `# cc-guide:` stamps, written by `baseline cite` only)
- Modify: `build/cc_guide/baseline.json` (written by `baseline cite` only)

**Interfaces:**
- Consumes: the final bytes of Tasks 2 and 3.

- [ ] **Step 1: Run the failing check**

Run: `uv run python build/cc_guide/cli.py lint 2>&1 | /usr/bin/grep -cE 'STALE skills/(finishing-a-development-branch|using-git-worktrees)/'`
Expected: `2`.

- [ ] **Step 2: Add the NOTICE bullet**

```text
  - finishing-a-development-branch's Step 6 and using-git-worktrees' Step 1a
    were corrected against this repo's Claude Code guide (plan 103, after
    the 2026-11-17 /cc-guide files review). Step 6 now says what archiving
    a desktop app session does: it can discard uncommitted changes in the
    worktree, usually after asking, a kept worktree is removed about 30
    days later, and the branch can outlive the archive. Step 1a no longer
    says that the native tool leaves HEAD's commits out when there is no
    remote, since it then branches from HEAD. A failed base check still
    goes to Step 1b's git commands.
```

- [ ] **Step 3: Stamp both files**

Run: `uv run python build/cc_guide/cli.py baseline cite skills/finishing-a-development-branch/SKILL.md skills/using-git-worktrees/SKILL.md`
Expected: one `stamped <path> @<release>` line per file. Plan 102 changes `build/cc_guide/` before this runs, so read the output. If cite refuses, stop and report it.

- [ ] **Step 4: Run the check again**

Run the Step 1 command. Expected: `0`. The `subagent-driven-development` STALE line is out of scope and stays.

- [ ] **Step 5: Commit**

```bash
git add NOTICE build/cc_guide/baseline.json skills/finishing-a-development-branch/SKILL.md skills/using-git-worktrees/SKILL.md
git commit -m "chore(cc-guide): cite the two worktree skills after their fixes"
```

### Task 5: Apply the option b live check

**Files:**
- Modify: `rules/pr-lifecycle.md:44-50` (step 3, the desktop-app case), on a pass only
- Modify: `README.md:219` (the `pr-lifecycle.md` row), on a pass only
- Modify: `specs/deferred_items.md` (the item "Free a desktop-app worktree's branch before the archive")

**Interfaces:**
- Consumes: the execution handoff brief's `Option b live check` section ("The option b record" above).

- [ ] **Step 1: Get the verdict (controller, before dispatch)**

A subagent has no `get_session`, so the controller runs this step and puts the verdict and the record into the task brief.
- The record says option b did not run: the verdict is `did not run`, with its reason.
- Otherwise, run `get_session` on the recorded session id. If `isArchived` is not true, stop and ask the owner whether to archive it now or wait. Record no failure.
- Otherwise, the verdict is `pass` only if all four hold, else `fail`, naming each condition that failed:
  1. The record shows both option b commands with exit status 0.
  2. `get_session` shows `isArchived` true.
  3. In `git worktree list --porcelain`, the recorded folder's entry has no `prunable` line, and the folder is gone, detached, or on a branch other than the recorded one (another session took it). Other entries do not count.
  4. `git branch --list <branch>` prints nothing.

- [ ] **Step 2a (pass): Run the failing check**

Run: `git grep -c 'git switch --detach' -- rules/pr-lifecycle.md README.md`
Expected: exit 1, no match.

- [ ] **Step 3a (pass): Replace the case and the row**

In `rules/pr-lifecycle.md`, replace the case that starts `- **A worktree the desktop app made**` and ends `which can outlive the archive.` with:

```markdown
   - **A worktree the desktop app made** (`get_session` with `self` shows a `worktreePath`):
     switch the main checkout to the default branch, fast-forward it, and prune. Do not remove the
     worktree: removing the session's own worktree moves the session onto the main checkout. Free
     its branch instead. Run `gh pr view <n> --json headRefOid`, then
     `git rev-list --count <headRefOid>..<branch>`, after `git fetch origin pull/<n>/head` if that
     commit is missing here. If it prints 0, run `git switch --detach` in the worktree, then
     `git branch -D <branch>`. If it prints more, or either command fails, stop and report the
     output, and run no other form of either command. The app handles the worktree when the
     session is archived (step 4). Archiving can discard uncommitted changes in it, usually after
     asking, and a kept worktree is removed about 30 days later. Report the worktree's path, and
     the branch if it is still there.
```

In `README.md`, replace `It leaves a desktop-app worktree and its branch for the app's archive, and reports them.` with `In a desktop-app worktree, it detaches the worktree and deletes the branch once the merged PR holds all its commits, and leaves the worktree for the app's archive.`

Run the Step 2a command, then `git grep -c 'detaches the worktree' -- README.md`, then `git grep -cF 'git rev-list --count <headRefOid>..<branch>' -- rules/pr-lifecycle.md`.
Expected: `rules/pr-lifecycle.md:1`, then `README.md:1`, then `rules/pr-lifecycle.md:1`.

- [ ] **Step 4a (pass): Close the item**

Tick the item's box, and add this note under it, 6 spaces in:

```text
      → done <YYYY-MM-DD> (plan 103 Task 5): the planning session's live check passed, and step 3 and the `README.md` rules row describe option b. finishing-a-development-branch's local-merge and discard flows (Options 1 and 4 under MADE_BY `launcher`) still keep the branch, since they are not the post-PR cleanup.
```

- [ ] **Step 2b (fail or did not run): Record the result**

Add this note under the item, and leave its box open:

```text
      → progress <YYYY-MM-DD> (plan 103 Task 5): <the option b live check failed: each failed condition | option b did not run: the reason>. Step 3 of `rules/pr-lifecycle.md` stays as it is.
```

Run: `git diff --quiet HEAD -- rules/pr-lifecycle.md README.md`. Expected: exit 0.

- [ ] **Step 5: Commit**

```bash
git add specs/deferred_items.md rules/pr-lifecycle.md README.md
git commit -m "docs(rules): apply the option b live check to the pr-lifecycle cleanup"
```

On the fail branch, the message is `docs(specs): record the option b live check result`.
