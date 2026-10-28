<!-- cc-guide: skills.locations commands.overview subagents.overview subagents.models rules.rules-files hooks.events hooks.exit-codes hooks.configuration @2.1.306 -->
# agent-skills

This repo is my personal collection of [Agent Skills](https://agentskills.io/specification) for
**Claude Code, Codex, and Gemini CLI**.

Each skill is a self-contained directory under [`skills/`](skills/). It holds a `SKILL.md`, plus
any `references/` or `scripts/` that it needs. All three runtimes find the
same skill source. A runtime loads a skill's full body only when the skill's description matches
the task, or when you invoke the skill explicitly.

> [!IMPORTANT]
> **These skills have strong opinions about my environment and my process.** They work best if you share those opinions, or if you choose to adopt them. Read a skill's `SKILL.md` before you install it, and edit what does not fit. It is all plain Markdown. Know these three assumptions:
>
> - **The process skills impose a spec-driven lifecycle.** `brainstorming`, `writing-plans`, `executing-plans`, and `subagent-driven-development`, with the `/deferred` command, drive every feature through spec → plan → implementation → retirement. They create and maintain this structure in your project:
>   - specs, as Markdown files in `specs/`
>   - plans, in `specs/plans/<id>-<spec-name>.md`, numbered automatically
>   - finished work, retired to `specs/completed/` and `specs/plans/completed/`
>   - work that you consciously defer, appended to `specs/deferred_items.md`
>
>   If your projects do not use that layout, these skills start to build it.
> - **The review steps send code to OpenAI when the Codex CLI is present.** `executing-plans`, `subagent-driven-development`, and `finishing-a-development-branch` run a read-only second-opinion review with the Codex CLI (`codex exec review`) whenever `codex` is on your `PATH`. The review is agentic. It sends the branch diff to OpenAI under your Codex login, *and* every repository file and command output that Codex reads during the review. Where code egress is governed, keep `codex` off that machine or remove the step.
> - **The data and modeling skills assume my stack.** That stack is Polars (not pandas), NumPyro + JAX (not PyMC), Python 3.13, and Altair, matplotlib, and plotly for charts. `validate-data` is tuned to BLS (Bureau of Labor Statistics) data.

## Layout

Skills are the center of the repo. The repo also carries runtime-specific agents, commands, hooks,
and instruction files:

```
agent-skills/
├── skills/      # agent skills, one directory per skill (the tables below)
├── archive/     # retired skills, kept whole for a later restore (archive/README.md); never installed
├── agents/      # subagent definitions (reviewers + security/search/test/debug/docs — see Agents below)
├── commands/    # slash commands (/deferred, /fix-issue, /license-audit — see Commands below)
├── runtimes/    # generated Codex/Gemini agent and command adapters
├── hooks/       # Claude Code hooks: gates for Python/uv work repos + the read-only agent guard (see Hooks below)
├── rules/       # rule files: path-scoped via .claude/rules/, one user-level (see Rules below)
├── build/       # lints and commit gates, the adapter generator, the Claude Code guide's drift detector, citation checks
├── specs/       # design records + implementation plans (retired work under completed/)
└── install.py   # safe installer for Claude, Codex, Gemini, or all three (idempotent when linking)
```

The canonical skill bodies are portable. The runtimes use different file formats and tool names,
so `build/sync_runtime_assets.py` generates the Codex and Gemini agent files from
[`agents/`](agents/). It also generates Gemini's TOML commands from [`commands/`](commands/). The
hooks and rules stay specific to Claude Code. See [Installation](#installation) and the
compatibility notes below.

## Skills

### Mine

| Skill | Description |
|-------|-------------|
| [`bayesian-workflow`](skills/bayesian-workflow/) | An opinionated Bayesian modeling workflow with NumPyro (JAX) and ArviZ. It walks the full loop, from formulating a model to reporting results. It encodes guardrails that most agents skip: prior and posterior predictive checks, LOO-PIT calibration, prior-sensitivity checks, 94% HDI, non-centered parameterizations, and reproducible PRNGKey seeds. It bundles three scripts. `diagnose_model.py` and `calibration_check.py` write their results as JSON. `check_diagnostics.py` turns that JSON into qualitative ratings and ordered next steps for the report. *(Adapted from Alexandre Andorra's PyMC skill. See Credits.)* |
| [`deep-learning`](skills/deep-learning/) | Design, implement, train, fine-tune, and diagnose neural models in JAX. It uses Flax NNX, Optax, and Orbax by default. Its focused references cover sequence, scientific, vision, geometric, generative, and LLM topics. |
| [`evaluate-deep-learning`](skills/evaluate-deep-learning/) | Evaluate neural models and research claims with explicit held-out inputs, metrics, leakage checks, comparable budgets, seed variation, domain checks, and experiment records. |
| [`optimize-jax`](skills/optimize-jax/) | Reproduce, profile, and improve JAX execution: tracing, compilation, memory, precision, sharding, and generation and cache performance. It measures every change and keeps correctness parity. |
| [`recommend-probabilistic-model`](skills/recommend-probabilistic-model/) | Given a problem and its data, recommend a probabilistic-ML method grounded in Kevin Murphy's *Probabilistic Machine Learning* books. The skill is a thin decision-map router over 8 deep families: regression/GLMs/counts, hierarchical, time-series/state-space, GPs, factor models, classification, mixtures, and graphical models. It gives **verified** § references and pyprobml notebooks, a regularization and selection step that depends on the chosen family, and a structured handoff to `bayesian-workflow`. It bundles `characterize.py`, which computes the modeling signals that `explore-data`'s `profile.py` does not, such as overdispersion and class balance. It recommends and points. It does not fit a model. |
| [`recommend-causal-design`](skills/recommend-causal-design/) | Choose a causal research design before estimation. The skill defines the requested effect, and it makes the causal diagram and the identification assumptions explicit. It compares credible designs and writes a recommendation memo with diagnostics, sensitivity plans, and an implementation handoff. It covers experiments, adjustment and weighting, instrumental variables (IV), regression discontinuity (RDD), difference-in-differences (DiD), synthetic control, interrupted time series, and longitudinal regimes. It keeps local effects separate from population targets. When identification fails, it gives an evidence plan. Its planning workflow is selectively adapted from Robson Tigre and Alexandre Andorra (MIT). |
| [`recommend-visualization`](skills/recommend-visualization/) | Given an `explore-data` profile and an intent (trend, comparison, distribution, correlation, part-to-whole, ranking, geographic, flow), recommend the right chart, then write the code. The recommendation conditions on the data's *signals*: cardinality, row count, skew, panel shape, and null rates. Its core is a pure, unit-tested `(intent × signal) → ranked candidates` router. The router ships the **encoding map** (field → channel), grounded in perceptual theory. It routes the code phase (Phase 2) to **Altair**, **matplotlib**, or **plotly**. The skill is the visualization sibling of `recommend-probabilistic-model`. That skill recommends a model. This one recommends a view and carries it through to code. |
| [`track-model-experiments`](skills/track-model-experiments/) | Keep a ledger of model variants for each analysis, and rank the variants on one declared criterion. A human-written `experiments.md` records *what changed and why* across `v1 → v2 → v3`. A bundled `compare_experiments.py` ranks the variants and stamps the winner back into the ledger. ELPD mode loads each Bayesian variant's saved InferenceData, ranks the variants with `az.compare`, and extracts convergence diagnostics. Score mode ranks any variants (tabular cross-validation, forecast backtests, or Bayesian leave-future-out) from each variant's `scores.json` of per-fold or per-origin scores. It reports each variant's paired difference from the top variant and its standard error. The comparator refuses the inputs that make a comparison silently wrong. In ELPD mode, it refuses variants fit to different observations, a missing `log_likelihood` group, several log-likelihood variables (one per source in a multi-source model), or a log-likelihood with no pointwise terms. In score mode, it refuses mixed criteria or orientations, unit sets that differ, non-finite scores, or fewer than two units. In both modes, it refuses a mode that does not match the ledger's criterion. It names each ledger row that it could not rank. `references/predictive-evaluation.md` holds the backtest protocol, the paired-difference rule and its limits, benchmark baselines, and proper scores. The skill owns the variant ledger and the stopping rule. `bayesian-workflow`'s `model-comparison.md` owns the ELPD statistics. Neural runs stay with `evaluate-deep-learning`. |
| [`tune-hyperparameters`](skills/tune-hyperparameters/) | Tune any model's knobs without leakage or overfitting: sklearn, boosting, statsmodels, NumPyro, dynamax and neural models. First classify the *regime*: predictive search (regime A), inference diagnostic (regime B) or structural choice (regime C), such as the number of mixture components or an AR order. Then tune the right objective with the right guard. For regime A, a table picks the cross-validation splitter from the data's dependence structure: independent, grouped, spatial or temporal. For temporal data, the skill bundles a `PurgedTimeSeriesSplit` (`time_series_cv.py`). It gives forward-chaining cross-validation with an embargo gap and an optional label-horizon *purge*. Given each row's period, it splits whole periods, so it also works on a panel. It feeds a manual, seeded **Optuna** objective (verified against the installed version), with nested cross-validation for large searches and a neural search loop: a trial budget, pruners, early stopping inside the training fold, and seed replication. A paired per-fold rule says when a gain is noise. For regime B, a thin decision table routes the NUTS and SVI knobs to `bayesian-workflow`, and the skill owns the optax learning rate of non-neural point fits. The bundled splitter guards **temporal** leakage only. It graduates a tuned winner to a `track-model-experiments` variant row with a `scores.json` that the comparator ranks in score mode, and it leaves revision and vintage leakage to `develop-testing-strategy`. |
| [`creative-thinking`](skills/creative-thinking/) | Divergent target-finding for when the goal itself is fuzzy: the analysis, the estimand, the objective, or the approach space. Instead of converging on the first plausible target, the skill delivers a *map* of genuinely distinct candidate targets. It sketches each candidate in 3 lines or fewer and names the selection criteria. At least one candidate escapes the map's own organizing frame. It sorts gating questions by where the answer lives. It asks first for facts that the user holds (data access, the consuming decision), with a one-line preview for each direction. It absorbs modeling judgments provisionally, and it marks the candidates that would flip under the other answer. It runs ahead of `brainstorming`'s narrowing and `tune-hyperparameters`' mechanics, and it hands the chosen target off unchanged. It was eval-tested against a no-skill baseline (RED→GREEN, two human-reviewed iterations). |
| [`develop-testing-strategy`](skills/develop-testing-strategy/) | Design a test strategy from *invariants*, not coverage %, for web scrapers, Polars pipelines, and NumPyro/PyMC models. Its methods include recorded fixtures, schema/null/key assertions, determinism, SBC-lite (parameter recovery on simulated data), and golden-master parity. |
| [`validate-data`](skills/validate-data/) | QA a dataset or an analysis before it ships: schema/integrity, reproducibility, benchmark reconciliation, and methodology/bias checks. It is Polars-first, and it is tuned to BLS data and to as-of/vintage correctness. |
| [`explore-data`](skills/explore-data/) | Profile a new dataset with Polars before analysis: null rates, key uniqueness, distributions, duplicates, quality flags, and panel balance. It bundles a reusable `profile.py`. |
| [`tech-debt`](skills/tech-debt/) | Audit, categorize, and prioritize tech debt in research and data codebases, with the DELETE-vs-HARDEN triage. It bundles `scan.sh`, a sweep for debt signals. |
| [`design-architecture`](skills/design-architecture/) | Write or evaluate Architecture Decision Records (ADRs) for data and modeling systems, for example NumPyro/JAX vs PyMC, a store layout, or a vintage data model. It bundles an ADR scaffolder. |
| [`llm-wiki`](skills/llm-wiki/) | Maintain a personal research wiki (the Karpathy LLM-wiki pattern) as a citation-audited knowledge base instead of a folder of unread PDFs. The skill ingests a source as a `status: unverified` page. It promotes claims onto concept pages that carry inline `[slug §x]` locators. The **quarantine rule** forbids an unverified summary from ever becoming grounds for another page. A contradiction keeps *both* claims, with an entry in `open-questions.md`, instead of an overwrite. Every operation that changes the wiki appends to `log.md`. The wiki root (`$LLM_WIKI_ROOT`) owns its normative `SCHEMA.md`, so the skill stays generic. A second root, for example work vs. personal with no content crossing between them, reuses the skill unchanged. A supervised harvest turns a repo's `specs/` corpus (specs, plans, deferred items) into a `raw/specs/` digest, one repo at a time. The skill bundles four stdlib-only scripts. `bootstrap_wiki.py` seeds a fresh root and never overwrites content. `lint_wiki.py` is the mechanical gate before any status flip. `distill_sessions.py` turns Claude Code transcripts into capture notes to ingest. `distill_specs.py` runs the harvest's mechanical inventory and assembly steps. An [`INSTALL.md`](skills/llm-wiki/INSTALL.md) covers fresh machines. |
| [`describe-critique-methodology`](skills/describe-critique-methodology/) | Leg 1 of the methodology-critique loop. Write a system-level or module-level **methodological description** of a codebase. Its math and prose are deliberately decoupled from the code: a notation table, the data-generating story, the estimation procedure, assumptions, evaluation criteria, and open questions. Carry the description to a Claude Chat **Research** critique. Then **synthesize** the description and the adjudicated critique into a house-format spec, routed onward to `derive-roadmap`. Routing headers in the artifacts themselves join the two modes (Describe and Synthesize). The skill bundles an advisory `check_decoupling.py`. In v1, its scope is statistical, Bayesian, and nowcast work. |
| [`derive-roadmap`](skills/derive-roadmap/) | Leg 2 of the methodology-critique loop. It takes a synthesized spec and the system that the spec describes, and it partitions the distance between them into staged spec→plan→implementation cycles. It runs a one-time gap analysis over every numbered requirement. The rubric in `references/gap-rubric.md` has four classes: implemented-as-specified, implemented-differently, missing, and in-code-but-not-in-spec. The skill orders stages by dependency and information order, not by the spec's own priority ranking. When the gaps fit a single cycle, it writes no roadmap file at all. Otherwise it writes a brevity-budgeted `specs/<name>-roadmap.md` (`references/roadmap-format.md`) that cites the spec's § references instead of restating them. Every stage routes onward to `brainstorming` or `writing-plans` by bare name. This skill never designs a stage. It resumes from authoritative stage stamps, and it supports a first-class PARKED exit that folds unticked stages into `specs/deferred_items.md`. |
| [`prepare-handoff`](skills/prepare-handoff/) | The sending half of a handoff between sessions. Before a fresh session takes over a spec, a plan, or a checkpoint, the skill sorts what that session needs into four bins. The bins are: already in the artifact, recomputed by the receiver, amendable and committed now, or everything else. Only the last bin goes into a brief, which is never committed. Fact-checker and cold-reader templates review the brief. The final message gives one launch line for each runtime, and it leaves the choice of model to the owner. |
| [`write-with-asd-ste100`](skills/write-with-asd-ste100/) | Write and rewrite in ASD-STE100 Simplified Technical English (STE), the controlled English of aircraft maintenance manuals. Human mode, the default, writes about 80% of the way to the standard, after a tip from Andrej Karpathy. Agent mode applies strict rules to prompts, tool descriptions, subagent briefs and error strings. The skill rewrites a text, or a whole file in place (left uncommitted) or as a `.ste` copy beside it. It also explains, summarizes and draws small Mermaid diagrams, and it never claims dictionary compliance. It bundles danyuchn's structural linter, unchanged. A user-level rule carries the everyday habits and a label rule into every session (see [Rules](#rules)). Adapted from danyuchn and prithivrajmu (MIT). |
| [`document-python-package`](skills/document-python-package/) | Document a public Python package with Great Docs 0.17.x. The skill is a thin layer over Posit's five official Great Docs skills. It builds on them and copies none of their text. A bundled `preflight.py` checks the great-docs version that `uv.lock` pins against the tested range and finds the config. Then it fetches the official skills from the matching release tag into a cache. The skill pins great-docs in a uv `docs` group that CI also installs. It makes the README work as the site homepage, and it freezes slow executed examples. Its done gate has three checks: lint, a build that kept its API reference, and docstring completeness. |

### Clean-code family (rule catalog adapted from Robert C. Martin's *Clean Code*)

This family is the proactive-cleanup counterpart to `tech-debt`. It applies standards in the flow of normal editing, and consent bounds how far it goes. Most rule *codes* come from Martin's Chapter 17 catalog, cited by code only, with no book prose. The exception is the Modules category (rules M1–M4, on module and subpackage granularity), which is adapted from Mancuso Lab's `python-module-design` skill (see [Credits](#credits)). The curation leaves mechanical rules to ruff and keeps the judgment-level ones, tuned to Polars and JAX. A third artifact, the [`clean-code-python`](rules/clean-code-python.md) rule, loads the Python guardrails whenever a `*.py` file is read, written or edited (see [Rules](#rules)).

| Skill | Description |
|-------|-------------|
| [`clean-coder`](skills/clean-coder/) | Opportunistic cleanup with a consent gate. In-scope fixes apply directly. Anything adjacent goes through announce → list (`file:line` + rule code) → ask → apply-on-yes. Beck's *Tidy First?* supplies the spine: tidyings and behavior changes never share a commit, and a stopping rule caps the cascade and defers bigger findings to `tech-debt`. It was pressure-tested against a no-skill baseline on six gate scenarios. |
| [`clean-code`](skills/clean-code/) | The curated standards catalog that `clean-coder` applies. It gives each of Martin's Names, Functions, General, Comments, and Tests rules (N/F/G/C/T) one disposition: keep, defer to ruff, or drop. Its examples are tuned to the stack. Polars fluent chains are not Law of Demeter violations. `jax.lax.switch` is the dispatch that G23 (dispatch over if/elif chains) asks for. Comments that carry design intent survive C3 (no redundant comments). A sixth category, Modules (M1–M4), comes from Mancuso Lab. Six per-category references load on demand, and every fix cites its rule code. |

### Adapted from [superpowers](https://github.com/obra/superpowers) (Jesse Vincent, MIT)

These skills are adapted from Jesse Vincent's superpowers skills. They are process disciplines for planning, TDD (test-driven development), debugging, code review, and skill authoring. I made three mechanical changes so that they work as standalone personal skills:

- I rewrote cross-skill references from the `superpowers:` plugin namespace to bare skill names.
- I removed unused authoring scaffolding.
- I dropped the plugin-bootstrap skill.

Beyond that cleanup, I rewired the planning and execution skills around the spec-driven lifecycle at the top of this README. The lifecycle has the `specs/` layout, auto-numbered plans, and a plan-completion protocol that marks up the plan, logs deferred items, and retires the spec. Upstream does not impose that workflow. For attribution and license, see [`NOTICE`](NOTICE) and [`LICENSE-superpowers`](LICENSE-superpowers).

> [!NOTE]
> These skills overlap with the upstream **superpowers plugin**. If you also run that plugin, these personal copies duplicate it under the same names: bare names here, and the `superpowers:` namespace in the plugin. Use one source to avoid the duplication.

| Skill | Description |
|-------|-------------|
| [`brainstorming`](skills/brainstorming/) | Explore intent, requirements, and design before any creative or build work. |
| [`writing-plans`](skills/writing-plans/) | Turn a spec into a written implementation plan before you touch code. |
| [`executing-plans`](skills/executing-plans/) | Execute a written plan directly in the current session. Use it for tightly coupled plans, or when your partner asks for direct execution. |
| [`subagent-driven-development`](skills/subagent-driven-development/) | Execute plans with independent tasks in the current session. |
| [`dispatching-parallel-agents`](skills/dispatching-parallel-agents/) | Fan out 2+ independent tasks with no shared state. |
| [`test-driven-development`](skills/test-driven-development/) | Write tests before implementation for any feature or bugfix. |
| [`systematic-debugging`](skills/systematic-debugging/) | Diagnose bugs and test failures methodically before you propose fixes. |
| [`verification-before-completion`](skills/verification-before-completion/) | Run the verification and check its output before you claim that work is done. |
| [`requesting-code-review`](skills/requesting-code-review/) | Get work reviewed when you complete a feature or before you merge. It also carries the recipe for the Codex CLI second-opinion review (`codex-review.md`). The plan executors run that review beside `code-reviewer`, and branch finishing runs it before a merge or a PR. Where the `codex` CLI is absent, the review is skipped with a notice. |
| [`receiving-code-review`](skills/receiving-code-review/) | Handle review feedback with rigor instead of blind agreement. |
| [`finishing-a-development-branch`](skills/finishing-a-development-branch/) | Decide how to integrate completed work: merge, PR, or cleanup. A Codex second-opinion review gates the merge and the PR. |
| [`using-git-worktrees`](skills/using-git-worktrees/) | Create an isolated workspace for feature work. |
| [`writing-skills`](skills/writing-skills/) | Create, edit, and verify agent skills. |

## Agents

The canonical subagent definitions live in [`agents/`](agents/). Claude Code loads these files
directly. The generated Codex TOML and Gemini Markdown adapters live under
[`runtimes/`](runtimes/). The adapters keep the same system-prompt body and map Gemini's tool
identifiers. They declare read-only sandboxes in Codex where required. They inherit the active
runtime model instead of carrying Claude model names.

Five agents are read-only: `code-reviewer`, `task-reviewer`, `security-auditor`, `Explore`, and
`test-runner`. They keep a shell, and each runtime handles that shell differently:

- **Claude Code:** their `tools:` lists hold no `Write` or `Edit`. The read-only agent guard, once
  you install it (see [Hooks](#hooks)), denies Bash commands that change files or git state. The
  guard is a guardrail against drift from the contract, not a sandbox.
- **Codex:** each adapter sets `sandbox_mode = "read-only"`.
- **Gemini CLI:** each adapter lists `run_shell_command` with no restriction.

| Agent | Description |
|-------|-------------|
| [`code-reviewer`](agents/code-reviewer.md) | A read-only reviewer for diff-based reviews against a plan, a spec, or requirements. `requesting-code-review` dispatches it, and so does `subagent-driven-development` for its final whole-branch review. Per-task reviews go to `task-reviewer`. It has no edit tools. It inspects history with `git show` and `git diff`, and it reports Critical, Important, and Minor findings with a merge verdict. Opus-pinned. |
| [`task-reviewer`](agents/task-reviewer.md) | A read-only, task-scoped reviewer for `subagent-driven-development`'s per-task gate. It checks one task's diff against its brief for spec compliance and code quality, and it returns both verdicts. It carries the full review contract, so a dispatch needs only the paths of the task's brief, report, and diff. Sonnet is its floor. For a risky or subtle diff, the controller escalates the review to Opus. |
| [`security-auditor`](agents/security-auditor.md) | A read-only security reviewer for a diff, a branch, or a repo. It covers injection, committed secrets and credential handling, insecure deserialization, TLS verification, and dependency risks. It ranks findings by severity, each with file:line and a concrete remediation. Opus-pinned, like `code-reviewer`. |
| [`explore`](agents/explore.md) | ⚠ A Haiku-pinned **override of the built-in `Explore` agent**. It keeps the same read-only fan-out-search contract and adds a structured output contract: `path:line` refs with relevance notes, and no file dumps. The frontmatter `name: Explore` (capital E) is what shadows the built-in. Claude Code resolves agents by the name field, case-sensitively. Shadowing depends on the version (probed on Claude Code 2.1.219), so probe again after a binary update. |
| [`test-runner`](agents/test-runner.md) | Runs one test suite in isolation and reports the complete failure output. It never truncates a traceback, it reports warnings as findings, and it does not diagnose. The dispatch supplies the exact command. The agent never guesses a runner. Haiku-pinned. |
| [`debugger`](agents/debugger.md) | Fixes one self-contained, reproducible failure in an isolated context: reproduce → isolate the root cause → failing test → minimal fix. It leaves all changes uncommitted for review. Sonnet-pinned. |
| [`docs-writer`](agents/docs-writer.md) | Writes grounded technical docs in an isolated context: READMEs, analysis write-ups (methods → results → caveats), docstrings under the clean-code comment discipline, and general guides. It reads the code first, flags unverified claims, and never commits. Sonnet-pinned. |

## Commands

The slash commands for Claude Code live in [`commands/`](commands/). The generated Gemini TOML
commands live in [`runtimes/gemini/commands/`](runtimes/gemini/commands/), and they pass user
arguments through `{{args}}`. This repo has no command adapter for Codex. In Codex, you invoke the
reusable workflows as skills.

| Command | Description |
|---------|-------------|
| [`/deferred`](commands/deferred.md) | Triage `specs/deferred_items.md` in the current project. It groups the unticked items by theme. Then it sorts each item into retire, quick fix, plan, design, or hold, so that the ceremony matches the item. Only items that record an open design decision go to brainstorming. The triage itself is read-only. On the user's selection, the command retires or quick-fixes items, ticks them with a dated suffix, and routes the rest to writing-plans or brainstorming. The plan-completion protocol still ticks the items that a plan implements. |
| [`/fix-issue`](commands/fix-issue.md) | Fix a GitHub issue end to end: `gh issue view` → classify → an offered worktree and a fix branch → systematic-debugging + TDD + verification → a PR that links `Fixes #N`. It hands the last step to `finishing-a-development-branch` (the PR path), so the backlog gate and the review step run before the push. It fixes bugs only, and it routes a feature-shaped issue to `brainstorming`. Without `gh` or a GitHub remote, it stops gracefully. |
| [`/license-audit`](commands/license-audit.md) | Audit the current repo's licensing and attribution. It runs the repo's mechanical gates where they exist. Then it makes judgment checks: NOTICE ↔ artifact sync, LICENSE consistency, flags for copyleft and NonCommercial (NC) compatibility, and the risk of uncredited adaptations. Read-only. |

## Hooks

Hook scripts live in [`hooks/`](hooks/). They are Claude Code hooks, not cross-runtime config. They
fall into two groups, which install differently:

- The **project tooling hooks** (`ruff-fix.sh`, `ruff-check.sh`, `uv-guard.sh`) are **templates for
  your Python/uv work repos**, not config for this repo. You copy each one into a target repo and
  register it in *that* repo's `.claude/settings.json`.
- The **read-only agent guard** (`readonly-agent-guard.py`) is an agent contract hook. It enforces
  the contract of the five read-only agents (see [Agents](#agents)). You install it once, globally,
  in `~/.claude`.

| Hook | Event | What it does |
|------|-------|--------------|
| [`ruff-fix.sh`](hooks/ruff-fix.sh) | `PostToolUse` (`Write`/`Edit`) | Runs `uv run ruff check --fix` + `ruff format` on the edited `*.py`. It is best-effort: `PostToolUse` fires *after* the write and cannot undo it. |
| [`ruff-check.sh`](hooks/ruff-check.sh) | `Stop` | Runs `uv run ruff check .`. Exit 2 feeds back to Claude whatever `--fix` could not resolve. `stop_hook_active` guards it against loops. When ruff cannot run, it exits 1 with "ruff unavailable", which does not block. |
| [`uv-guard.sh`](hooks/uv-guard.sh) | `PreToolUse` (`Bash`) | Blocks `pip install` and bare `python` / `pytest`, and injects the `uv …` form instead. Escape hatch: `no-uv-guard` anywhere in the command. |
| [`readonly-agent-guard.py`](hooks/readonly-agent-guard.py) | `PreToolUse` (`Bash`) | For the five read-only agents, denies Bash commands that change files or git state, such as `git checkout`, `git stash`, `git reset`, and `sed -i`. For every other agent, and for the main session, it exits at once and does nothing. Install it globally, by symlink. Then run [`probe-readonly-guard.sh`](hooks/probe-readonly-guard.sh) once, because a wrong path or a missing execute bit fails open. |

The three project tooling hooks read the hook JSON payload from stdin with `jq`. The guard is
Python and needs no `jq`. To block, a hook uses **exit 2**, which feeds stderr back to Claude, or
it prints a JSON deny decision, as the guard does. Exit 1 only logs, unless the hook sets
`"onFailure": "block"` (2.1.295+). That setting has no effect on a `Stop` hook such as
`ruff-check.sh`. A shell-form `PreToolUse` or `PermissionRequest` command hook on Windows without
Git Bash (2.1.299+) also blocks when it fails, unless it sets `shell` to powershell, which still
fails open.

> [!WARNING]
> **Do not install the project tooling hooks globally, and do not wire them into this repo.** A hook registered in `~/.claude/settings.json` fires in *every* project, including non-Python ones. Also, `agent-skills` itself has no root `pyproject.toml`. Its bundled scripts run on `uv run --with` inline deps. So `ruff check` would have no config to run against, and `uv-guard.sh` would fight the very invocation that the repo intends. Install them per work repo instead. The read-only agent guard is the exception: it is global by design, and it acts only on the five read-only agents.

[`hooks/README.md`](hooks/README.md) has the details for both groups. It gives the copy-in
procedure, the settings JSON to merge, and an optional permission allowlist that stops the `uv`
forms from prompting in manual permission mode. It also gives the guard's global install and tests,
and each script's known limits. One notable limit: `uv-guard.sh` is a command-word heuristic, not a
shell parser.

## Rules

Rule files live in [`rules/`](rules/). They hold standing conventions that load automatically, with no skill invocation. Claude Code loads a project's `.claude/rules/*.md` natively. A rule with a `paths:` frontmatter glob loads only when a matching file is read, written or edited. A rule without frontmatter loads at session start. (Native loading was verified against Claude Code 2.1.218.)

This repo keeps rule sources in `rules/`. A path-scoped rule applies here through a committed relative symlink from `.claude/rules/`. The user-level rule applies here, as in every project, from `~/.claude/rules/`:

| Rule | Scope | What it injects |
|------|-------|-----------------|
| [`clean-code-python.md`](rules/clean-code-python.md) | `**/*.py` | Python guardrails, loaded on `.py` reads, writes and edits (a compaction summarizes them away): single quotes, 4-space indent, Polars over pandas, method-style Polars expressions, lazy evaluation, NumPyro+JAX, and named constants (G25). It cross-references the `clean-code` catalog by rule code. |
| [`write-with-asd-ste100.md`](rules/write-with-asd-ste100.md) | every session, user-level | The everyday writing habits of the `write-with-asd-ste100` skill, for replies and for prose files written for people. It also carries the label rule, and a pointer to the skill for rewrites, agent-facing text and strict STE. |

Rules here ship project-level. Commit `7aa454f` made that decision when it added the Python rule. To use a path-scoped rule in another project, copy it into that repo's `.claude/rules/`. (User-level `~/.claude/rules/` also loaded in the 2.1.218 probe. See that commit's message.)

`write-with-asd-ste100.md` is the one exception. It shapes every reply and every prose file, and an "all output" rule only works at user level. So `install.py` places it in `~/.claude/rules/`, for Claude Code only: Codex and Gemini get the skill without the rule. It is not linked into this repo's `.claude/rules/`, because a second copy there would load it twice in this repo.

## Installation

Clone the repository somewhere stable:

```bash
git clone https://github.com/lowmason/agent-skills.git ~/agent-skills
```

Skills that bundle scripts run them with `uv run`, which reads each script's dependencies from its
own header. Install [uv](https://docs.astral.sh/uv/) before you use those skills. Each one names uv
in its `compatibility` field. The installer itself needs only `python3`.

Then run the installer for one runtime or for all three. It installs every skill, plus that
runtime's supported agents and commands:

```bash
cd ~/agent-skills
python3 install.py codex
python3 install.py gemini
python3 install.py claude
# or: python3 install.py all
```

Symlinks are the default, so edits to installed skills are live. Run the installer again after a
pull that adds skills, agents, or commands. It is idempotent for symlinks that already point at the
matching item in this checkout. It refuses to overwrite any other existing file or directory. It
checks every destination before it writes, so a conflict installs nothing and lists every
conflicting path at once. Useful options:

```bash
python3 install.py codex --skill bayesian-workflow                # just this skill; repeat --skill as needed
python3 install.py claude --skill finishing-a-development-branch  # plus its dependencies (see below)
python3 install.py codex --skill bayesian-workflow --companions   # the skill plus Codex's agents
python3 install.py claude --rule write-with-asd-ste100           # the user-level rule and the skill it names
python3 install.py claude --no-rules                              # everything except the user-level rules
python3 install.py claude --no-companions                         # every skill, no agents or commands
python3 install.py all --dry-run                                  # inspect without writing
python3 install.py gemini --copy                                  # frozen copies instead of symlinks (see below)
python3 install.py all --check                                    # list links into this repo whose source is gone
```

`--check` installs nothing. A renamed, archived or removed skill leaves its link behind, and a
normal install never looks at it. `--check` lists each link in the runtime's directories that points
into this repository at a source that is gone. It exits 1 when it finds one. It never removes a
link, so you delete the stale ones yourself.

`--skill` also installs what the named skills cannot work without, and what those need in turn.
That means the sibling skills whose scripts or files they use, and the `/deferred` command where
the runtime has commands (Claude Code, Gemini CLI). For example,
`--skill finishing-a-development-branch` brings `writing-plans`, `requesting-code-review`, and
`/deferred`. `--skill derive-roadmap` brings `writing-plans`, which `/deferred` needs, even where
the command itself is not installed (Codex, or `--no-companions`). `--skill` skips the runtime's other agents
and commands unless you add `--companions`. A full install includes every companion unless you add
`--no-companions`. That option leaves out all agents and commands, required ones included. The
table is `DEPENDENCIES` in `install.py`.

A full Claude install also places the user-level rules, today only
`write-with-asd-ste100`, in `~/.claude/rules/`. `--rule NAME` installs one of
them with the skills that it names and their dependencies. Like `--skill`, it
skips the runtime's other agents and commands unless you add `--companions`.
`--no-rules` leaves the rules out of a full Claude install. Codex and Gemini
installs place no rule. On those runtimes, `--rule` installs only the skills it
names and prints a one-line notice. The table is `USER_RULES` in `install.py`.

`--copy` installs the same skills, agents, and commands that a link install would, including any
that git ignores whole. It copies agents and commands as they are. Within a skill, it copies the
files that git keeps: tracked files, and untracked files that git does not ignore. Sometimes git
keeps none of a skill's files: there is no git, the directory is not a checkout, or git ignores the
skill whole. Then `--copy` copies everything except a fixed list of generic names from this repo's
`.gitignore`, such as caches and virtualenvs. Patterns that you add to `.gitignore` later do not
apply there. It installs nothing if anything that it would copy is a symlink, because a copy would
follow the link. It also installs nothing if it finds a nested repository or submodule, because it
cannot copy one file by file. It never replaces an existing destination, a previous copy included,
so remove old copies before you run it again.

| Runtime | Skills | Agents | Commands | Rules |
|---------|--------|--------|----------|-------|
| Claude Code | `~/.claude/skills/` | `~/.claude/agents/*.md` | `~/.claude/commands/*.md` | `~/.claude/rules/*.md` (user-level rules only) |
| Codex | `~/.agents/skills/` | `~/.codex/agents/*.toml` | — | — |
| Gemini CLI | `~/.agents/skills/` | `~/.gemini/agents/*.md` | `~/.gemini/commands/*.toml` | — |

Codex and Gemini deliberately share the cross-runtime `~/.agents/skills/`
installation. This matches [Codex's local skill discovery](https://developers.openai.com/codex/skills)
and [Gemini CLI's discovery tiers](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/using-agent-skills.md).

### Manual skill install

To link one skill manually for Codex and Gemini:

```bash
mkdir -p ~/.agents/skills
ln -s ~/agent-skills/skills/bayesian-workflow ~/.agents/skills/bayesian-workflow
```

For Claude Code, use `~/.claude/skills/` instead. To scope a skill to one project, use
`.agents/skills/` for Codex and Gemini, or `.claude/skills/` for Claude Code:

```bash
mkdir -p .agents/skills
ln -s ~/agent-skills/skills/bayesian-workflow .agents/skills/bayesian-workflow
```

### Verify

Use `/skills` in Claude Code or Codex, and `/skills list` in Gemini. In Gemini, check agents with
`/agents list` and commands with `/commands list`. After you change generated files, use the
matching `reload` command. Codex reads its TOML agents when a new session starts.

The repo also includes project instruction entrypoints. Codex reads [`AGENTS.md`](AGENTS.md).
Gemini reads [`GEMINI.md`](GEMINI.md), which imports the canonical maintainer guide.

### Claude Code hooks

The project tooling hooks break the pattern above. **Do not symlink them into `~/.claude/`**, or they fire in every project that you open (see the warning under [Hooks](#hooks)). Copy them into the work repo that wants them:

```bash
mkdir -p .claude/hooks && cp ~/agent-skills/hooks/{ruff-fix,ruff-check,uv-guard}.sh .claude/hooks/ && chmod +x .claude/hooks/*.sh
```

Then merge the `hooks` block from [`hooks/README.md`](hooks/README.md) into that repo's `.claude/settings.json`. Prefer `cp` to a symlink here. With a copy, an edit to a template cannot silently change the gates in every repo at once. Copy the hooks again when you want the update.

The read-only agent guard is the opposite case, and `install.py` does not install it. You symlink it once into `~/.claude/hooks/` and register it in `~/.claude/settings.json`, so it covers every project. A symlink keeps the guard in step with the agent files that it enforces, which are themselves symlinked from this repo. [`hooks/README.md`](hooks/README.md) gives the commands, the settings entry, and the live probe to run after the install.

### Claude Code rules

`write-with-asd-ste100.md` is user-level. A full `python3 install.py claude` places it.
`python3 install.py claude --rule write-with-asd-ste100` places it with only its skill.

The path-scoped rules are project-level, per repo:

```bash
mkdir -p <target-repo>/.claude/rules
cp ~/agent-skills/rules/clean-code-python.md <target-repo>/.claude/rules/
```

In this repo, the committed `.claude/rules/clean-code-python.md` symlink already wires the rule up. There is nothing to install.

## Credits

- **My original skills** — `develop-testing-strategy`, `validate-data`, `explore-data`, `tech-debt`, `design-architecture`, `recommend-probabilistic-model`, `recommend-visualization`, `track-model-experiments`, `tune-hyperparameters`, `creative-thinking`, `llm-wiki`, `describe-critique-methodology`, `derive-roadmap`, `deep-learning`, `evaluate-deep-learning`, `optimize-jax`, `prepare-handoff`, and `document-python-package` are my own work, MIT licensed (see [`LICENSE`](LICENSE)).
- **deep-learning**, **evaluate-deep-learning**, and **optimize-jax** — my own original work (MIT). That covers their JAX training, evaluation, execution and research-generation workflows, focused references, record contracts, prose, runnable examples and synthetic checks. The [Orchestra AI Research Skills suite](https://github.com/Orchestra-Research/AI-Research-SKILLs) is coverage inspiration, by reference to scope only. No Orchestra prose or code is adapted or reproduced. Primary documentation and papers are cited without bundled copies, model weights or datasets. CPU fixtures and the limits of the hardware and checkpoint recipes are recorded separately (see [`NOTICE`](NOTICE)).
- **Archived skills** — `archive/skills/` keeps three retired originals, `bls-data-context`, `classification-codes` and `geographic-codes`, so that one can be restored. They are not installed. They are my own work, MIT licensed. The `data/` tables in the two code skills are derived from publications of the U.S. Census Bureau, the U.S. Bureau of Labor Statistics, and the Office of Management and Budget. These are the NAICS and SOC structure and concordance workbooks, the Census occupation code lists, the county gazetteer, and the "List 1" CBSA delineation workbooks. Those publications are works of the United States Government and in the public domain under 17 U.S.C. § 105. Each code skill's `scripts/build.py` keeps the exact source bytes in `sources/` as the audit copy, with URL, sha256, and retrieval time in `MANIFEST.md`. It derives `data/` from them. The parsing code, the seed tables, the hand-curated county change log, and all prose are my own work, MIT (see [`NOTICE`](NOTICE)).
- **Cited-only sources** — `recommend-probabilistic-model` cites Kevin Murphy's *Probabilistic Machine Learning* books (CC-BY-NC-ND) by section number only. `bayesian-workflow` cites the *Bayesian Workflow* book by Gelman, Vehtari, McElreath et al. (2026) by chapter and section number only. It cites the Gelman et al. (2020), Betancourt (CC BY-NC 4.0), and Gabry et al. workflow papers by author-year. `recommend-visualization` cites the visualization literature by author-year only. No text is reproduced, and no copies are bundled (see [`NOTICE`](NOTICE)).
- **Clean-code family** — `clean-coder`, `clean-code`, and `rules/clean-code-python.md` adapt the rule-catalog concept from Robert C. Martin's *Clean Code* (Prentice Hall, 2008). They cite it **by rule code and short title only**, and they reproduce no book prose. `clean-coder` also cites Kent Beck's *Tidy First?* (O'Reilly, 2023), Martin Fowler's opportunistic-refactoring note, and John Ousterhout's *A Philosophy of Software Design* (2nd ed., 2021), by idea only (see [`NOTICE`](NOTICE)).
- **llm-wiki** — my own work (MIT). It implements the LLM-wiki pattern from [Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)'s public idea file. It adopts a simplified per-claim citation-audit form from [kfchou/wiki-skills](https://github.com/kfchou/wiki-skills). It takes both **by reference to the idea only**: no external prose or code is reproduced, and no copies are bundled. Its bundled `scripts/` are my own work under the same terms (see [`NOTICE`](NOTICE)).
- **bayesian-workflow** — adapted from [Alexandre Andorra](https://alexandorra.github.io/)'s original **PyMC** Bayesian-workflow skill (MIT licensed). I ported it to **NumPyro + JAX** and expanded the visualization guidance. Its `references/model-comparison.md` documents four `arviz_stats` APIs that the `model-evaluation` skill in pymc-labs/python-analytics-skills (Chris Fonnesbeck) pointed out. That repository ships no LICENSE text, so the skill takes the idea only and reproduces nothing from it.
- **Mancuso Lab's coding-skills** — two skills adapt material from [mancusolab/coding-skills](https://github.com/mancusolab/coding-skills) (MIT, © 2026 Mancuso Lab), and a third takes one idea from it. `bayesian-workflow`'s `references/jax-numerics.md` adapts precision and stability rules from its `jax-equinox-numerics` and `jax-project-engineering` skills. `clean-code`'s Modules category (M1–M4) adapts four rules from its `python-module-design` skill. `tech-debt`'s "Unguarded join cardinality" signal takes only the idea of the "Make join contracts explicit" rule in its `polars-data-engineering` skill. The upstream license text is in [`LICENSE-coding-skills`](LICENSE-coding-skills), and the exact scope is in [`NOTICE`](NOTICE).
- **recommend-causal-design** — its planning workflow is selectively adapted from [Robson Tigre's causal-planner](https://github.com/RobsonTigre/everyday-causal-skills) and [Alexandre Andorra's causal-inference](https://github.com/Learning-Bayesian-Statistics/baygent-skills), both MIT licensed. The method references and the memo contract are newly written. The skill cites the primary literature without reproducing or bundling it. Both full upstream notices are in [`LICENSE-causal-design-sources`](LICENSE-causal-design-sources). The exact source commits and the scope of the adaptation are in [`NOTICE`](NOTICE).
- **write-with-asd-ste100** — adapted from [danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill) (Dustin Yuchen Teng) and [prithivrajmu/asd-ste100](https://github.com/prithivrajmu/asd-ste100) (Dustin Yuchen Teng and Prithiv M U), both MIT licensed. `scripts/ste-lint.py` is danyuchn's linter, copied unchanged. The 80% style follows [a post by Andrej Karpathy](https://x.com/karpathy/status/2105819303471976479), cited by idea only. The skill cites ASD-STE100 by issue and bundles nothing from the standard or its dictionary. The skill's test record under `specs/` credits prithivrajmu's eval cases. Both full upstream notices are in [`LICENSE-write-with-asd-ste100-sources`](LICENSE-write-with-asd-ste100-sources). The exact source commits and the scope of the adaptation are in [`NOTICE`](NOTICE).
- **superpowers skills** — the 13 process skills are adapted from the [superpowers](https://github.com/obra/superpowers) project by [Jesse Vincent](https://github.com/obra), MIT licensed, © 2025. My modifications are under the same MIT terms. The [`code-reviewer`](agents/code-reviewer.md) and [`task-reviewer`](agents/task-reviewer.md) agents are distilled from the adapted `requesting-code-review` and `subagent-driven-development` reviewer templates, under the same terms. See [`LICENSE-superpowers`](LICENSE-superpowers) and [`NOTICE`](NOTICE).

## License

Everything I wrote here is MIT licensed. [`NOTICE`](NOTICE) tracks the attribution for each skill:

- **My original skills and `bayesian-workflow`** — MIT, © Lowell Mason; full text in [`LICENSE`](LICENSE). (`bayesian-workflow` is an adaptation of Alexandre Andorra's PyMC skill; its upstream notice is in [`LICENSE-andorra`](LICENSE-andorra).)
- **`recommend-causal-design`** — MIT. The adaptations are by Lowell Mason. [`LICENSE-causal-design-sources`](LICENSE-causal-design-sources) keeps the source copyrights and permission notices for Robson Tigre and Learning Bayesian Statistics.
- **`write-with-asd-ste100`** and its rule — MIT. The adaptations are by Lowell Mason. [`LICENSE-write-with-asd-ste100-sources`](LICENSE-write-with-asd-ste100-sources) keeps the source copyrights and permission notices for Dustin Yuchen Teng and Prithiv M U.
- **superpowers skills** — MIT, © 2025 Jesse Vincent ([superpowers](https://github.com/obra/superpowers)). The full text is in [`LICENSE-superpowers`](LICENSE-superpowers).
- **Mancuso Lab material** in `bayesian-workflow` and `clean-code` — MIT, © 2026 Mancuso Lab ([coding-skills](https://github.com/mancusolab/coding-skills)). The adaptations are by Lowell Mason. The full upstream text is in [`LICENSE-coding-skills`](LICENSE-coding-skills).
- **Bundled U.S. Government data** — the verbatim `sources/` audit copies in the archived `classification-codes` and `geographic-codes` (`archive/skills/`) are works of the United States Government, in the public domain under 17 U.S.C. § 105, and carry no license of mine; the `data/` tables derived from them, the build scripts, the seed tables, and all prose are MIT (see [`NOTICE`](NOTICE)).

Each skill directory also carries copies of the license files that apply to it, so a skill installed on its own keeps its notices; the root files are canonical, and `build/check_provenance.py` checks the copies.
