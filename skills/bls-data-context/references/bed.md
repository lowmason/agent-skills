# Business Employment Dynamics (BED/BDM)

## Source hierarchy

Use official BLS sources first. Treat current release dates, latest quarters, and file update dates as time-sensitive and re-check them when doing live analysis.

Primary Handbook of Methods sources:

- https://www.bls.gov/opub/hom/bdm/concepts.htm
- https://www.bls.gov/opub/hom/bdm/data.htm
- https://www.bls.gov/opub/hom/bdm/design.htm
- https://www.bls.gov/opub/hom/bdm/calculation.htm
- https://www.bls.gov/opub/hom/bdm/presentation.htm
- https://www.bls.gov/opub/hom/bdm/info.htm

Operational BLS sources useful for data work:

- BED/BDM home and latest release links: https://www.bls.gov/bdm/
- BDM databases page: https://www.bls.gov/bdm/data.htm
- BLS flat files directory: https://download.bls.gov/pub/time.series/bd/
- Flat-file documentation: https://download.bls.gov/pub/time.series/bd/bd.txt
- FAQ: https://www.bls.gov/bdm/bdmfaq.htm
- Data files and charts: https://www.bls.gov/bdm/charts.htm
- Establishment age and survival tables: https://www.bls.gov/bdm/bdmage.htm

Related source for an important naming pitfall:

- CES Net Birth-Death Model: https://www.bls.gov/web/empsit/cesbd.htm

## Naming conventions

The program name is **Business Employment Dynamics**, usually abbreviated **BED** in BLS explanatory text. BLS web navigation and some pages also use **BDM**. The public flat-file database abbreviation is **BD**, and the flat files live under `pub/time.series/bd/`.

Do not confuse BED establishment births/deaths with the **CES net birth-death model**. BED is QCEW-derived, administrative, quarterly, establishment-level job-flow data. The CES net birth-death model is a monthly model-based adjustment used in the sample-based Current Employment Statistics program.

## One-sentence mental model

BED tracks **private-sector establishment-level job flows** by longitudinally linking QCEW administrative records across quarters, then classifying each establishment's third-month employment change as an opening, expansion, contraction, closing, birth, or death.

## What BED measures

BED decomposes net employment change into gross job creation and destruction at the establishment level.

Core identities:

```text
gross_job_gains = openings + expansions
gross_job_losses = closings + contractions
net_employment_change = gross_job_gains - gross_job_losses
```

All employment-change measures are based on employment in the **third month of the previous quarter** versus employment in the **third month of the current quarter**. In practice, the quarter-end reference months are March, June, September, and December. QCEW employment is based on employment for the pay period including the 12th of the month.

Establishments with no employment change count in total employment denominators but do **not** contribute to gross job gain or gross job loss levels.

## Unit of observation

The core BED unit is the **establishment**, not the firm and not the individual worker.

An establishment is a business location and/or primary economic activity unit. A firm can contain one establishment or many establishments. BED's longitudinal establishment histories allow BLS to track whether a unit opens, closes, expands, contracts, survives, or dies.

BED also publishes firm-size tabulations, but those use special dynamic sizing methodology. Do not assume that firm-size BED is produced by naively assigning the entire quarterly job change to the firm's starting or ending size class.

## Source data and coverage

BED is derived from QCEW microdata. QCEW data come from employer reports required under state unemployment insurance laws and from Unemployment Compensation for Federal Employees reporting. Employers submit quarterly contribution reports with monthly employment and quarterly wages to state workforce agencies, which provide the administrative records used by BLS.

The QCEW source universe is very broad, roughly a near-census of UI-covered employment. However, published BED gross job flow estimates are narrower than all QCEW because BED is focused on private-sector longitudinal job flows.

Important exclusions and limits:

- BED gross job gains and losses exclude government employees.
- BED excludes private households and establishments with zero employment.
- Major UI-coverage exclusions include self-employed workers, religious organizations, most agricultural workers on small farms, Armed Forces members, elected officials in most states, most railroad employees, some domestic workers, many student workers at schools, and employees of certain nonprofit organizations.
- Puerto Rico and the Virgin Islands can appear in state/geography code mappings and release tables, but they are excluded from U.S. national totals.
- BED currently does not publish MSA-level or county-level time series in the public BD flat-file system; those codes are placeholders (`msa_code = 00000`, `county_code = 000`).
- BED is private-sector only in the flat-file ownership dimension (`ownership_code = 5`).

## BED versus nearby BLS programs

