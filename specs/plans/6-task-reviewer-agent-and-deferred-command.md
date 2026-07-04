# task-reviewer Agent + /deferred Command Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a dedicated `task-reviewer` subagent definition (taking over SDD's per-task reviews with a short dispatch form) and a global `/deferred` slash command that triages `specs/deferred_items.md`.

**Architecture:** Three markdown artifacts plus doc/provenance sync. The agent file carries the full stable review contract distilled from SDD's task-reviewer template; the template gains a placeholders-only Short Form (agent installed) while keeping the existing text verbatim as the Full Form (portable fallback); the command is a read-only triage prompt. Verification is by lints, content anchors, and fixture-based behavior checks — there is no compiled code.

**Tech Stack:** Markdown with YAML frontmatter (Claude Code agent + command formats), zsh, `uv run` lints from `build/`.

## Global Constraints

- `/deferred` is **read-only**: the command text must instruct never editing `specs/deferred_items.md`; ticking remains the job of later plans' completion-protocol runs (spec §3.6).
- The Full Form in `task-reviewer-prompt.md` is preserved **verbatim** except the single routing line (spec §2) — the skill must keep working for installs without the agents directory.
- Agent frontmatter: `name: task-reviewer`; `tools: Read, Grep, Glob, Bash`; **no `model` field** (tier chosen per dispatch, SDD Model Selection) (spec §1).
- Classification in `/deferred` is judged **from each item's recorded "why it was deferred"** — no repo cross-checking, no staleness maintenance (spec §3.3, triage-only decision).
- NOTICE line wording (spec §4, verbatim): `agents/task-reviewer.md is a read-only agent definition distilled from the adapted subagent-driven-development task-reviewer template (same MIT terms).`
- Repo conventions: provenance lints must pass; cross-skill references use bare skill names.

---

### Task 1: `agents/task-reviewer.md` + provenance + install

**Files:**
- Create: `agents/task-reviewer.md`
- Modify: `NOTICE` (Changes-from-upstream list, after the `agents/code-reviewer.md` item)
- Modify: `README.md` (Agents table; Credits superpowers bullet)
- Create (outside repo): symlink `~/.claude/agents/task-reviewer.md`

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: agent type name `task-reviewer` — Task 2's Short Form dispatches to exactly this name; the output contract ends in `**Task quality:** [Approved | Needs fixes]`, which SDD's SKILL.md already expects from task reviews.

- [ ] **Step 1: Create `agents/task-reviewer.md`** with exactly this content:

````markdown
---
name: task-reviewer
description: Read-only task-scoped reviewer that checks one task's implementation against its brief — spec compliance first, then code quality. Dispatched by the subagent-driven-development skill after each task; expects a task brief, an implementer report, and a diff file in the dispatch.
tools: Read, Grep, Glob, Bash
---

You are reviewing one task's implementation: first whether it matches its
requirements, then whether it is well-built. This is a task-scoped gate,
not a merge review — a broad whole-branch review happens separately after
all tasks are complete.

The dispatch prompt gives you the task brief (your requirements), the
implementer's report, and a diff file with base/head SHAs. The global
constraints quoted in the dispatch bind the task.

## Read-only contract

Your review is read-only on this checkout: you have no edit tools, and you
must not mutate the working tree, the index, HEAD, branch state, or the
worktree list via Bash.

## Reading the diff

Read the diff file once — it contains the commit list, a stat summary, and
the full diff with surrounding context, and it is your view of the change.
The diff's context lines ARE the changed files: do not Read a changed file
separately unless a hunk you must judge is cut off mid-function — and say
so in your report. Do not re-run git commands. If the diff file is missing,
fetch the diff yourself: `git diff --stat BASE..HEAD` and
`git diff BASE..HEAD`. Do not crawl the broader codebase. Inspect code
outside the diff only to evaluate a concrete risk you can name — one
focused check per named risk, and name both the risk and what you checked
in your report. Cross-cutting changes are legitimate named risks: if the
diff changes lock ordering, a function or API contract, or shared mutable
state, checking the call sites is the right method.

## Do not trust the report

