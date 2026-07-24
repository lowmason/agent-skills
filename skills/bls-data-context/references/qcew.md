# QCEW (Quarterly Census of Employment and Wages)

## Source pages reviewed

Primary pages provided by the user:

- BLS Handbook of Methods - QCEW Concepts: https://www.bls.gov/opub/hom/cew/concepts.htm
- BLS Handbook of Methods - QCEW Data Sources: https://www.bls.gov/opub/hom/cew/data.htm
- BLS Handbook of Methods - QCEW Design: https://www.bls.gov/opub/hom/cew/design.htm
- BLS Handbook of Methods - QCEW Calculation: https://www.bls.gov/opub/hom/cew/calculation.htm
- BLS Handbook of Methods - QCEW Presentation: https://www.bls.gov/opub/hom/cew/presentation.htm
- BLS QCEW Information for Survey Respondents: https://www.bls.gov/cew/info-survey-participants.htm
- BLS QCEW Data Overview: https://www.bls.gov/cew/data-overview.htm

Additional official BLS QCEW pages consulted for current operational details:

- QCEW Technical Note for County Employment and Wages News Release: https://www.bls.gov/cew/news-release-technical-note.htm
- QCEW Data Files: https://www.bls.gov/cew/downloadable-data-files.htm
- QCEW Over-the-Year Change Calculation Details: https://www.bls.gov/cew/about-data/over-the-year-calculations.htm
- QCEW Imputation Methodology: https://www.bls.gov/cew/additional-resources/imputation-methodology.htm

## Executive summary

QCEW is a BLS program that publishes establishment-based counts of establishments, employment, wages, and average weekly wages across detailed geography, industry, ownership, and establishment-size dimensions. It is built primarily from state unemployment insurance (UI) administrative records, plus federal civilian employment reports, and is enhanced through the Annual Refiling Survey (ARS) and Multiple Worksite Report (MWR).

The most important concept for agents: QCEW is not a sample survey estimate in the usual sense. BLS states that QCEW data are aggregations of establishment data and are not estimates, although missing or poor-quality records can be imputed. For time-series work, treat QCEW as a high-coverage administrative census-style dataset with revisions, imputation, administrative classification changes, disclosure suppression, and industry/geography recoding. Do not treat it as a clean, designed, seasonally adjusted economic time series without additional checks.

## Agent rules of thumb

1. Do not call QCEW employment a count of people. It is a count of covered jobs, by place of work.
2. Do not treat QCEW as residence-based employment. Workers are assigned to the establishment location, not the worker residence.
3. Do not compare QCEW levels directly with CPS, LAUS, CES, BEA, OPM, QWI, or CBP without explaining concept, scope, timing, geography, and coverage differences.
4. Do not assume QCEW time series breaks are purely economic. Industry recoding, county/geography changes, ownership changes, improved multi-worksite reporting, mergers, acquisitions, relocations, predecessor/successor changes, or error corrections can create discontinuities.
5. Prefer finalized QCEW data for historical modeling. Preliminary vintages are revised until finalization in the first quarter of the following reference year.
6. For programmatic access, prefer the downloadable files or Open Data Access CSVs over the BLS publication database when full coverage is needed.
7. For over-the-year changes, distinguish full-data unadjusted values from County Employment and Wages news-release adjusted growth rates. The adjusted news-release base data are not the same as public unadjusted data.
8. When analyzing average weekly wages, explicitly check for calendar/pay-period effects, industry composition changes, part-time/full-time mix, and wage payments to workers not counted in the employment reference period.
9. For long histories, document NAICS/SIC classification systems and any crosswalks. NAICS-based QCEW data are available from 1990 forward; earlier NAICS-based files are limited and reconstructed or by-ownership only.
10. For forecasting, model QCEW as an administrative count series with known revision and classification-break risks, not as a conventional survey estimate.

## What QCEW measures

QCEW publishes:

- Monthly employment counts.
- Quarterly wage totals.
- Quarterly establishment counts.
- Average weekly wages.
- Data by geography, industry, ownership, and establishment-size class.
- Data at national, state, county, MSA, Puerto Rico, and U.S. Virgin Islands geographies, with detailed NAICS industry levels where publishable.
- Location quotients and over-the-year changes in downloadable/open data products.

### Core unit: establishment

An establishment is a single economic unit, typically at one physical location, engaged in one primary economic activity. This differs from a firm or company, which can contain multiple establishments. A multi-establishment firm can operate establishments in different industries and geographies. QCEW tries to represent these separate worksites at the establishment level, especially through the MWR.

### Employment concept

QCEW monthly employment counts covered workers who worked during, or received pay for, the pay period including the 12th day of the month. It counts filled jobs, including full-time, part-time, temporary, and permanent jobs, by place of work.

Included examples:

- Corporate officials.
- Executives and supervisors.
- Professionals and clerical workers.
- Wage earners and piece workers.
- Part-time workers.
- Workers on paid sick leave, paid holiday, paid vacation, or similar paid leave.
- Many farmworkers if covered by UI.

Critical implications:

- A worker with jobs at two covered employers is counted twice.
- QCEW is a job count, not a unique-person count.
- QCEW excludes workers who earned no wages during the applicable pay period because of work stoppages, temporary layoffs, illness, or unpaid vacation.
- QCEW is place-of-work based, not residence based.
- QCEW counts all UI-covered workers regardless of age.

### Wages concept

QCEW wages are total compensation paid during the calendar quarter, usually regardless of when the services were performed.

Included examples:

- Regular pay.
- Bonuses.
- Stock options.
- Severance pay.
- Profit distributions.
- Cash value of meals and lodging.
- Tips and gratuities.
- In some states, employer contributions to certain deferred compensation plans such as 401(k) plans.

Generally excluded examples:

- Employer contributions to old-age, survivors, and disability insurance.
- Employer health insurance contributions.
- Employer UI contributions.
- Workers compensation contributions.
- Employer private pension and welfare fund contributions.

Employee contributions and withholding amounts are included in gross wages even if deducted from take-home pay.

Important wage caveats:

- State laws differ in whether wages are reported when paid or for the period in which services were performed.
- Irregular payments, bonuses, stock options, and pay-period timing can produce large quarterly movements.
- Wages may include payments to workers not present in the employment count for the 12th-of-month pay period.

### Average weekly wage (AWW)

For the County Employment and Wages news release, BLS calculates average weekly wage as:

```text
AWW = quarterly total wages / average(month 1 employment, month 2 employment, month 3 employment) / 13
```

BLS uses unrounded employment and wage values for this calculation. Values a user calculates from rounded public tables can differ from published AWW values.

AWW can change because of:

- Changes in total wages.
- Changes in average employment.
- Full-time versus part-time mix.
- High-wage versus low-wage occupational or industry composition.
- Calendar effects from different numbers of pay dates in a quarter.
- Wage payments to workers not included in the employment reference count.

## Scope and exclusions

QCEW covers employers subject to state UI laws and federal civilian workers covered by UCFE. It covers more than 95 percent of U.S. jobs. It is often described as a virtual census of nonagricultural employment, with a portion of agricultural workers also covered.

Common exclusions include:

- Proprietors.
- Unincorporated self-employed workers.
- Unpaid family workers.
- Certain farm workers not required to report employment data.
- Certain domestic workers.
- Railroad workers covered by the railroad unemployment insurance system.
- Active-duty military.
- Some national security agencies.
- Some elected officials and other excluded government categories.
- Workers with no wages in the reference pay period because of unpaid leave, temporary layoff, illness, work stoppage, or similar nonpaid status.

QCEW should not be used as a complete count of all work performed in an area because it excludes important non-UI-covered categories, especially self-employment and some agricultural/domestic work.

## Geography

The primary local geography is county, assigned by physical establishment location. Township is a secondary geography used mainly in New England states and New Jersey. Establishments are asked for physical addresses; addresses are converted into geocodes and used for geographic assignment and mapping.

