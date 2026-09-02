# How NAICS and SOC are made and revised

Who decides what an industry or an occupation is, by what criteria a new one gets created, on
what schedule the systems change, and what a revision looks like once it lands in `data/`.
Facts below come from the Office of Management and Budget's Federal Register notices and the
BLS SOC pages cited in the last section; where a number is computed from the bundled files it
says so.

## Governance

| | NAICS | SOC |
|---|---|---|
| Legal instrument | OMB Statistical Policy Directive No. 8 | OMB Statistical Policy Directive No. 10 |
| Working committee | Economic Classification Policy Committee (ECPC): representatives of the Bureau of Economic Analysis, BLS, the Census Bureau, and other agencies, recommending to OMB | SOC Policy Committee (SOCPC), a standing committee OMB established in 2005, chaired by BLS; 18 federal agencies and components as of 2024 |
| Partners | Statistics Canada and Mexico's INEGI — NAICS is a trilateral system | none; US-only |
| Unit classified | the establishment, by its production process | the job / worker, by work performed |
| Who must use it | OMB-recognized statistical agencies, in every relevant collection | every federal agency publishing occupational statistics; state/local use encouraged |
| Purpose clause | statistical only — administrative, regulatory, tax, or procurement users have no role in development or revision | same wording; non-statistical fitness is judged case by case |

Both systems are explicit that they are built for statistics. A code that looks wrong for a
contracting or regulatory purpose is not a defect the committees will fix.

## What counts as an industry — the NAICS rules

Four principles guide NAICS development (paraphrased from 89 FR 104229 and 91 FR 42976):

1. **Production-oriented framework.** Producing units that use the same or similar production
   processes are grouped together. This is the single aggregation principle; NAICS is not
   demand- or product-based.
2. **Priority areas.** New and emerging industries, service industries generally, and
   advanced-technology production get special attention.
3. **Time-series continuity** is maintained to the extent possible.
4. **International compatibility** with the two-digit level of the UN's ISIC.

Hierarchy (counts are NAICS 2022, from the notice and confirmed against `data/naics_2022.csv`):

| level | digits | count | note |
|---|---|---|---|
| sector | 2 | 20 | three are ranges: `31-33`, `44-45`, `48-49` |
| subsector | 3 | 96 | |
| industry group | 4 | 308 | |
| NAICS industry | 5 | 689 | "in most cases" the lowest level of three-country comparability |
| national industry | 6 | 1,012 | U.S. detail; never flagged trilateral |

**How a new industry gets created.** Anyone may propose one in response to the solicitation
notice. The ECPC evaluates each proposal on (89 FR 104229):

- fit with the production-function concept — a proposal that separates activities of *similar*
  producing units cannot be an industry; if the concern is really about what is produced, it
  belongs to the product classification (NAPCS), not NAICS;
- impact on North American comparability (and comparability with other regions), with Canada and
  Mexico negotiating any change that crosses the three-country level of agreement;
- impact on time series;
- **size** — enough establishments that agencies can publish the industry without disclosing
  individual firms, a binding constraint at state, metro, and county level even when the national
  count is fine;
- whether agencies can classify, collect, and publish on the proposed basis inside normal
  processing operations, and at what cost, given the budget environment.

Proposals must describe the specific economic activities, the production process, and how the
activity is currently classified. For 2027 the ECPC stated it would limit changes to those that
significantly improve relevance and efficiency, recommend new industries surfaced by the comment
process that fit the principles, and otherwise fix errors, omissions, and unclear narrative
(91 FR 42976).

## What counts as an occupation — the SOC rules

The 2018 SOC carries ten classification principles and six coding guidelines. OMB proposed the
principle set in 79 FR 29620 (2014), the SOCPC recommended it in 81 FR 48306 (2016), OMB adopted
it in 82 FR 56271 (2017), and the 2028 solicitation (89 FR 49911) states the intention to retain
both lists. Paraphrased:

**Classification principles**

1. Scope is every occupation in which work is done for pay or profit, including uncompensated
   family members in family businesses; occupations unique to volunteers are excluded. Each
   occupation sits in exactly one category at the most detailed level.
2. Classification is by **work performed**, and only secondarily by the skills, education, or
   training the work needs.
3. Workers whose primary role is planning and directing resources are managers, major group
   `11-0000`, even if they also supervise.
4. Supervisors in major groups `13` through `29` are classified **with the workers they
   supervise**, because they usually share the work and the experience.
5. Major group `31-0000` (healthcare support) has **no first-line supervisor occupations**;
   its workers are supervised by `29-0000` practitioners.
6. In major groups `33` through `53`, workers whose primary duty is supervising go in the
   **first-line supervisor** occupation, because that work is distinct from the work supervised.
7. Apprentices and trainees are classified with the occupation they are training for; helpers
   and aides are classified separately because they are not in training for it.
