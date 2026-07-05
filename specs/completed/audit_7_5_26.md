# Audit remediation — 2026-07-05 package review

**Status: COMPLETE (2026-07-05)** — implemented by specs/plans/completed/7-audit_7_5_26.md; deferred items in specs/deferred_items.md

Remediate all 17 distinct findings from the 2026-07-05 whole-package review
(five-lens workflow review: cross-references, skill quality, tooling,
data-skill content, process-skill coherence; 21 raw findings deduplicated
to 17). Zero Critical, six Important, eleven Minor. This spec is
self-contained: every finding is recorded here with evidence and required
fix, so the plan and implementer briefs need no external review artifact.

## Decisions (user-confirmed)

- **Scope:** all 17 findings — including lint hardening and the
  micro-testing that writing-skills doctrine requires for description and
  protocol wording changes.
- **Archives:** the four retired specs/plans get **mechanical link repair
  only** (paths re-pointed, prose/checkboxes/history untouched), plus the
  systemic fix — a line in the Plan Completion Protocol's Retire step so
  future retirements re-point relative links for the new directory depth.

## Global constraints

- Description rewrites (B1, B2) are micro-tested against a no-guidance
  control per writing-skills doctrine before deployment; the protocol
  wording addition (B4) gets a fixture rep.
- Lint changes (D1, D2) are test-first (red → green) in the existing
  `build/` pytest suite; run all three repo suites plus both lints before
  declaring done.
- Archived files (E1): path repairs only — any prose change is out of
  scope.
- NOTICE requires no edits: all touched superpowers-adapted skills are
  covered by the blanket modifications clause and the existing
  spec-driven-lifecycle item; E2 keeps the attribution link NOTICE
  documents.
- Bayesian fixes (A1, A2) require empirical verification via `uv run`
  repro scripts (scratchpad, never committed).
- Routing story all B-fixes must agree on: **executing-plans = direct,
  non-subagent execution in the current session; subagent-driven-development
  = the default when subagents exist and tasks are mostly independent.**

## A. bayesian-workflow content

**A1 (Important) — `set_host_device_count` ordering.**
`skills/bayesian-workflow/SKILL.md:103` calls `jax.random.PRNGKey` before
line 127's `numpyro.set_host_device_count(4)`. Any JAX op initializes the
XLA backend, after which the call silently no-ops — the template's
`num_chains=4` runs sequentially (empirically confirmed: template order →
1 device; corrected order → 4). The skill's own
`references/state-space.md:141` states the rule correctly.
Fix: move `numpyro.set_host_device_count(4)` to the top of the canonical
template (immediately after imports, before any JAX call) with
state-space.md's "MUST precede the first JAX op (e.g. PRNGKey) or it
silently no-ops" comment; add the ordering caveat to the Critical-rules
bullet (SKILL.md:244 area) and the Samplers section (SKILL.md:167 area).
Verify: repro script — subprocess with corrected order reports
`jax.local_device_count() == 4`.

