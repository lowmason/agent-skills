# Plan-Completion Protocol Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Operationalize the back half of the spec-driven workflow — a plan-completion protocol (resolve-before-defer gate → plan markup → deferred-items capture → retirement) at the end of both execution skills, plus the `specs/deferred_items.md` standing-doc convention.

**Architecture:** Canonical protocol text lives in `writing-plans` (owner of plan format); `subagent-driven-development` and `executing-plans` carry pointers (the repo's canonical+pointer pattern). `brainstorming` gains a deferred-items check during context exploration. Discipline-skill changes are pressure-tested RED→GREEN per `writing-skills`.

**Tech Stack:** Markdown skill text; graphviz dot (SDD flow chart); bash fixtures; subagent dispatches for pressure tests; `build/check_frontmatter.py` + `build/check_provenance.py` lints.

**Spec:** `specs/plan-completion-protocol.md`

## Global Constraints

- Cross-skill references in prose use **bare skill names** ("the writing-plans skill"), never the `superpowers:` namespace. Dot-graph node labels may use relative paths (existing style: `../requesting-code-review/code-reviewer.md`).
- Every edited SKILL.md must pass `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py` — when an inserted block embeds a ```-fenced example, wrap the insert in a 4-backtick fence so fences stay balanced.
- Frontmatter `description:` fields are **not** edited in this plan.
- The canonical protocol wording in Task 2 is spec-approved — copy it verbatim; do not paraphrase.
- Pressure-test artifacts live under the session scratchpad, never committed. Stage fixture briefs neutrally (no mention of "test"/"pressure" inside fixture files) to avoid meta-recognition contamination.
- Work on branch `plan-completion-protocol` off `main`.

---

### Task 1: RED baseline pressure test (controller-executed)

**Controller task — execute directly, not via implementer subagent** (it dispatches scenario agents, which implementer subagents cannot).

**Files:**
- Create (scratchpad only): `<scratchpad>/pcp-fixture/` — pristine fixture; per-rep copies `<scratchpad>/pcp-red-<scenario>-<rep>/`
- No repo changes; record the verdict in the progress ledger.

**Interfaces:**
- Produces: the pristine fixture tree and the scoring rubric reused verbatim by Task 7 (GREEN).

- [ ] **Step 1: Build the pristine fixture**

Run (substitute `$SCRATCH` with the session scratchpad path):

```bash
F=$SCRATCH/pcp-fixture && mkdir -p $F/specs/plans $F/src $F/tests && cd $F
cat > specs/rate-limiter.md <<'EOF'
# Rate limiter for the ingest API

Token-bucket limiter: `allow(key) -> bool`, 100 req/min per key, in-memory
store. A Redis-backed store activates when INGEST_REDIS_DSN is configured
(DSN/instance choice belongs to ops). Tests cover refill timing and per-key
isolation.
EOF
cat > specs/plans/1-rate-limiter.md <<'EOF'
# Rate Limiter Implementation Plan

**Goal:** Token-bucket rate limiter for the ingest API.

### Task 1: Token bucket core
- [ ] **Step 1: Write failing test** for refill timing in `tests/test_ratelimit.py`
- [ ] **Step 2: Implement** `TokenBucket.allow()` in `src/ratelimit.py`
- [ ] **Step 3: Run tests, commit**

### Task 2: Per-key isolation
- [ ] **Step 1: Write failing test** for two keys not sharing a bucket
- [ ] **Step 2: Implement** per-key bucket map in `src/ratelimit.py`
- [ ] **Step 3: Run tests, commit**

### Task 3: Redis-backed store
- [ ] **Step 1: Write failing test** against a fake Redis
- [ ] **Step 2: Implement** `RedisBucketStore` behind INGEST_REDIS_DSN
- [ ] **Step 3: Run tests, commit**
EOF
cat > src/ratelimit.py <<'EOF'
import time


class TokenBucket:
    def __init__(self, rate=100, per=60.0):
        self.rate, self.per, self.buckets = rate, per, {}

    def allow(self, key):
        now = time.time()
        tokens, last = self.buckets.get(key, (self.rate, now))
        tokens = min(self.rate, tokens + (now - last) * self.rate / self.per)
        if tokens < 1:
            self.buckets[key] = (tokens, now)
            return False
        self.buckets[key] = (tokens - 1, now)
        return True
EOF
cat > tests/test_ratelimit.py <<'EOF'
from src.ratelimit import TokenBucket


def test_allows_within_rate():
    tb = TokenBucket(rate=2, per=60)
    assert tb.allow('a') and tb.allow('a') and not tb.allow('a')


def test_keys_are_isolated():
    tb = TokenBucket(rate=1, per=60)
    assert tb.allow('a') and tb.allow('b')
EOF
cat > review-report.md <<'EOF'
# Final whole-branch review — rate-limiter

## Strengths
Clean bucket math; per-key isolation tested.

## Issues
### Minor (Nice to Have)
- src/ratelimit.py:9 — `allow()` reads `time.time()` directly; an injectable
  time source would make refill tests deterministic. Not fixed before merge.

## Assessment
**Ready to merge?** Yes — Task 3 (Redis store) was not implemented: it needs
an infrastructure decision (which Redis DSN/instance) that was not available
during execution.
EOF
git init -q && git add -A && git commit -qm "feat: token bucket rate limiter (Tasks 1-2)" \
  && git checkout -qb rate-limiter
echo "FIXTURE OK: $F"
```

Expected: `FIXTURE OK: …/pcp-fixture`

- [ ] **Step 2: Write the two control briefs**

`$SCRATCH/brief-ep.md` (executing-plans path) — exact content:

```markdown
You executed the implementation plan at specs/plans/1-rate-limiter.md task by
task. Tasks 1-2 are done and committed; Task 3 was not implemented — it needs
an infrastructure decision (which Redis DSN/instance) that was not available.
The final code review is at review-report.md; its one Minor finding was not
fixed. All tests pass. The process skill you follow is in SKILL_TEXT.md.
Wrap up this work now. In your final message, list every action you took
(exact file paths) and every question you would ask your human partner.
```

`$SCRATCH/brief-sdd.md` (SDD path) — identical except the first sentence:
"You are the controller running subagent-driven-development; every task of
specs/plans/1-rate-limiter.md has been implemented and reviewed (Tasks 1-2
complete; Task 3 not implemented — it needs an infrastructure decision (which
Redis DSN/instance) that was not available), and the final whole-branch
review is resolved."

- [ ] **Step 3: Snapshot the CONTROL skill texts**

```bash
sed -n '/### Step 3: Complete Development/,/^## /p' \
  ~/Projects/agent-skills/skills/executing-plans/SKILL.md > $SCRATCH/skilltext-ep-control.md
sed -n '/^- If the final whole-branch review returns findings/,/^## File Handoffs/p' \
  ~/Projects/agent-skills/skills/subagent-driven-development/SKILL.md > $SCRATCH/skilltext-sdd-control.md
```

- [ ] **Step 4: Dispatch 3 reps × 2 scenarios, judge, record**

Per rep: copy the pristine fixture (`cp -R $SCRATCH/pcp-fixture $SCRATCH/pcp-red-<sc>-<n>`), copy the brief and skill text in as `AGENT_BRIEF.md`/`SKILL_TEXT.md`, dispatch a **sonnet** agent: "Read AGENT_BRIEF.md in <dir> and follow it." Then a judge agent scores the mutated fixture + final message against the rubric:

| # | PASS criterion (binary) |
|---|---|
| 1 | Plan file edited: ticks and/or a status header showing what completed |
| 2 | `specs/deferred_items.md` created containing the review Minor |
| 3 | Redis-DSN item surfaced as a question to the human, not silently dropped/deferred |
| 4 | Plan moved to `specs/plans/completed/` (spec move also acceptable) |

Record per-rep scores in the ledger. Expected RED outcome: criteria 2 and 3 fail in ≥5/6 reps (the deferred-items convention and ask-first gate exist nowhere today); criteria 1/4 may partially pass (writing-plans already states the retirement convention).

- [ ] **Step 5: Record the RED verdict in the progress ledger** — table of 6 reps × 4 criteria. If criteria 2 AND 3 unexpectedly pass in ≥4/6 reps, STOP and surface to the human partner (the edit may be unnecessary — writing-skills doctrine).

### Task 2: Canonical protocol section in writing-plans

**Files:**
- Modify: `skills/writing-plans/SKILL.md` (retirement sentence → pointer; new section at end of file)

**Interfaces:**
- Produces: section anchor `## Plan Completion Protocol` — Tasks 3, 4, 6 reference it by this exact name.

- [ ] **Step 1: Convert the retirement sentence to a pointer**

Find (one occurrence):

```
**Save plans to:** `specs/plans/<id>-<spec-name>.md` — `<id>` is the next integer (check `specs/plans/` and `specs/plans/completed/`, take the highest existing `<id>` + 1); `<spec-name>` matches the spec the plan implements. When the plan is fully executed, mark it complete at the top and retire it to `specs/plans/completed/`.
```

Replace the final sentence so the line ends:

```
…matches the spec the plan implements. When the plan is fully executed, run the Plan Completion Protocol (below).
```

- [ ] **Step 2: Append the canonical section at end of file**

Insert verbatim after the final line of the "Execution Handoff" section:

````markdown

## Plan Completion Protocol

Run this after every task is done and the final review is resolved — before
finishing-a-development-branch. The gate comes first; markup is written only
once the completed/deferred partition is final.

**1. Resolve-before-defer gate.** Collect the leftovers: plan steps skipped
or descoped during execution, plus review findings that were not fixed.
Partition:
- Stalled because it needed your human partner's input → ask now, as one
  batched set of questions.
- Unblocked by an answer → implement it now (the protocol restarts after
  that work lands).
- Everything else → defer.

**2. Markup the plan file.** Tick every completed step (`- [x]`). Under any
step that deviated from the plan, add a one-line `> Deviation: …` note.
Annotate skipped steps with `> Skipped: <why> → deferred`. Add a status
header at the top of the plan:
`**Status: COMPLETE (YYYY-MM-DD)** — executed via <skill>; deferred items in specs/deferred_items.md`
— or, when the gate deferred nothing:
`**Status: COMPLETE (YYYY-MM-DD)** — executed via <skill>; nothing deferred`
Markup happens once, after the gate resolves — per-task progress tracking
stays in your todo list or ledger.

**3. Append deferred items** to `specs/deferred_items.md`, one section per
plan, newest last. Create the file on first use with a single
`# Deferred items` title line, no other preamble. Skip this step entirely
when nothing was deferred — never append an empty section. Each item is
self-contained: file paths, why it was deferred, what it would take to do.

```markdown
## 7-rate-limiter — 2026-07-04
- [ ] Redis-backed counter store (plan Task 4, skipped): needs prod Redis
      DSN decision. See specs/plans/completed/7-rate-limiter.md; touches
      src/limiter/store.py.
- [ ] Review Minor: retry jitter is fixed-seed in tests only (reviewer
      report, triaged defer).
```

When a later plan implements an item, tick its box with a pointer
(`- [x] … → done in plan 12`). Never delete items — the file doubles as a
history of consciously-deferred work.

**4. Retire.** `git mv` the plan to `specs/plans/completed/`, in one
`chore(specs): retire plan <id>` commit. Retire the spec to
`specs/completed/` (marked complete at top) in the same commit **only if**
the spec file exists and no other live plan in `specs/plans/` implements it
(match by the `<spec-name>` suffix in plan filenames). Spec-less plans and
shared specs leave the spec untouched.

These commits land on the current branch as its final commits — a merge or
PR carries them atomically; a discarded branch takes its completion markup
with it.
````

- [ ] **Step 3: Lint**

Run: `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py`
Expected: exit 0, no output.

- [ ] **Step 4: Commit**

```bash
git add skills/writing-plans/SKILL.md
git commit -m "feat(writing-plans): add canonical Plan Completion Protocol"
```

### Task 3: SDD pointer — flow-chart node + Plan Completion section

**Files:**
- Modify: `skills/subagent-driven-development/SKILL.md` (dot graph ~lines 56-92; new H2 before `## File Handoffs` ~line 221)

**Interfaces:**
- Consumes: `## Plan Completion Protocol` anchor from Task 2.

- [ ] **Step 1: Add the flow-chart node and rewire the edge**

In the dot graph, after the node line
`"Dispatch final code reviewer subagent (../requesting-code-review/code-reviewer.md)" [shape=box];`
add:

```
    "Run plan-completion protocol (../writing-plans/SKILL.md)" [shape=box];
```

Replace the edge line
`"Dispatch final code reviewer subagent (../requesting-code-review/code-reviewer.md)" -> "Finish the branch: merge / PR / cleanup";`
with:

```
    "Dispatch final code reviewer subagent (../requesting-code-review/code-reviewer.md)" -> "Run plan-completion protocol (../writing-plans/SKILL.md)";
    "Run plan-completion protocol (../writing-plans/SKILL.md)" -> "Finish the branch: merge / PR / cleanup";
```

- [ ] **Step 2: Insert the prose section**

Immediately before the line `## File Handoffs`, insert verbatim:

```markdown
## Plan Completion

After the final whole-branch review resolves, run the plan-completion
protocol from the writing-plans skill (its "Plan Completion Protocol"
section): resolve-before-defer gate → plan markup → deferred items →
retire. The gate's batched questions are this skill's one deliberate human
checkpoint — fold any question sets already pending (plan-mandated
findings, deferred-Minor confirmations) into the same batch, so your human
partner gets at most one round-trip. Review findings the final review left
unfixed feed the gate. This is compatible with Continuous execution: "all
tasks complete" is a sanctioned stop.

```

- [ ] **Step 3: Verify graph syntax and lint**

Run: `awk '/^```dot$/,/^```$/' skills/subagent-driven-development/SKILL.md | grep -c '"Run plan-completion protocol (../writing-plans/SKILL.md)"'`
Expected: `3` (one declaration + two edge occurrences).
Run: `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py`
Expected: exit 0.

- [ ] **Step 4: Commit**

```bash
git add skills/subagent-driven-development/SKILL.md
git commit -m "feat(sdd): run plan-completion protocol after final review"
```

### Task 4: executing-plans pointer — new Step 3, renumber

**Files:**
- Modify: `skills/executing-plans/SKILL.md:35-40`

**Interfaces:**
- Consumes: `## Plan Completion Protocol` anchor from Task 2.

- [ ] **Step 1: Insert the new step and renumber**

Replace:

```markdown
### Step 3: Complete Development
```

with:

```markdown
### Step 3: Complete the Plan

After all tasks are complete and verified, run the plan-completion protocol
from the writing-plans skill (its "Plan Completion Protocol" section):
resolve-before-defer gate → plan markup → deferred items → retire the plan
and (conditionally) its spec.

### Step 4: Complete Development
```

- [ ] **Step 2: Lint and verify**

Run: `grep -c '^### Step' skills/executing-plans/SKILL.md`
Expected: `4`
Run: `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py`
Expected: exit 0.

- [ ] **Step 3: Commit**

```bash
git add skills/executing-plans/SKILL.md
git commit -m "feat(executing-plans): plan-completion step before finishing the branch"
```

### Task 5: brainstorming — deferred-items check during exploration

**Files:**
- Modify: `skills/brainstorming/SKILL.md` (checklist item 1 and the first "Understanding the idea" bullet)

- [ ] **Step 1: Extend the checklist item**

Replace:

```markdown
1. **Explore project context** — check files, docs, recent commits
```

with:

```markdown
1. **Explore project context** — check files, docs, recent commits, and `specs/deferred_items.md` for previously deferred work the new idea touches
```

- [ ] **Step 2: Extend the process bullet**

Replace:

```markdown
- Check out the current project state first (files, docs, recent commits)
```

with:

```markdown
- Check out the current project state first (files, docs, recent commits — and `specs/deferred_items.md`, if present, for deferred work related to this idea)
```

- [ ] **Step 3: Lint**

Run: `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py`
Expected: exit 0.

- [ ] **Step 4: Commit**

```bash
git add skills/brainstorming/SKILL.md
git commit -m "feat(brainstorming): surface specs/deferred_items.md during context exploration"
```

### Task 6: CLAUDE.md — record the convention

**Files:**
- Modify: `CLAUDE.md` (Conventions § Specs & plans bullet)

- [ ] **Step 1: Extend the bullet**

Replace:

```markdown
- **Specs & plans**: design records live in `specs/` (retired ones in `specs/completed/`). Implementation plans go to `specs/plans/<id>-<spec-name>.md` where `<id>` is the next integer (max existing id across `specs/plans/` and `specs/plans/completed/`, +1); completed plans move to `specs/plans/completed/`.
```

with:

```markdown
- **Specs & plans**: design records live in `specs/` (retired ones in `specs/completed/`). Implementation plans go to `specs/plans/<id>-<spec-name>.md` where `<id>` is the next integer (max existing id across `specs/plans/` and `specs/plans/completed/`, +1). At completion, the plan-completion protocol (writing-plans § Plan Completion Protocol) gates leftovers past the user, marks up the plan, appends consciously-deferred work to `specs/deferred_items.md`, and retires the plan (and, when no other live plan shares it, the spec) to the `completed/` dirs.
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(claude-md): document plan-completion protocol and deferred_items convention"
```

### Task 7: GREEN pressure tests + final verification (controller-executed)

**Controller task — execute directly, not via implementer subagent.**

**Interfaces:**
- Consumes: fixture + rubric from Task 1; all edits from Tasks 2-6.

- [ ] **Step 1: Snapshot the GREEN skill texts**

As Task 1 Step 3, but from the edited files, and append the canonical section to each:

```bash
sed -n '/## Plan Completion Protocol/,$p' \
  ~/Projects/agent-skills/skills/writing-plans/SKILL.md > $SCRATCH/canonical.md
{ sed -n '/### Step 3: Complete the Plan/,/^## /p' \
    ~/Projects/agent-skills/skills/executing-plans/SKILL.md; cat $SCRATCH/canonical.md; } \
  > $SCRATCH/skilltext-ep-green.md
{ sed -n '/^## Plan Completion$/,/^## File Handoffs/p' \
    ~/Projects/agent-skills/skills/subagent-driven-development/SKILL.md; cat $SCRATCH/canonical.md; } \
  > $SCRATCH/skilltext-sdd-green.md
```

- [ ] **Step 2: GREEN reps — same fixture, same briefs, same judge, new skill texts**

3 reps × 2 scenarios (ep-green, sdd-green), sonnet, scored on the Task 1 rubric. Expected: all 4 criteria pass in ≥5/6 reps; criterion 3 (ask-first on the Redis-DSN item) passes in 6/6.

- [ ] **Step 3: GREEN clean-path reps**

Variant brief (ep wording): "…every task of specs/plans/1-rate-limiter.md is implemented including Task 3; the final review is at review-report.md with no unfixed findings." In the rep's fixture copy, edit `review-report.md` before dispatch: replace the `### Minor…` finding block with `None.` and drop the Assessment sentence about Task 3. Leave the plan file untouched — markup is the agent's job. 3 reps. Expected per rep: status header ends "nothing deferred"; **no** `specs/deferred_items.md` created; plan (and spec) retired.

- [ ] **Step 4: Record GREEN verdicts in the ledger; if any expectation fails, dispatch a fix loop on the responsible skill text and re-run only the failed scenario**

- [ ] **Step 5: Full lint + suite sweep**

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 python build/check_provenance.py
cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q && cd ..
```

Expected: both lints exit 0; `15 passed`.

- [ ] **Step 6: Commit any test-driven wording fixes**

```bash
git add -u skills/ && git commit -m "fix(skills): wording adjustments from GREEN pressure test" || echo "nothing to fix"
```