8. Work that matches no distinct detailed occupation goes in the group's residual **"All
   Other"** occupation. Residuals exist only where the detailed occupations of a broad group do
   not account for all its workers; they are the last code in the group, end in `9`, and carry
   "All Other" at the end of the title.
9. **A detailed occupation exists only if BLS or the Census Bureau can collect and report data
   on it.** This is the creation gate: the two agencies are charged with covering total U.S.
   employment across every major group, so an occupation neither can measure is not added.
10. Time-series continuity is maintained to the extent possible.

**Coding guidelines** (how a survey response becomes a code)

1. Code by work performed.
2. A job that spans occupations is coded to the one requiring the **highest skill**; if skill
   does not differ, to where the most time is spent. Teachers spanning levels code to the
   highest level taught.
3. Code to the **most detailed** occupation possible; agencies may aggregate differently
   depending on what they can collect.
4. Activities described by no detailed occupation code to the residual "All Other".
5. In major groups `33` through `53`, **80 percent or more** of time on supervision codes to the
   first-line supervisor occupation; less than 80 percent codes with the supervised workers.
6. Licensed and unlicensed workers doing the same work code together unless a definition says
   otherwise.

Two practical consequences for data work: the SOC is task-based, so a job title alone does not
determine a code (a "painter" can be `27-1013`, `47-2141`, or `51-9124`), which is why BLS
maintains a **Direct Match Title File** of titles that map to exactly one detailed occupation and
accepts additions to it quarterly through the SOCPC; and because residual "All Other" codes
absorb whatever the structure does not name, the absence of a specific title never implies the
absence of the workers.

## Revision cadence and the three-notice cycle

Both systems revise through the same shape: a Federal Register notice **soliciting proposals**,
a notice publishing the committee's **recommendations** for comment, and OMB's **final
decisions**. Statistical programs then implement the new vintage on their own schedules — the
adoption date per program is a program fact and lives in `bls-data-context`.

**NAICS** is reviewed every five years; 2027 is the sixth revision since OMB adopted NAICS in
1997 to replace the SIC.

| vintage | solicitation | ECPC recommendations | OMB final decisions |
|---|---|---|---|
| 1997 | ECPC notices 1996 | | 1997-04-09, 62 FR 17288 |
| 2002 | 2000-04-20, 65 FR 21242 | | 2001-01-16, 66 FR 3826 |
| 2007 | 2002-12-27, 67 FR 79500 | 2005-03-11, 70 FR 12390 | 2006-05-16, 71 FR 28532 |
| 2012 | 2009-01-07, 74 FR 764 | 2010-05-12, 75 FR 26856 | 2011-08-17, 76 FR 51240 |
| 2017 | 2014-05-22, 79 FR 29626 | 2015-08-04, 80 FR 46480 | 2016-08-08, 81 FR 52584 |
| 2022 | 2020-02-26, 85 FR 11120 | 2021-07-02, 86 FR 35350 | 2021-12-21, 86 FR 72277 |
| 2027 | 2024-12-20, 89 FR 104229 (comments to 2025-02-18) | 2026-07-13, 91 FR 42976 | **pending** as of 2026-09 |

Rule of thumb from the table: solicitation about three years before the vintage year,
recommendations one to two years before, final decisions roughly a year before. The final notice
is where the code list becomes authoritative; the Census structure and concordance workbooks
follow it.

**SOC** was first issued in 1977 and revised in 1980, 2000, 2010, and 2018 (the 2000 SOC's
final-decision notice, 64 FR 53136 of 1999-09-30, calls it the "1998 SOC"). From 2028 on OMB has
tied the SOC to NAICS: revisions are timed for **the year after a NAICS revision**, with a review
for possible revision **every ten years** thereafter (89 FR 49911).

| vintage | solicitation | SOCPC recommendations | OMB final decisions | in use from |
|---|---|---|---|---|
| 2010 | 2006-05-16, 71 FR 28536 | 2008-05-22, 73 FR 29930 | 2009-01-21, 74 FR 3920 | reference year 2010 |
| 2018 | 2014-05-22, 79 FR 29620 (to 2014-07-21) | 2016-07-22, 81 FR 48306 (to 2016-09-20) | 2017-11-28, 82 FR 56271 | reference year 2018 |
| 2028 | 2024-06-12, 89 FR 49911 | expected; a second comment round is planned | intended by early 2027 | reference year 2028 |

For 2018 the SOCPC began planning in early 2012 — six years before use. The 2028 review began in
December 2023 and put these topics up for comment: retaining the principles, guidelines, and 23
major groups; whether to define major groups; consolidating public-safety telecommunicators and
some production occupations; adding care workers; and changes to the STEM occupation framework.

## What a revision looks like in the bundled files

