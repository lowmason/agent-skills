# CES State and Area (SAE) Estimates

Use this file as project knowledge for answering questions, designing ETL pipelines, interpreting series, explaining revisions, and documenting methods for BLS Current Employment Statistics State and Area estimates. It is written for an AI agent that needs to reason about how SAE estimates are constructed, what they measure, how they revise, and how they differ from adjacent BLS programs such as CES National, QCEW, LAUS, and JOLTS.

The most compact mental model is:

> CES-SA is a monthly establishment survey estimate of nonfarm payroll jobs, hours, and earnings for states and metropolitan areas. Monthly estimates are produced from edited payroll reports using matched-sample link relatives, birth/death modeling, small-area modeling where sample is thin, and annual benchmarking to QCEW universe counts plus noncovered employment. Selected employment series are seasonally adjusted with X-13ARIMA-SEATS and revised with the annual benchmark.

## 1. Canonical source set

| Source key | URL | Use when the agent needs... |
|---|---|---|
| `BLS-SAE-CONCEPTS` | https://www.bls.gov/opub/hom/sae/concepts.htm | Scope, geography, industry classification, units of observation, reference period, employment/hours/earnings definitions, diffusion indexes. |
| `BLS-SAE-DATA` | https://www.bls.gov/opub/hom/sae/data.htm | Collection methods, sample enrollment schedule, respondent reporting, microdata editing/screening, confidentiality rules. |
| `BLS-SAE-DESIGN` | https://www.bls.gov/opub/hom/sae/design.htm | Sampling frame, sample design, strata, weights, sample updates, coverage, government sample treatment. |
| `BLS-SAE-CALCULATION` | https://www.bls.gov/opub/hom/sae/calculation.htm | Estimators, matched sample, robust weighted link relatives, small-area models, birth/death model, aggregation, benchmarking, seasonal adjustment, reliability. |
| `BLS-SAE-PRESENTATION` | https://www.bls.gov/opub/hom/sae/presentation.htm | Release schedule, publication products, data access, uses, corrections, confidentiality presentation. |
| `BLS-SAE-BENCHMARK-2025` | https://www.bls.gov/web/laus/benchmark.htm | Current benchmark article and technical notes for the 2025 benchmark, released with January 2026 SAE data in April 2026. Use for current benchmark-revision facts, discontinued series, and benchmark-specific exceptions. |
| `BLS-SAE-SEASONAL` | https://www.bls.gov/sae/seasonal-adjustment/ | Dedicated seasonal adjustment explanation: two-step method, concurrent adjustment, variable survey interval adjustment, outliers, prior adjustments, and published SA series. |
| `BLS-SAE-MSA-DEFS` | https://www.bls.gov/sae/additional-resources/metropolitan-statistical-area-definitions.htm | Which OMB bulletin CES uses now (23-01) and the list of previous bulletins it used (18-03, 17-01, 15-01, 13-01, 10-02). |
| `BLS-SAE-NOTICE-MSA-2024` | https://www.bls.gov/sae/notices/2024/upcoming-changes-to-metropolitan-statistical-area-delineations.htm | Notice that MSA estimates switch to the 2020 Census-based delineations with January 2025 data in March 2025 and that NECTAs are discontinued. |
| `BLS-SAE-BENCHMARK-2024` | 2024 benchmark article, "Revisions in State Establishment-based Employment Estimates Effective January 2025" (PDF `archives/annual-benchmark-article-2025.pdf` under `BLS-SAE-BENCHMARK-ARCHIVE`) | "Special notice regarding changes to statistical area delineations": counts of areas added, changed, and dropped; the reconstruction method; the prior bulletin (18-03). |
| `BLS-SAE-BENCHMARK-ARCHIVE` | https://www.bls.gov/sae/publications/benchmark-article/ | Every benchmark article since 2002, PDFs named by publication year (`archives/annual-benchmark-article-<year>.pdf`); the 2015, 2017, and 2019 articles document the 13-01, 15-01, and 17-01/18-03 adoptions. The PDFs prompt a download in a browser and bls.gov refuses scripted fetches; the Wayback Machine holds copies that `curl` can read. |
| `BLS-MSA-REDELINEATION-PLANS` | https://www.bls.gov/bls/msa-redelineation-announcement.htm | Cross-program statement that CES, LAUS, OEWS, and QCEW would not adopt Bulletin 18-04 or any later 2010-based update. |
| `BLS-LAUS-AREAS` | https://www.bls.gov/lau/lausmsa.htm | LAUS adoption dates for every bulletin (13-01 March 2015; 15-01 March 2017; 17-01 and 18-03 March 2019; 23-01 on 2025-03-17) and the labor-market-area concept. |

When answering public-facing questions, cite the BLS source page closest to the claim. Use `BLS-SAE-CALCULATION` for formulas and revision mechanics, `BLS-SAE-DESIGN` for sample design, `BLS-SAE-DATA` for collection/editing, and `BLS-SAE-BENCHMARK-2025` for the most recent benchmark-specific facts.

## 2. What CES State and Area estimates measure

### Program scope

CES State and Area is the state and local component of the Current Employment Statistics program. It produces monthly estimates for employment, hours, and earnings of workers on nonfarm payrolls, by industry, for:

- all 50 states,
- the District of Columbia,
- Puerto Rico,
- the U.S. Virgin Islands,
- New York City, and
- about 430 metropolitan statistical areas and metropolitan divisions.

BLS derives SAE estimates from payroll data collected through the CES survey. The survey sample is drawn from a frame based primarily on unemployment insurance (UI) tax records through the QCEW/LDB system, and it includes private and government establishments.

### Not a household survey

CES-SA measures payroll jobs at establishments, not people. A person with two payroll jobs can be counted twice. A person without a payroll job is not counted. Do not use CES-SA as a measure of unemployment, labor force participation, household employment, or number of employed persons. Those concepts belong primarily to LAUS/CPS-style household measures.

### Nonfarm payroll scope

The program covers wage and salary jobs in nonfarm industries. It excludes categories such as the self-employed, unpaid family workers, most agricultural workers, private household workers, and military personnel. It includes many types of employees who are on nonfarm payrolls during the reference period, subject to BLS scope rules.

### Industry classification

SAE estimates use the 2022 North American Industry Classification System (NAICS). Establishments are classified by primary economic activity. For publication and estimation, BLS sometimes combines NAICS industries into CES industry codes to support publication quality, confidentiality, or continuity.

