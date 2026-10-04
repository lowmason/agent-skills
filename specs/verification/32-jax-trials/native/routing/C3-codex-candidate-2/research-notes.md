# Selection research notes
Trial: C3-codex-candidate-2; task: Fix recompilation in a non-learning JAX calculation.
Frozen catalog start stdout captured completely in functions store native_c3_candidate_2_start: 89,489 characters.
Catalog fully read in separate 6,000-token calls: [0,18000), [18000,36000), [36000,54000), [54000,72000), [72000,89489).
Selected full bodies read with the recorded readskill helper; each helper exited 0 and used a 24,000-token command budget.
optimize-jax: 9,781 characters, fully displayed/read as [0,9781) in one 6,000-token call.
systematic-debugging: 10,177 characters, fully displayed/read as [0,10177) in one 6,000-token call.
Recovery: none needed; every stored stdout was fully paged without truncation.
Resident conflict: the resident catalog lacks optimize-jax; the frozen catalog supplied it and governed selection.
Resident implementation/CLAUDE/skill workflows were not invoked because this fixture authorizes selection only and prohibits repository/reference inspection.
Only the start/readskill helpers and these two owned artifacts were used; other files, trials, plans, scripts, web, and subagents were not inspected or invoked.
Other agents' work was preserved; no underlying task was implemented and no remediation outcome was claimed.
