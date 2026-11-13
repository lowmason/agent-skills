# Antigravity CLI Customization Guide

**Rules · skills · slash commands · agents · hooks · MCP · plugins · permissions — built and run on a token budget**

<!-- cli-stamp: agy 1.5.7 -->
> Checked on **November 12, 2026** against the [Antigravity documentation](https://antigravity.google/docs) and against local tests with **agy 1.5.7** (`agy --version`). A claim marked *(probed)* comes from those tests. The CLI updated itself from 1.2.17 (released October 5, 2026) to 1.5.7 before the probes started, so every probe ran on 1.5.7. The docs track the newest release. Some pages disagree with each other, and some disagree with the probes. ⚠ marks a claim that is version-sensitive, documented but not tested, or in conflict between sources. Run `agy --version` and `agy --help` before you rely on an exact field. The Antigravity App and IDE read most of the same folders, but this guide covers the CLI only.

This is the counterpart of the [Claude Code Customization Guide](claude-code-customization-guide.md) and the [Codex Customization Guide](codex-customization-guide.md) for the Antigravity CLI (`agy`), Google's successor to Gemini CLI. It keeps their organizing principle: a customization must make the agent more reliable without making every task pay for every workflow. Product behavior comes from the docs or from probes. Budget and workflow advice is practical guidance.

## 1. The organizing constraint: context

Every rule, skill description, tool schema and tool result competes with the task for the model's context window. Keep the always-loaded part small. Load procedures when a task needs them. Save expensive results to files instead of producing them again.

| Component | When it enters context | Cost profile |
|---|---|---|
| Built-in system prompt and tool declarations | Every turn | Fixed overhead. `/context` shows it as System prompt, System tools and System overhead |
| `AGENTS.md`, `GEMINI.md`, `always_on` and global rules | Every turn | Full text, inside a 20,000-token rules budget ⚠ |
| `model_decision` rules | Every turn, as a path and a description | The body loads only when the agent reads it *(probed)* |
| `glob` rules | When the agent works on a matching file | Full text while active ⚠ |
| Skill catalog | Every turn: the name and description of each skill | Grows with every skill and every enabled plugin |
| A selected `SKILL.md` | When the agent or the user activates the skill | The full procedure enters the task context |
| Skill references and script output | When read or run | Free while dormant. Large reads still cost tokens |
| MCP tools | Lazy by default: the server path and tool names each turn | A tool marked `eager` sends its full schema every turn |
| Subagents | In their own conversations | Keeps the main context clean. Their tokens still count against your quota |
| Hook output | When a hook injects steps | A script costs no tokens. Injected text does |
| Conversation, file reads, command output | Accumulates during work | Usually the largest source of growth |

Rules have their own 20,000-token budget. Skills, subagents, workflows and MCP tools share a separate customization budget. The docs do not give its size ⚠. [Rules](https://antigravity.google/docs/rules)

In the CLI, `/context` shows token use by category: system prompt, rules, skills, subagents, plugins, MCP tools, conversation and free space. It also lists compaction checkpoints and the rule and skill files in use. `/usage` (alias `/quota`) shows the remaining model quota. `/credits` shows AI credits. A headless run with `--output-format json` reports `input_tokens`, `output_tokens`, `thinking_tokens`, `cache_read_tokens` and `total_tokens` *(probed)*. These measure three different things: the context window, the plan quota and the cost of one run. [/context](https://antigravity.google/docs/cli/commands/context), [/usage](https://antigravity.google/docs/cli/commands/usage), [headless mode](https://antigravity.google/docs/cli/headless)

Each mechanism handles a different kind of context:

- **Rules** (`AGENTS.md`, `GEMINI.md`, `.agents/rules/`) give durable conventions before work starts.
- **Skills** hold procedures until a task needs them. Each skill is also a slash command.
- **Custom agents** keep bounded investigations and reviews in separate conversations.
- **Hooks** move mechanical checks out of model reasoning.
- **Permission rules and the terminal sandbox** set access and execution boundaries.
- **MCP servers and plugins** supply live data and actions.

Measure before you cut. A removed line that told the agent how to check a change can cost far more in trial and error than it saved.

## 2. Choosing the right mechanism

| The requirement is… | Put it in… | Why |
|---|---|---|
| A constraint for this task only | The prompt | Keeps it out of every future session |
| Short, durable repository guidance | `AGENTS.md` or `GEMINI.md` at the repository root | Loads every turn for a session started in the repository |
| Guidance for one file type | A rule in `.agents/rules/` with `trigger: glob` | Loads when the agent works on matching files |
| A long domain guide needed now and then | A rule with `trigger: model_decision` | Costs a path and a description until the agent reads it |
| A reusable procedure | A skill | Holds references and scripts, and doubles as a slash command |
| A bounded investigation or an independent review | A custom agent that the main agent starts as a subagent | Runs in its own conversation with its own tool allowlist |
| A different persona for a whole session | A custom agent started with `agy --agent <name>` | Replaces the default agent for that session |
| A deterministic check at a lifecycle event | A hook | Runs a command at a defined point in the loop |
| A file, URL or command boundary | `permissions` rules in `settings.json` | Enforced by the CLI, not by the model |
| Live external data or actions | An MCP server | Uses an authorized integration instead of stale copied text |
| A shareable bundle of the above | A plugin | Installs, enables and disables as one unit |

**Instructions guide behavior. Permission rules enforce it.** A rule or skill that says "do not edit files" is guidance. A `deny` rule in `settings.json` blocks the action in every mode. A hook can deny a tool call, but the docs do not say what happens when the hook itself fails ⚠. Keep CI as the acceptance gate for code that must pass checks. [Permissions](https://antigravity.google/docs/permissions), [hooks](https://antigravity.google/docs/hooks)

## 3. Rules: `AGENTS.md`, `GEMINI.md` and `.agents/rules/`

### Where rules load from

agy reads rules from the **workspace folder** and from each parent folder up to the repository root. The workspace folder is the folder where you start `agy`, plus any folder you add with `--add-dir` or `/add-dir`. At each level it reads:

- `AGENTS.md` and `GEMINI.md`
- `.agents/AGENTS.md` and `.agents/GEMINI.md`
- `.agents/rules/*.md` (and the legacy `.agent/rules/*.md`)

Global rules come from `~/.gemini/AGENTS.md`, `~/.gemini/GEMINI.md`, `~/.gemini/config/AGENTS.md`, `~/.gemini/config/GEMINI.md` and `~/.gemini/config/rules/*.md`. Rules from enabled plugins also load. [Rules](https://antigravity.google/docs/rules), [customization discovery](https://antigravity.google/docs/customization-discovery)

Rules add up. They do not replace each other. When `AGENTS.md` and `GEMINI.md` sit in the same folder, both load *(probed)*. A repository can serve Codex through `AGENTS.md` and agy through both files, but agy then pays for both every turn.

agy does not read rules below the workspace folder. A `src/api/AGENTS.md` does not load when you start at the repository root, even after the agent reads a file in `src/api/` *(probed)*. The CLI's built-in customization reference says that rules load as the agent opens files, which the probe did not show ⚠. Start `agy` in the subfolder when its rules matter, or move the rule into `.agents/rules/` with a `glob` trigger.

### Frontmatter and triggers

`AGENTS.md` and `GEMINI.md` take no frontmatter and are always on. Every file in `rules/` needs YAML frontmatter with a valid `trigger`. agy drops a file without frontmatter and gives no warning *(probed)*. It drops a file with an unknown value such as `alwaysOn` in the same way.

| `trigger` | What loads | Use for |
|---|---|---|
| `always_on` | The full text, every turn | Short invariants. Prefer `AGENTS.md` when no frontmatter is needed |
| `model_decision` | The path and `description` each turn. The agent reads the body when the task matches *(probed)* | Long domain guides |
| `glob` | The full text when the agent works on a file that matches `globs` ⚠ | Conventions for one language or file type |
| `manual` | Only on an `@` mention. The CLI does not support rule mentions, so a `manual` rule never loads in the CLI | Checklists used in the App or IDE |

```markdown
---
trigger: glob
globs: "*.py, *_test.py"
description: Python style and test conventions for this repository.
---

- Use Polars, not pandas.
- Use single quotes for strings.
- Run `uv run pytest` from the package folder.
```

Quote a `globs` value that starts with `*`, or YAML reads it as an alias. The docs do not say whether a pattern matches the full path or only the file name ⚠. [Rules](https://antigravity.google/docs/rules)

### Includes and file references

The two `@` forms in a rule file behave differently:

- `@[label](path)` **inlines** the target file before the size check. A relative path starts at the folder of the rule file. agy removes frontmatter from the included file. The included text reached the model in a probe *(probed)*.
- `@path`, including Gemini CLI's `@./path` import form, **does not inline**. agy rewrites it to an absolute `@/…` path and gives the agent only that pointer *(probed)*.

A `GEMINI.md` written for Gemini CLI that imports a file with `@./file.md` therefore loses that content under agy. The agent sees the path and must decide to read it. Use `@[file](file.md)` to inline the file, at the cost of its full size every turn.

### Size limits and the rules budget ⚠

- **24,000 bytes per file.** agy truncates a larger rule file at a line boundary. It measures the size after includes.
- **20,000 tokens in total** for always-on and global rules. When the total is over budget, agy turns the largest rule files into one-line pointers of the form `- <path>: <description>`. The agent reads them on demand.

Both limits come from the docs and were not tested here. A rule that turns into a pointer still exists, but the model sees only one line of it. Keep the always-on set well under the budget, and check `/context` when rules seem to be ignored. [Rules](https://antigravity.google/docs/rules)

### Discipline

Put in rules what agy cannot infer: the commands that prove a change works, directory routing, local conventions and environment quirks. Put long procedures in a skill. For each line, ask "what repeated mistake does this prevent?"

agy rereads rules and skills before each turn, so an edit applies to your next message without a restart. [Customization discovery](https://antigravity.google/docs/customization-discovery)

## 4. Skills

A skill is a folder that holds a `SKILL.md` file. It follows the open [Agent Skills format](https://agentskills.io/specification), so a skill written for Claude Code or Codex usually loads without change.

```text
release-preview/
├── SKILL.md
├── references/
├── scripts/
└── assets/
```

### `SKILL.md`

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

Write both `name` and `description`. The public skills page calls `name` optional, with the folder name as its default. In practice agy did not list a skill without `name`, or a skill without frontmatter *(probed)*. When `name` differs from the folder name, the skill loads under `name` *(probed)*. The agent reads the description to choose a skill, so state the job, the situations that call for it and its inputs. [Agent skills](https://antigravity.google/docs/skills)

The docs list no other frontmatter field. Claude Code fields such as `disable-model-invocation`, `allowed-tools`, `context`, `model` or `hooks` have no documented meaning in agy ⚠. No documented switch stops the agent from choosing a skill by itself. A skill that must run only on request needs a description that says so. Put hard limits on its actions in permission rules.

### Where skills live

| Location | Scope |
|---|---|
| `.agents/skills/<name>/` in the workspace folder and each parent up to the repository root | Workspace skills, shared through version control |
| `~/.gemini/config/skills/<name>/` | Personal skills for the CLI and the Antigravity App |
| `~/.gemini/skills/<name>/` and `~/.gemini/antigravity-cli/skills/<name>/` | Personal skills for the CLI only. `~/.gemini/skills/` loads *(probed)* |
| `<plugin>/skills/<name>/` in an enabled plugin | Plugin skills, listed as `<plugin>:<name>` *(probed)* |
| Built-in skills | Supplied by the CLI, such as `agy-customizations` and `migrate-agent-settings` |

A symlinked skill folder loads *(probed)*, so a version-controlled skills repository can feed `~/.gemini/config/skills/`. agy does **not** read `~/.agents/skills/`, the folder Codex uses *(probed)*. It also does not read the Gemini CLI workspace folder `.gemini/skills/`. Move those skills to `.agents/skills/`. [Customization discovery](https://antigravity.google/docs/customization-discovery), [Gemini CLI migration](https://antigravity.google/docs/cli/gcli-migration)

The scan goes one level deep. `skills/data/backfill/SKILL.md` does not load unless a manifest names it.

### Manifests: `skills.json` ⚠

A `skills.json` file in `.agents/` or in `~/.gemini/config/` registers skill folders outside the standard locations. `rules.json`, `agents.json` and `plugins.json` work the same way for their types.

```json
{
  "entries": [
    { "path": "/Users/me/shared-agent-config/skills", "exclude": ["draft-skill"] }
  ],
  "inherits": [
    { "path": "/Users/me/shared-agent-config/.agents/skills.json", "include_only": ["release-preview"] }
  ]
}
```

- agy scans each `entries` folder one level deep. `include_only` can name a nested item such as `data/backfill`.
- Use absolute paths in a personal manifest. A `~/` path did not load *(probed)*. That matches the public page and contradicts the CLI's built-in reference.
- A workspace manifest loads only from inside the workspace or its repository root. This restriction came in release 1.5.2.
- The public page says `exclude` and `include_only` take names, not wildcards. The built-in reference shows a pattern with `.*`. Test before you rely on either.

[Customization discovery](https://antigravity.google/docs/customization-discovery)

### Name collisions ⚠

For two skills with the same name, the docs give this priority: a personal folder inside the repository, then the workspace, then `~/.gemini/config/`, then the built-ins. They also say that the CLI-only folders `~/.gemini/skills/` and `~/.gemini/antigravity-cli/skills/` win over all of these. In a probe, a workspace skill and a `~/.gemini/skills/` skill had the same name, and `/skills` showed the workspace copy. Use unique names so that the order never matters. Plugin skills carry a `<plugin>:` prefix, so they do not collide.

### Selection, invocation and arguments

Each turn, the agent sees the catalog of names and descriptions. It reads a full `SKILL.md` when a skill fits the task. You can also run a skill as `/<name>` (see §5). `/skills` lists every loaded skill. `/skills reload` refreshes the list and the slash commands after you add or remove a skill. A headless `agy -p "/skills"` prints the list without a model call *(probed)*.

The docs describe no argument substitution like Claude's `$ARGUMENTS`. Write the procedure so that it takes its inputs from the request, and name the inputs it needs. For live state, tell the agent to run a bundled script. The script's output then costs tokens and passes through permission rules like any other command.

### Progressive disclosure

Keep three levels apart: the catalog entry, the `SKILL.md` procedure, and the reference files or script output. A short index that points to one reference costs less than "read everything in `references/`". The docs also suggest that the agent run a bundled script with `--help` instead of reading its source. [Agent skills](https://antigravity.google/docs/skills)

| Symptom | Adjustment |
|---|---|
| The skill is missed on relevant requests | Add the phrases and inputs that actually occur |
| The skill is chosen for unrelated work | Narrow the description and state what it is not for |
| The skill loads but steps are skipped | Shorten the procedure, and name each checkpoint and output |
| The same logic is worked out again on each run | Bundle a script with a clear contract |
| Every run reads too much material | Replace blanket reads with conditional references |

## 5. Slash commands are skills

agy has no separate command format. **Every skill is a slash command.** A skill named `release-preview` becomes `/release-preview`. TOML commands do not exist, and files in `~/.gemini/commands/*.toml` do not load *(probed)*. To bring Gemini CLI commands over, convert each one to a skill. `agy plugin import gemini` converts extension commands, and the built-in `migrate-agent-settings` skill converts loose ones. [Agent skills](https://antigravity.google/docs/skills), [Gemini CLI migration](https://antigravity.google/docs/cli/gcli-migration)

Built-in commands control the client. Some of them are built-in skills, such as `/agy-customizations`. Type `/` for the full menu, or run `/help`.

### Useful CLI commands ⚠

| Command | Use |
|---|---|
| `/context` | Show token use by category, checkpoints, and loaded rule and skill files |
| `/usage` (`/quota`), `/credits` | Show model quota and AI credits |
| `/skills`, `/skills reload` | List skills, or reload them from disk |
| `/agents` | Switch the session agent, or watch and stop subagents |
| `/hooks`, `/mcp`, `/plugin` | Inspect hooks, MCP servers and plugins |
| `/permissions`, `/config` (`/settings`) | Edit permission rules and settings |
| `/model`, `/effort` | Choose the model and its reasoning effort |
| `/plan`, `/grill-me` | Research and draft a plan, or answer design questions, before any edit |
| `/clear` (`/new`) | Start a fresh conversation |
| `/fork` (`/branch`), `/rewind` (`/undo`), `/resume` | Branch, roll back or reopen a conversation |
| `/btw` | Ask a side question that stays out of the main history |
| `/goal`, `/schedule` | Work toward an objective without pauses, or wake the agent on a timer |
| `/learn` | Turn corrections from the session into a proposed rule or skill |

The changelog also names `/compact`, which the reference table leaves out ⚠. In headless mode, a prompt that starts with `/` runs as a slash command or skill unless you pass `--disable-slash-commands`. [CLI commands](https://antigravity.google/docs/cli/reference), [slash commands](https://antigravity.google/docs/slash-commands)

## 6. Custom agents and subagents

A custom agent is a Markdown file with YAML frontmatter. Its body is the system prompt. One definition can serve two roles:

- **Session agent** (`mainAgent: true`, the default). You start a session with it through `agy --agent <name>`, or choose it in `/agents`. A switch in the middle of a conversation forks the conversation.
- **Subagent** (`subagent: true`, the default). The main agent starts it with the `invoke_subagent` tool. The subagent runs in its own conversation and reports back.

[Custom subagents](https://antigravity.google/docs/subagents), [/agents](https://antigravity.google/docs/cli/commands/agents)

### Where agents live

| Location | Scope |
|---|---|
| `.agents/agents/<name>.md` or `.agents/agents/<name>/agent.md` | Workspace |
| `~/.gemini/config/agents/<name>.md` or `~/.gemini/config/agents/<name>/agent.md` | Personal |
| `<plugin>/agents/<name>.md` | An enabled plugin |
| `~/.gemini/agents/<name>.md` | Session agents only. `agy agents` lists them and `agy --agent` starts them, but `invoke_subagent` rejects them *(probed)*. The docs do not mention this folder ⚠ |

`agy agents` listed personal agents but not workspace agents *(probed)*. Inside a session, `/agents` lists workspace and plugin agents too. A plugin agent keeps its bare name, with no plugin prefix *(probed)*. `mainAgent: false` hides an agent from `/agents` *(probed)*. The main agent can still start that agent as a subagent *(probed)*. Put personal agents in `~/.gemini/config/agents/`, the only personal folder whose agents work in both roles.

### Dispatch depends on the folder

The main agent started workspace agents, a plugin agent and an agent in `~/.gemini/config/agents/` with `invoke_subagent`. It named each one in the `TypeName` argument *(probed)*. An identical agent in `~/.gemini/agents/` failed with `subagent "<name>" not found or not allowed to be invoked` *(probed)*. Test again after an update if a workflow depends on dispatch.

A subagent does not inherit the parent's conversation history. Write a complete brief: the objective, the paths, the inputs, the limits and the result you expect. The subagent sends its result with `send_message`. A headless `-p` run can end before every subagent reports *(probed)*, so ask for results in files when you script delegation. The App section of the subagents page adds three points, not tested in the CLI ⚠. Subagents inherit the parent's command allow rules, file scopes and sandbox setting. Their permission prompts come back to your session. Nesting stops at 10 levels. [Custom subagents](https://antigravity.google/docs/subagents)

### Frontmatter ⚠

```markdown
---
name: review-reader
description: Inspects a supplied diff for correctness and requirement gaps, and returns findings with file and line references.
mainAgent: false
tools: [read_file]
---

Read the supplied task brief and diff before you judge the change.
Report correctness and requirement gaps with evidence.
Do not expand the review without a stated reason.
Return a short verdict and findings the caller can act on.
```

| Field | Default in the docs | Purpose |
|---|---|---|
| `name`, `description` | Required | Identity, and the text the main agent reads to decide on delegation |
| `mainAgent` | `true` | Allow the agent as a session agent |
| `subagent` | `true` | Allow the main agent to start it with `invoke_subagent` |
| `tools` | Pages disagree ⚠ | Tool allowlist. `send_message` and `manage_task` are always present *(probed)* |
| `model` | `inherit` | Model tier: `inherit`, `flash_lite`, `flash` or `pro` |
| `commandExecutionPolicy` | `sandbox` | Shell auto-run policy: `off`, `auto`, `eager` or `sandbox` |
| `skills`, `plugins`, `mcpServers` | Empty | Extra skills, plugins or MCP servers for this agent |
| `inheritMcp`, `inheritCustomizations` | `true` | Inherit workspace MCP servers, or skills, rules and hooks |

[Build plugins](https://antigravity.google/docs/build-plugins)

### Tool names are a trap ⚠

The `tools` list does not use the tool names from the hooks page or from the docs' own agent examples. In probes on 1.5.7:

- `tools: [read_file]` gave the subagent `read_file`, `send_message` and `manage_task`.
- `tools: [grep_search]` gave it only `send_message` and `manage_task`. agy dropped `grep_search` without a warning. A plugin agent behaved the same way.

The docs' examples list `view_file`, `grep_search` and `find_by_name`. The subagents page also warns that an unknown name can make a subagent hang. The CLI's built-in migration skill uses `read_file`, `edit_file`, `write_file`, `run_command`, `manage_task` and `search_web`. A subagent kept `read_file`, `write_file`, `edit_file`, `run_command` and `manage_task` *(probed)*. `search_web` was not checked. The default for an omitted `tools` key is also unclear. One page says an empty list, another says all tools, and the migration skill says a small read-only set. Always write `tools`. Before you rely on a new agent, ask it to list its tools.

A role instruction is not a sandbox. A reviewer told "do not edit" still has every write tool that its allowlist grants. Leave write and shell tools out of `tools` for a read-only role, and put hard limits in permission rules.

### When delegation pays

- Reading many files to answer one narrow question.
- Independent investigations that can run at the same time.
- An independent review of a finished change.
- A long test run whose log belongs in a file.

Delegation costs more than it saves when the task is smaller than its brief, or when several agents edit the same files. Parallel agents shorten the wait but raise total usage. `/boost`, `/teamwork` and `/swarm` run larger multi-agent teams. They depend on the plan and multiply token use, so keep them for work that needs them. [Slash commands](https://antigravity.google/docs/slash-commands)

### Model routing

Start with the inherited model. Give an agent `model: flash` for mechanical search, or `model: pro` for hard review, only when a test shows the difference. `/model` and `--model` choose the session model. `/effort` and `--effort` set reasoning effort from `low` to `max` where the model supports it. `agy models` lists what your account can use. [Choose a model](https://antigravity.google/docs/models)

## 7. Hooks

Hooks run shell commands at fixed points in the agent loop. Define them in a `hooks.json` file:

- **Workspace:** `.agents/hooks.json`
- **Personal:** `~/.gemini/config/hooks.json`
- **Plugin:** `hooks.json` at the plugin root

Hooks in `~/.gemini/antigravity-cli/settings.json` do not load. `/hooks` lists the active hooks. [Hooks](https://antigravity.google/docs/hooks)

**A workspace hook ran without a trust check in a headless run.** In a probe, agy ran `.agents/hooks.json` in a folder that was not on its trusted list *(probed)*. Read `.agents/hooks.json` before you run `agy` in a repository that you did not write. Whether an interactive session asks first was not tested ⚠.

### File format

Each top-level key names a hook group. A group maps event names to handlers, and `"enabled": false` turns the group off. Groups from all sources merge. Handlers for one event run one after another.

| Event | When it runs | Matcher | Useful output |
|---|---|---|---|
| `SessionStart` | Once, before the first model call | None | `injectSteps` |
| `PreToolUse` | Before a tool call | Tool-name regex | `decision`, `reason`, `overwrite`, `permissionOverrides` |
| `PostToolUse` | After a tool call | Tool-name regex | `{}` |
| `PreInvocation` | Before each model call | None | `injectSteps`, `terminationBehavior: "terminate"` |
| `PostInvocation` | After each model call | None | `injectSteps`, `terminationBehavior` (`force_continue` or `terminate`) |
| `Stop` | When the loop is about to stop | None | `decision: "continue"` with a `reason` |

`PreToolUse` and `PostToolUse` handlers sit in a group with a `matcher` and a `hooks` list. The other events take a flat list of handlers. A handler supports `type` (only `"command"`), `command`, and `timeout` in seconds (default 30). Hooks are synchronous and block the loop while they run.

### Input and output

The command reads one JSON object on stdin and must print one JSON object on stdout. Keys are camelCase. Common fields include `conversationId`, `workspacePaths`, `cwd` (the agent's working folder), `hookEventName`, `lastUserInput`, `modelName` and `transcriptPath` *(probed)*. The hook process itself runs in the folder that holds `hooks.json`, not in `cwd` *(probed)*. Plugin hooks also get `PLUGIN_ROOT` and `PLUGIN_DATA` as environment variables.

`PreToolUse` input carries `toolCall.name`, `toolCall.args` and `toolCall.id`. The public hooks page lists these values for `decision` ⚠:

- `allow` passes the call on to the next hook or to the normal permission policy. It does not approve the call.
- `auto_approve` approves a call that would otherwise prompt. Your own rules still apply.
- `deny` blocks the call.
- `ask` prompts and honors "always allow". `force_ask` prompts every time.
- `deny_unless_prior_grant` blocks the call unless an earlier grant covers it.

The CLI's built-in reference lists only `allow`, `deny`, `ask` and `force_ask`. `overwrite` replaces top-level argument keys before the call runs.

**Tool names in matchers do not always match the docs ⚠.** The hooks page names the file-read tool `view_file`, with an `AbsolutePath` argument. On 1.5.7, a hook saw a file read as `read_file`, with a `Path` argument *(probed)*. `invoke_subagent`, `schedule` and `manage_task` arrived under their documented names. While you develop a hook, match `"*"` and log `toolCall.name` and `toolCall.args`. Narrow the matcher after you see the real names.

### Failure behavior ⚠

For most events, the docs do not say what a non-zero exit, a timeout or invalid JSON does. The changelog says that a failing `PostToolUse` hook is logged and does not fail the tool call. Test success, rejection, malformed input and a missing interpreter before you depend on a hook. For a hard block, use a `deny` permission rule, which applies in every mode.

### Pattern 1: block a command with a correction

`.agents/hooks.json`:

```json
{
  "uv-only": {
    "PreToolUse": [
      {
        "matcher": "run_command",
        "hooks": [
          { "type": "command", "command": "python3 -I hooks/uv_only.py", "timeout": 5 }
        ]
      }
    ]
  }
}
```

`.agents/hooks/uv_only.py`. The hook runs in `.agents/`, so the relative path resolves there:

```python
import json
import sys

payload = json.load(sys.stdin)
command = payload.get('toolCall', {}).get('args', {}).get('CommandLine', '')
if 'pip install' in command:
    decision = {'decision': 'deny', 'reason': 'This project uses uv. Use the documented uv command.'}
else:
    decision = {'decision': 'allow'}
print(json.dumps(decision))
```

In a probe, this exact hook denied `pip install --dry-run …`, and the agent received the reason *(probed)*. A substring check is a workflow nudge, not a security policy. It misses other spellings and indirect installs.

### Pattern 2: run a check before the agent stops

`.agents/hooks.json`:

```json
{
  "check-before-stop": {
    "Stop": [
      { "type": "command", "command": "python3 -I hooks/check_stop.py", "timeout": 60 }
    ]
  }
}
```

`.agents/hooks/check_stop.py`, for a repository whose `scripts/check.sh` exits non-zero on failure:

```python
import json
import subprocess
import sys

payload = json.load(sys.stdin)
if payload.get('continuationActive') or payload.get('continuation_active'):
    print(json.dumps({'decision': 'stop'}))
    sys.exit(0)
check = subprocess.run(['bash', 'scripts/check.sh'], cwd=payload['cwd'], capture_output=True, text=True)
if check.returncode == 0:
    print(json.dumps({'decision': 'stop'}))
else:
    output = (check.stdout + check.stderr)[-2000:]
    reason = 'Fix these check failures before you finish:\n' + output
    print(json.dumps({'decision': 'continue', 'reason': reason}))
```

Any `decision` other than `continue` lets the agent stop. The loop guard matters. Without it, a check that keeps failing keeps the agent running. The built-in reference spells the guard field `continuationActive`, and the changelog spells it `continuation_active`, so the script reads both ⚠. `cwd` is the agent's working folder, so start `agy` at the repository root or resolve the root in the script. Keep the check fast. A long suite belongs in an explicit step, and CI stays the acceptance gate.

### Patterns 3 and 4: session context and prompt screening

A `SessionStart` or `PreInvocation` hook can inject a short system message: `{"injectSteps": [{"systemMessage": {"systemMessage": "…"}}]}`. `systemMessage` takes a nested object, not a plain string. Inject a pointer to current notes or a one-line status, not a transcript, because injected text stays in the conversation.

A `PreInvocation` hook can stop a turn before the model runs. It returns `"terminationBehavior": "terminate"` together with an `errorMessage` step. In a probe, such a run exited with code 3 and used zero tokens *(probed)*. That makes a cheap screen for prompts that must never reach the model.

## 8. MCP servers

Define servers in an `mcp_config.json` file:

- **Personal:** `~/.gemini/config/mcp_config.json`
- **Workspace:** `.agents/mcp_config.json`
- **Plugin:** `mcp_config.json` at the plugin root

agy does not read the `mcpServers` block of Gemini CLI's `~/.gemini/settings.json`. [MCP](https://antigravity.google/docs/mcp)

```json
{
  "mcpServers": {
    "local-db": {
      "command": "uvx",
      "args": ["some-mcp-server", "--read-only"]
    },
    "docs": {
      "serverUrl": "https://example.com/mcp",
      "disabledTools": ["delete_page"]
    }
  }
}
```

A local server uses `command`, `args`, `env` and `cwd`. A remote server must use the Streamable HTTP transport. Set its endpoint with `serverUrl`, or with `url`, which also works. The older HTTP+SSE transport and Gemini CLI's `httpUrl` key are not supported. For a server that speaks only SSE, run a stdio bridge such as `mcp-remote` as a local server. The pages disagree on which key is primary, and the migration page still shows an SSE example ⚠. From the shell, `agy mcp add`, `list`, `enable`, `disable` and `remove` manage servers. [MCP](https://antigravity.google/docs/mcp)

**Tools load lazily by default.** agy writes each tool's schema to `~/.gemini/antigravity-cli/mcp/<server>/<tool>.json`. The prompt gets only the server path and the tool names. When the agent needs a tool, it reads the schema and calls the tool through `call_mcp_tool`. `"tools": {"<name>": {"eager": true}}` sends a tool's full schema every turn. Use it only for a tool that most sessions call.

- Use `enabledTools` or `disabledTools` to trim a large server.
- Set `"disabled": true` to keep a server's settings but stop the server.
- Check the MCP tools row in `/context`, and turn off unused servers in `/mcp`.
- A tool call times out after 180 seconds and a connection after 300 seconds by default. `timeoutSeconds` changes both.
- Prefer a familiar CLI when it does the job simply. Use MCP when it adds authorization, structured queries or hosted access.

## 9. Plugins

A plugin bundles skills, custom agents, rules, hooks and MCP servers into one unit that installs, enables and disables together. [Plugins](https://antigravity.google/docs/plugins), [build plugins](https://antigravity.google/docs/build-plugins)

```text
my-plugin/
├── plugin.json        # or .antigravity-plugin/plugin.json
├── skills/<name>/SKILL.md
├── agents/<name>.md
├── rules/AGENTS.md
├── hooks.json         # must sit at the plugin root
└── mcp_config.json
```

Plugins load from `.agents/plugins/<folder>/` in the workspace and from `~/.gemini/config/plugins/<folder>/`. Most plugins start enabled. `~/.gemini/config/config.json` records your enable or disable choice by folder name. Your choice wins over the plugin's own `disabled` field. A plugin whose MCP servers need variables installs in the disabled state until you fill them in.

| Command | Use |
|---|---|
| `agy plugin install <name>`, `<github-url>` or `<path>` | Install from the official marketplace, a repository or a folder |
| `agy plugin list [--json]` | List plugins and their components |
| `agy plugin enable`, `disable`, `uninstall` | Change the state, or remove the plugin |
| `agy plugin validate [--strict] <path>` | Check the manifest and every component before you share a plugin |
| `agy plugin import gemini` or `agy plugin import claude` | Convert Gemini CLI extensions or Claude Code plugins |

Inside a session, `/plugin` opens the same manager. agy adds prefixes where names could collide. Plugin skills appear as `<plugin>:<skill>` *(probed)*, and MCP tools as `<plugin>_<server>`. Plugin agents keep bare names *(probed)*.

Each enabled plugin adds catalog entries, rules and perhaps MCP tools to every session. Turn off plugins that have no current use. While a workflow is personal and still changing, write it as a local skill. Package it as a plugin when others need it.

## 10. Permissions, modes and the sandbox

### Settings files

The CLI reads `~/.gemini/antigravity-cli/settings.json`. `--settings` applies a JSON object of settings to one session without saving it. `/config` (alias `/settings`) edits the file. The docs describe no project-level settings file for the CLI ⚠. Add `"$schema": "https://antigravity.google/schemas/v1/settings.json"` to get validation in an editor. [CLI commands](https://antigravity.google/docs/cli/reference), [settings](https://antigravity.google/docs/settings)

### Agent Mode and Tool Permission

`agentMode` sets how a session runs. `--mode` sets it for one session, and Shift+Tab cycles through the modes:

| `agentMode` | File edits | Shell commands |
|---|---|---|
| `""` (Default) | Diff review before each edit | Follow `toolPermission` |
| `accept-edits` | Approved inside the workspace | Follow `toolPermission` |
| `auto` | Approved inside the workspace | Run in the sandbox. A reviewer agent decides each command that must leave it |
| `plan` | None until you approve a plan | Research only |

**Since 1.5.7, Auto is the default** wherever the sandbox is available, headless `-p` runs included. Save `"agentMode": ""` to keep the earlier Default behavior. Auto is not offered to business or enterprise accounts. Several docs pages still name Default as the default ⚠. [Changelog](https://antigravity.google/docs/changelog), [execution modes](https://antigravity.google/docs/cli/modes)

`toolPermission` sets the policy outside Auto mode:

- `request-review` (the default) asks before write, shell, web and MCP tools.
- `proceed-in-sandbox` runs sandboxed commands without asking.
- `strict` asks before every tool, reads included, and overrides Auto and `accept-edits`.
- `always-proceed` asks only when a rule says so. `--dangerously-skip-permissions` sets it for one session.

[Agent settings](https://antigravity.google/docs/agent-settings)

### Permission rules

```json
{
  "permissions": {
    "allow": ["command(git status)", "command(uv run pytest)", "read_url(docs.python.org)"],
    "ask": ["command(git push)"],
    "deny": ["read_file(.env)", "command(sudo)"]
  }
}
```

Each rule is an `action(target)` string with no space before the parenthesis. **Deny beats Ask, and Ask beats Allow.** A deny rule applies in every mode. The CLI ignores a rule that it cannot parse, so check new rules in `/permissions`.

| Action | Target |
|---|---|
| `read_file`, `write_file` | A path, recursive. `write_file` implies `read_file`. A `read_file` deny also denies `write_file` |
| `command` | A word-by-word command prefix, or `regex:<pattern>`. Applies inside and outside the sandbox |
| `read_url`, `execute_url` | A domain and its subdomains. `execute_url` covers the browser agent opening a page |
| `mcp` | `server/tool`, `server/*` or `*` |
| `unsandboxed` | Business and enterprise accounts only. Other accounts ignore it |

Inside the workspace, reads and writes are allowed by default. Most other actions default to Ask. A headless run cannot ask, so it denies an action that needs approval. The run continues, exits 0 and names the denied action on stderr. Grant what a scripted run needs with `allow` rules instead of `--dangerously-skip-permissions`. [Permissions](https://antigravity.google/docs/permissions), [headless mode](https://antigravity.google/docs/cli/headless)

### The terminal sandbox

`enableTerminalSandbox` (or `--sandbox`) runs agent shell commands inside an operating-system boundary. Auto mode turns it on. macOS uses `sandbox-exec` profiles, Linux uses kernel namespaces, and Windows 11 24H2 or later uses an AppContainer. Sandboxed commands can write the workspace, temporary folders and common build caches. They have no network access by default. Domains in `read_url` allow rules join the sandbox's network allowlist. Paths in `read_file` and `write_file` allow rules are mounted read-only or read-write. Where no sandbox is available, Sandbox Mode has no effect and the CLI does not offer Auto. [Terminal sandbox](https://antigravity.google/docs/sandbox)

`allowNonWorkspaceAccess` (default `false`) lets the agent read and write outside the workspace. The rules above still apply.

## 11. Running lean: the token-budget playbook

### Know what you measure

- `/context` shows what fills the context window now.
- `/usage` shows the plan quota. The models in one group share a weekly limit and a five-hour limit.
- `/credits` shows AI credits. `"useG1Credits": true` lets the CLI spend credits after the plan quota runs out. Leave it off unless you intend to pay for overage.
- A headless JSON run reports the tokens of that run. Save the JSON as an artifact instead of pasting a transcript into another conversation.

```bash
mkdir -p artifacts
agy --settings '{"agentMode": ""}' --output-format json --print-timeout 600s -p "Review the staged diff and list correctness gaps with file and line references." > artifacts/review.json
jq '.usage' artifacts/review.json
```

`--settings '{"agentMode": ""}'` runs this review in Default mode, so the headless run denies file edits and shell commands that need approval ⚠. Put the prompt straight after `-p`, because `-p` takes the next argument as its prompt. `--output-format stream-json` adds usage for each step and shows tool calls as they happen. A real run spends plan quota. [Headless mode](https://antigravity.google/docs/cli/headless), [plans](https://antigravity.google/docs/plans)

### Session hygiene

- Keep one conversation for each coherent outcome.
- Use `/btw` for a side question, so that its answer stays out of the main history.
- Use `/clear` between unrelated tasks. `/fork` copies the history, so it saves no tokens.
- agy compacts older turns into checkpoints automatically. Before a long handoff, write the decisions, the open work and the evidence paths into a short file.
- After two failed corrections, improve the reproduction and the context before you spend more reasoning.

### Model and effort

Choose the model for the task, then the effort. Compare a Flash model with a stronger model on your real workload. A cheap run that needs three corrections can cost more than one strong run. Diagnose in this order: missing context, then a clearer decomposition, then effort, then a different model. [Choose a model](https://antigravity.google/docs/models)

### Caching ⚠

Headless usage reports `cache_read_tokens`, so agy reuses cached prompt prefixes. Stable rules and tools within a session help that reuse. The docs give no cache rules or prices for the CLI. Do not apply Claude's cache rules or Codex credit rates to agy.

### Scale ceremony to task size

| Phase | Keep when… | Collapse when… |
|---|---|---|
| Objective and completion evidence | Every task | Keep it short even for tiny changes |
| Clarification and planning (`/plan`, `/grill-me`) | Scope or approach is unclear | The edit and its check are already clear |
| Written spec or handoff | Another session needs the decisions | A small local edit leaves no design decision |
| Failing test first | Library or pipeline behavior changes | Prose, formatting or simple configuration |
| Subagent | The work is separable, or an independent review adds value | The brief costs more than the task |
| Verification | Always | Scale the check, but never replace evidence with confidence |

### Guard expensive operations

For simulations, training runs, large data pulls or long suites:

1. Save the full output and its metadata at once: the command, inputs, revision, environment and time.
2. Point later reviews at that file instead of running the work again.
3. Write the expensive skill's description narrowly, because no switch stops automatic selection.
4. Add an `ask` or `deny` permission rule for the command if accidental reruns must stop.
5. Run the work again only when inputs changed, a check failed or evidence is missing.

### Goals and schedules

`/goal` keeps the agent working toward an objective without a pause after each turn. `/schedule` wakes the agent with an instruction after a delay or on a cron schedule. Test the procedure by hand first. State what counts as done and when to stop. Each scheduled run spends quota. [/goal](https://antigravity.google/docs/commands/goal), [/schedule](https://antigravity.google/docs/commands/schedule)

## 12. Translating a Claude Code or Gemini CLI setup

| Claude Code | agy |
|---|---|
| `CLAUDE.md` | `AGENTS.md` or `GEMINI.md`. Inline a shared file with `@[CLAUDE.md](CLAUDE.md)` |
| `@path` imports | `@[label](path)` inlines. A bare `@path` is only a pointer |
| `.claude/rules/*.md` with `paths` | `.agents/rules/*.md` with `trigger: glob` and `globs` |
| `~/.claude/skills/`, `.claude/skills/` | `~/.gemini/config/skills/`, `.agents/skills/` |
| `/skill-name` | `/skill-name` |
| `disable-model-invocation: true` | No documented equivalent ⚠ |
| `.claude/commands/*.md` | A skill |
| `~/.claude/agents/*.md` | `~/.gemini/config/agents/*.md`, with agy tool names in `tools` |
| `context: fork` in a skill | Delegation to a custom subagent |
| `Bash(git status:*)` permission strings | `command(git status)` in `permissions` |
| Hooks in `settings.json` | `hooks.json`, with different events and payloads |
| `/context` | `/context` |
| Claude Code plugins | `agy plugin import claude` |

| Gemini CLI | agy |
|---|---|
| `.gemini/skills/` | `.agents/skills/` |
| `~/.gemini/skills/` | Still read by the CLI *(probed)*. Use `~/.gemini/config/skills/` to share with the App |
| `~/.gemini/commands/*.toml` | Skills. TOML commands do not load *(probed)* |
| Extensions in `~/.gemini/extensions/` | Plugins, through `agy plugin import gemini` |
| `mcpServers` in `settings.json` | `mcp_config.json`, with `serverUrl` instead of `httpUrl` |
| `@./file.md` in `GEMINI.md` | `@[file](file.md)` to inline. `@./file.md` becomes a pointer *(probed)* |
| Subagents in `~/.gemini/agents/` | Move them to `~/.gemini/config/agents/`. Agents left in `~/.gemini/agents/` run only as session agents *(probed)*. Rewrite `tools` with agy names, because agy drops Gemini CLI names such as `grep_search` *(probed)* |

For a bulk move, the built-in `migrate-agent-settings` skill collects MCP servers, skills, commands, agents and instruction files from Claude Code, Codex, Cursor and Gemini CLI. It writes them into one plugin under `~/.gemini/config/plugins/`. It asks before it writes and leaves the sources unchanged. Hooks and permission rules from Claude Code's `settings.json` do not convert. Review the output, especially each agent's `tools` list. [Plugins](https://antigravity.google/docs/plugins)

## Repository application

agy inlines this repository's canonical maintainer guide, `CLAUDE.md`, only when the root `GEMINI.md` includes it with the `@[…](…)` form. The Gemini CLI form `@./CLAUDE.md` gives agy a pointer only *(probed)*. `CLAUDE.md` is about 18 KB, under the 24,000-byte cap. Inlined, it costs roughly 4,500 tokens of the 20,000-token rules budget on every turn. agy also loads the root `AGENTS.md`, which tells the agent to read `CLAUDE.md`.

## Further reading

- [Customization discovery](https://antigravity.google/docs/customization-discovery), [rules](https://antigravity.google/docs/rules), [agent skills](https://antigravity.google/docs/skills), [custom subagents](https://antigravity.google/docs/subagents), [/agents](https://antigravity.google/docs/cli/commands/agents).
- [Hooks](https://antigravity.google/docs/hooks), [MCP](https://antigravity.google/docs/mcp), [plugins](https://antigravity.google/docs/plugins), [build plugins](https://antigravity.google/docs/build-plugins).
- [Permissions](https://antigravity.google/docs/permissions), [terminal sandbox](https://antigravity.google/docs/sandbox), [agent settings](https://antigravity.google/docs/agent-settings), [settings](https://antigravity.google/docs/settings), [execution modes](https://antigravity.google/docs/cli/modes).
- [CLI commands](https://antigravity.google/docs/cli/reference), [headless mode](https://antigravity.google/docs/cli/headless), [/context](https://antigravity.google/docs/cli/commands/context), [/usage](https://antigravity.google/docs/cli/commands/usage), [CLI credits](https://antigravity.google/docs/cli/credits), [models](https://antigravity.google/docs/models), [plans](https://antigravity.google/docs/plans).
- [Gemini CLI migration](https://antigravity.google/docs/cli/gcli-migration), [changelog](https://antigravity.google/docs/changelog).
