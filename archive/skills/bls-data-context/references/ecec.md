# Employer Costs for Employee Compensation (ECEC)

## 0. Source priority and conflict rules

Use the current BLS Handbook of Methods ECEC pages as the first authority for current ECEC concepts, data sources, design, calculation, and presentation. The current Handbook pages used here are last-modified September 30, 2025. Use the 2007 and 2011 PDFs for historical and technical context, especially for benchmarking, weighting, variance, and sample-design research. If a current Handbook statement conflicts with an older PDF, follow the current Handbook.

Important conflicts to handle explicitly:

- Current design: the current Handbook describes National Compensation Survey (NCS) data as selected in two stages: establishments and occupations within establishments. The 2011 design-research paper describes the older three-stage area-establishment-job design and a proposed redesign. Treat that paper as design history and context, not the current operational description.
- Variance replicates: the current Handbook describes 120 BRR replicates/variance strata and uses k = 0.5 for NCS publications. The 2007 variance note documents a historical implementation using R = 128 and a revised multiplier of 0.0313. Use the Handbook for current ECEC reliability descriptions.
- Weighting papers use historical sample panels and numerical examples. Treat those numbers as examples of the process, not current ECEC employment counts or current estimates.

## 1. Source index

| ID | Source | Type | Main use in this knowledge base |
|---|---|---|---|
| HOM-OVERVIEW | https://www.bls.gov/opub/hom/ecec/home.htm | Current BLS Handbook page | Program overview, key measures, periodicity, reference period, scope, geography |
| HOM-CONCEPTS | https://www.bls.gov/opub/hom/ecec/concepts.htm | Current BLS Handbook page | Definitions: universe, compensation components, benefits, subcategories, datatypes |
| HOM-DATA | https://www.bls.gov/opub/hom/ecec/data.htm | Current BLS Handbook page | NCS collection, field economists, respondent information, confidentiality |
| HOM-DESIGN | https://www.bls.gov/opub/hom/ecec/design.htm | Current BLS Handbook page | Sample design, establishment sampling, occupation sampling, rotation, PSO, SOC, work levels |
| HOM-CALC | https://www.bls.gov/opub/hom/ecec/calculation.htm | Current BLS Handbook page | Measuring costs, weights, nonresponse, imputation, benchmarking, estimates, CPE, reliability |
| HOM-PRESENTATION | https://www.bls.gov/opub/hom/ecec/presentation.htm | Current BLS Handbook page | Publications, accessing data, users, revisions, special requests, microdata |
| PDF-CALC-2007 | https://www.bls.gov/ecec/additional-publications/ecec-calculation-march-2007.pdf | BLS methodological note | Historical December 2006/March 2007 benchmark calculation change |
| PDF-WEIGHT-2011 | https://www.bls.gov/osmr/research-papers/2011/pdf/st110220.pdf | BLS research paper | Technical weighting process: initial weights, nonresponse adjustment, occupational adjustment, benchmarking |
| PDF-VAR-2007 | https://www.bls.gov/ecec/additional-publications/ecec-variance-calculation-march-2007.pdf | BLS methodological note | Historical December 2006/March 2007 variance method change |
| PDF-DESIGN-2011 | https://www.bls.gov/osmr/research-papers/2011/pdf/st110230.pdf | BLS research paper | Sample-design redesign context, transition from area-based to national design, frame/allocation considerations |

## 2. What ECEC measures

ECEC measures the average employer cost per employee hour worked for:

- Total compensation.
- Wages and salaries.
- Benefits.
- Specific benefit components.
- Costs as a percentage of total compensation.
- Compensation percentile estimates for selected wage percentiles.

The core ECEC unit is a cost level, not an index. It is a point-in-time average cost per employee hour worked. It is collected through the NCS and published quarterly. The reference periods are the pay periods that include the 12th day of March, June, September, and December. ECEC estimates are available for the civilian economy, private industry, and state and local government, with many estimates segmented by occupation, industry, geography, bargaining status, work status, and establishment size.

Primary sources: HOM-OVERVIEW, HOM-CONCEPTS, HOM-CALC, HOM-PRESENTATION.

## 3. Scope and universe

### 3.1 Ownership categories

ECEC ownership categories are central. Always identify the ownership category before interpreting an estimate.

| Ownership category | Meaning | Main exclusions |
|---|---|---|
| Civilian workers | Combined private industry plus state and local government workers | Volunteers, unpaid workers, people receiving long-term disability compensation, and workers overseas are excluded |
| Private industry | Workers in private industry establishments | Private households, self-employed workers, workers who set their own pay, proprietors, owners, major stockholders, partners in unincorporated firms, family members paid token wages, and the agricultural sector are excluded |
| State and local government | Workers in state and local government establishments | Federal government, quasi-federal agencies, military personnel |

National ECEC geography includes the continental United States, Alaska, and Hawaii, but excludes U.S. territories such as Puerto Rico, American Samoa, Guam, the Northern Mariana Islands, and the U.S. Virgin Islands.

Primary source: HOM-CONCEPTS.

### 3.2 Establishment

An establishment is a single economic unit engaged in one, or predominantly one, type of economic activity. In private industry this is usually a single physical location, such as a factory, mine, office, or store. If the sampled unit is owned by a larger multi-location company, only the sampled establishment's employment and characteristics are considered. For state and local government, an establishment may include more than one physical location, such as a school district or police department. Establishments are assigned six-digit NAICS codes.

Primary source: HOM-CONCEPTS.

### 3.3 Work schedule

A work schedule is the usual schedule for the selected job: daily hours, weekly hours, and annual weeks that employees in the occupation are scheduled and do work. Short-term fluctuations and one-time events are generally ignored unless the change becomes permanent. Work schedules can be fixed, flexible, rotating, or nonfixed. Work schedule data support hourly, weekly, and annual earnings calculations and benefit-cost calculations.

Primary sources: HOM-CONCEPTS, HOM-DATA.

## 4. Compensation concepts and components

### 4.1 Total compensation

Total compensation is employer cost for wages and salaries plus employer cost for employee benefits.

Primary source: HOM-CONCEPTS.

### 4.2 Wages and salaries

Wages and salaries are regular employer payments to employees for services during a period or based on production, sales, or specific output.

Include in wages and salaries:

