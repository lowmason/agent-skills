# Statement-readings probe Implementation Plan

**Status: COMPLETE (2026-11-09)** — executed via executing-plans; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Measure, before any skill text changes, how often statement-level readings at plan review catch harder plants than plan 81's (a wrong value that the plan argues for, and a spec sentence with two readings), against a fresh Self-Review, and how many false alarms and unclear cases they raise on an unchanged plan.

**Architecture:** A kit in `specs/red-baseline-statement-readings/kit/`, copied from plan 81's, builds six plan copies from plans 53, 55 and 66, and numbers each copy's spec sentence by sentence. Three copies carry plan 81's plants plus one defense sentence each, two carry one spec sentence edited to allow two readings, and one is plan 55 unchanged. Isolated `claude -p` and `codex exec` runs produce the readers' statements (numbered spec only), a planner stand-in's statements (plan and numbered spec) and a control Self-Review (whole copy). A comparison script and an `opus` adjudicator turn each run into cases for three arms: both readers, Claude alone and Codex alone. A scorer counts catches, false alarms, unclear cases, owner load and stand-in fidelity. The results go to `specs/red-baseline-statement-readings.md` for the owner's review (D8).

**Tech Stack:** Python 3.13 stdlib scripts run with `uv run python`, bash, `claude -p` (one Claude Code binary, pinned in Task 4; the PATH `claude` was 2.1.316 at planning), `codex exec` (codex-cli 0.163.0 at planning), git.

**Spec:** `specs/completed/statement-level-readings.md` (APPROVED 2026-11-09; owner decisions D9–D13, with D3, D7 and D8 carried from `specs/spec-derived-acceptance-tests.md`). This plan implements its Verification, "Probe first", only. A build plan comes only after the owner reviews this plan's results (D8).

## Labels used in this plan

- **D3, D7 and D8** are the old spec's decisions that the spec carries: the `opus` adjudicator that quotes the deciding text or rules `unclear` (D3), the cheaper Codex model first (D7), and the probe as its own plan before any build plan (D8). **D9–D13** are the spec's own owner decisions. Owner decisions at this plan's review take D14 onward, so every id stays unique.
- **DF-ARMS** and **DF-AMEND** are the two defaults that the handoff brief flagged. **PD1–PD13** are this plan's own defaults ("planner defaults"). They are not plan 81's DF1–DF11 or its handoff's DF-A. All are under "Defaults (approved, D14)".
- **`RS/`** is `specs/red-baseline-statement-readings/`. **`RB/`** is plan 81's folder, `specs/red-baseline-acceptance-tests/`. **The record** is plan 81's results file, `specs/red-baseline-acceptance-tests.md`. **The results file** is this plan's, `specs/red-baseline-statement-readings.md`.
- A **copy** is a spec-and-plan pair with one plant or none. A **spec id** names one distinct spec text: `p53`, `p66`, `p55`, `p66-today` or `p55-exit`. The **planted sentence** is the spec sentence that a copy's plant or edit is about.
- A **statement** is one run's list of slot entries (spec Design 3). The **stand-in** is the `claude -p` call that plays the planner (spec Verification 4).
- An **arm** of the step is `pair` (both readers), `claude` (Claude alone) or `codex` (Codex alone). The **control** is plan 81's fresh-session Self-Review.
- A **rep** is one repetition. Rep *k* of an arm pairs the *k*-th scored rep of each reader with the *k*-th scored rep of the stand-in.
- **Rules 1–9** are the comparison rules of spec Design 6. A **case** is a sentence that rule 2, 3 or 4 sends to the adjudicator.

## Global Constraints

