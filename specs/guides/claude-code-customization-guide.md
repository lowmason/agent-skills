# Claude Code Customization Guide

**Skills · slash commands · subagents · rules · hooks — built and run on a token budget**

<!-- cc-guide:stamp -->
> Checked against the Claude Code docs and changelog through 2.1.289 on 2026-10-05; oldest full re-verification 2026-10-03, at 2.1.288.
<!-- /cc-guide:stamp -->

> First verified in July 2026, at Claude Code 2.1.219, 58 releases before the full re-verification at 2.1.288 against the official documentation (code.claude.com/docs) and Anthropic's pricing pages. Claude Code changes quickly: items marked ⚠ are the most version-sensitive — confirm them against your installed version (`claude --version`, `/doctor`) before depending on exact numbers or field names.

## 1. The organizing constraint: context
<!-- cc: context.overview -->

Everything in this guide follows from one fact: **the context window fills up fast, and performance degrades as it fills.** Every token spent on configuration is a token unavailable for the task, and every always-loaded instruction competes for attention with the code in front of the model.

A session starts paying before you type anything:

| Component | When it loads | Cost profile |
|---|---|---|
| System prompt + built-in tool definitions | Always, at startup | A few thousand tokens; fixed |
| CLAUDE.md files (managed → user → project → local) | Always, at startup | Fully yours to control — keep lean |
| Rules files without a `paths` field | Always, at startup | Add `paths` globs to make them lazy |
| Skill listing (each skill's name + description) | Always, at startup | Names always; descriptions share a ~1%-of-window budget, least-used dropped first ⚠ |
| Auto-memory `MEMORY.md` | Always (first 200 lines / 25 KB) | Keep it an index; push detail to topic files |
| MCP tools | Names + server instructions upfront; schemas deferred via tool search ⚠ | Small until used — the big variable again wherever deferral is off |
| Skill bodies, `references/`, subdirectory CLAUDE.md, path-scoped rules | On demand | Near-free until used — then resident in history until compaction truncates or summarizes them |
| Conversation history + tool results | Grows every turn | Managed with `/clear`, `/compact`, subagents |

Run `/context` to see your actual breakdown and `/usage` for token spend; `/doctor` estimates the skill listing's cost and flags unused skills, MCP servers, and plugins. **Measure before optimizing.**

Each customization mechanism is, at bottom, a context-management tool:

- **Hooks** enforce rules deterministically for ~0 tokens.
- **Skills** load knowledge only when it's relevant (progressive disclosure).
- **Subagents** do heavy reading in an isolated window and return a short summary.
- **Rules with `paths`** load only when matching files are touched.
- **CLAUDE.md** is the only always-loaded prose you fully control — spend it like cash.

## 2. Choosing the right mechanism
<!-- cc: mechanisms.overview -->

| The guidance is… | Put it in… | Why |
|---|---|---|
| Deterministic and machine-checkable ("always format", "never use pip") | A hook (plus linter config) | Runs every time, costs no tokens, can't be ignored |
| A hard access boundary ("never read `.env`", "no destructive git") | Permission rules in `settings.json` | Checked before every tool call; add the sandbox where a shell command could read a file without naming it |
| Short, always-true, not inferable from code (build commands, style deltas) | CLAUDE.md | Always loaded — reserve it for what's always relevant |
| Relevant only when touching certain files | A rule file with `paths` | Lazy-loads on match |
| Sometimes-relevant knowledge or a multi-step workflow | A skill | Loads on demand; can bundle scripts and references |
| A repeatable entry point you trigger deliberately (`/deploy`, `/release`) | A skill with `disable-model-invocation: true` | Invocable, never auto-fired, absent from the listing — zero standing cost |
| Read-heavy, parallelizable, or fresh-eyes work | A subagent | Isolated context; only a summary returns |

The dividing principle: **instructions are advisory; hooks are deterministic.** A CLAUDE.md line saying "always run the linter" is usually followed. A `PostToolUse` hook runs the linter every time, no exceptions. Whenever a rule is checkable by a program, moving it from prose into a hook (or linter config) frees tokens and closes the compliance gap in one move — it is the single highest-leverage conversion in this guide.

## 3. Skills
<!-- cc: skills.overview -->

A skill is a directory with a `SKILL.md` (YAML frontmatter + Markdown body) plus optional supporting files:

```
my-skill/
├── SKILL.md          # frontmatter + instructions (keep the body well under 500 lines)
├── references/       # deep detail, loaded only when needed
└── scripts/          # executable helpers Claude runs instead of re-deriving logic
```

### Where skills live
<!-- cc: skills.locations -->

| Location | Applies to | Precedence |
|---|---|---|
| Enterprise managed skills | Org-wide | Highest |
| `~/.claude/skills/<name>/` | All your projects on this machine (not cloud, routine, or Cowork sessions) | ↓ |
| `.claude/skills/<name>/` | The project | Lowest of the three |
| Nested `.claude/skills/` in subdirectories | That subdirectory — loads when Claude first reads or edits a file there | Never shadows; on a clash, address it as `dir:name` (e.g. `apps/web:deploy`) |
| Plugin `skills/` | Wherever the plugin is enabled | Never shadows — namespaced as `plugin:skill` |

Among the first three, a same-name skill shadows the lower-precedence one. Skills enabled on your claude.ai account also sync into terminal sessions signed in with that account (`~/.claude/skills/synced/`; `syncClaudeAiSkills: false` opts out) and join the listing ⚠. Symlinks are followed — keeping a skills repo elsewhere and symlinking each skill into `~/.claude/skills/` gives you version control with live edits.

### Frontmatter reference ⚠
<!-- cc: skills.frontmatter -->

| Field | Effect |
|---|---|
| `name` | Sets the `/` command shown and typed (unless another command holds it); the directory name also invokes the skill |
| `description` | The router — drives auto-invocation. Combined with `when_to_use`, capped at 1,536 chars in the listing (`skillListingMaxDescChars`) |
| `when_to_use` | Extra trigger context appended to the description (shares the cap) |
| `argument-hint` | Autocomplete hint, e.g. `[issue-number]` |
| `arguments` | Named positional args usable as `$name` in the body |
| `allowed-tools` | Tools pre-approved for the turn the skill runs (clears next user message) |
| `disallowed-tools` | Tools removed while the skill is active |
| `model` / `effort` | Per-turn model and reasoning-effort override (respects `availableModels`). A `model` that differs from the session's makes that turn a full cache miss. In auto mode, a `model` that auto mode doesn't support (Haiku) is ignored and the session model runs — the behavior since 2.1.259, which also fixed a bug that ignored skill `model:` in interactive sessions ⚠ |
| `context: fork` | Run the body in an isolated subagent that doesn't see the conversation — the instructions must stand alone |
| `agent` | Which agent type executes a forked skill (default `general-purpose`) |
| `background` | For forked skills: `false` blocks the turn for the result; `true` (default, 2.1.218+) runs in background ⚠ |
| `disable-model-invocation` | `true` = Claude never runs the skill on its own, and the skill leaves the listing entirely — use for side-effecting workflows. `/name` at the start of a message runs it; `/name` later in a message only permits Claude to run it while answering that message, so write the bare name to mention it without permitting a run ⚠ |
| `user-invocable` | `false` = Claude-only: hidden from the `/` menu, and typing `/name` won't run it |
| `paths` | Globs restricting when the skill is auto-loaded |
| `hooks` | Hooks registered when the skill is invoked; they stay active for the rest of the session (same JSON shape as settings; `once: true` is honored only here) |
| `shell` | `bash` (default) or `powershell` for `` !`command` `` preprocessing |
| `license`, `compatibility`, `metadata` | Agent Skills spec fields — accepted, not acted on. Unknown fields are ignored silently, so a misspelled field fails without an error |

### The description is the router
<!-- cc: skills.description -->

When deciding what to load, Claude sees only each skill's name and description — the description does all the routing work:

- Write it in **third person**, stating both *what* the skill does and *when* to use it.
- Pack it with **concrete trigger phrases** that mirror how you actually phrase requests.
- Front-load the primary use case; the cap is 1,536 characters including `when_to_use`.
- Skills **under-trigger** on short requests more often than they over-trigger — when that happens, make the description pushier and more explicit; when a skill fires too often, narrow it.

### The listing budget ⚠
<!-- cc: skills.listing-budget -->

The always-loaded skill listing is budgeted at roughly **1% of the model's context window** (a character budget). Every skill's name always stays listed; when the descriptions overflow, Claude Code does not truncate them — it **drops entire descriptions, least-invoked skills first**. A skill whose description was dropped stays invocable by name but rarely auto-triggers.

- `/doctor` estimates the listing cost and the biggest contributors; `/skill-doctor` shows each skill's cost and how often it's used; the `/context` Skills row shows the post-budget size.
- `skillListingBudgetFraction` in settings raises the budget (e.g. `0.02` for 2%); each entry stays capped at 1,536 characters regardless.
- `disable-model-invocation: true` takes a skill out of the listing entirely — the cheapest home for manual-only workflows.
- `skillOverrides` sets individual skills to `"name-only"` (listed without a description), `"user-invocable-only"` (hidden from Claude, still typable), or `"off"`. It doesn't reach plugin skills — manage those in `/plugin`.
- Disable unused plugins — a plugin's whole skill set lands in the listing.

### Progressive disclosure
<!-- cc: skills.progressive-disclosure -->

Three tiers keep skills nearly free until used: the listing (name + description, always loaded) → the `SKILL.md` body (loaded on invocation) → bundled files (loaded only when the body points at them). Exploit tier three deliberately: keep the body short and push depth into `references/`, named explicitly in prose ("For the edge cases, read `references/edge-cases.md`").

Tier two is not free once paid: an invoked body enters the conversation and stays for the rest of the session. After compaction, Claude Code re-attaches only the first 5,000 tokens of each invoked skill (25,000 across all of them), so put the critical instructions near the top of `SKILL.md`. The docs' context walkthrough also says the listing itself is not re-injected after `/compact` ⚠.

Write the body as **process, not prose**. A 2,000-word essay gets skimmed and paraphrased; a numbered workflow with steps, checkpoints, and exit criteria gets executed — and gives you something verifiable. Bundle deterministic logic as scripts in `scripts/` rather than describing it and hoping the model re-derives it correctly.

### Arguments and dynamic context
<!-- cc: skills.arguments -->

| Substitution | Meaning |
|---|---|
| `$ARGUMENTS` | Everything typed after `/name` |
| `$0`, `$1`, … | Positional args — **zero-based** (`$0` is the first argument; `$ARGUMENTS[0]` is the same) ⚠ |
| `$name` | Named argument from the `arguments` frontmatter list |
| `${CLAUDE_SKILL_DIR}` | The skill's own directory (also usable inside `allowed-tools`) |
| `${CLAUDE_PROJECT_DIR}` | Project root |
| `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}` | Session metadata |
| `\$` | Escapes a `$` before a digit, `ARGUMENTS`, or a declared argument name (e.g. `\$1.00`) |

`` !`command` `` (inline) or a ```` ```! ```` fenced block runs a shell command **once, at render time, before Claude sees the content**, and splices in the output — useful for injecting `git status`, dates, or issue metadata. It is preprocessing, not an agentic tool call, but it is still permission-checked: a deny rule aborts the whole invocation, and outside auto mode so does any command your rules don't allow, so pre-approve the commands in `allowed-tools`. A non-zero exit aborts the invocation too (append `|| true` where failure is an expected result). `disableSkillShellExecution` turns injection off entirely.

### Iterating on skills
<!-- cc: skills.iterating -->

Treat skills like code with observable failure modes:

| Symptom | Fix |
|---|---|
| Doesn't trigger when it should | Pushier, more concrete description; add the phrases you actually used |
| Triggers when it shouldn't | Narrow the description; add `paths`; consider `disable-model-invocation` |
| Loads but gets followed loosely | Body too long or too essay-like — restructure as steps with exit criteria |
| Followed well, then drifts after `/compact` | Compaction kept only the start of the body — re-invoke it, and move the critical rules to the top |
| One rule keeps being skipped | That rule is probably checkable — move it to a hook |

A skill **raises the floor, not the ceiling**: it reliably prevents skipped steps, but it does not upgrade judgment. Keep human review on the judgment calls (design choices, priors, tradeoffs) and let skills guarantee the mechanical ones.

## 4. Slash commands
<!-- cc: commands.overview -->

Commands have been **merged into skills**. A file at `.claude/commands/deploy.md` and a skill at `.claude/skills/deploy/SKILL.md` both create `/deploy` and take the same frontmatter (except `name` and `paths` — a command's filename is its name); on a name collision the skill wins. Most built-ins, like `/help`, `/model`, and `/compact`, are coded into the CLI rather than files (a few bundled ones are prompt-based skills) — and in a local terminal session, a skill with a built-in's name replaces it, though not its aliases.

Command files still work, but the docs now recommend a skill for new work: a lone `SKILL.md` costs the same as a command file and leaves room for `references/`, `scripts/`, or forked execution later. Either way, set `disable-model-invocation: true` on anything side-effecting (`/commit`, `/deploy`, `/run-expensive-job`) so it fires only when you type it — and stays out of the listing.

## 5. Subagents
<!-- cc: subagents.overview -->

Subagent definitions are Markdown files in `~/.claude/agents/` (personal) or `.claude/agents/` (project): frontmatter plus a system prompt in the body. They deliver three levers at once — **an isolated context window, a per-agent model, and a scoped tool set**. Same-name definitions resolve managed → `--agents` CLI JSON → project → personal → plugin: here project beats personal, the reverse of skills.

### Frontmatter reference ⚠
<!-- cc: subagents.frontmatter -->

| Field | Effect |
|---|---|
| `name` | Unique lowercase-hyphenated ID |
| `description` | Drives delegation — concrete triggers like a skill description, but every agent's description sits in context, so keep it short |
| `tools` | Allowlist (omit to inherit all, MCP tools included); `Agent(worker, researcher)` restricts spawnable types only for an agent run as the main thread (`--agent`) |
| `disallowedTools` | Subtractive alternative to `tools` (applied first when both are set) |
| `model` | `sonnet` \| `opus` \| `haiku` \| `fable` \| full ID \| `inherit`. Resolution order: a per-spawn `model` Claude passes → this field → `CLAUDE_CODE_SUBAGENT_MODEL` → the main model ⚠ |
| `effort` | `low` … `max` reasoning effort for this agent (levels vary by model) |
| `permissionMode` | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan` — ignored when the parent runs in `bypassPermissions`, `acceptEdits`, or auto mode |
| `maxTurns` | Turn cap; at the limit the output comes back marked partial and can be resumed |
| `skills` | Skills whose **full content is preloaded** at start — costly; only for what the role always needs |
| `mcpServers` | MCP servers available to the agent (inline defs or refs to the parent's); an inline server's tool descriptions stay out of the parent's context |
| `hooks` | Lifecycle hooks active only while the agent runs |
| `memory` | `user` \| `project` \| `local` — persistent memory scope for cross-session learning; auto-enables Read/Write/Edit and loads that MEMORY.md (first 200 lines / 25 KB) at every spawn |
| `background` | `true` keeps it in the background even when Claude wants the result; unset, interactive sessions already background every non-teammate spawn (fork mode, on by default) ⚠ |
| `isolation` | `worktree` runs it in a disposable git worktree (auto-cleaned if unchanged), branched from `origin/<default-branch>` — unpushed commits are absent unless `worktree.baseRef` is `"head"` |
| `omitClaudeMd` | `true` launches it without user, project, and local CLAUDE.md (managed files still load) — a cheaper spawn (2.1.271+) |
| `experimental.cacheTtl` | `5m` or `1h` prompt-cache TTL for this agent's requests (2.1.248+) ⚠ |
| `color`, `initialPrompt` | Display color; auto-submitted first turn when run as a main session via `--agent` |

### Scope tools to the role
<!-- cc: subagents.tools -->

Least privilege keeps agents focused and safe:

- **Reviewers / auditors**: `Read, Grep, Glob` — analyze without modifying.
- **Researchers**: add `WebFetch, WebSearch`.
- **Implementers**: `Read, Write, Edit, Bash`.

A documentation agent doesn't need `Bash`; a review agent doesn't need `Write`. Two catches ⚠: on macOS, Linux, and WSL, `Glob` and `Grep` are absent by default and come back only for an agent that lists them *without* `Bash` (with `Bash`, search runs through the shell); and `memory:` silently adds Read/Write/Edit, so keep it off read-only roles.

### Route models by role
<!-- cc: subagents.models -->

Haiku 4.5 lists at a quarter of Opus 5.5's per-token price ($1/$5 vs $4/$20 per MTok) and half of Sonnet 5.5's, yet scored 73.3% on SWE-bench Verified at its October 2025 launch — cheap delegation costs little quality on mechanical work. Two caveats ⚠: Haiku's window is 200K tokens against 1M for the current Fable, Opus, and Sonnet (a subagent's window follows its own model, not the parent's), and its retirement window opens 2026-10-15. A sensible default split:

- **Haiku**: test-running, formatting checks, mechanical review, classification, search/exploration.
- **Sonnet**: implementation.
- **Opus**: planning, architecture, adversarial correctness review.
- **Fable**: the hardest reasoning and long-horizon work, when Opus at high effort still falls short — at 2.5× Opus's list price.

The built-in `Explore` agent now inherits the session model rather than running on Haiku; to explore on Haiku, define your own `Explore` with `model: haiku` (it overrides the built-in). `CLAUDE_CODE_SUBAGENT_MODEL` is only a fallback since 2.1.251: an agent's `model` field and a per-spawn `model` both outrank it, and it doesn't move the built-in Explore and Plan; `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` (2.1.257+) makes it override everything ⚠.

### Isolation mechanics — and when delegation pays
<!-- cc: subagents.isolation -->

A subagent starts from its own system prompt and environment details, not the parent's conversation. Custom agents and most built-ins also load your CLAUDE.md hierarchy and a git-status snapshot at spawn; Explore and Plan skip both. The exception is a **fork** — Claude's `fork` subagent type, or `/subtask` — which inherits the entire conversation; fork mode is on by default in interactive sessions ⚠. Either way, its exploration — possibly tens of thousands of tokens of file reads — stays in its own window; only its final text returns. Subagents keep their own prompt caches on a 5-minute TTL by default, even on a subscription where the main conversation gets 1 hour (`subagentPromptCacheTtl` or `experimental.cacheTtl` changes it); a fork reuses the parent's cache.

Delegation **pays** for: (a) read-heavy investigation whose file dumps would pollute the main context; (b) verification in a fresh context — a reviewer that never saw the reasoning that produced the code grades it honestly (use a named agent, not a fork, which inherits that reasoning); (c) parallel fan-out across independent workstreams.

Delegation **burns tokens** on: trivial single-file edits; tasks where the summary loses details the main agent must then re-derive; over-spawning (cost scales with team size — the docs put agent teams at roughly 7× a standard session's tokens when teammates run in plan mode). A reviewer *asked* to find problems will always find some — instruct reviewers to flag only correctness and requirement gaps.

## 6. Rules: CLAUDE.md, rules files, settings, permissions
<!-- cc: rules.overview -->

### CLAUDE.md discipline
<!-- cc: rules.claude-md -->

Include: non-guessable build/test commands, style deltas from language defaults, repo etiquette, environment quirks, genuine gotchas. Exclude: anything readable from the code, standard conventions, API documentation (link instead), fast-changing details, self-evident practice.

The per-line litmus test: **would removing this line make Claude err?** If not, cut it. The docs' size target is under 200 lines per file. A bloated CLAUDE.md doesn't just waste tokens — it dilutes attention until the instructions that matter get ignored.

### Hierarchy and loading
<!-- cc: rules.hierarchy -->

Files load broad → specific and are **concatenated, never overridden**: managed policy → `~/.claude/CLAUDE.md` → project `CLAUDE.md` (or `.claude/CLAUDE.md`) → `CLAUDE.local.md` (personal; gitignore it yourself). CLAUDE.md files in ancestor directories of the working directory load at launch too. Subdirectory CLAUDE.md files are lazy — they load when Claude reads or edits files in that subtree, which makes them the right home for module-specific guidance in a monorepo. Lazy content lives in message history, so compaction summarizes it away; anything that must persist belongs in an always-loaded file. `AGENTS.md` is read natively since 2.1.277, but only as a fallback when no CLAUDE.md exists ⚠.

`@path/to/file` inside CLAUDE.md inlines another file at load time (max 4 hops; escape with backticks to mention a path without importing it). Imports organize a long file but don't shrink it — imported files load at launch too.

### Rules files
<!-- cc: rules.rules-files -->

`.claude/rules/*.md` (project) and `~/.claude/rules/*.md` (personal) hold focused rule files:

- **Without `paths`**: loaded at session start, alongside CLAUDE.md.
- **With `paths` globs** (`**` wildcards and brace expansion supported): loaded lazily, only when Claude reads or edits matching files — the cheap way to carry per-area conventions. Compaction summarizes them away, so a rule that must persist should drop `paths` or move to the root CLAUDE.md.

Rules are discovered recursively, so subdirectory organization works. A symlinked rule whose target lies outside the project counts as an external import: it loads only after you approve external imports for the project, and then only if it has no `paths` (2.1.284+) ⚠. Keep cross-project rules in `~/.claude/rules/` instead.

### Auto memory
<!-- cc: rules.auto-memory -->

Claude Code keeps per-project memory in `~/.claude/projects/<project>/memory/`. The first 200 lines / 25 KB of `MEMORY.md` load every session; topic files load on demand. Keep `MEMORY.md` an index of one-line pointers and let the detail live in topic files. Claude's own config directory is a protected path, but the markdown files in this memory directory are exempt, so Claude's memory writes don't wait on approval, except in a session started with `--restricted` ⚠.

### Settings precedence and permission rules
<!-- cc: rules.settings -->

`settings.json` resolves highest-to-lowest: **managed → command-line args → `.claude/settings.local.json` → `.claude/settings.json` → `~/.claude/settings.json`**.

Permissions **merge across levels** — a deny anywhere wins; no other level can re-allow it. (One exception, 2.1.287+: an installed mod that handles `tool.check` can approve a call that a deny rule or a non-managed hook refused, unless managed settings or a Team/Enterprise login apply ⚠.) Evaluation order is `deny → ask → allow`, first match wins. Syntax details worth memorizing:

- `Bash(uv run *)` — matches `uv run` plus anything after it; the older `Bash(uv run:*)` form is equivalent, but only at the end of a pattern. A runner rule approves *whatever* follows `run`.
- Word boundaries matter: `Bash(ls *)` matches `ls -la` but not `lsof`; `Bash(ls*)` matches both.
- Compound commands are split on `&&`, `||`, `;`, `|`, `|&`, `&`, and newlines: an allow rule must match every part, while a deny or ask rule fires if any part matches — even inside `$()` or a subshell.
- File rules use gitignore-style paths: `Read(./.env)`, `Read(./secrets/**)`, `//abs/path` (filesystem root), `~/path`. A single leading slash is **not** absolute: `/path` anchors at the settings file's own root.
- On Windows with Git Bash installed, any Bash deny rule, scoped or bare, from a settings file or `--disallowedTools`, also turns the PowerShell tool off for the session, since a Bash rule can't restrict PowerShell. To keep PowerShell on, set `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` or add a scoped `PowerShell(…)` rule of your own ⚠.

`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` strips credentials, recognized by variable name or value, from the environments of Bash commands, hooks, and stdio MCP servers: a layer under permission rules, not a replacement. It deliberately keeps the GitHub token variables (`GITHUB_TOKEN`, `GH_TOKEN`, and the Enterprise pair) and `HTTP_PROXY`/`HTTPS_PROXY`, even a proxy URL carrying a username and password. Remove those yourself: list the GitHub variables under `sandbox.credentials.envVars` with `"mode": "deny"`, or `"mask"` with `"injectHosts": ["api.github.com"]` so `gh` keeps authenticating (mask entries count only from user or managed settings), and keep credentials out of proxy URLs. `sandbox.credentials` covers sandboxed commands only, so hooks and MCP servers still inherit whatever the scrub leaves ⚠.

Pair permission rules with hooks. In Manual mode an allowlist makes `uv run …` frictionless; in auto mode — the default starting mode since 2.1.283 — broad rules such as package-manager run commands are set aside and a classifier reviews those calls instead (on API and Enterprise billing its calls count toward your usage) ⚠. The first session after an install or upgrade can start in another mode, and so can every run in a clean CI container or through a gateway token with no API key, since none of those has saved feature flags: set the mode explicitly there with `--permission-mode` or `defaultMode` ⚠. The hook that makes `pip install` impossible holds in every mode.

## 7. Hooks
<!-- cc: hooks.overview -->

Hooks are shell commands (or HTTP calls, MCP tool calls, prompts, or agents) that the harness executes at lifecycle events. They are the deterministic layer: instead of spending tokens instructing "always format with ruff," a `PostToolUse` hook formats every Write and Edit, every time, for free.

### Events ⚠
<!-- cc: hooks.events -->

Current builds document 33 events (the newest, `PreModelSwitch` / `PostModelSwitch`, arrived in 2.1.251); these are the workhorses:

| Event | Fires | Exit 2 blocks? |
|---|---|---|
| `PreToolUse` | Before a tool call | ✅ blocks the call; JSON can also allow/deny/ask/defer or rewrite input |
| `PostToolUse` | After a tool succeeds | — the tool already ran; stderr goes to Claude (JSON `continue: false` halts the turn) |
| `PostToolUseFailure` | After a tool fails | — informational |
| `UserPromptSubmit` | On prompt submit, before processing | ✅ blocks the prompt; stdout can inject context |
| `PermissionRequest` | When a permission dialog would appear | via JSON `decision.behavior: allow\|deny` (exit 2 is ignored) |
| `Stop` | When Claude finishes a turn | ✅ forces continued work (8 consecutive blocks at most, by default ⚠) |
| `SubagentStart` / `SubagentStop` | Around subagent runs | `SubagentStop` ✅ keeps the subagent working; `SubagentStart` can inject context |
| `SessionStart` | Session begins/resumes | — stdout becomes session context |
| `PreCompact` / `PostCompact` | Around compaction | `PreCompact` ✅ blocks compaction |
| `ConfigChange` | Settings/skills change mid-session | ✅ (except managed policy) |
| `FileChanged` | A watched file changes on disk | — |
| `SessionEnd` | Session terminates | — (1.5 s default timeout) |

### Exit codes and JSON control
<!-- cc: hooks.exit-codes -->

- **Exit 0** — success; stdout may be plain text (becomes context on `SessionStart`/`UserPromptSubmit`) or structured JSON. JSON-looking output that fails to parse is a hook error (2.1.248+).
- **Exit 2** — block, on blockable events. The message is your JSON `reason` if you give one, otherwise stderr; tool events and `Stop` show it to Claude, most other events only to the user.
- **Other exits** — non-blocking error: the action proceeds, and the first stderr line surfaces in the transcript.

JSON on stdout unlocks finer control: universal fields (`continue`, `stopReason`, `systemMessage`; `suppressOutput` is still accepted but now does nothing) plus event-specific `hookSpecificOutput` — `permissionDecision` / `updatedInput` on `PreToolUse`, `updatedToolOutput` on `PostToolUse`, `additionalContext` for injected context. `decision` / `reason` stay top-level; a top-level `additionalContext` is silently ignored. Injected text — `additionalContext`, `systemMessage`, plain stdout — is capped at 10,000 characters per hook; the overflow arrives as a file path plus a short preview. Stop hooks receive `stop_hook_active: true` whenever Claude is already continuing because of a stop hook — **check it (or the transcript) to avoid blocking on a condition that can never resolve**; the 8-block cap is only the backstop.

### Handler types ⚠
<!-- cc: hooks.handlers -->

| Type | Runs | Default timeout |
|---|---|---|
| `command` | A shell command | 600s (lower for some events) |
| `prompt` | A single-turn Claude call returning `{ok, reason}` | 30s |
| `agent` | A multi-turn subagent verifier (experimental) | 60s |
| `http` / `mcp_tool` | POST to a URL / call an MCP tool | 600s |

### Configuration
<!-- cc: hooks.configuration -->

Hooks live in any settings level (user / project / local / managed — entries merge across levels), in plugins, and in **frontmatter**: a skill's hooks register when it's invoked and stay for the rest of the session (`once: true`, honored only there, removes one after its first successful run); an agent's hooks run only while that agent does. Per-hook fields: `matcher` (plain names or `A|B` lists match exactly; anything else is a regex over the event's field — tool name, session source, agent type), `if` (permission-rule syntax over tool arguments, e.g. `Bash(git *)`; honored only on tool events — elsewhere a hook with `if` never runs), `timeout`, `statusMessage`. `disableAllHooks: true` switches off user, project, local, and plugin hooks for debugging; managed hooks keep running unless it's set in managed settings.

### Patterns
<!-- cc: hooks.patterns -->

**1. Post-edit formatter** — `PostToolUse` on `Write|Edit`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{ "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/format.sh" }]
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

**3. Stop-gate verification** — a `Stop` hook that runs the project's check (lint, tests) and exits 2 with the failure output on stderr forces Claude to fix before finishing. Decide what happens on the continuation: exiting 0 whenever `stop_hook_active` is set (the docs' loop guard) gives the gate one attempt per turn and never re-checks the fix; re-running the check and blocking only while it still fails re-verifies each fix, but the 8-block cap won't bound that loop: it counts only blocks with no tool call between them, so every fix attempt that edits a file starts the count over. Cap the retries in the hook itself, for example with a per-session attempt counter ⚠.

