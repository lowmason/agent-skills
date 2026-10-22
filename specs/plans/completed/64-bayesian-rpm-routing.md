# Bayesian and RPM Routing Implementation Plan

**Status: COMPLETE (2026-10-21)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md (section 64-bayesian-rpm-routing)

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close five routing gaps from the 2026-10-03 audit (re-verified 2026-10-18) in bayesian-workflow, recommend-probabilistic-model (rpm) and creative-thinking: a home for Gaussian processes, a siblings block and scope for bayesian-workflow, four missing model classes in rpm, rpm's links to the skills that arrived after it, and creative-thinking's causal and neural hand-offs.

**Architecture:** Skill text only, plus one new bayesian-workflow reference with runnable NumPyro code, one new rpm family file, one `SOFT_REFERENCES` entry and NOTICE lines. Three description edits each get a routing micro-test (Appendix A) against the baseline description, with the competing descriptions in the prompt. No script, installer or adapter changes.

**Tech Stack:** Markdown skills; NumPyro + JAX at the versions in `build/snippet_preamble.py`'s `PINNED` (the snippet gate's Tier 3); `claude -p` for micro-tests; the repo's lints (`build/run_commit_lints.sh`).

**Spec:** none. The requirements are the five open items in `specs/deferred_items.md`, section `## audit-3-10-26 routing (no plan; re-verification pass, branch claude/quizzical-hermann-814d89) — 2026-10-18` (the `/deferred` "Plan" disposition, picked as group P2 at the 2026-10-21 triage). Each task quotes its item's Done-when.

## Owner questions (answered 2026-10-21)

The owner took the recommended default, option (a), for all eight questions at plan review on 2026-10-21. They are logged as D3–D10 in `## Decisions`. The tasks keep their non-default branches only as a record: execute option (a) everywhere.

- **Q1 — "Pyro" in bayesian-workflow's description (Task 3).** The description triggers on "Pyro" (`skills/bayesian-workflow/SKILL.md:11`), but the body is NumPyro-only. A PyTorch Pyro user would get NumPyro code. Options: (a) **drop "Pyro"** (recommended); (b) keep it. The deferred item requires your call to be recorded.
- **Q2 — bayesian-workflow's scope sentence (Task 3).** The recorded item says "SVI-only fits are not" in scope. Plan 59 has since added `references/svi.md`, "When SVI is the fit", and SKILL.md `:286-289` ("SVI as the final fit"). The recorded sentence now contradicts the skill. Options: (a) **NUTS is the default, SVI as the final approximation is in scope under `svi.md`'s checks, and BNNs are in scope when posterior inference is the task** (recommended); (b) keep the recorded sentence and narrow `svi.md` (outside this plan).
- **Q3 — Sources for the classes PML barely covers (Task 4).** A search of the local book index (`build/.scratch/book{1,2}_sections.tsv`) finds one exact section for ordinal regression (PML2 §15.4.4) and no section titled for survival, censoring, beta regression or quantile regression. Options: (a) **cite standard non-PML sources by author-year only, with a NOTICE line** (recommended): Kalbfleisch and Prentice (2002) for survival; Ferrari and Cribari-Neto (2004) for beta regression; Koenker and Bassett (1978) for quantile regression; McCullagh (1980) for proportional-odds ordinal regression; (b) leave the PML column `—` and cite nothing else. Either way a PML §-ref goes in only after a Gate B read confirms it.
- **Q4 — rpm's link to the new GP reference (Task 2).** Options: (a) **a path (`bayesian-workflow/references/gaussian-processes.md`) plus a `SOFT_REFERENCES` entry** (recommended: rpm only points the fitting session there and never reads it); (b) a hard `DEPENDENCIES` entry; (c) bare-name wording ("bayesian-workflow's GP reference") with no entry.
- **Q5 — creative-thinking's description (Task 6).** The item allows a body-only change. Options: (a) **add one sentence to the description and micro-test it** (recommended); (b) body only, with no micro-test.
- **Q6 — "Estimand (if causal)" row in bayesian-workflow's report template (Task 3).** The item makes it optional. Options: (a) **add it** (recommended); (b) skip it.
- **Q7 — New rows in bayesian-workflow's model-family table (outside the items).** Task 4 routes bounded and quantile outcomes to bayesian-workflow, whose table (`SKILL.md:311-326`) has ordinal and censored rows but no Beta or quantile row. Options: (a) **leave the table as is and log a deferred item** (recommended: the items do not ask for it); (b) add two rows in Task 4.
- **Q8 — Micro-test budget and model.** Three routing micro-tests (Tasks 3, 5, 6), about 150 decision-only calls on Sonnet. Plan 59's similar 75-call test cost $4.68. Options: (a) **Sonnet, cap $25** (recommended); (b) another model or cap.

## Global Constraints

