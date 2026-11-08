# Development history

## 80-development-history-record — 2026-11-08
Plan: specs/plans/completed/80-development-history-record.md · Spec: specs/completed/development-history-record.md (retired)

Differences from the design:
- Ruling (Task 1): run_reps.sh keeps the comment `Plan 77 deviation (a)` instead of the brief's 77 → 80 change — that deviation was plan 77's, so 80 would misname its source, and the record's Kit section says so — none if wrong; no rep reads the comment.
- Ruling (Task 4): Task 4 commits before Task 2 and Task 3 (commit order 4 → 2 → 3); Task 2's finished work stays uncommitted in the working tree until Task 4 lands — check_conformance's orphan-bundled-file rule exits 1 for any commit while no skill text names history_entry.py, and the plan first names it in Task 4; the commit gate (Global Constraints) outranks task order, and this keeps Task 4 Step 1's RED checks true with no stub, exemption or --no-verify — one commit's tree (Task 4's) names a script that lands in the next commit. Plan markup: a `> Deviation:` note under Task 4.
- Ruling (Task 2): a deviation's text is the whole blockquote note, joined over its continuation `>` lines, not only the text after the colon on the first line — real retired plans (12, 14, 19, 20) wrap deviation notes, and first-line text ends mid-sentence — the draft's deviation lines get longer, and Finish step 4 shortens them, if wrong.
- Ruling (Task 2): a deviation under a non-task `##` or `###` heading after the tasks prints with no task label and `Source: plan, § <heading text>.` — 12+ retired plans hold such notes, and the last task's label named the wrong source — the agent rewrites one Source pointer if wrong.
- Ruling (Task 7): the gate-tag wording round (fd4749b) adds two sentences to both executors' gate paragraphs — a tagged ruling is still a decision, the history entry records it in place of a spec amendment, ask nothing about it, a revert makes it a deferred item — treatment at T5 passed 2/5 (clause 4: three reps asked the partner to confirm or choose), and treatment2 passed 5/5 at fd4749b; the text restates the spec's gate section and Non-goals — the gate text grows by about 50 words, and an untested executing-plans copy, if wrong. Plan markup: a `> Deviation:` note under Task 7.
- Ruling, contradicts spec (final review): a decision qualifies when its `Applied in:` part matches `\(spec amendments?\b`, not only the literal `(spec amendment)` — retired plans 38, 43, 44, 53, 58 and 66 write `(spec amendments)`, `(spec amendment A2)` and `(spec amendment: R8.8 …)`, and spec rule 4's purpose is every spec-level decision — a prose-only decision that names a spec amendment could slip in if wrong. Plan markup: a `> Deviation:` note under Task 2.
- Ruling (final review): the `/deferred` step and the reference's `deferred` command pass `--date <the date on the pass's ticks>` — `--date` defaults to the machine's local today, so a pass that crosses midnight would print nothing and lose its entry silently — one more flag to type if wrong. Plan markup: a `> Deviation:` note under Task 6.
- Ruling (final review): a fence inside a blockquote (`> ```…`, `> ~~~…`) is code for `draft`, so a quoted `> Deviation:` inside it is not read — Codex [P2], within Review Focus 1 — only plan 40 has blockquoted fences today, holding bash — none if wrong.
- Deviation (Task 1): `run_reps.sh` keeps its comment `Plan 77 deviation (a)`. Source: plan, Task 1.
- Deviation (Task 2): a deviation note's text joins its wrapped `>` lines, and a note under a non-task heading after the tasks gets `§ <heading>`, not a task label. Source: plan, Task 2.
- Deviation (Task 2): a fence inside a blockquote counts as code. Source: plan, Task 2.
- Deviation (Task 2): a decision qualifies on `\(spec amendments?\b`, not only `(spec amendment)`. Source: plan, Task 2.
- Deviation (Task 4): Task 4 committed before Tasks 2 and 3, for the orphan-bundled-file lint. Source: plan, Task 4.
- Deviation (Task 6): `/deferred` passes `--date`, the date on the pass's ticks. Source: plan, Task 6.
- Deviation (Task 7): one wording round (`fd4749b`) added two sentences to both gate paragraphs. Source: plan, Task 7.
- Deferred: 2 items. Source: specs/deferred_items.md, § 80-development-history-record.
