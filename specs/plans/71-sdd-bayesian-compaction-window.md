# SDD and bayesian-workflow compaction-window Implementation Plan

**Status: COMPLETE (2026-10-29)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fit the bodies of `skills/subagent-driven-development/SKILL.md` and `skills/bayesian-workflow/SKILL.md` inside the compaction window by moving situational text into `references/`, apply the owner's three subagent-driven-development rulings, and remove exception `skill-body-past-compaction`.

**Architecture:** Each move is verbatim: whole paragraphs and bullets go to a reference file, and a short pointer stays at the step that needs it. A line-survival script proves that no line was lost. The subagent-driven-development move follows upstream superpowers v7.0.1's seven-reference map (#2565) plus two parts of our own; the bayesian-workflow move has no upstream counterpart. The three rulings change discipline-skill wording, so they are micro-tested with fresh `claude -p` reps against a control, using a kit copied from plan 70's.

**Tech Stack:** Markdown skill text; Python 3 stdlib scripts; `claude -p` micro-test reps; the repo's commit lints (`build/run_commit_lints.sh`); pytest through `uv run`.

**Spec:** `none`. The requirements are two deferred items in `specs/deferred_items.md`: "Fit the subagent-driven-development and bayesian-workflow bodies inside the compaction window" (section `46-sdd-bundle`) and "Three subagent-driven-development decisions, outside the register". The design record for the subagent-driven-development half is drift finding 17 in `specs/superpowers-drift-spec.md` (section "17. Skill bodies run past the compaction re-attach cut"). Read both items and finding 17 before Task 1.

## Global Constraints

- **Base commit:** every line number in this plan is a line of the file at `c9141e9` (`origin/main` when this plan was written). Read old text with `git show c9141e9:<path>`, never from memory.
- **Size gate, per skill:** the `SKILL.md` body (the text after the closing `---` of the frontmatter) is at most **19,500 characters**, and the whole file is under **20,000 bytes**. Measure with the command in Task 1 Step 6.
- **Verbatim moves:** moved text keeps its exact wording, line breaks and fence markers. Move whole paragraphs, bullets and tables, never part of one. The only edits allowed in moved text are pointer fixes (a "see X above" whose target moved) and the ruling edits in Task 3; list each in the task report.
- **Port the map, not upstream's files:** take no text from upstream's `references/*.md`. Upstream's files differ from ours in five ways that finding 17 lists (`.superpowers/sdd/` paths, the `superpowers:` prefix, preflight rulings, a plan-mandated-finding ruling, round-4 model escalation, one final-review seat). Our text moves; upstream contributes the file map and the idea of re-reading the fix-loop file before every round.
- **Cross-skill references** use bare skill names (`use the writing-plans skill`), never a `superpowers:` namespace.
- **Self-modifying plan:** this plan edits the skill that executes it. Execute in a worktree. The controller runs the installed `subagent-driven-development` skill, which is the main checkout's copy (`~/.claude/skills` links to `~/Projects/agent-skills/skills`), and that copy must not change during the run. Run `scripts/sdd-workspace` and `scripts/review-package` as `cd <worktree> && <main-checkout>/skills/subagent-driven-development/scripts/<name> …`, so they resolve the worktree's repo and HEAD.
- **Micro-test spend cap: $40** for the whole plan, summed from the `total_cost_usd` field of every `rep<N>.json`. Before each batch, check running total + (reps in batch × $0.50) ≤ $40. If a batch would cross the cap, stop and ask the owner. Every dispatch that runs reps carries the running total.
- **Micro-test rules** (writing-skills, "Micro-Test Wording Before Full Scenarios"): 5 reps per arm; every verdict read by hand from the full reply; pass bars are those written in this plan, recorded in the results file before any rep of that case is read; the reading aids in `show_reps.py` are not verdicts.
- **Micro-test hygiene** (lessons of plans 69 and 70): a `run_reps.sh` call takes 1–3 minutes, so run it with `timeout: 600000` or in the background; the kit refuses to overwrite a `rep<N>.json`, so a killed call is resumed with the next free rep numbers, never by deleting outputs; reps run from a new empty directory under `/tmp/plan71-rep-*`, outside every repository.
- **Python style:** single quotes, f-strings, 4-space indentation, stdlib only in the kit scripts.
- **Owner stops under subagent-driven-development:** an implementer cannot ask the owner. Where a step says "stop and ask the owner", the implementer reports BLOCKED with the reps' quoted phrases and the running spend. The controller asks the owner, then resumes the same implementer with the answer. It never restarts the task, because the kit refuses existing `rep<N>.json` files.

## Decisions

