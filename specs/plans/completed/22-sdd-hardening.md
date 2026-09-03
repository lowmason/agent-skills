# SDD Hardening Implementation Plan

**Status: COMPLETE (2026-09-03)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adopt four superpowers v6.1.0–v6.3.0 changes into `skills/subagent-driven-development` — a plan-scoped workspace, a no-nested-subagent ban, same-shape task batching, and a bounded review loop.

**Architecture:** One code change (the three bash dispatch scripts gain a plan argument, so the workspace becomes `.sdd/<plan-slug>/`) followed by five prose changes to skill text and prompt templates. The code change lands first and atomically, because the three scripts call each other: changing `sdd-workspace` alone leaves its two consumers broken.

**Tech Stack:** bash (the three scripts), pytest driving them as subprocesses via `uv run --python 3.13`, Markdown skill text.

## Global Constraints

- **Execute from a git worktree, never the main checkout.** `~/.claude/skills/subagent-driven-development` and `~/.claude/agents/task-reviewer.md` are symlinks into `/Users/lowell/Projects/agent-skills/`, so editing this repo from the main checkout changes the running controller's own tools mid-plan. Use the using-git-worktrees skill before Task 1.
- Cross-skill references use **bare skill names** (`use the writing-plans skill`), never the upstream `superpowers:` plugin namespace. Upstream's text uses the namespace; strip it from anything adapted.
- Python 3.13 via `uv run`. Tests are directory-scoped: run them from inside `skills/subagent-driven-development/scripts`, never from the repo root.
- Single quotes over double in Python.
- **Do not write tests that grep skill text or script source for wording.** The observable is behavior. Prose changes in Tasks 3–6 are verified by reading, not by asserting a phrase appears in a file.
- All adopted material is from superpowers (MIT, © 2025 Jesse Vincent, `LICENSE-superpowers`). Prose is rewritten in this repo's voice, not pasted.
- The workspace directory is `.sdd` (this repo's local rename of upstream's `.superpowers/sdd`). Never reintroduce `.superpowers/`.

---

### Task 1: Plan-scope the workspace across all three scripts

**Files:**
- Modify: `skills/subagent-driven-development/scripts/sdd-workspace`
- Modify: `skills/subagent-driven-development/scripts/task-brief:8-10,25`
- Modify: `skills/subagent-driven-development/scripts/review-package:7-8,12-27`
- Test: `skills/subagent-driven-development/scripts/test_sdd_scripts.py`

**Interfaces:**
- Produces: `sdd-workspace PLAN_FILE` → prints the absolute path of `<repo-root>/.sdd/<basename-of-plan-without-.md>/`, creating it. Exits 2 on wrong argument count and on a plan file that is not a regular file (including a directory).
- The slug guard rejecting `""`, `.`, and `..` sits after the file test, so it is **defensive and unreachable through normal input** — none of those three names is a regular file, so `[ -f ]` rejects them first. Keep it anyway: it is cheap, it matches upstream, and it bounds `basename` if the file test is ever reordered or relaxed. Do not write a test claiming to exercise it.
- Produces: `task-brief PLAN_FILE TASK_NUMBER [OUTFILE]` — signature unchanged; only its internal `sdd-workspace` call gains the plan.
- Produces: `review-package PLAN_FILE BASE HEAD [OUTFILE]` — **breaking change**, `PLAN_FILE` inserted first.
- Produces: the self-ignoring guard stays at `<repo-root>/.sdd/.gitignore`, the parent of the per-plan directories, so one guard covers every sibling.

All three scripts must change in this one task. `sdd-workspace` becomes argument-requiring, so its two callers break the moment it lands; a commit that split them would leave the suite red.

- [x] **Step 1: Write the failing tests for `sdd-workspace`**

Replace the two existing tests in the `# ── sdd-workspace ──` section of `skills/subagent-driven-development/scripts/test_sdd_scripts.py` with these five. The `repo` fixture already writes `plan.md` at the repo root, so the expected slug is `plan`.

