# OEWS (Occupational Employment and Wage Statistics)

## 1. What OEWS measures

OEWS estimates employment and wages for about 830 occupations of the 2018 SOC, for wage and salary workers in nonfarm establishments. It covers 22 of the 23 SOC major groups; major group 55 (military-specific occupations) is out. Self-employed workers, owners and partners in unincorporated firms, private-household employees and unpaid family workers are out of scope. ([HOM Concepts][5])

- **Employment** is the estimated number of full- and part-time **jobs** in an occupation, not persons. ([HOM Concepts][5])
- **Wages** are straight-time gross pay. Base rate, cost-of-living allowances, guaranteed pay, hazardous-duty pay, incentive pay (commissions, production bonuses) and tips are in. Overtime, shift differentials, nonproduction bonuses, severance and employer benefit costs are out. ([HOM Concepts][5])
- **Annual wages** are hourly wages times 2,080 hours (52 weeks times 40 hours). Teachers, pilots and flight attendants have annual wages only. Actors and musicians have hourly wages only. ([HOM Concepts][5], [HOM Calculation][7])
- **Industry and ownership.** Establishments are classified by NAICS (2022 NAICS since May 2022). Most government establishments are classified by ownership instead: OEWS-defined codes 999100 (federal executive branch and TVA), 999200 (state government, excluding schools and hospitals) and 999300 (local government, excluding schools, hospitals, gambling establishments and casino hotels) replace NAICS sector 92. USPS sits in NAICS 491100 in the industry-specific estimates. ([HOM Concepts][5])
- **Industry scope.** Most of agriculture is out. Logging (113310) and support activities for crop and animal production (1151, 1152) are in. Private households (NAICS 814) are out. ([HOM Concepts][5])
- **Geography.** The estimates cover the nation, the 50 states, DC, Guam, Puerto Rico and the Virgin Islands, and about 530 metropolitan and nonmetropolitan areas. The sampling design uses over 580 MSA and nonmetropolitan (balance-of-state) areas. ([HOM Concepts][5], [HOM Design][6])
- **Limit.** Cross-industry estimates are available by nation, state and metro area. Industry-specific estimates are available at the **national** level only. ([oe.txt][1]) There are no state x industry x SOC cells in these files.
- **Precision.** The estimator is model-based (MB3). The relative standard errors measure model error, not nonmodel error such as bias. ([HOM Presentation][8])

---

## 2. Panel design and reference periods

- **Two panels a year.** One panel is collected in May and one in November. Each holds about 186,000 to 189,000 establishments. Respondents report their payroll that **includes May 12 or November 12**. ([HOM Design][6])
- **Six panels per estimate.** Each annual estimate combines six semiannual panels, a 3-year cycle of about 1.1 million establishments. The May 2025 estimates combine May 2025, November 2024, May 2024, November 2023, May 2023 and November 2022. ([HOM Design][6], [HOM Calculation][7])
- **Estimates are published once a year**, with the May panel as the reference month. The "May 2025" vintage is not a May 2025 cross-section. It pools data from November 2022 on. ([HOM Calculation][7])
- **Consecutive vintages overlap.** From the six-panel window above, two consecutive May vintages share four of their six panels. (Inference from the published window, not a BLS sentence.) Do not treat adjacent vintages as independent samples.
- **Government data are a census.** The federal executive branch, USPS and TVA (annual), state government excluding schools and hospitals (each November) and Hawaii local government (each November) enter at the most recent year only. ([HOM Data sources][9], [HOM Design][6])
- **Employment control.** Each in-scope establishment's employment is the average of its May and November QCEW employment for the two most recent panels, so occupational employment sums to the QCEW-based population. ([HOM Data sources][9], [HOM Calculation][7])
- **Frame.** The frame is about 8.8 million UI-reporting establishments from QCEW, extracted every 6 months. ([HOM Design][6])
- **Substate sums.** A few establishments give a state but no county. They count in state and national estimates but not in any substate area, so the metro and nonmetropolitan areas of a state can sum to less than the state. ([HOM Design][6])