- Incentive-based pay, including commissions, production bonuses, and piece rates.
- Cost-of-living allowances.
- Hazard pay.
- Payments of income deferred because of participation in a salary reduction plan.
- Accrued longevity pay.
- Deadhead pay for transportation workers returning in a vehicle without freight or passengers.

Do not include as wages and salaries:

- Uniform and tool allowances.
- Free or subsidized room and board.
- Payments made by third parties, such as tips.
- On-call pay.
- Retroactive pay.
- Lump-sum non-accrued longevity pay.

Do not treat the following as wages and salaries; ECEC classifies them as benefits:

- Shift differentials.
- Premium pay for overtime, holidays, and weekends.
- Nonproduction bonuses, such as end-of-year bonuses and profit-sharing bonuses not directly tied to production.

Primary source: HOM-CONCEPTS.

### 4.3 Benefits

ECEC captures employer benefit costs in five major categories:

1. Paid leave: vacation, holiday, sick, and personal leave.
2. Supplemental pay: overtime and premium pay, shift differentials, and nonproduction bonuses.
3. Insurance: life, health, short-term disability, and long-term disability.
4. Retirement and savings: defined benefit and defined contribution plans.
5. Legally required benefits: Social Security, Medicare, federal unemployment insurance, state unemployment insurance, and workers' compensation.

Primary sources: HOM-OVERVIEW, HOM-CONCEPTS, HOM-CALC.

### 4.4 Benefit definitions

| Component | Definition or interpretation |
|---|---|
| Vacation leave | Paid absence from work, or pay in lieu of time off, provided annually and usually taken in blocks of days or weeks |
| Holiday leave | Paid absence on days of religious, cultural, social, or patriotic significance when work and business ordinarily cease |
| Sick leave | Paid absence when an employee cannot work because of non-work-related illness or injury |
| Personal leave | General-purpose leave for reasons important to the worker but not otherwise provided by other leave types |
| Overtime and premiums | Pay for work beyond normal straight-time schedules; usually includes a premium but may sometimes be regular pay or another amount |
| Shift differentials | Extra pay for regular-schedule hours worked on shifts that employers find harder to staff |
| Nonproduction bonuses | Employer-discretionary pay not tied to a production formula, such as holiday bonuses or cash profit sharing |
| Life insurance | Plans paying a lump sum to beneficiaries when the employee dies |
| Short-term disability | Plans covering non-work-related illness or accident, usually for 6 to 12 months per disability |
| Long-term disability | Plans paying monthly benefits to eligible employees unable to work for an extended period because of non-work-related illness or injury |
| Health insurance | Preventive and protective medical, dental, vision, or prescription drug coverage for employees and dependents |
| Defined benefit retirement | Guaranteed retirement benefits under a formula, often using age, service, and preretirement earnings |
| Defined contribution retirement | Employer contribution levels specified and placed into individual employee accounts |
| Social Security | Old Age, Survivors, and Disability Insurance |
| Medicare | Federal health insurance for older people, some people with disabilities, and people with permanent kidney failure |
| Unemployment insurance | Federal and state programs providing income to eligible workers who lose jobs |
| Workers' compensation | Medical expenses and lost income for work-related injury or illness |

Primary source: HOM-CONCEPTS.

## 5. Classifications and datatypes

### 5.1 Industry, occupation, worker, and establishment characteristics

ECEC estimates can be classified by:

- Ownership: civilian, private industry, state and local government.
- Compensation component: total compensation, wages and salaries, total benefits, and benefit components.
- Industry: NAICS.
- Occupation: SOC.
- Bargaining status: union or nonunion.
- Work status: full-time or part-time, using each establishment's definitions. ECEC does not impose a universal hours threshold for full-time or part-time.
- Establishment size: ranges such as less than 50 workers, 50-99 workers, less than 100, 100 or more, 100-499, or 500 or more.
- Area: national, census region, census division, and selected metropolitan areas.

Union workers meet all of these conditions: a labor organization is recognized as bargaining agent for all workers in the occupation; wage and salary rates are determined through collective bargaining or negotiations; and settlement terms on earnings provisions are embodied in a signed, mutually binding collective bargaining agreement. Workers not meeting those conditions are nonunion.

Primary sources: HOM-CONCEPTS, HOM-PRESENTATION.

### 5.2 Geographic concepts

ECEC uses census divisions and regions, plus selected MSAs/CSAs. Regions are:

- Northeast: New England and Middle Atlantic.
- South: South Atlantic, East South Central, and West South Central.
- Midwest: East North Central and West North Central.
- West: Mountain and Pacific.

ECEC data are available for the 15 largest MSAs and CSAs, as defined by OMB, when criteria are met. State-level ECEC estimates are not produced because the NCS is not designed to produce state-level ECEC estimates.

Primary sources: HOM-CONCEPTS, HOM-PRESENTATION.

### 5.3 Datatypes

| Datatype | Meaning |
|---|---|
| Cost per hour worked | Total employer cost of a wage, salary, benefit, or compensation component divided by total hours worked. This includes all workers in benefit estimates, including workers without access to a plan and workers who do not participate. |
| Percent of total compensation | The proportion of total compensation represented by a given component. BLS calculates this from unrounded cost estimates, so recomputing from rounded published estimates may differ slightly. |
| Compensation percentile estimate (CPE) | Wage percentile estimates based on wages and salaries. These determine the 10th-, 50th-, and 90th-percentile bands and average benefit costs for observations in those wage bands. |
| Current dollar | Nominal values, not adjusted for consumer prices. |
| Constant dollar | Real values adjusted for changes in consumer prices. |

Primary sources: HOM-CONCEPTS, HOM-CALC.

## 6. Data collection through the National Compensation Survey

ECEC microdata are collected through the NCS. The NCS is a voluntary, establishment-based survey of civilian workers in private industry and state and local government. It excludes private households, federal government, and agriculture.

BLS field economists collect compensation data. They receive training and use methods such as personal visits, mail, telephone, and email. They do not use a paper or online questionnaire for these data; they conduct conversational interviews and use descriptive documents, such as job descriptions, to collect cost, coverage, and provision data.

At initial and later contacts, field economists attempt to collect:

