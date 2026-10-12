# Synthesize-Mode Scenario Verification Re-run Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Re-run plan 36's Synthesize-mode scenario verification with its exemplar step isolated, and record B1–B3 verdicts from 5 valid reps. "Isolated" means `references/spec-synthesis.md` now names its two exemplars.

**Architecture:** This is plan 36's mechanism, changed in five places:
1. One sentence of `skills/describe-critique-methodology/references/spec-synthesis.md` names two retired specs as the exemplars. It is this plan's only skill edit. It lands on `main` before the pilot, because reps load skills through `~/.claude/skills/`, which symlinks into the main checkout.
2. The grader counts tool denials by the transcripts' `toolDenialKind` field. The fix is checked against plan 36's archived run: 0 denials before, 24 after.
3. The reps run in fresh repositories under `~/.cache/nfp-notes/`.
4. `run_rep.sh` unsets `LLM_WIKI_ROOT` and allows exactly `printenv LLM_WIKI_ROOT`.
5. The pre-registration adds a guard on the shared checkout, a stopping rule if the pilot is voided by the skill's own procedure, plan 36's rep repositories as a VOID path, and this plan's slug as an injected-context marker.

As in plan 36, the owner launches every rep from a plain terminal, and the executor builds the kit, audits and grades.

**Tech Stack:** Claude Code CLI (`claude -p`, `--session-id`, `--resume`, `--output-format json`, `--permission-mode`, `--allowedTools`); bash; Python 3.13 stdlib for `grade.py`; git.

**Spec:** none. The source is the `specs/deferred_items.md` § `18-methodology-pipeline-skills (plan #1, describe-critique-methodology) — 2026-07-26` item "Synthesize mode still has no scenario verification (successor …; plan 36 ran VOID)", selected at the 2026-10-11 `/deferred` pass. Its closure condition: "a re-run whose exemplar step is isolated yields 5 valid reps and a record under `specs/completed/` with verdicts for B1-B3."

Two documents give the background, and both are worth reading in full first:
- `specs/plans/completed/36-synthesize-mode-scenario-verification.md`, the base mechanism
- `specs/completed/synthesize-mode-verification-2026-10-05.md`, which explains why its run was void

The behaviour under test is specified in `skills/describe-critique-methodology/SKILL.md` § Synthesize mode and in `references/spec-synthesis.md`.

## Global Constraints

- **Channel 5: no rep may start inside this repository's context.** The owner launches every rep as a `claude -p` session from a plain terminal. Its working directory is set to its own scratch repo. Never launch a rep from a Claude Code session, and never from a directory inside `~/Projects/agent-skills`. (Memory `microtest-isolation-channels`, Channel 5: injected `CLAUDE.md` and `gitStatus` are inherited from the session, so no file quarantine can close it.)
- **Nothing a rep can read may contain the answer (Channel 3).** The rep repos hold only the two fixture files and a one-line README. The control directory lives outside every rep repo, under a neutral name.
- **No quarantine of this repository.** Sibling sessions use the main checkout, and a quarantine that isn't applied evenly is itself a tell (Channel 4). Contamination is handled by the pre-registered VOID rule, never by moving files.
- **This plan edits exactly one skill sentence (Task 1).** A behaviour that fails its pass bar is recorded and deferred. Fixing it is a writing-skills RED→GREEN cycle of its own.
- **Task 1 is on `main` before the pilot.** The checkpoint at the end of Task 1 is an owner step, and Task 2 ends by verifying it through `~/.claude/skills/`.
- **Owner steps are explicit and batched:**
  - land Task 1 on `main` (Task 1, Step 5)
  - run `run_pilot.sh` once (Task 3)
  - run `run_batch.sh` once (Task 4)
  - run `run_rep.sh <n>` once per replacement rep (Task 4, and only if reps are void)

  The executor runs everything else.
- **Paths are fixed, and every script refers to them literally:**
  - control directory: `~/.cache/ctl-q9/`, kept because its name is an injected-context marker
  - plan 36's run, archived: `~/.cache/ctl-q9/run-2026-10-05/`
  - rep repos: `~/.cache/nfp-notes/rep-1` … `rep-10`, which are fresh. Plan 36's `~/.cache/nfp-series/` holds its reps' syntheses of this same fixture.
- **Fixture source files, copied byte for byte:**
  - `/Users/lowell/Projects/alt-nfp-model/specs/completed/calibration_methodology.md`
  - `/Users/lowell/Projects/alt-nfp-model/specs/completed/calibration_methodology_review.md`
