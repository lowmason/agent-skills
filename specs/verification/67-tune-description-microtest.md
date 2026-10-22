# Plan 67 micro-test: tune-hyperparameters' description (V1, tune arm)

**Date:** 2026-10-22. **Model:** `claude-sonnet-5-5` (from each rep's init record) through `claude -p` (Claude Code 2.1.304). **Kit:** `~/.cache/agent-skills/scratch/plan67-micro/` (`run_microtest.py`, `screen_v2.py`, `system-v1-*.txt`, `results-v1-*.json`, `log-v1-*.txt`, `raw/`). **Cost:** $0.88 (pilot $0.01, control arm $0.45, variant arm $0.42).

## Design

Each rep is one decision-only `claude -p` call, run from its own new folder under `/tmp/p67micro/`. The isolation flags are `--model sonnet --tools "" --strict-mcp-config --no-session-persistence --system-prompt-file <listing>`, with `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1` set. The reply is one skill name, or `none`.

The system prompt lists six skills by name and description, in name order: creative-thinking, deep-learning, evaluate-deep-learning, recommend-probabilistic-model, track-model-experiments and tune-hyperparameters. The five probes are the skills next to tune that a prompt could also route to. Their descriptions come from the base commit `7a8fbaa` in both arms. The two listings differ only in the tune-hyperparameters line.

- **Control arm:** tune's description at the base commit. That text is also the description at the start of this task (`c53647b`), because Tasks 1 to 4 changed only tune's body.
- **Variant arm:** the draft description in the working tree (860 characters). It names any producer (sklearn and boosting models, statsmodels, NumPyro and dynamax fits, neural nets from deep-learning), the splitter choice for grouped, spatial, or independent rows, structural choices, early stopping, pruning and the trial budget. It drops "for a nowcasting/tabular model" and "dynamax optax SGD".

Each arm runs the eight prompts below, 5 reps each, so 40 reps per arm.

**Isolation check.** A pilot rep (the control listing, prompt `T1-grouped-cv`) ran first on the day of the test. Its init record showed `"tools": []`, `"mcp_servers": []` and the model `claude-sonnet-5-5`, so the kit's `clean` flag was True. The `usage.iterations` list was empty on every rep, so the kit's iteration clause passes without proof. A positive screen was used instead (`screen_v2.py`, which applies the same screen to V1 results). For each rep, the result event must show only `claude-sonnet-5-5` in `modelUsage`, `num_turns` of 1 and zero server tool use. An advisor call would add a second model to `modelUsage`.

Some context still reaches every rep in both arms. Three user-level SessionStart hooks run, and the init record shows the "Explanatory" output style. The user's global `CLAUDE.md` and rules also load. The init record lists the user's skills, but with no tools the agent cannot load one. This context is the same in both arms. So it does not change the contrast between the arms.

**Probe drift check.** The five probe descriptions at HEAD (`c53647b`) still equal those at the base commit:

```
creative-thinking same
deep-learning same
evaluate-deep-learning same
recommend-probabilistic-model same
track-model-experiments same
```

So the base-commit probe text that the kit uses is also the current probe text on this branch.

**Pass rule** (spec V1, fixed before the runs):

1. On each trigger prompt (`T1`–`T3`), the variant's count of answers that route to `tune-hyperparameters` is at least the control's count minus 1.
2. On each near-miss prompt (`N-…`), the variant's count that routes to `tune-hyperparameters` is at most the control's count: no near-miss newly routes to the target.
3. Every rep is clean (`tools` and `mcp` empty, only `message` iterations). A rep that is not clean is void: rerun it and count it.

## Prompts

- **T1-grouped-cv:** "I'm tuning a LightGBM model that predicts weekly sales for stores we have not opened yet. Rows from the same store are correlated. I want to search the learning rate, num_leaves and min_child_samples with Optuna without an optimistic CV score. How should I set up the search?"
- **T2-mixture-k:** "I've settled on a Gaussian mixture for county wage-growth profiles. Now I need to pick the number of components, somewhere between 2 and 8, without overfitting. How do I run that sweep?"
- **T3-neural-budget:** "I'm searching the learning rate and dropout of a small Flax MLP nowcaster. Each trial trains for up to 200 epochs, and I can afford about 60 trials. How do I set the trial budget, prune bad trials early, and use early stopping without leaking the validation fold?"
- **N-creative-thinking:** "There is something interesting in this county employment panel, but I can't say what I should even be estimating. Help me work out what the target of the analysis should be."
- **N-recommend-probabilistic-model:** "I have monthly counts of business births by county. They are overdispersed and a third are zero. Which kind of model should I fit?"
- **N-deep-learning:** "My Flax NNX training loss goes NaN after about 2,000 steps with a cosine schedule and warmup. How do I find the cause and resume training from the last good checkpoint?"
- **N-evaluate-deep-learning:** "I trained three transformer checkpoints for demand forecasting with different random seeds. I want to compare them on a held-out test period and decide which checkpoint to ship."
- **N-track-model-experiments:** "I've fit five variants for a county-level employment panel: two ridge regressions and three gradient-boosting models, each scored with the same 5-fold GroupKFold MSE. I keep forgetting which feature set each one used. I want one record of the variants, ranked on those fold scores."

## Results

Routed count is the number of the 5 answers that name `tune-hyperparameters`.

| Prompt | Kind | Control | Variant | Rule | Held |
|---|---|---|---|---|---|
| T1-grouped-cv | trigger | 5/5 | 5/5 | 1: variant at least 4 | yes |
| T2-mixture-k | trigger | 5/5 | 5/5 | 1: variant at least 4 | yes |
| T3-neural-budget | trigger | 5/5 | 5/5 | 1: variant at least 4 | yes |
| N-creative-thinking | near-miss | 0/5 | 0/5 | 2: variant at most 0 | yes |
| N-recommend-probabilistic-model | near-miss | 0/5 | 0/5 | 2: variant at most 0 | yes |
| N-deep-learning | near-miss | 0/5 | 0/5 | 2: variant at most 0 | yes |
| N-evaluate-deep-learning | near-miss | 0/5 | 0/5 | 2: variant at most 0 | yes |
| N-track-model-experiments | near-miss | 0/5 | 0/5 | 2: variant at most 0 | yes |

Rule 3 held. All 80 reps passed the isolation screen, and there were 0 voids in each arm. Every near-miss rep in both arms named the probe that the prompt was written for.

## Per rep

Each answer was graded by hand. Every answer is a bare skill name, so each is quoted whole.

| Arm | Prompt | Rep | Answer |
|---|---|---|---|
| control | T1-grouped-cv | 1 | `tune-hyperparameters` |
| control | T1-grouped-cv | 2 | `tune-hyperparameters` |
| control | T1-grouped-cv | 3 | `tune-hyperparameters` |
| control | T1-grouped-cv | 4 | `tune-hyperparameters` |
| control | T1-grouped-cv | 5 | `tune-hyperparameters` |
| control | T2-mixture-k | 1 | `tune-hyperparameters` |
| control | T2-mixture-k | 2 | `tune-hyperparameters` |
| control | T2-mixture-k | 3 | `tune-hyperparameters` |
| control | T2-mixture-k | 4 | `tune-hyperparameters` |
| control | T2-mixture-k | 5 | `tune-hyperparameters` |
| control | T3-neural-budget | 1 | `tune-hyperparameters` |
| control | T3-neural-budget | 2 | `tune-hyperparameters` |
| control | T3-neural-budget | 3 | `tune-hyperparameters` |
| control | T3-neural-budget | 4 | `tune-hyperparameters` |
| control | T3-neural-budget | 5 | `tune-hyperparameters` |
| control | N-creative-thinking | 1 | `creative-thinking` |
| control | N-creative-thinking | 2 | `creative-thinking` |
| control | N-creative-thinking | 3 | `creative-thinking` |
| control | N-creative-thinking | 4 | `creative-thinking` |
| control | N-creative-thinking | 5 | `creative-thinking` |
| control | N-recommend-probabilistic-model | 1 | `recommend-probabilistic-model` |
| control | N-recommend-probabilistic-model | 2 | `recommend-probabilistic-model` |
| control | N-recommend-probabilistic-model | 3 | `recommend-probabilistic-model` |
| control | N-recommend-probabilistic-model | 4 | `recommend-probabilistic-model` |
| control | N-recommend-probabilistic-model | 5 | `recommend-probabilistic-model` |
| control | N-deep-learning | 1 | `deep-learning` |
| control | N-deep-learning | 2 | `deep-learning` |
| control | N-deep-learning | 3 | `deep-learning` |
| control | N-deep-learning | 4 | `deep-learning` |
| control | N-deep-learning | 5 | `deep-learning` |
| control | N-evaluate-deep-learning | 1 | `evaluate-deep-learning` |
| control | N-evaluate-deep-learning | 2 | `evaluate-deep-learning` |
| control | N-evaluate-deep-learning | 3 | `evaluate-deep-learning` |
| control | N-evaluate-deep-learning | 4 | `evaluate-deep-learning` |
| control | N-evaluate-deep-learning | 5 | `evaluate-deep-learning` |
| control | N-track-model-experiments | 1 | `track-model-experiments` |
| control | N-track-model-experiments | 2 | `track-model-experiments` |
| control | N-track-model-experiments | 3 | `track-model-experiments` |
| control | N-track-model-experiments | 4 | `track-model-experiments` |
| control | N-track-model-experiments | 5 | `track-model-experiments` |
| variant | T1-grouped-cv | 1 | `tune-hyperparameters` |
| variant | T1-grouped-cv | 2 | `tune-hyperparameters` |
| variant | T1-grouped-cv | 3 | `tune-hyperparameters` |
| variant | T1-grouped-cv | 4 | `tune-hyperparameters` |
| variant | T1-grouped-cv | 5 | `tune-hyperparameters` |
| variant | T2-mixture-k | 1 | `tune-hyperparameters` |
| variant | T2-mixture-k | 2 | `tune-hyperparameters` |
| variant | T2-mixture-k | 3 | `tune-hyperparameters` |
| variant | T2-mixture-k | 4 | `tune-hyperparameters` |
| variant | T2-mixture-k | 5 | `tune-hyperparameters` |
| variant | T3-neural-budget | 1 | `tune-hyperparameters` |
| variant | T3-neural-budget | 2 | `tune-hyperparameters` |
| variant | T3-neural-budget | 3 | `tune-hyperparameters` |
| variant | T3-neural-budget | 4 | `tune-hyperparameters` |
| variant | T3-neural-budget | 5 | `tune-hyperparameters` |
| variant | N-creative-thinking | 1 | `creative-thinking` |
| variant | N-creative-thinking | 2 | `creative-thinking` |
| variant | N-creative-thinking | 3 | `creative-thinking` |
| variant | N-creative-thinking | 4 | `creative-thinking` |
| variant | N-creative-thinking | 5 | `creative-thinking` |
| variant | N-recommend-probabilistic-model | 1 | `recommend-probabilistic-model` |
| variant | N-recommend-probabilistic-model | 2 | `recommend-probabilistic-model` |
| variant | N-recommend-probabilistic-model | 3 | `recommend-probabilistic-model` |
| variant | N-recommend-probabilistic-model | 4 | `recommend-probabilistic-model` |
| variant | N-recommend-probabilistic-model | 5 | `recommend-probabilistic-model` |
| variant | N-deep-learning | 1 | `deep-learning` |
| variant | N-deep-learning | 2 | `deep-learning` |
| variant | N-deep-learning | 3 | `deep-learning` |
| variant | N-deep-learning | 4 | `deep-learning` |
| variant | N-deep-learning | 5 | `deep-learning` |
| variant | N-evaluate-deep-learning | 1 | `evaluate-deep-learning` |
| variant | N-evaluate-deep-learning | 2 | `evaluate-deep-learning` |
| variant | N-evaluate-deep-learning | 3 | `evaluate-deep-learning` |
| variant | N-evaluate-deep-learning | 4 | `evaluate-deep-learning` |
| variant | N-evaluate-deep-learning | 5 | `evaluate-deep-learning` |
| variant | N-track-model-experiments | 1 | `track-model-experiments` |
| variant | N-track-model-experiments | 2 | `track-model-experiments` |
| variant | N-track-model-experiments | 3 | `track-model-experiments` |
| variant | N-track-model-experiments | 4 | `track-model-experiments` |
| variant | N-track-model-experiments | 5 | `track-model-experiments` |

## Verdict

Pass. The variant met all three rules on its first run, so no rewording was needed and the variant arm ran once.

One fact limits what this test shows. **Ceiling effect.** The control already routed 5 of 5 on every trigger prompt and 0 of 5 on every near-miss. That includes `T2-mixture-k` and `T3-neural-budget`, which name a structural choice and a neural trial budget that the base description does not list. So the test shows that the new description loses no routing and pulls in no near-miss. It does not show that the new description routes structural or neural tuning better than the old one did.