Agent guidance:

- Do not assume a CES industry code is exactly one NAICS industry.
- Check the BLS industry mapping or metadata when joining to NAICS-based sources.
- Be alert for NAICS revisions, OMB area-definition updates, and benchmark history reconstructions that can change comparability.

### Geography

SAE uses state and metropolitan area geographies. Metropolitan areas follow Office of Management and Budget (OMB) delineations, which SAE adopts on its own schedule — with an annual benchmark, not on the bulletin's issue date. SAE adopted the 2020 Census-based delineations (OMB Bulletin 23-01) with the release of January 2025 estimates on March 17, 2025, as part of the 2024 benchmark; the full history is in "OMB delineation adoption" below. Agents should treat area definitions as vintage-sensitive metadata, especially for long historical comparisons.

Agent guidance:

- Do not assume a metropolitan area lies wholly within one state. Some MSAs cross state boundaries.
- Do not add MSA estimates together to produce a state estimate unless the requested concept explicitly permits that aggregation and the geography is non-overlapping.
- Use published state estimates for states and published MSA estimates for metropolitan areas.
- For current production work, store area-code and area-name metadata with a geography-definition vintage.

### OMB delineation adoption

SAE — and LAUS, which shares the State Employment and Unemployment release and has no separate reference in this skill — adopt a new OMB bulletin with the annual benchmark released in March, never on the bulletin's issue date. Naming key: "benchmark year N" is released with January N+1 data in March N+1, so the 2024 benchmark is a March 2025 event. Adoption by bulletin, with the BLS source for each row:

| OMB bulletin (issued) | SAE adoption | LAUS adoption | What changed for SAE | Source |
|---|---|---|---|---|
| 13-01 (2013-02-28; 2010 Census standards) | 2014 benchmark, released with January 2015 data in March 2015. Prior definitions: the December 2009 delineations (OMB Bulletin 10-02). | March 2015 | 373 MSAs, 28 metropolitan divisions, 21 NECTAs, 11 nonstandard areas; 82 MSAs changed composition. AE and non-AE histories were **reconstructed back to 1990** from QCEW/LDB microdata, so published series did not break. | `BLS-SAE-BENCHMARK-ARCHIVE`, article effective January 2015, "Special notice regarding changes to statistical area delineations" |
| 15-01 (2015-07-15) | 2016 benchmark, released with January 2017 data in March 2017. | March 2017 | Enid, OK (FIPS 21420) added as an MSA (formerly micropolitan); Macon, GA retitled Macon-Bibb County, GA (title only). Bulletin attribution is **inferred**: the article names the changes rather than the bulletin, but they are exactly 15-01's metropolitan changes, and `BLS-SAE-MSA-DEFS` lists 15-01 among the bulletins used. | `BLS-SAE-BENCHMARK-ARCHIVE`, article effective January 2017, "MSA updates" |
| 17-01 (2017-08-15), as updated by 18-03 (2018-04-10) | 2018 benchmark, released with January 2019 data in March 2019. | March 2019 (LAUS names both bulletins) | Twin Falls, ID added as an MSA (formerly micropolitan; the only metropolitan change in 17-01). 18-03 added one micropolitan area, so it changed nothing SAE publishes, but BLS describes pre-2024 CES definitions as "derived from the delineations in OMB Bulletin 18-03". | `BLS-SAE-BENCHMARK-ARCHIVE`, article effective January 2019, "Metropolitan statistical area (MSA) updates"; `BLS-SAE-BENCHMARK-2024` |
| 18-04 (2018-09-14), 20-01 (2020-03-06) | **Never adopted.** | Never adopted | BLS announced that the federal-state programs (CES State and Area, LAUS, OEWS, QCEW) would not adopt 18-04 or any later update to the 2010-based delineations, citing workload and comparability costs. | `BLS-MSA-REDELINEATION-PLANS` |
| 23-01 (2023-07-21; 2020 Census standards) | 2024 benchmark, released with January 2025 data on 2025-03-17. | 2025-03-17; LAUS reconstructed labor force and unemployment back to series beginnings (generally January 1990) | 393 MSAs (80 changed composition, 3 renamed with new FIPS codes, 27 new, 12 dropped); 37 metropolitan divisions (11 new, 2 dropped); all 21 NECTAs and 10 NECTA divisions dropped, replaced in New England by 17 county-based MSAs and 3 divisions; nonstandard areas cut to New York City only. Connecticut coded by its nine planning regions. AE histories again **reconstructed back to 1990** (hours and earnings for new areas from 2011); eight areas stayed NSA-only until the 2025 benchmark, from which every metropolitan area is seasonally adjusted. | `BLS-SAE-NOTICE-MSA-2024`; `BLS-SAE-BENCHMARK-2024`; `BLS-LAUS-AREAS`; `BLS-SAE-BENCHMARK-2025` (seasonal-adjustment follow-up) |

Consequences for agents:

- **An SAE metro series does not break at an adoption date.** BLS restates the whole history on the new delineation, so the discontinuity is *between vintages* (data downloaded before vs. after the benchmark), not inside a series. Pre- and post-adoption downloads of the same `area_code` are different geographies; store the delineation vintage with the data and never splice them.
- QCEW is the opposite: it does **not** re-tabulate history (references/qcew.md, "OMB delineation adoption"), so a QCEW MSA series breaks at the reference year of adoption. Reconcile SAE to QCEW across an adoption boundary on a common county list, not on the MSA code.
- NECTA-based New England series (vintages before March 2025) and the county-based MSAs that replaced them are different areas with different codes, not one series with a new label.
- Which counties belong to which CBSA under each bulletin is the `geographic-codes` skill's job; this reference records only *when each program switched*.

## 3. Core units and data concepts

### Establishment and reference period

The basic reporting unit is the establishment: an economic unit, such as a factory, office, store, or mine, that produces goods or services at a single physical location and is engaged in one primary activity. A multi-location firm can have many establishments.

The CES reference period is the pay period that includes the 12th day of the month. Respondents report employment, payroll, and paid hours for that pay period.

### Key data types

