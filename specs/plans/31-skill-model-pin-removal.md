# Skill Model-Pin Removal Implementation Plan

**Status: COMPLETE (2026-09-28)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Execution mode chosen at the 2026-09-28 handoff: SUBAGENT-DRIVEN.** Use the
> **subagent-driven-development** skill: a fresh implementer per task, the task review
> between tasks, and the final whole-branch review. Do not re-ask the execution mode.

> **Where this runs.** This plan exists only on branch `fix/skill-model-pin-removal`
> (cut from `main` at `d49c9fa`; not pushed), checked out in the worktree
> `/Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal`.
> Execute there. A session opened in the main checkout will not find this file, and
> `EnterWorktree` bases on `origin/main`, which does not have it either. `~/.claude/skills/*`
> resolve to the main checkout, so Task 2's `writing-skills` edit does not reach the live
> skill until merge.

**Goal:** Remove the four inert `model: haiku` skill pins, make `build/check_frontmatter.py` fail a Haiku skill or command model so they cannot come back, correct the two documents that say such pins work, and close deferred item 11.

**Architecture:** Task 1 is one red→green cycle across the lint, its tests and the four skills: the new tests fail; the rule makes them pass and turns `test_real_repo_is_clean` red on the four real pins; deleting the pins turns it green. Task 2 corrects two documents as a content task gated on the repo's lints. The completion protocol ticks item 11 and retires the plan and the spec.

**Tech Stack:** Python 3.13 through `uv run` with inline deps; PyYAML; pytest; Markdown. There is no CI — the gates are the lints in the root `CLAUDE.md` Commands block.

**Spec:** `specs/skill-model-pin-removal.md` (approved 2026-09-28; the completion protocol moves it to `specs/completed/`). R1–R5 and "Decision 3" below point into it.

## Global Constraints

Every task's requirements implicitly include this section.

- **The rejected set (R2):** a `SKILL.md` (`check_skill`) or a `commands/*.md` (`check_command_file`) whose `model:` is `haiku` or any `claude-haiku-*` model ID, compared case-insensitively. `agents/*.md` are not checked by this rule — subagent Haiku pins work, and `agents/explore.md` and `agents/test-runner.md` carry `model: haiku` and must stay clean.
- **What stays allowed (Decision 3):** `model: opus`, `sonnet` and `fable`, and every other value outside the rejected set.
- **Owner-approved tests beyond R3's list (2026-09-28 handoff):** `test_haiku_model_match_ignores_case` (R2's case-insensitivity, which no R3 bullet tests) and `test_models_auto_mode_can_run_stay_allowed` (Decision 3) are kept. The suite grows by +5, not the +4 R3's bullets alone would give. Reviewers: this is approved scope, not scope creep.
- **The message (R2)** states that auto mode drops a Haiku skill or command model and keeps the session model, says to put cheap work on a model-pinned subagent instead, and names the spec as `specs/completed/skill-model-pin-removal.md`. That is where the completion protocol moves the spec on this same branch, so the path is right from the merge on; `hooks/readonly-agent-guard.py:12` cited its own spec at the `completed/` path from its first commit (`3a799f4`) the same way. Do not "fix" it to `specs/…` during execution.
- **The constant (R2)** is a module constant beside `CONTEXT_VALUES`, with a comment giving the same "silently no-ops at runtime" rationale.
- **R4's `writing-skills` edit is reference content:** no behavioural micro-test (spec R4; the writing-skills checklist marks the wording micro-test "N/A for pure reference skills"). Line 103 is a local addition — `5572236` (plan 12's C6) wrote it and `9a8575c` added its `context` clause — not superpowers text, and neither commit touched `NOTICE`. `NOTICE` is unaffected.
- **Scope fence — do not touch** (spec "Out of scope"): the two `effort: xhigh` skill pins (`bayesian-workflow`, `tune-hyperparameters`); any `agents/*.md`; any `context: fork` routing; the owner's `~/.claude/CLAUDE.md`; any `description:` frontmatter (an edit there triggers writing-skills' micro-test protocol).
- **`specs/deferred_items.md` is completion-only.** Tasks 1–2 do not touch it; the completion protocol ticks item 11. Never edit the existing `## Aged-backlog acknowledgements` entries that name item 11 — they are history. (finishing-a-development-branch may append a new entry there later; appending is not editing.)
- **Python style** (`CLAUDE.md`, `rules/clean-code-python.md`): single quotes — double only around a string that itself contains single quotes, as `test_check_frontmatter.py` already does; 4-space indent, matching `check_frontmatter.py`; `'''` docstrings.
- **Test commands are directory-scoped.** Run `build/` tests from inside `build/`, never the repo root. The commands below `cd` to absolute worktree paths so the shell's working directory cannot drift between steps; if you execute from a different worktree, substitute its path.
- **Counts are deltas.** Task 1 Step 1 records what your own runs report. Every expected count in this plan is relative to that baseline; the plan never quotes an absolute pytest total.
- **Anchor on text, not line numbers.** Line numbers are as of `d49c9fa`, for orientation only. Every edit gives the exact old text to replace.
- **Never regress an existing test.** Everything green at the baseline stays green at every commit.

