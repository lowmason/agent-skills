# classification-codes data manifest

Generated 2026-09-02T22:12:27+00:00 by scripts/build.py.
sources/ holds the exact bytes each CSV was built from — commit it; Census and BLS overwrite
files in place, so an unarchived source vintage is unrecoverable. `retrieved` is the time the
cached source file was written.

| output | rows | source url | sha256 | retrieved |
|---|---|---|---|---|
| data/naics_2022.csv | 2125 | https://www.census.gov/naics/2022NAICS/2022_NAICS_Structure.xlsx | 217c9e0d4d74e7517bc288f5f308b73aa0de5ee787976a6dd222412be28ada22 | 2026-09-02T21:33:48+00:00 |
| data/naics_2017.csv | 2196 | https://www.census.gov/naics/2017NAICS/2017_NAICS_Structure.xlsx | 662b5a2bdff10938997acd7f59f84331527d6f06ff24d5533331581a00a94aad | 2026-09-02T21:33:51+00:00 |
| data/naics_2012.csv | 2209 | https://www.census.gov/naics/2012NAICS/2012_NAICS_Structure.xls | 50eba48db4e11f863e015d4d2bbaaf618565bd94ef9b019fe62b9bbaddbaaafb | 2026-09-02T21:33:51+00:00 |
| data/naics_2017_to_2022.csv | 1150 | https://www.census.gov/naics/concordances/2017_to_2022_NAICS.xlsx | 4662cc7ed9e7f3fb8a968e9504a7d06e448f5b65a349996a5627439df193eb30 | 2026-09-02T21:23:23+00:00 |
| data/naics_2012_to_2017.csv | 1069 | https://www.census.gov/naics/concordances/2012_to_2017_NAICS.xlsx | 17f463f7e8385df1cc762fadf0dd5c25910aa27034ca96275a906608399188f5 | 2026-09-02T21:33:51+00:00 |
| data/soc_2018.csv | 1447 | https://www.bls.gov/soc/2018/soc_structure_2018.xlsx | ade08af40923266f3a854842e888ca3e93c15b26a147c20a2b12a61f4c4f4077 | 2026-09-02T22:02:03+00:00 |
| data/soc_2010.csv | 1421 | https://www.bls.gov/soc/soc_structure_2010.xls | 4f39cd2e378e8bac5f73d8f9f90eb12010292d9c397529122b5790fd58183afd | 2026-09-02T22:02:04+00:00 |
| data/soc_2010_to_2018.csv | 900 | https://www.bls.gov/soc/2018/soc_2010_to_2018_crosswalk.xlsx | f3a847561562d3e5a30eb848f2902a5f7b02e9c48b3d7f2cc8879899fbc242a7 | 2026-09-02T22:02:04+00:00 |
| data/census_occ_2018.csv | 570 | https://www2.census.gov/programs-surveys/demo/guidance/industry-occupation/2018-occupation-code-list-and-crosswalk.xlsx | fca2818d691c32777a4cd733a9ab77c8c5bd47adcacd7ac3aa149bebd45b5f7f | 2026-09-02T22:10:28+00:00 |
| data/census_occ_2018_to_soc_2018.csv | 867 | derived from census_occ_2018, soc_2018 |  |  |
| data/census_occ_2010.csv | 540 | https://www2.census.gov/programs-surveys/demo/guidance/industry-occupation/2010-occ-codes-with-crosswalk-from-2002-2011.xls | ebf7e6f31c0cda16c7c8518a23bfa13ca537105ba41c427f99dff155a68c2cc6 | 2026-09-02T22:10:28+00:00 |
| data/census_occ_2010_to_soc_2010.csv | 840 | derived from census_occ_2010, soc_2010 |  |  |

No validation problems in the last run.
