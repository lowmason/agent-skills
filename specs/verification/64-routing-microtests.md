# Plan 64 micro-test M1: bayesian-workflow's description and scope

**Date:** 2026-10-21. **Model:** `claude-sonnet-5-5` through `claude -p` (Claude Code 2.1.304). **Kit:** `~/.cache/agent-skills/scratch/plan64-micro/` (`run_arm.py`, `grade.py`, `M1.json`, raw answers under `raw/M1/`). **Cost:** $2.24 of the $25 cap (pilot $0.04, arm B $0.73, candidate C1 $0.74, candidate C2 $0.73).

The owner answered Q1 with option (a) (decision D3): "Pyro" is dropped from bayesian-workflow's description, and "uncertainty quantification" becomes "posterior uncertainty". That edit is candidate C1. C1 missed pass bar 1 on B1 (2 of 5 fails). The owner then approved a reword: candidate C2 keeps C1 and adds the sentence "NumPyro only; Pyro/PyTorch fits go elsewhere." to the description. Only arm C was rerun. The bars did not change.

## Design

Each rep is one decision-only call with no tools (`claude -p --model sonnet --tools "" --strict-mcp-config`, with `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`), run from its own new folder under `/tmp/p64micro/`. The prompt lists the descriptions of 10 competing skills and asks for one `SKILL:` line and one `REASON:` line. Arm B uses every description as it stood at commit `1aa0f9f` (the start of Task 3). Arms C1 and C2 differ from arm B only in bayesian-workflow's description. C1 is the description after the Pyro edit. C2 is C1 plus the scope sentence. Description length: 766 characters at `1aa0f9f`, 755 for C1, 801 for C2. Five reps per arm and scenario.

The pilot (one rep, stream-json) printed `tools: []` and `mcp_servers: []` before any arm ran.

A "void" is a rep that errored or refused. There were 0 voids. The same edit also added a "Scope and sibling skills" block to SKILL.md. The routing prompt uses only the description, so the block does not enter the test.

## Scenarios, grading rules and pass bars

Fixed in `M1.json` before any run. A collision probe with a `fail` list fails a rep only when its SKILL is in that list. Any other pick passes. A scenario with a `pass` list passes a rep whose SKILL is in the list.

- **B1, Pyro SVI plateau** (fail if bayesian-workflow): "I have a Pyro model in PyTorch with an AutoNormal guide. The SVI loss plateaus after 2,000 steps. How do I fix the training?"
- **B2, Flax deep ensemble** (fail if bayesian-workflow): "My Flax MLP forecasts weekly demand. I need uncertainty quantification from a deep ensemble of 5 networks. Where do I start?"
- **B3, NumPyro divergences** (pass if bayesian-workflow): "My NumPyro hierarchical model gives 40 divergences out of 4,000 draws. What do I check first?"
- **B4, NUTS credible intervals** (pass if bayesian-workflow): "I fitted a NumPyro logistic regression with NUTS and need credible intervals for a report to managers."

Pass bars. An arm C candidate meets the bar when both hold:
1. On every scenario it fails at most 1 of 5 reps.
2. On every scenario where arm B fails 2 or more of 5, it fails fewer than arm B.

## Results

| Scenario | B fails | C1 fails | C2 fails | C1 bars met | C2 bars met |
|---|---|---|---|---|---|
| B1 | 5/5 | 2/5 | 0/5 | no (bar 1) | yes |
| B2 | 0/5 | 0/5 | 0/5 | yes | yes |
| B3 | 0/5 | 0/5 | 0/5 | yes | yes |
| B4 | 0/5 | 0/5 | 0/5 | yes | yes |

C1 fails bar 1 on B1 (2 of 5, limit 1). Bar 2 holds for C1 (2 is fewer than 5). C2 meets both bars on every scenario.

Reading the B1 reps by hand. Arm B: all 5 picked bayesian-workflow because the description named Pyro and SVI. C1: B1-2 and B1-3 still picked bayesian-workflow and said it was the closest match although it targets NumPyro. B1-4 and B1-5 picked tune-hyperparameters, and B1-1 picked none. C2: all 5 reps picked none, and each reply cites the new scope sentence or says the skills cover only NumPyro and JAX. No B2 to B4 rep changed its pick between arms.

