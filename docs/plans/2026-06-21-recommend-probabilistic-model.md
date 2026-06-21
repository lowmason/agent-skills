# recommend-probabilistic-model Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `recommend-probabilistic-model` skill — a PML-grounded advisor that turns a modeling problem + its data into a recommendation memo with verified citations into Murphy's books and pyprobml.

**Architecture:** Hub `SKILL.md` + on-demand markdown references (a thin `decision-map.md` router over eight per-family depth files, plus cross-cutting refs), a thin Polars script `characterize.py`, and a reporting template. Citations are guaranteed by a two-gate build process: a mechanical verifier (Gate A) plus an adversarial semantic read (Gate B). PDFs are never shipped or searched at runtime; the common path reads only markdown.

**Tech Stack:** Markdown (skill content); Python 3.13 + Polars (`characterize.py`); Python stdlib (`build/verify_citations.py`); poppler (`pdftotext`/`pdftoppm`) for build-time book access; `gh` CLI for the pyprobml listing.

## Global Constraints

Copied verbatim from the spec ([docs/specs/2026-06-21-recommend-probabilistic-model-design.md](../specs/2026-06-21-recommend-probabilistic-model-design.md)). Every task's requirements implicitly include these.

- **C1 — Verified-source rule.** Every §ref and notebook link is verified against the actual source before it ships — never written from recall. Two gates: **Gate A** (mechanical: section number + title exist in the extracted index; notebook path exists in the real listing) and **Gate B** (semantic: an adversarial read of the cited section text confirms it actually supports the claim).
- **C2 — Book 2 access.** `prob_ml_book.pdf` (144 MB) exceeds the Read 100 MB cap. Use `pdftotext -f N -l M prob_ml_book.pdf out.txt` and `pdftoppm -png -f N -l M -r 120 prob_ml_book.pdf out`. Naive `pdfseparate`+`pdfunite` splitting is **ruled out** (produced a 180 MB file from 20 pages). Book 1 (88 MB) and the supplement (12 MB) read fine via Read or `pdftotext`.
- **C3 — Which-book routing.** Dual-coverage topics: Book 1 = standard (default pointer); Book 2 = advanced/extended. Every dual entry names both.
- **C4 — Handoff interface.** A Bayesian recommendation must carry: likelihood family, candidate priors (incl. external-data-derived), structure (pooling/hierarchy/temporal), and the regularization & model-selection plan. Specified in `reporting.md`.
- **C5 — pyprobml index** is built from a real repo listing (`gh api`), not constructed paths. Notebooks are flat under `notebooks/book1/` and `notebooks/book2/` (master branch).
- **C6 — Licensing.** Books are **CC-BY-NC-ND** → summarize in original wording + cite; reproduce no prose, bundle no PDFs. `pyprobml` + `pml-book` repo materials are **MIT** → link. Record in `NOTICE`.
- **Performance/size.** Ship only markdown + a thin script (target: tens of KB). Common runtime path touches no PDFs. Build-scratch is gitignored.
- **Local PDFs** (not bundled): `~/Documents/Bayesian/Probabilistic Machine Learning/` — `prob_ml_1-book.pdf` (Book 1), `prob_ml_book.pdf` (Book 2), `prob_ml_1-solutions.pdf`, `prob_ml_2-supplementary.pdf`.

## Execution model

This plan serves both execution paths; be explicit about which runs what (do **not** let the stock "pick an execution mode" ending silently override this):

- **Inline / sequential (prerequisites):** Tasks 1–3 (extraction, the verifier harness, `characterize.py`) and the synthesis Tasks 7, 11–13. They have ordering dependencies.
- **Workflow fan-out (parallel):** Task 4 is **one parametrized task run once per family (×8)** — this is the fan-out unit. Tasks 5, 6, 8, 9, 10 are independent content files that can also run in parallel after Tasks 1–2.

## File structure