**4. Session context injection** — a `SessionStart` command hook whose stdout (sprint state, open tickets, environment status) is added to context — dynamic context without editing CLAUDE.md. Keep it under the 10,000-character cap.

### Pitfalls
<!-- cc: hooks.pitfalls -->

- `PostToolUse` runs *after* the edit — it can fix or report, not prevent. Pair it with a `Stop` gate for rules that must hold at turn end. A `Write|Edit` matcher also misses files that Bash or an outside process rewrites.
- Blocking requires **exit 2** (stderr carries the message) or a JSON deny/block decision; exit 1 is a non-blocking error — the action proceeds.
- **Gates fail open**: a mistyped script path, a crash, or a timeout lets the call through. Trigger each gate once to prove it blocks.
- `if` filtering is best-effort — enforce a hard allow/deny with a permission rule and keep hooks for logic and corrective messages.
- `@`-referenced files are read without a tool call, so no `PreToolUse` hook sees them — guard secrets with a `Read` deny rule.
- Hooks run inline — keep them fast, or the session drags on every event (`async: true` backgrounds a command hook but gives up blocking).
- Many events + many rules → route through a single dispatcher script instead of N config entries.
- For Python hook logic, single-file scripts with inline dependency declarations (`uv run`) keep hook deps out of your project environment.

