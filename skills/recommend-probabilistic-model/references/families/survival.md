# Survival & time-to-event

**When this family fits:** The outcome is the time until an event (churn, failure, job exit, death), and for some subjects the event has not happened yet when observation stops (right-censoring), or happened at an unknown time inside a window (interval-censoring). Dropping the censored subjects, or treating their last-seen time as the event time, biases durations downward.

## Methods & defaults

| Method | Use when | Default recommendation | PML §ref (Book 1 / Book 2) | pyprobml |
|--------|----------|------------------------|----------------------------|----------|
| Censored parametric likelihood (Weibull / LogNormal / Gamma) | A smooth hazard shape is plausible; you want predictions of whole duration distributions | Start here for a Bayesian fit: the censored subjects contribute their survival probability past the censoring time, the observed ones their density (Kalbfleisch and Prentice 2002) | — | — |
| Accelerated failure time (AFT) | Predictors should stretch or shrink time | Log-time is linear in predictors with a Weibull, LogNormal or log-logistic error; coefficients read as time ratios | — | — |
| Piecewise-exponential (Poisson trick) | The hazard shape is unknown or changes over time; time-varying predictors | Split time into intervals with a constant hazard each; fits as a Poisson GLM with a log-exposure offset, so hierarchical and spline priors carry over | — | — |
| Cox proportional hazards | Only relative risks matter and the baseline hazard is a nuisance | The frequentist default (partial likelihood); check proportional hazards before reporting one hazard ratio | — | — |

## Selection & regularization (Step 6, family-specific)
Complexity knobs: the hazard shape (parametric family, or the number of piecewise intervals) and which predictors enter. Compare parametric families with LOO-ELPD on the censored likelihood; regularize many predictors with the same shrinkage priors as `regression-glm.md`. Rpm's per-family knob table (`references/model-selection-regularization.md`) has no survival row yet: until it does, this subsection is the knob specification.

## Gotchas
- **Censoring is information, not missingness.** A customer still active at month 18 says the duration exceeds 18; drop them and you overstate churn.
- **Censoring must be independent of the risk.** If people leave the study because they are about to have the event, no likelihood fixes it from these data alone.
- **Hazard ratios are not time ratios.** Cox coefficients scale the hazard; AFT coefficients scale time. Report the one your audience can act on.
- **Competing risks.** When another event prevents the one of interest (job exit by retirement vs. layoff), a plain survival curve for one cause misleads; model the causes jointly.

## Handoff
Bayesian fits go to **bayesian-workflow**: wrap the base duration distribution in `RightCensoredDistribution` (or `LeftCensoredDistribution` / `IntervalCensoredDistribution`) with the censoring flag as the mask, as in its censored-data row. Frequentist alternatives: lifelines (`CoxPHFitter`, `WeibullAFTFitter`) or statsmodels `PHReg`. C4 memo payload if Bayesian:
- **Likelihood family:** censored Weibull / LogNormal, or piecewise-exponential as a Poisson GLM with offset.
- **Candidate priors:** on log-scale shape and scale; shrinkage on predictor coefficients.
- **Structure:** censoring type and flag; time-varying predictors; any grouping (hierarchical frailty).
- **Regularization/selection plan:** LOO-ELPD across hazard families; shrinkage on predictors.