```
recommend-probabilistic-model/          # the shipped skill (skill dir = only shipped files)
  SKILL.md                              # Task 11
  README.md                             # Task 12
  references/
    decision-map.md                     # Task 7  (thin router)
    families/                           # Task 4  (×8, the fan-out unit)
      regression-glm.md  hierarchical.md  timeseries-statespace.md
      gaussian-processes.md  factor-models.md  classification.md
      mixtures-clustering.md  graphical-models.md
    model-selection-regularization.md   # Task 5  (cross-cutting)
    pyprobml-index.md                   # Task 6
    drill-down.md                       # Task 8
    external-data-and-priors.md         # Task 9
    reporting.md                        # Task 10
  scripts/
    characterize.py                     # Task 3
    test_characterize.py                # Task 3
build/                                   # repo-level build tooling (NOT shipped)
  extract_structure.py                  # Task 1
  verify_citations.py                   # Task 2
  test_verify_citations.py              # Task 2
  .scratch/                             # gitignored: book{1,2}_sections.tsv, pyprobml_files.txt
README.md                               # Task 12 (root table row)
NOTICE                                  # Task 12 (attribution)
.gitignore                              # Task 1 (point at build/.scratch/)
```

---

### Task 1: Build-scratch extraction

Extract ground truth (book section indices + pyprobml listing) into gitignored scratch. Everything downstream verifies against these.

**Files:**
- Create: `build/extract_structure.py`
- Modify: `.gitignore` (replace the earlier `recommend-probabilistic-model/.build-scratch/` line)
- Output (gitignored): `build/.scratch/book1_sections.tsv`, `build/.scratch/book2_sections.tsv`, `build/.scratch/pyprobml_files.txt`

**Interfaces:**
- Produces: three scratch files. TSV format per line: `<section-number>\t<title>` (e.g. `10.2\tMaximum likelihood estimation`). `pyprobml_files.txt`: one notebook path per line (`notebooks/book1/foo.ipynb`).

- [ ] **Step 1: Fix the gitignore path**

Replace the build-scratch line so it points at the chosen location:

```
# Build-time scratch for recommend-probabilistic-model: extracted CC-BY-NC-ND
# book text used only to build/verify citations — never commit.
build/.scratch/
```

- [ ] **Step 2: Write `build/extract_structure.py`**

```python
"""Extract ground truth for citation verification into build/.scratch/ (gitignored).
Book section indices come from the TOC pages via pdftotext; the pyprobml listing from gh.
CC-BY-NC-ND note: these are factual section numbers/titles used only to VERIFY our own
citations at build time — not shipped, not redistributed prose."""
import json, re, subprocess, sys
from pathlib import Path

PDF_DIR = Path.home() / "Documents/Bayesian/Probabilistic Machine Learning"
BOOK1 = PDF_DIR / "prob_ml_1-book.pdf"
BOOK2 = PDF_DIR / "prob_ml_book.pdf"
SCRATCH = Path(__file__).parent / ".scratch"

# TOC page ranges (front matter). Verify by eye in Step 3; widen if truncated.
TOC = {"1": (BOOK1, 9, 30), "2": (BOOK2, 5, 34)}
SEC_RE = re.compile(r"^\s*(\d+(?:\.\d+)*)\s+(.+?)\s*\.{2,}?\s*\d*\s*$")

def extract_book(book, pdf, f, l):
    txt = subprocess.run(["pdftotext", "-f", str(f), "-l", str(l), str(pdf), "-"],
                         capture_output=True, text=True, check=True).stdout
    rows = {}
    for line in txt.splitlines():
        m = SEC_RE.match(line)
        if m:
            rows[m.group(1)] = m.group(2).strip()
    out = SCRATCH / f"book{book}_sections.tsv"
    out.write_text("\n".join(f"{n}\t{t}" for n, t in rows.items()))
    return len(rows)

def extract_pyprobml():
    js = subprocess.run(["gh", "api", "repos/probml/pyprobml/git/trees/master?recursive=1"],
                        capture_output=True, text=True, check=True).stdout
    paths = [t["path"] for t in json.loads(js)["tree"]
             if t["path"].endswith(".ipynb") and t["path"].startswith("notebooks/book")]
    (SCRATCH / "pyprobml_files.txt").write_text("\n".join(sorted(paths)))
    return len(paths)

if __name__ == "__main__":
    SCRATCH.mkdir(exist_ok=True)
    for book, (pdf, f, l) in TOC.items():
        print(f"book{book}: {extract_book(book, pdf, f, l)} sections")
    print(f"pyprobml: {extract_pyprobml()} notebooks")
```

- [ ] **Step 3: Run extraction and spot-check the index (the lenient-by-accident guard)**

