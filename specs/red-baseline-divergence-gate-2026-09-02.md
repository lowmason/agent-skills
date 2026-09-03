# RED baseline — divergence-fraction gate in `bayesian-workflow`

**Date:** 2026-09-02 · **Status:** RED complete; GREEN pending (Task 8 of plan 20).
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
quarantine window. Arm B inlined the pre-Task-6 SKILL.md + diagnostics.md (post-Task-2
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
