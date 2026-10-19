# Agent-Skills Portability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every skill in this repo installs and runs outside Claude Code: its frontmatter passes the Agent Skills spec's checks, its license texts travel with it, its scripts declare their own dependencies and run with `uv run`, and writing-skills' advice on description openings rests on a measured baseline.

**Architecture:** The spec's four stages, in the order A, B, C, D, except that Stage D's RED baseline is taken first, before anything edits writing-skills (R2.2). Stage A (R1) rebuilds `build/check_frontmatter.py`'s key rules: spec and host key sets, value shapes, a required `license`, Codex invocation parity, a body-length warning and a `--strict` profile. Stage B (R4) puts byte-identical copies of the applicable root license files in every skill directory, enforced by `build/check_provenance.py`. Stage C (R3) gives the 15 header-less runnable scripts PEP 723 headers, rewrites every documented invocation to `uv run <path>`, declares `compatibility`, and adds a lint rule for each. Stage D (R2) edits writing-skills only as its baseline allows. Every edit block and helper script below was replayed out of this file onto a clean clone (Planning record).

**Tech Stack:** Python 3.13 through `uv run` (stdlib `ast`, `tomllib`, `argparse`; PyYAML in `check_frontmatter.py`), pytest; PEP 723 inline script metadata; bash for the one-time execution proof and the micro-test runner; Claude Code's `claude -p` for Stage D's reps; Gemini CLI and Codex CLI for the load check; `gh` for one read-only fetch.

**Spec:** `specs/agent-skills-portability-spec.md` (approved 2026-10-18): R1–R4, Sequencing, and Validation 1–6. Task 1 amends the spec where planning's measurements or the gate's answers differ from its text; your human partner approves that wording at plan review.

## Global Constraints