---

## 3. Vintages and comparability over time

Each set of estimates mixes three years of panels. A classification change therefore takes three years to phase in. ([HOM History][10])

| Change | Vintage | What happened |
|---|---|---|
| SOC 2000 to SOC 2010 | May 2010 to May 2012 | May 2010 and May 2011 used a hybrid of the 2000 and 2010 SOC with some OEWS-specific combinations. May 2012 to May 2018 are 2010 SOC. |
| Occupation aggregation | May 2017 | 21 SOC detailed occupations were replaced by SOC broad occupations or OEWS-specific combinations. |
| SOC 2010 to SOC 2018 | May 2019 to May 2021 | May 2019 and May 2020 used a hybrid of the 2010 and 2018 SOC, with combinations found in neither. May 2021 and later are fully 2018 SOC. |
| NAICS updates | May 2008, May 2012, May 2017, May 2022 | 2007, 2012, 2017 and 2022 NAICS. |
| Gambling and casinos | May 2014 | Local government gambling establishments and casino hotels moved from industry 9993 to NAICS 7132 and 72112. |
| Private households | May 2017 | Some establishments moved from NAICS 814 (out of scope) to NAICS 624120 (in scope). Employment in occupations common in 624120 can rise. |
| Sample size | May 2017 | Panels fell from about 200,000 establishments. |
| Estimator | May 2021, May 2022 | MB3 replaced the earlier method in May 2021. May 2022 changed wage processing: reported wage rates now represent private-sector and local government employers, instead of 12 wage intervals. |
| Geography | May 2005, May 2015, May 2024 (major), May 2018 (detail) | See the delineation table in section 5. |

Other facts that matter across vintages ([HOM History][10]):

- The program was named Occupational Employment Statistics (OES) before spring 2021. Older pages and files use that name.
- Before 2002 the program collected 400,000 establishments a year with a fourth-quarter reference. From 2002 it uses the May 12 and November 12 reference dates. It published semiannually in 2003 and 2004 and went back to annual publication in 2005.
- The 1988-95 predecessor data are national, by 2- and 3-digit SIC industry, with no wages or state data. They are not directly comparable to current data.
- The 1997 and 1998 estimates used an OEWS-specific occupation system. The SOC began with the 1999 estimates.

The BLS Handbook does not state a break test for each of these changes. Treat a level comparison across a row above as a comparison across a definition change, and check the occupation or industry code in both vintages.

---

## 4. Series ID anatomy

`oe.txt` lists the `oe.series` columns and a series ID of the form `OEUM000040000000000000001`. ([oe.txt][1])

| Part | Chars | Example | Meaning |
|---|---|---|---|
| Survey abbreviation | 1-2 | `OE` | Survey code. |
| `seasonal` | 3 | `U` | Seasonal code. The `oe.txt` example is `U`. |
| `areatype_code` | 4 | `M` | Area type. `N` national, `S` state, `M` metropolitan or nonmetropolitan area. |
| `area_code` | 5-11 | `0000400` | 7-character area code. |
| `industry_code` | 12-17 | `000000` | 6-character OEWS industry code. |
| `occupation_code` | 18-23 | `000000` | 6-character SOC-based code. |
| `datatype_code` | 24-25 | `01` | Measure. See section 6. |

The `oe.txt` layout gives field lengths. The character positions above are the running sum of those lengths, so they are derived from `oe.txt` and not printed in it. The example is 25 characters. The `series_id` column is declared 30 characters wide. ([oe.txt][1])

Other `oe.series` columns that are not part of the ID breakdown: `state_code` (2), `sector_code` (6, for example `11--12`), `series_title`, `footnote_codes`, and the begin and end year and period. ([oe.txt][1]) The ID breakdown in the data-file section of `oe.txt` leaves out `areatype_code`, but it prints the same 25-character example. The `oe.series` section includes it.

Data files carry `series_id`, `year`, `period`, `value` (12 wide) and `footnote_codes`. ([oe.txt][1])

