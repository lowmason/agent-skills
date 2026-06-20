# JOLTS (Job Openings and Labor Turnover Survey)

Primary BLS sources reviewed:

- Handbook of Methods, JOLTS Concepts: https://www.bls.gov/opub/hom/jlt/concepts.htm
- Handbook of Methods, JOLTS Collections and Data Sources: https://www.bls.gov/opub/hom/jlt/data.htm
- Handbook of Methods, JOLTS Design: https://www.bls.gov/opub/hom/jlt/design.htm
- Handbook of Methods, JOLTS Calculation: https://www.bls.gov/opub/hom/jlt/calculation.htm
- Handbook of Methods, JOLTS Presentation: https://www.bls.gov/opub/hom/jlt/presentation.htm
- JOLTS 2025 Benchmark Article: https://www.bls.gov/jlt/joltsbmart2025.htm
- JOLTS Data Collection Forms page: https://www.bls.gov/jlt/jltcoll.htm
- National JOLTS technical note PDF: https://www.bls.gov/news.release/pdf/jolts.pdf
- State JOLTS technical note: https://www.bls.gov/news.release/jltst.tn.htm
- JOLTS public flat-file directory: https://download.bls.gov/pub/time.series/jt/

Note on source conflicts and freshness: the current Handbook and technical notes describe a sample of about 21,000 establishments. The flat-file dictionary `jt.txt` still contains some legacy language referring to 16,000 establishments and ES-202. Use the Handbook and technical notes for current methodology. Use `jt.txt` for file layout and code schema. Also, the Handbook collection page says initial CATI collection occurs for about 5 months, while the data collection forms page says respondents are in CATI for the first 3 months before web collection. Treat collection-mode duration as an operational detail that can change; do not use it as a statistical assumption unless verified for the relevant period.


## 1. What JOLTS measures

JOLTS is an establishment survey that measures labor demand and labor turnover. The core published data elements are:

- Job openings.
- Hires.
- Total separations.
- Quits.
- Layoffs and discharges.
- Other separations, nationally but generally not for state estimates.

JOLTS also collects employment from respondents. JOLTS employment is not published as a JOLTS data element. It is used for validation, benchmarking, and rate denominators. The employment definition is aligned with the Current Employment Statistics (CES) program.

The main conceptual difference among data elements is stock versus flow:

- Job openings are a stock measured on the last business day of the reference month.
- Hires and separations are flows over the entire reference month.
- Rates therefore use different denominators. The job openings rate includes both filled and unfilled jobs in the denominator; hires and separations rates use employment.


## 2. Coverage, frame, and population

### 2.1 Sampling frame

The JOLTS sampling frame is built from two sources:

1. The BLS Quarterly Census of Employment and Wages (QCEW), which is based on administrative records from state unemployment insurance programs and federal establishments covered by Unemployment Compensation for Federal Employees (UCFE).
2. A railroad-establishment frame from the Federal Railroad Administration (FRA), added to complete the JOLTS sampling frame.

The QCEW frame covers roughly 95 percent of U.S. jobs. JOLTS uses a frame derived from CES/QCEW infrastructure, and the Handbook states that JOLTS coverage rates do not fall below 85 percent; if they did, BLS would conduct bias studies.

### 2.2 In-scope establishments

JOLTS covers nonfarm business and government establishments in the 50 states and the District of Columbia. It includes:

- Private nonfarm establishments.
- Civilian federal government establishments.
- State and local government establishments.
- Agricultural-services establishments within agriculture, and logging, as specified by BLS scope rules.

### 2.3 Out-of-scope establishments

Out-of-scope units include:

- Establishments out of business.
- Invalid or missing NAICS codes, such as 000000 or 999999.
- Agriculture NAICS 11, except logging NAICS 1133.
- Private households, NAICS 814110.
- Establishments with no legal name or trade name.
- Establishments outside the 50 states and the District of Columbia.
- Establishments reporting zero employment for the most recent 6 months on the sampling frame.

### 2.4 Establishment concept

The basic sample unit is an establishment, generally a single physical location where business is conducted or services or industrial operations are performed. When multiple distinct economic activities occur at one physical location, they can be treated as separate establishments if separate reports can be prepared and the activities are significant.

### 2.5 Employer of record principle

Temporary help agency workers, employee-leasing employees, outside contractors, and consultants are counted by their employer of record, not by the establishment where they physically work. This affects both employment and all JOLTS flow measures. For example, a client establishment should not count temporary-help workers supplied by a staffing firm as its own employees.


## 3. Core definitions

### 3.1 Employment

Employment includes persons on the payroll who worked or received pay for any part of the pay period that includes the 12th day of the reference month. Included are:

- Full-time and part-time workers.
- Permanent, short-term, and seasonal workers.
- Salaried and hourly workers.
- Employees on paid vacation or other paid leave.
- Employees on paid sick leave when pay is received directly from the employer.
- Salaried officers of corporations.
- Civilian government employees.

Excluded are:

- Sole proprietors.
- Partners of unincorporated businesses.
- The unincorporated self-employed.
- Unpaid family workers and unpaid volunteers.
- Farm workers and domestic workers.
- Military personnel.
- Employees of certain national-security agencies specified by BLS.
- Persons on layoff, leave without pay, or strike for the entire pay period.
- Persons hired but not yet reported to work during the pay period.
- Temporary help, leased employees, outside contractors, and consultants at the client establishment; they are counted by their employer of record.

