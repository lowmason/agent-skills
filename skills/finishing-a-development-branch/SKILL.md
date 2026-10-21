---
name: finishing-a-development-branch
description: >
  Use when implementation on a development branch is complete and tests pass, and the work needs
  wrapping up — merge vs. PR vs. keep vs. discard is being decided, or a feature branch's
  worktree needs cleanup. Trigger on: "the feature is done", "ready to merge", "should I open a
  PR", "clean up this branch/worktree", deciding how to integrate a completed feature branch, or
  finishing work started with the using-git-worktrees skill.
license: MIT
compatibility: Requires uv to run bundled scripts (dependencies are declared inline); Python 3.11+.
metadata:
  author: 'Jesse Vincent'
  adapted_by: 'Lowell Mason'
  source: 'https://github.com/obra/superpowers'
---

# Finishing a Development Branch

## Overview

Guide completion of development work by presenting clear options and handling chosen workflow.

**Core principle:** Verify tests → Check deferred backlog → Detect environment → Present options → Codex review (merge/PR) → Execute choice → Clean up.

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
uv run <this-skill-dir>/../writing-plans/scripts/deferred_stats.py
```

Without uv, run the same path with `python3` in an environment that has the
dependencies listed in the script's header.

Run it without `--json`: this step needs the human-readable summary, and reading
`aged >45d:` off that line is all the gate requires. If the script prints
`no specs/deferred_items.md in this repo`, or reports `0 open`, say nothing and
continue to Step 2.

**If `aged >45d:` is 0:** report the summary line as printed and continue to Step 2.

```
Deferred backlog: 12 open, 40 ever closed (closure rate 77%), aged >45d: 0.
```

**If `aged >45d:` is greater than 0:** report it, then continue to Step 2 and
present the menu normally.

```
Deferred backlog: 44 open, 61 ever closed (closure rate 58%), aged >45d: 29.
Oldest open: 71d (12-audit_7_20_26).

29 items are aged past the 45-day review horizon — I'll ask about those before
merging or opening a PR.
```

**The gate binds Options 1 and 2 only.** Merge and PR are the paths where the
work leaves the building. Options 3 (Keep) and 4 (Discard) are never gated:
nothing ships on either, and gating Discard would force a triage pass onto a
branch that is about to be deleted — then delete the acknowledgement along with
it, destroying the very record the gate exists to create.

Before executing Option 1 or Option 2, ask, and wait for an answer:

```
29 items are aged past the 45-day review horizon. Before I <merge / open the PR>:

1. Run `/deferred` to triage them
2. Acknowledge and carry them — tell me why, and I'll log it