**NAICS structure files carry Census's change indicator per code**, verbatim in
`change_indicator`. The legend is vintage-specific:

| marker | 2012 | 2017 | 2022 |
|---|---|---|---|
| `*` | title change, no content change | same | same |
| `**` | new code for this vintage | same | same |
| `***` | re-used code, content change | (not used) | same |
| `****` | (not used) | (not used) | re-used code, content changed at a lower level with insignificant impact at this level |

Counts from `data/` (all levels): 2012 has 84 `**`, 18 `*`, 17 `***`; 2017 has 30 `**`, 4 `*`;
2022 has 186 `**`, 31 `*`, 7 `***`, 5 `****`. The dangerous markers are `***` and `****`: the
code survived, its boundary did not, and code equality across vintages will silently splice two
different populations.

**Concordances record links, not weights.** Computed from `data/`:

| concordance | rows | `1:1` | `1:m` | `m:1` | `m:m` |
|---|---|---|---|---|---|
| 2012 → 2017 | 1,069 | 1,045 | 3 | 16 | 5 |
| 2017 → 2022 | 1,150 | 928 (916 same code, 12 clean recodes) | 5 | 120 | 97 |

Every six-digit code on both sides of each concordance appears in at least one row, so an
unmatched code after a join means a bad key, not a gap in the file. Where Census names the piece
of a source industry that flows to a target, the source title carries it as a suffix
(`Crude Petroleum and Natural Gas Extraction - natural gas extraction`).

**The 2022 revision's theme** was to stop using mode of delivery (online versus in-store or
print) as an industry boundary in Wholesale Trade, Retail Trade, and Information, because the
internet had become a generic delivery channel rather than a distinct activity (86 FR 72277).
That is why 2017 `454110` Electronic Shopping and Mail-Order Houses fans out to 42 product-line
retailers, every row `m:m`, and why subsector `454` has no 2022 successor.

**SOC crosswalks carry BLS's own split and merge markers.** In the 2010→2018 workbook a source
title ending `(#)` is a 2010 code that splits and a target title ending `(##)` is a 2018 code
that merges. The build checked those markers against the multiplicity-derived `link_type` on all
900 rows and found no disagreement, then stripped them:

| crosswalk | rows | `1:1` | `1:m` | `m:1` | `m:m` |
|---|---|---|---|---|---|
| SOC 2010 → 2018 | 900 | 766 | 70 | 32 | 32 |

All 840 detailed 2010 codes and all 867 detailed 2018 codes appear. BLS also publishes a
type-of-change list by detailed occupation and a list of 2010 codes deleted in 2018 on the SOC
page; those are not bundled.

**A revision can outgrow the code pattern.** The 2018 SOC added enough physician specialties
that broad group `29-1210` Physicians ran past `29-1219`: `29-1221` through `29-1229` are its
members too, and no `29-1220` exists. The bundled `parent_code` follows the sheet's nesting, so
the hierarchy is right; anything that re-derives parents from digits will orphan those five.

## Sources

- NAICS 2027 solicitation, 89 FR 104229 (2024-12-20):
  https://www.federalregister.gov/documents/2024/12/20/2024-30060/statistical-policy-directive-no-8-north-american-industry-classification-system-naics-request-for
- NAICS 2027 ECPC recommendations, 91 FR 42976 (2026-07-13):
  https://www.federalregister.gov/documents/2026/07/13/2026-14086/statistical-policy-directive-no-8-north-american-industry-classification-system-naics-request-for
- NAICS 2022 final decisions, 86 FR 72277 (2021-12-21):
  https://www.federalregister.gov/documents/2021/12/21/2021-27536/north-american-industry-classification-system-revision-for-2022-update-of-statistical-policy
- SOC 2018 solicitation with the proposed principles, 79 FR 29620 (2014-05-22):
  https://www.federalregister.gov/documents/2014/05/22/2014-11913/standard-occupational-classification-soc-revision-for-2018-notice
- SOC 2018 recommendations, 81 FR 48306 (2016-07-22), and final decisions, 82 FR 56271 (2017-11-28):
  https://www.federalregister.gov/documents/2017/11/28/2017-25622/standard-occupational-classification-soc-system-revision-for-2018
- SOC 2028 solicitation, 89 FR 49911 (2024-06-12):
  https://www.federalregister.gov/documents/2024/06/12/2024-12825/statistical-policy-directive-no-10-standard-occupational-classification-soc-request-for-comments-on
- BLS 2018 SOC page (revision timeline, Direct Match Title File, downloadables):
  https://www.bls.gov/soc/2018/home.htm
- Earlier cycles: the Federal Register documents API, agency `management-and-budget-office`,
  terms "North American Industry Classification System" and "Standard Occupational
  Classification", ordered newest first — the tables above were built from that listing.
