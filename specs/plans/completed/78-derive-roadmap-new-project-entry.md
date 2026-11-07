# derive-roadmap New-Project Entry Implementation Plan

**Status: COMPLETE (2026-11-06)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give derive-roadmap a second entry for a project with nothing built, and route brainstorming and describe-critique-methodology to it, with a RED baseline before every text change and a GREEN run after.

**Architecture:** Task 1 builds a decision-only micro-test kit with 15 cases and pre-registers each pass rule. Task 2 runs every control arm on the skill text at `BASE` before any skill file changes. Tasks 3 and 4 edit derive-roadmap: the entry, then the resume and completion. Task 5 edits describe-critique-methodology and Task 6 edits brainstorming. Each of these four tasks commits its text and then runs its treatment arms against that commit. The exact new skill text is in this plan, so the owner reviews the wording here.

**Tech Stack:** Markdown skill text; Python per `build/versions.toml` (kit: stdlib only, run through `uv run python`); bash for the rep runner; the `claude` CLI (version recorded at the pilot); `git show` to read fixtures from local clones of the four case-study repositories; this repo's commit lints.

**Spec:** `specs/completed/derive-roadmap-new-project-entry.md` (approved 2026-11-06).

> **Execution base.** The spec and this plan exist only on the local, unpushed branch `claude/roadmap-methodology-scope-c00eab`. An execution worktree, which usually branches from `origin/main`, must contain that branch: merge `refs/heads/claude/roadmap-methodology-scope-c00eab` into it first, and confirm that `specs/derive-roadmap-new-project-entry.md` and this plan both exist. Never execute on `main`.
>
> **Quarantine.** This plan, the spec and the record `specs/red-baseline-new-project-entry.md` with its folder name the cases, the pass rules and the expected behavior. Keep them out of every prompt, and quarantine them during any later micro-test of derive-roadmap, describe-critique-methodology or brainstorming.

## Global Constraints

- **Anchors.** Line numbers were taken at `da5b21b`. The old text in each step is the match key, not the line number. Task 1 Step 1 checks for drift.
- **One owner per file.** A task edits only its listed files. Exceptions: Tasks 3 and 4 both edit `skills/derive-roadmap/SKILL.md`, in different sections (Task 3: description, Overview, §1, §4, §7, Quick reference, Common mistakes; Task 4: §5 and §6). `README.md` changes in Tasks 4 and 5, one row each. `build/test_runtime_support.py` changes in Tasks 5 and 6, one entry each. Tasks 2 to 6 each append their own sections to the record.
- **One definition.** This paragraph appears byte for byte in `skills/derive-roadmap/SKILL.md` (Task 3) and `skills/describe-critique-methodology/SKILL.md` (Task 5), and nowhere is it reworded (spec: "R1, R13(b) and R13(c) all use this one definition"):

  `**Nothing built** means that no outcome of the system the spec or request describes works end to end on real data yet. Judge that system, not the whole repository, and do not count code that only acquires inputs, such as downloads, as a working outcome.`

  Check, from Task 5 on: `for f in skills/derive-roadmap/SKILL.md skills/describe-critique-methodology/SKILL.md; do tr '\n' ' ' < "$f" | tr -s ' ' | /usr/bin/grep -o '\*\*Nothing built\*\* means[^.]*\.[^.]*\.'; done | sort | uniq -c` prints one line that starts with `2 **Nothing built** means that no outcome`.
- **Cross-skill references.** brainstorming and describe-critique-methodology name the entry as `derive-roadmap's New-Project Entry`, a form the dependency-drift test detects. Each new edge is declared soft in `build/test_runtime_support.py`'s `SOFT_REFERENCES`, in the task that adds it, with the reason given there. Each skill says what to do when derive-roadmap is not installed. No other new edge: the dependency-drift test in the commit lints confirms it in every task, and a new `<skill>'s Capitalized Words` phrase anywhere fails it.
- **Compaction window and descriptions.** A SKILL.md body stays at most 20,000 characters (`check_conformance.skill_body(text)[0]`). At `da5b21b`: brainstorming 16,914, derive-roadmap 9,758, describe-critique-methodology 7,511. A description stays at most 1,024 characters (`build/check_frontmatter.py`); derive-roadmap's is 338. No skill gains a `model:` pin.
- **Examples stay out of the fixtures (micro-test Channel 3).** No new skill text uses an example from a fixture domain. Excluded: SEC filings and EDGAR, CES or payroll revisions, embeddings and ACS, CPS or OSHA data, building permits, museum visitor counts, canal locks and river gauges, parking sensors, tide gauges, timesheets, GPX tracks. The spec's R8 examples (a first sec-edgar stage, a first ces-revisions stage) never go into skill text. The new text's examples use a transit agency's trip records.
- **Commit gate.** Before each commit, `bash build/run_commit_lints.sh` prints `commit lints passed`. Commit messages follow Conventional Commits, use plain technical English and end with the attribution trailer that the executing session is given.
- **Micro-tests.** The kit lives at `specs/red-baseline-new-project-entry/kit/`. Every rep is a fresh `claude -p --model claude-opus-5-5 --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence --output-format json --max-budget-usd <cap>` under `env -i` (plan 77's runner), with `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`, from a new empty directory under `/tmp` outside every repository. Five reps per arm. The control arm reads every text at `BASE`. A treatment arm reads every text at the commit its task just made. Text is read with `git show`, never through `~/.claude/skills/`. Each case's pass rule is committed before any rep runs. No kit file is named `test_*.py`.
- **Bars.** A case's clauses are *bar* clauses or *conformance* clauses (Task 1 lists them).
  - *Additive* case: the treatment passes every clause in at least 4 of 5 reps, and the control fails a bar clause in at least 1 of 5.
  - *Non-regression* (guard) case: the treatment passes at least as many reps as the control, minus one.
  - A control with no failure never reverts a change. The spec is owner-approved and requires the behavior, so writing-skills' "nothing to fix, stop" rule gives way: record the clean control and put it to the owner at the plan completion gate (plan 77's rule).
  - A treatment below its bar gets one wording round with the case's rule unchanged, then an owner ruling. A wording round re-runs the treatment of every case in its task whose decision the changed passage can reach. The record says why each other case of that task was not re-run.
- **Spend.** The controller keeps the running total in the record. Stop and ask the owner before the total passes **$60**, and when the control arms alone pass **$30**. Task 1 Step 6 sets the per-rep cap from a pilot.
- **Fixtures.** Fixture text from the case-study repositories is read at build time with `git -C "$CASE_REPOS/<repo>" show <commit>:<path>`, from local clones of the public repositories `lowmason/sec-edgar`, `lowmason/embedding-data` and `lowmason/ces-revisions`. Nothing from those repositories is committed here except the hand-written state lines in `cases.py` and the replies the reps write. Each build's `MANIFEST.txt` records repository URL, commit, path and sha256 for every file it read, and is copied into the arm folder. The case-study repositories are read only: never write, commit or check out there.
- **Leave alone.** `skills/derive-roadmap/references/gap-rubric.md`; every file under `skills/describe-critique-methodology/references/` (spec: no change to `critique-prompt.md`); describe-critique-methodology's description; brainstorming's description, `builder-check-prompt.md` and `visual-companion.md`; every writing-plans file; the open `specs/deferred_items.md` items on §5's two resume gaps and on the roadmap-stage guard wording; `specs/superpowers-drift-spec.md`; the four case-study repositories.
- **Public repository.** The plan, kit, record and commits hold no private detail. The four case-study repositories are public.
- **One execution at a time.** Execution starts only after the owner approves this plan, and only when no other plan executes in this repository (owner ruling, 2026-10-28).

## Review Focus

1. **A spec for a new subsystem inside a mature, working repository.** The person expects the offer when the subsystem has nothing built, even though the repository has working code. Pinned in Task 3 Step 6: the definition says "Judge that system, not the whole repository".
2. **A run that cannot ask** (a sub-agent, `claude -p`). The person expects a provisional file that partitions as today, with the offer at the top, and, in the entry, a ranking labeled provisional. Pinned in Task 3 Step 6: §1's offer and the reference's provisional rule.
3. **Resuming one of the live old-format roadmaps** (in sec-edgar-local, embedding-data and ces-revisions). The person expects §5 to behave as before when no Ranked list exists. Pinned in Task 4 by the `dr-resume-legacy` guard.
4. **A new project of one stage, with nothing built, in brainstorming.** The person expects the usual approaches and sizing, not a roadmap. Pinned by the `bs-guard` and `trigger-decoy` cases (Tasks 3 and 6), whose fixtures are one-cycle requests in empty repositories, and in Task 6 Step 4: every new brainstorming sentence says "several stages".
5. **No spec stem, and the proposed name already has a roadmap file.** The person expects to be asked for another name, never an overwrite. Pinned in Task 3 Step 6: the format's name rule.

## Decisions

The owner approved the plan at review on 2026-11-06: "Approved." D1 to D11 are the eleven defaults of Open for plan review that this approval covers, each as proposed.

- **D1** (owner, plan review, 2026-11-06): reps run on Opus 5.5; spend stops at $60 total and $30 for the controls; a pilot sets the per-rep cap. Applied in: Global Constraints (Micro-tests, Spend), Task 1 Step 6.
- **D2** (owner, plan review, 2026-11-06): fifteen cases, as Task 1 lists them. Applied in: Task 1 Step 3.
- **D3** (owner, plan review, 2026-11-06): additive bars at 4 of 5 with conformance clauses, non-regression at the control minus one, and no revert on a clean control. Applied in: Global Constraints (Bars).
- **D4** (owner, plan review, 2026-11-06): the names §7 "New-Project Entry", `references/new-project-entry.md`, `O1`…, `Outcomes`, `Track`, `Leaves out`, `## Ranked list — Track <X>`, and a roadmap name the owner confirms. Applied in: Tasks 3 and 4.
- **D5** (owner, plan review, 2026-11-06): a core stage's `Produces` names `specs/<name>-stage-<N>-findings.md`, which the research-track resume reads. Applied in: Task 3 Steps 3 and 4, Task 4 Step 2.
- **D6** (owner, plan review, 2026-11-06): the owner may stop a research track at the re-rank question, and its items park. Applied in: Task 4 Step 2.
- **D7** (owner, plan review, 2026-11-06): core stages come first, in the owner's track ranking, unless a dependency says otherwise. Applied in: Task 3 Step 3.
- **D8** (owner, plan review, 2026-11-06): no scaffold detector beyond the gap table and the definition. Applied in: Task 3 Step 2 (§1).
- **D9** (owner, plan review, 2026-11-06): brainstorming → derive-roadmap and describe-critique-methodology → derive-roadmap are soft edges, each with a fallback line. Applied in: Global Constraints (Cross-skill references), Tasks 5 and 6.
- **D10** (owner, plan review, 2026-11-06): the derive-roadmap and describe-critique-methodology README rows gain one sentence each, and "four classes" becomes five. Applied in: Task 4 Step 4, Task 5 Step 5.
- **D11** (owner, plan review, 2026-11-06): fixtures are read from local clones through `CASE_REPOS`, the ces-revisions drafts go in as excerpts, and embedding-data's first gap table is the V1b state with its stage pointers removed. Applied in: Global Constraints (Fixtures), Task 1 Steps 2 and 3.
- **D12** (owner, plan review, 2026-11-06): "Approved.", in answer to the recommendation of subagent-driven-development. Execute with subagent-driven-development in a fresh session. Applied in: the execution handoff.

