# Employment Cost Index (ECI)

This file summarizes the BLS Employment Cost Index (ECI) from the listed BLS Handbook of Methods chapters and related BLS Monthly Labor Review (MLR) and research papers. It is written for AI-agent use: definitions are normalized, source status is flagged, and common caveats are included.

## 1. Core definition and purpose

The Employment Cost Index (ECI) is a quarterly Principal Federal Economic Indicator that measures change over time in the hourly labor cost to employers. It is designed to measure a "pure" change in labor costs by holding constant a fixed basket of labor and therefore removing the effects of employment shifts across broad industry and occupation categories.

The ECI covers:

- Total compensation.
- Wages and salaries.
- Employer costs for employee benefits.

The BLS publishes ECI estimates as:

- Index values.
- 3-month percent changes.
- 12-month percent changes.
- Seasonally adjusted and not seasonally adjusted series.
- Current-dollar and constant-dollar (real) series.

All current ECI index estimates use a base period of **December 2005 = 100.0**.

Operational formulas for percent changes:

```text
3-month percent change at quarter t = 100 * (I_t / I_{t-1} - 1)
12-month percent change at quarter t = 100 * (I_t / I_{t-4} - 1)
```

## 2. Data source and collection

### 2.1 Source survey

The ECI is produced from microdata collected by the **National Compensation Survey (NCS)**. The NCS is a voluntary, establishment-based survey. Its ECI/ECEC update collection covers the pay period that includes the 12th day of March, June, September, and December. BLS field economists conduct updates over a roughly 6-week period for each reference period.

The same NCS data infrastructure supports multiple BLS compensation products, including:

- ECI: change in compensation costs over time.
- Employer Costs for Employee Compensation (ECEC): employer compensation cost levels in dollars or cents per hour.
- Employee Benefits: incidence/provisions/access data.

### 2.2 Collection mode

BLS field economists collect data through conversational interviews and employer records rather than a fixed paper or online questionnaire. Collection methods include personal visit, mail, telephone, and email. Field economists use documents such as payroll records, job descriptions, and benefit plan documents.

### 2.3 Information collected

At initiation and updates, field economists attempt to collect:

- Establishment primary business activity and correct NAICS industry code.
- Employee lists or job titles and employee counts.
- Sampled jobs/occupations and the number of employees in each sampled job.
- Occupational attributes: bargaining status, full-time or part-time status, and time- or incentive-based pay.
- Wages and salaries for sampled jobs, updated from payroll records covering the 12th of the reference month.
- Work-level information: tasks, knowledge required, controls and complexity, contacts, and environmental conditions.
- Usual work schedule and typical hours.
- Employer-sponsored benefit availability, plan documents, benefit costs, and benefit incidence/provisions.
- Benefit usage, including induced usage when changes to plan provisions or costs change usage.

For hours-based or wage-related benefits, such as paid leave, field economists gather hours/days of benefit use and calculate employer cost from the relevant contribution or compensation rate. For benefits not directly linked to wages/hours, such as insurance, field economists collect plan participation/contribution information.

### 2.4 Confidentiality

NCS data are collected only for statistical purposes. Published estimates are screened to prevent disclosure of identifiable respondent information.

## 3. Scope and exclusions

### 3.1 Ownership sectors

ECI ownership categories:

- **Civilian workers**: private industry workers plus state and local government workers.
- **Private industry workers**: workers in private establishments, subject to exclusions below.
- **State and local government workers**: workers in state and local government establishments.

### 3.2 Exclusions

Civilian worker scope excludes:

- Volunteers and unpaid workers.
- Individuals receiving long-term disability compensation.
- Individuals working overseas.

Private industry scope excludes:

- Workers in private households.
- Self-employed workers.
- Workers who set their own pay, such as proprietors, owners, major stockholders, and partners in unincorporated firms.
- Family members paid token wages.
- Agricultural sector workers.

State and local government scope excludes:

- Federal government workers.
- Quasi-federal agency workers.
- Military personnel.

Geographic scope for national estimates includes the 50 states and District of Columbia, including Alaska and Hawaii, and excludes U.S. territories such as Puerto Rico, American Samoa, Guam, the Northern Mariana Islands, and the U.S. Virgin Islands.

## 4. Classification and publication dimensions

ECI estimates are classified by:

- Ownership: civilian, private industry, state and local government.
- Compensation component: total compensation, wages and salaries, benefits.
- Industry: NAICS.
- Occupation: SOC.
- Geography: census region, census division, and selected MSAs/CSAs.
- Worker/establishment characteristics: bargaining status, basis of pay, and other published domains.

Current Handbook notes:

- Establishments are classified by NAICS.
- Workers are classified by SOC.
- MSA/CSA definitions are from OMB.
- ECI data are available for the 15 largest MSAs/CSAs.

### 4.1 Census geography used in concepts

Census regions:

- Northeast: New England and Middle Atlantic.
- South: South Atlantic, East South Central, and West South Central.
- Midwest: East North Central and West North Central.
- West: Mountain and Pacific.

Census divisions:

- New England.
- Middle Atlantic.
- South Atlantic.
- East South Central.
- West South Central.
- East North Central.
- West North Central.
- Mountain.
- Pacific.

## 5. Compensation concepts

### 5.1 Total compensation

Total compensation equals employer costs for wages and salaries plus employer costs for employee benefits.

### 5.2 Wages and salaries

Wages and salaries are regular payments from employer to employee as compensation for services performed during a specific period or based on production, sales, or specific output.

Included in wages and salaries:

- Incentive-based pay, including commissions, production bonuses, and piece rates.
- Cost-of-living allowances.
- Hazard pay.
- Payments of income deferred because of participation in a salary-reduction plan.
- Accrued longevity pay.
- Deadhead pay for transportation workers returning in a vehicle without freight or passengers.

Excluded from wages and salaries:

- Uniform and tool allowances.
- Free or subsidized room and board.
- Payments made by third parties, such as tips.
- On-call pay.
- Retroactive pay.
- Lump-sum nonaccrued longevity pay.

Classified as benefits, not wages and salaries:

- Shift differentials.
- Premium pay for overtime, holidays, and weekends.
- Nonproduction bonuses, such as year-end and profit-sharing bonuses.

### 5.3 Benefits

The ECI captures employer costs of benefits in five major categories:

1. Paid leave: vacation, holiday, sick, and personal leave.
2. Supplemental pay: overtime and premium pay, shift differentials, and nonproduction bonuses.
3. Insurance: life, health, short-term disability, and long-term disability.
4. Retirement and savings: defined benefit and defined contribution plans.
5. Legally required benefits: Social Security, Medicare, federal and state unemployment insurance, and workers' compensation.

Healthcare benefits include preventive and protective medical, dental, vision, or prescription drug coverage for employees and dependents, including spouses and children.

### 5.4 Bargaining and pay basis

A worker is classified as a union worker when all of the following are true:

- A labor organization is recognized as bargaining agent for all workers in the occupation.
- Wage and salary rates are determined through collective bargaining or negotiations.
- Settlement terms on earnings provisions are included in a signed, mutually binding collective bargaining agreement.

Incentive-based pay means wages and salaries at least partly based on productivity payments such as production bonuses, commissions, piece rates, sales, output, or other production-based incentives. Nonproduction bonuses are benefits.

Time-based pay means wages and salaries based solely on a time unit, such as an hourly rate or annual salary. Straight-time/base rates are time-based rates.

## 6. Current sample design

### 6.1 Current design status

Use the current BLS Handbook of Methods design page for current design details. The current Handbook describes NCS data collection for ECI as a national probability sample selected in two stages:

1. Establishments.
2. Occupations/jobs within sampled establishments.

The 2010 research paper summarized an older/current-at-the-time three-stage area-establishment-job design and should be treated as historical design research unless the current Handbook corroborates a detail.

### 6.2 Stage 1: establishments

Current Handbook stage 1:

- The sample is selected using probability proportional to size (PPS).
- Larger establishments have a greater probability of selection.
- Establishments in all 50 states and the District of Columbia are eligible.
- The sampling frame is built from Quarterly Census of Employment and Wages (QCEW) state unemployment insurance reports.
- The most recent available reference period at sample selection is used.

Industry/area sampling cells:

- 5 aggregate industry strata.
- 24 geographic subsets.
- 120 sampling cells total.
- The 24 geographic subsets are the 15 largest metropolitan areas plus the remaining portions of each of the 9 census divisions.

### 6.3 Sample rotation

Current Handbook rotation:

- Five sample rotation groups:
  - Three private industry groups.
  - One state and local government group.
  - One aircraft manufacturing group.
- Private industry and aircraft manufacturing establishments are rotated approximately every 3 years, except in years when state and local government establishments are rotated.
- State and local government establishments are rotated approximately every 10 years.
- Each private industry group is one-third of the private sample; rotation is staggered so only one private group rotates out in a given year.
- Rotation reduces respondent burden and keeps the sample current.

### 6.4 Stage 2: occupations/jobs within establishments

Current Handbook stage 2 uses probability selection of occupations (PSO). Field economists obtain a complete employee list and job titles, then randomly select jobs with probability proportional to the number of workers in the job.

