# Plan-completion triage and gate reverts — Design Spec

**Status:** COMPLETE (2026-11-19), implemented by plan 101 (`specs/plans/completed/101-plan-completion-triage-and-gate-revert.md`). It was APPROVED on 2026-11-17. The design came from a brainstorming session on 2026-11-17 for two `/deferred`
Design picks of that day. Decisions D1 and D2 are the owner's rulings from the `/deferred` pass. D3 and D4 are the
owner's answers in the brainstorming session. Text marked *(designer's call)* was the designer's choice. The owner
approved this file, its designer's calls included, on 2026-11-17 ("Approve spec").

This spec changes two parts of the plan-completion protocol. First, completion stops running the full backlog
triage on every plan: it shows the stats line and the plan's own new items, and it runs the triage only when the aged
tail is above 0. Second, a revert that the owner asks for at the completion gate is done at once, as a follow-on
task under Protocol step 1, in place of a backlog item.

## Motivation

| Fact | Evidence |
|---|---|
| Step 4 runs triage steps 1–4 when the backlog has 20 or more open items or any aged tail. On 2026-11-17 the backlog has 157 open items and an aged tail of 0. So every completion reads the whole backlog and hands the owner a full triage, even when the plan deferred two items. The cost grows with the backlog, not with the plan. | `skills/writing-plans/SKILL.md:363-384`; `deferred_stats.py` on 2026-11-17: `157 open, 462 ever closed (closure rate 75%), aged >45d: 0` |
| Both executors' gate paragraphs say that a revert of a tagged ruling `makes it a deferred item`. Protocol step 1 says an answer that unblocks work is done now. So a revert asked for at the gate has two rules. | `skills/subagent-driven-development/references/final-review.md:43-44`; `skills/executing-plans/references/final-review.md:174-175`; `skills/writing-plans/SKILL.md:297-298` |
| The same gate paragraphs already send one answer to step 1: when the owner overrules a `Ruling: (unclear)` line, the change goes to protocol step 1, which does it now. | `skills/subagent-driven-development/references/final-review.md:44-48`; `skills/executing-plans/references/final-review.md:175-179` |
| The writing-plans `SKILL.md` body is 19,689 characters. The compaction window that `check_conformance.py` applies is 19,700. The current step 4 is 1,060 characters. | `build/cc_guide/conformance.toml`, check `compaction-window`; measured 2026-11-17 |
| History "Finish the draft" step 2 relabels each ruling that the gate tagged `contradicts spec`. Its step 1 deletes rulings that did not change the build, and its examples are a declined finding and a parked finding. Nothing names a reverted ruling. Today a reverted ruling still stands when the entry is written, because the revert waits in the backlog. Once a revert lands at once, the ledger still holds the ruling, and the entry could record a spec contradiction that no longer exists. Nothing records an overruled `(unclear)` ruling either, so no existing path can be reused. | `skills/writing-plans/references/history.md:76-82` |
| Plan 80's spec says a reverted ruling `makes it a deferred item as today`. That spec is retired. | `specs/completed/development-history-record.md`, Contradicting rulings at the gate |

## Decisions

- **D1** (owner, 2026-11-17, `/deferred` ruling on "Narrow the read-only triage at plan completion"): approve a
  change to step 4. Completion prints the stats line and the plan's new items. The full triage runs under
  `/deferred` or when the aged tail is non-zero.
- **D2** (owner, 2026-11-17, `/deferred` ruling on "A revert asked for at the gate has two rules"): a revert asked
  for at the gate is done at once under Protocol step 1, and both gate paragraphs change to match.
- **D3** (owner, 2026-11-17, this session): a ruling reverted at the gate leaves the history entry. The revert writes
  a ledger line that names the ruling, and history "Finish the draft" step 1 deletes a ruling that such a line names.
  The two alternatives were: keep the ruling in the entry with a `Ruling, reverted at the gate` label (a new label
  form, and maybe a change to `history_entry.py`), and no change (cheapest, but the gate's tag still invites a false
  `contradicts spec` line).
