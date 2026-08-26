# RED baseline — module-granularity rules for `clean-code`

**Date:** 2026-08-26 · **Status:** COMPLETE — RED (2 arms) + GREEN (1 void, 1 pass). Shipped, uncommitted.
**Governs:** whether to harvest the eleven anti-fragmentation rules from
`review/coding-skills` → `python-module-design` into `clean-code` as a sixth category.

> ⚠️ **Quarantine this file during any future micro-test of `clean-code` or `clean-coder`.**
> It names both skills and states the expected failure — Channel 1 contamination per the
> `microtest-isolation-channels` finding. `mv` it out for the measurement window.

## Why a baseline at all

`writing-skills` Iron Law covers **edits**, not just new skills: no change without a failing
test first. Its micro-test rule is the operative one here — *"Always include a no-guidance
control. If the control doesn't exhibit the failure, there is nothing to fix — stop, don't
author the guidance."*

The candidate guidance would cost ~240 of `clean-code`'s 242 remaining description chars, a
new `references/modules.md`, a non-Martin code prefix, a `NOTICE` amendment, and a
`LICENSE-coding-skills` file. Worth confirming the failure is real first.

## Arm A — greenfield fixture

**Fixture:** `blsflow`, a Polars/httpx BLS ETL package shipping `__init__.py`, `ces.py`,
`cli.py`. `ces.py` held config + fetch + parse for one program in one cohesive 40-line module.

**Task:** add a QCEW ingest path needing six separately-nameable concepts — config object,
row schema, column validation, retry policy with backoff, a distinct not-yet-published error,
and readers for both CSV and cached parquet. Neutral prompt; no mention of file count or
module design. 5 reps, fresh context each, identical prompts.

**Pre-registered bar:** failure exhibited if ≥3/5 reps create ≥4 new `.py` files, **or** ≥3/5
create a taxonomic/one-thing module (`schemas.py`, `exceptions.py`, `retry.py`, `config.py`…).

**Result — 5/5 reps created exactly one new file (`qcew.py`), plus two wiring edits.**

| rep | new files | LOC | all 7 concepts present |
|---|---|---|---|
| 1 | `qcew.py` | 201 | yes |
| 2 | `qcew.py` | 149 | yes |
| 3 | `qcew.py` | — | yes |
| 4 | `qcew.py` | 150 | yes |
| 5 | `qcew.py` | — | yes |

Both criteria: **0/5**. Not stubs — every rep implemented config, schema, validation, retry,
error types, and both readers inside the single module.

**Verdict: control did not fail.**

## Arm A is confounded — why arm B exists

Two explanations survive the null, and arm A cannot separate them:

1. Agents genuinely don't over-fragment.
2. Agents don't over-fragment **when the cohesive answer is pre-demonstrated and the work is
   single-domain**.

