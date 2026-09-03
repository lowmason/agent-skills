# bayesian-workflow ← *Bayesian Workflow* (Gelman et al. 2026) Integration Plan

**Status: COMPLETE (2026-09-03)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Re-ground the `bayesian-workflow` skill on the 2026 *Bayesian Workflow* book (the successor to the 2020 arXiv paper it already cites) and close the five guidance gaps the book exposes — Monte-Carlo-error-driven digit choice, a divergence-fraction gate on raising `target_accept_prob`, a failure-signature catalog, exploration-vs-final run sizing, and current SBC practice — without reproducing any book prose, figure, or code.

**Architecture:** Docs-first, citation-keyed. Task 1 fixes the provenance record and the citation key (`Gelman et al. 2026, §x.y`) every later task uses. Tasks 2–4 and 6, 9 edit the skill's Markdown; Tasks 3 and 7 add small, tested additions to two bundled scripts (`diagnose_model.py` gains a `precision` block; `check_diagnostics.py` gates its divergence suggestion on the divergence fraction). The one behaviour-shaping wording change (the gate) is bracketed by a RED baseline (Task 5, before the edit) and a GREEN run (Task 8, after) per the writing-skills micro-test rule, recorded in `specs/red-baseline-divergence-gate-<date>.md`.

**Tech Stack:** Markdown skill files; Python 3.13 via `uv run` for the two scripts; ArviZ 1.3.0 / arviz-stats 1.3.1 / arviz-plots 1.3.1 (the stack `uv run --with arviz --with arviz-stats --with arviz-plots` resolves to on this machine, verified 2026-09-02); pytest, directory-scoped with bare imports (repo convention).

**Spec:** none — this plan is the spec (a well-specified batch under the repo's proportional-process rule). The assessment that produced it lives in the planning session; the requirements are restated in full under **Requirements** below so the self-review has something to check against.

## Source facts (verified 2026-09-02 — do not re-derive)

- **The book:** Gelman, Vehtari, McElreath, Simpson, Margossian, Yao, Kennedy, Gabry, Bürkner, Modrák & Leos Barajas (2026), *Bayesian Workflow*, Chapman & Hall/CRC. Corrected electronic edition dated 19 August 2026. © 2020–2026 by the authors. Every page is stamped "This electronic edition is for non-commercial purposes only." Website: https://avehtari.github.io/Bayesian-Workflow/ (states "Copyright by the authors" and links the PDF as "Electronic edition for non-commercial purposes only").
- **Companion code repo** `github.com/avehtari/Bayesian-Workflow` (R + Stan case studies): **no LICENSE file** (GitHub API reports `license: null`). All rights reserved by default → **nothing from it may be ported, translated to NumPyro, or paraphrased**. Case studies may be cited as worked examples by chapter number only.
- **Local PDF:** `~/Downloads/Bayesian-Workflow.pdf` (550 pages, 50 MB). Task 1 moves it beside the three workflow papers already kept in `~/Documents/Bayesian/Workflow/`. **PDF page = book page + 12** (book p. 17 is PDF p. 29). Use `Read` with `pages:` to verify any citation.
- **Book's acknowledgments** (PDF p. 11) state that many sections were adapted from Gelman, Vehtari, Simpson et al. (2020) — the arXiv paper the skill cites today. The book supersedes it; the paper stays listed as the open-access fallback.
- **ArviZ API facts** (probed on the resolved stack): `az.from_dict({"posterior": {...}, "sample_stats": {...}})` → `DataTree` (the 1.x signature takes one dict, not kwargs); `az.summary(idata)` columns are `mean, sd, eti89_lb, eti89_ub, ess_bulk, ess_tail, r_hat, mcse_mean, mcse_sd` and vector params flatten to `beta[0]`, `beta[1]`; `az.mcse(data, method="mean"|"sd"|"quantile", prob=None)` returns a `DataTree`; `arviz_plots.plot_ecdf_pit(dt, *, var_names=None, group="prior_sbc", coverage=False, ...)` "assumes the values in the DataTree have already been transformed to PIT values, as in the case of SBC analysis" and draws a simultaneous band with `suspicious_points` and `p_value_text` visuals.
- **Script facts (probed):** `arviz_stats.diagnose(idata, return_diagnostics=True, show_diagnostics=False)` returns `d["divergent"]["pct"]` **in percent** (8.0 for 160/2000) — the same unit as `diagnose_model`'s manual path, so a `> 1.0` gate is correct on both; on a `from_dict` idata with no `energy` stat it returns keys `divergent`, `ess`, `rhat` and an empty `bfmi` without raising. `az.summary` on a constant variable gives `sd = 0`, `mcse_mean = 0`, `mcse_sd = nan` and does not raise. `check_diagnostics.py --output` writes the suggestions under the JSON key `next_steps`.
- **Repo state at planning time:** `CLAUDE.md`, `README.md` (root), `commands/deferred.md` are modified and `specs/audit_9_2_26.md` is untracked — **pre-existing, unrelated work. Never `git add` them.** Stage by explicit path only.
- **No `ANTHROPIC_API_KEY` in the shell** → micro-tests (Tasks 5, 8) use single-shot subagents via the Agent tool, not raw API calls.

## Requirements

- **R1 Provenance.** NOTICE records the book (terms, no-prose/no-PDF/no-code stance, unlicensed companion repo); `references/publications.md` lists the book first with the arXiv paper as fallback; skill README names the book; SKILL.md `version` bumps to `2.1`. Frontmatter and provenance lints pass.
- **R2 Citations.** All seven `Gelman et al. 2020, §n` citations re-point to book sections verified against the PDF (mapping table in Task 2); a one-line Ch 26 pointer joins the HMM paragraph in `state-space.md`. Zero `Gelman et al. 2020` strings remain outside `publications.md`.
- **R3 Precision.** `diagnose_model.py` emits a `precision` block (per-parameter `sd`, `mcse_mean`, `mcse_sd`, `rel_mcse`, `stable_digits`; plus `max_rel_mcse`, `max_rel_mcse_param`, `min_stable_digits`), covered by tests; `reporting.md` gains a digits rule (§11.4–11.7) and the report templates carry the numbers.
- **R4 Divergence gate.** Every passage that tells the agent to raise `target_accept_prob` for divergences is conditioned on the divergence fraction (≤ ~1% → raise; > ~1% → inspect geometry first; Gelman et al. 2026, §12.3): `diagnostics.md` fix-list step 1 and ladder rung 1, SKILL.md "When things go wrong" row, and `check_diagnostics.suggest_next_steps` (tested). RED baseline recorded before the wording change; GREEN after; both in one record file.
- **R5 Failure signatures.** A signature → cause → NumPyro check/fix table (§12.3) in `diagnostics.md`, pointed to from SKILL.md.
- **R6 Run sizing.** An "Exploration runs vs. the final run" subsection (§2.1, §11.4, §12.1, §12.4) in `diagnostics.md`, echoed in one sentence in SKILL.md's Chains paragraph.
- **R7 SBC.** `model-criticism.md`'s SBC section rewritten to §14.1–14.3 practice: Δ-ECDF over histograms with a **verified** `plot_ecdf_pit` snippet, test quantities, prior-tension and rejection-sampling, posterior SBC, few-reps-still-useful, SBC as software testing.
- **R8 Green.** All lints, both script test files, and the stale-citation grep pass at the end.

## Global Constraints

- **License:** cite the book as `(Gelman et al. 2026, §x.y)` or `(Gelman et al. 2026, Ch n)` in **original wording only**. No quoted sentences, no figure reproductions, no Stan/R code from the book or its repo, no PDF in the repo (`build/check_provenance.py` fails on any tracked `.pdf`). This is the same regime NOTICE already applies to Murphy's PML books.
- **Verify before citing:** every `§` you write must be checked against the PDF page (`Read … pages: "<book page + 12>"`) before the commit that introduces it. Task 2 lists the pages; later tasks name their sections — open them.
- **Sibling-passage propagation:** this skill has a history of corrections that missed a sibling passage (commit `d47efab`). Every task that changes a rule ends with a `grep` across `skills/bayesian-workflow` for the rule's key phrase and updates every hit.
- **Python style:** match each script's existing style (double quotes, 4-space indent, type hints where the file already uses them). Tests co-located in `skills/bayesian-workflow/scripts/`, bare imports, run from inside that directory.
- **Test command (new in this plan, added to CLAUDE.md in Task 10):**
  `cd skills/bayesian-workflow/scripts && uv run --python 3.13 --with pytest --with arviz --with arviz-stats --with numpy --with xarray python -m pytest -q`
- **Lints (run after any task touching SKILL.md or NOTICE):**
  `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py` and `uv run --python 3.13 python build/check_provenance.py` — both exit 0.
- **Commits:** conventional style with scope (`docs(bayesian-workflow): …`, `feat(bayesian-workflow): …`, `test(bayesian-workflow): …`), body explains *why*, ends with `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. Stage by explicit path.
- **Scope fence:** no new reference files; no edits to `hierarchical.md`, `sensitivity.md`, `visualize.md`, `jax-numerics.md`, `calibration_check.py`. YAGNI.
- **Scratch runs:** never run a Python file whose directory is `/tmp` — a stray `/tmp/struct.py` shadows the stdlib `struct` module on this machine. Use `/tmp/bwprobe/` (exists) or `/tmp/bw-microtest/` and `cd` into it.

---

### Task 1: Provenance record and citation key

Establish the citation key every later task uses, record the licensing stance in NOTICE, and put the PDF where the other workflow papers live.

**Files:**
- Modify: `NOTICE:37-39` (the three-line paragraph that starts `The skill cites Gelman et al. 2020`)
- Modify: `skills/bayesian-workflow/references/publications.md` (whole file, 9 lines)
- Modify: `skills/bayesian-workflow/README.md:25` (last sentence of the guardrails paragraph)
- Modify: `skills/bayesian-workflow/SKILL.md:18` (`version: "2.0"`)
- Move (outside the repo): `~/Downloads/Bayesian-Workflow.pdf` → `~/Documents/Bayesian/Workflow/`

**Interfaces:**
- Produces: the citation key **`Gelman et al. 2026, §x.y`** (section) / **`Gelman et al. 2026, Ch n`** (chapter). Every later task writes citations in exactly this form.

- [x] **Step 1: Move the PDF beside the papers it supersedes**

```bash
mv ~/Downloads/Bayesian-Workflow.pdf ~/Documents/Bayesian/Workflow/Bayesian-Workflow-2026-corrected.pdf
ls -la ~/Documents/Bayesian/Workflow/
```

Expected: four PDFs listed (the three 2019/2020 papers plus the book). All later `Read … pages:` steps use this path.

- [x] **Step 2: Replace the NOTICE citation paragraph**

Replace these exact three lines in `NOTICE`:

```
    The skill cites Gelman et al. 2020 (arXiv:2011.01808), Betancourt 2020
    (CC BY-NC 4.0), and Gabry et al. 2019 (JRSS-A / arXiv:1709.01449) by
    author-year only; it reproduces no text and bundles no copies.
```

with:

```
    The skill cites Gelman, Vehtari, McElreath et al. (2026), "Bayesian
    Workflow" (Chapman & Hall/CRC; (c) 2020-2026 by the authors; the
    electronic edition at users.aalto.fi/~ave/Bayesian-Workflow.pdf is
    distributed "for non-commercial purposes only") by chapter and
    section number only, in original wording; it reproduces no book
    prose or figures and bundles no PDF. The book's companion repository
    (github.com/avehtari/Bayesian-Workflow, R + Stan case studies) ships
    no LICENSE file, so none of its code is ported, translated, or
    paraphrased -- case studies are cited as worked examples by chapter
    only. The earlier arXiv preprint (Gelman et al. 2020,
    arXiv:2011.01808) stays listed in references/publications.md as the
    open-access fallback. Betancourt 2020 (CC BY-NC 4.0) and Gabry et al.
    2019 (JRSS-A / arXiv:1709.01449) are likewise cited by author-year
    only; the skill reproduces no text and bundles no copies of any of
    them.