## 8. Running lean: the token-budget playbook
<!-- cc: lean.overview -->

### Know your numbers first
<!-- cc: lean.measure -->

`/context` (what's loaded), `/usage` (session tokens and estimated cost — computed locally at list price, not your bill; `/cost` and `/stats` are aliases), `/doctor` (listing cost, plus unused skills, MCP servers, and plugins), `/skill-doctor` (per-skill cost and usage). The status line can render live `current_usage` including cache reads/writes. For continuous tracking: OpenTelemetry (`CLAUDE_CODE_ENABLE_TELEMETRY=1` plus an OTLP exporter and endpoint exports `claude_code.token.usage` and `claude_code.cost.usage`; set it in your shell, user, or managed settings — project and local settings ignore it since 2.1.282) or the community `ccusage` tool. Establish a baseline before optimizing anything.

### Session hygiene
<!-- cc: lean.session-hygiene -->

- **`/clear` between unrelated tasks** — stale history is pure input-token overhead. After two failed corrections on the same bug, `/clear` and re-prompt beats a polluted session.
- **`/rewind` to abandon a wrong path** — truncates back to an earlier turn whose prefix is still cached; cheaper than compacting.
- **`/compact` at natural breaks**, not mid-task. Guide it (`/compact focus on the test failures`) or set a standing `# Compact instructions` section in CLAUDE.md. Auto-compact is only a backstop: on 1M-window models it waits until ~967K tokens, so don't wait for it. Lower the trigger with `/autocompact` (saved per model) or `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` (it can lower the trigger, never raise it) ⚠.
- **Compaction is lossy for loaded instructions**: invoked skills come back truncated (first 5,000 tokens each, 25,000 in total), and path-scoped rules and nested CLAUDE.md files are summarized away. Re-invoke a skill whose rules still matter.
- **Plan mode is cache-friendly** (its instructions append after the cached prefix) but adds process overhead — if you can describe the diff in one sentence, skip the plan. Under `opusplan`, though, each plan-mode toggle is a model switch and a fresh cache.

### Caching: automatic, but don't fight it
<!-- cc: lean.caching -->

Claude Code caches in three layers (system prompt + tools / project context / conversation). Economics per MTok of base input: cache **reads cost 0.1×** on most models — **0.05× on Opus 5.5, 0.025× on Fable 5.1** — while 5-minute-TTL **writes cost 1.25×** and 1-hour writes 2×. A 5-minute write repays itself after one cache read, a 1-hour write after two. TTL depends on how you authenticate ⚠: **on a subscription, within your plan's included usage, the main conversation gets the 1-hour TTL automatically; subagents, compaction, and other background requests stay at 5 minutes, as does API-key and cloud-provider auth.** `ENABLE_PROMPT_CACHING_1H=1` requests 1 hour for everything, subagents included (at 2× writes); `promptCacheTtl` / `subagentPromptCacheTtl` set each bucket separately.

What invalidates the cache mid-session ⚠:

- **Breaks it:** `/model` (each model has its own cache) — including a skill or command whose `model:` differs from the session's, for that turn; the first `/fast` in a conversation; a new Claude Code version (applied at next launch); and, only when tool schemas load upfront (tool search off), connecting or removing an MCP server or a deny rule that removes a whole tool.
- **Safe now:** `/effort` on Opus 5.5, Sonnet 5.5, and Fable 5.1 (API key or subscription); toggling the advisor; plugin skills, commands, agents, and hooks; scoped permission rules. `/compact` rebuilds the conversation layer and reloads CLAUDE.md and memory from disk.
- **Editing CLAUDE.md mid-session** doesn't break the cache — but the edit doesn't apply until `/clear`, `/compact`, or a restart.

The practical rule: **pick your model and server set at session start and leave them alone**, and front-load stable context.

### Model routing
<!-- cc: lean.model-routing -->

<!-- TODO(owner): decide the default-model stance in the first bullet below. Evidence as of 2026-10-03: the account default is now Opus 5.5 at medium effort; the costs docs still say Sonnet handles most coding and costs less; Opus 5.5 and Sonnet 5.5 charge the same $0.20/MTok for cached reads, so Sonnet saves only on output, cache writes, and fresh input (2x each). -->

Match the model to the phase, not the session:

- **Default to Sonnet-class** for routine implementation; escalate deliberately rather than idling on Opus.
- **`opusplan`** runs Opus in plan mode and Sonnet in execution — strong reasoning where it counts, cheaper tokens for the long implementation tail. Each phase switch is a full cache miss, and with Opus 5.5 and Sonnet 5.5 charging the same for cached reads, the savings now come only from output, cache writes, and fresh input — measure before assuming it wins.
- **The advisor** (`/advisor`, `advisorModel`; experimental, Anthropic API only) lets a cheaper main model consult a stronger one at decision points — e.g. Sonnet main with an Opus advisor. Toggling it keeps the main cache, but each consultation re-reads the transcript uncached ⚠.
- **Haiku for mechanical subagents** (see §5) — this is where per-agent `model:` earns its keep.
- **Raise `/effort` before escalating the model.** The diagnostic order for disappointing output: missing context → effort → model. On Opus 5.5, Sonnet 5.5, and Fable 5.1 an effort change keeps the cache, and Opus 5.5 and Sonnet 5.5 start at `medium`, so headroom is one command away; the level is saved per model (`modelSettings`).
- **Fast mode (`/fast`)** ⚠ is the same model — Opus 5.5 by default since 2.1.280 — up to ~2.5× faster at 2× the price ($8/$40 per MTok): a latency lever, not a capability one. The first toggle in a conversation re-reads the context uncached at fast rates; on subscriptions it bills usage credits only.

Pinning and defaults: model precedence runs `/model` → `--model` → `ANTHROPIC_MODEL` → the `model` setting, and the account default is now Opus 5.5 on most plans and providers ⚠. `ANTHROPIC_DEFAULT_OPUS_MODEL` / `_SONNET_MODEL` / `_HAIKU_MODEL` / `_FABLE_MODEL` control what each alias resolves to (alias targets differ by provider); `CLAUDE_CODE_SUBAGENT_MODEL` sets the subagent fallback; `availableModels` restricts every place a model can be named, subagent and skill models and the advisor included (`enforceAvailableModels`, in managed settings, extends it to the Default option). `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` cuts network chatter (updates, telemetry, error reports), not model calls — and because it stops feature-flag fetching, it also switches the advisor off ⚠.

List prices (October 2026, per MTok) ⚠:

| Model | Input | Output | Cache read | Cache write 5m / 1h |
|---|---|---|---|---|
| Fable 5.1 | $10.00 | $50.00 | $0.25 (0.025×) | $12.50 / $20.00 |
| Opus 5.5 | $4.00 | $20.00 | $0.20 (0.05×) | $5.00 / $8.00 |
| Sonnet 5.5 | $2.00 | $10.00 | $0.20 (0.1×) | $2.50 / $4.00 |
| Haiku 4.5 | $1.00 | $5.00 | $0.10 (0.1×) | $1.25 / $2.00 |

(Opus 5.5 and Sonnet 5.5 cost the same per cached-read token, so in a cache-heavy session Sonnet's discount applies only to output, writes, and fresh input. Claude models from 4.7 on use a tokenizer that yields roughly 30% more tokens for the same text, so per-token comparisons with older models such as Haiku 4.5 understate the gap. Batch API runs at 50% of list.)

### MCP hygiene
<!-- cc: lean.mcp -->

- Tool schemas are **deferred by default**: only tool names and server instructions load upfront; full schemas load on demand via tool search. `ENABLE_TOOL_SEARCH` tunes this (`auto` = load schemas upfront while they total under 10% of the window — up to ~100K tokens on a 1M window, so prefer the default or a small `auto:N`; `false` = all upfront; per-server `alwaysLoad: true` exempts a server). Deferral falls back to upfront loading when `ANTHROPIC_BASE_URL` points at a non-first-party host; `ENABLE_TOOL_SEARCH=true` overrides that ⚠.
- `MAX_MCP_OUTPUT_TOKENS` (default 25,000) caps tool-result size; oversized non-image results are written to disk and referenced instead of inlined. A second threshold ignores this variable: a successful text result over 50,000 characters also goes to disk, unless the server declares a larger `anthropic/maxResultSizeChars` for that tool ⚠.
- Audit `/mcp` and disable servers you don't use in this project. A server only one subagent needs can be defined inline in that agent's `mcpServers`, keeping its tool descriptions out of the main context.
- Prefer a CLI (`gh`, `aws`, `gcloud`) over an equivalent MCP server — a CLI has zero schema cost, and Bash permission rules can match its arguments, whereas settings-file rules can't match an MCP tool's parameters.

### Scale ceremony to task size
<!-- cc: lean.ceremony -->

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
<!-- cc: lean.expensive-ops -->

For anything costly to recompute — long test suites, big builds, simulations, model training, data pulls:

- **Persist results to disk immediately** (`cmd > results.txt 2>&1`), then have Claude read the artifact instead of re-running the producer. Don't rely on Claude Code to save it: only oversized *successful* Bash output goes to a file, and a failing run comes back as a head-and-tail excerpt with no file.
- **Gate the expensive command behind a manual skill** (`disable-model-invocation: true`) or a `PreToolUse` deny, so it never fires as a casual side effect.
- **Verify from saved output** — a skill instruction like "read the saved results file; do not re-run the job" plus a hook blocking the run command makes the cheap path the default and the expensive path deliberate.

## Further reading
<!-- cc: reading.overview -->

Official documentation (all under `code.claude.com/docs/en/`; append `.md` to any page for raw markdown, and `llms.txt` indexes them all): `skills`, `sub-agents`, `hooks` and `hooks-guide`, `memory` (CLAUDE.md, rules, auto-memory), `settings`, `permissions`, `permission-modes`, `model-config`, `advisor`, `context-window`, `prompt-caching`, `costs`, `monitoring-usage`, `mcp`, `fast-mode`, `changelog`. Current API pricing: `platform.claude.com/docs/en/about-claude/pricing`. The Haiku 4.5 SWE-bench figure is from Anthropic's launch post, `anthropic.com/news/claude-haiku-4-5`.