- **D4** (owner, 2026-11-17, this session): Approach 1, edit in place (see Approaches).

## Goals

1. Each plan completion shows backlog health (the stats summary line) and what this plan deferred. Its cost does not
   grow with the backlog.
2. The full triage runs where the owner acts on it: under `/deferred`, or at a completion when the aged tail is above
   0, because finishing-a-development-branch Step 1b asks about those items next.
3. One rule for a revert asked for at the gate: protocol step 1 does it now.
4. `specs/history.md` records only rulings that stand in the shipped build.

## Non-goals

- No change to `deferred_stats.py`, the Triage rubric, `/deferred`, finishing Step 1b or the Thresholds values. The
  volume line (`At or above the 20-item volume threshold.`) stays as the stats print it.
- No edit to Protocol step 1 for the revert. Its `Unblocked by an answer → implement it now` already holds the rule
  (D2). The gate paragraphs send the revert there, as they already do for an overruled `(unclear)` ruling. Plan 101
  adds the final review's Declined to judge lines to step 1's leftovers, for the item that the next bullet names
  (owner, plan 101, 2026-11-17).
- No `references/step-recipe.md` fallback. The rewrite of step 4 frees about 360 characters of the window. The item
  that needs room for Declined to judge lines in step 1 stays its own item → item: 73-reviewer-and-planning-contract —
  2026-10-30. Plan 101 folds it in after the step 4 shrink (owner, plan 101, 2026-11-17).
- No edit to the retired spec `specs/completed/development-history-record.md`. Retired specs are history. This spec
  replaces its `as today` line for every later plan.
- No script prints the plan's new items. Step 3 has just appended them, so the agent has them. *(designer's call)*

## Anti-goals

The change fails, even if it runs, when any of these happen:

- A completion stops showing the stats summary line.
- A completion hides an aged tail above 0 until finishing's gate.
- The gate puts a tagged ruling to the owner as a question ("revert this?"). The `gate-tag` case guards this in the
  subagent-driven-development copy, and the new `gate-tag-ep` case in the executing-plans copy.
- A history entry keeps `Ruling, contradicts spec` for a ruling that was reverted at the gate.
- The writing-plans `SKILL.md` body goes past the compaction window.

## Approaches

1. **Edit in place (chosen, D4).** Rewrite step 4 where it stands, shorter. Change the callers line in
   `references/deferred-backlog.md`. Put one identical sentence in both gate paragraphs. Add one clause to history
   "Finish the draft" step 1. Leave Protocol step 1 as it is. This is the smallest change, and step 4 stays in the
   part of the skill that compaction re-attaches.
2. **Move step 4 out to the reference.** Step 4 becomes a two-line pointer to a new section in
   `references/deferred-backlog.md`. This frees about 900 characters, enough for the Declined to judge item too. But
   an agent at step 4 must open another file to get the rule, and the change takes in another item's goal.
3. **Approach 1, plus the revert named in Protocol step 1.** The rule is then visible to any executor, not only the two
   that exist. But it is stated in two places, and it spends the room that step 4 frees. No third executor exists.

## Design

### Step 4: Backlog report

Step 4 keeps its place in the protocol and its read-only, non-blocking nature. Its content:

1. Run `deferred_stats.py` from the repo root, as today.
2. Always put its summary line in the completion report, even when the plan deferred nothing.
3. Under the summary line, list the items that step 3 appended for this plan, one line each. When step 3 appended
   none, write `nothing deferred`. *(designer's call: each line gives the item's first words and its `Size:`, which
   matches how the stats name an item.)*
4. When the summary line's `aged >45d:` is above 0, also run steps 1–4 of the Triage rubric, and present the
   proposal in the completion batch, as today.
5. Otherwise run no triage. Say that `/deferred` runs the full triage.
6. The triage never blocks completion. The aged tail is gated at finishing-a-development-branch Step 1b, as today.

