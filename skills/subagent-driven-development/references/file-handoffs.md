# File handoffs

Read this before your first dispatch: which files carry briefs, reports and diffs, and the BASE rule for the review package.

Everything you paste into a dispatch prompt — and everything a subagent
prints back — stays resident in your context for the rest of the session
and is re-read on every later turn. Hand artifacts over as files:

- **Task brief:** before dispatching an implementer, run
  `<this-skill-dir>/scripts/task-brief PLAN_FILE N` — it extracts the task's
  full text to a uniquely named file and prints the path. Compose the
  dispatch so the brief stays the single source of requirements. Your
  dispatch should contain: (1) one line on where this task fits in the
  project; (2) the brief path, introduced as "read this first — it is your requirements,
  including the plan's Global Constraints, with the exact values to use verbatim",
  and the excerpts path beside it (`[SPEC_EXCERPTS_FILE]`, see **Spec
  excerpts**); (3) interfaces and decisions
  from earlier tasks that the brief cannot know; (4) your resolution of
  any ambiguity you noticed in the brief; (5) the report-file path and
  report contract; (6) for the mutant step, `[MUTANTS_GUIDE]`
  (`<this-skill-dir>/references/mutants.md`), `[MUTANT_RUN]`
  (`<this-skill-dir>/scripts/mutant-run`), `[PLAN_FILE]` and `[WORKSPACE]`
  (the directory `<this-skill-dir>/scripts/sdd-workspace PLAN_FILE` prints),
  each as an absolute path, and `[BASE]`, the task's BASE as a full SHA
  (a value, not a path), as the placeholders list in
  [implementer-prompt.md](../implementer-prompt.md) says.
  Exact values (numbers, magic strings, signatures, test
  cases) appear only in the brief.
- **Spec excerpts:** before you dispatch an implementer, write
  `<workspace>/task-N-spec.md`, in this form. `<workspace>` is the directory
  `<this-skill-dir>/scripts/sdd-workspace PLAN_FILE` prints.

  ```text
  Spec: <spec path>

  <path>:<line>: <one spec sentence, verbatim>
  ```

  There is one line per sentence, each taken verbatim from three places: the
  spec sections the task's text cites, the plan's Review Focus lines that name
  this task, and the spec's sentences about the names and values in the task's
  Interfaces block. Leave out the Global Constraints, which the brief already
  carries. When the plan's `Spec:` is `none`, the file holds the single line
  `none: <why>`. Write it for every task, a task that is not a mutant task
  included. For a batch ([batching.md](batching.md)), N is the batch's first
  task number: name the one excerpts file with it, holding the excerpts of
  every task in the batch, and tell the implementer in the dispatch to use it
  as `<N>` for its mutants file and its mutant patches.
- **Review package (diffs):** generate every reviewer's diff as a file — run
  `<this-skill-dir>/scripts/review-package PLAN_FILE BASE HEAD` and pass it the
  path the script reports (or, without bash: `git log --oneline`,
  `git diff --stat`, and `git diff -U10` for the range, redirected to one
  uniquely named file).
  The script does not print a bare path — it prints one summary line,
  `wrote <path>: <N> commit(s), <M> bytes`, so take the path out of it rather
  than pasting the line into a dispatch. The output never enters
  your context; the reviewer sees the commit list, stat summary, and full diff
  in one Read. **Use the BASE you recorded before dispatching the implementer —
  never `HEAD~1`, which silently drops all but the last commit of a multi-commit
  task.** The same BASE fills `[BASE]` in the implementer's dispatch and goes
  to `mutant-run` ([test-run.md](test-run.md)). For the final whole-branch
  review, BASE is the branch's merge base (e.g. `git merge-base main HEAD`).
- **Report file:** name the implementer's report file after the brief
  (brief `…/task-N-brief.md` → report `…/task-N-report.md`) and put it in
  the dispatch prompt. The implementer writes the full report there and
  returns only status, commits, a one-line test summary, and concerns.
- **Reviewer inputs:** the task reviewer gets seven paths — the same brief
  file, the report file, your test run's file ([test-run.md](test-run.md)),
  the review package, the excerpts file (`[SPEC_EXCERPTS_FILE]`), the mutants
  file (`[MUTANTS_FILE]`, `<workspace>/task-N-mutants.md`, N the batch's first
  task number for a batch) and the mutant run
  file (`[MUTANT_RUN_FILE]`, the run file the mutant run reported) — plus the global constraints
  that bind the task, and `[TEST_RULINGS]`: the ledger's `Ruling:` lines that
  cover a change to this task's plan tests, quoted, or `none`. A path for a file
  that does not exist, as for a task that is not a mutant task, takes
  `none: <why>`.
- Fix dispatches append their fix report (with test results) to the same
  report file and return a short summary; re-reviews read the updated file
  and your new run files, the mutant run file too.
