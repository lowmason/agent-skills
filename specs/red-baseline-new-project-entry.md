# Plan 78 micro-tests: derive-roadmap's New-Project Entry

This record holds the micro-tests for plan 78 (`specs/plans/78-derive-roadmap-new-project-entry.md`). A micro-test
runs one decision many times through a fresh `claude -p` with no tools. Then a person reads each reply by a rule
that was fixed and committed before any rep ran. A rep is one such run.

Plan 78 gives derive-roadmap a second entry, the New-Project Entry, for a project with nothing built. It also routes
brainstorming and describe-critique-methodology to that entry. The spec is `specs/derive-roadmap-new-project-entry.md`.
Each case below cites the spec requirement (`R<n>`) or verification item (`V<n>`) that it checks.

Task 1 builds the kit, registers the 15 cases and their reading rules, runs the isolation probe and sets the per-rep
spend cap. Task 2 runs the control arms. Tasks 3 to 6 each run their treatment arms and append their own sections.

> **Quarantine.** This plan, the spec and the record `specs/red-baseline-new-project-entry.md` with its folder name
> the cases, the pass rules and the expected behavior. Keep them out of every prompt, and quarantine them during any
> later micro-test of derive-roadmap, describe-critique-methodology or brainstorming.

(Copied from the plan's header.)

## Base and drift

`BASE` is the commit that the control arms read every text from. It is the execution branch's start commit:
`1844bd8` (`1844bd8450200949e1999d1422f3b669e55a5cca`), on `claude/roadmap-methodology-scope-c00eab`.

The plan took its line anchors at `da5b21b`. The drift check is
`git diff --stat da5b21b 1844bd8 -- skills/derive-roadmap skills/describe-critique-methodology skills/brainstorming build/test_runtime_support.py README.md NOTICE`.
It printed nothing. No file that the plan edits changed, so every anchor holds and no deviation note is needed.

## Kit

Kit: `specs/red-baseline-new-project-entry/kit/`. Three files are copies of plan 77's kit
(`specs/red-baseline-audit-p2/kit/`). No file of plan 77's kit was edited.

- `run_reps.sh` changes its temp prefix to `/tmp/plan78-rep-` and names plan 78 in its comments. It keeps plan 77's
  `env -i` form (plan 77's Deviation (a)): only `HOME`, `USER`, `LOGNAME`, `PATH`, `SHELL`, `TMPDIR` and `LANG` pass
  through, each only when it is set, plus `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`.
- `isolation_probe.txt` is an unchanged copy.
- `show_reps.py` names plan 78. Its reading aids flag `derive-roadmap`, `New-Project`, `nothing built`, `rank`,
  `Leaves out`, `Ranked list`, `manifest`, `traceab`, `point-in-time`, `triage`, `notation` and `approach`. An aid
  only points the reader at a reply. It is never a verdict.
- `build_prompts.py` is plan 77's builder with the three changes of plan 78 Task 1 Step 2:
  - **Skills listing.** Every prompt carries, after the frame's first line, the block
    `Skills available in this session, as your skill listing shows them (name: description):`. It has one line per
    skill for brainstorming, creative-thinking, derive-roadmap, describe-critique-methodology, design-architecture,
    executing-plans, subagent-driven-development and writing-plans, in that order. Each description is read from the
    skill's frontmatter at the arm's sha. The kit is stdlib only, so the builder reads a folded (`description: >`)
    block by hand and refuses any other form. In the leak view, each description is the placeholder.
  - **Case-repository files.** `repo_file(repo, commit, path, excerpt=None)` reads with
    `git -C "$CASE_REPOS/<repo>" show <commit>:<path>`. It refuses when `CASE_REPOS` is unset or the read fails. With
    `excerpt`, it returns the file's first line, every Markdown heading line outside a code fence, the first
    `excerpt` characters, and then `[excerpt: <excerpt> of <N> characters]`, where `N` is the file's length in
    characters. A first line that is a heading shows twice: once as the first line, once in the heading list. Each
    read adds a `MANIFEST.txt` line with the repository URL, the full commit sha, the path and the sha256 of the text
    used. A fixture places a file's text with a `{file:<key>}` marker that the case maps to a `repo_file` call. A
    case file with a `derive` function adds a second line, the sha256 of the derived text. The leak view keeps these
    files, because they are fixture, not text under test.
  - **No texts.** A case whose `texts` list is empty (the two trigger cases) gets no text block.

  One further change is not in Step 2: every `git` call decodes its output as UTF-8, and every prompt and
  `MANIFEST.txt` is written as UTF-8. Plan 77's builder used the platform's default encoding. The prompts hold
  non-ASCII text (`→`, `—`, `§`), so the builder names the encoding and does not depend on the locale.
- `cases.py` is new. It holds the 15 cases, the VOID rule (when a rep is thrown out and rerun, not scored), the two
  bars and the derivation of the embedding-data gap table.

Commands, from the repository root:

- `CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py <sha> <out-dir> [<case> ...]`
  builds the prompts at a sha and writes `MANIFEST.txt`. `build_prompts.py leakview <out-dir>` builds the leak view.
- `bash specs/red-baseline-new-project-entry/kit/run_reps.sh <prompt> <out-dir> <first> <last> claude-opus-5-5 <cap>`
  runs the reps.
- `uv run python specs/red-baseline-new-project-entry/kit/show_reps.py <dir> ...` prints each rep for reading.

Each rep is a fresh `claude -p --model claude-opus-5-5 --tools "" --strict-mcp-config --setting-sources ""
--no-session-persistence --output-format json --max-budget-usd <cap>` under `env -i`. It runs from a new, empty
directory under `/tmp`, outside every repository. There are 5 reps per case and arm. Every verdict is read by hand
from the full reply. No kit file is named `test_*.py`.

## Arms

- `control`: every text at `BASE` (`1844bd8`). Task 2 runs it before any skill file changes.
- `treatment`: every text at the commit that its task has just made. Tasks 3, 4, 5 and 6 each write that sha here.

Both arms use the same frame, listing order, fixture and task. Only the sha of the texts and of the listing's
descriptions differs. A SKILL.md enters as its body, with the frontmatter removed. A reference file enters whole.

Text sets:

- **DR**: `skills/derive-roadmap/SKILL.md` and `skills/derive-roadmap/references/*.md`. At `BASE` the glob gives
  `gap-rubric.md` and `roadmap-format.md`. Task 3 adds `new-project-entry.md`, which the glob then picks up.
- **DCM-D**: `skills/describe-critique-methodology/SKILL.md` and its `references/methodology-template.md`.
- **DCM-S**: the same SKILL.md and its `references/spec-synthesis.md`.
- **BS**: `skills/brainstorming/SKILL.md`.
- **none**: the skill listing only (the two trigger cases).

## Bars and clause kinds

Each case's clauses are of three kinds:

- A **bar** clause is one that the change must fix. For an additive case, a control failure on a bar clause is the
  RED (failing) baseline.
- A **conformance** clause is one that the treatment must also pass. A control failure on it does not count as RED.
- A **recorded** clause is scored and written down, but it never counts toward a bar. Only `dr-known-progression`
  has one (clause E).

Each case has one of two bars, from plan 78's Global Constraints:

- **Additive bar.** The treatment passes every bar clause and every conformance clause in at least 4 of 5 reps, and
  the control fails a bar clause in at least 1 of 5.
- **Non-regression (guard) bar.** A rep passes when it meets the whole PASS rule. The treatment passes at least as
  many reps as the control, minus one.

For both bars:

- A control with no failure never reverts a change. The spec is owner-approved and requires the behavior, so
  writing-skills' "nothing to fix, stop" rule gives way. The clean control is recorded and put to the owner at the
  plan completion gate (plan 77's rule).
- A treatment below its bar gets one wording round with the case's rule unchanged, then an owner ruling. A wording
  round re-runs the treatment of every case in its task whose decision the changed passage can reach. The record
  says why each other case of that task was not re-run.

## Spend

The controller keeps the running total here. Stop and ask the owner before the total passes **$60**, and when the
control arms alone pass **$30**. An unreadable or empty rep file counts at its cap. Task 1 Step 6 sets the per-rep
cap from a cost pilot.

Per-rep cap: **$1.00** (Task 1 Step 6, below). It is in every case's `budget` in `cases.py`.

| Item | Reps | Cap per rep | Worst case | Spent |
|---|---|---|---|---|
| Task 1 Step 5, isolation probe | 1 | $1.00 | $1.00 | $0.0141 |
| Task 1 Step 6, cost pilot | 1 | $3.00 | $3.00 | $0.2821 |

Running total after Task 1: $0.2962 of $60 (`show_reps.py` prints $0.30). Control arms: $0.00 of $30. The cost pilot
read a control prompt, but it is not a control-arm rep: Task 2 does not count or score it. Counted against the $30
as well, it would make the control total $0.28.

## Fixture sources

The case-study repositories are public: `https://github.com/lowmason/sec-edgar`,
`https://github.com/lowmason/embedding-data` and `https://github.com/lowmason/ces-revisions`. The builder reads them
at build time from local clones under `$CASE_REPOS`, read only. Nothing from them is committed here except the
hand-written state lines in `cases.py` and the replies that the reps write. Each build's `MANIFEST.txt` records the
repository URL, the full commit, the path and the sha256 of every file it read.

| Repository | Commit | Files read | Cases |
|---|---|---|---|
| sec-edgar | `22c6767f` (`22c6767fb31de72eff8efbce4e2c20fa6c31508e`), its one commit | `specs/sec-filing-index-ingestion-spec.md`, whole | dr-offer-scaffold, dr-offer-yes, dr-known-progression, dcm-describe-route |
| embedding-data | `af7bf21` (`af7bf21d5522e0cd5cf3fbc72419ad77b436aa7e`), the parent of `4bc8cda` | `specs/embedding-evaluation-data-spec.md`, whole | dr-offer-inputs |
| embedding-data | `4bc8cda` (`4bc8cda6d594190a9bfb5d3cf993722cb105c9f9`) | `specs/embedding-evaluation-data-spec-roadmap.md`, its Gap analysis section only, derived (below) | dr-offer-inputs |
| ces-revisions | `0e24ecc` (`0e24ecc866e1d507373b01ef6c1a9d7962ae9b61`), the parent of `237b426` | `specs/ces-revisions-prompt.md` whole; `specs/ces-revisions-research-{chatgpt,claude,gemini}.md` as 3,000-character excerpts | dr-tracks, dr-research-depth, dcm-synth-route |

The other cases use constructed fixtures, each in its own domain: building permits (`trigger-stages`), a timesheet
tool (`trigger-decoy`), a museum's visitor-count forecaster (`dr-built-guard`), canal lock closures and river-gauge
levels (`dr-resume-rerank`), a parking-sensor occupancy pipeline (`dr-resume-legacy`), a tide-gauge archive
(`bs-route`) and GPX tracks (`bs-guard`).

**Hand-written state lines.** The tree lines of `sec-edgar`, `embedding-data` and `ces-revisions` are hand-written
from what `git show` and `git ls-tree` print at the commits above. They state facts, never a verdict that a case
scores. The `embedding-data` module lines quote each module's docstring, as the plan asks. Its test modules have no
docstring, so their lines say so and name the module each one imports.

**Deviation (a): the sec-edgar scaffold facts.** The plan's Step 3 says that the `[you, tools]` lines give every
`__init__.py` and `README.md` as empty and each `pyproject.toml` as declaring a name only. At `22c6767f`, every
`README.md` and `py.typed` is empty, but each `__init__.py` holds the two-line `hello()` stub that `uv init` writes.
Each `pyproject.toml` also holds version 0.1.0, the placeholder description and `dependencies = []`. The root one
also lists the four workspace members and a script entry for a module that does not exist. The fixture rule is
"facts only", so the lines state these facts. For the same reason, the gap-analysis evidence reads "no code beyond
the generated package scaffolds", not "no code beyond empty package scaffolds". No author detail from the
`pyproject.toml` files enters a fixture.

**The embedding-data gap table (`cases.gap_table_without_stages`).** `dr-offer-inputs` shows the Gap analysis table
of the `4bc8cda` roadmap, with its key, as the gap analysis that the agent ran. The function derives it from the
`repo_file` text at build time and only deletes text. It never adds prose. The rules:

1. Keep the section's key (`acs`, `cps`, `osha`) and its table. Keep nothing after the table: the owner's answers
   and the order note stay out.
2. Edit the Note column only. Split each note at `;`. In a segment with a pointer (`→ S<n>` and what follows it),
   delete the pointer. Keep the text before the arrow when it is a statement (4 words or more) or reports a check as
   unrecorded. A shorter text is the label of the pointed-to stage's work (`build`, `V1`, `Codes`), so it goes with
   the pointer. Delete a segment with no arrow that names a stage (`first in S6`, `Seeded S6`).
3. Empty the whole note of one row: the `in-code-but-not-in-spec` row whose Evidence cell is
   `` `osha` case-detail command `` (`LEAK_VERDICT_ROWS` in `cases.py`). The reason is the plan's leak rule for this
   case. A hit in the table's notes stays only where it is historical evidence and not a verdict. That note, "Kept;
   recorded in spec as acquired, feeding no target", is a verdict that clause B scores (leak word `acquir`). The
   other two `in-code-but-not-in-spec` rows go through rule 2 only, as every other row does. Their notes become
   "Moves out of `data/raw`" and "Retained; R4.4 motivates later starts". (Amendment 1 changed this rule.)
4. Refuse the build when an arrow or a stage reference (`S<n>`, `stage`) survives in a note, or when the row of
   rule 3 is not found.

**The lock-closures roadmap.** `dr-resume-rerank` needs a new-project roadmap before Task 3 adds that format. Its
fixture follows the format text of plan 78 Task 3 Step 4. Stage 1's Handoff reads `None`, so its COMPLETE stamp has
no Handoff sentence (`references/roadmap-format.md`). It has one track, so its stage entry has no `Track:` field.

## Leak check

The leak view was built with
`CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py leakview /tmp/plan78-work/leak`.
It is the one leak build. The check ran in two parts:

1. Each case's hand-written fixture lines and task line, from `cases.py`, were grepped case-insensitively for its
   leak words. Every case had 0 hits.
2. Each leak-view prompt was grepped case-insensitively (`re.I`, the same as `grep -i -E`) for its case's leak words.
   Each hit was traced to its source.

| Case | Leak words | Hits in the leak view | Verdict |
|---|---|---|---|
| trigger-stages | `New-Project`, `nothing built`, `outcome` | none | none needed |
| trigger-decoy | `New-Project`, `nothing built`, `outcome` | none | none needed |
| dr-offer-scaffold | `New-Project`, `nothing built`, `outcome`, `rank` | 6 × `outcome`, all in the sec-edgar spec's own text: "run outcome", "terminal outcome", the Attempt row's "outcome", "Named outcomes", "gated outcome" and "no-new-source outcomes" | exempt: a case-repository file read verbatim |
| dr-offer-inputs | as dr-offer-scaffold, plus `only`, `end to end`, `acquir` | 26 in the embedding-data spec's own text (22 × `only`, 2 × `acquir`, 1 × `outcome` in "Observable outcomes", 1 × `rank` in "rank correlations"); 5 in the derived gap table (below) | spec hits exempt: a case-repository file read verbatim. Table hits: below |
| dr-offer-yes | `New-Project`, `Leaves out`, `core stage` | none | none needed |
| dr-built-guard | `New-Project`, `nothing built`, `outcome` | none | none needed |
| dr-known-progression | `Leaves out`, `core stage`, `later stage`, `final-standard`, `hardening` | none | none needed |
| dr-tracks | `New-Project`, `research track`, `separate track` | none | none needed |
| dr-research-depth | `core stage`, `measured cost`, `Leaves out` | none | none needed |
| dr-resume-rerank | `re-rank`, `promote`, `stop the track` | none | none needed |
| dr-resume-legacy | `re-rank`, `promote`, `stop the track` | none | none needed |
| dcm-describe-route | `New-Project`, `nothing built` | none | none needed |
| dcm-synth-route | `New-Project`, `nothing built`, `background` | 1 × `background`, in `specs/ces-revisions-prompt.md`: "Do not pad with background the reader already knows" | exempt: a case-repository file read verbatim |
| bs-route | `New-Project`, `roadmap`, `nothing built` | 1 × `roadmap`, in the listing line `- derive-roadmap: [text under test]` | exempt: the listing's skill name |
| bs-guard | `New-Project`, `roadmap`, `nothing built` | 1 × `roadmap`, in the listing line `- derive-roadmap: [text under test]` | exempt: the listing's skill name |

No hit came from a hand-written line, so no line was reworded and no rebuild was needed.

**dr-offer-inputs, the gap table.** The plan checks `only`, `end to end` and `acquir` in the table's notes. It keeps
a hit only where the hit is the historical evidence and not a verdict. The source table at `4bc8cda` has three such
hits in its notes:

- R1.1, "ACS, CPS acquired; ITA acquisition is 2025 case detail, not 300A" (`acquir`): kept. It is the historical
  evidence of what the code at `af7bf21` downloads.
- R9.1, "Names `acs`, `cps` only" (`only`): kept. It is the historical evidence of the CLI's command names.
- The `osha` case-detail row (Req `—`), "Kept; recorded in spec as acquired, feeding no target" (`acquir`): removed
  by rule 3 of the derivation, because "feeding no target" is a verdict that clause B scores.

Three more hits sit in the Evidence column, outside the notes: R2.4 "2025 only", R3.4 "US samples only" and R8.2
"README links terms only". Each is the historical evidence of its row and is kept. `end to end` has no hit.

After Amendment 1, the leak view of dr-offer-inputs was rebuilt into `/tmp/plan78-work/leak-2` and grepped again.
The hits are the same 26 in the spec text and the same 5 in the table. The two restored notes, "Moves out of
`data/raw`" and "Retained; R4.4 motivates later starts", have no hit. No hit is in a hand-written line.

## Reading rules

These rules were registered and committed before any rep ran. Fixtures and rules are not edited after any rep
output is seen.

**VOID (every case).** VOID, rerun with the next free rep number and not scored, when any of these hold: show_reps.py's header for the rep says VOID (a tool or the advisor ran, or the run errored or stopped on its budget); the JSON is unreadable or its result is empty; the run timed out or exited without writing JSON; the model refuses the task; or the reply does no part of the task (no reply, no message and no tool call).

This VOID rule is copied unchanged from plan 77's `cases.py`. A rerun happens only within the spend stops. The
scored reps of a case are its first 5 reps that are not VOID.

Unless a case gives its own task, the task line is:

> It is your turn. You have no tools in this turn, so write any tool call as text. Write your next message to your partner.

### trigger-stages

Spec ref: R13d. Kind and bar: additive. Texts: none (the skill listing only).

Fixture: A new repository holds a one-line README.md. The partner asks to pull building-permit records from three county portals into one table, update them every month and put a public summary page on top. Nothing exists yet. "Can you lay out the stages for this?"

Task: `Name the skill you invoke first, if any, and give one sentence why. Then stop.`

Leak words: `New-Project`, `nothing built`, `outcome`.

PASS needs one bar clause. Clause A (bar): the first skill named is derive-roadmap.

Reading notes. The first skill named is the first skill that the reply says it invokes. A reply that names no skill fails.

### trigger-decoy

Spec ref: R13d guard. Kind and bar: non-regression (guard). Texts: none (the skill listing only).

Fixture: A new repository holds a one-line README.md, so nothing is built. The partner asks for a small command-line tool that totals the hours in a timesheet CSV. The request is clearly one cycle.

Task: `Name the skill you invoke first, if any, and give one sentence why. Then stop.`

Leak words: `New-Project`, `nothing built`, `outcome`.

PASS (guard): the first skill named is brainstorming.

Reading notes. As trigger-stages: the first skill named is the first skill that the reply says it invokes. A reply that names no skill fails.

### dr-offer-scaffold

Spec ref: V1, R1b. Kind and bar: additive. Texts: DR.

Fixture: sec-edgar at `22c6767f`. The partner asks to derive the roadmap for `specs/sec-filing-index-ingestion-spec.md`. The `[you, tools]` lines give the tree and the scaffold facts (Deviation (a)), the spec whole, and the ADR with its decision in one line. The gap analysis has 11 rows, one per numbered requirement (R1 to R11 in the spec's §3), every verdict `missing`. No file under `specs/` carries the roadmap header, and `specs/deferred_items.md` does not exist.

Leak words: `New-Project`, `nothing built`, `outcome`, `rank`.

PASS needs three bar clauses. Other batched questions may come with clause C's question.

Clause A (bar): the reply has no stage partition, stage list or roadmap text, including one offered "for approval".

Clause B (bar): it says, in any words, that no outcome works end to end yet.

Clause C (bar): it asks whether to stage the project from a list of outcomes that the partner ranks, in place of partitioning the requirements, and waits for the answer. It fails C when it switches to that path without asking.

Reading notes. Clause A: a list of named stages, phases or cycles counts, also when it is labeled draft, provisional or "for approval". A list of outcomes with no stage grouping is not a stage list. Clause B: a statement about the system as a whole passes, in any words: that nothing works yet, that nothing is built, or that no code exists beyond the scaffolds. The gap table shown with no such statement does not pass B. Clause C: the question offers the outcome list, ranked by the partner, as the basis for staging in place of a partition of the requirements. A question that asks only which requirements matter most, with a partition to follow, does not pass. "Waits for the answer" means that no stage, partition or roadmap text follows the question in the same message.

### dr-offer-inputs

Spec ref: V1b. Kind and bar: additive. Texts: DR.

Fixture: embedding-data at `af7bf21`: the spec whole, one docstring line per module of `src/` and `tests/`, and a line that pytest (44) and Behave (2) pass and five IPUMS extracts are on disk. The gap analysis is the derived Gap analysis table of the `4bc8cda` roadmap (Fixture sources). The partner line is dr-offer-scaffold's, with this spec's path.

Leak words: `New-Project`, `nothing built`, `outcome`, `rank`, `only`, `end to end`, `acquir`. The last three are checked in the gap table's notes.

PASS needs three bar clauses. Other batched questions may come with clause C's question.

Clause A (bar): the reply has no stage partition, stage list or roadmap text, including one offered "for approval".

Clause B (bar): it says, in any words, that no outcome works end to end yet.

Clause C (bar): it asks whether to stage the project from a list of outcomes that the partner ranks, in place of partitioning the requirements, and waits for the answer. It fails C when it switches to that path without asking.

Reading notes. Clause A: a list of named stages, phases or cycles counts, also when it is labeled draft, provisional or "for approval". A list of outcomes with no stage grouping is not a stage list. Clause B: a statement about the system as a whole passes, in any words: that nothing works yet, that nothing is built, or that no code exists beyond the scaffolds. The gap table shown with no such statement does not pass B. Clause C: the question offers the outcome list, ranked by the partner, as the basis for staging in place of a partition of the requirements. A question that asks only which requirements matter most, with a partition to follow, does not pass. "Waits for the answer" means that no stage, partition or roadmap text follows the question in the same message.

### dr-offer-yes

Spec ref: V1, R4, R5, R15. Kind and bar: additive. Texts: DR.

Fixture: dr-offer-scaffold's fixture, then a summary of the agent's last message: the gap table (all `missing`), the finding that nothing works yet, and the question whether to stage the project from a ranked list of outcomes, with the spec's requirements as candidates. The partner: "Yes, do that."

Leak words: `New-Project`, `Leaves out`, `core stage`.

PASS needs every bar and conformance clause.

Clause A (bar): a numbered list of outcomes in plain words, one line each, drawn from the spec's requirements.

Clause B (bar): the reply gives no ranking of its own, and it asks the partner to rank. The spec's order or list order, labeled as such, passes. A proposed priority order fails.

Clause C (bar): no roadmap text and no stage partition.

Clause D (conformance): at least one cost note with its basis, or a statement that only a run can measure it.

Reading notes. Clause A: an outcome in plain words says what the partner gets; a bare requirement number or a requirement's title alone is not one. A line that wraps is still one line. Clause B: a ranking of its own is any order that the reply recommends, proposes or calls a priority, or a pick of which outcome comes first. Clause C: as dr-offer-scaffold's clause A. Clause D: a basis is what the estimate rests on, such as a file count, a request rate, a data size or a comparable job.

### dr-built-guard

Spec ref: V5. Kind and bar: non-regression (guard). Texts: DR.

Fixture: A museum's visitor-count forecaster. `specs/visitor-forecast.md` has six numbered requirements and no routing header. R1 and R2 are `implemented-as-specified`, with test names and the line that daily counts from the real 2019–2025 turnstile export load and the baseline forecast runs on them end to end. R3 is `implemented-differently`, and R4 to R6 are `missing`. The partner asks to derive the roadmap.

Leak words: `New-Project`, `nothing built`, `outcome`.

PASS (guard): the reply neither says that nothing is built nor offers outcome-first staging, and goes on by the existing flow: the table with any batched questions, a partition, or the single-stage exit.

Reading notes. Outcome-first staging is staging from a list of outcomes that the partner ranks, in place of a partition of the gaps. Saying that R4 to R6 are missing is not saying that nothing is built.

### dr-known-progression

Spec ref: V2, R7-R9. Kind and bar: additive. Texts: DR.

Fixture: sec-edgar at `22c6767f`: the tree, the spec whole as background, and the ADR line. The partner asks for a roadmap for SEC filing ingestion, says nothing exists beyond the package scaffolds, and gives the progression: the quarterly and daily index files, then the individual submissions, then 10-K and 8-K handling. A summary of the agent's last message follows: the outcome list with cost notes, one known-progression track, the name `sec-filing-ingestion`, and a request to rank. The partner: "Rank them in the order I gave. One track, a known progression. The name is fine."

Task: `It is your turn. You have no tools in this turn. Write the full roadmap file you will commit now, as Markdown, then the one-line message you send with it.`

Leak words: `Leaves out`, `core stage`, `later stage`, `final-standard`, `hardening`.

PASS needs every bar and conformance clause. Clause E is recorded and never scored.

Clause B (bar): the first stage's Exit requires no manifest, no traceability (a provenance or lineage record per row) and no point-in-time (as-of) awareness. A quality named as left out passes.

Clause A (conformance): committed stages cover, in order, the index files, the individual submissions, and 10-K and 8-K handling.

Clause C (conformance): manifests, traceability and point-in-time awareness each appear in a named later stage.

Clause D (conformance): every stage entry has a field that names what it leaves out and where that goes.

Clause E (recorded, no bar): the first stage's Exit does not require complete dataset generations to publish atomically. The background spec's §1 asks for that, and the skill text does not name it, so E checks transfer.

Reading notes. Clause B reads the first stage's Exit field, or the criteria that the reply gives for finishing the first stage when it has no field of that name. A manifest of any kind (source, run, ingestion or publication) fails B. Per-row provenance columns, such as a source id or a source hash, are traceability and fail B. A quality that the first stage names as not required, or as left out, passes. Clause A: committed stages are the stage entries of the roadmap file. Clause C: a named later stage is a stage entry after the first whose fields name the quality. Clause D: the field may have any name.

### dr-tracks

Spec ref: V3, R4. Kind and bar: additive. Texts: DR.

Fixture: ces-revisions at `0e24ecc`: the tree (a package scaffold and smoke tests), `specs/ces-revisions-prompt.md` whole and the three research files as 3,000-character excerpts. An `[earlier]` line says that describe-critique-methodology routed the brief and the three research files to derive-roadmap as background, and that nothing is built. The partner: "Go ahead and stage it."

Leak words: `New-Project`, `research track`, `separate track`.

PASS needs every bar and conformance clause.

Clause A (bar): an outcome about collection time or the collection interval and revision size sits in a different track from an outcome about budget, staffing or attrition, and the reply says why.

Clause B (conformance): no ranking is given as settled, and the reply asks the partner to rank.

Clause C (conformance): one message with no roadmap text.

Clause D (conformance): a cost note for model fitting or compute, with a basis or a statement that the core stage measures it.

Reading notes. Clause A: a track is a grouping that the reply says can be ranked, run or stopped on its own. Two stages of one sequence are not separate tracks. "Says why" is any reason given for keeping the two apart. Clause B: an order proposed to the partner for approval is not settled; an order that the reply states as decided is. Clause C: roadmap text is the roadmap file's content or a stage partition; a list of outcomes and tracks is not roadmap text. Clause D: "the core stage measures it" is any statement that the first run on real data measures the cost.

### dr-research-depth

Spec ref: V3, R7, R8. Kind and bar: additive. Texts: DR.

Fixture: dr-tracks' fixture, then a summary of the agent's last message: outcomes O1 to O6, one plain line each, written from the brief; two research tracks (A, collection interval and revision size: O1 to O3; B, budget, staffing and attrition: O4 to O6); the reason for the split; cost notes; and the name `ces-revisions`. The partner: "Tracks are right, both research. Track A first. In Track A: O1, then O3, then O2. In Track B: O6, then O4, then O5. The name is fine."

Task: `It is your turn. You have no tools in this turn. Write the full roadmap file you will commit now, as Markdown, then the one-line message you send with it.`

Leak words: `core stage`, `measured cost`, `Leaves out`.

PASS needs every bar and conformance clause.

Clause A (bar): each track commits exactly one stage, and every other outcome of the track sits in a ranked list, not in a committed stage.

Clause B (bar): each committed stage's Exit names a cost of the real run to measure and record: time, compute or data volume.

Clause C (conformance): the two tracks stay separate.

Clause D (conformance): each stage entry names what it leaves out.

Clause E (conformance): each committed stage's Produces names a file that records the result and the measured cost.

Reading notes. Clause A: a committed stage is a stage entry of the roadmap file, such as a checkbox entry or a numbered stage with its fields. A stage entry labeled provisional, tentative or later still counts as committed. A ranked list is a list kept outside the stage entries, in the partner's order. Clause B: the Exit, or the stage's finishing criteria when it has no field of that name, must require the cost to be measured and recorded; a cost named only as an estimate does not pass. Clause C: no stage entry mixes outcomes of both tracks. Clause E: the file may be named by path or by a plain file name.

### dr-resume-rerank

Spec ref: V6, R11. Kind and bar: additive. Texts: DR.

Fixture: Canal lock closures and river-gauge levels. `specs/lock-closures-roadmap.md` is a new-project roadmap with one research track (Fixture sources). Its Stage 1, the core, is ticked and stamped COMPLETE. Its `## Ranked list — Track A` holds three items. Plan 4's `## Handoff to later stages` reads `None: shipped as the roadmap's Produces states.` The findings file gives a two-line result and the cost of the real run ("one fit on 11 years of daily gauge readings, 1.8 GB, took 22 minutes on a laptop"). The partner: "Resume the roadmap."

Leak words: `re-rank`, `promote`, `stop the track`.

PASS needs every bar and conformance clause.

Clause A (bar): no completion review starts, and the roadmap is neither parked nor retired.

Clause C (bar): one question that asks for a re-ranking of the list or the approval of a proposed next stage from it, with a default.

Clause B (conformance): the reply reports the core's finding and its measured cost.

Clause D (conformance): no new stage entry is written before the answer.

Reading notes. Clause A: a completion review is the audit run before a roadmap retires (derive-roadmap §6). Stopping the track offered as one option of the question is not parking. Clause C: the one question may offer options; a default is the answer that the reply proposes or takes if the partner agrees, such as "Stage 2 is O2 unless you re-order". Two or more separate questions fail C. Clause B: the finding is the 3.1 m level or the steep rise above it; the cost is the 22-minute, 1.8 GB run. Clause D: a new stage entry is a stage entry written into the roadmap text; a proposed stage described in the question is not an entry.

### dr-resume-legacy

Spec ref: R11 guard. Kind and bar: non-regression (guard). Texts: DR.

Fixture: A parking-sensor occupancy pipeline. The roadmap is in today's format: a Gap analysis table, three stages with `Spec` and `Gap closed`, all ticked and stamped COMPLETE, a Completion section and no Ranked list. Stage 3's plan Handoff reads `None`. The partner: "Resume the roadmap."

Leak words: `re-rank`, `promote`, `stop the track`.

PASS (guard): the reply goes to the completion review. It says every stage is complete and starts or proposes the audit over the spec's requirements, and it asks no re-ranking question.

Reading notes. The audit over the spec's requirements is the gap rubric re-run over R1 to R6 (derive-roadmap §6). A re-ranking question asks the partner to order, or pick from, a list of further work.

### dcm-describe-route

Spec ref: V4, R13b. Kind and bar: additive. Texts: DCM-D.

Fixture: sec-edgar at `22c6767f`: the tree and the spec whole. The partner: "Write the methodology description of this filing-index ingestion system for an external SOTA critique."

Leak words: `New-Project`, `nothing built`.

PASS needs three bar clauses.

Clause A (bar): no methodology description, notation table or template slot, and none planned as the next step.

Clause B (bar): the reply says, in any words, that the system has nothing built.

Clause C (bar): it routes to derive-roadmap to stage the project, and says the critique comes after the system is built. A route to brainstorming alone fails C.

Reading notes. Clause A: a template slot is any filled section of the methodology template. A plan to write a description of the spec's design next fails A; such a description offered to the partner as one option of a question does not. Clause B: as dr-offer-scaffold's clause B, said of the filing-index ingestion system. Clause C needs both parts: derive-roadmap named as the next step, to stage the project, and the critique placed after the system is built.

### dcm-synth-route

Spec ref: V3, R13c. Kind and bar: additive. Texts: DCM-S.

Fixture: ces-revisions at `0e24ecc`, as dr-tracks without the `[earlier]` routing line. The partner: "The research is back. Use synthesize mode: the description is specs/ces-revisions-prompt.md and the critiques are the three research files."

Leak words: `New-Project`, `nothing built`, `background`.

PASS needs three bar clauses.

Clause A (bar): no triage table and no spec text, now or as the next step.

Clause B (bar): the reply says that the description is a brief for something not built, or that nothing is built.

Clause C (bar): it routes the files to derive-roadmap as background for staging.

Reading notes. Clause A: a triage table is any table or list that sorts the research files' points into accept, reject, defer or similar verdicts. Spec text is any section of a design spec. A plan to write either next fails A; either one offered to the partner as one option of a question does not. Clause C: the route names derive-roadmap and gives it the brief and the research files as inputs for staging.

### bs-route

Spec ref: R13a. Kind and bar: additive. Texts: BS.

Fixture: A tide-gauge archive, in a fresh repository where nothing exists. The partner's first message, which does not name brainstorming: collect hourly readings from four coastal stations' public feeds, clean and gap-fill them, then publish monthly extremes per station as a CSV and a chart. The agent's first message restated the request and asked who uses it and what success looks like. The answer: a harbor-master group; one year of clean monthly extremes for each station; Python on their laptop; "in the order I said".

Leak words: `New-Project`, `roadmap`, `nothing built`.

PASS needs three bar clauses.

Clause A (bar): the reply hands the project to derive-roadmap in this session, to stage the outcomes: it invokes the skill, or says it does so now.

Clause B (bar): it lays out no approaches for the whole project.

Clause C (bar): it writes no design document or spec file, and asks no question that the conversation already answers.

Reading notes. Clause A: a written Skill call to derive-roadmap, or a statement that it hands over to derive-roadmap now, passes. A handoff put off to a later or fresh session, or only asked about ("shall I use derive-roadmap?"), fails. Clause B: an approach is a way to build the whole project; two or more such ways, or one presented as the design, fail B. Clause C: the conversation already answers who uses it, what success is, the language, where it runs and the order of the work.

### bs-guard

Spec ref: R13a guard. Kind and bar: non-regression (guard). Texts: BS.

Fixture: A small script, in a fresh repository where nothing exists, that reads a folder of GPX track files and writes one CSV with each track's distance and duration. Nothing is built and the work is one cycle, so only the "several stages" test keeps it off the new route (plan 78 Review Focus item 4). The agent's first message asked one question. The answer settles the units and what happens to a file that fails to parse.

Leak words: `New-Project`, `roadmap`, `nothing built`.

PASS (guard): the reply lays out two or three ways to build it, in this message, with a recommendation and one question asking which way to go. It does not hand off to derive-roadmap.

Reading notes. A way to build it is an approach to the whole script, such as a choice of parsing library or of structure. The message asks one question, which way to go; a message with further questions fails.

## Isolation probe (Task 1 Step 5)

`bash specs/red-baseline-new-project-entry/kit/run_reps.sh specs/red-baseline-new-project-entry/kit/isolation_probe.txt specs/red-baseline-new-project-entry/pilot/probe 1 1 claude-opus-5-5 1.00`
ran on Claude Code 2.1.316 (`claude --version` prints `2.1.316 (Claude Code)`), under `env -i`. The rep file is
`pilot/probe/rep1.json`.

All five probe lines read `NO`: no CLAUDE.md text, no output style, no rule, no SessionStart context and no memory.
`show_reps.py` shows one turn, no extra iterations, one model (`claude-opus-5-5`), `success`, and a cost of $0.014.
`claude -p` signed in under `env -i` with the CLI's stored login, so the kit keeps the `env -i` form for every rep.

## Spend calibration (Task 1 Step 6)

1. The control prompts were built with
   `CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py 1844bd8 /tmp/plan78-work/calibrate`.
   Its `MANIFEST.txt` is copied to `pilot/calibrate-MANIFEST.txt`. It shows `budget None`, because the cap did not
   exist yet. Its prompt hashes are the same as those of the sanity build made before the Step 4 commit. It holds
   the hashes of dr-offer-inputs from before Amendment 1, because those are the prompt that the pilot ran.
2. The largest prompt by bytes is `dr-offer-inputs.txt`: 59,366 bytes, sha256
   `9f53553c8d454b55b038db6397ecd18f213dc5775a9e89169dd44e0d37fd1377`. The next two are `dr-known-progression.txt`
   (57,687 bytes) and `dr-offer-yes.txt` (57,194 bytes).
3. One uncounted rep of it ran with a $3.00 cap, into `pilot/dr-offer-inputs/rep1.json`. It ended with `success`, in
   one turn, with no tool and one model. Its `total_cost_usd` is 0.2821344. The prompt wrote 23,336 tokens to the
   cache and read 1,592 from it. The reply had 4,756 output tokens, 2,116 of them thinking. The reply is not scored.
4. Per-rep cap: the larger of $1.00 and 3 × $0.2821 = $0.846, rounded up to the next $0.25. That is **$1.00**. It is
   written into every case's `budget` (`BUDGET` in `cases.py`).
5. Estimate for the full run: 150 × $0.2821344 = **$42.32**, where 150 is 15 cases × 5 reps × 2 arms. The control
   arms alone: 75 × $0.2821 = $21.16. Both are under their stops ($60 and $30), so no owner stop is needed before
   the counted reps. VOID reruns and wording rounds come on top of the estimate.

## Amendment 1 (before any counted rep)

The task review of Task 1 found that rule 3 of the gap-table derivation went past the plan. It emptied the notes of
all three `in-code-but-not-in-spec` rows and said that each records the owner's answers of 2026-10-12. That holds
for the `osha` row and the `data/raw` row. It does not hold for the `cps --start` row: its note is not among the
four owner answers that the `4bc8cda` roadmap records. The plan's fixture rule removes only stage pointers and
stage-naming phrases, and its leak rule removes the `acquir` verdict. The controller ruled:

- The `data/raw` row and the `cps --start` row go through rule 2 only. Each loses its `→ S1` pointer and the label
  before it, and keeps the statement before the arrow.
- The `osha` row's note stays empty, under the plan's leak rule. The code now finds that row by its own Evidence
  cell, not by Req `—`.
- R1.3 and every other row stay as they were.

`cases.py` (`LEAK_VERDICT_ROWS`) and rule 3 above now say this.

- Original rule 3: "Empty the notes of the three `in-code-but-not-in-spec` rows (Req `—`). Each records the owner's
  answer to the batched questions of 2026-10-12, which came after the gap analysis ran. One of them, "recorded in
  spec as acquired, feeding no target", is also a verdict that the case scores (leak word `acquir`)."
- Effect: in the dr-offer-inputs prompt, the `data/raw` row's note changes from empty to "Moves out of `data/raw`",
  and the `cps --start` row's note changes from empty to "Retained; R4.4 motivates later starts". Nothing else in
  any prompt changes. A rebuild at `BASE` into `/tmp/plan78-work/fix1-control` gives a new sha256 for
  `dr-offer-inputs.txt`, `6bbb36f3fbf6ae2b9e0d4e4c500ff8eff7be59a045832350aae109f8d4d5eb4e`. Its derived text is now
  `05fde81b400b1049ddbb02c77b9d3ddb4b0c70d407dfe301f678576bd2bd6b80`. The other 14 prompt hashes are unchanged.

The pilot reply for dr-offer-inputs (`pilot/dr-offer-inputs/rep1.json`) was read in full before this change. The
change moves the fixture toward the brief's literal rule, not toward any outcome of a case. The pilot rep stays
uncounted and unscored. `pilot/calibrate-MANIFEST.txt` keeps the pre-amendment hashes (`9f53553c…` for the prompt,
`fe110c12…` for the derived text), because it records the prompt that the pilot ran. The pass rule of
dr-offer-inputs is unchanged. The cap and the estimate are unchanged: the prompt grows by 62 bytes, from 59,366 to
59,428, and stays the largest. No billed run was made for this amendment.
