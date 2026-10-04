# Claude Code guide conformance audit — 2026-10-04

## 1. Header

- **Date:** 2026-10-04.
- **Worktree:** `feat/cc-guide-conformance` at `e30c438` (plan 35, Tasks 1–7 committed: the anchored guide, the register skeleton and the lint).
- **Guide:** `specs/guides/claude-code-customization-guide.md`, at 2.1.288, with drift R1.1's 38 anchors.
- **Method (spec R5.2):** the lint's day-one run gives the mechanical rows (`L-nn`). Four read-only seats audited the rest, one per artifact group. Each seat read every section assigned to it, classified each rule as fact or advice, checked every artifact against it, and returned a findings table with verbatim single-line quotes, proposed checks, section-map notes and guide notes. The seats were `code-reviewer` subagents dispatched with model `sonnet`, all under the read-only guard:
  - **S:** skills.
  - **A:** agents and commands.
  - **H:** hooks, rules and settings, plus the outside-the-repo table `O`.
  - **C:** CLAUDE.md files and the installer.
- **Quotes re-grepped:** 352 of 352 verified. Each quote was checked as a single-line match of at most 25 words in its file. Every quote in a seat table has a re-grepped line. **Rows discarded as unverified: 0.**
- **Statuses** are the seats' own: follows, gap, deviation candidate or n/a. Nothing in sections 3–9 is decided. The owner decides at the gate (section 10).

## 2. Mechanical findings

| ID | check | section | file | message |
|---|---|---|---|---|
| L-01 | claude-md-size | rules.claude-md | CLAUDE.md | 238 lines; the guide targets fewer than 200 |
| L-02 | bash-search-tools | subagents.tools | agents/code-reviewer.md | lists Grep and Glob beside Bash, where both are absent and search runs through the shell |
| L-03 | bash-search-tools | subagents.tools | agents/debugger.md | lists Grep and Glob beside Bash, where both are absent and search runs through the shell |
| L-04 | bash-search-tools | subagents.tools | agents/docs-writer.md | lists Grep and Glob beside Bash, where both are absent and search runs through the shell |
| L-05 | bash-search-tools | subagents.tools | agents/explore.md | lists Grep and Glob beside Bash, where both are absent and search runs through the shell |
| L-06 | bash-search-tools | subagents.tools | agents/security-auditor.md | lists Grep and Glob beside Bash, where both are absent and search runs through the shell |
| L-07 | bash-search-tools | subagents.tools | agents/task-reviewer.md | lists Grep and Glob beside Bash, where both are absent and search runs through the shell |
| L-08 | bash-search-tools | subagents.tools | agents/test-runner.md | lists Grep and Glob beside Bash, where both are absent and search runs through the shell |
| L-09 | hook-dir-quoted | hooks.patterns | hooks/README.md | JSON block at line 51: PostToolUse command leaves $CLAUDE_PROJECT_DIR unquoted |
| L-10 | hook-dir-quoted | hooks.patterns | hooks/README.md | JSON block at line 51: PreToolUse command leaves $CLAUDE_PROJECT_DIR unquoted |
| L-11 | hook-dir-quoted | hooks.patterns | hooks/README.md | JSON block at line 51: Stop command leaves $CLAUDE_PROJECT_DIR unquoted |

The other four checks (`rule-paths`, `stop-hook-guard`, `agent-fields`, `readonly-agent-tools`) found nothing, and `claude-md-size` passed `build/CLAUDE.md`.

## 3. Findings by group

Each seat's table appears as returned, with its own notes. Rows keep their IDs, and no row was discarded. Seat H's outside-the-repo table is in section 8, and the seats' guide notes are in section 7.

### Skills (S)

Worktree HEAD is e30c438 and the tree is clean. I ran no mutating command. Scope: 35 `skills/*/SKILL.md` files. Frontmatter lines before the closing `---`: 9 for most skills, longer for some.

