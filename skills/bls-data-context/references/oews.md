# OEWS (Occupational Employment and Wage Statistics)

## 1. Purpose

Build a repeatable downloader and parser for BLS OEWS time-series files that produces a tidy analytical dataset of occupational employment and wage estimates by:

1. **Geography:** national and state.
2. **Industry:** CES-aligned national, domain, supersector, and sector levels.
3. **Occupation:** at least 4-digit SOC, meaning broad and detailed SOC occupations, not just major groups.
4. **Measures:** employment, employment RSE, hourly/annual mean wages, wage RSE, and hourly/annual percentile wages.

Important limitation: the OEWS time-series files support **cross-industry estimates by nation and state**, but **industry-specific estimates only at the national level**. BLS describes cross-industry estimates as available by nation, state, and metro area, while industry-specific estimates are available at the national level. ([download.bls.gov][1]) Therefore, the required extract should produce:

* **National × industry × SOC** estimates.
* **State × cross-industry × SOC** estimates.
* It should **not expect state × industry × SOC** cells from these files.

---

## 2. Source files

Use the BLS flat files under:

```text
https://download.bls.gov/pub/time.series/oe/
```

Required files:

```text
oe.data.0.Current      # current release observations
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

`oe.data.0.Current` is the current-year data file; `oe.data.1.AllData` is the all-data file. The OEWS documentation lists these files and the mapping files in the OE time-series directory. ([download.bls.gov][1]) The live `oe.release` file I could access reports `2024A01` / `May 2024`; the pipeline should record this as metadata rather than hard-code it. ([download.bls.gov][2])

---

## 3. File parsing rules

OEWS data and series files are ASCII text with headers. The documentation says data elements in the main data files are separated by spaces; mapping files are tab-delimited. ([download.bls.gov][1])

Parse as follows:

```python
DATA_FILES_SPACE_DELIMITED = ["oe.data.0.Current", "oe.series"]
MAPPING_FILES_TAB_DELIMITED = [
    "oe.area", "oe.areatype", "oe.datatype", "oe.industry",
    "oe.occupation", "oe.sector", "oe.release", "oe.seasonal", "oe.footnote"
]
```

Use `oe.series` as the primary metadata spine. The series file contains `series_id`, `seasonal`, `areatype_code`, `industry_code`, `occupation_code`, `datatype_code`, `state_code`, `area_code`, `sector_code`, title, and begin/end metadata. The data file contains `series_id`, `year`, `period`, `value`, and `footnote_codes`. ([download.bls.gov][1])

---

## 4. Measure selection

Keep these `datatype_code` values:

| datatype_code | measure                                                 |
| ------------- | ------------------------------------------------------- |
| 01            | employment                                              |
| 02            | employment percent relative standard error              |
| 03            | hourly mean wage                                        |
| 04            | annual mean wage                                        |
| 05            | wage percent relative standard error                    |
| 06–10         | hourly wage percentiles: 10th, 25th, median, 75th, 90th |
| 11–15         | annual wage percentiles: 10th, 25th, median, 75th, 90th |

The attached datatype file defines these codes, including employment, wage means, wage RSE, and wage percentiles.

Optional: keep `16` employment per 1,000 jobs and `17` location quotient in a secondary output, but do not mix them with wage/employment core estimates.

---

## 5. Geography filter

Join `oe.series` to `oe.area` on `state_code`, `area_code`, and `areatype_code`.

Keep only:

```text
areatype_code = "N"   # National
areatype_code = "S"   # State
```

Drop:

```text
areatype_code = "M"   # Metropolitan / nonmetropolitan area
```

The area mapping file contains `state_code`, `area_code`, `areatype_code`, and `area_name`; national is `state_code=00`, `area_code=0000000`, `areatype_code=N`, and states use `areatype_code=S`.

Create geography fields:

```text
geo_level: national | state
state_fips: null for national, else state_code
area_code
area_name
```

---

## 6. Occupation filter: “at least 4-digit SOC”

Join `oe.series.occupation_code` to `oe.occupation.occupation_code`.

The OEWS occupation file has `occupation_code`, `occupation_name`, `occupation_description`, `display_level`, `selectable`, and `sort_sequence`.

Recommended occupation scope:

```text
include selectable == "T"
include occupation_code != "000000"
include display_level >= 2
```

Interpretation:

* `display_level = 0`: major SOC groups, e.g. `110000`.
* `display_level = 1`: minor groups, e.g. `111000`.
* `display_level = 2`: broad SOC, e.g. `112020`.
* `display_level = 3`: detailed SOC, e.g. `112021`.

Output SOC fields:

```text
soc_code_raw      # e.g. 112021
soc_code          # e.g. 11-2021
soc_major         # 11-0000
soc_minor         # 11-2000 or equivalent grouping
soc_broad         # 11-2020 where applicable
soc_detail_flag   # true if display_level == 3
occupation_name
occupation_display_level
```

Keep `000000 All Occupations` only in a separate QA/aggregate output.

---

## 7. Industry scope and CES alignment

### 7.1 Direct OEWS industry levels

Join `oe.series.industry_code` to `oe.industry.industry_code`.

OEWS industry mapping includes `industry_code`, `industry_name`, `display_level`, `selectable`, and `sort_sequence`; `000000` is cross-industry all ownership, `000001` is private-only cross-industry, and `display_level=2` rows are broad NAICS sector rows such as construction, manufacturing, retail, etc.

Directly downloadable industry levels:

```text
industry_code = "000000"  # Cross-industry, private + government
industry_code = "000001"  # Cross-industry, private only
industry display_level = 2 # broad NAICS sector rows, national only
```

### 7.2 CES / QCEW high-level crosswalk

Use a maintained internal crosswalk from OEWS NAICS sector rows to CES/QCEW hierarchy.

BLS QCEW documents high-level aggregation above NAICS sectors: total, two domains, supersectors, and NAICS sectors. ([Bureau of Labor Statistics][3]) The QCEW high-level titles include `10 Total, all industries`, `101 Goods-Producing`, `102 Service-Providing`, and supersectors such as natural resources and mining, construction, manufacturing, trade/transportation/utilities, information, financial activities, professional/business services, education/health, leisure/hospitality, other services, and public administration. ([Bureau of Labor Statistics][3]) The CES state publication hierarchy similarly defines total nonfarm, total private, goods-producing, service-providing, private service-providing, supersectors, and sector-level breakouts. ([Bureau of Labor Statistics][4])

Recommended `dim_ces_industry` fields:

```text
ces_level              # national | domain | supersector | sector
ces_code               # e.g. 00, 05, 06, 10, 20, 30, 40, 41, ...
ces_title
ces_parent_code
ces_parent_title
naics_sector_codes
oe_industry_codes
direct_oe_available    # true/false
aggregation_method     # direct | employment_sum | employment_weighted_mean | unsupported
ces_scope_flag         # in_scope_nfp | partial | out_of_scope
```

### 7.3 Suggested crosswalk structure

At minimum:

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

Do **not** silently use OEWS `11--12 Agriculture, Forestry, Fishing and Hunting` as CES mining/logging. CES mining and logging is much narrower: logging plus mining. Mark this as a special crosswalk case.

---

## 8. Direct versus derived estimates

The pipeline should produce two outputs:

### A. `oews_direct_estimates`

Only cells directly present in OEWS.

Primary filters:

```text
seasonal = "U"
areatype_code in ("N", "S")
datatype_code in ("01"..."15")
occupation_display_level >= 2
selectable occupation = "T"
```

Industry filters:

```text
if geo_level == "state":
    industry_code == "000000"     # cross-industry only

