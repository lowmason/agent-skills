# Current Population Survey (CPS)

## 0. Source precedence and update rules

1. Prefer current BLS CPS technical documentation and current Census CPS technical documentation for current operations.
2. Use the BLS Handbook of Methods pages for stable concepts, formulas, and general process descriptions, but note that those Handbook pages were last modified in 2018 and some sample-design details have been superseded.
3. Use Census Technical Paper 66 (TP66, October 2006) as historical and methodological background, not as the current design authority. The BLS documentation page now lists Technical Paper 77 (October 2019) as the comprehensive current technical paper, with TP66 as a previous version.
4. If sources conflict, identify the design vintage. For example, older Census/Handbook pages describe the 2010 sample design implemented in 2014, while BLS current documentation describes a 2020-Census-based sample redesign introduced beginning April 2025 and scheduled for completion in July 2026.
5. Do not treat unemployment insurance (UI) claims as the number of unemployed people. CPS is the official source for the national unemployment rate; UI records only cover people who applied for and are eligible for benefits.
6. For current data values, release dates, population-control effects, response rates, standard errors, seasonal-adjustment revisions, or microdata documentation, fetch the current BLS or Census page before answering.

Primary sources used in this file are listed in section 16.

## 1. What CPS is

The Current Population Survey is a monthly household survey conducted by the U.S. Census Bureau for the U.S. Bureau of Labor Statistics (BLS). It is the source of the official national unemployment rate and many measures of employment, unemployment, people not in the labor force, hours, earnings, and worker/demographic characteristics.

Key identity facts:

- Sponsor/producer relationship: Census conducts data collection and much processing; BLS analyzes and publishes the main labor-force statistics.
- Unit of observation: households/addresses are sampled; labor-force status is measured for people in sampled households.
- Survey type: probability sample of U.S. households, designed to represent the civilian noninstitutional population.
- Frequency: monthly; data are also presented as quarterly and annual averages.
- Core products: The Employment Situation monthly release, CPS public database series, CPS tables/charts, public-use microdata, and periodic/annual releases such as usual weekly earnings, union members, veterans, disability, foreign born, families, school enrollment, worker displacement, employee tenure, and other topics.

## 2. Universe, scope, and eligibility

Published CPS labor-force data generally cover the civilian noninstitutional population age 16 and older.

Operational universe details:

- CPS interviews collect labor-force information for civilian household members age 15 and older who do not have a usual residence elsewhere and are not in the Armed Forces. BLS generally publishes labor-force data for age 16 and older.
- Excluded from the CPS labor-force universe: active-duty Armed Forces and people in institutions such as prisons, long-term care hospitals, and nursing homes.
- Included population concept: civilian noninstitutional population = civilian labor force + not in labor force, for people age 16 and older.
- No upper age limit is used.
- Students are treated the same as nonstudents: classify by work, active job search, and availability, not by school status.
- CPS is national and state based: it covers all 50 states and the District of Columbia.
- Most sample units are housing units such as single-family homes, apartments, and condominiums. Some civilian noninstitutional group quarters are in scope, but college dormitories were excluded from the CPS sample beginning in late 2017 for cost and operational reasons.

Agent warning: do not describe CPS as covering the total resident population. It excludes active-duty military and institutionalized people, and published labor-force statistics generally exclude people under 16.

## 3. Survey timing

The CPS has a monthly reference week and interview week.

- Reference week: generally the week that includes the 12th day of the month. Labor-force questions refer to activities during this week.
- Interview week: generally the week that includes the 19th day of the month.
- December exception: interview timing may shift earlier to avoid the holiday season; Census methodology describes December cases in which the interview week includes the 12th and the reference week includes the 5th.
- BLS publishes major national labor-force estimates early in the following month in The Employment Situation.

When answering classification questions, always anchor the facts to the survey reference week, not the interview day or the whole month.

## 4. Sample design and rotation

### 4.1 Basic sample design

The CPS sample is a scientifically selected probability sample of addresses/housing units, not a list of named people or families. It is designed to represent the civilian noninstitutional population of each state and DC and the United States as a whole.

Typical sample-size language varies by stage and source:

- BLS Handbook design page: about 74,000 assigned housing units monthly; about 62,000 eligible; about 54,000 completed interviews; about 105,000 people age 16+ represented in collected information.
- BLS/Census plain-language and methodology pages often refer to about 60,000 eligible or occupied households and about 110,000 individuals monthly.
- Treat these as compatible approximations from different design stages/vintages. When precision matters, quote the exact source and date.

