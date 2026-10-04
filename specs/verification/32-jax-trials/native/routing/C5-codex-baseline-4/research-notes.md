# Selection research notes
Task: Use BlackJAX to sample a posterior distribution.
Frozen trial: C5-codex-baseline-4; selected only from its supplied catalog.
Choice: bayesian-workflow primary; no supporting skills.
Task rationale: explicit BlackJAX/posterior/MCMC match, confirmed by the full BlackJAX sampler section.
Catalog stdout captured in functions store: 89,489 characters.
Catalog full-read pages: [0,18000), [18000,36000), [36000,54000), [54000,72000), [72000,89489).
Skill read via recorded readskill helper; full stdout captured: 33,781 characters.
Skill full-read pages: [0,18000), [18000,33781).
Every page displayed in a separate functions.exec call with an explicit 6000-token budget; capture commands used 24000 tokens.
Recovery: none required; both helper commands exited 0 and all contiguous pages were read.
Resident conflicts: general repository/skill execution, web, and delegation guidance did not expand this frozen selection-only fixture; no repository change was made.
Limits: no references, scripts, implementation, tests, plan/rubric/manifest, other trials, repository inspection, web, or subagents; only these two owned artifacts were written.
