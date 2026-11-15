# geographic-codes data manifest

Generated 2026-09-02T21:36:32+00:00 by scripts/build.py.
Interval sentinels: valid_from=1990-01-01 means "already existed at the start of the
change log", valid_to=9999-12-31 means "currently valid". Intervals are [valid_from, valid_to).
sources/ holds the exact bytes each CSV was built from — commit it alongside data/.

| output | rows | source | sha256 | retrieved |
|---|---|---|---|---|
| data/states.csv | 57 | seed: SEED_STATES in build.py |  |  |
| data/county_changes.csv | 38 | seed: seeds/county_changes.csv | 58d467bef7f5cf5d46f4462144e0a1946910e44b761c6d2085de4a43e226ece4 |  |
| data/counties.csv | 3243 | https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2025_Gazetteer/2025_Gaz_counties_national.zip | 4c90d0f805779923b5958ab13d0c1e9b99fe4932b786bfcf75dd739bb2dcb4ea | 2026-09-02T21:19:52+00:00 |
| data/cbsa_counties[2013].csv | 1882 | OMB 13-01: https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2013/delineation-files/list1.xls | 1bb1d7ce747bcd72fc212bda806c28bb4b17d4cec72d1388770f2b0a6d06f5c0 | 2026-09-02T21:19:24+00:00 |
| data/cbsa_counties[2015].csv | 1899 | OMB 15-01: https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2015/delineation-files/list1.xls | 3f04531db0b1963c8681ad905bedd2efe2aa01084b9d90cb601f68a0b6d43323 | 2026-09-02T21:19:24+00:00 |
| data/cbsa_counties[2017].csv | 1899 | OMB 17-01: https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2017/delineation-files/list1.xls | 0b71f1ca2a59eec6ad393193b16037ca3e80a03a1a5ef1ec6b25292698568eff | 2026-09-02T21:19:24+00:00 |
| data/cbsa_counties[2018-04].csv | 1900 | OMB 18-03: https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2018/delineation-files/list1.xls | 09521676a26f294274705ddde7c5732e00d4ed1a910a0ad2d4f4b7ee65d2c857 | 2026-09-02T21:23:01+00:00 |
| data/cbsa_counties[2018-09].csv | 1915 | OMB 18-04: https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2018/delineation-files/list1_Sep_2018.xls | 22ba2e944ce1aa88b0bf0d09530d08f26c17a0bba7ae823290e7c4816316418c | 2026-09-02T21:19:24+00:00 |
| data/cbsa_counties[2020].csv | 1916 | OMB 20-01: https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2020/delineation-files/list1_2020.xls | 95b389487efcd818d71ba2a992e1edd43af93228e70c2a9634fd152acb345409 | 2026-09-02T21:19:24+00:00 |
| data/cbsa_counties[2023].csv | 1915 | OMB 23-01: https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2023/delineation-files/list1_2023.xlsx | 952c4b1e78acbb54e6ec9412434b7602fedacbf021736351a63c181bdb753629 | 2026-09-02T21:19:24+00:00 |
| data/cbsa_counties.csv | 13326 | see per-delineation rows above |  |  |
| data/cbsa.csv | 6577 | derived from cbsa_counties |  |  |

No validation problems.