```python
def test_workspace_is_created_inside_the_working_tree(repo):
    """Not under .git/ — Claude Code denies agent writes to that protected path,
    which would block an implementer subagent from writing its report."""
    result = run(WORKSPACE, repo / 'plan.md', cwd=repo)
    assert result.returncode == 0
    printed = Path(result.stdout.strip())
    assert printed.resolve() == (repo / '.sdd' / 'plan').resolve()
    assert '.git' not in printed.parts


def test_workspace_ignores_itself_so_artifacts_never_reach_git_status(repo):
    run(WORKSPACE, repo / 'plan.md', cwd=repo)
    assert (repo / '.sdd' / '.gitignore').read_text() == '*\n'
    # The guard sits at the .sdd parent, not inside the per-plan directory,
    # so one guard covers every sibling plan's workspace.
    assert not (repo / '.sdd' / 'plan' / '.gitignore').exists()
    (repo / '.sdd' / 'plan' / 'task-1-brief.md').write_text('scratch')
    status = run('git', 'status', '--short', cwd=repo).stdout
    assert '.sdd' not in status


def test_workspace_separates_two_plans_in_one_working_tree(repo):
    """The bug this change exists to fix: a flat workspace let a second plan
    read the first plan's ledger as its own progress and skip live tasks."""
    (repo / 'other.md').write_text(PLAN)
    first = Path(run(WORKSPACE, repo / 'plan.md', cwd=repo).stdout.strip())
    second = Path(run(WORKSPACE, repo / 'other.md', cwd=repo).stdout.strip())
    assert first.resolve() != second.resolve()
    (first / 'progress.md').write_text('Task 1: complete\n')
    assert not (second / 'progress.md').exists()


def test_workspace_is_stable_for_one_plan(repo):
    """Same plan, same directory — a resuming controller must find its ledger."""
    first = run(WORKSPACE, repo / 'plan.md', cwd=repo).stdout.strip()
    second = run(WORKSPACE, repo / 'plan.md', cwd=repo).stdout.strip()
    assert Path(first).resolve() == Path(second).resolve()


@pytest.mark.parametrize(
    'argv, message',
    [
        ([], 'usage: sdd-workspace'),
        (['plan.md', 'extra'], 'usage: sdd-workspace'),
        (['nosuch.md'], 'no such plan file'),
        # A directory reaches the same rejection as a missing file: [ -f ]
        # is false for both. This is the case that makes the slug guard for
        # '.' unreachable, and it is the behavior worth pinning — a caller
        # who passes a directory must not get a workspace named after it.
        (['.'], 'no such plan file'),
    ],
)
def test_workspace_rejects_bad_arguments(repo, argv, message):
    result = run(WORKSPACE, *argv, cwd=repo)
    assert result.returncode == 2
    assert message in result.stderr
```

> Deviation: this step's comment calls the slug guard for `""`/`.`/`..`
> unreachable, following the plan's own framing. Review showed that framing
> is wrong: a plan file literally named `..md` is a regular file, passes
> `[ -f ]`, and `basename "..md" .md` returns `.` — reaching the guard. The
> guard was kept exactly as specified either way; no test was added
> claiming to exercise it, per this step's own instruction.

- [x] **Step 2: Run them to verify they fail**

```bash
cd skills/subagent-driven-development/scripts && uv run --python 3.13 --with pytest python -m pytest -q -k workspace
```

Expected: FAIL. The current script ignores arguments, so the path assertions report `.sdd` where `.sdd/plan` was expected, and the argument-rejection cases exit 0 instead of 2.

- [x] **Step 3: Rewrite `sdd-workspace`**

Replace the whole file with:

```bash
#!/usr/bin/env bash
# Resolve and ensure the working-tree directory SDD uses for one plan's
# short-lived artifacts: task briefs, implementer reports, review packages,
# and the progress ledger. Print the directory's absolute path.
#
# The workspace is per plan. A flat workspace shared by every plan in a
# working tree let a later plan read an earlier plan's ledger as its own
# progress and skip tasks it had never run.
#
# The workspace lives in the working tree (not under .git/) because Claude Code
# treats .git/ as a protected path and denies agent writes there — which blocks
# an implementer subagent from writing its report file. A self-ignoring
# .gitignore at the .sdd parent covers every per-plan directory, keeping them
# out of `git status` and out of accidental commits without modifying any
# tracked file.
#
# Single source of truth for the workspace location, so task-brief and
# review-package cannot drift to different directories.
#
# Usage: sdd-workspace PLAN_FILE
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "usage: sdd-workspace PLAN_FILE" >&2
  exit 2
fi

plan=$1
[ -f "$plan" ] || { echo "no such plan file: $plan" >&2; exit 2; }

slug=$(basename "$plan" .md)
[ -n "$slug" ] && [ "$slug" != "." ] && [ "$slug" != ".." ] \
  || { echo "cannot derive a workspace name from: $plan" >&2; exit 2; }

root=$(git rev-parse --show-toplevel)
base="$root/.sdd"
dir="$base/$slug"
mkdir -p "$dir"
printf '*\n' > "$base/.gitignore"
cd "$dir" && pwd
```

- [x] **Step 4: Run the workspace tests to verify they pass**

```bash
cd skills/subagent-driven-development/scripts && uv run --python 3.13 --with pytest python -m pytest -q -k workspace
```

Expected: PASS, 8 tests (4 named plus the 4 parametrized argument cases).

- [x] **Step 5: Update `task-brief` to pass the plan through**

In `skills/subagent-driven-development/scripts/task-brief`, change the usage comment (lines 8-10) to:

```bash
# Usage: task-brief PLAN_FILE TASK_NUMBER [OUTFILE]
# Default OUTFILE: <repo-root>/.sdd/<plan-basename>/task-<N>-brief.md
# (per plan and per worktree; concurrent runs of the SAME plan share it).
```

