# Writing Portable Agent Skills: Best Practices for Claude Code, Codex, Gemini CLI, Cursor, Copilot and Other Agents (as of September 2026)

**Status: RETIRED (2026-10-03)** — the survey behind `specs/agent-skills-portability.md`; moved to `specs/completed/` in `79ad04f`, ahead of that spec.

Use the agentskills.io core as the contract: `name` and `description` are required, and `license`, `compatibility`, `metadata` and `allowed-tools` are optional.\[1\] Keep one canonical skills tree, ideally at `.agents/skills/`, and link it into each tool. Add each vendor's extensions as extras that the other tools can safely ignore, never as something the skill depends on. The biggest trap in 2026 is still discovery paths and invocation flags rather than the file format. Claude Code still doesn't scan `.agents/skills`.\[2\] Codex ignores Claude's `disable-model-invocation` and reads its own `agents/openai.yaml` sidecar instead.\[3\]\[4\]

## TL;DR

- **Write to the spec, extend on the side.** Keep the frontmatter to the spec's fields. Keep the body imperative and under about 500 lines or 5,000 tokens, with detail moved into `references/`. Bundle scripts that run without any particular tool's sandbox; for your stack that means Python with PEP 723 inline dependencies run via `uv run`. Treat `allowed-tools`, hooks, `context: fork` and invocation flags as optional extras that degrade gracefully.
- **One canonical repo, many install targets.** Codex, Gemini CLI, Cursor, Copilot, OpenCode, Windsurf, Amp and Cline all read `.agents/skills`. Claude Code needs `.claude/skills`, which can be a symlink, or a plugin marketplace. Distribute through a Claude Code `.claude-plugin/marketplace.json`, the Vercel `npx skills` CLI, `gh skill`, and a Codex plugin if you want the Codex/ChatGPT directory.
- **Test triggering like a classifier.** Use about 20 labeled queries, half of them near-miss negatives, run each 3 times, split 60/40 into train and validation, and choose the description with the best validation score. Anthropic's `skill-creator` automates this loop inside Claude Code. For Codex and Gemini, write a small harness. Re-run it whenever a model changes, and audit every third-party skill as if it were untrusted code.

## Key Findings

1. **The spec is tiny and stable; the tools around it diverge.** The agentskills.io spec defines six frontmatter fields and three optional directories (`scripts/`, `references/`, `assets/`), and recommends metadata of about 100 tokens and a body under 5,000 tokens.\[1\] Simon Willison (December 19, 2025) called it "a deliciously tiny specification" that is "quite heavily under-specified". Everything interesting, such as invocation control, tool permissions and discovery paths, is defined by each client.
2. **`.agents/skills` has become the de facto cross-agent location.** Claude Code is the notable exception. Codex, Gemini CLI, Cursor, GitHub Copilot, OpenCode and Windsurf all document `.agents/skills`.\[5\]\[6\]\[7\]\[8\] Claude Code's docs list only `.claude/skills` locations. Open issues such as anthropics/claude-code #31005 and #56193 ask for `.agents/skills` support.\[9\]\[10\] One practitioner found that Claude Code 2.1.280 knows those paths only through `/import`, which copies the skills, and so used a `.claude/skills → ../.agents/skills` symlink instead.\[2\]
3. **Invocation control doesn't transfer.** Claude Code, Cursor and Copilot honour `disable-model-invocation: true`.\[11\]\[12\] Codex ignores it and uses `agents/openai.yaml` with `policy.allow_implicit_invocation: false`.\[4\] Well-maintained repos such as mattpocock/skills now ship both and keep them in sync.\[13\]
4. **Strict validators reject Claude Code extensions.** claude.ai uploads, the Skills API and the reference validator accept only the six spec fields.\[14\]\[15\] Codex's validator has been reported to be stricter still.\[3\] A Claude-Code-flavoured SKILL.md with `argument-hint` or `disable-model-invocation` will pass locally and then fail those checks.\[15\]
5. **Descriptions are silently truncated, and the budgets differ.** Claude Code truncates `description` plus `when_to_use` at 1,536 characters per skill; issue #47627 records that Anthropic "raised the listing cap from 250 to 1,536 characters and added a startup warning when descriptions are truncated". OpenAI's Codex docs say the initial skills list "uses at most 2% of the model's context window, or 8,000 characters when the context window is unknown", and that "Codex shortens skill descriptions first" when many skills are installed. Put the trigger words at the start.
6. **Supply-chain risk is real.** Snyk's "ToxicSkills" audit scanned 3,984 skills from ClawHub and skills.sh as of February 5, 2026. It found that 13.4% of all skills (534) had at least one critical-level security issue, 36.82% (1,467) had at least one security flaw, and 76 contained malicious payloads. OWASP has since published the Agentic Skills Top 10 (AST10), which it calls "the first comprehensive security framework for AI agent skills"; one secondary source dates it to April 27, 2026.

## Details

### 1. The Agent Skills standard (agentskills.io; spec repo github.com/agentskills/agentskills)

