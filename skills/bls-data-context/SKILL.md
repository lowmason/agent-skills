---
name: bls-data-context
description: >
  Use when working with U.S. Bureau of Labor Statistics employment, wage, or labor-turnover data
  — QCEW, CES (national or state/area SAE), JOLTS, BED/BDM, OEWS/OES, ECI, ECEC, CPS — or
  building pipelines over their flat files or API. Consult BEFORE interpreting a BLS series,
  constructing or parsing a series ID, joining two BLS sources, reconciling to an official total,
  or reasoning about revisions / as-of correctness. Trigger on: QCEW, CES, CES-SA, SAE, JOLTS,
  BED, BDM, OEWS, OES, ECI, ECEC, CPS, LAUS, NAICS / SOC codes, series_id, M01–M13,
  download.bls.gov/pub/time.series, vintage / benchmark / revision, place-of-work vs residence,
  jobs vs persons, thousands-vs-persons units, "pay period including the 12th", UI / UCFE
  coverage, net birth-death model, benchmarking CES to QCEW, JOLTS alignment to CES, or
  reconciling a payroll-provider or nowcast series to BLS. The detailed program facts that agents
  otherwise get subtly wrong.
license: MIT
model: haiku
metadata:
  author: Lowell Mason
  version: "1.0"
---

# BLS Data Context

## What this is

The canonical reference for the BLS employment and wage programs this work depends on. This
SKILL.md is the **hub** — program selection, the concepts that cut *across* programs, and
cross-program reconciliation. Each program has a full, self-contained reference in
`references/<program>.md`. **Read the one(s) you need; do not load all nine** — that is the whole
point of the split. Come here first to pick the right program and to get the cross-cutting rules,
then open the specific reference for series-ID anatomy, flat-file schema, and lookup codes.

## Program selector

| Program | Measures | Basis · unit | Freq | Geography | Reference |
|---|---|---|---|---|---|
| **QCEW** | Covered jobs, establishments, wages, avg weekly wage | Establishment · **place of work**, UI/UCFE near-census (~95–97%) | Monthly emp + quarterly wages | Nation→county, MSA, PR/VI | [references/qcew.md](references/qcew.md) |
| **CES-N** | Nonfarm payroll jobs, hours, earnings | Establishment **sample** (QCEW/LDB frame) | Monthly | National | [references/ces.md](references/ces.md) |
| **CES-SA / SAE** | State & metro payroll jobs, hours, earnings | Establishment sample + small-area model | Monthly | 50 states, DC, PR, VI, NYC, ~430 MSAs | [references/sae.md](references/sae.md) |
| **JOLTS** | Job openings (stock), hires, separations (quits / layoffs / other) | Establishment sample (~21k, QCEW+FRA frame) | Monthly | Nation, region, **state = model-based** | [references/jolts.md](references/jolts.md) |
| **BED / BDM** | Gross job gains/losses, openings/closings, births/deaths | QCEW-derived administrative · establishment | Quarterly | Nation, state | [references/bed.md](references/bed.md) |
| **OEWS** | Occupational employment & wages by SOC | Establishment survey | Annual (May vintage) | Nation×industry; **state = cross-industry only** | [references/oews.md](references/oews.md) |
| **ECI** | *Change* in employer labor cost (fixed-weight index) | NCS establishment · index, Dec 2005=100 | Quarterly | Nation, region/division, 15 MSAs | [references/eci.md](references/eci.md) |
| **ECEC** | *Level* of employer cost per hour ($) | NCS establishment | Quarterly (Mar/Jun/Sep/Dec) | Nation, region/division, 15 MSAs (**no state**) | [references/ecec.md](references/ecec.md) |
| **CPS** | Employed/unemployed/NILF, unemployment rate, labor force | **Household** · **persons by residence** | Monthly | Nation, state | [references/cps.md](references/cps.md) |

## The one frame underneath most of it

**QCEW (state UI + federal UCFE administrative records) is the spine.** It is the sampling frame
and/or annual benchmark for CES, SAE, JOLTS, OEWS, and the NCS (ECI/ECEC); **BED is derived from
QCEW microdata directly**. The lone exception is **CPS**, which is a household survey on its own
frame. Consequences worth internalizing:

- A quirk or revision in QCEW propagates: a CES/SAE benchmark, a JOLTS denominator, a BED job-flow.
- "Compare my series to QCEW" is usually the right reconciliation target *because* QCEW is the
  universe — but it lags (~6 months, preliminary until finalized the next year).
- **QCEW has two different coverage gaps — do not conflate them.** *Against all U.S. jobs:* QCEW
  covers **more than 95%**; the miss is proprietors, the unincorporated self-employed, unpaid family
  workers, certain farm and domestic workers, and active-duty military. That gap is why a
  microdata-to-QCEW reconciliation never closes to exactly 100% — and those groups are **also out of
  CES scope**, so they are never added back at benchmark.