- Primary business activity and correct NAICS code.
- Employee lists or job titles and counts.
- Number of employees in each sampled job.
- Worker attributes for sampled jobs: bargaining status, work status, and time- or incentive-based pay.
- Wage and salary data for sampled jobs, updated from payroll records for the pay period including the 12th of the reference month.
- Job tasks, required knowledge, controls and complexity, contacts, and environmental conditions, used for work-level evaluation.
- Typical hours and usual work schedule.
- Availability of employer-sponsored benefits.
- Employer costs for benefits.

For hours-based or wage-related benefits such as paid leave, field economists collect the number of hours or days of benefit used by workers in sampled jobs, multiply by the employer contribution or compensation rate, and divide by total occupational employment to calculate cost. For benefits not directly linked to hours and wages, such as insurance, field economists collect information for plan participants.

Induced usage means that changes in plan provisions or costs may change benefit usage. Field economists capture induced usage during collection updates, separately from the usage captured at initiation.

Primary source: HOM-DATA.

### 6.1 Confidentiality

NCS data are subject to BLS confidentiality requirements. Data are used only for statistical purposes. BLS keeps the survey sample composition, reporter lists, and respondent names confidential. Published estimates are screened so they do not reveal or allow identification of a specific respondent without informed consent.

Primary source: HOM-DATA.

## 7. Current sample design

ECEC uses NCS microdata to measure employer costs in private industry and state and local government establishments across the nation. Current Handbook material describes national probability samples in two stages:

1. A probability sample of establishments.
2. A probability sample of occupations within sampled establishments.

Because the data come from probability samples, estimates are subject to sampling error and nonsampling error.

Primary source: HOM-DESIGN.

### 7.1 Stage 1: selecting establishments

NCS uses probability proportional to size (PPS) sampling to select private industry and state and local government establishments. Larger establishments have a greater chance of selection. Establishments in all 50 states and the District of Columbia are eligible.

The sample frame is developed from state unemployment insurance reports available through QCEW. The most recent reference period available at sample selection is used.

Current Handbook design features:

- 5 industry strata.
- 24 geographic subsets.
- 120 sampling cells = 5 industry strata * 24 geographic subsets.
- The 5 aggregate industries comprise 23 detailed NAICS sectors.
- The 24 geographic subsets consist of the 15 largest metropolitan areas by employment and the remaining portions of each of the 9 census divisions.

Primary source: HOM-DESIGN.

### 7.2 Sample rotation

The Handbook describes five sample rotation groups:

- Three private industry groups.
- One state and local government group.
- One aircraft manufacturing group.

Private industry and aircraft manufacturing establishments rotate approximately every 3 years, except in years when state and local government establishments rotate. State and local government establishments rotate approximately every 10 years. Each private industry group contains one-third of the private sample, and the rotation schedule is staggered so only one private group rotates out in any given year and is replaced by one new group. This reduces respondent burden and keeps the sample current. State and local government is rotated less frequently because establishments in that sector are generally more stable in births/deaths and employment.

Primary source: HOM-DESIGN.

### 7.3 Stage 2: selecting and classifying occupations

Workers counted in an establishment include workers on paid leave, salaried officers/executives/staff of incorporated firms, employees temporarily assigned to other units, and noncontract employees whose permanent duty station is the reporting unit, regardless of payroll issuing unit.

Field economists use a four-step process:

1. Obtain the establishment's complete employee/job-title list and apply probability selection of occupations (PSO), so selection probability is proportional to the number of workers in the job.
2. Match employees in sampled jobs to SOC occupations based on actual duties and responsibilities, not job title or education. If an employee performs two or more occupations, classify by the highest skill level, or by the occupation in which the employee spends the most time when skill difference is not measurable.
3. Identify occupational attributes: full-time/part-time, union/nonunion, and time/incentive pay. A selected occupation/quote must include only workers with the same attributes.
4. Evaluate job duties and responsibilities using point-factor leveling: knowledge, job controls and complexity, contacts, and physical environment. More impact, complexity, or difficulty generally means more points and a higher work level.

The number of jobs selected depends on establishment employment:

| Establishment employment | Jobs selected |
|---|---:|
| 1-49 | Up to 4 |
| 50-249 | 6 |
| 250 or more | 8 |

Exceptions:

- State and local government establishments: up to 20 jobs.
- Aircraft manufacturing, NAICS 336411: up to 32 jobs.

SOC has 23 major occupational groups, but NCS excludes military occupations (55-0000), so NCS occupations can fall into 22 major groups.

Primary source: HOM-DESIGN.

### 7.4 Jobs that cannot be leveled

Some occupations cannot be assigned points for all four leveling factors, so work levels are not assigned. Examples listed in the Handbook include legislators, judges and related legal occupations, actors, producers and directors, athletes and sports competitors, coaches and scouts, dancers and choreographers, music directors and composers, musicians and singers, entertainers and performers, broadcast announcers/radio disc jockeys, and models.

Primary source: HOM-DESIGN.

### 7.5 Supervisory classification

Under SOC rules, supervisors of professional and technical workers usually have a background similar to the workers they supervise and are classified with those workers. Team leaders, lead workers, and supervisors of production, sales, and service workers who spend at least 20 percent of time doing similar work are also classified with the supervised workers. Field economists record supervisory responsibility and level. Most supervisory jobs are evaluated by point-factor leveling, with a modified approach for some professional and administrative supervisors.

Primary source: HOM-DESIGN.

## 8. Relationship to the 2011 design-research paper

The 2011 design paper is useful for understanding why current design differs from the older design. It explains that the older NCS sample used a three-stage sample design of areas, establishments, and jobs. It described a proposed national design using two stages: establishments and jobs. The paper linked the redesign to the shift away from producing locality pay estimates directly from NCS and toward producing those earnings estimates using a model combining NCS national data with Occupational Employment Statistics locality data. It said ECI, ECEC, and benefit measures would continue to be produced using NCS data.

The proposed redesign discussed in the paper included:

- Two stages: establishments, then jobs.
- All sampled establishments supporting all NCS product lines.
- A three-year private industry rotation.
- Aircraft manufacturing sampled separately.
- State and local government sampled about every 10 years.
- Continued use of QCEW as the main frame.
- Supplemental railroad frame data where QCEW lacks full railroad coverage.
- A 24-area frame structure: 15 largest metro areas and the rest of each census division.
- 5 aggregate industry strata and 23 detailed industries.
- Quarterly updates for all establishments under the new design.
- Continued use of existing data-collection processes.
- Continued use of modified Faye's BRR approach for variance.

