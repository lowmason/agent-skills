---
name: geographic-codes
description: >
  Use when a task touches U.S. statistical geography codes over any time span — FIPS state or
  county codes, county-equivalents (parishes, boroughs, census areas, independent cities,
  municipios, Connecticut planning regions), CBSAs / MSAs / micropolitan areas, metropolitan
  divisions, CSAs — mapping a code to a name, listing a metro's counties, asking whether a
  code was valid at a reference date, joining panels across a county change or an OMB
  re-delineation, diagnosing a break that coincides with one, or explaining how OMB and
  Census define and revise these areas. Consult BEFORE answering any geography code
  question, before joining on a county or CBSA code, and before treating a code as the same
  thing at two dates. Trigger on: FIPS, GEOID, county code, CBSA, MSA, metro area,
  micropolitan, metropolitan division, CSA, NECTA, planning region, "what county is X",
  "which metro is Y in", "was this code valid in", delineation, county change, OMB bulletin,
  central / outlying county, commuting threshold.
license: MIT
model: haiku
metadata:
  author: Lowell Mason
  version: "0.2"
---

# Geographic Codes (FIPS, county-equivalents, CBSA/CSA)

## What this is

Interval-stamped reference tables for U.S. statistical geography under `data/`. Every row
carries `valid_from` and `valid_to`; the question is always **"valid at this reference date"**,
never "which vintage file do I open". Sibling of `classification-codes` (NAICS/SOC), same
architecture, same prime directive.

**Prime directive: never answer a code↔name, membership, or validity question from memory, and
never answer one without a reference date.** County-equivalents changed code or name on 16
distinct dates since 1990 and CBSAs were re-delineated by seven OMB bulletins since 2013; a code
that is right today was wrong for part of any multi-year panel. Grep for point lookups; load
with Polars for as-of, membership, or panel work. If `data/` is missing, rebuild it first.

## Files

| file | rows | columns |
|---|---|---|
| `data/states.csv` | 57 | `state_fips, state_usps, state_name, region_code, region_name, division_code, division_name, entity_type` |
| `data/counties.csv` | 3,243 | `county_geoid, name, state_fips, county_fips, state_usps, entity_type, valid_from, valid_to, is_current` |
| `data/county_changes.csv` | 38 | `change_group, effective_date, change_type, old_geoid, old_name, new_geoid, new_name, creates_new, status, source_note` |
| `data/cbsa_counties.csv` | 13,326 | `delineation, bulletin, cbsa_code, cbsa_title, cbsa_type, metdiv_code, metdiv_title, csa_code, csa_title, county_geoid, county_name, central_outlying, valid_from, valid_to` |
| `data/cbsa.csv` | 6,577 | `delineation, bulletin, cbsa_code, cbsa_title, cbsa_type, csa_code, csa_title, n_counties, n_metdivs, states, valid_from, valid_to` |

`counties.csv` has one row per entity-interval (3,222 current plus 21 closed), so the key is
`(county_geoid, valid_from)`, not `county_geoid` alone: a rename produces two rows with the same
code. `cbsa_counties.csv` holds one block per OMB delineation — `2013`, `2015`, `2017`,
`2018-04`, `2018-09`, `2020`, `2023` — with the issuing bulletin number alongside.
`MANIFEST.md` records source URL, sha256, and retrieval time; `sources/` holds the exact source
bytes.

## Interval semantics

- Intervals are half-open: **`[valid_from, valid_to)`**. Query with
  `is_between(valid_from, valid_to, closed='left')`.
- Sentinels: `valid_from = 1990-01-01` means *already existed when the change log begins*, not
  created that day. `valid_to = 9999-12-31` means currently valid (`is_current` is the same
  fact as a bool).
- **`valid_from` means exactly one thing: the date the code became valid for federal
  statistical products** (Census effective date for county-equivalents, OMB bulletin issue date
  for delineations). There are two other clocks that look similar and are not: the date the
  change happened in state law (Connecticut's councils of governments predate Census
  recognition by years), and the date a given BLS/BEA program started publishing on it (SAE
  implemented the 2023 delineations in March 2025). Program adoption dates live in
  `bls-data-context`. Do not use `valid_from` as a proxy for either of the other two.
- The bridge across county intervals is `county_changes.csv`. `change_type` plays the role
  `link_type` plays in the NAICS concordances: `rename` and `recode` bridge mechanically; `split`
  needs weights; `merge` sums; `create` / `dissolve` have no old or new side. The Connecticut
  restructuring is recorded as 8 dissolves + 9 creates in one `change_group` because the
  county↔planning-region relation is many-to-many at the town level and is **not bundled** — say
  so rather than improvising a bridge.
