# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/picker.md:7 | latest is the later-named file | test_latest_report_returns_the_latest_dated_report |
| specs/picker.md:7 | dates across years | test_date_is_compared_as_a_date_across_years |
| specs/picker.md:7 | date line first / not first | test_date_line_may_come_before_other_lines |
| specs/picker.md:8 | latest is the earlier-named file | test_file_names_carry_no_order |
| brief: .txt file directly in folder | other extension, subdirectory | test_only_txt_files_directly_in_the_folder_count |

## Mutants

Mutant 1: specs/picker.md:7, test_latest_report_returns_the_latest_dated_report — returns earliest instead of latest — task-1-mutant-1.patch
Mutant 2: specs/picker.md:8, test_file_names_carry_no_order — orders by file name — task-1-mutant-2.patch
Mutant 3: brief: directly in folder, test_only_txt_files_directly_in_the_folder_count — recursive glob — task-1-mutant-3.patch
Mutant 4: brief: .txt file, test_only_txt_files_directly_in_the_folder_count — any extension counts — task-1-mutant-4.patch
Mutant 5: specs/picker.md:7, test_date_is_compared_as_a_date_across_years — date key is reversed digits — task-1-mutant-5.patch
