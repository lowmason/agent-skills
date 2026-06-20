# Worked example: the inference-engine ADR

This is a fully-filled ADR for the decision whose *absence* motivated this skill — the same NFP
nowcast solved three ways (NumPyro/JAX in `alt-nfp`, PyMC in `alt_nfp` and `oi-indices`). Read it
as the exemplar of what "good" looks like, and copy it as a starting point for a real ADR. It is
written as a snapshot dated to when the choice was made; the bracketed notes `[like this]` are
authoring guidance, not part of the record — delete them when you adapt it.

---

# 0009. Use NumPyro/JAX over PyMC for NFP nowcasting

- **Status:** Accepted
- **Date:** 2025-11-03
- **Deciders:** Lowell Mason
- **Blast radius:** `nfp-model` (new) — the inference layer of `alt-nfp`. Establishes a deliberate
  split from the PyMC implementations in `alt_nfp` (frozen reference) and `oi-indices` (separate
  index work). Does not touch the four `nfp_*` data packages.

## Context

`alt_nfp` (v1) nowcasts US nonfarm payrolls with a PyMC state-space model. We are building `alt-nfp`
(v2), porting the data layer and **rewriting the model layer**. The backtest is the expensive part:
fitting the model independently across a grid of as-of dates D, each on a censored snapshot of what
was knowable on D. There are hundreds of such fits per backtest, and we want GPU as the speed lever.

A separate repo, `oi-indices`, also fits a related nowcast in PyMC. So as of this date the *same
class of problem is solved twice in PyMC already*; the question is what v2's engine should be — and
whether adding a third (JAX) implementation is justified rather than accidental.

Constraints that actually drive the choice, as of now:

- **Batching.** The backtest is an embarrassingly-parallel sweep over as-of dates with padded/masked
  inputs. We want one vectorized fit, not a Python loop of independent samplers.
- **GPU.** The intended A4 speed lever is GPU; the same batched code should run unmodified on CPU
  (CI) and GPU (backtests).
- **Parity.** v2 must be gated for *port fidelity* against the frozen `alt_nfp` reference — a
  statistical match enforced by golden-master fixtures. Parity is defined in **float64**.
- **Reproducibility.** Fits must be deterministic given a descriptive seed.

[Note: this section is frozen. When the world changes — e.g. GPU stops being the bottleneck — do
NOT edit here; write a superseding ADR.]

## Decision

We will implement the `alt-nfp` model layer in **NumPyro (NUTS) on JAX**, with `vmap`-batched
fitting over the as-of grid, float64 enabled globally at import, and descriptive PRNG seeds. The
PyMC implementation in `alt_nfp` is **retained, frozen, as the parity reference and fixture
generator** — not replaced and not a fallback.

## Consequences

- **Positive:** `vmap` collapses the as-of sweep into a single vectorized fit; the same code runs
  on CPU and GPU unmodified; NUTS is JIT-compiled (fast warmup); float64 + descriptive seeds make
  the parity gate well-defined; JAX immutability pushes us toward clean functional model code.
- **Negative:** a full model rewrite; an **ongoing parity-gate maintenance burden** (every model
  change must keep matching the frozen reference within tolerance); a **familiarity split** — the
  team now maintains JAX *and* PyMC across three repos; JAX debugging (traced control flow, no
  Python `if` on data, `jnp.where`) has a steeper learning curve than PyMC.
- **Neutral / follow-on:** creates the golden-master fixture infrastructure (`s3://alt-nfp/golden/`)
  and `nfp_model.parity`; raises a future question (its own ADR) of whether `oi-indices` should also
  migrate or stay PyMC.

## Alternatives considered

- **Stay on PyMC** (like `alt_nfp` and `oi-indices`) — ergonomic, `nutpie` is fast, the team is
  fluent, and it would unify all three repos on one engine. **Rejected:** batching the as-of sweep
  and running on GPU are awkward in PyMC compared to a single `vmap`; the GPU speed lever is the
  whole point of v2's backtest.
- **Stan (cmdstanpy)** — fast, mature NUTS. **Rejected:** introduces a second language, weaker
  interop with the Polars/NumPy data layer, and no clean path to the vectorized as-of batching we
  want.
- **BlackJAX** — same JAX/GPU/`vmap` upside, more control over warmup. **Rejected (for now):** more
  boilerplate than NumPyro for a standard NUTS state-space model; NumPyro gives the same JAX
  benefits with a higher-level modeling API. (Kept in mind as a "swap the sampler" option if we
  ever need custom adaptation.)

## Trade-offs & reversibility

We are trading **team familiarity and cross-repo uniformity** for **batching, GPU, and a
well-defined float64 parity gate**. This is close to a **one-way door**: a rewrite back to PyMC
would discard the JAX investment and the parity infrastructure. What would trigger a revisit (and a
superseding ADR): if GPU batching stops being the backtest bottleneck, the JAX maintenance cost may
no longer pay for itself; or if the familiarity split causes more bugs than the speedup saves.

Note on the three-way split this formalizes: it is **deliberate**, not drift. PyMC in `alt_nfp` is
the frozen parity reference; PyMC in `oi-indices` is separate index work on its own timeline; JAX
in `alt-nfp` is the GPU-batched production path. Anyone tempted to "unify" them should read this ADR
first — collapsing them would break the parity cross-check, which is exactly the rationale this
record exists to preserve. And note the floor it sets: **parity is fidelity, not correctness** —
matching the frozen PyMC reference proves the port reproduced it, not that it is right. Correctness
is validated separately against external ground truth (published BLS / ALFRED real-time vintages).