The step's heading changes from "Backlog triage" to "Backlog report", because the triage is now conditional.
No other file names step 4 by its heading (`git grep` on 2026-11-17). *(designer's call)*

A draft that fits the content, 698 characters against 1,060 today. The micro-tests fix the final words.

````markdown
**4. Backlog report.** Run from the repo root:

```bash
uv run <this-skill-dir>/scripts/deferred_stats.py
```

Put its summary line (open count, closure rate, aged tail) in the completion
report, and under it the items step 3 appended for this plan, one line each,
or `nothing deferred`. Always: the summary keeps the trend legible.

When `aged >45d:` is above 0, also run steps 1–4 of the **Triage rubric** in
`references/deferred-backlog.md`, which are read-only, and present the
proposal in this completion batch. Otherwise the full triage waits for
`/deferred`, which alone executes a disposition. The triage never blocks
completion — the aged tail is gated at finishing-a-development-branch.
````

### The backlog reference

In `skills/writing-plans/references/deferred-backlog.md`, the callers list says that writing-plans `runs the
read-only triage at completion` (lines 9–10). It changes to say that completion shows the stats line and the plan's
new items, and runs the read-only triage only when the aged tail is above 0. The Thresholds table does not change:
the Volume row's "Used by" is still the soft one-line status that the stats print.

### The gate paragraphs

In both `skills/subagent-driven-development/references/final-review.md` and
`skills/executing-plans/references/final-review.md`, this sentence goes:

```text
Your partner may still ask to revert it, which makes it a deferred item.
```

One identical sentence, or pair of sentences, takes its place in both files. It says three things:

1. A revert that your partner asks for is a `follow-up task`, and protocol step 1 does it now. This is the same
   form as the `(unclear)` sentence that follows it.
2. The revert writes a ledger line that names the ruling it reverts. *(designer's call: the form is
   `Reverted at the gate: <task> ruling — <the ruling's first words>`.)* The line must not carry `Ruling:` with a
   colon. `history_entry.py` reads a line with `Ruling:` as its own mark as a ruling, and warns on a line that holds
   it later.
3. A restarted gate (Protocol step 1 restarts after the work lands) shows that ruling as reverted and asks nothing
   about it, and the history entry leaves it out. *(designer's call: the restarted gate reads the same ledger, so
   the line serves both readers.)*

A draft, for the micro-tests to fix:

```text
If your partner asks to revert it, the revert is a follow-up task, and
protocol step 1 implements it now. Ledger it as `Reverted at the gate:
<task> ruling — <its first words>`, so that a restarted gate shows the
ruling as reverted and the history entry leaves it out.
```

The rule covers a revert of any ruling that the gate listed, tagged or not. Goals 3 and 4 hold for both, and the
sentence's place after the tagged-ruling sentence must not read as a limit to tagged rulings. *(designer's call)*

The rest of each paragraph does not change. The two files keep their own line breaks.

### History "Finish the draft" step 1

In `skills/writing-plans/references/history.md`, `## Plan entries`, "Finish the draft" step 1 adds a third example: a
ruling that a `Reverted at the gate:` ledger line names. A draft:

```text
1. Delete each ruling that did not change what got built against the spec or the plan: one that declined a finding
   and kept the plan as written, one that parked a finding with no change to the build, or one that a
   `Reverted at the gate:` ledger line names.
```

Step 1 runs before step 2's relabel, so a reverted ruling is gone before the tag is read. The ledger line survives a
`/clear`, unlike the gate message. Rule 3 of the entry rules (which rulings go in) does not change: a reverted ruling
no longer changed what got built.

### Micro-tests

These are discipline-skill edits. Each wording change is micro-tested against a control arm, as the writing-skills
skill requires. The repo's kits set the pattern (`specs/baseline/red-baseline-backlog-protocol.md`,
`specs/baseline/red-baseline-development-history.md`).

