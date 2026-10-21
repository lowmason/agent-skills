# SVI Convergence

## Contents
- When SVI is the fit
- Three checks before you trust it
- Running the checks

## When SVI is the fit

This skill fits with NUTS, and it uses SVI (stochastic variational inference) mainly to warm-start NUTS
([references/diagnostics.md](diagnostics.md), escalation ladder rung 4). This file covers the other
case: SVI is the final approximation, for example because NUTS is too slow at the data size. Then
SVI's learning rate and `num_steps` are inference settings. Tune them until the three checks below
pass, not to a held-out predictive score.

Passing the checks says the optimizer converged and the approximation holds up on what the checks
test. It does not make SVI as trustworthy as NUTS: a mean-field guide such as `AutoNormal` ignores
posterior correlations and tends to understate posterior variance. Where NUTS runs in reasonable
time on the model, prefer it.

## Three checks before you trust it

1. **The ELBO trace is flat at the end, and every seed reaches the same value.** `svi.run` returns
   the loss (the negative ELBO) at each step in `losses`. Run SVI from four seeds. Over the last few
   hundred steps the loss should not drift, and the seeds' final means should agree within the
   loss's own step-to-step noise. A trace that still falls: raise `num_steps`. A trace that
   oscillates or turns `nan`: lower the learning rate. A seed that settles at a different value found
   another optimum, which more steps will not fix: look at the model or the guide.
2. **PSIS-LOO for the approximate posterior.** `arviz_stats.loo_approximate_posterior` takes the log
   joint density `log p(θ, y)` and the guide's log density `log q(θ)` at each guide draw, and it
   corrects LOO for the gap between the guide and the posterior (Magnusson et al. 2019). Read its
   Pareto k values as for ordinary LOO ([references/model-criticism.md](model-criticism.md)). Values
   above `good_k` mean the importance weights are unstable at those observations, so the ELPD there
   is not reliable. A richer guide (`AutoMultivariateNormal`) or NUTS is the next step.
3. **VSBC (Yao et al. 2018).** `numpyro.infer.calibration.vsbc_diagnostic` simulates data sets from
   the model, refits the guide on each one, and tests whether the guide's posterior puts each
   parameter's true value at the middle on average. A small KS p-value for a parameter means the
   guide's estimate of it is biased. `ks_pvalues` is a dict keyed by site name. The check refits the
   guide `num_simulations` times, so set `num_svi_steps` to what check 1 showed is enough.

## Running the checks

The three checks on the running example's `model(x, y)` from SKILL.md's template:

```python
from numpyro.infer import SVI, Trace_ELBO, log_likelihood
from numpyro.infer.autoguide import AutoNormal
from numpyro.infer.calibration import vsbc_diagnostic
from numpyro.infer.util import log_density
from numpyro.optim import Adam

# 1. The ELBO trace: flat at the end, and the same value from every seed.
guide = AutoNormal(model)
svi = SVI(model, guide, Adam(0.01), Trace_ELBO())
runs = [svi.run(jax.random.PRNGKey(seed), 3000, x, y=y, progress_bar=False) for seed in range(4)]
tails = [np.asarray(run.losses[-500:]) for run in runs]
print("final loss by seed:", [round(float(t.mean()), 1) for t in tails])
print("drift over the tail:", [round(float(t[:250].mean() - t[250:].mean()), 2) for t in tails])
print("noise over the tail:", [round(float(t.std()), 2) for t in tails])

# 2. PSIS-LOO for the approximation: log p(theta, y) and log q(theta) at each guide draw.
params = runs[0].params
draws = Predictive(guide, params=params, num_samples=1000)(jax.random.PRNGKey(10), x)
latent = {site: draws[site] for site in ("beta", "sigma")}
log_p = jax.vmap(lambda s: log_density(model, (x,), {"y": y}, s)[0])(latent)
log_q = jax.vmap(lambda s: log_density(guide, (x,), {"y": y}, {**params, **s})[0])(latent)
idata_svi = az.from_dict({
    "posterior": {site: np.asarray(v)[None] for site, v in latent.items()},
    "log_likelihood": {"y_obs": np.asarray(log_likelihood(model, latent, x, y=y)["y_obs"])[None]},
    "observed_data": {"y_obs": y},
})
loo_svi = azs.loo_approximate_posterior(idata_svi, log_p=np.asarray(log_p), log_q=np.asarray(log_q))
print(loo_svi)                       # Pareto k above loo_svi.good_k: unstable weights there

# 3. VSBC: is the guide biased, averaged over data the model simulates?
vsbc = vsbc_diagnostic(jax.random.PRNGKey(20), model, AutoNormal(model), Adam(0.01), Trace_ELBO(), x,
                       observed_sites=["y_obs"], num_simulations=50, num_svi_steps=2000,
                       num_samples=500)
print(vsbc.ks_pvalues)               # {site: p-value}; a small one marks a biased estimate
```
