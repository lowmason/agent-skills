# Task 1 mutants

## Inputs

| Rule | Shape | Test |
|---|---|---|
| specs/picker.md:7 | two reports, later date in later-named file | test_latest_report_returns_the_latest_dated_report |
| specs/picker.md:7 | date line not first / after other lines | test_date_line_position_does_not_matter |
| specs/picker.md:8 | latest date in earliest-named file, three files | test_file_names_carry_no_order |
| brief: report is a .txt file directly in folder | non-.txt, subfolder, directory named .txt | test_non_txt_files_and_subfolders_are_not_reports |

## Mutants

Mutant 1: specs/picker.md:8, test_file_names_carry_no_order — picks by file name — task-1-mutant-1.patch
Mutant 2: specs/picker.md:7, test_latest_report_returns_the_latest_dated_report — picks earliest date — task-1-mutant-2.patch
Mutant 3: brief: .txt, test_non_txt_files_and_subfolders_are_not_reports — any extension accepted — task-1-mutant-3.patch
Mutant 4: brief: directly in folder, test_non_txt_files_and_subfolders_are_not_reports — recursive search — task-1-mutant-4.patch
Mutant 5: brief: file, test_non_txt_files_and_subfolders_are_not_reports — directories named .txt not excluded — task-1-mutant-5.patch
Mutant 6: specs/picker.md:7, test_date_line_position_does_not_matter — only first line is read for date — task-1-mutant-6.patch
