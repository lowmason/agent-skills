# How U.S. statistical geographies are defined and when they change

Two systems, two clocks. **County-equivalents** are legal or administrative units that states
create and the Census Bureau recognizes; they change whenever a state acts and Census records
it. **Core based statistical areas (CBSAs)** are statistical constructs that the Office of
Management and Budget (OMB) defines by published standards and revises on a decennial cycle
with intercensal updates. Everything below is summarized in original wording from the primary
sources listed at the end; section numbers refer to the 2020 standards (86 FR 37770).

## County-equivalents

### What counts as one

| entity | where | nature |
|---|---|---|
| county | 48 states | general-purpose local government (or, in CT before 2022, a historical unit with no government since 1960) |
| parish | Louisiana | county by another name |
| borough, city and borough, municipality | Alaska | organized local governments |
| census area | Alaska | Census-delineated statistical subdivision of the Unorganized Borough; no government |
| independent city | Virginia (38), plus Baltimore MD, St. Louis MO, Carson City NV | a city outside any county, counted as a county-equivalent |
| District of Columbia | — | one county-equivalent |
| municipio | Puerto Rico | county-equivalent |
| planning region | Connecticut, from 2022 | the nine councils of governments adopted as county-equivalents (87 FR 34235) |

The Alaska rows explain why Alaska dominates the change log: when part of the Unorganized
Borough incorporates as a borough (Skagway 2007, Wrangell 2008, Petersburg 2013), the new
borough takes a code and Census redraws and recodes the census area left behind.

### How a change becomes a code event

1. **A state acts** — a city reverts to town status (South Boston 1995, Clifton Forge 2001,
   Bedford 2013), a county is created (Broomfield 2001), a borough incorporates, or a name is
   changed by statute (Shannon → Oglala Lakota 2015, Wade Hampton → Kusilvak 2015).
2. **Census records it.** The Census Bureau maintains legal boundaries under OMB Circular A-16
   and collects boundary changes through its Boundary and Annexation Survey. Its published
   change log, *Substantial Changes to Counties and County Equivalent Entities*, is organized
   one page per decade and lists new, deleted, renamed, and recoded entities plus boundary
   changes affecting an estimated 200 or more people.
3. **The reference date is January 1.** Census products reference boundaries as of January 1 of
   the vintage year; a change effective after January 1 appears in products referenced to the
   following year. This is why `valid_from` (the legal effective date) and the first data
   vintage that shows the change differ by up to a year.
4. **Codes follow alphabetical order.** County FIPS codes were assigned alphabetically within a
   state using odd numbers, leaving even numbers free for insertions. Every recode in the
   change log restores that order: Dade `025` became Miami-Dade `086` (between Marion `083`
   and Monroe `087`), Shannon `113` became Oglala Lakota `102` (between Minnehaha `099` and
   Pennington `103`), Wade Hampton `270` became Kusilvak `158`, Broomfield took `014` between
   Boulder `013` and Chaffee `015`. A rename that keeps its alphabetical position keeps its
   code (Petersburg Census Area → Petersburg Borough, `195`). Predict a recode from the name,
   never assume a rename is code-preserving.
5. **Spelling corrections are not events.** Census fixed `De Kalb`, `La Porte`, `Mc Kean`,
   `Dona Ana`, `La Salle` (IL and LA) and similar without effective dates; the code never
   changed and the old spelling is treated as an error, not a prior name.

### The Connecticut case

Connecticut asked Census to adopt its nine planning regions (councils of governments) as
county-equivalents in place of eight counties that had had no government since 1960. The final
Federal Register notice is 87 FR 34235, published 2022-06-06; Census implemented the change
internally in 2022, in public data and geospatial products from late 2022, and across all
operations and products by 2024. Planning regions are built from towns, and towns do not nest
in the old counties, so the county↔planning-region relation is many-to-many. Census publishes a
town-level crosswalk for it; nothing in `data/` bridges the two.

## Core based statistical areas