### BED versus QCEW

QCEW provides employment and wage levels by geography and detailed industry. BED uses QCEW establishment microdata but links establishments over time to measure job flows. BED excludes some QCEW scope, including government employees, private households, and zero-employment establishments. BED net change will not necessarily match QCEW employment change totals because the scope and construction differ.

### BED versus CES

CES is a monthly sample-based establishment survey used for timely payroll employment, hours, and earnings. BED is quarterly, administrative, and released with a longer lag. BED gross job flows and net changes should not be forced to match CES monthly employment changes because CES has different timing, coverage, estimation, and benchmarking procedures.

### BED versus JOLTS

JOLTS measures worker-flow concepts such as hires, separations, quits, layoffs/discharges, and job openings. BED measures **job flows at establishments**. BED does not observe internal churn that leaves an establishment's employment count unchanged. For example, if 10 workers leave and 10 workers are hired at the same establishment during the quarter, JOLTS can show flows, but BED may show zero net establishment employment change.

## Core BED data classes

| Code | Data class | Meaning |
|---:|---|---|
| `01` | Gross Job Gains | Sum of jobs gained at expanding and opening establishments |
| `02` | Expansions | Existing linked establishments with positive employment in both quarters and higher current-quarter employment |
| `03` | Openings | Establishments with positive current third-month employment and no prior-quarter link, or positive current employment after zero prior-quarter employment |
| `04` | Gross Job Losses | Sum of jobs lost at contracting and closing establishments |
| `05` | Contractions | Existing linked establishments with positive employment in both quarters and lower current-quarter employment |
| `06` | Closings | Establishments with positive previous third-month employment and no positive current-quarter employment or inactive status |
| `07` | Establishment Births | Subset of openings intended to remove reopenings and seasonal/temporary openings |
| `08` | Establishment Deaths | Subset of closings intended to remove temporary shutdowns |

## Definitions and interpretation details

### Openings

Openings are establishments with positive employment in the third month of the current quarter and either no link to the previous quarter or zero employment in the previous quarter. Openings include both true new establishments and some reopenings. Use births, not openings, when the research question requires a stricter new-establishment concept.

### Expansions

Expansions are linked establishments with positive employment in the third month of both the previous and current quarters and a net employment increase over that interval.

### Gross job gains

Gross job gains equal all jobs added at opening and expanding establishments. Gross job gains are not hires; they are net increases at establishment units.

### Closings

Closings are establishments with positive employment in the third month of the previous quarter and zero/no employment or inactive status in the current quarter. Closings include permanent deaths and temporary shutdowns.

### Contractions

Contractions are linked establishments with positive employment in the third month of both the previous and current quarters and a net employment decrease over that interval.

### Gross job losses

Gross job losses equal all jobs lost at closing and contracting establishments. Gross job losses are not separations; they are net decreases at establishment units.

### Births

Births are a subset of openings. A birth is an establishment with positive employment for the first time in the current quarter and no previous-quarter link, or an establishment with positive employment in the current quarter after zero employment in the third month of the previous four quarters. This definition is designed to remove seasonal reopenings and temporary openings.

### Deaths

Deaths are a subset of closings. BLS requires no employment or zero employment in the third month of **four consecutive quarters** after the last quarter with positive employment. Because BLS waits to distinguish permanent closings from temporary shutdowns, there is a three-quarter lag between a permanent closing and publication as an establishment death. In practice, death series can lag the latest gross-flow quarter; always inspect `bd.series` end dates or the latest news release.

## Establishment-linking methodology

BED depends on linking QCEW establishment records across quarters before classifying job flows.

Linking sequence:

1. Match establishments using their state workforce agency / SESA identifier.
2. Use predecessor-successor information supplied by states when IDs change because of ownership changes, restructuring, or UI account changes.
3. Use statistical/probability matching based on identifying information such as name, address, and phone number.
4. Use analyst review for unmatched or ambiguous records.

BLS reports that most continuing establishments, about 95 to 97 percent, are linked by the agency ID. The remaining cases are where predecessor/successor records, statistical matching, and analyst review are especially important.

Agent caution: administrative changes can create false openings/closings if a continuing establishment is not linked properly. BLS explicitly notes that linkage complications can overstate openings and closings while understating expansions and contractions.

## Industry classification

BED uses NAICS. Federal statistical agencies revise NAICS every five years. When doing long time-series analysis by industry, watch for NAICS revisions and BLS recoding.

Quality review and classification changes:

- State agencies verify establishment industry, location, and ownership information on a four-year cycle.
- Verification-related classification changes and changes from improved employer reporting are generally introduced with first-quarter data.
- Avoid interpreting first-quarter industry-level discontinuities as economic changes without checking for classification updates, administrative events, and footnotes.

## Seasonal adjustment

BED data are available seasonally adjusted and not seasonally adjusted.

Important details:

- Seasonal adjustment is the main estimation procedure applied to BED aggregated series; the underlying job-flow data are administrative, not sample estimates.
- BED uses X-13-ARIMA methods, and the Handbook describes use of the ARIMA `(0,1,1)(0,1,1)` “airline” model for quarterly BED series.
- Components are seasonally adjusted and then aggregated to preserve additivity.
- Gross job gains are indirectly seasonally adjusted by summing seasonally adjusted expansions and openings.
- Gross job losses are indirectly seasonally adjusted by summing seasonally adjusted contractions and closings.
- Seasonally adjusted net change is calculated as seasonally adjusted gross job gains minus seasonally adjusted gross job losses.
- Seasonal adjustment models are updated annually.

Use seasonally adjusted series for quarter-to-quarter macro interpretation. Use not seasonally adjusted series for raw administrative accounting, seasonal analysis, and any work where the seasonal pattern itself is meaningful.

## Rates

BED publishes levels and rates.

Employment-flow rates are symmetric growth rates:

```text
gross_job_gain_rate = gross_job_gain_level / average(employment_previous_quarter, employment_current_quarter)

gross_job_loss_rate = gross_job_loss_level / average(employment_previous_quarter, employment_current_quarter)

net_growth_rate = gross_job_gain_rate - gross_job_loss_rate
```

For establishment-count rates, the analogous denominator is based on establishment counts rather than employment. The flat-file documentation describes rate denominators as the average of current and prior quarter levels, either employment or establishment counts depending on the series.

Important interpretation:

- Rates are useful for comparing sectors, states, and time periods with different employment levels.
- Rates can be added and subtracted consistently because BED calculates component rates and sums them to gross totals.
- The denominator level itself is generally not the BED value; use QCEW or other BLS denominators if you need to reconstruct rates exactly.

## Dynamic sizing for firm-size data

BED firm-size data use **dynamic sizing** (also called momentary sizing). This is a major methodological feature.

Why it matters: estimates of job creation by firm size are highly sensitive to size-class methodology. Naively assigning all growth to a firm's initial size class or final size class can bias conclusions about small-business job creation.

Dynamic sizing approach:

- Firms are initially assigned to a size class based on previous-quarter employment.
- If the firm's employment change crosses size-class thresholds during the quarter, the change is allocated across the size classes where the growth or loss occurred.
- The method assumes continuous linear employment change from one quarter endpoint to the next.
- This provides symmetric estimates and reduces systematic effects from transitory movement across thresholds.

Example: if a firm grows from 3 employees to 13 employees, dynamic sizing allocates the first part of growth to the 1-4 size class, the next part to the 5-9 size class, and the remaining growth to the 10-19 size class, rather than putting all 10 jobs in only the starting or ending size class.

Agent rule: when interpreting firm-size BED, say “job gains/losses allocated dynamically across size classes,” not “all jobs created by firms that started the quarter in size class X.”

## Revisions and reliability

BED is based on administrative data and is not a sample survey, so published BED data are not subject to sampling error. They are still subject to nonsampling error and revisions.

Sources of nonsampling error include:

- corrected employer reports received after initial processing;
- typographical or reporting errors;
- establishment classification changes;
- predecessor/successor updates;
- linkage complications;
- seasonal adjustment revisions.

Revision pattern:

- BED data are revised annually with the release of first-quarter data.
- Annual revisions cover the last four quarters of not seasonally adjusted data and five years of seasonally adjusted data.
- BLS may also revise because of corrections to QCEW records and updated predecessor-successor information.
- Preserve footnote codes in any derived dataset because BLS uses them for special situations such as administrative events.

The Handbook reports very high QCEW coverage due to mandatory UI reporting and substantial enforcement. It also describes employment imputation as very low. Still, do not present BED as error-free; present it as administrative near-census data with nonsampling and linkage risks.

## Release timing and availability

BED is published quarterly, with a substantial lag after the reference quarter. BLS Handbook presentation text describes publication approximately seven months after the reference period; flat-file documentation says about six months. Treat the practical rule as **about 6-7 months after quarter end** and verify the actual schedule on the BLS release calendar or BDM home page.

