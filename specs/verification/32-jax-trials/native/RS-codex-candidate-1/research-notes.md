# Research notes

Actual sources used:

- The complete supplied `optimize-jax` SKILL.md guidance returned by `python3 /private/tmp/jax-skill-trials-pAYZ0t/trial_io.py start /private/tmp/jax-skill-trials-pAYZ0t/native/RS-codex-candidate-1`. Its “Boundary and routing” section supplies the deep-learning/evaluate-deep-learning boundaries; its reproduction, diagnosis and generation sections supply the execution and cache routes.
- Supplied `references/profiling.md`, read only through `python3 /private/tmp/jax-skill-trials-pAYZ0t/trial_io.py readref /private/tmp/jax-skill-trials-pAYZ0t/native/RS-codex-candidate-1 references/profiling.md`. Used its specialization diagnostics and persistent-cache evidence guidance.
- Supplied `references/inference.md`, read only through `python3 /private/tmp/jax-skill-trials-pAYZ0t/trial_io.py readref /private/tmp/jax-skill-trials-pAYZ0t/native/RS-codex-candidate-1 references/inference.md`. Used its state/prediction contracts and cached-decode checks.

Ordinary skills used: none. This was a guidance-routing question, not a training diagnosis or implementation. The deep-learning and evaluate-deep-learning names are routing recommendations from the supplied main guidance; their whole skill files were not available in the supplied snapshot and were not consulted. No outside JAX skill files, other trial artifacts, plans, scoring or rubrics were inspected. No web sources were needed or consulted.

Explicit nonexecution: no delivered application/model code, JAX fixture, training code, generation code, benchmark or cache test was executed. Tool activity was limited to the authorized start/readref helpers and literal writes of response.txt and research-notes.md. No measured performance, correctness result or diagnosed application-specific cause is claimed.
