# Final review and plan completion

Read this when the last task's ledger line is written, and again after a compaction.

## Review the whole plan

After the last task is verified, review the whole branch with two reviewers,
launched in the same message so they run concurrently. Compute one BASE for
both, now: `git merge-base <base-branch> HEAD`. On a branch cut for this plan
that is where the plan began; on a branch that already carried work, the
review covers that work too — as subagent-driven-development's final review
does, and as finishing-a-development-branch relies on. Computing it at review
time, rather than recording it earlier, also survives a `/clear` and a rebase
onto a newer base branch. On the base branch itself that command returns HEAD
— an empty range — so use the start Setup had you record, or the one your
partner confirmed.

1. **code-reviewer** — fill requesting-code-review's
   [code-reviewer.md](../../requesting-code-review/code-reviewer.md) with the plan
   file, the spec path from its `Spec:` line (or `none: the plan is the
   requirement` when it has none) and its `## Review Focus` section word for
   word if it has one, and a pointer to the ledger's `Ruling:` lines, as
   `[PLAN_OR_REQUIREMENTS]` (the reviewer checks each
   Review Focus line deliberately), BASE as `[BASE_SHA]`, and the capable
   model tier (opus), as for any final whole-branch review.

   No per-task reviewer read this run's mutant step, so this review does.
   Add to `[PLAN_OR_REQUIREMENTS]` the ledger's `mutants: none: <why>`
   completion lines. When the workspace holds mutant files, add the path of
   each task's `task-<N>-mutants.md` and of its newest run, the one with
   the highest run number (`task-<N>-mutants.log` is run 1, and
   `task-<N>-mutants-<K>.log` is run K), and this check list. Each
   mutant's patch sits beside its mutants file, and a withdrawn one ends
   in `.withdrawn`.

   - **Inputs.** For each stated rule (a spec sentence the mutants file
     cites as `path:line`, or a rule in the task's brief), the Inputs
     table lists each input shape the rule's words cover, and each row's
     test uses its shape.
   - **Plausible mutants.** Each mutant is a mistake a person might make
     in this code. A syntax break, a crash on every call, or a change no
     one could see is not aimed at anything.
   - **Rules.** Each stated rule has a mutant aimed at it, or an
     `Unreachable:` line that holds: no code in the task's diff decides
     the rule. A spec sentence the task's code rests on that the mutants
     file never cites is a gap.
   - **Tests.** Each test the task adds or changes caught a mutant (a
     `test <id>: caught` line in the run), or has an `Unproven:` line that
     holds: no plausible wrong version of the code exists that the test
     should catch.
   - **Withdrawals.** Each `Withdrawn: K` line holds: no input makes
     mutant K's result differ from the code's in anything a person could
     see. A `Withdrawn: K` whose K also has a live mutant (a `mutant K:`
     line in the run, or a second `Mutant K:` line) does not hold.
   - **Plan tests.** No test whose code the plan gives is loosened (an
     assertion removed or loosened, an expected value changed, the test
     skipped or deleted) without a `Ruling:` line that covers the change.
   - **Revert.** After the mutants, the run ran the tests once more on
     the revert. The revert is the task's diff, from the run's `base:`
     to its `head:`, reversed over each changed path except test files
     and project config files (`pyproject.toml`, `uv.lock`, `uv.toml`,
     `.python-version`, `requirements*.txt`, `setup.cfg`, `pytest.ini`
     and `tox.ini`, at any depth). It puts the task's code back as it
     was at the run's `base:` and keeps the tests at its `head:`. The
     header's `revert:` line sums up that run. The revert section,
     `--- revert ---`, holds a `path:` line for each path that the
     revert put back and a `sha256:` line, then one line for each test
     case in the run's report: `failed <id>: <message>`,
     `not loaded <name>: <cause>` for the test file whose dotted module
     name is `<name>`, `skipped <id>: <reason>`, or `passed <id>`. A
     `skipped` line for a file skipped at its top gives its module name
     alone. A test that skips at the run's `head:` too did not run. The
     revert's output is under `--- output: revert ---`.

     Each test that the task adds or changes fails on the revert, plan
     tests that the task writes included. A test fails on the revert
     when the revert section lists it as failed, or lists its file as
     not loaded. A skip that the revert caused, of the test or of its
     file, counts too. When the `revert:` line gives counts, a test with
     no entry did not run: that is a gap. A test that passes on the
     revert needs a `Keeps:` line or, for a plan test, a `Strengthened:`
     line in the mutants file that holds. A `Keeps:` line holds when the test checks behavior
     that exists at the run's `base:` and that the task keeps. It never
     holds for behavior that the task's brief, or a spec sentence that
     the mutants file cites as `path:line`, changes. A `Strengthened:`
     line holds when its new test fails on the revert and checks the
     behavior that the plan test should have caught. A test with no line
     that holds is a finding: name the behavior that it should have
     caught on the old code. Also check a task whose brief states a
     behavior change. If the `revert:` line gives counts and no test
     fails on the revert, no test checks the change, and that is a
     finding, unless a test that the task adds or changes has no entry.
     A `revert: none: …` line holds when the task's diff changes only
     test files and project config files, and is a gap when it does not.
     A `revert: not applied: …` line is a gap. Read a `no report` or
     `timeout` revert from its output. A `conftest.py` that cannot load
     means that every test needs the change. Any other cause is a gap.
   - **Exemptions.** A task whose brief has a focused pytest command over
     code the task changes is a mutant task, so its `mutants: none: <why>`
     reason does not hold. Lints, link checks and checks over Markdown do
     not make a task a mutant task.

   Each run's `head:` is its task's last commit, the second sha in that
   task's ledger line, not the branch's HEAD. Each run's `base:` is the
   first sha in that line, as its `head:` is the second. Each gap is an
   Important finding: the mutant step is part of the task's requirements,
   and a test that lets a plausible wrong version through lets that
   defect reach a person. The review's last pass does not delete these
   findings.
2. **Codex** — the second-opinion review in
   [codex-review.md](../../requesting-code-review/codex-review.md), with
   `--base <BASE>`.

**Without a subagent tool:** read code-reviewer.md and perform that review
yourself against the BASE..HEAD diff, as a separate pass after the last task's
ledger line. Write `Final review: self-review (no subagent tool)` to the
ledger, and say so in your final message: a self-review by the author is
weaker than a fresh reviewer, and your human partner decides whether that
is enough before merge. The Codex seat still runs when the Codex CLI is present.

Touch nothing until both have returned. When the Codex run completes, copy
its `Codex reviewed <sha>` line into the ledger too, and back into the
conversation if you resume from the ledger, as
subagent-driven-development's final review does.

## Fix pass

Merge the two lists into one, and work it with the receiving-code-review
skill.

Fix the findings that hold up yourself — you are the
implementer here — in ONE pass. Each fix is verified by TDD, not by a
second reviewer: write the test that reproduces the finding, watch it
fail, make it pass, then run the project's documented test command(s).
Record each in the ledger as
`Final: fixed <finding> — <test name> RED→GREEN, suite <result>`. A fix
that changes no behavior (wording, a typo, a wrong name or path in prose
or docs) needs no test: ledger what you changed and that it changes no
behavior, so no test covers it. Any other fix
without a test that failed first is not verified; a documented suite that is not
green after the pass means the pass is not over. Do not dispatch a
re-review: it would re-read a diff whose covering tests already answer
"addressed" and whose suite run already answers "broke nothing".

A finding you decide not to fix is a ruling — `Final: Ruling: <finding> —
<why the code stands> — <cost if wrong>` — and reaches your human partner
in the rulings list at the plan-completion gate. There is no second fix pass.
A test that the revert never ran has one such case that no rerun can clear:
a test in a second suite that one pytest call cannot run with the first. The
revert section has no entry for it however often the script runs. Rule on it
with a `Ruling:` line that names the test and the second suite.

The code-reviewer's Declined to judge lines are not ruled on here: they go
to your partner at the plan-completion gate.

Commit the fixes — the plan-completion protocol commits only
`specs/`, and the branch ships as committed.

## Complete the plan

After the review resolves, run the plan-completion protocol
from the writing-plans skill (its "Plan Completion Protocol" section):
resolve-before-defer gate → plan markup → deferred items → retire the plan
and (conditionally) its spec.

In the gate's batched questions, list every `Ruling:` line in the ledger
first, all of them, in the order made, each with what it costs if wrong, and
tag each one that contradicts spec text `contradicts spec: <spec section>` —
decisions already taken, shown so your partner sees them, not questions —
then fold the final review's Declined to judge lines, each for your human
partner to rule on, into the same batch, so your human partner gets at most
one round-trip. A tagged ruling is still a decision taken, not a question:
the plan's entry in `specs/history.md` records it in place of a spec
amendment, so ask your partner nothing about it. Your partner may still ask
to revert it, which makes it a deferred item. One kind of ruling is not a
decision taken: a `Ruling: (unclear) …` line. It is a question in the same
batch, stalled on your partner's input (writing-plans' protocol step 1). If
your partner overrules it, the change is a follow-up task, and protocol step
1 implements it now. Findings the fix pass left unfixed feed the gate.