Run: `python build/extract_structure.py`
Expected: `book1: <N≥100> sections`, `book2: <M≥150> sections`, `pyprobml: <≥450> notebooks`.

Then **manually verify the parsed index against the PDFs** (pdftotext mangles multi-column TOCs):

```bash
grep -E "^(10|11|12)\." build/.scratch/book1_sections.tsv   # expect logistic/linear-reg/GLM sections
grep -E "^(4|8)\." build/.scratch/book2_sections.tsv        # expect graphical-models / gaussian-filtering sections
grep "notebooks/book1/" build/.scratch/pyprobml_files.txt | head
```
If a known chapter is missing or titles are garbled, widen the `TOC` page ranges or fix `SEC_RE`, and re-run. **Gate A is only as good as this index — do not proceed until a hand-checked sample of ≥10 sections per book matches the PDF.**

- [ ] **Step 4: Commit**

```bash
git add build/extract_structure.py .gitignore
git commit -m "build: extract book section indices + pyprobml listing for citation verification"
```

---

### Task 2: Citation-verification harness (Gate A)

A real Python tool with a true-negative test. This is the mechanical gate every content task runs.

**Files:**
- Create: `build/verify_citations.py`, `build/test_verify_citations.py`

**Interfaces:**
- Consumes: `build/.scratch/book{1,2}_sections.tsv`, `build/.scratch/pyprobml_files.txt` (Task 1).
- Produces: CLI `python build/verify_citations.py <file.md>...` → exit 0 if all citations resolve; exit 1 + a list of unresolved citations otherwise. Importable `verify_text(text: str) -> list[str]` returning the list of failures (empty = pass).

- [ ] **Step 1: Write the failing tests (incl. the true-negative)**

```python
# build/test_verify_citations.py
from build.verify_citations import verify_text

def test_true_negative_flags_bad_refs():
    bad = "Use PML1 §99.9 and notebooks/book1/does_not_exist_xyz.ipynb."
    failures = verify_text(bad)
    assert any("99.9" in f for f in failures)
    assert any("does_not_exist_xyz" in f for f in failures)

def test_true_positive_passes_real_refs(real_ref):
    # real_ref fixture = a (section, notebook) pair known-present in scratch
    assert verify_text(f"See PML1 §{real_ref.sec} and {real_ref.nb}.") == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest build/test_verify_citations.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'build.verify_citations'`.

- [ ] **Step 3: Write `build/verify_citations.py`**

```python
"""Gate A (mechanical) citation verifier. Parses PML §refs and pyprobml notebook paths
from markdown and checks each against build/.scratch/ ground truth. Exit 0 if all resolve.
Does NOT check semantic correctness — that is Gate B (an adversarial read), a separate step."""
import re, sys
from pathlib import Path

SCRATCH = Path(__file__).parent / ".scratch"
CITE_RE = re.compile(r"\bPML([12])\s*§\s*(\d+(?:\.\d+)*)")
NB_RE = re.compile(r"notebooks/book[12]/[^\s)`\"']+\.ipynb")

def _sections(book):
    f = SCRATCH / f"book{book}_sections.tsv"
    return {ln.split("\t")[0] for ln in f.read_text().splitlines() if ln.strip()}

def _notebooks():
    return set((SCRATCH / "pyprobml_files.txt").read_text().split())

def _section_ok(keys, ref):
    parts = ref.split(".")
    # pass if any prefix of the ref is, or is the parent of, an indexed section
    for k in range(len(parts), 0, -1):
        pref = ".".join(parts[:k])
        if pref in keys or any(s.startswith(pref + ".") for s in keys):
            return True
    return False

def verify_text(text: str) -> list[str]:
    secs = {"1": _sections("1"), "2": _sections("2")}
    nbs = _notebooks()
    failures = []
    for book, ref in CITE_RE.findall(text):
        if not _section_ok(secs[book], ref):
            failures.append(f"unresolved section: PML{book} §{ref}")
    for nb in NB_RE.findall(text):
        if nb not in nbs:
            failures.append(f"unresolved notebook: {nb}")
    return failures

def main(argv):
    all_fail = []
    for p in argv:
        fails = verify_text(Path(p).read_text())
        all_fail += [f"{p}: {f}" for f in fails]
    for f in all_fail:
        print(f)
    return 1 if all_fail else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 4: Add the `real_ref` fixture**

