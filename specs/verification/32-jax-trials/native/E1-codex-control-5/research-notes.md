# Research notes

- Trial: E1-codex-control-5.
- Authorized task source: full output of `python3 /private/tmp/jax-skill-trials-pAYZ0t/trial_io.py start /private/tmp/jax-skill-trials-pAYZ0t/native/E1-codex-control-5`, executed as the first operation. It requested comparison of the six supplied held-out errors and recommendations for additional evidence. It described this as an approved inline analysis/code-generation task without required application execution.
- Only substantive deliverable: `response.txt`. The task did not request an implementation, so the response contains the complete analysis and experimental recommendations rather than unsolicited model code.

## Ordinary skills consulted

- `/Users/lowell/.agents/skills/validate-data/SKILL.md` — read in full; applied its analysis-QA principles to units, claim-to-evidence correspondence, small-sample limitations, confounding, reproducibility metadata, and selection bias. No pipeline or underlying dataset was available for validation. Its prescribed extra validation-report artifact and execution workflow were not used because this trial permits only these two response files and explicitly does not require application execution.
- `/Users/lowell/.agents/skills/synced/436c75ee-0034-4548-871d-10a28ca0dddc_dee8080a-267f-4358-992a-e7416ee3bf5f/learn/SKILL.md` — read in full after an initial read of `/Users/lowell/.agents/skills/learn/SKILL.md` failed because that path did not exist. Not applied: the skill explicitly excludes evaluative-verdict and calculation tasks, which matches this request.
- Ordinary skill descriptions in the supplied catalog were considered for relevance. No JAX skill file was read.

## External primary sources actually consulted

1. Bouthillier et al. (2021), *Accounting for Variance in Machine Learning Benchmarks*: https://arxiv.org/abs/2103.03098. Searched the paper by title, then opened and read the abstract page. Search results also supplied excerpts of the paper from the official MLSys proceedings URL https://proceedings.mlsys.org/paper_files/paper/2021/file/0184b0cd3cfb185989f858a1d9f5c1eb-Paper.pdf. Used for the narrow statement that initialization, data sampling, and hyperparameter choice can materially affect benchmark variability. No quantitative result from that paper is asserted for these six runs.
2. NIST/SEMATECH e-Handbook of Statistical Methods, *Randomized block designs*: https://www.itl.nist.gov/div898/handbook/pri/section3/pri332.htm. Searched for official NIST paired/block design guidance, then opened and read the full page. Used for controlling nuisance factors within blocks and making within-block comparisons. Its general design guidance is applied by inference to training experiments; seed labels alone were explicitly not treated as sufficient pairing.

Other web search hits were not relied upon. External-source links appear next to the specific claims they support in `response.txt`.

## Arithmetic and interpretation

- A sum = 0.30; mean = 0.15; sample variance = 0.0002; sample SD approximately 0.014142.
- B sum = 0.57; mean = 0.1425; sum of squared deviations = 0.002075; sample variance = 0.002075 / 3; sample SD approximately 0.026300.
- Observed mean reduction = 0.1500 - 0.1425 = 0.0075; relative reduction = 0.0075 / 0.1500 = 0.05.
- B mean for supplied seeds 0–1 = (0.13 + 0.18) / 2 = 0.155; differences B - A on these labels = -0.01 and +0.02. These are descriptive calculations, not an inference from verified paired random streams.
- No formal hypothesis-test result, confidence interval, or population win probability was fabricated. Metric definition, evaluation sample size, sampling structure, actual compute, tuning protocol, and random-stream alignment were not supplied.

## Explicit nonexecution and scope

- No delivered application/model code was executed. No training, evaluation, resampling, statistical-analysis script, or model experiment was run. Descriptive arithmetic was derived directly from the provided values.
- Read-only ordinary-skill and primary-source research was performed. Only the authorized trial-start helper and file-reading shell commands were executed; file writes used a literal patch, so answer text could not execute as shell code.
- No other trial, rubric, plan, scoring material, or new JAX skill file was inspected. No agents were spawned or delegated to.
- No repository or shared skill file was changed. Mutations were limited to this trial's `response.txt`, `research-notes.md`, and the start helper's recorded read log.
