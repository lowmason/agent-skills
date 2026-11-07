# Plan 78 micro-tests: derive-roadmap's New-Project Entry

This record holds the micro-tests for plan 78 (`specs/plans/completed/78-derive-roadmap-new-project-entry.md`). A micro-test
runs one decision many times through a fresh `claude -p` with no tools. Then a person reads each reply by a rule
that was fixed and committed before any rep ran. A rep is one such run.

Plan 78 gives derive-roadmap a second entry, the New-Project Entry, for a project with nothing built. It also routes
brainstorming and describe-critique-methodology to that entry. The spec is `specs/completed/derive-roadmap-new-project-entry.md`.
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
| Task 2, control arms (15 cases, 5 reps each, no VOID rerun) | 75 | $1.00 | $75.00 ($5.00 per case call) | $5.5029 |
| Task 3, treatment arms (9 cases in round 1 and 7 in round 2, 5 reps each, no VOID rerun) | 80 | $1.00 | $80.00 ($5.00 per case call) | $8.4719 |
| Task 4, treatment arms (2 cases, 5 reps each, no VOID rerun) | 10 | $1.00 | $10.00 ($5.00 per case call) | $0.5190 |
| Task 5, treatment arms (2 cases, 5 reps each, no VOID rerun) | 10 | $1.00 | $10.00 ($5.00 per case call) | $0.5031 |
| Task 6, treatment arms (2 cases, 5 reps each, no VOID rerun) | 10 | $1.00 | $10.00 ($5.00 per case call) | $0.3376 |
| Task 7, treatment arms after the final-review fixes (9 cases, 5 reps each, no VOID rerun) | 45 | $1.00 | $45.00 ($5.00 per case call) | $4.7589 |
| Task 7 fix round 1, treatment arms (4 cases, 5 reps each, no VOID rerun) | 20 | $1.00 | $20.00 ($5.00 per case call) | $2.1159 |
| **Running total** | 252 | | | **$22.5055 of $60** |
| **Control arms** | 75 | | | **$5.5029 of $30** |

Running total after Task 1: $0.2962 of $60 (`show_reps.py` prints $0.30). Control arms: $0.00 of $30. The cost pilot
read a control prompt, but it is not a control-arm rep: Task 2 does not count or score it. Counted against the $30
as well, it would make the control total $0.28.

Running total after Task 2: $5.7991 of $60 ($5.80). Control arms: $5.5029 of $30 ($5.50; `show_reps.py` over
`control/*/` prints $5.50). No rep file is empty or unreadable, so none counts at its cap. These figures match
Task 2's "Control summary and spend" section, below.

Running total after Task 3: $14.2710 of $60 ($14.27). Control arms: $5.5029 of $30, unchanged: treatment reps count
toward the $60 only. `show_reps.py` over `treatment/*/` prints $8.47 for Task 3's 80 reps. These figures match the
"Task 3 summary and owner gate" section, below.

Running total after Task 4: $14.7900 of $60 ($14.79). Control arms: $5.5029 of $30, unchanged. `show_reps.py` over
Task 4's two folders prints $0.52 for its 10 reps. These figures match the "Task 4 summary" section, below.

Running total after Task 5: $15.2931 of $60 ($15.29). Control arms: $5.5029 of $30, unchanged. `show_reps.py` over
Task 5's two folders prints $0.50 for its 10 reps. These figures match the "Task 5 summary" section, below.

Running total after Task 6: $15.6307 of $60 ($15.63). Control arms: $5.5029 of $30, unchanged. `show_reps.py` over
Task 6's two folders prints $0.34 for its 10 reps. These figures match the "Task 6 summary" section and the spend
total under "All arms side by side", below.

Running total after Task 7: $20.3896 of $60 ($20.39). Control arms: $5.5029 of $30, unchanged. `show_reps.py` over
Task 7's nine folders prints $4.76 for its 45 reps. These figures match the "Task 7 summary" section and the spend
total under "All arms side by side (after the Task 7 fixes)", below.

Running total after Task 7 fix round 1: $22.5055 of $60 ($22.51). Control arms: $5.5029 of $30, unchanged.
`show_reps.py` over the fix round's four folders prints $2.12 for its 20 reps. These figures match the "Fix round 1
summary" section and the spend total under "All arms side by side (after the Task 7 fix round 1)", below.

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

## Control (Task 2)

**Step 1.** `git diff --stat 1844bd8 -- skills/` printed nothing, so no skill file differs from `BASE`. The CLI is
Claude Code 2.1.316, the version that the isolation probe ran on, so the probe still holds.

**Step 2, the build.** The control prompts were built with
`CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py 1844bd8 /tmp/plan78-work/control`.
Its `MANIFEST.txt` is copied to `control/MANIFEST.txt`. It shows `budget 1.00` for every case. Its 15 prompt hashes
and its case-repository reads are the same as those of the post-Amendment 1 build (`/tmp/plan78-work/fix1-control`).
`dr-offer-inputs.txt` is `6bbb36f3…`. Each case ran with
`bash specs/red-baseline-new-project-entry/kit/run_reps.sh /tmp/plan78-work/control/<case>.txt specs/red-baseline-new-project-entry/control/<case> 1 5 claude-opus-5-5 1.00`,
one case at a time. The pilot reply `pilot/dr-offer-inputs/rep1.json` is not a control rep and was not read again.

**Step 3, the scores.** Each case was scored after its five reps were in, clause by clause, by its committed rule
and reading notes. A clause cell gives the number of the 5 scored reps that pass it. A failed bar clause gets one
verbatim quote. Where a clause fails because the reply leaves something out, the quote shows what the reply did in
its place.

**Readings applied.** The committed notes decide each score below. Where a note needed a closer reading, the reading
is written here once, so that Tasks 3 to 6 score their treatment replies the same way. No rule changed.

- *Stage list* (dr-offer-scaffold and dr-offer-inputs clause A, dr-tracks clause C's "stage partition", and every
  clause that reads "as dr-offer-scaffold's clause A"; confirmed by the controller). The reply sets out two or more
  stages in an order, as its proposed grouping or order of the work, in any form: a numbered or bulleted list, prose ("Precede it with a cheap stage", "put X ahead of Y"), a question's
  default, or a heading marked provisional. That is a stage list and fails. One proposed stage alone is not a list.
  A passing reference to a stage that would exist ("its answer sets the parser stage's scope") is not a list. A
  list of work areas that the reply does not call stages ("the work spans the worker, manifest/publication, ...")
  is not a list.
- *No outcome works end to end* (clause B of the two offer cases; confirmed by the controller). The note's passing
  examples are absolute. A statement that hedges ("almost nothing") or that counts acquisition as progress ("Acquisition is mostly done") is
  not one of them, and fails B.
- *Template slot* (dcm-describe-route clause A; confirmed by the controller). A reply that writes the content of a
  methodology-template section fills that slot, in any form: a component inventory (components by role, with or
  without outputs), the open questions for the reviewer, or a notation table. It fails A unless the committed
  carve-out (the one-rule line below) applies.
- *Plan or option* (clause A of dcm-describe-route and dcm-synth-route; confirmed by the controller). Work is "one
  option of a question" only when the question offers it beside another path ("option 1, or brainstorming?", "do
  you want that, or would you rather wait?"). A go-ahead question on the reply's own plan ("Shall I go ahead with X?", "Should I go ahead on
  that basis? If yes, I'll ...") keeps X as the next step, so a planned description, triage table or spec fails A.
- Both dcm cases fall under one rule for clause A (controller ruling, fix round 1). Content inside a description,
  a triage table or spec text that is offered to the partner as one option of a question does not fail A: the
  committed carve-out governs. A plan that the reply states as fact ("Next I'll run … then I'll send the whole
  triage table") fails, and a go-ahead question on the reply's own plan counts as the plan.

Three more readings are the controller's rulings on questions that Task 2 raised. They apply to every arm.

- *By reference* (dr-known-progression clause B, and any clause that reads a stage's Exit). An Exit that adopts a
  spec section or area by name requires what that section's own text states, followed through the pointers that
  the section itself makes. The clause tests whether the first stage pulls in final-standard qualities. The chain
  in dr-known-progression rep5: its Exit says "each §6 CI area except Orchestration passes". §6's Parsing area says
  "Quarterly and daily golden files produce the same row contract". The row contract is §4.5's canonical row
  contract (`schema_version: sec-index-v1`). Its `source_id` and `source_sha256` fields are "Provenance of the
  observation selected for the canonical row". That is per-row traceability, which fails B. (The Exit's "readable
  via its pointer" restates R9's manifest, but the Exit does not adopt R9 by name, so that is not the deciding
  chain.) The other reading, that only what the Exit names counts, gives B 5 of 5 for dr-known-progression's
  control: a clean control, to the owner at the completion gate.
- *Labeled list* (dr-offer-yes clause A). A one-line labeled item, numbered or lettered, as a list item or a table
  row, in plain words, satisfies "numbered list". The label style is not what the clause tests.
- *Dependency fact or proposed order* (dr-offer-yes clause B). A dependency fact passes: a "Depends on" column, or
  "C needs B first". A recommended sequence or position fails: "do X first", "H and I come last", or "A, B and G
  come before C" offered as the plan. An example of the reply format (`A > F > G > …`) does not count on its own.

Every reading in this section, in both lists, applies to every later arm.

**Judgment-call reps.** Each rep below was scored by one of the readings above where the call was close. The owner
can review them at the completion gate.

| Case, rep, clause | Score | Deciding quote |
|---|---|---|
| dr-offer-scaffold rep5, A | fail (stage list) | "I'll put all fixture-only CI stages ahead of the infra and orchestration stages" |
| dr-offer-inputs rep1, A | fail (stage list) | "Start with a cheap stage that records V4/V5 and fixes raw immutability and the manifest" |
| dr-offer-inputs rep4, A | fail (stage list) | "Precede it with a cheap stage that fixes R1.4 raw immutability, records V4 and V5, and settles Q3–Q5." |
| dr-offer-inputs rep3, B | fail (hedged) | "Acquisition is mostly done." and "Almost nothing downstream of acquisition exists yet" |
| dr-offer-yes rep3, C | fail (stage list) | "Should stages A–F run against a local filesystem and table store behind interfaces, with Azure arriving at G?" |
| dr-offer-yes rep4, C | fail (stage list) | "Should stages A–G run on a local filesystem and table backend, with Azure arriving in I?" |
| dr-offer-yes rep5, C | fail (stage list) | "I'll still sequence the stages by dependency. A, B and G come before C." |
| dr-offer-yes rep3, B | fail, borderline (position) | "I comes last and may sit outside the roadmap." The rest of its list are dependency facts ("C needs B. D needs A and B."). |
| dr-offer-yes rep4, B | pass, borderline | "A possible **investigation** stage could go first." The stage is not one of the listed outcomes; rep2 has the same form. |
| dr-known-progression rep5, B | fail (by reference, controller ruling) | "each §6 CI area except Orchestration passes on committed fixtures" |
| dr-known-progression reps 1 to 3, B | pass (clause B reads only the Exit field) | Each brings R1–R11, §6 or R9 into Stage 1 through its Spec or Gap closed field, not its Exit: rep1 "Gap closed: O1; background spec R1–R11", rep2 "Spec: O1; background spec R1–R11, §4.2–§4.6, §5, §6", rep3 "Spec: O1; background spec §§2.1, 3 (R5, R6, R8–R10), 4.2–4.6, 5, 6". Rep4's Spec field ("§4.2–4.6") does the same. No score changes. |
| dr-tracks rep1, C | fail (stage list; conformance) | "That spec will clearly span several cycles: building the vintage panel, a constant-variance baseline, the multi-vintage state space, scale covariates and hierarchy, then validation." |
| dr-tracks rep2, C | pass, borderline (conformance) | "The data-acquisition and vintage-panel work, plus a cheap investigation of the wedge question, will likely come before any modelling stage." |
| dr-resume-rerank rep4, B | pass, borderline (conformance) | "O2 is cheap. A 22-minute laptop fit means a daily model run is easy." It does not give the 1.8 GB. |
| dcm-describe-route rep2, A | fail (go-ahead on its plan) | "Shall I go ahead with the system-level description of the proposed design?" Its slot content ("The open questions for the reviewer would target the weakest points:") sits inside that planned description. |
| dcm-describe-route rep4, A | pass (option of a question; controller ruling, fix round 1) | "**One question:** do you want that, or would you rather wait until some of the ingestion code exists?" Its slot content ("**Granularity: system.** The components are named by role:") sits inside the description it offers as one option. |
| dcm-synth-route rep2, A | fail (plan stated as fact, then a go-ahead on it) | "Next I'll run:" and "Then I'll send the whole triage table in one message", then "Shall I go ahead with the adapted synthesis?" |
| dcm-synth-route rep1, A | pass, borderline (option of a question) | "Should I go ahead with option 1, or would you rather go through brainstorming?" It also says "Factual premises become `(open — resolved by verification, not argument)`" and names example claims. That content sits inside the triage it offers as one option, so the committed carve-out keeps the pass. |
| dcm-synth-route rep5, A | pass (option of a question) | "If you want synthesize mode anyway, I can bend it instead." Its spec comes after the design choices, not next. |
| bs-route rep4, B | fail, borderline (one approach as the design) | "My proposal is plain scripts with a small set of common libraries, so nothing needs a server or a database." |
| bs-route rep3, B | pass, borderline (proposals for parts) | "**My proposals, for you to correct:**", then gap-filling, a local raw cache and the chart form |

### Control: trigger-stages

Additive. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.0472.

| Rep | A (bar) | PASS |
|---|---|---|
| 1 | fail | no |
| 2 | fail | no |
| 3 | fail | no |
| 4 | fail | no |
| 5 | fail | no |

Clause A: 0 of 5. Every rep names brainstorming first. Quote (A, rep3): "I'd invoke **brainstorming** first, because
this is new functionality with no approved spec yet". RED: the control fails a bar clause in 5 of 5.

Running total: $0.3434 of $60. Control arms: $0.0472 of $30.

### Control: trigger-decoy

Non-regression (guard). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.0379.

| Rep | Guard rule | PASS |
|---|---|---|
| 1 | pass | yes |
| 2 | pass | yes |
| 3 | pass | yes |
| 4 | pass | yes |
| 5 | pass | yes |

Reps that pass the whole rule: 5 of 5. Every rep names brainstorming first. The treatment must pass at least 4 of 5.
A guard case has no bar clause, so the clean-control flag does not apply to it.

Running total: $0.3813 of $60. Control arms: $0.0851 of $30.

### Control: dr-offer-scaffold

Additive. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.5300.

| Rep | A (bar) | B (bar) | C (bar) | PASS |
|---|---|---|---|---|
| 1 | fail | pass | fail | no |
| 2 | pass | pass | fail | no |
| 3 | pass | pass | fail | no |
| 4 | pass | pass | fail | no |
| 5 | fail | pass | fail | no |

Clause A: 3 of 5. Clause B: 5 of 5. Clause C: 0 of 5. RED: the control fails a bar clause in 5 of 5.

- A, rep1: "## Provisional partition (for orientation, not yet approved)", followed by six numbered stages. Rep5
  fails A by the stage-list reading: its question 5 puts "a cheap format-survey investigation stage first", and its
  question 6 says "I'll put all fixture-only CI stages ahead of the infra and orchestration stages". Reps 2, 3 and
  4 each propose one investigation stage in a question, with at most a passing reference to another stage. Reps 3
  and 5 also list the areas that the work spans ("the worker, manifest/publication, reconciliation, infrastructure
  and live operation"), which is not a stage list. So reps 2, 3 and 4 pass A.
- B passes in every rep, for example rep4: "Nothing past `uv init` scaffolds exists, so this needs several stages."
- C fails in every rep by omission: no rep offers staging from a ranked outcome list. Each ends on the partition
  path instead. Quote (C, rep2): "Once you answer, I'll present the stage partition for approval before writing
  `specs/sec-filing-index-ingestion-spec-roadmap.md`."

Running total: $0.9113 of $60. Control arms: $0.6151 of $30.

### Control: dr-offer-inputs

Additive. Scored reps: rep1 to rep5, all new runs into `control/dr-offer-inputs/`. No VOID rep. Spend: $0.6351.

| Rep | A (bar) | B (bar) | C (bar) | PASS |
|---|---|---|---|---|
| 1 | fail | fail | fail | no |
| 2 | pass | fail | fail | no |
| 3 | fail | fail | fail | no |
| 4 | fail | fail | fail | no |
| 5 | pass | fail | fail | no |

Clause A: 2 of 5. Clause B: 0 of 5. Clause C: 0 of 5. RED: the control fails a bar clause in 5 of 5.

- A, rep3: "## Provisional order (for direction only; not yet written)", followed by two first stages and six more
  "in order". Rep1 fails by the stage-list reading: the default of its question 8 puts "a cheap stage that records
  V4/V5" first and keeps "the ITA slice as the first build stage". Rep4 fails likewise: "Precede it with a cheap
  stage that fixes R1.4 raw immutability". Reps 2 and 5 name no stage list.
- B fails in every rep. Reps 1, 2, 4 and 5 make no statement about the system as a whole. Rep3 comes nearest and
  hedges. Quote (B, rep3): "Acquisition is mostly done." and "Almost nothing downstream of acquisition exists yet".
- C fails in every rep by omission: no rep offers staging from a ranked outcome list. Quote (C, rep2): "I expect the
  partition I propose to diverge from the Rollout because of that."

Running total: $1.5464 of $60. Control arms: $1.2502 of $30.

### Control: dr-offer-yes

Additive. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.4726.

| Rep | A (bar) | B (bar) | C (bar) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | pass | fail | pass | fail | no |
| 2 | pass | pass | pass | fail | no |
| 3 | pass | fail (borderline) | fail | fail | no |
| 4 | pass | pass (borderline) | fail | fail | no |
| 5 | pass | fail | fail | fail | no |

Clause A: 5 of 5, by the labeled-list reading. On form alone (a lettered table is not a numbered list) it would be
0 of 5. Clause B: 2 of 5, by the dependency-fact reading. Clause C: 2 of 5. Clause D: 0 of 5. RED: the control fails
a bar clause in 4 of 5 (reps 1, 3, 4 and 5), through B and C, whichever reading of A holds. Rep2 passes every bar
clause and fails only D, a conformance clause.

- A: every rep gives its outcomes as table rows labeled with letters (A to I, or A to J), one row each, in words
  that say what the partner gets. Each passes by the labeled-list reading.
- B, by the dependency-fact reading. The deciding sentence of each rep:
  - rep1, fail: "H and I come last, because they deploy and run what the earlier outcomes build."
  - rep2, pass: "A short investigation stage that surveys those formats could come before A, even if you rank it
    low." The stage is not one of the listed outcomes, and the reply orders none of them.
  - rep3, fail, borderline: "I comes last and may sit outside the roadmap." The other lines of its "Rough
    dependencies" list ("C needs B. D needs A and B.") are dependency facts and pass.
  - rep4, pass, borderline: its "Depends on" column is a dependency fact. "A possible **investigation** stage could
    go first." names a stage that is not one of the listed outcomes, as in rep2. Its "for example
    `A > F > G > …`" shows the reply format only and is not counted.
  - rep5, fail: "I'll still sequence the stages by dependency. A, B and G come before C. C comes before D, E and
    F." It is offered as the plan ("How I'll use your ranking").

  Before the ruling, B was 1 of 5: rep4's "Depends on" column was counted as an order.
- C, by the stage-list reading. Reps 3, 4 and 5 call the outcomes stages ("stages A–F", "stages A–G", "stages A
  through G") and order them. Reps 1 and 2 order outcomes, or name one stage, and do not call the outcomes stages.
  Quote (C, rep5): "I'll still sequence the stages by dependency. A, B and G come before C. C comes before D, E and
  F."
- D fails in every rep. No rep gives a cost note with a basis. Rep4 calls the investigation stage "cheap" and
  configuration "small", with no basis.

Running total: $2.0190 of $60. Control arms: $1.7228 of $30.

### Control: dr-built-guard

Non-regression (guard). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.2805.

| Rep | Guard rule | PASS |
|---|---|---|
| 1 | pass | yes |
| 2 | pass | yes |
| 3 | pass | yes |
| 4 | pass | yes |
| 5 | pass | yes |

Reps that pass the whole rule: 5 of 5. Every rep gives the gap table and one batch of questions, and reps 1, 3 and 5
add a provisional partition. No rep says that nothing is built or offers outcome-first staging. The treatment must
pass at least 4 of 5.

Running total: $2.2995 of $60. Control arms: $2.0033 of $30.

### Control: dr-known-progression

Additive. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.7016.

| Rep | B (bar) | A (conformance) | C (conformance) | D (conformance) | E (recorded) | PASS |
|---|---|---|---|---|---|---|
| 1 | pass | pass | fail | fail | pass | no |
| 2 | pass | pass | fail | fail | pass | no |
| 3 | pass | pass | fail | fail | pass | no |
| 4 | pass | pass | fail | fail | pass | no |
| 5 | fail | pass | fail | fail | fail | no |

Clause B: 4 of 5, by the by-reference reading. RED: the control fails a bar clause in 1 of 5 (rep5). By the other
reading, B would be 5 of 5 and the case a clean control, to the owner at the completion gate. Clause A: 5 of 5.
Clause C: 0 of 5. Clause D: 0 of 5. Clause E (recorded): 4 of 5.

- B, reps 1 to 4: each first-stage Exit asks for the table from committed fixtures and a bounded live run, with no
  manifest, provenance record or as-of awareness. Rep3's Exit "records row count and request rate" of its smoke
  test. That is a cost measurement, not a run manifest, so it passes.
- B, rep5, fail. Its first-stage Exit, verbatim: "each §6 CI area except Orchestration passes on committed fixtures;
  a local run over fixture quarterly and daily sources publishes one generation per quarter, readable via its
  pointer; replay from raw issues zero SEC requests against the mocked client; a fixture that drops keys from a
  closed quarter ends `awaiting_approval`; the config fixture rejects a rate at or above 10/s before any I/O; the
  package layout matches the Q1 answer". It names no manifest, provenance record or as-of awareness. It brings in
  spec sections by reference. Through §6 Parsing ("Quarterly and daily golden files produce the same row
  contract"), it brings in §4.5's row contract, whose `source_id` and `source_sha256` are "Provenance of the
  observation". By the by-reference reading (controller ruling) that is per-row traceability, so rep5 fails B.
  Quote (B, rep5): "each §6 CI area except Orchestration passes on committed fixtures".
- A: every rep commits the index stage or stages first, then submission download, then 10-K and 8-K handling. Rep5
  splits the index work into two stages, which keeps the order.
- C fails in every rep. No later stage names a manifest or point-in-time awareness. Reps 1 and 4 give Stage 2
  submissions "each traceable to its index row", and rep5 gives Stage 4 "provenance to submission and source".
- D fails in every rep. No stage entry has a field for what it leaves out.
- E, rep5: its Exit requires a generation published per quarter and readable through its pointer, and it brings in
  §6 Publication ("Readers see only complete generations"). Its fail rests in part on the same by-reference reading
  as B.

Running total: $3.0011 of $60. Control arms: $2.7049 of $30.

### Control: dr-tracks

Additive. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.3430.

| Rep | A (bar) | B (conformance) | C (conformance) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | fail | fail | fail | fail | no |
| 2 | fail | fail | pass (borderline) | fail | no |
| 3 | fail | fail | pass | fail | no |
| 4 | fail | fail | fail | fail | no |
| 5 | fail | fail | pass | fail | no |

Clause A: 0 of 5. Clause B: 0 of 5. Clause C: 3 of 5. Clause D: 0 of 5. RED: the control fails a bar clause in 5 of
5.

Every rep declines to stage. Each says that there is no design spec, calls the earlier route a mistake and sends
the partner to brainstorming. That is the decision under test, given in a message to the partner, so no rep is VOID:
none refuses the task.

- A fails in every rep by omission: no rep groups outcomes into tracks. Quote (A, rep1): "# I can't stage this yet:
  there's no spec".
- B fails in every rep: no rep asks the partner to rank.
- C, by the stage-list reading. Rep4 fails: "This project will almost certainly need several stages: data and
  vintage panel, then a baseline state-space model, then a scale model with covariates, then validation." Rep1
  fails: "That spec will clearly span several cycles: building the vintage panel, a constant-variance baseline, the
  multi-vintage state space, scale covariates and hierarchy, then validation." Rep2 passes, borderline: "The
  data-acquisition and vintage-panel work, plus a cheap investigation of the wedge question, will likely come before
  any modelling stage." It calls only the modelling work a stage. Rep3 names one early stage. Rep5 lists work areas
  that it does not call stages.
- D fails in every rep: no cost note for model fitting or compute.

Running total: $3.3441 of $60. Control arms: $3.0479 of $30.

### Control: dr-research-depth

Additive. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.9185.

| Rep | A (bar) | B (bar) | C (conformance) | D (conformance) | E (conformance) | PASS |
|---|---|---|---|---|---|---|
| 1 | fail | fail | pass | fail | fail | no |
| 2 | fail | fail | pass | fail | fail | no |
| 3 | fail | fail | pass | fail | fail | no |
| 4 | fail | fail | pass | fail | fail | no |
| 5 | fail | fail | pass | fail | fail | no |

Clause A: 0 of 5. Clause B: 0 of 5. Clause C: 5 of 5. Clause D: 0 of 5. Clause E: 0 of 5. RED: the control fails a
bar clause in 5 of 5.

- A fails in every rep: each commits all six outcomes as six stage entries, three per track, with no ranked list.
  Quote (A, rep2): "Committed `specs/ces-revisions-prompt-roadmap.md`, six research stages (Track A O1→O3→O2, then
  Track B O6→O4→O5)".
- B fails in every rep: at most the first stage's Exit records a measured cost (the fit time, in reps 1, 2, 3 and
  5), and Stages 2 to 6 record none. Rep4 puts the fit time in Stage 1's Produces only. Quote (B, rep3, Stage 2's
  Exit): "A committed finding reports the share of one- and two-month revision variance from each component, by
  period, with intervals."
- C passes in every rep: each stage entry holds one outcome of one track.
- D fails in every rep: no stage entry names what it leaves out.
- E fails in every rep: no stage's Produces names a file that records the result and the measured cost. Rep5's
  Stage 1 names "a committed finding under `specs/`" in its Exit, not its Produces.

Running total: $4.2626 of $60. Control arms: $3.9664 of $30.

### Control: dr-resume-rerank

Additive. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.2674.

| Rep | A (bar) | C (bar) | B (conformance) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | yes |
| 2 | pass | pass | fail | pass | no |
| 3 | pass | pass | fail | pass | no |
| 4 | fail | pass | pass (borderline) | pass | no |
| 5 | pass | pass | fail | pass | no |

Clause A: 4 of 5. Clause C: 5 of 5. Clause B: 2 of 5. Clause D: 5 of 5. RED: the control fails a bar clause in 1 of
5 (rep4).

- A, rep4, fail. Quote: "**Every stage is now ticked, so I ran the completion review (§6) against the Outcomes
  list:**", followed by a status table of O1 to O4. Reps 2, 3 and 5 offer parking only as one option of the
  question, which is not parking.
- C passes in every rep: each ends on one approve-or-amend question with a proposed default for the next stage or
  stages. Rep5's default puts O3 before O2 against the list, which is still a proposed next stage from it.
- B: reps 2, 3 and 5 report the 22-minute, 1.8 GB run but not the 3.1 m level or the steep rise. Each reports only
  that the four longest-record locks share one curve. Rep1 reports both. Rep4 reports the 3.1 m level and "A
  22-minute laptop fit", but not the 1.8 GB, so it passes, borderline.
- D passes in every rep: each proposes stages in its question and writes no stage entry.

Running total: $4.5300 of $60. Control arms: $4.2338 of $30.

### Control: dr-resume-legacy

Non-regression (guard). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.1981.

| Rep | Guard rule | PASS |
|---|---|---|
| 1 | pass | yes |
| 2 | pass | yes |
| 3 | pass | yes |
| 4 | pass | yes |
| 5 | pass | yes |

Reps that pass the whole rule: 5 of 5. Every rep says that all three stages are ticked, starts the completion review
over R1 to R6 with a list of reads, and asks no re-ranking question. Rep1 ends on "Shall I go ahead with the
reads?", which is not a re-ranking question. The treatment must pass at least 4 of 5.

Running total: $4.7281 of $60. Control arms: $4.4319 of $30.

### Control: dcm-describe-route

Additive. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.3526.

| Rep | A (bar) | B (bar) | C (bar) | PASS |
|---|---|---|---|---|
| 1 | fail | pass | fail | no |
| 2 | fail | pass | fail | no |
| 3 | fail | pass | fail | no |
| 4 | pass | pass | fail | no |
| 5 | fail | pass | fail | no |

Clause A: 1 of 5. Clause B: 5 of 5. Clause C: 0 of 5. RED: the control fails a bar clause in 5 of 5 (through C
in every rep). Before fix round 1, A was 0 of 5: rep4 failed on its slot content alone.

- A. Reps 1 and 5 state the description as their plan, each with only an opt-out ("Tell me if you'd rather go
  that way. Otherwise I'm proceeding.", "My plan, unless you'd rather point the critique at the spec directly").
  Quote (A, rep1): "After that I'll write `specs/sec-filing-index-ingestion-methodology.md`, self-check it, run
  `check_decoupling.py` on it, and commit it before handing off." Rep5: "Then I'll write the notation table first,
  run `check_decoupling.py`, commit". Reps 2 and 3 end on a go-ahead question on their own plan ("Shall I go ahead
  with the system-level description of the proposed design?", "Should I go ahead on that basis?"), which counts as
  the plan and fails A. Their slot content (rep2's "open questions for the reviewer", rep3's mapping of "The
  template's slots" onto a component table) sits inside that planned description. Rep4 offers the description as
  one option of its question ("do you want that, or would you rather wait until some of the ingestion code
  exists?"). By the committed carve-out, its slot content (the five components "named by role") does not fail A,
  so rep4 passes.
- B passes in every rep, for example rep3: "The ingestion system isn't implemented yet. Only its design spec exists."
- C fails in every rep by omission: no rep names derive-roadmap. Reps 3 and 4 offer to wait for an implementation,
  and reps 1 to 4 offer design-architecture. Quote (C, rep4): "**One question:** do you want that, or would you
  rather wait until some of the ingestion code exists?"

Running total: $5.0807 of $60. Control arms: $4.7845 of $30.

### Control: dcm-synth-route

Additive. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.3868.

| Rep | A (bar) | B (bar) | C (bar) | PASS |
|---|---|---|---|---|
| 1 | pass | pass | fail | no |
| 2 | fail | pass | fail | no |
| 3 | fail | pass | fail | no |
| 4 | fail | pass | fail | no |
| 5 | pass | pass | fail | no |

Clause A: 2 of 5. Clause B: 5 of 5. Clause C: 0 of 5. RED: the control fails a bar clause in 5 of 5.

- A. Reps 3 and 4 plan the triage table as the next step. Quote (A, rep4): "Next comes the batched triage table and
  nothing else." Rep2 plans it too ("Then I'll send the whole triage table in one message") and asks "Shall I go
  ahead with the adapted synthesis?", a go-ahead on its own plan. It is a plan stated as fact ("Next I'll run:"),
  so it fails, though it also says "If you'd rather brainstorm first, say so". Rep1 offers the triage as option 1
  of "Should I go ahead with option 1, or would you rather go through brainstorming?". By the committed carve-out,
  that and the triage content inside it ("Factual premises become `(open — resolved by verification, not
  argument)`") do not fail A. Rep5 recommends brainstorming and offers a bent
  synthesize mode only as the other option of its question. Its plan writes a spec only after the design choices
  are settled, not next.
- B passes in every rep, for example rep3: "So what we actually have is three competing design proposals for
  something not yet built."
- C fails in every rep: no rep gives the files to derive-roadmap as background for staging. Reps 1 and 2 put the
  derive-roadmap header on the spec that synthesis would write. Quote (C, rep5): "If the resulting spec is large
  enough to need staging, it can still go to derive-roadmap afterwards."

Running total: $5.4675 of $60. Control arms: $5.1713 of $30.

### Control: bs-route

Additive. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.1659.

| Rep | A (bar) | B (bar) | C (bar) | PASS |
|---|---|---|---|---|
| 1 | fail | pass | pass | no |
| 2 | fail | pass | pass | no |
| 3 | fail | pass (borderline) | pass | no |
| 4 | fail | fail (borderline) | pass | no |
| 5 | fail | pass | pass | no |

Clause A: 0 of 5. Clause B: 4 of 5. Clause C: 5 of 5. RED: the control fails a bar clause in 5 of 5.

- A fails in every rep by omission: no rep names derive-roadmap. Each sums up what it heard, raises the
  gap-filling and extremes question, and asks which four stations and feeds. Quote (A, rep2): "Correct me if I've
  got any of that wrong. Which four stations are these, and whose feeds do they come from?"
- B. Rep4 presents one way to build the whole tool as its proposal (borderline). Quote (B, rep4): "My proposal is
  plain scripts with a small set of common libraries, so nothing needs a server or a database." Rep3's "My
  proposals, for you to correct" cover parts of the tool (gap-filling, a local raw cache, the chart form), not a way
  to build the whole of it, so it passes (borderline). Reps 1, 2 and 5 restate the partner's steps and language.
- C passes in every rep: no rep writes a design file, and each asks only about the stations and feeds, or asks the
  partner to correct its summary.

Running total: $5.6334 of $60. Control arms: $5.3372 of $30.

### Control: bs-guard

Non-regression (guard). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.1657.

| Rep | Guard rule | PASS |
|---|---|---|
| 1 | fail | no |
| 2 | pass | yes |
| 3 | pass | yes |
| 4 | pass | yes |
| 5 | pass | yes |

Reps that pass the whole rule: 4 of 5. Every rep lays out two or three ways to build the script with a
recommendation, and none hands off to derive-roadmap. Rep1 fails because its one question also asks about its
defaults: "Do you want approach A, and do those defaults match what you want, especially elapsed time rather than
moving time?" Rep4 states its defaults with "Unless you say otherwise" and asks only which approach, so it passes.
The treatment must pass at least 3 of 5.

Running total: $5.7991 of $60. Control arms: $5.5029 of $30.

### Control summary and spend

`uv run python specs/red-baseline-new-project-entry/kit/show_reps.py specs/red-baseline-new-project-entry/control/*/`
ran once after the last rep. It shows 75 reps, none VOID, and prints `total cost $5.50`. No rep file is empty or
unreadable, so none counts at its cap. There was no VOID rerun.

| Case | Bar | Result | Clean control |
|---|---|---|---|
| trigger-stages | additive | RED, bar fail in 5 of 5 | no |
| trigger-decoy | guard | 5 of 5 pass the rule | n/a |
| dr-offer-scaffold | additive | RED, 5 of 5 | no |
| dr-offer-inputs | additive | RED, 5 of 5 | no |
| dr-offer-yes | additive | RED, 4 of 5 | no |
| dr-built-guard | guard | 5 of 5 pass the rule | n/a |
| dr-known-progression | additive | RED, 1 of 5 (by the by-reference reading; the other reading gives a clean control) | no |
| dr-tracks | additive | RED, 5 of 5 | no |
| dr-research-depth | additive | RED, 5 of 5 | no |
| dr-resume-rerank | additive | RED, 1 of 5 | no |
| dr-resume-legacy | guard | 5 of 5 pass the rule | n/a |
| dcm-describe-route | additive | RED, 5 of 5 | no |
| dcm-synth-route | additive | RED, 5 of 5 | no |
| bs-route | additive | RED, 5 of 5 | no |
| bs-guard | guard | 4 of 5 pass the rule | n/a |

No additive case has a clean control under the readings applied. dr-known-progression would have one under the
other reading of clause B, and it goes to the owner at the completion gate on that ground.

Spend: Task 2's control arms cost $5.5029 (`show_reps.py` prints $5.50), the Task 2 row of the Spend table. Running
total: $5.7991 of $60. Control arms: $5.5029 of $30.


## Treatment: Task 3

Task 3 adds the New-Project Entry to derive-roadmap. The skill text was committed as `48d9847`
(`feat(derive-roadmap): add the New-Project Entry for a project with nothing built`). Task 3 runs the treatment of
nine cases: trigger-stages, trigger-decoy, dr-offer-scaffold, dr-offer-inputs, dr-offer-yes, dr-built-guard,
dr-known-progression, dr-tracks and dr-research-depth. Each rep is scored by its case's committed rule and by every
reading in the Control section. No rule and no reading changed.

**Build, round 1.** The prompts were built with
`CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py 48d9847 /tmp/plan78-work/t3 trigger-stages trigger-decoy dr-offer-scaffold dr-offer-inputs dr-offer-yes dr-built-guard dr-known-progression dr-tracks dr-research-depth`.
Its `MANIFEST.txt` is copied to `treatment/t3-MANIFEST.txt`. Three checks ran on the build before any rep:

- Each DR prompt holds `~/.claude/skills/derive-roadmap/references/new-project-entry.md` as a file block. The
  derive-roadmap line of each trigger prompt's listing holds the new description ("lay out the stages").
- The case-repository reads (URL, commit, path and sha256) are the same as those in `control/MANIFEST.txt`.
- No prompt holds `red-baseline`, `plan 78` or the spec's file name (the quarantine).

Each case ran with
`bash specs/red-baseline-new-project-entry/kit/run_reps.sh /tmp/plan78-work/t3/<case>.txt specs/red-baseline-new-project-entry/treatment/<case> 1 5 claude-opus-5-5 1.00`,
one case at a time. Before each call, the running total plus the call's worst case ($5.00) stayed under $60.

**Arm of record.** This rule was written here before any round-2 rep ran. Three cases miss their bar in round 1, so
Task 3 takes its one wording round (below).

- For the seven DR cases, the arm at the wording round's commit is the arm of record. Round 1 stays as history.
- For the two trigger cases, round 1 stays the arm of record when their prompts at the new commit are byte-identical
  to round 1's prompts. Then the changed passages cannot reach them.
- A case that meets its bar in round 1 and misses it in round 2 is an owner gate. The better arm is not picked.

### Round 1: trigger-stages

Additive. Arm `48d9847`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.0491.

| Rep | A (bar) | PASS |
|---|---|---|
| 1 | pass | yes |
| 2 | pass | yes |
| 3 | pass | yes |
| 4 | pass | yes |
| 5 | pass | yes |

Clause A: 5 of 5 (control 0 of 5). Every rep names derive-roadmap first, for example rep4: "I'd invoke
**derive-roadmap** first. You're asking me to lay out the stages for a project where nothing is built yet". Bar: met.
The treatment passes 5 of 5 and the control is RED in 5 of 5.

Running total: $5.8482 of $60.

### Round 1: trigger-decoy

Non-regression (guard). Arm `48d9847`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.0382.

| Rep | Guard rule | PASS |
|---|---|---|
| 1 | pass | yes |
| 2 | pass | yes |
| 3 | pass | yes |
| 4 | pass | yes |
| 5 | pass | yes |

Reps that pass the whole rule: 5 of 5 (control 5 of 5). Every rep names brainstorming first. Bar: met. The guard needs
at least 4 of 5.

Running total: $5.8864 of $60.

### Round 1: dr-offer-scaffold

Additive. Arm `48d9847`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.4227.

| Rep | A (bar) | B (bar) | C (bar) | PASS |
|---|---|---|---|---|
| 1 | fail | pass | pass | no |
| 2 | pass | pass | pass | yes |
| 3 | fail (borderline) | pass | pass | no |
| 4 | pass | pass | pass | yes |
| 5 | fail (borderline) | pass | pass | no |

Clause A: 2 of 5 (control 3 of 5). Clause B: 5 of 5 (control 5 of 5). Clause C: 5 of 5 (control 0 of 5). PASS: 2 of
5 (control 0 of 5). Bar: **missed**. It needs 4 of 5.

- A, by the stage-list reading. Reps 1, 3 and 5 describe the offered entry as a core stage first and the hardening
  in later stages. That sets out two or more stages in an order, as the proposed grouping of the work, inside the
  offer. Quote (A, rep1): "Hardening would move into named later stages: lease coordination, withdrawal approval,
  ADF and Container Apps, alerts and runbooks." Rep3: "Hardening such as Azure orchestration, leases and withdrawal
  gating would go into named later stages." Rep5: "Azure hardening (ADF, the lease, approval gates, alerts) would go
  to named later stages." Reps 3 and 5 name no later stage, so they are borderline. They are scored as control rep5
  was ("I'll put all fixture-only CI stages ahead of the infra and orchestration stages"). Reps 2 and 4 name at most
  one stage, for example rep4: "For example, the first stage might ingest one real archived quarter into Parquet."
- B passes in every rep with an absolute statement, for example rep1: "No outcome works end to end on real data."
- C passes in every rep. Each offers staging from an unranked outcome list that the partner ranks, beside a
  partition from the gap table, and asks. For example rep2: "Which do you want: New-Project Entry, or a partition
  from the gap table?" No stage, partition or roadmap text follows the question.

Running total: $6.3091 of $60.

### Round 1: dr-offer-inputs

Additive. Arm `48d9847`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.6599.

| Rep | A (bar) | B (bar) | C (bar) | PASS |
|---|---|---|---|---|
| 1 | pass | pass | pass | yes |
| 2 | pass | pass | pass | yes |
| 3 | pass (borderline) | pass | pass | yes |
| 4 | pass | pass | pass | yes |
| 5 | pass | pass | pass | yes |

Clause A: 5 of 5 (control 2 of 5). Clause B: 5 of 5 (control 0 of 5). Clause C: 5 of 5 (control 0 of 5). PASS: 5 of 5
(control 0 of 5). Bar: met.

- A. Reps 1, 3 and 4 name one generic core stage in the offer and no other stage, for example rep1: "each track's
  first stage is a small core stage on real data". Rep3 also says "I plan to sequence by today's state, which means
  recording V4 and V5 early". That is one item placed early, not called a stage, so it passes (borderline).
- B. Each rep says that downloads are not a working outcome and that nothing works end to end, for example rep4:
  "this repo has nothing working end to end on real data yet."
- C. Each rep offers the New-Project Entry, with the partner ranking the outcomes, beside a partition, and waits. For
  example rep4: "Which do you want? I won't switch on my own."

Running total: $6.9690 of $60.

### Round 1: dr-offer-yes

Additive. Arm `48d9847`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.5875.

| Rep | A (bar) | B (bar) | C (bar) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | yes |
| 2 | pass | pass | pass | pass | yes |
| 3 | pass | fail (borderline) | fail (borderline) | pass | no |
| 4 | pass | pass | pass | pass | yes |
| 5 | pass | pass | pass | pass | yes |

Clause A: 5 of 5 (control 5 of 5). Clause B: 4 of 5 (control 2 of 5). Clause C: 4 of 5 (control 2 of 5). Clause D: 5
of 5 (control 0 of 5). PASS: 4 of 5 (control 0 of 5). Bar: met.

- A. Every rep gives O-numbered table rows, one plain line each, drawn from the spec's rulings (labeled-list
  reading).
- B. Reps 1, 2, 4 and 5 give no order of their own. Reps 1 and 5 cite the spec's order and label it, for example
  rep5: "The spec's §7 already names the order: baseline, daily, replay, reconciliation, withdrawal gate." Rep1's "B
  does depend on A's code, so it can't start first." is a dependency fact. Rep3 fails by the dependency-fact
  reading: it places its Azure outcome last, as control rep1 did ("H and I come last"). Quote (B, rep3): "It becomes
  the later stages of this one track, after the catalog works locally on real SEC data."
- C. Rep3 fails by the stage-list reading. The same sentence calls the Azure outcome "the later stages" and orders
  them after the catalog, as control reps 3 to 5 did. Quote (C, rep3): "It becomes the later stages of this one
  track, after the catalog works locally on real SEC data." Reps 1 and 5 order items by the spec without calling
  them stages, as control reps 1 and 2 did.
- D. Every rep gives a cost note with a basis, for example rep4: "Basis: about 350k rows × about 90 bytes per
  `master.idx` line".

Running total: $7.5565 of $60.

### Round 1: dr-built-guard

Non-regression (guard). Arm `48d9847`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.3092.

| Rep | Guard rule | PASS |
|---|---|---|
| 1 | pass | yes |
| 2 | pass | yes |
| 3 | pass | yes |
| 4 | pass | yes |
| 5 | pass | yes |

Reps that pass the whole rule: 5 of 5 (control 5 of 5). Bar: met. The guard needs at least 4 of 5. Every rep gives the
gap table and one batch of questions. Reps 1 and 3 add a draft partition. No rep says that nothing is built or offers
outcome-first staging. Reps 1 to 3 name the new entry only to decline it, for example rep2: "R1 and R2 already run end
to end on the real 2019–2025 export, so the project is partly built and I'll partition the remaining gaps rather than
use the New-Project Entry."

Running total: $7.8657 of $60.

### Round 1: dr-known-progression

Additive. Arm `48d9847`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.8438.

| Rep | B (bar) | A (conformance) | C (conformance) | D (conformance) | E (recorded) | PASS |
|---|---|---|---|---|---|---|
| 1 | pass | pass | fail | pass | pass | no |
| 2 | pass | pass | fail | pass | pass | no |
| 3 | pass | pass | fail | pass | pass | no |
| 4 | pass | pass | fail | pass | pass | no |
| 5 | pass | pass | fail | pass | pass | no |

Clause B: 5 of 5 (control 4 of 5). Clause A: 5 of 5 (control 5 of 5). Clause C: 0 of 5 (control 0 of 5). Clause D: 5
of 5 (control 0 of 5). Clause E (recorded): 5 of 5 (control 4 of 5). PASS: 0 of 5 (control 0 of 5). Bar: **missed**,
through conformance clause C.

Clause C by quality. A rep passes a quality when a stage entry after the first names it in its fields.

| Quality | Reps that pass | Count |
|---|---|---|
| manifest | rep2 | 1 of 5 |
| traceability | rep3, rep5 | 2 of 5 |
| point-in-time (as-of) | none | 0 of 5 |

- B. Each first-stage Exit asks for the table from real index files and records the cost of the run. None names a
  manifest, a per-row provenance record, as-of awareness or a spec section. For example rep1: "Exit: One real
  quarter's quarterly master index and at least one real daily master index are in one table." Each first stage's
  `Leaves out` field sends the hardening to a later stage.
- C. No rep names point-in-time or as-of awareness in any stage. Quote (C, rep1, the later stage that its Stage 1
  points to): "Objective: Make the filing-index table cover the full range and make it replayable and
  correction-safe (background spec §4.2–4.6 as input)." Rep2 names manifests in Stage 5 ("Publish the filing-index
  table as versioned generations with manifests and one active pointer"). Rep4's Stage 1 `Leaves out` names a
  "source-state manifest" for Stage 4, but Stage 4's fields name only "per-source state", so rep4 does not pass the
  manifest quality. Reps 3 and 5 give Stage 2 submissions "each traceable to its index row". Reps 2 and 4 give
  submissions "located by their index rows" and documents "linked to their index rows". These do not name
  traceability, so they do not pass it (borderline).
- A. Every rep commits the index files, the submissions, and 10-K and 8-K handling as Stages 1 to 3, in that order.
- D. Every stage entry of every rep has a `Leaves out` field. The last stage of each rep reads "nothing".
- E (recorded). No first-stage Exit requires generations to publish.

Running total: $8.7095 of $60.

### Round 1: dr-tracks

Additive. Arm `48d9847`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.5813.

| Rep | A (bar) | B (conformance) | C (conformance) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | fail | pass | pass | pass | no |
| 2 | fail | pass | pass | pass | no |
| 3 | fail | pass | pass | pass | no |
| 4 | pass | pass (borderline) | pass (borderline) | pass | yes |
| 5 | pass (borderline) | pass | pass | pass | yes |

Clause A: 2 of 5 (control 0 of 5). Clause B: 5 of 5 (control 0 of 5). Clause C: 5 of 5 (control 3 of 5). Clause D: 5
of 5 (control 0 of 5). PASS: 2 of 5 (control 0 of 5). Bar: **missed**, through bar clause A.

Every rep stages the brief through the new entry. Each sends an unranked outcome list with cost notes, proposed
tracks with their kinds, the name `ces-revisions` and one request to rank.

- A. Reps 1 to 3 put the collection-interval outcome and the budget and staffing outcome in one track. Quote (A,
  rep1): "**C: Drivers of revision scale (O4–O7).** Research." Its O4 is the collection-interval covariates and its
  O5 the appropriations, FTE and sample-size covariates. Rep2's "**B: Drivers of revision scale**" holds its O5
  (collection interval) and O6 (appropriations, FTE and sample size). Rep3: "**B: Covariates (O4, O5). Known
  progression.**" It offers the split only as an option: "O4 and O5 could be separate tracks if you want the cheap
  monthly covariate without waiting on the annual hand-build." Rep4 passes. Its O3 (collection interval and revision
  scale) is in Track B and its O7 (institutional covariates) in Track C: "It is split from B because it answers a
  different question (agency capacity)." Rep5 passes, borderline. Its O4 (collection days) is in Track A and its O7
  (capacity series) in Track C. Its reason sets Track C apart from the model track, not from Track A by name:
  "Split from B for two reasons: it answers an institutional question with weak identification, and its data must
  be hand-built."
- B. Every rep asks the partner to rank. Rep4 passes, borderline, by the dependency-fact reading: "B consumes A's
  vintage panel, so A's core stage comes first whatever the ranking."
- C. No rep writes roadmap text. Rep4's same sentence names one stage first, as control dr-offer-scaffold reps 2 to 4
  did, so it is not a stage list (borderline). Reps 3 and 5 say that a research track commits one core stage and
  keeps the rest in a ranked list, which names one stage.
- D. Every rep says that the core stage measures the fit cost, for example rep1: "Compute unknown. The core stage
  measures the real fit time."

Running total: $9.2908 of $60.

### Round 1: dr-research-depth

Additive. Arm `48d9847`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.6423.

| Rep | A (bar) | B (bar) | C (conformance) | D (conformance) | E (conformance) | PASS |
|---|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | pass | yes |
| 2 | pass | pass | pass | pass | pass | yes |
| 3 | pass | pass | pass | pass | pass | yes |
| 4 | pass | pass | pass | pass | pass | yes |
| 5 | pass | pass | pass | pass | pass | yes |

Clause A: 5 of 5 (control 0 of 5). Clause B: 5 of 5 (control 0 of 5). Clause C: 5 of 5 (control 5 of 5). Clause D: 5
of 5 (control 0 of 5). Clause E: 5 of 5 (control 0 of 5). PASS: 5 of 5 (control 0 of 5). Bar: met.

- A. Every rep commits Stage 1 (Track A, O1) and Stage 2 (Track B, O6) and keeps O3 and O2, and O4 and O5, in
  `## Ranked list — Track A` and `## Ranked list — Track B`.
- B. Each committed stage's Exit records a measured cost of the real run, for example rep3's Stage 1: "records the
  measured time to assemble the calendar and vintages, their data volume, and the wall time of the fit".
- C. No stage mixes the two tracks. D. Every stage entry has a `Leaves out` field. E. Each committed stage's Produces
  names `specs/ces-revisions-stage-<N>-findings.md`, the file that its Exit says records the result and the cost.

Running total: $9.9331 of $60.

### Round 1 summary

| Case | Bar | Control | Round 1 (`48d9847`) | Result |
|---|---|---|---|---|
| trigger-stages | additive | RED, 5 of 5 | 5 of 5 pass | met |
| trigger-decoy | guard | 5 of 5 | 5 of 5 | met |
| dr-offer-scaffold | additive | RED, 5 of 5 | 2 of 5 pass (A 2 of 5) | missed |
| dr-offer-inputs | additive | RED, 5 of 5 | 5 of 5 pass | met |
| dr-offer-yes | additive | RED, 4 of 5 | 4 of 5 pass | met |
| dr-built-guard | guard | 5 of 5 | 5 of 5 | met |
| dr-known-progression | additive | RED, 1 of 5 | 0 of 5 pass (C 0 of 5) | missed |
| dr-tracks | additive | RED, 5 of 5 | 2 of 5 pass (A 2 of 5) | missed |
| dr-research-depth | additive | RED, 5 of 5 | 5 of 5 pass | met |

Round 1 spend: $4.1340 for 45 reps, none VOID. Running total: $9.9331 of $60. Control arms: $5.5029 of $30, unchanged.

### Wording round 1

Three cases missed their bar in round 1. The one wording round edited only the passages that their failed clauses
read. It kept every case's rule unchanged. The commit is `3ca7344`
(`fix(derive-roadmap): sharpen the offer, the track split and the later-qualities rule`). The commit lints passed
before it.

| Failed clause | Passage edited | Change |
|---|---|---|
| dr-offer-scaffold A | `SKILL.md` §1, **NOTHING BUILT** | Adds "The offer names no stage, core or later: stages come only after your partner ranks the outcomes." |
| dr-tracks A | `SKILL.md` §7 step 2, and the second bullet of "Outcomes and tracks" in `references/new-project-entry.md` | Adds "Two questions are unrelated when either answer stands without the other, even when both explain the same result." The reference also gets a transit example: "Whether late trips follow the weather and whether they follow the age of the buses are two questions, though both explain lateness." |
| dr-known-progression C | The "Later qualities" bullet of `references/new-project-entry.md` | Adds "Check the project against each one, and place every one it will need." and "The later stage or item that picks a quality up names it in its own fields, by the name that `Leaves out` gives it." |

The new text uses no word from a fixture domain. The tracks sentence sharpens what the spec's R4 calls unrelated
questions and adds no split criterion. The later-qualities text keeps R9's split: a later stage in a known
progression, a Ranked-list item in a research track. After the edit the derive-roadmap body measures 14,090
characters, and every Step 6 pin still prints `1`.

**Build, round 2.** The prompts were built with
`CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py 3ca7344 /tmp/plan78-work/t3-r1 trigger-stages trigger-decoy dr-offer-scaffold dr-offer-inputs dr-offer-yes dr-built-guard dr-known-progression dr-tracks dr-research-depth`.
Its `MANIFEST.txt` is copied to `treatment/t3-r1-MANIFEST.txt`. Checks on the build:

- The sha256 of `trigger-stages.txt` and `trigger-decoy.txt` is the same as in `t3-MANIFEST.txt`. Those prompts carry
  only the skill listing, and the description did not change. So the changed passages cannot reach them, and they
  were not re-run. Round 1 stays their arm of record.
- Each of the seven DR prompts holds a phrase of each edit: "The offer names no stage, core or later" (1), "either
  answer stands without the other" (2) and "by the name that `Leaves out` gives it" (1).
- The case-repository reads are the same as in round 1, and no prompt holds `red-baseline`, `plan 78` or the spec's
  file name.

**Re-run scope.** Every DR prompt carries the whole of `SKILL.md` and its references, and §1 and §7 sit on the path
of every DR case's decision. So all seven DR cases were re-run, the four that met their bar in round 1 included.
Each ran with
`bash specs/red-baseline-new-project-entry/kit/run_reps.sh /tmp/plan78-work/t3-r1/<case>.txt specs/red-baseline-new-project-entry/treatment/<case>-r1 1 5 claude-opus-5-5 1.00`.
The `-r1` folders keep the round-1 rep files in place. Before each call, the running total plus $5.00 stayed under $60.

### Round 2: dr-offer-scaffold

Additive. Arm `3ca7344`. Scored reps: rep1 to rep5 of `treatment/dr-offer-scaffold-r1/`. No VOID rep. Spend: $0.4103.

| Rep | A (bar) | B (bar) | C (bar) | PASS |
|---|---|---|---|---|
| 1 | pass | pass | pass | yes |
| 2 | pass | pass | pass | yes |
| 3 | pass | pass | pass | yes |
| 4 | pass | pass | pass | yes |
| 5 | pass | pass | pass | yes |

Clause A: 5 of 5 (round 1 2 of 5). Clause B: 5 of 5. Clause C: 5 of 5. PASS: 5 of 5. Bar: met.

- A. No rep previews a stage. Each says that the stages come after the ranking, for example rep1: "You would rank
  them, and stages would follow from your ranking." Rep4 describes the spec's own phases, which is not its own stage
  list: "Its Phase 1 is built on Azure infrastructure and integration tests before anything runs on real data."
- B. For example rep1: "Nothing in this repository is built yet."
- C. Each rep offers the entry beside a partition and waits, for example rep4: "You would then rank them before I lay
  out any stages."

Running total: $10.3434 of $60.

### Round 2: dr-offer-inputs

Additive. Arm `3ca7344`. Scored reps: rep1 to rep5 of `treatment/dr-offer-inputs-r1/`. No VOID rep. Spend: $0.6830.

| Rep | A (bar) | B (bar) | C (bar) | PASS |
|---|---|---|---|---|
| 1 | pass | pass | pass | yes |
| 2 | pass | pass | pass | yes |
| 3 | pass | pass | pass | yes |
| 4 | pass | pass | pass | yes |
| 5 | pass | pass (borderline) | pass | yes |

Clause A: 5 of 5. Clause B: 5 of 5. Clause C: 5 of 5. PASS: 5 of 5 (round 1 5 of 5). Bar: met.

- B, for example rep1: "By the skill's test, no outcome of this system works end to end on real data." Rep5 passes,
  borderline. Its question is headed "**1. Nothing built: stage this as a new project?**". It lists "**What
  works:** the implemented rows are acquisition and conventions", then says "Downloads alone don't count as a
  working outcome." The heading is an absolute statement, and the reply does not count acquisition as progress.
- A and C. No rep names a stage before the ranking, and each offers the entry beside a partition and waits.

Running total: $11.0264 of $60.

### Round 2: dr-offer-yes

Additive. Arm `3ca7344`. Scored reps: rep1 to rep5 of `treatment/dr-offer-yes-r1/`. No VOID rep. Spend: $0.6015.

| Rep | A (bar) | B (bar) | C (bar) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | pass | fail (borderline) | fail | pass | no |
| 2 | pass | fail (borderline) | fail (borderline) | pass | no |
| 3 | pass | pass | pass | pass | yes |
| 4 | pass | pass | pass | pass | yes |
| 5 | pass | pass | pass | pass | yes |

Clause A: 5 of 5. Clause B: 3 of 5 (round 1 4 of 5). Clause C: 3 of 5 (round 1 4 of 5). Clause D: 5 of 5. PASS: 3 of
5 (round 1 4 of 5). Bar: **missed**. It needs 4 of 5. This case met its bar in round 1, so this is an owner gate.

- B and C, reps 1 and 2. Each applies the later-qualities rule inside the one message. It places some outcomes in
  later stages, outside a core stage, before the partner ranks. By the dependency-fact reading that is a position
  ("H and I come last"), so B fails. By the stage-list reading it is a core stage and later stages in an order, so C
  fails. Quote (B and C, rep1): "The shared cross-collector lease (O7), the pointer (O6) and replay (O4) would be
  named later stages, not part of the core stage's exit." Rep1 also calls its Track A outcomes stages and orders
  them by the spec, which fails C on its own: "The spec names these stages in order." Quote (B and C, rep2): "Under
  the skill's rules, the core stage would run on one real quarter at the smallest usable standard. It would leave
  out manifests, pointers, the withdrawal gate and Azure, each placed in a named later stage."
- Rep1's "B depends on A's commands existing, so it would come after at least A's core stage." is a dependency fact
  and does not decide B.
- Reps 3 to 5 give dependency facts and the spec's order, labeled. Rep4 names no stage: "Once you've answered, I'll
  write the stages."
- D. Every rep gives a cost note with a basis, such as a file count at 3 requests per second.
- Other reading. If a core stage and its later-quality stages, said inside the one message, are not read as a stage
  list or a position, rep2 passes B and C. Rep1 still fails C on "The spec names these stages in order." PASS would
  then be 4 of 5 and the bar met. The owner can rule on this reading (Judgment-call reps, below).

Running total: $11.6279 of $60.

### Round 2: dr-built-guard

Non-regression (guard). Arm `3ca7344`. Scored reps: rep1 to rep5 of `treatment/dr-built-guard-r1/`. No VOID rep.
Spend: $0.2912.

| Rep | Guard rule | PASS |
|---|---|---|
| 1 | pass | yes |
| 2 | pass | yes |
| 3 | pass | yes |
| 4 | pass | yes |
| 5 | pass | yes |

Reps that pass the whole rule: 5 of 5 (control 5 of 5, round 1 5 of 5). Bar: met. Every rep says that the system
already works end to end and goes to the gap partition, for example rep2: "so this is a normal gap-driven partition,
not a new project." Rep5 names the definition only to say that it does not apply: "The project is not "nothing
built"".

Running total: $11.9191 of $60.

### Round 2: dr-known-progression

Additive. Arm `3ca7344`. Scored reps: rep1 to rep5 of `treatment/dr-known-progression-r1/`. No VOID rep. Spend:
$0.9532.

| Rep | B (bar) | A (conformance) | C (conformance) | D (conformance) | E (recorded) | PASS |
|---|---|---|---|---|---|---|
| 1 | pass | pass | fail (borderline) | pass | pass | no |
| 2 | pass | pass | fail | pass | pass | no |
| 3 | pass | pass | fail | pass | pass | no |
| 4 | pass | pass | fail | pass | pass | no |
| 5 | pass | pass | fail | pass | pass | no |

Clause B: 5 of 5. Clause A: 5 of 5. Clause C: 0 of 5 (round 1 0 of 5). Clause D: 5 of 5. Clause E (recorded): 5 of 5.
PASS: 0 of 5 (round 1 0 of 5). Bar: **missed**, through conformance clause C.

Clause C by quality:

| Quality | Round 1 | Round 2 | Round 2 reps that pass |
|---|---|---|---|
| manifest | 1 of 5 | 5 of 5 | all |
| traceability | 2 of 5 | 4 of 5 | rep1, rep3, rep4, rep5 |
| point-in-time (as-of) | 0 of 5 | 0 of 5 | none (rep1 borderline) |

- C. Every rep now names a manifest in a later stage, for example rep1's "Stage 4: Source manifest and raw-byte
  replay". Four reps name traceability, for example rep1: "every output row traces to its source file and hash", and
  rep5's "Stage 5: Submission and document traceability". Rep2's submissions are only "linked to their index rows".
  No rep names point-in-time or as-of awareness. Quote (C, rep1, the nearest): "Objective: Re-read quarterly indexes,
  record their changes, and publish index generations readers can pin." It names version pinning, not point-in-time
  awareness, so it does not pass (borderline). The background spec never raises as-of reads, so the quality has to
  come from the skill's list alone. With rep1 passed, C would be 1 of 5 and PASS 1 of 5, still below the bar.
- B. No first-stage Exit names a manifest, a per-row provenance record, as-of awareness or a spec section. Rep5's
  Exit asks for the full history ("Exit: the table holds the rows of every quarterly master index from 1993Q1 through
  the last closed quarter"), which is not the smallest standard, but clause B does not test that.
- A, D and E pass in every rep.

Running total: $12.8723 of $60.

### Round 2: dr-tracks

Additive. Arm `3ca7344`. Scored reps: rep1 to rep5 of `treatment/dr-tracks-r1/`. No VOID rep. Spend: $0.6754.

| Rep | A (bar) | B (conformance) | C (conformance) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | pass | pass (borderline) | fail (borderline) | pass | no |
| 2 | fail | pass (borderline) | pass (borderline) | pass | no |
| 3 | pass | pass | pass | pass | yes |
| 4 | pass | pass (borderline) | pass (borderline) | pass | yes |
| 5 | pass | pass (borderline) | fail | pass | no |

Clause A: 4 of 5 (round 1 2 of 5). Clause B: 5 of 5. Clause C: 3 of 5 (round 1 5 of 5). Clause D: 5 of 5. PASS: 2 of
5 (round 1 2 of 5). Bar: **missed**.

- A. Four reps split the collection-interval outcome from the capacity outcome and say why, for example rep4: "Split
  from C because the two questions are unrelated even though both explain revision size." Rep2 keeps them in one
  track. Quote (A, rep2): "I kept fast covariates (O4) and slow ones (O5) together because they're estimated jointly
  in one scale equation. Split them if you'd rather."
- C. Rep5 lists the stages of its known-progression track inside the one message. Quote (C, rep5): "I'd expect total
  nonfarm first, then stage dispersion, then supersectors with NSA/SA. Tell me if you'd name the stages
  differently." Rep1 fails, borderline, by the same core-and-later-stages reading as dr-offer-yes: "Its core stage
  builds the vintage panel that every other track consumes, so it likely goes first whatever the ranking." and "Some
  qualities go to later stages, never a core stage's Exit:", followed by four named qualities. Rep2 passes,
  borderline. It says it will place its qualities "in a named later stage or a Ranked-list item", which sets out no
  stage, and it names one stage first. Rep4 names one stage first, as in round 1, so it passes (borderline). Reps
  3 and 4 order outcomes inside a track without calling them stages.
- B. Every rep asks the partner to rank. Reps 1, 2, 4 and 5 put Track A's core stage first as a dependency fact, for
  example rep2: "There's one dependency regardless of ranking: B, C and D all consume A's panel, so A's core stage
  comes first." These pass by the dependency-fact reading (borderline).
- D. Every rep says that a run measures the fit cost.
- Other reading. With rep1 passed on C, PASS would be 3 of 5, still below the bar.

Running total: $13.5477 of $60.

### Round 2: dr-research-depth

Additive. Arm `3ca7344`. Scored reps: rep1 to rep5 of `treatment/dr-research-depth-r1/`. No VOID rep. Spend: $0.7232.

| Rep | A (bar) | B (bar) | C (conformance) | D (conformance) | E (conformance) | PASS |
|---|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | pass | yes |
| 2 | pass | pass | pass | pass | pass | yes |
| 3 | pass | pass | pass | pass | pass | yes |
| 4 | pass | pass | pass | pass | pass | yes |
| 5 | pass | pass | pass | pass | pass | yes |

Every clause: 5 of 5. PASS: 5 of 5 (round 1 5 of 5). Bar: met. Every rep commits one core stage per track and keeps
the other outcomes in the two Ranked lists. The later-qualities edit adds quality items to the Ranked lists, not
stage entries, for example rep5's "6. Point-in-time vintage store." and rep4's "Q-A4 — a vintage store with as-of
queries and download manifests."

Running total: $14.2710 of $60 (the per-case figures above are rounded, so the last one reads $14.2709 by sum).

### Task 3 summary and owner gate

| Case | Bar | Control | Round 1 (`48d9847`) | Round 2 (`3ca7344`) | Arm of record | Result |
|---|---|---|---|---|---|---|
| trigger-stages | additive | RED, 5 of 5 | 5 of 5 pass | not re-run (prompt unchanged) | round 1 | met |
| trigger-decoy | guard | 5 of 5 | 5 of 5 | not re-run (prompt unchanged) | round 1 | met |
| dr-offer-scaffold | additive | RED, 5 of 5 | 2 of 5 pass | 5 of 5 pass | round 2 | met |
| dr-offer-inputs | additive | RED, 5 of 5 | 5 of 5 pass | 5 of 5 pass | round 2 | met |
| dr-offer-yes | additive | RED, 4 of 5 | 4 of 5 pass | 3 of 5 pass | round 2 | **missed** (4 of 5 by the other reading) |
| dr-built-guard | guard | 5 of 5 | 5 of 5 | 5 of 5 | round 2 | met |
| dr-known-progression | additive | RED, 1 of 5 | 0 of 5 pass | 0 of 5 pass | round 2 | **missed** (C: point-in-time 0 of 5) |
| dr-tracks | additive | RED, 5 of 5 | 2 of 5 pass | 2 of 5 pass | round 2 | **missed** (3 of 5 by the other reading) |
| dr-research-depth | additive | RED, 5 of 5 | 5 of 5 pass | 5 of 5 pass | round 2 | met |

Six of the nine cases meet their bar. Three miss it after the one wording round. By plan 78's Bars and D13, that is
an owner gate at Task 3 Step 9. No second wording round ran.

- **dr-known-progression** misses through conformance clause C alone. Round 2 names manifests in 5 of 5 reps and
  traceability in 4 of 5, but point-in-time awareness in none. The background spec never raises as-of reads, so
  that quality would have to come from the skill's example list.
- **dr-tracks** misses through bar clause A in rep2 (the two covariate outcomes in one track) and conformance clause
  C in rep5 (a known-progression track's stages listed in the one message). Rep1 fails C on the core-and-later-stages
  reading (below).
- **dr-offer-yes** met its bar in round 1 (4 of 5) and misses it in round 2 (3 of 5). By the rule written above
  under "Arm of record", the better arm is not picked. Its verdict turns on one reading (below).

**The core-and-later-stages reading.** Several replies describe, inside an offer or inside the one message, a core
stage and the later stages that take the hardening or the later qualities. Task 3 scores that as a stage list by
the committed stage-list reading ("two or more stages in an order, as its proposed grouping or order of the work, in
any form"), as Task 2 scored control dr-offer-scaffold rep5 ("I'll put all fixture-only CI stages ahead of the infra
and orchestration stages"). For dr-offer-yes clause B, the same text places outcomes later, which is a position by
the dependency-fact reading. This is the committed reading applied, not a new one. It decides one verdict:
dr-offer-yes round 2 (3 of 5 by it, 4 of 5 without it). Without it, dr-offer-scaffold round 1 would also read 4 of
5, and dr-tracks round 2 would read 3 of 5. The round-2 edit to the later-qualities rule ("Check the project
against each one, and place every one it will need") may have drawn this text into the one message: it appears in
dr-offer-yes reps 1 and 2 and dr-tracks rep1 of round 2. In round 1, only dr-offer-yes rep3 had a
form close to it.

**Judgment-call reps (Task 3).** These rows extend the Judgment-call list in the Control section. Each rep was
scored on a close reading.

| Arm, case, rep, clause | Score | Deciding quote |
|---|---|---|
| round 1, dr-offer-scaffold rep1, A | fail (stage list) | "Hardening would move into named later stages: lease coordination, withdrawal approval, ADF and Container Apps, alerts and runbooks." |
| round 1, dr-offer-scaffold rep3, A | fail, borderline (core and later stages) | "Hardening such as Azure orchestration, leases and withdrawal gating would go into named later stages." |
| round 1, dr-offer-scaffold rep5, A | fail, borderline (core and later stages) | "Azure hardening (ADF, the lease, approval gates, alerts) would go to named later stages." |
| round 1, dr-offer-inputs rep3, A | pass, borderline (one item early) | "I plan to sequence by today's state, which means recording V4 and V5 early" |
| round 1, dr-offer-yes rep3, B and C | fail, borderline (position, stage list) | "It becomes the later stages of this one track, after the catalog works locally on real SEC data." |
| round 1, dr-known-progression reps 2 and 4, C (traceability) | not passed, borderline | "located by their index rows" (rep2), "linked to their index rows" (rep4) |
| round 1, dr-known-progression rep4, C (manifest) | not passed, borderline | Stage 1 `Leaves out` names a "source-state manifest", but Stage 4's fields name only "per-source state" |
| round 1, dr-tracks rep4, B and C | pass, borderline (dependency fact, one stage) | "B consumes A's vintage panel, so A's core stage comes first whatever the ranking." |
| round 1, dr-tracks rep5, A | pass, borderline (reason sets Track C apart from the model track) | "Split from B for two reasons: it answers an institutional question with weak identification, and its data must be hand-built." |
| round 2, dr-offer-inputs rep5, B | pass, borderline (absolute heading) | "**1. Nothing built: stage this as a new project?**" |
| round 2, dr-offer-yes rep1, B | fail, borderline (position) | "The shared cross-collector lease (O7), the pointer (O6) and replay (O4) would be named later stages, not part of the core stage's exit." |
| round 2, dr-offer-yes rep2, B and C | fail, borderline (core and later stages, decides the case) | "It would leave out manifests, pointers, the withdrawal gate and Azure, each placed in a named later stage." |
| round 2, dr-known-progression rep1, C (point-in-time) | not passed, borderline | "publish index generations readers can pin" |
| round 2, dr-tracks rep1, C | fail, borderline (core and later stages) | "Some qualities go to later stages, never a core stage's Exit:" |
| round 2, dr-tracks rep2, C | pass, borderline (no stage set out) | "in a named later stage or a Ranked-list item" |
| round 2, dr-tracks reps 1, 2, 4 and 5, B | pass, borderline (dependency fact) | "There's one dependency regardless of ranking: B, C and D all consume A's panel, so A's core stage comes first." (rep2) |

**Task 3 spend.** `uv run python specs/red-baseline-new-project-entry/kit/show_reps.py specs/red-baseline-new-project-entry/treatment/*/`
ran once after the last rep. It shows 80 reps, none VOID, and prints `total cost $8.47`. No rep file is empty or
unreadable, so none counts at its cap. There was no VOID rerun. Round 1 cost $4.1340 (45 reps) and round 2 cost
$4.3379 (35 reps), so Task 3 cost $8.4719. Running total: $14.2710 of $60. Control arms: $5.5029 of $30, unchanged.

**Owner ruling at the Task 3 gate (2026-11-06).** The owner chose "Record and continue": keep the current skill text
(`3ca7344`), record the three misses with their causes, run Tasks 4 to 6, and rule on all misses together at the plan
completion gate, as plan 77 did.

**Review finding for the owner, Task 3 (parked to the plan completion gate with the three misses).** The Task 3
reviewer found that entry item 2 in `skills/derive-roadmap/SKILL.md` ("Your partner asks for a roadmap for a project
that has nothing built (below) … with or without a spec → §7") also matches a plain "derive the roadmap for
`specs/X.md`" on a scaffold-only repository. Item 2 comes before item 4 in the entry order, so read literally the
agent goes straight to §7 and skips the §1 offer that the Common mistakes bullet requires. Both offer fixtures hand
the agent a finished gap analysis, so no micro-test exercises the entry decision. The text is the owner-approved text
of D16 and the one wording round is spent, so no edit was made. The reviewer's smallest fix: make item 2's condition
the partner's own statement ("Your partner says the project has nothing built and asks for a roadmap …").


## Treatment: Task 4

Task 4 makes derive-roadmap's resume (§5) and completion review (§6) understand the new-project roadmap. The skill
text was committed as `a98ff27` (`feat(derive-roadmap): resume and complete new-project roadmaps with ranked
lists`). Task 4 runs the treatment of two cases: dr-resume-rerank (additive) and dr-resume-legacy (guard). Each rep is
scored by its case's committed rule and by every reading in the Control section. No rule and no reading changed.

**Task 3's cases are not re-run.** They decide at entry, §1 and §7, which Task 4 does not touch.

**Build.** The prompts were built with
`CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py a98ff27 /tmp/plan78-work/t4 dr-resume-rerank dr-resume-legacy`.
Its `MANIFEST.txt` is copied to `treatment/t4-MANIFEST.txt`. Two checks ran on the build before any rep:

- Each prompt holds the paragraph "A research track waiting on its Ranked list" once and
  `derive-roadmap/references/new-project-entry.md` as a file block.
- No prompt holds `red-baseline`, `plan 78` or the spec's file name (the quarantine).

Each case ran with
`bash specs/red-baseline-new-project-entry/kit/run_reps.sh /tmp/plan78-work/t4/<case>.txt specs/red-baseline-new-project-entry/treatment/<case>-t4 1 5 claude-opus-5-5 1.00`,
one case at a time, into folders with a `-t4` suffix, so Task 3's folders are untouched. Before each call, the
running total plus the call's worst case ($5.00) stayed under $60.

### Task 4: dr-resume-rerank

Additive. Arm `a98ff27`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.2646.

| Rep | A (bar) | C (bar) | B (conformance) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | yes |
| 2 | pass | pass | pass | pass | yes |
| 3 | pass | pass | pass | pass | yes |
| 4 | pass | pass | pass | pass | yes |
| 5 | pass | pass | pass | pass | yes |

Clause A: 5 of 5 (control 4 of 5). Clause C: 5 of 5 (control 5 of 5). Clause B: 5 of 5 (control 2 of 5). Clause D: 5 of
5 (control 5 of 5). Bar: met. The treatment passes every clause in 5 of 5 reps, and the control fails a bar clause in
1 of 5 (rep4, clause A).

No bar clause fails in any rep, so there is no failure quote. What the reps do, for the record:

- A: no rep starts a completion review. Every rep offers stopping the track as one option of the question, and says
  its remaining items would park in `specs/deferred_items.md`. Parking offered as one option is not parking.
- C: each rep ends on one approve-or-amend question that proposes a default, which is to promote O2 as Stage 2.
  Rep1 also proposes a re-ranking (O2, then O4, then O3). The other four keep the order O2, O3, O4.
- B: each rep reports the 3.1 m level with the steep rise above it, and the measured cost of one fit on 11 years of
  daily gauge readings: 1.8 GB in 22 minutes on a laptop. All five name the findings file. The control's three
  failures were the missing 3.1 m level or rise.
- D: no rep writes a stage entry. Each describes Stage 2 inside the question and says it will write the entry after
  the answer.

Running total: $14.5356 of $60.

### Task 4: dr-resume-legacy

Non-regression (guard). Arm `a98ff27`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.2544.

| Rep | Guard rule | PASS |
|---|---|---|
| 1 | pass | yes |
| 2 | pass | yes |
| 3 | pass | yes |
| 4 | pass | yes |
| 5 | pass | yes |

Reps that pass the whole rule: 5 of 5 (control 5 of 5). Bar: met. The guard needs at least 4 of 5. Every rep says that
all three stages are ticked, reconciles with no amendment (plan 5's Handoff reads `None`), goes to the completion
review (§6) and lists the reads of the audit over R1 to R6. Every rep also says that no Ranked list is waiting.
No rep asks a re-ranking question. Reps 1, 2 and 5 end on a go-ahead question ("Shall I run these reads?"), which is
not a re-ranking question, as in control rep1.

Running total: $14.7900 of $60.

### Task 4 summary

| Case | Bar | Control | Treatment (`a98ff27`) | Result |
|---|---|---|---|---|
| dr-resume-rerank | additive | RED, 1 of 5 (rep4, A) | 5 of 5 pass | met |
| dr-resume-legacy | guard | 5 of 5 | 5 of 5 | met |

Both cases meet their bar in the first round, so no wording round ran.

**Judgment-call reps (Task 4).** These rows extend the Judgment-call list in the Control section. Each rep was
scored on a close reading. None changes a verdict.

| Case, rep, clause | Score | Deciding quote |
|---|---|---|
| dr-resume-rerank rep2, C | pass, borderline (one question with options) | "**My question:** should I keep your ranking (O2, then O3, then O4) and promote **O2, the 7-day outlook**, as Stage 2?", then "You could also amend this in one reply:" and three options |
| dr-resume-rerank rep5, C and D | pass, borderline (a proposed cost-note change inside the question, no stage entry) | "I'd also re-note O3's cost as \"to confirm: how many locks Stage 1's 1.8 GB covers\"." |
| dr-resume-rerank all reps, A | pass (stopping the track offered as one option, not parking) | "The alternative is to stop Track A here, which would park O2, O3 and O4 in `specs/deferred_items.md`." (rep1) |
| dr-resume-legacy rep3, guard | pass (a later question on audit exits, not a re-ranking) | "I'll put that choice to you as one question." |

**Task 4 spend.** `uv run python specs/red-baseline-new-project-entry/kit/show_reps.py specs/red-baseline-new-project-entry/treatment/dr-resume-rerank-t4/ specs/red-baseline-new-project-entry/treatment/dr-resume-legacy-t4/`
ran once after the last rep. It shows 10 reps, none VOID, and prints `total cost $0.52`. No rep file is empty or
unreadable, so none counts at its cap. There was no VOID rerun. The two cases cost $0.2646 and $0.2544, so Task 4
cost $0.5190. Running total: $14.7900 of $60. Control arms: $5.5029 of $30, unchanged.

**Review finding for the owner, Task 4 (parked to the plan completion gate).** The Task 4 reviewer found that "stop the
track" has two readings in the owner-approved text of D16. The new §5 paragraph sends a stopped track's items to "the
Parking rule below". That rule ends by moving the whole roadmap to `specs/completed/` marked
`PARKED (date) — N of M stages complete`. The new §6 sentence says never-promoted items "have parked (§5)", which
assumes §6 still runs after a stop. So when the partner answers "stop the track", the agent can read either "park the
whole roadmap now, with no completion audit" or "park the items, then run §6 and retire". In a two-track roadmap the
first reading also parks the track that is still live. No micro-test reaches this path: `dr-resume-rerank` has one
track and no rep receives a "stop" answer. No edit was made. The reviewer's smallest fix: say in the new paragraph that
a stopped track's items append to `specs/deferred_items.md` under the Parking rule's item schema, and that the roadmap
itself moves only through §6 or when the partner parks the whole roadmap. Task 4's treatment arms met their bars in
round 1, with a thin control for `dr-resume-rerank` (the control failed a bar clause in 1 of 5 reps).

## Treatment: Task 5

Task 5 teaches describe-critique-methodology, in both modes, to stop on a system with nothing built and to route it to
derive-roadmap's New-Project Entry. The skill text was committed as `abc1ecb` (`feat(describe-critique-methodology):
route a system with nothing built to derive-roadmap`). Task 5 runs the treatment of two cases: dcm-describe-route and
dcm-synth-route. Both are additive. Each rep is scored by its case's committed rule and by every reading in the Control
section, including the corrected template-slot reading and the plan-or-option reading. No rule and no reading changed.

**Other cases are not re-run.** Task 5 edits only describe-critique-methodology's SKILL.md body (its description is
unchanged, so every skill listing is unchanged). The derive-roadmap and brainstorming cases read neither the changed
body nor a changed description, so their prompts and their scores are the same as before.

**Build.** The prompts were built with
`CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py abc1ecb /tmp/plan78-work/t5 dcm-describe-route dcm-synth-route`.
Its `MANIFEST.txt` is copied to `treatment/t5-MANIFEST.txt`. Two checks ran on the build before any rep:

- Each prompt holds the paragraph "Built systems only" once, the Synthesize paragraph "First, check what the files
  are" once, and the name `derive-roadmap's New-Project Entry` five times (the five places that the plan lists).
- No prompt holds `red-baseline`, `plan 78`, or the file name of the spec (the quarantine).

Each case ran with
`bash specs/red-baseline-new-project-entry/kit/run_reps.sh /tmp/plan78-work/t5/<case>.txt specs/red-baseline-new-project-entry/treatment/<case>-t5 1 5 claude-opus-5-5 1.00`,
one case at a time, into folders with a `-t5` suffix, so earlier folders are untouched. Before each call, the running
total plus the call's worst case ($5.00) stayed under $60.

### Task 5: dcm-describe-route

Additive. Arm `abc1ecb`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.2633.

| Rep | A (bar) | B (bar) | C (bar) | PASS |
|---|---|---|---|---|
| 1 | pass | pass | pass | yes |
| 2 | pass | pass | pass | yes |
| 3 | pass | pass | pass | yes |
| 4 | pass | pass | pass | yes |
| 5 | pass | pass | pass | yes |

Clause A: 5 of 5 (control 1 of 5). Clause B: 5 of 5 (control 5 of 5). Clause C: 5 of 5 (control 0 of 5). Bar: met on the
readings applied (see Other readings, below). The treatment passes every clause in 5 of 5 reps, and the control
failed a bar clause in 5 of 5.

No bar clause fails in any rep, so there is no failure quote. What the reps do, for the record:

- A: no rep writes a description, a notation table or any template section, and none plans one as the next step. Each
  lists what the repo holds (stub packages, the proposed spec) and stops. Reps 2 and 4 name the parts that a later
  description could cover, once the system is built. That is a later step, not the next one.
- B: each rep says in its first sentence or heading that the system is not built: "nothing is built yet" (reps 1 and
  4), "nothing in this system is built yet" (reps 2 and 5), "isn't built yet" (rep3).
- C: each rep names derive-roadmap's New-Project Entry as the next step, with the spec and its ADR as input, and
  tells the partner to start a fresh session (reps 1 to 4 quote the prompt to say). Each puts the critique after the
  build. No rep offers brainstorming or
  design-architecture in place of derive-roadmap. Rep3 offers design-architecture only as the path for a design
  review that the partner may want now, beside the route.

### Task 5: dcm-synth-route

Additive. Arm `abc1ecb`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.2398.

| Rep | A (bar) | B (bar) | C (bar) | PASS |
|---|---|---|---|---|
| 1 | pass | pass | pass | yes |
| 2 | pass | pass | pass | yes |
| 3 | pass | pass | pass | yes |
| 4 | pass | pass | pass | yes |
| 5 | pass | pass | pass | yes |

Clause A: 5 of 5 (control 2 of 5). Clause B: 5 of 5 (control 5 of 5). Clause C: 5 of 5 (control 0 of 5). Bar: met on the
readings applied (see Other readings, below). The treatment passes every clause in 5 of 5 reps, and the control
failed a bar clause in 5 of 5.

No bar clause fails in any rep, so there is no failure quote. What the reps do, for the record:

- A: every rep says it wrote no triage table and no spec, and gives the reason (the research proposes designs and
  critiques no built method). No rep plans either one as a next step.
- B: every rep calls `specs/ces-revisions-prompt.md` a research brief, and says that nothing is built. Rep3 and rep4
  add that no part of the system runs end to end on real data.
- C: every rep names derive-roadmap's New-Project Entry and gives it the brief and the three research files as
  background. Each hands the partner a fresh-session prompt that lists the four files.

Running total: $15.2931 of $60.

### Task 5 summary

| Case | Bar | Control | Treatment (`abc1ecb`) | Result |
|---|---|---|---|---|
| dcm-describe-route | additive | RED, 5 of 5 (C in every rep) | 5 of 5 pass | met (A would be 3 of 5 or fewer by an other reading) |
| dcm-synth-route | additive | RED, 5 of 5 (C in every rep) | 5 of 5 pass | met (A would be 3 of 5 if reps 1 and 5 both fail) |

Both cases meet their bar in the first round on the readings applied, so no wording round ran. No rep was VOID.
The Other readings note below gives the readings that would change a bar.

**Judgment-call reps (Task 5).** These rows extend the Judgment-call lists in the Control section and in Task 4. Each
rep was scored on a close reading. No score changes. Rows for dcm-describe-route clause A and dcm-synth-route clause A
rest on a reading that, ruled the other way, would change a bar. The Other readings note below gives the counts.

| Case, rep, clause | Score | Deciding quote |
|---|---|---|
| dcm-describe-route rep2, A | pass, borderline (a pointer to a later description, not a slot's content written now and not the next step) | "Come back to describe-critique-methodology once at least one outcome runs end to end on real data. Good candidates are the parse → canonical catalog path with its identity and precedence rules (§4.4), or the reconciliation and withdrawal gate." The template's "Open questions for the reviewer" slot is numbered questions addressed to the reviewer. This line asks none and sits under the heading "**After it's built**", so it is a pointer to what a later module-level description could cover. |
| dcm-describe-route rep2, C | pass (critique placed after the build, by the reply's own heading) | "**After it's built**", then "Come back to describe-critique-methodology once at least one outcome runs end to end on real data." |
| dcm-describe-route rep3, C | pass, borderline (critique placed after a working slice) | "The external critique fits better once a working slice exists, such as backfill plus publication running on real indexes." The reply also says "A description written now would describe the spec's intentions." |
| dcm-describe-route reps 2, 4 and 5, A | pass (a list of parts inside a statement of absence, not a Component inventory) | rep2: "No outcome of the filing-index ingestion system (discovery, collection, parsing, reconciliation or publication) works end to end on real data." rep4: "No discovery, collection, parsing, reconciliation or publication code exists." rep5: "discovery, collection, parsing, reconciliation and publication running end to end on real index files". Each names the parts only inside a sentence about what the repository lacks. Control rep4 opens its list as the content of the description it offers: "**Granularity: system.** The components are named by role:". The reading counts a component inventory "with or without outputs", so the distinction is where the list sits, not whether it gives outputs. Under the other reading of this row, see Other readings, below. |
| dcm-describe-route rep3, A | pass, borderline (a design review offered beside the route; no questions to the reviewer, no slot written) | "If you mainly want outside review of the *design* now, especially the identity key `(cik, archive_path)`, the withdrawal gate, and the per-quarter atomicity contract, that would be a design or ADR review (the design-architecture skill), not this round-trip." The line names where a design review would look. It is not the "Open questions for the reviewer" slot (no numbered questions, and it sends that review to another skill, not to a description). |
| dcm-describe-route rep4, A | pass, borderline (a pointer to a later description, not a slot's content written now and not the next step) | "The design to critique will then be its record identity and precedence rules, withdrawal gating and per-quarter publication." "Then" is after the build ("Once the system works end to end on real data, come back and ask for the methodology description again"). The line asks no question of a reviewer. |
| dcm-synth-route rep1, A | pass, borderline (items to check, not accept, reject or defer verdicts) | "Some things to check before treating any of them as settled:", then three items on the research files' figures and one claim. Control rep1's "Factual premises become `(open — resolved by verification, not argument)`" was triage content, a verdict label. It kept its pass only because the committed carve-out covers content inside a triage that is offered as one option of a question. Treatment rep1 offers no triage. Its items sort no research point into accept, reject or defer. If this rep alone failed A, the case would keep 4 of 5. With rep5 also failed, it would not (see Other readings, below). |
| dcm-synth-route rep5, A | pass, borderline (a list of points the reports agree on, no verdicts) | "They agree on a lot that a roadmap can stage. Examples:", then seven points |
| dcm-describe-route rep3 and dcm-synth-route reps 3 and 4, not scored (stage lists) | not a clause of these cases | dcm-describe-route rep3: "for example: shared downloader with one request budget, then parse and validate, then manifest and publication, then reconciliation". dcm-synth-route rep3: "likely the vintage-data acquisition first, then a constant-variance baseline, then the scale model". Both cases' clause A reads a methodology description, triage or spec, not a stage list. The reps describe what derive-roadmap would do. |

**Other readings (Task 5).** Every score above stands, and both cases meet their bar on the readings applied. Three
close readings decide the two bars. The counts below were re-read from the raw replies in
`treatment/dcm-describe-route-t5/` and `treatment/dcm-synth-route-t5/`. The owner can rule on these readings at the
plan completion gate. Each bar needs clause A in at least 4 of 5 reps.

- dcm-describe-route, reading 1: a list of parts inside a statement of absence is a Component inventory. The
  confirmed template-slot reading counts "a component inventory (components by role, with or without outputs)".
  Reps 2, 4 and 5 list the parts only to say that none works or exists (rep2: "(discovery, collection, parsing,
  reconciliation or publication)"; rep4: "No discovery, collection, parsing, reconciliation or publication code
  exists."; rep5: "discovery, collection, parsing, reconciliation and publication running end to end on real index
  files"). They fail A under this reading. Rep3's "not even discovery or download" names two parts and is the weakest
  case. Clause A is then 2 of 5 (reps 1 and 3) if rep3's pair does not count, and 1 of 5 (rep1 only) if it does.
  A wider form counts any list of the system's parts by role, wherever it sits. Then rep1 and rep4 also fail on
  "discovery, downloader, parser, manifest, publisher and CLI" (the spec's proposed package), and rep3 fails on "shared
  downloader with one request budget, then parse and validate, then manifest and publication, then reconciliation".
  Clause A is then 0 of 5. The bar is missed under all three counts.
- dcm-describe-route, reading 2: a pointer to critique targets is the "Open questions for the reviewer" slot, which
  the template describes as "the places you want the critique to push". Rep2 ("Good candidates are the parse →
  canonical catalog path with its identity and precedence rules (§4.4), or the reconciliation and withdrawal gate.")
  and rep4 ("The design to critique will then be its record identity and precedence rules, withdrawal gating and
  per-quarter publication.") fail A under this reading. Clause A is then 3 of 5 (reps 1, 3 and 5). Rep3 names targets
  of a design review that it sends to another skill ("especially the identity key `(cik, archive_path)`, the
  withdrawal gate, and the per-quarter atomicity contract"). If it counts too, clause A is 2 of 5. The bar is missed
  under both counts.
- dcm-synth-route, reading 3: a list that sorts the research points into verdict-like groups is a triage list ("or
  similar verdicts"). Rep1's list under "Some things to check before treating any of them as settled:" and rep5's
  "They agree on a lot that a roadmap can stage. Examples:" with its disagreements are the two candidates. If either
  fails alone, clause A is 4 of 5 and the bar is met. If both fail, clause A is 3 of 5 (reps 2, 3 and 4) and the bar
  is missed.

Why the scores stand: the committed rules and readings define a filled slot as the section's own content written in
the reply (an inventory, numbered questions to the reviewer, a notation table), and a triage list as a sort into
verdicts. The lines above are statements of absence, pointers to a later description, a design review offered beside
the route, or lists to check and to discuss. They do not meet those definitions.

**Task 5 spend.** `uv run python specs/red-baseline-new-project-entry/kit/show_reps.py specs/red-baseline-new-project-entry/treatment/dcm-describe-route-t5/ specs/red-baseline-new-project-entry/treatment/dcm-synth-route-t5/`
ran once after the last rep. It shows 10 reps, none VOID, and prints `total cost $0.50`. No rep file is empty or
unreadable, so none counts at its cap. There was no VOID rerun. The two cases cost $0.2633 and $0.2398, so Task 5 cost
$0.5031. Running total: $15.2931 of $60. Control arms: $5.5029 of $30, unchanged.

## Treatment: Task 6

Task 6 teaches brainstorming to hand a new project of several stages, with nothing built yet, to derive-roadmap's
New-Project Entry in the same session. The skill text was committed as `1f64a61` (`feat(brainstorming): hand a new
multi-stage project with nothing built to derive-roadmap`). Task 6 runs the treatment of two cases: bs-route
(additive) and bs-guard (guard). Each rep is scored by its case's committed rule and by every reading in the Control
section. No rule and no reading changed.

**Other cases are not re-run.** Task 6 edits only the brainstorming SKILL.md body. Its description is unchanged, so
every skill listing is unchanged, and no other case reads the brainstorming body. This was checked, not only
argued. The prompts of the two trigger cases, of dr-resume-rerank and dr-resume-legacy, and of dcm-describe-route and
dcm-synth-route were rebuilt at `1f64a61` into `/tmp/plan78-work/t6-check` (no rep ran). Each prompt has the same
sha256 as in its earlier arm: the trigger cases as in `t3-MANIFEST.txt`, the two resume cases as in
`t4-MANIFEST.txt`, and the two dcm cases as in `t5-MANIFEST.txt`. The other DR cases carry no brainstorming text and
the same listing, so the change cannot reach them either.

**Build.** The prompts were built with
`CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py 1f64a61 /tmp/plan78-work/t6 bs-route bs-guard`.
Its `MANIFEST.txt` is copied to `treatment/t6-MANIFEST.txt`. Two checks ran on the build before any rep:

- Each prompt holds the paragraph "A new project of several stages goes to a roadmap" once and the name
  `derive-roadmap's New-Project Entry` four times, each within one line. (The skill's fifth `derive-roadmap` is "If
  derive-roadmap is not installed", and the several-projects sentence says only "the New-Project Entry".) The
  derive-roadmap line of each listing holds the description at `1f64a61`.
- No prompt holds `red-baseline`, `plan 78` or the spec's file name (the quarantine).

Each case ran with
`bash specs/red-baseline-new-project-entry/kit/run_reps.sh /tmp/plan78-work/t6/<case>.txt specs/red-baseline-new-project-entry/treatment/<case>-t6 1 5 claude-opus-5-5 1.00`,
one case at a time, into folders with a `-t6` suffix, so earlier folders are untouched. Before each call, the running
total plus the call's worst case ($5.00) stayed under $60.

### Task 6: bs-route

Additive. Arm `1f64a61`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.1725.

| Rep | A (bar) | B (bar) | C (bar) | PASS |
|---|---|---|---|---|
| 1 | pass | pass | pass | yes |
| 2 | fail | pass (borderline) | pass | no |
| 3 | pass | pass | pass | yes |
| 4 | pass (borderline) | pass | pass | yes |
| 5 | pass | pass | pass | yes |

Clause A: 4 of 5 (control 0 of 5). Clause B: 5 of 5 (control 4 of 5). Clause C: 5 of 5 (control 5 of 5). PASS: 4 of
5. Bar: met on the readings applied (see Other readings, below). The treatment passes every clause in 4 of 5 reps,
and the control failed a bar clause in 5 of 5.

- A, rep2, fail. It plans the roadmap, names no skill and asks a question first. A handoff that is put off, or only
  asked about, fails. Quote (A, rep2): "Before I do that, one thing would change the first stage a lot. Is the year
  a past one, like 2025, that we can pull from the stations' archives today?"
- A, reps 1, 3, 4 and 5. Each says it hands the outcomes over and writes the call. Reps 1, 3 and 4 say "now", for
  example rep3: "Handing it to the roadmap step now, with your outcomes in your words:". Rep5 says "I'm handing this
  to the roadmap step with your outcomes as you stated them:". Each is followed by a block that begins
  `Skill: derive-roadmap (New-Project Entry)`. Each block gives the outcomes in the partner's words, in their order,
  with the harbor-master group, the one-year success line and the Python-on-a-laptop constraint.
- B passes in every rep. No rep lays out ways to build the whole project. Each says that each stage gets its own
  design when it is reached, and reps 1, 3, 4 and 5 add that questions such as which four stations and how to fill
  gaps wait for those sessions. Every rep gives the partner's order as the stages (collect, clean and fill, publish),
  which is not an approach.
- C passes in every rep. No rep writes a design document, a spec or any roadmap text. Reps 1, 3, 4 and 5 hand over
  a call block with the outcomes and the partner's answers, and reps 3 and 4 add the questions left open for the
  stage. Rep2's question (past year or a year collected from now) is not answered by the conversation, so it is not
  a question that the conversation already answers. No other rep asks a question. Reps 1, 3 and 5 only say that the
  partner can ask for a single design instead.

Running total: $15.4656 of $60.

### Task 6: bs-guard

Non-regression (guard). Arm `1f64a61`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.1651.

| Rep | Guard rule | PASS |
|---|---|---|
| 1 | fail | no |
| 2 | pass | yes |
| 3 | pass | yes |
| 4 | pass | yes |
| 5 | pass | yes |

Reps that pass the whole rule: 4 of 5 (control 4 of 5). Bar: met. The guard needs at least 3 of 5. Every rep lays out
two or three ways to build the script (reps 2 to 5 give two, rep1 gives three), recommends one and asks which way to
go. No rep names derive-roadmap or hands off to it. Rep1 fails the rule for the reason that control rep1 failed: its
one question also asks about its defaults. Quote (guard, rep1): "Which approach do you want, and do those defaults
match how you'd count a track with a long stop in it?" Rep5 states its defaults as ones "which you can override" and
asks only "Which way do you want to go?", so it passes. Its closing line, "after you pick I'll write a short design
here for your OK and then build it with tests", is a plan and not a question.

Running total: $15.6307 of $60.

### Task 6 summary

| Case | Bar | Control | Treatment (`1f64a61`) | Result |
|---|---|---|---|---|
| bs-route | additive | RED, 5 of 5 (A in every rep) | 4 of 5 pass (A 4 of 5) | met on the readings applied (A would be 3 of 5 and the bar missed if rep4 fails A) |
| bs-guard | guard | 4 of 5 | 4 of 5 | met |

Both cases meet their bar in the first round, so no wording round ran. No rep was VOID.

**Judgment-call reps (Task 6).** These rows extend the Judgment-call lists in the Control section and in Tasks 3 to
5. Each rep was scored on a close reading. The row for bs-route rep4, clause A, rests on a reading that, ruled the
other way, would change the bar. Other readings, below, gives the counts.

| Case, rep, clause | Score | Deciding quote |
|---|---|---|
| bs-route rep4, A | pass, borderline (the handoff is stated as now and written; the closing line offers a chance to object) | "I'm handing this to the roadmap step now, with your outcomes in your words:", then `Skill: derive-roadmap (New-Project Entry)`. The reply ends: "If any of that is off, tell me before the roadmap is written. Otherwise I'll go ahead." The reading notes pass a written Skill call or a statement that it hands over now. This rep has both. |
| bs-route rep2, A | fail (the handoff is put off by a question, and the skill is not named) | "Before I do that, one thing would change the first stage a lot." |
| bs-route rep2, B | pass, borderline (two readings of one outcome, not two ways to build the whole project) | "A past year means fetching a large batch of history once. A year going forward means a small collector that runs regularly on their laptop for twelve months without missing data." The two readings bear on the first stage only. If they counted as approaches, B would be 4 of 5. PASS would not change, because rep2 already fails A. |
| bs-route all reps, B | pass (the partner's own order, said back, is not an approach) | "Rather than design the whole thing now, I'll lay out those four stages, in your order, in a roadmap file." (rep5) |
| bs-route rep2, C | pass (a question the conversation does not answer) | "Is the year a past one, like 2025, that we can pull from the stations' archives today?" The partner said "one year of clean monthly extremes", and did not say whether that year is past or to come. |
| bs-guard rep1, guard | fail (a second question) | "Which approach do you want, and do those defaults match how you'd count a track with a long stop in it?" |
| bs-guard rep5, guard | pass, borderline (defaults offered as overridable, one question) | "A few defaults I'd use either way, which you can override:", then "Which way do you want to go?" |
| bs-guard reps 2 to 5, guard | pass (two ways meet "two or three") | "Two ways to build it:" (rep2) |

**Other readings (Task 6).** Every score above stands, and both cases meet their bar on the readings applied. One
reading decides the bs-route bar. The counts below were re-read from the raw replies in
`treatment/bs-route-t6/`. The owner can rule on this reading at the plan completion gate. The bar needs the treatment
to pass every clause in at least 4 of 5 reps.

- bs-route, reading 1: a handoff that ends "tell me before the roadmap is written. Otherwise I'll go ahead" is a
  handoff put to the partner for approval, not a handoff now. Rep4 then fails A. Clause A is 3 of 5 (reps 1, 3 and 5)
  and PASS is 3 of 5. The bar is missed. Control dcm-describe-route reps 1 and 5 (rep1: "Tell me if you'd rather go
  that way. Otherwise I'm proceeding."; rep5: "My plan, unless you'd rather point the critique at the spec directly")
  were read as stating the plan, so the description stayed as their next step and
  failed A. The same plan-or-option reading applied here keeps the handoff as rep4's next step, and it says "now"
  and writes the call before its closing line. So the score stands as a pass. Reading 1 is the owner's alternative.

Why the score stands: the reading notes for clause A name two ways to pass, a written Skill call and a statement of
handing over now, and fail only a handoff put off to a later or fresh session or asked about as a question. Rep4's
reply makes the call and says it is making it now. Its closing line does not move the call to a later session and
asks no question.

**Task 6 spend.** `uv run python specs/red-baseline-new-project-entry/kit/show_reps.py specs/red-baseline-new-project-entry/treatment/bs-route-t6/ specs/red-baseline-new-project-entry/treatment/bs-guard-t6/`
ran once after the last rep. It shows 10 reps, none VOID, and prints `total cost $0.34`. No rep file is empty or
unreadable, so none counts at its cap. There was no VOID rerun. The two cases cost $0.1725 and $0.1651, so Task 6
cost $0.3376. Running total: $15.6307 of $60. Control arms: $5.5029 of $30, unchanged.

## All arms side by side

One row per case. Every figure is taken from this record's own tables. Each count is the number of the 5 scored reps
that pass the clause. The control columns give the control arm at `BASE` (`1844bd8`) and the treatment columns give
the arm of record of the case's task: Task 3's derive-roadmap cases use round 2 (`3ca7344`), Task 3's two trigger
cases use round 1 (`48d9847`, their prompts did not change), Task 4 uses `a98ff27`, Task 5 uses `abc1ecb` and Task 6
uses `1f64a61`. Only bar clauses are counted in the clause columns. A conformance clause can still decide the bar
result, and the Bar result column says so where it does. A guard case has no bar clause, so its columns give the
reps that pass the whole rule.

| Case | Kind | Control, bar clauses | Treatment, bar clauses | Treatment PASS | Bar result | Clean control |
|---|---|---|---|---|---|---|
| trigger-stages | additive | A 0 | A 5 | 5 of 5 | met | no (RED, 5 of 5) |
| trigger-decoy | guard | 5 of 5 pass | 5 of 5 pass | 5 of 5 | met (needs 4 of 5) | n/a |
| dr-offer-scaffold | additive | A 3, B 5, C 0 | A 5, B 5, C 5 | 5 of 5 | met in round 2. Round 1 (`48d9847`) missed (PASS 2 of 5, A 2 of 5), so the one wording round ran | no (RED, 5 of 5) |
| dr-offer-inputs | additive | A 2, B 0, C 0 | A 5, B 5, C 5 | 5 of 5 | met (B rep5 borderline in round 2). Round 1 also met, 5 of 5 | no (RED, 5 of 5) |
| dr-offer-yes | additive | A 5 (by the labeled-list reading; 0 on form alone), B 2, C 2 | A 5, B 3, C 3 | 3 of 5 | **missed**: PASS 3 of 5, and 4 of 5 by the other reading of the core-and-later-stages text. Round 1 met (4 of 5), so this was an owner gate. Owner ruling at the Task 3 gate: "Record and continue" | no (RED, 4 of 5) |
| dr-built-guard | guard | 5 of 5 pass | 5 of 5 pass | 5 of 5 | met (needs 4 of 5) | n/a |
| dr-known-progression | additive | B 4 (by the by-reference reading; B 5 by the other reading) | B 5 | 0 of 5 | **missed** through conformance clause C (point-in-time awareness 0 of 5, though manifest 5 of 5 and traceability 4 of 5), although bar clause B is 5 of 5 | no by the by-reference reading (RED, 1 of 5); yes by the other reading of B (B 5 of 5) |
| dr-tracks | additive | A 0 | A 4 | 2 of 5 | **missed**: PASS 2 of 5, and 3 of 5 by the other reading. Rep2 fails bar clause A (two covariate outcomes in one track). Reps 1 and 5 fail conformance clause C (stage lists in the one message). Round 1 also missed (PASS 2 of 5) | no (RED, 5 of 5) |
| dr-research-depth | additive | A 0, B 0 | A 5, B 5 | 5 of 5 | met. Round 1 also met, 5 of 5 | no (RED, 5 of 5) |
| dr-resume-rerank | additive | A 4, C 5 | A 5, C 5 | 5 of 5 | met against a thin control: the control failed a bar clause in 1 of 5 reps (rep4, A) | no (thin: RED in 1 of 5) |
| dr-resume-legacy | guard | 5 of 5 pass | 5 of 5 pass | 5 of 5 | met (needs 4 of 5) | n/a |
| dcm-describe-route | additive | A 1 (0 before fix round 1), B 5, C 0 | A 5, B 5, C 5 | 5 of 5 | met on the readings applied. Under the other readings (Task 5, Other readings) A is 3 of 5 or fewer, and the bar is missed | no (RED, 5 of 5) |
| dcm-synth-route | additive | A 2, B 5, C 0 | A 5, B 5, C 5 | 5 of 5 | met on the readings applied. A is 3 of 5, and the bar is missed, if reps 1 and 5 both fail A (Task 5, Other readings) | no (RED, 5 of 5) |
| bs-route | additive | A 0, B 4, C 5 | A 4, B 5, C 5 | 4 of 5 | met on the readings applied. A is 3 of 5, PASS is 3 of 5 and the bar is missed, if rep4 fails A (Task 6, Other readings) | no (RED, 5 of 5) |
| bs-guard | guard | 4 of 5 pass | 4 of 5 pass | 4 of 5 | met (needs 3 of 5) | n/a |

**Counts.** 12 of the 15 cases meet their bar and 3 miss it: dr-offer-yes, dr-known-progression and dr-tracks. All
three are Task 3 derive-roadmap cases that missed after the one wording round. The owner ruled "Record and continue"
at the Task 3 gate, so all three go to the plan completion gate with the other items below. Of the 12 that meet their
bar, three meet it only on the readings applied (dcm-describe-route, dcm-synth-route and bs-route), and one meets it
against a thin control (dr-resume-rerank). dr-offer-scaffold meets it only after a wording round. The four guard
cases (trigger-decoy, dr-built-guard, dr-resume-legacy, bs-guard) all meet their bar and have no clean-control flag.

**Clean controls.** No additive case has a clean control under the readings applied. dr-known-progression would have
one under the other reading of its clause B, and it goes to the owner at the completion gate on that ground. Two
additive controls are thin, with a bar clause that fails in 1 of 5 reps: dr-resume-rerank (rep4, clause A) and
dr-known-progression (rep5, clause B, by the by-reference reading).

**For the owner at the plan completion gate.** The three misses and their causes (Task 3 summary). The
dr-known-progression clean control (Control summary). The other-reading counts that decide dcm-describe-route,
dcm-synth-route and bs-route (Task 5 and Task 6, Other readings). The review findings parked from Task 3 (entry item
2) and Task 4 ("stop the track"). No Task 6 edit is parked.

**Spend total.** Spend by task: Task 1 $0.2962 (isolation probe $0.0141 and cost pilot $0.2821), Task 2 $5.5029
(control arms), Task 3 $8.4719, Task 4 $0.5190, Task 5 $0.5031 and Task 6 $0.3376. These sum to **$15.6307 of $60**.
The control arms alone cost $5.5029 of $30, unchanged: treatment reps count toward the $60 only. The per-case figures
in this record sum to the same total, except Task 3's, which are rounded and sum to $0.0001 less (Round 2: dr-research-depth). No rep was VOID and there was no VOID rerun in any task, and no rep file was
empty or unreadable. The Spend table, the "Running total after Task 6" paragraph and this total agree.

## Treatment: Task 7 (final-review fixes)

Task 7 was added at the plan completion gate. It is not in the plan file. On 2026-11-06 the owner chose "Fix all four
now" for four routing gaps that the final whole-branch review found in derive-roadmap's new-project text. The four
edits were committed as `f824492` (`fix(derive-roadmap): close four routing gaps found by the final review`). Task 7
re-runs the treatment of the nine cases whose prompts carry derive-roadmap text. Each rep is scored by its case's
committed rule and by every reading in the Control section. No rule and no reading changed.

**The four edits.** They change only `skills/derive-roadmap/SKILL.md`, `references/roadmap-format.md` and
`references/new-project-entry.md`. The new text is the brief's text, wrapped like the text around it. No
description changed.

| Edit | Passage | Change |
|---|---|---|
| 1 | `SKILL.md`, entry item 2 | Item 2 now starts from the partner's own statement: "Your partner says the project has nothing built (below) and asks for a roadmap". It adds "A request that only names a spec is not this case: §1 runs the gap analysis and makes the offer." This is the Task 3 review finding (entry item 2). |
| 2 | `SKILL.md` §5, the research-track paragraph and the Parking rule | When the partner stops a research track, only that track's Ranked-list items park, and the roadmap stays live. It moves only through §6, or when the partner parks the whole roadmap. This is the Task 4 review finding ("stop the track"). |
| 3 | `SKILL.md` §5 and its Quick reference row, the `Produces` line of the stage-entry template in `references/roadmap-format.md`, and the Research bullet of `references/new-project-entry.md` | A re-rank reads the findings file of the track's most recently ticked stage. A stage promoted from a Ranked list names its own findings file in `Produces`. |
| 4 | `references/roadmap-format.md` (New-project roadmaps) and `references/new-project-entry.md` (The one message, items 4 and 5) | With a spec, the name is the spec's stem, and §3's scan applies first. The one message proposes a name, and asks the partner to confirm it, only with no spec. |

**Checks after the edits.** The four pins each print `1`. The one-definition check prints one line,
`2 **Nothing built** means that no outcome …`. The derive-roadmap body measures 15,400 characters. The commit lints
passed. The brief's check `grep -c "stopped track\|most recently ticked stage\|only that track"` on `SKILL.md` prints
2, not the 4 that the brief expects. Each of the three phrases occurs at most once in the brief's own new text. Edit
2(b) says "only the items of that track's", which the pattern does not match, and the one old "stopped track" leaves
with Edit 2(b). So 2 is the most that any wrapping gives. Direct checks over the three files confirm the intent: each
new phrase occurs once, and `its core stage's`, `a stopped track's Ranked list` and `Remaining unticked stages, and`
each occur 0 times. No text was added to reach 4.

**Build.** The prompts of all 15 cases were built with
`CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py f824492 /tmp/plan78-work/t7`.
Its `MANIFEST.txt` is copied to `treatment/t7-MANIFEST.txt`. Checks on the build before any rep:

- The six cases that read no derive-roadmap text have prompts that `cmp` finds byte-identical to their arms of
  record: trigger-stages and trigger-decoy to `/tmp/plan78-work/t3-r1/`, dcm-describe-route and dcm-synth-route to
  `/tmp/plan78-work/t5/`, and bs-route and bs-guard to `/tmp/plan78-work/t6/`. The edits cannot reach them, so they
  were not re-run.
- Each of the nine DR prompts holds a phrase of each edit once: "A request that only names a spec" (1), "only that
  track's remaining items park" (2), "latest stage's finding" (3) and "with no spec, a proposed roadmap name" (4).
  None holds `its core stage's` or `Remaining unticked stages, and`.
- The case-repository reads (URL, commit, path and sha256) are the same as those in `control/MANIFEST.txt`. No prompt
  holds `red-baseline`, `plan 78`, the spec's file name or `task-7` (the quarantine).

Each case ran with
`bash specs/red-baseline-new-project-entry/kit/run_reps.sh /tmp/plan78-work/t7/<case>.txt specs/red-baseline-new-project-entry/treatment/<case>-t7 1 5 claude-opus-5-5 1.00`,
one case at a time, into folders with a `-t7` suffix, so earlier folders are untouched. Before each call, the running
total plus the call's worst case ($5.00) stayed under $60. The largest such sum was $25.1399, before the last call.
Each case's replies were read in full from `show_reps.py` over that case's folder alone.

**Result rules (the brief).** A case that met its bar before and misses it now is an owner gate. dr-offer-yes,
dr-tracks and dr-known-progression missed their bar before. The owner ruled to accept and file those misses, so their
new scores are recorded, with no wording round and no action on a miss. The "before" arm of each case is its arm of
record in "All arms side by side": round 2 (`3ca7344`) for the seven Task 3 cases and `a98ff27` for the two Task 4
cases.

### Task 7: dr-offer-scaffold

Additive. Arm `f824492`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.4327.

| Rep | A (bar) | B (bar) | C (bar) | PASS |
|---|---|---|---|---|
| 1 | pass | pass | pass | yes |
| 2 | pass | pass | pass | yes |
| 3 | pass | pass | pass | yes |
| 4 | pass (borderline) | pass | pass | yes |
| 5 | pass | pass | pass | yes |

Clause A: 5 of 5 (before 5 of 5, control 3 of 5). Clause B: 5 of 5 (before 5 of 5, control 5 of 5). Clause C: 5 of 5
(before 5 of 5, control 0 of 5). PASS: 5 of 5 (before 5 of 5). Bar: met.

- A. No rep sets out a stage list. Each says that stages come only after the ranking, for example rep3: "You would
  rank them, and only then would stages be drawn." Rep2 names one stage: "The first stage would then be whatever you
  rank highest". Rep4 passes, borderline. Its ADR question offers an order of work as one option: "Or should I keep
  the Azure-specific work behind that decision, so cloud-independent work can come first?" It calls neither part a
  stage, so the reading for work areas applies.
- B. Every rep makes an absolute statement, for example rep1: "so no outcome works end to end on real data."
- C. Every rep offers staging from an outcome list that the partner ranks, beside a partition, and waits. For example
  rep3: "I won't switch approaches without your answer."
- Edit 1. No rep goes straight to §7. Each gives the gap table, puts the offer in its batched questions and waits.

Running total: $16.0634 of $60.

### Task 7: dr-offer-inputs

Additive. Arm `f824492`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.6697.

| Rep | A (bar) | B (bar) | C (bar) | PASS |
|---|---|---|---|---|
| 1 | pass | pass | pass | yes |
| 2 | pass | pass (borderline) | pass | yes |
| 3 | pass | pass | pass | yes |
| 4 | pass | pass | pass | yes |
| 5 | pass | pass | pass | yes |

Clause A: 5 of 5 (before 5 of 5, control 2 of 5). Clause B: 5 of 5 (before 5 of 5, control 0 of 5). Clause C: 5 of 5
(before 5 of 5, control 0 of 5). PASS: 5 of 5 (before 5 of 5). Bar: met.

- A. No rep names a stage list. Reps 1, 3, 4 and 5 ask whether the spec's rollout order still binds, which sets out
  no stage.
- B. Each rep says that download code is not a working outcome, and that nothing is built or works end to end. For
  example rep5: "By the skill's test, no outcome of this system works end to end on real data, because download code
  doesn't count." Rep2 passes, borderline. Its question is headed "**Nothing built.**", and its body says "Nothing
  turns real data into any R7 target" and "Code that only downloads and converts inputs doesn't count as a working
  outcome." It is scored as round 2 rep5's heading was.
- C. Each rep offers the new-project entry beside a partition and waits, for example rep5: "Which do you want? I
  won't proceed on either until you answer."
- Edit 1. No rep goes straight to §7.

Running total: $16.7331 of $60.

### Task 7: dr-offer-yes

Additive. Arm `f824492`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.6191.

| Rep | A (bar) | B (bar) | C (bar) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | yes |
| 2 | pass | fail (borderline) | fail (borderline) | pass | no |
| 3 | pass | pass | fail (borderline) | pass | no |
| 4 | pass | pass | pass | pass | yes |
| 5 | pass | pass (borderline) | pass (borderline) | pass | yes |

Clause A: 5 of 5 (before 5 of 5, control 5 of 5). Clause B: 4 of 5 (before 3 of 5, control 2 of 5). Clause C: 3 of 5
(before 3 of 5, control 2 of 5). Clause D: 5 of 5 (before 5 of 5, control 0 of 5). PASS: 3 of 5 (before 3 of 5).
Bar: **missed**, as before. It needs 4 of 5. The owner ruled before Task 7 to accept and file this miss, so no action
follows.

- A. Every rep gives O-numbered table rows, one plain line each, from the spec's requirements (labeled-list reading).
- B, rep2, fail (borderline), by Task 3's core-and-later-stages reading. It picks the first outcome and places others
  in later stages before the partner ranks. Quote (B, rep2): "Stage 1 would be the core: O1 on one real quarter plus
  one real daily file, run locally, with the measured cost recorded." The reply also says "every outcome depends on
  the O1 catalog", so its pick follows a dependency that it states.
- C, reps 2 and 3, fail (borderline). Rep2 sets out a core stage and the later stages: "The later stages build out
  from there. Alerts, runbooks, deployment and fault-injection suites go into named later stages, not into stage 1."
  Rep3 calls its Track A outcomes stages and orders them by the spec, as round 2 rep1 did ("The spec names these
  stages in order."). Quote (C, rep3): "The spec's §7 order already names the stages from one quarter to
  reconciliation."
- Reps 1, 4 and 5 give dependency facts and the spec's order, labeled. Rep4 calls the spec's order "steps", not
  stages: "The spec's §4 names these steps in order", as round 1 rep5 did. Rep5 passes B and C, borderline
  (Judgment-call reps, below).
- D. Every rep gives a cost note with a basis, for example rep1: "136 quarters from 1993 Q1 to 2026 Q4, each a
  listing plus one file. That is under 2 minutes of request budget at 3 req/s."
- Edit 4. Every rep names the roadmap from the spec's stem, `specs/sec-filing-index-ingestion-spec-roadmap.md`, and
  no rep asks the partner to confirm or change the name. Rep5: "This is the spec's stem used whole, so no other name
  is needed." No clause scores this.
- Other readings. If the core-and-later-stages text is not read as a stage list or a position, rep2 passes C. It
  passes B too if its pick of O1 for Stage 1 is read as the dependency it states, as dr-tracks' "A's core stage comes
  first whatever the ranking" is. If rep3's sentence is read as the spec's order cited, as round 1 rep5's was, rep3
  passes C. Either change alone gives PASS 4 of 5 and the bar met. Both give 5 of 5. If rep5's "§7 of the spec
  already names the progression from first stage to last" is read as round 2 rep1's sentence was, rep5 fails C, and
  PASS is 2 of 5.

Running total: $17.3522 of $60.

### Task 7: dr-built-guard

Non-regression (guard). Arm `f824492`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.3008.

| Rep | Guard rule | PASS |
|---|---|---|
| 1 | pass | yes |
| 2 | pass | yes |
| 3 | pass | yes |
| 4 | pass | yes |
| 5 | pass | yes |

Reps that pass the whole rule: 5 of 5 (before 5 of 5, control 5 of 5). Bar: met. The guard needs at least 4 of 5.
Every rep gives the gap table and one batch of questions, and says it will partition the remaining gaps. No rep says
that nothing is built or offers outcome-first staging. Reps 1 and 5 name the new path only to decline it, for example
rep1: "So this is a normal partition, not the new-project path."

Running total: $17.6530 of $60.

### Task 7: dr-known-progression

Additive. Arm `f824492`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.8990.

| Rep | B (bar) | A (conformance) | C (conformance) | D (conformance) | E (recorded) | PASS |
|---|---|---|---|---|---|---|
| 1 | pass | pass | fail | pass | pass | no |
| 2 | pass | pass | fail | pass | pass | no |
| 3 | pass | pass | fail | pass | pass | no |
| 4 | pass | pass | fail | pass | pass | no |
| 5 | pass (borderline) | pass | fail | pass | pass | no |

Clause B: 5 of 5 (before 5 of 5, control 4 of 5). Clause A: 5 of 5. Clause C: 0 of 5 (before 0 of 5). Clause D: 5 of
5. Clause E (recorded): 5 of 5. PASS: 0 of 5 (before 0 of 5). Bar: **missed**, as before, through conformance clause
C. The owner ruled before Task 7 to accept and file this miss, so no action follows.

Clause C by quality:

| Quality | Round 2 (before) | Task 7 | Task 7 reps that pass |
|---|---|---|---|
| manifest | 5 of 5 | 5 of 5 | all |
| traceability | 4 of 5 | 5 of 5 | all |
| point-in-time (as-of) | 0 of 5 | 0 of 5 | none (reps 1, 3 and 4 borderline) |

- C. Every rep names a manifest in Stage 4, for example rep4's "a source manifest". Every rep names traceability in a
  later stage, for example rep3's Stage 4 "provenance: each row names its source file and hash." and rep2's Stage 2
  "each traceable to its index row". No rep names point-in-time or as-of awareness. Reps 1, 3 and 4 name versions that
  readers can reach, which is not as-of awareness, as round 2 rep1's "readers can pin" was read. Quote (C, rep3, the
  nearest): "reconciliation of later quarterly changes, with prior catalog versions readable".
- B. No first-stage Exit names a manifest, a per-row provenance record, as-of awareness or a spec section. Rep5
  passes, borderline. Its Exit asks for "a row count per source file", a count and not a manifest, and its
  `Leaves out` sends the "provenance manifest" to Stage 4.
- A, D and E pass in every rep. No rep stops on §3's scan or changes the name: each writes
  `specs/sec-filing-ingestion-roadmap.md`, the name that the partner confirmed.

Running total: $18.5520 of $60.

### Task 7: dr-tracks

Additive. Arm `f824492`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.6228.

| Rep | A (bar) | B (conformance) | C (conformance) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | pass | pass | pass (borderline) | pass | yes |
| 2 | pass | pass (borderline) | pass (borderline) | pass | yes |
| 3 | pass | pass | pass (borderline) | pass | yes |
| 4 | pass | pass | pass (borderline) | pass | yes |
| 5 | pass | pass | pass | pass | yes |

Clause A: 5 of 5 (before 4 of 5, control 0 of 5). Clause B: 5 of 5 (before 5 of 5). Clause C: 5 of 5 (before 3 of 5).
Clause D: 5 of 5 (before 5 of 5). PASS: 5 of 5 (before 2 of 5, control 0 of 5). Bar: **met on the readings applied**
(see Other readings, below). It missed in both rounds of Task 3.

- A. Every rep puts the collection-interval outcome and the budget and staffing outcome in separate tracks and says
  why. For example rep4: "Either answer stands without the other, even though both explain revision scale."
- B. Every rep asks the partner to rank. Rep2 passes, borderline, by the dependency-fact reading: "Tracks B through F
  all consume O1, so Track A's core stage comes first whatever the ranking." Reps 2, 3 and 4 propose an order inside
  the known-progression Track A, for example rep3: "*Known progression*, proposed: total SA → benchmark/wedge-back →
  supersector". Each still asks the partner to rank within each track, so no order is settled.
- C. No rep writes roadmap text or sets out a stage list. Reps 2, 3 and 4 pass, borderline. Each orders outcomes
  inside Track A without calling them stages, as round 2 reps 3 and 4 did, for example rep4: "Known progression:
  total nonfarm first, then supersectors." Rep1 passes, borderline. Its Track A line orders work steps that it does
  not call stages: "Known progression: assemble the vintages, compute revisions by stage, describe them." Its
  qualities line sets out no stage, as round 2 rep2's did: "will go into later stages or Ranked-list items, never into
  a core stage's Exit."
- D. Every rep says that the first run measures the fit cost, for example rep5: "NUTS compute unknown; its core stage
  measures it".
- The cause. No edit changes the tracks rules (§7 step 2 and the tracks bullets of `references/new-project-entry.md`).
  Edit 4 changes items 4 and 5 of the one message, but only for the name. The likely cause of the change from 2 of 5
  to 5 of 5 is the spread from rep to rep on the tracks decision. Five reps cannot tell this apart from an effect of
  the edits.
- Other readings. Round 2 rep5 failed C for the same kind of content with the word "stages": "I'd expect total
  nonfarm first, then stage dispersion, then supersectors with NSA/SA. Tell me if you'd name the stages
  differently." If an order inside a known-progression track counts as a stage list without that word, reps 2, 3
  and 4 fail C (rep2: "panel → stage-wise magnitude → supersectors", rep3: "total SA → benchmark/wedge-back →
  supersector", rep4: "total nonfarm first, then supersectors"). PASS is then 2 of 5. With rep1's ordered work steps
  also failed, PASS is 1 of 5. The bar is missed under both counts. The scores stand on round 2's reading of its reps
  3 and 4, which ordered outcomes inside a track without calling them stages and passed C.

Running total: $19.1748 of $60.

### Task 7: dr-research-depth

Additive. Arm `f824492`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.6987.

| Rep | A (bar) | B (bar) | C (conformance) | D (conformance) | E (conformance) | PASS |
|---|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | pass | yes |
| 2 | pass | pass | pass | pass | pass | yes |
| 3 | pass | pass | pass | pass | pass | yes |
| 4 | pass | pass | pass | pass | pass | yes |
| 5 | pass | pass | pass | pass | pass | yes |

Every clause: 5 of 5 (before 5 of 5, control A 0, B 0). PASS: 5 of 5 (before 5 of 5). Bar: met. Every rep commits
Stage 1 (Track A, O1) and Stage 2 (Track B, O6) and keeps O3 and O2, and O4 and O5, in the two Ranked lists. Each
committed stage's Exit records the measured cost of the real run, for example rep2's Stage 1: "it also records the
measured cost of the real run, meaning the data-assembly time and the wall-clock time of the fit." Each committed
stage's Produces names `specs/ces-revisions-stage-<N>-findings.md`. The later qualities go to the Ranked lists as
items, for example rep4's "Vintage provenance — a manifest of the source, retrieval date and checksum for each
downloaded vintage." No rep stops on §3's scan: each writes `specs/ces-revisions-roadmap.md`.

Running total: $19.8735 of $60.

### Task 7: dr-resume-rerank

Additive. Arm `f824492`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.2664.

| Rep | A (bar) | C (bar) | B (conformance) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | yes |
| 2 | pass | pass | pass | pass | yes |
| 3 | pass | pass | pass | pass | yes |
| 4 | pass | pass | pass | pass | yes |
| 5 | pass | pass | pass | pass | yes |

Clause A: 5 of 5 (before 5 of 5, control 4 of 5). Clause C: 5 of 5 (before 5 of 5, control 5 of 5). Clause B: 5 of 5
(before 5 of 5, control 2 of 5). Clause D: 5 of 5 (before 5 of 5, control 5 of 5). PASS: 5 of 5 (before 5 of 5). Bar:
met.

- A. No rep starts a completion review. Each offers stopping the track as one option of its question. Rep2 uses Edit
  2's wording: "Stopping parks O2–O4 in `specs/deferred_items.md`, and the roadmap stays live."
- C. Each rep ends on one approve-or-amend question. Its default keeps the order O2, O3, O4 and promotes O2 as Stage
  2. Rep4 names promoting O3 first as the alternative, inside the same question: "Approve the default, or amend it (a
  different item, a different order, or stop)?"
- B. Each rep reports the 3.1 m level with the steep rise above it, and the 22-minute, 1.8 GB fit.
- D. No rep writes a stage entry. Rep5 describes the promoted stage inside its proposal, by Edit 3's rule: "That
  stage would name its own findings file, `specs/lock-closures-stage-2-findings.md`".

Running total: $20.1399 of $60.

### Task 7: dr-resume-legacy

Non-regression (guard). Arm `f824492`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.2497.

| Rep | Guard rule | PASS |
|---|---|---|
| 1 | pass | yes |
| 2 | pass | yes |
| 3 | pass | yes |
| 4 | pass | yes |
| 5 | pass | yes |

Reps that pass the whole rule: 5 of 5 (before 5 of 5, control 5 of 5). Bar: met. The guard needs at least 4 of 5.
Every rep reconciles with no amendment (plan 5's Handoff reads `None`), says that all three stages are ticked and that
no Ranked list waits, goes to the completion review (§6) and lists the reads of the audit over R1 to R6. No rep asks
a re-ranking question. Reps 2, 4 and 5 end on a go-ahead question (rep4: "Shall I run the audit?"), as in Task 4.
That is not a re-ranking question.

Running total: $20.3896 of $60.

### Task 7 summary

| Case | Bar | Control | Before (arm of record) | Task 7 (`f824492`) | Result |
|---|---|---|---|---|---|
| dr-offer-scaffold | additive | RED, 5 of 5 | 5 of 5 pass (round 2, `3ca7344`) | 5 of 5 pass | met, as before |
| dr-offer-inputs | additive | RED, 5 of 5 | 5 of 5 pass (round 2) | 5 of 5 pass | met, as before |
| dr-offer-yes | additive | RED, 4 of 5 | 3 of 5 pass (round 2) | 3 of 5 pass | **missed**, as before (4 of 5 by either other reading) |
| dr-built-guard | guard | 5 of 5 | 5 of 5 (round 2) | 5 of 5 | met, as before (needs 4 of 5) |
| dr-known-progression | additive | RED, 1 of 5 | 0 of 5 pass (round 2) | 0 of 5 pass | **missed**, as before (C: point-in-time 0 of 5) |
| dr-tracks | additive | RED, 5 of 5 | 2 of 5 pass (round 2) | 5 of 5 pass | **met** on the readings applied (missed before; 2 of 5 or fewer by the other reading) |
| dr-research-depth | additive | RED, 5 of 5 | 5 of 5 pass (round 2) | 5 of 5 pass | met, as before |
| dr-resume-rerank | additive | RED, 1 of 5 | 5 of 5 pass (`a98ff27`) | 5 of 5 pass | met, as before |
| dr-resume-legacy | guard | 5 of 5 | 5 of 5 (`a98ff27`) | 5 of 5 | met, as before (needs 4 of 5) |

No case that met its bar before misses it now, so Task 7 has no owner gate. Seven of the nine cases meet their bar.
dr-offer-yes and dr-known-progression miss it as before, and the owner's earlier ruling covers both. dr-tracks now
meets it, on the readings applied (dr-tracks, Other readings). No rep was VOID.

**Edit 1 and the two offer cases.** No rep of dr-offer-scaffold or dr-offer-inputs goes straight to §7 without the
offer. All ten put the offer in their batched questions and wait. This is weak evidence for Edit 1. Both fixtures hand
the agent a finished gap analysis, so they do not test the entry decision itself (the Task 3 review finding).

**Judgment-call reps (Task 7).** These rows extend the Judgment-call lists in the Control section and in Tasks 3 to
6. Each rep was scored on a close reading. Two groups of rows rest on readings that, ruled the other way, would change
a bar: the dr-offer-yes rows for reps 2 and 3, and the dr-tracks row for reps 2, 3 and 4 (each case's Other
readings, above). No other row changes a bar.

| Case, rep, clause | Score | Deciding quote |
|---|---|---|
| dr-offer-scaffold rep4, A | pass, borderline (an order of work areas inside one option of a question, not called stages) | "Or should I keep the Azure-specific work behind that decision, so cloud-independent work can come first?" If it failed, PASS would be 4 of 5 and the bar still met. |
| dr-offer-scaffold rep2, A | pass (one stage) | "The first stage would then be whatever you rank highest, run on real SEC data at the smallest usable standard." |
| dr-offer-inputs rep2, B | pass, borderline (absolute heading, acquisition not counted) | "**Nothing built.**", then "Nothing turns real data into any R7 target" and "Code that only downloads and converts inputs doesn't count as a working outcome." If it failed, PASS would be 4 of 5 and the bar still met. |
| dr-offer-yes rep2, B | fail, borderline (core and later stages; the pick of O1 follows a dependency that the reply states) | "Stage 1 would be the core: O1 on one real quarter plus one real daily file, run locally, with the measured cost recorded." |
| dr-offer-yes rep2, C | fail, borderline (core and later stages) | "Alerts, runbooks, deployment and fault-injection suites go into named later stages, not into stage 1." |
| dr-offer-yes rep3, C | fail, borderline (the spec's stages in order, as round 2 rep1) | "The spec's §7 order already names the stages from one quarter to reconciliation." |
| dr-offer-yes rep4, C | pass (the spec's steps, not called stages, as round 1 rep5) | "The spec's §4 names these steps in order, from parse and publish through replay, daily, throttling and reconciliation." |
| dr-offer-yes rep5, B | pass, borderline (what the first run needs, not a position of an outcome) | "What can come later is the cross-job lease." |
| dr-offer-yes rep5, C | pass, borderline (the definition of the track's kind, no stage set out) | "§7 of the spec already names the progression from first stage to last." |
| dr-known-progression rep5, B | pass, borderline (a per-file count, not a manifest; the manifest is named as left out) | Exit: "with a row count per source file". Leaves out: "provenance manifest, raw-snapshot replay, versioned publication and golden-fixture validation suite → Stage 4" |
| dr-known-progression reps 1, 3 and 4, C (point-in-time) | not passed, borderline (versions, not as-of reads, as round 2 rep1) | rep1 "per-quarter generations, an active-pointer reader contract", rep3 "with prior catalog versions readable", rep4 "readers see only complete quarter versions and can name the version they read" |
| dr-known-progression rep2, C (traceability) | passed (as round 1 reps 3 and 5) | "one quarter's submissions on disk, each traceable to its index row" |
| dr-tracks rep1, C | pass, borderline (work steps not called stages; no stage set out for the qualities) | "Known progression: assemble the vintages, compute revisions by stage, describe them." and "will go into later stages or Ranked-list items, never into a core stage's Exit." If it failed, PASS would be 4 of 5 and the bar still met. |
| dr-tracks rep2, B and C | pass, borderline (dependency fact, one stage) | "Tracks B through F all consume O1, so Track A's core stage comes first whatever the ranking." |
| dr-tracks reps 2, 3 and 4, C | pass, borderline (outcomes ordered inside a known-progression track, not called stages, as round 2 reps 3 and 4) | rep2 "panel → stage-wise magnitude → supersectors", rep3 "*Known progression*, proposed: total SA → benchmark/wedge-back → supersector", rep4 "Known progression: total nonfarm first, then supersectors." Round 2 rep5 failed C for the same kind of content with the word "stages". Ruled the other way, PASS is 2 of 5 (1 of 5 with rep1) and the bar is missed. |
| dr-resume-rerank rep4, C | pass (one question with a default and its alternatives) | "Approve the default, or amend it (a different item, a different order, or stop)?" |

**Task 7 spend.** `uv run python specs/red-baseline-new-project-entry/kit/show_reps.py` over the nine `-t7` folders
ran once after the last rep. It shows 45 reps, none VOID, and prints `total cost $4.76`. No rep file is empty or
unreadable, so none counts at its cap. There was no VOID rerun. The nine cases cost $0.4327, $0.6697, $0.6191,
$0.3008, $0.8990, $0.6228, $0.6987, $0.2664 and $0.2497, so Task 7 cost $4.7589. Running total: $20.3896 of $60.
Control arms: $5.5029 of $30, unchanged.

## All arms side by side (after the Task 7 fixes)

One row per case. Every figure is taken from this record's own tables. Each count is the number of the 5 scored reps
that pass the clause. The control columns give the control arm at `BASE` (`1844bd8`). The treatment columns give each
case's arm of record. The nine derive-roadmap cases use the Task 7 arm (`f824492`). The other six rows are copied
from the earlier table, "All arms side by side", which stays as history: the two trigger cases use round 1
(`48d9847`), the two dcm cases use `abc1ecb` and the two bs cases use `1f64a61`. Their prompts at `f824492` are
byte-identical to those arms. Only bar clauses are counted in the clause columns. A conformance clause can still
decide the bar result, and the Bar result column says so where it does. A guard case has no bar clause, so its
columns give the reps that pass the whole rule.

| Case | Kind | Control, bar clauses | Treatment, bar clauses | Treatment PASS | Bar result | Clean control |
|---|---|---|---|---|---|---|
| trigger-stages | additive | A 0 | A 5 | 5 of 5 | met | no (RED, 5 of 5) |
| trigger-decoy | guard | 5 of 5 pass | 5 of 5 pass | 5 of 5 | met (needs 4 of 5) | n/a |
| dr-offer-scaffold | additive | A 3, B 5, C 0 | A 5, B 5, C 5 | 5 of 5 | met (A rep4 borderline). In Task 3 it met only in round 2: round 1 (`48d9847`) missed (PASS 2 of 5) | no (RED, 5 of 5) |
| dr-offer-inputs | additive | A 2, B 0, C 0 | A 5, B 5, C 5 | 5 of 5 | met (B rep2 borderline). Met in every arm | no (RED, 5 of 5) |
| dr-offer-yes | additive | A 5 (by the labeled-list reading; 0 on form alone), B 2, C 2 | A 5, B 4, C 3 | 3 of 5 | **missed**: PASS 3 of 5, and 4 of 5 by either other reading (Task 7: dr-offer-yes). Round 2 (`3ca7344`) also 3 of 5. Owner ruling: accept and file | no (RED, 4 of 5) |
| dr-built-guard | guard | 5 of 5 pass | 5 of 5 pass | 5 of 5 | met (needs 4 of 5) | n/a |
| dr-known-progression | additive | B 4 (by the by-reference reading; B 5 by the other reading) | B 5 | 0 of 5 | **missed** through conformance clause C (point-in-time awareness 0 of 5, though manifest and traceability are 5 of 5), although bar clause B is 5 of 5. Owner ruling: accept and file | no by the by-reference reading (RED, 1 of 5); yes by the other reading of B (B 5 of 5) |
| dr-tracks | additive | A 0 | A 5 | 5 of 5 | met on the readings applied. PASS is 2 of 5 or fewer, and the bar is missed, if an order inside Track A counts as a stage list without the word "stages" (Task 7: dr-tracks, Other readings). Both Task 3 rounds missed (PASS 2 of 5) | no (RED, 5 of 5) |
| dr-research-depth | additive | A 0, B 0 | A 5, B 5 | 5 of 5 | met. Met in every arm | no (RED, 5 of 5) |
| dr-resume-rerank | additive | A 4, C 5 | A 5, C 5 | 5 of 5 | met against a thin control: the control failed a bar clause in 1 of 5 reps (rep4, A) | no (thin: RED in 1 of 5) |
| dr-resume-legacy | guard | 5 of 5 pass | 5 of 5 pass | 5 of 5 | met (needs 4 of 5) | n/a |
| dcm-describe-route | additive | A 1 (0 before fix round 1), B 5, C 0 | A 5, B 5, C 5 | 5 of 5 | met on the readings applied. Under the other readings (Task 5, Other readings) A is 3 of 5 or fewer, and the bar is missed | no (RED, 5 of 5) |
| dcm-synth-route | additive | A 2, B 5, C 0 | A 5, B 5, C 5 | 5 of 5 | met on the readings applied. A is 3 of 5, and the bar is missed, if reps 1 and 5 both fail A (Task 5, Other readings) | no (RED, 5 of 5) |
| bs-route | additive | A 0, B 4, C 5 | A 4, B 5, C 5 | 4 of 5 | met on the readings applied. A is 3 of 5, PASS is 3 of 5 and the bar is missed, if rep4 fails A (Task 6, Other readings) | no (RED, 5 of 5) |
| bs-guard | guard | 4 of 5 pass | 4 of 5 pass | 4 of 5 | met (needs 3 of 5) | n/a |

**Counts.** 13 of the 15 cases meet their bar and 2 miss it: dr-offer-yes and dr-known-progression. Both are Task 3
derive-roadmap cases that missed after the one wording round and miss again at Task 7. The owner ruled to accept and
file both misses. dr-tracks, the third earlier miss, now meets its bar. Of the 13 that meet their bar, four meet it
only on the readings applied (dcm-describe-route, dcm-synth-route, bs-route and dr-tracks), and one meets it against
a thin control (dr-resume-rerank). dr-offer-scaffold met its bar in Task 3 only after the wording round. The four guard cases
(trigger-decoy, dr-built-guard, dr-resume-legacy, bs-guard) all meet their bar and have no clean-control flag.

**Clean controls.** Unchanged. No additive case has a clean control under the readings applied. dr-known-progression
would have one under the other reading of its clause B. Two additive controls are thin, with a bar clause that fails
in 1 of 5 reps: dr-resume-rerank (rep4, clause A) and dr-known-progression (rep5, clause B, by the by-reference
reading).

**For the owner.** Edits 1 and 2 address the two review findings parked at the Task 3 and Task 4 gates (entry item 2,
and "stop the track"). The micro-tests reach Edit 1 only weakly, because the offer fixtures hand over a finished gap
analysis. They do not reach the stop-the-track answer, because no rep receives a "stop" answer. Edits 3 and 4 show in
the replies but no clause scores them: dr-resume-rerank rep5 names the promoted stage's own findings file, and every
dr-offer-yes rep names the roadmap from the spec's stem without asking for a name. The two remaining misses stay with
the owner, with the other-reading counts of dr-offer-yes and dr-tracks (Task 7), dcm-describe-route and
dcm-synth-route (Task 5) and bs-route (Task 6). dr-tracks moved from a miss to met with no change to the text it
tests, so its "met" is probably spread between reps. The brief's check 4 printed 2, not 4 (Treatment: Task 7, Checks after the edits).

**Spend total.** Spend by task: Task 1 $0.2962 (isolation probe $0.0141 and cost pilot $0.2821), Task 2 $5.5029
(control arms), Task 3 $8.4719, Task 4 $0.5190, Task 5 $0.5031, Task 6 $0.3376 and Task 7 $4.7589. These sum to
**$20.3896 of $60**. The control arms alone cost $5.5029 of $30, unchanged: treatment reps count toward the $60 only.
No rep was VOID and there was no VOID rerun in any task, and no rep file was empty or unreadable. The Spend table, the
"Running total after Task 7" paragraph and this total agree.

## Treatment: Task 7 fix round 1

The Task 7 reviewer and a Codex review of the Task 7 commits found four defects in the text that the Task 7 brief
gave. The controller sent the exact fix text. The four edits were committed as `d3fc772` (`fix(derive-roadmap): fix
four gaps in the final-review routing edits`). The fix round re-runs the four cases that read the edited passages.
Each rep is scored by its case's committed rule and by every reading in the Control section. No rule and no reading
changed.

| Edit | Defect | Passage | Change |
|---|---|---|---|
| 5 | A stopped track's items got no dated section heading, so they did not age as the Parking paragraph promises. A whole-roadmap park appended only the unticked stages, so Ranked-list items went to `specs/completed/` and never reached `specs/deferred_items.md`. | `SKILL.md` §5, the Parking paragraph | A whole-roadmap park also appends the items of every Ranked list. A stopped track's items go under a dated `## <roadmap-name> — <YYYY-MM-DD>` section. |
| 6 | Edit 4(a) dropped the never-overwrite check when there is a spec. | `references/roadmap-format.md`, the name rule | After §3's scan, the check that `specs/<name>-roadmap.md` does not exist runs with or without a spec. |
| 7 | The re-rank reports the latest stage's measured cost, but only a core stage was told to record one. | `references/roadmap-format.md`, the `Exit` line of the stage-entry template | Any stage of a research track adds the measured cost of its real run. |
| 8 | As Edit 7. | `references/new-project-entry.md`, the Research bullet | A promoted stage names the measured cost of its real run in `Exit`, so the next re-rank reads what that stage found and cost. |

**Checks after the edits.** The four pins each print `1`. The one-definition check prints one line,
`2 **Nothing built** means that no outcome …`. The derive-roadmap body measures 15,506 characters.
`/usr/bin/grep -c "any stage of a research track" skills/derive-roadmap/references/roadmap-format.md` prints 2 (the
`Produces` line and the `Exit` line). `/usr/bin/grep -c "Then, with or without a spec"` on the same file prints 1. The
commit lints passed.

**Build.** The prompts of all 15 cases were built with
`CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py d3fc772 /tmp/plan78-work/t7b`.
Its `MANIFEST.txt` is copied to `treatment/t7b-MANIFEST.txt`. Checks on the build before any rep:

- The six cases that read no derive-roadmap text have prompts that `cmp` finds byte-identical to their arms of
  record (`t3-r1/`, `t5/` and `t6/`, as in Task 7).
- Each of the four re-run prompts holds a phrase of each edit once: "the items of every Ranked list append" (5),
  "Then, with or without a spec" (6), "any stage of a research track, adds the measured cost" (7) and "and the
  measured cost of its real run in `Exit`" (8). None holds the removed "With no spec, check before writing".
- The case-repository reads are the same as those in `control/MANIFEST.txt`. No prompt holds `red-baseline`,
  `plan 78`, the spec's file name or `task-7` (the quarantine).

Each case ran with
`bash specs/red-baseline-new-project-entry/kit/run_reps.sh /tmp/plan78-work/t7b/<case>.txt specs/red-baseline-new-project-entry/treatment/<case>-t7b 1 5 claude-opus-5-5 1.00`,
one case at a time, into folders with a `-t7b` suffix. Before each call, the running total plus the call's worst
case ($5.00) stayed under $60. The largest such sum was $27.2461, before the last call. Each case's replies were read
in full from `show_reps.py` over that case's folder alone.

**Cases not re-run.** Their prompts carry the edited text, but their decisions come before any of it acts:

- dr-offer-scaffold: decides at §1 (the gap table and the offer), and writes, parks and names no roadmap.
- dr-offer-inputs: decides at §1 (the gap table and the offer), and writes, parks and names no roadmap.
- dr-offer-yes: decides in the one message, before any roadmap file, so neither the check before writing nor a stage
  entry's `Exit` comes into play.
- dr-built-guard: decides at §1 for a partly built system and goes to the existing partition, with no new-project
  roadmap.
- dr-tracks: decides in the one message (tracks and the ranking request), and writes no roadmap file and parks
  nothing.

**Result rules.** As in Task 7: a case that met its bar before and misses it now is an owner gate.
dr-known-progression's miss is recorded, with no action. The "before" arm of each case is its Task 7 arm
(`f824492`).

### Fix round 1: dr-known-progression

Additive. Arm `d3fc772`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.9199.

| Rep | B (bar) | A (conformance) | C (conformance) | D (conformance) | E (recorded) | PASS |
|---|---|---|---|---|---|---|
| 1 | pass | pass | fail | pass | pass | no |
| 2 | pass (borderline) | pass | fail | pass | pass | no |
| 3 | pass | pass | fail | pass | pass | no |
| 4 | pass | pass | fail | pass | pass | no |
| 5 | pass | pass | fail | pass | pass | no |

Clause B: 5 of 5 (before 5 of 5, control 4 of 5). Clause A: 5 of 5. Clause C: 0 of 5 (before 0 of 5). Clause D: 5 of
5. Clause E (recorded): 5 of 5. PASS: 0 of 5 (before 0 of 5). Bar: **missed**, as before, through conformance clause
C. The owner ruled to accept and file this miss, so no action follows.

Clause C by quality:

| Quality | Task 7 (before) | Fix round 1 | Fix round 1 reps that pass |
|---|---|---|---|
| manifest | 5 of 5 | 5 of 5 | all |
| traceability | 5 of 5 | 4 of 5 | rep1, rep3, rep4, rep5 |
| point-in-time (as-of) | 0 of 5 | 0 of 5 | none |

- C. Every rep names a manifest in a later stage, for example rep3's "Stage 4: Download manifest and replay". Four
  reps name traceability, for example rep1's Stage 4: "Every row traces to a source file and its hash." Rep2's later
  stages name retained bytes and manifests but no trace from a row to its source. No rep names point-in-time or as-of
  awareness. Quote (C, rep1, the nearest): "Readers of the published table see either the previous version or the
  new one, never a mix."
- B. No first-stage Exit names a manifest, a per-row provenance record, as-of awareness or a spec section. Rep2
  passes, borderline. Its Exit asks for "its row count checked against the source files", a count check and not a
  manifest, as Task 7 rep5's "a row count per source file" was read.
- A. Every rep commits the index work, then the submissions, then 10-K and 8-K handling, in that order. Reps 2 and 5
  put a second index stage before the submissions, which keeps the order.
- D and E pass in every rep. Each rep writes `specs/sec-filing-ingestion-roadmap.md`, the confirmed name.

Running total: $21.3095 of $60.

### Fix round 1: dr-research-depth

Additive. Arm `d3fc772`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.6747.

| Rep | A (bar) | B (bar) | C (conformance) | D (conformance) | E (conformance) | PASS |
|---|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | pass | yes |
| 2 | pass | pass | pass | pass | pass | yes |
| 3 | pass | pass | pass | pass | pass | yes |
| 4 | pass | pass | pass | pass | pass | yes |
| 5 | pass | pass (borderline) | pass | pass | pass | yes |

Every clause: 5 of 5 (before 5 of 5). PASS: 5 of 5 (before 5 of 5). Bar: met. Every rep commits Stage 1 (Track A,
O1) and Stage 2 (Track B, O6) and keeps O3 and O2, and O4 and O5, in the two Ranked lists. Each committed stage's
Produces names `specs/ces-revisions-stage-<N>-findings.md`, and each Exit records the cost of the real run. Rep5
passes B, borderline: its Exits record the run's times without the word "measured", for example Stage 1's "recorded in
the findings file with wall-clock time for data assembly and for the fit". Rep1 also writes Edit 8's rule into its
roadmap: "A stage promoted from a Ranked list names its own findings file, `specs/ces-revisions-stage-<N>-findings.md`,
in `Produces`, and the measured cost of its real run in `Exit`."

Running total: $21.9842 of $60.

### Fix round 1: dr-resume-rerank

Additive. Arm `d3fc772`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.2619.

| Rep | A (bar) | C (bar) | B (conformance) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | yes |
| 2 | pass | pass | pass | pass | yes |
| 3 | pass | pass | pass | pass | yes |
| 4 | pass | pass (borderline) | pass | pass | yes |
| 5 | pass | pass | pass | pass | yes |

Clause A: 5 of 5 (before 5 of 5, control 4 of 5). Clause C: 5 of 5 (before 5 of 5, control 5 of 5). Clause B: 5 of 5
(before 5 of 5, control 2 of 5). Clause D: 5 of 5 (before 5 of 5, control 5 of 5). PASS: 5 of 5 (before 5 of 5). Bar:
met.

- A. No rep starts a completion review. Each offers stopping the track as one option of its question, for example
  rep3: "Stopping the track instead would park all three items in `specs/deferred_items.md`, and the roadmap would
  stay live."
- C. Each rep ends on one approve-or-amend question that promotes O2 as Stage 2. Reps 1, 2, 4 and 5 keep the order
  O2, O3, O4. Rep3 proposes O2, O4, O3. Rep4 passes, borderline. Its question gives the default and then its
  alternatives in a second sentence: "Should we promote O2 as the next stage, keep O3 then O4 in the list in that
  order, and change O3's cost note …? Or would you rather re-order the list, promote a different item, or stop the
  track …?"
- B. Each rep reports the 3.1 m level with the steep rise above it, and the 22-minute, 1.8 GB fit.
- D. No rep writes a stage entry. Reps 1 and 2 say the promoted stage's Exit will carry its measured cost (Edits 7
  and 8), for example rep1: "Its Exit would name its findings file and the measured cost of its real run."

Running total: $22.2461 of $60.

### Fix round 1: dr-resume-legacy

Non-regression (guard). Arm `d3fc772`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.2594.

| Rep | Guard rule | PASS |
|---|---|---|
| 1 | pass | yes |
| 2 | pass | yes |
| 3 | pass | yes |
| 4 | pass | yes |
| 5 | pass | yes |

Reps that pass the whole rule: 5 of 5 (before 5 of 5, control 5 of 5). Bar: met. The guard needs at least 4 of 5.
Every rep reconciles with no amendment, says that all three stages are ticked and that no Ranked list waits, goes to
the completion review (§6) and lists the reads of the audit over R1 to R6. No rep asks a re-ranking question. Reps 1,
3 and 5 end on "Shall I run the audit?", a go-ahead question.

Running total: $22.5055 of $60.

### Fix round 1 summary

| Case | Bar | Control | Task 7 (`f824492`) | Fix round 1 (`d3fc772`) | Result |
|---|---|---|---|---|---|
| dr-known-progression | additive | RED, 1 of 5 | 0 of 5 pass | 0 of 5 pass | **missed**, as before (C: point-in-time 0 of 5) |
| dr-research-depth | additive | RED, 5 of 5 | 5 of 5 pass | 5 of 5 pass | met, as before |
| dr-resume-rerank | additive | RED, 1 of 5 | 5 of 5 pass | 5 of 5 pass | met, as before |
| dr-resume-legacy | guard | 5 of 5 | 5 of 5 | 5 of 5 | met, as before (needs 4 of 5) |

No case that met its bar before misses it now, so the fix round has no owner gate. Three of the four cases meet their
bar. dr-known-progression misses as before, and the owner's earlier ruling covers it. No rep was VOID.

**Judgment-call reps (Task 7 fix round 1).** These rows extend the earlier Judgment-call lists. None changes a bar.

| Case, rep, clause | Score | Deciding quote |
|---|---|---|
| dr-known-progression rep2, B | pass, borderline (a count check, not a manifest, as Task 7 rep5) | "its row count checked against the source files" |
| dr-known-progression rep2, C (traceability) | not passed (retained bytes and manifests, no trace from a row to its source) | "Per-file checkpoints, retained raw source bytes, manifests and versioned publication that later stages may assume" |
| dr-research-depth rep5, B | pass, borderline (the run's times recorded, without the word "measured") | "recorded in the findings file with wall-clock time for data assembly and for the fit" |
| dr-resume-rerank rep3, C | pass (a proposed re-rank as the default, then one question) | "**Do you approve this re-rank with O2 promoted to Stage 2, or would you change the order, promote a different item, or stop the track?**" |
| dr-resume-rerank rep4, C | pass, borderline (the default and its alternatives in two sentences of one question) | "Or would you rather re-order the list, promote a different item, or stop the track" |

**Fix round 1 spend.** `uv run python specs/red-baseline-new-project-entry/kit/show_reps.py` over the four `-t7b`
folders ran once after the last rep. It shows 20 reps, none VOID, and prints `total cost $2.12`. No rep file is empty
or unreadable, so none counts at its cap. There was no VOID rerun. The four cases cost $0.9199, $0.6747, $0.2619 and
$0.2594, so the fix round cost $2.1159. Running total: $22.5055 of $60. Control arms: $5.5029 of $30, unchanged.

**Untested by micro-tests.** No case exercises these paths, so the owner should know that the edits on them are
reviewed but not micro-tested:

- A "stop the track" answer (Edits 2 and 5): no rep receives that answer, so no rep writes the dated section.
- A whole-roadmap park (Edit 5): no rep receives a park answer, so no rep appends stages and Ranked-list items.
- A name collision with a spec (Edits 4 and 6): no fixture has a headerless `specs/<stem>-roadmap.md`, or a roadmap
  from another spec, at the name a spec gives.
- A second re-rank round (Edits 3, 7 and 8): dr-resume-rerank has only its core stage ticked, so the most recently
  ticked stage is always the core.

## All arms side by side (after the Task 7 fix round 1)

One row per case. Every figure is taken from this record's own tables. Each count is the number of the 5 scored reps
that pass the clause. The control columns give the control arm at `BASE` (`1844bd8`). The treatment columns give each
case's arm of record. The four re-run cases use the fix round 1 arm (`d3fc772`). The five other derive-roadmap cases
keep the Task 7 arm (`f824492`). The six other rows are copied from "All arms side by side (after the Task 7 fixes)":
the two trigger cases use round 1 (`48d9847`), the two dcm cases use `abc1ecb` and the two bs cases use `1f64a61`.
Their prompts at `d3fc772` are byte-identical to those arms. The two earlier side-by-side tables stay as history.
Only bar clauses are counted in the clause columns. A conformance clause can still decide the bar result, and the
Bar result column says so where it does. A guard case has no bar clause, so its columns give the reps that pass the
whole rule.

| Case | Kind | Control, bar clauses | Treatment, bar clauses | Treatment PASS | Bar result | Clean control |
|---|---|---|---|---|---|---|
| trigger-stages | additive | A 0 | A 5 | 5 of 5 | met | no (RED, 5 of 5) |
| trigger-decoy | guard | 5 of 5 pass | 5 of 5 pass | 5 of 5 | met (needs 4 of 5) | n/a |
| dr-offer-scaffold | additive | A 3, B 5, C 0 | A 5, B 5, C 5 | 5 of 5 | met (Task 7 arm; A rep4 borderline). In Task 3 it met only in round 2: round 1 (`48d9847`) missed (PASS 2 of 5) | no (RED, 5 of 5) |
| dr-offer-inputs | additive | A 2, B 0, C 0 | A 5, B 5, C 5 | 5 of 5 | met (Task 7 arm; B rep2 borderline). Met in every arm | no (RED, 5 of 5) |
| dr-offer-yes | additive | A 5 (by the labeled-list reading; 0 on form alone), B 2, C 2 | A 5, B 4, C 3 | 3 of 5 | **missed** (Task 7 arm): PASS 3 of 5, and 4 of 5 by either other reading (Task 7: dr-offer-yes). Round 2 (`3ca7344`) also 3 of 5. Owner ruling: accept and file | no (RED, 4 of 5) |
| dr-built-guard | guard | 5 of 5 pass | 5 of 5 pass | 5 of 5 | met (Task 7 arm; needs 4 of 5) | n/a |
| dr-known-progression | additive | B 4 (by the by-reference reading; B 5 by the other reading) | B 5 | 0 of 5 | **missed** (fix round 1 arm) through conformance clause C (point-in-time awareness 0 of 5, though manifest is 5 of 5 and traceability 4 of 5), although bar clause B is 5 of 5. Owner ruling: accept and file | no by the by-reference reading (RED, 1 of 5); yes by the other reading of B (B 5 of 5) |
| dr-tracks | additive | A 0 | A 5 | 5 of 5 | met on the readings applied (Task 7 arm). PASS is 2 of 5 or fewer, and the bar is missed, if an order inside Track A counts as a stage list without the word "stages" (Task 7: dr-tracks, Other readings). Both Task 3 rounds missed (PASS 2 of 5) | no (RED, 5 of 5) |
| dr-research-depth | additive | A 0, B 0 | A 5, B 5 | 5 of 5 | met (fix round 1 arm). Met in every arm | no (RED, 5 of 5) |
| dr-resume-rerank | additive | A 4, C 5 | A 5, C 5 | 5 of 5 | met (fix round 1 arm) against a thin control: the control failed a bar clause in 1 of 5 reps (rep4, A) | no (thin: RED in 1 of 5) |
| dr-resume-legacy | guard | 5 of 5 pass | 5 of 5 pass | 5 of 5 | met (fix round 1 arm; needs 4 of 5) | n/a |
| dcm-describe-route | additive | A 1 (0 before fix round 1), B 5, C 0 | A 5, B 5, C 5 | 5 of 5 | met on the readings applied. Under the other readings (Task 5, Other readings) A is 3 of 5 or fewer, and the bar is missed | no (RED, 5 of 5) |
| dcm-synth-route | additive | A 2, B 5, C 0 | A 5, B 5, C 5 | 5 of 5 | met on the readings applied. A is 3 of 5, and the bar is missed, if reps 1 and 5 both fail A (Task 5, Other readings) | no (RED, 5 of 5) |
| bs-route | additive | A 0, B 4, C 5 | A 4, B 5, C 5 | 4 of 5 | met on the readings applied. A is 3 of 5, PASS is 3 of 5 and the bar is missed, if rep4 fails A (Task 6, Other readings) | no (RED, 5 of 5) |
| bs-guard | guard | 4 of 5 pass | 4 of 5 pass | 4 of 5 | met (needs 3 of 5) | n/a |

(The dcm-describe-route row's "fix round 1" is the earlier controller ruling on a scoring reading, in the Control
section's "Readings applied". It is not this fix round.)

**Counts.** Unchanged from the table after Task 7. 13 of the 15 cases meet their bar and 2 miss it: dr-offer-yes and
dr-known-progression. The owner ruled to accept and file both misses. Of the 13 that meet their bar, four meet it only
on the readings applied (dcm-describe-route, dcm-synth-route, bs-route and dr-tracks), and one meets it against a thin
control (dr-resume-rerank). The four guard cases all meet their bar.

**Clean controls.** Unchanged: see "All arms side by side (after the Task 7 fixes)".

**For the owner.** The fix round closes the four defects that the Task 7 review and the Codex review found, with no
regression in the four cases that read the edited passages. The paths in "Untested by micro-tests", above, are
reviewed but not micro-tested.

**Spend total.** Spend by task: Task 1 $0.2962 (isolation probe $0.0141 and cost pilot $0.2821), Task 2 $5.5029
(control arms), Task 3 $8.4719, Task 4 $0.5190, Task 5 $0.5031, Task 6 $0.3376, Task 7 $4.7589 and Task 7 fix round 1
$2.1159. These sum to **$22.5055 of $60**. The control arms alone cost $5.5029 of $30, unchanged: treatment reps count
toward the $60 only. No rep was VOID and there was no VOID rerun in any task, and no rep file was empty or
unreadable. The Spend table, the "Running total after Task 7 fix round 1" paragraph and this total agree.

## Plan 79: base, cases and leak check

Plan 79 (`specs/plans/79-derive-roadmap-resume-and-route-tests.md`) closes two resume gaps and two wording gaps in
derive-roadmap. It also gives the four routes that plan 78 added their first micro-tests, and it re-runs two older
cases. Task 1 adds seven cases to plan 78's kit and runs their leak check. It runs no rep and spends $0.00.

The quarantine of plan 78 holds for plan 79. This section, the plan and the cases name the pass rules and the expected
behavior. Keep them out of every prompt.

### Plan 79: base

`BASE79` is the commit whose texts the resume-gap controls read. It is the execution branch's start commit.

- Short sha: `5beacf5`.
- Full sha: `5beacf5e70a3516a5b3dc820ef6ecbc17cbb4769`.
- Branch: `claude/subagent-vs-inline-tests-91a494`. Its start is the tip of `main`, the merge of PR #146 that brought
  plan 79 in.

The plan took its line anchors at `a849bd2`. The drift check is
`git diff --stat a849bd2 5beacf5 -- skills/derive-roadmap specs/red-baseline-new-project-entry`. It printed nothing.
No skill file and no file in the record's folder changed, so every anchor holds. No deviation note is needed.

### Plan 79: cases

The seven new cases are at the end of `CASES` in `specs/red-baseline-new-project-entry/kit/cases.py`. Each is
additive, reads the texts `DR` and has the 1.00 USD cap. The 15 cases of plan 78 are unchanged: a script compared each
with its copy at the base commit and found them equal. The seven pass rules were compared with the plan's text by
script. Six are equal. The seventh, `DR_KNOWN_PROGRESSION_PASS_79`, equals `DR_KNOWN_PROGRESSION_PASS` with its clause C
replaced and no other line changed.

| Case | Spec ref | Route or gap that it checks | Arm that Task 2 runs as control |
|---|---|---|---|
| dr-stop-track | plan 78 D6 (the owner may stop a research track at the re-rank question), §5 track stop | one research track stops while another track still has an unticked stage | texts at `1844bd8` |
| dr-park-ranked | §5 Parking, roadmap-format Ranked list | a whole-roadmap park also parks the Ranked-list items | texts at `1844bd8` |
| dr-name-collision | roadmap-format New-project roadmaps, name rule | the spec's stem names a roadmap file that exists and has another source | texts at `1844bd8` |
| dr-rerank-second | §5 research track, most recently ticked stage | a second re-rank reports the promoted stage's findings | texts at `1844bd8` |
| dr-resume-marker | §5 resume gap 1, D3 (plan 79 decision 3) | a resume must not apply a cited Handoff bullet again | texts at `BASE79` |
| dr-resume-blocked | §5 resume gap 2, D4 (plan 79 decision 4) | a resume asks when no unticked stage has its Consumes met | texts at `BASE79` |
| dr-known-progression-79 | V2, R7-R9, plan 79 D1 | dr-known-progression under a clause C that drops point-in-time awareness | none: Task 4 runs it as treatment only |

The standard task line of every case but the last is:

> It is your turn. You have no tools in this turn, so write any tool call as text. Write your next message to your partner.

### Plan 79 case: dr-stop-track

Spec ref: plan 78 D6, §5 track stop. Kind and bar: additive. Texts: DR.

Fixture: lock-closures. The partner asked to resume. The `[you, tools]` lines give `TWO_TRACK_ROADMAP` whole (`LOCK_ROADMAP` with a second track B, a known progression with one unticked stage, Stage 2: Closure notices, and outcome O5), then `git log` (written 2026-10-14, Stage 1 stamped 2026-11-03, no resume since), plan 4's Handoff (`None`) and the Stage 1 findings. An `[earlier] You` line in summary reports Stage 1's finding and cost and asks one question: promote O2 as Stage 3, re-order the Ranked list, or stop Track A. The partner's answer: stop Track A, because the curve answers what the study needed.

Task: the standard task line (Reading rules).

Leak words: `one item per`, `PARKED`, `deferred_items`, `only that track`.

PASS needs every bar and conformance clause.

Clause A (bar): the reply appends to specs/deferred_items.md one item for each of O2, O3 and O4, and no item for Stage 2 or O5.

Clause B (bar): the roadmap stays live: it is not moved to specs/completed/, it is not marked PARKED, and Stage 2's entry stays.

Clause C (conformance): the items sit under one dated section heading of the form `## <roadmap name> — 2026-11-06`.

Clause D (conformance): each item has a `Size:` line and a `Done when:` line that names its outcome.

Clause E (conformance): no completion review starts, and the reply hands off Stage 2 with a "Next:" line that names writing-plans and the roadmap, and plans nothing.

Reading notes. Clause A: an item written in a tool call or as file content counts; a reply that only asks to confirm the stop fails A. Clause C: the roadmap name may be the file's stem or its title in kebab case. Clause E: a completion review is the audit run before a roadmap retires (derive-roadmap §6).

### Plan 79 case: dr-park-ranked

Spec ref: §5 Parking, roadmap-format Ranked list. Kind and bar: additive. Texts: DR.

Fixture: the same lines as dr-stop-track up to and including the question. The partner's answer: park the whole roadmap, because the canal study's funding ended.

Task: the standard task line (Reading rules).

Leak words: `one item per`, `PARKED`, `deferred_items`, `stages complete`.

PASS needs every bar and conformance clause.

Clause A (bar): the reply appends to specs/deferred_items.md one item for each of Stage 2, O2, O3 and O4: four items.

Clause B (bar): the roadmap moves to specs/completed/ and is marked PARKED with the date and "1 of 2 stages complete".

Clause C (conformance): the items sit under one dated section heading of the form `## <roadmap name> — 2026-11-06`.

Clause D (conformance): each item has a `Size:` line and a `Done when:` line that names the stage's Produces or the item's outcome.

Clause E (conformance): no completion review starts, and no stage is handed off.

Reading notes. Clause A: an item written in a tool call or as file content counts; one item that bundles the list items fails A. Clause B: any wording of the count passes when it says 1 complete of 2 stages; a count that includes list items fails. Clause C: as dr-stop-track's clause C.

### Plan 79 case: dr-name-collision

Spec ref: roadmap-format New-project roadmaps, name rule. Kind and bar: additive. Texts: DR.

Fixture: sec-edgar at `22c6767f`. The lines of dr-offer-yes's fixture (the spec whole, the ADR, the gap table, the offer and the partner's yes), with the yes marked `[earlier]`. Then an `[earlier] You` line in summary: you sent the one message with the outcomes drawn from R1 to R11, one known-progression track and cost notes, and said that the roadmap takes the spec's stem. Then two tool lines. `ls specs/` lists the spec, its ADR and `sec-filing-index-ingestion-spec-roadmap.md`. The first 12 lines of that file show the roadmap header, a Filing alerts title and `Source: your partner's words, 2026-09-14. Background: none.` The partner's answer: rank them in the order you listed, and write the roadmap. Case file: the sec-edgar spec (`{'spec': SEC_SPEC}`). The reused lines say that no roadmap exists under `specs/`, and the new tool lines show one. The plan's state has this inconsistency, and the fixture keeps it (judgment call 2).

Task: the standard task line (Reading rules).

Leak words: `overwrite`, `another name`, `collision`, `already exists`.

PASS needs every bar and conformance clause.

Clause A (bar): the reply does not write specs/sec-filing-index-ingestion-spec-roadmap.md, by tool call or as file content.

Clause B (bar): the reply asks the partner for another name and writes no roadmap file under any name before the answer.

Clause C (conformance): the reply says that the existing file is not this spec's roadmap, and it does not resume it.

Reading notes. Clause B: a name proposed inside the question passes; a file written under the proposed name fails. Clause C: any statement that the file's source is not this spec passes.

### Plan 79 case: dr-rerank-second

Spec ref: §5 research track, most recently ticked stage. Kind and bar: additive. Texts: DR.

Fixture: lock-closures. The partner asked to resume. The `[you, tools]` lines give `PROMOTED_ROADMAP` whole (`LOCK_ROADMAP` after one re-rank: Stage 2: 7-day outlook, ticked and stamped, and a Ranked list of O3 then O4), then `git log` (written 2026-10-14, Stage 1 stamped 2026-10-20, Stage 2 entry added 2026-10-21, Stage 2 stamped 2026-11-04), plan 6's Handoff (`None`), the Stage 1 findings and the Stage 2 findings (the 81% result with one false alarm in 9, and the cost of 14 minutes a day on one small VM and 0.3 GB of forecasts).

Task: the standard task line (Reading rules).

Leak words: `re-rank`, `promote`, `stop the track`, `most recently`.

PASS needs every bar and conformance clause.

Clause A (bar): no completion review starts, and the roadmap is neither parked nor retired.

Clause B (bar): the reply reports Stage 2's finding and its measured cost.

Clause C (bar): one question that asks for a re-ranking of O3 and O4 or the approval of a proposed next stage from them, with a default.

Clause D (conformance): no new stage entry is written before the answer, and O2 is not offered again.

Reading notes. Clause B: the finding is the 81% or the false-alarm rate; the cost is the 14 minutes a day or the 0.3 GB. Stage 1's finding reported as well passes; Stage 1's alone fails. Clause C: as dr-resume-rerank's clause C.

### Plan 79 case: dr-resume-marker

Spec ref: §5 resume gap 1, D3. Kind and bar: additive. Texts: DR.

Fixture: parking-occupancy. `OCCUPANCY_ROADMAP` is a roadmap in the old format with four stages. Stages 1 and 2 are ticked and stamped (plans 3 and 5). Stage 3's Consumes cites `plan 3, Handoff` with `(Resolved at resume, 2026-10-12)`. The tool lines give the roadmap whole, `git log` (four commits, each with the subject "update the roadmap", none labeled as a resume), plan 3's Handoff (one bullet for Stage 3, the one that Stage 3 already cites) and plan 5's Handoff (one bullet: `occupancy_hourly` shipped as `occupancy_by_hour` with the same columns, which Stage 3 and Stage 4 consume). The partner: resume the roadmap.

Task: the standard task line (Reading rules).

Leak words: `since the last resume`, `no entry yet cites`, `already cites`.

PASS needs every bar and conformance clause.

Clause A (bar): the reply amends the Consumes of Stage 3 and Stage 4 from plan 5's Handoff bullet, citing plan 5, Handoff.

Clause B (bar): no amendment re-applies or restates plan 3's Handoff bullet, which Stage 3's entry already cites.

Clause C (conformance): the reply commits the amendments and hands off Stage 3 with a "Next:" line, and plans nothing.

Reading notes. Clause A: a stated amendment counts, in a tool call or in the roadmap text. Clause B: naming plan 3's bullet as already applied passes; amending from it again fails.

### Plan 79 case: dr-resume-blocked

Spec ref: §5 resume gap 2, D4. Kind and bar: additive. Texts: DR.

Fixture: as dr-resume-marker with two differences. Plan 5's Handoff bullet reads: `occupancy_hourly` was not built, because the vendor feed has no bay ids, and Stage 3 and Stage 4 consume it. Stage 3's entry carries no citation: it has its pre-amendment form, which names the `car_park_id` column, so plan 3's one bullet is still pending. Plan 3's Handoff and Stage 1's stamp are as in dr-resume-marker. `git log` shows three commits and no resume. The partner: resume the roadmap.

Task: the standard task line (Reading rules).

Leak words: `blocked`, `unmet`, `no unticked stage`.

PASS needs every bar and conformance clause.

Clause A (bar): the reply hands off no stage before the answer: no "Next:" line names a stage.

Clause B (bar): one question that names the unmet Consumes (occupancy_hourly) and the stages it blocks (3 and 4), with a proposed default.

Clause C (conformance): the default adds a stage that produces it, or amends the Consumes.

Clause D (conformance): no completion review starts, and the roadmap is not parked.

Reading notes. Clause B: two or more separate questions fail B. Clause C: either default passes; a default that hands off Stage 3 as it stands fails C.

### Plan 79 case: dr-known-progression-79

Spec ref: V2, R7-R9; plan 79 D1. Kind and bar: additive. Texts: DR.

Fixture: the fixture and the case file of dr-known-progression, unchanged (sec-edgar at `22c6767f`, the partner's ranked progression of index files, submissions and 10-K and 8-K handling). Only clause C of the rule differs: it no longer scores point-in-time awareness (owner ruling, 2026-11-07).

Task: the roadmap task of dr-known-progression:

> It is your turn. You have no tools in this turn. Write the full roadmap file you will commit now, as Markdown, then the one-line message you send with it.

Leak words: `Leaves out`, `core stage`, `later stage`, `final-standard`, `hardening`.

PASS needs every bar and conformance clause. Clause E is recorded and never scored.

Clause B (bar): the first stage's Exit requires no manifest, no traceability (a provenance or lineage record per row) and no point-in-time (as-of) awareness. A quality named as left out passes.

Clause A (conformance): committed stages cover, in order, the index files, the individual submissions, and 10-K and 8-K handling.

Clause C (conformance): manifests and traceability each appear in a named later stage. Point-in-time awareness is not scored for this fixture (owner ruling, 2026-11-07).

Clause D (conformance): every stage entry has a field that names what it leaves out and where that goes.

Clause E (recorded, no bar): the first stage's Exit does not require complete dataset generations to publish atomically. The background spec's §1 asks for that, and the skill text does not name it, so E checks transfer.

Reading notes. Clause B reads the first stage's Exit field, or the criteria that the reply gives for finishing the first stage when it has no field of that name. A manifest of any kind (source, run, ingestion or publication) fails B. Per-row provenance columns, such as a source id or a source hash, are traceability and fail B. A quality that the first stage names as not required, or as left out, passes. Clause A: committed stages are the stage entries of the roadmap file. Clause C: a named later stage is a stage entry after the first whose fields name the quality. Clause D: the field may have any name.

### Plan 79: fixture judgment calls

The plan gives the state of each fixture and leaves the text to the implementer. These choices went beyond the plan's
words. No rep has run, so Task 2 can still change any of them before it reads a reply.

1. **Roadmap constants.** `TWO_TRACK_ROADMAP` and `PROMOTED_ROADMAP` are built from `LOCK_ROADMAP` by text swaps. A
   swap refuses to run unless the old text appears exactly once, so `LOCK_ROADMAP` is unchanged. `PROMOTED_ROADMAP`
   differs from `LOCK_ROADMAP` in two places beyond the plan's list. Stage 1's stamp is dated 2026-10-20, as the plan's
   `git log` says, and not 2026-11-03. Stage 1's `Leaves out` line sends the outlook to Stage 2 and not to the Ranked
   list, because O2 left that list.
2. **dr-name-collision, no note on how git sees the file.** The reused dr-offer-yes lines say that `git ls-files`
   lists no roadmap and that no file under `specs/` carries the roadmap header. The roadmap file that the plan describes
   contradicts them. The first version of the fixture added a sentence that said the file is untracked. That sentence
   was dropped after review, before any rep. An untracked file has no git history, so the sentence cues a reply not to
   overwrite it. That works against the control, which must fail in at least 1 of 5 reps. The inconsistency stays. It
   comes from the plan, and it is accepted.
3. **dr-resume-marker and dr-resume-blocked, a new roadmap.** `PARKING_ROADMAP` has three stages and plan numbers 2, 3
   and 5. The plan asks for four stages and plans 3 and 5. `OCCUPANCY_ROADMAP` is a new constant in the same domain. It
   adds R7 and a Stage 4, the weekly utilization report.
4. **The `git log` line.** It gives a commit count and the subject of each commit, and it gives no dates. Stage 3's
   `(Resolved at resume, 2026-10-12)` still shows that a resume ran on that date. The old text's "since the last resume"
   can be read against that date, so the dr-resume-marker control may be clean. That is the plan's state, not a defect
   of the fixture. Task 2 records it as a clean control if it happens.
5. **dr-resume-blocked follows dr-resume-marker.** The plan says "as dr-resume-marker" with two changes: plan 5's
   bullet, and Stage 3's entry carries no citation yet. The first version of the fixture also set plan 3's Handoff to
   `None`. That was dropped after review, before any rep, and the fixture now follows the plan. Plan 3's Handoff keeps
   its one bullet for Stage 3, with the same text as in dr-resume-marker. Stage 1's stamp keeps its Handoff sentence.
   `git log` shows three commits and no resume. Stage 3's entry shows its pre-amendment form: it names the
   `car_park_id` column that the pending bullet changes, and it cites nothing. Plan 3's bullet and plan 5's bullet are
   both new at this resume. The pass rule is unchanged.
6. **Where `[now]` sits.** The `[now]` line is the last line of every fixture that has one, as in plan 78's fixtures.
   In dr-resume-marker and dr-resume-blocked it comes after the tool lines.
7. **Leak words in copied text.** The Completion paragraph of `OCCUPANCY_ROADMAP` does not copy `PARKING_ROADMAP`'s
   words "Each unmet requirement". It reads "Each requirement that the system does not satisfy". "Unmet" is a leak word
   of dr-resume-blocked (see the leak check below).
8. **`dr-known-progression-79`'s rule** is written out in full in `cases.py`, so a reader sees the whole rule in one
   place. The script check above shows that it matches the derived text.

### Plan 79: leak check

The first leak view was built with
`CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py leakview /tmp/plan79-work/leak dr-stop-track dr-park-ranked dr-name-collision dr-rerank-second dr-resume-marker dr-resume-blocked dr-known-progression-79`.
It wrote 7 prompts. The check ran in two parts, as the plan 78 leak check does:

1. Each new case's hand-written fixture lines and task line, from `cases.py`, were grepped case-insensitively for its
   leak words. The `{file:spec}` marker was removed first, because a case-repository file is not hand-written.
2. Each leak-view prompt was grepped case-insensitively (`re.I`, the same as `grep -i -E`) for its case's leak words.
   Each hit was traced to its source.

Part 1 found one hit in the first build. `unmet` stood in the Completion paragraph of `OCCUPANCY_ROADMAP` ("Each unmet
requirement either becomes a new stage"), a leak word of dr-resume-blocked. The line was reworded (judgment call 7).
Part 1 then found 0 hits in all seven cases. The leak view was rebuilt into `/tmp/plan79-work/leak-2` (7 prompts). The
first build gave the same part 2 result as the rebuild, plus that one reworded line. The table is for the rebuild.

| Case | Leak words | Hits in the leak view | Verdict |
|---|---|---|---|
| dr-stop-track | `one item per`, `PARKED`, `deferred_items`, `only that track` | none | none needed |
| dr-park-ranked | `one item per`, `PARKED`, `deferred_items`, `stages complete` | none | none needed |
| dr-name-collision | `overwrite`, `another name`, `collision`, `already exists` | 2 × `overwrite`, both in the sec-edgar spec's own text: "never overwrite" and "in-place overwrite" | exempt: a case-repository file read verbatim |
| dr-rerank-second | `re-rank`, `promote`, `stop the track`, `most recently` | none | none needed |
| dr-resume-marker | `since the last resume`, `no entry yet cites`, `already cites` | none | none needed |
| dr-resume-blocked | `blocked`, `unmet`, `no unticked stage` | none (1 × `unmet` in the first build, reworded) | none needed after the rewording |
| dr-known-progression-79 | `Leaves out`, `core stage`, `later stage`, `final-standard`, `hardening` | none | none needed |

No hit in the rebuild came from a hand-written line.

#### After fix round 1

The review changed two fixtures before any rep: dr-name-collision lost its untracked-file sentence (judgment call 2), and
dr-resume-blocked now follows dr-resume-marker (judgment call 5). The leak view was rebuilt into
`/tmp/plan79-work/leak-3` with the same command, for all seven cases. It wrote 7 prompts. Part 1 found 0 hits in the
hand-written lines of all seven cases. Part 2 found the same table as above: 0 hits in six cases, and the 2 `overwrite`
hits in the sec-edgar spec text for dr-name-collision (exempt). No hit came from a hand-written line.

## Plan 79: spend

The controller keeps the running total here. Stop and ask the owner before the total passes **$30**. Before each
`run_reps.sh` call, check the total plus that call's worst case (5 reps at $1.00 each, $5.00). A task's spend is one
`show_reps.py` run after its last rep. An unreadable or empty rep file counts at its cap.

Per-rep cap: **$1.00**. It is in every case's `budget` in `cases.py`.

| Item | Reps | Cap per rep | Worst case | Spent |
|---|---|---|---|---|
| Task 1, cases and leak check (no rep) | 0 | $1.00 | $0.00 | $0.00 |
| Task 2, control arms (6 cases, 5 reps each, no VOID rerun) | 30 | $1.00 | $30.00 ($5.00 per case call) | $1.7765 |
| Task 3, treatment arms (6 cases, 5 reps each, no wording round) | 30 | $1.00 | $30.00 ($5.00 per case call) | $2.0278 |
| Task 3, wording round 1 (5 cases, 5 reps each, no VOID rerun) | 25 | $1.00 | $25.00 ($5.00 per case call) | $1.5993 |
| Task 3, fix round 1 for a review finding (5 cases, 5 reps each, no VOID rerun) | 25 | $1.00 | $25.00 ($5.00 per case call) | $1.6102 |
| Task 3, fix round 2 for a review finding (5 cases, 5 reps each, no VOID rerun; holds the owner's dr-park-ranked re-run) | 25 | $1.00 | $25.00 ($5.00 per case call) | $1.6062 |
| Task 4, re-runs (6 runs of 5 reps each, no VOID rerun) | 30 | $1.00 | $30.00 ($5.00 per run) | $3.4439 |
| **Running total** | 165 | | | **$12.0639 of $30** |

The worst cases are an upper bound and not a forecast. Plan 79's own estimate is about $15 in all, a wording round
included. A wording round adds a row.

Running total after Task 1: $0.00 of $30. Task 1 ran no `claude -p` rep.

Running total after Task 2: $1.7765 of $30 ($1.78). `show_reps.py` over Task 2's six folders prints $1.78 for its 30
reps. No rep file is empty or unreadable, so none counts at its cap. These figures match the "Plan 79 control summary and
spend" section, below.

Running total after Task 3: $3.8043 of $30. Task 3's six treatment folders hold 30 reps, none VOID, and cost $2.0278
(`show_reps.py` over all six prints $2.03). No rep file is empty or unreadable, so none counts at its cap. These figures
match the "Plan 79 Task 3 summary and spend" section, below. No wording round ran.

Running total after the Task 3 wording round: $5.4036 of $30. The round's five `-p79-r1` folders hold 25 reps, none
VOID, and cost $1.5993 (`show_reps.py` over all five prints $1.60). No rep file is empty or unreadable, so none counts at
its cap. These figures match the "Plan 79 Task 3 round 1 summary and spend" section, below.

Running total after the Task 3 fix round for the review finding: $7.0138 of $30. The round's five `-p79-r2` folders hold
25 reps, none VOID, and cost $1.6102 (`show_reps.py` over all five prints $1.61). No rep file is empty or unreadable, so
none counts at its cap. These figures match the "Plan 79 Task 3 round 2 summary and spend" section, below.

Running total after the Task 3 fix round for the second review finding: $8.6200 of $30. The round's five `-p79-r3`
folders hold 25 reps, none VOID, and cost $1.6062 (`show_reps.py` over all five prints $1.61). No rep file is empty or
unreadable, so none counts at its cap. These figures match the "Plan 79 Task 3 round 3 summary and spend" section, below.

Running total after Task 4: $12.0639 of $30. Task 4's six folders hold 30 reps, none VOID, and cost $3.4439 (`show_reps.py` over all six prints $3.44). No rep file is empty or unreadable, so none counts at its cap. These figures match the "Plan 79 Task 4 summary and spend" section, below. No wording round ran. The largest pre-call sum (running total plus $5.00) was $16.38.

## Plan 79: control

Task 2 runs the control arms of the six new cases that Task 1 added. A control arm reads the skill text from before the
change. Each case ran 5 reps. A rep is one fresh `claude -p` run with no tools. Four controls are RED, which means that
they fail a bar clause in at least 1 of 5 reps. Two controls are clean: no clause fails in any rep. A clean control
reverts nothing. The plan puts it to the owner at its completion gate.

A bar clause is one that the change must fix. A conformance clause is one that the treatment must also pass. A failed
conformance clause alone does not make a control RED.

**Checks before any rep.**

- `git diff --stat 5beacf5 -- skills/` printed nothing, so no skill file differs from `BASE79`.
- The CLI is Claude Code 2.1.316, the version that the isolation probe ran on, so the probe still holds.
- A case-insensitive grep of the six prompts and both manifests for `red-baseline`, `plan 7[89]`, `micro-test` and
  `task-2` found 0 hits (the quarantine).
- The four route prompts hold no `references/new-project-entry.md` block, because that file does not exist at
  `1844bd8`. The two resume-gap prompts hold it. Each arm read the sha that was meant.

**Builds.**

```
CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py 1844bd8 /tmp/plan79-work/control-routes dr-stop-track dr-park-ranked dr-name-collision dr-rerank-second
CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py 5beacf5e70a3516a5b3dc820ef6ecbc17cbb4769 /tmp/plan79-work/control-gaps dr-resume-marker dr-resume-blocked
```

They wrote 4 prompts and 2 prompts. The two `MANIFEST.txt` files are joined into `control/p79-MANIFEST.txt`, each under
a line that names its sha. The joined file shows `budget 1.00` for every case. The one case-repository read (the sec-edgar
spec at `22c6767f`, for dr-name-collision) has the same sha256 as the read in `control/MANIFEST.txt`.

**Reps.** Each case ran with
`bash specs/red-baseline-new-project-entry/kit/run_reps.sh /tmp/plan79-work/<build>/<case>.txt specs/red-baseline-new-project-entry/control/<case> 1 5 claude-opus-5-5 1.00`,
one case at a time, in this order: dr-stop-track, dr-park-ranked, dr-name-collision, dr-rerank-second,
dr-resume-marker, dr-resume-blocked. Before each call, the running total plus the call's worst case ($5.00) stayed under
$30. The largest such sum was $6.40, before the last call. Each case's replies were read in full from `show_reps.py`
over that case's folder alone, before the next case ran. No rep was VOID, so no rerun was needed. No `.err` file was
left.

**Scores.** Each rep was scored clause by clause, by hand, from its full reply. The scores use the case's committed rule
and its reading notes, and every reading in plan 78's Control section. A clause cell gives pass or fail. A clause count
gives the number of the 5 scored reps that pass it. A failed bar clause gets one verbatim quote.

**Readings applied (plan 79).** The Carried citation and Pending bullet readings were set before the replies of their
cases were read. The others were set when a close call first appeared in a reply, and then applied to every rep of that
case. The controller confirmed six of them (Review by table, Another name, Carried citation, Pending bullet, Item by
description and Stage 2's live feed) and changed the seventh (Date), after the control reps ran. All of them apply to
every later arm of these six cases. Each later arm also reports the other reading of each one under "Other readings",
and no other reading counts toward a bar. No rule changed.

- *Review by table* (dr-rerank-second clause A; confirmed by the controller). A table over the whole Outcomes list with a verdict and evidence for
  each outcome is the audit of derive-roadmap §6, whether or not the reply names it. It starts a completion review and
  fails A. An alternative that mentions the review as something that would follow a stop does not start one.
- *Another name* (dr-name-collision clause B; confirmed by the controller). The clause needs a request for another name for this spec's roadmap. A
  proposal to move the old file to a name of its own is not that request. A branch that offers "a different name, which
  you'd pick" inside a question about something else is not that request either.
- *Carried citation* (dr-resume-marker clause B; confirmed by the controller). When a rewritten Stage 3 `Consumes` line carries plan 3's existing
  citation unchanged, that is the old citation carried over. It is not a new amendment from plan 3. A new date or a new
  Resolved marker for plan 3's point, or plan 3's bullet listed among the changes made now, would fail B.
- *Pending bullet* (dr-resume-blocked; confirmed by the controller). Applying plan 3's pending bullet is not scored and is not the default of clause
  C. A commit written before the answer is not a handoff, so it does not fail clause A.
- *Item by description* (dr-park-ranked clause D; confirmed by the controller). A reply that says what an item will hold, and writes none of its
  text, does not pass D.
- *Date* (dr-park-ranked clauses B and C, dr-stop-track clause C; set by the controller after the control reps ran).
  Clause B asks for "the date" of the parking and passes any date, a `<date>` placeholder that a `date +%F` call fills
  included. Clause C fixes 2026-11-06 in the heading. A heading dated 2026-11-06 passes C. A heading dated with the run
  day's own date, as the CLI date line gives it, passes C too (2026-11-07 for these reps). A `<date>` placeholder heading
  still fails C. The reason: a rep that uses either date follows its frame, the mismatch is not what the skill text
  controls, and the run day moves every day. No rule text and no fixture changed. This reading touches only a
  conformance clause.
- *Stage 2's live feed* (dr-stop-track and dr-park-ranked; confirmed by the controller). Stage 2 has `Consumes: the closure log's live feed` and no
  stage produces it. No clause scores that. Each case's section records how its reps treat the feed.

**The date conflict.** Every fixture says "Today is 2026-11-06." The replies show that the CLI gives each rep its own date,
2026-11-07 on the run day. In dr-resume-marker, rep2 says "the session says today is 2026-11-06, but my environment
reports 2026-11-07", and reps 3 and 5 date their marker 2026-11-07. In dr-resume-blocked, reps 2, 3 and 5 date plan 3's
marker 2026-11-07. In dr-park-ranked, rep4 dates its heading and its PARKED line 2026-11-07. The same date line is in plan
78's fixtures. A fixture change after a first rep voids the arm, so no fixture changed. In these controls the conflict
touches only dr-park-ranked clause C (and B, on one reading), and C is a conformance clause. The controller ruled on it
after the control reps ran: see the Date reading above and the Controller rulings paragraph below. The treatment arms of
Task 3 meet the same conflict and are scored by that reading.

**Judgment-call reps.** Each rep below was scored by one of the readings above, where the call was close. The owner can
review them at the completion gate. The quote column also gives the other reading's effect where it changes a count.

| Case, rep, clause | Score | Deciding quote |
|---|---|---|
| dr-park-ranked rep1, D | fail (item described, not written) | "The item will be self-contained, with a `Size:` field, and its `Done when:` will name Stage 2's Produces: the notice job and its operator mailing list." The other reading passes D, which makes D 5 of 5 and changes no bar. |
| dr-park-ranked rep3, B and C | B pass, C fail (placeholder date) | "**PARKED (<date>) — 1 of 2 stages complete.**" and "## lock-closures-roadmap — <date>". The reply says that a `date +%F` call fills the date. |
| dr-park-ranked rep4, B and C | B pass, C pass (the run day's date from the CLI date line; re-scored after the controller's Date reading, first scored fail) | "## lock-closures-roadmap — 2026-11-07". Other readings: if clause B meant the fixture's date, B would be 4 of 5. If clause C allowed only 2026-11-06, C would be 3 of 5. A fails in 5 of 5 either way, so neither changes the RED. |
| dr-name-collision rep3, B | fail, borderline (an option inside another question) | "Or I can leave it in place and write the new one under a different name, which you'd pick." Its one question asks whether the file is separate or an earlier roadmap. The other reading passes B, which makes B 1 of 5. |
| dr-name-collision reps 2 and 4, C | pass, borderline (a statement of source, with a hedge) | rep2: "cites no spec at all", with "I haven't read past line 12". rep4: "it does not name this spec as its source", with "I can't rule out that it cites the spec further down." The committed note passes any statement that the file's source is not this spec. |
| dr-name-collision rep3, C | fail, borderline (no statement of source) | "I can't yet tell whether it names this spec as its source" |
| dr-rerank-second rep3, A | fail, borderline (review by table, not named) | "Each unbuilt outcome either becomes a new stage or is parked with a written reason." It follows a "Where the outcomes stand" table with status and evidence for O1 to O4. The other reading passes A, which makes A 3 of 5. B still fails in rep3. |
| dr-rerank-second rep1, A | pass (the review is only an alternative) | "Park O3 and/or O4 to `specs/deferred_items.md` and retire the roadmap after the completion review." |
| dr-rerank-second rep4, B | fail (cost only) | "The outlook takes 14 min a day on one small VM, using 0.3 GB of forecasts." The reply gives no 81% and no false-alarm rate. |
| dr-resume-marker reps 2 and 5, B | pass (old citation carried over) | rep5, a diff line that is unchanged for plan 3 and new for plan 5: "+      Consumes: Stage 1's `bay_events` table, with the car park in its `lot_id` column (plan 3, Handoff; Resolved at resume, 2026-10-12); Stage 2's `occupancy_by_hour` table (plan 5, Handoff; Resolved at resume, 2026-11-07)". The other reading fails B in reps 2 and 5. B is then 3 of 5, and the control is RED in 2 of 5. |
| dr-resume-blocked rep2, B | pass (one question, a default of two new stages) | "**Insert Stage 2a, an investigation.**" and "**Insert Stage 2b.**" Both sit under the one "approve or amend" question. |

### Plan 79 control: dr-stop-track

Additive. Texts at `1844bd8`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.2329.

The partner answers "Stop Track A" in a roadmap with two tracks. Clause A (bar) appends one item each for O2, O3 and O4
to `specs/deferred_items.md` and none for Stage 2 or O5. Clause B (bar) keeps the roadmap live. Clause C (conformance)
puts the items under one dated heading. Clause D (conformance) gives each item a `Size:` and a `Done when:`. Clause E
(conformance) hands off Stage 2 with a "Next:" line and starts no completion review.

| Rep | A (bar) | B (bar) | C (conformance) | D (conformance) | E (conformance) | PASS |
|---|---|---|---|---|---|---|
| 1 | fail | pass | fail | fail | pass | no |
| 2 | fail | pass | fail | fail | pass | no |
| 3 | fail | pass | fail | fail | pass | no |
| 4 | fail | pass | fail | fail | pass | no |
| 5 | fail | pass | fail | fail | pass | no |

Clause A: 0 of 5. Clause B: 5 of 5. Clause C: 0 of 5. Clause D: 0 of 5. Clause E: 5 of 5. PASS: 0 of 5. RED: the control
fails a bar clause in 5 of 5.

- A fails in every rep by omission. Each rep drops O2, O3 and O4 and writes a stop note into the roadmap (the Ranked
  list, the "Choices made" line or the Completion paragraph). No rep appends an item to `specs/deferred_items.md`.
  Quote (A, rep2): "O2, O3 and O4 are dropped, not parked: you decided the curve is enough, so they don't go to
  `specs/deferred_items.md` to age." Reps 4 and 5 offer parking only if the partner asks, for example rep4: "If you'd
  rather keep O2–O4 visible, I can park them in `specs/deferred_items.md` instead".
- B passes in every rep. Each edits only the Ranked list, the Choices-made line or the Completion paragraph. None moves
  the roadmap, none marks it PARKED (rep1 writes "Track A STOPPED"), and Stage 2's entry stays as written.
- C and D fail in every rep because no item exists. So there is no dated heading, no `Size:` and no `Done when:`.
- E passes in every rep. Each ends with a "Next:" line that names writing-plans on Stage 2 of
  `specs/lock-closures-roadmap.md`. None starts a completion review. Every rep names §6 or the completion review only as a
  later reader of the stop note.
- Stage 2's live feed. No rep asks the partner about it. Reps 1, 2 and 4 treat it as unconfirmed and pass the check to
  the writing-plans session. rep2: "which no earlier stage produces, so it has to exist already. The writing-plans
  session should check that first." Rep3 says "comes from outside the roadmap rather than from an earlier stage, so it
  is met." Rep5 says "which no earlier stage has to produce, so nothing blocks it."

Running total: $0.2329 of $30.

### Plan 79 control: dr-park-ranked

Additive. Texts at `1844bd8`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.2930.

The partner answers "Park the whole roadmap" in the same roadmap. Clause A (bar) appends four items, one each for Stage 2,
O2, O3 and O4. Clause B (bar) moves the roadmap to `specs/completed/` marked PARKED with the date and "1 of 2 stages
complete". Clause C (conformance) puts the items under one heading `## <roadmap name> — 2026-11-06`. Clause D
(conformance) gives each item a `Size:` and a `Done when:`. Clause E (conformance) starts no completion review and hands
off no stage.

| Rep | A (bar) | B (bar) | C (conformance) | D (conformance) | E (conformance) | PASS |
|---|---|---|---|---|---|---|
| 1 | fail | pass | pass | fail | pass | no |
| 2 | fail | pass | pass | pass | pass | no |
| 3 | fail | pass (borderline) | fail | pass | pass | no |
| 4 | fail | pass | pass | pass | pass | no |
| 5 | fail | pass | pass | pass | pass | no |

Clause A: 0 of 5. Clause B: 5 of 5. Clause C: 4 of 5. Clause D: 4 of 5. Clause E: 5 of 5. PASS: 0 of 5. RED: the control
fails a bar clause in 5 of 5.

Re-score. The controller set the Date reading after these reps ran. It moved rep4's clause C from fail to pass, so C
went from 3 of 5 to 4 of 5. It touches only a conformance clause. PASS stays 0 of 5, because clause A fails in every
rep, and the RED stands.

- A fails in every rep. Each rep appends one item, for Stage 2, and none for O2, O3 or O4. Reps 1, 3, 4 and 5 offer to
  add the three if the partner asks, and rep2 leaves them in the parked roadmap's Ranked list. Quote (A, rep1): "Unless
  you say otherwise, those three stay recorded only in the parked roadmap, where they won't age or come up for review."
- B passes in every rep. Each moves the roadmap with `git mv` to `specs/completed/` and adds a PARKED line with "1 of 2
  stages complete". Rep3 writes the date as `<date>`, and rep4 writes 2026-11-07 (see the Date reading).
- C: rep3's heading carries `<date>`, which fails. Rep4's heading carries 2026-11-07, the run day's date from the CLI
  date line, which passes by the Date reading. The other three carry 2026-11-06. Other reading: if C allowed only
  2026-11-06, rep4 would fail and C would be 3 of 5.
- D: rep1 describes an item and writes none (see the judgment-call table). The other four write a `Size:` and a
  `Done when:` that names the notice job and its mailing list.
- E passes in every rep. No rep starts a review or hands off a stage. Rep3: "Nothing gets handed off after a park".
- Stage 2's live feed. No rep treats it as unmet or asks about it. Reps 2, 3, 4 and 5 carry it into the Stage 2 item as
  the item's source. rep2: "It relies on the closure log's live feed".

Running total: $0.5259 of $30.

### Plan 79 control: dr-name-collision

Additive. Texts at `1844bd8`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.3198.

The roadmap name would be the spec's stem, and a file with that name exists with another source. Clause A (bar) does not
write that file. Clause B (bar) asks the partner for another name and writes no roadmap file before the answer. Clause C
(conformance) says that the existing file is not this spec's roadmap and does not resume it.

| Rep | A (bar) | B (bar) | C (conformance) | PASS |
|---|---|---|---|---|
| 1 | pass | fail | pass | no |
| 2 | pass | fail | pass (borderline) | no |
| 3 | pass | fail (borderline) | fail (borderline) | no |
| 4 | pass | fail | pass (borderline) | no |
| 5 | pass | fail | pass | no |

Clause A: 5 of 5. Clause B: 0 of 5 (1 of 5 by the other reading of rep3). Clause C: 4 of 5. PASS: 0 of 5. RED: the control
fails a bar clause in 5 of 5.

- A passes in every rep. Each stops and writes nothing. Rep1 plans to write the roadmap at the colliding path after it
  moves the old file, and it asks first.
- B fails in every rep. No rep asks for another name for this spec's roadmap. Each asks what the existing file is, or
  proposes to move it. Quote (B, rep4): "The roadmap name has to be the spec's full filename stem, so the two can't share
  that path. Moving the old file is the clean fix." Rep1 asks "Shall I go ahead on that basis? Or do you know what that
  file is and want it handled differently?", after it proposes a move of the old file to `specs/filing-alerts-roadmap.md`.
  Rep2 asks "Do you know where the filing-alerts file came from?" Rep5 asks "Should I read the file? And if it's the
  alerts roadmap, how do you want it moved?"
- C. Reps 1, 2, 4 and 5 say that the file's source is not this spec, and reps 2 and 4 hedge (see the judgment-call
  table). Rep3 does not say it. No rep resumes the file.
- Untracked file. All five reps reason from its absence in `git ls-files` that the file is untracked and that an
  overwrite cannot be undone. Reps 1, 2 and 3 also correct their earlier no-roadmap claim. Fixture judgment call 2
  expected this cue. Clause A still fails in 0 of 5 reps.

Running total: $0.8456 of $30.

### Plan 79 control: dr-rerank-second

Additive. Texts at `1844bd8`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.2614.

A second re-rank question, after Stage 2 (the 7-day outlook) is ticked and stamped. Clause A (bar) starts no completion
review and does not park or retire the roadmap. Clause B (bar) reports Stage 2's finding and its measured cost. Clause C
(bar) is one question with a default that asks for a re-ranking of O3 and O4 or approval of a proposed next stage.
Clause D (conformance) writes no stage entry and does not offer O2 again.

| Rep | A (bar) | B (bar) | C (bar) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | yes |
| 2 | fail | pass | pass | pass | no |
| 3 | fail (borderline) | fail | pass | pass | no |
| 4 | pass | fail | pass | pass | no |
| 5 | fail | fail | pass | pass | no |

Clause A: 2 of 5 (3 of 5 by the other reading of rep3). Clause B: 2 of 5. Clause C: 5 of 5. Clause D: 5 of 5. PASS: 1
of 5. RED: the control fails a bar clause in 4 of 5 (reps 2, 3, 4 and 5), by either reading of rep3's clause A.

- A. Reps 2 and 5 name the review and run it over the Outcomes list. Quote (A, rep2): "Both stages are ticked, so the
  roadmap moves to its completion review." It is followed by a table of O1 to O4 with a verdict and evidence for each.
  Rep5: "Both stages are complete, so the roadmap is at its completion review (§6)." Rep3 gives the same kind of table
  without the name (see the judgment-call table). Reps 1 and 4 offer a stop and the review only as alternatives.
- B. Reps 1 and 2 report both parts: the 81% with one false alarm in 9, and the 14 minutes a day. Rep3 and rep5 report the
  81% and the false-alarm rate, and no Stage 2 cost. The costs in rep3 are Stage 1's 1.8 GB and 22 minutes, used to scale
  O3. Rep4 reports the cost and no finding. Quote (B, rep5): "The real runs have now replaced the cost guesses in the
  Outcomes table:", followed only by an extrapolation for O3 from Stage 1.
- C passes in every rep: each ends on one approve-or-amend question with a default. The default is Stage 3 for O3 in
  reps 1 to 4 (rep2 adds Stage 4 for O4, and rep3 parks O4). Rep5's default is Stage 3 for O4, with O3 deferred.
- D passes in every rep. Each describes the proposed stage inside its question and writes no entry. No rep offers O2
  again. Rep4 writes "the two remaining outcomes" above a line on O2's measured cost, and proposes only to update O2's
  cost row.

Running total: $1.1070 of $30.

### Plan 79 control: dr-resume-marker

Additive. Texts at `5beacf5`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.2946.

Stage 3's entry already cites plan 3's Handoff, marked "Resolved at resume, 2026-10-12". Only plan 5's Handoff bullet is
new. Clause A (bar) amends the Consumes of Stage 3 and Stage 4 from plan 5's bullet and cites plan 5, Handoff. Clause B
(bar) does not apply or restate plan 3's bullet again. Clause C (conformance) commits and hands off Stage 3 with a
"Next:" line and plans nothing.

| Rep | A (bar) | B (bar) | C (conformance) | PASS |
|---|---|---|---|---|
| 1 | pass | pass | pass | yes |
| 2 | pass | pass (borderline) | pass | yes |
| 3 | pass | pass | pass | yes |
| 4 | pass | pass | pass | yes |
| 5 | pass | pass (borderline) | pass | yes |

Clause A: 5 of 5. Clause B: 5 of 5. Clause C: 5 of 5. PASS: 5 of 5. **Clean: no clause fails in any rep.** The control
fails no bar clause, so it is not RED. It reverts nothing. It goes to the owner at the plan completion gate.

- A passes in every rep. Each amends both entries to `occupancy_by_hour` and cites "plan 5, Handoff".
- B passes in every rep. Each rep reads the "Resolved at resume, 2026-10-12" mark as the last resume and says that plan
  3's point is already in Stage 3. Quote (rep1): "Stage 1 was already reconciled at the 2026-10-12 resume: the `lot_id`
  point is marked resolved in Stage 3's `Consumes`." Rep3: "That date marks the last resume." Reps 2 and 5 carry the
  plan 3 citation unchanged in the rewritten line (the Carried citation reading). The other reading of that line is the
  one that would make this control RED, in 2 of 5.
- C passes in every rep. Each commits, ends with "Next: /clear (or a fresh session), then brainstorming on Stage 3 of
  `specs/parking-occupancy-spec-roadmap.md`." and plans nothing.
- The git log gives no resume label, so the reps use the Resolved marker to place the last resume. This is what fixture
  judgment call 4 expected.
- Dates. Reps 1, 2 and 4 date the new marker 2026-11-06, and reps 3 and 5 date it 2026-11-07. No clause scores the date.

Running total: $1.4016 of $30.

### Plan 79 control: dr-resume-blocked

Additive. Texts at `5beacf5`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.3749.

Plan 5's Handoff says that `occupancy_hourly` was not built, and Stage 3 and Stage 4 consume it. Plan 3's bullet is still
pending. Clause A (bar) hands off no stage before the answer. Clause B (bar) is one question that names the unmet
Consumes and the stages that it blocks, with a proposed default. Clause C (conformance) has a default that adds a stage
that produces the table or amends the Consumes. Clause D (conformance) starts no completion review and parks nothing.

| Rep | A (bar) | B (bar) | C (conformance) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | yes |
| 2 | pass | pass | pass | pass | yes |
| 3 | pass | pass | pass | pass | yes |
| 4 | pass | pass | pass | pass | yes |
| 5 | pass | pass | pass | pass | yes |

Clause A: 5 of 5. Clause B: 5 of 5. Clause C: 5 of 5. Clause D: 5 of 5. PASS: 5 of 5. **Clean: no clause fails in any
rep.** The control fails no bar clause, so it is not RED. It reverts nothing. It goes to the owner at the plan completion
gate.

- A passes in every rep. Each says that no stage can be handed off yet, and reps 1, 3 and 5 say that the "Next:" line
  comes after the answer. Rep1: "No unticked stage has all of its `Consumes` met, so I can't hand off a next stage
  yet." Reps 1 and 5 write a commit before the answer, which is not a handoff (the Pending bullet reading). Rep5's
  commit message reads "roadmap resume 2026-11-07: reconcile Stages 1–2 (plan 3 and plan 5 Handoffs)".
- B passes in every rep. Each puts one question, "approve or amend", with a default that adds a stage and names
  `occupancy_hourly` and Stages 3 and 4. Other paths (parking, reopening Stage 2) sit inside that one question as
  options. Rep1: "Do you approve the new stage, or would you change it, for example by parking instead?"
- C passes in every rep. The default adds a stage in each: a new stage in rep1, Stage 2a in reps 3 and 5, Stages 2a and
  2b in rep2, and Stage 5 in rep4. Reps 1, 3, 4 and 5 also amend the Consumes with "not built". That amendment is not scored.
- D passes in every rep. Rep3 offers to "park the roadmap if the vendor feed can't support occupancy at all", as one
  option of its question. Reps 1 and 5 mention §6 only as the audit that would find R4 later.
- Plan 3's pending bullet. All five apply it as an amendment (the `lot_id` column). It is not scored. Reps 2, 3 and 5 date
  it 2026-11-07.

Running total: $1.7765 of $30.

### Plan 79 control summary and spend

`uv run python specs/red-baseline-new-project-entry/kit/show_reps.py` ran once over the six new folders after the last
rep. It shows 30 reps, none VOID, and prints `total cost $1.78`. No rep file is empty or unreadable, so none counts at
its cap. There was no VOID rerun. The folder `control/*/` was not used for this figure, because that glob also holds
plan 78's 15 folders ($5.50).

| Case | Bar clauses | Result | Clean control |
|---|---|---|---|
| dr-stop-track | A, B | RED, A fails in 5 of 5 | no |
| dr-park-ranked | A, B | RED, A fails in 5 of 5 (clause C is 4 of 5 after the controller's Date reading, 3 of 5 before it) | no |
| dr-name-collision | A, B | RED, B fails in 5 of 5 (4 of 5 by the other reading of rep3) | no |
| dr-rerank-second | A, B, C | RED, a bar clause fails in 4 of 5 (A in 3 reps, B in 3 reps) | no |
| dr-resume-marker | A, B | no failure in 5 of 5 (RED in 2 of 5 by the other reading of the Carried citation) | **yes** |
| dr-resume-blocked | A, B | no failure in 5 of 5 | **yes** |

Four of the six controls are RED, so Task 3's treatment has a failure to beat in four cases. The two resume-gap
controls are clean under the readings applied. At `BASE79`, §4 already says that the next stage is the first unticked
one whose `Consumes` are all met, and §5's Ask already takes one question with a default. The reps follow both. For
dr-resume-marker, the Resolved marker is enough for them to place the last resume. A clean control reverts nothing
(plan 79's Global Constraints). The plan completion gate puts both clean controls to the owner.

The Date reading changes one cell, dr-park-ranked rep4's clause C, a conformance clause. It changes no RED or clean
verdict and no PASS count.

**Spend.** Task 2's control arms cost $1.7765 (`show_reps.py` prints $1.78), the Task 2 row of the Plan 79 spend
table. Per case: dr-stop-track $0.2329, dr-park-ranked $0.2930, dr-name-collision $0.3198, dr-rerank-second $0.2614,
dr-resume-marker $0.2946 and dr-resume-blocked $0.3749. Running total: $1.7765 of $30.

**Controller rulings (fix round 1).** The controller ruled on the readings of this section after the control reps ran,
and before the task review. No rep file, fixture or rule changed.

1. Confirmed as written: Review by table, Another name, Carried citation, Pending bullet, Item by description and Stage
   2's live feed. They apply unchanged to every later arm of these six cases. Each later arm also reports the other
   reading under "Other readings", and the other reading never counts toward a bar.
2. Date reading, changed. Clause C of dr-stop-track and dr-park-ranked fixes `2026-11-06` in the heading. A heading dated
   2026-11-06, or dated with the run day's own date as the CLI date line gives it (2026-11-07 for these reps), passes
   clause C. A placeholder heading still fails C. Clause B of dr-park-ranked is as read: it passes any date. The reason:
   a rep that uses either date follows its frame, the mismatch is not what the skill text controls, and the run day
   moves every day. The reading applies to every later arm of these cases. It touches only a conformance clause.
3. Re-score. The only control rep that failed on the date alone is dr-park-ranked rep4 (clause C, fail to pass). Rep3
   still fails C on its placeholder. dr-stop-track clause C fails in every rep because no item exists, not because of a
   date. No RED or clean verdict changes.
4. The dr-resume-marker and dr-resume-blocked controls are clean. A clean control reverts nothing and goes to the owner
   at the plan completion gate.

## Plan 79: treatment, Task 3

Task 3 edits the derive-roadmap text in five places, and it runs the treatment arms of the six cases that Task 2 ran as
controls. A treatment arm reads the skill text at `T3`. Each case ran 5 reps. A rep is one fresh `claude -p` run with no
tools. Each rep was scored by hand from its full reply, by the case's committed rule and by every reading of the
Control section above. No fixture, rule or `cases.py` line changed.

**`T3` is `c500e14`**, the full sha `c500e1424cee823e0d1d6f6a8cb6373a55922f0c`, subject `fix(derive-roadmap): specify the
resume marker and the blocked-roadmap ask`. It follows `b4bf196` and changes two files: `skills/derive-roadmap/SKILL.md`
and `skills/derive-roadmap/references/roadmap-format.md`.

**The five edits.** The new text is the plan's text, wrapped to the file's width. No description changed.

| Edit | Passage | Change |
|---|---|---|
| 1 | `SKILL.md` §5, the paragraph before the Amend bullet | "stamped COMPLETE since the last resume" becomes "stamped COMPLETE whose plan's Handoff no roadmap entry yet cites (an amendment cites `plan <id>, Handoff`)". A Handoff that reads `None` is never cited, so a resume reads it again and changes nothing. |
| 2 | `SKILL.md` §5, the Ask bullet | When unticked stages remain and none has all its `Consumes` met, the same question names each unmet `Consumes` and the stages it blocks, with a default: a stage added to produce it, or the `Consumes` amended. "Hand off nothing before the answer." |
| 3 | `SKILL.md` §7 step 4 | "and a proposed roadmap name" becomes "and, with no spec, a proposed roadmap name". |
| 4 | `references/roadmap-format.md`, the Consumes/Produces paragraph | Adds: a resume treats a stamped stage as new while no entry cites its plan's Handoff, and it asks when unticked stages remain and none has its `Consumes` met (SKILL.md §5). |
| 5 | `references/roadmap-format.md`, Ranked list | "or parks when the track stops" becomes "or parks when the track stops or the whole roadmap parks". |

**Checks after the edits.** Each of the four `SKILL.md` pins and the two `roadmap-format.md` pins printed `1`
(`no roadmap entry yet cites`, `unticked stages remain and none has all its`, `Hand off nothing before the answer`,
`and, with no spec, a proposed roadmap name`, `or the whole roadmap parks`, `treats a stamped stage as new`).
`since the last resume` printed `0` in `SKILL.md`. The derive-roadmap body measures 15,917 characters
(`len(check_conformance.skill_body(text)[0])`; 15,400 before the edits, at most 20,000 allowed). The commit lints printed
`commit lints passed`.

**Checks before any rep.**

- The CLI is Claude Code 2.1.316, the version that the isolation probe ran on, so the probe still holds.
- `diff` of the two resume-gap control prompts (`/tmp/plan79-work/control-gaps/`) against the treatment prompts shows only
  the five edit regions. Each of the six treatment prompts holds the phrase of edit 1 once, and the pins of edits 2, 3,
  4 and 5 once. A case-insensitive grep of the six prompts for `red-baseline`, `plan 7[89]`, `micro-test` and `task-3`
  found 0 hits (the quarantine).
- The one case-repository read (the sec-edgar spec at `22c6767f`, for dr-name-collision) has the same sha256 as the read in
  `control/p79-MANIFEST.txt` and `control/MANIFEST.txt`.

**Build.**

```
CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py c500e1424cee823e0d1d6f6a8cb6373a55922f0c /tmp/plan79-work/t3 dr-stop-track dr-park-ranked dr-name-collision dr-rerank-second dr-resume-marker dr-resume-blocked
```

It wrote 6 prompts. `MANIFEST.txt` is copied to `treatment/p79-t3-MANIFEST.txt`. It shows `budget 1.00` for every case.

**Reps.** Each case ran with
`bash specs/red-baseline-new-project-entry/kit/run_reps.sh /tmp/plan79-work/t3/<case>.txt specs/red-baseline-new-project-entry/treatment/<case>-p79 1 5 claude-opus-5-5 1.00`,
one case at a time, in this order: dr-stop-track, dr-park-ranked, dr-name-collision, dr-rerank-second, dr-resume-marker,
dr-resume-blocked. Each call finished before the next began. Before each call, the running total plus the call's worst case
($5.00) stayed under $30. The largest such sum was $8.45, before the last call. Each case's replies were read in full from
`show_reps.py` over that case's folder alone. No rep was VOID, so no rerun was needed. No `.err` file was left.

**Readings applied (Task 3).** Every reading of the Control section applies: Review by table, Another name, Carried
citation, Pending bullet, Item by description, Date and Stage 2's live feed. Two readings are new, and the controller has
not confirmed either. Each was set when a close call first appeared in a reply, and then applied to every rep of its case.
The Conditional handoff reading is counted in the scores, and it changes no verdict. The Name reading is not counted: the
scores follow the rule text. Each one's other reading is reported under "Other readings" in its case, and the other
reading never counts toward a bar.

- *Name* (clause C of dr-stop-track and dr-park-ranked; proposed, not confirmed, and not counted). The rule's note allows
  "the file's stem or its title in kebab case". The stem of `specs/lock-closures-roadmap.md` is `lock-closures-roadmap`,
  and its title in kebab case is `lock-closures-and-river-levels`. A heading that carries `lock-closures` is neither, so it
  fails C by the rule text. The scores below follow the rule text. The proposed reading is the other reading: SKILL.md §5
  gives the heading as `## <roadmap-name> — <YYYY-MM-DD>`, and `references/new-project-entry.md` item 4 defines a roadmap
  name as "the `<name>` in `specs/<name>-roadmap.md`", which is `lock-closures` for this file. By the proposed reading
  the heading passes. It never counts toward a bar. It decides dr-park-ranked's bar, so the controller may rule on it.
  The headings: dr-stop-track reps 1, 2 and 3 and dr-park-ranked reps 1, 2 and 5 carry `lock-closures`. No control rep
  used it, and the `1844bd8` control prompt lacks the definition of a roadmap name.
- *Conditional handoff* (dr-stop-track clause E; new, not confirmed). A rep that writes a full "Next:" line that names
  writing-plans and the roadmap, and plans nothing, passes E when the line is conditional on a fact that no clause scores
  (here, whether the live feed exists). Stage 2's live feed is such a fact, so scoring it through E would score the feed.
  A reply that asks a question and writes no "Next:" line fails E. Other reading: a conditional line is no handoff, so E
  fails in dr-stop-track reps 3, 4 and 5.

**Judgment-call reps.** Each rep below was scored on a close reading. The owner can review them at the completion gate.
The quote column gives the other reading's effect where it changes a count.

| Case, rep, clause | Score | Deciding quote |
|---|---|---|
| dr-stop-track reps 1, 2 and 3, C | fail (by the rule's allowed names; the proposed Name reading would pass) | "## lock-closures — 2026-11-06". The proposed Name reading passes C in these reps, so C is 5 of 5 and PASS is 3 of 5. The bar is missed on either reading. |
| dr-stop-track reps 3, 4 and 5, E | pass, borderline (the Conditional handoff reading) | rep5: "If you know it is live, the handoff is: Next: /clear (or a fresh session), then writing-plans on Stage 2 of `specs/lock-closures-roadmap.md`." The other reading fails E in these reps, so E is 0 of 5 and PASS is 0 of 5. The bar is missed on either reading. |
| dr-stop-track reps 1 and 2, E | fail (a question and no "Next:" line) | rep1: "So Stage 2's `Consumes` is unmet, and I won't hand it off until that is settled." |
| dr-park-ranked reps 1, 2 and 5, C | fail (by the rule's allowed names; the proposed Name reading would pass) | "## lock-closures — 2026-11-06". The proposed Name reading passes C in these reps, so C and PASS are 5 of 5 and the bar is met. The verdict depends on this reading. |
| dr-name-collision rep2, B | pass, borderline (a named other path as the default of a question about the file) | "I'll leave that file alone and write this roadmap to `specs/sec-filing-index-ingestion-roadmap.md`, which is free." The other reading fails B, which makes B and PASS 3 of 5, and the bar is missed. The verdict depends on this reading. |
| dr-name-collision rep3, B | fail, borderline (the recommended answer moves the old file) | "**(a) My recommendation:** you rename the Filing alerts roadmap to match its own project". The other reading passes B, which makes B and PASS 5 of 5. |
| dr-name-collision reps 2 and 3, C | pass, borderline (a statement of source, with a hedge) | rep2: "I don't think it belongs to this spec"; rep3: "Because it doesn't name this spec as its source, it isn't a roadmap for this spec". The committed note passes any statement that the file's source is not this spec. |
| dr-resume-marker reps 1, 2 and 5, B | pass (old citation carried over) | rep5: "Consumes: Stage 1's `bay_events` table, with the car park in its `lot_id` column (plan 3, Handoff; Resolved at resume, 2026-10-12); Stage 2's `occupancy_by_hour` table (plan 5, Handoff; Resolved at resume, 2026-11-07)". The other reading fails B in these reps, so B and PASS are 2 of 5. |
| dr-park-ranked reps 3, 4 and 5, D | pass (a draft, written in full) | rep4: "The wording below is a draft and will be fitted to the schema's exact fields once I've read it." Each item has its `Size:` and `Done when:`, so the Item by description reading does not fail D. |
### Plan 79 Task 3: dr-stop-track

Additive. Texts at `c500e14` (`T3`). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.3619.

The partner answers "Stop Track A" in a roadmap with two tracks. Clause A (bar) appends one item each for O2, O3 and O4
to `specs/deferred_items.md` and none for Stage 2 or O5. Clause B (bar) keeps the roadmap live. Clause C (conformance)
puts the items under one dated heading. Clause D (conformance) gives each item a `Size:` and a `Done when:`. Clause E
(conformance) hands off Stage 2 with a "Next:" line and starts no completion review.

| Rep | A (bar) | B (bar) | C (conformance) | D (conformance) | E (conformance) | PASS |
|---|---|---|---|---|---|---|
| 1 | pass | pass | fail (name) | pass | fail | no |
| 2 | pass | pass | fail (name) | pass | fail | no |
| 3 | pass | pass | fail (name) | pass | pass (borderline, conditional) | no |
| 4 | pass | pass | pass | pass | pass (borderline, conditional) | yes |
| 5 | pass | pass | pass | pass | pass (borderline, conditional) | yes |

Clause A: 5 of 5 (control 0 of 5). Clause B: 5 of 5 (control 5 of 5). Clause C: 2 of 5 (control 0 of 5; 5 of 5 by the
proposed Name reading). Clause D: 5 of 5 (control 0 of 5). Clause E: 3 of 5 (control 5 of 5; 0 of 5 by the other reading
of a conditional handoff). PASS: 2 of 5 (control 0 of 5; 3 of 5 by the proposed Name reading, 0 of 5 by the other
reading of a conditional handoff).

**Bar verdict: MISSED.** The additive bar needs 4 of 5 passing reps and a control that fails a bar clause. The control
fails clause A in 5 of 5, so the control half holds. The treatment passes 2 of 5, below 4 of 5. It misses the bar on
every reading of the two close calls (2, 3 or 0 of 5). Clause A, the bar clause that the route targets, is fixed: 5 of 5
against 0 of 5. The misses are in conformance clauses: E (reps 1 and 2) and C (reps 1, 2 and 3).

- A passes in every rep. Each rep writes three items, one each for O2, O3 and O4, as the content of an edit to
  `specs/deferred_items.md`, and none for Stage 2 or O5. Rep3 and rep5 call their text a sketch or "not the final form" and
  still write each item's text, so the items count (the committed note for clause A).
- B passes in every rep. Each rep replaces the body of `## Ranked list — Track A` with a stop note, commits, and leaves
  Stage 2's entry, the header and the stamp as they are. None moves the roadmap or marks it PARKED. Rep1 also proposes to
  amend Stage 2's `Consumes`, which keeps the entry.
- C fails in reps 1, 2 and 3 by the rule's allowed names. They head the section `## lock-closures — 2026-11-06`, which is
  neither the file's stem nor its title in kebab case. Reps 4 and 5 head it `## lock-closures-roadmap — 2026-11-06` and
  pass. All five use 2026-11-06, so the Date reading does not apply. See the proposed Name reading below.
- D passes in every rep. Each item has a `Size:` and a `Done when:` that names its outcome, for example rep1's O4 item:
  "Done when: boat operators can open a map of each lock's closure history." Rep3 and rep4 add a `Context:` line, which no
  clause forbids.
- E fails in reps 1 and 2. Both put one question about Stage 2's `Consumes` and hand off nothing. This is the watch item and
  the new Ask text is its cause (see below). Reps 3, 4 and 5 write a "Next:" line and no completion review, but each makes
  the handoff conditional (see the new Conditional handoff reading below).
- No rep starts a completion review. Reps 1 and 2 hand nothing off.

**What drove the failures.** The two causes are different.

*E, reps 1 and 2.* Both failing reps apply the new Ask text (edit 2), not the old text. Quote (E, rep1): "So Stage 2's `Consumes` is unmet, and I won't hand it off until that is settled." Rep1 then asks "Approve the amended `Consumes`, or amend it (for example, add the feed stage)?" Quote (E, rep2): "That leaves Stage 2 with an unmet `Consumes` and nothing ready to hand off." Rep2 then offers a default and ends "Approve, or amend:". In the control, no rep asked. Reps 1, 2 and 4 treated the feed as unconfirmed and passed it on, and reps 3 and 5 found it met. The three reps that hand off still name the feed (rep3: "Before handing off Stage 2, I'll confirm its `Consumes` is met"; rep4: "If it doesn't, I'll stop and ask one question first"; rep5: "If the feed doesn't exist yet, tell me. Then nothing gets handed off"). So the new Ask text, "none has all its `Consumes` met ... Hand off nothing before the answer", moved all five reps from "met" or "pass it on" to "check it first". Stage 2's `Consumes` is the closure log's live feed. No stage produces it. The new text has no rule for a `Consumes` that comes from outside the roadmap. This is my read, not a measured result.

*C, reps 1, 2 and 3.* No edit of Task 3 touches the heading. The §5 Parking text gives `## <roadmap-name> — <YYYY-MM-DD>`,
and the treatment prompt also defines a roadmap name as "the `<name>` in `specs/<name>-roadmap.md`" (in
`references/new-project-entry.md`). The `1844bd8` control prompt lacks that definition, and every control heading of
dr-park-ranked used the stem `lock-closures-roadmap`. The reps that wrote `lock-closures` read the skill's own definition
literally, so the heading form is under-specified for a roadmap whose file ends in `-roadmap`. This is my read.

**New readings (Task 3, not yet confirmed by the controller).**

- *Name* (clause C of dr-stop-track and dr-park-ranked; proposed, not counted). See "Readings applied (Task 3)" above. The
  scores follow the rule text, so reps 1, 2 and 3 fail C. The proposed reading passes them: C becomes 5 of 5 and PASS 3 of 5.
  It does not change this case's verdict.
- *Conditional handoff* (dr-stop-track clause E). A rep that writes a full "Next:" line that names writing-plans and the
  roadmap, and plans nothing, passes E when the line is conditional on a fact that no clause scores (here, whether the live
  feed exists). Stage 2's live feed is such a fact, so scoring it through E would score the feed. A reply that asks a
  question and writes no "Next:" line fails E (reps 1 and 2). Other reading: a conditional line is no handoff, so E fails in
  reps 3, 4 and 5, E is 0 of 5, and PASS is 0 of 5.

Running total: $2.1384 of $30.
### Plan 79 Task 3: dr-park-ranked

Additive. Texts at `c500e14` (`T3`). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.3357.

The partner answers "Park the whole roadmap" in the same roadmap. Clause A (bar) appends four items, one each for Stage 2,
O2, O3 and O4. Clause B (bar) moves the roadmap to `specs/completed/` marked PARKED with the date and "1 of 2 stages
complete". Clause C (conformance) puts the items under one heading `## <roadmap name> — 2026-11-06`. Clause D
(conformance) gives each item a `Size:` and a `Done when:`. Clause E (conformance) starts no completion review and hands
off no stage.

| Rep | A (bar) | B (bar) | C (conformance) | D (conformance) | E (conformance) | PASS |
|---|---|---|---|---|---|---|
| 1 | pass | pass | fail (name) | pass | pass | no |
| 2 | pass | pass | fail (name) | pass | pass | no |
| 3 | pass | pass | pass | pass | pass | yes |
| 4 | pass | pass | pass | pass | pass | yes |
| 5 | pass | pass | fail (name) | pass | pass | no |

Clause A: 5 of 5 (control 0 of 5). Clause B: 5 of 5 (control 5 of 5). Clause C: 2 of 5 (control 4 of 5; 5 of 5 by the
proposed Name reading). Clause D: 5 of 5 (control 4 of 5). Clause E: 5 of 5 (control 5 of 5). PASS: 2 of 5 (control 0
of 5; 5 of 5 by the proposed Name reading).

**Bar verdict: MISSED.** The additive bar needs 4 of 5 passing reps and a control that fails a bar clause. The control
fails clause A in 5 of 5, so the control half holds. The treatment passes 2 of 5, below 4 of 5. Clause A and clause B,
the bar clauses, pass in 5 of 5. The miss is in clause C, a conformance clause, in reps 1, 2 and 5. Quote (C, rep1):
`## lock-closures — 2026-11-06`. By the proposed Name reading (see dr-stop-track, New readings), the heading passes and
PASS is 5 of 5, so the bar would be met. The controller has not confirmed that reading, and it never counts toward a bar.

**What drove the miss.** None of Task 3's five edits touches the heading. The §5 Parking text gives
`## <roadmap-name> — <YYYY-MM-DD>`, and the treatment prompt also defines a roadmap name as "the `<name>` in
`specs/<name>-roadmap.md`" (in `references/new-project-entry.md`). The `1844bd8` control prompt lacks that definition,
and every control heading used the stem `lock-closures-roadmap`. The reps that wrote `lock-closures` read the skill's own
definition literally. This is my read. A wording change to the §5 Parking heading reaches dr-stop-track and dr-park-ranked.
`references/new-project-entry.md` is in the Leave-alone list, so only the §5 text is open.

- A passes in every rep. Each rep writes four items as the content of an edit to `specs/deferred_items.md`: one for
  Stage 2 (the notices), and one each for O2, O3 and O4. The control wrote one in every rep. Rep3, rep4 and rep5 offer
  to add text-message notices as a fifth item only if asked, which writes no extra item.
- B passes in every rep. Each rep runs `git mv specs/lock-closures-roadmap.md specs/completed/lock-closures-roadmap.md`
  and adds a PARKED line with 2026-11-06 and "1 of 2 stages complete". Quote (B, rep2): "PARKED (2026-11-06) — 1 of 2
  stages complete." No rep counts a list item as a stage.
- C fails in reps 1, 2 and 5 by the rule's allowed names. They head the section `## lock-closures — 2026-11-06`, which is
  neither the file's stem nor its title in kebab case. Reps 3 and 4 head it `## lock-closures-roadmap — 2026-11-06` and
  pass. All five use 2026-11-06, so the Date reading does not apply.
- D passes in every rep. Each of the four items per rep has a `Size:` line and a `Done when:` line. The Stage 2 item names
  the notice job and its operator mailing list or the test's outcome, and the three Ranked-list items name their
  outcomes. Reps 3, 4 and 5 call their text a draft or a sketch, and write each item in full, so the Item by description
  reading does not fail D.
- E passes in every rep. No rep starts a completion review and none hands off a stage. Quote (E, rep2): "Nothing is
  handed off." Rep1: "nothing else is routed or handed off."
- Stage 2's live feed. No rep treats it as unmet or asks about it. Reps 1, 2, 3, 4 and 5 carry it into the Stage 2 item
  as its source, for example rep1: "from the closure log's live feed". The new Ask text did not touch a parked roadmap,
  because the park hands nothing off and asks nothing.

Other readings: Name (above): PASS 5 of 5 and the bar met. Date: no effect. Item by description: no effect.

Running total: $2.4741 of $30.
### Plan 79 Task 3: dr-name-collision

Additive. Texts at `c500e14` (`T3`). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.3633.

The roadmap name would be the spec's stem, and a file with that name exists with another source. Clause A (bar) does not
write that file. Clause B (bar) asks the partner for another name and writes no roadmap file before the answer. Clause C
(conformance) says that the existing file is not this spec's roadmap and does not resume it.

| Rep | A (bar) | B (bar) | C (conformance) | PASS |
|---|---|---|---|---|
| 1 | pass | pass | pass | yes |
| 2 | pass | pass (borderline) | pass (borderline) | yes |
| 3 | pass | fail (borderline) | pass (borderline) | no |
| 4 | pass | pass | pass | yes |
| 5 | pass | pass | pass | yes |

Clause A: 5 of 5 (control 5 of 5). Clause B: 4 of 5 (control 0 of 5; 3 of 5 by the other reading of rep2, 5 of 5 by the
other reading of rep3). Clause C: 5 of 5 (control 4 of 5). PASS: 4 of 5 (control 0 of 5; 3 of 5 by the other reading of
rep2, 5 of 5 by the other reading of rep3).

**Bar verdict: MET, narrowly.** The treatment passes 4 of 5, which is the bar, and the control fails clause B in 5 of 5.
The verdict rests on one borderline call: rep2's clause B. If it is read the other way, PASS is 3 of 5 and the bar is
missed. If rep3's clause B is read the other way, PASS is 5 of 5.

- A passes in every rep. None writes `specs/sec-filing-index-ingestion-spec-roadmap.md`, and each says it will not
  overwrite it. None writes a roadmap under any name before the answer.
- B. Reps 1, 4 and 5 ask for another name for this roadmap. Rep1's one question is "where should this roadmap go?", and
  its recommended answer is "Write it to `specs/sec-filing-index-ingestion-roadmap.md`." Rep4 asks "A name for this
  roadmap. I propose `specs/sec-filing-index-ingestion-roadmap.md` ... Any other kebab-case name works too." Rep5
  recommends "A different name for this roadmap", with the same example. In the control no rep asked for a name, and every
  rep asked what the file was or proposed to move it.
- B, rep2, pass and borderline. Its question is about something else: "Is 'Filing alerts' a separate project that ended up
  in this repo?" Its default is a named other path: "I'll leave that file alone and write this roadmap to
  `specs/sec-filing-index-ingestion-roadmap.md`, which is free." It writes nothing before the confirmation. The Another
  name reading says that a branch that offers a different name "which you'd pick" inside a question about something else
  does not count. The rule's reading note says that a name proposed inside the question passes. Rep2 proposes a specific
  name as the question's default and waits for a confirmation, so it is scored as a pass.
- B, rep3, fail and borderline. Its one question is "how should I resolve the name?" Its recommendation is that the
  partner renames the Filing-alerts file to `specs/filing-alerts-roadmap.md`, so that this roadmap can take the spec's
  stem. A different name for this roadmap is only the alternative: "(b) Leave that file alone and give this roadmap a
  different name, for example `specs/sec-filing-index-ingestion-roadmap.md`." The Another name reading says a proposal
  to move the old file is not the request. This is the failure mode of the control.
- C passes in every rep. Each says that the file is not this spec's roadmap and none resumes it. Reps 2 and 3 hedge as in
  the control: rep2 "I don't think it belongs to this spec", with "I've only read its first 12 lines"; rep3 says that it
  "doesn't name this spec as its source, it isn't a roadmap for this spec", and plans to read the rest to confirm. The
  committed note passes any statement that the file's source is not this spec.
- Untracked file. All five reps again reason from `git ls-files` that the file is untracked, and say that an overwrite
  cannot be undone. Rep4 corrects its earlier claim that no file carried the roadmap header. Rep5 adds that the file is
  uncommitted and advises a commit. Clause A passes in 5 of 5, as in the control.
- Source of the change. The name rule that the treatment follows (the spec's stem, §3's scan, and "ask for another name")
  was added by plan 78's Task 7 commit `f824492`. The control reads `1844bd8`, before that rule. None of Task 3's five edits
  touches it, except that the §7 step 4 edit says "with no spec". So the gain over the control is not evidence for the five
  edits.

Other readings: Another name. Rep2's B read the other way gives B 3 of 5 and PASS 3 of 5 (bar missed). Rep3's B read the
other way gives B 5 of 5 and PASS 5 of 5. Neither is counted.

Running total: $2.8374 of $30.
### Plan 79 Task 3: dr-rerank-second

Additive. Texts at `c500e14` (`T3`). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.3159.

A second re-rank question, after Stage 2 (the 7-day outlook) is ticked and stamped. Clause A (bar) starts no completion
review and does not park or retire the roadmap. Clause B (bar) reports Stage 2's finding and its measured cost. Clause C
(bar) is one question with a default that asks for a re-ranking of O3 and O4 or approval of a proposed next stage.
Clause D (conformance) writes no stage entry and does not offer O2 again.

| Rep | A (bar) | B (bar) | C (bar) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | yes |
| 2 | pass | pass | pass | pass | yes |
| 3 | pass | pass | pass | pass | yes |
| 4 | pass | pass | pass | pass | yes |
| 5 | pass | pass | pass | pass | yes |

Clause A: 5 of 5 (control 2 of 5). Clause B: 5 of 5 (control 2 of 5). Clause C: 5 of 5 (control 5 of 5). Clause D: 5 of 5
(control 5 of 5). PASS: 5 of 5 (control 1 of 5).

**Bar verdict: MET.** The treatment passes every clause in 5 of 5 reps, and the control fails a bar clause in 4 of 5.

- A passes in every rep. Each rep says that this is a re-rank and not the completion review, for example rep4: "That
  means this resume goes to a re-rank, not to the completion review." No rep gives a table over the Outcomes list, so the
  Review by table reading has nothing to score. Each names a stop only as an alternative, with the parking that follows
  it. None parks or retires the roadmap.
- B passes in every rep, and each gives both parts. Rep1: "The 7-day outlook flagged 81% of closures at least 2 days
  ahead, with one false alarm in 9." and "Measured cost: 14 minutes a day on one small VM, using 0.3 GB of forecasts."
  Every rep reads the findings file of Stage 2, the most recently ticked stage, and not Stage 1's alone. Reps 2 to 5 also
  use Stage 1's results to read O3's cost.
- C passes in every rep. Each puts one approve-or-amend question with the default "keep the order and promote O3 as the
  next stage". Rep4 offers "promote O4 instead, re-order the list, or stop the track" as the alternatives, inside the
  one question.
- D passes in every rep. Each describes the stage that it would add, and says that it writes the entry after the answer
  ("I'll add the stage entry and hand it off once you answer", rep1). No rep offers O2 again. Rep3 mentions O2's "small"
  estimate once, as a comparison for the measured cost, and proposes nothing for O2.
- Source of the change. The rule that a re-rank reads the findings of the most recently ticked stage was added by plan 78's
  Task 7 commit `f824492` (its edit 3). The control reads `1844bd8`, before that rule. None of Task 3's five edits touches
  it. The gain over the control is not evidence for the five edits.

Other readings: Review by table: no effect, no rep has a table. No other reading applies.

Running total: $3.1532 of $30.
### Plan 79 Task 3: dr-resume-marker

Additive. Texts at `c500e14` (`T3`). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.2968.

Stage 3's entry already cites plan 3's Handoff, marked "Resolved at resume, 2026-10-12". Only plan 5's Handoff bullet is
new. Clause A (bar) amends the Consumes of Stage 3 and Stage 4 from plan 5's bullet and cites plan 5, Handoff. Clause B
(bar) does not apply or restate plan 3's bullet again. Clause C (conformance) commits and hands off Stage 3 with a
"Next:" line and plans nothing.

| Rep | A (bar) | B (bar) | C (conformance) | PASS |
|---|---|---|---|---|
| 1 | pass | pass (borderline, carried citation) | pass | yes |
| 2 | pass | pass (borderline, carried citation) | pass | yes |
| 3 | pass | pass | pass | yes |
| 4 | pass | pass | pass | yes |
| 5 | pass | pass (borderline, carried citation) | pass | yes |

Clause A: 5 of 5 (control 5 of 5). Clause B: 5 of 5 (control 5 of 5; 2 of 5 by the other reading, control 3 of 5).
Clause C: 5 of 5 (control 5 of 5). PASS: 5 of 5 (control 5 of 5; 2 of 5 by the other reading, control 3 of 5).

**Bar verdict: control clean: owner gate.** The control fails no clause, so the additive bar cannot be met. The treatment
passes in 5 of 5 reps, which is not fewer than 4 of 5, so it does not miss its bar. The treatment reverts nothing and
adds nothing that this case can measure. The clean control goes to the owner at the plan completion gate.

- A passes in every rep. Each amends both entries to `occupancy_by_hour`. Each cites "plan 5, Handoff", with the Resolved
  marker. Quote (A, rep4): "new: Stage 2's table, shipped as `occupancy_by_hour` (plan 5, Handoff; Resolved at resume,
  2026-11-06)".
- B passes in every rep. Each rep says that plan 3's point is already in Stage 3 and changes nothing for it. Quote
  (rep3): "Stage 3's `Consumes` already cites its Handoff, which says to read the car park from `lot_id` (resolved at
  resume, 2026-10-12). Nothing new." Reps 1, 2 and 5 write out the whole new Stage 3 `Consumes` line, with plan 3's citation
  carried over unchanged. That is the Carried citation reading. Rep2's table says "Already cited? Yes ... Action None."
  Reps 3 and 4 show only the changed part of the line.
- C passes in every rep. Each commits the amendments on `main` as text and ends with "Next: /clear (or a fresh session),
  then brainstorming on Stage 3 of `specs/parking-occupancy-spec-roadmap.md`." and plans nothing.
- The new text at work. Each rep tests the marker the way that the new SKILL.md §5 states it. Rep1: "no entry cites its
  Handoff yet". Rep3: "no entry cites its Handoff yet". Rep5: "No entry cites its Handoff yet." In the control the reps
  placed the last resume from the Resolved marker. The result is the same: 5 of 5.
- The new Ask text did not fire. No rep treats `occupancy_hourly` as unmet, because each amends the `Consumes` to
  `occupancy_by_hour`. Each says there is nothing to ask. Rep4: "Both unticked stages have their `Consumes` met."
- Dates. Reps 1 and 4 date the new marker 2026-11-06, and reps 2, 3 and 5 date it 2026-11-07. Reps 1, 2 and 3 say that the
  session and the environment disagree. No clause scores the date.

Other readings: Carried citation. If a Stage 3 line that carries plan 3's citation fails B, B fails in reps 1, 2 and 5,
and B and PASS are 2 of 5. That reading applies to the control too, where it gives 3 of 5. It is not counted.

Running total: $3.4501 of $30.
### Plan 79 Task 3: dr-resume-blocked

Additive. Texts at `c500e14` (`T3`). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.3543.

Plan 5's Handoff says that `occupancy_hourly` was not built, and Stage 3 and Stage 4 consume it. Plan 3's bullet is still
pending. Clause A (bar) hands off no stage before the answer. Clause B (bar) is one question that names the unmet
Consumes and the stages that it blocks, with a proposed default. Clause C (conformance) has a default that adds a stage
that produces the table or amends the Consumes. Clause D (conformance) starts no completion review and parks nothing.

| Rep | A (bar) | B (bar) | C (conformance) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | yes |
| 2 | pass | pass | pass | pass | yes |
| 3 | pass | pass | pass | pass | yes |
| 4 | pass | pass | pass | pass | yes |
| 5 | pass | pass | pass | pass | yes |

Clause A: 5 of 5 (control 5 of 5). Clause B: 5 of 5 (control 5 of 5). Clause C: 5 of 5 (control 5 of 5). Clause D: 5 of 5
(control 5 of 5). PASS: 5 of 5 (control 5 of 5).

**Bar verdict: control clean: owner gate.** The control fails no clause, so the additive bar cannot be met. The treatment
passes in 5 of 5 reps, which is not fewer than 4 of 5, so it does not miss its bar. The treatment reverts nothing. The
clean control goes to the owner at the plan completion gate.

- A passes in every rep. Each says that no stage can be handed off yet, and none writes a "Next:" line. Quote (A, rep3):
  "I'll hand off nothing until you answer." Rep2 mentions a later "Next:" line, which it gives after the answer, and
  names no stage in it. No rep commits before the answer. Each says that it commits with what the partner approves.
- B passes in every rep. Each puts one approve-or-amend question, with a default that adds a stage, and names
  `occupancy_hourly` and Stages 3 and 4. Quote (B, rep1): "The unmet `Consumes` is Stage 2's `occupancy_hourly` table,
  which blocks Stage 3 (dashboard and alerts) and Stage 4 (weekly report)." Other paths sit inside the one question as
  alternatives: amending the `Consumes` (reps 1 to 4), and dropping or reordering stages (rep5).
- C passes in every rep. The default adds a stage that produces `occupancy_hourly`: Stage 2a in rep1, Stage 2b in rep4,
  and one new stage before Stage 3 in reps 2, 3 and 5. Rep4 also marks both `Consumes` as "not built", which is not
  scored.
- D passes in every rep. No rep starts a completion review. Rep1 sends R4 "back to the spec" only as the outcome of a
  failed investigation stage, which is not a park.
- Plan 3's pending bullet. All five apply it as an amendment (the `lot_id` column), and none scores. Reps 1, 2, 3 and 5
  date it 2026-11-07, and rep4 dates it 2026-11-06.
- The new text at work. Each rep tests the marker as the new §5 states it ("no entry cites either plan's Handoff yet",
  reps 2, 3, 4 and 5; "Handoffs that no entry cites yet", rep1). Reps 1, 4 and 5 use the new Ask wording for the
  blocked state: rep1 "no unticked stage has all its `Consumes` met", rep4 "no unticked stage has all its `Consumes` met", and rep5
  "every unticked stage has an unmet `Consumes`". The control reps took the same steps from the old text, and the
  case is clean in both arms.

Other readings: Pending bullet: no effect. No other reading applies.

Running total: $3.8043 of $30.

### Plan 79 Task 3 summary and spend

| Case | Bar | Control (`1844bd8` or `5beacf5`) | Treatment (`T3`, `c500e14`) | Result |
|---|---|---|---|---|
| dr-stop-track | additive | RED, A fails 5 of 5 (PASS 0 of 5) | PASS 2 of 5 (3 of 5 by the proposed Name reading, 0 of 5 by the other Conditional handoff reading) | **MISSED** (needs 4 of 5) |
| dr-park-ranked | additive | RED, A fails 5 of 5 (PASS 0 of 5) | PASS 2 of 5 (5 of 5 by the proposed Name reading) | **MISSED** (needs 4 of 5) |
| dr-name-collision | additive | RED, B fails 5 of 5 (PASS 0 of 5) | PASS 4 of 5 (3 of 5 by the other reading of rep2, 5 of 5 by the other reading of rep3) | **MET**, narrowly |
| dr-rerank-second | additive | RED, a bar clause fails in 4 of 5 (PASS 1 of 5) | PASS 5 of 5 | **MET** |
| dr-resume-marker | additive | clean (PASS 5 of 5) | PASS 5 of 5 (2 of 5 by the other Carried citation reading) | control clean: owner gate; not below 4 of 5 |
| dr-resume-blocked | additive | clean (PASS 5 of 5) | PASS 5 of 5 | control clean: owner gate; not below 4 of 5 |

No rep was VOID.

**The misses: dr-stop-track and dr-park-ranked.** Both treatments fix clause A, the bar clause that the route targets (5 of
5 against 0 of 5 in each). Both miss the bar through conformance clauses, and the bar needs every clause in 4 of 5 reps.

*dr-stop-track.* Failing clauses: E (reps 1 and 2) and C (reps 1, 2 and 3). PASS is 2 of 5.

- E. Reps 1 and 2 ask about Stage 2's `Consumes` and hand off nothing. Reps 3, 4 and 5 pass E only on the Conditional
  handoff reading, and on the other reading E fails in all 5 reps. Quotes. Rep1: "So Stage 2's `Consumes` is unmet, and I
  won't hand it off until that is settled." Rep2: "That leaves Stage 2 with an unmet `Consumes` and nothing ready to
  hand off." Rep4, as a condition: "If it doesn't, I'll stop and ask one question first."
- Which text drove E (my read, not a measured result): edit 2, the new sentence in the §5 Ask bullet, "When unticked
  stages remain and none has all its `Consumes` met, the same question names each unmet `Consumes` and the stages it
  blocks ... Hand off nothing before the answer." Stage 2's `Consumes` is "the closure log's live feed", and no stage
  produces it. In the control, no rep asked about it: reps 3 and 5 found it met, and reps 1, 2 and 4 passed the check to
  the writing-plans session and handed off. The new sentence says nothing about a `Consumes` that comes from outside the
  roadmap, so the reps read the feed as unmet. This is the watch item that the brief named, and it is confirmed.
- C. Reps 1, 2 and 3 head the deferred-items section `## lock-closures — 2026-11-06`. See dr-park-ranked below for the cause.
- Other readings do not rescue it. By the proposed Name reading, PASS is 3 of 5. By the strict Conditional handoff reading,
  PASS is 0 of 5.

*dr-park-ranked.* Failing clause: C, in reps 1, 2 and 5. PASS is 2 of 5. Quote: `## lock-closures — 2026-11-06`.

- Which text drove it (my read): none of the five edits. The §5 Parking text gives `## <roadmap-name> — <YYYY-MM-DD>`.
  The treatment prompt also defines a roadmap name as "the `<name>` in `specs/<name>-roadmap.md`" (in
  `references/new-project-entry.md`), which is `lock-closures` for this file. The `1844bd8` control prompt lacks that
  definition, and every control heading used the stem `lock-closures-roadmap`. The reps that wrote `lock-closures` read the
  skill's own definition literally. This is the same cause as dr-stop-track's clause C.
- By the proposed Name reading, the heading passes and PASS is 5 of 5, so the bar would be met. That reading is not
  confirmed and never counts toward a bar. The controller may rule on it before the wording round.

*Reach of a wording change.* The Ask bullet decides dr-stop-track, dr-resume-marker and dr-resume-blocked. It does not
reach dr-park-ranked (a park asks nothing and hands off nothing), dr-name-collision (the reply stops at the name) or
dr-rerank-second (its question has no unmet `Consumes`). The §5 Parking heading form decides dr-stop-track and
dr-park-ranked. `references/new-project-entry.md` is in the Leave-alone list, so only the §5 text is open to the round.

**One met bar is borderline.** dr-name-collision is met by rep2's clause B. It proposes a named other path as the default of a
question about what the old file is. By the other reading PASS is 3 of 5 and the bar is missed. By the other reading of
rep3, PASS is 5 of 5.

**The route gains do not come from the five edits.** The text at `T3` carries the park and stop rules, the name rule and
the most-recent-findings rule that plan 78 added, and the four route controls read `1844bd8`, before them. A check of
`SKILL.md` at the three commits shows the stop and park text ("only the items of that track's Ranked list append, one item
per list item") absent at `1844bd8` and present at `5beacf5` and at `T3`. So the gains in dr-stop-track and dr-park-ranked
(clause A), dr-name-collision (clause B) and dr-rerank-second (clauses A and B) come from that earlier text. Only the E
failures of dr-stop-track trace to one of Task 3's five edits. The C failures of dr-stop-track and dr-park-ranked trace to
the heading wording, not to an edit.

**The clean resume-gap controls.** dr-resume-marker and dr-resume-blocked are clean in the control, so the additive bar
cannot be met and the treatment reverts nothing. The treatment passes 5 of 5 in each. In dr-resume-marker no rep
treats the renamed table as an unmet `Consumes`: each amends it, so the new Ask text did not fire there. Both cases go to
the owner at the plan completion gate, with the Task 2 note.

**Spend.** `uv run python specs/red-baseline-new-project-entry/kit/show_reps.py` ran once over each of the six `-p79`
folders after its last rep, and once over all six together (30 reps, none VOID, `total cost $2.03`). No rep file is empty
or unreadable, so none counts at its cap. There was no VOID rerun. The figures per case, from each rep's
`total_cost_usd`, are dr-stop-track $0.3619, dr-park-ranked $0.3357, dr-name-collision $0.3633, dr-rerank-second $0.3159,
dr-resume-marker $0.2968 and dr-resume-blocked $0.3543. Task 3 cost $2.0278. Running total: $3.8043 of $30.

No wording round was started. dr-stop-track and dr-park-ranked missed their bars, so the controller dispatches the wording
round to a stronger tier. The cases' rules are unchanged.

## Plan 79: Task 3 wording round 1

At `T3`, two treatments missed their bar: dr-stop-track and dr-park-ranked each passed 2 of 5. The Bars give one wording
round, with each case's rule unchanged. This round rewords two passages of skill text, re-runs every case of Task 3 whose
decision the new text can reach, and scores each rep by hand from its full reply. No fixture, rule or `cases.py` line
changed.

**`T3-r1` is `43fca10`**, the full sha `43fca109af87f13d9ec04f905d7d78dc628f755c`, subject `fix(derive-roadmap): scope the
blocked-roadmap ask and name the parking heading`. It follows `3aad784` and changes two files:
`skills/derive-roadmap/SKILL.md` (§5 only) and `skills/derive-roadmap/references/roadmap-format.md` (the one sentence of
Task 3's edit 4). No description changed. No example and no fixture detail is in the new text.

**Diagnosis, checked against the `T3` replies.**

1. dr-stop-track clause E. The `T3` Ask sentence starts "When unticked stages remain and none has all its `Consumes` met".
   Stage 2's `Consumes` is an input from outside the roadmap: no stage's `Produces` names it. The text had no rule for
   such an input. Reps 1 and 2 read it as unmet, asked, and handed off nothing (rep1: "So Stage 2's `Consumes` is unmet,
   and I won't hand it off until that is settled."). Reps 3, 4 and 5 made the handoff conditional on the feed (rep4: "If
   it doesn't, I'll stop and ask one question first."). The diagnosis holds.
2. Clause C of both cases. The `T3` Parking text gives the heading as `## <roadmap-name> — <YYYY-MM-DD>`. The
   reference `new-project-entry.md` item 4 calls `<name>` the roadmap name ("a proposed roadmap name, the `<name>` in
   `specs/<name>-roadmap.md`"). Every failing heading reads `## lock-closures — 2026-11-06`, which is `<name>` and not
   the file's stem. The diagnosis holds.

**Passage 1: the Ask bullet, `SKILL.md` §5.**

Old text (`T3`), from its fourth sentence:

> When unticked stages remain and none has all its `Consumes` met, the same question names each unmet `Consumes` and the
> stages it blocks, with your proposed default: a stage added to produce it, or the `Consumes` amended. Hand off nothing
> before the answer. Name no stage's routing in it; route only after the answer.

New text (`T3-r1`):

> When unticked stages remain and none has all its `Consumes` met, the same question names each unmet `Consumes` (one
> that an earlier stage was to produce and, as its Handoff or stamp shows, did not) and the stages it blocks, with your
> proposed default: a stage added to produce it, or the `Consumes` amended. Hand off nothing before the answer. Name no
> stage's routing in it; route only after the answer. A `Consumes` that no stage's `Produces` names comes from outside
> the roadmap: it counts as met, and the receiving session checks it.

Why this wording:

- The parenthetical ties the question to what shipped. It qualifies what the question names. It is not the only meaning
  of "unmet", so a stage that consumes the output of an unticked stage still waits.
- The outside input is named by the `Produces` fields, not by "no stage produces it". In dr-resume-blocked no stage
  produced `occupancy_hourly`, but Stage 2's `Produces` names it. The looser phrase could let a reply call that table
  external and hand off Stage 3.
- "It counts as met" lets §4's rule, "the first unticked one whose `Consumes` are all met", hand off as before, with no
  edit to §4.
- The new sentence comes after "Name no stage's routing in it", so that "it" still means the question.

**Passage 2: the Parking heading, `SKILL.md` §5.** Both `## <roadmap-name> — <YYYY-MM-DD>` become
`## <name>-roadmap — <YYYY-MM-DD>`.

Why this wording:

- `<name>-roadmap` is the stem of `specs/<name>-roadmap.md`, built from the `<name>` that §3 defines. So the heading
  names the roadmap file by its stem.
- The edit adds no character to the body.
- A sentence in §5 that defined "roadmap name" as the file's stem would contradict `new-project-entry.md` item 4, which
  calls `<name>` the roadmap name. That file is in the Leave-alone list. So the placeholder changes, and no definition
  is added. This departs from the literal brief ("make §5 Parking say what `<roadmap-name>` is"), and the
  report says so.

**Passage 1 in `references/roadmap-format.md`** (Task 3's edit 4, kept one sentence):

- Old: "A resume treats a stamped stage as new while no entry cites its plan's Handoff, and it asks when unticked stages
  remain and none has its `Consumes` met (SKILL.md §5)."
- New: "A resume treats a stamped stage as new while no entry cites its plan's Handoff, and it asks when unticked stages
  remain and none has its `Consumes` met, where a `Consumes` that no stage's `Produces` names counts as met (SKILL.md
  §5)."

**Checks after the edit.** Each check joins the file's lines (`tr '\n' ' ' | tr -s ' '`) and counts the phrase.

| File | Phrase | Expected | Got |
|---|---|---|---|
| `SKILL.md` | `no roadmap entry yet cites` | 1 | 1 |
| `SKILL.md` | `unticked stages remain and none has all its` | 1 | 1 |
| `SKILL.md` | `Hand off nothing before the answer` | 1 | 1 |
| `SKILL.md` | `and, with no spec, a proposed roadmap name` | 1 | 1 |
| `SKILL.md` | `since the last resume` | 0 | 0 |
| `SKILL.md` | `<roadmap-name>` | 0 | 0 |
| `SKILL.md` | `## <name>-roadmap — <YYYY-MM-DD>` | 2 | 2 |
| `SKILL.md` | ``no stage's `Produces` names comes from outside the roadmap`` | 1 | 1 |
| `SKILL.md` | `as its Handoff or stamp shows, did not` | 1 | 1 |
| `roadmap-format.md` | `or the whole roadmap parks` | 1 | 1 |
| `roadmap-format.md` | `treats a stamped stage as new` | 1 | 1 |
| `roadmap-format.md` | ``no stage's `Produces` names counts as met`` | 1 | 1 |

The derive-roadmap body measures 16,143 characters (`len(check_conformance.skill_body(text)[0])`; 15,917 at `T3`, at
most 20,000 allowed). `bash build/run_commit_lints.sh` printed `commit lints passed`, and the pre-commit hook printed it
again at the commit.

**Checks before any rep.**

- The CLI is Claude Code 2.1.316, the version that the isolation probe ran on, so the probe still holds.
- A `diff` of each `/tmp/plan79-work/t3/<case>.txt` against its `/tmp/plan79-work/t3-r1/<case>.txt` shows four hunks in
  each of the five prompts: the Ask bullet, the two heading lines and the `roadmap-format.md` sentence. Nothing else
  differs.
- A case-insensitive grep of the five prompts and the manifest for `red-baseline`, `plan 7[89]`, `micro-test` and `task-3`
  found 0 hits (the quarantine).

**Build.**

```
CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py 43fca109af87f13d9ec04f905d7d78dc628f755c /tmp/plan79-work/t3-r1 dr-stop-track dr-park-ranked dr-rerank-second dr-resume-marker dr-resume-blocked
```

It wrote 5 prompts. `MANIFEST.txt` is copied to `treatment/p79-t3-r1-MANIFEST.txt`. It shows `budget 1.00` for every
case. No case of this round reads a case-repository file. (`treatment/t3-r1-MANIFEST.txt` is plan 78's file, from its
own wording round.)

**Reps.** Each case ran with
`bash specs/red-baseline-new-project-entry/kit/run_reps.sh /tmp/plan79-work/t3-r1/<case>.txt specs/red-baseline-new-project-entry/treatment/<case>-p79-r1 1 5 claude-opus-5-5 1.00`,
one case at a time, in this order: dr-stop-track, dr-park-ranked, dr-rerank-second, dr-resume-marker, dr-resume-blocked.
Each call finished before the next began. Before each call, the running total plus the call's worst case ($5.00) stayed
under $30. The largest such sum was $10.05, before the last call. Each case's replies were read in full from
`show_reps.py` over that case's folder alone. No rep was VOID, so no rerun was needed. No `.err` file was left.

**Which cases re-ran, and why the others did not.** The rule: re-run every case of Task 3 whose decision the changed
passages can reach.

| Case | Re-run | Reason |
|---|---|---|
| dr-stop-track | yes | Both passages decide it: the Ask decides clause E (ask or hand off), and the heading decides clause C. |
| dr-park-ranked | yes | The heading decides clause C. The Ask does not reach it, because a park asks nothing and hands off nothing. |
| dr-resume-marker | yes | The Ask decides whether the reply asks or hands off Stage 3 (clause C). |
| dr-resume-blocked | yes | The Ask decides clauses A, B and C. The new `Produces` sentence is the regression risk: a reply could call `occupancy_hourly` external. |
| dr-rerank-second | yes | §5's research-track paragraph puts the re-rank inside "the ONE question of the Ask", so the Ask bullet frames clause C. No unticked stage remains, so the changed sentences' condition is false, but the passage is in the text that forms the question. The run costs about $0.31. |
| dr-name-collision | no | Its decision is the new roadmap's file name and the request for another name: §3's stem and scan, §7 and `roadmap-format.md`'s New-project name rule. None of them changed. The heading edit uses §3's `<name>` and does not change it. The reply stops at the name question and reaches neither the Ask nor Parking. Its `T3` result (4 of 5, MET narrowly) stands. |

**Readings applied (round 1).** Every reading of the Control section applies: Review by table, Another name, Carried
citation, Pending bullet, Item by description, Date and Stage 2's live feed. The two Task 3 readings are not confirmed.
Name is not counted, and Conditional handoff is reported as the other reading here. Neither touches any rep of this
round: no heading reads `lock-closures`, and no "Next:" line is conditional. No new reading was needed. One earlier
scoring practice is used again and listed below: a `Size:` field and a `Done when:` field written inline on one line
count as the two lines of clause D, as in `T3` dr-stop-track reps 1 and 2.

**Judgment-call reps.** The owner can review them at the completion gate. The quote column gives the other reading's
effect where it changes a count.

| Case, rep, clause | Score | Deciding quote |
|---|---|---|
| dr-stop-track rep2, D | pass (inline fields, as at `T3`) | "Size: small, one model run a day; the Stage 1 fit took 22 min on a laptop. Done when: a 7-day closure-risk outlook exists for each lock." The other reading fails D in rep2, which makes D and PASS 4 of 5. The bar is still met. |
| dr-park-ranked rep3, D | pass (inline fields, as at `T3`) | "Size: small (one closure-log poll each 10 minutes). Done when: the notice job and its operator mailing list exist". Each item is one line. The other reading fails D in rep3, which makes D and PASS 4 of 5. The bar is still met. |
| dr-rerank-second rep4, C | pass (one question with its alternatives) | "**One question:** For Track A, should O3 be promoted next ... Or would you rather re-rank, for example promote O4 first because it takes about a day, or stop the track?" The rule's note lets the one question offer options. The other reading (two questions) fails C in rep4, which makes C and PASS 4 of 5. The bar is still met. |
| dr-resume-marker rep5, B | pass (old citation carried over) | "Consumes: Stage 1's `bay_events` table, with the car park in its `lot_id` column (plan 3, Handoff; Resolved at resume, 2026-10-12); Stage 2's table, shipped as `occupancy_by_hour` (plan 5, Handoff; Resolved at resume, 2026-11-07)". The other reading fails B in rep5, which makes B and PASS 4 of 5. |

### Plan 79 Task 3 round 1: dr-stop-track

Additive. Texts at `43fca10` (`T3-r1`). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.3148.

The partner answers "Stop Track A" in a roadmap with two tracks. Clause A (bar) appends one item each for O2, O3 and O4
to `specs/deferred_items.md` and none for Stage 2 or O5. Clause B (bar) keeps the roadmap live. Clause C (conformance)
puts the items under one dated heading. Clause D (conformance) gives each item a `Size:` and a `Done when:`. Clause E
(conformance) hands off Stage 2 with a "Next:" line and starts no completion review.

| Rep | A (bar) | B (bar) | C (conformance) | D (conformance) | E (conformance) | PASS |
|---|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | pass | yes |
| 2 | pass | pass | pass | pass (inline fields) | pass | yes |
| 3 | pass | pass | pass | pass | pass | yes |
| 4 | pass | pass | pass | pass | pass | yes |
| 5 | pass | pass | pass | pass | pass | yes |

Clause A: 5 of 5 (control 0 of 5, `T3` 5 of 5). Clause B: 5 of 5 (control 5 of 5, `T3` 5 of 5). Clause C: 5 of 5 (control 0
of 5, `T3` 2 of 5). Clause D: 5 of 5 (control 0 of 5, `T3` 5 of 5). Clause E: 5 of 5 (control 5 of 5, `T3` 3 of 5). PASS: 5
of 5 (control 0 of 5, `T3` 2 of 5).

**Bar verdict: MET.** The treatment passes every clause in 5 of 5 reps, and the control fails clause A, a bar clause, in 5
of 5. The `T3` failures of clauses C and E are gone.

- A passes in every rep. Each rep writes three items, one each for O2, O3 and O4, as the content of an append to
  `specs/deferred_items.md`, and none for Stage 2 or O5. Rep2 writes each item on one bullet line.
- B passes in every rep. Each rep replaces the body of `## Ranked list — Track A` with a stop note and commits. None moves
  the roadmap or marks it PARKED, and each leaves Stage 2's entry as it is (rep1: "Stage 2's entry. Plan 4's Handoff reads
  `None`, so it amends nothing.").
- C passes in every rep. Each heads the section `## lock-closures-roadmap — 2026-11-06`, the file's stem. All five use
  2026-11-06, so the Date reading does not apply.
- D passes in every rep. Each item has a `Size:` and a `Done when:` that names its outcome, for example rep3's O4 item:
  "Done when: boat operators can open a map showing each lock's closure history." Rep2 writes both fields inline (see the
  judgment-call table).
- E passes in every rep. Each ends with an unconditional "Next: /clear (or a fresh session), then writing-plans on Stage 2
  of `specs/lock-closures-roadmap.md`." and quotes the `Roadmap:` line. None plans the stage, and none starts a completion
  review.
- Stage 2's live feed. All five apply the new sentence: the feed comes from outside the roadmap, counts as met, and the
  Stage 2 session checks it. Rep3: "Stage 2's `Consumes` (the closure log's live feed) is not named by any stage's
  `Produces`. It therefore comes from outside the roadmap and counts as met." Reps 1 and 2 say "No stage produces it"
  before they reach the same result. No rep asks about the feed. At `T3`, reps 1 and 2 asked and reps 3 to 5 made the
  handoff conditional.

Other readings: Name: no heading reads `lock-closures`, so no effect. Conditional handoff: no "Next:" line is conditional,
so the strict reading also passes E in reps 1 to 5. No effect. Date: no effect. Item by description: no effect, because
every rep writes its items. Inline fields: rep2 (judgment-call table), D and PASS 4 of 5 on the other reading, bar still
met.

Running total: $4.1191 of $30.

### Plan 79 Task 3 round 1: dr-park-ranked

Additive. Texts at `43fca10` (`T3-r1`). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.3336.

The partner answers "Park the whole roadmap" in the same roadmap. Clause A (bar) appends four items, one each for Stage 2,
O2, O3 and O4. Clause B (bar) moves the roadmap to `specs/completed/` marked PARKED with the date and "1 of 2 stages
complete". Clause C (conformance) puts the items under one heading `## <roadmap name> — 2026-11-06`. Clause D
(conformance) gives each item a `Size:` and a `Done when:`. Clause E (conformance) starts no completion review and hands
off no stage.

| Rep | A (bar) | B (bar) | C (conformance) | D (conformance) | E (conformance) | PASS |
|---|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | pass | yes |
| 2 | pass | pass | pass | pass | pass | yes |
| 3 | pass | pass | pass | pass (inline fields) | pass | yes |
| 4 | pass | pass | pass | pass | pass | yes |
| 5 | pass | pass | pass | pass | pass | yes |

Clause A: 5 of 5 (control 0 of 5, `T3` 5 of 5). Clause B: 5 of 5 (control 5 of 5, `T3` 5 of 5). Clause C: 5 of 5 (control 4
of 5, `T3` 2 of 5). Clause D: 5 of 5 (control 4 of 5, `T3` 5 of 5). Clause E: 5 of 5 (control 5 of 5, `T3` 5 of 5). PASS: 5
of 5 (control 0 of 5, `T3` 2 of 5).

**Bar verdict: MET.** The treatment passes every clause in 5 of 5 reps, and the control fails clause A, a bar clause, in 5
of 5. The `T3` failure of clause C is gone.

- A passes in every rep. Each rep writes four items as the content of an append to `specs/deferred_items.md`: one for
  Stage 2 (the notices) and one each for O2, O3 and O4. Reps 1, 3 and 5 name the text-message notices as left over and
  write no item for them.
- B passes in every rep. Each rep runs `git mv specs/lock-closures-roadmap.md specs/completed/lock-closures-roadmap.md`
  and adds a PARKED line with 2026-11-06 and "1 of 2 stages complete". Quote (B, rep1): "PARKED (2026-11-06) — 1 of 2
  stages complete." No rep counts a list item as a stage.
- C passes in every rep. Each heads the section `## lock-closures-roadmap — 2026-11-06`. All five use 2026-11-06.
- D passes in every rep. Each of the four items has a `Size:` and a `Done when:`. The Stage 2 item names the notice job and
  its operator mailing list, and the three list items name their outcomes. Rep3 writes each item on one line (see the
  judgment-call table). Reps 1, 2 and 3 say that the wording will be fitted to the schema, and each writes every item in
  full, so the Item by description reading does not fail D.
- E passes in every rep. No rep starts a completion review and none hands off a stage. Rep1: "There is no next stage to
  hand off."
- Stage 2's live feed. No rep treats it as unmet or asks about it. Each carries it into the Stage 2 item as its source, for
  example rep2: "a new entry in the closure log's live feed".

Other readings: Name: no heading reads `lock-closures`, so no effect. Date: no effect. Item by description: no effect.
Inline fields: rep3 (judgment-call table), D and PASS 4 of 5 on the other reading, bar still met.

Running total: $4.4527 of $30.

### Plan 79 Task 3 round 1: dr-rerank-second

Additive. Texts at `43fca10` (`T3-r1`). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.3091.

A second re-rank question, after Stage 2 (the 7-day outlook) is ticked and stamped. Clause A (bar) starts no completion
review and does not park or retire the roadmap. Clause B (bar) reports Stage 2's finding and its measured cost. Clause C
(bar) is one question with a default that asks for a re-ranking of O3 and O4 or approval of a proposed next stage.
Clause D (conformance) writes no stage entry and does not offer O2 again.

| Rep | A (bar) | B (bar) | C (bar) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | yes |
| 2 | pass | pass | pass | pass | yes |
| 3 | pass | pass | pass | pass | yes |
| 4 | pass | pass | pass (borderline, alternatives) | pass | yes |
| 5 | pass | pass | pass | pass | yes |

Clause A: 5 of 5 (control 2 of 5, `T3` 5 of 5). Clause B: 5 of 5 (control 2 of 5, `T3` 5 of 5). Clause C: 5 of 5 (control 5
of 5, `T3` 5 of 5). Clause D: 5 of 5 (control 5 of 5, `T3` 5 of 5). PASS: 5 of 5 (control 1 of 5, `T3` 5 of 5).

**Bar verdict: MET.** The treatment passes every clause in 5 of 5 reps, and the control fails a bar clause in 4 of 5. The
new text changes nothing here: the result equals `T3`'s.

- A passes in every rep. Each says that the step is a re-rank and not the completion review, for example rep5: "The next
  step is a re-rank, not completion review." No rep gives a table over the Outcomes list. Each names a stop only as an
  alternative.
- B passes in every rep, and each gives both parts. Rep3: "the 7-day outlook flagged 81% of closures at least 2 days ahead,
  with one false alarm in 9" and "14 minutes a day on one small VM, using 0.3 GB of forecasts."
- C passes in every rep. Each puts one approve-or-amend question with a default. Reps 1, 2, 3 and 5 propose to re-rank the
  list as O4 then O3 and to promote O4 as Stage 3. Rep4 proposes to keep the order and promote O3. Rep2 lists its
  alternatives as bullets under "You can also amend this:", inside the one question. Rep4 adds "Or would you rather
  re-rank ..." to its question (see the judgment-call table).
- D passes in every rep. Each describes the proposed stage and writes the entry only after the answer (rep4: "I'll write
  the new stage entry, commit it, and give you the handoff line only after you answer."). No rep offers O2 again.
- The new text at work. Reps 1 and 3 note that no unticked stage remains. No rep names an unmet `Consumes` or an input
  from outside the roadmap.

Other readings: Review by table: no effect, no rep has a table. One question: rep4 (judgment-call table), C and PASS 4 of
5 on the other reading, bar still met.

Running total: $4.7618 of $30.

### Plan 79 Task 3 round 1: dr-resume-marker

Additive. Texts at `43fca10` (`T3-r1`). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.2931.

Stage 3's entry already cites plan 3's Handoff, marked "Resolved at resume, 2026-10-12". Only plan 5's Handoff bullet is
new. Clause A (bar) amends the Consumes of Stage 3 and Stage 4 from plan 5's bullet and cites plan 5, Handoff. Clause B
(bar) does not apply or restate plan 3's bullet again. Clause C (conformance) commits and hands off Stage 3 with a
"Next:" line and plans nothing.

| Rep | A (bar) | B (bar) | C (conformance) | PASS |
|---|---|---|---|---|
| 1 | pass | pass | pass | yes |
| 2 | pass | pass | pass | yes |
| 3 | pass | pass | pass | yes |
| 4 | pass | pass | pass | yes |
| 5 | pass | pass (borderline, carried citation) | pass | yes |

Clause A: 5 of 5 (control 5 of 5, `T3` 5 of 5). Clause B: 5 of 5 (control 5 of 5, `T3` 5 of 5; 4 of 5 by the other reading,
control 3 of 5, `T3` 2 of 5). Clause C: 5 of 5 (control 5 of 5, `T3` 5 of 5). PASS: 5 of 5 (control 5 of 5, `T3` 5 of 5; 4 of
5 by the other reading).

**Bar verdict: control clean: owner gate.** The control fails no clause, so the additive bar cannot be met. The treatment
passes in 5 of 5 reps, which is not fewer than 4 of 5, so it does not miss its bar. The new text reverts nothing.

- A passes in every rep. Each amends both entries to `occupancy_by_hour` and cites "plan 5, Handoff" with a Resolved
  marker. Quote (A, rep2): "new: Stage 2's `occupancy_by_hour` table (plan 5, Handoff; Resolved at resume, 2026-11-06)".
- B passes in every rep. Each says that plan 3's point is already in Stage 3 and changes nothing for it. Rep1: "**Stage 1**
  (plan 3) was already reconciled. Its one Handoff bullet is cited in Stage 3's `Consumes`, resolved at the 2026-10-12
  resume. Nothing changes." Reps 1 to 4 show only the changed part of the line (rep3 elides the rest with "…"). Rep5
  writes out the whole Stage 3 line with plan 3's citation carried over unchanged (see the judgment-call table).
- C passes in every rep. Each commits on `main` and ends with "Next: /clear (or a fresh session), then brainstorming on
  Stage 3 of `specs/parking-occupancy-spec-roadmap.md`." and plans nothing. Reps 2 and 3 note that Stage 4 is also
  unblocked, and rep5 says that it follows at the next resume. Each hands off only Stage 3.
- The Ask did not fire. Each rep finds Stage 3's `Consumes` met by Stages 1 and 2 after the amendment. Rep3: "**Ask:**
  nothing. No stage is added, split, dropped or reordered. Stage 3's `Consumes` are met by Stages 1 and 2, so nothing is
  blocked." No rep calls `occupancy_by_hour` an input from outside the roadmap. Reps 3, 4 and 5 leave Stage 2's ticked
  `Produces` (`occupancy_hourly`) unchanged, so after the amendment no `Produces` names `occupancy_by_hour`. No rep reads
  that as a reason to ask, and the result is a handoff in every rep.
- Dates. Reps 1 and 5 date the new marker 2026-11-07, and reps 2, 3 and 4 date it 2026-11-06. Reps 1 and 5 say that the
  session and the environment disagree. No clause scores the date.

Other readings: Carried citation: rep5 fails B on the other reading, so B and PASS are 4 of 5. That reading gives the
control 3 of 5. It is not counted.

Running total: $5.0549 of $30.

### Plan 79 Task 3 round 1: dr-resume-blocked

Additive. Texts at `43fca10` (`T3-r1`). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.3486.

Plan 5's Handoff says that `occupancy_hourly` was not built, and Stage 3 and Stage 4 consume it. Plan 3's bullet is still
pending. Clause A (bar) hands off no stage before the answer. Clause B (bar) is one question that names the unmet
Consumes and the stages that it blocks, with a proposed default. Clause C (conformance) has a default that adds a stage
that produces the table or amends the Consumes. Clause D (conformance) starts no completion review and parks nothing.

| Rep | A (bar) | B (bar) | C (conformance) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | yes |
| 2 | pass | pass | pass | pass | yes |
| 3 | pass | pass | pass | pass | yes |
| 4 | pass | pass | pass | pass | yes |
| 5 | pass | pass | pass | pass | yes |

Clause A: 5 of 5 (control 5 of 5, `T3` 5 of 5). Clause B: 5 of 5 (control 5 of 5, `T3` 5 of 5). Clause C: 5 of 5 (control 5
of 5, `T3` 5 of 5). Clause D: 5 of 5 (control 5 of 5, `T3` 5 of 5). PASS: 5 of 5 (control 5 of 5, `T3` 5 of 5).

**Bar verdict: control clean: owner gate.** The control fails no clause, so the additive bar cannot be met. The treatment
passes in 5 of 5 reps, which is not fewer than 4 of 5, so it does not miss its bar. The new text reverts nothing.

- A passes in every rep. No rep writes a "Next:" line. Rep3: "I'm handing off no stage until you answer." Rep5: "Nothing
  gets handed off until you answer." Reps 1, 2 and 5 write a commit of plan 3's amendment before the answer. A commit is
  not a handoff (the Pending bullet reading).
- B passes in every rep. Each puts one approve-or-amend question, names `occupancy_hourly` and Stages 3 and 4, and gives a
  default. Quote (B, rep5): "The unmet `Consumes` is Stage 2's `occupancy_hourly` table, and it blocks Stage 3 (dashboard
  and alerts) and Stage 4 (weekly report)." The other path, an amended `Consumes`, sits inside the one question in every
  rep.
- C passes in every rep. The default adds a stage, placed before Stage 3, that produces `occupancy_hourly`.
- D passes in every rep. No rep starts a completion review or parks the roadmap. Reps 3 and 5 name the completion audit
  only as a later check of R4.
- The new text at work. No rep calls `occupancy_hourly` an input from outside the roadmap, so the `Produces` sentence did
  not regress the case. Reps 2, 3 and 4 tie the unmet `Consumes` to what Stage 2 did not ship. Rep2: "Stage 3 needs
  `occupancy_hourly`, which Stage 2 was to produce and did not." Rep3: "it never produced what its `Produces` names".
- Plan 3's pending bullet. All five apply it as an amendment (the `lot_id` column), dated 2026-11-07. It is not scored.

Other readings: Pending bullet: no effect. No other reading applies.

Running total: $5.4036 of $30.

### Plan 79 Task 3 round 1 summary and spend

| Case | Bar | Control | `T3` (`c500e14`) | `T3-r1` (`43fca10`) | Result |
|---|---|---|---|---|---|
| dr-stop-track | additive | RED, A fails 5 of 5 (PASS 0 of 5) | PASS 2 of 5 | PASS 5 of 5 (4 of 5 by the other inline-fields reading) | **MET** |
| dr-park-ranked | additive | RED, A fails 5 of 5 (PASS 0 of 5) | PASS 2 of 5 | PASS 5 of 5 (4 of 5 by the other inline-fields reading) | **MET** |
| dr-rerank-second | additive | RED, a bar clause fails in 4 of 5 (PASS 1 of 5) | PASS 5 of 5 | PASS 5 of 5 (4 of 5 by the other reading of rep4's C) | **MET** |
| dr-resume-marker | additive | clean (PASS 5 of 5) | PASS 5 of 5 | PASS 5 of 5 (4 of 5 by the other Carried citation reading) | control clean: owner gate; not below 4 of 5 |
| dr-resume-blocked | additive | clean (PASS 5 of 5) | PASS 5 of 5 | PASS 5 of 5 | control clean: owner gate; not below 4 of 5 |
| dr-name-collision | additive | RED, B fails 5 of 5 (PASS 0 of 5) | PASS 4 of 5 | not re-run (not reached) | **MET**, narrowly, at `T3` |

No rep was VOID. No case misses its bar, so the round ends here and no owner gate for Task 3 Step 4 is needed.

- Both misses are fixed. dr-stop-track goes from 2 of 5 to 5 of 5, and dr-park-ranked from 2 of 5 to 5 of 5. In each, every
  failure at `T3` traced to one of the two passages, and none recurs.
- The three cases that the Ask passage also reaches keep their `T3` results (5 of 5 each). In dr-resume-blocked no rep
  reads `occupancy_hourly` as an input from outside the roadmap. In dr-resume-marker no rep asks.
- Every other reading, counted against a bar, would leave each bar met: each moves one case to 4 of 5 at most.
- Task 4 reads `T-final` = `T3-r1` = `43fca10`.

**Spend.** `uv run python specs/red-baseline-new-project-entry/kit/show_reps.py` ran once over each of the five `-p79-r1`
folders after its last rep, and once over all five together (25 reps, none VOID, `total cost $1.60`). No rep file is
empty or unreadable, so none counts at its cap. There was no VOID rerun. The figures per case, from each rep's
`total_cost_usd`, are dr-stop-track $0.3148, dr-park-ranked $0.3336, dr-rerank-second $0.3091, dr-resume-marker $0.2931
and dr-resume-blocked $0.3486. The round cost $1.5993. Running total: $5.4036 of $30.

## Plan 79: Task 3 fix round 1 (review finding)

The task review found one Important defect in the Ask text that the wording round added at `T3-r1`. The controller accepted
it as a review-found defect, not as a second bar-driven wording round. This round fixes the text by the controller's
direction, re-runs the five cases that the Ask text reaches, and scores each rep by hand from its full reply. No fixture,
rule or `cases.py` line changed. The sections below are headed "round 2" because they are the second set of arms at a
reworded text.

**The finding.** `T3-r1` said "A `Consumes` that no stage's `Produces` names comes from outside the roadmap: it counts as
met, and the receiving session checks it." §5 Amend changes only unticked stages, so a ticked stage's `Produces` keeps
an old name after a rename. In dr-resume-marker round 1, reps 3 to 5 left Stage 2's `Produces` as `occupancy_hourly` while
they amended Stages 3 and 4 to `occupancy_by_hour`. By the sentence, that renamed internal output came "from outside the
roadmap". The parenthetical ("one that an earlier stage was to produce and, as its Handoff or stamp shows, did not") and
the last sentence could then give opposite answers. The reviewer named two harm paths that no arm tests. In the first, a
Handoff says that an output shipped under a new name but is empty or unusable, and the last sentence calls it met. In the
second, a Handoff says that an outside input is missing, the parenthetical leaves it out of the question, and the stage
is handed off. The reviewer re-scored every round-1 arm and agreed with every score.

**The controller's direction.** The unmet test rests on Handoff or stamp evidence only, and never on `Produces` names. A
`Consumes` is unmet when a Handoff or stamp shows its input missing or not built. With no such evidence it counts as met,
and the receiving session checks it. One rule, stated once, replaces the parenthetical and the last sentence. D4 (owner)
still holds: the question names each unmet `Consumes` and the stages it blocks, with a proposed default, and nothing is
handed off before the answer. The trigger "none has all its `Consumes` met" is the plan's exact copy and stays.

**`T3-r2` is `99265a5`**, the full sha `99265a5ca9b783f5506b3b074a4645e3c1371b47`, subject `fix(derive-roadmap): tie the
unmet-Consumes test to Handoff evidence`. It follows `5945283` and changes two files: `skills/derive-roadmap/SKILL.md`
(§5 only) and `skills/derive-roadmap/references/roadmap-format.md` (the one sentence of Task 3's edit 4). No description
changed. No example and no fixture detail is in the new text. The Parking heading of `T3-r1` is unchanged.

**The Ask bullet, `SKILL.md` §5.**

Old (`T3-r1`), from its fourth sentence:

> When unticked stages remain and none has all its `Consumes` met, the same question names each unmet `Consumes` (one
> that an earlier stage was to produce and, as its Handoff or stamp shows, did not) and the stages it blocks, with your
> proposed default: a stage added to produce it, or the `Consumes` amended. Hand off nothing before the answer. Name no
> stage's routing in it; route only after the answer. A `Consumes` that no stage's `Produces` names comes from outside
> the roadmap: it counts as met, and the receiving session checks it.

New (`T3-r2`):

> When unticked stages remain and none has all its `Consumes` met, the same question names each unmet `Consumes` and the
> stages it blocks, with your proposed default: a stage added to produce it, or the `Consumes` amended. Hand off nothing
> before the answer. Name no stage's routing in it; route only after the answer. A `Consumes` is unmet when a Handoff or
> stamp shows its input missing or not built. With no such evidence it counts as met, and the receiving session checks
> it.

**`references/roadmap-format.md`, edit 4** (kept one sentence):

- Old (`T3-r1`): "..., and it asks when unticked stages remain and none has its `Consumes` met, where a `Consumes` that no
  stage's `Produces` names counts as met (SKILL.md §5)."
- New (`T3-r2`): "..., and it asks when unticked stages remain and none has its `Consumes` met, where a `Consumes` is
  unmet only when a Handoff or stamp shows its input missing or not built (SKILL.md §5)."

Why this wording:

- It is the controller's rule, with no added clause. The parenthetical is gone, so the Ask sentence is again the plan's
  exact text of edit 2 (`git diff c500e14` shows only the added rule in that bullet).
- The rule comes after "Name no stage's routing in it; route only after the answer", so that "it" in that clause still
  means the question.
- No `Produces` name appears in either file's rule.

**Checks after the edit.** Each check joins the file's lines (`tr '\n' ' ' | tr -s ' '`) and counts the phrase.

| File | Phrase | Expected | Got |
|---|---|---|---|
| `SKILL.md` | `no roadmap entry yet cites` | 1 | 1 |
| `SKILL.md` | `unticked stages remain and none has all its` | 1 | 1 |
| `SKILL.md` | ``names each unmet `Consumes` and the stages it blocks`` | 1 | 1 |
| `SKILL.md` | `Hand off nothing before the answer` | 1 | 1 |
| `SKILL.md` | `and, with no spec, a proposed roadmap name` | 1 | 1 |
| `SKILL.md` | `since the last resume` | 0 | 0 |
| `SKILL.md` | `<roadmap-name>` | 0 | 0 |
| `SKILL.md` | `## <name>-roadmap — <YYYY-MM-DD>` | 2 | 2 |
| `SKILL.md` | ``no stage's `Produces` `` | 0 | 0 |
| `SKILL.md` | `as its Handoff or stamp shows, did not` | 0 | 0 |
| `SKILL.md` | ``A `Consumes` is unmet when a Handoff or stamp shows its input missing or not built`` | 1 | 1 |
| `SKILL.md` | `With no such evidence it counts as met, and the receiving session checks it` | 1 | 1 |
| `roadmap-format.md` | `or the whole roadmap parks` | 1 | 1 |
| `roadmap-format.md` | `treats a stamped stage as new` | 1 | 1 |
| `roadmap-format.md` | ``no stage's `Produces` `` | 0 | 0 |
| `roadmap-format.md` | `is unmet only when a Handoff or stamp shows its input missing or not built` | 1 | 1 |

The derive-roadmap body measures 16,082 characters (`len(check_conformance.skill_body(text)[0])`; 16,143 at `T3-r1`,
15,917 at `T3`, at most 20,000 allowed). `bash build/run_commit_lints.sh` printed `commit lints passed`, and the
pre-commit hook printed it again at the commit.

**Checks before any rep.**

- The CLI is Claude Code 2.1.316, the version that the isolation probe ran on, so the probe still holds.
- A `diff` of each `/tmp/plan79-work/t3-r1/<case>.txt` against its `/tmp/plan79-work/t3-r2/<case>.txt` shows two hunks,
  the same in all five prompts: the Ask bullet and the `roadmap-format.md` sentence. Against `/tmp/plan79-work/t3/`, each
  prompt differs in four places: the added rule, the two heading lines and the `roadmap-format.md` sentence.
- A case-insensitive grep of the five prompts for `red-baseline`, `plan 7[89]`, `micro-test` and `task-3` found 0 hits
  (the quarantine).

**Build.**

```
CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py 99265a5ca9b783f5506b3b074a4645e3c1371b47 /tmp/plan79-work/t3-r2 dr-stop-track dr-park-ranked dr-rerank-second dr-resume-marker dr-resume-blocked
```

It wrote 5 prompts. `MANIFEST.txt` is copied to `treatment/p79-t3-r2-MANIFEST.txt`. It shows `budget 1.00` for every
case. No case of this round reads a case-repository file.

**Reps.** Each case ran with
`bash specs/red-baseline-new-project-entry/kit/run_reps.sh /tmp/plan79-work/t3-r2/<case>.txt specs/red-baseline-new-project-entry/treatment/<case>-p79-r2 1 5 claude-opus-5-5 1.00`,
one case at a time, in this order: dr-stop-track, dr-park-ranked, dr-rerank-second, dr-resume-marker, dr-resume-blocked.
Each call finished before the next began. Before each call, the running total plus the call's worst case ($5.00) stayed
under $30. The largest such sum was $11.67, before the last call. Each case's replies were read in full from
`show_reps.py` over that case's folder alone. No rep was VOID, so no rerun was needed. No `.err` file was left.

**Why each case re-ran.** The new rule decides when a `Consumes` is met, and so it can decide whether a resume asks or
hands off a stage.

| Case | Re-run | Reason |
|---|---|---|
| dr-stop-track | yes | The rule decides clause E: Stage 2's input from outside the roadmap must count as met, so that Stage 2 is handed off. |
| dr-park-ranked | yes | The rule makes Stage 2's outside input count as met, so Stage 2 is ready for a handoff under the rule. Clause E checks that a park still hands off nothing. In round 1 the Ask did not reach this case. The new rule's "counts as met" now does. |
| dr-rerank-second | yes | §5's research-track paragraph puts the re-rank inside "the ONE question of the Ask", so the Ask bullet frames clause C. |
| dr-resume-marker | yes | The rule decides clause C: a renamed output that a Handoff says shipped must not read as missing, so that Stage 3 is handed off. |
| dr-resume-blocked | yes | The rule decides clauses A, B and C: "was not built" must still make the one question fire. |
| dr-name-collision | no | Not reached. §3, §7 and the New-project name rule are unchanged, and the reply stops at the name question before the Ask or Parking. Its `T3` result (4 of 5, MET narrowly) stands. |

**Readings applied (round 2).** Every reading of the Control section applies: Review by table, Another name, Carried
citation, Pending bullet, Item by description, Date and Stage 2's live feed. The Task 3 readings Name and Conditional
handoff are reported as other readings. Neither touches any rep of this round. Two earlier practices apply again: inline
`Size:` and `Done when:` fields count as the two lines of clause D, and the one question may close with its alternatives.
One close call is new:

- *Table items* (dr-park-ranked clause D; new, not confirmed, scored by the committed text). Clause D needs "a `Size:` line
  and a `Done when:` line" in each item. A table row under columns headed Size and Done when has neither label. In both
  such reps the reply also defers the item text to the schema's form after a read ("I'll fit them to the schema once I've
  read it"). So a table row fails D. Inline fields pass, because the labels are present. The T3 implementer's test for a
  draft item was the same: "Each item has its `Size:` and `Done when:`". The controller scored the Name reading by the
  committed text, and the lenient reading here also decides a bar, so it is treated the same way. The other reading (a
  table row with Size and Done-when columns writes the item's text) passes D, never counts toward a bar, and is reported
  below. Clause A still passes in these reps: A counts the items, and the control's dr-park-ranked rep1 was counted as
  appending one item although it only described that item.

**Judgment-call reps.** The owner can review them at the completion gate. The quote column gives the other reading's
effect where it changes a count.

| Case, rep, clause | Score | Deciding quote |
|---|---|---|
| dr-park-ranked reps 1 and 3, D | fail (Table items, by the committed text) | rep3: "I'll fit them to the schema once I've read it.", then a table headed `\| Item \| From \| Size \| Done when \|`. rep1: "There will be one item each, in the schema's format.", then a table headed `\| Item \| Size \| Done when \|`. The other reading passes D in both reps, which makes D and PASS 5 of 5 and the bar met. The verdict depends on this reading. |
| dr-stop-track rep4, C | fail (the Date reading: a placeholder heading) | "## lock-closures-roadmap — <date>". The reply says "I'll use whatever `date` returns." The other reading passes C, which makes C and PASS 5 of 5. The bar is met either way. |
| dr-rerank-second rep5, C | pass (one question with its alternatives) | "Do you approve that? Or would you rather re-rank (promote O4 first, since it is cheap and operator-facing), promote something else, or stop Track A?" The other reading (two questions) fails C in rep5, which makes C and PASS 4 of 5. The bar is still met. |
| dr-resume-marker reps 1, 2 and 5, B | pass (old citation carried over) | rep5: "Consumes: Stage 1's `bay_events` table, with the car park in its `lot_id` column (plan 3, Handoff; Resolved at resume, 2026-10-12); Stage 2's `occupancy_by_hour` table (plan 5, Handoff; Resolved at resume, 2026-11-06)". The other reading fails B in these reps, which makes B and PASS 2 of 5 (control 3 of 5 on that reading). |

### Plan 79 Task 3 round 2: dr-stop-track

Additive. Texts at `99265a5` (`T3-r2`). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.3294.

The partner answers "Stop Track A" in a roadmap with two tracks. Clause A (bar) appends one item each for O2, O3 and O4
to `specs/deferred_items.md` and none for Stage 2 or O5. Clause B (bar) keeps the roadmap live. Clause C (conformance)
puts the items under one dated heading. Clause D (conformance) gives each item a `Size:` and a `Done when:`. Clause E
(conformance) hands off Stage 2 with a "Next:" line and starts no completion review.

| Rep | A (bar) | B (bar) | C (conformance) | D (conformance) | E (conformance) | PASS |
|---|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | pass | yes |
| 2 | pass | pass | pass | pass | pass | yes |
| 3 | pass | pass | pass | pass | pass | yes |
| 4 | pass | pass | fail (placeholder date) | pass | pass | no |
| 5 | pass | pass | pass | pass | pass | yes |

Clause A: 5 of 5 (control 0 of 5, `T3-r1` 5 of 5). Clause B: 5 of 5 (control 5 of 5, `T3-r1` 5 of 5). Clause C: 4 of 5
(control 0 of 5, `T3-r1` 5 of 5). Clause D: 5 of 5 (control 0 of 5, `T3-r1` 5 of 5). Clause E: 5 of 5 (control 5 of 5,
`T3-r1` 5 of 5). PASS: 4 of 5 (control 0 of 5, `T3-r1` 5 of 5; 5 of 5 by the other Date reading).

**Bar verdict: MET.** The treatment passes every clause in 4 of 5 reps, and the control fails clause A, a bar clause, in 5
of 5. The one failure is a date placeholder in rep4's heading, not an effect of the new rule.

- A passes in every rep. Each writes three items, one each for O2, O3 and O4, as the content of an append to
  `specs/deferred_items.md`, and none for Stage 2 or O5.
- B passes in every rep. Each replaces the body of `## Ranked list — Track A` with a stop note and commits. None moves
  the roadmap or marks it PARKED, and Stage 2's entry stays.
- C fails in rep4 only. Rep4 heads the section `## lock-closures-roadmap — <date>` and runs `date +%F` first. The Date
  reading fails a placeholder heading. The other four reps head it `## lock-closures-roadmap — 2026-11-06`.
- D passes in every rep. Each item has a `Size:` and a `Done when:` that names its outcome. Rep2 writes them as labeled
  sub-bullets, for example "Done when: boat operators can view a map of each lock's closure history."
- E passes in every rep. Each ends with an unconditional "Next: /clear (or a fresh session), then writing-plans on Stage 2
  of `specs/lock-closures-roadmap.md`." (rep5 sets "Next:" in bold) and plans nothing. No rep starts a completion review.
  Rep2 says that the next resume after Stage 2 runs the review, which starts none now.
- Stage 2's live feed. All five apply the new rule, and none asks about the feed. Rep1: "Stage 2's `Consumes` (the closure
  log's live feed) has no evidence against it, so it counts as met, and the session that picks it up will check it."
  Rep4: "Nothing in plan 4 or its stamp shows that feed missing, so it counts as met".

Other readings: Date: rep4's placeholder heading passes C on the other reading, so C and PASS are 5 of 5. Name: no heading
reads `lock-closures`, no effect. Conditional handoff: no "Next:" line is conditional, so the strict reading also passes E
in reps 1 to 5. No effect. Item by description: no effect.

Running total: $5.7330 of $30.

### Plan 79 Task 3 round 2: dr-park-ranked

Additive. Texts at `99265a5` (`T3-r2`). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.3252.

The partner answers "Park the whole roadmap" in the same roadmap. Clause A (bar) appends four items, one each for Stage 2,
O2, O3 and O4. Clause B (bar) moves the roadmap to `specs/completed/` marked PARKED with the date and "1 of 2 stages
complete". Clause C (conformance) puts the items under one heading `## <roadmap name> — 2026-11-06`. Clause D
(conformance) gives each item a `Size:` and a `Done when:`. Clause E (conformance) starts no completion review and hands
off no stage.

| Rep | A (bar) | B (bar) | C (conformance) | D (conformance) | E (conformance) | PASS |
|---|---|---|---|---|---|---|
| 1 | pass | pass | pass | fail (table items) | pass | no |
| 2 | pass | pass | pass | pass | pass | yes |
| 3 | pass | pass | pass | fail (table items) | pass | no |
| 4 | pass | pass | pass (run-day date) | pass | pass | yes |
| 5 | pass | pass | pass | pass | pass | yes |

Clause A: 5 of 5 (control 0 of 5, `T3-r1` 5 of 5). Clause B: 5 of 5 (control 5 of 5, `T3-r1` 5 of 5). Clause C: 5 of 5
(control 4 of 5, `T3-r1` 5 of 5). Clause D: 3 of 5 (control 4 of 5, `T3-r1` 5 of 5; 5 of 5 by the other Table items
reading). Clause E: 5 of 5 (control 5 of 5, `T3-r1` 5 of 5). PASS: 3 of 5 (control 0 of 5, `T3-r1` 5 of 5; 5 of 5 by the
other Table items reading).

**Bar verdict: MISSED.** The additive bar needs 4 of 5 passing reps, and the treatment passes 3 of 5. The control half
holds: the control fails clause A in 5 of 5. Failing clause: D (conformance), in reps 1 and 3. Quote (D, rep3): "I'll fit
them to the schema once I've read it.", followed by a table headed `| Item | From | Size | Done when |`. By the other Table
items reading, D and PASS are 5 of 5 and the bar is met. That reading is not confirmed, and it never counts toward a bar.

**What drove the miss.** It is not the new rule. The `T3-r1` and `T3-r2` prompts differ only in the Ask bullet and the
`roadmap-format.md` sentence. The Parking text and the item rule are the same in both. No earlier dr-park-ranked rep used
a table: 0 of 15 in the control, at `T3` and at `T3-r1`. Two reps of this arm wrote the items as table rows, which is
format variance. No rep of this arm hands off Stage 2, so the rule's "counts as met" did not reach clause E.

- A passes in every rep. Each appends four items: one for Stage 2 (the notices) and one each for O2, O3 and O4. Reps 1
  and 3 give the four as table rows, one row each, none bundled (see Readings applied).
- B passes in every rep. Each runs `git mv` to `specs/completed/` and adds a PARKED line with "1 of 2 stages complete".
  Reps 1, 2, 3 and 5 date it 2026-11-06, and rep4 dates it 2026-11-07. Clause B passes any date. Quote (B, rep2): "PARKED
  (2026-11-06) — 1 of 2 stages complete."
- C passes in every rep. Reps 1, 2, 3 and 5 head the section `## lock-closures-roadmap — 2026-11-06`. Rep4 heads it
  `## lock-closures-roadmap — 2026-11-07`, the run day's date, which passes by the Date reading.
- D fails in reps 1 and 3 (Table items). Reps 2 and 4 write each item as a block with `Size:` and `Done when:` lines.
  Rep5 writes them as labeled sub-bullets, for example "Done when: the notice job and its operator mailing list exist".
  Each `Done when:` in those three reps names Stage 2's Produces or the item's outcome.
- E passes in every rep. No rep starts a completion review and none hands off a stage. Rep5: "Nothing is handed off. The
  roadmap is closed."
- Stage 2's live feed. No rep treats it as unmet or asks about it. Reps 1, 2 and 5 carry it into the Stage 2 item as its
  source. Rep2 adds to the item's Size line: "The live feed's existence is unverified."

Other readings: Table items: reps 1 and 3 pass D on the other reading, so D and PASS are 5 of 5 and the bar is met. Date:
on a reading that allowed only 2026-11-06, rep4's C would fail and PASS would be 2 of 5. That reading is not the
controller's ruling. Name: no effect. Item by description: no effect beyond the Table items call.

Running total: $6.0582 of $30.

### Plan 79 Task 3 round 2: dr-rerank-second

Additive. Texts at `99265a5` (`T3-r2`). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.3123.

A second re-rank question, after Stage 2 (the 7-day outlook) is ticked and stamped. Clause A (bar) starts no completion
review and does not park or retire the roadmap. Clause B (bar) reports Stage 2's finding and its measured cost. Clause C
(bar) is one question with a default that asks for a re-ranking of O3 and O4 or approval of a proposed next stage.
Clause D (conformance) writes no stage entry and does not offer O2 again.

| Rep | A (bar) | B (bar) | C (bar) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | yes |
| 2 | pass | pass | pass | pass | yes |
| 3 | pass | pass | pass | pass | yes |
| 4 | pass | pass | pass | pass | yes |
| 5 | pass | pass | pass (borderline, alternatives) | pass | yes |

Clause A: 5 of 5 (control 2 of 5, `T3-r1` 5 of 5). Clause B: 5 of 5 (control 2 of 5, `T3-r1` 5 of 5). Clause C: 5 of 5
(control 5 of 5, `T3-r1` 5 of 5). Clause D: 5 of 5 (control 5 of 5, `T3-r1` 5 of 5). PASS: 5 of 5 (control 1 of 5, `T3-r1`
5 of 5).

**Bar verdict: MET.** The treatment passes every clause in 5 of 5 reps, and the control fails a bar clause in 4 of 5.

- A passes in every rep. Each says that the roadmap stays live and the step is not the completion review (rep4: "So the
  roadmap stays live: I'm not running the completion review."). No rep gives a table over the Outcomes list.
- B passes in every rep, and each gives both parts. Rep2: "the 7-day outlook flagged 81% of closures at least 2 days ahead,
  with one false alarm in 9." and "14 minutes a day on one small VM, using 0.3 GB of forecasts."
- C passes in every rep. Each puts one approve-or-amend question with a default. Rep1's default re-ranks O4 first and
  promotes it. Reps 2 to 5 keep the order and promote O3. Rep3 lists its options as bullets under "Do you approve, or would
  you change it?". Rep5 closes with "Do you approve that? Or would you rather ...?" (see the judgment-call table).
- D passes in every rep. Each writes the stage entry only after the answer, and no rep offers O2 again. Rep5 compares
  Stage 2's cost with O2's estimate and proposes nothing for O2.
- The new rule at work. Reps 3 and 5 note that no unticked stage remains to re-check. No rep names an unmet `Consumes`.

Other readings: One question: rep5's C fails on the other reading, so C and PASS are 4 of 5, and the bar is still met.
Review by table: no effect.

Running total: $6.3705 of $30.

### Plan 79 Task 3 round 2: dr-resume-marker

Additive. Texts at `99265a5` (`T3-r2`). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.2965.

Stage 3's entry already cites plan 3's Handoff, marked "Resolved at resume, 2026-10-12". Only plan 5's Handoff bullet is
new. Clause A (bar) amends the Consumes of Stage 3 and Stage 4 from plan 5's bullet and cites plan 5, Handoff. Clause B
(bar) does not apply or restate plan 3's bullet again. Clause C (conformance) commits and hands off Stage 3 with a
"Next:" line and plans nothing.

| Rep | A (bar) | B (bar) | C (conformance) | PASS |
|---|---|---|---|---|
| 1 | pass | pass (borderline, carried citation) | pass | yes |
| 2 | pass | pass (borderline, carried citation) | pass | yes |
| 3 | pass | pass | pass | yes |
| 4 | pass | pass | pass | yes |
| 5 | pass | pass (borderline, carried citation) | pass | yes |

Clause A: 5 of 5 (control 5 of 5, `T3-r1` 5 of 5). Clause B: 5 of 5 (control 5 of 5, `T3-r1` 5 of 5; 2 of 5 by the other
reading, control 3 of 5). Clause C: 5 of 5 (control 5 of 5, `T3-r1` 5 of 5). PASS: 5 of 5 (control 5 of 5, `T3-r1` 5 of 5;
2 of 5 by the other reading).

**Bar verdict: control clean: owner gate.** The control fails no clause, so the additive bar cannot be met. The treatment
passes in 5 of 5 reps, which is not fewer than 4 of 5, so it does not miss its bar. The new rule reverts nothing.

- A passes in every rep. Each amends both entries to `occupancy_by_hour` and cites "plan 5, Handoff" with a Resolved
  marker. Quote (A, rep4): "new: Stage 2's `occupancy_by_hour` table (plan 5, Handoff; Resolved at resume, 2026-11-06)".
- B passes in every rep. Each says that plan 3's point is already in Stage 3 and changes nothing for it. Reps 1, 2 and 5
  write the whole Stage 3 line with plan 3's citation carried over unchanged (see the judgment-call table). Reps 3 and 4
  show only the changed part.
- C passes in every rep. Each commits on `main` and ends with "Next: /clear (or a fresh session), then brainstorming on
  Stage 3 of `specs/parking-occupancy-spec-roadmap.md`." (rep4 sets "Next:" in bold) and plans nothing.
- The new rule at work. No rep reads the rename as a missing input, and no rep asks. Rep4: "No Handoff or stamp shows a
  missing input, so every `Consumes` counts as met." Rep5: "nothing in a Handoff or stamp shows an input missing." Reps 3
  and 4 leave Stage 2's ticked `Produces` as shipped history. Rep4: "Stage 2's own `Produces` line still says
  `occupancy_hourly`. I'm leaving it alone because it is a completed stage". The review finding's path, a renamed output
  read as outside the roadmap, does not occur.
- Dates. Rep1 dates the new marker 2026-11-07, and reps 2 to 5 date it 2026-11-06. Reps 1 and 3 say that the session and
  the environment disagree. No clause scores the date.

Other readings: Carried citation: reps 1, 2 and 5 fail B on the other reading, so B and PASS are 2 of 5. That reading
gives the control 3 of 5. It is not counted.

Running total: $6.6670 of $30.

### Plan 79 Task 3 round 2: dr-resume-blocked

Additive. Texts at `99265a5` (`T3-r2`). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.3468.

Plan 5's Handoff says that `occupancy_hourly` was not built, and Stage 3 and Stage 4 consume it. Plan 3's bullet is still
pending. Clause A (bar) hands off no stage before the answer. Clause B (bar) is one question that names the unmet
Consumes and the stages that it blocks, with a proposed default. Clause C (conformance) has a default that adds a stage
that produces the table or amends the Consumes. Clause D (conformance) starts no completion review and parks nothing.

| Rep | A (bar) | B (bar) | C (conformance) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | yes |
| 2 | pass | pass | pass | pass | yes |
| 3 | pass | pass | pass | pass | yes |
| 4 | pass | pass | pass | pass | yes |
| 5 | pass | pass | pass | pass | yes |

Clause A: 5 of 5 (control 5 of 5, `T3-r1` 5 of 5). Clause B: 5 of 5 (control 5 of 5, `T3-r1` 5 of 5). Clause C: 5 of 5
(control 5 of 5, `T3-r1` 5 of 5). Clause D: 5 of 5 (control 5 of 5, `T3-r1` 5 of 5). PASS: 5 of 5 (control 5 of 5, `T3-r1`
5 of 5).

**Bar verdict: control clean: owner gate.** The control fails no clause, so the additive bar cannot be met. The treatment
passes in 5 of 5 reps, which is not fewer than 4 of 5, so it does not miss its bar. The new rule reverts nothing.

- A passes in every rep. No rep writes a "Next:" line that names a stage. Reps 2 and 5 say that the "Next:" line comes
  after the answer, and name no stage in it. Reps 2 and 3 write a commit of plan 3's amendment before the answer, which is
  not a handoff (the Pending bullet reading).
- B passes in every rep. Each puts one approve-or-amend question, names `occupancy_hourly` and Stages 3 and 4, and gives a
  default. Quote (B, rep2): "Do you approve the new stage, or would you rather amend the two `Consumes` (and if so, to
  what)?", after "Stage 3 has an unmet `Consumes`: Stage 2's `occupancy_hourly` table." and "Stage 4 has the same unmet
  `Consumes`."
- C passes in every rep. The default adds a stage, before Stages 3 and 4, that produces `occupancy_hourly`.
- D passes in every rep. No rep starts a completion review or parks the roadmap.
- The new rule at work. Each rep reads plan 5's "was not built" as Handoff evidence that the input is missing. Rep5: "It
  shows the input is missing, so the remaining stages are blocked". Rep3: "The table is therefore missing". No rep calls
  `occupancy_hourly` met or external.
- Plan 3's pending bullet. All five apply it as an amendment (the `lot_id` column). Rep1 dates it 2026-11-06, and reps 2
  to 5 date it 2026-11-07. It is not scored.

Other readings: Pending bullet: no effect. No other reading applies.

Running total: $7.0138 of $30.

### Plan 79 Task 3 round 2 summary and spend

| Case | Bar | Control | `T3-r1` (`43fca10`) | `T3-r2` (`99265a5`) | Result |
|---|---|---|---|---|---|
| dr-stop-track | additive | RED, A fails 5 of 5 (PASS 0 of 5) | PASS 5 of 5 | PASS 4 of 5 (5 of 5 by the other Date reading) | **MET** |
| dr-park-ranked | additive | RED, A fails 5 of 5 (PASS 0 of 5) | PASS 5 of 5 | PASS 3 of 5 (5 of 5 by the other Table items reading) | **MISSED** (needs 4 of 5) |
| dr-rerank-second | additive | RED, a bar clause fails in 4 of 5 (PASS 1 of 5) | PASS 5 of 5 | PASS 5 of 5 (4 of 5 by the other reading of rep5's C) | **MET** |
| dr-resume-marker | additive | clean (PASS 5 of 5) | PASS 5 of 5 | PASS 5 of 5 (2 of 5 by the other Carried citation reading) | control clean: owner gate; not below 4 of 5 |
| dr-resume-blocked | additive | clean (PASS 5 of 5) | PASS 5 of 5 | PASS 5 of 5 | control clean: owner gate; not below 4 of 5 |
| dr-name-collision | additive | RED, B fails 5 of 5 (PASS 0 of 5) | not re-run | not re-run (not reached) | **MET**, narrowly, at `T3` |

No rep was VOID.

**Owner gate: Task 3 Step 4.** dr-park-ranked falls below its bar: PASS 3 of 5. The failing clause is D, a conformance
clause, in reps 1 and 3, on the new Table items call (scored by the committed text). Quote (rep3): "I'll fit them to the
schema once I've read it.", followed by a table headed `| Item | From | Size | Done when |`. The cause is not this
round's text: the Parking text and the item rule did not change from `T3-r1`, and no earlier dr-park-ranked rep (0 of 15)
used a table. By the other Table items reading the case passes 5 of 5. No further round ran, as the controller directed.
The owner rules on the Table items reading and on the case.

- The review finding is fixed in the text. Neither file's rule uses a `Produces` name. In dr-resume-marker no rep reads the
  renamed output as missing or as an outside input, and every rep hands off Stage 3. In dr-resume-blocked every rep reads
  "was not built" as Handoff evidence and asks the one question.
- dr-stop-track passes 4 of 5. The one failure is a `<date>` placeholder heading (the Date reading). Every rep counts the
  live feed as met on the new rule and hands off Stage 2 with no condition.
- Two edge cases of the new rule are open, and no arm tests either. (1) The output of an unticked earlier stage has no
  Handoff or stamp, so the rule counts it as met. If that earlier stage is blocked, §4 could hand off a later stage that
  consumes its output, and "none has all its `Consumes` met" might not fire. (2) An output that a Handoff says shipped but
  is empty or unusable is caught only if "missing or not built" is read to include it.
- `T3-r2` (`99265a5`) is the last skill commit. Task 4's `T-final` waits on the owner's ruling at this gate.

**Spend.** `uv run python specs/red-baseline-new-project-entry/kit/show_reps.py` ran once over each of the five `-p79-r2`
folders after its last rep, and once over all five together (25 reps, none VOID, `total cost $1.61`). No rep file is
empty or unreadable, so none counts at its cap. There was no VOID rerun. The figures per case, from each rep's
`total_cost_usd`, are dr-stop-track $0.3294, dr-park-ranked $0.3252, dr-rerank-second $0.3123, dr-resume-marker $0.2965
and dr-resume-blocked $0.3468. The round cost $1.6102. Running total: $7.0138 of $30.

## Plan 79: Task 3 fix round 2 (review finding)

A scoped re-review of `T3-r2` found the first review finding addressed, and one new Important defect. The controller
accepted it as a review-found defect. This round adds one clause to the unmet rule, re-runs the five cases that the rule
reaches, and holds the owner's re-run of dr-park-ranked. Each rep was scored by hand from its full reply. No fixture,
rule or `cases.py` line changed. The sections below are headed "round 3", the third set of arms at a reworded text.

**The finding.** At `T3-r2` the rule read "A `Consumes` is unmet when a Handoff or stamp shows its input missing or not
built. With no such evidence it counts as met". An unticked stage has no Handoff and no stamp, so its outputs always
counted as met. The reviewer's chain:

1. A Handoff shows Stage 3's input missing, so Stage 3 is blocked.
2. Stage 4 consumes Stage 3's output.
3. That output has no evidence against it, so it counts as met, and §4's "first unticked one whose `Consumes` are all
   met" picks Stage 4.
4. "None has all its `Consumes` met" is false, so the one question never fires.
5. The partner gets a "Next:" line for Stage 4, whose input cannot exist until Stage 3 runs.

At `T3`, plain judgment held Stage 4 back, so this was a regression. The rename problem cannot come back: Amend keeps the
fields of unticked stages current, and only the fields of ticked stages go stale. The reviewer re-scored all five round-2
arms and agreed with every score.

**The controller's ruling.** Accept. The clause matches §4's own meaning (a stage is not ready while its producer is
unticked), so it completes the earlier direction. The rule is stated once. The plan's edit-2 sentence stays.

**The owner's ruling on dr-park-ranked** (3 of 5 at `T3-r2`, clause D failed in two reps that wrote tables). Run 5 more
independent reps and report both runs. If the new run passes at least 4 of 5, the case is recorded as met with both runs
shown. If not, the miss stays recorded. The round-3 arm of dr-park-ranked is that run.

**`T3-r3` is `5f52dfc`**, the full sha `5f52dfc75f7e55658b1f7eeb237845af7da06d54`, subject `fix(derive-roadmap): count a
Consumes from an unticked stage as unmet`. It follows `680d67d` and changes two files: `skills/derive-roadmap/SKILL.md`
(§5 only) and `skills/derive-roadmap/references/roadmap-format.md` (the one sentence of Task 3's edit 4). No description
changed. No example and no fixture detail is in the new text.

**The rule, `SKILL.md` §5 Ask bullet** (after "route only after the answer"):

- Old (`T3-r2`): "A `Consumes` is unmet when a Handoff or stamp shows its input missing or not built. With no such evidence
  it counts as met, and the receiving session checks it."
- New (`T3-r3`): "A `Consumes` is unmet when a Handoff or stamp shows its input missing or not built, or when the stage
  that is to produce it is unticked. Otherwise it counts as met, and the receiving session checks it."

**`references/roadmap-format.md`, edit 4:**

- Old (`T3-r2`): "..., where a `Consumes` is unmet only when a Handoff or stamp shows its input missing or not built
  (SKILL.md §5)."
- New (`T3-r3`): "..., where a `Consumes` is unmet only when a Handoff or stamp shows its input missing or not built, or the
  stage that is to produce it is unticked (SKILL.md §5)."

Why this wording:

- It is the reviewer's clause, unchanged. "With no such evidence" becomes "Otherwise", as the controller directed, so the
  second sentence covers both cases of the first.
- The clause names the producing stage by whether it is ticked, not by a `Produces` name of a ticked stage.
- The plan's edit-2 sentence and D4's question are unchanged.

**Checks after the edit.** Each check joins the file's lines (`tr '\n' ' ' | tr -s ' '`) and counts the phrase.

| File | Phrase | Expected | Got |
|---|---|---|---|
| `SKILL.md` | `no roadmap entry yet cites` | 1 | 1 |
| `SKILL.md` | `unticked stages remain and none has all its` | 1 | 1 |
| `SKILL.md` | ``names each unmet `Consumes` and the stages it blocks`` | 1 | 1 |
| `SKILL.md` | `Hand off nothing before the answer` | 1 | 1 |
| `SKILL.md` | `and, with no spec, a proposed roadmap name` | 1 | 1 |
| `SKILL.md` | `since the last resume` | 0 | 0 |
| `SKILL.md` | `<roadmap-name>` | 0 | 0 |
| `SKILL.md` | `## <name>-roadmap — <YYYY-MM-DD>` | 2 | 2 |
| `SKILL.md` | ``no stage's `Produces` `` | 0 | 0 |
| `SKILL.md` | `With no such evidence` | 0 | 0 |
| `SKILL.md` | ``A `Consumes` is unmet when a Handoff or stamp shows its input missing or not built, or when the stage that is to produce it is unticked`` | 1 | 1 |
| `SKILL.md` | `Otherwise it counts as met, and the receiving session checks it` | 1 | 1 |
| `roadmap-format.md` | `or the whole roadmap parks` | 1 | 1 |
| `roadmap-format.md` | `treats a stamped stage as new` | 1 | 1 |
| `roadmap-format.md` | ``no stage's `Produces` `` | 0 | 0 |
| `roadmap-format.md` | `is unmet only when a Handoff or stamp shows its input missing or not built, or the stage that is to produce it is unticked` | 1 | 1 |

The derive-roadmap body measures 16,125 characters (`len(check_conformance.skill_body(text)[0])`; 16,082 at `T3-r2`,
at most 20,000 allowed). `bash build/run_commit_lints.sh` printed `commit lints passed`, and the pre-commit hook printed it
again at the commit.

**Checks before any rep.**

- The CLI is Claude Code 2.1.316, the version that the isolation probe ran on, so the probe still holds.
- A `diff` of each `/tmp/plan79-work/t3-r2/<case>.txt` against its `/tmp/plan79-work/t3-r3/<case>.txt` shows two hunks,
  the same in all five prompts: the rule sentence in the Ask bullet and the `roadmap-format.md` sentence.
- A case-insensitive grep of the five prompts for `red-baseline`, `plan 7[89]`, `micro-test` and `task-3` found 0 hits
  (the quarantine).

**Build.**

```
CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py 5f52dfc75f7e55658b1f7eeb237845af7da06d54 /tmp/plan79-work/t3-r3 dr-stop-track dr-park-ranked dr-rerank-second dr-resume-marker dr-resume-blocked
```

It wrote 5 prompts. `MANIFEST.txt` is copied to `treatment/p79-t3-r3-MANIFEST.txt`. It shows `budget 1.00` for every
case. No case of this round reads a case-repository file.

**Reps.** Each case ran with
`bash specs/red-baseline-new-project-entry/kit/run_reps.sh /tmp/plan79-work/t3-r3/<case>.txt specs/red-baseline-new-project-entry/treatment/<case>-p79-r3 1 5 claude-opus-5-5 1.00`,
one case at a time, in this order: dr-stop-track, dr-park-ranked, dr-rerank-second, dr-resume-marker, dr-resume-blocked.
Each call finished before the next began. Before each call, the running total plus the call's worst case ($5.00) stayed
under $30. The largest such sum was $13.27, before the last call. Each case's replies were read in full from
`show_reps.py` over that case's folder alone. No rep was VOID, so no rerun was needed. No `.err` file was left.

**Why each case re-ran.** The rule decides when a `Consumes` is met, as in round 2, and the new clause adds one more case
to it.

| Case | Re-run | Reason |
|---|---|---|
| dr-stop-track | yes | The rule decides clause E: no stage is to produce the outside feed, so it must still count as met. |
| dr-park-ranked | yes | The rule decides whether Stage 2 is ready, and clause E checks that a park hands off nothing. The arm is also the owner's independent re-run. |
| dr-rerank-second | yes | §5 puts the re-rank inside "the ONE question of the Ask", so the Ask bullet frames clause C. |
| dr-resume-marker | yes | The rule decides clause C: Stage 3's producers are ticked and the Handoff says the table shipped, so Stage 3 must be handed off. |
| dr-resume-blocked | yes | The rule decides clauses A, B and C: "was not built" must still make the one question fire. |
| dr-name-collision | no | Not reached. §3, §7 and the New-project name rule are unchanged, and the reply stops at the name question. Its `T3` result (4 of 5, MET narrowly) stands. |

**No arm tests the new clause.** No fixture has a blocked chain. A test would need a roadmap where a Handoff shows Stage
3's input missing, and Stage 4 consumes Stage 3's output. Its pass rule would need one question that names the unmet
input and both blocked stages, and no "Next:" line for Stage 4. This is a note for the owner. No case was added, because
cases and fixtures stay unchanged in this task.

**Readings applied (round 3).** Every reading of the Control section applies: Review by table, Another name, Carried
citation, Pending bullet, Item by description, Date and Stage 2's live feed. Name and Conditional handoff are reported as
other readings. The round-2 Table items call applies again: clause D is scored by its committed text, so a table row with
no `Size:` or `Done when:` label fails D, and the lenient reading is the other reading. Two earlier practices apply too:
inline `Size:` and `Done when:` fields count as the two lines of clause D, and the one question may close with its
alternatives ("Do you approve? Or would you ...?").

**Judgment-call reps.** The owner can review them at the completion gate. The quote column gives the other reading's
effect where it changes a count.

| Case, rep, clause | Score | Deciding quote |
|---|---|---|
| dr-park-ranked rep3, D | fail (Table items, by the committed text) | A table headed `\| Item \| Size \| Done when \|`, then "The four items above get reshaped to fit it." The other reading passes D, which makes D and PASS 5 of 5. The bar is met either way. |
| dr-park-ranked rep2, D | pass (inline fields) | "Size: small, one closure-log poll every 10 minutes. Done when: the notice job and its operator mailing list exist". The other reading fails D in rep2, which makes D and PASS 3 of 5 and the bar missed. |
| dr-stop-track rep4, D | pass (inline fields) | "Size: about a day (one static map page). Done when: the map page is published to operators." The other reading fails D in rep4, which makes D and PASS 4 of 5. The bar is still met. |
| dr-rerank-second reps 3 and 4, C | pass (one question with its alternatives) | rep3: "Do you approve? Or would you change it: keep O3 first, promote O3 instead, or stop Track A?" rep4: "Do you approve? Or would you like a different change: promote O4 first, reorder the list, or stop the track?" The other reading (two questions) fails C in both reps, which makes C and PASS 3 of 5 and the bar missed. |
| dr-resume-blocked rep2, B | pass (one question with its alternative) | "**Question:** Do you approve adding a new Stage 3 that produces `occupancy_hourly`?" and, after its bullets, "Or would you rather amend their `Consumes`, ...?" The other reading (two questions) fails B in rep2, which makes B and PASS 4 of 5. |
| dr-resume-marker reps 4 and 5, B | pass (old citation carried over) | rep4: "Consumes: Stage 1's `bay_events` table, with the car park in its `lot_id` column (plan 3, Handoff; Resolved at resume, 2026-10-12); Stage 2's occupancy table, shipped as `occupancy_by_hour` (plan 5, Handoff; Resolved at resume, 2026-11-06)". The other reading fails B in these reps, which makes B and PASS 3 of 5. |

### Plan 79 Task 3 round 3: dr-stop-track

Additive. Texts at `5f52dfc` (`T3-r3`). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.3265.

The partner answers "Stop Track A" in a roadmap with two tracks. Clause A (bar) appends one item each for O2, O3 and O4
to `specs/deferred_items.md` and none for Stage 2 or O5. Clause B (bar) keeps the roadmap live. Clause C (conformance)
puts the items under one dated heading. Clause D (conformance) gives each item a `Size:` and a `Done when:`. Clause E
(conformance) hands off Stage 2 with a "Next:" line and starts no completion review.

| Rep | A (bar) | B (bar) | C (conformance) | D (conformance) | E (conformance) | PASS |
|---|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | pass | yes |
| 2 | pass | pass | pass | pass | pass | yes |
| 3 | pass | pass | pass | pass | pass | yes |
| 4 | pass | pass | pass | pass (inline fields) | pass | yes |
| 5 | pass | pass | pass | pass | pass | yes |

Clause A: 5 of 5 (control 0 of 5, `T3-r2` 5 of 5). Clause B: 5 of 5 (control 5 of 5, `T3-r2` 5 of 5). Clause C: 5 of 5
(control 0 of 5, `T3-r2` 4 of 5). Clause D: 5 of 5 (control 0 of 5, `T3-r2` 5 of 5). Clause E: 5 of 5 (control 5 of 5,
`T3-r2` 5 of 5). PASS: 5 of 5 (control 0 of 5, `T3-r2` 4 of 5).

**Bar verdict: MET.** The treatment passes every clause in 5 of 5 reps, and the control fails clause A, a bar clause, in 5
of 5.

- A passes in every rep. Each writes three items, one each for O2, O3 and O4, as the content of an append to
  `specs/deferred_items.md`, and none for Stage 2 or O5. Rep4 writes each item as one bullet with inline fields.
- B passes in every rep. Each replaces the Ranked list's body with a stop note and commits. None moves the roadmap or
  marks it PARKED, and Stage 2's entry stays. Rep3 adds a "(Resolved at resume, 2026-11-06)" marker to its stop note, which
  no clause scores.
- C passes in every rep. Each uses the heading `## lock-closures-roadmap — 2026-11-06`. Rep4 names it in prose in its
  append step.
- D passes in every rep. Each item has a `Size:` and a `Done when:` that names its outcome. Rep4 writes them inline (see
  the judgment-call table).
- E passes in every rep. Each ends with "Next: /clear (or a fresh session), then writing-plans on Stage 2 of
  `specs/lock-closures-roadmap.md`." (rep5 sets "Next:" in bold) and plans nothing. No rep starts a completion review.
  Rep2 puts "Once the commit above has landed:" before its "Next:" line. That orders the handoff after the commit, as §5
  Commit asks, and is not a condition on the feed.
- Stage 2's live feed. All five count it as met, and none asks about it. Rep1: "No Handoff or stamp shows it missing, so it
  counts as met, and the Stage 2 session will check it." Rep2: "No stage produces the feed and no Handoff says it is
  missing, so it counts as met". Reps 2 and 3 note that no stage produces the feed, so the new clause does not apply to it.

Other readings: Conditional handoff: no "Next:" line is conditional on the feed. Rep2's "Once the commit above has
landed:" orders the line after the commit, so the strict reading also passes E in reps 1 to 5. Inline fields: rep4
(judgment-call table), D and PASS 4 of 5 on the other reading, bar still met. Name, Date and Item by description: no
effect.

Running total: $7.3403 of $30.

### Plan 79 Task 3 round 3: dr-park-ranked

Additive. Texts at `5f52dfc` (`T3-r3`). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.3368.

The partner answers "Park the whole roadmap" in the same roadmap. Clause A (bar) appends four items, one each for Stage 2,
O2, O3 and O4. Clause B (bar) moves the roadmap to `specs/completed/` marked PARKED with the date and "1 of 2 stages
complete". Clause C (conformance) puts the items under one heading `## <roadmap name> — 2026-11-06`. Clause D
(conformance) gives each item a `Size:` and a `Done when:`. Clause E (conformance) starts no completion review and hands
off no stage.

This arm is the owner's independent re-run. The `T3-r2` and `T3-r3` texts differ only in the Ask bullet's rule sentence
and its copy in the `roadmap-format.md` sentence. The Parking text and the item rule are the same in both, so the two
arms run the same park behavior.

**The two runs side by side.**

| Rep | `T3-r2` A | B | C | D | E | PASS | `T3-r3` A | B | C | D | E | PASS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | pass | pass | pass | fail (table) | pass | no | pass | pass | pass | pass | pass | yes |
| 2 | pass | pass | pass | pass | pass | yes | pass | pass | pass | pass (inline fields) | pass | yes |
| 3 | pass | pass | pass | fail (table) | pass | no | pass | pass | pass (run-day date) | fail (table) | pass | no |
| 4 | pass | pass | pass (run-day date) | pass | pass | yes | pass | pass | pass | pass | pass | yes |
| 5 | pass | pass | pass | pass | pass | yes | pass | pass | pass | pass | pass | yes |

`T3-r2`: A 5, B 5, C 5, D 3, E 5. PASS 3 of 5 (5 of 5 by the other Table items reading).

`T3-r3`: Clause A: 5 of 5 (control 0 of 5). Clause B: 5 of 5 (control 5 of 5). Clause C: 5 of 5 (control 4 of 5). Clause
D: 4 of 5 (control 4 of 5; 5 of 5 by the other Table items reading). Clause E: 5 of 5 (control 5 of 5). PASS: 4 of 5
(control 0 of 5; 5 of 5 by the other Table items reading).

Both runs together: PASS 7 of 10, and 10 of 10 by the other Table items reading. Three of the ten reps wrote table items.

**Bar verdict: MET, by the owner's rule.** The new run passes 4 of 5, which is the bar, and the control fails clause A, a
bar clause, in 5 of 5. By the owner's ruling the case is recorded as met, with both runs shown. The `T3-r2` miss (3 of 5)
stays in the record above. The `T3-r3` verdict rests on one close call: rep2's inline fields. On the other reading of that
call, PASS is 3 of 5.

- A passes in every rep. Each appends four items: one for Stage 2 (the notices) and one each for O2, O3 and O4. Rep3
  gives them as four table rows, one per item. Rep2 gives them as four bullets with inline fields.
- B passes in every rep. Each runs `git mv` to `specs/completed/` and adds a PARKED line with "1 of 2 stages complete".
  Reps 1, 2, 4 and 5 date it 2026-11-06, and rep3 dates it 2026-11-07. Quote (B, rep4): "PARKED (2026-11-06) — 1 of 2
  stages complete."
- C passes in every rep. Reps 1, 2, 4 and 5 use `## lock-closures-roadmap — 2026-11-06`. Rep3 uses
  `## lock-closures-roadmap — 2026-11-07`, the run day's date, which passes by the Date reading.
- D fails in rep3 only (Table items). Quote (D, rep3): a table headed `| Item | Size | Done when |`, then "The four items
  above get reshaped to fit it." Reps 1, 4 and 5 write each item as a block with `Size:` and `Done when:` lines. Rep2
  writes them inline (see the judgment-call table). Each `Done when:` names Stage 2's Produces or the item's outcome.
- E passes in every rep. No rep starts a completion review or hands off a stage. Rep2 offers to keep the roadmap live for
  Stage 2 "If the notices should go ahead under other funding", and parks it by default. That offer hands off nothing.
- Stage 2's live feed. No rep treats it as unmet or asks about it. Reps 1, 2, 4 and 5 carry it into the Stage 2 item as its
  source.

Other readings: Table items: rep3 passes D on the other reading, so D and PASS are 5 of 5. Inline fields: rep2's D fails on
the other reading, so PASS is 3 of 5 and the new run would miss. Date: on a reading that allowed only 2026-11-06, rep3's C
would also fail, with no change to PASS (rep3 already fails). Name and Item by description: no effect.

Running total: $7.6771 of $30.

### Plan 79 Task 3 round 3: dr-rerank-second

Additive. Texts at `5f52dfc` (`T3-r3`). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.2932.

A second re-rank question, after Stage 2 (the 7-day outlook) is ticked and stamped. Clause A (bar) starts no completion
review and does not park or retire the roadmap. Clause B (bar) reports Stage 2's finding and its measured cost. Clause C
(bar) is one question with a default that asks for a re-ranking of O3 and O4 or approval of a proposed next stage.
Clause D (conformance) writes no stage entry and does not offer O2 again.

| Rep | A (bar) | B (bar) | C (bar) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | yes |
| 2 | pass | pass | pass | pass | yes |
| 3 | pass | pass | pass (borderline, alternatives) | pass | yes |
| 4 | pass | pass | pass (borderline, alternatives) | pass | yes |
| 5 | pass | pass | pass | pass | yes |

Clause A: 5 of 5 (control 2 of 5, `T3-r2` 5 of 5). Clause B: 5 of 5 (control 2 of 5, `T3-r2` 5 of 5). Clause C: 5 of 5
(control 5 of 5, `T3-r2` 5 of 5). Clause D: 5 of 5 (control 5 of 5, `T3-r2` 5 of 5). PASS: 5 of 5 (control 1 of 5, `T3-r2`
5 of 5).

**Bar verdict: MET.** The treatment passes every clause in 5 of 5 reps, and the control fails a bar clause in 4 of 5. The
verdict rests on the one-question reading in reps 3 and 4. On the other reading, PASS is 3 of 5 and the bar is missed.

- A passes in every rep. Each says that the step is a re-rank and not the completion review. Rep1: "the completion review
  (§6) waits until the Ranked list is either promoted or parked." No rep gives a table over the Outcomes list.
- B passes in every rep, and each gives both parts. Rep5: "the 7-day outlook flagged 81% of closures at least 2 days ahead,
  with one false alarm in 9." and "14 minutes a day on one small VM, using 0.3 GB of forecasts."
- C passes in every rep. Each puts one approve-or-amend question with a default. Reps 1, 3 and 5 propose to re-rank O4
  first and promote it. Reps 2 and 4 keep the order and promote O3. Rep2's "Do you approve that? If not, you could ..."
  follows its question with a statement of the options. Reps 3 and 4 close with "Do you approve? Or would you ...?" (see the
  judgment-call table).
- D passes in every rep. Each writes the stage entry only after the answer, and no rep offers O2 again.
- The new rule at work. Reps 4 and 5 note that no unticked stage remains for a Handoff to change. No rep names an unmet
  `Consumes`.

Other readings: One question: reps 3 and 4 fail C on the other reading, so C and PASS are 3 of 5 and the bar is missed.
Review by table: no effect.

Running total: $7.9703 of $30.

### Plan 79 Task 3 round 3: dr-resume-marker

Additive. Texts at `5f52dfc` (`T3-r3`). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.2999.

Stage 3's entry already cites plan 3's Handoff, marked "Resolved at resume, 2026-10-12". Only plan 5's Handoff bullet is
new. Clause A (bar) amends the Consumes of Stage 3 and Stage 4 from plan 5's bullet and cites plan 5, Handoff. Clause B
(bar) does not apply or restate plan 3's bullet again. Clause C (conformance) commits and hands off Stage 3 with a
"Next:" line and plans nothing.

| Rep | A (bar) | B (bar) | C (conformance) | PASS |
|---|---|---|---|---|
| 1 | pass | pass | pass | yes |
| 2 | pass | pass | pass | yes |
| 3 | pass | pass | pass | yes |
| 4 | pass | pass (borderline, carried citation) | pass | yes |
| 5 | pass | pass (borderline, carried citation) | pass | yes |

Clause A: 5 of 5 (control 5 of 5, `T3-r2` 5 of 5). Clause B: 5 of 5 (control 5 of 5, `T3-r2` 5 of 5; 3 of 5 by the other
reading, control 3 of 5). Clause C: 5 of 5 (control 5 of 5, `T3-r2` 5 of 5). PASS: 5 of 5 (control 5 of 5, `T3-r2` 5 of 5;
3 of 5 by the other reading).

**Bar verdict: control clean: owner gate.** The control fails no clause, so the additive bar cannot be met. The treatment
passes in 5 of 5 reps, which is not fewer than 4 of 5, so it does not miss its bar. The new clause reverts nothing.

- A passes in every rep. Each amends both entries to `occupancy_by_hour` and cites "plan 5, Handoff" with a Resolved
  marker. Quote (A, rep2): "+ ...; Stage 2's `occupancy_by_hour` table (plan 5, Handoff; Resolved at resume, 2026-11-07)".
- B passes in every rep. Each says that plan 3's point is already in Stage 3 and changes nothing for it. Reps 4 and 5 write
  the whole Stage 3 line with plan 3's citation carried over unchanged (see the judgment-call table). Reps 1, 2 and 3
  show only the changed part.
- C passes in every rep. Each commits on `main` and ends with "Next: /clear (or a fresh session), then brainstorming on
  Stage 3 of `specs/parking-occupancy-spec-roadmap.md`." and plans nothing. Reps 3 and 4 note that Stage 4's inputs are met
  too, and hand off only Stage 3.
- The new clause at work. Reps 2, 4 and 5 give the ticked producers as the reason that Stage 3's inputs are met. Rep4:
  "Both stages' `Consumes` are met: Stages 1 and 2 are ticked, and no Handoff shows an input missing." No rep reads the
  rename as missing, and no rep asks. Reps 1, 2, 3 and 5 leave Stage 2's ticked `Produces` as it is.
- Dates. Reps 1, 4 and 5 date the new marker 2026-11-06, and reps 2 and 3 date it 2026-11-07. Reps 3 and 5 say that the
  session and the environment disagree. No clause scores the date.

Other readings: Carried citation: reps 4 and 5 fail B on the other reading, so B and PASS are 3 of 5. That reading gives
the control 3 of 5. It is not counted.

Running total: $8.2702 of $30.

### Plan 79 Task 3 round 3: dr-resume-blocked

Additive. Texts at `5f52dfc` (`T3-r3`). Scored reps: rep1 to rep5. No VOID rep. Spend: $0.3498.

Plan 5's Handoff says that `occupancy_hourly` was not built, and Stage 3 and Stage 4 consume it. Plan 3's bullet is still
pending. Clause A (bar) hands off no stage before the answer. Clause B (bar) is one question that names the unmet
Consumes and the stages that it blocks, with a proposed default. Clause C (conformance) has a default that adds a stage
that produces the table or amends the Consumes. Clause D (conformance) starts no completion review and parks nothing.

| Rep | A (bar) | B (bar) | C (conformance) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | yes |
| 2 | pass | pass (borderline, alternative) | pass | pass | yes |
| 3 | pass | pass | pass | pass | yes |
| 4 | pass | pass | pass | pass | yes |
| 5 | pass | pass | pass | pass | yes |

Clause A: 5 of 5 (control 5 of 5, `T3-r2` 5 of 5). Clause B: 5 of 5 (control 5 of 5, `T3-r2` 5 of 5; 4 of 5 by the other
reading). Clause C: 5 of 5 (control 5 of 5, `T3-r2` 5 of 5). Clause D: 5 of 5 (control 5 of 5, `T3-r2` 5 of 5). PASS: 5 of
5 (control 5 of 5, `T3-r2` 5 of 5; 4 of 5 by the other reading).

**Bar verdict: control clean: owner gate.** The control fails no clause, so the additive bar cannot be met. The treatment
passes in 5 of 5 reps, which is not fewer than 4 of 5, so it does not miss its bar. The new clause reverts nothing.

- A passes in every rep. No rep writes a "Next:" line that names a stage. Rep1: "I'll hand off the next stage only after
  your answer." Rep5 says that the "Next:" line comes after the answer and names no stage in it. Reps 1, 2 and 5 write a
  commit before the answer, which is not a handoff (the Pending bullet reading). Rep1's commit also marks both `Consumes`
  "NOT BUILT", which no clause scores.
- B passes in every rep. Each puts one approve-or-amend question, names `occupancy_hourly` and Stages 3 and 4, and gives a
  default. Quote (B, rep1): "The missing input is Stage 2's `occupancy_hourly` table (R4), which blocks both Stage 3
  (dashboard and alerts) and Stage 4 (weekly report)." and "Approve the default, or amend it?" Rep2 closes its question
  with "Or would you rather amend their `Consumes`, ...?" (see the judgment-call table).
- C passes in every rep. The default adds a stage, before Stages 3 and 4, that produces `occupancy_hourly`.
- D passes in every rep. No rep starts a completion review or parks the roadmap. Rep5 names the Completion audit only as a
  later check of R4.
- The new rule at work. Each rep reads plan 5's "was not built" as Handoff evidence that the input is missing. Rep2: "The
  bullet does show that Stage 2's output is missing." No rep calls `occupancy_hourly` met.
- Plan 3's pending bullet. All five apply it as an amendment, dated 2026-11-07. It is not scored.

Other readings: One question: rep2 fails B on the other reading, so B and PASS are 4 of 5. Pending bullet: no effect.

Running total: $8.6200 of $30.

### Plan 79 Task 3 round 3 summary and spend

| Case | Bar | Control | `T3-r2` (`99265a5`) | `T3-r3` (`5f52dfc`) | Result |
|---|---|---|---|---|---|
| dr-stop-track | additive | RED, A fails 5 of 5 (PASS 0 of 5) | PASS 4 of 5 | PASS 5 of 5 (4 of 5 by the other inline-fields reading) | **MET** |
| dr-park-ranked | additive | RED, A fails 5 of 5 (PASS 0 of 5) | PASS 3 of 5 (missed) | PASS 4 of 5 (5 of 5 by the other Table items reading; 3 of 5 by the other inline-fields reading) | **MET** by the owner's rule, with both runs shown |
| dr-rerank-second | additive | RED, a bar clause fails in 4 of 5 (PASS 1 of 5) | PASS 5 of 5 | PASS 5 of 5 (3 of 5 by the other one-question reading) | **MET** |
| dr-resume-marker | additive | clean (PASS 5 of 5) | PASS 5 of 5 | PASS 5 of 5 (3 of 5 by the other Carried citation reading) | control clean: owner gate; not below 4 of 5 |
| dr-resume-blocked | additive | clean (PASS 5 of 5) | PASS 5 of 5 | PASS 5 of 5 (4 of 5 by the other one-question reading) | control clean: owner gate; not below 4 of 5 |
| dr-name-collision | additive | RED, B fails 5 of 5 (PASS 0 of 5) | not re-run | not re-run (not reached) | **MET**, narrowly, at `T3` |

No rep was VOID. No case is below 4 of 5 at `T3-r3`, so this round ends with no owner gate for Task 3 Step 4. The
round-2 gate on dr-park-ranked is closed by the owner's re-run rule: the new run passes 4 of 5.

- The second finding is fixed in the text. An input whose producing stage is unticked is unmet. No arm tests that clause
  (see "No arm tests the new clause" above). In the arms that do run, the clause changes no result. In dr-resume-marker
  the reps give the ticked producers as the reason that Stage 3 is ready.
- Three verdicts rest on one close call each. They are dr-park-ranked rep2 (inline fields), dr-rerank-second reps 3 and 4
  (one question with its alternatives) and, at `T3`, dr-name-collision rep2. The counted readings follow the practice of
  every earlier arm of these cases.
- Format variance in dr-park-ranked: 3 of 10 reps across `T3-r2` and `T3-r3` wrote the items as table rows, and 0 of 15
  before that.
- `T3-r3` (`5f52dfc`) is the last skill commit. Task 4 reads it as `T-final`, unless the owner rules otherwise.

**Spend.** `uv run python specs/red-baseline-new-project-entry/kit/show_reps.py` ran once over each of the five `-p79-r3`
folders after its last rep, and once over all five together (25 reps, none VOID, `total cost $1.61`). No rep file is
empty or unreadable, so none counts at its cap. There was no VOID rerun. The figures per case, from each rep's
`total_cost_usd`, are dr-stop-track $0.3265, dr-park-ranked $0.3368, dr-rerank-second $0.2932, dr-resume-marker $0.2999
and dr-resume-blocked $0.3498. The round cost $1.6062. Running total: $8.6200 of $30.

## Plan 79: re-runs

Task 4 runs six re-runs at the final skill text. A re-run has a treatment arm only. Each arm compares with the plan 78 arm that the plan names. A rep is one fresh `claude -p` run with no tools. Each rep was scored by hand from its full reply, by the case's committed rule and by the readings below. No fixture, rule or `cases.py` line changed.

**`T-final` is `T3-r3`**, `5f52dfc`, the full sha `5f52dfc75f7e55658b1f7eeb237845af7da06d54`, subject `fix(derive-roadmap): count a Consumes from an unticked stage as unmet`. It is the last skill commit. The brief names `T3-r1` as the text to read. That is out of date, because Task 3 ran two more rounds after `T3-r1` (`T3-r2` and `T3-r3`). `git diff --stat 5f52dfc -- skills/` prints nothing, so no skill file changed after `T-final`.

**Checks before any rep.**

- The CLI is Claude Code 2.1.316, the version that the isolation probe ran on, so the probe still holds.
- A case-insensitive grep of the five prompts and the manifest for `red-baseline`, `plan 7[89]`, `micro-test` and `task-4` found 0 hits (the quarantine).
- Each prompt holds the `T3-r3` Ask sentence ("or when the stage that is to produce it is unticked") once. The dr-offer-yes prompt holds "with no spec, a proposed roadmap name" once.
- The case-repository reads (the sec-edgar spec for two cases and the four ces-revisions files for dr-tracks) have the same sha256 as the reads in `control/MANIFEST.txt`.
- `git show 5f52dfc:skills/derive-roadmap/references/roadmap-format.md` holds "or the whole roadmap parks (SKILL.md §5)". `git show 5f52dfc:skills/derive-roadmap/SKILL.md` holds "and, with no spec, a proposed roadmap name" in §7 step 4.

**Build.**

```
CASE_REPOS="$HOME/Projects" uv run python specs/red-baseline-new-project-entry/kit/build_prompts.py 5f52dfc75f7e55658b1f7eeb237845af7da06d54 /tmp/plan79-work/t4 dr-known-progression-79 dr-tracks dr-resume-rerank dr-resume-legacy dr-offer-yes
```

It wrote 5 prompts. `MANIFEST.txt` is copied to `treatment/p79-t4-MANIFEST.txt`. It shows `budget 1.00` for every case.

**Reps.** Each folder ran with
`bash specs/red-baseline-new-project-entry/kit/run_reps.sh /tmp/plan79-work/t4/<case>.txt specs/red-baseline-new-project-entry/treatment/<folder> 1 5 claude-opus-5-5 1.00`.
The six calls ran in this order: dr-known-progression-79 into `dr-known-progression-79-p79`, dr-tracks into `dr-tracks-p79a`, dr-tracks again into `dr-tracks-p79b`, dr-resume-rerank into `dr-resume-rerank-p79`, dr-resume-legacy into `dr-resume-legacy-p79` and dr-offer-yes into `dr-offer-yes-p79`. The two dr-tracks runs are separate calls from the same prompt, so they are independent runs. Each call ran alone, as a background job. The next call started while the previous folder was being scored. No wording round could follow a score in this task, so the order did not change any result. Before each call, the running total plus the call's worst case ($5.00) stayed under $30. The largest such sum was $16.38, before the last call. No rep was VOID, so no rerun was needed. No `.err` file was left.

**Readings applied.**

- *Date.* No clause of these five cases fixes a date. The Date reading of the Plan 79 control section was not needed. Every fixture says "Today is 2026-11-06" and the CLI date line gives 2026-11-07. No clause scores a date.
- *Plan 79's own readings.* Review by table, Another name, Carried citation, Pending bullet, Item by description and Stage 2's live feed belong to the six route and resume cases of Tasks 2 and 3. They do not apply here.
- *dr-tracks, reading of record.* Open for plan review item 4: an order of outcomes inside a known-progression track, not called stages, is not a stage list. The other reading of item 4 is that such an order is a stage list. It is reported under "Other readings" and never counts toward a bar.
- *Every other case.* The readings of plan 78's record apply: By reference, Labeled list, Dependency fact or proposed order, and Stage list (all in the Control section). The owner's ruling of 2026-11-07 also applies: a reply that names a core stage and later stages for the hardening, inside the offer or the one message, counts as a stage list (the retired dr-offer-yes item in `specs/deferred_items.md`). It applies to dr-tracks too. The 2026-11-07 item of `specs/deferred_items.md` that names the ruling says that dr-offer-scaffold and dr-tracks read the same text and need a re-run.
- *Stage word* (dr-tracks clause C, new and not confirmed). Item 4 says "not called stages". The test used here is the one plan 78's round 2 rep5 applied: does the reply use the word "stages" for its own proposed order? If it does, the order is a stage list and clause C fails. The skill's own definition of a known-progression track is "your partner can name its stages from first to last" (`references/new-project-entry.md`, Outcomes and tracks, in the text at `T-final`). Several replies repeat that definition next to their order. This reading counts such a reply as calling its order stages. The reading was set when the close call first appeared (run a rep4). It was then applied to every rep of both runs.
- *Provenance on bytes* (dr-known-progression-79 clause C on traceability, new and not confirmed). Traceability is "a provenance or lineage record per row" (the rule's clause B). A stage that keeps provenance on retained bytes and links no row to its source does not name traceability. This is a new call. The nearest plan 78 call is fix round 1's on rep2 ("no trace from a row to its source"). That rep (`treatment/dr-known-progression-t7b/rep2`) has no "provenance" and no §4.5 citation, only "retained raw source bytes, manifests and versioned publication". So it settles nothing for a rep that uses the word. Rep2 here also cites "(background spec R6, R9, §4.5, §4.6)" in the same Objective. Section 4.5's row contract holds the per-row `source_id` and `source_sha256`. The By-reference reading is scoped to Exit fields, so the citation gets no credit here. Plan 78's control is RED only because that reading followed a pointer from an Exit to the same section. The test is applied at face value, as the Stage word reading is.
- *First stage per outcome* (dr-known-progression-79 clause A, new and not confirmed). Clause A asks that committed stages cover the index files, the submissions and 10-K and 8-K handling, in order. A reply that gives each outcome a core stage on one quarter, and then the full-range stages, passes when the first stage for each outcome is in that order. Rep2 puts its full index history at Stage 5, after its 10-K core at Stage 3. Plan 78 never ruled on outcomes that interleave. The strict reading, that a stage for an earlier outcome must not follow a stage for a later one, fails rep2 and rep5.
- *Echo* (the other reading of the Stage word, dr-tracks clause C, not counted). The phrase "name its stages first to last" only repeats the kind's definition and does not label the order as stages. It has two forms. Bare Echo counts the phrase as an echo when no order is attached to it in the same sentence by a colon or parentheses. Attached Echo also counts an order that is attached in that way. Neither form passes a reply that calls its own order "Track A's stage sequence", because that is the reply's own label. The counts for each run are in the Other readings of the two dr-tracks runs.

### Plan 79 Task 4: dr-known-progression-79

Additive. Texts at `5f52dfc` (`T-final`). Rule `DR_KNOWN_PROGRESSION_PASS_79`. Scored reps: rep1 to rep5. No VOID rep. Spend: $1.0925.

The reply writes the full roadmap file for SEC filing ingestion, and the one-line message. Clause B (bar): the first stage's Exit requires no manifest, no traceability and no point-in-time awareness. Clause A (conformance): stages cover the index files, the submissions and 10-K and 8-K handling, in order. Clause C (conformance): a manifest and traceability each appear in a named later stage. Point-in-time awareness is not scored for this fixture (owner ruling, 2026-11-07). Clause D (conformance): every stage entry has a field for what it leaves out. Clause E (recorded): the first stage's Exit does not require atomic publication of complete generations.

| Rep | B (bar) | A (conformance) | C (conformance) | D (conformance) | E (recorded) | PASS |
|---|---|---|---|---|---|---|
| 1 | pass (borderline) | pass | pass | pass | pass | yes |
| 2 | pass (borderline) | pass (borderline) | fail | pass | pass | no |
| 3 | pass | pass | pass | pass | pass | yes |
| 4 | pass | pass | pass | pass | pass | yes |
| 5 | pass (borderline) | pass (borderline) | fail | pass | pass | no |

Clause B: 5 of 5 (plan 78 control 4 of 5 by the by-reference reading). Clause A: 5 of 5 (control 5 of 5). Clause C: 3 of 5, which is manifest 4 of 5 and traceability 4 of 5 (control 0 of 5, scored with point-in-time, and no control rep names a manifest). Clause D: 5 of 5 (control 0 of 5). Clause E (recorded): 5 of 5 (control 4 of 5). PASS: 3 of 5.

Compared with plan 78's "Control: dr-known-progression": RED in 1 of 5 (rep5 fails bar clause B, by the by-reference reading). The control is RED, so the additive bar needs the treatment to pass every clause in at least 4 of 5 reps. Bar: **missed** (PASS 3 of 5), through conformance clause C. Bar clause B is 5 of 5.

- B. No first-stage Exit names a manifest, a per-row provenance record, as-of awareness or a spec section. Reps 1 and 5 ask for a count per source file ("with row counts reported per source", "with a row count per source"), and rep2 asks that "its row count matches the source files". Each is a count and not a manifest, as Task 7 rep5 and fix round 1 rep2 read it. In each, `Leaves out` sends the manifest and provenance to a later stage.
- A. Every rep puts the index work first, then the submissions, then 10-K and 8-K handling. Rep2 and rep5 do not run each outcome to its full range in turn. Rep2 gives each outcome a core stage on one quarter (Stages 1 to 3) and then the full-history stages (Stages 5 to 7). Rep5 puts a one-quarter 10-K and 8-K stage (Stage 4) before the full-history submissions (Stage 5) and says so: "Full-history submission download (Stage 5) comes after 10-K/8-K handling on one quarter (Stage 4)." Both pass on the order of the first stage for each outcome.
- C, manifest. Reps 1 to 4 name a manifest in a later stage, for example rep4's Stage 5: "a manifest of sources, snapshots and processing states". Rep5 names no manifest of any kind in any stage. Its Stage 6 holds "Provenance, replay, reconciliation and validation". Quote (C, rep5): "Make every output traceable to retained source bytes, add quarterly reconciliation, and cover the system with a full validation suite."
- C, traceability. Reps 1, 3, 4 and 5 link each output to its source. Rep4's Stage 5 Exit: "each output row names its source file and content hash". Rep2 does not. Quote (C, rep2, Stage 4 Objective): "Retain original bytes with provenance and make parsing and extraction replayable without SEC requests". Its later stages hold no per-row link to a source file. Its `Produces` line says "hash-addressed raw index files" and its Stage 8 says "withdrawal approvals bound to source hashes". Neither links a row.
- D and E pass in every rep. No Stage 1 Exit requires a publication pointer or an atomic generation.
- Point-in-time awareness (not scored). Rep3 names "point-in-time generations and reconciliation" in Stage 6. No other rep names it.
- Name (not scored). All five write `specs/sec-filing-ingestion-roadmap.md`, the name that the partner confirmed.

Other readings:

- The other reading of Provenance on bytes. If rep2's "with provenance" and its citation of spec §4.5 name traceability, rep2 passes C. PASS is then 4 of 5 and the bar is met, but only on the First stage per outcome reading of clause A. On the strict reading of A, rep2 fails A and PASS stays 3 of 5.
- The strict reading of clause A. If a stage for one outcome that follows a stage for the next outcome is out of order, rep2 and rep5 fail A. Rep5 already fails C. Rep2 then fails A even when it passes C, so PASS stays 3 of 5. The First stage per outcome reading is new and not confirmed.
- By reference (clause B of the control). By the other reading, plan 78's control is clean (B 5 of 5), so there is no RED to beat. Open for plan review item 2 asks that this be said here.

### Plan 79 Task 4: dr-tracks, run a

Additive. Texts at `5f52dfc`. Folder `dr-tracks-p79a`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.6731.

The partner says "Go ahead and stage it." for the CES revisions brief. Clause A (bar): the collection-interval outcome and the budget and staffing outcome sit in different tracks, and the reply says why. Clause B (conformance): no ranking is given as settled, and the reply asks the partner to rank. Clause C (conformance): one message with no roadmap text and no stage list. Clause D (conformance): a cost note for model fitting, with a basis or a statement that a run measures it.

| Rep | A (bar) | B (conformance) | C (conformance) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | pass | pass | pass (borderline) | pass | yes |
| 2 | pass | pass | pass | pass | yes |
| 3 | pass | pass | pass (borderline) | pass | yes |
| 4 | pass | pass | fail (borderline) | pass | no |
| 5 | pass | pass (borderline) | fail (borderline) | pass | no |

Clause A: 5 of 5 (control 0 of 5). Clause B: 5 of 5 (control 0 of 5). Clause C: 3 of 5 (control 3 of 5). Clause D: 5 of 5 (control 0 of 5). PASS: 3 of 5 (control 0 of 5, Task 7 5 of 5, both Task 3 rounds 2 of 5).

Compared with plan 78's "Control: dr-tracks": RED in 5 of 5 (bar clause A fails in every rep). The bar for each run is at least 4 of 5. Bar: **missed** (PASS 3 of 5), through conformance clause C. Bar clause A is 5 of 5.

- A. Every rep puts the collection-interval outcome in one track and the budget and staffing outcome in another, with a reason. Rep4: "I split C from D because a collection-interval answer stands without a capacity answer, and vice versa." Rep5: "B through E each answer a question that stands without the others."
- B. Every rep asks the partner to rank, and no rep states an order as decided. Rep5 passes, borderline, by the dependency-fact reading: "Every other track consumes A's panel, so A's core stage goes first regardless of ranking."
- C, reps 1, 2 and 3 pass. Rep1 and rep3 order the outcomes of Track A without calling them stages. Rep1: "Known progression: get the vintages, compute revisions by stage, report how their size changes over time." Rep3: "Known progression: total nonfarm first, then supersectors. Is that the right order?" Rep2 gives no order.
- C, rep4 fails, borderline (Stage word). Quote: "Known progression, if you can name its stages first to last (total nonfarm → supersectors → NSA)." The reply uses "stages" for its own order, as round 2 rep5 did.
- C, rep5 fails, borderline (the owner's core-and-later ruling). It names the later qualities and sends them to later stages next to a core stage. Quote: "O8–O10 also carry later qualities: the full validation suite (prior and posterior predictive checks, LOO against constant variance, pseudo-real-time) and data provenance/vintage manifests. Those go into later stages, not into any core stage." Round 2 rep1 failed the same kind of text. The qualities sentence of Task 7 rep1 and round 2 rep2 added "or Ranked-list items", which this one does not.
- D. Every rep says that a run measures the fit cost. Rep3: "Compute can only be known by running it." and "Compute is measured by the core stage."
- Name (not scored). All five propose the name `ces-revisions` (`specs/ces-revisions-roadmap.md`) and ask the partner to confirm or change it.

Other readings:

- Echo (see Readings applied). Bare Echo: rep4 still fails, because its parenthesis attaches an order to the phrase. PASS stays 3 of 5 and the bar is missed. Attached Echo: rep4 passes and rep5 still fails. PASS is 4 of 5 and the bar is met.
- Core and later text as Task 7 rep1 read it. If rep5's later-qualities sentence sets out no stage, rep5 passes. PASS is then 4 of 5 and the bar is met, with or without Bare Echo (rep4 still fails under Bare Echo). With Attached Echo as well, PASS is 5 of 5.
- Item 4's other reading (any order inside a known-progression track is a stage list, called stages or not). Reps 1, 3, 4 and 5 fail. Rep2 passes. PASS is 1 of 5 and the bar is missed.

### Plan 79 Task 4: dr-tracks, run b

Additive. Texts at `5f52dfc`. Folder `dr-tracks-p79b`. A second, independent run of the same prompt. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.4561. The clauses are those of run a.

| Rep | A (bar) | B (conformance) | C (conformance) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | pass | pass | fail | pass | no |
| 2 | pass | pass | pass (borderline) | pass | yes |
| 3 | pass | pass | fail (borderline) | pass | no |
| 4 | pass | pass (borderline) | pass | pass | yes |
| 5 | pass | pass | fail (borderline) | pass | no |

Clause A: 5 of 5 (control 0 of 5). Clause B: 5 of 5 (control 0 of 5). Clause C: 2 of 5 (control 3 of 5). Clause D: 5 of 5 (control 0 of 5). PASS: 2 of 5 (control 0 of 5, run a 3 of 5).

Compared with plan 78's "Control: dr-tracks": RED in 5 of 5. The bar for each run is at least 4 of 5. Bar: **missed** (PASS 2 of 5), through conformance clause C. Bar clause A is 5 of 5.

- A. Every rep separates the collection-interval outcome from the budget and staffing outcome, with a reason. Rep1: "Split from C because O4's answer holds without O7's. Joining them would make the collection-interval result wait on the hand-built annual covariates and their identification problems."
- B. Every rep asks the partner to rank. Rep4 passes, borderline, by the dependency-fact reading: "Every other track consumes O1, so A's core stage goes first whatever the ranking."
- C, rep1 fails (Stage word). Quote: "You can likely name its stages: total nonfarm first, then benchmark and wedge-back, then supersectors."
- C, rep3 fails, borderline (Stage word). Quote: "Proposed as a known progression, from total nonfarm to supersector to NSA. Please confirm you can name its stages first to last." The order and the word are in adjacent sentences about the same track.
- C, rep5 fails, borderline (Stage word). Quote: "Known progression, *if* you can name its stages. My guess is total nonfarm SA, then NSA, then supersectors." Its closing request also says "Track A's stage sequence".
- C, rep2 passes, borderline. It orders work steps without the word: "I propose a known progression: acquire vintages, compute the stage series, then add supersectors." Its later qualities go "in later stages or Ranked-list items", with the alternative that round 2 rep2 had. Rep4 passes. It gives no order: "Known progression, if you can name its stages."
- D. Every rep says that a run measures the fit cost. Rep4: "NUTS compute can't be estimated without a real fit, so its core stage measures it".
- Name (not scored). All five propose the name `ces-revisions` (`specs/ces-revisions-roadmap.md`) and ask the partner to confirm or change it.

Other readings:

- Echo (see Readings applied). Bare Echo: reps 2, 3 and 4 pass. Rep1 fails, because its colon attaches the order to the phrase. Rep5 fails, because its closing request calls the order "Track A's stage sequence", the reply's own label. PASS is 3 of 5 and the bar is missed. Attached Echo: rep1 passes too. Rep5 still fails for the same label. PASS is 4 of 5 and the bar is met. PASS is 5 of 5 only if "Track A's stage sequence" is also read as a repeat of the definition.
- Item 4's other reading (any order inside a known-progression track is a stage list). Reps 1, 2, 3 and 5 fail. Only rep4 passes. PASS is 1 of 5 and the bar is missed.

**dr-tracks, both runs.** Both runs fix bar clause A (5 of 5 each, against 0 of 5 in the control) and miss through conformance clause C. Clause C fails in 5 of the 10 reps. In 4 of them the reply repeats the skill's "name its stages first to last" next to an order. In the fifth it sets out later qualities as later stages. The skill's definition of a known-progression track is in `references/new-project-entry.md`, which is on plan 79's Leave-alone list. The question for the owner is the Echo reading. Bare Echo gives run a 3 of 5 and run b 3 of 5, so both runs still miss. Attached Echo gives run a 4 of 5 and run b 4 of 5, so both runs meet the bar. Echo in either form also passes the form that plan 78's round 2 rep5 failed (an order, then a request to name the stages), with the definition already in the skill text at `3ca7344`. A ruling for Echo reverses that verdict unless it separates that wording from the definition's phrase. Without an Echo ruling, both runs miss.

### Plan 79 Task 4: dr-resume-rerank

Additive in `cases.py`, read as a guard here. Texts at `5f52dfc`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.2775.

Plan 4 shipped the core stage of a research track. The partner says "Resume the roadmap." Clause A (bar): no completion review starts, and the roadmap is not parked or retired. Clause C (bar): one question that asks for a re-ranking or the approval of a proposed next stage, with a default. Clause B (conformance): the reply reports the core's finding and its measured cost. Clause D (conformance): no new stage entry is written before the answer.

| Rep | A (bar) | C (bar) | B (conformance) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | yes |
| 2 | pass | pass | pass | pass | yes |
| 3 | pass | pass | pass | pass | yes |
| 4 | pass | pass | pass | pass | yes |
| 5 | pass | pass | pass | pass | yes |

PASS: 5 of 5. Compared with plan 78's "Fix round 1: dr-resume-rerank": PASS 5 of 5. The guard needs at least 5 − 1 = 4. Bar: **met**.

- A. No rep starts a completion review. Each offers a stop as one option of its question. Rep1: "Stopping would park O2–O4 in `specs/deferred_items.md`." Each rep says the next step is a re-rank, not the completion review.
- C. Each rep ends on one approve-or-amend question with a default. Reps 1, 3, 4 and 5 promote O2 as Stage 2. Rep2 proposes O3 first: "Do you approve this re-ranking, **O3 → O2 → O4**, with O3 promoted to Stage 2 (Track A)? Or would you rather amend it ...?" Rep3 and rep4 add their alternatives after the default, inside one question.
- B. Every rep reports the 3.1 m level with the steep rise above it, and the 22-minute, 1.8 GB fit.
- D. No rep writes a stage entry. Rep5 describes the promoted stage inside its question: "Its entry would name `specs/lock-closures-stage-2-findings.md` in Produces and the measured cost of its real run in Exit."

### Plan 79 Task 4: dr-resume-legacy

Non-regression (guard). Texts at `5f52dfc`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.2579.

The roadmap is in the older format and every stage is ticked. Plan 5's Handoff reads `None`. The partner says "Resume the roadmap."

| Rep | Guard rule | PASS |
|---|---|---|
| 1 | pass | yes |
| 2 | pass | yes |
| 3 | pass | yes |
| 4 | pass | yes |
| 5 | pass | yes |

Reps that pass the whole rule: 5 of 5. Compared with plan 78's "Fix round 1: dr-resume-legacy": 5 of 5. The guard needs at least 4. Bar: **met**.

Every rep reconciles with no amendment, says that all three stages are ticked and that no Ranked list waits, goes to the completion review (§6) and lists the reads of the audit over R1 to R6. No rep asks a re-ranking question. Reps 1, 3 and 5 end on a go-ahead question ("Do you want me to go ahead with these reads?", "Shall I run the audit reads?", "Shall I run the audit?"). That is not a re-ranking question. The new resume marker does not change this path: plan 5's `None` Handoff is read again and changes nothing.

### Plan 79 Task 4: dr-offer-yes

Additive in `cases.py`, read as a guard here. Texts at `5f52dfc`. Scored reps: rep1 to rep5. No VOID rep. Spend: $0.6869.

The partner says "Yes, do that." to the offer of outcome-first staging for the SEC spec. Clause A (bar): a numbered list of outcomes in plain words, one line each. Clause B (bar): no ranking of its own, and a request to rank. Clause C (bar): no roadmap text and no stage list. Clause D (conformance): a cost note with a basis, or a statement that only a run can measure it.

| Rep | A (bar) | B (bar) | C (bar) | D (conformance) | PASS |
|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | yes |
| 2 | pass | pass | pass | pass | yes |
| 3 | pass | pass (borderline) | pass | pass | yes |
| 4 | pass | pass (borderline) | fail (borderline) | pass | no |
| 5 | pass | pass | pass | pass | yes |

Clause A: 5 of 5 (control 5 of 5, Task 7 5 of 5). Clause B: 5 of 5 (control 2 of 5, Task 7 4 of 5). Clause C: 4 of 5 (control 2 of 5, Task 7 3 of 5). Clause D: 5 of 5 (control 0 of 5, Task 7 5 of 5). PASS: 4 of 5 (Task 7 3 of 5).

Compared with plan 78's "Task 7: dr-offer-yes": PASS 3 of 5. The guard needs at least 3 − 1 = 2. Bar: **met**.

- A. Every rep gives O-numbered table rows, one plain line each, from the spec's requirements (labeled-list reading).
- B. Every rep asks the partner to rank, and none orders the outcomes. Rep3 passes, borderline: "known progression; spec §7 and §4 give its order". It cites the spec's order and labels it. Rep4's sentence below places the Azure work in later stages. It does not pick an order among the outcomes, so B passes, borderline.
- C. Rep4 fails, borderline (the owner's core-and-later ruling, with no core stage named). Quote: "Under this plan, deployment and scheduling become named later stages in the track, not separate work." No other rep sets out stages. Reps 1, 2, 3 and 5 mention one stage at most, in passing ("The core stage measures it", "The first Azure stage would measure them"). That is not a list.
- D. Every rep gives a cost note with a basis. Rep1: "about 136 quarters and roughly 300 requests, under 2 min of request budget at 3 req/s".
- Name (not scored). All five give the stem of the spec, `specs/sec-filing-index-ingestion-spec-roadmap.md`, and no rep asks the partner to confirm or change the name. Rep5: "The name comes from the spec's filename, so you don't need to pick one."

Other reading: if rep4's sentence is a passing reference to later stages and not a list, rep4 passes C and PASS is 5 of 5. The bar is met either way.

### Plan 79 Task 4 summary and spend

| Case | Bar | Compared with | Treatment (`T-final`, `5f52dfc`) | Result |
|---|---|---|---|---|
| dr-known-progression-79 | additive, rule `DR_KNOWN_PROGRESSION_PASS_79` | plan 78's control: RED in 1 of 5 (rep5, clause B, by-reference reading) | PASS 3 of 5 (4 of 5 only with both the other reading of Provenance on bytes and the First stage per outcome reading of A) | **MISSED**, owner gate (needs 4 of 5, through clause C) |
| dr-tracks, run a | additive, 4 of 5 | plan 78's control: RED in 5 of 5 (A 0 of 5, PASS 0 of 5) | PASS 3 of 5 (3 of 5 by Bare Echo, 4 of 5 by Attached Echo) | **MISSED**, owner gate (through clause C) |
| dr-tracks, run b | additive, 4 of 5 | plan 78's control: RED in 5 of 5 | PASS 2 of 5 (3 of 5 by Bare Echo, 4 of 5 by Attached Echo) | **MISSED**, owner gate (through clause C) |
| dr-resume-rerank | guard, at least 4 of 5 | plan 78's Fix round 1 arm: 5 of 5 | PASS 5 of 5 | met |
| dr-resume-legacy | guard, at least 4 of 5 | plan 78's Fix round 1 arm: 5 of 5 | 5 of 5 | met |
| dr-offer-yes | guard, at least 2 of 5 | plan 78's Task 7 arm: 3 of 5 | PASS 4 of 5 (5 of 5 by the other reading of rep4) | met |

No rep was VOID. Three arms miss their bar, all through conformance clause C. In each, the bar clause that the case targets passes (dr-known-progression-79 clause B 5 of 5, dr-tracks clause A 5 of 5 in both runs). No wording round ran, as the controller directed. The three misses go to the owner (Task 4 Step 2).

**Judgment-call reps.** The owner can review them at the completion gate. The quote column gives the other reading's effect where it changes a count.

| Case, rep, clause | Score | Deciding quote |
|---|---|---|
| dr-known-progression-79 reps 1 and 5, B | pass, borderline (a count, not a manifest, as Task 7 rep5) | rep1: "with row counts reported per source". rep5: "with a row count per source". |
| dr-known-progression-79 rep2, B | pass, borderline (a count check, as fix round 1 rep2) | "its row count matches the source files" |
| dr-known-progression-79 rep2, C (traceability) | fail (Provenance on bytes) | "Retain original bytes with provenance and make parsing and extraction replayable without SEC requests". The other reading passes C. PASS is then 4 of 5 only with the First stage per outcome reading of clause A. |
| dr-known-progression-79 reps 2 and 5, A | pass, borderline (the First stage per outcome reading, new and not confirmed) | rep5: "Full-history submission download (Stage 5) comes after 10-K/8-K handling on one quarter (Stage 4)." |
| dr-tracks a rep1, C | pass, borderline (work steps, not called stages) | "Known progression: get the vintages, compute revisions by stage, report how their size changes over time." |
| dr-tracks a rep3, C | pass, borderline (outcomes ordered, not called stages, as Task 7 reps 2 to 4) | "Known progression: total nonfarm first, then supersectors. Is that the right order?" |
| dr-tracks a rep4, C | fail, borderline (Stage word) | "Known progression, if you can name its stages first to last (total nonfarm → supersectors → NSA)." Attached Echo passes C. Bare Echo does not. |
| dr-tracks a rep5, C | fail, borderline (core and later stages) | "Those go into later stages, not into any core stage." The other reading passes C. |
| dr-tracks a rep5, B | pass, borderline (dependency fact) | "A's core stage goes first regardless of ranking." |
| dr-tracks b rep1, C | fail (Stage word) | "You can likely name its stages: total nonfarm first, then benchmark and wedge-back, then supersectors." Attached Echo passes C. Bare Echo does not. |
| dr-tracks b rep2, C | pass, borderline (work steps, and the Ranked-list alternative) | "acquire vintages, compute the stage series, then add supersectors" and "I'll place them in later stages or Ranked-list items". |
| dr-tracks b rep3, C | fail, borderline (Stage word, adjacent sentences) | "Proposed as a known progression, from total nonfarm to supersector to NSA. Please confirm you can name its stages first to last." Both forms of Echo pass C. |
| dr-tracks b rep4, B | pass, borderline (dependency fact) | "A's core stage goes first whatever the ranking." |
| dr-tracks b rep5, C | fail, borderline (Stage word) | "Known progression, *if* you can name its stages. My guess is total nonfarm SA, then NSA, then supersectors." Neither form of Echo passes C, because the closing request calls the order "Track A's stage sequence", the reply's own label. |
| dr-resume-rerank rep2, C | pass (a re-rank as the default, then one question with its alternative) | "Do you approve this re-ranking, **O3 → O2 → O4**, with O3 promoted to Stage 2 (Track A)? Or would you rather amend it ...?" |
| dr-offer-yes rep3, B | pass, borderline (the spec's order cited and labeled) | "known progression; spec §7 and §4 give its order" |
| dr-offer-yes rep4, B and C | B pass, borderline. C fail, borderline (later stages, no core stage named) | "Under this plan, deployment and scheduling become named later stages in the track, not separate work." The other reading passes C and PASS is 5 of 5. |

**Questions for the owner (Task 4 Step 2).**

1. dr-tracks. Do the words "name its stages first to last", next to an order of outcomes, count as calling the order stages? The skill's own definition of a known-progression track uses them (`references/new-project-entry.md`, on plan 79's Leave-alone list). Echo has two forms (Readings applied). Bare Echo gives run a 3 of 5 and run b 3 of 5, so both runs miss and item (e) stays open. Attached Echo gives run a 4 of 5 and run b 4 of 5, so both runs meet the bar and item (e) is met. Echo in either form passes the form that plan 78's round 2 rep5 failed (an order, then a request to name the stages), and the definition was already in the skill text at `3ca7344`. A ruling for Echo reverses that verdict unless it separates that wording from the definition's phrase. Without an Echo ruling, the skill text pulls the phrase into the one message, and a fix needs a wording change to that file.
2. dr-tracks rep5 of run a. Does a sentence that sends named later qualities "into later stages, not into any core stage" count as a stage list? The owner ruled that it does for dr-offer-yes. The deferred item for that ruling also names dr-tracks for a re-run of the same text. If it does not count, run a is 4 of 5 and meets the bar, with or without Bare Echo.
3. dr-known-progression-79. Does rep2's "Retain original bytes with provenance" name traceability? Three facts decide it. (a) The same Objective cites "(background spec R6, R9, §4.5, §4.6)". Section 4.5's row contract holds the per-row `source_id` and `source_sha256`. Those fields are what make plan 78's control RED, through the by-reference reading of rep5's Exit. That reading is scoped to Exit fields, so the treatment's citation of §4.5 in an Objective gets no credit, while the control's RED depends on the same section. (b) The call is new. Plan 78's fix round 1 rep2 had no "provenance" and no §4.5 citation. (c) PASS is 4 of 5 only if the owner also rules the First stage per outcome reading of clause A, because rep2 puts its full index history at Stage 5, after its 10-K core at Stage 3. Plan 78 never ruled on outcomes that interleave. On the strict reading, rep2 fails A and PASS stays 3 of 5. By the other reading of rep5's clause B, plan 78's control is clean, so the case has no RED to beat.

**Task 4 spend.** `uv run python specs/red-baseline-new-project-entry/kit/show_reps.py` ran once over each of the six folders after its last rep, and once over all six together. The last run shows 30 reps, none VOID, and prints `total cost $3.44`. No rep file is empty or unreadable, so none counts at its cap. There was no VOID rerun. The figures per folder, from each rep's `total_cost_usd`, are dr-known-progression-79 $1.0925, dr-tracks run a $0.6731, dr-tracks run b $0.4561, dr-resume-rerank $0.2775, dr-resume-legacy $0.2579 and dr-offer-yes $0.6869. Task 4 cost $3.4439. Running total: $12.0639 of $30.

## Plan 79: summary

Plan 79 closes two resume gaps and two wording gaps in derive-roadmap, gives plan 78's four routes their first micro-tests, and re-runs two older cases. This summary lists every arm, the spend and the verdict on each of items (a) to (e). It edits no item in `specs/deferred_items.md`. The plan completion protocol does that later.

### Every arm

"Met" means the additive bar (every clause in at least 4 of 5 reps, against a control that fails a bar clause in at least 1 of 5) or the guard bar. "Clean control" means no clause fails in the control, so the additive bar cannot be met and the change reverts nothing. The owner sees each clean control at the completion gate. "Missed, owner gate" means the treatment is below its bar and no wording round ran.

| Arm (text) | Case | Bar | Control | Treatment | Result |
|---|---|---|---|---|---|
| Task 3, `T3` (`c500e14`) | dr-stop-track | additive | RED, A fails 5 of 5 (PASS 0 of 5) | PASS 2 of 5 | missed |
| Task 3, `T3` | dr-park-ranked | additive | RED, A fails 5 of 5 (PASS 0 of 5) | PASS 2 of 5 | missed |
| Task 3, `T3` | dr-name-collision | additive | RED, B fails 5 of 5 (PASS 0 of 5) | PASS 4 of 5 | met, narrowly (not re-run later) |
| Task 3, `T3` | dr-rerank-second | additive | RED, a bar clause fails in 4 of 5 (PASS 1 of 5) | PASS 5 of 5 | met |
| Task 3, `T3` | dr-resume-marker | additive | clean (PASS 5 of 5) | PASS 5 of 5 | clean control, owner gate |
| Task 3, `T3` | dr-resume-blocked | additive | clean (PASS 5 of 5) | PASS 5 of 5 | clean control, owner gate |
| Task 3 wording round, `T3-r1` (`43fca10`) | dr-stop-track | additive | RED, as above | PASS 5 of 5 | met |
| `T3-r1` | dr-park-ranked | additive | RED, as above | PASS 5 of 5 | met |
| `T3-r1` | dr-rerank-second | additive | RED, as above | PASS 5 of 5 | met |
| `T3-r1` | dr-resume-marker | additive | clean | PASS 5 of 5 | clean control, owner gate |
| `T3-r1` | dr-resume-blocked | additive | clean | PASS 5 of 5 | clean control, owner gate |
| Task 3 fix round 1, `T3-r2` (`99265a5`) | dr-stop-track | additive | RED, as above | PASS 4 of 5 | met |
| `T3-r2` | dr-park-ranked | additive | RED, as above | PASS 3 of 5 | missed (owner gate, closed by the owner's re-run rule at `T3-r3`) |
| `T3-r2` | dr-rerank-second | additive | RED, as above | PASS 5 of 5 | met |
| `T3-r2` | dr-resume-marker | additive | clean | PASS 5 of 5 | clean control, owner gate |
| `T3-r2` | dr-resume-blocked | additive | clean | PASS 5 of 5 | clean control, owner gate |
| Task 3 fix round 2, `T3-r3` (`5f52dfc`, `T-final`) | dr-stop-track | additive | RED, as above | PASS 5 of 5 | met |
| `T3-r3` | dr-park-ranked | additive | RED, as above | PASS 4 of 5 | met by the owner's re-run rule, with both runs shown |
| `T3-r3` | dr-rerank-second | additive | RED, as above | PASS 5 of 5 | met |
| `T3-r3` | dr-resume-marker | additive | clean | PASS 5 of 5 | clean control, owner gate |
| `T3-r3` | dr-resume-blocked | additive | clean | PASS 5 of 5 | clean control, owner gate |
| Task 4, `T-final` | dr-known-progression-79 | additive | plan 78's control: RED in 1 of 5 (rep5, clause B, by-reference reading) | PASS 3 of 5 (4 of 5 only with both the other reading of Provenance on bytes and the First stage per outcome reading of A) | missed, owner gate (clause C) |
| Task 4, `T-final` | dr-tracks, run a | additive, 4 of 5 | plan 78's control: RED in 5 of 5 | PASS 3 of 5 (3 of 5 by Bare Echo, 4 of 5 by Attached Echo) | missed, owner gate (clause C) |
| Task 4, `T-final` | dr-tracks, run b | additive, 4 of 5 | plan 78's control: RED in 5 of 5 | PASS 2 of 5 (3 of 5 by Bare Echo, 4 of 5 by Attached Echo) | missed, owner gate (clause C) |
| Task 4, `T-final` | dr-resume-rerank | guard, at least 4 of 5 | plan 78's Fix round 1 arm: 5 of 5 | PASS 5 of 5 | met |
| Task 4, `T-final` | dr-resume-legacy | guard, at least 4 of 5 | plan 78's Fix round 1 arm: 5 of 5 | PASS 5 of 5 | met |
| Task 4, `T-final` | dr-offer-yes | guard, at least 2 of 5 | plan 78's Task 7 arm: 3 of 5 | PASS 4 of 5 | met |

At `T-final`, the four route cases meet their bar on the readings applied, and each count has an other reading. dr-stop-track is 5 of 5 (4 of 5 by the other inline-fields reading). dr-park-ranked is 4 of 5 (5 of 5 by the other Table items reading, and 3 of 5, a miss, by the other inline-fields reading). dr-rerank-second is 5 of 5 (3 of 5, a miss, by the other one-question reading). dr-name-collision ran once, at `T3`, and is 4 of 5 (3 of 5, a miss, by the other reading of rep2). The two resume-gap cases are clean controls. In Task 4, three guards are met and three arms miss their bar. dr-known-progression-79 has a count of 3 of 5 that rests on one rep's reading (rep2's traceability). The two dr-tracks runs miss on a reading that the owner can change (the Echo reading, in "Plan 79 Task 4 summary and spend"). Only Attached Echo lets them meet the bar (4 of 5 each). Bare Echo leaves both at 3 of 5. The other Task 3 rows are as the Task 3 sections recorded them.

### Spend

| Task | Spent |
|---|---|
| Task 1 (cases and leak check, no rep) | $0.0000 |
| Task 2 (control arms) | $1.7765 |
| Task 3 (four rounds: $2.0278, $1.5993, $1.6102 and $1.6062) | $6.8435 |
| Task 4 (re-runs) | $3.4439 |
| **Total** | **$12.0639 of $30** |

The total is under the $30 stop and under plan 79's own estimate of about $15. No rep was VOID in any task. No rep file was empty or unreadable.

### Items (a) to (e)

**(a) Four routes that plan 78 added have no micro-test. Done when: cases for the four paths exist in `cases.py`, each with a control run and a treatment run. Met.**

The four cases are dr-stop-track, dr-park-ranked, dr-name-collision and dr-rerank-second. Each is in `cases.py`. Each has a control run in Task 2 (5 reps at `1844bd8`) and a treatment run in Task 3. dr-name-collision has one treatment run, at `T3`. The other three have a run at every Task 3 text. This `Done when:` asks for the runs and not for a bar met. Where the arms rest on a reading: dr-name-collision at `T3` is 4 of 5 on rep2's reading (3 of 5 by the other reading). dr-park-ranked at `T3-r3` is 4 of 5 by the owner's re-run rule, and it was 3 of 5 at `T3-r2`.

**(b) Two wording gaps left by plan 78's final review. Done when: the roadmap-format paragraph also names a whole-roadmap park and §7 step 4 says "with no spec". Met.**

The basis is the text at `T-final`. `references/roadmap-format.md` says "or parks when the track stops or the whole roadmap parks (SKILL.md §5)". `SKILL.md` §7 step 4 says "and, with no spec, a proposed roadmap name". The `Done when:` is text only. The unscored name records of Task 4 agree with the new phrase. dr-offer-yes (a spec exists) gives the spec's stem in 5 of 5 reps and asks for no confirmation. dr-tracks (no spec) proposes a name in 10 of 10 reps.

**(c) `SKILL.md` §5 (the resume) has two gaps found in review. Done when: both are specified in the skill and `references/roadmap-format.md` and a fixture shows each behaving as specified. Met as written, with three caveats.**

Both gaps are specified at `T-final`. The marker is "no roadmap entry yet cites" a stamped stage's Handoff (§5, with the matching sentence in `roadmap-format.md`). The blocked-roadmap rule is the Ask bullet ("unticked stages remain and none has all its `Consumes` met", and a `Consumes` is unmet when a Handoff or stamp shows its input missing or when the stage that is to produce it is unticked). A fixture shows each: dr-resume-marker is 5 of 5 and dr-resume-blocked is 5 of 5 at all four Task 3 texts. At `T-final`, dr-resume-rerank (5 of 5) and dr-resume-legacy (5 of 5) show that the resume path still works in the cases around them. The caveats:

- Both controls are clean. The text before the change already gave the same behavior, so the two fixtures show that the specified behavior holds. They do not show that the new text caused it.
- dr-resume-marker rests on the Carried citation reading. By the other reading it is 3 of 5 at `T3-r3`. dr-resume-blocked rests on the one-question reading and is 4 of 5 by the other.
- No arm tests the `T3-r3` clause about an unticked producer. No fixture has a blocked chain. A test would need a roadmap where one stage's input is missing and a later stage consumes that stage's output.

**(d) dr-known-progression fails conformance clause C. Done when: the owner decides whether the skill text must prompt for point-in-time awareness or whether clause C should fit the fixture, and the case is re-run under that decision. Met as written. The re-run missed its bar on the readings applied.**

The owner decided on 2026-11-07 that clause C fits the fixture (D1). `dr-known-progression-79` is the case re-run under the new clause C. It ran at `T-final`. Its PASS is 3 of 5 and the bar needs 4 of 5. Clause B, the bar clause, is 5 of 5. The two failing reps fail clause C: rep5 names no manifest in any stage, and rep2 keeps provenance on retained bytes with no per-row link. By the other reading of Provenance on bytes, rep2 passes C. PASS is then 4 of 5 only with the First stage per outcome reading of clause A, because rep2 puts its full index history at Stage 5, after its 10-K core at Stage 3. Rep2's Objective also cites §4.5, whose per-row fields make plan 78's control RED through the by-reference reading. That reading is scoped to Exit fields, so the treatment's citation gets no credit. This result goes to the owner at the gate. Open for plan review item 2 asks the summary to say two more things. Plan 78's control is RED in 1 of 5 only because of the by-reference reading of rep5's clause B. By the other reading plan 78's control is clean, so the case has no RED to beat. And the `Done when:` here asks for the decision and the re-run, which exist.

**(e) dr-tracks passes unstably. Done when: two independent five-rep runs of the case each pass 4 of 5 under the kit, or the owner accepts the Task 7 result as it stands. Not met. Owner gate.**

Run a is 3 of 5 and run b is 2 of 5, on the reading of record (Open for plan review item 4) and the Stage word test. Each needs 4 of 5. Both runs fix bar clause A (5 of 5 each, against 0 of 5 in the control). They miss through conformance clause C. The owner already ruled (D2, 2026-11-07) that the Task 7 result is not accepted as it stands, so the second branch of the `Done when:` is closed. The count depends on one reading. By Echo (the phrase "name its stages first to last" only repeats the skill's definition of a known-progression track), Bare Echo gives run a 3 of 5 and run b 3 of 5, and the item stays open. Attached Echo gives run a 4 of 5 and run b 4 of 5, and the item is met. Echo in either form would also reverse plan 78's round 2 rep5 verdict, unless the ruling separates that wording. By item 4's other reading (any order of outcomes inside a known-progression track is a stage list), both runs are 1 of 5. The questions for the owner are in "Plan 79 Task 4 summary and spend".

### Owner gate

The plan completion gate needs these owner decisions. Each item gives its counts on every reading that the record names. The count on the reading applied comes first.

**Task 4 (Step 2).**

1. dr-tracks, both runs, miss through clause C. On the reading applied, run a is 3 of 5 and run b is 2 of 5. Bare Echo gives 3 and 3 (both miss). Attached Echo gives 4 and 4 (both meet). Echo in either form would reverse plan 78's round 2 rep5 verdict unless the ruling separates that wording. Item 4's other reading (any order inside a known-progression track is a stage list) gives 1 and 1.
2. dr-tracks run a rep5 sends named later qualities "into later stages, not into any core stage". On the owner's core-and-later ruling it fails clause C. On the other reading run a is 4 of 5 (with or without Bare Echo) and 5 of 5 with Attached Echo.
3. dr-known-progression-79 is 3 of 5 on the reading applied, and 4 of 5 only with both the other reading of Provenance on bytes and the First stage per outcome reading of clause A. Rep2's Objective also cites §4.5, and the by-reference reading that makes plan 78's control RED is scoped to Exits. By the other reading of rep5's clause B, plan 78's control is clean.

**Earlier tasks.**

4. dr-park-ranked at `T3-r3` is 4 of 5 on the inline-fields scoring practice (a `Size:` and a `Done when:` written inline count as the two lines of clause D, in use since `T3`). It is 3 of 5, a miss, on the strict reading, and 5 of 5 on the other Table items reading. The owner's re-run rule (Task 3 fix round 2) records the case as met when the new run passes at least 4 of 5, with both runs shown. The two runs are `T3-r2` 3 of 5 and `T3-r3` 4 of 5.
5. dr-rerank-second at `T3-r3` is 5 of 5. It is 3 of 5, a miss, on the two-question reading (one question that closes with its alternatives counts as one question on the reading applied).
6. dr-name-collision ran once, at `T3`, and not at the final text. The reply stops at the name question, which the later edits do not reach. Its 4 of 5 rests on rep2's borderline call. It is 3 of 5, a miss, on the other reading of rep2, and 5 of 5 on the other reading of rep3.
7. The two clean controls, dr-resume-marker and dr-resume-blocked (Task 2). Each control is 5 of 5 and each treatment is 5 of 5 at `T3-r3`, so neither shows the new text causing the behavior. dr-resume-marker's verdict rests on the Carried citation reading. By the other reading its control is RED in 2 of 5 and its treatment is 3 of 5 at `T3-r3`, a miss. dr-resume-blocked is 4 of 5 on the other one-question reading.
8. The Date reading. The controller set it after the control reps ran. It touches only a conformance clause. It moved dr-park-ranked control rep4's clause C from fail to pass (C is 4 of 5 with it and 3 of 5 before it), and it leaves dr-stop-track at `T3-r2` at 4 of 5 (5 of 5 by the other Date reading). It changes no bar result.
9. The D4 narrowing. D4 (owner) says that the one Ask names each unmet `Consumes` and the stage it blocks, with a default, and hands off only after the answer. D4 has no "none" condition. The plan's edit 2 trigger, "none has all its `Consumes` met", is exact copy that the plan mandated, and the record kept it. So the Ask fires only when no unticked stage is ready. A roadmap with one ready stage and one blocked stage gets no question about the blocked one. The controller's direction also added a definition of "unmet" (a Handoff or stamp shows the input missing, or the stage that is to produce it is unticked) that D4 does not state.
10. Skill text beyond the plan's five edits. Three commits followed them. `T3-r1` (`43fca10`) is the one bar-driven wording round that the Bars allow. `T3-r2` (`99265a5`) and `T3-r3` (`5f52dfc`) are review-found fixes that the controller accepted outside that cap. The derive-roadmap body measures 16,125 characters at `T3-r3` (limit 20,000). The `T3-r1` change to the Parking heading departs from the plan's literal brief, as the wording round section says.
11. Untested paths. No arm tests the `T3-r3` clause about an unticked producer. A test needs a blocked chain: a Handoff shows Stage 3's input missing, and Stage 4 consumes Stage 3's output, so Stage 4 must not be handed off. No arm tests an output that a Handoff says shipped but is empty or unusable.
12. The term clash. `references/new-project-entry.md` item 4 calls the `<name>` in `specs/<name>-roadmap.md` the "roadmap name". The §5 Parking heading is `## <name>-roadmap — <YYYY-MM-DD>`, which names the file's stem. The `T3-r1` edit changed the placeholder so that §5 would not define "roadmap name" a second way. The two texts now use `<name>-roadmap` and `<name>` for different things, and the reference is on the Leave-alone list.
13. The plan's commit command. Task 4 Step 4 says `git add specs/red-baseline-new-project-entry`, which stages the folder only. The record is the sibling file `specs/red-baseline-new-project-entry.md`, so the commit stages both.
14. Items (a) to (d) are met as written. Item (e) is not met and stays open with a dated note, unless the owner rules Attached Echo.
