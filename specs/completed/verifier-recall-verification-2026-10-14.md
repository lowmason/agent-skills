# Verifier-recall verification — the cc-guide verifier's failure-test contract

**Date:** 2026-10-14 · **Status:** `FAIL (P11: changed 0/2, control 0/2 valid gate reps; PASS needed 4/5, unreachable after wave 1; gate2 skipped by owner ruling). Cheap arms (b)-(e) met DF20 on the changed arm, (c) by the registered rule only (the range defect never reproduced); files-mode precision tripped checkpoint condition 5 as registered (changed readme 8 UNSUPPORTED contradicts, control 0); DF7 and DF8 held on the 2 + 2 gate reps, given ruling 6`
**Governs:** `.claude/agents/cc-guide-verifier.md` (plan 45)

> The raw replies, reports, sheets and transcripts stay in the kit `K` =
> `~/.cache/agent-skills/scratch/plan45/` (`results/`, `reports/`, `sheets/`, `RESULTS.md`,
> `changes.log`), outside this repository. This record carries counts, claim labels, line pointers
> and paths only: no text from a report, a packet or the docs.

Executes `e32a06f:specs/plans/45-claude-code-drift-automation.md`, Tasks 3-5 (the runs) and
Task 6 (this record). Source: the open item "The audit verifier's omission recall was 3 of 7 known positives"
in `specs/deferred_items.md`, under `44-claude-code-drift-automation — 2026-10-13`, whose done-when
is an audit of the pre-fix guide (`5bd78a7`) against the 2.1.296 snapshot that reports at least
`deniedModels` (P11). The change under test is Task 1's commit `0b76543` (the verdicts defined by a
failure test, the item rule DF18 and the choice guard DF19).

## Fixture

**Packets**, read in place under `~/.cache/agent-skills/cc-guide/packets/` (never written, never
settled); each rep got a copy without `report.md` and `settled.json`:

| Label | Packet | Mode | Valid reps per arm (target) |
|---|---|---|---|
| audit (gate) | `20261013T113847-audit` | audit | 5 |
| (d) rules | `20261013T175307-verify/rules` | verify | 3 |
| (b) readme | `20261013T121854-files/hooks__README.md` | files | 3 |
| (c) runner | `20261013T124015-files/agents__test-runner.md` | files | 3 |
| (e) pyrule | `20261013T205255-files/rules__clean-code-python.md` | files | 3 |

The audit and rules reps also read the docs snapshot `~/.cache/agent-skills/cc-guide/2.1.296/docs`
(`--add-dir`).

**Arms** (copied to `K/arms/`):

| Arm | Source | Blob | sha256 of `K/arms/<arm>.md` |
|---|---|---|---|
| control | `.claude/agents/cc-guide-verifier.md` at `938993c` | `ae9e2e2e29f31421dbf02ddaf62d6910c39d33ba` | `57aea189834ae8cc7c24911155952a4213c1eaf6e9bc93229911791889f16498` |
| changed | the same file at Task 1's commit `0b76543` | `d2b0bebfa80146697e642e514252754c09a181d1` | `1df2432041647b2c69e21ba4c39e490c888178ed44d65cdef9ef5463e26f3742` |

The bodies differ by Task 1's 20 added lines; the frontmatter differs only in the `# cc-guide:`
stamp, which never reaches the verifier's prompt.

**Freeze:** `K/FREEZE.sha256`, sha256 `442e3f74a61fea3c813a2152c63a15699e377bc924769043305ac7d70652a868`
(the round-1 record, kept as written; each later kit change logs its new hashes in `K/changes.log`).

## Pre-registration

