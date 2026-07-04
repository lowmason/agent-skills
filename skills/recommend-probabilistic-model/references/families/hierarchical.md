# Hierarchical / multilevel models

**When this family fits:** Data has a group / cluster / panel structure (a county, subject, school, store ID; repeated measures over the same unit) and at least some groups have few observations — so neither fitting each group separately (overfits small groups) nor pooling everything into one model (washes out real group differences) is right.

## Methods & defaults

| Method | Use when | Default recommendation | PML §ref (Book 1 / Book 2) | pyprobml |
|--------|----------|------------------------|----------------------------|----------|
| Partial-pooling hierarchical model (varying intercepts/slopes) | Grouped/panel data; few obs per group; want group estimates that borrow strength | **Default.** Give each group its own params drawn from a shared global prior — partial pooling shrinks sparse groups toward the population, keeps data-rich groups distinct | PML1 §4.6.5 / PML2 §15.5 | notebooks/book2/15/linreg_hierarchical_numpyro.ipynb |
| Hierarchical GLM / GLMM (mixed effects) | Non-Gaussian outcome (count/binary/rate) or you need a link; "fixed" global effects + "random" group offsets | Add group-level random effects on the GLM linear predictor; correlated random effects capture within-group dependence | — / PML2 §15.5.1 | notebooks/book2/03/hierarchical_binom_rats.ipynb |
| Non-centered parameterization | Any hierarchical model fit by HMC/NUTS, especially with few obs per group / small group-variance | Reparameterize group offsets as `θ_j = μ + σ·z_j`, `z_j ~ N(0,1)` to escape Neal's funnel and divergences | — / PML2 §15.5.2 | notebooks/book2/15/linreg_hierarchical_non_centered_numpyro.ipynb |

## Selection & regularization (Step 6, family-specific)
For this family, **partial pooling *is* the regularizer** — the group-level variances (σ_α, σ_β) are the complexity knob, learned from data rather than tuned. Large group variance → near no-pooling (groups float free); small group variance → near complete pooling (groups collapse to the global mean). You choose *structure* (which coefficients vary by group: intercept only vs. varying slopes; one level vs. nested levels), not a penalty strength. For comparing structures (e.g. varying-intercept vs. varying-intercept+slope), plan **LOO-ELPD** (post-fit, in bayesian-workflow). Specializes `references/model-selection-regularization.md`.

## Gotchas
- **Neal's funnel.** Group-level scale and group offsets are tightly coupled; centered parameterizations cause divergences and poor mixing when σ is small or groups are sparse. Default to non-centered (PML2 §15.5.2).
- **Half-normal / half-Cauchy on variances, not inverse-gamma.** Group-level standard deviations are weakly identified when there are few groups; use a weakly-informative half-Cauchy/half-normal `C+` prior (as the radon model does), not a vague IG prior.
- **Too few groups.** With only ~3–5 groups, the top-level variance is barely informed — the hierarchy degenerates toward complete pooling. Hierarchy pays off with many groups, some of them data-poor.
- **"Fixed vs random effects" is overloaded.** The terms have several conflicting definitions in the literature; specify the actual generative structure (which params are shared θ_0 vs. group-specific θ_j) rather than relying on the label.

## Handoff
**→ bayesian-workflow.** This is almost always a Bayesian recommendation. C4 payload the memo must carry: **likelihood family** (Gaussian for continuous; Binomial/Poisson + link for GLMM); **candidate priors** — global means weakly-informative (e.g. N(0,1)); group-level scales half-Cauchy/half-normal `C+(1)`; **structure** — the grouping column(s), which coefficients vary by group (intercept-only vs. varying-slope), nesting depth, non-centered parameterization; **regularization/selection plan** — partial pooling is the regularizer (group variances learned), compare structures by LOO-ELPD post-fit.