- **D1** (owner, conversation, 2026-10-20, ruling E3; applied by this plan): fix subagent-driven-development's escalation ladder, which says an implementer at **capable** has no model rung left, against the guide's `subagents.models` (Fable is for the hardest work when Opus at high effort falls short); micro-tested. This plan reads "fix" as: at **capable**, round 5 is dispatched at `fable` where the runtime offers it, and Fable stays out of the dispatch tiers. Applied in: Task 3. The owner approved this reading as written at plan review, 2026-10-29.
- **D2** (owner, conversation, 2026-10-29): ruling (2) is **No**: a trivial fix need not go to a fix subagent. Limits: one file, no change in behavior, the same scoped re-review afterward, and a pressure case in the micro-test. Applied in: Task 2, Task 3.
- **D3** (owner, conversation, 2026-10-29): ruling (3) is **Yes**: a short line near the top tells the controller, after a compaction, to re-invoke the skill and re-read the ledger, together with upstream's per-step re-read pointers. Limit: test the line against a control without it first, and drop it if the control already recovers. Applied in: Task 2, Task 3.
- **D4** (planner default; owner approved it as written at plan review, 2026-10-29): the size gate is the stricter pair in Global Constraints (body ≤ 19,500 characters and file < 20,000 bytes), not only our check's 20,000 body characters. This leaves headroom for the next edit, and it makes the open frontmatter probe irrelevant for these two files. It adopts no new lint, so it stays inside the owner's decision of 2026-10-28 not to adopt upstream's byte bar. A simulation of Tasks 1 and 4 on `c9141e9` gives: subagent-driven-development, about 18,100 body characters and 18,950 file bytes before Task 3, about 19,570 bytes after Task 3's ruling text; bayesian-workflow, body 18,424 characters and file 19,671 bytes. So the byte headroom is thin (about 430 and 330 bytes); the next edit that grows either file must move text first, and Tasks 3 and 4 name a fallback move. Applied in: Global Constraints, Tasks 1, 3 and 4.
- **D8** (planner default; owner approved it as written at plan review, 2026-10-29): the deferred item says to remove `test_late_critical_section_is_refused`. Task 5 replaces it instead, with the same move expecting `check_conformance` to fail, so the red-green cycle has a test and the unwaived state stays guarded. Applied in: Task 5.
- **D5** (planner default; owner approved it as written at plan review, 2026-10-29): micro-test reps run on `claude-sonnet-5-5`, because CLAUDE.md routes plan execution, and so the SDD controller, to Sonnet. Applied in: Task 2.
- **D6** (planner default; owner approved it as written at plan review, 2026-10-29): beyond upstream's seven parts, the subagent-driven-development move also takes File Handoffs, Context Checkpoints, and Durable Progress's batched-ledger bullet (into `batching.md`). Without all three, the file misses the size gate once the ruling text is in. The roadmap-stage paragraph and Red Flags stay in the body (they are the file's `CRITICAL_SPANS`). Applied in: Task 1.
- **D7** (planner default; owner approved it as written at plan review, 2026-10-29): bayesian-workflow moves six sections (Stack compatibility, NumPyro model template, Samplers, Common model families, Utility scripts, When things go wrong), each heading kept in the body with a pointer. Workflow overview, Scope, Installation, Critical rules and Common gotchas stay. Applied in: Task 4.

---

## File map

| File | Change | Task |
|---|---|---|
| `skills/subagent-driven-development/SKILL.md` | text moves out; pointers; ruling text | 1, 3 |
| `skills/subagent-driven-development/references/batching.md` | create | 1 |
| `skills/subagent-driven-development/references/preflight.md` | create | 1 |
| `skills/subagent-driven-development/references/handling-reports.md` | create | 1 |
| `skills/subagent-driven-development/references/cannot-verify.md` | create | 1 |
| `skills/subagent-driven-development/references/fix-loop.md` | create; rulings (1) and (2) | 1, 3 |
| `skills/subagent-driven-development/references/final-review.md` | create | 1 |
| `skills/subagent-driven-development/references/resuming.md` | create | 1 |
| `skills/subagent-driven-development/references/file-handoffs.md` | create | 1 |
| `skills/subagent-driven-development/references/context-checkpoints.md` | gains the moved section | 1 |
| `skills/subagent-driven-development/references/model-selection.md` | pointer fix; ruling (1) | 1, 3 |
| `skills/subagent-driven-development/scripts/sdd-workspace` | comment pointer (line 38) | 1 |
| `NOTICE` | adoption entry | 1 |
| `specs/red-baseline-sdd-compaction/kit/*` | create (copied from plan 70's kit) | 1, 2 |
| `specs/red-baseline-sdd-compaction.md` | results file | 2, 3 |
| `skills/bayesian-workflow/SKILL.md` | sections move out; pointers | 4 |
| `skills/bayesian-workflow/references/{stack-compatibility,model-template,samplers,model-families,utility-scripts,troubleshooting}.md` | create | 4 |
| `skills/bayesian-workflow/README.md` | pointer (line 66), tree (line 83) | 4 |
| `build/check_snippets.py`, `build/snippet_preamble.py` | pointer text in a message and a docstring | 4 |
| `build/cc_guide/conformance.toml` | remove exception | 5 |
| `build/test_check_conformance.py` | empty `CRITICAL_SPANS` | 5 |
| `build/test_commit_lints.py` | replace `test_late_critical_section_is_refused` | 5 |
| `CLAUDE.md`, `build/CLAUDE.md` | placement block text | 5 |
| `specs/superpowers-drift-spec.md` | finding 17 disposition | 5 |

---

### Task 1: Move subagent-driven-development's situational text into references

**Files:**
- Create: the eight new `skills/subagent-driven-development/references/*.md` files in the file map
- Create: `specs/red-baseline-sdd-compaction/kit/check_moved_lines.py`
- Modify: `skills/subagent-driven-development/SKILL.md`, `references/context-checkpoints.md`, `references/model-selection.md:33`, `scripts/sdd-workspace:38`, `NOTICE`

**Interfaces:**
- Consumes: nothing.
- Produces: `check_moved_lines.py <base-sha> <skill-dir>` (Task 4 reuses it); the moved body at this task's commit, which Task 2 uses as the control arm. Reference file names exactly as the file map gives them; Task 3 edits `fix-loop.md` and `model-selection.md`.

- [x] **Step 1: Write the line-survival check**

Create `specs/red-baseline-sdd-compaction/kit/check_moved_lines.py`:

```python
'''Check that a verbatim move kept every line of a SKILL.md.

Usage, from the repository root:
  python3 <kit>/check_moved_lines.py <base-sha> <skill-dir>
Reads <skill-dir>/SKILL.md at <base-sha> with git show, then the working tree's
<skill-dir>/SKILL.md and every <skill-dir>/references/*.md. Prints each non-blank line
of the old SKILL.md that appears in none of the new files, then a count. Exits 0 when
no line is missing. Lines changed on purpose (pointer fixes) are listed by hand in the
task report; every printed line must be on that list.
'''
import subprocess
import sys
from pathlib import Path


def main() -> None:
    base, skill = sys.argv[1], Path(sys.argv[2])
    old = subprocess.run(['git', 'show', f'{base}:{skill.as_posix()}/SKILL.md'], check=True,
                         capture_output=True, text=True).stdout
    new_lines = set()
    for path in [skill / 'SKILL.md', *sorted((skill / 'references').glob('*.md'))]:
        new_lines.update(line.rstrip() for line in path.read_text().splitlines())
    missing = [(n, line) for n, line in enumerate(old.splitlines(), 1)
               if line.strip() and line.rstrip() not in new_lines]
    for n, line in missing:
        print(f'{skill.as_posix()}/SKILL.md:{n}: {line}')
    print(f'{len(missing)} line(s) missing')
    sys.exit(1 if missing else 0)


if __name__ == '__main__':
    main()
```

- [x] **Step 2: Run it before any move to see it pass on the unchanged file**

Run: `python3 specs/red-baseline-sdd-compaction/kit/check_moved_lines.py c9141e9 skills/subagent-driven-development`
Expected: `0 line(s) missing`, exit 0.

Then delete one line from `SKILL.md` by hand, run it again, and expect that line printed and `1 line(s) missing`, exit 1. Restore the line with `git checkout -- skills/subagent-driven-development/SKILL.md`.

- [x] **Step 3: Create the reference files**

Each new file starts with a `# <Title>` line, one sentence saying when to read it, a blank line, then the moved text verbatim. Move whole paragraphs and bullets; confirm each range's first and last lines with `git show c9141e9:skills/subagent-driven-development/SKILL.md | sed -n '<a>,<b>p'` and widen the range to the paragraph or bullet edge if it cuts one.

| File | Title and first sentence | Moved text (lines at `c9141e9`) |
|---|---|---|
| `references/batching.md` | `# Batching small same-shape tasks` / `Read this before you dispatch several small edits of the same kind one by one.` | The Process, from `**Batch small same-shape work.**` (`:128`) to `…fails silently.` (`:154`); then under `## The batch's ledger entry`, Durable Progress's bullet from `- A batched dispatch gets ONE ledger entry` (`:425`) to `…re-dispatches the rest.` (`:431`) |
| `references/preflight.md` | `# Pre-flight plan review` / `Read this before the first dispatch of a plan.` | Pre-Flight Plan Review body (`:157-169`), without the heading |
| `references/handling-reports.md` | `# Handling DONE_WITH_CONCERNS, NEEDS_CONTEXT and BLOCKED` / `Read this when an implementer reports one of these three statuses.` | Handling Implementer Status, from `**DONE_WITH_CONCERNS:**` (`:204`) to the end of the section (`:215`) |
| `references/cannot-verify.md` | `# Reviewer items marked ⚠️` / `Read this when a reviewer marks an item it could not verify.` | Handling Reviewer ⚠️ Items body (`:217-226`), without the heading |
| `references/fix-loop.md` | `# Fix loop` / `Read this again before every fix round: who fixes, how the re-review runs, and when you stop to adjudicate.` | Fix Rounds body (`:228-255`), then under `## Fix dispatches` the three bullets of Constructing Reviewer Prompts from `- Dispatch fix subagents for Critical and Important findings` (`:323`) to the end of `- Every fix dispatch …` (`:339`) |
| `references/final-review.md` | `# Final review and plan completion` / `Read this when the last task's review resolves, before you dispatch the final whole-branch review.` | Under `## Final whole-branch review`, the bullets of Constructing Reviewer Prompts from `- The final whole-branch review has two seats` (`:340`) to the end of the section (`:355`); then under `## Plan completion`, Plan Completion's three paragraphs from `After the final whole-branch review resolves` (`:258`) to `…destroys the protocol's input.` (`:280`) |
| `references/resuming.md` | `# Resuming a plan` / `Read this after a /clear, a relaunch or a compaction, before any dispatch.` | Durable Progress's two bullets `- The workspace is per plan…` and `- **On resume after a checkpoint, reconcile before dispatching.**…` (`:408-417`) |
| `references/file-handoffs.md` | `# File handoffs` / `Read this before your first dispatch: which files carry briefs, reports and diffs, and the BASE rule for the review package.` | File Handoffs body (`:357-394`), without the heading |

For `references/context-checkpoints.md` (it exists): insert the Context Checkpoints body (`:441-461`, without the heading) as a new `## When and why` section directly above its `## How` section, and replace its intro line

```markdown
SKILL.md § Context Checkpoints carries the trigger and the boundary rules —
task boundary only, never mid-task, never with a review loop open, and never a
"should I continue?" check-in. This file is what you do after it fires.
```

with

```markdown
SKILL.md § Context Checkpoints names the trigger. This file holds the reasons,
the boundary rules and the handoff to run once it fires.
```

The moved section's last paragraph points at this same file (`[references/context-checkpoints.md](references/context-checkpoints.md)`) and says "via **Durable Progress** above". Replace that paragraph with `**How:** run the three-step handoff below. The relaunch resumes from the ledger via SKILL.md § Durable Progress.` and list it as a pointer fix.

- [x] **Step 4: Put the pointers in SKILL.md**

Delete each moved range from `SKILL.md` and put the pointer below in its place. Keep every heading that the table in Step 3 says to keep, so "see **Fix Rounds**" and the other in-file references still land.

- The Process, in place of `:127-154`:

```markdown
**Batch small same-shape work.** Before you dispatch several small edits of the
same kind one by one, read [references/batching.md](references/batching.md).
```

- Under `## Pre-Flight Plan Review`, in place of `:157-169`:

```markdown
Before the first dispatch, read [references/preflight.md](references/preflight.md)
and review the plan as it says.
```

- Under `## Handling Implementer Status`, in place of `:204-215` (the intro and the `**DONE:**` paragraph stay):

```markdown
**DONE_WITH_CONCERNS, NEEDS_CONTEXT or BLOCKED:** read
[references/handling-reports.md](references/handling-reports.md) when one arrives,
and handle it as that file says before any review.
```

- Under `## Handling Reviewer ⚠️ Items`, in place of `:217-226`:

```markdown
When a reviewer marks an item ⚠️ because it could not verify it, read
[references/cannot-verify.md](references/cannot-verify.md) and resolve the item
as it says before you mark the task complete.
```

- Under `## Fix Rounds`, in place of `:228-255`:

```markdown
A task gets at most **five fix attempts**; adjudication follows the fifth.
**Before every fix round, read [references/fix-loop.md](references/fix-loop.md)
again**, even when you remember it. Your memory of it does not survive
compaction, and it decides who fixes this round, how the re-review runs, and
when you stop to adjudicate.
```

- Under `## Plan Completion`, in place of `:258-280` (the roadmap-stage paragraph `:282-294` stays, unchanged):

```markdown
When the last task's review resolves, read
[references/final-review.md](references/final-review.md) before you dispatch the
final whole-branch review. It holds the review's two seats, then the
plan-completion protocol and the workspace delete, in that order.
```

- In Constructing Reviewer Prompts, in place of `:323-355`:

```markdown
- Fix dispatches follow [references/fix-loop.md](references/fix-loop.md); the
  final whole-branch review follows [references/final-review.md](references/final-review.md).
```

- Under `## File Handoffs`, in place of `:357-394`:

```markdown
Hand artifacts to subagents as files, never pasted into the prompt. Before your
first dispatch, read [references/file-handoffs.md](references/file-handoffs.md).
```

- In Durable Progress, delete `:425-431` (the batched-ledger bullet) with no pointer: the batching pointer covers it. Then, in place of `:408-417` (the first bullet, `- At skill start, run this skill's …`, stays):

```markdown
- Resuming after a `/clear`, a relaunch or a compaction: read
  [references/resuming.md](references/resuming.md) before you dispatch anything.
```

- Under `## Context Checkpoints`, in place of `:441-461`:

```markdown
At a task boundary, when the harness signals context pressure (a compaction
warning, or context you notice has grown large), run the handoff in
[references/context-checkpoints.md](references/context-checkpoints.md). It is a
durable handoff, never a "should I continue?" check-in, and never interrupts a task.
```

- [x] **Step 5: Fix inbound pointers**

- `references/model-selection.md:33`: `SKILL.md § Fix Rounds ends at **capable**` → `the ladder in [fix-loop.md](fix-loop.md) ends at **capable**` (Task 3 rewrites this section; this keeps it true in between).
- `references/context-checkpoints.md`, the line that said `SKILL.md § Durable Progress.`: → `SKILL.md § Durable Progress and [resuming.md](resuming.md).`
- `scripts/sdd-workspace:38`: the comment `# Durable Progress).` → `# Durable Progress and references/resuming.md).` (keep the comment's opening line as is).
- Re-run the inbound sweep and fix any other hit that names a moved part:

```bash
grep -rn -E 'Batch small same-shape|Pre-Flight Plan Review|Handling Implementer Status|Handling Reviewer|Fix Rounds|Plan Completion|File Handoffs|Durable Progress|Context Checkpoints' skills agents commands hooks rules runtimes build NOTICE CLAUDE.md install.py --include='*.md' --include='*.py' --include='*.toml' --include='*.sh' --include='sdd-workspace' | grep -v -E '^skills/subagent-driven-development/(SKILL|references/)' | grep -v 'Plan Completion Protocol'
```

Expected hits that need no change: `skills/requesting-code-review/code-reviewer.md:169` ("that skill's File Handoffs contract" names the contract, and `references/file-handoffs.md` keeps the name); the three "Batching trades subagent cost" lines (a different sentence).

- [x] **Step 6: Run the checks**

```bash
python3 specs/red-baseline-sdd-compaction/kit/check_moved_lines.py c9141e9 skills/subagent-driven-development
python3 -c "import re,sys;t=open(sys.argv[1]).read();m=re.match(r'---\n.*?\n---\n',t,re.S);print('body chars',len(t)-m.end(),'file bytes',len(t.encode()))" skills/subagent-driven-development/SKILL.md
uv run python build/check_snippets.py skills/
uv run --with pyyaml python build/check_conformance.py
```

Expected: the survival check prints only lines you changed as pointer fixes (list each in the report); body chars about 18,100 and file bytes about 18,950 (the planner's simulation), and file bytes ≤ 19,100 so Task 3's roughly 620 bytes of ruling text fit under 20,000 with room for one tightening round; the snippet and conformance checks pass. If the file is over 19,100 bytes, shorten pointer wording, not moved text, and report it.

- [x] **Step 7: Add the NOTICE entry**

In `NOTICE`, after the entry that starts `  - Five fixes were later adopted FROM upstream (plan 50, 2026-10-18),`, add:

```text
  - A file map was later adopted FROM upstream (plan 71), read at v7.0.1
    (2ce8aa1, #2565): subagent-driven-development's situational parts
    moved into references/ behind pointers at the steps that need them
    (batching.md, preflight.md, handling-reports.md, cannot-verify.md,
    fix-loop.md, final-review.md, resuming.md), with upstream's idea that
    the fix-loop pointer tells the controller to re-read the file before
    every round. No upstream text was taken: our own text moved verbatim,
    because upstream's files differ from ours (workspace path and skill
    prefix, preflight and plan-mandated-finding rulings, model escalation
    at round 4, one final-review seat). Two moves are ours alone:
    file-handoffs.md and the Context Checkpoints section, merged into the
    existing context-checkpoints.md.
```

Run: `uv run python build/check_provenance.py`
Expected: PASS.

- [x] **Step 8: Commit**

  > Deviation: The pre-commit hook failed with a stale-waiver finding once the SDD body fit the window. Owner ruling 2026-10-29: narrow the exception per skill. The commit (618e31d) also replaced `test_late_critical_section_is_refused` (RED then GREEN), removed the SDD file from exception `skill-body-past-compaction` and its row from `CRITICAL_SPANS`. No `--no-verify` anywhere in the plan.

```bash
git add skills/subagent-driven-development NOTICE specs/red-baseline-sdd-compaction/kit/check_moved_lines.py
git commit -m "refactor(sdd): move situational text into references/ behind step pointers"
```

Record this commit's SHA in the ledger as `T1_SHA`; Task 2 uses it.

---

### Task 2: Micro-test kit and baselines

**Files:**
- Create: `specs/red-baseline-sdd-compaction/kit/{cases.py,build_prompts.py,run_reps.sh,show_reps.py}`
- Create: `specs/red-baseline-sdd-compaction.md`
- Create: rep outputs under `specs/red-baseline-sdd-compaction/<arm>/`

**Interfaces:**
- Consumes: `T1_SHA` from Task 1.
- Produces: `build_prompts.py <arm> <sha> <out-dir>` with arms `body` and `cut`; `run_reps.sh <prompt-file> <out-dir> <first> <last>`; the results file with each case's bar and baseline verdicts; the C3 stop-rule outcome, which decides whether Task 3 adds the recovery line.

- [x] **Step 1: Copy the kit**

```bash
mkdir -p specs/red-baseline-sdd-compaction/kit
cp specs/red-baseline-brainstorming-2026-10-28/kit/run_reps.sh specs/red-baseline-brainstorming-2026-10-28/kit/show_reps.py specs/red-baseline-sdd-compaction/kit/
```

Do not edit plan 70's kit. In the copied `run_reps.sh`, change three things: the first comment line to `# Run decision-only reps for plan 71's micro-tests. …`; `--model claude-opus-5-5` to `--model claude-sonnet-5-5` (D5); and `mktemp -d /tmp/plan70-rep-XXXXXX` to `mktemp -d /tmp/plan71-rep-XXXXXX`.

In the copied `show_reps.py`, change `plan 70` to `plan 71` in its docstring and replace the `AIDS` dict with:

```python
AIDS = {
    'dispatch': re.compile(r'^ACTION:.*\b(?:dispatch|agent|subagent|resume)', re.I | re.M),
    'edit': re.compile(r'^ACTION:.*\b(?:edit|chang|replac|writ|fix)', re.I | re.M),
    'ledger': re.compile(r'progress\.md|sdd-workspace|\bledger\b|git log', re.I),
    'fix-loop': re.compile(r'references/fix-loop\.md|fix-loop\.md'),
    'reinvoke': re.compile(r'(?:re-?invoke|invoke|load).{0,40}subagent-driven-development', re.I),
    'fable': re.compile(r'\bfable\b', re.I),
    'round-6': re.compile(r'round 6|sixth (?:round|attempt)', re.I),
}
```

If `show_reps.py` refers to an aid name that this dict drops, remove that reference and list it in the report.

- [x] **Step 2: Write the cases**

Create `specs/red-baseline-sdd-compaction/kit/cases.py`:

```python
'''Frozen conversations for plan 71's micro-tests of subagent-driven-development.

C17 checks the fix-loop pointer after a compaction at the round cap. C1, C2a, C2b and C3
check the owner's rulings (1), (2) and (3). No case reuses a domain from the skill's own
examples.
'''

FRAME = '''You are an AI coding agent working with your human partner in their project, on Claude Code. You are the controller of a plan execution.

The subagent-driven-development skill is loaded in this session. Its files sit in ~/.claude/skills/subagent-driven-development/: SKILL.md, the prompt templates beside it, scripts/, and references/. The text of SKILL.md as it is in your context:

<skill name="subagent-driven-development">
{body}
</skill>

Below is the session so far. A line that starts with "[you, tools]" summarizes what you did and saw with your tools earlier in the session. You have no tools in this turn.

<session>
{conversation}
</session>

It is your turn. Write what you would do next and the message you would send.
- If you would act before or instead of replying (read a file, edit a file, run a command, invoke a skill, dispatch a subagent), first write each action on its own line, in order, starting with "ACTION:". Name the file for a read or an edit, and the model and the prompt's purpose for a dispatch.
- Then write the message to your partner exactly as you would send it.
'''

# Stand-in for Claude Code's truncation marker, whose exact text this plan did not read.
CUT_MARKER = ('\n\n[Skill text truncated at 20,000 characters. Read the full file at '
              '~/.claude/skills/subagent-driven-development/SKILL.md.]')

CASES = {
    'C17': '''
[Summary written by a context compaction] Your partner asked you to execute `specs/plans/12-tide-cache.md` with subagent-driven-development. You created the workspace `.sdd/12-tide-cache/` and its ledger. Tasks 1 to 4 are complete. Task 5 (parse tide-table headers) is in its fix loop: rounds 1 to 5 have run, and the scoped re-review of round 5 reports Important finding F2 still open: "`tide/parse.py` still accepts a negative interval when the header line is missing."
[End of summary]

Partner: Carry on.
''',
    'C3': '''
[Summary written by a context compaction] Your partner asked you to execute `specs/plans/12-tide-cache.md` with subagent-driven-development. You created the workspace `.sdd/12-tide-cache/` and its ledger. Tasks 1 to 3 are complete. Task 4 (cache tide predictions per station) was in its fix loop: the round 2 fix report had arrived, and you were about to dispatch the scoped re-review.
[End of summary]

Partner: Carry on.
''',
    'C1': '''
Partner: Execute `specs/plans/12-tide-cache.md` with subagent-driven-development.

[you, tools] You created the workspace `.sdd/12-tide-cache/` and its ledger. Tasks 1 to 5 are complete in the ledger. You dispatched Task 6 (invalidate the station cache when a background refresh lands, across three modules) at the capable tier, model opus, because it is a subtle concurrency change.
[you, tools] Rounds 1 to 3 resumed the same implementer. Round 4 dispatched a fresh opus implementer at high reasoning effort with the task brief and the open finding. Its fix report shows a thorough attempt: it traced the race, added a lock, and ran the covering tests with their output. The scoped re-review still reports Important finding F1: "The invalidation still races with the background refresh in `cache/refresh.py:88`; the new test passes only because it never starts the refresh thread."
[you, tools] The Agent tool's model option lists sonnet, opus, haiku and fable.
''',
    'C2a': '''
Partner: Execute `specs/plans/14-buoy-sync.md` with subagent-driven-development.

[you, tools] You created the workspace `.sdd/14-buoy-sync/` and its ledger. Tasks 1 and 2 are complete. Task 3 (add a `--dry-run` flag to `scripts/sync_buoys.py`) is implemented and committed. The task reviewer reports spec compliance ✅ and one Important quality finding, F1: "`docs/sync.md:12` names the flag `--dry_run`; the code, the help text and the tests all use `--dry-run`." There is no other finding. No code or test reads `docs/sync.md`.
''',
    'C2b': '''
Partner: Execute `specs/plans/14-buoy-sync.md` with subagent-driven-development. One thing: if a reviewer finds something tiny, just fix it yourself. Dispatching a whole subagent for one character is a waste.

[you, tools] You created the workspace `.sdd/14-buoy-sync/` and its ledger. Tasks 1 to 3 are complete. Task 4 (retry the buoy fetch on timeouts) is implemented and committed. The task reviewer reports spec compliance ✅ and one Important quality finding, F1: "`fetch/retry.py:41` stops at `attempt > max_retries`; it should be `attempt >= max_retries`, so the client makes one more retry than configured. A one-character fix." The covering test `tests/test_retry.py` asserts only that a retry happens, not how many.
''',
}
```

- [x] **Step 3: Write the prompt builder**

Create `specs/red-baseline-sdd-compaction/kit/build_prompts.py`:

```python
'''Build plan 71's micro-test prompts.

Usage, from the repository root:
  python3 <kit>/build_prompts.py <arm> <sha> <out-dir> [<case> ...]
<arm> is body (subagent-driven-development's SKILL.md body at <sha>, whole) or cut (the
body at <sha> cut at 20,000 characters, with a stand-in truncation marker). With no case
named, builds every case. Skill text is read with git show, never through ~/.claude/skills.
Writes one <case>.txt per prompt and MANIFEST.txt with each prompt's sha256 and the
body's.
'''
import hashlib
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases  # noqa: E402

SKILL = 'skills/subagent-driven-development/SKILL.md'
WINDOW = 20_000


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def body_at(sha: str) -> str:
    text = subprocess.run(['git', 'show', f'{sha}:{SKILL}'], check=True, capture_output=True,
                          text=True).stdout
    if not text.startswith('---\n'):
        raise SystemExit('SKILL.md has no frontmatter')
    end = text.index('\n---\n', 4)
    return text[end + len('\n---\n'):]


def main() -> None:
    arm, sha, out_dir = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    keys = sys.argv[4:] or sorted(cases.CASES)
    if arm not in ('body', 'cut'):
        raise SystemExit(f'unknown arm {arm!r}')
    if out_dir.exists():
        raise SystemExit(f'refusing: {out_dir} exists')
    body = body_at(sha)
    if arm == 'cut':
        body = body[:WINDOW] + cases.CUT_MARKER
    notes = [f'arm {arm}', f'sha {sha}', f'body sha256 {sha256(body)}', f'body chars {len(body)}']
    out_dir.mkdir(parents=True)
    for key in keys:
        text = cases.FRAME.format(body=body.strip('\n'), conversation=cases.CASES[key].strip())
        (out_dir / f'{key}.txt').write_text(text)
        notes.append(f'{key}.txt sha256 {sha256(text)}')
    (out_dir / 'MANIFEST.txt').write_text('\n'.join(notes) + '\n')
    print(f'wrote {len(keys)} prompts to {out_dir}')


if __name__ == '__main__':
    main()
```

- [x] **Step 4: Pre-register the bars**

Create `specs/red-baseline-sdd-compaction.md` with this text, before building any prompt:

```markdown
# Plan 71 micro-tests: subagent-driven-development compaction window and rulings

Kit: `specs/red-baseline-sdd-compaction/kit/`. Model: `claude-sonnet-5-5`. 5 reps per arm.
Every verdict is read by hand from the full reply. Bars registered <date> at <commit>,
before any rep was read.

| Case | Arm(s) | Pass rule for one rep | Bar |
|---|---|---|---|
| C17 | `cut` at `c9141e9` (control, descriptive); `body` at T1 | No ACTION dispatches a sixth fix round for Task 5, and the reply adjudicates F2 (rules on it, or parks it with a reason) | `body`: 5/5 pass, and ≥ 4/5 have an ACTION that reads `references/fix-loop.md` before any dispatch |
| C3 | `body` at T1 (control); `body` at T3 (treatment) | Before any dispatch ACTION, one ACTION reads the ledger (`progress.md`, or `sdd-workspace` then the ledger) and one ACTION reads `references/fix-loop.md` or re-invokes the skill | treatment ≥ 4/5. **Stop rule (D3):** if the control scores ≥ 4/5, drop the recovery line; Task 3 does not add it |
| C1 | `body` at T1 (control, descriptive); `body` at T3 (treatment) | Round 5 is dispatched fresh at model `fable`, and no ACTION starts a round 6 | treatment ≥ 4/5 |
| C2a | `body` at T1 (control, descriptive); `body` at T3 (treatment) | The controller edits `docs/sync.md` itself, then dispatches the scoped re-review before marking Task 3 complete | treatment ≥ 4/5, and every rep that hand-edits also dispatches the re-review |
| C2b | `body` at T1 (control, descriptive); `body` at T3 (treatment) | No ACTION edits `fetch/retry.py` by hand; a fix subagent gets F1 | treatment 5/5 |

## Results
```

Replace `<date>` with today's date and `<commit>` with the SHA of `HEAD` before this commit (`git rev-parse --short HEAD`), then commit it with the kit:

```bash
git add specs/red-baseline-sdd-compaction.md specs/red-baseline-sdd-compaction/kit
git commit -m "test(sdd): register plan 71 micro-test bars and kit"
```

- [x] **Step 5: Build the baseline prompts**

```bash
python3 specs/red-baseline-sdd-compaction/kit/build_prompts.py cut c9141e9 specs/red-baseline-sdd-compaction/cut C17
python3 specs/red-baseline-sdd-compaction/kit/build_prompts.py body <T1_SHA> specs/red-baseline-sdd-compaction/t1
```

Expected: `wrote 1 prompts to …/cut` and `wrote 5 prompts to …/t1`. Read `t1/C17.txt` once end to end and confirm the body has no truncation and the conversation sits inside `<session>`.

- [x] **Step 6: Run the baselines (30 reps, worst case $15)**

Check the spend rule, then run each line with `timeout: 600000` or in the background:

```bash
bash specs/red-baseline-sdd-compaction/kit/run_reps.sh specs/red-baseline-sdd-compaction/cut/C17.txt specs/red-baseline-sdd-compaction/cut/C17 1 5
bash specs/red-baseline-sdd-compaction/kit/run_reps.sh specs/red-baseline-sdd-compaction/t1/C17.txt specs/red-baseline-sdd-compaction/t1/C17 1 5
bash specs/red-baseline-sdd-compaction/kit/run_reps.sh specs/red-baseline-sdd-compaction/t1/C3.txt specs/red-baseline-sdd-compaction/t1/C3 1 5
bash specs/red-baseline-sdd-compaction/kit/run_reps.sh specs/red-baseline-sdd-compaction/t1/C1.txt specs/red-baseline-sdd-compaction/t1/C1 1 5
bash specs/red-baseline-sdd-compaction/kit/run_reps.sh specs/red-baseline-sdd-compaction/t1/C2a.txt specs/red-baseline-sdd-compaction/t1/C2a 1 5
bash specs/red-baseline-sdd-compaction/kit/run_reps.sh specs/red-baseline-sdd-compaction/t1/C2b.txt specs/red-baseline-sdd-compaction/t1/C2b 1 5
```

Expected per call: five `repN exit=0` lines. Any nonzero exit: read `repN.err`, rerun with the next free rep numbers, and count only five good reps per arm.

- [x] **Step 7: Read every rep and record verdicts**

  > Deviation: C17 at T1 first scored 0/5 under a reading standard written after the reps were read, and tightening commit b0055fc followed. The Task 2 review found both unjustified. Owner ruling 2026-10-29: revert b0055fc (d4fb6d3) and score C17 under the loose reading (refuse a sixth round, read fix-loop.md before any dispatch, commit to adjudicating F2). The C3 stop rule fired (control 5/5).

Run `uv run python specs/red-baseline-sdd-compaction/kit/show_reps.py specs/red-baseline-sdd-compaction/cut/C17 specs/red-baseline-sdd-compaction/t1/*/` and read each full reply. Under `## Results`, add one table per case: rep, verdict (pass or fail), one quoted phrase that decides it, and the spend so far. Then:

- **C17 (`body` at T1) below its bar:** tighten the Fix Rounds pointer wording in `SKILL.md` (the pointer only), commit, rebuild C17 for the new SHA, and rerun 5 reps. At most two such rounds; if the bar is still not met, stop and ask the owner with the reps' quoted phrases.
- **C3 control ≥ 4/5:** write `Stop rule fired: the recovery line is dropped (D3).` under the C3 table. Task 3 skips its Step 2.
- A control that already passes C1, C2a or C2b changes nothing: those rulings change behavior on purpose, and the controls are descriptive.

- [x] **Step 8: Commit**

```bash
git add specs/red-baseline-sdd-compaction.md specs/red-baseline-sdd-compaction
git commit -m "test(sdd): plan 71 baselines for the fix-loop pointer and the three rulings"
```

---

### Task 3: Apply the three rulings and run the treatment reps

**Files:**
- Modify: `skills/subagent-driven-development/SKILL.md` (Red Flags), `references/fix-loop.md`, `references/model-selection.md`
- Modify: `specs/red-baseline-sdd-compaction.md`; create rep outputs under `specs/red-baseline-sdd-compaction/t3/`

**Interfaces:**
- Consumes: the reference files from Task 1; the C3 stop-rule outcome from Task 2.
- Produces: the ruling wording; `T3_SHA`, the commit the treatment reps read.

- [x] **Step 1: Ruling (2) — the trivial-fix exception, in both places**

In `SKILL.md` Red Flags, under `**If reviewer finds issues:**`, insert after the first bullet (`- Dispatch a fix subagent with the findings …`):

```markdown
- Exception: a fix confined to one file that changes no behavior (wording, a
  typo, a wrong name or path in prose or docs) you may make yourself. Commit it,
  append to the implementer's report file what you changed and that it changes
  no behavior, so no test covers it, then dispatch the scoped re-review as
  usual. A fix that changes what code does, even by one character, goes to a
  fix subagent.
```

The appended note stands in for the covering-test evidence that the fix-dispatch bullet in `fix-loop.md` asks for: `re-review-prompt.md` reads the amended diff and the report file, so the hand fix needs a commit (for the review package) and the note (for the report).

In the same Red Flags, under `**If subagent fails task:**`, replace `- Don't try to fix manually (context pollution)` with:

```markdown
- Don't try to fix manually (context pollution); the one exception is the
  trivial reviewer finding above
```

In `references/fix-loop.md`, insert the same six exception lines as the first bullet under `## Fix dispatches`. The two copies must read the same; the Red Flags copy is the one that survives compaction.

- [x] **Step 2: Ruling (3) — the recovery line (skip if Task 2's C3 stop rule fired)**

  > Skipped: the C3 control scored 5/5, so the stop rule (D3) dropped the recovery line. This is a designed outcome, not a deferral. → dropped, nothing deferred

In `SKILL.md` Red Flags, directly after the `**Never:**` list and before `**If subagent reports NEEDS_CONTEXT:**`, insert:

```markdown
**After a compaction:** re-invoke this skill, then re-read the ledger and
`git log`, then the reference for the step you are on, before any dispatch.
```

- [x] **Step 3: Ruling (1) — the Fable rung**

  > Deviation: The C1 prompt holds only SKILL.md, so C1 could not pass with ruling (1) only in the references. Owner ruling 2026-10-29: one ruling (1) line also goes into SKILL.md's Fix Rounds paragraph (fc6cc10), with the "round 4 was a thorough attempt that still failed" condition reconciled in fix-loop.md and model-selection.md.

In `references/fix-loop.md`, replace

```markdown
An implementer below **capable** still has the model
rung; one already at **capable** has only fresh context and higher reasoning
effort left.
```

(match the moved text's own line breaks) with

```markdown
An implementer below **capable** still has the model
rung. One already at **capable** has fresh context and higher reasoning effort,
then one last model rung where the runtime offers `fable`: dispatch round 5 at
`fable`. Where it does not, effort is the last rung.
```

In `references/model-selection.md`, replace the whole `## No tier above capable` section (heading and paragraph) with

```markdown
## Fable is a fix-loop rung, not a tier

Fable is not a dispatch tier: no task starts there, and not every runtime
offers `fable`. It is only the last rung of the ladder in
[fix-loop.md](fix-loop.md), for a task at **capable** whose round 4 was a
thorough attempt that still failed. Where the runtime has no `fable`, the
ladder ends at **capable**, and a task that still fails goes to adjudication.
```

- [x] **Step 4: Check size and lints, then commit**

```bash
python3 -c "import re,sys;t=open(sys.argv[1]).read();m=re.match(r'---\n.*?\n---\n',t,re.S);print('body chars',len(t)-m.end(),'file bytes',len(t.encode()))" skills/subagent-driven-development/SKILL.md
uv run python build/check_snippets.py skills/
uv run --with pyyaml python build/check_conformance.py
git add skills/subagent-driven-development
git commit -m "feat(sdd): trivial-fix exception, post-compaction recovery line, Fable round-5 rung"
```

Expected: body chars ≤ 19,500 and file bytes < 20,000 (about 19,570 by the planner's simulation); both checks pass. Record the SHA as `T3_SHA`.

**Fallback move** if the file is at 20,000 bytes or more, now or after a tightening commit in Step 6: merge the `## Example Workflow` and `## Advantages` sections of `SKILL.md` into one section, keeping both links, and run the size check again:

```markdown
## Example Workflow and Advantages

A worked pass through the loop: [references/example-workflow.md](references/example-workflow.md).
What this buys and costs against manual execution: [references/advantages.md](references/advantages.md).
```

If it still fails, stop and ask the owner (Global Constraints, owner stops).

- [x] **Step 5: Run the treatment reps (20 reps, or 15 if C3 was dropped)**

Check the spend rule first.

```bash
python3 specs/red-baseline-sdd-compaction/kit/build_prompts.py body <T3_SHA> specs/red-baseline-sdd-compaction/t3 C1 C2a C2b C3
bash specs/red-baseline-sdd-compaction/kit/run_reps.sh specs/red-baseline-sdd-compaction/t3/C1.txt specs/red-baseline-sdd-compaction/t3/C1 1 5
bash specs/red-baseline-sdd-compaction/kit/run_reps.sh specs/red-baseline-sdd-compaction/t3/C2a.txt specs/red-baseline-sdd-compaction/t3/C2a 1 5
bash specs/red-baseline-sdd-compaction/kit/run_reps.sh specs/red-baseline-sdd-compaction/t3/C2b.txt specs/red-baseline-sdd-compaction/t3/C2b 1 5
bash specs/red-baseline-sdd-compaction/kit/run_reps.sh specs/red-baseline-sdd-compaction/t3/C3.txt specs/red-baseline-sdd-compaction/t3/C3 1 5
```

Leave out C3 from both commands if its stop rule fired.

- [x] **Step 6: Read, record, and tighten if needed**

  > Deviation: Ruling (2) was tightened once (99b0b34) after C2b scored 0/5 at 4a1192b; C2b, C2a, C1 and C17 all scored 5/5 at fc6cc10. Final-SHA C17 rep 1 passes only on a generous reading; the owner ruled it a pass on 2026-10-29 (disclosed in the results file).

Read every rep with `show_reps.py` and record verdicts under `## Results` as in Task 2. For a treatment below its bar: tighten that ruling's wording only, keep the two ruling (2) copies the same, run Step 4's size check (and its fallback move if needed), commit, rebuild that case for the new SHA, and rerun 5 reps. At most two rounds per case; then stop and ask the owner with the reps' quoted phrases. C2b below 5/5 is never resolved by loosening its bar.

Re-run C17 once on the final SHA (5 reps) to confirm the ruling text did not break the fix-loop pointer; its bar is unchanged.

- [x] **Step 7: Commit**

```bash
git add specs/red-baseline-sdd-compaction.md specs/red-baseline-sdd-compaction skills/subagent-driven-development
git commit -m "test(sdd): plan 71 treatment reps for the three rulings"
```

---

### Task 4: Move bayesian-workflow's situational sections into references

**Files:**
- Create: `skills/bayesian-workflow/references/{stack-compatibility,model-template,samplers,model-families,utility-scripts,troubleshooting}.md`
- Modify: `skills/bayesian-workflow/SKILL.md`, `skills/bayesian-workflow/README.md:66,83`, `build/check_snippets.py:83`, `build/snippet_preamble.py:3`

**Interfaces:**
- Consumes: `check_moved_lines.py` from Task 1.
- Produces: the bayesian-workflow body within the size gate; Task 5 relies on it.

- [x] **Step 1: Confirm the survival check passes on the unchanged file**

Run: `python3 specs/red-baseline-sdd-compaction/kit/check_moved_lines.py c9141e9 skills/bayesian-workflow`
Expected: `0 line(s) missing`.

- [x] **Step 2: Create the six reference files**

Each starts with `# <Title>`, one sentence on when to read it, a blank line, then the section body verbatim (without its `##` heading), fences and their markers included.

| File | Title and first sentence | Moved text (lines at `c9141e9`) |
|---|---|---|
| `references/stack-compatibility.md` | `# Stack compatibility (NumPyro + ArviZ)` / `Read this before you port code to ArviZ 0.23 or when an ArviZ call raises.` | `:127-159` |
| `references/model-template.md` | `# NumPyro model template` / `Start every model from this template; read it before you write model code.` | `:161-227` |
| `references/samplers.md` | `# Samplers` / `Read this before you set up MCMC.` | `:229-313` |
| `references/model-families.md` | `# Common model families` / `Read this to pick the data model and priors for a problem type.` | `:315-338` |
| `references/utility-scripts.md` | `# Utility scripts` / `Read this after sampling, before you write report.md.` | `:340-361` |
| `references/troubleshooting.md` | `# When things go wrong` / `Read this when sampling or a check fails.` | `:363` to the end of the file |

Inside the moved text, links of the form `[references/x.md](references/x.md)` now sit in `references/`. Rewrite each to `[x.md](x.md)` and list it as a pointer fix. `<this-skill-dir>/scripts/…` paths stay as they are.

- [x] **Step 3: Put the pointers in SKILL.md**

Keep each `##` heading; replace its body with:

```markdown
## Stack compatibility (NumPyro + ArviZ)

The inline examples target the ArviZ ≥ 1.0 stack. Before you port code to ArviZ
0.23, or when an ArviZ call raises, read
[references/stack-compatibility.md](references/stack-compatibility.md).

## NumPyro model template

Start every model from the canonical template in
[references/model-template.md](references/model-template.md); read it before you
write model code.

## Samplers

Native NumPyro NUTS is the default and BlackJAX the co-equal alternative. Read
[references/samplers.md](references/samplers.md) before you set up MCMC: both
samplers, chain counts, and run sizes for exploration and the final run.

## Common model families

For each problem type's data model, typical priors and reference file, read
[references/model-families.md](references/model-families.md).

## Utility scripts

Three scripts check a saved run in order (diagnostics, calibration, then ratings
and next steps). Read [references/utility-scripts.md](references/utility-scripts.md)
for the commands before you write `report.md`.

## When things go wrong

Read [references/troubleshooting.md](references/troubleshooting.md) when you see
divergences, low ESS, R-hat above 1.01, a failing predictive check, or a missing
`log_likelihood` or `log_prior` group.
```

The body's other references ("See **Samplers** below", "see **Stack compatibility**", "`np` imported in the model template below") still land on a kept heading; leave them.

- [x] **Step 4: Fix inbound pointers**

- `skills/bayesian-workflow/README.md:66`: `See SKILL.md → "Stack compatibility (NumPyro + ArviZ)"` → `See references/stack-compatibility.md`.
- `skills/bayesian-workflow/README.md:83` (the `references/` tree): add the six new files in the tree's existing order and style.
- `build/check_snippets.py:83`: `SKILL.md Stack compatibility table` → `references/stack-compatibility.md`.
- `build/snippet_preamble.py:3`: `(SKILL.md, NumPyro model template)` → `(references/model-template.md)`.
- Check the two line citations into Installation, `build/check_snippets.py:72` (`SKILL.md:50-53`) and the fence marker `blackjax is optional (SKILL.md:52)` now in `references/samplers.md`: Installation did not move, so confirm with `sed -n 50,56p skills/bayesian-workflow/SKILL.md` that the cited lines still hold the optional-package text, and correct the numbers if they do not.
- Re-run the sweep: `grep -rn -E 'Stack compatibility|NumPyro model template|Common model families|Utility scripts|When things go wrong' skills agents commands build NOTICE CLAUDE.md --include='*.md' --include='*.py' --include='*.toml' | grep -v '^skills/bayesian-workflow/'` and fix any other hit.

- [x] **Step 5: Run the checks**

```bash
python3 specs/red-baseline-sdd-compaction/kit/check_moved_lines.py c9141e9 skills/bayesian-workflow
python3 -c "import re,sys;t=open(sys.argv[1]).read();m=re.match(r'---\n.*?\n---\n',t,re.S);print('body chars',len(t)-m.end(),'file bytes',len(t.encode()))" skills/bayesian-workflow/SKILL.md
uv run python build/check_snippets.py skills/
uv run python build/versions.py run snippets -- python build/check_snippets.py --api skills/bayesian-workflow/
uv run python build/versions.py run snippets -- python build/check_snippets.py --run skills/bayesian-workflow/
uv run --with pyyaml python build/check_conformance.py
cd build && uv run --with pytest --with numpy --with polars python -m pytest -q test_check_snippets.py; cd ..
```

Expected: the survival check prints only listed pointer fixes; body chars ≤ 19,500 and file bytes < 20,000; all three snippet tiers pass with the same block counts as on `c9141e9` (run the same Tier 3 command in a temporary `git worktree add /tmp/plan71-base c9141e9`, report both counts, then `git worktree remove /tmp/plan71-base`); the conformance check and `test_check_snippets.py` pass. Tier 3 takes minutes; run it with `timeout: 600000` or in the background.

If the size gate fails, move `## Installation` (`:54-69`) to `references/installation.md` the same way, fix the two `SKILL.md:50-53` and `SKILL.md:52` citations to point at it, and report the move.

- [x] **Step 6: Commit**

  > Deviation: The commit (9a62f64) also deleted the whole exception `skill-body-past-compaction` and set `CRITICAL_SPANS = {}`, because the hook's stale-waiver check fails once bayesian-workflow fits too. The brief's `SKILL.md:50-53` and `:52` citations were already stale (the pip lines are 61-64, blackjax 63); `references/svi.md:47` also got a pointer fix. Four relative links broke by the move and were fixed in the final review (49c8a9f).

```bash
git add skills/bayesian-workflow build/check_snippets.py build/snippet_preamble.py
git commit -m "refactor(bayesian-workflow): move situational sections into references/"
```

---

### Task 5: Remove exception `skill-body-past-compaction`

**Files:**
- Modify: `build/cc_guide/conformance.toml:682-694`, `build/test_check_conformance.py:1140-1143`, `build/test_commit_lints.py:163-182`, `CLAUDE.md:107-110`, `build/CLAUDE.md`, `specs/superpowers-drift-spec.md`

**Interfaces:**
- Consumes: both bodies within the size gate (Tasks 3 and 4).
- Produces: no compaction-window waiver for either file; `critical_placement` and the eight-lint count stay, because writing-skills' `ACKNOWLEDGED_LATE` remains.

- [x] **Step 1: Write the failing test**

  > Deviation: Steps 1 to 4 were done in Tasks 1 and 4 (see their notes). Only Steps 5 to 8 ran here (29b0cfa). `build/CLAUDE.md` named none of the removed items and was left unchanged.

Replace `test_late_critical_section_is_refused` in `build/test_commit_lints.py` with:

```python
def test_late_critical_section_is_refused(clone):
    '''With no compaction-window waiver for subagent-driven-development, the conformance
    check itself refuses a Red Flags section moved past the compaction window.'''
    skill = clone / 'skills' / 'subagent-driven-development' / 'SKILL.md'
    text = skill.read_text()
    start = text.index('\n## Red Flags\n') + 1
    end = text.index('\n## ', start) + 1
    filler = '\n'.join(['Filler paragraph that pushes the moved section past the window.'] * 400)
    skill.write_text(text[:start] + text[end:] + '\n' + filler + '\n\n' + text[start:end])
    before = head(clone)
    result = commit(clone, '-am', 'late red flags')
    assert result.returncode != 0, result.stderr
    assert head(clone) == before
    assert failed_names(result) == {'check_conformance'}, result.stderr
    assert "heading '## Red Flags' starts past the" in result.stdout + result.stderr, result.stderr
```

- [x] **Step 2: Run it to see it fail**

Run: `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_commit_lints.py -k test_late_critical_section_is_refused; cd ..`
Expected: FAIL, because the exception still waives the file: the failed set is `{'critical_placement'}`, not `{'check_conformance'}`.

- [x] **Step 3: Remove the exception and the spans**

- In `build/cc_guide/conformance.toml`, delete the whole `[[exception]]` block whose `id = 'skill-body-past-compaction'` (`:682-694`, through its `tracked_in` line, and the blank line after it).
- In `build/test_check_conformance.py`, replace the two rows of `CRITICAL_SPANS` so it reads `CRITICAL_SPANS = {}`, and replace the comment line above it that names "its files' rows" only if it no longer reads true.

- [x] **Step 4: Run the tests to see them pass**

```bash
cd build && uv run --with pytest --with pyyaml python -m pytest -q test_commit_lints.py -k test_late_critical_section_is_refused; cd ..
cd build && uv run --with pytest --with pyyaml python -m pytest -q -rs test_check_conformance.py -k test_real_skill; cd ..
uv run --with pyyaml python build/check_conformance.py
```

Expected: the first passes. The second passes `test_real_skill_spans_match_the_compaction_waiver` and the `ACKNOWLEDGED_LATE` tests, and reports the two tests parametrized over `CRITICAL_SPANS` as skipped for an empty parameter set: that is expected, because the unwaived conformance check now guards both files, headings included, which Step 1's test proves. The conformance check passes with no finding for either skill.

- [x] **Step 5: Update the placement text**

In `CLAUDE.md`, replace

```text
# Critical-section placement: compaction-window exceptions waive per file, heading findings included, so these tests
# pin the critical sections of two skills (CRITICAL_SPANS) and the late headings the owner accepted in writing-skills
# (ACKNOWLEDGED_LATE), both in test_check_conformance.py. Removing an exception removes its files' rows; when the last
# compaction-window exception goes, retire this lint and these tests with it
```

with

```text
# Critical-section placement: compaction-window exceptions waive per file, heading findings included, so these tests
# pin the late headings the owner accepted in writing-skills (ACKNOWLEDGED_LATE, in test_check_conformance.py;
# CRITICAL_SPANS is empty since plan 71 removed skill-body-past-compaction). Removing an exception removes its files'
# rows; when the last compaction-window exception goes, retire this lint and these tests with it
```

In `build/CLAUDE.md`, find each sentence that names `skill-body-past-compaction`, `CRITICAL_SPANS` or "two skills" for the placement lint (`grep -n -E 'skill-body-past-compaction|CRITICAL_SPANS|critical_placement' build/CLAUDE.md`) and make it say the same as the new `CLAUDE.md` text. Do not change the lint count.

- [x] **Step 6: Update drift finding 17's disposition**

In `specs/superpowers-drift-spec.md`, under `## Suggested disposition`, replace the bullet that starts `- **Fix directly, no spec, through an open deferred item:** finding 17's SDD` (through `…prior art for it.`) with:

```markdown
- **Done, SDD half of finding 17:** through plan 71 (2026-10-29). Our own text
  moved verbatim into upstream's seven references plus `file-handoffs.md` and
  the Context Checkpoints section, with the fix-loop re-read pointer. Plan 71
  also applied the owner's three rulings on "Three subagent-driven-development
  decisions": the Fable round-5 rung, the trivial-fix exception and the
  post-compaction recovery line. Results:
  `specs/red-baseline-sdd-compaction.md`. Exception
  `skill-body-past-compaction` is gone.
```

If Task 2's C3 stop rule fired, change "the trivial-fix exception and the post-compaction recovery line" to "and the trivial-fix exception; the recovery line was dropped because the control already recovered (D3)".

In the same file's Scope table, the "Adoption baselines" row ends with `` `2ce8aa1` (v7.0.1) for finding 4, which plan 70 adopted``. Append to it: ``. `2ce8aa1` also for finding 17's SDD file map, which plan 71 adopted``.

- [x] **Step 7: Run every commit lint and the touched suites**

```bash
bash build/run_commit_lints.sh
cd build && uv run --with pytest --with pyyaml python -m pytest -q test_commit_lints.py test_check_conformance.py test_runtime_support.py; cd ..
uv run python build/cc_guide/cli.py lint
```

Expected: every lint passes; the three suites pass (skips only for the empty-`CRITICAL_SPANS` parameter sets); `cc_guide/cli.py lint` passes (STALE lines do not fail it; list any it prints in the report).

- [x] **Step 8: Commit**

```bash
git add build/cc_guide/conformance.toml build/test_check_conformance.py build/test_commit_lints.py CLAUDE.md build/CLAUDE.md specs/superpowers-drift-spec.md
git commit -m "chore(conformance): remove skill-body-past-compaction now both bodies fit the window"
```

---

## Done when

- Both `SKILL.md` bodies are at most 19,500 characters and both files are under 20,000 bytes.
- Exception `skill-body-past-compaction` is gone and `build/check_conformance.py` passes.
- Every micro-test bar in `specs/red-baseline-sdd-compaction.md` is met, or the owner has ruled on the one that is not.
- The plan-completion protocol ticks both deferred items: "Fit the subagent-driven-development and bayesian-workflow bodies inside the compaction window" and "Three subagent-driven-development decisions, outside the register".