### 3.2 Job openings

A job opening is a position open on the last business day of the reference month. A job is open only if all three conditions are met:

1. A specific position exists and work is available. The job may be full-time or part-time and may be permanent, short-term, or seasonal.
2. The job could start within 30 days, whether or not the employer finds a suitable candidate.
3. The employer is actively recruiting outside the establishment.

Active recruiting may include advertising, internet postings, help-wanted signs, word-of-mouth announcements, accepting applications, interviewing candidates, contacting employment agencies, and recruiting at job fairs or state/local employment offices.

Excluded from job openings are:

- Positions open only to internal transfers, promotions, demotions, or recall from layoff.
- Jobs with start dates more than 30 days in the future.
- Positions where employees have been hired but have not yet reported to work.
- Positions to be filled by workers from temporary-help agencies, employee-leasing companies, outside contractors, or consultants.

### 3.3 Hires

Hires include all additions to payroll during the reference month. Included are:

- New hires and rehires.
- Full-time and part-time hires.
- Permanent, short-term, and seasonal hires.
- Recalls to the location after a formal layoff lasting more than 7 days.
- On-call or intermittent workers returning after being formally separated.
- Workers both hired and separated during the month.
- Transfers from other locations.

Excluded are:

- Transfers or promotions within the same reporting location.
- Employees returning from strike.
- Temporary-help, leasing, outside-contractor, and consultant workers at the client establishment.

### 3.4 Separations

Separations include all separations from payroll during the entire reference month. JOLTS asks respondents to classify separations into quits, layoffs and discharges, and other separations.

Quits:

- Voluntary separations initiated by the employee.
- Exclude retirements and transfers to other locations, which are other separations.

Layoffs and discharges:

- Involuntary separations initiated by the employer.
- Include layoffs with no intent to rehire.
- Include formal suspensions from pay status lasting or expected to last more than 7 days.
- Include discharges from mergers, downsizing, or closings.
- Include firings or discharges for cause.
- Include terminations of permanent, short-term, and seasonal employees, whether or not seasonal employees are expected to return next season.

Other separations:

- Retirements.
- Transfers to other locations.
- Separations due to employee disability.
- Deaths.

Excluded from separations are:

- Transfers within the same location.
- Employees on strike.
- Temporary-help, employee-leasing, outside-contractor, and consultant workers at the client establishment.

Important interpretation: the quits rate is often used as a measure of workers' willingness or ability to leave jobs, but it is still an establishment-reported flow and can be affected by definitions, industry composition, revisions, and sampling/model error.


## 4. Rate formulas and annual calculations

### 4.1 Monthly rate formulas

Let:

- `E` = employment.
- `JO` = job openings.
- `H` = hires.
- `S` = separations or a separations component.

Then:

```text
job_openings_rate = JO / (E + JO) * 100
hires_rate        = H  / E * 100
separations_rate  = S  / E * 100
```

The job openings denominator is employment plus job openings because it represents filled plus unfilled jobs. Hires and separations rates use employment only.

### 4.2 Annual levels and rates

Annual flow levels for hires, quits, layoffs and discharges, other separations, and total separations are the sum of the 12 published monthly levels.

Annual average job openings levels are the average of the 12 monthly job openings levels.

Annual average flow rates are calculated as:

```text
annual_flow_rate = sum(monthly JOLTS flow levels) / sum(monthly CES employment levels) * 100
```

Annual average job openings rates are calculated as:

```text
annual_job_openings_rate = sum(monthly JO levels) / (sum(monthly CES employment levels) + sum(monthly JO levels)) * 100
```

Do not calculate annual rates as a simple unweighted average of monthly rates unless the explicit goal is a simple monthly-average statistic rather than the BLS annual average rate.


## 5. Industry, geography, and size classifications

### 5.1 Industry classification

JOLTS uses NAICS. BLS technical notes state that, starting with data for January 2023, industries are classified under the 2022 NAICS.

BLS verifies establishment industry, location, and ownership classifications through state workforce agencies. The Handbook notes that NAICS verification/updating occurs on a 3-year cycle.

### 5.2 National industry publication levels

JOLTS publishes national seasonally adjusted and not seasonally adjusted estimates at:

- Total nonfarm.
- Total private.
- Government.
- Sampled NAICS sectors and selected subsectors.
- Census regions at the total nonfarm level.
- Establishment size classes at the total private level.

The public flat-file industry mapping includes these common industry codes:

| Code | Industry |
|---:|---|
| 000000 | Total nonfarm |
| 100000 | Total private |
| 110099 | Mining and logging |
| 230000 | Construction |
| 300000 | Manufacturing |
| 320000 | Durable goods manufacturing |
| 340000 | Nondurable goods manufacturing |
| 400000 | Trade, transportation, and utilities |
| 420000 | Wholesale trade |
| 440000 | Retail trade |
| 480099 | Transportation, warehousing, and utilities |
| 510000 | Information |
| 510099 | Financial activities |
| 520000 | Finance and insurance |
| 530000 | Real estate and rental and leasing |
| 540099 | Professional and business services |
| 600000 | Private education and health services |
| 610000 | Private educational services |
| 620000 | Health care and social assistance |
| 700000 | Leisure and hospitality |
| 710000 | Arts, entertainment, and recreation |
| 720000 | Accommodation and food services |
| 810000 | Other services |
| 900000 | Government |
| 910000 | Federal |
| 920000 | State and local |
| 923000 | State and local government education |
| 929000 | State and local government, excluding education |