Number of selected jobs by establishment size:

| Establishment employment | Jobs selected |
|---:|---:|
| 1-49 | Up to 4 |
| 50-249 | 6 |
| 250 or more | 8 |

Exceptions:

- State and local government establishments: up to 20 jobs.
- Aircraft manufacturing industry (NAICS 336411): up to 32 jobs.

After selection:

- Jobs are classified by actual job duties and responsibilities, not job title or required education.
- Jobs use 6-digit SOC codes.
- Military occupations are excluded from the NCS occupational groups.
- Each selected occupation must be homogeneous in recorded attributes: full-time/part-time status, union/nonunion status, time/incentive pay basis, and work level.

A **quote** is a sampled occupation/job observation within an establishment, identified across quarters by establishment, detailed occupation or occupation group, worker attributes, pay basis, bargaining status, full-time/part-time status, and work level. The ECI tracks establishment jobs/quotes, not individual workers.

## 7. Weighting, nonresponse, imputation, and benchmarking

### 7.1 Weight types

Two important weight concepts:

- **Sample quote weights**: reflect establishment employment, sampled occupation employment, and probability of selection. These are used to estimate average wages/benefit costs within cells from the survey sample.
- **Fixed employment weights**: represent occupational-industry employment counts at one point in time and are held constant until the next reweight. Current Handbook says these employment levels come from the Occupational Employment and Wage Statistics (OEWS) program.

Note on naming: the 2016 MLR article used the then-current name Occupational Employment Statistics (OES). The current BLS program name is Occupational Employment and Wage Statistics (OEWS).

### 7.2 Usable occupation and unit response

An establishment is considered responding if it provides information on at least one usable occupation. A selected occupation is usable if it has:

- Occupational attributes: full-time/part-time, union/nonunion, and time/incentive pay basis.
- Work schedule.
- Wage data.

Wage data are essential because wages account for roughly 70 percent of compensation and many benefit-cost estimates are linked to wages.

### 7.3 Unit nonresponse adjustment

If an establishment refuses or cannot provide any usable occupation data, it is an establishment/unit nonrespondent. Unit nonresponse adjustments redistribute weights from nonrespondents to responding establishments in similar ownership, industry, size class, and area categories.

### 7.4 Quote nonresponse adjustment

Quote nonresponse occurs when an establishment refuses to provide wage data for a selected occupation/quote. During initiation, quote nonresponse is handled by redistributing quote weights to responding sample quotes in similar occupational group, ownership, industry, size class, and area categories. During update, quote nonresponse is addressed through imputation.

### 7.5 Item imputation

Item nonresponse occurs when an establishment responds but cannot or will not provide some benefits data for a sampled occupation.

Rules:

- Benefits can be imputed at initiation and updates.
- Wage and salary cost data are not imputed for item nonresponse at initiation.
- Wage and salary cost data can be imputed at later updates.

For update wage imputation, BLS estimates a rate of change for wages and salaries from similar establishments/occupations that reported wage data in both periods. The estimated rate is applied to the establishment's earlier reported wage/salary value.

### 7.6 Benchmarking/poststratification

Benchmarking adjusts each quote's survey weight so the survey matches the base-quarter distribution of employment by industry and occupational group. The benchmark cells are the ECI basic cells used in index calculation.

## 8. ECI index calculation

### 8.1 Modified Laspeyres structure

The current ECI is a modified Laspeyres index. It uses a standard fixed-weight index framework, modified for the ECI's sample design and statistical conditions.

Intuition:

- The ECI asks how employer labor costs would have changed if the industry-occupation composition of employment had remained fixed.
- It aggregates changes in hourly compensation within narrowly defined cells, using fixed wage or benefit bills as weights.
- It uses matched quotes to estimate quarter-to-quarter change within cells.

### 8.2 Basic cells

A basic cell is a narrow grouping of workers by ownership sector, industry, and occupational group.

Current Handbook cell structure:

- Private industry: 59 industry categories x 9 occupational groups = 531 cells.
- State government: 13 industry categories x 9 occupational groups = 117 cells.
- Local government: 13 industry categories x 9 occupational groups = 117 cells.
- Total: 765 ECI basic cells.

If a cell has too few quotes for reliable estimates of mean costs, link relatives, or apportionment factors, the estimate may be replaced by an estimate from a larger collapsed cell.

### 8.3 Matched quotes

A matched quote has current-quarter and previous-quarter wage or benefit data for the same sampled job/quote. The ECI uses matched quotes in the ratio of current to previous average cost. This helps avoid measuring changes caused by different sampled jobs or worker reassignment rather than changes in labor costs for comparable jobs.

