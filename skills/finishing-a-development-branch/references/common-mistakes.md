# Common Mistakes

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
- **Fix:** Require typed "discard" confirmation before anything is deleted