- *Against CES **in-scope** employment:* QCEW covers **~97%**. The residual ~3% is **noncovered
  employment (NCE)** — in CES scope but outside UI coverage: certain student workers, hospital
  interns, elected or appointed officials, some nonprofit or religious employment, RRB-covered
  railroad employment, plus corporate officers (a large noncovered group in states whose UI rules
  exclude them). CES adds NCE from other sources at the March benchmark.

## Cross-cutting concepts

These apply across programs and are the facts agents most often get subtly wrong. Program-specific
detail lives in each reference.

**Jobs vs persons.** Establishment programs (QCEW, CES, SAE, JOLTS, BED) count *filled jobs* — a
multiple-jobholder is counted once per job. **CPS counts people**, once. Never reconcile a payroll
job count one-for-one with CPS employment.

**Place of work vs residence.** QCEW/CES/SAE/JOLTS are **workplace**-based. CPS (and LAUS) are
**residence**-based. County-level workplace ≠ residence employment whenever there is commuting.

**Reference period: "the pay period including the 12th."** Shared by every establishment program's
employment count (QCEW, CES, SAE, JOLTS). CPS uses the reference *week* including the 12th. This is
not the calendar month — strikes, weather, holidays, and shutdowns that hit other weeks may not
show.

**Seasonal adjustment (SA vs NSA).** Use SA for month-to-month interpretation; use NSA for
benchmarking, birth-death reasoning, and direct administrative reconciliation. **Never mix SA and
NSA in one calculation.** Critically: **net birth-death forecasts and benchmark comparisons are NSA
concepts** — do not compare an NSA birth-death figure to an SA over-the-month change. Most programs
use concurrent X-13ARIMA-SEATS, so **SA history revises every month** even before a benchmark.

**Vintage, revisions, and the knowability boundary.** Every observation has a date on which it
*could first have been seen*; a revision merged back onto its original `ref_date` looks like
clairvoyance in a backtest. Per-program revision behavior (load the reference for specifics):

| Program | Revision pattern |
|---|---|
| QCEW | Preliminary until finalized with Q1 of the following year (Q1 data published 5×). |
| CES-N | Prelim → 2nd → 3rd sample-based; **annual March benchmark** to QCEW (NSA ~21 mo, SA 5 yr). |
| SAE | Annual benchmark to QCEW + NCE (NSA ~20 mo; SA longer); small-area model cells revise too. |
| JOLTS | Prior month revised each release; **annual benchmark to CES** (SA & NSA ~5 yr). |
| BED | Annual revision with Q1 data; death series lag ~3 quarters by construction. |
| OEWS | Annual; each May release is a vintage. |
| ECI | NSA final on publication; SA revised 5 yr; fixed weights reweighted ~every 10 yr. |
| ECEC | Cost levels final on publication; constant-dollar CPE revised annually. |
| CPS | Annual January population-control updates shift *levels*; SA reestimated 5 yr. |

For real-time/nowcast work: train and evaluate on the **vintage available at prediction time**, not
today's revised history. Pin inputs by release date / vintage, not "latest."

**Units & rounding traps.** CES and JOLTS **levels are in thousands**; QCEW is in **persons/jobs**
(counts). A reconciliation off by almost exactly 1000× is a units bug, not a data problem. Rates
appear as fractions or percent depending on file — check before arithmetic. BLS computes AWW, AHE,
percentages, and OTY changes from **unrounded** internals, so recomputing from rounded public
values yields small, expected discrepancies.

**NAICS / SOC and classification breaks.** Industry = NAICS, occupation = SOC, both revised on
cycles (NAICS ~every 5 yr; CES uses 2022 NAICS, OEWS/CPS have their own adoption dates). A CES/SAE
"industry code" is not always one NAICS industry. First-quarter discontinuities are often
recoding, not economics. Record the classification vintage for any long series.

**Flat-file conventions (LABSTAT).** Files live at `download.bls.gov/pub/time.series/<prefix>/`
(`en`/downloadable for QCEW, `ce`, `jt`, `bd`, `oe`, …). Data files are `series_id | year | period
| value | footnote_codes`; a `<prefix>.series` file holds metadata; mapping files decode each
dimension. **Period codes vary by program *and* by datatype within a program** — check the
program's `<prefix>.period` mapping file, or its `<prefix>.series` begin/end periods, before
assuming. Monthly (CES, SAE, JOLTS): `M01`–`M12`, with **`M13` = annual average**. Quarterly (BED,
ECI, ECEC, and the QCEW wage datatypes): `Q01`–`Q04`, plus **`Q05` = annual average** where a
quarterly program publishes one (BED has none — its series stay `Q01`–`Q04`). Annual-only cells
carry **`A01`** (QCEW average annual pay, OEWS). QCEW alone spans all three: employment is monthly
`M01`–`M12`, establishment counts / total wages / average weekly wage are quarterly `Q01`–`Q04`,
and average annual pay is `A01`. **Never mix an annual-average code into a periodic series** (drop
`M13` from monthly work, `Q05` from quarterly), and **never filter a quarterly file with a
monthly rule** — `M01`–`M12` over a BED, ECI, or ECEC file matches zero rows and silently empties
the frame instead of erroring.
**Series IDs have a fixed positional anatomy** (e.g. JOLTS 21 chars, BED 28 chars, CES CEU/CES
prefix) — parse by position and join the mapping files; do not hand-construct blindly. **Preserve
all code columns as strings with leading zeros** (`state_code`, `industry_code`, size classes).

