# RED baseline — divergence-fraction gate in `bayesian-workflow`

**Date:** 2026-09-02 · **Status:** RED + GREEN complete (plan 20, Tasks 5 and 8).
**Governs:** whether the "raise `target_accept_prob` first" rung in `references/diagnostics.md`
binds agents to a first action that Gelman et al. 2026 §12.3 says will not help above ~1% divergences. (§12.3 was read against the PDF in Task 6; this record predates that check.)

> ⚠️ **Quarantine this file during any future micro-test of `bayesian-workflow`.** It names
> the skill and states the expected failure — Channel 1 per `microtest-isolation-channels`.

## Measured behaviour

First concrete action recommended for a varying-intercept Poisson model with 320/4000 (8%)
divergent transitions, R-hat 1.02 and bulk-ESS 41 on the group scale. Rubric: FAIL = raise
`target_accept_prob` / `adapt_delta` / `max_tree_depth` first (PARTIAL counts as FAIL);
PASS = inspect geometry, reparameterize, center predictors, tighten the scale prior, or simplify.

## Fixture

Store-visits Poisson model, 12 regions, centered hierarchical prior (a funnel by construction).
Fixture and artifact cross-grepped clean for `target_accept|1%|funnel|non-centered|reparam` and
`sigma_region|promo|store visits` respectively. Prompts assembled from files outside the repo; skill
symlink, the plan file, the SDD workspace, and every `specs/` file mentioning `target_accept` moved
aside for the window. Dispatch: Agent tool, general-purpose, opus, opaque description ("Step 5 of 10"),
5 reps per arm, fresh context each. Dispatch was not one message: the first batch carried A1–A5 and
B1–B3; B4–B5 went out in a second batch minutes later with the identical prompt file, inside the same
quarantine window. The two PARTIAL reps fell one in each batch — B3 in the first, B4 in the second —
so the PARTIAL verdicts do not track the batch they were dispatched in. Arm B inlined the pre-Task-6 SKILL.md + diagnostics.md (post-Task-2
citations, unchanged rung 1).

Contamination check: every rep's transcript (`subagents/agent-<id>.jsonl`) was grepped for
`Read|Grep|Glob|Skill|Bash|WebFetch` — no hits; the harness reported `tool_uses: 0` for all ten.
**Deviation from the pre-registered VOID rule, disclosed:** every rep's `TOOLS USED:` line names
`advisor`, and the rubric's letter ("names any tool") would VOID all ten. `advisor` is the harness's
built-in model-consultation feature for opus subagents: it forwards the rep's own conversation (the
prompt above) to a second model and returns advice whose content is encrypted in the transcript. It has
no file, search, or skill access, so it cannot carry quarantined text into a rep — the contamination the
VOID rule exists to catch — and it was equally available to every rep in every arm (two A reps report it
rate-limited and empty). Voiding and re-dispatching would reproduce the same condition, so the reps
stand, with two consequences stated plainly: (1) arm A measures *opus + advisor* without the skill, not
an unaided model, so "native" below means native to that configuration; (2) arm C (Task 8) runs under
the same configuration, which keeps the three-arm contrast like-for-like. Because the advisor's content
is opaque, nothing in this record attributes any specific reasoning to it.

## Result

| rep | arm | first action | verdict | contamination |
|---|---|---|---|---|
| A1 | no guidance | "Non-center `a_region` and refit — nothing else changed." | PASS | none |
| A2 | no guidance | "The step: non-center `a_region`" | PASS | none |
| A3 | no guidance | "Non-center `a_region`." (via `numpyro.handlers.reparam`) | PASS | none |
| A4 | no guidance | "Reparameterize `a_region` non-centered, and refit." | PASS | none |
| A5 | no guidance | "refit with `a_region` non-centered" | PASS | none |
| B1 | current skill | "Re-run the same model with `target_accept_prob=0.95`." | FAIL | none |
| B2 | current skill | "Non-center `a_region`." (explicitly declines to raise `target_accept`) | PASS | none |
| B3 | current skill | "Refit with `a_region` non-centered." — code also sets `target_accept_prob=0.9` | PARTIAL | none |
| B4 | current skill | "refit with `a_region` non-centered." — code also sets `target_accept_prob=0.9` ("two changes, not one") | PARTIAL | none |
| B5 | current skill | "Non-center `a_region`." ("unchanged: same target_accept_prob") | PASS | none |

