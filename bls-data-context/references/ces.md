# CES National Estimates

This file summarizes the BLS Current Employment Statistics National program, with emphasis on the mechanics that matter when using CES National estimates in data pipelines, forecast systems, and explanatory agents.

Use this as project knowledge, not as a replacement for live BLS pages. For current-month estimates, current benchmark articles, current net birth-death forecasts, release calendars, or code lists, always re-check the official BLS URLs listed in the source inventory.

## Source inventory

Core BLS Handbook of Methods pages:

- Concepts: https://www.bls.gov/opub/hom/ces/concepts.htm
- Data sources: https://www.bls.gov/opub/hom/ces/data.htm
- Design: https://www.bls.gov/opub/hom/ces/design.htm
- Calculation: https://www.bls.gov/opub/hom/ces/calculation.htm
- Presentation: https://www.bls.gov/opub/hom/ces/presentation.htm

Additional BLS CES methodology and operational pages:

- Seasonal adjustment files and documentation: https://www.bls.gov/web/empsit/cesseasadj.htm
- CES net birth-death model page: https://www.bls.gov/web/empsit/cesbd.htm
- Current benchmark article: https://www.bls.gov/web/empsit/cesbmart.htm
- Length of pay periods in the CES survey: https://www.bls.gov/ces/publications/length-pay-period.htm
- Report forms: https://www.bls.gov/ces/report-forms/

Helpful official BLS data-access references:

- CES series ID format: https://www.bls.gov/help/hlpforma.htm#CE
- CES LABSTAT flat-file directory: https://download.bls.gov/pub/time.series/ce/
- CES flat-file dictionary: https://download.bls.gov/pub/time.series/ce/ce.txt
- CES published series page: https://www.bls.gov/web/empsit/cesseriespub.htm
- CES data access tips: https://www.bls.gov/web/empsit/cestips.htm

Source-date caveats:

- The BLS Handbook CES pages used here were last modified February 28, 2025.
- The CES birth-death page used here was last modified June 5, 2026, and should be preferred for current birth-death operational details.
- The length-of-pay-period publication was last modified August 4, 2023 and reports February 2023 point-in-time pay-period distributions.
- The report-forms page was last modified October 6, 2015; use it mainly for report-form structure and not for current sample statistics.

## Program identity and scope

CES-N is the national payroll survey program that publishes monthly estimates of employment, hours, and earnings by industry. It is one of the earliest monthly indicators of U.S. labor-market conditions.

The program is establishment based. A CES establishment is generally a single physical worksite engaged in one main economic activity. An establishment is not necessarily a firm or enterprise. Large firms can have many establishments.

CES-N measures nonfarm payroll jobs, not unique people. If a person holds two payroll jobs at two establishments and is paid for both during the reference period, the person can be counted twice. This is a core difference from the household survey/CPS, which measures people.

The reference period is the pay period that includes the 12th day of the month. It is not exactly the calendar month. This matters for strikes, severe weather, holiday placement, school calendars, government shutdowns, and other events that affect only part of a month.

CES-N excludes some worker groups, including proprietors, the unincorporated self-employed, unpaid family workers, unpaid volunteers, farm employment, private household/domestic employment, and the uniformed military. Government employment is civilian government employment; some intelligence/security agencies are excluded because they are outside the available sampling/benchmark sources.

CES uses 2022 NAICS in the current structure. CES industry codes mostly correspond to NAICS, but some CES industries combine multiple NAICS industries for estimation or publication.

## Key CES concepts and data types

Common employee groups:

- AE: all employees.
- PE: production employees in goods-producing industries and nonsupervisory employees in private service-providing industries.
- WE: women employees.

Common hours and earnings measures:

- AWH: average weekly hours.
- AHE: average hourly earnings.
- AWE: average weekly earnings.
- AWOH: average weekly overtime hours, published for manufacturing only.
- Aggregate weekly hours: employment multiplied by average weekly hours, with CES scaling conventions.
- Aggregate weekly payrolls: aggregate weekly hours multiplied by average hourly earnings, with CES scaling conventions.
- Real earnings: current-dollar earnings deflated by CPI measures and expressed in constant 1982-84 dollars.
- Diffusion indexes: measures of the breadth of employment increases or decreases across component industries.

