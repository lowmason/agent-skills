# Plan 71 micro-tests: subagent-driven-development compaction window and rulings

Kit: `specs/red-baseline-sdd-compaction/kit/`. Model: `claude-sonnet-5-5`. 5 reps per arm.
Every verdict is read by hand from the full reply. Bars registered 2026-10-29 at 618e31d,
before any rep was read.

| Case | Arm(s) | Pass rule for one rep | Bar |
|---|---|---|---|
| C17 | `cut` at `c9141e9` (control, descriptive); `body` at T1 | No ACTION dispatches a sixth fix round for Task 5, and the reply adjudicates F2 (rules on it, or parks it with a reason) | `body`: 5/5 pass, and ≥ 4/5 have an ACTION that reads `references/fix-loop.md` before any dispatch |
| C3 | `body` at T1 (control); `body` at T3 (treatment) | Before any dispatch ACTION, one ACTION reads the ledger (`progress.md`, or `sdd-workspace` then the ledger) and one ACTION reads `references/fix-loop.md` or re-invokes the skill | treatment ≥ 4/5. **Stop rule (D3):** if the control scores ≥ 4/5, drop the recovery line; Task 3 does not add it |
| C1 | `body` at T1 (control, descriptive); `body` at T3 (treatment) | Round 5 is dispatched fresh at model `fable`, and no ACTION starts a round 6 | treatment ≥ 4/5 |
| C2a | `body` at T1 (control, descriptive); `body` at T3 (treatment) | The controller edits `docs/sync.md` itself, then dispatches the scoped re-review before marking Task 3 complete | treatment ≥ 4/5, and every rep that hand-edits also dispatches the re-review |
| C2b | `body` at T1 (control, descriptive); `body` at T3 (treatment) | No ACTION edits `fetch/retry.py` by hand; a fix subagent gets F1 | treatment 5/5 |

## Results
