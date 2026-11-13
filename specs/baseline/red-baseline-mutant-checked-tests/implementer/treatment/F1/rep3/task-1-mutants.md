# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/picker.md:7 | two reports, latest second | test_latest_report_returns_the_latest_dated_report |
| specs/picker.md:7 | date line after other lines; year boundary | test_date_line_may_follow_other_lines_and_year_decides |
| specs/picker.md:8 | latest report has the earlier name | test_file_names_carry_no_order |
| brief: .txt directly in folder | non-.txt file, nested .txt | test_only_txt_files_directly_in_folder_count |

## Mutants

Mutant 1: specs/picker.md:8, test_file_names_carry_no_order — orders by file name — task-1-mutant-1.patch
Mutant 2: specs/picker.md:7, test_latest_report_returns_the_latest_dated_report — picks earliest — task-1-mutant-2.patch
Mutant 3: brief: .txt directly in folder, test_only_txt_files_directly_in_folder_count — recurses — task-1-mutant-3.patch
Mutant 4: brief: .txt directly in folder, test_only_txt_files_directly_in_folder_count — any extension — task-1-mutant-4.patch
Mutant 5: specs/picker.md:7, test_date_line_may_follow_other_lines_and_year_decides — ignores the year — task-1-mutant-5.patch