The plan's "Pre-registration (fixed before any rep runs)" section and its Settled defaults
DF2-DF21 (Planning record, "Settled defaults"), in
`e32a06f:specs/plans/45-claude-code-drift-automation.md` (lines 154-185 and 252-324 at
`e32a06f`), merged to `main` as `9773468` (lowmason/agent-skills#46). The ground-truth key P1-P14
is the Planning record's "Ground-truth key" in the same file (lines 109-140 at `e32a06f`).

**Logged changes and rulings** (`K/changes.log`, all 2026-10-14). The pre-registration allows two
pilot-stage rulings and says no post-hoc rulings; every entry after the pilot below except 3 is
therefore a deviation from it, marked with when it fell relative to the results it could touch.

1. **Kit guards before the freeze** (owner ruling at Task 2's review): `run.result_line` and
   `grade.load` guarded against a truncated line, `check_binary` refuses a missing held binary
   cleanly, the `common.CLAUDE` test pins the exact held path. The kit's tests became 47, not the
   plan's 43. Before any run.
2. **Pilot: no ruling needed.** The background dispatch counted as completed and its report was found.
3. **The cheap checkpoint's condition 5 held as rated** (r11 3, r27 4 UNSUPPORTED `contradicts`; 0
   under the nearest other reading). The owner chose to proceed to the gate, ratings standing as
   recorded. A decision point the rules provide.
4. **`grade.listed_paths` skips refused (`is_error`) tool results**, with a test (kit 48). r13's
   void came from a refused call's own error text; r13 stays void, so the fix rescued no rep.
   After the cheap results, before the gate.
5. **Gate1 r28-r31 all void** by `claude -p`'s 10-minute background-wait ceiling (V6). Rulings: every
   rep runs with `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=2280000` (38 minutes, under the audit's 2400 s
   timeout); the four voids are replaced by their own batch, `gate1redo` (gate1's pairs, re-blinded),
   outside the spare count; `run.result_line` reads the result record wherever it sits in the stream,
   so spend counts the recorded cost (kit 51). Before any valid gate result.
6. **V2 treats the rep's own session tool-results directory as inside.** Claude Code saved an
   oversized Grep result of the rep's own packet changelog under that rep's session and had the
   verifier Read it back (r32, r35). r32 and r35 were first graded VOID, then regraded blind before
   unblinding (kit 52). After r32's and r35's V2 grades, blind to arm, before unblinding; it changed
   those two reps' validity.
7. **Gate2 skipped.** After wave 1 the changed arm had 0 of 2 P11 hits, so 4 of 5 was unreachable;
   the owner ruled the gate FAIL on wave 1 (a deviation from Task 5 Step 3). After wave 1's results.

The docs snapshot's `shasum -a 256` listing and `~/.claude/settings.json`'s hash were recorded before
each hand-over and after each batch (probe and pilot, cheap, spare, gate1redo) and were unchanged
every time (`K/changes.log`, listings cited as unchanged, not reproduced). Gate1 has no after-batch
entry of its own: the gate1redo hand-over listing (`K/changes.log:342`), taken after gate1 ran,
served as that check.

## Dispatch

**Owner-launched, from a plain terminal** (Channel 5), every batch on 2026-10-14. Claude Code
2.1.296, the held copy `/Users/lowell/.cache/agent-skills/scratch/plan45-bin/2.1.296`, sha256
`c9b5341637becbd423ddffc5b254afb645682a3868cb708bbc6cc0e7bb419937`, version checked by `run.py`. Each
rep ran in its own `/private/tmp/q7r/<rid>/`, no git repository. Main session Sonnet 5.5; verifier
`claude-sonnet-5-5` at `xhigh` with the Opus 5.5 advisor available (V7, V8). Ceiling $100
(`K/ceiling.txt`), approved at Task 3.

**Probe (r01, $0.23).** Call 1, the canary Read outside the rep directory: refused. Call 2, another
project's auto-memory `MEMORY.md`: refused (the fence's exemption does not cover another project's
memory). Call 3, a Glob of the packets directory: refused. Call 4, a Read in the docs snapshot:
returned. The canary token appeared nowhere. A refusal shows as an `is_error` tool result naming the
fence setting. No redesign trigger.

**Pilot (r02; rules, control; $0.74; counts toward no result).** Compared with the production rules
verify (`f3828a8d`, `agent-a9d4a3fd`): 4 and 4 system-prompt parts, equal by index; model, effort and
version equal on both sides; the only attachment type in the rep alone is `budget_usd` (from
`--max-budget-usd`, spend figures only), none in production alone; request shape background,
entrypoint `sdk-cli` against production's `cli` (DF5's known difference); 1 advisor call. The hand
reading of its whole injected context found no packet, docs or answer content (V3 clean). Its control
contract found D1, recorded as a sheet check, not a count.

