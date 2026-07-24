# agent-skills

My personal collection of [agent skills](https://code.claude.com/docs/en/skills), primarily for **Claude Code**.

Each skill is a self-contained directory under [`skills/`](skills/) with a `SKILL.md` (plus any `references/` and `scripts/` it needs). Claude Code auto-discovers installed skills and loads one into context when it's relevant to what you're doing — or you can invoke it directly as a slash command.

> [!IMPORTANT]
> **These skills are opinionated — about my environment and my process.** They work best if you share (or deliberately adopt) those opinions. Read a skill's `SKILL.md` before installing it, and edit what doesn't fit — it's all plain markdown. Two families of assumptions to know about:
>
> - **The process skills impose a spec-driven lifecycle.** `brainstorming`, `writing-plans`, `executing-plans`, and `subagent-driven-development` (plus the `/deferred` command) drive every feature through spec → plan → implementation → retirement, and will create and maintain that structure in your project: specs as markdown in `specs/`, plans in `specs/plans/<id>-<spec-name>.md` (auto-numbered), finished work retired to `specs/completed/` and `specs/plans/completed/`, and consciously-deferred work appended to `specs/deferred_items.md`. If your projects don't follow that layout, these skills will start building it.
> - **The data & modeling skills assume my stack.** Polars (not pandas), NumPyro + JAX (not PyMC), Python 3.13, and Altair/matplotlib/plotly for charts. `bls-data-context` is domain-specific to US BLS employment data, and `validate-data` is tuned to it.

## Layout

Skills are the center of the repo, but it also carries the other Claude Code user-level config types:

```
agent-skills/
├── skills/      # agent skills, one directory per skill (the tables below)
├── agents/      # subagent definitions (code-reviewer, task-reviewer — see Agents below)
├── commands/    # slash commands (/deferred — see Commands below)
├── hooks/       # deterministic gates for Python/uv work repos (see Hooks below)
├── rules/       # reusable CLAUDE.md convention fragments (see Rules below)
├── build/       # citation-verification tooling for recommend-probabilistic-model
└── specs/       # design records + implementation plans (retired work under completed/)
```

Skills, agents, and commands install into `~/.claude/` and are discovered automatically. **Hooks and rules don't** — hooks are copied per work-repo, and rules are imported by path from a project's `CLAUDE.md`. See [Installation](#installation).

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
| [`llm-wiki`](skills/llm-wiki/) | Maintain a personal research wiki (the Karpathy LLM-wiki pattern) as a citation-audited knowledge base instead of a folder of unread PDFs. A source is ingested as a `status: unverified` page; claims are promoted onto concept pages carrying inline `[slug §x]` locators; the **quarantine rule** forbids an unverified summary from ever becoming grounds for another page, and a contradiction keeps *both* claims with an entry in `open-questions.md` rather than overwriting. Every mutating operation appends to `log.md`. The wiki root (`$LLM_WIKI_ROOT`) owns its normative `SCHEMA.md`, so the skill stays generic and a second root — work vs. personal, content never crossing — reuses it unchanged. Bundles stdlib-only `bootstrap_wiki.py` (seeds a fresh root, never overwrites content), `lint_wiki.py` (mechanical gate before any status flip), and `distill_sessions.py` (turns Claude Code transcripts into ingestable capture notes), plus an [`INSTALL.md`](skills/llm-wiki/INSTALL.md) for fresh machines. |

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
| [`requesting-code-review`](skills/requesting-code-review/) | Get work reviewed when completing features or before merging. |
| [`receiving-code-review`](skills/receiving-code-review/) | Handle review feedback with rigor instead of blind agreement. |
| [`finishing-a-development-branch`](skills/finishing-a-development-branch/) | Decide how to integrate completed work (merge, PR, or cleanup). |
| [`using-git-worktrees`](skills/using-git-worktrees/) | Create an isolated workspace for feature work. |
| [`writing-skills`](skills/writing-skills/) | Create, edit, and verify agent skills. |

## Agents

Subagent definitions live in [`agents/`](agents/) and install into `~/.claude/agents/` the same way skills do (symlink or copy):

| Agent | Description |
|-------|-------------|
| [`code-reviewer`](agents/code-reviewer.md) | Read-only reviewer for diff-based reviews against a plan, spec, or requirements — dispatched by `requesting-code-review`, and by `subagent-driven-development` for its final whole-branch review (per-task reviews go to `task-reviewer`). No edit tools; inspects history via `git show`/`git diff` and reports Critical/Important/Minor findings with a merge verdict. |
| [`task-reviewer`](agents/task-reviewer.md) | Read-only task-scoped reviewer for `subagent-driven-development`'s per-task gate — checks one task's diff against its brief for spec compliance and code quality, returning both verdicts. Carries the full review contract so dispatches only need the task's brief, report, and diff paths. |

## Commands

Slash commands live in [`commands/`](commands/) and install into `~/.claude/commands/` (symlink or copy, one file per command):

| Command | Description |
|---------|-------------|
| [`/deferred`](commands/deferred.md) | Triage `specs/deferred_items.md` in the current project: group unticked items by theme, classify actionable-now vs still-blocked, and propose which deserve promotion to a new spec. Read-only — ticking stays with the plan-completion protocol. |

## Hooks

Hook scripts live in [`hooks/`](hooks/). They're **templates for your Python/uv work repos**, not config for this one — each is copied into a target repo and registered in *that* repo's `.claude/settings.json`. What they buy you: the advisory prose in a `CLAUDE.md` ("always run ruff", "use uv, not pip") becomes a deterministic gate that fires every time, for ~0 tokens, instead of an instruction the agent may or may not honor.

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

Rule files live in [`rules/`](rules/): reusable fragments of standing convention — the *advisory* layer that [`hooks/`](#hooks) enforces mechanically. A rule file is plain markdown holding one coherent set of conventions (Python style, the `specs/` layout, review expectations) kept in one place so it can be pulled into a project rather than copy-pasted into each `CLAUDE.md` and left to drift.

Rules aren't auto-discovered the way skills and commands are. A project opts in by importing the file from its own `CLAUDE.md`:

```markdown
<!-- in a project's CLAUDE.md -->
@~/.claude/rules/python-style.md
```

The import is resolved by path at load time, so an edit here reaches every project that imports the file — which is the point, and also the reason to keep each rule file narrow enough that no importing project is forced to swallow conventions it doesn't want.

## Installation

These skills install into Claude Code's user-level skills directory, `~/.claude/skills/`, where they're discovered automatically.

First, clone the repo somewhere stable and make sure the skills directory exists:

```bash
git clone https://github.com/lowmason/agent-skills.git ~/agent-skills
mkdir -p ~/.claude/skills
```

Then install whichever skills you want, with **either** of these approaches.

### Symlink (recommended)

A symlink means edits in the repo are picked up live, without restarting Claude Code — ideal if you're tracking updates or hacking on the skill yourself:

```bash
ln -s ~/agent-skills/skills/bayesian-workflow ~/.claude/skills/bayesian-workflow
```

### Copy

A copy gives you a frozen, self-contained install that won't change when the repo does:

```bash
cp -r ~/agent-skills/skills/bayesian-workflow ~/.claude/skills/bayesian-workflow
```

### Project-level install (optional)

To make a skill available only inside one project (and shareable with collaborators via that repo), put it under the project's `.claude/skills/` instead of `~/.claude/skills/`:

```bash
mkdir -p .claude/skills
ln -s ~/agent-skills/skills/bayesian-workflow .claude/skills/bayesian-workflow
```

### Verify

Inside Claude Code, run `/skills` to list discovered skills and confirm yours shows up (along with the level it loaded from). You can also invoke a skill by name, e.g. `/bayesian-workflow`.

### Agents

Subagent definitions install the same way, into `~/.claude/agents/` (one symlink per file):

```bash
mkdir -p ~/.claude/agents
ln -s ~/agent-skills/agents/code-reviewer.md ~/.claude/agents/code-reviewer.md
```

### Commands

Slash commands install the same way, into `~/.claude/commands/` (one symlink per file):

```bash
mkdir -p ~/.claude/commands
ln -s ~/agent-skills/commands/deferred.md ~/.claude/commands/deferred.md
```

### Hooks

Hooks break the pattern above — **don't symlink them into `~/.claude/`**, or they'll fire in every project you open (see the warning under [Hooks](#hooks)). Copy them into the work repo that wants them:

```bash
mkdir -p .claude/hooks && cp ~/agent-skills/hooks/{ruff-fix,ruff-check,uv-guard}.sh .claude/hooks/ && chmod +x .claude/hooks/*.sh
```

Then merge the `hooks` block from [`hooks/README.md`](hooks/README.md) into that repo's `.claude/settings.json`. Prefer `cp` over a symlink here: a copy means editing a template can't silently change the gates in every repo at once — re-copy when you actually want the update.

### Rules

Rules aren't discovered automatically, so installing them is just making them reachable by path. Symlink the directory once:

```bash
ln -s ~/agent-skills/rules ~/.claude/rules
```

Then import whichever files a project should follow from its `CLAUDE.md` (`@~/.claude/rules/<name>.md`), one line per rule file.

## Credits

- **My original skills** — `develop-testing-strategy`, `validate-data`, `explore-data`, `tech-debt`, `design-architecture`, `bls-data-context`, `recommend-probabilistic-model`, `recommend-visualization`, `track-model-experiments`, `tune-hyperparameters`, `creative-thinking`, and `llm-wiki` are my own work, MIT licensed (see [`LICENSE`](LICENSE)).
- **Cited-only sources** — `recommend-probabilistic-model` cites Kevin Murphy's *Probabilistic Machine Learning* books (CC-BY-NC-ND) by section number only, and `bayesian-workflow` cites the Gelman/Betancourt/Gabry workflow papers (Betancourt's under CC BY-NC 4.0) by author-year — no text is reproduced and no copies are bundled (see [`NOTICE`](NOTICE)).
- **llm-wiki** — my own work (MIT). It implements the LLM-wiki pattern from [Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)'s public idea file, and adopts a simplified per-claim citation-audit form from [kfchou/wiki-skills](https://github.com/kfchou/wiki-skills) — both **by reference to the idea only**; no external prose or code is reproduced and no copies are bundled. Its bundled `scripts/` are my own work under the same terms (see [`NOTICE`](NOTICE)).
- **bayesian-workflow** — adapted from [Alexandre Andorra](https://alexandorra.github.io/)'s original **PyMC** Bayesian-workflow skill (MIT licensed). I ported it to **NumPyro + JAX** and expanded the visualization guidance.
- **superpowers skills** — the 13 process skills are adapted from the [superpowers](https://github.com/obra/superpowers) project by [Jesse Vincent](https://github.com/obra), MIT licensed, © 2025; my modifications under the same MIT terms. The [`code-reviewer`](agents/code-reviewer.md) and [`task-reviewer`](agents/task-reviewer.md) agents are distilled from the adapted `requesting-code-review` and `subagent-driven-development` reviewer templates, same terms. See [`LICENSE-superpowers`](LICENSE-superpowers) and [`NOTICE`](NOTICE).

## License

Everything here is MIT licensed; per-skill attribution is tracked in [`NOTICE`](NOTICE):

- **My original skills and `bayesian-workflow`** — MIT, © Lowell Mason; full text in [`LICENSE`](LICENSE). (`bayesian-workflow` is an adaptation of Alexandre Andorra's PyMC skill.)
- **superpowers skills** — MIT, © 2025 Jesse Vincent ([superpowers](https://github.com/obra/superpowers)); full text in [`LICENSE-superpowers`](LICENSE-superpowers).