Data begin in 1992 for the main quarterly gross job gain/loss series. Use `bd.series` begin and end fields for exact availability by series, because not all published series have the same start/end dates.

BED data products include:

- national private-sector gross job gains and losses;
- national industry data by NAICS sector and subsector;
- state gross job gain/loss data by NAICS sector;
- firm-size data;
- data by size of establishment employment change;
- establishment births and deaths;
- establishment age and survival data;
- annual data products.

The public flat-file time-series system is not the only BED output. Establishment age/survival and some research-style tables are available through BLS data files/charts pages.

## Public flat-file system

Canonical directory:

```text
https://download.bls.gov/pub/time.series/bd/
```

Key files:

| File | Purpose |
|---|---|
| `bd.txt` | Database documentation and file-layout descriptions |
| `bd.series` | Series metadata, component codes, titles, begin/end dates |
| `bd.data.0.Current` | Current-year-to-date observations |
| `bd.data.1.AllItems` | Full public history |
| `bd.dataclass` | Data class lookup |
| `bd.dataelement` | Data element lookup |
| `bd.industry` | Industry lookup |
| `bd.state` | State/geography lookup |
| `bd.sizeclass` | Firm size / size-of-change lookup |
| `bd.ratelevel` | Level/rate lookup |
| `bd.periodicity` | Annual/quarterly lookup |
| `bd.seasonal` | Seasonal adjustment lookup |
| `bd.ownership` | Ownership lookup |
| `bd.unitanalysis` | Unit-of-analysis lookup |
| `bd.footnote` | Footnote lookup |
| `bd.msa`, `bd.county` | Placeholder geography lookup files in current public BED time series |

### Data file columns

The data files contain:

| Column | Meaning |
|---|---|
| `series_id` | BLS time-series identifier |
| `year` | Observation year |
| `period` | Quarter or annual period code |
| `value` | Numeric value; jobs, establishment counts, or rates depending on series |
| `footnote_codes` | Optional BLS footnote codes |

### Series file columns

The series file contains:

| Column | Meaning |
|---|---|
| `series_id` | BLS time-series identifier |
| `seasonal` | `S` or `U` |
| `msa_code` | currently `00000` for public BED time series |
| `state_code` | `00` for U.S. totals, FIPS-style state codes, plus PR/VI codes |
| `county_code` | currently `000` for public BED time series |
| `industry_code` | BLS BED industry code |
| `unitanalysis_code` | currently code `1` |
| `dataelement_code` | employment vs number of establishments |
| `sizeclass_code` | all sizes, firm size, or size-of-change class |
| `dataclass_code` | gross gains, expansions, openings, gross losses, contractions, closings, births, deaths |
| `ratelevel_code` | level or rate |
| `periodicity_code` | quarterly or annual |
| `ownership_code` | private sector |
| `series_title` | human-readable title |
| `footnote_codes` | optional series-level notes |
| `begin_year`, `begin_period` | first observation |
| `end_year`, `end_period` | latest observation |

### Series ID anatomy

A BED series ID has a fixed logical structure. The meaningful portion is 28 characters; the `bd.series` field is length 30 with trailing blanks in the documentation.

Example:

```text
BDS0000006000200090110004LQ5
```

Breakout:

| Positions | Component | Example | Meaning |
|---:|---|---|---|
| 1-2 | database abbreviation | `BD` | Business Employment Dynamics flat-file database |
| 3 | seasonal | `S` | seasonally adjusted |
| 4-8 | MSA code | `00000` | national / no MSA detail |
| 9-10 | state code | `06` | California |
| 11-13 | county code | `000` | no county detail |
| 14-19 | industry code | `200090` | Leisure and hospitality |
| 20 | unit analysis | `1` | establishment code in mapping |
| 21 | data element | `1` | employment |
| 22-23 | size class | `00` | all size classes |
| 24-25 | data class | `04` | gross job losses |
| 26 | rate/level | `L` | level |
| 27 | periodicity | `Q` | quarterly |
| 28 | ownership | `5` | private sector |

### Core lookup codes

Seasonal:

| Code | Meaning |
|---|---|
| `S` | Seasonally adjusted |
| `U` | Not seasonally adjusted |

Data element:

| Code | Meaning |
|---|---|
| `1` | Employment |
| `2` | Number of establishments |

Rate/level:

| Code | Meaning |
|---|---|
| `L` | Level |
| `R` | Rate |

Periodicity:

| Code | Meaning |
|---|---|
| `Q` | Quarterly |
| `A` | Annual |