Implications:

- County changes can result from employer address corrections, relocations, or improved reporting.
- Multi-establishment employers may initially report statewide or unknown county records; improved MWR reporting can later allocate employment and wages across counties.
- For county-level time series, check whether sudden movements reflect actual local economic shifts or administrative/geocoding changes.

## Industry classification

Industry is assigned to establishments based on primary economic activity. QCEW uses NAICS for current industry detail. Data prior to the NAICS era used SIC; NAICS-based data for 1990-2000 were reconstructed from SIC-based data.

Agent guidance:

- Always record the NAICS version or classification system for long time series.
- Be cautious when comparing across NAICS revisions.
- Use BLS industry files and Industry Finder when validating codes.
- Treat NAICS 999999 or unclassified records carefully. Unclassified establishments exist when states lack enough information to assign a definitive NAICS code.
- Industry recoding can create apparent employment or wage shifts unrelated to real economic change.

## Ownership

QCEW distinguishes private ownership and public ownership, including federal, state, and local government. Coverage and reporting differ across private and government sectors. Federal civilian employment is based on UCFE reporting and excludes several categories such as active-duty military and certain other federal workers.

## Establishment size class

Establishment size classes are based on the number of employees reported by the establishment. Size-class files are available for the first quarter of a year. Use size-class data carefully because establishments can move between size classes over time.

## Data sources and survey infrastructure

### Primary administrative sources

QCEW is primarily based on microdata from federal-state UI programs. State Workforce Agencies receive Quarterly Contribution Reports (QCRs) from private-sector employers and state/local governments covered by UI. These reports support UI taxes and provide the foundation for QCEW employment and wages.

Federal government employers report via the Report of Federal Employment and Wages (RFEW), which provides employment and wage data for federal installations within each state.

### Why administrative UI data are not enough

A single-location employer in one state can often be represented adequately by a single UI report. A multi-establishment or multi-industry employer may file one consolidated state-level UI report. For QCEW statistical purposes, this is insufficient because BLS needs establishment-level industry and geography detail.

### Annual Refiling Survey (ARS)

ARS verifies and updates:

- Industrial activity.
- Geographic location.
- Business mailing address.
- Physical address.
- Auxiliary status.
- New worksites.

ARS is conducted on a 3-year cycle for many establishments, contacting about one-third of eligible establishments each year. Establishments in industries that rarely change may be placed on a 6-year cycle. States survey unclassified establishments annually to reduce NAICS 999999 records.

### Multiple Worksite Report (MWR)

MWR is used for eligible multi-establishment employers. It collects establishment/worksite-level employment and wages each quarter. It lets BLS and state agencies allocate consolidated employer data to the correct physical locations and industries.

### Electronic Data Interchange (EDI)

EDI is used for large employers and improves reporting stability and data collection efficiency. BLS also collects data through web systems and paper forms, depending on state and employer arrangements.

## Collection modes and reporting rates

Most QCEW data come through state labor market information departments that receive data from UI tax department partners. BLS also collects MWR data through BLS-operated web systems and the EDI center. BLS manages paper MWR collection for many states, while other states print and mail forms directly.

Reporting is high because UI reports are required under state UI laws. However, some ARS and MWR participation requirements vary by state. Missing and late reports still occur and can require imputation.

As of the BLS fourth-quarter 2023 collection table, QCEW included 12,148,421 establishments and 155,860,374 employment. Single establishments were 82.8 percent of establishments and 55 percent of employment, while multiple worksite reporter establishments were 17.2 percent of establishments and 45 percent of employment. This illustrates why multi-worksite reporting is disproportionately important for employment allocation.

## Data quality and validation

QCEW is a census-style administrative program, so it is not subject to sampling error in the same way as a survey. Its main risks are non-sampling errors, including:

- Nonresponse and late response.
- Item nonresponse.
- Incorrect industry codes.
- Incorrect geography or physical address.
- Incorrect ownership assignment.
- Incorrect establishment/worksite structure.
- Reporting errors by employers or payroll processors.
- Failure to identify predecessor/successor relationships.
- Business births, deaths, mergers, acquisitions, and relocations.
- Administrative recoding.

Quality controls include:

- Standardized state processing systems.
- Automated edits and validation checks.
- Follow-up with respondents for edit failures or large movements.
- BLS and state staff review of significant changes.
- Training in industry coding and survey procedures.
- Annual quality assurance reviews by BLS regional offices.
- Use of wage-record counts where available to corroborate employment changes.

BLS edits reduce millions of establishment records to a manageable review universe. Establishments with no change or statistically insignificant changes can be ignored during review, while significant employment, wage, industry, or county changes are validated.

## Calculation and aggregation

Published QCEW totals are generally sums of establishments belonging to a subdomain such as geography, industry, ownership, and size class. Averages and other derived statistics are calculated from those aggregations.

Important calculation points:

- QCEW is not a model-based survey estimate.
- Imputation can be used for missing or poor-quality records.
- Proration is used for multiple-establishment employers when top-line employment and wage levels are known but establishment-level distributions are unknown.
- Basic monthly employment edits use statistical tests on month-to-month changes, over-the-year changes, and 12-month variation in levels and rates.
- Record linkage across quarters supports editing, imputation, classification of births/deaths/continuing establishments, and longitudinal research.

## Imputation

### Current status and timeline

The Handbook calculation page describes an older imputation approach and the cell-ratio method as a researched/coming improvement. However, BLS's later imputation methodology page clarifies the current timeline:

- Prior to the November 2020 QCEW news release, the old method used year-earlier change patterns applied to the prior month's reported employment or quarterly wages.
- Effective with the November 2020 QCEW news release containing second-quarter 2020 QCEW data, BLS changed imputation methods.
- The new method uses current trends from similar businesses through a ratio method.
- The new method is used for data for 2020 and after; data prior to 2020 were not revised to incorporate the new method.
- Beginning with third-quarter 2021 data, BLS retired the Quarterly Imputation Improvement Project (QIIP) due to waning pandemic reporting impacts and implementation of the QUEST state-processing system.

Agent guidance:

- Treat the official imputation methodology page as the most current source for imputation details.
- For pre-2020 versus 2020+ comparisons, note the imputation-method change.
- During the pandemic period, expect unusual reporting and imputation issues, especially in small areas and detailed industries.
- Do not assume all apparent pandemic-era changes are directly observed reports; some portion can reflect imputation and later revisions.

### Ratio imputation concept

For employment, the ratio method computes an estimation-cell ratio as:

```text
ratio = sum(current-month reported employment for similar businesses)
        / sum(previous-month reported employment for similar businesses)
```

Then for a nonrespondent:

```text
imputed current employment = ratio * nonrespondent previous-month employment
```

A similar procedure applies to total quarterly wages.

## Revisions and publication status

QCEW data are published quarterly, generally within about six months after the reference period. Full quarterly and annual website data are unadjusted and preliminary until finalization with the publication of first-quarter data for the following reference year.

Revision pattern:

- First-quarter data are published five times: original release in September of the same year, then revisions in December, March, June, and September.
- Second-quarter data are published four times.
- Third-quarter data are published three times.
- Fourth-quarter data are published twice.
- The largest revision usually occurs from initial publication to first revision, as late reports and out-of-business reports arrive.
- Once final, QCEW data are generally not edited, but corrections can be issued if errors are found.

Year-to-date release structure (the mechanism behind the publication counts above):

