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
