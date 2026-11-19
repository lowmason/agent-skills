---
# cc-guide: rules.rules-files rules.hierarchy subagents.worktrees @2.1.326.1
---

# Pull request lifecycle

Standing authorization from the user; do not ask before steps 1–3.

Before you push a PR's branch and open the PR, commit everything the PR should carry, including
any record of the user's go-ahead to open it. Once auto-merge is on, a later push can land after
the merge, and a push to a merged PR's branch re-creates the remote branch that GitHub deleted.
So push to the branch again only while `gh pr view <n> --json state` shows OPEN. After the push,
run `gh pr view <n> --json state,headRefOid`: if the state is no longer OPEN and `headRefOid` is
not the commit you pushed, the push missed the PR. In either case, tell the user, and ask before
opening a follow-up PR.

1. After opening a PR, immediately enable Auto-fix (`ccd_pr` `set_monitor`) and auto-merge
   (`ccd_pr` `set_auto_merge`) for it. Repos have `allow_auto_merge` and
   `delete_branch_on_merge` on; if a repo lacks them, enable them with
   `gh api -X PATCH repos/<owner>/<repo> -F allow_auto_merge=true -F delete_branch_on_merge=true`.
   Fallback: GitHub refuses auto-merge ("clean" or "unstable" status) when the base branch has
   no required checks or reviews, so it has nothing to wait for. Then merge it yourself with
   `gh pr merge <n> --delete-branch` and the repo's usual method (`--merge`, `--squash` or
   `--rebase`, from its recent history), but only once every check `gh pr checks` lists has
   passed, or right away when the repo has no CI (no `.github/workflows/`; just after a push,
   "no checks reported" can mean the run has not started yet). Do not poll: if checks are still running at the
   end of the turn, say so, and merge on the next turn once they pass. A failed check goes
   to Auto-fix, not to a merge.
2. When the PR merges, verify it: PR state is MERGED, the remote head branch is gone (delete it
   with `git push origin --delete <branch>` if GitHub did not), and whether the PR had CI checks
   (`gh pr checks`). Then report exactly `CI passed, PR merged, remote deleted` — drop the
   leading `CI passed, ` when the repo has no CI checks on that PR.
3. Do the post-merge cleanup yourself; the user never does it. Stop and report instead of
   forcing if anything has uncommitted or unpushed work. To delete the local feature branch, check
   that it holds no commit the merged PR lacks, then use `git branch -D`: a squash or rebase
   merge leaves the branch unmerged to git. Find the session's case, in this order:
   - **A worktree this session made**, by a call this conversation shows (`EnterWorktree`, or
     `git worktree add`): if you are in it through `EnterWorktree`, leave with `ExitWorktree`
     action keep (action remove refuses a worktree whose commits are not on the original
     branch). Then, from the main checkout, switch to the default branch, fast-forward it, run
     `git worktree remove <path>`, delete the local feature branch, and prune (`git fetch --prune`).
   - **No worktree**: switch the checkout to the default branch, fast-forward it, delete the local
     feature branch, and prune.
   - **A worktree the desktop app made** (`get_session` with `self` shows a `worktreePath`):
     switch the main checkout to the default branch, fast-forward it, and prune. Do not remove the
     worktree: removing the session's own worktree moves the session onto the main checkout. Free
     its branch instead. Run `gh pr view <n> --json headRefOid`, then
     `git rev-list --count <headRefOid>..<branch>`, after `git fetch origin pull/<n>/head` if that
     commit is missing here. If it prints 0, run `git switch --detach` in the worktree, then
     `git branch -D <branch>`. If it prints more, or either command fails, stop and report the
     output, and run no other form of either command. The app handles the worktree when the
     session is archived (step 4). Archiving can discard uncommitted changes in it, usually after
     asking, and a kept worktree is removed about 30 days later. Report the worktree's path, and
     the branch if it is still there.
   - **Any other worktree**, such as one from `claude --worktree`, or one whose making this
     conversation no longer shows: switch the main checkout to the default branch, fast-forward
     it, and prune. Do not remove the worktree or delete its branch. Give the user
     `git worktree remove <path>` and then `git branch -D <branch>`, to run from the main checkout,
     and also the switch and fast-forward if Claude Code refuses git in the main checkout.
4. If the workflow has a next step (brainstorming → writing-plans; writing-plans →
   subagent-driven-development or executing-plans; a roadmap stage → its next stage), write a
   handoff brief to a file (follow the prepare-handoff skill) and end with a clickable link to
   that handoff brief file, which the user copies into a new session. Link the brief, not the
   spec or plan. If this session's work is done (subagent-driven-development or
   executing-plans finished, a handoff brief linked above, or a merged PR with no next step;
   nothing left in flight) and it is safe (no uncommitted work, no open PR, no linked session that
   is running or holds unfinished work), offer to archive the session as a `wrap_up` button;
   archive only on the user's yes.
   Do not offer it if this session removed the worktree it started in: it now runs in another
   folder, which an archive might act on. Tell the user so instead.