- Each quarterly QCEW release is a year-to-date package: the release for quarter q re-carries every earlier quarter of the same reference year, not just the newest quarter.
- A carried quarter k arrives in the quarter-q release at its (q−k)-th revision: the Q3 release carries Q3 original, Q2 at its first revision, and Q1 at its second.
- The terminal within-year revision of quarter q is therefore its (4−q)-th, and it arrives only with the Q4 release. Finalization follows with the next year's first-quarter release, completing the publication counts listed above.
- Prior-year quarters are additionally republished in annual benchmark windows, so even a quarter past its within-year revision cycle can change in a benchmark republication.
- Consequence for vintage capture: reconstructing any quarter's revision path requires archiving every quarterly release as it appears — the year-to-date files replace one another in place on the server (see references/ingest.md).

Agent guidance:

- Store vintage metadata whenever possible.
- For reproducible research, document the download date and whether data were preliminary or final.
- For training forecasting models, prefer finalized data except when the use case explicitly requires real-time/vintage performance.
- For nowcasting or preliminary analysis, model expected revisions or at least flag preliminary status.

## News releases versus full data files

Do not confuse County Employment and Wages news-release values with the complete public QCEW data files.

Important distinctions:

- The County Employment and Wages news release focuses on large counties, generally those with annual average employment of 75,000 or greater, plus selected national/state tables.
- News-release growth rates are over-the-year and adjusted to mute noneconomic administrative changes.
- Those adjusted growth rates are not published elsewhere.
- The adjusted prior-year base used for news-release over-the-year growth can be unpublished and may not match unadjusted website data.
- Quarterly and annual data on the website, separate from the news release, are unadjusted.
- News-release data are never updated, while full website data are revised until final.

Agent guidance:

- If matching a BLS news release, use the release's adjusted measures and technical note.
- If building a dataset, use full QCEW downloadable/open data files and compute your own transformations consistently.
- Do not expect to reproduce news-release adjusted growth rates from ordinary unadjusted public files.

## Over-the-year calculations in downloadable/open files

QCEW Open Data Access files and CSV downloadable files include over-the-year (OTY) level and percent changes.

Important details:

- OTY level change is current value minus the same data point from the prior year.
- OTY percent change is 100 * (current - prior) / prior, rounded to the tenths place.
- For data points representing averages, OTY changes use the rounded values in the file.
- OTY AWW level change subtracts prior AWW from current AWW; it does not recompute AWW from component differences.

Agent guidance:

- When exact reproducibility matters, use BLS-provided OTY fields rather than recomputing from separately rounded components.
- If recomputing, document rounding differences.

## Confidentiality and suppression

QCEW uses confidentiality protections because it publishes administrative data from identifiable employers. BLS withholds data where publication could reveal sensitive respondent information. The exact disclosure avoidance methods are not fully disclosed so that the protection remains effective.

Important details:

- Detailed industry/geography cells can be suppressed.
- Suppressed detailed data are included in higher-level state and national totals where disclosure is protected.
- Suppression means that lower-level detail may not sum exactly to visible higher-level totals.
- Confidentiality rules differ from ordinary BLS sample survey publication practices.

Agent guidance:

- Never interpret a missing/suppressed cell as zero.
- When aggregating visible detailed data, expect differences from published totals due to suppressed cells.
- Use published higher-level totals when totals are required.

## QCEW is not designed as a clean time series

BLS explicitly cautions that QCEW data are not designed as a time series. They are sums of establishment records that exist in a county or industry at a point in time.

Reasons for breaks or sudden shifts include:

- Establishment relocation into or out of a county.
- Corrected county designation.
- Change in primary economic activity.
- Change in industry definition.
- Correction of a reporting error.
- Change from single-unit to multi-unit reporting.
- Better worksite allocation for a multi-establishment employer.
- Mergers and acquisitions.
- Predecessor/successor updates.
- Business births and deaths.
- Changes in state or federal UI coverage laws.
- NAICS revisions and classification changes.

Agent guidance for time-series work:

- Flag and inspect large level shifts before modeling.
- Compare establishment count, employment, wages, ownership, industry, and geography together to detect administrative changes.
- Check whether changes occur in first-quarter data, when many classification updates are introduced.
- Use over-the-year comparisons carefully because seasonal and administrative effects can interact.
- For forecasting, consider robust changepoint methods and intervention flags for classification/system changes, not only macroeconomic recessions.
- Do not assume QCEW is seasonally adjusted.