| Data type | Meaning | Agent interpretation cautions |
|---|---|---|
| `AE` / all employees | All persons on establishment payrolls who received pay for any part of the pay period including the 12th. | This is jobs, not unique people. It includes full-time and part-time payroll jobs. |
| `PE` / production and nonsupervisory employees | Production employees in goods-producing industries and nonsupervisory employees in service-providing industries. | PE is a subset concept. Do not compare PE directly with AE without noting scope. |
| Aggregate weekly hours | Total paid hours for the reference pay period, converted to a weekly basis and aggregated. | Paid hours are not the same as hours worked. Paid leave can be included. |
| Aggregate weekly payrolls | Total payroll for the reference pay period, converted to a weekly basis and aggregated. | Payroll includes gross pay for the pay period; it is not employer compensation cost and excludes benefits. |
| `AWH` / average weekly hours | Aggregate weekly hours divided by employment for the relevant employee group. | AWH can change because of hours changes or employment-composition changes. |
| `AHE` / average hourly earnings | Aggregate payroll divided by aggregate hours. | AHE is an average, not a wage-rate series. Industry and occupational mix can affect it. |
| `AWE` / average weekly earnings | AWH multiplied by AHE. | AWE inherits both hours and earnings composition effects. |
| Diffusion index | Breadth measure of employment change across component areas or industries. | Values above 50 indicate more components increasing than decreasing; 50 is the neutral reference. |

CES-SA does not use all CES-N concepts for publication. In particular, women-worker and overtime concepts are not generally used by CES-SA even though some payroll variables can appear in data-screening contexts.

## 4. Collection, reporting, and microdata editing

### Data collection

BLS collects monthly employment, payroll, and paid-hours data from establishments. Participation is voluntary under federal law, but some states or territories can require reporting under state law. Respondents report through several modes, including:

- web collection,
- Computer-Assisted Telephone Interviewing (CATI),
- Data Collection Centers,
- Electronic Data Interchange (EDI) for large multi-establishment reporters, and
- a small number of legacy/nonstandard reporting modes.

Large firms and government agencies often report many worksites through EDI. An EDI file can cover dozens, hundreds, or thousands of worksites.

### Sample enrollment and rotation by industry group

After sample units are selected from UI/LDB records, BLS enrolls them. The annual sample update is phased into estimates by quarter and industry group. The BLS data-source page describes the following schedule:

| Group | Broad industry group | Enrollment quarter | First estimates using enrolled units |
|---|---|---:|---:|
| Group 1 | Mining and logging; wholesale trade; retail trade; transportation and warehousing; utilities; financial activities | Q1 | April |
| Group 2 | Construction; leisure and hospitality | Q2 | July |
| Group 3 | Information; professional and business services; other services | Q3 | October |
| Group 4 | Manufacturing; education and health services | Q4 | January |

Birth units identified from later LDB updates can be introduced with the relevant sample update. Agents should expect sample composition to evolve over the year.

### Microdata editing and screening

BLS edits all reported data before estimation. Edits check whether the data are correctly reported and whether they are consistent with the establishment's earlier reports. Questionable reports can lead to respondent follow-up, correction, analyst review, or exclusion from current-month estimation.

Important details for agents:

- Screening is primarily respondent-specific: tests compare a respondent's current data with that respondent's historical data.
- Payroll, commissions, and hours are normalized to weekly equivalents based on the respondent's pay-period length.
- Derived variables such as respondent-level AHE can be created from reported payroll and hours.
- Analyst review can accept a report as valid, exclude it from estimation, or request clarification/correction.
- Microdata can be treated as atypical or downweighted in estimation even if the establishment reported correctly, because the goal is to estimate population change without letting isolated events distort an estimating cell.

### Confidentiality and disclosure controls

BLS requires published estimates to meet statistical quality and confidentiality standards. Estimates are reviewed for sample adequacy, response, and potential dominance by a few reporters. Disclosure tests themselves are confidential. If a series fails standards, BLS may model it, remove it, or avoid publication.

Agent guidance:

- Do not infer confidential microdata from published estimates.
- Do not claim to know disclosure thresholds unless BLS publishes them.
- If a detailed SAE series disappears or is discontinued, check the latest benchmark article or special notices for low sample, coverage, or confidentiality explanations.

## 5. Sampling frame and sample design

### Frame: QCEW/LDB based

The CES sampling frame is the BLS Longitudinal Database (LDB), built from QCEW unemployment-insurance records. The UI/QCEW frame covers most CES-scope payroll employment, roughly 97 percent. Remaining CES-scope employment not covered by UI records is handled through noncovered employment adjustments.

The LDB tracks UI accounts and reporting units/worksites over time. It provides employer identifiers, industry, geography, size, and other administrative information used for sample selection.

### Private-sector sample

The private-sector CES sample is a stratified simple random sample of worksites, clustered by UI account number. Strata are defined by:

- state,
- industry, and
- employment size.

For private establishments, BLS describes 13 broad industry strata and 8 size classes, producing 104 allocation cells per state before other implicit sorting. Size classes range from 0-9 employees to 1,000 or more employees.

The sample is state-based. The design gives top priority to minimizing sampling error for statewide total nonfarm employment. This design choice matters: a detailed industry estimate in a small area can be less sample-supported than total nonfarm for a state.

### Optimum allocation and weights

BLS uses optimum allocation, specifically a Neyman-style allocation, to distribute a fixed sample across strata in a way that reduces variance for the primary estimate of interest. The primary design target is state total nonfarm employment.

Once selected, each sampled unit receives a selection weight approximately equal to the inverse probability of selection. Larger firms are sampled at higher rates, but weights are designed so that firms are represented according to their selection probabilities.

### Certainty units

Some units are always asked to participate and receive weight 1, representing only themselves. BLS lists certainty cases including:

- UI accounts in the largest size class,
- UI accounts that were in the largest class and later declined into the next-largest class,
- units reporting through EDI, and
- noncovered employment units not under the UI system.

### Government sample

The government sample is not part of the same probability-based private-sector design. BLS obtains high universe coverage for many government agencies, including full payroll counts in many cases. Government estimates are then summed with private estimates to produce total nonfarm estimates.

Agent guidance:

- Do not assume private and government sectors have identical sampling mechanics.
- Government estimates can be high-coverage administrative-style estimates, while private estimates rely more on probability sampling and modeling.

### Sample updates and overlap

Because businesses open and close continuously, BLS updates the sample annually. A sample update is performed using prior-year third-quarter LDB data, with information updates for establishments selected in sample updates. BLS also draws from first-quarter LDB data when available and adds a birth update from third-quarter LDB data. BLS notes that about two-thirds of the private sample overlaps from one sample to the next.