**A_fail = 0/5 · B_fail = 3/5 (VOID replaced: none)**

Scoring note on B3/B4: both name non-centering as the step but raise `target_accept_prob` from the
user's 0.8 default to the skill template's 0.9 in the same code block, and both say so ("0.9 is the
template baseline, not the fix"; "0.9 bundled in; two changes, not one"). The pre-registered rubric
scores a combined first step that raises `target_accept_prob` as PARTIAL, so they count as FAIL. Under a lenient reading (0.9 is the template default, not a divergence response) they PASS and
B_fail = 1/5, which would cross into the ≤ 1 branch and give the one-line conditional instead — so the
form decision is load-bearing on the B3/B4 PARTIAL call, not robust to it. The rule is applied as
written (a rubric that bends after the data are in was never pre-registered); the GREEN run will show
whether the recipe form was needed.

## Decision (pre-registered rule applied)

**Recipe form** for the rung, because B_fail = 3.
GREEN pass bar: C_fail ≤ 1 and ≥ 4/5 C reps converge on the same first action.

## Qualitative evidence

- **The failure is skill-caused, not native to the model configuration** (both arms ran opus + advisor — see Fixture). With no guidance, 5/5 reps non-centered first; the only
  outright FAIL cited the skill by name: "That is rung 1 of the escalation ladder, and it hasn't been
  tried." The same rep *knew* the threshold — its own decision rule was "you want divergences under
  ~1% and `sigma_region` ESS clearing 400" — and still raised first because the ladder told it to.
- **B1's rationalization for why non-centering was wrong:** "each region carries ~104 rows at a rate
  near e³ … That is the informative-likelihood regime where the centered parameterization is the
  better-conditioned one … two outlier regions fighting shrinkage looks like sharp curvature in
  log-sigma that the step size adapted at 0.8 keeps overshooting." (A real consideration several PASS
  reps also raised — but as a caveat *after* choosing to non-center, not as a reason to raise first.)
