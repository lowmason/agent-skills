# RED baseline — JAX numerics harvest into `bayesian-workflow`

**Date:** 2026-08-26 · **Status:** RED complete (scoping). GREEN not run — see Disposition.
**Governs:** which JAX-generic rules from `review/coding-skills` → `jax-equinox-numerics` and
`jax-project-engineering` are worth adding to `bayesian-workflow/references/`.

> ⚠️ **Quarantine this file during any future micro-test of `bayesian-workflow`.** It names
> the skill and states the expected failures — Channel 1 per `microtest-isolation-channels`.

## Purpose: scoping, not pass/fail

The intake review planned to harvest **two** reference files (`numerics_dtype_stability.md`,
88 lines; `jit_pytree_controlflow.md`, 280 lines) plus a demoted `equinox.md`. Rather than
port on plausibility, the baseline measured which practices agents already apply unprompted —
the same method that cut the `clean-code` module harvest from eleven rules to four.

## Fixture

`nowcast`, a Polars + NumPyro package: a `load_panel()` returning one row per (state, month)
with an observed `payroll` level and a per-row `survey_sd`. Task: implement a pooled
local-level (random walk + noise) state-space model, fit with NUTS on 4 chains, expose
`fit`/`summarize`, and run end to end. Deliberately close to `alt-nfp/packages/nfp-model`,
the code this reference would serve.

The prompt said nothing about precision, dtypes, or control flow, and the fixture contained
no JAX configuration to copy (verified by grep before dispatch). 5 reps, fresh context each.

All five produced working models that sampled cleanly — 0 divergences, R-hat ≤ 1.006. Two
went further and marginalized the latent states with hand-written Kalman filters; one added
a test pinning the filter against a closed-form MVN density. This is not low-effort output.

## Result

| Behaviour | rep1 | rep2 | rep3 | rep4 | rep5 | n/5 | Disposition |
|---|---|---|---|---|---|---|---|
| `set_host_device_count` before first JAX op | ✓ | ✓ | ✓ | ✓ | ✓ | **5/5** | already known → drop |
| `scan` for the time recursion | ✓ | ✓ | ✓ | ✓ | ✓ | **5/5** | already known → drop |
| Explicit PRNG threading / `split` | ✓ | ✓ | ✓ | ✓ | ✓ | **5/5** | already known → drop |
| **Enable x64** | – | – | – | ✓ | – | **1/5** | **keep** |
| **Explicit dtype at array boundary** | – | ✓ | – | – | – | **1/5** | **keep** |
| **Guard a division by a variance** | – | – | – | – | – | **0/5** | **keep** |
| **Nonfinite check** | – | – | ✓ | – | – | **1/5** | **keep** |

### Consequence: `jit_pytree_controlflow.md` is dropped entirely

Its three testable behaviours are 5/5 already-known. Porting 280 lines to teach `scan`, PRNG
discipline, and device counting would spend context on the already-done. `equinox.md` is
dropped too — Equinox is incidental to this stack and nothing in the baseline touched it.

The harvest reduces to the precision/stability cluster, i.e. `numerics_dtype_stability.md` —
the file that was independently the most JAX-generic (4 of 88 lines Equinox-bound).

### Note for `agent-skills-buildout` memory

That memory records `numpyro.set_host_device_count` ordering as a "verified technical gotcha".
Still true as a fact, but agents apply it **5/5 unprompted** — it does not need skill space.
Two reps wrote their own explanatory comment about the ordering requirement.

## Qualitative evidence for the x64 rule

The count understates it. The two reps doing the most precision-sensitive work — 60-step
sequential covariance recursions — both ran float32:

- One validated its filter against a closed-form MVN log-density and reported agreement
  "to ~4e-7 relative, **i.e. float32 precision**". It observed the precision and adopted it
  as the verification tolerance rather than treating it as a decision.
- Another cast boundary data to `np.float64` *without* enabling x64, so JAX discarded the
  cast one line later. The intent to work in double precision was present; the mechanism was
  not. This is the strongest single argument for the rule: care was applied and silently lost.

Neither would be caught by the tests those agents wrote — a closed-form check agrees to
float32 tolerance, R-hat is 1.00, and parameter recovery looks fine.

## Method note: three scorer false negatives, all caught by reading

The pre-registered grep patterns were wrong three times, each in the same direction —
missing a NumPyro-idiomatic form:

1. `enable_x64` — pattern matched only `jax_enable_x64`, missing `numpyro.enable_x64()`.
   Would have scored the one compliant rep as non-compliant.
2. `scan` — pattern matched `lax.scan`, missing `numpyro.contrib.control_flow.scan`. Would
   have reported a 2/5 gap where the truth is 5/5 already-known, and led to porting 280
   lines of unnecessary material.
3. `lax.scan` as a proxy for "correct recursion" — one rep used a non-centred `cumsum`
   parameterization instead, which is *better* than `scan` for a random walk. Absence of the
   pattern was not absence of the practice.

Each was caught by reading the code, per the `microtest-isolation-channels` rule to manually
read every flagged match. Automated counts alone would have produced the wrong harvest.

## Disposition

Shipped: `skills/bayesian-workflow/references/jax-numerics.md`, covering the four kept rules
plus the device/platform rule from `jax-project-engineering` (explicitly marked untested — no
fixture spanned two machines).

**GREEN not run.** This is a reference-file addition to a reference skill, which the repo
convention (`CLAUDE.md`: "pure reference skills are not [pressure-tested]") does not gate on
a GREEN arm; the RED here was for *scoping*, and it did its job. The x64 rule is behavioural
enough that a GREEN would still be informative.

**If GREEN is run later, use a different fixture.** This document and `jax-numerics.md` both
narrate the baseline in terms of a local-level state-space model with a Kalman recursion.
Re-using this fixture would reproduce the Channel-3 contamination that voided the first
`clean-code` GREEN. A hierarchical model with an LKJ/Cholesky covariance would test the same
rules on unfamiliar ground.