- **The spec's status block is not edited.** "The status-header change that records this is being landed separately, so do not edit that header." (brief; D1) It landed as `3bb71df`. Task 1's amendments start below it.
- **Push or merge nothing without the owner's go-ahead** (brief; D2).
- **The worktree.** Execute in a worktree whose branch holds this file's latest commit on `claude/intelligent-yonath-9539a3`: this plan's own worktree (`/Users/lowell/Projects/agent-skills/.claude/worktrees/intelligent-yonath-9539a3`), a worktree cut from that branch, or one cut from `main` once the owner fast-forwards or merges the branch into it. A session started from `main` before then lacks this file. Never in the shared checkout: the plan edits skills the executing session loads (writing-plans, finishing-a-development-branch, writing-skills), and `~/.claude/skills` resolves to the main checkout (spec Sequencing, "Work in a worktree"). Start the execution session with the worktree as its working directory. Every command below runs from the worktree root, and paths outside the repo are absolute. Never `cd`: a Bash `cd` persists across calls and moves the session.
- **Order.** Task 1 (amendments), Task 2 (Stage D's RED baseline, before any edit to writing-skills), Stage A (Tasks 3–7), Stage B (Tasks 8–9), Stage C (Tasks 10–13), Task 14 (Stage D's edit), Task 15 (acceptance). Each task leaves every gate green at its commit, so Stage A's rules are "green on arrival" (Sequencing) task by task.
- **Gates before every commit.** `bash build/run_commit_lints.sh` runs the nine commit lints and ends `commit lints passed`. Its `STALE` lines never fail it.
- **Test counts are deltas** (+N), never absolute totals. Each expected summary line below is what the replay printed on top of `d70e0b3`; on a later base the absolute counts may differ, the deltas may not.
- **CLAUDE.md stays under 200 lines** (check `claude-md-size`, which fails at 200). It has 199 at `d70e0b3`, and this plan adds none: Task 7 names `--strict` in an existing comment (D7), and Tasks 8 and 9 extend existing lines. Plan 52 (write-with-asd-ste100, written in parallel) adds 4 and must make room itself; plan 51 (drift automation) leaves the file alone. If another plan lands first and the check fails, stop and ask the owner where to make room (the conformance spec's rule R6 P1: trim elsewhere, never raise the limit).
- **A `# cc-guide:` citation stays last.** Fifteen SKILL.md files end their frontmatter with a `# cc-guide:` comment, the citation form that the drift-automation spec's R4 puts last. Two frontmatter edits land in such files, Task 4's metadata block (seven superpowers skills) and Task 12's `compatibility` line (`bayesian-workflow`, `track-model-experiments`, `writing-plans`), and both helper scripts insert above the citation.
- **Values copied verbatim from the spec:**
  - R1.1: `SPEC_KEYS = {name, description, license, compatibility, metadata, allowed-tools}`; `HOST_KEYS = {when_to_use, model, effort, context, disable-model-invocation}`, plus `agent` (D5).
  - R1.3: `compatibility` is "a string of 1–500 characters after stripping".
  - R1.4's metadata: `author: 'Jesse Vincent'`, `adapted_by: 'Lowell Mason'`, `source: 'https://github.com/obra/superpowers'`.
  - R1.7: "A `SKILL.md` body (the lines after the closing frontmatter `---`) over 500 lines prints one `WARN` line to stderr and does not change the exit code."
  - R3.5's sentence: "Without uv, run the same path with `python3` in an environment that has the dependencies listed in the script's header."
  - R3.6's value: `Requires uv to run bundled scripts (dependencies are declared inline); Python 3.X+.`
  - R4.1: copies are "regular files (never symlinks, which `install.py --copy` refuses) that are byte-identical to the root license files and carry the same names".
- **Helper scripts live outside the repo**, in `/tmp/portability-plan/`, never in `/tmp` itself (a stray `/tmp/struct.py` breaks `import numpy` there). They are one-time aids and are not committed.
- **Stage D's reps** run only through `run_reps.sh` (Task 2): each is a fresh `claude -p` with no tools, from a new directory outside every repository (spec Sequencing: the micro-test "runs from a session whose cwd was never this repo"). Read every reply by hand.
- **Python style:** single quotes, f-strings, named constants (clean-code rule G25); `build/` stays on Python 3.13.
- **Tick only step lines.** Some edit blocks quote writing-skills' own checklist, whose lines start `- [ ]` inside a code fence. Tick only this plan's step lines (`- [ ] **Step N…`), never a line inside a fence.
- **Commit trailer.** Each commit message ends with the executing session's own `Co-Authored-By:` line (add it as a second `-m`); subagent-authored commits keep that same line. Check with `git log -1 --format=%B`.
- **Couplings.** If `skills/write-with-asd-ste100/` exists on the execution branch, the conditional steps in Tasks 4, 8, 10, 11, 12 and 13 apply (Planning record, "Couplings with other work").
- **Another plan landed first.** Plan 52 (write-with-asd-ste100) also edits `NOTICE`, `README.md`, `CLAUDE.md` and the register (`build/cc_guide/conformance.toml`). If an edit block below no longer matches because another plan changed the text around it, read the current text, make the same change by hand, and note it as a deviation; never restore the old text.
- **document-python-package landed first** (plan 57, 2026-10-19, under D8 of that skill's spec). It adds a 39th skill and a 19th runnable script, `skills/document-python-package/scripts/preflight.py`. Plan 52's vendored `write-with-asd-ste100/scripts/ste-lint.py` is the 18th. The script already conforms: a PEP 723 header with `requires-python = '>=3.11'` and `dependencies = []`, a `uv run` invocation followed by R3.5's sentence, and a `compatibility` value that names uv. The skill's `LICENSE` copy already exists, byte-identical to the root file, so Task 8 writes the same bytes. The helpers in Tasks 10, 12 and 13 name their scripts and skills one by one, so they leave this skill alone.

## Decisions

- **D1** (owner, brief, 2026-10-18): The owner approved the design (2026-10-03) and the written spec (2026-10-18). The status-header change that records it lands separately, so this plan never edits that header. Applied in: Global Constraints, Task 1.
- **D2** (owner, brief, 2026-10-18): Push or merge nothing without the owner's go-ahead. Applied in: Global Constraints.
- **D3** (owner, brief, 2026-10-18): The JAX skills and `recommend-causal-design` have merged, so the spec's "coordinate with the in-flight JAX spec" now means this plan brings them into conformance. Applied in: Task 1 (A8), Task 8 (`recommend-causal-design`'s license copy).
- **D4** (owner, brief, 2026-10-18): The open call in the backlog item "`build/check_frontmatter.py`'s SKILL.md key set" is settled at this plan's gate: allow `agent` and `disable-model-invocation`, or record deviations. Applied in: D5.
- **D5** (owner, plan review, 2026-10-18): `build/check_frontmatter.py` accepts the `agent` key: it joins `HOST_KEYS`, its test and writing-skills' key list, amendment A1 adds it to the spec's R1.1, and `--strict` flags it like the other Claude Code keys. Applied in: Task 1 (spec amendment A1), Task 3, Task 4.
- **D6** (owner, plan review, 2026-10-18): Validation 6 governs only writing-skills' description guidance; Stage A's key-list, template and checklist edits fall outside it. Applied in: Task 1 (spec amendment A10), Task 15.
- **D7** (owner, plan review, 2026-10-18): Task 7 names `--strict` in the frontmatter lint's existing CLAUDE.md comment and adds no line. Applied in: Task 7.
- **D8** (owner, plan review, 2026-10-18): writing-skills' note carries the Codex cut that Task 14 measures when it runs, with the 2026-10-03 figures kept as history, and amendment A3 records this in the spec's R2.3. Applied in: Task 1 (spec amendment A3), Task 14.

---

## Planning record

### Facts measured while planning (2026-10-18)

- **Branches.** Planning began at `e9325de`. `main` then moved to `c3a9cf7` with two spec-only commits, the portability spec's status block (`3bb71df`) and the superpowers drift assessment (`f9ae68d`), and then to `d70e0b3`, the merge of plan 50 (lowmason/agent-skills#56, five superpowers fixes adopted from upstream). Plan 50 changed `CLAUDE.md` (4 lines added, so 199), `NOTICE` (an entry right after the drift-automation one), three superpowers skills' scripts and tests, and `systematic-debugging/SKILL.md`. This plan is based on `d70e0b3`: its edit blocks were regenerated and replayed there (Prototype and replays).
- **Skills.** 37 under `skills/`. The 13 superpowers skills lack `license`; the other 24 carry it. Fifteen end their frontmatter with a `# cc-guide:` citation line: seven superpowers skills (brainstorming, dispatching-parallel-agents, executing-plans, requesting-code-review, subagent-driven-development, writing-plans, writing-skills), `bayesian-workflow`, `track-model-experiments`, and six whose frontmatter this plan leaves alone (derive-roadmap, develop-testing-strategy, prepare-handoff, recommend-probabilistic-model, tech-debt, tune-hyperparameters). Only llm-wiki's description holds angle brackets (`'verify <page>'`). Every `metadata` value is a string. No skill sets `compatibility`, `disable-model-invocation` or `agent`, or ships `agents/openai.yaml`.
- **Bodies.** writing-skills' body is 696 lines (697 after Task 4), the only one over 500.
- **`--strict`'s set today:** `bayesian-workflow` (`effort`), `tech-debt` (`context`), `tune-hyperparameters` (`effort`), R1.8's expected three.
- **Scripts.** 17 runnable `skills/*/scripts/*.py` files (a `__main__` guard): the spec's 16 plus `writing-plans/scripts/entry_check.py`. The two `build.py` scripts carry headers; 15 do not. `tune-hyperparameters/scripts/time_series_cv.py` has no guard (a library), and no test file has one.
- **Floors.** Each changed script suite, run at 3.11, 3.12 and 3.13 with its CLAUDE.md dependencies, passes at 3.11 except two: `bayesian-workflow` (a collection error in `test_calibration_check.py`) and `track-model-experiments` (4 failed, 5 errors), because `arviz>=1.0` needs Python 3.12. `check_diagnostics.py` is stdlib-only and its own tests pass at 3.11.
- **Resolved versions:** polars 2.0.0, numpy 2.5.4, arviz 1.3.0, arviz-base 1.3.1, arviz-stats 1.3.3, arviz-plots 1.3.2, xarray 2026.9.0, scipy 1.18.1, h5netcdf 1.8.1, h5py 3.16.0, matplotlib 3.11.2. Reading a `.nc` file needs `h5py` beside `h5netcdf` (without it: "backend not available").
- **uv 0.13.1** (Homebrew) picked Python 3.14.0, the newest managed interpreter, for every headered script. A header-less script inside a project binds to that project (Task 13's control: CPython 3.10.19, then a resolution error).
- **Invocations.** 28 documented invocations of a runnable bundled script use `python`, `python3` or `uv run … python`, in 12 markdown files across 9 skills; `geographic-codes` and `classification-codes` already use `uv run`. So 11 skills run a bundled script and get R3.5's sentence and R3.6's `compatibility`. Outside `skills/`, only completed plans and specs and one deferred item use the old forms; they stay as history. `commands/` runs none of these scripts.
- **Runtimes** (real HOME, from a directory outside any repo): Gemini CLI 0.46.0 lists all 37 skills `[Enabled]`. Codex CLI 0.163.0 lists 105 skills (`skill-creator` twice), all 37 of this repo's among them; it cuts 28 of their descriptions to 316–320 characters (median 318) and shows 9 whole. The spec measured 156–164 characters with 93 listed under Codex 0.154.
- **R2.1 re-check:** all 37 descriptions name their primary trigger within their first 150 characters.
- **CLAUDE.md** has 199 lines. **CI:** `.github/workflows/lints.yml`, added by plan 41 (the commit-lints hook and CI, `acabb52`), runs the commit lints as an advisory check.
- **Compaction window** (check `compaction-window`: 5,000 tokens at 4 characters each): writing-skills' "The Iron Law" heading starts at body offset 15,436 at `d70e0b3` (unchanged since `e9325de`), 15,886 after Stage A, and 16,236 after Task 14's note. No critical-sounding heading lies between it and the two acknowledged late headings, so none crosses the window.
- **Andorra (R4.5).** Upstream is the `bayesian-workflow` skill in https://github.com/Learning-Bayesian-Statistics/baygent-skills. Its `LICENSE` is MIT, "Copyright (c) 2026 Learning Bayesian Statistics", unchanged since upstream's first commit `3681125`; at `1959ef6` (v1.5, 2026-06-07) it is 1,085 bytes, sha256 `21f3fa613e8b7130156aec53c66616d176112066d08493aaad209e495534b5f5`. This repo imported the skill on 2026-06-20 (`2d99584`); which upstream version was ported is not recorded.
- **Claude Code 2.1.302.** A smoke rep (`claude -p --model claude-opus-5-5 --tools "" --no-session-persistence --output-format json` on the prompt "Reply with the single word OK.") returned `is_error: false`, a `modelUsage` keyed `claude-opus-5-5`, and cost $0.237. No rep of Stage D's scenario ran while planning, so its first result comes at execution.

### Prototype and replays

- **Prototype.** Every change was built in task order on a throwaway clone of `e9325de` (`~/.cache/agent-skills/scratch/portability-proto`), each RED run before its implementation.
- **Patch replay.** On a second fresh clone of `e9325de`, every patch applied in plan order: each RED came out as its step predicts, and all eight commit lints passed after every task. The final tree matched the prototype's except for one stale register comment, which Task 3 now drops.
- **Re-base.** On `d70e0b3` all 111 patches matched exactly once again. Two were re-anchored for plan 50: Task 4's NOTICE entry now follows plan 50's entry, and Task 7's CLAUDE.md change extends a comment instead of adding a line (D7).
- **Plan-text replay** (on `d70e0b3`, with this file committed on top). A script lifted every edit and create block out of this file, applied them in task and step order, ran each step's command as written (with the scratch paths mapped into a sandbox), and compared each output with the expectation the step states. It skipped only the micro-test reps of Tasks 2 and 14 and the two commits that record their results (Tasks 2 and 13). Every RED and GREEN count, lint report and helper output matched; each task's commit left the tree clean, so every `git add` list is complete; and after Task 12 the tree equalled the patch replay's, outside `specs/`.
- **Suites.** The `build/` suite went from 1083 passed to 1121 (+38: +31 frontmatter, +7 provenance). Its only failures, before and after, are the 4 `test_verify_citations.py` tests that need the gitignored `build/.scratch/`. The nine changed skills' script suites kept their counts.
- **Execution proof.** Task 13's script: all 17 scripts exited 0 under Python 3.14.0; inside the hostile project the headered copy exited 0 and the header-less control exited 1 under CPython 3.10.19.
- **Load check.** Task 15's copy install into a scratch HOME: Gemini 37/37 `[Enabled]`, Codex 37/37 listed.
- **Stage D.** Both of Task 14's branches pass all eight commit lints, and a prompt built after the at-most-3/5 edit carries the note and the checklist line. Task 14's live Codex measurement reproduced the figures above.

### Settled defaults (your human partner reviews each)

- **DF1. One plan, not one per stage.** `check_frontmatter.py` changes in Stages A and C, NOTICE in all four, CLAUDE.md in A and B; one plan keeps those edits in sequence.
- **DF2. Stage D's RED reps run first** (Task 2), before Stage A touches writing-skills, so R2.2's "before any edit" holds in time and in text. The prompt builder reads the working tree, so a GREEN arm (Task 14, if due) quotes the text that ships. If wrong: build the RED prompt from `git show d70e0b3:skills/writing-skills/SKILL.md` instead and run Stage D last.
- **DF3. Script floors** (R3.3): `>=3.12` for `calibration_check.py`, `diagnose_model.py` and `compare_experiments.py`, which import ArviZ 1.x; `>=3.11` for the other twelve, `check_diagnostics.py` included, since its suite's 3.11 failure is attributable to `calibration_check.py`.
- **DF4. Dependency floors** at the major version resolved on 2026-10-18 (R3.4): `polars>=2.0` for the three new polars headers (the two `build.py` headers keep `polars>=1.0`, untouched), `numpy>=2.0`, `arviz>=1.0`, `arviz-base>=1.0`, `xarray>=2026.0`, `scipy>=1.0`. Where the code states a higher minimum, the code wins: `arviz-plots>=1.1` and `arviz-stats>=1.1` in `calibration_check.py`.
- **DF5. Declared beyond the imports:** `h5netcdf>=1.0` and `h5py>=3.0` for the three `.nc` readers (R3.4's backend clause; the execution proof fails without `h5py`); `matplotlib>=3.0` for `calibration_check.py`'s `--save-plots`, which the skill's documented invocation uses, and its `ImportError`-guarded imports, which that path needs.
- **DF6. Vendored scripts** are exempt from the two header rules through `VENDORED_SCRIPTS` (empty today); the invocation rule still applies to them.
- **DF7. The invocation rule flags any `python` or `python3` right before a resolving path,** `uv run --python 3.13 --with … python <path>` included, since that form ignores the header. This is stricter than R3.7's "bare `python`" and matches R3.5's single form.
- **DF8. Where the fallback sentence goes:** once per skill, after its first fenced invocation; where the first mention is inline, right after that sentence (writing-plans' "Save plans to", llm-wiki's step 2), or, for design-architecture, after the Scaffolder block that documents the script. llm-wiki's INSTALL.md says the same in its Prerequisites in its own words, keeps `python3` for `install.py`, and loses a stale "test suite, below" clause.
- **DF9. Prose floors are aligned, not removed** (R3.3): "Python ≥ 3.9" becomes "Python ≥ 3.11" in `recommend-visualization` and `recommend-probabilistic-model`, and llm-wiki's INSTALL.md moves from 3.12 to 3.11.
- **DF10. Left as they are:** the scripts' own docstring usage lines and `bootstrap_wiki.py`'s printed next step (`python3 <root>/scripts/lint_wiki.py`). R3.5 covers skill markdown, and `python3` still runs these stdlib scripts.
- **DF11. `recommend-causal-design`'s skill `LICENSE`,** today a copy of the sources file, is renamed to `LICENSE-causal-design-sources`; a copy of the root `LICENSE` takes its place, and its three links re-point.
- **DF12. License copies are exempt from the register's `orphan-bundled-file` check** (`LICENSE*`): nothing names them.
- **DF13. An unparseable `agents/openai.yaml` is reported** whatever `disable-model-invocation` says (R1.6).
- **DF14. Andorra: outcome 1** (R4.5; facts above). Root `LICENSE-andorra` is upstream's text verbatim; NOTICE quotes its copyright line and composes nothing.
- **DF15. The llm-wiki installed copies** in each wiki lack headers until the owner refreshes them after merge (`bootstrap_wiki.py "$LLM_WIKI_ROOT" --check`, then `--force`). Until then they still run under `uv run`, but one run from inside a Python project binds to it.
- **DF16. Stage D's reps:** model pinned to `claude-opus-5-5` (the model planning sessions write skills with), `--max-budget-usd 0.50` each, about $1–3 in all. Scenario and pass rule as Task 2 pre-registers them.
- **DF17. NOTICE** gains an entry for each superpowers file this plan changes: Task 4 (metadata, writing-skills' key list), Task 11 (writing-plans' and finishing-a-development-branch's invocations), Task 12 (their `compatibility`), Task 14 (writing-skills' note).
- **DF18. Validation 5 runs before merge,** against a scratch HOME holding an `install.py codex --copy` of the branch's skills, since the real `~/.agents/skills` links the main checkout. Gemini reads the same directory.
- **DF19. The Discovery Workflow item stays in the backlog:** Validation 6, even as amended, lets Stage D change only description guidance, and that rewording needs its own micro-test.
- **DF20. The register's Stage D debts move to a rewrite item.** `writing-skills-guide-gaps` and `writing-skills-late-critical-headings` are `tracked_in` "portability Stage D", and `writing-skills-tdd-for-docs` revisits "When portability Stage D revises writing-skills". R2.3 allows Stage D a note and at most one checklist line, so it closes none of those gaps. Task 14 re-points both `tracked_in` values to a new deferred item, "Split and rewrite writing-skills against the guide", which takes in the spec's out-of-scope "Splitting writing-skills"; sets the deviation's revisit to that rewrite; and, where the gap's reason says Stage D verifies or drops writing-skills' `@` loading claim, says the rewrite does. If wrong: leave all three on Stage D, which will have finished.

### Questions settled at plan review

The owner answered all four on 2026-10-18, each with option (a): Q1 as D5, Q2 as D6, Q3 as D7 and Q4 as D8. The questions stay here as asked.

- **Q1. The `agent` key** (D4; backlog "`build/check_frontmatter.py`'s SKILL.md key set"). R1.1 already lists `disable-model-invocation`, so the open call is `agent`, which names the agent type a `context: fork` skill runs on. No skill sets it.
  - (a) Allow it. Amendment A1 adds it to R1.1; Tasks 3 and 4 put it in `HOST_KEYS`, its test and writing-skills' key list; `--strict` flags it like the other host keys. **Recommended:** the guide documents it, and the item's own closure condition pairs allowing it with the key list and tests, as Tasks 3 and 4 do.
  - (b) Record a deviation. Drop A1; Task 3's `HOST_KEYS` and test omit `agent`, writing-skills' sentence drops its `agent` clause, and the register gains a `[[exception]]` with `type = 'deviation'`, `id = 'skill-agent-key-rejected'`, `sections = ['skills.frontmatter']`, `artifacts = ['skills/*/SKILL.md']`, guide `A context: fork skill may name its agent type with agent.` and reason `No skill forks to a named agent, so the lint keeps the key out until one needs it.`
- **Q2. Validation 6 against Stage A's writing-skills edits.** Validation 6 says writing-skills changes "only as R2.3's outcome branch allows", but Stage A must update writing-skills' frontmatter key list (`license` required, `disable-model-invocation` and `agent` accepted), or the skill misstates the lint. (a) Amend Validation 6 to cover R2's description guidance only (A10). **Recommended.** (b) Leave writing-skills' key list stale.
- **Q3. Where `--strict` goes in CLAUDE.md** (R1.9; the conformance spec's rule R6 P1 leaves the room to the owner). Plan 50 left CLAUDE.md at 199 lines and the `claude-md-size` check fails at 200, so R1.9's planned command line no longer fits.
  - (a) Name it in the existing comment: Task 7 extends the frontmatter lint's comment with `; add --strict to the first, a report and not a gate, when preparing a claude.ai upload or a spec-only validator run`, and adds no line. **Recommended:** nothing else in CLAUDE.md moves, and that comment is R1.9's "one line on when to use it".
  - (b) Add `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py --strict` as its own line and remove a line the owner names; Task 7 then makes both edits.
- **Q4. R2.3's Codex figures.** R2.3 names the 2026-10-03 cut (156–164 characters, 93 skills, Codex 0.154); on 2026-10-18 it is 316–320, 105 skills, Codex 0.163. (a) Amend R2.3 (A3): the note carries the cut re-measured when it is written (Task 14 Step 1), with the old figures kept as history. **Recommended.** (b) Write the spec's figures as they stand.

The other amendments (A2, A4–A9, A11) correct counts and facts the spec states as of 2026-10-03; they are approved with the plan.

### Couplings with other work

- **write-with-asd-ste100**, plan 52 (committed as `2b93c70` on branch `claude/elegant-bassi-20474d`, worktree `elated-taussig-004443`, based on `e9325de`). If it lands first, these conditional steps apply. They are also in the shared note `portability-plan-couplings-with-asd-ste100.md`, and plan 52's own Couplings (a), (c) and (e) name the same points:
  1. Task 4: its SKILL.md needs `license`.
  2. Task 8: its skill `LICENSE` must equal the root `LICENSE`, and the sources file travels as `LICENSE-write-with-asd-ste100-sources`, with a `BUNDLED_LICENSES` row. Plan 52's Q3 lets its owner adopt this form early; Task 8's conditional step works either way.
  3. Task 10: `skills/write-with-asd-ste100/scripts/ste-lint.py`, copied byte for byte from upstream, joins `VENDORED_SCRIPTS`.
  4. Task 11: plan 52 runs the linter as `python3 <this-skill-dir>/scripts/ste-lint.py --json` on purpose, so that it also runs under `/usr/bin/python3` (its DF18), and this plan's invocation lint flags that call. A header-less script under `uv run` binds to any Python project around it (Task 13's control fails that way), so `uv run` is no safe default for a vendored script. Stop and ask the owner: exempt `VENDORED_SCRIPTS` from the invocation rule too, or run the linter with `uv run`.
  5. Task 12: only if the owner chose `uv run`, the skill's `compatibility` is the house string with 3.X = 3.9, the lowest Python plan 52 verifies `--selftest` under (`/usr/bin/python3` 3.9.6). "Dependencies are declared inline" is loose for a header-less script; the owner may word it otherwise (the lint needs only `uv`).
  6. Task 13: `r38.sh` also runs `ste-lint.py --selftest`.
  7. Tasks 2 and 14: once the asd rule is installed in `~/.claude/rules/`, it loads in every rep, in both arms; the record notes it.

  If this plan lands first, plan 52 must meet these rules, or the commit lints fail on its arrival; its Task 1 checks for that and stops to ask. Plan 52 also adds 4 CLAUDE.md lines to a file that already has 199. The owner settles the order at integration.
- **Plan 51**, the drift-automation plan (worktree `suspicious-ptolemy-161633`), edits `build/cc_guide/cli.py`, `settle.py`, their tests, `build/CLAUDE.md` and the `/cc-guide` skill: no file in common with this plan, and it leaves `CLAUDE.md` alone.
- **Drift-automation citations.** The fifteen SKILL.md citation lines (the drift-automation spec's R4) are on `main`, hence the "citation stays last" constraint.
- **Plan 50 and the superpowers drift assessment** (`specs/superpowers-drift-spec.md`). Plan 50 adopted three of its findings and merged before this plan was written (Facts, "Branches"). A later adoption of upstream text into a superpowers skill keeps this plan's frontmatter, license copies and invocations, and NOTICE records both changes.
- **Backlog items.**
  - "`build/check_frontmatter.py`'s SKILL.md key set" (`specs/deferred_items.md`, section cc-guide-files-backlog) closes with D5; it is ticked at completion.
  - "Gate or make manual-only the four ungated side-effecting skills" (section 35-claude-code-guide-conformance, from plan 35's audit of the skills against the Claude Code guide) waits on Stage A. After Task 3, `disable-model-invocation` passes the lint, and after Task 5, R1.6 requires a paired `agents/openai.yaml`; completion adds that note to the item.
  - "writing-skills' Discovery Workflow" stays open (DF19).
  - "Pin the `_late_headings` parse with a positive control" (section 48-compaction-late-heading-ratchet, from plan 48's review) is revisited only "if portability Stage D empties a row while its exception stays". Task 14's note lands above the window's edge and no row changes, so it is not triggered.

### Plan ID

`entry_check.py` printed `next free: 52` early on 2026-10-18. Re-run right before writing, it found 52 taken by the write-with-asd-ste100 plan (`52-write-with-asd-ste100.md`, committed as `2b93c70` on branch `claude/elegant-bassi-20474d`), so this plan is 53. Re-run with this file in place, it reports `highest: 53` (this file), `next free: 54` and `collisions: none`. Plan 50 is retired on `main`, and plan 51, the drift-automation plan, is in worktree `suspicious-ptolemy-161633`. `main` and `origin/main` are both `d70e0b3`.

### CLAUDE.md line budget

199 lines at `d70e0b3` (plan 50 added 4), and still 199 after this plan: Task 7 extends a comment instead of adding a line (D7), and Tasks 8 and 9 extend the provenance paragraph and a provenance bullet. Plan 52 (write-with-asd-ste100) adds 4, so it must make room or the owner settles the order at integration.

---

### Task 1: Spec amendments (A1–A11)

**Files:**
- Modify: `specs/agent-skills-portability-spec.md` (R1.1, R2.1, R2.3, R3.1, R3.5, R3.7, R3.8, Sequencing, Validation 4 and 6, Out of scope)

**Interfaces:**
- Consumes: decisions D5, D6 and D8.
- Produces: a spec whose counts and rules match Tasks 2–15.

Each edit is tagged `(owner, plan 53, 2026-10-18)`; the status block stays untouched (D1). A1, A10 and A3 carry the plan-review decisions D5, D6 and D8.

- [ ] **Step 1: Apply the edits,** each an exact replace of the block shown.

**A1 (Q1, option a).** R1.1: `agent` joins `HOST_KEYS`.

**Edit `specs/agent-skills-portability-spec.md`: replace**

```markdown
- `HOST_KEYS = {when_to_use, model, effort, context, disable-model-invocation}`
```

**with**

```markdown
- `HOST_KEYS = {when_to_use, model, effort, context, disable-model-invocation, agent}`.
  `agent`, the agent type a `context: fork` skill runs on, joins the set
  (owner, plan 53, 2026-10-18).
```

**A2.** R2.1: the 2026-10-18 re-check of the descriptions.

**Edit `specs/agent-skills-portability-spec.md`: replace**

```markdown
canonical use. All 32 descriptions pass as of 2026-10-03. The closest calls are
```

**with**

```markdown
canonical use. All 32 descriptions pass as of 2026-10-03, and all 37 pass on
2026-10-18 (owner, plan 53, 2026-10-18). The closest calls are
```

**A3 (Q4).** R2.3: the note carries the cut measured when it is written.

**Edit `specs/agent-skills-portability-spec.md`: replace**

```markdown
  description when its listing exceeds its budget; the measured cut (156–164
  characters with 93 skills listed, Codex 0.154, 2026-10-03); and how to re-measure
```

**with**

```markdown
  description when its listing exceeds its budget; the measured cut, re-taken when
  the note is written (on 2026-10-18: 316–320 characters with 105 skills listed,
  Codex 0.163; on 2026-10-03: 156–164 with 93, Codex 0.154; owner, plan 53,
  2026-10-18); and how to re-measure
```

**A4.** R3.1: 17 runnable scripts, 15 of which gain a header.

**Edit `specs/agent-skills-portability-spec.md`: replace**

```markdown
with a `__main__` guard. There are 16. Fourteen gain a header:
```

**with**

```markdown
with a `__main__` guard. There are 17: `writing-plans/scripts/entry_check.py`
came after 2026-10-03. Fifteen gain a header (owner, plan 53, 2026-10-18):
```

**A4, continued.** R3.1's list.

**Edit `specs/agent-skills-portability-spec.md`: replace**

```markdown
- `writing-plans`: `deferred_stats.py`
```

**with**

```markdown
- `writing-plans`: `deferred_stats.py`, `entry_check.py`
```

**A5.** R3.5: the count.

**Edit `specs/agent-skills-portability-spec.md`: replace**

```markdown
  of the 16 scripts uses the form `uv run <path> [args]`, replacing `python`,
  `python3`, `uv run --no-project --python 3.13 python`, and
  `uv run --python 3.13 --with … python`.
```

**with**

```markdown
  of the 17 scripts uses the form `uv run <path> [args]`, replacing `python`,
  `python3`, `uv run --no-project --python 3.13 python`, and
  `uv run --python 3.13 --with … python` (owner, plan 53, 2026-10-18).
```

**A6.** R3.7: the example named a file removed on 2026-10-11.

**Edit `specs/agent-skills-portability-spec.md`: replace**

```markdown
  the next line). A path that does not resolve to a bundled script, such as
  `writing-skills/anthropic-best-practices.md`'s teaching example
  `scripts/migrate.py`, is not flagged.
```

**with**

```markdown
  the next line). A path that does not resolve to a bundled script, such as a
  teaching example's `scripts/migrate.py` in a skill that bundles no such
  script, is not flagged. (The example named here before,
  `writing-skills/anthropic-best-practices.md`, was removed on 2026-10-11;
  owner, plan 53, 2026-10-18.)
```

**A7.** R3.8: the count.

**Edit `specs/agent-skills-portability-spec.md`: replace**

```markdown
  `/tmp` itself), each of the 16 scripts runs `uv run <absolute-path>` on a
  minimal real input that exercises its main code path.
```

**with**

```markdown
  `/tmp` itself), each of the 17 scripts runs `uv run <absolute-path>` on a
  minimal real input that exercises its main code path (owner, plan 53, 2026-10-18).
```

**A8.** Sequencing: the JAX skills and `recommend-causal-design` have merged.

**Edit `specs/agent-skills-portability-spec.md`: replace**

```markdown
- **Coordinate with the in-flight JAX spec.** `specs/jax-deep-learning-skills.md`
  is being implemented on `codex/jax-deep-learning-skills` and defines three
  skills (`skills/deep-learning` is on that branch as of 2026-10-03).
  R1.4's required `license`, R3's header and invocation rules, and R4's per-skill
  license copies apply to them too. Whichever branch merges second brings the
  other's skills into conformance in the same merge, or the new lints fail on
  arrival.
```

**with**

```markdown
- **The JAX skills and `recommend-causal-design` have merged.** They are in
  scope like every other skill: R1.4's required `license`, R3's header and
  invocation rules, and R4's per-skill license copies apply to them. All four
  already carry `license` and `metadata`, none bundles a runnable script, and
  `recommend-causal-design`'s copy of its sources license takes the root file's
  name (R4.1) (owner, plan 53, 2026-10-18).
```

**A9.** Validation 4: the count.

**Edit `specs/agent-skills-portability-spec.md`: replace**

```markdown
4. R3.8's execution proof is recorded for all 16 scripts.
```

**with**

```markdown
4. R3.8's execution proof is recorded for all 17 scripts (owner, plan 53, 2026-10-18).
```

**A10 (Q2).** Validation 6: R2 governs writing-skills' description guidance only.

**Edit `specs/agent-skills-portability-spec.md`: replace**

```markdown
6. R2.2's red-baseline file exists, and `writing-skills` changed only as R2.3's
   outcome branch allows.
```

**with**

```markdown
6. R2.2's red-baseline file exists, and `writing-skills`' description guidance
   changed only as R2.3's outcome branch allows. Stage A's updates to its
   frontmatter key list, template and checklist, which keep it accurate about
   what `check_frontmatter.py` accepts, are outside R2 (owner, plan 53, 2026-10-18).
```

**A11.** Out of scope: the repo has an advisory CI.

**Edit `specs/agent-skills-portability-spec.md`: replace**

```markdown
- **Skill security scanning** (e.g. Cisco's `skill-scanner`). The repo has no CI.
```

**with**

```markdown
- **Skill security scanning** (e.g. Cisco's `skill-scanner`). The repo's only CI,
  `.github/workflows/lints.yml` (plan 41), runs the commit lints as an advisory
  check (owner, plan 53, 2026-10-18).
```

- [ ] **Step 2: Check.** Run `grep -c 'plan 53' specs/agent-skills-portability-spec.md`. Expected: `11`, one per amendment (A4's list edit carries no tag), one fewer for each amendment dropped at review. Run `sed -n '3p' specs/agent-skills-portability-spec.md`. Expected: `**Status: APPROVED (2026-10-18).** The owner approved the design on 2026-10-03`.
- [ ] **Step 3: Gates and commit.**

```bash
bash build/run_commit_lints.sh
```

```bash
git add specs/agent-skills-portability-spec.md
```

```bash
git commit -m "docs(specs): amend the portability spec for plan 53"
```

---

### Task 2: Stage D's RED baseline (R2.2), before any edit to writing-skills

**Files:**
- Create: `specs/red-baseline-description-openings-<run-date>.md`, where `<run-date>` is the day the reps run (`YYYY-MM-DD`)
- Scratch, outside every repository: `/tmp/portability-stage-d/kit/` (three files) and `/tmp/portability-stage-d/red/` (the reps)

**Interfaces:**
- Produces: the RED verdict, n of 5, which picks Task 14's branch (R2.3: at least 4/5, the note alone; at most 3/5, the note, a checklist line and a GREEN arm). Task 14 reuses the kit.

- [ ] **Step 1: Run this task before Task 3,** the first task that edits `skills/writing-skills/SKILL.md`. Record the background that loads in every rep: run `claude --version` and `ls ~/.claude/rules/`. If `write-with-asd-ste100.md` is there, the asd rule loads in every rep, both arms.
- [ ] **Step 2: Create the kit.**

**Create `/tmp/portability-stage-d/kit/build_prompt.py`:**

```python
'''Build the description micro-test prompt (portability R2.2, R2.3).

Usage: uv run --no-project --python 3.13 python build_prompt.py <worktree> <out-file>
The guidance is writing-skills' description text as it stands in the worktree:
the frontmatter bullets, Skill Discovery Optimization sections 1 and 2, the
Token Efficiency section's description bullet, and the checklist's description
items. The RED arm runs it before any edit to writing-skills; a GREEN arm runs
it again after the edit, so it quotes the text that ships.
'''
import sys
from pathlib import Path

SCENARIO = '''pg-slow-query diagnoses slow PostgreSQL queries. It applies when any of these happen:
1. a dashboard or API endpoint got slower after a deploy;
2. pg_stat_statements shows a query's mean execution time rising;
3. the connection pool runs out, or clients see "too many connections";
4. autovacuum falls behind and tables bloat;
5. EXPLAIN ANALYZE shows a sequential scan on a large table, or row estimates far from the actual counts;
6. sessions wait on locks, or the log says "deadlock detected";
7. a migration added an index that the planner does not use;
8. a read replica lags the primary;
9. queries time out only at production data volumes.
The primary trigger, the case the skill exists for, is number 5.'''
TEMPLATE = '''You are writing the frontmatter description for a new agent skill. Follow this
guidance from the skill-authoring guide you work from:

<guidance>
{guidance}
</guidance>

The skill:

{scenario}

Reply with the description text only: no YAML key, no quotation marks, no commentary.
'''


def between(text: str, start: str, end: str, *, include_end: bool = False) -> str:
    a = text.index(start)
    b = text.index(end, a) + (len(end) if include_end else 0)
    return text[a:b]


def guidance(text: str) -> str:
    frontmatter = between(text, '**Frontmatter (YAML):**', '  - Keep under 500 characters if possible\n',
                          include_end=True)
    sdo = between(text, '## Skill Discovery Optimization (SDO)', '### 3. Descriptive Naming')
    tier = between(text, '- `description` (always resident):', '- SKILL.md body (loaded on trigger)')
    items = between(text, '- [ ] Description starts with "Use when..."', '- [ ] Clear overview')
    return (f'{frontmatter}\n{sdo.rstrip()}\n\nFrom the Token Efficiency section:\n{tier.rstrip()}'
            f'\n\nFrom the skill creation checklist:\n{items.rstrip()}')


if __name__ == '__main__':
    worktree, out = Path(sys.argv[1]), Path(sys.argv[2])
    text = (worktree / 'skills' / 'writing-skills' / 'SKILL.md').read_text()
    out.write_text(TEMPLATE.format(guidance=guidance(text), scenario=SCENARIO))
    print(f'wrote {out}')
```

**Create `/tmp/portability-stage-d/kit/run_reps.sh`:**

```bash
#!/bin/bash
# Run N decision-only reps of a prompt, each a fresh `claude -p` with no tools,
# from a new directory outside every repository (isolation Channels 1-5).
# Usage: run_reps.sh <prompt-file> <new-out-dir> <n>
set -u
PROMPT="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"; OUT="$2"; N="$3"
[ -e "$OUT" ] && { echo "refusing: $OUT exists"; exit 2; }
mkdir -p "$OUT/run" && cd "$OUT/run" || exit 2
git rev-parse --show-toplevel > /dev/null 2>&1 && { echo "refusing: $OUT/run is inside a git repository"; exit 2; }
for i in $(seq 1 "$N"); do
  claude -p --model claude-opus-5-5 --tools "" --no-session-persistence --output-format json \
    --max-budget-usd 0.50 < "$PROMPT" > "$OUT/rep$i.json" 2> "$OUT/rep$i.err"
  echo "rep$i exit=$?"
done
```

**Create `/tmp/portability-stage-d/kit/show_reps.py`:**

```python
'''Print each rep's reply and the verbatim first 150 characters of its description.

Usage: uv run --no-project --python 3.13 python show_reps.py <out-dir>
Normalizes as a listing renders: strips a stray description: key and quotes, then
collapses whitespace. The keyword column is a reading aid; the verdict is read by hand.
'''
import json
import re
import sys
from pathlib import Path

PREFIX = 150
AID = re.compile(r'explain|sequential scan|seq scan|row estimate|misestimat|estimated row', re.I)


def normalize(reply: str) -> str:
    text = re.sub(r'^\s*description:\s*', '', reply.strip(), flags=re.I)
    return ' '.join(text.strip('\'"').split())


for path in sorted(Path(sys.argv[1]).glob('rep*.json'), key=lambda p: int(p.stem[3:])):
    data = json.loads(path.read_text() or '{}')
    desc = normalize(str(data.get('result', '')))
    head = desc[:PREFIX]
    print(f"== {path.stem}: is_error={data.get('is_error')} cost=${data.get('total_cost_usd', 0):.3f} "
          f"chars={len(desc)} aid={'yes' if AID.search(head) else 'no'}")
    print(f'   first {PREFIX}: {head!r}')
    print(f'   reply: {data.get("result", "")!r}')
```

Run `chmod +x /tmp/portability-stage-d/kit/run_reps.sh`.

- [ ] **Step 3: Pre-register the pass rule.** Copy it into the record (Step 7) before reading any reply:
  - **PASS:** the description's first 150 characters, as `show_reps.py` normalizes it (a stray `description:` key and quotes stripped, whitespace collapsed), name trigger 5: `EXPLAIN` or `EXPLAIN ANALYZE` output, a sequential scan, or row estimates far from the actual counts. Naming only the topic, slow PostgreSQL queries, does not pass.
  - **FAIL:** a description whose first 150 characters do not.
  - **VOID:** no description (a non-zero exit, `is_error: true`, a refusal or a question), or text other than the description first, so its start is unclear. Re-run each VOID rep, at most two extra reps in all, and record every rep.
  - `show_reps.py`'s `aid=` column is a reading aid. The verdict is read.
- [ ] **Step 4: Build the prompt.** Run `uv run --no-project --python 3.13 python /tmp/portability-stage-d/kit/build_prompt.py . /tmp/portability-stage-d/red-prompt.txt`. Expected: `wrote /tmp/portability-stage-d/red-prompt.txt`. For the record, run `shasum -a 256 /tmp/portability-stage-d/red-prompt.txt` and `git rev-parse --short HEAD`.
- [ ] **Step 5: Run the five reps,** in the background (each takes up to a minute): `/tmp/portability-stage-d/kit/run_reps.sh /tmp/portability-stage-d/red-prompt.txt /tmp/portability-stage-d/red 5`. Expected: `rep1 exit=0` through `rep5 exit=0`; a non-zero exit is a VOID rep.
- [ ] **Step 6: Read.** Run `uv run --no-project --python 3.13 python /tmp/portability-stage-d/kit/show_reps.py /tmp/portability-stage-d/red`. Read each full reply and settle its verdict by Step 3's rule. `run_reps.sh` refuses an existing directory, so run a VOID rep's replacement into `/tmp/portability-stage-d/red-extra` (n = 1 or 2) and record it as rep6 or rep7.
- [ ] **Step 7: Write the record** at `specs/red-baseline-description-openings-<run-date>.md`, in this form, with the measured values in place of each angle-bracketed slot:

````markdown
# RED baseline — description openings for `writing-skills`

**Date:** <run-date> · **Status:** RED complete: <n>/5, so R2.3's <at least 4/5 | at most 3/5> branch applies. <GREEN not needed. | GREEN: see below.>
**Governs:** which branch of `specs/agent-skills-portability-spec.md` R2.3 applies to `writing-skills`' description guidance (plan 53, Tasks 2 and 14).

> ⚠️ Quarantine this file during any later micro-test of writing-skills.
> It names the scenario and the pass rule (Channel 1).

## Method

- Five reps, each a fresh `claude -p --model claude-opus-5-5 --tools "" --no-session-persistence --output-format json --max-budget-usd 0.50`, run by `run_reps.sh` from `/tmp/portability-stage-d/red/run`, a new directory outside every repository (R2.2). Claude Code <version>.
- The guidance is writing-skills' frontmatter bullets, Skill Discovery Optimization sections 1 and 2, the Token Efficiency section's `description` bullet and the checklist's description items, as they stood at `<sha>`, before any edit (`build_prompt.py`; prompt sha256 `<hash>`).
- Background, the same in every arm: `~/.claude/CLAUDE.md`; the rules in `~/.claude/rules/` (<files>); the SessionStart hooks' explanatory and learning output-style instructions. With `--tools ""` a rep reads no file and loads no skill; outside every repository it gets no project CLAUDE.md and no auto-memory.
- Pass rule, registered before any reply was read: <Step 3's rule>.

## Scenario

<build_prompt.py's SCENARIO, verbatim, in a text fence>

## Result

| Rep | First 150 characters, verbatim | Verdict |
|---|---|---|
| rep1 | <prefix> | <PASS, FAIL or VOID> |

**<n>/5 pass.**

## Disposition

<At least 4/5: Task 14 adds only R2.3's factual note. At most 3/5: Task 14 adds the note and the checklist line, then runs the GREEN arm, recorded below.>
````

- [ ] **Step 8: Gates and commit.**

```bash
bash build/run_commit_lints.sh
```

```bash
git add specs/red-baseline-description-openings-<run-date>.md
```

```bash
git commit -m "docs(specs): RED baseline for description openings (portability R2.2)"
```

---

### Task 3: Frontmatter key sets and value shapes (R1.1–R1.3, R1.5)

**Files:**
- Modify: `build/check_frontmatter.py` (module docstring; `ALLOWED_KEYS` becomes `SPEC_KEYS` and `HOST_KEYS`; new `_check_value_shapes`; `check_skill`)
- Test: `build/test_check_frontmatter.py` (+4)
- Modify: `skills/llm-wiki/SKILL.md` (its description), `skills/writing-skills/SKILL.md` (the optional-keys bullet), `build/cc_guide/conformance.toml` (two comments)

**Interfaces:**
- Produces, in `check_frontmatter.py`: `SPEC_KEYS: frozenset[str]`; `HOST_KEYS: frozenset[str]`, which Task 7's `strict_violations` reads; `COMPATIBILITY_CAP = 500`; `ANGLE_BRACKET_RE`; `_check_value_shapes(sk: Path, fm: dict) -> list[str]`.

- [ ] **Step 1: Write the failing tests.**

**Edit `build/test_check_frontmatter.py`: insert before the line `def make_agent(tmp_path: Path, name: str, description: str) -> Path:`:**

```python
def test_spec_and_host_keys_are_allowed(tmp_path):
    # Portability R1.1: the spec's six fields and the host extensions this repo
    # allows. disable-model-invocation is false here: true needs Codex's policy
    # file (R1.6), which a later test covers.
    d = make_skill(tmp_path, 'keyed-skill',
                   'name: keyed-skill\ndescription: Use when testing.\nlicense: MIT\n'
                   'compatibility: Requires uv.\nmetadata:\n  author: Someone\nallowed-tools: Read\n'
                   'when_to_use: Testing.\ncontext: fork\nagent: Explore\n'
                   'disable-model-invocation: false')
    assert check_skill(d) == []


def test_metadata_must_map_strings_to_strings(tmp_path):
    # Portability R1.2. An unquoted version: 1.0 parses as a float.
    d = make_skill(tmp_path, 'meta-skill',
                   'name: meta-skill\ndescription: Use when testing.\nmetadata:\n  version: 1.0')
    assert check_skill(d) == [
        f"{d / 'SKILL.md'}: metadata must map strings to strings (quote a value such as version: \"1.0\")"]
    listed = make_skill(tmp_path, 'meta-list',
                        'name: meta-list\ndescription: Use when testing.\nmetadata: [a, b]')
    assert len(check_skill(listed)) == 1


def test_compatibility_must_be_a_string_of_1_to_500_characters(tmp_path):
    # Portability R1.3, both edges: 500 passes, 501 and a blank value fail.
    ok = make_skill(tmp_path, 'compat-ok',
                    "name: compat-ok\ndescription: Use when testing.\ncompatibility: '" + 'x' * 500 + "'")
    assert check_skill(ok) == []
    msg = 'compatibility must be a string of 1-500 characters'
    for i, value in enumerate(["'" + 'x' * 501 + "'", "'   '", '42']):
        d = make_skill(tmp_path, f'compat-bad-{i}',
                       f'name: compat-bad-{i}\ndescription: Use when testing.\ncompatibility: {value}')
        assert check_skill(d) == [f"{d / 'SKILL.md'}: {msg}"], value


def test_angle_brackets_in_a_description_are_rejected(tmp_path):
    # Portability R1.5: claude.ai rejects < and > in name and description.
    d = make_skill(tmp_path, 'angle-skill',
                   "name: angle-skill\ndescription: \"Use when asked to 'verify <page>'.\"")
    assert check_skill(d) == [f"{d / 'SKILL.md'}: description contains < or >"]


```

- [ ] **Step 2: Run them to see them fail.** Run `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_frontmatter.py`. Expected: `4 failed, 41 passed`, the four new tests.
- [ ] **Step 3: Implement.**

**Edit `build/check_frontmatter.py`: replace**

```python
'''Frontmatter and bundled-path lint for every skill in the repo (Gate A pattern).

Per <skill>/SKILL.md: the frontmatter must parse as YAML (catches unquoted-
scalar breakage), name must equal the directory name (<=64 chars, lowercase
letters/digits/hyphens), description must be present and <=1024 chars (Agent
Skills spec cap), keys must be spec-valid, context must be in CONTEXT_VALUES,
model must not be haiku or a claude-haiku-* ID (not portable across providers), and every
relative markdown-link target plus every backticked references/ or scripts/
path must exist.
```

**with**

```python
'''Frontmatter and bundled-path lint for every skill in the repo (Gate A pattern).

Per <skill>/SKILL.md:
- the frontmatter parses as YAML (catches unquoted-scalar breakage);
- name equals the directory name (<=64 chars, lowercase letters/digits/hyphens);
- description is present and <=1024 chars (the Agent Skills spec cap);
- every key is an Agent Skills spec key (SPEC_KEYS) or a host extension this
  repo allows (HOST_KEYS);
- name and description contain no < or >; metadata maps strings to strings;
  compatibility is a string of 1-500 characters;
- context is in CONTEXT_VALUES, and model is not haiku or a claude-haiku-* ID
  (not portable across providers);
- every relative markdown-link target and every backticked references/ or
  scripts/ path exists.
```

**Edit `build/check_frontmatter.py`: replace**

```python
ALLOWED_KEYS = {'name', 'description', 'license', 'allowed-tools', 'metadata',
                'when_to_use', 'model', 'effort', 'context', 'compatibility'}
```

**with**

```python
# The Agent Skills spec's fields (agentskills.io/specification), which every
# runtime that implements the spec accepts.
SPEC_KEYS = frozenset({'name', 'description', 'license', 'compatibility', 'metadata',
                       'allowed-tools'})
# Claude Code extensions this repo allows beside them. Gemini CLI and Codex load
# a skill that carries one; claude.ai uploads and spec-only validators reject
# them, which is what --strict checks.
HOST_KEYS = frozenset({'when_to_use', 'model', 'effort', 'context',
                       'disable-model-invocation', 'agent'})
# The spec caps compatibility at 500 characters.
COMPATIBILITY_CAP = 500
ANGLE_BRACKET_RE = re.compile(r'[<>]')
```

**Edit `build/check_frontmatter.py`: replace**

```python
    errs += _check_model_pin(sk, fm)
    for key in fm:
        if key not in ALLOWED_KEYS:
            errs.append(f'{sk}: unknown frontmatter key {key!r}')
```

**with**

```python
    errs += _check_model_pin(sk, fm)
    errs += _check_value_shapes(sk, fm)
    for key in fm:
        if key not in SPEC_KEYS | HOST_KEYS:
            errs.append(f'{sk}: unknown frontmatter key {key!r}')
```

**Edit `build/check_frontmatter.py`: insert before the line `def check_skill(skill_dir: Path) -> list[str]:`:**

```python
def _check_value_shapes(sk: Path, fm: dict) -> list[str]:
    '''The value shapes the Agent Skills spec defines: no < or > in name or
    description, metadata as a string-to-string map, compatibility as a string
    of 1 to COMPATIBILITY_CAP characters.'''
    errs = [f'{sk}: {key} contains < or >' for key in ('name', 'description')
            if ANGLE_BRACKET_RE.search(str(fm.get(key) or ''))]
    meta = fm.get('metadata', {})
    if not (isinstance(meta, dict)
            and all(isinstance(k, str) and isinstance(v, str) for k, v in meta.items())):
        errs.append(f'{sk}: metadata must map strings to strings (quote a value such as version: "1.0")')
    if 'compatibility' in fm:
        compat = fm['compatibility']
        if not (isinstance(compat, str) and 1 <= len(compat.strip()) <= COMPATIBILITY_CAP):
            errs.append(f'{sk}: compatibility must be a string of 1-{COMPATIBILITY_CAP} characters')
    return errs


```

- [ ] **Step 4: See the rule catch the real violation.** Run `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py`. Expected: exit 1, one line ending `skills/llm-wiki/SKILL.md: description contains < or >`.
- [ ] **Step 5: Fix it, and keep the docs true.**

**Edit `skills/llm-wiki/SKILL.md`: replace**

```markdown
  say', 'wiki lint', 'verify <page>', 'file this into the wiki'; any reference
```

**with**

```markdown
  say', 'wiki lint', 'verify a page', 'file this into the wiki'; any reference
```

**Edit `skills/writing-skills/SKILL.md`: replace**

```markdown
- Optional keys the lint accepts: `license`, `compatibility`, `metadata`, `allowed-tools`, `when_to_use`, the two delegation keys `model` and `effort` (per-skill overrides for the model tier and reasoning effort a skill runs at; a Haiku `model` is not portable, since auto mode drops Haiku 4.5 and the `haiku` alias means Haiku 5.5 on the Anthropic API but 4.5 on other providers, so the lint fails it, and cheap work belongs on a model-pinned subagent), and `context` (sole value `fork`: runs the skill in an isolated subagent, so the main session sees only what the skill returns). Any other key fails `build/check_frontmatter.py`.
```

**with**

```markdown
- Optional keys the lint accepts: `license`, `compatibility`, `metadata`, `allowed-tools`, `when_to_use`, the two delegation keys `model` and `effort` (per-skill overrides for the model tier and reasoning effort a skill runs at; a Haiku `model` is not portable, since auto mode drops Haiku 4.5 and the `haiku` alias means Haiku 5.5 on the Anthropic API but 4.5 on other providers, so the lint fails it, and cheap work belongs on a model-pinned subagent), `context` (sole value `fork`: runs the skill in an isolated subagent, so the main session sees only what the skill returns), `agent` (the agent type a `context: fork` skill runs on), and `disable-model-invocation` (a YAML boolean; `true` makes the skill manual-only). Any other key fails `build/check_frontmatter.py`. The spec's own keys are `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`; the rest are Claude Code extensions, which a claude.ai upload or a spec-only validator rejects.
```

**Edit `build/cc_guide/conformance.toml`: replace**

```toml
# names it. Idle on skills/*/SKILL.md while check_frontmatter's ALLOWED_KEYS
# rejects the key there, but .claude/skills/ is not linted for it. Drift R4.1's
```

**with**

```toml
# names it. check_frontmatter's HOST_KEYS allows the key on skills/*/SKILL.md
# since portability Stage A, and .claude/skills/ is not linted for it. Drift R4.1's
```

**Edit `build/cc_guide/conformance.toml`: replace**

```toml
# change so the register maps them to the guide. Portability Stage A owns
# that file.
```

**with**

```toml
# change so the register maps them to the guide.
```

- [ ] **Step 6: Run the tests.** Same command as Step 2. Expected: `45 passed` (+4).
- [ ] **Step 7: Gates and commit.**

```bash
bash build/run_commit_lints.sh
```

```bash
git add build/check_frontmatter.py build/test_check_frontmatter.py skills/llm-wiki/SKILL.md skills/writing-skills/SKILL.md build/cc_guide/conformance.toml
```

```bash
git commit -m "feat(build): spec and host frontmatter key sets and value shapes (portability R1.1-R1.3, R1.5)"
```

---

### Task 4: `license` is required; the superpowers metadata (R1.4, R4.3)

**Files:**
- Modify: `build/check_frontmatter.py` (new `_check_license`, called from `check_skill`)
- Test: `build/test_check_frontmatter.py` (+1; `make_skill` adds `license: MIT` unless told not to)
- Modify: the 13 superpowers `SKILL.md` files (helper script), `skills/writing-skills/SKILL.md` (required fields, optional keys, template, checklist), `NOTICE` (one entry)

**Interfaces:**
- Consumes: Task 3's `check_skill` layout.
- Produces: `_check_license(sk: Path, fm: dict) -> list[str]`; `make_skill(tmp_path, name, frontmatter, *, licensed=True)` in the tests, which later tasks' tests use.

- [ ] **Step 1: Write the failing test.**

**Edit `build/test_check_frontmatter.py`: replace**

```python
import subprocess
from pathlib import Path
```

**with**

```python
import re
import subprocess
from pathlib import Path
```

**Edit `build/test_check_frontmatter.py`: replace**

```python
def make_skill(tmp_path: Path, name: str, frontmatter: str) -> Path:
    d = tmp_path / name
    d.mkdir()
    (d / 'SKILL.md').write_text(f'---\n{frontmatter}\n---\n\n# Body\n')
    return d
```

**with**

```python
def make_skill(tmp_path: Path, name: str, frontmatter: str, *, licensed: bool = True) -> Path:
    '''A skill directory with this frontmatter. Every SKILL.md needs a license
    (portability R1.4), so one is added unless the frontmatter sets its own or
    the test passes licensed=False.'''
    d = tmp_path / name
    d.mkdir()
    if licensed and not re.search(r'^license:', frontmatter, re.M):
        frontmatter = f'license: MIT\n{frontmatter}'
    (d / 'SKILL.md').write_text(f'---\n{frontmatter}\n---\n\n# Body\n')
    return d
```

**Edit `build/test_check_frontmatter.py`: insert before the line `def test_metadata_must_map_strings_to_strings(tmp_path):`:**

```python
def test_license_is_required(tmp_path):
    # Portability R1.4: repo policy, beyond the spec, so a single-skill install
    # still says how the skill is licensed.
    msg = 'license is required, a non-empty string (repo policy, beyond the Agent Skills spec)'
    missing = make_skill(tmp_path, 'no-license', 'name: no-license\ndescription: Use when testing.',
                         licensed=False)
    assert check_skill(missing) == [f"{missing / 'SKILL.md'}: {msg}"]
    blank = make_skill(tmp_path, 'blank-license',
                       "name: blank-license\ndescription: Use when testing.\nlicense: ' '")
    assert check_skill(blank) == [f"{blank / 'SKILL.md'}: {msg}"]


```

- [ ] **Step 2: Run it to see it fail.** Run `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_frontmatter.py`. Expected: `1 failed, 45 passed`.
- [ ] **Step 3: Implement.**

**Edit `build/check_frontmatter.py`: replace**

```python
- every key is an Agent Skills spec key (SPEC_KEYS) or a host extension this
  repo allows (HOST_KEYS);
```

**with**

```python
- every key is an Agent Skills spec key (SPEC_KEYS) or a host extension this
  repo allows (HOST_KEYS);
- license is a non-empty string (repo policy, beyond the spec);
```

**Edit `build/check_frontmatter.py`: replace**

```python
    errs += _check_model_pin(sk, fm)
    errs += _check_value_shapes(sk, fm)
```

**with**

```python
    errs += _check_model_pin(sk, fm)
    errs += _check_license(sk, fm)
    errs += _check_value_shapes(sk, fm)
```

**Edit `build/check_frontmatter.py`: insert before the line `def _check_value_shapes(sk: Path, fm: dict) -> list[str]:`:**

```python
def _check_license(sk: Path, fm: dict) -> list[str]:
    '''Every SKILL.md names its license (portability R1.4: repo policy, beyond
    the spec), so a single-skill install still says how the skill is licensed.'''
    lic = fm.get('license')
    if isinstance(lic, str) and lic.strip():
        return []
    return [f'{sk}: license is required, a non-empty string (repo policy, beyond the Agent Skills spec)']


```

- [ ] **Step 4: Keep writing-skills and NOTICE true.**

**Edit `skills/writing-skills/SKILL.md`: replace**

```markdown
- Two required fields: `name` and `description` (see [agentskills.io/specification](https://agentskills.io/specification) for all supported fields)
```

**with**

```markdown
- Three required fields: `name` and `description`, the Agent Skills spec's two (see [agentskills.io/specification](https://agentskills.io/specification) for all supported fields), and `license`, this repo's rule, enforced by `build/check_frontmatter.py`
```

**Edit `skills/writing-skills/SKILL.md`: replace**

```markdown
- Optional keys the lint accepts: `license`, `compatibility`, `metadata`, `allowed-tools`, `when_to_use`, the two delegation keys `model` and `effort` (per-skill overrides for the model tier and reasoning effort a skill runs at; a Haiku `model` is not portable, since auto mode drops Haiku 4.5 and the `haiku` alias means Haiku 5.5 on the Anthropic API but 4.5 on other providers, so the lint fails it, and cheap work belongs on a model-pinned subagent), `context` (sole value `fork`: runs the skill in an isolated subagent, so the main session sees only what the skill returns), `agent` (the agent type a `context: fork` skill runs on), and `disable-model-invocation` (a YAML boolean; `true` makes the skill manual-only). Any other key fails `build/check_frontmatter.py`. The spec's own keys are `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`; the rest are Claude Code extensions, which a claude.ai upload or a spec-only validator rejects.
```

**with**

```markdown
- Optional keys the lint accepts: `compatibility`, `metadata`, `allowed-tools`, `when_to_use`, the two delegation keys `model` and `effort` (per-skill overrides for the model tier and reasoning effort a skill runs at; a Haiku `model` is not portable, since auto mode drops Haiku 4.5 and the `haiku` alias means Haiku 5.5 on the Anthropic API but 4.5 on other providers, so the lint fails it, and cheap work belongs on a model-pinned subagent), `context` (sole value `fork`: runs the skill in an isolated subagent, so the main session sees only what the skill returns), `agent` (the agent type a `context: fork` skill runs on), and `disable-model-invocation` (a YAML boolean; `true` makes the skill manual-only). Any other key fails `build/check_frontmatter.py`. The spec's own keys are `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`; the rest are Claude Code extensions, which a claude.ai upload or a spec-only validator rejects.
```

**Edit `skills/writing-skills/SKILL.md`: replace**

```markdown
name: Skill-Name-With-Hyphens
description: Use when [specific triggering conditions and symptoms]
---
```

**with**

```markdown
name: Skill-Name-With-Hyphens
description: Use when [specific triggering conditions and symptoms]
license: MIT
---
```

**Edit `skills/writing-skills/SKILL.md`: replace**

```markdown
- [ ] YAML frontmatter with required `name` and `description` fields (`description` max 1024 chars — the field, not the whole block; see [spec](https://agentskills.io/specification))
```

**with**

```markdown
- [ ] YAML frontmatter with required `name`, `description` and `license` fields (`description` max 1024 chars — the field, not the whole block; see [spec](https://agentskills.io/specification))
```

**Edit `NOTICE`: replace**

```text
    path against the user's repository.
```

**with**

```text
    path against the user's repository.
  - All thirteen skills' SKILL.md files gained `license: MIT` and a
    `metadata` block naming Jesse Vincent as author, Lowell Mason as
    adapter and https://github.com/obra/superpowers as source, placed
    above any `# cc-guide:` line so that line stays last
    (specs/agent-skills-portability-spec.md, R1.4). writing-skills' list of
    the frontmatter keys build/check_frontmatter.py accepts was brought up
    to date in the same change: `license` is required, and
    `disable-model-invocation` and `agent` are accepted.
```

- [ ] **Step 5: Give the superpowers skills their license and metadata.**

**Create `/tmp/portability-plan/add_superpowers_metadata.py`:**

```python
'''Give the 13 superpowers skills R1.4's license and metadata, above any # cc-guide: line.

Usage: uv run --no-project --python 3.13 python add_superpowers_metadata.py <repo-root>
Refuses a file that already has a license key.
'''
import sys
from pathlib import Path

SUPERPOWERS = (
    'brainstorming', 'dispatching-parallel-agents', 'executing-plans',
    'finishing-a-development-branch', 'receiving-code-review', 'requesting-code-review',
    'subagent-driven-development', 'systematic-debugging', 'test-driven-development',
    'using-git-worktrees', 'verification-before-completion', 'writing-plans', 'writing-skills',
)
BLOCK = [
    'license: MIT',
    'metadata:',
    "  author: 'Jesse Vincent'",
    "  adapted_by: 'Lowell Mason'",
    "  source: 'https://github.com/obra/superpowers'",
]
root = Path(sys.argv[1])
for name in SUPERPOWERS:
    path = root / 'skills' / name / 'SKILL.md'
    lines = path.read_text().split('\n')
    close = lines.index('---', 1)
    front = lines[1:close]
    if any(line.startswith('license:') for line in front):
        sys.exit(f'{path}: already has a license key')
    cite = [i for i, line in enumerate(front, start=1) if line.startswith('# cc-guide:')]
    at = cite[0] if cite else close
    path.write_text('\n'.join(lines[:at] + BLOCK + lines[at:]))
    print(f'{name}: inserted at frontmatter line {at}' + (' (above the citation)' if cite else ''))
```

Run `uv run --no-project --python 3.13 python /tmp/portability-plan/add_superpowers_metadata.py .`. Expected: 13 lines; the seven skills with a citation report `(above the citation)`.

If `skills/write-with-asd-ste100/` exists and the lint reports `skills/write-with-asd-ste100/SKILL.md: license is required…`, add `license: MIT` as its frontmatter's line after `description`.

- [ ] **Step 6: Run the tests.** Same command as Step 2. Expected: `46 passed` (+1).
- [ ] **Step 7: Gates and commit.**

```bash
bash build/run_commit_lints.sh
```

```bash
git add build/check_frontmatter.py build/test_check_frontmatter.py NOTICE skills
```

```bash
git commit -m "feat(build): require a license in every SKILL.md; superpowers metadata (portability R1.4)"
```

---

### Task 5: Codex invocation parity (R1.6)

**Files:**
- Modify: `build/check_frontmatter.py` (new `DMI_KEY`, `CODEX_POLICY`, `_check_invocation_parity`)
- Test: `build/test_check_frontmatter.py` (+6)

**Interfaces:**
- Produces: `_check_invocation_parity(skill_dir: Path, fm: dict) -> list[str]`, called from `check_skill`; `CODEX_POLICY = Path('agents') / 'openai.yaml'`.

- [ ] **Step 1: Write the failing tests.**

**Edit `build/test_check_frontmatter.py`: insert before the line `def make_agent(tmp_path: Path, name: str, description: str) -> Path:`:**

```python
def _skill_with_dmi(tmp_path: Path, name: str, dmi: str, policy: str | None = None) -> Path:
    '''A skill setting disable-model-invocation, optionally with Codex's policy file.'''
    d = make_skill(tmp_path, name,
                   f'name: {name}\ndescription: Use when testing.\ndisable-model-invocation: {dmi}')
    if policy is not None:
        (d / 'agents').mkdir()
        (d / 'agents' / 'openai.yaml').write_text(policy)
    return d


FORBID_IMPLICIT = 'policy:\n  allow_implicit_invocation: false\n'


def test_disable_model_invocation_must_be_a_yaml_boolean(tmp_path):
    # Portability R1.6: a quoted 'true' is a string, which disables nothing.
    d = _skill_with_dmi(tmp_path, 'quoted-dmi', "'true'")
    assert check_skill(d) == [f"{d / 'SKILL.md'}: disable-model-invocation must be a YAML boolean, got 'true'"]


def test_a_manual_only_skill_needs_the_codex_policy_file(tmp_path):
    d = _skill_with_dmi(tmp_path, 'manual-skill', 'true')
    assert check_skill(d) == [
        f"{d / 'SKILL.md'}: disable-model-invocation: true needs agents/openai.yaml with "
        'policy.allow_implicit_invocation: false, so Codex keeps the skill manual-only too']


def test_a_manual_only_skill_with_the_codex_policy_passes(tmp_path):
    assert check_skill(_skill_with_dmi(tmp_path, 'paired-skill', 'true', FORBID_IMPLICIT)) == []


def test_the_codex_policy_must_forbid_implicit_invocation(tmp_path):
    d = _skill_with_dmi(tmp_path, 'loose-skill', 'true', 'policy:\n  allow_implicit_invocation: true\n')
    assert check_skill(d) == [
        f"{d / 'agents' / 'openai.yaml'}: must set policy.allow_implicit_invocation: false, "
        'because SKILL.md sets disable-model-invocation: true']


def test_a_codex_manual_only_skill_needs_disable_model_invocation(tmp_path):
    # The converse: manual-only in Codex but still auto-invoked by Claude Code.
    d = _skill_with_dmi(tmp_path, 'codex-only', 'false', FORBID_IMPLICIT)
    assert check_skill(d) == [
        f"{d / 'SKILL.md'}: agents/openai.yaml sets policy.allow_implicit_invocation: false, "
        'so disable-model-invocation must be true']


def test_an_unparseable_codex_policy_is_reported(tmp_path):
    d = _skill_with_dmi(tmp_path, 'broken-policy', 'true', 'policy: [unclosed\n')
    errs = check_skill(d)
    assert len(errs) == 1 and 'agents/openai.yaml: does not parse as YAML' in errs[0], errs


```

- [ ] **Step 2: Run them to see them fail.** Run `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_frontmatter.py`. Expected: `5 failed, 47 passed`. `test_a_manual_only_skill_with_the_codex_policy_passes` is a guard: it passes before and after.
- [ ] **Step 3: Implement.**

**Edit `build/check_frontmatter.py`: replace**

```python
- name and description contain no < or >; metadata maps strings to strings;
  compatibility is a string of 1-500 characters;
```

**with**

```python
- name and description contain no < or >; metadata maps strings to strings;
  compatibility is a string of 1-500 characters;
- disable-model-invocation is a YAML boolean, and it is true exactly when the
  skill's agents/openai.yaml sets Codex's policy.allow_implicit_invocation: false;
```

**Edit `build/check_frontmatter.py`: replace**

```python
# The spec caps compatibility at 500 characters.
COMPATIBILITY_CAP = 500
```

**with**

```python
# The spec caps compatibility at 500 characters.
COMPATIBILITY_CAP = 500
DMI_KEY = 'disable-model-invocation'
# Codex reads a skill's invocation policy from this file
# (developers.openai.com/codex/skills).
CODEX_POLICY = Path('agents') / 'openai.yaml'
```

**Edit `build/check_frontmatter.py`: replace**

```python
    errs += _check_value_shapes(sk, fm)
```

**with**

```python
    errs += _check_value_shapes(sk, fm)
    errs += _check_invocation_parity(skill_dir, fm)
```

**Edit `build/check_frontmatter.py`: insert before the line `def check_skill(skill_dir: Path) -> list[str]:`:**

```python
def _check_invocation_parity(skill_dir: Path, fm: dict) -> list[str]:
    '''disable-model-invocation and Codex's policy.allow_implicit_invocation
    agree (portability R1.6), so a manual-only skill cannot auto-fire in Codex.'''
    sk = skill_dir / 'SKILL.md'
    dmi = fm.get(DMI_KEY)
    if DMI_KEY in fm and not isinstance(dmi, bool):
        return [f'{sk}: {DMI_KEY} must be a YAML boolean, got {dmi!r}']
    policy_file = skill_dir / CODEX_POLICY
    if not policy_file.is_file():
        if dmi is True:
            return [f'{sk}: {DMI_KEY}: true needs {CODEX_POLICY} with '
                    'policy.allow_implicit_invocation: false, so Codex keeps the skill manual-only too']
        return []
    try:
        data = yaml.safe_load(policy_file.read_text())
    except yaml.YAMLError as exc:
        return [f'{policy_file}: does not parse as YAML ({type(exc).__name__})']
    policy = data.get('policy') if isinstance(data, dict) else None
    allow = policy.get('allow_implicit_invocation') if isinstance(policy, dict) else None
    if dmi is True and allow is not False:
        return [f'{policy_file}: must set policy.allow_implicit_invocation: false, '
                f'because SKILL.md sets {DMI_KEY}: true']
    if dmi is not True and allow is False:
        return [f'{sk}: {CODEX_POLICY} sets policy.allow_implicit_invocation: false, '
                f'so {DMI_KEY} must be true']
    return []


```

- [ ] **Step 4: Run the tests.** Same command as Step 2. Expected: `52 passed` (+6).
- [ ] **Step 5: Gates and commit.**

```bash
bash build/run_commit_lints.sh
```

```bash
git add build/check_frontmatter.py build/test_check_frontmatter.py
```

```bash
git commit -m "feat(build): disable-model-invocation agrees with Codex's implicit-invocation policy (portability R1.6)"
```

---

### Task 6: The body-length advisory (R1.7)

**Files:**
- Modify: `build/check_frontmatter.py` (new `BODY_LINE_ADVISORY`, `FRONTMATTER_RE`, `skill_body_warning`; `main` prints the warning)
- Test: `build/test_check_frontmatter.py` (+2)
- Modify: `build/cc_guide/conformance.toml` (new check `skill-body-size`, R1.7's register row)

**Interfaces:**
- Produces: `skill_body_warning(skill_dir: Path) -> str | None`; `FRONTMATTER_RE`, which Task 7 does not use and later code may.

- [ ] **Step 1: Write the failing tests.**

**Edit `build/test_check_frontmatter.py`: replace**

```python
import re
import subprocess
from pathlib import Path
```

**with**

```python
import re
import subprocess
import sys
from pathlib import Path
```

**Edit `build/test_check_frontmatter.py`: replace**

```python
    check_skill,
    load_readonly_roster,
```

**with**

```python
    check_skill,
    load_readonly_roster,
    skill_body_warning,
```

**Edit `build/test_check_frontmatter.py`: insert before the line `def make_agent(tmp_path: Path, name: str, description: str) -> Path:`:**

```python
def _skill_with_body_lines(tmp_path: Path, name: str, extra: int) -> Path:
    '''make_skill's body is two lines (a blank line and "# Body"); add extra lines.'''
    d = make_skill(tmp_path, name, f'name: {name}\ndescription: Use when testing.')
    (d / 'SKILL.md').write_text((d / 'SKILL.md').read_text() + 'line\n' * extra)
    return d


def test_a_body_over_500_lines_warns_without_an_error(tmp_path):
    # Portability R1.7: an advisory, so check_skill (the errors) stays clean.
    at_limit = _skill_with_body_lines(tmp_path, 'at-limit', 498)
    over = _skill_with_body_lines(tmp_path, 'over-limit', 499)
    assert skill_body_warning(at_limit) is None
    assert skill_body_warning(over) == (
        f"WARN {over / 'SKILL.md'}: body is 501 lines; the guide keeps a SKILL.md body under 500")
    assert check_skill(over) == []


def test_the_body_warning_goes_to_stderr_and_keeps_exit_zero():
    # writing-skills is the one body over 500 lines (portability baseline);
    # revisit this test when it is split, a portability deferred item.
    result = subprocess.run([sys.executable, str(REPO / 'build' / 'check_frontmatter.py')],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout
    assert 'WARN' not in result.stdout
    assert any(line.startswith('WARN ') and 'skills/writing-skills/SKILL.md: body is' in line
               for line in result.stderr.splitlines()), result.stderr


```

- [ ] **Step 2: Run them to see them fail.** Run `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_frontmatter.py`. Expected: `1 error`, a collection error: `ImportError: cannot import name 'skill_body_warning'`.
- [ ] **Step 3: Implement, and map it in the register.**

**Edit `build/check_frontmatter.py`: replace**

```python
- every relative markdown-link target and every backticked references/ or
  scripts/ path exists.
```

**with**

```python
- every relative markdown-link target and every backticked references/ or
  scripts/ path exists.
A body (the lines after the closing frontmatter ---) over 500 lines prints one
WARN line to stderr; the exit code does not change.
```

**Edit `build/check_frontmatter.py`: replace**

```python
# The spec caps compatibility at 500 characters.
COMPATIBILITY_CAP = 500
```

**with**

```python
# The spec caps compatibility at 500 characters.
COMPATIBILITY_CAP = 500
# The guide's skills.overview keeps a SKILL.md body under 500 lines; past it,
# the lint warns and does not fail (portability R1.7).
BODY_LINE_ADVISORY = 500
FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---\n', re.S)
```

**Edit `build/check_frontmatter.py`: insert before the line `def _parse_frontmatter(md: Path) -> tuple[dict | None, list[str]]:`:**

```python
def skill_body_warning(skill_dir: Path) -> str | None:
    '''One WARN line for a SKILL.md body over BODY_LINE_ADVISORY lines, counted
    as wc -l counts the lines after the closing frontmatter ---.'''
    sk = skill_dir / 'SKILL.md'
    text = sk.read_text()
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None  # check_skill reports the missing block
    lines = text[m.end():].count('\n')
    if lines <= BODY_LINE_ADVISORY:
        return None
    return f'WARN {sk}: body is {lines} lines; the guide keeps a SKILL.md body under {BODY_LINE_ADVISORY}'


```

**Edit `build/check_frontmatter.py`: replace**

```python
        if d.is_dir() and (d / 'SKILL.md').exists():
            errs += check_skill(d)
```

**with**

```python
        if d.is_dir() and (d / 'SKILL.md').exists():
            errs += check_skill(d)
            warning = skill_body_warning(d)
            if warning:
                print(warning, file=sys.stderr)
```

**Edit `build/cc_guide/conformance.toml`: replace**

```toml
rule = 'Descriptions stay within the listing cap; the repo enforces the stricter 1,024-character Agent Skills cap.'
enforced_by = 'check_frontmatter'
```

**with**

```toml
rule = 'Descriptions stay within the listing cap; the repo enforces the stricter 1,024-character Agent Skills cap.'
enforced_by = 'check_frontmatter'

# Portability R1.7, mapped here by conformance spec R6 (P3). An advisory: the
# lint prints one WARN line and the exit code does not change.
[[check]]
id = 'skill-body-size'
kind = 'skill'
sections = ['skills.overview']
type = 'advice'
rule = 'A SKILL.md body stays under 500 lines; check_frontmatter.py warns past that and does not fail.'
enforced_by = 'check_frontmatter'
```

- [ ] **Step 4: Run the tests and the lint.** Same command as Step 2. Expected: `54 passed` (+2). Then `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py` exits 0 and prints one stderr line, ending `skills/writing-skills/SKILL.md: body is 697 lines; the guide keeps a SKILL.md body under 500`.
- [ ] **Step 5: Gates and commit.**

```bash
bash build/run_commit_lints.sh
```

```bash
git add build/check_frontmatter.py build/test_check_frontmatter.py build/cc_guide/conformance.toml
```

```bash
git commit -m "feat(build): warn on a SKILL.md body over 500 lines (portability R1.7)"
```

---

### Task 7: `--strict` and its docs (R1.8, R1.9)

**Files:**
- Modify: `build/check_frontmatter.py` (new `RESERVED_NAME_WORDS`, `strict_violations`; `main` takes `--strict`; docstring)
- Test: `build/test_check_frontmatter.py` (+2)
- Modify: `CLAUDE.md` (Commands: the frontmatter lint's comment names `--strict`; no line added, D7)

**Interfaces:**
- Consumes: Task 3's `HOST_KEYS`.
- Produces: `strict_violations(skill_dir: Path) -> list[str]`; `main(argv: list[str] | None = None) -> int`.

- [ ] **Step 1: Write the failing tests.**

**Edit `build/test_check_frontmatter.py`: replace**

```python
    load_readonly_roster,
    skill_body_warning,
```

**with**

```python
    load_readonly_roster,
    skill_body_warning,
    strict_violations,
```

**Edit `build/test_check_frontmatter.py`: insert before the line `def make_agent(tmp_path: Path, name: str, description: str) -> Path:`:**

```python
def test_strict_flags_host_keys_and_reserved_name_words(tmp_path):
    # Portability R1.8: the keys pass the default gate and fail --strict.
    hosted = make_skill(tmp_path, 'hosted',
                        'name: hosted\ndescription: Use when testing.\neffort: xhigh\ncontext: fork')
    assert check_skill(hosted) == []
    note = 'is a Claude Code extension, not an Agent Skills spec key (--strict)'
    assert strict_violations(hosted) == [f"{hosted / 'SKILL.md'}: 'context' {note}",
                                         f"{hosted / 'SKILL.md'}: 'effort' {note}"]
    named = make_skill(tmp_path, 'claude-helper', 'name: claude-helper\ndescription: Use when testing.')
    assert strict_violations(named) == [
        f"{named / 'SKILL.md'}: name contains the reserved word 'claude' (--strict)"]
    plain = make_skill(tmp_path, 'plain', 'name: plain\ndescription: Use when testing.')
    assert strict_violations(plain) == []


def test_strict_is_off_by_default_and_on_with_the_flag():
    # The default gate stays green; --strict adds only its own SKILL.md lines.
    script = str(REPO / 'build' / 'check_frontmatter.py')
    default = subprocess.run([sys.executable, script], capture_output=True, text=True)
    strict = subprocess.run([sys.executable, script, '--strict'], capture_output=True, text=True)
    assert default.returncode == 0, default.stdout
    assert strict.returncode == 1, strict.stdout
    lines = strict.stdout.splitlines()
    assert lines and all(line.endswith('(--strict)') and '/SKILL.md: ' in line for line in lines), lines


```

- [ ] **Step 2: Run them to see them fail.** Run `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_frontmatter.py`. Expected: `1 error`, a collection error: `ImportError: cannot import name 'strict_violations'`.
- [ ] **Step 3: Implement, and document it.**

**Edit `build/check_frontmatter.py`: replace**

```python
A body (the lines after the closing frontmatter ---) over 500 lines prints one
WARN line to stderr; the exit code does not change.

Run: uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
Exit 0 if clean; exit 1 with one line per violation.
```

**with**

```python
A body (the lines after the closing frontmatter ---) over 500 lines prints one
WARN line to stderr; the exit code does not change.

--strict also fails a SKILL.md that carries a HOST_KEYS key or whose name
contains claude or anthropic. It is not part of the commit gate: run it before
a claude.ai upload or a spec-only validator run. Agents and commands are not
Agent Skills, so it leaves them alone.

Run: uv run --python 3.13 --with pyyaml python build/check_frontmatter.py [--strict]
Exit 0 if clean; exit 1 with one line per violation.
```

**Edit `build/check_frontmatter.py`: replace**

```python
import importlib.util
import re
import sys
```

**with**

```python
import argparse
import importlib.util
import re
import sys
```

**Edit `build/check_frontmatter.py`: insert after the line `DMI_KEY = 'disable-model-invocation'`:**

```python
# A skill name may not contain these words on claude.ai (portability R1.8).
RESERVED_NAME_WORDS = ('claude', 'anthropic')
```

**Edit `build/check_frontmatter.py`: insert before the line `def _parse_frontmatter(md: Path) -> tuple[dict | None, list[str]]:`:**

```python
def strict_violations(skill_dir: Path) -> list[str]:
    '''The --strict profile (portability R1.8): host keys and reserved name
    words, which only a claude.ai upload or a spec-only validator rejects.'''
    sk = skill_dir / 'SKILL.md'
    fm, _ = _parse_frontmatter(sk)
    if fm is None:
        return []  # check_skill reports why
    errs = [f'{sk}: {key!r} is a Claude Code extension, not an Agent Skills spec key (--strict)'
            for key in sorted(set(fm) & HOST_KEYS)]
    name = str(fm.get('name') or '').lower()
    errs += [f'{sk}: name contains the reserved word {word!r} (--strict)'
             for word in RESERVED_NAME_WORDS if word in name]
    return errs


```

**Edit `build/check_frontmatter.py`: replace**

```python
def main() -> int:
    errs: list[str] = []
    for d in sorted((REPO / 'skills').iterdir()):
        if d.is_dir() and (d / 'SKILL.md').exists():
            errs += check_skill(d)
```

**with**

```python
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Lint skill, agent and command frontmatter.')
    parser.add_argument('--strict', action='store_true',
                        help='also fail host keys and the reserved words claude and anthropic in a '
                             'SKILL.md; run before a claude.ai upload or a spec-only validator run')
    args = parser.parse_args(argv)
    errs: list[str] = []
    for d in sorted((REPO / 'skills').iterdir()):
        if d.is_dir() and (d / 'SKILL.md').exists():
            errs += check_skill(d)
            if args.strict:
                errs += strict_violations(d)
```

**Edit `CLAUDE.md`: replace**

```markdown
# Frontmatter, provenance and guide-conformance lints (run before committing any Claude Code artifact)
```

**with**

```markdown
# Frontmatter, provenance and guide-conformance lints (run before committing any Claude Code artifact); add --strict to the first, a report and not a gate, when preparing a claude.ai upload or a spec-only validator run
```

- [ ] **Step 4: Run the tests and the profile.** Same command as Step 2. Expected: `56 passed` (+2). Then `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py --strict` exits 1. Its stdout has exactly three lines, for `bayesian-workflow` (`'effort'`), `tech-debt` (`'context'`) and `tune-hyperparameters` (`'effort'`), each ending `is a Claude Code extension, not an Agent Skills spec key (--strict)` (Validation 2); stderr carries Task 6's `WARN` line. `wc -l CLAUDE.md` still prints 199.
- [ ] **Step 5: Gates and commit.**

```bash
bash build/run_commit_lints.sh
```

```bash
git add build/check_frontmatter.py build/test_check_frontmatter.py CLAUDE.md
```

```bash
git commit -m "feat(build): check_frontmatter.py --strict for claude.ai uploads and spec-only validators (portability R1.8, R1.9)"
```

---

### Task 8: License copies travel with each skill (R4.1, R4.2, R4.4)

**Files:**
- Modify: `build/check_provenance.py` (docstring; new `PLAIN_LICENSE`, `BUNDLED_LICENSES`, `bundled_license_violations`; `main`)
- Test: `build/test_check_provenance.py` (+7)
- Rename: `skills/recommend-causal-design/LICENSE` to `skills/recommend-causal-design/LICENSE-causal-design-sources`, and re-point its links in that skill's `SKILL.md`, `README.md` and `references/sources.md`
- Create: a copy of each applicable root license file in every skill directory (helper script)
- Modify: `build/cc_guide/conformance.toml` (`orphan-bundled-file` exempts `LICENSE*`), `NOTICE`, `README.md`, `CLAUDE.md` (R4.4)

**Interfaces:**
- Produces, in `check_provenance.py`: `PLAIN_LICENSE = 'LICENSE'`; `BUNDLED_LICENSES: dict[str, tuple[str, ...]]`, which Task 9 extends and the helper imports; `bundled_license_violations(repo: Path, skills: list[str], table: dict[str, tuple[str, ...]]) -> list[str]`.

- [ ] **Step 1: Write the failing tests.**

**Edit `build/test_check_provenance.py`: replace**

```python
from check_provenance import (
    claude_md_originals,
```

**with**

```python
from check_provenance import (
    BUNDLED_LICENSES,
    bundled_license_violations,
    claude_md_originals,
```

**Edit `build/test_check_provenance.py`: insert before the line `def test_find_binary_assets_flags_documents():`:**

```python
ROOT_TEXT = {'LICENSE': 'MIT, Lowell Mason\n', 'LICENSE-x': 'MIT, Upstream\n'}


def _license_tree(tmp_path, copies):
    '''A repo with two root license files and one skill directory per key of
    copies, each holding the named license files copied from the root.'''
    for name, text in ROOT_TEXT.items():
        (tmp_path / name).write_text(text)
    for skill, files in copies.items():
        d = tmp_path / 'skills' / skill
        d.mkdir(parents=True)
        (d / 'SKILL.md').write_text('---\nname: x\n---\n')
        for name in files:
            (d / name).write_text(ROOT_TEXT[name])
    return tmp_path


TABLE = {'LICENSE-x': ('adapted',)}


def test_bundled_licenses_clean_when_every_copy_matches(tmp_path):
    repo = _license_tree(tmp_path, {'own': ['LICENSE'], 'adapted': ['LICENSE', 'LICENSE-x']})
    assert bundled_license_violations(repo, ['adapted', 'own'], TABLE) == []


def test_bundled_licenses_report_a_missing_copy(tmp_path):
    repo = _license_tree(tmp_path, {'own': [], 'adapted': ['LICENSE', 'LICENSE-x']})
    assert bundled_license_violations(repo, ['adapted', 'own'], TABLE) == [
        'skills/own/LICENSE: missing; copy the root LICENSE here as a regular file']


def test_bundled_licenses_report_a_symlinked_copy(tmp_path):
    # install.py --copy refuses symlinks, so a linked copy would not travel.
    repo = _license_tree(tmp_path, {'own': [], 'adapted': ['LICENSE', 'LICENSE-x']})
    (repo / 'skills' / 'own' / 'LICENSE').symlink_to(repo / 'LICENSE')
    assert bundled_license_violations(repo, ['adapted', 'own'], TABLE) == [
        'skills/own/LICENSE: a symlink, which install.py --copy refuses; copy the root LICENSE as a regular file']


def test_bundled_licenses_report_a_copy_that_differs(tmp_path):
    repo = _license_tree(tmp_path, {'own': ['LICENSE'], 'adapted': ['LICENSE', 'LICENSE-x']})
    (repo / 'skills' / 'adapted' / 'LICENSE-x').write_text('edited\n')
    assert bundled_license_violations(repo, ['adapted', 'own'], TABLE) == [
        'skills/adapted/LICENSE-x: differs from the root LICENSE-x; copy it again']


def test_bundled_licenses_report_a_license_outside_the_mapping(tmp_path):
    repo = _license_tree(tmp_path, {'own': ['LICENSE', 'LICENSE-x'], 'adapted': ['LICENSE', 'LICENSE-x']})
    assert bundled_license_violations(repo, ['adapted', 'own'], TABLE) == [
        'skills/own/LICENSE-x: not mapped to own in BUNDLED_LICENSES']


def test_bundled_licenses_report_an_unmapped_root_file_and_a_bad_table(tmp_path):
    repo = _license_tree(tmp_path, {'own': ['LICENSE']})
    table = {'LICENSE-gone': ('own',), 'LICENSE-x': ('ghost',)}
    assert bundled_license_violations(repo, ['own'], {}) == [
        'LICENSE-x: root license file is mapped to no skill in BUNDLED_LICENSES']
    assert bundled_license_violations(repo, ['own'], table) == [
        'BUNDLED_LICENSES: LICENSE-gone is not a root license file',
        'BUNDLED_LICENSES: LICENSE-x names ghost, which is not a skill directory',
    ]


def test_bundled_licenses_table_names_no_plain_license():
    # LICENSE goes to every skill implicitly; listing it would hide a gap.
    assert 'LICENSE' not in BUNDLED_LICENSES


```

- [ ] **Step 2: Run them to see them fail.** Run `uv run --directory build --python 3.13 --with pytest python -m pytest -q test_check_provenance.py`. Expected: `1 error`, a collection error: `ImportError: cannot import name 'BUNDLED_LICENSES'`.
- [ ] **Step 3: Implement.**

**Edit `build/check_provenance.py`: replace**

```python
'''Provenance lint: every skill directory is attributed in NOTICE, and no
binary document assets (.pdf/.epub/.docx) are git-tracked.
```

**with**

```python
'''Provenance lint: every skill directory is attributed in NOTICE and carries
byte-identical copies of the root license files that apply to it
(BUNDLED_LICENSES), and no binary document assets (.pdf/.epub/.docx) are
git-tracked.
```

**Edit `build/check_provenance.py`: insert after the line `BINARY_SUFFIXES = ('.pdf', '.epub', '.docx')`:**

```python
PLAIN_LICENSE = 'LICENSE'
# Root license file -> the skills that carry a byte-identical copy of it under
# the same name, so a single-skill install keeps the notice MIT requires
# (portability R4). PLAIN_LICENSE goes to every skill and is not listed.
BUNDLED_LICENSES: dict[str, tuple[str, ...]] = {
    'LICENSE-superpowers': (
        'brainstorming', 'dispatching-parallel-agents', 'executing-plans',
        'finishing-a-development-branch', 'receiving-code-review',
        'requesting-code-review', 'subagent-driven-development',
        'systematic-debugging', 'test-driven-development', 'using-git-worktrees',
        'verification-before-completion', 'writing-plans', 'writing-skills',
    ),
    # NOTICE records adapted Mancuso Lab content in these two; tech-debt took
    # only an idea from it and carries no copy.
    'LICENSE-coding-skills': ('bayesian-workflow', 'clean-code'),
    'LICENSE-causal-design-sources': ('recommend-causal-design',),
}
```

**Edit `build/check_provenance.py`: insert before the line `def find_binary_assets(tracked: list[str]) -> list[str]:`:**

```python
def bundled_license_violations(repo: Path, skills: list[str],
                               table: dict[str, tuple[str, ...]]) -> list[str]:
    '''Every skill holds a regular-file copy of PLAIN_LICENSE and of each root
    license file the table maps to it, byte-identical to the root file, and no
    other LICENSE* file; every root LICENSE* file is mapped (portability R4.2).'''
    errs: list[str] = []
    roots = sorted(p.name for p in repo.glob('LICENSE*') if p.is_file())
    errs += [f'{name}: root license file is mapped to no skill in BUNDLED_LICENSES'
             for name in roots if name != PLAIN_LICENSE and name not in table]
    for name, owners in sorted(table.items()):
        if name not in roots:
            errs.append(f'BUNDLED_LICENSES: {name} is not a root license file')
        errs += [f'BUNDLED_LICENSES: {name} names {skill}, which is not a skill directory'
                 for skill in owners if skill not in skills]
    for skill in skills:
        d = repo / 'skills' / skill
        wanted = {PLAIN_LICENSE} | {name for name, owners in table.items()
                                    if skill in owners and name in roots}
        for name in sorted(wanted):
            copy, rel = d / name, f'skills/{skill}/{name}'
            if copy.is_symlink():
                errs.append(f'{rel}: a symlink, which install.py --copy refuses; '
                            f'copy the root {name} as a regular file')
            elif not copy.is_file():
                errs.append(f'{rel}: missing; copy the root {name} here as a regular file')
            elif copy.read_bytes() != (repo / name).read_bytes():
                errs.append(f'{rel}: differs from the root {name}; copy it again')
        errs += [f'skills/{skill}/{p.name}: not mapped to {skill} in BUNDLED_LICENSES'
                 for p in sorted(d.glob('LICENSE*')) if p.name not in wanted]
    return errs


```

**Edit `build/check_provenance.py`: replace**

```python
    for name in missing_attributions(skill_dirs(), notice):
        errs.append(f'NOTICE: missing attribution entry for skill {name}/')
```

**with**

```python
    for name in missing_attributions(skill_dirs(), notice):
        errs.append(f'NOTICE: missing attribution entry for skill {name}/')
    errs += bundled_license_violations(REPO, skill_dirs(), BUNDLED_LICENSES)
```

- [ ] **Step 4: Run the tests and see the lint catch the gap.** Same command as Step 2. Expected: `1 failed, 20 passed`. The failure is `test_real_repo_is_clean`: the repo lacks the copies until Step 6. Then `uv run --python 3.13 python build/check_provenance.py` exits 1, reporting 53 lines, one per gap: `LICENSE` is missing from 36 skills and differs from the root file in `recommend-causal-design`; `LICENSE-superpowers` is missing from the 13 superpowers skills, `LICENSE-coding-skills` from `bayesian-workflow` and `clean-code`, and `LICENSE-causal-design-sources` from `recommend-causal-design`.
- [ ] **Step 5: Rename `recommend-causal-design`'s sources copy, and re-point its links.** Run `git mv skills/recommend-causal-design/LICENSE skills/recommend-causal-design/LICENSE-causal-design-sources`, then:

**Edit `skills/recommend-causal-design/SKILL.md`: replace**

```markdown
[sources.md](references/sources.md). Upstream MIT notices are bundled in
[LICENSE](LICENSE), and recorded in the repository's
`LICENSE-causal-design-sources` and `NOTICE`. No upstream code,
```

**with**

```markdown
[sources.md](references/sources.md). Upstream MIT notices are bundled in
[LICENSE-causal-design-sources](LICENSE-causal-design-sources), a copy of the
repository's file of that name, and recorded in `NOTICE`. No upstream code,
```

**Edit `skills/recommend-causal-design/README.md`: replace**

```markdown
grading are included. Retained upstream MIT notices are bundled in
[LICENSE](LICENSE); repository-level attribution is also recorded in `NOTICE`
and `LICENSE-causal-design-sources`.
```

**with**

```markdown
grading are included. Retained upstream MIT notices are bundled in
[LICENSE-causal-design-sources](LICENSE-causal-design-sources), a copy of the
repository's file of that name; repository-level attribution is in `NOTICE`.
```

**Edit `skills/recommend-causal-design/references/sources.md`: replace**

```markdown
was checked at that exact commit. Full MIT notices are retained inside this
skill in [LICENSE](../LICENSE), also recorded in the repository's
`LICENSE-causal-design-sources` and attribution in `NOTICE`.
```

**with**

```markdown
was checked at that exact commit. Full MIT notices are retained inside this
skill in [LICENSE-causal-design-sources](../LICENSE-causal-design-sources), a
copy of the repository's file of that name, with attribution in `NOTICE`.
```

**Edit `build/cc_guide/conformance.toml`: replace**

```toml
# or its directory with a trailing slash. exempt files need no naming; tests
# neither need it nor count as naming anything.
[[check]]
id = 'orphan-bundled-file'
kind = 'skill-bundle'
sections = ['skills.progressive-disclosure']
type = 'advice'
rule = 'A bundled file under a skill directory is named by a file in that skill.'
enforced_by = 'check_conformance'
exempt = ['SKILL.md', 'README.md', 'INSTALL.md']
```

**with**

```toml
# or its directory with a trailing slash. exempt files need no naming; tests
# neither need it nor count as naming anything. The license copies each skill
# carries (portability R4) are exempt because nothing names them: they travel
# with a single-skill install and are never loaded.
[[check]]
id = 'orphan-bundled-file'
kind = 'skill-bundle'
sections = ['skills.progressive-disclosure']
type = 'advice'
rule = 'A bundled file under a skill directory is named by a file in that skill.'
enforced_by = 'check_conformance'
exempt = ['SKILL.md', 'README.md', 'INSTALL.md', 'LICENSE*']
```

**Edit `NOTICE`: replace**

```text
This repository bundles agent skills from more than one source; skills live
under skills/, one directory per skill. Attribution and licensing, by skill:

```

**with**

```text
This repository bundles agent skills from more than one source; skills live
under skills/, one directory per skill. Attribution and licensing, by skill:

Each skill directory carries copies of the license texts that apply to it:
LICENSE in every skill, and each root LICENSE-* file whose source the skill
adapts. A single-skill install (install.py --copy --skill, or a third-party
installer) therefore keeps the notice the MIT license requires. The root files
are canonical, and build/check_provenance.py checks that every copy is
byte-identical to its root file.

```

**Edit `README.md`: replace**

```markdown
- **Bundled U.S. Government data** — the verbatim `sources/` audit copies in `classification-codes` and `geographic-codes` are works of the United States Government, in the public domain under 17 U.S.C. § 105, and carry no license of mine; the `data/` tables derived from them, the build scripts, the seed tables, and all prose are MIT (see [`NOTICE`](NOTICE)).
```

**with**

```markdown
- **Bundled U.S. Government data** — the verbatim `sources/` audit copies in `classification-codes` and `geographic-codes` are works of the United States Government, in the public domain under 17 U.S.C. § 105, and carry no license of mine; the `data/` tables derived from them, the build scripts, the seed tables, and all prose are MIT (see [`NOTICE`](NOTICE)).

Each skill directory also carries copies of the license files that apply to it, so a skill installed on its own keeps its notices; the root files are canonical, and `build/check_provenance.py` checks the copies.
```

**Edit `CLAUDE.md`: replace**

```markdown
The user is meticulous about attribution and licensing — surface provenance/license implications proactively rather than assuming.
```

**with**

```markdown
The user is meticulous about attribution and licensing — surface provenance/license implications proactively rather than assuming. Each skill directory carries byte-identical copies of the root license files that apply to it (`LICENSE` in every skill, the rest per `BUNDLED_LICENSES` in `build/check_provenance.py`, which enforces the copies), so edit a root license file and its copies together.
```

- [ ] **Step 6: Copy the license files.**

**Create `/tmp/portability-plan/copy_licenses.py`:**

```python
'''Copy the root license files into each skill directory, as BUNDLED_LICENSES maps them.

Usage: uv run --no-project --python 3.13 python copy_licenses.py <repo-root>
Regular-file copies only: install.py --copy refuses symlinks.
'''
import shutil
import sys
from pathlib import Path

repo = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(repo / 'build'))
from check_provenance import BUNDLED_LICENSES, PLAIN_LICENSE, skill_dirs  # noqa: E402

for skill in skill_dirs():
    names = [PLAIN_LICENSE] + [n for n, owners in BUNDLED_LICENSES.items() if skill in owners]
    for name in names:
        shutil.copyfile(repo / name, repo / 'skills' / skill / name)
    print(f'{skill}: {", ".join(names)}')
```

Run `uv run --no-project --python 3.13 python /tmp/portability-plan/copy_licenses.py .`. Expected: 37 lines. Then `git status --short` lists 9 modified files (`CLAUDE.md`, `NOTICE`, `README.md`, the register, the lint, its tests and the three `recommend-causal-design` files), the rename, and 52 new copies: 37 `LICENSE`, 13 `LICENSE-superpowers` and 2 `LICENSE-coding-skills`.

If `skills/write-with-asd-ste100/` exists: when `cmp skills/write-with-asd-ste100/LICENSE LICENSE-write-with-asd-ste100-sources` reports no difference, run `git mv skills/write-with-asd-ste100/LICENSE skills/write-with-asd-ste100/LICENSE-write-with-asd-ste100-sources`; add `'LICENSE-write-with-asd-ste100-sources': ('write-with-asd-ste100',),` to `BUNDLED_LICENSES`; re-point any link in that skill's files to `LICENSE` that means the upstream notices; then re-run the helper.

- [ ] **Step 7: Run the tests, then the gates, and commit.** Same command as Step 2. Expected: `21 passed` (+7). `uv run --python 3.13 python build/check_provenance.py` exits 0.

```bash
bash build/run_commit_lints.sh
```

```bash
git add build/check_provenance.py build/test_check_provenance.py build/cc_guide/conformance.toml NOTICE README.md CLAUDE.md skills
```

```bash
git commit -m "feat(build): every skill carries its license files, checked by check_provenance.py (portability R4.1, R4.2, R4.4)"
```

---

### Task 9: The Andorra lookup (R4.5)

Planning found outcome 1 (DF14): upstream ships an MIT notice. "Never compose a copyright line that is not quoted from the source" (R4.5).

**Files:**
- Create: `LICENSE-andorra` (upstream's text, verbatim) and its copy `skills/bayesian-workflow/LICENSE-andorra`
- Modify: `build/check_provenance.py` (one `BUNDLED_LICENSES` row), `NOTICE` (`bayesian-workflow/` block), `README.md`, `CLAUDE.md`

**Interfaces:**
- Consumes: Task 8's `BUNDLED_LICENSES` and helper.

- [ ] **Step 1: Fetch the notice.** Run `gh api 'repos/Learning-Bayesian-Statistics/baygent-skills/contents/LICENSE?ref=1959ef6f66e5189ab23bd27c83bdf39f94bab6a1' --jq .content > /tmp/portability-plan/andorra.b64`, then `base64 -d -i /tmp/portability-plan/andorra.b64 -o LICENSE-andorra`. Check: `shasum -a 256 LICENSE-andorra` prints `21f3fa613e8b7130156aec53c66616d176112066d08493aaad209e495534b5f5`, and `grep -c 'Copyright (c) 2026 Learning Bayesian Statistics' LICENSE-andorra` prints `1`. If either differs, stop and tell the owner.
- [ ] **Step 2: See the lint fail.** Run `uv run --python 3.13 python build/check_provenance.py`. Expected: exit 1, `LICENSE-andorra: root license file is mapped to no skill in BUNDLED_LICENSES`.
- [ ] **Step 3: Map it, and record it.**

**Edit `build/check_provenance.py`: replace**

```python
    'LICENSE-causal-design-sources': ('recommend-causal-design',),
}
```

**with**

```python
    'LICENSE-causal-design-sources': ('recommend-causal-design',),
    'LICENSE-andorra': ('bayesian-workflow',),
}
```

**Edit `NOTICE`: replace**

```text
    Adapted by Lowell Mason from Alexandre Andorra's original PyMC
    Bayesian-workflow skill. Ported to NumPyro + JAX with expanded
    visualization guidance. MIT licensed.
```

**with**

```text
    Adapted by Lowell Mason from Alexandre Andorra's original PyMC
    Bayesian-workflow skill. Ported to NumPyro + JAX with expanded
    visualization guidance. MIT licensed.
    Upstream is the bayesian-workflow skill in
    https://github.com/Learning-Bayesian-Statistics/baygent-skills, whose
    LICENSE reads "Copyright (c) 2026 Learning Bayesian Statistics"; the
    full upstream MIT text is in LICENSE-andorra. This repository imported
    the skill on 2026-06-20 (2d99584), after upstream's v1.5 (1959ef6,
    2026-06-07); which upstream version was ported is not recorded. That
    LICENSE file is unchanged since upstream's first commit (3681125).
```

**Edit `README.md`: replace**

```markdown
- **My original skills and `bayesian-workflow`** — MIT, © Lowell Mason; full text in [`LICENSE`](LICENSE). (`bayesian-workflow` is an adaptation of Alexandre Andorra's PyMC skill.)
```

**with**

```markdown
- **My original skills and `bayesian-workflow`** — MIT, © Lowell Mason; full text in [`LICENSE`](LICENSE). (`bayesian-workflow` is an adaptation of Alexandre Andorra's PyMC skill; its upstream notice is in [`LICENSE-andorra`](LICENSE-andorra).)
```

**Edit `CLAUDE.md`: replace**

```markdown
- **`bayesian-workflow`** — adapted from Alexandre Andorra's PyMC skill, ported to NumPyro+JAX (MIT).
```

**with**

```markdown
- **`bayesian-workflow`** — adapted from Alexandre Andorra's PyMC skill, ported to NumPyro+JAX (MIT; upstream notice in `LICENSE-andorra`).
```

- [ ] **Step 4: Copy it.** Run `uv run --no-project --python 3.13 python /tmp/portability-plan/copy_licenses.py .`. Then `uv run --python 3.13 python build/check_provenance.py` exits 0.
- [ ] **Step 5: Gates and commit.**

```bash
bash build/run_commit_lints.sh
```

```bash
git add LICENSE-andorra skills/bayesian-workflow/LICENSE-andorra build/check_provenance.py NOTICE README.md CLAUDE.md
```

```bash
git commit -m "docs: bundle Alexandre Andorra's upstream notice with bayesian-workflow (portability R4.5)"
```

---

### Task 10: PEP 723 headers and the header lint (R3.1–R3.4, R3.7)

**Files:**
- Modify: `build/check_frontmatter.py` (imports `ast` and `tomllib`; new `MAIN_GUARD_RE`, `PEP723_RE`, `IMPORT_DISTRIBUTIONS`, `VENDORED_SCRIPTS`, `runnable_scripts`, `script_metadata`, `required_imports`, `check_script_headers`)
- Test: `build/test_check_frontmatter.py` (+8)
- Modify: the 15 header-less runnable scripts (helper script): a shebang where missing, then the header

**Interfaces:**
- Produces: `MAIN_GUARD_RE`; `runnable_scripts(skill_dir: Path) -> list[Path]`; `script_metadata(text: str) -> dict | None` (raises `tomllib.TOMLDecodeError`); `required_imports(tree: ast.Module, siblings: set[str]) -> set[str]`; `check_script_headers(skill_dir: Path, vendored: frozenset[str] = VENDORED_SCRIPTS) -> list[str]`; `VENDORED_SCRIPTS: frozenset[str]`, keyed `skills/<skill>/scripts/<file>`. Task 11 uses `MAIN_GUARD_RE`.

- [ ] **Step 1: Write the failing tests.**

**Edit `build/test_check_frontmatter.py`: replace**

```python
from check_frontmatter import (
    check_agent_file,
```

**with**

```python
from check_frontmatter import (
    check_agent_file,
    check_script_headers,
```

**Edit `build/test_check_frontmatter.py`: insert before the line `def make_agent(tmp_path: Path, name: str, description: str) -> Path:`:**

```python
def _skill_with_script(tmp_path: Path, name: str, script: str, filename: str = 'tool.py') -> Path:
    d = make_skill(tmp_path, name, f'name: {name}\ndescription: Use when testing.')
    (d / 'scripts').mkdir()
    (d / 'scripts' / filename).write_text(script)
    return d


HEADER = "#!/usr/bin/env python3\n# /// script\n# requires-python = '>=3.11'\n# dependencies = []\n# ///\n"
MAIN_GUARD = "\nif __name__ == '__main__':\n    pass\n"


def test_a_runnable_script_needs_a_pep723_block(tmp_path):
    # Portability R3.7: a scripts/*.py with a __main__ guard is runnable.
    d = _skill_with_script(tmp_path, 'bare-script', 'import json\n' + MAIN_GUARD)
    assert check_skill(d) == [
        f"{d / 'scripts' / 'tool.py'}: a runnable script needs a PEP 723 script block, "
        'so uv run can build its environment']


def test_a_script_without_a_main_guard_is_a_library(tmp_path):
    # Like tune-hyperparameters' time_series_cv.py: imported, never run (R3.1).
    assert check_skill(_skill_with_script(tmp_path, 'library-script', 'import numpy\n')) == []


def test_the_block_needs_requires_python_and_dependencies(tmp_path):
    no_deps = _skill_with_script(tmp_path, 'no-deps', "# /// script\n# requires-python = '>=3.11'\n# ///\n" + MAIN_GUARD)
    assert check_skill(no_deps) == [
        f"{no_deps / 'scripts' / 'tool.py'}: the PEP 723 block needs a dependencies list ([] for a stdlib-only script)"]
    no_floor = _skill_with_script(tmp_path, 'no-floor', '# /// script\n# dependencies = []\n# ///\n' + MAIN_GUARD)
    assert check_skill(no_floor) == [f"{no_floor / 'scripts' / 'tool.py'}: the PEP 723 block needs requires-python"]


def test_an_unparseable_block_is_reported(tmp_path):
    d = _skill_with_script(tmp_path, 'bad-toml', '# /// script\n# dependencies = [\n# ///\n' + MAIN_GUARD)
    errs = check_skill(d)
    assert len(errs) == 1 and 'the PEP 723 script block does not parse' in errs[0], errs


def test_every_third_party_import_is_declared(tmp_path):
    # A function-level import counts; the stdlib and a sibling module need nothing.
    body = 'import json\nimport helper\n\ndef read():\n    import polars as pl\n    return pl\n' + MAIN_GUARD
    d = _skill_with_script(tmp_path, 'undeclared', HEADER + body)
    (d / 'scripts' / 'helper.py').write_text('')
    assert check_skill(d) == [
        f"{d / 'scripts' / 'tool.py'}: imports polars, which its PEP 723 dependencies do not declare"]
    declared = HEADER.replace('dependencies = []', "dependencies = ['polars>=2.0']")
    d2 = _skill_with_script(tmp_path, 'declared', declared + body)
    (d2 / 'scripts' / 'helper.py').write_text('')
    assert check_skill(d2) == []


def test_import_names_map_to_distribution_names(tmp_path):
    # yaml ships as PyYAML (the alias table); arviz_base matches arviz-base once
    # both are normalized.
    header = HEADER.replace('dependencies = []', "dependencies = ['PyYAML>=6.0', 'arviz-base>=1.0']")
    script = header + 'import yaml\nfrom arviz_base import from_dict\n' + MAIN_GUARD
    assert check_skill(_skill_with_script(tmp_path, 'aliased', script)) == []
    missing = _skill_with_script(tmp_path, 'alias-missing', HEADER + 'import yaml\n' + MAIN_GUARD)
    assert check_skill(missing) == [
        f"{missing / 'scripts' / 'tool.py'}: imports yaml, which its PEP 723 dependencies do not declare (as pyyaml)"]


def test_an_import_guarded_by_import_error_is_optional(tmp_path):
    # Portability R3.4's exemption: the script runs without it.
    body = 'try:\n    import arviz_stats\nexcept (ImportError, ValueError):\n    arviz_stats = None\n' + MAIN_GUARD
    assert check_skill(_skill_with_script(tmp_path, 'optional', HEADER + body)) == []


def test_a_vendored_script_is_exempt_from_the_header_rules(tmp_path):
    d = _skill_with_script(tmp_path, 'vendored', 'import json\n' + MAIN_GUARD, filename='upstream.py')
    assert check_script_headers(d, vendored=frozenset({'skills/vendored/scripts/upstream.py'})) == []
    assert len(check_script_headers(d)) == 1


```

- [ ] **Step 2: Run them to see them fail.** Run `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_frontmatter.py`. Expected: `1 error`, a collection error: `ImportError: cannot import name 'check_script_headers'`.
- [ ] **Step 3: Implement.**

**Edit `build/check_frontmatter.py`: replace**

```python
- every relative markdown-link target and every backticked references/ or
  scripts/ path exists.
```

**with**

```python
- every relative markdown-link target and every backticked references/ or
  scripts/ path exists;
- every runnable script (a scripts/*.py with a __main__ guard) carries a PEP 723
  block with requires-python and dependencies, and declares every third-party
  import outside a try that catches ImportError (VENDORED_SCRIPTS are exempt).
```

**Edit `build/check_frontmatter.py`: replace**

```python
import argparse
import importlib.util
import re
import sys
```

**with**

```python
import argparse
import ast
import importlib.util
import re
import sys
import tomllib
```

**Edit `build/check_frontmatter.py`: insert after the line `FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---\n', re.S)`:**

```python
# A scripts/*.py with this guard is runnable (portability R3.1).
MAIN_GUARD_RE = re.compile(r'''^if __name__ == ['"]__main__['"]\s*:''', re.M)
# PEP 723's reference regex for an inline script metadata block.
PEP723_RE = re.compile(
    r'(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$')
# Import names whose distribution is named differently. Other names match once
# both sides are normalized (PEP 503), so arviz_base matches arviz-base.
IMPORT_DISTRIBUTIONS = {'yaml': 'pyyaml', 'sklearn': 'scikit-learn', 'PIL': 'pillow'}
# Scripts copied byte for byte from upstream, which cannot carry a header. They
# are exempt from the two header rules only. Keys are skills/<skill>/scripts/<file>.
VENDORED_SCRIPTS: frozenset[str] = frozenset()
```

**Edit `build/check_frontmatter.py`: insert before the line `def check_skill(skill_dir: Path) -> list[str]:`:**

```python
def runnable_scripts(skill_dir: Path) -> list[Path]:
    '''The skill's scripts/*.py files that carry a __main__ guard.'''
    return [p for p in sorted((skill_dir / 'scripts').glob('*.py'))
            if MAIN_GUARD_RE.search(p.read_text())]


def script_metadata(text: str) -> dict | None:
    '''The parsed PEP 723 script block, or None when there is none. Raises
    tomllib.TOMLDecodeError when the block does not parse.'''
    block = next((m for m in PEP723_RE.finditer(text) if m.group('type') == 'script'), None)
    if block is None:
        return None
    content = ''.join(line[2:] if line.startswith('# ') else line[1:]
                      for line in block.group('content').splitlines(keepends=True))
    return tomllib.loads(content)


def _normalize_distribution(name: str) -> str:
    return re.sub(r'[-_.]+', '-', name).lower()


def _catches_import_error(handler: ast.ExceptHandler) -> bool:
    caught = handler.type.elts if isinstance(handler.type, ast.Tuple) else [handler.type]
    return any(isinstance(t, ast.Name) and t.id in ('ImportError', 'ModuleNotFoundError')
               for t in caught)


def required_imports(tree: ast.Module, siblings: set[str]) -> set[str]:
    '''Top-level names of the third-party modules a script imports, at any depth,
    except inside a try that catches ImportError or ModuleNotFoundError (portability
    R3.4: those are optional). The stdlib and sibling modules are left out.'''
    optional: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Try) and any(_catches_import_error(h) for h in node.handlers):
            optional.update(id(sub) for stmt in node.body for sub in ast.walk(stmt))
    names: set[str] = set()
    for node in ast.walk(tree):
        if id(node) in optional:
            continue
        if isinstance(node, ast.Import):
            names.update(alias.name.split('.')[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split('.')[0])
    return {n for n in names if n not in sys.stdlib_module_names and n not in siblings}


def check_script_headers(skill_dir: Path, vendored: frozenset[str] = VENDORED_SCRIPTS) -> list[str]:
    '''Each runnable script carries a PEP 723 block with requires-python and a
    dependencies list that declares every required third-party import
    (portability R3.7), so `uv run <path>` builds the environment it needs.'''
    errs: list[str] = []
    for script in runnable_scripts(skill_dir):
        if f'skills/{skill_dir.name}/scripts/{script.name}' in vendored:
            continue
        text = script.read_text()
        try:
            meta = script_metadata(text)
        except tomllib.TOMLDecodeError as exc:
            errs.append(f'{script}: the PEP 723 script block does not parse ({exc})')
            continue
        if meta is None:
            errs.append(f'{script}: a runnable script needs a PEP 723 script block, '
                        'so uv run can build its environment')
            continue
        if not isinstance(meta.get('requires-python'), str):
            errs.append(f'{script}: the PEP 723 block needs requires-python')
        deps = meta.get('dependencies')
        if not (isinstance(deps, list) and all(isinstance(d, str) for d in deps)):
            errs.append(f'{script}: the PEP 723 block needs a dependencies list ([] for a stdlib-only script)')
            continue
        declared = {_normalize_distribution(re.split(r'[\s<>=!~;\[(]', d.strip(), maxsplit=1)[0])
                    for d in deps}
        siblings = {p.stem for p in script.parent.glob('*.py')}
        for name in sorted(required_imports(ast.parse(text), siblings)):
            dist = IMPORT_DISTRIBUTIONS.get(name, name)
            if _normalize_distribution(dist) not in declared:
                alias = f' (as {dist})' if dist != name else ''
                errs.append(f'{script}: imports {name}, which its PEP 723 dependencies do not declare{alias}')
    return errs


```

**Edit `build/check_frontmatter.py`: replace**

```python
    errs += _check_invocation_parity(skill_dir, fm)
```

**with**

```python
    errs += _check_invocation_parity(skill_dir, fm)
    errs += check_script_headers(skill_dir)
```

- [ ] **Step 4: See the rule catch the real gap.** Same command as Step 2. Expected: `3 failed, 61 passed`; the three are the real-repo tests (`test_real_repo_is_clean`, `test_the_body_warning_goes_to_stderr_and_keeps_exit_zero`, `test_strict_is_off_by_default_and_on_with_the_flag`), and the lint itself names exactly the 15 scripts in Step 5's table, each `a runnable script needs a PEP 723 script block, so uv run can build its environment`.
- [ ] **Step 5: Add the headers** (floors and dependencies: DF3–DF5).

**Create `/tmp/portability-plan/add_headers.py`:**

```python
'''Give each runnable bundled script its PEP 723 header (portability R3.2-R3.4).

Usage: uv run --no-project --python 3.13 python add_headers.py <repo-root>
Adds #!/usr/bin/env python3 as line 1 where missing, then the block. Refuses a
script that already has a block.
'''
import sys
from pathlib import Path

STDLIB = ('>=3.11', [])
POLARS = ('>=3.11', ['polars>=2.0'])
NETCDF = ['h5netcdf>=1.0', 'h5py>=3.0']
HEADERS = {
    'bayesian-workflow/scripts/calibration_check.py': ('>=3.12', [
        'numpy>=2.0', 'arviz-base>=1.0', 'arviz-plots>=1.1', 'arviz-stats>=1.1',
        'xarray>=2026.0', 'scipy>=1.0', *NETCDF, 'matplotlib>=3.0']),
    'bayesian-workflow/scripts/check_diagnostics.py': STDLIB,
    'bayesian-workflow/scripts/diagnose_model.py': ('>=3.12', ['arviz>=1.0', 'numpy>=2.0', *NETCDF]),
    'describe-critique-methodology/scripts/check_decoupling.py': STDLIB,
    'design-architecture/scripts/new_adr.py': STDLIB,
    'explore-data/scripts/profile.py': POLARS,
    'llm-wiki/scripts/bootstrap_wiki.py': STDLIB,
    'llm-wiki/scripts/distill_sessions.py': STDLIB,
    'llm-wiki/scripts/distill_specs.py': STDLIB,
    'llm-wiki/scripts/lint_wiki.py': STDLIB,
    'recommend-probabilistic-model/scripts/characterize.py': POLARS,
    'recommend-visualization/scripts/recommend.py': POLARS,
    'track-model-experiments/scripts/compare_experiments.py': ('>=3.12', ['arviz>=1.0', *NETCDF]),
    'writing-plans/scripts/deferred_stats.py': STDLIB,
    'writing-plans/scripts/entry_check.py': STDLIB,
}
SHEBANG = '#!/usr/bin/env python3'


def header(floor: str, deps: list[str]) -> str:
    listed = '# dependencies = []\n' if not deps else (
        '# dependencies = [\n' + ''.join(f"#   '{d}',\n" for d in deps) + '# ]\n')
    return f"# /// script\n# requires-python = '{floor}'\n{listed}# ///\n"


root = Path(sys.argv[1])
for rel, (floor, deps) in HEADERS.items():
    path = root / 'skills' / rel
    text = path.read_text()
    if '# /// script' in text:
        sys.exit(f'{path}: already has a script block')
    body = text.split('\n', 1)[1] if text.startswith(SHEBANG + '\n') else text
    path.write_text(f'{SHEBANG}\n{header(floor, deps)}{body}')
    print(f'{rel}: {floor} {deps}')
```

Run `uv run --no-project --python 3.13 python /tmp/portability-plan/add_headers.py .`. Expected: 15 lines, one per script.

If `skills/write-with-asd-ste100/scripts/ste-lint.py` exists, add it to `VENDORED_SCRIPTS`: `VENDORED_SCRIPTS: frozenset[str] = frozenset({'skills/write-with-asd-ste100/scripts/ste-lint.py'})`.

- [ ] **Step 6: Run the tests and every changed script suite.** Same command as Step 2. Expected: `64 passed` (+8). Then each suite below passes with the count it had before this task (2026-10-18's counts in brackets):

```bash
uv run --directory skills/describe-critique-methodology/scripts --python 3.13 --with pytest python -m pytest -q
```

```bash
uv run --directory skills/design-architecture/scripts --python 3.13 --with pytest python -m pytest -q
```

```bash
uv run --directory skills/writing-plans/scripts --python 3.13 --with pytest python -m pytest -q
```

```bash
uv run --directory skills/llm-wiki/scripts --python 3.13 --with pytest python -m pytest -q
```

```bash
uv run --directory skills/explore-data/scripts --python 3.13 --with pytest --with polars python -m pytest -q
```

```bash
uv run --directory skills/recommend-probabilistic-model/scripts --python 3.13 --with pytest --with numpy --with polars python -m pytest -q
```

```bash
uv run --directory skills/recommend-visualization/scripts --python 3.13 --with pytest --with numpy --with polars python -m pytest -q
```

```bash
uv run --directory skills/bayesian-workflow/scripts --python 3.13 --with pytest --with arviz --with arviz-stats --with numpy --with xarray python -m pytest -q
```

```bash
uv run --directory skills/track-model-experiments/scripts --python 3.13 --with pytest --with numpy --with polars --with arviz --with numpyro --with h5netcdf --with h5py python -m pytest -q
```

(22, 9, 27, 268, 7, 10, 29, 129 with 3 skipped, 11.)

- [ ] **Step 7: Gates and commit.**

```bash
bash build/run_commit_lints.sh
```

```bash
git add build/check_frontmatter.py build/test_check_frontmatter.py skills
```

```bash
git commit -m "feat(build): PEP 723 headers on every runnable bundled script, and their lint (portability R3.1-R3.4, R3.7)"
```

---

### Task 11: `uv run` invocations and the invocation lint (R3.5, R3.7)

**Files:**
- Modify: `build/check_frontmatter.py` (new `CONTINUATION_RE`, `SCRIPT_PATH_RE`, `RUNNER_RE`, `THIS_SKILL`, `PATH_ALIASES`, `resolve_bundled_script`, `bundled_invocations`, `check_invocations`)
- Test: `build/test_check_frontmatter.py` (+6)
- Modify: 14 markdown files in 11 skills (Step 5), `NOTICE` (one entry)

**Interfaces:**
- Consumes: Task 10's `MAIN_GUARD_RE`.
- Produces: `bundled_invocations(skill_dir: Path) -> list[tuple[Path, str, str]]`, giving (markdown file, runner, path) with runner one of `'python'`, `'python3'` or `'uv run'`; Task 12 reads it. `check_invocations(skill_dir: Path) -> list[str]`; `resolve_bundled_script(path: str, skill_dir: Path) -> Path | None`.

- [ ] **Step 1: Write the failing tests.**

**Edit `build/test_check_frontmatter.py`: replace**

```python
from check_frontmatter import (
    check_agent_file,
```

**with**

```python
from check_frontmatter import (
    bundled_invocations,
    check_agent_file,
    check_invocations,
```

**Edit `build/test_check_frontmatter.py`: insert before the line `def make_agent(tmp_path: Path, name: str, description: str) -> Path:`:**

````python
RUNNABLE = HEADER + MAIN_GUARD


def _skill_running(tmp_path: Path, name: str, body: str, md: str = 'SKILL.md') -> Path:
    '''A skill with a runnable scripts/tool.py, whose markdown file md holds body.'''
    d = _skill_with_script(tmp_path, name, RUNNABLE)
    path = d / md
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text((path.read_text() if path.exists() else '') + body)
    return d


def test_python_before_a_bundled_script_is_flagged(tmp_path):
    # Portability R3.5, R3.7: uv run <path> reads the header; python does not.
    d = _skill_running(tmp_path, 'bare', '```bash\npython <this-skill-dir>/scripts/tool.py --x 1\n```\n')
    assert check_invocations(d) == [
        f"{d / 'SKILL.md'}: runs <this-skill-dir>/scripts/tool.py with python; "
        "use uv run <this-skill-dir>/scripts/tool.py, which reads the script's PEP 723 header"]


def test_python3_and_uv_run_python_are_flagged_too(tmp_path):
    # uv run ... python <path> runs the project environment, not the header's.
    body = ('Run `python3 scripts/tool.py`, or\n'
            '`uv run --python 3.13 --with polars python <this-skill-dir>/scripts/tool.py`.\n')
    runners = [runner for _, runner, _ in bundled_invocations(_skill_running(tmp_path, 'forms', body))]
    assert runners == ['python3', 'python']


def test_a_line_continued_invocation_is_joined_first(tmp_path):
    d = _skill_running(tmp_path, 'continued', '```bash\npython \\\n    <this-skill-dir>/scripts/tool.py \\\n    --x 1\n```\n')
    assert [runner for _, runner, _ in bundled_invocations(d)] == ['python']


def test_uv_run_of_a_bundled_script_passes(tmp_path):
    d = _skill_running(tmp_path, 'uv-form', '```bash\nuv run <this-skill-dir>/scripts/tool.py --x 1\n```\n')
    assert check_invocations(d) == []
    assert bundled_invocations(d) == [(d / 'SKILL.md', 'uv run', '<this-skill-dir>/scripts/tool.py')]


def test_a_path_that_is_no_runnable_bundled_script_is_not_flagged(tmp_path):
    # A teaching example (no such file) and a library (no __main__ guard).
    d = _skill_running(tmp_path, 'examples', 'Run `python scripts/migrate.py`, then `python scripts/lib.py`.\n')
    (d / 'scripts' / 'lib.py').write_text('X = 1\n')
    assert bundled_invocations(d) == []


def test_paths_resolve_across_skills_aliases_and_references(tmp_path):
    # The R3.5 path forms: a sibling skill, the llm-wiki install root, a clone
    # path, a repo-relative path, and an invocation in references/.
    other = _skill_with_script(tmp_path, 'other', RUNNABLE)
    wiki = _skill_with_script(tmp_path, 'llm-wiki', RUNNABLE, filename='lint_wiki.py')
    body = ('`python <this-skill-dir>/../other/scripts/tool.py`\n'
            '`python3 "$LLM_WIKI_ROOT/scripts/lint_wiki.py"`\n'
            '`python3 ~/Projects/agent-skills/skills/other/scripts/tool.py`\n')
    d = _skill_running(tmp_path, 'caller', body)
    (d / 'references').mkdir()
    (d / 'references' / 'usage.md').write_text('`python skills/other/scripts/tool.py`\n')
    assert [(md.name, path) for md, _, path in bundled_invocations(d)] == [
        ('SKILL.md', '<this-skill-dir>/../other/scripts/tool.py'),
        ('SKILL.md', '$LLM_WIKI_ROOT/scripts/lint_wiki.py'),
        ('SKILL.md', '~/Projects/agent-skills/skills/other/scripts/tool.py'),
        ('usage.md', 'skills/other/scripts/tool.py')]
    assert other.is_dir() and wiki.is_dir()


````

- [ ] **Step 2: Run them to see them fail.** Run `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_frontmatter.py`. Expected: `1 error`, a collection error: `ImportError: cannot import name 'bundled_invocations'`.
- [ ] **Step 3: Implement.**

**Edit `build/check_frontmatter.py`: replace**

```python
  import outside a try that catches ImportError (VENDORED_SCRIPTS are exempt).
```

**with**

```python
  import outside a try that catches ImportError (VENDORED_SCRIPTS are exempt);
- no markdown in the skill runs a runnable bundled script with python or python3,
  line continuations joined: the form is uv run <path>.
```

**Edit `build/check_frontmatter.py`: insert after the line `VENDORED_SCRIPTS: frozenset[str] = frozenset()`:**

```python
# A backslash line continuation, joined before the invocation scan so that
# python \ with the path on the next line is caught (portability R3.7).
CONTINUATION_RE = re.compile(r'\\\n[ \t]*')
# A documented path to a bundled script: <owner>/scripts/<file>.py or scripts/<file>.py.
SCRIPT_PATH_RE = re.compile(r'''(?:[^\s"'`()]*/)?scripts/[\w.-]+\.py''')
# The runner word right before a script path, after an optional opening quote.
RUNNER_RE = re.compile(r'''(?:^|[\s`(])(?P<runner>python3?|uv run)\s+["']?$''')
# How a skill's markdown names its own directory.
THIS_SKILL = '<this-skill-dir>'
# Path owners that stand for a skill under another name: a wiki root's
# scripts/ holds the copies llm-wiki's bootstrap_wiki.py installs.
PATH_ALIASES = {'$LLM_WIKI_ROOT': 'llm-wiki'}
```

**Edit `build/check_frontmatter.py`: insert before the line `def check_skill(skill_dir: Path) -> list[str]:`:**

```python
def resolve_bundled_script(path: str, skill_dir: Path) -> Path | None:
    '''The runnable bundled script a documented path names, or None. The owner
    before scripts/ is THIS_SKILL, a PATH_ALIASES key or a skill directory
    name; a bare scripts/<file>.py is this skill's.'''
    parts = path.split('/')
    owner = parts[-3] if len(parts) >= 3 else THIS_SKILL
    skill = skill_dir.name if owner == THIS_SKILL else PATH_ALIASES.get(owner, owner)
    script = skill_dir.parent / skill / 'scripts' / parts[-1]
    if script.is_file() and MAIN_GUARD_RE.search(script.read_text()):
        return script
    return None


def bundled_invocations(skill_dir: Path) -> list[tuple[Path, str, str]]:
    '''(markdown file, runner, path) for each place the skill's markdown runs a
    runnable bundled script with python, python3 or uv run, in file order.'''
    found = []
    for md in sorted(skill_dir.rglob('*.md')):
        text = CONTINUATION_RE.sub(' ', md.read_text())
        for m in SCRIPT_PATH_RE.finditer(text):
            line_start = text.rfind('\n', 0, m.start()) + 1
            runner = RUNNER_RE.search(text[line_start:m.start()])
            if runner and resolve_bundled_script(m.group(), skill_dir):
                found.append((md, runner.group('runner'), m.group()))
    return found


def check_invocations(skill_dir: Path) -> list[str]:
    '''The skill's markdown runs each bundled script as uv run <path>, which
    reads the script's header, never with python or python3 (portability R3.5).'''
    return [f"{md}: runs {path} with {runner}; use uv run {path}, which reads the script's PEP 723 header"
            for md, runner, path in bundled_invocations(skill_dir) if runner != 'uv run']


```

**Edit `build/check_frontmatter.py`: replace**

```python
    errs += check_script_headers(skill_dir)
```

**with**

```python
    errs += check_script_headers(skill_dir)
    errs += check_invocations(skill_dir)
```

- [ ] **Step 4: See the rule catch the real invocations.** Same command as Step 2. Expected: `3 failed, 67 passed` (the three real-repo tests). `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py` reports 28 invocations:

| File | Lines |
|---|---|
| `skills/bayesian-workflow/SKILL.md` | 3 (`python`) |
| `skills/bayesian-workflow/references/diagnostics.md` | 1 (`python`) |
| `skills/describe-critique-methodology/SKILL.md` | 1 (`python3`) |
| `skills/design-architecture/SKILL.md` | 3 (`python3`) |
| `skills/explore-data/SKILL.md` | 1 (`python`) |
| `skills/finishing-a-development-branch/SKILL.md` | 1 (`python`) |
| `skills/llm-wiki/SKILL.md` | 6 (`python3`) |
| `skills/llm-wiki/INSTALL.md` | 6 (`python3`) |
| `skills/recommend-visualization/SKILL.md` | 2 (`python`) |
| `skills/track-model-experiments/SKILL.md` | 1 (`python`) |
| `skills/writing-plans/SKILL.md` | 2 (`python`) |
| `skills/writing-plans/references/deferred-backlog.md` | 1 (`python`) |

- [ ] **Step 5: Rewrite the invocations,** with R3.5's sentence once per skill (DF8). `geographic-codes` and `classification-codes` already use `uv run` and gain only the sentence.

**Edit `skills/bayesian-workflow/SKILL.md`: replace**

```markdown
# 1. Run convergence + LOO + PPC checks (writes diagnostics.json)
python <this-skill-dir>/scripts/diagnose_model.py --idata <slug>/inference_data.nc --output <slug>/diagnostics.json
```

**with**

```markdown
# 1. Run convergence + LOO + PPC checks (writes diagnostics.json)
uv run <this-skill-dir>/scripts/diagnose_model.py --idata <slug>/inference_data.nc --output <slug>/diagnostics.json
```

**Edit `skills/bayesian-workflow/SKILL.md`: replace**

```markdown
#    with --loo-pit the figures are loo_pit_ecdf.png + loo_pit_coverage.png instead)
python <this-skill-dir>/scripts/calibration_check.py --idata <slug>/inference_data.nc --output <slug>/calibration.json --save-plots --plot-dir <slug>/
```

**with**

```markdown
#    with --loo-pit the figures are loo_pit_ecdf.png + loo_pit_coverage.png instead)
uv run <this-skill-dir>/scripts/calibration_check.py --idata <slug>/inference_data.nc --output <slug>/calibration.json --save-plots --plot-dir <slug>/
```

**Edit `skills/bayesian-workflow/SKILL.md`: replace**

```markdown
# 3. Interpret the JSON outputs into qualitative ratings + suggested next steps
python <this-skill-dir>/scripts/check_diagnostics.py --diagnostics <slug>/diagnostics.json --calibration <slug>/calibration.json --output <slug>/check_report.json
```

**with**

```markdown
# 3. Interpret the JSON outputs into qualitative ratings + suggested next steps
uv run <this-skill-dir>/scripts/check_diagnostics.py --diagnostics <slug>/diagnostics.json --calibration <slug>/calibration.json --output <slug>/check_report.json
```

**Edit `skills/bayesian-workflow/SKILL.md`: replace**

````markdown
```

Step 3 is what powers the `report.md` Assessment lines and Suggested Next Steps section — never hand-roll those interpretations from raw R-hat / ESS / pareto-k numbers when the harness can produce them consistently.
````

**with**

````markdown
```

Without uv, run the same path with `python3` in an environment that has the dependencies listed in the script's header.

Step 3 is what powers the `report.md` Assessment lines and Suggested Next Steps section — never hand-roll those interpretations from raw R-hat / ESS / pareto-k numbers when the harness can produce them consistently.
````

**Edit `skills/bayesian-workflow/references/diagnostics.md`: replace**

```markdown
python <this-skill-dir>/scripts/diagnose_model.py --idata model_output.nc
```

**with**

```markdown
uv run <this-skill-dir>/scripts/diagnose_model.py --idata model_output.nc
```

**Edit `skills/describe-critique-methodology/SKILL.md`: replace**

````markdown
   python3 <this-skill-dir>/scripts/check_decoupling.py specs/<name>-methodology.md
   ```

````

**with**

````markdown
   uv run <this-skill-dir>/scripts/check_decoupling.py specs/<name>-methodology.md
   ```

   Without uv, run the same path with `python3` in an environment that has the
   dependencies listed in the script's header.

````

**Edit `skills/design-architecture/SKILL.md`: replace**

```markdown
2. **Pick the number and file** (or run `python3 <this-skill-dir>/scripts/new_adr.py "<title>"`).
```

**with**

```markdown
2. **Pick the number and file** (or run `uv run <this-skill-dir>/scripts/new_adr.py "<title>"`).
```

**Edit `skills/design-architecture/SKILL.md`: replace**

````markdown
# (stdlib-only, so plain python3 suffices; <this-skill-dir> resolves to an absolute path,
# so it works from any repo cwd)
python3 <this-skill-dir>/scripts/new_adr.py "Use NumPyro/JAX over PyMC for nowcasting"
python3 <this-skill-dir>/scripts/new_adr.py "Store parquet levels only" --dir docs/adr --status Proposed
```

````

**with**

````markdown
# (<this-skill-dir> resolves to an absolute path, so it works from any repo cwd)
uv run <this-skill-dir>/scripts/new_adr.py "Use NumPyro/JAX over PyMC for nowcasting"
uv run <this-skill-dir>/scripts/new_adr.py "Store parquet levels only" --dir docs/adr --status Proposed
```

Without uv, run the same path with `python3` in an environment that has the dependencies listed
in the script's header.

````

**Edit `skills/explore-data/SKILL.md`: replace**

```markdown
uv run --python 3.13 --with polars python \
    <this-skill-dir>/scripts/profile.py \
```

**with**

```markdown
uv run <this-skill-dir>/scripts/profile.py \
```

**Edit `skills/explore-data/SKILL.md`: replace**

````markdown
    --json profile.json
```

## This skill vs. its siblings
````

**with**

````markdown
    --json profile.json
```

Without uv, run the same path with `python3` in an environment that has the dependencies listed
in the script's header.

## This skill vs. its siblings
````

**Edit `skills/finishing-a-development-branch/SKILL.md`: replace**

````markdown
uv run --no-project --python 3.13 python <this-skill-dir>/../writing-plans/scripts/deferred_stats.py
```

````

**with**

````markdown
uv run <this-skill-dir>/../writing-plans/scripts/deferred_stats.py
```

Without uv, run the same path with `python3` in an environment that has the
dependencies listed in the script's header.

````

**Edit `skills/geographic-codes/SKILL.md`: replace**

````markdown
uv run skills/geographic-codes/scripts/build.py --list     # the pinned sources
```

````

**with**

````markdown
uv run skills/geographic-codes/scripts/build.py --list     # the pinned sources
```

Without uv, run the same path with `python3` in an environment that has the dependencies listed
in the script's header.

````

**Edit `skills/classification-codes/SKILL.md`: replace**

````markdown
cd skills/classification-codes/scripts && uv run --python 3.13 --with pytest --with polars --with fastexcel python -m pytest -q
```

`scripts/build.py` pins the official Census/BLS URLs, handles the known layout quirks (preamble
````

**with**

````markdown
cd skills/classification-codes/scripts && uv run --python 3.13 --with pytest --with polars --with fastexcel python -m pytest -q
```

Without uv, run the same path with `python3` in an environment that has the dependencies listed
in the script's header.

`scripts/build.py` pins the official Census/BLS URLs, handles the known layout quirks (preamble
````

**Edit `skills/llm-wiki/SKILL.md`: replace**

```markdown
   argument: `python3 <this-skill-dir>/scripts/bootstrap_wiki.py <root>`.
```

**with**

```markdown
   argument: `uv run <this-skill-dir>/scripts/bootstrap_wiki.py <root>`.
   Without uv, run the same path with `python3` in an environment that has the
   dependencies listed in the script's header.
```

**Edit `skills/llm-wiki/SKILL.md`: replace**

```markdown
- Run `python3 $LLM_WIKI_ROOT/scripts/lint_wiki.py` (mechanical) before any
```

**with**

```markdown
- Run `uv run $LLM_WIKI_ROOT/scripts/lint_wiki.py` (mechanical) before any
```

**Edit `skills/llm-wiki/SKILL.md`: replace**

```markdown
   with `python3 $LLM_WIKI_ROOT/scripts/distill_sessions.py --source claude-code
```

**with**

```markdown
   with `uv run $LLM_WIKI_ROOT/scripts/distill_sessions.py --source claude-code
```

**Edit `skills/llm-wiki/SKILL.md`: replace**

```markdown
1. **Mechanical:** run `python3 $LLM_WIKI_ROOT/scripts/lint_wiki.py` (add
```

**with**

```markdown
1. **Mechanical:** run `uv run $LLM_WIKI_ROOT/scripts/lint_wiki.py` (add
```

**Edit `skills/llm-wiki/SKILL.md`: replace**

```markdown
1. Inventory (mechanical): `python3 $LLM_WIKI_ROOT/scripts/distill_specs.py
```

**with**

```markdown
1. Inventory (mechanical): `uv run $LLM_WIKI_ROOT/scripts/distill_specs.py
```

**Edit `skills/llm-wiki/SKILL.md`: replace**

```markdown
6. Assemble: `python3 $LLM_WIKI_ROOT/scripts/distill_specs.py assemble
```

**with**

```markdown
6. Assemble: `uv run $LLM_WIKI_ROOT/scripts/distill_specs.py assemble
```

**Edit `skills/llm-wiki/INSTALL.md`: replace**

```markdown
- **Python 3.12 or newer** on `PATH` as `python3`. The wiki scripts are
  standard-library only — nothing to `pip install` to *use* the wiki. (`uv` is
  needed only to run the bundled test suite, below, which you can skip.)
```

**with**

```markdown
- **uv** on `PATH`. The commands below run each wiki script as `uv run <path>`;
  the script's header gives uv its Python floor (3.11 or newer) and its
  dependencies (none: the scripts are standard-library only). Without uv, run
  the same path with `python3` 3.11 or newer.
- **`python3`** on `PATH`, for the installer in step 2 (or link the skill by
  hand, as step 2 shows).
```

**Edit `skills/llm-wiki/INSTALL.md`: replace**

```markdown
python3 ~/Projects/agent-skills/skills/llm-wiki/scripts/bootstrap_wiki.py ~/work-wiki
```

**with**

```markdown
uv run ~/Projects/agent-skills/skills/llm-wiki/scripts/bootstrap_wiki.py ~/work-wiki
```

**Edit `skills/llm-wiki/INSTALL.md`: replace**

```markdown
python3 ~/Projects/agent-skills/skills/llm-wiki/scripts/bootstrap_wiki.py ~/work-wiki \
```

**with**

```markdown
uv run ~/Projects/agent-skills/skills/llm-wiki/scripts/bootstrap_wiki.py ~/work-wiki \
```

**Edit `skills/llm-wiki/INSTALL.md`: replace**

```markdown
python3 "$LLM_WIKI_ROOT/scripts/lint_wiki.py" "$LLM_WIKI_ROOT"
```

**with**

```markdown
uv run "$LLM_WIKI_ROOT/scripts/lint_wiki.py" "$LLM_WIKI_ROOT"
```

**Edit `skills/llm-wiki/INSTALL.md`: replace**

```markdown
python3 ~/Projects/agent-skills/skills/llm-wiki/scripts/bootstrap_wiki.py "$LLM_WIKI_ROOT" --check
```

**with**

```markdown
uv run ~/Projects/agent-skills/skills/llm-wiki/scripts/bootstrap_wiki.py "$LLM_WIKI_ROOT" --check
```

**Edit `skills/llm-wiki/INSTALL.md`: replace**

```markdown
python3 ~/Projects/agent-skills/skills/llm-wiki/scripts/bootstrap_wiki.py "$LLM_WIKI_ROOT" --force
```

**with**

```markdown
uv run ~/Projects/agent-skills/skills/llm-wiki/scripts/bootstrap_wiki.py "$LLM_WIKI_ROOT" --force
```

**Edit `skills/llm-wiki/INSTALL.md`: replace**

```markdown
python3 "$LLM_WIKI_ROOT/scripts/distill_sessions.py" --source claude-code \
```

**with**

```markdown
uv run "$LLM_WIKI_ROOT/scripts/distill_sessions.py" --source claude-code \
```

**Edit `skills/recommend-visualization/SKILL.md`: replace**

````markdown
uv run --python 3.13 --with polars python \
    <this-skill-dir>/../explore-data/scripts/profile.py data.parquet --json profile.json
uv run --python 3.13 --with polars python \
    <this-skill-dir>/scripts/recommend.py data.parquet \
    --profile profile.json --intent correlation
```
````

**with**

````markdown
uv run <this-skill-dir>/../explore-data/scripts/profile.py data.parquet --json profile.json
uv run <this-skill-dir>/scripts/recommend.py data.parquet \
    --profile profile.json --intent correlation
```

Without uv, run the same path with `python3` in an environment that has the dependencies listed
in the script's header.
````

**Edit `skills/track-model-experiments/SKILL.md`: replace**

````markdown
uv run --python 3.13 --with numpyro --with arviz --with arviz-stats --with numpy \
  --with h5netcdf --with h5py python <this-skill-dir>/scripts/compare_experiments.py \
  --analysis-dir <analysis-dir> --ledger <analysis-dir>/experiments.md --output comparison.json
```

Run `--help` for the rest (`--folders` compares an explicit subset instead of
auto-discovering every `*/inference_data.nc` under `--analysis-dir`). The
`h5netcdf`/`h5py` pair is required — `az.from_netcdf` needs a netCDF backend
that does not install transitively with `arviz`.
````

**with**

````markdown
uv run <this-skill-dir>/scripts/compare_experiments.py \
  --analysis-dir <analysis-dir> --ledger <analysis-dir>/experiments.md --output comparison.json
```

Without uv, run the same path with `python3` in an environment that has the
dependencies listed in the script's header. The header declares the
`h5netcdf`/`h5py` pair because `az.from_netcdf` needs a netCDF backend that
does not install transitively with `arviz`.

Run `--help` for the rest (`--folders` compares an explicit subset instead of
auto-discovering every `*/inference_data.nc` under `--analysis-dir`).
````

**Edit `skills/writing-plans/SKILL.md`: replace**

```markdown
**Save plans to:** `specs/plans/<id>-<spec-name>.md` — `<id>` is the `next free:` id that `uv run --no-project --python 3.13 python <this-skill-dir>/scripts/entry_check.py` prints under `plan ids:`, run from the repo root. It reads every branch, remote-tracking ref and worktree, untracked plans included, because ids are allocated per branch and collide. A collision it reports is your human partner's call. `<spec-name>` matches the spec the plan implements. When the plan is fully executed, run the Plan Completion Protocol (below).
```

**with**

```markdown
**Save plans to:** `specs/plans/<id>-<spec-name>.md` — `<id>` is the `next free:` id that `uv run <this-skill-dir>/scripts/entry_check.py` prints under `plan ids:`, run from the repo root. Without uv, run the same path with `python3` in an environment that has the dependencies listed in the script's header. The script reads every branch, remote-tracking ref and worktree, untracked plans included, because ids are allocated per branch and collide. A collision it reports is your human partner's call. `<spec-name>` matches the spec the plan implements. When the plan is fully executed, run the Plan Completion Protocol (below).
```

**Edit `skills/writing-plans/SKILL.md`: replace**

```markdown
uv run --no-project --python 3.13 python <this-skill-dir>/scripts/deferred_stats.py
```

**with**

```markdown
uv run <this-skill-dir>/scripts/deferred_stats.py
```

**Edit `skills/writing-plans/references/deferred-backlog.md`: replace**

````markdown
Run from the repo root. `--no-project` stops uv from binding the run to that
repo's own project, whose `requires-python` may exclude 3.13; the script is
stdlib-only and needs no project environment.

```bash
uv run --no-project --python 3.13 python <this-skill-dir>/scripts/deferred_stats.py
```
````

**with**

````markdown
Run from the repo root. The script's PEP 723 header gives it an environment of
its own under `uv run`, so that repo's own project, whose `requires-python`
may not admit the script's Python, plays no part.

```bash
uv run <this-skill-dir>/scripts/deferred_stats.py
```
````

If `skills/write-with-asd-ste100/` exists, the lint flags its `python3 <this-skill-dir>/scripts/ste-lint.py` call. Stop and ask the owner (Couplings, item 4) which of two changes to make. Either exempt vendored scripts from the invocation rule: in `check_invocations`, skip a path whose `resolve_bundled_script` result, as `skills/<skill>/scripts/<file>`, is in `VENDORED_SCRIPTS`, with a RED test first that a vendored copy run with `python3` passes. Or rewrite the call to `uv run <this-skill-dir>/scripts/ste-lint.py …`, with R3.5's sentence once, right after it.

- [ ] **Step 6: Record the superpowers change in NOTICE.**

**Edit `NOTICE`: replace**

```text
    `disable-model-invocation` and `agent` are accepted.
```

**with**

```text
    `disable-model-invocation` and `agent` are accepted.
  - writing-plans and finishing-a-development-branch ran the
    deferred_stats.py and entry_check.py reporters as `uv run --no-project
    --python 3.13 python <path>`. They now run `uv run <path>`, which
    reads the PEP 723 header each script gained, and each SKILL.md gained
    one sentence on running the same path with `python3` where uv is
    absent (specs/agent-skills-portability-spec.md, R3.5). The same
    change in references/deferred-backlog.md, and the two headers, are to
    the original works named above.
```

- [ ] **Step 7: Run the tests.** Same command as Step 2. Expected: `70 passed` (+6).
- [ ] **Step 8: Gates and commit.** The dependency-drift lint passes unchanged (R3.9): no cross-skill reference was added or dropped.

```bash
bash build/run_commit_lints.sh
```

```bash
git add build/check_frontmatter.py build/test_check_frontmatter.py NOTICE skills
```

```bash
git commit -m "feat(skills): run bundled scripts with uv run, and lint the form (portability R3.5, R3.7)"
```

---

### Task 12: `compatibility` and the prose floors (R3.3, R3.6, R3.7)

**Files:**
- Modify: `build/check_frontmatter.py` (new `UV_WORD_RE`, `_check_compatibility_names_uv`)
- Test: `build/test_check_frontmatter.py` (+2)
- Modify: the 11 SKILL.md files of the skills that run a bundled script (helper script); `skills/recommend-visualization/SKILL.md` and `skills/recommend-probabilistic-model/SKILL.md` (prose floors); `NOTICE`

**Interfaces:**
- Consumes: Task 11's `bundled_invocations`.
- Produces: `_check_compatibility_names_uv(skill_dir: Path, fm: dict) -> list[str]`, called from `check_skill`.

- [ ] **Step 1: Write the failing tests.**

**Edit `build/test_check_frontmatter.py`: insert before the line `def make_agent(tmp_path: Path, name: str, description: str) -> Path:`:**

````python
UV_COMPATIBILITY = 'Requires uv to run bundled scripts (dependencies are declared inline); Python 3.11+.'


def _uv_skill(tmp_path: Path, name: str, extra: str = '') -> Path:
    '''A skill whose SKILL.md runs its bundled scripts/tool.py with uv run.'''
    d = make_skill(tmp_path, name, f'name: {name}\ndescription: Use when testing.{extra}')
    (d / 'scripts').mkdir()
    (d / 'scripts' / 'tool.py').write_text(RUNNABLE)
    with (d / 'SKILL.md').open('a') as f:
        f.write('```bash\nuv run <this-skill-dir>/scripts/tool.py\n```\n')
    return d


def test_a_uv_run_invocation_needs_compatibility_naming_uv(tmp_path):
    # Portability R3.6-R3.7. uv must be a word: cuvid does not name it.
    for name, extra in (('no-compat', ''), ('no-uv', '\ncompatibility: Python 3.11+.'),
                        ('uv-inside-a-word', '\ncompatibility: Needs cuvid.')):
        d = _uv_skill(tmp_path, name, extra)
        assert check_skill(d) == [
            f"{d / 'SKILL.md'}: its markdown runs a bundled script with uv run, so compatibility must name uv"], name
    assert check_skill(_uv_skill(tmp_path, 'named', f'\ncompatibility: {UV_COMPATIBILITY}')) == []


def test_compatibility_is_optional_when_no_markdown_runs_a_script(tmp_path):
    # A guard, green before and after: recommend-probabilistic-model bundles
    # characterize.py but its markdown never runs it.
    assert check_skill(_skill_with_script(tmp_path, 'unrun', RUNNABLE)) == []


````

- [ ] **Step 2: Run them to see them fail.** Run `uv run --directory build --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_frontmatter.py`. Expected: `1 failed, 71 passed`. The new `test_compatibility_is_optional_when_no_markdown_runs_a_script` is a guard: it passes before and after.
- [ ] **Step 3: Implement.**

**Edit `build/check_frontmatter.py`: replace**

```python
  line continuations joined: the form is uv run <path>.
```

**with**

```python
  line continuations joined: the form is uv run <path>;
- a skill whose markdown runs a bundled script with uv run names uv in
  compatibility.
```

**Edit `build/check_frontmatter.py`: insert after the line `PATH_ALIASES = {'$LLM_WIKI_ROOT': 'llm-wiki'}`:**

```python
# compatibility names uv as a word (portability R3.6).
UV_WORD_RE = re.compile(r'\buv\b')
```

**Edit `build/check_frontmatter.py`: insert before the line `def check_skill(skill_dir: Path) -> list[str]:`:**

```python
def _check_compatibility_names_uv(skill_dir: Path, fm: dict) -> list[str]:
    '''A skill whose markdown runs a bundled script with uv run names uv in
    compatibility (portability R3.6-R3.7), so a host can tell it needs uv.'''
    if not any(runner == 'uv run' for _, runner, _ in bundled_invocations(skill_dir)):
        return []
    if UV_WORD_RE.search(str(fm.get('compatibility') or '')):
        return []
    return [f"{skill_dir / 'SKILL.md'}: its markdown runs a bundled script with uv run, "
            'so compatibility must name uv']


```

**Edit `build/check_frontmatter.py`: replace**

```python
    errs += check_invocations(skill_dir)
```

**with**

```python
    errs += check_invocations(skill_dir)
    errs += _check_compatibility_names_uv(skill_dir, fm)
```

- [ ] **Step 4: See the rule catch the real gap.** Same command as Step 2. Expected: `3 failed, 69 passed`. The lint names the 11 skills in Step 5's helper, each `its markdown runs a bundled script with uv run, so compatibility must name uv`.
- [ ] **Step 5: Declare `compatibility`.** 3.X is the highest `requires-python` floor among the scripts each skill runs (R3.6).

**Create `/tmp/portability-plan/add_compatibility.py`:**

```python
'''Give each skill whose markdown runs a bundled script with uv run its R3.6 compatibility value.

Usage: uv run --no-project --python 3.13 python add_compatibility.py <repo-root>
Inserts the line right after the frontmatter's license: line, so a # cc-guide:
line stays last. 3.X is the highest requires-python floor among the scripts the
skill runs. Refuses a SKILL.md that already has a compatibility key.
'''
import re
import sys
from pathlib import Path

FLOORS = {
    'bayesian-workflow': '3.12', 'track-model-experiments': '3.12',
    'classification-codes': '3.11', 'describe-critique-methodology': '3.11',
    'design-architecture': '3.11', 'explore-data': '3.11',
    'finishing-a-development-branch': '3.11', 'geographic-codes': '3.11',
    'llm-wiki': '3.11', 'recommend-visualization': '3.11', 'writing-plans': '3.11',
}
VALUE = 'Requires uv to run bundled scripts (dependencies are declared inline); Python {}+.'
LICENSE_LINE = re.compile(r'^license: .*\n', re.M)

root = Path(sys.argv[1])
for skill, floor in FLOORS.items():
    path = root / 'skills' / skill / 'SKILL.md'
    text = path.read_text()
    frontmatter_end = text.index('\n---\n', 4)
    if re.search(r'^compatibility:', text[:frontmatter_end], re.M):
        sys.exit(f'{path}: already has a compatibility key')
    m = LICENSE_LINE.search(text, 0, frontmatter_end)
    if m is None:
        sys.exit(f'{path}: no license line in the frontmatter')
    path.write_text(f'{text[:m.end()]}compatibility: {VALUE.format(floor)}\n{text[m.end():]}')
    print(f'{skill}: Python {floor}+')
```

Run `uv run --no-project --python 3.13 python /tmp/portability-plan/add_compatibility.py .`. Expected: 11 lines.

If the owner chose `uv run` for write-with-asd-ste100's linter in Task 11, give that skill `compatibility: Requires uv to run bundled scripts (dependencies are declared inline); Python 3.9+.` on the line after its `license:` line (Couplings, item 5).

- [ ] **Step 6: Align the prose floors, and extend NOTICE's entry.**

**Edit `skills/recommend-visualization/SKILL.md`: replace**

```markdown
- The skill is **markdown** — Phase 0/1 need only `polars` (and `recommend.py`, Python ≥ 3.9).
```

**with**

```markdown
- The skill is **markdown** — Phase 0/1 need only `polars` (and `recommend.py`, Python ≥ 3.11).
```

**Edit `skills/recommend-probabilistic-model/SKILL.md`: replace**

```markdown
- `scripts/characterize.py` needs `polars` (Python ≥ 3.9).
```

**with**

```markdown
- `scripts/characterize.py` needs `polars` (Python ≥ 3.11).
```

**Edit `NOTICE`: replace**

```text
    change in references/deferred-backlog.md, and the two headers, are to
    the original works named above.
```

**with**

```text
    change in references/deferred-backlog.md, and the two headers, are to
    the original works named above. Both SKILL.md files also gained a
    `compatibility` field naming uv (R3.6).
```

- [ ] **Step 7: Run the tests.** Same command as Step 2. Expected: `72 passed` (+2). `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py --strict` still names exactly Task 7's three skills: `compatibility` is a spec key.
- [ ] **Step 8: Gates and commit.**

```bash
bash build/run_commit_lints.sh
```

```bash
git add build/check_frontmatter.py build/test_check_frontmatter.py NOTICE skills
```

```bash
git commit -m "feat(skills): declare compatibility where a skill runs a bundled script (portability R3.3, R3.6, R3.7)"
```

---

### Task 13: The execution proof (R3.8)

Run once, and record the result in this plan's completion notes.

**Files:**
- Modify: this plan, `specs/plans/53-agent-skills-portability.md` (Plan completion notes, "R3.8 execution proof")
- Scratch: `/tmp/portability-plan/r38.sh`; the run's directory `/tmp/portability-r38/` (the script refuses an existing one)

**Interfaces:**
- Consumes: Tasks 10–12's headers.
- Produces: Validation 4's record.

- [ ] **Step 1: Create the script.**

**Create `/tmp/portability-plan/r38.sh`:**

```bash
#!/bin/bash
# Portability R3.8 execution proof: run every runnable bundled script once as
# `uv run -v <absolute path>` on a minimal real input, from a new scratch
# directory, and log its exit code and the interpreter uv chose. Then run one
# script inside a hostile project, with a header-less copy as the control.
# Usage: r38.sh <repo-root> <new-scratch-dir>   (the scratch dir must not exist)
set -u
R="$(cd "$1" && pwd)"; S="$2"; K="$R/skills"
case "$S" in /tmp|/tmp/|/private/tmp|/private/tmp/) echo 'refusing: never /tmp itself'; exit 2;; esac
[ -e "$S" ] && { echo "refusing: $S exists"; exit 2; }
mkdir -p "$S/plots" && cd "$S" || exit 2
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
LOG="$S/r38.log"; : > "$LOG"
run() {  # run <label> <command...>: one log line with the exit code and interpreter
  local label="$1"; shift
  "$@" > "$S/$label.out" 2> "$S/$label.err"; local rc=$?
  local py; py=$(grep -oE 'Using Python [0-9]+\.[0-9]+\.[0-9]+ interpreter' "$S/$label.err" | tail -1 | cut -d' ' -f2-3)
  [ -n "$py" ] || py=$(grep -m1 -oE 'CPython [0-9]+\.[0-9]+\.[0-9]+' "$S/$label.err" || echo 'interpreter not logged')
  echo "$label rc=$rc $py" | tee -a "$LOG"
}

# Fixtures: a small table, a methodology file, one Claude Code session, a git repo with a spec.
uv run --no-project --python 3.13 python - "$S" <<'PY'
import csv, json, random, sys
from pathlib import Path
s = Path(sys.argv[1]); random.seed(0)
with (s / 'data.csv').open('w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['series_id', 'ref_date', 'y', 'x', 'count'])
    for i in range(36):
        x = random.gauss(0, 1)
        w.writerow([f's{i // 12}', f'2025-{i % 12 + 1:02d}-01',
                    round(2 * x + random.gauss(0, 1), 4), round(x, 4), random.randint(0, 9)])
(s / 'method.md').write_text('# Methodology\n\nThe state evolves with growth; '
                             'the kalman_ll factor carries the likelihood.\n')
proj = s / 'projects' / '-tmp-r38'
proj.mkdir(parents=True)
records = [
    {'type': 'user', 'uuid': 'a', 'parentUuid': None, 'sessionId': 'S',
     'timestamp': '2026-10-18T10:00:00Z', 'cwd': '/tmp/r38',
     'message': {'role': 'user', 'content': 'What sampler?'}},
    {'type': 'assistant', 'uuid': 'b', 'parentUuid': 'a', 'sessionId': 'S',
     'timestamp': '2026-10-18T10:00:01Z',
     'message': {'role': 'assistant', 'content': [{'type': 'text', 'text': 'NUTS.'}]}},
]
(proj / '11111111-2222-3333-4444-555555555555.jsonl').write_text(
    '\n'.join(json.dumps(r) for r in records) + '\n')
PY
git init -q -b main "$S/repo" && mkdir -p "$S/repo/specs/plans"
printf '# A spec\n\n**Decision:** use X over Y.\n' > "$S/repo/specs/a-spec.md"
git -C "$S/repo" add . && git -C "$S/repo" -c user.name=t -c user.email=t@t.invalid commit -qm 'spec: a'

# InferenceData fixtures: one fit, and two variants for the comparator.
mkdir -p "$S/fixtures" "$S/analysis/full" "$S/analysis/intercept"
uv run --no-project --python 3.13 --with 'arviz>=1.0' --with 'numpy>=2.0' --with h5netcdf --with h5py \
  python - "$S" <<'PY'
import sys
from pathlib import Path
import numpy as np
from arviz_base import from_dict
s = Path(sys.argv[1]); rng = np.random.default_rng(0)
n_obs, chains, draws = 40, 4, 250
y = rng.normal(0.0, 1.0, n_obs)
def normal_logpdf(x, loc, scale):
    return -0.5 * np.log(2 * np.pi * scale**2) - (x - loc) ** 2 / (2 * scale**2)
def idata(loc_sd):
    mu = rng.normal(0.0, loc_sd, (chains, draws))
    return from_dict({
        'posterior': {'mu': mu},
        'sample_stats': {'diverging': np.zeros((chains, draws), dtype=bool)},
        'posterior_predictive': {'y': rng.normal(mu[..., None], 1.0, (chains, draws, n_obs))},
        'observed_data': {'y': y},
        'log_likelihood': {'y': normal_logpdf(y, mu[..., None], 1.0)},
    }, dims={'y': ['obs']})
idata(0.15).to_netcdf(str(s / 'fixtures' / 'inference_data.nc'))
idata(0.15).to_netcdf(str(s / 'analysis' / 'full' / 'inference_data.nc'))
idata(0.60).to_netcdf(str(s / 'analysis' / 'intercept' / 'inference_data.nc'))
PY

# The 17 runnable scripts.
run bootstrap_wiki uv run -v "$K/llm-wiki/scripts/bootstrap_wiki.py" "$S/wiki"
run lint_wiki uv run -v "$K/llm-wiki/scripts/lint_wiki.py" "$S/wiki"
run distill_sessions uv run -v "$K/llm-wiki/scripts/distill_sessions.py" --source claude-code "$S/projects" "$S/wiki/raw/sessions"
run distill_specs uv run -v "$K/llm-wiki/scripts/distill_specs.py" inventory "$S/repo" --root "$S/wiki"
run new_adr uv run -v "$K/design-architecture/scripts/new_adr.py" 'Probe decision' --dir "$S/adr"
run check_decoupling uv run -v "$K/describe-critique-methodology/scripts/check_decoupling.py" "$S/method.md"
run deferred_stats uv run -v "$K/writing-plans/scripts/deferred_stats.py" --file "$R/specs/deferred_items.md"
cd "$S/repo" && run entry_check uv run -v "$K/writing-plans/scripts/entry_check.py" specs/a-spec.md; cd "$S"
run profile uv run -v "$K/explore-data/scripts/profile.py" "$S/data.csv" --json "$S/profile.json"
run recommend uv run -v "$K/recommend-visualization/scripts/recommend.py" "$S/data.csv" --profile "$S/profile.json" --intent correlation
run characterize uv run -v "$K/recommend-probabilistic-model/scripts/characterize.py" "$S/data.csv" --target y
run diagnose_model uv run -v "$K/bayesian-workflow/scripts/diagnose_model.py" --idata "$S/fixtures/inference_data.nc" --output "$S/diagnostics.json"
run calibration_check uv run -v "$K/bayesian-workflow/scripts/calibration_check.py" --idata "$S/fixtures/inference_data.nc" --output "$S/calibration.json" --save-plots --plot-dir "$S/plots"
run check_diagnostics uv run -v "$K/bayesian-workflow/scripts/check_diagnostics.py" --diagnostics "$S/diagnostics.json" --calibration "$S/calibration.json" --output "$S/check_report.json"
run compare_experiments uv run -v "$K/track-model-experiments/scripts/compare_experiments.py" --analysis-dir "$S/analysis" --output "$S/comparison.json"
run geographic_build uv run -v "$K/geographic-codes/scripts/build.py" --offline --data-dir "$S/geo-data"
run classification_build uv run -v "$K/classification-codes/scripts/build.py" --offline --data-dir "$S/class-data"
# A vendored script that lands with write-with-asd-ste100 runs too, by its own self-test.
[ -f "$K/write-with-asd-ste100/scripts/ste-lint.py" ] && run ste_lint uv run -v "$K/write-with-asd-ste100/scripts/ste-lint.py" --selftest

# Isolation: a project whose Python and dependency cannot be met. The headered
# script runs; the same script without its header is bound to the project and fails.
mkdir -p "$S/hostile"
printf '[project]\nname = "hostile"\nversion = "0"\nrequires-python = "==3.10.*"\ndependencies = ["r38-no-such-distribution>=99"]\n' \
  > "$S/hostile/pyproject.toml"
cp "$K/writing-plans/scripts/deferred_stats.py" "$S/hostile/with_header.py"
uv run --no-project --python 3.13 python - "$S/hostile" <<'PY'
import re, sys
from pathlib import Path
d = Path(sys.argv[1])
text = (d / 'with_header.py').read_text()
(d / 'without_header.py').write_text(re.sub(r'(?ms)^# /// script$.*?^# ///$\n', '', text, count=1))
PY
cd "$S/hostile" && run isolated_with_header uv run -v with_header.py --file "$R/specs/deferred_items.md"
run control_without_header uv run -v without_header.py --file "$R/specs/deferred_items.md"; cd "$S"
echo "uv: $(uv --version)" | tee -a "$LOG"
```

Run `chmod +x /tmp/portability-plan/r38.sh`.

- [ ] **Step 2: Run it,** in the background (about two minutes with uv's cache warm, longer cold): `/tmp/portability-plan/r38.sh . /tmp/portability-r38`. Expected log (`/tmp/portability-r38/r38.log`): 17 script lines, each `rc=0 Python 3.x.y`; `isolated_with_header rc=0 Python 3.x.y`; `control_without_header rc=1 CPython 3.10.z` or another non-zero exit; and uv's version. With write-with-asd-ste100 present, an 18th script line, `ste_lint`, appears. Any script line that is not `rc=0` stops the task: read that script's `.err` file under `/tmp/portability-r38/` and fix the cause before going on.
- [ ] **Step 3: Record it.** Copy `/tmp/portability-r38/r38.log` into this plan under "Plan completion notes", "R3.8 execution proof", in a text fence, with the run's date.
- [ ] **Step 4: Commit.**

```bash
git add specs/plans/53-agent-skills-portability.md
```

```bash
git commit -m "docs(specs): record plan 53's execution proof (portability R3.8)"
```

---

### Task 14: Stage D's edit (R2.3) and the register (DF20)

**Files:**
- Modify: `skills/writing-skills/SKILL.md` (the Token Efficiency `description` bullet; on the at-most-3/5 branch, also the checklist), `NOTICE`, `build/cc_guide/conformance.toml` (three exceptions)
- Modify, on the at-most-3/5 branch: `specs/red-baseline-description-openings-<run-date>.md` (the GREEN arm)
- Scratch: `/tmp/portability-stage-d/` (the Codex measurement; the GREEN reps)

**Interfaces:**
- Consumes: Task 2's verdict and kit.

- [ ] **Step 1: Re-measure the Codex cut** (D8), with the real HOME. Run `codex --version` and `mkdir -p /tmp/portability-stage-d/neutral`, then `env -C /tmp/portability-stage-d/neutral codex debug prompt-input > /tmp/portability-stage-d/codex-prompt.json`: `env -C` runs Codex from a directory outside every repository without moving this session. Then:

**Create `/tmp/portability-stage-d/kit/codex_cut.py`:**

```python
'''Measure how Codex cuts this repo's skill descriptions in its listing (portability R2.3).

Usage, where <dir> is outside every repository:
  env -C <dir> codex debug prompt-input > <dir>/codex-prompt.json
  uv run --no-project --python 3.13 --with pyyaml python codex_cut.py <worktree> <dir>/codex-prompt.json
Prints the number of skills Codex listed, how many of this repo's skills it listed,
and the listed length range of the descriptions it cut.
'''
import json
import re
import sys
from pathlib import Path

import yaml

# One listing entry: '- <name>: <description> (file: <path>)'. A plugin skill's
# name holds a colon (plugin:skill), so the name runs to the first ': '.
ENTRY_RE = re.compile(r'^\s*- (?P<name>\S+?): (?P<desc>.*) \(file: .*\)\s*$', re.M)


def strings(node):
    if isinstance(node, dict):
        for v in node.values():
            yield from strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from strings(v)
    elif isinstance(node, str):
        yield node


worktree, prompt = Path(sys.argv[1]), Path(sys.argv[2])
listing = max((s for s in strings(json.loads(prompt.read_text())) if '(file: ' in s), key=len)
found = [(m['name'], m['desc']) for m in ENTRY_RE.finditer(listing)]
entries = dict(found)
twice = sorted({n for n, _ in found if sum(1 for m, _ in found if m == n) > 1})
ours = {}
for sk in sorted(worktree.glob('skills/*/SKILL.md')):
    fm = yaml.safe_load(re.match(r'^---\n(.*?)\n---\n', sk.read_text(), re.S).group(1))
    ours[sk.parent.name] = ' '.join(str(fm['description']).split())
listed = {n: d for n, d in entries.items() if n in ours}
cut = sorted(len(d) for n, d in listed.items() if len(d) < len(ours[n]))
print(f'skills listed: {len(found)} (listed twice: {twice or "none"}); '
      f'this repo listed: {len(listed)} of {len(ours)}; missing: {sorted(set(ours) - set(listed)) or "none"}')
if cut:
    print(f'cut: {len(cut)} descriptions, listed at {cut[0]}-{cut[-1]} characters '
          f'(median {cut[len(cut) // 2]}); whole: {len(listed) - len(cut)}')
else:
    print(f'cut: none; whole: {len(listed)}')
```

Run `uv run --no-project --python 3.13 --with pyyaml python /tmp/portability-stage-d/kit/codex_cut.py . /tmp/portability-stage-d/codex-prompt.json`. On 2026-10-18 it printed `skills listed: 105 (listed twice: ['skill-creator']); this repo listed: 37 of 37; missing: none` and `cut: 28 descriptions, listed at 316-320 characters (median 318); whole: 9`. If `codex debug prompt-input` fails on Codex's configuration, ask the owner; never edit `~/.codex/config.toml`.
- [ ] **Step 2: Write the note.** If Step 1's figures, date or Codex version differ from 2026-10-18's, put the new ones in the note below in their place, keeping the 2026-10-03 figures as they are.

**Edit `skills/writing-skills/SKILL.md`: replace**

```markdown
  competes for context in conversations where the skill is never used.
```

**with**

```markdown
  competes for context in conversations where the skill is never used. Codex also shortens
  descriptions once its skills listing passes its budget: with 105 skills listed, Codex 0.163 cut
  this repo's longer descriptions to 316–320 characters (2026-10-18; Codex 0.154 cut to 156–164
  with 93 listed, 2026-10-03). Re-measure with `codex debug prompt-input` from a directory outside
  any repo, reading its Skills list.
```

**Edit `NOTICE`: replace**

```text
    the original works named above. Both SKILL.md files also gained a
    `compatibility` field naming uv (R3.6).
```

**with**

```text
    the original works named above. Both SKILL.md files also gained a
    `compatibility` field naming uv (R3.6).
  - writing-skills' Token Efficiency section gained a note that Codex
    shortens long descriptions once its skills listing passes its budget,
    with the cut measured on 2026-10-18 and how to re-measure it
    (specs/agent-skills-portability-spec.md, R2.3).
```

- [ ] **Step 3, only on the at-most-3/5 branch: the checklist line and the GREEN arm.**

**Edit `skills/writing-skills/SKILL.md` (at-most-3/5 branch only): insert after the line `- [ ] Description starts with "Use when..." and includes specific triggers/symptoms`:**

```markdown
- [ ] The primary trigger falls within the first ~150 characters of the description
```

**Edit `NOTICE` (at-most-3/5 branch only): replace**

```text
    with the cut measured on 2026-10-18 and how to re-measure it
    (specs/agent-skills-portability-spec.md, R2.3).
```

**with**

```text
    with the cut measured on 2026-10-18 and how to re-measure it, and its
    checklist gained a line placing the primary trigger within a
    description's first ~150 characters, tested GREEN first
    (specs/agent-skills-portability-spec.md, R2.3).
```

  Then build the GREEN prompt from the edited tree: `uv run --no-project --python 3.13 python /tmp/portability-stage-d/kit/build_prompt.py . /tmp/portability-stage-d/green-prompt.txt`; run `/tmp/portability-stage-d/kit/run_reps.sh /tmp/portability-stage-d/green-prompt.txt /tmp/portability-stage-d/green 5` in the background; read with `show_reps.py`, under Task 2's rule. At least 4/5 must pass (R2.3). Record the arm in the red-baseline file under a `## GREEN` heading, in the Result table's form, and update its Status line. If fewer than 4/5 pass, stop and ask the owner: R2.3 sets no fallback.
- [ ] **Step 4: The register** (DF20). Stage D closes none of the writing-skills gaps, so their pointers move to the deferred item that completion logs.

**Edit `build/cc_guide/conformance.toml`: replace**

```toml
tracked_in = 'portability Stage D'
```

**with**

```toml
tracked_in = 'deferred item: split and rewrite writing-skills against the guide'
```

**Edit `build/cc_guide/conformance.toml`: replace**

```toml
tracked_in = 'portability Stage D, with writing-skills-guide-gaps'
```

**with**

```toml
tracked_in = 'deferred item: split and rewrite writing-skills against the guide, with writing-skills-guide-gaps'
```

**Edit `build/cc_guide/conformance.toml`: replace**

```toml
revisit = 'When portability Stage D revises writing-skills.'
```

**with**

```toml
revisit = 'When writing-skills is split and rewritten against the guide (a deferred item).'
```

**Edit `build/cc_guide/conformance.toml`: replace**

```toml
reason = 'writing-skills departs from the guide on body length, the listing budget, critical-rules-first and @ loading; its @ loading claim is unsupported rather than contradicted, and Stage D verifies or drops it.'
```

**with**

```toml
reason = 'writing-skills departs from the guide on body length, the listing budget, critical-rules-first and @ loading; its @ loading claim is unsupported rather than contradicted, and the rewrite verifies or drops it.'
```

- [ ] **Step 5: Gates.** Run `bash build/run_commit_lints.sh`. Its `critical_placement` lint passes unchanged: the note lands above the compaction window's edge (Planning record).
- [ ] **Step 6: Commit.**

```bash
git add skills/writing-skills/SKILL.md NOTICE build/cc_guide/conformance.toml specs
```

```bash
git commit -m "docs(skills): writing-skills notes Codex's description cut (portability R2.3)"
```

---

### Task 15: Acceptance (Validation 1–6)

**Files:** none changed. A scratch HOME at `/tmp/portability-home/`.

**Interfaces:**
- Consumes: Tasks 1–14.

- [ ] **Step 1: Validation 1, every gate.** Run `bash build/run_commit_lints.sh`: `commit lints passed`. Run `uv run --directory build --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q`: +38 passed against the base, and no failure but the 4 `test_verify_citations.py` tests when the worktree lacks the gitignored `build/.scratch/` (run the same command on the base to compare). Re-run Task 10 Step 6's nine suites: unchanged counts. `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py` exits 0 with one `WARN`, for writing-skills' body. `uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py --check` exits 0 (no adapter changed).
- [ ] **Step 2: Validation 2.** `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py --strict` names exactly `bayesian-workflow`, `tech-debt` and `tune-hyperparameters`.
- [ ] **Step 3: Validation 3.** Each new rule's RED step in Tasks 3–6 and 8–12 is ticked, with the failure it predicted.
- [ ] **Step 4: Validation 4.** Task 13's record is in this plan.
- [ ] **Step 5: Validation 5, the cross-runtime load check,** against the branch's own files (DF18). Run `mkdir -p /tmp/portability-home/neutral`, then `HOME=/tmp/portability-home python3 install.py codex --copy --no-companions` (expected: one `copied …` line per skill). Then run both CLIs from the scratch HOME's `neutral` directory, which is outside every repository (`env -C` sets the directory without moving this session): `env -C /tmp/portability-home/neutral HOME=/tmp/portability-home gemini skills list --all > /tmp/portability-home/gemini.txt` and `env -C /tmp/portability-home/neutral HOME=/tmp/portability-home codex debug prompt-input > /tmp/portability-home/codex.json`. Then:

**Create `/tmp/portability-plan/runtime_check.py`:**

```python
'''Validation 5: every skill under skills/ loads in Gemini CLI and Codex.

Usage: uv run --no-project --python 3.13 python runtime_check.py <worktree> <gemini.txt> <codex.json>
gemini.txt is `gemini skills list --all`'s output and codex.json is
`codex debug prompt-input`'s, both run from a directory outside every repository
with HOME set to a scratch home that holds a copy install of the worktree's skills.
Exit 1 if any skill is missing from either list or is not [Enabled] in Gemini's.
'''
import json
import re
import sys
from pathlib import Path


def strings(node):
    if isinstance(node, dict):
        for v in node.values():
            yield from strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from strings(v)
    elif isinstance(node, str):
        yield node


worktree, gemini, codex = (Path(a) for a in sys.argv[1:4])
names = sorted(p.parent.name for p in worktree.glob('skills/*/SKILL.md'))
enabled = set(re.findall(r'^(\S+) \[Enabled\]$', gemini.read_text(), re.M))
listing = max((s for s in strings(json.loads(codex.read_text())) if '(file: ' in s), key=len)
listed = set(re.findall(r'^\s*- ([^:\s]+): ', listing, re.M))
no_gemini = [n for n in names if n not in enabled]
no_codex = [n for n in names if n not in listed]
print(f'gemini: {len(names) - len(no_gemini)}/{len(names)} [Enabled]; missing: {no_gemini or "none"}')
print(f'codex: {len(names) - len(no_codex)}/{len(names)} listed; missing: {no_codex or "none"}')
sys.exit(1 if no_gemini or no_codex else 0)
```

Run `uv run --no-project --python 3.13 python /tmp/portability-plan/runtime_check.py . /tmp/portability-home/gemini.txt /tmp/portability-home/codex.json`. Expected: `gemini: 37/37 [Enabled]; missing: none` and `codex: 37/37 listed; missing: none` (38/38 with write-with-asd-ste100), exit 0.
- [ ] **Step 6: Validation 6.** The red-baseline file exists. `git diff d70e0b3 HEAD -- skills/writing-skills/SKILL.md` shows only Tasks 3 and 4's edits (the frontmatter's `license` and `metadata`, the required-fields and optional-keys bullets, the template and the checklist's frontmatter item) and Task 14's note (and its checklist line, on that branch).
- [ ] **Step 7: Hand over** to the plan-completion protocol (writing-plans): the notes below list what it logs and ticks.

---

## Plan completion notes

### R3.8 execution proof

Task 13 records the log here.

### For the completion protocol

- **Deferred items to log** (the spec's Out of scope, with two changes):
  - Trigger-eval suites; distribution channels; Codex adapters for `/deferred`, `/fix-issue` and `/license-audit`; tables of contents for long `references/` files; a versioning policy; license travel for single-file agents: as the spec words them.
  - Skill security scanning: "The repo has no CI" no longer holds; `.github/workflows/lints.yml` (plan 41's advisory CI) runs the commit lints only.
  - "Split and rewrite writing-skills against the guide", in place of the spec's "Splitting writing-skills": split the body below 500 lines (R1.7's warning) and close the register gaps `writing-skills-guide-gaps` and `writing-skills-late-critical-headings`, which Task 14 points at it (DF20), verifying or dropping the skill's `@` loading claim on the way.
- **Backlog to tick:** "`build/check_frontmatter.py`'s SKILL.md key set" (section cc-guide-files-backlog), done in plan 53 under D5 (`agent` allowed beside `disable-model-invocation`). Add a progress note to "Gate or make manual-only the four ungated side-effecting skills" (section 35-claude-code-guide-conformance): Stage A landed, and a manual-only skill now needs `agents/openai.yaml` with `policy.allow_implicit_invocation: false` (R1.6).
- **Owner steps after merge:** refresh each wiki's installed llm-wiki scripts (DF15).
