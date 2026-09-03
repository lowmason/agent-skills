# Skill Intake Review — `review/coding-skills`, `review/python-analytics-skills`

**Date:** 2026-08-26 · **Reviewer:** Claude (Opus 5) · **Status:** COMPLETE (retired 2026-09-02) — all three recommended adoptions shipped on 2026-08-26 and are recorded in NOTICE: the `python-module-design` rules into `clean-code` (`references/modules.md`), the JAX-generic core into `bayesian-workflow/references/jax-numerics.md`, and the ArviZ API names into `model-comparison.md`. The `polars-data-engineering` port (§5 item 4) was assessed and **not** adopted — see `specs/red-baseline-polars-join-contracts-2026-08-26.md`.

> **The three `specs/red-baseline-*-2026-08-26.md` files stay in `specs/` root, not here.** They are live micro-test fixtures, not finished records: `skills/clean-code/references/modules.md` and `skills/bayesian-workflow/references/jax-numerics.md` cite them by path, and each carries a quarantine banner for future micro-tests of its skill. Moving them would break two shipped skills.

Two cloned repos assessed for additions to `skills/`. Verdict: **one adopt, five harvests,
six skips.** The binding constraint is not quality — it is the skill-listing budget.

> **Revised 2026-08-26 after user review.** The first pass skipped both JAX skills on a
> dependency grep of `~/Projects`. That grep measured the wrong environment: JAX is authored
> here and run at work. The JAX-generic core is now a substantial HARVEST (§4), and §2 records
> the corrected reasoning. Equinox is incidental; the repo is Mac-only for now.

---

## 0. The binding constraint (measured, with one honest gap)

`skillListingBudgetFraction: 0.025` → ~5,000 tok ≈ **20,000 chars**. The 30 personal skills
consume **18,126 chars** → **1,874 chars headroom against personal skills alone.**

**That figure is optimistic and should not be read as real headroom.** The listing is shared
with ~55 app-injected plugin entries (`product-management:*`, `engineering:*`, `data:*`,
`anthropic-skills:*`, `dataviz`, `claude-api`, …). Per the `skill-listing-budget` memory these
are injected by the desktop app at runtime, are *not* in the on-disk plugin cache, and are not
settings-disableable — so they have never been measured. A rough read of this session's own
listing puts them near ~16k chars, which would put the **total already ~1.7× over budget**.

Counter-evidence from this same session: **all 30 personal skills are present in the live
listing** alongside those injected entries. So drop-by-rank is not observably biting today,
whatever the accounting is. `/context`'s per-plugin breakdown remains the authoritative check
and is unavailable in this non-interactive session.

**What this means for the recommendation:** treat one adopt as the ceiling, and prefer a lever
that costs no global listing budget at all. Per-project scoping — a repo-local symlink in
`alt-nfp` rather than `~/.claude/skills/` — is already recorded in the memory as an untaken
option and fits the one ADOPT candidate exactly, since that skill is only needed where
`nfp-model` lives. See §4.

Everything else of value is recommended as **content harvested into a named incumbent**, which
costs zero listing budget and — per `writing-skills` — requires no RED/GREEN pressure-test,
unlike a new discipline skill.

---

## 1. Provenance and licensing (read before any adoption)

### `mancusolab/coding-skills` — clean
MIT, `LICENSE` present, © 2026 Mancuso Lab. Author Nick Mancuso. Adoption is
straightforward: standard superpowers-style NOTICE entry + `LICENSE-coding-skills`.

**But these are Codex skills, not Claude Code skills.** `AGENTS.md` states: *"This repository
contains Codex-only skill definitions."* Verified consequence — all six fail this repo's own
lint:

```
$ check_frontmatter.check_skill(<each>)
jax-equinox-numerics      -> unknown frontmatter key 'user-invocable'
jax-project-engineering   -> unknown frontmatter key 'user-invocable'
polars-data-engineering   -> unknown frontmatter key 'user-invocable'
pragmatic-rust-guidelines -> unknown frontmatter key 'user-invocable'
python-module-design      -> unknown frontmatter key 'user-invocable'
python-rust-bridge        -> unknown frontmatter key 'user-invocable'
```