---

## File Structure

| File | Responsibility | Task |
|---|---|---|
| `build/check_frontmatter.py` | The frontmatter lint. Gains `AUTO_MODE_DROPPED_MODEL_RE` beside `CONTEXT_VALUES` and a private `_check_model_pin`, called from `check_skill` and `check_command_file`. | 1 |
| `build/test_check_frontmatter.py` | Lint tests. +5 tests; the `test_model_and_effort_keys_allowed` fixture moves from `haiku` to `sonnet`. | 1 |
| `skills/bls-data-context/SKILL.md`, `skills/classification-codes/SKILL.md`, `skills/explore-data/SKILL.md`, `skills/geographic-codes/SKILL.md` | Each loses its single frontmatter line `model: haiku`; nothing else changes (R1). | 1 |
| `CLAUDE.md` | The `# Full build-directory tests` comment carries per-suite counts; six of its figures rise by 5. | 1 |
| `skills/writing-skills/SKILL.md` | Line 103 gains the auto-mode caveat. | 2 |
| `specs/claude-code-customization-guide.md` | Row 82 (`model` / `effort`) gains a ⚠ note. | 2 |
| `specs/deferred_items.md` | Item 11's open sub-item is ticked. **Completion protocol only.** | — |
| `specs/skill-model-pin-removal.md` | Marked complete and moved to `specs/completed/`. **Completion protocol only.** | — |

No new files, and none is split — `check_frontmatter.py` grows by 18 lines.

---

### Task 1: Fail a Haiku skill or command model, and remove the four pins (R1–R3)

Auto mode drops a skill or command `model` it cannot run and keeps the session model, and it cannot run Haiku: the spec's transcript sweep found 0 of 26 pinned-skill loads served by Haiku. This task makes the lint fail such a pin and deletes the four that exist. The rule and the pin removal belong to one task because the rule turns the repo red until the pins are gone. That red is the spec's intended RED step (R3); observe it, never commit it.

**Files:**
- Modify: `build/check_frontmatter.py` (a constant after `CONTEXT_VALUES`, currently line 30; a helper just above `check_skill`, currently line 54; one call in `check_skill`, one in `check_command_file`)
- Modify: `build/test_check_frontmatter.py` (the `test_model_and_effort_keys_allowed` fixture, currently lines 164–170, and five new tests directly after it)
- Modify: `skills/bls-data-context/SKILL.md:17`, `skills/classification-codes/SKILL.md:17`, `skills/explore-data/SKILL.md:16`, `skills/geographic-codes/SKILL.md:17`
- Modify: `CLAUDE.md` (the `# Full build-directory tests` comment block, currently lines 87–94)

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces:
  - `AUTO_MODE_DROPPED_MODEL_RE` — a module-level compiled `re.Pattern` with `re.IGNORECASE`, always applied as `.fullmatch(str(model))`.
  - `_check_model_pin(md: Path, fm: dict) -> list[str]` — private; returns `[]`, or exactly one message beginning `f'{md}: model {model!r} is inert: '`.
  - The rule itself. Task 2's new `writing-skills` wording says "the lint fails a Haiku `model`", which is true only once this task has landed.