- **The record goes to `specs/completed/synthesize-mode-verification-<YYYY-MM-DD>.md`.** It follows the house record format of `specs/completed/red-baseline-derive-roadmap-2026-09-08.md`. The 2026-10-05 record stays as it is.
- **Work in a worktree** for Task 1 and Task 5, created with the using-git-worktrees skill.

## Decisions

- **D1** (owner, /deferred pass, 2026-10-11): isolate the exemplar step by naming two exemplars in `spec-synthesis.md`. The VOID rule is not relaxed: reading the skill's own design spec still voids a rep. Applied in: Task 1, Pre-registration.
- **D2** (owner, plan writing, 2026-10-11): the exemplars are `delegation-frontmatter-rollout.md` and `skill-model-pin-removal.md`. They replace `calibration-check-verdicts.md`, which has no Requirements, Verification or Rollout note. Applied in: Task 1.
- **D3** (owner, plan writing, 2026-10-11): `run_rep.sh` unsets `LLM_WIKI_ROOT` and allows exactly `Bash(printenv LLM_WIKI_ROOT)`. A bare `printenv` stays refused, because the whole environment could carry a VOID path. Applied in: Task 2, Pre-registration.
- **D4** (planner default, for plan review, 2026-10-11): do not add `Projects/alt-nfp` (no `-model`) to the VOID list. `~/Projects/alt-nfp` does not exist (checked 2026-10-11), so no read can hit it. Applied in: Pre-registration.
- **D5** (planner default, for plan review, 2026-10-11): add the pre-registration's three new rules: the shared-checkout guard, the pilot redesign trigger, and `.cache/nfp-series` as a VOID path. Applied in: Pre-registration, Tasks 2–4.

## Pre-registration (fixed before any rep runs)

These are plan 36's rules. Each change is marked **(new)** or **(changed)**.

**The three turns.** These are the exact texts, already in `~/.cache/ctl-q9/prompts/` (unchanged):
- T1, the skill's own re-entry utterance from `SKILL.md` Describe step 4: `The critique is back — use describe-critique-methodology (synthesize mode) on specs/calibration_methodology_review.md`
- T2: `Thanks. On every needs-user-adjudication point, go with your recommendation, or with the critique's position where you gave none. Go ahead and finish the spec.`
- T3: `Approved — the spec looks good.`

**Behaviours and how each is scored** (per valid rep; pass/fail):
- **B1: triage before spec text.**
  - M1 (mechanical): the first assistant message with a markdown table that has a verdict column comes before the first write to the new spec file in the transcript. This holds even when both happen in one turn, because a first-pass critique may leave no question to wait on.
  - R1 (manual): above the table, the rep states whether the critique was adjudicated or a first pass.
  - R2 (manual): the table covers every critique point in the coverage key, `~/.cache/ctl-q9/coverage-key.md`, which is frozen at 50 points.
  - R3 (manual): every needs-user-adjudication question is in the table's message, and none is asked in a later message.

  B1 passes when M1, R1, R2 and R3 all hold.
- **B2: locator discipline.**
  - M3 (mechanical): before the Requirements section, the spec names both fixture files.
  - R4 (manual): a Design provenance paragraph declares a locator scheme. The critique has no C-numbers, so a declared custom scheme is the expected behaviour.
  - R5 (manual): every requirement carries at least one locator in that scheme.
  - R6 (manual): five locators sampled per rep each resolve to a real section or point of the fixture.
  - R7 (manual): every requirement has a locator, unless it is explicitly routed to brainstorming.

  B2 passes when M3 and R4–R7 all hold.
- **B3: routing header and handoff.**
  - M2 (mechanical): the spec's first non-blank line after its title is the routing header from `spec-synthesis.md`, verbatim except for whitespace.
  - M4 (mechanical): no roadmap or plan file exists after T3.
  - M5 (mechanical): the final assistant message names derive-roadmap and recommends a fresh or new session.
  - R8 (manual): the rep stops after the handoff, and never drafts a roadmap, stages or a plan in chat.

  B3 passes when M2, M4, M5 and R8 all hold.

**Pass bar:** each behaviour holds in at least 4 of 5 valid reps. Below that, the behaviour is a recorded failure.