```python
# build/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def real_ref():
    scratch = Path(__file__).parent / ".scratch"
    sec = next(ln.split("\t")[0] for ln in (scratch/"book1_sections.tsv").read_text().splitlines() if ln.strip())
    nb = (scratch/"pyprobml_files.txt").read_text().split()[0]
    return type("R", (), {"sec": sec, "nb": nb})
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest build/test_verify_citations.py -v`
Expected: PASS (2 tests).

- [ ] **Step 6: Commit**

```bash
git add build/verify_citations.py build/test_verify_citations.py build/conftest.py
git commit -m "build: add Gate A citation verifier with true-negative test"
```

---

### Task 3: `characterize.py` — modeling-signal extractor

Thin Polars script for the ~5 modeling signals `explore-data`'s `profile.py` does NOT emit (drop-check resolved: profile.py already gives null %, cardinality, quartiles, key-uniqueness, panel balance — so build only the gap).

**Files:**
- Create: `recommend-probabilistic-model/scripts/characterize.py`, `recommend-probabilistic-model/scripts/test_characterize.py`

**Interfaces:**
- Produces: CLI `python characterize.py DATA --target COL [--predictors A,B] [--time COL] [--json out.json]`. Functions: `overdispersion(s)->float|None`, `zero_fraction(s)->float`, `n_over_p(n,p)->float|None`, `class_balance(s)->dict|None`, `stationarity_hint(s)->dict|None`. JSON consumed by procedure Step 2.

- [ ] **Step 1: Write the failing tests**

```python
# scripts/test_characterize.py
import polars as pl
from scripts.characterize import overdispersion, zero_fraction, class_balance, stationarity_hint

def test_overdispersion_flags_var_gg_mean():
    s = pl.Series([0,0,1,0,5,0,12,0,0,30,0,7], dtype=pl.Int64)
    assert overdispersion(s) > 1.5            # variance ≫ mean
    assert overdispersion(pl.Series([1.0,2.0,3.0])) is None   # not count-like

def test_zero_fraction():
    assert abs(zero_fraction(pl.Series([0,0,1,2,0])) - 0.6) < 1e-9

def test_class_balance_imbalance_ratio():
    cb = class_balance(pl.Series(["a"]*90 + ["b"]*10))
    assert cb["n_classes"] == 2 and cb["imbalance_ratio"] == 9.0

def test_stationarity_hint_detects_trend():
    s = pl.Series([float(i) for i in range(40)])   # strong upward trend
    assert stationarity_hint(s)["split_half_mean_shift_sd"] > 1.0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest scripts/test_characterize.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.characterize'`.

- [ ] **Step 3: Write `scripts/characterize.py`**

