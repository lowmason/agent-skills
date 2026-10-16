# Late-heading ratchet for the compaction-window waivers

**Status: COMPLETE (2026-10-16)** — implemented by plan 48 (`specs/plans/completed/48-compaction-late-heading-ratchet.md`) and retired here. Design approved 2026-10-16 (D1, D2). One implementation difference: R2's failure message says the row and its exception go once the body fits the window, not "once no row remains", because the exception also waives the length finding; the plan's deviation notes record it.

## Goal

Stop a new critical heading from slipping past the compaction window in `skills/writing-skills/SKILL.md` while every commit lint passes. Plan 47 guards the other two oversized skills; this guards the third.

## Background

Facts verified at `6fa8959` (plan 47 merged as lowmason/agent-skills#51).

- The `compaction-window` check (`check_compaction_window` in `build/check_conformance.py`; parameters in the `[[check]]` entry `compaction-window` of `build/cc_guide/conformance.toml`) reports two kinds of finding for a `SKILL.md` body over 5,000 tokens (20,000 characters at 4 per token): a length finding, and one finding for each heading, at any level and outside a code fence, that contains a word from `headings` (STOP, Red Flags, Critical, Gotchas, Iron Law, Hard Gate, Warning) and starts at or past that offset.
- Exactly three skills exceed the window: `bayesian-workflow` (about 8.2k tokens), `subagent-driven-development` (about 7.4k) and `writing-skills` (about 7.2k).
- `apply_waivers` waives per (check, file). Exception `skill-body-past-compaction` waives the first two; exception `writing-skills-late-critical-headings` waives the third. Both waivers hide the heading findings along with the length finding.
- Plan 47 guards the first exception: the `critical_placement` commit lint runs the `test_real_skill_*` tests in `build/test_check_conformance.py`, which pin each critical span of those two skills inside the window (`CRITICAL_SPANS`) and compare `CRITICAL_SPANS` to that one exception's `artifacts`.
- Nothing guards the second. Its waiver hides two heading findings today:
  - `### Create Red Flags List` (line 545): advice about writing a Red Flags list in other skills. A false positive of the heading heuristic.
  - `## STOP: Before Moving to Next Skill` (line 631): a real critical section. The owner accepted it past the window on 2026-10-05; the register's `tracked_in` for the exception is portability Stage D (`specs/agent-skills-portability-spec.md`, not yet planned), which owns every `writing-skills` edit.
- A new late heading in `writing-skills`, such as `## Warning`, therefore passes every lint.
- Source: the `## 47-placement-lint — 2026-10-16` item in `specs/deferred_items.md`, from plan 47's review.

## Decisions

- **D1** (owner, brainstorming, 2026-10-16): ratchet the two known late headings by text. Moving STOP inside the window is Stage D's work; dropping the item leaves the blind spot.
- **D2** (owner, brainstorming, 2026-10-16): build the ratchet as tables in the tests (Approach A). Narrowing the waiver in the register was rejected: it changes the waiver semantics plan 47's D1 left alone, and it would not cover span ends.

## Requirements

All changes use the existing `critical_placement` lint. It selects tests by `-k test_real_skill`, so every new test in `build/test_check_conformance.py` is named `test_real_skill_…`.

- **R1. Acknowledged table.** `build/test_check_conformance.py` gains `ACKNOWLEDGED_LATE`, beside `CRITICAL_SPANS`, mapping a file to the headings the owner accepted past the window. It has one entry: `skills/writing-skills/SKILL.md` with `### Create Red Flags List` and `## STOP: Before Moving to Next Skill`. Headings are matched by text, never by line number or offset.
- **R2. Equality.** A parametrised test `test_real_skill_late_headings_match_the_acknowledged_set` runs for each file in `ACKNOWLEDGED_LATE`. It reads the file's late headings from the messages of `check_compaction_window` that contain `starts past` (the quoted heading in `line N: heading '<text>' starts past …`) and asserts the sorted list equals the file's sorted table entry. Equality, not subset: a heading that is gone from the file fails too. The message says that a new late heading belongs inside the window, and that a removed one means shrinking the table row, and removing the exception once no row remains. If the message wording ever changes, the parsed list comes back empty and the test fails closed.
- **R3. Pinned files unchanged.** The existing tests for `CRITICAL_SPANS` files stay as they are.
- **R4. Coupling over all waivers.** `test_real_skill_spans_match_the_compaction_waiver` keeps its name and is no longer keyed to one exception id. It collects the `artifacts` of every exception whose `check` is `compaction-window` and asserts they equal `set(CRITICAL_SPANS) | set(ACKNOWLEDGED_LATE)`. It also asserts the two tables share no file. With no such exception it fails with a message to retire the lint, both tables and the `test_real_skill_*` tests together. On any other mismatch the message names the file and says which side lacks it.
- **R5. End-to-end refusal.** `build/test_commit_lints.py` gains a clone-based test. It appends a `## Warning` section to the end of `skills/writing-skills/SKILL.md` in the clone, commits with `-am`, and asserts a non-zero exit, an unchanged HEAD, `failed_names(result) == {'critical_placement'}`, and the `FAILED …test_real_skill_late_headings_match_the_acknowledged_set[skills/writing-skills/SKILL.md]` line in stderr. Before R2 exists the same commit must succeed, which demonstrates the hole.
- **R6. Register text.** In `build/cc_guide/conformance.toml`, refresh the `reason` of `writing-skills-late-critical-headings`: it cites lines 630 and 544 that have moved. The new text names the two acknowledged headings, says the waiver is per check and file, and names the guard. The exception's `id`, `check`, `sections`, `artifacts`, `guide`, `evidence` and `tracked_in` stay as they are.
- **R7. Docs and backlog text.** The comment above `CRITICAL_SPANS`, the `CLAUDE.md` placement block and the `specs/deferred_items.md` note under "Fit the subagent-driven-development and bayesian-workflow bodies inside the compaction window" say that removing an exception removes its file's rows, and that the lint and the `test_real_skill_*` tests retire when the last `compaction-window` exception goes. The count of commit lints stays eight.

## Non-goals

- No edit to `skills/writing-skills/SKILL.md`. Stage D owns it, and it is a discipline skill whose changes are micro-tested.
- No change to `apply_waivers`, `parse_exceptions`, `check_compaction_window`, the check's parameters, or any exception's `id`, `check` or `artifacts`.
- No new commit lint, and no edit to `build/run_commit_lints.sh` or `.github/workflows/lints.yml`.
- No `cli.py baseline cite` on any edited file. `CLAUDE.md` and `conformance.toml` carry drift citations.

## Testing

Test-first, with the mutation REDs plan 47 used. Test counts are deltas.

- R5's commit succeeds before R2 exists, then is refused after it.
- Appending a late `## Warning` heading to `writing-skills` fails R2.
- Deleting one acknowledged row fails R2 and names the heading.
- Adding a file to either table without an exception, or an exception artifact without a row, fails R4.
- Each mutation is restored and the suite rerun green.

## Done when

A late critical heading added to `skills/writing-skills/SKILL.md` fails a commit lint with `writing-skills-late-critical-headings` still in place. That closes the `## 47-placement-lint` backlog item.

Size: plan. The planner chooses the task split; R5's RED (the commit succeeds) must be observed before R2 lands, as plan 47's Task 1 did for its refusal test.