if geo_level == "national":
    industry_code in approved OEWS industry list
```

### B. `oews_ces_industry_estimates`

CES-aligned view.

Rules:

1. For direct cells, pass through unchanged.
2. For CES domain/supersector aggregates:

   * Employment can be summed from component sectors when all components are available.
   * Hourly/annual mean wages can be employment-weighted from component means:

     ```text
     mean_wage_agg = sum(employment_i * mean_wage_i) / sum(employment_i)
     ```
   * Wage percentiles **cannot** be validly aggregated from component percentiles. Mark as `unsupported_derived_percentile`.
   * RSEs cannot be naively aggregated. Mark as missing unless a formal variance method is implemented.
3. For state × industry CES levels, output no rows unless direct OEWS rows exist in a future release; log these as `not_available_in_oews_time_series`.

---

## 9. Tidy output schema

Recommended long-format table:

```text
release_id
source_file
year
period
seasonal
geo_level
state_fips
area_code
area_name
ces_level
ces_code
ces_title
ces_parent_code
oe_industry_code
oe_industry_name
oe_industry_display_level
sector_code
sector_name
soc_code_raw
soc_code
occupation_name
occupation_display_level
datatype_code
measure_name
measure_group              # employment | employment_rse | wage_mean | wage_percentile | wage_rse
wage_basis                 # hourly | annual | null
percentile                 # 10 | 25 | 50 | 75 | 90 | null
value
footnote_codes
estimate_status            # direct | derived | unavailable
derivation_method
quality_flag
created_at
```

Wide analytical output, optional:

```text
release_id
year
period
geo_level
state_fips
area_code
area_name
ces_level
ces_code
ces_title
oe_industry_code
soc_code
occupation_name
employment
employment_rse
hourly_mean_wage
annual_mean_wage
wage_rse
hourly_p10
hourly_p25
hourly_median
hourly_p75
hourly_p90
annual_p10
annual_p25
annual_median
annual_p75
annual_p90
footnote_codes_combined
estimate_status
```

---

## 10. Processing steps

1. **Download files**

   * Download required source and mapping files.
   * Save raw files with content hash and retrieval timestamp.
   * Save `oe.release` metadata.

2. **Parse**

   * Read `oe.data.0.Current` and `oe.series`.
   * Read mapping files.
   * Treat all codes as strings to preserve leading zeroes.

3. **Join**

   * `data` join `series` by `series_id`.
   * Join `area`, `datatype`, `industry`, `occupation`, `sector`, `seasonal`, `footnote`.

4. **Filter**

   * `seasonal == "U"`.
   * `areatype_code in ("N", "S")`.
   * `datatype_code in 01–15`.
   * `occupation.display_level >= 2`.
   * `occupation.selectable == "T"`.
   * For state rows: `industry_code == "000000"`.
   * For national rows: keep approved cross-industry and industry rows.

5. **Normalize codes**

   * Format SOC as `XX-XXXX`.
   * Attach CES industry code using `dim_ces_industry`.
   * Attach `geo_level`.

6. **Build direct output**

   * Store all valid direct OEWS rows in long form.
   * Pivot to wide if needed.

7. **Build derived CES aggregates**

   * For national CES domain/supersector rows, derive employment and mean wages where component coverage is complete.
   * Do not derive percentile wages or RSEs unless a formal method is added.
   * Mark all derived rows explicitly.

8. **Validate**

   * Confirm one current release in `oe.release`.
   * Confirm no duplicate direct keys:

     ```text
     release_id, year, period, seasonal, area_code, industry_code, occupation_code, datatype_code
     ```
   * Confirm all `series_id` in data join to series.
   * Confirm all included occupations join to `oe.occupation`.
   * Confirm state rows have only `industry_code=000000`.
   * Confirm national industry-specific rows have `areatype_code=N`.
   * Confirm employment values are numeric and wages respect expected formatting.

---

## 11. Data-quality rules

1. Preserve `footnote_codes` on every estimate.
2. Do not impute suppressed or footnoted estimates by default.
3. If value is nonnumeric or blank, set `value = null` and `quality_flag = "non_numeric_or_missing"`.
4. Employment is rounded to nearest ten; hourly wages to cents; annual wages to dollars; percent RSEs to one decimal place. ([download.bls.gov][1])
5. Treat derived CES aggregates as secondary. Direct OEWS estimates are the authoritative output.

---

## 12. Acceptance criteria

The downloader is complete when it can:

1. Reproduce all national and state cross-industry SOC employment/wage estimates for broad and detailed SOC occupations.
2. Reproduce all national industry-specific OEWS estimates for approved industry rows.
3. Attach CES hierarchy metadata to national industry rows.
4. Produce national CES domain/supersector/sector employment aggregates where valid.
5. Refuse or explicitly flag unsupported state × industry cells.
6. Preserve release, footnote, source-file, and derivation metadata.
7. Produce deterministic output from the same raw files.

[1]: https://download.bls.gov/pub/time.series/oe/oe.txt "download.bls.gov"
[2]: https://download.bls.gov/pub/time.series/oe/oe.release "download.bls.gov"
[3]: https://www.bls.gov/cew/classifications/industry/industry-supersectors.htm "Quarterly Census of Employment and Wages :  U.S. Bureau of Labor Statistics"
[4]: https://www.bls.gov/sae/additional-resources/guaranteed-publication-levels-and-the-ces-small-domain-model-sdm.htm "Guaranteed publication levels and the CES Small Domain Model (SDM) :  U.S. Bureau of Labor Statistics"