Treat the implementer's report as unverified claims about the code. It may
be incomplete, inaccurate, or optimistic. Verify the claims against the
diff. Design rationales in the report are claims too: "left it per YAGNI,"
"kept it simple deliberately," or any other justification is the
implementer grading their own work. Judge the code on its merits — a
stated rationale never downgrades a finding's severity.

## Tests

The implementer already ran the tests and reported results with TDD
evidence for exactly this code. Do not re-run the suite to confirm their
report. Run a test only when reading the code raises a specific doubt that
no existing run answers — and then a focused test, never a package-wide
suite, race detector run, or repeated/high-count loop. If heavy validation
seems warranted, recommend it in your report instead of running it. If you
cannot run commands in this environment, name the test you would run.

Warnings or other noise in the implementer's reported test output are
findings — test output should be pristine.

## Part 1: Spec compliance

Compare the diff against the brief:

- **Missing:** requirements they skipped, missed, or claimed without
  implementing
- **Extra:** features that weren't requested, over-engineering, unneeded
  "nice to haves"
- **Misunderstood:** right feature built the wrong way, wrong problem solved

If a requirement cannot be verified from this diff alone (it lives in
unchanged code or spans tasks), report it as a ⚠️ item instead of
broadening your search.

## Part 2: Code quality

**Code quality:** clean separation of concerns; proper error handling; DRY
without premature abstraction; edge cases handled.

**Tests:** do the new and changed tests verify real behavior, not mocks?
Are the task's edge cases covered?

**Structure:** one clear responsibility per file with a well-defined
interface; units decomposed so they can be understood and tested
independently; implementation follows the plan's file structure. Flag new
files that are already large, or significant growth this change contributed
— not pre-existing file sizes.

## Calibration

Categorize issues by actual severity. Not everything is Critical. Important
means this task cannot be trusted until it is fixed: incorrect or fragile
behavior, a missed requirement, or maintainability damage you would block a
merge over — verbatim duplication of a logic block, swallowed errors, tests
that assert nothing. "Coverage could be broader" and polish suggestions are
Minor.

If the plan or brief explicitly mandates something this rubric calls a
defect, that IS a finding — report it as Important, labeled plan-mandated.
The plan's authorship does not grade its own work; the human decides.

Acknowledge what was done well before listing issues — accurate praise
helps the implementer trust the rest of the feedback.

## Report

Your final message is the report itself: begin directly with the
spec-compliance verdict. Every line is a verdict, a finding with file:line,
or a check you ran — no preamble, no process narration, no closing summary.
Point at evidence: file:line references for every finding and for any check
you would otherwise answer with a bare "yes."

### Spec Compliance

- ✅ Spec compliant | ❌ Issues found: [what's missing/extra/misunderstood,
  with file:line references]
- ⚠️ Cannot verify from diff: [requirements you could not verify from the
  diff alone, and what the controller should check — report alongside the
  ✅/❌ verdict for everything you could verify]

### Strengths

### Issues

#### Critical (Must Fix)
#### Important (Should Fix)
#### Minor (Nice to Have)

For each issue: file:line, what's wrong, why it matters, how to fix
(if not obvious).

### Assessment

**Task quality:** [Approved | Needs fixes]

**Reasoning:** [1-2 sentence technical assessment]
````

- [ ] **Step 2: Add the NOTICE line.** In `NOTICE`, the "Changes from upstream" list currently contains this item:

```
  - agents/code-reviewer.md is a read-only agent definition distilled from
    the adapted requesting-code-review reviewer template (same MIT terms).
```

Insert directly after it, as a new list item with identical indentation:

```
  - agents/task-reviewer.md is a read-only agent definition distilled from
    the adapted subagent-driven-development task-reviewer template (same
    MIT terms).
```

- [ ] **Step 3: Add the README Agents-table row.** In `README.md`, the Agents table currently has one data row (`code-reviewer`). Add below it:

```markdown
| [`task-reviewer`](agents/task-reviewer.md) | Read-only task-scoped reviewer for `subagent-driven-development`'s per-task gate — checks one task's diff against its brief for spec compliance and code quality, returning both verdicts. Carries the full review contract so dispatches only need the task's brief, report, and diff paths. |
```

