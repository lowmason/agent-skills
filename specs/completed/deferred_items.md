# Deferred items

## 7-audit_7_5_26 — 2026-07-05
- [x] Empirical micro-test of the reworked execution-skill routing (B1/B2,
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
      → done 2026-07-05 (Group A verification, this session; workflow
      wf_ad906866-ec1): ran the empirical arm as a 48-rep, codename-scrubbed
      micro-test (fictional skill names + names scrubbed from the description
      bodies, so routing was on wording alone, not installed-skill knowledge;
      role-assignment and listing order counterbalanced). Result: the new and
      old SDD descriptions route IDENTICALLY — S2 (tightly-coupled) and S3
      (direct execution) → executing-plans at ~100% in BOTH arms; S1 (bare
      "execute … task by task") is a ~50/50 coin-flip in BOTH arms because
      executing-plans' own (held-constant) description surface-overlaps "task
      by task … current session". The control was non-discriminative (as
      predicted), and S1's ambiguity is inherent to the two descriptions'
      overlap — not caused by the rewrite, and disambiguated in real use by
      the plan header (stripped from this isolated probe). Net: the rewrite is
      confirmed HARMLESS (no regression) and the routing-critical carve-outs
      hold; empirically backs the read-through's conclusion that the fix stands
      on removing the textual contradiction, not on shifting the routing
      distribution. Observation (not actioned): the two descriptions don't
      disambiguate a bare "execute task by task" on their own.
- [x] Subagent fixture rep of the deferred-items ticking pass (B4):
      deferred by the same spend limit. Build a fixture where a plan that
      defers nothing implements an earlier deferred item, and confirm the
      Plan Completion Protocol ticks that item (`- [x] … → done in plan <id>`)
      without appending an empty section for the new plan. A read-through of
      the amended writing-plans § Plan Completion Protocol step 3 confirmed
      the ticking pass runs even when nothing is deferred; this is the
      end-to-end arm. See specs/plans/completed/7-audit_7_5_26.md Task 6
      Step 3.
      → done 2026-07-05 (Group A verification, this session): ran the fixture
      rep on 3 ISOLATED git-init'd fixtures (each a nothing-deferred plan 9 that
      implements an earlier open plan-3 item). 3/3 reps produced the exact
      correct end state, verified on ground-truth files (not self-reports): the
      earlier item ticked "→ done in plan 9", NO empty plan-9 section appended,
      a "nothing deferred" status header added, and the plan retired to
      specs/plans/completed/ in one retire commit with a clean tree. Zero
      blast-radius on the real repo (confirmed clean after). Confirms the
      step-3 ticking pass end-to-end.

## 8-track-model-experiments — 2026-07-05
- [x] `_has_warning` folds ArviZ 1.2.0's `diag_diff` (similar predictions / N<100)
      and `diag_elpd` (the Pareto-k analog) into one `warning` boolean, so the
      ledger's `warn`/`warning` over-reports (the SAFE direction; a clarifying
      comment is present). Consider surfacing the two diagnostics as separate
      fields/columns. Same site
      (skills/track-model-experiments/scripts/compare_experiments.py `_has_warning`)
      has a latent NaN false-positive — `str(np.nan).strip()` → `'nan'` is truthy;
      ArviZ emits `''` not NaN today so it's latent, but harden with a NaN guard.
      → done in the track-model-experiments hardening batch (commit 6043bf8): NaN
      guard added (`_diag_str`); raw `diag_diff`/`diag_elpd` surfaced as JSON fields
      in `comparison.json` (kept the single `warning` boolean for the ledger column
      rather than widening it).
- [x] `compare()` raises `SystemExit` for the <2-variants and mismatched-observation
      guards while `main()` catches only `ValueError`
      (skills/track-model-experiments/scripts/compare_experiments.py). Tests pass
      (SystemExit exits nonzero with the message), but `compare()` is documented as
      a reusable interface a library caller can't recover from. Make both guards
      raise `ValueError` and let `main()` own the process exit.
      → done in commit 6043bf8: both guards now raise `ValueError` (main() already
      caught it, so CLI behavior is unchanged); new direct-call test pins the contract.
- [x] `update_ledger` normalizes cell whitespace on any table row it rewrites
      (collapses human cell padding) with no docstring note that this is intentional
      (skills/track-model-experiments/scripts/compare_experiments.py). Add a one-line
      docstring note so a maintainer doesn't read it as accidental.
      → done in commit 6043bf8: docstring note added.
- [x] `update_ledger`'s "no existing COMPARISON block" else-branch (the append path)
      is untested — every fixture ledger already contains the markers
      (skills/track-model-experiments/scripts/test_compare_experiments.py). Traced as
      idempotent (run 2 matches the regex and substitutes at the same position), but
      add a one-line test that starts from a marker-less ledger.
      → done in commit 6043bf8: test_update_ledger_appends_when_no_markers added.
