Frozen catalog read fully before selection: 89,498 characters, five contiguous pages.
Catalog page spans: [0,18000), [18000,36000), [36000,54000), [54000,72000), [72000,89498).
Start helper used explicit native-routing workdir and a 24,000-token command budget; stdout retained in functions store.
Each catalog page was displayed/read in a separate functions.exec with a 6,000-token output budget.
Selected full body read through the recorded readskill helper: optimize-jax, 9,781 characters, one page [0,9781).
The skill page was displayed/read in a separate functions.exec with a 6,000-token output budget.
Both helper calls exited 0; captured outputs fit their command budgets; no recovery or reread was needed.
Primary selection rationale: direct coverage of speed measurement plus cache correctness in one execution-oriented skill.
Develop-testing-strategy is conditional on designing permanent tests, which this task does not explicitly establish.
Resident repository/skill workflow guidance was not substituted for the frozen catalog; selection-only limits precluded implementation workflows and repository reads.
Only authorized helpers and these two own artifacts were used; no other trials, plans, rubrics, manifests, references, scripts, web, or subagents were inspected or invoked.
