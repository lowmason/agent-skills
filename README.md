# agent-skills

My personal collection of [Agent Skills](https://agentskills.io/specification) for
**Claude Code, Codex, and Gemini CLI**.

Each skill is a self-contained directory under [`skills/`](skills/) with a
`SKILL.md` (plus any `references/`, `scripts/`, or bundled `data/` tables it
needs). All three runtimes discover the same skill source and load the full body
only when its description matches the task or you invoke it explicitly.

> [!IMPORTANT]
> **These skills are opinionated — about my environment and my process.** They work best if you share (or deliberately adopt) those opinions. Read a skill's `SKILL.md` before installing it, and edit what doesn't fit — it's all plain markdown. Three assumptions to know about:
>
> - **The process skills impose a spec-driven lifecycle.** `brainstorming`, `writing-plans`, `executing-plans`, and `subagent-driven-development` (plus the `/deferred` command) drive every feature through spec → plan → implementation → retirement, and will create and maintain that structure in your project: specs as markdown in `specs/`, plans in `specs/plans/<id>-<spec-name>.md` (auto-numbered), finished work retired to `specs/completed/` and `specs/plans/completed/`, and consciously-deferred work appended to `specs/deferred_items.md`. If your projects don't follow that layout, these skills will start building it.
> - **The review steps send code to OpenAI when the Codex CLI is present.** `executing-plans`, `subagent-driven-development`, and `finishing-a-development-branch` run a read-only Codex CLI second-opinion review (`codex exec review`) whenever `codex` is on your `PATH`, which sends the branch diff to OpenAI under your Codex login. Where code egress is governed, keep `codex` off that machine or delete the step.
> - **The data & modeling skills assume my stack.** Polars (not pandas), NumPyro + JAX (not PyMC), Python 3.13, and Altair/matplotlib/plotly for charts. `bls-data-context`, `classification-codes`, and `geographic-codes` are domain-specific to US federal statistics (BLS employment programs; NAICS, SOC, and Census occupation codes; FIPS and CBSA geography), and `validate-data` is tuned to the BLS side.

## Layout

Skills are the center of the repo, but it also carries runtime-specific agent,
command, hook, and instruction assets:

```
agent-skills/
├── skills/      # agent skills, one directory per skill (the tables below)
├── agents/      # subagent definitions (reviewers + security/search/test/debug/docs — see Agents below)
├── commands/    # slash commands (/deferred, /fix-issue, /license-audit — see Commands below)
├── runtimes/    # generated Codex/Gemini agent and command adapters
├── hooks/       # deterministic gates for Python/uv work repos (see Hooks below)
├── rules/       # path-scoped rule files, loaded via .claude/rules/ (see Rules below)
├── build/       # citation-verification tooling for recommend-probabilistic-model
├── specs/       # design records + implementation plans (retired work under completed/)
└── install.py   # safe, idempotent installer for Claude, Codex, Gemini, or all three
```

The canonical skill bodies are portable. Agent manifests are generated from
[`agents/`](agents/) because the runtimes use different file formats and tool
names; Gemini command TOML is generated from [`commands/`](commands/). Claude's
hooks and path-scoped rules remain Claude-specific. See
[Installation](#installation) and the compatibility notes below.

## Skills

### Mine

| Skill | Description |
|-------|-------------|
| [`bayesian-workflow`](skills/bayesian-workflow/) | Opinionated Bayesian modeling workflow with NumPyro (JAX) and ArviZ. Encodes guardrails most agents skip — prior/posterior predictive checks, LOO-PIT calibration, prior-sensitivity checks, 94% HDI, non-centered parameterizations, reproducible PRNGKey seeds — and walks the full loop from formulating a model to reporting results. *(adapted from Alexandre Andorra's PyMC skill — see Credits)* |
| [`recommend-probabilistic-model`](skills/recommend-probabilistic-model/) | Given a problem and its data, recommend a probabilistic-ML method grounded in Kevin Murphy's *Probabilistic Machine Learning* books — a thin decision-map router over 8 deep families (regression/GLMs/counts, hierarchical, time-series/state-space, GPs, factor models, classification, mixtures, graphical models) with **verified** §refs + pyprobml notebooks, a family-conditional regularization/selection step, and a structured handoff to `bayesian-workflow`. Recommends and points; it doesn't fit. |
| [`recommend-visualization`](skills/recommend-visualization/) | Given an `explore-data` profile and an intent (trend, comparison, distribution, correlation, part-to-whole, ranking, geographic, flow), recommend the right chart by conditioning on the data's *signals* — cardinality, row count, skew, panel shape, null rates — then write the code. A pure, unit-tested `(intent × signal) → ranked candidates` router that ships the **encoding map** (field → channel), grounded in perceptual theory, routing Phase-2 code to **Altair** / **matplotlib** / **plotly**. The visualization sibling of `recommend-probabilistic-model`: one recommends a model, this recommends a view — and carries through to code. |
| [`track-model-experiments`](skills/track-model-experiments/) | Keep a per-analysis ledger of Bayesian model variants and rank them. A human-authored `experiments.md` records *what changed and why* across `churn-logistic → v2 → v3`; a bundled `compare_experiments.py` loads each variant's saved InferenceData, ranks them with `az.compare`, extracts convergence diagnostics, and stamps the winner back into the ledger — guarding the two ways the comparison goes silently wrong (variants fit to different observations, or a missing `log_likelihood` group). The iteration layer above `bayesian-workflow`: it owns the variant ledger and the stopping rule; `bayesian-workflow`'s `model-comparison.md` owns the ELPD statistics. |
| [`tune-hyperparameters`](skills/tune-hyperparameters/) | Tune model hyperparameters without leaking or overfitting — classify the *regime* first (predictive search vs. inference diagnostic), then tune the right objective with the right guard. Ships a bundled `PurgedTimeSeriesSplit` (`time_series_cv.py`): forward-chaining CV with an embargo gap and an optional label-horizon *purge*, feeding a manual, seeded **Optuna** objective (verified against the installed version) for regime-A predictive search; a thin decision table routes regime-B inference knobs (NUTS/SVI/optax) to `bayesian-workflow`. Guards **temporal** leakage only; graduates a tuned winner to a `track-model-experiments` variant row, and defers revision/vintage leakage to `develop-testing-strategy`. |
| [`creative-thinking`](skills/creative-thinking/) | Divergent target-finding for when the goal itself is fuzzy — the analysis, the estimand, the objective, or the approach space. Delivers a *map* of genuinely distinct candidate targets (sketched in ≤3 lines each, with named selection criteria and at least one candidate that escapes the map's own organizing frame) instead of converging on the first plausible one. Sorts gating questions by where the answer lives: user-held facts (data access, consuming decision) get asked first with a one-line-per-direction preview; modeling judgments are absorbed provisionally with flip-marked candidates. Runs ahead of `brainstorming`'s narrowing and `tune-hyperparameters`' mechanics; hands the picked target off unchanged. Eval-tested against a no-skill baseline (RED→GREEN, two human-reviewed iterations). |
| [`develop-testing-strategy`](skills/develop-testing-strategy/) | Design a test strategy from *invariants* (not coverage %) for web scrapers, Polars pipelines, and NumPyro/PyMC models — recorded fixtures, schema/null/key assertions, determinism, SBC-lite, golden-master parity. |
| [`validate-data`](skills/validate-data/) | QA a dataset or analysis before it ships — schema/integrity, reproducibility, benchmark reconciliation, and methodology/bias checks. Polars-first, tuned to BLS data and as-of/vintage correctness. |
| [`explore-data`](skills/explore-data/) | Profile a new dataset with Polars before analysis — null rates, key uniqueness, distributions, duplicates, quality flags, panel balance. Bundles a reusable `profile.py`. |
| [`tech-debt`](skills/tech-debt/) | Audit, categorize, and prioritize tech debt in research/data codebases; the DELETE-vs-HARDEN triage. Bundles a `scan.sh` sweep for debt signals. |
| [`design-architecture`](skills/design-architecture/) | Author or evaluate Architecture Decision Records (ADRs) for data & modeling systems (e.g. NumPyro/JAX vs PyMC, store layout, vintage data model). Bundles an ADR scaffolder. |
| [`bls-data-context`](skills/bls-data-context/) | Canonical reference for the BLS employment/wage programs (QCEW, CES, SAE, JOLTS, BED, OEWS, ECI, ECEC, CPS) — program selector, cross-cutting concepts (jobs-vs-persons, place-of-work, vintage/benchmark, units), reconciliation rules, and nine full per-program references loaded on demand. |
| [`classification-codes`](skills/classification-codes/) | The NAICS (2012, 2017, 2022) and SOC (2010, 2018) classification systems, their official vintage concordances, and the Census occupation code lists (the ACS/CPS `OCC` variable, expanded to detailed SOC) as tidy, greppable CSVs under `data/`, built from the Census/BLS workbooks by a bundled, validated `build.py` (sources archived with sha256 in `MANIFEST.md`). The SKILL.md carries the semantics agents get wrong — ranged sectors (`31-33`), SOC's trailing-zero levels, "All Other" residuals, `link_type`-routed vintage bridging with no weights — and a `references/revision-process.md` on how the ECPC and SOCPC create and revise codes (Federal Register cycle, NAICS 2027, SOC 2028). Prime directive: codes and titles come from `data/`, never from model memory. |
| [`geographic-codes`](skills/geographic-codes/) | U.S. statistical geography as interval-stamped reference tables under `data/` — FIPS states and territories, county-equivalents (counties, parishes, boroughs and census areas, independent cities, municipios, Connecticut planning regions), and CBSAs with their metropolitan divisions and CSAs — every county-equivalent and CBSA row carrying a half-open `[valid_from, valid_to)` so the question is always "valid at this reference date", never "which vintage file do I open". Built from the Census county gazetteer and OMB's seven "List 1" delineation workbooks (bulletins 13-01 through 23-01) by a bundled, validated `build.py` (sources archived with sha256 in `MANIFEST.md`); `counties.csv` is synthesized by playing a hand-curated, Census-verified `seeds/county_changes.csv` forward from 1990. The SKILL.md carries the semantics agents get wrong — CBSA ≠ MSA, metropolitan-division double-counting, independent cities outside any county, spelling corrections vs. renames, the Connecticut county retirement (87 FR 34235), NECTAs' discontinuation, and `valid_from` as the federal-statistics date rather than state law or a BLS program's adoption date — and a `references/how-geographies-are-defined.md` on OMB's qualification rules and revision clocks. Sibling of `classification-codes`, same architecture, same prime directive: codes and names come from `data/`, never from model memory, and never without a reference date. |
| [`llm-wiki`](skills/llm-wiki/) | Maintain a personal research wiki (the Karpathy LLM-wiki pattern) as a citation-audited knowledge base instead of a folder of unread PDFs. A source is ingested as a `status: unverified` page; claims are promoted onto concept pages carrying inline `[slug §x]` locators; the **quarantine rule** forbids an unverified summary from ever becoming grounds for another page, and a contradiction keeps *both* claims with an entry in `open-questions.md` rather than overwriting. Every mutating operation appends to `log.md`. The wiki root (`$LLM_WIKI_ROOT`) owns its normative `SCHEMA.md`, so the skill stays generic and a second root — work vs. personal, content never crossing — reuses it unchanged. Bundles stdlib-only `bootstrap_wiki.py` (seeds a fresh root, never overwrites content), `lint_wiki.py` (mechanical gate before any status flip), and `distill_sessions.py` (turns Claude Code transcripts into ingestable capture notes), plus an [`INSTALL.md`](skills/llm-wiki/INSTALL.md) for fresh machines. |
| [`describe-critique-methodology`](skills/describe-critique-methodology/) | Leg 1 of the methodology-critique loop: write a system- or module-level **methodological description** of a codebase — math and prose deliberately decoupled from the code (notation table, data-generating story, estimation procedure, assumptions, evaluation criteria, open questions) — carry it to a Claude Chat **Research** critique, then **synthesize** description + adjudicated critique into a house-format spec routed onward to `derive-roadmap`. Two modes (Describe / Synthesize) joined by routing headers in the artifacts themselves; bundles an advisory `check_decoupling.py`. Stats/Bayesian/nowcast scope in v1. |
| [`derive-roadmap`](skills/derive-roadmap/) | Leg 2 of the methodology-critique loop: takes a synthesized spec and the system it describes and partitions the distance between them into staged spec→plan→implementation cycles. Runs a one-time gap analysis over every numbered requirement (`references/gap-rubric.md`: implemented-as-specified / implemented-differently / missing / in-code-but-not-in-spec), sequences stages by dependency and information order rather than the spec's own priority ranking, and — unless the gaps fit a single cycle, which gets no roadmap file at all — writes a brevity-budgeted `specs/<name>-roadmap.md` (`references/roadmap-format.md`) that cites spec §-refs instead of restating them. Every stage routes onward to `brainstorming` or `writing-plans` by bare name; this skill never designs a stage. Resumes via authoritative stage stamps, and supports a first-class PARKED exit that folds unticked stages into `specs/deferred_items.md`. |

### Clean-code family (rule catalog adapted from Robert C. Martin's *Clean Code*)

Proactive-cleanup counterpart to `tech-debt`: standards applied in the flow of normal editing, bounded by consent. The rule *codes* come from Martin's Ch. 17 catalog (cited by code only — no book prose); the curation defers mechanical rules to ruff and keeps the judgment-level ones, tuned to Polars/JAX. A third artifact, the [`clean-code-python`](rules/clean-code-python.md) rule, injects the always-on Python guardrails on every `*.py` edit (see [Rules](#rules)).

| Skill | Description |
|-------|-------------|
| [`clean-coder`](skills/clean-coder/) | Opportunistic cleanup with a consent gate: in-scope fixes apply directly; anything adjacent goes through announce → list (`file:line` + rule code) → ask → apply-on-yes. Beck's *Tidy First?* supplies the spine — tidyings and behavior changes never share a commit, and a stopping rule caps the cascade, deferring bigger findings to `tech-debt`. Pressure-tested against a no-skill baseline on six gate scenarios. |
| [`clean-code`](skills/clean-code/) | The curated standards catalog `clean-coder` applies: Martin's N/F/G/C/T rules dispositioned keep / defer-to-ruff / drop, with stack-tuned examples (Polars fluent chains are not Demeter violations; `jax.lax.switch` is G23's dispatch; comments carrying design intent survive C3). Five per-category references load on demand; every fix cites its rule code. |

### Adapted from [superpowers](https://github.com/obra/superpowers) (Jesse Vincent, MIT)

Adapted from Jesse Vincent's superpowers skills — process disciplines for planning, TDD, debugging, code review, and skill authoring. I rewrote cross-skill references from the `superpowers:` plugin namespace to bare skill names, removed unused authoring scaffolding, and dropped the plugin-bootstrap skill so these work as standalone personal skills. Beyond that mechanical cleanup, I rewired the planning and execution skills around the spec-driven lifecycle described at the top of this README (the `specs/` layout, auto-numbered plans, and a plan-completion protocol that marks up the plan, logs deferred items, and retires the spec) — upstream does not impose that workflow. Attribution and license: [`NOTICE`](NOTICE) and [`LICENSE-superpowers`](LICENSE-superpowers).

> [!NOTE]
> These overlap with the upstream **superpowers plugin**. If you also run that plugin, these personal copies duplicate it under the same names (bare here vs. the plugin's `superpowers:` namespace) — use one source to avoid redundancy.

| Skill | Description |
|-------|-------------|
| [`brainstorming`](skills/brainstorming/) | Explore intent, requirements, and design before any creative or build work. |
| [`writing-plans`](skills/writing-plans/) | Turn a spec into a written implementation plan before touching code. |
| [`executing-plans`](skills/executing-plans/) | Execute a written plan directly in the current session — for tightly coupled plans or partner-requested direct execution. |
| [`subagent-driven-development`](skills/subagent-driven-development/) | Execute plans with independent tasks in the current session. |
| [`dispatching-parallel-agents`](skills/dispatching-parallel-agents/) | Fan out 2+ independent tasks with no shared state. |
| [`test-driven-development`](skills/test-driven-development/) | Write tests before implementation for any feature or bugfix. |
| [`systematic-debugging`](skills/systematic-debugging/) | Diagnose bugs and test failures methodically before proposing fixes. |
| [`verification-before-completion`](skills/verification-before-completion/) | Run verification and confirm output before claiming work is done. |
| [`requesting-code-review`](skills/requesting-code-review/) | Get work reviewed when completing features or before merging. Also carries the Codex CLI second-opinion recipe (`codex-review.md`): the plan executors run it beside `code-reviewer`, and branch finishing runs it before merge or PR. It is skipped with a notice where the `codex` CLI is absent. |
| [`receiving-code-review`](skills/receiving-code-review/) | Handle review feedback with rigor instead of blind agreement. |
| [`finishing-a-development-branch`](skills/finishing-a-development-branch/) | Decide how to integrate completed work (merge, PR, or cleanup); merge and PR are gated on a Codex second-opinion review. |
| [`using-git-worktrees`](skills/using-git-worktrees/) | Create an isolated workspace for feature work. |
| [`writing-skills`](skills/writing-skills/) | Create, edit, and verify agent skills. |

## Agents

Canonical subagent definitions live in [`agents/`](agents/). Claude loads these
files directly; generated Codex TOML and Gemini Markdown adapters live under
[`runtimes/`](runtimes/). The adapters keep the same system-prompt body, map
Gemini's tool identifiers, declare read-only sandboxes in Codex where required,
and inherit the active runtime model instead of carrying Claude model names.

| Agent | Description |
|-------|-------------|
| [`code-reviewer`](agents/code-reviewer.md) | Read-only reviewer for diff-based reviews against a plan, spec, or requirements — dispatched by `requesting-code-review`, and by `subagent-driven-development` for its final whole-branch review (per-task reviews go to `task-reviewer`). No edit tools; inspects history via `git show`/`git diff` and reports Critical/Important/Minor findings with a merge verdict. |
| [`task-reviewer`](agents/task-reviewer.md) | Read-only task-scoped reviewer for `subagent-driven-development`'s per-task gate — checks one task's diff against its brief for spec compliance and code quality, returning both verdicts. Carries the full review contract so dispatches only need the task's brief, report, and diff paths. |
| [`security-auditor`](agents/security-auditor.md) | Read-only security reviewer for a diff, branch, or repo — injection, committed secrets and credential handling, insecure deserialization, TLS verification, dependency risks. Severity-ranked findings with file:line and concrete remediation; Opus-pinned like `code-reviewer`. |
| [`explore`](agents/explore.md) | ⚠ Haiku-pinned **override of the built-in `Explore` agent** — same read-only fan-out-search contract, plus a structured output contract (`path:line` refs with relevance notes, no file dumps). The frontmatter `name: Explore` (capital E) is what shadows the built-in — resolution keys on the name field, case-sensitively; shadowing is version-sensitive (probed on Claude Code 2.1.219), so re-probe after binary updates. |
| [`test-runner`](agents/test-runner.md) | Runs one test suite in isolation and reports complete failure output — full tracebacks never truncated, warnings surfaced as findings, no diagnosis. The dispatch supplies the exact command; it never guesses a runner. Haiku-pinned. |
| [`debugger`](agents/debugger.md) | Fixes one self-contained, reproducible failure in an isolated context — reproduce → isolate the root cause → failing test → minimal fix — and leaves all changes uncommitted for review. Sonnet-pinned. |
| [`docs-writer`](agents/docs-writer.md) | Writes grounded technical docs in an isolated context — READMEs, analysis writeups (methods → results → caveats), docstrings under the clean-code comment discipline, general guides. Reads the code first, flags unverified claims, never commits. Sonnet-pinned. |

## Commands

Slash commands live in [`commands/`](commands/) for Claude. Generated Gemini
TOML commands live in [`runtimes/gemini/commands/`](runtimes/gemini/commands/)
and preserve user arguments through `{{args}}`. Codex has no equivalent command
adapter in this repo; its reusable workflows are invoked as skills.

| Command | Description |
|---------|-------------|
| [`/deferred`](commands/deferred.md) | Triage `specs/deferred_items.md` in the current project: group unticked items by theme, then sort each into retire / quick fix / plan / design / hold so the ceremony matches the item — brainstorming only for items that record an open design decision. The triage is read-only; on the user's selection it retires or quick-fixes items (ticking them with a dated suffix) and routes the rest to writing-plans or brainstorming. Plan-implemented items are still ticked by the plan-completion protocol. |
| [`/fix-issue`](commands/fix-issue.md) | Fix a GitHub issue end-to-end: `gh issue view` → classify (bugs only — feature-shaped issues route to `brainstorming`) → fix branch → systematic-debugging + TDD + verification → PR linking `Fixes #N`. Stops gracefully without `gh` or a GitHub remote. |
| [`/license-audit`](commands/license-audit.md) | Audit the current repo's licensing and attribution: run its mechanical gates where present, then judgment checks — NOTICE ↔ artifact sync, LICENSE consistency, copyleft/NC compatibility flags, uncredited-adaptation risks. Read-only. |

## Hooks

Hook scripts live in [`hooks/`](hooks/). They're **Claude Code templates for your
Python/uv work repos**, not cross-runtime config and not config for this one —
each is copied into a target repo and registered in *that* repo's
`.claude/settings.json`.

| Hook | Event | What it does |
|------|-------|--------------|
| [`ruff-fix.sh`](hooks/ruff-fix.sh) | `PostToolUse` (`Write`/`Edit`) | Runs `uv run ruff check --fix` + `ruff format` on the edited `*.py`. Best-effort: `PostToolUse` fires *after* the write and can't undo it. |
| [`ruff-check.sh`](hooks/ruff-check.sh) | `Stop` | Runs `uv run ruff check .`; exit 2 feeds whatever `--fix` couldn't resolve back to Claude. Guarded by `stop_hook_active` against loops. |
| [`uv-guard.sh`](hooks/uv-guard.sh) | `PreToolUse` (`Bash`) | Blocks `pip install` and bare `python` / `pytest`, injecting the `uv …` form instead. Escape hatch: `no-uv-guard` anywhere in the command. |

All three read the hook JSON payload from stdin with `jq`. Only **exit 2** blocks a tool call and feeds stderr back to Claude — exit 1 merely logs.

> [!WARNING]
> **Don't install these globally, and don't wire them into this repo.** A hook registered in `~/.claude/settings.json` fires in *every* project, including non-Python ones. And `agent-skills` itself has no root `pyproject.toml` — its bundled scripts run on `uv run --with` inline deps, so `ruff check` would have no config to run against and `uv-guard.sh` would fight the very invocation the repo intends. Install per work-repo instead.

[`hooks/README.md`](hooks/README.md) carries the copy-in procedure, the settings JSON to merge, an optional permission allowlist so the `uv` forms stop prompting, and each script's known limits (notably that `uv-guard.sh` is a first-token heuristic, not a shell parser).

## Rules

Rule files live in [`rules/`](rules/): standing conventions injected automatically, without a skill invocation. Claude Code loads a project's `.claude/rules/*.md` natively — a rule with a `paths:` frontmatter glob loads only when a matching file is read or edited; a rule without frontmatter loads at session start (verified against Claude Code 2.1.218).

This repo keeps rule sources in `rules/` and commits a relative symlink from `.claude/rules/` so the rules apply here too:

| Rule | Scope | What it injects |
|------|-------|-----------------|
| [`clean-code-python.md`](rules/clean-code-python.md) | `**/*.py` | Always-on Python guardrails — single quotes, 4-space indent, Polars-over-pandas, method-style Polars expressions, lazy evaluation, NumPyro+JAX, named constants (G25). Cross-references the `clean-code` catalog by rule code. |

To use a rule in another project, copy it into that repo's `.claude/rules/` (project-level is the verified mechanism; user-level `~/.claude/rules/` support is version-dependent — see the rule's commit history for probe results).

## Installation

Clone the repository somewhere stable:

```bash
git clone https://github.com/lowmason/agent-skills.git ~/agent-skills
```

Then use the installer for one runtime or all three. It installs every skill plus
that runtime's supported agents and commands:

```bash
cd ~/agent-skills
python3 install.py codex
python3 install.py gemini
python3 install.py claude
# or: python3 install.py all
```

Symlinks are the default, so repository updates are live. The installer is
idempotent for links it already owns and refuses to overwrite any other existing
file or directory. Useful options:

```bash
python3 install.py codex --skill bayesian-workflow  # one skill; repeat --skill as needed
python3 install.py all --dry-run                    # inspect without writing
python3 install.py gemini --copy                    # frozen copies instead of links
```

| Runtime | Skills | Agents | Commands |
|---------|--------|--------|----------|
| Claude Code | `~/.claude/skills/` | `~/.claude/agents/*.md` | `~/.claude/commands/*.md` |
| Codex | `~/.agents/skills/` | `~/.codex/agents/*.toml` | — |
| Gemini CLI | `~/.agents/skills/` | `~/.gemini/agents/*.md` | `~/.gemini/commands/*.toml` |

Codex and Gemini deliberately share the cross-runtime `~/.agents/skills/`
installation. This matches [Codex's local skill discovery](https://developers.openai.com/codex/skills)
and [Gemini CLI's discovery tiers](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/using-agent-skills.md).

### Manual skill install

To link one skill manually for Codex and Gemini:

```bash
mkdir -p ~/.agents/skills
ln -s ~/agent-skills/skills/bayesian-workflow ~/.agents/skills/bayesian-workflow
```

For Claude Code, use `~/.claude/skills/` instead. To scope a skill to one
project, use `.agents/skills/` for Codex/Gemini or `.claude/skills/` for Claude:

```bash
mkdir -p .agents/skills
ln -s ~/agent-skills/skills/bayesian-workflow .agents/skills/bayesian-workflow
```

### Verify

Use `/skills` in Claude or Codex and `/skills list` in Gemini. Gemini agents and
commands can be checked with `/agents list` and `/commands list`; use the
corresponding `reload` command after changing generated files. Codex reads its
TOML agents when a new session starts.

Project instruction entrypoints are included too: Codex reads [`AGENTS.md`](AGENTS.md),
while Gemini reads [`GEMINI.md`](GEMINI.md), which imports the canonical
maintainer guide.

### Claude Code hooks

Hooks break the pattern above — **don't symlink them into `~/.claude/`**, or they'll fire in every project you open (see the warning under [Hooks](#hooks)). Copy them into the work repo that wants them:

```bash
mkdir -p .claude/hooks && cp ~/agent-skills/hooks/{ruff-fix,ruff-check,uv-guard}.sh .claude/hooks/ && chmod +x .claude/hooks/*.sh
```

Then merge the `hooks` block from [`hooks/README.md`](hooks/README.md) into that repo's `.claude/settings.json`. Prefer `cp` over a symlink here: a copy means editing a template can't silently change the gates in every repo at once — re-copy when you actually want the update.

### Claude Code rules

Project-level, per repo:

```bash
mkdir -p <target-repo>/.claude/rules
cp ~/agent-skills/rules/clean-code-python.md <target-repo>/.claude/rules/
```

In this repo the committed `.claude/rules/clean-code-python.md` symlink already wires the rule up — nothing to install.

## Credits

- **My original skills** — `develop-testing-strategy`, `validate-data`, `explore-data`, `tech-debt`, `design-architecture`, `bls-data-context`, `recommend-probabilistic-model`, `recommend-visualization`, `track-model-experiments`, `tune-hyperparameters`, `creative-thinking`, `llm-wiki`, `describe-critique-methodology`, `derive-roadmap`, `classification-codes`, and `geographic-codes` are my own work, MIT licensed (see [`LICENSE`](LICENSE)).
- **Public-domain data** — the `data/` tables in `classification-codes` and `geographic-codes` are derived from U.S. Census Bureau, U.S. Bureau of Labor Statistics, and Office of Management and Budget publications (the NAICS and SOC structure and concordance workbooks, the Census occupation code lists, the county gazetteer, and the "List 1" CBSA delineation workbooks). Those publications are works of the United States Government and in the public domain under 17 U.S.C. § 105. Each skill's `scripts/build.py` keeps the exact source bytes in `sources/` as the audit copy, with URL, sha256, and retrieval time in `MANIFEST.md`, and derives `data/` from them; the parsing code, the seed tables, the hand-curated county change log, and all prose are my own work, MIT (see [`NOTICE`](NOTICE)).
- **Cited-only sources** — `recommend-probabilistic-model` cites Kevin Murphy's *Probabilistic Machine Learning* books (CC-BY-NC-ND) by section number only, and `bayesian-workflow` cites the Gelman/Betancourt/Gabry workflow papers (Betancourt's under CC BY-NC 4.0) by author-year — no text is reproduced and no copies are bundled (see [`NOTICE`](NOTICE)).
- **Clean-code family** — `clean-coder`, `clean-code`, and `rules/clean-code-python.md` adapt the rule-catalog concept from Robert C. Martin's *Clean Code* (Prentice Hall, 2008), cited **by rule code and short title only** — no book prose is reproduced. `clean-coder` additionally cites Kent Beck's *Tidy First?* (O'Reilly, 2023), Martin Fowler's opportunistic-refactoring note, and John Ousterhout's *A Philosophy of Software Design* (2nd ed., 2021) by idea only (see [`NOTICE`](NOTICE)).
- **llm-wiki** — my own work (MIT). It implements the LLM-wiki pattern from [Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)'s public idea file, and adopts a simplified per-claim citation-audit form from [kfchou/wiki-skills](https://github.com/kfchou/wiki-skills) — both **by reference to the idea only**; no external prose or code is reproduced and no copies are bundled. Its bundled `scripts/` are my own work under the same terms (see [`NOTICE`](NOTICE)).
- **bayesian-workflow** — adapted from [Alexandre Andorra](https://alexandorra.github.io/)'s original **PyMC** Bayesian-workflow skill (MIT licensed). I ported it to **NumPyro + JAX** and expanded the visualization guidance.
- **superpowers skills** — the 13 process skills are adapted from the [superpowers](https://github.com/obra/superpowers) project by [Jesse Vincent](https://github.com/obra), MIT licensed, © 2025; my modifications under the same MIT terms. The [`code-reviewer`](agents/code-reviewer.md) and [`task-reviewer`](agents/task-reviewer.md) agents are distilled from the adapted `requesting-code-review` and `subagent-driven-development` reviewer templates, same terms. See [`LICENSE-superpowers`](LICENSE-superpowers) and [`NOTICE`](NOTICE).

## License

Everything I wrote here is MIT licensed; per-skill attribution is tracked in [`NOTICE`](NOTICE):

- **My original skills and `bayesian-workflow`** — MIT, © Lowell Mason; full text in [`LICENSE`](LICENSE). (`bayesian-workflow` is an adaptation of Alexandre Andorra's PyMC skill.)
- **superpowers skills** — MIT, © 2025 Jesse Vincent ([superpowers](https://github.com/obra/superpowers)); full text in [`LICENSE-superpowers`](LICENSE-superpowers).
- **Bundled U.S. Government data** — the verbatim `sources/` audit copies in `classification-codes` and `geographic-codes` are works of the United States Government, in the public domain under 17 U.S.C. § 105, and carry no license of mine; the `data/` tables derived from them, the build scripts, the seed tables, and all prose are MIT (see [`NOTICE`](NOTICE)).