## Data access options

### BLS Data Overview page

The QCEW Data Overview page points users to several access methods:

- Databases.
- Data Viewer.
- Downloadable Files.
- Industry Finder.
- About Data.
- For Developers / Open Data Access.
- State and County Maps.
- Regional Resources.
- Latest Numbers.
- Interactive Charts.

### Downloadable files

BLS states that the downloadable files provide full data set access. The Data Overview page notes that the BLS publication database cannot fully support the QCEW dataset and contains less than 10 percent of QCEW data; for full data, use downloadable files.

Data file history:

- NAICS-based data are available from 1990 forward.
- More limited NAICS-based data are available from 1975 to 1989.
- NAICS-based 1990-2000 files were reconstructed from SIC data.
- NAICS-based 1975-1989 files contain only totals by ownership.
- SIC-based data are available from 1975 through 2000.
- Open Data Access CSVs provide all QCEW data for the most recent five years.

Common file types include:

- By area CSVs.
- By industry CSVs.
- Single files.
- By size files.
- County high-level files.
- Annual average files.
- Quarterly files.
- Legacy formats.
- Associated code/title files for industries, areas, ownerships, size classes, and aggregation levels.

Agent guidance:

- For complete reproducible pipelines, use downloadable files plus code/title lookup files.
- For recent programmatic access, Open Data Access CSVs are appropriate.
- For all history, use downloadable data files by year and format.
- Always capture file layout documentation along with data files.
- Read `area_fips` as a string, never as a number. The column mixes alphanumeric aggregate codes (`US000` national, MSA codes such as `C1010`) with zero-padded county FIPS codes (`01001`). A numeric parse either errors on the alpha codes or silently strips leading zeros from county codes — both corrupt the join key.

## Related data programs and comparability

### CES (Current Employment Statistics)

CES is a monthly establishment survey and a Principal Federal Economic Indicator. It estimates nonfarm payroll jobs, hours, and earnings. CES uses QCEW as a sampling frame and annually benchmarks March estimates to QCEW population counts for UI/UCFE-covered employment. QCEW covers about 97 percent of CES in-scope employment; CES benchmarks the remaining jobs from other sources.

Do not directly compare CES and QCEW levels without adjusting for:

- Monthly survey versus administrative quarterly reporting.
- CES nonfarm scope versus QCEW UI/UCFE coverage.
- Jobs not covered by UI.
- Publication timing and revisions.
- Seasonally adjusted versus not seasonally adjusted series.
- Benchmarking and birth-death modeling in CES.

### BED (Business Employment Dynamics)

BED uses longitudinally linked QCEW UI records to measure gross job gains and losses from establishment openings, closings, expansions, and contractions. It excludes government, private households, and zero-employment establishments. BED is designed for dynamics; QCEW is the broader administrative count.

### CPS (Current Population Survey)

CPS is a household survey that counts employed people, generally by place of residence. QCEW counts covered jobs by place of work.

Key differences:

- CPS counts people; QCEW counts jobs.
- CPS includes self-employed workers and unpaid family workers meeting CPS criteria; QCEW generally excludes them.
- CPS includes people with a job but not at work who may have no wages in the pay period; QCEW excludes unpaid workers in the reference pay period.
- CPS counts multiple-jobholders once; QCEW counts each covered job.
- CPS excludes people under age 16; QCEW counts all UI-covered workers regardless of age.

### LAUS (Local Area Unemployment Statistics)

LAUS estimates employed and unemployed people by place of residence, aligned to CPS concepts. It measures labor supply and unemployment rates. QCEW measures met labor demand by UI-covered employers at place of work.

A county's LAUS employment and QCEW employment match only in a hypothetical case where every working resident has one local covered job, no in-commuters/out-commuters exist, and there is no self-employment, agricultural exclusion, multiple jobholding, telework mismatch, or cross-border commuting.

