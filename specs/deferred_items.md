# Deferred items

## 7-audit_7_5_26 — 2026-07-05
- [ ] Empirical micro-test of the reworked execution-skill routing (B1/B2,
      writing-skills doctrine): deferred because the monthly spend limit
      blocked subagent dispatch during inline execution. Run the three
      scenarios against the new vs. old subagent-driven-development
      description — S1 "execute plan task by task" → subagent-driven-development,
      S2 "tightly interleaved, one continuous context" → executing-plans,
      S3 "execute directly, no subagent dispatch" → executing-plans; expect
      3/3 on the new wording, with the old wording as the control. A direct
      read-through confirmed the routing at execution time; this is the
      empirical arm. See specs/plans/completed/7-audit_7_5_26.md Task 6
      Steps 1–2.
- [ ] Subagent fixture rep of the deferred-items ticking pass (B4):
      deferred by the same spend limit. Build a fixture where a plan that
      defers nothing implements an earlier deferred item, and confirm the
      Plan Completion Protocol ticks that item (`- [x] … → done in plan <id>`)
      without appending an empty section for the new plan. A read-through of
      the amended writing-plans § Plan Completion Protocol step 3 confirmed
      the ticking pass runs even when nothing is deferred; this is the
      end-to-end arm. See specs/plans/completed/7-audit_7_5_26.md Task 6
      Step 3.

## 8-track-model-experiments — 2026-07-05
- [ ] `_has_warning` folds ArviZ 1.2.0's `diag_diff` (similar predictions / N<100)
      and `diag_elpd` (the Pareto-k analog) into one `warning` boolean, so the
      ledger's `warn`/`warning` over-reports (the SAFE direction; a clarifying
      comment is present). Consider surfacing the two diagnostics as separate
      fields/columns. Same site
      (skills/track-model-experiments/scripts/compare_experiments.py `_has_warning`)
      has a latent NaN false-positive — `str(np.nan).strip()` → `'nan'` is truthy;
      ArviZ emits `''` not NaN today so it's latent, but harden with a NaN guard.
- [ ] `compare()` raises `SystemExit` for the <2-variants and mismatched-observation
      guards while `main()` catches only `ValueError`
      (skills/track-model-experiments/scripts/compare_experiments.py). Tests pass
      (SystemExit exits nonzero with the message), but `compare()` is documented as
      a reusable interface a library caller can't recover from. Make both guards
      raise `ValueError` and let `main()` own the process exit.
- [ ] `update_ledger` normalizes cell whitespace on any table row it rewrites
      (collapses human cell padding) with no docstring note that this is intentional
      (skills/track-model-experiments/scripts/compare_experiments.py). Add a one-line
      docstring note so a maintainer doesn't read it as accidental.
- [ ] `update_ledger`'s "no existing COMPARISON block" else-branch (the append path)
      is untested — every fixture ledger already contains the markers
      (skills/track-model-experiments/scripts/test_compare_experiments.py). Traced as
      idempotent (run 2 matches the regex and substitutes at the same position), but
      add a one-line test that starts from a marker-less ledger.