Which?
```

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

Commit that edit with the branch's other completion commits, then proceed with
the chosen option — on Options 1 and 2 the branch survives, so the record
survives with it. The full contract is the **Aged-tail gate** section of
`../writing-plans/references/deferred-backlog.md`.

"Carried deliberately" with no reason is the silent default this gate exists to
convert into a conscious one. Never write the acknowledgement without asking —
taking the override on your partner's behalf defeats the whole mechanism.

### Step 2: Detect Environment

**Determine workspace state before presenting options.** Run each command as its own Bash call, exactly as written. A session that Claude Code isolates in a worktree refuses `git -C`, `$(…)` and `cd … &&` forms, so the commands this skill runs inside the worktree avoid them:

```bash
git rev-parse --path-format=absolute --git-dir
git rev-parse --path-format=absolute --git-common-dir
git rev-parse --show-toplevel
git worktree list --porcelain
```

From the output, record GIT_DIR (the first command), GIT_COMMON (the second), WORKTREE_PATH (the third) and MAIN_ROOT, the path on the first `worktree` line of the list.

**If GIT_DIR != GIT_COMMON, record two more values.** Detect both. Never infer either from the worktree's path.

**MAIN_GIT** — whether this session may run git in the main checkout. Run this probe as its own call, with the recorded MAIN_ROOT written out in place of `<MAIN_ROOT>`:

```bash
git -C <MAIN_ROOT> rev-parse --show-toplevel
```

- Refused, with a message that says the session is isolated in this worktree: MAIN_GIT is `blocked`.
- It prints MAIN_ROOT, and your instructions do not tell you to stay in the worktree: MAIN_GIT is `allowed`.
- It prints MAIN_ROOT, but your instructions tell you to stay in the worktree or not to `cd` to the main checkout: MAIN_GIT is `ask`.
- It fails any other way, a permission denial included: MAIN_GIT is `ask`.

**MADE_BY** — who created this worktree, from this conversation's record:

- `this session`: the conversation shows the call that created it, a `git worktree add` or EnterWorktree with `name`.
- `launcher`: anything else. The session started inside the worktree (the desktop app, `claude --worktree`, another harness), or the conversation no longer shows how the worktree was made, after a `/clear` or a compaction for example.

**Record every value in the conversation now.** Shell state does not
persist across tool calls, and Steps 5 and 6 consume the values recorded here —
re-detecting after Options 1/4 have moved to MAIN_ROOT always reports
"normal repo" and orphans the worktree.

This determines which menu to show and how cleanup works:

| State | Menu | Cleanup |
|-------|------|---------|
| `GIT_DIR == GIT_COMMON` (normal repo) | Standard 4 options | No worktree to clean up |
| `GIT_DIR != GIT_COMMON`, named branch | Standard 4 options | By MADE_BY (see Step 6) |
| `GIT_DIR != GIT_COMMON`, detached HEAD | Reduced 3 options (no merge) | No cleanup (externally managed) |

### Step 3: Determine Base Branch

```bash
git symbolic-ref --short refs/remotes/origin/HEAD
```

BASE_BRANCH is its output without the `origin/` prefix. If it fails (no `origin/HEAD`: a fresh clone or no remote), ask `gh`, which also fails when `gh` is not installed:

```bash
gh repo view --json defaultBranchRef -q .defaultBranchRef.name
```

**If both fail** — no `origin/HEAD`, and no `gh` to ask —
ask instead: "This branch split from main - is that correct?"

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

### Step 4b: Codex Second Review (Merge and PR Only)

When your partner picks merge or PR — on a detached HEAD, push-as-new-branch —
get a second model's review before the work leaves the building. Keep and
Discard ship nothing and skip this step, the same binding as the aged-tail
gate. Resolve that gate first: both of its outcomes commit to the branch — an
acknowledgement, or `/deferred` quick fixes — and the review must see the
branch as it will ship. For the same reason
`git status --porcelain --untracked-files=normal` must print nothing before
you go on: commit what is part of the work, and ask your
partner about anything else.

Run it from the feature worktree, before Option 1 leaves it — from
the base branch there is nothing left to review. If nothing reviewed this
branch before finishing — it did not come through executing-plans or
subagent-driven-development — first offer your partner a code-reviewer pass
via the requesting-code-review skill; if they take it, launch it in the same
message as Codex. Follow
[codex-review.md](../requesting-code-review/codex-review.md), choosing the base
this way:

- **The conversation holds a `Codex reviewed <sha>` line** — executing-plans
  and subagent-driven-development write one when their final review's Codex
  run completes. If `git merge-base --is-ancestor <sha> HEAD` fails, the
  branch was rebased since: treat the line as lost. Otherwise see what has
  changed since, outside the plan-completion bookkeeping in `specs/` — the
  pathspecs are anchored at the repo root, so this holds from any directory:

  ```bash
  git diff --stat <sha>..HEAD -- ':/' ':(top,exclude)specs/'
  ```

  Empty: say "Codex reviewed this code at <sha>; only specs/ bookkeeping
  since" and skip the review. Otherwise `--base <sha>`, which reviews just the
  new commits.
- **Otherwise** — no such line, or it was lost to a `/clear` or a rebase —
  `--base <base-branch>`, the whole branch. On the base branch itself (a plan
  executed there) that is an empty range, a review of nothing: ask your
  partner which commit the work starts after, and use that.

Work its findings — merged with code-reviewer's, if that ran — with the
receiving-code-review skill: fix what holds up, re-run the tests, commit. Show
your partner anything you left unfixed, and execute the chosen option only
after they have seen it.

### Step 5: Execute Choice

#### Option 1: Merge Locally

**Aged-tail gate (Step 1b):** if aged items were reported, resolve them before
merging — a `/deferred` pass or a logged acknowledgement.

**Codex review (Step 4b):** done from the feature worktree, before you leave it.

**Get to the main checkout.** The merge runs in MAIN_ROOT. Your partner's choice of this option is their request to leave the worktree. Go by the MAIN_GIT that Step 2 recorded:

- **Normal repo, or `allowed`:** run each command below from MAIN_ROOT. A Bash call can start back in the worktree, so begin each call with `cd <MAIN_ROOT> &&`.
- **`ask`:** ask your partner, "Finishing runs git in the main checkout at <MAIN_ROOT>. May I?" A yes is `allowed`. On a no, give your partner the commands, as the no-op case under `blocked` does.
- **`blocked`:** call ExitWorktree with `action: "keep"`. Never use `"remove"`: it deletes the branch before the merge. If ExitWorktree returns the session to MAIN_ROOT, run the commands below there. If it reports a no-op, this session cannot run git in the main checkout. Do not rewrite a refused command to get round the check. Give your partner the commands below with every value written out, ask them to run the commands in a terminal and tell you the test result, and wait.

```bash
# Merge first — verify success before removing anything
git checkout <base-branch>
git pull
git merge <feature-branch>