```python
"""Modeling-relevant signals that explore-data's profile.py does NOT compute:
overdispersion, zero-fraction, n/p, class balance, stationarity hint. Polars + stdlib only.
Output JSON feeds the recommend-probabilistic-model procedure (Step 2: Characterize the data)."""
import argparse, json, sys
import polars as pl

def overdispersion(s: pl.Series):
    if not s.dtype.is_integer(): return None
    s = s.drop_nulls()
    if s.len() == 0 or (s < 0).any(): return None
    m = s.mean()
    return None if not m else round(float(s.var() / m), 3)

def zero_fraction(s: pl.Series):
    s = s.drop_nulls()
    return 0.0 if s.len() == 0 else round(float((s == 0).sum() / s.len()), 4)

def n_over_p(n_rows: int, n_predictors: int):
    return None if not n_predictors else round(n_rows / n_predictors, 2)

def class_balance(s: pl.Series):
    s = s.drop_nulls()
    if s.len() == 0: return None
    vc = s.value_counts(sort=True)
    fr = [c / s.len() for c in vc[vc.columns[-1]].to_list()]
    return {"n_classes": len(fr), "min_class_frac": round(min(fr), 4),
            "max_class_frac": round(max(fr), 4),
            "imbalance_ratio": round(max(fr) / min(fr), 2) if min(fr) else None}

def stationarity_hint(s: pl.Series):
    s = s.drop_nulls().cast(pl.Float64)
    if s.len() < 8: return None
    h, sd = s.len() // 2, s.std()
    shift = round(float((s[h:].mean() - s[:h].mean()) / sd), 3) if sd else 0.0
    x0, x1 = s[:-1], s[1:]
    ac1 = (round(float(((x0 - x0.mean()) * (x1 - x1.mean())).sum() / ((x0 - x0.mean())**2).sum()), 3)
           if x0.std() else None)
    return {"split_half_mean_shift_sd": shift, "lag1_autocorr": ac1}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data"); ap.add_argument("--target"); ap.add_argument("--predictors")
    ap.add_argument("--time"); ap.add_argument("--json")
    a = ap.parse_args()
    df = pl.read_csv(a.data) if a.data.endswith((".csv", ".tsv")) else pl.read_parquet(a.data)
    preds = a.predictors.split(",") if a.predictors else [c for c in df.columns if c != a.target]
    out = {"n_rows": df.height, "n_predictors": len(preds), "n_over_p": n_over_p(df.height, len(preds))}
    if a.target and a.target in df.columns:
        t = df[a.target]
        out["target"] = {"name": a.target, "overdispersion": overdispersion(t),
                         "zero_fraction": zero_fraction(t), "class_balance": class_balance(t)}
    if a.time and a.time in df.columns:
        out["stationarity"] = {c: stationarity_hint(df[c]) for c in preds if df[c].dtype.is_numeric()}
    js = json.dumps(out, indent=2)
    (open(a.json, "w").write(js) if a.json else print(js))

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest scripts/test_characterize.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add recommend-probabilistic-model/scripts/characterize.py recommend-probabilistic-model/scripts/test_characterize.py
git commit -m "feat: add thin characterize.py for modeling-relevant data signals"
```

---

### Task 4: Family depth files (parametrized — run once per family, ×8)

**This is the Workflow fan-out unit.** Run this same task template once per row of the family table. Each produces one `references/families/<slug>.md` and passes both gates.

**Files (per run):**
- Create: `recommend-probabilistic-model/references/families/<slug>.md`

**Family table** (chapter-level anchors — refine to exact §refs during Gate A/B; do NOT ship a §ref until both gates pass):

| slug | Book 1 chapters | Book 2 area | pyprobml dir | selecting signals | handoff |
|------|-----------------|-------------|--------------|-------------------|---------|
| `regression-glm` | 10 Logistic Reg, 11 Linear Reg, 12 GLMs | GLM/robust, Bayesian lin-reg | book1, book2 | `var≫mean`→NB; `zeros high`→ZI/hurdle; heavy tails→StudentT | bayesian-workflow |
| `hierarchical` | (intro in 4 Statistics) | hierarchical Bayes | book1, book2 | group/panel columns; repeated measures | bayesian-workflow |
| `timeseries-statespace` | 15 NN for Sequences (partial) | 8 Gaussian filtering & smoothing; SSMs | book1, book2 | time index; autocorr; nonstationarity | bayesian-workflow / statsmodels |
| `gaussian-processes` | 17 Kernel methods | GP chapter | book1, book2 | smooth nonlinear; small-n; need uncertainty | bayesian-workflow / GPyTorch |
| `factor-models` | 20 Dimensionality Reduction | factor analysis; dynamic factor / SSM | book1, book2 | many correlated indicators → common signal | bayesian-workflow / sklearn |
| `classification` | 9 LDA, 10 Logistic, 18 Trees/Boosting | — | book1, book2 | categorical target; class balance | sklearn / bayesian-workflow |
| `mixtures-clustering` | 21 Clustering | mixture/latent-var; Dirichlet process | book1, book2 | regimes/segments; multimodality | sklearn / bayesian-workflow |
| `graphical-models` | 3 Probability: Multivariate (MVN/precision) | 4 Graphical models; structure learning; GNNs | book1, book2 | many vars, unknown deps; network data | bayesian-workflow / specialized |

- [ ] **Step 1: Locate the candidate sections** (build-time read; CC-BY-NC-ND use, not redistribution)

```bash
# Book 1: Read tool works (88 MB) OR pdftotext for a page range.
# Book 2: pdftotext only (C2). Find the family's sections in the scratch index:
grep -iE "<keyword>" build/.scratch/book1_sections.tsv build/.scratch/book2_sections.tsv
# List candidate notebooks:
grep -iE "<keyword>" build/.scratch/pyprobml_files.txt
```