D13 to D16 come from the owner's "Approved." (2026-11-06), the reply to four handoff points the planning session proposed after the brief's review.

- **D13** (owner, handoff, 2026-11-06): an owner stop in a task (a spend stop, a bar miss, a wording-round ruling) is not a subagent-driven-development blocker. The implementer leaves its files in place and ends with `BLOCKED (owner gate: Task N Step M)`. The controller does not re-dispatch or escalate: it asks the owner, then continues the same implementer from that step with SendMessage. A task never restarts at Step 1, because the kit refuses an existing build folder or rep file. Applied in: Global Constraints (Bars, Spend).
- **D14** (owner, handoff, 2026-11-06): every billed run counts toward the $60 total, the isolation probe and the cost pilot included, and the $30 stop counts Task 2's control reps. Each implementer dispatch carries the running total and the headroom under both stops. Before each `run_reps.sh` call, the implementer checks the total plus that call's worst case (its reps × its cap). A task's spend is one `show_reps.py` run after its last rep, and an unreadable or empty rep file counts at its cap. Applied in: Global Constraints (Spend), Tasks 1 to 6.
- **D15** (owner, handoff, 2026-11-06): when the execution session starts in the planning worktree, on `claude/roadmap-methodology-scope-c00eab` at the commit that records these decisions (a `/clear` there), it executes on that branch. Otherwise a fresh worktree fast-forwards to that commit, the branch's tip at handoff. `BASE` (Task 1 Step 1) is that commit either way. The handoff brief names its sha. Applied in: Execution base, Task 1 Step 1.
- **D16** (owner, handoff, 2026-11-06): the plan-review approval covers the whole plan as written, its exact skill text (Tasks 3 to 6) and its pass rules (Task 1 Step 3) included. A text change found during execution goes through the Bars' wording round or to the owner. Applied in: D1 to D11.

## Open for plan review

Resolved at plan review on 2026-11-06: the owner approved each item as proposed (D1 to D11).

Defaults this plan settles where the spec leaves a call to the builder, or where a choice costs money. The owner approves or amends them as one batch.

1. **Rep model and spend.** Opus 5.5 for every rep, because all three skills run in Opus sessions. Stop at $60 total and at $30 for the controls. Sonnet 5.5 costs less per rep, but its behavior would then stand in for Opus's. The per-rep cap is set from a pilot (Task 1 Step 6).
2. **Fifteen cases.** The spec's checks V1 to V6 map to cases: V1 and V1b (the offer on a spec with nothing built), V2 (no hardening in a first stage), V3 (track split and research depth), V4 (Describe mode stops), V5 (a partly built system gets no offer) and V6 (the resume re-ranks). V1's second half ("on a yes it presents the spec's requirements as an outcome list") gets its own case, `dr-offer-yes`. V7 asks for a RED and a GREEN run for each changed trigger and route. So it adds four cases: a trigger case with a decoy for derive-roadmap's new description (R13d), a route case with a guard for brainstorming's handoff (R13a), and a resume guard for old-format roadmaps. Both guards and the decoy are one-cycle requests in empty repositories, where only the "several stages" test can tell them from the new route.
3. **Bars.** As Global Constraints give them: additive at 4 of 5 with conformance clauses, non-regression at control minus one, and no revert on a clean control.
4. **Names.** The entry is §7, "New-Project Entry", with its detail in `skills/derive-roadmap/references/new-project-entry.md`. Outcome ids are `O1`, `O2`, … The stage fields are `Outcomes` (in place of `Spec` and `Gap closed`), `Track` (only with more than one track) and `Leaves out` (the later-qualities field). A research track's list is `## Ranked list — Track <X>`. The roadmap name, with no spec, is one the owner confirms in the one message.
5. **A core stage writes a findings file.** Its `Produces` names `specs/<name>-stage-<N>-findings.md`, which records the result and the measured cost. The resume of a research track (R11) reads that file. A research core usually feeds no committed later stage, so its plan's Handoff section would read `None`, and the resume would have nothing to report.
6. **A track can stop.** At the resume's re-rank question, the owner may stop a research track instead of promoting an item. The track's remaining items then park under the Parking rule, and §6 (the completion review) runs once no Ranked list waits. Without that branch, a list the owner never empties would block §6 for good.
7. **Core stages come first,** in the owner's track ranking, unless a dependency says otherwise (spec Goal: "Each track reaches a usable result on real data early").
8. **No other scaffold detector.** The gap table and the definition decide (spec, Left to the builder, third bullet).
9. **Soft edges, with fallbacks.** brainstorming → derive-roadmap and describe-critique-methodology → derive-roadmap are soft. brainstorming sizes the work as a project when derive-roadmap is absent. describe-critique-methodology says so and stops.
10. **README.** The derive-roadmap and describe-critique-methodology rows gain one sentence each. The derive-roadmap row's stale "four classes" becomes five, adding out-of-repo.
11. **Fixtures.** Read from local clones (`CASE_REPOS`). The ces-revisions research drafts (about 214 KB) go in as excerpts. embedding-data's first gap table is the state for V1b (the offer when only inputs are downloaded), with its stage pointers removed.

---

### Task 1: micro-test kit, cases, record and pilot

