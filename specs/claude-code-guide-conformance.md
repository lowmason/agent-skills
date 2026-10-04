# Claude Code guide conformance — Design Spec

**Status: APPROVED (2026-10-04), R6's amendments included.**
- The owner approved all four design sections in a brainstorming session,
  along with three choices: comply-or-explain, report-only for files outside
  the repo, and approach A.
- The owner then reviewed the written spec and approved it with R6's
  amendments to the drift spec (D1–D5) and the portability spec (P1–P3).
  The plan applies those amendments without a further gate.
- Nothing here has been implemented.

## Purpose and scope

`specs/guides/claude-code-customization-guide.md` (the guide) is the hub. The
repo's Claude Code artifacts are built and checked against it: its skills,
agents, commands, hooks, rules, settings and CLAUDE.md files. This spec
designs that anchoring and takes the guide as it stands.

**What "anchored" means.** Artifacts comply with the guide or explain why not.
- A **fact** is a guide line that a docs page could confirm or refute. That is
  the drift spec's R8.5 test, so both specs classify a line the same way.
  Facts must hold: an artifact that contradicts one has a bug.
- **Advice** is followed, or the register records an exception with its reason.
- Conformance never edits the guide. When the audit judges the guide itself
  wrong, the finding goes to the owner, and to drift's `verify` once that
  exists.

**Five parts:**
1. **Guide anchors** (R1). They use the drift spec's R1.1 IDs, the only way
   anything here names a guide section.
2. **The register** (R2). It links section IDs to artifact kinds, to checks
   and to exceptions.
3. **The lint** (R3). It checks the mechanical rules and the register's
   integrity.
4. **The authoring rule** (R4). It is one CLAUDE.md line, with no net growth
   of that file.
5. **The one-time audit** (R5). It seeds the register. Its fixes go to other
   stages.

**Neighbours.**
- `specs/claude-code-drift-automation.md` (approved 2026-10-03, not
  implemented) keeps the guide current. Its R4 citations keep the statements
  in citing files true.
- Conformance is a different question: does every artifact of a kind follow
  the sections that govern that kind, whether or not the artifact cites the
  guide?
- `specs/agent-skills-portability.md` (approved 2026-10-03, not implemented)
  edits `build/check_frontmatter.py`, `writing-skills` and skill frontmatter.
  This spec leaves all three to it.

## Measured baseline (2026-10-04)