When the protocol has finished, delete this plan's workspace — the
directory `sdd-workspace` printed at setup; if you lost it, re-run the
`sdd-workspace` command that Setup ran, with the plan's retired path
`specs/plans/completed/<file>` (protocol step 5 moved the plan there, and the
script exits 2 on a missing plan file; the workspace is named from the
basename, so it is the same workspace). Sibling directories under `.sdd/` belong to other plans; leave them
alone. The delete runs after the protocol, never before, because the
resolve-before-defer gate reads the ledger, the unfixed findings and the
Declined to judge lines to build its questions and deferred items.

## Complete development

Once the plan is complete and retired:
- Announce: "I'm using the finishing-a-development-branch skill to complete this work."
- **REQUIRED SUB-SKILL:** Use finishing-a-development-branch
- Follow that skill to verify tests, present options, execute choice

## Hand off a roadmap stage

When the plan's header carries a `Roadmap:` line, end by the outcome of
finishing-a-development-branch:

| Outcome | Final message |
|---|---|
| Merged locally | "Stage N of `<roadmap>` is merged. Next: /clear (or a fresh session), then resume the roadmap: derive-roadmap on `<roadmap>`." Then stop. |
| PR opened | "Resume the roadmap once `<PR>` merges." |
| Kept | "Stage N is complete on `<branch>` but unmerged. Resume the roadmap after it merges." |
| Discarded | No handoff: the stamp went with the branch. |

Even when asked to keep going, never resume the roadmap here or plan,
brainstorm or route to the next stage (step 3a's Handoff bullets and stamp
still name the stages they feed), and make no model-tier claim. A stage this
session finds already merged when it starts, with the protocol not yet run,
runs the protocol on the merged branch now.
Any other plan ends at Complete development.