Then change the `sdd-workspace` call so it passes the plan. The line currently reads:

```bash
  dir=$("$(cd "$(dirname "$0")" && pwd)/sdd-workspace")
```

Replace it with:

```bash
  dir=$("$(cd "$(dirname "$0")" && pwd)/sdd-workspace" "$plan")
```

`task-brief`'s own signature does not change — it already takes `PLAN_FILE` as argument 1.

> Deviation: the plan omitted that
> `test_task_brief_writes_to_and_prints_the_default_workspace_path` also
> needed its expected path updated to `.sdd/plan/` — `task-brief`'s test
> still asserted the old flat path. The implementer caught it during this
> step; required for the 21-test passing state.

- [x] **Step 6: Write the failing tests for `review-package`'s new signature**

In the `# ── review-package ──` section, add `repo / 'plan.md'` as the first argument to all four existing `run(REVIEW_PACKAGE, ...)` calls, and update the default-path expectation. The four calls become:

```python
    result = run(REVIEW_PACKAGE, repo / 'plan.md', 'HEAD~1', 'HEAD', out, cwd=repo)
```
```python
    result = run(REVIEW_PACKAGE, repo / 'plan.md', 'nosuchrev', 'HEAD', repo / 'p.diff', cwd=repo)
```
```python
    result = run(REVIEW_PACKAGE, repo / 'plan.md', 'HEAD', 'nosuchrev', repo / 'p.diff', cwd=repo)
```
```python
    result = run(REVIEW_PACKAGE, repo / 'plan.md', 'HEAD~1', 'HEAD', cwd=repo)
```

In `test_review_package_writes_to_and_prints_the_default_workspace_path`, the expected path gains the plan directory. That line currently reads:

```python
    expected = repo / ".sdd" / f"review-{shortbase}..{shorthead}.diff"
```

Replace it with:

```python
    expected = repo / '.sdd' / 'plan' / f'review-{shortbase}..{shorthead}.diff'
```

`shortbase` and `shorthead` are already defined a few lines above in the same test; do not redefine them.

Then add one test for the new rejection case:

```python
def test_review_package_rejects_a_missing_plan_file(repo):
    """PLAN_FILE is argument 1. A caller still passing the old
    BASE HEAD OUTFILE form must fail loudly, not write a package into the
    wrong plan's workspace."""
    (repo / 'a.txt').write_text('one\n')
    git('add', 'a.txt', 'plan.md', cwd=repo)
    git('commit', '-qm', 'first', cwd=repo)
    result = run(REVIEW_PACKAGE, 'HEAD', 'HEAD', repo / 'p.diff', cwd=repo)
    assert result.returncode == 2
    assert 'no such plan file' in result.stderr
```

- [x] **Step 7: Run them to verify they fail**

```bash
cd skills/subagent-driven-development/scripts && uv run --python 3.13 --with pytest python -m pytest -q -k review_package
```

Expected: FAIL. The current script reads the plan path as `BASE` and reports `bad BASE:` for it.

- [x] **Step 8: Update `review-package`**

Change the usage comment (lines 7-8) to:

```bash
# Usage: review-package PLAN_FILE BASE HEAD [OUTFILE]
# Default OUTFILE: <repo-root>/.sdd/<plan-basename>/review-<base7>..<head7>.diff
```

Change the argument block. It currently reads:

```bash
if [ $# -lt 2 ] || [ $# -gt 3 ]; then
  echo "usage: review-package BASE HEAD [OUTFILE]" >&2
  exit 2
fi

base=$1
head=$2
```

Replace with:

```bash
if [ $# -lt 3 ] || [ $# -gt 4 ]; then
  echo "usage: review-package PLAN_FILE BASE HEAD [OUTFILE]" >&2
  exit 2
fi

plan=$1
base=$2
head=$3
[ -f "$plan" ] || { echo "no such plan file: $plan" >&2; exit 2; }
```

Then update the OUTFILE branch, which currently reads:

```bash
if [ $# -eq 3 ]; then
  out=$3
else
  dir=$("$(cd "$(dirname "$0")" && pwd)/sdd-workspace")
```

Replace with:

```bash
if [ $# -eq 4 ]; then
  out=$4
else
  dir=$("$(cd "$(dirname "$0")" && pwd)/sdd-workspace" "$plan")
```

Leave the two `git rev-parse --verify` checks and everything below unchanged.

- [x] **Step 9: Run the whole suite**

```bash
cd skills/subagent-driven-development/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: PASS. 21 tests — the 14 that existed, minus the 2 replaced workspace tests (12), plus 8 workspace test instances (4 named plus 4 parametrized) and 1 new review-package rejection test.

- [x] **Step 10: Commit**

```bash
git add skills/subagent-driven-development/scripts/
git commit -m "fix(sdd): scope the workspace to one plan

