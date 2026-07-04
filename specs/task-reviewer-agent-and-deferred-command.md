# task-reviewer agent + /deferred command

Two additions to the config repo: a dedicated `task-reviewer` subagent
definition that takes over SDD's per-task reviews from the borrowed
`code-reviewer` agent, and a global `/deferred` slash command that gives
`specs/deferred_items.md` the deliberate review entry point the plan-completion
protocol leaves open.

## Motivation

- SDD dispatches a task review after **every task**, sending the full
  ~120-line template as the prompt each time. The stable contract belongs in
  an agent's system prompt; only per-task material belongs in the dispatch.
  [task-reviewer-prompt.md:11](../skills/subagent-driven-development/task-reviewer-prompt.md)
  currently routes to `code-reviewer if defined` — a borrowed persona whose
  contract (merge-review framing) doesn't match the task-scoped gate.
- `specs/deferred_items.md` is append-only and is only ever re-read by
  brainstorming, and only when a related idea happens to come up. Deferred
  work needs a deliberate trigger: a user-typed command, never auto-fired.

## Requirements

### 1. `agents/task-reviewer.md`

A read-only agent definition carrying the **full stable contract** distilled
from `skills/subagent-driven-development/task-reviewer-prompt.md`:

- Role: task-scoped gate reviewing one task's implementation — spec
  compliance first, then code quality. Not a merge review.
- Read-only contract: no edit tools; must not mutate working tree, index,
  HEAD, or branch state via Bash.
- Diff-reading method: read the dispatch's diff file once; the diff's context
  lines are the view of the change; no codebase crawling; inspection outside
  the diff only for a concrete named risk (one focused check per risk, both
  named in the report); fallback `git diff` commands if the diff file is
  missing.
- "Do Not Trust the Report": the implementer's report is unverified claims;
  rationales never downgrade severity.
- Tests policy: never re-run the suite to confirm the report; focused test
  only for a specific doubt no existing run answers; warnings in reported
  test output are findings.
- Part 1 — Spec Compliance: Missing / Extra / Misunderstood, with ⚠️ items
  for requirements not verifiable from the diff alone.
- Part 2 — Code Quality: code quality, tests-verify-real-behavior, structure
  (one responsibility per file; flag growth this change contributed, not
  pre-existing size).
- Calibration: severity rubric (Important = cannot be trusted until fixed);
  plan-mandated defects are reported as Important, labeled plan-mandated —
  the human decides; acknowledge strengths first.
- Report style: final message IS the report; begins with the spec-compliance
  verdict; every line a verdict, a file:line finding, or a check run; no
  preamble or closing summary.
- Output format: `### Spec Compliance` (✅/❌/⚠️), `### Strengths`,
  `### Issues` (Critical / Important / Minor), `### Assessment` ending in
  `**Task quality:** [Approved | Needs fixes]` + 1–2 sentence reasoning.

Frontmatter: `name: task-reviewer`; `description` stating it is dispatched by
the subagent-driven-development skill after each task and expects a task
brief, implementer report, and diff file; `tools: Read, Grep, Glob, Bash`.
**No `model` field** — the tier is chosen per dispatch (SDD Model Selection).

### 2. SDD template: short dispatch form

Restructure `skills/subagent-driven-development/task-reviewer-prompt.md` into
two forms:

- **Short form** — used when the `task-reviewer` agent is installed. Dispatch
  carries only per-task material: brief file, global constraints, report
  file, base/head SHAs, diff file (+ model per Model Selection). The agent's
  system prompt supplies the method.
- **Full form** — the existing template text, kept verbatim as the portable
  fallback, dispatched to `general-purpose` when the agent is absent.

The routing line becomes: `task-reviewer if defined (short form), else
general-purpose (full form)`. The full form must remain complete enough that
the skill works for installs without the agents directory (the repo is
public). `SKILL.md` keeps pointing at the template file — no change there.

### 3. `commands/deferred.md` — `/deferred`

A markdown slash command, installed globally, that works in any project
following the specs convention. Frontmatter: `description` (one line,
triage-oriented). Behavior:

1. Read `specs/deferred_items.md` in the current project. If the file is
   absent or has no unticked items, report that nothing is deferred and stop.
2. Group unticked items **by theme** (not merely by plan section), noting
   each item's source plan and date from its `## <plan> — <date>` header.
3. Classify each group: **actionable now** vs **still blocked**, judged from
   each item's recorded "why it was deferred".
4. Propose the top promotion candidates — items or groups that deserve to
   become a new spec — with one-line reasoning each.
5. If the user selects candidates, invoke the brainstorming skill with the
   selection as the idea (promotion = new spec = normal design cycle).
6. **Read-only**: the command never edits `specs/deferred_items.md`. Ticking
   remains the job of later plans' completion-protocol runs.

### 4. Provenance, docs, install

- **NOTICE**: add one line to the superpowers "Changes from upstream" list,
  mirroring the code-reviewer entry: `agents/task-reviewer.md is a read-only
  agent definition distilled from the adapted subagent-driven-development
  task-reviewer template (same MIT terms).` `/deferred` is original work
  (MIT, `LICENSE`); no NOTICE entry.
- **README**: add `task-reviewer` row to the Agents table; add a **Commands**
  section (parallel to Agents) documenting `/deferred` with its install line
  (`mkdir -p ~/.claude/commands; ln -s ...`); update the layout-tree comment
  for `commands/` (no longer "scaffolding, empty for now").
- **Repo CLAUDE.md**: update the sentence claiming `commands/`, `hooks/`,
  `rules/` are all empty scaffolding.
- **Install**: remove `commands/.gitkeep`; create symlinks
  `~/.claude/agents/task-reviewer.md → agents/task-reviewer.md` and
  `~/.claude/commands/deferred.md → commands/deferred.md`.

## Verification

- Frontmatter + provenance lints pass (`build/check_frontmatter.py`,
  `build/check_provenance.py`).
- The `task-reviewer` agent type is discovered (appears in the agent list /
  resolvable by the Agent tool); `/deferred` is discovered as a slash command.
- Fixture check: a scratch project with a synthetic `deferred_items.md`
  (mixed ticked/unticked items across two plan sections) — `/deferred`
  groups, classifies, and proposes without editing the file; and on a project
  with no `specs/deferred_items.md` it reports nothing deferred and stops.
- Short-form dispatch sanity check: the short form contains every placeholder
  the full form defines (brief, constraints, report, SHAs, diff, model) and
  no contract text.
- Not in scope: the RED/GREEN pressure-test regime — writing-skills scopes
  that to skill wording changes; the only skill-file change here is a
  mechanical template restructure with the full form preserved verbatim.
