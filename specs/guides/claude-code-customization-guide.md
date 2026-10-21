# Claude Code Customization Guide

**Skills · slash commands · subagents · rules · hooks — built and run on a token budget**

<!-- cc-guide:stamp -->
> Checked against the Claude Code docs and changelog through 2.1.306 on 2026-10-21; oldest full re-verification 2026-10-03, at 2.1.288.
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
- **CLAUDE.md**, with any rules file that has no `paths` field, is the always-loaded prose you control most directly. Spend it like cash.

## 2. Choosing the right mechanism
<!-- cc: mechanisms.overview -->

| The guidance is… | Put it in… | Why |
|---|---|---|
| Deterministic and machine-checkable ("always format", "never use pip") | A hook (plus linter config) | Runs every time, costs no tokens unless it returns output, can't be ignored |
| A hard access boundary ("never read `.env`", "no destructive git") | Permission rules in `settings.json` | Checked before every tool call. A shell-command rule matches the command text only, so back a must-never command with a `PreToolUse` hook or the sandbox. Add the sandbox where a shell command could read a file without naming it |
| Short, always-true, not inferable from code (build commands, style deltas) | CLAUDE.md | Always loaded — reserve it for what's always relevant |
| Relevant only when touching certain files | A rule file with `paths` | Lazy-loads on match |
| Sometimes-relevant knowledge or a multi-step workflow | A skill | Loads on demand; can bundle scripts and references |
| A repeatable entry point you trigger deliberately (`/deploy`, `/release`) | A skill with `disable-model-invocation: true` | Invocable, never auto-fired, absent from the listing — zero standing cost |
| Read-heavy, parallelizable, or fresh-eyes work | A subagent | Isolated context; only a summary returns |

The dividing principle: **instructions are advisory; hooks are deterministic.** A CLAUDE.md line saying "always run the linter" is usually followed. A `PostToolUse` hook runs the linter after every successful matching tool call, with no model decision (a failed call fires PostToolUseFailure instead). Whenever a rule is checkable by a program, moving it from prose into a hook (or linter config) frees tokens and closes the compliance gap in one move — it is the single highest-leverage conversion in this guide.

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
| `~/.claude/skills/<name>/` | All your projects on this machine, but not Cowork or cloud sessions, cloud scheduled tasks (formerly routines) included. Desktop scheduled tasks run locally and do load it | ↓ |
| `.claude/skills/<name>/` | The project: sessions in this repository, but not cloud threads in a project, where committed project skills are unavailable (enable the skill for the claude.ai account instead) | Lowest of the three |
| Nested `.claude/skills/` in subdirectories | That subdirectory — loads at startup when the session starts in or below it, otherwise when Claude first reads or edits a file there. Not available in cloud threads in a project | Never shadows; on a clash, address it as `dir:name` (e.g. `apps/web:deploy`) |
| Plugin `skills/` | Wherever the plugin is enabled | Never shadows — namespaced as `plugin:skill` |

Among the first three, a same-name skill shadows the lower-precedence one. Skills enabled on your claude.ai account also sync into terminal sessions signed in with that account (`~/.claude/skills/synced/`; `syncClaudeAiSkills: false` opts out) and join the listing ⚠. Symlinks are followed — keeping a skills repo elsewhere and symlinking each skill into `~/.claude/skills/` gives you version control with live edits.

### Frontmatter reference ⚠
<!-- cc: skills.frontmatter -->

| Field | Effect |
|---|---|
| `name` | Sets the `/` command shown and typed (unless another command holds it); the directory name also invokes the skill. A `name` holding a character Claude Code refuses (zero-width, control, private-use or unassigned, direction-changing or odd blank characters, `<` or `>`) is ignored (2.1.299+): the menu hides it and typing it runs nothing. A refused folder name keeps a skill from loading outside plugins; in a plugin's skills directory the characters become hyphens ⚠ |
| `description` | The router — drives auto-invocation. Combined with `when_to_use`, capped at 1,536 chars in the listing (`skillListingMaxDescChars`) |
| `when_to_use` | Extra trigger context appended to the description (shares the cap) |
| `argument-hint` | Autocomplete hint, e.g. `[issue-number]` |
| `arguments` | Named positional args usable as `$name` in the body; only the first 64 names, each up to 64 characters, are filled in (2.1.301+) |
| `allowed-tools` | Tools pre-approved for the turn the skill runs (clears next user message). Ignored when managed settings set `allowManagedPermissionRulesOnly` (2.1.282+) in skills and commands from a repository's .claude directory, your ~/.claude skills and commands (synced claude.ai skills included), an --add-dir directory, or a manifest plugin inside a skills folder, since 2.1.305 in plugins that Claude Desktop mounts by path, and since 2.1.284 in plugins from marketplaces, claude.ai or npm unless they come from an official Anthropic source or one that managed settings vouch for; managed and bundled skills keep theirs, and `disallowed-tools` still applies. Since 2.1.304 it is also not granted to a main-conversation skill whose hooks a plugins-only hook policy keeps out |
| `disallowed-tools` | Tools removed while the skill is active (clears next user message, like `allowed-tools`) |
| `model` / `effort` | Model override for the rest of the turn, and reasoning-effort override while the skill is active (respects `availableModels`). A `model` that differs from the session's makes that turn a full cache miss (with `context: fork` it sets the forked subagent's model instead). In auto mode, and in plan mode while the classifier reviews commands, a `model` that auto mode doesn't support (older than Opus 4.6 or Sonnet 4.6 on the Anthropic API and Claude Platform on AWS, older than Sonnet 5 or Opus 4.7 on Bedrock, Google Cloud, Foundry and the Claude apps gateway, and Haiku 4.5 or earlier anywhere; Haiku 5.5 and the Fable models are supported everywhere, and `haiku` resolves to Haiku 5.5 on the Anthropic API since 2.1.293) is ignored and the session model runs — the behavior since 2.1.259, which also fixed a bug that ignored skill `model:` in interactive sessions ⚠ |
| `context: fork` | Run the body in an isolated subagent that doesn't see the conversation — the instructions must stand alone |
| `agent` | Which agent type executes a forked skill (default `general-purpose`) |
| `background` | For forked skills: `false` blocks the turn for the result; `true` (default, 2.1.218+) runs in background. Claude Code still waits for the result in claude -p and Agent SDK runs, with CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1, on a repeat invocation while the earlier one runs, when a session-scoped scheduled task fires the skill, and, since 2.1.295, when an agent in a dynamic workflow invokes it ⚠. A fork that runs in the background gets the narrower tool set of background subagents, so a skill whose steps need another tool sets `false`. Its edits also fall outside the session's checkpoints: `/rewind` restores only the files Claude had already edited in the conversation, so the fork's changes to any other file stay and need reverting with git |
| `disable-model-invocation` | `true` = Claude never runs the skill on its own, and the skill leaves the listing entirely — use for side-effecting workflows. `/name` at the start of a message runs it; `/name` later in a message only permits Claude to run it while answering that message, so write the bare name to mention it without permitting a run. It also keeps the skill from being preloaded into subagents and from running when a session-scoped scheduled task fires with it as the prompt ⚠ |
| `user-invocable` | `false` = Claude-only: hidden from the `/` menu, and typing `/name` won't run it |
| `paths` | Globs restricting when the skill is auto-loaded |
| `hooks` | Hooks registered when the skill is invoked; they stay active for the rest of the session (same JSON shape as settings; `once: true` is honored only here). The skill's own `UserPromptSubmit` hook first runs on the prompt after the one that invokes the skill (2.1.299+). Since 2.1.304 the skills of one source (a repo, your own folder, or a plugin) can register at most 1,024 hooks and 16,384 matcher characters per session |
| `shell` | `bash` (default) or `powershell` for `` !`command` `` preprocessing |
| `license`, `compatibility`, `metadata` | Agent Skills spec fields — accepted, not acted on. Unknown fields are ignored silently, so a misspelled field fails without an error. The same holds for the whole block: Claude Code reads frontmatter only when its opening three-dash line is the file's first line, and YAML that doesn't parse loads the skill with no fields set |

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