## Per-rep results

Quote: the first 15 words of each REASON line. The last column is the isolation screen.

| Arm | Scenario | Rep | Verdict | Skill | Quote | Screen |
|---|---|---|---|---|---|---|
| B | B1 | 1 | FAIL | bayesian-workflow | "This is a Bayesian inference problem (Pyro SVI with an AutoNormal guide and a plateauing" | ok |
| B | B1 | 2 | FAIL | bayesian-workflow | "A plateauing SVI loss with an AutoNormal guide in Pyro is a Bayesian inference diagnosis" | ok |
| B | B1 | 3 | FAIL | bayesian-workflow | "A plateauing SVI loss with an AutoNormal guide is a Bayesian inference convergence diagnosis, and" | ok |
| B | B1 | 4 | FAIL | bayesian-workflow | "A plateauing SVI loss with an AutoNormal guide is an inference-convergence diagnosis problem for a" | ok |
| B | B1 | 5 | FAIL | bayesian-workflow | "A plateaued SVI loss with an AutoNormal guide is a Pyro inference-diagnostics problem, and this" | ok |
| B | B2 | 1 | PASS | deep-learning | "The user has already chosen a deep ensemble of 5 Flax MLPs, so the work" | ok |
| B | B2 | 2 | PASS | deep-learning | "The request is to design and train a Flax MLP deep ensemble of 5 networks" | ok |
| B | B2 | 3 | PASS | deep-learning | "Building and training a Flax MLP deep ensemble of 5 networks is neural model design" | ok |
| B | B2 | 4 | PASS | deep-learning | "The user must design and train five Flax MLPs as a deep ensemble, which is" | ok |
| B | B2 | 5 | PASS | deep-learning | "Building and training a deep ensemble of five Flax MLPs, including the loss and member" | ok |
| B | B3 | 1 | PASS | bayesian-workflow | "Diagnosing divergences in a NumPyro hierarchical model is a convergence-diagnostics task, which this skill covers" | ok |
| B | B3 | 2 | PASS | bayesian-workflow | "Diagnosing divergences in a NumPyro hierarchical model is a convergence-diagnostics task that this skill covers," | ok |
| B | B3 | 3 | PASS | bayesian-workflow | "Diagnosing divergences in a NumPyro hierarchical model is a convergence-diagnostics task that this skill covers," | ok |
| B | B3 | 4 | PASS | bayesian-workflow | "Divergences in a NumPyro hierarchical model are a convergence-diagnostics problem, and this skill covers NUTS" | ok |
| B | B3 | 5 | PASS | bayesian-workflow | "The request asks how to diagnose divergences in a fitted NumPyro hierarchical model, which is" | ok |
| B | B4 | 1 | PASS | bayesian-workflow | "The task covers credible intervals from a NumPyro NUTS logistic regression and presenting Bayesian results" | ok |
| B | B4 | 2 | PASS | bayesian-workflow | "The user has a fitted NumPyro NUTS model and needs credible intervals presented to non-technical" | ok |
| B | B4 | 3 | PASS | bayesian-workflow | "The request covers a fitted NumPyro logistic regression with NUTS, credible intervals, and reporting results" | ok |
| B | B4 | 4 | PASS | bayesian-workflow | "The model is already fitted with NumPyro and NUTS, and the skill covers computing credible" | ok |
| B | B4 | 5 | PASS | bayesian-workflow | "The task covers NumPyro NUTS results, credible intervals, and presenting Bayesian results to non-technical managers," | ok |
| C1 | B1 | 1 | PASS | none | "The request is about Pyro on PyTorch, but the Bayesian, SVI-tuning and deep-learning skills here" | ok |
| C1 | B1 | 2 | FAIL | bayesian-workflow | "It covers fitting and diagnosing probabilistic models, including SVI and AutoNormal problems, but its examples" | ok |
| C1 | B1 | 3 | FAIL | bayesian-workflow | "A plateaued SVI loss with an AutoNormal guide is an inference-diagnosis problem (guide family, ELBO" | ok |
| C1 | B1 | 4 | PASS | tune-hyperparameters | "A plateaued SVI loss is an inference-knob problem (learning rate and step count), which this" | ok |
| C1 | B1 | 5 | PASS | tune-hyperparameters | "A plateaued SVI loss is most likely an inference-knob problem (learning rate, step count), which" | ok |
| C1 | B2 | 1 | PASS | deep-learning | "The user has already chosen a Flax MLP deep ensemble, so the task is to" | ok |
| C1 | B2 | 2 | PASS | deep-learning | "Building and training a 5-member Flax MLP ensemble with a probabilistic output head for weekly" | ok |
| C1 | B2 | 3 | PASS | deep-learning | "The user is building and training an ensemble of Flax MLPs, including the loss and" | ok |
| C1 | B2 | 4 | PASS | deep-learning | "The request is to design and train an ensemble of five Flax MLPs, which is" | ok |
| C1 | B2 | 5 | PASS | deep-learning | "The user needs to design and train a Flax MLP deep ensemble of 5 networks," | ok |
| C1 | B3 | 1 | PASS | bayesian-workflow | "Diagnosing divergences in a NumPyro hierarchical model is a convergence-diagnostics task, which this skill covers" | ok |
| C1 | B3 | 2 | PASS | bayesian-workflow | "Diagnosing divergences in a NumPyro NUTS hierarchical model is a convergence-diagnostics task that this skill" | ok |
| C1 | B3 | 3 | PASS | bayesian-workflow | "The request asks how to diagnose NUTS divergences in a NumPyro hierarchical model, which this" | ok |
| C1 | B3 | 4 | PASS | bayesian-workflow | "Diagnosing NUTS divergences in a NumPyro hierarchical model is a core convergence-diagnostics task that this" | ok |
| C1 | B3 | 5 | PASS | bayesian-workflow | "The question is about NUTS divergences in a NumPyro hierarchical model, which this skill covers" | ok |
| C1 | B4 | 1 | PASS | bayesian-workflow | "The model is already fitted with NumPyro and NUTS, and the task is to report" | ok |
| C1 | B4 | 2 | PASS | bayesian-workflow | "The task is to compute and present credible intervals from a fitted NumPyro NUTS logistic" | ok |
| C1 | B4 | 3 | PASS | bayesian-workflow | "The task covers NumPyro NUTS output, credible intervals (HDI), and presenting Bayesian results to non-technical" | ok |
| C1 | B4 | 4 | PASS | bayesian-workflow | "The model is already fitted in NumPyro with NUTS, and the task is to report" | ok |
| C1 | B4 | 5 | PASS | bayesian-workflow | "The model is already fitted in NumPyro, and the task is to report credible intervals" | ok |
| C2 | B1 | 1 | PASS | none | "This is a Pyro/PyTorch SVI problem, and bayesian-workflow explicitly excludes Pyro/PyTorch fits while the other" | ok |
| C2 | B1 | 2 | PASS | none | "The bayesian-workflow skill covers NumPyro only and says Pyro/PyTorch fits go elsewhere, and deep-learning covers" | ok |
| C2 | B1 | 3 | PASS | none | "bayesian-workflow covers NumPyro only and explicitly excludes Pyro/PyTorch fits, and deep-learning covers JAX, Flax NNX," | ok |
| C2 | B1 | 4 | PASS | none | "The model is Pyro on PyTorch, and bayesian-workflow, deep-learning, and optimize-jax all cover only NumPyro" | ok |
| C2 | B1 | 5 | PASS | none | "The skills cover NumPyro/JAX, so Pyro/PyTorch SVI training is out of scope, and bayesian-workflow explicitly" | ok |
| C2 | B2 | 1 | PASS | deep-learning | "You are designing and training a Flax MLP deep ensemble, which is neural model implementation" | ok |
| C2 | B2 | 2 | PASS | deep-learning | "The request is about building and training a Flax MLP deep ensemble of 5 networks," | ok |
| C2 | B2 | 3 | PASS | deep-learning | "The user is designing and training a Flax MLP with a deep ensemble of 5" | ok |
| C2 | B2 | 4 | PASS | deep-learning | "The request is to design and train an ensemble of five Flax MLPs, which is" | ok |
| C2 | B2 | 5 | PASS | deep-learning | "The user needs to design and train a Flax MLP deep ensemble (5 members, with" | ok |
| C2 | B3 | 1 | PASS | bayesian-workflow | "Diagnosing divergences in a NumPyro hierarchical model is core Bayesian-workflow work, such as checking for" | ok |
| C2 | B3 | 2 | PASS | bayesian-workflow | "Diagnosing divergences in a NumPyro hierarchical model is a convergence-diagnostics task that this skill covers" | ok |
| C2 | B3 | 3 | PASS | bayesian-workflow | "Diagnosing divergences in a NumPyro hierarchical model is a convergence-diagnostics task that this skill covers," | ok |
| C2 | B3 | 4 | PASS | bayesian-workflow | "Diagnosing divergences in a NumPyro NUTS hierarchical model is a convergence-diagnostics task that this skill" | ok |
| C2 | B3 | 5 | PASS | bayesian-workflow | "Diagnosing divergences in a NumPyro hierarchical model is a core bayesian-workflow task, and that skill" | ok |
| C2 | B4 | 1 | PASS | bayesian-workflow | "The task is reporting credible intervals from a fitted NumPyro NUTS model to non-technical managers," | ok |
| C2 | B4 | 2 | PASS | bayesian-workflow | "The task covers credible intervals from a NumPyro NUTS fit and how to present them" | ok |
| C2 | B4 | 3 | PASS | bayesian-workflow | "The request covers a fitted NumPyro NUTS model and credible intervals, and the skill also" | ok |
| C2 | B4 | 4 | PASS | bayesian-workflow | "The model is already fitted in NumPyro with NUTS, and the task is to compute" | ok |
| C2 | B4 | 5 | PASS | bayesian-workflow | "The model is a NumPyro logistic regression fitted with NUTS, and the task is to" | ok |

