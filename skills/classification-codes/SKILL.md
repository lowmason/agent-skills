---
name: classification-codes
description: >
  Use when a task touches NAICS or SOC codes in any way — mapping a code to its title or a title
  to its code, listing what a sector / subsector / major group contains, walking the hierarchy,
  converting between vintages (NAICS 2017↔2022, SOC 2010↔2018), joining datasets coded in
  different vintages, or interpreting a series break that coincides with a classification
  revision. Consult BEFORE answering any code↔title question, before joining on an industry or
  occupation code, and before treating a code as meaning the same thing in two vintages. Trigger
  on: NAICS, SOC, O*NET, sector, subsector, industry group, six-digit code, occupation code,
  major group, detailed occupation, concordance, crosswalk, 2017-to-2022, 2010-to-2018, Census
  occupation code, unclassified / 999999, "what industry is X", "what does code X mean", "is
  code X still valid". Codes and titles are answered from data/, never from model memory —
  memory produces plausible codes with wrong titles and wrong vintages.
license: MIT
model: haiku
metadata:
  author: Lowell Mason
  version: "0.1"
---

# Classification Codes (NAICS & SOC)

## What this is

The authoritative local copy of the U.S. industry (NAICS) and occupation (SOC) classification
systems, plus the official vintage concordances, as tidy greppable CSVs under `data/`. This
SKILL.md carries the structural semantics and the query recipes; the codes themselves live only
in the data files.

**Prime directive: never answer a code↔title, membership, or vintage question from memory.**
Code→referent mappings are arbitrary, dense, and vintage-dependent — exactly what a model
confabulates most fluently. Grep for point lookups; load with Polars for hierarchy, membership,
or concordance work. If `data/` is missing, rebuild it first (see *Rebuilding*).

## Files

| file | rows ≈ | columns |
|---|---|---|
| `data/naics_2022.csv` | 2,100 (1,012 six-digit) | `code, level, title, parent_code, sector_code, trilateral` |
| `data/naics_2017.csv` | 2,200 (1,057 six-digit) | same |
| `data/naics_2017_to_2022.csv` | ~1,100 | `naics_2017, title_2017, naics_2022, title_2022, link_type` |
| `data/soc_2018.csv` | 1,447 (867 detailed) | `code, level, title, parent_code` |
| `data/soc_2010.csv` | ~1,420 (840 detailed) | same |
| `data/soc_2010_to_2018.csv` | ~900 | `soc_2010, title_2010, soc_2018, title_2018, link_type` |

`level` is 2–6 for NAICS and `major | minor | broad | detailed` for SOC. `link_type` is derived
from code multiplicities: `1:1` (unchanged or clean recode), `1:m` (split), `m:1` (merge),
`m:m` (reshuffle). `MANIFEST.md` records the source URL, sha256, and retrieval time behind every
file; `sources/` holds the exact source bytes.

## How to query

**Codes are strings, always.** NAICS prefix logic dies on integers, and the adjacent Census
occupation codes carry leading zeros. In Polars, force them:
`schema_overrides={'code': pl.Utf8, 'parent_code': pl.Utf8, 'sector_code': pl.Utf8}` (and the
`naics_*` columns of the concordance).

Point lookups — grep, don't load:

```bash
grep -E '^561320,' data/naics_2022.csv          # code -> title
grep -iE 'temporary help' data/naics_2022.csv    # title -> code
grep -E '^15-1252,' data/soc_2018.csv            # SOC lookup
grep -E '^454110,' data/naics_2017_to_2022.csv   # where did a 2017 code go
```

Membership and hierarchy — load, then use the materialized columns, never string surgery:

```python
naics = pl.read_csv(
  'data/naics_2022.csv',
  schema_overrides={'code': pl.Utf8, 'parent_code': pl.Utf8, 'sector_code': pl.Utf8},
)
manufacturing = naics.filter(pl.col('sector_code').eq('31-33').and_(pl.col('level').eq(6)))
children = naics.filter(pl.col('parent_code').eq('5613'))
```

Vintage bridging — join on the concordance and route by `link_type`; only `1:1` rows bridge
mechanically:

```python
conc = pl.read_csv(
  'data/naics_2017_to_2022.csv',
  schema_overrides={'naics_2017': pl.Utf8, 'naics_2022': pl.Utf8},
)
bridged = series_2017.join(conc, left_on='naics', right_on='naics_2017', how='left')
needs_allocation = bridged.filter(pl.col('link_type').ne('1:1'))
```

## NAICS semantics

