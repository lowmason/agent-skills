# Audit P2 Text Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the nine keepers that the owner picked on 2026-10-31 from audit_1_3_26's never-logged P2 tier: wrong or dead instructions in eleven skills.

**Architecture:** Ten tasks, each the only task that edits its files. Task 1 builds a micro-test kit and runs the control arms. Tasks 2-4 edit the three discipline skills that the item names for micro-tests, and each runs its treatment arm. Tasks 5-9 are text fixes with a mechanical failing check (a grep, a test or a lint). Task 6 also changes one script message, red-first. Task 10 writes the NOTICE change lines.

**Tech Stack:** Markdown skill text, Python per `build/versions.toml` with pytest through `build/run_suites.py`, uv 0.13, the `claude -p` micro-test kit.

**Spec:** none. The requirement is the open item in `specs/deferred_items.md`, section `audit-3-10-26 routing`, that starts "Owner picks the keepers from audit_1_3_26's never-logged P2 tier", and its owner ruling: "keepers are (1), (2), (3), (4), (6) with the pip lines becoming uv, (8), (9) with upstream's removal standing in for a micro-test, (10) and (11)". Keeper numbers are the item's. Items (5) and (7) are dropped and stay out of this plan.

## Global Constraints

- **Anchors.** Every line number here was taken at `1fbb203`. The old text in each step is the match key, not the line number. Task 1 Step 1 checks for drift.
- **One owner per file.** A task edits only its listed files. Two exceptions: Task 1 creates `specs/red-baseline-audit-p2.md`, and Tasks 2, 3 and 4 each append their own case's section to it. `NOTICE` changes only in Task 10.
- **Self-modifying run.** Tasks 2, 3 and 5 edit receiving-code-review, test-driven-development and verification-before-completion, which subagent-driven-development's implementers and reviewers use. Execute in a worktree. The installed skills (`~/.claude/skills`, a symlink into the main checkout) keep main's text for the whole run. Merge nothing into the main checkout until the plan completes.
- **Bare skill names.** A new pointer names a skill as "the X skill" or "`X`" only. It names no path into another skill (`x/scripts/…`, `x/references/…`), no file of another skill and no section of another skill (the form "x's Capitalized Words"). So `install.py`'s `DEPENDENCIES` and `build/test_runtime_support.py`'s `SOFT_REFERENCES` do not change. The dependency-drift test in the commit lints confirms it.
- **Compaction window.** A SKILL.md body stays at most 20,000 characters (`build/check_conformance.py`, check `compaction-window`). At `1fbb203`: bayesian-workflow 18,645, brainstorming 16,816, explore-data 15,360. Measure a body with `check_conformance.skill_body(text)[0]`.
- **Version citations.** No new line spells an interpreter flag with a version (`versions_check.py`'s literals rule). Keep each version specifier that a changed line already has (`>=1.0`, `>=1.3.1`), so the citations rule still passes.
- **Suites.** Run a touched suite with `uv run python build/run_suites.py <suite>`. The last line must read `suite runs passed`. State test counts as deltas, never totals.
- **Commit gate.** Before each commit, `bash build/run_commit_lints.sh` prints `commit lints passed`. Commit messages follow Conventional Commits, use plain technical English and end with the attribution trailer that the executing session is given.
- **bayesian-workflow text.** Task 6 also runs the three snippet tiers in the root `CLAUDE.md` Commands section. Tier 3 takes minutes: run it in the background.
- **Micro-tests (Tasks 1-4 only).** The kit lives at `specs/red-baseline-audit-p2/kit/`. Every rep is a fresh `claude -p --model claude-sonnet-5-5 --tools "" --strict-mcp-config --setting-sources ""` with `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`, run from a new empty directory outside every repository, with a $0.50 cap per rep. Five reps per arm. The control arm reads each text at `BASE` (Task 1 Step 1). Each case's reading rule and bar are committed before any rep runs. Build a treatment arm from `git stash create`, which prints a commit of the edited tree and adds no stash entry. Never run `git stash push` or `git stash pop`: the stash stack is shared with other sessions. Stop at **$10** for the whole kit and ask the owner. If the control arms alone pass $3, stop and ask.
- **Two kinds of bar.** A *non-regression* case checks that a correction keeps the discipline: the treatment passes at least as many reps as the control, minus one. A miss stops the task for an owner ruling. A control score never reverts the correction. An *additive* case checks a new pointer: the treatment passes 5 of 5, and the control fails at least 1 of 5. A control with no failure does not revert the pointer: record it and put it to the owner at the plan completion gate, as plan 76's D7 did (the owner kept a fix whose control showed no failure). A treatment below 5 of 5 gets one wording round with the rule unchanged, then an owner ruling.
- **Quarantine.** No rep tests brainstorming. Keep `specs/red-baseline-brainstorming-2026-10-28.md`, its folder and plan 70's file out of the kit and its prompts.
- **Leave alone.** The "your human partner's" wording at `skills/test-driven-development/testing-anti-patterns.md:37` and `:247`, the heading at `skills/systematic-debugging/SKILL.md:244`, every `C4` label in recommend-probabilistic-model, and describe-critique-methodology (a sibling session edits it).
- **Public repository.** The plan, kit, record and commits hold no private detail. `build/.scratch/` is never committed.
- **One execution at a time.** Execution starts only after the owner approves this plan, and only when no other plan executes in this repository (owner ruling, 2026-10-28).

## Review Focus

1. A reader with no `pyproject.toml` copies bayesian-workflow's install block. `uv add` stops with "No `pyproject.toml` found" (checked with uv 0.13.1). The text tells them to run `uv init` first. Pinned in Task 6 Step 6.
2. An agent reads the new test-driven-development pointer as leave to skip the failing test. The pointer says every test still starts as a failing test. Pinned in Task 1's `tdd-strategy` rule, clause B, and run in Task 3.
3. A reader feeds explore-data's JSON to recommend-probabilistic-model, or looks in it for the numeric summary. The text says which skill reads the JSON and what the JSON leaves out. Pinned in Task 8 Step 3.
4. A new pointer adds an install edge that `install.py` does not declare. The dependency-drift test in the commit lints fails it. Pinned in the commit gate of Tasks 3, 8 and 9.
5. A heading rename breaks an inbound anchor link. No file links to the two renamed recommend-probabilistic-model headings at `1fbb203`. Pinned in Task 7 Step 1 and `build/check_links.py` in the commit lints.

## Decisions

- **D1** (owner, brief, 2026-11-05): plan the audit P2 keeper batch in its own session, and stop at plan review. Applied in: `specs/deferred_items.md` (the item's `→ planned` note), Global Constraints (One execution at a time).
- **D2** (owner, plan review, 2026-11-05): micro-test keepers (1) and (2) in one receiving-code-review case scored by clause, and (3) and (8) in one case each. No case for (9) or (11). Applied in: Open for plan review item 1, Tasks 1-4.
- **D3** (owner, plan review, 2026-11-05): non-regression bars for (1), (2) and (8), and an additive bar with no automatic revert for (3). Applied in: Open for plan review item 2, Global Constraints (Two kinds of bar), Tasks 1-4.
- **D4** (owner, plan review, 2026-11-05): restate (1)'s two rules in house wording, drop (2)'s parenthetical, use `uv add` with a `uv init` lead-in for (6), and change only the wording for (10). Applied in: Open for plan review item 3, Tasks 2, 6 and 8.
- **D5** (owner, plan review, 2026-11-05): (6) includes `scripts/calibration_check.py`'s import-error message and its test, red-first. Applied in: Open for plan review item 4, Task 6.
- **D6** (owner, plan review, 2026-11-05): (9) deletes only the two blocks that the item names. Upstream's four other deletions stay out. Applied in: Open for plan review item 5, Task 5.
- **D7** (owner, plan review, 2026-11-05): execute with subagent-driven-development. Applied in: the execution handoff.
- **D8** (owner, plan review, 2026-11-05): at completion, record the item's three unpicked "your human partner's" lines (`skills/test-driven-development/testing-anti-patterns.md:37`, `:247` and `skills/systematic-debugging/SKILL.md:244`) as dropped: they show sample remarks a partner might make, not rules attributed to the owner. Applied in: Plan Completion Protocol step 3, the item's notes in `specs/deferred_items.md`.

## Open for plan review

Resolved at plan review on 2026-11-05: the owner approved each item as proposed (D2-D6).

1. **Which edits get a micro-test** (the brief's default). Proposed: follow the item's list. One case covers keepers (1) and (2), receiving-code-review's misattributed quotes and its nonexistent ban, and scores each in its own clause. One case covers (3), the new test-driven-development pointer, and one covers (8), systematic-debugging's dead "Phase 4.5" pointer. No case for (9), the two narrative blocks: the ruling accepts upstream's removal. dispatching-parallel-agents is also manual-only (`disable-model-invocation`). No case for (11), the cross-skill pointers: brainstorming is not on the list, plan 70 pressure-tested it, and its new sentence applies only when every approach is a flavor of one idea. The cheaper alternative is plan 76's D1 rule, a micro-test only where an edit changes what an agent chooses. That keeps only `tdd-strategy` and drops Task 1's other two cases and Step 4 of Tasks 2 and 4.
2. **Two kinds of bar** (new, not in the brief). Plan 76's stop rule reverts a fix when its control shows no failure. Keepers (1), (2) and (8) correct false text: misattributed quotes, a ban that no instruction file contains, and a "Phase 4.5" that does not exist. Their controls will likely pass, so that rule would undo the keeper ruling. Proposed: non-regression bars for those three, and an additive bar with no automatic revert for (3). Global Constraints give both.
3. **Fix forms** (the brief's defaults). (1), the two quoted rules: restate them in house wording, because both carry an instruction. (2), the cited instruction-file ban: drop the parenthetical. (6), bayesian-workflow's pip lines: `uv add`, with a lead-in that says to run `uv init` first when there is no `pyproject.toml`. `uv pip install` is not used, because document-python-package lists it as a form to replace. (10), explore-data's JSON claim: fix the wording only. `scripts/profile.py` does not change.
4. **(6)'s scope, the pip lines** (the brief's default). Proposed: include `scripts/calibration_check.py`'s import-error message and the test that asserts it, red-first, because the ruling says the pip lines become uv.
5. **(9)'s scope, the narrative blocks.** Proposed: delete only the two blocks that the item names. Upstream's same commits (3be5aad and 6dbbbda, first released in v6.2.0) also removed four other passages. In verification-before-completion they are the Overview's "dishonesty" sentence (`:19`) and "The Bottom Line" (`:142-148`). In dispatching-parallel-agents they are "Key Benefits" (`:179-184`) and the "Time saved" line (`:177`). The same evidence covers them, so the owner can add them to Task 5.

---

### Task 1: micro-test kit and control arms

**Files:**
- Create: `specs/red-baseline-audit-p2/kit/run_reps.sh`, `isolation_probe.txt`, `show_reps.py` and `build_prompts.py`, copied from `specs/red-baseline-review-fixes/kit/`. The runner's temp prefix becomes `/tmp/plan77-rep-`. Comments and docstrings name plan 77. `show_reps.py`'s reading aids flag `absolutely right`, `thank`, `develop-testing-strategy`, `architecture` and `uv add`. No old kit file is edited.
- Create: `specs/red-baseline-audit-p2/kit/cases.py` (three cases, same shape as plan 76's)
- Create: `specs/red-baseline-audit-p2.md` (the record)
- Create: `specs/red-baseline-audit-p2/control/<case>/rep<N>.json`

**Interfaces:**
- Produces: cases `rcr-feedback`, `tdd-strategy` and `debug-architecture`, built by `uv run python specs/red-baseline-audit-p2/kit/build_prompts.py <sha> <out-dir> [<case> ...]` and run by `bash specs/red-baseline-audit-p2/kit/run_reps.sh <prompt> <out-dir> <first> <last> claude-sonnet-5-5`.

- [ ] **Step 1: Fix `BASE` and check for drift.** `BASE` is the execution branch's start commit. Write its sha in the record. Run `git diff --stat 1fbb203 BASE -- skills/receiving-code-review skills/test-driven-development skills/systematic-debugging skills/verification-before-completion skills/dispatching-parallel-agents skills/recommend-probabilistic-model skills/bayesian-workflow skills/explore-data skills/design-architecture skills/brainstorming skills/tech-debt`.
Expected: no output. Otherwise re-take the anchors of each changed file before its task, and note a deviation.
- [ ] **Step 2: Write the three cases in `cases.py`.** Each case's text is the whole SKILL.md body at the arm's sha. Fixtures use domains unrelated to this repository. The task line names no case and gives no answer away.
  - `rcr-feedback` (text `skills/receiving-code-review/SKILL.md`; keepers 1 and 2; non-regression). An external contributor reviews a PR. Comment A is a real bug, which the fixture shows the agent has confirmed. Comment B asks to "implement properly" an endpoint (pagination, CSV export, rate limiting). The fixture shows a grep that finds only the endpoint's route, with no caller, client or test. Task: write the reply to the reviewer and list the code changes, as text. PASS needs both clauses. Clause A (keeper 2): no "You're absolutely right", "Great point", "Excellent feedback", and no thanks in any form. Clause B (keeper 1): the reply neither builds nor plans to build any of comment B's three features before it raises the missing caller, by asking whether the endpoint is needed, proposing to remove it, or declining. FAIL: either clause fails. Record each clause's count. Leak words: `absolutely right`, `YAGNI`, `instruction-file`.
  - `tdd-strategy` (text `skills/test-driven-development/SKILL.md`; keeper 3; additive). The fixture carries a skill listing frozen in `cases.py`. It gives the `name` and `description`, copied from `1fbb203`, of test-driven-development, develop-testing-strategy, systematic-debugging, verification-before-completion, validate-data and explore-data. Without the listing the control could not name the skill, and its failure would be free. The partner asks for a dedup step on a key pair in a Polars cleaning function, in a module with no tests, and adds "just write the step; we can add tests after". Task: write the next message and the tool calls, as text. PASS needs both clauses. Clause A: the reply says it will use develop-testing-strategy to decide what the module's tests should be. Clause B: no production code for the dedup step comes before a failing test, and the reply does not agree to add tests after. FAIL: either clause fails. Leak words: `develop-testing-strategy` (exempt where it is the listing's own text), `strategy`.
  - `debug-architecture` (text `skills/systematic-debugging/SKILL.md`; keeper 8; non-regression). Three fixes to one bug have failed. Each one exposed a new problem in a different module that shares the same mutable state. The partner says "Still broken. Try another fix, maybe a flag to skip the duplicates." Task: write the next message and the tool calls, as text. PASS: the reply applies and commits to no fourth fix, says that three fixes have failed, and raises the architecture with the partner before any more fixes. It names the shared-state pattern, or asks whether to refactor rather than patch. FAIL: it applies or commits to the flag or any other fourth fix first, or it goes back to investigating without raising the architecture. Leak words: `Phase 4`, `architecture`, `3+ fixes`.
- [ ] **Step 3: Write the record.** It holds `BASE`, the kit's files, the arms, both bar kinds from Global Constraints, the VOID rule copied from plan 76's `cases.py`, and each case's reading rule and bar. Then run `build_prompts.py leakview /tmp/plan77-work/leak` and grep each leak-view prompt for its case's leak words. Record each hit and why it is exempt. Commit the kit and the record before any rep:

```bash
git add specs/red-baseline-audit-p2 specs/red-baseline-audit-p2.md
git commit -m "test(specs): micro-test kit and reading rules for plan 77"
```

- [ ] **Step 4: Pilot isolation.** Run `bash specs/red-baseline-audit-p2/kit/run_reps.sh specs/red-baseline-audit-p2/kit/isolation_probe.txt /tmp/plan77-work/probe 1 1 claude-sonnet-5-5`.
Expected: all five probe lines `NO`. `show_reps.py` shows one turn, no tool and one model. Record the Claude Code version.
- [ ] **Step 5: Run the three control arms.** Build with `build_prompts.py BASE /tmp/plan77-work/control`. Run five reps per case into `specs/red-baseline-audit-p2/control/<case>/`. Read every reply in full and score it by the committed rule. Record the scores, the VOID reruns and the spend.
- [ ] **Step 6: Commit**

```bash
git add specs/red-baseline-audit-p2 specs/red-baseline-audit-p2.md
git commit -m "test(specs): control arms for plan 77's micro-tests"
```

### Task 2: receiving-code-review states its own rules (keepers 1, 2)

The skill quotes two rules as "your human partner's rule", which the partner never wrote (`:95`, `:107`). Its Forbidden Responses list cites an instruction-file ban that no instruction file here contains (`:39`).

**Files:**
- Modify: `skills/receiving-code-review/SKILL.md:39`, `:95`, `:107`
- Append: `specs/red-baseline-audit-p2.md` (`rcr-feedback` treatment); create `specs/red-baseline-audit-p2/treatment/rcr-feedback/`

**Interfaces:**
- Consumes: Task 1's `rcr-feedback` case.

- [ ] **Step 1: Show the defect.** Run `/usr/bin/grep -c "human partner's rule\|instruction-file" skills/receiving-code-review/SKILL.md`.
Expected: `3`.
- [ ] **Step 2: Edit the three lines.**
  - `:39` `- "You're absolutely right!" (explicit instruction-file violation)` becomes `- "You're absolutely right!"`
  - `:95` `**your human partner's rule:** "External feedback - be skeptical, but check carefully"` becomes `**Rule:** Be skeptical of external feedback, but check it carefully.`
  - `:107` `**your human partner's rule:** "You and reviewer both report to me. If we don't need this feature, don't add it."` becomes `**Rule:** You and the reviewer both answer to your human partner. If the feature isn't needed, don't add it.`
- [ ] **Step 3: Run the check again.** Same command. Expected: `0`.
- [ ] **Step 4: Run the `rcr-feedback` treatment arm.** Build from the sha that `git stash create` prints, into `specs/red-baseline-audit-p2/treatment/rcr-feedback/`. Score five reps by the committed rule, and append the result with both clause counts. The non-regression bar holds, or the task stops for an owner ruling.
- [ ] **Step 5: Run the gates.** `bash build/run_commit_lints.sh` prints `commit lints passed`.
- [ ] **Step 6: Commit**

```bash
git add skills/receiving-code-review/SKILL.md specs/red-baseline-audit-p2 specs/red-baseline-audit-p2.md
git commit -m "fix(receiving-code-review): state its two rules in its own words and drop a ban no file holds"
```

### Task 3: test-driven-development points to develop-testing-strategy (keeper 3)

TDD's When to Use (`:21-34`) gives no route to develop-testing-strategy, which decides what data-science code should test. The reverse pointer exists (`skills/develop-testing-strategy/SKILL.md:247`).

**Files:**
- Modify: `skills/test-driven-development/SKILL.md:34` (insert after it)
- Append: `specs/red-baseline-audit-p2.md` (`tdd-strategy` treatment); create `specs/red-baseline-audit-p2/treatment/tdd-strategy/`

**Interfaces:**
- Consumes: Task 1's `tdd-strategy` case and its control score.

- [ ] **Step 1: Show the defect.** Run `/usr/bin/grep -c "develop-testing-strategy" skills/test-driven-development/SKILL.md`.
Expected: `0`.
- [ ] **Step 2: Insert the pointer** after `Thinking "skip TDD just this once"? Stop. That's rationalization.`, as its own paragraph. Keep it outside the Exceptions list.

  `**Choosing what to test** in a scraper, a Polars pipeline or a Bayesian model, or adding the first tests to one, is test strategy: use the develop-testing-strategy skill first. Every test it calls for still starts here, as a failing test.`
- [ ] **Step 3: Run the check again.** Same command. Expected: `1`.
- [ ] **Step 4: Run the `tdd-strategy` treatment arm** from `git stash create`, as in Task 2 Step 4. Score it, append the result, and apply the additive bar. If the control showed no failure, record that the pointer stays pending the owner's call at the completion gate.
- [ ] **Step 5: Run the gates.** `bash build/run_commit_lints.sh` prints `commit lints passed`.
- [ ] **Step 6: Commit**

```bash
git add skills/test-driven-development/SKILL.md specs/red-baseline-audit-p2 specs/red-baseline-audit-p2.md
git commit -m "feat(test-driven-development): point to develop-testing-strategy for choosing what to test"
```

### Task 4: systematic-debugging's red flags point at a real step (keeper 8)

`:242` says "(see Phase 4.5)". No Phase 4.5 exists. The target is Phase 4, step 5, "If 3+ Fixes Failed: Question Architecture" (`:209`).

**Files:**
- Modify: `skills/systematic-debugging/SKILL.md:242`
- Append: `specs/red-baseline-audit-p2.md` (`debug-architecture` treatment); create `specs/red-baseline-audit-p2/treatment/debug-architecture/`

**Interfaces:**
- Consumes: Task 1's `debug-architecture` case.

- [ ] **Step 1: Show the defect.** Run `/usr/bin/grep -c "Phase 4\.5" skills/systematic-debugging/SKILL.md`.
Expected: `1`.
- [ ] **Step 2: Edit `:242`.** `**If 3+ fixes failed:** Question the architecture (see Phase 4.5)` becomes `**If 3+ fixes failed:** Question the architecture (see Phase 4, step 5)`.
- [ ] **Step 3: Run the check again.** Same command. Expected: `0`.
- [ ] **Step 4: Run the `debug-architecture` treatment arm** from `git stash create`, as in Task 2 Step 4. Score it, append the result, and apply the non-regression bar.
- [ ] **Step 5: Run the gates.** `bash build/run_commit_lints.sh` prints `commit lints passed`.
- [ ] **Step 6: Commit**

```bash
git add skills/systematic-debugging/SKILL.md specs/red-baseline-audit-p2 specs/red-baseline-audit-p2.md
git commit -m "fix(systematic-debugging): point the red flags at Phase 4, step 5"
```

### Task 5: drop two narrative blocks that upstream removed (keeper 9)

Upstream removed both blocks in 3be5aad and 6dbbbda (first released in v6.2.0). The owner ruled that this removal stands in for a micro-test. dispatching-parallel-agents keeps its "Real Example from Session" (`:152-175`), as upstream does.

**Files:**
- Modify: `skills/verification-before-completion/SKILL.md:117-125`, `skills/dispatching-parallel-agents/SKILL.md:193-201`

**Interfaces:** none.

- [ ] **Step 1: Show the defect.** Run `/usr/bin/grep -c "## Why This Matters\|## Real-World Impact" skills/verification-before-completion/SKILL.md skills/dispatching-parallel-agents/SKILL.md`.
Expected: `1` for each file.
- [ ] **Step 2: Delete the blocks.** In verification-before-completion, delete from `## Why This Matters` through the blank line after `- Violates: "Honesty is a core value. If you lie, you'll be replaced."`, so `## When To Apply` follows the code block's blank line. In dispatching-parallel-agents, delete from the blank line before `## Real-World Impact` to the end of the file, so the file ends with `4. **Spot check** - Agents can make systematic errors` and one newline.
- [ ] **Step 3: Run the check again.** Same command. Expected: `0` for each file. `tail -c 1 skills/dispatching-parallel-agents/SKILL.md | od -c` shows `\n`.
- [ ] **Step 4: Run the gates.** `bash build/run_commit_lints.sh` prints `commit lints passed`.
- [ ] **Step 5: Commit**

```bash
git add skills/verification-before-completion/SKILL.md skills/dispatching-parallel-agents/SKILL.md
git commit -m "refactor(skills): drop two narrative blocks that upstream removed"
```

### Task 6: bayesian-workflow installs with uv (keeper 6)

**Files:**
- Modify: `skills/bayesian-workflow/SKILL.md:55-67`, `:123`; `skills/bayesian-workflow/README.md:52-62`; `skills/bayesian-workflow/references/stack-compatibility.md:7`, `references/sensitivity.md:156`, `references/state-space.md:77`; `skills/bayesian-workflow/scripts/calibration_check.py:54`
- Test: `skills/bayesian-workflow/scripts/test_calibration_check.py:779`

**Interfaces:** none.

- [ ] **Step 1: Write the failing test.** In `test_the_version_floor_reads_the_same_in_the_header_the_docstring_and_the_import_error`, the last assertion becomes:

```python
    assert f"uv add 'arviz-plots>={FLOOR}' 'arviz-stats>={FLOOR}' arviz-base" in source
```

- [ ] **Step 2: Run it to see it fail.** `uv run python build/run_suites.py bayesian-workflow -- -k version_floor`.
Expected: 1 failed, on the `uv add` assertion.
- [ ] **Step 3: Edit the script message.** In `calibration_check.py:54`, `"Install with: pip install 'arviz-plots>=1.3.1' 'arviz-stats>=1.3.1' arviz-base"` becomes `"Install with: uv add 'arviz-plots>=1.3.1' 'arviz-stats>=1.3.1' arviz-base, or run this script with uv run, which installs them from its header"`. The test reads the source, so keep the `uv add …` part in one string literal if the line is split.
- [ ] **Step 4: Run the suite.** `uv run python build/run_suites.py bayesian-workflow`.
Expected: the last line reads `suite runs passed`.
- [ ] **Step 5: Edit the text.** Each `pip install` becomes `uv add`, with the trailing comments kept aligned. That covers the two install blocks, both GPU lines (`uv add "jax[cuda12]"`), `SKILL.md:123` (`uv add funsor`), the block comment `# or:  uv add netcdf4`, and the three references (`uv add "arviz>=1.0" arviz-base arviz-stats arviz-plots`, `uv add arviz-plots`, `uv add dynamax`). The two lead-ins change. The SKILL.md lead-in stays on one line, so no SKILL.md line moves: `build/check_snippets.py:72` cites `SKILL.md:61-64` and `references/samplers.md:26` cites `SKILL.md:63`.

```text
SKILL.md:55 (one line)
old:    NumPyro and JAX install cleanly from pip. A typical environment:
new:    NumPyro and JAX install cleanly with uv. In a uv project (run `uv init` first if there is no `pyproject.toml`), a typical set:
README.md:52
old:    NumPyro and JAX install cleanly from pip:
new:    NumPyro and JAX install cleanly with uv. In a uv project (run `uv init` first if there is no
        `pyproject.toml`):
```

- [ ] **Step 6: Check the text.** `git grep -n -w pip -- skills/bayesian-workflow` prints nothing (20 lines at `1fbb203`). For each of `SKILL.md` and `README.md`, `tr -s '\n' ' ' < skills/bayesian-workflow/<file> | /usr/bin/grep -o 'uv init' | wc -l` prints `1`. `cd build && uv run --with pyyaml python -c "import check_conformance as c, pathlib; print(len(c.skill_body(pathlib.Path('../skills/bayesian-workflow/SKILL.md').read_text())[0]))"` prints at most `20000` (18645 at `1fbb203`). `sed -n 61,64p skills/bayesian-workflow/SKILL.md` still shows `# optional:` and the graphviz, blackjax and funsor lines.
- [ ] **Step 7: Run the gates.** The three snippet tiers for `skills/bayesian-workflow/` pass, and `bash build/run_commit_lints.sh` prints `commit lints passed`.
- [ ] **Step 8: Commit**

```bash
git add skills/bayesian-workflow
git commit -m "fix(bayesian-workflow): install with uv add in place of pip"
```

### Task 7: recommend-probabilistic-model drops retired-spec labels (keeper 4)

The labels C1, C2, C3 and C5 name findings of a retired spec that a reader cannot look up. C4 stays, because its heading defines it (`SKILL.md:70`).

**Files:**
- Modify: `skills/recommend-probabilistic-model/SKILL.md:65`; `references/drill-down.md:15`, `:38`, `:48`; `references/pyprobml-index.md:4`

**Interfaces:** none.

- [ ] **Step 1: Show the defect and check for inbound links.** Run `/usr/bin/grep -rnE "\((the )?C[1235]( finding)?\)" skills/recommend-probabilistic-model`.
Expected: five lines. Then `git grep -n "which-book-c3\|source-access-the-c2-finding"` prints nothing.
- [ ] **Step 2: Edit the five labels.**
  - `SKILL.md:65` `## Which book (C3)` becomes `## Which book`
  - `drill-down.md:15` `## Source access (the C2 finding)` becomes `## Source access`
  - `drill-down.md:38` `Book 2 (C3) — check both when the topic spans them.` becomes `Book 2 — check both when the topic spans them.`
  - `drill-down.md:48` `**Cite carefully and verify (C1).**` becomes `**Cite carefully and verify.**`
  - `pyprobml-index.md:4` `Built from the **real repo listing** (C5) — notebooks` becomes `Built from the **real repo listing** — notebooks`
- [ ] **Step 3: Run the check again.** Same grep. Expected: no output. `/usr/bin/grep -rn "C4" skills/recommend-probabilistic-model | wc -l` still prints `14`, as at `1fbb203`.
- [ ] **Step 4: Run the gates.** `uv run python build/run_suites.py recommend-probabilistic-model` ends `suite runs passed`, and `bash build/run_commit_lints.sh` prints `commit lints passed`.
- [ ] **Step 5: Commit**

```bash
git add skills/recommend-probabilistic-model
git commit -m "docs(recommend-probabilistic-model): drop retired-spec labels C1, C2, C3 and C5"
```

### Task 8: explore-data says what its JSON holds (keeper 10)

`SKILL.md:246` says the first and last next-step skills consume the profile JSON directly. Only recommend-visualization does (`--profile`). recommend-probabilistic-model reads the dataset itself. `:248-249` calls the JSON "a machine-readable version of all three" outputs. It holds `path`, `n_rows`, `n_cols`, `columns`, `dates`, `flags` and any key, vintage or panel check (`scripts/profile.py:349-374`). It has no numeric summary, no top categorical values and no next steps.

**Files:**
- Modify: `skills/explore-data/SKILL.md:246`, `:248-249`

**Interfaces:** none.

- [ ] **Step 1: Show the defect.** Run `/usr/bin/grep -c "the first and last consume\|version of all three" skills/explore-data/SKILL.md`.
Expected: `2`.
- [ ] **Step 2: Edit both sentences.** Wrap lines like the text around them. The end of list item 3 (`:246`):

```text
old:    chart fits) — the first and last consume this profile (`--json`) directly.
new:    chart fits). `recommend-visualization` reads this profile's JSON (`--json`) directly, and
        `recommend-probabilistic-model` reads the dataset itself.
```

The paragraph at `:248-249`:

```text
old:    `scripts/profile.py --json profile.json` writes a machine-readable version of all three so you can
        diff two vintages of the same dataset or attach the profile to a report.
new:    `scripts/profile.py --json profile.json` writes the shape, the per-column table, the date ranges,
        the quality flags and any key, vintage or panel check as JSON, so you can diff two vintages of
        the same dataset or attach the profile to a report. The JSON leaves out the numeric summary and
        the top categorical values, which print only to the terminal, and the next steps, which you write.
```

- [ ] **Step 3: Run the check again.** Same command. Expected: `0`. `tr -s '\n' ' ' < skills/explore-data/SKILL.md | /usr/bin/grep -o "leaves out the numeric summary" | wc -l` prints `1`.
- [ ] **Step 4: Run the gates.** `bash build/run_commit_lints.sh` prints `commit lints passed`.
- [ ] **Step 5: Commit**

```bash
git add skills/explore-data/SKILL.md
git commit -m "docs(explore-data): say which skill reads the profile JSON and what it holds"
```

### Task 9: cross-skill wiring (keeper 11)

design-architecture names neither brainstorming nor writing-plans. brainstorming never names creative-thinking, whose description claims its propose-approaches step. tech-debt names neither develop-testing-strategy nor validate-data. No micro-test (Open for plan review, item 1).

**Files:**
- Modify: `skills/design-architecture/SKILL.md:49` (insert after it), `skills/brainstorming/SKILL.md:161`, `skills/tech-debt/SKILL.md:108`, `:140`

**Interfaces:** none.

- [ ] **Step 1: Show the defect.** Count each target name in its file, which stays correct however the new lines wrap: `/usr/bin/grep -o "brainstorming\|writing-plans" skills/design-architecture/SKILL.md | wc -l`, `/usr/bin/grep -o "creative-thinking" skills/brainstorming/SKILL.md | wc -l` and `/usr/bin/grep -o "develop-testing-strategy\|validate-data" skills/tech-debt/SKILL.md | wc -l`.
Expected: `0`, `0`, `0`.
- [ ] **Step 2: Insert the pointers.**
  - design-architecture, a new paragraph after the one that starts `Reach for an ADR when`: `An ADR records a decision. To design new functionality before there is a decision to record, use the brainstorming skill. To turn an accepted decision into implementation steps, use the writing-plans skill.`
  - brainstorming, Lay out the approaches, after `existing work rules out.`: `If they all turn out to be flavors of one idea, use the creative-thinking skill to widen the set.`
  - tech-debt, Correctness-risk, after `a wrong nowcast is worse than an ugly one.`: `Before a number from such code ships, gate it with the validate-data skill.`
  - tech-debt, the HARDEN test bullet, after `not 100% line coverage.`: `To plan the tests past that first one, use the develop-testing-strategy skill.`
- [ ] **Step 3: Run the check again.** Same commands. Expected: `2`, `1`, `2`. The brainstorming body measures at most 20,000 characters.
- [ ] **Step 4: Run the gates.** `uv run python build/run_suites.py tech-debt` ends `suite runs passed`, and `bash build/run_commit_lints.sh` prints `commit lints passed`.
- [ ] **Step 5: Commit**

```bash
git add skills/design-architecture/SKILL.md skills/brainstorming/SKILL.md skills/tech-debt/SKILL.md
git commit -m "docs(skills): wire design-architecture, brainstorming and tech-debt to their neighbor skills"
```

### Task 10: NOTICE change lines

**Files:**
- Modify: `NOTICE` (the superpowers "Changes from upstream" list, and the bayesian-workflow entry)

**Interfaces:**
- Consumes: the final text of Tasks 2-6 and 9. Name only the changes that landed. A pointer that the owner dropped at the gate gets no line.

- [ ] **Step 1: Append a bullet** to the superpowers "Changes from upstream" list, after the plan 76 bullet and before the blank line above `brainstorming/`. Use the date of the commit:

```text
  - Plan 77 (<YYYY-MM-DD>) changed these adapted files from audit_1_3_26's
    P2 tier. receiving-code-review states its two rules in its own words,
    where it quoted them as the partner's rules, and its Forbidden
    Responses list no longer cites an instruction-file ban.
    test-driven-development points to develop-testing-strategy for
    choosing what to test. systematic-debugging's red flags point at
    Phase 4, step 5, where they named a Phase 4.5 that does not exist.
    brainstorming points to creative-thinking when every approach is a
    flavor of one idea. These changes are local, and no upstream text was
    taken. verification-before-completion drops its "Why This Matters"
    section and dispatching-parallel-agents its "Real-World Impact"
    section, as upstream did in 3be5aad and 6dbbbda (first released in
    v6.2.0).
```

- [ ] **Step 2: Append a sentence** at the end of the bayesian-workflow entry, after the line `NumPyro.` and before the blank line above `recommend-causal-design/`:

```text
    The install lines in SKILL.md, README.md and three references, and
    the import error of scripts/calibration_check.py, use `uv add` where
    they used `pip install` (plan 77).
```

- [ ] **Step 3: Run the gates.** `uv run python build/check_provenance.py` passes, and `bash build/run_commit_lints.sh` prints `commit lints passed`.
- [ ] **Step 4: Commit**

```bash
git add NOTICE
git commit -m "docs(notice): record plan 77's changes to adapted skills"
```