Also update the layout-tree comment for `agents/` (the table now documents two agents). Replace the line:

```
├── agents/      # subagent definitions (code-reviewer — see Agents below)
```

with:

```
├── agents/      # subagent definitions (code-reviewer, task-reviewer — see Agents below)
```

- [ ] **Step 4: Update the README Credits sentence.** In the Credits superpowers bullet, replace:

```markdown
The [`code-reviewer`](agents/code-reviewer.md) agent is distilled from the adapted `requesting-code-review` reviewer template, same terms.
```

with:

```markdown
The [`code-reviewer`](agents/code-reviewer.md) and [`task-reviewer`](agents/task-reviewer.md) agents are distilled from the adapted `requesting-code-review` and `subagent-driven-development` reviewer templates, same terms.
```

- [ ] **Step 5: Create the install symlink**

```bash
mkdir -p ~/.claude/agents
ln -sfn /Users/lowell/Projects/agent-skills/agents/task-reviewer.md ~/.claude/agents/task-reviewer.md
test -f ~/.claude/agents/task-reviewer.md && echo OK
```

(`ln -sfn` keeps the step rerun-safe under fix loops; the destination is a per-file link in a real directory, so `-f` cannot clobber a directory.)

Expected: `OK`

- [ ] **Step 6: Verify provenance lint passes**

```bash
cd /Users/lowell/Projects/agent-skills
uv run --python 3.13 python build/check_provenance.py
```

Expected: exit 0, no missing-attribution errors.

- [ ] **Step 7: Commit**

```bash
cd /Users/lowell/Projects/agent-skills
git add agents/task-reviewer.md NOTICE README.md
git commit -m "feat(agents): add task-reviewer agent definition (distilled from SDD template)"
```

---

### Task 2: Short/Full dispatch forms in the SDD template

**Files:**
- Modify: `skills/subagent-driven-development/task-reviewer-prompt.md`

**Interfaces:**
- Consumes: agent type name `task-reviewer` (Task 1).
- Produces: the Short Form dispatch shape — controllers send only `[BRIEF_FILE]`, `[GLOBAL_CONSTRAINTS]`, `[REPORT_FILE]`, `[BASE_SHA]`, `[HEAD_SHA]`, `[DIFF_FILE]`, plus `model`.

- [ ] **Step 1: Replace the template's opening.** The file currently begins:

```markdown
# Task Reviewer Prompt Template

Use this template when dispatching a task reviewer subagent. The reviewer
reads the task's diff once and returns two verdicts: spec compliance and
code quality.

**Purpose:** Verify one task's implementation matches its requirements (nothing
more, nothing less) and is well-built (clean, tested, maintainable)
```