### 5.3 Regions and states

The public flat files use state/region codes. Common region codes are:

| Code | Geography |
|---:|---|
| 00 | Total US |
| NE | Northeast region |
| MW | Midwest region |
| SO | South region |
| WE | West region |

State estimates are available for all 50 states and the District of Columbia, but are published only at the total nonfarm level.

### 5.4 Establishment size classes

JOLTS size class is based on an establishment's maximum employment over the last 12 months at the time of sample selection. The classification remains fixed for a year until the next annual sample is drawn.

| Code | Size class |
|---:|---|
| 00 | All size classes |
| 01 | 1 to 9 employees |
| 02 | 10 to 49 employees |
| 03 | 50 to 249 employees |
| 04 | 250 to 999 employees |
| 05 | 1,000 to 4,999 employees |
| 06 | 5,000 or more employees |

All establishments with 5,000 or more employees are included with virtual certainty and remain in sample as long as the employment count remains at or above 5,000.

Size-class estimates are produced at the total private industry level and are available back to December 2000. The size-class estimation process is broadly similar to national industry/region estimation, except BLS notes that size-class estimates are not reviewed for outliers and are aligned at total private using proportions of size classes to CES total employment.


## 6. Data collection and review

### 6.1 Collection process

JOLTS data are collected monthly from selected establishments. BLS data collection centers are in Atlanta, Georgia and Kansas City, Missouri. Interviewers refine addresses and contacts, send enrollment material, and follow up by phone.

Collection modes include:

- Computer-Assisted Telephone Interviewing (CATI) early in a unit's time in sample.
- Web self-reporting after initial collection.
- Email reporting for some respondents.

The Handbook says initial CATI collection takes place for approximately 5 months, while the JOLTS collection forms page says respondents are in CATI for the first 3 months before web collection. Treat this as a possible process update or source inconsistency.

### 6.2 Collection forms

The basic form asks for the same columns an analyst should expect conceptually:

- Total employment for the pay period including the 12th.
- Job openings on the last business day of the month.
- Hires and recalls for the entire month.
- Quits for the entire month.
- Layoffs and discharges for the entire month.
- Other separations for the entire month.

Special forms exist for:

- Temporary Help Services and Professional Employer Organizations, NAICS 561320 and 561330.
- Educational Services, NAICS Sector 61.

Special-form details matter when interpreting microdata or respondent instructions:

- Temporary help and PEO forms focus on employees on the respondent employer's payroll. Temporary help agencies include employees placed at client sites from the sampled office. Temporary help employees between paid assignments for the entire pay period are excluded from employment. Temporary help agencies do not count employees merely being assigned to a different client as hires or separations.
- Education forms include faculty under contract regardless of whether they receive pay while school is out, teachers on paid sabbaticals, employees on paid leave, and substitute teachers who worked during the pay period, except substitutes paid as individual contractors. They exclude non-teaching employees who did not work or receive pay for the entire pay period, and exclude employees returning from summer vacation unless they had been formally separated.

### 6.3 Data review

BLS reviews reported data at two levels:

1. System checks after data are entered into web/CATI systems. Failing records are flagged for collection-center staff review.
2. BLS national-office screening using additional criteria to identify common problems and potential errors.

This matters because JOLTS estimates are not a simple sum of raw reports. They pass through validation, imputation, weighting, benchmarking, outlier handling, alignment, and seasonal adjustment.


## 7. Sample design

JOLTS uses a probability-based stratified random sample. The basic sample unit is an establishment at a single physical location.

### 7.1 Stratification

The sample is stratified by:

- Ownership: private or public.
- Census region: Northeast, Midwest, South, West.
- Industry sector/subsector.
- Establishment employment size class.

Private-sector stratification subsectors include mining and logging; construction; durable manufacturing; nondurable manufacturing; wholesale trade; retail trade; transportation, warehousing, and utilities; information; finance and insurance; real estate and rental and leasing; professional and business services; private educational services; health care and social assistance; arts, entertainment, and recreation; accommodation and food services; and other services.

Public-sector strata include:

- Federal government.
- State and local government education.
- State and local government excluding education.

### 7.2 Panels and time in sample

Most sampled establishments remain in the survey for 36 months and are not sampled again for at least 3 years after completing their time in sample.

The sample has:

- 36 active noncertainty panels.
- 1 certainty panel.

Each month, a new noncertainty panel rotates in and an old panel rotates out. Noncertainty units are asked to report for 36 months.

Each year, BLS selects a new 12-panel sample. At any point, active panels may come from multiple annual samples. Older panels are updated for current stratum characteristics, and out-of-business establishments are removed. Sampling weights are recomputed, and post-stratification represents the updated age structure of the frame.

### 7.3 Sample allocation

Noncertainty sample allocation uses a standard Neyman allocation logic. Strata with more frame units or larger employment variability receive more sample. Frame employment is used to approximate population standard deviation.

### 7.4 Birth samples

