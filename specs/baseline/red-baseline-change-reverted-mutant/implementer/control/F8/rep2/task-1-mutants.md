# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/sizes.md:7 | unit B | test_to_bytes_reads_each_unit |
| specs/sizes.md:7 | unit KB (1024) | test_to_bytes_reads_each_unit |
| specs/sizes.md:7 | unit MB | test_to_bytes_reads_each_unit |
| specs/sizes.md:7 | multi-digit number | test_to_bytes_reads_a_number_of_several_digits |

## Mutants

Mutant 1: specs/sizes.md:7, test_to_bytes_reads_each_unit — KB is 1000 — task-1-mutant-1.patch
Mutant 2: specs/sizes.md:7, test_to_bytes_reads_each_unit — MB is 1024*1000 — task-1-mutant-2.patch
Mutant 3: specs/sizes.md:7, test_to_bytes_reads_a_number_of_several_digits — only one digit read — task-1-mutant-3.patch
Mutant 4: specs/sizes.md:7, test_to_bytes_reads_each_unit — B factor is 2 — task-1-mutant-4.patch
