# claude/plan-80-execution-636c1e: plan 80, the development history record

## Synopsis

**The plan:** Plan 80 answers finding 22 of the superpowers drift assessment. A mid-run `Ruling:` that contradicts
spec text never reaches the spec, and the ledger that holds it is deleted after the run. The approved spec chose
not to edit specs. Instead, each project gets one append-only file, `specs/history.md`. It records where each plan's
build differed from its design, and which deferred items each `/deferred` quick-fix pass closed.

**The build:** First, a micro-test kit ran control arms on the old texts. Next came a stdlib script,
`history_entry.py`, with two subcommands. `draft` reads a retired plan, the run's ledger and the backlog, and
`deferred` reads the quick-fix ticks for one date. Each prints a draft and writes no file. A new reference,
`references/history.md`, holds the file rules and the steps to finish a draft. Protocol step 5 points at it. Both
executors' gates now tag a ruling that contradicts spec text. `/deferred` writes its own entry. Treatment arms then
checked the gate tag and the ruling filter.

**The project:** Rulings now outlive the ledger. Every plan retirement and every quick-fix pass leaves a short,
sourced record in one place, in any project that uses these skills. This branch wrote the first entry, for plan 80
itself. Two deferred items remain: one rule for a revert asked for at the gate, and a source for the gate's tags
after a `/clear`.

## Background

Before the branch, the plan-completion protocol in `skills/writing-plans/SKILL.md` ran gate, plan markup, deferred
items and retire. The executors' gates (`references/final-review.md` in subagent-driven-development and
executing-plans) listed each ledger `Ruling:` as a decision already taken, with its cost if wrong. The ledger lived
in `<workspace>/progress.md`, and the executor deleted the workspace when the protocol finished. So the owner saw
each ruling once, and nothing kept it.

Differences from a design were spread over `> Deviation:` notes, `## Decisions` entries, deferred items and their
closure notes. Most closures came from `/deferred` quick fixes, not from plans. No file collected these.

The spec, `specs/completed/development-history-record.md`, records the owner's decisions D1 to D7. D2 says the
record need not be in the spec. D4 drops the earlier idea of a trigger that writes closures back into retired
plans. D5 picks a script that drafts the entry. D6 adds `/deferred` entries. D7 keeps only rulings that changed the
build.

`skills/writing-plans/SKILL.md` sat at the 20,000-character compaction limit. Any new line needed an equal cut.

## The change

### 1. The micro-test kit and control arms

`specs/red-baseline-development-history/kit/` holds `cases.py`, `build_prompts.py`, `run_reps.sh` and
`show_reps.py`. There are two cases. `gate-tag` checks that the gate tags a contradicting ruling and asks nothing
about it. `history-filter` checks that an agent finishing a draft drops rulings that changed nothing and relabels
the tagged one. Both cases share the bar `treatment 5/5; control fails at least 1 of 5`. The control arms ran on
the texts at `fb784f4` and failed 5 of 5 in both cases (`specs/red-baseline-development-history.md`, Control). The
treatment arms in part 6 depend on this baseline.

Ruling (Task 1): `run_reps.sh` keeps the comment `Plan 77 deviation (a)`, because that deviation was plan 77's.

### 2. The reference and the step 5 pointer

`skills/writing-plans/references/history.md` (131 lines) defines `specs/history.md`. The file is append-only, newest
last, with a `## <plan-stem> — YYYY-MM-DD` or `## /deferred — YYYY-MM-DD` heading for each entry. It fixes the entry
format, seven rules and an eight-step "Finish the draft" list. The rules copy each ruling whole, because its source
is deleted. They keep only rulings that changed the build (D7), and only decisions marked as spec amendments.

`skills/writing-plans/SKILL.md` gains three lines in step 5. They say to draft the entry before the
`chore(specs): retire plan <id>` commit and to append it in that commit. To pay for them, step 3 loses its example
block (11 lines removed in total). `references/deferred-backlog.md` already holds that example.

Ruling (Task 4): Task 4 committed before Tasks 2 and 3. The orphan-bundled-file rule in `check_conformance` fails
any commit while no skill text names `history_entry.py`. So the script's commit had to follow the reference that
names it.

### 3. `history_entry.py draft`