Newly opened establishments are represented through quarterly birth samples. BLS implemented quarterly birth sampling in April 2009.

Birth units are selected from establishments that:

- First reported positive employment during the current quarter.
- Belong to JOLTS size class 1-9, 10-49, or 50-249.

Birth samples are drawn by age, industry, and size strata. If a birth stratum has 3 or fewer units, all births in that stratum are selected. Sampled birth units are distributed evenly into 3 panels rolled in over the quarter.


## 8. National estimation workflow

The national estimation workflow is ordered roughly as follows:

1. Unit nonresponse adjustment.
2. Item nonresponse adjustment.
3. Monthly benchmarking and estimation.
4. Automated outlier detection.
5. Birth-death model estimation.
6. Estimates review and manual outlier selection.
7. Alignment to CES employment change.
8. Seasonal adjustment.
9. Variance estimation.
10. Annual benchmarking and reprocessing.

### 8.1 Unit nonresponse adjustment

Unit nonresponse occurs when sampled viable units do not provide usable data. JOLTS inflates respondent weights in an estimation cell using a multiplicative nonresponse adjustment factor, NRAF.

Conceptually:

```text
NRAF_cell = weighted frame employment of viable sampled units
            / weighted frame employment of usable respondent units
```

Where a viable unit is an in-scope sampled unit capable of reporting, and a usable unit is a viable respondent with usable JOLTS data. NRAF is at least 1. The adjustment redistributes nonrespondent weight across respondents while preserving total weighted employment in the cell.

### 8.2 Item nonresponse and imputation

Item nonresponse occurs when a respondent reports some data elements but not others. JOLTS imputes missing values to reduce bias, improve statistical efficiency, and make analysis possible.

The imputation approach groups establishments by employment dynamics:

- Expanding: reported employment increased over the month.
- Stable: reported employment did not change.
- Contracting: reported employment decreased over the month.

Within each industry imputation cell, BLS builds separate models for expanding, stable, and contracting establishments. Donor distributions are based on respondent rates for each data element. The imputation model estimates distribution characteristics such as mean, dispersion, and skewness, then draws imputed rates from uniform distributions.

The model reflects that respondent-rate distributions are often non-normal and skewed, with many observations below the mean and a long upper tail. Imputation therefore uses a below-mean and above-mean draw process:

- Estimate the mean rate `mu` for the dynamic group and item.
- Estimate a distribution length/upper-bound parameter from observed deviations and size-class constraints.
- Estimate the probability that respondent rates fall below the mean.
- Draw from a uniform distribution below or above the mean according to that probability.
- Multiply the imputed rate by the recipient establishment's employment to produce an imputed level.

If total separations are reported but components are missing, imputed component levels are prorated to the reported total separations level.

### 8.3 Monthly benchmarking and estimation

JOLTS estimates are benchmarked monthly to current CES employment. The purpose is to make weighted JOLTS employment equal CES employment in each estimation cell and improve reliability.

The benchmark factor (BMF) is calculated by comparing CES employment with summed weighted JOLTS employment in a region/industry cell.

Conceptually:

```text
SWTE_cell = sum(sample_weight_i * NRAF_cell * reported_employment_i)
BMF_cell  = CES_employment_cell / SWTE_cell
```

The estimate for a data element is then produced by summing establishment-level data multiplied by sampling weights and adjustments, including NRAF, BMF, and any aggregation/disaggregation adjustment.

BLS describes this as a Horvitz-Thompson estimator with a ratio adjustment. Data-element levels are converted to rates after estimation.

Important implication: JOLTS rates depend on CES employment denominators. When CES is benchmarked or revised, JOLTS estimates can revise even if reported JOLTS microdata did not change.

### 8.4 Automated outlier detection

JOLTS uses winsorization to reduce the influence of extreme reported values. Separate cutoff values are established by establishment employment size and data element. Reported values above the cutoff are reset to the cutoff value.

For state estimates, winsorization also safeguards forecasted/extended state estimates. The extended QCEW ratio process uses historical 99th percentile cutoffs for regional ratios by variable.

### 8.5 Birth-death model

JOLTS sample data cannot immediately capture openings, hires, and separations at establishments born after the frame is constructed, especially because the lag from establishment birth to frame appearance is about 1 year and many births die within the first year.

BLS therefore uses a birth-death model. The model:

- Uses establishment birth and death activity from previous years in QCEW.
- Projects forward using over-the-year CES employment change.
- Uses historical JOLTS data to calculate churn rates for establishments of various sizes.
- Combines churn and projected employment changes to estimate hires and separations not measurable in the current sample.
- Allocates model-based total separations to quits, layoffs and discharges, and other separations in proportion to their contribution to sample-based total separations.
- Estimates job openings by applying the sample-based openings-to-hires ratio to modeled hires.
- Adds model-based estimates to sample-based estimates.

### 8.6 Estimates review and manual outlier selection

JOLTS staff manually review not seasonally adjusted estimates during monthly review and annual processing. They flag atypical or large movements, inspect establishment-level microdata behind the estimate, and mark confirmed atypical establishments as outliers. The not seasonally adjusted estimates are then rerun and reviewed again.

### 8.7 Alignment to CES employment change

JOLTS hires minus separations is conceptually comparable to CES over-the-month net employment change, but definitional differences plus sampling and nonsampling error can cause cumulative divergence. BLS uses monthly alignment to limit divergence and improve the hires and separations series.