---

## 5. Flat files

Use the BLS flat files under:

```text
https://download.bls.gov/pub/time.series/oe/
```

```text
oe.data.0.Current      # current release observations
oe.data.1.AllData      # all year-to-date data
oe.series              # series metadata / code decomposition
oe.area                # geography codes
oe.areatype            # geography type labels
oe.datatype            # employment and wage measure labels
oe.industry            # OEWS industry codes and display levels
oe.occupation          # SOC occupation codes
oe.sector              # sector labels
oe.release             # current release metadata
oe.seasonal            # seasonal code labels
oe.footnote            # footnote labels
oe.txt                 # layout documentation
```

([oe.txt][1]) Read the current release from `oe.release` rather than hard-coding it. `oe.release` has `release_date` (for example `2004S01`) and a description (for example `May 2004`). ([oe.txt][1])

### File parsing rules

OEWS data and series files are ASCII text with headers. The documentation says data elements in the main data files are separated by spaces and mapping files are tab-delimited. ([oe.txt][1])

```python
DATA_FILES_SPACE_DELIMITED = ["oe.data.0.Current", "oe.series"]
MAPPING_FILES_TAB_DELIMITED = [
    "oe.area", "oe.areatype", "oe.datatype", "oe.industry",
    "oe.occupation", "oe.sector", "oe.release", "oe.seasonal", "oe.footnote"
]
```

`oe.series` is the metadata spine. It holds `series_id`, `seasonal`, `areatype_code`, `industry_code`, `occupation_code`, `datatype_code`, `state_code`, `area_code`, `sector_code`, a title, and begin and end metadata. Keep all codes as strings so leading zeros survive. ([oe.txt][1])

---

## 6. Measures

`oe.datatype` defines these `datatype_code` values:

| datatype_code | measure                                                 |
| ------------- | ------------------------------------------------------- |
| 01            | employment                                              |
| 02            | employment percent relative standard error              |
| 03            | hourly mean wage                                        |
| 04            | annual mean wage                                        |
| 05            | wage percent relative standard error                    |
| 06-10         | hourly wage percentiles: 10th, 25th, median, 75th, 90th |
| 11-15         | annual wage percentiles: 10th, 25th, median, 75th, 90th |
| 16            | employment per 1,000 jobs                               |
| 17            | location quotient                                       |

Codes 16 and 17 are different in kind from the core estimates. Do not mix them with employment and wage values.

Storage: employment is rounded to the nearest ten, hourly wages to the cent, annual wages to the dollar, and percent RSEs to one decimal place. ([oe.txt][1]) Percentile wages come from the empirical distribution of the predicted population. ([HOM Calculation][7])

---

## 7. Geography

`oe.series` joins to `oe.area` on `state_code`, `area_code` and `areatype_code`. The area file holds `state_code`, `area_code`, `areatype_code` and `area_name`. National is `state_code=00`, `area_code=0000000`, `areatype_code=N`. States use `areatype_code=S`. Metropolitan and nonmetropolitan areas use `areatype_code=M`.

### OMB delineation adoption (matters only if `areatype_code = "M"` rows are kept)

Each May vintage is an independent cross-section, so OEWS metro estimates never break *within* a series; instead the set of `area_code`s and their county compositions changes between vintages. The bulletin behind each vintage:

| May vintage (release) | Delineation | How established |
|---|---|---|
| May 2012–May 2014 (released 2013–2015) | pre-2013 (2009) delineations | Inferred from the published area lists: the metros that Bulletin 13-01 created (The Villages, FL; Daphne-Fairhope-Foley, AL; Hammond, LA; California-Lexington Park, MD) are absent. |
| May 2015–May 2016 (released March 2016 and March 2017) | OMB Bulletin 13-01 | Inferred from the area lists: the 13-01 metros appear from May 2015 while Enid, OK is still nonmetropolitan. |
| May 2017–May 2018 (released March 2018 and March 2019) | OMB Bulletin 15-01 | Inferred: Enid, OK appears as an MSA from May 2017 while Twin Falls, ID is still nonmetropolitan. May 2018 also **dropped all metropolitan-division estimates** and consolidated nonmetropolitan areas from 167 to 134 (BLS notice of 2019-03-29). |
| May 2019–May 2023 (released 2020 through 2024) | OMB Bulletin 17-01 | BLS-stated: the May 2019 release's technical note says the estimates "use the metropolitan area definitions delineated in OMB Bulletin 17-01, which add a new MSA for Twin Falls, Idaho"; the May 2020–May 2023 technical notes repeat 17-01. Bulletin 18-03 (one micropolitan addition) is invisible to OEWS; 18-04 and 20-01 were never adopted by any BLS federal-state program. |
| May 2024 onward (released April 2025 onward) | OMB Bulletin 23-01 (2020 Census standards) | BLS-stated: notice of 2025-03-05 and the May 2024 and May 2025 technical notes. New MSAs added, others renamed, recomposed, or dropped; NECTAs discontinued in favor of county-based New England MSAs; nonmetropolitan areas redrawn to match. |

Rules:

- Never join two vintages' metro rows on `area_code` across a boundary in this table without checking composition in each vintage's area-definition list (`https://www.bls.gov/oes/<year>/may/msa_def.htm` for May 2016 onward; earlier lists survive only in the Wayback Machine). Twelve MSAs were dropped and 27 added at May 2024 alone.
- Nonmetropolitan areas are OEWS-specific groupings set with the state workforce agencies, not OMB geography; they were redrawn at May 2018 and May 2024.
- Rows marked "inferred" are read off the published area lists, not from a BLS sentence naming the bulletin; the technical notes before May 2019 name none.

Sources: https://www.bls.gov/oes/notices/2024/msa-changes.htm; https://www.bls.gov/oes/notices/2019/areas_2018.htm; https://www.bls.gov/oes/current/oes_tec.htm and the per-year `https://www.bls.gov/oes/<year>/may/oes_tec.htm`; https://www.bls.gov/news.release/archives/ocwage_03312020.htm (May 2019 technical note); https://www.bls.gov/bls/msa-redelineation-announcement.htm.

---

## 8. Occupations

`oe.occupation` has `occupation_code`, `occupation_name`, `occupation_description`, `display_level`, `selectable` and `sort_sequence`. `000000` is All Occupations.

* `display_level = 0`: major SOC groups, for example `110000`.
* `display_level = 1`: minor groups, for example `111000`.
* `display_level = 2`: broad SOC, for example `112020`.
* `display_level = 3`: detailed SOC, for example `112021`.

OEWS publishes most 2018 SOC detailed occupations. For a few it publishes only the broad occupation or an OEWS-specific combination of detailed occupations. ([HOM Concepts][5])

---

## 9. Industry scope and the CES crosswalk

### 9.1 OEWS industry levels

`oe.series.industry_code` joins to `oe.industry.industry_code`. The mapping has `industry_code`, `industry_name`, `display_level`, `selectable` and `sort_sequence`. `000000` is cross-industry all ownership. `000001` is cross-industry private only. `display_level=2` rows are broad NAICS sector rows such as construction, manufacturing and retail. State series carry only cross-industry codes. National series carry the industry detail. National industry-specific estimates go to the sector, 3-digit, most 4-digit and selected 5- and 6-digit NAICS levels. ([HOM Concepts][5], [HOM Presentation][8])

### 9.2 CES and QCEW high-level hierarchy

BLS QCEW documents high-level aggregation above NAICS sectors: total, two domains, supersectors and NAICS sectors. ([Bureau of Labor Statistics][3]) The QCEW high-level titles include `10 Total, all industries`, `101 Goods-Producing`, `102 Service-Providing`, and supersectors such as natural resources and mining, construction, manufacturing, trade/transportation/utilities, information, financial activities, professional/business services, education/health, leisure/hospitality, other services and public administration. ([Bureau of Labor Statistics][3]) The CES state publication hierarchy similarly defines total nonfarm, total private, goods-producing, service-providing, private service-providing, supersectors and sector-level breakouts. ([Bureau of Labor Statistics][4])