```

- [x] **Step 3: Rewrite `references/publications.md`**

Replace the whole file with:

```markdown
# Workflow references (cited, not bundled)

The skill cites these by author-year and, for the book, by chapter/section number.
None are redistributed here (see the repo-root NOTICE).

- Gelman, Vehtari, McElreath, Simpson, Margossian, Yao, Kennedy, Gabry, Bürkner, Modrák &
  Leos Barajas (2026), *Bayesian Workflow* — Chapman & Hall/CRC. Cited as
  "Gelman et al. 2026, §x.y" using the book's section numbers.
  Website: https://avehtari.github.io/Bayesian-Workflow/ (electronic edition for
  non-commercial use only). The companion code repository carries no license file, so
  its R/Stan case studies are cited by chapter and not ported.
- Gelman et al. (2020), *Bayesian Workflow* — arXiv:2011.01808. The open-access preprint
  the book grew from; use it when a reader cannot access the book. Its section numbers
  differ from the book's (e.g. the folk theorem is paper §5, book §12.4).
- Betancourt (2020), *Towards a Principled Bayesian Workflow* —
  https://betanalpha.github.io/assets/case_studies/principled_bayesian_workflow.html (CC BY-NC 4.0)
- Gabry et al. (2019), *Visualization in Bayesian workflow*, JRSS-A 182(2) —
  doi:10.1111/rssa.12378 / arXiv:1709.01449
```

- [x] **Step 4: Name the book in the skill README**

In `skills/bayesian-workflow/README.md` line 25, replace the final sentence

```
It also ships a dedicated visualization guide (`references/visualize.md`) translating the Gabry et al. (2019) *Visualization in Bayesian workflow* paper into ArviZ.
```

with

```
It also ships a dedicated visualization guide (`references/visualize.md`) translating the Gabry et al. (2019) *Visualization in Bayesian workflow* paper into ArviZ. Workflow guidance throughout is cited by section to Gelman, Vehtari, McElreath et al. (2026), *Bayesian Workflow* (see `references/publications.md`); the book is cited, not reproduced.
```

- [x] **Step 5: Bump the skill version**

In `skills/bayesian-workflow/SKILL.md` frontmatter, change `  version: "2.0"` to `  version: "2.1"`.

- [x] **Step 6: Run both lints**

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py && uv run --python 3.13 python build/check_provenance.py && echo LINTS-OK
```

Expected: `LINTS-OK` (each lint prints nothing on success and exits 0).

- [x] **Step 7: Commit**

