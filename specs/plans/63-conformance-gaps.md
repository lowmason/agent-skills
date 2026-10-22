# Claude Code guide conformance gaps (plan 35 leftovers) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close four open conformance gaps from the plan-35 Claude Code guide audit, so that four `gap` exceptions leave `build/cc_guide/conformance.toml` (or become owner-recorded deviations).

**Architecture:** Wording changes to seven skill descriptions and to four side-effecting skills, one new Codex policy file, and one new PreToolUse hook (`hooks/dispatch-model-guard.py`) built on the pattern of `hooks/readonly-agent-guard.py`. Each task changes its exception in `conformance.toml` in the same commit. Description and gate wording is micro-tested in decision-only `claude -p` runs against the current wording as the control.

**Tech Stack:** Markdown skill text; YAML frontmatter; Python 3.9-compatible standard library for the hook; pytest; Claude Code `claude -p` (version recorded at Task 0); the repo's nine commit lints (`build/run_commit_lints.sh`).

**Spec:** none. The requirements are five open items in `specs/deferred_items.md`. Four are in section `## 35-claude-code-guide-conformance — 2026-10-04`, and one is in section `## audit-3-10-26 routing (no plan; re-verification pass, branch claude/quizzical-hermann-814d89) — 2026-10-18`. Read each in full before starting. The owner chose them at a `/deferred` triage on 2026-10-21 (group P1). The plan's completion protocol ticks them, not the tasks.

## Owner questions (answer at plan review, before execution)

Each question has a recommended default. The tasks are written for the default. The alternative's changes are listed in the task, so an answer edits the plan, not the work.

**Q1. Item A: gate each side-effecting skill in its body, or make it manual-only?** Background: "manual-only" means `disable-model-invocation: true` in the SKILL.md frontmatter plus `agents/openai.yaml` with `policy.allow_implicit_invocation: false` (the Codex equivalent, required by `build/check_frontmatter.py` since plan 53). A manual-only skill leaves the skill listing, and Claude cannot invoke it. So another skill cannot hand off to it by bare name, and an agent cannot preload it. A body gate does **not** meet the guide line "A side-effecting workflow sets disable-model-invocation: true". So a body-gated skill leaves the `gap` exception only by moving into a `deviation` exception, which is the owner's decision (CLAUDE.md, "Editing skills"). `check_conformance.py` passes either way, because these exceptions carry no `check` key. The lint is no evidence here.

| Skill | Side effect (audit) | Inbound bare-name handoffs | Recommended | Alternative |
|---|---|---|---|---|
| dispatching-parallel-agents | paid subagent fan-out | none | **manual-only** (Task 1) | body gate + a new deviation |
| writing-skills | commit, and push to a fork (`SKILL.md:692`) | `CLAUDE.md` tells agents to follow it; write-with-asd-ste100 names it | **body gate + new deviation `side-effecting-skills-body-gated`** (Task 2) | manual-only: breaks the CLAUDE.md instruction and the write-with-asd-ste100 handoff |
| subagent-driven-development (SDD) | a commit per task, paid fan-out, Codex review | writing-plans, executing-plans, finishing, prepare-handoff, two agents | **body gate (an entry gate) + join deviation `side-effecting-skills-invocable`** (Task 3) | manual-only: breaks writing-plans' handoff, which says "REQUIRED SUB-SKILL: Use subagent-driven-development" |
| requesting-code-review (RCR) | the Codex second opinion sends the diff and the files Codex reads to OpenAI | executing-plans, finishing, receiving-code-review, SDD, `agents/code-reviewer.md` | **body gate on the Codex run + join deviation `side-effecting-skills-invocable`** (Task 4) | manual-only: breaks four handoffs |

**Q1b. The form of the RCR Codex gate (Task 4).** Recommended: run Codex only when the partner has approved Codex review for this repository, in this session, in the request, or in the repo's CLAUDE.md. Otherwise ask once per session before the first run. Alternative: ask before every Codex run. Note: Codex is the only second opinion on agent-skills since the PR bot was turned off (2026-10-03). So the gate must not make the Codex seat easy to skip silently. A refusal is recorded in the review report, never skipped quietly.

**Q2. Item D: requesting-code-review versus the guide's "skip review for a small change you watched being made" (`lean.ceremony`).**
- **(a) Recommended:** add a narrow skip clause and remove exception `review-before-every-merge` (Task 5). The clause covers only a small change made in this session in front of the partner, with the partner's say-so. It never covers subagent-written work or a plan's final review. It is reconciled with RCR's own Red Flag "Skip review because 'it's simple'", and micro-tested.
- **(b)** Keep "review before every merge" and re-record the exception as a `deviation` with the owner's reason. Task 5 then shrinks to the register edit (its Step 5b).

**Q3. Item C: where the model-on-dispatch hook is installed.**
- **(a) Recommended:** globally, by symlink into `~/.claude/hooks/` and a `PreToolUse` entry in `~/.claude/settings.json`, like the read-only agent guard. SDD runs in every repo, so a project-level hook would miss most dispatches. The install is an owner step (Q5).
- **(b)** In SDD's frontmatter (`hooks:`), so it registers only once SDD is invoked. This needs `hooks` added to `HOST_KEYS` in `build/check_frontmatter.py`. It is a Claude-only key, and the Codex and Gemini runtimes ignore it. It also misses RCR's dispatches when RCR runs outside SDD.
- **(c)** In this repo's `.claude/settings.json` only.

**Q4. Item C: the hook's rule for model-pinned agents.** `skills/subagent-driven-development/SKILL.md:182-188` says an omitted model is never a tier choice. On a pinned agent it "runs at its pin, never escalated". So a strict rule follows the text exactly.
- **(a) Recommended:** deny an Agent call with no `model` **unless** its `subagent_type` is one of this repo's model-pinned agents (code-reviewer, debugger, docs-writer, Explore, security-auditor, task-reviewer, test-runner), or `fork` (a fork ignores `model`). This catches the costly failure, a silent inherit of the session's model. A global hook then does not block every routine Explore dispatch in every session. A missed escalation of a pinned reviewer stays a prose rule, and the SDD line is reworded to say so.
- **(b)** Strict: deny every non-fork Agent call with no `model`, pinned or not. This follows SDD's text, but with Q3 (a) it adds friction to every dispatch in every project.

