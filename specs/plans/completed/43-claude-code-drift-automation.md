# Claude Code Drift Automation, Stage 2 (Wiring) Implementation Plan

**Status: COMPLETE (2026-10-12)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Where this runs.** This plan reaches `main` through its own PR. After that merges, create the worktree from the main checkout (Global Constraints, "Worktree") and execute there: `/Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2`, on branch `feat/cc-drift-stage2`. Start the execution session with that worktree as its working directory, not the main checkout: subagent-driven-development's `sdd-workspace` and `review-package` take the repo root and `HEAD` from the shell's working directory, so launched from the main checkout they would write the SDD workspace there and diff `main`. Below, **`W`** names that absolute path in prose. Every command spells the path out, because a worktree-isolated session refuses compound shell (`&&`, `$(...)`).

**Goal:** Build Stage 2 of the drift spec, the wiring. Every file whose correctness rests on a Claude Code fact carries a citation naming the guide sections it relies on. `lint` keeps the citations honest and prints the stale ones. `check` lists the citing files of each flagged section and the stale backlog. `baseline cite` restamps a file after its review. The first sweep tags 41 files.

**Architecture:** Stage 1's modules gain the citation layer without new modules:
- `guide.py`: R4.1's parser. It holds the two comment forms, the per-kind placement and the `Citation` record (the Layout puts the citation parser there).
- `state.py`: the citation scan, `Source.grep` and `citing_files`. It reads tracked files through `git grep` at the same ref as every other input (R6.1).
- `lint.py`: R5's citation rules and the stale computation.
- `check.py`: R6.8's lists.
- `baseline.py`: `cite`, and `accept`'s citer stamps (R2.4).
- `cli.py`: the command line.

Outside `cc_guide/`, three gates change. `check_conformance.py` stops reading imports inside block-level HTML comments, as Claude Code does. `run_commit_lints.sh` gains `cli.py lint` as a seventh lint. The sweep then adds one comment line to each of the 41 files.

**Tech Stack:** Python 3.13 through `uv run`, stdlib only inside `build/cc_guide/` (`ast`, `re`, `subprocess` for git); pytest; pyyaml in `build/`'s frontmatter tests; git; bash.

**Spec:** `specs/claude-code-drift-automation-spec.md` (DESIGN APPROVED 2026-10-03; Stage 1 shipped as plan 38). R-numbers, "Sequencing item N" and "Validation item N" point into it. Task 1 writes the owner's 2026-10-12 amendments into it. The base is `main` at `b5a209d` plus this plan's own merge.

## Global Constraints

Every task's requirements implicitly include this section.

- **Scope (Sequencing item 2).** In scope:
  - R4: citations, their forms and placement, and the scope list, as Task 1 amends it;
  - R5's citation rules and `STALE` lines;
  - R6.8's citing-file lists and stale backlog;
  - R7's `baseline cite`, and R2.4's citer stamps wired into `baseline accept --substantive`;
  - R11.3, the sweep;
  - R12.2 for these, R12.3's replay, R12.4 and R12.7.

  Not in this stage:
  - Stage 3: `packets`, `quotes`, the skill and the verifier, and fixing any cited file, including the three known drifts;
  - Stage 4: `notice.sh`, the citation carrier for `.claude/settings.json`;
  - Stage 5: probes.

  The sweep stamps; it never edits a file's content to match the guide.
- **Order.** Task 1 (spec amendments), then:
  - Tasks 2–5 (the citation layer, one module boundary each);
  - Task 6 (the conformance import fix), which must land before the sweep cites `CLAUDE.md`;
  - Task 7 (the seventh commit lint), which must land before the sweep so the pre-commit hook lints its commits;
  - Task 8 (the sweep);
  - Task 9 (validation).

  Each task's tests run with every earlier task in place.
- **Worktree.** Before creating it, run `git -C /Users/lowell/Projects/agent-skills fetch --prune`, then `git -C /Users/lowell/Projects/agent-skills log --oneline -3 origin/main`, and confirm `origin/main` holds this plan's merge.
  - Create the worktree with `git -C /Users/lowell/Projects/agent-skills worktree add .claude/worktrees/plan-43-cc-drift-stage2 -b feat/cc-drift-stage2 origin/main`. `.claude/worktrees/` is gitignored. Commit only from the worktree, as `git -C <W> commit …`.
  - Before every commit, run `git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2 branch --show-current` and confirm it prints `feat/cc-drift-stage2`.
  - The repo sets `core.hooksPath=build/githooks`, so every commit runs `build/run_commit_lints.sh` (six lints, seven from Task 7, about 40 s). A refused commit is a finding: fix the cause, never pass `--no-verify`.
  - Scratch files live under W's gitignored `.sdd/43-claude-code-drift-automation/` and are never committed. Deviations go in the SDD ledger there as they happen. They reach this plan as `> Deviation:` notes only at the completion markup.
  - Each commit ends with the executing session's own Co-Authored-By trailer, which subagent-authored commits keep too. After each subagent commit, check `git -C <W> log -1 --format=%B` and amend the trailer if the implementer wrote its own.
- **Baseline and counts.** Before Task 1, run the three suites in W and record their counts in the SDD ledger:
  - `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2/build --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q -rf`
  - `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2/build/cc_guide --python 3.13 --with pytest python -m pytest -q`
  - `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2/hooks --python 3.13 --with pytest python -m pytest -q`
  - A worktree lacks the gitignored `build/.scratch/`, so four tests in `test_verify_citations.py` fail there and stay failing throughout: `test_true_negative_flags_bad_refs`, `test_empty_text_has_no_failures`, `test_chapter_fallback_passes_gate_a_but_is_flagged` and `test_known_good_fallback_is_not_flagged`. They are not this plan's to fix.
  - Every expected change below is a **+N delta over the baseline you record**. This plan adds **+59 tests** to the build directory. Of those, +54 are in `build/cc_guide/` (Tasks 2–5); the other five are `test_check_conformance.py` +1 (Task 6), `test_commit_lints.py` +1 (Task 7) and `test_check_frontmatter.py` +3 (Task 8). `hooks/` gains none.
- **Test-first.** Each task writes its tests first, runs them, and reconciles the run against the step's prediction before writing code: the counts, and each failure's cause.
  - The predictions were observed by replaying this plan's edit blocks, task by task, against a clean checkout of `b5a209d` while the plan was written.
  - A test that passes at its RED step is a plan defect: fix the assertion so it fails for the stated reason, and report the deviation. Task 8 names its two exceptions, which pin existing behaviour that R12.4 requires to stay unchanged.