- [x] **Step 1: Record the baseline**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_frontmatter.py | tail -1
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal/build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q --collect-only | tail -1
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal && uv run --python 3.13 --with pyyaml python build/check_frontmatter.py; echo "exit=$?"
```

Expected: the frontmatter suite reports only `passed` — write that count down, it is the baseline for Steps 3, 5 and 7; the build directory reports a `collected` total — the baseline for Step 8; the lint prints nothing and `exit=0`.

- [x] **Step 2: Write the failing tests**

In `build/test_check_frontmatter.py`, replace exactly this function:

```python
def test_model_and_effort_keys_allowed(tmp_path):
    d = make_skill(
        tmp_path,
        'pinned-skill',
        'name: pinned-skill\ndescription: Use when testing pins.\nmodel: haiku\neffort: xhigh',
    )
    assert check_skill(d) == []
```

with this — the same function on `sonnet`, so it keeps testing that the keys are allowed (R3), followed by five new tests:

```python
def test_model_and_effort_keys_allowed(tmp_path):
    d = make_skill(
        tmp_path,
        'pinned-skill',
        'name: pinned-skill\ndescription: Use when testing pins.\nmodel: sonnet\neffort: xhigh',
    )
    assert check_skill(d) == []


def test_haiku_model_on_a_skill_is_rejected(tmp_path):
    # Auto mode drops a skill `model` it cannot run and keeps the session model,
    # so the pin is inert (specs/completed/skill-model-pin-removal.md).
    d = make_skill(
        tmp_path,
        'haiku-skill',
        'name: haiku-skill\ndescription: Use when testing pins.\nmodel: haiku',
    )
    errs = check_skill(d)
    assert len(errs) == 1, errs
    msg = errs[0]
    assert msg.startswith(f"{d / 'SKILL.md'}: model 'haiku' ")
    assert 'auto mode drops a Haiku skill or command model and keeps the session model' in msg
    assert 'model-pinned subagent' in msg
    assert 'specs/completed/skill-model-pin-removal.md' in msg


def test_haiku_model_id_on_a_skill_is_rejected(tmp_path):
    d = make_skill(
        tmp_path,
        'haiku-id-skill',
        'name: haiku-id-skill\ndescription: Use when testing pins.\nmodel: claude-haiku-4-5-20251001',
    )
    errs = check_skill(d)
    assert len(errs) == 1 and 'auto mode drops' in errs[0], errs


def test_haiku_model_on_a_command_is_rejected(tmp_path):
    md = tmp_path / 'cheap-command.md'
    md.write_text(
        '---\ndescription: Does a thing.\ndisable-model-invocation: true\nmodel: haiku\n---\nbody\n'
    )
    errs = check_command_file(md)
    assert len(errs) == 1 and 'auto mode drops' in errs[0], errs


def test_haiku_model_match_ignores_case(tmp_path):
    # The alias and the model-ID prefix are both compared case-insensitively.
    for i, model in enumerate(['Haiku', 'CLAUDE-HAIKU-4-5-20251001']):
        d = make_skill(
            tmp_path,
            f'case-{i}',
            f'name: case-{i}\ndescription: Use when testing pins.\nmodel: {model}',
        )
        errs = check_skill(d)
        assert len(errs) == 1 and 'auto mode drops' in errs[0], (model, errs)


