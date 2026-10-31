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

Run it without `--json`: the gate reads `aged >45d:` off the summary line,
and the `Aged, carry unused:` and `Carry used (only /deferred clears):`
lines when they print. If the script prints
`no specs/deferred_items.md in this repo`, or reports `0 open`, say nothing
and continue to Step 2.

**If `aged >45d:` is 0:** report the summary line as printed and continue to Step 2.

```
Deferred backlog: 12 open, 40 ever closed (closure rate 77%), aged >45d: 0.
```

**If `aged >45d:` is greater than 0:** report it, then continue to Step 2 and
present the menu normally.

```
Deferred backlog: 44 open, 61 ever closed (closure rate 58%), aged >45d: 29.
Aged, carry unused: 12-audit_7_20_26: <first words>…; …
Oldest open: 71d (12-audit_7_20_26).

29 items are aged past the 45-day review horizon — I'll ask about those before
merging or opening a PR.
```

**The gate binds Options 1 and 2 only.** Merge and PR are the paths where the
work leaves the building. Options 3 (Keep) and 4 (Discard) are never gated:
nothing ships on either, and gating Discard would force a triage pass onto a
branch that is about to be deleted — destroying the notes along with it.

Before executing Option 1 or Option 2, ask, and wait for an answer. The
question, with each aged item listed, is in the `## Aged-tail gate` section of
`../writing-plans/references/deferred-backlog.md`. Follow that section. Your
partner answers for each aged item, one of two:

- **A `/deferred` pass**, which your partner runs. Then re-run the stats.
- **One carry**, on your partner's reason. Only an item that has not used its
  carry can take it. Write `→ acknowledged <YYYY-MM-DD> (<branch>): <reason>`
  on the item, not in a separate log, and commit the notes with the branch's
  other completion commits.

An item on the `Aged, carry unused:` line gets both choices. An item on the
`Carry used` line gets only `/deferred`. Your partner may carry some items
and send others to `/deferred`. Proceed with the merge or the PR when no
other aged item is left: each one is carried in this finish, or a
`/deferred` pass changed its state. After the pass, the items you carried show
on `Carry used`. That is expected, and they stay cleared for this finish.

The reason is required. Never write the acknowledgement without asking —
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
| `GIT_DIR != GIT_COMMON`, detached HEAD | Reduced 3 options (no merge) | By MADE_BY (see Step 6) |

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
Implementation complete. You're on a detached HEAD.

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
`→ acknowledged` note on a carried item, or a `/deferred` pass's edits — and
the review must see the branch as it will ship. For the same reason
`git status --porcelain --untracked-files=normal` must print nothing before
you go on: commit what is part of the work, and ask your
partner about anything else.

Run it from the feature worktree, before Option 1 leaves it or your partner
merges — from the base branch there is nothing left to review. If nothing reviewed this
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

If your partner declined the Codex run at its approval gate, skip the Codex run, say the Codex seat was skipped at their word, and continue. The code-reviewer offer above still applies. When no review remains, go on to Step 5.

Work its findings — merged with code-reviewer's, if that ran — with the
receiving-code-review skill: fix what holds up, re-run the tests, commit. Show
your partner anything you left unfixed and each Declined to judge line, and
execute the chosen option only after they have seen it.

**If you left any finding or Declined to judge line unfixed,** ask your partner
which of them to carry, and offer to record each one they carry in
`specs/deferred_items.md`. On their yes:

- Append one item per carried finding, in the **Deferred-item schema** of
  `../writing-plans/references/deferred-backlog.md`: the file paths, the
  finding and why it is carried, what fixing it would take, a `Size:`, and a
  `Done when:` or `Revisit if:`. Write each as an unticked `- [ ]` line at
  column 0, which `deferred_stats.py` counts. A finding with no closure condition is not
  deferrable: tell your partner, and fix or drop it.
- Put the items under a new section at the end of the file,
  `## <name> Step 4b review — <YYYY-MM-DD>`, with an em dash, so the backlog
  stats can date it. `<name>` is the executed plan's file name without `.md`,
  or the branch name when no plan ran. If the file is missing, create it with
  a single `# Deferred items` title line first.
- Commit the edit on the branch before the work leaves it: before Option 1 leaves
  the worktree or your partner merges, and before the push (Option 2; Option 1
  on a detached HEAD), so the record ships with the work. The commit changes only `specs/`,
  so a `Codex reviewed <sha>` line stays current: do not re-run the review for
  it.

Record only the findings your partner carries.

### Step 5: Execute Choice

#### Option 1: Merge Locally

**Aged-tail gate (Step 1b):** if aged items were reported, resolve them before
merging — a `/deferred` pass, or one carry noted on the item.

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

Then: Cleanup worktree (Step 6). Leave the branch while a worktree still has it checked out, since git refuses to delete it. Delete it if Step 2 recorded a normal repo or Step 6 removed the worktree:

```bash
git branch -d <feature-branch>
```

#### Option 2: Push and Create PR

**Aged-tail gate (Step 1b):** if aged items were reported, resolve them before
pushing — a `/deferred` pass, or one carry noted on the item.

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

