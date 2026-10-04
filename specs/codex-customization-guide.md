# Codex Customization Guide

**Skills · slash commands · subagents · AGENTS.md · permissions · hooks — built and run on a token budget**

> Verified against the [official Codex manual](https://developers.openai.com/codex/codex-manual.md) and its source documentation on **October 3, 2026**. Local CLI command and flag checks used **codex-cli 0.154.0**. Items marked ⚠ are especially version-sensitive. Check `codex --version`, `codex --help`, and the linked reference before adopting exact fields. CLI, IDE, desktop, and cloud experiences share concepts but have different controls and execution environments; a local configuration example does not establish cloud support.

This is the Codex counterpart of the [Claude Code Customization Guide](claude-code-customization-guide.md). It preserves that guide's organizing principle: customization should improve reliability without making every task pay for every workflow. Product behavior is sourced; budgeting and workflow recommendations are practical guidance.

## 1. The organizing constraint: context

Every instruction, tool result, and file excerpt competes with the task for space and attention. Keep durable context small, load specialized procedures when needed, and preserve expensive results as artifacts rather than repeatedly regenerating them.

| Component | When it enters context | Cost profile |
|---|---|---|
| Built-in instructions and tool definitions | Supplied by the active client and runtime | Baseline overhead; varies with model, client, and enabled capabilities |
| Global and applicable project `AGENTS.md` files | Collected for the session's working directory | Persistent prose; keep the instruction chain concise |
| Available skill catalog | Discovery metadata before selection | Names, descriptions, and paths consume a bounded catalog budget ⚠ |
| Selected `SKILL.md` body | When a skill is invoked or selected | Full procedure becomes task context |
| Skill references and helper output | When read or executed | Cheap while dormant; large reference dumps and script output still cost tokens |
| Local memories | When enabled and relevant memories are injected | Helpful recall with its own generation and context costs ⚠ |
| MCP and plugin tools | As the client exposes or discovers capabilities | Tool metadata, schemas, and returned data can all contribute; inspect the active setup |
| Conversation, file reads, command output | Accumulates during work | Usually the largest controllable source of growth |
| Subagent work | In separate agent threads | Reduces clutter in the main thread; still consumes usage across the team |
| Hook output | When an event's contract adds feedback or context | Running a script needs no model inference, but injected output and follow-up turns consume tokens |

In the **CLI**, use `/status` for active configuration, token use, and remaining context; `/statusline` can show context and token counters continuously. `/usage` reports account token activity when supported by the session's authentication. `codex doctor --summary` checks installation and configuration health; `/debug-config` explains active layers and policy constraints. These are different measurements: context capacity, account usage, and installation health. [CLI commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli)

Each mechanism handles a different kind of context:

- **`AGENTS.md`** supplies durable conventions before work starts.
- **Skills** defer detailed procedures until the task needs them.
- **Subagents** keep bounded investigations and reviews in their own threads.
- **Hooks and existing checks** move mechanical work out of model reasoning.
- **Permission profiles and command rules** enforce access and execution boundaries.
- **MCP and plugins** retrieve live context and expose actions when a workflow needs them.

Measure the current setup before changing it. Removing the command that tells Codex how to verify a change can save a few tokens while causing much more expensive trial and error.

## 2. Choosing the right mechanism

| The requirement is… | Put it in… | Why |
|---|---|---|
| A constraint for this task or chat | The prompt or chat | Keeps temporary decisions out of every future session |
| Short, durable repository guidance | `AGENTS.md` | Applies consistently when working in the repository |
| Guidance for a particular module | A nested `AGENTS.md` | Associates conventions with the directory where they matter |
| A reusable procedure or domain reference | A skill | Supports instructions, references, scripts, and progressive disclosure |
| A workflow that should be selected explicitly | A skill with implicit invocation disabled | Avoids automatic selection; permissions still govern its actions |
| Bounded exploration, tests, or an independent review | A subagent | Separates responsibility and exploration from the main thread |
| A deterministic lifecycle check | A synchronous hook and an existing check script | Executes at a defined event with documented feedback or blocking behavior |
| A file or network access boundary for local commands | Permission configuration | Enforced by the execution environment |
| A decision about commands outside the sandbox | An execution-policy `.rules` file | Matches command prefixes and decides allow, prompt, or forbid |
| Model, reasoning, MCP, or other persistent defaults | `config.toml` | Separates runtime settings from natural-language guidance |
| Live external data or an external action | An MCP server or app connector | Uses an authorized integration rather than stale copied context |
| A distributable bundle of skills and integrations | A plugin | Packages reusable capabilities for installation and sharing |
| A recurring check or follow-up | A scheduled task | Defines when to run a stable prompt or skill |

**Instructions guide behavior; execution controls enforce their own boundaries.** A skill saying “only inspect files” is useful role guidance. A read-only sandbox constrains local commands. A hook can block supported operations when it is trusted, matched, synchronous, and returns a supported decision. CI remains the durable acceptance gate for code that must pass checks regardless of which client produced it. [Customization](https://learn.chatgpt.com/docs/customization/overview), [permissions](https://learn.chatgpt.com/docs/permissions), [hooks](https://learn.chatgpt.com/docs/hooks)

## 3. Skills

A skill is a directory containing `SKILL.md`, with optional files for deeper knowledge and deterministic helpers:

```text
release-preview/
├── SKILL.md
├── agents/
│   └── openai.yaml   # optional Codex metadata and invocation policy
├── references/
├── scripts/
└── assets/
```

The portable core is the skill's name, description, and Markdown procedure. Codex-specific settings belong in the supported metadata format; Claude Code frontmatter does not automatically acquire the same meaning in Codex. [Build skills](https://learn.chatgpt.com/docs/build-skills)

### Where skills live ⚠

| Location | Intended scope |
|---|---|
| `$HOME/.agents/skills/<name>/` | Personal skills across repositories |
| `.agents/skills/<name>/` along the current directory's ancestor chain to the repository root | Repository and directory-local workflows |
| `/etc/codex/skills/<name>/` | Administrator-provided local skills |
| Bundled system skills and enabled plugin skills | Capabilities supplied by the runtime or an installed bundle |

Codex supports symlinked skill folders, which is useful for a version-controlled personal skills repository. Discovery locations are distinct from `CODEX_HOME`: current shared personal skills use `~/.agents/skills/`; `~/.codex` is the default home for Codex configuration and state. [Build skills](https://learn.chatgpt.com/docs/build-skills)

Use unique names when several skill sources are active. Codex documentation says same-name skills are kept rather than merged; do not rely on Claude Code's same-name shadowing hierarchy to choose the desired procedure. Select the intended skill and inspect its path when diagnosing a collision. [Build skills](https://learn.chatgpt.com/docs/build-skills)

### `SKILL.md`: the portable procedure

```markdown
---
name: release-preview
description: Use when preparing release notes or checking release readiness from an existing Git diff and saved verification results.
---

1. Identify the requested base and head revisions. Ask if either is missing.
2. Read the diff and the saved verification report named by the user.
3. Draft release notes grouped by user-visible behavior.
4. List unresolved checks with their evidence paths.
5. Return the draft and readiness assessment for review.
```

`name` and `description` are required. Make the description specific enough to route requests: state the job, the situations that call for it, and the inputs it needs. Keep examples and detailed workflow steps in the body; they need not be paid for in the discovery catalog. [Build skills](https://learn.chatgpt.com/docs/build-skills)

### `agents/openai.yaml`: Codex metadata ⚠

```yaml
interface:
  display_name: "Release Preview"
  short_description: "Draft release notes from a diff and saved checks"
  default_prompt: "Use $release-preview to draft release notes from the revisions and verification report I provide."
policy:
  allow_implicit_invocation: false
```

| Field family | Purpose |
|---|---|
| `interface.display_name`, `short_description`, `default_prompt` | Presentation and suggested invocation text |
| `interface.icon_small`, `icon_large`, `brand_color` | Optional visual identity |
| `policy.allow_implicit_invocation` | Whether Codex may select the skill without explicit invocation; default is `true` |
| `dependencies.tools` | Declared tool dependencies, including supported MCP integration metadata |

`allow_implicit_invocation: false` is the Codex control for explicit selection. It is **not an authorization gate**: explicitly selecting a skill does not automatically authorize every deployment, publication, or external message its procedure might describe. Keep action scope explicit and use the appropriate permission and review controls. [Build skills](https://learn.chatgpt.com/docs/build-skills)

Avoid importing Claude-specific fields such as `context: fork`, `allowed-tools`, `model`, or `hooks` and assuming they control Codex execution. Use Codex subagent definitions, runtime configuration, and lifecycle-hook configuration for those purposes.

### Invocation and arguments

In the CLI and IDE, use `/skills` to browse skills or mention one with `$skill-name`. The desktop app also supports explicit `$skill-name` invocation. Codex can select implicitly eligible skills when their descriptions match the task. [Build skills](https://learn.chatgpt.com/docs/build-skills)

```text
Use $release-preview for base v1.4.0 and head HEAD.
Use the saved report at artifacts/release-checks.txt.
```

Pass inputs as task context and define their expected shape in the procedure. The skill format does not establish Claude's `$ARGUMENTS`, `$0`, `${CLAUDE_SKILL_DIR}`, or inline shell-preprocessing behavior. If a workflow needs live state, instruct Codex to read it or run a bundled helper through an ordinary tool call. Its output then has the usual permission and token costs.

### The catalog budget ⚠

Codex budgets its available-skills catalog. Current documentation describes a default of **2% of the model context window** and an **8,000-character fallback** when the window size is unknown. `skills.max_context_tokens` sets an explicit token budget, capped at **10,000 tokens**. Under pressure, descriptions can be shortened and skills may be omitted with a warning; the documented behavior does not establish Claude's least-invoked-first removal policy. [Build skills](https://learn.chatgpt.com/docs/build-skills), [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)

Practical response to pressure:

- Tighten descriptions without removing useful trigger phrases.
- Disable skills and plugins that have no current use.
- Split a broad skill into focused workflows only when that improves selection and execution; splitting also adds catalog entries.
- Increase the catalog budget deliberately when the active set earns its cost.

### Progressive disclosure and iteration

Keep three levels distinct: discovery metadata → the selected procedure → specific reference files or helper output. A short index pointing to one relevant reference is cheaper than instructions to read the entire `references/` directory.

| Symptom | Adjustment |
|---|---|
| Skill is missed on relevant requests | Add the concrete phrases and inputs that actually occur |
| Skill is selected for unrelated work | Narrow its scope; disable implicit invocation when explicit selection is appropriate |
| Skill loads but required steps are skipped | Shorten the procedure; name checkpoints, outputs, and exit conditions |
| Deterministic logic is repeatedly re-derived | Bundle a helper script with a clear contract |
| Every request loads too much supporting material | Replace blanket reads with conditional references |
| Skill depends on an unavailable integration | Declare the dependency and verify connection and authorization |

Test representative tasks both with and without the skill. Evaluate the artifact and checks it produces, not just whether the skill was mentioned. [Build skills](https://learn.chatgpt.com/docs/build-skills)

## 4. Slash commands

Built-in slash commands control the client; skills provide reusable workflows. A skill named `release-preview` does not create a Claude-style `/release-preview` command. Use explicit skill invocation through `$release-preview` or the skill picker. [CLI commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli), [build skills](https://learn.chatgpt.com/docs/build-skills)

### Useful CLI commands ⚠

| Command | Use |
|---|---|
| `/status`, `/statusline`, `/usage` | Inspect configuration, context, tokens, and supported account activity |
| `/debug-config` | Explain configuration layers and requirements |
| `/model` | Choose an available model and supported reasoning settings |
| `/plan` | Gather context and develop a plan before implementation |
| `/skills`, `/mcp`, `/plugins`, `/apps` | Inspect or select relevant capabilities |
| `/hooks` | Review, trust, inspect, or disable non-managed hooks |
| `/permissions` | Adjust available permission settings for the session |
| `/compact` | Reduce active history while retaining a summary |
| `/new`, `/clear` | Start a fresh chat; `/clear` also clears the terminal display |
| `/resume`, `/fork` | Continue saved work or branch an existing transcript |
| `/agent` or `/subagents` | Inspect or switch among active agent threads |
| `/diff`, `/review` | Inspect changes and request review |
| `/goal` | Manage a persistent, measurable objective in supporting builds |

Discover the installed client's commands from its `/` menu. IDE and desktop menus differ from the CLI list; do not assume a command exists on every surface. [CLI commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli)

### Legacy custom prompts ⚠

Codex's older custom-prompt mechanism uses Markdown files in `~/.codex/prompts/`, invoked with `/prompts:<name>`. It supports prompt-template argument substitution, but it is deprecated in favor of skills. It is a separate mechanism from Claude's `.claude/commands/` and from Codex's current skill format. For a new reusable workflow, author a skill with its references and helpers together. [Custom prompts](https://learn.chatgpt.com/docs/custom-prompts)

## 5. Subagents

Subagents delegate bounded work to specialized agent threads. Use them when a task can produce a compact result the main agent can act on: file locations, a test report, an independent review, or an implementation in a clearly owned area. Current Codex multi-agent collaboration is enabled by default; custom-agent configuration is evolving ⚠. [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)

### Definitions and settings ⚠

Current custom agents are standalone TOML files:

| Location | Scope |
|---|---|
| `~/.codex/agents/<name>.toml` | Personal role definitions |
| `.codex/agents/<name>.toml` | Project role definitions |

Example `.codex/agents/review-reader.toml`:

```toml
name = "review-reader"
description = "Inspect a supplied diff for correctness and requirement gaps; return findings with file and line references."
sandbox_mode = "read-only"
developer_instructions = """
Read the supplied task brief and diff before judging the change.
Report actionable correctness and requirement gaps with evidence.
Do not edit files, change Git state, or expand the review without a named reason.
Return a concise verdict and findings the caller can act on.
"""
```

| Field | Purpose |
|---|---|
| `name` | Required agent identity; duplicate names and built-in-name collisions affect discovery |
| `description` | Required delegation guidance |
| `developer_instructions` | Required role instructions |
| `model`, `model_reasoning_effort` | Optional overrides of the model and effort resolved for the subagent |
| `sandbox_mode` | Optional local execution setting; parent live overrides and managed requirements still apply |
| Supported additional config, such as MCP configuration | Role-specific configuration where the reference permits it |

Built-in roles include `default`, `worker`, and `explorer`. Avoid reusing a built-in name accidentally: a custom definition can shadow that role. The configuration reference also includes `[agents.<name>]` registration fields; check your version before adapting an older registered-agent setup. [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents), [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)

A role instruction is not a tool-removal manifest. Do not translate Claude's `tools: Read, Grep, Glob` into an unsupported Codex allowlist. Apply supported sandbox and integration controls, then state the role contract in `developer_instructions`.

Model and effort resolution considers explicit spawn settings, `[agents]` defaults, and the parent session, then applies the agent file's overrides. Set both fields when a role requires a specific combination. Parent live sandbox and approval overrides are reapplied at spawn, so the example's `sandbox_mode` alone is not proof that the effective child permissions are read-only; verify them in the active runtime. [Subagent inheritance](https://learn.chatgpt.com/docs/agent-configuration/subagents)

### Context and ownership

Codex manages agents as separate threads and carries applicable configuration and permissions into delegation. The precise history passed to an agent depends on the runtime and dispatch mechanism; do not assume that every subagent starts with no parent history or that only a summary can ever return. Construct a bounded brief anyway: objective, relevant paths, inputs, constraints, and an output contract. [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)

Agents can share a checkout. Separate threads do not isolate filesystem edits. Give each implementer clear ownership, and use separate Git worktrees when concurrent work would collide. A reviewer should receive the diff and acceptance criteria; a test runner should receive the exact command and directory. [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents), [worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees)

### When delegation pays

- Reading many files to answer one narrow question.
- Independent investigations that can run concurrently.
- Review where a separate assessment adds value.
- A bounded test run whose detailed log belongs in an artifact.

It adds overhead when the task is smaller than its dispatch, when the main agent must repeat the same exploration, or when several agents edit the same module. More parallelism reduces elapsed time only when the work is separable; it can increase total usage.

Current concurrency configuration includes `agents.max_concurrent_threads_per_session`; `agents.max_threads` remains a legacy alias ⚠. Set limits from actual workload and usage, not the largest available value. [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)

### Model routing

Use inherited settings until a role has a demonstrated reason to differ. Compare an efficient available model for mechanical search or report generation with a stronger model for ambiguous architecture and correctness review. Check supported reasoning levels for that model; raise effort only when more reasoning is useful. Availability comes from the active account, workspace, and client, not from a model name written in a file. [Model selection](https://learn.chatgpt.com/docs/model-selection), [CLI commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli)

## 6. Rules: AGENTS.md, settings, permissions, and command policies

### `AGENTS.md` discipline

Include commands Codex cannot infer reliably, directory routing, local conventions, environment quirks, and the checks that prove completion. Link detailed procedures rather than inlining every workflow. A useful test for each instruction is: “What recurring mistake does this prevent?”

This repository already uses a small Codex entry point that directs the agent to `CLAUDE.md`, the canonical cross-runtime maintainer guide. That indirection is a repository convention: Codex does not automatically import `CLAUDE.md` merely because the file exists. [Custom instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

### Discovery, overrides, and size ⚠

Codex collects an instruction chain at session start:

1. In `CODEX_HOME` (normally `~/.codex`), use the first nonempty candidate: `AGENTS.override.md`, then `AGENTS.md`.
2. Walk from the detected project root toward the current working directory.
3. In each directory, use the first applicable file: `AGENTS.override.md`, `AGENTS.md`, then configured fallback filenames. Empty files are skipped.
4. Concatenate applicable guidance from broad to specific; nearer guidance takes precedence when instructions conflict.

Only one instruction file is selected per directory. An override file replaces that directory's normal candidate; it does not erase the rest of the chain. The dedicated AGENTS guide describes a default **32 KiB combined instruction limit**, configurable through `project_doc_max_bytes`. Keep comfortably below it and inspect loading if a large instruction chain is incomplete. [Custom instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

Nested `AGENTS.md` files express guidance for their subtree, but the documented startup discovery follows the current directory's ancestry. Do not assume Claude's file-touch-triggered lazy loading. Start Codex in the relevant directory and confirm the guidance it sees when diagnosing scope issues. A Markdown link or instruction to read another file is also distinct from Claude's automatic `@path` import syntax. [Custom instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

### Local memories ⚠

Local Codex memories are optional, generated recall under `~/.codex/memories/`. Current documentation says they are off by default. `/memories` controls use and generation for a chat; global settings live in configuration and desktop personalization controls. Memory generation happens in the background and can be skipped when remaining quota is low. [Memories](https://learn.chatgpt.com/docs/customization/memories)

Keep required team rules in `AGENTS.md` or checked-in documentation. Treat the memory directory as generated state, not as a manually maintained instruction file. Codex local memories and ChatGPT web memory have different storage and controls; Claude's first-200-lines `MEMORY.md` rule does not describe this system. [Memories](https://learn.chatgpt.com/docs/customization/memories)

### Configuration precedence ⚠

The normal local configuration order, highest to lowest, is:

1. CLI flags and `--config` overrides.
2. Trusted project `.codex/config.toml` layers, with the nearest directory winning.
3. The selected `~/.codex/<profile-name>.config.toml` file.
4. User `~/.codex/config.toml`.
5. Cloud-managed configuration defaults, when delivered for the signed-in workspace.
6. System configuration, such as `/etc/codex/config.toml` on Unix.
7. Built-in defaults.

Managed requirements constrain the resolved configuration; they are not another ordinary preference file that a CLI flag can overrule. Untrusted projects skip project `.codex/` layers, including local configuration, hooks, and execution rules. Some host-owned settings are ignored in project config even when the project is trusted; consult the restricted-key list before moving user settings into a repository. [Config basics](https://learn.chatgpt.com/docs/config-file/config-basic), [advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced#project-config-files-codexconfigtoml)

Relative paths in project `config.toml` resolve from the containing `.codex/` directory. Use explicit paths when a setting's path base matters. The CLI, IDE, and desktop local host share configuration layers; web execution does not read your laptop's TOML files. [Advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced), [MCP](https://learn.chatgpt.com/docs/extend/mcp)

Named CLI configuration profiles now use separate files:

```toml
# ~/.codex/review.config.toml
model_reasoning_effort = "medium"
approval_policy = "on-request"
default_permissions = ":read-only"
```

```bash
codex --profile review
```

Since Codex **0.134.0**, `--profile` no longer reads `[profiles.review]` from the base file, and the old top-level `profile` selector is removed. A configuration profile supplies defaults; it can be overridden by project settings and CLI flags. A named **permission profile** defines access policy. The two uses of “profile” are separate. [Profiles](https://learn.chatgpt.com/docs/config-file/config-advanced#profiles)

### Sandbox and approval are separate

The sandbox constrains local command execution. Approval policy decides when Codex asks to step beyond current permissions. `approval_policy = "never"` removes approval prompts; it does not remove the sandbox. Automatic review can evaluate approval requests, but it does not expand the approved task's scope. [Agent approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security), [auto-review](https://learn.chatgpt.com/docs/auto-review)

With the older settings, `read-only`, `workspace-write`, and `danger-full-access` are sandbox modes. Workspace-write generally permits the project and temporary directories while protecting paths such as `.git`, `.agents`, and `.codex`. A writable project root does not guarantee that its configuration or Git metadata is writable. [Agent approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security#protected-paths-in-writable-roots)

Local command network settings also do not describe every hosted web tool, connector, or MCP action. Review the relevant integration's authorization and runtime policy separately. [Agent approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security#network-isolation)

### Named permission profiles ⚠

Permission profiles are **beta**, supported by current local clients, with a **0.138.0** compatibility floor in the managed rollout guidance. Prefer extending a built-in baseline so its protections remain in place:

```toml
# ~/.codex/config.toml, or a trusted project .codex/config.toml
default_permissions = "project-edit"
approval_policy = "on-request"

[permissions.project-edit]
description = "Edit the workspace with environment files excluded."
extends = ":workspace"

[permissions.project-edit.filesystem]
glob_scan_max_depth = 3

[permissions.project-edit.filesystem.":workspace_roots"]
"**/*.env" = "deny"

[permissions.project-edit.network]
enabled = false
```

The deny glob has platform-specific limits. Linux, WSL, and native Windows may expand matches before sandbox startup; `glob_scan_max_depth = 3` bounds that scan, and deeper or newly created matching files may not be covered by the snapshot. Choose a sufficient bound or explicit paths for the actual repository, and test denied reads on the deployed platform. [Deny-read patterns](https://learn.chatgpt.com/docs/permissions#deny-reads-with-exact-paths-or-globs)

Do not combine this with `sandbox_mode` or `[sandbox_workspace_write]`. Current docs say a legacy `sandbox_mode` in any loaded layer, or the CLI's `--sandbox`, selects the older mechanism instead. Managed `allowed_permission_profiles` is an exception that forces permission-profile use. Remove old settings deliberately when migrating. [Permissions](https://learn.chatgpt.com/docs/permissions)

When enabling domain-restricted command networking, `network.enabled = true` is insufficient by itself: the network proxy must also be active for domain rules to constrain direct access. Use the documented profile and proxy setup rather than assuming the allowlist is enforced. [Permissions](https://learn.chatgpt.com/docs/permissions)

Older compatible local-command configuration, as a separate alternative:

```toml
approval_policy = "on-request"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = false
```

`approval_policy = "untrusted"` is retired in current builds and can prevent startup; do not copy it from an old example. Project trust is configured separately. [Migration guidance](https://learn.chatgpt.com/docs/agent-approvals-security#migrate-from-the-retired-untrusted-approval-policy)

### Execution-policy `.rules` files ⚠

Codex execution rules are experimental Starlark-style command policy, not Markdown guidance. Codex discovers `.rules` files under `rules/` beside active config layers; trusted project rules can live in `.codex/rules/`. They decide whether matching commands may run **outside the sandbox**. The strictest matching decision wins: `forbidden` → `prompt` → `allow`. [Rules](https://learn.chatgpt.com/docs/agent-configuration/rules)

Example `.codex/rules/release.rules`:

```python
prefix_rule(
    pattern = ["git", "push"],
    decision = "prompt",
    justification = "Review the destination and commits before publishing.",
    match = ["git push origin release"],
    not_match = ["git status"],
)
```

The fence highlights a Starlark policy example; it is not a Python program. Check matching without executing the target command:

```bash
codex execpolicy check --rules .codex/rules/release.rules -- git push origin release
```

Match argv prefixes, not arbitrary shell substrings. Shell wrappers, compound commands, and prefix breadth need deliberate testing. These rules govern execution decisions; they do not prove that an external action is appropriate or that every tool path is covered. [Rules](https://learn.chatgpt.com/docs/agent-configuration/rules)

Codex does not use Claude's `Bash(uv run:*)` syntax or `.claude/rules/*.md` `paths` frontmatter here. Put directory guidance in `AGENTS.md`, workflow knowledge in skills, and access decisions in the supported enforcement layer.

## 7. Hooks

Codex supports lifecycle hooks in current local releases. Configure them in `hooks.json` beside an active config layer, inline `[hooks]` tables in `config.toml`, or an enabled plugin's hook bundle. Matching sources **accumulate**; a higher-precedence configuration layer does not replace all lower-layer hooks. If one layer contains both JSON and inline hook configuration, Codex merges them and warns. [Hooks](https://learn.chatgpt.com/docs/hooks)

Typical local locations are `~/.codex/hooks.json` and project `.codex/hooks.json`. Project hooks require project trust. In addition, non-managed hooks require review and trust of their exact definition; changed definitions are skipped until trusted again. Use `/hooks` to inspect them. Managed hooks have separate policy control and cannot be disabled from the user hook browser. [Hook trust](https://learn.chatgpt.com/docs/hooks#review-and-trust-hooks)

### Events and supported control ⚠

| Event | Useful behavior |
|---|---|
| `PreToolUse` | Block supported calls, add context, or rewrite supported arguments |
| `PermissionRequest` | Allow, deny, or leave an approval request to the normal flow |
| `PostToolUse` | Add feedback after output; a blocking result replaces or withholds output, not completed side effects |
| `UserPromptSubmit` | Add context or reject a prompt before processing |
| `Stop` | Request another model step with a reason before the main turn finishes |
| `SubagentStop` | Apply a continuation check to a subagent |
| `SessionStart` | Inject context on startup, resume, clear, or compact |
| `SubagentStart` | Inject context into a new subagent |
| `PreCompact`, `PostCompact` | Observe compaction or use the supported stop-control response |
| `Interrupt` | Main-thread interruption cleanup; does not run for subagents |
| `SessionEnd` | Advisory main-thread cleanup; does not keep the thread open |

Current handlers support **`command`** and **`mcp_tool`**. `prompt` and `agent` handler types may parse but are skipped. Compatibility with a field or event name in another agent's schema does not establish Codex behavior. [Hooks](https://learn.chatgpt.com/docs/hooks)

### Input, exits, and JSON

Command hooks receive JSON on stdin. Common fields include `session_id`, `transcript_path`, `cwd`, and `hook_event_name`; event-specific inputs add tool arguments, prompt text, or stop state. The event contract determines what stdout means:

- **Exit 0:** complete normally; supported structured output can still make a decision.
- **Exit 2:** blocking or corrective feedback on supporting events, with the reason on **stderr**.
- **Other nonzero exits:** hook failure, not a universal policy deny.
- Plain stdout becomes context on supporting events such as `SessionStart` and `UserPromptSubmit`; it is ignored for events such as `PreToolUse`.

For `PreToolUse`, use the supported `hookSpecificOutput.permissionDecision` contract. `permissionDecision: "ask"` and several compatibility fields are currently unsupported; they can produce a hook error while the original tool proceeds. Validate the specific event contract before depending on a gate. [PreToolUse](https://learn.chatgpt.com/docs/hooks#pretooluse)

### Pattern 1: block a supported call with a corrective message

Example `.codex/hooks.json` for a Git repository with `jq` installed:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "^Bash$",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$(git rev-parse --show-toplevel)/.codex/hooks/pre-command.sh\"",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

Example `.codex/hooks/pre-command.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
task_command=$(jq -r '.tool_input.command // empty')
if [[ "$task_command" == *"pip install"* ]]; then
  echo "This project uses uv. Use the documented uv command for this task." >&2
  exit 2
fi
exit 0
```

This is a lightweight workflow correction for a literal command phrase. It does not cover every spelling or indirect way of installing packages; a string check is not a complete command-security policy.

Hook `Bash` is the documented canonical name for shell calls. `apply_patch` also has `Edit` and `Write` matcher aliases, but its input is patch text in `tool_input.command`; it does not use Claude's `tool_input.file_path` contract. Check the actual payload before adapting a formatter. [Tool coverage](https://learn.chatgpt.com/docs/hooks#tool-coverage), [PreToolUse](https://learn.chatgpt.com/docs/hooks#pretooluse)

### Pattern 2: validate before a turn finishes

Example inline TOML, with a repository check script that accepts no input and exits nonzero on failure:

```toml
[[hooks.Stop]]

[[hooks.Stop.hooks]]
type = "command"
command = 'bash "$(git rev-parse --show-toplevel)/.codex/hooks/check-stop.sh"'
timeout = 30
```

Example `.codex/hooks/check-stop.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
task_hook_input=$(cat)
if jq -e '.stop_hook_active == true' >/dev/null <<< "$task_hook_input"; then
  exit 0
fi
task_repo_root=$(git rev-parse --show-toplevel)
if task_check_output=$(cd "$task_repo_root" && bash scripts/check.sh 2>&1); then
  exit 0
fi
printf '%s\n' "$task_check_output" >&2
echo "Resolve the reported check failures before finishing." >&2
exit 2
```

The `stop_hook_active` check avoids an endless continuation loop. It also means this example is a corrective checkpoint rather than a permanent guarantee of a green build: the next continuation still needs to fix and verify the failure, and CI should enforce acceptance. Choose a timeout that fits the intended fast check; keep long suites explicit. [Stop](https://learn.chatgpt.com/docs/hooks#stop)

### Patterns 3 and 4: post-edit checks and session context

For `PostToolUse` on `apply_patch`, invoke a fast checker or formatter that understands patch input or determines affected files from a reliable repository state. The original edit has already happened; feedback can guide the next model step but cannot prevent that edit retroactively.

For `SessionStart`, inject a small summary of useful live state: the selected work item, a saved check report, or a pointer to current notes. Large hook text consumes context; `additionalContextLimit` can bound the preview while preserving full output on disk. Avoid injecting whole transcripts. [PostToolUse](https://learn.chatgpt.com/docs/hooks#posttooluse), [large hook output](https://learn.chatgpt.com/docs/hooks#large-hook-output)

### Pitfalls and surface limits ⚠

- Matching command hooks for the same event run concurrently; one cannot prevent another from starting. Combine ordered steps inside one handler.
- `async: true` handlers provide later informational output; they cannot block, approve, or rewrite the operation that triggered them.
- Command hooks run from the session's `cwd`; resolve repository paths deliberately so starting from a subdirectory works.
- `SessionEnd` and `Interrupt` have short default timeouts and a three-second maximum; do not put long checks there.
- Hook errors are not all fail-closed. Test ordinary success, rejection, malformed input, and missing dependencies before trusting an enforcement check.
- Local-only execution supports the documented local hook setup. Cloud orchestration has separate, narrower support for administrator-defined MCP hooks where enabled; local command and plugin hooks do not automatically carry over.

[Hook behavior and scope](https://learn.chatgpt.com/docs/hooks), [cloud orchestration configuration](https://learn.chatgpt.com/docs/config-file/config-advanced#applying-these-examples-to-local-computer-access-with-work-cloud)

### Notifications are a separate mechanism

`notify` runs an external program for supported notifications, currently `agent-turn-complete`, with its JSON payload as a command-line argument. It is not a substitute for a `PreToolUse` policy hook. `tui.notifications` and the terminal notification method control another notification surface. Put machine-local notification commands in user configuration; current project config ignores `notify`. [Notifications](https://learn.chatgpt.com/docs/config-file/config-advanced#notifications)

## 8. Running lean: the token-budget playbook

### Know the measurement you are optimizing

Use `/status` and the status line to watch a CLI session, and use the account usage view to understand shared limits. For scripted runs, `codex exec --json` emits events including completion usage fields such as input, cached input, and output tokens. Save the JSONL as an artifact rather than placing a large run transcript into another conversation. [Non-interactive mode](https://learn.chatgpt.com/docs/noninteractive)

```bash
# Example agent run: save events and the final report separately.
codex exec --sandbox read-only --json \
  --output-last-message artifacts/review.md \
  "Review the supplied diff and report actionable correctness gaps." \
  > artifacts/review-events.jsonl
```

Create `artifacts/` and supply the intended diff or revision scope before running this example. These options were checked against the installed CLI's help; an actual model run also uses account quota. Observability configuration can report per-turn token usage where needed; introducing telemetry is a separate operational choice. [Advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced)

### Session hygiene

- Keep one chat per coherent outcome. Preserve context while the same investigation is active.
- Start a new chat for unrelated work. In the CLI, `/new` starts fresh and `/clear` also clears the visible terminal.
- `/fork` branches the existing transcript; it does not remove its accumulated history. Use it when the branch benefits from that history.
- `/compact` reduces active history. Before a long transition, save decisions, remaining work, and evidence paths in a concise handoff artifact.
- After repeated unsuccessful corrections, improve the reproduction and relevant context before spending more reasoning or starting another agent.
- Let the client manage automatic compaction by default. `model_auto_compact_token_limit` is available when there is a measured need for a different threshold ⚠.

[CLI commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli), [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)

### Caching and usage economics ⚠

Keep stable instructions and tool sets stable during a coherent task, but optimize for correct work first. Cached input can reduce metered cost; it does not make a bloated context small or eliminate the model's attention burden. Codex's exact cache reuse depends on the provider and runtime; do not import Claude's cache-layer invalidation list, cache-write premiums, or subscription TTL rules.

Current **Standard-speed Codex credit rates**, verified October 3, 2026:

| Model | Input credits / 1M tokens | Cached-input credits / 1M tokens | Output credits / 1M tokens |
|---|---:|---:|---:|
| GPT-6 Astra | 250 | 25 | 1,250 |
| GPT-6.1 Sol | 50 | 2.5 | 250 |
| GPT-6 Sol | 50 | 5 | 250 |
| GPT-6 Luna | 2.5 | 0.25 | 12.5 |

These are **credits**, not USD or a formula for included subscription limits. Codex credit billing has no separate cache-write charge. API-key sessions use [API pricing](https://developers.openai.com/api/docs/pricing); enterprise agreements and available credit pricing can differ. Check the current rate card and account dashboard before relying on this snapshot. [Codex pricing](https://learn.chatgpt.com/docs/pricing#token-rates)

Fast service tiers trade usage for latency, with model- and plan-specific availability. They do not imply stronger reasoning. Select a tier because turnaround time matters; compare the resulting usage as well as task duration. [Speed](https://learn.chatgpt.com/docs/agent-configuration/speed)

### Model and effort discipline

Choose an available model appropriate to the task, then use supported reasoning settings. Avoid a universal role-to-model mapping copied from another provider. Measure whether a smaller model meets the quality bar for the actual workload; a cheap run that requires several corrections may cost more than one successful stronger run. [Model selection](https://learn.chatgpt.com/docs/model-selection)

A practical diagnostic order is missing context → clearer decomposition → suitable effort → a different model. Write a handoff artifact when planning and execution need different sessions; that preserves the decisions without carrying the entire planning transcript.

`model` and `model_reasoning_effort` set durable defaults, CLI flags provide one-off choices, and custom-agent definitions can override their own settings. `review_model` optionally changes the model used for review. Verify effective settings rather than assuming a profile or agent file won precedence. [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)

### MCP and plugin hygiene

Use an integration when it removes a concrete manual loop or provides authoritative live context. Codex supports STDIO and Streamable HTTP MCP servers; user and trusted project configuration can define them. For example:

```toml
[mcp_servers.openaiDeveloperDocs]
url = "https://developers.openai.com/mcp"
```

Equivalent CLI setup:

```bash
codex mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp
codex mcp list
```

This server provides documentation search and retrieval. It is a useful source for current OpenAI behavior rather than a reason to preload all documentation. [Docs MCP](https://developers.openai.com/learn/docs-mcp)

- Inspect `/mcp` and enabled plugins before adding another overlapping integration.
- Use MCP `enabled_tools` or `disabled_tools` where supported to scope large tool catalogs.
- Ask for a small relevant query or page, not every item in the connected service.
- Use `tool_output_token_limit` to bound stored tool outputs when warranted, and save full evidence to disk when it matters.
- Use a familiar CLI when it supplies the needed functionality simply; prefer an authorized connector when it provides permissions, structured queries, or hosted access the CLI lacks.

[MCP](https://learn.chatgpt.com/docs/extend/mcp), [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)

A plugin is the installable distribution unit for skills and related capabilities. It may bundle MCP, apps, assets, and hooks. Install a relevant existing bundle before duplicating its integration; author a local skill first when the workflow is personal and still changing. Enabled plugin skills and tools can add context overhead even when the package itself is small. [Plugins](https://learn.chatgpt.com/docs/plugins), [build plugins](https://learn.chatgpt.com/docs/build-plugins)

### Scale ceremony to task size

| Phase | Keep when… | Collapse when… |
|---|---|---|
| Objective and completion evidence | Every task needs an observable result | Keep this concise even for tiny changes |
| Clarification and planning | Scope or approach is uncertain; work spans several components | The requested edit and check are already clear |
| Written spec or handoff | Another session or implementer needs the decisions | A small local edit has no lasting design decision |
| Failing test before implementation | Library or pipeline behavior changes | The change is prose, formatting, or straightforward configuration |
| Subagent | Work is separable or independent review is valuable | Dispatch overhead exceeds the bounded task |
| Review | Correctness matters or work will run unattended | A small change can be inspected directly |
| Verification | Always check the result appropriate to the change | Scale the check; do not replace evidence with confidence |

For a typo, edit and verify. For a small feature, establish acceptance criteria, test the behavior, implement, and verify. For ambiguous work across components, write the decisions down and delegate only the independent parts.

### Guard expensive operations

For simulations, training, large data pulls, full builds, or long suites:

1. Save complete output and metadata immediately: command, inputs or revision, environment, timestamp, and result.
2. Make subsequent review read that artifact rather than regenerate the expensive work.
3. Require explicit workflow selection for costly procedures with `allow_implicit_invocation: false`.
4. Add an appropriate synchronous hook or execution boundary if accidental reruns must be prevented.
5. Rerun when changed inputs, failed checks, or unresolved evidence gaps justify it.

A persisted report is only evidence for the inputs it records. Cheap verification should detect whether those inputs still match before accepting saved results.

### Scheduled tasks and long-running goals ⚠

Use a skill to define the procedure and a scheduled task to define cadence. Current desktop scheduled tasks can operate on local projects or dedicated worktrees; the computer must remain on and the app running for local-file work. A task in an existing chat preserves its context; standalone runs start from their saved prompt. CLI and IDE clients do not provide the Scheduled management interface. [Scheduled tasks](https://learn.chatgpt.com/docs/automations)

Test the workflow manually before scheduling it. State what constitutes a meaningful finding, when to notify, and when to stop. Repeated schedules multiply model, tool, and filesystem costs; frequent worktree runs also require cleanup. Unattended runs use applicable sandbox and organization policies, so tools that require unavailable approvals can fail. [Scheduled tasks](https://learn.chatgpt.com/docs/automations)

A **Goal** gives supporting Codex builds a persistent objective within a chat; a schedule decides when to revisit work. Use a measurable completion condition and supporting artifacts for multi-turn investigations. A normal prompt remains enough for an ordinary edit or explanation. A budget limit means work stopped within its budget, not that the objective was achieved. [Using Goals in Codex](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex)

### Translating a Claude Code setup

| Claude Code concept | Codex counterpart or adaptation |
|---|---|
| `CLAUDE.md` | `AGENTS.md`; explicitly reference a shared maintainer file if desired |
| `.claude/rules/*.md` with `paths` | Nested `AGENTS.md` for subtree guidance; `.rules` means command policy in Codex |
| `.claude/skills/` or `~/.claude/skills/` | Current shared `.agents/skills/` and `~/.agents/skills/` locations |
| `disable-model-invocation: true` | `policy.allow_implicit_invocation: false` in `agents/openai.yaml` |
| `/skill-name` | `$skill-name` or `/skills` selection |
| `.claude/commands/` | A reusable skill; legacy Codex prompt files are a separate deprecated mechanism |
| Markdown agent frontmatter | Codex custom-agent TOML |
| `context: fork` in a skill | Explicit Codex subagent delegation where it fits |
| Claude permission allow/ask/deny strings | Codex permission configuration and prefix execution rules |
| Claude hook configuration | Codex hooks, with its own event payloads, supported decisions, and trust review |
| Claude auto-memory layout and load cap | Optional Codex local memories with their own controls |
| `/context` and Claude cache accounting | Codex `/status`, status-line counters, and Codex or API usage reporting |

## Repository application

This repository's canonical skill content remains under `skills/`. Its installer places Codex skills under `~/.agents/skills/` and generated agent adapters under `~/.codex/agents/`. Canonical agent definitions stay in `agents/`; files under `runtimes/` are generated. Edit the canonical definition, regenerate, and check adapters using the maintainer commands in [CLAUDE.md](../CLAUDE.md).

That arrangement preserves portable procedures while translating runtime-specific manifests. Model pins from Claude definitions do not carry into generated Codex agents here; the adapters inherit the active runtime model. The repository does not generate Codex command adapters: reusable Codex workflows are skills.

## Further reading

- [Customization overview](https://learn.chatgpt.com/docs/customization/overview), [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [memories](https://learn.chatgpt.com/docs/customization/memories).
- [Build skills](https://learn.chatgpt.com/docs/build-skills), [subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents), [hooks](https://learn.chatgpt.com/docs/hooks), [execution rules](https://learn.chatgpt.com/docs/agent-configuration/rules).
- [Config basics](https://learn.chatgpt.com/docs/config-file/config-basic), [advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced), [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference), [managed configuration](https://learn.chatgpt.com/docs/enterprise/managed-configuration).
- [Permissions](https://learn.chatgpt.com/docs/permissions), [agent approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security), [auto-review](https://learn.chatgpt.com/docs/auto-review).
- [CLI commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli), [MCP](https://learn.chatgpt.com/docs/extend/mcp), [plugins](https://learn.chatgpt.com/docs/plugins), [scheduled tasks](https://learn.chatgpt.com/docs/automations).
- [Model selection](https://learn.chatgpt.com/docs/model-selection), [speed tiers](https://learn.chatgpt.com/docs/agent-configuration/speed), [Codex credit pricing](https://learn.chatgpt.com/docs/pricing), [API pricing](https://developers.openai.com/api/docs/pricing).