Important caveat: the ECI tracks costs for jobs in establishments, not the wage path of individual people. Data are collected for incumbents in a job even when the incumbents change.

### 8.4 Simplified modified Laspeyres formula

For cell `c` and quarter `t`, define:

```text
B_c0  = fixed base-period wage bill or benefit bill for cell c
       = fixed employment in cell c * base-period average hourly wage/benefit cost

r_ct  = current-quarter weighted average cost for matched quotes in cell c
        ---------------------------------------------------------------
        previous-quarter weighted average cost for matched quotes in cell c

A_ct  = accumulated cell cost change from base to quarter t
       = A_c,t-1 * r_ct, with A_c0 = 1

I_t   = 100 * [sum over c of B_c0 * A_ct] / [sum over c of B_c0]
```

For wage indexes, `B_c0` is a wage bill. For benefit indexes, it is a benefit bill. For total compensation, the cost weight is the sum of the wage/salary and benefit cost weights.

### 8.5 Five calculation steps

The current Handbook describes five main steps:

1. Calculate a weighted average wage or benefit cost for each basic cell in the current and previous quarters, using matched quotes and sample quote weights.
2. Calculate the ratio of current-quarter to previous-quarter weighted average cost for each cell, then multiply by the prior cumulative cell change.
3. Generate a current-quarter wage/benefit bill by multiplying the cumulative change by the base-period wage/benefit bill.
4. Sum current-quarter and base-period bills across all cells in the index domain and divide summed current-quarter bill by summed base-period bill.
5. Multiply by 100 to get the index, then divide by the previous-quarter index to obtain the quarter-to-quarter link relative.

### 8.6 Aggregates, subindexes, and comparability limits

Aggregate civilian, private, state and local government, industry, occupation, and MSA/CSA indexes use fixed employment weights.

Some domains are handled differently because the sample is not large enough to hold wage/benefit bills constant at the most detailed level:

- Census region/division indexes.
- Union/nonunion indexes.
- Time-paid/incentive-paid or excluding-incentive-worker indexes.

For these, the previous-quarter sample distribution is used to apportion the previous wage/benefit bill within each ownership-industry-occupation cell. Because their weights can vary over time, these indexes are **not strictly comparable** to aggregate, industry, occupation, and MSA/CSA indexes.

## 9. Constant-dollar (real) ECI

Constant-dollar ECI estimates adjust nominal/current-dollar ECI values for consumer price changes.

Current BLS method:

```text
Rebased CPI-U_t = CPI-U_t / CPI-U_December_2005
Real ECI_t      = Nominal ECI_t / Rebased CPI-U_t
```

National ECI series are adjusted using CPI-U for all items. Regional ECI series use the corresponding not-seasonally-adjusted current-dollar index divided by the rebased CPI-U.

Interpretation: constant-dollar ECI measures changes in real employer compensation costs after removing consumer price inflation as measured by CPI-U.

## 10. Seasonal adjustment

### 10.1 What seasonal adjustment does

Seasonal adjustment estimates and removes recurring within-year patterns, making it easier to see underlying labor-cost trends. Seasonal adjustment is an approximation based on historical patterns, and seasonally adjusted estimates have a similar margin of error as the underlying not-seasonally-adjusted data.

### 10.2 Method

BLS uses the Census Bureau's X-13ARIMA-SEATS seasonal-adjustment software.

ECI seasonal adjustment can be:

- **Direct**: divide an unadjusted index by its seasonal factor.
- **Indirect/composite**: compute a weighted sum of seasonally adjusted component indexes; weights come from the index weights.

General pattern:

- Lower-level series, such as construction wages, tend to be directly adjusted.
- Higher-level aggregate indexes, such as civilian wages and salaries, generally use indirect seasonal adjustment.
- Industry and occupational series adjusted indirectly are based on adjusted industry or occupational components.

### 10.3 Revisions and publication

At the beginning of each calendar year:

- Seasonal adjustment factors are calculated for the coming year.
- Seasonally adjusted historical data are revised for the most recent 5 years.
- Directly adjusted seasonal factors for the coming year are published with the March publication.
- BLS reviews all published series for seasonality using the most recent 10 years of estimates.
- Series can be added or dropped from seasonally adjusted publication depending on whether stable, identifiable seasonality is present.

Not-seasonally-adjusted ECI series are final upon publication. Seasonally adjusted series are subject to annual revision for the most recent 5 years.

### 10.4 2024 MLR findings on seasonality

The 2024 MLR article reports:

- Each quarter, ECI publishes 3-month percent-change estimates for 132 worker domains.
- Total compensation and wages/salaries are published for all 132 domains; total benefits are published for 14 domains. That yields 278 published 3-month percent-change estimates per quarter.
- About half of these published estimates are seasonally adjusted or eligible for seasonal adjustment.
- No estimates defined by census region/division, bargaining status, or basis of pay are seasonally adjusted.
- As of the March 2023 seasonal-factor revision, 2 of 136 eligible series did not meet stable/identifiable seasonality criteria and therefore were not published as seasonally adjusted.

The article's central finding is that seasonal adjustment usually has a small effect on the most aggregate ECI 3-month percent changes. For civilian total compensation during March 2014-December 2023, differences between seasonally adjusted and unadjusted estimates were generally about 0.1 to 0.2 percentage point.

Average differences for civilian workers, March 2014-December 2023, seasonally adjusted minus unadjusted:

| Reference-period change | Total compensation | Wages and salaries | Total benefits |
|---|---:|---:|---:|
| December-March | -0.15 | -0.11 | -0.24 |
| March-June | 0.00 | -0.01 | 0.04 |
| June-September | -0.06 | -0.08 | 0.00 |
| September-December | 0.20 | 0.20 | 0.21 |

The 2024 article explains that ECI seasonality is smaller than seasonality in CES average hourly earnings because ECI holds industry-occupation employment composition fixed, while CES average hourly earnings can move with month-to-month employment shifts across industries.

Domains with larger seasonal adjustments include some finance and insurance industries, educational services, and utilities.

## 11. Reliability, standard errors, and validation

### 11.1 Error types

ECI estimates can have:

- Sampling error: error because the sample is only part of the population.
- Nonsampling error: data collection, processing, response, and other non-sampling sources.

Standard errors measure sampling variability. Approximate interpretation:

- About 68 percent of possible sample estimates are within 1 standard error of the complete-population figure.
- About 90 percent are within 1.6 standard errors.

BLS comparison statements in ECI publications are significant at 1.6 standard errors or better. Published standard errors are available for ECI estimates excluding seasonally adjusted series. The current Handbook says standard errors of the original not-seasonally-adjusted series can be used to approximate precision for the corresponding seasonally adjusted estimates.

### 11.2 Balanced repeated replication (BRR)

ECI standard errors use a variation of balanced repeated replication (BRR):

- The sample is partitioned into 120 variance strata.
- Each variance stratum is split into two variance primary sampling units (PSUs).
- Balanced half-samples are formed.
- Replicate estimates are computed using adjusted final weights.
- 120 replicates are used.
- Fay's method uses `k = 0.5`; half-sample units receive multiplier 1.5, and non-half-sample units receive multiplier 0.5.

### 11.3 Quality assurance and validation

BLS mitigates nonsampling error through:

- Data collection reinterviews.
- Observed interviews.
- Computer edits.
- Systematic professional review.
- Extensive field economist training.
- Estimate validation against historical trends, economic conditions, legislation, labor-management disputes, sample composition, sample rotation, compensation structure, and other evidence.

## 12. Presentation, access, and revisions

### 12.1 Releases and products

Primary ECI publication:

- Released quarterly in January, April, July, and October.
- Includes summary text, data tables, and a technical note.
- Tables include index values, 3-month percent changes, and 12-month percent changes.

Other access points:

- BLS ECI homepage.
- News releases and archives.
- BLS database tools.
- Historical tables/spreadsheets.
- Standard errors.
- Seasonal factors.
- Interactive charts.

Historical tables include seasonal, nonseasonal, and continuous indexes. BLS says continuous indexes were deemed continuous across prior classification systems (SIC and OCS) and current systems (NAICS and SOC), with data dating back to 1975.

### 12.2 Corrections and revisions

- Not-seasonally-adjusted ECI series are final upon publication.
- Seasonally adjusted series are revised annually for the most recent 5 years.
- If an error is found, BLS corrects and republishes the affected product and notes the correction on the publication, program homepage, and BLS errata page.

### 12.3 Special tabulations and microdata

- ECI does **not** produce state-level estimates; the NCS is not designed for state estimates.
- Special tabulations are evaluated based on resources, complexity, reliability, and confidentiality.
- If a special tabulation is cited, cite it as an unpublished BLS/NCS/ECI estimate with the reference period.
- ECI microdata are available only on a limited basis through BLS Restricted Data Access for valid statistical research.

## 13. Uses and common interpretation issues

### 13.1 Uses

Private-sector uses include:

- Collective bargaining negotiations.
- Evaluating changes in benefit package costs.
- Analyzing contract settlements.
- Wage and salary administration.
- Adjusting wages or labor costs in long-term contracts.

