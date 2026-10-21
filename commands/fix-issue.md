---
description: Fix a GitHub issue end-to-end — bugs only; feature-shaped issues route to brainstorming. Usage — /fix-issue <number|url>
disable-model-invocation: true
# cc-guide: skills.frontmatter commands.overview @2.1.304.3
---

Fix the GitHub issue given as the argument (an issue number or URL). This
is the bugfix lane only — it never implements features.

1. **Fetch.** `gh issue view <arg>` (add `--comments` when triage needs
   the discussion). Stop gracefully, stating the reason, if `gh` is
   missing or unauthenticated, or the repo has no GitHub remote.
2. **Classify.** Bug-shaped (existing behavior is broken — a regression,
   a crash, a wrong result) → continue. Feature-shaped (new behavior, an
   enhancement, something that never existed) → stop and invoke the
   brainstorming skill with the issue as the idea; the spec gate stays
   intact. Genuinely ambiguous → ask the user which lane, don't guess.
3. **Branch.** Offer an isolated worktree first (the using-git-worktrees
   skill), so the fix does not disturb the current checkout. Then create a
   fix branch off the default branch (e.g. `fix/<issue-number>-<short-slug>`)
   in the worktree, or in place if the user declines. Never fix on the
   default branch directly.
4. **Fix under the house disciplines, by name:** systematic-debugging
   (reproduce before patching), test-driven-development (failing test
   first), verification-before-completion (run the relevant suite and
   confirm the output before claiming done). The suite run may dispatch
   the test-runner agent.
5. **Ship.** Commit the fix, then hand off to the
   finishing-a-development-branch skill and take its Option 2 (push and
   create a PR). Its aged-backlog gate and its review step run before the
   push; do not push or open the PR yourself. Link the issue in the PR
   body (`Fixes #<n>`).
