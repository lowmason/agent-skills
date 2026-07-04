# External data & priors — turning auxiliary information into model structure

The primary dataset is rarely all you know. Official statistics, published benchmarks, related
series, and domain constraints are a **first-class input** to the recommendation — they often
determine the prior, the pooling target, or a hard constraint more than the data itself does. This
is procedure Step 2's "inventory external/auxiliary information," made concrete.

This reference bridges `bls-data-context` (where the external numbers come from) and
`bayesian-workflow` (where priors are elicited and checked — e.g. with PreliZ).

## Four ways external information enters a model

| Channel | When | How it enters | Example |
|---------|------|---------------|---------|
| **Informative prior** | A published aggregate pins a plausible range for a parameter | Center/scale a prior on the parameter | A national rate of ~3% → `Normal(logit(0.03), small)` on a baseline log-odds |
| **Partial-pooling target** | Many small units + a trustworthy benchmark total | Shrink unit estimates toward the benchmark (hierarchical mean) | County estimates pooled toward the state/official total |
| **Covariate / offset** | A related series moves with the outcome | Add as a predictor, or as a fixed `offset`/exposure in a count model | Use an official monthly index as a covariate; population as a Poisson exposure offset |
| **Hard constraint** | An accounting identity or known bound must hold | Constrained support, sum-to-known-total, or a likelihood `factor` | Components must sum to a published total; a share ∈ [0,1] |

## Recommendation hooks (per family)

- **regression-glm / hierarchical:** external aggregate → informative prior on the intercept/rate, or
  a partial-pooling target so sparse groups borrow strength toward the benchmark (the bias–variance
  win is largest for small groups).
- **timeseries-statespace:** a benchmark series → a regression component in an STS model, or a
  measurement that the latent state is calibrated against; a known revision/benchmark → an
  observation with tight noise at that time point.
- **factor-models:** an official common index → a prior on (or a fixed value of) a loading, anchoring
  the otherwise rotation-unidentified latent factor to a known quantity.
- **counts:** population/exposure → a Poisson/NB `offset`, not a free coefficient.

## Worked example — official aggregate as an informative prior

> You model a small-area rate; the official national rate is 3.0% (SE ~0.1%).
> 1. Translate to the model's scale: baseline log-odds ≈ `logit(0.03) = -3.48`.
> 2. Set a prior centered there with width reflecting how much the area may differ from national —
>    e.g. `Normal(-3.48, 0.5)` (wider than the official SE: the area is not the nation).
> 3. Record it in `recommendation.md` §6 as a **candidate prior derived from external data**, so
>    `bayesian-workflow` carries it into prior-predictive checks and prior-sensitivity analysis.

## Cautions

- **Don't double-count.** If a benchmark already informs the prior, don't *also* fit to it as data —
  you'd use the same information twice and overshrink.
- **Match the estimand.** Place-of-work vs. place-of-residence, jobs vs. persons, vintage/as-of
  timing — an external number on a different basis is a biased prior. Check `bls-data-context` for
  the program's exact definition before borrowing its numbers.
- **Widen for transfer.** An external estimate's own SE understates the uncertainty about *your*
  unit; inflate the prior width to reflect that the external population isn't yours.
- **Pass it on.** Every external-derived prior/constraint belongs in the C4 handoff payload so it's
  reproduced, justified, and sensitivity-checked downstream — never silently baked in.