| ID | section | guide line | rule | fact/advice | artifact file:line | status | guide quote | artifact quote |
|---|---|---|---|---|---|---|---|---|
| S-01 | skills.overview | 53 | A skill is a directory holding SKILL.md | fact | skills/*/SKILL.md (35 files) | follows | "A skill is a directory with a `SKILL.md` (YAML frontmatter + Markdown body) plus optional supporting files:" | |
| S-02 | skills.overview | 57 | Keep the SKILL.md body well under 500 lines | advice | skills/writing-skills/SKILL.md:232 | gap | "keep the body well under 500 lines" | "carries, so treat a body pushing past ~2,000 words as a prompt to ask what belongs in" |
| S-03 | skills.overview | 57 | Same rule, remaining skills | advice | skills/*/SKILL.md (34 other files; max body 478 lines) | follows | "keep the body well under 500 lines" | |
| S-04 | skills.locations | 73 | Symlinked skills are followed | fact | skills/*/SKILL.md (35 files) | follows | "Symlinks are followed" | |
| S-05 | skills.locations | 73 | Same-name skill shadows the lower-precedence one | fact | .claude/skills/*/SKILL.md (0 files exist) | n/a | "a same-name skill shadows the lower-precedence one" | |
| S-06 | skills.locations | 70 | Nested .claude/skills load per subdirectory | fact | none (no nested skills) | n/a | "Nested `.claude/skills/` in subdirectories" | |
| S-07 | skills.locations | 71 | Plugin skills never shadow; namespaced | fact | none (repo ships no plugin) | n/a | "Never shadows — namespaced as `plugin:skill`" | |
| S-08 | skills.locations | 73 | claude.ai skills sync into terminal sessions | fact | none | n/a | "Skills enabled on your claude.ai account also sync into terminal sessions" | |
| S-09 | skills.frontmatter | 80 | Directory name also invokes the skill | fact | skills/*/SKILL.md (35 files) | follows | "the directory name also invokes the skill" | |
| S-10 | skills.frontmatter | 81 | Description capped at 1,536 characters in listing | fact | skills/*/SKILL.md (35 files; max 1,023 chars) | follows | "capped at 1,536 chars in the listing" | |
| S-11 | skills.frontmatter | 82 | when_to_use appends trigger context | fact | skills/*/SKILL.md (none sets it) | n/a | "Extra trigger context appended to the description" | |
| S-12 | skills.frontmatter | 83 | argument-hint and arguments define args | fact | skills/*/SKILL.md (none sets them) | n/a | "Autocomplete hint, e.g. `[issue-number]`" | |
| S-13 | skills.frontmatter | 85 | allowed-tools and disallowed-tools scope tools | fact | skills/*/SKILL.md (none sets them) | n/a | "Tools pre-approved for the turn the skill runs" | |
| S-14 | skills.frontmatter | 87 | model and effort override per turn; Haiku ignored in auto | fact | skills/*/SKILL.md (35 files; effort on 2, model on 0) | follows | "Per-turn model and reasoning-effort override" | |
| S-15 | skills.frontmatter | 88 | context: fork body must stand alone | fact | skills/tech-debt/SKILL.md:15 | follows | "the instructions must stand alone" | |
| S-16 | skills.frontmatter | 90 | Forked skill's background defaults to true | fact | skills/tech-debt/SKILL.md:15 | follows | "`true` (default, 2.1.218+) runs in background" | |
| S-17 | skills.frontmatter | 92 | user-invocable false hides skill from menu | fact | skills/*/SKILL.md (none sets it) | n/a | "hidden from the `/` menu" | |
| S-18 | skills.frontmatter | 93 | paths restricts auto-loading | fact | skills/*/SKILL.md (none sets it) | n/a | "Globs restricting when the skill is auto-loaded" | |
| S-19 | skills.frontmatter | 94 | hooks and shell frontmatter fields | fact | skills/*/SKILL.md (none sets them) | n/a | "Hooks registered when the skill is invoked" | |
| S-20 | skills.frontmatter | 96 | license and metadata accepted; unknown fields ignored | fact | skills/*/SKILL.md (35 files; keys used: name, description, license, metadata, effort, context) | follows | "Unknown fields are ignored silently" | |
| S-21 | skills.description | 103 | Write description in third person | advice | skills/clean-coder/SKILL.md:5 | gap | "Write it in **third person**" | "applying cleanups to code you are already editing; noticing adjacent" |
| S-22 | skills.description | 103 | Write description in third person | advice | skills/executing-plans/SKILL.md:4 | gap | "Write it in **third person**" | "Use when you have a written implementation plan to execute yourself, task by task, in the" |
| S-23 | skills.description | 103 | Write description in third person | advice | skills/explore-data/SKILL.md:6 | gap | "Write it in **third person**" | "is actually unique; when you suspect duplicates," |
| S-24 | skills.description | 103 | Write description in third person | advice | skills/recommend-visualization/SKILL.md:4 | gap | "Write it in **third person**" | "Use when you need to choose — and then build — the right chart for a dataset:" |
| S-25 | skills.description | 103 | Write description in third person | advice | skills/systematic-debugging/SKILL.md:8 | gap | "Write it in **third person**" | "you're tempted to try one more quick change." |
| S-26 | skills.description | 103 | Write description in third person | advice | skills/validate-data/SKILL.md:5 | gap | "Write it in **third person**" | "the last gate before a number leaves your laptop." |
| S-27 | skills.description | 103 | Write description in third person | advice | skills/writing-plans/SKILL.md:4 | gap | "Write it in **third person**" | "Use when you have a spec, design doc, or requirements for a multi-step task and need an" |
| S-28 | skills.description | 103 | State both what the skill does and when | advice | skills/bayesian-workflow/SKILL.md:4 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when building, fitting, diagnosing, comparing, or reporting on Bayesian/probabilistic" |
| S-29 | skills.description | 103 | State both what the skill does and when | advice | skills/brainstorming/SKILL.md:4 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when the user proposes new functionality — a feature, component, script, scraper, pipeline," |
| S-30 | skills.description | 103 | State both what the skill does and when | advice | skills/clean-coder/SKILL.md:4 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when editing, fixing, or refactoring existing Python — before touching code near the" |
| S-31 | skills.description | 103 | State both what the skill does and when | advice | skills/creative-thinking/SKILL.md:4 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when the target itself is fuzzy:" |
| S-32 | skills.description | 103 | State both what the skill does and when | advice | skills/deep-learning/SKILL.md:4 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when designing, implementing, training, fine-tuning, post-training, or" |
| S-33 | skills.description | 103 | State both what the skill does and when | advice | skills/design-architecture/SKILL.md:4 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when authoring or evaluating Architecture Decision Records (ADRs) for data and modeling" |
| S-34 | skills.description | 103 | State both what the skill does and when | advice | skills/develop-testing-strategy/SKILL.md:4 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when designing a test strategy or plan for data-science code" |
| S-35 | skills.description | 103 | State both what the skill does and when | advice | skills/dispatching-parallel-agents/SKILL.md:4 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when 2+ tasks are independent" |
| S-36 | skills.description | 103 | State both what the skill does and when | advice | skills/evaluate-deep-learning/SKILL.md:4 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when benchmarking neural models, comparing checkpoints or methods," |
| S-37 | skills.description | 103 | State both what the skill does and when | advice | skills/executing-plans/SKILL.md:4 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when you have a written implementation plan to execute yourself," |
| S-38 | skills.description | 103 | State both what the skill does and when | advice | skills/finishing-a-development-branch/SKILL.md:4 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when implementation on a development branch is complete and tests pass, and the work needs" |
| S-39 | skills.description | 103 | State both what the skill does and when | advice | skills/geographic-codes/SKILL.md:4 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when a task touches U.S. statistical geography codes over any time span" |
| S-40 | skills.description | 103 | State both what the skill does and when | advice | skills/llm-wiki/SKILL.md:4 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when maintaining or setting up the research wiki (Karpathy LLM-wiki" |
| S-41 | skills.description | 103 | State both what the skill does and when | advice | skills/optimize-jax/SKILL.md:4 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when JAX code has tracing errors, unexpected recompilation, memory" |
| S-42 | skills.description | 103 | State both what the skill does and when | advice | skills/receiving-code-review/SKILL.md:4 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when receiving code review feedback" |
| S-43 | skills.description | 103 | State both what the skill does and when | advice | skills/recommend-visualization/SKILL.md:4 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when you need to choose — and then build — the right chart for a dataset:" |
| S-44 | skills.description | 103 | State both what the skill does and when | advice | skills/requesting-code-review/SKILL.md:4 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when completed work needs a code review" |
| S-45 | skills.description | 103 | State both what the skill does and when | advice | skills/subagent-driven-development/SKILL.md:4 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when executing an implementation plan task-by-task in the current session." |
| S-46 | skills.description | 103 | State both what the skill does and when | advice | skills/systematic-debugging/SKILL.md:4 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes" |
| S-47 | skills.description | 103 | State both what the skill does and when | advice | skills/tech-debt/SKILL.md:4 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when auditing a research or data codebase for technical debt" |
| S-48 | skills.description | 103 | State both what the skill does and when | advice | skills/test-driven-development/SKILL.md:3 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when implementing any feature or bugfix, before writing implementation code" |
| S-49 | skills.description | 103 | State both what the skill does and when | advice | skills/using-git-worktrees/SKILL.md:4 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when starting feature work, a bugfix, or plan execution that must not disturb the current" |
| S-50 | skills.description | 103 | State both what the skill does and when | advice | skills/verification-before-completion/SKILL.md:4 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when about to claim work is complete, fixed, done, or passing" |
| S-51 | skills.description | 103 | State both what the skill does and when | advice | skills/writing-plans/SKILL.md:4 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when you have a spec, design doc, or requirements for a multi-step task and need an" |
| S-52 | skills.description | 103 | State both what the skill does and when | advice | skills/writing-skills/SKILL.md:4 | deviation candidate | "stating both *what* the skill does and *when* to use it" | "Use when creating a new skill, editing or renaming an existing skill, or verifying a skill" |
| S-53 | skills.description | 103 | State both what the skill does and when | advice | skills/*/SKILL.md (10 files add a what clause; listed in note N11) | follows | "stating both *what* the skill does and *when* to use it" | |
| S-54 | skills.description | 104 | Pack description with concrete trigger phrases | advice | skills/test-driven-development/SKILL.md:3 | deviation candidate | "Pack it with **concrete trigger phrases** that mirror how you actually phrase requests." | "Use when implementing any feature or bugfix, before writing implementation code" |
| S-55 | skills.description | 104 | Same rule, remaining skills | advice | skills/*/SKILL.md (34 other files) | follows | "Pack it with **concrete trigger phrases** that mirror how you actually phrase requests." | |
| S-56 | skills.description | 105 | Front-load the primary use case | advice | skills/*/SKILL.md (35 files; every description opens "Use when") | follows | "Front-load the primary use case; the cap is 1,536 characters including `when_to_use`." | |
| S-57 | skills.description | 106 | Make a skill pushier when it under-triggers | advice | skills/*/SKILL.md (no trigger evidence in repo) | n/a | "Skills **under-trigger** on short requests more often than they over-trigger" | |
| S-58 | skills.listing-budget | 111 | Overflowing descriptions are dropped, not always resident | fact | skills/writing-skills/SKILL.md:222 | gap | "it **drops entire descriptions, least-invoked skills first**" | "`description` is resident in EVERY conversation" |
| S-59 | skills.listing-budget | 111 | Listing budget is about 1% of the window | fact | skills/*/SKILL.md (35 files as an aggregate) | n/a | "budgeted at roughly **1% of the model's context window** (a character budget)" | |
| S-60 | skills.listing-budget | 114 | Each listing entry capped at 1,536 characters | fact | skills/*/SKILL.md (35 files; max 1,023 chars) | follows | "each entry stays capped at 1,536 characters regardless" | |
| S-61 | skills.listing-budget | 113 | /doctor and /skill-doctor report listing cost | fact | none | n/a | "`/doctor` estimates the listing cost" | |
| S-62 | skills.listing-budget | 114 | skillListingBudgetFraction raises the budget | fact | none (a settings key) | n/a | "`skillListingBudgetFraction` in settings" | |
| S-63 | skills.listing-budget | 116 | skillOverrides sets name-only or off per skill | fact | none (a settings key) | n/a | "`skillOverrides` sets individual skills" | |
| S-64 | skills.listing-budget | 117 | Disable unused plugins | advice | none (repo ships no plugin) | n/a | "Disable unused plugins" | |
| S-65 | skills.progressive-disclosure | 122 | Bundled files load only when the body points at them | fact | skills/*/SKILL.md (35 files) | follows | "bundled files (loaded only when the body points at them)" | |
| S-66 | skills.progressive-disclosure | 122 | Name references explicitly in body prose | advice | skills/*/SKILL.md (35 files) | follows | "named explicitly in prose" | |
| S-67 | skills.progressive-disclosure | 124 | Put critical instructions near top; compaction keeps 5,000 tokens | advice | skills/writing-skills/SKILL.md:98 | gap | "so put the critical instructions near the top of `SKILL.md`" | "## SKILL.md Structure" |
| S-68 | skills.progressive-disclosure | 124 | Put critical instructions near top; compaction keeps 5,000 tokens | advice | skills/writing-skills/SKILL.md:630 | gap | "so put the critical instructions near the top of `SKILL.md`" | "## STOP: Before Moving to Next Skill" |
| S-69 | skills.progressive-disclosure | 124 | Put critical instructions near top; compaction keeps 5,000 tokens | advice | skills/subagent-driven-development/SKILL.md:436 | gap | "so put the critical instructions near the top of `SKILL.md`" | "## Red Flags" |
| S-70 | skills.progressive-disclosure | 124 | Put critical instructions near top; compaction keeps 5,000 tokens | advice | skills/bayesian-workflow/SKILL.md:323 | gap | "so put the critical instructions near the top of `SKILL.md`" | "## Common gotchas" |
| S-71 | skills.progressive-disclosure | 124 | Same rule, remaining skills | advice | skills/*/SKILL.md (32 other files; est. body at most 4.6k tokens) | follows | "so put the critical instructions near the top of `SKILL.md`" | |
| S-72 | skills.progressive-disclosure | 126 | Write the body as a process, not prose | advice | skills/*/SKILL.md (35 files; judged by structure) | follows | "a numbered workflow with steps, checkpoints, and exit criteria gets executed" | |
| S-73 | skills.progressive-disclosure | 126 | Bundle deterministic logic as scripts | advice | skills/*/SKILL.md (35 files) | follows | "Bundle deterministic logic as scripts in `scripts/`" | |
| S-74 | skills.arguments | 139 | Substitution tokens in a body are rewritten; escape with \$ | fact | skills/*/SKILL.md (35 files; 0 `$digit`, `$ARGUMENTS` or `${CLAUDE_` hits) | follows | "Escapes a `$` before a digit, `ARGUMENTS`, or a declared argument name" | |
| S-75 | skills.arguments | 136 | ${CLAUDE_SKILL_DIR} gives the skill's own directory | fact | skills/*/SKILL.md (none uses it; 12 use a `<this-skill-dir>` placeholder) | n/a | "(also usable inside `allowed-tools`)" | |
| S-76 | skills.arguments | 141 | !`command` runs once at render time | fact | skills/*/SKILL.md (none uses it) | n/a | "runs a shell command **once, at render time, before Claude sees the content**" | |
| S-77 | skills.iterating | 150 | Symptom-to-fix table for trigger problems | advice | skills/*/SKILL.md (no trigger evidence in repo) | n/a | "Pushier, more concrete description; add the phrases you actually used" | |
| S-78 | skills.iterating | 156 | Keep human review on judgment calls | advice | skills/*/SKILL.md (a design stance, no testable property) | n/a | "Keep human review on the judgment calls" | |
| S-79 | commands.overview | 161 | On a name collision the skill wins | fact | skills/*/SKILL.md (35 files; 0 collide with commands/*.md) | follows | "on a name collision the skill wins" | |
| S-80 | commands.overview | 163 | Docs recommend a skill for new work | advice | none (bears on commands/) | n/a | "the docs now recommend a skill for new work" | |
| S-81 | commands.overview | 163 | Side-effecting workflows set disable-model-invocation | advice | skills/finishing-a-development-branch/SKILL.md:241 | deviation candidate | "set `disable-model-invocation: true` on anything side-effecting" | "git merge <feature-branch>" |
| S-82 | commands.overview | 163 | Side-effecting workflows set disable-model-invocation | advice | skills/using-git-worktrees/SKILL.md:100 | deviation candidate | "set `disable-model-invocation: true` on anything side-effecting" | 'git worktree add "$path" -b "$BRANCH_NAME"' |
| S-83 | commands.overview | 163 | Side-effecting workflows set disable-model-invocation | advice | skills/brainstorming/SKILL.md:34 | deviation candidate | "set `disable-model-invocation: true` on anything side-effecting" | "save the spec to `specs/<descriptive-name>.md` and commit" |
| S-84 | commands.overview | 163 | Side-effecting workflows set disable-model-invocation | advice | skills/writing-plans/SKILL.md:275 | deviation candidate | "set `disable-model-invocation: true` on anything side-effecting" | "**5. Retire.** `git mv` the plan to `specs/plans/completed/`, in one" |
| S-85 | commands.overview | 163 | Side-effecting workflows set disable-model-invocation | advice | skills/executing-plans/SKILL.md:70 | deviation candidate | "set `disable-model-invocation: true` on anything side-effecting" | "tests, and commit the fixes — the plan-completion protocol commits only" |
| S-86 | commands.overview | 163 | Side-effecting workflows set disable-model-invocation | advice | skills/describe-critique-methodology/SKILL.md:74 | deviation candidate | "set `disable-model-invocation: true` on anything side-effecting" | "Commit the description in the target repo," |
| S-87 | commands.overview | 163 | Side-effecting workflows set disable-model-invocation | advice | skills/llm-wiki/SKILL.md:53 | deviation candidate | "set `disable-model-invocation: true` on anything side-effecting" | "**Every mutating operation appends one line to `log.md`**" |
| S-88 | commands.overview | 163 | Side-effecting workflows set disable-model-invocation | advice | skills/subagent-driven-development/SKILL.md:22 | gap | "set `disable-model-invocation: true` on anything side-effecting" | "Do not pause to check in with your human partner between tasks." |
| S-89 | commands.overview | 163 | Side-effecting workflows set disable-model-invocation | advice | skills/requesting-code-review/SKILL.md:19 | gap | "set `disable-model-invocation: true` on anything side-effecting" | "pair this reviewer with a Codex second opinion" |
| S-90 | commands.overview | 163 | Side-effecting workflows set disable-model-invocation | advice | skills/writing-skills/SKILL.md:681 | gap | "set `disable-model-invocation: true` on anything side-effecting" | "Commit skill to git and push to your fork (if configured)" |
| S-91 | commands.overview | 163 | Side-effecting workflows set disable-model-invocation | advice | skills/dispatching-parallel-agents/SKILL.md:18 | gap | "set `disable-model-invocation: true` on anything side-effecting" | "Dispatch one agent per independent problem domain." |
| S-92 | commands.overview | 163 | Side-effecting workflows set disable-model-invocation | advice | skills/derive-roadmap/SKILL.md:126 | deviation candidate | "set `disable-model-invocation: true` on anything side-effecting" | "as self-contained items; the roadmap moves to" |
| S-93 | mechanisms.overview | 44 | Sometimes-relevant knowledge or workflows go in a skill | advice | skills/*/SKILL.md (35 files) | follows | "Sometimes-relevant knowledge or a multi-step workflow" | |
| S-94 | mechanisms.overview | 40 | Machine-checkable rules belong in a hook | advice | skills/subagent-driven-development/SKILL.md:156 | gap | "Deterministic and machine-checkable" | "**Always specify the model explicitly when dispatching**" |
| S-95 | mechanisms.overview | 40 | Same rule, remaining skills | advice | skills/*/SKILL.md (34 other files) | follows | "Deterministic and machine-checkable" | |
| S-96 | lean.ceremony | 451 | Skip brainstorming when you can already describe the solution | advice | skills/brainstorming/SKILL.md:23 | deviation candidate | "You can already describe the solution" | "Every project goes through this process. A todo list, a single-function utility, a config change — all of them." |
| S-97 | lean.ceremony | 454 | Skip TDD for formatting, docs and config | advice | skills/writing-skills/SKILL.md:404 | deviation candidate | "Formatting, docs, config" | 'Not for "documentation updates"' |
| S-98 | lean.ceremony | 454 | Skip TDD for formatting, docs and config | advice | skills/test-driven-development/SKILL.md:24 | follows | "Formatting, docs, config" | |
| S-99 | lean.ceremony | 456 | Skip review for a small change you watched | advice | skills/requesting-code-review/SKILL.md:21 | gap | "You watched every step of a small change" | "Before merge to main" |
| S-100 | lean.ceremony | 457 | Verification is always kept | advice | skills/verification-before-completion/SKILL.md, skills/finishing-a-development-branch/SKILL.md | follows | "**Always** — a runnable check is what lets you walk away" | |
| S-101 | lean.ceremony | 463 | Full path: spec in one session, implement in a fresh one | advice | skills/brainstorming/SKILL.md, skills/writing-plans/SKILL.md | follows | "implementation started fresh from the spec file" | |
| S-102 | lean.ceremony | 455 | Subagents for read-heavy or fresh-context work only | advice | skills/subagent-driven-development/SKILL.md, skills/dispatching-parallel-agents/SKILL.md | follows | "Read-heavy research or fresh-context review" | |
| S-103 | lean.expensive-ops | 470 | Persist costly results to disk immediately | advice | skills/bayesian-workflow/SKILL.md:157 | follows | "**Persist results to disk immediately**" | |
| S-104 | lean.expensive-ops | 471 | Gate costly commands behind a manual skill or deny | advice | skills/geographic-codes/SKILL.md:37 | gap | "**Gate the expensive command behind a manual skill**" | "If `data/` is missing, rebuild it first." |
| S-105 | lean.expensive-ops | 471 | Gate costly commands behind a manual skill or deny | advice | skills/classification-codes/SKILL.md:37 | gap | "**Gate the expensive command behind a manual skill**" | "rebuild it (see *Rebuilding*) rather than guessing." |
| S-106 | lean.expensive-ops | 472 | Verify from saved output, not a re-run | advice | skills/bayesian-workflow/SKILL.md (harness reads saved diagnostics JSON) | follows | "**Verify from saved output**" | |
| S-107 | rules.hierarchy | 240 | @ imports inline a file at load time (CLAUDE.md) | fact | skills/writing-skills/SKILL.md:304 | gap | "`@path/to/file` inside CLAUDE.md inlines another file at load time" | "`@` syntax force-loads files immediately, consuming 200k+ context before you need them." |

#### Row notes

- **R5.7 verdicts.**
  - Body length, S-02: confirmed.
  - Line 222, S-58: confirmed.
  - Line 304, S-107: candidate rejected as a contradiction (see N3), recorded as an unsupported claim.
  - No critical-rules-first advice, S-67: confirmed.
  - brainstorming, S-96: confirmed as a departure and recorded as a deviation candidate.
- **N1 (S-02, S-03).**
  - Body means the lines after the closing frontmatter `---`.
  - Longest bodies: writing-skills 696 (705 file lines, unchanged since 54fc246), subagent-driven-development 478, finishing-a-development-branch 421, test-driven-development 352, bayesian-workflow 337.
  - Threshold applied is 500. That is the repo's own measure (portability spec R1.7; the closed deferred item that trimmed subagent-driven-development to under ~500). The guide does not quantify "well under".
  - The two files above 400 lines are flagged here, not counted as gaps.
  - Splitting writing-skills is tracked as Out of scope at specs/agent-skills-portability.md:399 and in conformance Decision 10. I found no `specs/deferred_items.md` entry for it.
- **N2 (S-58).** The same "always resident" premise recurs at writing-skills:227-229. It matches the guide's own line 122, which conflicts with line 111 (E note S-108).
- **N3 (S-107).**
  - The guide documents `@` imports only inside CLAUDE.md.
  - The mechanism it states (inlines at load time) agrees with the skill, so there is no contradiction.
  - The SKILL.md scope and the "200k+" figure are not in the guide: unsupported, not contradicted.
  - The claim recurs at writing-skills:302.
  - Reject this row if the owner reserves "gap" for contradictions only.
- **N4 (S-67 to S-71).**
  - Token figures are estimates (body characters / 4), not a tokenizer.
  - writing-skills past the 5,000-token cut:
    - STOP section :630 (~6.4k)
    - Skill Creation Checklist :643 (~6.5k)
    - Discovery Workflow :684 (~7.0k)
    - Its Iron Law at :390 (~3.8k) is inside the cut.
  - subagent-driven-development past the cut:
    - Context Checkpoints :395 (~6.0k)
    - Red Flags :436 (~6.6k)
    - Integration :475 (~7.1k)
  - bayesian-workflow past the cut:
    - Common gotchas :323 (~6.5k)
    - When things go wrong :340 (~7.6k)
    - Its Critical rules at :242 (~3.7k) is inside the cut.
  - Nearest others: validate-data ~4.6k, develop-testing-strategy ~4.3k.
  - S-67: grep of writing-skills for compact, re-attach, 5,000, near the top and front-load returns no hits. Its template at :112-144 opens Overview, then When to Use.
- **N5 (S-96).**
  - The citable skill rule is the Anti-Pattern at brainstorming:21-23 ("Simple" projects are where unexamined assumptions cause the most wasted work). The description repeats it at :8 ("however simple it looks").
  - Counter-evidence in the repo: commands/deferred.md:2 says the ceremony should match the item and reserves brainstorming for items that record an open design decision.
  - The guide's Micro path at line 461 lists "config" under no spec, plan or review.
- **N6 (S-97).** The cited reason is writing-skills:409: tests written after the fact prove nothing, so the skill treats its documentation as behaviour-shaping.
- **N7 (S-14).** The guide lists no valid `effort` values, so `xhigh` (bayesian-workflow:14, tune-hyperparameters:13) cannot be checked against it.
- **N8 (S-16).**
  - tech-debt sets neither `agent` nor `background`, so it runs as general-purpose and in the background by default.
  - `build/check_frontmatter.py` ALLOWED_KEYS rejects both keys today.
- **N9 (S-59).**
  - Names plus descriptions of the 35 skills total 21,297 characters.
  - Whether that fits depends on window size and `skillListingBudgetFraction`. Neither is in repo files (.claude/settings.json sets neither), so I give no verdict.
- **N10 (S-72).** I judged structure for all 35 bodies (headings, numbered steps, tables, checklists), not content. Skills with no numbered steps: bls-data-context, classification-codes, clean-code, evaluate-deep-learning, geographic-codes, optimize-jax, recommend-visualization, requesting-code-review, test-driven-development, track-model-experiments, tune-hyperparameters, writing-plans.
- **N11 (S-28 to S-53).**
  - Reason cited: writing-skills:157-165 (tested evidence that a workflow summary in the description lets agents skip the body), plus portability Decisions 4 and 5. The register's draft exception `description-when-only` can cite S-28 to S-52.
  - S-43 and S-47 are counted as when-only because their only non-trigger text is a one-line scope tag.
  - S-53 covers the 10 that add a what clause: bls-data-context, classification-codes, clean-code, derive-roadmap, describe-critique-methodology, explore-data, recommend-probabilistic-model, track-model-experiments, tune-hyperparameters, validate-data.
- **N12 (S-21 to S-27).**
  - These are second-person "you/your" outside quoted user phrases.
  - Pronouns inside quoted trigger phrases are user phrasing and not counted. That covers the "I" and "we" quotes in brainstorming, creative-thinking, design-architecture, develop-testing-strategy and the recommend-* skills, and tech-debt's quoted "Add your description here".
  - writing-skills:106, :186 and :656 hold the same third-person rule, with no recorded exception.
- **N13 (S-54, S-55).**
  - Nine descriptions have neither a quoted phrase nor a "Trigger on" list: deep-learning, dispatching-parallel-agents, evaluate-deep-learning, executing-plans, optimize-jax, receiving-code-review, requesting-code-review, test-driven-development, using-git-worktrees. They name concrete conditions, so I count them as following.
  - TDD alone is a deviation candidate: 79 characters, and writing-skills:178 and :565 hold up exactly that string as GOOD.
  - Portability Decision 5 records that no descriptions were rewritten.
- **N14 (S-94).** "Always specify the model on dispatch" is a tool-call parameter a PreToolUse hook could require. I found no recorded reason for keeping it in prose.
- **N15 (S-98).** TDD exempts configuration files (:24-28) but lists neither docs nor formatting. Its scope (features, bug fixes, behaviour changes) does not reach them, so I record it as following. Its "Always: Refactoring" is a mild departure from "Logic or behavior changes" and is left unflagged.

#### R2.7 list: side-effecting yet model-invocable skills

None of the 35 skills sets `disable-model-invocation`. The lint's ALLOWED_KEYS would reject the key on a SKILL.md today (see C-9).

**Criterion counted.** The skill's own procedure does one of:
1. changes git history, branches or worktrees;
2. moves or deletes tracked files;
3. writes outside the project tree;
4. pulls from the network or sends code off-machine;
5. fans out paid subagents.

Plain authoring (ADR, ledger, source edits) is not counted.

**Decision 3 reason** (portability spec): a manual-only skill cannot receive a bare-name handoff, and the body gates the side effect. Two conditions follow from it:
- **(a)** an inbound bare-name reference exists;
- **(b)** the body gates the side effect.

Both hold gives deviation candidate; either fails gives gap.

| skill | side effect | (a) inbound bare-name reference | (b) body gate | row | status |
|---|---|---|---|---|---|
| finishing-a-development-branch | merge, push, PR, branch delete, worktree remove; Codex review sends the diff off-machine (README.md:15) | yes: executing-plans, writing-plans, subagent-driven-development, requesting-code-review/codex-review.md | yes for git ops: 4-option menu :152, typed discard :318. The Codex step has no consent gate | S-81 | deviation candidate |
| using-git-worktrees | worktree add, branch create, commits a .gitignore edit (:90) | yes: executing-plans, finishing, writing-plans, subagent-driven-development | yes: consent before creating (:45) | S-82 | deviation candidate |
| brainstorming | commits the spec; opens a local server and browser tab | yes: derive-roadmap, writing-plans refs, describe-critique-methodology, creative-thinking, /deferred, /fix-issue | yes: HARD-GATE :17, spec review :36, companion offer needs consent | S-83 | deviation candidate |
| writing-plans | plan retirement: `git mv` and commits (:275) | yes: derive-roadmap, executing-plans, finishing, brainstorming, subagent-driven-development, /deferred | partial: resolve-before-defer gate :200; the retirement commit is ungated but lands on the feature branch | S-84 | deviation candidate |
| executing-plans | commits fixes (:70); whole-plan Codex review (:64-65) | yes: finishing, writing-plans, requesting-code-review, subagent-driven-development | partial: concerns raised first (:24), consent for base-branch execution (:26); commits and Codex step ungated | S-85 | deviation candidate |
| describe-critique-methodology | commits description and critique (:74) | yes: derive-roadmap, agents/docs-writer.md | partial: user gate before the roadmap handoff (:116); commits precede it | S-86 | deviation candidate |
| llm-wiki | writes pages and log.md; bootstrap writes under $LLM_WIKI_ROOT, outside the repo | weak: one pointer (describe-critique-methodology/references/wiki-touchpoints.md:9, a read-only query) | yes: root confirmed with the human before bootstrap (:29) | S-87 | deviation candidate |
| derive-roadmap | parks a roadmap: moves it to specs/completed/ and retires the methodology and critique files (:126-128) | yes: writing-plans refs, describe-critique-methodology, /deferred | partial: stops on a header collision (:96); parking is a Resume exit | S-92 | deviation candidate |
| subagent-driven-development | subagent commits per task, paid fan-out, Codex review | yes: eight skills and agents | no: continuous execution, no check-ins (:22) | S-88 | gap |
| requesting-code-review | reviewer dispatch; the Codex second opinion sends the diff and files read to OpenAI (README.md:15, codex-review.md:43) | yes: executing-plans, finishing, receiving-code-review, subagent-driven-development, agents/code-reviewer.md | no: skipped only when `codex` is absent | S-89 | gap |
| writing-skills | commit and push to a fork (:681) | CLAUDE.md:59 only | no | S-90 | gap |
| dispatching-parallel-agents | paid subagent fan-out only | none | no | S-91 | gap |
| geographic-codes, classification-codes | network rebuild of data/ when absent (:37 each) | pointers only, from bls-data-context | partial: BLS contact-email variable | S-104, S-105 under lean.expensive-ops | gap |

Not counted:
- design-architecture (ADR scaffolder), track-model-experiments (ledger rewrite) and clean-coder (governs commit shape only): authoring only.
- tech-debt: forked, read-only scan.

### Agents and commands (A)

Seat: Agents and commands. 7 agents, 3 commands, 9 sections.

Two things are not in the table:
- subagents.tools line 202's Grep/Glob-with-Bash catch is covered by L-02 to L-08, which cover all seven agents. I added no row for it.
- The remaining optional fields have no row because no artifact sets them. YAML-parsed keys are only `name, description, tools, model, effort` for agents and `description, disable-model-invocation` for commands. Agent fields not rowed: disallowedTools, permissionMode, maxTurns, skills, mcpServers, hooks, background, experimental.cacheTtl, color, initialPrompt, `Agent(...)` in tools. Skill-table fields not rowed: when_to_use, arguments, allowed-tools, disallowed-tools, context, agent, background, user-invocable, paths, hooks, shell, license/compatibility/metadata, and the `$0`, `$name`, `${CLAUDE_*}` substitutions.

| ID | section | guide line | rule | fact/advice | artifact file:line | status | guide quote | artifact quote |
|---|---|---|---|---|---|---|---|---|
| A-01 | subagents.overview | 168 | Agent file is Markdown: frontmatter plus a system-prompt body | fact | agents/*.md (7 files) | follows | frontmatter plus a system prompt in the body | |
| A-02 | subagents.overview | 168 | Use isolated context, per-agent model, scoped tools together | advice | agents/*.md (7 files) | follows | an isolated context window, a per-agent model, and a scoped tool set | |
| A-03 | subagents.overview | 168 | Same-name agents resolve project over personal | fact | none (no `.claude/agents/` file exists) | n/a | here project beats personal, the reverse of skills | |
| A-04 | subagents.frontmatter | 175 | Agent name is a lowercase-hyphenated ID | fact | agents/explore.md:9 | deviation candidate | Unique lowercase-hyphenated ID | name: Explore |
| A-05 | subagents.frontmatter | 175 | Agent name is a lowercase-hyphenated ID | fact | agents/*.md (6 of 7 files, all but explore.md) | follows | Unique lowercase-hyphenated ID | |
| A-06 | subagents.frontmatter | 176 | Agent descriptions carry concrete triggers and stay short | advice | agents/*.md (7 files, 261 to 445 chars) | follows | every agent's description sits in context, so keep it short | |
| A-07 | subagents.frontmatter | 177 | Set a tools allowlist; omitting it inherits everything | fact | agents/*.md (7 files) | follows | Allowlist (omit to inherit all, MCP tools included) | |
| A-08 | subagents.frontmatter | 179 | model is an alias or ID; per-spawn model outranks it | fact | agents/*.md (7 files) | follows | Resolution order: a per-spawn `model` Claude passes → this field → `CLAUDE_CODE_SUBAGENT_MODEL` → the main model | |
| A-09 | subagents.frontmatter | 180 | effort runs from low to max | fact | agents/*.md (2 of 7 set effort: xhigh) | follows | `low` … `max` reasoning effort for this agent | |
| A-10 | subagents.frontmatter | 188 | isolation: worktree runs an agent in a disposable worktree | fact | none (no agent sets isolation) | n/a | `worktree` runs it in a disposable git worktree (auto-cleaned if unchanged) | |
| A-11 | subagents.frontmatter | 189 | omitClaudeMd launches an agent without CLAUDE.md files | fact | none (no agent sets omitClaudeMd) | n/a | `true` launches it without user, project, and local CLAUDE.md (managed files still load) | |
| A-12 | subagents.tools | 198 | Reviewers and auditors get Read, Grep, Glob only | advice | agents/code-reviewer.md:4 | deviation candidate | `Read, Grep, Glob` — analyze without modifying | tools: Read, Grep, Glob, Bash |
| A-13 | subagents.tools | 198 | Reviewers and auditors get Read, Grep, Glob only | advice | agents/security-auditor.md:4 | deviation candidate | `Read, Grep, Glob` — analyze without modifying | tools: Read, Grep, Glob, Bash |
| A-14 | subagents.tools | 198 | Reviewers and auditors get Read, Grep, Glob only | advice | agents/task-reviewer.md:4 | deviation candidate | `Read, Grep, Glob` — analyze without modifying | tools: Read, Grep, Glob, Bash |
| A-15 | subagents.tools | 198 | Reviewers and auditors get Read, Grep, Glob only | advice | agents/explore.md:11 | deviation candidate | `Read, Grep, Glob` — analyze without modifying | tools: Read, Grep, Glob, Bash |
| A-16 | subagents.tools | 199 | Researchers add WebFetch and WebSearch | advice | none (Explore searches the repo, not the web) | n/a | add `WebFetch, WebSearch` | |
| A-17 | subagents.tools | 196 | Scope each agent's tools to its role | advice | agents/test-runner.md (1 file) | follows | Least privilege keeps agents focused and safe: | |
| A-18 | subagents.tools | 200 | Implementers get Read, Write, Edit, Bash | advice | agents/debugger.md:4 | deviation candidate | `Read, Write, Edit, Bash` | tools: Read, Edit, Bash, Grep, Glob |
| A-19 | subagents.tools | 200 | Implementers get Read, Write, Edit, Bash | advice | agents/docs-writer.md (1 file) | follows | `Read, Write, Edit, Bash` | |
| A-20 | subagents.tools | 202 | A documentation agent does not need Bash | advice | agents/docs-writer.md:4 | gap | A documentation agent doesn't need `Bash` | tools: Read, Write, Edit, Grep, Glob, Bash |
| A-21 | subagents.tools | 202 | A review agent does not need Write | advice | agents/{code-reviewer,security-auditor,task-reviewer}.md (3 files) | follows | a review agent doesn't need `Write` | |
| A-22 | subagents.tools | 202 | memory adds Read/Write/Edit; keep it off read-only roles | fact | agents/*.md (7 files, none sets memory) | follows | `memory:` silently adds Read/Write/Edit, so keep it off read-only roles | |
| A-23 | subagents.models | 209 | Haiku takes test-running and search work | advice | agents/test-runner.md:5, agents/explore.md:12 (2 files) | follows | test-running, formatting checks, mechanical review, classification, search/exploration | |
| A-24 | subagents.models | 210 | Sonnet takes implementation work | advice | agents/debugger.md:5, agents/docs-writer.md:5 (2 files) | follows | **Sonnet**: implementation. | |
| A-25 | subagents.models | 211 | Opus takes adversarial correctness review | advice | agents/code-reviewer.md:5, agents/security-auditor.md:5 (2 files) | follows | planning, architecture, adversarial correctness review | |
| A-26 | subagents.models | 211 | Opus takes adversarial correctness review | advice | agents/task-reviewer.md:5 | deviation candidate | planning, architecture, adversarial correctness review | task-review floor per subagent-driven-development Model Selection |
| A-27 | subagents.models | 207 | Haiku's retirement window opens 2026-10-15 | fact | agents/explore.md:12, agents/test-runner.md:5 (2 files) | follows | its retirement window opens 2026-10-15 | |
| A-28 | subagents.models | 207 | Haiku's window is 200K tokens, against 1M | fact | agents/test-runner.md (1 file) | follows | Haiku's window is 200K tokens against 1M for the current Fable, Opus, and Sonnet | |
| A-29 | subagents.models | 214 | To explore on Haiku, define your own Explore | fact | agents/explore.md (1 file) | follows | define your own `Explore` with `model: haiku` (it overrides the built-in) | |
| A-30 | subagents.isolation | 219 | A subagent starts from its own prompt, not the conversation | fact | agents/*.md (7 files) | follows | A subagent starts from its own system prompt and environment details, not the parent's conversation. | |
| A-31 | subagents.isolation | 221 | Verify in a fresh context with a named agent | advice | agents/{code-reviewer,security-auditor,task-reviewer}.md (3 files) | follows | (use a named agent, not a fork, which inherits that reasoning) | |
| A-32 | subagents.isolation | 223 | Do not delegate where the summary loses needed detail | advice | agents/debugger.md (1 file) | follows | tasks where the summary loses details the main agent must then re-derive | |
| A-33 | subagents.isolation | 223 | Instruct reviewers to flag only correctness and requirement gaps | advice | agents/code-reviewer.md:51 | gap | instruct reviewers to flag only correctness and requirement gaps | #### Minor (Nice to Have) — style, optimization, docs polish |
| A-34 | subagents.isolation | 223 | Instruct reviewers to flag only correctness and requirement gaps | advice | agents/task-reviewer.md:102 | gap | instruct reviewers to flag only correctness and requirement gaps | **Code quality:** clean separation of concerns; proper error handling; DRY |
| A-35 | subagents.isolation | 223 | Instruct reviewers to flag only correctness and requirement gaps | advice | agents/security-auditor.md (1 file) | follows | instruct reviewers to flag only correctness and requirement gaps | |
| A-36 | commands.overview | 161 | A command's filename is its name; it takes no name field | fact | commands/*.md (3 files) | follows | a command's filename is its name | |
| A-37 | commands.overview | 161 | A skill wins a command-name collision | fact | commands/*.md (3 files) | follows | on a name collision the skill wins | |
| A-38 | commands.overview | 163 | The docs recommend a skill for new work | advice | commands/deferred.md:2 | deviation candidate | the docs now recommend a skill for new work | Triage specs/deferred_items.md — group unticked items, then sort each into retire |
| A-39 | commands.overview | 163 | The docs recommend a skill for new work | advice | commands/fix-issue.md:2 | deviation candidate | the docs now recommend a skill for new work | Fix a GitHub issue end-to-end — bugs only; feature-shaped issues route to brainstorming. |
| A-40 | commands.overview | 163 | The docs recommend a skill for new work | advice | commands/license-audit.md:2 | deviation candidate | the docs now recommend a skill for new work | Audit the current repo's licensing and attribution |
| A-41 | commands.overview | 163 | Set disable-model-invocation: true on side-effecting commands | advice | commands/*.md (3 files) | follows | set `disable-model-invocation: true` on anything side-effecting | |
| A-42 | skills.frontmatter | 81 | Descriptions stay within the 1,536-character listing cap | fact | commands/*.md (3 files, 120 to 236 chars) | follows | capped at 1,536 chars in the listing (`skillListingMaxDescChars`) | |
| A-43 | skills.frontmatter | 91 | disable-model-invocation: true makes a command manual-only and unlisted | fact | commands/*.md (3 files) | follows | `true` = only manual `/name` invocation, and the skill leaves the listing entirely | |
| A-44 | skills.frontmatter | 87 | A Haiku model is ignored in auto mode | fact | commands/*.md (3 files, none sets model or effort) | follows | a `model` that auto mode doesn't support (Haiku) is ignored and the session model runs | |
| A-45 | skills.frontmatter | 83 | argument-hint gives an autocomplete hint | fact | none (no command sets argument-hint) | n/a | Autocomplete hint, e.g. `[issue-number]` | |
| A-46 | skills.frontmatter | 96 | Misspelled frontmatter fields are ignored silently | fact | commands/*.md (3 files) | follows | Unknown fields are ignored silently, so a misspelled field fails without an error | |
| A-47 | skills.arguments | 133 | $ARGUMENTS holds everything typed after /name | fact | none (no command uses a substitution token) | n/a | Everything typed after `/name` | |
| A-48 | skills.arguments | 139 | Escape a $ before a digit or ARGUMENTS | fact | commands/*.md (3 files) | follows | Escapes a `$` before a digit, `ARGUMENTS`, or a declared argument name | |
| A-49 | skills.arguments | 141 | Inline shell preprocessing runs at render time | fact | commands/*.md (3 files) | follows | runs a shell command **once, at render time, before Claude sees the content** | |
| A-50 | skills.description | 103 | Write descriptions in third person: what, then when | advice | none (manual-only commands are never routed by description) | n/a | Write it in **third person**, stating both *what* the skill does and *when* to use it. | |
| A-51 | skills.description | 105 | Front-load the primary use case within the cap | advice | commands/*.md (3 files) | follows | Front-load the primary use case; the cap is 1,536 characters including `when_to_use`. | |

#### Row notes

- **A-04** (deviation candidate, R5.7-adjacent).
  - Reason: the comment at agents/explore.md:2-8 says Claude Code resolves agent types by the frontmatter name alone, case-sensitively, and only `Explore` shadows the built-in. It was probed on 2.1.219 on 2026-07-25.
  - Further evidence: build/check_frontmatter.py:134-137 and README.md:114.
  - Revisit trigger: explore.md:7-8 says to re-probe after binary updates.
  - The guide's own line 214 also says `Explore` with a capital E (see A-52).
- **A-12 to A-15** (R5.7 reviewer-agents candidate, confirmed as deviation candidates).
  - Reason: specs/completed/readonly-agent-guard.md:24-26 calls Bash "the `Bash` tool the agents legitimately need". The bodies need git and test commands: code-reviewer.md:17-20, security-auditor.md:17-18, task-reviewer.md:32 and :78, explore.md:22-23.
  - The guard covers all five (hooks/readonly-agent-guard.py:29-35).
  - Buckets: code-reviewer, security-auditor and task-reviewer are reviewers/auditors. Explore is the researcher bucket (line 199), whose base is the reviewer set. It adds Bash and no web tools.
  - test-runner fits none of the guide's three buckets. Bash is its function (test-runner.md:8-11), so it gets A-17.
- **A-18**: debugger omits Write. Reason: specs/completed/agents-and-commands-expansion.md:107-109 ("Edit is included because fixing requires modifying code (per the official archetype)"). debugger.md:20-21 tells it to write a failing test when none exists, which needs a new file, so Bash is its only route. That is not recorded as a reason.
- **A-20**: no recorded reason for holding Bash.
  - agents-and-commands-expansion.md:125-127 and specs/plans/completed/17-agents-and-commands-expansion.md:478 list the tool set without one.
  - readonly-agent-guard.md:53-55 and :359-362 record that docs-writer is deliberately unguarded and its "never commit" clause stays prose.
  - L-04 covers the Grep/Glob-with-Bash fact for this file. This row is a different rule.
- **A-26**: the reason is the file's own comment at task-reviewer.md:5, which says the floor is Sonnet and the controller escalates to opus per dispatch. specs/completed/task-reviewer-agent-and-deferred-command.md:62 ("No `model` field") predates the pin. The escalation relies on the per-spawn override in A-08.
- **A-33 and A-34**: no recorded reason.
  - The specs record only the Critical/Important/Minor tiers (agents-and-commands-expansion.md:53, task-reviewer-agent-and-deferred-command.md:56).
  - Partial mitigations: code-reviewer.md:40 ("not everything is Critical") and task-reviewer.md:120 (polish suggestions are Minor).
  - Both files explicitly invite non-correctness findings: code-reviewer.md:51, and the task-reviewer.md:100-104 Part 2 on structure and DRY.
- **A-35**: judged on its own merits. security-auditor.md:36-38 ("Flag real exposures, not theoretical ones") bounds the scope. The Minor tier at :46 ("hardening opportunities") is the soft spot.
- **A-38 to A-40** (R5.7 commands candidate, confirmed as deviation candidates).
  - Reason: the Gemini TOML adapters are generated from commands/*.md (build/sync_runtime_assets.py:25, :116-123, :131-132; README.md:121-124; CLAUDE.md:39).
  - `/deferred` is also a hard dependency in install.py:41, :44, :50 and :60.
  - Context only: agents-and-commands-expansion.md:31-34 chose a command file for cheapness, but guide line 163 says a lone SKILL.md costs the same.
  - Weak point: skills already install to Codex and Gemini under `~/.agents/skills` (CLAUDE.md:22), so the adapter reason covers only the TOML adapters.
- **A-45 and A-47** (fix-issue).
  - fix-issue.md:6 and :9 take the argument by prose ("given as the argument", `gh issue view <arg>`). The usage hint sits in the description at :2.
  - The Gemini adapter appends `{{args}}` (sync_runtime_assets.py:118; README.md:121-122).
  - The guide states no rule for a body without a placeholder, so I give no status other than n/a. The runtime behaviour is not verifiable from the guide.
  - deferred.md and license-audit.md take no argument.
- **A-50**: all three commands set disable-model-invocation, so they are out of the listing (guide lines 45, 91, 163; build/check_frontmatter.py:164-167). Their descriptions are imperative ("Triage…", "Fix…", "Audit…"). Line 104 (trigger phrases) and line 106 (under-trigger) are n/a for the same reason.
- **A-27**: today is 2026-10-04, so the window opens in 11 days. No retirement plan is recorded (grep of specs/deferred_items.md and specs/claude-code-*.md). It is `follows` because no rule is broken. See A-53.
- **A-28**: test-runner.md:23-24 promises untruncated tracebacks, and Haiku's window is 200K. See D on lean.expensive-ops.
- **A-11**: no agent sets omitClaudeMd. Line 219 says custom agents load the CLAUDE.md hierarchy and a git-status snapshot, and the built-in Explore skips both. The guide does not say whether the custom `Explore` override still skips them. explore.md sets no omitClaudeMd. This is unverified and could be probed.
- **A-09**: `xhigh` is not named by the guide, which gives only the endpoints. See C8.
- **A-10**: debugger.md:29-30 and docs-writer.md:38 write in the caller's checkout by design.
- **Quote check**: every quote was re-checked as a single-line substring at its stated line, with a read-only Python match. Every quote is 25 words or fewer.

### Hooks, rules and settings (H)

All repo paths are relative to the worktree. G = specs/guides/claude-code-customization-guide.md. Row IDs L-09 to L-11 (README:56, :60, :64) are not repeated. I grouped n/a rules that share a reason into one row each. Quote cells are shown in plain quotes, and section B holds the exact text. Every quote was re-grepped as a single-line match, and all hit the cited line. In cells, `\|` stands for a literal pipe.

| ID | section | guide line | rule | fact/advice | artifact file:line | status | guide quote | artifact quote |
|---|---|---|---|---|---|---|---|---|
| H-01 | hooks.overview | 274 | Hooks are the deterministic layer; use them over prose | advice | hooks/*.sh, hooks/*.py (5 files) | follows | "They are the deterministic layer" | |
| H-02 | hooks.events | 284 | PostToolUse cannot block; the tool already ran | fact | hooks/ruff-fix.sh (1 file) | follows | "the tool already ran; stderr goes to Claude" | |
| H-03 | hooks.events | 288 | Stop fires at turn end; exit 2 forces continuation | fact | hooks/ruff-check.sh (1 file) | follows | "When Claude finishes a turn" | |
| H-04 | hooks.events | 283 | PreToolUse exit 2 blocks; JSON can also deny | fact | hooks/uv-guard.sh, hooks/readonly-agent-guard.py (2 files) | follows | "blocks the call; JSON can also allow/deny/ask/defer or rewrite input" | |
| H-05 | hooks.events | 285-287 | UserPromptSubmit, PostToolUseFailure, PermissionRequest behaviours | fact | none of the artifacts uses these events | n/a | "On prompt submit, before processing" | |
| H-06 | hooks.events | 289-294 | Subagent, SessionStart, compaction, config, file and SessionEnd events | fact | none of the artifacts uses these events | n/a | "Session terminates" | |
| H-07 | hooks.events | 279 | Event count and newest events | fact | none of the artifacts depends on it | n/a | "Current builds document 33 events" | |
| H-08 | hooks.exit-codes | 299 | Unparseable JSON-looking stdout is a hook error | fact | hooks/readonly-agent-guard.py:936 (1 file) | follows | "JSON-looking output that fails to parse is a hook error (2.1.248+)" | |
| H-09 | hooks.exit-codes | 300 | Exit 2 blocks blockable events; stderr reaches Claude | fact | hooks/uv-guard.sh, hooks/ruff-check.sh (2 files) | follows | "block, on blockable events" | |
| H-10 | hooks.exit-codes | 303 | PreToolUse decision goes in hookSpecificOutput.permissionDecision | fact | hooks/readonly-agent-guard.py:895-899 (1 file) | follows | "`permissionDecision` / `updatedInput` on `PreToolUse`" | |
| H-11 | hooks.exit-codes | 303 | A Stop hook checks stop_hook_active | advice | hooks/ruff-check.sh:13 (1 file) | follows | "check it (or the transcript) to avoid blocking on a condition that can never resolve" | |
| H-12 | hooks.exit-codes | 303 | Injected text is capped at 10,000 characters | fact | none injects through additionalContext, systemMessage or stdout | n/a | "is capped at 10,000 characters per hook" | |
| H-13 | hooks.handlers | 310 | Command handlers default to a 600s timeout | fact | hooks/README.md (1 file; four command entries, none sets timeout) | follows | "600s (lower for some events)" | |
| H-14 | hooks.handlers | 312 | prompt, agent, http and mcp_tool handler types | fact | every entry is type command | n/a | "A multi-turn subagent verifier (experimental)" | |
| H-15 | hooks.configuration | 318 | Hooks live in any settings level, merged | fact | hooks/README.md:49-68, :117-122 (1 file); .claude/settings.json holds no hooks, by README:18-24 | follows | "Hooks live in any settings level (user / project / local / managed — entries merge across levels)" | |
| H-16 | hooks.configuration | 318 | matcher takes a plain name or an A\|B list | fact | hooks/README.md:55, :59, :120 (1 file) | follows | "plain names or `A\|B` lists match exactly" | |
| H-17 | hooks.configuration | 318 | if, timeout, statusMessage, once, disableAllHooks fields | fact | no artifact sets them | n/a | "honored only on tool events — elsewhere a hook with `if` never runs" | |
| H-18 | hooks.patterns | 331 | Hook command double-quotes the variable locating its script | advice | hooks/README.md:121 (guard install; $HOME unquoted). R5.7 candidate confirmed. Extends the rule by analogy: the guide's pattern quotes only $CLAUDE_PROJECT_DIR. README:127-128 explains why $CLAUDE_PROJECT_DIR is not used, not why $HOME is unquoted | gap | "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/format.sh" | "command": "$HOME/.claude/hooks/readonly-agent-guard.py" |
| H-19 | hooks.patterns | 323 | Formatter: PostToolUse on Write\|Edit, always exit 0 | advice | hooks/ruff-fix.sh (1 file) | follows | "`PostToolUse` on `Write\|Edit`" | |
| H-20 | hooks.patterns | 350 | Blocker: PreToolUse on Bash, stderr message, exit 2 | advice | hooks/uv-guard.sh (1 file) | follows | "the stderr text steers Claude to the right alternative" | |
| H-21 | hooks.patterns | 362 | A Stop gate decides what happens on the continuation | advice | hooks/ruff-check.sh:13 (1 file; takes the one-attempt branch) | follows | "Decide what happens on the continuation" | |
| H-22 | hooks.patterns | 364 | SessionStart hook injects dynamic context | advice | no SessionStart hook exists | n/a | "dynamic context without editing CLAUDE.md" | |
| H-23 | hooks.pitfalls | 369 | PostToolUse fixes only; pair it with a Stop gate | advice | hooks/ruff-fix.sh, hooks/ruff-check.sh, hooks/README.md:87-89 (3 files) | follows | "Pair it with a `Stop` gate for rules that must hold at turn end" | |
| H-24 | hooks.pitfalls | 370 | Blocking takes exit 2 or a JSON deny | fact | hooks/README.md:90. The bullet is scoped to the three templates, but the claim is general, and README:93-122 documents a JSON-deny hook | gap | "(stderr carries the message) or a JSON deny/block decision" | "only exit 2 blocks and feeds stderr to Claude; exit 1 just" |
| H-25 | hooks.pitfalls | 370 | Exit 1 is non-blocking; the action proceeds | fact | hooks/uv-guard.sh, hooks/ruff-check.sh, hooks/readonly-agent-guard.py (3 files) | follows | "exit 1 is a non-blocking error — the action proceeds" | |
| H-26 | hooks.pitfalls | 371 | Gates fail open; trigger each gate once | advice | hooks/probe-readonly-guard.sh, hooks/README.md:158-173 (guard; 2 files) | follows | "Trigger each gate once to prove it blocks." | |
| H-27 | hooks.pitfalls | 371 | Gates fail open; trigger each gate once | advice | hooks/README.md:39-78 (the three-template install path ends at the settings merge, with no verify step; this is an absence, so the quote is the last install step) | gap | "Trigger each gate once to prove it blocks." | "`.claude/settings.json` (merge if it exists):" |
| H-28 | hooks.pitfalls | 372 | if is best-effort; hard allow/deny belongs in permission rules | advice | no artifact uses `if` | n/a | "`if` filtering is best-effort" | |
| H-29 | hooks.pitfalls | 373 | @-referenced files bypass PreToolUse hooks | fact | the guard covers Bash only | n/a | "no `PreToolUse` hook sees them" | |
| H-30 | hooks.pitfalls | 374 | Hooks run inline; keep them fast | advice | hooks/*.sh, hooks/*.py (5 files; the guard exits at the agent check, README:124-127) | follows | "keep them fast, or the session drags on every event" | |
| H-31 | hooks.pitfalls | 375 | Many events and rules go through one dispatcher | advice | one script per wired entry | n/a | "route through a single dispatcher script instead of N config entries" | |
| H-32 | hooks.pitfalls | 376 | Python hook logic uses single-file inline-deps scripts via uv | advice | hooks/readonly-agent-guard.py:15. R5.7 candidate confirmed as a deviation: stdlib only, no inline-dependency block, plain python3 shebang | deviation candidate (specs/completed/readonly-agent-guard.md:65; hooks/README.md:132-139) | "single-file scripts with inline dependency declarations (`uv run`) keep hook deps out of your project environment" | "Python), so keep this file 3.9-compatible: stdlib only, no `match`, and" |
| H-33 | mechanisms.overview | 40 | Deterministic, machine-checkable rules go in a hook | advice | hooks/uv-guard.sh, hooks/ruff-fix.sh, hooks/ruff-check.sh (3 files) | follows | "A hook (plus linter config)" | |
| H-34 | mechanisms.overview | 41 | Hard access boundaries go in permission rules | advice | hooks/readonly-agent-guard.py:6 (a hard Bash boundary enforced by a hook) | deviation candidate (specs/completed/readonly-agent-guard.md:44-47, since the PreToolUse matcher keys on tool name not agent type; hooks/README.md:177-179) | "Permission rules in `settings.json`" | "frontmatter already denies Write/Edit; nothing enforced the Bash half. This hook" |
| H-35 | mechanisms.overview | 42, 44-46 | CLAUDE.md, skill, manual-skill and subagent placement rows | advice | none of the artifacts is one of these | n/a | "Loads on demand; can bundle scripts and references" | |
| H-36 | mechanisms.overview | 43 | File-specific guidance goes in a rule file with paths | advice | rules/*.md, .claude/rules/*.md (2 files) | follows | "A rule file with `paths`" | |
| H-37 | mechanisms.overview | 48 | Move checkable prose into a hook | advice | hooks/README.md:15-16 (1 file) | follows | "moving it from prose into a hook (or linter config) frees tokens" | |
| H-38 | rules.rules-files | 248 | A paths rule loads lazily, on a matching read or edit | fact | rules/clean-code-python.md:6-8 (the .claude/rules/ link shares it). Same finding as D12 at specs/audit-3-10-26.md:863 | gap | "loaded lazily, only when Claude reads or edits matching files" | "# Python conventions (always-on)" |
| H-39 | rules.rules-files | 248 | A rule that must persist drops paths | advice | rules/clean-code-python.md:2. Whether it must persist is the owner's call (audit D12) | deviation candidate (specs/plans/completed/15-clean-code-family.md:7-9, a deliberate token-cheap path-scoped rule) | "a rule that must persist should drop `paths` or move to the root CLAUDE.md" | "paths:" |
| H-40 | rules.rules-files | 250 | An outside-project rule symlink is an external import | fact | .claude/rules/clean-code-python.md (1 file; the link resolves inside the repo, and README.md:276 installs by cp) | follows | "A symlinked rule whose target lies outside the project counts as an external import" | |
| H-41 | rules.rules-files | 250 | Keep cross-project rules in ~/.claude/rules/ | advice | rules/clean-code-python.md:26 (the last bullet names work repos; it ships per-repo, not user-level) | deviation candidate (specs/deferred_items.md:564-575, a project-level-only decision retired 2026-09-08) | "Keep cross-project rules in `~/.claude/rules/` instead." | "(agent-skills: 3.13; work repos: 3.12)." |
| H-42 | rules.rules-files | 247 | A rule without paths loads at session start | fact | every repo rule sets paths | n/a | "loaded at session start, alongside CLAUDE.md" | |
| H-43 | rules.hierarchy | 238 | CLAUDE.md files concatenate, never override | fact | governs CLAUDE.md files only | n/a | "concatenated, never overridden" | |
| H-44 | rules.hierarchy | 240 | @path imports inline a file, four hops at most | fact | no rules file imports | n/a | "inlines another file at load time" | |
| H-45 | rules.settings | 260 | Precedence: managed, CLI, local, project, user | fact | descriptive; .claude/settings.json repeats the user file's three keys with equal values, so no conflict | n/a | "resolves highest-to-lowest" | |
| H-46 | rules.settings | 262 | Permissions merge; a deny anywhere wins | fact | .claude/settings.json has no permissions | n/a | "a deny anywhere wins; no other level can re-allow it" | |
| H-47 | rules.settings | 264 | The legacy :* form is equivalent only at pattern end | fact | hooks/README.md:74 (1 file; all three patterns end in :*) | follows | "the older `Bash(uv run:*)` form is equivalent, but only at the end of a pattern" | |
| H-48 | rules.settings | 269 | Auto mode sets aside broad runner allow rules | fact | hooks/README.md:70-74 (says the allowlist spares the uv forms a prompt; true only in manual mode) | gap | "in auto mode — the default starting mode since 2.1.283 — broad rules such as package-manager run commands are set aside" | "Optionally pair with a permission allowlist in the same file so the `uv` forms" |
| H-49 | rules.settings | 269 | A pip-blocking hook holds in every permission mode | advice | hooks/uv-guard.sh (1 file) | follows | "The hook that makes `pip install` impossible holds in every mode." | |
| H-50 | rules.settings | 265-267 | Word boundaries, compound splitting, gitignore-style file rules | fact | README:74 patterns exercise none of these | n/a | "File rules use gitignore-style paths" | |
| H-51 | lean.model-routing | 422 | enforceAvailableModels is a managed-settings key | fact | .claude/settings.json:4. R5.7 candidate confirmed as a gap. No spec decision explains the project-level placement. specs/completed/delegation-frontmatter-rollout.md:20 records only that it shipped | gap | "`enforceAvailableModels`, in managed settings, extends it to the Default option" | "\"enforceAvailableModels\": true" |
| H-52 | lean.model-routing | 422 | availableModels restricts every place a model can be named | fact | .claude/settings.json:3 (1 file) | follows | "`availableModels` restricts every place a model can be named" | |
| H-53 | lean.model-routing | 422 | Model precedence ends at the model setting | fact | .claude/settings.json:2 (1 file) | follows | "model precedence runs `/model` → `--model` → `ANTHROPIC_MODEL` → the `model` setting" | |
| H-54 | lean.model-routing | 416-420 | opusplan, advisor, Haiku subagents, effort-first, fast mode | advice | the project settings sets none of them | n/a | "Raise `/effort` before escalating the model." | |
| H-55 | lean.model-routing | 422 | Alias-target and subagent-fallback environment variables | fact | not set in project settings | n/a | "`CLAUDE_CODE_SUBAGENT_MODEL` sets the subagent fallback" | |
| H-56 | lean.model-routing | 424-433 | List prices and cache-read table | fact | no artifact depends on it | n/a | "List prices (October 2026, per MTok)" | |

Notes on A.
- I wrote no row for the section's TODO(owner) bullet, so nothing is filed against `"model": "opus"` at .claude/settings.json:2.
- The guide's Stop-gate pattern lets a script choose between one attempt and a re-check. ruff-check.sh takes the one-attempt branch, and README:34 does not state that consequence.
- H-18's gap against README:121 sits beside L-09 to L-11, which cover README:56, :60 and :64. The lint keys on $CLAUDE_PROJECT_DIR only.

### CLAUDE.md and installer (C)

| ID | section | guide line | rule | fact/advice | artifact | status | guide quote | artifact quote |
|---|---|---|---|---|---|---|---|---|
| C-01 | rules.claude-md | 231 | Include build/test commands, style deltas, etiquette, quirks, gotchas | advice | CLAUDE.md, build/CLAUDE.md (2 files) | follows | Include: non-guessable build/test commands, style deltas from language defaults, repo etiquette, environment quirks, genuine gotchas. | |
| C-02 | rules.claude-md | 231 | Exclude fast-changing details | advice | CLAUDE.md:87 | gap. 22 comment lines in the Commands block carry pass and test counts, kept by hand. specs/claude-code-guide-conformance.md:537-538 records how the count is updated, not a reason to keep it. The 83 + 62 + 37 breakdown omits build/test_check_conformance.py (58 test functions), so the 182 total is already stale on this branch. | Exclude: anything readable from the code, standard conventions, API documentation (link instead), fast-changing details, self-evident practice. | # Full build-directory tests — 182 tests |
| C-03 | rules.claude-md | 231 | Exclude anything readable from the code | advice | CLAUDE.md:182 | gap. build/check_snippets.py:9-10 states the same norun and noparse semantics; its :26 defers only the invocations to CLAUDE.md, not the marker rules. | Exclude: anything readable from the code, standard conventions, API documentation (link instead), fast-changing details, self-evident practice. | # Two fence markers opt a block out, each REQUIRING a reason (tests pin this): |
| C-04 | rules.claude-md | 231 | Exclude fast-changing details | advice | CLAUDE.md:72 | gap. Stale-prone description: 3 of build/'s 20 .py files concern citations (extract_structure.py, verify_citations.py, test_verify_citations.py); the rest are lints, gates and tests for other work. | Exclude: anything readable from the code, standard conventions, API documentation (link instead), fast-changing details, self-evident practice. | Most of `build/` is the citation-verification pipeline for |
| C-05 | rules.claude-md | 231 | Exclude fast-changing details | advice | build/CLAUDE.md:3 | gap. Same claim as C-04; the line opens build/CLAUDE.md. | Exclude: anything readable from the code, standard conventions, API documentation (link instead), fast-changing details, self-evident practice. | Most files here form a citation-verification pipeline, not a project build. |
| C-06 | rules.claude-md | 233 | Each CLAUDE.md stays under 200 lines | advice | build/CLAUDE.md (1 file, 17 lines) | follows | is under 200 lines per file | |
| C-07 | rules.hierarchy | 238 | CLAUDE.md files concatenate, broad to specific, never override | fact | CLAUDE.md, build/CLAUDE.md (2 files) | follows | Files load broad → specific and are **concatenated, never overridden** | |
| C-08 | rules.hierarchy | 238 | Must-persist guidance lives in an always-loaded file | advice | build/CLAUDE.md (1 file) | follows (both its must-persist rules, :10 and :15, repeat in CLAUDE.md:75 and :28) | Lazy content lives in message history, so compaction summarizes it away; anything that must persist belongs in an always-loaded file. | |
| C-09 | rules.hierarchy | 238 | AGENTS.md is read only when no CLAUDE.md exists | fact | CLAUDE.md, AGENTS.md (2 files) | follows (CLAUDE.md exists, so Claude Code never reads AGENTS.md; AGENTS.md:4 sends Codex to CLAUDE.md by prose) | `AGENTS.md` is read natively since 2.1.277, but only as a fallback when no CLAUDE.md exists | |
| C-10 | rules.hierarchy | 240 | An @path inlines a file; backticks escape it | fact | CLAUDE.md, build/CLAUDE.md (2 files) | follows (the only @ token, CLAUDE.md:122, lies inside the bash fence open from :82 to :238) | escape with backticks to mention a path without importing it | |
| C-11 | rules.hierarchy | 240 | Imported files still load at launch | fact | none | n/a (no CLAUDE.md imports a file; GEMINI.md:3 `@./CLAUDE.md` is Gemini's import) | imported files load at launch too | |
| C-12 | rules.hierarchy | 238 | CLAUDE.local.md is personal; gitignore it | advice | none | n/a (no CLAUDE.local.md exists; .gitignore is in no kind, see D) | `CLAUDE.local.md` (personal; gitignore it yourself) | |
| C-13 | rules.hierarchy | 238 | Ancestor-directory CLAUDE.md files load at launch | fact | none | n/a (no artifact says otherwise; the layout effect is in D) | CLAUDE.md files in ancestor directories of the working directory load at launch too | |
| C-14 | context.overview | 22 | Subdirectory CLAUDE.md loads on demand, then stays resident | fact | build/CLAUDE.md (1 file) | follows | Near-free until used — then resident in history until compaction truncates or summarizes them | |
| C-15 | lean.session-hygiene | 392 | Compaction summarizes nested CLAUDE.md files away | fact | build/CLAUDE.md (1 file) | follows (see C-08) | path-scoped rules and nested CLAUDE.md files are summarized away | |
| C-16 | lean.session-hygiene | 391 | Set a standing Compact instructions section, or guide each /compact | advice | none | n/a (either/or option; no file bears on it) | or set a standing `# Compact instructions` section in CLAUDE.md | |
| C-17 | lean.session-hygiene | 389 | /clear, /rewind, /compact timing and plan mode | advice | none | n/a (session practice; no file bears on it) | stale history is pure input-token overhead | |
| C-18 | skills.locations | 68 | Personal skills live in ~/.claude/skills/name/ | fact | CLAUDE.md, install.py (2 files) | follows (install.py:140; CLAUDE.md:22) | All your projects on this machine (not cloud, routine, or Cowork sessions) | |
| C-19 | skills.locations | 73 | Symlinks are followed, so a symlinked skills repo edits live | fact | CLAUDE.md, install.py (2 files) | follows (CLAUDE.md:22-24; install.py:363 links each skill directory; scope note in D) | Symlinks are followed — keeping a skills repo elsewhere and symlinking each skill into | |
| C-20 | skills.locations | 73 | A same-name skill shadows a lower-precedence one | fact | none | n/a (the repo holds no .claude/skills/; install.py writes only the personal root) | a same-name skill shadows the lower-precedence one | |
| C-21 | skills.locations | 73 | claude.ai skills sync into ~/.claude/skills/synced/ | fact | install.py (1 file) | follows (no skills/ directory is named synced) | (`~/.claude/skills/synced/`; `syncClaudeAiSkills: false` opts out) | |
| C-22 | subagents.overview | 168 | Personal agents live in ~/.claude/agents/ | fact | CLAUDE.md, install.py (2 files) | follows (install.py:141; CLAUDE.md:14-15) | Subagent definitions are Markdown files in `~/.claude/agents/` (personal) or `.claude/agents/` (project) | |
| C-23 | subagents.overview | 168 | A project agent outranks a personal agent of the same name | fact | none | n/a (no .claude/agents/ exists; install.py writes only the personal root) | here project beats personal, the reverse of skills | |
| C-24 | commands.overview | 163 | Command files still work | fact | install.py (1 file) | follows (install.py:142) | Command files still work | |
| C-25 | commands.overview | 161 | On a name collision the skill wins | fact | install.py (1 file) | follows (3 command stems and 35 skill directories share no name) | on a name collision the skill wins | |
| C-26 | commands.overview | 161 | Built-in commands are CLI code; a same-name skill replaces one | fact | install.py (1 file) | follows (no installed skill or command is named help, model or compact) | Most built-ins, like `/help`, `/model`, and `/compact`, are coded into the CLI rather than files | |
| C-27 | commands.overview | 161 | Commands are skills and take skill frontmatter | fact | none | n/a (frontmatter bears on commands/*.md, another seat; install.py copies files unread) | Commands have been **merged into skills** | |
| C-28 | commands.overview | 163 | Docs recommend a skill for new work | advice | none | n/a (bears on commands/*.md, another seat; install.py only places files) | the docs now recommend a skill for new work | |
| C-29 | commands.overview | 163 | Side-effecting commands set disable-model-invocation | advice | none | n/a (bears on commands/*.md, another seat) | set `disable-model-invocation: true` on anything side-effecting | |
| C-30 | mechanisms.overview | 40 | Machine-checkable rules belong in a hook or linter config | advice | CLAUDE.md:75, build/CLAUDE.md:10 (the .scratch lines) | follows (the never-commit rule is enforced by .gitignore:14) | A hook (plus linter config) | |
| C-31 | mechanisms.overview | 48 | Checkable rules move from prose into a hook | advice | CLAUDE.md:166 | gap. R5.7 candidate confirmed. The same prose recurs at :170, :186 and :28. The programs exist (check_frontmatter.py, check_provenance.py, check_snippets.py Tier 1, the declared_dependencies test, sync_runtime_assets.py --check) but no hook runs them: .claude/settings.json sets none, and the repo has no CI (specs/agent-skills-portability.md:401). Spec R4.1 and R4.3 (specs/claude-code-guide-conformance.md:394-396) justify the prose reaching Codex and Gemini, not the absence of a Claude Code hook; hooks/README.md:18-20 leaves unwired only the ruff and uv templates. | Whenever a rule is checkable by a program, moving it from prose into a hook (or linter config) frees tokens | # Frontmatter + provenance lints (run before committing skill changes) |
| C-32 | mechanisms.overview | 48 | Checkable rules move from prose into a hook | advice | build/CLAUDE.md:15 | gap. CLAUDE.md:28 states the same rule. sync_runtime_assets.py --check (CLAUDE.md:34) finds hand edits only when someone runs it; the guide's :41 row routes access boundaries to permission rules, and .claude/settings.json sets none. Spec decision 1 (specs/claude-code-guide-conformance.md:79-81) and R4.3 explain why the prose also serves Codex and Gemini, not why Claude Code has no guard. | Whenever a rule is checkable by a program, moving it from prose into a hook (or linter config) frees tokens | never edit `../runtimes/` by hand. |
| C-33 | mechanisms.overview | 43 | Guidance for certain files belongs in a path-scoped rule | advice | CLAUDE.md:67 | deviation candidate. rules/clean-code-python.md (`paths: **/*.py`, linked at .claude/rules/) already carries these rules for Claude Code, but CLAUDE.md is the one file Codex and Gemini read (CLAUDE.md:3-4; spec R4.3 at specs/claude-code-guide-conformance.md:394-396). hooks/README.md:18-20 records that no ruff config exists here to enforce quote style mechanically. | Relevant only when touching certain files | Polars over pandas; single quotes over double; |
| C-34 | mechanisms.overview | 44 | Sometimes-relevant knowledge belongs in a skill | advice | CLAUDE.md:99 | deviation candidate. The Commands block (CLAUDE.md:78-238, 161 lines) is per-subtree commands, relevant only when touching that subtree; moving it off CLAUDE.md would hide it from Codex and Gemini (spec decision 1 at :79-81, R4.3 at :394-396). Size itself is L-01. | Sometimes-relevant knowledge or a multi-step workflow | cd skills/recommend-probabilistic-model/scripts && uv run --python 3.13 --with pytest --with numpy --with polars python -m pytest -q |
| C-35 | rules.auto-memory | 255 | MEMORY.md loads each session; keep it an index | fact | none | n/a (the memory directory is outside the repo; no repo file mentions MEMORY.md or auto memory) | Claude Code keeps per-project memory in `~/.claude/projects/<project>/memory/`. | |
| C-36 | lean.measure | 384 | Measure with /context, /usage, /doctor before optimizing | advice | none | n/a (no repo file prescribes a measurement practice) | Establish a baseline before optimizing anything. | |
| C-37 | lean.caching | 406 | Pick model and server set at session start | advice | none | n/a (session practice; the :404 edit-timing fact is in D) | pick your model and server set at session start and leave them alone | |
| C-38 | lean.mcp | 440 | Audit /mcp and disable unused servers | advice | none | n/a (no .mcp.json; no mcpServers in agents, commands, hooks, rules, skills, runtimes, .claude, README.md, CLAUDE.md or install.py) | Audit `/mcp` and disable servers | |
| C-39 | reading.overview | 477 | Pointers to the official docs | fact | none | n/a | append `.md` to any page for raw markdown | |

Notes on the table:
- CLAUDE.md's length against rules.claude-md :233, and its keep-lean reading under context.overview (:17, :33), are L-01. No row added for either.
- The per-line litmus test (:233) is applied through C-02 to C-05. No separate row.
- GEMINI.md reaches CLAUDE.md by the `@./CLAUDE.md` import and AGENTS.md by a prose instruction. build/test_runtime_support.py:88-89 pins both.
- R5.7 "run before committing lints": confirmed as C-31 and C-32. R5.7 "CLAUDE.md length": L-01.

## 4. R5.7 candidates

| Candidate (spec R5.7) | Verdict | Rows |
|---|---|---|
| CLAUDE.md's length against `rules.claude-md` (225 when the spec was written) | Confirmed: 238 lines on this branch | L-01 |
| `enforceAvailableModels` in project settings against `lean.model-routing` | Confirmed as a gap. The guide line itself is ambiguous (guide note H-57) | H-51; outside, O-13 |
| `writing-skills`' 696-line body against `skills.overview` | Confirmed as a gap | S-02 |
| `writing-skills` line 222 (every description stays resident) against `skills.listing-budget` | Confirmed as a gap. The guide's line 122 says the same as line 222 (guide note S-108) | S-58 |
| `writing-skills` line 304's `@`-loading claim against `rules.hierarchy` | Rejected as a contradiction, recorded as an unsupported claim. The guide documents `@` imports only inside CLAUDE.md, and the mechanism it states agrees with the skill. The SKILL.md scope and the "200k+" figure are not in the guide. The seat keeps the row's status as gap, and says to reject the row if the owner reserves "gap" for contradictions (note N3) | S-107 |
| `writing-skills` gives no critical-rules-first advice against `skills.progressive-disclosure` | Confirmed as a gap. Rows S-68 to S-70 extend it to subagent-driven-development and bayesian-workflow | S-67 |
| brainstorming's "every project" against `lean.ceremony` | Confirmed as a deviation candidate (the skill's Anti-Pattern section) | S-96 |
| `commands/` kept as command files against `commands.overview` | Confirmed as deviation candidates (the Gemini TOML adapters are generated from them) | A-38, A-39, A-40 |
| Reviewer agents hold Bash against `subagents.tools`' reviewer set | Confirmed as deviation candidates (the read-only guard spec records the need for Bash) | A-12, A-13, A-14, A-15 |
| CLAUDE.md's "run before committing" lints as prose against `mechanisms.overview` | Confirmed as gaps | C-31, C-32 |
| The read-only guard's stdlib-only design against `hooks.pitfalls`' advice on `uv` inline deps | Confirmed as a deviation candidate (stdlib only by design, for the 3.9 floor) | H-32 |
| `hooks/README.md:121` leaves `$HOME` unquoted | Confirmed as a gap. `hook-dir-quoted` covers only `$CLAUDE_PROJECT_DIR` | H-18; outside, O-16 |
| Outside: the AWS rule has no `paths` | Confirmed as a gap (report-only) | O-18 |
| Outside: `settings.local.json` allows `Bash(pip install *)` | Confirmed as a gap (report-only) | O-22 |

**Side-effecting yet model-invocable skills (R2.7's `side-effecting-skills-invocable`).** Seat S's list appears under its table in section 3. None of the 35 skills sets `disable-model-invocation`. The seat applied portability Decision 3's two conditions: (a) an inbound bare-name reference exists, and (b) the body gates the side effect.
- **Deviation candidates:** both conditions hold, some only in part. There are eight:
  - finishing-a-development-branch (S-81);
  - using-git-worktrees (S-82);
  - brainstorming (S-83);
  - writing-plans (S-84);
  - executing-plans (S-85);
  - describe-critique-methodology (S-86);
  - llm-wiki (S-87);
  - derive-roadmap (S-92).

  The gates of writing-plans, executing-plans, describe-critique-methodology and derive-roadmap are partial. llm-wiki's inbound reference is weak.
- **Gaps:** a condition fails. There are four:
  - subagent-driven-development (S-88);
  - requesting-code-review (S-89);
  - writing-skills (S-90);
  - dispatching-parallel-agents (S-91).
- **Gaps under `lean.expensive-ops`:** geographic-codes and classification-codes (S-104, S-105).

## 5. Section map

These are proposed changes to `[kinds]` and `[unmapped]`, taken from the seats' section-D notes, with the rows that support each. The current lists are in `build/cc_guide/conformance.toml`. None removes a section from a kind.

- **kinds.skill:**
  - **Add `lean.model-routing`.** Skills pin `effort` and `model` (bayesian-workflow:14, tune-hyperparameters:13), and the register maps the section only to settings. Source: seat S, section D.
  - **Add `context.overview`.** Its rows at lines 19 and 22 (the skill listing and on-demand bodies) govern skills. Source: seat S, section D.
  - **Add `lean.session-hygiene`.** Its line 392 restates the 5,000-token re-attach of `skills.progressive-disclosure` line 124. Source: seat S, section D. Seat C, section D, also names subagent-driven-development's ledger against compaction.
- **kinds.agent:**
  - **Add `lean.model-routing`.** Lines 418 and 422 govern agent model pins and `availableModels`. Source: seat A, section D.
  - **Add `mechanisms.overview`.** Line 41 puts hard access boundaries in permission rules, where the reviewers' Bash boundary is a PreToolUse hook. Source: seat A, section D; rows A-12 to A-15.
  - **Add `lean.expensive-ops`.** Line 470 conflicts with test-runner's promise of untruncated output. Source: seat A, section D; row A-28.
  - **Add `lean.ceremony`.** Lines 455 and 462 bear on agent dispatch. Source: seat A, section D.
- **kinds.command:**
  - **Add `mechanisms.overview`.** Line 45 says a repeatable entry point is a manual skill. This is the R5.7 command candidate (A-38 to A-40).
  - **Add `skills.listing-budget`.** Line 115 supports the commands' zero standing cost. Source: seat A, section D.
- **kinds.hook:** **add `rules.settings`.** hooks/README.md carries permission-rule snippets at :74 (H-47, H-48).
- **kinds.rule:** **add three sections**, all from seat H, section D:
  - `mechanisms.overview` (line 43);
  - `lean.session-hygiene` (line 392: compaction summarises path-scoped rules);
  - `context.overview` (lines 18 and 22).
- **kinds.settings:**
  - **Add `hooks.patterns` and `hooks.exit-codes`.** The `hook-dir-quoted` and `stop-hook-guard` checks scan the settings kind, but its section list omits both.
  - **Add `mechanisms.overview` (line 41) and `hooks.pitfalls` (line 373: guard secrets with a Read deny).** Source: seat H, section D.
  - Seat H also notes that `hooks.configuration` maps to this kind vacuously today, since `.claude/settings.json` holds no hooks. It proposes no change.
- **kinds.claude-md:**
  - **Add `mechanisms.overview`.** Its lines 42, 43, 44 and 48 govern CLAUDE.md's content (C-30 to C-34).
  - **Add `subagents.isolation` (line 219) and `subagents.frontmatter` (line 189, `omitClaudeMd`).** Every custom agent loads the CLAUDE.md hierarchy at spawn. Source: seat C, section D.
- **`[unmapped]`:** seats S and C disagree on `lean.caching`.
  - **Seat S:** line 402 governs skill `effort` and `model` pins, which would move the section to the skill kind.
  - **Seat C:** the section governs no file's content and stays unmapped. Its line 404 bears on CLAUDE.md's "edits here are live" sentence, but only through skills.
  - The other six sections are not in dispute. Seat C confirms they govern no repo file (C-35 to C-39).
- **Not map changes, recorded for the owner:**
  - The skill kind's globs cover `SKILL.md` only, so a skill's bundled `references/`, `scripts/` and root files sit outside every check (seat S, section D; check S#7).
  - `.claude/skills/*/SKILL.md` matches no file (portability Decision 2).
  - `AGENTS.md`, `GEMINI.md` and `.gitignore` are in no kind, and install.py's Codex and Gemini roots fall under no section (seat C, section D).
  - A worktree session loads the main checkout's CLAUDE.md as well as its own, and no kind covers that layout (seat C, section D).

## 6. Proposed checks (R5.6)

Each line comes from a seat's section-C list. The bracket gives the source seat and that seat's own check number. Counts are the seats' measurements on this branch. Each check becomes a deferred item if the owner confirms it. None becomes a check in this plan.

**Skills (seat S):**
- **skill-body-lines** [S#1]: a SKILL.md body over 500 lines. Today 1 (writing-skills, 696). Portability R1.7 specifies it as a warning that `check_frontmatter.py` does not yet have. The conformance spec's R6 P3 already plans a `skill-body-size` entry for it.
- **compaction-window** [S#2]: estimated body tokens above 5,000, plus critical-sounding headings (STOP, Red Flags, Critical and similar) past that offset. Today 3 bodies and 6 headings.
- **description-person** [S#3]: first- or second-person pronouns in a description, outside quoted phrases. Today 7 (S-21 to S-27).
- **trigger-phrase-presence** [S#4]: a description has a quoted phrase or a "Trigger on" list. Heuristic. Today 9 lack both.
- **listing-aggregate** [S#5]: the summed name and description characters against window × fraction. Today 21,297 characters across 35 skills. It needs the unit the guide leaves open (guide note S-109).
- **substitution-hazard** [S#6]: an unescaped `$ARGUMENTS`, `$<digit>`, `${CLAUDE_...}` or render-time shell token in a SKILL.md body. Today 0; it would guard against regressions.
- **orphan-bundled-file** [S#7]: a file under a skill directory that no SKILL.md or reference names, excluding tests and READMEs. Today 2.
- **frontmatter-allowlist-drift** [S#8]: `check_frontmatter.py`'s `ALLOWED_KEYS` against the guide's field table. Today it rejects 10 documented fields. This is portability Stage A's ground, and it also blocks setting `disable-model-invocation` on a skill.
- **dmi-handoff-consistency** [S#9]: a skill that sets `disable-model-invocation: true` is never named as a handoff elsewhere.
- **skill-command-name-collision** [S#10, A#2, C#1]: no `commands/*.md` stem equals a `skills/*/` directory name. Today 0.

Seat S adds that its row S-94 (model named on dispatch) suits a PreToolUse hook, not a lint.

**Agents and commands (seat A):**
- **command-frontmatter-keys** [A#1]: command keys are a subset of the skill fields, with no `name` or `paths`. Today 0.
- **agent-name-form** [A#3]: an agent name is lowercase-hyphenated unless a register allow-list names it. Today it flags only `Explore` (A-04).
- **agent-model-available** [A#4]: each agent's model alias appears in `availableModels`. Today 0.
- **agent-name-unique** [A#5]: no name repeats across `agents/` and `.claude/agents/`. Today `.claude/agents/` does not exist.
- **haiku-retirement-date** [A#6]: warn on Haiku pins from 2026-10-15. Today it would flag explore.md and test-runner.md.
- **command-substitution-tokens** [A#7]: substitution or render-time shell tokens in a command body that the command does not declare. Today 0.
- **agent-effort-level** [A#8]: blocked until the guide lists the effort levels. Two agents use `xhigh`.

**Hooks, rules and settings (seat H):**
- **hook-var-quoted** [H#1]: generalise `hook-dir-quoted` to any unquoted `$VAR` at the start of a script path, `$HOME` included. It would catch README:121 (H-18).
- **managed-only-keys** [H#2]: `enforceAvailableModels` in non-managed settings (H-51). It needs guide note H-57 settled first.
- **rule-always-on-claim** [H#3]: a path-scoped rule whose text calls itself always-on (H-38).
- **hook-readme-exit-claims** [H#4]: a hooks README that says only exit 2 blocks, while it also documents a `permissionDecision` deny (H-24).
- **hook-scripts-executable** [H#5]: every wired hook script exists with mode 100755. Today all five do.
- **hook-python-deps** [H#6]: hook Python is stdlib-only or declares a PEP 723 block. The guard would pass, which turns H-32 into a recorded fact.
- **allow-rule-compound-operators** [H#7]: an unquoted `&&`, `||`, `;`, `|` or `&` in an allow rule. It would apply only to a gitignored per-machine settings file, so it can only be a local check.
- **inert-runner-allow-rules** [H#8]: runner-style allow snippets that claim to spare prompts, which auto mode sets aside (H-48).
- **hook-install-verify-step** [H#9]: install docs for a blocking hook name a trigger-it-once step (H-27). Heuristic.

**CLAUDE.md and installer (seat C):**
- **builtin-name-shadow** [C#2]: no skill or command takes a built-in command's name. It needs a register list. Today 0 against the three the guide names.
- **reserved-skill-name** [C#3, optional]: no `skills/synced/`. Absent today.
- **claude-md-import-resolves** [C#4, optional]: each `@` import in a claude-md file resolves, within 4 hops, using a fence-aware scan. Today a fence-aware scan passes; a naive one would flag CLAUDE.md:122.
- **local-md-ignored** [C#5]: `CLAUDE.local.md` is gitignored. Today it is not, and no such file exists.
- **claude-md-count-claims** [C#6, optional]: lines in claude-md files that state a test, pass or skip count. Today 22 hits. The "(19 originals" note is pinned by the test from `c67278d` on `main`, so it would need an allow-list.

Seat C proposes no install-location check, since `build/test_runtime_support.py` already pins them.

## 7. Guide notes (to the owner; for drift's `/cc-guide verify` once it exists)

Report-only. Nothing here edits the guide.

| ID | guide line | quote (verified) | note |
|---|---|---|---|
| S-108 | 122 | the listing (name + description, always loaded) | Contradicts line 111, under which overflowing descriptions are dropped. writing-skills:222 follows the line-122 reading. |
| S-109 | 111 | **1% of the model's context window** (a character budget) | The unit is unstated (the window is in tokens, the budget is called characters), so no threshold can be computed. |
| S-110 | 45 | Invocable, never auto-fired, absent from the listing | "Invocable" does not say by whom, while line 91 says manual only. Portability Decision 3's handoff exception turns on the answer. |
| A-52 | 175 | Unique lowercase-hyphenated ID | Contradicts line 214, which defines a custom `Explore` with a capital E. The repo's probe shows only the capital form shadows the built-in. |
| A-53 | 207 | its retirement window opens 2026-10-15 | Lines 209 and 214 still recommend Haiku, so line 207 goes stale in 11 days. Alias behaviour at retirement is unstated. |
| A-54 | 219 | Explore and Plan skip both | Line 214 recommends overriding the built-in Explore, while line 219 says custom agents load CLAUDE.md and git status. It does not say which applies to an override. |
| H-57 | 422 | `enforceAvailableModels`, in managed settings, extends it to the Default option | Ambiguous: it may mean the key is honoured only in managed settings, or only that it is documented there. Without the answer, H-51 and O-13 cannot be settled from the guide. |
| H-58 | 362 (against 303) | re-running the check and blocking only while it still fails re-verifies each fix, with the 8-block cap bounding the loop | Line 303 says to check `stop_hook_active`, while line 362 endorses a gate that re-blocks until the cap. The `stop-hook-guard` check enforces only line 303's reading. |
| C-40 | 48 | A `PostToolUse` hook runs the linter every time, no exceptions. | Overstates: line 369 says a Write/Edit matcher misses files that Bash rewrites, and line 371 says gates fail open. |
| C-41 | 33 | **CLAUDE.md** is the only always-loaded prose you fully control | Line 18 lists path-less rules files as always loaded and equally under your control. |

## 8. Outside the repo (R5.3)

This is seat H's `O` table, paraphrased and report-only. It reproduces no credential, and nothing in it enters the register. It covers four files:
- `~/.claude/CLAUDE.md`
- `~/.claude/settings.json`
- `~/.claude/rules/*`
- the main checkout's `.claude/settings.local.json`

The seat's text is unchanged except in O-12, where the controller paraphrased a three-word phrase that the seat had quoted from `~/.claude/CLAUDE.md`. The quoted phrase in O-22's rule column is from the guide (line 40). At the completion gate on 2026-10-04, the owner redacted O-20, O-21, O-23 and O-25 to ID, section and status, because this repo is public; their detail is held locally, outside the repo.

~/.claude/CLAUDE.md is "CLAUDE.md". The AWS rule is ~/.claude/rules/aws-agent-toolkit.md. The local settings are the main checkout's .claude/settings.local.json.

| ID | section | guide line | rule | fact/advice | artifact file:line | status | guide quote | artifact quote |
|---|---|---|---|---|---|---|---|---|
| O-01 | rules.claude-md | 233 | CLAUDE.md stays under the 200-line target | advice | ~/.claude/CLAUDE.md (33 lines) | follows | | |
| O-02 | rules.claude-md | 231 | Exclude fast-changing details and what config already states | advice | ~/.claude/CLAUDE.md:17 (states an effort default the user settings no longer carry), :32-33 (restates the model-list settings keys) | gap | | |
| O-03 | rules.claude-md | 233 | Per-line litmus: would removing the line make Claude err | advice | ~/.claude/CLAUDE.md:7-14 (behavioural deltas from defaults) | follows | | |
| O-04 | context.overview | 33 | CLAUDE.md is the only always-loaded prose; keep it lean | advice | ~/.claude/CLAUDE.md (33 lines) | follows | | |
| O-05 | lean.session-hygiene | 389 | /clear between unrelated tasks and after two failed fixes | advice | ~/.claude/CLAUDE.md:18-22, :28-30 | follows | | |
| O-06 | lean.session-hygiene | 391 | A standing compact-instructions section is an optional alternative | advice | ~/.claude/CLAUDE.md (none present) | n/a | | |
| O-07 | lean.session-hygiene | 391 | The autocompact override can only lower the trigger | fact | ~/.claude/settings.json (env override set to a low threshold) | follows | | |
| O-08 | lean.session-hygiene | 390, 392-393 | /rewind, compaction loss, plan-mode caching | advice | CLAUDE.md carries no such guidance | n/a | | |
| O-09 | lean.model-routing | 419 | Diagnose in order: context, then effort, then model | advice | ~/.claude/CLAUDE.md:25-30 | follows | | |
| O-10 | lean.model-routing | 418 | Haiku for mechanical subagents | advice | ~/.claude/CLAUDE.md:24 | follows | | |
| O-11 | lean.model-routing | 419 | Effort is saved per model in modelSettings | fact | ~/.claude/CLAUDE.md:17 says sessions default to auto effort, while ~/.claude/settings.json persists a fixed top effort level for Opus 5.5 | gap | | |
| O-12 | lean.model-routing | 422 | Model precedence ends at the model setting | fact | ~/.claude/CLAUDE.md:19-20 sends execution to a Sonnet-default session, but line 17 and ~/.claude/settings.json make Opus the default | gap | | |
| O-13 | lean.model-routing | 422 | enforceAvailableModels is a managed-settings key | fact | ~/.claude/settings.json sets it at user level; ~/.claude/CLAUDE.md:32-33 relies on it to pin the selectable set (R5.7 candidate; same rule as H-51) | gap | | |
| O-14 | lean.model-routing | 417 | The advisor pairs a cheaper main model with a stronger one | advice | ~/.claude/settings.json (advisor is Opus, equal to the default main model; the pairing helps in Sonnet execution sessions) | follows | | |
| O-15 | hooks.configuration | 318 | A user-level hook entry: matcher Bash, type command | fact | ~/.claude/settings.json:19-30 (the target is a symlink to the repo guard, exists and is executable) | follows | | |
| O-16 | hooks.patterns | 331 | Hook command double-quotes the variable locating its script | advice | ~/.claude/settings.json:25 (the guard command starts with an unquoted $HOME; same as H-18) | gap | | |
| O-17 | hooks.pitfalls | 371 | Gates fail open on a bad path; trigger each gate once | advice | ~/.claude/settings.json:25 (the path resolves; Gate B probe exists) | follows | | |
| O-18 | rules.rules-files | 247 | A rule without paths loads in every session | fact | ~/.claude/rules/aws-agent-toolkit.md (no frontmatter, 31 lines). R5.7 candidate confirmed. Its header records an upstream source and date, not a reason for omitting paths. Its secrets clause may be meant to persist | gap | | |
| O-19 | rules.rules-files | 245 | ~/.claude/rules holds personal rules | fact | ~/.claude/rules/ (one regular file, no symlinks out) | follows | | |
| O-20 | mechanisms.overview | | | | detail held locally | gap | | |
| O-21 | rules.settings | | | | detail held locally | gap | | |
| O-22 | mechanisms.overview | 40 | "Never use pip" belongs in a hook | advice | settings.local.json:36, :102 (allows any pip install, system and /tmp venv). R5.7 candidate confirmed. README.md:18-24 says why uv-guard is not wired here, not why pip stays allowed | gap | | |
| O-23 | rules.settings | | | | detail held locally | gap | | |
| O-24 | rules.settings | 264, 267 | `*` word-boundary form and //abs file-rule paths | fact | settings.local.json (uses the `*` form throughout, and the // form for the three Read rules) | follows | | |
| O-25 | hooks.pitfalls | | | | detail held locally | gap | | |

## 9. Unverified rows

None. All 352 quotes re-grepped as single-line matches.

## 10. Owner decisions

The owner decided these at the plan 35 owner gate on 2026-10-04, answering the questions interactively. Each exception ID below is the register entry Task 11 writes. A deferred item for a gap names, in its text, the exception that its fix must remove (R5.5). No row was corrected to follows or n/a, so no group-table row is annotated.

### Exceptions

| exception | rows | type | reason | revisit trigger, or where the fix lands |
|---|---|---|---|---|
| `grep-glob-beside-bash` | L-02–L-08 | gap | The Gemini adapters map Grep and Glob to working tools, so removing them from the canonical files would regress Gemini (`protects = ['gemini']`). | drift Stage 3 (drift R11.5 #1) |
| `hook-dir-unquoted` | L-09–L-11 | gap | The README install snippet predates the quoted pattern. | drift Stage 3 (drift R11.5 #3) |
| `claude-md-size` | L-01 | gap | Codex and Gemini read the same file, so instructions leave it only by deliberate condensing or relocation. | deferred item: bring the root CLAUDE.md under 200 lines. Ceiling 225; see the CLAUDE.md decision below |
| `description-when-only` | S-28–S-52, S-54 | deviation | writing-skills requires trigger-only "Use when" descriptions, on tested evidence that a workflow summary lets agents skip the body (portability Decision 4). S-54 is TDD's short description, which writing-skills holds up as its good example. | when trigger-eval suites exist |
| `side-effecting-skills-invocable` | S-81–S-87, S-92 | deviation | Other skills hand off to these eight by bare name, which a manual-only skill cannot receive, and each body gates its side effect, some only in part (portability Decision 3). | when the guide documents a way for one skill to hand off to a manual-only skill |
| `side-effecting-skills-ungated` | S-88–S-91 | gap | subagent-driven-development, requesting-code-review, writing-skills and dispatching-parallel-agents act with side effects, but each lacks a body gate or an inbound handoff, so Decision 3's reason does not cover them. | deferred item |
| `writing-skills-guide-gaps` | S-02, S-58, S-67, S-68, S-107 | gap | writing-skills departs from the guide on body length, the listing budget, critical-rules-first and `@` loading. S-107's claim is unsupported rather than contradicted, and Stage D verifies or drops it. | portability Stage D |
| `writing-skills-tdd-for-docs` | S-97 | deviation | writing-skills:409: tests written after the fact prove nothing, so the skill treats documentation as behaviour-shaping. | when portability Stage D revises writing-skills |
| `description-second-person` | S-21–S-27 | gap | Seven skill descriptions use second person outside quoted trigger phrases. | deferred item |
| `critical-rules-past-compaction` | S-69, S-70 | gap | Critical sections of subagent-driven-development and bayesian-workflow sit past the first 5,000 tokens that compaction re-attaches. | deferred item |
| `dispatch-model-in-prose` | S-94 | gap | subagent-driven-development's model-on-dispatch rule is machine-checkable but stays prose. | deferred item |
| `brainstorming-every-project` | S-96 | gap | brainstorming applies to every project, while the guide and the owner's proportional-process rule in `/deferred` reserve it for open design decisions. | deferred item |
| `review-before-every-merge` | S-99 | gap | requesting-code-review requires review before every merge, where the guide skips it for a small change you watched. | deferred item |
| `network-rebuild-ungated` | S-104, S-105 | gap | geographic-codes and classification-codes rebuild `data/` from the network when it is missing, with no manual gate. | deferred item |
| `explore-capitalised-name` | A-04 | deviation | Only the capitalised name overrides the built-in Explore agent (explore.md:2-8). | re-probe after Claude Code binary updates (explore.md:7-8) |
| `readonly-agents-hold-bash` | A-12–A-15, H-34 | deviation | The read-only agents need Bash for git and test commands. The guard hook bounds it, because a PreToolUse matcher keys on the tool, not the agent (the read-only-guard spec). | when permission rules can be scoped to an agent type |
| `debugger-lacks-write` | A-18 | gap | debugger has Edit and Bash but not Write, yet its body has it create a failing test file. The recorded reason covers Edit only. | deferred item |
| `docs-writer-holds-bash` | A-20 | gap | docs-writer holds Bash with no recorded reason. | deferred item |
| `task-reviewer-sonnet-floor` | A-26 | deviation | task-reviewer.md:5: Sonnet is the floor, and the controller escalates to Opus per dispatch. | if the per-spawn model override stops applying |
| `reviewers-flag-beyond-correctness` | A-33, A-34 | gap | code-reviewer and task-reviewer invite findings beyond correctness and requirement gaps. | deferred item |
| `commands-stay-command-files` | A-38–A-40 | deviation | The Gemini TOML adapters are generated from `commands/*.md`, and `/deferred` is an install dependency. | when the Gemini adapters can be generated from skills |
| `hooks-readme-home-unquoted` | H-18 | gap | The guard's install command in hooks/README.md leaves `$HOME` unquoted. | deferred item: hooks/README.md fixes (shared) |
| `hooks-readme-exit-claim` | H-24 | gap | hooks/README.md says only exit 2 blocks, beside a hook that blocks by JSON deny. | deferred item: hooks/README.md fixes (shared) |
| `hooks-readme-no-verify-step` | H-27 | gap | The install path for the blocking hooks has no step to trigger each one once. | deferred item: hooks/README.md fixes (shared) |
| `hooks-readme-auto-mode-allow` | H-48 | gap | hooks/README.md says the allowlist spares the uv forms a prompt, which holds only in manual mode. | deferred item: hooks/README.md fixes (shared) |
| `guard-stdlib-only` | H-32 | deviation | The guard must run on the Python 3.9 floor under launchd's `/usr/bin` interpreter, so it stays stdlib-only (readonly-agent-guard.md:65). | when the guard needs a third-party dependency |
| `clean-code-rule-always-on-label` | H-38 | gap | rules/clean-code-python.md is titled always-on but loads only on a `.py` read or edit (the 2026-10-03 repo audit's D12). | deferred item |
| `clean-code-rule-path-scoped` | H-39 | deviation | Plan 15 chose a token-cheap, path-scoped rule. | when the clean-code family is next revised |
| `clean-code-rule-project-level` | H-41 | deviation | The rule names work repos but ships per repo, by the project-level-only decision at deferred_items.md:564-575. | if the rule moves to `~/.claude/rules` |
| `enforce-available-models-project` | H-51 | gap | `enforceAvailableModels` is set in project settings, while the guide places its effect in managed settings. Whether this is a gap at all turns on guide note H-57. | deferred item, pending H-57 |
| `claude-md-fast-changing-details` | C-02–C-05 | gap | CLAUDE.md and build/CLAUDE.md carry hand-kept test counts, rules restated from code, and a stale description of `build/`. | deferred item: bring the root CLAUDE.md under 200 lines (shared with `claude-md-size`) |
| `commit-lints-in-prose` | C-31, C-32 | gap | CLAUDE.md's before-commit lints and its rule against hand-editing `runtimes/` are prose that no hook or CI enforces. | deferred item |
| `claude-md-serves-codex-gemini` | C-33, C-34 | deviation | CLAUDE.md is the one file Codex and Gemini read (spec Decision 1, R4.3), so the Python-style line and the Commands block stay. | when Codex and Gemini can load that content from a rule or a skill |

### CLAUDE.md

- **Choice A:** trim to 225 without dropping any instruction (Task 10).
- **Measured at the gate:** L = 238, M = 238, B = 238, so G = 0 and P = 238.
- **Exception:** `claude-md-size` is a gap, with ceiling 225. Its `tracked_in` is the deferred item "bring the root CLAUDE.md under 200 lines", which `claude-md-fast-changing-details` shares.
- **Unmerged branches:** `codex/recommend-causal-design` adds +1 net and `worktree-deferred-triage-2026-10-03` adds +3 net. Once the ceiling lands, a merge that takes CLAUDE.md over 225 fails the lint. A branch whose delta does not fit trims at its merge, or raises the ceiling there on purpose, with a reason.

### Section map

- **c1–c17 confirmed.** Task 11 adds these sections:
  - **kinds.skill:** `lean.model-routing`, `context.overview` and `lean.session-hygiene`.
  - **kinds.agent:** `lean.model-routing`, `mechanisms.overview`, `lean.expensive-ops` and `lean.ceremony`.
  - **kinds.command:** `mechanisms.overview` and `skills.listing-budget`.
  - **kinds.hook:** `rules.settings`.
  - **kinds.rule:** `mechanisms.overview`, `lean.session-hygiene` and `context.overview`.
  - **kinds.settings:** `hooks.patterns`, `hooks.exit-codes`, `mechanisms.overview` and `hooks.pitfalls`.
  - **kinds.claude-md:** `mechanisms.overview`, `subagents.isolation` and `subagents.frontmatter`.
- **c18:** `lean.caching` leaves `[unmapped]` for `kinds.skill`. Its line 402 governs a skill whose `model:` differs from the session's (seat S's reading).

### Proposed checks (R5.6)

- d2–d7 and d9–d31 each become a deferred item, 29 in all.
- d1 (`skill-body-lines`) gets no new item: it is already planned, as conformance R6 P3's `skill-body-size`.
- d8 (`frontmatter-allowlist-drift`) gets no new item either. It goes to portability Stage A (R1.1).

### Guide notes

- f1–f10 each become a deferred item to run `/cc-guide verify <section>` once drift lands (drift R8.5):
  - S-108: `skills.progressive-disclosure`
  - S-109: `skills.listing-budget`
  - S-110: `mechanisms.overview`
  - A-52: `subagents.frontmatter`
  - A-53: `subagents.models`
  - A-54: `subagents.isolation`
  - H-57: `lean.model-routing`
  - H-58: `hooks.patterns`
  - C-40: `mechanisms.overview`
  - C-41: `context.overview`
- Nothing here edits the guide.

### Outside the repo

- **Two owner items,** covering rows O-20 and O-25, and O-21, O-22 and O-23. Because this repo is public, the owner redacted their detail at the completion gate (2026-10-04). It is held locally, outside the repo, and neither item is logged in `specs/deferred_items.md`.
- **Folded into repo items:**
  - O-13 goes into `enforce-available-models-project`'s item.
  - O-16 goes into the shared hooks/README.md item, which re-applies the quoted command to `~/.claude/settings.json`.
- **No item:** O-02, O-11, O-12 and O-18. Nothing in this plan edits these files.

### Deferred items to log at completion

54 in `specs/deferred_items.md`:
- **15 from the exceptions above:**
  - the root CLAUDE.md under 200 lines;
  - `side-effecting-skills-ungated`;
  - `description-second-person`;
  - `critical-rules-past-compaction`;
  - `dispatch-model-in-prose`;
  - `brainstorming-every-project`;
  - `review-before-every-merge`;
  - `network-rebuild-ungated`;
  - `debugger-lacks-write`;
  - `docs-writer-holds-bash`;
  - `reviewers-flag-beyond-correctness`;
  - the shared hooks/README.md fixes, flagged for `/deferred` as a quick fix;
  - `clean-code-rule-always-on-label`;
  - `enforce-available-models-project`;
  - `commit-lints-in-prose`.
- **29 proposed checks.**
- **10 guide-note verifications.**
- **The 2 owner items outside the repo** are held locally instead (completion gate).

drift Stage 3 and portability Stages A and D carry the rest.