Scope caveats:

- Hours and earnings data are for paid hours and paid earnings, not necessarily hours worked or labor cost.
- Hours include paid leave and other paid hours. They are not adjusted to an hours-worked concept.
- Payroll is before deductions and includes regular pay, overtime pay, pay for paid leave, and frequent commissions; it excludes irregular bonuses, retroactive pay outside the period, in-kind payments, and employer benefit costs.
- Overtime hours are collected and published only for manufacturing. Overtime hours are hours paid at premium rates and are not converted to straight-time equivalent hours.
- Government and educational establishments are limited in hours/earnings scope; do not assume hours or earnings exist for every employment series.

Basic identities:

```text
AWH = aggregate weekly hours / employees paid for those hours
AHE = aggregate weekly payroll / aggregate weekly hours
AWE = AWH * AHE
Aggregate weekly hours = employment * AWH
Aggregate weekly payrolls = aggregate weekly hours * AHE
```

For manufacturing AHE excluding overtime, CES removes an estimated overtime premium using a time-and-one-half assumption. Do not generalize this measure to nonmanufacturing industries.

## Practical data access and series IDs

CES National series IDs use the CE database prefix and encode seasonal adjustment, industry, and data type:

```text
Example: CEU0800000003
Positions 1-2: CE   = CES National database prefix
Position 3:    U/S  = not seasonally adjusted or seasonally adjusted
Positions 4-11: industry/supersector code
Positions 12-13: data type code
```

Common examples:

```text
CES0000000001 = total nonfarm, seasonally adjusted, all employees
CEU0000000001 = total nonfarm, not seasonally adjusted, all employees
CES0500000001 = total private, seasonally adjusted, all employees
CEU0500000003 = total private, not seasonally adjusted, average hourly earnings of all employees
```

Common data type codes:

```text
01 = all employees, thousands
02 = average weekly hours of all employees
03 = average hourly earnings of all employees
04 = average weekly overtime hours of all employees, manufacturing only
06 = production or nonsupervisory employees, thousands
07 = average weekly hours of production or nonsupervisory employees
08 = average hourly earnings of production or nonsupervisory employees
09 = average weekly overtime hours of production or nonsupervisory employees, manufacturing only
10 = women employees, thousands
11 = average weekly earnings of all employees
21 = 1-month diffusion index
22 = 3-month diffusion index
23 = 6-month diffusion index
24 = 12-month diffusion index
30 = average weekly earnings of production or nonsupervisory employees
```

Recommended flat-file workflow:

1. Pull metadata from `ce.series`, `ce.industry`, `ce.datatype`, `ce.supersector`, `ce.seasonal`, `ce.footnote`, and `ce.period` in `https://download.bls.gov/pub/time.series/ce/`.
2. Pull values from `ce.data.0.ALLCESSeries` when broad coverage matters, or use supersector-specific files for smaller downloads.
3. Join values to `ce.series` on `series_id`.
4. Parse periods as `M01` through `M12` for months. Treat `M13` as an annual average, not a month.
5. Preserve footnotes. Footnote codes can identify preliminary status, independent seasonal adjustment, or other special series status.
6. Store seasonal adjustment as a dimension. Do not mix `CES...` and `CEU...` in a single model unless the transformation is explicit.

Data precision in flat files and publications:

- Employment is in thousands. Higher aggregates are generally rounded to the nearest thousand. More detailed employment series can be stored to one decimal place, meaning nearest hundred jobs.
- AWH and AWOH are in hours rounded to one decimal.
- AHE and AWE are in dollars rounded to cents.
- Aggregated values should be recomputed from unrounded or BLS-published components only when the exact required precision is known. Rounding can create small discrepancies.

## Sampling frame and sample design

CES uses a sample of establishments drawn largely from the Longitudinal Database, which is derived from Quarterly Census of Employment and Wages unemployment-insurance records. The QCEW/LDB frame covers roughly 97 percent of the employment scope used for CES benchmarks. The remaining noncovered employment is estimated from other sources.