### BEA regional employment and income

BEA uses QCEW as a major input for regional income and employment estimates, but BEA products include other sources and adjustments for non-QCEW concepts. BEA regional employment and compensation measures are not directly comparable to QCEW.

### OPM federal employment

OPM federal employment differs from QCEW/UCFE coverage and reference periods. UCFE uses the pay period including the 12th; OPM can use the last workday of the month or last pay period before month end plus intermittent employees. Coverage categories also differ.

### QWI / LEHD

Quarterly Workforce Indicators use QCEW and UI data as major inputs but link worker and employer records to provide local labor-market statistics by demographics, employer age, size, hires, separations, and turnover. QCEW itself does not publish worker demographics.

### CBP (County Business Patterns)

CBP is an annual Census Bureau series with establishment, employment during the week of March 12, first-quarter payroll, and annual payroll. It is based on the Census Business Register and related sources, not directly on the QCEW administrative file.

Key differences:

- QCEW is quarterly and publishes monthly employment and quarterly wages.
- CBP is annual and centered on March 12 employment plus payroll measures.
- QCEW includes all NAICS industries where covered by UI, including government ownership categories; CBP excludes most government establishments and several sectors/categories.
- CBP uses noise infusion for disclosure protection; QCEW uses BLS confidentiality/suppression practices.
- QCEW and CBP should not be treated as interchangeable establishment/employment series.

## Typical agent workflow for QCEW analysis

1. Define the concept.
   - Employment, establishments, wages, AWW, location quotient, OTY change, or size class.
   - Decide whether the answer needs monthly employment, quarterly wages, or annual averages.

2. Define the universe.
   - Area code/geography.
   - Industry code and NAICS version.
   - Ownership.
   - Size class if relevant.
   - Time period and vintage.

3. Select access method.
   - Use downloadable files for full data/history.
   - Use Open Data Access for recent programmatic CSV access.
   - Use Data Viewer for interactive exploratory tables.
   - Use BLS database only for limited series retrieval.

4. Download data and lookup files.
   - Data file(s).
   - File layout documentation.
   - Industry codes/titles.
   - Area codes/titles.
   - Ownership codes.
   - Size-class codes.
   - Aggregation-level codes.

5. Validate definitions.
   - Confirm whether fields are monthly, quarterly, or annual.
   - Confirm employment month 1/month 2/month 3 semantics.
   - Confirm whether totals are annual averages or quarter-specific values.
   - Confirm whether OTY fields are BLS-provided rounded calculations.

6. Quality-check series.
   - Check revisions/preliminary status.
   - Check suppressed cells.
   - Check industry/geography/ownership changes.
   - Check large establishment count shifts.
   - Check abrupt level changes in March/June/September/December and especially first quarter.

7. Document caveats.
   - Coverage exclusions.
   - Place-of-work and job-count concept.
   - Non-time-series caution.
   - Imputation and revisions.
   - Suppression and nonadditivity due to hidden cells.
   - Classification versions.

## Forecasting guidance for QCEW

QCEW can be forecast, but agents should explicitly model or document its administrative data-generating process.

Recommended principles:

- Train on finalized historical data where possible.
- Use preliminary data only for real-time/nowcasting workflows and document expected revisions.
- Include intervention or changepoint checks for administrative breaks, not only economic recessions.
- Model pandemic-era data separately or with strong robustness controls because imputation methods and reporting conditions changed in 2020.
- Consider benchmarking/nowcasting with CES for timely monthly signal, but keep concept differences explicit.
- For local or detailed industry forecasts, check whether changes are driven by one or a few large employers, disclosure suppression, or reclassification.
- Use establishment counts and wages as supporting diagnostics for employment models.
- Avoid blindly seasonally adjusting all cells; small geographies/industries can be sparse, suppressed, or discontinuous.
- For annual forecasts, decide whether to forecast annual average employment, December employment, third-month-of-quarter employment, quarterly total wages, or AWW. These are distinct targets.