A flat .sdd/ had no plan identity, so a second plan executed in the same
working tree read the first plan's ledger as its own progress and skipped
tasks it had never run. sdd-workspace now takes the plan file and resolves
.sdd/<plan-basename>/; task-brief and review-package pass it through.

review-package gains PLAN_FILE as its first argument, matching its two
sibling scripts so all three take the plan as argument 1. The self-ignoring
guard stays at .sdd/.gitignore, the parent, covering every per-plan sibling."
```

---

### Task 2: Update SKILL.md for the plan-scoped workspace and its end of life

**Files:**
- Modify: `skills/subagent-driven-development/SKILL.md:217-228` (Plan Completion)
- Modify: `skills/subagent-driven-development/SKILL.md:265-292` (Durable Progress)
- Modify: `skills/subagent-driven-development/SKILL.md:229-264` (File Handoffs — the `review-package` call sites)

**Interfaces:**
- Consumes: Task 1's `sdd-workspace PLAN_FILE` and `review-package PLAN_FILE BASE HEAD [OUTFILE]`.

No tests. This is skill text; per the Global Constraints an assertion that a phrase appears in `SKILL.md` would pass without the behavior existing.

- [x] **Step 1: Fix the ledger path in Durable Progress**

`SKILL.md:272-276` currently tells a resuming controller to run `sdd-workspace` bare and then `cat` a hardcoded flat path:

````markdown
- At skill start, run this skill's `scripts/sdd-workspace` (it creates the
  workspace and its self-ignoring .gitignore), then check for a ledger:
  `cat "$(git rev-parse --show-toplevel)/.sdd/progress.md"`. Tasks listed there
  as complete are DONE — do not re-dispatch them; resume at the first task
  not marked complete.
````

Replace with:

````markdown
- At skill start, run this skill's `scripts/sdd-workspace <plan-file>` once and
  keep the directory it prints — it creates this plan's workspace and the
  self-ignoring .gitignore that covers every plan's:
  `WORKSPACE=$(scripts/sdd-workspace <plan-file>)`. Then check for a ledger:
  `cat "$WORKSPACE/progress.md"`. Tasks listed there as complete are DONE — do
  not re-dispatch them; resume at the first task not marked complete.
- The workspace is per plan, so that ledger is always this plan's. Its first
  line names the plan it belongs to; if that name is not the plan in your hand,
  stop and say so rather than resuming against it.
````

> Deviation: the implementer also corrected the Durable Progress
> `git clean -fdx` bullet, which still described "the workspace's own
> .gitignore" — stale once Task 1 moved the self-ignoring guard to the
> `.sdd` parent so it covers every sibling plan. Reviewer confirmed the fix
> as correct and in scope for this step's section.

- [x] **Step 2: Add the ledger's plan-naming line**

In the same Durable Progress section, the ledger currently gains entries only for completed tasks. Add, immediately before the bullet beginning "When a task's review comes back clean":

````markdown
- When you create the ledger, write its first line as
  `Plan: <plan-file-path>`. A workspace is named from the plan's basename, so
  two plans with the same basename in different directories would collide;
  this line is what makes that visible instead of silent.
````

- [x] **Step 3: Update the `review-package` call sites in File Handoffs**

Read `SKILL.md:229-264`. Every `review-package` invocation shown there takes the old `BASE HEAD` form. Add the plan file as the first argument to each, so they read `review-package <plan-file> <base> <head>`. Leave the surrounding DIFF_FILE contract prose intact — only the command form changes.

> Deviation: scope expanded by the controller from the plan's one SKILL.md
> range to seven stale call sites across four files (`SKILL.md`,
> `task-reviewer-prompt.md`, `requesting-code-review/SKILL.md`,
> `requesting-code-review/code-reviewer.md`), plus `CLAUDE.md`'s test count
> (14→21, stale after Task 1's suite growth). All seven verified by grep
> against `review-package`'s new signature before fixing.

- [x] **Step 4: Add workspace deletion to Plan Completion**

At the end of the Plan Completion section (`SKILL.md:217-228`), after the existing paragraph and before the `## File Handoffs` heading, add:

````markdown
When the plan-completion protocol has finished and the final review's fixes
are merged, delete this plan's workspace — the `$WORKSPACE` you resolved at
skill start: `rm -rf "$WORKSPACE"`. Git history is the record now. Sibling
directories under `.sdd/` belong to other plans — leave them alone, and never
`rm -rf .sdd` itself.

Order matters. The delete runs **after** the protocol, never before: the
resolve-before-defer gate reads this run's leftovers — the ledger, unfixed
review findings, deferred-Minor confirmations — to build its batched questions
and the `specs/deferred_items.md` entries. Deleting the workspace first
destroys the protocol's input.
````

- [x] **Step 5: Verify by reading**