- [ ] **Step 2: Draft `families/<slug>.md`** using this skeleton (summaries in original wording — C6):

```markdown
# <Family name>

**When this family fits:** <1–2 lines, original wording — the data signal(s) that point here.>

## Methods & defaults

| Method | Use when | Default rec | PML §ref (Book 1 / Book 2) | pyprobml |
|--------|----------|-------------|----------------------------|----------|
| <e.g. NegativeBinomial GLM> | <var≫mean count data> | <NB2(mean, conc)> | PML1 §<x.y> / PML2 §<x.y> | notebooks/book1/<nb>.ipynb |

## Selection & regularization (Step 6, family-specific)
<This family's complexity knobs + the criterion to use — e.g. # factors via CV/ELPD; sparsity prior;
partial pooling IS the regularizer; structure penalty. Specializes references/model-selection-regularization.md.>

## Gotchas
<battle-tested pitfalls, original wording.>

## Handoff
<bayesian-workflow | sklearn/other | drill-down — and what the memo must carry (C4).>
```

- [ ] **Step 3: Gate A — mechanical verification**

Run: `python build/verify_citations.py recommend-probabilistic-model/references/families/<slug>.md`
Expected: exit 0, no output. If any citation is unresolved, fix the §ref/path and re-run.

- [ ] **Step 4: Gate B — adversarial semantic read (per citation)**

For **each** §ref in the file, open the cited section and confirm it actually supports the claim:

```bash
# Book 1 (Read tool ok) or:
pdftotext -f <p> -l <p+2> "$HOME/Documents/Bayesian/Probabilistic Machine Learning/prob_ml_1-book.pdf" -
# Book 2 (C2):
pdftotext -f <p> -l <p+2> "$HOME/Documents/Bayesian/Probabilistic Machine Learning/prob_ml_book.pdf" -
```
Pass criterion: the section's actual content backs the summary/recommendation it is attached to. **If the section is real but about something adjacent, the citation FAILS** — replace it. Record a one-line "verified: §x.y supports <claim>" note per citation in the commit body.

- [ ] **Step 5: Commit**

```bash
git add recommend-probabilistic-model/references/families/<slug>.md
git commit -m "feat: add <slug> family reference (Gate A+B verified)"
```

---

### Task 5: Cross-cutting `model-selection-regularization.md`

**Files:** Create `recommend-probabilistic-model/references/model-selection-regularization.md`

- [ ] **Step 1: Draft** — general CV / IC / LOO-ELPD theory (original wording + §refs) and a **per-family knobs table** (family → selection criterion → regularizer), e.g. `factor-models → # factors → CV/ELPD`; `regression-glm → predictors → lasso/horseshoe`; `hierarchical → partial pooling (intrinsic)`. State the boundary: pre-fit specification here; post-fit LOO/ELPD comparison is `bayesian-workflow`.
- [ ] **Step 2: Gate A** — `python build/verify_citations.py recommend-probabilistic-model/references/model-selection-regularization.md` → exit 0.
- [ ] **Step 3: Gate B** — adversarial read of each §ref (as Task 4 Step 4).
- [ ] **Step 4: Commit** — `git commit -m "feat: add cross-cutting model-selection & regularization reference (Gate A+B)"`

---

### Task 6: `pyprobml-index.md`

**Files:** Create `recommend-probabilistic-model/references/pyprobml-index.md`

**Interfaces:** Consumes `build/.scratch/pyprobml_files.txt`. Produces a map: family/topic → verified notebook path(s).

- [ ] **Step 1: Build the index** from the real listing only (C5):

```bash
grep -iE "regression|glm|poisson|logistic" build/.scratch/pyprobml_files.txt
grep -iE "gp|gauss|kernel|factor|pca|mixture|gmm|hmm|kalman|graph" build/.scratch/pyprobml_files.txt
```
Map each deep family to its 1–3 most relevant notebooks (book1 = standard, book2 = advanced, per C3).

- [ ] **Step 2: Gate A** — `python build/verify_citations.py recommend-probabilistic-model/references/pyprobml-index.md` → exit 0 (every path exists in the listing).
- [ ] **Step 3: Commit** — `git commit -m "feat: add pyprobml notebook index (verified against real listing)"`