## Isolation screen

`grade.py` screened every saved answer. All 60 answers took one turn, ended without error, hold only `message` iterations (no tool or advisor call) and came from one model. The screen column reads `ok` for every rep. No rep was voided, and no FAIL rep was ambiguous after reading the full reply.

---

# Plan 64 micro-test M2: recommend-probabilistic-model's description and routing

**Date:** 2026-10-21. **Model:** `claude-sonnet-5-5` through `claude -p` (Claude Code 2.1.304). **Kit:** `~/.cache/agent-skills/scratch/plan64-micro/` (`run_arm.py`, `grade.py`, `M2.json`, raw answers under `raw/M2/`). **Cost:** $2.20 of the $25 cap for M2 (pilot $0.04, arm B $1.08, arm C $1.08). With M1 ($2.24) the plan has spent $4.44.

The edit under test is Task 5's description change: the phrase "ordinal, proportion, quantile and censored or time-to-event outcomes" after "Covers regression / GLMs / counts," and the closing sentence "A causal-effect question goes to recommend-causal-design first." It carries Task 4's class names. Description length: 871 characters at `97a8525`, 1,005 after the edit. The same commit adds sibling pointers, a Step 1 sentence, a memo line and neural hand-offs. The routing prompt uses only the description, so those do not enter the test.

