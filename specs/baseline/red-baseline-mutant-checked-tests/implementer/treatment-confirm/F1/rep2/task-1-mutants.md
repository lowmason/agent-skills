# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/picker.md:7 | latest is in the later-named file | test_latest_report_returns_the_latest_dated_report |
| specs/picker.md:7 | date line after other lines; year boundary | test_date_line_may_follow_other_lines_and_year_decides_first |
| specs/picker.md:8 | latest file name first | test_file_names_carry_no_order |
| brief: .txt directly in folder | other extension; subfolder | test_only_txt_files_directly_in_the_folder_count |

## Mutants

Mutant 1: specs/picker.md:8, test_file_names_carry_no_order — picks by file name — task-1-mutant-1.patch
Mutant 2: specs/picker.md:7, test_latest_report_returns_the_latest_dated_report — picks earliest date — task-1-mutant-2.patch
Mutant 3: brief: .txt directly in folder, test_only_txt_files_directly_in_the_folder_count — recurses into subfolders — task-1-mutant-3.patch
Mutant 4: brief: .txt directly in folder, test_only_txt_files_directly_in_the_folder_count — accepts any extension — task-1-mutant-4.patch
