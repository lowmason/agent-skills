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