Re-read the three edited sections start to finish. Confirm: no remaining bare `scripts/sdd-workspace` call without a plan argument, no remaining `.sdd/progress.md` flat path, every `review-package` line has four or five whitespace-separated fields, and the deletion paragraph sits after the protocol paragraph rather than before it.

```bash
grep -n "sdd-workspace\|review-package\|\.sdd/" skills/subagent-driven-development/SKILL.md
```

Expected: every `sdd-workspace` occurrence is followed by a plan argument; no occurrence of `.sdd/progress.md`.

- [x] **Step 6: Commit**

```bash
git add skills/subagent-driven-development/SKILL.md
git commit -m "docs(sdd): teach SKILL.md the plan-scoped workspace

The resume path hardcoded a flat .sdd/progress.md, which after Task 1
resolves to nothing; the ledger now lives per plan and names its plan on
line 1. review-package call sites gain the plan argument. Plan Completion
gains workspace deletion, sequenced strictly after the protocol so the
resolve-before-defer gate still has its input."
```

---

### Task 3: Ban nested subagents and add the illegible-evidence rule

**Files:**
- Modify: `skills/subagent-driven-development/implementer-prompt.md`
- Modify: `skills/subagent-driven-development/task-reviewer-prompt.md` (both the Short Form at `:15` and the Full Form at `:44`)
- Modify: `skills/requesting-code-review/code-reviewer.md`
- Modify: `agents/task-reviewer.md`
- Modify: `agents/code-reviewer.md`

**Interfaces:**
- Consumes: nothing from earlier tasks.

The two agent definitions already declare `tools: Read, Grep, Glob, Bash` with no Agent tool, so spawning is structurally impossible on that path. The prose still goes in both, because `task-reviewer-prompt.md:10` routes to `general-purpose` with the Full Form whenever the agent is not installed, and the implementer is always `general-purpose`.

No tests — skill text.

- [x] **Step 1: Add the ban to the implementer prompt**

In `skills/subagent-driven-development/implementer-prompt.md`, add this section immediately before the self-review instructions:

````markdown
## You Do Not Dispatch Subagents

Do all of this task's work yourself. Never spawn a subagent to implement part
of the task, and above all never spawn a reviewer to check your work.
Self-review means reading your own diff. Review is the controller's job: after
you report, it dispatches a fresh reviewer against your diff. A reviewer you
spawn duplicates that review at full cost, and its approval counts for nothing
in the process. If you catch yourself thinking "an independent review would
strengthen my report" — that review is already scheduled. Report instead.
````

- [x] **Step 2: Add the ban and the evidence rule to both reviewer template forms**

Add this to `skills/subagent-driven-development/task-reviewer-prompt.md`, in **both** the Short Form (`:15`) and the Full Form (`:44`) bodies:

````markdown
## You Do Not Dispatch Subagents

Do all of this review yourself. Never spawn a subagent to review part of the
diff, and never spawn another reviewer for a second opinion. This process
already provides every review seat the work gets; a reviewer you spawn
duplicates one of them at full cost, and its verdict counts for nothing. If the
diff feels too large for one pass, review it in passes yourself and say so in
your report.

Evidence you cannot see is not evidence that doesn't exist. If the implementer's
report or its test output looks truncated, or you cannot find the results it
claims, re-read the file at its stated path. If it is genuinely missing or
garbled, report that as a gap for the controller. Re-running the suite to
regenerate what you failed to read is not verification — illegibility of the
evidence is not invalidation of it.
````

- [x] **Step 3: Add the ban to the whole-branch reviewer template**

Add the same "You Do Not Dispatch Subagents" section from Step 2 to
`skills/requesting-code-review/code-reviewer.md`. Include the evidence
paragraph as well — the final reviewer reads the same implementer reports.

- [x] **Step 4: Add both rules to the two agent definitions**

Add the Step 2 text to `agents/task-reviewer.md` and `agents/code-reviewer.md`. The Short Form dispatch relies on the agent definition to carry the review contract, so a rule that lives only in the prompt template applies on one dispatch path and not the other.

Do **not** change either file's `tools:` line. `Read, Grep, Glob, Bash` is what makes spawning impossible; the prose is the belt to that structural brace, and it is what travels when these skills are installed without the agents.

- [x] **Step 5: Verify by reading**

```bash
grep -c "You Do Not Dispatch Subagents" skills/subagent-driven-development/implementer-prompt.md skills/subagent-driven-development/task-reviewer-prompt.md skills/requesting-code-review/code-reviewer.md agents/task-reviewer.md agents/code-reviewer.md
```

Expected: `2` for `task-reviewer-prompt.md` (one per form) and `1` for each of the other four. Then read each insertion in place and confirm it reads as instruction to that specific agent, not as narration about the process.

- [x] **Step 6: Commit**