**A2 (Important) — `add_log_prior` crashes on event-dim sites.**
`skills/bayesian-workflow/references/sensitivity.md:60-64` pairs
`post[name].dims` (batch + event dims) with a log-prob array reduced over
event dims; for `dist.LKJCholesky` / `dist.MultivariateNormal` /
`dist.Dirichlet` sites (recommended by this skill's own hierarchical.md)
`xr.Dataset` raises `ValueError` — and prior sensitivity is mandatory
workflow step 8. Line 74's "The recipe is exact" over-promises with no
event-dim caveat.
Fix: slice dims to the array's rank —
`arr = np.asarray(v).reshape((chains, draws) + v.shape[1:])` paired with
`post[name].dims[:arr.ndim]` — and add a sentence noting `log_prob`
reduces over event dims (one log-prior value per batch element for
multivariate sites); temper line 74 accordingly.
Verify: repro script — the correlated-varying-effects model from
hierarchical.md:91-107 (LKJCholesky + MultivariateNormal) runs
`add_log_prior` without raising and the `log_prior` group exists.

**A3 (Minor) — artifact list incomplete.** `SKILL.md:251` presents a
complete-looking artifact list but omits `prior_predictive.png`,
`pit_coverage.png`, and the `psense.png`/`psense.json` pair that
`references/reporting.md:29-44` requires and the report template embeds
unconditionally (lines 116, 164).
Fix: replace the inline list with a pointer to reporting.md's Output
structure as the single canonical list (retain one or two examples if
helpful, marked as examples).

**A4 (Minor) — contradictory ESS thresholds.** `SKILL.md:238` says
ESS < 100 × n_chains = unreliable; `references/diagnostics.md:72-77`
classifies 100–100×n_chains as "Marginal" and its first table row is
garbled ("≥ 100 * number of chains per chain").
Fix: adopt the ESS ≥ 100 × n_chains convention in both places; below it =
act (run longer / reparameterize); drop the "per chain" phrase.

**A5 (Minor) — mislabeled link.** `references/hierarchical.md:15` labels
NumPyro's baseball (Efron–Morris) example "eight-schools example".
Fix: relabel "baseball partial-pooling example".

**A6 (Minor) — stale skill README.** `skills/bayesian-workflow/README.md:53-55`
claims the skill "stays runnable on the older classic-ArviZ (0.23)" —
SKILL.md:65-67 explicitly disavows this ("the 1.x idioms here will raise
on a 0.23-only environment"); the What's-included tree (README.md:69-85)
omits `references/state-space.md` and `references/publications.md`.
Fix: reword to "documents the 0.23 equivalents as a porting reference;
inline examples target ArviZ ≥ 1.0"; add both files to the tree.

## B. Process-skill routing + protocol

**B1 (Important) — SDD description summarizes its workflow.**
`skills/subagent-driven-development/SKILL.md:3-12` frontmatter describes
the process ("a fresh implementer per task, a task-scoped spec+quality
review after each…", "Covers model-tier selection…") and embeds a process
instruction ("check the progress ledger before re-dispatching anything") —
the anti-pattern writing-skills/SKILL.md:107 and :157-167 forbids, on the
very skill whose description-following failure the doctrine documents.
Fix: rewrite triggers-only — keep the trigger list ("execute this plan",
plan header naming the skill, a specs/plans/*.md handoff, resuming a
partially executed plan) and the "Not for" carve-outs (updated per B2);
no workflow clauses. Micro-test per doctrine.

**B2 (Important) — circular routing between the execution skills.**
`skills/executing-plans/SKILL.md:17` unconditionally defers to SDD
whenever subagents exist; SDD:11-12 routes "execution in a separate
session" to executing-plans while executing-plans:4 says "current
session"; `README.md:55` calls executing-plans "Execute a written plan in
a separate session with review checkpoints" — both claims false (its body
has no checkpoints and it is current-session). A tightly coupled plan
bounces between the two skills.
Fix (per the routing story in Global constraints): executing-plans:17
becomes "If subagents are available and the tasks are mostly independent
and your human partner didn't ask for direct execution, use the
subagent-driven-development skill instead"; SDD's carve-out becomes "Not
for tightly coupled tasks needing one continuous context, or
partner-requested direct execution (use executing-plans)" — dropping
"separate session"; README.md:55 reworded to match (direct, current-
session, non-subagent execution). Micro-test the two description changes.

**B3 (Important) — inline execution handoff never names executing-plans.**
`skills/writing-plans/SKILL.md:160-178`: option 1 says "REQUIRED
SUB-SKILL: Use subagent-driven-development" but option 2 names no skill,
leaning on a parenthetical about the user's private CLAUDE.md that other
consumers of the public repo don't have; the mandatory plan header
(SKILL.md:65) requires SDD unconditionally even for inline execution.
Fix: option 2 gains "REQUIRED SUB-SKILL: Use executing-plans" and drops
the CLAUDE.md parenthetical; the plan-header sentence is reworded to name
subagent-driven-development as the **default** for agentic workers, with
executing-plans as the alternative when inline execution was chosen.

**B4 (Important) — the /deferred ticking hole.**
`commands/deferred.md:5-7` delegates all ticking to "later plans'
completion-protocol runs", but the Plan Completion Protocol's only ticking
instruction (writing-plans/SKILL.md:225-227) lives inside step 3, and step
3 is skipped entirely "when nothing was deferred" — so a plan that defers
nothing but implements an old deferred item never ticks it, and read-only
/deferred re-proposes done work forever.
Fix: add an explicit action to step 3 **before** the skip clause: "If
`specs/deferred_items.md` exists, first tick any earlier items this plan
implemented (`- [x] … → done in plan <id>`) — do this even when the
current plan deferred nothing; the skip below applies only to appending
new items." Verify with one fixture rep: a plan that implements an old
deferred item while deferring nothing new; judge that the agent ticks it.

**B5 (Minor) — retirement breaks archive links (systemic half).**
The protocol's Retire step (writing-plans/SKILL.md:229-234) git-mv's docs
one directory deeper without adjusting relative links (the mechanism that
broke E1's files).
Fix: add one line to the Retire step: re-point the retiring plan's/spec's
relative links for their new depth as part of retirement.

**B6 (Minor) — brainstorming restates retirement without the guard.**
`skills/brainstorming/SKILL.md:113` says unconditionally "When the spec's
work is complete, mark it complete at the top and retire it to
`specs/completed/`", omitting the protocol's shared-spec guard ("only if …
no other live plan implements it").
Fix: turn the line into a pointer to writing-plans' Plan Completion
Protocol, noting retirement is guarded.

**B7 (Minor) — SDD's ending is asymmetric.** SDD:76 terminal node and its
Integration section (:430-435) never name finishing-a-development-branch
(executing-plans does, :45-46), deferring to "your CLAUDE.md
engineering-discipline rules" — which only this user has.
Fix: SDD's terminal step and Integration section name
finishing-a-development-branch as the required next skill; drop the
CLAUDE.md reliance.

## C. Reviewer-template sync

**C1 (Minor) — `[DIFF_FILE]` undocumented.**
`skills/requesting-code-review/code-reviewer.md:33` uses
`**Diff file (optional):** [DIFF_FILE]` but the Placeholders list
(:143-147) and `requesting-code-review/SKILL.md:50-54` omit it — while
SDD's File Handoffs contract expects every reviewer dispatch, including
the final whole-branch review, to carry a review-package path.
Fix: add `[DIFF_FILE]` to both placeholder lists, worded like
task-reviewer-prompt.md:216-218 (the path printed by SDD's
`scripts/review-package`; expected when dispatched from SDD, optional
otherwise).

## D. Lint hardening (test-first)

**D1 (Minor) — agents/ and commands/ are unlinted.**
`build/check_frontmatter.py:99-101` walks only `skills/`; the load-bearing
frontmatter in `agents/code-reviewer.md`, `agents/task-reviewer.md`, and
`commands/deferred.md` has no mechanical guard.
Fix: extend check_frontmatter.py with per-type schemas — `agents/*.md`:
frontmatter parses as a YAML mapping, `name` matches the filename stem,
`description` non-empty, `tools` (if present) is a comma-separated list
drawn from a known-tools set; `commands/*.md`: frontmatter parses,
`description` non-empty. Tests first in `build/test_check_frontmatter.py`
(true-positive on the real repo, true-negative on synthetic bad fixtures).

**D2 (Minor) — provenance check is a raw substring match.**
`build/check_provenance.py:33` uses `if f'{name}/' not in notice` — a
future skill whose `name/` appears inside existing NOTICE prose (e.g.
`plans`, `code-review`, `data`) passes with no attribution entry.
Fix: anchor the match to an entry position (line-start regex per the
existing NOTICE entry indentation, e.g.
`re.search(rf'^\s*{re.escape(name)}/', notice, re.M)` tightened to avoid
prose matches); add a true-negative test for a name that is a substring of
another entry.

## E. Hygiene

**E1 (Minor) — dangling links in four archived files** (broken by the
skills/ move and/or retirement `git mv`):
- `specs/completed/audit_1_3_26.md:15` → `../bayesian-workflow/SKILL.md`
  should be `../../skills/bayesian-workflow/SKILL.md`; `:40` →
  `../subagent-driven-development/SKILL.md` and
  `../subagent-driven-development/scripts/sdd-workspace` likewise gain
  `../../skills/` prefixes.
- `specs/completed/task-reviewer-agent-and-deferred-command.md:16` →
  `../skills/subagent-driven-development/task-reviewer-prompt.md` should
  be `../../skills/subagent-driven-development/task-reviewer-prompt.md`.
- `specs/plans/completed/1-recommend-probabilistic-model.md:19` →
  `../specs/2026-06-21-recommend-probabilistic-model-design.md` should be
  `../../completed/recommend-probabilistic-model.md` (renamed and moved).
- `specs/plans/completed/4-audit_1_3_26.md:13` → `../audit_1_3_26.md`
  should be `../../completed/audit_1_3_26.md` (note: the review's own
  suggested path `../completed/…` was wrong — it resolves back into
  `specs/plans/completed/`).
Paths only; no prose changes. Verify each repaired link resolves from its
file's directory.

**E2 (Minor) — "Superpowers vunknown" footer.**
`skills/brainstorming/scripts/server.cjs:201-218` probes
`<repo-root>/package.json` / `.codex-plugin/plugin.json` (upstream plugin
layout; neither exists here), so `brandMarkup()` (:228-232) always renders
"Superpowers vunknown".
Fix: drop the version probe and render the attribution link without a
version string (keeping the github.com/obra/superpowers link NOTICE
documents). Remove `readSuperpowersVersion` if nothing else uses it.

**E3 (Minor) — `.sdd/` guard is single-point-of-failure.**
Root `.gitignore` has no `.sdd/` entry; exclusion rests entirely on the
generated `.sdd/.gitignore` (`*`), which `git clean` or stray deletion can
remove — surfacing ~65 briefs/reports/diffs to a `git add -A`.
Fix: add `.sdd/` to the root `.gitignore` with a comment noting it
deliberately duplicates the workspace's self-ignoring guard.

## Out of scope (conscious exclusions)

- Pruning stale `.sdd/` artifacts from completed plans — observation only;
  no protocol change (YAGNI).
- Any change to `commands/deferred.md` — the B4 hole is protocol-side.
- The review's two gap proposals (`track-model-experiments`,
  `tune-hyperparameters`) — separate upcoming spec(s).

## Verification

- Both lints and all three test suites green (build 15+new, recommend-
  probabilistic-model 10, recommend-visualization 29).
- A1/A2 repro scripts pass on the corrected text (scratchpad, `uv run`,
  never committed).
- B1/B2 micro-tests: reworded descriptions correctly load the skill for
  trigger phrases and stay quiet for the carve-outs, against a control.
- B4 fixture rep passes (old item ticked by a nothing-deferred plan).
- Link-resolution check over the four E1 files passes.
- Repo-wide grep: no remaining "separate session" / checkpoint claims
  about executing-plans outside historical archives.
