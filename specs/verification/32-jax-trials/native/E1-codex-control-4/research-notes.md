# Research notes

Task source: the full authorized prompt was read from the required first command, `python3 /private/tmp/jax-skill-trials-pAYZ0t/trial_io.py start /private/tmp/jax-skill-trials-pAYZ0t/native/E1-codex-control-4`.

## Sources actually consulted

- Ordinary skill: `/Users/lowell/.agents/skills/validate-data/SKILL.md`, read fully. Applied its analysis QA guidance to distinguish arithmetic from supported inference, check units and run counts, and state unavailable reproducibility and selection information. The skill's embedded example code was not executed. A separate validation report records these checks and limitations.
- Primary external source: Xavier Bouthillier et al., *Accounting for Variance in Machine Learning Benchmarks*, https://arxiv.org/abs/2103.03098. The abstract was opened and read. It supports the statement that data sampling, initialization, and hyperparameter choice affect benchmarking variance, rather than any case-specific conclusion about A or B.
- Discovery search: `Accounting for variance in machine learning benchmarks Bouthillier 2021 paper random seeds computational budget`. Search results included the author's site, arXiv, PMLR, and secondary indexes. Secondary summaries were not used as evidence for the delivered claims.
- Attempted to open the official proceedings abstract at https://proceedings.mlsys.org/paper/2021/hash/cfecdb276f634854f3ef915e2e980c31-Abstract.html; the browsing tool reported it inaccessible. No claim relies on that inaccessible page.

## Calculations and assumptions

All arithmetic was checked analytically without running analysis code. A's sum is 0.30, mean 0.15, and sample variance 0.0002. B's sum is 0.57, mean 0.1425, and sample variance 0.002075/3 = 0.0006916667. The sample standard deviations are approximately 0.014142 and 0.026300. The independent-run standard-error expression is sqrt(0.0002/2 + 0.0006916667/4), approximately 0.01652. The mean B-minus-A difference is −0.0075, while the mean difference on shared seed labels is +0.005. These describe unequal training budgets and cannot identify a method effect at a common budget.

The supplied description does not verify a common evaluation set, metric definition, random-factor coupling, independent seed draws, tuning equality, or absence of run selection. The response states its initial metric/evaluation assumptions and requests the missing evidence. The advice on equal budgets, balanced pilot, decision threshold, and uncertainty is analysis specific to this prompt, not a quotation or empirical finding from the external paper.

## Explicit nonexecution and scope

No delivered application, model, training, analysis, resampling, or test code was executed. The authorized helper command was executed solely to read the task. Subsequent actions were read-only skill/source inspection and literal artifact writes followed by artifact readback. No new JAX skill was opened. No other trial directories, rubrics, plans, scoring materials, or delivered application code were inspected. No agents were spawned or delegated to. No repository or shared skill files were modified. All authored artifacts belong only to `/private/tmp/jax-skill-trials-pAYZ0t/native/E1-codex-control-4/`.