def test_models_auto_mode_can_run_stay_allowed(tmp_path):
    # Only a model auto mode cannot run is rejected. This guard passes before the
    # Haiku rule exists, too; it fails only if the rule matches too much.
    for i, model in enumerate(['sonnet', 'opus', 'fable', 'claude-sonnet-5']):
        d = make_skill(
            tmp_path,
            f'runnable-{i}',
            f'name: runnable-{i}\ndescription: Use when testing pins.\nmodel: {model}',
        )
        assert check_skill(d) == [], model
```

The fixtures are complete on purpose: each skill fixture's `name` matches its directory and carries a `description`, and the command fixture carries `description` and `disable-model-invocation: true`. Drop any of those and `check_skill` / `check_command_file` add a second error, so `len(errs) == 1` fails even with a correct rule.

Coverage, spec clause → test:

| Clause | Test |
|---|---|
| R3: a skill with `model: haiku` fails with the R2 message | `test_haiku_model_on_a_skill_is_rejected` — checks the path and value, then each of the message's three required parts |
| R3: a skill with `model: claude-haiku-4-5-20251001` fails | `test_haiku_model_id_on_a_skill_is_rejected` |
| R3: a command file with `model: haiku` fails | `test_haiku_model_on_a_command_is_rejected` |
| R2: "compared case-insensitively" — no R3 bullet tests it, so an exact-string rule would pass everything else | `test_haiku_model_match_ignores_case` |
| R3: a skill with `model: sonnet` passes; Decision 3: `opus` and `fable` stay allowed | `test_models_auto_mode_can_run_stay_allowed` |
| R3: the existing fixture moves from `haiku` to `sonnet` | `test_model_and_effort_keys_allowed` |

- [x] **Step 3: Run the tests to verify they fail**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_frontmatter.py
```

Expected: `4 failed`, and `passed` = your Step 1 count + 1. The four failures are exactly:

```text
FAILED test_check_frontmatter.py::test_haiku_model_on_a_skill_is_rejected
FAILED test_check_frontmatter.py::test_haiku_model_id_on_a_skill_is_rejected
FAILED test_check_frontmatter.py::test_haiku_model_on_a_command_is_rejected
FAILED test_check_frontmatter.py::test_haiku_model_match_ignores_case
```

Read each failure. Every one must be `assert 0 == 1` with `where 0 = len([])` — the check returned no error because the rule does not exist yet. Any other reason (a second error such as `missing description`, a `NameError`) means a broken fixture: fix the test before going on and record a `> Deviation:`.

Two tests pass here **by design**, and neither is vacuous: `test_models_auto_mode_can_run_stay_allowed` guards against a rule that matches too much, so it passes before and after the rule; `test_model_and_effort_keys_allowed` now uses `sonnet`.

- [x] **Step 4: Implement the rule (R2)**

In `build/check_frontmatter.py`, (a) directly after the line `CONTEXT_VALUES = frozenset({'fork'})`, add:

```python
# A skill or command `model:` that auto mode cannot run: the bare `haiku` alias
# or any claude-haiku-* model ID, matched whole and case-insensitively. Auto
# mode drops such a model and the turn keeps the session model, so the pin
# silently no-ops at runtime; it fails here instead. agents/*.md are not checked
# — a subagent's Haiku pin does apply. See specs/completed/skill-model-pin-removal.md.
AUTO_MODE_DROPPED_MODEL_RE = re.compile(r'haiku|claude-haiku-.+', re.IGNORECASE)
```

`.fullmatch` anchors the whole alternation: the value must be exactly `haiku`, or `claude-haiku-` followed by at least one character, in any case. A value that merely contains "haiku" elsewhere does not match — that is the spec's set, no wider.

(b) Between the `TICK_PATH_RE = re.compile(...)` line — the last module-level constant — and `def check_skill(skill_dir: Path) -> list[str]:`, add (keeping two blank lines on each side):

