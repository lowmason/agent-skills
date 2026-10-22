# Plan 65 micro-test: track-model-experiments' description (V1, track arm)

**Date:** 2026-10-22. **Model:** `claude-sonnet-5-5` (from each rep's init record) through `claude -p` (Claude Code 2.1.304). **Kit:** `~/.cache/agent-skills/scratch/plan65-micro/` (`run_microtest.py`, `screen.py`, `system-*.txt`, `results-*.json`, `raw/`). **Cost:** $0.76 (pilot $0.03, control arm $0.37, variant arm $0.36).

## Design

Each rep is one decision-only `claude -p` call, run from its own new folder under `/tmp/p65micro/`. The isolation flags are `--model sonnet --tools "" --strict-mcp-config --no-session-persistence --system-prompt-file <listing>`, with `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1` set. The reply is one skill name, or `none`.

The system prompt lists five skills by name and description, in name order: bayesian-workflow, evaluate-deep-learning, recommend-probabilistic-model, track-model-experiments and tune-hyperparameters. The four probes are the skills next to track that a prompt could also route to. Their descriptions come from the base commit `7603e69` in both arms.

- **Control arm:** track's description at the base commit. That text is also the description at the start of this task (`671b85a`), because Tasks 1 to 4 changed only track's body.
- **Variant arm:** the draft description in the working tree.

Each arm runs the seven prompts below, 5 reps each, so 35 reps per arm.

**Isolation check.** A pilot rep ran first. Its init record showed `"tools": []` and `"mcp_servers": []`, so the kit's `clean` flag was True. The `usage.iterations` list was empty on every rep, so the kit's iteration clause passes without proof. A positive screen was used instead (`screen.py`). For each rep, the result event must show only `claude-sonnet-5-5` in `modelUsage`, `num_turns` of 1 and zero server tool use. An advisor call would add a second model to `modelUsage`.

Two channels still reach every rep in both arms. Three user-level SessionStart hooks run, and two of them add output-style context (the "learning" and "explanatory" styles). The user's global `CLAUDE.md` and rules also load. This context is the same in both arms and names none of the five listed skills. So it does not change the contrast between the arms.

**Probe drift check.** The plan checked that the four probe descriptions at HEAD still equal those at the base commit:

```
bayesian-workflow CHANGED
evaluate-deep-learning same
recommend-probabilistic-model CHANGED
tune-hyperparameters same
```

Plan 64 (executed on main before this task) changed the bayesian-workflow and recommend-probabilistic-model descriptions. The kit still uses the base text for all four probes, as the spec asks. So this test measures the new track description against the probe descriptions at plan time, not the descriptions on main now.

**Pass rule** (spec V1, fixed before the runs):

1. On each trigger prompt (T1–T3), the variant's count of answers that route to `track-model-experiments` is at least the control's count minus 1.
2. On each near-miss prompt (N-…), the variant's count that routes to `track-model-experiments` is at most the control's count: no near-miss newly routes to the target.
3. Every rep is clean (`tools` and `mcp` empty, only `message` iterations). A rep that is not clean is void: rerun it and count it.

## Prompts

- **T1-cv-ledger:** "I've fit five variants for a county-level employment panel: two ridge regressions and three gradient-boosting models, each scored with the same 5-fold GroupKFold MSE. I keep forgetting which feature set each one used and why I dropped two of them. I want one record of the variants, ranked on those fold scores, so I can decide which to ship."
- **T2-bayes-lfo:** "I have three NumPyro state-space nowcast models: local level, local linear trend, and AR(2) errors. I want to rank them by their leave-future-out log score at a one-month horizon and keep a record of what each variant changed."
- **T3-elpd-variants:** "I'm on variant 6 of a hierarchical NumPyro model of weekly store sales. Each variant changed a prior or the pooling, and I've lost track of what v3 changed and why v4 was dropped. I want the variants ranked by ELPD with the reasons written down."
- **N-bayesian-workflow:** "I fitted one hierarchical NumPyro model of store sales. Max R-hat is 1.04 and 30 of 4000 transitions diverged. How do I check this fit and report it?"
- **N-evaluate-deep-learning:** "I trained three transformer checkpoints for demand forecasting with different random seeds. I want to compare them on a held-out test period and decide which checkpoint to ship."
- **N-tune-hyperparameters:** "I need to choose the learning rate, max depth and L2 penalty for a gradient-boosting nowcast. I plan an Optuna search with rolling-origin cross-validation and must not leak future data."
- **N-recommend-probabilistic-model:** "I have monthly counts of business births by county. They are overdispersed and a third are zero. Which kind of model should I fit?"

## Results

Routed count is the number of the 5 answers that name `track-model-experiments`.

| Prompt | Kind | Control | Variant | Rule | Held |
|---|---|---|---|---|---|
| T1-cv-ledger | trigger | 5/5 | 5/5 | 1: variant at least 4 | yes |
| T2-bayes-lfo | trigger | 5/5 | 5/5 | 1: variant at least 4 | yes |
| T3-elpd-variants | trigger | 5/5 | 5/5 | 1: variant at least 4 | yes |
| N-bayesian-workflow | near-miss | 0/5 | 0/5 | 2: variant at most 0 | yes |
| N-evaluate-deep-learning | near-miss | 0/5 | 0/5 | 2: variant at most 0 | yes |
| N-tune-hyperparameters | near-miss | 0/5 | 0/5 | 2: variant at most 0 | yes |
| N-recommend-probabilistic-model | near-miss | 0/5 | 0/5 | 2: variant at most 0 | yes |

Rule 3 held. All 70 reps passed the isolation screen, and there were 0 voids in each arm. Every near-miss rep in both arms named the probe that the prompt was written for.

## Per rep

Each answer was graded by hand. Every answer is a bare skill name, so each is quoted whole.

| Arm | Prompt | Rep | Answer |
|---|---|---|---|
| control | T1-cv-ledger | 1 | `track-model-experiments` |
| control | T1-cv-ledger | 2 | `track-model-experiments` |
| control | T1-cv-ledger | 3 | `track-model-experiments` |
| control | T1-cv-ledger | 4 | `track-model-experiments` |
| control | T1-cv-ledger | 5 | `track-model-experiments` |
| control | T2-bayes-lfo | 1 | `track-model-experiments` |
| control | T2-bayes-lfo | 2 | `track-model-experiments` |
| control | T2-bayes-lfo | 3 | `track-model-experiments` |
| control | T2-bayes-lfo | 4 | `track-model-experiments` |
| control | T2-bayes-lfo | 5 | `track-model-experiments` |
| control | T3-elpd-variants | 1 | `track-model-experiments` |
| control | T3-elpd-variants | 2 | `track-model-experiments` |
| control | T3-elpd-variants | 3 | `track-model-experiments` |
| control | T3-elpd-variants | 4 | `track-model-experiments` |
| control | T3-elpd-variants | 5 | `track-model-experiments` |
| control | N-bayesian-workflow | 1 | `bayesian-workflow` |
| control | N-bayesian-workflow | 2 | `bayesian-workflow` |
| control | N-bayesian-workflow | 3 | `bayesian-workflow` |
| control | N-bayesian-workflow | 4 | `bayesian-workflow` |
| control | N-bayesian-workflow | 5 | `bayesian-workflow` |
| control | N-evaluate-deep-learning | 1 | `evaluate-deep-learning` |
| control | N-evaluate-deep-learning | 2 | `evaluate-deep-learning` |
| control | N-evaluate-deep-learning | 3 | `evaluate-deep-learning` |
| control | N-evaluate-deep-learning | 4 | `evaluate-deep-learning` |
| control | N-evaluate-deep-learning | 5 | `evaluate-deep-learning` |
| control | N-tune-hyperparameters | 1 | `tune-hyperparameters` |
| control | N-tune-hyperparameters | 2 | `tune-hyperparameters` |
| control | N-tune-hyperparameters | 3 | `tune-hyperparameters` |
| control | N-tune-hyperparameters | 4 | `tune-hyperparameters` |
| control | N-tune-hyperparameters | 5 | `tune-hyperparameters` |
| control | N-recommend-probabilistic-model | 1 | `recommend-probabilistic-model` |
| control | N-recommend-probabilistic-model | 2 | `recommend-probabilistic-model` |
| control | N-recommend-probabilistic-model | 3 | `recommend-probabilistic-model` |
| control | N-recommend-probabilistic-model | 4 | `recommend-probabilistic-model` |
| control | N-recommend-probabilistic-model | 5 | `recommend-probabilistic-model` |
| variant | T1-cv-ledger | 1 | `track-model-experiments` |
| variant | T1-cv-ledger | 2 | `track-model-experiments` |
| variant | T1-cv-ledger | 3 | `track-model-experiments` |
| variant | T1-cv-ledger | 4 | `track-model-experiments` |
| variant | T1-cv-ledger | 5 | `track-model-experiments` |
| variant | T2-bayes-lfo | 1 | `track-model-experiments` |
| variant | T2-bayes-lfo | 2 | `track-model-experiments` |
| variant | T2-bayes-lfo | 3 | `track-model-experiments` |
| variant | T2-bayes-lfo | 4 | `track-model-experiments` |
| variant | T2-bayes-lfo | 5 | `track-model-experiments` |
| variant | T3-elpd-variants | 1 | `track-model-experiments` |
| variant | T3-elpd-variants | 2 | `track-model-experiments` |
| variant | T3-elpd-variants | 3 | `track-model-experiments` |
| variant | T3-elpd-variants | 4 | `track-model-experiments` |
| variant | T3-elpd-variants | 5 | `track-model-experiments` |
| variant | N-bayesian-workflow | 1 | `bayesian-workflow` |
| variant | N-bayesian-workflow | 2 | `bayesian-workflow` |
| variant | N-bayesian-workflow | 3 | `bayesian-workflow` |
| variant | N-bayesian-workflow | 4 | `bayesian-workflow` |
| variant | N-bayesian-workflow | 5 | `bayesian-workflow` |
| variant | N-evaluate-deep-learning | 1 | `evaluate-deep-learning` |
| variant | N-evaluate-deep-learning | 2 | `evaluate-deep-learning` |
| variant | N-evaluate-deep-learning | 3 | `evaluate-deep-learning` |
| variant | N-evaluate-deep-learning | 4 | `evaluate-deep-learning` |
| variant | N-evaluate-deep-learning | 5 | `evaluate-deep-learning` |
| variant | N-tune-hyperparameters | 1 | `tune-hyperparameters` |
| variant | N-tune-hyperparameters | 2 | `tune-hyperparameters` |
| variant | N-tune-hyperparameters | 3 | `tune-hyperparameters` |
| variant | N-tune-hyperparameters | 4 | `tune-hyperparameters` |
| variant | N-tune-hyperparameters | 5 | `tune-hyperparameters` |
| variant | N-recommend-probabilistic-model | 1 | `recommend-probabilistic-model` |
| variant | N-recommend-probabilistic-model | 2 | `recommend-probabilistic-model` |
| variant | N-recommend-probabilistic-model | 3 | `recommend-probabilistic-model` |
| variant | N-recommend-probabilistic-model | 4 | `recommend-probabilistic-model` |
| variant | N-recommend-probabilistic-model | 5 | `recommend-probabilistic-model` |

## Verdict

Pass. The variant met all three rules on its first run, so no rewording was needed and the variant arm ran once.

Two facts limit what this test shows:

1. **Ceiling effect.** The control already routed 5 of 5 on every trigger prompt, T1 included, and 0 of 5 on every near-miss. So the test shows that the new description does not lose any routing and does not pull in a near-miss. It does not show that the new description routes a CV-ranked or backtest-ranked ledger better than the old one did.
2. **Probe text at plan time.** The probes used their base-commit descriptions. Two of them have changed on main since then (see the probe drift check). The test did not run against the current text of those two descriptions.
