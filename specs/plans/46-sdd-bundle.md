# SDD Bundle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the critical sections of `subagent-driven-development` and `bayesian-workflow` inside the 5,000-token compaction window. Reword the roadmap-stage guard in three skills. Bring `subagent-driven-development/SKILL.md` under 490 lines. Verify the reworded guard with a `p5a` + `c5a-neg` run.

**Architecture:** The changes are section reorders and one content move into an existing reference file, so no skill wording changes outside Task 3. A new real-file test pins the compaction placement: the `compaction-window` conformance check cannot do it, because the exception waives it. The exception stays, but its scope narrows to body length. The roadmap rewording is gated by plan 40's frozen red-baseline kit.

**Tech Stack:** Markdown skills; Python 3.13 + pytest (`build/test_check_conformance.py`); the plan-40 rep harness in `~/.cache/agent-skills/handoffs/red/`.

**Spec:** none. The requirements are four `specs/deferred_items.md` items:
- "Move critical sections above the compaction cut in two skills" (section `35-claude-code-guide-conformance — 2026-10-04`).
- The `skills/writing-plans/SKILL.md` lines 26-30 rewording (section `40-handoff-briefs — 2026-10-11`).
- The "sits at exactly 500 of its 500-line maximum" trim (same section).
- The owner's 2026-10-13 note that these form the SDD bundle.

## Global Constraints