```bash
git add NOTICE skills/bayesian-workflow/references/publications.md skills/bayesian-workflow/README.md skills/bayesian-workflow/SKILL.md
git commit -m "docs(bayesian-workflow): record Gelman et al. 2026 Bayesian Workflow as the cited source

The skill's seven workflow citations point at the 2020 arXiv paper; the
2026 book (CRC Press, corrected e-edition 19 Aug 2026) states it adapted
many sections from that paper and is now the primary source. Record it in
NOTICE under the same regime as Murphy's PML books: cite by chapter/section
in original wording, reproduce no prose or figures, bundle no PDF. The
companion code repo has no LICENSE file, so nothing from it is ported.
Bump the skill to 2.1; later commits re-point the citations and add the
guidance the book adds.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 2: Re-point the seven paper citations to verified book sections

**Files:**
- Modify: `skills/bayesian-workflow/SKILL.md:27` and `:235`
- Modify: `skills/bayesian-workflow/references/diagnostics.md:122`
- Modify: `skills/bayesian-workflow/references/priors.md:18`
- Modify: `skills/bayesian-workflow/references/model-comparison.md:18`, `:25`, `:94`
- Modify: `skills/bayesian-workflow/references/state-space.md:33` (append one line after the HMM paragraph)

**Interfaces:**
- Consumes: citation key from Task 1.
- Produces: `diagnostics.md:122` now ends `(Gelman et al. 2026, §12.4).` — Task 6 replaces that whole paragraph and quotes this post-Task-2 text.

- [x] **Step 1: Gate B — open each cited page and confirm the claim before editing**

Use `Read` on `~/Documents/Bayesian/Workflow/Bayesian-Workflow-2026-corrected.pdf` with the `pages` below. Tick each row only after reading it.

| Site | New citation | PDF pages (book pages) | Claim the section must support |
|---|---|---|---|
| SKILL.md:27 | `Gelman et al. 2026, §2.1` | 29 (17) | in a typical workflow we fit a series of models, several of which are poor in retrospect; those are unavoidable steps toward the useful model |
| SKILL.md:235 | `Gelman et al. 2026, §11.4` | 210–211 (198–199) | run at least four chains by default; multiple chains reveal multimodality and poor adaptation; more parallel chains are an alternative to longer chains for variance reduction |
| diagnostics.md:122 | `Gelman et al. 2026, §12.4` | 239 (227) | the folk theorem: computational trouble usually signals a model problem; the first instinct should not be more compute |
| priors.md:18 | `Gelman et al. 2026, §5.6` (+ `§5.9` for the dimension point) | 90 (78); 104–105 (92–93) | five levels of prior informativeness from flat to specific; "weak" is relative to the question; independent weak coefficient priors become a strong prior on predictions as the number of predictors grows |
| model-comparison.md:18 | `Gelman et al. 2026, §9.6; worked example Ch 28` | 182 (170) | projection predictive variable selection is stable and avoids the overfitting of searching a large model space by cross-validation score |
| model-comparison.md:25 | `Gelman et al. 2026, §9.3 and §9.5` | 174 (162); 179–180 (167–168) | multiverse analysis: fit all the options and see whether conclusions change; when they do not, deciding which model is "best" matters less |
| model-comparison.md:94 | `Gelman et al. 2026, §9.6` | 181 (169) | stacking has outperformed Bayesian model averaging in the authors' examples; marginal-likelihood weights move by large factors under prior changes that barely affect predictions; heterogeneous stacking weights hint that a hierarchical model could do better |
| state-space.md (new line) | `Gelman et al. 2026, Ch 26` | 413 (401) — title page of the chapter is enough | Ch 26 is a hidden-Markov-model case study on animal movement, built up then state-decoded |

- [x] **Step 2: Apply the seven substitutions**

Each is an exact substring replacement inside the existing line:

| File:line | Replace | With |
|---|---|---|
| SKILL.md:27 | `(Gelman et al. 2020, §1)` | `(Gelman et al. 2026, §2.1)` |
| SKILL.md:235 | `(Gelman et al. 2020, §3.2)` | `(Gelman et al. 2026, §11.4)` |
| diagnostics.md:122 | `(Gelman et al. 2020, §5)` | `(Gelman et al. 2026, §12.4)` |
| model-comparison.md:18 | `(Gelman et al. 2020, §8.3)` | `(Gelman et al. 2026, §9.6; worked example in Ch 28)` |
| model-comparison.md:25 | `(the multiverse view, Gelman et al. 2020, §8)` | `(the multiverse view, Gelman et al. 2026, §9.3 and §9.5)` |
| model-comparison.md:94 | `(Gelman et al. 2020, §8.2)` | `(Gelman et al. 2026, §9.6)` |

For `priors.md:18`, replace `(Gelman et al. 2020, §7.3)` with `(Gelman et al. 2026, §5.6)` **and** replace the sentence fragment

```
and as the model grows, tighten priors so a fixed information budget isn't spread too thin.
```

with

```
and as the model grows, tighten priors so a fixed information budget isn't spread too thin — independent `Normal(0, 1)` coefficient priors that are weak for two predictors imply a prior on the predicted probability that piles up at 0 and 1 by fifteen predictors (§5.9), which is why joint priors such as the regularized horseshoe or R2-D2 exist (see Sparsity priors below).
```

- [x] **Step 3: Add the Ch 26 pointer to `state-space.md`**

After the line ending `` is a worked JAX example. `` (line 33, end of the **Discrete latent state?** paragraph), append to that paragraph:

```
Gelman et al. 2026, Ch 26 is a full case study of the same build-then-decode HMM workflow on animal-movement data (its code is R/Stan and unlicensed — cite it, don't port it).
```

- [x] **Step 4: Verify no stale paper citation survives outside `publications.md`**
> Deviation: the `Gelman et al. 2026` count is 9, not 8 — publications.md's own key line; no action.

```bash
grep -rn 'Gelman et al. 2020\|Gelman et al. (2020)' skills/bayesian-workflow
```

Expected: exactly one hit, `skills/bayesian-workflow/references/publications.md` (the fallback entry).

```bash
grep -rn 'Gelman et al. 2026' skills/bayesian-workflow | wc -l
```

Expected: `8` (seven re-pointed citations plus the Ch 26 line).

- [x] **Step 5: Commit**

```bash
git add skills/bayesian-workflow/SKILL.md skills/bayesian-workflow/references/diagnostics.md skills/bayesian-workflow/references/priors.md skills/bayesian-workflow/references/model-comparison.md skills/bayesian-workflow/references/state-space.md
git commit -m "docs(bayesian-workflow): re-point workflow citations from the 2020 paper to the 2026 book

Paper sections do not map one-to-one onto the book: §1 -> §2.1, §3.2 ->
§11.4, §5 (folk theorem) -> §12.4, §7.3 (prior ladder) -> §5.6, §8 ->
§9.3/§9.5, §8.2 (stacking vs BMA) -> §9.6, §8.3 (projection predictive) ->
§9.6 + Ch 28. Each target page was read before the edit. Adds the §5.9
dimension point to the prior ladder and a Ch 26 pointer beside the HMM
guidance in state-space.md.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 3: `precision` block in `diagnose_model.py` (MCSE → stable digits)

Gelman et al. 2026, §11.5–11.6: report the Monte Carlo standard error next to the posterior sd, and choose reported digits so that a re-run with a new seed would not change them. The relative MCSE (`mcse_mean / sd`) maps to stable significant digits as `floor(-log10(rel))` — 10% → 1 digit, 1% → 2 (§11.6, "Rough estimates for how many iterations to run initially"). Verify by reading PDF pages 213–216 (book 201–204) before writing the docstring.

**Files:**
- Modify: `skills/bayesian-workflow/scripts/diagnose_model.py` (add `check_precision`, wire into `generate_report`)
- Create: `skills/bayesian-workflow/scripts/test_diagnose_model.py`

**Interfaces:**
- Produces: `check_precision(idata) -> dict` with schema

  ```python
  {
    "params": {"<name>": {"sd": float, "mcse_mean": float, "mcse_sd": float,
                          "rel_mcse": float, "stable_digits": int}, ...},
    "max_rel_mcse": float,            # 0.0 when no usable param
    "max_rel_mcse_param": str | None,
    "min_stable_digits": int | None,
  }
  ```
  and `generate_report(idata)["precision"]` carrying it. Task 4's prose names these keys verbatim. Parameter names are `az.summary` index labels (`beta[0]` for vectors).

- [x] **Step 1: Write the failing tests**

Create `skills/bayesian-workflow/scripts/test_diagnose_model.py`:

```python
"""Tests for diagnose_model.py — run from this directory (bare imports).

cd skills/bayesian-workflow/scripts && uv run --python 3.13 --with pytest --with arviz \
  --with arviz-stats --with numpy --with xarray python -m pytest -q
"""

import json

import arviz as az
import numpy as np

from diagnose_model import _json_default, check_precision, generate_report


def _idata(n_chains=4, n_draws=500, seed=0, extra=None):
    """Synthetic InferenceData with i.i.d. unit-normal draws (ESS ~ n_chains * n_draws)."""
    rng = np.random.default_rng(seed)
    post = {
        "mu": rng.normal(size=(n_chains, n_draws)),
        "beta": rng.normal(size=(n_chains, n_draws, 2)),
    }
    if extra:
        post.update(extra)
    stats = {"diverging": np.zeros((n_chains, n_draws), dtype=bool)}
    # arviz 1.x from_dict takes ONE dict of groups (the 0.23 kwargs form raises TypeError)
    return az.from_dict({"posterior": post, "sample_stats": stats})


def test_check_precision_iid_draws_give_one_stable_digit():
    prec = check_precision(_idata())
    mu = prec["params"]["mu"]
    # 2000 independent draws -> relative MCSE ~ 1/sqrt(2000) ~ 0.022 -> floor(-log10) == 1
    assert 0.01 < mu["rel_mcse"] < 0.05
    assert mu["stable_digits"] == 1
    assert mu["sd"] > 0 and mu["mcse_mean"] > 0 and mu["mcse_sd"] > 0
    # vector params are flattened the way az.summary labels them
    assert {"beta[0]", "beta[1]"} <= set(prec["params"])
    assert prec["max_rel_mcse_param"] in prec["params"]
    assert prec["min_stable_digits"] == 1


def test_check_precision_skips_constant_params():
    const = {"fixed": np.ones((4, 500))}
    prec = check_precision(_idata(extra=const))
    assert "fixed" not in prec["params"]
    assert "mu" in prec["params"]


def test_check_precision_empty_when_nothing_usable():
    prec = check_precision(az.from_dict({"posterior": {"fixed": np.ones((4, 500))}}))
    assert prec["params"] == {}
    assert prec["max_rel_mcse"] == 0.0
    assert prec["max_rel_mcse_param"] is None
    assert prec["min_stable_digits"] is None


def test_generate_report_carries_precision_and_serializes():
    report = generate_report(_idata())
    assert "precision" in report
    assert report["precision"]["params"]["mu"]["stable_digits"] == 1
    json.dumps(report, default=_json_default)  # must not raise
```

- [x] **Step 2: Run the tests to verify they fail**

```bash
cd skills/bayesian-workflow/scripts && uv run --python 3.13 --with pytest --with arviz --with arviz-stats --with numpy --with xarray python -m pytest -q test_diagnose_model.py
```

Expected: collection error `ImportError: cannot import name 'check_precision' from 'diagnose_model'`.

- [x] **Step 3: Implement `check_precision` and wire it in**

In `diagnose_model.py`, add `import math` to the imports, then add this function directly above `def generate_report(idata):`:

```python
def check_precision(idata):
    """Monte Carlo precision per parameter: how many significant digits of the
    posterior mean are stable under a re-run with a new seed.

    Follows Gelman et al. 2026, §11.5-11.6: report the Monte Carlo standard error
    (MCSE) beside the posterior sd and choose reported digits so the rounding
    unit exceeds ~2 * MCSE. The relative MCSE ``mcse_mean / sd`` maps to stable
    significant digits as ``floor(-log10(rel))``: 10% -> 1 digit, 1% -> 2.
    Parameters with a non-positive or non-finite sd or MCSE (deterministic
    quantities, constants) are skipped. Interval endpoints are usually less
    precise than the mean; check ``az.mcse(idata, method="quantile", prob=...)``
    separately before quoting a tail quantile to two digits.
    """
    summary = az.summary(idata)  # has sd / mcse_mean / mcse_sd on arviz 0.23 and 1.x alike
    params = {}
    for name, row in summary.iterrows():
        sd = float(row["sd"])
        mcse = float(row["mcse_mean"])
        if not (np.isfinite(sd) and np.isfinite(mcse)) or sd <= 0 or mcse <= 0:
            continue
        rel = mcse / sd
        params[str(name)] = {
            "sd": sd,
            "mcse_mean": mcse,
            "mcse_sd": float(row["mcse_sd"]),
            "rel_mcse": round(rel, 4),
            "stable_digits": int(max(0, math.floor(-math.log10(rel)))),
        }
    if not params:
        return {
            "params": {},
            "max_rel_mcse": 0.0,
            "max_rel_mcse_param": None,
            "min_stable_digits": None,
        }
    worst = max(params, key=lambda k: params[k]["rel_mcse"])
    return {
        "params": params,
        "max_rel_mcse": params[worst]["rel_mcse"],
        "max_rel_mcse_param": worst,
        "min_stable_digits": min(p["stable_digits"] for p in params.values()),
    }
```

In `generate_report`, change

```python
    report = {
        "convergence": check_convergence(idata),
        "loo": check_loo(idata),
        "posterior_predictive": check_posterior_predictive(idata),
    }
```

to

```python
    report = {
        "convergence": check_convergence(idata),
        "loo": check_loo(idata),
        "posterior_predictive": check_posterior_predictive(idata),
        "precision": check_precision(idata),
    }
```

Also update the module docstring's first paragraph to read:

```
Runs convergence checks, posterior predictive checks, LOO, and a Monte Carlo
precision block (MCSE -> stable digits), and produces a structured report.
```

- [x] **Step 4: Run the tests to verify they pass**

```bash
cd skills/bayesian-workflow/scripts && uv run --python 3.13 --with pytest --with arviz --with arviz-stats --with numpy --with xarray python -m pytest -q test_diagnose_model.py
```

Expected: `4 passed`.

If `test_generate_report_carries_precision_and_serializes` fails *inside* `check_convergence` (an `arviz_stats.diagnose` error on the synthetic idata rather than anything in `check_precision`), add `"energy": rng.normal(size=(n_chains, n_draws))` to the `stats` dict in `_idata` so E-BFMI has something to compute, and re-run. Any other failure is a real bug in this task — fix it, do not weaken the assertions.

- [x] **Step 5: Commit**

```bash
git add skills/bayesian-workflow/scripts/diagnose_model.py skills/bayesian-workflow/scripts/test_diagnose_model.py
git commit -m "feat(bayesian-workflow): report Monte Carlo precision (MCSE -> stable digits) in diagnostics.json

diagnose_model.py now emits a precision block: per-parameter sd, mcse_mean,
mcse_sd, relative MCSE and the number of significant digits of the mean that
would survive a re-run with a new seed (floor(-log10(mcse/sd)); Gelman et
al. 2026, §11.5-11.6). The skill had no MCSE guidance at all and its report
templates printed three-digit tables regardless of Monte Carlo error. First
tests for this script; uses az.summary so it works on arviz 0.23 and 1.x.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 4: Digits rule and precision rows in `reporting.md`

Read PDF pages 211–217 (book 199–205: §11.4 "How long to run", §11.5, §11.6, §11.7) before writing; the rule below paraphrases them and must not quote.

**Files:**
- Modify: `skills/bayesian-workflow/references/reporting.md` at four sites: the diagnostics table (after the `| Divergences | … |` row near line 129), the parameter table (after the `| <param_2> | … |` row near line 146), the Reporting principles list (after item 5, near line 228), and the analysis-report template's convergence list (after `- Divergences: [N] [✓ or ✗]` near line 273).

**Interfaces:**
- Consumes: `diagnostics.json → precision` keys from Task 3 (`params[name].stable_digits`, `params[name].rel_mcse`, `max_rel_mcse`, `max_rel_mcse_param`, `min_stable_digits`).

- [x] **Step 1: Add the diagnostics-table row**

After the exact row

```
| Divergences | <e.g., 0> | 0 (or near zero) | <✓ / ✗> |
```

insert

```
| Max relative MCSE | <e.g., 0.02 (β₁)> | ≤ 0.05 (≥ 1 stable digit; from `diagnostics.json → precision`) | <✓ / ✗> |
```

- [x] **Step 2: Add the rounding note under the parameter table**

After the exact row

```
| <param_2> | <m> | <s> | [<lo>, <hi>] | <prob> |
```

insert (as its own paragraph, before **Substantive interpretation.**):

```
Round every cell to the parameter's `stable_digits` from `diagnostics.json → precision` — and usually to fewer, since the posterior sd sets the meaningful digits and the MCSE only sets the *stable* ones (see Reporting principles → 6). Interval endpoints are less precise than the mean: before quoting a tail quantile to two digits, check `az.mcse(idata, method="quantile", prob=0.05)` (and `prob=0.95`).
```

- [x] **Step 3: Add Reporting principle 6**

After the exact line

```
5. **Use probability language**, not p-value language. "There is a 94% probability that θ lies in [a, b]" — not "the interval [a, b] is significant."
```

insert

```
6. **Round to what the posterior and the Monte Carlo error support** (Gelman et al. 2026, §11.4–11.6). Two separate limits: the posterior *sd* decides how many digits are *meaningful* — a mean of 1.97 with a 90% interval of [0.7, 3.2] is honestly "about 2", or "1 to 3" — and the *MCSE* decides how many are *stable* under a new seed (rounding unit ≳ 2 × MCSE). `diagnostics.json → precision` carries both per parameter as `rel_mcse` and `stable_digits`; `max_rel_mcse_param` is the parameter that limits the whole table. Never print more significant digits than `stable_digits`; usually print fewer. If you want another digit, halving the MCSE costs four times the draws (§11.4) — it is almost always better to report fewer digits or a rounder interval than to run longer. A fixed seed does not make a number reproducible in the sense that matters (§11.7): the test is whether a *different* seed gives the same *reported* digits, and that is exactly what the MCSE check certifies — so a report built from an exploration-sized run (see diagnostics.md → Exploration runs vs. the final run) must say so.
```

- [x] **Step 4: Add the template line**

After the exact line

```
- Divergences: [N] [✓ or ✗]
```

insert

```
- Relative MCSE: max [X] on [param] → [N] stable significant digit(s) ✓
```

- [x] **Step 5: Sibling sweep**

```bash
grep -n -i 'mcse\|stable_digits\|precision' skills/bayesian-workflow/references/reporting.md | wc -l
grep -rn -i 'three significant\|3 significant\|two decimal' skills/bayesian-workflow --include='*.md'
```

Expected: first count ≥ 8; second grep returns nothing (no passage elsewhere prescribes a fixed digit count). If the second grep finds one, rewrite it to defer to `stable_digits`.

- [x] **Step 6: Commit**

```bash
git add skills/bayesian-workflow/references/reporting.md
git commit -m "docs(bayesian-workflow): choose reported digits from posterior sd and MCSE

Adds Reporting principle 6 and threads diagnostics.json's new precision
block through the report templates: a max-relative-MCSE row in the
diagnostics table, a rounding note under the parameter table, and a
template line. Gelman et al. 2026 §11.4-11.7: sd sets the meaningful
digits, MCSE the stable ones; more digits cost four times the draws per
halving, so report fewer instead.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 5: RED baseline for the divergence-fraction gate (before any wording change)

The writing-skills rule: no behaviour-shaping wording change without first watching agents fail without it. The measured behaviour is **the first concrete action recommended when 8% of transitions diverge on a hierarchical model**. Two arms, five fresh reps each: **A** = no guidance, **B** = the *current* skill text. Task 8 runs arm **C** with the new text.

**Files:**
- Create (outside the repo, measurement window only): `/tmp/bw-microtest/fixture.md`, `/tmp/bw-microtest/header.md`, `/tmp/bw-microtest/promptA.md`, `/tmp/bw-microtest/promptB.md`, `/tmp/bw-microtest/ledger.md`
- Create (after the window): `specs/red-baseline-divergence-gate-<YYYY-MM-DD>.md`

**Interfaces:**
- Produces: the record file with per-rep verdicts for arms A and B and a pre-registered form decision consumed by Task 6 (recipe strength) and Task 8 (GREEN pass bar).

- [x] **Step 1: Write the fixture (contamination-checked)**

Create `/tmp/bw-microtest/fixture.md` with exactly this content:

````markdown
I fit this model for weekly visits to 48 stores grouped into 12 regions (1248 rows; `x` is a standardized promo-spend index).

```python
def model(region, x, y=None):
    mu_a = numpyro.sample("mu_a", dist.Normal(3.0, 1.0))
    sigma_region = numpyro.sample("sigma_region", dist.HalfNormal(1.0))
    beta = numpyro.sample("beta", dist.Normal(0.0, 0.5))
    with numpyro.plate("regions", 12):
        a_region = numpyro.sample("a_region", dist.Normal(mu_a, sigma_region))
    log_rate = a_region[region] + beta * x
    with numpyro.plate("obs", x.shape[0]):
        numpyro.sample("y_obs", dist.Poisson(jnp.exp(log_rate)), obs=y)

mcmc = MCMC(NUTS(model), num_warmup=1000, num_samples=1000, num_chains=4, chain_method="parallel")
```

`azs.diagnose(idata)` printed:

```
Divergences: 320 of 4000 post-warmup draws (8.0%)
R-hat > 1.01: sigma_region (1.02)
ESS bulk < 400: sigma_region (41), a_region[2] (88), a_region[7] (95)
ESS tail < 400: sigma_region (63)
E-BFMI: ok
```

Posterior summary: `sigma_region` mean 0.11, sd 0.09, 5% 0.01, 95% 0.29. Everything else looks sane.

What is the single next thing you would do, and what is the code for it? Give one step, not a list. End your answer with a line `TOOLS USED:` followed by the names of any tools you called, or `none`.
````

Then run the Channel-3 guard — the fixture must not echo the artifact under test and the artifact must not contain the fixture:

```bash
grep -n -i -E 'target_accept|adapt_delta|1%|one percent|funnel|non-centered|noncentered|reparam' /tmp/bw-microtest/fixture.md
grep -rn -i -E 'sigma_region|promo|store visits|48 stores' skills/bayesian-workflow
```

Expected: both greps print nothing. If either hits, rewrite the fixture (different domain, different names) until both are clean.

- [x] **Step 2: Write the header and assemble the two arm prompts**

Create `/tmp/bw-microtest/header.md`:

```markdown
You are the coding assistant of a data scientist who uses NumPyro. Answer in chat only. Do not read, search, or open any files; do not run code; do not invoke any skill. Everything you need is in this message.
```

Assemble the prompts. Arm B inlines the **current** SKILL.md and diagnostics.md — this task runs *before* Task 6, so the working tree is the current text:

```bash
cd /tmp/bw-microtest
{ cat header.md; echo; cat fixture.md; } > promptA.md
{ cat header.md; echo; echo 'The following reference material is already loaded in your context; it is the team standard operating guide:'; echo; echo '===== SKILL.md ====='; cat ~/Projects/agent-skills/skills/bayesian-workflow/SKILL.md; echo; echo '===== references/diagnostics.md ====='; cat ~/Projects/agent-skills/skills/bayesian-workflow/references/diagnostics.md; echo; echo '===== end of reference material ====='; echo; cat fixture.md; } > promptB.md
wc -l promptA.md promptB.md
```

Expected: promptA ≈ 35 lines, promptB ≈ 580 lines.

- [x] **Step 3: Open the quarantine window (Channels 1 and skill-autoload)**

```bash
mv ~/.claude/skills/bayesian-workflow /tmp/bw-microtest/skill-symlink.quarantine
mv ~/Projects/agent-skills/specs/plans/20-bayesian-workflow-book-integration.md /tmp/bw-microtest/plan.quarantine.md
cd ~/Projects/agent-skills && grep -rl -E 'target_accept' specs/ | sed 's|^|specs-hit: |'
```

For every `specs-hit:` path printed, move it aside too (`mv <path> /tmp/bw-microtest/quarantine-<basename>`), and write the list of moved paths to `/tmp/bw-microtest/quarantined.txt` so Step 7 can restore them. Keep the ledger (`/tmp/bw-microtest/ledger.md`) outside the repo for the whole task.

- [x] **Step 4: Dispatch arm A (5 reps) and arm B (5 reps)**
> Deviation: dispatched in two batches (A1–A5 + B1–B3, then B4–B5) from the identical prompt file inside one window, not one message — disclosed in the record.

Use the Agent tool, `subagent_type: general-purpose`, `model: opus` (the model this skill runs under by default), one call per rep, all ten in a single message so they run concurrently. The `prompt` of each call is the **full text** of `promptA.md` (reps A1–A5) or `promptB.md` (reps B1–B5). Description for every call: `Step 5 of 10` (opaque — do not name the skill, the arm, or the behaviour). Do not add any framing beyond the file contents.

- [x] **Step 5: Score every rep by hand and record it in the ledger**
> Deviation: every opus rep reported `TOOLS USED: advisor` (the harness's model-consult; no file access; present in every arm), so the VOID rule as written would void all ten; not applied — disclosed and justified in the record's Fixture section.

Rubric (pre-registered; apply to the **first** concrete action — the first numbered step, or the first code change if there are no numbers):

- **FAIL** — raises `target_accept_prob` (or `adapt_delta` / `max_tree_depth`), alone or as the first item of a combined step.
- **PASS** — inspects geometry first (`plot_pair` on `sigma_region` vs an `a_region[k]`, per-chain traces, rank plots), or reparameterizes (non-centered), or centers/scales predictors, or tightens the scale prior, or simplifies the model.
- **PARTIAL** — a combined first step that both raises `target_accept_prob` and does one of the PASS actions → counts as FAIL for the decision rule (the point of the gate is *not* to raise at 8%).
- **VOID** — the rep read files, invoked a skill, or its `TOOLS USED:` line names any tool; also VOID if it quotes text that only exists in the quarantined files. Replace a VOID rep with a fresh one (same prompt) and note it.

Contamination check for VOID:

```bash
ls -t ~/.claude/projects/-Users-lowell-Projects-agent-skills/*/subagents/*.jsonl 2>/dev/null | head -12 | xargs -I{} sh -c 'grep -l -E "\"name\":\"(Read|Grep|Glob|Skill|Bash|WebFetch)\"" {} && echo "  ^ tool use in {}"' 2>/dev/null
```

Any file printed → its rep is VOID. If the `subagents/` directory does not exist on this build, rely on the `TOOLS USED:` self-report plus the quoted-text test.

Append one row per rep to `/tmp/bw-microtest/ledger.md`:

```markdown
| rep | first action (≤ 15 words, quoted) | verdict | evidence of contamination |
|---|---|---|---|
| A1 | "…" | PASS/FAIL/PARTIAL/VOID | none / <quote> |
```

- [x] **Step 6: Apply the pre-registered decision rule and write the record**
> Deviation: the recipe-form decision is load-bearing on scoring B3/B4 as PARTIAL (both bundled `target_accept_prob=0.9` "as the template baseline"); a lenient reading gives the one-line form — disclosed in the record. Moot in the direction that matters: the recipe form measured C_fail 0/5 in both GREEN rounds.

Counts to compute: `A_fail`, `B_fail` out of 5 each (PARTIAL counts as FAIL).

- **B_fail ≥ 3** → the current wording binds agents to raise-first; Task 6 writes the gate in **recipe form** (the full conditional rung as drafted there).
- **B_fail ≤ 1** → the current wording does not bind; Task 6 still makes the change (the text contradicts its own cited source) but the gate can stay a **one-line conditional** — delete the second sentence of the rung ("at that level the geometry …") and keep the predicate and the pointer.
- **B_fail = 2** → recipe form (ties go to the stronger form; no nuance clauses).
- `A_fail` is recorded for the two-arm contrast (it tells whether the failure is *caused* by the skill or *native* to the model) and does not change the form.
- **GREEN pass bar for Task 8 (fixed now):** `C_fail ≤ 1` **and** at least 4 of 5 C reps name the same first action (variance is a metric).

Create `specs/red-baseline-divergence-gate-<YYYY-MM-DD>.md` (date = today) with this structure, filling every bracket from the ledger:

```markdown
# RED baseline — divergence-fraction gate in `bayesian-workflow`

**Date:** <YYYY-MM-DD> · **Status:** RED complete; GREEN pending (Task 8 of plan 20).
**Governs:** whether the "raise `target_accept_prob` first" rung in `references/diagnostics.md`
binds agents to a first action that Gelman et al. 2026 §12.3 says will not help above ~1% divergences.

> ⚠️ **Quarantine this file during any future micro-test of `bayesian-workflow`.** It names
> the skill and states the expected failure — Channel 1 per `microtest-isolation-channels`.

## Measured behaviour

First concrete action recommended for a varying-intercept Poisson model with 320/4000 (8%)
divergent transitions, R-hat 1.02 and bulk-ESS 41 on the group scale. Rubric: FAIL = raise
`target_accept_prob` / `adapt_delta` / `max_tree_depth` first (PARTIAL counts as FAIL);
PASS = inspect geometry, reparameterize, center predictors, tighten the scale prior, or simplify.

## Fixture

Store-visits Poisson model, 12 regions, centered hierarchical prior (a funnel by construction).
Fixture and artifact cross-grepped clean for `target_accept|1%|funnel|non-centered|reparam` and
`sigma_region|promo|store visits` respectively. Prompts assembled from files outside the repo; skill
symlink and every `specs/` file mentioning `target_accept` moved aside for the window.
Dispatch: Agent tool, general-purpose, opus, opaque description, 5 reps per arm, fresh context each.

## Result

| rep | arm | first action | verdict | contamination |
|---|---|---|---|---|
| A1 | no guidance | "<quote>" | <verdict> | <none/quote> |
| … | | | | |
| B5 | current skill | "<quote>" | <verdict> | <none/quote> |

**A_fail = <n>/5 · B_fail = <n>/5 (VOID replaced: <list or none>)**

## Decision (pre-registered rule applied)

<recipe form | one-line conditional> for the rung, because B_fail = <n>.
GREEN pass bar: C_fail ≤ 1 and ≥ 4/5 C reps converge on the same first action.

## Qualitative evidence

<2–5 bullets: verbatim rationalizations from FAIL reps ("smaller steps will fix the
divergences…"), and what PASS reps looked at first. Keep the quotes — they are evidence and
later inform the rung's wording.>
```

- [x] **Step 7: Close the quarantine window**

```bash
mv /tmp/bw-microtest/skill-symlink.quarantine ~/.claude/skills/bayesian-workflow
mv /tmp/bw-microtest/plan.quarantine.md ~/Projects/agent-skills/specs/plans/20-bayesian-workflow-book-integration.md
cat /tmp/bw-microtest/quarantined.txt   # restore each listed path with mv, one per line
ls -la ~/.claude/skills/bayesian-workflow ~/Projects/agent-skills/specs/plans/
cd ~/Projects/agent-skills && git status --short specs/
```

Expected: the symlink is back and resolves; the plan file is back; `git status` shows no deleted `specs/` files (the pre-existing modified/untracked entries from the Source-facts section are fine).

- [x] **Step 8: Commit the record**

```bash
git add specs/red-baseline-divergence-gate-*.md
git commit -m "test(bayesian-workflow): RED baseline for the divergence-fraction gate

Measures the first action agents recommend at 8% divergent transitions on a
centered hierarchical model, with no guidance (A) and with the current skill
text (B), 5 fresh reps each. Pre-registers the wording form for the gate and
the GREEN pass bar before the wording changes.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 6: Divergence gate, failure signatures, and run sizing in `diagnostics.md` + SKILL.md

Read PDF pages 221–222 (book 209–210, §12.1), 224–238 (book 212–226, §12.3), 239–241 (book 227–229, §12.4), and 210–212 (book 198–200, §11.4) before writing. All prose below is original; check it against those pages for accuracy, not wording.

**Files:**
- Modify: `skills/bayesian-workflow/references/diagnostics.md` — Contents list (lines 3–11); insert a new section after the Quick diagnostic checklist (after line 48); line 81; the fix-list step 1 (line 101); insert a new section before `## When sampling fails: the escalation ladder` (line 120); replace the ladder intro + rung 1 (lines 122–124, post-Task-2 text).
- Modify: `skills/bayesian-workflow/SKILL.md` — the Chains paragraph (ends line 237 `low-memory fallback.`); the `| Divergences |` row (line 341); add one line after the "When things go wrong" table (after line 351).

**Interfaces:**
- Consumes: the form decision from Task 5's record (recipe vs one-line conditional).
- Produces: section headings `## Exploration runs vs. the final run` and `## Failure signatures` in `diagnostics.md` — Task 4's principle 6 and Task 7's suggestion text link to them by these exact names.

- [x] **Step 1: Update the Contents list**

Replace the Contents block at the top of `diagnostics.md`:

```
## Contents
- Quick diagnostic checklist
- R-hat
- Effective sample size (ESS)
- Divergences
- When sampling fails: the escalation ladder
- Trace plots and rank plots
- Energy diagnostics
- Automated diagnostics workflow
```

with

```
## Contents
- Quick diagnostic checklist
- Exploration runs vs. the final run
- R-hat
- Effective sample size (ESS)
- Divergences
- Failure signatures
- When sampling fails: the escalation ladder
- Trace plots and rank plots
- Energy diagnostics
- Automated diagnostics workflow
```

- [x] **Step 2: Insert "Exploration runs vs. the final run"**

Insert before the line `## R-hat` (after the paragraph ending `fall back to the manual checks below.`):

```markdown
## Exploration runs vs. the final run

Most fits in a workflow are provisional — poor in retrospect, and unavoidable on the way to the useful model (Gelman et al. 2026, §2.1). Size each run to the question you are asking of it (§11.4, §12.1, §12.4):

| Phase | Settings | Accept when |
|---|---|---|
| **Exploring** — does this model fit at all? does the new component break sampling? | `num_warmup=200, num_samples=200, num_chains=4` (raise to 500/500 only if warmup is visibly unfinished) | R-hat ≤ 1.1, no chain stuck or drifting, divergences ≤ ~1% — enough to decide *keep / change / discard* |
| **Final** — the numbers go in the report | `num_warmup=1000, num_samples=1000, num_chains=4` (the template default) | R-hat ≤ 1.01, ESS_bulk and ESS_tail ≥ 100 × n_chains, zero divergences, **and** relative MCSE small enough for the digits you will report (`diagnostics.json → precision`; see reporting.md → Reporting principles 6) |

This is the "fit fast, fail fast" rule (§12.1): a model that is slow or badly behaved at 200 draws will not be rescued by 2000, and long chains on a model you are still debugging spend compute on a posterior you will throw away. When a big model is slow, the book's own advice (§12.4) is to fit on simulated data, build up from a smaller model, run few iterations, fit on a subset of the data, and put at least moderately informative priors on coefficients and group-level scales — *then* run long. Report numbers only from a final-phase run; if a report has to be built from an exploration run, say so in it.
```

- [x] **Step 3: Qualify the ESS bullet**

Replace the exact line

```
- Increase `target_accept_prob` (trades speed for better exploration)
```

with

```
- Increase `target_accept_prob` (trades speed for better exploration) — for divergence-driven ESS loss only, and only when divergences are ≤ ~1% of transitions (see the gate below)
```

- [x] **Step 4: Gate the fix-list step 1**

Replace the exact line

```
1. **Increase `target_accept_prob`**: `NUTS(model, target_accept_prob=0.95)` — try up to 0.99
```

with

```
1. **Only when divergences are ≤ ~1% of post-warmup transitions, increase `target_accept_prob`**: `NUTS(model, target_accept_prob=0.95)` — try up to 0.99. Above ~1% a smaller step size trades a fast wrong fit for a slow wrong fit (Gelman et al. 2026, §12.3) — skip to 2–4 and the Failure signatures table below.
```

- [x] **Step 5: Insert the "Failure signatures" section**
> Deviation: four rows (unused parameter, unconstrained scale, varying curvature, mixture aliasing) rewritten to NumPyro-observable symptoms after review, PDF-verified; three rows touched again in the final-review fix (tree-depth cue, aliasing fix cell, no "rejected proposals").

Insert immediately before the line `## When sampling fails: the escalation ladder`:

```markdown
## Failure signatures

What the diagnostics look like for the common ways a fit goes wrong, what each usually means, and where to look in a NumPyro model (Gelman et al. 2026, §12.3). Read this table before touching a sampler setting: the fix is almost always in the model.

| Signature | Usual cause | Check / fix in NumPyro |
|---|---|---|
| Chains drift to ±1e20, R-hat ≈ 3, most transitions hit max tree depth | **Improper or near-improper posterior** — a site under `dist.ImproperUniform`, or a `Normal(0, 100)`-class prior on a logistic coefficient whose classes are separated | Give every site a proper prior on the scale the parameter actually lives on (`Normal(0, 2.5)` for a standardized logistic coefficient). Raising `max_tree_depth` never helps here |
| One site's trace random-walks with no bound while everything else converges | **Unused parameter** — sampled but never reaches the likelihood (a typo, or a branch that never uses it); its posterior *is* its prior | `numpyro.render_model(model, model_args=...)` shows the orphan node with no path to `y_obs`; delete the site or wire it in |
| Sampling slow (many leapfrog steps), ESS lower than expected, *no* warnings; pair plot shows a straight-line ridge with correlation ≈ ±1 | **Aliased parameters** — two sites play one role: an intercept plus a constant predictor column; item ability vs. item difficulty with no anchor; a mixture scale vs. its label | Only the sum or ratio is identified. Drop one, anchor a reference level, use a sum-to-zero contrast, or add a prior that separates them — see the identifiability rule in SKILL.md |
| Slow, bulk-ESS in the low hundreds where thousands are expected, strong intercept–slope correlation | **Uncentered predictors** — the intercept means "outcome at x = 0", far outside the data | Center (and scale) predictors before the fit; the book's own regression example gains ~3× ESS and >20× speed from centering alone. `dense_mass=True` is the second-best fix |
| R-hat ≫ 1 on a location parameter with **tail-ESS far above bulk-ESS**, bimodal histogram, chains flat at different values | **Multimodal posterior** — chains stuck in separate modes (mixture, non-log-concave likelihood, heavy-tailed prior) | More chains from dispersed inits to map the modes; then decide whether the extra modes carry mass (stack chains by LOO weight — Yao, Vehtari & Gelman 2022) or are artifacts to exclude by inits or priors. An `ordered` constraint fixes mixture label switching |
| Two chains fine, two stuck at their initial values; `-inf`/NaN log-density at init | **Overflow at initialization** — NumPyro's default `init_to_uniform` (radius 2 on the unconstrained scale) plus predictors far from unit scale gives `exp(huge)` | Scale predictors to unit scale, or `NUTS(model, init_strategy=init_to_median)` / `init_to_value(values={...})` / `init_to_uniform(radius=0.1)`. Not a step-size problem |
| Divergences with R-hat near threshold and low ESS; rank-ECDF fans out at the extremes | **Varying curvature** — thick-tailed priors on unconstrained parameters (`Cauchy` on a regression coefficient), or a thin-tailed posterior | Use `Normal` or `StudentT` with moderate `df` on unconstrained parameters. `HalfCauchy` on a *positive* scale is fine: the log transform NumPyro applies tames the tail |
| Divergences cluster where a group-level scale → 0; `log(sigma)` vs a group mean is a funnel | **Funnel** — hierarchical prior with a weak per-group likelihood | Non-centered `LocScaleReparam` (Divergences, above). If per-group data are *strong*, non-centering hurts — keep centered; mixed strength → per-group choice |
| Sporadic "scale must be positive" warnings, many rejected proposals, some divergences | **Scale parameter left unconstrained** — a `Normal` prior on `sigma` instead of `HalfNormal`/`LogNormal`/`Exponential` | NumPyro derives the constraint from the *prior's support*, so the fix is the prior family, never a manual `jnp.abs` |

Moves that help regardless of signature (§12.4): a **weak-prior probe** (`Normal(0, 100)` on everything shows what blows up when nothing holds it), a **strong-prior probe** (pin parameters near plausible values, then loosen one at a time), **simplify from both ends** (fit models simpler than yours until one works and more complex than the working one until it breaks — the bug lives in between), and the **fake-data check** (simulate from known parameters, refit, recover — model-criticism.md → SBC).
```

- [x] **Step 6: Replace the ladder intro and rung 1**
> Deviation: the plan's folk-theorem clause was a verbatim 12-word book sentence (p. 227); reworded to original wording under the no-quoted-sentences constraint. Rung 1's `> 1` consequent was later tightened in Task 8 (one action: pair-plot the flagged scale against a child, before any refit).

Replace the two lines (post-Task-2 text; rung 1 begins `1. **Raise`):

```
When sampling is broken — persistent divergences, R-hat > 1.01, low ESS, or stuck/separated chains — escalate in this order, **re-checking diagnostics after each rung and stopping at the first that fixes it.** Don't jump to a model rewrite when a sampler setting would do, and don't re-run an unchanged model hoping it converges. (For divergences *specifically*, the targeted fixes above are the first thing to try; the ladder is the general path when problems persist or aren't divergence-specific.) This is the "folk theorem of statistical computing": when you have computational problems, often there's a problem with your model (Gelman et al. 2026, §12.4).

1. **Raise `target_accept_prob` (→ 0.95, then 0.99).** Smaller steps, fewer divergences. *Check:* divergences fall toward zero — a handful remaining with healthy R-hat/ESS is often acceptable.
```

with — **recipe form** (use this when Task 5 decided "recipe"):

```
When sampling is broken — persistent divergences, R-hat > 1.01, low ESS, or stuck/separated chains — first match the symptoms against the Failure signatures table, then escalate in this order, **re-checking diagnostics after each rung and stopping at the first that fixes it.** Don't jump to a model rewrite when a sampler setting would do, and don't re-run an unchanged model hoping it converges. This is the "folk theorem of statistical computing": when you have computational problems, often there's a problem with your model (Gelman et al. 2026, §12.4).

1. **Read the divergence fraction before touching the sampler.** `pct = 100 * n_div / (num_chains * num_samples)`. **If `pct` ≤ 1 and R-hat/ESS are otherwise healthy** → raise `target_accept_prob` (→ 0.95, then 0.99): smaller steps clear a few divergences at a curvature edge. *Check:* divergences fall toward zero — a handful remaining with healthy R-hat/ESS is often acceptable. **If `pct` > 1, or the divergences come with R-hat > 1.05 or ESS far below threshold** → do not raise `target_accept_prob` and do not raise `max_tree_depth`: at that level the geometry or the identification is wrong, and a smaller step only makes the wrong posterior slower to sample (Gelman et al. 2026, §12.3). Go straight to `az.plot_pair(idata, var_names=[...])` on the flagged scale/location pairs, the Failure signatures table, and rungs 5–7.
```

or — **one-line conditional** (use this when Task 5 decided "one-line"): the same intro paragraph, and rung 1 as

```
1. **If divergences are ≤ ~1% of post-warmup transitions and R-hat/ESS are otherwise healthy, raise `target_accept_prob` (→ 0.95, then 0.99).** *Check:* divergences fall toward zero. Above ~1% skip this rung — a smaller step does not fix geometry (Gelman et al. 2026, §12.3); go to the Failure signatures table and rungs 5–7.
```

- [x] **Step 7: SKILL.md — Chains paragraph, table row, pointer line**

(a) The Chains paragraph's last sentence wraps across two lines and ends on the line reading exactly `low-memory fallback.` (line 237). Append to that line, as part of the same paragraph:

```
Size the run to the phase: exploration fits at `num_warmup=200, num_samples=200` accept R-hat ≤ 1.1; the 1000/1000 template default is the *final* run (Gelman et al. 2026, §11.4, §12.1 — see diagnostics.md → Exploration runs vs. the final run).
```

(b) Replace the exact table row

```
| Divergences | Posterior geometry issue | Reparameterize (non-centered via `LocScaleReparam`), raise `target_accept_prob` to 0.95-0.99 |
```

with

```
| Divergences | Posterior geometry issue | ≤ ~1% of transitions: raise `target_accept_prob` to 0.95–0.99. More than that: don't — reparameterize (non-centered via `LocScaleReparam`), center predictors, check `az.plot_pair`; see diagnostics.md → Failure signatures (Gelman et al. 2026, §12.3) |
```

(c) After the table's last row (`| Prior sensitivity flag | … |`), add a blank line and:

```
For the fuller catalog of failure signatures — improper posterior, unused parameter, aliasing, uncentered predictors, multimodality, overflow at init, varying curvature, funnel, unconstrained scale — and what each looks like in the diagnostics, see [references/diagnostics.md](references/diagnostics.md) → Failure signatures.
```

- [x] **Step 8: Sibling sweep and lints**

```bash
grep -rn -E 'target_accept|adapt_delta' skills/bayesian-workflow --include='*.md'
```

Expected hits and their required state: SKILL.md template/sampler lines (`target_accept_prob=0.9`, unchanged — those are defaults, not advice); SKILL.md horseshoe gotcha and priors.md:169 (unchanged — a *pre-emptive* 0.95 for a known double-funnel geometry is not the divergence-response rule); SKILL.md table row (gated, Step 7b); diagnostics.md:81, fix-list step 1, and rung 1 (all gated). Any other hit that tells the agent to raise `target_accept_prob` *in response to divergences* must carry the ≤ ~1% condition — fix it.

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py && echo FM-OK
```

Expected: `FM-OK`.

- [x] **Step 9: Commit**

```bash
git add skills/bayesian-workflow/SKILL.md skills/bayesian-workflow/references/diagnostics.md
git commit -m "docs(bayesian-workflow): gate target_accept on the divergence fraction; add failure signatures and run sizing

Rung 1 of the escalation ladder told agents to raise target_accept_prob
first, unconditionally. Gelman et al. 2026 §12.3 is explicit that above ~1%
divergent transitions a smaller step size does not help - the geometry or
identification is wrong - so rung 1, the divergence fix-list, the SKILL.md
symptom table and the ESS bullet now condition on the fraction. Adds the
§12.3 failure-signature catalog (improper posterior, unused parameter,
aliasing, uncentered predictors, multimodality via tail-ESS >> bulk-ESS,
init overflow, varying curvature, funnel, unconstrained scale) with the
NumPyro-side check for each, and the §11.4/§12.1/§12.4 exploration-vs-final
run sizing the skill previously did not distinguish. RED baseline in
specs/red-baseline-divergence-gate-*.md; GREEN follows.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 7: Gate the divergence suggestion in `check_diagnostics.py`

`suggest_next_steps` currently always ends its divergence step with "increase target_accept_prob to 0.95–0.99". Make it consistent with Task 6.

**Files:**
- Modify: `skills/bayesian-workflow/scripts/check_diagnostics.py` (constant near line 32; `check_diagnostics()` near line 188; `suggest_next_steps()` near line 283)
- Create: `skills/bayesian-workflow/scripts/test_check_diagnostics.py`

**Interfaces:**
- Consumes: `diagnostics["convergence"]["divergences"]["pct"]` (percent, already emitted by `diagnose_model.check_convergence` on both code paths).
- Produces: `report["convergence"]["divergence_pct"]: float`; module constant `DIVERGENCE_GATE_PCT = 1.0`.

- [x] **Step 1: Write the failing tests**
> Deviation: one-character unbalanced-paren fix to the brief's test code (SyntaxError otherwise).

Create `skills/bayesian-workflow/scripts/test_check_diagnostics.py`:

```python
"""Tests for check_diagnostics.py — run from this directory (bare imports).

cd skills/bayesian-workflow/scripts && uv run --python 3.13 --with pytest --with arviz \
  --with arviz-stats --with numpy --with xarray python -m pytest -q
"""

from check_diagnostics import DIVERGENCE_GATE_PCT, check_diagnostics, suggest_next_steps


def _diagnostics(n_div, pct):
    """Minimal diagnose_model-shaped input: only divergences are flagged."""
    return {
        "convergence": {
            "all_ok": False,
            "method": "manual",
            "rhat": {"ok": True, "max": 1.003, "problematic_params": []},
            "ess_bulk": {"ok": True, "min": 900, "problematic_params": []},
            "ess_tail": {"ok": True, "min": 900, "problematic_params": []},
            "divergences": {"count": n_div, "pct": pct, "ok": False},
        },
        "loo": {"computed": False, "error": "no log_likelihood group"},
        "posterior_predictive": {"available": False},
    }


def _divergence_step(steps):
    hits = [s for s in steps if "ivergence" in s]
    assert len(hits) == 1, steps
    return hits[0]


def test_gate_constant_is_one_percent():
    assert DIVERGENCE_GATE_PCT == 1.0


def test_report_carries_divergence_pct():
    report = check_diagnostics(diagnostics=_diagnostics(320, 8.0))
    assert report["convergence"]["divergence_pct"] == 8.0


def test_many_divergences_do_not_suggest_raising_target_accept():
    step = _divergence_step(suggest_next_steps(check_diagnostics(diagnostics=_diagnostics(320, 8.0))))
    assert "8.0%" in step
    assert "Do not raise target_accept_prob" in step
    assert "plot_pair" in step and "Failure signatures" in step


def test_few_divergences_suggest_raising_target_accept_first():
    step = _divergence_step(suggest_next_steps(check_diagnostics(diagnostics=_diagnostics(3, 0.08)))
    assert "raise target_accept_prob to 0.95" in step
    assert "Do not raise" not in step


def test_no_divergences_no_divergence_step():
    diag = _diagnostics(0, 0.0)
    diag["convergence"]["divergences"]["ok"] = True
    diag["convergence"]["all_ok"] = True
    assert not [s for s in suggest_next_steps(check_diagnostics(diagnostics=diag)) if "ivergence" in s]
```

- [x] **Step 2: Run the tests to verify they fail**

```bash
cd skills/bayesian-workflow/scripts && uv run --python 3.13 --with pytest --with arviz --with arviz-stats --with numpy --with xarray python -m pytest -q test_check_diagnostics.py
```

Expected: collection error `ImportError: cannot import name 'DIVERGENCE_GATE_PCT'`.

- [x] **Step 3: Implement**

(a) Under the existing line `DIVERGENCE_FAIR = 0.005  # < 0.5% of post-warmup draws` add:

```python
DIVERGENCE_GATE_PCT = 1.0  # percent; above this, raising target_accept_prob rarely helps (Gelman et al. 2026, §12.3)
```

(b) In `check_diagnostics()`, replace

```python
        conv_rating, conv_issues = _rate_convergence(diagnostics.get("convergence", {}))
        report["convergence"] = {
            "rating": conv_rating,
            "problematic_params": conv_issues,
        }
```

with

```python
        conv_in = diagnostics.get("convergence", {})
        conv_rating, conv_issues = _rate_convergence(conv_in)
        report["convergence"] = {
            "rating": conv_rating,
            "problematic_params": conv_issues,
            # percent of post-warmup transitions that diverged; drives the
            # target_accept_prob gate in suggest_next_steps
            "divergence_pct": float((conv_in.get("divergences") or {}).get("pct", 0.0) or 0.0),
        }
```

(c) In `suggest_next_steps()`, replace

```python
        if has_divergences:
            steps.append(
                "Divergences detected — reparameterize the affected component "
                "(non-centered via numpyro.infer.reparam.LocScaleReparam for hierarchical "
                "scales; replace HalfCauchy with Gamma(2, ...) for scale priors) and increase "
                "target_accept_prob to 0.95–0.99 on the NUTS kernel."
            )
```

with

```python
        if has_divergences:
            pct = float(conv.get("divergence_pct", 0.0) or 0.0)
            if pct > DIVERGENCE_GATE_PCT:
                steps.append(
                    f"Divergences are {pct:.1f}% of post-warmup transitions — above the ~1% level "
                    "at which a smaller step size stops helping (Gelman et al. 2026, §12.3). "
                    "Do not raise target_accept_prob or max_tree_depth. Inspect the geometry "
                    "first: az.plot_pair(idata, var_names=[...]) on the flagged scale/location "
                    "pairs, then reparameterize (non-centered via "
                    "numpyro.infer.reparam.LocScaleReparam), center predictors, or tighten scale "
                    "priors (replace HalfCauchy with Gamma(2, ...)). See references/diagnostics.md "
                    "→ Failure signatures."
                )
            else:
                steps.append(
                    f"Divergences are {pct:.2f}% of transitions (≤ 1%) — raise target_accept_prob "
                    "to 0.95–0.99 on the NUTS kernel first; if any remain, reparameterize the "
                    "affected component (non-centered via numpyro.infer.reparam.LocScaleReparam "
                    "for hierarchical scales) or replace HalfCauchy with Gamma(2, ...) on scale "
                    "priors."
                )
```

- [x] **Step 4: Run both test files**

```bash
cd skills/bayesian-workflow/scripts && uv run --python 3.13 --with pytest --with arviz --with arviz-stats --with numpy --with xarray python -m pytest -q
```

Expected: `9 passed` (4 from Task 3 + 5 here).

- [x] **Step 5: Smoke the CLI end to end on the synthetic idata**

```bash
mkdir -p /tmp/bwprobe && cd /tmp/bwprobe && cat > smoke_plan20.py <<'EOF'
import json, subprocess, sys
import numpy as np, arviz as az
rng = np.random.default_rng(1)
n_c, n_d = 4, 500
div = np.zeros((n_c, n_d), dtype=bool); div[0, :160] = True   # 160/2000 = 8%
idata = az.from_dict({"posterior": {"mu": rng.normal(size=(n_c, n_d))},
                      "sample_stats": {"diverging": div}})
idata.to_netcdf("smoke.nc")
S = "/Users/lowell/Projects/agent-skills/skills/bayesian-workflow/scripts"
subprocess.run([sys.executable, f"{S}/diagnose_model.py", "--idata", "smoke.nc", "--output", "diag.json"], check=True)
subprocess.run([sys.executable, f"{S}/check_diagnostics.py", "--diagnostics", "diag.json", "--output", "check.json"], check=True)
d = json.load(open("diag.json")); c = json.load(open("check.json"))
print("precision:", d["precision"]["max_rel_mcse_param"], d["precision"]["min_stable_digits"])
print("div pct:", d["convergence"]["divergences"]["pct"], "->", c["convergence"]["divergence_pct"])
print([s for s in c["next_steps"] if "ivergence" in s][:1])
EOF
uv run --python 3.13 --with arviz --with arviz-stats --with numpy --with xarray --with h5netcdf --with h5py python smoke_plan20.py
```

Expected: `precision: mu 1`, `div pct: 8.0 -> 8.0`, and one printed step beginning `Divergences are 8.0% of post-warmup transitions — above the ~1% level`.

- [x] **Step 6: Commit**

```bash
git add skills/bayesian-workflow/scripts/check_diagnostics.py skills/bayesian-workflow/scripts/test_check_diagnostics.py
git commit -m "feat(bayesian-workflow): gate the divergence next-step on the divergence fraction

suggest_next_steps always told the report to raise target_accept_prob. Above
~1% divergent transitions that advice is wrong (Gelman et al. 2026, §12.3),
and the report's Suggested Next Steps must agree with diagnostics.md rung 1
(previous commit). Carries divergence_pct through the interpreted report and
branches on DIVERGENCE_GATE_PCT = 1.0. First tests for this script.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 8: GREEN run for the gate (arm C) and refactor loop

**Files:**
- Create (window only): `/tmp/bw-microtest/promptC.md`
- Modify: `specs/red-baseline-divergence-gate-<date>.md` (append the GREEN section; flip Status)
- Possibly modify: `skills/bayesian-workflow/references/diagnostics.md` (rung 1 wording, if the pass bar is missed)

**Interfaces:**
- Consumes: the pass bar from Task 5's record (`C_fail ≤ 1` and ≥ 4/5 converge).

- [x] **Step 1: Assemble the arm-C prompt from the post-Task-6 text and re-run the Channel-3 guard**

```bash
cd /tmp/bw-microtest
{ cat header.md; echo; echo 'The following reference material is already loaded in your context; it is the team standard operating guide:'; echo; echo '===== SKILL.md ====='; cat ~/Projects/agent-skills/skills/bayesian-workflow/SKILL.md; echo; echo '===== references/diagnostics.md ====='; cat ~/Projects/agent-skills/skills/bayesian-workflow/references/diagnostics.md; echo; echo '===== end of reference material ====='; echo; cat fixture.md; } > promptC.md
grep -c 'Failure signatures' promptC.md
grep -rn -i -E 'sigma_region|promo|store visits|48 stores' ~/Projects/agent-skills/skills/bayesian-workflow
```

Expected: the count is ≥ 3 (the new section is in the prompt); the second grep prints nothing (Task 6 did not smuggle the fixture into the artifact).

- [x] **Step 2: Open the quarantine window** — exactly Task 5 Step 3 (symlink, this plan file, every `specs/` file matching `target_accept`, **and now also** `specs/red-baseline-divergence-gate-*.md`, which states the expected verdict). Record the moved paths in `/tmp/bw-microtest/quarantined.txt`.

- [x] **Step 3: Dispatch arm C (5 reps)** — Agent tool, `general-purpose`, `model: opus`, description `Step 8 of 10`, prompt = full text of `promptC.md`, five calls in one message.
> Deviation: five calls in one message is not achievable (the ~53 KB prompt fits twice per dispatch message); both GREEN rounds went 2+2+1 from the identical file inside one window — disclosed in the record.

- [x] **Step 4: Score with the Task 5 rubric, append to the ledger, run the contamination check** (same command as Task 5 Step 5). Replace VOID reps.

- [x] **Step 5: Apply the pass bar**
> Deviation: round 1 missed the convergence half (C_fail 0/5, but first actions split 2 non-center / 2 pair-plot / 1 data check because rung 1 ended in three destinations); refactored to one action and propagated to fix-list step 1 and the SKILL.md row (outside this task's Files list — sibling-propagation constraint); round 2: C_fail 0/5, 5/5 pair plot. Both rounds recorded.

- **Pass** (`C_fail ≤ 1` and ≥ 4/5 name the same first action) → Step 7.
- **Miss** → REFACTOR per writing-skills: tighten the *form* of rung 1 (recipe over prohibition; a conditional on an observable predicate; no nuance clauses; if reps rationalized "a few divergences are fine, so raise it and see", add the divergence *count* to the predicate rather than an exception clause), re-run five fresh C reps, and record **both** rounds. Two misses in a row → stop, keep the second-round wording, and report the miss at the completion gate rather than iterating blind.

- [x] **Step 6: Close the quarantine window** — exactly Task 5 Step 7, plus restore the red-baseline record.

- [x] **Step 7: Append the GREEN section to the record and flip its status**

Change the Status line to `**Status:** RED + GREEN complete (plan 20, Tasks 5 and 8).` and append:

```markdown
## GREEN (new wording — Task 6 recipe / one-line form: <which>)

| rep | first action | verdict | contamination |
|---|---|---|---|
| C1 | "<quote>" | <verdict> | <none/quote> |
| … | | | |

**C_fail = <n>/5 · convergence: <n>/5 named "<action>" first.** Pass bar <met / missed → refactor round 2: …>.

## Disposition

<One paragraph: what the three-arm contrast shows (native vs. skill-caused failure), what the
wording now makes agents do first, and anything the reps did that the failure-signatures table
should say and does not.>
```

- [x] **Step 8: Commit**

```bash
git add specs/red-baseline-divergence-gate-*.md skills/bayesian-workflow/references/diagnostics.md
git commit -m "test(bayesian-workflow): GREEN run for the divergence-fraction gate

Five fresh reps with the new diagnostics.md text against the same 8%-
divergence fixture as the RED baseline. Records first actions, pass-bar
outcome, and any wording refactor.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

(If diagnostics.md did not change in this task, omit it from `git add`.)

---

### Task 9: Rewrite the SBC section of `model-criticism.md` to §14.1–14.3 practice

Read PDF pages 261–265 (book 249–253) before writing. Verify the plotting snippet **before** it goes into the reference — this skill's history (commit `c707a48`, "repair crashing prior-predictive recipe") is exactly a recipe that shipped unrun.

**Files:**
- Modify: `skills/bayesian-workflow/references/model-criticism.md` — the Contents entry `- Simulation-based calibration (SBC)` and the whole section from `## Simulation-based calibration (SBC)` through the line beginning `**When to run SBC**:` (inclusive; the next line is `## Residual analysis`).

**Interfaces:**
- Consumes: nothing from earlier tasks beyond the citation key.

- [x] **Step 1: Prove the Δ-ECDF snippet runs on the resolved stack**
> Deviation: the snippet ran unchanged, but the plan's Source-facts claim that `plot_ecdf_pit` "draws a simultaneous band" is false for the default `method="pot_c"` on arviz-plots 1.3.1 (it draws the Δ-ECDF, a zero line, highlighted suspicious points and a p-value at α = 1 − rcParams["stats.envelope_prob"] = 0.01); `method="envelope"` is deprecated and raised a TypeError. The reference describes the default rendering; the fact was propagated to the PPC/LOO-PIT passages.

```bash
mkdir -p /tmp/bwprobe && cd /tmp/bwprobe && cat > sbc_ecdf_probe.py <<'EOF'
import numpy as np, arviz as az, arviz_plots as azp
rng = np.random.default_rng(0)
L, S = 100, 200
ranks = rng.integers(0, L + 1, size=S)                    # uniform ranks = a correct pipeline
pit = (ranks + 0.5) / (L + 1)                             # ranks in [0, L] -> PIT in (0, 1)
sbc_dt = az.from_dict({"prior_sbc": {"beta": pit[None, :]}})   # (chain=1, draw=S)
pc = azp.plot_ecdf_pit(sbc_dt, var_names=["beta"])
pc.savefig("sbc_ecdf.png")
print("ok", type(pc).__name__)
EOF
uv run --python 3.13 --with arviz --with arviz-stats --with arviz-plots --with matplotlib --with numpy --with xarray python sbc_ecdf_probe.py && ls -la sbc_ecdf.png
```

Expected: `ok PlotCollection` and a non-empty `sbc_ecdf.png` (open it with `Read` — a Δ-ECDF hugging zero inside a band). If `plot_ecdf_pit` raises about the group or dims, the two likely fixes are (a) passing `sample_dims=["draw"]`, or (b) supplying the values as a 1-D array under `"prior_sbc"` — apply the one the error names, and carry the *working* form into Step 3. Do not write a form into the reference that this probe did not run.

- [x] **Step 2: Update the Contents entry**

Replace `- Simulation-based calibration (SBC)` with `- Simulation-based calibration checking (SBC)`.

- [x] **Step 3: Replace the SBC section**
> Deviation: the plan's posterior-SBC sentence contradicted §14.3 and was rewritten (verify-before-citing governs the plan's text); "all 0s or all 1s" and a nine-word run tracking p. 253 reworded; four cited works added to `references/publications.md` and the band fact to `reporting.md` — both outside this task's Files list.

Delete from the line `## Simulation-based calibration (SBC)` through the line that starts `**When to run SBC**:` and insert:

````markdown
## Simulation-based calibration checking (SBC)

SBC checks that the whole pipeline — prior, data model, NumPyro code, and sampler — is *coherent*: draw parameters from the prior, simulate data, fit, and the posterior draws should be exchangeable with the parameter that generated the data, so its rank among the posterior draws is uniform (Gelman et al. 2026, §14.1; Modrák et al. 2025). A single fit to simulated data with one "known truth" cannot do this job: a posterior is calibrated only *on average over the prior*, so one truth landing in a tail — or a bimodal posterior straddling it — proves nothing either way (§14). SBC is the standard for validating a new model implementation; it needs many fits, so run it once per model specification when you have doubts.

**Mechanics** (Talts et al. 2018; Modrák et al. 2025; Gelman et al. 2026, §14.1): for each of `S` replications, draw `θ̃` from the prior, simulate `ỹ`, fit to get `L` (thinned, ~independent) posterior draws, and record the rank of `θ̃` among them. More generally, rank a *test quantity* `T(θ̃, ỹ)` among `T(θ_l, ỹ)` — functions of parameters *and* data catch bugs a single parameter's rank misses. If everything is correct the ranks are uniform on `{0, …, L}`. When draws can tie the truth exactly (discrete quantities), break ties at random.

A NumPyro sketch (roll your own; `simuk` from arviz-devs can also help):

```python
from numpyro.infer import Predictive, MCMC, NUTS
import jax, numpy as np

def sbc_rank(key, model, param, *model_args, L=100, idx=0):
    k_prior, k_fit = jax.random.split(key)
    # 1. draw one ground-truth parameter set + simulated data from the prior
    sim = Predictive(model, num_samples=1)(k_prior, *model_args)
    theta_true = np.asarray(sim[param][0])   # np.asarray needed to index a JAX array
    y_sim = sim["y_obs"][0]
    # 2. fit the model to the simulated data
    mcmc = MCMC(NUTS(model), num_warmup=500, num_samples=L, num_chains=1, progress_bar=False)
    mcmc.run(k_fit, *model_args, y=y_sim)
    draws = np.asarray(mcmc.get_samples()[param])
    # 3. rank of the truth within the posterior draws — pick one scalar component (idx)
    #    so the rank stays in [0, L]; a vector param would otherwise sum over all components
    return int((draws[..., idx] < theta_true[idx]).sum())

L = 100
ranks = np.array([sbc_rank(jax.random.PRNGKey(i), model, "beta", x, L=L) for i in range(200)])
```

**Read the ranks as a Δ-ECDF, not a histogram** (§14.2; Säilynoja, Bürkner & Vehtari 2022). Histogram shapes depend on the binning; the ECDF-difference plot with its simultaneous confidence band is the sharper instrument, and the same band yields a numerical pass/fail — the γ statistic, the tail probability of the most extreme ECDF deviation — for models with too many parameters to inspect by eye. In ArviZ, map ranks to PIT values and use `plot_ecdf_pit`, whose default group is `prior_sbc`:

```python
import arviz as az, arviz_plots as azp

pit = (ranks + 0.5) / (L + 1)                                   # ranks in [0, L] -> PIT in (0, 1)
sbc_dt = az.from_dict({"prior_sbc": {"beta": pit[None, :]}})     # (chain=1, draw=S)
azp.plot_ecdf_pit(sbc_dt, var_names=["beta"])                    # Δ-ECDF + simultaneous band + γ p-value
```

| Δ-ECDF shape (band = 95% simultaneous) | Rank histogram equivalent | Meaning |
|---|---|---|
| inside the band throughout | flat | pipeline coherent for this quantity |
| positive hump (ECDF runs ahead of uniform) | ranks pile at the low end | posterior *overestimates* — truth sits low among the draws |
| negative hump | ranks pile at the high end | posterior *underestimates* |
| + then − (crosses zero mid-way) | both ends piled | posterior *too narrow* — over-confident |
| − then + | middle piled | posterior *too wide* — under-confident |
| mostly flat, one edge shoots out of the band | a spike at one end | a subset of simulated datasets the model or sampler cannot handle — look at those reps |

Avoid "cup"/"cap"/"frown" for these shapes; the histogram and the Δ-ECDF invert each other's vocabulary (see the PIT section above).

**Fitting SBC into the workflow** (§14.3):

- **SBC over the whole prior can waste runs.** A prior that is weakly informative for *parameters* is often wild for *data* — a logistic regression with `Normal(0, 100)` coefficients simulates datasets that are all 0s or all 1s, and checking calibration there tells you nothing about the region you care about. Either tighten the prior (joint priors where independent ones are the problem — priors.md → Sparsity priors) or **rejection-sample the prior predictive**: discard a simulated dataset by a criterion that depends only on *data* (a maximum count above some cap, an outcome sd below some floor) and redraw. A data-only criterion leaves the posterior unchanged, so SBC stays valid.
- **Posterior SBC** (Säilynoja, Schmitt et al. 2026): once you have real data, run SBC with the *posterior* as the generating distribution. It checks the sampler where the posterior mass actually is and catches incoherent Bayesian updating — bugs in the sampler or the log-density — but cannot catch a wrong generative model, because the same code generates and fits.
- **Too slow for hundreds of replications?** A handful still catch gross bugs: any rank of exactly `0` or `L` is already a red flag; per-rep z-scores of the truth flag the same thing; and SBC on a fast sub-model first localises the problem. A few simulations beat none.
- **SBC as software testing.** The sketch above uses `Predictive(model)` to simulate, so it tests the *sampler* against the model as coded — it cannot detect a mis-coded likelihood, because the same code generates and fits. When the likelihood is non-trivial, write an independent NumPy simulator from the *equations* and feed its data to the NumPyro model; rank uniformity then also certifies that the two agree.

**When to run SBC**: developing a new model you'll reuse; complex hierarchical models where bugs are easy to introduce; custom likelihoods; any hand-written marginalization (state-space.md). Not necessary for routine analyses with standard model families.
````

- [x] **Step 4: Confirm the PIT-vocabulary rule is respected and nothing else references the old heading**

```bash
grep -n -i -E 'frown|cup-shaped|cap-shaped' skills/bayesian-workflow/references/model-criticism.md
grep -rn 'Simulation-based calibration (SBC)' skills/bayesian-workflow
```

Expected: the first grep hits only the pre-existing "Avoid the word frown" sentence in the PIT section (and the new "Avoid cup/cap/frown" line); the second grep prints nothing (README's tree line says `PPC, calibration, LOO-PIT, SBC`, which still holds).

- [x] **Step 5: Commit**

```bash
git add skills/bayesian-workflow/references/model-criticism.md
git commit -m "docs(bayesian-workflow): bring SBC guidance to Gelman et al. 2026 §14 practice

Replaces the histogram-only SBC reading with the Δ-ECDF plus simultaneous
band (arviz_plots.plot_ecdf_pit on a prior_sbc group - snippet executed on
arviz-plots 1.3.1 before inclusion), adds test quantities, the
prior-tension/rejection-sampling advice, posterior SBC, the few-reps-still-
useful rule, and the point that Predictive(model)-based SBC cannot catch a
mis-coded likelihood.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 10: Final verification sweep, README tree, CLAUDE.md test command

**Files:**
- Modify: `skills/bayesian-workflow/README.md` (the `scripts/` tree block near lines 435–438)
- Modify: `CLAUDE.md` (Commands section — add the new test command block after the `track-model-experiments` block). **`CLAUDE.md` has unrelated uncommitted changes at planning time** — see Step 3.

- [x] **Step 1: Add the test files to the README tree**

Replace

```
└── scripts/
    ├── diagnose_model.py             # Post-sampling diagnostics report (writes diagnostics.json)
    ├── calibration_check.py          # Calibration plots from InferenceData (writes calibration.json)
    └── check_diagnostics.py          # Interprets diagnostics + calibration into qualitative ratings + suggested next steps
```

with

```
└── scripts/
    ├── diagnose_model.py             # Post-sampling diagnostics report incl. MCSE precision block (writes diagnostics.json)
    ├── calibration_check.py          # Calibration plots from InferenceData (writes calibration.json)
    ├── check_diagnostics.py          # Interprets diagnostics + calibration into qualitative ratings + suggested next steps
    ├── test_diagnose_model.py        # pytest: precision block (run from scripts/)
    └── test_check_diagnostics.py     # pytest: divergence-fraction gate in suggested next steps
```

- [x] **Step 2: Add the test command to CLAUDE.md**

After the `track-model-experiments` block (the one ending `--with h5netcdf --with h5py python -m pytest -q`) and its trailing blank line, insert:

```bash
# bayesian-workflow script tests (MCSE precision block + divergence-gate next steps) — 9 tests
cd skills/bayesian-workflow/scripts && uv run --python 3.13 --with pytest --with arviz --with arviz-stats --with numpy --with xarray python -m pytest -q
```

- [x] **Step 3: Decide how CLAUDE.md gets committed**
> Deviation: CLAUDE.md carried six unrelated pre-existing hunks → the test-command block (with a note on the 4 expected arviz RuntimeWarnings) was left uncommitted for the user's own batch.

```bash
git diff --stat CLAUDE.md
```

If the diff touches *only* the block you just added → stage it in Step 6. If it also contains other hunks (the pre-existing edits from the Source-facts section) → **do not stage CLAUDE.md**; leave the edit in the working tree and list it at the completion gate ("CLAUDE.md test-command line left uncommitted because the file carried unrelated uncommitted changes — commit with that batch").

- [x] **Step 4: Run everything**

```bash
cd ~/Projects/agent-skills && uv run --python 3.13 --with pyyaml python build/check_frontmatter.py && uv run --python 3.13 python build/check_provenance.py && echo LINTS-OK
cd ~/Projects/agent-skills/skills/bayesian-workflow/scripts && uv run --python 3.13 --with pytest --with arviz --with arviz-stats --with numpy --with xarray python -m pytest -q
cd ~/Projects/agent-skills && grep -rn 'Gelman et al. 2020\|Gelman et al. (2020)' skills/bayesian-workflow
cd ~/Projects/agent-skills && grep -rn -c 'Gelman et al. 2026' skills/bayesian-workflow | grep -v ':0$'
```

Expected: `LINTS-OK`; `9 passed`; the 2020 grep hits only `references/publications.md`; the 2026 grep lists SKILL.md, diagnostics.md, priors.md, model-comparison.md, model-criticism.md, reporting.md, state-space.md, publications.md, README.md — each with a non-zero count.

- [x] **Step 5: Read-through for the license line**

Open each file the plan touched and confirm no sentence is a quotation from the book (no quotation marks around book text, no figure descriptions that reproduce a figure's data), and every `§` cited was opened in its task. This is Gate B; tick it only after doing it.

- [x] **Step 6: Commit**
> Deviation: the brief's verbatim subject claimed the withheld CLAUDE.md line; message amended with a *why* body (commit-body constraint governs).

```bash
git add skills/bayesian-workflow/README.md
# plus CLAUDE.md only if Step 3 said so
git commit -m "docs(bayesian-workflow): list the new script tests; add their run command

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

- [x] **Step 7: Hand off to the Plan Completion Protocol** (writing-plans § Plan Completion Protocol): resolve-before-defer gate → mark up this plan → `specs/deferred_items.md` ticking pass and append → `git mv` this plan to `specs/plans/completed/` (spec-less; nothing to retire in `specs/`). Candidates to surface at the gate: the uncommitted `CLAUDE.md` line (if Step 3 withheld it); any GREEN miss from Task 8; the open deferred item on a snippet-execution gate (Tasks 3, 7, 9 each executed their snippets by hand — the item stays open).
> Deviation: the gate (2026-09-03) approved editing the scope-fenced `references/visualize.md:211` and `scripts/calibration_check.py` docstring so the skill no longer says the PIT plots draw a band (commit de30860); passed diagnostics.md:61's §12.4 restatement; kept the 4 test warnings visible; chose a local merge. Two items deferred to specs/deferred_items.md.

---

## Self-review (run by the plan author before handoff — done 2026-09-02)

**Spec coverage.** R1 → Task 1. R2 → Task 2 (seven substitutions + Ch 26 line; Gate-B table with pages). R3 → Tasks 3 (script + tests) and 4 (prose + templates). R4 → Tasks 5 (RED), 6 (rung 1, fix-list step 1, ESS bullet, SKILL.md row), 7 (script + tests), 8 (GREEN). R5 → Task 6 Step 5 + SKILL.md pointer (Step 7c). R6 → Task 6 Steps 2 and 7a. R7 → Task 9 with the snippet proven in Step 1. R8 → Task 10.

**Placeholder scan.** Every code step shows the code; every command states its expected output; the two contingencies (Task 3 Step 4 E-BFMI fixture; Task 9 Step 1 two named fixes) are concrete alternatives, not "handle it". The bracketed fields in the Task 5/8 record templates are fill-ins from the ledger, by design.

**Type/name consistency.** `check_precision` keys (`params`, `sd`, `mcse_mean`, `mcse_sd`, `rel_mcse`, `stable_digits`, `max_rel_mcse`, `max_rel_mcse_param`, `min_stable_digits`) match between Task 3's function, its tests, Task 4's prose, and Task 7's smoke script. `DIVERGENCE_GATE_PCT` and `report["convergence"]["divergence_pct"]` match between Task 7's code and tests. Section names `Exploration runs vs. the final run` and `Failure signatures` are identical in Task 6 (headings + Contents), Task 4 (principle 6), Task 7 (suggestion text), and SKILL.md pointers. Citation key form `Gelman et al. 2026, §x.y` is used uniformly.
