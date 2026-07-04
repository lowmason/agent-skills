# agent-skills

My personal collection of [agent skills](https://code.claude.com/docs/en/skills), primarily for **Claude Code**.

Each skill is a self-contained directory under [`skills/`](skills/) with a `SKILL.md` (plus any `references/` and `scripts/` it needs). Claude Code auto-discovers installed skills and loads one into context when it's relevant to what you're doing — or you can invoke it directly as a slash command.

## Layout

Skills are the center of the repo, but it also carries the other Claude Code user-level config types:

```
agent-skills/
├── skills/      # agent skills, one directory per skill (the tables below)
├── agents/      # subagent definitions (code-reviewer, task-reviewer — see Agents below)
├── commands/    # slash commands (/deferred — see Commands below)
├── hooks/       # hook scripts (scaffolding, empty for now)
├── rules/       # rule files (scaffolding, empty for now)
├── build/       # citation-verification tooling for recommend-probabilistic-model
└── specs/       # design records + implementation plans (retired work under completed/)
```

## Skills

### Mine

| Skill | Description |
|-------|-------------|
| [`bayesian-workflow`](skills/bayesian-workflow/) | Opinionated Bayesian modeling workflow with NumPyro (JAX) and ArviZ. Encodes guardrails most agents skip — prior/posterior predictive checks, LOO-PIT calibration, prior-sensitivity checks, 94% HDI, non-centered parameterizations, reproducible PRNGKey seeds — and walks the full loop from formulating a model to reporting results. *(adapted from Alexandre Andorra's PyMC skill — see Credits)* |
| [`recommend-probabilistic-model`](skills/recommend-probabilistic-model/) | Given a problem and its data, recommend a probabilistic-ML method grounded in Kevin Murphy's *Probabilistic Machine Learning* books — a thin decision-map router over 8 deep families (regression/GLMs/counts, hierarchical, time-series/state-space, GPs, factor models, classification, mixtures, graphical models) with **verified** §refs + pyprobml notebooks, a family-conditional regularization/selection step, and a structured handoff to `bayesian-workflow`. Recommends and points; it doesn't fit. |
| [`recommend-visualization`](skills/recommend-visualization/) | Given an `explore-data` profile and an intent (trend, comparison, distribution, correlation, part-to-whole, ranking, geographic, flow), recommend the right chart by conditioning on the data's *signals* — cardinality, row count, skew, panel shape, null rates — then write the code. A pure, unit-tested `(intent × signal) → ranked candidates` router that ships the **encoding map** (field → channel), grounded in perceptual theory, routing Phase-2 code to **Altair** / **matplotlib** / **plotly**. The visualization sibling of `recommend-probabilistic-model`: one recommends a model, this recommends a view — and carries through to code. |
| [`develop-testing-strategy`](skills/develop-testing-strategy/) | Design a test strategy from *invariants* (not coverage %) for web scrapers, Polars pipelines, and NumPyro/PyMC models — recorded fixtures, schema/null/key assertions, determinism, SBC-lite, golden-master parity. |
| [`validate-data`](skills/validate-data/) | QA a dataset or analysis before it ships — schema/integrity, reproducibility, benchmark reconciliation, and methodology/bias checks. Polars-first, tuned to BLS data and as-of/vintage correctness. |
| [`explore-data`](skills/explore-data/) | Profile a new dataset with Polars before analysis — null rates, key uniqueness, distributions, duplicates, quality flags, panel balance. Bundles a reusable `profile.py`. |
| [`tech-debt`](skills/tech-debt/) | Audit, categorize, and prioritize tech debt in research/data codebases; the DELETE-vs-HARDEN triage. Bundles a `scan.sh` sweep for debt signals. |
| [`design-architecture`](skills/design-architecture/) | Author or evaluate Architecture Decision Records (ADRs) for data & modeling systems (e.g. NumPyro/JAX vs PyMC, store layout, vintage data model). Bundles an ADR scaffolder. |
| [`bls-data-context`](skills/bls-data-context/) | Canonical reference for the BLS employment/wage programs (QCEW, CES, SAE, JOLTS, BED, OEWS, ECI, ECEC, CPS) — program selector, cross-cutting concepts (jobs-vs-persons, place-of-work, vintage/benchmark, units), reconciliation rules, and nine full per-program references loaded on demand. |

### Adapted from [superpowers](https://github.com/obra/superpowers) (Jesse Vincent, MIT)

Adapted from Jesse Vincent's superpowers skills — process disciplines for planning, TDD, debugging, code review, and skill authoring. I rewrote cross-skill references from the `superpowers:` plugin namespace to bare skill names, removed unused authoring scaffolding, and dropped the plugin-bootstrap skill so these work as standalone personal skills. Attribution and license: [`NOTICE`](NOTICE) and [`LICENSE-superpowers`](LICENSE-superpowers).

> [!NOTE]
> These overlap with the upstream **superpowers plugin**. If you also run that plugin, these personal copies duplicate it under the same names (bare here vs. the plugin's `superpowers:` namespace) — use one source to avoid redundancy.

| Skill | Description |
|-------|-------------|
| [`brainstorming`](skills/brainstorming/) | Explore intent, requirements, and design before any creative or build work. |
| [`writing-plans`](skills/writing-plans/) | Turn a spec into a written implementation plan before touching code. |
| [`executing-plans`](skills/executing-plans/) | Execute a written plan in a separate session with review checkpoints. |
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

## Credits

- **My original skills** — `develop-testing-strategy`, `validate-data`, `explore-data`, `tech-debt`, `design-architecture`, `bls-data-context`, `recommend-probabilistic-model`, and `recommend-visualization` are my own work, MIT licensed (see [`LICENSE`](LICENSE)).
- **Cited-only sources** — `recommend-probabilistic-model` cites Kevin Murphy's *Probabilistic Machine Learning* books (CC-BY-NC-ND) by section number only, and `bayesian-workflow` cites the Gelman/Betancourt/Gabry workflow papers (Betancourt's under CC BY-NC 4.0) by author-year — no text is reproduced and no copies are bundled (see [`NOTICE`](NOTICE)).
- **bayesian-workflow** — adapted from [Alexandre Andorra](https://alexandorra.github.io/)'s original **PyMC** Bayesian-workflow skill (MIT licensed). I ported it to **NumPyro + JAX** and expanded the visualization guidance.
- **superpowers skills** — the 13 process skills are adapted from the [superpowers](https://github.com/obra/superpowers) project by [Jesse Vincent](https://github.com/obra), MIT licensed, © 2025; my modifications under the same MIT terms. The [`code-reviewer`](agents/code-reviewer.md) and [`task-reviewer`](agents/task-reviewer.md) agents are distilled from the adapted `requesting-code-review` and `subagent-driven-development` reviewer templates, same terms. See [`LICENSE-superpowers`](LICENSE-superpowers) and [`NOTICE`](NOTICE).

## License

Everything here is MIT licensed; per-skill attribution is tracked in [`NOTICE`](NOTICE):

- **My original skills and `bayesian-workflow`** — MIT, © Lowell Mason; full text in [`LICENSE`](LICENSE). (`bayesian-workflow` is an adaptation of Alexandre Andorra's PyMC skill.)
- **superpowers skills** — MIT, © 2025 Jesse Vincent ([superpowers](https://github.com/obra/superpowers)); full text in [`LICENSE-superpowers`](LICENSE-superpowers).
