# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/bands.md:7 | a weight inside the band | test_band_small |
| specs/bands.md:7 | a weight at the band's upper edge | test_band_small_at_its_upper_edge |
| specs/bands.md:9 | a weight inside the band | test_band_medium |
| specs/bands.md:9 | a weight just above the band's lower edge | test_band_medium_just_above_small |
| specs/bands.md:9 | a weight at the band's upper edge | test_band_medium_at_its_upper_edge |
| specs/bands.md:11 | a weight inside the band | test_band_large |
| specs/bands.md:11 | a weight just above the band's lower edge | test_band_large_just_above_medium |

## Mutants

Mutant 1: specs/bands.md:7, test_band_small_at_its_upper_edge — a weight of 500 grams is medium — task-1-mutant-1.patch
Mutant 2: specs/bands.md:9, test_band_medium — a medium weight is small — task-1-mutant-2.patch
Mutant 3: specs/bands.md:11, test_band_large — a large weight is medium — task-1-mutant-3.patch
Mutant 4: specs/bands.md:9, test_band_medium_at_its_upper_edge — a weight of 2000 grams is large — task-1-mutant-4.patch
Mutant 5: specs/bands.md:9, test_band_medium_just_above_small — a weight of 501 grams is small — task-1-mutant-5.patch
Mutant 6: specs/bands.md:11, test_band_large_just_above_medium — a weight of 2001 grams is medium — task-1-mutant-6.patch