Use the current Handbook for the current official design. Use the 2011 paper only when explaining design history, redesign motivations, or methodological context.

Primary sources: PDF-DESIGN-2011, HOM-DESIGN.

## 9. Weighting, nonresponse, imputation, and benchmarking

Participation in NCS is voluntary. Establishments may refuse initial participation, refuse or fail to update data, be out of scope, or go out of business. BLS addresses missing data through weight adjustment and imputation. The objective is for published estimates to represent compensation in civilian, private industry, and state and local government sectors.

Primary source: HOM-CALC.

### 9.1 Unit nonresponse adjustment

An establishment is responding if it provides information for at least one usable occupation. A selected occupation is usable if these are present:

- Occupational attributes: full-time/part-time, union/nonunion, and time/incentive pay.
- Work schedule.
- Wage data.

Wages are essential. BLS notes that wages account for about 70 percent of compensation, and without wage data it is not possible to create benefit-cost estimates because many benefits, such as paid leave, are linked to wages.

An establishment is nonresponding if it refuses or does not provide wages/salaries, occupational classification, worker attributes, and work schedule data for any selected occupation. Establishment nonresponse at initiation is handled by redistributing nonrespondent weights to responding sample units in the same ownership, industry, size class, and area.

Primary source: HOM-CALC.

### 9.2 Quote nonresponse adjustment

A quote is a selected job/occupation. Quote nonresponse occurs when an establishment refuses to provide any wage data for a sampled occupation. At initiation, quote nonresponse is handled by redistributing weights to responding sample quotes in the same occupational group, ownership, industry, size class, and area. During updates, quote nonresponse is addressed by imputation.

Primary source: HOM-CALC.

### 9.3 Item imputation

Item nonresponse occurs when an establishment responds but cannot or will not provide some or all benefit data for a sampled occupation. BLS imputes missing values from similar occupations and establishments with similar characteristics.

For benefit estimates, items can be imputed at initial and later collections. Example: if wage and salary data are reported but whether workers receive vacation benefits is missing, BLS imputes vacation incidence based on similar occupations in similar establishments.

For wages and salaries, cost data are not imputed for item nonresponse at initial collection, but are imputed at updates. Example: if an establishment reported wage data at initiation but not at a later update, BLS estimates the rate of wage change for similar workers in similar establishments between the periods, using a regression model fit to establishments reporting wages in both periods, and applies that rate to initiation wages.

Primary source: HOM-CALC.

### 9.4 Benchmarking/poststratification

Benchmarking adjusts establishment weights to match the most current employment distribution by industry. The NCS sample is drawn from QCEW, with QCEW and railroad data from the Railroad Retirement Board and Surface Transportation Board contributing employment data. Because those sources do not always provide current employment at the needed timing, BLS calculates a CES factor to adjust employment. Benchmarking updates initial establishment weights assigned at sampling by current employment.

Benchmarking helps ensure that survey estimates reflect current industry composition for private industry, state government, and local government. Private industry also uses establishment-employment-size class in benchmarking.

In most private industry cases, ECEC employment weights are total employment estimates for two-digit NAICS groups, such as utilities or wholesale trade. Some more detailed categories are used, including elementary and secondary schools (6111), junior colleges (6112), colleges and universities (6113), and aircraft manufacturing (336411). For state and local governments, ECEC uses a more aggregated level, reflecting CES publication detail.

Primary source: HOM-CALC.

### 9.5 Historical 2007 benchmark calculation change

The March 2007 note says the December 2006 ECEC data introduced a benchmark calculation to standardize estimation calculations among NCS products. Benchmarking adjusted each establishment's survey weight to match the distribution of employment by industry at the reference period. The note says the new benchmark factor used QCEW and CES data: QCEW for industry coverage and CES for more current employment. The benchmark process was also refined to account for establishments without any occupations, often owner-only or family-member-only establishments, so they were treated consistently with other NCS programs.

The note gives a simplified benchmark factor:

```text
Benchmark factor_i = Population employment_i / sum(ECEC weight_i)
```

Where population employment is current employment for the industry and ownership group from QCEW and CES, and the denominator sums ECEC sample occupation weights in that industry and ownership group after nonresponse and other subsampling adjustments.

The note says the benchmark change had a negligible effect on estimates and estimated variances.

Primary source: PDF-CALC-2007.

## 10. Technical weighting formulas from the 2011 weighting paper

The 2011 weighting paper is a technical source for how ECEC weights were derived in the NCS sample context of that paper. Treat the formulas as methodological context and examples. Current BLS production systems may differ in implementation details, and public ECEC users usually do not have the microdata or replicate weights needed to reproduce these steps.

Primary source: PDF-WEIGHT-2011.

### 10.1 Initial establishment weight

The paper describes a multi-stage design where the initial establishment weight reflects the inverse probability of selecting an area and the inverse probability of selecting an establishment within a sampled area, multiplied by an allocation adjustment factor:

```text
W0_i = (1 / p_a) * (1 / p_asi) * adj_fct_as
```

Where:

- W0_i = initial weight of establishment i.
- p_a = probability of selecting area a.
- p_asi = probability of selecting establishment i in industry s and area a.
- adj_fct_as = adjustment factor in industry s and area a due to allocation.

### 10.2 Establishment nonresponse adjustment factor (ENRAF)

The paper describes establishment nonresponse cells based on ownership, industry group, size class, and area. It used 24 industry groups and 4 size classes for forming cells. If a cell factor exceeded 4.00 or no usable establishments existed in the cell, cells were collapsed to reduce the impact on mean squared error.

Conceptual ENRAF formula:

```text
ENRAF_C = [sum_U WgtEmp_CU + sum_V WgtEmp_CV] / [sum_U WgtEmp_CU]
```

Where:

- C = nonresponse cell.
- U = in-scope or cooperating establishments at update.
- V = establishments refusing at initiation.
- WgtEmp = weighted employment, generally frame employment times initial weight for the establishment.

### 10.3 Collected Other Than Assigned Factor (COTAF)

The paper also describes COTAF for special collection situations, such as collecting data for more or less than the assigned sampled unit. Conceptually:

```text
COTAF_i = collected employment for establishment i at initiation / frame employment for establishment i
```

COTAF is set to 1.0 when the relevant flag indicates no adjustment.

### 10.4 Final establishment weight