---

### Task 7: `decision-map.md` (thin router)

**Files:** Create `recommend-probabilistic-model/references/decision-map.md`

**Interfaces:** Consumes the eight `families/*.md` (Task 4) and `pyprobml-index.md` (Task 6). Produces the runtime router table.

- [ ] **Step 1: Write the router table** — one row per (task × selecting signal), columns: signal → target family → pointer to `families/<slug>.md` → primary §ref → primary notebook. Keep it scannable (no deep detail — that lives in the family files).
- [ ] **Step 2: Verify every family pointer resolves**

```bash
for f in $(grep -oE 'families/[a-z-]+\.md' recommend-probabilistic-model/references/decision-map.md | sort -u); do
  test -f "recommend-probabilistic-model/references/$f" && echo "ok $f" || echo "MISSING $f"
done
```
Expected: all `ok`, none `MISSING`.
- [ ] **Step 3: Gate A** — `python build/verify_citations.py recommend-probabilistic-model/references/decision-map.md` → exit 0.
- [ ] **Step 4: Commit** — `git commit -m "feat: add decision-map router over the eight family files"`

---

### Task 8: `drill-down.md`

**Files:** Create `recommend-probabilistic-model/references/drill-down.md`

- [ ] **Step 1: Write the long-tail procedure** — Book 1 via Read; Book 2 via the exact `pdftotext`/`pdftoppm` commands (C2, incl. the ruled-out `pdfunite`); grep pyprobml; how to cite + record a verification date. Include a worked example for one route-only family (e.g. reinforcement learning).
- [ ] **Step 2: Smoke-test the documented commands** — run each command block once; confirm it returns text/images, not an error.
- [ ] **Step 3: Commit** — `git commit -m "feat: add drill-down procedure for the long tail"`

---

### Task 9: `external-data-and-priors.md`

**Files:** Create `recommend-probabilistic-model/references/external-data-and-priors.md`

- [ ] **Step 1: Draft** — how official statistics / benchmarks / related series / domain constraints become informative priors, partial-pooling targets, covariates, or hard constraints. Cross-link `bls-data-context` (sources) and `bayesian-workflow` (prior elicitation / PreliZ). Worked example: an official aggregate → an informative prior on a rate.
- [ ] **Step 2: Gate A** (if any §refs) → exit 0; **Gate B** for each §ref.
- [ ] **Step 3: Commit** — `git commit -m "feat: add external-data & priors bridge reference"`

---

### Task 10: `reporting.md` (recommendation.md template = C4 interface)

**Files:** Create `recommend-probabilistic-model/references/reporting.md`

- [ ] **Step 1: Write the canonical template** with the 8 sections from the spec: (1) Problem framing, (2) Data characterization, (3) Candidate methods, (4) Recommendation, (5) Regularization & model selection, (6) Specification for handoff (likelihood family / priors incl. external-data-derived / structure / regularization plan — the C4 payload), (7) References, (8) Next steps / handoff.
- [ ] **Step 2: Verify structure** — confirm all 8 sections present and §6 enumerates every C4 field.

```bash
grep -cE "^#{2,3} " recommend-probabilistic-model/references/reporting.md   # expect ≥ 8
```
- [ ] **Step 3: Commit** — `git commit -m "feat: add recommendation.md reporting template (C4 handoff interface)"`

---

### Task 11: `SKILL.md` (hub)

**Files:** Create `recommend-probabilistic-model/SKILL.md`

**Interfaces:** Consumes all `references/*` and `scripts/characterize.py`. Produces the entry point.

