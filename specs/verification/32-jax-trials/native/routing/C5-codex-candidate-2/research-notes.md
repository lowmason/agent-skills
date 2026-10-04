# Routing research notes
Trial: C5-codex-candidate-2; frozen helper catalog only.
Initial start used the repository workdir and failed with missing C5-codex-candidate-2/conditions.json; its complete 1,088-character error was read in one page.
Recovery reran the same start helper with explicit workdir /private/tmp/jax-skill-trials-pAYZ0t/native-routing; no alternate trial or file was inspected.
Successful start stdout: 89,485 characters, captured in functions store and fully read as five contiguous pages.
Catalog page boundaries: [0,18000), [18000,36000), [36000,54000), [54000,72000), [72000,89485).
Chosen read ID: bayesian-workflow; readskill helper completed successfully.
Selected body stdout: 33,776 characters, captured in functions store and fully read as [0,18000) and [18000,33776).
Every page display used a separate functions.exec call with explicit max_output_tokens 6000; helper command budgets were 24000.
Resident guidance favors skills, design, tests, and delegation, but this fixture explicitly permits selection only; no implementation workflow or subagent was invoked.
The repository CLAUDE.md requirement applies before repository changes; none were made, and repository inspection was outside the authorized fixture.
The selected skill references further reading, scripts, installation, and analysis outputs; those remain outside this simulation and were not accessed.