### 4.2 Rotation pattern: 4-8-4 design

CPS uses an 8-interview rotation design:

- A household is interviewed for 4 consecutive months.
- It leaves the sample for 8 months.
- It returns for 4 more consecutive months.
- It then leaves the CPS sample permanently.

CPS divides each full monthly sample into 8 rotation groups. Each month, one group is in month-in-sample 1 (MIS-1), another in MIS-2, and so on through MIS-8. The design yields about 75 percent sample overlap from one month to the next and about 50 percent overlap with the same month one year earlier. This overlap improves estimates of month-to-month and year-to-year change without interviewing the same households indefinitely.

### 4.3 Geographic stages and current redesign

The traditional CPS sample design is multistage and state based:

- First stage: define primary sampling units (PSUs), typically counties or groups of contiguous counties within state boundaries.
- Stratify PSUs within each state.
- Select sample PSUs, with self-representing PSUs selected with certainty and non-self-representing PSUs selected with probability proportional to population.
- Second stage: select sample housing units/addresses within selected PSUs, using address frames and systematic sampling.

Important current-design note:

- The BLS Handbook design page still describes the 2010-Census sample design that was implemented beginning in 2014.
- BLS current technical documentation lists a 2025 sample redesign based on the 2020 Census blended base. The new sample began being introduced in April 2025 and is scheduled to be fully phased in by July 2026 using the normal rotation pattern.
- The 2020 redesign page states that the sample remains about 60,000 eligible housing units, including about 10,000 eligible housing units from the CHIP supplementary sample in 32 states plus DC, and describes a stratified two-stage design using the Census Master Address File (MAF), USPS updates, a unit frame, and a group-quarters frame.

### 4.4 Reliability criteria warning

Reliability criteria differ across design vintages:

- Older Census methodology/sampling pages and TP66 describe a national monthly unemployment-level coefficient of variation (CV) target around 1.9 percent, corresponding to a 0.2 percentage-point change being significant at the 90 percent confidence level, and state annual unemployment-level CV targets around 8 percent.
- The BLS 2025 redesign page describes a national monthly unemployment-level CV requirement of 2.8 percent or less, corresponding to a 0.3 percentage-point unemployment-rate difference between consecutive months being statistically significant at the 90 percent confidence level, and annual average state unemployment-level CV requirements of 10 percent or less.

Agent rule: for 2025+ current sample design statements, use the BLS 2025 sample redesign page; for historical 2000/2010 design discussions, use the appropriate older source.

## 5. Data collection

### 5.1 Interview mode and roster

Each month, Census field representatives and centralized telephone interviewers attempt to interview a responsible/knowledgeable household respondent in each eligible sampled household.

Key collection details:

- The CPS questionnaire is computerized.
- Interviews are live interviews, generally by personal visit or telephone.
- A personal visit is required/preferred for first-month sample households because the sample is an address sample and Census must establish occupancy, eligibility, and the household roster. Telephone interviewing may occur after initial personal contact if the respondent requests it.
- The fifth interview occurs after the 8-month break and is used to reestablish contact and update the roster; a personal visit is generally attempted/preferred.
- For other months, telephone interviewing is generally preferred for cost and timeliness.
- Census operates centralized telephone interviewing from Jeffersonville, Indiana, and Tucson, Arizona in current descriptions. TP66 is historical and mentions an additional older facility; prefer current Census/BLS pages for current facilities.

At the first interview, the interviewer creates a roster of resident household members and collects demographic characteristics such as age/date of birth, sex, race, Hispanic or Latino ethnicity, marital status, educational attainment, veteran status, and relationship to the reference person/householder. The roster is checked and updated in later interviews.

### 5.2 Self and proxy response

CPS attempts to collect labor-force information directly from each eligible person where possible, but a knowledgeable adult household respondent often answers for other household members. The Census methodology page says just over one-half of CPS labor-force data are collected by self-response, with most of the remainder collected by proxy. Proxy response is allowed because timeliness is critical.

### 5.3 Questionnaire length and supplements

The computerized labor-force questionnaire contains more than 200 possible questions, but skip patterns mean that each respondent receives only a small subset. Census states that, averaged across the 8 interview months, the labor-force portion lasts about 6 minutes per person.