**Per rep.** Cost is `total_cost_usd` from each rep's `type: result` record (`K/results/<rid>.jsonl`);
advisor calls from the sheet or `K/RESULTS.md`.

| rid | batch | packet | arm | valid / VOID | cost | advisor |
|---|---|---|---|---|---|---|
| r01 | probe | rules | probe | (validity run) | $0.23 | n/a |
| r02 | pilot | rules | control | valid (uncounted) | $0.74 | 1 |
| r03 | cheap | rules | control | valid | $0.41 | 0 |
| r04 | cheap | rules | changed | valid | $1.00 | 1 |
| r05 | cheap | rules | changed | valid | $0.93 | 1 |
| r06 | cheap | rules | control | valid | $0.44 | 0 |
| r07 | cheap | rules | control | valid | $0.54 | 0 |
| r08 | cheap | rules | changed | valid | $0.99 | 1 |
| r09 | cheap | readme | changed | valid | $1.15 | 1 |
| r10 | cheap | readme | control | valid | $0.53 | 0 |
| r11 | cheap | readme | changed | valid | $1.20 | 1 |
| r12 | cheap | readme | control | valid | $0.87 | 1 |
| r13 | cheap | readme | changed | **VOID** (V2 as graded) | $1.12 | 1 |
| r14 | cheap | readme | control | valid | $0.94 | 1 |
| r15 | cheap | runner | changed | valid | $0.50 | 1 |
| r16 | cheap | runner | control | valid | $0.29 | 0 |
| r17 | cheap | runner | changed | valid | $0.52 | 1 |
| r18 | cheap | runner | control | valid | $0.45 | 1 |
| r19 | cheap | runner | control | valid | $0.30 | 0 |
| r20 | cheap | runner | changed | valid | $0.26 | 0 |
| r21 | cheap | pyrule | changed | valid | $0.49 | 1 |
| r22 | cheap | pyrule | control | valid | $0.24 | 0 |
| r23 | cheap | pyrule | control | valid | $0.25 | 0 |
| r24 | cheap | pyrule | changed | valid | $0.47 | 1 |
| r25 | cheap | pyrule | changed | valid | $0.45 | 1 |
| r26 | cheap | pyrule | control | valid | $0.25 | 0 |
| r27 | spare (r13) | readme | changed | valid | $1.03 | 1 |
| r28 | gate1 | audit | control | **VOID** (V6) | $1.14 | 1 |
| r29 | gate1 | audit | changed | **VOID** (V6) | $1.64 | 1 |
| r30 | gate1 | audit | changed | **VOID** (V6) | $1.58 | 1 |
| r31 | gate1 | audit | control | **VOID** (V6) | $3.00 | 1 |
| r32 | gate1redo | audit | control | valid (after ruling 6) | $2.95 | 1 |
| r33 | gate1redo | audit | changed | valid | $3.51 | 1 |
| r34 | gate1redo | audit | changed | valid | $3.09 | 1 |
| r35 | gate1redo | audit | control | valid (after ruling 6) | $3.36 | 1 |

**Spend:** probe and pilot $0.97; cheap batch (r03-r26) $14.58; spare r27 $1.03; gate1's void reps
$7.37 (their mid-stream result records; `run.py` first charged each its $8 cap); gate1redo $12.91.
Run total **$36.86 of the $100 ceiling**.

## Validity

**Voids.**
- **r13 (readme, changed): VOID, V2 as graded.** Its Glob of
  `/Users/lowell/Projects/agent-skills/hooks/` was refused by the fence; the grader's
  `listed_paths` matched that path inside the refusal's own error text. No outside content
  returned. Replaced by spare r27 under the pre-registered rule, and kept void after ruling 4
  changed the grader (the regenerated sheet now prints no void for it).
