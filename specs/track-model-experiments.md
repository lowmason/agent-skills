# track-model-experiments — Design Spec

**Status: IN PROGRESS** — approved 2026-07-05; plan pending.

## Motivation — the gap

`bayesian-workflow` already covers two of the three activities in iterative
Bayesian modeling:

- **Per-variant artifacts** — `references/reporting.md` produces a versioned slug
  folder per model (`churn-logistic/`, `churn-logistic-v2/`, …), each with
  `inference_data.nc`, `diagnostics.json`, `report.md`. It even says "when
  iterating on the same problem, append a version" — then stops. There is no
  index above the versions and no record of *what changed* or *why*.
- **The comparison statistics** — `references/model-comparison.md` gives
  `az.compare({m1, m2, m3})` over a dict of InferenceData the user has *already
  assembled by hand* ("Fit multiple models, store InferenceData for each").

Neither covers **the iteration loop itself**: what changed v1→v2→…→vN, the
hypothesis behind each change, which variants are indexed where, driving
`az.compare` over them programmatically, recording the ranked result and the
decision, and knowing when to stop. Today (per the user) that loop is tracked by
"nothing formal" — git branches, notebook cells, and memory — so variants get
lost and it is hard to reconstruct what changed or why one won.

`track-model-experiments` is exactly that connective tissue. It sits **above**
the slug folders and **defers down** to `model-comparison.md` for the ELPD
statistics; it adds bookkeeping, a comparator, and a stopping rule. It does not
re-derive LOO.

## Goal

A standalone skill giving the Bayesian model-iteration loop a home: a per-analysis
ledger recording what changed and why, and a comparator script that ranks the
variants from their saved InferenceData and stamps the winner back into the
ledger. Correctness lives in a script that runs on real InferenceData, so the
skill is validated by execution (not subagent pressure scenarios) and ships
regardless of subagent availability.

## Non-goals

- **Not** a hyperparameter-tuning skill. Optimizing continuous/ML hyperparameters
  is the sibling `tune-hyperparameters` (future, separate spec). This skill tracks
  *model-structure* iteration: priors, distribution parameters, likelihood,
  hierarchical structure.
- **Not** a re-implementation of LOO / ELPD / stacking. Those stay in
  `bayesian-workflow/references/model-comparison.md`; this skill points to them.
- **Not** an external tracker (MLflow / W&B) wrapper. The user's stack is
  file-based and git-tracked across ~12 repos; portability comes from a local
  markdown ledger, not a service.
- **Not** a global cross-repo experiment registry (see D1).

## Design decisions (approved)

- **D1 — per-analysis ledger, not a global registry.** One `experiments.md` lives
  in the analysis directory next to the variant slug folders, git-tracked with the
  code it describes. A global log would need a home-dir convention and would
  outlive the code; a local file travels with the repo and diffs alongside the
  model. YAGNI on cross-repo.
- **D2 — human-authored *what-changed* / *hypothesis*; script fills only the
  metric columns.** The "why" is a modeling judgment, and auto-diffing arbitrary
  NumPyro model code is brittle. Metrics are structured and auto-captured.
- **D3 — build the Bayesian metrics layer only.** Keep the ledger's core columns
  (`id` / `parent` / `what changed` / `status`) generic so a future
  `tune-hyperparameters` sibling can reuse the ledger + decision-log spine without
  a rewrite. Do not build the ML half now.
- **D4 — the script updates the ledger idempotently via delimited markers.** Its
  primary outputs are `comparison.json` + a printed table; when handed the ledger
  it rewrites only the `<!-- COMPARISON:BEGIN … END -->` block and the `status`
  column's best marker, never the human prose.

## Architecture

Two artifacts plus wiring.

### Component 1 — the ledger (`experiments.md`, one per analysis)

A single markdown file the modeler maintains, with a script-maintained comparison
block. Canonical shape:

```markdown
# Experiments — churn logistic

**Question:** Does region explain churn beyond tenure?
**Data:** warehouse export, N=4013 — SAME observations across all variants (required for LOO)
**Current best:** churn-logistic-v3 (2026-07-05)

## Variants
| id (slug) | parent | what changed | hypothesis | ELPD | ΔELPD | max R̂ | div | PPC | psense | status |
|---|---|---|---|---|---|---|---|---|---|---|
| churn-logistic    | — | baseline logistic | — | -241.2 | -6.7 | 1.004 | 0 | ✓ | — | rejected |
| churn-logistic-v2 | v1 | + region-varying intercept | region heterogeneity | -236.0 | -1.5 | 1.006 | 0 | ✓ | ok | candidate |
| churn-logistic-v3 | v2 | StudentT tails | tail outliers | -234.5 | 0.0 | 1.003 | 0 | ✓ | ok | **best** |

<!-- COMPARISON:BEGIN --> …az.compare table, script-generated… <!-- COMPARISON:END -->

## Decision log
- 2026-07-05 — v3 vs v2: ΔELPD 1.5 (~1.2·dSE) → indistinguishable; kept v3 for
  robustness margin, noted it isn't data-forced. Region effect > 0 stable across
  v2/v3 → stop.
```

Columns:
- **Human-authored** (D2): `id` (the slug), `parent` (the variant this one derives
  from), `what changed`, `hypothesis`, `status`
  (candidate / rejected / best / shipped).
- **Script-filled** (D2/D4): `ELPD`, `ΔELPD`, `max R̂`, `div`, `PPC`, `psense`.

The **Decision log** is a dated narrative — why a variant was tried, what the
comparison showed, what was decided next. This captures the "why v7 won" that is
currently lost.

The **header freezes the comparison basis** (same observations across all
variants). This is load-bearing for correctness (see Correctness guardrail).

### Component 2 — the comparator (`scripts/compare_experiments.py`)

```bash
python scripts/compare_experiments.py --analysis-dir experiments/churn/ \
    --ledger experiments/churn/experiments.md \
    --output experiments/churn/comparison.json
```

Behavior:
1. Discover the variant slug folders under `--analysis-dir` (each contains
   `inference_data.nc`); or accept an explicit list of folders.
2. Load each InferenceData; convert JAX→NumPy defensively
   (`map_over_datasets(lambda ds: ds.as_numpy())`) so PSIS-LOO's in-place updates
   don't trip on JAX immutability.
3. Verify each has a `log_likelihood` group (hard error otherwise — see below).
4. Verify all variants share the same observed-data length (refuse otherwise).
5. Run `az.compare(models)` (stacking weights, default).
6. Pull each variant's `max R̂`, `min ESS`, divergence count from `sample_stats`
   (fall back to the folder's `diagnostics.json` if present — do not recompute what
   `diagnose_model.py` already wrote). The **ledger table** carries the compact
   convergence signal (`max R̂`, `div`); `comparison.json` carries the full set
   including `min ESS`. The `PPC` / `psense` columns are read from the folder's
   interpreted JSON where available (`check_report.json` / `calibration.json` for
   PPC-pass; `psense.json` for a sensitivity flag) and fall back to a presence
   marker (ran / did-not-run) when only raw outputs exist.
7. Print the ranked table; write `comparison.json`.
8. If `--ledger` is given, rewrite the `<!-- COMPARISON -->` block idempotently and
   set the `best` marker on the top-ranked variant's `status` (D4).

CLI is documented via `--help`; the SKILL.md shows the common invocation only
(token efficiency).

### Error handling — the three real failure modes

- **No `log_likelihood` group** in a variant → hard error naming the exact fix:
  `az.from_numpyro(..., log_likelihood=True)`. This is the #1 LOO gotcha and must
  fail loudly, not silently drop the variant.
- **Mismatched observed-data length across variants** → refuse with the reason.
  LOO compares predictions of *the same* observations; ELPD across models fit to
  different data is meaningless. `model-comparison.md` is explicit that the
  observation *distribution* may differ but the observations may not.
- **High Pareto k** (`az.compare`'s `warning` column, or per-model
  `az.loo(pointwise=True)`) → surface in the printed table and `comparison.json`;
  never silently trust a flagged comparison.

Also: handle the ArviZ 1.x `elpd` vs classic-0.23 `elpd_loo` column-name
difference (per the Stack-compatibility table in `bayesian-workflow/SKILL.md`), and
exit with a clear message on fewer than two comparable variants.

## Correctness guardrail

The ledger header freezes the comparison basis (same observations); the script
enforces it (step 4 above). This is the one place the skill protects the user from
a silent statistical error rather than merely doing bookkeeping.

## Stopping rule