```python
def _check_model_pin(md: Path, fm: dict) -> list[str]:
    '''Fail a skill or command `model:` that auto mode drops (AUTO_MODE_DROPPED_MODEL_RE).'''
    model = fm.get('model')
    if model is None or not AUTO_MODE_DROPPED_MODEL_RE.fullmatch(str(model)):
        return []
    return [f'{md}: model {model!r} is inert: auto mode drops a Haiku skill or command '
            'model and keeps the session model; put cheap work on a model-pinned '
            'subagent instead (specs/completed/skill-model-pin-removal.md)']
```

(c) In `check_skill`, replace exactly:

```python
        errs.append(f'{sk}: context must be one of {sorted(CONTEXT_VALUES)}, got {ctx!r}')
    for key in fm:
```

with:

```python
        errs.append(f'{sk}: context must be one of {sorted(CONTEXT_VALUES)}, got {ctx!r}')
    errs += _check_model_pin(sk, fm)
    for key in fm:
```

(d) In `check_command_file`, replace exactly:

```python
        errs.append(f'{md}: disable-model-invocation must be the YAML boolean true')
    return errs
```

with:

```python
        errs.append(f'{md}: disable-model-invocation must be the YAML boolean true')
    errs += _check_model_pin(md, fm)
    return errs
```

`check_agent_file` is not touched — that is the agent exemption.