**Kit.** A new kit, `specs/baseline/red-baseline-completion-triage/kit/`, with its record
`specs/baseline/red-baseline-completion-triage.md`. Its `run_reps.sh`, `isolation_probe.txt`, `show_reps.py` and
`build_prompts.py` are copies of plan 80's kit, with the plan number and temp prefix changed and the next-kit fixes
added: `run_reps.sh` drops `credential_expires_at` from each rep JSON file, and a no-model self-test shows that each
rep has its own scratch folder (owner, plan 101, 2026-11-17). Its `cases.py` is new. The re-runs of `gate-tag` and
`history-filter` build their prompts with plan 80's kit unchanged and run them through this kit's `run_reps.sh` (owner,
plan 101, 2026-11-17), and append a section to `specs/baseline/red-baseline-development-history.md`, as the
`/deferred` pass of 2026-11-12 did.

**Arms.** `control` reads each text at the plan's base commit. `treatment` reads each text after the edit tasks. Both
arms use the same frame, fixture and task. Only the sha differs. Fixtures use a domain that is not this repository.
The gate and history cases can reuse plan 80's bike-share fixture.

| Case | Kind | Texts under test | Situation | Pass |
|---|---|---|---|---|
| `triage-narrow` | RED | writing-plans `SKILL.md` body, `references/deferred-backlog.md` | Protocol step 4. The stats show 26 open items and `aged >45d: 0`. The plan deferred two items. | The reply shows the summary line and both items, presents no disposition proposal over the backlog, and goes on to step 5 or names `/deferred` for the full triage. |
| `triage-aged` | guard | the same | The same, but `aged >45d: 2`. | The reply shows the summary line and both items, presents a read-only grouped disposition proposal, and does not stop the protocol on it. |
| `gate-revert-sdd` | RED | `skills/subagent-driven-development/references/final-review.md` | The gate message went out with four rulings, the Task 2 ruling tagged `contradicts spec`. The partner answers: revert the Task 2 ruling, the others stand. | The next action does the revert now, as a task before plan markup, writes a ledger line that names the reverted ruling, and writes no backlog item for it. |
| `gate-revert-ep` | RED | `skills/executing-plans/references/final-review.md` | The same, in an executing-plans run. | The same, with the revert done inline. |
| `history-revert` | RED | writing-plans `SKILL.md` body, `references/histor*.md` | Protocol step 5 after a `/clear`. The gate message is not in context. The ledger holds the Task 2 ruling and a `Reverted at the gate:` line for it. The draft lists the Task 2 ruling. | The entry leaves out the Task 2 ruling, and meets the rest of `history-filter`'s pass rule. |
| `gate-tag-ep` | guard | `skills/executing-plans/references/final-review.md` | Plan 80's `gate-tag` fixture, recast as an executing-plans run. | Plan 80's `gate-tag` pass rule. |
| `gate-revert-untagged` | guard | `skills/subagent-driven-development/references/final-review.md` | As `gate-revert-sdd`, but the partner reverts the Task 3 module-name ruling, which the gate did not tag (owner, plan 101, 2026-11-17). | As `gate-revert-sdd`, for the Task 3 ruling. |
| `gate-declined` | RED | writing-plans `SKILL.md` body | Protocol step 1, run from writing-plans alone after a `/clear`. The final review left one finding unfixed and two Declined to judge lines (owner, plan 101, 2026-11-17). | The gate message puts both Declined to judge lines and the unfixed finding to the partner, in one batch. |
| `gate-tag` (re-run) | regression | plan 80's kit | Plan 80's fixture, unchanged. | Plan 80's pass rule. |
| `history-filter` (re-run) | regression | plan 80's kit | Plan 80's fixture, unchanged. | Plan 80's pass rule. |

**Bars.** A RED case needs `treatment 5/5; control fails at least 1 of 5`. A guard or regression case needs
`treatment 5/5`. The `gate-tag` re-run meeting its bar closes the second item's `Done when:`.

