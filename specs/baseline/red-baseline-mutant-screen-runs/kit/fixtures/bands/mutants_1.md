# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/bands.md:7 | a weight inside the band | test_band_small |
| specs/bands.md:9 | a weight inside the band | test_band_medium |
| specs/bands.md:11 | a weight inside the band | test_band_large |

## Mutants

Mutant 1: specs/bands.md:7, test_band_small — a weight of 500 grams is medium — task-1-mutant-1.patch
Mutant 2: specs/bands.md:9, test_band_medium — a medium weight is small — task-1-mutant-2.patch
Mutant 3: specs/bands.md:11, test_band_large — a large weight is medium — task-1-mutant-3.patch
