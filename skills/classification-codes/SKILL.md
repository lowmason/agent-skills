---
name: classification-codes
description: >
  Use when a task touches NAICS or SOC codes — mapping a code to its title or a title to its
  code, listing a sector's, subsector's, or major group's members, converting between vintages
  (NAICS 2012↔2017↔2022, SOC 2010↔2018), joining datasets coded in different vintages,
  interpreting a series break at a classification revision, or explaining how industries and
  occupations are defined, created, and revised (ECPC / SOCPC, NAICS 2027, SOC 2028). Consult
  BEFORE answering any code↔title question, before joining on an industry or occupation code,
  and before treating a code as meaning the same thing in two vintages. Trigger on: NAICS, SOC,
  O*NET, sector, subsector, industry group, six-digit code, occupation code, major group,
  detailed occupation, concordance, crosswalk, trilateral, change indicator, unclassified /
  999999, "what industry is X", "what does code X mean", "is code X still valid", "when is the
  next revision". Codes and titles come from data/, never from model memory.
license: MIT
model: haiku
metadata:
  author: Lowell Mason
  version: "0.2"
---

# Classification Codes (NAICS & SOC)

## What this is

The authoritative local copy of the U.S. industry (NAICS) and occupation (SOC) classification
systems, plus the official vintage concordances, as tidy greppable CSVs under `data/`. This
SKILL.md carries the structural semantics and the query recipes; the codes themselves live only
in the data files, and how the systems are governed and revised lives in
`references/revision-process.md`.

**Prime directive: never answer a code↔title, membership, or vintage question from memory.**
Code→referent mappings are arbitrary, dense, and vintage-dependent — exactly what a model
confabulates most fluently (a no-skill control asserted "for certain" that `449210` sits in a
hardware-store group; it is Electronics and Appliance Retailers). Grep for point lookups; load
with Polars for hierarchy, membership, or concordance work. If a file below is missing,
`MANIFEST.md` says why (`NOT BUILT`) — rebuild it (see *Rebuilding*) rather than guessing.

## Files

| file | rows | columns |
|---|---|---|
| `data/naics_2022.csv` | 2,125 (1,012 six-digit) | `code, level, title, parent_code, sector_code, trilateral, change_indicator` |
| `data/naics_2017.csv` | 2,196 (1,057 six-digit) | same |
| `data/naics_2012.csv` | 2,209 (1,065 six-digit) | same |
| `data/naics_2017_to_2022.csv` | 1,150 | `naics_2017, title_2017, naics_2022, title_2022, link_type` |
| `data/naics_2012_to_2017.csv` | 1,069 | `naics_2012, title_2012, naics_2017, title_2017, link_type` |
| `data/soc_2018.csv` | 1,447 (867 detailed) | `code, level, title, parent_code` |
| `data/soc_2010.csv` | 1,421 (840 detailed) | same |
| `data/soc_2010_to_2018.csv` | 900 | `soc_2010, title_2010, soc_2018, title_2018, link_type` |

`level` is 2–6 for NAICS and `major | minor | broad | detailed` for SOC. `trilateral` marks the
Census superscript-T rows. `change_indicator` is Census's own marker for what changed at that
code versus the prior vintage (`*` title only, `**` new code, `***` re-used code with content
change, `****` content change at a lower level); null means unchanged. `link_type` is derived
from code multiplicities: `1:1` (unchanged or clean recode), `1:m` (split), `m:1` (merge),
`m:m` (reshuffle). `MANIFEST.md` records the source URL, sha256, and retrieval time behind every
file; `sources/` holds the exact source bytes.

## How to query

**Codes are strings, always.** NAICS prefix logic dies on integers, and the adjacent Census
occupation codes carry leading zeros. In Polars, force them:
`schema_overrides={'code': pl.Utf8, 'parent_code': pl.Utf8, 'sector_code': pl.Utf8}` (and the
`naics_*` columns of the concordances).

Point lookups — grep, don't load:

```bash
grep -E '^561320,' data/naics_2022.csv          # code -> title
grep -iE 'temporary help' data/naics_2022.csv    # title -> code
grep -E '^15-1252,' data/soc_2018.csv            # SOC lookup
grep -E '^454110,' data/naics_2017_to_2022.csv   # where did a 2017 code go (42 rows, all m:m)
```

Membership and hierarchy — load, then use the materialized columns, never string surgery:

