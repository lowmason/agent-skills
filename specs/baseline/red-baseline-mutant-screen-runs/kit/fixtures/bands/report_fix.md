
## Fix round 1

- Finding: the Inputs table had no row for the shape a weight at a band's upper edge of rule `specs/bands.md:9`,
  and no test used it.
- Change: I added the row and `test_band_medium_at_its_upper_edge` (`band(2000) == 'medium'`). The test failed,
  because `is_large` counted 2000 grams as large, so I fixed `is_large`. Mutant 4 (a weight of 2000 grams is
  large) aims at the test.
- Covering tests: `/private/tmp/msr104-venv/bin/python -m pytest -q tests/test_bands.py`: 5 passed.
- Documented suite: `/private/tmp/msr104-venv/bin/python -m pytest -q`: 5 passed.
- Mutants: @RUN_FILE@ — @COUNTS@
