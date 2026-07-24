# Claude Code Customization Guide

**Skills · slash commands · subagents · rules · hooks — built and run on a token budget**

> Facts in this guide were verified against the official Claude Code documentation (code.claude.com/docs) in July 2026, on the Claude Code 2.1.x line. Claude Code changes quickly: items marked ⚠ are the most version-sensitive — confirm them against your installed version (`claude --version`, `/doctor`) before depending on exact numbers or field names.

## 1. The organizing constraint: context

Everything in this guide follows from one fact: **the context window fills up fast, and performance degrades as it fills.** Every token spent on configuration is a token unavailable for the task, and every always-loaded instruction competes for attention with the code in front of the model.

A session starts paying before you type anything:

| Component | When it loads | Cost profile |
|---|---|---|
| System prompt + built-in tool definitions | Always, at startup | A few thousand tokens; fixed |
| CLAUDE.md files (managed → user → project → local) | Always, at startup | Fully yours to control — keep lean |
| Rules files without a `paths` field | Always, at startup | Add `paths` globs to make them lazy |
| Skill listing (each skill's name + description) | Always, at startup | Budgeted at ~1% of the context window ⚠ |
| Auto-memory `MEMORY.md` | Always (first 200 lines / 25 KB) | Keep it an index; push detail to topic files |
| MCP tool schemas | Deferred by default via tool search ⚠ | The big variable on loaded setups |
| Skill bodies, `references/`, subdirectory CLAUDE.md, path-scoped rules | On demand | Near-free until actually used |
| Conversation history + tool results | Grows every turn | Managed with `/clear`, `/compact`, subagents |

Run `/context` to see your actual breakdown and `/usage` for token spend; `/doctor` warns about problems such as skill-listing pressure. **Measure before optimizing.**

Each customization mechanism is, at bottom, a context-management tool:

- **Hooks** enforce rules deterministically for ~0 tokens.
- **Skills** load knowledge only when it's relevant (progressive disclosure).
- **Subagents** do heavy reading in an isolated window and return a short summary.
- **Rules with `paths`** load only when matching files are touched.
- **CLAUDE.md** is the only always-loaded prose you fully control — spend it like cash.

## 2. Choosing the right mechanism

| The guidance is… | Put it in… | Why |
|---|---|---|
| Deterministic and machine-checkable ("always format", "never use pip") | A hook (plus linter config) | Runs every time, costs no tokens, can't be ignored |
| A hard access boundary ("never read `.env`", "no destructive git") | Permission rules in `settings.json` | Enforced before the model acts |
| Short, always-true, not inferable from code (build commands, style deltas) | CLAUDE.md | Always loaded — reserve it for what's always relevant |
| Relevant only when touching certain files | A rule file with `paths` | Lazy-loads on match |
| Sometimes-relevant knowledge or a multi-step workflow | A skill | Loads on demand; can bundle scripts and references |
| A repeatable entry point you trigger deliberately (`/deploy`, `/release`) | A skill with `disable-model-invocation: true` | Invocable, never auto-fired |
| Read-heavy, parallelizable, or fresh-eyes work | A subagent | Isolated context; only a summary returns |

The dividing principle: **instructions are advisory; hooks are deterministic.** A CLAUDE.md line saying "always run the linter" is usually followed. A `PostToolUse` hook runs the linter every time, no exceptions. Whenever a rule is checkable by a program, moving it from prose into a hook (or linter config) frees tokens and closes the compliance gap in one move — it is the single highest-leverage conversion in this guide.

## 3. Skills

A skill is a directory with a `SKILL.md` (YAML frontmatter + Markdown body) plus optional supporting files:

```
my-skill/
├── SKILL.md          # frontmatter + instructions (keep the body well under 500 lines)
├── references/       # deep detail, loaded only when needed
└── scripts/          # executable helpers Claude runs instead of re-deriving logic
```

### Where skills live

| Location | Applies to | Precedence |
|---|---|---|
| Enterprise managed skills | Org-wide | Highest |
| `~/.claude/skills/<name>/` | All your projects | ↓ |
| `.claude/skills/<name>/` | The project | ↓ |
| Nested `.claude/skills/` in subdirectories | That subdirectory (lazy; also addressable as `subdir:name`) | ↓ |
| Plugin `skills/` | Wherever the plugin is enabled | Lowest |

Same-name skills shadow lower-precedence ones. Symlinks are followed — keeping a skills repo elsewhere and symlinking each skill into `~/.claude/skills/` gives you version control with live edits.

### Frontmatter reference ⚠

| Field | Effect |
|---|---|
| `name` | Display name; the directory name is what defines `/name` invocation |
| `description` | The router — drives auto-invocation. Combined with `when_to_use`, capped at 1,536 chars |
| `when_to_use` | Extra trigger context appended to the description (shares the cap) |
| `argument-hint` | Autocomplete hint, e.g. `[issue-number]` |
| `arguments` | Named positional args usable as `$name` in the body |
| `allowed-tools` | Tools pre-approved for the turn the skill runs (clears next user message) |
| `disallowed-tools` | Tools removed while the skill is active |
| `model` / `effort` | Per-skill model and reasoning-effort override (respects `availableModels`) |
| `context: fork` | Run the body in an isolated subagent instead of the main conversation |
| `agent` | Which agent type executes a forked skill (default `general-purpose`) |
| `background` | For forked skills: `false` blocks the turn for the result; `true` (default) runs in background ⚠ |
| `disable-model-invocation` | `true` = only manual `/name` invocation — use for side-effecting workflows |
| `user-invocable` | `false` = hidden from the `/` menu; Claude can still auto-invoke |
| `paths` | Globs restricting when the skill is auto-loaded |
| `hooks` | Hooks scoped to the skill's lifetime (same JSON shape as settings; supports `once`) |
| `shell` | `bash` (default) or `powershell` for `` !`command` `` preprocessing |

### The description is the router

When deciding what to load, Claude sees only each skill's name and description — the description does all the routing work:

- Write it in **third person**, stating both *what* the skill does and *when* to use it.
- Pack it with **concrete trigger phrases** that mirror how you actually phrase requests.
- Front-load the primary use case; the cap is 1,536 characters including `when_to_use`.
- Skills **under-trigger** on short requests more often than they over-trigger — when that happens, make the description pushier and more explicit; when a skill fires too often, narrow it.

### The listing budget ⚠

The always-loaded skill listing is budgeted at roughly **1% of the model's context window**. When you exceed it, Claude Code does not truncate descriptions — it **drops entire descriptions, least-invoked skills first** (and under heavy pressure drops skills from the listing altogether). A skill whose description was dropped effectively stops auto-triggering.

- `/doctor` shows the listing cost and the biggest contributors.
- `skillListingBudgetFraction` in settings raises the budget (e.g. `0.02` for 2%).
- `skillOverrides` can demote individual skills to `"name-only"` or `"off"`.
- Disable unused plugins — a plugin's whole skill set lands in the listing.

### Progressive disclosure

Three tiers keep skills nearly free until used: the listing (name + description, always loaded) → the `SKILL.md` body (loaded on invocation) → bundled files (loaded only when the body points at them). Exploit tier three deliberately: keep the body short and push depth into `references/`, named explicitly in prose ("For the edge cases, read `references/edge-cases.md`").

Write the body as **process, not prose**. A 2,000-word essay gets skimmed and paraphrased; a numbered workflow with steps, checkpoints, and exit criteria gets executed — and gives you something verifiable. Bundle deterministic logic as scripts in `scripts/` rather than describing it and hoping the model re-derives it correctly.

### Arguments and dynamic context

| Substitution | Meaning |
|---|---|
| `$ARGUMENTS` | Everything typed after `/name` |
| `$0`, `$1`, … | Positional args — **zero-based** (`$0` is the first argument) ⚠ |
| `$name` | Named argument from the `arguments` frontmatter list |
| `${CLAUDE_SKILL_DIR}` | The skill's own directory (also usable inside `allowed-tools`) |
| `${CLAUDE_PROJECT_DIR}` | Project root |
| `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}` | Session metadata |
| `\$` | Escapes a literal dollar sign |

`` !`command` `` (inline) or a ```` ```! ```` fenced block runs a shell command **once, at render time, before Claude sees the content**, and splices in the output — useful for injecting `git status`, dates, or issue metadata. It is preprocessing, not an agentic tool call, and is governed by the `disableSkillShellExecution` setting rather than by `allowed-tools`.

### Iterating on skills

Treat skills like code with observable failure modes:

| Symptom | Fix |
|---|---|
| Doesn't trigger when it should | Pushier, more concrete description; add the phrases you actually used |
| Triggers when it shouldn't | Narrow the description; add `paths`; consider `disable-model-invocation` |
| Loads but gets followed loosely | Body too long or too essay-like — restructure as steps with exit criteria |
| One rule keeps being skipped | That rule is probably checkable — move it to a hook |

A skill **raises the floor, not the ceiling**: it reliably prevents skipped steps, but it does not upgrade judgment. Keep human review on the judgment calls (design choices, priors, tradeoffs) and let skills guarantee the mechanical ones.

## 4. Slash commands

Commands have been **merged into skills**. A file at `.claude/commands/deploy.md` and a skill at `.claude/skills/deploy/SKILL.md` both create `/deploy`, support the same frontmatter, and behave identically; on a name collision the skill wins. Built-ins like `/help`, `/model`, and `/compact` are CLI-native, not files.

Use a bare command file when the whole thing is one prompt with no supporting files — it's a skill without the directory. The moment you want `references/`, `scripts/`, or forked execution, promote it to a skill directory. Either way, set `disable-model-invocation: true` on anything side-effecting (`/commit`, `/deploy`, `/run-expensive-job`) so it fires only when you type it.

## 5. Subagents

Subagent definitions are Markdown files in `~/.claude/agents/` (personal) or `.claude/agents/` (project): frontmatter plus a system prompt in the body. They deliver three levers at once — **an isolated context window, a per-agent model, and a scoped tool set**.

### Frontmatter reference ⚠

| Field | Effect |
|---|---|
| `name` | Unique lowercase-hyphenated ID |
| `description` | Drives delegation — write it like a skill description, with concrete triggers |
| `tools` | Allowlist (omit to inherit all); `Agent(worker, researcher)` restricts which subagents it may spawn |
| `disallowedTools` | Subtractive alternative to `tools` |
| `model` | `sonnet` \| `opus` \| `haiku` \| `fable` \| full ID \| `inherit` (default) |
| `effort` | `low` … `max` reasoning effort for this agent |
| `permissionMode` | `default`, `acceptEdits`, `plan`, etc. — parent modes may take precedence |
| `maxTurns` | Hard cap on agentic turns |
| `skills` | Skills whose **full content is preloaded** at start — costly; only for what the role always needs |
| `mcpServers` | MCP servers available to the agent (inline defs or refs to the parent's) |
| `hooks` | Lifecycle hooks scoped to the agent |
| `memory` | `user` \| `project` \| `local` — persistent memory scope for cross-session learning |
| `background` | Default `true` (runs as background task); `false` blocks the turn for the result ⚠ |
| `isolation` | `worktree` runs it in a disposable git worktree (auto-cleaned if unchanged) |
| `color`, `initialPrompt` | Display color; auto-submitted first turn when run as a main session via `--agent` |

### Scope tools to the role

Least privilege keeps agents focused and safe:

- **Reviewers / auditors**: `Read, Grep, Glob` — analyze without modifying.
- **Researchers**: add `WebFetch, WebSearch`.
- **Implementers**: `Read, Write, Edit, Bash, Glob, Grep`.

A documentation agent doesn't need `Bash`; a review agent doesn't need `Write`.

### Route models by role

Haiku is ~5× cheaper than Opus per token ($1/$5 vs $5/$25 per MTok) yet scores 73.3% on SWE-bench Verified — cheap delegation costs little quality on mechanical work. A sensible default split:

- **Haiku**: test-running, formatting checks, mechanical review, classification, search/exploration.
- **Sonnet**: implementation.
- **Opus**: planning, architecture, adversarial correctness review.

`CLAUDE_CODE_SUBAGENT_MODEL` sets a default subagent model globally ⚠; the per-agent `model` field overrides it.

### Isolation mechanics — and when delegation pays

A subagent starts from its own system prompt and environment details, not the parent's conversation (whether CLAUDE.md loads depends on the agent type ⚠). Its exploration — possibly tens of thousands of tokens of file reads — stays in its own window; only a compact summary returns. Subagents maintain their own prompt caches on the 5-minute TTL.

Delegation **pays** for: (a) read-heavy investigation whose file dumps would pollute the main context; (b) verification in a fresh context — a reviewer that never saw the reasoning that produced the code grades it honestly; (c) parallel fan-out across independent workstreams.

Delegation **burns tokens** on: trivial single-file edits; tasks where the summary loses details the main agent must then re-derive; over-spawning (cost scales with team size). A reviewer *asked* to find problems will always find some — instruct reviewers to flag only correctness and requirement gaps.

## 6. Rules: CLAUDE.md, rules files, settings, permissions

### CLAUDE.md discipline

Include: non-guessable build/test commands, style deltas from language defaults, repo etiquette, environment quirks, genuine gotchas. Exclude: anything readable from the code, standard conventions, API documentation (link instead), fast-changing details, self-evident practice.

The per-line litmus test: **"Would removing this cause a mistake?"** If not, cut it. A bloated CLAUDE.md doesn't just waste tokens — it dilutes attention until the instructions that matter get ignored.

### Hierarchy and loading

Files load broad → specific and are **concatenated, never overridden**: managed policy → `~/.claude/CLAUDE.md` → project `CLAUDE.md` (or `.claude/CLAUDE.md`) → `CLAUDE.local.md` (personal, gitignored). Subdirectory CLAUDE.md files are lazy — they load when Claude works with files in that subtree, which makes them the right home for module-specific guidance in a monorepo.

`@path/to/file` inside CLAUDE.md inlines another file at load time (max 4 hops; escape with backticks to mention a path without importing it).

### Rules files

`.claude/rules/*.md` (project) and `~/.claude/rules/*.md` (personal) hold focused rule files:

- **Without `paths`**: loaded at session start, alongside CLAUDE.md.
- **With `paths` globs** (`**` wildcards and brace expansion supported): loaded lazily, only when Claude touches matching files — the cheap way to carry per-area conventions.

Subdirectory organization and symlinked shared rules both work.

### Auto memory

Claude Code keeps per-project memory in `~/.claude/projects/<project>/memory/`. The first 200 lines / 25 KB of `MEMORY.md` load every session; topic files load on demand. Keep `MEMORY.md` an index of one-line pointers and let the detail live in topic files.

### Settings precedence and permission rules

`settings.json` resolves highest-to-lowest: **managed → command-line args → `.claude/settings.local.json` → `.claude/settings.json` → `~/.claude/settings.json`**.

Permissions **merge across levels** — a deny anywhere wins; no other level can re-allow it. Evaluation order is `deny → ask → allow`, first match wins. Syntax details worth memorizing:

- `Bash(uv run:*)` — the trailing `:*` matches `uv run` plus anything after it (only valid at the end of a pattern).
- Word boundaries matter: `Bash(ls *)` matches `ls -la` but not `lsof`; `Bash(ls*)` matches both.
- Compound commands are split on `&&`, `||`, `;`, `|` — each part must match independently.
- File rules use gitignore-style paths: `Read(./.env)`, `Read(./secrets/**)`, `//abs/path` (filesystem root), `~/path`.

Pair permission allowlists with hooks: the allowlist makes `uv run …` frictionless, the hook makes `pip install` impossible.

## 7. Hooks

Hooks are shell commands (or prompts/agents) that the harness executes at lifecycle events. They are the deterministic layer: instead of spending tokens instructing "always format with ruff," a `PostToolUse` hook formats every write, every time, for free.

### Events ⚠

Current builds expose ~33 events; these are the workhorses:

| Event | Fires | Exit 2 blocks? |
|---|---|---|
| `PreToolUse` | Before a tool call | ✅ blocks the call; JSON can also allow/deny/rewrite input |
| `PostToolUse` | After a tool succeeds | ✅ blocks the rest of the turn; stderr feeds back to Claude |
| `PostToolUseFailure` | After a tool fails | — informational |
| `UserPromptSubmit` | On prompt submit, before processing | ✅ blocks the prompt; stdout can inject context |
| `PermissionRequest` | When a permission dialog would appear | via JSON `decision.behavior: allow\|deny` |
| `Stop` | When Claude finishes a turn | ✅ forces continued work (capped at 8 consecutive blocks ⚠) |
| `SubagentStart` / `SubagentStop` | Around subagent runs | — |
| `SessionStart` | Session begins/resumes | — stdout becomes session context |
| `PreCompact` / `PostCompact` | Around compaction | — |
| `ConfigChange` | Settings/skills change mid-session | ✅ |
| `FileChanged` | A watched file changes on disk | — |
| `SessionEnd` | Session terminates | — |

### Exit codes and JSON control

- **Exit 0** — success; stdout may be plain text (becomes context on `SessionStart`/`UserPromptSubmit`) or structured JSON.
- **Exit 2** — block, on blockable events; **stderr is the feedback channel** shown to Claude. On non-blockable events stderr is shown but execution continues.
- **Other exits** — non-blocking error, first stderr line surfaces in the transcript.

JSON on stdout unlocks finer control: universal fields (`continue`, `suppressOutput`, `systemMessage`) plus event-specific `hookSpecificOutput` — `permissionDecision` / `updatedInput` on `PreToolUse`, `updatedToolOutput` on `PostToolUse`, `decision` / `reason` / `additionalContext` on `UserPromptSubmit` and `Stop`. Stop hooks receive `stop_hook_active: true` in their input JSON once the block cap is near — **check it and exit 0 to avoid infinite loops**.

### Handler types ⚠

| Type | Runs | Default timeout |
|---|---|---|
| `command` | A shell command | 600s (lower for some events) |
| `prompt` | A single-turn Claude call returning `{ok, reason}` | 30s |
| `agent` | A multi-turn subagent verifier | 60s |
| `http` / `mcp_tool` | POST to a URL / call an MCP tool | 600s |

### Configuration

Hooks live in any settings level (user / project / local / managed), in plugins, and in **skill or agent frontmatter** (scoped to that skill's or agent's lifetime; supports `once: true`). Per-hook fields: `matcher` (exact name, `A|B` list, or regex over tool/event names), `if` (permission-rule syntax over tool arguments, e.g. `Bash(git *)`), `timeout`, `statusMessage`. `disableAllHooks: true` switches everything off for debugging.

### Patterns

**1. Post-edit formatter** — `PostToolUse` on `Write|Edit`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{ "type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/format.sh" }]
      }
    ]
  }
}
```

```bash
#!/usr/bin/env bash
# format.sh — auto-format Python files after every write
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')
if [[ "$file_path" == *.py && -f "$file_path" ]]; then
  ruff check --fix --quiet "$file_path" 2>/dev/null
  ruff format --quiet "$file_path" 2>/dev/null
fi
exit 0
```

**2. Pre-tool blocker with a corrective message** — `PreToolUse` on `Bash`; the stderr text steers Claude to the right alternative:

```bash
#!/usr/bin/env bash
cmd=$(cat | jq -r '.tool_input.command // empty')
if [[ "$cmd" == *"pip install"* ]]; then
  echo "This project uses uv. Run 'uv add <package>' instead of pip install." >&2
  exit 2
fi
exit 0
```

**3. Stop-gate verification** — a `Stop` hook that runs the project's check (lint, tests) and exits 2 with the failure output on stderr forces Claude to fix before finishing. Read `stop_hook_active` from the input JSON and exit 0 when set.

**4. Session context injection** — a `SessionStart` command hook whose stdout (sprint state, open tickets, environment status) is added to context — dynamic context without editing CLAUDE.md.

### Pitfalls

- `PostToolUse` runs *after* the edit — it can fix or report, not prevent. Pair it with a `Stop` gate for rules that must hold at turn end.
- Blocking requires **stderr + exit 2**; writing the message to stdout or exiting 1 only logs it.
- Hooks run inline — keep them fast, or the session drags on every event.
- Many events + many rules → route through a single dispatcher script instead of N config entries.
- For Python hook logic, single-file scripts with inline dependency declarations (`uv run`) keep hook deps out of your project environment.

## 8. Running lean: the token-budget playbook

### Know your numbers first

`/context` (what's loaded), `/usage` (session tokens and estimated cost — a local estimate, not your bill), `/doctor` (listing-budget pressure). The status line can render live `current_usage` including cache reads/writes. For continuous tracking: OpenTelemetry (`CLAUDE_CODE_ENABLE_TELEMETRY=1` exports `claude_code.token.usage` and `claude_code.cost.usage`) or the community `ccusage` tool. Establish a baseline before optimizing anything.

### Session hygiene

- **`/clear` between unrelated tasks** — stale history is pure input-token overhead. After two failed corrections on the same bug, `/clear` and re-prompt beats a polluted session.
- **`/rewind` to abandon a wrong path** — truncates back to an earlier turn whose prefix is still cached; cheaper than compacting.
- **`/compact` at natural breaks**, not mid-task. Guide it (`/compact focus on the test failures`) or set a standing `# Compact instructions` section in CLAUDE.md. Auto-compact fires near the window limit on its own.
- **Plan mode is cache-friendly** (its instructions append after the cached prefix) but adds process overhead — if you can describe the diff in one sentence, skip the plan.

### Caching: automatic, but don't fight it

Claude Code caches in three layers (system prompt + tools / project context / conversation). Economics per MTok of base input: cache **reads cost 0.1×**, 5-minute-TTL **writes 1.25×**, 1-hour writes 2× — a warm cache pays for itself from the second request. TTL depends on how you authenticate ⚠: **subscription plans get 1-hour TTL automatically; API-key and cloud-provider auth default to 5 minutes** (`ENABLE_PROMPT_CACHING_1H=1` opts in to 1h).

What invalidates the cache mid-session ⚠: `/model`, `/effort`, `/fast`, connecting/disconnecting MCP servers (when schemas load upfront), toggling plugins, denying a tool, and version upgrades. `/compact` rebuilds only the conversation layer. The practical rule: **pick your model, effort, and server set at session start and leave them alone**; front-load stable context and avoid editing CLAUDE.md or settings mid-session.

### Model routing

Match the model to the phase, not the session:

- **Default to Sonnet-class** for routine implementation; escalate deliberately rather than idling on Opus.
- **`opusplan`** runs Opus in plan mode and Sonnet in execution — strong reasoning where it counts, cheaper tokens for the long implementation tail. (Each phase switch is a cache miss; on long tasks the routing still wins.)
- **Haiku for mechanical subagents** (see §5) — this is where per-agent `model:` earns its keep.
- **Raise `/effort` before escalating the model.** The diagnostic order for disappointing output: missing context → effort → model.
- **Fast mode (`/fast`)** ⚠ is the same Opus at ~2× price ($10/$50 per MTok) for higher output speed — a latency lever, not a capability one.

Pinning and defaults: the `model` setting or `ANTHROPIC_MODEL` picks the session model; `ANTHROPIC_DEFAULT_OPUS_MODEL` / `_SONNET_MODEL` / `_HAIKU_MODEL` / `_FABLE_MODEL` control what each alias resolves to; `CLAUDE_CODE_SUBAGENT_MODEL` sets the subagent default; `availableModels` (+ `enforceAvailableModels`) restricts the picker. Background/auxiliary traffic can be reduced with `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` (older builds: `DISABLE_NON_ESSENTIAL_MODEL_CALLS=1`) ⚠.

List prices (July 2026, per MTok) ⚠:

| Model | Input | Output | Cache read (0.1×) | Cache write 5m / 1h |
|---|---|---|---|---|
| Opus 4.8 | $5.00 | $25.00 | $0.50 | $6.25 / $10.00 |
| Sonnet 4.6 | $3.00 | $15.00 | $0.30 | $3.75 / $6.00 |
| Haiku 4.5 | $1.00 | $5.00 | $0.10 | $1.25 / $2.00 |

(Sonnet 5 lists at $3/$15 with introductory $2/$10 pricing through 2026-08-31. Batch API runs at 50% of list.)

### MCP hygiene

- Tool schemas are **deferred by default**: only tool names (~a hundred tokens) load upfront; full schemas load on demand via tool search. `ENABLE_TOOL_SEARCH` tunes this (`auto` = load schemas only if they fit in ~10% of the window; `false` = all upfront; per-server `alwaysLoad: true` exempts a server) ⚠.
- `MAX_MCP_OUTPUT_TOKENS` caps tool-result size; oversized results are written to disk and referenced instead of inlined.
- Audit `/mcp` and remove servers you don't use in this project.
- Prefer a CLI (`gh`, `aws`, `gcloud`) over an equivalent MCP server — a CLI has zero schema cost and hooks/permissions apply to it uniformly.

### Scale ceremony to task size

A full Goal → Brainstorm → Spec → Plan → TDD → Subagents → Review → Verify pipeline earns its cost on large, ambiguous work and burns tokens on small fixes. Per-phase:

| Phase | Keep when… | Skip/collapse when… |
|---|---|---|
| Goal | Always — it's one line | Never |
| Brainstorm | The approach is genuinely uncertain | You can already describe the solution |
| Spec | Multi-file, cross-cutting, or handing off to a fresh session | Single-file, localized change |
| Plan | Multiple files or unfamiliar code | One-sentence diff |
| TDD | Logic or behavior changes | Formatting, docs, config |
| Subagents | Read-heavy research or fresh-context review | Trivial edits |
| Review | Correctness-critical or unattended runs | You watched every step of a small change |
| Verify | **Always** — a runnable check is what lets you walk away | Never |

In practice this collapses into three paths:

- **Micro** (typo, rename, config, docstring): implement → verify. No spec, plan, or review.
- **Standard** (one feature, few files, clear approach): brief plan → TDD → implement → verify, with a cheap test-runner subagent.
- **Full** (large, ambiguous, cross-cutting): the whole pipeline, with the spec written in one session and implementation started fresh from the spec file — planning residue is context you don't want to pay for during execution.

### Guard expensive operations

For anything costly to recompute — long test suites, big builds, simulations, model training, data pulls:

- **Persist results to disk immediately**, then have Claude read the artifact instead of re-running the producer.
- **Gate the expensive command behind a manual skill** (`disable-model-invocation: true`) or a `PreToolUse` deny, so it never fires as a casual side effect.
- **Verify from saved output** — a skill instruction like "read the saved results file; do not re-run the job" plus a hook blocking the run command makes the cheap path the default and the expensive path deliberate.

## Further reading

Official documentation (all under `code.claude.com/docs/en/`): `skills`, `subagents`, `hooks` and `hooks-guide`, `memory` (CLAUDE.md, rules, auto-memory), `settings`, `model-config`, `context-window`, `prompt-caching`, `costs`, `monitoring-usage`, `mcp`, `fast-mode`. Current API pricing: `platform.claude.com/docs/en/about-claude/pricing`.
