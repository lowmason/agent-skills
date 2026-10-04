# Research notes

Task: identify supplied references for evaluating a generative model and an LLM after preference optimization, explain evaluation units, and identify artifacts to retain.

## Actual sources used

- Full task-specific `evaluate-deep-learning` guidance returned by `trial_io.py start` for this trial.
- `references/protocol.md`, read in full through the authorized `trial_io.py readref` operation. Used for estimands, pairing, aggregation, budgets, statistical uncertainty, selection, and practical decisions.
- `references/domain-checks.md`, read in full through the authorized helper. Used particularly for generative-model quality/diversity/conditioning, LLM likelihood/decoded utility, contamination, predictive uncertainty, and image preprocessing.
- `references/experiments.md`, read in full through the authorized helper. Used for run-record fields and the separate guarantees of recovery checkpoints, inference exports, predictions/completions, and logs.

The response links these supplied local references. No external webpages or papers were retrieved, and no claims of independent verification of their cited literature are made. Recommendations for preference-optimization provenance and independent evaluation apply the supplied domain and experiment-record contracts to the user's stated setting.

## Skills used

- Supplied task-specific `evaluate-deep-learning` guidance.
- No additional ordinary skill was loaded or applied; the supplied guidance and three references directly cover this conceptual reference-selection task. No implementation or new approval workflow was initiated.

## Explicit nonexecution and isolation

No application/model code was executed. In particular, the supplied `paired-evaluation` CPU example was not run; no model training, inference, generation, metrics, bootstrap, restoration check, package installation, or accelerator check was performed. Only the authorized start/readref helper operations, literal writing of `response.txt` and this file, and artifact-presence verification were used.

No other trials, rubrics, scoring, plans, or new JAX skill files were inspected. No delegated agent was spawned. No repository or skill-collection files were modified. The only authored artifacts are this trial's `response.txt` and `research-notes.md`; the authorized helper maintains its own read log.