A short inline section that reuses `model-comparison.md`'s thresholds by pointer
(does not restate the numbers as new doctrine):
- `ΔELPD < 2·dSE` across top candidates → practically indistinguishable; prefer the
  simpler model / stop.
- Conclusions stable across the models that pass their checks → the multiverse view
  (Gelman et al. 2020, §8); stop crowning a single winner.

## File structure

```
skills/track-model-experiments/
  SKILL.md                          # overview; ledger template (inline); stopping rule (points to model-comparison.md)
  scripts/compare_experiments.py
  scripts/test_compare_experiments.py
```

The ledger template (< 50 lines) and stopping rule are inline in SKILL.md per
`writing-skills` (separate files only for heavy reference or reusable tools). The
one reusable tool — the comparator — gets its own file plus a test.

## Wiring into existing skills

- `bayesian-workflow/SKILL.md` Step 9 ("Compare models") gains a one-line pointer:
  for *iterating* over many variants and tracking them, use
  `track-model-experiments`; `model-comparison.md` remains the statistics.
- `bayesian-workflow/references/reporting.md`'s "append a version" note gains a
  pointer up to the ledger.
- These are small pointer-edits into a skill *adapted from* Andorra's work;
  attribution is unaffected (adding cross-references only). Cross-references use
  **bare skill names** (`track-model-experiments`), never a plugin namespace.

## Provenance

`track-model-experiments` is a new **original** work by Lowell Mason (MIT). It must
be added to:
- `NOTICE` — the "original works by Lowell Mason, MIT licensed" list (line ~17,
  keyed by bare `track-model-experiments/`).
- `README.md` — the "Mine" skill table (a row) and the "My original skills" line
  (~146).

The frontmatter lint (`build/check_frontmatter.py`) and provenance lint
(`build/check_provenance.py`) must pass. The `description:` must be trigger-only
("Use when…"), third-person, ≤ 1024 chars, and must NOT summarize the workflow
(writing-skills SDO doctrine). No external runtime dependencies beyond the
NumPyro/ArviZ stack `bayesian-workflow` already assumes.

## Global constraints

- Python style: single quotes; target Python 3.13; NumPyro + JAX; ArviZ 1.x
  (`arviz` umbrella + `arviz-stats` / `arviz-plots`), with the documented 0.23
  porting notes only where a column name differs.
- Cross-skill references use bare skill names.
- Run everything through `uv run --python 3.13 --with …` (no repo-wide pyproject);
  tests use bare imports and are directory-scoped (run pytest from inside
  `skills/track-model-experiments/scripts/`).
- No PDFs, no book prose, no bundled external material.

## Testing strategy (how it ships now)

`scripts/test_compare_experiments.py` is the RED→GREEN gate, run by execution, not
subagents:

1. Build one shared synthetic dataset and 2–3 fast NumPyro variants — e.g. a
   well-specified model, a misspecified one, and a fixture whose idata is saved
   *without* `log_likelihood`. Fit small (few warmup/draws) and deterministically
   via a seeded `PRNGKey`; save each idata to `.nc`.
2. Assert the comparator:
   - ranks the better-specified model on top (deterministic given the seed);
   - **hard-errors** on the missing-`log_likelihood` fixture with the naming fix;
   - **refuses** a mismatched observed-length fixture.
3. Optionally assert the ledger's `<!-- COMPARISON -->` block is rewritten
   idempotently (running twice yields identical bytes) and the `best` marker lands
   on the top-ranked variant.

Run under `uv run --python 3.13 --with pytest --with numpyro --with arviz
--with arviz-stats --with numpy python -m pytest -q` from the scripts directory.

Because correctness is verified by running the script on real InferenceData —
reference/tooling content, exempt from the no-guidance-control micro-test
requirement — the skill ships even if the monthly spend cap that blocked last
cycle's subagent dispatch is still in effect. The SKILL.md prose itself needs no
pressure-test: its failure mode is "omits the cross-variant ledger the user
already partially produces," which writing-skills routes to a structural template
slot, not a discipline rationalization table.

## Out of scope / future

- `tune-hyperparameters` (ML sibling) — reuses this ledger's generic core (D3);
  its own spec + plan later.
- Auto-diffing model specifications to fill the *what changed* column (D2 rejects
  this as brittle for now).
