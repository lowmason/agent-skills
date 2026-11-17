---
# cc-guide: rules.rules-files rules.hierarchy @2.1.323
---

# Pull request lifecycle

Standing authorization from the user; do not ask before steps 1–3.

1. After opening a PR, immediately enable Auto-fix (`ccd_pr` `set_monitor`) and auto-merge
   (`ccd_pr` `set_auto_merge`) for it. Repos have `allow_auto_merge` and
   `delete_branch_on_merge` on; if a repo lacks them, enable them with
   `gh api -X PATCH repos/<owner>/<repo> -F allow_auto_merge=true -F delete_branch_on_merge=true`.
   Fallback: GitHub refuses auto-merge ("clean" or "unstable" status) when the base branch has
   no required checks or reviews, so it has nothing to wait for. Then merge it yourself with
   `gh pr merge <n> --delete-branch` and the repo's usual method (`--merge`, `--squash` or
   `--rebase`, from its recent history), but only once every check `gh pr checks` lists has
   passed, or right away when it lists none. Do not poll: if checks are still running at the
   end of the turn, say so, and merge on the next turn once they pass. A failed check goes
   to Auto-fix, not to a merge.
2. When the PR merges, verify it: PR state is MERGED, the remote head branch is gone (delete it
   with `git push origin --delete <branch>` if GitHub did not), and whether the PR had CI checks
   (`gh pr checks`). Then report exactly `CI passed, PR merged, remote deleted` — drop the
   leading `CI passed, ` when the repo has no CI checks on that PR.
3. Do the post-merge cleanup yourself; the user never does it: switch the main checkout to the
   default branch and fast-forward it, delete the local feature branch, remove the session's
   worktree (`ExitWorktree` / `git worktree remove`), and prune (`git fetch --prune`). Stop and
   report instead of forcing if anything has uncommitted or unpushed work.
4. If the workflow has a next step (brainstorming → writing-plans; writing-plans →
   subagent-driven-development or executing-plans; a roadmap stage → its next stage), write a
   handoff brief to a file (follow the prepare-handoff skill) and end with a clickable link to
   that handoff brief file, which the user copies into a new session. Link the brief, not the
   spec or plan. If this session is terminal (subagent-driven-development or
   executing-plans finished, nothing left in flight) and it is safe (no uncommitted work, no
   open PR, no running linked sessions), offer to archive the session as a `wrap_up` button;
   archive only on the user's yes.