The alignment logic:

1. Seasonally adjust JOLTS hires and separations and CES employment change.
2. Compute the divergence between JOLTS implied net employment change and CES net employment change.
3. Proportionally adjust hires and separations by their shares of total churn, where churn equals hires plus separations.
4. Back out seasonal adjustment factors to return to not seasonally adjusted estimates.
5. Seasonally adjust again.

Job openings are aligned based on the ratio of job openings to hires from not seasonally adjusted estimates; the openings-to-hires ratio is applied to updated hires to compute updated job openings.

Important implication: after alignment, `hires - separations` is not an independent estimate of net employment growth in the same way raw survey flows would be. It has been constrained toward CES employment trends.

### 8.8 Seasonal adjustment

After alignment, JOLTS uses X-13-ARIMA-SEATS for seasonal adjustment. The program uses concurrent seasonal adjustment: each month, all relevant data through the current month are used to compute updated seasonal adjustment factors.

JOLTS seasonal adjustment uses:

- Moving-average seasonal filters.
- Additive and multiplicative models.
- REGARIMA modeling to improve factors at the beginning and end of series and detect/adjust outliers.

Important implication: current and historical seasonally adjusted values can revise when new months arrive because seasonal factors are recomputed concurrently.

### 8.9 Variance estimation

JOLTS sample variance is estimated using balanced half samples (BHS) with Fay's method. Sample units within region/industry/size cells are split into two random groups. Half-sample estimates are generated using adjusted weights, and variance is based on variability across those replicate estimates.

Fay's factor is 0.5. The method uses the full sample with unequal half-sample weights, rather than discarding half the sample.

### 8.10 Reliability and errors

JOLTS estimates are subject to sampling and nonsampling error.

Sampling error arises because JOLTS surveys a sample, not the entire population. BLS analyses generally use a 90 percent confidence level, meaning intervals are often described as estimate plus or minus 1.65 standard errors.

Nonsampling error can arise from:

- Failure to include a segment of the population.
- Nonresponse.
- Late response.
- Respondent mistakes.
- Collection and processing errors.
- Errors from employment benchmark data used in estimation.

BLS releases median standard errors monthly as part of significant-change tables, and standard errors are updated annually with the most recent 5 years of data.


## 9. Annual benchmarking, revisions, and special adjustments

### 9.1 Monthly revisions

JOLTS publishes a preliminary current-month estimate and a revised estimate for the previous month. Monthly revisions incorporate corrected or late-reported microdata and recalculated seasonal factors.

Practical implication: do not treat the latest month as final. In time-series pipelines, mark the most recent month as preliminary and expect the prior month to revise in the next release.

### 9.2 Annual benchmarking

Each year, with the release of January data, JOLTS estimates are revised to reflect:

- Annual updates to CES employment estimates.
- New seasonal adjustment factors.
- Any needed special adjustments.

JOLTS employment levels, which are not published, are ratio-adjusted to revised CES employment levels. The resulting ratios are applied to all JOLTS data elements. Annual benchmarking revises both seasonally adjusted and not seasonally adjusted series.

The Handbook says seasonally adjusted estimates are recalculated for the most recent 5 years. Because the alignment method depends on seasonal adjustment, not seasonally adjusted estimates are also recalculated for the most recent 5 years to reflect the effect of updated seasonal factors on alignment.

### 9.3 2025 benchmark article details

BLS's 2025 benchmark article states that, with January data, national and regional estimates were annually revised for job openings, hires, separations, and separations components. Seasonally adjusted and not seasonally adjusted data back to January 2021 were subject to revision.

The article also noted a special federal-government alignment procedure for September 2025 through January 2026 related to large federal employment declines, mostly due to the federal deferred resignation program. BLS adjusted the alignment to reconcile CES employment change with JOLTS hires-minus-separations while preserving the impact of the deferred resignation program on JOLTS separations.

Practical implication: when analyzing federal government JOLTS around September 2025 to January 2026, explicitly check benchmark documentation and avoid interpreting revisions as ordinary seasonal-factor changes only.

### 9.4 Error corrections

If errors are discovered after release, BLS evaluates them and develops an action plan within 3 working days of discovery or as soon as practical. Substantial corrections are announced publicly, with the correction extent and timing communicated when possible. Public database entries may be footnoted and BLS errata may be issued.


## 10. State JOLTS estimates

### 10.1 What is published

JOLTS publishes total nonfarm state estimates for all 50 states and the District of Columbia. State estimates include:

- Job openings.
- Hires.
- Quits.
- Layoffs and discharges.
- Total separations.

Other separations are generally not published for states because rates are low and variance estimates are relatively high. The state technical note states that other separations comprise less than 8 percent of total separations and are not published for states.

### 10.2 Why state estimates are model-based

The JOLTS sample of about 21,000 establishments does not directly support fully sample-based state estimates. State-supersector cells can have small respondent counts. Therefore, BLS combines available sample information with model-based estimates using other BLS data.

### 10.3 Four major state-estimate models

BLS describes four major models:

1. Composite Regional model: unpublished intermediate model.
2. Synthetic model: unpublished intermediate model.
3. Composite Synthetic model: published historical series through the most current benchmark year.
4. Extended Composite Synthetic model: published current-year monthly series.