Public-sector uses include:

- Public policy formulation and assessment.
- Collective bargaining.
- Evaluating benefit package costs.
- Analyzing contract settlements.
- Indexing some payments or reimbursements.
- Monetary policy analysis.

BLS examples include active-duty military pay adjustments, federal white-collar pay adjustments under FEPCA, Medicare reimbursement adjustments, government contract escalator clauses, and state minimum-wage escalation.

### 13.2 ECI vs ECEC

Do not confuse ECI and ECEC.

| Measure | Main purpose | Output | Employment weights |
|---|---|---|---|
| ECI | Change in employer labor costs over time | Indexes and percent changes | Fixed employment weights for core aggregate/industry/occupation indexes |
| ECEC | Level of employer compensation costs | Dollars/cents per hour worked | Current employment distribution |

ECEC uses the same NCS data infrastructure but measures cost levels at a point in time. ECI measures change in costs over time.

### 13.3 ECI vs CES average hourly earnings or productivity compensation per hour

The ECI holds industry-occupation composition fixed for core series, so it is less affected by employment shifts across industries and occupations. Measures such as CES average hourly earnings or productivity compensation per hour can be affected by employment shifts because they are current-composition averages or aggregate compensation divided by aggregate hours.

### 13.4 Employer cost vs employee value

The ECI measures employer costs, not employee utility or employee valuation. Employer cost of a noncash benefit can differ from employee value because of tax treatment, uniform benefit provision, heterogeneous employee preferences, and legally required benefits.

## 14. Historical and research context from supplied papers

### 14.1 2001 MLR: "The Employment Cost Index: what is it?"

Status: conceptual/historical context. Some definitions remain useful, but verify any current coverage rules against the current Handbook.

Key points:

- The ECI is a quarterly measure of the change in the price of labor, defined as compensation per employee hour worked.
- It is watched as an indicator of labor-cost pressure that can lead to price inflation.
- It covers wages, salaries, and a broad set of benefits.
- It is a fixed-weight/Laspeyres-type index that controls for changes in industry-occupation employment composition.
- The article emphasizes BLS's preference for a **rate-and-usage** approach for benefits: estimate current costs under current plan provisions and fixed usage/participation assumptions, rather than using past expenditures whenever possible.
- For many benefits, eligibility/participation/usage are held constant from initiation unless plan provisions change; this helps remove workforce-composition changes from measured cost changes.
- Infrequent payments, such as bonuses, were described as carried forward from the payment quarter into subsequent quarters until a new payment occurs. This avoids spikes but can obscure the timing of cost increases and assumes persistence of the payment.
- The article discusses why the ECI is often less cyclically variable than average hourly earnings: it holds industry-occupation composition fixed and, in the historical discussion, held certain usage measures such as overtime fixed at initiation unless plan provisions changed.
- The article explains that nonproduction bonuses are in benefits, while production bonuses are in wages and salaries.
- The article noted in 2001 that stock options were excluded from the ECI and that BLS was researching feasibility of costing them. Treat this as historical unless verified with current BLS definitions.
- The article compares ECI with ECEC and compensation per hour. ECEC measures levels, while compensation per hour uses aggregate compensation and hours and can be affected by employment shifts.

### 14.2 2010 BLS research paper: NCS sample design issues

Status: research/historical context, not current official methodology.

The 2010 paper described an NCS design then in use:

- Three-stage sample design: areas, establishments, and jobs.
- PPS sampling at each stage.
- Five-year rotating sample panels.
- QCEW as sampling frame.
- Establishments initiated over one year, then updated for five years; index respondents updated quarterly.

Design concerns identified in 2010:

- Repeated selection of some establishments under independent PPS sampling and multi-year certainty treatment could burden respondents.
- Five-year rotation slowed implementation of changes to scope, definitions, sampled areas, NAICS, SOC, and processes.
- Private industry establishments could remain in the survey for six or more years, creating attrition; the paper cited private industry attrition of about 1 percent per quarter.
- Budget reductions complicated allocation assumptions based on fixed five-year sample sizes.
- Moving away from an area-based design toward a national design would require eliminating the first stage of area sampling and revising frames/weights.
- Response rates and frame coverage required research.

Research directions discussed:

- Three-year rotation, if staffing and product changes made it feasible.
- National design stratification with 24 geographic strata: 15 largest metropolitan areas plus remaining counties/states in each of 9 census divisions.
- Five aggregate industry strata for allocation/sampling cells, with detailed industries used for implicit stratification.
- Dependent sampling to reduce repeated establishment selection.
- Analysis of QCEW frame records with zero employment.