**If it is not** (GitHub Enterprise hosts, BBGitHub among them, commonly ship
without it), hand your partner the PR URL, as
[references/pr-without-gh.md](references/pr-without-gh.md) shows. Report the
push, and never a PR you did not open.

**Do NOT clean up worktree** — user needs it alive to iterate on PR feedback.

**Detached HEAD ("push as new branch") recipe** — same `gh` branch as above:

```bash
git push origin HEAD:refs/heads/<new-branch>
gh pr create --base <base-branch> --head <new-branch>  # no gh: the compare URL, head <new-branch>
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

In a normal repo, leave out the worktree line: `<path>` is the main checkout.

If Step 2 recorded MADE_BY `launcher`, Step 6 cannot remove the worktree, and git cannot delete a branch that a worktree has checked out. Do not show the list above and do not ask for confirmation. Tell your partner this, then stop: "I did not record that this session made <path>, so I won't delete it or its branch <name>. They stay until you run `git worktree remove <path>` and then `git branch -D <name>` from <MAIN_ROOT>, unless the tool that made the worktree removes it first."

Otherwise, wait for exact confirmation.

If confirmed, get to the main checkout as Option 1 does, by the MAIN_GIT that Step 2 recorded. Where Option 1 would hand the merge commands to your partner, skip the merge and hand over Step 6's commands and the branch command below. Then: Cleanup worktree (Step 6). In a normal repo, first run `git checkout <base-branch>`, since git will not delete the branch you are on. If it refuses, tell your partner why and ask, without forcing it. Force-delete the branch if Step 2 recorded a normal repo or Step 6 removed the worktree:
```bash
git branch -D <feature-branch>
```

### Step 6: Cleanup Workspace

**Only runs for Options 1 and 4** (on the detached-HEAD menu, for Discard, with no branch to delete). A push or a keep always preserves the worktree.

**Use the values recorded in Step 2** (GIT_DIR, GIT_COMMON, WORKTREE_PATH,
MAIN_ROOT, MAIN_GIT, MADE_BY). Do NOT re-run detection here — after Options 1/4 move to
MAIN_ROOT, re-detection reports a normal repo and skips cleanup, orphaning
the worktree and making the branch deletion below fail.

**If Step 2 recorded `GIT_DIR == GIT_COMMON`:** Normal repo, no worktree to clean up. Skip this step; the option's branch deletion still follows.

**If Step 2 recorded MADE_BY `this session`:** you own cleanup. Unless your partner runs them (see below), run these from MAIN_ROOT. On `allowed`, or after a yes to the `ask` question, begin each call with `cd <MAIN_ROOT> &&`:

```bash
git worktree remove <WORKTREE_PATH>
git worktree prune  # Self-healing: clean up any stale registrations
```

**If MADE_BY is `this session` and your partner runs the commands** (Option 1 handed them the merge commands, or Option 4 handed over Step 6): give them these two commands and the branch command that the option gives, with every value written out, and wait for their result. For Option 1, give them only once they report that the merge and tests passed.

**If `git worktree remove` refuses, stop.** Do not add `--force` or `-f -f`, and do not run `git worktree unlock`, whatever git's message suggests. A lock can belong to a session that is still running, and modified or untracked files can be work that exists nowhere else. Tell your partner the cause:

- **Locked:** quote the lock reason from git's message.
- **Modified or untracked files:** list them, from `git -C <WORKTREE_PATH> status --porcelain --untracked-files=all`.

Then ask what to do, and wait. If your partner wants it forced or unlocked, run none of it yourself: give them the unlock or the forced removal, `git worktree prune` and the option's branch deletion, with every value written out, and wait for their result. Delete the branch only once the worktree is gone.

**If Step 2 recorded MADE_BY `launcher`:** you did not record that this session made the worktree. Do NOT remove it, and leave its branch: git refuses to delete a branch that a worktree has checked out. Tell your partner where the worktree is and what removes it. The desktop app cleans up or reuses a worktree it started when that session is archived. Anywhere else, your partner can run `git worktree remove <WORKTREE_PATH>` from MAIN_ROOT and then delete the branch.

## Quick Reference

| Option | Codex Review | Merge | Push | Keep Worktree | Cleanup Branch |
|--------|--------------|-------|------|---------------|----------------|
| 1. Merge locally | yes | yes | - | - | yes |
| 2. Create PR | yes | - | yes | yes | - |
| 3. Keep as-is | - | - | - | yes | - |
| 4. Discard | - | - | - | - | yes (force) |

Options 1 and 4 delete the branch in a normal repo or once Step 6 removed the worktree, and keep both the worktree and the branch under MADE_BY `launcher` or after a refused removal.

## Common Mistakes

When a step above fails, or before you depart from one, read [references/common-mistakes.md](references/common-mistakes.md).

## Red Flags

**Never:**
- Proceed with failing tests
- Merge or open a PR with an unaddressed aged tail
- Merge or open a PR without the Step 4b Codex review, or a stated reason it was skipped
- Report a Codex review that did not complete
- Report a PR as created when only the branch was pushed
- Write an `→ acknowledged` note your partner did not ask for
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
- Get typed confirmation for Option 4 before it deletes anything
- Clean up worktree for Options 1 & 4 only
- Remove worktrees from MAIN_ROOT
- Run `git worktree prune` after removal