| level | name | digits | example |
|---|---|---|---|
| 2 | sector | 2 (or a range) | `31-33` Manufacturing |
| 3 | subsector | 3 | `311` Food Manufacturing |
| 4 | industry group | 4 | `3111` Animal Food Manufacturing |
| 5 | NAICS industry | 5 | `31111` |
| 6 | national industry | 6 | `311111` Dog and Cat Food Manufacturing |

- **Three sectors are ranges — `31-33`, `44-45`, `48-49` — so `code[:2]` is never sector-safe.**
  `461` does not exist but `48` and `49` are both Transportation and Warehousing. Group and
  filter on `sector_code`; walk the tree on `parent_code`. Both are materialized in the files
  precisely so no one re-derives them wrong.
- There are 20 sectors in every recent vintage. Six-digit codes are **U.S.-specific detail**;
  cross-country (US/Canada/Mexico) comparability holds only on rows flagged `trilateral` (the
  superscript-T lines in the Census files, stripped from the stored titles).
- Vintages revise every 5 years: 1997, 2002, 2007, 2012, 2017, 2022, with 2027 in progress.
  Datasets adopt a vintage years after it exists, program by program — which program is on which
  vintage for which reference period is a *program* fact: `bls-data-context`.
- `999999` / "unclassified" appears in QCEW and admin data but is not part of the standard.
  PSP-style microdata carries NAICS assigned at client onboarding — codes go stale and vintages
  mix within a single panel month. Never assume a panel is single-vintage.

## SOC semantics

- Canonical form is hyphenated `XX-YYYY`. **The aggregation level is encoded in the trailing-zero
  pattern of the digits, not in prefix length**: `XX-0000` major group, ends `00` minor, ends
  `0` broad, else detailed. This is a different parsing rule than NAICS — do not transplant
  prefix logic. `parent_code` is materialized (minor groups mix `XX-Y000` and `XX-YY00`
  granularity, so digit surgery mis-parents; the files already resolved it).
- 2018 SOC: 23 major groups, 98 minor, 459 broad, 867 detailed. 2010: 23 major, 840 detailed.
  Vintages: 2000, 2010, 2018.
- Codes ending in `9` titled "… All Other" are residual catch-alls. They are where semantic
  title-matching goes to die: absence of a specific title does not mean absence of the workers.
- **Taxonomies that masquerade as SOC:** O*NET-SOC extends detailed SOC with 8-digit `.XX`
  suffixes — not SOC, don't join it raw. OEWS spent transition vintages on hybrid taxonomies.
  CPS/ACS use 4-digit *Census occupation codes* (leading zeros!) that crosswalk to SOC — that
  crosswalk is not yet bundled; say so rather than improvising one.

## Vintages and concordances

- Concordances are **many-to-many and unweighted**. The official files identify the links;
  allocating employment across a `1:m` split needs external weights (QCEW or CBP shares) — the
  concordance alone cannot do it, and pretending otherwise silently reallocates jobs.
- **Same code ≠ same content across vintages.** A code can persist while its boundary moves
  (it will appear in `m:1`/`1:m`/`m:m` rows with itself). Check `link_type` — never code
  equality — before treating a series as continuous across a revision.
- The canonical break: **NAICS 2022 rebuilt retail.** Subsector `454` (nonstore retailers,
  including `454110` electronic shopping) was abolished and e-commerce reallocated into
  product-line retailers; furniture and electronics stores merged into new subsector `449`.
  Any industry employment series crossing the adoption boundary breaks there by construction.
- Joining two datasets coded in different vintages requires an explicit concordance join with
  `link_type` handling. There is no shortcut.

## Boundary with bls-data-context

Program-specific encodings — CES industry codes and supersectors, QCEW `agglvl`/ownership
codes, how NAICS is embedded in a `series_id`, and which program adopted which vintage when —
live in `bls-data-context`. This skill owns the classification systems themselves and their
concordances. Both may load together; that is correct, not redundant.

## Rebuilding the data

```bash
uv run skills/classification-codes/scripts/build.py            # download, parse, validate
uv run skills/classification-codes/scripts/build.py --offline  # rebuild from sources/ cache
```

`scripts/build.py` pins the official Census/BLS URLs, handles the known layout quirks (preamble
rows, ranged sector codes, trilateral markers, numeric code cells, one-code-column-per-row SOC
sheets), and hard-fails on structural drift (sector/major-group counts, hierarchy closure,
duplicate codes, concordance referential integrity). Commit `data/`, `sources/`, and
`MANIFEST.md` together: Census and BLS overwrite source files in place, so an unarchived source
vintage is unrecoverable. Adding NAICS 2012 or the 2012→2017 concordance is one `Build` entry.
