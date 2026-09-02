# classification-codes data manifest

Generated 2026-09-02T21:53:01+00:00 by scripts/build.py.
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
| data/soc_2018.csv | 1447 | https://www.bls.gov/soc/2018/soc_structure_2018.xlsx | 7f85f2f857883a5d2b2e5e161c2467ecc51ce49937bee8434f06119b77a9e5c7 | 2026-09-02T21:47:03+00:00 |
| data/soc_2010.csv | 1421 | https://www.bls.gov/soc/soc_structure_2010.xls | 2dd312e9a6f057b615718fe5737e88b90370192760827a7c4e80e918a940cf02 | 2026-09-02T21:46:08+00:00 |
| data/soc_2010_to_2018.csv | 900 | https://www.bls.gov/soc/2018/soc_2010_to_2018_crosswalk.xlsx | 83db039d8aac06e8d243a6ecf3520e368943ff81b11ce43fb97e9d98979463f8 | 2026-09-02T21:46:41+00:00 |

No validation problems in the last run.
