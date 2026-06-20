# bayesian-workflow

An opinionated [Agent Skill](https://agentskills.io) for building, diagnosing, and reporting on Bayesian statistical models using **NumPyro (JAX)** and **ArviZ**.

Compatible with Claude Code, Kimi Code, Cursor, Gemini CLI, and any agent that supports the [Agent Skills spec](https://agentskills.io/specification).

This is the **NumPyro + JAX** variant of the workflow skill (the original targets PyMC + ArviZ).
Full breakdown of the original [here](https://learnbayesstats.com/blog-posts/bayesian-workflow-agent-skill-pymc-arviz).

## What it does

Guides your coding agent through the full Bayesian workflow:

1. **Formulate** the generative story
2. **Specify priors** with documented justifications
3. **Implement in NumPyro** using modern best practices (`numpyro.sample`/`plate`/`deterministic`, coords/dims, PRNGKey seeds)
4. **Prior predictive checks** before fitting (`numpyro.infer.Predictive`)
5. **Inference** via MCMC — NUTS in JAX (native `MCMC(NUTS)`, or BlackJAX as a co-equal alternative)
6. **Convergence diagnostics** (R-hat, ESS, divergences, trace/rank plots, energy plots)
7. **Model criticism** (posterior predictive checks, LOO-PIT calibration)
8. **Prior/likelihood sensitivity** (power-scaling via PSIS)
9. **Model comparison** (LOO-CV, ELPD, stacking weights)
10. **Reporting** with a canonical `<slug>/report.md` artifact and audience-adapted prose

The skill enforces guardrails that agents won't apply on their own: credible intervals (a 94% HDI is a fine default — no width is magic), mandatory calibration checks, prior/likelihood sensitivity checks (including the `log_prior` group NumPyro doesn't produce on its own), non-centered parameterizations via `LocScaleReparam`, reproducible descriptive `PRNGKey` seeds, immediate save-to-disk after sampling, JAX→NumPy conversion for downstream ArviZ ops, xarray-first data manipulation, a NUTS sampling-failure escalation ladder, discrete-latent marginalization over soft plug-ins, and a canonical report artifact whose Assessment lines and Suggested Next Steps come from a programmatic harness — not hand-rolled prose. It also ships a dedicated visualization guide (`references/visualize.md`) translating the Gabry et al. (2019) *Visualization in Bayesian workflow* paper into ArviZ.

## Install

### Claude Code

Clone and copy the skill into your personal skills directory:

```bash
git clone https://github.com/Learning-Bayesian-Statistics/baygent-skills.git /tmp/baygent-skills
mkdir -p ~/.claude/skills
cp -r /tmp/baygent-skills/bayesian-workflow ~/.claude/skills/
```

For project-level installation (available only in that project), copy into `.claude/skills/` at the project root instead.

### Other compatible agents (Kimi Code, Cursor, etc.)

Clone the repo and copy the skill folder into your agent's skills directory:

```bash
git clone https://github.com/Learning-Bayesian-Statistics/baygent-skills.git /tmp/baygent-skills
cp -r /tmp/baygent-skills/bayesian-workflow/ ~/.config/agents/skills/bayesian-workflow/
```

### NumPyro installation

NumPyro and JAX install cleanly from pip:

```bash
pip install numpyro jax arviz arviz-stats arviz-plots arviz-base preliz
pip install h5netcdf h5py          # netCDF backend for idata.to_netcdf(...)  (or: netcdf4)
pip install graphviz               # optional: model-graph rendering (needs system `dot`)
pip install blackjax               # optional: co-equal alternative JAX NUTS sampler
pip install funsor                 # optional: discrete-latent enumeration
```

For **GPU/TPU**, install the matching JAX wheel (e.g. `pip install "jax[cuda12]"`); the model code is identical.

The skill teaches the latest NumPyro + ArviZ 1.x idioms and stays runnable on the older
classic-ArviZ (0.23) plotting/stats API during the transition; its scripts are verified on the
modern stack. See SKILL.md → "Stack compatibility (NumPyro + ArviZ)" for the handful of APIs that diverge.

## Example prompts

Once installed, just ask your agent naturally:

- *"I have customer churn data with binary outcome plus age, tenure, and monthly spend. Build me a Bayesian logistic regression with uncertainty estimates."*
- *"My model has 47 divergences and R-hat of 1.03. What do I do?"*
- *"I have test scores for 200 students across 15 schools. Some schools only have 5 students. Help me build a hierarchical model."*
- *"Compare these two models and tell me which one to use. I have the InferenceData objects."*
- *"I need to present Bayesian results to my boss who has no stats background."*

## What's included

```
bayesian-workflow/
├── SKILL.md                          # Main workflow instructions
├── main.py                           # Entrypoint for programmatic use
├── pyproject.toml                    # Package metadata
├── references/
│   ├── priors.md                     # Prior selection guide + PyMC→NumPyro distribution map
│   ├── diagnostics.md                # Convergence diagnostics
│   ├── model-criticism.md            # PPC, calibration, LOO-PIT, SBC
│   ├── model-comparison.md           # LOO-CV, ELPD, stacking weights
│   ├── hierarchical.md               # Partial pooling, non-centered parameterization (reparam)
│   ├── sensitivity.md                # Prior/likelihood sensitivity (power-scaling) + log_prior recipe
│   ├── reporting.md                  # Report templates, audience adaptation
│   └── visualize.md                  # Visualization across the workflow (Gabry et al. 2019 → ArviZ)
└── scripts/
    ├── diagnose_model.py             # Post-sampling diagnostics report (writes diagnostics.json)
    ├── calibration_check.py          # Calibration plots from InferenceData (writes calibration.json)
    └── check_diagnostics.py          # Interprets diagnostics + calibration into qualitative ratings + suggested next steps
```

## License

MIT - see [LICENSE](../LICENSE).