**E1, the exemplar step (new; observed, not scored).** For each rep, record which `specs/completed/` files it read (`grade.py`'s `exemplars_read`). The skill now names `delegation-frontmatter-rollout.md` and `skill-model-pin-removal.md`. E1 is the GREEN check of Task 1's edit, and the pilot rule below uses it.

**VOID rule.** A rep is void if its transcript shows it reading this plan's context, or a worked synthesis of its own fixture. That means either of these:
- A tool input that names, or a tool result that carries, the full path of any of:
  - agent-skills `specs/deferred_items.md`
  - `specs/plans/`
  - `specs/completed/methodology-pipeline-skills.md`
  - `specs/completed/audit_9_2_26.md`
  - `specs/completed/red-baseline-*`
  - `specs/completed/synthesize-mode-*`
  - `.claude/`
  - anything under `~/Projects/alt-nfp-model`, `~/Projects/alt-nfp-stats*` or `~/Projects/archive/alt_nfp`
  - the control directory, including its archived run
  - **(new)** `~/.cache/nfp-series/`, plan 36's rep repos, which hold its reps' syntheses of this fixture
- Injected context (`attachment` / `system` records) that carries any injected-context marker: `36-synthesize-mode`, **(new)** `42-synthesize-mode`, `synthesize-mode-verification`, `scenario verification`, `ctl-q9`.

Reading the skill's own files, and reading `specs/completed/` exemplars other than the listed paths, is required behaviour and never voids a rep. A bare directory listing that shows file names does not void a rep. Reading or grepping the content of a listed VOID path does.

**Shared-checkout guard (new).** Record four values at four points: before the pilot, after the pilot, after the batch, and after each replacement rep.
- `git -C ~/Projects/agent-skills rev-parse --abbrev-ref HEAD`
- `git -C ~/Projects/agent-skills rev-parse HEAD:skills/describe-critique-methodology`
- the exit status of `git -C ~/Projects/agent-skills diff --quiet HEAD -- skills/describe-critique-methodology`
- `grep -c 'skill-model-pin-removal.md' ~/.claude/skills/describe-critique-methodology/references/spec-synthesis.md`

Any of the following voids the reps run since the previous check: the branch is not `main`, the tree hash differs from the one recorded before the pilot, the `diff` exits nonzero, or the `grep` count is not 1.

**Pilot redesign trigger (new).** A pilot rep can be void because it followed the skill's own procedure to a VOID path, for example opening a VOID-listed spec while looking for exemplars. Then **stop**: run no batch, record the run as VOID with the cause, and make the redesign a new deferred item. A pilot that is void for any other cause follows plan 36's rule: record the path and GO.

**Denials (changed).** `permission_denials` counts transcript records that carry `toolDenialKind`, and `denied_calls` lists each denied call's tool and input. Plan 36 counted tool results whose text contained "permission", and reported 0 where its transcripts held 24.

**Wiki environment (new).** Every rep runs with `LLM_WIKI_ROOT` unset, and the only `printenv` it may run is `printenv LLM_WIKI_ROOT`.

**Replacement:** void reps are replaced from rep-6 upward, up to 10 reps in total. With fewer than 5 valid reps after rep-10, stop: record the run as void and report.

---

### Task 1: Name the two exemplars in the skill

**Files:**
- Modify: `skills/describe-critique-methodology/references/spec-synthesis.md:32-35`

**Interfaces:**
- Produces: the exemplar sentence that E1 observes, in the form `read two retired exemplars in the agent-skills repo's specs/completed/ directory, delegation-frontmatter-rollout.md and skill-model-pin-removal.md`. Task 2 verifies it through `~/.claude/skills/`.

- [ ] **Step 1: Confirm the failing evidence**

writing-skills requires a failing test before a skill edit, and plan 36's run is this edit's failing test. Read `specs/completed/synthesize-mode-verification-2026-10-05.md` § Validity: all 5 reps opened the skill's own design spec through the unnamed-exemplar sentence. No new RED run is needed. This plan's run, through E1, is the GREEN check.

- [ ] **Step 2: Edit the sentence**

In `skills/describe-critique-methodology/references/spec-synthesis.md`, replace:

```text
Out of scope, Rollout note. Do not reinvent the skeleton — before writing
your first synthesized spec, read two retired exemplars in the agent-skills
repo's `specs/completed/` directory (that repo owns the house format; this
file cites it rather than restating it).
```

with:

```text
Out of scope, Rollout note. Do not reinvent the skeleton — before writing
your first synthesized spec, read two retired exemplars in the agent-skills
repo's `specs/completed/` directory, `delegation-frontmatter-rollout.md` and
`skill-model-pin-removal.md` (that repo owns the house format; this file
cites it rather than restating it).
```

Name only these two files. Do not mention the skill's own design spec, even as a prohibition: naming it would draw reps to it.

- [ ] **Step 3: Run the commit lints**

From the worktree root, run the six commit lints. If plan 41 has merged, `bash build/run_commit_lints.sh` runs all six. Otherwise, run:

```bash
uv run --python 3.13 --with pyyaml python build/check_frontmatter.py
uv run --python 3.13 python build/check_provenance.py
uv run --python 3.13 python build/check_snippets.py skills/
uv run --python 3.13 --with pyyaml python build/check_conformance.py
(cd build && uv run --python 3.13 --with pytest --with pyyaml python -m pytest -q test_runtime_support.py -k declared_dependencies)
uv run --python 3.13 --with pyyaml python build/sync_runtime_assets.py --check
```

Expected: every command exits 0.

- [ ] **Step 4: Commit**

```bash
git add skills/describe-critique-methodology/references/spec-synthesis.md
git commit -m "docs(describe-critique-methodology): name the two spec exemplars"
```

- [ ] **Step 5: Checkpoint — the owner lands Task 1 on `main`**

Report to the owner: "Task 1's commit must be on `main` before the pilot, because reps load the skill through `~/.claude/skills/`, which symlinks into the main checkout. Please land it, either as a pull request of this commit alone or by fast-forwarding local `main` to it, and tell me when it is there." Task 2 can run meanwhile. Its last step checks this landing.

---

### Task 2: Refresh the kit

**Files (all outside this repository):**
- Move: `~/.cache/ctl-q9/results/` and `~/.cache/ctl-q9/sessions/` into `~/.cache/ctl-q9/run-2026-10-05/`
- Modify: `~/.cache/ctl-q9/grade.py`
- Replace: `~/.cache/ctl-q9/run_rep.sh`
- Create: `~/.cache/ctl-q9/results/`, `~/.cache/ctl-q9/sessions/rep-1.id` … `rep-10.id`
- Create: `~/.cache/nfp-notes/rep-1` … `rep-10` (git repos)
- Unchanged: `~/.cache/ctl-q9/prompts/`, `coverage-key.md`, `run_pilot.sh`, `run_batch.sh`

**Interfaces:**
- Consumes: plan 36's kit as it stands in `~/.cache/ctl-q9/`.
- Produces:
  - `grade.py <n> …` keeps plan 36's keys and adds `denied_calls`. `permission_denials` now counts `toolDenialKind` records.
  - Two environment variables, `GRADE_SESSIONS` and `GRADE_REPOS`, override where `grade.py` looks. They default to `~/.cache/ctl-q9/sessions` and `~/.cache/nfp-notes`.
  - `run_rep.sh <n>` runs rep *n* from `~/.cache/nfp-notes/rep-<n>`.

- [ ] **Step 1: Archive plan 36's run**

```bash
mkdir -p ~/.cache/ctl-q9/run-2026-10-05
mv ~/.cache/ctl-q9/results ~/.cache/ctl-q9/sessions ~/.cache/ctl-q9/run-2026-10-05/
mkdir -p ~/.cache/ctl-q9/results ~/.cache/ctl-q9/sessions
ls ~/.cache/ctl-q9/run-2026-10-05/sessions | wc -l
```

Expected: `10`.

- [ ] **Step 2: Make the grader's run location configurable**

In `~/.cache/ctl-q9/grade.py`, add `import os` after `import json`. Then replace:

```python
CTL = HOME / '.cache' / 'ctl-q9'
REPOS = HOME / '.cache' / 'nfp-series'
```

with:

```python
CTL = HOME / '.cache' / 'ctl-q9'
SESSIONS = Path(os.environ.get('GRADE_SESSIONS', CTL / 'sessions'))
REPOS = Path(os.environ.get('GRADE_REPOS', HOME / '.cache' / 'nfp-notes'))
```

Then replace both occurrences, in `grade` and in `dump_injected`, of:

```python
    sid = (CTL / 'sessions' / f'rep-{n}.id').read_text().strip()
```

with:

```python
    sid = (SESSIONS / f'rep-{n}.id').read_text().strip()
```

- [ ] **Step 3: Watch the denial count fail on plan 36's run**

```bash
GRADE_SESSIONS=~/.cache/ctl-q9/run-2026-10-05/sessions GRADE_REPOS=~/.cache/nfp-series python3 ~/.cache/ctl-q9/grade.py 1 2 3 4 5 | python3 -c 'import json, sys; print(sum(json.loads(line)["permission_denials"] for line in sys.stdin))'
```

Expected: `0`. That is the bug: these five transcripts hold 24 records with `toolDenialKind: "user-rejected"` (6, 4, 4, 6 and 4, counted 2026-10-11).

- [ ] **Step 4: Count denials by `toolDenialKind`**

In `grade`, replace:

```python
    void_hits, inherited_hits, exemplars, denials, bash_writes = [], [], set(), 0, []
```

with:

```python
    void_hits, inherited_hits, exemplars, denials, bash_writes = [], [], set(), 0, []
    calls, denied_calls = {}, []
```

Replace:

```python
                if item.get('is_error') and 'permission' in text.lower():
                    denials += 1
```

with:

```python
                if record.get('toolDenialKind'):
                    denials += 1
                    denied_calls.append(calls.get(item.get('tool_use_id'), '?'))
```

Replace:

```python
                tool_input = json.dumps(item.get('input', {}))
```

with:

```python
                tool_input = json.dumps(item.get('input', {}))
                calls[item.get('id')] = (item.get('name', '?') + ': ' + tool_input)[:160]
```

And in the returned dict, replace:

```python
        'permission_denials': denials,
```

with:

```python
        'permission_denials': denials,
        'denied_calls': denied_calls,
```

- [ ] **Step 5: Watch the denial count pass**

Run the Step 3 command again. Expected: `24`. Then read rep-1's list:

```bash
GRADE_SESSIONS=~/.cache/ctl-q9/run-2026-10-05/sessions GRADE_REPOS=~/.cache/nfp-series python3 ~/.cache/ctl-q9/grade.py 1 | python3 -c 'import json, sys; r = json.loads(sys.stdin.readline()); print(r["permission_denials"]); print(*r["denied_calls"], sep="\n")'
```

Expected: `6`, then six lines, each starting `Bash: `. Among them is a `printenv LLM_WIKI_ROOT` call.

- [ ] **Step 6: Add the new VOID path and marker**

In `grade.py`, replace:

```python
    '.cache/ctl-q9',
)
INHERITED = ('36-synthesize-mode', 'synthesize-mode-verification',
             'scenario verification', 'ctl-q9')
```

with:

```python
    '.cache/ctl-q9',
    '.cache/nfp-series',
)
INHERITED = ('36-synthesize-mode', '42-synthesize-mode', 'synthesize-mode-verification',
             'scenario verification', 'ctl-q9')
```

Then `python3 -m py_compile ~/.cache/ctl-q9/grade.py`. Expected: no output.

- [ ] **Step 7: Build the ten fresh rep repos and session ids**

Run this block once for each `n` from 1 to 10, as plain commands, with `n` written in literally. In a worktree-isolated session, loops of git commands may be refused, so run them one at a time.

```bash
mkdir -p ~/.cache/nfp-notes/rep-1/specs
cp /Users/lowell/Projects/alt-nfp-model/specs/completed/calibration_methodology.md ~/.cache/nfp-notes/rep-1/specs/
cp /Users/lowell/Projects/alt-nfp-model/specs/completed/calibration_methodology_review.md ~/.cache/nfp-notes/rep-1/specs/
printf '%s\n' '# nfp-notes' > ~/.cache/nfp-notes/rep-1/README.md
git -C ~/.cache/nfp-notes/rep-1 init -q
git -C ~/.cache/nfp-notes/rep-1 add -A
GIT_AUTHOR_DATE='2026-09-22T06:02:00' GIT_COMMITTER_DATE='2026-09-22T06:02:00' git -C ~/.cache/nfp-notes/rep-1 -c user.name='nfp-notes' -c user.email='nfp-notes@example.invalid' commit -q -m 'docs(specs): calibration methodology and its review'
uuidgen | tr 'A-Z' 'a-z' > ~/.cache/ctl-q9/sessions/rep-1.id
```

Verify:

```bash
ls ~/.cache/nfp-notes | wc -l
ls ~/.cache/ctl-q9/sessions | wc -l
git -C ~/.cache/nfp-notes/rep-10 log --oneline
ls -d ~/.claude/projects/-Users-lowell--cache-nfp-notes-* 2>/dev/null | wc -l
```

Expected: `10`, `10`, one commit line, and `0`. The last value confirms that Claude Code holds no project state for the new paths.

- [ ] **Step 8: Replace `run_rep.sh`**

Write `~/.cache/ctl-q9/run_rep.sh`:

```bash
#!/usr/bin/env bash
# One rep: three turns of one fresh `claude -p` session rooted in the rep's repo.
# Run from a plain terminal, never from a Claude Code session.
set -euo pipefail
n="$1"
ctl="$HOME/.cache/ctl-q9"
repo="$HOME/.cache/nfp-notes/rep-$n"
sid="$(cat "$ctl/sessions/rep-$n.id")"
tools=(Read Glob Grep Skill Write Edit 'Bash(git:*)' 'Bash(ls:*)' 'Bash(cat:*)'
  'Bash(head:*)' 'Bash(tail:*)' 'Bash(grep:*)' 'Bash(rg:*)' 'Bash(find:*)' 'Bash(wc:*)'
  'Bash(printenv LLM_WIKI_ROOT)')
# The skill's wiki touchpoints run only when LLM_WIKI_ROOT is set; every rep
# runs without a wiki.
unset LLM_WIKI_ROOT
cd "$repo"
claude -p --session-id "$sid" --output-format json --permission-mode acceptEdits \
  --allowedTools "${tools[@]}" < "$ctl/prompts/turn1.txt" > "$ctl/results/rep-$n.turn1.json"
claude -p --resume "$sid" --output-format json --permission-mode acceptEdits \
  --allowedTools "${tools[@]}" < "$ctl/prompts/turn2.txt" > "$ctl/results/rep-$n.turn2.json"
claude -p --resume "$sid" --output-format json --permission-mode acceptEdits \
  --allowedTools "${tools[@]}" < "$ctl/prompts/turn3.txt" > "$ctl/results/rep-$n.turn3.json"
git -C "$repo" status --porcelain --untracked-files=all > "$ctl/results/rep-$n.status.txt"
git -C "$repo" log --oneline > "$ctl/results/rep-$n.log.txt"
echo "rep-$n done"
```

Then `chmod +x ~/.cache/ctl-q9/run_rep.sh` and `bash -n ~/.cache/ctl-q9/run_rep.sh`. Expected: no output.

Plan 36 passed the allowed tools as one space-separated string. They are now one argument per rule, because the `printenv` rule contains a space. Task 3's pilot audit checks that the rule took effect.

- [ ] **Step 9: Run the grep gate**

The gate covers what reps can read: the fixture repos and the two exemplars the skill now names.

```bash
grep -rlic 'derive-roadmap\|locator\|design provenance\|required next skill\|triage table\|synthesize mode\|describe-critique' ~/.cache/nfp-notes/ | wc -l
grep -lic 'derive-roadmap\|locator\|design provenance\|required next skill\|triage table\|synthesize mode\|describe-critique' ~/Projects/agent-skills/specs/completed/delegation-frontmatter-rollout.md ~/Projects/agent-skills/specs/completed/skill-model-pin-removal.md | wc -l
```

Expected: `0` and `0`. Both exemplars returned 0 on 2026-10-11. A hit means a file names a measured behaviour: inspect it and report before continuing.

Every rep that follows the skill reads both exemplars. If either one contained a VOID path or a marker, every such rep would be void by construction. Check both:

```bash
for p in 'Projects/agent-skills/specs/deferred_items.md' 'Projects/agent-skills/specs/plans/' 'Projects/agent-skills/specs/completed/methodology-pipeline-skills.md' 'Projects/agent-skills/specs/completed/audit_9_2_26.md' 'Projects/agent-skills/specs/completed/red-baseline-' 'Projects/agent-skills/specs/completed/synthesize-mode-' 'Projects/agent-skills/.claude/' 'Projects/alt-nfp-model' 'Projects/alt-nfp-stats' 'Projects/archive/alt_nfp' '.cache/ctl-q9' '.cache/nfp-series' '36-synthesize-mode' '42-synthesize-mode' 'synthesize-mode-verification' 'scenario verification'; do grep -l -i -F -- "$p" ~/Projects/agent-skills/specs/completed/delegation-frontmatter-rollout.md ~/Projects/agent-skills/specs/completed/skill-model-pin-removal.md; done | wc -l
```

Expected: `0`. Both files returned 0 on 2026-10-11. A hit sends the exemplar choice back to the owner before the pilot.

- [ ] **Step 10: Smoke-test the transcript lookup**

Run: `python3 ~/.cache/ctl-q9/grade.py 1`
Expected: `expected one transcript for <uuid>, found 0`. That shows the lookup is live and that no rep has run yet.

- [ ] **Step 11: Checkpoint — record the guard and hand the pilot to the owner**

Confirm the owner has landed Task 1 (Task 1, Step 5). Then record the guard's first values in the ledger:

```bash
git -C ~/Projects/agent-skills rev-parse --abbrev-ref HEAD
git -C ~/Projects/agent-skills rev-parse HEAD:skills/describe-critique-methodology
git -C ~/Projects/agent-skills diff --quiet HEAD -- skills/describe-critique-methodology; echo $?
grep -c 'skill-model-pin-removal.md' ~/.claude/skills/describe-critique-methodology/references/spec-synthesis.md
```

Expected: `main`, a tree hash (record it), `0` and `1`. If any value differs, stop: Task 1 is not on `main`, or the checkout has moved.

Then report to the owner: "Kit ready. Please run `bash ~/.cache/ctl-q9/run_pilot.sh` from a plain terminal, not from any Claude Code session, and tell me when it prints `rep-1 done`."

---

### Task 3: Pilot audit (owner runs, executor audits)

**Files:**
- Read: `~/.cache/ctl-q9/results/rep-1.*`, and rep-1's transcript under `~/.claude/projects/`

**Interfaces:**
- Consumes: `grade.py` (Task 2), and the guard values from Task 2, Step 11.
- Produces: a go/no-go for the batch, with the audit notes that Task 5 copies into the record.

- [ ] **Step 1: The owner runs the pilot**

The owner runs `bash ~/.cache/ctl-q9/run_pilot.sh` and reports `rep-1 done`. If it errors, collect `~/.cache/ctl-q9/results/rep-1.turn*.json` and stop: the mechanism failed, not the skill.

- [ ] **Step 2: Re-check the guard**

Run Task 2, Step 11's four commands. Expected: `main`, the same tree hash, `0` and `1`. Any difference voids rep-1 under the guard.

- [ ] **Step 3: Grade the pilot mechanically**

Run: `python3 ~/.cache/ctl-q9/grade.py 1`
Expected, before you read any behavioural field:
- `inherited_hits` is `[]`.
- `void_hits` is `[]`.
- Every entry in `denied_calls` is a command that the rep then completed another way.
- No denied call's command is exactly `printenv LLM_WIKI_ROOT`. If one is, the allow rule did not take effect. That is NO-GO: fix the mechanism and re-run the pilot as rep-6.
- Compound forms such as `printenv LLM_WIKI_ROOT; echo …` are still refused by the exact-match rule (plan-36 reps ran them). Their denial is expected and is not a NO-GO.
- `exemplars_read`: record it. The expected value is the two named exemplars.

- [ ] **Step 4: Read what the pilot was handed**

Run: `python3 ~/.cache/ctl-q9/grade.py --injected 1`

Read the file it prints, `~/.cache/ctl-q9/results/rep-1.injected.jsonl`, in full rather than by grep. It holds every `attachment` and `system` record, plus every user text that is not one of the three turn prompts. The pilot passes this audit only if none of it mentions this plan, the deferred item or the expected behaviours. The global `~/.claude/CLAUDE.md`, the skill listing and the rep repo's own git status are expected there, and are not contamination.

- [ ] **Step 5: Decide**

- **GO:** Steps 2–4 are all clean, and all three turns produced output. rep-1 counts as the first rep if it is not void.
- **NO-GO:** inherited context names this plan or the item. Stop and report: Channel 5 has a path this plan did not foresee.
- **NO-GO:** denials blocked the spec write or the commit, or the `printenv` rule did not take effect. Report which tool was denied. Widening `tools` in `run_rep.sh` is an owner decision, because it changes what every rep may run.
- **STOP (redesign trigger):** rep-1 is void because it followed the skill's own procedure to a VOID path, such as a VOID-listed spec opened while looking for exemplars. Run no batch. Go to Task 5 and record the run as VOID, with the cause and the transcript evidence.
- **GO:** rep-1 is void for any other cause. Record which path voided it and how, because that path will recur.

- [ ] **Step 6: Checkpoint — hand the batch to the owner**

On GO, report the audit and ask: "Please run `bash ~/.cache/ctl-q9/run_batch.sh` from a plain terminal and tell me when it prints `batch done`."

---

### Task 4: Batch and validity (owner runs, executor audits)

**Interfaces:**
- Consumes: `grade.py`, the VOID rule, the guard and the replacement rule (Pre-registration).
- Produces: a set of exactly 5 valid reps, or a void run.

- [ ] **Step 1: The owner runs the batch**

The owner runs `bash ~/.cache/ctl-q9/run_batch.sh` and reports `batch done`.

- [ ] **Step 2: Re-check the guard**

Run Task 2, Step 11's four commands. Expected: `main`, the same tree hash, `0` and `1`. Any difference voids reps 2–5.

- [ ] **Step 3: Grade every rep and apply the VOID rule**

Run: `python3 ~/.cache/ctl-q9/grade.py 1 2 3 4 5`

A rep is void if `void_hits` or `inherited_hits` is non-empty. For each void rep, open its transcript at the first hit and confirm that it reads a VOID path or carries a marker. A false match, such as a bare listing, is not a void: record why. Record each rep's `exemplars_read` and `denied_calls`.

- [ ] **Step 4: Replace void reps, if any**

For each void rep, ask the owner to run `bash ~/.cache/ctl-q9/run_rep.sh <k>` for the next unused *k* (6, 7, …). After each one, re-check the guard, then grade it. Stop at rep-10. With fewer than 5 valid reps after rep-10, skip to Task 5 and record the run as void.

- [ ] **Step 5: Fix the valid set**

The first 5 valid reps by number are the scored set. Note the batching, and every void with its cause, for the record.

---

### Task 5: Score, record and commit

**Files:**
- Create: `specs/completed/synthesize-mode-verification-<YYYY-MM-DD>.md`

**Interfaces:**
- Consumes: the scored set and the audit notes (Tasks 3–4), and `coverage-key.md`.
- Produces: the record, and a verdict per behaviour that the Plan Completion Protocol acts on.

- [ ] **Step 1: Score the manual rubric for each scored rep**

For each rep, read its turn-1 output (`results/rep-<n>.turn1.json`, field `result`), its spec, and its turn-3 output. Score:
- R1: the adjudication status is stated above the table.
- R2: every coverage-key point appears in the table. List the missing ones.
- R3: the needs-user-adjudication questions are all in the table's message.
- R4: the provenance paragraph declares a scheme. Quote it.
- R5: every requirement carries a locator.
- R6: five sampled locators resolve. List them, with where each resolves.
- R7: every requirement has a locator, unless it is routed to brainstorming.
- R8: the rep stops after the handoff.

Keep a verbatim quote for every fail.

The mechanical checks are heuristics, so read before counting any check that came out false:
- M1 false: the table may sit under a header other than "Verdict".
- M2 or M3 false: `spec` may list more than one new file, or the file names may be written without `.md`.

Where reading shows the property holds, score it true and note why.

- [ ] **Step 2: Compute the verdicts**

Per rep: B1 = M1 ∧ R1 ∧ R2 ∧ R3; B2 = M3 ∧ R4 ∧ R5 ∧ R6 ∧ R7; B3 = M2 ∧ M4 ∧ M5 ∧ R8. A behaviour holds when it passes in at least 4 of the 5 scored reps. Also report E1: how many scored reps read exactly the two named exemplars.

- [ ] **Step 3: Write the record**

Create `specs/completed/synthesize-mode-verification-<YYYY-MM-DD>.md` with these sections:
- **Header**: Date, Status (for example "B1 held 5/5, B2 held 4/5, B3 failed 2/5", or "VOID"), and Governs ("whether describe-critique-methodology Synthesize mode's triage ordering, locator discipline and derive-roadmap handoff hold in practice").
- **Fixture**: the two source paths, their pre-skill shape (no C-numbers, foreign structure), and the coverage key's 50 points.
- **Changes from plan 36**: the five changes listed under Architecture, each with where it is applied.
- **Pre-registration**: copied verbatim from this plan.
- **Dispatch**:
  - the owner-run mechanism and why it is owner-run (Channel 5)
  - the batching
  - the model and effort the reps ran at, read from the transcripts' `message.model` and `effort` fields
  - the guard values at each check
  - the pilot audit
- **Validity**: every void with its cause, each rep's `exemplars_read` (E1), and the denied calls.
- **Result**: one table, with a row per scored rep and columns M1–M5, R1–R8, B1–B3, write turn and spec path.
- **Decision**: the three verdicts against the pass bar, and E1.
- **Qualitative evidence**: verbatim quotes for every failure, plus any notable behaviour the pass bar does not capture.
- **Disposition**: for each failed behaviour, the deferred item it becomes. Use the Deferred-item schema in `skills/writing-plans/references/deferred-backlog.md`, normally `Size: design` with `Done when:` set to a skill change verified by a writing-skills cycle.

- [ ] **Step 4: Commit**

```bash
git add specs/completed/synthesize-mode-verification-*.md
git commit -m "docs(specs): record the synthesize-mode scenario verification re-run"
```

- [ ] **Step 5: Report**

Report the three verdicts, E1, the void count and the record's path. Failed behaviours go to the Plan Completion Protocol's resolve-before-defer gate as leftovers.

The protocol ticks the source item `→ done in plan 42` only when its closure condition holds: 5 valid reps, and a record with B1–B3 verdicts. A recorded failure counts as a verdict. A void run does not: the item stays open, and the protocol appends a successor that carries the cause.