### Legal basis and building blocks

OMB delineates CBSAs for federal statistical use under 44 U.S.C. § 3504(e), 31 U.S.C. § 1104(d),
and Executive Order 10253 (1951). The program has existed under various names since the 1950
census. The building block is the whole county-equivalent (including Puerto Rico's municipios);
a CBSA never splits a county. The delineations are statistical; OMB states they are not an
urban–rural classification and are not designed for program administration or funding formulas
(the MAPS Act of 2021 makes the same point), though many programs use them anyway.

### The qualification rules (2020 standards)

| rule | criterion | section |
|---|---|---|
| a CBSA exists | contains a Census Urban Area of ≥ 10,000 population | §1 |
| **central county** | ≥ 50 % of its population lives in Urban Areas of ≥ 10,000, **or** ≥ 5,000 of its residents live in a single Urban Area of ≥ 10,000 | §2 |
| **outlying county** | ≥ 25 % of its resident workers work in the central counties, **or** ≥ 25 % of its jobs are held by central-county residents | §3 |
| one CBSA per county | central beats outlying; among outlying claims the strongest commuting tie wins; counties must be contiguous | §3 |
| merge | two adjacent CBSAs merge when one's central counties qualify as outlying to the other's | §4 |
| **metropolitan** vs **micropolitan** | largest Urban Area ≥ 50,000 → metropolitan; 10,000–49,999 → micropolitan; everything else is "outside CBSAs" | §6 |
| **metropolitan division** | only inside an MSA whose single Urban Area is ≥ 2.5 million; a *main county* has ≥ 65 % of resident workers working in-county and a jobs-to-resident-workers ratio ≥ 0.75; a *secondary county* has 50–65 % and the same ratio; remaining counties attach by highest employment interchange | §7 |
| **combined statistical area** | two adjacent CBSAs with an employment interchange measure ≥ 15; both remain CBSAs | §8 |
| titles | the largest principal city first, up to three cities, plus every state the area touches; titles change without codes changing | §5, §9 |

The **employment interchange measure** is the sum of two percentages: the share of the smaller
entity's resident workers who work in the larger entity, plus the share of the smaller entity's
jobs held by residents of the larger entity (§11).

Inputs are decennial census population, Census Urban Areas, American Community Survey five-year
commuting estimates used as point estimates with no allowance for sampling error, and, between
censuses, Population Estimates Program figures and special censuses.

### What the 2020 standards changed

The 2020 standards (86 FR 37770, 2021-07-16) replaced the 2010 standards (75 FR 37246,
2010-06-28) and made only three substantive decisions:

- **Kept the 50,000 metropolitan threshold.** The review committee had recommended 100,000;
  OMB declined, citing disruption to statistical programs and insufficient justification.
- **Discontinued NECTAs** — the town-based New England City and Town Areas, their divisions,
  and combined NECTAs that the 2010 standards had delineated alongside county-based CBSAs.
  Programs had been releasing NECTA data for New England and CBSA data elsewhere; OMB judged
  that contrary to a nationally consistent framework, after consulting BLS as the primary user.
- **Committed to research** on a territorially exhaustive classification covering all counties.

Everything else — the thresholds, the commuting test, divisions, CSAs — carried over unchanged,
so 2013–2020 and 2023 delineations are comparable in concept even though membership moved.

### The revision schedule

- **Decennial re-delineation.** Each decade's standards are applied to the new census: 2013
  (bulletin 13-01, on the 2010 Census) and 2023 (bulletin 23-01, on the 2020 Census and
  2016–2020 ACS). §10(e) schedules a full review of every CBSA in **2028** using 2021–2025 ACS
  commuting and employment estimates, with new areas added on the same rules.
- **Intercensal updates.** Between censuses OMB adds a new micropolitan or metropolitan area
  when a city outside any CBSA reaches 10,000 or 50,000 in a special census or in two
  consecutive years of Population Estimates Program figures, and qualifies its outlying counties
  from ACS commuting (§10(b)–(d)). Other aspects of existing delineations are frozen between
  censuses (§10(f)). Updates are issued at most once a year, in **December** of update years
  (§10(g)), and OMB maintains a public release schedule (§10(h)). Under the 2010 standards the
  same mechanism produced the 2015, 2017, and two 2018 bulletins and the 2020 bulletin.
- **Schedules slip.** §10(a) promised the 2023 delineations "during June 2023"; the bulletin
  issued 2023-07-21. Treat announced dates as intentions until the bulletin exists.
- **Bulletins take effect immediately** on their issue date. That date is `valid_from` in
  `data/cbsa_counties.csv`. Statistical programs adopt a bulletin later, each on its own
  timetable, usually at an annual benchmark or reference-year rollover, so a metro series
  breaks at the program's adoption date — `bls-data-context` — not at `valid_from`.

### The bulletins bundled here

| block | bulletin | issued | supersedes | basis |
|---|---|---|---|---|
| `2013` | 13-01 | 2013-02-28 | 09-01 (Dec 2009) | 2010 Census; 2010 standards |
| `2015` | 15-01 | 2015-07-15 | 13-01 | intercensal update |
| `2017` | 17-01 | 2017-08-15 | 15-01 | intercensal update |
| `2018-04` | 18-03 | 2018-04-10 | 17-01 | intercensal update |
| `2018-09` | 18-04 | 2018-09-14 | 18-03 | correction and update, five months on |
| `2020` | 20-01 | 2020-03-06 | 18-04 | intercensal update |
| `2023` | 23-01 | 2023-07-21 | 20-01 | 2020 Census; 2020 standards; first block coded with Connecticut planning regions |

What a new bulletin typically changes: outlying counties join or leave (commuting shares crossed
25 percent), micropolitan areas appear or graduate to metropolitan, adjacent areas merge, CSAs
gain or lose members, and titles change as principal cities are re-ranked. CBSA codes are
stable for a continuing area; a merged area keeps one code and retires the other, so a code that
vanishes between blocks was absorbed, not deleted.

## Regions and divisions

The four Census regions and nine divisions are fixed groupings of whole states and have not
changed over the period covered here; `data/states.csv` is a static seed. Territories carry no
region or division.

## Primary sources

- Census, *Substantial Changes to Counties and County Equivalent Entities: 1970-Present* —
  `census.gov/programs-surveys/geography/technical-documentation/county-changes.html`, with one
  page per decade at `county-changes.1990.html`, `.2000.html`, `.2010.html`,
  `.January_2020.html`.
- Census, *Change to County-Equivalents in the State of Connecticut*, 87 FR 34235 (2022-06-06),
  `federalregister.gov/d/2022-12063`.
- OMB, *2020 Standards for Delineating Core Based Statistical Areas*, 86 FR 37770 (2021-07-16),
  `federalregister.gov/d/2021-15159`; *2010 Standards for Delineating Metropolitan and
  Micropolitan Statistical Areas*, 75 FR 37246 (2010-06-28), `federalregister.gov/d/2010-15605`.
- OMB bulletins, archived by administration: 13-01 and 15-01 under
  `obamawhitehouse.archives.gov/sites/default/files/omb/bulletins/`; 17-01, 18-03, 18-04, and
  20-01 under `trumpwhitehouse.archives.gov/` (`sites/whitehouse.gov/files/omb/bulletins/2017/`
  and `wp-content/uploads/`); 23-01 at `bidenwhitehouse.archives.gov/wp-content/uploads/2023/07/`
  and, at the time of writing, still at `whitehouse.gov/wp-content/uploads/2023/07/`.
- Census delineation files (the "List 1" workbooks `data/` is built from):
  `www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/<year>/delineation-files/`.
- Census Gazetteer Files (the current county-equivalent set):
  `www2.census.gov/geo/docs/maps-data/data/gazetteer/<year>_Gazetteer/`.