The sample is a stratified simple random sample of worksites, clustered by unemployment-insurance account. Private-sector sample strata combine state, industry, and establishment size. The design emphasizes precision for total nonfarm employment while still supporting detailed industry estimates.

Private establishments are stratified by broad industry groups and by eight size classes:

```text
0-9 employees
10-19
20-49
50-99
100-249
250-499
500-999
1,000+
```

Large units and some special units are selected with certainty. Government sample design is high coverage but not a standard probability sample in the same way the private sample is.

Important sample-maintenance details:

- New samples are drawn annually from the first-quarter LDB, with additional birth updates from the third-quarter LDB.
- Units generally remain in sample for at least two years.
- Units can rotate out after several years, with overlap retained to reduce discontinuities.
- Sample weights are inverse probabilities of selection and are adjusted for sample design and merged units.
- Large establishments are few but contain a large share of employment; small establishments are numerous but contain a smaller employment share. Weights are essential to avoid size bias.

Current sample size changes over time. Recent BLS operational pages describe a sample around 119,000 businesses and government agencies representing about 622,000 worksites. Older or topic-specific pages may cite about 122,000 businesses and 666,000 worksites. Prefer the latest BLS CES page when quoting current sample size.

## Data collection and respondent reporting

CES data are collected monthly from participating establishments. Federal participation is voluntary, but some states or territories have mandatory reporting rules for CES collection. Puerto Rico may appear in collection references but is excluded from CES National estimates.

Collection modes include electronic reporting, web, computer-assisted telephone interviewing, and other BLS collection channels.

Respondents report for the pay period including the 12th of the month. CES asks for all workers who received pay for any part of that pay period.

The core reported items vary by industry/report form, but commonly include:

- all employees;
- women employees;
- production or nonsupervisory employees where applicable;
- payroll;
- hours;
- commissions when relevant;
- overtime hours for manufacturing;
- length of pay period.

Report forms differ by industry and by whether the establishment has one pay group or two pay groups. A two-pay-group form is used when some workers at the same establishment are paid on different schedules.

The report-form categories shown by BLS include:

- mining and logging;
- construction;
- manufacturing;
- service-providing industries;
- educational services;
- public administration.

## Length-of-pay-period handling

CES publishes hours and earnings on a weekly basis, but establishments can pay weekly, biweekly, semimonthly, or monthly. Therefore, reported hours and payroll for nonweekly pay periods must be normalized to weekly equivalents.

BLS asks respondents for length of pay period because it affects the normalization of reported hours and earnings. CES can collect up to two pay-period lengths for an establishment.

The BLS length-of-pay-period publication is a point-in-time distribution, not a time series. In the February 2023 snapshot, biweekly pay was the most common among private establishments, followed by weekly, semimonthly, and monthly. These shares should not be treated as monthly observations.

Agent caveat: length-of-pay-period effects can affect hours and earnings, especially when pay periods are monthly or semimonthly and include different numbers of weekdays. CES seasonal adjustment has special adjustments for length-of-pay-period and 4-week versus 5-week survey-interval effects where appropriate.

## Microdata editing and screening

CES microdata pass automated and analyst-review edits before estimation.

Strict logical checks include examples such as:

- required all-employee data;
- production/nonsupervisory employees and women employees cannot exceed all employees;
- payroll and hours must be reported in paired combinations where needed;
- hours and earnings must satisfy plausible bounds;
- production/nonsupervisory hours or payroll should not exceed comparable all-employee values;
- overtime-hour values must be valid and cannot exceed total hours.

Non-strict edits flag unusual but not impossible values, such as unusually high hours, high hourly earnings, or inconsistent relationships between all-employee and production/nonsupervisory data.

Screening tests compare current reports with the respondent's own history. They are not primarily cross-sectional comparisons with other establishments. Analyst review can identify atypical reports, changed reporting basis, strikes, weather disruptions, special bonuses, or other events that should be handled separately.

Confidentiality is fundamental. Establishment-level microdata and many edit parameters are not public.

## Monthly estimation pipeline

