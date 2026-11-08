# Development history record Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give each project one append-only file, `specs/history.md`, that records what each completed plan built
and where the build differed from its design, and which deferred items each `/deferred` quick-fix pass closed.

**Architecture:** A new stdlib script, `skills/writing-plans/scripts/history_entry.py`, reads the sources (the plan,
the run's ledger, `specs/deferred_items.md`, `specs/history.md`) and prints a draft entry. It never writes a file. A
new reference, `skills/writing-plans/references/history.md`, holds the file's rules and the steps to finish a draft.
Protocol step 5 of writing-plans gets one pointer sentence, paid for by deleting step 3's example block, which
`references/deferred-backlog.md` already holds byte for byte. Both executors' gates tag a ruling that contradicts spec
text, and `/deferred` step 5 writes an entry for a pass that closes items with a quick fix. A small micro-test kit
checks the two rules that change what an agent chooses: the gate's tag and the ruling filter. This plan's own
completion writes the first entry of this repository's `specs/history.md`.

**Tech Stack:** Python 3.11+ stdlib (PEP 723 script), pytest through `build/run_suites.py`, Markdown skill and
command text, the runtime adapter generator, the `claude -p` micro-test kit.

**Spec:** `specs/development-history-record.md` (APPROVED 2026-11-08; decisions D1–D7)

## Global Constraints

- **Execution base.** `BASE80` is the commit that adds this plan. Task 1 Step 1 records its sha. Line numbers below
  were taken at `4d69454`. The old text in each step is the match key, not the line number.
- **One execution at a time.** No execution starts while another plan executes in this repository (owner ruling,
  2026-10-28).
- **A parallel session (brief T6).** The findings 21 and 24 session (branch `claude/admiring-curie-2vilnz`, draft
  spec `specs/spec-derived-acceptance-tests.md`) plans edits to `skills/writing-plans/SKILL.md` and to the gate
  paragraph of both executors' `references/final-review.md`, after a writing-plans references split. Before Task 1,
  and again before Tasks 4 and 5, run `git fetch origin main` and
  `git log --oneline <BASE80>..origin/main -- skills/writing-plans/SKILL.md skills/subagent-driven-development/references/final-review.md skills/executing-plans/references/final-review.md`.
  If it lists a commit, stop and tell your human partner before the task starts.
  The old text in each edit step is the match key.
  Never push to `claude/admiring-curie-2vilnz`.
- **The history file** (spec, The history file), exact: path `specs/history.md`; title line `# Development history`
  and no other preamble, created on first use; one `##` section for each completed plan and one for each `/deferred`
  pass that closes items, newest last; plan heading `## <plan-stem> — YYYY-MM-DD`, where `<plan-stem>` is the plan
  filename without `.md` and the date is the completion date; `/deferred` heading `## /deferred — YYYY-MM-DD`, the
  pass date. Append-only: no skill step edits or moves an earlier section.
- **Entry rules 1–7** are the spec's (Entry format, Rules), unchanged. Rule 3 is D7: an entry keeps only the rulings
  that changed the build against the spec or the plan. A ruling that declined a finding and kept the plan as written
  stays out.
- **Script CLI**, exact:
  `uv run <writing-plans>/scripts/history_entry.py draft <plan> [--ledger <path>] [--spec <path> --spec-status retired|live] [--date YYYY-MM-DD]`
  and `uv run <writing-plans>/scripts/history_entry.py deferred [--date YYYY-MM-DD]`. `--date` defaults to today.
  Exit 0 with a draft. `draft` exits 2 with a one-line error on stderr when the plan file is missing or not a plan.
  `deferred` prints nothing and exits 0 when no item qualifies. The script writes no file.
- **Script form.** PEP 723 header like `deferred_stats.py` (`requires-python = '>=3.11'`, `dependencies = []`),
  stdlib only, single quotes, 4-space indent. Import from `deferred_stats` (`parse_items`, `Item`, `NOTE_RE`) and
  `deferral_scan` (`blank_code`) as needed. Do not edit either module.
- **Tests.** In `skills/writing-plans/scripts/test_history_entry.py`, in the existing `writing-plans` suite of
  `build/suites.toml`. Bare imports. Fixtures are literal inline text in the test file, written to `tmp_path`. Tests
  never call `git show`. Run with `uv run python build/run_suites.py writing-plans`; its pytest summary line gives
  the counts.
- **Compaction window.** The writing-plans `SKILL.md` body stays at or below its base: 19,994 characters at
  `4d69454`, measured with
  `cd build && python3 -c "import check_conformance as c, pathlib; print(len(c.skill_body(pathlib.Path('../skills/writing-plans/SKILL.md').read_text())[0]))"`.
  Do not move `## What a Step Contains` (micro-tested exact copy from plan 73).
- **Canonical sources.** After the edit of `commands/deferred.md`, regenerate and check `runtimes/` with
  `uv run --with pyyaml python build/sync_runtime_assets.py` and then the same command with `--check`. Never
  hand-edit `runtimes/`.
- **Commit gate.** Before each commit, `bash build/run_commit_lints.sh` prints `commit lints passed`. Before a commit
  that changes a skill, a command or NOTICE, `uv run --with pyyaml python build/check_conformance.py` and
  `uv run python build/check_provenance.py` also pass. Commit messages follow Conventional Commits, use plain
  technical English and end with the attribution trailer that the executing session is given.
- **Deferral lint at retirement.** In this plan and in every file it adds, put note forms, marker forms and quoted
  deferral phrases inside backticks. This plan is a fixture of the lint when it retires.
- **Leave alone.** `skills/writing-plans/references/deferred-backlog.md`; `deferred_stats.py`, `deferral_scan.py`,
  `archive_deferred.py` and `entry_check.py`; `skills/writing-plans/SKILL.md` outside step 3's example block and the
  end of step 5; every retired plan and spec (no backfill, and the stale-pointer item of section
  `spec-drift-finding-22` stays open); the task-review surfaces of subagent-driven-development (findings 21 and 24);
  the backlog item `spec-reading-test-check`; the other session's branch `claude/admiring-curie-2vilnz`;
  `install.py`.
- **Micro-tests.** Kit at `specs/red-baseline-development-history/kit/`, record at
  `specs/red-baseline-development-history.md`. Every rep is a fresh
  `claude -p --model claude-opus-5-5 --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence --output-format json --max-budget-usd 1.00`
  under `env -i`, run by the kit's `run_reps.sh` from a new empty directory under `/tmp`. Five scored reps per case
  and arm. Texts are read with `git show` at a sha, never through `~/.claude/skills/`. Each pass rule is committed
  before any rep of its case runs, and no fixture or rule is edited after a rep output is seen. Every verdict is read
  by hand from the full reply. No kit file is named `test_*.py`.
- **Spend stop: $12** for the whole kit, summed from `total_cost_usd` over every `rep<N>.json` in the record folder
  (`show_reps.py` prints the total). If the control arms alone pass $5, stop and ask your human partner.

## Review Focus

1. **A plan that quotes the protocol's own forms in code.** This plan does it: fenced test fixtures hold
   `> Deviation:`, `### Task` and `- **D2**` lines, one fence inside a longer one. A person running `draft` on such a
   plan expects none of the quoted forms in the entry. Pinned in Task 2 (`test_quoted_forms_in_code_are_not_read`).
2. **Plan ids that share a prefix.** A `(plan 79)` tick must not count as closed by plan 7. Pinned in Task 2
   (`test_plan_id_matches_whole_word`).
3. **Decisions that wrap.** Real plans wrap a decision's `Applied in:` list onto indented lines, and
   `(spec amendment)` can break across them. The decision must still be found, with its whole text. Pinned in Task 2
   (the golden test's D2 fixture) and Task 7 Step 4 (plan 74's D18).
4. **Quoted note forms in item prose.** `specs/deferred_items.md` quotes tick forms in backticks. A quoted
   `→ done … (/deferred quick fix)` is not a close. Pinned in Task 3 (`test_quoted_quick_fix_form_is_not_a_close`).
5. **A second `/deferred` pass on the same date.** The person expects each closed item listed once across that date's
   sections, and no section when nothing new closed, even after the first section's note text was shortened.
   Pinned in Task 3 (`test_second_pass_same_date_lists_only_new_items`, `test_all_listed_prints_nothing`).

## Decisions

Numbered after the spec's D1–D7. The brief records no decision after D7.

- **D8** (owner, plan review, 2026-11-08): approve the plan as written, including the planner's calls in Open for
  plan review items 1–12. Applied in: Open for plan review.

## Open for plan review

All twelve items are settled: approved as written by D8 (2026-11-08).

1. **The brief came by relay.** It was not in this container. The findings 21 and 24 session relayed its text on
   2026-11-08. It has no decisions and no owner gates. Its leave-alone list is in Global Constraints. Its traps
   T1–T6 are applied: T1 in Task 4 Steps 1 and 4, T2 and T4 in Task 2's fixtures, T3 in Task 4 Step 2, T5 in
   Task 6 Step 2, T6 in Global Constraints. Its two defaults are items 10 and 11 below.
   The brief file is not saved in this container.
   Say if you want it kept.
2. **The cut that pays for the pointer.** Task 4 deletes step 3's example block (509 characters plus one blank line).
   It is byte-identical to the example under **Deferred-item schema** in `references/deferred-backlog.md`, to which
   step 3 already points. Net body change: about −330 characters.
3. **The pointer's place.** The last sentence of step 5, after the `git mv` and the spec decision, so the draft gets
   the plan's and the spec's final paths (spec, Left to the builder).
4. **Titles are verbatim.** A closed item's title is its first line with notes cut, exactly as the script prints it.
   The agent never edits the quoted title or its `(deferred by …)` part, because the second-pass check matches on
   them. The spec's example shows a shortened title.
5. **Warning lines.** The draft prints `Rulings: no ledger given` (spec) and `Spec: --spec not given` (when the
   plan's header names a spec and `--spec` is absent) on their own lines after the `Plan:` line. The agent resolves
   and deletes each one before appending. `--spec` and `--spec-status` come together, or `draft` exits 2.
6. **Only ticked items count as closed.** An unticked item with a `→ done` note stays out (the checkbox decides, as
   in `deferred_stats.py`).
7. **A deviation above the first `### Task` heading** is printed as `- Deviation: <text>. Source: plan, header.`
8. **Micro-tests: two cases, Opus 5.5, $12 stop.** House practice since plan 76 (its D1) micro-tests only the wording
   that changes what an agent chooses. Here that is the gate's `contradicts spec` tag and rule 3's ruling filter.
   Every other text change gets a mechanical failing check. The alternative is mechanical checks only (drop Tasks 1
   and 7's reps). Recommended: keep the two cases.
9. **A README bullet.** Task 6 adds `specs/history.md` to the README's list of the files the lifecycle skills create,
   since D3 says the record serves any project that uses these skills.
10. **Brief F1: the source of a closed item is its section's slug.** The slug is the section name up to the first
    ` (`, so `## deferred-triage (no plan; /deferred pass, branch …) — 2026-09-28` gives `deferred-triage`, and a
    plan section gives its plan stem. The spec's rule 6 says only "the section it came from". The other choice is the
    full heading, which a reader can search for. Pinned in Task 3 (`test_deferred_draft`).
11. **Brief F2: this plan writes the first entry.** Its own completion runs the new step and creates this
    repository's `specs/history.md` (Architecture). The other choice starts the history with the next plan.
12. **Order against the references split.** The findings 21 and 24 work waits for a writing-plans references split,
    which may move protocol text out of `SKILL.md`. Task 4 cuts only step 3's example block. If plan 80 lands first,
    the split starts from it. The owner orders the plans.

---

### Task 1: Micro-test kit and control arms

**Files:**
- Create: `specs/red-baseline-development-history/kit/{run_reps.sh,isolation_probe.txt,show_reps.py,build_prompts.py,cases.py}`
- Create: `specs/red-baseline-development-history.md`
- Create: `specs/red-baseline-development-history/control/<case>/rep<N>.json` (rep output)

**Interfaces:**
- Produces: `cases.CASES` with keys `gate-tag` and `history-filter`; the record's `## Control` section; `BASE80`
  recorded in the record's `## Base` section. Task 7 runs the treatment arms with the same kit.

- [ ] **Step 1: Record the base**

Run: `git rev-parse --short HEAD`. Write it into the record's `## Base` section as `BASE80`.

- [ ] **Step 2: Copy plan 77's kit**

Copy `run_reps.sh`, `isolation_probe.txt`, `show_reps.py` and `build_prompts.py` from
`specs/red-baseline-audit-p2/kit/`. Change only the plan number in comments and docstrings (77 → 80), the temp
prefix (`/tmp/plan77-rep-` → `/tmp/plan80-rep-`), and `show_reps.py`'s `AIDS` to flag `contradicts spec`,
`Ruling`, `history` and `\?` (a question mark). `isolation_probe.txt` stays unchanged.

- [ ] **Step 3: Write `cases.py`**

Same shape as `specs/red-baseline-review-fixes/kit/cases.py` (`case(texts, fixture, task, pass_rule, leak, bar)`,
`CASES`, a shared `VOID` string copied from it), with `MODEL = 'claude-opus-5-5'` and `BUDGET = '1.00'`. The bar for
both cases is `'treatment 5/5; control fails at least 1 of 5'`. Fixtures, tasks, rules and leak patterns, exact:

`gate-tag`, texts `['skills/subagent-driven-development/references/final-review.md']`:

```text
Today is 2026-11-09. The repo is a bike-share dock-status service; the branch is `feat/dock-alerts`. You are the controller of a subagent-driven run of `specs/plans/12-dock-alerts.md`, which implements `specs/dock-alerts.md`.

[you, tools] All four tasks are complete and reviewed. The final whole-branch review came back clean, with one Declined to judge line: "Whether email is the right channel for alerts sent at night."
[you, tools] Read the spec. Its sections, in full:
- § 1 Scope: the service alerts the operations team about docks that are nearly full.
- § 2 Alert threshold: a dock alerts when it has 2 or fewer free slots.
- § 3 Alert channel: alerts go out by email, one email per alert.
[you, tools] Read the plan. Task 3 creates `alerts/send.py` with `send_alert(dock_id: str) -> None`.
[you, tools] The ledger, `.sdd/12-dock-alerts/progress.md`, in full:
Plan: specs/plans/12-dock-alerts.md
Task 1: complete (commits 3f1a2b7..8c9d0e1, review clean)
Task 2: Ruling: alert at 3 or fewer free slots, not 2 or fewer — docks refill more slowly than the design assumed, so 2 free slots leaves riders no warning — the team gets about one extra alert a day if wrong.
Task 2: complete (commits 8c9d0e1..a4b5c6d, review clean)
Task 3: Ruling: the module is `alerts/notify.py`, not `alerts/send.py` — `send` shadows the socket helper the service already imports — one import path changes if wrong.
Task 3: Ruling: declined the reviewer's request to batch alerts into one email — the plan sends one email per alert as written — more email than needed if wrong.
Task 3: complete (commits a4b5c6d..e7f8a9b, review clean)
Task 4: complete (commits e7f8a9b..0b1c2d3, review clean)
Final: Ruling: the retry-jitter finding stays out — the tests seed the jitter on purpose — one flaky test if wrong.
[you, tools] Nothing from the plan was skipped. No review finding is unfixed.
```

Task: `It is your turn. You have no tools in this turn. You are at the plan-completion protocol's gate. Write the message you send your partner, exactly as you send it, and nothing else.`

Pass rule: `PASS = the message lists all four rulings; the Task 2 ruling's entry contains the literal text "contradicts spec" followed by "§ 2" or "Alert threshold"; no other ruling's entry contains "contradicts spec"; and no ruling is put to the partner as a question to approve. FAIL = any of these does not hold.`

Leak: `r'contradicts spec|spec section|changed the build'`.

`history-filter`, texts `['skills/writing-plans/SKILL.md', 'skills/writing-plans/references/histor*.md']` (the glob
matches nothing at `BASE80`):

```text
Today is 2026-11-09. The repo is a bike-share dock-status service; the branch is `feat/dock-alerts`. You are the controller of a subagent-driven run of `specs/plans/12-dock-alerts.md`, which implements `specs/dock-alerts.md`. All four tasks are complete, and you are running the plan-completion protocol.

[you, tools] At the gate you sent your partner this list of the ledger's rulings, as decisions already taken:
1. Task 2: alert at 3 or fewer free slots, not 2 or fewer — docks refill more slowly than the design assumed, so 2 free slots leaves riders no warning — the team gets about one extra alert a day if wrong. contradicts spec: § 2 Alert threshold
2. Task 3: the module is `alerts/notify.py`, not `alerts/send.py` — `send` shadows the socket helper the service already imports — one import path changes if wrong.
3. Task 3: declined the reviewer's request to batch alerts into one email — the plan sends one email per alert as written — more email than needed if wrong.
4. Final review: the retry-jitter finding stays out — the tests seed the jitter on purpose — one flaky test if wrong.
[partner] All four stand. No reverts.
[you, tools] Steps 2 to 4 are done: the plan is marked up, nothing was deferred, and step 3 ticked one earlier item, "Dock status cache ignores the time zone", in section `9-dock-status`, with `→ done 2026-11-09 (plan 12)`.
[you, tools] Step 5: the deferral scan listed no lines. `git mv` moved the plan to `specs/plans/completed/12-dock-alerts.md`. No other live plan implements the spec, so it moved to `specs/completed/dock-alerts.md`, marked complete.
[you, tools] Ran `uv run ~/.claude/skills/writing-plans/scripts/history_entry.py draft specs/plans/completed/12-dock-alerts.md --ledger .sdd/12-dock-alerts/progress.md --spec specs/completed/dock-alerts.md --spec-status retired --date 2026-11-09`. It printed:
## 12-dock-alerts — 2026-11-09
Plan: specs/plans/completed/12-dock-alerts.md · Spec: specs/completed/dock-alerts.md (retired)

Differences from the design:
- Ruling (Task 2): alert at 3 or fewer free slots, not 2 or fewer — docks refill more slowly than the design assumed, so 2 free slots leaves riders no warning — the team gets about one extra alert a day if wrong.
- Ruling (Task 3): the module is `alerts/notify.py`, not `alerts/send.py` — `send` shadows the socket helper the service already imports — one import path changes if wrong.
- Ruling (Task 3): declined the reviewer's request to batch alerts into one email — the plan sends one email per alert as written — more email than needed if wrong.
- Ruling (final review): the retry-jitter finding stays out — the tests seed the jitter on purpose — one flaky test if wrong.
- Deviation (Task 1): the dock list loads from the city feed's v2 endpoint, because v1 was retired in October. Source: plan, Task 1.

Closed earlier deferred items:
- "Dock status cache ignores the time zone" (deferred by 9-dock-status).
```

Task: `It is your turn. You have no tools in this turn. Write the exact text you append to specs/history.md, and nothing else.`

Pass rule: `PASS = the entry keeps the Task 2 ruling labelled "Ruling, contradicts spec (Task 2)" and the module-name ruling labelled "Ruling (Task 3)", each with its what, why and cost parts all present; it leaves out the batch-email ruling and the retry-jitter ruling; it keeps the Deviation line (shortened or not) with a Source pointer, and the closed-item line with its quoted title and "(deferred by 9-dock-status)" unchanged; and the heading and Plan line are unchanged. FAIL = any of these does not hold.`

Leak: `r'changed the build|kept the plan as written|rule 3|parks? a finding'`.

- [ ] **Step 4: Write the record and register the rules**

Sections, in this order: `## Base` (`BASE80`), `## Kit` (what was copied from where and what changed), `## Arms`
(control: texts at `BASE80`; treatment: texts at Task 5's last commit, `T5`), `## Bars`, `## Spend stop`,
`## Stop rule`, `## Leak check`, `## Reading rules` (the VOID rule and both pass rules, copied from `cases.py`).
Stop rule, exact: `A case whose control fails 0 of 5 has nothing to fix in wording. Record it and put it to the owner
in the completion gate's batch. The spec-required wording still lands.`

- [ ] **Step 5: Run the leak check**

Run: `uv run python specs/red-baseline-development-history/kit/build_prompts.py leakview /tmp/plan80-work/leak`,
then `grep -nE` each case's leak pattern over its leak-view prompt.
Expected: no hit, except `contradicts spec` in the `history-filter` fixture (the gate's list, shown on purpose).
Record each hit and why it stands in `## Leak check`.

- [ ] **Step 6: Commit the registration**

```bash
git add specs/red-baseline-development-history specs/red-baseline-development-history.md
git commit -m "test(specs): register the development-history micro-tests"
```

- [ ] **Step 7: Run the isolation probe**

Run: `bash specs/red-baseline-development-history/kit/run_reps.sh specs/red-baseline-development-history/kit/isolation_probe.txt /tmp/plan80-work/probe 1 1 claude-opus-5-5`
Expected: all five probe lines read `NO`. Record the Claude Code version and the result in `## Isolation probe`. Any
`YES`: stop and ask your human partner.

- [ ] **Step 8: Build the control prompts and run the control arms**

Run: `uv run python specs/red-baseline-development-history/kit/build_prompts.py <BASE80> /tmp/plan80-work/control`,
then for each case
`bash specs/red-baseline-development-history/kit/run_reps.sh /tmp/plan80-work/control/<case>.txt specs/red-baseline-development-history/control/<case> 1 5 claude-opus-5-5 1.00`.
Expected: 10 reps; rerun VOID reps with the next free number, inside the spend stop.

- [ ] **Step 9: Read and record the control verdicts**

Run: `uv run python specs/red-baseline-development-history/kit/show_reps.py specs/red-baseline-development-history/control/<case>`
for each case. Read every reply in full. Write `## Control` with one verdict line per scored rep (`rep<N>: PASS|FAIL —
<reason>`), the fail count per case, and the spend so far.
Expected: each case fails at least 1 of 5. If not, apply the stop rule.

- [ ] **Step 10: Commit the control arm**

```bash
git add specs/red-baseline-development-history specs/red-baseline-development-history.md
git commit -m "test(specs): run the development-history control arms"
```

### Task 2: `history_entry.py draft`

**Files:**
- Create: `skills/writing-plans/scripts/history_entry.py`
- Create: `skills/writing-plans/scripts/test_history_entry.py`
- Modify: `build/suites.toml:166` (the `writing-plans` suite's notes)

**Interfaces:**
- Consumes: `deferred_stats.parse_items(text: str) -> list[Item]`, `Item.section`, `Item.checked`, `Item.text`,
  `Item.notes` (`Note.kind`, `Note.date`, `Note.rest`); `deferral_scan.blank_code(text: str) -> str`.
- Produces: `main(argv: list[str] | None = None) -> int` with the `draft` subcommand. Task 3 adds the `deferred`
  subcommand to the same parser, and reuses the closed-item line form `- "<title>" (deferred by <section>)`.

- [ ] **Step 1: Write the failing tests**

All tests build a throwaway repo under `tmp_path`: the plan at `specs/plans/completed/<stem>.md`, the backlog at
`specs/deferred_items.md`, and the ledger anywhere. They call `main([...])` and read `capsys`. Fixtures, exact:

````python
PLAN = '''# Rate Limiter Implementation Plan

**Spec:** `specs/rate-limiter.md`

> Roadmap: specs/edge-roadmap.md, Stage 2 — on plan completion, tick the stage and re-validate later stages against what shipped.

## Decisions

- **D1** (owner, plan review, 2026-07-01): keep the per-IP bucket size. Applied in: Task 2.
- **D2** (owner, plan review, 2026-07-01): the 429 body is JSON. Applied in: Task 1 (spec
  amendment), Task 3.

---

### Task 1: Store

- [x] **Step 1: Write the failing test**

> Deviation: the store reads the limit from config, not from a constant.

### Task 2: Middleware

- [x] **Step 1: Run it**

  > Deviation (two, from review): `X-RateLimit` headers are lower-case.
'''

LEDGER = '''Plan: specs/plans/7-rate-limiter.md
Task 1: complete (commits a1b2c3d..d4e5f6a, review clean)
Task 3: Ruling: count requests per key, not per IP — the spec's per-IP rule breaks behind the proxy — clients behind one NAT share a key if wrong.
Ruling: returned 503, not the plan's 429, when the store is down — a 429 tells clients to back off from a fault that is ours — clients retry at once if wrong.
Final: Ruling: the jitter finding stays out — tests seed jitter on purpose — a flaky test if wrong.
'''

BACKLOG = '''# Deferred items

## 5-http-client — 2026-06-01
- [x] Retry jitter is fixed-seed in tests only
      (final review). Size: quick-fix. → done 2026-07-04 (plan 7)
- [x] Older tick form → done in plan 7 (D)
- [x] Belongs to another plan → done 2026-07-04 (plan 79)
- [ ] Open item with a note → done 2026-07-04 (plan 7)
- [x] Prose that quotes `→ done 2026-07-04 (plan 7)` only → retired 2026-07-04: gone.

## 7-rate-limiter — 2026-07-04
- [ ] Redis-backed counter store. Size: design. Done when: the DSN is recorded.
- [ ] Second deferred thing. Size: quick-fix. Done when: it lands.
'''
````

Tests and assertions:

- `test_golden_draft`: `draft <root>/specs/plans/completed/7-rate-limiter.md --ledger <ledger> --spec specs/completed/rate-limiter.md --spec-status retired --date 2026-07-04` returns 0 and prints exactly:

```text
## 7-rate-limiter — 2026-07-04
Plan: specs/plans/completed/7-rate-limiter.md · Spec: specs/completed/rate-limiter.md (retired) · Roadmap: specs/edge-roadmap.md, Stage 2

Differences from the design:
- Ruling (Task 3): count requests per key, not per IP — the spec's per-IP rule breaks behind the proxy — clients behind one NAT share a key if wrong.
- Ruling: returned 503, not the plan's 429, when the store is down — a 429 tells clients to back off from a fault that is ours — clients retry at once if wrong.
- Ruling (final review): the jitter finding stays out — tests seed jitter on purpose — a flaky test if wrong.
- Deviation (Task 1): the store reads the limit from config, not from a constant. Source: plan, Task 1.
- Deviation (Task 2): `X-RateLimit` headers are lower-case. Source: plan, Task 2.
- Decision D2 (spec amendment): the 429 body is JSON. Source: plan, `## Decisions`.
- Deferred: 2 items. Source: specs/deferred_items.md, § 7-rate-limiter.

Closed earlier deferred items:
- "Retry jitter is fixed-seed in tests only" (deferred by 5-http-client).
- "Older tick form" (deferred by 5-http-client).
```

- `test_no_ledger_and_spec_none`: a plan `9-tiny` whose header is `**Spec:** none. The requirement is one item.`,
  with one `### Task 1` and no notes, and a backlog section `## 9-tiny — 2026-07-04` with one item; `draft` with no
  `--ledger` and no `--spec` prints, line for line:
  `## 9-tiny — 2026-07-04`, `Plan: specs/plans/completed/9-tiny.md · Spec: none`, `Rulings: no ledger given`, ``,
  `Differences from the design:`, `- Deferred: 1 item. Source: specs/deferred_items.md, § 9-tiny.`
- `test_header_spec_without_flag_warns`: `PLAN` with `--ledger` and no `--spec`: the second line ends
  `· Spec: specs/rate-limiter.md (status not given) · Roadmap: specs/edge-roadmap.md, Stage 2`, and the next line
  is `Spec: --spec not given`.
- `test_no_differences`: plan `9-tiny` as above, no backlog file, a ledger with no `Ruling:` line: output is
  `## 9-tiny — 2026-07-04`, `Plan: specs/plans/completed/9-tiny.md · Spec: none`, ``,
  `No differences from the design.`
- `test_header_deviation`: a `> Deviation: the plan ran on main.` line above the first `### Task` heading prints
  `- Deviation: the plan ran on main. Source: plan, header.`
- `test_quoted_forms_in_code_are_not_read`: `PLAN` plus a block opened by four backticks that holds a
  three-backtick fence and, inside both, the lines `> Deviation: quoted.`, `### Task 9: Quoted` and
  `- **D9** (owner, plan review, 2026-07-01): quoted. Applied in: Task 9 (spec amendment).`, plus a prose line
  `` Add a one-line `> Deviation: …` note. `` The output equals `test_golden_draft`'s.
- `test_plan_id_matches_whole_word`: in `test_golden_draft`'s output, no line names `Belongs to another plan`.
- `test_unticked_and_quoted_ticks_are_not_closes`: no line names `Open item with a note` or `Prose that quotes`.
- `test_missing_plan_exits_2` and `test_not_a_plan_exits_2` (a file with no `### Task` heading outside code): `main`
  returns 2, stdout is empty, and stderr is one line that names the path.
- `test_spec_without_status_exits_2`: `--spec specs/x.md` alone returns 2 with a one-line error.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run python build/run_suites.py writing-plans -- test_history_entry.py`
Expected: collection error — `ModuleNotFoundError: No module named 'history_entry'`.

- [ ] **Step 3: Implement `main(argv: list[str] | None = None) -> int` with `draft` in `history_entry.py`**

Rules the tests do not fully fix:
- Repo root: the parent of the plan's nearest ancestor directory named `specs`. None: exit 2, not a plan. The
  `Plan:` path is the plan's path relative to that root, in posix form. `--spec` is printed as given.
- Header lines (`**Spec:**`, the `Roadmap:` line after any `> `) are read only above the first `## ` heading. A
  `**Spec:**` value that starts with `none` gives `Spec: none`. Otherwise the first `specs/…md` path in it is the
  header spec.
- Code: decide every match on the lines of `blank_code(text)` (fences and inline spans blanked, line count kept), and
  take the printed text from the original line. So a form inside code never matches.
- A deviation is a line `^\s*>\s*(\*\*)?Deviation\b[^:]*:`. Its text is what follows that colon, stripped, with one
  trailing `.` removed before `. Source: …` is added. Its task is the `### Task <N>` heading above it.
- A decision is a `- **D<n>**` bullet plus its indented continuation lines, joined with single spaces. It qualifies
  when its `Applied in:` part contains `(spec amendment)`. Its text runs from after the `): ` that closes the
  parenthesis to before ` Applied in:`, with one trailing `.` removed.
- A ruling is any ledger line containing `Ruling:`; its text is everything after the first `Ruling:`, stripped. A line
  that starts `Task <N>` labels it `(Task <N>)`; one that starts `Final` labels it `(final review)`.
- Plan id: the stem's leading digits before `-`. Closed items: ticked items with a `done` note whose `rest` matches
  `(?<![\w-])plan\s+#?<id>(?![\w-])`. Title: the item's first line with every note span cut, whitespace collapsed.
  Source: the item's section name up to the first ` (` (brief F1).
  No id, or no backlog file: no closed items and no `Deferred:` line.
- `Deferred:` counts every item in the section named exactly `<plan-stem>`; `1 item`, otherwise `<n> items`.
- Warning lines follow the `Plan:` line, `Spec: --spec not given` first, then `Rulings: no ledger given`.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run python build/run_suites.py writing-plans`
Expected: PASS, with every earlier writing-plans test still passing.

- [ ] **Step 5: Update the suite note**

In `build/suites.toml`, the `writing-plans` notes become
`'Deferred-backlog stats, deferral scan, history-entry and entry-check tests (stdlib only; the entry-check tests build throwaway git repos).'`
Run: `uv run python build/run_suites.py --check`. Expected: exit 0.

- [ ] **Step 6: Commit**

```bash
git add skills/writing-plans/scripts/history_entry.py skills/writing-plans/scripts/test_history_entry.py build/suites.toml
git commit -m "feat(writing-plans): draft a plan's history entry"
```

### Task 3: `history_entry.py deferred`

**Files:**
- Modify: `skills/writing-plans/scripts/history_entry.py`
- Modify: `skills/writing-plans/scripts/test_history_entry.py`

**Interfaces:**
- Consumes: Task 2's parser and its closed-item line form `- "<title>" (deferred by <section>)`.
- Produces: the `deferred` subcommand. It reads `specs/deferred_items.md` and `specs/history.md` relative to the
  current directory (tests `monkeypatch.chdir(tmp_path)`).

- [ ] **Step 1: Write the failing tests**

Fixtures, exact:

````python
QUICK = '''# Deferred items

## 34-calibration — 2026-09-20
- [x] The spread step is direction-blind
      (final review). → done 2026-10-05 (/deferred quick fix): signed the spread
      and added a test.
- [x] Quoted form only: `→ done 2026-10-05 (/deferred quick fix)` here
      → retired 2026-10-05: the premise is gone.
- [x] Fixed on another day → done 2026-10-04 (/deferred quick fix): moved the guard.
- [x] No note text → done 2026-10-05 (/deferred quick fix)
- [ ] Open, not closed → done 2026-10-05 (/deferred quick fix): typo.

## deferred-triage (no plan; /deferred pass, branch deferred-triage-2026-09-28) — 2026-09-28
- [x] Brief path is relative → done 2026-10-05 (/deferred quick fix): made it absolute.
'''

HISTORY = '''# Development history

## /deferred — 2026-10-04

Closed deferred items:
- "Brief path is relative" (deferred by deferred-triage): an older close.

## /deferred — 2026-10-05

Closed deferred items:
- "The spread step is direction-blind" (deferred by 34-calibration): signed it.
'''
````

Tests and assertions:

- `test_deferred_draft`: with `QUICK` and no history file, `deferred --date 2026-10-05` returns 0 and prints exactly:

```text
## /deferred — 2026-10-05

Closed deferred items:
- "The spread step is direction-blind" (deferred by 34-calibration): signed the spread and added a test.
- "No note text" (deferred by 34-calibration).
- "Brief path is relative" (deferred by deferred-triage): made it absolute.
```

  The last line pins brief F1: a section with no plan is named by its slug.

- `test_quoted_quick_fix_form_is_not_a_close`: in that output, no line names `Quoted form only`, `Fixed on another
  day` or `Open, not closed`.
- `test_second_pass_same_date_lists_only_new_items`: with `HISTORY` present, the output lists only the `No note text`
  and `Brief path is relative` lines. The 2026-10-04 section does not hide the 2026-10-05 close.
- `test_all_listed_prints_nothing`: `HISTORY` plus those two lines under a second `## /deferred — 2026-10-05`
  section: stdout is empty and `main` returns 0.
- `test_no_backlog_prints_nothing`: no `specs/deferred_items.md`: stdout is empty, exit 0.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run python build/run_suites.py writing-plans -- test_history_entry.py`
Expected: the five new tests FAIL with `SystemExit: 2` (argparse: `invalid choice: 'deferred'`); Task 2's tests pass.

- [ ] **Step 3: Implement the `deferred` subcommand in `history_entry.py`**

An item qualifies when it is ticked and has a `done` note dated `--date` whose `rest` starts with
`(/deferred quick fix)`. Its note text is what follows that prefix and one `:`, through the note's continuation lines
up to the next note or the item's end, joined with single spaces. An item is already listed when a line in an earlier
`## /deferred — <date>` section of `specs/history.md` starts with its `- "<title>" (deferred by <section>)` prefix.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run python build/run_suites.py writing-plans`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/writing-plans/scripts/history_entry.py skills/writing-plans/scripts/test_history_entry.py
git commit -m "feat(writing-plans): draft a /deferred pass's history entry"
```

### Task 4: The history reference and the step 5 pointer

**Files:**
- Create: `skills/writing-plans/references/history.md`
- Modify: `skills/writing-plans/SKILL.md:328-338` (step 3's example block) and `:405-406` (the end of step 5)

**Interfaces:**
- Consumes: Tasks 2–3's CLI and output forms; the spec's sections The history file, Entry format, `/deferred`
  entries, The script and Protocol step.
- Produces: `references/history.md` with the headings `## The history file`, `## Plan entries`,
  `## /deferred entries` and `## The script`, which Task 6's command text and Task 7's micro-test read.

- [ ] **Step 1: Write the failing check**

Run: `grep -c 'history_entry.py' skills/writing-plans/SKILL.md; test -f skills/writing-plans/references/history.md`
Expected: `0`, and `test` exits 1.
Run: the Global Constraints' body measure, and record the figure as the before value (brief T1).
Expected: 19,994, unless a rebase changed the file.

- [ ] **Step 2: Write `references/history.md`**

Agent-facing. Title `# Development history reference`, then one paragraph: what `specs/history.md` records, and its
two writers (Protocol step 5 and `/deferred` step 5). Then:
- `## The history file`: the Global Constraints' history-file line, as rules.
- `## Plan entries`: when (step 5, after the `git mv` and the spec decision, before the retire commit; the executor
  deletes its workspace only after the protocol, so the ledger is readable); the command
  `uv run <this-skill-dir>/scripts/history_entry.py draft specs/plans/completed/<file> --ledger <workspace>/progress.md --spec <final spec path> --spec-status retired|live`,
  where `<workspace>` is the executor's `.sdd/<plan-basename>/` directory, `--spec` and `--spec-status` are left out
  for a plan whose header reads `**Spec:** none`, and `--ledger` is left out only when the run kept no ledger; the
  spec's entry-format example, copied unchanged; rules 1–7, copied from the spec with their designer's-call marks
  and rule 6's last sentence (about `SKILL.md` step 3) dropped; then a numbered list, **Finish the draft**:
  1. Delete each ruling that did not change what got built against the spec or the plan: one that declined a finding
     and kept the plan as written, or one that parked a finding with no change to the build.
  2. Relabel each ruling that the gate listed with `contradicts spec: <spec section>` as `Ruling, contradicts spec`,
     keeping its bracketed task.
  3. Keep each remaining ruling's text whole.
  4. Shorten each `Deviation` and `Decision` line to one short line, and keep its `Source:` pointer.
  5. Never edit a quoted title or its `(deferred by …)` part.
  6. Resolve and delete each warning line: `Rulings: no ledger given`, `Spec: --spec not given`.
  7. Delete a list heading whose list is now empty. When both lists are gone, the body after the `Plan:` line is
     `No differences from the design.`
  8. Create `specs/history.md` with its title line when it is absent, append the entry after one blank line, and
     stage the file into the `chore(specs): retire plan <id>` commit.
- `## /deferred entries`: when (step 5 of `/deferred`, before the closing `archive_deferred.py` run, when the pass
  ticked at least one item with `→ done <YYYY-MM-DD> (/deferred quick fix)`; a pass that only retires, holds, plans
  or designs writes none); the command `uv run <this-skill-dir>/scripts/history_entry.py deferred`; the spec's
  `/deferred` example, copied unchanged; finishing (shorten the text after `:` only, never the title or
  `(deferred by …)`; no output means no entry); the entry goes into the pass's commit.
- `## The script`: it writes no file, so a wrong draft never lands unread; the exit codes; `--date` defaults to
  today.

All note forms in backticks. Every link resolves from `references/`.

- [ ] **Step 3: Cut step 3's example and add the step 5 pointer in `SKILL.md`**

Delete the block from the line `` ```markdown `` through its closing `` ``` `` that holds
`## 7-rate-limiter — 2026-07-04` in step 3, and one of the two blank lines around it. Then, after the step 5
sentence that ends ``(`../skills/…` becomes `../../skills/…`).``, add, exactly:

```markdown
Before the `chore(specs): retire plan <id>` commit, draft this plan's
history entry with `scripts/history_entry.py`, finish it and append it to
`specs/history.md` in that commit (`references/history.md`).
```

- [ ] **Step 4: Run the checks**

Run: Step 1's check. Expected: `1`, and `test` exits 0.
Run: the Global Constraints' body measure. Expected: at or below Step 1's before value. Put both figures in the
task report.
Run: `uv run python build/check_links.py` and `uv run python build/check_snippets.py skills/`. Expected: both pass.
Run: `uv run --with pyyaml python build/check_conformance.py`. Expected: no finding for `skills/writing-plans/`.
Run: `cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies`.
Expected: PASS (a skill's own `references/` and `scripts/` are no new dependency).

- [ ] **Step 5: Commit**

```bash
git add skills/writing-plans/references/history.md skills/writing-plans/SKILL.md
git commit -m "feat(writing-plans): write a history entry at plan retirement"
```

### Task 5: The gate tags rulings that contradict spec text

**Files:**
- Modify: `skills/subagent-driven-development/references/final-review.md:36`
- Modify: `skills/executing-plans/references/final-review.md:79`

**Interfaces:**
- Produces: the gate tag form `contradicts spec: <spec section>`, which `references/history.md` (Task 4) reads.
- Task 7's treatment arms read both files at this task's last commit, `T5`.

- [ ] **Step 1: Write the failing check**

Run: `grep -c 'contradicts spec: <spec section>' skills/subagent-driven-development/references/final-review.md skills/executing-plans/references/final-review.md`
Expected: `0` for each file.

- [ ] **Step 2: Edit both gate paragraphs**

In each file, replace `each with what it costs if wrong —` with
``each with what it costs if wrong, and tag each one that contradicts spec text `contradicts spec: <spec section>` —``.
Rewrap the paragraph at its current width. Change nothing else.

- [ ] **Step 3: Run the check**

Run: Step 1's command. Expected: `1` for each file.
Run: `uv run --with pyyaml python build/check_conformance.py` and `uv run python build/check_reviewer_block.py`.
Expected: both pass.

- [ ] **Step 4: Commit and record `T5`**

```bash
git add skills/subagent-driven-development/references/final-review.md skills/executing-plans/references/final-review.md
git commit -m "feat(executors): tag gate rulings that contradict the spec"
```

Run: `git rev-parse --short HEAD`. Note it as `T5`. Task 7 writes it into the record's `## Arms` section.

### Task 6: `/deferred` writes its entry; NOTICE and README

**Files:**
- Modify: `commands/deferred.md` (step 5, the archive paragraph at the end)
- Modify: `runtimes/` (generated)
- Modify: `NOTICE` (after the plan 74 paragraph, which ends `Step 4b, Options 1 and 2 and Red Flags name the note on the item.`)
- Modify: `README.md:19` (the lifecycle file list)

**Interfaces:**
- Consumes: Task 3's `deferred` subcommand and Task 4's `## /deferred entries`.

- [ ] **Step 1: Write the failing check**

Run: `grep -c 'history_entry.py deferred' commands/deferred.md; grep -c 'history_entry.py' NOTICE; grep -c 'specs/history.md' README.md`
Expected: `0`, `0`, `0`.

- [ ] **Step 2: Edit `commands/deferred.md` step 5**

Before the paragraph that starts `End the pass by running the writing-plans skill's`, add, exactly, at the same
indent:

```markdown
   When the pass ticked at least one item `→ done <YYYY-MM-DD> (/deferred quick fix)`,
   run the writing-plans skill's `scripts/history_entry.py deferred` with `uv run`
   before the archive run. Finish its draft and append it to `specs/history.md`, as
   that skill's `references/history.md` says. No output means no entry.
```

In the archive paragraph, replace `Commit both files with the pass's other edits.` with
``Commit both files, and `specs/history.md` when the pass wrote an entry, with the pass's other edits.``

- [ ] **Step 3: Regenerate the adapters**

Run: `uv run --with pyyaml python build/sync_runtime_assets.py`, then the same with `--check`.
Expected: `runtimes/gemini/commands/deferred.toml` changes; `--check` exits 0.

- [ ] **Step 4: Add the NOTICE paragraph**

Plain technical English, at the change list's indent, exactly:

```text
    Plan 80 added a development history record, which is not upstream:
    writing-plans/references/history.md (the file specs/history.md, its
    entry format and its rules) and writing-plans/scripts/history_entry.py,
    which drafts each entry, with its tests
    (writing-plans/scripts/test_history_entry.py). These three files are
    original works by Lowell Mason under the same MIT terms. In the adapted
    skills, step 5 of writing-plans' Plan Completion Protocol appends a
    history entry before the retire commit. Step 3 no longer has its
    example block, which the deferred-backlog reference already holds. The
    plan-completion gate in subagent-driven-development and executing-plans
    tags each ruling that contradicts spec text. The /deferred command
    writes a history entry for a pass that closes items with a quick fix.
```

- [ ] **Step 5: Add the README bullet**

After the README line that ends ``appended to `specs/deferred_items.md` ``, add this line, exactly:

```markdown
>   - a short history of what each plan built and where it differed from its design, appended to `specs/history.md`
```

- [ ] **Step 6: Run the checks**

Run: Step 1's command. Expected: `1`, `1`, `1`.
Run: `uv run python build/check_provenance.py`,
`uv run --with pyyaml python build/check_conformance.py` and
`cd build && uv run --with pytest --with pyyaml python -m pytest -q test_runtime_support.py`.
Expected: all pass.

- [ ] **Step 7: Commit**

```bash
git add commands/deferred.md runtimes NOTICE README.md
git commit -m "feat(deferred): write a history entry for quick-fix passes"
```

### Task 7: Treatment arms and the real-data check

**Files:**
- Modify: `specs/red-baseline-development-history.md`
- Create: `specs/red-baseline-development-history/treatment/<case>/rep<N>.json`

**Interfaces:**
- Consumes: Task 1's kit and record; `T5` (Task 5); Tasks 2–3's script.

- [ ] **Step 1: Build the treatment prompts and run the treatment arms**

Write `T5` into the record's `## Arms` section.
Run: `uv run python specs/red-baseline-development-history/kit/build_prompts.py <T5> /tmp/plan80-work/treatment`,
then `run_reps.sh` for each case into `specs/red-baseline-development-history/treatment/<case>`, reps 1–5, as in
Task 1 Step 8. Check the spend stop before each batch.

- [ ] **Step 2: Read and record the verdicts**

As Task 1 Step 9, under `## Treatment`, with the bar result per case.
Expected: each case 5/5. A case below its bar gets one wording round in its text under test, in its own commit, and
5 new reps under `treatment2/<case>` at that commit. A `gate-tag` round edits both executor files the same way. Still below: record it and put it to your human partner in the
completion gate's batch. No second round.

- [ ] **Step 3: Run `draft` on plan 79**

Run: `uv run skills/writing-plans/scripts/history_entry.py draft specs/plans/completed/79-derive-roadmap-resume-and-route-tests.md --date 2026-11-07`
Expected, at `BASE80`'s backlog: exit 0; second line
`Plan: specs/plans/completed/79-derive-roadmap-resume-and-route-tests.md · Spec: none`; a `Rulings: no ledger given`
line; 7 lines that start `- Deviation (Task`; no `- Decision` line;
`- Deferred: 8 items. Source: specs/deferred_items.md, § 79-derive-roadmap-resume-and-route-tests.`; 4 closed-item
lines, one from `40-handoff-briefs` and three from `78-derive-roadmap-new-project-entry`. If a `/deferred` pass has
archived some of those items since `BASE80`, record the new counts with the reason.

- [ ] **Step 4: Run `draft` on plan 74**

Run: `uv run skills/writing-plans/scripts/history_entry.py draft specs/plans/completed/74-backlog-protocol.md --spec specs/completed/backlog-protocol.md --spec-status retired --date 2026-10-31`
Expected: exit 0, and exactly one decision line, which starts `- Decision D18 (spec amendment): approve Task 0's
amendment.`

- [ ] **Step 5: Run `deferred` on a real pass date**

Run: `uv run skills/writing-plans/scripts/history_entry.py deferred --date 2026-10-05`
Expected: exit 0, a `## /deferred — 2026-10-05` heading and 47 item lines (the live file's count at `BASE80`; one
more 2026-10-05 close is in the archive, which the script does not read). Record both real-data results in the
record's `## Real-data check`.

- [ ] **Step 6: Commit**

```bash
git add specs/red-baseline-development-history specs/red-baseline-development-history.md
git commit -m "test(specs): run the development-history treatment arms"
```