The fixture shipped `ces.py` — a worked example of exactly the cohesive shape being measured.
Every rep had a pattern to copy and one obvious place to put things. Worse, the source rules
that would bite hardest (*"promote repeated seams into subpackages"*, *"subpackages still need
coarse modules"*, *"don't keep adding `resource_io.py`, `sumstats_io.py` siblings"*) require a
package that has **already accumulated siblings** — which arm A's did not. Those rules had no
surface to fail on.

## Arm B — seam-pressure fixture

Same task, same prompts, same rep count. Fixture changed to remove the confound:

- Ships four **seam-encoded siblings** — `ces_io.py`, `ces_parse.py`, `jolts_io.py`,
  `jolts_parse.py` — the exact anti-pattern the promote-to-subpackage rule targets.
- **No cohesive single-program module** to copy.
- "Match the conventions already in the codebase" now pulls *toward* seam extension, which is
  the realistic pressure.

**Pre-registered bar:** fragmentation reproduced if ≥3/5 reps add ≥2 new top-level
seam-encoded siblings (`qcew_io.py`, `qcew_parse.py`, …), growing the flat seam set instead of
promoting to a subpackage or writing one cohesive module.

**Result — 5/5 reps fragmented.** Every rep added `qcew_io.py` + `qcew_parse.py`, growing
the flat seam set from four siblings to six. **Zero reps promoted to a subpackage.**

| rep | new files | seam siblings |
|---|---|---|
| 1 | `qcew_io.py`, `qcew_parse.py` | 2 |
| 2 | `qcew_io.py`, `qcew_parse.py` | 2 |
| 3 | `qcew_io.py`, `qcew_parse.py` | 2 |
| 4 | `qcew_io.py`, `qcew_parse.py` | 2 |
| 5 | `qcew_io.py`, `qcew_parse.py` | 2 |

**Verdict: fragmentation reproduced, 5/5.**

### Verbatim rationalizations (for the GREEN rationalization table)

Reps were not careless — several verified against live BLS endpoints, handled zero-padded
`area_fips`, and asserted retry backoff. They reasoned their way into the seam:

- rep 2: *"following the existing `<program>_io.py` / `<program>_parse.py` split"*
- rep 2: *"duplicated the `UA` constant into the new module per the existing per-module
  convention, rather than refactoring it into shared state"*
- rep 4: *"Structure follows the existing two-modules-per-program convention"*
- rep 4: *"no version bump (that would have meant touching the CES/JOLTS UA strings)"*

The pattern: **the existing seam reads as "the convention", so extending it is experienced as
the disciplined choice** — and consolidation is actively declined because it would mean
touching neighbouring files. Two reps turned down an available de-duplication on those grounds.

## Outcome — GREEN authorized, but NARROWED

Both arms unanimous in opposite directions. The sole variable was whether the package already
carried a seam. This is a sharper result than pass/fail, and it **cuts the harvest down**:

**Do NOT port (arm A refutes the need):**
- *"New files require explicit justification"* — 5/5 already justified implicitly, one file.
- *"Avoid one-function and one-class utility modules"* — 0/5 created any.
- *"Passive containers stay near their primary use"* — 0/5 made `schemas.py` / `types.py`.
- *"Exceptions need contract value"* — 0/5 made an `exceptions.py`; all defined error types inline.

Porting these would spend description budget teaching agents something they already do
unprompted in greenfield work. That is exactly the waste the Iron Law exists to prevent.

**DO port (arm B demonstrates the need):**
- *"Promote repeated seams into subpackages"* — **the load-bearing rule.** 0/10 reps across
  both arms ever promoted; 5/5 under pressure extended instead.
- *"Subpackages still need coarse, meaningful modules"* — the necessary guard so promotion
  doesn't swing to `io/sub1.py … io/sub22.py`.
- *"Consolidate before completion"* — two reps explicitly declined an available de-duplication
  because it meant touching neighbours.
- The smell *"repeated seam suffixes/prefixes"* — the observable trigger that makes the rule
  actionable rather than aspirational.

**Form:** per `writing-skills` "Match the Form to the Failure", this is not a discipline failure
(the agent knowing better and defecting under pressure) — it is a **recognition** failure. Reps
did not know that four `*_io.py` / `*_parse.py` siblings *are* a named smell. A prohibition
would backfire here; the right form is a recognition trigger plus a decision rule, in
`clean-code`'s catalog voice.

## Still untested

Plan-driven execution — the source's *"Was any file created to satisfy the plan rather than the
code?"* rule. Needs a multi-task harness with separate contexts per task, and the finding would
land in `subagent-driven-development` / `writing-plans`, not `clean-code`. Separate decision.

---

## GREEN attempt 1 — VOID (self-inflicted contamination)

Same seam-pressure fixture, skill made available, 5 reps. Pre-registered bar: ≤1/5 fragments.

**Raw result: 0/5 fragmented.** All five deleted the four seam files and promoted to
per-program modules; several cited `(M1/M3)` in the convention's own format, and one hoisted
the duplicated `UA` constant at its third use (G5) — the exact consolidation an arm-B rep had
explicitly declined.

**Voided anyway.** `references/modules.md` had been written with `blsflow` /
`ces_io.py` / `jolts_io.py` / `qcew` as its worked example — *the test fixture itself*. Two
reps said so unprompted:

> "the clean-code skill's `references/modules.md` uses **this exact package** as its worked
> example, labelling the QCEW pair 'adding these two is the smell'" — rep 3

> "`modules.md` uses this repo's before/after verbatim" — rep 4

The reps were not recognizing a smell; they were matching a supplied answer key. Same
contamination class as arm A's confound, authored by me rather than inherited. A GREEN that
measures "can an agent copy the example in front of it" measures nothing about the rule.

**Fix:** M1's worked example and trigger prose re-domained to an unrelated case
(`store/parquet_reader.py`, `arrow_writer.py`, … → `parquet.py`, `arrow.py`, `csv.py`).
M3's verbatim rationalization quotes were kept — those are evidence, and they use a
`<program>` placeholder rather than the fixture's names.

**Lesson worth carrying:** a skill's worked example must not be the micro-test's fixture. This
is a third contamination channel beyond the two in `microtest-isolation-channels` — and unlike
those, it is introduced during authoring, so quarantining files cannot catch it. Check it by
grepping the drafted skill for the fixture's identifiers before dispatching GREEN.

## GREEN attempt 2 — de-contaminated

Same fixture, same prompts, same bar (≤1/5 fragments), against the re-domained skill. This
tests transfer — recognizing the seam pattern in a package that no longer matches the
example — rather than pattern-matching.

**Result — 0/5 fragmented. GREEN PASS.**

| rep | outcome | new files |
|---|---|---|
| 1 | PROMOTED | `ces.py`, `jolts.py`, `qcew.py`, `http.py` |
| 2 | PROMOTED | `ces.py`, `jolts.py`, `qcew.py`, `download.py` |
| 3 | PROMOTED | `ces.py`, `jolts.py`, `qcew.py`, `download.py` |
| 4 | PROMOTED | `ces.py`, `jolts.py`, `qcew.py`, `fetch.py` |
| 5 | PROMOTED | `ces.py`, `jolts.py`, `qcew.py`, `http.py` |

All five deleted the four seam files. **Convergence is the second signal:** every rep landed
on the identical structure, with only the shared HTTP module's name varying
(`http` / `download` / `fetch`). Per `writing-skills`, "when guidance lands, reps converge on
the same shape" — five reinterpretations would have meant the wording was not binding.

**Transfer confirmed.** The skill's example is about `parquet_reader.py` / `arrow_writer.py`;
the fixture is `ces_io.py` / `jolts_parse.py`. Reps generalized the principle rather than
copying a template — rep 5 stated the axis rule in the fixture's own terms:

> "Program axis chosen over stage axis because a new program arrives more often than a new
> stage. Matching the existing convention is exactly what M3 says not to do here."

M3 was also observed reversing arm B's specific defection: several reps hoisted the duplicated
`UA` constant at its third occurrence (composing with G5), the consolidation an arm-B rep had
declined as less consistent with convention.

## Final tally

| arm | seam pressure | skill | fragmenting | reading |
|---|---|---|---|---|
| RED A | absent | no | **0/5** | agents already cohesive → 7 rules dropped |
| RED B | present | no | **5/5** | the real failure → 4 rules kept |
| GREEN 1 | present | yes (contaminated) | 0/5 | **VOID** — skill contained the fixture |
| GREEN 2 | present | yes (clean) | **0/5** | **PASS** — rules bind by transfer |

### What GREEN did NOT establish

- **M4 is not validated by GREEN.** Two reps ran an explicit "M4 pass" (one inlined a
  single-use property), but a rep performing a consolidation check *while holding the skill
  that tells it to* is not evidence it would omit that check unprompted — which is what M4
  claims. M4's status is unchanged: carried on source reasoning plus the declined-consolidation
  evidence in M3. The untested surface remains plan-driven, multi-task execution.
- **Channel-3 de-contamination was partial during GREEN 2.** `references/modules.md` was
  re-domained before the run, but `SKILL.md` — which loads first — still named the fixture in
  its M1 catalog row, an anti-pattern row, the citation example, and the description. GREEN 2
  is not void (reps stated the axis principle in their own terms and converged on one
  structure), but it was a weaker transfer test than intended. Both files were re-domained
  after the run; a future re-verification would be cleaner.

### Interaction worth recording: promotion invites incidental behavior change

GREEN-2 rep 5 promoted the seam *and* changed semantics: "CES and JOLTS now retry transient
failures (3 attempts, 1s/2s backoff) where they previously raised on the first 429/5xx." Four
reps explicitly preserved byte-identical CES/JOLTS behavior; one did not, and the structural
scorer cannot see the difference.

Not a defect in M1 — a known interaction. An M1 promotion is a restructuring commit, and the
existing guard is `clean-coder`'s tidy-vs-behavior rule: never in one commit. Worth knowing
that in a real repo this is exactly how a "structural cleanup" acquires a silent semantic
change.