- **r28-r31 (audit, gate1): VOID, V6**, no report: each verifier was stopped about 10 minutes after
  the main session's last turn by the `-p` background-wait ceiling. The grader as then written also
  found no result record (the record was not on the stream's last line). Replaced by gate1redo
  outside the spare count (ruling 5).
- **r32, r35 (audit, control): first VOID under V2**, for a Read of their own session's saved tool
  result; valid after ruling 6, regraded blind before unblinding.

**Injected hits traced.** The verifier sheets show no injected hit in any rep (V3). Every main
session shows one recorded-only hit, `specs/plans` inside its `skill_listing` attachment: a
skill description's own text in the user's skill listing, not a path into this repo or an answer.
V1 pins everything the main session passes on. Permission denials: 0 in every rep. Refused outside
calls: none but r13's.

**Listings.** The docs snapshot's listing and the settings hash were unchanged after every batch
(Pre-registration, above).

## Result

### Cheap arms, each against DF20 (3 valid reps per packet and arm)

| Packet | Measure | changed | control | DF20 rule (changed arm) | Met |
|---|---|---|---|---|---|
| (d) rules | D1 hits | 3/3 | 1/3 (r06) | hit in ≥ 2 of 3 | yes |
| (d) rules | UNSUPPORTED | 0 | 0 | | |
| (b) readme | B1 hits | 3/3 | 0/3 | B1 in ≥ 2 of 3 and N1/N2 flagged in ≤ 1 | yes |
| (b) readme | B2 found (key) | 2/3 (r09, r11; r27 in substance only) | 1/3 (r12) | (retention) | |
| (b) readme | N1 or N2 flagged | 0/3 | 0/3 | | |
| (b) readme | UNSUPPORTED `contradicts` | 8 (r09 1, r11 3, r27 4) | 0 | | |
| (c) runner | passes | 3/3 | 1/3 (r16, r19 fail: 3 `unparseable:` none-lines each) | passes in all 3 | yes (registered rule) |
| (c) runner | UNSUPPORTED | 0 | 1 (r18) | | |
| (e) pyrule | E1 hits | 3/3 | 0/3 | hit in ≥ 2 of 3 | yes |
| (e) pyrule | UNSUPPORTED `contradicts` | 0 | 0 | | |

(c) passed by the registered rule, 3/3 against 1/3, but the control's two failures were none-line
formatting: r16 and r19 each wrote 3 section none-lines that settle could not parse
(`K/sheets/r16.txt:16-18`, `K/sheets/r19.txt:16-18`), not line ranges. No rep in either arm wrote
a range row, so the original range defect never reproduced and the one-line rule's effect is
untested; the added contract text does not address none-lines.

r27's B2: its `hooks/README.md:97` row is B2 in substance and SUPPORTED, but the key as registered
needs the row to name `onFailure`, so it is scored not found.

The 8 changed-arm readme UNSUPPORTED rows are all on contested readings (`K/RESULTS.md`, rating
notes): the newline-split row on `:89`, the memory-re-enables-Write/Edit rows on `:107`/`:108` and
`:191`/`:192`, and r27's `:141` row on the main-session guard. Each was rated UNSUPPORTED because the
case it adds is hypothetical for this file or not given by the passage its quote comes from; under
the nearest other reading each is SUPPORTED and the changed readme total is 0 (r09 0, r11 0, r27 0).
The `:89` rows (r09, r11, r27) have independent confirmation: the final review's Codex seat (Codex
final review, 2026-10-14) found them false contradictions, since the hook already splits on
newlines. This matters beyond the tally: settle prints a files rep's `contradicts` rows as fixes to
apply in the working tree (`build/cc_guide/settle.py:674-675`, `:684`), so each false contradiction
becomes a proposed edit. DF7's ceiling covers only the audit, and was measured on 2 + 2 reps.

