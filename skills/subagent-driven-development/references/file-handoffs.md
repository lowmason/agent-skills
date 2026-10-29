# File handoffs

Read this before your first dispatch: which files carry briefs, reports and diffs, and the BASE rule for the review package.

Everything you paste into a dispatch prompt — and everything a subagent
prints back — stays resident in your context for the rest of the session
and is re-read on every later turn. Hand artifacts over as files:

- **Task brief:** before dispatching an implementer, run this skill's
  `scripts/task-brief PLAN_FILE N` — it extracts the task's full text to a
  uniquely named file and prints the path. Compose the dispatch so the
  brief stays the single source of requirements. Your dispatch should
  contain: (1) one line on where this task fits in the project; (2) the
  brief path, introduced as "read this first — it is your requirements,
  including the plan's Global Constraints, with the exact values to use verbatim"; (3) interfaces and decisions
  from earlier tasks that the brief cannot know; (4) your resolution of
  any ambiguity you noticed in the brief; (5) the report-file path and
  report contract. Exact values (numbers, magic strings, signatures, test
  cases) appear only in the brief.
- **Review package (diffs):** generate every reviewer's diff as a file — run
  this skill's `scripts/review-package PLAN_FILE BASE HEAD` and pass it the path
  the script reports (or, without bash: `git log --oneline`, `git diff --stat`,
  and `git diff -U10` for the range, redirected to one uniquely named file).
  The script does not print a bare path — it prints one summary line,
  `wrote <path>: <N> commit(s), <M> bytes`, so take the path out of it rather
  than pasting the line into a dispatch. The output never enters
  your context; the reviewer sees the commit list, stat summary, and full diff
  in one Read. **Use the BASE you recorded before dispatching the implementer —
  never `HEAD~1`, which silently drops all but the last commit of a multi-commit
  task.** For the final whole-branch review, BASE is the branch's merge base
  (e.g. `git merge-base main HEAD`).
- **Report file:** name the implementer's report file after the brief
  (brief `…/task-N-brief.md` → report `…/task-N-report.md`) and put it in
  the dispatch prompt. The implementer writes the full report there and
  returns only status, commits, a one-line test summary, and concerns.
- **Reviewer inputs:** the task reviewer gets three paths — the same brief
  file, the report file, and the review package — plus the global
  constraints that bind the task.
- Fix dispatches append their fix report (with test results) to the same
  report file and return a short summary; re-reviews read the updated file.