# Verify tests on merged result
<test command>
```

Then: Cleanup worktree (Step 6). If Step 6 removed the worktree, delete the branch. git refuses while a worktree still has it checked out:

```bash
git branch -d <feature-branch>
```

#### Option 2: Push and Create PR

**Aged-tail gate (Step 1b):** if aged items were reported, resolve them before
pushing — a `/deferred` pass or a logged acknowledgement.

**Codex review (Step 4b):** done before the push.

Push first — this half never needs `gh`, and it makes the branch a real ref the
fallback URL below can point at:

```bash
git push -u origin <feature-branch>
```

**If `gh` is installed** (`command -v gh`), create the PR with it:

```bash
gh pr create --base <base-branch>
```

**If it is not** — GitHub Enterprise hosts (BBGitHub among them) commonly ship
without it — derive the PR URL from the remote and hand it to your partner. On
GitHub-family hosts the PR form lives at
`<web-root>/compare/<base>...<branch>?expand=1`:

```bash
git remote get-url origin \
  | sed -e 's|^git@\([^:]*\):|https://\1/|' -e 's|^ssh://git@|https://|' -e 's|\.git$||'
```

Report the push, and never a PR you did not open:

```
Pushed <feature-branch> to origin. `gh` isn't installed here, so I can't open
the PR from the command line — open it in the browser:

<web-root>/compare/<base-branch>...<feature-branch>?expand=1
```

**Do NOT clean up worktree** — user needs it alive to iterate on PR feedback.

**Detached HEAD ("push as new branch") recipe** — same `gh` branch as above:

```bash
git push origin HEAD:refs/heads/<new-branch>
gh pr create --base <base-branch> --head <new-branch>  # no gh: compare URL above, head <new-branch>
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

If Step 2 recorded MADE_BY `launcher`, Step 6 cannot remove the worktree, and git cannot delete a branch that a worktree has checked out. Do not show the list above and do not ask for confirmation. Tell your partner this, then stop: "<path> and its branch <name> belong to the tool that started this session, so I can't delete them. They stay until it removes the worktree, or you run `git worktree remove <path>` and then `git branch -D <name>` from <MAIN_ROOT>."

Otherwise, wait for exact confirmation.

If confirmed, get to the main checkout as Option 1 does, by the MAIN_GIT that Step 2 recorded. Then: Cleanup worktree (Step 6). If Step 6 removed the worktree, force-delete the branch:
```bash
git branch -D <feature-branch>
```

### Step 6: Cleanup Workspace

**Only runs for Options 1 and 4.** Options 2 and 3 always preserve the worktree.

**Use the values recorded in Step 2** (GIT_DIR, GIT_COMMON, WORKTREE_PATH,
MAIN_ROOT, MAIN_GIT, MADE_BY). Do NOT re-run detection here — after Options 1/4 move to
MAIN_ROOT, re-detection reports a normal repo and skips cleanup, orphaning
the worktree and making the branch deletion below fail.

**If Step 2 recorded `GIT_DIR == GIT_COMMON`:** Normal repo, no worktree to clean up. Done.

**If Step 2 recorded MADE_BY `this session`:** you own cleanup. Run these from MAIN_ROOT, where Option 1 or 4 took you. On `allowed`, begin each call with `cd <MAIN_ROOT> &&`. If Option 1 or 4 handed the commands to your partner, give them these commands too, with every value written out, and wait for their result:

```bash
git worktree remove <WORKTREE_PATH>
git worktree prune  # Self-healing: clean up any stale registrations
```

