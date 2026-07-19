# Delegation-frontmatter Rollout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `model`/`effort` delegation frontmatter to the compute-heavy skills and the reviewer agents, and give the mechanical data skills a Haiku path, so a Sonnet-default session escalates *by structure* (the skill invoked) instead of by per-prompt guessing.

**Architecture:** Pure frontmatter edits plus one lint change. First extend the skill-frontmatter lint to accept the two new keys (blocking prereq, TDD); then apply effort pins to the heavy-reasoning skills, `model: haiku` pins to the data skills, and an effort pin to the whole-branch reviewer. No new files, scripts, agents, or dependencies.

**Tech Stack:** Claude Code skill/subagent frontmatter (`model`, `effort`); Python 3.13 lint (`build/check_frontmatter.py`) run via `uv`; pytest.

## Context — read this, skip the archaeology

This plan implements `specs/delegation-frontmatter-rollout.md`. Two things that spec left to "verify/decide" are **already resolved** — do not re-litigate:

**Prereq A (field support) — VERIFIED** against the official docs (code.claude.com/docs/en/skills and /sub-agents) via the claude-code-guide agent, 2026-07-19. Every field this plan uses is valid and honored on the installed v2.1.x:

| Field | Valid & honored | Semantics |
|---|---|---|
| skill `model` | yes | overrides the model **for the current turn**; session model resumes next prompt. Values: `haiku`/`sonnet`/`opus`/full-id/`inherit`. |
| skill `effort` | yes | overrides session effort **while the skill runs**. Values: `low`/`medium`/`high`/`xhigh`/`max`. |
| agent `effort` | yes | honored like agent `model`; same values. |
| Explore model | confirmed | **inherits the session model** (capped Opus) as of v2.1.198 — it is no longer always-Haiku. |