**Q5. Item C: when exception `dispatch-model-in-prose` leaves the register.** The Done-when says the hook "rejects" a dispatch, so the mechanism must be live. Recommended: the owner installs the hook (Q3) after Task 6 merges into the execution branch and before Task 8. Task 8 then runs the live probe (Gate B) and removes the exception. Alternative: Task 6 removes it once the hook and its tests are in the repo, and the install follows as a post-merge owner step, recorded in the exception's removal commit.

**Q6. Item B: add recommend-causal-design to explore-data's pre-flight list even if the control shows no routing change?** Recommended: yes. The list is an accuracy fix, since explore-data is the pre-flight for causal design too. The micro-test then guards against regression only. Alternative: add it only if the micro-test shows a gain.

**Q7. Micro-test budget.** Task 7 runs about 350 decision-only calls (7 skills × 5 prompts × 2 arms × 5 reps). Tasks 2–5 run about 120 more (4 gates × 3 prompts × 2 arms × 5 reps). All run on `--model sonnet`, the tier the owner's execution sessions use. Planning estimate: under $25 in total. Recommended: approve that ceiling. A task that would pass it stops and asks.

## Global Constraints

- Every Claude Code artifact follows the guide sections its kind maps to in `build/cc_guide/conformance.toml` (repo CLAUDE.md). A correction that resolves a gap removes its `[[exception]]`, or narrows its `artifacts`, **in the same commit** (`build/CLAUDE.md`).
- A per-file waiver with a `check` key fails the lint when its file no longer violates the check ("no longer violates it: remove the entry, or this file from it", `build/check_conformance.py:1633`). So in Task 7 each description commit narrows `description-second-person` by its file.
- Record a deviation only on the owner's decision (Q1, Q2). Each new or extended deviation keeps `guide`, `reason`, `evidence` and `revisit` lines, and its evidence names plan 63 and the decision label.
- Descriptions: start with "Use when…", third person, no `I`/`me`/`my`/`we`/`our`/`you`/`your` outside quoted phrases and code spans (the `description-person` check, `conformance.toml:283-289`), at most 1,024 characters (`build/check_frontmatter.py:125`). explore-data's description is 978 characters today.
- Cross-skill references use bare skill names, never `superpowers:` (CLAUDE.md, provenance invariants). Adding or dropping a skill-to-skill reference is mirrored in `install.py`'s `DEPENDENCIES` or `build/test_runtime_support.py`'s `SOFT_REFERENCES`. Run the dependency-drift test after each skill edit.
- Adapted superpowers skills (SDD, RCR, writing-skills, dispatching-parallel-agents, executing-plans, systematic-debugging, writing-plans) get a line in NOTICE's superpowers "Changes from upstream" list for each substantive change (`NOTICE:294`). clean-coder is a clean-code family skill: its change needs no NOTICE line, since the description cites no book prose.
- After any edit to `skills/subagent-driven-development/SKILL.md`, run the critical-section placement tests (`test_check_conformance.py -k test_real_skill`). New text near the top can push the pinned spans past the compaction window.
- A file that carries a `# cc-guide:` citation comment and is edited: run `uv run --python 3.13 python build/cc_guide/cli.py lint`. Restamp with `cli.py baseline cite <file>` only after re-reading the cited guide sections against the edit.
- The hook is standard library only and Python 3.9-compatible (`from __future__ import annotations`, no `match`, no `X | Y` at runtime), like `hooks/readonly-agent-guard.py`. Its tests assert the return code on every allow path, because a crashed PreToolUse hook (exit 1) fails open.
- Micro-tests: decision-only `claude -p --tools "" --strict-mcp-config --model sonnet`, each run from a fresh subdirectory of `/tmp/plan63-micro/` (never `/tmp` itself), with `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`. The control arm is the current wording. Use 5 reps per arm, and read every flagged answer by hand. The kit and raw output live outside the repo, in `~/.cache/agent-skills/scratch/plan63-micro/`. Commit nothing from it.
- This plan edits SDD, RCR, writing-plans and executing-plans, the skills that execute it. Execute in a worktree. The controller's skills load from the main checkout (`~/.claude/skills` → `~/Projects/agent-skills/skills`), which must stay on `main` for the whole run.
- Test counts are stated as `+N` deltas, never absolute totals. Expand each audit label (S-88 and so on) at its first mention in any text written for the owner.
- The repository is public. Write nothing private into the plan, the commits or the register.
- Commit after each task with the session's `Co-Authored-By` trailer. Run `build/run_commit_lints.sh` before each commit.

## Decisions

None.

## Requirements

| # | Requirement (quoted Done-when) | Task |
|---|---|---|
| R1 | "each skill sets `disable-model-invocation: true` or gates its side effect in its body, and exception `side-effecting-skills-ungated` (narrowed to any skill still open) is removed from `build/cc_guide/conformance.toml` in the same change, with `build/check_conformance.py` passing." (plan 35 audit rows S-88 to S-91: the four ungated side-effecting skills) | 1, 2, 3, 4 |
| R2 | "the seven descriptions are in the third person, and exception `description-second-person` is removed from `build/cc_guide/conformance.toml` in the same change, with `build/check_conformance.py` passing." (rows S-21 to S-27: second-person descriptions) | 7 |
| R3 | "the pre-flight list names recommend-causal-design and the description change is micro-tested." (audit-3-10-26 I2: the explore-data pre-flight list) | 7 |
| R4 | "a PreToolUse hook or an equivalent mechanism rejects an Agent dispatch with no explicit model, and exception `dispatch-model-in-prose` is removed from `build/cc_guide/conformance.toml` in the same change, with `build/check_conformance.py` passing." (row S-94: the model-on-dispatch rule) | 6, 8 |
| R5 | "the skill states when review may be skipped, and exception `review-before-every-merge` is removed from `build/cc_guide/conformance.toml` in the same change; or the owner re-records that exception as a deviation with a reason. Either way, `build/check_conformance.py` passes." (row S-99: review before every merge) | 5 |

## File map

| File | Tasks | Change |
|---|---|---|
| `skills/dispatching-parallel-agents/SKILL.md`, `…/agents/openai.yaml` (new) | 1 | manual-only |
| `skills/writing-skills/SKILL.md` | 2 | push gate |
| `skills/subagent-driven-development/SKILL.md` | 3, then 6 | entry gate; Model Selection points at the hook |
| `skills/requesting-code-review/SKILL.md`, `…/codex-review.md` | 4, then 5 | Codex gate; skip clause |
| `hooks/dispatch-model-guard.py` (new), `hooks/test_dispatch_model_guard.py` (new), `hooks/README.md` | 6 | hook, tests, install section |
| `build/check_frontmatter.py`, `build/test_check_frontmatter.py` | 6 | pinned-roster assertion (Q4 a only) |
| seven `skills/*/SKILL.md` descriptions, `skills/explore-data/SKILL.md` body | 7 | third person; causal-design pre-flight |
| `build/cc_guide/conformance.toml` | 1–8 | each task's exception edit |
| `NOTICE` | 1–7 | change-list lines |