**If `git worktree remove` refuses, stop.** Do not add `--force` or `-f -f`, and do not run `git worktree unlock`, whatever git's message suggests. A lock can belong to a session that is still running, and modified or untracked files can be work that exists nowhere else. Tell your partner the cause:

- **Locked:** quote the lock reason from git's message.
- **Modified or untracked files:** list them, from `git -C <WORKTREE_PATH> status --porcelain --untracked-files=all`.

Then ask what to do, and wait. Delete the branch only once the worktree is gone.

**If Step 2 recorded MADE_BY `launcher`:** the tool that started this session owns the worktree. Do NOT remove it, and leave its branch: git refuses to delete a branch that a worktree has checked out. Tell your partner where the worktree is and what removes it. The desktop app cleans up or reuses a session's worktree when the session is archived. Anywhere else, your partner can run `git worktree remove <WORKTREE_PATH>` from MAIN_ROOT and then delete the branch.

## Quick Reference

| Option | Codex Review | Merge | Push | Keep Worktree | Cleanup Branch |
|--------|--------------|-------|------|---------------|----------------|
| 1. Merge locally | yes | yes | - | - | yes |
| 2. Create PR | yes | - | yes | yes | - |
| 3. Keep as-is | - | - | - | yes | - |
| 4. Discard | - | - | - | - | yes (force) |

Options 1 and 4 delete the branch only when Step 6 removed the worktree. They do not when Step 2 recorded MADE_BY `launcher`.

## Common Mistakes

**Skipping test verification**
- **Problem:** Merge broken code, create failing PR
- **Fix:** Always verify tests before offering options

**Taking the aged-tail override unasked**
- **Problem:** Writing the acknowledgement yourself turns a gate meant to force a conscious decision back into a silent default
- **Fix:** Present both options and wait; log only the reason your partner gives

**Running the Codex review after Option 1's checkout**
- **Problem:** On the base branch the merge base is HEAD itself — Codex reviews an empty diff
- **Fix:** Run Step 4b from the feature worktree, before Option 1 leaves it

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
- **Fix:** Run it from MAIN_ROOT, where Option 1 or 4 takes you

**Cleaning up a worktree you did not make**
- **Problem:** Removing a worktree the harness or the desktop app created causes phantom state, and a path proves nothing: Claude Code and the app put their worktrees under `.claude/worktrees/`
- **Fix:** Remove only a worktree Step 2 recorded as MADE_BY `this session`

**Running git in the main checkout from an isolated session**
- **Problem:** Claude Code refuses `cd <MAIN_ROOT> &&`, `git -C <MAIN_ROOT>` and `$(…)` forms there, and a rewritten command is not a safe one
- **Fix:** On MAIN_GIT `blocked`, leave with ExitWorktree `keep`, or give your partner the commands (Option 1)

**Forcing a refused removal**
- **Problem:** git's message suggests `--force`, `-f -f` or unlocking, but a lock can belong to a running session, and untracked files can be the only copy of work
- **Fix:** Name the cause and ask (Step 6)

**No confirmation for discard**
- **Problem:** Accidentally delete work
- **Fix:** Require typed "discard" confirmation

## Red Flags

**Never:**
- Proceed with failing tests
- Merge or open a PR with an unaddressed aged tail
- Merge or open a PR without the Step 4b Codex review, or a stated reason it was skipped
- Report a Codex review that did not complete
- Report a PR as created when only the branch was pushed
- Write an aged-backlog acknowledgement your partner did not ask for
- Merge without verifying tests on result
- Delete work without confirmation
- Force-push without explicit request
- Remove a worktree before confirming merge success
- Remove a worktree that Step 2 did not record as MADE_BY `this session`, or judge who made it from its path
- Run `git worktree remove` from inside the worktree
- Add `--force` or `-f -f` to a refused `git worktree remove`, or unlock the worktree
- Rewrite a command an isolated session refused, to get round the refusal

**Always:**
- Verify tests before offering options
- Check the deferred backlog before offering options
- Detect environment before presenting menu
- Present exactly 4 options (or 3 for detached HEAD)
- Run the Codex review (Step 4b) before merging or pushing
- Get typed confirmation for Option 4
- Clean up worktree for Options 1 & 4 only
- Remove worktrees from MAIN_ROOT
- Run `git worktree prune` after removal