```python
naics = pl.read_csv(
  'data/naics_2022.csv',
  schema_overrides={'code': pl.Utf8, 'parent_code': pl.Utf8, 'sector_code': pl.Utf8},
)
manufacturing = naics.filter(pl.col('sector_code').eq('31-33').and_(pl.col('level').eq(6)))
children = naics.filter(pl.col('parent_code').eq('5613'))
new_in_2022 = naics.filter(pl.col('change_indicator').eq('**'))
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
  cross-country (US/Canada/Mexico) comparability holds only on rows flagged `trilateral`, which
  occur at levels 2–5 only (all 20 sectors; 466 of 689 five-digit industries in 2022) and never
  at six digits.
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
  prefix logic. `parent_code` is materialized from the sheet's own nesting because the pattern
  is not even reliable for parentage: minor groups mix `XX-Y000` and `XX-YY00` granularity, and
  **the 2018 SOC overflows a code range** — `29-1221` through `29-1229` (pediatricians,
  pathologists, psychiatrists, radiologists, physicians all other) belong to broad group
  `29-1210` Physicians; there is no `29-1220`. Digit surgery orphans all five.
- 2018 SOC: 23 major groups, 98 minor, 459 broad, 867 detailed. 2010: 23 major, 97 minor,
  461 broad, 840 detailed. Vintages: 2000, 2010, 2018; 2028 is under review.
- **Join on code, never on title.** BLS's own structure and crosswalk files disagree on ten
  titles (hyphenation, `First-line` vs `First-Line`, a curly apostrophe in `Sheriff’s` that a
  straight-quote grep misses, and one typo, `Repairs` for `Repairers`, in the 2010 structure).
  The files are stored as published, so a title grep is a starting point, not a key.
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
  (it will appear in `m:1`/`1:m`/`m:m` rows with itself, and its structure row carries `***` or
  `****`). Check `link_type` — never code equality — before treating a series as continuous
  across a revision.
- Coverage is complete: every six-digit code on both sides of each concordance appears in at
  least one row, so an unmatched code after a join is a bad key, not a gap. 2017→2022 is 928
  `1:1` (916 same code, 12 clean recodes), 5 `1:m`, 120 `m:1`, 97 `m:m`; 2012→2017 is 1,045
  `1:1`, 3 `1:m`, 16 `m:1`, 5 `m:m`.
- Where Census names the piece of a source industry that flows to a target, the source title
  carries it as a suffix: `Crude Petroleum and Natural Gas Extraction - natural gas extraction`.
- SOC 2010→2018 is 766 `1:1`, 70 `1:m`, 32 `m:1`, 32 `m:m`, covering all 840 and 867 detailed
  codes. BLS marks split sources `(#)` and merged targets `(##)` in its own titles; the build
  verified those markers agree with `link_type` on every row and then stripped them, so the
  stored titles are the official ones. The software-developer split is the canonical case:
  2010 `15-1132` and `15-1133` both feed 2018 `15-1252` and `15-1253`, all four rows `m:m`.
- The canonical break: **NAICS 2022 rebuilt retail.** Subsector `454` (nonstore retailers,
  including `454110` electronic shopping) was abolished and e-commerce reallocated into
  product-line retailers (42 targets, every row `m:m`); furniture and electronics stores merged
  into new subsector `449`. Any industry employment series crossing the adoption boundary breaks
  there by construction.
- Joining two datasets coded in different vintages requires an explicit concordance join with
  `link_type` handling. There is no shortcut.

## How codes are created and revised

Both systems are OMB statistical standards (Directives No. 8 and No. 10) maintained by
interagency committees — the ECPC for NAICS (with Statistics Canada and INEGI as trilateral
partners) and the BLS-chaired SOCPC for SOC — and both revise through the same three Federal
Register notices: solicitation of proposals, committee recommendations for comment, OMB final
decisions. NAICS is reviewed every five years; a new industry must group establishments with the
same production process and be large enough to publish without disclosure at sub-national
levels. SOC is task-based (work performed, not credentials); a new detailed occupation exists
only if BLS or Census can collect data on it, and the residual "All Other" rule absorbs whatever
the structure does not name. NAICS 2027 recommendations were published 2026-07-13 with OMB's
final decisions pending; SOC 2028 is under review for use from reference year 2028, after which
SOC revisions follow NAICS by one year on a ten-year cycle. Dates, citations, the ten SOC
principles and six coding guidelines, and the per-vintage change-indicator legend:
`references/revision-process.md`.

## Boundary with bls-data-context

Program-specific encodings — CES industry codes and supersectors, QCEW `agglvl`/ownership
codes, how NAICS is embedded in a `series_id`, and which program adopted which vintage when —
live in `bls-data-context`. This skill owns the classification systems themselves, their
concordances, and their revision process. Both may load together; that is correct, not
redundant.

## Rebuilding the data

```bash
uv run skills/classification-codes/scripts/build.py            # download, parse, validate
uv run skills/classification-codes/scripts/build.py --offline  # rebuild from sources/ cache
cd skills/classification-codes/scripts && uv run --python 3.13 --with pytest --with polars --with fastexcel python -m pytest -q
```

`scripts/build.py` pins the official Census/BLS URLs, handles the known layout quirks (preamble
and legend rows, ranged sector codes, trilateral markers with trailing spaces, numeric code
cells, multi-line header cells, one-code-column-per-row SOC sheets nested by row order, BLS
split/merge title markers), and hard-fails on structural drift (sector/major-group counts,
hierarchy closure, nesting that contradicts the code pattern, duplicate codes, unknown change
markers, trilateral six-digit rows, crosswalk markers that disagree with `link_type`,
concordance referential integrity). A failed download skips that artifact and records the reason
in `MANIFEST.md` so the rest still builds.

**bls.gov admits scripts only with a contact email in the User-Agent** (an Akamai "Access
Denied" 403 otherwise, and also for any User-Agent containing `github.com` or
`python-requests`). Export `BLS_CONTACT_EMAIL` — the same variable `bls-stats` uses — before
building the SOC artifacts; without it the build refuses to contact bls.gov rather than get
blocked. Fallback: save the workbook from a browser into `sources/` under its original filename
without opening it in Excel (a re-save changes the bytes and the recorded sha256), and the
cached copy is used. Commit `data/`, `sources/`, and `MANIFEST.md` together: Census and BLS
overwrite source files in place, so an unarchived source vintage is unrecoverable. Adding a
vintage or a concordance is one `Build` entry (plus a `REFERENTIAL_PAIRS` row for a
concordance).