```bash
git add skills/subagent-driven-development/implementer-prompt.md \
        skills/subagent-driven-development/task-reviewer-prompt.md \
        skills/requesting-code-review/code-reviewer.md \
        agents/task-reviewer.md agents/code-reviewer.md
git commit -m "feat(sdd): forbid nested subagents, require re-reading illegible evidence

The implementer is dispatched as general-purpose with the full tool set and
no prohibition, so it could spawn a reviewer duplicating the one the
controller already schedules — full cost, verdict counts for nothing. The
agent definitions omit the Agent tool and so are structurally safe, but both
reviewer templates fall back to general-purpose when the agents are absent,
so the prose goes in every seat.

Reviewers also stop re-running suites to regenerate evidence they failed to
read: illegibility is not invalidation."
```

---

### Task 4: Batch small same-shape work

**Files:**
- Modify: `skills/subagent-driven-development/SKILL.md` (a new subsection under The Process, and one ledger bullet under Durable Progress)
- Modify: `skills/subagent-driven-development/task-reviewer-prompt.md` (both forms)
- Modify: `agents/task-reviewer.md`

**Interfaces:**
- Consumes: Task 2's ledger conventions.

`agents/code-reviewer.md` is deliberately **not** in this task's file list. Batching is per-task; that agent reviews the whole branch.

No tests — skill text.

- [x] **Step 1: Add the batching rule to SKILL.md**

Add to `skills/subagent-driven-development/SKILL.md`, as a subsection of The Process near the dispatch guidance:

````markdown
**Batch small same-shape work.** When the plan lists several tasks that are
each a small, independent edit of the same kind — the same one-line fix,
constant change, or field addition repeated across files — do not dispatch one
subagent per task. Compose ONE dispatch brief listing every file and its
change, send the whole batch to a single implementer, and review its diff as
one unit. Reserve one-dispatch-per-task for work that needs its own judgment,
its own tests, or its own review surface.

You write the batch brief yourself; `scripts/task-brief` still extracts exactly
one task and gains no multi-task mode. That is a deliberate exception to the
rule that task text stays out of your context: batching applies only to changes
small enough to state in a line each, so the cost is bounded — and teaching
`task-brief` to concatenate sections would pull full task text through your
context for exactly the tasks that need it least.
````

