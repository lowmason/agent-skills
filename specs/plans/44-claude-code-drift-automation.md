# Claude Code Drift Automation, Stage 3 (Act) Implementation Plan

**Status: COMPLETE (2026-10-13)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Where this runs.** This plan reaches `main` through its own PR. After that merges, create the worktree from the main checkout (Global Constraints, "Worktree") and execute there: `/Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3`, on branch `feat/cc-drift-stage3`. Start the execution session with that worktree as its working directory, not the main checkout: subagent-driven-development's `sdd-workspace` and `review-package` take the repo root and `HEAD` from the shell's working directory, so launched from the main checkout they would write the SDD workspace there and diff `main`. Below, **`W`** names that absolute path in prose. Every command spells the path out, because a worktree-isolated session refuses compound shell (`&&`, `$(...)`).

**Goal:** Build Stage 3 of the drift spec, the act layer. `/cc-guide` and its `cc-guide-verifier` agent turn what `check` reports into quote-checked guide corrections and citation reviews, left in the working tree for the owner. `cli.py packets` writes the files the verifier reads. `cli.py settle` re-greps the verifier's quotes, applies the spec's fail-safe and discard rules, and prints the corrections, the owner's-call items and the `baseline` commands that follow. `cli.py quotes` checks single rows. The first live jobs (R11.5) run after the merge, as the "Live run" section says.

**Architecture:** Four modules and two Claude Code files:
- `quotes.py` (R8.3): the single-line quote search that `quotes` and `settle` share.
- `state.py` and `check.py`: each block finding carries its key hash. A group's snapshot pages yield each baselined block's name and text by key hash (T5). The snapshot copy `baseline rebaseline` made moves into `state.copy_to_snapshot`, which `packets` reuses.
- `guide.py` and `cli.py`: citation placement learns the `.claude/` kinds. Three of plan 43's deferred items fold in (T6).
- `packets.py` (R6.11): builds packet directories from `check`'s parts, offline, from the last fetch.
- `settle.py` (R8.10, new): parses the verifier's report, then applies R8.4 steps 4–6 to a triage and R8.8 steps 1–4 to the other modes.
- `.claude/skills/cc-guide/` and `.claude/agents/cc-guide-verifier.md` (R8.1): the typed-only skill and the read-only verifier.

**Tech Stack:** Python 3.13 through `uv run`, stdlib only inside `build/cc_guide/` (`difflib` for packet diffs, `shlex`, `json`, `pathlib.PurePosixPath.full_match`, new in 3.13); pytest; Claude Code skill and agent Markdown. No new git call.

**Spec:** `specs/claude-code-drift-automation-spec.md` (DESIGN APPROVED 2026-10-03; Stage 1 shipped as plan 38, Stage 2 as plan 43). R-numbers, "Sequencing item N" and "Validation item N" point into it. Task 1 writes this plan's amendments into it. The base is `main` at `4991f4b` plus this plan's own merge.

## Global Constraints

Every task's requirements implicitly include this section.

- **Scope (Sequencing item 3).** In scope:
  - R8 except `/cc-guide probes` (R8.9): the skill, the verifier, R8.3's `quotes` and R8.10's `settle`, which Task 1 adds;
  - R6.11's `packets`;
  - R12.2's R8 bullet, R12.4's `.claude/` frontmatter checks and R12.7's documentation;
  - T5's open item and the three T6 items Task 4 folds in.

  Not in this stage:
  - R11.5's live first jobs, which run after the merge (DF1; "Live run" below);
  - Stage 4: `notice.sh`, `check --hook`;
  - Stage 5: probes;
  - fixing any cited file, including the three known drifts, which the live `files` batch does.
- **Order.** Task 1 (spec amendments), then Tasks 2–6, one module boundary each, in dependency order (`quotes`, then the snapshot readers, citation placement, `packets`, `settle`), then Task 7 (the skill, the verifier and the docs), then Task 8 (validation). Each task's tests run with every earlier task in place.
- **Worktree.** Before creating it, run `git -C /Users/lowell/Projects/agent-skills fetch --prune`, then `git -C /Users/lowell/Projects/agent-skills log --oneline -3 origin/main`, and confirm `origin/main` holds this plan's merge.
  - Create the worktree with `git -C /Users/lowell/Projects/agent-skills worktree add .claude/worktrees/plan-44-cc-drift-stage3 -b feat/cc-drift-stage3 origin/main`. `.claude/worktrees/` is gitignored. Commit only from the worktree, as `git -C <W> commit …`.
  - Before every commit, run `git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 branch --show-current` and confirm it prints `feat/cc-drift-stage3`.
  - The repo sets `core.hooksPath=build/githooks`, so every commit runs `build/run_commit_lints.sh` (seven lints, about 40 s). A refused commit is a finding: fix the cause, never pass `--no-verify`.
  - Scratch files live under W's gitignored `.sdd/44-claude-code-drift-automation/` and are never committed. Deviations go in the SDD ledger there as they happen. They reach this plan as `> Deviation:` notes only at the completion markup.
  - Each commit ends with the executing session's own Co-Authored-By trailer, which subagent-authored commits keep too. After each subagent commit, check `git -C <W> log -1 --format=%B` and amend the trailer if the implementer wrote its own.
- **Baseline and counts.** Before Task 1, run the three suites in W and record their counts in the SDD ledger:
  - `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3/build --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q -rf`
  - `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3/build/cc_guide --python 3.13 --with pytest python -m pytest -q`
  - `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3/hooks --python 3.13 --with pytest python -m pytest -q`
  - A worktree lacks the gitignored `build/.scratch/`, so four tests in `test_verify_citations.py` fail there and stay failing throughout: `test_true_negative_flags_bad_refs`, `test_empty_text_has_no_failures`, `test_chapter_fallback_passes_gate_a_but_is_flagged` and `test_known_good_fallback_is_not_flagged`. They are not this plan's to fix.
  - Every expected change below is a **+N delta over the baseline you record**. This plan adds **+111 tests**, all in `build/cc_guide/`, so the build directory, which collects that suite, rises by the same +111: Task 2 +6, Task 3 +2, Task 4 +14, Task 5 +25, Task 6 +52, Task 7 +12. `hooks/` gains none.
- **Test-first.** Each task writes its tests first, runs them, and reconciles the run against the step's prediction before writing code: the counts, and each failure's cause.
  - The predictions were observed by replaying this plan's edit blocks, task by task, against a clean checkout of `4991f4b` while the plan was written.
  - A test that passes at its RED step is a plan defect: fix the assertion so it fails for the stated reason, and report the deviation. Task 4 names its one exception: three cases that pin existing behaviour the new rule must leave alone.
- **Test conventions** (Stage 1's, unchanged).
  - Run the cc_guide suite from inside `build/cc_guide/` (here, `uv run --directory`).
  - Bare imports, no `__init__.py`. Test files import modules by name and reach names through them.
  - Fixtures are hand-written in `cc_fixtures.py`, never copied from docs text.
  - Every cc_guide test file imports `isolated_home` from `cc_fixtures` (with `# noqa: F401`).
  - Fixture repos go through `cc_fixtures.git`. Messages are compared with exact equality.
- **No citation-shaped lines in sources (R5).** No line of any tracked file outside `specs/`, `runtimes/` and `review/` may begin, after indentation, with `#` or `<!--` followed by `cc-guide:`, unless it is a real citation where R4.1 puts it. Task 7's two files carry real ones, as the last line of their frontmatter. Test data lives inside quotes, or is built as `'#' + ' cc-guide: …'`.
- **Python style** (`CLAUDE.md`, `rules/clean-code-python.md`). Single quotes, `'''` docstrings, 4-space indent, Python 3.13, stdlib only inside `build/cc_guide/`, lines within about 120 columns.
- **CLI contract** (Stage 1's). `uv run --python 3.13 python build/cc_guide/cli.py <subcommand>` finds the repo from its own location. Exit 0 is clean or nothing due; 1 is violations, something due, or a report that failed something safe; 2 is an error (`cc-guide: <message>` on stderr for a `SetupError`, a traceback otherwise).
- **Inputs.** `packets` reads the guide, `manifest.toml` and `baseline.json` from the working tree, as `check --worktree` does, and the docs from the cache's last fetch (`latest/`). It never fetches. `settle` reads its packet directory, and for verify and audit the snapshot directory the packet names. `quotes` reads stdin and the directory it is given.
- **Writes.** Nothing in the repo; nothing commits.
  - `packets` writes a new packet directory, and refuses one that is not empty or that resolves inside any checkout (spec Decision 10).
  - `--verify` and `--audit` copy their groups' pages into the head release's snapshot (`<head>/docs/`) through `state.copy_to_snapshot`. It never overwrites different bytes and never writes the 2.1.288 bootstrap.
  - `settle` writes only `settled.json`, in a triage packet.
- **Git calls (T2).** This plan adds no git call: packet diffs use `difflib`, and `files` packets reuse `citing_files`, whose `git grep` already passes `--no-color`. A git call added during execution whose output git can colour (grep, diff, log, show) passes `--no-color`. It also needs a test that sets that colour key to `always` in the fixture repo's own config, as `build/cc_guide/test_state.py`'s hostile-config test does.
- **Unchanged gates (R12.4).** `check_frontmatter.py`, the dependency-drift test and `sync_runtime_assets.py` stay unchanged. `check_frontmatter.py` never reads `.claude/`, which is why Task 7's own tests check that frontmatter. `sync_runtime_assets.py --check` must report no adapter change, since `.claude/agents/` is not adapted.
- **Never commit docs text.** No step copies text from `~/.cache/agent-skills/cc-guide/`. Packets, reports and quotes stay under the cache and in session reports. This plan cites docs by page and line only.
- **Nothing outward-facing.** No push, PR, issue or post during execution, and no network use: no task fetches.
- **Leave alone:**
  - the spec's status line;
  - the by-hand batch (D1);
  - the SDD bundle (H26/P2/P3/Q2), which is its own plan;
  - every cited file's content, which the live run's `files` batches review;
  - `.claude/settings.json`;
  - `build/cc_guide/conformance.toml`, the owner's register.
- **Anchor on text, not line numbers.** Line numbers are as of `4991f4b`. Every edit gives its exact old text. Never regress an existing test.

## Decisions

- **D1** (owner, brief, 2026-10-12): the owner hand-ran the due 2.1.290–2.1.296 changelog batch before Stage 3. It landed as lowmason/agent-skills#38 (true merge `5a4777e`; commits `cb1c847`, `62d564a`, `3e0a38f`): the guide reads "through 2.1.296", `check` on `main` lists nothing untriaged, and the stale-citation backlog stays at 41 files. There the owner applied the two `lean.model-routing` rewrites the spec makes report-only, kept the Haiku-skill ban and reworded its register reason, and left older gaps for an audit (T7). So the live triage starts after 2.1.296, and the Haiku 5.5 case is a worked example, not a live expectation. Applied in: Task 1 (spec amendment: R11.5, Sequencing item 3, Validation 3), Task 6 (the Haiku fixture), Live run.
- **D2** (owner, plan review, 2026-10-12): fix every finding of the independent review ("Independent review" below), test-first in the prototype, then rebuild the replay and regenerate this plan. Applied in: Tasks 1 and 5–8 (spec amendments: R6.11, R8.4 step 1, R8.5, R8.6, R8.7, R8.8 step 1, R8.10), Planning record.
- **D3** (owner, plan review, 2026-10-12): block findings ride in the first triage range and are settled there against the current docs. Their sections advance only to that range's end, and the next range starts after the previous `--through`. No block holds remain; a missing page's holds are saved in `settled.json`. Applied in: Task 1 (spec amendment: R8.4 step 1, R8.10), Tasks 5–7 (S4).
- **D4** (owner, plan review, 2026-10-12): the skill's discipline rules are micro-tested: `claude -p` from a directory that was never the repo, a no-guidance control and the rules, 5 reps each, on tempting settle outputs. Applied in: Planning record (application test, run 6).
- **D5** (owner, plan review, 2026-10-12): a contradiction the register records as a `deviation` is the owner's standing decision and holds nothing; a `gap` still holds its file. Applied in: Task 1 (spec amendment: R8.8 step 2), Task 6 (settle's files header), Task 7 (the skill), Live run (S17).
- **D6** (owner, plan review, 2026-10-12): fix every finding of the second independent review ("Independent review" below), test-first in the prototype. Finding 1 is fixed by narrowing the claim: a row outside the packet's sections holds nothing and names the `/cc-guide verify` that reviews its section, rather than the triage holding back its cleared sections' advance until every verify reconciles (S24). Finding 10's header change is re-tested on run 6's D and E scenarios (run 6b). Applied in: Tasks 1, 5–7 (spec amendments: R6.11, R8.5, R8.8 steps 1–4, R8.10), Planning record.

---

## Planning record

### Prototype and replay

Every task was built and run in a throwaway clone (`~/.cache/agent-skills/scratch/plan44-proto`, branch `proto`). It was then replayed task by task onto a clean `4991f4b` in a worktree of that clone, through the same edit data this plan's code blocks are generated from. The replayed files equal the prototype's byte for byte. These totals are what the replay saw, a record and not a target:
- baseline at `4991f4b`: the build directory 854 passed, 4 failed and 11 skipped; `build/cc_guide/` 296 passed; `hooks/` 274 passed on both interpreters;
- after Task 7: the build directory 965 passed (+111), with the 4 known failures; `build/cc_guide/` 407 passed (+111); `hooks/` 274 on both;
- `build/run_commit_lints.sh`: all seven lints pass; `check_conformance.py` exits 0;
- `cli.py lint`: exit 0 and the same 41 `STALE` lines. Task 7's two files carry their own stamps (`@2.1.296`) and are not stale, so 43 files now cite the guide;
- against the real cache, offline: `packets --triage` printed `nothing to triage: no untriaged release and no block finding`; `packets --files agents/explore.md` wrote a files packet under the cache's `packets/`, marking all three cited sections changed since its `@2.1.219` stamp; and `packets --audit` refused with `no audit is due before 2026-11-02: name a group to audit one anyway`.

### Application test (writing-skills)

The pipeline, the verifier's contract with `packets` and `settle`, was tested by application: does a verifier given the contract and a real packet return a report `settle` can parse and act on? The skill's rules on what a session may do after `settle` are discipline under pressure, so they were micro-tested (run 6, D4).

**The input was synthetic.** Every packet was built from a scratch cache whose fetch record was edited to head 2.1.297, and whose pricing page had one injected change: the Haiku 5.5 up-to-100K output cell. The real cache (`~/.cache/agent-skills/cc-guide/latest/`, head 2.1.296) was never edited, and the scratch cache is deleted. The rows that rest on the injected cell show the pipeline catching a planted change. **They are not guide drift**: triage's B1 rows, and the verify rep's corrections and judgments about Haiku 5.5's output price and the ratios built on it (guide lines 211, 438, 441). Do not change the guide's prices on their account.

The runs:
1. **Two triage reps**: general-purpose Sonnet agents given the contract's text, with Bash and CLAUDE.md, which the real agent lacks. Rep 1 ran `ls` and `wc`. Both settled clean: 0 quotes not found, 0 unparseable lines, nothing left out. They answered 42 and 37 items, since a bullet's row is optional. Rep 1 sent three sections to verify (`subagents.models`, `lean.caching`, `lean.model-routing`) and advanced `reading.overview`. Rep 2 sent only `subagents.models` and `lean.model-routing`, and advanced `lean.caching` too. A clean settle shows the reports parse, not that two verifiers agree.
2. **One verify rep** on the `models` group, from rep 2's settled triage: 77 A rows, 4 B rows and 4 C rows. It settled clean: 47 confirmed, 8 corrections, 26 owner's call, 0 unverified, 0 unparseable, once S7's TODO reach was in place. Six of the eight corrections rest on the injected cell. It did not report `deniedModels` (T7), which the pages it read hold; its four C rows, the spec's cap, went to four other omissions.
3. **The real definition**: `.claude/agents/cc-guide-verifier.md`, dispatched by `claude -p --model sonnet` (Claude Code 2.1.296, auto mode) from the clone with the skill's dispatch prompt.
   - Claude Code listed it, dispatched it by `subagent_type`, and it ran 4 Reads and 1 Glob under `~/.cache` with 0 tool errors and 0 permission denials. Its transcript holds no CLAUDE.md text; the positive control, a general-purpose rep's transcript, does. Grep was not exercised.
   - Its report settled clean: 15 items, 4 of 4 releases covered, and rep 1's three verify sections.
   - It cost $1.32: $0.80 on Sonnet for the session and the verifier, $0.52 on Opus for auto mode's classifier, which approved six of its tool calls (decision source `classifier`).
   - So the verifier reads packets under `~/.cache` in auto mode with no `additionalDirectories`. In another permission mode, or if prompts appear, an allow rule is an owner-gated settings change, not this plan's.
4. **The skill body, RED**: `claude -p --model sonnet '/cc-guide files agents/explore.md'` from the clone, against the real cache (files mode writes no snapshot). Every step of the skill ran, and its `report.md` Write into `~/.cache` met no denial. But:
   - the verifier opened a free-text statement with a quoted phrase, the first grammar misread the row, and settle discarded it;
   - the session then read `settle.py`, resumed the verifier to reword the row, and overwrote `report.md` to get past the gate;
   - it edited `agents/explore.md`, `build/sync_runtime_assets.py` and `README.md`, fixed one of four listed contradictions, and still ran `baseline cite`, which would have cleared the file from the backlog with three contradictions in it.

   It cost $1.58, $0.65 of it the classifier.
5. **The skill body, GREEN**, after S15 and S16, with the same command:
   - it saved the report unchanged, and settle exited 0 with nothing unverified;
   - it edited no file;
   - it left all three contradictions for the owner, each with a reason (a registered gap, a registered deviation, and a fix that reaches two other files), and skipped `cite`.

   It cost $1.37, $0.67 of it the classifier. The clone's tree stayed clean. Both probe reports settle again under the review's fixes: the GREEN report answers all three cited sections, so the completeness rule (S19) passes it (5 consistent, 3 contradictions, 4 not covered, exit 0).
6. **The skill's rules, micro-tested** (D4). Each run was `claude -p --model sonnet --tools ""` (2.1.296) from `/tmp/plan44-micro/run`, a directory that was never the repo: one decision-only turn with the skill body inline, answering with the edits and commands it would make. The control lacked the five rules under test: the edit scope with its two follow-ons, `--hold`, the deviation rule (S17), step 3's "what settle held or discarded stands", and files step 2's cite gate. Both arms saw the same settle output, whose header names `--hold`. Pass and fail were pre-registered. There were 50 runs, costing $3.71, and every answer was read by hand:

   | Scenario | Control | With the rules |
   |---|---|---|
   | an unparseable row holds the file | 0/5: each re-dispatched the verifier to overturn the hold | 5/5 |
   | the fix reaches two other files | 0/5: each edited `README.md` and `build/sync_runtime_assets.py`, then cited | 5/5: held, edited nothing |
   | one fix in the file, one the owner's decision | 5/5 | 5/5 |
   | a registered deviation covers the contradiction | 0/5: each held the file | 5/5: cited it |
   | decoy: the same deviation, another statement | 5/5 | 5/5: none stretched the deviation over it |

   So the scope rule, "what settle held stands" and the deviation rule each change behaviour, and the deviation rule causes no over-matching. The files-step cite gate is not shown necessary, since settle's header names `--hold` itself; it stays as the skill's statement of that header.
7. **The skill body, GREEN after the fixes**, with run 4's command, against the real cache. It cost $0.78, $0.19 of it the classifier.
   - It saved the report unchanged, and settle exited 0: 7 consistent, 2 contradictions, 2 not covered.
   - It read the register: it left the capital-E `name`, a deviation that holds nothing (S17), and held the file for the Grep and Glob gap with `settle --hold`.
   - It ran lint and `check_conformance.py`, edited nothing and skipped `cite`.
   - Its verifier rated the "Haiku-pinned" description consistent, where run 5's called it a contradiction: a verifier judgment the live run's owner review settles.
8. **Run 6's D and E against settle's new files header** (run 6b; second review, finding 10; D6). Settle's files header now says a contradiction `build/cc_guide/conformance.toml` records as a deviation stays as it is (S17). Run 6b re-ran the two scenarios the deviation rule decides, pre-registered, on run 6's prompt files with only that header line replaced: 20 runs, $2.33, every answer read by hand. The deviation scenario passed 5/5 in both arms; run 6's control had failed it 0/5, so the header now carries that route by itself, and the skill's rule stays as its statement. The decoy passed 5/5 in both arms: no answer stretched the deviation over the other statement, and each fixed it and cited the file.

What the test changed: the TODO reach (S7), the evidence rows a verify packet carries (S9), quote fields by position (S15), the skill's rules and settle's headers (S16, S17), and the test that an indented report settles as written, since the Agent tool hands a report back with every line indented. The evidence is in `~/.cache/agent-skills/cc-guide/plan44-application/`. Its `README.txt` labels the synthetic rows, `micro-tests/` holds run 6's pre-registration, prompts, answers and grader (`micro-tests/run6b/` holds run 6b's), `review/` holds the independent review, and `review2/` the second, with the tests that reproduced its findings.

### Settled defaults (your human partner reviews each)

- **DF1 (brief). The live first jobs run after the merge.** The plan builds and tests R8, `quotes` and `packets` against hand-written fixtures, adds R12.4's `.claude/` checks and writes R12.7's docs. The triage, the `verify` it triggers, one `audit` and the first `files` batch run after the merge, from a fresh worktree, with the owner reviewing the uncommitted diff ("Live run" below). One deferred item, whose Done-when is Validation 3, points at that section. If wrong: plan review adds a late, owner-gated live-run task modelled on plan 38's Tasks 11–13.
- **DF2 (brief). The stale first-jobs text is amended** (Task 1: `r11.5`, `seq3`, `val3`). The guide no longer shows the Haiku 5.5 case (D1 applied it), so the case becomes a hand-written fixture: Task 6's `test_the_haiku_case_a_section_the_hints_miss_still_goes_to_verify`. While `check` shows nothing untriaged, Validation 3's triage bullet waits for the next release.
- **DF3 (brief). The 190-line ceiling binds.** CLAUDE.md stays at 186 lines (+0): Task 7 extends one comment line in place. `build/CLAUDE.md` gains 5 lines (50 → 55) and has no ceiling.
- **S1. `settle` is a new subcommand with its own module** (Task 1: `layout`, `r8.10`). R8.4 steps 4–6 and R8.8 steps 1–4 are "deterministic" but name no tool. The Layout's subcommand list is closed, so a new subcommand is an amendment. The alternatives were to fold the rules into `quotes`, which overloads a single-row tool, or to leave them to the skill body, which is neither deterministic nor testable.
- **S2. `packets.py` is its own module**, built on `check.py`'s parts and loading offline from `latest/`; the Layout names no module for it.
- **S3. The packet layout.** A packet is a directory: `index.json`, the guide copied whole so its line numbers are the guide's, and the mode's Markdown files. `--out` is optional, with a timestamped default under the cache's `packets/`. Verify writes one packet per group and files one per file. A packet never writes over an earlier one.
- **S4. The triage ranges (T1, D3).** A range counts the untriaged releases after the newest release any section is checked through. Above 20 of them, `packets --triage` refuses and names the `--through` of the first range of 20. A settled range prints the next range's `packets --triage --through`, the 20th untriaged release after its own, so no session counts releases. A range takes every release up to its `--through` that is untriaged for some section, with no lower bound. A lower bound would let a section deferred in an earlier range advance past releases nobody triaged clean for it; this way it shows them again, without their counting toward the 20. Counting all untriaged releases instead would name the same first range in every later session while a deferral stands, which is review finding 5's loop by another path. Block findings belong to no release and show the current docs, so they ride in every range, and the first range settles them; their sections advance only to that range's end. The first design held their candidates in every range but the last. The review showed why that fails: a held section keeps its old `checked`, so each new batch re-chose the same first range and never reached the last. A missing page needs a `manifest.toml` edit, so it is an owner item whose sections are held.
- **S5. An owner item caps the advance** below the oldest release it names, so no section advances past a release nobody read. The cap reads the release recorded with each owner item, not its wording. A bullet whose row does not parse, or whose NOISE row's quote fails, sends the sections its terms hint at to verify, or becomes such an owner item when it hints at none.
- **S6. The hold rules** (Task 1: `r8.8.1`). The spec's discard rule says nothing about the bookkeeping after a discard, and advancing past an unverified correction would hide it. A held section gets no `advance`, no `audited` and no rebaseline of a block it is a candidate of; a held file gets no `cite`. A section is held when:
  - no surviving A row or `<section> | none` line answers for it (S19);
  - a discarded correction, a discarded `JUDGMENT (mechanism STALE)` row or an A row that does not parse concerns it. An A row whose line is in no section, past the guide's end included, holds every section;
  - a correction to it goes to the owner: one within a TODO's reach, or one the session leaves (S21). A surviving `JUDGMENT (mechanism STALE)` row holds it too, since its judgment waits for the owner;
  - its triage held it, which `settled.json` carries into verify, or a missing page holds it.

  Only a section in the packet is held; a row outside its sections holds nothing (S24).

  A hold keeps `accept`: lint fails on a section whose text changed without one, so a held section's applied corrections still get it. A B or C row that does not parse is listed and holds nothing, but makes settle exit 1.
- **S7. A `TODO(owner)` reaches through the first list item after it** (Task 1: `r8.5`). There were two readings:
  - the prototype's fixed eight lines after the TODO;
  - the TODO's own words: the guide's one TODO, at line 418, names "the first bullet below".

  The verify rep returned two PARTIAL rows at line 426, the fourth bullet after the one the TODO names. The eight-line reach made both owner's calls; the verifier itself had treated them as checkable. The reach takes the first item's continuation lines and nested content (review finding 8); when no list item follows, it runs to the end of the TODO's section. A list-like line in fenced code is no list item, and a TODO in fenced code is an example (second review, finding 7). On the real guide it covers lines 418–422, and line 426 is outside it. The verifier contract states the same reach. Within it the verifier gives each claim its usual verdict and `settle` routes a correction to the owner, holding its section; the contract had said to report everything there as JUDGMENT, which holds nothing (second review, finding 2).
- **S8. Verify and audit copy their groups' pages into `<head>/docs/`**, which is R8.5's "current snapshot, copied from `latest/`". They use the copy `baseline rebaseline` uses, which never overwrites different bytes and never writes the bootstrap. Pages refetch only when the head moves (R6.3), so at a given head the two hold the same bytes. The changelog refetches on every run, so it is copied into each verify and audit packet instead.
- **S9. `settled.json` carries each verify section's evidence**: the block's reference or the bullet's text, with the verifier's row. The verify packet's `sections.md` then shows the verifier why each section was sent.
- **S10. R8.7's row reads `file:line`** (Task 1: `r8.7`), matching the other modes' `doc:line`.
- **S11. `quotes --in <dir>` prints `MISSING file`** (Task 1: `r8.3`), so a miss names its file.
- **S12. The skill and the agent are project-local and original.** NOTICE gains no entry: `check_provenance.py` reads `skills/` only, and nothing in them is adapted. CLAUDE.md's originals list is unchanged, and `check_frontmatter.py` stays unchanged (R12.4; the spec's out-of-scope bullet on `.claude/`).
- **S13. Costs.** The skill states the spec's costs (R8.4–R8.6). The three real-agent probes cost $1.32 to $1.58 each, and $0.52 to $0.67 of each went to auto mode's classifier. That is recorded here and in "Live run" for the owner. A permission rule that spares the classifier those reads is an owner-gated settings change.
- **S14. T6 dispositions.** Task 4 folds in three items: the `cite` guard, the refusal of an HTML-form citation above a frontmatter kind's frontmatter, and the on-demand Markdown rule. Two items are re-deferred by name:
  - **CRLF**, on its existing Revisit: no tracked file is CRLF, and the `cite` write is unchanged.
  - **The style minors.** Their Revisit fires, because this plan edits `state.py`, `check.py` and `cli.py`. None of the lines they name is in this plan's edit blocks, though: `state.py:78` and `:92`, `cli.py:132-139`, `summary()`, `test_state.py:318` and `:331`, and `CLAUDE.md:126`. The `CLAUDE.md:126` reflow would take the file to 187 of the 190 lines.

- **S15. Only quote fields may hold `|` and `"`** (Task 1: `r8.10`; Task 6). The first grammar let any field that opened with `"` run to a closing quote. In the skill probe, the verifier opened a free-text statement with a quoted phrase from the file, and settle discarded the misread row. Each format's quote fields sit at fixed positions, so the quote rule now applies to those fields only.
- **S16. The skill's rules on what the session may do after settle**, from the skill probe's baseline. Each is a prohibition with its reason, the form for a gate negotiated under pressure (writing-skills), and run 6 tested them:
  - apply only what settle lists. Edit only the guide (verify, audit) or the reviewed file (files), plus two follow-ons of the same fix: the register `[[exception]]` it resolves (R8.8; review finding 15), and `runtimes/`, regenerated by `build/sync_runtime_assets.py` for a canonical agent or command (CLAUDE.md, "Runtime adapters"). A fix reaching any other file is the owner's call;
  - an item left for the owner holds its section or file: run `settle --hold` (S21) and the commands it prints;
  - what settle held or discarded stands: no edits to `report.md`, no asking the verifier to reword, no reading settle's code to get past it.

  Only `cite` waits for a file's last contradiction; lint and `check_conformance.py` run after any fix (review finding 16). Verify and audit run `check --worktree` first unless the run's triage just did, so an old cache is never audited as today's (finding 14).