### Implicit metropolitan representation

Within allocation cells, units are grouped by MSA and sorted by number of UI accounts. The sampling rate is uniform within the allocation cell, and this sorting creates implicit stratification by MSA so that a proportional number of units are sampled from each MSA.

## 6. Estimation cells and matched samples

### Estimation cells

SAE estimates are produced for state-area-industry cells. The level of industry detail varies by area and data type. Large states or large metropolitan areas can support more detailed cells; small areas or detailed industries often require aggregation or modeling.

BLS distinguishes between different cell types, including basic cells, summary cells, independent basic cells, and independent summary cells. Aggregate cells are generally created by summing or aggregating lower-level components, but some cells can be independently estimated when needed.

### Matched sample concept

Monthly CES estimation relies heavily on the matched sample: establishments that reported usable data for both the current and previous month. For all-employee estimation, a report generally must have AE data for both months to enter the matched sample.

Important matched-sample exclusions:

- Reports with zero employment because the business has closed are excluded from the matched sample.
- Nonrespondents are excluded from the matched sample.
- Excluding deaths and nonrespondents is part of the logic that lets continuing sampled firms represent over-the-month change among continuing businesses, while birth/death modeling handles establishment openings and closings not captured directly by the matched sample.

## 7. Monthly all-employee (`AE`) estimation

### Basic formula

For many cells with adequate sample, all-employee employment is estimated with a weighted link-relative approach plus a net birth/death component:

```text
AE_hat[t] = AE_hat[t-1] * L[t] + BD[t]
```

where:

- `AE_hat[t]` is the current-month all-employee estimate,
- `AE_hat[t-1]` is the previous-month estimate,
- `L[t]` is the weighted matched-sample link relative from current to prior month, and
- `BD[t]` is the modeled net birth/death component.

Conceptually:

```text
L[t] = weighted current-month matched-sample AE / weighted prior-month matched-sample AE
```

BLS uses robust procedures rather than a naive ratio when influential reports could distort the estimate.

### Robust weighted link-relative estimator

The robust weighted link-relative estimator is used when the cell has enough sample. BLS describes adequacy conditions based on disclosure and either response-count/coverage standards. The robust procedure identifies atypical and influential reports and reduces their effect while controlling bias.

BLS may classify a report as atypical because:

- the establishment experienced an unusual movement not representative of the cell,
- the report is associated with strikes or special events,
- the unit is a key nonrespondent that must be imputed,
- analyst review determines that the report should not drive the cell estimate, or
- robust influence diagnostics indicate the report would have an excessive effect.

Atypical reports can be excluded from the link-relative change or downweighted for current estimation. This does not necessarily mean the establishment report was wrong. It often means the report is real but not representative of the broader population movement the cell is intended to estimate.

### Large events outside the matched sample

BLS and State Workforce Agencies investigate large public events outside the matched sample, such as large business births, deaths, or strikes. When a large event is not captured in sample reports, BLS can adjust the estimate, but only for the part not already captured by responding sample units.

### Key nonrespondents

For important nonresponding units, BLS can impute values using information such as:

- the prior month CES value multiplied by the prior-year QCEW relative change,
- QCEW levels where available, or
- prior-year CES data for some education cases.

Key nonrespondent imputations are generally treated as atypical so they do not drive the matched-sample link relative as though they were direct respondent observations.

## 8. Small Area Model (`SAM Gen3`)

When a cell lacks adequate sample for robust direct estimation, BLS uses small-area modeling. The current SAE small-area model generation, SAM Gen3, was implemented in January 2022.

SAM Gen3 generalizes a Fay-Herriot style small-area model. In plain language, it borrows strength across related areas and industries. BLS describes the method as using direct estimates, model-based variance information, state-average information, and synthetic information. It can group or relate cells using regression-tree logic and shrink noisy direct estimates toward more stable model components.

Agent interpretation:

- Modeled does not mean fabricated. It means BLS is using a statistical model because direct sample evidence is not strong enough.
- The smaller and more detailed the cell, the more likely model assistance matters.
- Modeled cells can revise when benchmark data, sample, variance estimates, model weights, or area/industry definitions change.
- When explaining volatility or revisions in a small detailed cell, discuss sample adequacy and model borrowing before assuming an economic event.

## 9. Weight smoothing

BLS uses weight-smoothing procedures for many area-level and modeled estimates. Weight smoothing reduces the influence of individual units whose original sampling weights would otherwise cause excessive month-to-month volatility or benchmark revision. BLS describes the approach as replacing original weights for non-influential units using smooth functions while preserving important information from influential units.

Agent guidance:

- If a user asks why SAE does not mechanically equal a simple weighted sample ratio, mention robust estimation and weight smoothing.
- If a user sees high volatility in a detailed small-area series, consider sample design, small cell sizes, and weight effects as candidate explanations.

## 10. Non-AE estimates: PE, AWH, AHE, AWE

### Production and nonsupervisory employees (`PE`)

PE estimates are generally derived using a ratio of PE to AE applied to the current AE estimate. In broad form:

```text
PE_hat[t] = AE_hat[t] * estimated(PE / AE)[t]
```

The ratio is estimated from sample data, with robust and composite methods as appropriate.

### Average weekly hours (`AWH`)

AWH is calculated as aggregate hours divided by employment for the relevant employee group. For aggregate cells, AWH is employment-weighted across components.

```text
AWH = aggregate weekly hours / employment
```

### Average hourly earnings (`AHE`)

AHE is calculated as aggregate payroll divided by aggregate hours. For summary cells, BLS aggregates payroll and hours and then divides; agents should not average lower-level AHE values arithmetically unless the correct hours weights are applied.

```text
AHE = aggregate weekly payroll / aggregate weekly hours
```

### Average weekly earnings (`AWE`)

AWE is derived from AWH and AHE:

```text
AWE = AWH * AHE
```

### Weighted difference-link-and-taper estimator

For non-AE estimates, BLS uses a robust weighted-difference-link-and-taper estimator. The difference-link captures over-the-month change from the matched sample. The taper component gradually pulls the estimate toward the overall sample average over time. BLS describes a typical composite base using about 90 percent prior-month estimate and 10 percent current sample average, although implementation can vary by estimate type and cell.

Agent cautions for non-AE data:

- There is no QCEW benchmark source for hours and earnings comparable to the AE employment benchmark.
- Hours and earnings estimates can be more sensitive to sample composition, payroll timing, bonuses, commissions, and industry mix.
- AHE is not a fixed wage rate; it can move because different types of workers or establishments enter or leave the average.
- Use hours weights for AHE aggregation and employment weights for AWH aggregation.

## 11. Net birth/death modeling

### Why the birth/death model exists

The CES sample cannot fully capture new establishment births or deaths in real time because:

- the UI/QCEW frame arrives with a lag,
- newly opened businesses are not immediately in the sample frame,
- practical sampling begins after firms have existed long enough to enter administrative records and be selected/enrolled, and
- closed businesses often stop responding rather than reporting a clean final zero.

Therefore, monthly all-employee estimation includes a net birth/death (`BD`) component.

### Two-step logic

BLS describes the birth/death approach in two broad steps.

1. **Sample-based link excluding deaths and nonrespondents.** Out-of-business zero reports and nonrespondents are excluded from the matched sample so continuing businesses represent the change among continuing businesses.
2. **ARIMA residual model based on QCEW/LDB history.** BLS uses QCEW-based population data to measure the residual net birth/death component not captured by the continuing-business link, then forecasts it with time-series models.

### Population-history construction

For model input, BLS uses recent LDB/QCEW history. It classifies or constructs population employment, continuous units, deaths, imputed continuing/death employment, and residual net birth/death components. Residuals are chained and forecast. BLS produces forecasts by sample age, because one-year-old and two-year-old samples capture different amounts of birth/death activity.

### Level and distribution

Birth/death forecasts are produced at statewide industry levels, then reconciled and distributed:

- state forecasts are raked or reconciled to CES National forecasts to prevent divergence between national and summed state birth/death components,
- detailed industry and MSA birth/death components are distributed using employment proportions, and
- aggregate cells sum lower-level components.

Agent guidance:

- Do not treat the birth/death model as a small correction only. It can be important during turning points or in industries with high firm churn.
- Do not assume the birth/death model perfectly identifies real-time recessions or booms. It relies on historical patterns and later QCEW benchmarking.
- When explaining benchmark revisions, consider birth/death forecast error as one contributor.

## 12. Aggregation and top-down controls

### Industry aggregate structure

SAE estimates follow the usual CES aggregate hierarchy:

```text
Total nonfarm = Total private + Government
Total private = Goods-producing + Private service-providing
Goods-producing = Mining and logging + Construction + Manufacturing
Private service-providing = Trade, transportation, and utilities
                           + Information
                           + Financial activities
                           + Professional and business services
                           + Education and health services
                           + Leisure and hospitality
                           + Other services
Government = Federal government + State government + Local government
```

The exact published detail available depends on area size, sample, confidentiality, and benchmark-vintage decisions.

### Top-down estimation

BLS uses top-down estimation to reduce the accumulation of error from small detailed cells. Detailed AE estimates can be constrained to stronger higher-level values. This matters when agents try to reconstruct totals by independently estimating detailed industries.

Agent guidance:

- Prefer official published aggregates to user-created sums where possible.
- When summing detailed estimates, expect discrepancies from rounding, constraints, unavailable detail, direct estimation, or seasonal adjustment.
- For all employees and production employees, aggregate employment is generally a rounded sum of component estimates.
- For AWH, aggregate values are employment-weighted.
- For AHE, aggregate values should be payroll divided by hours, not a simple average of component AHE values.

### Rounding

Published CES estimates are rounded. Aggregates can differ slightly from sums computed from rounded components. Agents should not over-interpret small arithmetic differences caused by rounding.

## 13. Annual benchmarking

### Benchmark source

The annual benchmark reanchors SAE employment estimates to QCEW universe employment counts, plus noncovered employment adjustments for CES-scope jobs outside QCEW/UI coverage.

QCEW is more comprehensive than the monthly CES sample, but it is not timely enough to replace CES for current monthly estimation. The benchmark therefore improves historical levels while CES provides timelier current estimates.

### Standard revision window

The benchmark normally replaces or revises a block of not seasonally adjusted estimates after the latest benchmark month. BLS describes the standard process as revising about 20 months of not seasonally adjusted data before monthly estimation resumes on the new benchmark level.

For the 2025 benchmark, BLS replaced estimates for April 2024 through September 2025 for all states, D.C., Puerto Rico, the U.S. Virgin Islands, and about 430 metropolitan areas/divisions. October through December 2025 were then reestimated from the new September 2025 level using updated microdata and birth/death inputs.

### Seasonally adjusted revision window

Seasonally adjusted estimates usually revise over a longer window because updated not seasonally adjusted data and updated seasonal factors affect multiple years. For the 2025 benchmark, BLS revised seasonally adjusted SAE data for January 2021 through December 2025, with select historical revisions before April 2024.

### Benchmark revision definition

A benchmark revision is generally:

```text
benchmark revision = benchmark employment level - previously published sample-based estimate
```

The September benchmark month is often used to assess benchmark revision because it is the latest month in the benchmark period with QCEW-based universe employment available before subsequent months are reestimated.

### Net error interpretation

Benchmark revisions are often used as a practical proxy for total survey error in AE estimates, but they are not a pure sampling-error measure. They include sampling error, model error, frame updates, classification changes, noncovered employment revisions, and QCEW measurement error.

Agent guidance:

- Always report both level revisions and percentage revisions when possible. A small percent revision in a large industry can be a large job-count revision; a large percent revision in a small industry can be a small job-count revision.
- Check the benchmark article for benchmark-specific caveats, discontinued series, area definition updates, and special handling.
- Keep benchmark vintage as explicit metadata in time-series databases.

## 14. Noncovered employment (`NCE`) and special benchmark adjustments

### Noncovered employment

Noncovered employment is CES-scope employment not covered by UI records and therefore not directly in QCEW. Examples can include certain student workers, hospital interns, elected or appointed officials, some nonprofit or religious employment, railroad employment covered by the Railroad Retirement Board, and other categories depending on law and coverage.

State Workforce Agencies provide monthly noncovered employment counts where available. BLS also uses sources such as administrative records, Census data, Railroad Retirement Board data, and other surveys where needed.

Agent guidance:

- QCEW is not exactly equal to the CES benchmark population because CES adds noncovered employment where in scope.
- When reconciling QCEW and CES, account for NCE before declaring a discrepancy.