- [x] **Step 5: Run the tests — the real repo must now go red**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_frontmatter.py
```

Expected: `1 failed`, and `passed` = your Step 1 count + 4:

```text
FAILED test_check_frontmatter.py::test_real_repo_is_clean - AssertionError: [...
```

with the assertion reporting `Left contains 4 more items` — one message per pinned skill. This is the spec's intended RED step (R3), not a regression. `test_real_agents_and_commands_are_clean` passes: agents are not checked, and no command carries `model:`.

Confirm with the lint itself:

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal && uv run --python 3.13 --with pyyaml python build/check_frontmatter.py; echo "exit=$?"
```

Expected: exactly these four lines — each path prefixed by the absolute worktree root, shown here as `…` — then `exit=1`:

```text
…/skills/bls-data-context/SKILL.md: model 'haiku' is inert: auto mode drops a Haiku skill or command model and keeps the session model; put cheap work on a model-pinned subagent instead (specs/completed/skill-model-pin-removal.md)
…/skills/classification-codes/SKILL.md: model 'haiku' is inert: auto mode drops a Haiku skill or command model and keeps the session model; put cheap work on a model-pinned subagent instead (specs/completed/skill-model-pin-removal.md)
…/skills/explore-data/SKILL.md: model 'haiku' is inert: auto mode drops a Haiku skill or command model and keeps the session model; put cheap work on a model-pinned subagent instead (specs/completed/skill-model-pin-removal.md)
…/skills/geographic-codes/SKILL.md: model 'haiku' is inert: auto mode drops a Haiku skill or command model and keeps the session model; put cheap work on a model-pinned subagent instead (specs/completed/skill-model-pin-removal.md)
```

Do not commit in this state.

- [x] **Step 6: Delete the four pins (R1)**

First confirm each file carries exactly one pin:

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal && grep -c 'model: haiku' skills/bls-data-context/SKILL.md skills/classification-codes/SKILL.md skills/explore-data/SKILL.md skills/geographic-codes/SKILL.md
```

Expected: each of the four paths followed by `:1`.

In each of the four files the pin sits between the same two frontmatter lines. In each file, replace exactly this text:

```text
license: MIT
model: haiku
metadata:
```

with exactly this text:

```text
license: MIT
metadata:
```

Nothing else in these files changes: no skill body refers to its own model tier (R1).

- [x] **Step 7: Run every gate — green**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_check_frontmatter.py | tail -1
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal && uv run --python 3.13 --with pyyaml python build/check_frontmatter.py; echo "exit=$?"
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal && grep -rn '^model: haiku' skills/*/SKILL.md commands/*.md; echo "exit=$?"
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal && uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py --check; echo "exit=$?"
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal && uv run --python 3.13 python build/check_provenance.py; echo "exit=$?"
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal && uv run --python 3.13 python build/check_snippets.py skills/; echo "exit=$?"
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies | tail -1
```

Expected, in order:
- the suite reports only `passed`, = your Step 1 count + 5;
- the lint prints nothing, `exit=0`;
- the spec's grep prints nothing and `exit=1` — for `grep`, exit 1 means "no match", which is the pass condition here;
- `sync_runtime_assets.py --check`, `exit=0` (skills are not adapter inputs; this guards against an accidental agent edit);
- `check_provenance.py`, `exit=0`;
- `check_snippets.py` Tier 1, `exit=0` (any `WARN` lines on stderr are advisory);
- the dependency-drift check reports `1 passed` (every other test in the file is deselected).

- [x] **Step 8: Sync the build-directory counts in `CLAUDE.md`**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal/build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q --collect-only | tail -1
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal/build && uv run --python 3.13 --with pytest --with numpy --with polars --with pyyaml python -m pytest -q | tail -1
```

Expected: `collected` = your Step 1 build-directory total + 5. The full run reports `4 failed, N passed, 8 skipped`. Those 4 failures and 1 of the skips are `test_verify_citations.py`'s tests that need the gitignored `build/.scratch/`, which a worktree lacks; the other 7 skips are `test_check_snippets.py`'s ArviZ-chain tests. All are pre-existing and documented in the block you are about to edit.

Now edit the `# Full build-directory tests` comment in `CLAUDE.md` (currently lines 87–94). The five tests added here need neither `build/.scratch/` nor the ArviZ chain, so add 5 to exactly these six figures and to nothing else:
- the directory total, three times — in `— … tests (`, in `(all … collect either way`, and in `to run all ….`;
- the subtotal in `(… citation/lint/snippet +`;
- the pass count in `reports … passed, 7 skipped` (the `.scratch/`-present run);
- the pass count in `lacking both: … passed, 4 failed, 8 skipped`.

Leave unchanged: `62 runtime-support`, `7 of test_check_snippets.py's`, the `7 skipped`, `5 in test_verify_citations.py`, and `4 failed, 8 skipped`.

Check the edit against your own runs, not against arithmetic alone: the new directory total equals the `collected` count you just saw; the new lacking-both pass count equals the `N passed` your full run just reported; and the `.scratch/`-present pass count + 7 equals the new directory total.

> Deviation: at the completion gate (2026-09-28) the owner had the final review's two
> Minors fixed in `d5638ec`: a sixth test, `test_haiku_model_on_an_agent_is_allowed`, pins
> the agent exemption with a synthetic fixture, and `check_frontmatter.py`'s docstring now
> names the context and model checks. The suite grew by +6, not +5, so these six figures
> now read 145 (three times), 83, 138 and 133.

- [x] **Step 9: Commit**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal && git add build/check_frontmatter.py build/test_check_frontmatter.py skills/bls-data-context/SKILL.md skills/classification-codes/SKILL.md skills/explore-data/SKILL.md skills/geographic-codes/SKILL.md CLAUDE.md
git commit -m "fix(skills): remove the inert model: haiku pins and fail them in the lint"
```

---

### Task 2: Correct the two documents that say a Haiku skill pin works (R4)

`skills/writing-skills/SKILL.md:103` presents `model` as a per-skill model override with no caveat — the wording plan 11 relied on when it shipped the pins — and the customization guide's frontmatter table says the same. This is a content task, not a code task, so the red→green cycle takes the form plan 12's C6 task used on this same line: capture the before-state, apply the exact edit, re-run, confirm the change, and pass the lints.

**Files:**
- Modify: `skills/writing-skills/SKILL.md:103` (inside the "Optional keys the lint accepts" bullet)
- Modify: `specs/claude-code-customization-guide.md:82` (the `model` / `effort` row of the Skills "Frontmatter reference ⚠" table)

**Interfaces:**
- Consumes: Task 1's rule. The new `writing-skills` wording says "the lint fails a Haiku `model`", and line 103 opens "Optional keys the lint accepts", so without that clause the line would misstate the lint once Task 1 lands. Run this task after Task 1.
- Produces: nothing consumed by code.

**REQUIRED SKILL:** writing-skills — this is an edit to a skill. Per spec R4 it is reference content, so the wording micro-test does not apply; the gates in Step 5 do. Do not touch the skill's `description:`.

- [x] **Step 1: Confirm the provenance claim**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal && git log --format='%h %ad %s' --date=short -S 'the two delegation keys' -- skills/writing-skills/SKILL.md
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal && git log --format='%h %ad %s' --date=short -S 'sole value `fork`' -- skills/writing-skills/SKILL.md
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal && git show --stat --format='%h %s' 5572236 9a8575c | grep -c NOTICE
```

Expected: `5572236 2026-07-20 docs(writing-skills): scope the 1024-char cap to description (C6)`; then `9a8575c 2026-09-04 feat(tech-debt): run the audit forked in an isolated subagent`; then `0`. Both are local additions that left `NOTICE` alone, so this edit leaves it alone too. If either log names a different commit, stop and ask: the line's provenance is not what the spec recorded.

- [x] **Step 2: Capture the before-state**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal && grep -c 'silently dropped' skills/writing-skills/SKILL.md; grep -c 'observed on 2.1.219' specs/claude-code-customization-guide.md
```

Expected: `0` and `0`.

- [x] **Step 3: Correct `writing-skills`**

In `skills/writing-skills/SKILL.md`, replace exactly this text (it occurs once, in line 103):

```text
(per-skill overrides for the model tier and reasoning effort a skill runs at)
```

with exactly this text:

```text
(per-skill overrides for the model tier and reasoning effort a skill runs at; a `model` the session's permission mode cannot run — Haiku under auto mode — is silently dropped, so the lint fails a Haiku `model`, and cheap work belongs on a model-pinned subagent)
```

The rest of the line — the `context` clause and "Any other key fails `build/check_frontmatter.py`." — is unchanged.

- [x] **Step 4: Correct the customization guide**

In `specs/claude-code-customization-guide.md`, replace exactly this row:

```text
| `model` / `effort` | Per-skill model and reasoning-effort override (respects `availableModels`) |
```

with exactly this row:

```text
| `model` / `effort` | Per-skill model and reasoning-effort override (respects `availableModels`). In auto mode, a skill `model` that auto mode does not support (Haiku) is ignored and the session model runs — observed on 2.1.219–2.1.281 ⚠ |
```

The guide's header defines ⚠ as "most version-sensitive — confirm against your installed version", which is why the observed version range rides with it. The new text contains no `|`, so the row stays two cells. The subagent table further down (its own `model` row lists `haiku` as a value) is correct — subagent pins work — and is not touched.

- [x] **Step 5: Gate**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal && grep -c 'silently dropped' skills/writing-skills/SKILL.md; grep -c 'observed on 2.1.219' specs/claude-code-customization-guide.md
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal && grep '^| `model` / `effort` |' specs/claude-code-customization-guide.md | tr -cd '|' | wc -c
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal && uv run --python 3.13 --with pyyaml python build/check_frontmatter.py; echo "exit=$?"
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal && uv run --python 3.13 python build/check_provenance.py; echo "exit=$?"
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal && uv run --python 3.13 python build/check_snippets.py skills/; echo "exit=$?"
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal/build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies | tail -1
```

Expected: `1` and `1`; `3` (the row keeps exactly three pipes, i.e. two cells); then `exit=0` three times; then `1 passed`. The new wording names no other skill, no skill's section, and no `references/` or `scripts/` path, so the drift check and the lint's path check have nothing new to match.

- [x] **Step 6: Commit**

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal && git add skills/writing-skills/SKILL.md specs/claude-code-customization-guide.md
git commit -m "docs(writing-skills): say auto mode drops a Haiku skill model"
```

---

## Plan completion (R5)

Run writing-plans' Plan Completion Protocol after Tasks 1–2 and the final review. The protocol supplies the steps; this section adds what is specific to this plan.

**Step 1, the gate — one named question.** Add this to the batch; do not decide it yourself:

> The spec's "Out of scope" records a watch condition for the two `effort: xhigh` skill pins
> (`bayesian-workflow`, `tune-hyperparameters`): *"Revisit if: the session default moves off
> xhigh, or a skill turn is seen running at a lower effort than its session because of a
> pin."* Once the spec retires, `/deferred` no longer sees it. Record it in
> `specs/deferred_items.md` as a watch item (`Size: quick-fix`, with that `Revisit if:`), or
> let it retire with the spec?

**Step 3, deferred items — tick item 11 (R5).** Before editing, record the file-wide open count:

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal && grep -c '^- \[ \]' specs/deferred_items.md
```

Anchor the tick on the checkbox line itself. Anchoring it on the item's last lines appends the note and silently leaves `- [ ]` in place. Under `## 11-delegation-frontmatter-rollout — 2026-07-19`, replace exactly:

```text
- [ ] Interactive verification (plan Task 5 Steps 3–4, deviation): confirm the live
```

with:

```text
- [x] Interactive verification (plan Task 5 Steps 3–4, deviation): confirm the live
```

Then, directly after that item's last continuation line —

```text
      tail, so the finishing-a-development-branch merge/PR gate stays bound.
```

— insert these lines, which keep the item's 6-space continuation indent:

```text
      → done in plan 31: superseded, not run. The 2026-09-28 transcript sweep answered
      the question this check asked — 0 of 26 informative pinned-skill loads ran on
      Haiku, because auto mode drops a Haiku skill model and keeps the session model.
      Plan 31 removed the four pins and made build/check_frontmatter.py fail a Haiku
      skill or command model; the two `effort: xhigh` pins stay (the spec's "Out of
      scope"). See specs/completed/skill-model-pin-removal.md.
```

Verify by count, not by reading the diff:

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal && sed -n '/^## 11-delegation-frontmatter-rollout/,/^## 12-audit_7_20_26/p' specs/deferred_items.md | grep -c '^- \[ \]'
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal && grep -c '^- \[ \]' specs/deferred_items.md
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal && grep -n '^## 11-delegation-frontmatter-rollout' specs/deferred_items.md; git diff -U0 specs/deferred_items.md | grep '^@@'
```

Expected: `0` for item 11's section; the file-wide count equals your recorded count − 1 + the number of items the gate appended; and every hunk's `@@ -N` start line is at or below the `## 11-delegation-frontmatter-rollout` header line (plus any appended section at the file's end) — nothing in `## Aged-backlog acknowledgements` changed.

**Step 5, retire — the spec retires with the plan.** This plan is the spec's only plan. In the one `chore(specs): retire plan 31` commit:
- `git mv specs/plans/31-skill-model-pin-removal.md specs/plans/completed/`
- `git mv specs/skill-model-pin-removal.md specs/completed/`, and mark it complete at the top: replace exactly `**Status: APPROVED (2026-09-28)** — design approved in a brainstorming pass opened by the` with `**Status: COMPLETE (<today's date, YYYY-MM-DD>)** — implemented by plan 31 (`specs/plans/completed/31-skill-model-pin-removal.md`) and retired here. Design approved 2026-09-28 in a brainstorming pass opened by the`.
- Neither file carries a relative markdown link, so nothing needs re-pointing.

After that commit, confirm the lint's citation resolves:

```bash
cd /Users/lowell/Projects/agent-skills/.claude/worktrees/plan-31-skill-model-pin-removal && ls specs/completed/skill-model-pin-removal.md && grep -c 'specs/completed/skill-model-pin-removal.md' build/check_frontmatter.py
```

Expected: the path, then `2` (the constant's comment and the message).

**Integration.** Then finishing-a-development-branch. This branch was cut from `main` at `d49c9fa`; re-read `git merge-base` at that point, since `main` moves.
