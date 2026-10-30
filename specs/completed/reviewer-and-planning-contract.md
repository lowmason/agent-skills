# Reviewer and planning contract: one scope for reviewers, lean plans

> For agentic workers: REQUIRED NEXT SKILL: writing-plans. Plan this spec in a fresh session.
> Do not build from this file directly.

**Status: COMPLETE (2026-10-30)** — implemented by plan 73 (`specs/plans/completed/73-reviewer-and-planning-contract.md`) and retired here. Approved by the owner on 2026-10-29, as committed, including the F1 change, case R4 and the $40 micro-test stop. Designed with the owner through the brainstorming skill, after a `/deferred` Design pick. The behavior record is `specs/red-baseline-reviewer-planning-contract.md`.

## Intent

This spec settles two backlog items together, because they pull one contract two ways.

1. **Superpowers drift findings 9 and 10** (`specs/deferred_items.md`, section
   `audit-3-10-26 routing … — 2026-10-18`, item "Open the planning-surface spec for
   superpowers drift findings 9 and 10"). Finding 9 makes a plan a record of decisions, not
   a copy of the code. Finding 10 makes reviewers judge behaviour that the spec does not
   mention by what a reasonable user expects. It also adds a "Declined to judge" list and a
   Review Focus section in the plan.
2. **The plan-35 reviewer-scope item** (section `35-claude-code-guide-conformance —
   2026-10-04`, item "Scope code-reviewer and task-reviewer findings to correctness and
   requirement gaps"). Plan 35 audited this repo against the Claude Code guide. Its rows
   A-33 and A-34 found that the reviewers invite style and polish findings. The guide's
   section `subagents.isolation` says that a reviewer asked to find problems always finds
   some. It advises: flag only correctness and requirement gaps. The register records the
   gap as exception `reviewers-flag-beyond-correctness` in `build/cc_guide/conformance.toml`.

Finding 10 widens what a reviewer judges. The plan-35 item narrows what a reviewer reports.
The owner's decision D1 joins them: a reasonable user's expectation counts as a requirement,
so a crash on an input that the spec does not name is a requirement gap. Polish is not.

Why now: upstream's motivating failure (obra/superpowers PR #2319) was a grading error. The
final reviewer found a crash on an unnamed input in every rep, graded it Minor, and the crash
shipped. Our reviewers have the same Minor tier and no standard for the spec's silence. Our
plans also show finding 9's pattern. Seven of eight measured plans are more than 4 times the
length of their spec (drift spec, finding 9 table).

## Owner decisions

Each line records the option that the owner picked, in the owner's terms.

- **D1** (owner, 2026-10-29): option A, "one scope". Reviewers report only correctness and
  requirement gaps. Where the spec is silent, a reasonable user's expectation counts as a
  requirement. The Minor/polish tier goes. Every reviewer adds a "Declined to judge" list.
  Exception `reviewers-flag-beyond-correctness` is removed, and `build/check_conformance.py`
  passes.
- **D2** (owner, 2026-10-29): rulings on "Declined to judge" lines are split. In a
  subagent-driven-development run, the controller rules on each line from a per-task review
  and ledgers a `Ruling:` line. The lines from the final whole-branch review go to the owner
  in the batched questions of the plan-completion gate.
- **D3** (owner, 2026-10-29): both executors pass the spec path and the plan's Review Focus
  section to the final code-reviewer. These are subagent-driven-development's
  `references/final-review.md` and executing-plans.
- **D4** (owner, 2026-10-29): staged testing. First, micro-tests R1–R3 and P1–P3. Then one
  full-frame comparison, F1, of the old against the new writing-plans, on Sonnet, with 2
  reps per arm and a cap of about $80. F1 gates only finding 9's step recipe.
  - **Changed after the builder check, to be confirmed at review:** F1's arms now differ only
    in the step recipe. Both use the new reviewers and Review Focus. Plans are written on
    Opus, and the final reviewer keeps its Opus pin, while implementers and task reviewers
    run on Sonnet. The reason: F1 gates only the step recipe. With Review Focus in one arm
    only, Review Focus could hide a loss that the step recipe causes. Case R4 and a $40 stop for the
    micro-tests were also added (section "Testing").
- **D5** (owner, 2026-10-29): approach A, one plan. The shared reviewer block is a copy in
  each of the four reviewer files, and a new test asserts that the copies are identical.
- **D6** (owner, 2026-10-29): the task-reviewer checks, as proposed in section 8. Keep
  "Extra", noise in the test output, and "follows the plan's file structure". Drop the
  other "Structure" checks, "DRY" and verbatim duplication as findings of their own, unless
  the reviewer names a correctness risk.

The design conversation also played back six reviewer proposals and a set of plan-side
proposals, each with an invitation to correct. No correction came, but the owner did not
confirm them either. They appear below as design and are listed under "Proposals played
back, not yet confirmed". The "My calls" section lists the calls that the conversation did
not discuss.

## Goals

- G1. One reviewer scope on every review surface: correctness and requirement gaps only.
  This includes the reasonable-user standard for behaviour that the spec does not mention.
- G2. A visible record of what each reviewer set aside ("Declined to judge"). The record has
  an owner for each line (D2).
- G3. Plans that record decisions: exact interfaces, tests with the spec's values, and
  commands with their passing output. Plans do not copy function bodies that the tests
  already determine.
- G4. Plans that name the implied inputs most likely to hurt a user (Review Focus), each
  pinned by a test.
- G5. Evidence: every change passes its micro-test against a no-guidance control, and the
  step recipe passes F1.
- G6. The register, NOTICE, the runtime adapters and all commit lints stay green.

## Non-goals

- The executing-plans port (finding 11) and finding 13's TDD wording. They have their own
  design item (section `owner-calls-2026-10-21`). This spec edits executing-plans only for
  D3's handoff and for the "Declined to judge" lines.
- The other layers of the "Spec-reading test check" item: worked examples in specs,
  Codex-written acceptance tests, implementer brief excerpts and the end-of-run acceptance
  run. The design leaves room for them (see "Room for the spec-reading check").
- Implementer wording. Upstream measured five executor-side variants in 30 reps with no
  separation from control. The reviewer and the planner are where wording moves behaviour.
- `agents/security-auditor.md`. It has its own Minor tier ("hardening opportunities") and a
  different purpose. It is out of scope.
- Upstream's deletion of `plan-document-reviewer-prompt.md`. This repo has no such file.

## Anti-goals

The work fails, even if every test passes, when any of these happens:

- A reviewer reports a style, naming or polish point as a finding, or a polish point comes
  back through the Codex seat.
- A finding that would hurt a reasonable user is filed under "Declined to judge" in place of
  a grade.
- A plan paraphrases skill wording that a micro-test fixed, because the proportion check
  told it to be shorter.
- The four reviewer copies drift apart with no failing check.
- Any text, fixture or case is copied from `prime-radiant-inc/superpowers-evals`. That
  repository carries no license.

## Approaches considered

| Approach | What it trades | Result |
|---|---|---|
| A. One plan. The shared block is a copy in four files, plus a test that the copies are identical | One large final review. The Review Focus contract spans the plan and the reviewers, so the plan does not split it | **Picked (D5)** |
| B. Two plans in sequence, the reviewer contract first | Smaller diffs, and the plan-35 item closes sooner. But the first plan ships a reviewer that reads a section that no plan writes yet. Two completion runs, and the rule "one plan execution at a time" doubles the wait | Not picked |
| C. One shared reference file that each reviewer reads at run time | One source. But each review adds a tool call that the reviewer can skip. The subagent-driven-development templates paste text by design, and the Codex seat cannot read the file | Not picked |

## Design

### 1. The shared reviewer block

Each of the four reviewer surfaces carries one identical block. The block's final wording is
set by the micro-tests (section "Testing"). The content it must carry:

1. **Scope.** Report only correctness and requirement gaps. Style, naming, formatting,
   optimisation with no effect on correctness, documentation polish and general suggestions
   are not findings. They are not reported anywhere, the "Declined to judge" list included.
   In this repo, skill and agent text is the product. An error in that text that changes
   what its reader does is a correctness defect, not polish. Examples are a contradiction,
   a wrong path, a wrong command, or an instruction that has two readings.
2. **The spec's silence.** Upstream's text is the starting candidate (PR #2319,
   `skills/requesting-code-review/code-reviewer.md`, section "The spec is a vision
   document"). For behaviour that the spec does not mention, judge by what a reasonable
   person using the software would expect. That expectation is a requirement, and the
   spec's silence is not permission. Grade by the effect on that person, not by whether the
   spec names the trigger.
3. **Two grades.**
   - **Critical:** bugs, security problems, data loss, broken functionality.
   - **Important:** a missed or misread requirement, a reasonable-user expectation broken,
     wrong or fragile behaviour, errors that are swallowed, and tests that assert nothing.
   - There is no third grade. A point that would not hurt a user is not reported.
4. **Declined to judge.** Upstream's text is the starting candidate (PR #2319, section
   "Declined to judge"). Before the verdict, list each behaviour that you considered and set
   aside as outside the plan or spec, one line each, with the reason. An empty list means
   you set nothing aside. A behaviour that would hurt a reasonable user is graded, not
   declined. A declined line names a behaviour, not a style point.

The block is plain Markdown with no indentation of its own. The templates carry it inside
their `prompt: |` fences at the template's indentation. The sync test (section 6) compares
the copies after it removes that indentation.

### 2. Changes to each reviewer surface

Find each anchor by its quoted text, because line numbers move.

| File | Anchor (quoted) | Change |
|---|---|---|
| `agents/code-reviewer.md` | "#### Minor (Nice to Have) — style, optimization, docs polish" | Add the shared block. Remove the Minor line and the `### Recommendations` heading. Important loses "architecture". Keep `### Strengths` |
| `agents/task-reviewer.md` | "\"Coverage could be broader\" and polish suggestions are" | Add the shared block. Remove the Minor tier. Part 1 (spec compliance) applies the reasonable-user standard to what the brief does not mention. Handling an implied input is never "Extra". Part 2 keeps only the checks that D6 keeps (section 8) |
| `skills/requesting-code-review/code-reviewer.md` | "#### Minor (Nice to Have)" and "[Code style, optimization opportunities, documentation polish]" | Same as `agents/code-reviewer.md`. The "Reviewer returns" line and the Example Output change to two grades and a "Declined to judge" list. The example's Minor item (progress indicators) is dropped, and the list shows one behaviour set aside as outside the plan |
| `skills/subagent-driven-development/task-reviewer-prompt.md` | "and polish suggestions are Minor." | Same as `agents/task-reviewer.md` |
| `skills/subagent-driven-development/re-review-prompt.md` | "Critical / Important / Minor severities" | Two grades. New findings from a fix also get the "Declined to judge" list |
| `skills/requesting-code-review/codex-review.md` | "`[P2]`/`[P3]` →\nMinor" | Map `[P0]` to Critical and `[P1]` to Important. The controller grades each `[P2]` or `[P3]` finding by its effect on a reasonable user. If a user meets it, it is Important. If it is a behaviour outside the plan or spec, it becomes a declined line ruled under D2. Otherwise it is polish and is dropped |
| `skills/requesting-code-review/SKILL.md` | "Note Minor issues for later" and the example "Minor: Magic number (100) for reporting interval" | Replace with "rule on each Declined to judge line". The example drops the magic-number nit and shows one declined behaviour |

The task-reviewer text for the spec's silence is local text. Upstream added the standard to
its final reviewer only (PR #2319 changed `code-reviewer.md` and not
`task-reviewer-prompt.md`). The drift spec's rule that the contract lands on all four
surfaces makes this repo's copy wider than upstream's. NOTICE marks it as original (section
"Provenance").

### 3. Executor changes

- **subagent-driven-development, `references/fix-loop.md`.** The anchor is "Record Minor
  findings in the progress ledger as you go". This becomes: for each "Declined to judge"
  line from a per-task review, the controller rules and ledgers it in the existing format
  (`Ruling: <what you decided> — <why> — <what it costs if wrong>`) (D2). The rest of that
  bullet changes to match. The final whole-branch review gets a pointer to these `Ruling:`
  lines as context. If it disagrees with a ruling, it reports that as a finding.
- **subagent-driven-development, `references/final-review.md`.**
  - The final code-reviewer dispatch passes the spec path (from the plan's `Spec:` header)
    and the plan's Review Focus section, word for word (D3). This is the spec-path half of
    layer 5 of the "Spec-reading test check" item. Layer 5 is that item's end-of-run step.
    Its other half, a run of reconciled acceptance tests, is not in scope.
  - Some plans have no spec (plans 41, 42, 46 and 47, for example). With no `Spec:` line,
    the plan is the requirement. Review Focus then lists what the plan's requirements imply.
  - "deferred-Minor confirmations", which appears twice, becomes the final review's
    "Declined to judge" lines. They go into the plan-completion gate's batch to the owner
    (D2).
  - The order rule (delete the workspace only after the protocol) keeps its meaning.
- **subagent-driven-development, `SKILL.md`.** The pre-judging warning lists "at most
  Minor". Replace it with a phrase of the same length that still names pre-judging, for
  example "not Important". The body is about 1,080 characters under the compaction window
  (the check measures the body, not the frontmatter). Keep this edit about the same length.
- **executing-plans, `SKILL.md`, Step 3.** The anchor is "fill requesting-code-review's
  [code-reviewer.md]". The final code-reviewer also gets the spec path and the Review Focus
  section (D3). Its "Declined to judge" lines join the findings that "feed the
  resolve-before-defer gate" in Step 4 (D2).

### 4. writing-plans changes (finding 9 and the Review Focus half of finding 10)

The source is upstream PRs #2333 and #2319, on `skills/writing-plans/SKILL.md`.

- **Reader.** The anchor is "zero context for our codebase and questionable taste". Replace
  it with upstream's capable reader: an engineer who has not seen this codebase or spec.
  Given the exact interface and test, this engineer writes idiomatic code. Where the plan
  leaves a choice open, the engineer makes a reasonable one. The handoff's "zero-context handoff"
  wording changes to match.
- **Step size.** "one action (2-5 minutes)" becomes "one action with a checkable result".
  The heading changes as upstream's did.
- **"What a Step Contains" replaces "No Placeholders".**
  - A test step: the test name and its assertions, as code, with the spec's exact values.
  - A code step: the exact signature, the file, and the values the spec pins. A body appears
    only for an algorithm that the signature and tests do not determine, or for exact copy.
  - A verification step: the command and the output that means it passed.
  - A reference to another task goes through that task's Interfaces block.
  - Lines that decide nothing ("TBD", "handle edge cases") stay named as the opposite
    failure.
- **The template's code step.** The template's Step 3 changes as upstream's did: a signature
  and file in the step title, and one line on the approach.
- **The "Remember" list.** Delete "Complete code in every step — if a step changes code,
  show the code".
- **Self-review.** Item 2, "Placeholder scan", becomes upstream's "Step scan". Add item 4,
  Review Focus, and item 5, Proportion.
- **The carve-out (local).** Proportion carries this sentence: wording that a micro-test
  fixed against a no-guidance control is exact copy, and the plan keeps it word for word. It
  does not count as a transcript. Upstream already exempts "exact copy the spec fixes".
  This repo's product is skill text, so the carve-out names micro-tested wording outright.
- **The proportion threshold.** Keep upstream's "several times longer than the spec". No
  lint. P2 and F1 measure whether a number is needed.
- **The Review Focus template section.** Upstream's text sits after Global Constraints.
  It lists the five input classes or failure modes, most likely first, that the spec implies
  but no task's tests exercise. Each line names the input and the behaviour a reasonable
  user would expect. Each line gets its test in the task that owns the code. An empty
  section means the planner checked and found none.
- **Interfaces blocks keep exact signatures and types.** No change, but the design depends
  on it (see "Room for the spec-reading check").
- **No change** to Global Constraints, `## Decisions`, the Execution Handoff's plan review,
  or the Plan Completion Protocol, with one exception. The deferred-item example "Review
  Minor: retry jitter …" (in `SKILL.md` and in `references/deferred-backlog.md`) names a
  tier that no longer exists. Relabel it as a declined review line, with the same meaning.
- **Size.** The body has about 2,550 characters of room under the compaction window (5,000
  tokens at 4 characters each, from `conformance.toml` check `compaction-window`, measured
  on the body). The
  removed lines roughly pay for the new ones. If the body still runs over, move "What a
  Step Contains" and the template's step examples into `references/step-recipe.md`, with
  one pointer line in the body.

### 5. The plan's Review Focus reaches the reviewers

The Review Focus tests sit in the tasks that own the code, so the task brief already carries
them. The task reviewer needs no new input. The final code-reviewer gets the section from
the executor (D3).

### 6. The sync test

Add a test that extracts the shared block from the four reviewer files, removes the
template indentation, and asserts that the copies are byte-identical. Register it where the
commit lints run it. The builder picks the file and the suite (see "Left to the builder").

### 7. Mechanics

- The two `agents/*.md` edits need `uv run --with pyyaml python build/sync_runtime_assets.py`
  and its `--check`. Never hand-edit `runtimes/`.
- Remove exception `reviewers-flag-beyond-correctness` from `build/cc_guide/conformance.toml`
  in the same change as the reviewer edits. Then run
  `uv run --with pyyaml python build/check_conformance.py`.
- Run `build/run_commit_lints.sh` before each commit.
- Edit no cross-skill references other than the ones that this design names. Each one keeps
  its bare skill name, never `superpowers:`. If a new `../<skill>/` path appears (for
  example, executing-plans reading a writing-plans section by name), mirror it in
  `install.py`'s `DEPENDENCIES` or in `SOFT_REFERENCES`, and run the dependency-drift test.

### 8. Task-reviewer checks under D1 (decided, D6)

The builder check raised this after the design conversation. The owner approved it as
proposed.

1. **Which task-reviewer checks survive D1.** Several current checks are not plainly
   correctness checks:
   - **Keep** Part 1's "Extra" (unrequested features, over-engineering). The brief is the
     requirement, and work it did not ask for is a requirement gap.
   - **Keep** "warnings or other noise in the reported test output are findings". Noise can
     hide a failure.
   - **Keep** "follows the plan's file structure". The plan is a requirement.
   - **Drop** as findings of their own: the other "Structure" checks (file size growth,
     decomposition), "DRY", and "verbatim duplication of a logic block". Each of them stays
     reportable when the reviewer names the correctness risk it causes.
   - The plan-mandated rule keeps its other example, "a test that asserts nothing".

## Testing

The project's discipline-skill bar governs: writing-skills' micro-test against a
no-guidance control, then its pressure test. The ready controls are upstream's ideas only.
Every case, fixture and prompt is this repo's own.

### Kit

- **Micro-tests:** copy `specs/red-baseline-writing-skills-split/kit/` into a new record
  directory, `specs/red-baseline-reviewer-planning-contract/kit/`. This is the isolated
  form:
  - `claude -p` with `--tools ""`, `--strict-mcp-config` and `--setting-sources ""`.
  - `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`.
  - Each rep runs from a new, empty directory outside every repository.
  - Pilot `isolation_probe.txt` on the installed Claude Code version before the first rep.
- **Arms:** the no-guidance control, the current text (the RED baseline), and the new text.
  Run 5 reps per arm.
- **Models:** each case runs on the model that runs it in production. The task reviewer runs
  on Sonnet, the final code-reviewer on Opus, and the planner on Opus.

### Micro-test cases

| Case | Setup | Pass bar (new arm) |
|---|---|---|
| R1 Unnamed-input crash | A small spec and a diff. The code crashes on an input that the spec implies ("cannot be read") but never names. No test exercises it | Graded Important or Critical in at least 4 of 5 reps, on the task reviewer and on the final reviewer |
| R2 Polish only | A diff with one real bug and three or more style, naming or optimisation points | The bug is reported, with no polish point in the findings or in the declined list, in at least 4 of 5 |
| R3 Declined list | The R1 and R2 reps | The list is present in 5 of 5, and the R1 crash is never in it |
| R4 Skill-text defect | A diff to a skill file with one wrong path or contradiction, plus two wording-style points | The defect is graded Important or Critical, and no style point is reported, in at least 4 of 5 |
| P1 Planner Review Focus | A spec with one implied input that no stated requirement covers | The plan names it in Review Focus and pins a test in the owning task, in at least 4 of 5 |
| P2 Proportion | A spec for a small script | The new arm's median plan-to-spec ratio is at most 0.6 times the current arm's median, and its median share of lines in code fences is lower |
| P3 Carve-out | A spec that fixes exact skill wording, quoted | The plan keeps the wording word for word in 5 of 5 |

Each bar must also beat the control. A case where the control already passes shows nothing
about the wording. Record that, as the plan-70 record did for its case T6 (a `/deferred`
routing case that the control also passed 5 of 5).

**Stop rule.** A case that misses its bar gets at most two wording rounds. After that, stop
and ask the owner. Nothing ships on a case that has not passed:

- R1, R2 and R4 gate the D1 scope change and the removal of the exception.
- R1 and R3 gate the reasonable-user text and the "Declined to judge" list.
- P1 gates Review Focus. P2 and P3 gate the step recipe, with F1.

The micro-test estimate below is not a cap. If the micro-tests pass $40, stop and ask.

### Pressure test

After GREEN, run writing-skills' pressure test:

- **Reviewer:** the implementer's report argues that the crash is out of scope because the
  spec never names the input. Add time pressure.
- **Planner:** the request asks for "the complete code so I can paste it". A second scenario
  asks for a shorter plan in a way that tempts paraphrase of micro-tested wording.

Any new Red Flags row that the pressure test adds re-runs the affected cases.

### F1 full-frame comparison (D4)

- **Fixture:** one spec of our own for a script, with about three planted defects. Two are
  inputs that the spec implies but does not name. One is a value that the spec states.
- **Arms:** only the step recipe differs. Both arms run the new reviewer contract, the new
  executors and Review Focus. Arm 1 uses the new writing-plans with the old step recipe. Arm
  2 uses the full new writing-plans. This keeps the reviewers and Review Focus from hiding a
  loss caused by the step recipe.
- **Runs:** each rep writes its own plan on Opus, as in production, so planner variance is
  sampled. Two reps per arm, four plans in all. Each plan is executed by
  subagent-driven-development with its production tiers: Sonnet implementers and task
  reviewers, and the final code-reviewer at its Opus pin. Skip the Codex seat.
- **Scoring:** a planted defect is handled when the finished branch passes a hidden
  acceptance test for it. No agent in the run sees that test. Count handled defects per arm,
  summed over the two reps.
- **Isolation:** these runs need tools, so `--tools ""` does not apply. Run in a scratch repo
  outside agent-skills. The arm's skills and agents are installed as project files in that
  repo. Turn off user settings and auto-memory. Pilot an isolation probe for the
  tool-enabled form first.
- **Pass bar:** arm 2's handled count is at least arm 1's, and its median plan-to-spec ratio
  is lower. Two reps can catch a clear loss. They cannot prove that the arms are equal.
- **Cap:** about $80 for F1. Stop and ask the owner if the runs approach it.
- **Gate:** if arm 2 handles fewer defects than arm 1, the step recipe does not ship. For
  this gate, the step recipe is these parts of section 4: Reader, Step size, "What a Step
  Contains", the template step, the Remember line, Step scan and Proportion. Review Focus and every finding-10 and D1 change ship on the micro-test results
  alone.

### Order and cost

1. RED baseline on the current text and the control.
2. GREEN on the new text.
3. Pressure test.
4. F1.

The micro-tests cost about $5–20 (the kit caps each rep at $0.50). F1's cap is above. The
record goes to `specs/red-baseline-reviewer-planning-contract.md`, in the form of the
earlier red-baseline records.

## Provenance

- Every ported change gets a NOTICE change-list line in the superpowers section. The lines
  cover writing-plans (#2333 and the Review Focus half of #2319), requesting-code-review's
  `code-reviewer.md` (#2319), and the executor handoff (the idea in #2319's
  executing-plans hunk).
- NOTICE marks these as this repo's own work:
  - the D1 scope narrowing and the two grades
  - the reasonable-user text in the two task-reviewer surfaces
  - the "Declined to judge" ruling split (D2)
  - the Codex tag mapping
  - the micro-test carve-out
  - the sync test
- NOTICE says that no text comes from `prime-radiant-inc/superpowers-evals`, which carries no
  license. The planted-defect probe and the unnamed-input crash eval are credited as ideas.
- Upstream text quoted in this spec stays under its MIT license (`LICENSE-superpowers`).
  Every skill that changes already carries that file.

## Closing the backlog and the drift spec

On completion, the plan-completion protocol does these things:

- Ticks both backlog items, and records exception `reviewers-flag-beyond-correctness` as
  removed.
- Adds a note to the "Spec-reading test check" item: layer 5's spec-path handoff landed (D3).
  The item stays open.
- Updates the drift spec (`specs/superpowers-drift-spec.md`): the status lines of findings 9
  and 10, and the "Spec candidate, planning surface" bullet under "Suggested disposition".
  The design branch does not edit that file. The execution branch does, from the drift spec
  as it stands on main at that time.
- Retires this spec to `specs/completed/` with the plan.

## Room for the spec-reading check

The later layers of the "Spec-reading test check" item need these things to stay true:

- **Layer 3** has Codex write acceptance tests from the spec and the Interfaces blocks
  alone. So Interfaces blocks keep exact signatures and types, and the lean step recipe does
  not move signatures out of them.
- **Layer 4** puts spec excerpts in the implementer brief. Nothing here changes the brief.
- **Layer 5's other half** runs reconciled acceptance tests before the final review. D3's
  handoff is the slot that it extends.
- Review Focus and "Declined to judge" judge behaviour that the spec does not mention. They
  do not check a misread of what the spec does say. That gap stays with the item.

## Proposals played back, not yet confirmed

The owner saw these in the design conversation with an invitation to correct, and sent no
correction.

- Two grades, Critical and Important, graded by effect on the user.
- The shared block lands on all four reviewer surfaces. The task-reviewer copy of the
  reasonable-user text is local text.
- The Codex seat gets the same scope.
- Every place that counts or stores Minor findings changes.
- The writing-plans changes in section 4: the capable reader, "What a Step Contains", the
  carve-out, upstream's proportion wording with no lint, the Review Focus section, exact
  Interfaces blocks, and the size fallback.
- The micro-test cases and pass bars, as first played back (R1–R3, P1–P3).

## My calls (not discussed in the design conversation)

- The Recommendations section is removed from both output formats. It is where polish would
  return.
- Strengths stays. It is not a finding.
- The Codex `[P2]`/`[P3]` mapping in section 2.
- The F1 fixture skips the Codex seat.
- F1's arm design, run shape and scoring rule (one plan per rep on Opus, the step recipe as
  the only difference, a hidden acceptance test per defect).
- The stop rule: two wording rounds per case, the per-case gates, and the $40 micro-test
  stop.
- P2's bar of 0.6 times the current arm's median ratio.
- Case R4, and the scope sentence that counts an error in skill text as a correctness
  defect.
- Polish is never a declined line. The Codex `[P2]`/`[P3]` points that are polish are dropped.
- The final review gets a pointer to the per-task `Ruling:` lines.
- The "Review Minor" example in the Plan Completion Protocol is relabelled.
- The `references/step-recipe.md` fallback if writing-plans runs over the window.
- The micro-test record lives at `specs/red-baseline-reviewer-planning-contract/`.
- `agents/security-auditor.md` is out of scope.

## Left to the builder

- The final wording of each changed passage, within the content rules above, as fixed by
  the micro-tests.
- The file and suite for the sync test, and how it finds the shared block (for example, by
  heading).
- The case prompts, the fixture spec and diffs, and the F1 scratch-repo setup.
- Task order inside the one plan, provided that the RED baseline runs before any wording
  changes.