- Delineation blocks abut: each block's `valid_to` is the next bulletin's issue date. The two
  2018 bulletins are both present (18-03 in April, superseded by 18-04 in September), so there
  is no gap in coverage from 2013-02-28 onward.

## How to query

**Codes are strings, always.** FIPS leads with zeros (`01` Alabama, `001` Autauga). Load with
`schema_overrides={'county_geoid': pl.Utf8, 'state_fips': pl.Utf8, 'county_fips': pl.Utf8}`
and `try_parse_dates=True`.

Point lookups — grep, don't load:

```bash
grep -E '^25025,' data/counties.csv               # code -> name, all intervals
grep -iE 'oglala|shannon' data/counties.csv        # both sides of a recode
grep -E '^2023,[^,]*,14460,' data/cbsa_counties.csv  # a metro's counties, current delineation
grep -E ',14460,' data/cbsa.csv                    # one metro across every delineation
```

As-of lookup — the default shape for everything else:

```python
counties = pl.read_csv(
    'data/counties.csv',
    schema_overrides={'county_geoid': pl.Utf8, 'state_fips': pl.Utf8, 'county_fips': pl.Utf8},
    try_parse_dates=True,
)
as_of = counties.filter(
    pl.col('valid_from').le(ref_date).and_(pl.col('valid_to').gt(ref_date))
)
```

Stamping a panel whose rows carry their own reference dates:

```python
matched = (
    panel
    .join(counties, on='county_geoid', how='left')
    .filter(pl.col('ref_date').is_between(pl.col('valid_from'), pl.col('valid_to'), closed='left'))
)
```

**Staleness detector** — the inverse of the stamp. Microdata carries the geography assigned at
onboarding, so a 2025 panel month will still contain `09001` for clients nobody re-coded. Rows
that fail to match are records asserting a code that was not valid at their own reference date:

```python
stale = panel.join(matched.select('client_id'), on='client_id', how='anti')
```

Metro membership as-of, metropolitan only, no division double-counting:

```python
cbsa_counties = pl.read_csv(
    'data/cbsa_counties.csv',
    schema_overrides={'cbsa_code': pl.Utf8, 'county_geoid': pl.Utf8, 'metdiv_code': pl.Utf8, 'csa_code': pl.Utf8},
    try_parse_dates=True,
)
metros_as_of = cbsa_counties.filter(
    pl.col('valid_from').le(ref_date)
    .and_(pl.col('valid_to').gt(ref_date))
    .and_(pl.col('cbsa_type').eq('metropolitan'))
)
```

## County-equivalent semantics

- `county_geoid` (5 digits, state + county) is the only key. 3-digit county FIPS is unique only
  within a state; names are worse (30-odd Washington Counties, `LaSalle` vs `La Salle`,
  `Doña Ana`). Never join on names.
- **Spelling corrections are not renames.** Census corrected `De Kalb`→`DeKalb`,
  `La Porte`→`LaPorte`, `Mc Kean`→`McKean`, `Dona Ana`→`Doña Ana`, `La Salle`→`LaSalle`
  (IL and LA) and a few others without an effective date, treating the old spelling as an
  error. `counties.csv` carries the current gazetteer spelling for the whole interval; older
  source files will disagree on the name while the code is unchanged.
- `entity_type` distinguishes county, parish (LA), borough / city_and_borough / census_area /
  municipality (AK), independent_city (38 in VA plus Baltimore, St. Louis, Carson City),
  municipio (PR), planning_region (CT), district (DC), and `other` for the retired Yellowstone
  National Park county-equivalent. Independent cities are **not inside a county**; summing
  counties to a state without them undercounts.
- **Connecticut is the flagship break.** Eight counties (`09001`–`09015`) were retired for nine
  planning regions (`09110`–`09190`) effective 2022-06-06 for federal statistics (87 FR 34235).
  County-level series do not join across it.
- Alaska redraws boroughs and census areas continually (Valdez-Cordova → Chugach + Copper River,
  2019; Wade Hampton → Kusilvak, 2015; Petersburg, Wrangell, Prince of Wales, Skagway, and
  Hoonah-Angoon in 2007–13). Oglala Lakota `46102` replaced Shannon `46113` in 2015. Bedford city
  `51515` folded into Bedford County in 2013. All are in `county_changes.csv`, every row
  verified against the Census county-changes pages (`status = verified`).