Replace that opening (everything above the ```` ``` ```` fence that starts the dispatch prompt) with:

````markdown
# Task Reviewer Prompt Template

Use this template when dispatching a task reviewer subagent. The reviewer
reads the task's diff once and returns two verdicts: spec compliance and
code quality.

**Purpose:** Verify one task's implementation matches its requirements (nothing
more, nothing less) and is well-built (clean, tested, maintainable)

**Routing:** dispatch to the `task-reviewer` agent if it is defined (use the
Short Form — the agent's definition carries the review contract); otherwise
dispatch to `general-purpose` (use the Full Form, which carries the contract
inline). The Placeholders section at the bottom applies to both forms.

## Short Form (task-reviewer agent installed)

```
Subagent (task-reviewer):
  description: "Review Task N (spec + quality)"
  model: [MODEL — REQUIRED: choose per SKILL.md Model Selection; an omitted
         model silently inherits the session's most expensive one]
  prompt: |
    Review one task's implementation. Your agent definition carries the
    review contract; this dispatch carries the task.

    ## What Was Requested

    Read the task brief: [BRIEF_FILE]

    Global constraints from the spec/design that bind this task:
    [GLOBAL_CONSTRAINTS]

    ## What the Implementer Claims They Built

    Read the implementer's report: [REPORT_FILE]

    ## Diff Under Review

    **Base:** [BASE_SHA]
    **Head:** [HEAD_SHA]
    **Diff file:** [DIFF_FILE]
```

## Full Form (no task-reviewer agent)

````

- [ ] **Step 2: Edit the Full Form's routing line.** Inside the existing dispatch-prompt fence (now under `## Full Form (no task-reviewer agent)`), replace the line:

```
Subagent (code-reviewer if defined, else general-purpose):
```

with:

```
Subagent (general-purpose):
```

Everything else inside the fence stays byte-for-byte identical, as do the trailing **Placeholders** / **Reviewer returns** sections.

- [ ] **Step 3: Verify the Full Form survived verbatim.** The diff for this file must show only (a) the new opening/Short Form block and (b) the one routing line. Diff against `HEAD` so staging state cannot mask the change:

```bash
cd /Users/lowell/Projects/agent-skills
git diff HEAD -- skills/subagent-driven-development/task-reviewer-prompt.md | grep '^-' | grep -v '^---'
git diff HEAD -- skills/subagent-driven-development/task-reviewer-prompt.md | awk '/^\+## Full Form/{seen=1; next} seen && /^\+/ && !/^\+\+\+/'
```

Expected: the first command prints exactly one line — `Subagent (code-reviewer if defined, else general-purpose):`. **Empty output is a failure** (the routing edit is missing). Any other `-` line means the Full Form was altered. The second command prints exactly one line — `+Subagent (general-purpose):`; any other line means content was inserted inside the Full Form, which also violates the verbatim requirement. Fix before committing.

- [ ] **Step 4: Verify both forms parse and anchors exist**

```bash
cd /Users/lowell/Projects/agent-skills
grep -c '## Short Form (task-reviewer agent installed)' skills/subagent-driven-development/task-reviewer-prompt.md
grep -c '## Full Form (no task-reviewer agent)' skills/subagent-driven-development/task-reviewer-prompt.md
grep -c 'Subagent (task-reviewer):' skills/subagent-driven-development/task-reviewer-prompt.md
grep -c 'Subagent (general-purpose):' skills/subagent-driven-development/task-reviewer-prompt.md
for p in BRIEF_FILE GLOBAL_CONSTRAINTS REPORT_FILE BASE_SHA HEAD_SHA DIFF_FILE; do
  n=$(grep -c "\[$p\]" skills/subagent-driven-development/task-reviewer-prompt.md); echo "$p: $n"
done
```

Expected: each heading/routing grep prints `1`; every placeholder count is ≥ 2 (once in the Short Form, once or more in the Full Form/Placeholders list).

- [ ] **Step 5: Run the frontmatter lint** (the template lives inside a skill directory; confirm nothing regressed)

```bash
cd /Users/lowell/Projects/agent-skills
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
```

Expected: exit 0.

- [ ] **Step 6: Commit**

```bash
cd /Users/lowell/Projects/agent-skills
git add skills/subagent-driven-development/task-reviewer-prompt.md
git commit -m "refactor(sdd): split task-reviewer template into Short/Full dispatch forms"
```

---

### Task 3: `/deferred` command + docs + install

**Files:**
- Create: `commands/deferred.md`
- Delete: `commands/.gitkeep`
- Modify: `README.md` (layout tree; new Commands section; Installation)
- Modify: `CLAUDE.md` (scaffolding sentence)
- Create (outside repo): symlink `~/.claude/commands/deferred.md`

**Interfaces:**
- Consumes: the `specs/deferred_items.md` conventions defined in writing-plans § Plan Completion Protocol (`## <plan> — <date>` section headers, `- [ ]` items); the brainstorming skill by bare name.
- Produces: user-invocable `/deferred` in any project.

- [ ] **Step 1: Create `commands/deferred.md`** with exactly this content:

```markdown
---
description: Triage specs/deferred_items.md — group unticked items, classify actionable vs blocked, propose promotions to a new spec
---

Triage the deferred-work backlog in the current project. This is read-only:
never edit `specs/deferred_items.md` — ticking items is the job of later
plans' completion-protocol runs.

1. Read `specs/deferred_items.md` at the project root. If the file does not
   exist, or it contains no unticked (`- [ ]`) items, report that nothing
   is deferred and stop.
2. Group the unticked items by theme — related items from different plan
   sections belong together. Keep each item's source plan and date (from
   its `## <plan> — <date>` section header) attached.
3. Classify each group as **actionable now** or **still blocked**, judging
   only from each item's recorded reason for deferral.
4. Propose the top promotion candidates: which items or groups deserve to
   become a new spec. Present a short ranked list with one-line reasoning
   each.
5. If the user selects candidates, use the brainstorming skill with the
   selection as the idea — promotion means a new spec through the normal
   design cycle.
```

- [ ] **Step 2: Remove the placeholder**

```bash
cd /Users/lowell/Projects/agent-skills
git rm --ignore-unmatch commands/.gitkeep
```

(`--ignore-unmatch` keeps the step rerun-safe if a fix loop re-enters this task.)

- [ ] **Step 3: Update the README layout tree.** Replace the line:

```
├── commands/    # slash commands (scaffolding, empty for now)
```

with:

```
├── commands/    # slash commands (/deferred — see Commands below)
```

- [ ] **Step 4: Add the README Commands section.** Directly after the `## Agents` section (after its table), insert:

```markdown
## Commands

Slash commands live in [`commands/`](commands/) and install into `~/.claude/commands/` (symlink or copy, one file per command):

| Command | Description |
|---------|-------------|
| [`/deferred`](commands/deferred.md) | Triage `specs/deferred_items.md` in the current project: group unticked items by theme, classify actionable-now vs still-blocked, and propose which deserve promotion to a new spec. Read-only — ticking stays with the plan-completion protocol. |
```

- [ ] **Step 5: Add the Installation subsection.** Directly after the `### Agents` subsection at the end of Installation, insert:

````markdown
### Commands

Slash commands install the same way, into `~/.claude/commands/` (one symlink per file):

```bash
mkdir -p ~/.claude/commands
ln -s ~/agent-skills/commands/deferred.md ~/.claude/commands/deferred.md
```
````

- [ ] **Step 6: Update CLAUDE.md.** In the "What this repo is" paragraph, replace:

```
`commands/` (slash commands), `hooks/` (hook scripts), `rules/` (rule files) — the latter three are scaffolding, currently empty.
```

with:

```
`commands/` (slash commands — `/deferred`), `hooks/` (hook scripts), `rules/` (rule files) — the latter two are scaffolding, currently empty.
```

- [ ] **Step 7: Create the install symlink**

```bash
mkdir -p ~/.claude/commands
ln -sfn /Users/lowell/Projects/agent-skills/commands/deferred.md ~/.claude/commands/deferred.md
test -f ~/.claude/commands/deferred.md && echo OK
```

Expected: `OK`

- [ ] **Step 8: Commit**

```bash
cd /Users/lowell/Projects/agent-skills
git add commands/deferred.md README.md CLAUDE.md
git commit -m "feat(commands): add /deferred deferred-items triage command"
```

(The `.gitkeep` deletion from Step 2 is already staged by `git rm`.)

---

### Task 4: Verification (controller task — lints, discovery, fixture behavior)

**Files:**
- Create (scratchpad only, never committed): `<scratchpad>/deferred-fixture/specs/deferred_items.md`, `<scratchpad>/deferred-empty/` (empty project dir)

**Interfaces:**
- Consumes: `commands/deferred.md` body (Task 3); `agents/task-reviewer.md` (Task 1).

This task is executed by the controller directly (like plan 5's pressure-test task), because it dispatches evaluation subagents.

- [ ] **Step 1: Run both lints and the full test suites**

```bash
cd /Users/lowell/Projects/agent-skills
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 python build/check_provenance.py
cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q
```

Expected: both lints exit 0; 15 tests pass.

- [ ] **Step 2: Verify discovery.** Confirm both symlinks resolve and the agent frontmatter parses:

```bash
test -f ~/.claude/agents/task-reviewer.md && test -f ~/.claude/commands/deferred.md && echo LINKS-OK
head -5 ~/.claude/agents/task-reviewer.md
```

Expected: `LINKS-OK`; frontmatter shows `name: task-reviewer`.

Then best-effort in-session discovery: dispatch a trivial Agent-tool call
with subagent type `task-reviewer` ("Report the first heading of README.md
in /Users/lowell/Projects/agent-skills and stop"). If the type resolves,
agent discovery is confirmed. If it errors as an unknown agent type, that is
**not conclusive** — agent lists load at session start. Slash-command
discovery cannot be checked from inside a session at all. Anything not
confirmable in-session becomes a **gate question at plan completion**: ask
the human partner to confirm, in a fresh session, that `task-reviewer`
appears in the agent list and `/deferred` autocompletes.

- [ ] **Step 3: Build the triage fixture.** Create `<scratchpad>/deferred-fixture/specs/deferred_items.md`:

```markdown
# Deferred items

## 3-ingest-pipeline — 2026-05-12
- [x] Parquet output option (plan Task 5, skipped): needed a partitioning
      decision. → done in plan 4
- [ ] Retry with backoff on HTTP 429 (plan Task 2, descoped): needs a
      decision on max retry budget. Touches src/ingest/client.py.

## 4-report-generator — 2026-06-02
- [ ] PDF export (review Important, triaged defer): blocked on choosing a
      rendering lib (weasyprint vs reportlab).
- [ ] Rate-limit the summary endpoint (plan Task 6, skipped): needs prod
      traffic numbers to size the limit.
```

Also create an empty project dir `<scratchpad>/deferred-empty/` containing only a `.git` marker (`git init -q`).

- [ ] **Step 4: Fixture rep — populated file.** Record `md5 <fixture>/specs/deferred_items.md`. Dispatch a sonnet subagent whose prompt **begins with an explicit project root** — `Project root: <scratchpad>/deferred-fixture — resolve all relative paths against it.` — followed by the body of `commands/deferred.md` as its instruction (staged neutrally — do not say it is a test). The root declaration is required: subagents inherit the session cwd (the repo), and without it the command body's "at the project root" would resolve against the repo, which has no `specs/deferred_items.md`, spuriously failing every judgment below. Judge the transcript for: (a) the ticked Parquet item is excluded; (b) the three unticked items are grouped with plan/date attribution; (c) each group gets an actionable-now/still-blocked classification with reasoning drawn from the recorded deferral reason; (d) promotion candidates are proposed as a ranked list; (e) no file edit occurred — re-run `md5` and compare.

Expected: all five hold; md5 unchanged.

- [ ] **Step 5: Fixture rep — missing file.** Dispatch a sonnet subagent with the same command body, prefixed the same way with `Project root: <scratchpad>/deferred-empty — resolve all relative paths against it.` Judge: it reports nothing is deferred and stops — no invented items, no file creation (`ls <dir>/specs/` fails or is empty).

Expected: clean "nothing deferred" stop.

- [ ] **Step 6: Short Form completeness check**

```bash
cd /Users/lowell/Projects/agent-skills
awk '/## Short Form/,/## Full Form/' skills/subagent-driven-development/task-reviewer-prompt.md | grep -o '\[[A-Z_]*\]' | sort -u
awk '/## Short Form/,/## Full Form/' skills/subagent-driven-development/task-reviewer-prompt.md | grep -c 'model: \[MODEL'
awk '/## Short Form/,/## Full Form/' skills/subagent-driven-development/task-reviewer-prompt.md | grep -ci 'do not trust' || true
```

Expected: first command — exactly `[BASE_SHA] [BRIEF_FILE] [DIFF_FILE] [GLOBAL_CONSTRAINTS] [HEAD_SHA] [REPORT_FILE]` as a sorted list (`[MODEL]` can't match that grep because its bracket closes after the multi-line comment); second command — `1` (the model placeholder is present); third command — `0` (no contract prose in the Short Form; the `|| true` is deliberate — `grep -c` exits 1 on zero matches, and the printed `0` is the pass signal).

- [ ] **Step 7: Fix anything found, commit fixes**

Any failed check above is fixed in-place and committed as `fix: <what>` before the plan is declared complete. If all checks pass with no changes, there is nothing to commit.

---

## Verification Summary

Lints + suites green (Task 4 Step 1); both installs discoverable (Step 2); `/deferred` behaves per spec on populated and missing fixtures without writes (Steps 4-5); Short Form carries all placeholders and no contract text (Step 6); Full Form verbatim except the routing line (Task 2 Step 3).