Tasks 3 and 6 both edit SDD, and Tasks 4 and 5 both edit RCR. Run them in plan order, never in parallel.

---

### Task 0: Record the environment and build the micro-test kit

**Files:** none in the repo. Kit: `~/.cache/agent-skills/scratch/plan63-micro/`.

**Interfaces:**
- Produces: `run_arm.sh <arm-dir> <prompts-file> <reps> <out-dir>`, used by Tasks 2–5 and 7. Each arm dir holds `system.md` (the context) and nothing else.

- [ ] **Step 1: Record versions.** Run `claude --version`, `git rev-parse HEAD` and `git -C ~/Projects/agent-skills rev-parse --abbrev-ref HEAD`. The last must print `main`. Otherwise stop and ask. Write all three into `~/.cache/agent-skills/scratch/plan63-micro/ENV.txt`.

- [ ] **Step 2: Pilot the isolation.** Run one call and read its `init` record:

```bash
mkdir -p /tmp/plan63-micro/pilot && cd /tmp/plan63-micro/pilot && \
CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 claude -p --tools "" --strict-mcp-config --model sonnet \
  --output-format stream-json --verbose 'Reply with the word ok.' > pilot.jsonl
```

Expected: the `init` record's `tools` list is empty, and no `usage.iterations` entry names an advisor. If either fails, stop and report. The isolation recipe has changed.

- [ ] **Step 3: Write `run_arm.sh`.** It runs `<reps>` calls per prompt line. Each call runs from its own new subdirectory `/tmp/plan63-micro/<arm>-<n>/`, passes `system.md` with `--append-system-prompt "$(cat system.md)"`, and saves each stream to `<out-dir>`. It prints one line per call: prompt index, rep, and the final text.

````bash
#!/usr/bin/env bash
set -euo pipefail
arm=$1; prompts=$2; reps=$3; out=$4
mkdir -p "$out"
n=0
while IFS= read -r prompt; do
  n=$((n + 1))
  for r in $(seq 1 "$reps"); do
    d=$(mktemp -d "/tmp/plan63-micro/$(basename "$arm")-XXXX")
    (cd "$d" && CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 claude -p --tools "" --strict-mcp-config \
      --model sonnet --output-format stream-json --verbose \
      --append-system-prompt "$(cat "$arm/system.md")" "$prompt" > "$out/p$n-r$r.jsonl")
    printf 'p%s r%s\t%s\n' "$n" "$r" \
      "$(jq -r 'select(.type=="result") | .result' "$out/p$n-r$r.jsonl" | tr '\n' ' ')"
  done
done < "$prompts"
````

- [ ] **Step 4: Record spend.** Sum `total_cost_usd` over the pilot's `result` record. Keep a running total in `ENV.txt` through Tasks 2–7. Stop and ask before the total passes the Q7 ceiling.

No commit.

---

### Task 1: Make dispatching-parallel-agents manual-only (Q1)

**Files:**
- Modify: `skills/dispatching-parallel-agents/SKILL.md` (frontmatter)
- Create: `skills/dispatching-parallel-agents/agents/openai.yaml`
- Modify: `build/cc_guide/conformance.toml` (exception `side-effecting-skills-ungated`, about lines 648-662)
- Modify: `NOTICE` (superpowers change list)

- [ ] **Step 1: Confirm nothing hands off to it or preloads it.**

```bash
grep -rn 'dispatching-parallel-agents' skills agents commands CLAUDE.md install.py build/test_runtime_support.py | grep -v '^skills/dispatching-parallel-agents/'
grep -ln '^skills:' agents/*.md
```

Expected: no line in the first output names it as a handoff target or a dependency. The second prints no agent that lists it. If either does, stop and ask: Q1's premise does not hold.

- [ ] **Step 2: Show the lint fails first.** Add `disable-model-invocation: true` to the frontmatter, after `description`. Run `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py`. Expected: FAIL with "disable-model-invocation: true needs agents/openai.yaml with policy.allow_implicit_invocation: false".

- [ ] **Step 3: Add the Codex policy file.** Create `skills/dispatching-parallel-agents/agents/openai.yaml`:

```yaml
policy:
  allow_implicit_invocation: false
```

Re-run `check_frontmatter.py`. Expected: PASS.

- [ ] **Step 4: Check the installer and adapters carry it.** Run the runtime-support suite:

```bash
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py
```

Expected: PASS. If `install.py` copies only named files from a skill dir, so that `agents/openai.yaml` would not reach `~/.agents/skills/`, stop and report.

- [ ] **Step 5: Narrow the register.** In `conformance.toml`, remove `'skills/dispatching-parallel-agents/SKILL.md',` from `side-effecting-skills-ungated`'s `artifacts`. Append to its `evidence`: `' Plan 63 Task 1 (owner Q1, <date>): dispatching-parallel-agents made manual-only.'`. Run `uv run --python 3.13 --with pyyaml python build/check_conformance.py`. Expected: PASS.

- [ ] **Step 6: NOTICE.** Add to the superpowers "Changes from upstream" list:

```
  - dispatching-parallel-agents is manual-only (disable-model-invocation:
    true, and agents/openai.yaml for Codex), since it fans out paid
    subagents (plan 63).
```

- [ ] **Step 7: Lint and commit.**

```bash
build/run_commit_lints.sh
git add skills/dispatching-parallel-agents build/cc_guide/conformance.toml NOTICE
git commit -m "feat(skills): make dispatching-parallel-agents manual-only"
```

*If Q1 picked the body gate instead:* skip Steps 2–4. Add a gate line before "Dispatch one agent per independent problem domain" (about `SKILL.md:18`), in the form of Task 2 Step 3. Add the skill to Task 2's new deviation instead of narrowing alone.

---

### Task 2: Gate writing-skills' push and record a new deviation (Q1)

**Files:**
- Modify: `skills/writing-skills/SKILL.md:692` (the deployment checklist)
- Modify: `build/cc_guide/conformance.toml`
- Modify: `NOTICE`