After core labor-force questions, many months include supplemental questions. Supplements may cover topics such as annual work activity and income, health insurance, veteran status, school enrollment, contingent work, worker displacement, job tenure, computer/internet use, voting, and other sponsor topics.

### 5.4 Month-in-sample content differences

Some questions are asked only in particular rotation months:

- MIS-4 and MIS-8 are the outgoing rotation groups and collect additional earnings questions for employed wage and salary workers.
- MIS-4 and MIS-8 also collect second-job industry/occupation information for multiple jobholders and additional previous-labor-force-attachment information for people not in the labor force.
- Dependent interviewing may import previous-month information to reduce respondent burden and improve consistency, especially for main-job industry/occupation, unemployment duration, and some not-in-labor-force categories. It is not used for MIS-5 or for data collected only in MIS-4 and MIS-8.

## 6. Labor-force classification: canonical decision logic

The CPS classifies each eligible person into exactly one of three mutually exclusive categories for the reference week:

1. Employed.
2. Unemployed.
3. Not in the labor force.

Priority rule:

- Employment takes precedence over unemployment and not-in-labor-force activities.
- Labor-force activities take precedence over non-labor-force activities.
- A person who did any qualifying work during the reference week is employed even if they lost the job later in the week and also searched for work.

A practical decision tree:

```text
For published labor-force estimates:
  if person is under 16, active-duty Armed Forces, institutionalized, or otherwise out of scope:
      exclude from civilian noninstitutional population age 16+
  else if person did any work for pay or profit during the reference week:
      employed
  else if person worked 15+ hours without pay in a business or farm operated by a family member with whom they live:
      employed
  else if person had a job or business but was temporarily absent during the reference week:
      employed
  else if person was on temporary layoff and expected recall under CPS layoff rules:
      unemployed; active job search is not required
  else if person had no job, made at least one specific active job-search effort in the 4-week period ending with the reference week, and was available for work except for temporary illness:
      unemployed
  else:
      not in the labor force
```

Important: CPS respondents are not simply asked whether they are unemployed, and neither respondents nor interviewers choose the final labor-force category. The category is derived from answers to standardized questions.

## 7. Key labor-force concepts and definitions

### 7.1 Civilian labor force

Civilian labor force = employed people + unemployed people, for people age 16+ in the civilian noninstitutional population.

### 7.2 Employed people

A person is employed if, during the reference week, they meet any of these criteria:

- Did any work at all as a paid employee, including as little as 1 hour.
- Worked in their own business, profession, or farm.
- Worked 15 or more hours without pay in a family member's business or farm, if the family member is in the household.
- Had a job or business but was temporarily absent because of illness, vacation, bad weather, labor dispute, maternity/paternity leave, childcare problems, family/personal reasons, or similar reasons.

Additional employment rules:

- Count each employed person once, even if they hold more than one job.
- Exclude work around the person's own home, such as housework, painting, and repairs, when that is the only activity.
- Exclude volunteer activities for religious, charitable, and similar organizations when that is the only activity.
- People temporarily absent from a job are counted as employed because they have a specific job to which they will return.

### 7.3 Unemployed people

A person is unemployed if all of these apply:

- They were not employed during the reference week.
- They were available for work, except for temporary illness.
- They made at least one specific active effort to find employment during the 4-week period ending with the reference week.

Temporary-layoff exception:

- People waiting to be recalled to work while on temporary layoff do not need to look for a job to be classified as unemployed.

Waiting-to-start-job rule:

- People waiting to start a new job must have actively looked for work within the last 4 weeks to be classified as unemployed; otherwise they are not in the labor force.

Active job-search methods include actions that could result in a job offer without further action by the jobseeker, such as:

- contacting an employer directly;
- having a job interview;
- submitting a resume or job application;
- using a public or private employment agency or university employment center;
- contacting friends or relatives or using social networks for job leads;
- checking union or professional registers;
- placing or answering job advertisements;
- other active methods.

Passive methods do not count as active job search. Examples include only looking at job postings without taking further action, merely reading job ads, or taking a training course.

### 7.4 Not in the labor force

People age 16+ in the civilian noninstitutional population are not in the labor force if they are neither employed nor unemployed.

CPS collects additional information for people not in the labor force, including whether they want a job, whether they are available, whether they looked in the previous 12 months, and why they did not look in the 4-week reference period.

### 7.5 Marginally attached and discouraged workers