- [ ] **Step 1: Write the frontmatter** — `name`, a triggering-optimized `description` (lead with "Use when…"; enumerate concrete contexts: "which model/method should I use", "what approach for this data", "is this Poisson or negative binomial", "how to handle overdispersion/zero-inflation/panel data", "model selection", grounded in Murphy PML), `license: MIT` (the skill's own code/prose), and `metadata` (author: Lowell Mason; cites Murphy PML under CC-BY-NC-ND).
- [ ] **Step 2: Write the body** — boundaries ("this vs. siblings": explore-data discovers → this decides → bayesian-workflow executes; bls-data-context supplies; validate-data gates); the **8-step procedure**; the which-book rule (C3); the handoff interface (→ reporting.md); a short install/stack note (poppler optional, only for drill-down).
- [ ] **Step 3: Verify all internal links resolve**

```bash
for f in $(grep -oE '\(references/[a-zA-Z0-9/_-]+\.md\)|\(scripts/[a-z_]+\.py\)' recommend-probabilistic-model/SKILL.md | tr -d '()'); do
  test -f "recommend-probabilistic-model/$f" && echo "ok $f" || echo "MISSING $f"
done
```
Expected: all `ok`.
- [ ] **Step 4: Commit** — `git commit -m "feat: add SKILL.md hub with 8-step procedure and sibling boundaries"`

---

### Task 12: README, root table, NOTICE (attribution + discoverability)

**Files:**
- Create: `recommend-probabilistic-model/README.md`
- Modify: `README.md` (root — add a row to the "Mine" table), `NOTICE`

- [ ] **Step 1: Skill `README.md`** — one-paragraph summary + the licensing note (books CC-BY-NC-ND, cited/summarized; pyprobml + pml-book MIT, linked).
- [ ] **Step 2: Root `README.md`** — add a row to the "Mine" table linking `recommend-probabilistic-model/` with a one-line description.
- [ ] **Step 3: `NOTICE`** — add an entry: this skill cites Kevin Murphy's *Probabilistic Machine Learning* (Book 1 © 2022 MIT; Book 2 © 2023 K. P. Murphy) under **CC-BY-NC-ND** (summarized/cited, not redistributed) and links `pyprobml` / `pml-book` materials under **MIT**.
- [ ] **Step 4: Verify links** — `grep recommend-probabilistic-model README.md` shows the new row; confirm the skill README link resolves.
- [ ] **Step 5: Commit** — `git commit -m "docs: add README + NOTICE attribution for recommend-probabilistic-model"`

---

### Task 13: End-to-end smoke test

Prove the assembled skill produces a correct recommendation on a known case.

**Files:** Create (temporary, not committed) `/tmp/rpm_smoke.csv`

- [ ] **Step 1: Build a synthetic case** — overdispersed counts with a group column:

```python
import polars as pl, numpy as np
rng = np.random.default_rng(sum(map(ord, "rpm-smoke")))
g = rng.integers(0, 5, 400)
y = rng.negative_binomial(2, 0.3, 400) * (1 + (g == 0))  # overdispersed, group-varying
pl.DataFrame({"y": y, "group": g, "x": rng.normal(size=400)}).write_csv("/tmp/rpm_smoke.csv")
```

- [ ] **Step 2: Run `characterize.py`**

Run: `python recommend-probabilistic-model/scripts/characterize.py /tmp/rpm_smoke.csv --target y`
Expected JSON: `target.overdispersion > 1.5` (flags NB over Poisson); `n_over_p` present.

- [ ] **Step 3: Walk the procedure by hand** — using `decision-map.md`, confirm the signal `var≫mean` routes to `families/regression-glm.md` → NegativeBinomial, and the `group` column surfaces `families/hierarchical.md` (partial pooling). Produce a `recommendation.md` from `reporting.md` and confirm §6 carries the C4 payload (likelihood = NB2; structure = varying intercept by group).
- [ ] **Step 4: Confirm no PDF was touched** — the routing used only markdown (performance invariant).
- [ ] **Step 5: Commit** — `git commit -m "test: end-to-end smoke (overdispersed grouped counts → NB + hierarchical)"`

---

## Self-review

- **Spec coverage:** scope/advisor (Tasks 7,11), hybrid map+drill-down (7,8), tiered 8 families (4) + route-only (8), adaptive data-aware input (3) + external data (9), 8-step procedure incl. Step 6 (11,5), thin router + family files (4,7), perf/no-PDF-runtime (13 Step 4), C1 two gates (2,4), C2 Book 2 access (1,4,8), C3 which-book (4), C4 handoff (10), C5 pyprobml listing (1,6), C6 licensing (12). Covered.
- **Placeholders:** family table uses chapter-level anchors with an explicit "refine + verify via Gate A/B" instruction — concrete pointers, not TBDs.
- **Type consistency:** `verify_text`/`verify_citations.py` signatures match between Tasks 2 and 4–9; `characterize.py` function names match between Task 3 code and tests and Task 13.