> Deviation: one Important fix round. As drafted, this step's text never
> said where the composed batch brief should live, but `[BRIEF_FILE]` is a
> REQUIRED reviewer input — so a batch had no artifact for the reviewer,
> and the file-by-file safeguard (Task 4 Step 3) could never fire against
> it. Fixed by adding the `batch-N-M-brief.md` convention (e.g.
> `batch-4-7-brief.md`, written to this plan's workspace) to this section.

- [x] **Step 2: Add the ledger rule for batched dispatches**

In Durable Progress, after the bullet about appending a completion line, add:

````markdown
- A batched dispatch gets ONE ledger entry naming every task number it covered:
  `Tasks 4-7: complete (batched; commits <base7>..<head7>, review clean)`. A
  resuming controller reads task numbers from that line, so a batch recorded
  under only its first task's number re-dispatches the rest.
````

- [x] **Step 3: Add the file-by-file check to both reviewer forms and the agent**

Add to both forms of `skills/subagent-driven-development/task-reviewer-prompt.md` and to `agents/task-reviewer.md`:

````markdown
## Batched Dispatches

If the brief lists several files each with its own change, check the diff
against that list file by file: every listed file must have its corresponding
hunk. A listed file the diff never touches is a Missing finding, no matter how
clean the rest of the batch looks. Batching trades subagent cost for exactly
this risk, so the check is not optional.
````

- [x] **Step 4: Verify by reading**

Confirm the SKILL.md subsection sits with the dispatch guidance rather than in the review sections, and that the file-by-file rule appears twice in `task-reviewer-prompt.md` and once in `agents/task-reviewer.md`.

```bash
grep -c "Batched Dispatches" skills/subagent-driven-development/task-reviewer-prompt.md agents/task-reviewer.md agents/code-reviewer.md
```

Expected: `2`, `1`, and `0` respectively — the whole-branch reviewer must not gain it.

- [x] **Step 5: Commit**

```bash
git add skills/subagent-driven-development/SKILL.md \
        skills/subagent-driven-development/task-reviewer-prompt.md \
        agents/task-reviewer.md
git commit -m "feat(sdd): batch small same-shape tasks into one dispatch

Plans here are written bite-sized by policy, which is where per-task
dispatch overhead dominates. Several same-shape one-line edits now go to one
implementer and get reviewed as one diff.

The safeguard is not optional: a batched review checks the diff against the
brief's file list file by file, and a listed file the diff never touches is a
Missing finding. Without it, batching trades cost for silent omissions. The
ledger records a batch under every task number it covered, so a resume does
not re-dispatch the tail of a completed batch."
```

---

### Task 5: Bound the review loop

**Files:**
- Create: `skills/subagent-driven-development/re-review-prompt.md`
- Modify: `skills/subagent-driven-development/SKILL.md:160-168` (Handling Reviewer ⚠️ Items and the fix loop)
- Modify: `skills/subagent-driven-development/SKILL.md:326-331` (Prompt Templates list)

**Interfaces:**
- Consumes: Task 3's reviewer rules — the re-review template inherits the no-nested-subagent ban and the illegible-evidence rule.

No tests — skill text.

- [x] **Step 1: Create the scoped re-review template**

Create `skills/subagent-driven-development/re-review-prompt.md`:

````markdown
# Scoped Re-Review Prompt Template

Use this template when dispatching a re-review after an implementer has fixed
a previous round's findings. It is scoped: the re-reviewer checks whether each
finding was addressed, not whether the task as a whole is correct. The full
task review already happened.

**Routing:** dispatch to the `task-reviewer` agent if it is defined; otherwise
dispatch to `general-purpose`. Either way, paste the findings list and the diff
path — never your session history.

**Purpose:** Verify each finding from the previous review was addressed, and
that the fixes introduced nothing new.

## Dispatch Body

    You are re-reviewing fixes to one task. A previous review raised the
    findings below; an implementer has since amended the work.

    Findings from the previous round:
    <numbered findings, verbatim from the previous reviewer's report>

    The amended diff is at <DIFF_FILE>. The implementer's report, including
    its appended fix report, is at <REPORT_FILE>.

    For EACH numbered finding, return one verdict:
      ADDRESSED     — the diff resolves it; say which hunk does
      NOT ADDRESSED — it remains; say what is still missing

    Then report any NEW findings the fixes introduced, at the usual
    Critical / Important / Minor severities. Do not re-review parts of the
    task no finding touched — that review already happened and its cost is
    not worth paying twice.

    ## You Do Not Dispatch Subagents

    Do all of this review yourself. Never spawn a subagent for part of the
    diff or for a second opinion.

    Evidence you cannot see is not evidence that doesn't exist. If the
    report or its test output looks truncated, or you cannot find the
    results it claims, re-read the file at its stated path. If it is
    genuinely missing or garbled, report that as a gap. Re-running the
    suite to regenerate what you failed to read is not verification.

**Placeholders:** `<DIFF_FILE>` is the path printed by
`scripts/review-package <plan-file> <base> <head>`; `<REPORT_FILE>` is the
implementer's report path.

**Re-reviewer returns:** per-finding verdicts (ADDRESSED / NOT ADDRESSED) plus
any new findings.
````

- [x] **Step 2: Add the round cap and escalation ladder to SKILL.md**

After the Handling Reviewer ⚠️ Items section (`:160-168`), add:

````markdown
## Fix Rounds

A task gets at most **five fix attempts**. Adjudication follows the fifth; it
is not itself an attempt.

| Round | Action |
|---|---|
| 1-3 | Resume the same implementer with the findings. It appends a fix report to its existing report file: what changed, the covering tests it ran, the command, and the output. |
| 4-5 | Dispatch a **fresh** implementer with the task brief and the findings. Raise reasoning effort when the prior rounds show a thorough attempt rather than a missing-context failure. |
| after 5 | The cap is reached. Adjudicate every still-open finding; dispatch no further fix rounds for this task. |

Re-review each round with the scoped [re-review-prompt.md](re-review-prompt.md),
not a fresh full review — the task review already happened, and re-reading the
whole task every round is the cost this cap exists to bound.

Going fresh at round 4 is the load-bearing half. A resumed implementer carries
its own failed attempts as context, which anchors it to the approach that is not
working; a fresh one does not. Escalate in the order context, then effort, then
model, and stop when there is no headroom — sessions here already run at the
top of the model ladder, so in practice rounds 4-5 buy fresh context and higher
effort, not a bigger model.

**Adjudicating** means you rule on each open finding: record the load-bearing
ones as work, and park the rest in the ledger with your reasoning
(`Ruling: <what you decided> — <why> — <what it costs if wrong>`). Stop for your
human partner only when every path forward is a guess.
````

> Deviation: two fix rounds. Three passages outside this step's literal
> scope still described the pre-Task-5 unbounded full-review loop — the
> Process digraph's re-review edge routed to the full template, Example
> Workflow showed a full verdict, and Red Flags said "Repeat until
> approved" — and were reconciled to Fix Rounds. `re-review-prompt.md`
> (Step 1) did not tell the task-reviewer agent to set aside its own
> full-review contract and report format; live evidence this mattered came
> from re-reviews earlier in this same execution, which came back in the
> full report shape until the fix landed. The digraph's rounds-2-5 loop
> also funnelled every round through one generic fix-dispatch node, hiding
> the resume-vs-fresh switch this section calls load-bearing; now
> captioned outside the dot fence. Digraph validity reconfirmed with
> graphviz after both rounds.

- [x] **Step 3: Register the new template**

In the Prompt Templates list (`:326-331`), add between the task-reviewer and final-review lines:

````markdown
- [re-review-prompt.md](re-review-prompt.md) - Dispatch a scoped re-review after fixes (per-finding ADDRESSED / NOT ADDRESSED)
````

- [x] **Step 4: Verify by reading**

Confirm the ladder says five attempts with adjudication after, matching the spec — not four attempts, and not adjudication as round 5. Confirm the new file is reachable from the Prompt Templates list and that its link resolves.

```bash
ls skills/subagent-driven-development/re-review-prompt.md && grep -n "re-review-prompt.md" skills/subagent-driven-development/SKILL.md
```

Expected: the file exists and SKILL.md references it at least twice, once in Fix Rounds and once in Prompt Templates.

- [x] **Step 5: Commit**

```bash
git add skills/subagent-driven-development/re-review-prompt.md \
        skills/subagent-driven-development/SKILL.md
git commit -m "feat(sdd): bound the review loop with scoped re-review and a round cap

The fix loop had no cap, no scoped re-review, and no escalation: every round
re-read the whole task. Rounds are now capped at five, re-review is scoped to
per-finding ADDRESSED/NOT ADDRESSED verdicts, and rounds 4-5 dispatch a fresh
implementer rather than resuming one anchored to its own failed attempts.

Escalation follows this repo's context-then-effort-then-model order rather
than upstream's 'more capable model', which assumes headroom above the
model tier these sessions already run at."
```

---

### Task 6: Update NOTICE

**Files:**
- Modify: `NOTICE` (the superpowers "Changes from upstream" list)

**Interfaces:**
- Consumes: every preceding task — this records what they changed.

- [x] **Step 1: Read the current entry**

```bash
grep -n "Vendored on 2026-06-20" -A 60 NOTICE
```

The last two bullets describe the local script reworks: `c5ff0b5` moving the workspace to `.sdd/`, and `b8faf9c` reworking `task-brief`'s heading termination and Global Constraints prepending. Both remain true and must not be deleted.

- [x] **Step 2: Extend the change list**

Add to the "Changes from upstream" list, after the `b8faf9c` bullet:

````
  - Four changes were later adopted FROM upstream v6.1.0-v6.3.0 (see
    specs/completed/sdd-hardening.md): the plan-scoped workspace, the
    no-nested-subagent ban on the implementer and reviewer templates,
    same-shape task batching with its file-by-file diff check, and the
    bounded review loop with re-review-prompt.md. Two of them diverge
    deliberately. The workspace is .sdd/<plan-basename>/, keeping this
    repo's .sdd rename rather than upstream's .superpowers/sdd. The
    fix-round ladder escalates context, then effort, then model, rather
    than upstream's "more capable model" — these sessions already run at
    the top of the model ladder, so that rung has no headroom here.
    task-brief's local heading-termination and Global-Constraints rework
    survives unchanged: upstream's own change to that script was only the
    workspace call, so the two compose.
````

> Deviation: one fix round. NOTICE's cross-reference pointer ("see the
> c5ff0b5 and b8faf9c entries below") reached 2 of the 3 change events it
> needed to — 09a10ee changed the same three scripts again and was missed.
> Made count-independent: "(see the entries below)". The illegible-evidence
> rule adopted in Task 3 was also unreachable from any item in this change
> list; now named explicitly.

- [x] **Step 3: Run the provenance and frontmatter lints**

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py && uv run --python 3.13 python build/check_provenance.py && echo "both lints clean"
```

Expected: `both lints clean`.

- [x] **Step 4: Run the full script suite once more**

```bash
cd skills/subagent-driven-development/scripts && uv run --python 3.13 --with pytest python -m pytest -q
```

Expected: PASS, 21 tests.

- [x] **Step 5: Commit**

```bash
git add NOTICE
git commit -m "docs(NOTICE): record the four changes adopted from superpowers v6.3.0

Names the two deliberate divergences: the workspace keeps this repo's .sdd
rename, and the fix-round ladder escalates context-then-effort-then-model
rather than reaching for a model tier above the one these sessions run at."
```

---

## Notes for the executor

**The spec's § D wording is normative for the ladder.** Five attempts, adjudication after the fifth. If a reviewer reads the table as four attempts, the table is wrong and the prose above it governs.

**Tasks 3, 4, and 5 all edit skill text with no tests.** That is deliberate and recorded in the spec: a test asserting a phrase appears in `SKILL.md` would pass whether or not the behavior it describes exists, which is the string-presence trap. Verify these by reading the edits in place.

**Do not adopt upstream's compression campaign.** Several of the files touched here have Advantages, Key Principles, or Red Flags sections that upstream deleted in v6.2.0. Leave them. Compression is out of scope for this plan and, for the TDD skill, upstream measured that doing it carelessly regresses behavior.