**Correction volume (DF21, report only)**, median / total over valid reps:

| Packet | changed | control |
|---|---|---|
| (d) rules | 6 / 18 | 1 / 4 |
| (b) readme | 8 / 23 | 1 / 2 |
| (c) runner | 1 / 3 | 1 / 4 |
| (e) pyrule | 2 / 6 | 0 / 0 |
| audit | 16.5 / 33 | 7 / 14 |

**Cheap checkpoint.** Conditions 1-4 did not hold on the changed arm ((d) misses 0/3, (e) misses
0/3, (c) fails 0, N1/N2 0/3). Condition 5 held as rated (r11 3, r27 4 UNSUPPORTED `contradicts`, the
ceiling being 2), and not under the nearest other reading. The owner chose to proceed (ruling 3).

### The gate (audit), per arm over the valid reps (changed r33, r34; control r32, r35)

| Measure | changed | control |
|---|---|---|
| P11 hits | 0/2 | 0/2 |
| P11 B-only mentions | 0 | 0 |
| UNSUPPORTED (kept corrections), total / max per rep | 2 / 1 (r33 1, r34 1) | 1 / 1 (r35) |
| P1 / P2 / P3 / P4 / P5 / P6 | 1 / 2 / 2 / 2 / 1 / 2 | 0 / 2 / 2 / 2 / 0 / 2 |
| P9 / P13 / P14 | 2 / 1 / 2 | 2 / 2 / 2 |
| secondary P7 / P8 / P10 / P12 | 1 / 0 / 1 / 0 | 0 / 0 / 1 / 0 |