One-line fix each (drop `user-invocable`, keep `metadata.short-description` — it is in
`ALLOWED_KEYS`). Noted because it confirms these need porting, not copying.

**Quality signal:** `docs/validation-notes.md` records a 2026-05-21 pressure-test run with
`testing-skills-with-subagents` — the same superpowers-lineage discipline `writing-skills`
mandates. Upstream hardening is real, but a local RED/GREEN control is still required before
deploy (their scenarios test *their* boundaries, not this repo's incumbents).

### `pymc-labs/python-analytics-skills` — **licensing gap, resolve before adapting**

- **No `LICENSE` file, and none has ever existed** in all 48 commits.
- `README.md:174` says *"MIT License. See [LICENSE](LICENSE) for details."* — **a link to a
  file that does not exist.**
- `.claude-plugin/plugin.json` declares `"license": "MIT"`.

So the grant is an express MIT statement by the copyright holder (Chris Fonnesbeck, with
Will Dean; 44/4 commits) in two manifests, but the repo **ships no license text and no
copyright notice**. Whether that satisfies MIT's notice condition is a legal judgment, not
something this review settles — it is simply a gap worth closing before building on it.

Given the repo's attribution standard, the two defensible routes:

1. **Treat as MIT** (the declaration is explicit and by the copyright holder): vendor
   `LICENSE-python-analytics` with the standard MIT text and `Copyright (c) 2026 Chris
   Fonnesbeck`, plus a NOTICE entry. Cleanest if upstream is asked to add the file — worth a
   one-line issue on the repo.
2. **Idea-only adoption** — the precedent this repo *already set for `llm-wiki`* (Karpathy's
   gist and `kfchou/wiki-skills` adopted "by reference to the idea only"; original prose,
   nothing reproduced). This route needs no license text at all.

**Recommendation: route 2 for everything recommended below**, because every
python-analytics recommendation is a harvest of a *fact* (an API name, a structural
distinction), not of prose. That sidesteps the gap entirely.

### Ancestry finding (NOTICE-relevant)

`NOTICE` credits `bayesian-workflow` to *"Alexandre Andorra's original PyMC
Bayesian-workflow skill."* This repo **also had a `bayesian-workflow` skill**, removed in:

```
2a704b1 | Chris Fonnesbeck | 2026-03-02
  "Remove bayesian-workflow skill and related references, replacing it with
   updated context for iterative modeling in pymc-modeling."
```

That upstream skill was a 175-line *strategy* skill citing Gelman/Vehtari/McElreath (2025).
**Andorra appears nowhere in this repo's history** (only Fonnesbeck and Dean), so this is
most likely a sibling lineage, not the ancestor — **NOTICE needs no change**. Flagged
because it is one hop from an attribution error, and because it is a design signal:
upstream deliberately *retired* the standalone workflow skill and folded strategy into its
API skill. This repo went the other way. That divergence is a deliberate fork worth knowing
about, not a defect.

---

## 2. Stack fit — **corrected 2026-08-26 after user review**

### The original error

The first pass grepped `~/Projects` for dependencies and read "zero Equinox, zero Lineax /
Optimistix" as grounds to skip both JAX skills. **That inference was wrong.** Per the user:

> *"Not used here as this is a Mac M4 Max and is not JAX friendly. Used HEAVILY at work."*

`~/Projects` is the **authoring** environment, not the runtime. JAX/NumPyro code is written
here and executed on work hardware (Apple Silicon has no mature JAX GPU backend). A dependency
grep measures where code *runs*; skill fit depends on where code is *written* — and Claude Code
runs on the Mac. The two diverge here, so runtime deps are a broken proxy.

`alt-nfp/packages/nfp-model` declaring `jax>=0.4.38` / `numpyro>=0.16.1` while JAX is
impractical locally is the visible fingerprint of exactly that split.

**Corrected user input:** JAX is heavy at work; **Equinox appears only incidentally**;
this skills repo is **Mac-only for now** (does not deploy to work).

### Revised table

| Dependency | Status | Consequence |
|---|---|---|
| **JAX / NumPyro** | **heavy at work, authored here** | JAX skills earn their keep — code is written where Claude Code runs |
| **Equinox** | **incidental** | don't spend `SKILL.md` budget on `eqx.Module` semantics; demote to a loaded-on-demand reference |
| Lineax, Optimistix | not indicated | drop those references |
| **Rust / PyO3 / Cargo** | zero, and no work signal | skip both Rust skills — unchanged |
| PreliZ | zero | `prior-elicitation` still has no hook |
| marimo | `archive/Time-series` only | archived — unchanged |
| pymc-extras, nutpie | `archive/oi-indices` only | PyMC legacy — unchanged |
| **Polars** | live both here and at work | Polars→JAX seam stands |

Only the JAX rows moved. The Rust, PyMC, marimo, and PreliZ skips rested on evidence the
correction doesn't touch — no work-side signal was offered for any of them, and the Rust skip
in particular is safe in both environments.

### Equinox-boundness, measured per file

Because Equinox is incidental, the split matters:

| File | Equinox lines / total | Verdict |
|---|---|---|
| `references/numerics_dtype_stability.md` | **4 / 88** | effectively JAX-generic — take as-is |
| `references/jit_pytree_controlflow.md` | **55 / 280** | take the JAX-generic ~75%; its `filter_jit` / `filter_vmap` / `filter_shard` rules are eqx-bound |
| `references/ad_checkpointing_callbacks.md` | 31 / 187 | mostly portable |
| `SKILL.md` body | ~90 / 353 | the abstract-or-final Module pattern and field/init rules are pure Equinox |

---

## 3. Overlap against the incumbent 30 (grep-verified, not impression)

Absent from **all 30** existing skills:

```
to_jax            ABSENT      validate=          ABSENT      nulls_equal   ABSENT
coalesce          ABSENT      row-order          ABSENT      from_arrow    ABSENT
sink_csv/parquet  ABSENT      enable_x64         ABSENT      PyTree        ABSENT
static_argnums    ABSENT      donate_argnums     ABSENT
```

Already well covered (harvesting these would duplicate):

```
scan_parquet / scan_csv / LazyFrame / collect()  -> explore-data, validate-data, clean-code
maintain_order                                   -> validate-data
loo (236 hits), elpd, stacking, pareto, loo-pit,
prior predictive, sensitivity, preliz            -> bayesian-workflow (+ 10 references/)
pytest slow-marker discipline, tiny MCMC smoke
config, CI exclusions                            -> develop-testing-strategy Step 6
module/package granularity, file-count discipline -> ABSENT from clean-code, clean-coder,
                                                     and design-architecture
```

---

## 4. Recommendations

> **STATUS 2026-08-26 — the `python-module-design` harvest is DONE, and landed differently
> than recommended below.** It shipped into **`clean-code`** as a new *Modules* category
> (M1–M4 + `references/modules.md`), not into `clean-coder`, and was **cut from eleven rules
> to four** on measured evidence: a two-arm RED baseline found agents already satisfy seven of
> them unprompted. Full record and both GREEN arms:
> `specs/red-baseline-module-granularity-2026-08-26.md`. The `clean-coder` recommendation in
> the HARVEST table below is superseded; the other three harvests and the Polars ADOPT are
> untouched.

### ADOPT (1) — `polars-data-engineering` → **WITHDRAWN 2026-08-26**

> **This recommendation did not survive measurement.** A two-arm RED baseline
> (`specs/red-baseline-polars-join-contracts-2026-08-26.md`) planted a silent join fanout and
> measured the *delivered artifact*: 5/5 agents shipped correct arrays, detecting the duplicate,
> collapsing before the join, and guarding the row count. The rules describe what agents already
> do when authoring, so a listing slot would buy nothing.
>
> The `54 joins / 0 validate=` finding in `alt-nfp` stands, but it is about **existing** code —
> an audit gap. Shipped instead as one signal in `tech-debt`'s sweep plus a `scan.sh` check, at
> zero listing cost. `to_jax()`, Arrow interchange, and streaming sinks were dropped outright.
>
> The original recommendation follows, unedited, for the record.

### ADOPT (1) — `polars-data-engineering` → port as skill #31

The only candidate that is both on a live seam and materially non-duplicative.

- **New material:** join contracts (`validate=` cardinality, `nulls_equal=`, `coalesce=`,
  `maintain_order=`), the row-order-freeze rule before array export, `to_jax(dtype=…)` as an
  adapter boundary, Arrow-vs-pandas interchange, streaming `sink_*` for larger-than-RAM egress.
  All eleven terms verified absent from the incumbent 30.
- **Duplicative material to drop on port:** lazy-first / `scan_*` vs `read_*` / materialize-once —
  already in `explore-data` and `validate-data`.
- **Quality:** date-stamped rules ("As of March 3, 2026") citing primary Polars docs, with the
  API-unstable flags on `to_jax` / `write_csv(compression=)` / `sink_csv` called out honestly.
- **Costs:** rewrite the 203-char description to repo trigger-density (~700 chars); drop
  `user-invocable`; convert examples to single quotes / py3.13; RED/GREEN pressure-test per
  `writing-skills`; NOTICE entry *before* the SKILL.md lands or `check_provenance.py` fails.
- **Listing budget (see §0):** this is the only recommendation that consumes a slot. Given the
  unmeasured injected listing, prefer **per-project scoping** — symlink it into `alt-nfp`
  rather than `~/.claude/skills/` — since `nfp-model` is the only place the Polars→JAX seam
  exists. That gets the skill with zero global listing cost. Promote to global later if it
  proves useful in `bls-stats-aggregation` too.
- **Boundary to draw explicitly:** `explore-data` profiles a dataset, `validate-data` gates it
  pre-publish, this one engineers the pipeline and its export contract. Without a stated
  boundary this will mis-trigger against two incumbents.

### HARVEST (4) — into named incumbents, zero listing cost

| Source | → Target | What |
|---|---|---|
| **`jax-equinox-numerics`** — the JAX-generic core (both reference files + the non-eqx rules) | **`bayesian-workflow/references/jax-numerics.md`** (new) | **Upgraded from SKIP after the stack-fit correction.** dtype-normalize-at-boundary, `jnp.where` divide/norm guards, early nonfinite surfacing, JIT-at-the-public-boundary, static-vs-dynamic args, PyTree stability / recompilation avoidance, `lax.scan` vs `lax.while_loop`, explicit PRNG threading with `split`/`fold_in`. Every one of `PyTree`, `static_argnums`, `donate_argnums`, `enable_x64` is absent from all 30. Demote `eqx.Module` / `filter_*` material to a short `equinox.md` beside it, per "Equinox is incidental". |
| `jax-project-engineering` — the runtime-config rule only | **`bayesian-workflow/references/jax-numerics.md`** | `jax.config.update('jax_platform_name', …)` driven by a `--device` flag, plus `jax_enable_x64` policy set inline in `main()` — with the explicit *don't wrap this in a config layer* guidance. **This is the develop-on-Mac / run-at-work seam made explicit**, and it pairs with the `set_host_device_count`-must-precede-first-JAX-op gotcha already recorded in memory. The rest of the skill (API lifecycle, packaging, CI gates) overlaps `design-architecture` and `develop-testing-strategy` — leave it. |
| `python-module-design` — the anti-fragmentation rules | **`clean-coder`** (or `clean-code`) | "new files require explicit justification", "avoid one-function utility modules", "consolidate before completion", the four *Smells That Suggest A Missing Subpackage*. Genuinely absent: no file/module/package-granularity rule exists in `clean-code`, `clean-coder`, or `design-architecture`. This is the file-level counterweight to Clean Code's tiny-unit instinct — exactly the role `clean-coder` already assigns Ousterhout's APOSD at *function* level, extended one layer up. **The strongest harvest.** |
| `model-evaluation` — three API names only | **`bayesian-workflow/references/model-comparison.md`** | `loo_expectations`, `loo_metrics`, `loo_r2` (ArviZ 1.1) and the Bayes-factor section — all zero hits in `bayesian-workflow`, which otherwise already covers LOO/ELPD/stacking/Pareto-k far more thoroughly. Facts only, idea-only route, no prose. |

### SKIP (6)

| Skill | Why |
|---|---|
| `pragmatic-rust-guidelines`, `python-rust-bridge` | Zero Rust/PyO3/Cargo across all eight repos. |
| `jax-equinox-numerics`, `jax-project-engineering` *(as whole skills)* | **Not a stack-fit skip — a scoping one.** JAX is heavy, so the content is wanted; but with Equinox only incidental, ~90 of 353 `SKILL.md` lines (abstract-or-final Modules, field/init rules) and the Lineax/Optimistix rules are dead weight, and `jax-project-engineering` is mostly API-lifecycle/packaging/CI that `design-architecture` and `develop-testing-strategy` already own. Take the JAX-generic core as a reference (§4 HARVEST) rather than spending a listing slot on an Equinox-framed skill. **Escalation trigger:** if JAX work outgrows NumPyro modeling — custom kernels, non-Bayesian numerics — promote `jax-numerics.md` to its own skill, since `bayesian-workflow` won't trigger on non-Bayesian JAX. |
| `pymc-modeling`, `pymc-extras` | PyMC/PyTensor API surface. Against a NumPyro-first convention *and* the only PyMC repo (`oi-indices`) is archived. High-quality, wrong stack. |
| `prior-elicitation` | `bayesian-workflow/references/priors.md` + `sensitivity.md` cover it (27 prior-predictive, 66 sensitivity, 9 PreliZ hits); PreliZ unused live. |
| `pymc-testing` | Its portable idea — fast structure-only vs slow real-inference tests behind markers — is already `develop-testing-strategy` Step 6, in more detail and with this repo's actual marker vocabulary. The remainder is `pymc.testing.mock_sample`, which has no NumPyro equivalent. |
| `marimo-notebook` | The judgment call. Zero overlap with all 30, well built, and there are three `scratch.ipynb` files in live repos it could target. But marimo is **not installed anywhere live** (archive only) — this would be adopting a *tool*, not documenting a practice, and its examples are pandas-idiomatic (`df.copy()`, `temp['new_col']`) against a Polars-first convention. **Revisit if and when marimo is actually adopted**; do not spend the last listing slot on it now. |

---

## 5. If pursued

Per the repo lifecycle: `brainstorming` → `writing-plans` → execution. Scope is one adopt +
four harvests — a single small plan, not a roadmap.

Ordering that front-loads value and defers the expensive item:

1. **`python-module-design` → `clean-coder`** — highest value/cost ratio, and unchanged by the
   correction. A reference-file edit to a skill that already owns the "temper the tiny-unit
   instinct" role. No listing entry, no pressure-test.
2. **JAX-generic core → `bayesian-workflow/references/jax-numerics.md`** (+ a short
   `equinox.md`) — promoted by the correction, and now the largest single harvest. Closes the
   `enable_x64` / PyTree / PRNG-discipline gap in the stack that gets the heaviest use, and
   makes the develop-on-Mac / run-at-work device split explicit via the `--device` +
   `jax_platform_name` rule. Strip `filter_*` and Lineax/Optimistix on the way in.
3. **Three ArviZ API names → `model-comparison.md`** — minutes.
4. **`polars-data-engineering` port** — the only item carrying a listing slot, a NOTICE entry,
   a `LICENSE-coding-skills` file, and a RED/GREEN pressure-test. Do it last and deliberately.

Note the correction did not change the *ordering*, only the size of item 2 — which is
reassuring, since it means the ranking rested on overlap-with-incumbents evidence rather than
on the faulty dependency grep. Items 1–3 cost no listing budget, so the budget uncertainty in
§0 only ever gates item 4.

**Housekeeping:** `review/` holds two full nested git clones inside this tracked repo and is
currently untracked-but-not-ignored. Add `review/` to `.gitignore` (or delete after this
review) — it must not be committed.