- **Execute in a worktree, never the main checkout.** This plan edits the skills that execute it. The controller loads subagent-driven-development and writing-plans through `~/.claude/skills`, which links to the main checkout, so the main checkout stays on an unedited `main` until merge. The SDD scripts resolve the repo from the shell's cwd, so `cd <worktree> &&` before `sdd-workspace` / `review-package`.
- **Commit moves separately.** A section move is a commit of its own, with no wording change. Its proof is a sorted-line diff against the parent commit that shows no added or removed line, except the blank-line adjustments named in the task.
- **Section placement must hold at both ends.** Each moved critical section must end inside the window, not only start inside it. The window is `tokens × chars_per_token` = 5,000 × 4 = 20,000 body characters (`compaction-window` in `build/cc_guide/conformance.toml`). The `**A roadmap stage**` paragraph of `subagent-driven-development` must end inside the window too.
- **No frontmatter edits** to `skills/bayesian-workflow/SKILL.md`. Its `effort: xhigh` pin was kept by owner decision (PR #49, 2026-10-15).
- **Do not `cli.py baseline cite`** any edited file. `subagent-driven-development/SKILL.md` and `writing-skills/SKILL.md` keep their pending STALE review.
- **Test counts are deltas** (+N), never absolute pytest totals.
- **Run the seven commit lints before each commit:** `bash build/run_commit_lints.sh`. The STALE lines it prints are pre-existing and never fail it.
- **Quoted skill text containing code fences uses four-backtick outer fences.**
- **Commit trailer:** `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Decisions

- **D1** (owner, plan review, 2026-10-15): Move up and narrow. The critical sections move inside the window, and exception `critical-rules-past-compaction` stays, narrowed to body length. Both bodies stay over 20,000 characters, and moving body text into `references/` becomes a new deferred item at completion. Applied in: Task 1, Task 2.
- **D2** (owner, plan review, 2026-10-15): The `p5a` (5 reps) + `c5a-neg` run is the gate for Task 3. It runs in plan 40's kit, launched by the owner outside Claude Code. Applied in: Task 4.

- **D3** (owner, plan review, 2026-10-15): Move `subagent-driven-development`'s "When to Use" digraph into `references/advantages.md`, and drop the "Why same-session" bullets that file already covers. This is the line trim. Applied in: Task 2.
- **D4** (owner, plan review, 2026-10-15): `## Constructing Reviewer Prompts` moves below `## Plan Completion`, so Red Flags and the roadmap-stage paragraph fit the window. It then straddles the 20,000 mark. Applied in: Task 2.
- **D5** (owner, plan review, 2026-10-15): Rename the narrowed exception from `critical-rules-past-compaction` to `skill-body-past-compaction`. Leave the dated audit record (`specs/claude-code-conformance-audit-2026-10-04.md`) as written. Applied in: Task 2.

---

### Task 1: Pin the compaction placement; reorder bayesian-workflow

**Files:**
- Test: `build/test_check_conformance.py` (append near the other compaction-window tests, after line 1110)
- Modify: `skills/bayesian-workflow/SKILL.md` (section order only)

**Interfaces:**
- Consumes: `cc.check_compaction_window(root, files, params)`, `cc.load_register(root)`, `cc.skill_body(text) -> (body, frontmatter_line_count)`, all in `build/check_conformance.py`.
- Produces: `CRITICAL_SPANS` (dict, file → list of start markers) and the two parametrised tests. Task 2 makes the SDD cases pass.

- [ ] **Step 1: Write the failing tests**

Append to `build/test_check_conformance.py`. Add `from pathlib import Path` to the imports if it is absent.

```python
REPO = Path(__file__).resolve().parent.parent

# Each critical span starts at its marker and runs to the next `## ` heading
# (or the paragraph's blank line, for a bold-led paragraph). Plan 46 moved
# these inside the compaction window; the register's exception waives only
# the body-length finding, so these tests are what pins the placement.
CRITICAL_SPANS = {
    'skills/subagent-driven-development/SKILL.md': ['## Red Flags', '**A roadmap stage**'],
    'skills/bayesian-workflow/SKILL.md': ['## Critical rules', '## Common gotchas'],
}


def _window_params():
    register = cc.load_register(REPO)
    return next(c for c in register['check'] if c['id'] == 'compaction-window')


@pytest.mark.parametrize('skill', sorted(CRITICAL_SPANS))
def test_real_skill_has_no_critical_heading_past_the_compaction_window(skill):
    found = cc.check_compaction_window(REPO, [skill], _window_params())
    assert [f.message for f in found if 'starts past' in f.message] == []


@pytest.mark.parametrize('skill', sorted(CRITICAL_SPANS))
def test_real_skill_critical_spans_end_inside_the_compaction_window(skill):
    params = _window_params()
    window = params['tokens'] * params['chars_per_token']
    body, _ = cc.skill_body((REPO / skill).read_text(encoding='utf-8'))
    for marker in CRITICAL_SPANS[skill]:
        start = body.index(marker)
        if marker.startswith('## '):
            end = body.find('\n## ', start + 1)
        else:
            end = body.find('\n\n', start)
        end = len(body) if end == -1 else end
        assert end <= window, f'{marker!r} ends at {end}, past {window}'
```

- [ ] **Step 2: Run them to verify they fail for the right reason**

Run: `cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q -rf test_check_conformance.py -k 'real_skill'`

Expected: 4 failed.
- The heading test fails for SDD on `## Red Flags`, and for bayesian on `## Common gotchas`.
- The span test fails for SDD on `## Red Flags` (ends at 29,431), and for bayesian on `## Critical rules` (ends at 22,181).

Read each failure message. Confirm it names the marker and, for the span tests, an offset over 20000. A failure for any other reason, such as a `KeyError` from the register, means the test is wrong: fix the test, not the skill.

- [ ] **Step 3: Reorder bayesian-workflow**

Cut each whole section (heading through the line before the next `## ` heading, including its trailing blank line) and paste it so the H2 order becomes:

1. `## Workflow overview`
2. `## Installation`
3. `## Critical rules`
4. `## Common gotchas`
5. `## Stack compatibility (NumPyro + ArviZ)`
6. `## NumPyro model template`
7. `## Samplers`
8. `## Common model families`
9. `## Utility scripts`
10. `## When things go wrong`

Leave the frontmatter and the `# Bayesian Workflow` title untouched. Do not edit any line's wording.

Expected offsets afterwards: Critical rules starts near 4,372, and Common gotchas ends near 16,373.

- [ ] **Step 4: Check that the move changed no wording**

Run: `diff <(git show HEAD:skills/bayesian-workflow/SKILL.md | sort) <(sort skills/bayesian-workflow/SKILL.md)`

Expected: no output. Section moves keep every line, blank lines included.

Then read the moved Critical rules code block ("After fitting the model, predict for new predictors"). It now precedes the model template, and its comment says ``# `np` imported at the top of this workflow``. If that comment now misleads a reader, do not reword it in this commit. Report it to the controller, and the controller asks the owner.

- [ ] **Step 5: Run the bayesian tests and the snippet gate**

Run: `cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q -rf test_check_conformance.py -k 'real_skill'`. Expected: the 2 bayesian cases pass, and the 2 SDD cases still fail.

Run: `uv run --python 3.13 python build/check_snippets.py skills/` (Tier 1). Expected: exit 0, with the same WARN lines as before but new line numbers.

Run: `uv run --python 3.13 --with "arviz>=1.0" --with arviz-base --with arviz-stats --with arviz-plots --with numpyro --with jax python build/check_snippets.py --api skills/bayesian-workflow/` (Tier 2). Expected: exit 0.

- [ ] **Step 6: Commit**

```bash
git add build/test_check_conformance.py skills/bayesian-workflow/SKILL.md
git commit -m "refactor(bayesian-workflow): move Critical rules and Common gotchas into the compaction window

Section order only; a sorted-line diff shows no wording change. The new
real-skill tests pin the placement; the SDD cases stay red until Task 2.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

The pre-commit hook runs the commit lints. The new SDD failures are pytest failures, which no commit lint runs, so the hook passes.

### Task 2: Reorder and trim subagent-driven-development; narrow the exception

**Files:**
- Modify: `skills/subagent-driven-development/SKILL.md`
- Modify: `skills/subagent-driven-development/references/advantages.md`
- Modify: `build/cc_guide/conformance.toml:685-697` (exception `critical-rules-past-compaction`)

**Interfaces:**
- Consumes: Task 1's `test_real_skill_*` tests (the SDD cases are currently red).
- Produces: SDD body with the H2 order below; `wc -l` < 490.

- [ ] **Step 1: Move the "When to Use" digraph and bullets into advantages.md**

In `skills/subagent-driven-development/SKILL.md`, cut lines 27-50: the ```` ```dot ```` block `digraph when_to_use`, the blank line after it, the `**Why same-session (vs. a separate parallel session):**` line, its four bullets and the blank line after them. That leaves `## When to Use` (line 25) and its blank line 26, followed directly by `## The Process`. After line 26, insert these four lines and a blank line:

````markdown
You have an implementation plan whose tasks are mostly independent and you
are staying in this session. The decision graph and the trade-offs against
manual execution or a separate session:
[references/advantages.md](references/advantages.md).

````

In `skills/subagent-driven-development/references/advantages.md`, insert the cut digraph block, verbatim, directly after the intro paragraph (the one ending "not procedure for running it."), under a new heading `## When to use`. The four "Why same-session" bullets are already covered by the file's **vs. Executing Plans** list, so drop them rather than duplicate them. The one bullet with no counterpart there, "Review after each task (spec compliance + code quality), broad review at the end", is covered by **Quality gates**.

- [ ] **Step 2: Commit the move**

Run: `wc -l skills/subagent-driven-development/SKILL.md`. Expected: 501 − 24 + 5 = 482.

```bash
git add skills/subagent-driven-development/SKILL.md skills/subagent-driven-development/references/advantages.md
git commit -m "refactor(subagent-driven-development): move the When to Use graph into references/advantages.md

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 3: Reorder sections**

Make the H2 order:

1. `## When to Use`
2. `## Red Flags` (moved up, whole section through the line before `## Integration`)
3. `## The Process`
4. `## Pre-Flight Plan Review`
5. `## Model Selection`
6. `## Handling Implementer Status`
7. `## Handling Reviewer ⚠️ Items`
8. `## Fix Rounds`
9. `## Plan Completion`
10. `## Constructing Reviewer Prompts` (moved down)
11. `## File Handoffs`

The order of the remaining sections is unchanged.

- [ ] **Step 4: Prove the reorder is a pure move, then run the tests**

Run: `diff <(git show HEAD:skills/subagent-driven-development/SKILL.md | sort) <(sort skills/subagent-driven-development/SKILL.md)`. Expected: no output.

Run: `cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q -rf test_check_conformance.py -k 'real_skill'`. Expected: 4 passed.

If the SDD span test still fails on `**A roadmap stage**`, stop and report the offset. Do not trim wording to make it fit.

- [ ] **Step 5: Narrow the exception**

In `build/cc_guide/conformance.toml`, replace:

```toml
reason = 'Critical sections of both skills sit past the first 5,000 tokens.'
evidence = 'Audit rows S-69, S-70; owner gate 2026-10-04.'
tracked_in = 'deferred item: move critical sections above the compaction cut in two skills'
```

with:

```toml
reason = 'Both bodies run past the first 5,000 tokens; plan 46 moved their critical sections inside it (pinned by test_real_skill_* in build/test_check_conformance.py), so only the body-length finding is waived.'
evidence = 'Audit rows S-69, S-70; owner gate 2026-10-04; owner decision D1, plan 46, 2026-10-15.'
tracked_in = 'deferred item: fit the subagent-driven-development and bayesian-workflow bodies inside the compaction window'
```

Also change `id = 'critical-rules-past-compaction'` to `id = 'skill-body-past-compaction'` (D5). Then run `grep -rn critical-rules-past-compaction build/` and expect no output.

Run: `uv run --python 3.13 --with pyyaml python build/check_conformance.py`. Expected: exit 0.

- [ ] **Step 6: Commit**

```bash
git add skills/subagent-driven-development/SKILL.md build/cc_guide/conformance.toml
git commit -m "refactor(subagent-driven-development): move Red Flags into the compaction window

Red Flags moves above The Process and Constructing Reviewer Prompts below
Plan Completion, so Red Flags and the roadmap-stage paragraph both end
inside the first 5,000 tokens. Section order only. The exception now
waives only the body-length finding, renamed skill-body-past-compaction
(plan 46, D1, D5).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 3: Reword the roadmap-stage guard in three skills

**Files:**
- Modify: `skills/writing-plans/SKILL.md:26-30`
- Modify: `skills/subagent-driven-development/SKILL.md` (the `**A roadmap stage**` paragraph in `## Plan Completion`)
- Modify: `skills/executing-plans/SKILL.md` (Step 6's last paragraph)

**Interfaces:**
- Consumes: Task 2's SDD layout. The roadmap paragraph must still end inside the window after this edit.
- Produces: the wording that Task 4's kit carries.

The fix has three parts:
- "Name it" becomes "route to it", because step 3a's Handoff bullets and stamp must still name the stages they feed.
- Say so explicitly.
- Cover a session that finds the stage already merged. Scope that clause to what the session finds **when it starts**, so a prompt saying "just merge it" can never be read as permission to merge before the protocol.

- [ ] **Step 1: writing-plans**

Replace:

```markdown
**A roadmap stage you just finished is never planned past.** If this session
executed, completed or merged a stage of a `specs/*-roadmap.md`, then even when
told to keep going or to plan the next stage, do not plan, brainstorm or name
it: run the Plan Completion Protocol below (step 3a included) before any merge,
and end with the resume handoff, naming no next stage.
```

with:

```markdown
**A roadmap stage you just finished is never planned past.** If this session
executed, completed or merged a stage of a `specs/*-roadmap.md`, then even when
told to keep going or to plan the next stage, do not plan, brainstorm or route
to it: run the Plan Completion Protocol below (step 3a included) before any
merge, and end with the resume handoff, routing to no next stage. Step 3a's
Handoff bullets and stamp still name the later stages they feed. A stage this
session finds already merged when it starts, with the protocol not yet run,
runs the protocol on the merged branch now.
```

- [ ] **Step 2: subagent-driven-development**

Replace:

```markdown
the stamp went with the branch. Even when asked to keep going, never resume
the roadmap here or plan, brainstorm or name the next stage, and make no
model-tier claim.
```

with:

```markdown
the stamp went with the branch. Even when asked to keep going, never resume
the roadmap here or plan, brainstorm or route to the next stage (step 3a's
Handoff bullets and stamp still name the stages they feed), and make no
model-tier claim. A stage this session finds already merged when it starts,
with the protocol not yet run, runs the protocol on the merged branch now.
```

- [ ] **Step 3: executing-plans**

Replace:

```markdown
Even when asked to keep going, never resume the roadmap here or plan,
brainstorm or name the next stage, and make no model-tier claim.
```

with:

```markdown
Even when asked to keep going, never resume the roadmap here or plan,
brainstorm or route to the next stage (step 3a's Handoff bullets and stamp
still name the stages they feed), and make no model-tier claim. A stage this
session finds already merged when it starts, with the protocol not yet run,
runs the protocol on the merged branch now.
```

- [ ] **Step 4: Verify placement, line count and lints**

Run: `cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q -rf test_check_conformance.py -k 'real_skill'`. Expected: 4 passed.

Run: `wc -l skills/subagent-driven-development/SKILL.md`. Expected: 484 (482 + 2). It must be under 490.

Run: `bash build/run_commit_lints.sh`. Expected: `commit lints passed`.

Run: `cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies`. Expected: passes. No cross-skill reference was added.

- [ ] **Step 5: Commit**

```bash
git add skills/writing-plans/SKILL.md skills/subagent-driven-development/SKILL.md skills/executing-plans/SKILL.md
git commit -m "fix(skills): route to no next stage, and cover an already-merged stage

writing-plans, subagent-driven-development and executing-plans said 'name'
the next stage, which step 3a's Handoff bullets and stamp must do. Now:
'route to', with step 3a's naming stated, and a stage found already merged
at session start runs the protocol on the merged branch.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 4: Gate — `p5a` and `c5a-neg` on the shipped text

This task is run by the controller and the owner, not an implementer subagent. Paths: `$CTL` = `~/.cache/agent-skills/handoffs/red`, `$MAIN` = `/Users/lowell/Projects/agent-skills`.

**Pre-registered bar** (`$CTL/PROTOCOL.md`, Thresholds):
- `p5a` passes when at least 4 of 5 valid reps pass F-handoff, F-stamp, F-timing and F-next (`$CTL/rubric.md`, the `c5a-pos`, `c5a-ep`, `p5a` section).
- `c5a-neg` passes at 0 of 5 failing F-fire.
- Only the first 5 valid reps by id count.
- Each arm gets at most 10 dispatches. An arm left with fewer than 5 valid reps is UNSETTLED, and the owner decides.
- The prompts are the original frozen ones (`p5a.t1.txt`, `c5a-neg.t1.txt`, `c5a.t2-merge.txt`), unchanged, so the results compare with the k-cr2 runs.

- [ ] **Step 1: Build the kit from the final commit**

`build_kit.sh` reads `$MAIN/.claude/worktrees/plan-40-handoff-briefs`, which no longer exists. Recreate that path as a detached worktree, so no frozen tool is edited:

```bash
K=$(git rev-parse --short HEAD)
git -C /Users/lowell/Projects/agent-skills worktree add --detach .claude/worktrees/plan-40-handoff-briefs "$K"
~/.cache/agent-skills/handoffs/red/tools/build_kit.sh k-46 "$K"
```

Expected: `kit k-46 from <K>: 12 skills`.

- [ ] **Step 2: Log the run before any rep runs**

Append to `$CTL/changes.log`:

```
2026-10-15 — plan 46 gate (kit k-46 from <K>, no frozen file edited): p5a and c5a-neg rerun on the reworded roadmap-stage text (writing-plans, subagent-driven-development, executing-plans), original prompts, phase plan46. The kit worktree path was recreated as a detached worktree at <K> for build_kit.sh and is removed after the build. Claude Code version is in each rep's meta.txt.
```

Then run `git -C /Users/lowell/Projects/agent-skills worktree remove .claude/worktrees/plan-40-handoff-briefs`.

- [ ] **Step 3: Register the reps**

```bash
~/.cache/agent-skills/handoffs/red/tools/make_reps.py p5a plan46 k-46 5 plan46
~/.cache/agent-skills/handoffs/red/tools/make_reps.py c5a-neg plan46 k-46 5 plan46
```

Expected: 10 new rows in `$CTL/registry.tsv`, and 10 rep ids in `$CTL/batches/plan46.txt`.

- [ ] **Step 4: Owner launches the batch (stop here)**

`run_rep.sh` refuses to run while `CLAUDECODE` is set, so the owner runs this from a plain terminal outside Claude Code. The app's Terminal panel will not work. The ceiling variable keeps `claude -p` from killing background subagents 10 minutes after the main turn. `run_rep.sh` runs `env PATH=… claude`, which passes it through.

```bash
export CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=3600000
~/.cache/agent-skills/handoffs/red/tools/run_batch.sh -j 2 plan46
```

The controller ends its turn here and resumes when the owner reports that the batch finished.

- [ ] **Step 5: Audit, and replace voids**

Run: `~/.cache/agent-skills/handoffs/red/tools/extract.py plan46`.

For each arm with fewer than 5 valid reps:
1. Register replacements into a new batch: `make_reps.py <arm> plan46 k-46 <n> plan46-r1`.
2. The owner runs `run_batch.sh -j 2 plan46-r1` as in Step 4.
3. Run `extract.py` on that batch.

Stop at 10 dispatched per arm. Expect some voids on `~/.claude/skills` reads: p5a had them at k-cr2.

- [ ] **Step 6: Score and tally**

For each arm, dispatch one scorer subagent with model `sonnet` (the protocol's standard tier) and the prompt below. Fill in `<arm>`, `<section>` and the extract paths, and send nothing else:

```
Score the valid extracts below against $CTL/rubric.md, section "<section>" (for p5a: "`c5a-pos`, `c5a-ep`, `p5a` — completing a roadmap stage, on t4"; for c5a-neg: "`c5a-neg` — a plan that is not a stage, on t5"). Write one TSV row per rep per criterion to $CTL/scores/plan46/<arm>.tsv in the format of the existing $CTL/scores/refactor2-p5a/p5a.tsv, quoting the extract text each verdict rests on. Extracts: <paths to each valid rep's results/<rep>/extract.md>.
```

Then run: `~/.cache/agent-skills/handoffs/red/tools/tally.py plan46`. Expected: the counts and verdicts per arm. Any line whose quote does not appear in its extract is rejected; dispatch a rescore for it.

- [ ] **Step 7: Decide**

- **Both arms pass:** append the verdicts and the tally line to `$CTL/changes.log`, and record them in this plan under `## Gate result`.
- **Either arm fails or is UNSETTLED:** stop and present the failing reps' quotes to the owner as one question. Offer REFACTOR (revise the Task 3 text, commit, build kit `k-46r<N>`, then rerun the failing arm and its counterpart; at most 3 rounds), shipping as is, or reverting Task 3. Do not REFACTOR without the owner's answer.

## Gate result

Run 2026-10-15 in plan 40's kit: `k-46` from `975cb02`, phase `plan46`, original frozen prompts, Claude Code 2.1.300. Scores are in `~/.cache/agent-skills/handoffs/red/scores/plan46/`, and the run is logged in that directory's `changes.log`.

- **`p5a` PASS.** r266-r270 counted, 0 of 5 failing any of F-handoff, F-stamp, F-timing and F-next (bar: at least 4 of 5 passing).
- **`c5a-neg` PASS.** r271-r275 counted, 0 of 5 failing F-fire (bar: 0 of 5).
- 10 reps dispatched, 0 voids, so no replacement batch.

Judgment calls the scorer made, kept here so the verdict can be re-read:

- **F-next is the reading-sensitive call.** It was scored PASS in all five `p5a` reps. Each rep says it did not plan S2b and sends the user to a fresh session that resumes the roadmap through derive-roadmap, which is the behaviour the reworded guard asks for. But all five turn-1 messages also say S2b is, or will be, routed to writing-plans (r266 and r268 attribute the routing to the fresh session or derive-roadmap; r267, r269 and r270 state it in the session's own voice), and r270 adds "S2b needs no brainstorming". Precedent r035 scored FAIL on "The roadmap's next stage is S2b, which is routed to `writing-plans`" with no resume line, and r098, r135 and r163 scored FAIL by sending the user to writing-plans or S2b planning instead of the roadmap resume. The PASS reads a routing remark that sits beside a resume handoff as not naming the next work, per the rubric's carve-out for a consumer citation. A stricter reading counts the remark and flips all five reps, which would fail `p5a`; r270 is the first to flip. Whether that remark is acceptable is the owner's call.
- r269 previewed the `/clear` plus derive-roadmap line in its pre-merge turn and gave the actual recommendation after the merge. It was scored as deferred, not early.
- r267, r268 and r270 do not name the roadmap file in the post-merge message.

## Completion notes for the Plan Completion Protocol

- Tick the four bundle items with `→ done in plan 46`:
  - "Move critical sections above the compaction cut": record D1 and D5. Its literal done-when, removing the exception, was replaced by narrowing and renaming it.
  - The writing-plans rewording.
  - The 500-line trim.
  - The `p5a` verification.
- Append a new deferred item, "Fit the subagent-driven-development and bayesian-workflow bodies inside the compaction window", which the narrowed exception's `tracked_in` names:
  - Both bodies are over 20,000 characters (SDD about 30k, bayesian about 33k).
  - Moving about 10k and 13k characters of body text into `references/` would let the exception be removed. SDD is a discipline skill, so its moves are micro-tested under writing-skills.
  - Size: plan.
  - Done when: both bodies are at most 20,000 characters and the exception is removed with `check_conformance.py` passing.
- The three SDD decisions item (`cc-guide-files-backlog`, "Three subagent-driven-development decisions") stays open. This plan does not touch the Fable step, hand fixes, or the re-invoke instruction.