### 9.3 Crosswalk from OEWS sector rows to CES

```text
national:
  00 Total Nonfarm / OEWS all industries -> oe_industry_code 000000
  05 Total Private -> oe_industry_code 000001, if available

domain:
  06 Goods-Producing -> derive from CES goods-producing supersector components
  07 Service-Providing -> derive from private service-providing + government
  08 Private Service-Providing -> derive from private service supersectors

supersector:
  10 Mining and Logging -> NAICS 1133 + 21
  20 Construction -> NAICS 23
  30 Manufacturing -> NAICS 31-33
  40 Trade, Transportation, and Utilities -> NAICS 42, 44-45, 48-49, 22
  50 Information -> NAICS 51
  55 Financial Activities -> NAICS 52, 53
  60 Professional and Business Services -> NAICS 54, 55, 56
  65 Education and Health Services -> NAICS 61, 62
  70 Leisure and Hospitality -> NAICS 71, 72
  80 Other Services -> NAICS 81
  90 Government -> OEWS government including schools/hospitals/USPS if available

sector:
  41 Wholesale Trade -> NAICS 42
  42 Retail Trade -> NAICS 44-45
  43 Transportation and Utilities -> NAICS 48-49 + 22
  43-400089 Transportation and Warehousing -> NAICS 48-49
  43-220000 Utilities -> NAICS 22
  55-520000 Finance and Insurance -> NAICS 52
  55-530000 Real Estate and Rental and Leasing -> NAICS 53
  60-540000 Professional, Scientific, and Technical Services -> NAICS 54
  60-550000 Management of Companies and Enterprises -> NAICS 55
  60-560000 Administrative and Waste Services -> NAICS 56
  65-610000 Educational Services -> NAICS 61
  65-620000 Health Care and Social Assistance -> NAICS 62
  70-710000 Arts, Entertainment, and Recreation -> NAICS 71
  70-720000 Accommodation and Food Services -> NAICS 72
```

Do **not** silently use OEWS `11--12 Agriculture, Forestry, Fishing and Hunting` as CES mining/logging. CES mining and logging is much narrower: logging plus mining. Treat it as a special crosswalk case.

### 9.4 Aggregating across OEWS cells

- Employment can be summed from component sectors when all components are present.
- Mean wages can be employment-weighted from component means: `mean_wage_agg = sum(employment_i * mean_wage_i) / sum(employment_i)`.
- Wage percentiles **cannot** be aggregated from component percentiles.
- RSEs cannot be aggregated by simple arithmetic.
- State x industry cells do not exist in these files (section 1).

---

## Sources

[1]: https://download.bls.gov/pub/time.series/oe/oe.txt "download.bls.gov"
[3]: https://www.bls.gov/cew/classifications/industry/industry-supersectors.htm "Quarterly Census of Employment and Wages :  U.S. Bureau of Labor Statistics"
[4]: https://www.bls.gov/sae/additional-resources/guaranteed-publication-levels-and-the-ces-small-domain-model-sdm.htm "Guaranteed publication levels and the CES Small Domain Model (SDM) :  U.S. Bureau of Labor Statistics"
[5]: https://www.bls.gov/opub/hom/oews/concepts.htm "OEWS Handbook of Methods: Concepts"
[6]: https://www.bls.gov/opub/hom/oews/design.htm "OEWS Handbook of Methods: Design"
[7]: https://www.bls.gov/opub/hom/oews/calculation.htm "OEWS Handbook of Methods: Calculation"
[8]: https://www.bls.gov/opub/hom/oews/presentation.htm "OEWS Handbook of Methods: Presentation"
[9]: https://www.bls.gov/opub/hom/oews/data.htm "OEWS Handbook of Methods: Data Sources"
[10]: https://www.bls.gov/opub/hom/oews/history.htm "OEWS Handbook of Methods: History"