No valid gate rep wrote any row naming `deniedModels`, in either arm. P14 was carried as a B row
in every rep (r34 also as an A row). The three UNSUPPORTED rows: r33's L423 row also names Microsoft
Foundry, where the price case it adds does not hold (scope; `model-config.md:42-49`); r34's L429 row
adds an organization default behind the user's choices with the wrong conditions
(`model-config.md:141`); r35's L418 row rewords the TODO's date in a way that changes nothing a
follower does (settle left it out of r35's 7; the grader kept it, so it is rated). Every other kept
correction in r32-r35 was SUPPORTED, against the pointers listed in `K/RESULTS.md`.

## Decision

The PASS rule (`e32a06f:specs/plans/45-claude-code-drift-automation.md`, Pre-registration,
"Decision rules"), clause by clause:

| Clause | Needed | Observed | Holds |
|---|---|---|---|
| changed arm hits P11 | ≥ 4 of 5 valid | 0 of 2 | **no** |
| control hits P11 | ≤ 1 of 5 | 0 of 2 | yes (so far) |
| DF7: changed UNSUPPORTED ≤ control + 3, no changed rep > 2 | ≤ 4, max ≤ 2 | 2, max 1 (control 1) | yes |
| DF8: each of P1-P6, P9, P13, P14, changed ≥ control − 1 | | P1 1 vs 0, P2 2 vs 2, P3 2 vs 2, P4 2 vs 2, P5 1 vs 0, P6 2 vs 2, P9 2 vs 2, P13 1 vs 2, P14 2 vs 2 | yes |

The first-wave stop rule (control P11 hits reaching 2) did not trigger.

**FAIL, not UNSETTLED.** The Replacement rule makes a packet UNSETTLED when spares run out short of
its target, and the audit has 2 + 2 of 5 + 5 valid reps. But the PASS clause on the changed arm was
already decided: with 0 of 2, even three more hits in gate2's three changed reps give at most 3 of 5,
below the 4 needed. The owner ruled the gate FAIL on that basis and skipped gate2 (ruling 7); gate2
was not run, not voided. The DF7 and DF8 clauses hold on these 2 + 2 reps only, not on the
registered 5 + 5.

**Sensitivity.** Under the nearest other reading of the contested gate rows (r33's L423 Foundry
clause read as an aside, r34's L429 organization default read as beside the core correction), the
changed arm's UNSUPPORTED total is 0, and r35's control total stays 1. The verdict does not move: it
is decided by P11, which no rep in either arm reported under any reading. Under the nearest other
reading of the contested cheap readme rows, the checkpoint's condition 5 would not have held, and
the run would have gone to the gate without a stop.

The DF7 and DF8 "holds" depend on ruling 6: r32 and r35 are the control's only valid gate reps, and
without that ruling neither clause can be evaluated. The FAIL verdict does not depend on it, since
the changed arm's 0 of 2 on P11 is unaffected.

**What the result says.** The contract change fixes three of the cheap defects on their packets: (d)
and (e), the calibration miss in both modes, go from 1/3 and 0/3 to 3/3; (b) from 0/3 to 3/3 with no
negative control flagged. (c) passed by the registered rule, 3/3 against 1/3, but the control's
failures were none-line formatting and the range defect never reproduced, so the one-line rule is
untested. Files-mode precision has a cost: under the registered reading checkpoint condition 5
tripped, the changed (b) reps keeping 8 UNSUPPORTED `contradicts` rows (r11 3, r27 4, r09 1) against
the control's 0, above the per-rep ceiling of 2, and settle turns each into a proposed edit
(`build/cc_guide/settle.py:674-675`, `:684`); the Codex final review (2026-10-14) independently
found the `:89` rows false. DF7 covers only the audit, on 2 + 2 reps. It does not reach the audit's
gate omission: neither arm, on either contract, wrote a row of any kind on `deniedModels`, though
the audit packet's changelog carries the entry (`changelog.md:1288`, the key's pointer). The
audit's correction volume roughly doubled on the changed arm (median 16.5 against 7), with
precision inside DF7's ceiling.

## Disposition

The item "The audit verifier's omission recall was 3 of 7 known positives" stays open in
`specs/deferred_items.md` with a `> plan 45:` note giving these counts and this record's path. Its
(b) and (c) observations met DF20 on the changed arm, but nothing closes, because the gate failed.
Whether Task 1's contract change landed was the owner's decision at plan completion: the owner
reverted it (2026-10-15, before integration), so `.claude/agents/cc-guide-verifier.md` stays at the
control arm. For the record, the change held DF7 and DF8
(on 2 + 2 reps, given ruling 6) and fixed (b), (d) and (e); (c) passed only by the registered rule.
Against it: in files mode it tripped checkpoint condition 5 as registered (changed readme 8
UNSUPPORTED `contradicts`, r11 3 and r27 4 above the per-rep ceiling of 2, control 0), each of which
settle would print as an edit to apply (`build/cc_guide/settle.py:674-675`, `:684`), and DF7 does
not cover files mode; the Codex final review (2026-10-14) confirmed the `:89` rows false.

New items, in the schema of `skills/writing-plans/references/deferred-backlog.md`, under
`## 45-claude-code-drift-automation — 2026-10-14`:

1. One files row per checkable statement on a source line (DF17, deferred at planning; evidence
   `README.md:163` in the `20261013T205255-files` pass). Size: design.
2. A files-mode miss that settle does not hold leads to `baseline cite`, which hides it until the
   guide section changes again (deferred at planning). Size: design; done when the owner has chosen
   a remedy and it is applied.
3. The audit writes no B row for the changelog entries behind P11 and P8 (borne out: no valid gate
   rep named `deniedModels` in any row, and none wrote a B row for P8's entry). Size: design.
4. A fixture-domain-free precision fixture for the files rule (borne out: the cheap checkpoint
   turned on contested readings of the changed readme reps' rows). Size: plan.
5. The files rule's reference case must apply to the component the file describes (the Codex final
   review's finding on the changed arm's files-rule wording; the `:89` rows applied Claude Code's
   permission-matcher splitting to the repo's own hook). Added at plan completion. Size: plan.

The backlog carries each in full, with its closure condition. Not filed: P12's two pages (P12 was 0
in every rep, both arms) and verify-mode `doc:line` ranges (DF14; this run has no evidence on
them). P7 is not in the B-row item: r33 wrote a B row for its changelog entry (`changelog.md:224`).