Consequence of the last row: forking the data skills to `agent: Explore` would run them on the **session** model (Sonnet), not Haiku — so this plan pins `model: haiku` directly (Req 5's chosen path). The skill `model` override being *per-turn* means the saving is scoped to the invoking turn; that is acceptable for short profiling/lookup bodies. Whole-workflow Haiku isolation (a fork to a haiku-pinned agent) is the documented deferred upgrade, out of scope here.

**Two decisions — LOCKED** (each a reversible one-liner; flip before execution if desired):
1. **`bayesian-workflow`: `effort: xhigh`, no `model` pin.** It runs in its own fresh session (commit `af4b252`) where the user already picks the model; a `model: opus` pin would override that deliberate choice. Effort composes with whatever model they chose. (The opus pin is a documented opt-in, not taken.)
2. **`task-reviewer`: no `effort` pin.** SDD's Model Selection dispatches reviews at a model tier that **scales with the diff** per-dispatch (small mechanical → sonnet, risky/subtle → opus; final whole-branch → opus). Its `model: sonnet` is a *floor* the controller overrides per dispatch. A fixed `effort` pin would fight that scale-with-diff policy, so effort likewise stays per-dispatch — documented with a comment only.

`recommend-probabilistic-model` and `recommend-visualization` are **deliberately unchanged**: they are advisory routers ("recommend, don't fit") and should stay cheap; `high` is already the session-default effort on Sonnet 5 / Opus 4.8, so an `effort: high` pin would be a no-op most of the time. Left `inherit` (documented opt-in).

## Global Constraints

- **Effort before model.** Prefer `effort` pins; reserve `model` pins for the mechanical-Haiku case. A frontmatter pin is a *structural* router (route by task structure) — never the banned per-prompt model self-assessment.
- **Haiku has no `effort` parameter** — never add `effort` to a `model: haiku` skill.
- **Frontmatter values are dispatch aliases** (`haiku`/`sonnet`/`opus`/`inherit`), not version IDs.
- **Lint gate:** `build/check_frontmatter.py:22` `ALLOWED_KEYS` must contain every *skill* frontmatter key or the lint (and `test_real_repo_is_clean`) fails; **agent** files are not key-checked (only name/description/tools). Both `check_frontmatter.py` and `check_provenance.py` must exit 0, and the full `build/` pytest suite must pass.
- **Python style** (lint/test edits): single quotes, 4-space indent, Python 3.13. Run everything through `uv run --python 3.13 --with …` from inside `build/` (no repo-wide interpreter).
- **Cross-skill references stay bare skill names.** No new third-party code; no new skill or agent, so **no `NOTICE`/`README` rows** are added.
- **Commit per task**, conventional-commit style; end each commit message with the standard `Co-Authored-By:` trailer for the executing model (repo convention).
- **Task ordering:** Task 1 is a blocking prereq for Tasks 2 and 3 (the skill pins fail the lint without it). Task 4 (agents) does not depend on Task 1 but is sequenced after for a clean history.

---

### Task 1: Extend the frontmatter lint to accept `model`/`effort` (blocking prereq)

**Files:**
- Modify: `build/check_frontmatter.py:22`
- Test: `build/test_check_frontmatter.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `ALLOWED_KEYS` now contains `'model'` and `'effort'` — the precondition Tasks 2 and 3 rely on to lint clean.

- [ ] **Step 1: Write the failing test (plus an unknown-key guard)**

Append to `build/test_check_frontmatter.py` (reuses the existing `make_skill` helper):

```python
def test_model_and_effort_keys_allowed(tmp_path):
    d = make_skill(
        tmp_path,
        'pinned-skill',
        'name: pinned-skill\ndescription: Use when testing pins.\nmodel: haiku\neffort: xhigh',
    )
    assert check_skill(d) == []


def test_unknown_frontmatter_key_still_rejected(tmp_path):
    d = make_skill(
        tmp_path,
        'bogus-skill',
        'name: bogus-skill\ndescription: Use when testing.\nbogus-key: nope',
    )
    errs = '\n'.join(check_skill(d))
    assert "unknown frontmatter key 'bogus-key'" in errs
```

- [ ] **Step 2: Run the tests to verify the new-keys test fails**

Run: `cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest test_check_frontmatter.py -q`
Expected: `test_model_and_effort_keys_allowed` **FAILS** — `check_skill` returns `["…/SKILL.md: unknown frontmatter key 'model'", "…: unknown frontmatter key 'effort'"]` instead of `[]`. `test_unknown_frontmatter_key_still_rejected` PASSES (that key is already rejected).

- [ ] **Step 3: Add the two keys to `ALLOWED_KEYS`**

In `build/check_frontmatter.py`, line 22:

```python
ALLOWED_KEYS = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'when_to_use', 'model', 'effort'}
```

- [ ] **Step 4: Run the full build suite to verify green**

Run: `cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q`
Expected: PASS — all tests green, including the two new ones (`test_real_repo_is_clean` still passes; no skill carries `model`/`effort` yet).

- [ ] **Step 5: Commit**

```bash
git add build/check_frontmatter.py build/test_check_frontmatter.py
git commit -m "build(lint): allow model/effort skill frontmatter keys"
```

---

### Task 2: Effort pins on the compute-heavy skills

**Files:**
- Modify: `skills/bayesian-workflow/SKILL.md` (frontmatter)
- Modify: `skills/tune-hyperparameters/SKILL.md` (frontmatter)

**Interfaces:**
- Consumes: Task 1's `ALLOWED_KEYS` extension (`effort` now permitted).
- Produces: both skills bump to `xhigh` effort while active, composing with the session model.

- [ ] **Step 1: Add `effort: xhigh` to `bayesian-workflow`**

In `skills/bayesian-workflow/SKILL.md`, insert the `effort` line after `license: MIT`:

```yaml
license: MIT
effort: xhigh
metadata:
  author: "Alexandre Andorra (https://alexandorra.github.io/)"
  adapted_by: Lowell Mason
  version: "2.0"
```

- [ ] **Step 2: Add `effort: xhigh` to `tune-hyperparameters`**

In `skills/tune-hyperparameters/SKILL.md`, same insertion point:

```yaml
license: MIT
effort: xhigh
metadata:
  author: Lowell Mason
  version: "1.0"