### Noneconomic code changes (`NECCs`)

Benchmarking can reveal code changes due to administrative reclassification rather than real economic movement. BLS refers to these as noneconomic code changes. If a noneconomic code change is small relative to employment, BLS can wedge it over a defined period; if large, BLS can lengthen the wedge or reconstruct history with historical QCEW.

Agent guidance:

- Do not interpret every benchmark-related industry movement as a real employment shift.
- Check whether the benchmark article mentions classification or code-change effects.

### Local government education summer adjustment

CES and QCEW can treat some local government education employees differently during summer months. CES can count certain faculty with annual contracts as employed year-round, while QCEW may not show them in summer payroll records in the same way. BLS applies a summer adjustment for local government education benchmark construction.

Agent guidance:

- Be careful when comparing summer local government education CES and QCEW employment.
- Large seasonal summer swings in education need program-specific interpretation.

## 15. Seasonal adjustment

### What is seasonally adjusted

SAE publishes seasonally adjusted data for selected nonfarm payroll employment series, including selected state industry/supersector/sector series and total nonfarm for metropolitan areas with sufficient history. Not every SAE series has a seasonally adjusted counterpart.

### Method

BLS uses X-13ARIMA-SEATS. By default, BLS uses 10 years of history for seasonal adjustment when possible, with a minimum of 3 years. Historical corrections can extend farther back when model changes or data changes affect earlier periods.

### Two-step method

SAE uses a two-step seasonal adjustment method because the time series contains:

- benchmarked universe data through the latest benchmark period, and
- sample-based estimates after the benchmark period.

BLS seasonally adjusts the benchmark/universe portion and the sample-based portion separately, then splices the adjusted series at the benchmark transition point.

### Concurrent seasonal adjustment

SAE uses concurrent seasonal adjustment. Each month, all available current data are used to update seasonal factors and produce revised seasonally adjusted estimates. This means seasonally adjusted current data can revise even before an annual benchmark.

### Variable survey interval adjustment

The CES reference period is the pay period including the 12th. Depending on the calendar, the interval between monthly reference periods can be 4 or 5 weeks. BLS uses REGARIMA variables to adjust for variable survey interval effects. The model uses monthly variables, with March serving as the excluded reference month.

### Outliers and prior adjustments

BLS can identify outliers and use prior adjustments for known nonseasonal effects before running seasonal adjustment. Prior adjustments remove known effects from the input series before seasonal factor estimation, then add them back afterward. This is important when large one-time events, disasters, strikes, or pandemic effects would otherwise distort seasonal factors.

### Aggregation of seasonally adjusted series

For states, many broader seasonally adjusted series are aggregations of independently seasonally adjusted components. For metropolitan areas, total nonfarm employment is directly seasonally adjusted and is not constructed as an aggregation of seasonally adjusted component industries.

Agent guidance:

- Do not seasonally adjust by hand unless the task explicitly asks for experimental work.
- Do not mix seasonally adjusted and not seasonally adjusted values in growth calculations.
- Do not aggregate MSA component SA estimates to approximate MSA total nonfarm; use the directly adjusted MSA total nonfarm series.
- Expect SA data to revise monthly under concurrent adjustment and more extensively during benchmark updates.

## 16. Derivative measures

### Annual and quarterly averages

SAE publishes or supports annual and quarterly averages. Annual averages are typically simple averages of monthly values for the year. In BLS public access tools, annual average can be represented with period `M13`.

### Three-month average change

SAE presentation can include 3-month average changes for selected seasonally adjusted employment series. These smooth month-to-month volatility but still depend on current vintage and seasonal adjustment.

### Diffusion indexes

A diffusion index measures breadth of employment change across a set of component series. For each component:

- increasing employment contributes 100,
- unchanged employment contributes 50,
- decreasing employment contributes 0.

The diffusion index is the average of these component scores. A value above 50 indicates more breadth of increase than decrease; a value below 50 indicates more breadth of decrease than increase.

CES-SA diffusion indexes can be computed across states, D.C., and metropolitan areas for selected periods such as 1, 3, 6, and 12 months.

## 17. Reliability, error, and interpretation

### Sampling and nonsampling error

CES estimates are subject to both sampling and nonsampling error. Sampling error arises because CES surveys a sample rather than the full universe each month. Nonsampling error can come from reporting errors, nonresponse, classification issues, frame lag, model error, benchmark-source error, and processing issues.

### Benchmark revision as a reliability measure

For AE employment, benchmark revisions are often used to evaluate total error because the QCEW-based benchmark replaces sample-based estimates with more complete universe information. However, QCEW itself can contain measurement and classification error, and benchmark revisions also include noncovered employment changes and methodology updates.

### Sampling variance and significance

BLS produces sample variance measures for AE estimates using generalized variance functions and related methods. These variance estimates are useful for assessing whether over-the-month changes are statistically significant, but they do not include all sources of error, especially nonsampling and model error.

Agent guidance:

- For small monthly changes, avoid saying employment definitively rose or fell unless the change is material or statistically supported.
- Use benchmark revision history to discuss reliability over longer horizons.
- For small areas and detailed industries, emphasize uncertainty more than for state total nonfarm.
- Distinguish real economic movement from estimation noise, model revision, seasonal-adjustment revision, and benchmark revision.

## 18. Release schedule and publication products

SAE estimates are released monthly. The state and area employment release is usually published on the fifth Friday after the reference period that includes the 12th of the month. Metropolitan area estimates are released later, typically two Wednesdays after the state release. Standard benchmarked data are generally incorporated in the annual benchmark release cycle, but agents should always check the current BLS release calendar and benchmark article because release timing can vary.

SAE data are available through BLS public tools, news releases, tables, text files, and database interfaces. The presentation page also notes that SAE estimates are used by other programs and institutions, including:

- Federal Reserve Bank of Philadelphia state coincident indexes,
- BEA state personal income estimates,
- LAUS models,
- JOLTS state models, and
- productivity measures.

Agent guidance:

- For current estimates, retrieve the latest BLS data directly rather than relying on this static knowledge file.
- Store release date, reference month, preliminary/final status, seasonal-adjustment status, and benchmark vintage.
- Monitor BLS errata and special notices for corrections.

## 19. Current benchmark-specific notes: 2025 benchmark / January 2026 release

The `BLS-SAE-BENCHMARK-2025` article is the benchmark-specific source for the latest details as of this file's review date.