## Cross-program reconciliation

- **CES ↔ QCEW:** QCEW is the CES/SAE benchmark source (~97% of scope; NCE added for the rest).
  Reconcile on the **March** benchmark month, **NSA**, aligned industry/ownership scope.
- **JOLTS ↔ CES:** JOLTS rates use **CES employment denominators**, and BLS *aligns* JOLTS
  hires-minus-separations to CES net change — so JOLTS net flow is **not** an independent check on
  CES growth, and JOLTS revises when CES revises even if its own microdata didn't.
- **BED ↔ QCEW/CES:** BED is QCEW-derived but narrower (private only, excludes zero-employment and
  government); its net change need not match QCEW or CES change. Explain differences; don't force.
- **OEWS limits:** national × industry × SOC and state × *cross-industry* × SOC only — there are no
  state × industry cells in the time series.
- **Provider/nowcast ↔ official:** payroll-provider microdata is **not** a random sample of the
  population — coverage skews by size/industry/region. Quantify the skew against QCEW before
  generalizing, and score nowcasts against the real-time vintage.
- **Golden rule:** do not compare QCEW, CES, CPS, LAUS, BED, JOLTS, OEWS, BEA, or CBP levels
  directly without reconciling concept, scope, timing, geography, and coverage first.

## Pitfalls that span programs

- Treating an establishment job count as a count of people.
- Mixing SA and NSA, or comparing an NSA birth-death/benchmark figure to an SA change.
- Treating the latest month/quarter as final; ignoring annual benchmarks (they revise *years*, not
  just the newest point, and are not purely economic — they fold in classification/coverage).
- A units mismatch (thousands vs persons) read as a real divergence.
- Losing leading zeros on code columns; mixing `M13` annual into a monthly series, or `Q05` annual
  into a quarterly one.
- Filtering a quarterly file (BED, ECI, ECEC, QCEW wages) with a monthly `M01`–`M12` rule: it
  matches zero rows, so the series vanishes silently instead of raising.
- Treating a suppressed QCEW cell as zero, or expecting suppressed detail to sum to totals.
- Assuming a series ID's industry/geography from its label instead of decoding via mapping files.

## How the method skills use this

The methodology skills defer here for authoritative BLS facts rather than re-deriving them:
`explore-data` (profiling BLS microdata), `validate-data` (reconciliation, units, vintage gates),
`develop-testing-strategy` (vintage/as-of test invariants), `design-architecture` (vintage data-
model ADRs), and `bayesian-workflow` (nowcast inputs). When one of them needs a program specific,
it points to the relevant `references/<program>.md`.

## Reference files (load on demand)

| File | Program | Read it for |
|---|---|---|
| [references/qcew.md](references/qcew.md) | QCEW | The universe/frame; covered-jobs concept; AWW; suppression; downloadable files; the non-time-series cautions. |
| [references/ces.md](references/ces.md) | CES National | Payroll-jobs estimation; CEU/CES series IDs; net birth-death model; March benchmark; vintages. |
| [references/sae.md](references/sae.md) | CES State & Area | State/metro estimation; SAM Gen3 small-area model; benchmark windows; SA two-step; ETL schema. |
| [references/jolts.md](references/jolts.md) | JOLTS | Stock-vs-flow; rate denominators; 21-char series IDs; CES alignment; model-based state estimates. |
| [references/bed.md](references/bed.md) | BED/BDM | Job-flow definitions; 28-char series IDs; dynamic firm sizing; death lag; flat-file schema. |
| [references/oews.md](references/oews.md) | OEWS | Occupation×industry×geo scope limits; CES crosswalk; tidy schema; aggregation rules. |
| [references/eci.md](references/eci.md) | ECI | Fixed-weight Laspeyres index; ECI-vs-ECEC; reweighting; seasonality; constant-dollar. |
| [references/ecec.md](references/ecec.md) | ECEC | Cost-level concepts; benefit-cost-over-all-workers caveat; no state estimates; CPE bands. |
| [references/cps.md](references/cps.md) | CPS | Household concepts; labor-force classification logic; rates/denominators; weights; CPS-vs-CES. |

## Maintenance note

These references are point-in-time (2025–2026 vintage). BLS pages are living documents — current
release dates, latest benchmarks, net birth-death method, and sample sizes change. Each reference
lists its official source URLs; re-check them for anything recency-sensitive rather than trusting a
date quoted here.