`skills/writing-plans/scripts/history_entry.py` (555 lines) is a PEP 723 stdlib script. `draft_entry` (line 388)
reads the plan's `**Spec:**` and `Roadmap:` header lines, its `> Deviation:` notes, its spec-level decisions, every
`Ruling:` line in `--ledger`, the deferred count, and items ticked `→ done … (plan <id>)`. It prints the draft with
warning lines such as `Rulings: no ledger given`. It exits 2 when the plan is missing or not a plan, or when
`--spec` and `--spec-status` do not come together.

The build made four rulings here that change the spec's or plan's text:

- A deviation's text is the whole blockquote note, joined over its wrapped `>` lines.
- A deviation under a non-task heading after the tasks prints `Source: plan, § <heading>`, not a task label.
- A fence inside a blockquote counts as code, so a quoted `> Deviation:` inside it is not read
  (`_blank_quoted_fences`, line 138).
- A decision qualifies on `SPEC_AMENDMENT_MARK_RE`, `\(spec amendments?\b` (line 84), not only the literal
  `(spec amendment)`. This one is tagged `contradicts spec`. Retired plans 38, 43, 44, 53, 58 and 66 use the wider
  forms.

The reference's rule 4 still names only the literal `(spec amendment)`. The script's docstring (line 13) gives the
wider rule.

### 4. `history_entry.py deferred`

`deferred_entry` (line 474) reads `specs/deferred_items.md` for items ticked
`→ done <date> (/deferred quick fix)` on `--date`. It leaves out items that an earlier `## /deferred — <date>`
section of `specs/history.md` already lists. When no item qualifies, it prints nothing and exits 0.

`skills/writing-plans/scripts/test_history_entry.py` (661 lines, 40 test functions) covers both subcommands with
inline fixtures. `build/suites.toml` names the history-entry tests in the `writing-plans` suite's note.

### 5. The gate tag

Both `references/final-review.md` gate paragraphs now tag each contradicting ruling
`contradicts spec: <spec section>`. They also say that a tagged ruling is still a decision, that the history entry
records it in place of a spec amendment, that the agent asks nothing about it, and that a revert makes it a deferred
item. Finish step 2 of the reference reads these tags.

Ruling (Task 7): the first treatment run passed `gate-tag` only 2 of 5, because three reps asked the partner to
confirm. One wording round (`fd4749b`) added the last two sentences, and `treatment2` passed 5 of 5.
`history-filter` passed 5 of 5 at `6df0a2c`. The whole kit cost $0.74 of a $12 spend stop.

### 6. `/deferred`, NOTICE and README

`commands/deferred.md` step 5 runs `history_entry.py deferred --date <YYYY-MM-DD>` before the archive run, when the
pass ticked at least one quick fix. It commits `specs/history.md` with the pass. The final review added `--date`,
because a pass that crossed midnight would otherwise print nothing and lose its entry. `build/sync_runtime_assets.py`
regenerated `runtimes/gemini/commands/deferred.toml`. `NOTICE` records the three new files as original work in the
adapted skill. `README.md` lists `specs/history.md` among the files the skills write.

### 7. The real-data check and retirement

Task 7 ran the script on real data. `draft` ran on plans 79 and 74. `deferred --date 2026-10-05` printed 47 item
lines, as expected. The plan, the spec and `specs/history.md`'s first entry then landed in the retire commit. That
entry lists 8 rulings, 7 deviations and 2 deferred items.

## What it adds to the project

- **A new record.** Each plan retirement now ends with a drafted, finished entry in `specs/history.md`. Each
  `/deferred` pass with a quick fix adds one too. Later readers of a retired spec go there to see where the build
  differed, with no edit to the spec.
- **A changed gate.** The owner now sees which rulings contradict the spec before they are recorded. The tag
  replaces the spec amendment that finding 22 proposed.
- **New dependents.** Writing-plans step 5, both executors' gates and `/deferred` step 5 now depend on the script
  and the reference. Finish step 2 depends on the gate's tags.
- **Not done.** Entries are not backfilled for plans retired earlier (a spec non-goal). The stale backlog pointer in
  retired plans stays a separate item.
- **Deferred by this branch** (`specs/deferred_items.md`, § 80-development-history-record):
  - A revert asked for at the gate has two rules. The spec and the gate paragraphs say it becomes a deferred item,
    but protocol step 1 unblocks work at once. Size: design.
  - Finish step 2 has no source for the gate's tags after a `/clear`, because the gate message is gone. Size:
    quick-fix.

## Questions

1. What did plan 80 set out to do, and why did the owner choose a separate history file over spec amendments?
2. How was it built: which parts came first, and why did the script commit wait for the reference?
3. What does the branch add to the project, and what does it leave for later?
