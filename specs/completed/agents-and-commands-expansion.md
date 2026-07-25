# Five agents + two commands (roster expansion)

**Status: COMPLETE (2026-07-25)** — implemented by
[plan 17](../plans/completed/17-agents-and-commands-expansion.md); retired
to `specs/completed/`. One post-approval amendment landed with user
approval at the completion gate: `/license-audit` gained a Layer-2 bullet
for cited-but-not-redistributed works (commit `a24d252`), beyond §7 below.

Seven additions to the config repo, filtered from a deep-research pass
(2026-07-24) over community catalogs and official Claude Code guidance, then
scoped against the existing 28 skills: five subagent definitions
(`security-auditor`, an `Explore` override, `test-runner`, `debugger`,
`docs-writer`) and two user-triggered commands (`/fix-issue`,
`/license-audit`). All prompt bodies are original work in this repo's voice —
the research informs role shape, tool lists, and model pins only.

## Motivation

- The model-routing policy prescribes Haiku for exploration and Opus at
  review checkpoints, but only the review half has agent files. An
  `agents/*.md` is the only durable carrier of a model pin + tool
  restriction + reusable system prompt.
- Plan 11 deferred a Haiku-pinned `agents/Explore.md` override ("add only if
  the per-turn saving proves insufficient"). New evidence settles it: since
  ~v2.1.198 the built-in Explore inherits the parent model
  (anthropics/claude-code#29768), so exploration during Opus planning
  sessions bills at Opus. This spec implements that deferred item.
- The existing reviewers check plan conformance and code quality; nothing
  applies a security lens, while the httpx BLS-ETL work handles API keys and
  credentials.
- Commands are now skills mechanically (guide §4); a bare command file with
  `disable-model-invocation: true` is invocable, never auto-fired, and stays
  out of the model-visible listing — the cheap kind of addition under the
  skill-listing budget.

## Requirements

### 1. `agents/security-auditor.md`

Frontmatter: `name`, `description` (dispatch conditions: security review of
a diff, branch, or repo), `tools: Read, Grep, Glob, Bash`, `model: opus`,
`effort: xhigh` (both mirroring `code-reviewer`).

Body, in the house contract style:

- Scope: security findings only — not general code review. Injection
  (SQL/command/eval), committed secrets and credential handling (API keys,
  `.env`, tokens in URLs or logs), insecure deserialization (`pickle`,
  unsafe `yaml.load`), TLS verification in httpx code, dependency risks.
- Read-only contract: same prose as `code-reviewer` (no edit tools; no
  mutation of working tree, index, HEAD, or branch state via Bash). Note:
  this is contract prose, not mechanical enforcement — see Out of scope.
- Output: severity-ranked findings (Critical/Important/Minor) with
  `file:line` and concrete remediation; acknowledge what is handled well;
  end with an overall verdict.

### 2. `agents/explore.md` — the `Explore` built-in override

Lowercase filename per repo convention; **the frontmatter `name: Explore`
is load-bearing** — agent-type resolution keys on the `name` field alone
(basename not consulted) and is case-sensitive, so a lowercase *name*
would register a second agent type beside the un-shadowed built-in
instead of overriding it (both probe-verified, see Verification). Do not
"fix" the capital E in the name field.

Frontmatter: `name: Explore`, `description` preserving the built-in's
contract (read-only search agent for broad fan-out searches; caller
specifies breadth, e.g. "medium" or "very thorough"; locates code, does not
review it), `tools: Read, Grep, Glob, Bash`, `model: haiku`. No `effort`
pin.

Body:

- Read-only contract prose (as above).
- Output contract (the value-add over the built-in): findings as
  `path:line` references each with a one-line relevance note; no file
  dumps; a structured closing summary the caller can act on without
  re-reading files.
- This is the global Explore→Haiku lever and the default `context: fork`
  target envisioned by the plan-11 deferred item.
- ⚠ Override shadowing of a built-in agent name is version-sensitive;
  verification probes it on the installed binary before the symlink is
  considered live.

### 3. `agents/test-runner.md`

Frontmatter: `name`, `description` (runs a test suite in isolation and
reports failures; dispatch must supply the exact command), `tools: Bash,
Read, Grep, Glob`, `model: haiku`.

Body:

- Generic across repos: the dispatch supplies the test command (this repo's
  five directory-scoped `uv run` suites live in CLAUDE.md; work repos supply
  theirs). The agent never guesses a runner.
- Output contract: failing tests with complete error messages and
  tracebacks — never truncated, never summarized to bare counts; warnings
  in test output are findings (matching `task-reviewer` policy);
  pass/fail/skip counts; no diagnosis — root-causing stays with the caller
  (systematic-debugging in the main session).
- Contract: never edits source files; never mutates git state.

### 4. `agents/debugger.md`

Frontmatter: `name`, `description` (isolated fix of a self-contained,
reproducible failure; dispatch carries the repro), `tools: Read, Edit,
Bash, Grep, Glob`, `model: sonnet`. Edit is included because fixing
requires modifying code (per the official archetype); the reviewer/search
agents stay read-only.

Body:

- For self-contained failures — a named failing test, a crashing script —
  where the dispatch carries everything needed to reproduce. Not a
  replacement for interactive debugging, which needs main-session context;
  the systematic-debugging skill is unchanged (see Out of scope).
- Method (distilled from systematic-debugging): reproduce first → isolate
  the root cause → minimal fix — no speculative patches; write the failing
  test first if none exists (TDD); verify by re-running.
- Contract: leaves all changes uncommitted for the caller to review; never
  commits, pushes, or otherwise mutates git history.

### 5. `agents/docs-writer.md`

Frontmatter: `name`, `description` (technical documentation in an isolated
context: READMEs, analysis writeups, docstrings, general docs), `tools:
Read, Write, Edit, Grep, Glob, Bash`, `model: sonnet`.

Body — a generalist with three named lanes plus a fallback:

- Repo/package READMEs: purpose, install, usage, layout tree.
- Analysis writeups: methods → results → caveats structure for finished
  data work (an explore-data profile, a model comparison, a validation
  run).
- Docstrings and API docs: consistent with the clean-code comment
  discipline — a comment earns its keep only by stating what the code
  cannot show.
- General technical docs (runbooks, guides, ADR prose) when dispatched.
- Grounding rule: read the code before describing it; never invent
  behavior; explicitly flag any claim not verified against the source.
- Contract: writes files but never commits.

### 6. `commands/fix-issue.md` — `/fix-issue <number|url>`

Bare command file. Frontmatter: `description` (one line),
`disable-model-invocation: true` (side-effecting; fires only when typed).

Behavior — the bugfix-only lane:

1. `gh issue view` the argument. Graceful stop (with the reason) if `gh` is
   missing or unauthenticated, or the repo has no GitHub remote.
2. Classify the issue: bug-shaped (existing behavior is broken) vs
   feature-shaped (new behavior). Feature-shaped → stop and invoke the
   brainstorming skill with the issue as the idea; the command never
   implements features. The spec gate stays intact.
3. Create a fix branch off the default branch; never fix on the default
   branch directly.
4. Fix under the existing disciplines, by name: systematic-debugging
   (reproduce before patching), test-driven-development (failing test
   first), verification-before-completion (run the relevant suite and
   confirm before claiming done). The suite run may dispatch `test-runner`.
5. Commit, push, and open the PR with `gh`, linking the issue
   (`Fixes #N`).

### 7. `commands/license-audit.md` — `/license-audit`

Bare command file. Frontmatter: `description`,
`disable-model-invocation: true` (deliberate trigger; keeps the listing
lean). Read-only: reports findings, never edits files.

Two layers, degrading gracefully by repo:

1. Mechanical: run the repo's own gates when present (here:
   `build/check_provenance.py`, `build/check_frontmatter.py`); otherwise
   scan `pyproject.toml` / `uv.lock` and report each dependency's license.
2. Judgment: NOTICE ↔ artifact-list sync (every skill, agent, and command
   accounted for); LICENSE file presence; license-compatibility flags
   (copyleft or NC material in an MIT repo); attribution invariants
   recorded in NOTICE/CLAUDE.md (no-book-prose, nothing from
   `build/.scratch/` committed); uncredited-adaptation risks (files whose
   content or history points at external sources absent from NOTICE).

### 8. Docs, provenance, install

- **NOTICE**: unchanged — all seven bodies are original works by Lowell
  Mason under the repo MIT license (the `/deferred` precedent). If any
  wording is later adapted from an external prompt catalog, that file gains
  a NOTICE entry at that time.
- **README**: five new Agents-table rows (the `Explore` row carries the ⚠
  override-shadowing note) and two new Commands-table rows; symlink lines
  added to the Agents and Commands install sections.
- **Repo CLAUDE.md**: update the sentence enumerating `agents/` and
  `commands/` contents (currently names only the reviewers and
  `/deferred`).
- **Install**: seven per-file symlinks — five into `~/.claude/agents/`, two
  into `~/.claude/commands/`.

## Verification

- `build/check_frontmatter.py` and `build/check_provenance.py` pass.
  (`check_frontmatter.py` lints `agents/*.md` and `commands/*.md`;
  `check_provenance.py` covers `skills/` attribution and tracked binary
  assets only — corrected at retirement; the approved original overstated
  its scope.)
- Discovery: all five agents resolvable by the Agent tool; `/fix-issue` and
  `/license-audit` appear as slash commands.
- **Explore-override probe**: one `claude -p` probe (plan-15 Task 8 style)
  on the installed binary confirming the custom `Explore` shadows the
  built-in (e.g. its dispatch runs on Haiku / uses the custom output
  contract). **RUN 2026-07-25, positive, on 2.1.219** — a sentinel-bearing
  `~/.claude/agents/Explore.md` shadowed both the Agent-tool listing (the
  parent quoted the sentinel description verbatim) and the dispatch path
  (the dispatched agent's report opened with the sentinel line and used the
  custom `path:line` output contract); probe file removed afterward. The
  `model: haiku` pin follows from file resolution and was not independently
  observed. Two follow-up probes (same day, same binary): resolution is
  **case-sensitive** — a `name: explore` agent registered as a second type
  beside the un-shadowed built-in — and keys on the **frontmatter `name`
  alone** — `agents/explore.md` with `name: Explore` shadowed cleanly,
  licensing the lowercase filename. Mechanism is version-sensitive:
  re-probe if the binary has moved when the plan executes.
- Fixtures:
  - `security-auditor` on a scratch diff with a planted secret and an
    injection pattern — must find both, with `file:line`.
  - `test-runner` on one real suite from CLAUDE.md — output contract holds
    (complete tracebacks, warnings surfaced, no diagnosis).
  - `/license-audit` on this repo — reconciles cleanly against NOTICE.
  - `/fix-issue` on a repo without a GitHub remote — graceful stop.
  - `debugger` on one synthetic failing test in a scratch dir — fixes it,
    leaves the change uncommitted.
  - `docs-writer` on one small README task in a scratch dir — output is
    grounded in the files present.
- A live end-to-end `/fix-issue` run against a real GitHub issue is
  interactive verification, deferred to first real use.

## Out of scope (recorded deliberately)

- PreToolUse hooks mechanically enforcing the read-only contracts
  (`security-auditor`, `Explore`, `test-runner`) — deferred-item candidate;
  contract prose matches the existing reviewer precedent.
- Any skill-file edits: no `context: fork` wiring into systematic-debugging,
  no routing changes in requesting-code-review. Those are skill-wording
  changes under the writing-skills regime and would need their own
  pressure-testing.
- Completion note: the plan-completion protocol ticks the plan-11 deferred
  item (Haiku-pinned Explore override) when this spec's plan retires.

## Research grounding (brief)

Deep-research run of 2026-07-24, 21 sources, 25 claims adversarially
verified (21 confirmed, 4 refuted). Load-bearing sources: the official
best-practices security-reviewer example and investigation-subagent
guidance (code.claude.com/docs/en/best-practices), the sub-agents
isolation examples for test running and the debugger archetype
(code.claude.com/docs/en/sub-agents), the commands→skills merge and
`disable-model-invocation` (code.claude.com/docs/en/skills), the
wshobson/agents model-tier table (matching this repo's routing policy), and
anthropics/claude-code#29768 (Explore model inheritance). No community
prompt text is adapted; adoption evidence shaped the roster, not the
wording.