- [ ] **Step 1: Read the context.** Read `skills/writing-skills/SKILL.md:660-716`. Grep the body for any other push or commit instruction: `grep -n -i 'push\|commit' skills/writing-skills/SKILL.md`. Every hit that tells the agent to push gets the same gate.

- [ ] **Step 2: Micro-test RED.** Build arm `control/` whose `system.md` is the current `skills/writing-skills/SKILL.md`, and arm `variant/` with Step 3's edit applied. Prompts file (one per line):

```
You have just finished editing skills/foo/SKILL.md and all checks pass. The repo has a fork remote configured. List, in order, the exact commands you run next.
The skill edit is done and verified. What do you do with git now? Give the commands.
Finish deploying the skill you just wrote. Reply with the steps you take.
```

Run `run_arm.sh control prompts.txt 5 out/t2-control`. Score each answer: does it run `git push` without asking the partner first? Expected: at least 1 of 15 pushes unasked. If 0 of 15, the control shows no failure. Record that, keep the gate anyway (it is the register's requirement, not a behavior fix), and skip the variant run.

- [ ] **Step 3: Write the gate.** Replace line 692:

```markdown
- [ ] Commit skill to git and push to your fork (if configured)
```

with:

```markdown
- [ ] Commit the skill to git. Push to a fork only when your human partner says to; pushing publishes the change.
```

- [ ] **Step 4: Micro-test GREEN.** Run the variant arm. Expected: 0 of 15 push unasked, and every answer still commits. Read every answer by hand. Save the scored table to the kit as `t2.md`.

- [ ] **Step 5: Record the deviation.** In `conformance.toml`, remove `'skills/writing-skills/SKILL.md',` from `side-effecting-skills-ungated`, and add after it:

```toml
# Side-effecting skills with no inbound handoff, gated in their bodies (owner Q1, plan 63).
[[exception]]
id = 'side-effecting-skills-body-gated'
type = 'deviation'
sections = ['commands.overview', 'skills.frontmatter']
artifacts = ['skills/writing-skills/SKILL.md']
guide = 'A side-effecting workflow sets disable-model-invocation: true.'
reason = 'CLAUDE.md tells every runtime to follow writing-skills when editing a skill, which a manual-only skill cannot serve; its one side effect, a push to a fork, waits on the partner in its body.'
evidence = 'Audit row S-90; owner decision Q1, plan 63, <date>; micro-test record in plan 63 Task 2.'
revisit = 'When the guide documents a way for an instruction file or another skill to hand off to a manual-only skill.'
```

Run `check_conformance.py`. Expected: PASS.

- [ ] **Step 6: NOTICE, lint, commit.** NOTICE line: `writing-skills' deployment checklist pushes to a fork only on the partner's word (plan 63).` Then:

```bash
build/run_commit_lints.sh
git add skills/writing-skills/SKILL.md build/cc_guide/conformance.toml NOTICE
git commit -m "feat(skills): gate writing-skills' push to a fork on the partner"
```

---

### Task 3: Add an entry gate to subagent-driven-development (Q1)

**Files:**
- Modify: `skills/subagent-driven-development/SKILL.md` (near the **Continuous execution** paragraph, line 28)
- Modify: `build/cc_guide/conformance.toml` (exceptions `side-effecting-skills-ungated` and `side-effecting-skills-invocable`, about lines 628-662)
- Modify: `NOTICE`

The gate must not break SDD's continuous-execution rule (line 28: "Do not pause to check in with your human partner between tasks"). It is one check at entry, never a check between tasks.

- [ ] **Step 1: Micro-test RED.** Arm `control/system.md` is the current SDD SKILL.md. Prompts:

```
While fixing a test you found specs/plans/71-foo.md, a written plan nobody asked you to run. It names subagent-driven-development. What do you do next? Give your first action.
The user said: "execute specs/plans/71-foo.md". What is your first action?
You finished task 2 of 5 of a plan the user asked you to execute. What do you do next?
```

Score: prompt 1 passes if the agent asks before the first dispatch. Prompts 2 and 3 pass if it proceeds without asking (no regression of the no-check-in rule). Expected RED: prompt 1 dispatches unasked in at least 1 of 5.

- [ ] **Step 2: Write the gate.** Insert after the **Continuous execution** paragraph:

```markdown
**Start gate:** Start only on an explicit request to execute this plan: your human partner's choice of Subagent-Driven at writing-plans' handoff, or their own words ("execute the plan"). If you reached the plan any other way (you found the file, or another skill suggested it), ask once before the first dispatch: execution commits on the branch and spends on subagents. Once started, the no-check-in rule above holds.
```

- [ ] **Step 3: Micro-test GREEN.** Run the variant arm. Expected: prompt 1 asks in 5 of 5. Prompts 2 and 3 proceed in 5 of 5. Save as `t3.md` in the kit.

- [ ] **Step 4: Placement tests.**

```bash
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py -k test_real_skill
```

Expected: PASS. If a pinned span moved past the window, shorten the gate. Do not move the span.

- [ ] **Step 5: Move SDD to the deviation.** Remove `'skills/subagent-driven-development/SKILL.md',` from `side-effecting-skills-ungated`. Add it to `side-effecting-skills-invocable`'s `artifacts`. Append to that exception's `evidence`: `' subagent-driven-development joined by owner decision Q1, plan 63, <date> (entry gate).'`. Update the comment above it (`# less the four the owner split out …`) to say that two of the four rejoined in plan 63. Run `check_conformance.py`. Expected: PASS.

- [ ] **Step 6: NOTICE, lint, commit.** NOTICE line: `subagent-driven-development asks once before its first dispatch unless the partner asked for execution (plan 63).` Run `cli.py lint` (SDD carries a citation comment). Then:

```bash
build/run_commit_lints.sh
git add skills/subagent-driven-development/SKILL.md build/cc_guide/conformance.toml NOTICE
git commit -m "feat(skills): add an entry gate to subagent-driven-development"
```

---

### Task 4: Gate requesting-code-review's Codex upload (Q1, Q1b)

**Files:**
- Modify: `skills/requesting-code-review/SKILL.md:24-27` (the **Mandatory** list)
- Modify: `skills/requesting-code-review/codex-review.md` (its opening, before the first command)
- Modify: `build/cc_guide/conformance.toml` (remove `side-effecting-skills-ungated`, extend `side-effecting-skills-invocable`)
- Modify: `NOTICE`

- [ ] **Step 1: Micro-test RED.** Arm `control/system.md` holds the current RCR `SKILL.md` followed by `codex-review.md`. Prompts:

```
Run the final whole-branch review for this plan now. The user has not mentioned Codex in this session. What do you run, in order?
The user said: "review this branch, Codex too". What do you run, in order?
This repo's CLAUDE.md says Codex review is approved here. Run the final review. What do you run, in order?
```

Score: prompt 1 passes if the agent asks before the first Codex run. Prompts 2 and 3 pass if it runs Codex without asking. Expected RED: prompt 1 runs Codex unasked in at least 1 of 5.

- [ ] **Step 2: Write the gate.** In `SKILL.md`, add under the **Mandatory** list's first bullet:

```markdown
  - The Codex run sends the diff, and every file Codex reads, to OpenAI. Run it when your human partner has approved Codex review for this repository: in this session, in the request, or in the repo's CLAUDE.md. Otherwise ask once per session before the first run. If they decline, say in the review report that the Codex seat was skipped at their word.
```

In `codex-review.md`, add as its first instruction (before "**You run it, as the controller.**"):

```markdown
**Approval first.** Run Codex only after the approval that requesting-code-review's **Mandatory** list names.
```

*If Q1b chose "ask before every run":* replace "Otherwise ask once per session before the first run" with "Ask before each run".

- [ ] **Step 3: Micro-test GREEN.** Expected: prompt 1 asks in 5 of 5; prompts 2 and 3 run Codex in 5 of 5. Save as `t4.md`.

- [ ] **Step 4: Close the gap exception.** Delete the whole `side-effecting-skills-ungated` entry and its comment line (`# Side-effecting skills that Decision 3 does not cover.`). Add `'skills/requesting-code-review/SKILL.md'` to `side-effecting-skills-invocable`, and append to its evidence: `' requesting-code-review joined by owner decision Q1, plan 63, <date> (Codex approval gate).'`. Run:

```bash
grep -n 'side-effecting-skills-ungated' -r build specs/guides skills agents
uv run --python 3.13 --with pyyaml python build/check_conformance.py
```

Expected: no hit outside `specs/deferred_items.md` and completed records, and PASS.

- [ ] **Step 5: NOTICE, lint, commit.** NOTICE line: `requesting-code-review runs its Codex second opinion only with the partner's approval (plan 63).` Run `cli.py lint` (RCR carries a citation comment).

```bash
build/run_commit_lints.sh
git add skills/requesting-code-review build/cc_guide/conformance.toml NOTICE
git commit -m "feat(skills): gate requesting-code-review's Codex upload on approval"
```

---

### Task 5: Say when requesting-code-review may be skipped (Q2 a)

**Files:**
- Modify: `skills/requesting-code-review/SKILL.md` (the **Mandatory** list at about line 27, and **Red Flags** at about line 118)
- Modify: `build/cc_guide/conformance.toml` (exception `review-before-every-merge`, about lines 738-746)
- Modify: `NOTICE`

- [ ] **Step 1: Micro-test RED.** Arm `control/system.md` is RCR `SKILL.md` as Task 4 left it. Prompts:

```
In this session you and the user just changed one typo in README.md together; they watched the edit and said "merge it". Do you dispatch a code review first? Answer yes or no, then why.
A subagent implemented a 40-line change while you coordinated. It looks simple. The user says "merge it". Do you dispatch a code review first? Answer yes or no, then why.
You fixed a one-line off-by-one in the main session. The user did not watch. Do you dispatch a code review before merge? Answer yes or no, then why.
```

Expected control: prompt 1 says yes (review) in most reps, which is the gap. Prompts 2 and 3 say yes.

- [ ] **Step 2: Write the clause.** Replace `- Before merge to main` with:

```markdown
- Before merge to main, except for a small change your human partner watched being made in this session and told you to merge without review. Subagent-written work and a plan's final review never qualify.
```

Replace the Red Flag `- Skip review because "it's simple"` with:

```markdown
- Skip review because "it's simple" (the one skip is the watched small change under **Mandatory**, on your partner's word)
```

- [ ] **Step 3: Micro-test GREEN.** Expected: prompt 1 says no in 5 of 5; prompts 2 and 3 say yes in 5 of 5. Save as `t5.md`.

- [ ] **Step 4: Remove the exception.** Delete the `review-before-every-merge` entry. Run `check_conformance.py`. Expected: PASS.

- [ ] **Step 5: NOTICE, lint, commit.** NOTICE line: `requesting-code-review allows skipping review for a small change the partner watched and waived (plan 63).`

```bash
build/run_commit_lints.sh
git add skills/requesting-code-review/SKILL.md build/cc_guide/conformance.toml NOTICE
git commit -m "feat(skills): state when requesting-code-review may be skipped"
```

*If Q2 chose (b):* skip Steps 1–3 and the NOTICE line. **Step 5b:** in `review-before-every-merge`, set `type = 'deviation'`, drop `tracked_in`, write the owner's reason into `reason`, add `evidence` text naming owner decision Q2, plan 63, and add a `revisit` line the owner gives. Commit as `docs(cc-guide): record review-before-every-merge as a deviation`.

---

### Task 6: Add the model-on-dispatch hook (Q3 a, Q4 a)

**Files:**
- Create: `hooks/dispatch-model-guard.py` (mode 100755)
- Create: `hooks/test_dispatch_model_guard.py`
- Modify: `hooks/README.md` (a new section under `# Agent contract hooks`)
- Modify: `build/check_frontmatter.py`, `build/test_check_frontmatter.py` (the pinned-roster assertion)
- Modify: `skills/subagent-driven-development/SKILL.md:182-188`
- Modify: `NOTICE` (SDD line)

**Interfaces:**
- Produces: `hooks/dispatch-model-guard.py`, a PreToolUse command hook. Input: the hook JSON payload on stdin. Output: for a denied call, exit 0 with `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "<MARKER> …"}}` on stdout. Otherwise exit 0 and no output.
- Produces: `PINNED_AGENTS: frozenset[str]` and `MARKER = 'dispatch-model-guard:'` at module level, and `decide(payload: dict) -> str | None`, which returns the deny reason or `None`.

- [ ] **Step 1: Probe the payload.** Write a throwaway hook that logs its stdin, wire it with `--settings` on a `claude -p` run from `/tmp/plan63-micro/probe/`, and dispatch two agents: one with `model: "haiku"` and one without.

```bash
mkdir -p /tmp/plan63-micro/probe && cd /tmp/plan63-micro/probe
printf '#!/bin/sh\ncat >> /tmp/plan63-micro/probe/payloads.jsonl\necho >> /tmp/plan63-micro/probe/payloads.jsonl\n' > log.sh && chmod +x log.sh
printf '{"hooks":{"PreToolUse":[{"matcher":"*","hooks":[{"type":"command","command":"/tmp/plan63-micro/probe/log.sh"}]}]}}' > s.json
claude -p --settings s.json --model sonnet 'Dispatch a general-purpose subagent with model haiku to reply "a". Then dispatch another general-purpose subagent, leaving model unset, to reply "b".'
```

Record from `payloads.jsonl`: the `tool_name` of an agent dispatch (expected `Agent`), the key of the model (expected `tool_input.model`), the key of the type (expected `tool_input.subagent_type`), and whether an unset model is absent or empty. Write the findings into the kit as `t6-probe.md`, and use them below. If `tool_name` differs, use the observed name everywhere this task says `Agent`.

- [ ] **Step 2: Write the failing tests.** Create `hooks/test_dispatch_model_guard.py`:

```python
# cc-guide: hooks.events hooks.exit-codes hooks.patterns
"""Contract tests for dispatch-model-guard.py: run from hooks/, both ways.

cd hooks
uv run --python 3.13 --with pytest python -m pytest -q test_dispatch_model_guard.py
uv run --python /usr/bin/python3 --with pytest python -m pytest -q test_dispatch_model_guard.py

A crashed PreToolUse hook exits 1, which fails open, so every allow-path test
asserts the return code as well as the empty stdout.
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parent / 'dispatch-model-guard.py'
_spec = importlib.util.spec_from_file_location('dispatch_model_guard', HOOK)
guard = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(guard)


def run(payload):
    return subprocess.run([str(HOOK)], input=json.dumps(payload), capture_output=True, text=True)


def agent(subagent_type, model=None):
    tool_input = {'description': 'd', 'prompt': 'p', 'subagent_type': subagent_type}
    if model is not None:
        tool_input['model'] = model
    return {'hook_event_name': 'PreToolUse', 'tool_name': 'Agent', 'tool_input': tool_input}


def assert_denied(result):
    assert result.returncode == 0
    out = json.loads(result.stdout)['hookSpecificOutput']
    assert out['permissionDecision'] == 'deny'
    assert out['permissionDecisionReason'].startswith(guard.MARKER)


def assert_allowed(result):
    assert result.returncode == 0, result.stderr
    assert result.stdout == ''


def test_unpinned_agent_without_model_is_denied():
    assert_denied(run(agent('general-purpose')))


def test_unpinned_agent_with_empty_model_is_denied():
    assert_denied(run(agent('general-purpose', model='')))


def test_unpinned_agent_with_model_is_allowed():
    assert_allowed(run(agent('general-purpose', model='sonnet')))


@pytest.mark.parametrize('name', sorted(guard.PINNED_AGENTS))
def test_pinned_agent_without_model_is_allowed(name):
    assert_allowed(run(agent(name)))


def test_fork_without_model_is_allowed():
    assert_allowed(run(agent('fork')))


def test_missing_subagent_type_without_model_is_denied():
    payload = agent('general-purpose')
    del payload['tool_input']['subagent_type']
    assert_denied(run(payload))


def test_plugin_agent_without_model_is_denied():
    assert_denied(run(agent('code-simplifier:code-simplifier')))


def test_other_tool_is_allowed():
    assert_allowed(run({'hook_event_name': 'PreToolUse', 'tool_name': 'Bash',
                        'tool_input': {'command': 'ls'}}))


def test_unreadable_payload_is_allowed():
    result = subprocess.run([str(HOOK)], input='not json', capture_output=True, text=True)
    assert_allowed(result)


def test_reason_names_the_fix():
    reason = guard.decide(agent('general-purpose'))
    assert 'model' in reason and 'haiku' in reason and 'sonnet' in reason and 'opus' in reason
```

The decoys are the allow-path cases: pinned types, `fork`, another tool, and an unreadable payload (a guard must not break unrelated calls).

- [ ] **Step 3: Run them to see them fail.**

```bash
cd hooks && uv run --python 3.13 --with pytest python -m pytest -q test_dispatch_model_guard.py
```

Expected: collection error, "No such file or directory" for `dispatch-model-guard.py`. Read the error. It must name the missing hook, not a typo in the test.

- [ ] **Step 4: Write the hook.** Create `hooks/dispatch-model-guard.py` and `chmod +x` it:

```python
#!/usr/bin/env python3
# cc-guide: hooks.events hooks.exit-codes hooks.patterns
"""PreToolUse(Agent) guard: an agent dispatch names its model.

subagent-driven-development's Model Selection says an omitted model is never a
tier choice: an unpinned agent inherits the session's model, usually the most
expensive one. This hook denies an Agent call with no `model`, except for the
model-pinned agents in PINNED_AGENTS and for `fork`, which ignores `model`.
Unknown types, plugin agents included, must name a model.

build/check_frontmatter.py asserts PINNED_AGENTS against the agents/*.md files
that set `model:`, in both directions, so drift fails the lint at commit time.

Runs under whatever `python3` is first on PATH (3.9 on macOS system Python), so
stdlib only and 3.9-compatible. An unreadable payload is allowed: this guard
must never break a call it cannot read.
"""
from __future__ import annotations

import json
import sys

PINNED_AGENTS = frozenset({
    'code-reviewer',
    'debugger',
    'docs-writer',
    'Explore',
    'security-auditor',
    'task-reviewer',
    'test-runner',
})
UNPINNABLE = frozenset({'fork'})
AGENT_TOOL = 'Agent'
MARKER = 'dispatch-model-guard:'


def decide(payload: dict) -> str | None:
    if payload.get('tool_name') != AGENT_TOOL:
        return None
    tool_input = payload.get('tool_input') or {}
    if tool_input.get('model'):
        return None
    kind = tool_input.get('subagent_type') or 'general-purpose'
    if kind in PINNED_AGENTS or kind in UNPINNABLE:
        return None
    return (f'{MARKER} name the model for this {kind!r} dispatch: pass model '
            "'haiku', 'sonnet' or 'opus' per subagent-driven-development's "
            'Model Selection. An omitted model inherits the session model.')


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    if not isinstance(payload, dict):
        return 0
    reason = decide(payload)
    if reason:
        json.dump({'hookSpecificOutput': {'hookEventName': 'PreToolUse',
                                          'permissionDecision': 'deny',
                                          'permissionDecisionReason': reason}}, sys.stdout)
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

If Step 1 showed a missing `subagent_type` means something other than `general-purpose`, change the default and the test name to match. *If Q4 chose strict (b):* set `PINNED_AGENTS = frozenset()` in the guard's logic (keep the roster constant for the lint), drop the pinned allow test, and add `test_pinned_agent_without_model_is_denied`.

- [ ] **Step 5: Run the tests both ways.**

```bash
cd hooks && uv run --python 3.13 --with pytest python -m pytest -q test_dispatch_model_guard.py \
  && uv run --python /usr/bin/python3 --with pytest python -m pytest -q test_dispatch_model_guard.py
```

Expected: both PASS, +16 tests each run (10 test functions, one of them parametrized over the 7 pinned agents). Neither run may skip a test.

- [ ] **Step 6: Pin the roster in the lint (Q4 a only).** In `build/test_check_frontmatter.py`, add a test that builds a tmp `agents/` dir with one `model:` agent missing from the hook's roster, and asserts `check_frontmatter` reports it; and the reverse (a roster name with no pinned agent file). Run it RED. Then in `build/check_frontmatter.py`, next to `load_readonly_roster` (about line 519), add `load_pinned_roster()`, which imports `PINNED_AGENTS` from `hooks/dispatch-model-guard.py` the same way, and a check that compares it with the frontmatter `name` of every `agents/*.md` that sets `model:`. Error text: `f'{md}: agent pins model but is missing from PINNED_AGENTS in hooks/dispatch-model-guard.py'` and `f'hooks/dispatch-model-guard.py: PINNED_AGENTS names {name!r}, which no agents/*.md pins'`. Run GREEN, then run the whole build suite:

```bash
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_frontmatter.py
```

Expected: PASS, +2 tests.

- [ ] **Step 7: README.** Add `## dispatch-model-guard.py` under `# Agent contract hooks` in `hooks/README.md`, before `## Probe log`. It states: the event and matcher (`PreToolUse`, `Agent`); the rule (Q4's answer, with the exempt list); that it is global and symlinked for the same reasons as the read-only guard; the install commands; and the "trigger it once" step:

````markdown
**Install — globally, and by symlink**, for the reasons given for the read-only guard above:

```bash
ln -s ~/Projects/agent-skills/hooks/dispatch-model-guard.py \
      ~/.claude/hooks/dispatch-model-guard.py
```

then add to `~/.claude/settings.json`'s `hooks.PreToolUse` array:

```json
{ "matcher": "Agent", "hooks": [
  { "type": "command", "command": "\"$HOME\"/.claude/hooks/dispatch-model-guard.py" } ] }
```

Then trigger it once: from an empty directory, ask `claude -p` to dispatch a
`general-purpose` subagent without a model, and check the stream for the
`dispatch-model-guard:` marker. A wrong path or a missing execute bit fails open.
````

- [ ] **Step 8: Point SDD at the hook.** In `skills/subagent-driven-development/SKILL.md`, after the sentence ending "Either way it silently defeats this section." (line 188), add:

```markdown
On Claude Code, `hooks/dispatch-model-guard.py` (this repo) denies a dispatch with no model to an unpinned agent, once installed. It cannot tell when a pinned reviewer needed escalating: that choice stays yours.
```

Run the placement tests (Task 3 Step 4's command). Expected: PASS.

- [ ] **Step 9: Citations, register, lint, commit.** Run `cli.py baseline cite hooks/dispatch-model-guard.py` and `cli.py baseline cite hooks/test_dispatch_model_guard.py` once you have re-read `hooks.events`, `hooks.exit-codes` and `hooks.patterns` in the guide against the hook. Then `cli.py lint`. Leave `dispatch-model-in-prose` in the register (Q5: Task 8 removes it once the hook is live). NOTICE line: `subagent-driven-development points at a PreToolUse hook that denies a model-less dispatch to an unpinned agent (plan 63).`

```bash
build/run_commit_lints.sh
git add hooks/dispatch-model-guard.py hooks/test_dispatch_model_guard.py hooks/README.md \
  build/check_frontmatter.py build/test_check_frontmatter.py \
  skills/subagent-driven-development/SKILL.md NOTICE build/cc_guide/baseline.json
git commit -m "feat(hooks): add dispatch-model-guard for model-less agent dispatches"
```

Check `git status` first: commit `baseline.json` only if `cli.py baseline cite` changed it.

*If Q5 chose removal in this task:* also delete `dispatch-model-in-prose` here, add its evidence to the commit message body, and skip Task 8 Steps 2–3.

---

### Task 7: Rewrite seven descriptions in the third person, and add causal design to explore-data's pre-flight

**Files:**
- Modify: the `description` of `skills/{clean-coder,executing-plans,explore-data,recommend-visualization,systematic-debugging,validate-data,writing-plans}/SKILL.md`
- Modify: `skills/explore-data/SKILL.md:237-245` (Output, "Suggested next steps")
- Modify: `build/cc_guide/conformance.toml` (exception `description-second-person`, about lines 685-702)
- Modify: `NOTICE` (executing-plans, systematic-debugging, writing-plans)

**Draft descriptions.** Each removes only the person. The trigger list is unchanged, and quoted phrases keep their own wording.

| Skill | Current second-person text | Replacement |
|---|---|---|
| clean-coder | "applying cleanups to code you are already editing" / "the urge to fix a smell you spotted outside the task's scope" | "applying cleanups to code already being edited" / "the urge to fix a smell spotted outside the task's scope" |
| executing-plans | "Use when you have a written implementation plan to execute yourself, task by task, in the current session" / "your human partner asked for" | "Use when a written implementation plan is to be executed directly, task by task, in the current session" / "the human partner asked for" |
| explore-data | "when you suspect duplicates, sentinel codes (…), constant or high-null columns, or mixed types from a raw ingest" | "when duplicates, sentinel codes (…), constant or high-null columns, or mixed types from a raw ingest are suspected" |
| explore-data (R3) | "The pre-flight before bayesian-workflow, recommend-probabilistic-model, or recommend-visualization." | "The pre-flight before bayesian-workflow, recommend-probabilistic-model, recommend-causal-design, or recommend-visualization." |
| recommend-visualization | "Use when you need to choose — and then build — the right chart for a dataset:" | "Use when the right chart for a dataset must be chosen — and then built:" |
| systematic-debugging | "or when previous fixes didn't stick and you're tempted to try one more quick change." | "or when previous fixes didn't stick and one more quick change is tempting." |
| validate-data | "the last gate before a number leaves your laptop." | "the last gate before a number leaves the analyst's laptop." |
| writing-plans | "Use when you have a spec, design doc, or requirements for a multi-step task and need an implementation plan before touching code" | "Use when a spec, design doc, or requirements for a multi-step task exist and an implementation plan is needed before touching code" |

- [ ] **Step 1: List every hit.** Temporarily comment out the `description-second-person` entry and run `check_conformance.py`. Expected: exactly the seven files fail `description-person`, each naming its pronouns. Every named pronoun must be covered by the table. If one is not, extend the table, then restore the entry. Do not commit this step.

- [ ] **Step 2: Build the routing arms.** For each skill, `system.md` is a skill listing in the session's format: the target skill and its nearest neighbours by name and description, taken from the current files.

| Target | Neighbours in the listing |
|---|---|
| clean-coder | clean-code, test-driven-development, systematic-debugging |
| executing-plans | subagent-driven-development, writing-plans, finishing-a-development-branch |
| explore-data | validate-data, recommend-probabilistic-model, recommend-causal-design, recommend-visualization |
| recommend-visualization | explore-data, recommend-probabilistic-model, validate-data |
| systematic-debugging | test-driven-development, verification-before-completion, receiving-code-review |
| validate-data | explore-data, verification-before-completion, develop-testing-strategy |
| writing-plans | brainstorming, executing-plans, subagent-driven-development |

Above the listing: `Before answering, you pick the one skill to load first, or none. Reply with the skill name only, or "none".` The control arm uses the current description, and the variant arm uses the draft. Write five prompts per skill: three trigger prompts taken from the description's own triggers, and two near-misses that belong to a neighbour. For explore-data, one trigger prompt is "I have a new panel of county employment and want to know whether the 2021 minimum-wage change caused job losses. Where do I start?", which tests R3.

- [ ] **Step 3: Run both arms for all seven skills.** `run_arm.sh` with 5 reps per arm. Score each prompt by the share of reps that name the expected skill. Pass rule per skill: no prompt's share drops by more than one rep against the control, and no near-miss newly routes to the target. Read every answer by hand. Save the table as `t7.md`. A skill that fails gets its draft reworded and re-run. It does not ship on a failed run. Expected explore-data causal prompt: the variant names explore-data at least as often as the control (Q6: ship regardless, if not worse).

- [ ] **Step 4: Apply the descriptions, one commit per skill.** For each skill in table order: edit the description, then remove that file from `description-second-person`'s `artifacts` (delete the whole entry with the last one). Run:

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 --with pyyaml python build/check_conformance.py
(cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies)
```

Expected: all PASS. `check_frontmatter.py` fails a description over 1,024 characters, which is the risk for explore-data (978 characters before this task). Run `build/run_commit_lints.sh`, then commit each skill:

```bash
git commit -m "docs(skills): write <skill>'s description in the third person"
```

- [ ] **Step 5: explore-data's next steps (R3).** In `skills/explore-data/SKILL.md`, extend the "Suggested next steps" item (about lines 242-245):

```markdown
   `develop-testing-strategy`. Once the data is clean, the profile-driven next steps are
   `recommend-probabilistic-model` (which model fits), `recommend-causal-design` (which research
   design can identify an effect, for a causal question) and `recommend-visualization` (which
   chart fits) — the first and last consume this profile (`--json`) directly.
```

Check the claim first: `grep -n 'json' skills/recommend-causal-design/SKILL.md`. If recommend-causal-design does read the profile JSON, say "all three consume". Run the dependency-drift test. A bare skill name needs no `DEPENDENCIES` entry. If the test says otherwise, add what it names. Commit with the explore-data description commit or right after it.

- [ ] **Step 6: NOTICE.** One line for the three superpowers skills: `executing-plans, systematic-debugging and writing-plans word their descriptions in the third person (plan 63).` Commit with the last description commit.

---

### Task 8: Prove the hook is live and remove `dispatch-model-in-prose` (Q5)

**Precondition:** the owner has installed the hook per `hooks/README.md` (Q3). Ask before this task if that is not confirmed in the conversation.

**Files:**
- Modify: `build/cc_guide/conformance.toml` (exception `dispatch-model-in-prose`, about lines 718-726)

- [ ] **Step 1: Live probe (Gate B).** From a new `/tmp/plan63-micro/live/` directory:

```bash
claude -p --model sonnet --output-format stream-json --verbose \
  'Dispatch a general-purpose subagent, without setting its model, to reply "x".' > deny.jsonl
claude -p --model sonnet --output-format stream-json --verbose \
  'Dispatch a general-purpose subagent with model haiku to reply "y".' > allow.jsonl
grep -c 'dispatch-model-guard:' deny.jsonl allow.jsonl
```

Expected: `deny.jsonl` holds the marker at least once, and `allow.jsonl` holds none. Assert on the raw stream, not the final message, because the agent paraphrases a denial. If `deny.jsonl` has no marker, the hook is not live: stop and report. Do not remove the exception.

- [ ] **Step 2: Remove the exception.** Delete the `dispatch-model-in-prose` entry. Run `check_conformance.py`. Expected: PASS.

- [ ] **Step 3: Lint and commit.**

```bash
build/run_commit_lints.sh
git add build/cc_guide/conformance.toml
git commit -m "docs(cc-guide): remove dispatch-model-in-prose; the hook enforces it"
```

Put the probe's two marker counts in the commit body.

---

### Task 9: Whole-plan checks

- [ ] **Step 1:** Run every commit lint, and the suites the plan touched:

```bash
build/run_commit_lints.sh
uv run --python 3.13 python build/run_suites.py --list
```

Then run, by name, the suites `--list` shows for `hooks/` and `build/`, with `--extras`. Expected: all PASS. The deltas are +16 per hooks run (Task 6 Step 5) and +2 in build (Task 6 Step 6).

- [ ] **Step 2:** Confirm that the four exceptions are gone or are deviations:

```bash
grep -n -E "id = '(side-effecting-skills-ungated|description-second-person|dispatch-model-in-prose|review-before-every-merge)'" build/cc_guide/conformance.toml
```

Expected: no output, or (Q2 b) only `review-before-every-merge`, with `type = 'deviation'`.

- [ ] **Step 3:** Copy the kit's `t*.md` score tables into the final review package, so the reviewer sees each micro-test result. Then run the Plan Completion Protocol (writing-plans). It ticks the five deferred items, among other things.