- `/doctor` estimates the listing cost and the biggest contributors; `/skill-doctor` shows each skill's cost and how often it's used (2.1.252+, and missing from sessions that skip feature-flag fetching); the `/context` Skills row shows the post-budget size.
- `skillListingBudgetFraction` in settings raises the budget (e.g. `0.02` for 2%), and the `SLASH_COMMAND_TOOL_CHAR_BUDGET` environment variable sets it as a fixed character count instead. Each entry's description and `when_to_use` text stays capped at 1,536 characters by default, however large the budget. `skillListingMaxDescChars` changes that cap, and lowering it fits more skills under the budget.
- `disable-model-invocation: true` takes a skill out of the listing entirely — the cheapest home for manual-only workflows.
- `skillOverrides` sets individual skills to `"name-only"` (listed without a description), `"user-invocable-only"` (hidden from Claude, still typable), or `"off"`. It doesn't reach plugin skills — manage those in `/plugin`.
- Disable unused plugins — a plugin's whole skill set lands in the listing.

### Progressive disclosure
<!-- cc: skills.progressive-disclosure -->

Three tiers keep skills nearly free until used: the listing (name + description, always loaded) → the `SKILL.md` body (loaded on invocation) → bundled files (loaded only when the body points at them). Exploit tier three deliberately: keep the body short and push depth into `references/`, named explicitly in prose ("For the edge cases, read `references/edge-cases.md`").

Tier two is not free once paid: an invoked body enters the conversation and stays for the rest of the session. After compaction, Claude Code re-attaches the most recent invocation of each skill and keeps the first 5,000 tokens of each, within a shared 25,000-token budget filled newest first. Older invoked skills can drop out entirely, so put the critical instructions near the top of `SKILL.md`. Since 2.1.304, compaction also sends Claude the skill listing again, and `/reload-skills` re-sends only new or changed skills.

Write the body as **process, not prose**. A 2,000-word essay gets skimmed and paraphrased; a numbered workflow with steps, checkpoints, and exit criteria gets executed — and gives you something verifiable. Bundle deterministic logic as scripts in `scripts/` rather than describing it and hoping the model re-derives it correctly.

### Arguments and dynamic context
<!-- cc: skills.arguments -->

| Substitution | Meaning |
|---|---|
| `$ARGUMENTS` | Everything typed after `/name`; with skills stacked at the start of a terminal message, up to six expand and each gets the trailing text, and a forked skill or a /loop-style command ends the expansion and becomes part of that text (through claude -p or the Agent SDK only the first skill loads, and the rest of the line is its arguments). When no placeholder receives an argument, Claude Code appends the input to the content as `ARGUMENTS: <value>` |
| `$0`, `$1`, … | Positional args — **zero-based** (`$0` is the first argument; `$ARGUMENTS[0]` is the same) ⚠ |
| `$name` | Named argument from the `arguments` frontmatter list |
| `${CLAUDE_SKILL_DIR}` | The skill's own directory (also usable inside `allowed-tools`) |
| `${CLAUDE_PROJECT_DIR}` | Project root |
| `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}` | Session metadata |
| `\$` | Escapes a `$` before a digit, `ARGUMENTS`, or a declared argument name (e.g. `\$1.00`). It does not stop a `${CLAUDE_*}` substitution, which has no escape |