| Fact | Evidence |
|---|---|
| `main` and `origin/main` are both at `6186635` | `git rev-parse` |
| Nothing outside `specs/` references the guide, and the guide names no file in this repo | `git grep customization-guide` |
| The guide has 38 `##`/`###` headings and no anchors. All 8 of its fence lines open at column 0. The `hooks.patterns` fences contain `#` lines | `grep` |
| `build/fences.py` recognizes fence openers at column 0 only, which is sufficient for the guide | `build/fences.py` |
| Inventory: 32 skills, 7 agents, 3 commands. `hooks/` holds `readonly-agent-guard.py` and its tests, `probe-readonly-guard.sh`, `ruff-check.sh`, `ruff-fix.sh`, `uv-guard.sh` and `README.md`. `rules/clean-code-python.md` has `paths: ['**/*.py']`, and `.claude/rules/` links to it through a relative symlink. `.claude/settings.json` sets `model`, `availableModels` and `enforceAvailableModels` | `ls`; file reads |
| The root CLAUDE.md is 225 lines. Its Commands section runs from line 78 to the end (148 lines). `build/CLAUDE.md` is 17 lines | `wc -l`; `grep -n '^#'` |
| `GEMINI.md` `@`-imports CLAUDE.md, and `AGENTS.md` tells Codex to read it completely. A CLAUDE.md change therefore reaches all three runtimes | file reads |
| `check_frontmatter.py` already enforces five rules that come from the guide, without naming it: commands set `disable-model-invocation: true`; `context` is only `fork`; no Haiku `model` on a skill or command; agent tools come from a known set; description caps. `check_agent_file` checks only `name`, description length and `tools` | `build/check_frontmatter.py` |
| `writing-skills`' body is 696 lines. Its Claude Code guidance sits at lines 102–104 (keys, caps, `context: fork`) and 220–235 (tier budgets). Line 106 says a description states only when to use the skill, never what it does. The guide's `skills.description` says to state both | file reads |
| Two deviations from the guide's advice already exist, recorded only in the portability spec. Decision 4: descriptions say "Use when" only. Decision 3: side-effecting skills stay model-invocable for by-name handoffs | `specs/agent-skills-portability.md` |
| All 7 agents list Grep and Glob beside Bash. `hooks/README.md` lines 56, 60 and 64 leave `$CLAUDE_PROJECT_DIR` unquoted. `ruff-check.sh` reads `stop_hook_active` and exits 0 when it is set | file reads |
| `hooks/README.md`'s three JSON blocks all parse. Their hook commands are the three above and the guard's `$HOME/.claude/hooks/readonly-agent-guard.py` (line 121, also unquoted). No JSON block in the root `README.md` or CLAUDE.md is a hook config | `json.loads` over `iter_code_blocks` |
| `install.py` installs skills to all three runtimes, plus agents and commands. Hooks and rules are copy-in templates. `runtimes/` is generated | `install.py`; README |
| Under `~/.claude/`, the `agents/`, `commands/` and `skills/` entries and `hooks/readonly-agent-guard.py` are symlinks into this repo. Four files are outside it: `~/.claude/CLAUDE.md` (33 lines); `~/.claude/settings.json`; `~/.claude/rules/aws-agent-toolkit.md` (31 lines, third-party, no `paths`); and the main checkout's gitignored `.claude/settings.local.json` (about 15 KB of allow rules, `Bash(pip install *)` among them) | `ls -la`; `.gitignore:5` |
| `.gitignore` ignores `.claude/worktrees/` | `.gitignore:25` |
| Plan ids 32–34 are taken on sibling branches. 32 is used twice: on `codex/jax-deep-learning-skills` and on `worktree-deferred-triage-2026-10-03`. 33 is on `codex/recommend-causal-design` and the deferred-triage branch, and 34 is on the deferred-triage branch. `claude/superpowers-drift-spec-update-65c2f5` stops at 31 | `git ls-tree` on each branch |
| Every in-flight workstream grows CLAUDE.md. `codex/jax-deep-learning-skills` has it at 238 lines (+19, −6 against `main`). Portability's R1.9 and R4.4 add lines, as does drift's R12.7 | `git diff --stat`; both specs |

## Decisions and alternatives

