# Research and delivery notes

## Authorized scope
- Read the task and complete supplied guidance using:
  python3 /private/tmp/jax-skill-trials-pAYZ0t/trial_io.py start /private/tmp/jax-skill-trials-pAYZ0t/native/E2-codex-candidate-1
- Wrote only response.txt and research-notes.md in the owned trial directory. The helper may maintain its authorized reference read log.
- Did not inspect other trials, rubrics, scoring, plans, or external new JAX skill files.
- Did not spawn or delegate.

## Supplied task-specific sources actually read
The helper readref operation was used for all three references, with their full outputs read:
- references/protocol.md: comparison contract; sample/run/sampling/predictive/numerical uncertainty; paired alignment; nonlinear metrics; temporal blocks; no automatic pairing from seed IDs.
- references/domain-checks.md: origin/horizon/stride contracts; sequence causality, availability, chronological splits; repeated target timestamps; shared panel shocks; predictive calibration.
- references/experiments.md: run, parent, data, configuration, seed, environment, artifacts, metrics, budget, status, and decision record contract.

Main task-specific guidance: supplied evaluate-deep-learning snapshot, read in the start operation. No other evaluate-deep-learning/deep-learning/optimize-jax skill collection files were read.

## Ordinary skills actually used
- /Users/lowell/.agents/skills/clean-code/SKILL.md: read completely; used descriptive names, cohesive validation/resampling/comparison responsibilities, explanatory denominator variables, and comments that identify statistical intent.
- /Users/lowell/.agents/skills/verification-before-completion/SKILL.md: read completely; completion claim is limited to writing and inspecting the requested text artifacts. No pass, coverage, model-quality, or numerical execution claim is made.
- No new design approval workflow or implementation-plan artifact was created. The supplied authorization describes an already approved inline task.

## Primary external sources actually accessed
- Hyndman and Athanasopoulos, Forecasting: Principles and Practice, section 5.10:
  https://otexts.com/fpp3/tscv.html
  Opened and read the returned section. Used for rolling forecast origins, chronological information availability, and horizon evaluation.
- Politis and Romano, The Stationary Bootstrap:
  https://statistics.stanford.edu/technical-reports/stationary-bootstrap
  Opened Stanford's primary report landing page. Its purl link failed with a tool timeout; no content from the inaccessible repository document was claimed.
- Politis and Romano, The Stationary Bootstrap, JASA:
  https://www.tandfonline.com/doi/abs/10.1080/01621459.1994.10476870
  Search result supplied publisher abstract: stationary weak dependence, random blocks, standard errors/confidence regions. Final response links this primary publisher source.
- Politis and Romano, The Stationary Bootstrap, Purdue technical report:
  https://www.stat.purdue.edu/docs/research/tech-reports/1991/tr91-03.pdf
  Primary paper search excerpt read: geometric block lengths and recalculation of the statistic on pseudo series.
- Bouthillier et al., Accounting for Variance in Machine Learning Benchmarks:
  https://arxiv.org/abs/2103.03098
  Opened and read abstract/source information. Used for distinct data sampling, parameter initialization, and hyperparameter-selection variation.
- Search returned other secondary results, but none was used as support.
- The provided stationary-bootstrap implementation is original application code based on the stated construction, not a claimed executed benchmark implementation.

## Explicit nonexecution and evidence limitations
- No delivered application/model/statistical code was executed.
- No training, inference, array scoring, bootstrap simulation, model validity checks, permanent tests, accelerator checks, or interval-coverage experiment was run.
- No numerical model scores, empirical intervals, effective sample size, calibration results, or test passes were invented.
- The code is a supplied unexecuted implementation for one regularly spaced trajectory and two frozen checkpoints; broader cluster/panel and repeated-training designs are described separately.
- The anticipated artifact check will inspect text presence, size, required content, and fenced-code balance only; it will not execute or parse the delivered Python.