## Design

Each rep is one decision-only call with no tools (`claude -p --model sonnet --tools "" --strict-mcp-config`, with `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`), run from its own new folder under `/tmp/p64micro/`. The prompt lists the descriptions of 10 competing skills and asks for one `SKILL:` line and one `REASON:` line. Arm B uses every description as it stood at commit `97a8525` (read with `--base 97a8525`, so edits to the working tree could not touch it). Arm C differs only in recommend-probabilistic-model's description, read from the working tree. Five reps per arm and scenario. The `run_arm.py` and `grade.py` files match Appendix A byte for byte.

The pilot (one rep, stream-json) printed `tools: []` and `mcp_servers: []` before any arm ran. A "void" is a rep that errored or refused. There were 0 voids.

## Scenarios, grading rules and pass bars

Fixed in `M2.json` before any run. Each scenario has a `pass` list, and a rep passes when its SKILL is in the list.

- **R1, minimum-wage causal question** (pass: recommend-causal-design): "Did the 2024 minimum-wage increase cause job losses in these counties? Which model should I fit?"
- **R2, censored churn times** (pass: recommend-probabilistic-model): "Customer churn: I have each customer's time to cancellation, but 60% are still active. Which model family fits?"
- **R3, ordinal rating** (pass: recommend-probabilistic-model): "My outcome is a 1-5 satisfaction rating with a dozen predictors. Which model should I use?"
- **R4, graph neural network training** (pass: deep-learning): "I want to train a graph neural network in Flax on molecule graphs. How should I set up training?"
- **R5, overdispersed counts** (pass: recommend-probabilistic-model): "My counts have variance 8 times the mean. Poisson or negative binomial?"
- **R6, bounded share** (pass: recommend-probabilistic-model): "My outcome is each county's share of workers in manufacturing, between 0 and 1. Which model fits?"