Marginally attached to the labor force:

- Not in the labor force.
- Want a job.
- Available for work.
- Looked for work sometime in the prior 12 months, or since the end of their last job if they held one within the prior 12 months.
- Did not actively search in the 4-week period ending with the reference week, so they are not counted as unemployed.

Discouraged workers are a subset of the marginally attached whose reason for not currently looking indicates discouragement about job prospects. Examples: they believe no jobs are available, they could not find work before, they lack needed schooling/training, or they believe employers view them as too young/old or subject them to other discrimination.

Other marginally attached people include those not looking for reasons such as family responsibilities, lack of childcare, transportation problems, or illness.

## 8. Rates and formulas

Use these formulas for CPS headline measures:

```text
civilian_labor_force = employed + unemployed
unemployment_rate = 100 * unemployed / civilian_labor_force
labor_force_participation_rate = 100 * civilian_labor_force / civilian_noninstitutional_population_age_16_plus
employment_population_ratio = 100 * employed / civilian_noninstitutional_population_age_16_plus
not_in_labor_force = civilian_noninstitutional_population_age_16_plus - civilian_labor_force
```

Agent rules:

- The unemployment-rate denominator is the labor force, not the total population.
- The labor-force-participation-rate and employment-population-ratio denominators are the civilian noninstitutional population age 16+.
- Use unrounded levels for calculations when possible; published rates may differ from calculations using rounded published levels.
- Use seasonally adjusted series for month-to-month headline comparisons unless the user specifically asks for not seasonally adjusted data.
- Annual averages are generally not seasonally adjusted and are not part of the annual seasonal-adjustment revision process described by BLS.

## 9. Hours, part time, multiple jobs, class, occupation, industry, and earnings

### 9.1 Full-time/part-time status and hours at work

Usual full-time/part-time status:

- Full-time workers usually work 35 or more hours per week at all jobs combined.
- Part-time workers usually work fewer than 35 hours per week at all jobs combined.
- This is based on usual hours, not necessarily actual hours during the reference week.

Hours at work:

- Actual hours worked during the reference week.
- Applies to people who were at work at least 1 hour in the reference week.
- Excludes people who were not at work for the entire week, even if they had jobs.
- For multiple jobholders, published total hours at work generally refer to all jobs during the reference week.

### 9.2 Part time for economic reasons

People at work part time for economic reasons, also called involuntary part-time workers, are people who:

- were at work 1 to 34 hours during the reference week;
- gave an economic reason for working 1 to 34 hours;
- wanted and were available to work full time.

Economic reasons include slack work, unfavorable business conditions, inability to find full-time work, and seasonal declines in demand.

People at work part time for noneconomic reasons are usually part-time workers who gave reasons such as illness, childcare/family obligations, school/training, retirement/Social Security earnings limits, full-time work being less than 35 hours in their job, or other noneconomic reasons. The category also includes a small number of people with an economic reason who were unavailable to work full time.

### 9.3 Reasons for unemployment and duration

Major unemployment-reason categories:

- Job losers: temporary layoff, permanent job losers, and people who completed temporary jobs.
- Job leavers: people who voluntarily quit or otherwise voluntarily ended employment.
- Reentrants: people who previously worked but were not in the labor force before beginning the current job search.
- New entrants: people who never previously worked.

Duration of unemployment is the length of the current, still-in-progress spell through the reference week. It is not the eventual completed jobless spell. For people on layoff, duration is the number of full weeks on layoff.

### 9.4 Occupation and industry

Occupation = type of work performed. Industry = business activity of the employer or company. For employed people with more than one job, occupation and industry are based on the job at which the person worked the greatest number of hours during the reference week. For unemployed people, occupation and industry are based on the last job.

Current classification notes from BLS technical documentation:

- Beginning with January 2020 data, CPS adopted the 2018 Census occupational classification, derived from the 2018 Standard Occupational Classification (SOC).
- Starting January 2025, CPS transitioned to the 2022 Census industry classification, derived from the 2022 North American Industry Classification System (NAICS).
- Census classifications are tailored for demographic household surveys and are generally less detailed than the full SOC/NAICS structures.

### 9.5 Class of worker

Main categories:

- Wage and salary workers: receive wages, salaries, commissions, tips, or payment in kind from a private-sector employer or a local, state, or federal government entity.
- Self-employed people: work for profit or fees in their own business, profession, trade, or farm. In general CPS class-of-worker tabulations, incorporated self-employed workers are often included among wage and salary workers because they are paid employees of their corporations; unincorporated self-employed are usually the self-employed category.
- Unpaid family workers: work without pay for 15+ hours per week in a business or farm operated by a family member with whom they reside.

### 9.6 Multiple jobholders

Multiple jobholders are employed people who had two or more jobs during the reference week. To be classified as a multiple jobholder, a person must have been a wage and salary worker in at least one job. A self-employed person with multiple unincorporated businesses, a person with multiple unpaid family-worker jobs, or a private-household worker with multiple employers is not counted as a multiple jobholder under the CPS definition.

### 9.7 Usual weekly earnings

CPS usual weekly earnings:

- Apply to wage and salary workers.
- Are before taxes and other deductions.
- Include usual overtime pay, commissions, and tips.
- Are collected for the main job for multiple jobholders.
- Convert nonweekly pay periods to weekly amounts.
- The term "usual" is based on the respondent's understanding; if asked, interviewers define it as more than half the weeks worked during the past 4 or 5 months.
- BLS CPS earnings data exclude all self-employed people, whether incorporated or unincorporated.
- Earnings are collected only for employed people, not unemployed people's last jobs.
- Published medians are calculated by linear interpolation of the $50 centered interval containing the median.

## 10. Processing, weights, controls, and estimation

### 10.1 Processing pipeline

After interviews, Census processes raw interview files before BLS estimation. Processing includes:

- secure daily transmission from interviewers/telephone centers to Census headquarters;
- removal of personally identifiable information for public-use files;
- editing for completeness and consistency;
- imputation for missing or inconsistent data items;
- standardized occupation and industry coding;
- creation of derived variables such as labor-force status and full-time/part-time status;
- household and person weight assignment;
- supplemental processing for supplement data when applicable.

Census transfers the processed microdata file securely to BLS for official labor-force estimation.

### 10.2 Weights

CPS weights convert sampled people/households into population estimates.

Weighting concepts:

- Base weight: inverse of selection probability; roughly the number of people represented by the sample person.
- Noninterview adjustment: adjusts interviewed-household weights to account for eligible occupied households not interviewed because of absence, refusals, impassable roads, or other reasons.
- Ratio adjustments: adjust sample weights to independent population controls, improving estimates and reducing undercoverage effects.
- First-stage ratio adjustment: historically reduces variance from selecting a sample of PSUs rather than sampling every PSU.
- Second-stage ratio adjustment/raking: aligns weighted sample totals with population controls by state, Hispanic origin, race, age, and sex categories. TP66 describes this as iterative proportional fitting/raking ratio estimation.

On average, a CPS sample person represents roughly 2,500 people in the population, but actual weights vary by state, sampling probability, nonresponse, and poststratification.

Agent microdata caution: use the correct weight for the estimate and file. Basic monthly person estimates, household estimates, outgoing rotation group earnings, ASEC supplements, and other supplements can require different weights. Do not hard-code weight variable names without checking the month/year-specific Census data dictionary.

### 10.3 Population controls

Population controls are independent population estimates used to weight CPS sample results to the civilian noninstitutional population age 16+. Census develops CPS population controls from decennial census counts, birth and death data, and net international migration estimates.

BLS incorporates annual population-control adjustments into CPS estimates with January data. These adjustments may raise or lower population levels depending on whether prior estimates had trended high or low. They can create discontinuities in population, labor force, employment, and unemployment levels. Rates are usually less affected than levels, but users should still check BLS adjustment effect tables when comparing December-to-January changes.

Current BLS documentation notes updated experimental series that account for January 2026 population-control effects. For current population-control effects, fetch BLS CPS technical documentation and adjustment tables.

### 10.4 Composite estimation and official estimates

TP66 describes composite estimation for national labor-force categories and notes that since January 1998 composite estimation effects have been incorporated into microdata weights for operational simplicity. The rotation design and sample overlap improve change estimates; composite estimation further uses correlation between months.

Agent rule: for official headline estimates, use BLS published series when available. Custom microdata estimates can approximate published results but may differ because of official processing, rounding, revisions, composite methods, or special specifications.

## 11. Seasonal adjustment

Seasonal adjustment removes recurring seasonal movements caused by weather, holidays, school schedules, and regular hiring/layoff patterns so that cyclical and other economic trends are easier to see.

Key rules:

- BLS produces many seasonally adjusted CPS labor-market series, but not all CPS measures are seasonally adjusted.
- For current-year seasonally adjusted estimates, BLS uses concurrent adjustment: the current month's adjusted estimate is computed using relevant original data through the current month.
- Revisions to prior months are generally postponed until the annual reestimation at the end of the calendar year.
- After annual reestimation, BLS revises seasonally adjusted CPS data for the previous 5 years.
- Revised seasonal factors and series are introduced with the publication of December estimates in January.
- Not seasonally adjusted data, including annual averages, are not part of the seasonal-adjustment revision process.

Agent rules:

- Use seasonally adjusted data for month-to-month analysis of headline labor-market movements.
- Use not seasonally adjusted data for demographic detail when no adjusted series exists, for local/season-specific questions, or when the user asks for actual counts/rates in a month.
- Do not mix seasonally adjusted and not seasonally adjusted series in the same calculation.

## 12. Reliability, standard errors, and nonsampling error

CPS estimates are sample-survey estimates and are subject to both sampling and nonsampling error.

Sampling error:

- Arises because CPS surveys a sample rather than the full population.
- Measured by the standard error of an estimate.
- Approximate 90 percent confidence intervals use estimate +/- 1.645 * standard_error.
- BLS generally conducts CPS significance analyses at the 90 percent confidence level.
- BLS provides standard-error tables, statistical-significance tables, and guidance for calculating approximate standard errors and confidence intervals.

Nonsampling error:

- Can arise from inability to interview all sample households, different interpretations of questions, incorrect recall, unwillingness/inability to provide accurate information, collection and processing errors, imputation errors, and undercoverage.
- The full extent of nonsampling error is unknown.
- Census and BLS control nonsampling error through standardized questionnaires, interviewer training, supervision, automated consistency checks, edits, imputation, coding procedures, confidentiality review, and response-rate monitoring.

Response/noninterview categories:

- Type A noninterviews: eligible occupied households for which usable data were not collected, such as refusals, temporary absence, or inability to contact/respond.
- Type B noninterviews: temporarily ineligible units, such as vacant units or units occupied only by people not eligible for CPS labor-force interviewing.
- Type C noninterviews: permanently ineligible addresses, such as demolished units, converted businesses, or addresses outside the selected area.

When comparing two CPS estimates, do not infer a real change solely from different point estimates. Check standard errors/significance, especially for small groups, subnational estimates, and month-to-month changes.

## 13. Data products, access, and presentation

### 13.1 Regular BLS outputs

BLS publishes CPS data through:

- The Employment Situation monthly news release.
- CPS online tables, charts, and thousands of BLS public database series.
- Quarterly usual weekly earnings release.
- Annual and periodic releases on union membership, veterans, disability, foreign-born workers, families, school enrollment, employee tenure, worker displacement, youth employment, and other topics.
- Annual reports such as minimum-wage workers, the working poor, and earnings by sex.

### 13.2 Microdata

Public-use CPS microdata files contain edited questionnaire-response records for people in the survey, with confidentiality protections. BLS Handbook presentation notes that public-use microdata are available for all months since January 1976 and for various months in earlier years; files from January 1994 onward and documentation are available from Census Bureau data resources.

Agent rules for microdata:

- Always pair a public-use file with the correct data dictionary/technical documentation for that month/year and supplement.
- Use appropriate weights and universe restrictions.
- Use official BLS series where exact headline values are needed.
- For supplement estimates, use supplement-specific weights, universes, and documentation.
- Cite the microdata file vintage and any supplement.

### 13.3 CPS vs CES

BLS has two major monthly employment surveys:

- CPS/household survey: surveys households, classifies people as employed/unemployed/not in labor force, and provides demographic characteristics. It includes groups not in CES, such as self-employed workers, agricultural workers, unpaid family workers, and people not working.
- CES/payroll or establishment survey: surveys employers/payrolls and estimates nonfarm payroll jobs, hours, and earnings by industry.

Agent rule: CPS employment is a count of employed people; CES employment is a count of payroll jobs. They are not interchangeable.

## 14. Historical comparability and breakpoints

CPS series are long-running but not mechanically uniform over time. Check comparability before building long time series or interpreting breaks.

Important comparability issues:

- CPS has operated monthly since 1940; Census took over responsibility in 1942.
- 1953: 4-8-4 rotation pattern introduced.
- 1994: major redesign including computerization and questionnaire changes.
- 2001: CPS sample expansion and SCHIP/CHIP supplementary sample became part of official CPS.
- 2003: changes included new race and Hispanic ethnicity questions, updated population controls, and new occupation/industry classifications.
- 2004 and 2014: sample redesigns.
- 2008: disability questions added.
- 2011: changes to unemployment-duration data collection.
- 2015: professional certification and license questions added.
- 2020: CPS adopted 2018 Census occupational classification.
- 2025: CPS transitioned to 2022 Census industry classification and began introducing the 2020-Census-based sample redesign.
- Annual January population-control adjustments can affect levels.
- Annual seasonal-adjustment reestimation revises recent seasonally adjusted series.

Agent rule: for time series involving occupation, industry, race/ethnicity, disability, duration of unemployment, population levels, or redesign transition months, look up BLS comparability notes before making strong claims.

## 15. Answering patterns and pitfalls

### 15.1 Classification examples

Use these rules in examples:

- Worked 1 hour for pay in the reference week -> employed.
- Worked 15+ unpaid hours in a household family member's business/farm -> employed.
- Temporarily absent from a job due to vacation, illness, leave, labor dispute, bad weather, or similar reason -> employed.
- Lost a job during the reference week but worked part of the week -> employed.
- No job, actively applied/interviewed/contacted employers in prior 4 weeks, available -> unemployed.
- Waiting recall from temporary layoff -> unemployed even without active search, if CPS layoff criteria are met.
- Waiting to start a new job but did not actively search in prior 4 weeks -> not in labor force.
- Only read job ads or browsed postings without further action -> not active search; not unemployed unless another active method or layoff exception applies.
- Wants a job, available, searched sometime in prior 12 months, but not in prior 4 weeks -> marginally attached, not unemployed.
- Wants a job but not available -> not marginally attached under CPS criteria.

### 15.2 Common mistakes to avoid

- Do not say the unemployment rate is unemployed divided by population; it is unemployed divided by the labor force.
- Do not count people not looking for work as unemployed, even if they want a job, unless they meet the temporary-layoff exception.
- Do not use UI claims as a direct unemployment measure.
- Do not mix CPS household-survey employment with CES payroll jobs without explaining the conceptual difference.
- Do not treat all part-time workers as involuntary part-time workers.
- Do not classify unpaid family work under 15 hours as employment.
- Do not include active-duty military or institutionalized people in the CPS civilian noninstitutional population.
- Do not treat sample-size figures as exact across all years and sources; quote source/date.
- Do not ignore population-control changes when interpreting December-to-January level changes.
- Do not ignore seasonal adjustment when comparing adjacent months.
- Do not assume occupation/industry codes are comparable across classification changes.

### 15.3 Source selection by user task

- Official current unemployment rate or employment level: use BLS Employment Situation or BLS public database, with seasonally adjusted status as requested.
- Definitions and formulas: BLS Handbook concepts and BLS "How the Government Measures Unemployment."
- Sample design/current phase-in: BLS 2025 sample redesign page and current BLS technical documentation.
- Interview procedures, noninterviews, roster, dependent interviewing: Census methodology collection pages and TP66/TP77 background.
- Weighting and controls: BLS Handbook calculation, BLS population-control documentation, Census weighting page, and current technical paper.
- Seasonal adjustment: BLS Handbook calculation and BLS CPS technical documentation seasonal-adjustment section.
- Microdata: Census CPS technical documentation and the relevant file-specific data dictionary.
- Long historical comparisons: BLS historical comparability notes, population-control notes, occupation/industry classification notes, seasonal-adjustment revisions, and redesign notes.

## 16. Source map

User-requested sources examined:

- [BLS-HOM-OVERVIEW] BLS Handbook of Methods, CPS Overview: https://www.bls.gov/opub/hom/cps/home.htm
- [BLS-HOM-CONCEPTS] BLS Handbook of Methods, CPS Concepts: https://www.bls.gov/opub/hom/cps/concepts.htm
- [BLS-HOM-DATA] BLS Handbook of Methods, CPS Data Sources: https://www.bls.gov/opub/hom/cps/data.htm
- [BLS-HOM-DESIGN] BLS Handbook of Methods, CPS Design: https://www.bls.gov/opub/hom/cps/design.htm
- [BLS-HOM-CALCULATION] BLS Handbook of Methods, CPS Calculation: https://www.bls.gov/opub/hom/cps/calculation.htm
- [BLS-HOM-PRESENTATION] BLS Handbook of Methods, CPS Presentation: https://www.bls.gov/opub/hom/cps/presentation.htm
- [CENSUS-TP66-USER-URL] User-supplied TP66 URL: https://www.census.gov/prod/2006pubs/tp-66.pdf
  - Retrieval note: this URL returned 404 during this review. The official Census copy examined is [CENSUS-TP66-OFFICIAL].
