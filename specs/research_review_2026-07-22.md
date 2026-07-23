# Claude Code Customization & Cost-Efficient Extension Development: A Practical Report for a Python/Bayesian Stack

> **⚠️ Verified corrections — appended 2026-07-23.** The items below were fact-checked
> against current official Claude Code / Anthropic docs (live web) and against the actual
> repo. The report's *conceptual architecture* is sound; several specific *figures* are
> wrong or stale, and — as its own Caveats admit — it never accessed this repo, so its
> central "21 skills" premise is inferred from a different project. Rule of thumb when
> reusing this report: **trust the architecture, re-check every number.**

## ⚠️ Corrections (verified 2026-07-23)

**Wrong / stale — fix before acting on or citing this report:**
1. **"Haiku ~15× cheaper than Opus" → ~5×.** Current Opus (4.5–4.8) is $5/$25 per MTok; Haiku 4.5 is $1/$5 → 5× on input and output. "15×" is deprecated Opus-4.1-era pricing ($15/MTok). The report contradicts itself here: its own cache-price section ($0.50 Opus read = 0.1×$5) is the *correct* branch. (~6.5× only if you also count Opus 4.7+'s denser tokenizer.)
2. **Env var `DISABLE_NONESSENTIAL_MODEL_CALLS` is misspelled** → real name is `DISABLE_NON_ESSENTIAL_MODEL_CALLS` (underscore between NON and ESSENTIAL). The other three (`ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL`, `CLAUDE_CODE_SUBAGENT_MODEL`) are correct.
3. **"17+ hook event types" undercounts** — current docs enumerate ~31 (adds SessionStart, Setup, PermissionRequest, PostToolBatch, SubagentStart, TaskCreated/Completed, StopFailure, Pre/PostCompact, SessionEnd, …). Version-dependent.
4. **Backtick-bang `` !`command` `` injection does NOT require `allowed-tools` approval.** It runs as preprocessing by default; it is gated only by the `disableSkillShellExecution` setting. (`allowed-tools` gating of `!` was legacy *slash-command* behavior.) §2 "Arguments" overstates this.
5. **"~30–45K tokens before you type" is a loaded-setup figure, not a floor.** A vanilla session is ~9–20K (mostly built-in tool defs); 30–45K needs several MCP servers + custom agents + a large CLAUDE.md/memory also loaded.
6. **"21 always-on skills → prune to 8–12" is inferred from a different repo** (`addyosmani/agent-skills`, per the Caveats). This repo has **26** skills, all deliberately symlinked live. The real listing-budget pressure is enabled *plugins* — the Airflow `data-engineering` set (~26 skills, ~2.2K tokens) — not the personal skills. Prune plugins, not skills.

**Correct, but treat as version-snapshots (drift-prone):**
- The description char-limit history (v2.1.86 = 250 → v2.1.105 = 1,536 → v2.1.129 drops-not-truncates; listing budget ~1% of window) is accurate *as of those builds* — but it is the single most version-volatile claim. Re-verify against your installed version.
- `$ARGUMENTS` **zero-based** indexing (`$0` / `$ARGUMENTS[0]` = first arg) is **confirmed correct** — the report flagged it as uncertain; it needn't have.

**Confirmed solid (no change needed):** progressive-disclosure model; all permission semantics (deny→ask→allow first-match, `:*` trailing-wildcard, word-boundary, compound splitting); hook exit-code semantics (`exit 2` blocks, `stop_hook_active`); commands-merged-into-skills; cache economics (0.1× / 1.25× / 2×); Bayesian numerics (R-hat < 1.01, bulk-ESS > 400, Vehtari et al. 2021 *Bayesian Analysis* 16(2):667–718); Haiku 4.5 = 73.3% SWE-bench Verified. The **"skills raise the floor, not the ceiling"** thesis is correct; its source is real (A. Andorra, *learnbayesstats.com*, 2026-03-23 — a blog post, not peer-reviewed).

---

## TL;DR
- **Scale ceremony to task size, not to a fixed pipeline.** Keep only 8–12 always-on skills, gate the full Goal→Brainstorm→Spec→Plan→TDD→Subagents→Review→Verify pipeline behind large/ambiguous work, and collapse it to a two-step "plan-lite → implement-with-verify" path for small changes. This is the single biggest cost lever because, per Anthropic's official best-practices doc, "Most best practices are based on one constraint: Claude's context window fills up fast, and performance degrades as it fills."
- **Move deterministic rules out of tokens and into hooks; move sometimes-relevant knowledge out of CLAUDE.md and into on-demand skills.** A PostToolUse ruff hook enforces formatting every time for ~0 tokens, where a CLAUDE.md instruction is only advisory and competes for attention. Route models per phase (Opus/opusplan for planning, Sonnet for implementation, Haiku for mechanical review/test-running); teams report 60–80% cost savings versus running Opus for everything, and a per-task breakdown shows three-tier routing at $0.98/session vs $2.02 for uniform Opus 4.6 (a 51% reduction).
- **For your JAX/NumPyro work, the highest-value guardrails are hooks and skills that prevent re-running expensive MCMC and enforce the Bayesian workflow** (prior predictive → fit → convergence diagnostics → posterior predictive), plus caching sampler outputs to disk so the agent reads results instead of re-sampling.

## Key Findings

1. **Context is the binding constraint, and every primitive is really a context-management tool.** Anthropic's guidance is explicit: "Most best practices are based on one constraint: Claude's context window fills up fast, and performance degrades as it fills." A fresh Claude Code session already consumes roughly 30K–45K tokens (system prompts, tool definitions, CLAUDE.md, skill descriptions) before you type anything, with noticeable degradation as the 200K window fills. Skills (progressive disclosure), subagents (isolated context windows), hooks (enforcement without instructions), and a lean CLAUDE.md all exist to protect that budget.

2. **Skills use three-tier progressive disclosure.** At startup only each skill's name + description load (~a few dozen tokens each); the SKILL.md body loads when triggered; bundled reference files load only when needed. Keep SKILL.md under 500 lines. The description is the trigger and does all the routing work.

3. **Custom commands have been merged into skills in current Claude Code.** A file at `.claude/commands/deploy.md` and a skill at `.claude/skills/deploy/SKILL.md` both create `/deploy`. Legacy command files still work and support the same frontmatter, but skills are now the recommended home because they support bundled files.

4. **Subagents give you isolated context + per-agent model + scoped tools** — the three levers that make delegation pay. A subagent explores in its own window and returns a 1,000–2,000 token summary instead of polluting the main conversation with tens of thousands of tokens of file reads.

5. **Hooks are deterministic; CLAUDE.md is advisory.** "A CLAUDE.md instruction says 'always run the linter.' The agent usually complies. A PostToolUse hook runs the linter after every file write, every single time, no exceptions. That gap between 'usually' and 'always' is where production systems fail."

6. **Prompt caching is automatic in Claude Code and saves 70–90% on the cached portion of repeat traffic** — but it does not shrink your context; it only makes the repeated prefix cheap. Cache-hit reads cost 0.1× base input price (a 90% discount: ~$0.10/MTok on Haiku 4.5, $0.30/MTok on Sonnet 4.6, $0.50/MTok on Opus 4.6), while a 5-minute-TTL cache write costs 1.25× base input and a 1-hour write 2×. Break-even arrives at the second cache hit; every successful read resets the 5-minute TTL, so a loop firing at least every ~5 minutes keeps its cache warm indefinitely. Caching and context-trimming are different levers that stack.

7. **Model routing is the largest direct cost lever.** `opusplan` uses Opus during plan mode then auto-switches to Sonnet for implementation; per-subagent `model:` lets Haiku handle mechanical roles. Haiku is roughly 15× cheaper per token than Opus for read-only work (file search, grep, test execution) yet Haiku 4.5 scores 73.3% on SWE-bench Verified and reaches ~90% of Sonnet 4.5's performance in published evals — so cheap mechanical delegation costs little quality.

## Details

### 1. Skills

**Structure & frontmatter.** A skill is a directory with a required `SKILL.md` (YAML frontmatter + Markdown body) plus optional `scripts/`, `references/`, and `assets/` subdirectories. Required frontmatter is `name` (lowercase, numbers, hyphens only) and `description`. The current field set (shared with commands) includes: `description`, `when_to_use`, `argument-hint`, `arguments`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `disable-model-invocation`, `user-invocable`, `context: fork`, `agent`, `hooks`, `paths`, and `shell`.

**Writing descriptions for reliable triggering.** The description is the single most important field — Claude sees only metadata when deciding what to load. Write it in third person, include *both* what the skill does and *when* to use it (concrete trigger phrases mirroring how you actually phrase requests), and front-load the key use case. Note the listing budget has changed across versions: v2.1.86 capped descriptions at 250 characters, v2.1.105 raised it to 1,536, and as of v2.1.129 Claude Code instead *drops entire low-use skill descriptions* (ranked by recency/frequency) rather than truncating, with the listing budget scaling to ~1% of the model's context window. Claude tends to **under-trigger** skills on short/simple requests, so Anthropic's own skill-creator advises making descriptions "a little bit pushy." Consider gerund naming (e.g., `running-mcmc`, `reviewing-diffs`).

**Progressive disclosure.** Keep SKILL.md small and push detail to reference files referenced by name (e.g., "For hierarchical reparameterization, see `references/noncentered.md`"). This is the mechanism that lets you install dozens of skills without startup bloat — a project with 8 skills can consume ~500 startup tokens instead of loading everything.

**Process over prose.** The strongest community finding (and the design behind addyosmani/agent-skills and the Bayesian skill work) is that skills should encode *workflows with steps, checkpoints, and exit criteria*, not reference essays. "If you put a 2,000-word essay on testing best practices into the agent's context, the agent reads it, generates plausible-looking text, and skips the actual testing. If you put a workflow there … the agent has something to do, and you have something to verify."

**Skill vs. command vs. CLAUDE.md — where knowledge belongs:**
- **CLAUDE.md**: short, *always-true* project conventions Claude can't infer (build commands, uv/ruff usage, house style deltas). Loaded every session — keep it tight.
- **Skill**: domain knowledge/workflows relevant *sometimes*; loaded on demand. Best home for your Bayesian workflow, Polars conventions, JAX gotchas.
- **Command (manual skill)**: an explicit, repeatable entry point you type (`/spec`, `/verify`). Set `disable-model-invocation: true` for side-effecting workflows.

**Pruning & tiering (your 21→8–12 migration).** The symlink-tier pattern is sound and matches an emerging community pattern: make a canonical source-of-truth directory (e.g., `.agents/skills/` or a `skills/all/` folder) hold *all* skills, and symlink only the core tier into the directory Claude actually scans (`.claude/skills/`). This keeps startup metadata lean while preserving the full library on disk. Concretely:
- **Tier 1 (always-on, 8–12):** router/dispatch skill, spec-driven-development, TDD, code-review, context-engineering, your Polars conventions, your uv/ruff conventions, the Bayesian-workflow skill.
- **Tier 2 (symlinked in per-project):** language/framework specifics only some repos need.
- **Tier 3 (on-disk, not linked):** rarely used skills, invoked manually by path when needed.
Run `/doctor` if trigger keywords start disappearing — when many skills are present, the least-used skills' descriptions are dropped first to fit the listing budget.

### 2. Slash commands

Command files live in `.claude/commands/` (project) or `~/.claude/commands/` (personal); file name without extension becomes the command (`deploy.md` → `/deploy`). They support the same frontmatter as skills — most usefully `allowed-tools` (e.g., `Bash(git diff:*), Bash(git commit:*)`), `argument-hint` (`[issue-number]`), `description`, and `model`.

**Arguments.** `$ARGUMENTS` expands to the full argument string. Indexed access uses **zero-based** `$ARGUMENTS[0]`/`$0` for the first argument, `$1` for the second (note: this contradicts many third-party guides that treat `$1` as the first argument — verify against your installed version, as there is an open docs issue on this ambiguity). Named arguments via the `arguments:` frontmatter list map to positions in order. Dynamic context injection with `` !`command` `` runs a shell command before the prompt is sent (the command must be pre-approved in `allowed-tools`).

**When commands beat skills.** Use a command when you want a deterministic, user-triggered entry point with a fixed sequence — especially side-effecting workflows (`/commit`, `/deploy`, `/run-mcmc`) where you don't want model auto-invocation. Commands compose: a command can spell out "spin up the planning subagent, then the review subagent" to pipeline work in a fixed order.

### 3. Subagents / custom agents

**Definition files** live in `.claude/agents/*.md` (project) or `~/.claude/agents/` (personal), with frontmatter: `name`, `description`, `tools` (comma-separated; omit to inherit all), `model` (`opus`/`sonnet`/`haiku`/`inherit`), and optionally `permissionMode`, `disallowedTools`, MCP servers, hooks, max turns, skills, effort, and background/isolation behavior.

**Scope tools per role (principle of least privilege):**
- Reviewers/auditors: `Read, Grep, Glob` — analyze without modifying.
- Researchers: add `WebFetch, WebSearch`.
- Implementers: `Read, Write, Edit, Bash, Glob, Grep`.
"A documentation agent doesn't need Bash. A code review agent doesn't need Write."

**Model per role.** Cheap mechanical roles (test-running, formatting checks, mechanical review, classification) → Haiku (≈15× cheaper than Opus, ~90% of Sonnet's performance on eval). Implementation → Sonnet. Planning/architecture/adversarial correctness review → Opus. This is where per-agent `model:` earns its keep.

**When subagents genuinely help:** (a) large read-heavy investigation whose file reads would pollute main context; (b) verification in a *fresh* context (a reviewer that never saw the reasoning that produced the code grades it more honestly); (c) parallel fan-out across independent files. Each subagent returns a condensed summary (~1–2k tokens) while its exploration (tens of thousands of tokens) stays isolated.

**When subagents burn tokens without benefit:** trivial single-file edits; tasks where the summary loses information the main agent then has to re-derive; over-spawning teammates (token usage scales roughly with team size — shut them down when done). A reviewer *asked* to find gaps will always find some; instruct it to flag only correctness/requirement gaps to avoid over-engineering.

### 4. Rules (CLAUDE.md, settings.json, permissions)

**CLAUDE.md discipline.** Include: non-guessable bash commands, style deltas from defaults, test instructions, repo etiquette, project-specific architecture decisions, env quirks, common gotchas. Exclude: anything Claude can read from code, standard language conventions, detailed API docs (link instead), frequently-changing info, self-evident practices. The litmus test per line: *"Would removing this cause Claude to make mistakes? If not, cut it."* Bloated CLAUDE.md files cause Claude to ignore your actual instructions.

**Hierarchy (load order, broad → specific; concatenated, not overridden):** managed policy (`/Library/Application Support/ClaudeCode/CLAUDE.md`, `/etc/claude-code/CLAUDE.md`, or `C:\Program Files\ClaudeCode\CLAUDE.md`) → user (`~/.claude/CLAUDE.md`) → project (`./CLAUDE.md` or `./.claude/CLAUDE.md`) → local (`./CLAUDE.local.md`, gitignored). All discovered files are concatenated (not overridden); within a directory, `CLAUDE.local.md` is appended after `CLAUDE.md`. Files above the working directory load fully at launch; subdirectory CLAUDE.md files load on demand — so per-directory files are a good home for module-specific rules in a monorepo. `.claude/rules/*.md` without a `paths` field load at launch alongside `.claude/CLAUDE.md`; add a `paths` glob to make a rule load only for matching files. (There is also an auto-memory mechanism at `~/.claude/projects/<project>/memory/MEMORY.md`, whose first 200 lines / 25KB load each session.)

**settings.json precedence (highest → lowest):** managed → command-line args → local (`.claude/settings.local.json`) → project (`.claude/settings.json`) → user (`~/.claude/settings.json`).

**Permissions merge (they do NOT override):** if a tool is denied at any level, no other level can allow it. Rules evaluate in order **deny → ask → allow**, first match wins. Syntax is `Tool` or `Tool(specifier)`:
- `Bash(uv run:*)` — the `:*` suffix is equivalent to a trailing wildcard (`Bash(uv run *)`), matching `uv run` + anything. (The `:*` form is only recognized at the *end* of a pattern.)
- Word boundary matters: `Bash(ls *)` matches `ls -la` but not `lsof`; `Bash(ls*)` matches both.
- File rules use gitignore-style paths: `Read(./.env)`, `Read(./secrets/**)`, `//abs/path` (double slash for filesystem root), `~/home/path`.
- Compound commands are split on `&&`, `||`, `;`, `|`, etc. — each subcommand must match independently (up to 5 rules per compound command).
- Enterprise lock: `allowManagedPermissionRulesOnly` (managed settings only) prevents user/project settings from defining any allow/ask/deny rules.

### 5. Hooks

**Lifecycle events.** Claude Code supports 17+ event types; the workhorses are `PreToolUse` (can block: exit code 2 denies the action), `PostToolUse` (validate/format after; cannot undo the edit but can feed stderr back to the model), `Stop`/`SubagentStop` (exit 2 forces continued work — check `stop_hook_active` to avoid loops), `UserPromptSubmit`, and `SessionStart`. Configure in settings.json with a `matcher` regex over tool names and a nested `hooks` array. Handler types: command (shell), prompt (single-turn LLM), and agent.

**Deterministic enforcement as a cheap alternative to instructions.** Instead of spending tokens telling Claude "always format with ruff," a PostToolUse hook does it every time for free. Instead of "never use pip," a PreToolUse hook exits 2 on `pip install` and injects "use `uv add`" into context. This is the core cost-efficiency move: convert advisory prose into deterministic gates.

**Pitfalls:** PostToolUse hooks run *after* the edit (best-effort, can't undo — pair with a Stop hook running `ruff check .` for unfixable errors); hooks must send blocking messages to stderr and use exit 2 (exit 1 only logs); a single entry-point dispatcher avoids per-event performance penalties; keep hook scripts fast since they run inline. UV single-file scripts (`.claude/hooks/*.py` with inline dependency declarations) keep hook logic isolated from your project's dependency tree.

### Resource / Cost Efficiency

**Context management techniques (in priority order):**
1. **`/clear` between unrelated tasks** — stop paying input tokens for stale history. After two failed corrections on the same issue, `/clear` and restart with a better prompt beats a long polluted session.
2. **Plan mode** to separate exploration from execution — but the docs are explicit that "plan mode is useful, but also adds overhead… If you could describe the diff in one sentence, skip the plan."
3. **`/compact`** while the cache is still warm (within ~5 min of last message); if idle longer, `/clear` and restart instead, because compacting a cold cache re-processes the entire context.
4. **Lean CLAUDE.md + progressive-disclosure skills** to keep the always-loaded footprint small.
5. **Subagents for investigation** so exploration reads don't hit main context.
6. **Tool-result clearing / context editing** for long-horizon runs (Anthropic ships tool-result clearing as one of the "safest, lightest-touch" forms of compaction).

**Prompt caching implications.** It's automatic and you generally shouldn't try to add caching on top of Claude Code's own sessions (system prompts, tool defs, and history are already cached). To keep the cache warm: front-load stable content, batch context into one initial load, and avoid editing early context mid-session (which invalidates the cached prefix). Cache-hit reads are 0.1× base input price; break-even is the second read.

**Model routing.** Default to Sonnet; use `opusplan` so planning gets Opus reasoning and implementation runs at Sonnet rates; drop to Haiku for mechanical subagents. Pin models via `ANTHROPIC_DEFAULT_OPUS_MODEL` / `ANTHROPIC_DEFAULT_SONNET_MODEL` and set a cheaper subagent default via `CLAUDE_CODE_SUBAGENT_MODEL`.

**Cost monitoring.** Use `/usage` (session token stats; note the dollar figure is a local estimate, not your bill) and `/context` to confirm what loaded. The community `ccusage` tool and a custom status line give continuous visibility; establish a baseline before optimizing. `DISABLE_NONESSENTIAL_MODEL_CALLS=1` cuts background token use.

**When each pipeline phase earns its cost:**
| Phase | Keep when… | Skip/collapse when… |
|---|---|---|
| **Goal** | Always (one line) | Never skip — it's cheap |
| **Brainstorm** | Approach is genuinely uncertain | You can describe the solution already |
| **Specification** | Multi-file, cross-cutting, or you'll hand off to a fresh session | Single-file/localized change |
| **Plan** | Modifies multiple files or unfamiliar code | One-sentence diff |
| **TDD** | Logic/behavior changes | Pure formatting, docs, config |
| **Subagents** | Read-heavy research or fresh-context review | Trivial edits |
| **Review** | Correctness-critical or unattended runs | You watched every step of a tiny change |
| **Verify** | **Always** — a runnable check (tests/build) is what lets you walk away | Never skip; it's the cheapest insurance |

### Python-stack-specific recommendations

**Hooks for ruff (deterministic).** PostToolUse hook on `Write|Edit` for `*.py`:
```bash
#!/usr/bin/env bash
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path')
if [[ "$file_path" == *.py ]] && [[ -f "$file_path" ]]; then
  uv run ruff check --fix --quiet "$file_path" 2>/dev/null
  uv run ruff format --quiet "$file_path" 2>/dev/null
fi
exit 0
```
Pair with a Stop hook running `uv run ruff check .` to catch unfixable (non-auto-fix) rules each turn.

**uv-first enforcement.** A PreToolUse hook on `Bash` that exits 2 when it sees `pip install`, bare `python `, or `pytest` without `uv run`, injecting the corrected form (`uv add`, `uv run`, `uv run pytest`). Belt-and-suspenders: also state it once in CLAUDE.md ("This project uses uv and ruff exclusively; never call pip/black/flake8/isort/pylint"), and add permission allowlists like `Bash(uv run:*)`, `Bash(uv add:*)`, `Bash(uv sync:*)`.

**Where conventions belong (evidence-based):** deterministic, checkable rules (formatting, import style, uv usage) → **hooks + ruff config in pyproject.toml** (most reliably followed). Judgment conventions that can't be linted (Polars method-style expressions, single quotes as a deliberate deviation, two-space indent) → a **skill** with concrete before/after examples, reinforced by ruff settings where possible. Only the shortest always-true facts → CLAUDE.md.

**Polars conventions skill.** Encode your house style as canonical examples, e.g.:
```python
result = (
  df
  .filter(pl.col('value').ge(0))
  .filter(pl.col('flag').eq(True))
  .group_by('key')
  .agg(pl.col('value').sum())
)
```
Note that ruff can enforce single quotes (`quote-style = 'single'`) and 2-space indent (`indent-width = 2`) via `pyproject.toml`, but `.eq()`/`.ge()` over `==`/`>=` is a semantic preference a linter won't catch — that's exactly what the skill's examples are for.

**pytest / TDD.** The most important lever is giving Claude a runnable check. Encode "write the failing test first, run it, watch it fail, implement, watch it pass" as a TDD skill with exit criteria, and prefer running single tests over the whole suite for performance (a documented CLAUDE.md tip). A Stop hook that runs the relevant test file closes the loop deterministically.

**Agent-assisted scientific computing (JAX/NumPyro/Blackjax/ArviZ).** This is the area needing the most bespoke guardrails:
- **Never let the agent re-run expensive MCMC casually.** Cache `arviz.InferenceData` to disk (e.g., `az.to_netcdf`) immediately after sampling, and write a skill/rule instructing the agent to *read the saved InferenceData* rather than re-sample. A published stress-test of a Bayesian agent skill found the disciplined workflow "Saved InferenceData immediately after sampling, before any post-processing… one crash away from losing an expensive MCMC run" — bake that in.
- **Enforce the Bayesian workflow** as a skill: prior predictive check → fit → convergence diagnostics → posterior predictive check → model comparison (LOO/WAIC). Use the strict **R-hat < 1.01** threshold (and bulk-ESS > 400 for 4×1000-iteration chains) per Vehtari, Gelman, Simpson, Carpenter & Bürkner (2021), "Rank-normalization, folding, and localization: An improved R̂ for assessing convergence of MCMC," *Bayesian Analysis* 16(2):667–718 — not the outdated 1.1/1.05. The same stress test showed a skill "makes the floor higher but doesn't always raise the ceiling": it enforces steps but can miss subtle modeling choices (it hard-coded `Normal(0,1)` priors where a regularized horseshoe prior was warranted, and missed an identifiability trap). **Implication:** keep an expert in the loop for prior choice and identifiability; use the skill to guarantee the mechanical steps.
- **Long-running sampling jobs**: run them as explicit user-invoked commands (`disable-model-invocation: true`), consider background execution, set a deterministic (and descriptive, traceable) seed rather than a bare `42`, and have the agent verify numerics (R-hat, divergence counts, BFMI, ESS) from saved output rather than re-fitting.
- Use a cheap model (Haiku/Sonnet) for the mechanical diagnostic-reading and plotting; reserve Opus for model specification and interpreting pathologies.

## Recommendations

**Stage 1 — Prune and tier now (this week).**
1. Cut always-on skills from 21 to a core 8–12 using the symlink structure: canonical `.agents/skills/` (or `skills/`) source of truth, symlink only Tier-1 into `.claude/skills/`. Keep in Tier 1: a router/dispatch skill, spec-driven-development, TDD, code-review, context-engineering, Polars-conventions, uv-ruff-conventions, Bayesian-workflow.
2. Audit CLAUDE.md line-by-line with the "would removing this cause a mistake?" test. Move sometimes-relevant content into skills. Target a CLAUDE.md that's mostly bash commands + a handful of style deltas.
3. Verify with `/context` and `/doctor` that startup footprint dropped and no trigger keywords are being dropped from the listing budget.

**Stage 2 — Convert advisory rules to hooks (this week).**
4. Add the PostToolUse ruff hook + Stop `ruff check .` hook.
5. Add the PreToolUse uv-enforcement hook and the matching permission allowlist.
6. Add a PreToolUse deny for dangerous/expensive operations (e.g., block accidental full-suite re-runs or MCMC re-sampling scripts unless user-invoked).

**Stage 3 — Restructure the pipeline into tiers (next).**
7. Implement three workflow paths behind a router skill that picks based on task size (see proposal below).
8. Set `opusplan` as your default working mode; define Haiku-backed `test-runner` and `mechanical-reviewer` subagents and a Sonnet `implementer`; reserve an Opus `planner`/`adversarial-reviewer`.

**Stage 4 — Instrument and iterate.**
9. Stand up `ccusage` + a status line; capture a per-task-type baseline (small fix vs. full build).
10. Treat skills like code: when Claude under/over-triggers, refine the *description*; when it ignores a rule, the file is probably too long or the rule belongs in a hook.

**Benchmarks that change the plan:**
- If startup context runs high (a fresh session already sits near 30–45K tokens; watch for climbing beyond that) or `/doctor` reports dropped skill descriptions → prune Tier 1 further.
- If Sonnet implementation quality on your Bayesian models is inadequate → promote implementation to Opus for those specific tasks only (not globally).
- If review subagents generate over-engineering churn → tighten the reviewer prompt to correctness-only, or drop the review phase for small tasks.
- If a convention is followed <90% of the time via CLAUDE.md/skill → make it a hook or a ruff rule.

**Proposed tiered pipeline:**
- **Path A — Micro (typo, log line, rename, config, docstring):** Goal → implement → Verify (hook-run tests/lint). No spec, plan, TDD, subagents, or review. Sonnet or Haiku.
- **Path B — Standard (single feature, few files, clear approach):** Goal → brief Plan (plan mode, `opusplan`) → TDD → implement (Sonnet) → Verify. Add a Haiku test-runner subagent. Skip full Spec and Brainstorm; skip Review unless correctness-critical.
- **Path C — Full (large/ambiguous/cross-cutting build, new model architecture):** the complete Goal→Brainstorm→Spec→Plan→TDD→Subagents→Review→Verify. Interview-to-SPEC.md, then a *fresh session* to implement. Opus planner, Sonnet implementer, Haiku mechanical reviewer, Opus adversarial correctness reviewer. Verify always.

A router skill (with a "pushy" description covering "small change / quick fix / large feature / new model") selects the path; the human can always override by invoking the path command directly. Expect this tiering plus model routing to land in the range others report — roughly 50–80% cost reduction versus running the full pipeline on Opus for everything, with the rigor preserved where it matters (spec precision, TDD on behavior changes, and an always-on verification step).

## Caveats
- **I could not directly access `github.com/lowmason/agent-skills`** (it did not surface in search indexes, and the fetch tool only permits URLs returned by search). Recommendations about your specific implementation are inferred from your task description and from closely comparable public repos — notably addyosmani/agent-skills, which implements a near-identical lifecycle pipeline and the symlink/tier and "process-over-prose" patterns, and published Bayesian-workflow agent-skill writeups. Validate the specifics against your actual repo.
- **Claude Code changes weekly.** Field names, model aliases, defaults, and even the skill-listing budget mechanism shift between versions (e.g., the merger of commands into skills; the 250→1,536-char→drop-entire-description evolution; zero- vs. one-based `$N` argument indexing). Confirm against your installed version's `/help` and the live docs.
- **Model/pricing specifics** (which alias resolves to which model, exact per-token prices) depend on your provider and date; treat cited ratios as directional. Cited cache prices are Anthropic list rates for Haiku 4.5 / Sonnet 4.6 / Opus 4.6.
- **Skills raise the floor, not the ceiling.** For Bayesian modeling especially, an enforced workflow prevents skipped steps but will not catch subtle prior/identifiability errors — keep expert review for modeling decisions.
- **The `$N` zero-based indexing** in current docs contradicts many third-party guides and older doc versions; test argument substitution in your version before relying on it in commands.