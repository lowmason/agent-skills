---
name: finishing-a-development-branch
description: >
  Use when implementation on a development branch is complete and tests pass, and the work needs
  wrapping up — merge vs. PR vs. keep vs. discard is being decided, or a feature branch's
  worktree needs cleanup. Trigger on: "the feature is done", "ready to merge", "should I open a
  PR", "clean up this branch/worktree", deciding how to integrate a completed feature branch, or
  finishing work started with the using-git-worktrees skill.
---

# Finishing a Development Branch

## Overview

Guide completion of development work by presenting clear options and handling chosen workflow.

**Core principle:** Verify tests → Check deferred backlog → Detect environment → Present options → Execute choice → Clean up.

**Announce at start:** "I'm using the finishing-a-development-branch skill to complete this work."

## The Process

### Step 1: Verify Tests

**Before presenting options, verify tests pass:**

```bash
# Run project's test suite
npm test / cargo test / pytest / go test ./...
```

**If tests fail:**
```
Tests failing (<N> failures). Must fix before completing:

[Show failures]

Cannot proceed with merge/PR until tests pass.
```

Stop. Don't proceed to Step 2.

**If tests pass:** Continue to Step 1b.

### Step 1b: Check Deferred Backlog

This is the last moment before the work leaves the building. Volume is
reported; only the **aged tail** gates.

```bash
uv run --python 3.13 python ~/.claude/skills/writing-plans/scripts/deferred_stats.py
```

Run it without `--json`: this step needs the human-readable summary, and reading
`aged >45d:` off that line is all the gate requires. If the script prints
`no specs/deferred_items.md in this repo`, or reports `0 open`, say nothing and
continue to Step 2.

**If `aged >45d:` is 0:** report the summary line as printed and continue to Step 2.

```
Deferred backlog: 12 open, 40 ever closed (closure rate 77%), aged >45d: 0.
```

**If `aged >45d:` is greater than 0:** report it and stop before the menu.

```
Deferred backlog: 44 open, 61 ever closed (closure rate 58%), aged >45d: 29.
Oldest open: 71d (12-audit_7_20_26).

29 items have been open past the 45-day review horizon. Before finishing:

1. Run `/deferred` to triage them
2. Acknowledge and carry them — tell me why, and I'll log it

Which?
```

Do not present the merge/PR menu until one of the two lands.

- **`/deferred`** is your human partner's to run. When they have, re-run the
  stats and continue from the new numbers.
- **Acknowledge** requires a reason. Append one plain bullet — never a
  checkbox, so it stays out of the backlog counts — under a
  `## Aged-backlog acknowledgements` section pinned directly beneath the
  file's `# Deferred items` title, creating that section if absent:

```markdown
## Aged-backlog acknowledgements
- 2026-09-08 — finished `feat/rate-limiter` with 29 items aged >45d, carried
  deliberately: the Redis decision is still with the platform team.
```

Commit that edit with the branch's other completion commits, then continue to
Step 2. The full contract is the **Aged-tail gate** section of the
writing-plans skill's `references/deferred-backlog.md`.

"Carried deliberately" with no reason is the silent default this gate exists to
convert into a conscious one. Never write the acknowledgement without asking —
taking the override on your partner's behalf defeats the whole mechanism.

### Step 2: Detect Environment

**Determine workspace state before presenting options:**

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
WORKTREE_PATH=$(git rev-parse --show-toplevel)
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
```
**Record all four values in the conversation now.** Shell state does not
persist across tool calls, and Step 6 consumes the values recorded here —
re-detecting after Options 1/4 have cd-ed to MAIN_ROOT always reports
"normal repo" and orphans the worktree.

This determines which menu to show and how cleanup works:

| State | Menu | Cleanup |
|-------|------|---------|
| `GIT_DIR == GIT_COMMON` (normal repo) | Standard 4 options | No worktree to clean up |
| `GIT_DIR != GIT_COMMON`, named branch | Standard 4 options | Provenance-based (see Step 6) |
| `GIT_DIR != GIT_COMMON`, detached HEAD | Reduced 3 options (no merge) | No cleanup (externally managed) |

### Step 3: Determine Base Branch

```bash
BASE_BRANCH=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')
# Fallback when origin/HEAD is unset (fresh clone or no remote):
[ -n "$BASE_BRANCH" ] || BASE_BRANCH=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null)
```

Or ask: "This branch split from main - is that correct?"

### Step 4: Present Options

**Normal repo and named-branch worktree — present exactly these 4 options:**

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work

Which option?
```

**Detached HEAD — present exactly these 3 options:**

```
Implementation complete. You're on a detached HEAD (externally managed workspace).

1. Push as new branch and create a Pull Request
2. Keep as-is (I'll handle it later)
3. Discard this work

Which option?
```

**Don't add explanation** - keep options concise.

### Step 5: Execute Choice

#### Option 1: Merge Locally