### 10.4 Composite Regional model

The Composite Regional model uses:

- JOLTS microdata.
- JOLTS final weights, including sampling weights, NRAF, and other adjustments.
- Published JOLTS regional estimates.
- CES state-supersector employment.

The idea is to use direct JOLTS microdata when enough state-supersector respondents exist and supplement with regional estimates when respondent counts are low.

Respondent-count rules:

```text
if n >= 30: use JOLTS microdata-based estimate only
if n < 5:  use regional estimate only
if 5 <= n < 30: use composite weight n / 30 for JOLTS microdata and (30 - n) / 30 for regional estimate
```

State-supersector estimates are benchmarked to CES employment. State-supersector estimates are summed to total nonfarm. Regional sums of state estimates are benchmarked to published JOLTS regional estimates to stabilize estimates.

Limitation: state estimates can be volatile because national and regional JOLTS are based on a relatively small sample. States with seasonal patterns very different from their region, such as Alaska relative to the West region, can be difficult for a regional proxy approach.

### 10.5 Synthetic model

The Synthetic model uses QCEW linked longitudinal microdata, called QCEW-LDB, rather than JOLTS microdata. It converts monthly employment changes in QCEW-LDB into JOLTS-like hires and separations:

- Expanding QCEW-LDB records: employment growth is treated as hires; separations are zero.
- Contracting records: employment decline is treated as separations; hires are zero.
- Stable records: no hires or separations are attributed.

The QCEW-LDB summaries are ratio-adjusted to published JOLTS regional hires and total separations. Job openings are derived from the regional openings-to-hires ratio applied to modeled hires. Quits and layoffs/discharges are derived from regional shares of total separations components.

Limitations:

- Not intended for modeling individual QCEW-LDB records.
- Not prudent for populations of 30 or fewer establishments.
- Works best at the state level.
- State job openings and separations components are based on ratios common to the region, so state-specific differences in openings-to-hires or separations shares may not be detected.
- QCEW-LDB lags current JOLTS production by about 6 to 9 months, so the Synthetic model alone cannot produce current state estimates.

### 10.6 Composite Synthetic model

The Composite Synthetic model is like Composite Regional, but when JOLTS microdata are insufficient it uses Synthetic model estimates rather than published regional estimates.

Rules are analogous:

```text
if n >= 30: use JOLTS microdata-based estimate only
if n < 5:  use Synthetic model estimate only
if 5 <= n < 30: use composite weight n / 30 for JOLTS microdata and 1 - n / 30 for Synthetic estimate
```

State-supersector estimates are summed to total nonfarm and benchmarked so regional sums align to published JOLTS regional estimates.

Limitations are similar to the Synthetic model. Because QCEW-LDB lags, the Composite Synthetic model is not available for the most current months until QCEW data arrive.

### 10.7 Extended Composite Synthetic model

The Extended Composite Synthetic model projects Composite Synthetic estimates forward until QCEW-LDB data become available. It ratio-adjusts a prior Composite Synthetic state-industry estimate using the ratio of the current Composite Regional estimate to the Composite Regional estimate from the previous year.

Conceptually:

```text
extended_composite_synthetic_t = composite_synthetic_t_minus_12
                                 * (composite_regional_t / composite_regional_t_minus_12)
```

State estimates are then summed across industry. This model allows current-month state estimates without waiting for lagged QCEW-LDB.

Limitations:

- It is still model-based.
- It reflects current economic trends at the CES industry by JOLTS region level, and state-specific current trends only to the extent sufficient JOLTS microdata exist.
- Error measures are updated annually in June.

### 10.8 State variance estimates

The state technical note states that state variance estimates account for both sampling error and model error. BLS uses a small-area domain model with a Bayesian approach:

- QCEW-based JOLTS synthetic model data generate a prior distribution.
- JOLTS microdata and sample-based variance estimates at state and Census region level update the prior.
- State variances are estimated by drawing 2,500 estimates from the posterior distribution.

Practical implication: state JOLTS estimates should not be treated as equivalent to direct survey estimates. For state comparisons, use BLS standard errors/significant-change tables and be careful with small differences.


## 11. Public data access and flat-file schema

The JOLTS public flat files are available at:

```text
https://download.bls.gov/pub/time.series/jt/
```

### 11.1 Main files

Common files in the directory:

| File | Purpose |
|---|---|
| `jt.data.0.Current` | Current data, described by BLS as 9 years plus year-to-date estimates |
| `jt.data.1.AllItems` | All estimates |
| `jt.data.2.JobOpenings` | Job openings levels and rates |
| `jt.data.3.Hires` | Hires levels and rates |
| `jt.data.4.TotalSeparations` | Total separations levels and rates |
| `jt.data.5.Quits` | Quits levels and rates |
| `jt.data.6.LayoffsDischarges` | Layoffs and discharges levels and rates |
| `jt.data.7.OtherSeparations` | Other separations levels and rates |
| `jt.data.8.UnemployedPerJobOpeningRatio` | Unemployed persons per job opening ratio |
| `jt.series` | Series metadata and code components |
| `jt.industry` | Industry code mapping |
| `jt.state` | State and region code mapping |
| `jt.sizeclass` | Establishment size code mapping |
| `jt.dataelement` | Data element code mapping |
| `jt.ratelevel` | Rate or level code mapping |
| `jt.seasonal` | Seasonality code mapping |
| `jt.period` | Period code mapping |
| `jt.footnote` | Footnote mapping |
| `jt.area` | Area code mapping, typically all areas for JOLTS flat files |
| `jt.txt` | General file documentation |