- **Test conventions** (Stage 1's, unchanged).
  - Run the cc_guide suite from inside `build/cc_guide/` (here, `uv run --directory`).
  - Bare imports, no `__init__.py`. Test files import modules by name and reach names through them.
  - Fixtures are hand-written in `cc_fixtures.py`, never copied from docs text.
  - Every cc_guide test file imports `isolated_home` from `cc_fixtures` (with `# noqa: F401`).
  - Fixture repos go through `cc_fixtures.git`. Messages are compared with exact equality.
- **No citation-shaped lines in sources (R5).** No line of any tracked file outside `specs/`, `runtimes/` and `review/` may begin, after indentation, with `#` or `<!--` followed by `cc-guide:`, unless it is a real citation where R4.1 puts it. Test data therefore lives inside quotes: a list item `'# cc-guide: …',` starts with a quote. Where a string must begin a line, build it as `'#' + ' cc-guide: …'`. Never use triple-quoted multi-line test data that contains one.
- **Python style** (`CLAUDE.md`, `rules/clean-code-python.md`). Single quotes, `'''` docstrings, 4-space indent, Python 3.13, stdlib only inside `build/cc_guide/`.
- **CLI contract** (Stage 1's). `uv run --python 3.13 python build/cc_guide/cli.py <subcommand>` finds the repo from its own location. Exit 0 is clean or nothing due; 1 is violations or something due; 2 is an error (`cc-guide: <message>` on stderr for a `SetupError`, a traceback otherwise).
- **Inputs (R6.1).** The citation scan reads at the same `Source` as the guide, manifest and baseline: the working tree for `lint` (or `--ref`) and for `baseline`, and `main` for `check` (or `--ref` / `--worktree`). It reads tracked files only (`git grep`), outside R4.2's excluded trees and the guide.
- **Writes.** `cite` writes only the files it names, each checked before any is written. `lint` and `check` write nothing in the repo. Nothing commits.
- **Unchanged gates (R12.4).** The logic of `check_frontmatter.py`, the dependency-drift test and `sync_runtime_assets.py` stays unchanged. `check_frontmatter.py` gains only its citation line (Task 8), and `sync_runtime_assets.py --check` must report no adapter change.
- **Portability coupling.** The portability spec's R1.4 has not landed: no superpowers `SKILL.md` carries `metadata` at `b5a209d`, and no `codex/*` or portability branch exists. When it lands, its `metadata` block goes above the citation, which stays the frontmatter's last line. Whichever branch merges second reconciles that.
- **Never commit docs text.** No step copies text from `~/.cache/agent-skills/cc-guide/`.
- **Nothing outward-facing.** No push, PR, issue or post during execution. The only network use is Task 9's live `check --worktree` (R6.4's fetch).
- **Leave alone:**
  - the spec's status line;
  - the content of every cited file apart from its new citation line, including the three known drifts (`Grep, Glob` in the agents, `hooks/ruff-check.sh`'s `stop_hook_active` branch, `hooks/README.md`'s unquoted `$CLAUDE_PROJECT_DIR`);
  - the findings listed under "Drift the sweep found";
  - `.claude/settings.json`.

  All are Stage 3's or the owner's.
- **Anchor on text, not line numbers.** Line numbers are as of `b5a209d`. Every edit gives its exact old text. Never regress an existing test.

## Decisions

- **D1** (owner, planning, 2026-10-12): a rules file with frontmatter (`rules/*.md`) cites like a skill: a `# cc-guide:` YAML comment as the frontmatter's last line. R4.1's first row widens to Markdown with frontmatter. The tracked symlink `.claude/rules/clean-code-python.md` is git's link text, so the scan reads the rule once. Applied in: Task 1 (spec amendment), Task 2, Task 8.
- **D2** (owner, planning, 2026-10-12): a skill's `SKILL.md` citation covers its `references/`, which carry none of their own. Its scripts carry their own line. Applied in: Task 1 (spec amendment), Task 8.
- **D3** (owner, planning, 2026-10-12): `cli.py lint` joins the commit lints as the seventh, so the pre-commit hook and CI enforce citation placement. Applied in: Task 1 (spec amendment), Task 7.
- **D4** (owner, plan review, 2026-10-12): D2 widens from `references/` to every Markdown file a skill loads on demand, in `references/` or beside `SKILL.md`, after the Codex review found Claude Code facts in `requesting-code-review/code-reviewer.md` and SDD's prompt templates. `requesting-code-review`'s citation gains `subagents.models` for `code-reviewer.md`. Applied in: Task 1 (spec amendment), Task 8.

---

## Planning record

### R4.5 load check (run 2026-10-12, before planning the sweep)

All three runtimes were run from a tmpdir outside any repo, against two workspace-scoped probe skills with a folded `description: >`.
- `ccprobe-cited` carried `# cc-guide: skills.frontmatter @2.1.288` as its last frontmatter line.
- `ccprobe-plain` was the control.

Results:
- **Claude Code 2.1.296** (`claude -p --model sonnet`): both skills appeared in `skills` and `slash_commands`; `/ccprobe-cited` answered `ZEBRA-CITED-OK`; both descriptions were quoted unfolded, with no comment text.
- **Codex 0.162.1** (`codex debug prompt-input`): both skills listed, descriptions unfolded, no comment text.
- **Gemini 0.46.0** (`gemini skills list --all`, with `GEMINI_CLI_TRUST_WORKSPACE=true` for that run only): both `[Enabled]`, descriptions unfolded, no comment text.

**PASS in all three.** No user-level skills directory or trust file was written. The evidence is in `~/.cache/agent-skills/cc-guide/load-check/` (`2026-10-12-README.txt` and five artifacts). Decision 3 (comments, not `metadata`) stands.

### CLAUDE.md import probe (run 2026-10-12)

The trial sweep made `check_conformance.py` fail with `CLAUDE.md line 1: import @2.1.219 does not resolve`. Its `claude-md-import-resolves` check read the citation's stamp as an `@path` import.

Claude Code 2.1.296 was probed with two non-repo tmpdirs, each holding a `marker.md` with a secret word:
- **comment arm:** `<!-- cc-guide: skills.locations @marker.md -->` on line 1 → `NONE`, not imported;
- **control arm:** `@marker.md` on its own line → the word, imported.

So Claude Code expands no import inside a block-level HTML comment. `memory.md` documents only that code spans and fenced blocks are skipped, and that block-level comments are stripped before injection. The ordering is undocumented, so it is listed as a coverage gap. Task 6 teaches the check the same rule (settled default S1). The evidence is in the same directory.

Two follow-up probes ran the same day, recorded in the same README:
- **Gemini 0.46.0** (`GEMINI.md` importing `@./CLAUDE.md`) does expand an `@path` inside an HTML comment: its comment arm imported `marker.md`. It never reads the stamp as an import, though. Its scanner takes an import path only when it starts with `.`, `/` or a letter, and a citation's stamp always starts with a digit. In the real arm, `<!-- cc-guide: skills.locations @2.1.219 -->` reached context verbatim, with no import-failed note.
- **Claude Code, rules files:** a `.claude/rules/` file's frontmatter is stripped before injection, so its citation never reached context. An `@path` in a rules file's body was not expanded either.

### Prototype

Every task was built and run in a throwaway clone of `b5a209d` (`~/.cache/agent-skills/scratch/plan43-proto`). These totals are what that clone saw, a record and not a target; the tasks state deltas, measured against the baseline the execution session records:
- baseline, in a fresh clone of `b5a209d`: the build directory 776 passed, 4 failed and 11 skipped; `build/cc_guide/` 224 passed; `hooks/` 274 passed;
- after all nine tasks: the build directory 835 passed (+59), with the 4 known failures; `build/cc_guide/` 278 passed (+54); `hooks/` 274 on both interpreters; `test_commit_lints.py` 12 passed (+1);
- `build/run_commit_lints.sh`: all seven lints pass after the sweep;
- `cli.py lint`: exit 0 and 41 `STALE` lines.

This plan's code blocks are cut from that clone's files.

### Settled defaults (your human partner reviews each)

- **S1. The conformance import check skips block-level HTML comments.** This is the CLAUDE.md probe above, at Task 6.
  - An inline comment, mid-line, is still read, since the probe covered the block-level case only.
  - The alternative was to leave `CLAUDE.md` uncited. R4.2 names it, and in Claude Code its citation costs no context tokens, since block-level comments are stripped.
  - Gemini reads `CLAUDE.md` through `GEMINI.md`'s import and keeps HTML comments, so there the citation is one inert line of context. It is never an import (follow-up probes above).
- **S2. `build/check_conformance.py` cites 13 sections, not R4.2's three.**
  - R4.2 took the three from conformance R3.6. Since then, plan 35's later checks hard-code ten more sections' facts in the file: Bash rule separators, `stop_hook_active`, `$CLAUDE_PROJECT_DIR`, the `@` import grammar, `disable-model-invocation`, `availableModels` and others.
  - R4.2 says the plan's sweep fixes the exact list.
- **S3. Placement within R4.1:**
  - scripts: directly after the shebang, or on line 1 without one;
  - Markdown without frontmatter: line 1 ("at the top");
  - TOML: line 1;
  - Markdown with frontmatter: the line before the closing `---`.
- **S4. A skill's `README.md` or `INSTALL.md` carries its own HTML citation.** D2 and D4 cover the Markdown a skill loads on demand; nothing loads a README or INSTALL file into context, so neither is covered. This applies to `skills/bayesian-workflow/README.md` and `skills/llm-wiki/INSTALL.md`.
- **S5. NOTICE gains one bullet** in the superpowers changes list. It names the seven superpowers skills and the two superpowers-derived agents that now carry a citation comment, and says no parsed field changed.
  - The sweep also cites two other adapted works: `bayesian-workflow` (its `SKILL.md` and `README.md`) and the clean-code family's `rules/clean-code-python.md`. Their NOTICE entries describe what was adapted and from whom; neither keeps a change-by-change list, which the superpowers section does. A citation comment adds no adapted material, so neither entry gains a bullet.
- **S6. `cite` takes one or more files**, read from the repo root as `lint` and `check` print them. A symlink is stamped at its target. Every file is checked before any is written.
- **S7. The lint reads citation-shaped lines loosely** (`#` or `<!--`, optional spaces, then `cc-guide:`), so near-misses such as `#cc-guide:` are reported rather than skipped.
  - It reports a duplicated ID, and an indented citation gets its own message, since YAML reads one inside a folded scalar as text.
  - In a shell script an HTML-form line is code, so it reads as misplaced.
- **S8. `STALE` lines print on every commit-lint run**: 41 lines until Stage 3's `files` batches clear them, as R5 specifies.
- **S9. R11.4's offline round trip against the 2.1.288 snapshot is no longer a Stage 2 check.** The 2.1.289 bookkeeping (PR #23, `a3336cf`) rebaselined since, so that snapshot now reads as 50 changed and 14 missing blocks. The guide's `2.1.289` is also not a label in that changelog. Task 9 runs a live `check --worktree` instead.

### Plan ID

`entry_check.py` (2026-10-12) reports `next free: 43` and no collisions, and lists `38-claude-code-drift-automation.md` under this spec. No branch other than `main`/`origin/main` existed. The SDD bundle (H26/P2/P3/Q2) was not yet planned, so it takes the next free ID after this one.

### Timing

A-53, Haiku's retirement window opening on 2026-10-15, is due for `/cc-guide verify subagents.models`, which is Stage 3's. Stage 2 plus Stage 3 will not both merge by 2026-10-15. If the date matters, the owner checks A-53 by hand.

### The sweep (R11.3)

Four read-only mapping passes proposed the list: hooks and root files; agents, commands and build tooling; the 13 superpowers skills; the other 24 skills. Each file was then checked against the guide text. The rules:
- Cite only sections whose text states the fact the file relies on.
- Prefer the narrowest section.
- Pre-existing files take `@2.1.219`. The conformance register and its lint take `@2.1.288` (R11.3).
- This stage creates no file that rests on a Claude Code fact.

Every listed file starts stale: no file cites only sections whose `changed` is 2.1.219, and that backlog is the review the refresh skipped (Decision 2).

| File | Cites | Stamp |
|---|---|---|
| `hooks/README.md` | `subagents.frontmatter` `rules.settings` `hooks.events` `hooks.exit-codes` `hooks.configuration` `hooks.patterns` `hooks.pitfalls` | `@2.1.219` |
| `hooks/probe-readonly-guard.sh` | `hooks.exit-codes` `hooks.pitfalls` | `@2.1.219` |
| `hooks/readonly-agent-guard.py` | `hooks.events` `hooks.exit-codes` `hooks.patterns` | `@2.1.219` |
| `hooks/ruff-check.sh` | `hooks.events` `hooks.exit-codes` `hooks.patterns` | `@2.1.219` |
| `hooks/ruff-fix.sh` | `hooks.events` `hooks.patterns` | `@2.1.219` |
| `hooks/uv-guard.sh` | `hooks.events` `hooks.exit-codes` `hooks.patterns` | `@2.1.219` |
| `hooks/test_readonly_agent_guard.py` | `hooks.events` `hooks.exit-codes` `hooks.patterns` | `@2.1.219` |
| `rules/clean-code-python.md` | `rules.rules-files` | `@2.1.219` |
| `CLAUDE.md` | `skills.locations` | `@2.1.219` |
| `README.md` | `skills.locations` `commands.overview` `subagents.overview` `subagents.models` `rules.rules-files` `hooks.events` `hooks.exit-codes` `hooks.configuration` | `@2.1.219` |
| `install.py` | `skills.locations` `commands.overview` `subagents.overview` | `@2.1.219` |
| `agents/code-reviewer.md` | `subagents.frontmatter` `subagents.tools` | `@2.1.219` |
| `agents/debugger.md` | `subagents.frontmatter` `subagents.tools` | `@2.1.219` |
| `agents/docs-writer.md` | `subagents.frontmatter` `subagents.tools` | `@2.1.219` |
| `agents/explore.md` | `subagents.frontmatter` `subagents.tools` `subagents.models` | `@2.1.219` |
| `agents/security-auditor.md` | `subagents.frontmatter` `subagents.tools` | `@2.1.219` |
| `agents/task-reviewer.md` | `subagents.frontmatter` `subagents.tools` | `@2.1.219` |
| `agents/test-runner.md` | `subagents.frontmatter` `subagents.tools` `subagents.models` | `@2.1.219` |
| `commands/deferred.md` | `skills.frontmatter` `commands.overview` | `@2.1.219` |
| `commands/fix-issue.md` | `skills.frontmatter` `commands.overview` | `@2.1.219` |
| `commands/license-audit.md` | `skills.frontmatter` `commands.overview` | `@2.1.219` |
| `build/check_frontmatter.py` | `skills.frontmatter` `commands.overview` `subagents.frontmatter` `subagents.tools` `subagents.models` | `@2.1.219` |
| `build/check_conformance.py` | `skills.frontmatter` `skills.arguments` `commands.overview` `subagents.frontmatter` `subagents.tools` `rules.hierarchy` `rules.rules-files` `rules.settings` `hooks.exit-codes` `hooks.configuration` `hooks.patterns` `hooks.pitfalls` `lean.model-routing` | `@2.1.288` |
| `build/cc_guide/conformance.toml` | all 38 sections, in guide order | `@2.1.288` |
| `skills/brainstorming/SKILL.md` | `lean.session-hygiene` | `@2.1.219` |
| `skills/dispatching-parallel-agents/SKILL.md` | `subagents.frontmatter` `subagents.models` `subagents.isolation` | `@2.1.219` |
| `skills/executing-plans/SKILL.md` | `subagents.frontmatter` | `@2.1.219` |
| `skills/requesting-code-review/SKILL.md` | `subagents.frontmatter` `subagents.models` `subagents.isolation` | `@2.1.219` |
| `skills/subagent-driven-development/SKILL.md` | `subagents.frontmatter` `subagents.models` `subagents.isolation` `lean.session-hygiene` `lean.model-routing` | `@2.1.219` |
| `skills/writing-plans/SKILL.md` | `lean.session-hygiene` `lean.model-routing` | `@2.1.219` |
| `skills/writing-skills/SKILL.md` | `skills.locations` `skills.frontmatter` `skills.description` `skills.listing-budget` `skills.progressive-disclosure` `subagents.isolation` | `@2.1.219` |
| `skills/bayesian-workflow/SKILL.md` | `skills.frontmatter` | `@2.1.219` |
| `skills/bayesian-workflow/README.md` | `skills.locations` | `@2.1.219` |
| `skills/tune-hyperparameters/SKILL.md` | `skills.frontmatter` | `@2.1.219` |
| `skills/tech-debt/SKILL.md` | `skills.frontmatter` `subagents.isolation` | `@2.1.219` |
| `skills/prepare-handoff/SKILL.md` | `subagents.isolation` `rules.auto-memory` `lean.session-hygiene` `lean.model-routing` | `@2.1.219` |
| `skills/derive-roadmap/SKILL.md` | `lean.session-hygiene` | `@2.1.219` |
| `skills/develop-testing-strategy/SKILL.md` | `lean.session-hygiene` `lean.model-routing` | `@2.1.219` |
| `skills/recommend-probabilistic-model/SKILL.md` | `lean.session-hygiene` `lean.model-routing` | `@2.1.219` |
| `skills/track-model-experiments/SKILL.md` | `lean.session-hygiene` | `@2.1.219` |
| `skills/llm-wiki/INSTALL.md` | `skills.locations` | `@2.1.219` |

Considered and not cited:
- `AGENTS.md`, `GEMINI.md` and `build/CLAUDE.md`;
- `build/sync_runtime_assets.py`, `build/test_runtime_support.py`, `build/run_commit_lints.sh`, `build/githooks/pre-commit`, `build/check_provenance.py` and `build/check_snippets.py`;
- every `build/cc_guide/` tool module and `manifest.toml` (docs-site format, not Claude Code behaviour);
- `.claude/settings.json`, which has no carrier until Stage 4's `notice.sh` (R4.2);
- `hooks/.gitkeep`;
- the skills `receiving-code-review`, `systematic-debugging`, `test-driven-development`, `verification-before-completion`, `finishing-a-development-branch` and `using-git-worktrees` (the last two rest only on uncovered facts);
- the domain skills;
- `llm-wiki`'s `SKILL.md` and scripts, which rest only on the session-transcript format, a coverage gap.

### Coverage gaps (R4.3; Task 9 lists them in the completion notes for the owner)

Facts the cited files rely on that no guide section states:
1. `agent_type` (and `agent_id`) in PreToolUse payloads, and that it equals the frontmatter `name`, case-sensitively. Files: `hooks/readonly-agent-guard.py`, its tests, `hooks/README.md`.
2. `claude -p` mechanics. Files: `hooks/probe-readonly-guard.sh`, `hooks/README.md`, `CLAUDE.md`.
   - the stdin wait;
   - variadic `--allowedTools`;
   - `--agent` populating `agent_type`;
   - stream-json carrying the denial.
3. The launchd PATH for hooks (`/usr/bin:/bin:/usr/sbin:/sbin`, system Python 3.9). Files: the guard, its tests, `hooks/README.md`, `CLAUDE.md`.
4. The capitalised `Explore` shadowing rule: agent types resolve by frontmatter `name` alone. Files: `agents/explore.md`, `build/check_frontmatter.py`.
5. The Bash tool's shell environment (zsh, snapshot aliasing). Files: the guard and its tests.
6. Deny-output keys beyond `permissionDecision`, and other payload keys. File: the guard's tests.
7. A hook without its execute bit fails open. Files: `hooks/README.md`, `build/check_conformance.py`.
8. Symlinked agents and commands load, and `~/.claude/commands/` is the personal command location. Files: `install.py`, `README.md`.
9. The `/skills` command. File: `README.md`.
10. The session-transcript format and location. Files: `llm-wiki`'s scripts, `SKILL.md`, `INSTALL.md`.
11. `xhigh` as an effort level. Files: `bayesian-workflow`, `tune-hyperparameters`, two agents.
12. Session models. Files: `writing-plans`, `prepare-handoff`, `develop-testing-strategy`, `recommend-probabilistic-model`.
    - what model a cleared or fresh session runs on;
    - `/model` saving a default;
    - `/clear` keeping the model.
13. An initial prompt as a positional argument (`claude --model <m> "$(cat file)"`). File: `prepare-handoff`.
14. A non-interactive or subagent run cannot ask questions. File: `derive-roadmap`.
15. `<this-skill-dir>`: Claude Code surfaces the skill's base directory on invocation. Files: several skills.
16. Same-response multi-dispatch runs concurrently. Files: `dispatching-parallel-agents`, `executing-plans`, `subagent-driven-development`.
17. Subagent dispatch. Files: `subagent-driven-development`, `requesting-code-review`, `writing-skills`.
    - per-spawn `model` accepts aliases only;
    - per-spawn effort;
    - resuming a finished subagent;
    - nested dispatch.
18. Bash `run_in_background` and its notification, and detached processes surviving between calls. Files: `requesting-code-review` (`codex-review.md`), `brainstorming` (`visual-companion.md`).
19. Worktree and session mechanics. Files: `using-git-worktrees`, `finishing-a-development-branch`, `requesting-code-review`, `subagent-driven-development`.
    - worktree isolation refusing variable-built commands;
    - `EnterWorktree` and `ExitWorktree`;
    - `.git/` as a protected path;
    - shell state not persisting.
20. `@path` inside a skill body force-loads a file. File: `writing-skills`.
21. The valid `tools:` names. Files: `build/check_frontmatter.py`, `build/sync_runtime_assets.py`.
22. A subagent's `model: haiku` is not dropped under auto mode. Files: `build/check_frontmatter.py`, two agents.
23. Claude Code expands no `@` import inside a block-level HTML comment (the probe above). Files: `build/check_conformance.py`, `CLAUDE.md`.

### Drift the sweep found (for Stage 3's `files` batches; not fixed here)

Every one sits in a file the sweep stamps stale, so Stage 3's `files` batches review it, except the `.claude/settings.json` item, which is uncited until Stage 4:
- `README.md:147` says "Only exit 2 blocks a tool call", but a JSON deny also blocks (`hooks.exit-codes`).
- `README.md:164` calls user-level `~/.claude/rules/` "version-dependent"; the guide states it as supported (`rules.rules-files`).
- `.claude/settings.json:4` sets `enforceAvailableModels` in project settings, while the guide places it in managed settings (`lean.model-routing`).
- `skills/dispatching-parallel-agents/SKILL.md:76,86`: "one dispatch per response = sequential" contradicts the guide's background spawns (`subagents.frontmatter`).
- `skills/develop-testing-strategy/SKILL.md:250-254` and `skills/recommend-probabilistic-model/SKILL.md:72-77` say the next session runs on the model default, but `/clear` keeps the current model (gap 12).
- `skills/subagent-driven-development/SKILL.md` runs to about 6–8k tokens, and a compacted session re-attaches only the first 5,000 tokens of an invoked skill (`skills.progressive-disclosure`, `lean.session-hygiene`). Its recovery sections sit past that cutoff. This bears on the SDD bundle's H26 trim.

### CLAUDE.md line budget

184 lines at `b5a209d`. Task 3 rewrites two comment lines as three (+1), and Task 7 rewrites the four commit-lint comment lines in place (+0). Task 8's citation adds one line, so **186** after this plan, under the 190 that plan 38 set as each stage's ceiling.

---

### Task 1: Spec amendments (D1–D4)

**Files:**
- Modify: `specs/claude-code-drift-automation-spec.md` (R4.1, R5, Out of scope)

Each edit is tagged `(owner, plan 43, 2026-10-12)`; the status line stays untouched.

- [x] **Step 1: Widen R4.1's first row (D1)**

**Edit** `specs/claude-code-drift-automation-spec.md` — replace:

```text
| `SKILL.md`, `agents/*.md`, `commands/*.md`, `.claude/skills/*/SKILL.md`, `.claude/agents/*.md` | `# cc-guide: …` as a YAML comment, the last line inside the frontmatter |
```

with:

```text
| Markdown with frontmatter: `SKILL.md`, `agents/*.md`, `commands/*.md`, `rules/*.md`, `.claude/skills/*/SKILL.md`, `.claude/agents/*.md` (owner, plan 43, 2026-10-12) | `# cc-guide: …` as a YAML comment at column 0, the last line inside the frontmatter |
```

- [x] **Step 2: Say what a skill's citation covers (D2, D4)**

**Edit** `specs/claude-code-drift-automation-spec.md` — replace:

```text
Citations never go in a skill or agent body: bodies reach Codex and Gemini
verbatim and cost tokens on every load.
```

with:

```text
Citations never go in a skill or agent body: bodies reach Codex and Gemini
verbatim and cost tokens on every load. A skill's `SKILL.md` citation covers
the Markdown files it loads on demand, in `references/` or beside it, which
load the same way and carry none of their own, while its scripts carry their
own (owner, plan 43, 2026-10-12).
```

- [x] **Step 3: The lint joins the commit lints (D3)**

**Edit** `specs/claude-code-drift-automation-spec.md` — replace:

```text
Commands section gains the invocation, to run before committing a change to
the guide or to any file carrying a citation.
```

with:

```text
Commands section gains the invocation, to run before committing a change to
the guide or to any file carrying a citation. `build/run_commit_lints.sh`
runs it as the seventh commit lint, so the pre-commit hook and CI enforce it
(owner, plan 43, 2026-10-12).
```

- [x] **Step 4: Correct the out-of-scope note on CI (D3)**

**Edit** `specs/claude-code-drift-automation-spec.md` — replace:

```text
- Anything automatic and outward-facing (commits, PRs, issues), and CI, which
  the repo does not have.
```

with:

```text
- Anything automatic and outward-facing (commits, PRs, issues). Plan 41 added
  CI, which runs `lint` among the commit lints; `check`, which fetches, never
  runs there (owner, plan 43, 2026-10-12).
```

- [x] **Step 5: Commit**

> Deviation: every commit in this run ends with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`, the executing session's model, not the `Claude Opus 5.5` the commit blocks show (Global Constraints, trailer rule).

Confirm the branch (Global Constraints), then:

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2 add specs/claude-code-drift-automation-spec.md
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2 commit -m "docs(specs): drift Stage 2 amendments for rules files, skill references and the seventh commit lint" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: The citation parser (`guide.py`, R4.1)

**Files:**
- Create: `build/cc_guide/test_citations.py`
- Modify: `build/cc_guide/guide.py` (module docstring and imports; append the citation layer)

**Interfaces:**
- Produces:
  - `guide.Citation(path: str, line: int, ids: tuple[str, ...], stamp: str)`;
  - `guide.CITE_SHAPED_RE`, `guide.HASH_FORM` and `guide.HTML_FORM`;
  - `guide.file_citation(path: str, text: str) -> tuple[Citation | None, list[str]]`;
  - `guide.read_citations(files: dict[str, str]) -> tuple[list[Citation], list[str]]`;
  - `guide.by_section(citations) -> dict[str, list[Citation]]`.
  - Problem messages begin `<path>:<line>: `.

- [x] **Step 1: Write the failing tests**

**Create** `build/cc_guide/test_citations.py`:

```python
'''Tests for guide.py's citations: R4.1's forms and placements, and how R5
reads citation-shaped lines (drift spec R4, R5). No line here begins with a
citation: test data sits inside quotes.'''
import pytest

import guide
from cc_fixtures import isolated_home  # noqa: F401

IDS = ('hooks.patterns', 'hooks.pitfalls')
HASH = '# cc-guide: hooks.patterns hooks.pitfalls @2.1.219'
HTML = '<!-- cc-guide: hooks.patterns hooks.pitfalls @2.1.219 -->'
FRONT = 'the last line inside the frontmatter'
CODE = 'a line before the first line of code'
PY = 'a line before the first line of code, outside the docstring and any PEP 723 block'


def read(path, *lines):
    return guide.file_citation(path, '\n'.join(lines))


def cited(path, line):
    return guide.Citation(path, line, IDS, '2.1.219'), []


def misplaced(path, line, place):
    return None, [f'{path}:{line}: a citation goes on {place} (R4.1)']


@pytest.mark.parametrize('path', ['skills/demo/SKILL.md', 'agents/demo.md', 'commands/demo.md',
                                  'rules/demo.md', '.claude/skills/demo/SKILL.md', '.claude/agents/demo.md'])
def test_markdown_with_frontmatter_cites_on_its_last_frontmatter_line(path):
    assert read(path, '---', 'name: demo', 'description: >', '  Use when testing.', HASH, '---', '',
                'Body.') == cited(path, 5)


def test_a_frontmatter_citation_anywhere_else_is_misplaced():
    path = 'skills/demo/SKILL.md'
    assert read(path, '---', HASH, 'name: demo', '---', 'Body.') == misplaced(path, 2, FRONT)
    assert read(path, '---', 'name: demo', '---', HASH) == misplaced(path, 4, FRONT)


def test_an_indented_citation_is_refused_since_yaml_would_read_it_as_text():
    path = 'skills/demo/SKILL.md'
    assert read(path, '---', 'description: >', '  Use when testing.', '  ' + HASH, '---') == (
        None, [f'{path}:4: an indented citation; it starts at column 0'])


def test_markdown_without_frontmatter_cites_on_its_first_line_in_the_html_form():
    assert read('CLAUDE.md', HTML, '', '# CLAUDE.md') == cited('CLAUDE.md', 1)
    assert read('hooks/README.md', '# Hooks', '', HTML) == misplaced('hooks/README.md', 3, 'the first line')
    assert read('README.md', HASH, '# Readme') == (
        None, [f'README.md:1: malformed citation; the form is {guide.HTML_FORM}'])


def test_python_cites_before_its_first_line_of_code_outside_docstring_and_pep723():
    path = 'hooks/demo.py'
    assert read(path, '#!/usr/bin/env python3', '# A comment.', HASH, "'''Doc.'''", 'import os') == cited(path, 3)
    assert read(path, "'''Doc.", 'More doc.', "'''", HASH, '', 'import os') == cited(path, 4)
    assert read(path, '# /// script', '# dependencies = []', '# ///', HASH, 'import os') == cited(path, 4)
    assert read(path, '# /// script', HASH, '# ///', 'import os') == misplaced(path, 2, PY)
    assert read(path, 'import os', HASH) == misplaced(path, 2, PY)
    assert read(path, "'''Doc.", HASH, "'''", 'import os') == misplaced(path, 2, PY)
    assert read(path, '@decorate', HASH, 'def f():', '    pass') == misplaced(path, 2, PY)


def test_a_python_file_that_does_not_parse_carries_no_citation():
    assert read('hooks/demo.py', HASH, 'def (') == (
        None, ['hooks/demo.py:1: no citation can go here: does not parse as Python (invalid syntax)'])


def test_shell_and_toml_cite_before_their_first_command_or_key():
    assert read('hooks/demo.sh', '#!/bin/sh', '# Gate.', HASH, 'set -e') == cited('hooks/demo.sh', 3)
    assert read('hooks/demo.sh', '#!/bin/sh', 'set -e', HASH) == misplaced('hooks/demo.sh', 3, CODE)
    assert read('build/githooks/pre-commit', '#!/usr/bin/env bash', HASH, 'exit 0') == cited(
        'build/githooks/pre-commit', 2)
    assert read('build/demo.toml', '# Register.', '', HASH, '[guide]') == cited('build/demo.toml', 3)
    assert read('build/demo.toml', '[guide]', HASH) == misplaced('build/demo.toml', 2,
                                                                 'a line before the first key or table')


def test_a_file_r41_has_no_slot_for_carries_no_citation():
    assert read('notes.txt', HASH) == (
        None, ['notes.txt:1: no citation can go here: R4.1 gives this kind of file no citation'])
    assert read('skills/demo/SKILL.md', '---', 'name: demo', HASH) == (
        None, ['skills/demo/SKILL.md:3: no citation can go here: its frontmatter never closes'])


def test_a_file_carries_one_citation():
    assert read('hooks/demo.sh', '#!/bin/sh', HASH, HASH, 'exit 0') == (
        None, ['hooks/demo.sh:3: a second citation; a file carries one'])


@pytest.mark.parametrize('line', [
    '# cc-guide: hooks.patterns',
    '# cc-guide: Hooks.patterns @2.1.219',
    '# cc-guide: hooks @2.1.219',
    '#cc-guide: hooks.patterns @2.1.219',
    '# cc-guide: hooks.patterns @latest',
    '# cc-guide: hooks.patterns, hooks.pitfalls @2.1.219',
])
def test_a_malformed_citation_names_the_form(line):
    assert read('hooks/demo.sh', '#!/bin/sh', line, 'exit 0') == (
        None, [f'hooks/demo.sh:2: malformed citation; the form is {guide.HASH_FORM}'])


def test_an_html_citation_in_a_script_is_code_so_it_is_misplaced():
    assert read('hooks/demo.sh', '#!/bin/sh', HTML, 'exit 0') == misplaced('hooks/demo.sh', 2, CODE)


def test_a_section_cited_twice_is_a_problem():
    assert read('hooks/demo.sh', '# cc-guide: hooks.patterns hooks.patterns @2.1.219') == (
        None, ['hooks/demo.sh:1: cites hooks.patterns twice'])


def test_a_four_part_stamp_is_a_well_formed_citation():
    citation, problems = read('hooks/demo.sh', '# cc-guide: hooks.patterns @2.1.288.1')
    assert (citation.stamp, problems) == ('2.1.288.1', [])


@pytest.mark.parametrize('line, shaped', [
    ('# cc-guide: x', True), ('  # cc-guide: x', True), ('\t#cc-guide:', True), ('<!--cc-guide: x', True),
    ('<!-- cc-guide:stamp -->', True), ('<!-- /cc-guide:stamp -->', False), ('x  # cc-guide: x', False),
    ("'# cc-guide: x',", False), ('## cc-guide: x', False),
])
def test_a_citation_shaped_line_is_read_only_at_line_start(line, shaped):
    assert bool(guide.CITE_SHAPED_RE.match(line)) is shaped


def test_read_citations_runs_in_path_order_and_by_section_groups_them():
    files = {'hooks/b.sh': '# cc-guide: hooks.patterns @2.1.219\n',
             'hooks/a.sh': '# cc-guide: hooks.pitfalls hooks.patterns @2.1.288\n',
             'hooks/c.sh': 'exit 0\n# cc-guide: hooks.patterns @2.1.219\n'}
    citations, problems = guide.read_citations(files)
    assert [c.path for c in citations] == ['hooks/a.sh', 'hooks/b.sh']
    assert problems == [f'hooks/c.sh:2: a citation goes on {CODE} (R4.1)']
    assert {sid: [c.path for c in cs] for sid, cs in guide.by_section(citations).items()} == {
        'hooks.pitfalls': ['hooks/a.sh'], 'hooks.patterns': ['hooks/a.sh', 'hooks/b.sh']}
```

- [x] **Step 2: Run them; expect 33 failures**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2/build/cc_guide --python 3.13 --with pytest python -m pytest -q test_citations.py`
Expected: `33 failed`, each an `AttributeError: module 'guide' has no attribute …` (`file_citation`, `CITE_SHAPED_RE`, `read_citations` or `HASH_FORM`).

- [x] **Step 3: Implement**

> Deviation: the final review tightened the stamp pattern to R2.4's three or four numeric parts (54b81f2, with tests): `@3.0` had parsed clean and would have raised `IndexError` in `accept --substantive`.

**Edit** `build/cc_guide/guide.py` — replace:

```python
'''The guide: its anchored sections, their text hashes and terms, and the
stamp region (drift spec R1, R2.3, R3.6).'''
import hashlib
import re
from typing import NamedTuple
```

with:

```python
'''The guide: its anchored sections, their text hashes and terms, the stamp
region, and the citations that point at its sections (drift spec R1, R2.3,
R3.6, R4).'''
import ast
import hashlib
import re
import warnings
from typing import NamedTuple
```

**Append** to `build/cc_guide/guide.py`:

```python
# R5's citation-shaped line: after indentation, `#` or `<!--`, then
# `cc-guide:`. Looser than R4.1's two forms, so a near-miss is still read.
CITE_SHAPED_RE = re.compile(r'^[ \t]*(?:#|<!--)[ \t]*cc-guide:')
CITE_BODY = rf'cc-guide: (?P<ids>{ID_RE.pattern}(?: {ID_RE.pattern})*) @(?P<stamp>[0-9]+(?:\.[0-9]+)+)'
HASH_CITE_RE = re.compile(rf'# {CITE_BODY}')
HTML_CITE_RE = re.compile(rf'<!-- {CITE_BODY} -->')
HASH_FORM = '`# cc-guide: <id> [<id> …] @<version>`'
HTML_FORM = '`<!-- cc-guide: <id> [<id> …] @<version> -->`'
FRONTMATTER = '---'
PEP723_OPEN, PEP723_CLOSE = '# /// script', '# ///'


class Citation(NamedTuple):
    path: str              # repo-relative
    line: int              # 1-based
    ids: tuple[str, ...]   # as written
    stamp: str             # the release the file was last reviewed against


class Slot(NamedTuple):
    '''Where R4.1 lets one file carry its citation.'''
    lines: frozenset[int]  # 0-based lines the citation may sit on
    form: re.Pattern       # HASH_CITE_RE or HTML_CITE_RE
    shape: str             # the form, as messages print it
    place: str             # the rule, as messages print it


def first_code(lines: list[str]) -> int:
    '''The first line that is neither blank nor a `#` comment, or len(lines).'''
    return next((i for i, line in enumerate(lines)
                 if line.strip() and not line.lstrip().startswith('#')), len(lines))


def pep723_lines(lines: list[str]) -> set[int]:
    '''The lines of each PEP 723 block, markers included; an unclosed one
    runs to the end.'''
    out: set[int] = set()
    start = None
    for i, line in enumerate(lines):
        if start is None and line.rstrip() == PEP723_OPEN:
            start = i
        elif start is not None and line.rstrip() == PEP723_CLOSE:
            out.update(range(start, i + 1))
            start = None
    if start is not None:
        out.update(range(start, len(lines)))
    return out


def python_lines(lines: list[str]) -> frozenset[int] | str:
    '''The lines before a Python file's first line of code, less its module
    docstring and any PEP 723 block; or why the file cannot be read.'''
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', SyntaxWarning)
            body = ast.parse('\n'.join(lines)).body
    except SyntaxError as exc:
        return f'does not parse as Python ({exc.msg})'
    doc = range(0)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
            and isinstance(body[0].value.value, str):
        doc = range(body[0].lineno - 1, body[0].end_lineno)
        body = body[1:]
    first = len(lines)
    if body:
        first = min([body[0].lineno] + [d.lineno for d in getattr(body[0], 'decorator_list', [])]) - 1
    block = pep723_lines(lines)
    return frozenset(i for i in range(first) if i not in doc and i not in block)


def citation_slot(path: str, lines: list[str]) -> Slot | str:
    '''R4.1's placement for the file at path, or why it can carry no
    citation. Markdown with frontmatter (skills, agents, commands, rules)
    takes a YAML comment as the frontmatter's last line; other Markdown an
    HTML comment on its first line; TOML, shell and Python a `#` line before
    the first key or line of code.'''
    name = path.rsplit('/', 1)[-1]
    if name.endswith('.md'):
        if lines[0] != FRONTMATTER:
            return Slot(frozenset({0}), HTML_CITE_RE, HTML_FORM, 'the first line')
        close = next((i for i in range(1, len(lines)) if lines[i] == FRONTMATTER), None)
        if close is None:
            return 'its frontmatter never closes'
        return Slot(frozenset({close - 1} - {0}), HASH_CITE_RE, HASH_FORM, 'the last line inside the frontmatter')
    if name.endswith('.toml'):
        return Slot(frozenset(range(first_code(lines))), HASH_CITE_RE, HASH_FORM, 'a line before the first key or table')
    if name.endswith('.py'):
        found = python_lines(lines)
        if isinstance(found, str):
            return found
        return Slot(found, HASH_CITE_RE, HASH_FORM,
                    'a line before the first line of code, outside the docstring and any PEP 723 block')
    if name.endswith('.sh') or lines[0].startswith('#!'):
        return Slot(frozenset(range(first_code(lines))), HASH_CITE_RE, HASH_FORM, 'a line before the first line of code')
    return 'R4.1 gives this kind of file no citation'


def file_citation(path: str, text: str) -> tuple[Citation | None, list[str]]:
    '''R4.1 and R5 for one file: its citation, and every problem with its
    citation-shaped lines. The citation is None unless the file has exactly
    one such line, well-formed, at column 0, where R4.1 puts it.'''
    lines = text.split('\n')
    shaped = [i for i, line in enumerate(lines) if CITE_SHAPED_RE.match(line)]
    if not shaped:
        return None, []
    slot = citation_slot(path, lines)
    problems = [f'{path}:{i + 1}: a second citation; a file carries one' for i in shaped[1:]]
    i = shaped[0]
    where = f'{path}:{i + 1}'
    if isinstance(slot, str):
        return None, [f'{where}: no citation can go here: {slot}'] + problems
    if i not in slot.lines:
        return None, [f'{where}: a citation goes on {slot.place} (R4.1)'] + problems
    match = slot.form.fullmatch(lines[i])
    if match is None:
        indented = slot.form.fullmatch(lines[i].strip()) is not None
        return None, [f'{where}: an indented citation; it starts at column 0' if indented
                      else f'{where}: malformed citation; the form is {slot.shape}'] + problems
    ids = tuple(match['ids'].split(' '))
    twice = sorted({sid for sid in ids if ids.count(sid) > 1})
    if twice:
        problems.insert(0, f"{where}: cites {', '.join(twice)} twice")
    if problems:
        return None, problems
    return Citation(path, i + 1, ids, match['stamp']), []


def read_citations(files: dict[str, str]) -> tuple[list[Citation], list[str]]:
    '''Each file's citation and problems (R4.1, R5), in path order.'''
    citations: list[Citation] = []
    problems: list[str] = []
    for path in sorted(files):
        citation, found = file_citation(path, files[path])
        problems += found
        if citation is not None:
            citations.append(citation)
    return citations, problems


def by_section(citations: list[Citation]) -> dict[str, list[Citation]]:
    '''Each cited section's citations, in the citations' order.'''
    out: dict[str, list[Citation]] = {}
    for citation in citations:
        for sid in citation.ids:
            out.setdefault(sid, []).append(citation)
    return out
```

- [x] **Step 4: Run the suite; expect +33**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2/build/cc_guide --python 3.13 --with pytest python -m pytest -q`
Expected: all pass, 33 more than the recorded baseline.

- [x] **Step 5: Commit**

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2 add build/cc_guide/guide.py build/cc_guide/test_citations.py
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2 commit -m "feat(cc_guide): parse drift citations and their R4.1 placement" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: The citation lint (R5): scan, rules, `STALE`, replay

**Files:**
- Modify: `build/cc_guide/state.py` (constants, `Source.grep`, `citing_files`)
- Modify: `build/cc_guide/lint.py` (citation rules, stale computation, `lint()`'s new `files` argument)
- Modify: `build/cc_guide/check.py` (pass the scan's files to `lint`; Task 4 adds the report)
- Modify: `build/cc_guide/cli.py` (`lint` prints `STALE`; docstring)
- Modify: `build/cc_guide/test_state.py`, `test_lint.py`, `test_cli.py`, `test_baseline.py`
- Modify: `CLAUDE.md` (the drift-detector comment, in place)

**Interfaces:**
- Consumes: Task 2's `guide.file_citation`, `guide.read_citations` and `guide.Citation`.
- Produces:
  - `state.UNCITED` and `state.CITE_SHAPED_ERE`;
  - `state.Source.grep(pattern: str, exclude) -> list[str]`;
  - `state.citing_files(source, guide_path) -> dict[str, str]`;
  - `lint.citation_problems(guide_text, files) -> list[str]`;
  - `lint.stale_citations(citations, state) -> list[tuple[str, list[str]]]`;
  - `lint.stale_lines(citations, state) -> list[str]`;
  - `lint.stale_by_section(citations, state) -> dict[str, list[str]]`;
  - `lint.lint(guide_text, manifest, state, labels, files) -> (violations, notes)`, where `files` is now required.

- [x] **Step 1: Write the failing tests**

> Deviation: the fix wave renamed one test here, `test_a_citation_of_a_section_the_baseline_lacks_is_a_violation_never_stale` to `..._is_never_stale` (f759c79), and changed the label tests to cover the note rule (2c0421f) and its three-part limit (1000221).

**Append** to `build/cc_guide/test_state.py`:

```python
CITE = '# cc-guide: alpha.overview @2.1.900'


def test_citing_files_reads_tracked_files_outside_the_excluded_trees_once(tmp_path):
    '''R4.2 and R5: the scan reads tracked files outside specs/, runtimes/,
    review/ and the guide. A tracked symlink is git's link text, so the file
    it points at is read once, in the working tree and at a ref alike.'''
    repo = fixture_repo(tmp_path / 'repo', {
        'hooks/gate.sh': '#!/bin/sh\n' + CITE + '\nexit 0\n',
        'rules/style.md': '---\npaths: x\n' + CITE + '\n---\n',
        'notes.md': 'No citation here.\n',
        'specs/plan.md': CITE + '\n',
        'runtimes/agent.md': CITE + '\n',
        'review/r.md': CITE + '\n',
        'specs/guides/claude-code-customization-guide.md': '<!-- cc-guide:stamp -->\n',
    })
    (repo / '.claude' / 'rules').mkdir(parents=True)
    (repo / '.claude' / 'rules' / 'style.md').symlink_to('../../rules/style.md')
    git(repo, 'add', '-A')
    git(repo, 'commit', '-qm', 'link the rule')
    (repo / 'hooks' / 'gate.sh').write_text('#!/bin/sh\nexit 0\n' + CITE + '\n')
    (repo / 'hooks' / 'new.sh').write_text(CITE + '\n')
    guide_path = 'specs/guides/claude-code-customization-guide.md'
    tree = state.citing_files(state.Source(repo), guide_path)
    assert sorted(tree) == ['hooks/gate.sh', 'rules/style.md']
    assert tree['hooks/gate.sh'] == '#!/bin/sh\nexit 0\n' + CITE + '\n'
    committed = state.citing_files(state.Source(repo, 'main'), guide_path)
    assert sorted(committed) == ['hooks/gate.sh', 'rules/style.md']
    assert committed['hooks/gate.sh'] == '#!/bin/sh\n' + CITE + '\nexit 0\n'


def test_no_citation_anywhere_reads_no_file(tmp_path):
    repo = fixture_repo(tmp_path / 'repo', {'a.txt': 'text\n'})
    assert state.citing_files(state.Source(repo), 'guide.md') == {}
    assert state.citing_files(state.Source(repo, 'main'), 'guide.md') == {}


def test_the_git_pattern_matches_the_python_pattern(tmp_path):
    '''CITE_SHAPED_ERE is guide.CITE_SHAPED_RE spelled for git grep -E.'''
    import guide
    lines = ['# cc-guide: x', '  # cc-guide: x', '\t#cc-guide:', '<!--cc-guide: x', '<!--  cc-guide: x',
             'x # cc-guide: x', "'# cc-guide: x'", '## cc-guide: x', '<!-- /cc-guide:stamp -->', '#  cc-guide x']
    repo = fixture_repo(tmp_path / 'repo', {f'f{n}.txt': line + '\n' for n, line in enumerate(lines)})
    found = set(state.Source(repo).grep(state.CITE_SHAPED_ERE, ()))
    assert found == {f'f{n}.txt' for n, line in enumerate(lines) if guide.CITE_SHAPED_RE.match(line)}
    assert len(found) == 5


def test_a_git_grep_failure_is_a_setup_error(tmp_path):
    repo = fixture_repo(tmp_path / 'repo', {'a.txt': 'text\n'})
    with pytest.raises(state.SetupError) as err:
        state.Source(repo).grep('(', ())
    assert str(err.value).startswith('git grep in the working tree: ')
```

**Edit** `build/cc_guide/test_lint.py` — replace:

```python
'''Tests for lint.py: every R5 rule but the citation rules (Stage 2's).'''
```

with:

```python
'''Tests for lint.py: every R5 rule, the citation rules included, and STALE.'''
```

**Edit** `build/cc_guide/test_lint.py` — replace:

```python
def run(text, s, labels=LABELS, manifest=MANIFEST):
    return lint.lint(text, manifest, s, labels)
```

with:

```python
def run(text, s, labels=LABELS, manifest=MANIFEST, files=None):
    return lint.lint(text, manifest, s, labels, files or {})
```

**Append** to `build/cc_guide/test_lint.py`:

```python
def test_citation_problems_fail_the_lint_after_the_guide_checks(docs_dir):
    '''R5: every citation parses, cites guide sections, sits where R4.1 puts
    it and appears once per file; each file's problems come together, files
    in path order.'''
    files = {'hooks/b.sh': '#!/bin/sh\nexit 0\n# cc-guide: alpha.overview @2.1.900\n',
             'agents/a.md': '---\nname: a\n# cc-guide: alpha.overview gamma.overview @2.1.900\n---\n'}
    assert run(guide_text(), fixture_state(docs_dir), files=files)[0] == [
        'agents/a.md:3: cites gamma.overview, which is not a guide section',
        'hooks/b.sh:3: a citation goes on a line before the first line of code (R4.1)']


def test_well_placed_citations_lint_clean_and_stale_ones_are_reported_apart(docs_dir):
    '''R5: a stamp below a cited section's `changed` is STALE, which is no
    violation. Stamps compare as versions, so 2.1.900.1 is not stale against
    2.1.900.'''
    s = fixture_state(docs_dir)
    files = {'hooks/old.sh': '# cc-guide: alpha.overview alpha.reference beta.overview @2.1.899\n',
             'hooks/new.sh': '# cc-guide: alpha.overview @2.1.900.1\n',
             'CLAUDE.md': '<!-- cc-guide: beta.reference @2.1.900 -->\n# Notes\n'}
    assert run(guide_text(), s, files=files) == ([], [])
    citations, _ = guide.read_citations(files)
    assert lint.stale_lines(citations, s) == ['STALE hooks/old.sh alpha.overview beta.overview']
    assert lint.stale_by_section(citations, s) == {'alpha.overview': ['hooks/old.sh'],
                                                   'beta.overview': ['hooks/old.sh']}


def test_a_citation_of_a_section_the_baseline_lacks_is_a_violation_never_stale(docs_dir):
    s = fixture_state(docs_dir)
    del s['sections']['beta.reference']
    citations, _ = guide.read_citations({'hooks/a.sh': '# cc-guide: beta.reference @2.1.800\n'})
    assert lint.stale_citations(citations, s) == []
```

**Edit** `build/cc_guide/test_cli.py` — replace:

```python
    assert 'Offline gate over the guide, manifest.toml and baseline.json (R5)' in outs[0]
```

with:

```python
    assert 'Offline gate over the guide, manifest.toml, baseline.json and every' in outs[0]
```

**Append** to `build/cc_guide/test_cli.py`:

```python
def cited(repo, files):
    write_tree(repo, files)
    git(repo, 'add', '-A')
    git(repo, 'commit', '-qm', 'cite the guide')


def test_lint_prints_stale_on_stderr_and_lints_the_citations_at_its_ref(world, capsys):
    '''R5: STALE lines go to stderr and never change the exit; a misplaced
    citation is a violation; --ref reads the committed citations.'''
    repo, cache, _ = world
    cited(repo, {'hooks/gate.sh': '#!/bin/sh\n# cc-guide: alpha.overview alpha.reference @2.1.899\nexit 0\n'})
    assert main(cache, 'lint') == 0
    assert capsys.readouterr() == ('', 'STALE hooks/gate.sh alpha.overview\n')
    write_tree(repo, {'hooks/gate.sh': '#!/bin/sh\nexit 0\n# cc-guide: alpha.overview @2.1.899\n'})
    assert main(cache, 'lint') == 1
    assert capsys.readouterr().out == 'hooks/gate.sh:3: a citation goes on a line before the first line of code (R4.1)\n'
    assert main(cache, 'lint', '--ref', 'main') == 0
```

**Edit** `build/cc_guide/test_baseline.py` — replace:

```python
'''Tests for baseline.py: R2.4's stamp rule, R11.1's derivation, and each
`baseline` subcommand's effect on the state (drift spec R7). The write sets
on disk are test_cli.py's.'''
```

with:

```python
'''Tests for baseline.py: R2.4's stamp rule, R11.1's derivation and R12.3's
replay over it, and each `baseline` subcommand's effect on the state or a
citing file (drift spec R7). The write sets on disk are test_cli.py's.'''
```

**Edit** `build/cc_guide/test_baseline.py` — replace:

```python
import baseline
import blocks
import guide
import state
```

with:

```python
import baseline
import blocks
import guide
import lint
import state
```

**Edit** `build/cc_guide/test_baseline.py` — replace:

```python
def test_init_baselines_each_groups_selected_blocks(docs_dir):
```

with:

```python
def test_the_replay_flags_the_citers_of_drifted_sections_and_not_the_control():
    '''R12.3: with `changed` derived from the real history as R11.1 does,
    fixture citers stamped @2.1.219 of subagents.tools and hooks.patterns
    are stale, and a control citing skills.description is not.'''
    changed = baseline.derive_changed(
        history(baseline.JULY[0]), history(baseline.REFRESH[0]),
        (REPO / 'specs/guides/claude-code-customization-guide.md').read_text(encoding='utf-8'))
    s = {'sections': {sid: {'changed': release} for sid, release in changed.items()}}
    citations, problems = guide.read_citations({
        'agents/replay.md': '---\nname: replay\n# cc-guide: subagents.tools @2.1.219\n---\n',
        'hooks/replay.sh': '#!/bin/sh\n# cc-guide: hooks.patterns @2.1.219\n',
        'skills/control/SKILL.md': '---\nname: control\n# cc-guide: skills.description @2.1.219\n---\n'})
    assert problems == []
    assert lint.stale_citations(citations, s) == [('agents/replay.md', ['subagents.tools']),
                                                   ('hooks/replay.sh', ['hooks.patterns'])]


def test_init_baselines_each_groups_selected_blocks(docs_dir):
```

- [x] **Step 2: Run them; expect 27 failures**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2/build/cc_guide --python 3.13 --with pytest python -m pytest -q`
Expected: `27 failed`. Reconcile by file:
- `test_lint.py` 20:
  - 19 tests that call `run` (17 existing and 2 new) fail with `TypeError: lint() takes 4 positional arguments but 5 were given`;
  - `test_a_citation_of_a_section_the_baseline_lacks…` fails with `AttributeError: module 'lint' has no attribute 'stale_citations'`;
  - the one existing test that never calls `run` passes.
- `test_state.py` 4: `AttributeError` on `state.citing_files`, or on `Source`'s missing `grep`.
- `test_cli.py` 2: the help test's new assertion, and `test_lint_prints_stale…` (no `STALE` on stderr).
- `test_baseline.py` 1: the replay, `AttributeError: module 'lint' has no attribute 'stale_citations'`. Where the history is unavailable it skips instead; record that.

- [x] **Step 3: Implement the scan (`state.py`)**

> Deviation: the final review added `--no-color` to `Source.grep`'s git arguments (216183b, with a forced-colour fixture test): under `color.grep=always` git wrapped file names in ANSI escapes and the commit-gating lint exited 2.

**Edit** `build/cc_guide/state.py` — replace:

```python
MANIFEST = 'build/cc_guide/manifest.toml'
BASELINE = 'build/cc_guide/baseline.json'
PROBES = 'build/cc_guide/PROBES.md'
```

with:

```python
MANIFEST = 'build/cc_guide/manifest.toml'
BASELINE = 'build/cc_guide/baseline.json'
PROBES = 'build/cc_guide/PROBES.md'
# R4.2's excluded trees, which the citation scan never reads.
UNCITED = ('specs', 'runtimes', 'review')
# guide.CITE_SHAPED_RE, spelled for `git grep -E`.
CITE_SHAPED_ERE = '^[[:blank:]]*(#|<!--)[[:blank:]]*cc-guide:'
```

**Edit** `build/cc_guide/state.py` — replace:

```python
    def require(self, path: str) -> str:
        text = self.read(path)
        if text is None:
            raise SetupError(f'{path}: not found in {self.label}')
        return text
```

with:

```python
    def require(self, path: str) -> str:
        text = self.read(path)
        if text is None:
            raise SetupError(f'{path}: not found in {self.label}')
        return text

    def grep(self, pattern: str, exclude) -> list[str]:
        '''The tracked files outside the excluded paths holding a line that
        matches the extended regex pattern, read where this source reads
        (R6.1). Binary files are skipped. A git failure is a SetupError.'''
        args = ['git', 'grep', '-l', '-z', '-I', '-E', '-e', pattern]
        if self.ref is not None:
            args.append(self.ref)
        args += ['--', '.', *(f':(exclude){path}' for path in exclude)]
        proc = subprocess.run(args, cwd=self.repo, capture_output=True)
        if proc.returncode == 1:
            return []
        if proc.returncode != 0:
            raise SetupError(f"git grep in {self.label}: {proc.stderr.decode('utf-8', 'replace').strip()}")
        prefix = '' if self.ref is None else f'{self.ref}:'
        return [name.removeprefix(prefix) for name in proc.stdout.decode('utf-8').split('\0') if name]
```

**Append** to `build/cc_guide/state.py`:

```python
def citing_files(source: Source, guide_path: str) -> dict[str, str]:
    '''The files R5's citation scan reads, path -> text: tracked files
    outside R4.2's excluded trees and the guide that hold a citation-shaped
    line. A tracked symlink is git's link text, so it is never read twice.'''
    return {path: source.require(path) for path in source.grep(CITE_SHAPED_ERE, (*UNCITED, guide_path))}
```

- [x] **Step 4: Implement the rules (`lint.py`)**

> Deviation: owner decision at the completion gate (2026-10-12): the release-label rule treats a three-part label newer than the cached changelog's newest release as a `note:` on stderr, not a violation (2c0421f, limited to three parts in 1000221). Spec R5 still reads as written; amending it is deferred.

**Edit** `build/cc_guide/lint.py` — replace:

```python
'''`lint`: the offline gate over the guide, manifest.toml and baseline.json
(drift spec R5). Its citation rules and STALE lines are Stage 2's.'''
import json
import re

from blocks import CELL_SPLIT_RE, fence_spans, fenced_lines, is_table_start
from guide import NO_STAMP, anchor_problems, render_stamp, sections, stamp_bounds, stamp_content, text_hash
from state import Manifest
```

with:

```python
'''`lint`: the offline gate over the guide, manifest.toml, baseline.json and
the citations that point at the guide (drift spec R5).'''
import json
import re

from blocks import CELL_SPLIT_RE, fence_spans, fenced_lines, is_table_start
from docs import version_key
from guide import (NO_STAMP, Citation, anchor_problems, file_citation, render_stamp, sections, stamp_bounds,
                   stamp_content, text_hash)
from state import Manifest
```

**Edit** `build/cc_guide/lint.py` — replace:

```python
def lint(guide_text: str, manifest: Manifest, state: dict,
         labels: set[str] | None) -> tuple[list[str], list[str]]:
    '''R5 without its citation rules: (violations, notes). `labels` are the
    newest changelog's release labels, None when there is no changelog to
    read, which skips the label check with a note. The caller parses the
    changelog, so a malformed one is a setup error there.'''
    lines = guide_text.split('\n')
    violations = (anchor_problems(guide_text) + id_set_problems(guide_text, manifest, state)
                  + hash_problems(guide_text, state) + stamp_problems(guide_text, state)
                  + (label_problems(lines, labels) if labels is not None else [])
                  + table_problems(lines) + json_problems(lines))
    return violations, [NO_CHANGELOG] if labels is None else []
```

with:

```python
def citation_problems(guide_text: str, files: dict[str, str]) -> list[str]:
    '''R5's citation rules over the files the scan found: each citation
    parses, cites guide sections, sits where R4.1 puts it, and appears once
    per file. In path order, each file's problems together.'''
    ids = {s.id for s in sections(guide_text) if s.id}
    out = []
    for path in sorted(files):
        citation, problems = file_citation(path, files[path])
        out += problems
        if citation is not None:
            out += [f'{path}:{citation.line}: cites {sid}, which is not a guide section'
                    for sid in citation.ids if sid not in ids]
    return out


def stale_citations(citations: list[Citation], state: dict) -> list[tuple[str, list[str]]]:
    '''R5: each citing file whose stamp is below a cited section's
    `changed`, with those sections. A section baseline.json lacks is a lint
    violation, never stale.'''
    out = []
    for c in citations:
        behind = [sid for sid in c.ids if sid in state['sections']
                  and version_key(c.stamp) < version_key(state['sections'][sid]['changed'])]
        if behind:
            out.append((c.path, behind))
    return out


def stale_lines(citations: list[Citation], state: dict) -> list[str]:
    '''R5's `STALE <file> <ids>` lines, which never change the exit code.'''
    return [f"STALE {path} {' '.join(ids)}" for path, ids in stale_citations(citations, state)]


def stale_by_section(citations: list[Citation], state: dict) -> dict[str, list[str]]:
    '''R6.8's stale backlog: each section's stale citing files, sections in
    baseline.json's (the guide's) order.'''
    by: dict[str, list[str]] = {}
    for path, ids in stale_citations(citations, state):
        for sid in ids:
            by.setdefault(sid, []).append(path)
    return {sid: by[sid] for sid in state['sections'] if sid in by}


def lint(guide_text: str, manifest: Manifest, state: dict, labels: set[str] | None,
         files: dict[str, str]) -> tuple[list[str], list[str]]:
    '''R5: (violations, notes). `labels` are the newest changelog's release
    labels, None when there is no changelog to read, which skips the label
    check with a note; the caller parses the changelog, so a malformed one is
    a setup error there. `files` are the citation scan's, path -> text
    (state.citing_files). Stale citations are not violations: callers print
    them (stale_lines) or report them (stale_by_section).'''
    lines = guide_text.split('\n')
    violations = (anchor_problems(guide_text) + id_set_problems(guide_text, manifest, state)
                  + hash_problems(guide_text, state) + stamp_problems(guide_text, state)
                  + (label_problems(lines, labels) if labels is not None else [])
                  + table_problems(lines) + json_problems(lines) + citation_problems(guide_text, files))
    return violations, [NO_CHANGELOG] if labels is None else []
```

- [x] **Step 5: Pass the files through (`check.py`, `cli.py`)**

**Edit** `build/cc_guide/check.py` — replace:

```python
from state import (BASELINE, MANIFEST, PROBES, Manifest, ProbeRow, SetupError, Snapshot, Source, block_namer,
                   fetch_record, group_terms, latest_docs, no_snapshot, parse_baseline, parse_manifest, parse_probes,
                   read_fetch, read_utf8, snapshot_text)
```

with:

```python
from state import (BASELINE, MANIFEST, PROBES, Manifest, ProbeRow, SetupError, Snapshot, Source, block_namer,
                   citing_files, fetch_record, group_terms, latest_docs, no_snapshot, parse_baseline,
                   parse_manifest, parse_probes, read_fetch, read_utf8, snapshot_text)
```

**Edit** `build/cc_guide/check.py` — replace:

```python
    rows = parse_probes(source.read(PROBES))
    terms = group_terms(manifest, guide_text)
```

with:

```python
    rows = parse_probes(source.read(PROBES))
    terms = group_terms(manifest, guide_text)
    files = citing_files(source, manifest.guide)
```

**Edit** `build/cc_guide/check.py` — replace:

```python
    violations, notes = lint(guide_text, manifest, state, {r.label for r in releases} if releases else None)
```

with:

```python
    violations, notes = lint(guide_text, manifest, state, {r.label for r in releases} if releases else None, files)
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
'''cc_guide: the drift detector for specs/guides/claude-code-customization-guide.md
(Stage 1 of specs/claude-code-drift-automation-spec.md).
```

with:

```python
'''cc_guide: the drift detector for specs/guides/claude-code-customization-guide.md
and the citations that point at it (Stages 1 and 2 of
specs/claude-code-drift-automation-spec.md).
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
  lint [--ref REF]
      Offline gate over the guide, manifest.toml and baseline.json (R5). Reads
      the working tree unless --ref names a commit. Exit 0 clean, 1 with one
      line per violation, 2 on a setup error.
```

with:

```python
  lint [--ref REF]
      Offline gate over the guide, manifest.toml, baseline.json and every
      citation (R5). Reads the working tree unless --ref names a commit. Exit
      0 clean, 1 with one line per violation, 2 on a setup error. A citation
      stamped below a cited section's `changed` prints STALE <file> <ids> on
      stderr, which never changes the exit.
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
from guide import render_stamp
from lint import lint
from state import (BASELINE, BOOTSTRAP_DATE, BOOTSTRAP_RELEASE, MANIFEST, SetupError, Source, default_cache,
                   dump_baseline, is_iso_date, is_label, latest_docs, newest_changelog, parse_baseline,
                   parse_manifest, read_fetch, read_utf8, snapshot_docs, snapshot_text)
```

with:

```python
from guide import read_citations, render_stamp
from lint import lint, stale_lines
from state import (BASELINE, BOOTSTRAP_DATE, BOOTSTRAP_RELEASE, MANIFEST, SetupError, Source, citing_files,
                   default_cache, dump_baseline, is_iso_date, is_label, latest_docs, newest_changelog,
                   parse_baseline, parse_manifest, read_fetch, read_utf8, snapshot_docs, snapshot_text)
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
    releases = cached_releases(cache)
    violations, notes = lint(source.require(manifest.guide), manifest, state,
                             None if releases is None else {r.label for r in releases})
    for line in violations:
        print(line)
    for line in notes:
        print(f'note: {line}', file=sys.stderr)
    return 1 if violations else 0
```

with:

```python
    releases = cached_releases(cache)
    files = citing_files(source, manifest.guide)
    violations, notes = lint(source.require(manifest.guide), manifest, state,
                             None if releases is None else {r.label for r in releases}, files)
    for line in violations:
        print(line)
    for line in notes:
        print(f'note: {line}', file=sys.stderr)
    for line in stale_lines(read_citations(files)[0], state):
        print(line, file=sys.stderr)
    return 1 if violations else 0
```

**Edit** `CLAUDE.md` — replace:

```text
# Claude Code guide drift detector (build/cc_guide/): its suite; lint, run before committing a change to the guide or
# build/cc_guide/; check, which fetches the docs and reports what is due (exit 1 = due; reads main unless --worktree)
```

with:

```text
# Claude Code guide drift detector (build/cc_guide/): its suite; lint, run before committing a change to the guide, to
# build/cc_guide/ or to a file carrying a citation (its STALE lines never fail it); check, which fetches the docs and
# reports what is due (exit 1 = due; reads main unless --worktree)
```

- [x] **Step 6: Run the suites; expect +9 in cc_guide**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2/build/cc_guide --python 3.13 --with pytest python -m pytest -q`
Expected: all pass, 42 above the recorded baseline: Task 2's 33, plus 9 here (4 in `test_state.py`, 3 in `test_lint.py`, 1 in `test_cli.py`, 1 in `test_baseline.py`).

Then run the repo lint: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2 --python 3.13 python build/cc_guide/cli.py lint`
Expected: exit 0 with no `STALE` line (no citation exists yet).

- [x] **Step 7: Commit**

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2 add build/cc_guide/state.py build/cc_guide/lint.py build/cc_guide/check.py build/cc_guide/cli.py build/cc_guide/test_state.py build/cc_guide/test_lint.py build/cc_guide/test_cli.py build/cc_guide/test_baseline.py CLAUDE.md
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2 commit -m "feat(cc_guide): lint drift citations and print the stale ones" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: `check` lists citing files and the stale backlog (R6.8)

**Files:**
- Modify: `build/cc_guide/check.py`
- Modify: `build/cc_guide/test_check.py`

**Interfaces:**
- Consumes:
  - Task 2's `guide.read_citations` and `guide.by_section`;
  - Task 3's `lint.stale_by_section` and `state.citing_files`.
- Produces: two report keys.
  - `report['stale']` maps each stale section, in guide order, to its stale citing files. It is always present.
  - `report['citing']` maps each candidate section of a finding, in guide order, to its citing files. It is present when the docs were read.
  - The summary prints `stale citations: …` after the lint line, and `files citing a candidate section:` after the findings.

- [x] **Step 1: Write the failing tests**

**Edit** `build/cc_guide/test_check.py` — replace:

```python
'''Tests for check.py: compare, the changelog, every due rule, the fetch gate,
the report and exit codes (drift spec R6, R12.3's row fixture).'''
```

with:

```python
'''Tests for check.py: compare, the changelog, every due rule, the fetch gate,
the report with its citing files and stale backlog, and exit codes (drift
spec R6, R12.3's row fixture).'''
```

**Edit** `build/cc_guide/test_check.py` — replace:

```python
    assert set(report) == {'generated_at', 'inputs', 'docs', 'hashes', 'lint', 'latest_release', 'findings',
                           'deselected', 'llms', 'untriaged', 'releases', 'due', 'errors', 'exit'}
```

with:

```python
    assert set(report) == {'generated_at', 'inputs', 'docs', 'hashes', 'lint', 'stale', 'latest_release', 'findings',
                           'deselected', 'citing', 'llms', 'untriaged', 'releases', 'due', 'errors', 'exit'}
```

**Append** to `build/cc_guide/test_check.py`:

```python
def citing_repo(root, folder):
    '''The drift repo plus three committed citers: one stale against
    alpha.overview (changed 2.1.900), two current.'''
    repo = drift_repo(root, folder)
    write_tree(repo, {'hooks/old.sh': '#!/bin/sh\n# cc-guide: alpha.overview @2.1.899\nexit 0\n',
                      'agents/beta.md': '---\nname: beta\n# cc-guide: beta.overview beta.reference @2.1.900\n---\n',
                      'CLAUDE.md': '<!-- cc-guide: beta.reference @2.1.900 -->\n# Notes\n'})
    git(repo, 'add', '-A')
    git(repo, 'commit', '-qm', 'cite the guide')
    return repo


def test_the_report_lists_each_candidate_sections_citers_and_the_stale_backlog(tmp_path, docs_dir):
    '''R6.8: the citing files of every candidate section, from the index at
    the same inputs, and the stale backlog by section. Stale citations are
    never due (R6.7).'''
    repo = citing_repo(tmp_path / 'repo', docs_dir)
    code, report, _ = run_check(repo, tmp_path / 'cache', docs_dir)
    assert (code, report['stale'], report['citing']) == (0, {'alpha.overview': ['hooks/old.sh']}, {})
    write_tree(docs_dir, {'events.md': DOCS['events.md'].replace('fires on beta', 'fires on gamma')})
    code, report, path = run_check(repo, tmp_path / 'cache', docs_dir)
    assert [(f['kind'], f['candidates']) for f in report['findings']['beta']] == [('changed', ['beta.reference'])]
    assert (code, report['citing']) == (1, {'beta.reference': ['CLAUDE.md', 'agents/beta.md']})
    lines = check.summary(report, path)
    assert lines[2:4] == ['stale citations: 1 file(s) under 1 section(s), informational',
                          '  alpha.overview: hooks/old.sh']
    at = lines.index('files citing a candidate section:')
    assert lines[at + 1] == '  beta.reference: CLAUDE.md, agents/beta.md'


def test_check_reads_citations_at_its_inputs_and_lints_them(tmp_path, docs_dir):
    '''R6.1-R6.2: the citation index comes from the same ref as the rest, and
    a misplaced citation is a lint failure, due at once.'''
    repo = citing_repo(tmp_path / 'repo', docs_dir)
    write_tree(repo, {'hooks/old.sh': '#!/bin/sh\nexit 0\n# cc-guide: alpha.overview @2.1.899\n'})
    code, report, _ = run_check(repo, tmp_path / 'cache', docs_dir)
    assert (code, report['lint']['violations']) == (
        1, ['hooks/old.sh:3: a citation goes on a line before the first line of code (R4.1)'])
    code, report, _ = check.check(state.Source(repo, 'main'), tmp_path / 'cache', docs_dir=docs_dir,
                                  today=date(2026, 9, 10), now=NOW, fetch=None)
    assert (code, report['lint']['violations'], report['stale']) == (0, [], {'alpha.overview': ['hooks/old.sh']})
```

- [x] **Step 2: Run them; expect 3 failures**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2/build/cc_guide --python 3.13 --with pytest python -m pytest -q test_check.py`
Expected: `3 failed`:
- the report-keys test (an `AssertionError` on the key set);
- `test_the_report_lists…` (`KeyError: 'stale'`);
- `test_check_reads_citations…` (its first assertion passes, since Task 3 lints the files; it then fails on `KeyError: 'stale'`).

- [x] **Step 3: Implement**

**Edit** `build/cc_guide/check.py` — replace:

```python
selected blocks with the baseline, list each section's untriaged releases,
and report what is due (drift spec R6). R6.8's citing-file lists are Stage
2's, `--hook` (R6.10) Stage 4's and `packets` (R6.11) Stage 3's.'''
```

with:

```python
selected blocks with the baseline, list each section's untriaged releases
and the files citing it, and report what is due (drift spec R6). `--hook`
(R6.10) is Stage 4's and `packets` (R6.11) Stage 3's.'''
```

**Edit** `build/cc_guide/check.py` — replace:

```python
from lint import lint
```

with:

```python
from guide import by_section, read_citations
from lint import lint, stale_by_section
```

**Edit** `build/cc_guide/check.py` — replace:

```python
    files = citing_files(source, manifest.guide)
```

with:

```python
    files = citing_files(source, manifest.guide)
    citations, _ = read_citations(files)
```

**Edit** `build/cc_guide/check.py` — replace:

```python
    report['lint'] = {'violations': violations, 'notes': notes}
```

with:

```python
    report['lint'] = {'violations': violations, 'notes': notes}
    report['stale'] = stale_by_section(citations, state)
```

**Edit** `build/cc_guide/check.py` — replace:

```python
        slugs = parse_llms(docs.llms)
        report.update({
```

with:

```python
        slugs = parse_llms(docs.llms)
        cited = by_section(citations)
        flagged = {sid for f in findings for sid in f.candidates}
        report.update({
```

**Edit** `build/cc_guide/check.py` — replace:

```python
            'deselected': deselected,
```

with:

```python
            'deselected': deselected,
            'citing': {sid: [c.path for c in cited.get(sid, [])] for sid in state['sections'] if sid in flagged},
```

**Edit** `build/cc_guide/check.py` — replace:

```python
    lines += [f'  {v}' for v in violations]
    if 'findings' in report:
```

with:

```python
    lines += [f'  {v}' for v in violations]
    stale = report['stale']
    files = {path for paths in stale.values() for path in paths}
    lines.append('stale citations: none' if not stale else
                 f'stale citations: {len(files)} file(s) under {len(stale)} section(s), informational')
    lines += [f"  {sid}: {', '.join(paths)}" for sid, paths in stale.items()]
    if 'findings' in report:
```

**Edit** `build/cc_guide/check.py` — replace:

```python
        lines += [f"  [{f['group']}] {f['kind']} {Finding(**f).ref()}"
                  f" (candidates: {', '.join(f['candidates'])})" for f in kinds]
```

with:

```python
        lines += [f"  [{f['group']}] {f['kind']} {Finding(**f).ref()}"
                  f" (candidates: {', '.join(f['candidates'])})" for f in kinds]
        citing = {sid: paths for sid, paths in report['citing'].items() if paths}
        if citing:
            lines.append('files citing a candidate section:')
            lines += [f"  {sid}: {', '.join(paths)}" for sid, paths in citing.items()]
```

- [x] **Step 4: Run the suite; expect +2**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2/build/cc_guide --python 3.13 --with pytest python -m pytest -q`
Expected: all pass, 44 above the recorded baseline.

- [x] **Step 5: Commit**

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2 add build/cc_guide/check.py build/cc_guide/test_check.py
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2 commit -m "feat(cc_guide): report each flagged section's citers and the stale backlog" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: `baseline cite` and `accept`'s citer stamps (R7, R2.4)

**Files:**
- Modify: `build/cc_guide/baseline.py`
- Modify: `build/cc_guide/cli.py`
- Modify: `build/cc_guide/test_baseline.py`, `build/cc_guide/test_cli.py`
- Modify: `build/CLAUDE.md` (the `cc_guide/` paragraph)

**Interfaces:**
- Consumes:
  - Task 2's `guide.file_citation`, `guide.read_citations` and `guide.by_section`;
  - Task 3's `state.citing_files`;
  - Stage 1's `baseline.known` and `baseline.next_changed`.
- Produces:
  - `baseline.cite(path: str, text: str, state: dict) -> tuple[str, str]`, returning the new text and the stamp;
  - the CLI `baseline cite FILE [FILE ...]`;
  - `cli.repo_path(name: str) -> str`;
  - `baseline accept … --substantive` refuses, exit 2 and nothing written, while any citation fails to parse: a broken citation has no stamp for the new `changed` to exceed (R2.4).

- [x] **Step 1: Write the failing tests**

**Append** to `build/cc_guide/test_baseline.py`:

```python
def test_cite_stamps_the_highest_changed_and_changes_nothing_else(docs_dir):
    '''R7 cite: versions compare as tuples, so 2.1.900.1 outranks 2.1.900.'''
    s = fixture_state(docs_dir)
    text = '#!/bin/sh\n# A gate.\n# cc-guide: alpha.reference alpha.overview @2.1.219\nexit 0\n'
    assert baseline.cite('hooks/gate.sh', text, s) == (text.replace('@2.1.219', '@2.1.900'), '2.1.900')
    s['sections']['alpha.reference']['changed'] = '2.1.900.1'
    assert baseline.cite('hooks/gate.sh', text, s)[1] == '2.1.900.1'


def test_cite_refuses_a_file_it_cannot_stamp(docs_dir):
    s = fixture_state(docs_dir)
    for text, message in [('exit 0\n', 'hooks/gate.sh: carries no citation'),
                          ('# cc-guide: gamma.overview @2.1.219\n', 'hooks/gate.sh: unknown section IDs: gamma.overview'),
                          ('exit 0\n# cc-guide: alpha.overview @2.1.219\n',
                           'hooks/gate.sh:2: a citation goes on a line before the first line of code (R4.1)')]:
        with pytest.raises(state.SetupError) as err:
            baseline.cite('hooks/gate.sh', text, s)
        assert str(err.value) == message
```

**Edit** `build/cc_guide/test_cli.py` — replace:

```python
    assert 'Offline gate over the guide, manifest.toml, baseline.json and every' in outs[0]
```

with:

```python
    assert 'Offline gate over the guide, manifest.toml, baseline.json and every' in outs[0]
    assert '  baseline cite FILE [FILE ...]\n' in outs[0]
```

**Append** to `build/cc_guide/test_cli.py`:

```python
def test_cite_stamps_each_file_at_its_sections_highest_changed_and_writes_only_those_files(world, capsys):
    '''R7 cite: alpha.overview changed at 2.1.900 and alpha.reference at
    2.1.899, so a file citing both is stamped @2.1.900. Paths are read from
    the repo root, so a symlink is stamped at its target.'''
    repo, cache, _ = world
    cited(repo, {'hooks/gate.sh': '#!/bin/sh\n# cc-guide: alpha.overview alpha.reference @2.1.219\nexit 0\n',
                 'rules/style.md': '---\npaths: x\n# cc-guide: alpha.reference @2.1.219\n---\n'})
    (repo / '.claude').mkdir()
    (repo / '.claude' / 'style.md').symlink_to('../rules/style.md')
    git(repo, 'add', '-A')
    git(repo, 'commit', '-qm', 'link the rule')
    assert main(cache, 'baseline', 'cite', 'hooks/gate.sh', str(repo / '.claude' / 'style.md')) == 0
    assert capsys.readouterr().out == 'stamped hooks/gate.sh @2.1.900\nstamped rules/style.md @2.1.899\n'
    assert dirty(repo) == ['hooks/gate.sh', 'rules/style.md']
    assert (repo / 'hooks/gate.sh').read_text() == (
        '#!/bin/sh\n# cc-guide: alpha.overview alpha.reference @2.1.900\nexit 0\n')
    assert main(cache, 'lint') == 0
    assert capsys.readouterr() == ('', '')


@pytest.mark.parametrize('files, args, message', [
    ({'hooks/gate.sh': '#!/bin/sh\nexit 0\n'}, ['hooks/gate.sh'], 'hooks/gate.sh: carries no citation'),
    ({'hooks/gate.sh': '#!/bin/sh\n# cc-guide: gamma.overview @2.1.219\n'}, ['hooks/gate.sh'],
     'hooks/gate.sh: unknown section IDs: gamma.overview'),
    ({'hooks/gate.sh': '#!/bin/sh\nexit 0\n# cc-guide: alpha.overview @2.1.219\n'}, ['hooks/gate.sh'],
     'hooks/gate.sh:3: a citation goes on a line before the first line of code (R4.1)'),
    ({}, ['hooks/none.sh'], 'hooks/none.sh: not found in the working tree'),
    ({}, ['/etc/hosts'], '/etc/hosts: not a file in {repo}'),
], ids=['uncited', 'unknown-id', 'misplaced', 'absent', 'outside'])
def test_cite_refuses_with_one_error_line_and_writes_nothing(world, capsys, files, args, message):
    repo, cache, _ = world
    good = {'hooks/ok.sh': '#!/bin/sh\n# cc-guide: alpha.overview @2.1.219\n'}
    cited(repo, {**good, **files})
    assert main(cache, 'baseline', 'cite', 'hooks/ok.sh', *args) == 2
    assert capsys.readouterr() == ('', f'cc-guide: {message.format(repo=repo)}\n')
    assert dirty(repo) == []


def test_a_substantive_accept_keeps_changed_above_every_citers_stamp(world):
    '''R2.4: a citer already stamped at the newest release forces a fourth
    component, so the new `changed` still flags it.'''
    repo, cache, _ = world
    cited(repo, {'hooks/gate.sh': '#!/bin/sh\n# cc-guide: alpha.overview @2.1.902\n'})
    guide = repo / GUIDE_PATH
    guide.write_text(guide.read_text().replace('Alpha uses', 'Alpha now uses'))
    assert main(cache, 'baseline', 'accept', 'alpha.overview', '--substantive') == 0
    assert load(repo)['sections']['alpha.overview']['changed'] == '2.1.902.1'


def test_a_substantive_accept_refuses_while_a_citation_is_broken(world, capsys):
    '''R2.4: a citation that does not parse yields no stamp for `changed` to
    exceed, so the accept refuses until the lint passes, and writes nothing.'''
    repo, cache, _ = world
    cited(repo, {'hooks/gate.sh': '#!/bin/sh\nexit 0\n# cc-guide: alpha.overview @2.1.902\n'})
    guide = repo / GUIDE_PATH
    guide.write_text(guide.read_text().replace('Alpha uses', 'Alpha now uses'))
    assert main(cache, 'baseline', 'accept', 'alpha.overview', '--substantive') == 2
    assert capsys.readouterr() == ('', (
        'cc-guide: a substantive accept needs every citation to parse (R2.4); fix these first:\n'
        'hooks/gate.sh:3: a citation goes on a line before the first line of code (R4.1)\n'))
    assert dirty(repo) == [GUIDE_PATH]
```

- [x] **Step 2: Run them; expect 11 failures**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2/build/cc_guide --python 3.13 --with pytest python -m pytest -q test_baseline.py test_cli.py`
Expected: `11 failed`:
- `test_baseline.py` 2: `AttributeError: module 'baseline' has no attribute 'cite'`;
- `test_cli.py` 9:
  - the help test's new assertion;
  - six `cite` tests that end in `SystemExit: 2` from argparse (`invalid choice: 'cite'`);
  - the accept test (`'2.1.902' != '2.1.902.1'`);
  - the broken-citation accept test, which today's accept lets through (`assert 0 == 2`).

- [x] **Step 3: Implement `cite` (`baseline.py`)**

**Edit** `build/cc_guide/baseline.py` — replace:

```python
region (drift spec R7). These functions return new state; cli.py writes it
to the working tree, and nothing is committed. `cite` is Stage 2's.'''
```

with:

```python
region, and of citation stamps (drift spec R7). These functions return new
state or text; cli.py writes it to the working tree, and nothing is
committed.'''
```

**Edit** `build/cc_guide/baseline.py` — replace:

```python
from guide import NO_STAMP, anchor_problems, render_stamp, sections, stamp_bounds, text_hash, with_stamp
```

with:

```python
from guide import (NO_STAMP, anchor_problems, file_citation, render_stamp, sections, stamp_bounds, text_hash,
                   with_stamp)
```

**Edit** `build/cc_guide/baseline.py` — replace:

```python
    sets a new `changed` (R2.4), which flags the section's citers; only it
    reads `newest`, which an editorial accept may leave None. Stage 1 has
    no citations, so cli.py passes none; Stage 2 passes the index's stamps.'''
```

with:

```python
    sets a new `changed` (R2.4), which flags the section's citers; only it
    reads `newest`, which an editorial accept may leave None, and
    `citer_stamps`, each section's citers' review stamps.'''
```

**Append** to `build/cc_guide/baseline.py`:

```python
def cite(path: str, text: str, state: dict) -> tuple[str, str]:
    '''R7 cite: the file's text with its citation stamped at the highest
    `changed` among its cited sections, and that stamp. A file without one
    well-formed, well-placed citation, or citing a section baseline.json
    lacks, is a SetupError (R6.9: exit 2).'''
    citation, problems = file_citation(path, text)
    if problems:
        raise SetupError('\n'.join(problems))
    if citation is None:
        raise SetupError(f'{path}: carries no citation')
    try:
        known(state, citation.ids)
    except SetupError as exc:
        raise SetupError(f'{path}: {exc}') from None
    stamp = max((state['sections'][sid]['changed'] for sid in citation.ids), key=version_key)
    lines = text.split('\n')
    lines[citation.line - 1] = lines[citation.line - 1].replace(f'@{citation.stamp}', f'@{stamp}')
    return '\n'.join(lines), stamp
```

- [x] **Step 4: Wire the CLI (`cli.py`)**

**Edit** `build/cc_guide/cli.py` — replace:

```python
  baseline stamp
      The only writer of baseline.json and the guide's stamp region (R7).
```

with:

```python
  baseline stamp
  baseline cite FILE [FILE ...]
      The only writer of baseline.json, the guide's stamp region and citation
      stamps (R7). cite stamps each file's citation at the highest `changed`
      among its cited sections, after a review; FILE is repo-relative, as
      lint and check print it. accept --substantive keeps a new `changed`
      above every citer's stamp (R2.4).
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
from guide import read_citations, render_stamp
```

with:

```python
from guide import by_section, read_citations, render_stamp
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
    b.add_parser('stamp')
    return p
```

with:

```python
    b.add_parser('stamp')
    b.add_parser('cite').add_argument('files', nargs='+')
    return p
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
def run_lint(args, cache: Path) -> int:
```

with:

```python
def repo_path(name: str) -> str:
    '''A FILE argument as a repo-relative path. A relative one is read from
    the repo root, as lint and check print paths.'''
    full = (REPO / name).resolve()
    try:
        return full.relative_to(REPO.resolve()).as_posix()
    except ValueError:
        raise SetupError(f'{name}: not a file in {REPO}') from None


def run_lint(args, cache: Path) -> int:
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
    if args.action == 'accept':
        # Only --substantive sets `changed`, from the newest release; an editorial accept needs no cache.
        newest = newest_releases(cache)[0].label if args.substantive else None
        new = baseline.accept(state, guide_text, args.ids, args.substantive, newest)
```

with:

```python
    if args.action == 'cite':
        stamped = []
        for name in dict.fromkeys(args.files):
            path = repo_path(name)
            stamped.append((path, *baseline.cite(path, tree.require(path), state)))
        for path, text, stamp in stamped:  # all checked before any write
            (REPO / path).write_text(text, encoding='utf-8')
            print(f'stamped {path} @{stamp}')
        return 0
    if args.action == 'accept':
        # Only --substantive sets `changed`, from the newest release and above every citer's stamp (R2.4);
        # an editorial accept needs no cache.
        newest, stamps = None, None
        if args.substantive:
            newest = newest_releases(cache)[0].label
            citations, problems = read_citations(citing_files(tree, manifest.guide))
            if problems:  # a citation that does not parse has no stamp to stay above
                raise SetupError('a substantive accept needs every citation to parse (R2.4); fix these first:\n'
                                 + '\n'.join(problems))
            stamps = {sid: [c.stamp for c in cs] for sid, cs in by_section(citations).items()}
        new = baseline.accept(state, guide_text, args.ids, args.substantive, newest, stamps)
```

**Edit** `build/CLAUDE.md` — replace:

```text
narrows its `artifacts`, in the same change. Nothing is committed for you.
```

with:

```text
narrows its `artifacts`, in the same change. Files whose correctness rests
on a Claude Code fact carry a `cc-guide:` citation naming the guide sections
they rely on (the spec's R4.1 places it); `cli.py lint` checks each one and
prints `STALE` for a file reviewed before a cited section last changed.
After reviewing such a file, `cli.py baseline cite <file>` restamps it.
Nothing is committed for you.
```

- [x] **Step 5: Run the suite; expect +10**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2/build/cc_guide --python 3.13 --with pytest python -m pytest -q`
Expected: all pass, 54 above the recorded baseline. That is +2 in `test_baseline.py` and +8 new tests in `test_cli.py`; the help test was already counted.

- [x] **Step 6: Commit**

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2 add build/cc_guide/baseline.py build/cc_guide/cli.py build/cc_guide/test_baseline.py build/cc_guide/test_cli.py build/CLAUDE.md
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2 commit -m "feat(cc_guide): baseline cite, and keep accept's new changed above every citer" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: The conformance import check skips block-level HTML comments (S1)

**Files:**
- Modify: `build/check_conformance.py` (`import_targets`, and a new `comment_lines`)
- Modify: `build/test_check_conformance.py`

**Interfaces:**
- Produces: `check_conformance.comment_lines(text: str) -> set[int]` (1-based); `import_targets` now skips those lines.

- [x] **Step 1: Write the failing test**

**Edit** `build/test_check_conformance.py` — replace:

```python
def test_claude_md_import_resolves_pass(tmp_path):
```

with:

```python
def test_import_targets_skip_block_level_html_comments_only():
    '''Claude Code expands no import inside a block-level HTML comment (probed
    on 2.1.296), so a drift citation's @<version> there is no import. A comment
    inside a line is not block-level and is still read.'''
    text = ('<!-- cc-guide: skills.locations @2.1.219 -->\n'
            '# Title\n'
            '   <!-- a maintainer note\n'
            '   naming @docs/x.md\n'
            '   -->\n'
            'Inline <!-- @docs/y.md --> is not block-level.\n'
            '    <!-- four spaces is code, @docs/z.md -->\n'
            f'{FENCE}html\n<!-- fenced, so no comment opens\n{FENCE}\n'
            '@docs/w.md\n')
    assert cc.import_targets(text) == [(6, 'docs/y.md'), (7, 'docs/z.md'), (11, 'docs/w.md')]
    assert cc.comment_lines('<!-- open, never closed\n@docs/a.md') == {1, 2}


def test_claude_md_import_resolves_pass(tmp_path):
```

- [x] **Step 2: Run it; expect 1 failure**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2/build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py -k block_level`
Expected: `1 failed`. `import_targets` also returns `(1, '2.1.219')` and `(4, 'docs/x.md')`.

- [x] **Step 3: Implement**

**Edit** `build/check_conformance.py` — replace:

```python
IMPORT_RE = re.compile(r'(?<![\w/.@-])@([^\s`]+)')


def import_targets(text: str) -> list[tuple[int, str]]:
    '''(line, path) for each @path import: outside fenced blocks and inline code
    spans, not glued to a word (so not an email address), trailing punctuation dropped.'''
    fenced = fenced_lines(text)
    found: list[tuple[int, str]] = []
    for n, line in enumerate(text.split('\n'), start=1):
        if n in fenced:
            continue
        bare = INLINE_CODE_RE.sub(lambda m: ' ' * len(m.group(0)), line)
        for m in IMPORT_RE.finditer(bare):
            target = m.group(1).rstrip('.,;:!?)]}\'"')
            if target:
                found.append((n, target))
    return found
```

with:

```python
IMPORT_RE = re.compile(r'(?<![\w/.@-])@([^\s`]+)')
# A block-level HTML comment opens a line, after at most three spaces (CommonMark HTML block 2).
COMMENT_OPEN_RE = re.compile(r'^ {0,3}<!--')


def comment_lines(text: str) -> set[int]:
    '''1-based lines inside block-level HTML comments, outside fenced blocks:
    from a line opening one through the first line holding `-->`. Claude Code
    expands no import there (probed on 2.1.296; plan 43); an unclosed comment
    runs to the end.'''
    fenced = fenced_lines(text)
    out: set[int] = set()
    open_at = None
    for n, line in enumerate(text.split('\n'), start=1):
        if open_at is None and n not in fenced and COMMENT_OPEN_RE.match(line):
            open_at = n
        if open_at is not None:
            out.add(n)
            tail = line[line.index('<!--') + 4:] if n == open_at else line
            if '-->' in tail:
                open_at = None
    return out


def import_targets(text: str) -> list[tuple[int, str]]:
    '''(line, path) for each @path import: outside fenced blocks, block-level
    HTML comments and inline code spans, not glued to a word (so not an email
    address), trailing punctuation dropped.'''
    skipped = fenced_lines(text) | comment_lines(text)
    found: list[tuple[int, str]] = []
    for n, line in enumerate(text.split('\n'), start=1):
        if n in skipped:
            continue
        bare = INLINE_CODE_RE.sub(lambda m: ' ' * len(m.group(0)), line)
        for m in IMPORT_RE.finditer(bare):
            target = m.group(1).rstrip('.,;:!?)]}\'"')
            if target:
                found.append((n, target))
    return found
```

- [x] **Step 4: Run the conformance suite and lint**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2/build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_conformance.py`
Expected: all pass, +1.

Then run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2 --python 3.13 --with pyyaml python build/check_conformance.py`
Expected: exit 0.

- [x] **Step 5: Commit**

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2 add build/check_conformance.py build/test_check_conformance.py
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2 commit -m "fix(conformance): read no @ import inside a block-level HTML comment, as Claude Code does" -m "Probed on Claude Code 2.1.296 (plan 43): an @path in a block-level comment is not expanded. Drift citations put @<version> in one at the top of CLAUDE.md." -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: `cli.py lint` becomes the seventh commit lint (D3)

**Files:**
- Modify: `build/run_commit_lints.sh`, `build/githooks/pre-commit` (comment)
- Modify: `build/test_commit_lints.py`
- Modify: `CLAUDE.md` (the commit-lint comment, in place), `build/CLAUDE.md` ("six")

**Interfaces:**
- Produces: the runner check name `cc_guide_lint`, which appears on `commit lints failed:` lines.

- [x] **Step 1: Write the failing tests**

**Edit** `build/test_commit_lints.py` — replace:

```python
CHECKS = {'check_frontmatter', 'check_provenance', 'check_snippets',
          'check_conformance', 'declared_dependencies', 'sync_runtime_assets'}
```

with:

```python
CHECKS = {'check_frontmatter', 'check_provenance', 'check_snippets',
          'check_conformance', 'declared_dependencies', 'sync_runtime_assets', 'cc_guide_lint'}
```

**Edit** `build/test_commit_lints.py` — replace:

```python
def test_hook_fails_open_without_uv(clone, tmp_path):
```

with:

```python
def test_misplaced_drift_citation_is_refused(clone):
    '''The seventh lint is the drift tool's: a citation after a script's first
    line of code is a violation (drift spec R5).'''
    script = clone / 'build' / 'smoke_test.py'
    script.write_text(script.read_text() + '#' + ' cc-guide: hooks.events @2.1.219\n')
    git(clone, 'add', 'build/smoke_test.py')
    before = head(clone)
    result = commit(clone, '-m', 'misplaced citation')
    assert result.returncode != 0
    assert failed_names(result) == {'cc_guide_lint'}, result.stderr
    assert head(clone) == before


def test_hook_fails_open_without_uv(clone, tmp_path):
```

- [x] **Step 2: Run them; expect 2 failures**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2/build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_commit_lints.py`
Expected: `2 failed`:
- `test_runner_fails_closed_without_uv`: the failed set lacks `cc_guide_lint`;
- `test_misplaced_drift_citation_is_refused`: the commit succeeds.

The clone holds HEAD, which has Tasks 2–5's lint, but the working-tree runner it copies lacks the seventh check. Both tests need Tasks 2–5 committed, which the order guarantees.

- [x] **Step 3: Implement**

> Deviation: the final review corrected the CLAUDE.md comment's claim that the hook lints untracked drafts; the drift lint reads tracked files only (cb855c4).

**Edit** `build/run_commit_lints.sh` — replace:

```bash
# The six commit lints that CLAUDE.md lists under Commands. Fails closed: exit 1
```

with:

```bash
# The seven commit lints that CLAUDE.md lists under Commands. Fails closed: exit 1
```

**Edit** `build/run_commit_lints.sh` — replace:

```bash
run sync_runtime_assets uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py --check
```

with:

```bash
run sync_runtime_assets uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py --check
run cc_guide_lint uv run --python 3.13 python build/cc_guide/cli.py lint
```

**Edit** `build/githooks/pre-commit` — replace:

```bash
# Pre-commit: run the six commit lints
```

with:

```bash
# Pre-commit: run the seven commit lints
```

**Edit** `CLAUDE.md` — replace:

```text
# Commit lints: these three, the dependency-drift test, snippet Tier 1 and sync_runtime_assets.py --check make six.
# build/run_commit_lints.sh runs all six; build/githooks/pre-commit runs it on each commit once enabled (an owner step:
# git config core.hooksPath build/githooks writes repo config every worktree reads); the hook lints the working tree,
# untracked files included, so a broken untracked draft can block any commit. .github/workflows/lints.yml: PRs and main.
```

with:

```text
# Commit lints: these three, the dependency-drift test, snippet Tier 1, sync_runtime_assets.py --check and the drift
# lint (cli.py lint, below) make seven. build/run_commit_lints.sh runs all seven; build/githooks/pre-commit runs it on
# each commit once enabled (an owner step: git config core.hooksPath build/githooks writes repo config every worktree
# reads); the hook lints the working tree, untracked drafts included. .github/workflows/lints.yml: PRs and main.
```

**Edit** `build/CLAUDE.md` — replace:

```text
`run_commit_lints.sh` runs the six commit lints that the root `CLAUDE.md`
```

with:

```text
`run_commit_lints.sh` runs the seven commit lints that the root `CLAUDE.md`
```

- [x] **Step 4: Run the commit-lint tests and the runner**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2/build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_commit_lints.py`
Expected: all pass, +1.

Then run: `bash /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2/build/run_commit_lints.sh`
Expected: `== cc_guide_lint` appears, then `commit lints passed`.

- [x] **Step 5: Commit** (this commit is the first the hook lints with seven checks)

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2 add build/run_commit_lints.sh build/githooks/pre-commit build/test_commit_lints.py CLAUDE.md build/CLAUDE.md
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2 commit -m "build: run the drift lint as the seventh commit lint" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: The citation sweep (R11.3), NOTICE, and the frontmatter tests (R12.4)

**Files:**
- Modify: the 41 files in the sweep table (one inserted line each)
- Modify: `NOTICE` (one bullet)
- Modify: `build/test_check_frontmatter.py`

The R4.5 load check ran before this task (Planning record) and passed in all three runtimes.

- [x] **Step 1: Write the frontmatter tests**

> Deviation: the fix wave replaced the `CITATION[:11]` slice with a named `CITATION_PREFIX` constant (f759c79).

**Edit** `build/test_check_frontmatter.py` — replace:

```python
from pathlib import Path

from check_frontmatter import (
```

with:

```python
import subprocess
from pathlib import Path

import yaml

from check_frontmatter import (
```

**Append** to `build/test_check_frontmatter.py`:

```python
CITATION = '#' + ' cc-guide: skills.frontmatter @2.1.219'


def test_a_drift_citation_comment_passes_every_frontmatter_check(tmp_path):
    '''Drift spec R12.4: a `# cc-guide:` YAML comment as the last frontmatter
    line passes check_frontmatter.py, which never sees it.'''
    d = make_skill(tmp_path, 'cited-skill', f'name: cited-skill\ndescription: >\n  Use when testing.\n{CITATION}')
    assert check_skill(d) == []
    agent = tmp_path / 'cited-agent.md'
    agent.write_text(f'---\nname: cited-agent\ndescription: Use when testing.\ntools: Read\n{CITATION}\n---\n\nBody.\n')
    assert check_agent_file(agent) == []
    command = tmp_path / 'cited-command.md'
    command.write_text(f'---\ndescription: Do a thing.\ndisable-model-invocation: true\n{CITATION}\n---\n\nBody.\n')
    assert check_command_file(command) == []


def test_an_indented_citation_would_join_a_folded_description():
    '''Why the drift lint wants column 0: indented, the line is description text.'''
    folded = 'name: x\ndescription: >\n  Use when testing.\n'
    assert yaml.safe_load(folded + CITATION + '\n') == yaml.safe_load(folded)
    assert yaml.safe_load(folded + '  ' + CITATION + '\n') != yaml.safe_load(folded)


def test_every_frontmatter_citation_leaves_the_parsed_frontmatter_unchanged():
    '''Drift spec R4.1: each tracked Markdown file whose frontmatter carries a
    citation parses to the same mapping without that line.'''
    listed = subprocess.run(['git', 'ls-files', '-z', '*.md'], cwd=REPO, capture_output=True, check=True)
    cited = []
    for name in filter(None, listed.stdout.decode().split('\0')):
        path = REPO / name
        if path.is_symlink() or not path.is_file():
            continue
        lines = path.read_text(encoding='utf-8').split('\n')
        if lines[0] != '---' or '---' not in lines[1:]:
            continue
        front = lines[1:lines.index('---', 1)]
        kept = [line for line in front if not line.startswith(CITATION[:11])]
        if kept != front:
            cited.append(name)
            # Each line ends in a newline, as it does before the closing ---.
            assert yaml.safe_load(''.join(f'{line}\n' for line in kept)) == yaml.safe_load(
                ''.join(f'{line}\n' for line in front)), name
    assert cited, 'no tracked frontmatter carries a citation, so this test checked nothing'
```

- [x] **Step 2: Run them; expect 1 failure, 2 passes by design**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2/build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_frontmatter.py`
Expected: `1 failed`. `test_every_frontmatter_citation…` fails with `no tracked frontmatter carries a citation, so this test checked nothing`.

The other two pass at once, and that is the design, not a plan defect:
- `test_a_drift_citation_comment_passes…` is R12.4's pin that `check_frontmatter.py`, unchanged, never sees the comment;
- `test_an_indented_citation…` pins the YAML fact the column-0 rule rests on.

- [x] **Step 3: Save the sweep script**

Save this as `/Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2/.sdd/43-claude-code-drift-automation/sweep.py`. The `.sdd/` directory is gitignored and never committed. `TABLE` is the sweep table above, row for row.

```python
'''Plan 43's citation sweep (drift spec R11.3): insert each TABLE row's
citation where R4.1 puts it, read it back through guide.file_citation, and
write nothing until every row checks out. 'ALL' cites every guide section,
in guide order. Run with the worktree as the working directory.'''
import sys
from pathlib import Path

sys.path.insert(0, 'build/cc_guide')
import guide  # noqa: E402

TABLE = [
    ('hooks/README.md', 'subagents.frontmatter rules.settings hooks.events hooks.exit-codes hooks.configuration hooks.patterns hooks.pitfalls', '2.1.219'),
    ('hooks/probe-readonly-guard.sh', 'hooks.exit-codes hooks.pitfalls', '2.1.219'),
    ('hooks/readonly-agent-guard.py', 'hooks.events hooks.exit-codes hooks.patterns', '2.1.219'),
    ('hooks/ruff-check.sh', 'hooks.events hooks.exit-codes hooks.patterns', '2.1.219'),
    ('hooks/ruff-fix.sh', 'hooks.events hooks.patterns', '2.1.219'),
    ('hooks/uv-guard.sh', 'hooks.events hooks.exit-codes hooks.patterns', '2.1.219'),
    ('hooks/test_readonly_agent_guard.py', 'hooks.events hooks.exit-codes hooks.patterns', '2.1.219'),
    ('rules/clean-code-python.md', 'rules.rules-files', '2.1.219'),
    ('CLAUDE.md', 'skills.locations', '2.1.219'),
    ('README.md', 'skills.locations commands.overview subagents.overview subagents.models rules.rules-files hooks.events hooks.exit-codes hooks.configuration', '2.1.219'),
    ('install.py', 'skills.locations commands.overview subagents.overview', '2.1.219'),
    ('agents/code-reviewer.md', 'subagents.frontmatter subagents.tools', '2.1.219'),
    ('agents/debugger.md', 'subagents.frontmatter subagents.tools', '2.1.219'),
    ('agents/docs-writer.md', 'subagents.frontmatter subagents.tools', '2.1.219'),
    ('agents/explore.md', 'subagents.frontmatter subagents.tools subagents.models', '2.1.219'),
    ('agents/security-auditor.md', 'subagents.frontmatter subagents.tools', '2.1.219'),
    ('agents/task-reviewer.md', 'subagents.frontmatter subagents.tools', '2.1.219'),
    ('agents/test-runner.md', 'subagents.frontmatter subagents.tools subagents.models', '2.1.219'),
    ('commands/deferred.md', 'skills.frontmatter commands.overview', '2.1.219'),
    ('commands/fix-issue.md', 'skills.frontmatter commands.overview', '2.1.219'),
    ('commands/license-audit.md', 'skills.frontmatter commands.overview', '2.1.219'),
    ('build/check_frontmatter.py', 'skills.frontmatter commands.overview subagents.frontmatter subagents.tools subagents.models', '2.1.219'),
    ('build/check_conformance.py', 'skills.frontmatter skills.arguments commands.overview subagents.frontmatter subagents.tools rules.hierarchy rules.rules-files rules.settings hooks.exit-codes hooks.configuration hooks.patterns hooks.pitfalls lean.model-routing', '2.1.288'),
    ('build/cc_guide/conformance.toml', 'ALL', '2.1.288'),
    ('skills/brainstorming/SKILL.md', 'lean.session-hygiene', '2.1.219'),
    ('skills/dispatching-parallel-agents/SKILL.md', 'subagents.frontmatter subagents.models subagents.isolation', '2.1.219'),
    ('skills/executing-plans/SKILL.md', 'subagents.frontmatter', '2.1.219'),
    ('skills/requesting-code-review/SKILL.md', 'subagents.frontmatter subagents.models subagents.isolation', '2.1.219'),
    ('skills/subagent-driven-development/SKILL.md', 'subagents.frontmatter subagents.models subagents.isolation lean.session-hygiene lean.model-routing', '2.1.219'),
    ('skills/writing-plans/SKILL.md', 'lean.session-hygiene lean.model-routing', '2.1.219'),
    ('skills/writing-skills/SKILL.md', 'skills.locations skills.frontmatter skills.description skills.listing-budget skills.progressive-disclosure subagents.isolation', '2.1.219'),
    ('skills/bayesian-workflow/SKILL.md', 'skills.frontmatter', '2.1.219'),
    ('skills/bayesian-workflow/README.md', 'skills.locations', '2.1.219'),
    ('skills/tune-hyperparameters/SKILL.md', 'skills.frontmatter', '2.1.219'),
    ('skills/tech-debt/SKILL.md', 'skills.frontmatter subagents.isolation', '2.1.219'),
    ('skills/prepare-handoff/SKILL.md', 'subagents.isolation rules.auto-memory lean.session-hygiene lean.model-routing', '2.1.219'),
    ('skills/derive-roadmap/SKILL.md', 'lean.session-hygiene', '2.1.219'),
    ('skills/develop-testing-strategy/SKILL.md', 'lean.session-hygiene lean.model-routing', '2.1.219'),
    ('skills/recommend-probabilistic-model/SKILL.md', 'lean.session-hygiene lean.model-routing', '2.1.219'),
    ('skills/track-model-experiments/SKILL.md', 'lean.session-hygiene', '2.1.219'),
    ('skills/llm-wiki/INSTALL.md', 'skills.locations', '2.1.219'),
]
GUIDE = 'specs/guides/claude-code-customization-guide.md'
ORDER = [s.id for s in guide.sections(Path(GUIDE).read_text(encoding='utf-8'))]


def place(path: str, lines: list[str], line: str) -> list[str]:
    '''R4.1's placement: the frontmatter's last line, else a Markdown file's
    first line; directly after a script's shebang, else its first line.'''
    if path.endswith('.md'):
        if lines[0] == '---':
            close = lines.index('---', 1)
            return lines[:close] + [line] + lines[close:]
        return [line] + lines
    at = 1 if lines[0].startswith('#!') else 0
    return lines[:at] + [line] + lines[at:]


def main() -> int:
    writes = []
    for path, ids, stamp in TABLE:
        ids = ' '.join(ORDER) if ids == 'ALL' else ids
        body = f'cc-guide: {ids} @{stamp}'
        line = f'<!-- {body} -->' if path.endswith('.md') and not Path(path).read_text(encoding='utf-8').startswith('---\n') else f'# {body}'
        text = Path(path).read_text(encoding='utf-8')
        if any(guide.CITE_SHAPED_RE.match(old) for old in text.split('\n')):
            sys.exit(f'{path}: already holds a citation-shaped line')
        new = '\n'.join(place(path, text.split('\n'), line))
        citation, problems = guide.file_citation(path, new)
        if problems or citation is None or citation.ids != tuple(ids.split()) or citation.stamp != stamp:
            sys.exit(f'{path}: {problems or citation}')
        writes.append((path, new))
    for path, new in writes:
        Path(path).write_text(new, encoding='utf-8')
        print(f'cited {path}')
    print(f'{len(writes)} files cited')
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

- [x] **Step 4: Run the sweep**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2 --python 3.13 python .sdd/43-claude-code-drift-automation/sweep.py`
Expected: 41 `cited <path>` lines, then `41 files cited`.

The script checks every row before it writes, so a refusal changes nothing. On a refusal, report the message and stop; do not edit the table to force it.

Then confirm the diff is one added line per file and no mode change:
- `git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2 diff --shortstat -- . ':(exclude)build/test_check_frontmatter.py'` prints `41 files changed, 41 insertions(+)`;
- `git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2 diff --summary` prints nothing.

- [x] **Step 5: Record it in NOTICE (S5)**

**Edit** `NOTICE` — replace:

```text
    page (https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).
    The file remains in this repo's git history.
```

with:

```text
    page (https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).
    The file remains in this repo's git history.
  - Seven of these skills' SKILL.md files (brainstorming,
    dispatching-parallel-agents, executing-plans, requesting-code-review,
    subagent-driven-development, writing-plans, writing-skills), and
    agents/code-reviewer.md and agents/task-reviewer.md, gained one
    `# cc-guide:` YAML comment as the last frontmatter line on 2026-10-12.
    It names the sections of this repo's Claude Code guide that the file
    rests on, so a docs change flags it for review
    (specs/claude-code-drift-automation-spec.md, R4). No parsed field changed.
```

- [x] **Step 6: Run every gate**

Run each:
- the frontmatter tests: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2/build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_frontmatter.py`. Expected: all pass, +3.
- `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2 --python 3.13 python build/cc_guide/cli.py lint`. Expected: exit 0, nothing on stdout, and 41 `STALE` lines on stderr, among them `STALE hooks/ruff-check.sh …`, `STALE hooks/README.md …` and one for each of the 7 `agents/*.md`.
- `bash /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2/build/run_commit_lints.sh`. Expected: `commit lints passed`, and `sync_runtime_assets` reports no adapter change.
- `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2/hooks --python 3.13 --with pytest python -m pytest -q`, then `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2/hooks --python /usr/bin/python3 --with pytest python -m pytest -q`. Expected: both unchanged from the baseline you recorded. The guard and its tests gained a comment line and must still run on 3.9.

- [x] **Step 7: Commit** (the hook runs all seven lints on it)

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2 add -u
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2 commit -m "chore: cite the Claude Code guide in the 41 files that rest on it (drift R11.3)" -m "Pre-existing files are stamped @2.1.219, their true last review, and the conformance register and lint @2.1.288, so every one starts in the stale backlog that Stage 3 reviews." -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

`add -u` stages tracked files only: the 41, `NOTICE` and the test file. Check `git -C <W> status --porcelain` first: it must list exactly those 43 paths, all as modified.

---

### Task 9: Validation (Validation items 2 and 6)

**Files:** none changed. This task produces the completion report's evidence.

- [x] **Step 1: The load check (Validation 2, first bullet).** Already done (Planning record). Restate the result and the evidence path in the completion report.
- [x] **Step 2: The replay (Validation 2, second bullet).** In the full cc_guide run, `test_the_replay_flags_the_citers_of_drifted_sections_and_not_the_control` passed, not skipped. Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2/build/cc_guide --python 3.13 --with pytest python -m pytest -q -rs test_baseline.py`. Expected: all pass, no `SKIPPED` line.
- [x] **Step 3: The stale backlog (Validation 2, third bullet).** Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-43-cc-drift-stage2 --python 3.13 python build/cc_guide/cli.py check --worktree`. This is a live fetch (R6.4).
  - Its summary prints `stale citations: 41 file(s) under 21 section(s), informational`, with `subagents.tools` listing all 7 agents and `hooks.patterns` listing `hooks/README.md` and `hooks/ruff-check.sh`.
  - The exit is 1 if anything else is due (2.1.290 and later are untriaged), never 2.
  - Read `report['citing']` in the report path the summary prints, and confirm it is a mapping.
  > Deviation: the summary's lists were supersets of the plan's wording: `subagents.tools` listed the 7 agents plus `build/check_frontmatter.py`, and `hooks.patterns` listed 8 files, not two. The 41-file and 21-section totals matched, `report['citing']` was a mapping of 38 entries, and the exit was 1 (changelog releases from 2.1.290 untriaged), never 2.
- [x] **Step 4: Every existing gate (Validation 6).** Run each, and record each outcome against the baseline:
  - the build suite (+59, the 4 known failures only);
  - the cc_guide suite (+54);
  - `hooks/` on both interpreters (unchanged);
  - `build/run_commit_lints.sh` (all seven pass);
  - `uv run --python 3.13 --with pyyaml python build/check_conformance.py` (exit 0).

  `check_snippets.py skills/` (Tier 1), `check_frontmatter.py`, `check_provenance.py`, the dependency-drift test and `sync_runtime_assets.py --check` are inside the runner.

  > Deviation: counts are after the fix wave (216183b to 1000221, +18 tests): the build suite 853 passed (+77 over the 776 baseline) with the 4 known failures, cc_guide 296 (+72), hooks 274 on both interpreters, all seven commit lints passing. Task 9's own run, before the fix wave, read 835 and 278.
- [x] **Step 5: The coverage gaps (Validation 2, R4.3).** Put the Planning record's list of 23 gaps in the completion report for the owner, who decides for each whether to extend the guide (a new section, verified like any `/cc-guide verify` run) or leave it uncovered. Add any gap execution found.
- [x] **Step 6: Hygiene.**
  - `git -C <W> status --porcelain --untracked-files=normal` prints nothing.
  - No line outside `specs/` begins with a citation except the 41: `git -C <W> grep -c -E '^[[:blank:]]*(#|<!--)[[:blank:]]*cc-guide:' -- . ':(exclude)specs'` lists exactly those 41 files, `:1` each.

---

## Plan completion notes

- **Step 3, deferred items.** Log one item for the stale backlog (R11.6): it tracks itself through `lint`'s `STALE` lines and the report, so there is one item, not one per file. Its `Done when:` is that Stage 3's `files` batches have cleared it. Its text points at this plan's "Drift the sweep found" list. Also tick any earlier item this plan implemented.
- **Step 4, triage.** The backlog is over 20 open items, so the triage proposal runs.
- **Step 5, retire.** `git mv` this plan to `specs/plans/completed/`. The spec stays in `specs/`, because Stages 3–5 remain and no other live plan implements it yet. Re-point this plan's relative links, if any, for its new depth.