Connection to current Handbook: current Handbook's national two-stage design, 24 geographic subsets, 5 industry strata, and approximately 3-year private rotation resemble some later directions discussed in the 2010 research paper, but current facts should be taken from the Handbook.

### 14.3 2016 MLR: 2012 fixed employment weights

Status: methodology/history of reweighting.

Key facts:

- With the release of December 2013 estimates, ECI introduced 2012 fixed-employment weights.
- These replaced the 2002 fixed-employment weights used from March 2006 through September 2013.
- The 2012 weights were based on BLS Occupational Employment Statistics (now OEWS) data and QCEW data.
- BLS also updated classifications from 2002 SOC to 2010 SOC and from 2007 NAICS to 2012 NAICS.
- The article found minimal disruption to historical continuity.
- For civilian total compensation over December 2005-June 2013, estimated cumulative change was 18.9 percent with 2012 weights versus 19.0 percent with 2002 weights; 3-month changes never differed by more than 0.1 percentage point over March 2006-June 2013.

Reweighting interpretation:

- A pure fixed-weight Laspeyres index is best for measuring long-run change in a fixed basket.
- An index with current weights is better for measuring current rates of change.
- ECI is a compromise: weights remain fixed for years, then are updated periodically.
- Around 10-year reweight intervals help preserve long-run analytical continuity while keeping the index relevant.

Seasonal-adjustment issue at reweight:

- Indirect seasonally adjusted aggregates need continuity adjustments when aggregation weights change.
- Without adjustment, a change across the reweight quarter would combine economic cost change with a weight-change effect.
- BLS applied an aggregation weight adjustment factor to December 2013 indirect seasonally adjusted indexes and subsequent quarters to remove the weight-change effect.

### 14.4 2022 MLR: Linked ECI

Status: BLS evaluation/potential replacement methodology as of the 2022 article. Do not assume adoption without checking current BLS methodology and releases.

Goal of Linked ECI:

- Provide a more direct index calculation.
- Make sample-design improvements easier to implement.
- Allow experimentation with compensation definitions without waiting for a reweight period.
- Increase flexibility in updating the index with new information.

Current modified Laspeyres vs Linked ECI:

- Current modified Laspeyres is a cell-link update procedure: base-period cost weights are aged forward by accumulated cell cost changes.
- Linked ECI is an index-linking approach: each current-period index is directly linked to the prior-period index using current and prior matched-quote costs.

Simplified Linked ECI for a domain:

```text
Link_t = [sum over cells c of E_c0 * mean_cost_current_ct]
         ---------------------------------------------------
         [sum over cells c of E_c0 * mean_cost_prior_ct]

Linked_ECI_t = Linked_ECI_{t-1} * Link_t
```

where `E_c0` is fixed employment for cell `c`; current and prior mean costs use matched quotes.

For a single cell, the article's example is simply:

```text
current-period index = prior-period index * (current average wage / prior average wage)
```

Important differences from modified Laspeyres:

- Modified Laspeyres computes base cost weights once and ages them forward.
- Linked ECI recomputes the current/prior average-cost ratio each quarter independently of the aged base-period cost weights.
- Linked ECI uses matched quotes in the average-cost terms.

Findings from the 2022 article:

- Preliminary Linked ECI estimates tracked currently published modified Laspeyres ECI estimates closely.
- At the 95-percent confidence level, no 3-month or 12-month percent-change estimates differed significantly between methods.
- In most cases, absolute percent differences were below 0.1 percent.
- For total compensation of civilian workers, the difference in percent-change estimates never exceeded 0.1 percentage point in the article's comparison period.
- Linked ECI standard errors were generally slightly larger, but absolute differences in standard errors were small.
- BLS noted that employment weights were currently updated every 10 years and that reweighting can disrupt historical continuity.

### 14.5 2024 MLR: seasonality

Status: recent analysis of ECI seasonal adjustment.

Main points:

- ECI seasonal adjustment generally has a small effect on the most aggregate 3-month percent-change series.
- Only about half of ECI's published 3-month percent-change estimates are seasonally adjusted or eligible for seasonal adjustment.
- The ECI's fixed industry-occupation structure helps explain why seasonal adjustment is smaller than in CES average hourly earnings.
- Some industries have larger seasonal patterns, including finance/insurance, education, and utilities.
- Agents should not assume every ECI series has a seasonally adjusted version.

## 15. Agent decision rules and caveats

### 15.1 Which source to trust

Use this priority order:

1. Current BLS Handbook of Methods ECI pages for current definitions, scope, sample design, calculation, data source, presentation, and revisions.
2. Current ECI news release/technical note and BLS database for current data values and series availability.
3. MLR 2024 for recent seasonality interpretation.
4. MLR 2022 for Linked ECI evaluation, but verify whether BLS adopted it before calling it current.
5. MLR 2016 for the 2012 reweight and historical continuity.
6. 2010 research paper for historical sample-design issues and design evolution.
7. MLR 2001 for conceptual explanations; verify current treatment of any potentially changed compensation item.

### 15.2 Common mistakes to avoid

- Do not say the ECI measures wage levels. It measures changes in employer labor costs. ECEC measures levels.
- Do not describe ECI as a household survey. It is an establishment-based NCS product.
- Do not include federal workers, military personnel, private household workers, agriculture, the self-employed, or pay-setting owners in scope.
- Do not assume seasonally adjusted data exist for every published ECI series.
- Do not use seasonally adjusted series for facts requiring final unrevised values; not-seasonally-adjusted series are final upon publication, while seasonally adjusted series are revised annually for 5 years.
- Do not assume regional, union/nonunion, or incentive-basis indexes are strictly comparable with core fixed-weight aggregate/industry/occupation indexes; their weights can vary over time.
- Do not say ECI tracks individual workers. It tracks establishment jobs/quotes and the compensation costs attached to them.
- Do not infer state-level ECI estimates. BLS says ECI does not produce estimates for individual states.
- Do not claim the Linked ECI is the current official production method without checking current BLS documentation.
- Do not equate employer benefit cost with employee value.

### 15.3 When answering user questions

Use these response patterns:

- For "What is ECI?" answer: quarterly BLS index of changes in employer hourly labor costs for a fixed basket of labor, covering wages/salaries and benefits, from NCS.
- For "Why fixed weights?" answer: to isolate compensation-cost change from industry/occupation employment shifts.
- For "What is total compensation?" answer: wages/salaries plus employer benefit costs.
- For "What is real ECI?" answer: nominal ECI divided by CPI-U rebased to December 2005.
- For "Is this series revised?" answer: not-seasonally-adjusted ECI is final upon publication; seasonally adjusted history is revised annually for the most recent 5 years.
- For "Can I get state ECI?" answer: BLS does not produce state ECI estimates; special tabulations are possible only subject to BLS review and confidentiality/reliability constraints.
- For "Why does ECI differ from average hourly earnings?" answer: ECI uses fixed industry-occupation weights and NCS compensation-cost concepts; average hourly earnings is a current-composition payroll/hours measure.

## 16. Source map

Primary Handbook sources:

- BLS Handbook of Methods, Employment Cost Index: Overview. https://www.bls.gov/opub/hom/eci/home.htm
- BLS Handbook of Methods, Employment Cost Index: Concepts. https://www.bls.gov/opub/hom/eci/concepts.htm
- BLS Handbook of Methods, Employment Cost Index: Data Sources. https://www.bls.gov/opub/hom/eci/data.htm
- BLS Handbook of Methods, Employment Cost Index: Design. https://www.bls.gov/opub/hom/eci/design.htm
- BLS Handbook of Methods, Employment Cost Index: Calculation. https://www.bls.gov/opub/hom/eci/calculation.htm
- BLS Handbook of Methods, Employment Cost Index: Presentation. https://www.bls.gov/opub/hom/eci/presentation.htm

Supplementary BLS articles and papers:

- John W. Ruser, "The Employment Cost Index: what is it?" Monthly Labor Review, September 2001. https://www.bls.gov/opub/mlr/2001/09/art1full.pdf
- Joana Allamani, Kirubel Aysheshim, Leland Righter, and Christopher J. Guciardo, "The Linked Employment Cost Index: a first look and estimation methodology," Monthly Labor Review, December 2022. https://www.bls.gov/opub/mlr/2022/article/the-linked-employment-cost-index.htm
- E. Raphael Branch and David Zook, "Introducing 2012 fixed employment weights for the Employment Cost Index," Monthly Labor Review, August 2016. https://www.bls.gov/opub/mlr/2016/article/introducing-2012-fixed-employment-weights-for-the-employment-cost-index.htm
- Gwyn R. Ferguson, Chester Ponikowski, and Joan Coleman, "Evaluating Sample Design Issues in the National Compensation Survey," BLS research paper, October 2010. https://www.bls.gov/osmr/research-papers/2010/pdf/st100220.pdf
- Michael K. Lettau, "Seasonality in the Employment Cost Index," Monthly Labor Review, February 2024. https://www.bls.gov/opub/mlr/2024/article/seasonality-in-the-employment-cost-index.htm