### 11.2 Data-file columns

Data files use these fields:

```text
series_id
year
period
value
footnote_codes
```

Periods are monthly `M01` through `M12`. `M13` is annual.

All levels are in thousands. Rates are percentages, normally shown to one decimal place.

### 11.3 Series ID structure

A JOLTS series ID is 21 characters. Example:

```text
JTS000000000000000JOR
```

Breakdown:

```text
JT | S | 000000 | 00 | 00000 | 00 | JO | R
```

| Component | Length | Example | Meaning |
|---|---:|---|---|
| Survey abbreviation | 2 | `JT` | JOLTS |
| Seasonal code | 1 | `S` | Seasonally adjusted |
| Industry code | 6 | `000000` | Total nonfarm |
| State/region code | 2 | `00` | Total US |
| Area code | 5 | `00000` | All areas |
| Size class code | 2 | `00` | All size classes |
| Data element code | 2 | `JO` | Job openings |
| Rate/level code | 1 | `R` | Rate |

Thus, `JTS000000000000000JOR` means seasonally adjusted total nonfarm U.S. job openings rate for all areas and all size classes.

### 11.4 Data element codes

| Code | Element |
|---|---|
| `JO` | Job openings |
| `HI` | Hires |
| `TS` | Total separations |
| `QU` | Quits |
| `LD` | Layoffs and discharges |
| `OS` | Other separations |
| `UO` | Unemployed persons per job opening ratio |
| `UN` | Unemployment rate, present in mapping but not selectable in the current mapping |
| `R1` | First closing response rate |
| `R2` | Second closing response rate |

Note: `UO` and `UN` are not employer-reported JOLTS data elements in the same way job openings, hires, and separations are. They appear in the public data element mapping and should be treated as derived/contextual series.

### 11.5 Rate/level and seasonal codes

| Code | Meaning |
|---|---|
| `L` | Level, in thousands |
| `R` | Rate |
| `S` | Seasonally adjusted |
| `U` | Not seasonally adjusted |

### 11.6 Data ingestion guidance

For reproducible pipelines:

- Prefer official BLS flat files or the BLS Public Data API.
- Preserve `series_id`, `year`, `period`, `value`, and `footnote_codes` exactly.
- Parse series IDs into components and join mapping files for human-readable labels.
- Treat `M13` as annual; do not mix with monthly records unless intentionally analyzing annual data.
- Store levels as numeric values in thousands unless converting explicitly to persons.
- Store rates as percentages, not decimals, unless converting explicitly.
- Do not infer geography solely from industry labels; use `state_code`/region code and `industry_code`.
- Use `jt.data.0.Current` for fast current pipelines, but use `jt.data.1.AllItems` or item-specific files for historical reproducibility.
- Re-download history after annual benchmark revisions, not only the newest month.
- Keep snapshots of previously downloaded files when revision analysis matters.


## 12. Publication schedule and release structure

JOLTS estimates are published monthly at 10:00 a.m. Eastern Time on preannounced release dates.

Typical release timing:

- National estimates are published in the first week of the month or the last week of the previous month.
- State estimates are published within about 2 weeks of national estimates.

The national news release summarizes current preliminary data and revised previous-month data. It includes tables for total nonfarm, industry, region, and establishment size class depending on the table. State releases contain state-level total nonfarm estimates.

Annual national estimates for hires, quits, layoffs and discharges, other separations, and total separations are released with the January news release, which is issued in March. Annual state estimates for hires, quits, layoffs and discharges, and total separations are released in June.


## 13. Practical interpretation pitfalls for agents

### 13.1 Stock-flow confusion

Do not compare job openings levels to hires or separations as if all are same-period flows. Job openings are a point-in-time stock on the last business day; hires and separations are monthly flows.

### 13.2 Rate denominator confusion

Do not use employment alone as the denominator for the job openings rate. Use employment plus job openings. Use employment alone for hires and separations rates.

### 13.3 Published JOLTS employment

JOLTS employment is collected but not published as a JOLTS estimate. If a task needs employment denominators, use CES employment where appropriate or the BLS-provided rates, not an inferred JOLTS employment series unless the methodology explicitly requires it.

### 13.4 Employer-of-record rule

Do not assign temporary-help workers to client industries or client establishments for JOLTS concepts. Count them under the employer of record.

### 13.5 Internal transfers and promotions

Internal transfers or promotions within the same reporting location are not hires or separations. Transfers from other locations are hires; transfers to other locations are other separations.

### 13.6 Recall and layoff threshold

Recalls from layoff count as hires when the formal suspension from pay status lasted more than 7 days. Layoffs and discharges include formal suspensions lasting or expected to last more than 7 days.

### 13.7 Latest month is preliminary

The current month is preliminary and revised in the next release. Avoid statements that imply the current month is final.

### 13.8 Annual benchmark revisions are not small bookkeeping changes

Annual benchmarking can revise both seasonally adjusted and not seasonally adjusted series for 5 years because of CES benchmark updates, seasonal factor updates, and alignment effects. Always refresh historical data after a benchmark release.