```

- [ ] **Step 3: Run the frontmatter lint to verify clean**

Run: `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py`
Expected: exit 0, no output (both skills lint clean; `effort` is now an allowed key).

- [ ] **Step 4: Commit**

```bash
git add skills/bayesian-workflow/SKILL.md skills/tune-hyperparameters/SKILL.md
git commit -m "feat(skills): pin bayesian-workflow + tune-hyperparameters to xhigh effort"
```

---

### Task 3: Haiku model pins on the mechanical data skills

**Files:**
- Modify: `skills/explore-data/SKILL.md` (frontmatter)
- Modify: `skills/bls-data-context/SKILL.md` (frontmatter)

**Interfaces:**
- Consumes: Task 1's `ALLOWED_KEYS` extension (`model` now permitted).
- Produces: these two skills run their invoking turn on Haiku. **No `effort`** (Haiku has none).

> **Scope note — `validate-data` is deliberately EXCLUDED from the Haiku pin.** It is
> the ship-gate (benchmark reconciliation, methodology/bias, "why doesn't this match
> the official total," silent-fallback detection) — reasoning checks whose whole value
> is catching the subtle problem a weaker model misses, and it is the last line, with
> nothing downstream to catch what it lets through. `explore-data` is safe on Haiku
> because its numbers come from the deterministic bundled `profile.py` and it feeds
> *into* analysis with `validate-data` as the net; `bls-data-context` is reference
> retrieval with facts in-context. `validate-data` stays `inherit`. (See spec Req 5.)

- [ ] **Step 1: Add `model: haiku` to `explore-data`**

In `skills/explore-data/SKILL.md`, insert after `license: MIT`:

```yaml
license: MIT
model: haiku
metadata:
  author: Lowell Mason
  version: "1.0"
```

- [ ] **Step 2: Add `model: haiku` to `bls-data-context`** (same insertion point, identical `metadata` block).

```yaml
license: MIT
model: haiku
metadata:
  author: Lowell Mason
  version: "1.0"
```

- [ ] **Step 3: Run the frontmatter lint to verify clean**

Run: `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py`
Expected: exit 0, no output.

- [ ] **Step 4: Commit**

```bash
git add skills/explore-data/SKILL.md skills/bls-data-context/SKILL.md
git commit -m "feat(skills): pin explore-data + bls-data-context to haiku"
```

---

### Task 4: Reviewer-agent effort

**Files:**
- Modify: `agents/code-reviewer.md` (frontmatter)
- Modify: `agents/task-reviewer.md` (frontmatter comment only)

**Interfaces:**
- Consumes: nothing (agent files are not `ALLOWED_KEYS`-checked).
- Produces: `code-reviewer` reviews at `xhigh` effort; `task-reviewer` documents that effort is intentionally per-dispatch.

- [ ] **Step 1: Add `effort: xhigh` to `code-reviewer`**

In `agents/code-reviewer.md`, add the `effort` line after `model: opus`:

```yaml
tools: Read, Grep, Glob, Bash
model: opus
effort: xhigh
---
```

- [ ] **Step 2: Document the intentional no-effort-pin on `task-reviewer`**

In `agents/task-reviewer.md`, add a comment line directly below the existing `model:` line (YAML `#` comments are ignored by the lint's `yaml.safe_load`):

```yaml
model: sonnet  # task-review floor per subagent-driven-development Model Selection; the controller escalates to opus for risky/subtle diffs via an explicit dispatch override. The final whole-branch review (code-reviewer) stays opus.
# effort: intentionally unpinned — like model, effort follows the per-dispatch tier
# (SDD Model Selection); a fixed pin would fight the scale-with-diff review policy.
```

- [ ] **Step 3: Run the frontmatter lint to verify clean**

Run: `uv run --python 3.13 --with pyyaml python build/check_frontmatter.py`
Expected: exit 0, no output (agent files still pass name/description/tools checks; `effort` and comments are fine).