1. **Comply-or-explain** (the owner's call). Facts must hold. Advice is
   followed or carries a recorded exception. Rejected:
   - facts only: advice would go unenforced, and the design would shrink to
     drift's `files` review;
   - facts and advice both strictly binding: `writing-skills`' tested "Use
     when" rule would have to change, and no exception could protect Codex or
     Gemini.
2. **A register between the guide and the artifacts** (the owner's call:
   approach A). Rejected:
   - citations in every artifact, reviewed by drift's `files` mode
     (approach C): 32 `SKILL.md` files would cite the same IDs, each check
     would be a model call, deviations would scatter across files, and the
     work could not start before drift Stages 1–3;
   - repo notes inside the guide: they churn drift's section hashes, add
     claims its verifier cannot confirm against the docs, and make a generic
     guide repo-specific;
   - a review checklist with no lint (approach B): nothing would catch a
     regression or a stale waiver.
3. **Neither end names the other.** The guide keeps its generic examples.
   Artifacts gain no conformance links and no version stamps; drift's R4 fact
   citations are unchanged. For conformance, the register's drift citation
   is the only one, so a substantive guide change flags one file for review.
4. **The register is `build/cc_guide/conformance.toml`.** It sits outside
   `specs/`, which the drift spec's R4.2 excludes from citations, so drift can
   flag it. It shares the directory drift's tool will use, and it is TOML read
   with `tomllib`, like drift's `manifest.toml`. It is edited by hand, on the
   owner's decisions; no script writes it. Rejected:
   - `specs/guides/`: the register would never be flagged when the guide
     changes;
   - Markdown tables: fragile to parse;
   - a Python dict: precedented by `DEPENDENCIES` and `SOFT_REFERENCES`, but
     awkward for the owner to edit.
5. **Values that come from the guide live in the register, not in code.**
   Examples are the 200-line target and the agent field list. A guide change is
   then reviewed in one flagged file, and the lint's code changes only when a
   mechanism changes.
6. **Only mechanical rules become checks.** Authors and reviewers read the
   judgment rules in the governing sections, and the audit checks them once.
   This keeps the register small.
7. **Two kinds of exception.**
   - A **deviation** is deliberate and carries a revisit trigger.
   - A **gap** is known non-conformance and names where its fix lands.

   The lint passes from day one without hiding debt.
8. **Waivers match both ways, name explicit paths, and ratchet.**
   - A waiver for a lint check lists its files explicitly, since a glob would
     silently waive a future file. An exception without a check may use globs.
   - A waiver whose violation disappears fails the lint, as a vanished
     `SOFT_REFERENCES` entry does.
   - A waiver on a numeric check carries a ceiling: the file may shrink but
     not grow.
   - An exception with no check has no automatic staleness test. A gap is
     closed by the work named in its `tracked_in`, which removes the entry as
     part of the fix (R6). A deviation is re-examined when its `revisit`
     trigger fires.

   Rejected: one-way waivers, which pile up stale entries that warn nobody.
9. **No deviation comments at the artifact in v1.** The both-ways match shows
   the reason to anyone who edits a waived file into compliance.
   `SKILL.md` frontmatter comments wait for the drift spec's R4.5 load check.
   Skill bodies never carry them.
10. **`writing-skills` keeps its Claude Code text.** It ships to three
    runtimes and the guide ships nowhere, so that text is the only copy an
    installed session sees.
    - The audit checks it once.
    - Drift's R4 citation flags it whenever a section it cites changes.
    - Edits ride portability Stage D's micro-test cycle.

    Rejected:
    - pointing it at the guide: an installed skill cannot follow a path into
      `specs/`;
    - distilling its text into a `references/` file now: revisit that when
      `writing-skills` is split, a portability deferred item.
11. **Nothing new ships.** Anchoring works at authoring, review and lint
    time.
12. **Cross-runtime precedence.**
    1. Never regress a runtime where the artifact works today. The evidence
       is `sync_runtime_assets.py --check` and the Codex and Gemini load
       checks.
    2. Prefer a fix that satisfies every runtime, made in canonical text or in
       the generator, never by hand-editing `runtimes/`.
    3. Otherwise keep the form that is safe across runtimes, and record a
       deviation that names the protected runtime.
13. **Files outside the repo: report only** (the owner's call). Rejected:
    - repo only: the guard's wiring in the global `settings.json` would go
      unexamined;
    - fully in scope: a lint that reads `~/.claude` and an ignored file in the
      main checkout cannot be reproduced from a worktree.
14. **Anchors land in this plan.** The lint validates section IDs, so it
    needs them. Drift's Stage 1 adopts them (R6). Rejected:
    - waiting for drift Stage 1: it blocks this work behind the detector;
    - validating against a copy of the R1.1 table: that creates a second
      source of truth.
15. **A separate lint module.** Portability Stage A rewrites
    `check_frontmatter.py`. Its five rules that come from the guide are mapped
    in the register, not moved. Rejected: extending `check_frontmatter.py`,
    which conflicts with Stage A, and most of the new checks are not
    frontmatter checks.
16. **This plan fixes nothing it finds.** Fixes go to the stages that already
    edit those files, and proposed new checks become deferred items. One spec
    holds one mechanism and one audit.

## Requirements

### R1 — Guide anchors

R1.1 Add drift's R1.1 anchors to the guide. Each of the 38 `##` and `###`
headings is followed on the next line by `<!-- cc: <id> -->`, using exactly
the IDs and order of the R1.1 table in
`specs/claude-code-drift-automation.md`.
- Headings are found outside fenced code, through `build/fences.py`.
- No other edit is made to the guide.

R1.2 A test parses the real guide and pins three things:
- there are 38 headings outside fences;
- each heading's next line is exactly one well-formed anchor;
- the IDs, in heading order, equal the R1.1 table.

This lint's heading–anchor pairing rule (R3.3) deliberately overlaps the
drift spec's R5 rule, because this lint must work before drift Stage 1
lands.

### R2 — The register (`build/cc_guide/conformance.toml`)

R2.1 **File.**
- TOML, read with stdlib `tomllib`. It is edited by hand, on the owner's
  decisions; no script writes it.
- Comments record why each entry exists.
- Paraphrases are in the repo's own wording; no docs text is committed.

R2.2 **`[guide]`** holds `path = 'specs/guides/claude-code-customization-guide.md'`.

R2.3 **`[kinds.<kind>]`** holds four keys:
- `globs`, matched against the files git keeps (tracked, or untracked and not
  ignored, as `install.py` lists them);
- an optional `exclude`;
- `sections`, the IDs governing the kind;
- `description`, one line.

A kind's globs may match no file: drift's `.claude/` skill and agent are
listed before they exist. Initial map, which the audit may change:

| Kind | Globs | Sections |
|---|---|---|
| skill | `skills/*/SKILL.md`, `.claude/skills/*/SKILL.md` | `skills.*` (8), `commands.overview`, `mechanisms.overview`, `lean.ceremony`, `lean.expensive-ops` |
| agent | `agents/*.md`, `.claude/agents/*.md` | `subagents.*` (5) |
| command | `commands/*.md` | `commands.overview`, `skills.frontmatter`, `skills.arguments`, `skills.description` |
| hook | `hooks/*.sh`, `hooks/*.py`, `hooks/README.md`; exclude `hooks/test_*.py` | `hooks.*` (7), `mechanisms.overview` |
| rule | `rules/*.md`, `.claude/rules/*.md` | `rules.rules-files`, `rules.hierarchy` |
| settings | `.claude/settings.json` | `rules.settings`, `hooks.configuration`, `lean.model-routing` (the `TODO(owner)` bullet excepted) |
| claude-md | `CLAUDE.md`, `build/CLAUDE.md` | `rules.claude-md`, `rules.hierarchy`, `context.overview`, `lean.session-hygiene` |
| installer | `install.py` | `skills.locations`, `subagents.overview`, `commands.overview` |

`skills.*` and the like are shorthand here; the register spells out every ID.
Globs are matched with `PurePath.full_match` (Python 3.13), so `*` stays
within one path segment and `**` crosses them.

R2.4 **`[unmapped]`** maps each section that governs no repo file to a reason.
Initially:
- `rules.overview` and `lean.overview`: empty intros;
- `rules.auto-memory`: memory lives outside the repo;
- `lean.measure` and `lean.caching`: these govern how sessions run;
- `lean.mcp`: the repo configures no MCP server;
- `reading.overview`: pointers to the docs.

`[unmapped]` and the kinds' `sections` are disjoint, and together they cover
every anchor.

R2.5 **`[[check]]`** lists mechanical rules only. Each entry has:
- `id`, `kind` and `sections`;
- `type`: `'fact'` or `'advice'`, per R8.5's test;
- `rule`: a one-line paraphrase;
- `enforced_by`: `'check_conformance'` or `'check_frontmatter'`;
- any value taken from the guide, as a named parameter.

The seven `check_conformance` checks are in R3.4. The `check_frontmatter`
entries record existing rules without changing them:

| Check | Sections | Rule |
|---|---|---|
| `command-manual-only` | `commands.overview` | Commands set `disable-model-invocation: true` |
| `fork-only-context` | `skills.frontmatter` | `context`, when present, is `fork` |
| `no-haiku-skill-model` | `skills.frontmatter` | No Haiku `model` on a skill or command, since auto mode ignores it |
| `known-agent-tools` | `subagents.frontmatter` | Agent tools come from a known set |
| `description-cap` | `skills.description` | Descriptions stay within the listing cap. The repo's 1,024-character spec cap is stricter |

When portability Stage A adds its R1.7 body-length warning, that stage adds a
`skill-body-size` entry for `skills.overview` mapping to it (R6, P3).

R2.6 **`[[exception]]`.** Every exception carries:
- `id`, unique;
- `type`: `'deviation'` or `'gap'`;
- `sections` and `artifacts`;
- `guide`: what the guide says, paraphrased;
- `reason` and `evidence`: a commit, spec decision, measurement or audit row.

Optional fields:
- `check`: a check ID; the exception then waives that check;
- `protects`: a subset of `['codex', 'gemini']`;
- `ceiling`: for a numeric check only, the highest value the file may reach.

By type:
- A deviation carries `revisit`, an observable trigger, and no `tracked_in`.
- A gap carries `tracked_in` (drift Stage 3, a portability stage, a deferred
  item or a plan) and no `revisit`.

On paths:
- With `check` set, `artifacts` lists explicit paths that exist.
- Without it, `artifacts` may use globs, each matching at least one file.

R2.7 **Expected entries.** The owner gate (R5.5) decides the final set.

| Exception | Type | What it covers |
|---|---|---|
| `grep-glob-beside-bash` | gap | `check = 'bash-search-tools'`; the 7 agents by path; `protects = ['gemini']`; tracked in drift Stage 3 (its R11.5 #1) |
| `hook-dir-unquoted` | gap | `check = 'hook-dir-quoted'`; `hooks/README.md`; tracked in drift Stage 3 (R11.5 #3) |
| `claude-md-size` | gap or deviation, the owner's call | the root CLAUDE.md; the owner sets `ceiling` at the gate, expected `225`, today's length |
| `description-when-only` | deviation | `skills/*/SKILL.md`; evidence: `writing-skills`' "Skill Discovery Optimization" section and portability Decision 4; revisit when trigger-eval suites exist (a portability deferred item) |
| `side-effecting-skills-invocable` | deviation | the skills the audit lists; evidence: portability Decision 3; revisit when the guide documents a way for one skill to hand off to a manual-only skill |

Drift's #2, the continuation choice in `ruff-check.sh`, stays in drift Stage 3
and fails no check: the script reads `stop_hook_active`.

R2.8 **Citation.** The register carries one `# cc-guide:` line citing all 38
IDs, in the TOML placement that R6 adds to the drift spec. Whichever lands
second adds it, this plan or drift Stage 2. Written against the guide at
2.1.288, the register is stamped `@2.1.288`.

### R3 — The lint (`build/check_conformance.py`)

R3.1 **Invocation.** `uv run --python 3.13 --with pyyaml python
build/check_conformance.py`.
- Stdlib plus `pyyaml`, as `check_frontmatter.py` uses.
- `build/fences.py` handles fences.
- It finds the repo from its own location, never the working directory.

R3.2 **Exit codes.**
- 0: clean.
- 1: one stdout line per violation, in the form
  `<file>: <check> (<section>): <message>`.
- 2: the guide or register is missing or does not parse as TOML, so a crash
  never looks clean.

Field-level register problems are violations, not errors.

R3.3 **Integrity rules.**
1. Anchors:
   - every heading outside fences has exactly one well-formed anchor on its
     next line;
   - every section ID in the register exists as an anchor;
   - every anchor sits in a kind's `sections` or in `[unmapped]`, never both.
2. Every `[[check]]` whose `enforced_by` is `check_conformance` has an
   implementation, and every implementation has an entry.
3. Every exception has the fields its type requires (R2.6). It cites existing
   section IDs and an existing `check`. Its paths exist, or its globs match.
   Check and exception IDs are unique.
4. Waivers match both ways, per (check, file), however many occurrences the
   file holds:
   - a check violation that no exception waives fails;
   - an exception file that no longer violates its check fails. The message
     gives the exception's ID and reason and says to remove the entry or the
     file from it;
   - a waived file that exceeds its `ceiling` fails.

R3.4 **The seven checks.** Parameters come from the register (Decision 5).

| Check | Sections | Type | Passes when |
|---|---|---|---|
| `claude-md-size` | `rules.claude-md` | advice | each claude-md file has fewer than `limit = 200` lines |
| `rule-paths` | `rules.rules-files` | advice | each rule file's frontmatter has a non-empty `paths` list, unless the check's `always_on` parameter lists it. The same section says a rule that must persist past compaction should drop `paths`, and `always_on` starts empty. A listed rule that has `paths` fails. Each `.claude/rules/` symlink must resolve inside the repo, since a target outside it would be an external import |
| `hook-dir-quoted` | `hooks.patterns` | advice | in every hook `command` string (the `hooks` tree of each JSON block in hook-kind Markdown, and of `.claude/settings.json`), each `$CLAUDE_PROJECT_DIR` or `${CLAUDE_PROJECT_DIR}` lies inside a double-quoted span, found by scanning quote state. A single-quoted occurrence fails too, since it never expands. A JSON block that does not parse is a violation |
| `stop-hook-guard` | `hooks.exit-codes`, `hooks.patterns` | advice | for each command wired to `Stop` in those trees, the basename of its first shell word (`shlex.split`) names a hook-kind script that reads `stop_hook_active`. An unresolvable script is a violation |
| `agent-fields` | `subagents.frontmatter` | fact | agent frontmatter keys come from `fields`, and `model` is in `models` or is a full `claude-` model ID |
| `readonly-agent-tools` | `subagents.tools` | advice | an agent with a line reading exactly `## Read-only contract` (the marker `check_frontmatter.py` uses) has a `tools` list without any of `forbidden_tools` (`Write`, `Edit`, `NotebookEdit`) and no `memory` key |
| `bash-search-tools` | `subagents.tools` | fact | an agent whose `tools` include Bash lists neither Grep nor Glob |

`tools` may be a comma-separated string or a YAML list.

The register holds two lists taken from the guide's `subagents.frontmatter`:
- `fields`: `name`, `description`, `tools`, `disallowedTools`, `model`,
  `effort`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`,
  `memory`, `background`, `isolation`, `omitClaudeMd`, `experimental`,
  `color` and `initialPrompt`;
- `models`: `sonnet`, `opus`, `haiku`, `fable` and `inherit`.

R3.5 **Tests.**
- `build/test_check_conformance.py` is written red-first, rule by rule, with
  hand-written fixture trees.
- Cases:
  - each check, passing and failing;
  - each integrity rule;
  - both waiver directions;
  - a ceiling breach;
  - a heading inside a fence that must not be read as a heading;
  - exit code 2 on an unparseable register;
  - R1.2's pin on the real guide;
  - a run against the repo that passes. It can pass only once the owner gate
    (R5.5) has filled the register, so the plan orders it after that gate.
- `cd build && pytest` collects the file, so the build count rises by +N.

R3.6 **Citation.** The lint cites the sections whose mechanisms it parses
(`hooks.configuration`, `subagents.frontmatter`, `rules.rules-files`), under
the same rule as R2.8.

### R4 — Authoring rule and CLAUDE.md

R4.1 **The rule.** CLAUDE.md's "Editing skills" section gains one rule; the
section may be retitled to cover every artifact kind. It says:
- a Claude Code artifact (skill, agent, command, hook, rule, settings or
  CLAUDE.md) follows the guide sections listed for its kind in the register;
- any departure is recorded there as a deviation or a gap;
- `check_conformance.py` runs before committing.

The rule binds whichever runtime does the editing, because conformance
concerns the artifact's target runtime.

R4.2 **The command.** The `check_conformance.py` command joins the existing
"Frontmatter + provenance lints" entry in Commands.

R4.3 **Net zero.** The same commit trims at least as many CLAUDE.md lines as
R4.1 and R4.2 add. It condenses wording; it removes no instruction, since
Codex and Gemini read the same file. Validation item 5 checks it. If the
owner sets the ceiling at 225, the lint enforces it as well.

### R5 — The one-time audit

R5.1 **Scope.** All 38 sections against every in-scope kind, plus a separate
report section on the four files outside the repo.

R5.2 **Method.**
- For each section:
  1. list the rules that bear on repo artifacts;
  2. classify each one as fact or advice;
  3. check every artifact of each governed kind.
- The lint's day-one violations are the mechanical findings. The audit judges
  the rest.
- Four subagents run with read-only instructions at Sonnet, one per group:
  1. skills;
  2. agents and commands;
  3. hooks, rules and settings;
  4. CLAUDE.md and the installer.

  The plan picks the agent type. No subagent edits a file.
- Each finding row holds the section ID, guide line, rule, fact or advice,
  artifact `file:line`, status and supporting quotes. The status is one of
  follows, gap, deviation candidate or n/a. Quotes are at most 25 words, from
  the guide and from the artifact.
- Every quote is re-grepped as a single-line match before the report is
  written, the refresh's rule.

R5.3 **Files outside the repo.**
- The audit reads, by absolute path:
  - `~/.claude/CLAUDE.md`;
  - `~/.claude/settings.json`;
  - `~/.claude/rules/*`;
  - the main checkout's `.claude/settings.local.json` (located through
    `git worktree list`).
- The report paraphrases settings rather than quoting them, and it never
  reproduces a value that looks like a credential.
- Nothing is edited, and nothing enters the register.

R5.4 **Output.** `specs/claude-code-conformance-audit-<YYYY-MM-DD>.md`, a
dated record. Register entries cite its rows as evidence.

R5.5 **Owner gate.** The owner decides each gap or deviation candidate:
- a **deviation**, with its reason and revisit trigger; or
- a **gap**, with its destination.

Then the register is filled in and the lint passes. Destinations:

| Finding | Destination |
|---|---|
| The three known drifts | drift Stage 3 |
| `check_frontmatter.py` | portability Stage A |
| `writing-skills` | portability Stage D |
| Anything else | a deferred item, flagged for `/deferred` when it is a quick fix |

A deferred item created for a gap names the register exception that its fix
must remove. That closes the loop R6's D5 and P2 close for the staged
destinations. This plan applies no fix.

R5.6 **Proposed checks.** A mechanical rule the audit finds beyond R3.4's
seven becomes a deferred item. This plan builds exactly seven checks.

R5.7 **Candidates already visible.** The audit confirms or rejects each
one; none is decided here.
- **CLAUDE.md**: 225 lines against `rules.claude-md`'s target.
- **`enforceAvailableModels`**: set in project settings, while
  `lean.model-routing` places its effect in managed settings.
- **`writing-skills`**:
  - its body is 696 lines against `skills.overview`;
  - line 222 says every description stays resident, while
    `skills.listing-budget` drops descriptions by rank;
  - line 304's claim about `@` loading, against `rules.hierarchy`;
  - it gives no advice to put critical rules first, though
    `skills.progressive-disclosure` says compaction keeps 5,000 tokens.
- **brainstorming**: its "every project goes through this process" against
  `lean.ceremony`'s "skip when you can already describe the solution".
- **`commands/`**: it stays as command files, while `commands.overview` says
  the docs recommend skills for new work. The command files generate the
  Gemini adapters.
- **Reviewer agents**: they hold Bash, guarded by the read-only hook, beside
  `subagents.tools`' reviewer tool set.
- **CLAUDE.md's "run before committing" lints**: prose where
  `mechanisms.overview` would use a hook.
- **The read-only guard**: stdlib-only with no dependencies, so
  `hooks.pitfalls`' advice on `uv` inline deps probably does not apply.
- **`hooks/README.md:121`**: the guard's install command leaves `$HOME`
  unquoted. `hook-dir-quoted` covers only `$CLAUDE_PROJECT_DIR`, the variable
  the guide's pattern quotes.
- **Outside the repo**: the AWS rule has no `paths`, and
  `settings.local.json` contains `Bash(pip install *)`.

### R6 — Amendments to the drift and portability specs

Both specs are already approved, so this plan applies these amendments only
with the owner's approval. The register's waivers and its CLAUDE.md ceiling
reach into their stages, and each amendment says how.

**`specs/claude-code-drift-automation.md`:**
- D1. Stage 1 adopts the anchors already present instead of adding them.
- D2. R4.1 gains a TOML placement: a `# cc-guide:` line before the first key
  or table, preceded only by comments and blank lines.
- D3. R4.2's known clusters gain `build/cc_guide/conformance.toml` and
  `build/check_conformance.py`. They are stamped `@2.1.288`, not R11.3's
  bootstrap `@2.1.219`.
- D4. R12.7's CLAUDE.md additions stay within the `claude-md-size` ceiling,
  either by trimming elsewhere or by raising the ceiling in the register on
  purpose, with a reason.
- D5. Whenever drift applies a fix that resolves a conformance gap, it
  removes or narrows the matching register exception in the same
  working-tree change and runs `check_conformance.py`. This covers Stage 3's
  fixes to the known drifts and any later R8.8 correction. R8.8's step 5
  runs `check_conformance.py` beside `lint`. Without this, the both-ways
  match fails the fix as a stale waiver.

**`specs/agent-skills-portability.md`:**
- P1. The CLAUDE.md lines from R1.9 and R4.4 stay within the
  `claude-md-size` ceiling, by trimming elsewhere or by raising the ceiling
  on purpose, with a reason.
- P2. When Stage A or Stage D fixes a gap the register tracks to it, the same
  change removes or narrows the exception and runs `check_conformance.py`.
- P3. When Stage A adds R1.7's body-length warning, it adds the register's
  `skill-body-size` entry mapping `skills.overview` to that warning.

## Sequencing and execution constraints

One plan, in this order:
1. R1 anchors.
2. The register skeleton (R2.1–R2.5), then R3 test-first.
3. The R5 audit.
4. The owner gate.
5. Finish the register; the lint goes green.
6. R4.
7. R6.
8. Validation.

Constraints:
- **Worktree.** Check `git rev-parse main origin/main` first: `EnterWorktree`
  branches from `origin/main` and leaves out unpushed commits.
- **Plan id.** Check `specs/plans/` on every branch (`git ls-tree`) before
  allocating one. Ids 32–34 are taken on sibling branches, and 32 twice.
- **Test counts** are +N deltas, never absolute totals. CLAUDE.md's
  build-suite count moves by the same delta.
- **No artifact fixes.** CLAUDE.md changes only as R4 allows. The plan edits
  no skill, so the self-modifying-plan hazard does not arise.
- **Drift coupling.**
  - The anchors and R6's amendments come from this plan.
  - Whichever lands second, this plan or drift Stage 2, adds the register's
    and the lint's citation lines.
  - The audit's three known drifts stay with drift Stage 3. D5 keeps the
    register in step when Stage 3 fixes them.
- **Portability coupling.**
  - Stage A owns `check_frontmatter.py`, and P3 maps its R1.7 warning.
  - Stage D owns any `writing-skills` edit, batched into its single
    micro-test cycle.
  - P1 and P2 cover the ceiling and the gaps routed to Stages A and D.
  - Line 25 of `writing-skills` and `anthropic-best-practices.md` stay out of
    every task.
- **JAX branch.** Its skills fall under the skill kind, and its merge runs
  the lint.
  - Its CLAUDE.md is 238 lines, over the expected 225 ceiling.
  - Whichever lands second, the JAX merge or this plan, trims CLAUDE.md or
    raises the ceiling in the register on purpose, with a reason.
- **The ceiling at the gate.** Every in-flight workstream grows CLAUDE.md.
  The owner sets `claude-md-size`'s ceiling at the gate (R5.5) knowing that.
- **Nothing outward-facing.** Nothing is pushed or posted.

## Validation and acceptance

1. Every in-scope kind maps to its sections, and every anchor is mapped or
   unmapped with a reason. Every rule that applies is followed or carries an
   exception.
2. `check_conformance.py` exits 0 on the repo. Each check and integrity rule
   has a test that failed before its implementation and passes after.
3. R1.2's pin passes, so the anchors equal drift's R1.1 table.
4. The audit report exists, and every quote in it was re-grepped. The owner's
   decisions are recorded in the register.
5. This plan leaves CLAUDE.md no longer than 225 lines, its length at
   `6186635` (R4.3).
6. Every existing gate passes:
   - `check_frontmatter.py`;
   - `check_provenance.py`;
   - `check_snippets.py skills/` (Tier 1);
   - the dependency-drift test;
   - the `build/` suite;
   - `sync_runtime_assets.py --check`, with no adapter change.

## Out of scope (deferred; logged to `specs/deferred_items.md` at plan completion)

- Fixing what the audit finds. Each fix goes where R5.5 sends it.
- Checks beyond R3.4's seven (R5.6).
- Keeping the guide current: that is the drift spec's work.
- The Codex and Gemini guides in `specs/guides/`. The register is per guide,
  so a second register could follow later.
- The guide's §8 `TODO(owner)`.
- `skills/writing-skills/anthropic-best-practices.md`, whose provenance is
  the owner's call.
- Editing any of the four files outside the repo.
- Deviation comments at artifact sites (Decision 9), and a distilled
  `references/` file for `writing-skills` (Decision 10).

## Provenance and copyright

- The register, lint, tests and audit report are original work under the
  repo's MIT `LICENSE`.
- The register paraphrases the guide in the repo's own wording. The audit's
  quotes come from the guide and the repo's artifacts, both this repo's text.
  No docs text is committed.
- `NOTICE` is unaffected, because no skill is added.

## Sources and verification notes

- The guide, the drift spec and the portability spec at `6186635`.
- The drift spec supplies:
  - R1.1 (the IDs);
  - R2.3 and R5 (section hashes and the lint);
  - R4.1, R4.2 and R4.5 (citation placement, scope and the load check);
  - R8.5 (fact versus judgment);
  - R8.7 (the `files` review);
  - R11.1, R11.3 and R11.5 (bootstrap and the three known drifts);
  - R12.7 (CLAUDE.md additions).
- The portability spec supplies Decisions 3 and 4, R1.7 and Stage D.
- File reads at `6186635`:
  - `build/check_frontmatter.py`, `build/fences.py`,
    `build/test_runtime_support.py` (`SOFT_REFERENCES`) and `install.py`;
  - `skills/writing-skills/SKILL.md`, `skills/brainstorming/SKILL.md` and the
    agent and command frontmatter;
  - `hooks/ruff-check.sh`, `hooks/README.md`, `.claude/settings.json`,
    `rules/clean-code-python.md`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`,
    `README.md` and `.gitignore`.
- The `~/.claude/` listing and the main checkout's `settings.local.json`
  were read on 2026-10-04.
- Memory notes: `cc-guide-refresh`, `writing-skills-anthropic-page`,
  `agent-skills-buildout`, `skill-listing-budget` and `proportional-process`.