- **What PASS reps looked at first:** the scale parameter's lower tail ("5% at 0.01 — a scale
  parameter unidentified toward zero"), the *localization* of bad R-hat/ESS to the scale and its
  children ("A globally bad model degrades everything; a funnel degrades the scale parameter and its
  children"), and clean E-BFMI as ruling out an energy problem.
- **The skill's own template leaks into the fix step.** B3/B4 carried the template's
  `target_accept_prob=0.9` into their reparameterized rerun. A gate that says "don't raise" needs to be
  readable as covering *any* raise, including "just adopting the template baseline".
- **Explicit resistance in PASS reps (wording worth keeping for rung 1):** "Resist bumping
  `target_accept` to 0.95+ instead — it buys a smaller step size, which suppresses the divergence
  *count* while leaving the neck unexplored, so you get a clean-looking report and a biased
  `sigma_region`." / "raising it in the same run would confound the test, and it treats the symptom
  rather than the geometry."
- **What reps flagged next (candidates for the failure-signatures table):** unmodeled store level
  (48 stores under 12 region intercepts) and Poisson overdispersion — "Clean divergences will mean
  sampling is fixed, not that the model is adequate — check the PPC before believing the posterior."

## GREEN (new wording — Task 6 recipe / one-line form: recipe)

**Round 1** — the Task 6 wording as committed (571a16c). Rung 1's `> 1` branch ended in three destinations ("Go straight to `az.plot_pair(...)` on the flagged scale/location pairs, the Failure signatures table, and rungs 5–7"), and its two sibling passages named different ones first (fix-list step 1: "skip to 2–4"; SKILL.md row: "reparameterize …, center predictors, check `az.plot_pair`").

| rep | first action | verdict | contamination |
|---|---|---|---|
| C1 | "Non-center `a_region` and refit." — "past the gate where `target_accept_prob` is the right lever" | PASS | none |
| C2 | "Do not touch `target_accept_prob`." → "pair-plot the flagged scale/location pair on the log scale" | PASS | none |
| C3 | "Non-center `a_region` and re-fit." — code comment "leave target_accept_prob at the default" | PASS | none |
| C4 | "plot the scale–location pair to confirm (or kill) the funnel before changing the model" | PASS | none |
| C5 | "dispersion check on the data you already have — no refit" (per-store variance-to-mean ratio, within-region spread) | PASS* | none |

**C_fail = 0/5 · convergence: 2/5 named "non-center" first, 2/5 "pair plot", 1/5 "data dispersion check".** Pass bar missed on the convergence half (≥ 4/5 required) → refactor round 2.

\*C5 is none of the rubric's enumerated PASS actions (inspect geometry / reparameterize / center / tighten the scale prior / simplify); it raises nothing and inspects before any refit, so it is scored PASS and flagged here.

What split the reps: four of five cited the funnel row's strong-per-group-likelihood caveat, computed ~104 rows per region, and went to look before non-centering (C2, C4 by pair plot; C5 by a data check); C1 and C3 read the summary as a textbook funnel and went straight to rung 5. The gate itself held in every rep — nobody raised `target_accept_prob` — so the variance came from the rung's *consequent*, not its predicate.

**Refactor** (writing-skills: one observable predicate → one action). The `> 1` branch now names a single next action — the pair plot of the flagged scale against one of its children, before any refit — and routes from the picture to the table row and rung (neck → rung 5, straight ridge → aliasing row, no shape → rung 6). The two sibling passages were rewritten to name the same first action; SKILL.md is outside Task 8's file list and was changed under the plan's sibling-propagation constraint (commit `d47efab` is the precedent this guards against). The funnel row's caveat was left intact — it is book-accurate — and rung 1 now says the plot, not the printed summary, settles it.

**Round 2** — refactored wording, five fresh reps, same fixture, same quarantine window:

| rep | first action | verdict | contamination |
|---|---|---|---|
| R1 | "pair-plot `log(sigma_region)` against one of its children — before any refit" | PASS | none |
| R2 | "plot the flagged scale against one of its children — before any refit, and before touching a sampler setting" | PASS | none |
| R3 | "Do the diagnostic pair plot — one plot, no refit." | PASS | none |
| R4 | "don't touch the sampler — plot the funnel" | PASS | none |
| R5 | "one `az.plot_pair` of the flagged scale against one of its children, before any refit" | PASS | none |

**C_fail = 0/5 · convergence: 5/5 named "pair plot of the flagged scale vs one of its children" first.** Pass bar met (round 2).

Dispatch note: the quarantine for arm C moved aside this record itself (it names the expected verdict), the plan file, the skill symlink, every `specs/` file mentioning `target_accept` (four in all, this record among them), and the `.sdd/` workspace — the set is listed in `quarantined.txt` and reported at `.sdd/task-8-report.md:8`. In both rounds the reps went out in batches of 2, 2 and 1 — the ~53 KB prompt does not fit five times in one dispatch message — from the identical prompt file, inside one quarantine window (the round-1 prompt is kept as `promptC-r1.md` beside the round-2 `promptC.md`). Every rep reports `TOOLS USED: advisor` except C3 (`none`); the harness reported `tool_uses: 0` for all ten and every transcript grepped clean for `Read|Grep|Glob|Skill|Bash|WebFetch` — the same configuration as arms A and B (see Fixture).

## Disposition

Three-arm contrast: A (no guidance) 0/5 raised `target_accept_prob`; B (the pre-gate skill) 3/5 raised it or bundled a raise into the fix; C (the gated skill) 0/5 in both rounds. The failure was skill-caused, and the gate removes it. What the wording now makes agents do first, above ~1% divergences, is one thing: pair-plot the flagged scale against one of its children — every round-2 rep chose the worst-ESS child, and four of five put the scale on the log axis up front — and let the picture choose between rung 5, the aliasing row, and rung 6; five of five converged on it, against a three-way split when the rung offered three destinations. Two things the reps did that the Failure signatures table should say and does not: (1) four of five reps in each round read the funnel row's caveat as a rows-per-group rule (~104 per region → "strong" → non-centering may hurt), so the table should say what "strong per-group likelihood" means operationally — the pair plot decides, not n per group, which rung 1 now states but the row itself does not; (2) all five round-1 reps and one round-2 rep named the unmodeled store level (48 stores under 12 region intercepts) with Poisson overdispersion as the structural suspect if the plot shows no neck — the table has no row for a missing nesting level or overdispersion presenting as a funnel — and every one of them deferred that change to the user, as rung 7 asks.