- [ ] **Step 4: Commit**

```bash
git add agents/code-reviewer.md agents/task-reviewer.md
git commit -m "feat(agents): code-reviewer xhigh effort; document task-reviewer per-dispatch effort"
```

---

### Task 5: Whole-rollout verification sweep

**Files:** none modified — this is the cross-cutting gate.

**Interfaces:**
- Consumes: all prior tasks.
- Produces: confirmation the repo is green and the pins behave.

- [ ] **Step 1: Full build suite + both lints green**

Run:
```bash
cd build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q
cd .. && uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 python build/check_provenance.py
```
Expected: pytest all-pass; both lint scripts exit 0 with no output.

- [ ] **Step 2: Confirm pins are present and descriptions untouched**

Run: `grep -rE '^(model|effort):' skills/*/SKILL.md agents/*.md`
Expected exactly:
```
skills/bayesian-workflow/SKILL.md:effort: xhigh
skills/bls-data-context/SKILL.md:model: haiku
skills/explore-data/SKILL.md:model: haiku
skills/tune-hyperparameters/SKILL.md:effort: xhigh
agents/code-reviewer.md:model: opus
agents/code-reviewer.md:effort: xhigh
agents/task-reviewer.md:model: sonnet  # …
```
(No `model`/`effort` on `validate-data`, `recommend-*`, or the superpowers process
skills — those are intentionally unchanged. `validate-data` in particular stays
`inherit` because it is a judgment-heavy ship-gate, per Task 3's scope note.)

- [ ] **Step 3: Manual behavioral spot-check (interactive; note results, do not block the plan on tooling)**

In an interactive session: invoke `explore-data` (or `/explore-data`) and confirm the model indicator / `/status` shows **haiku** for that turn; invoke `bayesian-workflow` and confirm effort shows **xhigh**. If the environment cannot surface the active model/effort, record that and move on — the lint is the enforceable gate; this is confirmation only.

- [ ] **Step 4: Cost check (method, not a pass/fail gate — and expect modest numbers)**

This rollout is primarily **task-model fit** (right model/effort for the work), not a cost lever. Plan 10's own telemetry put cache-reads at 61% of spend and the top-10 *long* sessions at ~85% — profiling/lookup turns are not the spend center, and the skill `model` override only covers the invoking turn. The effort pins (Tasks 2, 4) are justified on **quality**, not cost. So: optionally record `/status` before/after on one exploration-heavy session and note any drop in the completion writeup, but do not expect (or chase) a large number — the real cost lever remains the session-boundary/`/clear` work from plan 10 and commit `af4b252`.

- [ ] **Step 5: No commit** — nothing changed in this task. Proceed to the Plan Completion Protocol.

## Out of scope / consciously deferred

Log these under the Plan Completion Protocol (`specs/deferred_items.md`) so they are not silently lost:

- **Haiku-pinned `Explore` override agent** (fork-isolation upgrade): would keep a *whole* multi-turn profiling workflow on Haiku (the direct `model: haiku` pin only covers the invoking turn) and double as a global Explore→Haiku lever. Add only if the per-turn saving proves insufficient. Touches `agents/` (a new `Explore.md`).
- **`validate-data` `model: haiku` pin** — deliberately excluded: it is a judgment-heavy ship-gate whose value is catching subtle problems a weaker model misses (Task 3 scope note). Stays `inherit`; revisit only if a cheap bulk-validation need emerges that can be scoped to the mechanical checks alone.
- **`recommend-probabilistic-model` / `recommend-visualization` `effort: high` pins** — decided against (no-op at the default `high`); available opt-in.
- **`bayesian-workflow` `model: opus` pin** — decided against (effort-only, to not override the fresh-session model choice); available opt-in.
- **Settings / `opusplan`** — decided in plan 10 (`opusplan` rejected); not in scope.
- **Custom `advisor` agent** — redundant (`advisorModel: opus` is live); only for a gateway work machine.