- `999` county and similar sentinels are program conventions (QCEW unknown/statewide), not
  Census geography — `bls-data-context`.

## CBSA / CSA semantics

- **CBSA ≠ MSA.** CBSA is the umbrella: metropolitan (urban core ≥ 50k) and micropolitan
  (10k–50k) sit in the same file. Filter on `cbsa_type`.
- Metropolitan divisions subdivide the largest MSAs (31 divisions through 2020, 37 in 2023).
  Summing `metdiv_code` rows and their parent `cbsa_code` double-counts. CSAs are optional
  groupings of adjacent CBSAs; most CBSAs have `csa_code` null.
- CBSA codes are 5-digit and share a numeric space with county GEOIDs. `35620` is the New York
  MSA, not a county. A bare 5-digit code is ambiguous until you know which table it came from.
- Delineations change **which counties belong to which metro**, so a metro employment series
  breaks at the *program's adoption date* of a new delineation, not at the bulletin date.
- **NECTAs (New England town-based metros) were discontinued by the 2020 OMB standards.** Older
  BLS New England metro series are NECTA-based and carry different codes and boundaries than the
  county-based CBSAs that replaced them; the two are not the same series with a new label.
- MSAs cross state lines. Never aggregate metros to a state.
- `central_outlying` records why a county is in the CBSA: central counties contain the urban
  core, outlying counties qualify by commuting. Outlying counties are the ones that move between
  delineations.

## How these areas are defined and when they change

The qualification rules (urban-area population thresholds, the 25 percent commuting test, the
employment-interchange measure for divisions and CSAs), the two revision clocks (OMB's
decennial standards plus intercensal bulletins; Census's January 1 boundary reference date and
per-decade county-change log), and the list of bulletins with their archive URLs are in
`references/how-geographies-are-defined.md`. Read it before explaining *why* a county joined or
left a metro, before predicting when the next re-delineation lands, or before describing what a
county change means for a series.

## Deliberately not bundled

- **ZIP / ZCTA.** ZIPs are USPS delivery routes, not Census geography; ZCTAs approximate them and
  nest into neither counties nor places. ZIP→county is a *weighted* crosswalk (HUD USPS
  Crosswalk, quarterly, residential/business address shares) — the geographic analogue of an
  employment-weighted NAICS bridge. Point at HUD; do not improvise a many-to-one lookup.
- The town-level Connecticut county↔planning-region crosswalk (Census publishes it separately).
- Pre-2013 delineations (2003–2009, under the 2000 standards) and the 2003 switch from
  MSA/PMSA/CMSA to CBSAs. Coverage starts with the first delineation under the 2010 standards.
- Boundary-only changes (annexations, corrections) between existing county-equivalents. The
  change log records code and name events only; territory moving between two live codes is
  noted in `source_note` when it accompanies one.
- BLS `la.area` / `sm.area` codes and QCEW area conventions — program encodings, `bls-data-context`.

## Boundary with bls-data-context

Which BLS program adopted which delineation for which reference period, how a county or CBSA
code is embedded in a `series_id` or an `area_fips`, NECTA-era series codes, and the QCEW
`999` / statewide conventions live in `bls-data-context`. This skill owns the geographic
entities themselves, their validity intervals, and the change log. Both may load together; that
is correct, not redundant.

## Rebuilding the data

```bash
uv run skills/geographic-codes/scripts/build.py            # download, synthesize, validate
uv run skills/geographic-codes/scripts/build.py --offline  # from sources/ cache
uv run skills/geographic-codes/scripts/build.py --list     # the pinned sources
```

`counties.csv` is *synthesized*: the current Census gazetteer supplies the live set, and
`seeds/county_changes.csv` is played forward from 1990 to open and close intervals. The seed is
hand-curated because Census publishes county changes as prose, one page per decade; rows carry
`status=unverified` until checked against those pages, and the build warns on every unverified
row. Validation covers chronology, closure against the gazetteer, non-overlapping intervals,
CBSA count bands, per-CBSA title consistency, and a referential check that every county a
delineation names had a valid interval on that delineation's bulletin date — the check that
catches a 2023 file coded with Connecticut's retired counties. Commit `data/`, `sources/`,
`seeds/`, and `MANIFEST.md` together. Adding a delineation vintage is one `Delineation` entry;
tests for the synthesizer, readers, and checks are in `scripts/test_build.py`:

```bash
cd skills/geographic-codes/scripts && uv run --python 3.13 --with pytest --with polars --with fastexcel python -m pytest -q
```