```text
FinalEstWgt_i = W0_i * ENRAF_Ci * COTAF_i
```

The paper states that the final establishment weight is set to 0.0 for initiation refusals and drops.

### 10.5 Occupational nonresponse adjustment factor (ONRAF)

Occupational nonresponse adjusts weights of usable occupations to account for unusable occupations at initiation. Cells begin at the lowest level by SOC group, industry, size class, and area, then collapse to higher levels if needed. As with ENRAF, factors exceeding 4.00 or cells with no usable occupations are collapsed.

Conceptual ONRAF formula:

```text
ONRAF_Cq = [sum_U WgtEmp_CUq + sum_V WgtEmp_CVq] / [sum_U WgtEmp_CUq]
```

Where:

- q = quote.
- U_q = in-scope or cooperating quote q at update in cell C.
- V_q = refusing quote q at update in cell C.
- WgtEmp_C(U,V)q = PSOInterval_iq * ClpsF_q * FinalEstWgt_iq.
- PSOInterval_iq = collected in-scope employment at initiation of establishment i applied to quote q divided by number of assigned quotes.
- ClpsF_q = collapsed-quote factor when the same job quote is selected more than once within an establishment.

### 10.6 Final occupational weight

```text
FinalOccWgt_q = FinalEstWgt_iq * PSOInterval_iq * ClpsF_q * ONRAF_Cq
```

### 10.7 Sample panel factor (SPF) and adjusted final occupational weight

The paper says multiple sample panels were used in estimation, and each sample panel's weights represented the entire frame. Therefore, a sample panel reduction factor was needed before estimation. In the paper's design context, SPF was 0.2 for private industry units except aircraft manufacturing, and 1.0 for government units and aircraft manufacturing units.

```text
AdjFinalOccWgt_q = SPF * FinalOccWgt_q
```

### 10.8 Technical benchmark factor and benchmark-adjusted occupational weight

The paper says the benchmark factor is based on QCEW employment adjusted by the CES employment ratio, divided by adjusted weighted sample employment plus an adjustment for no-in-scope-jobs establishments/occupations.

Conceptual benchmark factor from the paper:

```text
BMF_Cq = [sum QCEW_employment_C * (CES_A / CES_B)]
         / [sum_USE AdjFinalOccWgt_q + sum_NMJ (AsgEmp_i * W0_i * SGF_i)]
```

Where:

- C = benchmark cell.
- CES_A = most current CES employment for cell C.
- CES_B = CES employment for the same period as QCEW in cell C.
- NMJ = establishments where all occupations are not in scope for the survey.
- USE = usable occupations.

Then:

```text
BmkAdjOccWgt_q = AdjFinalOccWgt_q * BMF_Cq
```

The paper says cells are collapsed when the benchmark factor is larger than 4.00 or there are fewer than three contributing establishments. The factor is capped at 4.00 to prevent overrepresentation. In the paper's experience at the time, benchmark factors typically ranged from 0.7 to 2.3.

### 10.9 Coverage discrepancy between ECEC and QCEW

The weighting paper reports that ECEC benchmarked employment can be below CES-adjusted QCEW employment because of coverage differences. Examples include owners and workers who set their own pay: they can be present in QCEW but excluded from ECEC. In the paper's example, the difference between final benchmarked employment and CES-adjusted QCEW employment was about 3.0 percent, and the loss due to no-in-scope jobs was about 3.2 million. Treat these as historical example values only.

Primary source: PDF-WEIGHT-2011.

## 11. Cost estimate calculation

ECEC measures average costs to employers for wages, salaries, and benefits per employee hour worked. The series provides an average cost across all workers. For benefit costs, eligible workers with access who do not participate are included, and workers with no access are included. This means benefit-cost averages include zero-cost workers.

Cost data are published in dollars and as percentages of total compensation. Published cost estimates are quarterly.

Primary source: HOM-CALC.

### 11.1 Employment weights used for cost levels

ECEC uses current employment weights to reflect the changing composition of the labor force. The weights come from QCEW and CES. QCEW provides detailed industry coverage, while CES helps provide a more current timeframe for benchmarking.

Primary source: HOM-CALC.

### 11.2 Mean hourly cost formula

The Handbook presents the formula in image form; the operational idea is a weighted mean over quotes in the domain.

For an agent explaining ECEC methods, a clear schematic expression is:

```text
Mean hourly cost for component c in domain D
  = sum_{q in D} final_weight_q * mean_hourly_cost_{q,c}
    / sum_{q in D} final_weight_q
```

Where:

- D is the domain of interest, such as all manufacturing workers or private industry workers.
- q indexes sampled quotes/selected jobs in the domain.
- final_weight_q is the final quote weight after sampling, nonresponse, imputation/adjustment, and benchmarking steps as applicable.
- mean_hourly_cost_{q,c} is the mean hourly cost for component c for quote q.

The public Handbook states that the unweighted average wage or benefit cost is calculated from all workers within a sampled quote and that the final quote weight is used in the domain formula.

Primary source: HOM-CALC.

### 11.3 Percent of total compensation

The percent of total compensation for component c in domain D is:

```text
Percent_{c,D} = 100 * MeanHourlyCost_{c,D} / MeanHourlyCost_{total compensation,D}
```

BLS calculates percentages from unrounded hourly employer-cost estimates and then rounds percentages to one decimal place. If a user recomputes percentages from rounded published hourly costs, the result can differ slightly.

Primary source: HOM-CALC.

### 11.4 Missing data

When respondents do not provide all needed data, BLS assigns plausible values for missing values through the weighting/nonresponse/imputation/benchmarking processes described above. Do not treat raw respondent records as complete without considering these adjustment steps.

Primary source: HOM-CALC.

## 12. Compensation Percentile Estimates (CPE)

CPE provide current-dollar and constant-dollar 10th-, 50th-, and 90th-percentile wage estimates for civilian, private industry, and state and local government workers. These percentiles are based on wages and salaries. Benefit costs are then calculated for observations in the corresponding wage bands. CPE are available starting with March 2009.

Primary source: HOM-CALC.

### 12.1 Four-percent wage bands

ECEC uses four-percentile-wide bands:

- 10th percentile band: observations with wage rates within the 8th through 12th percentiles.
- 50th percentile band: observations within the 48th through 52nd percentiles.
- 90th percentile band: observations within the 88th through 92nd percentiles.

