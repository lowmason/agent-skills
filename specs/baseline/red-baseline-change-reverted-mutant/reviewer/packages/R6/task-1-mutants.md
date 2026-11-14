# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/sizes.md:7 | each unit: `B`, `KB` and `MB` | test_to_bytes_reads_each_unit |
| specs/sizes.md:7 | a number of several digits | test_to_bytes_reads_a_number_of_several_digits |
| specs/sizes.md:7 | zero (`0B`), and a number with leading zeros (`007KB`) | test_to_bytes_reads_zero_and_leading_zeros |
| specs/sizes.md:8 | 1 KB = 1024 B and 1 MB = 1024 KB | test_to_bytes_reads_each_unit |
| specs/sizes.md:9 | empty text | test_to_bytes_rejects_any_other_text |
| specs/sizes.md:9 | a number with no unit (`12`), and a unit with no number (`KB`) | test_to_bytes_rejects_any_other_text |
| specs/sizes.md:9 | a unit that is not `B`, `KB` or `MB` (`3GB`) | test_to_bytes_rejects_any_other_text |
| specs/sizes.md:9 | a unit not in capitals (`3kb`, `3Kb`) | test_to_bytes_rejects_any_other_text |
| specs/sizes.md:9 | a blank between, before or after (`3 KB`, ` 3KB`, `3KB `, `3KB\n`) | test_to_bytes_rejects_any_other_text |
| specs/sizes.md:9 | other text after the unit (`3KBs`) | test_to_bytes_rejects_any_other_text |
| specs/sizes.md:9 | a sign, a decimal point or an underscore (`-3KB`, `+3KB`, `1.5KB`, `1_0KB`) | test_to_bytes_rejects_any_other_text |
| specs/sizes.md:9 | a digit outside `0` to `9` (`\u0663KB`, the Arabic-Indic three) | test_to_bytes_rejects_any_other_text |

## Mutants

Mutant 1: specs/sizes.md:8, test_to_bytes_reads_each_unit, test_to_bytes_reads_a_number_of_several_digits, test_to_bytes_reads_zero_and_leading_zeros — 1 KB is 1000 B (`'KB': 1000`) — task-1-mutant-1.patch
Mutant 2: specs/sizes.md:8, test_to_bytes_reads_each_unit — 1 MB is 1000 KB (`'MB': 1000 * 1024`) — task-1-mutant-2.patch
Mutant 3: specs/sizes.md:7, test_to_bytes_reads_a_number_of_several_digits, test_to_bytes_reads_zero_and_leading_zeros — reads a number of one digit only (`[0-9]` for `[0-9]+`) — task-1-mutant-3.patch
Mutant 4: specs/sizes.md:9, test_to_bytes_rejects_any_other_text — matches a size at the start of the text only, so text after it gets through (`match` for `fullmatch`) — task-1-mutant-4.patch
Mutant 5: specs/sizes.md:9, test_to_bytes_rejects_any_other_text — takes any Unicode digit (`\d` for `[0-9]`) — task-1-mutant-5.patch