At a high level, CES monthly estimates are built from:

1. reported sample microdata;
2. matched-sample over-the-month links;
3. weights;
4. imputation/handling for nonresponse and atypical observations;
5. net birth-death adjustment for all-employee employment;
6. aggregation;
7. seasonal adjustment;
8. monthly and annual revisions.

### Basic estimation cells

CES estimates are first computed in basic estimating cells, primarily detailed industries. Some cells include geographic stratification where needed, such as selected construction and government cells. Basic cells aggregate upward to major sectors, supersectors, total private, and total nonfarm.

### Matched sample

A matched sample is the set of units that reported usable data for both the current month and prior month. For a given data type, the establishment must have the required data in both months. Units that report zero employment because they are out of business are excluded from the matched link.

### All employees estimator

All-employee employment is estimated with a weighted link relative plus net birth-death adjustment. Conceptually:

```text
AE_t = AE_{t-1} * weighted_sample_link_t + net_birth_death_t
```

The weighted sample link measures the over-the-month change among matched continuing establishments. Atypical observations, such as major strikes or disaster-related disruptions, can be removed from the normal link and then added back to the current estimate so they do not distort the underlying trend.

### Production/nonsupervisory employees and women employees

PE and WE estimates are related to all-employees estimates through weighted sample ratios and link procedures. Treat PE and WE as modeled survey estimates, not as simple fixed proportions of all employees. Ratios can move over time and can be affected by sample composition.

### Hours and earnings estimators

Hours and earnings estimates use weighted sample relationships and composite/taper procedures. The purpose is to keep estimates responsive to sample movement while preventing excessive drift from the sample average.

Important caveat: non-AE hours and earnings series do not have a complete external monthly universe count equivalent to the QCEW employment benchmark. Annual benchmark revisions can still affect summary-level hours and earnings through updated employment weights and sample ratios, but the benchmarking mechanics are not the same as for all-employee employment.

### Small-domain model

For selected small industries with limited sample support, CES uses a small-domain model combining CES sample information with ARIMA projections based on QCEW trends. Examples in the BLS methods include lessors of nonfinancial intangible assets except copyrighted works, and tax preparation services. For these small modeled domains, sampling-error estimates may not apply in the usual way.

## Net birth-death model

The CES sample cannot immediately capture new business births because new establishments enter administrative frames with a lag. Business deaths can also be missed because closed establishments may stop responding. CES therefore uses a birth-death adjustment for all-employee employment.

The birth-death method has two broad components:

1. A sample-based component: out-of-business zero-employment reports are excluded from the matched link. Their employment remains in the estimate and helps offset missing employment from births not yet on the frame.
2. A model-based component: an ARIMA residual model uses historical differences between CES sample-based estimates and QCEW universe employment to forecast residual net birth-death employment.

Net birth-death forecasts are applied to not seasonally adjusted all-employee estimates. They are unique to month and industry and often display strong seasonal patterns. They can be positive or negative.

Critical agent caveat: do not compare a not seasonally adjusted net birth-death forecast directly with a seasonally adjusted over-the-month payroll change. If evaluating the contribution of net birth-death, compare it to not seasonally adjusted employment changes or to a properly transformed model.

Current-method caveat as of the June 2026 BLS birth-death page: effective with preliminary January 2026 estimates released in February 2026, BLS modified the ARIMA component by incorporating current sample information. The current method can change again; always check the CES birth-death page before implementing or explaining the latest operational method.

Birth-death forecasts do not correct all possible sources of sampling or nonsampling error. They are one part of the CES estimator, not a full reconciliation to future QCEW.

## Aggregation and publication structure

CES builds from detailed basic cells to summary industries. Common aggregate levels include:

- total nonfarm;
- total private;
- goods-producing;
- service-providing;
- private service-providing;
- major sectors such as mining and logging, construction, manufacturing, trade/transportation/utilities, information, financial activities, professional and business services, private education and health services, leisure and hospitality, other services, and government;
- more detailed NAICS/CES industry cells.

For all-employee and women-employee employment, total nonfarm is the highest aggregate. For hours and earnings, total private is usually the highest relevant aggregate because hours and earnings are private-sector measures.