Pass bars. Arm C meets the bar when both hold:
1. On every scenario it fails at most 1 of 5 reps.
2. On every scenario where arm B fails 2 or more of 5, it fails fewer than arm B.

## Results

| Scenario | B fails | C fails | C bars met |
|---|---|---|---|
| R1 | 0/5 | 0/5 | yes |
| R2 | 0/5 | 0/5 | yes |
| R3 | 0/5 | 0/5 | yes |
| R4 | 0/5 | 0/5 | yes |
| R5 | 0/5 | 0/5 | yes |
| R6 | 0/5 | 0/5 | yes |

Arm C meets both bars on every scenario. Bar 2 does not apply, since arm B failed no scenario. The test therefore shows that the edit does not harm routing. It does not show a gain, because arm B already routed all six requests correctly. Reading the replies by hand: in both arms R1 went to recommend-causal-design on the "did X cause Y" wording, R2, R3 and R6 went to recommend-probabilistic-model on model-family wording (arm C replies name "censored time-to-event" and "bounded proportion" outcomes), and R4 went to deep-learning on "design and train a neural model" wording.

## Per-rep results

Quote: the first 15 words of each REASON line. The last column is the isolation screen.

| Arm | Scenario | Rep | Verdict | Skill | Quote | Screen |
|---|---|---|---|---|---|---|
| B | R1 | 1 | PASS | recommend-causal-design | "The question asks whether a policy caused an outcome, so you must pick an identification" | ok |
| B | R1 | 2 | PASS | recommend-causal-design | "The question asks whether a policy caused an outcome, so the research design (such as" | ok |
| B | R1 | 3 | PASS | recommend-causal-design | "The question asks whether the increase caused job losses, so you must first choose an" | ok |
| B | R1 | 4 | PASS | recommend-causal-design | "The question "did the minimum-wage increase cause job losses" is about identifying a causal effect," | ok |
| B | R1 | 5 | PASS | recommend-causal-design | "This is a "did X cause Y" policy-impact question, so the identification design (such as" | ok |
| B | R2 | 1 | PASS | recommend-probabilistic-model | "The request is to choose a model family before fitting, and the right-censored time-to-cancellation data" | ok |
| B | R2 | 2 | PASS | recommend-probabilistic-model | "The user needs to choose a model family for time-to-event data with 60% censoring, which" | ok |
| B | R2 | 3 | PASS | recommend-probabilistic-model | "The user asks which model family fits right-censored time-to-cancellation data, which is a model-selection question" | ok |
| B | R2 | 4 | PASS | recommend-probabilistic-model | "The user needs to choose a model family for right-censored time-to-cancellation data before fitting, which" | ok |
| B | R2 | 5 | PASS | recommend-probabilistic-model | "The user asks which model family fits censored time-to-event data (60% still active) before fitting," | ok |
| B | R3 | 1 | PASS | recommend-probabilistic-model | "The user asks which model fits an ordinal 1-5 outcome with about twelve predictors, which" | ok |
| B | R3 | 2 | PASS | recommend-probabilistic-model | "You ask which model fits an ordinal 1-5 outcome with a dozen predictors, and this" | ok |
| B | R3 | 3 | PASS | recommend-probabilistic-model | "The user asks which model fits an ordinal 1-5 outcome with about a dozen predictors," | ok |
| B | R3 | 4 | PASS | recommend-probabilistic-model | "You are choosing a model for an ordinal 1-5 outcome with several predictors before fitting," | ok |
| B | R3 | 5 | PASS | recommend-probabilistic-model | "The user wants to choose a model family for an ordinal 1-5 outcome before fitting," | ok |
| B | R4 | 1 | PASS | deep-learning | "The request is about designing and training a neural model (a graph neural network) in" | ok |
| B | R4 | 2 | PASS | deep-learning | "Setting up training for a graph neural network in Flax on molecule graphs is designing" | ok |
| B | R4 | 3 | PASS | deep-learning | "Designing and training a graph neural network in Flax on molecule graphs is a neural" | ok |
| B | R4 | 4 | PASS | deep-learning | "Setting up training for a graph neural network in Flax on molecule graphs is neural" | ok |
| B | R4 | 5 | PASS | deep-learning | "Designing and training a graph neural network in Flax (geometric/scientific model on molecule graphs) is" | ok |
| B | R5 | 1 | PASS | recommend-probabilistic-model | "The user is choosing between Poisson and negative binomial for overdispersed counts, which is a" | ok |
| B | R5 | 2 | PASS | recommend-probabilistic-model | "The user is choosing between Poisson and negative binomial for overdispersed counts before fitting, which" | ok |
| B | R5 | 3 | PASS | recommend-probabilistic-model | "This is a model-selection question about overdispersed counts (Poisson vs negative binomial) before any fitting," | ok |
| B | R5 | 4 | PASS | recommend-probabilistic-model | "Choosing between Poisson and negative binomial for overdispersed counts is a model-selection question to settle" | ok |
| B | R5 | 5 | PASS | recommend-probabilistic-model | "The user is choosing between Poisson and negative binomial for overdispersed counts before fitting, which" | ok |
| B | R6 | 1 | PASS | recommend-probabilistic-model | "The user asks which model fits a bounded 0-to-1 share outcome, which is a model-selection" | ok |
| B | R6 | 2 | PASS | recommend-probabilistic-model | "The question asks which model fits a bounded 0-to-1 share outcome, which is model selection" | ok |
| B | R6 | 3 | PASS | recommend-probabilistic-model | "The question asks which model fits a bounded 0-to-1 share outcome (for example beta, fractional" | ok |
| B | R6 | 4 | PASS | recommend-probabilistic-model | "The user asks which model fits a bounded 0-to-1 share outcome, which is model selection" | ok |
| B | R6 | 5 | PASS | recommend-probabilistic-model | "The user needs to pick a model for a bounded 0-to-1 share outcome (such as" | ok |
| C | R1 | 1 | PASS | recommend-causal-design | "The question asks whether a policy caused job losses, so a causal research design (such" | ok |
| C | R1 | 2 | PASS | recommend-causal-design | ""Did the increase cause job losses" is a causal-effect question, so pick an identification design" | ok |
| C | R1 | 3 | PASS | recommend-causal-design | "This is a causal question ("did X cause Y"), so the research design must be" | ok |
| C | R1 | 4 | PASS | recommend-causal-design | "The question asks whether a minimum-wage increase caused job losses, which is a causal-effect question," | ok |
| C | R1 | 5 | PASS | recommend-causal-design | "This is a causal question ("did the increase cause job losses"), so you must pick" | ok |
| C | R2 | 1 | PASS | recommend-probabilistic-model | "The user needs to choose a model family for a censored time-to-event outcome (60% still" | ok |
| C | R2 | 2 | PASS | recommend-probabilistic-model | "The user is choosing a model family for right-censored time-to-cancellation data (60% still active), which" | ok |
| C | R2 | 3 | PASS | recommend-probabilistic-model | "The user asks which model family fits censored time-to-event data (60% still active), which is" | ok |
| C | R2 | 4 | PASS | recommend-probabilistic-model | "The user is choosing a model family for a right-censored time-to-event outcome (60% still active)" | ok |
| C | R2 | 5 | PASS | recommend-probabilistic-model | "The question asks which model family fits right-censored time-to-cancellation data (60% still active) before any" | ok |
| C | R3 | 1 | PASS | recommend-probabilistic-model | "The user wants to pick a modeling approach for an ordinal 1-5 outcome before fitting," | ok |
| C | R3 | 2 | PASS | recommend-probabilistic-model | "The user wants to choose a model for a 1-5 ordinal outcome before fitting, which" | ok |
| C | R3 | 3 | PASS | recommend-probabilistic-model | "The user needs a model choice for an ordinal 1-5 outcome before any fitting, which" | ok |
| C | R3 | 4 | PASS | recommend-probabilistic-model | "The user is choosing a modeling approach for an ordinal 1-5 outcome with about a" | ok |
| C | R3 | 5 | PASS | recommend-probabilistic-model | "The user is choosing a model for an ordinal 1-5 outcome with about a dozen" | ok |
| C | R4 | 1 | PASS | deep-learning | "The request is to design and train a graph neural network (a geometric neural model)" | ok |
| C | R4 | 2 | PASS | deep-learning | "Setting up training for a graph neural network in Flax (molecule graphs, masking, losses, optimizers)" | ok |
| C | R4 | 3 | PASS | deep-learning | "Training a graph neural network in Flax (NNX) on molecule graphs is neural model design" | ok |
| C | R4 | 4 | PASS | deep-learning | "The request is to design and set up training for a graph neural network (a" | ok |
| C | R4 | 5 | PASS | deep-learning | "Designing and setting up training for a graph neural network on molecule graphs in Flax" | ok |
| C | R5 | 1 | PASS | recommend-probabilistic-model | "Choosing between Poisson and negative binomial for overdispersed counts is a model-selection question to settle" | ok |
| C | R5 | 2 | PASS | recommend-probabilistic-model | "Choosing between Poisson and negative binomial for overdispersed counts is a model-selection question to settle" | ok |
| C | R5 | 3 | PASS | recommend-probabilistic-model | "Choosing between Poisson and negative binomial for overdispersed counts is a model-selection question to settle" | ok |
| C | R5 | 4 | PASS | recommend-probabilistic-model | "Choosing between Poisson and negative binomial for overdispersed counts (variance 8x the mean) is a" | ok |
| C | R5 | 5 | PASS | recommend-probabilistic-model | "The question is which count model fits overdispersed data (variance 8 times the mean), which" | ok |
| C | R6 | 1 | PASS | recommend-probabilistic-model | "The user asks which model fits a bounded proportion outcome (county manufacturing share) before any" | ok |
| C | R6 | 2 | PASS | recommend-probabilistic-model | "The user is asking which model fits a bounded proportion outcome, which is model selection" | ok |
| C | R6 | 3 | PASS | recommend-probabilistic-model | "The user is choosing a model family for a bounded 0-to-1 proportion outcome (county manufacturing" | ok |
| C | R6 | 4 | PASS | recommend-probabilistic-model | "The user is choosing a model family for a proportion outcome (county manufacturing share between" | ok |
| C | R6 | 5 | PASS | recommend-probabilistic-model | "The user is choosing a model for a bounded proportion outcome before any fitting, which" | ok |

## Isolation screen

`grade.py` screened every saved answer. All 60 answers took one turn, ended without error, hold only `message` iterations (no tool or advisor call) and came from one model. The screen column reads `ok` for every rep. No rep was voided, and no FAIL rep exists to review.