- **Probe only (D8).** "The probe runs as its own plan, before any build plan and before any skill text changes" (spec Verification, "Probe first"). This plan changes no file under `skills/`, `agents/`, `commands/`, `hooks/`, `rules/` or `runtimes/`, and it writes no build plan.
- **One execution at a time.** No execution of this plan starts while another plan executes in this repository (plan 73's owner ruling D10, `specs/plans/completed/73-reviewer-and-planning-contract.md:59`). Plan 82 (`claude/laughing-einstein-c40dda`) is live at planning. Before Task 1, confirm with the owner that no plan execution is running.
- **Leave alone** (spec Constraints): plan 81's record, kit, copies and runs (`RB/`), and the old spec's finding 21 parts. Also plan 82, the finding 21 build plan, and both watch items in `specs/deferred_items.md`, § 81-spec-derived-acceptance-tests. This plan names the item that fires (next line) and edits neither.
- **The watch item that fires** (spec Constraints, "Watch items"): "`measure.py score` does not VOID a Codex reader rep whose log shows tool activity" (`specs/deferred_items.md:6103`). This kit's scorer is built from a copy of plan 81's `measure.py`, so it runs the residual check inside its VOID check (Task 4). Plan 81's kit stays unchanged.
- **Where the arms run (DF-ARMS).** Every run executes on the owner's Mac, where the `codex` CLI is logged in. Codex is not installed in cloud sessions. Every `claude -p` call uses the one binary that Task 4 pins.
- **The reference for the bare plants** (spec Verification 6, Constraints): plan 81's control results, 15 of 15. This plan uses no result of plan 81's treatment arms.
- **Codex data** (spec Constraints, carried): "A Codex run sends the numbered spec, and every file that it reads, to OpenAI." `CLAUDE.md:54` approves Codex reviews only. So each session that runs Codex asks the owner once, before its first Codex run, with the question in Task 4 Step 8. Without a yes, no Codex reader runs: the `pair` and `codex` arms read "not run", and the results file says why.
- **Codex model** (D7, spec Constraints): every Codex call names `-m` and pins the effort at `ultra`, as plan 81's did. `gpt-6-sol` runs first, and `gpt-6.1-sol` only when PD9 triggers. Each run's model and effort come from its log header. Codex runs directly from `run_codex.sh`, not through `claude -p`, so `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS` is not needed.
- **Isolation** (spec Constraints). Every `claude -p` call runs as plan 81's did: from a fresh empty folder under `/tmp`, outside every repository, with `--tools ""`, `--strict-mcp-config`, `--setting-sources ""`, `--no-session-persistence`, `--output-format json` and `--max-budget-usd`, and with `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`. It runs under `env -i` with only `HOME`, `USER`, `LOGNAME`, `PATH`, `SHELL`, `TMPDIR` and `LANG` set. Codex runs use plan 81's Task 4 flags in `run_codex.sh` (record, Appendix A), under the same `env -i`. Their run folder is empty, and the prompt, numbered spec included, comes on stdin.
- **What each role sees** (spec Design 5 and 7, Verification 4–6, D10):
  - A reader: the slot rules and one numbered spec. Nothing from any plan: no plan path, plan line, defense sentence or planted token that the spec lacks.
  - The stand-in: its copy's plan, with line numbers, and the copy's numbered spec. It is told that it wrote the plan.
  - The adjudicator: the numbered spec and, for each case, the entries of the arm's own readers. Never the copy, the stand-in's statement or a plan path.
  - The control: plan 81's control prompt, with writing-plans' `SKILL.md` at one sha for all control reps, the copy's spec and the whole copy.
- **Models.** `opus` for the Claude reader, the stand-in, the adjudicator and the control (spec Design 9 and Verification 5). Every `claude -p` call names `--model`.
- **Runs** (spec Verification 3–6): 5 scored reps of each reader on each of the five spec ids, of the stand-in on each of the six copies, of the control on each of the five planted copies, and of the adjudicator on each arm and copy. A VOID rep (PD6) reruns and never counts as a miss.
- **The bars** (spec Verification 9, quoted): "The step catches each new plant in at least 4 of 5 runs, and the control catches it in at most 2 of 5." "On the clean copy, the step raises at most one false alarm and at most one unclear case per plan. Each bar uses the mean over the 5 runs." "The second reader stays only if the pair beats Claude alone on catches or on false alarms." The owner reviews the results and decides whether anyone writes a build plan (D8). This plan reports. It decides nothing.
- **Cost** (PD7): each `claude -p` call caps at `--max-budget-usd 4.00`. Task 4's pilot projects Task 5's cost. Above $150, stop and ask the owner.
- **Provenance** (spec Provenance): the kit adapts plan 81's kit, this repository's own work. Knight and Leveson (1986) is cited for an idea only. No text or fixture comes from `prime-radiant-inc/superpowers-evals`. The copies are this repository's own files.
- **Commit gate.** Before each commit, `bash build/run_commit_lints.sh` prints `commit lints passed`. Commit messages follow Conventional Commits, use plain technical English and end with the attribution trailer that the executing session is given.
- **Public repository.** The kit, the runs and the results file hold no private detail.
- **Shell.** The Bash tool runs zsh: quote any `===` in an echo. Scratch files go under `/tmp/plan83-work/`.
- **Completion** (spec, "Closing the backlog and the drift spec"). Completion has two branches, by the owner's decision at Task 6's gate. With a build plan to come, the spec does not retire, even though no other live plan names it then. With no build plan, completion closes finding 24's line (Task 6 Step 5) and retires the spec.

## Review Focus

1. A plant or a two-reading edit on a sentence that the copy's own amendment task changes. Rule 9 then skips it, so no arm can catch it. Pinned by `make_copies.py selftest` against the PD3 answer keys (Task 2 Step 1).
2. A reply cut off at the output limit. A statement that ends without `</statement>` must be VOID and rerun, never scored with its later entries treated as absent. Pinned by `compare.py selftest` and `measure.py selftest` (Task 3 Step 1, Task 4 Step 1).
3. A reader or adjudicator prompt that holds plan text: a copy path, a defense sentence, a planted token that the spec lacks, a stand-in entry, or, in a one-reader arm, the other reader's entry (spec anti-goals 1 and 2). Pinned by `build_prompts.py selftest` (Task 4 Step 5).
4. A Codex reader rep that shows tool activity in its log, or that ran on another model. It must be VOID and never paired (the watch item). Pinned by `measure.py selftest` (Task 4 Step 1).
5. An entry dropped by the quote check on a planted sentence (PD5). The scorer must name the drop as the reason for that rep's miss, never record a silent miss. Pinned by `measure.py selftest` (Task 4 Step 1).

## Decisions

- **D14** (owner, plan review, 2026-11-09): approved the plan as written ("Approve as written"). It keeps both two-reading plants, `p55-exit` included, and the defaults DF-ARMS, DF-AMEND and PD1–PD13. Applied in: Defaults (approved, D14).
- **D15** (owner, before Task 1, 2026-11-09): execute inline (executing-plans) on Opus ("Inline on Opus (Recommended)"). Before the question, the owner confirmed that no other plan execution runs: "Plan 82 is not executing." Applied in: the execution session.
- **D16** (owner, before Task 1, 2026-11-09): "Approve Codex runs", the answer to Task 4 Step 8's question. The session asked it word for word before Task 1, not at Step 8, and so before its first Codex run (Global Constraints, "Codex data"). Applied in: Task 4 Steps 8–9, Task 5 Steps 2, 6 and 8.

## Defaults (approved, D14)

The brief has no decisions. It flagged two defaults, and this plan settles both as the brief recommends. PD1–PD13 are this plan's own. The owner approved all of them as written at plan review (D14).

- **DF-ARMS. Every arm runs on the owner's Mac, on one Claude Code binary.** The Codex reader can run only where the owner's `codex` CLI is logged in. Plan 81 ran its Claude arms in a cloud container and its Codex arms on the Mac, and the record lists that split as limit 8 (`:294-296`). One split remains: plan 81's control results on the bare plants, the reference for plants with no defense, ran on Claude Code 2.1.319 in the cloud, and the Mac had no 2.1.319 (record `:43-44`). `env -i` is not part of this choice, because the spec requires it when a Desktop session drives the runs (Constraints, "Isolation"). If wrong: the arms differ in place and version again, and the results file repeats limit 8.
- **DF-AMEND. A plan conflict that a copy's own amendment causes** gets the label `false-alarm` with a reason that starts `amendment:`, as in plan 81 (record `:345`). The clean-copy false-alarm bar is judged both on the literal count and on the count without those lines, as plan 81's owner ruled (record `:124-126`, `:351`). Each copy keeps its spec as it stood at plan review. So a value that the plan's own amendment sets, such as plan 55's `cc_guide` suite name, disagrees with the copy's spec. A stand-in that marks the sentence `amended` makes rule 9 skip it. A stand-in that does not raises a plan conflict, which is neither a false alarm nor real. If wrong: the bar counts a known amendment as a false alarm, or the label hides a real one.
- **PD1. The defense sentences** (spec Verification 2, designer's call 14). Each is the planner's reasoning, not an owner decision. Each is one Global Constraints line, inserted after one line of plan 81's planted copy:

  | Copy | Inserted after this line of `RB/copies/<copy>/plan.md` | The defense line |
  |---|---|---|
  | `p53-unit` | `:30`, the line that starts `  - R4.1: copies are "regular files` | `- R1.3's cap guards a stored field, so the lint measures the stripped value in UTF-8 bytes: a non-ASCII value can stay within 500 code points and still overflow a 500-byte field.` |
  | `p66-bound` | `:106`, the line that starts `- **Freeze.**` | ``- The cutoff falls at the start of the freeze date, so every `bump` or `verify` run on that date resolves the same files, however late in the day it runs.`` |
  | `p55-default` | `:18`, the line that starts `- **Shell forms (R3.2):**` | ``- A suite with no `pythons` key runs on 3.12, the oldest Python that every suite still supports, so the default run keeps that floor tested.`` |

- **PD2. The two two-reading plants** (spec Verification 2). Each edits one sentence of a source spec, and the plan stays as the owner approved it. Both readings are recorded here, before any run:

  | | `p66-today` | `p55-exit` |
  |---|---|---|
  | Source | plan 66 and `specs/package-versions.md` at `526b7de` | plan 55 and `specs/test-suite-registry.md` at `f0ebef6` |
  | Sentence | R3.1's `bump` table row, spec `:202` | R4.3, spec `:172` |
  | Edit | `(default: today, UTC)` becomes `(default: today)` | `one line per finding and exit 1.` becomes `one line per finding and an error exit.` |
  | Slot | `default` | `value` |
  | Reading A, the plan's | Today's date in UTC: plan `:1258` (`help='the new freeze date (default: today, UTC)'`), `:1263` (`datetime.datetime.now(datetime.timezone.utc).date()`), `:1357` | Exit 1: plan `:807` and `:827` (`assert rs.main(['--check'], …) == 1`) |
  | Reading B | Today's date in the local time zone of the machine that runs `bump` | Exit 2, the status that R3.7 gives "a usage error, an unknown suite name, or a registry that fails validation" |
  | Screening | "UTC" appears elsewhere only in R2.1's `uv.toml` row (`:174`), about upload times. The same row says that uv "reads a bare date in local time". "today" appears elsewhere only at `:89`, a dated fact. No amendment changes the edited row (PD3). Plan 66 quotes only its parenthetical, in the `:1258` help string, which is reading A. | No other sentence gives `--check`'s status for a finding. R3.7 covers runs and gives exit 2 to "a registry that fails validation". R3.9 stops the other modes with exit 2, and says that `--check` reports the same failures "as findings (R4.3)". R6.1's "with exit 2" tests the R3.9 failures. No amendment changes R4.3 (PD3), and plan 55 does not quote it. |
  | Lean toward A | R2.1's row puts the freeze date in UTC: "00:00:00Z", "(UTC)". | R3.9 sets `--check` apart from the modes that stop "with exit 2". |
  | Lean toward B | The same row says that uv "reads a bare date in local time". | R3.9 sends `--check`'s validation failures to R4.3 "as findings", and R3.7 gives exit 2 to "a registry that fails validation". R6.1's "with exit 2" may read as covering `--check` too. |

  Both edits fill a slot that a reader must commit to, the `default` or the `value`. Plan 81's three plant sentences stay unedited, so no sentence carries two kinds of plant.

  The decider regexes (Task 2) screen one sentence at a time, by its words. The cross-references in the two lean rows were checked by hand on 2026-11-09. An adjudicator that follows a lean rules a reading, not `unclear`. Reading A makes the rep a miss, and reading B makes it a plan conflict, which PD10 counts apart. So a lean can lower the step's catches on a plant for a reason in the plant, not in the step. The results file gives the adjudicator's deciding quote for each ruling on these sentences, so the owner can tell the two apart. The owner kept `p55-exit`, whose leans run through two requirements, at plan review (D14).
- **PD3. The amendment answer keys.** These are the source-spec lines that each plan's amendment tasks change. They were found on 2026-11-09 by matching each replace block's old text in the source spec:
  - plan 53, Task 1 (A1–A11): `104, 159, 181-182, 192, 203, 238-240, 268-270, 276-277, 371-377, 394, 401-402, 419`;
  - plan 55, Task 1 Step 5 (Q1): `83, 98, 144-145, 186`;
  - plan 66, A1–A3 (Tasks 1, 4 and 6): `94-95, 138-148, 182`.

  A sentence is amended when one of its lines is in its key. The kit checks the plants against the keys. The scorer reports the stand-in's `amended` marks against them, both missing marks and extra marks.
- **PD4. Numbering rules** (spec Design 2; the exact rules are left to the builder):
  1. A heading line is no sentence. It becomes the `heading` of the sentences below it.
  2. A fenced block is one sentence, its fence lines included.
  3. A table row is one sentence, the header row included. The separator row is none.
  4. Other lines join with single spaces into a block, which ends at a blank line, a heading, a fence, a table row or a new list item. A block splits after `.`, `!` or `?`, and any closing `*`, `` ` ``, `"`, `'`, `)` or `]`, when whitespace and then a character other than a lowercase letter follow.
  5. A block does not split after a label such as `R2.1.`, `D3.` or `A11.`, after a bold run-in title that opens the block, alone or after its label (``R1.3 **`compatibility`.**``), after `e.g.`, `i.e.`, `etc.` or `vs.`, or after a list marker such as `1.` at the start of the block. So plan 53's R1.3 stays one sentence with its value.
- **PD5. Statements, matching and the quote check** (spec Design 3 and 6; the format and the normalization are left to the builder).
  - A statement is one `<statement>` block of `<entry sentence="S<n>">` elements. Each holds `<quote>`, `<subject>`, `<value>`, `<unit>`, `<edge>` and `<default>`. A reader adds `<other_reading>`, which holds `none` or its own `<value>`, `<unit>`, `<edge>` and `<default>`. The stand-in adds `<plan_lines>` and `<amended>` (`none` or a task), and `<note>` when it notices a difference.
  - The rulings are one `<rulings>` block of `<ruling case="C<n>" verdict="reading|no-value|unclear">` elements. Each holds `<quote>`, and with `reading`, the four slots.
  - Matching applies `flatten` (Task 1) to each slot, then these rules:
    - A trailing period is dropped.
    - `none`, `n/a`, `-` and an empty slot all read `none`.
    - A comma between digits is dropped.
    - `a to b` and `a-b` between numbers read `a-b`.
    - Parentheses around a list read as brackets. A trailing comma and the spaces after commas inside brackets are dropped.
    - A one-item list reads as its item.
  - An entry whose quote is not in its numbered sentence, or whose sentence does not exist, is returned (designer's call 6). No writer can redo it in a probe, so the comparison drops it and lists it as `returned`. The scorer reports a drop on a planted sentence apart.
  - The comparison does not check a stand-in value against its cited plan lines (spec, "Left to the builder"). The fidelity outcomes cover the planted sentences.
- **PD6. Reps.** A rep is VOID when:
  - its JSON is unreadable;
  - it errored or stopped on its budget;
  - it ran more than one turn;
  - its reply lacks the closing tag of its block (`</statement>`, `</rulings>` or `</findings>`);
  - (Codex only) its log names another model, or shows a line that is not the header, the prompt, the reply or a known status line;
  - (adjudicator only) a case has no ruling, or a ruling names no case.

  A VOID reader, stand-in or control rep reruns under the next rep number. A VOID adjudicator rep reruns on its own prompt after its reply is renamed `rep<k>.void<j>.json`. Rep *k* of an arm uses the *k*-th scored rep, in rep order, of each input, so a rerun never shifts the pairing of the other reps.
- **PD7. Cost.** The cap is $4.00 a call (plan 81's DF8). If a pilot rep costs more than $3.00, that role's cap rises to twice its pilot cost, and the pilot record says so. The pilot projects Task 5 at 25 reader, 30 stand-in, 25 control and 90 adjudicator calls, and asks the owner above $150.
- **PD8. The adjudicator in the probe** (spec, "Left to the builder"). It runs once per arm, copy and rep, on that arm's cases only. So no one-reader arm sees the other reader's entry, and rule 3 reads its own copy's stand-in. Its prompt names the readers `Reader A` and `Reader B`, never by model. It is a kit prompt run by `claude -p --model opus`, not an agent file. A rep with no case runs no adjudicator.
- **PD9. When `gpt-6-sol` "misses a bar"** (D7). `gpt-6.1-sol` runs only when, with `gpt-6-sol`, one of these holds for the `pair` arm:
  - it catches a planted copy in fewer than 4 of 5 reps;
  - its clean-copy false-alarm mean, on either DF-AMEND count, is above 1.0;
  - its clean-copy unclear mean is above 1.0;
  - it beats Claude alone neither on catches nor on false alarms.

  The control's half of the catch bar never triggers it, because no Codex model can move it.
- **PD10. Catches, near catches and fidelity, as tokens.** These are the flattened forms that the scorer looks for in an entry's four slots joined:

  | Copy | Spec's value | Planted value, or reading A | Reading B |
  |---|---|---|---|
  | `p53-unit` | `character` | `byte` | |
  | `p66-bound` | `day after`, `next day`, `following day`, `+1 day`, `+ 1 day` | `00:00:00z on the freeze date`, `start of the freeze date` | |
  | `p55-default` | `3.13` | `3.12` | |
  | `p66-today` | | `utc` (whole word, `default` slot) | `local` (whole word, `default` slot) |
  | `p55-exit` | | `1` (whole word, `value` slot) | `2` (whole word, `value` slot) |

  The `p66-bound` planted tokens keep the `00:00:00z` prefix. R2.1's row also says "Files uploaded on the freeze date itself (UTC) are included", and a correct reading may copy that into its `edge` slot.

  - **A catch on an argued plant** is a `plan-conflict` outcome on the planted sentence. Its agreed reading holds a spec token and no plant token, and the stand-in entry holds a plant token (spec Verification 8).
  - **A catch on a two-reading plant** is an `unclear` outcome on the planted sentence. A `plan-conflict` on that sentence is counted apart.
  - **A near catch on an argued plant** is any other `plan-conflict` or `unclear` outcome on the planted sentence. The executor judges it.
  - **For the control,** plan 81's catch rule holds on an argued plant. On a two-reading plant, a catch is a finding whose `<quote>` holds the edit's `spec_key` (designer's call 16). A finding without that quote whose `<plan>` text comes from one of the edit's plan lines (PD2) is a near catch. The bare tokens `1` and `utc` are too common to mark one.
  - **The stand-in's fidelity** on the planted sentence reads all of its entries on that sentence, and takes the first of these that applies (spec Verification 4, adapted for the two-reading plants):
    1. `amended`: an entry marks the sentence amended;
    2. `absent`: there is no entry;
    3. `faithful`: the entries hold a planted or reading-A token, and no spec or reading-B token;
    4. `spec value`: they hold a spec token and no planted token (argued plants);
    5. `other`: they hold a reading-B token and no reading-A token (two-reading plants);
    6. `unmatched`: any other case, which the executor labels.
- **PD11. Hand labels**, only where a bar or a catch reads them:
  - each `plan-conflict` on `p55-clean`, in every arm: `false-alarm` (with an `amendment:` reason under DF-AMEND) or `real`;
  - each `unclear` outcome on `p55-clean`, in every arm: `ambiguous` or `false` (designer's call 17);
  - each near catch, in every arm and in the control: `near-catch` or `near-miss`;
  - each `unmatched` fidelity entry: `faithful`, `spec-value` (the label form of `spec value`) or `other`.

  Each label line gives a reason. `table` counts a `near-catch` as a catch, as plan 81's did.
- **PD12. Kit tests and the frozen kit.** Kit tests are `selftest` subcommands, as plan 81's DF7 made them, so `run_suites.py --check` needs no new suite. Task 4's pilot may change the prompt texts and the normalization. Each change lands before Task 5's first run, with a deviation note that cites the pilot evidence, and the pilot reruns on the changed text. From Task 5's first run the kit is frozen: a needed change stops the task for the owner.
- **PD13. The reader's scope and the examples.** The reader prompt keeps the spec's definition of a stated value. It adds one sentence: skip a value that only records a fact (a measurement, an inventory row, a dated history), unless a requirement makes the plan keep or use it. Every worked example in a prompt comes from a domain that no probe spec touches, so that no prompt carries a probe value.

## Files

| Path | Responsibility | Task |
|---|---|---|
| `RS/kit/` | A copy of `RB/kit/`, the start of this kit | 1 |
| `RS/kit/number.py` | Numbers a spec's sentences, `S1` to `Sn` (PD4) | 1 |
| `RS/kit/plants.py` | Plan 81's three plants with their defenses (PD1), the two edits (PD2), the answer keys (PD3), the tokens (PD10), the six copies | 2 |
| `RS/kit/make_copies.py` | Builds and checks the copies, their numbered specs and `MANIFEST.txt` | 2 |
| `RS/kit/compare.py` | Parses statements and rulings, pairs and matches entries, applies rules 1–9 (PD5) | 3 |
| `RS/kit/prompts/reader.txt`, `standin.txt`, `adjudicator.txt` | The three new prompt texts. `control.txt` stays plan 81's. | 4 |
| `RS/kit/build_prompts.py` | Fills the four prompts, and builds each arm's cases and adjudicator prompts | 4 |
| `RS/kit/measure.py` | VOID checks, `score`, `table` with the bars, `selftest` | 4 |
| `RS/kit/run_reps.sh`, `RS/kit/run_codex.sh` | Plan 81's runners, with `env -i`, the pinned binary and skipped reps | 4 |
| `RS/copies/<copy>/{spec.md,plan.md,numbered.txt,SITES.txt}`, `RS/copies/MANIFEST.txt` | The built copies | 2 |
| `RS/runs/` | Prompts, replies, cases, results, `SCORE.txt`, `CLASSIFY.txt`, `SOURCES.txt`, `BINARY.txt`, `TABLE.txt` | 4, 5 |
| `specs/red-baseline-statement-readings.md` | The results file | 6 |
| `specs/statement-level-readings.md` | One results line under Verification, "Probe first" | 6 |
| `specs/deferred_items.md` | A progress note on "Spec-reading test check"; with no build plan, its closing | 6 |
| `specs/superpowers-drift-spec-v7-0-2.md` | With no build plan only: finding 24 and its disposition bullet | 6 |

The copies:

| Copy | Spec id | Source plan and spec | Plant |
|---|---|---|---|
| `p53-unit` | `p53` | plan 53 at `b8f4d0f` | plan 81's unit plant, plus the PD1 defense |
| `p66-bound` | `p66` | plan 66 at `526b7de` | plan 81's bound plant, plus the PD1 defense |
| `p55-default` | `p55` | plan 55 at `f0ebef6` | plan 81's default plant, plus the PD1 defense |
| `p55-clean` | `p55` | plan 55 at `f0ebef6` | none |
| `p66-today` | `p66-today` | plan 66 at `526b7de` | the PD2 `bump` edit |
| `p55-exit` | `p55-exit` | plan 55 at `f0ebef6` | the PD2 R4.3 edit |

The run folders under `RS/runs/` are these:

- `reader-opus/<spec id>/` and `reader-gpt-6-sol/<spec id>/`;
- `standin-opus/<copy>/`;
- `control-opus/<copy>/`, for the five planted copies;
- `step-pair-gpt-6-sol/<copy>/`, `step-claude/<copy>/` and `step-codex-gpt-6-sol/<copy>/`;
- the shared prompts in `prompts/`, and the pilot in `pilot/`;
- the `gpt-6.1-sol` folders, only after PD9 triggers.

---

### Task 1: Copy the kit and write the numbering script

**Files:**
- Create: `RS/kit/` (a copy of the 10 tracked files of `RB/kit/`)
- Create: `RS/kit/number.py`

**Interfaces:**
- Consumes: nothing.
- Produces, in `number.py`:
  - `@dataclass(frozen=True) class Sentence(n: int, heading: str, text: str, lines: tuple[int, int])`. `n` counts from 1 and is written `S<n>`. `heading` is the nearest heading line above, or `''`. `text` joins the source lines with single spaces, except a fenced block, which keeps its lines. `lines` holds the first and last source line, 1-based.
  - `flatten(text: str) -> str`: lowercase, en and em dashes to `-`, backticks, quote marks and `*` removed, whitespace collapsed. The key lookups and the quote check use it.
  - `number(text: str) -> list[Sentence]`, deterministic (PD4).
  - `numbered_text(sentences: list[Sentence]) -> str`: each heading line once, where it changes, then one `S<n>. <text>` item for each sentence.
  - `uv run python RS/kit/number.py <spec.md>` prints `numbered_text(number(text))`. `selftest`.

- [x] **Step 1: Copy the kit, and commit the copy alone**

```bash
mkdir -p specs/red-baseline-statement-readings
cp -R specs/red-baseline-acceptance-tests/kit specs/red-baseline-statement-readings/kit
git add specs/red-baseline-statement-readings/kit
git status --short specs/red-baseline-statement-readings
```

Expected: 10 added files, with the names that `git ls-files specs/red-baseline-acceptance-tests/kit` lists, and no `__pycache__` (`.gitignore` drops it). Run `bash build/run_commit_lints.sh` (expected: `commit lints passed`), then:

```bash
git commit -m "chore(specs): copy plan 81's probe kit for the statement-readings probe (plan 83 task 1)"
```

Later tasks change the copy, so `git log -p` on `RS/kit/` shows each change against plan 81's kit.

- [x] **Step 2: Write `number.py selftest`**

`FENCE = '`' * 3` keeps a literal fence out of the source. The selftest numbers this 20-line sample:

```python
SAMPLE = '\n'.join([
    '### R2. Synced outputs', '',
    'The first sentence wraps', 'over two lines. The second', 'ends here.', '',
    '| Key | Default |', '|---|---|', "| `pythons` | `['3.13']` |", '',
    f'{FENCE}toml', '[python]', "dev = '3.13'", FENCE, '',
    'R2.1. **`sync`.** It writes three files.', '',
    'Floors cover runtime backends (e.g. `h5netcdf` for NetCDF) as well.', '',
    '1. `uv run` respects the cutoff. It gave 0.12.0.'])
s = number(SAMPLE)
assert [x.text for x in s] == [
    'The first sentence wraps over two lines.', 'The second ends here.',
    '| Key | Default |', "| `pythons` | `['3.13']` |", f"{FENCE}toml\n[python]\ndev = '3.13'\n{FENCE}",
    'R2.1. **`sync`.** It writes three files.',
    'Floors cover runtime backends (e.g. `h5netcdf` for NetCDF) as well.',
    '1. `uv run` respects the cutoff.', 'It gave 0.12.0.']
assert [x.lines for x in s[:2]] == [(3, 4), (4, 5)] and s[4].lines == (11, 14)
assert {x.heading for x in s} == {'### R2. Synced outputs'}
assert number(SAMPLE) == s
assert flatten('A “Quoted” – `x`  **y**') == 'a quoted - x y'
```

- [x] **Step 3: Run it to verify it fails**

Run: `uv run python specs/red-baseline-statement-readings/kit/number.py selftest`
Expected: FAIL with `NameError`, because nothing is defined yet.

- [x] **Step 4: Implement `number.py`**

One line-by-line scan, fence-aware as `extract.py` is: a heading or a table row inside a fence is text. The split rules are PD4's.

- [x] **Step 5: Run it to verify it passes**

Run: the same command. Expected: `number selftest ok`.

- [x] **Step 6: Commit**

```bash
git add specs/red-baseline-statement-readings/kit/number.py
git commit -m "test(specs): add the sentence-numbering script to the statement-readings kit (plan 83 task 1)"
```

### Task 2: Plant the copies

**Files:**
- Modify: `RS/kit/plants.py`, `RS/kit/make_copies.py`
- Create (built): `RS/copies/<copy>/{spec.md,plan.md,numbered.txt,SITES.txt}` for the six copies, and `RS/copies/MANIFEST.txt`

**Interfaces:**
- Consumes: `number.number`, `number.flatten`, `number.numbered_text`, `extract.section_of`.
- Produces, in `plants.py`:
  - `Plant` keeps plan 81's six fields. It adds `defense: tuple[str, str]`, the anchor line's start and the PD1 line, and the PD10 tokens `spec_tokens: tuple[str, ...]` and `plant_tokens: tuple[str, ...]`.
  - `@dataclass(frozen=True) class TwoReading(spec_key: str, edit: tuple[str, str], slot: str, reading_a: str, reading_b: str, plan_lines: tuple[int, ...], a_tokens: tuple[str, ...], b_tokens: tuple[str, ...], deciders: tuple[str, ...])`, with PD2's values and PD10's tokens:
    - `spec_key` is the edited sentence's own words: `Sets the freeze date (default: today)` and `one line per finding and an error exit`.
    - `edit` is `(old, new)`, and `old` occurs once in the source spec.
    - `deciders` are regexes that no other flattened sentence of the edited spec may match: `(r'today,? \(?utc', r'utc (date|day)')` for `p66-today`, and `(r'--check[^.]*exit [12]', r'finding[^.]*exit [12]')` for `p55-exit`.
  - `Copy` keeps `id`, `commit`, `spec_path`, `plan_path` and `plant`. It adds `spec_id: str` and `two: TwoReading | None`.
  - `AMENDED_LINES: dict[str, tuple[tuple[int, int], ...]]`, keyed `'p53'`, `'p55'` and `'p66'` (PD3).
  - `COPIES`, in the order of the copies table.
- Produces, in `make_copies.py`:
  - `plant(source: str, plant: Plant) -> tuple[str, list[Site]]`. It applies plan 81's replacements, then inserts the defense line after the one line that starts with the anchor.
  - `edit_spec(source: str, two: TwoReading) -> str`.
  - `planted_sentence(copy: Copy, sentences: list[Sentence]) -> Sentence`: the one sentence whose flattened text holds the flattened `spec_key` of the plant or the edit.
  - `amended_sentences(copy: Copy, sentences: list[Sentence]) -> set[int]`: the `n` of each sentence whose `lines` meet the copy's answer key.
  - `build` writes the files above. `MANIFEST.txt` gains the `numbered.txt` lines, with the origin `built`. `selftest`.

- [x] **Step 1: Write the new selftest assertions**

Plan 81's assertions stay, on `replacements` and on `true_hits`. These are added for each copy, where `source` and `source_spec` come from `git show` at the copy's commit, and `plan81` is `Path('specs/red-baseline-acceptance-tests/copies')`:

```python
planted, sites = (source, []) if copy.plant is None else plant(source, copy.plant)
spec = source_spec if copy.two is None else edit_spec(source_spec, copy.two)
if copy.plant:
    assert planted.count(copy.plant.defense[1]) == 1
    assert any(site.section == 'global-constraints' and site.text == copy.plant.defense[1] for site in sites)
    assert true_hits(planted, copy.plant) == []                         # the defense restates no true value
    assert planted.replace(copy.plant.defense[1] + '\n', '', 1) == (plan81 / copy.id / 'plan.md').read_text()
else:
    assert planted == source
if copy.id in ('p55-clean', 'p55-exit'):
    assert planted == (plan81 / 'p55-clean' / 'plan.md').read_text()
sentences = number(spec)
if copy.plant or copy.two:
    target = planted_sentence(copy, sentences)                        # exactly one sentence holds the key
    assert target.n not in amended_sentences(copy, sentences)          # Review Focus 1, trap 3
if copy.plant:
    flat = flatten(target.text)                                        # PD10: the spec's words hold a spec token
    assert any(t in flat for t in copy.plant.spec_tokens) and not any(t in flat for t in copy.plant.plant_tokens)
if copy.two is None:
    assert spec == source_spec
else:
    before = number(source_spec)
    assert len(before) == len(sentences)
    assert [b.n for b, a in zip(before, sentences) if b.text != a.text] == [target.n]
    others = [flatten(a.text) for a in sentences if a.n != target.n]
    assert not any(re.search(d, t) for d in copy.two.deciders for t in others)
    assert flatten(before[target.n - 1].text) not in flatten(planted)   # the plan does not quote it
```

The selftest prints, for each copy, its site lines in plan 81's form, its planted sentence (`S<n>` and the first 80 characters), and its amended sentence numbers.

- [x] **Step 2: Run it to verify it fails**

Run: `uv run python specs/red-baseline-statement-readings/kit/make_copies.py selftest`
Expected: FAIL with `AttributeError` or `ImportError`, because the new fields and functions are not defined yet.

- [x] **Step 3: Write the values into `plants.py`**

Copy each value from PD1, PD2, PD3 and PD10, character for character. The defense anchors are `'  - R4.1: copies are "regular files'`, `'- **Freeze.**'` and `'- **Shell forms (R3.2):**'`.

- [x] **Step 4: Implement the changes to `make_copies.py`**

`build` writes `RS/copies/`. It refuses to overwrite a file that differs, as plan 81's did. `SITES.txt` holds the site lines, and `numbered.txt` holds `numbered_text(number(spec))`.

- [x] **Step 5: Run the selftest, then build**

Run: `uv run python specs/red-baseline-statement-readings/kit/make_copies.py selftest`, then the same with `build`.
Expected: `make_copies selftest ok`, then six copy folders and a `MANIFEST.txt` of 24 lines. Each argued copy's `SITES.txt` holds plan 81's sites plus one `global-constraints` line for its defense. Each two-reading copy's `SITES.txt` is empty.

- [x] **Step 6: Commit**

```bash
git add specs/red-baseline-statement-readings/kit/plants.py specs/red-baseline-statement-readings/kit/make_copies.py \
  specs/red-baseline-statement-readings/copies
git commit -m "test(specs): plant argued and two-reading copies for the statement-readings probe (plan 83 task 2)"
```

### Task 3: The comparison script

**Files:**
- Create: `RS/kit/compare.py`

**Interfaces:**
- Consumes: `number.flatten`.
- Produces, in `compare.py`:
  - `@dataclass(frozen=True) class Slots(value: str, unit: str, edge: str, default: str)`.
  - `@dataclass(frozen=True) class Entry(sentence: int, quote: str, subject: str, slots: Slots, other: Slots | None, plan_lines: str, amended: str, note: str)`. A reader entry leaves the last three empty. A stand-in entry has `other=None`, and `amended` holds `none` or a task.
  - `parse_statement(text: str) -> list[Entry] | None`. It returns `None` (VOID) when the text has no complete `<statement>…</statement>` block.
  - `normalize_slot(text: str) -> str` (PD5). `match(a: Slots, b: Slots) -> bool`: the four slots are equal after `normalize_slot`.
  - `check_quotes(entries: list[Entry], sentences: dict[int, str]) -> tuple[list[Entry], list[Entry]]`: the kept entries and the returned ones.
  - `@dataclass(frozen=True) class Case(id: str, rule: int, sentence: int, subject: str, entries: dict[str, list[Entry]])`. `entries` is keyed `'claude'` and `'codex'`, and holds only the arm's readers, unpaired entries included.
  - `@dataclass(frozen=True) class Reading(sentence: int, subject: str, slots: Slots)`.
  - `@dataclass(frozen=True) class Outcome(kind: str, sentence: int, subject: str, agreed: Slots | None, planner: Slots | None, detail: str)`. `kind` is one of `plan-conflict`, `missing`, `unclear`, `amended-skip`, `unchecked`, `no-value` and `returned`.
  - `@dataclass(frozen=True) class Phase(cases: list[Case], agreed: list[Reading], outcomes: list[Outcome])`.
  - `reader_phase(sentences: dict[int, str], claude: list[Entry] | None, codex: list[Entry] | None, planner: list[Entry]) -> Phase`. It runs the quote checks, the pairing of spec Design 6 and rules 1–5. A missing reader passes `None`, and each of the other reader's entries then falls under rule 3 or rule 4.
  - `@dataclass(frozen=True) class Ruling(case: str, verdict: str, quote: str, slots: Slots | None)`. `verdict` is `reading`, `no-value` or `unclear`.
  - `parse_rulings(text: str, cases: list[Case]) -> list[Ruling] | None`. It returns `None` (VOID) in three cases: the text has no complete `<rulings>` block, a case has no ruling, or a ruling names no case.
  - `resolve(phase: Phase, rulings: list[Ruling], planner: list[Entry]) -> list[Outcome]`. It applies rules 6–9 to each agreed reading, both rule 1's and each `reading` ruling's. It adds a `no-value` outcome for each `no-value` ruling and an `unclear` outcome for each `unclear` ruling, and it keeps the Phase's own outcomes.
  - `phase_to_json(phase: Phase) -> str`, `phase_from_json(text: str) -> Phase`, `outcomes_to_json(outcomes: list[Outcome]) -> str` and `outcomes_from_json(text: str) -> list[Outcome]`.
  - `uv run python RS/kit/compare.py selftest`.

- [x] **Step 1: Write `compare.py selftest`**

> Deviation: the selftest adds a second fixture beyond the plan's assertions. In it, two values in one sentence pair by subject, entities unescape, and a planner entry with no sentence is returned, never compared.

The fixtures are `SENTENCES` (S1–S10), the statements `READER_A` (Claude), `READER_B` (Codex) and `PLANNER`, and `RULINGS`. They use the values `x`, `y` and `z`, chosen so that each sentence tests one rule:

| S | A | B | P | Ruling | Pair outcome | A case in Claude alone |
|---|---|---|---|---|---|---|
| 1 | x | x | x | | none | no |
| 2 | x | x | y | | `plan-conflict` | yes |
| 3 | x | x | absent | | `missing` | yes |
| 4 | x | y | x | `reading` x | none | no |
| 5 | x | y | z | `unclear` | `unclear` | yes |
| 6 | x | x | y, `amended` | | `amended-skip` | yes |
| 7 | absent | absent | x | | `unchecked` | no |
| 8 | x | absent | y | `no-value` | `no-value` | yes |
| 9 | x, its quote not in S9 | absent | absent | | `returned` | no |
| 10 | x | x, other reading y | x | `reading` x | none | no |

```python
A, B, P = (parse_statement(t) for t in (READER_A, READER_B, PLANNER))
assert parse_statement(READER_A.replace('</statement>', '')) is None          # cut off: VOID
assert normalize_slot("('3.12',)") == normalize_slot("['3.12']") == normalize_slot('3.12') == '3.12'
assert normalize_slot('1,000') == '1000' and normalize_slot('N/A') == normalize_slot('') == 'none'
assert normalize_slot('1–500') == normalize_slot('1 to 500') == '1-500'
phase = reader_phase(SENTENCES, A, B, P)
assert sorted((c.sentence, c.rule) for c in phase.cases) == [(4, 2), (5, 2), (8, 3), (10, 4)]
assert all(set(c.entries) <= {'claude', 'codex'} for c in phase.cases)        # no stand-in entry (D10)
assert parse_rulings('<rulings></rulings>', phase.cases) is None               # a case without a ruling
out = resolve(phase, parse_rulings(RULINGS, phase.cases), P)
assert sorted((o.sentence, o.kind) for o in out) == [(2, 'plan-conflict'), (3, 'missing'), (5, 'unclear'),
    (6, 'amended-skip'), (7, 'unchecked'), (8, 'no-value'), (9, 'returned')]
alone = reader_phase(SENTENCES, A, None, P)                                     # Claude alone
assert sorted(c.sentence for c in alone.cases) == [2, 3, 5, 6, 8]
assert all(set(c.entries) == {'claude'} for c in alone.cases)
assert phase_from_json(phase_to_json(phase)) == phase and outcomes_from_json(outcomes_to_json(out)) == out
```

- [x] **Step 2: Run it to verify it fails**

Run: `uv run python specs/red-baseline-statement-readings/kit/compare.py selftest`
Expected: FAIL with `NameError`.

- [x] **Step 3: Implement `compare.py`**

> Deviation: PD5's comma rule drops only a thousands separator. `parse_rulings` is also VOID for an unknown verdict or two rulings on one case. The builder's choices are in the docstring: subject keys, a lone matched entry that joins the agreed readings, `unchecked` for an unpaired planner entry, the quote check on the planner's entries, and HTML-unescaped fields.

Tags are parsed with regular expressions, as plan 81's `measure.py` parsed its blocks. Case ids run `C1`, `C2` and on, in sentence order.

- [x] **Step 4: Run it to verify it passes**

Run: the same command. Expected: `compare selftest ok`.

- [x] **Step 5: Commit**

```bash
git add specs/red-baseline-statement-readings/kit/compare.py
git commit -m "test(specs): add the statement comparison script to the statement-readings kit (plan 83 task 3)"
```

### Task 4: Prompts, runners, scorer and pilot

**Files:**
- Create: `RS/kit/prompts/standin.txt`. Replace: `RS/kit/prompts/reader.txt`, `RS/kit/prompts/adjudicator.txt`
- Modify: `RS/kit/build_prompts.py` (rewritten), `RS/kit/measure.py` (rewritten from plan 81's), `RS/kit/run_reps.sh`, `RS/kit/run_codex.sh`
- Create: `RS/runs/BINARY.txt`, `RS/runs/pilot/`

**Interfaces:**
- Consumes: everything that `compare.py` produces, `number.number`, `number.numbered_text`, `plants.COPIES`, `make_copies.planted_sentence` and `make_copies.amended_sentences`.
- Produces, in `build_prompts.py` (run from the repository root):
  - `reader <spec-id> <out-file>`, from `reader(spec_id: str) -> str`: `reader.txt` with the numbered spec. It calls `guard`.
  - `standin <copy> <out-file>`, from `standin(copy_id: str) -> str`: `standin.txt` with the numbered spec and the copy's plan, each plan line prefixed `<n>| `.
  - `control <copy> <out-file> <sha>`, from `control(copy_id: str, sha: str) -> str`: plan 81's `control.txt` with writing-plans' `SKILL.md` at `<sha>`, the copy's `spec.md` and its `plan.md`. Plan 81's `control` read `origin/main` itself. The argument pins one sha for all five control prompts.
  - `adjudicator <runs-dir> <arm> <copy>`. For each *k* up to 5 for which each input has a *k*-th scored rep, it reads that rep of the arm's readers and of `standin-opus/<copy>/`. The readers are `reader-opus/<spec id>/` and `reader-<model>/<spec id>/`. It runs `compare.reader_phase`, and writes `<runs-dir>/step-<arm>/<copy>/cases/rep<k>.json` and either `prompts/rep<k>.txt` or, with no case, `prompts/rep<k>.skip`.
  - `adjudicator_prompt(phase: Phase, spec_id: str) -> str`.
  - `guard(text: str, spec_id: str) -> None`. It refuses (`SystemExit`) a reader or adjudicator prompt that holds any of these: a copy folder or a source plan path, a PD1 defense line, or a plant or edit token that the spec text lacks.
  - Every built prompt appends one `SOURCES.txt` line. It gives the copy or spec id and its `MANIFEST.txt` sha256, and for `control`, the sha.
- Produces, in `measure.py`:
  - `reply(path: Path) -> str | None`, as in plan 81's.
  - `void_reason(path: Path, kind: str, model: str | None = None, prompt: str | None = None) -> str | None`. It returns `None` for a scored rep. Otherwise it returns one of `unreadable`, `error`, `budget`, `turns`, `no-block`, `model` and `residual` (PD6). `kind` is `statement`, `rulings` or `findings`. For a Codex rep, the check also reads the log next to the `.md` reply. It compares the log header's model with `model`, and it runs plan 81's `codex_residual` with `prompt`.
  - `scored_reps(run_dir: Path, kind: str, model: str | None = None, prompt: str | None = None) -> list[Path]`: the first five scored reps, in rep order. Names of the form `rep<k>.void<j>.json` are skipped.
  - `@dataclass class StepScore(catch: bool, near: list[int], conflict_on_plant: bool, conflicts: int, unclear: int, missing: int, unchecked: int, skipped: int, returned: int, returned_on_plant: bool, miss_reason: str)`. `near` holds outcome indices.
  - `score_step(outcomes: list[Outcome], copy: Copy, planted_n: int | None) -> StepScore`. `miss_reason` is `''` for a catch. Otherwise it is one of `returned`, `absent`, `amended`, `agreed` (the readers matched the stand-in) or `other`.
  - `fidelity(planner: list[Entry], copy: Copy, planted_n: int) -> str` (PD10). `amend_marks(planner: list[Entry], amended: set[int]) -> tuple[int, int]` returns the entries on a key sentence without a mark, and the marked entries off the key.
  - `uv run python RS/kit/measure.py score <runs-dir> <arm> <copy-or-spec-id>`. It writes `SCORE.txt`, and for a step arm also `results/rep<k>.json`.
  - `table <runs-dir>`. It prints one row for each arm and copy, then the bar lines of spec Verification 9, then a `PD9 trigger: yes|no (<bars>)` line.
  - `selftest`.
  - `CLASSIFY.txt` lines read `rep<k> <outcome|finding|fidelity><j> <label> <reason>`, with PD11's labels.
- Produces, the runners:
  - `CLAUDE_BIN=<path> bash RS/kit/run_reps.sh <prompt-file|prompt-dir> <out-dir> <first> <last> <model> [<budget>]`. It is plan 81's runner with these changes:
    - it runs under `env -i` (Global Constraints) and calls `$CLAUDE_BIN` in place of `claude`;
    - its rep folders are `/tmp/plan83-rep-XXXXXX`;
    - it refuses to run when `CLAUDE_BIN` is unset, or when its sha256 differs from the one in `RS/runs/BINARY.txt`;
    - in the directory form, it skips rep *i* when `rep<i>.skip` exists.
  - `bash RS/kit/run_codex.sh` keeps plan 81's arguments. It runs under the same `env -i`, from `/tmp/plan83-codex-XXXXXX` folders.

- [x] **Step 1: Write `measure.py selftest`**

> Deviation: the selftest uses `TODAY_N` for `p66-today`, whose planted sentence is S134, not S115. It also adds `_control_selftest` and `_step_selftest`, and two mutants fail them.

The inline fixtures are scored against `p66-bound`, `p66-today` and `p55-exit` from `plants.COPIES`:

```python
assert void_reason(CUT_JSON, 'statement') == 'no-block'                  # cut off at the output limit
assert void_reason(BUDGET_JSON, 'statement') == 'budget'
assert void_reason(CODEX_TOOL_MD, 'statement', 'gpt-6-sol', PROMPT) == 'residual'   # the watch item
assert void_reason(CODEX_OTHER_MODEL_MD, 'statement', 'gpt-6-sol', PROMPT) == 'model'
assert [p.name for p in scored_reps(DIR_REP2_VOID, 'statement')][:2] == ['rep1.json', 'rep3.json']
assert score_step(CATCH_OUTCOMES, P66_BOUND, PLANTED_N).catch
assert score_step(TOKENLESS_CONFLICT, P66_BOUND, PLANTED_N).near == [0]
miss = score_step(RETURNED_ON_PLANT, P66_BOUND, PLANTED_N)
assert not miss.catch and miss.returned_on_plant and miss.miss_reason == 'returned'   # Review Focus 5
assert score_step(UNCLEAR_ON_EDIT, P55_EXIT, EDIT_N).catch
edit = score_step(CONFLICT_ON_EDIT, P55_EXIT, EDIT_N)
assert edit.conflict_on_plant and not edit.catch
assert [fidelity(p, P66_BOUND, PLANTED_N) for p in (PLANTED_P, SPEC_P, AMENDED_P, [])] == [
    'faithful', 'spec value', 'amended', 'absent']
assert fidelity(UTC_P, P66_TODAY, EDIT_N) == 'faithful' and fidelity(LOCAL_P, P66_TODAY, EDIT_N) == 'other'
assert amend_marks(MARKS_P, {4, 5}) == (1, 1)
```

A temporary runs folder then checks `table`:

- it refuses a `p55-clean` conflict that has no `CLASSIFY.txt` line;
- it counts `false-alarm` lines both with and without the `amendment:` reasons;
- it prints `catch bar p66-bound: step 4/5, control 1/5: met`.

- [x] **Step 2: Run it to verify it fails**

Run: `uv run python specs/red-baseline-statement-readings/kit/measure.py selftest`
Expected: FAIL with `NameError` or `ImportError`.

- [x] **Step 3: Implement `measure.py`**

> Deviation: `void_reason` also makes a Claude rep VOID (`model`) when it used a second model, and a step rep whose rulings fail `parse_rulings` is VOID (`cases`). `score_step` takes a `listed` flag to tell `agreed` from `absent`. Near catches are listed only for a rep with no catch.

`score` picks the kind of rep from the arm's prefix:

- **`reader-`:** the VOID checks; the entries and `other_reading`s of each reply.
- **`standin-`:** the VOID checks; on the planted sentence, the fidelity and `amend_marks`; and the notes of each reply.
- **`control-`:** plan 81's `score_reply`, with PD10's rule on a two-reading copy.
- **`step-`:** for each rep, it reads `cases/rep<k>.json` and either the adjudicator's `rep<k>.json` or the `.skip` file, runs `compare.resolve`, writes `results/rep<k>.json` and scores the rep with `score_step`. Each outcome on a sentence in the copy's answer key carries the flag `amended-sentence`, to guide the DF-AMEND label.

Each line of a `table` row gives these columns:

- the scored reps and the catches out of 5, with the near catches;
- the conflicts on the planted sentence;
- the false alarms per rep, both literal and without `amendment:`;
- the unclear cases per rep, with the `ambiguous` and `false` counts;
- the owner load per rep (unclear cases plus plan conflicts);
- the missing, unchecked, skipped and returned entries per rep;
- the cost: dollars for Claude, `tokens used` for Codex.

Each stand-in row gives the fidelity counts, the amended marks (missing and extra) and the notes. The bar lines follow spec Verification 9 and PD9. "Beats" means more catches, or a lower clean-copy false-alarm mean on either DF-AMEND count.

- [x] **Step 4: Run it to verify it passes**

Run: the same command. Expected: `measure selftest ok`.

- [x] **Step 5: Write the prompts and `build_prompts.py`, with its selftest**

> Deviation: the selftest checks for `specs/plans/` outside the numbered spec only, because three spec sentences name it. `reader.txt` drops the *(designer's call)* mark. `adjudicator.txt` gets a one-reader opening and a paragraph on slot forms. The guard skips the reader entries inside an adjudicator prompt, and matches tokens as whole words.

`reader.txt` states, in this order:

1. "You read a spec alone and state what it asks, in fixed slots. A planner wrote a plan from this spec. You never see that plan." (D9)
2. The first two sentences of spec Design 3, word for word ("A **stated value** is …"), then PD13's sentence.
3. The slot table of spec Design 3 without its *(designer's call)* marks, and the first bullet under it ("A sentence that states two values gets two entries…").
4. "Fill every slot. When the words allow another reading of a slot, write that reading's value, unit, edge and default in `other_reading`. Otherwise write `none`."
5. "You have no tools. Do not look for a plan or any other file."
6. One worked example (PD13).
7. The numbered spec, then the PD5 format and "Reply with exactly one `<statement>` block and nothing else."

`standin.txt` states, in this order:

1. "You are the planner. You wrote the plan below from the spec below. Before two readers state what the spec asks, you state your plan's values in the same slots." (D13)
2. The rules of spec Design 4:
   - Fill the slots for each value that your plan uses, keyed by sentence number.
   - State the value that your plan implements, from its lines, not a fresh reading of the spec.
   - Use the slot forms, not the plan's code syntax. PD13's example is a plan line `MAX_RETRIES = 3`, which gives the value `3`.
   - Cite the plan lines that hold the value in `plan_lines`.
3. "`amended`: when a task of your plan amends the spec so that this sentence changes, name that task. Otherwise write `none`. Mark each sentence that an amendment's replacement text changes, one sentence at a time, never a whole requirement or section."
4. "When you notice that your plan's value differs from the spec, still state your plan's value, and add a `<note>` that says so. You cannot edit the plan." (spec Verification 4)
5. "You have no tools."
6. The numbered spec, the plan with line numbers, then the stand-in's format.

`adjudicator.txt` states, in this order:

1. "Two readers each stated, from the spec alone, what the spec asks. Each case below is a sentence where they differ, where one reader alone states a value, or where a reader names another reading."
2. "For each case, rule on the reading that the text supports. Give the verdict `reading` with its value, unit, edge and default, or `no-value` when the sentence states no value. Quote the words that decide the case, word for word, from the numbered spec. When no words decide it, rule `unclear` with an empty quote." (D3)
3. "You see no plan. You have no tools, and you edit no file."
4. The numbered spec, then the cases: each case's id, its `S<n>`, and its entries under `Reader A` (Claude) and `Reader B` (Codex) (PD8). Then the PD5 rulings format.

`build_prompts.py selftest` asserts:

```python
for spec_id in ('p53', 'p66', 'p55', 'p66-today', 'p55-exit'):
    text = reader(spec_id)
    assert '@@' not in text and 'copies/' not in text and 'specs/plans/' not in text
    assert not any(c.plant and c.plant.defense[1] in text for c in COPIES)
adj = adjudicator_prompt(CLAUDE_ONLY_PHASE, 'p55')                       # a one-reader arm
assert 'Reader B' not in adj and CODEX_SENTINEL not in adj and PLANNER_SENTINEL not in adj
try:
    guard(reader('p53') + COPIES[1].plant.defense[1], 'p53')
    raise AssertionError('guard passed a defense line')
except SystemExit:
    pass
```

Run: `uv run python specs/red-baseline-statement-readings/kit/build_prompts.py selftest`. Expected: FAIL before the code exists, then `build_prompts selftest ok`.

- [x] **Step 6: Adapt the runners**

The changes are the ones listed under Interfaces. When Step 9 finds a reply cut off at the output limit, `run_reps.sh` passes `CLAUDE_CODE_MAX_OUTPUT_TOKENS` through `env -i` for every role, and the pilot record says so.

- [x] **Step 7: Pin the binary, and check isolation**

```bash
claude --version
mkdir -p ~/.cache/agent-skills/scratch/plan83-bin
cp -p "$(realpath "$(command -v claude)")" ~/.cache/agent-skills/scratch/plan83-bin/claude
shasum -a 256 ~/.cache/agent-skills/scratch/plan83-bin/claude
```

Write the path, the version line and the sha256 to `RS/runs/BINARY.txt`. Then run:

```bash
CLAUDE_BIN="$HOME/.cache/agent-skills/scratch/plan83-bin/claude" bash specs/red-baseline-statement-readings/kit/run_reps.sh \
  specs/red-baseline-reviewer-planning-contract/kit/isolation_probe.txt specs/red-baseline-statement-readings/runs/pilot/isolation 1 1 opus
```

Expected: the reply's five lines each read `NO`. Any `YES` stops the task: report it.

- [x] **Step 8: Ask the owner about Codex, then probe Codex's context**

> Deviation: the session asked this question word for word before Task 1, and the owner answered "Approve Codex runs" (D16).

Ask once in this session: "The probe's Codex reader sends five numbered spec texts to OpenAI: the specs of plans 53, 55 and 66 as they stood at plan review, and two copies with one sentence edited (plan 66's `bump` default and plan 55's R4.3). It also sends plan 81's Codex context probe. Approve the Codex runs for this session? That is 1 context probe and 1 pilot rep, then 25 reader reps on `gpt-6-sol`, and 25 more on `gpt-6.1-sol` only if `gpt-6-sol` misses a bar." Without a yes, skip the Codex parts of this task and of Task 5 (Global Constraints, "Codex data").

With a yes, run `codex --version` and `codex exec --help`. Expected: a version line, and help that lists `-m`, `-c`, `--skip-git-repo-check`, `-C`, `-o`, `--ignore-user-config`, `--ignore-rules`, `--ephemeral`, `--enable` and `--disable`. Then run:

```bash
bash specs/red-baseline-statement-readings/kit/run_codex.sh specs/red-baseline-acceptance-tests/runs/pilot/codex-isolation/probe.txt \
  specs/red-baseline-statement-readings/runs/pilot/codex-isolation 1 1 gpt-6-sol
```

Expected: the reply matches the column "With Task 4's flags" of the record's Appendix A table. If a shell, web search or an MCP server is in reach, stop the task and report it.

- [x] **Step 9: Pilot one rep of each role on the largest inputs**

> Deviation: the pilot made three kit changes (PD12). Pairing falls back to matching slots, then to shared subject words, where spec Design 6 pairs by subject only. Units match when both name a unit and share a content word. Each case shows the entries it asks about apart from the other entries on its sentence. Also, `runs/CONTROL_SHA.txt` pins one `origin/main` sha for every control prompt, and a free dry run of a whole Task 5 tree came before the freeze.

Build the prompts. Run `git rev-parse origin/main` once, and pass that sha to the `control` build. Then run rep 1 of each of these under `RS/runs/pilot/`:

- `reader-opus` on `p53` and on `p66`;
- `reader-gpt-6-sol` on `p66`, only with the Codex yes;
- `standin-opus` on `p66-bound`;
- `control-opus` on `p66-bound`;
- the `claude` and `pair-gpt-6-sol` step arms on `p66-bound`: the cases, and adjudicator rep 1.

Score each.
Expected: every rep scores, with no VOID. Read the last entry and the closing tag of each statement. Record each rep's `total_cost_usd` in `RS/runs/pilot/COST.txt`. Then project Task 5: 25 reader, 30 stand-in, 25 control and 90 adjudicator calls, each scaled by its prompt size against the pilot's. Above $150, stop and ask the owner (PD7). Any change that the pilot leads to follows PD12.

- [x] **Step 10: Commit**

```bash
git add specs/red-baseline-statement-readings/kit specs/red-baseline-statement-readings/runs
git commit -m "test(specs): add the statement-readings prompts, runners and scorer, and pilot them (plan 83 task 4)"
```

### Task 5: The runs

**Files:**
- Create: `RS/runs/prompts/`, and the run folders listed under "Files"; `RS/runs/TABLE.txt`. The `gpt-6.1-sol` folders only after Step 8.

**Interfaces:**
- Consumes: everything that Task 4 produces.
- Produces: for each arm and copy (or spec id), 5 scored reps with `SCORE.txt` and `SOURCES.txt`, `CLASSIFY.txt` where PD11 asks for labels, and `TABLE.txt`.

The kit is frozen (PD12). If this session did not ask the owner about Codex in Task 4, ask now, with Task 4 Step 8's question. In the commands below, `$K` stands for `specs/red-baseline-statement-readings/kit` and `$R` for `specs/red-baseline-statement-readings/runs`. Write each command out in full.

- [x] **Step 1: Build the shared prompts**

> Deviation: the 16 Claude-role folders (readers, stand-ins and control) have no `SOURCES.txt` of their own. The shared `runs/SOURCES.txt` holds exactly their 16 lines, and every Codex and step folder has its own (owner, completion gate).

- `build_prompts.py reader <s> $R/prompts/reader-<s>.txt` for each spec id;
- `build_prompts.py standin <copy> $R/prompts/standin-<copy>.txt` for each of the six copies;
- `build_prompts.py control <copy> $R/prompts/control-<copy>.txt <sha>` for each planted copy, with one sha from `git rev-parse origin/main`.

Expected: 16 prompt files. `SOURCES.txt` holds one sha for all five control prompts.

- [x] **Step 2: Run the readers**

- `CLAUDE_BIN=… bash $K/run_reps.sh $R/prompts/reader-<s>.txt $R/reader-opus/<s> 1 5 opus` for each spec id;
- `bash $K/run_codex.sh $R/prompts/reader-<s>.txt $R/reader-gpt-6-sol/<s> 1 5 gpt-6-sol` for each spec id. The five Codex runs can run in parallel, in the background; each takes about 50 minutes.

- [x] **Step 3: Run the stand-ins**

`CLAUDE_BIN=… bash $K/run_reps.sh $R/prompts/standin-<copy>.txt $R/standin-opus/<copy> 1 5 opus` for each of the six copies.

- [x] **Step 4: Run the control**

`CLAUDE_BIN=… bash $K/run_reps.sh $R/prompts/control-<copy>.txt $R/control-opus/<copy> 1 5 opus` for each planted copy. It does not run on `p55-clean` (designer's call 16).

- [x] **Step 5: Score them, and rerun each VOID rep**

`uv run python $K/measure.py score $R <arm> <id>` for each folder of Steps 2–4. Rerun each VOID rep under the next rep number (PD6) until each folder has 5 scored reps.

- [x] **Step 6: Run the three step arms**

> Deviation: the claude arm ran before the Codex readers finished, because it reads no Codex rep.

For each arm (`pair-gpt-6-sol`, `claude`, `codex-gpt-6-sol`) and each of the six copies:

```bash
uv run python specs/red-baseline-statement-readings/kit/build_prompts.py adjudicator specs/red-baseline-statement-readings/runs <arm> <copy>
```

Then run `CLAUDE_BIN=… bash $K/run_reps.sh $R/step-<arm>/<copy>/prompts $R/step-<arm>/<copy> 1 5 opus` and `uv run python $K/measure.py score $R step-<arm> <copy>`. A VOID adjudicator rep reruns on its own prompt (PD6).

- [x] **Step 7: Label, then tabulate**

> Deviation: each false-alarm reason starts with its cause: `pairing:`, `form:`, `slot:` or `scope:`. S144 on `p55-clean` is `real`, as in plan 81. One same-facet test decides every near-catch label, and the S126 unclear rulings are `ambiguous`.

Write a `CLASSIFY.txt` line for each item that a `SCORE.txt` lists to label (PD11). Judge each against the copy's spec only. For each label, check the reason against the plan line that the outcome's stand-in entry cites. Then run:

```bash
uv run python specs/red-baseline-statement-readings/kit/measure.py table specs/red-baseline-statement-readings/runs
```

Write its output to `RS/runs/TABLE.txt`.
Expected: a row for each arm and copy with every cell filled, the bar lines, and the `PD9 trigger:` line.

- [x] **Step 8: Run `gpt-6.1-sol` only when PD9 triggers**

> Deviation: this step started before Step 7's labels and `TABLE.txt`, because the PD9 trigger was already certain, and `TABLE.txt` later read yes. Four `codex-gpt-6.1-sol` conflicts on S144 are `false-alarm`, with the cause `pairing:`.

If the line reads `PD9 trigger: yes`, repeat these with the model `gpt-6.1-sol`:

- Step 2's Codex runs, into `reader-gpt-6.1-sol/`;
- Steps 5–7, for the arms `pair-gpt-6.1-sol` and `codex-gpt-6.1-sol`.

Otherwise skip this step, and the results file says so.

- [x] **Step 9: Commit**

```bash
git add specs/red-baseline-statement-readings/runs
git commit -m "test(specs): run the readers, stand-ins, control and step arms of the statement-readings probe (plan 83 task 5)"
```

### Task 6: The results file and the owner's review

**Files:**
- Create: `specs/red-baseline-statement-readings.md`
- Modify: `specs/statement-level-readings.md` (one line), `specs/deferred_items.md` (one note)
- Modify, with no build plan only: `specs/superpowers-drift-spec-v7-0-2.md`, and the backlog item in `specs/deferred_items.md`

**Interfaces:**
- Consumes: `TABLE.txt`, every `CLASSIFY.txt` and `SOURCES.txt`, `RS/runs/BINARY.txt`, `RS/runs/pilot/COST.txt` and `RS/copies/MANIFEST.txt`.

- [x] **Step 1: Write the results file**

It gives these sections, in this order:

1. **Sources.** The date and the shas:
   - the copies' source commits, and the commit of plan 81's kit that Task 1 copied;
   - the pinned binary's version and sha256, the codex-cli version, and each model and effort from the log headers;
   - the writing-plans sha of the control;
   - the owner's Codex approval, quoted.
2. **The plants.** Each argued plant with its site count and its defense line, and each two-reading plant with both readings, from PD1 and PD2.
3. **The table**, from `TABLE.txt`, with the false-alarm counts with and without `amendment:`.
4. **The bars.** Each bar with its result: met, missed or not run. Then the inputs of the designer's reading: the plants on which the step beats the control, and the clean-copy bars.
5. **The second reader.** `pair` against `claude` on catches and on false alarms. Then the `codex` arm, for information.
6. **Fidelity and owner load:**
   - the stand-in's outcomes and notes;
   - its amended marks, missing and extra;
   - the missing, unchecked and returned entries;
   - the owner load, an upper bound because no planner answers a case.
7. **Real conflicts.** Each `real` label, with its spec quote.
8. **Cost.**
9. **What the probe cannot show.** The limits of spec Verification 10, PD2's leans with the adjudicator's deciding quotes on the two edited sentences, and each limit found in execution.
10. **Appendix A:** isolation, with what reached the Codex reps.
11. **Appendix B:** the executor's rulings and the owner's decisions, word for word.

The results file recommends nothing about a build plan (D8). It states plan 81's 15 of 15 control catches as the reference for the bare plants.

- [x] **Step 2: Link it, and note the backlog**

Under the spec's Verification, "Probe first", after item 10, add one line: "Results: `specs/red-baseline-statement-readings.md` (plan 83, <date>)."

Under the item "Spec-reading test check" (`specs/deferred_items.md`, section `spec-reading-test-check`), add one note line: "→ progress <YYYY-MM-DD> (plan 83): the statement-readings probe ran, and its results are in `specs/red-baseline-statement-readings.md`. The owner reviews them before any build plan. The item stays open."

Edit neither plan 81 watch item.

- [x] **Step 3: Check and commit**

Run: `bash build/run_commit_lints.sh`. Expected: `commit lints passed`.

```bash
git add specs/red-baseline-statement-readings.md specs/statement-level-readings.md specs/deferred_items.md
git commit -m "docs(specs): record the statement-readings probe results (plan 83 task 6)"
```

- [x] **Step 4: Owner gate (D8)**

Present the table, the bars and the second-reader comparison, and stop. The owner decides whether anyone writes a build plan, and what it keeps. Write no build plan. Copy the owner's decision, word for word, into the results file's Appendix B, and commit it.

- [x] **Step 5: With no build plan only, close finding 24's line**

> Deviation: the layer 4 item went into this plan's backlog section in this step, not in the Plan Completion Protocol. Finding 24's row in the drift spec's summary table changed too. The Reported-order bullet kept its text and got a dated update. The new citations use the spec's retired path.

Skip this step when a build plan is to come. The spec then stays live (Global Constraints, "Completion").

This step follows the spec's "Closing the backlog and the drift spec":

1. Tick the item "Spec-reading test check" with `→ done <YYYY-MM-DD> (plan 83)`. Its closing note says three things:
   - what happened to layers 3 and 5;
   - that layer 1 applies only when a spec has examples (old D4);
   - that layer 4 stays open as a new item, with an `→ item:` marker. The Plan Completion Protocol adds that item to this plan's section.
2. From `specs/superpowers-drift-spec-v7-0-2.md` as it stands on `main` at that time, update finding 24 (its heading at `:769` at planning) and its bullet in the "Suggested disposition" section (the heading at `:1025` at planning).
3. In the Plan Completion Protocol, retire `specs/statement-level-readings.md` with this plan.

Finding 21's closure stays with the old spec's build plan.