**Layout.**
```
skill-name/
├── SKILL.md      # required: YAML frontmatter + Markdown body
├── scripts/      # optional: executable code
├── references/   # optional: docs loaded on demand
└── assets/       # optional: templates, schemas, data
```

**Frontmatter fields (spec, read September 2026):**

| Field | Req. | Constraint |
|---|---|---|
| `name` | Yes | 1–64 characters; lowercase `a-z`, `0-9` and `-`; no leading, trailing or double hyphens; **must match the parent directory name**\[1\] |
| `description` | Yes | 1–1024 characters; says what the skill does *and* when to use it\[1\]\[16\] |
| `license` | No | A licence name, or a reference to a bundled licence file |
| `compatibility` | No | 1–500 characters; environment requirements. "Most skills do not need" it\[1\] |
| `metadata` | No | A map of string keys to string values; use keys unique enough not to collide\[1\] |
| `allowed-tools` | No | A space-separated list of pre-approved tools. **Experimental**; support varies\[1\] |

**Progressive disclosure.** Loading happens in three stages:
1. `name` and `description` load at startup for every skill, about 100 tokens each.\[1\]
2. The full body loads when the skill activates.\[1\]
3. Files in `scripts/`, `references/` and `assets/` load only when needed.\[1\]\[17\]\[18\]

The spec says to keep SKILL.md under 500 lines and to use relative paths from the skill root. Keep references one level deep, and avoid chains of references that point to further references.\[1\]\[16\]

**Anthropic's extra rules** (platform.claude.com best practices). `name` and `description` can't contain XML tags. `name` can't contain "anthropic" or "claude".\[19\] Descriptions should be in the third person, because they are injected into the system prompt. Gerund names such as `processing-pdfs` are preferred. Reference files longer than about 100 lines should start with a table of contents, because Claude may preview a file with a partial read.\[16\]

**Validation.** `skills-ref validate ./my-skill` checks the frontmatter and naming rules.\[1\] Other commands are `read-properties` for JSON output and `to-prompt`, which produces the suggested `<available_skills>` XML block. The official README calls the library "for demonstration purposes only" and says it is not for production use. Install it from the repo with `pip install -e .` or `uv sync`.\[20\] A PyPI package, `skills-ref 0.1.1` (January 10, 2026, alpha), exposes the command as `agentskills` instead, and its maintainership is unclear.\[21\] Third-party reports say the validator hard-fails any top-level key outside the six spec fields.\[14\]\[22\] I couldn't confirm that from the source.

**Revisions.** The spec was published as an open standard\[23\] in December 2025 and has changed little since. `compatibility` was added to the optional fields, which is why older validators, such as the one behind openai/skills issue #187, rejected it.\[24\] `allowed-tools` is still marked experimental.\[1\] The GitHub org says the standard is "maintained by Anthropic and open to contributions".\[21\]\[25\]

### 2. How each tool discovers and loads skills (September 2026)

| Tool | Project paths | User paths | Invocation / notes |
|---|---|---|---|
| **Claude Code** | `.claude/skills/<n>/` (walks up to repo root; nested dirs load lazily)\[26\] | `~/.claude/skills/` | Invoke with `/name` or automatically. Plugin skills are namespaced `/plugin:skill`. Symlinked skill folders are supported.\[26\] **Doesn't read `.agents/skills`.** Personal skills don't load in Cowork or cloud sessions.\[26\] |
| **claude.ai / Claude API** | Upload a zip (claude.ai) or use `/v1/skills` (API) | — | Only the six spec fields are allowed. The API sandbox has **no network access and no runtime package install**. claude.ai can install from PyPI and npm.\[16\] |
| **OpenAI Codex** (CLI, IDE, app) | `.agents/skills` in every dir from CWD to repo root\[27\] | `$HOME/.agents/skills`, `/etc/codex/skills`, plus bundled system skills\[27\] | Invoke with `$skill-name` or `/skills`. The optional `agents/openai.yaml` holds UI settings, `policy.allow_implicit_invocation` and MCP `dependencies`. Symlinks are followed. Duplicate names are not merged.\[27\] |
| **Gemini CLI** | `.gemini/skills/` or the `.agents/skills/` alias\[28\] | `~/.gemini/skills/` or `~/.agents/skills/`\[28\] | The model calls `activate_skill`, and the **user sees a consent prompt**. The skill's directory is then added to the allowed paths.\[28\] Workspace skills load only in **trusted** folders.\[29\] |
| **Cursor** | `.cursor/skills/` or `.agents/skills/` (anywhere in the repo; nested dirs are auto-scoped)\[5\]\[30\] | `~/.cursor/skills/`\[12\] | Invoke with `/skill-name`. Honours `disable-model-invocation` and `paths`. Can sync to Cloud Agents and publish to a team marketplace.\[11\]\[12\]\[31\] |
| **GitHub Copilot** (CLI, cloud agent, VS Code, Visual Studio, JetBrains) | `.github/skills`, `.claude/skills`, `.agents/skills`\[6\] | `~/.copilot/skills`, `~/.agents/skills`\[6\]\[32\] | Use `/skills reload` and `/skills info`.\[6\] `gh skill install` writes provenance (repo, ref, tree SHA) into the frontmatter.\[33\] VS Code **won't load a skill whose name doesn't match its folder**.\[34\] |
| **OpenCode** | `.opencode/skills`, `.claude/skills`, `.agents/skills` (walks to git worktree)\[8\] | `~/.config/opencode/skills`, `~/.claude/skills`, `~/.agents/skills`\[35\] | Loaded through a native `skill` tool. Recognises only a fixed set of fields and ignores unknown ones.\[35\] v2 adds config-listed and HTTP-catalog sources.\[36\] |
| **Windsurf (Cascade)** | `.windsurf/skills/`, plus `.agents/skills/`; `.claude/skills/` if Claude config reading is on\[7\] | `~/.agents/skills/` (and a Codeium path) | Community reports say automatic invocation is unreliable and recommend explicit `@skill-name`.\[37\] Treat that as anecdotal. |
| **Amp, Cline, Warp, Zed, Replit and others** | `.agents/skills/` | `~/.config/agents/skills/` (Amp) or `~/.agents/skills/` | Paths come from the Vercel `skills` CLI agent table, not each vendor's own docs.\[38\]\[39\] |
| **Goose, Roo Code, Kilo Code** | Supported as install targets by `npx skills` since its January 2026 launch\[40\] | — | I couldn't verify their paths from vendor docs. Check with `npx skills add … --list` and each tool's docs. |