The four-percent bands enlarge the sample around each target percentile so benefit costs can be estimated for workers around those wage points.

Primary source: HOM-CALC.

### 12.2 Pooling formula and cutoff weights

Sometimes, especially near the 10th percentile, including all observations within a percentile band would exceed the expected 4 percent of total weight. BLS introduced a pooling process that adjusts weights for observations exactly on the lower and upper cutoffs so that only 4 percent of total weight is allocated to each percentile band.

Conceptually:

- Sort observations by wages and salaries and a random number value.
- Calculate cumulative weights.
- Define lower and upper cutoffs for the target percentile p.
- Adjust weights for observations at the cutoffs using conditions that determine whether full, partial, or zero weight enters the band.

The random number is used so observations from all weight classes are eligible for inclusion, improving representation of small, medium, and large establishments.

Primary source: HOM-CALC.

### 12.3 Constant-dollar CPE

Constant-dollar CPE adjust nominal CPE by CPI to express estimates in real terms. The Handbook states that constant dollar estimates are produced by taking current-dollar CPE and adjusting them by the Consumer Price Index. Presentation guidance says the CPI-U U.S. City Average All Items is used to adjust prior years' costs to current-dollar costs for CPE revisions.

A schematic expression is:

```text
Adjustment factor_t = CPI_reference / CPI_t
Constant dollar estimate_t = Current dollar estimate_t * Adjustment factor_t
```

Use BLS's published CPE series for actual values rather than recomputing unless CPI reference-period details are known.

Primary sources: HOM-CALC, HOM-PRESENTATION.

## 13. Estimate reliability and variance

ECEC estimates are based on a sample, so they can contain sampling error. They can also contain nonsampling error from data collection, data processing, respondent reporting, or other non-sampling sources.

Primary source: HOM-CALC.

### 13.1 Standard errors and comparisons

A standard error measures variation among sample estimates. BLS states that the chances are about 68 out of 100 that a survey estimate differs from a complete-population value by less than one standard error, and about 90 out of 100 that the difference is less than 1.6 standard errors.

Statements of comparison in ECEC publications are significant at 1.6 standard errors or better. When comparing estimates, use the standard error of the difference, not just the standard errors of the two estimates independently.

Primary source: HOM-CALC.

### 13.2 Current BRR approach in the Handbook

ECEC uses a variation of balanced repeated replication (BRR) to estimate standard errors. Current Handbook description:

- Partition the sample into 120 variance strata.
- Split sample units in each variance stratum evenly into two variance primary sampling units (PSUs).
- Choose balanced half-samples so each half-sample contains exactly one variance PSU from each variance stratum.
- For each half-sample, compute a replicate estimate using the regular estimate formula but adjusted final weights.
- Use 120 replicates.
- If a unit is in the half-sample, multiply its weight by (2 - k). If it is not in the half-sample, multiply its weight by k.
- For NCS publications, k = 0.5, so multipliers are 1.5 and 0.5.

Schematic current BRR standard error:

```text
SE(Y) = sqrt( [1 / (R * (1 - k)^2)] * sum_{r=1..R} (Y_r - Y)^2 )
```

Where:

- R = number of replicate estimates, currently 120 in the Handbook.
- k = 0.5 in NCS publications.
- Y_r = replicate estimate r.
- Y = full-sample estimate.

Primary source: HOM-CALC.

### 13.3 Percent relative standard error

Percent relative standard error (RSE) expresses the standard error as a percentage of the full-sample estimate:

```text
Percent RSE = 100 * SE(Y) / Y
```

ECEC publications provide percent RSE data alongside estimates.

Primary source: HOM-CALC.

### 13.4 Nonsampling error controls

BLS mitigates collection and processing errors through quality assurance programs such as:

- Data collection reinterviews.
- Observed interviews.
- Computer edits.
- Systematic professional review.
- Extensive field economist training.

Before publication, BLS validates estimates against expected values and context, including historical trends, economic conditions and indicators, legislation, labor-management disputes, sample composition, sample rotation, and changes in compensation structure.

Primary source: HOM-CALC.

### 13.5 Historical 2007 variance change

The 2007 variance note documents a change introduced with December 2006 ECEC data released in March 2007 to standardize variance calculations among NCS products.

Historical change:

- Old replicate weight factors: 0 or 2, meaning a quote was excluded or doubled in a replicate.
- Revised replicate weight factors: 0.5 or 1.5, so every replicate includes all survey data but with different weight adjustments.
- Old final variance multiplying factor: 1 / number of replicates = 1 / 128 = 0.0078125.
- Revised final multiplier at that time: 1 / [R * (1 - k)^2] = 0.0313, where R = 128 and k = 0.5.

Historical revised variance formula:

```text
V(Y_ct) = 0.0313 * sum_{r=1..R} (Y_ctr - Y_ct)^2
```

Where Y_ctr is replicate r for characteristic c at time t, and Y_ct is the full-sample estimate. Use the current Handbook's 120-replicate description for current ECEC explanations.

Primary source: PDF-VAR-2007, HOM-CALC.

## 14. Presentation, publications, and access

ECEC publications provide estimates for March, June, September, and December reference periods. They measure average employer cost for wages, salaries, and benefits per employee hour worked and costs as a percent of total compensation. Estimates include private and public sector workers, union and nonunion workers, full-time and part-time workers, and establishment-size categories. Estimates are classified by NAICS, SOC, and area.

Primary source: HOM-PRESENTATION.

### 14.1 Publications and data products

Main ECEC outputs include:

- Quarterly ECEC news release, released in March, June, September, and December. It contains summary text, data tables, and a technical note.
- Interactive charts.
- Public database tools with available data.
- Historical tables and spreadsheets for civilian, private industry, and state and local government workers.
- Relative standard error tables.

For the March ECEC release, supplementary data are also released:

- CPE data based on wage percentile bands and benefit costs for observations in those bands.
- Metropolitan area data, available starting in 2009 for private industry only.

Primary source: HOM-PRESENTATION.

### 14.2 Users and uses

Private-sector uses include:

- Collective bargaining negotiations.
- Evaluating benefit packages.
- Analyzing contract settlements.
- Business or plant location decisions.
- Wage and salary administration.
- Adjusting wages in long-term contracts.

Public-sector uses include:

- Formulating and assessing public policy.
- Collective bargaining negotiations.
- Evaluating benefit packages.
- Analyzing contract settlements.
- Benchmarking compensation costs.
- Setting minimum wages and benefit payments.
- Estimating benefit expenditures.

Primary source: HOM-PRESENTATION.

### 14.3 Revisions and corrections

ECEC cost estimates are final upon publication. CPE have some revisions released only with the March publication; constant-dollar CPE are revised to reflect the most recent year. Each year, constant-dollar real estimates are updated to reflect the most recent reference period. If an error is discovered in ECEC data, the product is corrected and republished, and corrections are noted on the publication, ECEC homepage, and BLS errata page.

Primary source: HOM-PRESENTATION.

### 14.4 Special tabulations

Special tabulations are evaluated by resource availability and complexity. ECEC does not produce individual state estimates because the NCS is not designed for state-level ECEC estimates. Special tabulations are reviewed for reliability and confidentiality before release, which may limit the data provided.

When citing a special tabulation, say it is an unpublished estimate from the Bureau of Labor Statistics, National Compensation Survey, Employer Costs for Employee Compensation, and include the reference period.

Primary source: HOM-PRESENTATION.

### 14.5 Microdata

ECEC microdata are available only on a limited basis to researchers conducting valid statistical analyses, generally through BLS restricted data access. Researchers should apply early and discuss projects with BLS contacts before applying.

Primary source: HOM-PRESENTATION.

## 15. Agent interpretation rules

Use these rules when answering questions about ECEC.

### 15.1 Always identify the estimate context

Before interpreting or comparing an ECEC number, identify:

- Reference period.
- Ownership: civilian, private industry, or state/local government.
- Component: total compensation, wages and salaries, total benefits, or specific benefit.
- Datatype: dollars per hour worked, percent of total compensation, CPE, current dollar, or constant dollar.
- Classification: industry, occupation, region/division/metro, union/nonunion, full-time/part-time, establishment size.
- Whether estimate reliability/RSE is available and whether a comparison is statistically significant.

### 15.2 Do not treat benefit costs as participant-only costs

ECEC benefit cost estimates average over all workers in the domain. This includes workers without access to the benefit, workers with access who do not participate, and workers for whom the employer has zero cost. Therefore, ECEC benefit cost per hour is not the same as average employer cost per participating employee.

Primary sources: HOM-CONCEPTS, HOM-CALC.

### 15.3 Do not recompute percentages from rounded costs

BLS computes percent of total compensation from unrounded hourly costs and then rounds. Recomputed percentages from published rounded dollar amounts may differ slightly.

Primary source: HOM-CALC.

### 15.4 Do not call ECEC a price index

ECEC is a cost-level series: average employer cost per employee hour worked. ECI is the compensation-cost index product from NCS; ECEC is not the ECI. Use ECI for index/trend questions that require fixed-employment-weight compensation change over time. Use ECEC for current compensation cost levels and shares.

Primary sources: HOM-OVERVIEW, HOM-DATA, HOM-CALC.

### 15.5 Use current data sources for current estimates

This file describes methods. It should not be used to answer questions requiring current dollar estimates, latest releases, or updated tables unless the values are retrieved from current BLS ECEC data products. For current or historical numerical estimates, use the BLS ECEC homepage, news releases, historical spreadsheets, public database tools, or API as appropriate.

Primary source: HOM-PRESENTATION.

### 15.6 Use current Handbook over older PDFs

When explaining the current program:

- Use current Handbook design and calculation pages.
- Use 2007 and 2011 PDFs as historical background or deeper technical context.
- Explain conflicts, such as 120 current BRR replicates versus 128 in the 2007 historical variance note.

### 15.7 Be careful comparing public and private sectors

ECEC can compare average employer costs across sectors, but differences reflect many factors, including occupation and industry mix, unionization, full-time/part-time composition, establishment size, benefit incidence, and benefit generosity. Do not infer that sector differences are pure pay premiums without controlling for composition.

Primary sources: HOM-CONCEPTS, HOM-PRESENTATION.

### 15.8 No state estimates

ECEC does not produce individual state estimates. If asked for state ECEC, explain that the NCS is not designed to produce state-level ECEC estimates. Use available census region, census division, national, or selected metro estimates if appropriate.

Primary source: HOM-PRESENTATION.

## 16. Operational status codes from the 2011 weighting paper

The 2011 weighting paper includes operational status codes used in its weighting examples. Use these only for technical context unless working with internal NCS-style microdata documentation.

| Code | Establishment meaning | Occupation meaning |
|---|---|---|
| USE | Usable; at least one usable occupation; occupation has required characteristics, work schedule, and wage data | Usable occupation with worker characteristics, work schedule, and wage data |
| TNR | Temporary refusal at establishment update | Not listed as occupation status in the same way in the paper's summary |
| VAC | All occupations vacant or temporary seasonal condition | Occupation temporarily vacant or seasonal condition |
| STR | All occupations on strike | Occupation on strike |
| REF | Permanent refusal to provide data | Permanent refusal for the occupation; missing earnings/SOC/worker characteristics/work schedule |
| NMJ | No in-scope jobs; collected in-scope employment is zero, such as owner-only situations | Selected occupation out of scope for PSO, including owners who should have been excluded |
| OOS | Establishment out of survey scope | Not shown as occupation status in summary |
| OOB | Establishment out of business | Not shown as occupation status in summary |
| ABO | Occupation abolished at update | Occupation abolished at update |

Primary source: PDF-WEIGHT-2011.

## 17. Industry cells and strata context

Current Handbook: the establishment sample uses 5 industry strata and 24 geographic subsets, for 120 sampling cells. The 5 aggregate industries comprise 23 detailed NAICS sectors.

The 2011 design paper's private-industry appendix maps 23 detailed industries into 5 aggregate groups. Use this as context for sample allocation and selection, not as a substitute for current BLS classification documentation.

### 17.1 Private industry detailed industries in the 2011 design paper