Important facts from that article:

- With the January 2026 SAE release in April 2026, BLS revised state and area payroll employment, hours, and earnings estimates to incorporate 2025 benchmark levels and updated seasonal adjustment factors.
- The 2025 benchmark revised not seasonally adjusted estimates for April 2024 through December 2025, seasonally adjusted estimates for January 2021 through December 2025, and selected historical data before April 2024.
- For the 2025 benchmark, BLS replaced estimates through September 2025 with benchmark information and reestimated October through December 2025 from the new September benchmark level using updated microdata and birth/death inputs.
- BLS discontinued roughly 900 detailed employment, hours, and earnings series in the 2026 release because of low or declining employment and sample coverage. BLS stated that all all-employee state and metropolitan statistical area series continued.
- BLS began publishing seasonally adjusted data for all metropolitan areas with the 2025 benchmark, adding selected metropolitan areas that previously lacked sufficient history or had definitional changes.

Agent guidance:

- For any 2026-current question about why a detailed SAE series is missing, first check the 2025 benchmark article and related special notices.
- For historical work, flag the 2025 benchmark as a vintage event that can change values and available series.
- If comparing values downloaded before and after April 2026, expect revisions.

## 20. Relationship to adjacent programs

### CES National (`CES-N`) vs CES State and Area (`CES-SA` / `SAE`)

CES-N and CES-SA use the same underlying survey but are separate estimation programs with different estimation structures and publication goals. CES-N focuses on national estimates. CES-SA focuses on states and areas. Birth/death reconciliation helps prevent major divergence between national and summed state components, but agents should still use the official program series for the requested geography and concept.

Do not replace a CES-N national estimate with a sum of state SAE estimates unless the analysis explicitly requires that sum and handles rounding, methodology, and seasonal-adjustment differences.

### QCEW vs CES-SA

QCEW is a near-universe quarterly administrative count of employment and wages based on UI records. CES-SA is a monthly survey estimate benchmarked annually to QCEW plus noncovered employment.

Use QCEW for detailed historical universe employment and wage counts when timeliness is less important. Use CES-SA for timely monthly payroll employment, hours, and earnings by state and area.

### LAUS vs CES-SA

LAUS provides labor force, employment, unemployment, and unemployment-rate measures based on household/labor-force concepts and models. CES-SA provides establishment payroll jobs. Payroll jobs and household employment can diverge because of multiple jobholding, self-employment, agricultural scope, unpaid family work, commuting, and residence-vs-workplace differences.

### JOLTS vs CES-SA

JOLTS measures job openings, hires, quits, layoffs/discharges, and separations. CES-SA measures payroll employment, hours, and earnings. JOLTS state models can use CES-related inputs, but the concepts are different.

## 21. Agent operating rules

### Rule 1: Always identify the concept first

Before answering, determine whether the user is asking for:

- payroll jobs (`AE`),
- production/nonsupervisory jobs (`PE`),
- hours (`AWH`),
- earnings (`AHE`, `AWE`),
- unemployment/labor force (not SAE),
- employment counts by universe record (often QCEW), or
- turnover/openings (JOLTS).

If the concept is not SAE, redirect to the appropriate program.

### Rule 2: Track vintage and seasonal status

Every SAE observation should carry at least:

- series id,
- area code and area name,
- industry code and industry name,
- data type,
- seasonal adjustment flag,
- period,
- value,
- units,
- preliminary/final status if known,
- release date or download timestamp,
- benchmark vintage,
- geography-definition vintage where relevant.

For Polars-friendly data pipelines, store SAE as a long table rather than wide monthly columns. Use categorical/string dimensions for area, industry, data type, and seasonal status; use date or `(year, period)` fields for time.

### Rule 3: Do not mix SA and NSA data

Seasonally adjusted and not seasonally adjusted series answer different questions. Growth rates, month-to-month changes, and charts should not mix them unless explicitly demonstrating the difference.

### Rule 4: Use official aggregates when possible

Because of rounding, direct seasonal adjustment, top-down constraints, and unavailable detail, official aggregates can differ from sums of published components. Prefer the official total or aggregate series.

### Rule 5: Treat detailed small-area estimates carefully

For detailed industries in small areas, consider:

- sample size,
- sample coverage,
- small-area modeling,
- confidentiality/disclosure rules,
- annual benchmark revisions,
- birth/death model effects,
- local one-off events,
- classification changes.

Use cautious language when interpreting small monthly changes.

### Rule 6: Explain earnings and hours as averages

Average hourly earnings and average weekly hours are averages across changing establishments and workers. They are not direct measures of wage rates or individual worker schedules.

### Rule 7: Benchmark revisions are not always economic events

Benchmark revisions can arise from updated QCEW universe counts, noncovered employment changes, birth/death forecast error, sample error, classification updates, noneconomic code changes, seasonal-factor updates, or methodology changes. Do not interpret revisions as actual employment changes in the benchmark month.

### Rule 8: For latest values, fetch fresh data

This file is methodological knowledge. For current employment levels, release dates, discontinued series, or special notices, query current BLS data pages, news releases, or files.

## 22. Common question patterns and recommended responses

### "Why did my SAE series revise?"

Check:

1. Was there an annual benchmark release?
2. Was the series seasonally adjusted under concurrent seasonal adjustment?
3. Did BLS update birth/death inputs or sample microdata?
4. Was there a geography, NAICS, or area-definition update?
5. Was there a correction/erratum?
6. Was the series detailed and sample-thin, making it more exposed to model and benchmark revision?

Recommended framing:

> SAE revisions can come from regular monthly sample updates, concurrent seasonal adjustment, and annual benchmarking to QCEW plus noncovered employment. Benchmark revisions can reflect improved universe counts and classification changes, not just new economic activity.

### "Why does SAE differ from QCEW?"

Check:

- monthly survey estimate vs quarterly universe count,
- CES scope vs QCEW UI coverage,
- noncovered employment additions,
- timing and reference-period differences,
- benchmark vintage,
- industry/geography classification,
- summer local government education treatment,
- rounding and aggregation.

Recommended framing:

> QCEW is the benchmark source but not identical to CES-SA. CES-SA is monthly and includes model-based current estimates and noncovered employment; QCEW is a lagged administrative universe count.

### "Why does SAE differ from LAUS?"

Check:

- payroll jobs vs employed persons,
- workplace vs residence concept,
- multiple jobholding,
- self-employment and agricultural scope,
- household vs establishment survey/model.