Ownership:

| Code | Meaning |
|---|---|
| `5` | Private Sector |

Unit analysis:

| Code | Meaning |
|---|---|
| `1` | Establishment |

Size class:

| Code | Meaning |
|---|---|
| `00` | All size classes |
| `01` | 1 to 4 employees |
| `02` | 5 to 9 employees |
| `03` | 10 to 19 employees |
| `04` | 20 to 49 employees |
| `05` | 50 to 99 employees |
| `06` | 100 to 249 employees |
| `07` | 250 to 499 employees |
| `08` | 500 to 999 employees |
| `09` | 1,000 or more employees |
| `10`-`28` | Detailed establishment size-of-employment-change classes |
| `31` | 1 to 4 jobs |
| `32` | 5 to 19 jobs |
| `33` | 20 or more jobs |

Data class:

| Code | Meaning |
|---|---|
| `01` | Gross Job Gains |
| `02` | Expansions |
| `03` | Openings |
| `04` | Gross Job Losses |
| `05` | Contractions |
| `06` | Closings |
| `07` | Establishment Births |
| `08` | Establishment Deaths |

Footnotes:

| Code | Meaning |
|---|---|
| `1` | Total private includes unclassified sector not shown separately |
| `2` | Administrative event occurred during the quarter |

Geography:

- `state_code = 00` means U.S. totals.
- State codes are FIPS-style codes for the 50 states and District of Columbia, with `72` for Puerto Rico and `78` for Virgin Islands.
- `county_code = 000` and `msa_code = 00000` are placeholders in the current public BED flat-file system.

Industry:

- `000000` = Total private.
- `100000` = Goods-producing.
- `200000` = Service-providing.
- National 3-digit NAICS industry codes are represented as `300` + the 3-digit NAICS code, e.g. `300721` = Accommodation.
- State data are available at broader NAICS sector detail than national 3-digit subsector data. Use `bd.industry` and `bd.series` rather than hard-coding assumptions.

## Agent workflow for data retrieval

1. **Clarify the concept**: gross gains, openings, expansions, gross losses, closings, contractions, births, deaths, net, rate, level, employment, or establishment count.
2. **Clarify adjustment**: seasonally adjusted (`S`) or not seasonally adjusted (`U`).
3. **Clarify geography**: U.S. total (`00`) or state code. Do not assume MSA/county availability.
4. **Clarify industry**: total private, goods-producing, service-providing, NAICS sector, or national 3-digit subsector.
5. **Clarify size dimension**: all size classes, firm size class, or establishment size-of-change class.
6. **Use `bd.series` to select series IDs** rather than constructing IDs blindly.
7. **Join observations from `bd.data.*` to metadata and lookup tables**.
8. **Run identity checks**:
   - gross job gains = openings + expansions;
   - gross job losses = closings + contractions;
   - net = gross job gains - gross job losses;
   - seasonally adjusted additivity should hold after allowing for rounding;
   - births are a subset of openings;
   - deaths are a subset of closings, but lagged.
9. **Preserve footnotes** and surface administrative-event notes in downstream outputs.
10. **Check `end_year` and `end_period`** for each series; do not assume all series are current through the same quarter.

## Polars-oriented ingestion notes

When implementing a downloader/loader, prefer flat files over repeated API calls for full-history work.

Practical notes:

- Download the raw files from `https://download.bls.gov/pub/time.series/bd/`.
- Do not parse the web-rendered view of the files; it may wrap rows and remove useful delimiters.
- The documentation describes data files as ASCII text with headers and mapping files as tab-separated text. Inspect each raw file and use a delimiter strategy that matches the downloaded bytes.
- Preserve code columns as strings, including leading zeroes (`state_code`, `industry_code`, `sizeclass_code`, etc.).
- Treat `value` as decimal/float until after filtering by `ratelevel_code` and `dataelement_code`; levels are counts, but rates may be decimal values.
- Use lazy scans where possible for large full-history files.
- Recommended normalized tables:
  - `bd_observations(series_id, year, period, value, footnote_codes)`
  - `bd_series(series_id, seasonal, state_code, industry_code, dataelement_code, sizeclass_code, dataclass_code, ratelevel_code, periodicity_code, ownership_code, series_title, begin_year, begin_period, end_year, end_period, ...)`
  - lookup tables for dimensions
  - derived calendar table mapping `period` to quarter-end month and date.

## Common analytical pitfalls

### Mistaking job flows for worker flows

