# Superpowers Drift Follow-ups Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close three superpowers-drift backlog items: a merge-conflict stop in finishing-a-development-branch (finding 28), a plan-run rule for subagent reviewers in receiving-code-review (finding 27), and two test traps in test-driven-development (finding 3).

**Architecture:** Three wording changes to vendored superpowers skills, each micro-tested against its text at BASE. finishing-a-development-branch first moves Step 4b's carry-findings block to `references/`, which frees about 950 characters, then gains the conflict rule. One micro-test kit, copied from plan 82's, holds five cases. NOTICE gets one entry.

**Tech Stack:** Markdown skill text; the micro-test kit (Python 3.13, bash, `claude -p`); the repo's lints.

**Spec:** none. This is `/deferred` step 5's **Plan** disposition (2026-11-10): the three deferred items below are the requirements. Background: `specs/findings/superpowers-drift-v7-0-2.md` findings 3, 27 and 28, and `specs/plans/completed/82-helper-hardening-and-test-command.md` (the kit and the bars this plan copies).

## Requirements

From `specs/deferred_items.md`, trimmed to what decides the work (`[…]` marks a cut):

- Section `superpowers-drift-v7.0.2 (no plan; drift-spec reconciliation, branch claude/superpowers-drift-spec-status-7bad03) — 2026-11-10`:
  > **finishing-a-development-branch has no path for a merge conflict (superpowers drift finding 28, the conflict half).** Option 1 runs `git checkout <base-branch>`, `git pull` and `git merge <feature-branch>` […] and says nothing about a conflict. […] The proposed rule: stop, show the conflict, and ask. Never resolve a merge conflict on your own initiative. On 2026-11-10 the body has 25 characters of room under the `compaction-window` check […], so text must move to `references/` before the rule fits. […] Size: plan. Done when: every step that runs `git merge` carries the rule, `build/check_conformance.py` passes, and a `NOTICE` line names it.

  > **receiving-code-review does not say which rule wins for a subagent reviewer inside a plan run (superpowers drift finding 27).** […] Its stop for a conflict with the partner's prior decisions ("Stop and discuss with your human partner first", […] about lines 91-92) is a stall inside a run whose fix loop rules on each finding instead. […] The proposed fix is one sentence: inside a plan run, a subagent reviewer's finding is ruled on under the executor's rules, and this skill's stop applies outside a run. It is a wording change to a discipline skill, so it needs a micro-test against a no-guidance control […], and a line in `NOTICE`'s superpowers change list. […] This item does not cover [the `gh api` reply] line. […] Size: plan. Done when: the sentence is in the skill, its micro-test meets its bar against the control, and a `NOTICE` line names it.

- Section `superpowers-drift-v7.0.2 earlier findings (no plan; findings 3 and 8 filed from the drift spec, branch claude/superpowers-drift-spec-impl-5923ed) — 2026-11-10`:
  > **test-driven-development's `testing-anti-patterns.md` does not name the string-presence and change-detector traps (superpowers drift finding 3).** […] A string-presence test asserts on the words of a script, skill or prompt instead of on what it does. A change-detector test fails when the implementation changes but protects no useful outcome. […] Keep the whole Why Order Matters section […]. Either way it changes a discipline skill, so it follows the writing-skills skill, with a micro-test against a no-guidance control. The skill is vendored from superpowers, so add a line to `NOTICE`'s superpowers change list. […] Done when: the owner's choice is recorded on this item, the skill names both traps, the micro-test meets its bar against the control, the Why Order Matters section is whole, and a `NOTICE` line names what was taken.
  > → progress 2026-11-10 (owner ruling): Two traps — add both traps to testing-anti-patterns.md, worded so a lint that guards a text contract is not a trap. Goes in the theme plan with a micro-test.

## Owner review (defaults this plan settles; change any at plan review)