**Known divergences to design around:**
- **Name/folder mismatch.** Claude Code falls back to the directory name.\[26\] VS Code/Copilot and the spec validator refuse the skill.\[1\]\[34\] *Always make them match.*
- **Invocation flags.** Claude Code's `disable-model-invocation: true` also removes the description from context, stops preloading into subagents, and (from v2.1.196) blocks the skill in scheduled tasks. Setting `user-invocable: false` hides it from the `/` menu, but Claude can still invoke it.\[26\] Codex needs the `agents/openai.yaml` policy described above. OpenClaw now reads both after a July–September 2026 fix.\[41\] Some Claude Code builds have had bugs where manual-only skills couldn't be invoked by slash command (issues #26251 and mattpocock/skills #1055).\[42\]\[43\] Test both paths after every upgrade.
- **Claude-only body features.** These are `` !`cmd` `` dynamic context injection, `$ARGUMENTS`/`$0`/`$name` substitution, `${CLAUDE_PROJECT_DIR}`, `context: fork`, `hooks`, `model` and `effort`. Other tools pass them through as literal text. Even Claude Code skips `!` commands for skills synced from claude.ai when running outside cloud or Cowork sessions.\[26\]
- **Consent and sandboxing.** Gemini asks before activating a skill.\[28\] Codex runs sandboxed by default.\[44\] The Claude API has no network.\[16\] A script that runs `pip install` or calls an HTTP API will behave differently in each.
- **Context budgets.** OpenAI's Codex docs cap the skills list at "2% of the model's context window, or 8,000 characters when the context window is unknown"; openai/codex issue #19679 shows this hardcoded as `DEFAULT_SKILL_METADATA_CHAR_BUDGET = 8_000`. Claude Code truncates each skill at 1,536 characters.\[26\] Claude Code's docs, as quoted in issue #47627, say the overall listing budget "scales dynamically at 1% of the context window, with a fallback of 8,000 characters"; the issue says `SLASH_COMMAND_TOOL_CHAR_BUDGET` overrides it (a secondary guide cites `skillListingBudgetFraction` instead). Check `/doctor`.

### 3. Writing portable skills

**Descriptions (the trigger).**
- Lead with the capability and the key trigger terms. Hosts truncate from the end, and OpenAI says to "front-load the key use case and trigger words."\[27\]
- Say both *what* the skill does and *when* to use it.\[1\] Name the user intents and file types, including cases where the user doesn't name the domain.\[16\]\[18\]
- Mind the conflict between guides. agentskills.io says to use imperative phrasing ("Use this skill when…") and to "err on the side of being pushy."\[18\] Anthropic says to write in the third person ("Processes Excel files…").\[16\] Both work in practice with the form "Does X. Use when Y, even if Z." It is third person for the capability and imperative-ish for the trigger. **Avoid first or second person** ("I can help you…").
- Add a one-clause boundary for near misses, e.g. "Not for pandas code or SQL ETL." Negative boundaries are how the spec guide fixes false triggers.\[18\]
- For manual-only skills, some authors add "Manual-only: do not invoke unless the user asks for /x." That is a model-agnostic fallback for tools that have no invocation flag.\[45\] Pair it with the real flags.

**Body.**
- Be concise and imperative. Anthropic's best-practices guide says "Default assumption: Claude is already very smart" and "Only add context Claude doesn't already have."
- Match the degrees of freedom to how fragile the task is. Use prose for judgement calls, parameterised templates where a preferred pattern exists, and exact scripts ("run exactly this; do not add flags") for fragile steps.\[16\]
- Use checklists and validate→fix→repeat loops for multi-step work.\[16\]
- Give one default tool plus an escape hatch rather than a menu of options.\[16\]
- Keep terminology consistent. Avoid time-sensitive statements; put history in an "old patterns" section.\[16\]
- Once loaded, a Claude Code skill stays in context across turns, so every line is a recurring cost.\[26\]
- **Stay model-agnostic.** Don't say "Claude" or "use the Skill tool/Read tool". Say "read `references/x.md`" and "run `uv run scripts/check.py`". Use plain Markdown with no XML-ish tags. Test with every model you target; Anthropic explicitly recommends testing with small and large models.\[16\]

**Scripts.**
- Make them self-contained and deterministic, with helpful errors\[1\] ("solve, don't defer") and documented constants.\[16\]
- Use forward-slash relative paths, and tell the agent whether to *execute* or *read* each script.\[16\]
- For your Python stack, use a PEP 723 inline-metadata header with `uv run`, so dependencies such as Polars travel with the script, and a `#!/usr/bin/env -S uv run --script` shebang.
- Declare `uv` in `compatibility`.
- Degrade gracefully when there's no network (Claude API, Codex sandbox). Keep heavy imports like JAX out of scripts that only need to validate data.
- Use `npx` only for Node tooling. Never assume `pip install` works at run time.

**Framework-specific features.** Put Claude-only fields (`disable-model-invocation`, `allowed-tools`, `hooks`, `context: fork`, `argument-hint`) in the frontmatter only when you accept two things. First, strict validators and claude.ai uploads will reject them.\[15\] Second, other agents will ignore them. The skill must still be correct when they are ignored. Three examples:
- If `allowed-tools` is ignored, the agent simply asks for permission.
- If hooks don't run, put the "gate" in the body as an explicit step, such as "run `scripts/validate.py`; stop if it fails".
- If `context: fork` is ignored, the skill runs inline.

**Skills vs AGENTS.md/CLAUDE.md vs MCP.**
- **AGENTS.md / CLAUDE.md / GEMINI.md / Copilot instructions** hold short facts that are always relevant: test commands, "Polars not pandas", style. They are always in context but are guidance, not enforcement.\[46\] Note that Claude Code still centres on CLAUDE.md; import a shared file with `@path`.\[47\]
- **Skills** hold procedures and bulky reference material needed only sometimes, such as a NumPyro model-building workflow or BLS data context. Anthropic's rule of thumb is to create a skill "when a section of CLAUDE.md has grown into a procedure rather than a fact."\[26\]
- **MCP servers** provide typed tools, data access and auth. A skill describes the *procedure around* MCP tools and never holds credentials.\[48\] Codex can declare MCP dependencies in `agents/openai.yaml`.\[27\]

**Versioning and licensing.**
- The spec has no `version` field. Use `metadata.version` (a string)\[1\] and a repo-level CHANGELOG, and tag releases so installers can pin versions. Claude marketplaces accept `#ref`,\[49\] and `gh skill` pins by ref and SHA.\[33\]
- Put an SPDX name in `license` and ship a LICENSE file. If you vendor third-party skills, keep their licences and NOTICE files; your repo already does this for superpowers.

**Security.**
- Treat skills as code. Anthropic advises installing only from trusted sources and auditing scripts, dependencies and any instruction that points to external network sources.\[50\]
- The Snyk ToxicSkills figures above and academic work (SkillJect, SkillSieve and others) show that prompt injection can hide in helper scripts and in "inducement" rewrites of the documentation.\[51\]\[52\]
- Don't embed secrets; read them from the environment.\[48\]
- Require explicit user confirmation for side effects,\[48\] and make destructive or deploy skills manual-only in *both* Claude Code and Codex.
- Avoid angle brackets in frontmatter. Claude Code now escapes them in synced skills.\[26\]\[53\]
- Consider running Cisco's `skill-scanner` in CI.\[51\]

### 4. Testing, evaluation and maintenance

- **Trigger evals (agentskills.io guide).** Build about 20 realistic queries: 8–10 should trigger and 8–10 are near-miss negatives. Include file paths, casual phrasing and typos. Run each 3 times and count a pass at a trigger rate of 0.5 or more. Split 60/40 into train and validation, iterate about 5 times, and pick the best *validation* score rather than the latest version.\[18\] The guide's reference harness detects `Skill` tool calls in `claude -p --output-format json`. Replace the detector with each client's logs, such as Codex or Gemini tool-call output.\[18\]
- **Output-quality evals.** Anthropic's approach is to write evaluations *before* writing extensive docs:\[16\]
  1. Measure a no-skill baseline on 3 scenarios.\[16\]
  2. Write the minimal instructions needed.\[16\]
  3. Iterate using the "Claude A authors / Claude B tests" loop.\[16\]
- **Tooling.**
  - Anthropic's `skill-creator` runs evals, benchmarks with variance analysis, and blind A/B comparisons between versions. It also optimises descriptions,\[18\] but that feature needs `claude -p`, so it runs only in Claude Code.\[54\]\[55\]\[56\]
  - Codex ships `$skill-creator`,\[27\] and `@plugin-creator` validates plugins.\[57\]
  - Gemini CLI has a built-in `skill-creator` that validates and packages skills.\[58\]
  - `gh skill publish --dry-run` checks your repo against the spec and GitHub settings, and `--fix` repairs metadata.\[33\]
  - `claude plugin validate` checks marketplaces.\[59\]
  - Community tools include mgechev/skills-best-practices and skillc, whose proposed rule checks that Claude and Codex invocation flags agree.\[60\]\[61\]
- **Maintenance.** Re-run the trigger and quality suites on every model or agent upgrade.\[62\] Use `/doctor` in Claude Code to check for listing-budget overflow.\[63\] Keep a CI job that runs `skills-ref validate` on the spec core and checks that `name` matches the folder.

### 5. Distribution and installation

- **Claude Code plugin marketplace.** Add `.claude-plugin/marketplace.json`, with `name`, `owner` and `plugins[]`, each plugin having a `name` and a relative `source`,\[59\] plus `<plugin>/.claude-plugin/plugin.json` and `<plugin>/skills/<skill>/SKILL.md`. Users run `/plugin marketplace add owner/repo` and then `/plugin install <plugin>@<marketplace-name>`.\[64\] Skills are namespaced as `/plugin:skill`.\[65\] Keep the entry name and the manifest name identical.\[59\]
- **Vercel `skills` CLI.** Users run `npx skills add owner/repo [--skill x] [-a claude-code -a codex] [-g]`. It supports 75+ agents.\[38\] By default it keeps one canonical copy and symlinks it into each agent's directory; `--copy` makes copies instead. Other commands are `list`, `find`, `update`, `remove` and `init`.\[38\]\[66\] Installs appear on skills.sh through install telemetry.\[67\] There is also an experimental `skills-lock.json` restore.\[66\]
- **GitHub CLI.** `gh skill install owner/repo <skill>` supports pinning and provenance, and `gh skill publish` validates before publishing.\[32\]\[33\]
- **Codex.** OpenAI now recommends **plugins** for distribution; the old openai/skills catalog is deprecated in favour of openai/plugins.\[27\]\[68\] Create `.codex-plugin/plugin.json` with a `skills` entry. A repo marketplace goes at `.agents/plugins/marketplace.json`\[69\]\[70\]\[71\] and a personal one at `~/.agents/plugins/marketplace.json`. Install with `codex plugin add name@marketplace`.\[57\] A secondary source reported in May 2026 that self-serve publishing to the official directory was "coming soon".\[72\]
- **Monorepo pattern (recommended for you).**
```
agent-skills/
├── .agents/skills/<skill>/        # canonical source (SKILL.md, scripts/, references/, agents/openai.yaml)
├── .claude/skills -> ../.agents/skills   # symlink for Claude Code in this repo
├── .claude-plugin/marketplace.json       # Claude Code distribution
├── plugins/<bundle>/.claude-plugin/plugin.json + skills/ (symlinks or build step)
├── .codex-plugin/plugin.json             # optional Codex plugin
├── AGENTS.md  (+ CLAUDE.md that @-imports it)
├── CHANGELOG.md, LICENSE, NOTICE, README.md (install matrix per agent)
└── tests/trigger_evals/<skill>.json
```
Prefer symlinks or a small installer over copies, because copies drift.\[2\]\[47\] Symlinks can break on Windows and in some CI setups,\[10\] so keep a `--copy` fallback; your `install.py` already does this.\[73\] Git submodules work for pulling in third-party skills but make updates clumsy. Vendoring at a pinned SHA with a NOTICE file is simpler.\[74\] For discoverability, put a per-agent install table in the README, add the `agent-skills` GitHub topic, and make `npx skills add lowmason/agent-skills --list` work cleanly.

### 6. Template and examples

**Minimal portable skill**
```
polars-data-validation/
├── SKILL.md
├── agents/openai.yaml        # optional, Codex-only
├── scripts/validate.py
└── references/checks.md
```
```markdown
---
name: polars-data-validation
description: Validates tabular datasets with Polars — schema, nulls, ranges, duplicate keys — and writes a pass/fail report. Use when the user wants to check, audit, or sanity-test a CSV/Parquet file or DataFrame before modeling, even if they don't say "validate". Not for pandas code or database ETL.
license: MIT
compatibility: Requires Python 3.12+ and uv; no network needed.
metadata:
  author: lowmason
  version: "1.2.0"
---

# Polars data validation

1. Run `uv run scripts/validate.py <path> --schema <schema.json>`; it prints JSON.
2. If `status` is `fail`, report each failed check with column and row count; do not modify data.
3. For check definitions or adding a custom rule, read `references/checks.md`.
4. Re-run step 1 after any fix; stop only when it passes or the user decides.
```
```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["polars>=1.0"]
# ///
"""Validate a CSV/Parquet file; print a JSON report; exit 1 on failure."""
import json, sys
from pathlib import Path
import polars as pl

def main(path: str) -> int:
    p = Path(path)
    if not p.exists():
        print(json.dumps({"status": "error", "message": f"{p} not found"}))
        return 2
    df = pl.read_parquet(p) if p.suffix == ".parquet" else pl.read_csv(p)
    nulls = {c: n for c, n in df.null_count().row(0, named=True).items() if n}
    report = {"status": "fail" if nulls else "pass", "rows": df.height, "nulls": nulls}
    print(json.dumps(report))
    return 1 if nulls else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
```
Optional `agents/openai.yaml` (only for manual-only skills; mirror `disable-model-invocation`):
```yaml
policy:
  allow_implicit_invocation: false
```

**Good vs poor descriptions**
- ❌ `description: Helps with Bayesian models.` It gives no trigger terms and no boundary.
- ✅ `description: Builds and diagnoses NumPyro models on JAX — priors, reparameterization, NUTS settings, divergence and R-hat checks. Use when the user is writing or debugging a NumPyro/JAX probabilistic model or sampler output, even if they only mention "divergences" or "my chains won't mix". Not for PyMC or Stan.`
- ❌ `description: I can help you deploy the docs site.` It is written in first person, has no when-clause, and is risky to auto-trigger.
- ✅ `description: Deploys the docs site to GitHub Pages. Manual-only: run only when the user explicitly invokes /deploy-docs.` Pair it with `disable-model-invocation: true` and the Codex yaml.

**Good vs poor body**
- ❌ "Polars is a fast DataFrame library written in Rust. There are many ways to read files… You might consider using lazy frames…" This explains what the model already knows and offers options instead of a default.
- ✅ "Use `pl.scan_parquet(...).collect()` for files larger than 1 GB; otherwise `pl.read_parquet`. Never convert to pandas. Run `scripts/validate.py` before modeling; stop on failure."

## Recommendations (in priority order)

1. **Move your canonical tree to `.agents/skills/`**, or keep `skills/` and have `install.py` link it into `.agents/skills`, `~/.agents/skills`, `~/.claude/skills` and `~/.gemini/skills`. Symlink `.claude/skills` in the repo itself.
2. **Build a two-profile lint in CI.** "Strict" runs `skills-ref validate` on a copy with non-spec keys removed. "Host" checks that the name matches the folder, the description is 1,024 characters or less with triggers in the first 200 characters, the body is 500 lines or less, and `disable-model-invocation` matches `agents/openai.yaml`.
3. **Audit every side-effecting skill** (release, deploy, `/deferred`-style writes). Make each one manual-only in both Claude Code and Codex, and add a "manual-only" clause to its description for other agents.
4. **Convert scripts to PEP 723 + `uv run`**, and declare `uv` in `compatibility`.
5. **Add trigger-eval JSON for your five most-used skills**, especially the overlapping data and modeling ones. Run them in Claude Code (`skill-creator`) and Codex (a custom harness).
6. **Publish through three channels**: a Claude Code marketplace, `npx skills`, and `gh skill`. Add a Codex plugin only if you want ChatGPT/Codex directory visibility.
7. **Version with `metadata.version` + CHANGELOG + git tags**, and keep vendored licences and NOTICE files.

## Caveats

- This ecosystem changes monthly. Claude Code alone shipped behaviour changes across v2.1.196–2.1.281 that affect skills. Whether Claude Code will adopt `.agents/skills` is an open question; it wasn't supported when checked in September 2026.
- **Conflicting information on Codex user paths.** OpenAI's current docs say `$HOME/.agents/skills`.\[27\] The Vercel CLI table and older guides from December 2025 list `~/.codex/skills`.\[38\]\[44\]\[75\] Current Codex may still scan the legacy path, but write to `~/.agents/skills`.
- **Unconfirmed claims.** The Windsurf, Goose, Roo and Kilo details and the reported Codex validator allowlist come from community or secondary sources, not vendor docs. The Claude Code 1% listing budget comes from the docs as quoted in a GitHub issue, not from a page I fetched directly.
- The skill counts and security percentages come from vendors with commercial interests (Snyk, marketplaces). Treat them as order-of-magnitude figures.
- Your repo README appears to have recently changed from "primarily for Claude Code" to covering Claude, Codex and Gemini with generated `runtimes/` adapters.\[76\] The advice here is meant to complement that direction, not replace it.

## Sources

1. <https://agentskills.io/specification>
2. [Claude Code reads AGENTS.md only when telemetry is on · blog.szypowi.cz](https://blog.szypowi.cz/p/claude-code-reads-agents.md-only-when-telemetry-is-on/)
3. [Add agents/openai.yaml so Codex honors explicit-only skill invocation · Issue #6 · zanellig/skills](https://github.com/zanellig/skills/issues/6)
4. [Add Codex \`agents/openai.yaml\` to the eight piv skills · Issue #2 · fabianosobreira/piv-pipeline](https://github.com/fabianosobreira/piv-pipeline/issues/2)
5. [Agent Skills](https://cursor.com/docs/skills.md)
6. [Adding agent skills for GitHub Copilot CLI - GitHub Docs](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)
7. [Converge windsurf skills onto .agents/skills/ (Cascade native cross-agent discovery) · Issue #1520 · microsoft/apm](https://github.com/microsoft/apm/issues/1520)
8. [Agent Skills | OpenCode](https://opencode.ai/docs/skills/)
9. [Support for AGENTS.md and .agents/skills/, the community has been asking since August 2025 · Issue #31005 · anthropics/claude-code](https://github.com/anthropics/claude-code/issues/31005)
10. [\[FEATURE\] Support additional skills search paths (e.g. .agents/skills/) to enable sharing with Codex and Gemini · Issue #56193 · anthropics/claude-code](https://github.com/anthropics/claude-code/issues/56193)
11. [.cursor/docs/cursor-skills.md at main · hutchic/.cursor](https://github.com/hutchic/.cursor/blob/main/docs/cursor-skills.md)
12. [Cursor Skills: How to Create and Use Agent Skills - Ajit Singh](https://singhajit.com/how-to-create-and-use-skills-in-cursor/)
13. [skills/.agents/invocation.md at main · mattpocock/skills](https://github.com/mattpocock/skills/blob/main/.agents/invocation.md)
14. [\[P1\] proof / autonomy / proof\_evidence as top-level frontmatter fail skills-ref validate and Claude Code packaging — move under metadata · Issue #263 · ravidsrk/orca-fleet](https://github.com/ravidsrk/orca-fleet/issues/263)
15. [\[DOCS\] Custom Skills and Claude Code plugin Skills silently use different frontmatter schemas · Issue #83981 · anthropics/claude-code](https://github.com/anthropics/claude-code/issues/83981)
16. <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.md>
17. [What Are Agent Skills and How To Use Them](https://strapi.io/blog/what-are-agent-skills-and-how-to-use-them)
18. [Optimizing skill descriptions - Agent Skills](https://agentskills.io/skill-creation/optimizing-descriptions)
19. [Align validation with current skill-authoring guidance by aminmesbahi · Pull Request #97 · agent-ecosystem/skill-validator](https://github.com/agent-ecosystem/skill-validator/pull/97)
20. [agentskills/skills-ref/README.md at main · agentskills/agentskills](https://github.com/agentskills/agentskills/blob/main/skills-ref/README.md)
21. [skills-ref](https://pypi.org/project/skills-ref/)
22. [Skills: top-level \`origin\` frontmatter key isn't in the official Agent Skills spec whitelist · Issue #2233 · affaan-m/ECC](https://github.com/affaan-m/ECC/issues/2233)
23. [GitHub - agentskills/agentskills: Specification and documentation for Agent Skills · GitHub](https://github.com/agentskills/agentskills)
24. [Allow "compatibility" property in frontmatter for consistency with Agent Skills Specification · Issue #187 · openai/skills](https://github.com/openai/skills/issues/187)
25. [Agent Skills · GitHub](https://github.com/agentskills)
26. [Extend Claude with skills - Claude Code Docs](https://code.claude.com/docs/en/skills)
27. <https://developers.openai.com/codex/skills.md>
28. [Agent Skills | Gemini CLI](https://geminicli.com/docs/cli/skills/)
29. [Get started with Agent Skills | Gemini CLI](https://geminicli.com/docs/cli/tutorials/skills-getting-started/)
30. [Agent Skills | Cursor Docs](https://cursor.com/docs/skills)
31. [Skills | Cursor Docs](https://cursor.com/help/customization/skills)
32. [About agent skills - GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
33. [Adding agent skills for GitHub Copilot - GitHub Docs](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
34. [Use Agent Skills in VS Code](https://code.visualstudio.com/docs/agent-customization/agent-skills)
35. [OpenCode Skills - Reusable AI Agent Instructions - OpenCode Docs](https://open-code.ai/en/docs/skills)
36. [Skills | OpenCode](https://opencode.ai/v2/docs/skills/)
37. [GitHub - falconnt/windsurf-skills · GitHub](https://github.com/falconnt/windsurf-skills)
38. [skills/README.md at main · vercel-labs/skills](https://github.com/vercel-labs/skills/blob/main/README.md)
39. [Supported Agents - Skills CLI](https://vercel-labs-skills.mintlify.app/guides/supported-agents)
40. [Introducing skills, the open agent skills ecosystem - Vercel](https://vercel.com/changelog/introducing-skills-the-open-agent-skills-ecosystem)
41. [fix(skills): honor Codex agents/openai.yaml invocation policy by ml12580 · Pull Request #115735 · openclaw/openclaw](https://github.com/openclaw/openclaw/pull/115735)
42. [Skills with disable-model-invocation: true are invisible in Claude Code — users cannot invoke them · Issue #1055 · mattpocock/skills](https://github.com/mattpocock/skills/issues/1055)
43. [Skill with disable-model-invocation: true cannot be invoked by user via slash command · Issue #26251 · anthropics/claude-code](https://github.com/anthropics/claude-code/issues/26251)
44. [Codex CLI Skills & AGENTS.md Setup Guide 2026 | Install…](https://www.agensi.io/learn/codex-cli-agents-md-complete-guide)
45. [\[agnostic-skill\] Ticket: Frontmatter & agentskills.io schema conformance in SKILL.md · Issue #2 · awhipp/ship-it](https://github.com/awhipp/ship-it/issues/2)
46. [Codex AGENTS.md Explained: How Team Instructions Work - Verdent Guides](https://www.verdent.ai/guides/codex-agents-md-explained)
47. [\[FEATURE\] Support user-level .agents/skills/ discovery for cross-agent single-source-of-truth workflows · Issue #66352 · anthropics/claude-code](https://github.com/anthropics/claude-code/issues/66352)
48. [Codex CLI Agent Skills | 2026 Install and Usage Guide | ITECS](https://itecsonline.com/post/codex-cli-agent-skills-guide-install-usage-cross-platform-resources-2026)
49. [Host and maintain a marketplace - Claude Code Docs](https://code.claude.com/docs/en/plugins/host-marketplace)
50. [Engineering at Anthropic](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
51. [SkillJect: Effectively Automating Skill-Based Prompt Injection for Skill-Enabled Agents](https://arxiv.org/html/2602.14211v3)
52. [GitHub - LLMSecurity/awesome-agent-skills-security: 🛡️ A curated list of resources on agent skills security: attacks, defenses, frameworks, and benchmarks for securing AI agent tool use and skill ecosystems](https://github.com/LLMSecurity/awesome-agent-skills-security)
53. [How Do You Build Your First Agent Skill? A Complete SKILL.md Anatomy Guide | Agentman Blog](https://agentman.ai/blog/build-your-first-agent-skill-skillmd-anatomy)
54. [skill-creator - Skill | Smithery](https://smithery.ai/skills/anthropics/skill-creator)
55. [skills/skills/skill-creator/SKILL.md at main · anthropics/skills](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)
56. [Anthropic brings evals to skill-creator. Here’s why that’s a big deal](https://tessl.io/blog/anthropic-brings-evals-to-skill-creator-heres-why-thats-a-big-deal)
57. [How to build a Codex plugin](https://www.simplified.guide/codex/plugin-build)
58. [A Deep Dive into Agent Skills in Gemini CLI – damian\_site](https://damimartinez.github.io/agent-skills-gemini-cli/)
59. <https://code.claude.com/docs/en/plugins/create-marketplace>
60. [Add an invocation-consistency rule: Claude Code and Codex must agree a skill is user-invoked · Issue #50 · cooneycw/skillc](https://github.com/cooneycw/skillc/issues/50)
61. [GitHub - mgechev/skills-best-practices: Write professional-grade skills for agents, validate them using LLMs, and maintain a lean context window. · GitHub](https://github.com/mgechev/skills-best-practices)
62. [Claude Agent Skills 2.0: The Beginner’s Guide to the Updated Skill-Creator](https://innovaitionpartners.com/blog/claude-agent-skills-2.0-the-beginners-guide-to-the-updated-skill-creator)
63. [Claude Code SKILL.md Frontmatter Reference — ClaudeKit Guide](https://getclaudekit.com/blog/tools/skills/skill-frontmatter-reference)
64. [Anthropic's marketplaces - Claude Code Docs](https://code.claude.com/docs/en/plugins/anthropic-marketplaces)
65. [Glossary - Claude Code Docs](https://code.claude.com/docs/en/glossary)
66. [Managing AI Agent Skills with \`npx skills\`: A Practical Guide - DEV Community](https://dev.to/toyama0919/managing-ai-agent-skills-with-npx-skills-a-practical-guide-2an8)
67. [Agent Skills: Creating, Installing, and Sharing Reusable Agent Context | Vercel Knowledge Base](https://vercel.com/kb/guide/agent-skills-creating-installing-and-sharing-reusable-agent-context)
68. [GitHub - openai/skills: Skills Catalog for Codex · GitHub](https://github.com/openai/skills)
69. [Package your plugin – Plugins | OpenAI Developers](https://developers.openai.com/codex/plugins/build)
70. [GitHub - openai/plugins: OpenAI Plugins · GitHub](https://github.com/openai/plugins)
71. [The Ultimate Codex Plugin Guide — Guide](https://promptkit.natebjones.com/20260504_knu_guide_main)
72. [Codex Marketplace: Plugin Distribution and the Plugin Marketplace Add Command | Codex Knowledge Base](https://codex.danielvaughan.com/2026/04/11/codex-marketplace-plugin-distribution/)
73. [install.py: dependency-aware --skill, pre-flight, git-aware --copy by lowmason · Pull Request #16 · lowmason/agent-skills](https://github.com/lowmason/agent-skills/pull/16)
74. [Vendor the TypeSafe agent skill as a project skill by lowmason · Pull Request #10 · lowmason/ces-revisions](https://github.com/lowmason/ces-revisions/pull/10)
75. [Skills in OpenAI Codex — Massively Parallel Procrastination](https://blog.fsck.com/2025/12/19/codex-skills/)
76. [GitHub - lowmason/agent-skills · GitHub](https://github.com/lowmason/agent-skills)