`` !`command` `` (inline) or a ```` ```! ```` fenced block runs a shell command **once, at render time, before Claude sees the content**, and splices in the output — useful for injecting `git status`, dates, or issue metadata. It is preprocessing, not an agentic tool call, but it is still permission-checked: a deny rule aborts the whole invocation, and outside auto mode so does any command your rules don't allow, so pre-approve the commands in `allowed-tools`. A non-zero exit aborts the invocation too, except exit code 1 from search and comparison commands such as grep, which counts as a normal result (append `|| true` to any other command where failure is an expected result). `disableSkillShellExecution` turns injection off for user, project, plugin and added-directory skills and commands, replacing each command with a placeholder; bundled and managed skills are not affected.

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
| `name` | Required, as is `description`. Unique ID of at most 256 characters; it can't start with `-` or contain a colon (plugin-scoped names reserve it), or Claude Code skips the file; the filename needn't match |
| `description` | Drives delegation — concrete triggers like a skill description, but every agent's description sits in context, so keep it short |
| `tools` | Allowlist (omit to inherit every tool available to subagents, MCP tools included, though a few tools are always removed and a background run keeps only a fixed set of built-in tools, except a fork or a resumed foreground subagent, which keeps the tool set it had); `Agent(worker, researcher)` restricts spawnable types only for an agent run as the main thread (`--agent`) |
| `disallowedTools` | Subtractive alternative to `tools` (applied first when both are set) |
| `model` | `sonnet` \| `opus` \| `haiku` \| `fable` \| full ID \| `inherit`. Resolution order: a per-spawn `model` Claude passes → this field → `CLAUDE_CODE_SUBAGENT_MODEL` → the main model ⚠ |
| `effort` | `low` … `max` reasoning effort for this agent (levels vary by model); a per-spawn `effort` Claude passes (2.1.292+) overrides it, and `CLAUDE_CODE_EFFORT_LEVEL` outranks both |
| `permissionMode` | `default` (manual is an alias), `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan` — ignored when the parent runs in `bypassPermissions`, `acceptEdits`, or auto mode. `bypassPermissions` never escalates: the agent runs in it only when the main conversation does |
| `maxTurns` | Turn cap; at the limit the output comes back marked partial and can be resumed |
| `autoCompactWindow` | Lowers this agent's auto-compact window, so it compacts earlier: a plain-integer token count from 100000 to 1000000 (200k reads as 200 and is ignored). Only a value below the window the agent would otherwise inherit changes anything. No effect while CLAUDE_CODE_AUTO_COMPACT_WINDOW holds a window (a plain integer or, since 2.1.304, a value with a k or M suffix), or when the whole session runs as this agent through --agent or the `agent` setting. Also accepted in --agents JSON and applied to in-process teammates (2.1.296+) ⚠ |
| `skills` | Skills whose **full content is preloaded** at start — costly; only for what the role always needs. A skill with `disable-model-invocation: true`, as advised for side-effecting skills, can't be preloaded: preloading draws from the skills Claude can invoke |
| `mcpServers` | MCP servers available to the agent (inline defs or refs to the parent's); an inline server's tool descriptions stay out of the parent's context |
| `hooks` | Lifecycle hooks active only while the agent runs |
| `memory` | `user` \| `project` \| `local` — persistent memory scope for cross-session learning; auto-enables Read/Write/Edit and loads that MEMORY.md (first 200 lines / 25 KB) at every spawn. No effect while auto memory is off (`autoMemoryEnabled` or CLAUDE_CODE_DISABLE_AUTO_MEMORY): the agent then gets neither the memory instructions nor that tool access |
| `background` | `true` keeps it in the background even when Claude wants the result. Unset, a subagent Claude spawns from the main conversation starts in the background in every session (unless CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1, which makes Claude wait for every subagent and turns off Ctrl+B); fork mode only decides whether Claude can wait for it. Fork mode is on by default in the terminal and, since 2.1.302, in claude -p, the Agent SDK, the desktop app and VS Code (CLAUDE_CODE_FORK_SUBAGENT=0 turns it off). While it is on, Claude cannot wait in interactive terminal, VS Code and desktop sessions on your machine. In claude -p and the Agent SDK, Claude may still choose to wait, so set the field to true there to keep it in the background. A spawning subagent waits for its nested subagents by default in the interactive terminal, and in claude -p and the Agent SDK while fork mode is on; with fork mode off, nested subagents there start in the background (the 2.1.302 changelog also lists the desktop app and VS Code) ⚠ |
| `isolation` | `worktree` runs it in a disposable git worktree (auto-cleaned if unchanged), branched from `origin/<default-branch>` — unpushed commits are absent unless `worktree.baseRef` is `"head"`. Exception: with agent teams on in an interactive session, a subagent Claude spawns from the main conversation with a `name` launches as a teammate in the main working directory unless the call is a fork or passes `isolation` itself; frontmatter `isolation` doesn't stop that |
| `omitClaudeMd` | `true` launches it without user, project, and local CLAUDE.md (managed files still load, except for managed subagents) — a cheaper spawn (2.1.271+). A subdirectory's CLAUDE.md and matching path-scoped rules still load when it works with files there, and the field is ignored when the agent runs as the session agent via `--agent` or the `agent` setting |
| `experimental.cacheTtl` | `5m` or `1h` prompt-cache TTL for this agent's requests (2.1.248+) ⚠ |
| `color`, `initialPrompt` | Display color; auto-submitted first turn when run as a main session via `--agent` or the `agent` setting |

Plugin subagents ignore `permissionMode`, `mcpServers`, `hooks` and `initialPrompt`. Field names are camelCase and must match exactly: Claude Code ignores an unknown or misspelled field without an error, and since 2.1.296 `claude --debug` logs it as "does not recognize or apply".

### Scope tools to the role
<!-- cc: subagents.tools -->

Least privilege keeps agents focused and safe:

- **Reviewers / auditors**: `Read, Grep, Glob` — analyze without modifying.
- **Researchers**: add `WebFetch, WebSearch`.
- **Implementers**: `Read, Write, Edit, Bash`.

A documentation agent doesn't need `Bash`; a review agent doesn't need `Write`. Two catches ⚠: on macOS, Linux, and WSL, `Glob` and `Grep` are absent by default and come back only for an agent that lists them *without* `Bash` (with `Bash`, search runs through the shell); and `memory:` silently adds Read/Write/Edit, so keep it off read-only roles.

### Route models by role
<!-- cc: subagents.models -->

Since 2.1.293 the `haiku` alias resolves to Haiku 5.5 on the Anthropic API: $0.10/$0.50 per MTok for prompts up to 100K tokens — a fortieth of Opus 5.5's price ($4/$20) and a twentieth of Sonnet 5.5's — with a 1M window, aimed by Anthropic at high-volume, latency-sensitive work such as classification, extraction, and routing. Its predecessor Haiku 4.5, which lists at a quarter of Opus 5.5's per-token price ($1/$5), scored 73.3% on SWE-bench Verified at its October 2025 launch — evidence that cheap delegation costs little quality on mechanical work. Two caveats ⚠: on Amazon Bedrock, Google Cloud's Agent Platform, Microsoft Foundry, and Claude Platform on AWS, `haiku` still resolves to Haiku 4.5, now a legacy model whose 200K window trails the 1M of the current Fable, Opus, Sonnet, and Haiku 5.5 (a subagent's window follows its own model, not the parent's) and whose retirement window opens no sooner than 2026-10-15 on Anthropic-operated platforms (the Claude API, Microsoft Foundry, Claude Platform on AWS), while Bedrock and Google Cloud set their own dates; and Haiku 5.5 bills every rate at 5× once a prompt passes 100K tokens, cache reads and writes included. A sensible default split:

- **Haiku**: test-running, formatting checks, mechanical review, classification, search/exploration.
- **Sonnet**: implementation.
- **Opus**: planning, architecture, adversarial correctness review.
- **Fable**: the hardest reasoning and long-horizon work, when Opus at high effort still falls short — at 2.5× Opus's list price.

The built-in `Explore` agent now inherits the session model rather than running on Haiku — except that under a Fable session, on a subscription, a Console account or an `ANTHROPIC_BASE_URL` gateway, it runs on whatever `opus` resolves to; to explore on Haiku, define your own `Explore` with `model: haiku` (it overrides the built-in). `CLAUDE_CODE_SUBAGENT_MODEL` is only a fallback since 2.1.251: an agent's `model` field and a per-spawn `model` both outrank it, and it doesn't move the built-in Explore and Plan; `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` (2.1.257+) applies it to every subagent, teammate, and workflow agent, ignoring definition and per-spawn models — but forks and `model: inherit` skills stay on the session model ⚠.

### Isolation mechanics — and when delegation pays
<!-- cc: subagents.isolation -->

A subagent starts from its own system prompt and environment details, not the parent's conversation. Custom agents and most built-ins also load your CLAUDE.md hierarchy and a git-status snapshot at spawn; Explore and Plan skip both. The exception is a **fork** — Claude's `fork` subagent type, or `/subtask` — which inherits the entire conversation; fork mode is on by default in the terminal and, since 2.1.302, in claude -p, the Agent SDK, the desktop app and VS Code (CLAUDE_CODE_FORK_SUBAGENT=0 turns fork mode off, while an `Agent(fork)` deny rule stops only the forks; claude mcp serve never offers forks) ⚠. Either way, its exploration — possibly tens of thousands of tokens of file reads — stays in its own window; only its final text returns. Subagents keep their own prompt caches on a 5-minute TTL by default, even on a subscription where the main conversation gets 1 hour. CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL, `subagentPromptCacheTtl` and `experimental.cacheTtl` change it, in that order of precedence, and `FORCE_PROMPT_CACHING_5M=1` outranks all three; a frontmatter `1h` is ignored while a subscription is using usage credits. A fork reuses the parent's cache.

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

Files load broad → specific and are **concatenated, never overridden**: managed policy → `~/.claude/CLAUDE.md` → project `CLAUDE.md` (or `.claude/CLAUDE.md`) → `CLAUDE.local.md` (personal; gitignore it yourself). CLAUDE.md files in ancestor directories of the working directory load at launch too. Subdirectory CLAUDE.md files are lazy — they load when Claude reads or edits files in that subtree, which makes them the right home for module-specific guidance in a monorepo. Lazy content lives in message history, so compaction summarizes it away; anything that must persist belongs in an always-loaded file. `AGENTS.md` is read natively since 2.1.277, but by default only as a fallback: a `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` in the working directory or above it stops it loading, while `~/.claude/CLAUDE.md`, managed instructions and rules files don't count. The Project instructions setting in /config changes that default ⚠.

`@path/to/file` inside CLAUDE.md inlines another file at load time (max 4 hops; a relative path resolves from the importing file, not the working directory). Import parsing skips code spans and fenced code blocks, so backticks mention a path without importing it. Imports organize a long file but don't shrink it — imported files load at launch too.

### Rules files
<!-- cc: rules.rules-files -->

`.claude/rules/*.md` (project) and `~/.claude/rules/*.md` (personal) hold focused rule files:

- **Without `paths`**: loaded at session start, alongside CLAUDE.md.
- **With `paths` globs** (`**` wildcards and brace expansion supported): loaded lazily, only when Claude reads, writes, or edits a matching file (a Bash command that counts as a read, such as cat or head on a single file, included since 2.1.293) — the cheap way to carry per-area conventions. Compaction summarizes them away, so a rule that must persist should drop `paths` or move to the root CLAUDE.md. Brace expansion is bounded: a rule's whole `paths` list shares one budget of 1,000 expanded patterns and 4 MiB, and a pattern that would exceed it is used unexpanded, so its literal braces match no files. A `[` that can't open a bracket expression makes its pattern match nothing too, while the rule's other patterns keep working (escape a literal one as `\[`). Frontmatter that doesn't parse as YAML is ignored, so the rule loads every session as if it had no `paths`; claude --debug shows the parse error.

Rules are discovered recursively, so subdirectory organization works. A symlinked rule whose target lies outside the project counts as an external import: it loads only after you approve external imports for the project, and then only if it has no `paths` (2.1.284+) ⚠. Keep cross-project rules in `~/.claude/rules/` instead. User rules load before project rules and neither set overrides the other: when two conflict, Claude may follow either, so keep them consistent.

### Auto memory
<!-- cc: rules.auto-memory -->

Claude Code keeps per-project memory in `~/.claude/projects/<project>/memory/`. The first 200 lines / 25 KB of `MEMORY.md` load every session; topic files load on demand. Keep `MEMORY.md` an index of one-line pointers and let the detail live in topic files. Claude's own config directory is a protected path, but the markdown files in this memory directory are exempt, so Claude's memory writes don't wait on approval, except in a session started with `--restricted` ⚠.

### Settings precedence and permission rules
<!-- cc: rules.settings -->

`settings.json` resolves highest-to-lowest: **managed → `--settings` JSON → `.claude/settings.local.json` → `.claude/settings.json` → `~/.claude/settings.json`** (other flags, such as `--model`, set one thing for the session and aren't part of this stack). Since 2.1.304 a mod's `settings.read` hook receives each layer and can rewrite the merged settings, so a managed mod can make an organization's setting a ceiling.

Permissions **merge across levels** — a deny anywhere wins; no other level can re-allow it. (One exception, 2.1.287+: outside plan mode, or for a read-only call, an installed mod that handles `tool.check` can approve a call that a deny rule refused or a PreToolUse hook blocked, but only when the machine has no managed settings and the session's credential is not a Team or Enterprise /login (a session on an API key or a long-lived CLAUDE_CODE_OAUTH_TOKEN doesn't count, even with that login stored). With either present, deny rules hold over the mod by default, though an organization can change that, and so do ask prompts, hook blocks from any settings file, and --permission-prompt-tool or canUseTool questions. A mod's approval also doesn't skip the prompt for a tool that needs user interaction (2.1.292+). In plan mode it can't approve a file edit or another call that isn't read-only ⚠.) Evaluation order is `deny → ask → allow`, first match wins. Syntax details worth memorizing:

- `Bash(uv run *)` — matches `uv run` plus anything after it; the older `Bash(uv run:*)` form is equivalent, but only at the end of a pattern. A runner rule approves *whatever* follows `run`.
- Word boundaries matter: `Bash(ls *)` matches `ls -la` but not `lsof`; `Bash(ls*)` matches both.
- Compound commands are split on `&&`, `||`, `;`, `|`, `|&`, `&`, and newlines: an allow rule must match every part, while a deny or ask rule fires if any part matches — even inside `$()` or a subshell.
- File rules use gitignore-style paths: `Read(./.env)`, `Read(./secrets/**)`, `//abs/path` (filesystem root), `~/path`. A single leading slash is **not** absolute: `/path` anchors at a directory tied to the settings source, the primary working directory for project and local settings, CLI flags and session rules, ~/.claude for user settings, and the file's own directory for `--settings`.
- On Windows with Git Bash installed, any Bash deny rule, scoped or bare, from a settings file or `--disallowedTools`, also turns the PowerShell tool off for the session, since a Bash rule can't restrict PowerShell. To keep PowerShell on, set `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` or add a scoped `PowerShell(…)` rule of your own ⚠.

`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` strips credentials, recognized by variable name or value, from the environments of Bash commands, hooks, and stdio MCP servers: a layer under permission rules, not a replacement. It also turns sandbox auto-allow (`autoAllowBashIfSandboxed`) off, and on Linux runs Bash in an isolated PID namespace, so ps, pgrep and kill can't see or signal host processes. It deliberately keeps the GitHub token variables (`GITHUB_TOKEN`, `GH_TOKEN`, and the Enterprise pair) and `HTTP_PROXY`/`HTTPS_PROXY`, even a proxy URL carrying a username and password. It also keeps GIT_CONFIG_COUNT and its GIT_CONFIG_KEY_n and GIT_CONFIG_VALUE_n pairs, whatever they hold. Remove the GitHub and proxy variables yourself: list the GitHub variables under `sandbox.credentials.envVars` with `"mode": "deny"`, or `"mask"` with `"injectHosts": ["api.github.com"]` so `gh` keeps authenticating once the sandbox proxy terminates TLS (`sandbox.network.tlsTerminate`, or `allowPlaintextInject` on plain-HTTP test networks; mask entries count only from user settings, managed settings or the `--settings` flag), and keep credentials out of proxy URLs. `sandbox.credentials` covers sandboxed commands only, so hooks and MCP servers still inherit whatever the scrub leaves ⚠.

Pair permission rules with hooks. In Manual mode an allowlist makes `uv run …` frictionless; in auto mode — the built-in starting mode for interactive terminal and VS Code sessions since 2.1.283, except where a settings file sets `disableAutoMode` to `"disable"`, under the HIPAA configuration (2.1.285+), or where auto mode is unavailable for the model or turned off server-side, which all start in Manual — broad rules such as package-manager run commands are set aside and a classifier reviews those calls instead (on Enterprise plans and on API or cloud-provider accounts its calls count toward your token usage, unless the server reviews actions within the model requests) ⚠. Since 2.1.302 a claude -p or Agent SDK run with no mode set starts in Manual and denies calls that need approval, so for CI, gateway and similar runs pass `--permission-mode auto`, set the SDK permission mode option, or list allow rules. To start in auto by default, set `defaultMode` in user or managed settings, since auto set as the default in project or local settings files doesn't take effect ⚠. The hook that makes `pip install` impossible holds in every mode.

## 7. Hooks
<!-- cc: hooks.overview -->

Hooks are shell commands (or HTTP calls, MCP tool calls, prompts, or agents) that the harness executes at lifecycle events. They are the deterministic layer: instead of spending tokens instructing "always format with ruff," a `PostToolUse` hook formats every Write and Edit, every time, for free.

### Events ⚠
<!-- cc: hooks.events -->

Current builds document 33 events (the newest, `PreModelSwitch` / `PostModelSwitch`, arrived in 2.1.251); these are the workhorses:

| Event | Fires | Exit 2 blocks? |
|---|---|---|
| `PreToolUse` | Before a tool call | ✅ blocks the call; JSON can also allow/deny/ask or rewrite input, and defer works only in non-interactive claude -p runs (an interactive session logs a warning and ignores it) |
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

- **Exit 0** — success; stdout may be plain text (becomes context on `SessionStart`, `UserPromptSubmit`, `UserPromptExpansion` and `PostModelSwitch`) or structured JSON. JSON-looking output that fails to parse is a hook error (2.1.248+).
- **Exit 2** — block, on blockable events. The message is your JSON `reason` if you give one, otherwise stderr; tool events and `Stop` show it to Claude, most other events only to the user.
- **Other exits** — non-blocking error: the action proceeds, and the first stderr line surfaces in the transcript, except for hooks whose failure blocks (`onFailure: "block"` below, or the Windows case under Pitfalls). A non-0/2 exit that prints schema-valid JSON is decided by that JSON instead, but still counts as a failure for a hook whose failure blocks. On a `command` or `http` hook, `onFailure: "block"` (2.1.295+) makes such a failure do what exit 2 does on that event — on `PermissionRequest`, where exit 2 is ignored, it denies the request — except for the events and hooks listed under Pitfalls, where it has no effect.

JSON on stdout unlocks finer control: universal fields (`continue`, `stopReason`, `systemMessage` — a warning shown to the user, which some events discard or deliver elsewhere; `suppressOutput` is still accepted but now does nothing) plus event-specific `hookSpecificOutput` — `permissionDecision` / `updatedInput` on `PreToolUse`, `updatedToolOutput` on `PostToolUse`, `additionalContext` for injected context. `decision` / `reason` stay top-level; a top-level `additionalContext` is silently ignored. Injected text — `additionalContext`, `systemMessage`, `initialUserMessage`, plain stdout — is capped at 10,000 characters per string, each measured on its own even when several hooks run for one event; the overflow arrives as a file path plus a short preview. Stop hooks receive `stop_hook_active: true` whenever Claude is already continuing because of a stop hook — **check it (or the transcript) to avoid blocking on a condition that can never resolve**; the 8-block cap is only the backstop.

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

Hooks live in any settings level (user / project / local / managed — entries merge across levels), in plugins, and in **frontmatter**: a skill's hooks register when it's invoked and stay for the rest of the session (`once: true`, honored only there, removes one after its first successful run); an agent's hooks run only while that agent does. Each matcher group sets `matcher` (omitted, empty or `*` matches every occurrence of the event; otherwise a value of only letters, digits, underscores, hyphens, spaces, commas and pipes matches exactly — one name, or an `A|B` or comma-separated list; any other character makes it an unanchored regex over the event's field — tool name, session source, agent type; for FileChanged and StopFailure only letters, digits, underscores and pipes stay exact; SessionStart's sources are startup, resume, clear, compact and fork) for the hook handlers it wraps, whose common fields are type, `if` (permission-rule syntax over tool arguments, e.g. `Bash(git *)`; honored only on tool events — elsewhere a hook with `if` never runs), `timeout`, `statusMessage` and once (above); `command` and `http` handlers also take `onFailure` (unset, the action goes ahead as with `"continue"`, except that a shell-form `PreToolUse` or `PermissionRequest` command hook on Windows without Git Bash that doesn't set `shell` to powershell blocks when it fails, while one that does still fails open; `"block"` makes a failed `command` or `http` hook block, 2.1.295+). `disableAllHooks: true` switches off user, project, local, and plugin hooks for debugging, stops the mods you installed (your organization's mods keep running), and narrows a custom status line, subagent status line and file-suggestion command to managed values (a deployed managed value still runs, otherwise they are off); managed hooks, Agent SDK hooks, and hooks from plugins force-enabled in managed `enabledPlugins` keep running. Set in managed settings, it switches off every configured hook, managed ones included, though in-process Agent SDK hooks keep running; it stops installed mods along with their hooks and turns the custom status line, subagent status line and file-suggestion command fully off, not narrowed. Claude Code reads the value left after settings precedence, so a project's `false` overrides a user `true`; to turn hooks off for one run, pass it with the --settings flag.

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
- Blocking requires **exit 2** (stderr carries the message) or a JSON deny/block decision; exit 1 is a non-blocking error — the action proceeds, unless the hook sets `onFailure: "block"` (next bullet) or is a shell-form `PreToolUse` or `PermissionRequest` command hook on Windows without Git Bash that doesn't set `shell` to powershell. Exit 1 with schema-valid JSON on stdout is decided by the JSON, not the exit code, unless the hook's failure blocks the action (`onFailure: "block"`, or that Windows case): then any exit other than 0 or 2 is a failure even with JSON that allows the action, so return JSON decisions with exit 0.
- **Gates fail open** by default on command, HTTP and MCP tool hooks: a mistyped script path, a crash, or a timeout lets the call go on through the normal permission flow, so permission rules still apply but the gate does nothing. A timed-out Agent SDK callback hook blocks instead (the `PreToolUse` call or the `UserPromptSubmit` prompt), and so does a `PreModelSwitch` hook that times out (it blocks the switch). The exception, since 2.1.299, is a shell-form `PreToolUse` or `PermissionRequest` command hook on Windows without Git Bash that doesn't set `shell` to powershell, which blocks when it fails with `onFailure` unset ⚠. On a `command` or `http` hook, `"onFailure": "block"` (2.1.295+) turns each of those into a block — it has no effect on `Stop`, `SubagentStop`, `TaskCompleted`, `TeammateIdle`, or background (`async` or `asyncRewake`) command hooks. Either way, trigger each gate once to prove it blocks.
- `if` filtering is best-effort — enforce a hard allow/deny with a permission rule and keep hooks for logic and corrective messages.
- By default, `@`-referenced files are read without a tool call, so no `PreToolUse` hook sees them — guard secrets with a `Read` deny rule. `CLAUDE_CODE_DISABLE_FILE_MENTIONS=1` (2.1.299+; ignored in project and local settings) hands Claude the paths to read with its file tools instead, so matching hooks run.
- Hooks run inline — keep them fast, or the session drags on every event (`async: true` backgrounds a command hook but gives up blocking). An async hook's output is delivered on the next conversation turn (an idle session waits for the next user interaction, except that an `asyncRewake` hook exiting 2 wakes Claude at once), its `timeout` is not enforced (it is on `asyncRewake`), and claude -p kills one still running at teardown, finalizing it as cancelled.
- Many events + many rules → route through a single dispatcher script instead of N config entries.
- For Python hook logic, single-file scripts with inline dependency declarations (`uv run`) keep hook deps out of your project environment.

## 8. Running lean: the token-budget playbook
<!-- cc: lean.overview -->

### Know your numbers first
<!-- cc: lean.measure -->

`/context` (what's loaded), `/usage` (session tokens and estimated cost — computed locally at list price, or at your contracted rates while an administrator's managed `modelPricing` table is in effect; an estimate either way, not your bill; `/cost` and `/stats` are aliases), `/doctor` (listing cost, plus unused skills, MCP servers, and plugins), `/skill-doctor` (per-skill cost and usage; 2.1.252+, and unavailable in a session that skips feature-flag fetching). The status line can render live `current_usage` including cache reads/writes. For continuous tracking: OpenTelemetry (`CLAUDE_CODE_ENABLE_TELEMETRY=1` plus an OTLP exporter, endpoint, and protocol (`OTEL_EXPORTER_OTLP_PROTOCOL` or a per-signal one; there is no default) exports `claude_code.token.usage` and `claude_code.cost.usage`; set it in your shell, user, or managed settings — since 2.1.282, project and local settings can't turn export on, choose its destination, or capture content, though an off value there, such as an exporter selector set to none, still applies) or the community `ccusage` tool. Establish a baseline before optimizing anything.

### Session hygiene
<!-- cc: lean.session-hygiene -->

- **`/clear` between unrelated tasks** — stale history is pure input-token overhead. After two failed corrections on the same bug, `/clear` and re-prompt beats a polluted session.
- **`/rewind` to abandon a wrong path** — truncates back to an earlier turn whose prefix is still cached; cheaper than compacting.
- **`/compact` at natural breaks**, not mid-task. Guide it (`/compact focus on the test failures`) or set a standing `# Compact instructions` section in CLAUDE.md. Auto-compact is only a backstop: on models with a native 1M window (Fable, Sonnet 5 and later, Haiku 5.5, Opus 4.7 and later) it waits until ~967K tokens by default — a larger `CLAUDE_CODE_MAX_OUTPUT_TOKENS` moves that earlier — so don't wait for it. A second automatic trigger sits far below it: idle compaction (announced in 2.1.299) compacts a conversation of 200K tokens or more, left idle about 54 minutes in an interactive terminal on the one-hour cache TTL with feature flags fetched, shortly before its cache expires. `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS` moves that threshold (floor 100K); `idleCompaction: false`, the Idle compaction row in /config (2.1.302+), `DISABLE_AUTO_COMPACT` or `autoCompactEnabled: false` turns it off. The key and the variable need 2.1.290 or later, and an older build stops idle compaction only with `autoCompactEnabled: false` ⚠. Lower the trigger with `/autocompact` (saved per model) or `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` (it can lower the trigger, never raise it, and applies only in sessions that compact before the model's context limit, as native-1M models do; elsewhere set the window with `/autocompact` or --autocompact) ⚠. CLAUDE_CODE_AUTO_COMPACT_WINDOW sets the window itself. While Claude Code accepts its value, it overrides `/autocompact`, --autocompact and the `autoCompactWindow` setting, and `/autocompact` only reports it. A value that isn't a usable size is ignored, and the window then comes from those sources or the default.
- **Compaction is lossy for loaded instructions**: invoked skills come back capped at 5,000 tokens each, keeping the start of the file, and past 25,000 tokens in total the oldest invoked skills drop out whole; path-scoped rules and nested CLAUDE.md files are summarized away until Claude next reads, writes, or edits their trigger file, which reloads them; a rule that must persist drops its `paths:` frontmatter or moves to the project-root CLAUDE.md. Re-invoke a skill whose rules still matter.
- **Plan mode is cache-friendly** (its instructions append after the cached prefix) but adds process overhead — if you can describe the diff in one sentence, skip the plan. Under `opusplan`, though, each plan-mode toggle is a model switch and a fresh cache.

### Caching: automatic, but don't fight it
<!-- cc: lean.caching -->

Claude Code caches in three layers (system prompt + tools / project context / conversation). Economics per MTok of base input: cache **reads cost 0.1×** on most models — **0.05× on Opus 5.5 and Sonnet 5.5, 0.025× on Fable 5.1** — while 5-minute-TTL **writes cost 1.25×** and 1-hour writes 2×. A 5-minute write repays itself after one cache read, a 1-hour write after two. TTL depends on how you authenticate ⚠: **on a subscription, within your plan's included usage, the main conversation gets the 1-hour TTL automatically; subagents, compaction, and other background requests stay at 5 minutes, apart from a few server-controlled helper requests that get the hour, and API-key and cloud-provider auth stays at 5 minutes throughout.** `ENABLE_PROMPT_CACHING_1H=1` requests 1 hour for everything, subagents included (at 2× writes); `promptCacheTtl` / `subagentPromptCacheTtl` set each bucket separately. When controls conflict, `FORCE_PROMPT_CACHING_5M=1` wins, then the bucket's environment variable (`CLAUDE_CODE_PROMPT_CACHE_TTL` / `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL`), then its setting, then a subagent's `experimental.cacheTtl`, and only then `ENABLE_PROMPT_CACHING_1H=1`.

What invalidates the cache mid-session ⚠:

- **Breaks it:** `/model` (each model has its own cache) — including a skill or command whose `model:` differs from the session's, for that turn; the first `/fast` in a conversation; an automatic model fallback or a `fallbackModel` chain switch, which runs that turn on a cold cache; a new Claude Code version (applied at next launch); dropping a batch of the oldest images once a request would pass the image limit, which reprocesses from the earliest affected message (one slow turn per batch); and, only when tool schemas load upfront (tool search below its auto threshold, disabled, or unavailable), connecting or removing an MCP server or a deny rule that removes a whole tool.
- **Safe now:** `/effort` on Opus 5.5, Sonnet 5.5, Haiku 5.5, and Fable 5.1 (API key or subscription); toggling the advisor; plugin skills, commands, agents, and hooks; scoped permission rules.
- **Rebuilds by design:** `/compact` invalidates the conversation layer (its summarization request still reads the warm prefix) and reloads CLAUDE.md and memory from disk.
- **Editing CLAUDE.md mid-session** doesn't break the cache — but the edit doesn't apply until `/clear`, `/compact`, or a restart.

The practical rule: **pick your model and server set at session start and leave them alone**, and front-load stable context.

### Model routing
<!-- cc: lean.model-routing -->

Match the model to the phase, not the session:

- **Plan on Opus, execute on Sonnet.** Opus 5.5, the account default on most plans, earns its price on planning, design, and review; implementing a written plan runs well on Sonnet-class, and Sonnet 5.5 costs half of Opus 5.5 on every token class. Escalate a Sonnet session deliberately, not by habit. Choose the execution model at launch with --model: a typed `/model` also saves its choice as the default for new sessions. To switch for the current session only, open the picker with `/model` and press s on the model's row. Off the Anthropic API the `sonnet` and `haiku` aliases resolve to older models (Sonnet 4.5 or 4.6 and Haiku 4.5, and on Foundry `opus` is Opus 4.6), so this split, `opusplan` and the price comparisons in this section hold as stated only where the aliases resolve to the 5.5 models ⚠.
- **`opusplan`** runs Opus in plan mode and Sonnet in execution — strong reasoning where it counts, cheaper tokens for the long implementation tail. Each phase switch is a full cache miss, but Sonnet 5.5 now bills half of Opus 5.5 at every rate, cached reads included, so the execution tail is cheaper throughout — measure before assuming it wins.
- **The advisor** (`/advisor`, `advisorModel`; experimental; the Anthropic API, plus Claude Platform on AWS since 2.1.300 by the changelog, though the advisor page still lists that platform as unavailable and the environment-variable docs still name it among the sessions that skip the feature-flag fetch the advisor needs, so treat it as unconfirmed there) lets a cheaper main model consult a stronger one at decision points — e.g. Sonnet main with an Opus advisor. Toggling it keeps the main cache, but each consultation re-reads the transcript uncached ⚠.
- **Haiku for mechanical subagents** (see §5) — this is where per-agent `model:` earns its keep.
- **Raise `/effort` before escalating the model.** The diagnostic order for disappointing output: missing context → effort → model. On Opus 5.5, Sonnet 5.5, Haiku 5.5, and Fable 5.1 an effort change keeps the cache with an API key or a subscription (not on Bedrock, Google Cloud's Agent Platform, or a Claude apps gateway, nor with `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` or a HIPAA configuration), and Opus 5.5, Sonnet 5.5, and Haiku 5.5 start at `medium`, so headroom is one command away; the level is saved per model (`modelSettings`), except that `max` lasts only the current session unless set through `CLAUDE_CODE_EFFORT_LEVEL`, and a top-level `effortLevel` in user settings no longer applies to Opus 5.5 or later models.
- **Fast mode (`/fast`)** ⚠ is the same model — Opus 5.5 by default since 2.1.280 — up to ~2.5× faster at 2× the price ($8/$40 per MTok): a latency lever, not a capability one. The first toggle in a conversation re-reads the context uncached at fast rates; on subscriptions it bills usage credits only.

Pinning and defaults: model precedence runs `/model` → `--model` → `ANTHROPIC_MODEL` → the `model` setting → `ANTHROPIC_DEFAULT_MODEL` (the default for new sessions), and the account default is now Opus 5.5 on most plans and providers ⚠. `ANTHROPIC_DEFAULT_OPUS_MODEL` / `_SONNET_MODEL` / `_HAIKU_MODEL` / `_FABLE_MODEL` control what each alias resolves to (alias targets differ by provider: on Bedrock, Google Cloud's Agent Platform, and Microsoft Foundry, `sonnet` still means Sonnet 4.5, deprecated on 2026-09-30 and retiring on 2026-11-30 on Anthropic-operated platforms, while Bedrock and Google Cloud set their own dates); `CLAUDE_CODE_SUBAGENT_MODEL` sets the subagent fallback; `CLAUDE_CODE_AUTO_MODE_MODEL` (2.1.302+) sets the model for the client-side auto-mode classifier, and Claude Code ignores it, so the default classifier model reviews, when it names Opus 5, Sonnet 5.5 or Opus 5.5, or a model that `availableModels` or `deniedModels` blocks; `availableModels` restricts every place a model can be named, subagent and skill models and the advisor included; `deniedModels` (managed settings only, 2.1.283+) blocks a model even when that list permits it; and `enforceAvailableModels`, honoured in any settings file, extends the list to the Default option, though once an organization deploys managed settings only the managed value counts. `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` cuts network chatter (updates, telemetry, error reports), not model calls. It also suppresses the fast-mode availability check, so with no cached successful check `/fast` reports fast mode unavailable until CLAUDE_CODE_SKIP_FAST_MODE_ORG_CHECK=1 or CLAUDE_CODE_SKIP_FAST_MODE_NETWORK_ERRORS=1 is set. And because it stops feature-flag fetching, it switches the advisor off, as do the other variables that stop that fetch (DISABLE_TELEMETRY, DO_NOT_TRACK, DISABLE_GROWTHBOOK), a Claude apps gateway session, and a third-party provider session unless CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST is set ⚠.

List prices (October 2026, per MTok) ⚠:

| Model | Input | Output | Cache read | Cache write 5m / 1h |
|---|---|---|---|---|
| Fable 5.1 | $10.00 | $50.00 | $0.25 (0.025×) | $12.50 / $20.00 |
| Opus 5.5 | $4.00 | $20.00 | $0.20 (0.05×) | $5.00 / $8.00 |
| Sonnet 5.5 | $2.00 | $10.00 | $0.10 (0.05×) | $2.50 / $4.00 |
| Haiku 5.5 (prompts up to 100K) | $0.10 | $0.50 | $0.01 (0.1×) | $0.125 / $0.20 |
| Haiku 4.5 | $1.00 | $5.00 | $0.10 (0.1×) | $1.25 / $2.00 |

(Sonnet 5.5 now costs exactly half of Opus 5.5 at every rate in the table. Haiku 5.5 is priced by prompt length: its row covers prompts up to 100K tokens (cache reads and writes count toward that length), and a longer prompt bills every rate at 5×. Claude models from 4.7 on use a tokenizer that yields roughly 30% more tokens for the same text, so a per-token comparison against an older model such as Haiku 4.5 understates the newer model's real cost: it hides part of the gap for a model that costs more per token, and overstates Haiku 5.5's saving. Batch API runs at 50% of list.)

### MCP hygiene
<!-- cc: lean.mcp -->

- Tool schemas are **deferred by default**: only tool names and server instructions load upfront; full schemas load on demand via tool search. `ENABLE_TOOL_SEARCH` tunes this (`auto` = load schemas upfront while they total under 10% of the window — up to ~100K tokens on a 1M window, so prefer the default or a small `auto:N`; `false` = all upfront; per-server `alwaysLoad: true` exempts a server). Since 2.1.304 deferral stays on behind a custom `ANTHROPIC_BASE_URL`. From 2.1.305, a 400 or 422 whose cause Claude Code doesn't recognize is retried without tool search, and MCP tools then load upfront. Deferral still falls back to upfront loading on models older than Opus 4, Sonnet 4 and Haiku 4.5 (older than the 4.5 generation on Google Cloud's Agent Platform) and on a Microsoft Foundry deployment hosted on Azure, and `ENABLE_TOOL_SEARCH=true` lifts neither fallback. `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` keeps tool search off whatever `ENABLE_TOOL_SEARCH` says (managed settings can keep it on, 2.1.227+, except in a session that gets the HIPAA configuration, where neither turns it back on) ⚠.
- `MAX_MCP_OUTPUT_TOKENS` (default 25,000) caps tool-result size; a successful result with no image content over the cap is written to disk and referenced instead of inlined. For a call that completes in the foreground, error text over ~11,000 characters keeps only its first and last 5,000, and a second threshold ignores this variable: a successful text result over 50,000 characters also goes to disk. A call moved to a background task reports through its task notification instead. A tool that declares `anthropic/maxResultSizeChars` uses that value for its text in place of both limits (ceiling 500,000 characters); image results stay under the token cap ⚠.
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