Aggregation principles:

- Employment levels aggregate additively.
- AWH aggregates as an employment-weighted average of component AWH values.
- AHE aggregates as aggregate payroll divided by aggregate hours, not as a simple average of component AHE values.
- AWE is AWH multiplied by AHE.
- Rounding can create small differences between recomputed values and published values.

## Benchmarking and annual revisions

CES sample estimates are reanchored annually to more complete universe employment counts. The benchmark month is March. The main benchmark source is QCEW unemployment-insurance tax records, covering roughly 97 percent of benchmark employment. Noncovered employment is added from other sources.

Annual benchmark logic:

- The March not seasonally adjusted all-employee estimate is replaced by the benchmark universe count.
- The prior 11 months are revised by wedging the difference back to the previous benchmark.
- Months after the benchmark are recalculated using updated sample links and updated birth-death factors.
- Not seasonally adjusted data are generally revised for 21 months.
- Seasonally adjusted data are generally revised for 5 years, or longer if a series reconstruction requires it.
- Benchmark revisions are normally published with the January estimates in February.

PE and WE estimates are updated by applying sample ratios to revised all-employee levels. Hours and earnings at basic levels are generally not benchmarked in the same direct way as employment, but summary-level hours and earnings can change because employment weights and aggregation relationships change.

Noncovered employment estimation matters because QCEW does not cover all employment included in CES scope. BLS uses sources such as County Business Patterns, Annual Survey of Public Employment and Payroll, Railroad Retirement Board data, and state labor-market information. Corporate officers are a large noncovered group in some states because state unemployment-insurance coverage rules differ.

Current benchmark example as of the 2026 benchmark article:

- With January 2026 data released February 11, 2026, BLS incorporated the March 2025 benchmark.
- The seasonally adjusted March 2025 total nonfarm level was revised downward by 898,000, or 0.6 percent.
- The not seasonally adjusted March 2025 total nonfarm level was revised downward by 862,000, or 0.5 percent.
- Treat these as historical examples. They will be superseded by future benchmark articles.

Agent caveat: benchmark revisions are not just a correction to the latest month. They can alter growth rates, industry levels, seasonal factors, and historical interpretation over the revised span.

## Seasonal adjustment

CES seasonal adjustment removes normal recurring seasonal variation from selected series so that over-the-month movements are easier to interpret.

CES uses concurrent seasonal adjustment with X-13ARIMA-SEATS. Model choices are reviewed annually, while factors are recalculated as new data arrive. Monthly revisions to seasonally adjusted estimates can come from both new sample data and updated seasonal factors.

CES uses both direct and indirect seasonal adjustment:

- Some detailed series are directly adjusted.
- Some aggregates are indirectly adjusted by summing adjusted components.
- Some second-preliminary detailed series are independently adjusted but not used for aggregation.
- Some construction components are raked so residential and nonresidential specialty trade estimates align with their aggregate.

Special model adjustments can include:

- 4-week versus 5-week survey interval effects;
- length-of-pay-period effects for average hours and earnings;
- poll worker adjustment in local government excluding education around elections;
- floating holiday adjustments such as Good Friday and Labor Day where applicable;
- intervention/outlier handling from seasonal adjustment model specs.

Agent caveats:

- Use seasonally adjusted series for month-to-month economic interpretation.
- Use not seasonally adjusted series for benchmarking, birth-death comparisons, and direct reconciliation with raw administrative timing.
- Do not aggregate independently adjusted detailed second-preliminary series upward unless BLS specifies that the series are used in official aggregation.
- When BLS publishes updated seasonal adjustment files, model specs can show whether a series is additive, multiplicative, indirect, raked, or has special adjustments.

## Revisions and vintages

CES releases are vintage-sensitive.

Typical monthly vintage pattern:

- First preliminary: current reference month.
- Second preliminary: prior month, incorporating more sample receipts and corrections.
- Third/final sample-based estimate: two months prior.

Annual benchmark revisions then reanchor and revise a longer span.

For modeling and backtesting:

- Keep release vintages if the goal is real-time forecasting or nowcasting.
- Do not train a real-time model on fully benchmarked data and then evaluate as if those data were available in real time.
- For current-month explanatory agents, always label whether values are first preliminary, second preliminary, final sample-based, or benchmark-revised.
- Watch for unusual data-availability notes, such as missing collection-rate or real-earnings values during special events.

## Reliability and error measures

CES error has both sampling and nonsampling components.

Sampling error comes from using a sample rather than a full census. CES publishes standard errors and relative standard errors for selected estimates. BLS uses replication methods, including Fay's balanced half-sample approach, for variance estimation.

Nonsampling error includes reporting errors, nonresponse, classification issues, frame error, processing error, model error, and benchmark source differences. The annual benchmark revision is often used as a broad proxy for total survey error in employment, but it reflects differences between two estimation systems and should not be interpreted as a pure sampling-error measure.

Revision analysis should distinguish:

- ordinary monthly revisions from late reports and corrections;
- concurrent seasonal-adjustment revisions;
- annual benchmark revisions;
- historical reconstructions or errata;
- model changes such as birth-death model updates.

## Diffusion indexes

CES diffusion indexes measure the breadth of employment change across industries.

General method:

```text
industry employment decreased: 0
industry employment unchanged: 50
industry employment increased: 100
diffusion index = average of these coded values across component industries
```

Interpretation:

- 50 means equal balance between increasing and decreasing components, after allowing unchanged series.
- Above 50 means increases are more widespread than decreases.
- Below 50 means decreases are more widespread than increases.

CES uses seasonally adjusted employment for 1-, 3-, and 6-month diffusion indexes and not seasonally adjusted employment for 12-month diffusion indexes.

## Current benchmark and birth-death notes for 2026-era data

As of the BLS pages reviewed on June 18, 2026:

- The latest benchmark article available in the supplied sources was the benchmark incorporated with January 2026 estimates, published February 11, 2026.
- That benchmark revised March 2025 total nonfarm downward by 898,000 on a seasonally adjusted basis and 862,000 on a not seasonally adjusted basis.
- The current birth-death page notes an effective January 2026 modification to the ARIMA component that incorporates current sample information.
- The birth-death page and benchmark article should be treated as living operational pages; refresh them before using these notes in current analysis.

## Common pitfalls for AI agents

1. Jobs versus people: CES counts payroll jobs, not employed persons. Do not reconcile one-for-one with CPS employment.
2. Reference period: CES covers the pay period including the 12th, not the full calendar month.
3. Paid hours versus worked hours: CES hours are paid hours. Productivity or hours-worked applications need transformations outside basic CES.
4. NSA versus SA: birth-death forecasts and benchmarking are NSA concepts. Do not compare them directly to SA payroll changes.
5. Revision status: current-month CES data are preliminary. Always label vintage.
6. Benchmark status: benchmarked historical data can materially differ from initially published data.
7. QCEW relationship: QCEW is the main benchmark source, not the same thing as CES. QCEW is less timely, administrative, and coverage differs.
8. Noncovered employment: CES benchmarks include estimates for workers not covered by QCEW/UI records.
9. Hours/earnings scope: do not assume hours and earnings exist for government or all employment aggregates.
10. Aggregation: AHE is not a simple average of component AHE values. Use aggregate payroll divided by aggregate hours or BLS-published aggregate.
11. Rounding: published values can differ from recomputed values because BLS uses internal precision and then rounds.
12. PE and WE: production/nonsupervisory and women-employee estimates are not simple fixed ratios to all employees.
13. NAICS/CES code mapping: CES industry codes can combine NAICS industries. Use BLS mapping files.
14. Seasonal adjustment aggregation: do not aggregate independently adjusted detailed series unless BLS marks them as aggregation components.
15. Pay-period normalization: hours/earnings are weeklyized from weekly, biweekly, semimonthly, or monthly payroll reports.
16. Overtime: overtime hours exist for manufacturing only and are premium hours, not straight-time equivalents.
17. Real earnings: real earnings use CPI deflators and are in constant 1982-84 dollars; do not mix with nominal earnings.
18. Sample size: quote current sample counts only after checking the latest BLS CES pages because sample counts change.
19. Small domains: some industries use small-domain models; sampling-error tables may not apply the same way.
20. Current pages: benchmark and birth-death pages change over time. Always refresh them for current analysis.