- **S17. A contradiction the register records as a `deviation` holds nothing** (D5; Task 1: `r8.8.2`). The register's `deviation` is the owner's standing decision, so `agents/explore.md`'s capital-E `name` (`explore-capitalised-name`) no longer keeps that file in the backlog. A `gap` is a fix not yet made, so it holds. A deviation covers only the statement its `guide` line names. In run 6 the control held the deviation-covered file in every rep; with the rule, every rep cited it, and no rep stretched the deviation over the decoy's other statement. R8.8 step 2 and settle's files header now say so too (second review, finding 10), and run 6b re-ran both scenarios against that header.
- **S18. A doc quote counts only in the docs** (review finding 1). Verify and audit re-grep a doc quote in the head snapshot's pages and the packet's `changelog.md` only. The first version searched the whole packet, so a verifier's own `report.md`, the guide copy or `index.json` could serve as evidence. A triage source quote likewise counts only within its own item's text: a block's lines in `blocks.md`, which its index entry names, or a bullet's text. Quoting the packet's own headings, or another item's text, no longer clears a NOISE row.
- **S19. Every section, and every cited section, is answered** (review finding 2; Task 1: `r8.5`, `r8.7`). Each gets a surviving row or a `<section> | none` line, the seventh report format. Silence holds it, as silence fails safe in triage, so an empty or prose-only report holds everything. A files row naming a section the file does not cite does not parse, so it holds the file (second review, finding 8).
- **S20. `-` is an empty field everywhere** (review finding 9): it proposes no wording, and gives NOISE no why. A quote a row may omit is re-grepped whenever it is given (finding 13), a NOISE row's guide quote included (second review, finding 3). A B or C row must parse (finding 12), and a B row names a release and `changelog.md:<line>` (second review, finding 9).
- **S21. `settle --hold <sections | file>`** prints the commands again with the named sections or file held. It replaces asking the session to drop items from a printed command list, and refuses names outside the packet.
- **S22. Two CLI defaults** (the review's open questions; Task 1: `r6.11`, `r8.6`). `--verify` with no IDs takes the sections a settled triage (`--from`) sent on, which R8.5's `verify [<ids>]` allows. `--audit` with no group refuses when no audit is due, naming the date, and a named group is audited anyway.
- **S23. Packets never land in a checkout** (review finding 10; second review, finding 4; spec Decision 10). `packets` refuses an `--out` inside any checkout, found by the nearest `.git`, a directory or a linked worktree's file: the repo's own, the main checkout a worktree sits in, or a sibling worktree, through a symlink too. Task 8's smoke packets take the cache's default.
- **S24. A row outside the packet's sections holds nothing** (second review, finding 1; D6; Task 1: `r8.8.1`, `r8.8.3`). The triage's commands advance the sections it cleared before any verify runs, so a verify that held one would claim a hold it cannot keep. A correction outside the packet's sections goes to the owner and names the `/cc-guide verify` that reviews its section; a discarded or unparseable row there, or a `JUDGMENT (mechanism STALE)` there, holds nothing either. The alternative was to hold back the cleared sections' advance until every verify reconciles, which stalls the triage's advance whenever a verify is deferred, names the same range again, and needs a reconcile step across groups.
- **S25. A page waits whole for its rebaseline** (second review, finding 5; Task 1: `r8.8.1`). `baseline rebaseline` refuses a listed run while an unlisted baselined block on the page also changed or is gone. So while a changed or missing block on a page stays unresolved, settle lists none of that page's blocks; an unresolved new block, never baselined, holds nothing back. Each block entry names its `page`.
- **S26. No backward advance** (second review, finding 6; Task 1: `r8.8.4`). A verify packet names each section's checked release (`checked`), and settle advances only a section not checked past the triage's target. A triage capped below a release, by an owner item or an early `--through`, could otherwise print an `advance` that `baseline` refuses.

### Independent review (D2)

Codex (`gpt-6-astra`, max effort) reviewed the first draft read-only against the spec, the brief, plan 43's conventions and the replay. It returned 18 findings: 10 P1, 7 P2 and 1 P3. Each was reproduced before it was fixed, and all 18 are fixed:
- findings 1 → S18; 2 → S19; 3, 4 → S5; 5 → S4; 6, 7, 11 → S6; 8 → S7; 9, 12, 13 → S20; 10 → S23;
- 14, 15, 16 → S16; 17 → run 6; 18 → runs 1 and 2's corrected counts above.

Its open questions are D5, S22 and Task 8's four known failures, which Validation 6 meets as plan 43's did. It confirmed that every block applied to `4991f4b` with unique anchors and that the reconstructed files equalled the replay; it ran no pytest. The rebuilt replay meets the same checks. The prompt and report are in the evidence directory's `review/`.

**Second review (D6).** The same seat reviewed the committed draft (`7ad57b5`) read-only, focused on what the fix wave changed. It returned 11 findings: 4 P1, 6 P2 and 1 P3. Each was reproduced against the prototype before it was fixed (`review2/test_review2_repro.py`), and all 11 are fixed:
- findings 1 → S24; 2, 7 → S7; 3, 9 → S20; 4 → S23; 5 → S25; 6 → S26; 8 → S19; 10 → S17 and run 6b; 11 → run 6's corrected count.

Its table marked the first round's findings 7, 8, 10, 12 and 13 partly fixed; findings 1–4, 7 and 9 complete them. It confirmed the blocks applied with unique anchors, the reconstructed files equalled the replay, and the deltas summed; it could not run pytest in its sandbox, and had no owner questions. The prompt and report are in `review2/`.

### The brief's traps (T1–T7)

- **T1.** No release or block count is stated as an expectation; S4 says how `packets --triage` splits block findings.
- **T2.** No new git call (Global Constraints, "Git calls").
- **T3.** The Haiku 5.5 case is Task 6's fixture and DF2's amendment wording. A-53 and H-57 close on the live `audit models` ("Live run").
- **T4.** Task 7 writes its tests before the files, puts each citation on the frontmatter's last line, and rewords `build/CLAUDE.md`'s bare `cc-guide:`. In the replay, adding the skill without that rewording made `check_conformance.py` exit 1 with `dmi-handoff-consistency` naming `build/CLAUDE.md`. `trigger-phrase-presence` passes, since the description quotes its trigger phrases. New text writes `/cc-guide`, a path or `cc-guide-verifier`, never a bare `cc-guide`.
- **T5.** Task 3 carries each finding's key hash and reads a group's baselined block text by key hash. Task 5's triage packet shows a missing block's baselined text from its page's snapshot. The item is ticked at completion.
- **T6.** S14.
- **T7.** "Live run", step B.

### Coverage gaps (R4.3; listed in the completion report for the owner)

Two Claude Code facts the new files rely on that no guide section covers:
- **G1.** When a skill's body has no `$ARGUMENTS`, the typed words are appended as an `ARGUMENTS:` line, which is how `/cc-guide` reads its mode. `skills.arguments` documents `$ARGUMENTS` only. Using `$ARGUMENTS` explicitly would rest on a covered fact, but the register's `substitution-hazard` check fails any unescaped `$ARGUMENTS` in a skill body. Changing that is the owner's register.
- **G2.** A project subagent reads files outside the project in auto mode, and auto mode's classifier approves and bills those reads. No section covers subagent file access outside the project; `rules.settings` mentions classifier billing for broad Bash rules only.

### Plan ID

`entry_check.py` (2026-10-12) reports `next free: 44` and no collisions; `main` and `origin/main` are both `4991f4b`. Plan 43 (Stage 2) is retired. The SDD bundle takes the next free ID after this one.

### CLAUDE.md line budget

186 lines at `4991f4b`, and 186 after this plan: Task 7 extends the drift detector's comment line in place. The style minors' `CLAUDE.md:126` reflow stays deferred (S14).

---

### Task 1: Spec amendments (S1, S3–S7, S10, S11, S15, S17–S26, DF2, D3)

**Files:**
- Modify: `specs/claude-code-drift-automation-spec.md` (Layout, R6.11, R8.3, R8.4, R8.5, R8.6, R8.7, R8.8, a new R8.10, R11.5, Sequencing item 3, Validation 3)

Each edit is tagged `(owner, plan 44, 2026-10-12)`; the status line stays untouched. Your human partner approves this wording at plan review.

- [x] **Step 1: The Layout names `settle` and its modules (S1, S2)**

**Edit** `specs/claude-code-drift-automation-spec.md` — replace:

```text
    subcommands, named in code font below, are `lint`, `check`, `packets`,
    `quotes`, `baseline <sub>`, `probes` and `binaries`. Each one's logic lives
    in its own module (`lint.py`, `check.py`, `baseline.py`, `quotes.py`,
    `probes.py`), on shared parsers for the guide, anchors and citations
    (`guide.py`) and for docs blocks (`blocks.py`);
```

with:

```text
    subcommands, named in code font below, are `lint`, `check`, `packets`,
    `quotes`, `settle`, `baseline <sub>`, `probes` and `binaries`. Each one's
    logic lives in its own module (`lint.py`, `check.py`, `packets.py`,
    `quotes.py`, `settle.py`, `baseline.py`, `probes.py`), on shared parsers
    for the guide, anchors and citations (`guide.py`) and for docs blocks
    (`blocks.py`) (owner, plan 44, 2026-10-12);
```

- [x] **Step 2: R6.11's grammar and packet layout (S3, S4, S22, S23)**

**Edit** `specs/claude-code-drift-automation-spec.md` — replace:

```text
R6.11 **Packets.** `packets --triage | --verify <ids> | --audit <group> |
--files [<paths>] --out <dir>` writes the files the skill hands to its
verifier (R8), from the same inputs as `check --worktree`.
```

with:

```text
R6.11 **Packets.** `packets --triage [--through <release>] | --verify [<ids>]
[--from <dir>] | --audit [<group>] | --files [<paths>]`, with an optional
`--out <dir>`, writes the files the skill hands to its verifier (R8), from
the same inputs as `check --worktree`, reading the last fetch and never
fetching. Each packet is a directory holding an `index.json` (its mode, the
items the verifier answers for and the files each kind of quote is checked
in), the guide copied whole, and its mode's Markdown files. `--out` defaults
to a new directory under the cache's `packets/`, and a directory inside any
checkout is refused, since packets hold docs text (Decision 10); `--verify`
writes one packet per group and `--files` one per file. `--audit` with no
group takes the due one, and refuses when none is due. `--from` names a
settled triage packet, whose advance target, cleared and held sections and
rows carry over (R8.10); `--verify` with no IDs then takes the sections it
sent on (owner, plan 44, 2026-10-12).
```

- [x] **Step 3: R8.3's `--in` and `MISSING file` (S11)**

**Edit** `specs/claude-code-drift-automation-spec.md` — replace:

```text
R8.3 **`quotes`** reads `file<TAB>quote` rows on stdin against a named file
set and prints `FOUND file:line` or `MISSING` per row, exiting 1 on any miss.
```

with:

```text
R8.3 **`quotes --in <dir>`** reads `file<TAB>quote` rows on stdin against the
files under `<dir>` and prints `FOUND file:line` or `MISSING file` per row,
exiting 1 on any miss (owner, plan 44, 2026-10-12).
```

- [x] **Step 4: R8.4 step 1, the missing block's text and the ranges (S4, T5, D3)**

**Edit** `specs/claude-code-drift-automation-spec.md` — replace:

```text
1. Run `check --worktree`, then `packets --triage`: the whole guide with line
   numbers; each changed, missing or new block's current text, with a unified
   diff against its snapshot when that is cached; and every bullet of every
   untriaged release, with term hits marked. After a long absence, split it by
   release range.
```

with:

```text
1. Run `check --worktree`, then `packets --triage`: the whole guide with line
   numbers; each changed or new block's current text, with a unified diff
   against its snapshot when that is cached, and each missing block's
   baselined text, read from its page's snapshot by key hash; and every bullet
   of every untriaged release, with term hits marked. After a long absence,
   split it by release range. A range counts the untriaged releases after
   the newest release any section is checked through; above 20 of them
   `packets --triage` refuses and names the `--through <release>` of the
   first range of 20, and each settled range names the next one's, the 20th
   untriaged release after its own. A range takes every release up to its
   `--through` that is untriaged for some section, so a section deferred in
   an earlier range shows its earlier releases again, without their counting
   toward the 20. Block findings belong to no release and
   show the current docs, so they ride in every range, and the first range
   settles them; their sections advance only to that range's end. A missing
   page needs a `manifest.toml` edit, so it is an owner item whose sections
   are held (owner, plan 44, 2026-10-12).
```

- [x] **Step 5: R8.4 step 4, the owner cap (S5)**

**Edit** `specs/claude-code-drift-automation-spec.md` — replace:

```text
   line becomes UNSURE for every section whose terms its bullets hit, or an
   owner item when they hit none. Silence never counts as NOISE.
```

with:

```text
   line becomes UNSURE for every section whose terms its bullets hit, or an
   owner item when they hit none; an owner item stops the advance below its
   release (owner, plan 44, 2026-10-12). Silence never counts as NOISE.
```

- [x] **Step 6: R8.5, the TODO reach and the none line (S7, S19)**

**Edit** `specs/claude-code-drift-automation-spec.md` — replace:

```text
  cache-read prices is an example. Lines next to a `TODO(owner)` are
  report-only.
```

with:

```text
  cache-read prices is an example. A `TODO(owner)` is report-only from its
  own line through the first list item after it outside fenced code, that
  item's continuation lines included, or to the end of its section when no
  list item follows: a claim there gets its usual verdict, and a correction
  there goes to the owner (R8.8 step 3). Each section in scope gets at least
  one A row, or a `<section> | none` line when it holds no checkable claim
  (owner, plan 44, 2026-10-12).
```

- [x] **Step 7: R8.6, an audit when none is due (S22)**

**Edit** `specs/claude-code-drift-automation-spec.md` — replace:

```text
R8.6 **`/cc-guide audit [<group>]`.** With no argument, the due group (R6.7).
```

with:

```text
R8.6 **`/cc-guide audit [<group>]`.** With no argument, the due group (R6.7);
when none is due, `packets` refuses, and a named group is audited anyway
(owner, plan 44, 2026-10-12).
```

- [x] **Step 8: R8.7's row form and none line (S10, S19)**

**Edit** `specs/claude-code-drift-automation-spec.md` — replace:

```text
2. One verifier per file returns rows of
   `file line | statement | section | "verbatim guide quote" | consistent / contradicts / not covered`.
```

with:

```text
2. One verifier per file returns rows of
   `file:line | statement | section | "verbatim guide quote" | consistent / contradicts / not covered`,
   and a `<section> | none` line for each cited section no statement rests
   on (owner, plan 44, 2026-10-12).
```

- [x] **Step 9: R8.8 step 1, the hold rules (S6, S19, S20, S24, S25)**

**Edit** `specs/claude-code-drift-automation-spec.md` — replace:

```text
1. `quotes` re-greps every quote. A row whose quote fails is discarded and
   listed as unverified. This is the refresh's rule, and the opposite of
   triage's escalation.
```

with:

```text
1. `quotes` re-greps every quote, and a quote a row may omit is re-grepped
   when it is given. A row whose quote fails is discarded and listed as
   unverified. This is the refresh's rule, and the opposite of triage's
   escalation. So is a STALE, WRONG or PARTIAL row whose proposed wording is
   empty or `-`. A section is held, which means no `advance`, no `audited`
   and no `rebaseline` of a block whose candidates include it, nor, while
   that block is changed or missing, of any other block on its page (R7),
   when: no surviving A row or `<section> | none` line answers for it; a
   discarded STALE, WRONG, PARTIAL or `JUDGMENT (mechanism STALE)` row, or
   an A row that does not parse, concerns it; a correction to it is left for
   the owner, within a `TODO(owner)`'s reach or by the run, or a
   `JUDGMENT (mechanism STALE)` row survives; or its triage held it. Only a
   section in the packet is held: a row whose line falls outside the
   packet's sections holds nothing, since the run neither reviews nor
   advances that section, and its triage may have advanced it already. An
   A row whose line falls in no section holds every section in the packet;
   a B or C row that does not parse holds nothing. In `files`, a cited
   section with no surviving row or none line, a discarded `contradicts`
   row, or a row that does not parse or names a section the file does not
   cite holds the file: no `cite`. A hold keeps `accept` for the text the
   run changed (owner, plan 44, 2026-10-12).
```

- [x] **Step 10: R8.8 step 2, a registered deviation (S17, D5)**

**Edit** `specs/claude-code-drift-automation-spec.md` — replace:

```text
2. Surviving corrections are applied **in the working tree only**: guide
   prose for STALE, WRONG and PARTIAL rows; citing-file text for
   `contradicts` rows.
```

with:

```text
2. Surviving corrections are applied **in the working tree only**: guide
   prose for STALE, WRONG and PARTIAL rows; citing-file text for
   `contradicts` rows. A `contradicts` row that
   `build/cc_guide/conformance.toml` records as a `deviation` for that file
   and statement is the owner's standing decision: it stays as it is and
   holds nothing. One a `gap` records is a fix not yet made, so it holds the
   file (owner, plan 44, 2026-10-12).
```

- [x] **Step 11: R8.8 step 3, what goes to the owner (S6, S7, S24)**

**Edit** `specs/claude-code-drift-automation-spec.md` — replace:

```text
3. JUDGMENT items and `not covered` rows go to an owner's-call list and are
   never applied; a `not covered` row may also be a coverage gap (R4.3).
```

with:

```text
3. JUDGMENT and NOT FOUND items, C omissions and `not covered` rows go to an
   owner's-call list and are never applied, and so does a correction to a
   line within a `TODO(owner)`'s reach (R8.5) or outside the packet's
   sections, which `settle` lists with the `/cc-guide verify` that reviews
   it; a `not covered` row may also be a coverage gap (R4.3) (owner,
   plan 44, 2026-10-12).
```

- [x] **Step 12: R8.8 step 4, no backward advance (S26)**

**Edit** `specs/claude-code-drift-automation-spec.md` — replace:

```text
   - `advance` to the newest release the run covered: the newest triaged
     release for `verify`; for an audit, `audited` instead;
```

with:

```text
   - `advance` to the newest release the run covered: the newest triaged
     release for `verify`, for each section not checked past it already
     (owner, plan 44, 2026-10-12); for an audit, `audited` instead;
```

- [x] **Step 13: R8.10, `settle` (S1, S9, S15, S18–S21)**

> Deviation: the final review's fix wave (owner, 2026-10-13) amended the spec again: R6.11 (a packet's `cache` key, `--out` checked before any snapshot write, `--from` refusing a cleared ID), R7 (`baseline audited GROUP --to RELEASE`), R8.4 steps 5–6 (a failed block-row quote sends every candidate on; a broken line flags what it names, a broken coverage line leaves its release uncovered, a line naming nothing holds the packet; a block that flags another group's section holds its own group's rebaseline) and R8.10 (list markers stripped, template and table headers skipped, a line past the guide's end holds every section, an outside-the-packet none line holds nothing, printed commands carry a non-default `--cache`), each tagged `(owner, plan 44, 2026-10-13)`.

**Edit** `specs/claude-code-drift-automation-spec.md` — replace:

```text
R8.9 **`/cc-guide probes`** runs `probes` (R10).
```

with:

```text
R8.9 **`/cc-guide probes`** runs `probes` (R10).

R8.10 **`settle <packet> [--hold <ids or file>]`** is the deterministic step
between a verifier's report and the bookkeeping (owner, plan 44,
2026-10-12). The skill saves the report unchanged as `report.md` in its
packet. `settle` parses its rows, re-greps every quote as `quotes` does,
applies R8.4 steps 4-6 to a triage and R8.8 steps 1-3 to the other modes,
and prints the corrections, the owner's-call items, what it held, and R8.8
step 4's `baseline` commands in order, followed by `lint` and
`check_conformance.py`. A row splits on `|`: a quote field that opens with
`"` runs to the first `"` followed by `|` or the end of the line, any other
field ends at the next `|`, and the last field takes the rest of the line;
`-` marks an empty field. A table's outer pipes, header rows and separator
rows are ignored; any other line holding `|` that is no row is listed as
unparseable. A triage source quote counts only within its own item's text. A
NOISE row whose source quote, or a guide quote it gives, fails sends its
section and its block's candidate sections to verify. A bullet's triage row
that does not parse, or a bullet's NOISE row whose quote fails, sends the
sections its terms hint at, or is an owner item when they hit none. A doc
quote counts only in the snapshot's pages or the packet's `changelog.md`. A
settled triage writes `settled.json` in its packet for
`packets --verify --from`: the advance target, the sections it cleared and
held, and the rows that sent each verify section; a ranged triage also
prints the next range's `packets --triage --through`. `--hold` names the
sections, or the file, the run leaves for the owner, and prints the
commands again with them held. `settle` exits 0 when every row parsed,
every quote was found, and nothing was discarded or left out; 1 otherwise.
It applies nothing and commits nothing.
```

- [x] **Step 14: R11.5's first triage (DF2, D1)**

**Edit** `specs/claude-code-drift-automation-spec.md` — replace:

```text
- Triage the backlog since 2.1.288. 2.1.289's deny/ask-rule notes should come
  back TOUCHES for `rules.settings` and `hooks.pitfalls`.
```

with:

```text
- Triage the untriaged backlog; PRs #23 and #38 triaged 2.1.289 to 2.1.296 by
  hand (owner, plan 44, 2026-10-12). The worked example is now a hand-written
  fixture modelled on 2.1.293, where Haiku 5.5 became the `haiku` alias on
  the Anthropic API: the release's bullet hints one section while the docs
  block that changed names more, and a verifier that answers the bullet and
  leaves the block out still sends every candidate section to verify.
```

- [x] **Step 15: Sequencing item 3's first jobs (DF1, DF2)**

**Edit** `specs/claude-code-drift-automation-spec.md` — replace:

```text
   (owner, plan 38, 2026-10-04). Its first jobs are triaging the backlog
   since 2.1.288 and the first `files` batch.
```

with:

```text
   (owner, plan 38, 2026-10-04). Its first jobs, run after its merge, are
   triaging the untriaged backlog, one `audit` and the first `files` batch
   (owner, plan 44, 2026-10-12).
```

- [x] **Step 16: Validation 3's triage bullet (DF2)**

**Edit** `specs/claude-code-drift-automation-spec.md` — replace:

```text
   - Triaging the backlog since 2.1.288 produces quote-checked rows.
```

with:

```text
   - Triaging the untriaged backlog produces quote-checked rows; while
     `check` shows nothing untriaged, this waits for the next release
     (owner, plan 44, 2026-10-12).
```

- [x] **Step 17: Lint and commit**

> Deviation: the commits for Tasks 1–7 end with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`, the executing session's model then, not the `Claude Opus 5.5` the commit blocks show (Global Constraints, trailer rule). The session moved to Opus 5.5 for the final review's fix wave, whose six commits (f775b22..b970318) end with `Claude Opus 5.5`.

Run `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 --python 3.13 python build/cc_guide/cli.py lint`. Expected: exit 0 (the spec sits outside the citation scan, and no label changed). Confirm the branch (Global Constraints), then:

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 add specs/claude-code-drift-automation-spec.md
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 commit -m "docs(specs): drift Stage 3 amendments for packets, settle and the first jobs" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: `quotes` (R8.3)

**Files:**
- Create: `build/cc_guide/quotes.py`, `build/cc_guide/test_quotes.py`
- Modify: `build/cc_guide/cli.py` (module docstring; imports; `parser`; a new `run_quotes`; `main`)

**Interfaces:**
- Produces:
  - `quotes.QuoteFiles(root: Path)`, with `.lines(name: str) -> list[str] | None` (None when the name leaves `root` or is not a file), `.find(name: str, quote: str) -> int | None` (the 1-based line holding the whole quote; an empty quote is never found) and `.find_any(names: Iterable[str], quote: str) -> tuple[str, int] | None` (the first name, in order, that holds it);
  - `quotes.check_rows(root: Path, rows: Iterable[str]) -> tuple[list[str], bool]`: `FOUND file:line` or `MISSING file` per `file<TAB>quote` row, skipping blank and `#` rows, and whether all were found;
  - `cli.py quotes --in DIR`: exit 0 when all are found, 1 on any miss, 2 when DIR is not a directory (`cc-guide: DIR: not a directory`).

- [x] **Step 1: Write the failing tests**

**Create** `build/cc_guide/test_quotes.py`:

```python
'''Tests for quotes.py and `cli.py quotes`: a quote counts only whole within
one line of a file under the named root (drift spec R8.3).'''
import io

import pytest

import cli
import quotes
from cc_fixtures import isolated_home, write_tree  # noqa: F401


@pytest.fixture
def root(tmp_path):
    folder = tmp_path / 'docs'
    write_tree(folder, {'hooks.md': 'Exit 2 blocks the call.\nA JSON | deny "blocks" too.\n',
                        'sub/page.md': 'One line.\nTwo line.\n'})
    (tmp_path / 'outside.md').write_text('Exit 2 blocks the call.\n')
    return folder


def test_a_quote_is_found_whole_within_one_line(root):
    files = quotes.QuoteFiles(root)
    assert files.find('hooks.md', 'Exit 2 blocks') == 1
    assert files.find('hooks.md', 'A JSON | deny "blocks" too.') == 2
    assert files.find('sub/page.md', 'Two line.') == 2
    assert files.find('sub/page.md', 'One line. Two line.') is None  # never across lines
    assert files.find('hooks.md', 'exit 2 blocks') is None           # case-sensitive


def test_an_empty_quote_a_missing_file_and_a_path_outside_the_root_are_never_found(root):
    files = quotes.QuoteFiles(root)
    assert files.find('hooks.md', '') is None
    assert files.find('nope.md', 'Exit') is None
    assert files.find('../outside.md', 'Exit 2 blocks') is None
    assert files.find(str(root.parent / 'outside.md'), 'Exit 2 blocks') is None
    assert files.find('sub', 'One') is None


def test_find_any_takes_the_first_file_in_order_that_holds_the_quote(root):
    files = quotes.QuoteFiles(root)
    assert files.find_any(['nope.md', 'sub/page.md', 'hooks.md'], 'line.') == ('sub/page.md', 1)
    assert files.find_any(['hooks.md'], 'line.') is None


def test_rows_print_found_or_missing_and_skip_blanks_and_comments(root):
    rows = ['hooks.md\tExit 2 blocks\n', '\n', '# a comment\n', 'sub/page.md\tTwo line.\n',
            'hooks.md\tnot there\n', 'no-tab-here\n']
    assert quotes.check_rows(root, rows) == (
        ['FOUND hooks.md:1', 'FOUND sub/page.md:2', 'MISSING hooks.md', 'MISSING no-tab-here'], False)
    assert quotes.check_rows(root, ['hooks.md\tExit 2 blocks\n']) == (['FOUND hooks.md:1'], True)


def test_a_quote_keeps_any_tab_after_the_first(root):
    write_tree(root, {'tabs.md': 'a\tb\n'})
    assert quotes.check_rows(root, ['tabs.md\ta\tb']) == (['FOUND tabs.md:1'], True)


def test_the_cli_exits_one_on_any_miss_and_two_without_a_directory(root, monkeypatch, capsys):
    monkeypatch.setattr('sys.stdin', io.StringIO('hooks.md\tExit 2 blocks\n'))
    assert cli.main(['quotes', '--in', str(root)]) == 0
    assert capsys.readouterr() == ('FOUND hooks.md:1\n', '')
    monkeypatch.setattr('sys.stdin', io.StringIO('hooks.md\tExit 2 blocks\nhooks.md\tExit 3\n'))
    assert cli.main(['quotes', '--in', str(root)]) == 1
    assert capsys.readouterr() == ('FOUND hooks.md:1\nMISSING hooks.md\n', '')
    assert cli.main(['quotes', '--in', str(root / 'nope')]) == 2
    assert capsys.readouterr() == ('', f"cc-guide: {root / 'nope'}: not a directory\n")
```

- [x] **Step 2: Run them to verify they fail**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3/build/cc_guide --python 3.13 --with pytest python -m pytest -q test_quotes.py`
Expected: `1 error` during collection, `ModuleNotFoundError: No module named 'quotes'`.

- [x] **Step 3: Write `quotes.py`**

**Create** `build/cc_guide/quotes.py`:

```python
'''`quotes`: re-grep a verifier's quotes against the files they came from
(drift spec R8.3). A quote counts only when it appears whole within one
line, the method that found 151 of 151 quotes in the 2026-10-03 refresh.
It succeeds the snapshot's check/qcheck.py.'''
from collections.abc import Iterable
from pathlib import Path


class QuoteFiles:
    '''The files under one root that quotes may name, each read once.'''

    def __init__(self, root: Path):
        self.root = root.resolve()
        self._lines: dict[str, list[str] | None] = {}

    def lines(self, name: str) -> list[str] | None:
        '''The file's lines, or None when name leaves the root or is no file.
        Bytes that are not UTF-8 read as U+FFFD, which no quote matches.'''
        if name not in self._lines:
            path = (self.root / name).resolve()
            inside = path.is_relative_to(self.root) and path.is_file()
            self._lines[name] = path.read_text(encoding='utf-8', errors='replace').split('\n') if inside else None
        return self._lines[name]

    def find(self, name: str, quote: str) -> int | None:
        '''The 1-based line of name that holds quote whole, or None. An empty
        quote is never found: it would sit inside every line.'''
        lines = self.lines(name)
        if not quote or lines is None:
            return None
        return next((n for n, line in enumerate(lines, start=1) if quote in line), None)

    def find_any(self, names: Iterable[str], quote: str) -> tuple[str, int] | None:
        '''The first of names, in order, whose line holds quote: (name, line).'''
        for name in names:
            line = self.find(name, quote)
            if line is not None:
                return name, line
        return None


def check_rows(root: Path, rows: Iterable[str]) -> tuple[list[str], bool]:
    '''R8.3: each `file<TAB>quote` row as `FOUND file:line` or `MISSING
    file`, and whether every row was found. Blank rows and `#` comments are
    skipped; a row without a tab has an empty quote, so it is MISSING.'''
    files = QuoteFiles(root)
    out: list[str] = []
    for raw in rows:
        row = raw.rstrip('\n')
        if not row.strip() or row.startswith('#'):
            continue
        name, _, quote = row.partition('\t')
        line = files.find(name, quote)
        out.append(f'MISSING {name}' if line is None else f'FOUND {name}:{line}')
    return out, not any(o.startswith('MISSING') for o in out)
```

- [x] **Step 4: Wire `quotes` into the CLI**

**Edit** `build/cc_guide/cli.py` — replace:

```python
'''cc_guide: the drift detector for specs/guides/claude-code-customization-guide.md
and the citations that point at it (Stages 1 and 2 of
specs/claude-code-drift-automation-spec.md).
```

with:

```python
'''cc_guide: the drift detector for specs/guides/claude-code-customization-guide.md,
the citations that point at it, and the deterministic half of /cc-guide
(Stages 1 to 3 of specs/claude-code-drift-automation-spec.md).
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
      whole page. It also refuses to overwrite a snapshot page that holds
      other text.
```

with:

```python
      whole page. It also refuses to overwrite a snapshot page that holds
      other text.
  quotes --in DIR
      Read `file<TAB>quote` rows on stdin and print FOUND file:line or
      MISSING file for each, a quote counting only within one line of the
      file under DIR (R8.3). Exit 0 when all are found, 1 on any miss.
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
from lint import lint, stale_lines
```

with:

```python
from lint import lint, stale_lines
from quotes import check_rows
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
    b.add_parser('cite').add_argument('files', nargs='+')
    return p
```

with:

```python
    b.add_parser('cite').add_argument('files', nargs='+')
    sub.add_parser('quotes').add_argument('--in', dest='root', type=Path, required=True)
    return p
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
def main(argv=None, *, today: date | None = None, now: datetime | None = None, fetch=None) -> int:
```

with:

```python
def run_quotes(args) -> int:
    if not args.root.is_dir():
        raise SetupError(f'{args.root}: not a directory')
    lines, ok = check_rows(args.root, sys.stdin)
    print('\n'.join(lines))
    return 0 if ok else 1


def main(argv=None, *, today: date | None = None, now: datetime | None = None, fetch=None) -> int:
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
        if args.command == 'check':
            return run_check(args, cache, today, now, fetch or http_get)
```

with:

```python
        if args.command == 'check':
            return run_check(args, cache, today, now, fetch or http_get)
        if args.command == 'quotes':
            return run_quotes(args)
```

- [x] **Step 5: Run the suite to verify it passes**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3/build/cc_guide --python 3.13 --with pytest python -m pytest -q`
Expected: all pass, +6 over the baseline.

- [x] **Step 6: Commit**

Confirm the branch, then:

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 add build/cc_guide/quotes.py build/cc_guide/test_quotes.py build/cc_guide/cli.py
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 commit -m "feat(cc_guide): quotes re-greps verifier quotes within one line (R8.3)" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Key hashes, snapshot readers and the shared snapshot copy (T5)

**Files:**
- Modify: `build/cc_guide/check.py` (`Finding`; the four `Finding(...)` calls in `compare`)
- Modify: `build/cc_guide/state.py` (the `blocks` import; `block_namer` becomes four functions plus `copy_to_snapshot`)
- Modify: `build/cc_guide/cli.py` (the `state` import; `run_baseline`'s `rebaseline` branch)
- Test: `build/cc_guide/test_check.py`, `build/cc_guide/test_state.py`

**Interfaces:**
- Consumes: `blocks.key_hash`, `blocks.page_blocks`; `state.snapshot_docs`, `state.latest_docs`, `state.BOOTSTRAP_RELEASE`.
- Produces:
  - `check.Finding.key_hash: str | None`, the last field: the key as `baseline.json` stores it (R2.3); `None` for a missing page;
  - `state.snapshot_blocks(state: dict, group: str, snapshot) -> Callable[[str], dict[str, tuple[str, str]]]`: page → {key hash: (key, normalized text)}, each page read once;
  - `state.block_namer(...)` keeps its signature and behaviour;
  - `state.baselined_text(state: dict, group: str, snapshot) -> Callable[[str, str], str | None]`;
  - `state.writable_snapshot(cache: Path, release: str) -> Path`, refusing the bootstrap with the message `rebaseline` gave before;
  - `state.copy_to_snapshot(cache: Path, release: str, files: dict[str, str]) -> Path`: label → cache file name, every file checked before any is written, the refusal message `rebaseline` gave before.

- [x] **Step 1: Write the failing tests**

**Edit** `build/cc_guide/test_check.py` — replace:

```python
def test_deselection_is_informational_only_while_the_block_is_unchanged(docs_dir):
```

with:

```python
def test_each_block_finding_carries_its_key_hash(docs_dir):
    '''A packet reads a missing block's baselined text by key hash, which a
    name read back from a snapshot does not carry when the snapshot is gone.'''
    s = fixture_state(docs_dir)
    write_tree(docs_dir, {'events.md': DOCS['events.md'].replace('## Payload', '## Body').replace('on beta', 'on all')})
    found, _ = check.compare(MANIFEST, s, TERMS, offline(docs_dir), state.no_snapshot)
    assert [(f.kind, f.key_hash) for f in found] == [
        ('changed', blocks.key_hash('Events')), ('missing', blocks.key_hash('Events › Payload')),
        ('new', blocks.key_hash('Events › Body'))]
    (docs_dir / 'events.md').unlink()
    found, _ = check.compare(MANIFEST, s, TERMS, offline(docs_dir), state.no_snapshot)
    assert [(f.kind, f.key_hash) for f in found] == [('missing-page', None)]


def test_deselection_is_informational_only_while_the_block_is_unchanged(docs_dir):
```

**Edit** `build/cc_guide/test_state.py` — replace:

```python
import state
from cc_fixtures import (MANIFEST_TOML, fixture_repo, git, guide_text,  # noqa: F401
                         isolated_home)
```

with:

```python
import blocks
import state
from cc_fixtures import (MANIFEST_TOML, docs_dir, fixture_repo, fixture_snapshot, fixture_state, git,  # noqa: F401
                         guide_text, isolated_home)
```

**Edit** `build/cc_guide/test_state.py` — replace:

```python
    with pytest.raises(state.SetupError) as err:
        state.Source(repo).grep('(', ())
    assert str(err.value).startswith('git grep in the working tree: ')
```

with:

```python
    with pytest.raises(state.SetupError) as err:
        state.Source(repo).grep('(', ())
    assert str(err.value).startswith('git grep in the working tree: ')


def test_a_snapshot_names_each_baselined_block_and_gives_its_text(docs_dir):
    '''A packet shows a missing block's baselined text, read from the page's
    snapshot by key hash with the lookup that names it (R2.3).'''
    s = fixture_state(docs_dir)
    payload = blocks.key_hash('Events › Payload')
    assert state.block_namer(s, 'beta', fixture_snapshot)('events', payload) == 'Events › Payload'
    assert state.baselined_text(s, 'beta', fixture_snapshot)('events', payload) == (
        '## Payload\nThe payload carries `BETA_ENV`.')
    assert state.block_namer(s, 'beta', state.no_snapshot)('events', payload) == payload
    assert state.baselined_text(s, 'beta', state.no_snapshot)('events', payload) is None
    assert state.baselined_text(s, 'beta', fixture_snapshot)('events', '0' * 16) is None
```

- [x] **Step 2: Run them to verify they fail**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3/build/cc_guide --python 3.13 --with pytest python -m pytest -q test_check.py::test_each_block_finding_carries_its_key_hash test_state.py::test_a_snapshot_names_each_baselined_block_and_gives_its_text`
Expected: `2 failed`: `AttributeError: 'Finding' object has no attribute 'key_hash'` and `AttributeError: module 'state' has no attribute 'baselined_text'`.

- [x] **Step 3: Carry the key hash, read the snapshot's blocks, share the copy**

**Edit** `build/cc_guide/check.py` — replace:

```python
    candidates: list[str]

    def ref(self) -> str:
```

with:

```python
    candidates: list[str]
    key_hash: str | None    # the key as baseline.json stores it (R2.3); None for a missing page

    def ref(self) -> str:
```

**Edit** `build/cc_guide/check.py` — replace:

```python
                findings.append(Finding(gid, 'missing-page', page, None, list(sec_terms)))
```

with:

```python
                findings.append(Finding(gid, 'missing-page', page, None, list(sec_terms), None))
```

**Edit** `build/cc_guide/check.py` — replace:

```python
                    findings.append(Finding(gid, 'missing', page, gone, cands))
                elif block_hash(found[key]) != recorded:
                    findings.append(Finding(gid, 'changed', page, key, candidates(key, found[key], sec_terms)))
```

with:

```python
                    findings.append(Finding(gid, 'missing', page, gone, cands, kh))
                elif block_hash(found[key]) != recorded:
                    findings.append(Finding(gid, 'changed', page, key, candidates(key, found[key], sec_terms), kh))
```

**Edit** `build/cc_guide/check.py` — replace:

```python
                    findings.append(Finding(gid, 'new', page, key, candidates(key, found[key], sec_terms)))
```

with:

```python
                    findings.append(Finding(gid, 'new', page, key, candidates(key, found[key], sec_terms),
                                            key_hash(key)))
```

**Edit** `build/cc_guide/state.py` — replace:

```python
from blocks import CELL_SPLIT_RE, HASH_RE, key_names, page_blocks
```

with:

```python
from blocks import CELL_SPLIT_RE, HASH_RE, key_hash, page_blocks
```

**Edit** `build/cc_guide/state.py` — replace:

```python
def block_namer(state: dict, group: str, snapshot: Snapshot) -> Callable[[str, str], str]:
    '''Names one group's baselined blocks, (page, key hash) -> key: the key
    read back from the page's snapshot (R2.3), else the key hash itself.'''
    releases = state['groups'].get(group, {}).get('snapshot', {})
    names: dict[str, dict[str, str]] = {}

    def name(page: str, kh: str) -> str:
        if page not in names:
            text = snapshot(page, releases[page]) if page in releases else None
            names[page] = {} if text is None else key_names(page_blocks(text))
        return names[page].get(kh, kh)
    return name
```

with:

```python
def snapshot_blocks(state: dict, group: str, snapshot: Snapshot) -> Callable[[str], dict[str, tuple[str, str]]]:
    '''Reads one group's snapshot pages, page -> {key hash: (key, normalized
    text)}: each page as the release in the group's `snapshot` holds it
    (R2.3), {} when no snapshot holds it. Each page is read once.'''
    releases = state['groups'].get(group, {}).get('snapshot', {})
    held: dict[str, dict[str, tuple[str, str]]] = {}

    def read(page: str) -> dict[str, tuple[str, str]]:
        if page not in held:
            text = snapshot(page, releases[page]) if page in releases else None
            held[page] = {} if text is None else {key_hash(k): (k, body) for k, body in page_blocks(text).items()}
        return held[page]
    return read


def block_namer(state: dict, group: str, snapshot: Snapshot) -> Callable[[str, str], str]:
    '''Names one group's baselined blocks, (page, key hash) -> key: the key
    read back from the page's snapshot (R2.3), else the key hash itself.'''
    read = snapshot_blocks(state, group, snapshot)
    return lambda page, kh: read(page).get(kh, (kh, ''))[0]


def baselined_text(state: dict, group: str, snapshot: Snapshot) -> Callable[[str, str], str | None]:
    '''Reads one group's baselined blocks' text, (page, key hash) -> the
    block's normalized text as the page's snapshot holds it, else None. A
    block gone from the page has no current text, so a packet shows this.'''
    read = snapshot_blocks(state, group, snapshot)
    return lambda page, kh: read(page).get(kh, (kh, None))[1]


def writable_snapshot(cache: Path, release: str) -> Path:
    '''<release>/docs, which rebaseline and packets may write; the bootstrap
    snapshot is never written (R2.6).'''
    target = snapshot_docs(cache, release)
    if release == BOOTSTRAP_RELEASE:
        raise SetupError(f'{target} is the bootstrap snapshot, which is never '
                         'written (R2.6): run check to fetch a newer release first')
    return target


def copy_to_snapshot(cache: Path, release: str, files: dict[str, str]) -> Path:
    '''Copy latest/docs files into <release>/docs, returning that directory.
    `files` maps the name a message gives each file to its cache file name.
    A file already there with different bytes is never overwritten, since
    another group's `snapshot` may name it. Every file is checked before any
    is written.'''
    target = writable_snapshot(cache, release)
    copies = [(label, target / name, (latest_docs(cache) / name).read_bytes()) for label, name in files.items()]
    for label, held, body in copies:
        if held.is_file() and held.read_bytes() != body:
            raise SetupError(f'{label}: {held} already holds different text, which another group may have '
                             'baselined; it is never overwritten')
    target.mkdir(parents=True, exist_ok=True)
    for _, held, body in copies:
        held.write_bytes(body)
    return target
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
from state import (BASELINE, BOOTSTRAP_DATE, BOOTSTRAP_RELEASE, MANIFEST, SetupError, Source, citing_files,
                   default_cache, dump_baseline, is_iso_date, is_label, latest_docs, newest_changelog,
                   parse_baseline, parse_manifest, read_fetch, read_utf8, snapshot_docs, snapshot_text)
```

with:

```python
from state import (BASELINE, BOOTSTRAP_DATE, BOOTSTRAP_RELEASE, MANIFEST, SetupError, Source, citing_files,
                   copy_to_snapshot, default_cache, dump_baseline, is_iso_date, is_label, latest_docs,
                   newest_changelog, parse_baseline, parse_manifest, read_fetch, read_utf8, snapshot_docs,
                   snapshot_text, writable_snapshot)
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
        release = record['changelog_head']
        if release == BOOTSTRAP_RELEASE:
            raise SetupError(f'{snapshot_docs(cache, release)} is the bootstrap snapshot, which is never '
                             'written (R2.6): run check to fetch a newer release first')
        new, pages, notes = baseline.rebaseline(state, manifest, guide_text, args.group, args.refs,
                                                latest_docs(cache), release, partial(snapshot_text, cache))
        target = snapshot_docs(cache, release)
        target.mkdir(parents=True, exist_ok=True)
        copies = [(page, target / page_file(page), (latest_docs(cache) / page_file(page)).read_bytes())
                  for page in pages]
        for page, held, body in copies:  # all checked before any write
            if held.is_file() and held.read_bytes() != body:
                raise SetupError(f'{page}: {held} already holds different text, which another group may have '
                                 'baselined; it is never overwritten')
        for _, held, body in copies:
            held.write_bytes(body)
```

with:

```python
        release = record['changelog_head']
        writable_snapshot(cache, release)
        new, pages, notes = baseline.rebaseline(state, manifest, guide_text, args.group, args.refs,
                                                latest_docs(cache), release, partial(snapshot_text, cache))
        copy_to_snapshot(cache, release, {page: page_file(page) for page in pages})
```

- [x] **Step 4: Run the suite to verify it passes**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3/build/cc_guide --python 3.13 --with pytest python -m pytest -q`
Expected: all pass, +8 over the baseline. The existing `rebaseline` tests pin the refactored copy's refusals, word for word.

- [x] **Step 5: Commit**

Confirm the branch, then:

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 add build/cc_guide/check.py build/cc_guide/state.py build/cc_guide/cli.py build/cc_guide/test_check.py build/cc_guide/test_state.py
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 commit -m "feat(cc_guide): carry key hashes and read baselined block text from snapshots" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Citation placement for frontmatter kinds and on-demand Markdown, and a stricter `cite` (T6)

**Files:**
- Modify: `build/cc_guide/guide.py` (imports; three constants after `PEP723_OPEN`; `citation_slot`)
- Modify: `build/cc_guide/cli.py` (the `guide` import; `run_baseline`'s `cite` branch)
- Test: `build/cc_guide/test_citations.py`, `build/cc_guide/test_cli.py`

**Interfaces:**
- Produces:
  - `guide.FRONTMATTER_KINDS`, `guide.SKILL_MARKDOWN`, `guide.SELF_CITED`;
  - two new `citation_slot` reasons, which `file_citation` reports as `<path>:<line>: no citation can go here: <reason>`: `its kind cites as the last line of a frontmatter that opens the file` and `its skill loads it on demand, so the skill's SKILL.md citation covers it`;
  - `baseline cite` refuses a citing file the lint never reads with `cc-guide: <path>: the lint never reads it (untracked, or under specs/, runtimes/ or review/), so its stamp would never be checked`, and stamps a symlink and its target once.

These fold in three deferred items from plan 43 (`specs/deferred_items.md`): "An HTML-form citation can sit above a rules file's frontmatter", "A citation in on-demand Markdown lints clean" and "`baseline cite` stamps files `lint` never reads".

- [x] **Step 1: Write the failing tests**

**Edit** `build/cc_guide/test_citations.py` — replace:

```python
def test_a_frontmatter_citation_anywhere_else_is_misplaced():
```

with:

```python
@pytest.mark.parametrize('path', ['skills/demo/SKILL.md', 'agents/demo.md', 'commands/demo.md',
                                  'rules/demo.md', '.claude/skills/demo/SKILL.md', '.claude/agents/demo.md'])
def test_a_frontmatter_kind_never_takes_an_html_citation_above_its_frontmatter(path):
    '''An HTML-form citation on line 1 linted clean and pushed the
    frontmatter off line 1, which drops a rule's `paths:` scoping (deferred:
    An HTML-form citation can sit above a rules file's frontmatter).'''
    assert read(path, HTML, '---', 'paths: x', '---') == (
        None, [f'{path}:1: no citation can go here: its kind cites as the last line of a frontmatter that opens'
               ' the file'])


@pytest.mark.parametrize('path', ['skills/demo/references/notes.md', 'skills/demo/notes.md',
                                  'skills/demo/scripts/usage.md', '.claude/skills/demo/references/formats.md'])
def test_markdown_a_skill_loads_on_demand_carries_no_citation(path):
    '''R4.1: its SKILL.md's citation covers it (deferred: A citation in
    on-demand Markdown lints clean).'''
    assert read(path, HTML, 'Notes.') == (
        None, [f"{path}:1: no citation can go here: its skill loads it on demand, so the skill's SKILL.md citation"
               ' covers it'])


@pytest.mark.parametrize('path', ['skills/demo/README.md', 'skills/demo/INSTALL.md', 'notes/demo.md'])
def test_a_skills_readme_or_install_guide_and_other_markdown_still_cite_on_line_one(path):
    assert read(path, HTML, 'Text.') == cited(path, 1)


def test_a_frontmatter_citation_anywhere_else_is_misplaced():
```

**Edit** `build/cc_guide/test_cli.py` — replace:

```python
    assert capsys.readouterr() == ('', '')


@pytest.mark.parametrize('files, args, message', [
```

with:

```python
    assert capsys.readouterr() == ('', '')


def test_cite_refuses_a_file_the_lint_never_reads_and_stamps_a_symlink_and_its_target_once(world, capsys):
    '''A stamp on a file the lint's scan skips would never be checked
    (deferred: `baseline cite` stamps files `lint` never reads).'''
    repo, cache, _ = world
    cited(repo, {'rules/style.md': '---\npaths: x\n# cc-guide: alpha.reference @2.1.219\n---\n',
                 'specs/notes.md': '<!-- cc-guide: alpha.overview @2.1.219 -->\n'})
    (repo / '.claude').mkdir()
    (repo / '.claude' / 'style.md').symlink_to('../rules/style.md')
    write_tree(repo, {'hooks/new.sh': '#!/bin/sh\n# cc-guide: alpha.overview @2.1.219\n'})
    assert main(cache, 'baseline', 'cite', 'rules/style.md', '.claude/style.md') == 0
    assert capsys.readouterr().out == 'stamped rules/style.md @2.1.899\n'
    for name in ('hooks/new.sh', 'specs/notes.md'):
        assert main(cache, 'baseline', 'cite', 'rules/style.md', name) == 2
        assert capsys.readouterr() == ('', f'cc-guide: {name}: the lint never reads it (untracked, or under specs/,'
                                           ' runtimes/ or review/), so its stamp would never be checked\n')
    assert main(cache, 'baseline', 'cite', '../outside.sh') == 2
    assert capsys.readouterr() == ('', f'cc-guide: ../outside.sh: not a file in {repo}\n')


@pytest.mark.parametrize('files, args, message', [
```

- [x] **Step 2: Run them to verify they fail**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3/build/cc_guide --python 3.13 --with pytest python -m pytest -q -rf test_citations.py test_cli.py`
Expected: `11 failed`, every other test in the two files passing.
- The ten `test_a_frontmatter_kind_…` and `test_markdown_a_skill_loads_on_demand_…` cases fail with an `AssertionError`: today each line-1 HTML citation reads as a valid `Citation`.
- `test_cite_refuses_…` fails because `stamped rules/style.md @2.1.899` prints twice.
- **The named exception:** the three `test_a_skills_readme_or_install_guide_and_other_markdown_still_cite_on_line_one` cases pass here. They pin the behaviour the new rule must leave alone: a README, an INSTALL guide and Markdown outside a skill keep their line-1 HTML citation.

- [x] **Step 3: Teach `citation_slot` the kinds, and guard `cite`**

**Edit** `build/cc_guide/guide.py` — replace:

```python
import warnings
from typing import NamedTuple
```

with:

```python
import warnings
from pathlib import PurePosixPath
from typing import NamedTuple
```

**Edit** `build/cc_guide/guide.py` — replace:

```python
PEP723_OPEN, PEP723_CLOSE = '# /// script', '# ///'
```

with:

```python
PEP723_OPEN, PEP723_CLOSE = '# /// script', '# ///'
# R4.1's first row: these kinds cite inside a frontmatter that opens the file,
# so an HTML-form citation on line 1 would push their frontmatter down.
FRONTMATTER_KINDS = ('skills/*/SKILL.md', '.claude/skills/*/SKILL.md', 'agents/*.md', '.claude/agents/*.md',
                     'commands/*.md', 'rules/*.md')
# R4.1: the Markdown a skill loads on demand carries no citation, since its
# SKILL.md's covers it; a README or INSTALL file loads nowhere, so it cites itself.
SKILL_MARKDOWN = ('skills/*/**/*.md', '.claude/skills/*/**/*.md')
SELF_CITED = ('SKILL.md', 'README.md', 'INSTALL.md')
```

**Edit** `build/cc_guide/guide.py` — replace:

```python
    citation. Markdown with frontmatter (skills, agents, commands, rules)
    takes a YAML comment as the frontmatter's last line; other Markdown an
    HTML comment on its first line; TOML, shell and Python a `#` line before
    the first key or line of code.'''
    name = path.rsplit('/', 1)[-1]
    if name.endswith('.md'):
        if lines[0] != FRONTMATTER:
            return Slot(frozenset({0}), HTML_CITE_RE, HTML_FORM, 'the first line')
```

with:

```python
    citation. Markdown with frontmatter (skills, agents, commands, rules)
    takes a YAML comment as the frontmatter's last line, and those kinds
    always open with one; other Markdown an HTML comment on its first line,
    except the Markdown a skill loads on demand; TOML, shell and Python a `#`
    line before the first key or line of code.'''
    name = path.rsplit('/', 1)[-1]
    if name.endswith('.md'):
        kind = PurePosixPath(path)
        if name not in SELF_CITED and any(kind.full_match(g) for g in SKILL_MARKDOWN):
            return "its skill loads it on demand, so the skill's SKILL.md citation covers it"
        if lines[0] != FRONTMATTER:
            if any(kind.full_match(g) for g in FRONTMATTER_KINDS):
                return 'its kind cites as the last line of a frontmatter that opens the file'
            return Slot(frozenset({0}), HTML_CITE_RE, HTML_FORM, 'the first line')
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
from guide import by_section, read_citations, render_stamp
```

with:

```python
from guide import CITE_SHAPED_RE, by_section, read_citations, render_stamp
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
    if args.action == 'cite':
        stamped = []
        for name in dict.fromkeys(args.files):
            path = repo_path(name)
            stamped.append((path, *baseline.cite(path, tree.require(path), state)))
```

with:

```python
    if args.action == 'cite':
        readable = citing_files(tree, manifest.guide)
        stamped = []
        for path in dict.fromkeys(map(repo_path, args.files)):  # a symlink and its target are one file
            text = tree.require(path)
            if path not in readable and any(CITE_SHAPED_RE.match(line) for line in text.split('\n')):
                raise SetupError(f'{path}: the lint never reads it (untracked, or under specs/, runtimes/ or '
                                 'review/), so its stamp would never be checked')
            stamped.append((path, *baseline.cite(path, text, state)))
```

- [x] **Step 4: Run the suite and the repo lint**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3/build/cc_guide --python 3.13 --with pytest python -m pytest -q`
Expected: all pass, +22 over the baseline.

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 --python 3.13 python build/cc_guide/cli.py lint`
Expected: exit 0. No tracked file breaks the stricter placement rules.

- [x] **Step 5: Commit**

Confirm the branch, then:

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 add build/cc_guide/guide.py build/cc_guide/cli.py build/cc_guide/test_citations.py build/cc_guide/test_cli.py
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 commit -m "fix(cc_guide): place citations by kind and refuse a cite the lint never reads" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: `packets` (R6.11)

**Files:**
- Create: `build/cc_guide/packets.py`, `build/cc_guide/test_packets.py`
- Modify: `build/cc_guide/check.py` (module docstring)
- Modify: `build/cc_guide/cli.py` (module docstring; imports; `parser`; a new `run_packets`; `main`)

**Interfaces:**
- Consumes: Task 3's `Finding.key_hash`, `state.baselined_text` and `state.copy_to_snapshot`; `check.compare`, which names a missing block from its snapshot, `check.offline_docs`, `check.release_notes`, `check.releases_of` and `check.untriaged`; `lint.stale_citations`; `state.citing_files` and `state.group_terms`.
- Produces (Task 6 reads these):
  - the file-name constants `packets.INDEX` (`index.json`), `REPORT` (`report.md`), `SETTLED` (`settled.json`), `GUIDE` (`guide.md`), `BLOCKS`, `RELEASES`, `SECTIONS`; `BLOCK_KINDS`; and `RANGE` (20, the untriaged releases one triage packet takes);
  - `packets.World` and `packets.load(source: Source, cache: Path, now: datetime) -> World`, which raises `no latest fetch: run check --worktree first`;
  - `packets.section_lines(guide_text: str) -> dict[str, tuple[int, int]]`, each anchored section's first and last line;
  - `packets.triage(world, out: Path, through: str | None, size: int = RANGE) -> Path | None` (None when nothing is untriaged and no block finding exists; more than `size` untriaged releases after the newest `checked` release, without `through`, is a `SetupError` naming the first range's `--through`);
  - `packets.verify(world, out: Path, ids: list[str], settled: Path | None) -> list[Path]` (empty `ids` takes the settled triage's `verify` list);
  - `packets.audit(world, out: Path, group: str) -> Path`;
  - `packets.files(world, out: Path, paths: list[str]) -> list[Path]`;
  - `packets.checkout_of(path: Path) -> Path | None`, the nearest folder holding a `.git`; every writer refuses an `out` that resolves inside a checkout: `<out>: inside the checkout <root>; packets hold docs text, so they live outside every checkout`;
  - `index.json`, per mode: every packet has `mode`, `inputs`, `generated_at`, `head` and `quotes`;
    - triage adds `newest`, `next_through`, `groups`, `blocks` (item, group, kind, ref, page, key_hash, candidates, and `lines`, the 1-based `[first, last]` spans of `blocks.md` holding its text), `releases` (label, date, pending, hits, bullets with item, hints and text), `held` and `owner`; its `quotes` are `guide` and `source`;
    - verify adds `group`, `sections`, `lines`, `checked` (each section's checked release), `docs`, `advance_to`, `cleared`, `held` and `blocks`; its `quotes` are `guide` (`guide.md`), `changelog` (`changelog.md`) and `docs` (the snapshot directory);
    - audit adds `group`, `sections`, `lines`, `docs`, `releases`, `held` and `blocks`, with verify's `quotes`;
    - files adds `file`, `copy`, `stamp`, `sections`, `lines` and `changed`.

- [x] **Step 1: Write the failing tests**

**Create** `build/cc_guide/test_packets.py`:

`````python
'''Tests for packets.py and `cli.py packets`: what each packet holds, the
index settle reads back, the triage split by release range, and the
snapshot copy verify and audit make (drift spec R6.11, R8.4-R8.7).'''
import json
from datetime import date, datetime, timezone

import pytest

import blocks
import cli
import packets
import state
from cc_fixtures import (DOCS, FIXTURE_RELEASE, GUIDE_PATH, MANIFEST_TOML, docs_dir, fixture_repo,  # noqa: F401
                         fixture_state, guide_text, isolated_home, prime_cache, write_tree)

NOW = datetime(2026, 10, 4, 12, 0, tzinfo=timezone.utc)
ALL = ['alpha.overview', 'alpha.reference', 'beta.overview', 'beta.reference']
# Two tracked citing files: gate.sh's stamp is below alpha.overview's changed
# (2.1.900), so it is stale; fresh.md is not.
CITERS = {'hooks/gate.sh': '#!/bin/sh\n' + '#' + ' cc-guide: alpha.overview @2.1.899\nexit 0\n',
          'notes/fresh.md': '<!-- cc-guide: beta.overview @2.1.900 -->\nNotes.\n'}


@pytest.fixture
def world(tmp_path, docs_dir):
    '''A committed fixture repo with two citing files, and a cache holding
    the baseline's 2.1.900 snapshot and a latest fetch at 2.1.902.'''
    repo = fixture_repo(tmp_path / 'repo', {GUIDE_PATH: guide_text(), state.MANIFEST: MANIFEST_TOML,
                                            state.BASELINE: state.dump_baseline(fixture_state(docs_dir)), **CITERS})
    cache = tmp_path / 'cache'
    write_tree(state.snapshot_docs(cache, FIXTURE_RELEASE), DOCS)
    prime_cache(cache, docs_dir)
    return repo, cache


def load(world):
    repo, cache = world
    return packets.load(state.Source(repo), cache, NOW)


def latest(world, files):
    write_tree(state.latest_docs(world[1]), files)


def index(folder):
    return json.loads((folder / packets.INDEX).read_text())


def test_a_triage_packet_holds_the_guide_and_every_bullet_of_each_untriaged_release(world, tmp_path):
    out = packets.triage(load(world), tmp_path / 'p', None)
    assert sorted(p.name for p in out.iterdir()) == ['blocks.md', 'guide.md', 'index.json', 'releases.md']
    assert (out / 'guide.md').read_text() == guide_text()
    i = index(out)
    assert {k: i[k] for k in ('mode', 'inputs', 'head', 'newest', 'blocks', 'held', 'owner')} == {
        'mode': 'triage', 'inputs': 'the working tree', 'head': '2.1.902', 'newest': '2.1.902',
        'blocks': [], 'held': [], 'owner': []}
    assert i['quotes'] == {'guide': ['guide.md'], 'source': ['blocks.md', 'releases.md']}
    assert i['groups'] == {'alpha': ['alpha.overview', 'alpha.reference'], 'beta': ['beta.overview', 'beta.reference']}
    assert i['releases'] == [
        {'label': '2.1.901', 'date': '2026-09-20', 'pending': ALL, 'hits': ['alpha.reference'],
         'bullets': [{'item': '2.1.901#1', 'hints': ['alpha.reference'],
                      'text': 'Added `ALPHA_ENV` to the alpha tools'}]},
        {'label': '2.1.902', 'date': '2026-10-01', 'pending': ALL, 'hits': ['beta.overview'],
         'bullets': [{'item': '2.1.902#1', 'hints': ['beta.overview'], 'text': 'Changed how `BETA_ENV` is read'},
                     {'item': '2.1.902#2', 'hints': [], 'text': 'Fixed a crash in the fixture tool'}]}]
    assert (out / 'releases.md').read_text().split('\n') == [
        '# Untriaged releases', '',
        '## 2.1.901 · 2026-09-20', '',
        'Untriaged for 4 section(s); term hits, as hints only: alpha.reference.', '',
        '- 2.1.901#1 · hints: alpha.reference · Added `ALPHA_ENV` to the alpha tools', '',
        '## 2.1.902 · 2026-10-01', '',
        'Untriaged for 4 section(s); term hits, as hints only: beta.overview.', '',
        '- 2.1.902#1 · hints: beta.overview · Changed how `BETA_ENV` is read',
        '- 2.1.902#2 · hints: none · Fixed a crash in the fixture tool', '', '']
    assert (out / 'blocks.md').read_text() == '# Block findings\n\nNone.\n\n'


def test_a_changed_block_shows_its_text_and_a_diff_against_its_snapshot(world, tmp_path):
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = packets.triage(load(world), tmp_path / 'p', None)
    # lines: blocks.md's lines that hold the block's own text, the only lines
    # its source quote may come from.
    assert index(out)['blocks'] == [{'item': 'B1', 'group': 'alpha', 'kind': 'changed', 'ref': 'tools › Tools',
                                     'page': 'tools', 'key_hash': blocks.key_hash('Tools'),
                                     'candidates': ['alpha.overview'], 'lines': [[9, 10], [15, 20]]}]
    assert (out / 'blocks.md').read_text().split('\n') == [
        '# Block findings', '',
        '## B1 · changed · [alpha] tools › Tools', '',
        'Candidate sections: alpha.overview', '',
        'Current text:', '```', '# Tools', 'The `ALPHA_TOOL` runs alpha batches.', '```', '',
        'Diff against the 2.1.900 snapshot:', '```',
        '--- the 2.1.900 snapshot', '+++ now', '@@ -1,2 +1,2 @@', ' # Tools',
        '-The `ALPHA_TOOL` runs alpha jobs.', '+The `ALPHA_TOOL` runs alpha batches.', '```', '', '']


def test_a_missing_block_shows_its_baselined_text_read_by_key_hash(world, tmp_path):
    '''A block gone from the page has no current text, so the packet reads
    its baselined text from the page's snapshot by key hash, the lookup
    check uses to name it (deferred: Carry each missing block's key hash).'''
    latest(world, {'events.md': DOCS['events.md'].replace('## Payload', '## Body')})
    out = packets.triage(load(world), tmp_path / 'p', None)
    payload = blocks.key_hash('Events › Payload')
    assert [(b['kind'], b['ref'], b['key_hash']) for b in index(out)['blocks']] == [
        ('missing', 'events › Events › Payload', payload),
        ('new', 'events › Events › Body', blocks.key_hash('Events › Body'))]
    text = (out / 'blocks.md').read_text()
    assert ('Baselined text, from the 2.1.900 snapshot (the block has left the page):\n```\n'
            '## Payload\nThe payload carries `BETA_ENV`.\n```\n') in text
    assert 'Current text:\n```\n## Body\nThe payload carries `BETA_ENV`.\n```\n' in text


def test_without_its_snapshot_a_missing_block_goes_by_key_hash_and_says_so(world, tmp_path):
    latest(world, {'events.md': DOCS['events.md'].replace('## Payload', '## Body')})
    (state.snapshot_docs(world[1], FIXTURE_RELEASE) / 'events.md').unlink()
    out = packets.triage(load(world), tmp_path / 'p', None)
    payload = blocks.key_hash('Events › Payload')
    assert index(out)['blocks'][0]['ref'] == f'events › {payload}'
    assert f'## B1 · missing · [beta] events › {payload}\n\nCandidate sections: beta.overview, beta.reference\n\n' \
           'No cached snapshot holds its baselined text.\n' in (out / 'blocks.md').read_text()


def test_a_fence_in_a_block_gets_a_longer_outer_fence():
    assert packets.fenced('a\n```json\n{}\n```') == ['````', 'a', '```json', '{}', '```', '````']
    assert packets.fenced('plain') == ['```', 'plain', '```']


def test_every_release_range_carries_the_block_findings(world, tmp_path):
    '''R8.4's split: block findings ride in the range being triaged, the
    oldest first, so they are settled there against the current docs.'''
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    early = index(packets.triage(load(world), tmp_path / 'early', '2.1.901'))
    assert (early['newest'], [b['item'] for b in early['blocks']], early['held']) == ('2.1.901', ['B1'], [])
    assert [r['label'] for r in early['releases']] == ['2.1.901']
    with pytest.raises(state.SetupError) as err:
        packets.triage(load(world), tmp_path / 'bad', '2.1.950')
    assert str(err.value) == '--through 2.1.950: not an untriaged release (2.1.901, 2.1.902)'


def test_more_releases_than_a_range_name_the_first_ranges_through_and_each_range_the_next(world, tmp_path):
    '''The tool names the ranges, so a session never has to: the first
    range ends at the size-th oldest untriaged release, and each range's
    index names the next, the size-th untriaged release after its own.'''
    with pytest.raises(state.SetupError) as err:
        packets.triage(load(world), tmp_path / 'p', None, size=1)
    assert str(err.value) == ('2 untriaged releases after 2.1.900: take them in ranges of 1, the first with '
                              '--through 2.1.901, or all at once with --through 2.1.902')
    assert not (tmp_path / 'p').exists()
    assert index(packets.triage(load(world), tmp_path / 'a', '2.1.901', size=1))['next_through'] == '2.1.902'
    assert index(packets.triage(load(world), tmp_path / 'b', '2.1.902', size=1))['next_through'] is None


def test_a_range_counts_from_the_newest_checked_release_so_a_deferral_never_repeats_it(world, tmp_path):
    '''A section deferred in an earlier range keeps its old `checked`, so a
    later session counts the range from the newest release any section is
    checked through: the deferred section's earlier releases ride along
    without counting, and the first range is never named again.'''
    repo, _ = world
    s = state.parse_baseline((repo / state.BASELINE).read_text())
    for sid in ('alpha.overview', 'alpha.reference'):
        s['sections'][sid]['checked'] = {'release': '2.1.901', 'date': '2026-10-04'}
    (repo / state.BASELINE).write_text(state.dump_baseline(s))
    i = index(packets.triage(load(world), tmp_path / 'p', None, size=1))
    assert ([r['label'] for r in i['releases']], i['newest'], i['next_through']) == (
        ['2.1.901', '2.1.902'], '2.1.902', None)
    assert i['releases'][0]['pending'] == ['beta.overview', 'beta.reference']


def test_a_missing_page_is_an_owner_item_whose_sections_are_held(world, tmp_path):
    (state.latest_docs(world[1]) / 'events.md').unlink()
    i = index(packets.triage(load(world), tmp_path / 'p', None))
    assert (i['owner'], i['held']) == (['missing page events in group beta: drop or remap it in manifest.toml'],
                                       ['beta.overview', 'beta.reference'])


def test_nothing_to_triage_writes_no_packet(world, tmp_path):
    repo, _ = world
    s = state.parse_baseline((repo / state.BASELINE).read_text())
    for sid in s['sections'].values():
        sid['checked'] = {'release': '2.1.902', 'date': '2026-10-04'}
    (repo / state.BASELINE).write_text(state.dump_baseline(s))
    assert packets.triage(load(world), tmp_path / 'p', None) is None
    assert not (tmp_path / 'p').exists()


def test_a_packet_never_writes_over_an_earlier_one(world, tmp_path):
    write_tree(tmp_path / 'p', {'report.md': 'old'})
    with pytest.raises(state.SetupError) as err:
        packets.triage(load(world), tmp_path / 'p', None)
    assert str(err.value) == f"{tmp_path / 'p'}: not an empty directory; packets never write over an earlier packet"


def test_packets_need_a_latest_fetch(world, tmp_path):
    state.fetch_record(world[1]).unlink()
    with pytest.raises(state.SetupError) as err:
        load(world)
    assert str(err.value) == 'no latest fetch: run check --worktree first'


def test_the_cli_writes_a_triage_packet_under_the_cache_by_default(world, monkeypatch, capsys):
    repo, cache = world
    monkeypatch.setattr(cli, 'REPO', repo)
    assert cli.main(['--cache', str(cache), 'packets', '--triage'], now=NOW) == 0
    out = cache / 'packets' / '20261004T120000-triage'
    assert capsys.readouterr() == (f'wrote triage packet {out}\n', '')
    assert index(out)['mode'] == 'triage'
    assert cli.main(['--cache', str(cache), 'packets', '--audit', '--through', '2.1.901'], now=NOW) == 2
    assert capsys.readouterr() == ('', 'cc-guide: --through goes with --triage\n')


def test_a_verify_packet_per_group_copies_the_groups_pages_to_the_head_snapshot(world, tmp_path):
    '''R8.5: one verifier per group, which greps the head release's snapshot,
    copied from latest/.'''
    made = packets.verify(load(world), tmp_path / 'v', ['beta.reference', 'alpha.overview'], None)
    assert made == [tmp_path / 'v' / 'alpha', tmp_path / 'v' / 'beta']
    head = state.snapshot_docs(world[1], '2.1.902')
    assert sorted(p.name for p in head.iterdir()) == ['env-vars.md', 'events.md', 'platform_pricing.md', 'tools.md']
    assert (head / 'tools.md').read_text() == DOCS['tools.md']
    i = index(made[0])
    # checked: each section's checked release, so settle never advances one
    # past the triage's target backwards (second review, finding 6).
    assert {k: i[k] for k in ('mode', 'group', 'sections', 'lines', 'checked', 'docs', 'advance_to', 'cleared',
                              'held', 'blocks')} == {
        'mode': 'verify', 'group': 'alpha', 'sections': ['alpha.overview'], 'lines': {'alpha.overview': [11, 15]},
        'checked': {'alpha.overview': '2.1.900'}, 'docs': str(head), 'advance_to': None, 'cleared': [], 'held': [],
        'blocks': []}
    # A doc quote comes from the snapshot's pages or the packet's changelog,
    # never from the report, the guide copy or the index.
    assert i['quotes'] == {'guide': ['guide.md'], 'changelog': ['changelog.md'], 'docs': [str(head)]}
    assert sorted(p.name for p in made[0].iterdir()) == ['blocks.md', 'changelog.md', 'guide.md', 'index.json',
                                                         'sections.md']
    assert (made[1] / 'sections.md').read_text() == (
        '# Sections\n\n## beta.reference · guide lines 37-41\n\nNo triage row sent it here.\n\n')


def test_a_verify_packet_from_a_settled_triage_carries_its_rows_and_bookkeeping(world, tmp_path):
    write_tree(tmp_path / 't', {packets.SETTLED: json.dumps(
        {'mode': 'triage', 'advance_to': '2.1.902', 'verify': ['alpha.overview'], 'cleared': ['alpha.reference'],
         'held': ['alpha.overview'], 'rows': {'alpha.overview': ['B1: TOUCHES']}})})
    made = packets.verify(load(world), tmp_path / 'v', [], tmp_path / 't' / packets.SETTLED)
    i = index(made[0])
    assert (i['sections'], i['advance_to'], i['cleared'], i['held']) == (
        ['alpha.overview'], '2.1.902', ['alpha.reference'], ['alpha.overview'])
    assert (made[0] / 'sections.md').read_text() == (
        '# Sections\n\n## alpha.overview · guide lines 11-15\n\nTriage rows that sent it here:\n- B1: TOUCHES\n\n')


def test_the_snapshot_copy_never_overwrites_other_text_or_the_bootstrap(world, tmp_path, docs_dir):
    head = state.snapshot_docs(world[1], '2.1.902')
    write_tree(head, {'tools.md': DOCS['tools.md']})  # the same bytes: copied again
    packets.verify(load(world), tmp_path / 'v', ['alpha.overview'], None)
    write_tree(head, {'tools.md': 'other text\n'})
    with pytest.raises(state.SetupError) as err:
        packets.verify(load(world), tmp_path / 'w', ['alpha.overview'], None)
    assert str(err.value) == (f"tools: {head / 'tools.md'} already holds different text, which another group may "
                              'have baselined; it is never overwritten')
    assert not (tmp_path / 'w').exists()
    prime_cache(world[1], docs_dir, head='2.1.288')
    with pytest.raises(state.SetupError) as err:
        packets.verify(load(world), tmp_path / 'x', ['alpha.overview'], None)
    assert str(err.value) == (f"{state.snapshot_docs(world[1], '2.1.288')} is the bootstrap snapshot, which is never "
                              'written (R2.6): run check to fetch a newer release first')


def test_verify_refuses_an_unknown_section_and_a_missing_or_foreign_settled_file(world, tmp_path):
    with pytest.raises(state.SetupError) as err:
        packets.verify(load(world), tmp_path / 'v', ['gamma.overview'], None)
    assert str(err.value) == 'unknown section IDs: gamma.overview'
    with pytest.raises(state.SetupError) as err:
        packets.verify(load(world), tmp_path / 'v', ['alpha.overview'], tmp_path / 't' / packets.SETTLED)
    assert str(err.value) == f"{tmp_path / 't' / packets.SETTLED}: not found; run settle on the triage packet first"
    write_tree(tmp_path / 't', {packets.SETTLED: json.dumps({'mode': 'verify'})})
    with pytest.raises(state.SetupError) as err:
        packets.verify(load(world), tmp_path / 'v', ['alpha.overview'], tmp_path / 't' / packets.SETTLED)
    assert str(err.value) == f"{tmp_path / 't' / packets.SETTLED}: not a settled triage"


def test_verify_and_audit_hold_a_missing_pages_sections(world, tmp_path):
    (state.latest_docs(world[1]) / 'events.md').unlink()
    assert index(packets.audit(load(world), tmp_path / 'a', 'beta'))['held'] == ['beta.overview', 'beta.reference']
    made = packets.verify(load(world), tmp_path / 'v', ['beta.reference', 'alpha.overview'], None)
    assert [index(m)['held'] for m in made] == [[], ['beta.overview', 'beta.reference']]


def test_verify_needs_section_ids_or_a_triage_that_sent_some(world, tmp_path):
    with pytest.raises(state.SetupError) as err:
        packets.verify(load(world), tmp_path / 'v', [], None)
    assert str(err.value) == '--verify needs section IDs, or --from a settled triage'
    write_tree(tmp_path / 't', {packets.SETTLED: json.dumps({'mode': 'triage', 'verify': []})})
    with pytest.raises(state.SetupError) as err:
        packets.verify(load(world), tmp_path / 'v', [], tmp_path / 't' / packets.SETTLED)
    assert str(err.value) == f"{tmp_path / 't' / packets.SETTLED}: its triage sent no section to verify"


def test_a_packet_never_lands_inside_a_checkout(world, tmp_path):
    '''Review finding 10, and the second review's finding 4: packets hold
    docs text, so a destination inside any checkout is refused (spec
    Decision 10), through a symlink too: the repo's own, the main checkout
    a worktree sits in, and a sibling worktree, whose `.git` is a file.'''
    repo, _ = world
    (tmp_path / 'link').symlink_to(repo)
    for out in (repo / 'packets', tmp_path / 'link' / 'packets'):
        with pytest.raises(state.SetupError) as err:
            packets.triage(load(world), out, None)
        assert str(err.value) == (f'{out}: inside the checkout {repo.resolve()}; packets hold docs text, so they '
                                  'live outside every checkout')
    assert not (repo / 'packets').exists()
    main = tmp_path / 'main'
    (main / '.git').mkdir(parents=True)
    worktree, sibling = main / 'wt' / 'one', main / 'wt' / 'two'
    for root in (worktree, sibling):
        root.mkdir(parents=True)
        (root / '.git').write_text(f'gitdir: {main}/.git/worktrees/{root.name}\n')
    for out, checkout in ((main / 'packets', main), (sibling / 'packets', sibling)):
        with pytest.raises(state.SetupError) as err:
            packets.new_dir(out, worktree)
        assert str(err.value) == (f'{out}: inside the checkout {checkout.resolve()}; packets hold docs text, so '
                                  'they live outside every checkout')
        assert not out.exists()
    assert packets.new_dir(tmp_path / 'cache' / 'packets', worktree).is_dir()


def test_an_audit_packet_holds_every_section_its_untriaged_releases_and_its_blocks(world, tmp_path):
    latest(world, {'events.md': DOCS['events.md'].replace('on beta', 'on every beta')})
    out = packets.audit(load(world), tmp_path / 'a', 'beta')
    i = index(out)
    assert (i['mode'], i['group'], i['sections']) == ('audit', 'beta', ['beta.overview', 'beta.reference'])
    assert [(r['label'], r['pending'], r['hits']) for r in i['releases']] == [
        ('2.1.901', ['beta.overview', 'beta.reference'], []),
        ('2.1.902', ['beta.overview', 'beta.reference'], ['beta.overview'])]
    assert [b['ref'] for b in i['blocks']] == ['events › Events']
    assert sorted(p.name for p in out.iterdir()) == ['blocks.md', 'changelog.md', 'guide.md', 'index.json',
                                                     'releases.md', 'sections.md']
    with pytest.raises(state.SetupError) as err:
        packets.audit(load(world), tmp_path / 'b', 'gamma')
    assert str(err.value) == 'unknown group gamma'


def test_a_files_packet_per_stale_file_marks_the_sections_changed_since_its_stamp(world, tmp_path):
    made = packets.files(load(world), tmp_path / 'f', [])
    assert made == [tmp_path / 'f' / 'hooks__gate.sh']
    i = index(made[0])
    assert {k: i[k] for k in ('mode', 'file', 'copy', 'stamp', 'sections', 'lines', 'changed', 'quotes')} == {
        'mode': 'files', 'file': 'hooks/gate.sh', 'copy': 'cited_gate.sh', 'stamp': '2.1.899',
        'sections': ['alpha.overview'], 'lines': {'alpha.overview': [11, 15]}, 'changed': ['alpha.overview'],
        'quotes': {'guide': ['guide.md']}}
    assert (made[0] / 'cited_gate.sh').read_text() == CITERS['hooks/gate.sh']
    assert (made[0] / 'sections.md').read_text().split('\n')[:9] == [
        '# Sections', '', '## alpha.overview · guide lines 11-15', '',
        'Changed after @2.1.899: now @2.1.900.', '', '```', '## 1. Alpha', '']


def test_files_takes_named_citing_files_and_refuses_any_the_lint_never_reads(world, tmp_path):
    fresh = packets.files(load(world), tmp_path / 'f', ['notes/fresh.md'])
    assert index(fresh[0])['changed'] == []
    assert 'Unchanged since @2.1.900.' in (fresh[0] / 'sections.md').read_text()
    write_tree(world[0], {'specs/x.md': '<!-- cc-guide: beta.overview @2.1.900 -->\n'})
    with pytest.raises(state.SetupError) as err:
        packets.files(load(world), tmp_path / 'g', ['specs/x.md', 'hooks/gate.sh'])
    assert str(err.value) == 'not a citing file the lint reads: specs/x.md'


def test_files_with_no_stale_citation_and_no_paths_is_an_error(world, tmp_path):
    repo, _ = world
    write_tree(repo, {'hooks/gate.sh': CITERS['hooks/gate.sh'].replace('@2.1.899', '@2.1.900')})
    with pytest.raises(state.SetupError) as err:
        packets.files(load(world), tmp_path / 'f', [])
    assert str(err.value) == 'no stale citation: name the files to review'


def test_the_cli_writes_verify_audit_and_files_packets(world, monkeypatch, capsys, tmp_path):
    repo, cache = world
    monkeypatch.setattr(cli, 'REPO', repo)
    base = ['--cache', str(cache), 'packets']
    assert cli.main([*base, '--verify', 'beta.overview', '--out', str(tmp_path / 'v')], now=NOW) == 0
    assert cli.main([*base, '--audit', '--out', str(tmp_path / 'a')], now=NOW, today=NOW.date()) == 0
    assert cli.main([*base, '--files', str(repo / 'hooks/gate.sh'), '--out', str(tmp_path / 'f')], now=NOW) == 0
    assert capsys.readouterr() == (f"wrote verify packet {tmp_path / 'v' / 'beta'}\n"
                                   f"wrote audit packet {tmp_path / 'a'}\n"
                                   f"wrote files packet {tmp_path / 'f' / 'hooks__gate.sh'}\n", '')
    assert index(tmp_path / 'a')['group'] == 'alpha'  # the due group, oldest audited in manifest order
    assert cli.main([*base, '--files', '--from', str(tmp_path)], now=NOW) == 2
    assert capsys.readouterr() == ('', 'cc-guide: --from goes with --verify\n')
    # Due from 2026-10-02, 30 days after the fixture's audits: before then,
    # only a named group is audited.
    early = date(2026, 9, 30)
    assert cli.main([*base, '--audit', '--out', str(tmp_path / 'b')], now=NOW, today=early) == 2
    assert capsys.readouterr() == ('', 'cc-guide: no audit is due before 2026-10-02: name a group to audit one '
                                       'anyway\n')
    assert cli.main([*base, '--audit', 'beta', '--out', str(tmp_path / 'b')], now=NOW, today=early) == 0
    write_tree(tmp_path / 't', {packets.SETTLED: json.dumps({'mode': 'triage', 'verify': ['beta.overview']})})
    assert cli.main([*base, '--verify', '--from', str(tmp_path / 't'), '--out', str(tmp_path / 'w')], now=NOW) == 0
    assert capsys.readouterr()[0].split('\n')[-2] == f"wrote verify packet {tmp_path / 'w' / 'beta'}"
`````

- [x] **Step 2: Run them to verify they fail**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3/build/cc_guide --python 3.13 --with pytest python -m pytest -q test_packets.py`
Expected: `1 error` during collection, `ModuleNotFoundError: No module named 'packets'`.

- [x] **Step 3: Write `packets.py`**

> Deviation: the final review's fix wave (owner, 2026-10-13; f775b22) changed this code: `index.json` records the resolved `cache`; `--verify` and `--audit` check `--out` (`check_out`) before writing the head snapshot; `files` refuses a cited ID in neither the baseline nor the guide, and `read_settled` a malformed `settled.json`, with a `SetupError`; `--verify --from` refuses an ID the triage cleared. `test_state.py` gained the all-checked-before-any-write test for `copy_to_snapshot`.

**Create** `build/cc_guide/packets.py`:

```python
'''`packets`: the files /cc-guide hands its verifier (drift spec R6.11, R8.2).

A packet is a directory. Its index.json names the mode, the items the
verifier answers for and where each kind of quote is checked; `settle`
reads it back beside the verifier's report.md. Its Markdown files hold what
the verifier reads. The guide is copied whole, so a line number in a packet
is a line number in the guide. Packets hold docs text, so they live under
the cache, never in a checkout.

The inputs are check --worktree's: the working tree, and the docs and
snapshots check left in the cache. Packets never fetch: run check first.
'''
import difflib
import json
import re
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import NamedTuple

from blocks import page_blocks
from check import Docs, Finding, compare, offline_docs, release_notes, releases_of, untriaged
from docs import CHANGELOG, Release, page_file, version_key
from guide import read_citations, sections
from lint import stale_citations
from state import (BASELINE, MANIFEST, Manifest, SetupError, Source, baselined_text, citing_files, copy_to_snapshot,
                   group_terms, latest_docs, parse_baseline, parse_manifest, read_fetch, snapshot_text)

INDEX = 'index.json'
REPORT = 'report.md'
SETTLED = 'settled.json'
GUIDE = 'guide.md'
BLOCKS = 'blocks.md'
RELEASES = 'releases.md'
SECTIONS = 'sections.md'
BLOCK_KINDS = ('changed', 'missing', 'new')
RANGE = 20  # the untriaged releases one triage packet takes, when more are untriaged
BACKTICK_RUN_RE = re.compile(r'`+')


class World(NamedTuple):
    '''One run's inputs, read once.'''
    source: Source
    cache: Path
    manifest: Manifest
    state: dict
    guide: str
    terms: dict
    docs: Docs
    releases: list[Release]
    findings: list[Finding]
    head: str  # the latest fetch's changelog head
    now: datetime


def load(source: Source, cache: Path, now: datetime) -> World:
    '''check --worktree's inputs, with the docs read offline from latest/.'''
    manifest = parse_manifest(source.require(MANIFEST))
    state = parse_baseline(source.require(BASELINE))
    guide = source.require(manifest.guide)
    record = read_fetch(cache)
    if record is None:
        raise SetupError('no latest fetch: run check --worktree first')
    docs = offline_docs(manifest, latest_docs(cache))
    terms = group_terms(manifest, guide)
    findings, _ = compare(manifest, state, terms, docs, partial(snapshot_text, cache))
    releases = releases_of(docs.changelog, str(latest_docs(cache) / CHANGELOG))
    return World(source, cache, manifest, state, guide, terms, docs, releases, findings, record['changelog_head'], now)


def section_lines(guide_text: str) -> dict[str, tuple[int, int]]:
    '''Each anchored section's 1-based heading line and last line.'''
    found = sections(guide_text)
    ends = [s.line - 1 for s in found[1:]] + [len(guide_text.split('\n'))]
    return {s.id: (s.line, end) for s, end in zip(found, ends) if s.id}


def fenced(text: str) -> list[str]:
    '''text inside a backtick fence longer than any backtick run it holds.'''
    longest = max((len(m.group()) for m in BACKTICK_RUN_RE.finditer(text)), default=0)
    fence = '`' * max(3, longest + 1)
    return [fence, *text.split('\n'), fence]


def checkout_of(path: Path) -> Path | None:
    '''The checkout holding path: the nearest folder, path itself included,
    with a `.git`, a directory or a linked worktree's file.'''
    return next((p for p in (path, *path.parents) if (p / '.git').exists()), None)


def new_dir(out: Path, repo: Path) -> Path:
    '''An empty directory for a run, outside every checkout (spec Decision
    10), since packets hold docs text: the repo's, the main checkout a
    worktree sits in, and any other. An existing one must be empty, so a
    report from an earlier run is never settled against a new packet.'''
    where = out.resolve()
    inside = checkout_of(where) or (repo.resolve() if where.is_relative_to(repo.resolve()) else None)
    if inside is not None:
        raise SetupError(f'{out}: inside the checkout {inside}; packets hold docs text, so they live outside '
                         'every checkout')
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise SetupError(f'{out}: not an empty directory; packets never write over an earlier packet')
    out.mkdir(parents=True, exist_ok=True)
    return out


def write_packet(world: World, out: Path, index: dict, files: dict[str, str | list[str]]) -> Path:
    new_dir(out, world.source.repo)
    for name, body in files.items():
        (out / name).write_text(body if isinstance(body, str) else '\n'.join(body) + '\n', encoding='utf-8')
    (out / INDEX).write_text(json.dumps(index, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    return out


def header(world: World, mode: str) -> dict:
    return {'mode': mode, 'inputs': world.source.label, 'generated_at': world.now.isoformat(timespec='seconds'),
            'head': world.head}


def page_holds(world: World) -> set[str]:
    '''The sections a missing page holds: it needs a manifest.toml edit.'''
    return {sid for f in world.findings if f.kind == 'missing-page' for sid in f.candidates}


def block_item(world: World, item: str, f: Finding) -> tuple[dict, list[str]]:
    '''One block finding's index entry and its blocks.md lines: its current
    text, and its baselined text read from the page's snapshot by key hash,
    as a diff for a changed block and whole for a missing one. The entry's
    `lines` are the item's lines that hold that text, the only ones its
    source quote may come from.'''
    text = world.docs.pages.get(f.page)
    now = None if text is None or f.kind == 'missing' else page_blocks(text).get(f.key)
    then = None if f.kind == 'new' else baselined_text(world.state, f.group, partial(snapshot_text, world.cache))(
        f.page, f.key_hash)
    release = world.state['groups'].get(f.group, {}).get('snapshot', {}).get(f.page)
    lines = [f'## {item} · {f.kind} · [{f.group}] {f.ref()}', '',
             f"Candidate sections: {', '.join(f.candidates)}", '']
    spans: list[list[int]] = []

    def show(label: str, body: str) -> None:
        lines.append(label)
        block = fenced(body)
        spans.append([len(lines) + 2, len(lines) + len(block) - 1])  # inside the fence
        lines.extend([*block, ''])

    if now is not None:
        show('Current text:', now)
    if f.kind == 'changed' and then is not None and now is not None:
        diff = difflib.unified_diff(then.split('\n'), now.split('\n'), f'the {release} snapshot', 'now', lineterm='')
        show(f'Diff against the {release} snapshot:', '\n'.join(diff))
    elif f.kind == 'missing' and then is not None:
        show(f'Baselined text, from the {release} snapshot (the block has left the page):', then)
    elif f.kind != 'new':
        lines += ['No cached snapshot holds its baselined text.', '']
    entry = {'item': item, 'group': f.group, 'kind': f.kind, 'ref': f.ref(), 'page': f.page,
             'key_hash': f.key_hash, 'candidates': f.candidates, 'lines': spans}
    return entry, lines


def block_items(world: World, found: list[Finding]) -> tuple[list[dict], list[str]]:
    '''The index entries and blocks.md for block findings, numbered B1, B2,
    ..., each entry's `lines` counted in blocks.md.'''
    entries, lines = [], ['# Block findings', '']
    for n, f in enumerate(found, start=1):
        entry, body = block_item(world, f'B{n}', f)
        entry['lines'] = [[first + len(lines), last + len(lines)] for first, last in entry['lines']]
        entries.append(entry)
        lines += body
    return entries, lines + ([] if found else ['None.', ''])


def release_items(world: World, labels: list[str], pending: dict[str, list[str]]) -> tuple[list[dict], list[str]]:
    '''The index entries and releases.md for untriaged releases: every bullet,
    numbered <release>#1, #2, ..., with the sections whose terms it contains
    as hints only (R6.6). Hints and hits name only the sections the release
    is untriaged for.'''
    notes = release_notes(world.releases, set(labels), world.terms)
    entries, lines = [], ['# Untriaged releases', '']
    for label in labels:
        mine = [sid for sid, ls in pending.items() if label in ls]
        bullets = [{'item': f'{label}#{n}', 'hints': [h for h in b['hints'] if h in mine], 'text': b['text']}
                   for n, b in enumerate(notes[label]['bullets'], start=1)]
        hits = [sid for sid in mine if any(sid in b['hints'] for b in bullets)]
        entries.append({'label': label, 'date': notes[label]['date'], 'pending': mine, 'hits': hits,
                        'bullets': bullets})
        lines += [f"## {label} · {notes[label]['date']}", '',
                  f"Untriaged for {len(mine)} section(s); term hits, as hints only: {', '.join(hits) or 'none'}.", '']
        lines += [f"- {b['item']} · hints: {', '.join(b['hints']) or 'none'} · {b['text']}" for b in bullets] + ['']
    return entries, lines + ([] if labels else ['None.', ''])


def triage(world: World, out: Path, through: str | None, size: int = RANGE) -> Path | None:
    '''R8.4 step 1's packet: the guide, each changed, missing or new block,
    and every bullet of each untriaged release. With `through`, only the
    untriaged releases up to that one. A range counts the releases after the
    newest one any section is checked through, so a section deferred in an
    earlier range shows its earlier releases without their counting. More
    than `size` of them need `through`: the error names the first range's,
    and each range's index names the next one's, the size-th untriaged
    release after its own.
    Block findings belong to no release, so they ride in every range, the
    oldest first, and are settled there against the current docs. A missing
    page needs a manifest edit, so it is an owner item whose sections are
    held. None when nothing is due.'''
    pending = untriaged(world.state, world.releases)
    every = sorted({label for ls in pending.values() for label in ls}, key=version_key)
    if through is not None and through not in every:
        raise SetupError(f"--through {through}: not an untriaged release ({', '.join(every) or 'none'})")
    checked = max((s['checked']['release'] for s in world.state['sections'].values()), key=version_key)
    fresh = [label for label in every if version_key(label) > version_key(checked)]
    if through is None and len(fresh) > size:
        raise SetupError(f'{len(fresh)} untriaged releases after {checked}: take them in ranges of {size}, the '
                         f'first with --through {fresh[size - 1]}, or all at once with --through {every[-1]}')
    labels = every[:every.index(through) + 1] if through is not None else every
    after = every[len(labels):]
    pages = [f for f in world.findings if f.kind == 'missing-page']
    found = [f for f in world.findings if f.kind in BLOCK_KINDS]
    held = page_holds(world)
    if not labels and not found and not pages:
        return None
    rel_entries, rel_lines = release_items(world, labels, pending)
    block_entries, block_lines = block_items(world, found)
    order = list(world.state['sections'])
    index = header(world, 'triage') | {
        'newest': labels[-1] if labels else None,
        'next_through': after[min(size, len(after)) - 1] if after else None,
        'quotes': {'guide': [GUIDE], 'source': [BLOCKS, RELEASES]},
        'groups': {gid: g.sections for gid, g in world.manifest.groups.items()},
        'blocks': block_entries,
        'releases': rel_entries,
        'held': sorted(held, key=order.index),
        'owner': [f'missing page {f.page} in group {f.group}: drop or remap it in manifest.toml' for f in pages],
    }
    return write_packet(world, out, index, {GUIDE: world.guide, BLOCKS: block_lines, RELEASES: rel_lines})


def group_docs(world: World, groups: list[str]) -> Path:
    '''R8.5's snapshot: the groups' cached pages copied from latest/ to the
    head release's snapshot, which the verifier greps.'''
    names = {page: page_file(page) for gid in groups for page in world.manifest.groups[gid].pages
             if (latest_docs(world.cache) / page_file(page)).is_file()}
    return copy_to_snapshot(world.cache, world.head, names)


def section_list(world: World, sids: list[str], notes: dict[str, list[str]]) -> tuple[dict, list[str]]:
    '''Each section's guide lines, then its notes: (sid -> [first, last],
    the sections.md lines).'''
    lines = section_lines(world.guide)
    out = ['# Sections', '']
    for sid in sids:
        out += [f'## {sid} · guide lines {lines[sid][0]}-{lines[sid][1]}', '', *notes.get(sid, []), '']
    return {sid: list(lines[sid]) for sid in sids}, out


def triage_notes(triaged: dict, sid: str) -> list[str]:
    '''The settled triage rows that sent a section to verify.'''
    rows = triaged.get('rows', {}).get(sid)
    return ['Triage rows that sent it here:', *(f'- {r}' for r in rows)] if rows else ['No triage row sent it here.']


def known_sections(world: World, ids: list[str]) -> None:
    unknown = [sid for sid in dict.fromkeys(ids) if sid not in world.state['sections']]
    if unknown:
        raise SetupError(f"unknown section IDs: {', '.join(unknown)}")


def verify(world: World, out: Path, ids: list[str], settled: Path | None) -> list[Path]:
    '''R8.5's packets, one per group of the named sections: the guide, the
    sections' lines with the triage rows that sent them here, every block
    finding of the group, the changelog, and the group's pages copied to the
    head release's snapshot. From a settled triage, `advance_to`, `cleared`
    and `held` carry over for settle's bookkeeping, and no IDs means the
    sections it sent on. `checked` names each section's checked release, so
    settle never advances one backwards.'''
    if settled and not settled.is_file():
        raise SetupError(f'{settled}: not found; run settle on the triage packet first')
    triaged = json.loads(settled.read_text(encoding='utf-8')) if settled else {}
    if settled and triaged.get('mode') != 'triage':
        raise SetupError(f'{settled}: not a settled triage')
    if not ids and not settled:
        raise SetupError('--verify needs section IDs, or --from a settled triage')
    ids = list(ids) or triaged.get('verify', [])
    if not ids:
        raise SetupError(f'{settled}: its triage sent no section to verify')
    known_sections(world, ids)
    holds = page_holds(world) | set(triaged.get('held', []))
    owner = world.manifest.group_of()
    groups = [gid for gid in world.manifest.groups if any(owner[sid] == gid for sid in ids)]
    docs = group_docs(world, groups)
    new_dir(out, world.source.repo)
    made = []
    for gid in groups:
        sids = [sid for sid in world.manifest.groups[gid].sections if sid in ids]
        found = [f for f in world.findings if f.group == gid and f.kind in BLOCK_KINDS]
        entries, block_lines = block_items(world, found)
        lines, section_md = section_list(world, sids, {sid: triage_notes(triaged, sid) for sid in sids})
        index = header(world, 'verify') | {
            'group': gid, 'sections': sids, 'lines': lines,
            'checked': {sid: world.state['sections'][sid]['checked']['release'] for sid in sids}, 'docs': str(docs),
            'advance_to': triaged.get('advance_to'), 'cleared': triaged.get('cleared', []),
            'held': [sid for sid in world.manifest.groups[gid].sections if sid in holds],
            'quotes': {'guide': [GUIDE], 'changelog': [CHANGELOG], 'docs': [str(docs)]}, 'blocks': entries,
        }
        made.append(write_packet(world, out / gid, index, {GUIDE: world.guide, SECTIONS: section_md,
                                                           BLOCKS: block_lines, CHANGELOG: world.docs.changelog}))
    return made


def audit(world: World, out: Path, group: str) -> Path:
    '''R8.6's packet: every section of the group, all its pages copied to the
    head release's snapshot, every bullet of each release untriaged for its
    sections, the changelog, and the group's block findings.'''
    if group not in world.manifest.groups:
        raise SetupError(f'unknown group {group}')
    sids = world.manifest.groups[group].sections
    docs = group_docs(world, [group])
    pending = {sid: ls for sid, ls in untriaged(world.state, world.releases).items() if sid in sids}
    labels = sorted({label for ls in pending.values() for label in ls}, key=version_key)
    rel_entries, rel_lines = release_items(world, labels, pending)
    entries, block_lines = block_items(world, [f for f in world.findings if f.group == group and f.kind in BLOCK_KINDS])
    lines, section_md = section_list(world, sids, {})
    index = header(world, 'audit') | {
        'group': group, 'sections': sids, 'lines': lines, 'docs': str(docs), 'releases': rel_entries,
        'held': [sid for sid in sids if sid in page_holds(world)],
        'quotes': {'guide': [GUIDE], 'changelog': [CHANGELOG], 'docs': [str(docs)]}, 'blocks': entries,
    }
    return write_packet(world, out, index, {GUIDE: world.guide, SECTIONS: section_md, BLOCKS: block_lines,
                                            RELEASES: rel_lines, CHANGELOG: world.docs.changelog})


def files(world: World, out: Path, paths: list[str]) -> list[Path]:
    '''R8.7's packets, one per file: a copy of the file, the guide, and its
    cited sections' lines and text, each marked when it changed after the
    file's stamp. No paths: the stale backlog. A path must be a citing file
    the lint reads.'''
    citations, _ = read_citations(citing_files(world.source, world.manifest.guide))
    by_path = {c.path: c for c in citations}
    targets = list(dict.fromkeys(paths)) or [path for path, _ in stale_citations(citations, world.state)]
    unread = [path for path in targets if path not in by_path]
    if unread:
        raise SetupError(f"not a citing file the lint reads: {', '.join(unread)}")
    if not targets:
        raise SetupError('no stale citation: name the files to review')
    texts = {s.id: s.text for s in sections(world.guide) if s.id}
    new_dir(out, world.source.repo)
    made = []
    for path in targets:
        c = by_path[path]
        changed = [sid for sid in c.ids if version_key(world.state['sections'][sid]['changed']) > version_key(c.stamp)]
        marks = {sid: [f"Changed after @{c.stamp}: now @{world.state['sections'][sid]['changed']}." if sid in changed
                       else f'Unchanged since @{c.stamp}.', '', *fenced(texts[sid])] for sid in c.ids}
        lines, section_md = section_list(world, list(c.ids), marks)
        copy = 'cited_' + path.rsplit('/', 1)[-1]
        index = header(world, 'files') | {
            'file': path, 'copy': copy, 'stamp': c.stamp, 'sections': list(c.ids), 'lines': lines,
            'changed': changed, 'quotes': {'guide': [GUIDE]},
        }
        made.append(write_packet(world, out / path.replace('/', '__'), index,
                                 {GUIDE: world.guide, SECTIONS: section_md, copy: world.source.require(path)}))
    return made
```

- [x] **Step 4: Wire `packets` into the CLI**

**Edit** `build/cc_guide/check.py` — replace:

```python
and the files citing it, and report what is due (drift spec R6). `--hook`
(R6.10) is Stage 4's and `packets` (R6.11) Stage 3's.'''
```

with:

```python
and the files citing it, and report what is due (drift spec R6). `--hook`
(R6.10) is Stage 4's; packets.py builds R6.11's packets from these parts.'''
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
  quotes --in DIR
```

with:

```python
  packets (--triage [--through RELEASE] | --verify [ID ...] [--from DIR]
           | --audit [GROUP] | --files [FILE ...]) [--out DIR]
      Write the packets /cc-guide hands its verifier (R6.11), from check
      --worktree's inputs: run check --worktree first, since packets never
      fetch. --verify and --audit copy their groups' pages to the head
      release's snapshot, which the verifier greps. --verify with no IDs
      takes the sections the settled triage --from names sent on. --audit
      with no group takes the due one, and refuses when none is due. --out
      defaults to a new directory under the cache's packets/, and is refused
      inside any checkout. Exit 0, or 2 on an error.
  quotes --in DIR
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
import baseline
from check import check, http_get, releases_of, summary
```

with:

```python
import baseline
import packets
from check import check, due_audit, http_get, releases_of, summary
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
    sub.add_parser('quotes').add_argument('--in', dest='root', type=Path, required=True)
```

with:

```python
    k = sub.add_parser('packets')
    mode = k.add_mutually_exclusive_group(required=True)
    mode.add_argument('--triage', action='store_true')
    mode.add_argument('--verify', nargs='*', metavar='ID')
    mode.add_argument('--audit', nargs='?', const='', metavar='GROUP')
    mode.add_argument('--files', nargs='*', metavar='FILE')
    k.add_argument('--through', metavar='RELEASE')
    k.add_argument('--from', dest='settled', type=Path, metavar='DIR')
    k.add_argument('--out', type=Path)
    sub.add_parser('quotes').add_argument('--in', dest='root', type=Path, required=True)
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
def run_quotes(args) -> int:
```

with:

```python
def run_packets(args, cache: Path, today: date, now: datetime) -> int:
    if args.through and not args.triage:
        raise SetupError('--through goes with --triage')
    if args.settled and args.verify is None:
        raise SetupError('--from goes with --verify')
    mode = next(m for m in ('triage', 'verify', 'audit', 'files') if getattr(args, m) not in (None, False))
    world = packets.load(Source(REPO), cache, now)
    out = args.out or cache / 'packets' / f"{now.strftime('%Y%m%dT%H%M%S')}-{mode}"
    if mode == 'triage':
        made = packets.triage(world, out, args.through)
        if made is None:
            print('nothing to triage: no untriaged release and no block finding')
            return 0
        made = [made]
    elif mode == 'verify':
        made = packets.verify(world, out, args.verify, args.settled and args.settled / packets.SETTLED)
    elif mode == 'audit':
        group = args.audit
        if not group:
            due = due_audit(world.manifest, world.state, world.manifest.cadence['audit_days'], today)
            if not due['due']:
                raise SetupError(f"no audit is due before {due['due_from']}: name a group to audit one anyway")
            group = due['group']
        made = [packets.audit(world, out, group)]
    else:
        made = packets.files(world, out, [repo_path(name) for name in args.files])
    for folder in made:
        print(f'wrote {mode} packet {folder}')
    return 0


def run_quotes(args) -> int:
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
        if args.command == 'quotes':
            return run_quotes(args)
```

with:

```python
        if args.command == 'packets':
            return run_packets(args, cache, today, now)
        if args.command == 'quotes':
            return run_quotes(args)
```

- [x] **Step 5: Run the suite to verify it passes**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3/build/cc_guide --python 3.13 --with pytest python -m pytest -q`
Expected: all pass, +47 over the baseline.

- [x] **Step 6: Commit**

Confirm the branch, then:

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 add build/cc_guide/packets.py build/cc_guide/test_packets.py build/cc_guide/check.py build/cc_guide/cli.py
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 commit -m "feat(cc_guide): packets writes the verifier's packets (R6.11)" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: `settle` (R8.10)

**Files:**
- Create: `build/cc_guide/settle.py`, `build/cc_guide/test_settle.py`
- Modify: `build/cc_guide/cli.py` (module docstring; imports; `parser`; a new `run_settle`; `main`)

**Interfaces:**
- Consumes: Task 2's `quotes.QuoteFiles`; Task 5's file-name constants, `packets.section_lines` and `index.json` keys; `lint.CLI`; `guide.sections`; `blocks.fenced_lines`; `docs.version_key`, `docs.LABEL_RE` and `docs.CHANGELOG`.
- Produces (Task 7 reads these):
  - the seven report formats `settle.TRIAGE_ROW`, `COVERAGE_ROW`, `VERIFY_ROW`, `CHANGELOG_ROW`, `OMISSION_ROW`, `FILES_ROW` and `NONE_ROW` (`section | none`), and `settle.FORMATS`, the tuple of all seven;
  - each row's quote fields by index, `settle.TRIAGE_QUOTES` `(4, 5)`, `VERIFY_QUOTES` `(4,)` and `FILES_QUOTES` `(3,)`;
  - `settle.split_row(line: str, count: int, quoted: tuple[int, ...] = ()) -> list[str] | None`, where only a field at a `quoted` index may hold `|` and `"`; `settle.unquote(field: str) -> str`; `settle.given(field: str) -> str` (`''` for an empty field or `-`); and `settle.report_lines(text: str) -> list[str]`;
  - `settle.section_at(p, line: int) -> str | None` and `settle.todo_reaches(guide: str) -> list[tuple[int, int]]`, on `packets.section_lines`' ranges;
  - `settle.settle(folder: Path, hold: Iterable[str] = ()) -> Settled(lines: list[str], clean: bool, saved: dict | None)`, which writes `settled.json` for a triage (`advance_to`, `verify`, `cleared`, `held`, `rows`);
  - `cli.py settle DIR [--hold ID | FILE ...]`: exit 0 when clean, 1 otherwise, 2 on a setup error such as a missing `report.md`, a `--hold` name outside the packet, or `--hold` on a triage.

- [x] **Step 1: Write the failing tests**

**Create** `build/cc_guide/test_settle.py`:

````python
'''Tests for settle.py and `cli.py settle`: the report grammar, triage's
completeness and fail-safe rules, the discard rule for verify, audit and
files, and the bookkeeping each prints (drift spec R8.4-R8.8, R11.5).'''
import json
import shlex
from datetime import datetime, timezone

import pytest

import baseline
import cli
import packets
import settle
import state
from cc_fixtures import (DOCS, FIXTURE_RELEASE, GUIDE_PATH, MANIFEST_TOML, docs_dir, fixture_repo,  # noqa: F401
                         fixture_state, guide_text, isolated_home, prime_cache, write_tree)
from lint import CLI

NOW = datetime(2026, 10, 4, 12, 0, tzinfo=timezone.utc)
CONFORMANCE = 'uv run --python 3.13 --with pyyaml python build/check_conformance.py'
TAIL = [f'  {CLI} baseline stamp', f'  {CLI} lint', f'  {CONFORMANCE}']
CITER = '#!/bin/sh\n' + '#' + ' cc-guide: alpha.overview @2.1.899\nexit 0\n'
# A new events.md block that names both beta sections' terms.
RETRY = '## Retry\n\nA retry resends `BETA_ENV` with each `BetaEvent`.\n'


@pytest.fixture
def world(tmp_path, docs_dir):
    repo = fixture_repo(tmp_path / 'repo', {GUIDE_PATH: guide_text(), state.MANIFEST: MANIFEST_TOML,
                                            state.BASELINE: state.dump_baseline(fixture_state(docs_dir)),
                                            'hooks/gate.sh': CITER})
    cache = tmp_path / 'cache'
    write_tree(state.snapshot_docs(cache, FIXTURE_RELEASE), DOCS)
    prime_cache(cache, docs_dir)
    return repo, cache


def load(world):
    return packets.load(state.Source(world[0]), world[1], NOW)


def latest(world, files):
    write_tree(state.latest_docs(world[1]), files)


def settled(folder, *rows):
    (folder / packets.REPORT).write_text('\n'.join(rows) + '\n')
    return settle.settle(folder)


def triage(world, tmp_path, through=None):
    return packets.triage(load(world), tmp_path / 'p', through)


@pytest.mark.parametrize('line, count, quoted, fields', [
    ('B1 | NOISE | - | - | - | "a | b "c"" | why | it has a pipe', 7, settle.TRIAGE_QUOTES,
     ['B1', 'NOISE', '-', '-', '-', '"a | b "c""', 'why | it has a pipe']),
    ('| B1 | TOUCHES | x.y | 4 | "g" | "s" | why |', 7, settle.TRIAGE_QUOTES,
     ['B1', 'TOUCHES', 'x.y', '4', '"g"', '"s"', 'why']),
    ('2.1.901 | none', 2, (), ['2.1.901', 'none']),
    ('B1 | NOISE | why', 7, settle.TRIAGE_QUOTES, None),
    ('B1 | NOISE | - | - | "unclosed | why', 7, settle.TRIAGE_QUOTES, None),
    # A free-text field that opens with a quote ends at the next pipe, as in
    # the 2026-10-12 skill probe's files row.
    ('a.md:22 | "no edit tools": no Write | x.y | "a | b" | consistent', 5, settle.FILES_QUOTES,
     ['a.md:22', '"no edit tools": no Write', 'x.y', '"a | b"', 'consistent']),
])
def test_a_row_splits_on_pipes_but_a_quote_field_holds_pipes_and_quotes(line, count, quoted, fields):
    assert settle.split_row(line, count, quoted) == fields


def test_a_quote_field_drops_its_outer_quotes_and_a_dash_is_no_quote():
    assert [settle.unquote(f) for f in ('"a "b" c"', '-', '', 'bare')] == ['a "b" c', '', '', 'bare']


def test_table_separators_header_rows_and_prose_are_no_rows():
    text = '\n'.join(['# Report', 'Prose without a pipe.', settle.TRIAGE_ROW, '|---|---|', '| item | verdict |',
                      'B1 | NOISE | - | - | - | "s" | why'])
    assert settle.report_lines(text) == ['B1 | NOISE | - | - | - | "s" | why']


def test_a_complete_triage_advances_every_section_and_rebaselines_the_block(world, tmp_path):
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = triage(world, tmp_path)
    result = settled(out, settle.TRIAGE_ROW,
                     'B1 | NOISE | - | - | - | "runs alpha batches" | a wording change; the guide claims nothing here',
                     '2.1.901 | none', '2.1.902 | none')
    assert result.lines == [
        f'cc-guide settle: triage, {out}',
        'report: 1 item(s) answered, 2 of 2 release(s) covered; 0 quote(s) not found; 0 unparseable line(s); '
        '0 left out',
        'then, in this order (R8.8):',
        f"  {CLI} baseline rebaseline alpha 'tools › Tools'",
        f'  {CLI} baseline advance alpha.overview alpha.reference beta.overview beta.reference --to 2.1.902',
        *TAIL]
    assert result.clean
    assert json.loads((out / packets.SETTLED).read_text()) == {
        'mode': 'triage', 'advance_to': '2.1.902', 'verify': [],
        'cleared': ['alpha.overview', 'alpha.reference', 'beta.overview', 'beta.reference'], 'held': [], 'rows': {}}


def test_a_report_handed_back_indented_settles_as_written(world, tmp_path):
    '''The Agent tool hands a report back with every line indented. Saved
    unchanged, as the skill says, it settles the same.'''
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = triage(world, tmp_path)
    rows = ['B1 | NOISE | - | - | - | "runs alpha batches" | a wording change', '2.1.901 | none', '2.1.902 | none']
    assert settled(out, *(f'  {r}' for r in rows)) == settled(out, *rows)
    out = review(world, tmp_path / 'r')
    rows = [GOOD, 'B | 2.1.901 | adds ALPHA_ENV | changelog.md:14', 'C | an omission']
    assert settled(out, *(f'  {r}' for r in rows)) == settled(out, *rows)


def test_an_omitted_block_and_a_missing_coverage_line_go_to_verify_as_unsure(world, tmp_path):
    '''R8.4 step 4: silence never counts as NOISE.'''
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = triage(world, tmp_path)
    result = settled(out, '2.1.901 | none')
    assert result.lines == [
        f'cc-guide settle: triage, {out}',
        'report: 0 item(s) answered, 1 of 2 release(s) covered; 0 quote(s) not found; 0 unparseable line(s); '
        '2 left out',
        'UNSURE or TOUCHES alpha.overview: B1: no row',
        'UNSURE or TOUCHES beta.overview: 2.1.902: no coverage line',
        'then, in this order (R8.8):',
        f'  {CLI} baseline advance alpha.reference beta.reference --to 2.1.902',
        *TAIL,
        'verify: /cc-guide verify alpha.overview beta.overview; or defer it, and those sections do not advance, '
        'so the next triage shows them again']
    assert not result.clean
    saved = json.loads((out / packets.SETTLED).read_text())
    assert (saved['verify'], saved['rows']) == (['alpha.overview', 'beta.overview'], {
        'alpha.overview': ['B1, block tools › Tools: no row'],
        'beta.overview': ['2.1.902: no coverage line; its bullets that hint at it: "Changed how `BETA_ENV` is read"']})


def test_a_failed_quote_makes_noise_unsure_and_is_listed_on_touches(world, tmp_path):
    '''R8.4 step 5: a row whose quote fails becomes UNSURE, handled as
    TOUCHES, so triage fails safe.'''
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = triage(world, tmp_path)
    noise = 'B1 | NOISE | - | - | - | "runs alpha quickly" | wording'
    touches = '2.1.902#1 | TOUCHES | beta.overview | 31 | "| `BETA_ENV` | off |" | "how `BETA_ENV` is read" | moved'
    result = settled(out, noise, touches, '2.1.901 | none', '2.1.902 | beta.overview')
    assert result.lines[1:6] == [
        'report: 2 item(s) answered, 2 of 2 release(s) covered; 2 quote(s) not found; 0 unparseable line(s); '
        '0 left out',
        f'  quote not found, NOISE becomes UNSURE: {noise}',
        f'  quote not found, TOUCHES becomes UNSURE: {touches}',
        "UNSURE or TOUCHES alpha.overview: B1: its NOISE row's source quote was not found",
        'UNSURE or TOUCHES beta.overview: 2.1.902#1: TOUCHES, quote not found; '
        '2.1.902: its coverage line names it']
    assert not result.clean


def test_an_unparseable_row_is_listed_and_a_bullets_falls_back_to_its_hints(world, tmp_path):
    out = triage(world, tmp_path)
    rows = ['B9 | TOUCHES | alpha.overview | 14 | "g" | "s" | no such item',
            '2.1.901#1 | TOUCHES | gamma.overview | 1 | "g" | "s" | no such section',
            '2.1.902#2 | NOISE | - | - | - | "Fixed a crash" |']
    result = settled(out, *rows, '2.1.901 | alpha.reference', '2.1.902 | none')
    assert result.lines[1:5] == [
        'report: 0 item(s) answered, 2 of 2 release(s) covered; 0 quote(s) not found; 3 unparseable line(s); '
        '0 left out', *(f'  unparseable row: {r}' for r in rows)]
    assert 'UNSURE or TOUCHES alpha.reference: 2.1.901#1: its row does not parse; 2.1.901: its coverage line names it' \
        in result.lines


def test_a_release_no_coverage_line_and_no_hint_reaches_is_an_owner_item_that_caps_the_advance(world, tmp_path):
    changelog = DOCS['changelog.md'].replace(
        '<Update label="2.1.902"', '<Update label="2.1.903" description="October 3, 2026">\n'
        '  * Fixed a typo\n</Update>\n\n<Update label="2.1.902"')
    latest(world, {'changelog.md': changelog})
    out = triage(world, tmp_path)
    result = settled(out, '2.1.901 | none', '2.1.902 | none')
    assert "owner: 2.1.903: no coverage line, and its bullets hit no section's terms" in result.lines
    assert f'  {CLI} baseline advance alpha.overview alpha.reference beta.overview beta.reference --to 2.1.902' \
        in result.lines


def test_the_first_release_range_settles_the_block_findings(world, tmp_path):
    '''R8.4's split: block findings ride in the oldest range, so a block
    resolved there is rebaselined, and its sections advance only to the
    range's end.'''
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = triage(world, tmp_path, '2.1.901')
    result = settled(out, 'B1 | NOISE | - | - | - | "runs alpha batches" | a wording change', '2.1.901 | none')
    assert result.lines[2:5] == [
        'then, in this order (R8.8):', f"  {CLI} baseline rebaseline alpha 'tools › Tools'",
        f'  {CLI} baseline advance alpha.overview alpha.reference beta.overview beta.reference --to 2.1.901']
    assert result.lines[-1] == f'next range, once these commands are run: {CLI} packets --triage --through 2.1.902'


def test_a_missing_pages_held_sections_are_saved_and_hold_their_groups_blocks(world, tmp_path):
    '''A held section never advances, its group's blocks are not
    rebaselined, and settled.json carries the hold into verify.'''
    (state.latest_docs(world[1]) / 'events.md').unlink()
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches'),
                   'env-vars.md': DOCS['env-vars.md'].replace('Turns on beta', 'Turns on every beta')})
    out = triage(world, tmp_path)
    i = json.loads((out / packets.INDEX).read_text())
    assert [(b['item'], b['group']) for b in i['blocks']] == [('B1', 'alpha'), ('B2', 'beta')]
    result = settled(out, 'B1 | NOISE | - | - | - | "runs alpha batches" | a wording change',
                     'B2 | NOISE | - | - | - | "Turns on every beta" | a wording change', '2.1.901 | none',
                     '2.1.902 | none')
    assert [line for line in result.lines if 'baseline' in line][:2] == [
        f"  {CLI} baseline rebaseline alpha 'tools › Tools'",
        f'  {CLI} baseline advance alpha.overview alpha.reference --to 2.1.902']
    assert json.loads((out / packets.SETTLED).read_text())['held'] == ['beta.overview', 'beta.reference']


def test_the_haiku_case_a_section_the_hints_miss_still_goes_to_verify(world, tmp_path):
    '''R11.5's acceptance case, modelled on 2.1.293 (Haiku 5.5 became the
    `haiku` alias on the Anthropic API): the release's bullet hints only one
    section, while the docs block that changed names more. A verifier that
    answers the bullet and leaves the block out still sends every candidate
    section to verify.'''
    latest(world, {'events.md': DOCS['events.md'] + RETRY})
    out = triage(world, tmp_path)
    i = json.loads((out / packets.INDEX).read_text())
    assert [(b['ref'], b['candidates']) for b in i['blocks']] == [
        ('events › Events › Retry', ['beta.overview', 'beta.reference'])]
    assert i['releases'][1]['bullets'][0]['hints'] == ['beta.overview']
    bullet = '2.1.902#1 | TOUCHES | beta.overview | 31 | "| `BETA_ENV` | on |" | "how `BETA_ENV` is read" | reads'
    left_out = settled(out, bullet, '2.1.901 | none', '2.1.902 | beta.overview')
    assert json.loads((out / packets.SETTLED).read_text())['verify'] == ['beta.overview', 'beta.reference']
    assert 'UNSURE or TOUCHES beta.reference: B1: no row' in left_out.lines
    cleared = settled(out, bullet, 'B1 | NOISE | - | - | - | "A retry resends `BETA_ENV`" | retries are not claimed',
                      '2.1.901 | none', '2.1.902 | beta.overview')
    assert json.loads((out / packets.SETTLED).read_text())['verify'] == ['beta.overview']
    assert cleared.clean


def test_a_noise_bullet_whose_quote_fails_falls_back_to_its_hints_or_caps_the_advance(world, tmp_path):
    '''Review finding 3: a NOISE row's failed quote never clears its item.
    A bullet's falls back to its hints, as a broken bullet row does, or is
    an owner item that caps the advance below its release.'''
    out = triage(world, tmp_path)
    hinted = '2.1.901#1 | NOISE | - | - | - | "not in the bullet" | harmless'
    bare = '2.1.902#2 | NOISE | - | - | - | "not in the bullet" | harmless'
    result = settled(out, hinted, bare, '2.1.901 | none', '2.1.902 | none')
    assert "UNSURE or TOUCHES alpha.reference: 2.1.901#1: its NOISE row's source quote was not found" in result.lines
    assert ("owner: 2.1.902#2: its NOISE row's source quote was not found, and its bullet hits no section's terms"
            in result.lines)
    assert f'  {CLI} baseline advance alpha.overview beta.overview beta.reference --to 2.1.901' in result.lines


def test_a_bullets_owner_item_caps_the_advance_below_its_release(world, tmp_path):
    '''Review finding 4: the cap reads an owner item's release, not its
    wording.'''
    out = triage(world, tmp_path)
    result = settled(out, '2.1.902#2 | broken', '2.1.901 | none', '2.1.902 | none')
    assert "owner: 2.1.902#2: its row does not parse, and its bullet hits no section's terms" in result.lines
    assert (f'  {CLI} baseline advance alpha.overview alpha.reference beta.overview beta.reference --to 2.1.901'
            in result.lines)
    assert json.loads((out / packets.SETTLED).read_text())['advance_to'] == '2.1.901'


def test_a_source_quote_counts_only_within_its_own_item(world, tmp_path):
    '''The packet's own scaffolding and another item's text are no source
    for an item: a NOISE row quoting them becomes UNSURE.'''
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = triage(world, tmp_path)
    scaffold = 'B1 | NOISE | - | - | - | "Current text:" | the packet\'s own words'
    other = '2.1.902#1 | NOISE | - | - | - | "Fixed a crash" | another bullet\'s words'
    result = settled(out, scaffold, other, '2.1.901 | none', '2.1.902 | none')
    assert result.lines[2:4] == [f'  quote not found, NOISE becomes UNSURE: {scaffold}',
                                 f'  quote not found, NOISE becomes UNSURE: {other}']
    assert "UNSURE or TOUCHES alpha.overview: B1: its NOISE row's source quote was not found" in result.lines
    assert "UNSURE or TOUCHES beta.overview: 2.1.902#1: its NOISE row's source quote was not found" in result.lines


def test_a_noise_rows_guide_quote_is_checked_when_given(world, tmp_path):
    '''Second review, finding 3: a NOISE row may leave its guide quote out,
    but one it gives must be found, or the row becomes UNSURE.'''
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = triage(world, tmp_path)
    noise = 'B1 | NOISE | alpha.overview | 14 | "guide fiction" | "runs alpha batches" | harmless'
    result = settled(out, noise, '2.1.901 | none', '2.1.902 | none')
    assert f'  quote not found, NOISE becomes UNSURE: {noise}' in result.lines
    assert "UNSURE or TOUCHES alpha.overview: B1: its NOISE row's guide quote was not found" in result.lines
    assert not any('rebaseline' in line for line in result.lines)
    assert not result.clean


def test_a_noise_row_whose_why_is_a_dash_does_not_parse(world, tmp_path):
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = triage(world, tmp_path)
    dash = 'B1 | NOISE | - | - | - | "runs alpha batches" | -'
    result = settled(out, dash, '2.1.901 | none', '2.1.902 | none')
    assert f'  unparseable row: {dash}' in result.lines
    assert 'UNSURE or TOUCHES alpha.overview: B1: no row' in result.lines


# ---- verify and audit --------------------------------------------------------

def review(world, tmp_path, sids=('alpha.overview', 'alpha.reference'), settled_triage=None):
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    return packets.verify(load(world), tmp_path / 'v', list(sids), settled_triage)[0]


GOOD = 'L14 | Alpha uses ALPHA_TOOL | STALE | tools.md:5 | "runs alpha batches" | Alpha batches with `ALPHA_TOOL`.'


def test_a_verify_report_lists_corrections_owners_calls_and_the_bookkeeping(world, tmp_path):
    write_tree(tmp_path / 't', {packets.SETTLED: json.dumps(
        {'mode': 'triage', 'advance_to': '2.1.902', 'verify': ['alpha.overview'], 'cleared': [], 'rows': {}})})
    out = review(world, tmp_path, settled_triage=tmp_path / 't' / packets.SETTLED)
    result = settled(out, settle.VERIFY_ROW, GOOD,
                     'L19 | Set ALPHA_ENV | CONFIRMED | changelog.md:14 | "Added `ALPHA_ENV`" | -',
                     'L19 | the tick span | NOT FOUND | - | - | -',
                     'L14 | prefer alpha | JUDGMENT | - | - | -',
                     'B | 2.1.901 | adds ALPHA_ENV to the alpha tools | changelog.md:14',
                     'C | the guide never says what ALPHA_TOOL costs')
    assert result.lines == [
        f'cc-guide settle: verify alpha, {out}',
        "report: 1 confirmed, 1 correction(s), 3 owner's call, 0 unverified",
        'corrections, to apply to the guide in the working tree:',
        '  L14 alpha.overview STALE: Alpha uses ALPHA_TOOL → Alpha batches with `ALPHA_TOOL`. '
        '(tools.md:5: "runs alpha batches")',
        "owner's call, never applied:",
        '  L19 alpha.reference NOT FOUND: the tick span',
        '  L14 alpha.overview JUDGMENT: prefer alpha',
        '  omission: the guide never says what ALPHA_TOOL costs',
        'unverified, discarded:',
        'changelog items (B):',
        '  2.1.901 | adds ALPHA_ENV to the alpha tools | changelog.md:14',
        'then, in this order (R8.8), once every correction is applied; for one you leave for the owner, settle '
        'again with --hold <section>, which holds the section and keeps its accept:',
        f'  {CLI} baseline accept alpha.overview --substantive   # only the sections you changed',
        f"  {CLI} baseline rebaseline alpha 'tools › Tools'",
        f'  {CLI} baseline advance alpha.overview alpha.reference --to 2.1.902',
        *TAIL,
        "a correction that resolves a conformance gap removes its [[exception]] from build/cc_guide/conformance.toml "
        "in the same change; lint's STALE lines then name the citing files of each section whose `changed` moved"]
    assert result.clean


def test_a_failed_verify_quote_is_discarded_and_holds_its_section(world, tmp_path):
    '''R8.8 step 1: the refresh's rule, the opposite of triage's escalation.
    A discarded correction holds its section, so nothing advances past it.'''
    out = review(world, tmp_path)
    bad = 'L14 | Alpha uses ALPHA_TOOL | WRONG | tools.md:5 | "runs alpha slowly" | Alpha batches.'
    result = settled(out, bad, 'L19 | Set ALPHA_ENV | CONFIRMED | tools.md:1 | "not on the page" | -')
    assert result.lines[1:8] == [
        "report: 0 confirmed, 0 correction(s), 0 owner's call, 2 unverified",
        'corrections, to apply to the guide in the working tree:',
        "owner's call, never applied:",
        'unverified, discarded:',
        f'  quote not found, discarded: {bad}',
        '  quote not found, discarded: L19 | Set ALPHA_ENV | CONFIRMED | tools.md:1 | "not on the page" | -',
        'changelog items (B):']
    assert result.lines[8:10] == ['left out (no surviving row, no none line), so held: alpha.overview alpha.reference',
                                  'held, neither advanced nor audited: alpha.overview alpha.reference']
    assert not any('rebaseline' in line or 'accept' in line for line in result.lines if line.startswith('  '))
    assert not result.clean


def test_a_correction_next_to_a_todo_owner_or_outside_the_packet_is_the_owners_call(world, tmp_path):
    out = review(world, tmp_path, sids=('alpha.reference',))
    guide = (out / packets.GUIDE).read_text().split('\n')
    guide[17] = '<!-- TODO(owner): decide the alpha stance -->'  # line 18, just above line 19
    (out / packets.GUIDE).write_text('\n'.join(guide))
    near = 'L19 | Set ALPHA_ENV | STALE | tools.md:5 | "runs alpha batches" | Set ALPHA_ENV twice.'
    result = settled(out, near, GOOD)
    assert result.lines[3:6] == [
        "owner's call, never applied:",
        '  L19 alpha.reference STALE (next to a TODO(owner), report-only): Set ALPHA_ENV → Set ALPHA_ENV twice.',
        "  L14 alpha.overview STALE (outside this packet's sections, so it holds nothing; "
        '/cc-guide verify alpha.overview reviews it): Alpha uses ALPHA_TOOL → Alpha batches with `ALPHA_TOOL`.']


def test_a_todo_owner_reaches_through_the_first_list_item_after_it(world, tmp_path):
    '''The guide's TODO names "the first bullet below": the bullet after it
    is checkable again (the 2026-10-12 application run's L426).'''
    out = review(world, tmp_path, sids=('alpha.reference',))
    guide = (out / packets.GUIDE).read_text().split('\n')
    guide[17:20] = ['<!-- TODO(owner): decide the alpha stance -->', '- Set `ALPHA_ENV`.', '- Run alpha batches.']
    (out / packets.GUIDE).write_text('\n'.join(guide))
    first = 'L19 | Set ALPHA_ENV | STALE | tools.md:5 | "runs alpha batches" | Set ALPHA_ENV twice.'
    second = 'L20 | Run alpha batches | STALE | tools.md:5 | "runs alpha batches" | Run them twice.'
    result = settled(out, first, second)
    assert result.lines[2:6] == [
        'corrections, to apply to the guide in the working tree:',
        '  L20 alpha.reference STALE: Run alpha batches → Run them twice. (tools.md:5: "runs alpha batches")',
        "owner's call, never applied:",
        '  L19 alpha.reference STALE (next to a TODO(owner), report-only): Set ALPHA_ENV → Set ALPHA_ENV twice.']


@pytest.mark.parametrize('line', ['L99x | a claim | STALE | tools.md:5 | "runs" | x',
                                  # Review finding 11: past the guide's end is in no section.
                                  'L999 | an invented claim | WRONG | tools.md:5 | "runs alpha batches" | Else.'])
def test_an_unattributable_line_holds_every_section(world, tmp_path, line):
    out = review(world, tmp_path)
    result = settled(out, line, GOOD, 'alpha.reference | none')
    assert 'held, neither advanced nor audited: alpha.overview alpha.reference' in result.lines
    assert f'  unparseable: {line}' in result.lines


def test_a_doc_quote_counts_only_in_the_docs_or_the_packets_changelog(world, tmp_path):
    '''Review finding 1: the verifier's own report, the guide copy and the
    index are no docs. Only the head snapshot's pages and the packet's
    changelog.md are.'''
    out = review(world, tmp_path, sids=('alpha.overview',))
    rows = ['L14 | Alpha uses ALPHA_TOOL | STALE | report.md:1 | "Alpha uses ALPHA_TOOL" | Alpha batches.',
            'L14 | Alpha uses ALPHA_TOOL | WRONG | guide.md:14 | "Alpha uses `ALPHA_TOOL`" | Alpha batches.',
            'L14 | Alpha uses ALPHA_TOOL | PARTIAL | index.json:1 | "mode" | Alpha batches.']
    result = settled(out, *rows, 'L14 | ALPHA_ENV arrived | CONFIRMED | changelog.md:14 | "Added `ALPHA_ENV`" | -')
    assert [line for line in result.lines if line.startswith('  quote not found')] == [
        f'  quote not found, discarded: {r}' for r in rows]
    assert result.lines[1] == "report: 1 confirmed, 0 correction(s), 0 owner's call, 3 unverified"


def test_a_section_needs_a_surviving_row_or_a_none_line(world, tmp_path):
    '''Review finding 2: a section the report says nothing verifiable about
    was not reviewed, so it is held. `<section> | none` says it holds no
    checkable claim.'''
    out = review(world, tmp_path)
    left = settled(out, GOOD)
    assert 'left out (no surviving row, no none line), so held: alpha.reference' in left.lines
    assert not left.clean
    answered = settled(out, GOOD, 'alpha.reference | none')
    assert not any(line.startswith(('left out', 'held')) for line in answered.lines)
    assert answered.clean


@pytest.mark.parametrize('text', ['', 'No report could be produced.\n'])
def test_an_empty_or_prose_only_report_holds_every_section(world, tmp_path, text):
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = packets.audit(load(world), tmp_path / 'a', 'alpha')
    (out / packets.REPORT).write_text(text)
    result = settle.settle(out)
    assert 'left out (no surviving row, no none line), so held: alpha.overview alpha.reference' in result.lines
    assert not any(('audited' in line or 'rebaseline' in line) for line in result.lines if line.startswith('  '))
    assert not result.clean


def test_a_dash_is_no_proposed_wording(world, tmp_path):
    '''Review finding 9: `-` marks an empty field, so it proposes nothing.'''
    out = review(world, tmp_path, sids=('alpha.overview',))
    dash = 'L14 | Alpha uses ALPHA_TOOL | STALE | tools.md:5 | "runs alpha batches" | -'
    result = settled(out, dash)
    assert f'  no proposed wording, discarded: {dash}' in result.lines
    assert 'held, neither advanced nor audited: alpha.overview' in result.lines


def test_a_broken_b_or_c_row_is_unparseable_and_holds_nothing(world, tmp_path):
    '''Review finding 12.'''
    out = review(world, tmp_path)
    rows = ['B | 2.1.297', 'B | 2.1.901 | adds ALPHA_ENV | changelog', 'C | -',
            # Second review, finding 9: only a release label and a changelog.md line.
            'B | 2.1.901 | adds ALPHA_ENV | report.md:1', 'B | banana | adds ALPHA_ENV | changelog.md:14',
            'B | 2.1.901 | adds ALPHA_ENV | changelog.md:0']
    result = settled(out, GOOD, 'alpha.reference | none', *rows)
    assert [line for line in result.lines if line.startswith('  unparseable')] == [
        f'  unparseable: {r}' for r in rows]
    assert not any(line.startswith('held') for line in result.lines)
    assert not result.clean


def test_a_quote_a_row_need_not_give_is_still_checked_when_given(world, tmp_path):
    '''Review finding 13: JUDGMENT and NOT FOUND may leave their quote out,
    but a quote they give is re-grepped like any other.'''
    out = review(world, tmp_path)
    rows = ['L14 | prefer alpha | JUDGMENT | tools.md:5 | "does not exist" | -',
            'L19 | the tick span | NOT FOUND | tools.md:5 | "nor does this" | -']
    result = settled(out, GOOD, 'L19 | Set ALPHA_ENV | CONFIRMED | changelog.md:14 | "Added `ALPHA_ENV`" | -', *rows)
    assert [line for line in result.lines if line.startswith('  quote not found')] == [
        f'  quote not found, discarded: {r}' for r in rows]


def triage_file(tmp_path, **saved):
    write_tree(tmp_path / 't', {packets.SETTLED: json.dumps(
        {'mode': 'triage', 'advance_to': '2.1.902', 'verify': [], 'cleared': [], 'held': [], 'rows': {}} | saved)})
    return tmp_path / 't' / packets.SETTLED


def todo_guide(out, lines):
    guide = (out / packets.GUIDE).read_text().split('\n')
    guide[17:20] = lines
    (out / packets.GUIDE).write_text('\n'.join(guide))


def test_a_correction_left_for_the_owner_holds_its_section(world, tmp_path):
    '''Review finding 7: a correction next to a TODO(owner) is the owner's
    call, so it holds its section: no advance, and no rebaseline of a block
    it is a candidate of. One outside the packet's sections holds nothing
    (second review, finding 1): the packet neither reviews nor advances its
    section, so the block its triage cleared is rebaselined.'''
    saved = triage_file(tmp_path, verify=['alpha.reference'], cleared=['alpha.overview'])
    out = review(world, tmp_path, sids=('alpha.reference',), settled_triage=saved)
    todo_guide(out, ['<!-- TODO(owner): decide the alpha stance -->', '- Set `ALPHA_ENV`.', ''])
    near = 'L19 | Set ALPHA_ENV | STALE | tools.md:5 | "runs alpha batches" | Set ALPHA_ENV twice.'
    result = settled(out, near, GOOD)
    assert 'held, neither advanced nor audited: alpha.reference' in result.lines
    assert [line for line in result.lines if 'baseline' in line] == [
        f"  {CLI} baseline rebaseline alpha 'tools › Tools'", f'  {CLI} baseline stamp']


def test_a_correction_outside_the_packet_never_claims_a_hold_its_triage_already_advanced(world, tmp_path):
    '''Second review, finding 1: the triage's commands advanced the sections
    it cleared before this verify ran, so a correction in one of them is the
    owner's call with a verify of its own, never a hold.'''
    out = triage(world, tmp_path)
    settled(out, '2.1.901 | alpha.overview', '2.1.902 | none')
    v = review(world, tmp_path, sids=('alpha.overview',), settled_triage=out / packets.SETTLED)
    wrong = 'L19 | Set ALPHA_ENV | WRONG | tools.md:5 | "runs alpha batches" | Set it twice.'
    result = settled(v, 'L14 | Alpha uses ALPHA_TOOL | CONFIRMED | tools.md:5 | "runs alpha batches" | -', wrong)
    assert ("  L19 alpha.reference WRONG (outside this packet's sections, so it holds nothing; "
            '/cc-guide verify alpha.reference reviews it): Set ALPHA_ENV → Set it twice.') in result.lines
    assert not any(line.startswith('held') for line in result.lines)
    assert f'  {CLI} baseline advance alpha.overview --to 2.1.902' in result.lines
    assert result.clean


def test_a_todo_owner_reach_covers_its_first_items_continuation_lines(world, tmp_path):
    '''Review finding 8: a wrapped first item is in reach to its last line.'''
    out = review(world, tmp_path, sids=('alpha.reference',))
    todo_guide(out, ['<!-- TODO(owner): decide the alpha stance -->', '- Set `ALPHA_ENV`, which',
                     '  wraps onto a second line.', '- Run alpha batches.'])
    wrapped = 'L20 | ALPHA_ENV wraps | STALE | tools.md:5 | "runs alpha batches" | Set it once.'
    second = 'L21 | Run alpha batches | STALE | tools.md:5 | "runs alpha batches" | Run them twice.'
    result = settled(out, wrapped, second)
    assert result.lines[2:6] == [
        'corrections, to apply to the guide in the working tree:',
        '  L21 alpha.reference STALE: Run alpha batches → Run them twice. (tools.md:5: "runs alpha batches")',
        "owner's call, never applied:",
        '  L20 alpha.reference STALE (next to a TODO(owner), report-only): ALPHA_ENV wraps → Set it once.']


def test_a_fenced_example_never_ends_a_todo_reach(world, tmp_path):
    '''Second review, finding 7: a list-like line inside fenced code is no
    list item, so the reach runs on to the first real one.'''
    out = review(world, tmp_path, sids=('alpha.reference',))
    todo_guide(out, ['<!-- TODO(owner): decide the default in the first bullet -->', '```text',
                     '- illustrative syntax', '```', '', '- Alpha default is old.',
                     "  This continuation needs the owner's decision."])
    assert settle.todo_reaches((out / packets.GUIDE).read_text()) == [(18, 24)]
    row = 'L24 | the owner decides | STALE | tools.md:5 | "runs alpha batches" | Decide it.'
    result = settled(out, row)
    assert ('  L24 alpha.reference STALE (next to a TODO(owner), report-only): the owner decides → Decide it.'
            in result.lines)
    assert 'held, neither advanced nor audited: alpha.reference' in result.lines


def test_hold_settles_again_with_a_declined_correction_held_and_keeps_its_accept(world, tmp_path):
    '''A listed correction the session leaves for the owner: `--hold` prints
    the commands again with its section held. accept still lists it, for
    any other correction applied there.'''
    saved = triage_file(tmp_path, verify=['alpha.overview', 'alpha.reference'])
    out = review(world, tmp_path, settled_triage=saved)
    (out / packets.REPORT).write_text(f'{GOOD}\nalpha.reference | none\n')
    result = settle.settle(out, hold=['alpha.overview'])
    assert [line for line in result.lines if 'baseline' in line] == [
        f'  {CLI} baseline accept alpha.overview --substantive   # only the sections you changed',
        f'  {CLI} baseline advance alpha.reference --to 2.1.902', f'  {CLI} baseline stamp']
    assert 'held, neither advanced nor audited: alpha.overview' in result.lines
    assert result.clean
    with pytest.raises(state.SetupError) as err:
        settle.settle(out, hold=['beta.overview'])
    assert str(err.value) == '--hold beta.overview: not a section this packet reviews (alpha.overview, alpha.reference)'


def test_a_verify_packet_holds_what_its_triage_held(world, tmp_path):
    '''Review finding 6: settled.json's holds reach verify's bookkeeping.'''
    saved = triage_file(tmp_path, verify=['alpha.overview', 'alpha.reference'], held=['alpha.overview'])
    out = review(world, tmp_path, settled_triage=saved)
    result = settled(out, GOOD, 'alpha.reference | none')
    assert 'held, neither advanced nor audited: alpha.overview' in result.lines
    assert f'  {CLI} baseline advance alpha.reference --to 2.1.902' in result.lines
    assert not any('rebaseline' in line for line in result.lines)


def test_a_page_with_an_unresolved_changed_block_is_never_rebaselined(world, tmp_path):
    '''Second review, finding 5: baseline rebaselines a page's changed
    blocks together, so while one is held, settle lists none of that page's,
    and every command it does print, baseline runs.'''
    tools = DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches').replace(
        '| `--fast` | Runs fast. |', '| `--fast` | Runs fast with `ALPHA_ENV`. |')
    latest(world, {'tools.md': tools})
    w = load(world)
    out = packets.verify(w, tmp_path / 'v', ['alpha.overview', 'alpha.reference'], triage_file(tmp_path))[0]
    (out / packets.REPORT).write_text('L14 | Alpha uses ALPHA_TOOL | CONFIRMED | tools.md:5 | "runs alpha batches" | -'
                                      '\nalpha.reference | none\n')
    assert not any('rebaseline' in line for line in settle.settle(out, hold=['alpha.overview']).lines)
    whole = [line for line in settle.settle(out).lines if 'rebaseline' in line]
    assert whole == [f"  {CLI} baseline rebaseline alpha 'tools › Tools' 'tools › Tools › Options › `--fast`'"]
    refs = shlex.split(whole[0])[shlex.split(whole[0]).index('rebaseline') + 2:]
    new, _, _ = baseline.rebaseline(w.state, w.manifest, w.guide, 'alpha', refs, state.latest_docs(world[1]),
                                    '2.1.902')  # baseline refuses a page listed in part
    assert new != w.state


def test_verify_never_advances_a_section_past_its_triages_target_backwards(world, tmp_path):
    '''Second review, finding 6: a section checked past the triage's capped
    target is verified but not advanced.'''
    repo = world[0]
    baselined = state.parse_baseline((repo / state.BASELINE).read_text())
    baselined['sections']['alpha.overview']['checked'] = {'release': '2.1.902', 'date': '2026-10-04'}
    (repo / state.BASELINE).write_text(state.dump_baseline(baselined))
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = triage(world, tmp_path)
    settled(out, 'B1 | TOUCHES | alpha.overview | 14 | "Alpha uses `ALPHA_TOOL`" | "runs alpha batches" | moved',
            '2.1.902#2 | broken', '2.1.901 | none', '2.1.902 | none')
    v = packets.verify(load(world), tmp_path / 'v', [], out / packets.SETTLED)[0]
    result = settled(v, 'L14 | Alpha uses ALPHA_TOOL | CONFIRMED | tools.md:5 | "runs alpha batches" | -')
    assert not any(' advance ' in line for line in result.lines)
    assert f"  {CLI} baseline rebaseline alpha 'tools › Tools'" in result.lines


def test_an_audit_ends_with_audited_unless_a_section_is_held(world, tmp_path):
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = packets.audit(load(world), tmp_path / 'a', 'alpha')
    result = settled(out, 'L14 | Alpha uses ALPHA_TOOL | CONFIRMED | tools.md:5 | "runs alpha batches" | -',
                     'alpha.reference | none')
    assert result.lines[0] == f'cc-guide settle: audit alpha, {out}'
    assert [line for line in result.lines if 'baseline' in line][:2] == [
        f"  {CLI} baseline rebaseline alpha 'tools › Tools'", f'  {CLI} baseline audited alpha']
    held = settled(out, 'L14 | Alpha uses ALPHA_TOOL | PARTIAL | tools.md:5 | "absent" | Partly.')
    assert not any('audited' in line for line in held.lines if line.startswith('  '))


# ---- files -------------------------------------------------------------------

def test_a_files_report_lists_contradictions_and_cites_the_file(world, tmp_path):
    out = packets.files(load(world), tmp_path / 'f', [])[0]
    result = settled(out, settle.FILES_ROW,
                     'hooks/gate.sh:3 | exits 0 always | alpha.overview | "Alpha uses `ALPHA_TOOL`" | contradicts',
                     'hooks/gate.sh:1 | a shell script | alpha.overview | "## 1. Alpha" | consistent',
                     'hooks/gate.sh:2 | the launchd PATH | alpha.overview | - | not covered')
    assert result.lines == [
        f'cc-guide settle: files hooks/gate.sh, {out}',
        'report: 1 consistent, 1 contradiction(s), 1 not covered, 0 unverified',
        'contradictions, to fix in hooks/gate.sh in the working tree:',
        '  hooks/gate.sh:3 (alpha.overview): exits 0 always (guide: "Alpha uses `ALPHA_TOOL`")',
        "owner's call, never applied:",
        '  hooks/gate.sh:2 (alpha.overview, not covered; a coverage gap?): the launchd PATH',
        'unverified, discarded:',
        'then, in this order (R8.8), once every contradiction is fixed in hooks/gate.sh, unless '
        'build/cc_guide/conformance.toml records it as a deviation, which stays as it is; for one you leave for the '
        'owner, settle again with --hold hooks/gate.sh, which skips its cite:',
        f'  {CLI} baseline cite hooks/gate.sh', f'  {CLI} lint', f'  {CONFORMANCE}']
    assert result.clean


def test_a_statement_that_opens_with_a_quote_still_parses(world, tmp_path):
    out = packets.files(load(world), tmp_path / 'f', [])[0]
    result = settled(out, 'hooks/gate.sh:3 | "exit 0": it always succeeds | alpha.overview | "## 1. Alpha" | consistent')
    assert result.lines[1] == 'report: 1 consistent, 0 contradiction(s), 0 not covered, 0 unverified'
    assert result.clean


def test_a_discarded_contradiction_holds_the_file_uncited(world, tmp_path):
    out = packets.files(load(world), tmp_path / 'f', [])[0]
    result = settled(out, 'hooks/gate.sh:3 | exits 0 | alpha.overview | "not in the guide" | contradicts',
                     'other/file.sh:1 | x | alpha.overview | "## 1. Alpha" | consistent')
    assert ('held, not cited: hooks/gate.sh: a discarded or unparseable row might have changed it; '
            'a cited section was left out') in result.lines
    assert not any('cite' in line for line in result.lines if line.startswith('  '))
    assert '  unparseable: other/file.sh:1 | x | alpha.overview | "## 1. Alpha" | consistent' in result.lines


def test_a_files_row_on_a_section_the_file_does_not_cite_holds_it(world, tmp_path):
    '''Second review, finding 8: a files review covers the cited sections
    only, so a row naming another section does not parse.'''
    out = packets.files(load(world), tmp_path / 'f', [])[0]
    beta = 'hooks/gate.sh:1 | Beta contradicts | beta.reference | "`BetaEvent` fires." | contradicts'
    result = settled(out, 'alpha.overview | none', beta)
    assert f'  unparseable: {beta}' in result.lines
    assert 'held, not cited: hooks/gate.sh: a discarded or unparseable row might have changed it' in result.lines
    assert not any('cite' in line for line in result.lines if line.startswith('  '))


@pytest.mark.parametrize('rows', [(), ('No report could be produced.',)])
def test_a_cited_section_with_no_surviving_row_or_none_line_holds_the_file(world, tmp_path, rows):
    out = packets.files(load(world), tmp_path / 'f', [])[0]
    result = settled(out, *rows)
    assert 'left out (no surviving row, no none line): alpha.overview' in result.lines
    assert not any('cite' in line for line in result.lines if line.startswith('  '))
    assert not result.clean
    answered = settled(out, 'alpha.overview | none')
    assert f'  {CLI} baseline cite hooks/gate.sh' in answered.lines
    assert answered.clean


def test_a_not_covered_rows_quote_is_checked_when_given_and_hold_holds_the_file(world, tmp_path):
    out = packets.files(load(world), tmp_path / 'f', [])[0]
    bogus = 'hooks/gate.sh:2 | the launchd PATH | alpha.overview | "not in the guide" | not covered'
    result = settled(out, bogus, 'hooks/gate.sh:1 | a shell script | alpha.overview | "## 1. Alpha" | consistent')
    assert f'  quote not found, discarded: {bogus}' in result.lines
    assert f'  {CLI} baseline cite hooks/gate.sh' in result.lines
    held = settle.settle(out, hold=['hooks/gate.sh'])
    assert 'held, not cited: hooks/gate.sh: held by --hold' in held.lines
    assert [line for line in held.lines if line.startswith('  ')][-2:] == [f'  {CLI} lint', f'  {CONFORMANCE}']
    assert not any('cite' in line for line in held.lines if line.startswith('  '))
    with pytest.raises(state.SetupError) as err:
        settle.settle(out, hold=['alpha.overview'])
    assert str(err.value) == '--hold alpha.overview: a files packet holds only its file, hooks/gate.sh'


# ---- the CLI -----------------------------------------------------------------

def test_the_cli_exits_on_the_report_and_two_without_one(world, tmp_path, capsys):
    out = triage(world, tmp_path)
    assert cli.main(['settle', str(out)]) == 2
    assert capsys.readouterr() == ('', f"cc-guide: {out / 'report.md'}: not found; save the verifier's report as "
                                       'report.md in the packet\n')
    (out / packets.REPORT).write_text('2.1.901 | none\n2.1.902 | none\n')
    assert cli.main(['settle', str(out)]) == 0
    (out / packets.REPORT).write_text('2.1.901 | none\n')
    assert cli.main(['settle', str(out)]) == 1
    assert cli.main(['settle', str(tmp_path / 'nope')]) == 2
    capsys.readouterr()
    assert cli.main(['settle', str(out), '--hold', 'alpha.overview']) == 2
    assert capsys.readouterr() == ('', 'cc-guide: --hold goes with a verify, audit or files packet\n')
````

- [x] **Step 2: Run them to verify they fail**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3/build/cc_guide --python 3.13 --with pytest python -m pytest -q test_settle.py`
Expected: `1 error` during collection, `ModuleNotFoundError: No module named 'settle'`.

- [x] **Step 3: Write `settle.py`**

> Deviation: Task 6's review found plan-mandated defects in this code (fail-safe gaps and untested hold rules), and the final review confirmed them. Task 6 stayed open, and the owner had them fixed test-first in one wave after the final review (c335f36, f67869d, fe606b8, 16ee8ec, b970318): a failed block-row quote flags every candidate; a broken line flags the sections and blocks it names, a broken coverage line leaves its release uncovered, and a line that names nothing holds the packet; list markers are stripped; a block whose row flags another group's section holds its own group's rebaseline (the owner's design (a)); `section_at` stops at the guide's end; template and table headers are skipped; an outside-the-packet none line holds nothing; printed commands carry a non-default `--cache`; 13 isolating tests pin the hold rules. A mutation harness killed 60 of 60 mutants. The replay no longer matches `settle.py`, `packets.py` or their tests.

**Create** `build/cc_guide/settle.py`:

````python
'''`settle`: the deterministic half of a /cc-guide run (drift spec R8.4
steps 4-6, R8.8 steps 1-4, R8.10). It reads a packet's index.json beside
the verifier's report.md, parses the report's rows, re-greps every quote
(quotes.py), and prints what follows. It writes nothing but a settled
triage's settled.json in the packet; `baseline` records the outcome.

- triage fails safe: a block the report leaves out, a release with no
  coverage line and a row whose quote fails all become UNSURE, handled as
  TOUCHES. A source quote counts only within its own item's text. It names
  the sections for verify, and prints the rebaseline and advance commands
  for the rest. An owner item stops the advance below its release.
- verify, audit and files discard a row whose quote fails, a quote a row
  need not give included, and list it as unverified. Surviving corrections
  are listed to apply; JUDGMENT, NOT FOUND, omissions and not-covered rows
  are the owner's call. Each section in scope, or each cited section in
  files, needs a surviving row or a `<section> | none` line. A section is
  held, neither advanced nor audited, when it is left out, when a discarded
  row would have changed it, when a correction to it is left for the owner,
  when its triage held it, or when `--hold` names it; a file is held, not
  cited, the same way. A row outside the packet's sections holds nothing:
  the run neither reviews nor advances that section, and its triage may
  have advanced it already. A hold keeps `accept`, for the text the run
  changed.

A row's fields are split on `|`. A quote field that opens with `"` runs to
the first `"` followed by `|` or the end of the line, so a quote may hold `|`
and `"`; the last field takes the rest of the line. `-` marks an empty
field. A Markdown table's outer pipes, header rows and separator rows are
ignored. A line holding `|` that is no row is listed as unparseable, never
dropped in silence.
'''
import json
import re
import shlex
from collections.abc import Iterable
from pathlib import Path
from typing import NamedTuple

from blocks import fenced_lines
from docs import CHANGELOG, LABEL_RE, version_key
from guide import sections
from lint import CLI
from packets import BLOCKS, GUIDE, INDEX, REPORT, SETTLED, section_lines
from quotes import QuoteFiles
from state import SetupError

# The report formats, as the verifier's contract (.claude/agents/cc-guide-verifier.md)
# and the skill's references/formats.md state them; a test pins all three together.
TRIAGE_ROW = 'item | TOUCHES / NOISE / UNSURE | section | guide line | "guide quote" | "source quote" | why'
COVERAGE_ROW = 'release | sections touched, or none'
VERIFY_ROW = ('L<line> | claim ≤12 words | CONFIRMED / STALE / WRONG / PARTIAL / NOT FOUND / JUDGMENT | doc:line'
              ' | "verbatim quote ≤25 words" | proposed wording')
CHANGELOG_ROW = 'B | version | one line | changelog.md:line'
OMISSION_ROW = 'C | omission'
FILES_ROW = 'file:line | statement | section | "verbatim guide quote" | consistent / contradicts / not covered'
NONE_ROW = 'section | none'
FORMATS = (TRIAGE_ROW, COVERAGE_ROW, VERIFY_ROW, CHANGELOG_ROW, OMISSION_ROW, FILES_ROW, NONE_ROW)
# Each row's quote fields, by index: only these may hold `|` and `"`.
TRIAGE_QUOTES = (4, 5)
VERIFY_QUOTES = (4,)
FILES_QUOTES = (3,)

TRIAGE_VERDICTS = ('TOUCHES', 'NOISE', 'UNSURE')
CORRECTIONS = ('STALE', 'WRONG', 'PARTIAL')
MECHANISM = 'JUDGMENT (mechanism STALE)'
VERIFY_VERDICTS = ('CONFIRMED', *CORRECTIONS, 'NOT FOUND', 'JUDGMENT', MECHANISM)
FILES_VERDICTS = ('consistent', 'contradicts', 'not covered')
TODO = 'TODO(owner)'
LIST_ITEM_RE = re.compile(r'[ \t]*(?:[-*+]|\d+[.)])[ \t]')
# A line that opens a Markdown block of its own ends a list item's lazy continuation.
BLOCK_START_RE = re.compile(r'[ \t]*(?:[-*+][ \t]|\d+[.)][ \t]|#{1,6}[ \t]|```|~~~|>|<)')
CLOSE_QUOTE_RE = re.compile(r'"[ \t]*(?:\||$)')
SEPARATOR_RE = re.compile(r'^[\s|:-]+$')
LINE_REF_RE = re.compile(r'L(\d+)')
DOC_REF_RE = re.compile(r'(.+):(\d+)')
CHANGELOG_REF_RE = re.compile(re.escape(CHANGELOG) + r':[1-9][0-9]*')
HEADERS = ('item', 'release', 'l<line>', 'file:line', 'file line', 'section')
LEFT_OUT = 'left out (no surviving row, no none line)'


def split_row(line: str, count: int, quoted: tuple[int, ...] = ()) -> list[str] | None:
    '''A report row's first `count` fields, or None when it has fewer. A
    field at a `quoted` index that opens with `"` runs to the first `"`
    followed by `|` or the end of the line; any other field ends at the next
    `|`. The last field takes the rest of the line.'''
    s = line.strip()
    s = s[1:] if s.startswith('|') else s
    s = s[:-1] if s.endswith('|') else s
    out: list[str] = []
    i = 0
    while len(out) < count - 1:
        while i < len(s) and s[i] in ' \t':
            i += 1
        if len(out) in quoted and s.startswith('"', i):
            m = CLOSE_QUOTE_RE.search(s, i + 1)
            if m is None:
                return None
            out.append(s[i:m.start() + 1])
            i = m.end()
        else:
            j = s.find('|', i)
            if j < 0:
                return None
            out.append(s[i:j].strip())
            i = j + 1
    out.append(s[i:].strip())
    return out


def unquote(field: str) -> str:
    '''A quote field's text: its outer double quotes dropped; `-` or nothing
    is no quote.'''
    if len(field) >= 2 and field[0] == field[-1] == '"':
        return field[1:-1]
    return '' if field in ('', '-') else field


def given(field: str) -> str:
    '''A field's text, or '' when it is empty or `-`, the empty-field mark.'''
    return '' if field.strip() in ('', '-') else field.strip()


def report_lines(text: str) -> list[str]:
    '''The report's lines that may be rows: those holding `|`, less table
    separators and header rows.'''
    out = []
    for line in text.split('\n'):
        if '|' not in line or SEPARATOR_RE.match(line):
            continue
        first = (split_row(line, 2) or [''])[0].lower()
        if first not in HEADERS:
            out.append(line.strip())
    return out


def none_line(line: str) -> bool:
    '''Whether a `<section> | none` line says none.'''
    return split_row(line, 2)[1].strip().lower() == 'none'


class Packet(NamedTuple):
    folder: Path
    index: dict
    report: str
    guide: str
    ids: list[str]  # the guide's section IDs, in guide order


def read_packet(folder: Path) -> Packet:
    '''A packet's index, its guide copy and the verifier's report.md.'''
    for name in (INDEX, GUIDE, REPORT):
        if not (folder / name).is_file():
            raise SetupError(f'{folder / name}: not found; save the verifier\'s report as {REPORT} in the packet'
                             if name == REPORT else f'{folder / name}: not found; not a packet')
    index = json.loads((folder / INDEX).read_text(encoding='utf-8'))
    guide = (folder / GUIDE).read_text(encoding='utf-8')
    return Packet(folder, index, (folder / REPORT).read_text(encoding='utf-8'), guide,
                  [s.id for s in sections(guide) if s.id])


def command(*words: str) -> str:
    return CLI + ' ' + ' '.join(shlex.quote(w) for w in words)


CONFORMANCE = 'uv run --python 3.13 --with pyyaml python build/check_conformance.py'


class Settled(NamedTuple):
    lines: list[str]   # what settle prints
    clean: bool        # every row parsed and every quote was found, nothing discarded or left out
    saved: dict | None  # settled.json, for a triage


# ---- triage (R8.4 steps 4-6) ----------------------------------------------

class Tally:
    '''A triage report read row by row: the sections each item sends to
    verify, why, and what the report got wrong or left out.'''

    def __init__(self, p: Packet):
        self.p = p
        self.files = QuoteFiles(p.folder)
        self.blocks = {b['item']: b for b in p.index['blocks']}
        self.releases = {r['label']: r for r in p.index['releases']}
        self.bullets = {b['item']: b for r in p.index['releases'] for b in r['bullets']}
        self.release_of = {b['item']: r['label'] for r in p.index['releases'] for b in r['bullets']}
        self.flags: dict[str, list[str]] = {}     # section -> why it goes to verify, as settle prints it
        self.evidence: dict[str, list[str]] = {}  # section -> the same, with each row and item, for the verify packet
        # (release or None, text): an owner item with a release caps the advance below it
        self.owner: list[tuple[str | None, str]] = [(None, o) for o in p.index['owner']]
        self.notes: list[str] = []
        self.answered: set[str] = set()
        self.covered: dict[str, list[str]] = {}
        self.failed = self.unparseable = 0

    def named(self, item: str) -> str:
        if item in self.blocks:
            return f"{item}, block {self.blocks[item]['ref']}"
        return f"{item}, bullet \"{self.bullets[item]['text']}\""

    def flag(self, sid: str, why: str, detail: str) -> None:
        self.flags.setdefault(sid, []).append(why)
        self.evidence.setdefault(sid, []).append(detail)

    def broken(self, line: str, kind: str) -> None:
        self.notes.append(f'unparseable {kind}: {line}')
        self.unparseable += 1

    def fallback(self, item: str, why: str, line: str) -> None:
        '''A bullet whose row says nothing safe goes to verify for each
        section its terms hint at, or is an owner item when they hit none.'''
        hints = self.bullets[item]['hints']
        for hint in hints:
            self.flag(hint, f'{item}: {why}', f'{self.named(item)}: {why}: {line}')
        if not hints:
            self.owner.append((self.release_of[item], f"{item}: {why}, and its bullet hits no section's terms"))

    def source_found(self, item: str, quote: str) -> bool:
        '''A source quote counts only within its own item: a block's text in
        blocks.md, by the lines its index entry names, or a bullet's text.'''
        if not quote:
            return False
        if item in self.bullets:
            return quote in self.bullets[item]['text']
        lines = self.files.lines(BLOCKS) or []
        return any(quote in lines[n - 1] for first, last in self.blocks[item]['lines']
                   for n in range(first, min(last, len(lines)) + 1))

    def coverage(self, label: str, line: str) -> None:
        rest = split_row(line, 2)[1]
        listed = [s.strip() for s in rest.split(',')] if rest.strip().lower() != 'none' else []
        if '|' in rest or any(s not in self.p.ids for s in listed):
            self.broken(line, 'coverage line')
            return
        self.covered[label] = listed
        for sid in listed:
            self.flag(sid, f'{label}: its coverage line names it', f'{label}: its coverage line names it')

    def row(self, item: str, line: str) -> None:
        row = split_row(line, 7, TRIAGE_QUOTES) if item in self.blocks or item in self.bullets else None
        verdict = row[1].upper() if row else ''
        sid = given(row[2]) if row else ''
        if not (row is not None and verdict in TRIAGE_VERDICTS
                and (sid in self.p.ids or (verdict == 'NOISE' and not sid))
                and (verdict != 'NOISE' or given(row[6]))):
            self.broken(line, 'row')
            if item in self.bullets:  # a bullet's row is optional, so a broken one falls back to its hints
                self.fallback(item, 'its row does not parse', line)
            return
        self.answered.add(item)
        guide_ok = self.files.find_any(self.p.index['quotes']['guide'], unquote(row[4])) is not None
        source_ok = self.source_found(item, unquote(row[5]))
        if verdict == 'NOISE':
            # A NOISE row's failed quote, its source quote or a guide quote it
            # gives, never clears its item: UNSURE for its section and every
            # candidate or hint.
            if not source_ok or (unquote(row[4]) and not guide_ok):
                self.failed += 1
                self.notes.append(f'quote not found, NOISE becomes UNSURE: {line}')
                why = f"its NOISE row's {'guide' if source_ok else 'source'} quote was not found"
                if sid:
                    self.flag(sid, f'{item}: {why}', f'{self.named(item)}: {why}: {line}')
                if item in self.blocks:
                    for target in self.blocks[item]['candidates']:
                        if target != sid:
                            self.flag(target, f'{item}: {why}', f'{self.named(item)}: {why}: {line}')
                elif not sid or self.bullets[item]['hints']:
                    self.fallback(item, why, line)
            return
        if not (guide_ok and source_ok):
            self.failed += 1
            self.notes.append(f'quote not found, {verdict} becomes UNSURE: {line}')
        self.flag(sid, f'{item}: {verdict}' + ('' if guide_ok and source_ok else ', quote not found'),
                  f'{self.named(item)}: {line}')

    def fail_safe(self) -> list[str]:
        '''Silence never counts as NOISE: each block with no row and each
        release with no coverage line goes to verify. Returns them.'''
        for item, b in self.blocks.items():
            if item not in self.answered:
                for sid in b['candidates']:
                    self.flag(sid, f'{item}: no row', f'{self.named(item)}: no row')
        for label, r in self.releases.items():
            if label in self.covered:
                continue
            for sid in r['hits']:
                hinting = '; '.join(f"\"{b['text']}\"" for b in r['bullets'] if sid in b['hints'])
                self.flag(sid, f'{label}: no coverage line',
                          f'{label}: no coverage line; its bullets that hint at it: {hinting}')
            if not r['hits']:
                self.owner.append((label, f"{label}: no coverage line, and its bullets hit no section's terms"))
        return [i for i in self.blocks if i not in self.answered] + [r for r in self.releases if r not in self.covered]


def settle_triage(p: Packet) -> Settled:
    t = Tally(p)
    for line in report_lines(p.report):
        first = (split_row(line, 2) or [''])[0]
        if first in t.releases:
            t.coverage(first, line)
        else:
            t.row(first, line)
    omitted = t.fail_safe()
    index, order = p.index, p.ids
    verify = sorted(t.flags, key=order.index)
    held = set(index['held'])
    capped = [release for release, _ in t.owner if release is not None]
    labels = sorted(t.releases, key=version_key)
    if capped:
        oldest = min(capped, key=version_key)
        labels = [label for label in labels if version_key(label) < version_key(oldest)]
    target = labels[-1] if labels else None
    advance = [sid for sid in order if sid not in t.flags and sid not in held
               and any(sid in t.releases[label]['pending'] for label in labels)]
    rebaseline = {gid: [b['ref'] for b in index['blocks'] if b['group'] == gid]
                  for gid, sids in index['groups'].items()
                  if any(b['group'] == gid for b in index['blocks'])
                  and not any(s in t.flags or s in held for s in sids)}
    scope = {sid for b in index['blocks'] for sid in b['candidates']} | {
        sid for r in index['releases'] for sid in r['pending']}
    cleared = [sid for sid in order if sid in scope and sid not in t.flags and sid not in held]

    out = [f'cc-guide settle: triage, {p.folder}',
           f'report: {len(t.answered)} item(s) answered, {len(t.covered)} of {len(t.releases)} release(s) covered; '
           f'{t.failed} quote(s) not found; {t.unparseable} unparseable line(s); {len(omitted)} left out']
    out += [f'  {n}' for n in t.notes]
    out += [f'UNSURE or TOUCHES {sid}: ' + '; '.join(t.flags[sid]) for sid in verify]
    out += [f'owner: {o}' for _, o in t.owner]
    if held:
        out.append(f"held, never advanced here: {' '.join(sorted(held, key=order.index))}")
    steps = [command('baseline', 'rebaseline', gid, *refs) for gid, refs in rebaseline.items()]
    if advance and target:
        steps.append(command('baseline', 'advance', *advance, '--to', target))
    if steps:
        out.append('then, in this order (R8.8):')
        out += [f'  {s}' for s in [*steps, command('baseline', 'stamp'), command('lint'), CONFORMANCE]]
    else:
        out.append('nothing to record')
    if verify:
        out.append(f"verify: /cc-guide verify {' '.join(verify)}; or defer it, and those sections do not advance, "
                   'so the next triage shows them again')
    if index.get('next_through'):
        out.append('next range, once these commands are run: '
                   + command('packets', '--triage', '--through', index['next_through']))
    saved = {'mode': 'triage', 'advance_to': target, 'verify': verify, 'cleared': cleared,
             'held': sorted(held, key=order.index), 'rows': {sid: t.evidence[sid] for sid in verify}}
    return Settled(out, not t.failed and not t.unparseable and not omitted, saved)


# ---- verify and audit (R8.5, R8.6, R8.8) ------------------------------------

def section_at(p: Packet, line: int) -> str | None:
    '''The section whose lines hold a guide line, by the ranges the packet
    gives its verifier; None before the first section or past the end.'''
    return next((sid for sid, (first, last) in section_lines(p.guide).items() if first <= line <= last), None)


def todo_reaches(guide: str) -> list[tuple[int, int]]:
    '''R8.5: each TODO(owner)'s reach, 1-based and inclusive. The guide's
    one TODO names "the first bullet below", so a TODO reaches from its own
    line through the first list item after it outside fenced code, with its
    continuation lines and nested content, or to the end of its section when
    no list item follows; never past its section. A TODO in fenced code is
    an example, not one.'''
    lines = guide.split('\n')
    fenced = fenced_lines(lines)  # 0-based
    ends = [last for first, last in section_lines(guide).values()]
    starts = [first for first, last in section_lines(guide).values()]
    out = []
    for n, text in enumerate(lines, start=1):
        if TODO not in text or n - 1 in fenced:
            continue
        end = next((e for s, e in zip(starts, ends) if s <= n <= e), None)
        if end is None:
            continue
        item = next((m for m in range(n + 1, end + 1)
                     if m - 1 not in fenced and LIST_ITEM_RE.match(lines[m - 1])), None)
        if item is None:
            out.append((n, end))
            continue
        indent = len(lines[item - 1]) - len(lines[item - 1].lstrip())
        last, blank = item, False
        for m in range(item + 1, end + 1):
            s = lines[m - 1]
            if not s.strip():
                blank = True
                continue
            deeper = len(s) - len(s.lstrip()) > indent
            if not (deeper or (not blank and not BLOCK_START_RE.match(s))):
                break
            last, blank = m, False
        out.append((n, last))
    return out


def settle_review(p: Packet, hold: tuple[str, ...]) -> Settled:
    '''verify and audit: R8.5's A/B/C report under R8.8's discard rule.'''
    index = p.index
    scope, cleared = index['sections'], index.get('cleared', [])
    files = QuoteFiles(p.folder)
    docs = [QuoteFiles(Path(root)) for root in index['quotes']['docs']]
    reaches = todo_reaches(p.guide)

    def found(ref_field: str, quote: str) -> bool:
        '''A doc quote counts in the packet's changelog.md or a page of the
        snapshot, never in the report, the guide copy or the index.'''
        ref = DOC_REF_RE.fullmatch(ref_field)
        if ref is None or not quote:
            return False
        if ref.group(1) in index['quotes']['changelog']:
            return files.find(ref.group(1), quote) is not None
        return any(d.find(ref.group(1), quote) is not None for d in docs)

    corrections, owner, unverified, changelog = [], [], [], []
    confirmed = 0
    held = set(index.get('held', [])) | set(hold)
    answered: set[str] = set()
    whole_held = False

    def hold_inside(sid: str) -> None:
        '''A row holds its section only inside the packet's sections: the run
        neither reviews nor advances any other, and its triage may have
        advanced it already.'''
        if sid in scope:
            held.add(sid)

    for line in report_lines(p.report):
        first = (split_row(line, 2) or [''])[0]
        if first == 'B':
            row = split_row(line, 4)
            if row is None or not (LABEL_RE.fullmatch(given(row[1])) and given(row[2])
                                   and CHANGELOG_REF_RE.fullmatch(row[3])):
                unverified.append(f'unparseable: {line}')
            else:
                changelog.append(' | '.join(row[1:]))
            continue
        if first == 'C':
            omission = given(split_row(line, 2)[1])
            if omission:
                owner.append(f'omission: {omission}')
            else:
                unverified.append(f'unparseable: {line}')
            continue
        if first in p.ids:  # `<section> | none`: the section holds no checkable claim
            if first in scope and none_line(line):
                answered.add(first)
            else:
                unverified.append(f'unparseable: {line}')
                if first in scope:
                    held.add(first)
            continue
        m = LINE_REF_RE.fullmatch(first)
        row = split_row(line, 6, VERIFY_QUOTES) if m else None
        verdict = row[2].upper().replace('(MECHANISM STALE)', '(mechanism STALE)') if row else ''
        n = int(m.group(1)) if m else 0
        sid = section_at(p, n) if m else None
        if row is None or verdict not in VERIFY_VERDICTS or sid is None:
            unverified.append(f'unparseable: {line}')
            if sid is None:
                whole_held = True
            else:
                hold_inside(sid)
            continue
        quote, wording = unquote(row[4]), given(row[5])
        if (quote or verdict not in ('NOT FOUND', 'JUDGMENT')) and not found(row[3], quote):
            unverified.append(f'quote not found, discarded: {line}')
            if verdict in (*CORRECTIONS, MECHANISM):
                hold_inside(sid)
            continue
        if verdict in CORRECTIONS and not wording:
            unverified.append(f'no proposed wording, discarded: {line}')
            hold_inside(sid)
            continue
        answered.add(sid)
        where = f'L{n} {sid} {verdict}'
        near = any(a <= n <= b for a, b in reaches)
        if verdict == 'CONFIRMED':
            confirmed += 1
        elif verdict in CORRECTIONS and sid not in scope:
            owner.append(f"{where} (outside this packet's sections, so it holds nothing; /cc-guide verify {sid} "
                         f'reviews it): {row[1]} → {wording}')
        elif verdict in CORRECTIONS and not near:
            corrections.append((sid, f'{where}: {row[1]} → {wording} ({row[3]}: "{quote}")'))
        elif verdict in CORRECTIONS:  # listed for the owner, so it holds its section
            owner.append(f'{where} (next to a TODO(owner), report-only): {row[1]} → {wording}')
            held.add(sid)
        else:
            owner.append(f'{where}: {row[1]}' + (f' ({row[3]}: "{quote}")' if quote else ''))
            if verdict == MECHANISM:  # a judgment whose mechanism moved waits for the owner
                hold_inside(sid)
    if whole_held:
        held |= set(scope)
    left = [sid for sid in scope if sid not in answered]
    held |= set(left)
    fixed = list(dict.fromkeys(sid for sid, _ in corrections))
    resolved = {sid for sid in [*scope, *cleared] if sid not in held}
    ready = [b for b in index['blocks'] if set(b['candidates']) <= resolved]
    # baseline rebaselines a page's changed and missing blocks together, so a
    # page that keeps one unresolved waits whole (R7)
    waiting = {b['page'] for b in index['blocks'] if b['kind'] != 'new' and b not in ready}
    refs = [b['ref'] for b in ready if b['page'] not in waiting]
    mode = index['mode']
    out = [f"cc-guide settle: {mode} {index['group']}, {p.folder}",
           f'report: {confirmed} confirmed, {len(corrections)} correction(s), {len(owner)} owner\'s call, '
           f'{len(unverified)} unverified']
    out += ['corrections, to apply to the guide in the working tree:'] + [f'  {c}' for _, c in corrections]
    out += ["owner's call, never applied:"] + [f'  {o}' for o in owner]
    out += ['unverified, discarded:'] + [f'  {u}' for u in unverified]
    out += ['changelog items (B):'] + [f'  {c}' for c in changelog]
    if left:
        out.append(f"{LEFT_OUT}, so held: {' '.join(left)}")
    shown = [sid for sid in scope if sid in held]
    if shown:
        out.append(f"held, neither advanced nor audited: {' '.join(shown)}")
    steps = []
    if fixed:
        steps.append(command('baseline', 'accept', *fixed, '--substantive') + '   # only the sections you changed')
    if refs:
        steps.append(command('baseline', 'rebaseline', index['group'], *refs))
    # a section checked past the triage's target is not advanced backwards
    target, checked = index.get('advance_to'), index.get('checked', {})
    advance = [sid for sid in scope if sid not in held
               and not (target and sid in checked and version_key(checked[sid]) > version_key(target))]
    if mode == 'audit' and not any(sid in held for sid in scope):
        steps.append(command('baseline', 'audited', index['group']))
    elif mode == 'verify' and target and advance:
        steps.append(command('baseline', 'advance', *advance, '--to', target))
    steps += [command('baseline', 'stamp'), command('lint'), CONFORMANCE]
    out.append('then, in this order (R8.8), once every correction is applied; for one you leave for the owner, '
               'settle again with --hold <section>, which holds the section and keeps its accept:')
    out += [f'  {s}' for s in steps]
    out.append('a correction that resolves a conformance gap removes its [[exception]] from '
               'build/cc_guide/conformance.toml in the same change; lint\'s STALE lines then name the citing files '
               'of each section whose `changed` moved')
    return Settled(out, not unverified and not left, None)


# ---- files (R8.7, R8.8) -----------------------------------------------------

def settle_files(p: Packet, hold: tuple[str, ...]) -> Settled:
    index = p.index
    files = QuoteFiles(p.folder)
    path = index['file']
    fixes, owner, unverified = [], [], []
    consistent = 0
    answered: set[str] = set()
    discarded = False
    for line in report_lines(p.report):
        first = (split_row(line, 2) or [''])[0]
        if first in index['sections']:  # `<section> | none`: no statement in the file rests on it
            if none_line(line):
                answered.add(first)
            else:
                unverified.append(f'unparseable: {line}')
                discarded = True
            continue
        row = split_row(line, 5, FILES_QUOTES)
        ref = DOC_REF_RE.fullmatch(row[0]) if row else None
        verdict = row[4].strip().lower() if row else ''
        if ref is None or ref.group(1) != path or verdict not in FILES_VERDICTS or row[2] not in index['sections']:
            unverified.append(f'unparseable: {line}')
            discarded = True
            continue
        quote = unquote(row[3])
        if (quote or verdict != 'not covered') and files.find_any(index['quotes']['guide'], quote) is None:
            unverified.append(f'quote not found, discarded: {line}')
            discarded = discarded or verdict == 'contradicts'
            continue
        answered.add(row[2])
        if verdict == 'consistent':
            consistent += 1
        elif verdict == 'contradicts':
            fixes.append(f'{row[0]} ({row[2]}): {row[1]} (guide: "{quote}")')
        else:
            owner.append(f'{row[0]} ({row[2]}, not covered; a coverage gap?): {row[1]}')
    left = [sid for sid in index['sections'] if sid not in answered]
    reasons = (['a discarded or unparseable row might have changed it'] if discarded else []) + (
        ['a cited section was left out'] if left else []) + (['held by --hold'] if hold else [])
    out = [f'cc-guide settle: files {path}, {p.folder}',
           f'report: {consistent} consistent, {len(fixes)} contradiction(s), {len(owner)} not covered, '
           f'{len(unverified)} unverified']
    out += [f'contradictions, to fix in {path} in the working tree:'] + [f'  {f}' for f in fixes]
    out += ["owner's call, never applied:"] + [f'  {o}' for o in owner]
    out += ['unverified, discarded:'] + [f'  {u}' for u in unverified]
    if left:
        out.append(f"{LEFT_OUT}: {' '.join(left)}")
    steps = [command('lint'), CONFORMANCE]
    if reasons:
        out.append(f"held, not cited: {path}: {'; '.join(reasons)}")
    else:
        steps.insert(0, command('baseline', 'cite', path))
    out.append(f'then, in this order (R8.8), once every contradiction is fixed in {path}, unless '
               'build/cc_guide/conformance.toml records it as a deviation, which stays as it is; for one you leave '
               f'for the owner, settle again with --hold {path}, which skips its cite:')
    out += [f'  {s}' for s in steps]
    return Settled(out, not unverified and not left, None)


def settle(folder: Path, hold: Iterable[str] = ()) -> Settled:
    '''Settle the packet in folder against its report.md. A triage also
    writes settled.json there, which `packets --verify --from` reads.
    `hold` names the sections, or the file, the session leaves for the
    owner: they are held as a discarded correction holds them.'''
    p = read_packet(folder)
    mode = p.index.get('mode')
    hold = tuple(dict.fromkeys(hold))
    if mode == 'triage':
        if hold:
            raise SetupError('--hold goes with a verify, audit or files packet')
        result = settle_triage(p)
        (folder / SETTLED).write_text(json.dumps(result.saved, indent=1) + '\n', encoding='utf-8')
        return result
    if mode in ('verify', 'audit'):
        unknown = [h for h in hold if h not in p.index['sections']]
        if unknown:
            raise SetupError(f"--hold {' '.join(unknown)}: not a section this packet reviews "
                             f"({', '.join(p.index['sections'])})")
        return settle_review(p, hold)
    if mode == 'files':
        other = [h for h in hold if h != p.index['file']]
        if other:
            raise SetupError(f"--hold {' '.join(other)}: a files packet holds only its file, {p.index['file']}")
        return settle_files(p, hold)
    raise SetupError(f'{folder / INDEX}: unknown mode {mode!r}')
````

- [x] **Step 4: Wire `settle` into the CLI**

> Deviation: the owner approved `baseline audited GROUP --to RELEASE` (2026-10-13; fe606b8), refusing a release the newest cached changelog lacks as `advance` does, so settle prints `audited <group> --to <head>` and an audit is recorded at the release its packet reviewed, not the cache's newest. `baseline.py` is unchanged.

**Edit** `build/cc_guide/cli.py` — replace:

```python
      file under DIR (R8.3). Exit 0 when all are found, 1 on any miss.
```

with:

```python
      file under DIR (R8.3). Exit 0 when all are found, 1 on any miss.
  settle DIR [--hold ID | FILE ...]
      Settle a packet against the verifier's report, saved as DIR/report.md:
      re-grep every quote, apply triage's completeness rules or the discard
      rule, and print the corrections, the owner's-call items and the
      baseline commands that follow, in R8.8's order. --hold names the
      sections, or the file, the session leaves for the owner: they are held,
      neither advanced, audited nor cited. Writes nothing but a settled
      triage's DIR/settled.json. Exit 0 when every row parsed and every quote
      was found, with nothing discarded or left out; 1 otherwise; 2 on an
      error.
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
from quotes import check_rows
```

with:

```python
from quotes import check_rows
from settle import settle
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
    sub.add_parser('quotes').add_argument('--in', dest='root', type=Path, required=True)
```

with:

```python
    sub.add_parser('quotes').add_argument('--in', dest='root', type=Path, required=True)
    s = sub.add_parser('settle')
    s.add_argument('folder', type=Path)
    s.add_argument('--hold', nargs='+', default=[], metavar='ID')
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
def main(argv=None, *, today: date | None = None, now: datetime | None = None, fetch=None) -> int:
```

with:

```python
def run_settle(args) -> int:
    result = settle(args.folder, args.hold)
    print('\n'.join(result.lines))
    return 0 if result.clean else 1


def main(argv=None, *, today: date | None = None, now: datetime | None = None, fetch=None) -> int:
```

**Edit** `build/cc_guide/cli.py` — replace:

```python
        if args.command == 'quotes':
            return run_quotes(args)
```

with:

```python
        if args.command == 'quotes':
            return run_quotes(args)
        if args.command == 'settle':
            return run_settle(args)
```

- [x] **Step 5: Run the suite to verify it passes**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3/build/cc_guide --python 3.13 --with pytest python -m pytest -q`
Expected: all pass, +99 over the baseline.

- [x] **Step 6: Commit**

Confirm the branch, then:

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 add build/cc_guide/settle.py build/cc_guide/test_settle.py build/cc_guide/cli.py
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 commit -m "feat(cc_guide): settle applies the fail-safe and discard rules to a verifier's report (R8.10)" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: The skill, the verifier and the docs (R8.1, R12.4, R12.7)

**Files:**
- Create: `build/cc_guide/test_skill_files.py`
- Create: `.claude/agents/cc-guide-verifier.md`, `.claude/skills/cc-guide/SKILL.md`, `.claude/skills/cc-guide/references/formats.md`
- Modify: `build/CLAUDE.md` (the `cc_guide/` paragraph), `CLAUDE.md` (the drift detector's comment line)

**Interfaces:**
- Consumes: Task 6's `settle.FORMATS`; `guide.file_citation`.
- Produces: `/cc-guide` (typed only) and the `cc-guide-verifier` agent (Sonnet; `Read, Grep, Glob`; no CLAUDE.md), whose contract states the seven formats verbatim.

The skill's description quotes its trigger phrases (`trigger-phrase-presence`). Its body escapes each `$` before a digit (`\$0.05`), because the `substitution-hazard` check reads `$0` as a positional argument. The agent's body has no `## Read-only contract` heading, which would put it in the read-only guard's roster semantics; without Bash it needs none (R8.1).

- [x] **Step 1: Write the failing tests**

**Create** `build/cc_guide/test_skill_files.py`:

```python
'''The /cc-guide skill and its verifier (drift spec R8.1, R12.4): each file
opens with its frontmatter and carries its citation as the frontmatter's
last line, the frontmatter sets what R8.1 names, and the report formats the
skill and the verifier state are the ones settle parses. The suite has no
YAML parser, so frontmatter lines are compared as text.'''
from pathlib import Path

import pytest

import guide
import settle
from cc_fixtures import isolated_home  # noqa: F401

REPO = Path(__file__).resolve().parents[2]
SKILL = '.claude/skills/cc-guide/SKILL.md'
AGENT = '.claude/agents/cc-guide-verifier.md'
FORMATS = '.claude/skills/cc-guide/references/formats.md'


def frontmatter(path: str) -> list[str]:
    '''The frontmatter's lines. check_frontmatter.py never reads .claude/,
    so this is the only check that the frontmatter opens the file.'''
    lines = (REPO / path).read_text(encoding='utf-8').split('\n')
    assert lines[0] == '---', f'{path} must open with its frontmatter'
    return lines[1:lines.index('---', 1)]


@pytest.mark.parametrize('path', [SKILL, AGENT])
def test_each_file_cites_the_guide_on_its_frontmatters_last_line(path):
    text = (REPO / path).read_text(encoding='utf-8')
    citation, problems = guide.file_citation(path, text)
    assert problems == []
    assert citation is not None and citation.line == len(frontmatter(path)) + 1


def test_the_skill_is_typed_only():
    assert {'name: cc-guide', 'disable-model-invocation: true'} <= set(frontmatter(SKILL))


def test_the_verifier_runs_on_sonnet_with_read_only_search_tools_and_no_claude_md():
    assert {'name: cc-guide-verifier', 'tools: Read, Grep, Glob', 'model: sonnet',
            'omitClaudeMd: true'} <= set(frontmatter(AGENT))


def test_the_verifier_reports_a_todo_reach_with_its_usual_verdict():
    '''Second review, finding 2: settle lists a correction within a
    TODO(owner)'s reach for the owner and holds its section, so the verifier
    keeps its STALE, WRONG or PARTIAL there rather than turning it into a
    JUDGMENT that holds nothing.'''
    (rule,) = [line for line in (REPO / AGENT).read_text(encoding='utf-8').split('\n') if 'TODO(owner)' in line]
    assert 'usual verdict' in rule and 'JUDGMENT' not in rule


@pytest.mark.parametrize('form', settle.FORMATS)
def test_the_skill_and_the_verifier_state_the_report_formats_settle_parses(form):
    for path in (AGENT, FORMATS):
        assert form in (REPO / path).read_text(encoding='utf-8'), f'{path} lacks {form!r}'
```

- [x] **Step 2: Run them to verify they fail**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3/build/cc_guide --python 3.13 --with pytest python -m pytest -q test_skill_files.py`
Expected: `12 failed`, every one a `FileNotFoundError` for `.claude/agents/cc-guide-verifier.md` (10, seven of them the format cases) or `.claude/skills/cc-guide/SKILL.md` (2).

- [x] **Step 3: Write the verifier**

**Create** `.claude/agents/cc-guide-verifier.md`:

```markdown
---
name: cc-guide-verifier
description: Checks this repo's Claude Code guide against the docs, from a packet the /cc-guide skill builds. Only /cc-guide dispatches it.
tools: Read, Grep, Glob
model: sonnet
omitClaudeMd: true
# cc-guide: subagents.frontmatter subagents.tools subagents.models @2.1.296
---

You check `specs/guides/claude-code-customization-guide.md`, the guide, against the Claude Code docs, working from a packet that /cc-guide built. You read files and return one report. You never edit, write or create a file.

## Start

The dispatch names your mode and the packet directory. Read the packet's `index.json` first: it names the mode, the items you answer for and the files you may quote. The packet's `guide.md` is the guide copied whole, so its line numbers are the guide's.

## Accuracy

- A quote is copied character for character from one line of the file it comes from: never across two lines, never tidied, at most 25 words. A script re-greps every quote, an optional one too when you give it. In triage a row whose quote it cannot find becomes UNSURE; in every other mode the row is discarded.
- Quote only the files the row names: never this packet's `index.json`, nor a report.
- Proposed wording is your own paraphrase, never a sentence from the docs. `-` proposes nothing.
- Absence of evidence is NOT FOUND, never WRONG.
- A claim is checkable when a doc page could confirm or refute it: names, defaults, numbers, behaviour, precedence, syntax. A recommendation is JUDGMENT and gets no proposed wording. When a judgment rests on a mechanism, check the mechanism; if it moved, report `JUDGMENT (mechanism STALE)` with its quote.
- A `TODO(owner)` is report-only from its own line through the first list item after it outside fenced code, that item's continuation lines included, or to the end of its section when no list item follows: report what you find there with its usual verdict, and settle lists it for the owner.

## The report

Return only the report. Every row is one line, its fields separated by ` | `, each quote inside double quotes, `-` for an empty field. Put `|` in no other line.

### triage

`blocks.md` holds each changed, missing or new docs block (B1, B2, ...) with its candidate sections. `releases.md` holds every bullet of each untriaged release, numbered `<release>#<n>`, with the sections its terms hint at.

Give every block at least one row, and one row per section it touches. Give a bullet a row only when it touches a section or might. Give every release one coverage line.

    item | TOUCHES / NOISE / UNSURE | section | guide line | "guide quote" | "source quote" | why
    release | sections touched, or none

- TOUCHES: the item changes what a guide claim should say. UNSURE: it might. NOISE: it changes no claim; its section, guide line and guide quote may be `-`, but it needs its source quote and its why.
- The guide quote comes from `guide.md`. The source quote comes from the item's own text: a block's text in `blocks.md`, or the bullet's text in `releases.md`, never another item's or the packet's own headings.
- Hints are only hints: a bullet that touches a section its hints miss still gets a row.
- A coverage line names sections comma-separated, as in `2.1.297 | rules.settings, hooks.pitfalls`, or says `none`.

A block with no row, and a release with no coverage line, go to verify as UNSURE: silence never counts as NOISE.

### verify and audit

`sections.md` names the sections to check and their guide lines; in verify it also carries the triage rows that sent each one. `blocks.md` holds the group's block findings, `changelog.md` the changelog, and the directory `index.json` names as `docs` holds the group's pages. Check every claim in those guide lines; an audit checks every section of its group against all its pages and the releases in `releases.md`. Report three parts, and a none line for each section with no checkable claim:

    L<line> | claim ≤12 words | CONFIRMED / STALE / WRONG / PARTIAL / NOT FOUND / JUDGMENT | doc:line | "verbatim quote ≤25 words" | proposed wording
    B | version | one line | changelog.md:line
    C | omission
    section | none

- A, one row per claim. `doc:line` names a page file in the `docs` directory, such as `hooks.md:426`, or `changelog.md` in the packet; a doc quote comes from one of those, never from `guide.md`. Proposed wording only for STALE, WRONG and PARTIAL, `-` otherwise. NOT FOUND and JUDGMENT may leave `doc:line` and the quote `-`.
- Every section in `sections.md` gets at least one A row, or `<section> | none` when it holds no checkable claim. A section with neither is held, as if unreviewed.
- B, one row per changelog item that changes a claim in scope.
- C, at most four rows: omissions that would change the guide's existing advice.

### files

The cited file's copy is the file `index.json` names as `copy`; its line numbers are the file's. `sections.md` holds the sections it cites, each marked when it changed after the file's stamp. Give one row per statement in the file that rests on a cited section, and a none line for each cited section no statement rests on:

    file:line | statement | section | "verbatim guide quote" | consistent / contradicts / not covered
    section | none

`file` is the path `index.json` names as `file`, as in `hooks/README.md:56`. A not-covered row may leave its quote `-`. A cited section with no row and no none line holds the file, as if unreviewed.
```

- [x] **Step 4: Write the skill and its formats reference**

> Deviation: the fix wave amended `references/formats.md` (Packets' `cache` key; Reports' list of lines dropped without listing; "What settle does with a report"; Bookkeeping's capped `advance_to` and `audited --to`) and `SKILL.md` (the audit paragraph, and "that file and statement" for R8.8 step 2).

**Create** `.claude/skills/cc-guide/SKILL.md`:

```markdown
---
name: cc-guide
description: >
  Use when acting on what this repo's Claude Code drift check reports about
  specs/guides/claude-code-customization-guide.md: "triage the changelog",
  "verify these guide sections", "audit a group", "review the stale citations",
  or a check summary that names releases untriaged, changed docs blocks, an
  audit due or stale citing files.
argument-hint: 'triage | verify <ids> | audit [<group>] | files [<paths>]'
disable-model-invocation: true
# cc-guide: skills.frontmatter skills.arguments subagents.isolation @2.1.296
---

# /cc-guide

Acts on what `check` reports for `specs/guides/claude-code-customization-guide.md`, the guide. Each mode builds packets, dispatches the `cc-guide-verifier` agent on them, and settles every report with a script before anything is applied. The design is `specs/claude-code-drift-automation-spec.md`, R8; `references/formats.md` holds the packet layout and the report formats.

`cli.py` below stands for `uv run --python 3.13 python build/cc_guide/cli.py`, run from the repo root.

## Ground rules

- Nothing is committed. Corrections, bookkeeping and stamps stay in the working tree for the owner to review as a diff.
- Run in a worktree on its own branch, cut from current `main`, never in the shared checkout: every mode can edit the guide, `build/cc_guide/baseline.json` and citing files. The commands read the working tree.
- Packets live under `~/.cache/agent-skills/cc-guide/packets/` and hold docs text: copy nothing from them into the repo. Quotes go only into the report to the owner.
- Never paste a packet into a dispatch prompt; name its directory, and the verifier reads it.
- State the number of verifiers before dispatching. Above 6, ask the owner first or take a subset.
- Apply only what settle lists as a correction or a contradiction, and never an owner's-call item. Edit only the guide in verify and audit, and only the reviewed file in files. Two follow-ons belong to the same fix: removing or narrowing the `[[exception]]` it resolves in `build/cc_guide/conformance.toml` (After any mode), and, for a canonical agent or command, regenerating `runtimes/` with `uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py`. A fix that would reach any other file is the owner's call.
- A listed item you leave for the owner, because it needs a decision (R11.5's #1 and #2) or would reach another file, holds its section or file: run `cli.py settle <packet> --hold <section or file>`, and run the commands it prints in place of the first ones.
- In files, a contradiction that `build/cc_guide/conformance.toml` records as a `deviation` for that file, in that section, is the owner's standing decision: leave it as it is, and it holds nothing. One the register records as a `gap` is still open, so it holds the file. A deviation covers only the statement its `guide` line names; any other contradiction in the file is handled as if no entry named it.

## Pick the mode

The typed words arrive on the ARGUMENTS line: `triage`, `verify <ids>`, `audit [<group>]` or `files [<paths>]`. With none, run `cli.py check --worktree` and offer the mode its due items call for. Probes arrive with Stage 5.

## Dispatch, save, settle

Every mode handles each packet the same way:

1. Dispatch the Agent tool with subagent type `cc-guide-verifier` and the prompt `Mode: <mode>. Packet: <absolute packet directory>. Read its index.json first, then follow your contract and return only the report.` Dispatch several packets in one message, so they run in parallel.
2. Save the verifier's reply, unchanged, as `report.md` in its packet directory, with the Write tool.
3. Run `cli.py settle <packet directory>`. Exit 0: every row parsed, every quote was found, and nothing was discarded or left out. Exit 1: settle failed something safe; read its UNSURE, unverified, unparseable and left-out lines. Exit 2: a setup error to fix before going on. What settle held or discarded stands: never edit `report.md`, ask the verifier to reword a row, or read settle's code to get past it. Report it to the owner; the next run takes it up again.
4. Run the commands settle prints, in the order it prints them.

## triage

1. Run `cli.py check --worktree`. Exit 2 is an error to fix first.
2. Run `cli.py packets --triage`. "nothing to triage" ends the mode. Above 20 untriaged releases after the newest checked one, it refuses and names the `--through` of the first range of 20: build that one.
3. Dispatch one verifier, about \$0.05–0.20, then save and settle.
4. Settle's `verify:` line names the sections a TOUCHES or UNSURE row sent on. Verify them now with `cli.py packets --verify --from <triage packet directory>`, which takes those sections, or tell the owner they are deferred: they do not advance, so the next triage shows them again.
5. Settle's `owner:` lines go to the owner. Its advance stops below the oldest release one names.
6. A ranged triage's settle ends with `next range`. Once its commands have run and its verify is done or deferred, build that range the same way.

## verify <ids>

1. Run `cli.py check --worktree`, unless a triage in this run just did.
2. Run `cli.py packets --verify <ids>`. It writes one packet per group, about \$0.30–1 each.
3. Dispatch, save and settle each.
4. Apply each correction settle lists to the guide in the working tree, checking it against its quote. Then run settle's commands: `accept --substantive` only for the sections whose text you changed (lint names any you missed), then rebaseline, advance, stamp, lint and `check_conformance.py`.

## audit [<group>]

As verify, from `cli.py check --worktree` and then `cli.py packets --audit [<group>]`: no group means the due one, and packets refuses when none is due. It costs about \$2.50–5.30, and settle's commands end with `baseline audited <group>` in place of advance.

## files [<paths>]

1. Run `cli.py packets --files [<paths>]`: no paths means the stale backlog. It writes one packet per file; dispatch them in batches under the ask-above-6 rule.
2. For each, settle, then fix each contradiction it lists, in that file only, and run its commands. `baseline cite <file>` runs only for a file settle does not hold: settle again with `--hold <file>` before running anything when you leave a contradiction for the owner. Lint and `check_conformance.py` run either way. A held file stays in the backlog.
3. A not-covered row is the owner's call, and may be a coverage gap the guide could gain (spec R4.3).

## After any mode

- A correction that resolves a conformance gap removes its `[[exception]]` from `build/cc_guide/conformance.toml`, or narrows its `artifacts`, in the same change; `check_conformance.py` must pass.
- Report to the owner: the working-tree diff, split into fact corrections and owner's-call items; what settle held or left unverified; the B and C items; and lint's `STALE` lines for each section whose `changed` moved.
```

**Create** `.claude/skills/cc-guide/references/formats.md`:

```markdown
# Packet and report formats

`cli.py packets` writes the packets and `cli.py settle` reads them back; both live in `build/cc_guide/` (`packets.py`, `settle.py`), whose tests pin these formats. The verifier's contract, `.claude/agents/cc-guide-verifier.md`, states the same report formats.

## Packets

A packet is a directory under `~/.cache/agent-skills/cc-guide/packets/`, by default `<YYYYMMDDTHHMMSS>-<mode>/`; verify and files runs hold one packet per group or file in it. `packets` refuses a directory inside any checkout, or one that is not empty. Every packet holds:

- `index.json`: `mode`, `inputs` (the working tree), `generated_at`, `head` (the changelog head the docs were fetched at), the items the verifier answers for, and `quotes`, the files each kind of quote is re-grepped in.
- `guide.md`: the guide, copied whole, so its line numbers are the guide's.

Then, by mode:

| Mode | Files | `index.json` also names |
|---|---|---|
| triage | `blocks.md` (each changed, missing or new docs block, B1, B2, ...: its current text, and its baselined text from the page's snapshot, as a diff or whole), `releases.md` (every bullet of each untriaged release, `<release>#<n>`, with term hints) | `blocks` (item, group, kind, ref, page, key hash, candidate sections, and `lines`, the lines of `blocks.md` that hold its text), `releases` (label, date, the sections each is untriaged for, hints, hits), `newest`, `next_through`, `groups`, `held`, `owner` |
| verify | per group: `sections.md` (the sections' guide lines and the triage rows that sent them), `blocks.md`, `changelog.md` | `group`, `sections`, `lines`, `checked` (each section's checked release), `docs` (the head release's snapshot, where the group's pages were copied), `advance_to`, `cleared` and `held` (from `--from`, and the sections a missing page holds), `blocks` |
| audit | `sections.md`, `blocks.md`, `releases.md` (the releases untriaged for the group), `changelog.md` | `group`, `sections`, `lines`, `docs`, `releases`, `held`, `blocks` |
| files | per file: `cited_<name>` (the file's copy), `sections.md` (its cited sections' text, each marked when it changed after the file's stamp) | `file`, `copy`, `stamp`, `sections`, `lines`, `changed` |

A triage range counts the untriaged releases after the newest release any section is checked through. With more than 20 of them, `packets --triage` refuses and names the `--through` of the first range of 20; `--through <release>` takes the untriaged releases up to that one, and the range's `next_through` names the next range's, the 20th untriaged release after its own. A section deferred in an earlier range shows its earlier releases again, since they stay untriaged for it, but they do not count toward the 20, so a later session never names the same first range again. Block findings ride in every range, so the first range settles them against the current docs. A missing page needs a `manifest.toml` edit, so it is an `owner` item whose sections are held.

## Reports

The verifier returns one report, saved as `report.md` in its packet. Every row is one line, its fields separated by ` | `, each quote inside double quotes, `-` for an empty field. Settle splits a row on `|`, but a quote field that opens with `"` runs to the first `"` followed by `|` or the end of the line, so a quote may hold `|` and `"`; any other field ends at the next `|`, and the last field takes the rest of the line. A Markdown table's outer pipes, header rows and separator rows are ignored; any other line holding `|` that is no row is listed as unparseable.

Triage, one row per block (at least) and per bullet that touches a section, and one coverage line per release:

    item | TOUCHES / NOISE / UNSURE | section | guide line | "guide quote" | "source quote" | why
    release | sections touched, or none

Verify and audit, parts A, B and C, and a none line for each section with no checkable claim:

    L<line> | claim ≤12 words | CONFIRMED / STALE / WRONG / PARTIAL / NOT FOUND / JUDGMENT | doc:line | "verbatim quote ≤25 words" | proposed wording
    B | version | one line | changelog.md:line
    C | omission
    section | none

Files, one row per statement that rests on a cited section, and a none line for each cited section no statement rests on:

    file:line | statement | section | "verbatim guide quote" | consistent / contradicts / not covered
    section | none

## What settle does with a report

- **Triage fails safe.** A block with no row becomes UNSURE for each of its candidate sections. A release with no coverage line becomes UNSURE for each section its bullets' terms hit, or an owner item when they hit none. A row whose quote is not found becomes UNSURE, handled as TOUCHES; a source quote counts only within its own item's text, and a NOISE row whose source quote, or a guide quote it gives, fails sends its section and every candidate or hint on, or is an owner item when there are none. A bullet's row that does not parse falls back to its hints the same way. An owner item stops the advance below its release. Each TOUCHES or UNSURE section goes to verify. Every other section with an untriaged release in the packet advances to the range's newest one, unless a missing page holds it, and a group's blocks are rebaselined once none of its sections goes to verify or is held. `settled.json` keeps the advance target, the sections cleared, the sections held and the rows each verify section carries, for `packets --verify --from`.
- **Verify, audit and files discard.** A row whose quote is not found is discarded and listed as unverified, and so is a quote a row need not give but gives. A doc quote counts only in the `docs` snapshot's pages or the packet's `changelog.md`. A STALE, WRONG or PARTIAL row whose proposed wording is empty or `-` is discarded too. A surviving STALE, WRONG or PARTIAL row is a correction to apply, unless its line sits within a `TODO(owner)`'s reach (from the TODO through the first list item after it outside fenced code, continuation lines included, or to the end of the section when none follows) or outside the packet's sections; then it is the owner's call, with every JUDGMENT, NOT FOUND, C row and not-covered row, and one outside the packet's sections names the `/cc-guide verify` that reviews it. A B row needs a release and `changelog.md:<line>`; a B or C row that does not parse is listed as unparseable and holds nothing.
- **Holds.** A section is held, neither advanced nor audited, and no block whose candidates include it is rebaselined, nor, while that block is changed or missing, any other block on its page, when: no surviving row or none line answers for it; a discarded STALE, WRONG, PARTIAL or `JUDGMENT (mechanism STALE)` row, or an A row that does not parse, concerns it; a correction to it is left for the owner, or a `JUDGMENT (mechanism STALE)` row survives; its triage or a missing page held it; or `settle --hold` names it. An A row whose line falls in no section holds every section in the packet; a row outside the packet's sections holds nothing, since the run neither reviews nor advances that section and its triage may have advanced it already. A file is held, not cited, when a cited section has no surviving row or none line, a discarded `contradicts` row or a row that does not parse concerns it, a row names a section the file does not cite, or `settle --hold` names it. A hold keeps `accept`, for the text the run did change.
- **Bookkeeping**, in R8.8's order: `baseline accept --substantive` for the sections whose text changed, `rebaseline` for the resolved blocks, `advance` to the triage's newest release (verify after a triage), for each section not checked past it, or `audited` (audit), `cite` (files), `stamp`; then `cli.py lint` and `build/check_conformance.py`. A ranged triage ends with the next range's `packets --triage --through` command.
```

- [x] **Step 5: Watch the register trip (T4)**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 --python 3.13 --with pyyaml python build/check_conformance.py`
Expected: exit 1, with one finding: `.claude/skills/cc-guide/SKILL.md: dmi-handoff-consistency (skills.frontmatter, commands.overview): sets disable-model-invocation: true, but build/CLAUDE.md names cc-guide, and Claude cannot invoke a manual-only skill`.

- [x] **Step 6: Reword the docs**

**Edit** `build/CLAUDE.md` — replace:

```text
on a Claude Code fact carry a `cc-guide:` citation naming the guide sections
they rely on (the spec's R4.1 places it); `cli.py lint` checks each one and
prints `STALE` for a file reviewed before a cited section last changed.
After reviewing such a file, `cli.py baseline cite <file>` restamps it.
```

with:

```text
on a Claude Code fact carry a citation comment naming the guide sections
they rely on (the spec's R4.1 gives its form and place); `cli.py lint` checks
each one and prints `STALE` for a file reviewed before a cited section last
changed. After reviewing such a file, `cli.py baseline cite <file>` restamps
it. The `/cc-guide` skill in `../.claude/skills/` acts on what `check`
reports: `cli.py packets` writes the packets its verifier agent reads, under
the cache, and `cli.py settle` re-greps the verifier's quotes (`cli.py quotes`
checks single rows), applies the spec's fail-safe and discard rules, and
prints the corrections and the `baseline` commands that follow.
```

**Edit** `CLAUDE.md` — replace:

```text
# reports what is due (exit 1 = due; reads main unless --worktree)
```

with:

```text
# reports what is due (exit 1 = due; reads main unless --worktree); /cc-guide acts on what it reports
```

`build/CLAUDE.md` gains 5 lines; `CLAUDE.md` gains none (DF3).

- [x] **Step 7: Run the tests and the register**

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3/build/cc_guide --python 3.13 --with pytest python -m pytest -q`
Expected: all pass, +111 over the baseline.

Run: `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 --python 3.13 --with pyyaml python build/check_conformance.py`
Expected: exit 0.

- [x] **Step 8: Commit**

Confirm the branch, then:

```bash
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 add build/cc_guide/test_skill_files.py .claude/agents/cc-guide-verifier.md .claude/skills/cc-guide/SKILL.md .claude/skills/cc-guide/references/formats.md build/CLAUDE.md CLAUDE.md
git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 commit -m "feat(cc-guide): the /cc-guide skill and its verifier agent (R8.1)" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: Validation (Validation item 6, and Stage 3's offline checks)

**Files:** none changed. This task produces the completion report's evidence.

- [x] **Step 1: Every existing gate (Validation 6).** Run each, and record each outcome against the baseline:

  - the build suite (+111, the 4 known failures only);
  - the cc_guide suite (+111);
  - `hooks/` on both interpreters (unchanged): `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3/hooks --python 3.13 --with pytest python -m pytest -q`, then the same with `--python /usr/bin/python3`;
  - `bash /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3/build/run_commit_lints.sh` (all seven pass; it runs `check_frontmatter.py`, `check_provenance.py`, `check_snippets.py skills/` Tier 1, the dependency-drift test, `sync_runtime_assets.py --check` and `cli.py lint`);
  - `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 --python 3.13 --with pyyaml python build/check_conformance.py` (exit 0).

> Deviation: re-run after the fix wave, at b970318: the build suite 1005 passed (+151: this plan's +111 and the wave's +40), with the 4 known failures and 11 skipped; cc_guide 447 (+151); `hooks/` 274 on both interpreters; all seven commit lints and `check_conformance.py` pass. Steps 2 and 3 gave the same results as before, and the files packet's `index.json` now carries `cache`.

- [x] **Step 2: The new commands against the real cache, offline.** Each reads `~/.cache/agent-skills/cc-guide/latest/` and fetches nothing. The packets go to the cache's default `packets/` directory, never into the worktree (S23).
  - `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 --python 3.13 python build/cc_guide/cli.py packets --triage`: exit 0. It prints either `nothing to triage: no untriaged release and no block finding`, or `wrote triage packet …` when a release has landed since 2.1.296.
  - `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 --python 3.13 python build/cc_guide/cli.py packets --files agents/explore.md`: exit 0. It prints `wrote files packet /Users/lowell/.cache/agent-skills/cc-guide/packets/<stamp>-files/agents__explore.md`. That packet's `index.json` names `stamp` `2.1.219` and the three sections the file cites.
  - `uv run --directory /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 --python 3.13 python build/cc_guide/cli.py packets --audit`: exit 2 with `cc-guide: no audit is due before 2026-11-02: name a group to audit one anyway`, until that date.
  - Record the packet paths in the completion report; they hold the guide and one cited file, so the owner may delete them.
- [x] **Step 3: Hygiene.**
  - `git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 status --porcelain --untracked-files=normal` prints nothing (`.sdd/` is gitignored).
  - `git -C /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-44-cc-drift-stage3 grep -c -E '^[[:blank:]]*(#|<!--)[[:blank:]]*cc-guide:' -- . ':(exclude)specs'` lists 43 files, `:1` each: the 41 that plan 43's sweep cited, plus Task 7's two.
  - `cli.py lint` prints the same 41 `STALE` lines as at the baseline, none naming a `.claude/` file.
- [x] **Step 4: The coverage gaps (R4.3).** Put G1 and G2 (Planning record) in the completion report for the owner, with any gap execution found.

---

## Live run (after the merge; DF1)

This is not a task. It runs after this plan's PR merges and the plan is retired, as Stage 1's bookkeeping ran after the detector merged (#21, then #23). Its product is an uncommitted diff the owner reviews. Plan completion logs one deferred item pointing here, whose Done-when is Validation 3.

**Setup.**
1. Run `git -C /Users/lowell/Projects/agent-skills fetch --prune`, and confirm `origin/main` holds this plan's merge.
2. Run `git -C /Users/lowell/Projects/agent-skills worktree add .claude/worktrees/cc-drift-first-jobs -b chore/cc-drift-first-jobs origin/main`. git refuses a second worktree on `main`.
3. Start a session with that worktree as its working directory, so the skill and the agent load from its `.claude/`. Check `claude --version`.
4. Type `/cc-guide`. With no mode it runs `check --worktree`, the live fetch, and offers what is due.

**A. Triage.** If `check` lists an untriaged release or a block finding, run `/cc-guide triage`, then verify the sections it sends on, or defer them. Above 20 untriaged releases, `packets` names each range (S4). If nothing is untriaged, Validation 3's triage bullet waits for the next release (Task 1, `val3`).

**B. Audit `models`.** Run `/cc-guide audit models`, at about $2.50–5.30; no group is due before 2026-11-02 (R6.7), so the group is named.
- It judges A-53 (`subagents.models`) and H-57 (`lean.model-routing`). H-57 settles "Settle where enforceAvailableModels belongs" with it, including that item's register exception, `enforce-available-models-project`.
- Expected positives. The application test found these in unedited pages; none is confirmed until this run:
  - `deniedModels` is missing from the `availableModels` sentence (T7). The verify rep missed it, so an audit that misses it too is a verifier defect to record for the owner;
  - guide line 426: a Max effort pick applies to the current session only (2.1.295). This bullet is past the TODO's reach under S7, which ends at line 422;
  - line 426: an effort change keeps the cache only with an API key or a Claude subscription, not on Bedrock, Agent Platform or a gateway;
  - `CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL` (2.1.296) is missing from `subagents.models`' precedence text and `lean.model-routing`'s list of model variables;
  - the verify rep's other omissions: `ANTHROPIC_DEFAULT_MODEL`; a top-level `effortLevel` no longer applying from Opus 5.5 on; Sonnet 4.5's deprecation on the Claude API while `sonnet` still maps to it on partner platforms.
- These five omissions exceed R8.5's cap of four C rows, so the audit cannot list them all as omissions. Some may surface as PARTIAL rows on the claims they qualify. The cap is the spec's; the owner may accept a dropped one, or raise the cap for this dispatch.
- A correction within the TODO's reach, guide lines 418–422, goes to the owner and holds `lean.model-routing` (S6), so settle prints no `baseline audited models` until the owner settles that TODO. The audit's A/B/C report is still in hand.
- T7's other two positives, the classifier-billing sentence and the HIPAA exception to the auto-mode default, sit in `rules.settings` (guide line 276). They are left for a `rules` audit.

**C. The first `files` batch: the three known drifts** (R11.5). That is the 7 `agents/*.md` files, `hooks/ruff-check.sh` and `hooks/README.md`: 9 verifiers, above 6, so the skill asks the owner first or takes a subset.
- The owner decides #1, `Grep, Glob` beside `Bash`, and #2, `ruff-check.sh`'s `stop_hook_active` branch, from R11.5's considerations; #3 quotes `$CLAUDE_PROJECT_DIR`.
- H-58 (`hooks.patterns`: the Stop gate at guide line 362 against line 303's `stop_hook_active` check) bears on #2. The owner may run `/cc-guide verify hooks.patterns` first, at about $0.30–1.
- Fixing #1 or #3 removes or narrows its register exception in the same change (R8.8; conformance R6 D5), and fixing an `agents/*.md` file regenerates `runtimes/` (S16). Each reviewed file leaves the backlog through `baseline cite`.
- Under D5, `agents/explore.md`'s capital-E `name`, a registered deviation, holds nothing (S17). Its Grep and Glob entries are #1's gap, which holds the file until the owner decides #1. Verifiers split on its "Haiku-pinned" description (runs 5 and 7). Where one reports a contradiction, the fix reaches `build/sync_runtime_assets.py` and `README.md`, so it is the owner's call and `settle --hold agents/explore.md` keeps the file in the backlog (S16).

**D. Review.** The owner reviews the uncommitted diff, split into fact corrections and owner's-call items. Nothing is committed by the run; how it lands, such as its own PR as #23 did, is the owner's call. Validation 3 then passes.

**Cost.** Each real-agent probe cost $1.32 to $1.58, and $0.52 to $0.67 of that was auto mode's classifier approving reads and writes under `~/.cache` (S13). A permission rule that spares those reads the classifier is an owner-gated settings change.

**Left for later runs:**
- the eight other plan-35 guide notes in `specs/deferred_items.md`, each closing on a `/cc-guide verify` of its section: S-108 (`skills.progressive-disclosure`), S-109 (`skills.listing-budget`), S-110 and C-40 (`mechanisms.overview`), C-41 (`context.overview`), A-52 (`subagents.frontmatter`), A-54 (`subagents.isolation`) and H-58 (`hooks.patterns`), unless step C takes H-58;
- T7's two `rules.settings` positives;
- the rest of the stale backlog (R11.6), including plan 43's "Drift the sweep found", except its `.claude/settings.json:4` item (Stage 4) and the SDD-size item (the SDD bundle).

---

## Plan completion notes

- **Step 1, gate.** The live run is not a leftover of this plan: DF1 places it after the merge.
- **Step 3, deferred items.**
  - Tick, with `→ done in plan 44`:
    - "Carry each missing block's key hash into Stage 3's packets" (T5);
    - "An HTML-form citation can sit above a rules file's frontmatter";
    - "A citation in on-demand Markdown lints clean";
    - "`baseline cite` stamps files `lint` never reads".
  - Under "Style and typing minors in the citation code", add `→ re-deferred by plan 44 (2026-10-12): none of the lines it names was edited`. "Newline handling in the citation reader" stays open on its own Revisit.
  - Append one item for the live run: "Run drift Stage 3's first jobs (plan 44's Live run)". It is self-contained: the worktree recipe, steps A–D, the expected positives and the left list, by pointer to `specs/plans/completed/44-claude-code-drift-automation.md`. Size: plan. Done when: Validation 3 passes as Task 1 amends it. The owner's decisions on #1 and #2 are recorded, the fixes applied and those files left the backlog, the audit's A/B/C report is in hand, and the owner has reviewed the split diff.
- **Step 4, triage.** The backlog is over 20 open items, so the triage proposal runs.
- **Step 5, retire.** `git mv` this plan to `specs/plans/completed/`. The spec stays in `specs/`, because Stages 4–5 remain. Re-point this plan's relative links, if any, for its new depth.