| Aggregate group | Detailed industry | NAICS included |
|---|---|---|
| Education | Educational services, rest of | 61 excluding 6111-6113 |
| Education | Elementary and secondary schools | 6111 |
| Education | Junior colleges, colleges, and universities | 6112, 6113 |
| Finance, insurance, and real estate | Finance, rest of | 52 excluding 524 |
| Finance, insurance, and real estate | Insurance | 524 |
| Finance, insurance, and real estate | Real estate, renting, leasing | 53 |
| Goods producing | Mining | 21 |
| Goods producing | Construction | 23 |
| Goods producing | Manufacturing excluding aircraft | 31-33 excluding 336411 |
| Health care, hospitals, and nursing care | Health care and social assistance, rest of | 62 excluding 622, 623 |
| Health care, hospitals, and nursing care | Hospitals | 622 |
| Health care, hospitals, and nursing care | Nursing and residential care facilities | 623 |
| Service providing | Utilities | 22 |
| Service providing | Wholesale trade | 42 |
| Service providing | Retail trade | 44-45 |
| Service providing | Transportation and warehousing | 48-49 |
| Service providing | Information | 51 |
| Service providing | Professional, scientific, and technical services | 54 |
| Service providing | Management of companies and enterprises | 55 |
| Service providing | Administrative/support/waste management | 56 |
| Service providing | Arts, entertainment, and recreation | 71 |
| Service providing | Accommodation and food services | 72 |
| Service providing | Other services excluding public administration | 81 excluding 814 |

Primary source: PDF-DESIGN-2011.

### 17.2 Weighting-paper industry cells

The 2011 weighting paper's Appendix D uses 24 private industry cells and 10 state plus 10 local government industry cells for its weighting and benchmarking context. The private list includes aircraft manufacturing as its own cell and splits categories such as finance versus insurance and hospitals versus nursing homes. State and local government cells include goods-producing; trade/transportation/utilities; elementary and secondary education; colleges and universities; rest of education; hospitals; nursing homes; rest of health and social services; public administration excluding NAICS 928; and other service-producing.

Primary source: PDF-WEIGHT-2011.

## 18. Worker inclusion/exclusion details from the 2011 weighting paper

The 2011 weighting paper gives examples for collected in-scope employment. Treat as technical context. Included workers can include employees on family leave, executive loan, sabbatical, sick leave, strike less than a year, leave without pay during shutdown, seasonal workers, adjunct faculty, temporary workers/trainees, religious workers, personalized/red-circle/blue-circle rate employees, family members with market earnings, substitute teachers, contingent workers, and elected officials/government-funded positions. Exclusions include contractors, proprietors, owners, owner managers, major stockholders, family members without market earnings, bona fide partners, work/study students, long-term disability cases not expected to return, non-working individuals with no guarantee to return, employees on strike more than a year, volunteers/unpaid workers, employees outside the assigned area, token-wage employees, temporary-help employees, and leased employees.

Primary source: PDF-WEIGHT-2011.

## 19. Common question patterns and recommended agent responses

### Q: What does ECEC measure?

Answer: It measures average employer cost per employee hour worked for wages and salaries, benefits, total compensation, and component shares of total compensation. It is based on NCS data and reference-period pay periods including the 12th of March, June, September, and December.

Sources: HOM-OVERVIEW, HOM-CONCEPTS.

### Q: Why does ECEC benefit cost seem low compared with employer premiums for enrolled workers?

Answer: ECEC benefit cost averages over all workers in the domain, including workers with no access, workers who do not participate, and workers for whom the employer incurs zero cost. It is not an enrolled-worker-only average.

Sources: HOM-CONCEPTS, HOM-CALC.

### Q: Can I use ECEC for state-level estimates?

Answer: No. BLS says ECEC does not produce estimates for individual states because NCS is not designed to produce state-level ECEC estimates. Use national, census region/division, or available metro estimates.

Source: HOM-PRESENTATION.

### Q: Are ECEC estimates revised?

Answer: ECEC cost estimates are final upon publication. CPE constant-dollar estimates can be revised annually to reflect the most recent year. Errors, if discovered, are corrected and republished with notices.

Source: HOM-PRESENTATION.

### Q: How are percent-of-compensation estimates calculated?

Answer: BLS calculates them from unrounded hourly employer costs, then rounds to one decimal place. Percentages calculated from rounded published hourly costs may differ slightly.

Source: HOM-CALC.

### Q: How should I compare two ECEC estimates?

Answer: Use standard errors or relative standard errors and the standard error of the difference. BLS statements of comparison are significant at 1.6 standard errors or better, approximately a 90 percent standard.

Source: HOM-CALC.

### Q: Why are older papers describing three sampling stages when the current Handbook says two?

Answer: The 2011 design paper describes the older area-based design and the planned redesign. The current Handbook is the authority for current design and says NCS data are selected in two stages: establishments and occupations.

Sources: PDF-DESIGN-2011, HOM-DESIGN.

## 20. Minimal formula reference

Use these formulas as explanatory summaries, not as a claim that public users can reproduce BLS production estimates without restricted microdata and BLS processing systems.

```text
Total compensation = Wages and salaries + Benefits
```

```text
Mean hourly cost_{c,D} = sum_{q in D} W_q * C_{q,c} / sum_{q in D} W_q
```

```text
Percent of total compensation_{c,D}
  = 100 * Mean hourly cost_{c,D} / Mean hourly cost_{total compensation,D}
```

```text
Percent RSE = 100 * SE(Y) / Y
```

```text
Current BRR standard error (schematic)
SE(Y) = sqrt( [1 / (R * (1 - k)^2)] * sum_{r=1..R} (Y_r - Y)^2 )
where current Handbook says R = 120 and k = 0.5 for NCS publications.
```

```text
Historical 2007 variance note
V(Y_ct) = 0.0313 * sum_{r=1..128} (Y_ctr - Y_ct)^2
```

```text
Historical 2007 benchmark note
Benchmark factor_i = Population employment_i / sum(ECEC weight_i)
```

## 21. Final cautions for downstream AI agents

- Do not invent current ECEC values; retrieve them from current BLS data products.
- Do not treat ECEC as state-level data.
- Do not treat benefit costs as costs among participants only.
- Do not infer causal sector pay differences from simple ECEC averages.
- Do not use older methodological papers as current authority where the current Handbook differs.
- Do not ignore standard errors when comparing estimates.
- Do not mix current-dollar and constant-dollar CPE.
- Do not classify production bonuses and nonproduction bonuses the same way: production/incentive pay is wages; nonproduction bonuses are supplemental-pay benefits.
- Do not define full-time or part-time using a universal hours cutoff; ECEC uses establishment definitions.
- Do not recompute percent-of-total-compensation from rounded published dollar costs and expect exact agreement.