## Common pitfalls

- Saying QCEW counts workers instead of covered jobs.
- Treating QCEW as residence-based employment.
- Treating preliminary data as final.
- Mixing adjusted news-release growth with unadjusted full data.
- Recomputing BLS AWW or OTY changes from rounded public components and expecting exact matches.
- Treating suppressed cells as zero.
- Parsing `area_fips` numerically: alpha aggregate codes like `C1010` and leading-zero county codes like `01001` both break.
- Summing visible detailed cells and assuming they equal higher-level totals.
- Ignoring NAICS revisions in long histories.
- Ignoring multi-establishment reporting changes.
- Assuming all sudden county/industry movements are real economic changes.
- Comparing QCEW to CES, CPS, LAUS, BEA, OPM, QWI, or CBP without concept reconciliation.

## Glossary

ARS: Annual Refiling Survey. A QCEW survey used to verify and update establishment industry, geography, address, and related classification information.

AWW: Average weekly wage. A derived wage measure, often quarterly total wages divided by average monthly employment and then by 13.

BED: Business Employment Dynamics. BLS program using longitudinally linked QCEW records to measure gross job gains/losses.

CBP: County Business Patterns. Census Bureau annual establishment/employment/payroll series based on the Business Register and related sources.

CES: Current Employment Statistics. BLS monthly establishment survey of payroll employment, hours, and earnings.

CPS: Current Population Survey. Household survey used for labor force, employment, and unemployment measures.

EDI: Electronic Data Interchange. Direct transfer of data from employer/firm systems to BLS.

Establishment: A single economic unit, typically at one physical location and engaged in one primary activity.

Firm/company: A business entity that may include one or more establishments.

FIPS: Federal Information Processing Standards. Used for geographic area coding.

LAUS: Local Area Unemployment Statistics. Program that estimates labor force, employment, unemployment, and unemployment rates by residence-based concepts.

MWR: Multiple Worksite Report. Quarterly report for multi-establishment employers, collecting worksite-level employment and wages.

NAICS: North American Industry Classification System. Current industry classification system used for QCEW.

OTY: Over the year. A comparison against the same data point one year earlier.

QCEW: Quarterly Census of Employment and Wages.

QCR: Quarterly Contribution Report. Employer UI report submitted to state workforce agencies.

RFEW: Report of Federal Employment and Wages. Federal government reporting source for QCEW.

SIC: Standard Industrial Classification. Historical industry classification system used before NAICS.

UI: Unemployment Insurance.

UCFE: Unemployment Compensation for Federal Employees.

## Suggested agent answer template

When describing a QCEW series, use language like:

> This QCEW series measures covered jobs by place of work for employers subject to UI/UCFE reporting, not employed persons by residence. Monthly employment is for workers who worked or received pay during the pay period including the 12th day of the month. Wages are quarterly compensation paid, including irregular pay such as bonuses and some deferred compensation contributions depending on state law. The data are administrative counts and may include imputation for missing records. Recent quarters may be preliminary and subject to revision; detailed cells may be suppressed for confidentiality. Long-run comparisons should account for NAICS changes, establishment relocations, ownership/geography/industry recoding, and multi-worksite reporting changes.

## Recommended project metadata fields

For each QCEW dataset or derived series stored in this project, retain:

- `source`: BLS QCEW.
- `download_url`.
- `download_date`.
- `reference_period_start` and `reference_period_end`.
- `vintage_or_release_date` if known.
- `preliminary_or_final`.
- `area_code` and `area_title`.
- `industry_code` and `industry_title`.
- `industry_classification_system` and version if known.
- `ownership_code` and `ownership_title`.
- `size_class` if used.
- `aggregation_level`.
- `measure`.
- `unit`.
- `seasonal_adjustment`: normally unadjusted unless a downstream process adjusts it.
- `suppression_flag` if present.
- `imputation_notes` if relevant.
- `known_breaks_or_notes`.
- `file_layout_version` or documentation URL.