### 13.9 Alignment limits independent net-flow interpretation

Because BLS aligns hires minus separations to CES net employment change, using JOLTS net flows as an independent check on CES job growth can be circular. JOLTS remains valuable for gross flows and labor-market churn, but the aligned net flow is constrained toward CES.

### 13.10 State estimates are modeled

State JOLTS estimates are model-based and not direct state survey estimates. They leverage regional JOLTS, CES, QCEW, and model extensions. Use caution for state rankings, month-to-month changes, and small differences.

### 13.11 Other separations at state level

Other separations are not published for states. Do not attempt to reconstruct state other separations as total separations minus quits minus layoffs/discharges unless the task explicitly accepts an unofficial residual, and label it as unofficial.

### 13.12 Seasonally adjusted values revise

JOLTS uses concurrent seasonal adjustment, so seasonally adjusted historical values can revise as new data arrive. Pipelines should support vintage tracking.

### 13.13 Mapping file metadata may lag methodology text

The flat-file dictionary is useful for schemas and series IDs, but some narrative text can be stale. Prefer current Handbook/technical notes for sample size and methodology.


## 14. Recommended agent workflow for JOLTS analysis

When answering or generating code for a JOLTS task:

1. Identify the requested data element: job openings, hires, total separations, quits, layoffs/discharges, other separations, or derived ratio.
2. Identify level versus rate.
3. Identify seasonal adjustment: seasonally adjusted or not seasonally adjusted.
4. Identify geography: U.S., region, state, or all areas.
5. Identify industry or size class.
6. Confirm whether the desired series is national/regional direct survey or state model-based.
7. Use the official BLS series ID when possible.
8. Use BLS levels/rates directly rather than recomputing rates unless a task requires custom calculations.
9. If calculating annual values, use BLS annual formulas.
10. For comparisons over time, account for preliminary and annual benchmark revisions.
11. For state estimates, mention model-based nature and use error measures for significance where possible.
12. For public reporting, cite the Handbook or technical note for definitions and the data release or flat file for values.


## 15. Common examples

### 15.1 Total nonfarm job openings rate, seasonally adjusted

```text
series_id = JTS000000000000000JOR
JT = JOLTS
S = seasonally adjusted
000000 = total nonfarm
00 = total US
00000 = all areas
00 = all size classes
JO = job openings
R = rate
```

### 15.2 Total nonfarm job openings level, seasonally adjusted

```text
series_id = JTS000000000000000JOL
```

Only the final component changes from `R` to `L`.

### 15.3 Total nonfarm hires level, not seasonally adjusted

```text
series_id = JTU000000000000000HIL
```

`U` indicates not seasonally adjusted, `HI` indicates hires, and `L` indicates level in thousands.

### 15.4 Total private quits rate, seasonally adjusted

```text
series_id = JTS100000000000000QUR
```

`100000` indicates total private, `QU` indicates quits, and `R` indicates rate.


## 16. Checklist for QA and validation

Before finalizing JOLTS analysis, verify:

- Are levels in thousands clearly labeled?
- Are rates percentages, not fractions?
- Is the latest month preliminary?
- Has the series been refreshed after the latest annual benchmark?
- Is the period monthly (`M01`-`M12`) or annual (`M13`)?
- Is the data seasonally adjusted or not seasonally adjusted?
- Are job openings interpreted as a stock and hires/separations as flows?
- Are state estimates described as model-based?
- Are state other separations avoided or labeled as unofficial if residualized?
- Are revisions considered when comparing with previously published values?
- Are CES/QCEW dependencies acknowledged when discussing benchmarking or alignment?
- Are size-class estimates limited to total private?
- Are special forms/industry rules considered for temporary help, PEOs, and education when relevant?


## 17. Minimal glossary

BMF: Benchmark factor used to ratio-adjust JOLTS weighted employment to CES employment.

CATI: Computer-Assisted Telephone Interviewing.

CES: Current Employment Statistics, the BLS establishment survey that provides employment estimates used for JOLTS benchmarking and alignment.

Churn: Hires plus separations, or more generally the gross labor-flow intensity used in parts of the JOLTS methodology.

Composite Regional model: State-estimation model combining JOLTS microdata with regional JOLTS estimates when state-supersector sample counts are small.

Composite Synthetic model: State-estimation model combining JOLTS microdata with Synthetic model estimates.

Extended Composite Synthetic model: Current-month state-estimation extension that projects Composite Synthetic estimates forward using Composite Regional ratios.

FRA: Federal Railroad Administration, provider of railroad establishments added to the JOLTS frame.

JOLTS: Job Openings and Labor Turnover Survey.

NAICS: North American Industry Classification System.

NRAF: Nonresponse adjustment factor used to inflate respondent weights for unit nonresponse.

QCEW: Quarterly Census of Employment and Wages, the administrative-record-based program that provides the main establishment universe/frame source.

QCEW-LDB: QCEW Longitudinal Database used in synthetic state-estimate modeling.

REGARIMA: Regression with autocorrelated errors model used in seasonal adjustment.

SWTE: Summed weighted total employment for a JOLTS estimation cell.

X-13-ARIMA-SEATS: Seasonal adjustment software used by BLS for JOLTS.