**`gate-tag-ep`.** No case has tested the executing-plans copy of the gate paragraph. Plan 80's kit reads only the
subagent-driven-development copy, and plan 80's history entry names the executing-plans copy as untested. This plan
rewrites that paragraph, so the case runs a control arm too, at the base commit, for reading only. The control shows
whether a failure is old or new. Its bar is the guard bar, `treatment 5/5`. A treatment below the bar gets the one
wording round, inside the paragraph that this plan already rewrites. *(designer's call)*

**Rules taken from the earlier kits.** 5 scored reps per case and arm. Every verdict is read by hand from the full
reply. The VOID rules, the leak check on the leak-view prompts, and the isolation probe (run again when the Claude
Code version is newer than the last probe) are as in plan 80's record. Fixtures and pass rules are registered before
any rep and not edited after a rep is seen. A case below its bar gets one wording round, as plan 80's `gate-tag` did.

**Stop rule.** A RED case whose control fails 0 of 5 has nothing to fix in wording. The record says so, and the
completion gate puts it to the owner. The wording that D1, D2 and D3 require still lands.

**Models.** *(designer's call)* `claude-sonnet-5-5` for the two triage cases, as plan 74 used for its
protocol-step cases. `claude-opus-5-5` for the gate and history cases, as plan 80's kit used.

**Spend stop.** *(designer's call)* $30 for the whole run, summed by `show_reps.py`. If the control arms alone pass
$12, the run stops and asks the owner.

## Constraints

- **The plan edits the skills that run it.** It changes writing-plans' completion protocol and both executors' gate
  paragraphs. Execute it in a worktree, with the tooling pinned to `main`. The installed skills are symlinks to the
  main checkout, so the plan's own completion runs under the old step 4 and the old gate rule. That is expected.
- **Parallel sessions.** Before the base commit and before each text edit, run `git fetch origin main` and
  `git log <base>..origin/main` over the edited files. A commit there stops the run until the owner decides. The
  Declined to judge item (Non-goals) also edits the protocol in `SKILL.md`.
- **The compaction window.** After the edit, `uv run --with pyyaml python build/check_conformance.py` exits 0, and
  the writing-plans `SKILL.md` body is 19,700 characters or fewer.
- **Commit lints.** `build/run_commit_lints.sh` passes on each commit.
- **No new install dependency.** The executors already name protocol step 1. The ledger line form is a text
  agreement between the executors and `references/history.md`, not a path, so `install.py`'s `DEPENDENCIES` and
  `SOFT_REFERENCES` do not change. The dependency-drift test confirms this.
- **Deferral-scan wording.** This spec, the plan and the records retire into `completed/` folders, so the deferral
  lint reads them. Quote deferral phrases from skill text in code spans, and give any deferral sentence a marker.

## Done when

1. Step 4 of the writing-plans Plan Completion Protocol has the content in Design, Step 4.
2. The callers line in `references/deferred-backlog.md` names the aged-tail condition.
3. Both gate paragraphs carry the same revert sentence, and neither says that a revert makes a deferred item.
4. History "Finish the draft" step 1 names a ruling that a `Reverted at the gate:` ledger line names.
5. Every case in Micro-tests meets its bar, or a case below its bar after its one wording round goes to the owner
   at the completion gate. The results are in the two records named there.
6. `check_conformance.py` exits 0, with the body at or under 19,700 characters, and the commit lints pass.
7. At plan completion, Protocol step 3 ticks both items with `→ done <YYYY-MM-DD> (plan <id>)`: "Narrow the
   read-only triage at plan completion" (section `backlog-protocol-design … — 2026-10-29`) and "A revert asked for at
   the gate has two rules" (section `80-development-history-record — 2026-11-08`).

## Left to the builder

- The final words of step 4, the gate sentence, the callers line and the history clause, within the content above.
  The micro-tests decide them.
- Each case's fixture text, leak pattern and per-rep budget.
- The task order. The control arms run before any text edit.
- Whether `triage-narrow` and `triage-aged` share one fixture with only the stats line changed. *(designer's
  suggestion: yes.)*
