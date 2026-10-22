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