**Files:**
- Create: `specs/red-baseline-new-project-entry/kit/run_reps.sh`, `isolation_probe.txt` and `show_reps.py`, copied from `specs/red-baseline-audit-p2/kit/`. The runner's temp prefix becomes `/tmp/plan78-rep-`. Comments and docstrings name plan 78. `show_reps.py`'s reading aids flag `derive-roadmap`, `New-Project`, `nothing built`, `rank`, `Leaves out`, `Ranked list`, `manifest`, `traceab`, `point-in-time`, `triage`, `notation` and `approach`. No old kit file is edited.
- Create: `specs/red-baseline-new-project-entry/kit/build_prompts.py`, from plan 77's, with the three changes in Step 2.
- Create: `specs/red-baseline-new-project-entry/kit/cases.py` (15 cases, Step 3)
- Create: `specs/red-baseline-new-project-entry.md` (the record)
- Create: `specs/red-baseline-new-project-entry/pilot/`

**Interfaces:**
- Produces: `CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py <sha> <out-dir> [<case> ...]` (and `leakview <out-dir>`); `bash specs/red-baseline-new-project-entry/kit/run_reps.sh <prompt> <out-dir> <first> <last> claude-opus-5-5 <cap>`; `uv run python specs/red-baseline-new-project-entry/kit/show_reps.py <dir> ...`. The 15 case keys below. The per-rep cap in the record.
- Consumes, for fixtures: the roadmap format fixed in Task 3 Step 4 (the `dr-resume-rerank` fixture uses it before Task 3 runs).

- [x] **Step 1: Fix `BASE` and check for drift.** `BASE` is the execution branch's start commit; write its sha in the record. Run `git diff --stat da5b21b BASE -- skills/derive-roadmap skills/describe-critique-methodology skills/brainstorming build/test_runtime_support.py README.md NOTICE`.
Expected: no output. Otherwise re-take the anchors of each changed file before its task, and add a deviation note.

- [x] **Step 2: Write `build_prompts.py`.** Plan 77's file, with these changes:
  - **Skills listing.** Every prompt carries, after the frame's first line, a block headed `Skills available in this session, as your skill listing shows them (name: description):`, with one line per skill, read from the frontmatter at the arm's sha, for `brainstorming`, `creative-thinking`, `derive-roadmap`, `describe-critique-methodology`, `design-architecture`, `executing-plans`, `subagent-driven-development` and `writing-plans`, in that order. In `leakview`, each description is the placeholder.
  - **Case-repository files.** `repo_file(repo: str, commit: str, path: str, excerpt: int | None = None) -> str` reads with `git -C "$CASE_REPOS/<repo>" show <commit>:<path>`. It refuses when `CASE_REPOS` is unset or the read fails. With `excerpt`, it returns the file's first line, then every Markdown heading line, then the first `excerpt` characters, then `[excerpt: <excerpt> of <N> characters]`. Each read adds a MANIFEST line: `https://github.com/lowmason/<repo>`, commit, path, sha256 of the text used. A fixture places a file's text with a `{file:<key>}` marker that the case maps to a `repo_file` call. `leakview` keeps these files, since they are fixture, not text under test.
  - **No texts.** A case whose `texts` list is empty (the trigger cases) builds a prompt with no text block.