## Suggested agent workflow for answering CES questions

When asked about a CES National series:

1. Identify whether the user needs CES National or CES State and Area.
2. Identify whether the needed data are seasonally adjusted or not seasonally adjusted.
3. Identify industry/CES code and data type code from official metadata.
4. Retrieve values from BLS API or LABSTAT flat files.
5. Preserve period, vintage, footnotes, and preliminary status.
6. For month-to-month economic interpretation, prefer seasonally adjusted data.
7. For benchmark or birth-death reconciliation, use not seasonally adjusted data.
8. For hours/earnings, verify employee group, private-sector scope, pay-period issues, and whether overtime applies.
9. For historical comparisons, check whether a benchmark, NAICS reconstruction, erratum, or discontinuation affects the span.
10. State caveats in plain language: payroll jobs, pay period including the 12th, preliminary/revised status, SA/NSA basis.

When asked to forecast CES:

1. Decide whether the target is first-preliminary, final sample-based, benchmark-revised, or latest-available data.
2. Use vintage data if evaluating real-time performance.
3. Model SA and NSA separately. Do not train on SA and then append raw NSA birth-death factors.
4. Include release-calendar effects, survey interval effects, strikes, weather, government shutdowns, Census workers, school calendars, and major benchmark/model changes as candidate regressors or interventions.
5. Consider QCEW-based benchmark drift if forecasting benchmark-revised levels, but account for QCEW publication lag.
6. Treat the pandemic and other extreme events as intervention regimes rather than ordinary outliers.
7. Report uncertainty in payroll jobs and in thousands, consistent with CES units.

When reconciling CES to QCEW:

1. Use March benchmark months as anchors.
2. Align industry classification and ownership scope.
3. Account for noncovered employment in CES.
4. Recognize QCEW publication lag and benchmark timing.
5. Use NSA CES for direct benchmark comparisons.
6. Expect post-benchmark months to be recomputed from benchmark base using sample links and updated birth-death factors.

## Minimal glossary

```text
AE: all employees
AHE: average hourly earnings
AWH: average weekly hours
AWE: average weekly earnings
AWOH: average weekly overtime hours
BLS: Bureau of Labor Statistics
CES-N: Current Employment Statistics - National
CES-SA: Current Employment Statistics - State and Area
CPS: Current Population Survey
LDB: Longitudinal Database, based largely on QCEW UI records
NAICS: North American Industry Classification System
NBD: net birth-death adjustment
NSA: not seasonally adjusted
PE: production or nonsupervisory employees
QCEW: Quarterly Census of Employment and Wages
SA: seasonally adjusted
UI: unemployment insurance
WE: women employees
X-13: X-13ARIMA-SEATS seasonal adjustment software
```

## Implementation notes for code agents

Preferred normalized schema for CES flat files:

```text
series_id string
seasonal string              # S or U
industry_code string          # 8 chars
industry_name string
supersector_code string
data_type_code string         # 2 chars
data_type_text string
year int
period string                 # M01-M13
month int nullable            # 1-12; null for M13 annual average
value numeric
footnote_codes string nullable
begin_year int
begin_period string
end_year int
end_period string
```

Recommended checks:

```text
assert series_id starts with "CE"
assert seasonal in {"S", "U"}
assert period in M01-M13
if period == "M13": month is null and observation is annual average
if data_type_code in {"04", "09", "20", "37", "58", "83"}: verify manufacturing or published scope
if series_id starts with "CES": treat as seasonally adjusted
if series_id starts with "CEU": treat as not seasonally adjusted
```

Parsing hint:

```text
seasonal = series_id[2]
industry_code = series_id[3:11]
data_type_code = series_id[11:13]
```

Do not hard-code the set of published industries or data types. Read `ce.series`, `ce.industry`, and `ce.datatype` because published series and metadata can change.
