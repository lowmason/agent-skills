## `c5a-merged` — a stage already merged, on t4 + merged

The kit's `merged` extra runs before turn 1. In the rep's repo, `feat/s2a-csv-export` is already merged into `main` with a merge commit, the feature branch is deleted, and `main` is pushed to origin. The plan file stays in `specs/plans/`, unretired, and the roadmap's S2a box stays unticked.

`specs/plans/4-pondwatch-v2-s2a.md` is Stage S2a of `specs/pondwatch-v2-roadmap.md`. Its ledger records the deviation: `export_csv(rows, path)` shipped as `write_table(rows, path, columns=None)`. Stage S2b consumes it. Turn 1 says the final review was resolved and the branch was merged into `main` yesterday, then asks to plan S2b. Turn 2 says "Go ahead."

- **F-handoff** and **F-stamp**, as for `c5a-pos`.
- **F-branch:**
  - PASS if, at the end, `main` holds the protocol's commits: the plan's markup and retirement, and the roadmap stamp.
  - FAIL if those commits are only on another branch, or if the rep recreates `feat/s2a-csv-export` for them.
- **F-resume:**
  - PASS if the last final message recommends resuming the roadmap: a `/clear` or fresh session, then derive-roadmap, or "resume the roadmap", on the roadmap file.
  - FAIL otherwise.
- **F-next**, as for `c5a-pos`, read under the owner's ruling of 2026-10-15: a routing remark beside a correct resume handoff is not naming the next work.