> Deviation: `build_prompts.py` also reads and writes UTF-8 explicitly, and its listing parser accepts only a folded `description: >` block.
- [x] **Step 3: Write the 15 cases in `cases.py`.** Each case gives `texts`, `model` (`claude-opus-5-5`), `budget` (filled in at Step 6), `kind`, `fixture`, `task`, `pass` (clauses marked bar or conformance, with reading notes), `leak` and, where it reads them, its `repo_file` calls. Text sets: **DR** = `skills/derive-roadmap/SKILL.md` and `skills/derive-roadmap/references/*.md`. **DCM-D** = `skills/describe-critique-methodology/SKILL.md` and its `references/methodology-template.md`. **DCM-S** = the same SKILL.md and its `references/spec-synthesis.md`. **BS** = `skills/brainstorming/SKILL.md`. Rules for every fixture:
  - `[you, tools]` lines state what the tools showed, as facts, and never a verdict the case scores.
  - A constructed fixture uses its listed domain only.
  - The task line is `It is your turn. You have no tools in this turn, so write any tool call as text. Write your next message to your partner.` unless the case gives another.

  | Case | Spec ref | Kind | Texts |
  |---|---|---|---|
  | `trigger-stages` | R13d | additive | none |
  | `trigger-decoy` | R13d guard | non-regression | none |
  | `dr-offer-scaffold` | V1, R1b | additive | DR |
  | `dr-offer-inputs` | V1b | additive | DR |
  | `dr-offer-yes` | V1, R4, R5, R15 | additive | DR |
  | `dr-built-guard` | V5 | non-regression | DR |
  | `dr-known-progression` | V2, R7–R9 | additive | DR |
  | `dr-tracks` | V3, R4 | additive | DR |
  | `dr-research-depth` | V3, R7, R8 | additive | DR |
  | `dr-resume-rerank` | V6, R11 | additive | DR |
  | `dr-resume-legacy` | R11 guard | non-regression | DR |
  | `dcm-describe-route` | V4, R13b | additive | DCM-D |
  | `dcm-synth-route` | V3, R13c | additive | DCM-S |
  | `bs-route` | R13a | additive | BS |
  | `bs-guard` | R13a guard | non-regression | BS |

  - **`trigger-stages`.** The session opens in a new repository that holds a one-line `README.md`. The partner's first message: they want building-permit records from three county portals in one table, then monthly updates, then a public summary page; nothing exists yet; "Can you lay out the stages for this?" Task: `Name the skill you invoke first, if any, and give one sentence why. Then stop.` PASS (bar): the first skill named is derive-roadmap. Leak: `New-Project`, `nothing built`, `outcome`.
  - **`trigger-decoy`.** The session opens in a new repository that holds a one-line `README.md`, so nothing is built, and the request is clearly one cycle. The partner: "Let's build a small command-line tool that totals the hours in a timesheet CSV." Task as `trigger-stages`. PASS: the first skill named is brainstorming. Leak: as `trigger-stages`.
  - **`dr-offer-scaffold`.** Source `sec-edgar` at `22c6767f`. The partner: "Derive the roadmap for specs/sec-filing-index-ingestion-spec.md." `[you, tools]` lines give the tree and say that every `__init__.py` and `README.md` is empty and each `pyproject.toml` declares a name only. The spec follows whole (`{file:spec}`), and the ADR is named with a one-line statement of its decision. One line gives the gap analysis as run: one row per numbered requirement (count them by the spec's own numbering and state the count), every verdict `missing`, evidence "no code beyond empty package scaffolds". Further lines: no file under `specs/` carries the roadmap header, and `specs/deferred_items.md` does not exist. PASS needs three bar clauses:
    - **A.** The reply has no stage partition, stage list or roadmap text, including one offered "for approval".
    - **B.** It says, in any words, that no outcome works end to end yet.
    - **C.** It asks whether to stage the project from a list of outcomes that the partner ranks, in place of partitioning the requirements, and waits for the answer. It fails C when it switches to that path without asking.

    Other batched questions may come with it. Leak: `New-Project`, `nothing built`, `outcome`, `rank`.
  - **`dr-offer-inputs`.** Source `embedding-data`. The spec is `specs/embedding-evaluation-data-spec.md` at `af7bf21`, whole. The tree of `src/` and `tests/` has one line per module, taken from its docstring. One line says pytest (44) and Behave (2) pass and five IPUMS extracts are on disk. The `[you, tools]` gap analysis is the Gap analysis table of `specs/embedding-evaluation-data-spec-roadmap.md` at `4bc8cda`. Remove every stage pointer from its Note column (`→ S<n>`, `S<n>`, `V<n> → S<n>`) and any phrase that names a stage, and include nothing after the table. Same partner line, task and PASS as `dr-offer-scaffold`, with the spec's path. Leak: as `dr-offer-scaffold`, plus `only`, `end to end` and `acquir` in the table's notes. Record each hit, and keep it only where it is the historical evidence and not a verdict.
  - **`dr-offer-yes`.** As `dr-offer-scaffold`, then an `[earlier]` summary of your last message: the gap table (all `missing`), the finding that nothing works yet, and the question whether to stage the project from a ranked list of outcomes, with the spec's requirements as candidates. The partner: "Yes, do that." PASS:
    - **A (bar).** A numbered list of outcomes in plain words, one line each, drawn from the spec's requirements.
    - **B (bar).** The reply gives no ranking of its own, and it asks the partner to rank. The spec's order or list order, labeled as such, passes. A proposed priority order fails.
    - **C (bar).** No roadmap text and no stage partition.
    - **D (conformance).** At least one cost note with its basis, or a statement that only a run can measure it.

    Leak: `New-Project`, `Leaves out`, `core stage`.
  - **`dr-built-guard`.** Constructed; domain: a museum's visitor-count forecaster. `specs/visitor-forecast.md` has six numbered requirements: R1 load daily turnstile counts from the real export, R2 a baseline seasonal forecast, R3 holiday effects, R4 a weather covariate, R5 a weekly report and R6 an accuracy dashboard. It has no routing header. The `[you, tools]` gap table gives R1 and R2 `implemented-as-specified`, with test names and the line "daily counts from the real 2019–2025 turnstile export load, and the baseline forecast runs on them end to end; tests pass". R3 is `implemented-differently` and R4 to R6 are `missing`. The partner: "Derive the roadmap for specs/visitor-forecast.md." PASS: the reply neither says that nothing is built nor offers outcome-first staging, and goes on by the existing flow: the table with any batched questions, a partition, or the single-stage exit. Leak: `New-Project`, `nothing built`, `outcome`.
  - **`dr-known-progression`.** Source `sec-edgar` at `22c6767f`: the tree as in `dr-offer-scaffold`, and the spec whole as background. The partner's first message asks for a roadmap for SEC filing ingestion and says nothing exists beyond the package scaffolds. The progression is the quarterly and daily index files, then the individual submissions, then 10-K and 8-K handling, and the spec and ADR are background. An `[earlier]` summary follows: you sent the outcome list with cost notes, proposed one known-progression track and the name `sec-filing-ingestion`, and asked for a ranking. The partner: "Rank them in the order I gave. One track, a known progression. The name is fine." Task: `It is your turn. You have no tools in this turn. Write the full roadmap file you will commit now, as Markdown, then the one-line message you send with it.` PASS:
    - **B (bar).** The first stage's Exit requires no manifest, no traceability (a provenance or lineage record per row) and no point-in-time (as-of) awareness. A quality named as left out passes.
    - **A (conformance).** Committed stages cover, in order, the index files, the individual submissions, and 10-K and 8-K handling.
    - **C (conformance).** Manifests, traceability and point-in-time awareness each appear in a named later stage.
    - **D (conformance).** Every stage entry has a field that names what it leaves out and where that goes.
    - **E (recorded, no bar).** The first stage's Exit does not require complete dataset generations to publish atomically. The background spec's §1 asks for that, and the skill text does not name it, so E checks transfer.

    Leak: `Leaves out`, `core stage`, `later stage`, `final-standard`, `hardening`.
  - **`dr-tracks`.** Source `ces-revisions` at `0e24ecc`, the parent of `237b426`. `[you, tools]` lines give the tree: a package scaffold and smoke tests. `specs/ces-revisions-prompt.md` follows whole. Each of `specs/ces-revisions-research-chatgpt.md`, `-claude.md` and `-gemini.md` follows as a 3,000-character excerpt. An `[earlier]` line says describe-critique-methodology routed the brief and the three research files here as background, and that nothing is built. The partner: "Go ahead and stage it." PASS:
    - **A (bar).** An outcome about collection time or the collection interval and revision size sits in a different track from an outcome about budget, staffing or attrition, and the reply says why.
    - **B (conformance).** No ranking is given as settled, and the reply asks the partner to rank.
    - **C (conformance).** One message with no roadmap text.
    - **D (conformance).** A cost note for model fitting or compute, with a basis or a statement that the core stage measures it.

    Leak: `New-Project`, `research track`, `separate track`.
  - **`dr-research-depth`.** As `dr-tracks`, then an `[earlier]` summary of your message. It lists outcomes O1 to O*k*, one plain line each, written in `cases.py` from the brief. It proposes two research tracks: A, collection interval and revision size; B, budget, staffing and attrition. It gives the reason for the split, cost notes and the name `ces-revisions`. The partner: "Tracks are right, both research. Track A first." The partner then gives an order within each track, written in `cases.py`, and says "The name is fine." Task as `dr-known-progression`. PASS:
    - **A (bar).** Each track commits exactly one stage, and every other outcome of the track sits in a ranked list, not in a committed stage.
    - **B (bar).** Each committed stage's Exit names a cost of the real run to measure and record: time, compute or data volume.
    - **C (conformance).** The two tracks stay separate.
    - **D (conformance).** Each stage entry names what it leaves out.
    - **E (conformance).** Each committed stage's Produces names a file that records the result and the measured cost.

    Leak: `core stage`, `measured cost`, `Leaves out`.
  - **`dr-resume-rerank`.** Constructed; domain: canal lock closures and river-gauge levels. `specs/lock-closures-roadmap.md` is a new-project roadmap in the Task 3 Step 4 format. It has one research track, and its Stage 1 (the core) is ticked with its COMPLETE stamp. `## Ranked list — Track A` holds three items. `[you, tools]` lines say that the stage plan's `## Handoff to later stages` reads `None: shipped as the roadmap's Produces states.` and give `specs/lock-closures-stage-1-findings.md`: a two-line result and the measured cost ("one fit on 11 years of daily gauge readings, 1.8 GB, took 22 minutes on a laptop"). The partner: "Resume the roadmap." PASS:
    - **A (bar).** No completion review starts, and the roadmap is neither parked nor retired.
    - **C (bar).** One question that asks for a re-ranking of the list or the approval of a proposed next stage from it, with a default.
    - **B (conformance).** The reply reports the core's finding and its measured cost.
    - **D (conformance).** No new stage entry is written before the answer.

    Leak: `re-rank`, `promote`, `stop the track`.
  - **`dr-resume-legacy`.** Constructed; domain: a parking-sensor occupancy pipeline. The roadmap is in today's format: a Gap analysis table, three stages with `Spec` and `Gap closed`, all ticked and stamped COMPLETE, a Completion section and no Ranked list. The partner: "Resume the roadmap." PASS: the reply goes to the completion review. It says every stage is complete and starts or proposes the audit over the spec's requirements, and it asks no re-ranking question. Leak: as `dr-resume-rerank`.
  - **`dcm-describe-route`.** Source `sec-edgar` at `22c6767f`: the tree and the spec whole. The partner: "Write the methodology description of this filing-index ingestion system for an external SOTA critique." PASS needs three bar clauses:
    - **A.** No methodology description, notation table or template slot, and none planned as the next step.
    - **B.** The reply says, in any words, that the system has nothing built.
    - **C.** It routes to derive-roadmap to stage the project, and says the critique comes after the system is built. A route to brainstorming alone fails C.

    Leak: `New-Project`, `nothing built`.
  - **`dcm-synth-route`.** Source `ces-revisions` at `0e24ecc`, as `dr-tracks` without the `[earlier]` routing line. The partner: "The research is back. Use synthesize mode: the description is specs/ces-revisions-prompt.md and the critiques are the three research files." PASS needs three bar clauses:
    - **A.** No triage table and no spec text, now or as the next step.
    - **B.** The reply says that the description is a brief for something not built, or that nothing is built.
    - **C.** It routes the files to derive-roadmap as background for staging.

    Leak: `New-Project`, `nothing built`, `background`.
  - **`bs-route`.** Constructed; domain: a tide-gauge archive. The partner's first message, not naming brainstorming: collect hourly readings from four coastal stations' public feeds, clean and gap-fill them, then publish monthly extremes per station as a CSV and a chart. It is a fresh repository and nothing exists. Your first message, given in an `[earlier]` line, echoed the request and asked who uses it and what success looks like. The partner's answer: a harbor-master group uses it; success is one year of clean monthly extremes for each station; Python on their laptop; "in the order I said". PASS needs three bar clauses:
    - **A.** The reply hands the project to derive-roadmap in this session, to stage the outcomes: it invokes the skill, or says it does so now.
    - **B.** It lays out no approaches for the whole project.
    - **C.** It writes no design document or spec file, and asks no question that the conversation already answers.

    Leak: `New-Project`, `roadmap`, `nothing built`.
  - **`bs-guard`.** Constructed; domain: a small script, in a fresh repository where nothing exists, that reads a folder of GPX track files and writes one CSV with each track's distance and duration. Nothing is built, and the work is one cycle, so only the "several stages" test keeps it off the new route (Review Focus item 4). Your first message, given in an `[earlier]` line, echoed the request and asked one question. The partner's answer settles the units and what happens to a file that fails to parse. PASS: the reply lays out two or three ways to build it, in this message, with a recommendation and one question asking which way to go. It does not hand off to derive-roadmap. Leak: as `bs-route`.

> Deviation: At `22c6767f` each sec-edgar `__init__.py` holds the `uv init` `hello()` stub, so the fixture states that fact and the gap evidence reads "generated package scaffolds", not "empty". The `dr-offer-inputs` gap table empties only the osha row's note, by the plan's leak rule (record: Amendment 1).
- [x] **Step 4: Write the record.** It holds `BASE`; the kit's files; the arms; both bar kinds and the clause kinds from Global Constraints; the VOID rule copied from plan 77's `cases.py`; each case's reading rule, kind and bar; the fixture sources with their commits; and the quarantine note from this plan's header. Then build the leak view, `CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py leakview /tmp/plan78-work/leak`, and grep each prompt for its case's leak words. Record each hit, and whether it is exempt and why: a hit in the listing's skill names, or in a case-repository file read verbatim, can be exempt. A hit in a hand-written line is reworded. Commit before any rep:

```bash
git add specs/red-baseline-new-project-entry specs/red-baseline-new-project-entry.md
git commit -m "test(specs): micro-test kit and reading rules for plan 78"
```

- [x] **Step 5: Pilot isolation.** Run `bash specs/red-baseline-new-project-entry/kit/run_reps.sh specs/red-baseline-new-project-entry/kit/isolation_probe.txt specs/red-baseline-new-project-entry/pilot/probe 1 1 claude-opus-5-5 1.00`.
Expected: all five probe lines `NO`; `show_reps.py` shows one turn, no tool and one model. Record the Claude Code version (`claude --version`).

- [x] **Step 6: Calibrate the spend.** Build the control prompts with `build_prompts.py BASE /tmp/plan78-work/calibrate`. Run one uncounted rep of the largest prompt by bytes into `specs/red-baseline-new-project-entry/pilot/<case>/` with a $3.00 cap. Set the per-rep cap to the larger of $1.00 and three times the pilot's `total_cost_usd`, rounded up to the next $0.25. Write it into every case's `budget`, and estimate the run as 150 × the pilot cost.
Expected: the record shows the pilot cost, the cap and the estimate. If the estimate passes $60, stop and ask the owner before any counted rep.

- [x] **Step 7: Commit**

```bash
git add specs/red-baseline-new-project-entry specs/red-baseline-new-project-entry.md
git commit -m "test(specs): isolation pilot and spend calibration for plan 78"
```

### Task 2: control arms (RED)

**Files:**
- Create: `specs/red-baseline-new-project-entry/control/<case>/rep<N>.json` and `control/MANIFEST.txt`
- Append: `specs/red-baseline-new-project-entry.md` (Control)

**Interfaces:**
- Consumes: Task 1's kit, cases and cap.
- Produces: each case's control score per clause, which Tasks 3 to 6 compare against.

- [x] **Step 1: Confirm no skill file has changed.** `git diff --stat BASE -- skills/` prints nothing.
- [x] **Step 2: Run five reps per case.** Build with `build_prompts.py BASE /tmp/plan78-work/control`, now that every case carries its cap, and run into `specs/red-baseline-new-project-entry/control/<case>/`. Copy the build's `MANIFEST.txt` to `control/`. Rerun each VOID rep under the next free number.
- [x] **Step 3: Score every reply by hand** by the committed rule, clause by clause. Record each case's score per clause, the VOID reruns, one verbatim quote per failed bar clause, and the spend. A case whose control passes every bar clause in 5 of 5 is marked "clean control: to the owner at the completion gate".
> Deviation: Scoring needed readings that the committed notes do not state. The controller confirmed them during execution. They are written once under "Readings applied" in `specs/red-baseline-new-project-entry.md` and apply to every arm.
- [x] **Step 4: Commit**

```bash
git add specs/red-baseline-new-project-entry specs/red-baseline-new-project-entry.md
git commit -m "test(specs): control arms for plan 78's micro-tests"
```

### Task 3: derive-roadmap's New-Project Entry

**Files:**
- Modify: `skills/derive-roadmap/SKILL.md:3-8` (description), `:25-27`, `:29-46`, `:63-72` (§1), `:125-126` (§4), `:190-214` (Quick reference, Common mistakes); append §7 after §6 (`:188`)
- Create: `skills/derive-roadmap/references/new-project-entry.md`
- Modify: `skills/derive-roadmap/references/roadmap-format.md` (append)
- Append: `specs/red-baseline-new-project-entry.md` (Task 3 treatment); create `specs/red-baseline-new-project-entry/treatment/<case>/`

**Interfaces:**
- Consumes: Task 2's control scores.
- Produces: §7 "New-Project Entry" (the name Tasks 5 and 6 cite as `derive-roadmap's New-Project Entry`); the `New-project roadmaps` format: the `Outcomes` section, the stage fields `Outcomes`, `Track` and `Leaves out`, `## Ranked list — Track <X>`, and the findings file `specs/<name>-stage-<N>-findings.md`, which Task 4's §5 text reads.

- [x] **Step 1: Show the gap.** `/usr/bin/grep -c "New-Project\|Nothing built" skills/derive-roadmap/SKILL.md`.
Expected: `0`.

- [x] **Step 2: Edit `SKILL.md`.** Wrap each new passage like the text around it.
  - Description (`:3-8`) becomes:

```text
  Use when a spec opens with a header naming derive-roadmap as the required
  next skill, when resuming staged work ("resume the roadmap", a
  specs/*-roadmap.md file), when comparing a spec against the current
  implementation to stage what remains, or when a project with nothing built
  yet needs its stages laid out ("lay out the stages", "roadmap this new
  project", outcomes or a progression to rank and stage). Partitions gaps or
  outcomes into staged spec-to-plan cycles. Never plans or brainstorms a stage
  itself.
```

  - Core principle (`:25-27`): after `and does not brainstorm one.` add `Listing, splitting, ranking and costing a new project's outcomes is partitioning, not design.`
  - Entry list (`:32-43`): insert a new item 2 and renumber the old items 2 and 3 to 3 and 4.

```text
2. Your partner asks for a roadmap for a project that has nothing built
   (below), or gives its outcomes or its stages in their own words, with or
   without a spec → §7, New-Project Entry.
```

  - After `does not make a document a roadmap — only the header does.` (`:46`), a new paragraph: the definition from Global Constraints, verbatim.
  - §1, between the paragraph that ends `gates before stage 1.` (`:67`) and `**SINGLE-STAGE EXIT.**`:

```text
**NOTHING BUILT.** When the table shows nothing built (Overview), do not
partition. Add one item to the batched question set: what you found (which
rows are implemented, and why none of them is a working outcome), and an
offer to stage the project through the New-Project Entry (§7), with the
spec's requirements as outcome candidates. Then wait for the answer: never
switch on your own. On a yes, go to §7. On a no, partition as below. When the
session cannot ask, the offer goes in the questions block and the provisional
file partitions as below. The table is the whole test: no other check decides
that a repository is only a scaffold.
```

  - §4 (`:125-126`): `scoped to the stage entry's `Spec` refs.` becomes `scoped to the stage entry's `Spec` refs, or its `Outcomes` refs in a new-project roadmap.`
  - After §6 and before `## Quick reference`, the new section:

```text
## 7. New-Project Entry

For a project with nothing built (Overview). Read
`references/new-project-entry.md` before your first message: it holds the
inputs, the checks you may run, and each rule below in full.

1. **Outcomes.** Write the outcomes as a numbered list (O1, O2, …), one line
   each, in plain words: what your partner gets, not how it is built. They
   come from your partner's words, or from a spec's requirements as
   candidates. Background files give facts, options and costs, and never add
   an outcome on their own.
2. **Tracks.** Group the outcomes into tracks. Outcomes that answer unrelated
   questions, or serve different uses, go in separate tracks, and you say why
   you split them. Catching a bundled request is your job, not your
   partner's. Each track is a known progression (your partner can name its
   stages from first to last) or research (the method or the answer is open).
3. **Cost.** Each outcome whose cost is material gets a rough estimate and its
   basis. When only running the work can tell, say so.
4. **One message.** Before any roadmap text, send one message: the outcome
   list, unranked, with the cost notes, the tracks and their kinds, and a
   proposed roadmap name. It makes one request: rank the outcomes within each
   track and the tracks among themselves, and confirm the tracks. Do not rank
   for your partner unless they ask.
5. **Stages.** Each track's first stage is its core stage: it works on real
   data at the smallest standard that gives a usable result, and its Exit
   names the measured cost of the real run. A known-progression track commits
   every stage, first to last, its later hardening stages included. A research
   track commits its core stage only, and its other outcomes wait in its
   Ranked list until the core has run on real data. A quality the project
   needs eventually but not to work goes to a named later stage or a
   Ranked-list item, never into a core stage's Exit.
6. **Write, then §4.** Write the roadmap per `references/roadmap-format.md`
   (New-project roadmaps), then present the partition for approval (§4).
```

  - Quick reference: three rows after `| A spec carrying the Synthesize-mode header … |`:

```text
| Your partner's outcomes or stages for a project with nothing built | §7: outcomes, tracks, cost notes, one message, then stages |
| A gap table that shows nothing built | Offer §7 in the batched questions, then wait for the answer |
| A research track with its committed stages ticked and a Ranked list waiting | Report the core's finding and cost, then one re-rank question (§5) |
```

  - Common mistakes: three bullets after the last one (`:214`):

```text
- **Switching to §7 on your own** — when the table shows nothing built,
  offer it and wait for a yes.
- **Ranking outcomes for your partner** — show the list unranked; the ranking
  is their judgment of value.
- **A final-standard quality in a core stage's Exit** — manifests,
  traceability and the like go to a named later stage or a Ranked-list item,
  recorded in `Leaves out`.
```

- [x] **Step 3: Create `references/new-project-entry.md`** with this text:

````markdown
# New-Project Entry

SKILL.md §7 gives the steps. This file gives the rules behind each one.

## When you are here

Your partner asked for a roadmap for a project with nothing built (defined in
SKILL.md's Overview), or said yes to the offer that SKILL.md §1 makes when a
gap table shows nothing built. A document that carries the roadmap header
goes to Resume (§5) first, always.

## Inputs

- Your partner's outcomes or progression, in plain words. These are the
  source.
- A spec, when there is one. Its numbered requirements become outcome
  candidates, one line each, for your partner to confirm and rank.
- Background files, when given: research results, a draft spec, notes. Read
  them for facts, options and costs. An outcome that only a background file
  states is a candidate: list it, mark it "from <file>", and let your partner
  confirm it. Background never becomes a requirement list on its own.
- Choices your partner has already made for the whole project, such as the
  language or the platform. Record each in one line. Recording a choice is
  not designing.

## Checks you may run before the message

Only cheap read-only checks: a directory listing, a file-size lookup, a
published limit such as a rate limit, a quota or a price. The message may
also propose one small probe, such as fetching one real file or timing one
model fit, to firm up a cost note. Run a probe only after your partner says
yes. A probe gathers information. It does not design the stage.

## Outcomes and tracks

- One line per outcome: what your partner gets, not how it is built. "On-time
  rates per route for one real month of trip records" is an outcome. "A
  pipeline with a manifest layer" is not.
- Put outcomes in separate tracks when they answer unrelated questions or
  serve different uses, even when one request names them together. Joined,
  the first outcome waits on the machinery of the second. Say why in one line.
- A track is a known progression when your partner can name its stages from
  first to last, and research when the method or the answer is open. One
  project may hold tracks of both kinds. When the kind is unclear, propose one
  and ask in the same message.

## Cost notes

Each outcome whose cost is material gets a rough estimate and its basis.
Material costs include compute hours or dollars, data volume, rate limits and
your partner's time. A basis is a published limit, a file size, or arithmetic
from known figures: "about 4 GB: 12 monthly files of about 330 MB each, from
the listing". When no estimate is possible without running the work, say so:
the track's core stage measures it.

## The one message

Before any roadmap text, send one message that holds:

1. the numbered outcome list, unranked, each line with its cost note;
2. the proposed tracks, each with its kind and, for a split, the reason;
3. the choices already made, one line each;
4. a proposed roadmap name, the `<name>` in `specs/<name>-roadmap.md`;
5. one request: rank the outcomes within each track and the tracks among
   themselves, and confirm or change the tracks, their kinds and the name.

Do not rank for your partner unless they ask: the ranking is their judgment of
value. A list or a table both work. When the session cannot ask, write the
roadmap as a provisional file (SKILL.md §1): rank by the order your partner
gave, or else by the list order, and label the ranking provisional.

## Stages

- **Core stage.** Each track's first stage. It works on real data at the
  smallest standard that gives a usable result, and in a research track it
  delivers the top-ranked outcome end to end. Its Exit names the observable
  result and the measured cost of the real run: time, compute or data volume.
  Its Produces names `specs/<name>-stage-<N>-findings.md`, which records the
  result and the measured cost. Example: a first stage that loads one real
  month of a transit agency's trip records, reports on-time rates per route,
  has no manifest layer, and records how long the month took to load.
- **Known progression.** Commit every stage, first to last, later hardening
  stages included. describe-critique-methodology runs once these stages are
  built, not before.
- **Research.** Commit the core stage only. The track's other outcomes go in
  its Ranked list, in your partner's order, until the core has run on real
  data, because the first results may change the ranking (SKILL.md §5).
- **Later qualities.** A quality the project needs eventually but not to work
  goes to a named later stage in a known progression, or to a Ranked-list item
  in a research track. Examples: manifests, traceability, point-in-time
  awareness, full validation suites, scheduling and deployment. A core stage's
  Exit never requires one. Each stage entry's `Leaves out` field names what
  that stage leaves out and which later stage or item picks it up, so the
  stage's own brainstorming session or plan does not pull the quality back in.
- **Order.** Sequence by SKILL.md §2. A core stage is the cheap information
  about its track, so the core stages come first, in your partner's track
  ranking, unless a dependency says otherwise.

## What stays out

How a stage is built: its tasks, its tests, its approach. That stays with
brainstorming or writing-plans, by bare name, in the stage's own session.
````

- [x] **Step 4: Append to `references/roadmap-format.md`,** after its last line:

````markdown

## New-project roadmaps

A roadmap from the New-Project Entry (SKILL.md §7) keeps the header, the stage
checkboxes, the stamps and the resume above, with these differences.

`<name>` is the spec's stem when there is a spec. With no spec, it is the
kebab-case name your partner confirmed in the one message. Before writing,
check that `specs/<name>-roadmap.md` does not exist. If it does, ask for
another name: never overwrite it.

After the header, in order:

1. **Outcomes**, in place of the Gap analysis. With no spec, this section is
   the roadmap's source of truth.
2. **Open questions**, as above.
3. **Stages**, the entries below.
4. **Ranked list — Track <X>**, one section for each research track.
5. **Stage-spec stamp**, as above.
6. **Completion**: SKILL.md §6, run over the Outcomes list.

The Outcomes section keeps one line per outcome:

```
Source: <your partner's words, YYYY-MM-DD> | <spec path>. Background: <paths> | none.
Choices made: <one line each> | none.

| # | Outcome | Track | Rank | Cost (estimate; basis) |
|---|---|---|---|---|
| O1 | <what your partner gets> | A | 1 | <estimate; basis> or "measured by Stage 1" |

Tracks: A — <name> (known progression | research). <Split from B because …>
```

Stage entries carry these fields and nothing else. `Outcomes` takes the place
of `Spec` and `Gap closed`:

```
- [ ] Stage N: <short name>
      Objective: <one sentence>
      Outcomes: <the O-numbers this stage delivers>
      Track: <letter> (omit with one track)
      Consumes: <as above>
      Produces: <as above; a core stage names specs/<name>-stage-<N>-findings.md>
      Exit: <one observable outcome per O-number; a core stage adds the measured cost of its real run>
      Leaves out: <each quality this stage does not need, with the stage or Ranked-list item that picks it up> | nothing
      ROUTING: brainstorming | writing-plans
```

Each research track's Ranked list keeps your partner's order:

```
## Ranked list — Track B
1. O4 — <cost note>
2. O6 — <cost note>
```

An item leaves the list when your partner promotes it to a stage at a resume,
or parks when the track stops (SKILL.md §5).
````

- [x] **Step 5: Measure.** The derive-roadmap body measures at most 20,000 characters: `cd build && uv run --with pyyaml python -c "import check_conformance as c, pathlib; print(len(c.skill_body(pathlib.Path('../skills/derive-roadmap/SKILL.md').read_text())[0]))"`. `uv run --with pyyaml python build/check_frontmatter.py` passes. `/usr/bin/grep -c "New-Project\|Nothing built" skills/derive-roadmap/SKILL.md` prints at least `4`.
- [x] **Step 6: Check the Review Focus pins.** Each command prints `1`:
  - `tr '\n' ' ' < skills/derive-roadmap/SKILL.md | tr -s ' ' | /usr/bin/grep -o 'Judge that system, not the whole repository' | wc -l` (item 1)
  - `tr '\n' ' ' < skills/derive-roadmap/SKILL.md | tr -s ' ' | /usr/bin/grep -o 'the offer goes in the questions block' | wc -l` (item 2)
  - `tr '\n' ' ' < skills/derive-roadmap/references/new-project-entry.md | tr -s ' ' | /usr/bin/grep -o 'label the ranking provisional' | wc -l` (item 2)
  - `tr '\n' ' ' < skills/derive-roadmap/references/roadmap-format.md | tr -s ' ' | /usr/bin/grep -o 'never overwrite it' | wc -l` (item 5)
- [x] **Step 7: Run the gates.** `bash build/run_commit_lints.sh` prints `commit lints passed`.
- [x] **Step 8: Commit**

```bash
git add skills/derive-roadmap
git commit -m "feat(derive-roadmap): add the New-Project Entry for a project with nothing built"
```

- [x] **Step 9: Run the treatment arms** at `HEAD` (write its sha in the record as the arm's sha) for `trigger-stages`, `trigger-decoy`, `dr-offer-scaffold`, `dr-offer-inputs`, `dr-offer-yes`, `dr-built-guard`, `dr-known-progression`, `dr-tracks` and `dr-research-depth`. Build into `/tmp/plan78-work/t3`, run into `specs/red-baseline-new-project-entry/treatment/<case>/`, and copy the build's `MANIFEST.txt` to `treatment/t3-MANIFEST.txt`. Score by the committed rules. Append each case's clause scores, its bar result, VOID reruns and the spend, and apply the bars. A wording round edits only the passage that the failed clause reads and commits it as `fix(derive-roadmap): …`.
> Deviation: One wording round ran (`3ca7344`). Three cases still missed their bar, and the owner ruled "Record and continue" (2026-11-06). The controller committed the arms and the record (Step 10) after that ruling. See "Task 3 summary and owner gate" in `specs/red-baseline-new-project-entry.md`.
- [x] **Step 10: Commit**

```bash
git add specs/red-baseline-new-project-entry specs/red-baseline-new-project-entry.md
git commit -m "test(specs): treatment arms for derive-roadmap's New-Project Entry"
```

### Task 4: resume and completion for new-project roadmaps

**Files:**
- Modify: `skills/derive-roadmap/SKILL.md` §5 (`:143-169`) and §6 (`:173-175`)
- Modify: `README.md:73` (the derive-roadmap row)
- Append: `specs/red-baseline-new-project-entry.md` (Task 4 treatment)

**Interfaces:**
- Consumes: Task 3's format names: `Outcomes`, `Leaves out`, `## Ranked list — Track <X>` and the findings file in a core stage's `Produces`.

- [x] **Step 1: Show the gap.** `tr '\n' ' ' < skills/derive-roadmap/SKILL.md | tr -s ' ' | /usr/bin/grep -o "no Ranked list waiting\|A research track waiting on its Ranked list\|stopped track" | wc -l`.
Expected: `0`.
- [x] **Step 2: Edit §5 and §6.**
  - Amend (`:143-144`), then re-wrap the bullet:

```text
old:    When a Handoff bullet changes a later stage's `Spec`, `Consumes`, `Produces` or `Exit`, amend that entry
new:    When a Handoff bullet changes a later stage's `Spec` (or `Outcomes`), `Consumes`, `Produces`, `Exit` or `Leaves out`, amend that entry
```

  - Between the **Commit** bullet (ends `goes to prepare-handoff.`, `:157`) and `Then hand off the next stage (§4).`, a new paragraph:

```text
**A research track waiting on its Ranked list** (a new-project roadmap). When
every committed stage of a research track is ticked and its Ranked list is
not empty, do not go to §6 for that track. Read the findings file that its
core stage's `Produces` names, and report what the core found and its
measured cost. Then, inside the ONE question of the Ask, put a re-ranking of
the list and your proposed next stage (one item to promote), or stopping the
track. A promoted item becomes a stage entry only after the answer. When your
partner stops the track, its remaining items park, one deferred item each,
under the Parking rule below.
```

  - `:159`: `With every stage ticked, go to §6.` becomes `With every stage ticked and no Ranked list waiting, go to §6.`
  - Parking (`:161-166`): `Remaining unticked stages append to` becomes `Remaining unticked stages, and the items of a stopped track's Ranked list, append to`. `one item per stage` becomes `one item per stage or list item`. `a `Done when:` naming the stage's Produces` becomes ``a `Done when:` naming the stage's Produces or the item's outcome``. Re-wrap the paragraph.
  - §6, after the sentence that ends `deferred_items entries).` (`:175`): `In a new-project roadmap, run it over the Outcomes list in place of spec requirements. Ranked-list items your partner never promoted have parked (§5).`
- [x] **Step 3: Check.** Step 1's command prints `3`. The body measures at most 20,000 characters (Task 3 Step 5's command).
- [x] **Step 4: Edit the README row** (`README.md:73`). `The rubric in `references/gap-rubric.md` has four classes: implemented-as-specified, implemented-differently, missing, and in-code-but-not-in-spec.` becomes ``The rubric in `references/gap-rubric.md` has five classes: implemented-as-specified, implemented-differently, missing, in-code-but-not-in-spec, and out-of-repo.`` At the end of the row, before ` |`, add: ` For a project with nothing built, its New-Project Entry takes the outcomes in plain words, splits unrelated ones into tracks, adds rough cost notes and asks for a ranking. A known progression then gets every stage, and a research track gets only its core stage until that stage has run on real data.`
- [x] **Step 5: Run the gates.** `bash build/run_commit_lints.sh` prints `commit lints passed`.
- [x] **Step 6: Commit**

```bash
git add skills/derive-roadmap/SKILL.md README.md
git commit -m "feat(derive-roadmap): resume and complete new-project roadmaps with ranked lists"
```

- [x] **Step 7: Run the treatment arms** at `HEAD` for `dr-resume-rerank` and `dr-resume-legacy`, as in Task 3 Step 9, with `t4` in place of `t3`. Score, append and apply the bars. Task 3's cases decide at entry, §1 and §7, which this task does not touch. The record says so in one line, in place of re-running them.
- [x] **Step 8: Commit**

```bash
git add specs/red-baseline-new-project-entry specs/red-baseline-new-project-entry.md
git commit -m "test(specs): treatment arms for the new-project resume"
```

### Task 5: describe-critique-methodology routes a system with nothing built

**Files:**
- Modify: `skills/describe-critique-methodology/SKILL.md:43` (insert after), `:47-50`, `:97` (insert after), `:139` (insert after), `:158` (insert after)
- Modify: `build/test_runtime_support.py` (`SOFT_REFERENCES`)
- Modify: `README.md:72` (the describe-critique-methodology row)
- Append: `specs/red-baseline-new-project-entry.md` (Task 5 treatment)

**Interfaces:**
- Consumes: Task 3's §7 name, cited as `derive-roadmap's New-Project Entry`; the definition from Global Constraints.

- [x] **Step 1: Show the gap.** `/usr/bin/grep -c "New-Project" skills/describe-critique-methodology/SKILL.md`.
Expected: `0`.
- [x] **Step 2: Edit `SKILL.md`.** Wrap like the text around each edit.
  - After the Mode selection paragraph (ends `Otherwise, Describe mode.`, `:43`), two paragraphs: first the definition from Global Constraints, verbatim, then:

```text
**Built systems only.** When the system has nothing built, there is no method
to critique yet. Route the work to derive-roadmap's New-Project Entry, as each
mode's first step says, and stop: the critique comes after the system is
built. If derive-roadmap is not installed, say so and stop.
```

  - Describe step 1 (`:47-50`) becomes:

```text
1. **Check that something is built, then choose granularity.** If the system
   you would describe has nothing built, say so, write no description, and
   route to derive-roadmap's New-Project Entry. Otherwise choose granularity
   up front — module (one estimand, one procedure) or system (composed
   components) — and announce the choice and the target. If `$LLM_WIKI_ROOT`
   is set, run the pre-flight in `references/wiki-touchpoints.md` first.
```

  - After `## Synthesize mode` (`:97`), before step 1:

```text
**First, check what the files are.** When the "description" is a brief or a
design for something with nothing built, or the "critique" is research
written in answer to such a brief, say so. Write no triage table and no spec.
Route the files to derive-roadmap's New-Project Entry as background, and stop.
```

  - Quick reference, after `| A new-functionality idea | — | brainstorming, not this skill |`: `| A system with nothing built, or a brief and research written for one | — | derive-roadmap's New-Project Entry, not this skill |`
  - Common mistakes, after the bullet that ends `Never implement critique points directly.` (`:158`):

```text
- **Describing or synthesizing a system with nothing built** — there is no
  method to critique yet. Route it to derive-roadmap's New-Project Entry; the
  critique comes after the system is built.
```

- [x] **Step 3: Declare the soft edge.** In `SOFT_REFERENCES`, after the `('skill:derive-roadmap', 'skill:writing-plans')` entry:

```python
  # Routes a system with nothing built to the New-Project Entry; both modes run
  # without it on a built system, and the text stops when it is absent.
  ('skill:describe-critique-methodology', 'skill:derive-roadmap'),
```

- [x] **Step 4: Check.** The one-definition check in Global Constraints prints one line: the count `2`, then the definition. `tr '\n' ' ' < skills/describe-critique-methodology/SKILL.md | tr -s ' ' | /usr/bin/grep -o "derive-roadmap's New-Project Entry" | wc -l` prints `5`. `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies` passes. The body measures at most 20,000 characters.
- [x] **Step 5: Edit the README row** (`README.md:72`). At the end of the row, before ` |`, add: `` A system with nothing built goes to `derive-roadmap`'s New-Project Entry instead, because the critique comes after the system is built.``
- [x] **Step 6: Run the gates.** `bash build/run_commit_lints.sh` prints `commit lints passed`.
- [x] **Step 7: Commit**

```bash
git add skills/describe-critique-methodology/SKILL.md build/test_runtime_support.py README.md
git commit -m "feat(describe-critique-methodology): route a system with nothing built to derive-roadmap"
```

- [x] **Step 8: Run the treatment arms** at `HEAD` for `dcm-describe-route` and `dcm-synth-route`, as in Task 3 Step 9, with `t5`. Score, append and apply the bars.
> Deviation: Both cases met their bar only on the readings applied. The record states the other readings and their counts for the owner.
- [x] **Step 9: Commit**

```bash
git add specs/red-baseline-new-project-entry specs/red-baseline-new-project-entry.md
git commit -m "test(specs): treatment arms for describe-critique-methodology's routes"
```

### Task 6: brainstorming hands a new multi-stage project to the roadmap

**Files:**
- Modify: `skills/brainstorming/SKILL.md:48` (insert after), `:217` (insert after), `:228` (insert after), `:236-237`, `:322-323`
- Modify: `build/test_runtime_support.py` (`SOFT_REFERENCES`)
- Modify: `NOTICE` (the superpowers "Changes from upstream" list)
- Append: `specs/red-baseline-new-project-entry.md` (Task 6 treatment; All arms side by side)

**Interfaces:**
- Consumes: Task 3's §7 name.

- [x] **Step 1: Show the gap.** `/usr/bin/grep -c "derive-roadmap" skills/brainstorming/SKILL.md`.
Expected: `0`.
- [x] **Step 2: Edit `SKILL.md`.** Wrap at about 72 columns, like the file.
  - After the paragraph that ends `once they've opted out of the questions.` (`:48`):

```text
One kind of work takes a different path. A new project of several stages,
with nothing built yet, goes to derive-roadmap's New-Project Entry once its
outcomes are clear, in place of steps 1 to 4 (see Size the Work).
```

  - Size table, after the `| A project | … |` row (`:217`):

```text
| A new project of several stages, with nothing built yet | none here: the roadmap file is the record | no design to approve: derive-roadmap's New-Project Entry, in this session |
```

  - After the paragraph `**A small change stays here.** …` (ends `No `specs/` file, no fresh session.`, `:228`):

```text
**A new project of several stages goes to a roadmap.** When nothing of
it works end to end on real data yet and your human partner's outcomes
are clear, don't lay out approaches for the whole project or write a
full design. Hand it to derive-roadmap's New-Project Entry in this
session, with their outcomes in their own words. The roadmap file is the
only written record. How each stage gets built is settled later, in that
stage's own brainstorming session or plan. If derive-roadmap is not
installed, size it as a project.
```

  - `:236-237`: after `brainstorm them one at a time.` add `A new project of several stages with nothing built goes to the New-Project Entry whole, and it splits unrelated outcomes into tracks.`
  - HARD-GATE (`:322-323`): after `writing-plans, in a fresh session, and no other skill.` add `A new project of several stages with nothing built has no spec: it goes to derive-roadmap's New-Project Entry in this session, which builds nothing.`
- [x] **Step 3: Declare the soft edge.** In `SOFT_REFERENCES`, between the `('skill:brainstorming', 'command:deferred')` and `('skill:brainstorming', 'skill:writing-plans')` entries:

```python
  # Hands a new project of several stages with nothing built to the New-Project
  # Entry; every other path works without it, and the text sizes the work as a
  # project when it is absent.
  ('skill:brainstorming', 'skill:derive-roadmap'),
```

- [x] **Step 4: Check.** `tr '\n' ' ' < skills/brainstorming/SKILL.md | tr -s ' ' | /usr/bin/grep -o "derive-roadmap" | wc -l` prints `5`. Review Focus item 4: `tr '\n' ' ' < skills/brainstorming/SKILL.md | tr -s ' ' | /usr/bin/grep -o 'several stages' | wc -l` prints `5`. The brainstorming body measures at most 20,000 characters. The declared-dependencies test passes (Task 5 Step 4's command).
- [x] **Step 5: Append the NOTICE bullet** after the plan 77 bullet and before the blank line above `brainstorming/`, dated with the commit's date:

```text
  - Plan 78 (<YYYY-MM-DD>) gave brainstorming a route for a new project
    of several stages with nothing built yet. Once the outcomes are
    clear, it hands the project to derive-roadmap's New-Project Entry in
    the same session, in place of the approaches, the written design and
    writing-plans. The paragraph after the ordered list, Size the Work
    (its table and one paragraph), the several-projects sentence and the
    HARD-GATE carry it. The change is local, and no upstream text was
    taken.
```

- [x] **Step 6: Run the gates.** `uv run python build/check_provenance.py` passes, and `bash build/run_commit_lints.sh` prints `commit lints passed`.
- [x] **Step 7: Commit**

```bash
git add skills/brainstorming/SKILL.md build/test_runtime_support.py NOTICE
git commit -m "feat(brainstorming): hand a new multi-stage project with nothing built to derive-roadmap"
```

- [x] **Step 8: Run the treatment arms** at `HEAD` for `bs-route` and `bs-guard`, as in Task 3 Step 9, with `t6`. Score, append and apply the bars. Then add "All arms side by side" to the record: one row per case with its kind, control and treatment scores per bar clause, bar result, and the clean-control flag. Add the spend total.
- [x] **Step 9: Commit**

```bash
git add specs/red-baseline-new-project-entry specs/red-baseline-new-project-entry.md
git commit -m "test(specs): treatment arms for brainstorming's route and the side-by-side table"
```

> Deviation: Task 7 was added at the completion gate (owner: "Fix all four now", 2026-11-06). Its first commit (`f824492`) closed four routing defects that two task reviewers, Codex and the final code-reviewer found in the approved text of Tasks 3 and 4. A fix round (`d3fc772`) closed four gaps in the Task 7 text itself. Nine, then four, derive-roadmap cases were re-run. See "Treatment: Task 7" in `specs/red-baseline-new-project-entry.md`.
