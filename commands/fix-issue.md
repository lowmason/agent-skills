---
description: Fix a GitHub issue end-to-end — bugs only; feature-shaped issues route to brainstorming. Usage — /fix-issue <number|url>
disable-model-invocation: true
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
3. **Branch.** Create a fix branch off the default branch (e.g.
   `fix/<issue-number>-<short-slug>`). Never fix on the default branch
   directly.
4. **Fix under the house disciplines, by name:** systematic-debugging
   (reproduce before patching), test-driven-development (failing test
   first), verification-before-completion (run the relevant suite and
   confirm the output before claiming done). The suite run may dispatch
   the test-runner agent.
5. **Ship.** Commit, push, and open the PR with `gh`, linking the issue
   (`Fixes #<n>` in the PR body).