Recommended framing:

> SAE counts jobs on nonfarm payrolls by place of work. LAUS estimates labor-force concepts for residents. They are designed to answer different questions.

### "Can I sum states to the U.S.?"

Use caution. For analytical sums of not seasonally adjusted state estimates, a sum can be informative, but it is not a substitute for the official CES National estimate. For seasonally adjusted estimates, independent seasonal adjustment and aggregation rules make this especially risky. Use CES-N for U.S. totals.

### "Can I sum metro areas to a state?"

Usually no. MSAs can cross state lines, do not cover all territory, and can overlap with divisions or other geographies depending on definition. Use published state series.

### "Can I average AHE across industries?"

Not arithmetically. AHE aggregation requires payroll and hours, or at least hours weights. A simple unweighted mean of industry AHE values is not an official aggregate AHE.

### "Why is a detailed series missing or discontinued?"

Check the latest benchmark article, SAE special notices, and confidentiality/sample-adequacy rules. The 2026 benchmark release discontinued roughly 900 detailed series due to low or declining employment and sample coverage, while all all-employee state and MSA series continued.

## 23. Suggested ETL/data model for eco-stats projects

A robust SAE table should be long and vintage-aware.

Suggested fields:

```text
source_program          # "SAE" or "CES-SA"
series_id               # BLS time-series id if available
area_code
area_name
area_type               # state, metro, metropolitan division, territory, NYC, etc.
industry_code
industry_name
data_type               # AE, PE, AWH, AHE, AWE, etc.
seasonal_adjustment     # SA or NSA
period                  # monthly date, or year + BLS period code
value
units                   # thousands of jobs, dollars, hours, index, etc.
footnote_codes
preliminary_flag
release_date
benchmark_vintage
geography_vintage
industry_classification # e.g., 2022 NAICS, if known
retrieved_at
source_url_or_file
```

Recommended quality checks:

- Validate that period codes map correctly to monthly dates; annual averages can use `M13` in BLS tools.
- Verify units before arithmetic. Employment may be in thousands; hours and earnings use different units.
- Keep SA and NSA series separate.
- Do not overwrite old downloads without preserving vintage if revisions matter.
- Compare official aggregate series with computed sums only as a diagnostic, not as a replacement.
- For benchmark analysis, compute both level revision and percent revision.
- For AHE/AWH aggregation, use the correct weights or official aggregate values.

## 24. Glossary

| Term | Meaning |
|---|---|
| `AE` | All employees; payroll jobs on establishment payrolls for the reference pay period. |
| `AHE` | Average hourly earnings; aggregate payroll divided by aggregate hours. |
| `AWH` | Average weekly hours; aggregate hours divided by employment. |
| `AWE` | Average weekly earnings; AWH multiplied by AHE. |
| `BD` | Net birth/death component added to all-employee estimates to account for establishment openings and closings not captured by the sample in real time. |
| Benchmark | Annual reanchoring of CES estimates to QCEW universe counts plus noncovered employment. |
| CES-N | Current Employment Statistics National program. |
| CES-SA / SAE | Current Employment Statistics State and Area program. |
| Diffusion index | Breadth measure of employment change across components, where increases count 100, no change 50, decreases 0. |
| Establishment | Single physical location engaged in one primary economic activity. |
| LDB | BLS Longitudinal Database, based on QCEW/UI records and used as the CES sampling frame. |
| Matched sample | Establishments with usable reports for both current and prior months. |
| MSA | Metropolitan Statistical Area. |
| NAICS | North American Industry Classification System. SAE currently uses 2022 NAICS. |
| NCE | Noncovered employment; CES-scope jobs not covered by UI/QCEW. |
| NECC | Noneconomic code change; administrative classification change rather than real economic movement. |
| PE | Production and nonsupervisory employees. |
| QCEW | Quarterly Census of Employment and Wages, a near-universe administrative employment and wage source based on UI records. |
| SAM Gen3 | SAE small-area model generation implemented in January 2022 for cells with insufficient sample. |
| UI account | Unemployment insurance account identifier used in the sampling frame. |
| Variable survey interval | Calendar effect caused by 4-week vs 5-week intervals between CES reference periods. |

## 25. Minimal answer checklist for agents

Before finalizing any SAE-related answer, check:

```text
[ ] Is the user asking for payroll jobs, not persons or unemployment?
[ ] Have I identified the geography and whether it is state, MSA, division, territory, or NYC?
[ ] Have I identified the industry and NAICS/CES code vintage if relevant?
[ ] Have I identified AE vs PE vs hours/earnings?
[ ] Have I kept SA and NSA separate?
[ ] Have I checked whether the answer depends on latest data or a recent benchmark?
[ ] Have I considered benchmark vintage, preliminary/final status, and revisions?
[ ] For small areas/details, have I mentioned sample/model uncertainty if interpreting changes?
[ ] For earnings/hours, have I avoided wage-rate or hours-worked overclaims?
[ ] For aggregates, have I used official aggregates or correct weights?
[ ] Have I cited the closest BLS source page?
```

## 26. Source-to-topic map for quick citation

Use these source keys for citations or documentation:

- Scope, estimates, units, geography, industry classification: `BLS-SAE-CONCEPTS`.
- Respondent collection, EDI, microdata edits, screening, confidentiality: `BLS-SAE-DATA`.
- Sampling frame, stratified sample, optimum allocation, certainty units, government sample, weights, coverage: `BLS-SAE-DESIGN`.
- Estimation formulas, matched sample, robust link relatives, SAM Gen3, non-AE estimators, birth/death modeling, aggregation, benchmarking, seasonal adjustment, reliability: `BLS-SAE-CALCULATION`.
- Release schedule, data access, uses, corrections: `BLS-SAE-PRESENTATION`.
- Latest benchmark-revision facts and discontinued/current series notes: `BLS-SAE-BENCHMARK-2025`.
- Detailed seasonal adjustment operations: `BLS-SAE-SEASONAL`.
- OMB delineation adoption history and area-definition vintages: `BLS-SAE-MSA-DEFS`, `BLS-SAE-BENCHMARK-ARCHIVE`, `BLS-SAE-BENCHMARK-2024`, `BLS-SAE-NOTICE-MSA-2024`, `BLS-LAUS-AREAS`, `BLS-MSA-REDELINEATION-PLANS`.