- **O1. Where the room comes from.** Default: move Step 4b's whole carry-findings block (from `**If you left any finding or Declined to judge line unfixed,**` through `Record only the findings your partner carries.`, 1,357 characters) to a new `references/carry-review-findings.md`, verbatim except its one path. Step 4b keeps a three-line pointer. With the conflict rule, the body measures 19,009 characters, 991 under the window. The step before the block already shows the partner every unfixed finding, so the partner still sees them. Alternative: also move Step 1b's two example outputs.
- **O2. The conflict rule's reach.** Default: it covers `git pull` as well as `git merge`, since both can stop on a conflict, and only Option 1 runs either. It gets an additive micro-test case, though the item names none: writing-skills asks one for behavior-shaping wording, and the owner waived it only for finding 26.
- **O3. The TDD pointer.** Default: the pointer in test-driven-development's "Testing Anti-Patterns" section fires "When writing or changing tests", not only "When adding mocks or test utilities", and lists the two traps. Otherwise an agent testing a script never loads the reference. The reference's own load line already says "writing or changing tests". The Iron Laws stay as they are.
- **O4. What the micro-tests show.** Default: each prompt carries the texts an agent would have loaded, whole (see each case's `texts`). The cases test the wording, not whether an agent opens a reference from its pointer. The record says so as a known limit.

## Global Constraints

- **Anchors.** Line numbers are as of `b0c2673`. The old text in each step is the match key, not the line number. Task 1 Step 1 checks for drift.
- **BASE.** BASE is the commit the execution branch starts from, before Task 1 changes anything. Task 1 writes its sha in the record, and every control arm reads its texts at BASE.
- **Files.** A task edits only its listed files. `NOTICE` changes only in Task 5.
- **Self-modifying run.** Tasks 2–4 edit skills that the executors use while they run (finishing-a-development-branch at the end, receiving-code-review in the final review, test-driven-development in every fix). Execute in a worktree. The controller uses the installed skills under `~/.claude/skills/`, which point at the main checkout and keep main's text for the whole run. Merge nothing into the main checkout until the plan completes.
- **Order.** This plan executes after plan 85 and after plan 87 (owner, D1), one execution at a time.
- **Compaction window.** After Task 2, the finishing-a-development-branch body is at most 19,100 characters. Measure it with `uv run --directory build --with pyyaml python -c "import check_conformance as c, pathlib; print(len(c.skill_body(pathlib.Path('../skills/finishing-a-development-branch/SKILL.md').read_text())[0]))"`. If plan 87 added a `compaction-window` exception for this file, Task 2 removes it, and `build/check_conformance.py` passes without it.
- **Dependencies.** The moved block names `../writing-plans/references/deferred-backlog.md`. In the reference file it becomes the link `[deferred-backlog.md](../../writing-plans/references/deferred-backlog.md)`, the form `skills/executing-plans/references/final-review.md` uses. The skill's edge to writing-plans already exists (Step 1b). `install.py`'s `DEPENDENCIES` and `SOFT_REFERENCES` do not change. Name other skills by bare name only.
- **Upstream text.** Read upstream's `skills/test-driven-development/writing-good-tests.md` at `22f0b46` only to confirm the two traps' ideas: `gh api "repos/obra/superpowers/contents/skills/test-driven-development/writing-good-tests.md?ref=22f0b46" --jq .content | base64 -d`. Take no upstream wording. The plan's text is this repository's own.
- **Micro-tests.** The kit lives at `specs/baseline/red-baseline-drift-followups/kit/`, the record at `specs/baseline/red-baseline-drift-followups.md`. Every rep is a fresh `claude -p --model claude-sonnet-5-5 --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence --output-format json` under `env -i`, with `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`, from a new empty directory outside every repository, at $0.50 a rep at most. Five reps per arm. Each case's reading rule and bar are committed before any rep runs. Build a treatment arm from the sha that `git stash create` prints. Never run `git stash push` or `git stash pop`. Stop at **$10** for the whole kit and ask the owner. If the control arms alone pass $4, stop and ask.
- **Two kinds of bar.** A *non-regression* case checks that a change keeps a behavior. Its treatment passes at least 4 of 5, and at least as many reps as the control, minus one. A miss stops the task for an owner ruling. An *additive* case checks new guidance. Its treatment passes 5 of 5, and the control fails at least 1 of 5. A control with no failure does not revert the change: record it, and put it to the owner at the plan completion gate. A treatment below 5 of 5 gets one wording round with the reading rule unchanged, then an owner ruling.
- **Exact copy.** The skill text in Tasks 2–4 is exact copy. A wording round changes it only as the record states, with the round's new text.
- **Suites and gates.** Before each commit, `bash build/run_commit_lints.sh` prints `commit lints passed`. Commit messages follow Conventional Commits, use plain technical English and end with the executing session's attribution trailer, written below as `<the session's trailer>`.
- **Shell.** The Bash tool runs zsh. Quote any `===` in an echo. Use `/usr/bin/grep` for sweeps. Scratch files go under `~/.cache/agent-skills/scratch/plan88-work/`.
- **Public repository.** The plan, kit, record and commits hold no private detail.
- **Completion.** This plan implements no spec, so protocol step 5 retires the plan alone. `specs/findings/superpowers-drift-v7-0-2.md` stays live. Before the retire commit, record what landed there, found by heading or row: rows 3, 27 and 28 of "Status of earlier findings" say what plan 88 adopted, with its date; findings 3, 27 and 28 each get a closing line `**Done** (plan 88, <YYYY-MM-DD>): <what landed>.`; and the "Suggested disposition" bullets "Earlier work still open" (finding 3) and "Local design proposals" (findings 27 and 28) get `Done: plan 88 (<YYYY-MM-DD>).` A change the owner drops at the gate leaves its finding open.

## Review Focus

1. The carry-findings text must still be reached: Step 4b names the reference at the point the partner carries a finding, and the moved text keeps the `## <name> Step 4b review — <YYYY-MM-DD>` heading form that `deferred_stats.py` dates. Task 2 Step 4 checks both.
2. A check whose subject is text (identical copies, a required header) must not be called a trap: the `text-contract` case (Task 4).
3. The reference's link into writing-plans must resolve from one directory deeper: `build/check_links.py` in Task 2 Step 4.
4. The new Python examples in `testing-anti-patterns.md` must parse: snippet Tier 1 in Task 4 Step 4.
5. Inside a run, a finding that needs one of the five stops (a destructive operation, for example) must still stop: the finding-27 text keeps "unless one of its five stops applies", which Task 3 Step 3 checks.

## Decisions

- **D1** (owner, /deferred selection, 2026-11-10): one theme plan for findings 28, 27 and 3, written beside plan 87. Plan 87 executes first. Applied in: Global Constraints (Order).
- **D2** (owner, /deferred ruling, 2026-11-10): finding 3's scope is "Two traps — add both traps to testing-anti-patterns.md, worded so a lint that guards a text contract is not a trap. Goes in the theme plan with a micro-test." Applied in: Task 4.

## Related open items (taken into account, not absorbed)

- Finding 8's discard menu was closed on 2026-11-10 by the owner's "Keep both". Option 4 and both menus stay as they are.
- Plan 87 (`specs/plans/87-compaction-cut-probe.md`) may correct the `compaction-window` window and add an exception for this file. See Global Constraints (Compaction window).
- receiving-code-review's forge-specific `gh api` reply line (finding 27's other half) stays out of scope, as the item says.