BED job gains/losses are establishment net changes. They do not count all hires and separations. Use JOLTS for worker-flow concepts.

### Comparing BED net change directly to CES or QCEW

BED net change is useful, but it has different scope and construction than CES or QCEW. Explain differences rather than forcing reconciliation.

### Treating openings as births

Births are a stricter subset of openings. Openings can include reopenings after zero prior-quarter employment. Use births for entrepreneurship/new-establishment analysis.

### Ignoring the death lag

Deaths require four consecutive quarters without positive employment after the last positive quarter. Do not compare same-quarter births and deaths without acknowledging the lag and publication timing.

### Ignoring linkage problems

Administrative ID changes can cause false openings/closings. At turning points, mergers, restructurings, and UI-account changes can matter.

### Naive firm-size interpretation

Firm-size series use dynamic sizing. Never attribute all growth/loss to the firm's beginning or ending size class.

### Forgetting geography restrictions

The BD flat files use state-level and national geography, not county or MSA time series. `bd.county` and `bd.msa` contain placeholder national codes.

### Losing leading zeroes

Most BED dimensions are codes, not numeric quantities. Read and store them as strings.

### Ignoring annual revisions

Annual revisions can affect recent not seasonally adjusted data and several years of seasonally adjusted data. Reproducible pipelines should version downloads and record file timestamps.

### Ignoring NAICS revisions and Q1 recoding

Industry classification updates can enter in first-quarter data. Long industry histories require caution around NAICS revisions and recoding cycles.

## Good language for reports

Use:

- “Gross job gains from opening and expanding private-sector establishments...”
- “Gross job losses from closing and contracting private-sector establishments...”
- “From the third month of one quarter to the third month of the next...”
- “BED measures job flows at establishments, not hires and separations.”
- “Births are a subset of openings; deaths are a subset of closings.”
- “Firm-size estimates use dynamic sizing, allocating growth or loss across size classes as thresholds are crossed.”

Avoid:

- “Businesses hired X workers” when using BED gross job gains.
- “Workers lost jobs” when the measure is gross job losses at establishments.
- “New firms” when the series is openings or establishment births.
- “BED survey estimates” because BED is administrative/QCEW-derived, not a sample survey.
- “Small firms created all these jobs” without noting dynamic sizing.

## Quick examples of series-selection logic

### U.S. total private gross job gains, seasonally adjusted, level, quarterly

Use:

- `seasonal = S`
- `state_code = 00`
- `county_code = 000`
- `msa_code = 00000`
- `industry_code = 000000`
- `dataelement_code = 1`
- `sizeclass_code = 00`
- `dataclass_code = 01`
- `ratelevel_code = L`
- `periodicity_code = Q`
- `ownership_code = 5`

### U.S. total private number of establishments gaining jobs

Use the same filters as gross job gains, but `dataelement_code = 2`. Confirm the exact `series_title` in `bd.series`.

### Gross job loss rate by state

Use:

- `dataclass_code = 04`
- `ratelevel_code = R`
- `state_code` for the desired state
- likely `industry_code = 000000` for total private unless the user asks for sector
- `seasonal = S` for quarter-to-quarter macro comparison or `U` for raw data.

### Establishment births

Use:

- `dataclass_code = 07`
- choose `dataelement_code = 1` for employment associated with births or `2` for number of establishments
- remember births are a subset of openings and are designed to exclude temporary/seasonal reopenings.

### Firm-size job gains

Use:

- `sizeclass_code` in `01`-`09`
- `dataclass_code = 01`, `02`, or `03` depending on gross gains, expansions, or openings
- cite dynamic sizing in any interpretation.

## Recommended metadata to store with derived datasets

For reproducibility, store:

- download timestamp;
- source file URL;
- source file last-modified timestamp if available from HTTP headers;
- BLS release quarter;
- whether observations are seasonally adjusted;
- annual revision vintage if known;
- `series_id`;
- full `series_title`;
- all decoded dimensions;
- original `footnote_codes`;
- parser version and transformation code version.

## Minimal BED checklist before publishing an answer

Before giving a BED-based answer, verify:

- The statistic is a BED statistic, not CES/JOLTS/QCEW.
- The user asked for jobs, establishments, rates, or net change, and the chosen data element matches.
- The seasonality choice is explicit.
- The geography and industry are supported by BED public data.
- The latest quarter is verified from BLS if recency matters.
- Births/deaths lag is acknowledged where relevant.
- Firm-size estimates mention dynamic sizing.
- Any revision-sensitive claims note that BED data revise annually.