```bash
# Get main repo root for CWD safety
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"

# Merge first — verify success before removing anything
git checkout <base-branch>
git pull
git merge <feature-branch>

# Verify tests on merged result
<test command>

# Only after merge succeeds: cleanup worktree (Step 6), then delete branch
```

Then: Cleanup worktree (Step 6), then delete branch:

```bash
git branch -d <feature-branch>
```

#### Option 2: Push and Create PR

```bash
# Push branch, then create the PR with the gh CLI
git push -u origin <feature-branch>
gh pr create --base <base-branch>
```

Consider a pre-PR review via the requesting-code-review skill first.

**Do NOT clean up worktree** — user needs it alive to iterate on PR feedback.

**Detached HEAD ("push as new branch") recipe:**

```bash
git push origin HEAD:refs/heads/<new-branch>
gh pr create --base <base-branch> --head <new-branch>
```

#### Option 3: Keep As-Is

Report: "Keeping branch <name>. Worktree preserved at <path>."

**Don't cleanup worktree.**

#### Option 4: Discard

**Confirm first:**
```
This will permanently delete:
- Branch <name>
- All commits: <commit-list>
- Worktree at <path>

Type 'discard' to confirm.
```

Wait for exact confirmation.

If confirmed:
```bash
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"
```

Then: Cleanup worktree (Step 6), then force-delete branch:
```bash
git branch -D <feature-branch>
```

### Step 6: Cleanup Workspace

**Only runs for Options 1 and 4.** Options 2 and 3 always preserve the worktree.

**Use the values recorded in Step 2** (GIT_DIR, GIT_COMMON, WORKTREE_PATH,
MAIN_ROOT). Do NOT re-run detection here — after Options 1/4 cd to
MAIN_ROOT, re-detection reports a normal repo and skips cleanup, orphaning
the worktree and making the branch deletion below fail.

**If Step 2 recorded `GIT_DIR == GIT_COMMON`:** Normal repo, no worktree to clean up. Done.

**If the recorded WORKTREE_PATH is under `.worktrees/` or `worktrees/`:** the
using-git-worktrees skill (or you) created this worktree — we own cleanup.

```bash
cd "$MAIN_ROOT"
git worktree remove "$WORKTREE_PATH"
git worktree prune  # Self-healing: clean up any stale registrations
```

**Otherwise:** The host environment (harness) owns this workspace. Do NOT
remove it. If your platform provides a workspace-exit tool (e.g.
ExitWorktree), use it. Otherwise, leave the workspace in place.

## Quick Reference

| Option | Merge | Push | Keep Worktree | Cleanup Branch |
|--------|-------|------|---------------|----------------|
| 1. Merge locally | yes | - | - | yes |
| 2. Create PR | - | yes | yes | - |
| 3. Keep as-is | - | - | yes | - |
| 4. Discard | - | - | - | yes (force) |

## Common Mistakes

**Skipping test verification**
- **Problem:** Merge broken code, create failing PR
- **Fix:** Always verify tests before offering options

**Taking the aged-tail override unasked**
- **Problem:** Writing the acknowledgement yourself turns a gate meant to force a conscious decision back into a silent default
- **Fix:** Present both options and wait; log only the reason your partner gives

**Open-ended questions**
- **Problem:** "What should I do next?" is ambiguous
- **Fix:** Present exactly 4 structured options (or 3 for detached HEAD)

**Cleaning up worktree for Option 2**
- **Problem:** Remove worktree user needs for PR iteration
- **Fix:** Only cleanup for Options 1 and 4

**Deleting branch before removing worktree**
- **Problem:** `git branch -d` fails because worktree still references the branch
- **Fix:** Merge first, remove worktree, then delete branch

**Running git worktree remove from inside the worktree**
- **Problem:** Command fails silently when CWD is inside the worktree being removed
- **Fix:** Always `cd` to main repo root before `git worktree remove`

**Cleaning up harness-owned worktrees**
- **Problem:** Removing a worktree the harness created causes phantom state
- **Fix:** Only clean up worktrees under `.worktrees/` or `worktrees/`

**No confirmation for discard**
- **Problem:** Accidentally delete work
- **Fix:** Require typed "discard" confirmation

## Red Flags

**Never:**
- Proceed with failing tests
- Present the merge/PR menu with an unaddressed aged tail
- Write an aged-backlog acknowledgement your partner did not ask for
- Merge without verifying tests on result
- Delete work without confirmation
- Force-push without explicit request
- Remove a worktree before confirming merge success
- Clean up worktrees you didn't create (provenance check)
- Run `git worktree remove` from inside the worktree

**Always:**
- Verify tests before offering options
- Check the deferred backlog before offering options
- Detect environment before presenting menu
- Present exactly 4 options (or 3 for detached HEAD)
- Get typed confirmation for Option 4
- Clean up worktree for Options 1 & 4 only
- `cd` to main repo root before worktree removal
- Run `git worktree prune` after removal