- **Lifecycle coordination.** The model-lifecycle spec (`specs/model-lifecycle.md`, PR lowmason/agent-skills#106, branch `claude/model-lifecycle-spec-592dd5`, anchors at `7612c6e`) re-scopes tune-hyperparameters and widens track-model-experiments (owner decision O1 (ii), 2026-10-21). This plan must NOT edit:
  - any file under `skills/tune-hyperparameters/` or `skills/track-model-experiments/`;
  - rpm's knob table (`skills/recommend-probabilistic-model/references/model-selection-regularization.md`, "Per-family knobs", `:39-50`; lifecycle R12a);
  - rpm `references/reporting.md:54`, the "Runs next" line (lifecycle R28);
  - `skills/bayesian-workflow/references/model-comparison.md` (lifecycle R19).
- **Shared files.** Both efforts edit `skills/recommend-probabilistic-model/SKILL.md`, `skills/recommend-probabilistic-model/references/reporting.md` and `skills/bayesian-workflow/SKILL.md`. The plan that lands second rebases and re-reads its anchors (the lifecycle spec's Coordination section says the same).
- **Describe tune and track so the text stays true across O1.** Use these exact phrasings: tune-hyperparameters "searches a model's knobs (regularization, depth, learning rate, inference settings) without leaking the future"; track-model-experiments "keeps the ledger of fitted model variants and compares them". Do not name a mode (ELPD, tabular CV, score mode) that track may or may not have when this lands.
- **Plan 63** (`specs/plans/63-conformance-gaps.md`, branch `claude/plan-35-conformance-gaps-427f5e`) rewrites seven descriptions (clean-coder, executing-plans, explore-data, recommend-visualization, systematic-debugging, validate-data, writing-plans). None is in this plan. It also edits `build/test_runtime_support.py` and `NOTICE` (found by `entry_check.py`'s overlap report, 2026-10-21). Task 2 adds one `SOFT_REFERENCES` entry to the first, and Tasks 1 and 4 add lines to the second, so the plan that lands second rebases.
- **Plan 53** (portability, not executed) edits other lines of `skills/bayesian-workflow/SKILL.md`. Do not touch those lines' content beyond this plan's anchors.
- **Version numbers.** Never write a literal package version in skill text or in this plan's commands. Run the snippet gate with CLAUDE.md's Tier 3 command, whose pins are `build/snippet_preamble.py`'s `PINNED`. (A repo-wide version policy is being designed separately: the brainstorming session "Brainstorm repo-wide package version policy", 2026-10-21. It is not part of this plan.)
- **Compaction window (bayesian-workflow).** The body is past the 20,000-character window. `build/test_check_conformance.py`'s `CRITICAL_SPANS` guards `## Critical rules` and `## Common gotchas`. At `7612c6e`, `## Common gotchas` ends at body offset 16,441, so at most about 3,500 characters may be inserted before it. Target 1,300 or fewer (block plus scope sentence). Run the critical-placement tests after Task 3.
- **Licensing.** rpm and creative-thinking are the owner's originals. bayesian-workflow is adapted from Alexandre Andorra's skill (`LICENSE-andorra`). NOTICE records external sources each skill cites, by author-year, in that skill's paragraph; it does not list the owner's own new files. Never reproduce PML book prose anywhere, this plan and commit messages included: cite section numbers only, in original wording. Never commit `build/.scratch/`.
- **Cross-skill references.** Use bare skill names. A skill name followed by a possessive and a capitalized word ("recommend-causal-design's Estimand") or a path (`x/references/…`) is an install edge that `build/test_runtime_support.py -k declared_dependencies` checks. Run that test in every task that edits skill text.
- **Descriptions.** Each stays under 1,024 characters and starts with "Use when". Measured at `7612c6e`: rpm 872, bayesian-workflow 766, creative-thinking 496. The candidates below measure rpm 1,005, bayesian-workflow 755 (Q1 a), creative-thinking 576.
- **Citations.** `build/.scratch/` exists only in the main checkout (`/Users/lowell/Projects/agent-skills/build/.scratch/`, gitignored at `.gitignore:21`). Run Gate A with the main checkout's script, by absolute path, against the worktree's skill directory (Task 4 gives the command). If `.scratch` is missing, the owner rebuilds it with `uv run --python 3.13 python build/extract_structure.py` from the main checkout (needs the local PDFs under `~/Documents/Bayesian/Probabilistic Machine Learning/` and `gh`). Do not copy or symlink `.scratch` into the worktree.
- **Commits.** End each commit message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` (the session's trailer, per the owner's standing rule). Run `build/run_commit_lints.sh` before each commit.

## Decisions

- **D1** (owner, brief, 2026-10-21): O1 (ii) — track-model-experiments covers Bayesian variants plus a tabular-CV mode; neural records stay with evaluate-deep-learning. O2 (b) — a predictive-evaluation reference owned by track. Recorded on main in `specs/deferred_items.md` (`7612c6e`). Applied in: Global Constraints (the tune and track phrasings, the leave-alone list).
- **D2** (owner, plan writing, 2026-10-21): a package version policy for all skills (latest release or version as a parameter, JAX and Python included) goes to its own brainstorming session, not this plan. Applied in: Global Constraints (version numbers).
- **D3** (owner, plan review, 2026-10-21): Q1 (a) — drop "Pyro" from bayesian-workflow's description. Applied in: Task 3 (Steps 4 and 7; M1 keeps probe B1).
- **D4** (owner, plan review, 2026-10-21): Q2 (a) — the scope sentence says NUTS is the default, SVI as the final approximation is in scope under `references/svi.md`'s checks, and BNNs are in scope when posterior inference is the task. Applied in: Task 3 (Step 3).
- **D5** (owner, plan review, 2026-10-21): Q3 (a) — where PML has no supporting section, cite Kalbfleisch and Prentice (2002), Ferrari and Cribari-Neto (2004), Koenker and Bassett (1978) and McCullagh (1980) by author-year only, with a NOTICE line; a PML §-ref goes in only after a Gate B read. Applied in: Task 4 (Steps 4, 5 and 7).
- **D6** (owner, plan review, 2026-10-21): Q4 (a) — rpm cites the path `bayesian-workflow/references/gaussian-processes.md` and gets a `SOFT_REFERENCES` entry. Applied in: Task 2 (Steps 3 and 4).
- **D7** (owner, plan review, 2026-10-21): Q5 (a) — add one sentence to creative-thinking's description and micro-test it (M3). Applied in: Task 6 (Steps 1, 3 and 5).
- **D8** (owner, plan review, 2026-10-21): Q6 (a) — add the "Estimand (if causal)" row to bayesian-workflow's report template. Applied in: Task 3 (Step 5).
- **D9** (owner, plan review, 2026-10-21): Q7 (a) — leave bayesian-workflow's model-family table as is, and log the Beta and quantile rows as a deferred item. Applied in: Completion notes.
- **D10** (owner, plan review, 2026-10-21): Q8 (a) — run the micro-tests on Sonnet, with a $25 cap across M1–M3. Applied in: Tasks 3, 5 and 6; Appendix A.

---

## File map

| File | Task | Change |
|---|---|---|
| `skills/bayesian-workflow/references/gaussian-processes.md` | 1 | Create: GP template, priors, HSGP |
| `skills/bayesian-workflow/SKILL.md` | 1, 3 | GP row (`:326`); siblings block and scope sentence; description |
| `build/snippet_preamble.py` | 1 | Re-measure the block-count docstring (`:15-22`) |
| `NOTICE` | 1, 4 | Author-year sources for the GP reference and the new rpm rows |
| `skills/recommend-probabilistic-model/references/families/gaussian-processes.md` | 2 | Default to bayesian-workflow's reference; off-stack note; drop PyMC |
| `build/test_runtime_support.py` | 2 | One `SOFT_REFERENCES` entry (Q4 a) |
| `skills/bayesian-workflow/references/reporting.md` | 3 | "Estimand (if causal)" row (Q6 a) |
| `specs/verification/64-routing-microtests.md` | 3, 5, 6 | Create: micro-test record |
| `skills/recommend-probabilistic-model/references/decision-map.md` | 4 | Four signal rows, one task row |
| `skills/recommend-probabilistic-model/references/families/regression-glm.md` | 4 | Ordinal, bounded and quantile rows, gotchas, handoff |
| `skills/recommend-probabilistic-model/references/families/survival.md` | 4 | Create: time-to-event family |
| `skills/recommend-probabilistic-model/SKILL.md` | 4, 5 | Reference map count; siblings, Step 1, description |
| `skills/recommend-probabilistic-model/references/reporting.md` | 5 | Memo §8 line for tune and track (not `:54`) |
| `skills/recommend-probabilistic-model/references/families/graphical-models.md` | 5 | GNN handoff |
| `skills/recommend-probabilistic-model/references/families/classification.md` | 5 | Deep-ensemble handoff |
| `skills/creative-thinking/SKILL.md` | 6 | Hand-offs; description (Q5 a) |

Micro-test kit (outside the repo): `~/.cache/agent-skills/scratch/plan64-micro/` (Appendix A).

---

### Task 1: Gaussian-process reference in bayesian-workflow

Item (G11), Done when: "the reference exists with runnable examples and both skills point at it." This task does the bayesian-workflow half; Task 2 does rpm.

**Files:**
- Create: `skills/bayesian-workflow/references/gaussian-processes.md`
- Modify: `skills/bayesian-workflow/SKILL.md:326` (the "Gaussian processes" row of "Common model families")
- Modify: `build/snippet_preamble.py:15-22` (coverage docstring)
- Modify: `NOTICE` (bayesian-workflow paragraph, after the "Betancourt 2020 … bundles no copies of any of them." sentence ending at `:71`)

**Interfaces:**
- Produces: the path `skills/bayesian-workflow/references/gaussian-processes.md`, which Task 2 cites. Model function names `gp_model` and `hsgp_model`.

Facts verified while planning (2026-10-21, NumPyro and JAX at `PINNED`):
- `numpyro.contrib.hsgp` exports nothing at package level. Import from `numpyro.contrib.hsgp.approximation`: `hsgp_squared_exponential(x, alpha, length, ell, m, non_centered=True)`, `hsgp_matern(x, nu, alpha, length, ell, m, non_centered=True)`, `hsgp_periodic_non_centered`, `hsgp_rational_quadratic`. The functions sample an internal site named `beta`.
- In float32 the HSGP fit below diverged on all 300 draws at n = 2,000 (13 of 300 at n = 200). With `numpyro.enable_x64()` it gave 0 divergences and recovered the noise scale (0.199 against a true 0.2). The x64 line is load-bearing.
- Both blocks below are runnable under `check_snippets.py --run` (no fixture variables, no unbound names). Extracted from this plan, they passed Tiers 1, 2 and 3, and a planted `assert` failure in the HSGP block was reported (exit 1), so the gate does execute them. `Predictive` recomputes the deterministic `f` at `x_new` (shape (300, 50)); it does not reuse the fitted values.

- [x] **Step 1: Write the failing check.** Tier 1 on a missing file proves nothing, so the failing check is the SKILL.md link. Run:

```bash
grep -c 'references/gaussian-processes.md' skills/bayesian-workflow/SKILL.md
```

Expected: `0`.

- [x] **Step 2: Create the reference.** Write `skills/bayesian-workflow/references/gaussian-processes.md` with exactly this content:

````markdown
# Gaussian Processes

## Contents
- When to use which GP
- Priors on the length-scale and amplitude
- Exact GP template
- Hilbert-space approximation (HSGP)
- Off-stack GP libraries

## When to use which GP

A GP puts a prior on an unknown smooth function. Pick the implementation by the number of
observations n and the input dimension D:

| Case | Use | Cost |
|---|---|---|
| n up to about 1,000 to 2,000 | Exact GP: `MultivariateNormal` over the n points | O(n³) per gradient |
| Larger n, D = 1 to 3 | HSGP from `numpyro.contrib.hsgp.approximation` | O(n·m^D), m basis functions per dimension |
| Larger n and D above 3 | Neither scales well: reduce D, or see Off-stack GP libraries | — |

Standardize the outcome and centre the inputs before either. Set the numerics policy first:
GP covariance algebra loses accuracy in float32 (see [jax-numerics.md](jax-numerics.md)).

## Priors on the length-scale and amplitude

- **Length-scale.** The data cannot inform length-scales shorter than the smallest gap between
  inputs or longer than the input range. Put most prior mass between those two numbers. An
  `InverseGamma` has light left and right tails there; choose its two parameters so that about
  1% of the mass falls below the smallest gap and about 1% above the range, and check with a
  prior predictive draw of functions.
- **Amplitude** (the marginal standard deviation of f). On a standardized outcome, `HalfNormal(1)`
  is a sound default. Shrink it when f should explain only part of the variance.
- **Noise.** `HalfNormal` on the observation scale, as for any regression.
- Fix the kernel family before fitting: squared exponential for very smooth functions, Matérn
  3/2 or 5/2 (`hsgp_matern`, `nu=1.5` or `nu=2.5`) for rougher ones, periodic for seasonal terms.
  Compare kernel families with LOO ([model-comparison.md](model-comparison.md)).

## Exact GP template

```python
import jax
import jax.numpy as jnp
import numpy as np
import numpyro
import numpyro.distributions as dist
from numpyro.infer import MCMC, NUTS

numpyro.enable_x64()  # GP covariance algebra loses accuracy in float32

rng = np.random.default_rng(0)
x_gp = np.sort(rng.uniform(0, 10, 30))
y_gp = np.sin(x_gp) + rng.normal(0, 0.2, x_gp.shape[0])


def rbf_kernel(xa, xb, amplitude, length_scale):
    sq_dist = (xa[:, None] - xb[None, :]) ** 2
    return amplitude**2 * jnp.exp(-0.5 * sq_dist / length_scale**2)


def gp_model(x, y=None):
    length_scale = numpyro.sample('length_scale', dist.InverseGamma(5.0, 5.0))
    amplitude = numpyro.sample('amplitude', dist.HalfNormal(1.0))
    noise = numpyro.sample('noise', dist.HalfNormal(0.5))
    cov = rbf_kernel(x, x, amplitude, length_scale) + (noise**2 + 1e-6) * jnp.eye(x.shape[0])
    numpyro.sample('y_gp', dist.MultivariateNormal(jnp.zeros(x.shape[0]), covariance_matrix=cov), obs=y)


gp_mcmc = MCMC(NUTS(gp_model), num_warmup=300, num_samples=300, num_chains=1, progress_bar=False)
gp_mcmc.run(jax.random.PRNGKey(1), x_gp, y=y_gp)
gp_draws = gp_mcmc.get_samples()
```

The `1e-6` jitter keeps the Cholesky factorization stable. Replace the `InverseGamma(5.0, 5.0)`
with one tuned to your input spacing and range (see the priors section). The template uses one
chain to stay short; a real fit uses four (SKILL.md, step 5).

## Hilbert-space approximation (HSGP)

HSGP replaces the n×n covariance with m basis functions per input dimension on a box
[-L, L] around the centred inputs (Solin and Särkkä 2020; Riutort-Mayol et al. 2023). Two
settings control it:

- **Boundary `ell`** (L): a factor c times the largest absolute centred input. Use c of at least
  1.2; 1.5 is a safe start.
- **Basis size `m`**: more functions are needed as the length-scale gets shorter relative to L.
  Check the choice by refitting with a larger `m`: if the posterior of f or the length-scale
  moves, `m` was too small.

```python
import jax
import jax.numpy as jnp
import numpy as np
import numpyro
import numpyro.distributions as dist
from numpyro.contrib.hsgp.approximation import hsgp_squared_exponential
from numpyro.infer import MCMC, NUTS, Predictive

numpyro.enable_x64()  # in float32 this fit diverges on most draws

rng = np.random.default_rng(0)
x_big = np.sort(rng.uniform(0, 10, 2000))
y_big = np.sin(x_big) + rng.normal(0, 0.2, x_big.shape[0])
x_shift = x_big.mean()
x_center = x_big - x_shift  # HSGP's box is centred on 0
boundary = 1.5 * float(np.abs(x_center).max())  # c = 1.5


def hsgp_model(x, y=None, ell=boundary, m=30):
    length_scale = numpyro.sample('length_scale', dist.InverseGamma(5.0, 5.0))
    amplitude = numpyro.sample('amplitude', dist.HalfNormal(1.0))
    noise = numpyro.sample('noise', dist.HalfNormal(0.5))
    f = hsgp_squared_exponential(x=x, alpha=amplitude, length=length_scale, ell=ell, m=m)
    numpyro.deterministic('f', f)
    with numpyro.plate('obs_gp', x.shape[0]):
        numpyro.sample('y_hsgp', dist.Normal(f, noise), obs=y)


hsgp_mcmc = MCMC(NUTS(hsgp_model), num_warmup=500, num_samples=300, num_chains=1, progress_bar=False)
hsgp_mcmc.run(jax.random.PRNGKey(2), x_center, y=y_big, extra_fields=('diverging',))
n_divergent = int(hsgp_mcmc.get_extra_fields()['diverging'].sum())
assert n_divergent == 0, n_divergent

# Predict at new inputs: apply the same shift, and keep `ell` and `m` unchanged.
x_new = np.linspace(0, 10, 50) - x_shift
f_new = Predictive(hsgp_model, hsgp_mcmc.get_samples())(jax.random.PRNGKey(3), x_new)['f']
assert f_new.shape == (300, 50), f_new.shape  # f recomputed at x_new, not reused
```

For a Matérn kernel use `hsgp_matern(x=x, nu=1.5, alpha=amplitude, length=length_scale,
ell=ell, m=m)`. For D > 1, pass `x` with shape (n, D) and a list for `ell` and `m`. The
functions sample an internal site named `beta` (the basis weights), so do not name a site of
your own `beta` in the same model.

## Off-stack GP libraries

GPyTorch (PyTorch) and tinygp (JAX) are outside this skill's stack: name them only when the
user's project already uses them. Sparse variational GPs (inducing points) are not covered here.
````

- [x] **Step 3: Repoint the SKILL.md row.** In `skills/bayesian-workflow/SKILL.md`, replace the line

```text
| Gaussian processes | GP prior over the latent function | Kernel hyperpriors (lengthscale, amplitude) | [references/priors.md](references/priors.md) |
```

with

```text
| Gaussian processes | Exact GP (`MultivariateNormal` over the inputs) for small n; HSGP (`numpyro.contrib.hsgp.approximation`) for large n in 1–3 input dims | `InverseGamma` on the length-scale, `HalfNormal` on the amplitude | [references/gaussian-processes.md](references/gaussian-processes.md) |
```

- [x] **Step 4: Run the checks.** Run each, from the worktree root:

```bash
grep -c 'references/gaussian-processes.md' skills/bayesian-workflow/SKILL.md
uv run --python 3.13 python build/check_snippets.py skills/
```

Expected: `1`, then exit 0. Then run CLAUDE.md's Tier 2 command and its Tier 3 command, each with the path `skills/bayesian-workflow/` (copy them from CLAUDE.md's "Snippet gate" block; do not retype versions). Expected: both exit 0. Then confirm both new blocks are in the executed set:

```bash
uv run --python 3.13 python -c "
import sys; sys.path.insert(0, 'build'); import check_snippets as c; from pathlib import Path
p = Path('skills/bayesian-workflow/references/gaussian-processes.md')
print([c._unrunnable_reason(b) for b in c.iter_code_blocks(p.read_text())])"
```

Expected: `['', '']`.

- [x] **Step 5: Re-measure the snippet docstring.** `build/snippet_preamble.py:15-22` states block counts "Measured against the skill on 2026-10-19". Recount with the same method (all fenced python blocks under `skills/bayesian-workflow/`, how many parse, how many are norun-exempt, advisory by reason, and executed). Expected change: +2 blocks, +2 parse, +2 executed, 0 new advisories. Update the date and numbers in place.

> Deviation: the docstring was already one block stale at the base (79/35 against a measured 80/36, after the SVI commit 8a33e61); it now reads 82 blocks, 82 parse, 38 executed.

- [x] **Step 6: NOTICE.** In NOTICE's bayesian-workflow paragraph, after the sentence ending "the skill reproduces no text and bundles no copies of any of them." (`:68-71`), add:

```text
    references/gaussian-processes.md cites Solin and Särkkä (2020) and
    Riutort-Mayol et al. (2023) for the Hilbert-space approximation, by
    author-year only and in original wording; its examples are original
    and were run against the snippet gate's pinned NumPyro.
```

Then run `uv run --python 3.13 python build/check_provenance.py`. Expected: exit 0.

- [x] **Step 7: Lints and commit.**

> Deviation: every commit in this run ends with `Co-Authored-By: Claude Sonnet 5.5`, the session trailer, not the Opus text the plan names.

```bash
build/run_commit_lints.sh
git add skills/bayesian-workflow/references/gaussian-processes.md skills/bayesian-workflow/SKILL.md build/snippet_preamble.py NOTICE
git commit -m "feat(bayesian-workflow): add a Gaussian-process reference with HSGP"
```

---

### Task 2: Point rpm's GP family at the new reference

Item (G11), rpm half: "make rpm name it as the default, mark GPyTorch and tinygp off-stack, and drop PyMC. A path citation from rpm needs a DEPENDENCIES or SOFT_REFERENCES entry." Done when (whole item): "the reference exists with runnable examples and both skills point at it."

**Files:**
- Modify: `skills/recommend-probabilistic-model/references/families/gaussian-processes.md:13` (Sparse row), `:25` (Handoff)
- Modify: `build/test_runtime_support.py:478-` (`SOFT_REFERENCES`), under Q4 (a)

**Interfaces:**
- Consumes: `skills/bayesian-workflow/references/gaussian-processes.md` (Task 1).

- [x] **Step 1: Failing check.**

```bash
grep -c 'PyMC' skills/recommend-probabilistic-model/references/families/gaussian-processes.md
```

Expected: `1`.

- [x] **Step 2: Sparse row.** In the "Sparse / scalable GP" row, replace the cell text `Inducing-point (SVGP) approximation, O(nm²); use GPyTorch for GPU MVM-based inference` with:

```text
In-stack: HSGP (Hilbert-space basis functions) for 1–3 input dimensions, O(n·m^D). Inducing-point (SVGP) approximation, O(nm²), for higher D; GPyTorch and tinygp implement it but are off-stack
```

Keep the row's PML and pyprobml cells unchanged.

- [x] **Step 3: Handoff.** Replace the first sentence of `## Handoff`,

```text
Route to **bayesian-workflow / GPyTorch** for fitting (GPyTorch for scalable GPU inference; PyMC/NumPyro for fully-Bayesian hyperparameter treatment). C4 memo payload if Bayesian:
```

with (Q4 a):

```text
Route to **bayesian-workflow** for fitting. Its GP reference, `bayesian-workflow/references/gaussian-processes.md`, is the default template: an exact GP for small n, HSGP for large n in 1–3 input dimensions, with full posteriors over the kernel hyperparameters. GPyTorch and tinygp are off-stack: name them only when the user's project already uses them. C4 memo payload if Bayesian:
```

Under Q4 (c), write `bayesian-workflow's GP reference` in place of the backticked path and skip Step 4.

- [x] **Step 4: SOFT_REFERENCES.** Run the drift test first to see it fail:

```bash
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies; cd ..
```

Expected: FAIL, naming `('skill:recommend-probabilistic-model', 'skill:bayesian-workflow')`. Then add to `SOFT_REFERENCES` in `build/test_runtime_support.py`, keeping the alphabetical order by source (after the existing `recommend-probabilistic-model` entry):

```python
  # Points the fitting session at bayesian-workflow's GP reference; never reads it.
  ('skill:recommend-probabilistic-model', 'skill:bayesian-workflow'),
```

Under Q4 (b), add `'skill:bayesian-workflow'` to `install.py`'s `DEPENDENCIES` entry for `'skill:recommend-probabilistic-model'` instead (create the entry if absent).

- [x] **Step 5: Run the checks.**

```bash
grep -c 'PyMC' skills/recommend-probabilistic-model/references/families/gaussian-processes.md
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py; cd ..
uv run --python 3.13 python /Users/lowell/Projects/agent-skills/build/verify_citations.py skills/recommend-probabilistic-model/; echo "gate A exit=$?"
```

Expected: `0`; all pass; `gate A exit=0`.

- [x] **Step 6: Lints and commit.**

```bash
build/run_commit_lints.sh
git add skills/recommend-probabilistic-model/references/families/gaussian-processes.md build/test_runtime_support.py
git commit -m "feat(recommend-probabilistic-model): default GP handoff to bayesian-workflow's reference"
```

---

### Task 3: bayesian-workflow siblings block, scope and description

Item (G12), Done when: "the block and the scope sentence land, the description edit is micro-tested, and the owner's Pyro call is recorded."

**Files:**
- Modify: `skills/bayesian-workflow/SKILL.md` (insert after the paragraph ending "…covered in [references/jax-numerics.md](references/jax-numerics.md)." at `:42`, before `## Installation`; description `:3-12`)
- Modify: `skills/bayesian-workflow/references/reporting.md:93-98` ("Data and Question" table), under Q6 (a)
- Create: `specs/verification/64-routing-microtests.md`
- Kit: Appendix A

**Interfaces:**
- Produces: the micro-test kit `~/.cache/agent-skills/scratch/plan64-micro/` (`run_arm.py`, `grade.py`), reused by Tasks 5 and 6; the record file, which Tasks 5 and 6 append to.

- [x] **Step 1: Record the baseline commit and build the kit.** Run `git rev-parse HEAD` and note it as `BASE3`. Create the kit from Appendix A (both scripts and `M1.json`).

- [x] **Step 2: Pilot and baseline arm.** Run the pilot (Appendix A). Expected: the init record's `tools` is `[]` and no MCP server is listed. Then run arm B (baseline): `P64_REPO=$PWD uv run ~/.cache/agent-skills/scratch/plan64-micro/run_arm.py --test M1 --arm B --base $BASE3`. Grade it with `grade.py --test M1 --arm B`.

- [x] **Step 3: Insert the siblings block.** Insert this section between the numerics paragraph (`:42`) and `## Installation`. It shows the Q2 (a) scope sentence; under Q2 (b) use the item's sentence instead: "NUTS posterior inference is in scope, Bayesian neural networks included when posterior inference is the task; SVI-only fits are not."

```markdown
## Scope and sibling skills

This skill fits by NUTS posterior inference; SVI is a warm start, or the final fit only under the checks in [references/svi.md](references/svi.md). Bayesian neural networks are in scope when posterior inference is the task.

- Upstream: explore-data profiles the data; recommend-probabilistic-model picks the model family; recommend-causal-design picks the design and the estimand for a causal question.
- Downstream: validate-data gates a result before it leaves; track-model-experiments keeps the ledger of fitted model variants and compares them.
- Not here: point-estimate neural training (deep-learning) and JAX speed, memory or compilation problems (optimize-jax).
```

- [x] **Step 4: Edit the description.** In the frontmatter description, under Q1 (a) replace `Pyro, BlackJAX` with `BlackJAX` (under Q1 (b) leave it). In all cases replace `or uncertainty quantification.` with `or posterior uncertainty.` Keep the YAML folding (lines under 100 characters).

> Deviation: bayesian-workflow's description also gained "NumPyro only; Pyro/PyTorch fits go elsewhere." (801 characters, not 755). The first candidate (C1) failed M1 bar 1 on probe B1 (2 of 5 reps); the owner approved the reword in chat and arm C was rerun (C2, 0 of 5). Both candidates are in the record.

- [x] **Step 5: Estimand row (Q6 a).** In `references/reporting.md`'s "Data and Question" table, after the `| Question | … |` row, add:

```text
| Estimand (if causal) | <the causal quantity and population, e.g. ATT for treated counties; the identifying design from recommend-causal-design> |
```

- [x] **Step 6: Placement and dependency checks.**

```bash
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py -k test_real_skill; cd ..
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies; cd ..
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
```

Expected: all pass. If the critical-span test fails, the block is too long: shorten it, do not move it below `## Common gotchas`. The `references/svi.md` link is inside the skill and adds no edge.

- [x] **Step 7: Candidate arm and record.** Run arm C (`--arm C --base $BASE3`, same command), grade it, and check the pass bars in `M1.json`. Write `specs/verification/64-routing-microtests.md` in the form of `specs/verification/59-regime-b-router-microtest.md`: date, model, Claude Code version (`claude --version`), kit path, cost; design; scenarios and pass bars (copied from `M1.json`, written before any run); results table; a per-rep table with a quote of at most 15 words; the isolation screen from `grade.py`. Record Q1's answer in the record's first paragraph. If a bar fails, stop and bring the failing reps to the owner; do not reword and rerun without the owner's go-ahead.

> Deviation: see Step 4: the stop rule fired once and the owner approved one reword; the record documents C1 and C2.

- [x] **Step 8: Lints and commit.**

```bash
build/run_commit_lints.sh
git add skills/bayesian-workflow/SKILL.md skills/bayesian-workflow/references/reporting.md specs/verification/64-routing-microtests.md
git commit -m "feat(bayesian-workflow): add a siblings block and scope; narrow the description"
```

---

### Task 4: Route four model classes in rpm

Item (G10), Done when: "each class routes to a family note with verified citations."

**Files:**
- Modify: `skills/recommend-probabilistic-model/references/decision-map.md` (task table `:11-22`, signal table `:28-41`)
- Modify: `skills/recommend-probabilistic-model/references/families/regression-glm.md` (methods table, gotchas, handoff)
- Create: `skills/recommend-probabilistic-model/references/families/survival.md`
- Modify: `skills/recommend-probabilistic-model/SKILL.md` (reference map: "per-family depth (8)" → "(9)")
- Modify: `NOTICE` (rpm paragraph, after the pyprobml/dynamax bullet ending `:207`), under Q3 (a)

**Interfaces:**
- Produces: `families/survival.md`, and the four class names that Task 5's description adds ("ordinal, proportion, quantile and censored or time-to-event outcomes").

- [x] **Step 1: Failing check.**

```bash
grep -r -i -c -E 'surviv|censor|ordinal|quantile regression|beta regression' skills/recommend-probabilistic-model/ | grep -v ':0$' | wc -l
```

Expected: `0` (the item's re-verified grep).

- [x] **Step 2: Find and Gate-B-read the PML sections.** For each class, search the local index from the main checkout:

```bash
grep -n -i -E 'ordinal|censor|surviv|hazard|quantile|pinball|beta|bounded|proportion' /Users/lowell/Projects/agent-skills/build/.scratch/book1_sections.tsv /Users/lowell/Projects/agent-skills/build/.scratch/book2_sections.tsv
```

Known at planning: PML2 §15.4.4 is titled for ordinal probit regression. For each candidate section, read its text in `book{1,2}_full.txt` and confirm it supports the claim the row makes (Gate B). Use a §-ref only when it does. Do not copy any of that text into the repo, the plan, the record or a commit message. List each accepted and rejected ref, with one line of your own words on why, in the commit message body.

- [x] **Step 3: Decision-map rows.** In `decision-map.md`, add this row to the task table after the "Outcome indexed by time" row:

```text
| Time until an event, with some subjects not yet observed to have it (censored) | Survival & time-to-event | `families/survival.md` |
```

Add these rows to the signal table after the "Continuous target, heavy tails / outliers" row:

```text
| Target is an ordered category (ratings, grades, stages) | Ordinal regression (cumulative logit / probit) | regression-glm |
| Target bounded in (0, 1): a proportion or rate | Beta regression; BetaBinomial for k-of-n counts | regression-glm |
| Question is about a quantile or the whole conditional distribution, not the mean | Quantile / distributional regression | regression-glm |
| Durations, some still running or lost to follow-up | Censored likelihood: AFT / piecewise-exponential | survival |
```

- [x] **Step 4: regression-glm rows.** Append three rows to the methods table (after "Zero-inflated (ZIP) / hurdle"). Fill each PML cell with the refs Step 2 accepted, formatted `PML1 §x / PML2 §y`, or `—`. Fill the pyprobml cell only with a path present in `/Users/lowell/Projects/agent-skills/build/.scratch/pyprobml_files.txt`, else `—`. Under Q3 (a), name the non-PML source in the "Default recommendation" cell as shown:

> Deviation: only PML2 §15.4.4 (ordinal), PML2 §14.3.2.1 and PML1 §13.2.4.4 (quantile and distributional) passed Gate B; the Beta and all survival PML cells are "—", and every new pyprobml cell is "—".

```text
| Ordinal regression (cumulative logit / probit) | Ordered categories where gaps between levels are unknown | One latent continuous score cut by ordered thresholds; proportional-odds (cumulative logit) is the default (McCullagh 1980). Never treat the levels as equally spaced numbers | <PML cell> | <pyprobml cell> |
| Beta / BetaBinomial regression | Target is a proportion in (0, 1), or k successes of n trials with extra variation | Beta likelihood with a logit-linked mean and a precision parameter (Ferrari and Cribari-Neto 2004); BetaBinomial when you have the counts. Exact 0s or 1s need a zero/one-inflated variant | <PML cell> | <pyprobml cell> |
| Quantile / distributional regression | The decision depends on a tail or a quantile, or predictors change the spread as well as the mean | Quantile regression fits one conditional quantile with the check (pinball) loss (Koenker and Bassett 1978); distributional regression models the mean and the scale (or shape) each as a function of predictors | <PML cell> | <pyprobml cell> |
```

Add these bullets to `## Gotchas`:

```text
- **Ordinal is not metric.** Coding a 1–5 rating as a number assumes equal gaps and can reverse effect signs; fit the ordinal model, then report predicted category probabilities.
- **Boundaries break Beta.** A proportion of exactly 0 or 1 has zero density under Beta; use the counts (BetaBinomial) or an inflated model rather than squeezing the data inward.
- **Separate quantile fits can cross.** Quantile curves fitted one at a time can cross; fit them jointly or check monotonicity before you report intervals.
```

Append to `## Handoff` (as a new last paragraph):

```text
Bayesian fits of these three go to **bayesian-workflow**: `OrderedLogistic` (ordinal), `Beta` / `BetaProportion` / `BetaBinomial` (bounded), `AsymmetricLaplaceQuantile` (one quantile). Frequentist alternatives: statsmodels `OrderedModel`, statsmodels `QuantReg`, sklearn's `QuantileRegressor` or gradient boosting with a quantile loss.
```

- [x] **Step 5: Survival family file.** Create `families/survival.md`. Its sections follow the other family files exactly: a "When this family fits" line, `## Methods & defaults`, `## Selection & regularization (Step 6, family-specific)`, `## Gotchas`, `## Handoff`. Fill the PML cells per Step 2's verdicts (`—` when none):

````markdown
# Survival & time-to-event

**When this family fits:** The outcome is the time until an event (churn, failure, job exit, death), and for some subjects the event has not happened yet when observation stops (right-censoring), or happened at an unknown time inside a window (interval-censoring). Dropping the censored subjects, or treating their last-seen time as the event time, biases durations downward.

## Methods & defaults

| Method | Use when | Default recommendation | PML §ref (Book 1 / Book 2) | pyprobml |
|--------|----------|------------------------|----------------------------|----------|
| Censored parametric likelihood (Weibull / LogNormal / Gamma) | A smooth hazard shape is plausible; you want predictions of whole duration distributions | Start here for a Bayesian fit: the censored subjects contribute their survival probability past the censoring time, the observed ones their density (Kalbfleisch and Prentice 2002) | <PML cell> | <pyprobml cell> |
| Accelerated failure time (AFT) | Predictors should stretch or shrink time | Log-time is linear in predictors with a Weibull, LogNormal or log-logistic error; coefficients read as time ratios | <PML cell> | <pyprobml cell> |
| Piecewise-exponential (Poisson trick) | The hazard shape is unknown or changes over time; time-varying predictors | Split time into intervals with a constant hazard each; fits as a Poisson GLM with a log-exposure offset, so hierarchical and spline priors carry over | <PML cell> | <pyprobml cell> |
| Cox proportional hazards | Only relative risks matter and the baseline hazard is a nuisance | The frequentist default (partial likelihood); check proportional hazards before reporting one hazard ratio | <PML cell> | <pyprobml cell> |

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
````

- [x] **Step 6: Family count.** In rpm `SKILL.md`'s reference map, replace `per-family depth (8)` with `per-family depth (9)`.

- [x] **Step 7: NOTICE (Q3 a).** In NOTICE's rpm paragraph, after the pyprobml/dynamax bullet (ends "the skill links to them.", `:207`), add:

```text
  - The survival, ordinal, bounded-outcome and quantile rows also cite
    Kalbfleisch and Prentice (2002), McCullagh (1980), Ferrari and
    Cribari-Neto (2004) and Koenker and Bassett (1978) by author-year
    only, in original wording; no text is reproduced.
```

Under Q3 (b), skip this step and remove the author-year names from Steps 4 and 5.

- [x] **Step 8: Verify.**

```bash
grep -r -i -c -E 'surviv|censor|ordinal|quantile regression|beta regression' skills/recommend-probabilistic-model/ | grep -v ':0$' | wc -l
uv run --python 3.13 python /Users/lowell/Projects/agent-skills/build/verify_citations.py skills/recommend-probabilistic-model/; echo "gate A exit=$?"
uv run --python 3.13 python build/check_provenance.py
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies; cd ..
uv run --python 3.13 --with numpy --with polars python build/smoke_test.py
```

Expected: a non-zero count; `gate A exit=0` (WARN lines on stderr for chapter fallbacks are Gate B worklist items: each must be one Step 2 read); provenance exit 0; drift test passes; smoke test passes.

- [x] **Step 9: Lints and commit.** Put Step 2's accepted and rejected refs in the commit body.

```bash
build/run_commit_lints.sh
git add skills/recommend-probabilistic-model/ NOTICE
git commit -m "feat(recommend-probabilistic-model): route survival, ordinal, bounded and quantile outcomes"
```

---

### Task 5: Wire rpm to the skills that arrived after it

Item (G10 causal part, I2, I3), Done when: "the pointers land and the micro-test record is kept." This task also carries Task 4's description terms, so rpm's description changes once and is micro-tested once.

**Files:**
- Modify: `skills/recommend-probabilistic-model/SKILL.md` (description `:3-13`; sibling list `:31-37`; Step 1 `:41-43`)
- Modify: `skills/recommend-probabilistic-model/references/reporting.md:52-56` (memo §8; do NOT edit `:54`)
- Modify: `skills/recommend-probabilistic-model/references/families/graphical-models.md` (GNN row `:13`; Handoff `:25`)
- Modify: `skills/recommend-probabilistic-model/references/families/classification.md` (deep-ensemble row `:15`; Handoff)
- Modify: `specs/verification/64-routing-microtests.md` (append M2)

**Interfaces:**
- Consumes: the kit and record from Task 3; Task 4's class names.

- [x] **Step 1: Baseline.** Note `BASE5=$(git rev-parse HEAD)`. Write `M2.json` (Appendix A). Run and grade arm B.

- [x] **Step 2: Description.** In the description, replace `Covers regression / GLMs / counts, classification,` with `Covers regression / GLMs / counts, ordinal, proportion, quantile and censored or time-to-event outcomes, classification,` and append the sentence `A causal-effect question goes to recommend-causal-design first.` at the end. Re-fold lines under 100 characters. Measured at planning: 1,005 characters. Run `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py`; expected exit 0.

- [x] **Step 3: Siblings.** In `## This skill vs. its siblings`, add after the `bayesian-workflow` bullet:

```text
- **`recommend-causal-design`** comes first when the question is causal (did X change Y): it picks the design and the estimand, and returns here only for the outcome model inside that design.
- **`deep-learning`** *trains* neural models when the recommendation is a network (GNN, deep ensemble); **`evaluate-deep-learning`** compares them; **`optimize-jax`** fixes JAX speed, memory or compilation problems.
- **`tune-hyperparameters`** searches a model's knobs (regularization, depth, learning rate, inference settings) without leaking the future.
- **`track-model-experiments`** keeps the ledger of fitted model variants and compares them.
```

- [x] **Step 4: Step 1.** In Procedure step 1, after `inference vs. causal vs. sequential decision).` add: ` A causal question goes to recommend-causal-design before this procedure continues.`

- [x] **Step 5: Memo template.** In `references/reporting.md`'s `## 8. Next steps / handoff`, add after the `**Bracketing skills:**` line (leave `**Runs next:**` untouched):

```text
- **Iterate:** <tune-hyperparameters to search the knobs from §5; track-model-experiments to log and compare the fitted variants>
```

- [x] **Step 6: Neural hand-offs.** In `graphical-models.md`'s Graph neural network row, append to the "Default recommendation" cell: `; build and train it with deep-learning, compare variants with evaluate-deep-learning`. In its `## Handoff`, add the sentence: `A graph neural network goes to deep-learning (evaluate-deep-learning for comparisons), not bayesian-workflow.` In `classification.md`'s Deep ensembles row, append to the "Default recommendation" cell: `; train with deep-learning, compare with evaluate-deep-learning`. In its `## Handoff`, add: `Deep ensembles and other neural classifiers go to deep-learning (evaluate-deep-learning for comparisons).`

- [x] **Step 7: Checks.**

```bash
grep -c 'recommend-causal-design' skills/recommend-probabilistic-model/SKILL.md
grep -l 'deep-learning' skills/recommend-probabilistic-model/references/families/graphical-models.md skills/recommend-probabilistic-model/references/families/classification.md
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies; cd ..
uv run --python 3.13 python /Users/lowell/Projects/agent-skills/build/verify_citations.py skills/recommend-probabilistic-model/; echo "gate A exit=$?"
```

Expected: `3` or more; both files; pass (bare names add no edge); `gate A exit=0`.

- [x] **Step 8: Candidate arm and record.** Run and grade arm C; check M2's bars; append an "M2: recommend-probabilistic-model" section to the record in the same form. Same stop rule as Task 3.

> Deviation: arm B already routed all six scenarios correctly, so bar 2 was vacuous and M2 shows no regression but no gain.

- [x] **Step 9: Lints and commit.**

```bash
build/run_commit_lints.sh
git add skills/recommend-probabilistic-model/ specs/verification/64-routing-microtests.md
git commit -m "feat(recommend-probabilistic-model): route causal, neural and lifecycle siblings"
```

---

### Task 6: creative-thinking hand-offs

Item (G14, I2), Done when: "the hand-offs land, with any description change micro-tested."

**Files:**
- Modify: `skills/creative-thinking/SKILL.md` (description `:3-10`, under Q5 (a); "Scope and handoff" list `:112-124`)
- Modify: `specs/verification/64-routing-microtests.md` (append M3, under Q5 (a))

- [x] **Step 1: Baseline.** `BASE6=$(git rev-parse HEAD)`. Under Q5 (a), write `M3.json` (Appendix A); run and grade arm B.

- [x] **Step 2: Body.** In `## Scope and handoff`, replace the bullet beginning `- A picked target that is an objective to search over goes to` with:

```text
- A picked target that is an objective to search over goes to
  tune-hyperparameters; a defined question choosing a model family goes to
  recommend-probabilistic-model; a defined dataset choosing a chart goes
  to recommend-visualization.
- A picked target that is a causal question (did X change Y, for whom)
  goes to recommend-causal-design, which fixes the estimand and the
  design before any model is chosen.
- A picked target that a neural model must learn goes to deep-learning;
  comparing neural models goes to evaluate-deep-learning.
```

- [x] **Step 3: Description (Q5 a).** Append to the description: ` Causal question to frame: recommend-causal-design. Neural target: deep-learning.` (576 characters at planning). Run `check_frontmatter.py`; expected exit 0.

- [x] **Step 4: Checks.**

```bash
grep -c -E 'recommend-causal-design|deep-learning' skills/creative-thinking/SKILL.md
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies; cd ..
```

Expected: 3 or more (2 without Q5 a); pass.

- [x] **Step 5: Candidate arm and record (Q5 a).** Run and grade arm C; check M3's bars; append "M3: creative-thinking" to the record. Same stop rule.

> Deviation: same as M2: arm B failed nothing. T1 moved from creative-thinking (3 of 5) to recommend-causal-design (4 of 5), both accepted.

- [x] **Step 6: Final checks, lints and commit.** Run the whole set once:

> Deviation: the three descriptions grew +250 characters folded (bayesian-workflow +35, rpm +134, creative-thinking +81), not +202, because of the C2 phrase. Total micro-test cost $6.22 of the $25 cap. After the tasks, the final review (an Opus code-reviewer and a Codex review, `Codex reviewed 944ac33`) led to two fix commits, f17791d and 326e0b9. With the owner's approval they corrected four wording errors in text this plan dictated (survival.md's "as the mask" and AFT row, the InverseGamma tail claim, the exact-GP LOO caveat) and the tinygp claim, and added the README, bibliography and record fixes.

```bash
uv run --python 3.13 python build/check_snippets.py skills/
cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py test_check_conformance.py; cd ..
build/run_commit_lints.sh
git add skills/creative-thinking/SKILL.md specs/verification/64-routing-microtests.md
git commit -m "feat(creative-thinking): hand off causal and neural targets"
```

Expected: all pass. Then report total micro-test cost against the Q8 cap, and the three descriptions' total character change (+202 at planning: rpm +133, bayesian-workflow −11, creative-thinking +80; the owner judges the skill-listing budget headroom).

---

## Completion notes (for the Plan Completion Protocol)

At step 3 of the protocol, append these to `specs/deferred_items.md` under a `## 64-bayesian-rpm-routing` section (owner's call at the completion gate whether either is resolved instead):

- Add a survival row to rpm's per-family knob table (`skills/recommend-probabilistic-model/references/model-selection-regularization.md`, "Per-family knobs"). Plan 64 created `families/survival.md` but left the table alone, since the model-lifecycle spec (`specs/model-lifecycle.md`, R12a) owns it and was written before the survival family existed. Size: quick-fix. Done when: the table has a survival row matching `families/survival.md`'s "Selection & regularization" subsection.
- Add Beta / BetaBinomial and quantile (`AsymmetricLaplaceQuantile`) rows to bayesian-workflow's "Common model families" table (`skills/bayesian-workflow/SKILL.md`), which rpm's bounded and quantile handoffs now point at. Size: quick-fix. Done when: both rows land with a priors pointer.

## Appendix A: Routing micro-test kit

Kit folder: `~/.cache/agent-skills/scratch/plan64-micro/` (outside the repo; never committed). Each rep is one decision-only `claude -p` call with no tools, run from its own new folder under `/tmp/p64micro/`, with the isolation recipe from the micro-test notes: `--tools ""`, `--strict-mcp-config`, `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`, and a pilot that reads the init record's `tools`. The prompt lists the competing skills' descriptions. Arm B uses every description at the baseline commit. Arm C differs only in the edited skill's description, read from the working tree.

**Verdicts.** A scenario with a `pass` list passes a rep whose SKILL is in the list. A collision probe with a `fail` list fails a rep only when its SKILL is in that list (the edited skill stealing the request); any other pick passes. Each collision probe contains the trigger term its edit removes or adds.

**Pass bars (all tests, fixed before any run).** Arm C meets the bar when (1) on every scenario it fails at most 1 of 5 reps, and (2) on every scenario where arm B fails 2 or more of 5, arm C fails fewer than arm B. A rep that errors or refuses is void: rerun it and count the voids.

`run_arm.py`:

```python
# /// script
# requires-python = '>=3.13'
# dependencies = ['pyyaml']
# ///
'''Plan 64 routing micro-test: one decision-only `claude -p` call per rep.'''
import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

import yaml

KIT = Path(__file__).parent
REPO = Path(os.environ['P64_REPO'])
SCRATCH = Path('/tmp/p64micro')
PROMPT = '''You route a user's request to one skill. The skills are:

{catalog}

Request: {request}

Answer with exactly two lines and nothing else:
SKILL: <one skill name from the list, or none>
REASON: <one sentence>'''


def skill_text(skill, rev):
    if rev == 'WORKTREE':
        return (REPO / 'skills' / skill / 'SKILL.md').read_text()
    return subprocess.run(['git', '-C', str(REPO), 'show', f'{rev}:skills/{skill}/SKILL.md'],
                          check=True, capture_output=True, text=True).stdout


def description(skill, rev):
    front = skill_text(skill, rev).split('---')[1]
    return ' '.join(yaml.safe_load(front)['description'].split())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', required=True)
    parser.add_argument('--arm', required=True, choices=['B', 'C'])
    parser.add_argument('--base', required=True)
    parser.add_argument('--reps', type=int, default=5)
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    spec = json.loads((KIT / f'{args.test}.json').read_text())
    revs = {s: ('WORKTREE' if args.arm == 'C' and s == spec['edited'] else args.base) for s in spec['catalog']}
    catalog = '\n'.join(f'- {s}: {description(s, revs[s])}' for s in spec['catalog'])
    out = KIT / 'raw' / args.test / ('pilot' if args.pilot else args.arm)
    out.mkdir(parents=True, exist_ok=True)
    SCRATCH.mkdir(exist_ok=True)
    env = {**os.environ, 'CLAUDE_CODE_DISABLE_ADVISOR_TOOL': '1'}
    fmt = ['--output-format', 'stream-json', '--verbose'] if args.pilot else ['--output-format', 'json']
    scenarios = spec['scenarios'][:1] if args.pilot else spec['scenarios']
    reps = 1 if args.pilot else args.reps
    for scenario in scenarios:
        prompt = PROMPT.format(catalog=catalog, request=scenario['request'])
        for rep in range(1, reps + 1):
            cwd = tempfile.mkdtemp(dir=SCRATCH)
            cmd = ['claude', '-p', '--model', 'sonnet', '--tools', '', '--strict-mcp-config', *fmt, prompt]
            proc = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=300)
            (out / f'{scenario["id"]}-{rep}.json').write_text(proc.stdout)
            if args.pilot:
                init = next(json.loads(line) for line in proc.stdout.splitlines()
                            if '"subtype":"init"' in line.replace(' ', ''))
                print('tools:', init.get('tools'), 'mcp_servers:', init.get('mcp_servers'))


if __name__ == '__main__':
    main()
```

`grade.py`:

```python
# /// script
# requires-python = '>=3.13'
# ///
'''Tabulate a plan 64 arm: verdicts, a short quote, cost, and the isolation screen.'''
import argparse
import json
import re
from pathlib import Path

KIT = Path(__file__).parent
QUOTE_WORDS = 15


def verdict(skill, scenario):
    if skill == 'VOID':
        return 'VOID'
    if 'fail' in scenario:
        return 'FAIL' if skill in scenario['fail'] else 'PASS'
    return 'PASS' if skill in scenario['pass'] else 'FAIL'


def screen(record):
    '''One turn, no error, message iterations only (no tool or advisor call), one model.'''
    kinds = {i.get('type') for i in record.get('usage', {}).get('iterations') or []}
    one_turn = record.get('num_turns') == 1 and not record.get('is_error')
    return 'ok' if one_turn and kinds <= {'message'} and len(record.get('modelUsage', {})) == 1 else 'SCREEN'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', required=True)
    parser.add_argument('--arm', required=True, choices=['B', 'C'])
    args = parser.parse_args()
    spec = json.loads((KIT / f'{args.test}.json').read_text())
    scenarios = {s['id']: s for s in spec['scenarios']}
    fails, voids, cost = {}, 0, 0.0
    for path in sorted((KIT / 'raw' / args.test / args.arm).glob('*.json')):
        scenario = path.stem.rsplit('-', 1)[0]
        try:
            record = json.loads(path.read_text())
        except json.JSONDecodeError:
            record = {}
        text = record.get('result', '')
        skill = (re.search(r'SKILL:\s*([\w-]+)', text) or [None, 'VOID'])[1]
        reason = ' '.join(text.split('REASON:', 1)[-1].split()[:QUOTE_WORDS])
        result = verdict(skill, scenarios[scenario])
        fails[scenario] = fails.get(scenario, 0) + (result == 'FAIL')
        voids += result == 'VOID'
        cost += record.get('total_cost_usd', 0.0)
        print(f'| {args.arm} | {path.stem} | {result} | {skill} | "{reason}" | {screen(record)} |')
    print('fails by scenario:', fails, 'voids:', voids, f'cost ${cost:.2f}')


if __name__ == '__main__':
    main()
```

Pilot (once per test, before arm B): `P64_REPO=$PWD uv run ~/.cache/agent-skills/scratch/plan64-micro/run_arm.py --test M1 --arm B --base <BASE> --pilot`. Expected: `tools: []` and no MCP server. If tools are listed, stop and fix the isolation before any arm runs. Read every FAIL and every SCREEN rep by hand; `grade.py` only tabulates.

`M1.json` (bayesian-workflow; B1 applies only under Q1 (a) — under Q1 (b) delete it before arm B):

```json
{
  "edited": "bayesian-workflow",
  "catalog": ["bayesian-workflow", "recommend-probabilistic-model", "recommend-causal-design", "deep-learning",
              "evaluate-deep-learning", "optimize-jax", "track-model-experiments", "tune-hyperparameters",
              "explore-data", "validate-data"],
  "scenarios": [
    {"id": "B1", "request": "I have a Pyro model in PyTorch with an AutoNormal guide. The SVI loss plateaus after 2,000 steps. How do I fix the training?", "fail": ["bayesian-workflow"]},
    {"id": "B2", "request": "My Flax MLP forecasts weekly demand. I need uncertainty quantification from a deep ensemble of 5 networks. Where do I start?", "fail": ["bayesian-workflow"]},
    {"id": "B3", "request": "My NumPyro hierarchical model gives 40 divergences out of 4,000 draws. What do I check first?", "pass": ["bayesian-workflow"]},
    {"id": "B4", "request": "I fitted a NumPyro logistic regression with NUTS and need credible intervals for a report to managers.", "pass": ["bayesian-workflow"]}
  ]
}
```

`M2.json` (rpm):

```json
{
  "edited": "recommend-probabilistic-model",
  "catalog": ["recommend-probabilistic-model", "bayesian-workflow", "recommend-causal-design", "creative-thinking",
              "deep-learning", "evaluate-deep-learning", "explore-data", "tune-hyperparameters",
              "track-model-experiments", "recommend-visualization"],
  "scenarios": [
    {"id": "R1", "request": "Did the 2024 minimum-wage increase cause job losses in these counties? Which model should I fit?", "pass": ["recommend-causal-design"]},
    {"id": "R2", "request": "Customer churn: I have each customer's time to cancellation, but 60% are still active. Which model family fits?", "pass": ["recommend-probabilistic-model"]},
    {"id": "R3", "request": "My outcome is a 1-5 satisfaction rating with a dozen predictors. Which model should I use?", "pass": ["recommend-probabilistic-model"]},
    {"id": "R4", "request": "I want to train a graph neural network in Flax on molecule graphs. How should I set up training?", "pass": ["deep-learning"]},
    {"id": "R5", "request": "My counts have variance 8 times the mean. Poisson or negative binomial?", "pass": ["recommend-probabilistic-model"]},
    {"id": "R6", "request": "My outcome is each county's share of workers in manufacturing, between 0 and 1. Which model fits?", "pass": ["recommend-probabilistic-model"]}
  ]
}
```

`M3.json` (creative-thinking, Q5 (a) only):

```json
{
  "edited": "creative-thinking",
  "catalog": ["creative-thinking", "brainstorming", "recommend-probabilistic-model", "recommend-causal-design",
              "deep-learning", "evaluate-deep-learning", "tune-hyperparameters", "recommend-visualization",
              "explore-data"],
  "scenarios": [
    {"id": "T1", "request": "We changed onboarding last spring and I suspect it mattered, but I can't say what effect to estimate or for whom.", "pass": ["creative-thinking", "recommend-causal-design"]},
    {"id": "T2", "request": "Did the onboarding change raise 90-day retention? We have before/after cohorts and a holdout region. Which design?", "pass": ["recommend-causal-design"]},
    {"id": "T3", "request": "Which architecture should I train in JAX for a 10,000-sequence classification task?", "pass": ["deep-learning"]},
    {"id": "T4", "request": "There's something interesting in this panel of county wages but I can't articulate the analysis.", "pass": ["creative-thinking"]},
    {"id": "T5", "request": "Poisson or negative binomial for these overdispersed counts?", "pass": ["recommend-probabilistic-model"]}
  ]
}
```
