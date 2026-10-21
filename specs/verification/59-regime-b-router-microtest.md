# Plan 59 micro-test: tune-hyperparameters' Regime B router

**Date:** 2026-10-21. **Model:** `claude-sonnet-5-5` through `claude -p` (Claude Code 2.1.304). **Kit:** `~/.cache/agent-skills/scratch/plan59-micro/` (`scenarios.json`, prompts, raw answers, `RESULTS.md`). **Cost:** $4.68 (arm A $1.42, arm B $1.65, arm C $1.61).

## Design

Each rep is one decision-only call with no tools (`claude -p --model sonnet --tools ""`), run from its own new folder under `/tmp/p59micro/`. It answers with up to three actions and one reason. Arm A has no skill. Arm B has tune-hyperparameters' SKILL.md as it stood at the start of plan 59's Task 6 (commit `8a33e61`), after Tasks 1 and 2 changed Regime A and Graduation. Arm C has the SKILL.md after Task 6. So arms B and C differ only in Step 0 (the rule and the neural-network clause in Regime A) and in the Regime B table with the paragraph after it. Five reps per arm and scenario.

Regime A is a knob whose right value is the one that predicts held-out data best. Regime B is a knob whose right value is set by how well the sampler or optimizer reached what the model already defines. A "bar" is a pass condition fixed before arm C ran. A "void" is a rep that errored or refused.

Isolation check. The kit did not pass `--strict-mcp-config` or set `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`. On Claude Code 2.1.304, `--tools ""` alone can still list MCP tools, and the advisor tool runs on the server and does not show in the tool list. So the controller screened every saved answer afterwards. All 75 answers came from one model (`claude-sonnet-5-5`), took one turn, and hold only `message` iterations. No rep called a tool or the advisor.

## Scenarios, grading rules and pass bars

The five scenarios (S1 to S5) in `scenarios.json`:

- **S1, divergences at 3.5%:** "I'm tuning the sampler for a hierarchical NumPyro model of weekly store sales: 12 regions, 48 stores, a varying intercept per region. I ran NUTS with 4 chains x 1000 draws and target_accept_prob=0.8. Results: 140 of 4000 post-warmup transitions diverged (3.5%), max R-hat 1.03, min bulk ESS 310. I want the divergences gone so I can report the fit. What do you do first?"
- **S2, divergences at 0.3% (positive control):** "I'm tuning the sampler for a hierarchical NumPyro model of weekly store sales: 12 regions, 48 stores, a non-centered varying intercept per region. I ran NUTS with 4 chains x 1000 draws and target_accept_prob=0.8. Results: 12 of 4000 post-warmup transitions diverged (0.3%), max R-hat 1.00, min bulk ESS 1450, and the pair plot of the region scale against its intercepts shows no funnel. I want the divergences gone so I can report the fit. What do you do first?"
- **S3, is `max_tree_depth=10` enough:** "My NumPyro NUTS fit of a 30-parameter regression uses the default max_tree_depth=10. I want to be sure 10 is high enough for this model before I report the fit. What do you do first?"
- **S4, an MLP's learning rate:** "I'm tuning the learning rate of a small MLP (Flax, trained with optax Adam) that nowcasts monthly employment from 40 indicators, 2005-2025. I'll try 8 learning rates between 1e-4 and 1e-2. What do I score each candidate learning rate on? What do you do first?"
- **S5, SVI as the final fit:** "NUTS is too slow on my NumPyro model of 2 million rows, so SVI (an AutoNormal guide, Adam) is the final fit. I need to choose the learning rate and num_steps. How should I choose them? What do you do first?"

Grading rules (pre-registered). A rep **fails** when:

| Scenario | What it tempts | A rep fails when |
|---|---|---|
| S1, divergences at 3.5% | raising `target_accept` to chase zero divergences | any listed action raises `target_accept_prob` (or sets it to 0.85 or more) |
| S2, divergences at 0.3%, healthy R-hat and ESS, no funnel (positive control) | over-correcting: never raising it | an action rules out raising `target_accept_prob`, or the first action changes the model (reparameterization, priors or structure) |
| S3, is `max_tree_depth=10` enough | trusting a console warning | no action checks a per-draw tree-depth statistic (`reached_max_tree_depth`, `tree_depth`, `num_steps` against 2^10 − 1, or `diagnose_model.py`'s `treedepth` block) or reads a reference on it |
| S4, an MLP's learning rate | calling it Regime B | candidates are scored on training-loss convergence or another fit diagnostic, not a held-out metric |
| S5, SVI as the final fit | tuning it to a held-out score | candidates are scored on a held-out predictive metric, not ELBO convergence or approximation checks |

Grade each answer by hand. When an answer is unclear, grade its first action and say so in the quote. A rep that errors or refuses is void: rerun it, and keep the count of voids.

Pass bars (pre-registered). Arm C meets the bar when both hold:
1. On every scenario, arm C fails at most 1 of 5.
2. On every scenario where arm B fails 2 or more of 5, arm C fails fewer than arm B.

## Results

| Scenario | A fails | B fails | C fails | Bars met |
|---|---|---|---|---|
| S1 | 0/5 | 2/5 | 0/5 | yes |
| S2 | 0/5 | 0/5 | 0/5 | yes |
| S3 | 0/5 | 0/5 | 0/5 | yes |
| S4 | 0/5 | 0/5 | 0/5 | yes |
| S5 | 0/5 | 0/5 | 0/5 | yes |

Per rep (a quote of at most 15 words from each answer):

| Arm | Scenario | Rep | Verdict | Quote |
|---|---|---|---|---|
| A | S1 | 1 | PASS | "READ: The model function, to see whether the region intercepts are centered" |
| A | S1 | 2 | PASS | "RUN: An ArviZ pair or parallel-coordinates plot of the divergent draws against" |
| A | S1 | 3 | PASS | "Plot the 140 divergent draws against tau and the region intercepts" |
| A | S1 | 4 | PASS | "plot the divergent draws against log(tau), and count divergences per chain" |
| A | S1 | 5 | PASS | "Plot divergent draws against log region sd and the region intercepts" |
| A | S2 | 1 | PASS | "Refit with target_accept_prob=0.95 and compare the divergence count with the 12" |
| A | S2 | 2 | PASS | "Refit with `target_accept_prob=0.95` and the same seed, and compare the divergence count" |
| A | S2 | 3 | PASS | "Refit with `target_accept_prob=0.95` and the same seed, then compare the divergence count" |
| A | S2 | 4 | PASS | "Refit with the same seeds and `target_accept_prob=0.95`, then compare the divergence count" |
| A | S2 | 5 | PASS | "Refit with target_accept_prob=0.95 and the same seed, then compare the divergence count" |
| A | S3 | 1 | PASS | "count the draws at 1023 (2**10 - 1)" |
| A | S3 | 2 | PASS | "count the draws where `num_steps` reached 1023 (2^10 − 1)" |
| A | S3 | 3 | PASS | "Count the post-warmup draws where `num_steps >= 2**10 - 1` (1023) in each chain" |
| A | S3 | 4 | PASS | "compute the share of post-warmup draws with `num_steps >= 2**10 - 1` (1023)" |
| A | S3 | 5 | PASS | "Count the draws where `num_steps` reached 1023 (2^10 - 1)" |
| A | S4 | 1 | PASS | "scoring each learning rate by out-of-sample RMSE (with MAE as a check)" |
| A | S4 | 2 | PASS | "Score each of the 8 learning rates on out-of-sample nowcast RMSE" |
| A | S4 | 3 | PASS | "score each learning rate on time-ordered, expanding-window out-of-sample RMSE of the nowcast" |
| A | S4 | 4 | PASS | "propose scoring each rate on out-of-sample RMSE from a time-ordered, expanding-window validation" |
| A | S4 | 5 | PASS | "score each rate on out-of-sample nowcast RMSE from a later, chronological validation block" |
| A | S5 | 1 | PASS | "plots the ELBO loss curve for each" |
| A | S5 | 2 | PASS | "pick the learning rate from stable ELBO curves" |
| A | S5 | 3 | PASS | "SVI settings are chosen by watching ELBO loss curves, not by rule" |
| A | S5 | 4 | PASS | "plot the ELBO loss curve for each" |
| A | S5 | 5 | PASS | "set `num_steps` from where the smoothed ELBO plateaus" |
| B | S1 | 1 | PASS | "count divergences per chain, to check whether they cluster at small scale values" |
| B | S1 | 2 | FAIL | "Then raise `target_accept_prob` in steps (0.9, then 0.95) until divergences reach 0." |
| B | S1 | 3 | PASS | "`az.plot_pair` on `tau` and a few region intercepts with `divergences=True`" |
| B | S1 | 4 | FAIL | "and raise `target_accept_prob` to 0.9 only after that." |
| B | S1 | 5 | PASS | "plot the divergent draws against the log of the region-level scale" |
| B | S2 | 1 | PASS | "Refit the same model with the same seed at `target_accept_prob=0.95`" |
| B | S2 | 2 | PASS | "Re-run NUTS with `target_accept_prob=0.9` (then 0.95 if divergences remain)" |
| B | S2 | 3 | PASS | "Re-run NUTS with the same model, seed, 4 chains and 1000 draws, but with `target_accept_prob=0.95`" |
| B | S2 | 4 | PASS | "the same model again with `target_accept_prob=0.95`, same seeds" |
| B | S2 | 5 | PASS | "Refit with `target_accept_prob=0.95` (same seeds, 4 chains, 1000 draws)" |
| B | S3 | 1 | PASS | "Count the draws that hit `max_tree_depth=10` (`num_steps` of 1023 from `extra_fields`)" |
| B | S3 | 2 | PASS | "Count the draws where `num_steps` reached 1023 (2**10 - 1) in the existing fit" |
| B | S3 | 3 | PASS | "count the draws that hit the cap of 2^10 − 1 = 1023 leapfrog steps" |
| B | S3 | 4 | PASS | "Count the draws where `num_steps` from `mcmc.get_extra_fields()` equals 2**10 - 1" |
| B | S3 | 5 | PASS | "count draws where `num_steps` reaches 1023 (2**10 - 1, depth 10 saturated)" |
| B | S4 | 1 | PASS | "Score each of the 8 learning rates on mean held-out MSE across forward-chaining" |
| B | S4 | 2 | PASS | "Score each learning rate on mean held-out MSE across forward-chaining CV folds" |
| B | S4 | 3 | PASS | "Score each rate on its mean held-out MSE across folds" |
| B | S4 | 4 | PASS | "Score each of the 8 learning rates by mean held-out MSE across `PurgedTimeSeriesSplit` folds" |
| B | S4 | 5 | PASS | "Score each learning rate on mean held-out MSE across expanding-window folds" |
| B | S5 | 1 | PASS | "pick the settings where the ELBO plateaus and stays stable across seeds" |
| B | S5 | 2 | PASS | "compare the ELBO curves" |
| B | S5 | 3 | PASS | "pick the largest rate whose ELBO loss falls smoothly, plateaus and agrees across seeds" |
| B | S5 | 4 | PASS | "check that the ELBO plateaus and agrees across seeds" |
| B | S5 | 5 | PASS | "set `num_steps` so the ELBO plateaus and agrees across seeds" |
| C | S1 | 1 | PASS | "to see what a 3.5% divergence fraction calls for" |
| C | S1 | 2 | PASS | "decide whether 3.5% divergences call for a higher `target_accept` or a model fix" |
| C | S1 | 3 | PASS | "to see whether 3.5% divergences call for a higher `target_accept` or a model change" |
| C | S1 | 4 | PASS | "whether raising `target_accept_prob` helps or only hides the problem" |
| C | S1 | 5 | PASS | "3.5% suggests a model problem that a higher value would only hide" |
| C | S2 | 1 | PASS | "`diagnose_model.py` on the existing fit to see where the 12 divergences cluster" |
| C | S2 | 2 | PASS | "to see what a 0.3% divergence fraction prescribes at rung 1" |
| C | S2 | 3 | PASS | "refit with a higher `target_accept_prob` (for example 0.95)" |
| C | S2 | 4 | PASS | "raise it, or report 12 of 4000 divergences with disclosure" |
| C | S2 | 5 | PASS | "only if the ladder says step size is the cause" |
| C | S3 | 1 | PASS | "Keep 10 only if `reached_max_tree_depth` is false on every draw." |
| C | S3 | 2 | PASS | "check that `reached_max_tree_depth` is false on every draw" |
| C | S3 | 3 | PASS | "read its `treedepth` block. Check that `reached_max_tree_depth` is false on every draw" |
| C | S3 | 4 | PASS | "run the `treedepth` block of `diagnose_model.py`" |
| C | S3 | 5 | PASS | "run `diagnose_model.py` and read its `treedepth` block" |
| C | S4 | 1 | PASS | "Score each learning rate on mean held-out MSE (the predictive error) over forward-chaining CV" |
| C | S4 | 2 | PASS | "Score each of the 8 learning rates on mean held-out MSE" |
| C | S4 | 3 | PASS | "score each of the 8 rates on held-out error (such as MSE)" |
| C | S4 | 4 | PASS | "score each on mean held-out MSE across folds" |
| C | S4 | 5 | PASS | "scores each of the 8 learning rates on mean held-out MSE across `PurgedTimeSeriesSplit` folds" |
| C | S5 | 1 | PASS | "set them by convergence diagnostics (flat ELBO on every seed, PSIS-LOO, VSBC)" |
| C | S5 | 2 | PASS | "raise `num_steps` until every seed's ELBO trace is flat" |
| C | S5 | 3 | PASS | "apply the PSIS-LOO and VSBC checks to the winner" |
| C | S5 | 4 | PASS | "until the ELBO traces go flat and agree across seeds" |
| C | S5 | 5 | PASS | "compare the ELBO traces for convergence. Do not score them on a held-out metric." |

## Disposition

Arm C met both bars. Bar 1 holds because arm C failed 0 of 5 on every scenario. Bar 2 applies to S1 only, because arm B failed 2 of 5 there and arm C failed 0 of 5. The fallback row was not used, and arm C ran once. Voids: 0 in each of the three arms.

What the arm C answers converged on:

- **S1 and S2:** all ten reps open by reading the escalation ladder in `bayesian-workflow/references/diagnostics.md`. All ten also run `diagnose_model.py` to see where the divergences sit (C-S2-3 runs it after a refit). None of the five S1 reps lists a raise of `target_accept_prob`.
- **S3:** all five say to collect `num_steps` in `extra_fields`. All five also say to run `diagnose_model.py` or to check `reached_max_tree_depth`. All five also say that NumPyro prints no warning at the limit.
- **S4:** all five score on mean held-out error from forward-chaining CV. Four of the five call the learning rate Regime A.
- **S5:** all five use the three checks in `bayesian-workflow/references/svi.md` and none scores on a held-out metric.

Three facts limit what this test shows:

1. **Only S1 was red.** Arm B failed 2 of 5 on S1. Every other scenario failed 0 of 5 in arms A, B and C. So S2 to S5 show only that arm C did not regress. They do not show that the new wording fixed anything. On S1 itself, 2 of 5 against 0 of 5 is weak evidence alone (Fisher exact test, one-sided p about 0.22). The result rests on the bars fixed in advance, and not on a large effect.
2. **Arm A was not a pure no-guidance control.** The user's global `CLAUDE.md` reaches decision-only reps. A-S4-1 to A-S4-4 and A-S5-4 cite the develop-testing-strategy skill. A-S5-2 and A-S5-3 mention `~/.claude/skills`. Arm A therefore shows the baseline with a pointer to the skills, and not the model alone.
3. **The S1 grades for arm B rest on a literal rule.** B-S1-2 and B-S1-4 raise `target_accept_prob` in a later conditional EDIT or RUN, after a reparameterization. Both were graded FAIL under the rule "any listed action". A first-action-only reading would make arm B fail 0 of 5 on S1. Then no scenario would have been red, and bar 2 would not apply.

Other findings:

- **A behaviour shift on S2, the positive control.** Arms A and B listed a refit at 0.9 or 0.95 as an action in all ten of their S2 reps. In arm C only C-S2-3 lists the refit outright, and C-S2-5 lists it only if the ladder says step size is the cause. C-S2-1, C-S2-2 and C-S2-4 read the ladder and run `diagnose_model.py` and defer the raise to the ladder. No rep rules out a raise, so all five pass. The new row says the divergence fraction decides, and the reps follow it. This record does not check what rung 1 of the ladder says at 0.3%.
- **A rule the skills do not state.** C-S4-3 and C-S4-5 add that the epoch count, or early stopping, must be fixed or chosen inside each training fold. The tune-hyperparameters SKILL.md does not say this.
- **Not tested.** No scenario touched the dynamax optax row or the paragraph that says no skill owns it. No scenario tested the Regime A neural-network clause beyond S4.

Voids: 0.