- [CENSUS-TP66-OFFICIAL] Census/BLS, Current Population Survey: Design and Methodology, Technical Paper 66, October 2006: https://www2.census.gov/programs-surveys/cps/methodology/tp-66.pdf
- [CENSUS-METHODOLOGY] Census CPS methodology: https://www.census.gov/programs-surveys/cps/technical-documentation/methodology.html
- [CENSUS-QUESTIONNAIRES] Census CPS questionnaires: https://www.census.gov/programs-surveys/cps/technical-documentation/questionnaires.html
- [BLS-DOC-OI] BLS CPS technical documentation, occupational and industry classification anchor: https://www.bls.gov/cps/documentation.htm#oi
- [BLS-DOC-POP] BLS CPS technical documentation, population controls anchor: https://www.bls.gov/cps/documentation.htm#pop
- [BLS-DOC-SA] BLS CPS technical documentation, seasonal adjustment anchor: https://www.bls.gov/cps/documentation.htm#sa
- [BLS-HTGM] BLS, How the Government Measures Unemployment: https://www.bls.gov/cps/cps_htgm.htm

Linked official sources used for current context from the requested pages:

- [BLS-2025-SAMPLE-REDESIGN] BLS, Redesign of the Sample for the Current Population Survey: https://www.bls.gov/cps/methods/sample_redesign_2025.htm
- [CENSUS-COLLECTING-DATA] Census CPS methodology, Collecting Data: https://www.census.gov/programs-surveys/cps/technical-documentation/methodology/collecting-data.html
- [CENSUS-SAMPLING] Census CPS methodology, Sampling: https://www.census.gov/programs-surveys/cps/technical-documentation/methodology/sampling.html
- [CENSUS-WEIGHTING] Census CPS methodology, Weighting: https://www.census.gov/programs-surveys/cps/technical-documentation/methodology/weighting.html
- [CENSUS-REVIEWING] Census CPS methodology, Reviewing and Revising the Data: https://www.census.gov/programs-surveys/cps/technical-documentation/methodology/reviewing-and-revising-the-data.html

## 17. Quick reference table

| Topic | Canonical answer |
|---|---|
| Survey | Monthly household survey conducted by Census for BLS |
| Main use | Official national unemployment rate and broad labor-force statistics |
| Population | Civilian noninstitutional population age 16+ for published labor-force data |
| Reference week | Usually week including the 12th |
| Interview week | Usually week including the 19th |
| Classification groups | Employed, unemployed, not in labor force |
| Labor force | Employed + unemployed |
| Unemployment rate | 100 * unemployed / labor force |
| LF participation rate | 100 * labor force / civilian noninstitutional population age 16+ |
| Employment-population ratio | 100 * employed / civilian noninstitutional population age 16+ |
| Employed minimum paid work | Any work for pay/profit, even 1 hour, during reference week |
| Unpaid family work threshold | 15+ hours in family business/farm operated by household family member |
| Active search window | 4 weeks ending with the reference week |
| Temporary layoff | Can be unemployed without active search if waiting recall under CPS rules |
| Waiting to start job | Needs active search in last 4 weeks to be unemployed |
| Rotation | 4 months in, 8 months out, 4 months in; total 8 interviews |
| Sample overlap | About 75 percent month-to-month, 50 percent year-to-year |
| Weights | Base weight, noninterview adjustment, ratio/raking to population controls |
| Population controls | Census controls introduced by BLS each January |
| Seasonal adjustment | Concurrent current-month adjustment; annual reestimation revises prior 5 years |
| Confidence convention | BLS commonly uses 90 percent confidence; estimate +/- 1.645 SE |
| Current sample redesign | 2020-base sample phased in April 2025 to July 2026 |
| Current occupation classification | 2018 Census occupation classification beginning Jan. 2020 |
| Current industry classification | 2022 Census industry classification beginning Jan. 2025 |