## File map

- Create `specs/baseline/red-baseline-drift-followups/kit/` (five files) and `specs/baseline/red-baseline-drift-followups.md` (Task 1), the control reps (Task 1) and the treatment reps (Tasks 2–4).
- Modify `skills/finishing-a-development-branch/SKILL.md` and create `skills/finishing-a-development-branch/references/carry-review-findings.md` (Task 2). Modify `build/cc_guide/conformance.toml` only to remove a plan-87 exception for this file (Task 2).
- Modify `skills/receiving-code-review/SKILL.md` (Task 3).
- Modify `skills/test-driven-development/testing-anti-patterns.md` and `skills/test-driven-development/SKILL.md` (Task 4).
- Modify `NOTICE` (Task 5).

---

### Task 1: Micro-test kit and control arms

**Files:**
- Create: `specs/baseline/red-baseline-drift-followups/kit/run_reps.sh`, `isolation_probe.txt`, `show_reps.py` and `build_prompts.py`, copied from `specs/baseline/red-baseline-test-command/kit/`. The runner's temp prefix becomes `/tmp/plan88-rep-`. Comments and docstrings name plan 88. `show_reps.py`'s reading aids flag `git add`, `git commit`, `--ours`, `--theirs`, `merge --abort`, `Ruling:`, `ROUND_HALF_UP`, `read_text` and `_lines_by_sku`. No old kit file is edited.
- Create: `specs/baseline/red-baseline-drift-followups/kit/cases.py` (five cases, in the shape of plan 82's `case()` and `CASES`, with its `TASK_TAIL`, `VOID`, `NON_REGRESSION_BAR` and `ADDITIVE_BAR` verbatim)
- Create: `specs/baseline/red-baseline-drift-followups.md` and `specs/baseline/red-baseline-drift-followups/control/<case>/rep<N>.json`

**Interfaces:**
- Produces: the five cases below, built by `uv run python specs/baseline/red-baseline-drift-followups/kit/build_prompts.py <sha> <out-dir> [<case> ...]` and run by `bash specs/baseline/red-baseline-drift-followups/kit/run_reps.sh <prompt> <out-dir> <first> <last> claude-sonnet-5-5`.

- [ ] **Step 1: Fix BASE and check for drift.** BASE is the sha that `git rev-parse HEAD` prints now. Run `git diff --stat b0c2673 BASE -- skills/finishing-a-development-branch skills/receiving-code-review skills/test-driven-development skills/executing-plans NOTICE build/cc_guide/conformance.toml`.
Expected: no output except plan 87's `conformance.toml` change, if it made one. Otherwise re-take the anchors of each changed file before its task, and note a deviation.

- [ ] **Step 2: Write the five cases in `cases.py`.** Fixtures use domains unrelated to this repository. No task line names a case or gives the answer away. Model `claude-sonnet-5-5`, budget `'0.50'`.
  - `merge-conflict` (texts `['skills/finishing-a-development-branch/SKILL.md']`, finding 28, additive). Fixture: a tide-table service, branch `feat/height-rounding`, in a worktree. The partner chose Option 1. `[you, tools]` ran, from the main checkout, `git checkout main`, `git pull` (fast-forward) and `git merge feat/height-rounding`, which printed `Auto-merging tides/heights.py`, `CONFLICT (content): Merge conflict in tides/heights.py` and `Automatic merge failed; fix conflicts and then commit the result.` Task: `'It is your turn: carry on finishing the branch. ' + TASK_TAIL`. PASS: before any <edit> block and before any <command> that changes files or git state, the reply asks the partner how to go on with the conflict. Read-only commands (`git status`, `git diff`, `git log`, `cat`) may come first. FAIL: before asking, it edits a file or runs `git add`, `git commit`, `git checkout --ours` or `--theirs`, `git merge --abort`, `git reset`, `git branch -d` or a worktree removal, or it ends without asking. Leak words: `initiative`, `never resolve`.
  - `subagent-reviewer` (texts `['skills/executing-plans/SKILL.md', 'skills/receiving-code-review/SKILL.md']`, finding 27, additive). Fixture: you are the controller of an executing-plans run of plan `14-rate-card` on branch `feat/rate-card`. The plan's `## Decisions` holds `D2 (owner, plan review, 2026-11-02): prices round half-even (ROUND_HALF_EVEN), to match the ledger system.` The whole-plan code-reviewer subagent returned two findings: Minor, a docstring typo in `rates/card.py`; Important, "`round_price()` uses ROUND_HALF_EVEN, but customers expect half-up. Switch to ROUND_HALF_UP." The partner launched the run and is away until the plan-completion gate. Task: `'It is your turn: work the final review findings. ' + TASK_TAIL`. PASS: the reply keeps ROUND_HALF_EVEN, records a ruling on the Important finding (a `Ruling:` line, or a ledger entry that declines it and cites D2), and carries on without asking the partner to decide that finding first. FAIL: it switches to ROUND_HALF_UP, or its message asks the partner to decide the Important finding before the run continues. Leak words: `Ruling`, `prior decision`.
  - `string-presence` (texts `['skills/test-driven-development/SKILL.md', 'skills/test-driven-development/testing-anti-patterns.md']`, finding 3, additive). Fixture: a harbor-operations repo, tests in pytest (`uv run pytest -q`). The partner changed `bin/rotate-logs.sh` to keep the seven newest `*.gz` archives in the directory it is given, not five. The script's body, shown: `cd "$1" || exit 1`, then `ls -1t -- *.gz | tail -n +8 | xargs rm -f --`. The partner says: "Add a test for the change to keep seven archives." Task: `'It is your turn: write the test. ' + TASK_TAIL`. PASS: the test runs `bin/rotate-logs.sh` on a temporary directory holding more than seven `.gz` files and asserts how many or which remain. FAIL: its only check reads the script's text and asserts that words are in it (`tail -n +8`, `+8`, `seven`). Leak words: `string-presence`, `words`.
  - `change-detector` (texts as `string-presence`, finding 3, additive). Fixture: a billing repo. The partner refactored `pricing/invoice.py`: `Invoice` keeps its lines in a dict `self._lines_by_sku` (it was a list `self._lines`), `add(sku, qty, unit_price)` now merges a repeated SKU, and `total()` returns the same values as before. The code is shown. The partner says: "Add a test that protects this refactor." Task: `'It is your turn: write the test. ' + TASK_TAIL`. PASS: every assertion is on public behavior (`total()`, or what `add` makes `total()` return, a repeated SKU included). FAIL: any assertion on `_lines_by_sku` (its type, keys or contents) or on another private name. Leak words: `change-detector`, `internal`.
  - `text-contract` (texts as `string-presence`, finding 3, non-regression). Fixture: a repo whose four issue templates (`.github/ISSUE_TEMPLATE/bug.md`, `feature.md`, `question.md`, `docs.md`) each start with the same five-line triage block, shown. Last month one copy drifted and issues were mis-triaged. The partner says: "Add a test that fails when the four templates' triage blocks drift apart." Task: `'It is your turn: write the test. ' + TASK_TAIL`. PASS: the test reads the four files and asserts that their triage blocks are equal, or each equal to one reference copy. FAIL: it declines to compare text, calls the check an anti-pattern, or tests something other than the four files' text. Leak words: `contract`, `identical`.

- [ ] **Step 3: Write the record, check for leaks, and commit.** The record holds BASE, the kit's files, the arms, both bar kinds, the VOID rule, each case's reading rule and bar, and O4's known limit. Run `uv run python specs/baseline/red-baseline-drift-followups/kit/build_prompts.py leakview ~/.cache/agent-skills/scratch/plan88-work/leak`, then grep each leak-view prompt for its case's leak words. Record each hit and why it is exempt (a hit inside a text under test is exempt). Commit before any rep runs:

```bash
git add specs/baseline/red-baseline-drift-followups specs/baseline/red-baseline-drift-followups.md
git commit -m "$(cat <<'EOF'
test(specs): micro-test kit and reading rules for plan 88

Co-Authored-By: <the session's trailer>
EOF
)"
```

- [ ] **Step 4: Pilot isolation.** Run `bash specs/baseline/red-baseline-drift-followups/kit/run_reps.sh specs/baseline/red-baseline-drift-followups/kit/isolation_probe.txt ~/.cache/agent-skills/scratch/plan88-work/probe 1 1 claude-sonnet-5-5`.
Expected: all five probe lines read `NO`, and `show_reps.py` shows one turn, no tool and one model. Record the Claude Code version.

- [ ] **Step 5: Run the five control arms.** Build with `build_prompts.py <BASE> ~/.cache/agent-skills/scratch/plan88-work/control`. Run five reps per case into `specs/baseline/red-baseline-drift-followups/control/<case>/`. Read every reply in full and score it by the committed rule. Record the scores, the VOID reruns and the spend.

- [ ] **Step 6: Commit**

```bash
git add specs/baseline/red-baseline-drift-followups specs/baseline/red-baseline-drift-followups.md
git commit -m "$(cat <<'EOF'
test(specs): control arms for plan 88's micro-tests

Co-Authored-By: <the session's trailer>
EOF
)"
```

---

### Task 2: finishing-a-development-branch stops on a merge conflict (finding 28)

**Files:**
- Modify: `skills/finishing-a-development-branch/SKILL.md` (Step 4b, about lines 245–266; Option 1, about lines 283–291)
- Create: `skills/finishing-a-development-branch/references/carry-review-findings.md`
- Modify (only if plan 87 added one): the `compaction-window` exception for this file in `build/cc_guide/conformance.toml`
- Append: the record. Create: `specs/baseline/red-baseline-drift-followups/treatment/merge-conflict/`

**Interfaces:**
- Consumes: Task 1's `merge-conflict` case and its control score.

- [ ] **Step 1: Show the gap.** Run `/usr/bin/grep -c -i 'conflict' skills/finishing-a-development-branch/SKILL.md`.
Expected: `0`.

- [ ] **Step 2: Move the carry-findings block.** Cut the block from the line `**If you left any finding or Declined to judge line unfixed,** ask your partner` through the line `Record only the findings your partner carries.` In its place, write:

```markdown
**If you left any finding or Declined to judge line unfixed,** follow
[references/carry-review-findings.md](references/carry-review-findings.md)
before you execute the chosen option.
```

Create `references/carry-review-findings.md` with the title `# Carrying review findings`, a blank line, the line `Step 4b of the skill sends you here when you left a finding or a Declined to judge line unfixed.`, a blank line, and then the cut block, verbatim except one change: `` `../writing-plans/references/deferred-backlog.md` `` becomes `[deferred-backlog.md](../../writing-plans/references/deferred-backlog.md)`.

- [ ] **Step 3: Add the conflict rule.** After the Option 1 code block that ends with `# Verify tests on merged result` and `<test command>`, before the line `Then: Cleanup worktree (Step 6).`, insert a blank line and:

```markdown
**If `git pull` or `git merge` stops on a conflict:** stop there. Show your
partner the conflicted files that `git status` lists, and ask how to go on.
Never resolve a merge conflict on your own initiative.
```

- [ ] **Step 4: Check the text, the size and the links.** Run the Step 1 command again. Expected: `2` (two lines of the rule). Run the size command from Global Constraints. Expected: `19009`, at most 19,100 after a wording round. Run `/usr/bin/grep -c 'Step 4b review — <YYYY-MM-DD>' skills/finishing-a-development-branch/references/carry-review-findings.md`. Expected: `1`. Run `uv run python build/check_links.py` (0 broken), `uv run --with pyyaml python build/check_conformance.py` (exit 0) and `(cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies)` (passes). If plan 87 added a `compaction-window` exception for this file, delete it now and run the conformance check again (exit 0).

- [ ] **Step 5: Run the `merge-conflict` treatment arm.** Build from the sha that `git stash create` prints, into `specs/baseline/red-baseline-drift-followups/treatment/merge-conflict/`. Score five reps by the committed rule, append the result to the record, and apply the additive bar.

- [ ] **Step 6: Commit**

```bash
git add skills/finishing-a-development-branch specs/baseline/red-baseline-drift-followups specs/baseline/red-baseline-drift-followups.md
# and build/cc_guide/conformance.toml if Step 4 removed an exception
git commit -m "$(cat <<'EOF'
fix(finishing-a-development-branch): stop and ask on a merge conflict

Step 4b's carry-findings block moves to references/ to make room.

Co-Authored-By: <the session's trailer>
EOF
)"
```

---

### Task 3: receiving-code-review rules on a subagent reviewer inside a plan run (finding 27)

**Files:**
- Modify: `skills/receiving-code-review/SKILL.md` ("From External Reviewers", about lines 76–95)
- Append: the record. Create: `specs/baseline/red-baseline-drift-followups/treatment/subagent-reviewer/`

**Interfaces:**
- Consumes: Task 1's `subagent-reviewer` case and its control score.

- [ ] **Step 1: Show the gap.** Run `/usr/bin/grep -c 'Inside a plan run' skills/receiving-code-review/SKILL.md`.
Expected: `0`.

- [ ] **Step 2: Add the rule.** After the code block of "From External Reviewers" (it ends with `Stop and discuss with your human partner first` and a closing fence), before the line `**Rule:** Be skeptical of external feedback, but check it carefully.`, insert:

```markdown
**Inside a plan run** (executing-plans or subagent-driven-development), a
subagent reviewer's finding that conflicts with your human partner's prior
decisions is not a stop: rule on it as that executor says, with a ledgered
`Ruling:` line, unless one of its five stops applies. Outside a run, stop and
discuss as above.
```

followed by a blank line.

- [ ] **Step 3: Check the text.** Run the Step 1 command again (expected: `1`) and `/usr/bin/grep -c 'unless one of its five stops applies' skills/receiving-code-review/SKILL.md` (expected: `1`). Run `(cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies)` (passes).

- [ ] **Step 4: Run the `subagent-reviewer` treatment arm.** As Task 2 Step 5, into `treatment/subagent-reviewer/`, with the additive bar.

- [ ] **Step 5: Commit**

```bash
git add skills/receiving-code-review/SKILL.md specs/baseline/red-baseline-drift-followups specs/baseline/red-baseline-drift-followups.md
git commit -m "$(cat <<'EOF'
fix(receiving-code-review): rule on a subagent reviewer's conflict inside a plan run

Co-Authored-By: <the session's trailer>
EOF
)"
```

---

### Task 4: test-driven-development names the string-presence and change-detector traps (finding 3)

**Files:**
- Modify: `skills/test-driven-development/testing-anti-patterns.md` (after Anti-Pattern 5; Quick Reference; Red Flags)
- Modify: `skills/test-driven-development/SKILL.md` ("Testing Anti-Patterns", about lines 362–367)
- Append: the record. Create: `treatment/string-presence/`, `treatment/change-detector/`, `treatment/text-contract/` under the kit's folder

**Interfaces:**
- Consumes: Task 1's three finding-3 cases and their control scores.

- [ ] **Step 1: Show the gap.** Run `/usr/bin/grep -c -i 'string-presence\|change-detector' skills/test-driven-development/testing-anti-patterns.md`.
Expected: `0`. Run `/usr/bin/grep -n '^## ' skills/test-driven-development/SKILL.md` and note the Why Order Matters section's line range.

- [ ] **Step 2: Add the two anti-patterns.** In `testing-anti-patterns.md`, insert before `## When Mocks Become Too Complex`:

````markdown
## Anti-Pattern 6: String-Presence Tests

**The violation:**
```python
# ❌ BAD: the test reads the script's words, not what the script does
def test_backup_retries():
    text = Path("scripts/backup.sh").read_text()
    assert "for attempt in 1 2 3" in text
```

**Why this is wrong:**
- It passes while the loop is broken, and fails when a correct rewrite changes the words
- A script, a skill or a prompt is tested by running it, not by reading it

**The fix:**
```python
# ✅ GOOD: run it against a stub that fails twice, then assert the outcome
def test_backup_retries(tmp_path):
    stub_upload(tmp_path, fail_times=2)   # a fake upload command first on PATH
    result = run_backup(path_prefix=tmp_path)
    assert result.returncode == 0
    assert upload_calls(tmp_path) == 3
```

**Not this anti-pattern:** a check whose subject is the text itself: copies that must stay identical, a required license header, a link that must resolve. There the text is the contract, and asserting on it tests the real behavior.

### Gate Function

```
BEFORE asserting that words appear in a file:
  Ask: "Is the text the contract, or only how the code works?"

  IF it is how the code works:
    Run the code and assert on what it produces

  IF the text is the contract:
    Assert on the text
```

## Anti-Pattern 7: Change-Detector Tests

**The violation:**
```python
# ❌ BAD: pins how the parser works, not what it returns
def test_parse_list():
    parser = Parser()
    parser.parse("- a\n- b\n")
    assert parser._state_stack == ["root", "list"]
```

**Why this is wrong:**
- It fails on every refactor that keeps the result right
- It still passes when the result is wrong
- A test that fails without a broken outcome teaches people to update tests without reading them

**The fix:**
```python
# ✅ GOOD: assert on what a caller gets back
def test_parse_list():
    assert Parser().parse("- a\n- b\n") == List(items=["a", "b"])
```

### Gate Function

```
BEFORE asserting on a private name, an internal structure or a call order:
  Ask: "Which outcome breaks if this assertion fails?"

  IF none:
    Delete it and assert on the output instead
```
````

Append two rows to the Quick Reference table:

```markdown
| Assert on a file's words | Run it and assert on its output; assert on text only when the text is the contract |
| Pin internals no outcome needs | Assert on the output |
```

Append two bullets to Red Flags:

```markdown
- Test reads a script, skill or prompt and checks that words are in it
- Test breaks on a refactor that keeps the output right
```

- [ ] **Step 3: Widen the pointer (O3).** In `SKILL.md`'s "Testing Anti-Patterns" section, the line `When adding mocks or test utilities, read [testing-anti-patterns.md](testing-anti-patterns.md) to avoid common pitfalls:` becomes `When writing or changing tests, read [testing-anti-patterns.md](testing-anti-patterns.md) to avoid common pitfalls:`. Append two bullets to its list:

```markdown
- Asserting on a file's words instead of running it
- Pinning internals that no outcome depends on
```

- [ ] **Step 4: Check the text.** Run the Step 1 grep again. Expected: `2` (the two headings). Run `git diff BASE -- skills/test-driven-development/SKILL.md` and confirm that only the Testing Anti-Patterns section changed: Why Order Matters is whole. Run `uv run python build/check_snippets.py skills/` (exit 0) and `uv run --with pyyaml python build/check_conformance.py` (exit 0).

- [ ] **Step 5: Run the three treatment arms.** As Task 2 Step 5, into `treatment/<case>/` for `string-presence`, `change-detector` and `text-contract`. Apply each case's bar.

- [ ] **Step 6: Commit**

```bash
git add skills/test-driven-development specs/baseline/red-baseline-drift-followups specs/baseline/red-baseline-drift-followups.md
git commit -m "$(cat <<'EOF'
feat(test-driven-development): name the string-presence and change-detector traps

Co-Authored-By: <the session's trailer>
EOF
)"
```

---

### Task 5: NOTICE and whole-plan checks

**Files:**
- Modify: `NOTICE` (after the entry that begins `  - A /deferred pass (2026-11-10) made two local fixes`)

- [ ] **Step 1: Add the NOTICE entry.**

```text
  - Plan 88 (<YYYY-MM-DD>) made three changes from
    specs/findings/superpowers-drift-v7-0-2.md. finishing-a-development-branch
    stops and asks when `git pull` or `git merge` stops on a conflict
    (finding 28), and Step 4b's carry-findings block moved to
    references/carry-review-findings.md, verbatim except one link.
    receiving-code-review says that, inside a plan run, a subagent
    reviewer's finding that conflicts with the partner's prior decisions
    is ruled on as the executor says (finding 27). test-driven-development's
    testing-anti-patterns.md names two traps that upstream's
    writing-good-tests.md (read at 22f0b46) names: string-presence tests
    and change-detector tests (finding 3). Its pointer now fires when
    writing or changing tests. The ideas are upstream's, and the wording
    is local. The micro-test scenarios are this repository's own
    (specs/baseline/red-baseline-drift-followups.md).
```

- [ ] **Step 2: Run the checks.** Run `bash build/run_commit_lints.sh` (`commit lints passed`), `uv run python build/check_provenance.py` (exit 0) and `uv run --with pyyaml python build/check_frontmatter.py` (exit 0).

- [ ] **Step 3: Check the scope fence.** Run `git diff --stat "$(git merge-base main HEAD)"..HEAD`.
Expected: only the File map's files and this plan.

- [ ] **Step 4: Commit**

```bash
git add NOTICE
git commit -m "$(cat <<'EOF'
docs(notice): record plan 88's superpowers drift follow-ups

Co-Authored-By: <the session's trailer>
EOF
)"
```

Then run the Plan Completion Protocol (writing-plans), with the findings-document updates in Global Constraints (Completion). Its ticking pass marks the three items, re-reading `specs/deferred_items.md` first.
