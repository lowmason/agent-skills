# STE Drift Review and Obligation-Word Rule Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Re-vendor danyuchn's `ste-lint.py` at `d714e536`, add one obligation-word line to `write-with-asd-ste100`'s meaning rules and measure it against a control, add the tracked-symlink document case, and recheck four linter items against the new upstream diff.

**Architecture:** Task 1 is the drift review and re-vendor, in its own commit. Task 2 builds a new committed micro-test kit under `specs/baseline/red-baseline-ste-obligation-word/kit/`, ported from the 2026-10-18 scratch kit and given every next-kit fix. Tasks 3 to 5 run a control arm, the wording change with its treatment arm, and the document cases. Task 6 writes the record.

**Tech Stack:** Python 3.13 (dev, `build/versions.toml`) and `/usr/bin/python3` 3.9.6 for the linter suite, bash, `claude -p` (CLI version recorded at hold), `gh api`.

**Spec:** none. The requirements are four `specs/deferred_items.md` items, quoted by section below.

- [119] "The next drift review of both STE upstreams", section `deferred-2026-11-17 (no plan; /deferred pass, branch claude/deferred-a35864) — 2026-11-17`.
- [33] "`SKILL.md` has no line that keeps the strength of an obligation word", section `52-write-with-asd-ste100 — 2026-10-18`. Owner ruling 2026-11-17: go ahead.
- [34] "Three review fixes have no test", same section. Its signal fires when the skill's cases run again.
- Recheck only: [105], [106] (section `claude/peaceful-gauss-1ce419 Step 4b review — 2026-11-12`) and [120], [121] (section `claude/deferred-a35864 Step 4b review — 2026-11-17`).

## Global Constraints

- The vendored `skills/write-with-asd-ste100/scripts/ste-lint.py` stays byte-identical to upstream (root `CLAUDE.md`, "Provenance is load-bearing"). Mode stays 100644.
- Before any upstream file is downloaded, the executing session asks the owner in its own conversation and names the file, the source commit and the size. A plan approval or a ledger line is not that ask.
- Read `NOTICE` before editing it. `LICENSE-write-with-asd-ste100-sources` and `skills/write-with-asd-ste100/LICENSE-write-with-asd-ste100-sources` stay byte-identical (`build/check_provenance.py`).
- Files this stream may touch: `skills/write-with-asd-ste100/`, `rules/write-with-asd-ste100.md`, `NOTICE`, both STE sources files, `specs/baseline/red-baseline-ste-obligation-word*`, this plan, one new entry in `build/suites.toml`, and append-only lines in `specs/deferred_items.md` and `specs/history.md`. Never touch `skills/derive-roadmap/` or `build/cc_guide/` (parallel streams).
- A wording change to measured skill text follows the writing-skills micro-test discipline (`skills/writing-skills/SKILL.md` "Micro-Test Wording Before Full Scenarios" and `references/micro-tests.md`): a no-guidance control, 5 reps per variant per model, two models, rules committed before any reply is read, blind sheets, a spend cap.
- Models: `claude-opus-5-5` and `claude-sonnet-5-5`, 5 reps each, default effort.
- Spend cap: $30 for all reps and judge calls. Stop rule: stop and ask the owner when the running total plus the next batch's worst case passes the cap, or when one rep costs more than $3.
- Pass bar: a case passes on a model when at least 4 of its 5 good runs meet every registered check.
- Next-kit fixes (memory `serialize-plan-executions`), all required: a per-rep `HOME` and `TMPDIR`; no `credential_expires_at`, `session_id` or `uuid` in any kept rep file; the `for`-loop `Read(~/**)` gap closed by the per-rep `HOME` plus a PreToolUse guard; a no-tool rep with `result_index` > 0 or a non-null `origin` is void, and `origin` is scrubbed; cross-session tools (`ListAgents`, `SendMessage`, `PushNotification`, `RemoteTrigger`) denied in tool reps; `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1` and `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`; `env -i`; an isolation probe before the first scored rep.
- No rep can reach this repository, the plan, the kit, the old scratch kit or the test records.
- Commit lints pass before every commit: `build/run_commit_lints.sh`.

## Review Focus

1. A reply that keeps "should" only in a `Kept as-is:` line or a flag, while the rewrite drops it. The obligation check scores the rewritten block only.
2. A reply that turns "should" into "must", "always", "required" or "has to". That fails, the same as a bare command.
3. The new linter's wrapped-phrase pass adds findings to `SKILL.md` or to the rule. The record separates the re-vendor's delta from the new line's delta.
4. A `doc-symlink` rep that rewrites through the link and changes the dirty target. The mechanical check compares the target's bytes.
5. A sheet line that differs by arm (memory `microtest-sheet-arm-tell`). A no-model test diffs sheet lines across arms.

## Decisions

- **D1** (owner, brief, 2026-11-27): [33]'s change is one line in `SKILL.md`'s meaning rules, a pre-registered obligation-word check, and a re-run of the three agent cases at a bar of 4 of 5. Applied in: Tasks 2 to 4.
- **D2** (owner, brief, 2026-11-27): the four recheck items close only on evidence from the diff that upstream fixed their code path. Applied in: Task 1.
- **D3** (planner, for plan review, 2026-11-27): the kit is new and committed, under `specs/baseline/red-baseline-ste-obligation-word/kit/`. The 2026-10-18 scratch kit stays frozen (its `PREREGISTRATION.md` forbids a change after the first run), and it predates every isolation fix. "The kit's `cases.py`" in [33] and [34] is read as the new kit's `cases.py`. Applied in: Task 2.
- **D4** (planner, for plan review, 2026-11-27): a fresh control arm runs on the current `SKILL.md`. The isolation differs from `skill-r2`, so its unscored 3 of 5 is no control. If the control passes the obligation check at 4 of 5 or better on both models, stop and ask the owner before the line ships. Applied in: Task 3.
- **D5** (planner, for plan review, 2026-11-27): all four document cases run (`doc-clean`, `doc-dirty`, `skill-md`, `doc-symlink`), on the final skill text and both models. [34] says "a run of the document cases", and `doc-clean` ran before fix 4 changed step 3. Applied in: Task 5.
- **D6** (planner, for plan review, 2026-11-27): the new line names "should", a word of the `agent-instruction` source. The item names "should" as its example, so the overlap check records it and allows it. Applied in: Task 4.
- **D7** (owner, plan review, 2026-11-27): approve as written, with D3 to D6 standing. Execute inline in the planning session (executing-plans). Applied in: all tasks.
- **D8** (owner, execution, 2026-11-27): "Give agent reps Read". With `--tools ""`, 4 of 5 Opus 5.5 control reps wrote tool calls as text, and 2 ran to the output limit (about $3.40 each). Agent reps now get the Read tool, and they are scored on their final message. The first 5 reps are set aside. Applied in: Task 2 (kit amendment 1), Tasks 3 to 5.

---

### Task 1: Drift review and re-vendor at `d714e536`

**Files:**
- Modify: `skills/write-with-asd-ste100/scripts/ste-lint.py` (replaced by upstream's bytes)
- Modify: `skills/write-with-asd-ste100/scripts/test_ste_lint.py`
- Modify: `NOTICE` (STE paragraph), `LICENSE-write-with-asd-ste100-sources`, `skills/write-with-asd-ste100/LICENSE-write-with-asd-ste100-sources`
- Modify: this plan (an `## Execution notes` section)

**Interfaces:**
- Produces: the re-vendored linter, which every later task's lint and kit check calls as `python3 skills/write-with-asd-ste100/scripts/ste-lint.py`.

Known facts from planning (2026-11-27, `gh api` compare `70736273...d714e536`): two commits. `65c8ab6e` (#72, Anton, `v-anton`, 2026-11-20) changes only `scripts/ste-lint.py` (+77/−1): it adds `_fill`, `_wrapped_findings`, fills autolink ranges after `_gfm_autolinks` in both main-pass call sites, and adds self-test cases. `d714e536` (#73, Iztok Oder, `ioder`, 2026-11-24) adds `"version": "0.4.0"` to `.claude-plugin/plugin.json`, which the skill does not adapt. No `SKILL.md`, `references/` or LICENSE file changed. prithivrajmu HEAD is still `cf9787b6`. Upstream blob at `d714e536`: sha `0b48290f765aafba6f97f410a4a317141f6786d2`, 192,330 bytes. Vendored blob now: `44c62334`.

- [x] **Step 1: Ask the owner.** In the executing session's conversation, ask whether to download and re-vendor `scripts/ste-lint.py` from danyuchn/asd-ste100-skill at `d714e536`, 192,330 bytes. Say that the self-test was not run before the ask (memory `classifier-blocks-downloaded-script-run`). On a no, skip Steps 2 to 7, record the review only, and note it as a deviation.
- [x] **Step 2: Write two failing tests in `test_ste_lint.py`.** `test_bare_url_semicolon_is_not_prose`: linting `See https://x.io/a;b for it.` gives no `semicolon` finding, and `See https://x.io/a; then go.` gives one at column 19. `test_wrapped_phrasal_verb_is_found`: linting `Next we spin\nup the server.` gives exactly one `phrasal-verb` finding, at line 1, column 9. Update the pinned-bytes test to blob `0b48290f765aafba6f97f410a4a317141f6786d2`.
- [x] **Step 3: Run the suite on the `70736273` copy.** Run: `uv run python build/run_suites.py write-with-asd-ste100`. Expected: the two new tests and the pin test FAIL, all others pass.
- [x] **Step 4: Download into a new empty folder** (`mktemp -d`), outside the repo, with `gh api 'repos/danyuchn/asd-ste100-skill/contents/scripts/ste-lint.py?ref=d714e536' -H 'Accept: application/vnd.github.raw'`. Check: `git hash-object` prints `0b48290f765aafba6f97f410a4a317141f6786d2` and `wc -c` prints 192330. Copy it over the vendored file, then check `git ls-files -s` still shows mode 100644.
- [x] **Step 5: Run the suite.** Same command as Step 3. The suite runs the self-test under the dev Python and `/usr/bin/python3` 3.9.6. Expected: all pass, no skip.
- [x] **Step 6: Recheck [105], [106], [120] and [121].** Run each item's own reproduction (in its item text) on the `70736273` copy (`git show HEAD:<path>`, saved to a temp folder) and on the new copy. Also run, for [121], a span that opens on line 1 and holds autolink-like text such as `https://x.io/a` and a `;` on line 2 before its closing backtick, and, for [106], a single-quoted multi-line `description:` with `It can''t have failed.` split across the line break. An item counts as fixed only if its named function changed in the diff and its reproduction now gives the correct result. Write the four results, with the commands and outputs, under `## Execution notes` in this plan, with [120]'s new line numbers for its cited code.
- [x] **Step 7: Record the linter's counts** on `skills/write-with-asd-ste100/SKILL.md` and `rules/write-with-asd-ste100.md` before (planning: SKILL.md 2 violations, 1 hard, 1339 words) and after the re-vendor, under `## Execution notes`.
- [x] **Step 8: Update `NOTICE` and both sources files.** Move the linter pin to `d714e536` (2026-11-24, retrieved 2026-11-27). Credit Anton (https://github.com/v-anton) for pull request #72 (bare URLs skipped, phrases that a line break splits found). Add 2026-11-27 to NOTICE's list of reviews. Keep the adapted-text pin `3944283c` and prithivrajmu's pin. Run `uv run python build/check_provenance.py`: PASS, and `cmp` the two sources files: same.
- [x] **Step 9: Commit** `chore(write-with-asd-ste100): re-vendor ste-lint.py at d714e536`, after `build/run_commit_lints.sh` passes.

### Task 2: Build the kit and register its rules

**Files:**
- Create: `specs/baseline/red-baseline-ste-obligation-word/kit/` with `README.md`, `PREREGISTRATION.md`, `cases.py`, a runner, a scrub step, a judge step, a sheet builder, a tally and no-model tests.
- Modify: `build/suites.toml` (one new suite)

**Interfaces:**
- Consumes: the old kit's texts at `~/.cache/agent-skills/scratch/write-with-asd-ste100-kit/` (`cases.py`: `GUIDE`, `DUMMY_SKILL`, the three agent cases and their checks, `NO_ADDITIONS`, `doc_checks` in `kit.py`; `kit.py`: `JUDGE_PROMPT`, `JUDGE_SCHEMA`; `upstream/before-after.md` Examples A to C, the **Before** text). Port these texts byte for byte.
- Consumes: the runner patterns of `specs/baseline/red-baseline-handoff-rerun/kit/` (per-rep `HOME` with a `Library/Keychains` link, `guard.py`, the `credential_expires_at` check) and `specs/baseline/red-baseline-worktree-skills-fix/kit/` (`run_reps.sh` `env -i` set, `postprocess.py` void and scrub, the isolation probe).
- Produces: `cases.py` with the 7 cases below; a runner taking `<arm> <case> <model> <first-rep> <last-rep>`; a tally that prints one line per case and model, `<case> <model> <good>/<5> PASS|FAIL`.

Case set:

| Case | Tools | Checks |
|---|---|---|
| `agent-tool-description` | none | hedge (ported), `NO_ADDITIONS`, obligation, sentence cap 25 |
| `agent-error-message` | none | hedge (ported), `NO_ADDITIONS`, obligation, sentence cap 25 |
| `agent-instruction` | none | conditions and hedge (ported), `NO_ADDITIONS`, obligation, sentence cap 20 |
| `doc-clean`, `doc-dirty`, `skill-md` | `Bash,Read,Edit,Write` | ported `doc_checks` and judge checks |
| `doc-symlink` | `Bash,Read,Edit,Write` | see Step 3 |

- [x] **Step 1: Define the obligation check in `cases.py`,** exact text for the judge: `Every obligation word keeps its strength. "should" stays "should" or "ought to". It does not become a bare command, "must", "shall", "always", "required" or "has to". The rewrite adds no obligation word that the source does not have.` Add it to all three agent cases. The mechanical half: `obligation_flags(reply: str, source: str) -> list` raises a flag when the rewritten block holds fewer `should`/`ought to` matches than the source, or any `must`/`shall`/`required`/`has to`/`always` that the source lacks. The rewritten block is the reply up to the first `Kept as-is:` line, flag line or table, with fences removed.
- [x] **Step 2: Write the no-model tests for `obligation_flags`:** a reply `The downstream agent should consume the artifact.` gives no flag for source C; `Consume the artifact.` gives one; `The agent must consume the artifact.` gives one; a reply whose rewrite drops "should" but whose `Kept as-is: should` line keeps it gives one.
- [x] **Step 3: Define `doc-symlink`.** Fixture repo: `docs/manual.md` holds `GUIDE` and is committed. `docs/guide.md` is a committed symbolic link to `manual.md`. After the commit, `docs/manual.md` gets `GUIDE + '\nLast checked by facilities on 2026-10-01.\n'`, uncommitted. Prompt: `Rewrite docs/guide.md in 80% STE.\n`. Mechanical checks: `copy written` (`docs/guide.ste.md` exists and is a regular file), `link kept` (`docs/guide.md` is still a link to `manual.md`), `target untouched` (`docs/manual.md` holds the dirty bytes), `no commit` (one commit), `no other change` (`git status --porcelain` lists only `M docs/manual.md` and `?? docs/guide.ste.md`). A no-model test builds the fixture and checks that `test ! -L docs/guide.md` fails and that both git commands of step 3 of `references/document-rewrite.md` succeed with empty status, which is the case that fix 4 reproduced.
- [x] **Step 4: Build the runner.** Each rep gets its own `HOME` under `/private/tmp/ste114/<rep>` holding `.claude/rules/write-with-asd-ste100.md` (the arm's frozen rule) and nothing else under `.claude`, plus the `Library/Keychains` link. The skill reaches the rep as an appended system prompt that starts `Base directory for this skill: <dir>`, followed by the arm's frozen `SKILL.md`, where `<dir>` is the arm's frozen skill folder copied into the rep's `HOME`. No-tool reps run with `--tools ""` from an empty folder in the rep's `HOME`. Tool reps run in their fixture repo inside the rep's `HOME`, with `--add-dir <frozen skill folder>`, the guard as a PreToolUse hook and the four cross-session tools denied, through `--settings`. Every rep: `env -i` with the plan 103 variable set, `--strict-mcp-config`, `--no-session-persistence`, `--output-format json` (no-tool) or `stream-json` (tool), `--model <model>`. Raw output goes to `~/.cache/agent-skills/scratch/ste114/`; the kit keeps only scrubbed copies.
- [x] **Step 5: Freeze both arms.** `control`: `SKILL.md`, `references/`, `scripts/` and the rule from commit `4168d2a`, by `git show`. `treatment`: the same paths from the commit that Task 4 makes. Record each frozen `SKILL.md`'s SHA-256 in `README.md`. Never point a rep at `~/.claude/skills`.
- [x] **Step 6: Build the blind sheets and judges.** Sheets and judge packets use opaque ids. A no-model test builds sheets from stub replies of both arms and checks that no sheet line differs by arm except the reply text.
- [x] **Step 7: Write `PREREGISTRATION.md`.** It holds the checks above, the void rules (V1 no result or an empty reply; V2 a no-tool rep that called a tool; V3 a tool rep that the guard denied or that reached a path outside its `HOME`; V4 a peer `origin` or `result_index` > 0; V5 a cross-session tool in a tool rep's init record), the pass bar, D4's stop rule, the spend cap and stop rule, the hand-reading table for flags (`count` or `justified`, ported from the old `PREREGISTRATION.md` rows for the checks kept), and the run order of Tasks 3 to 5.
- [x] **Step 8: Run the no-model tests.** Command: `cd specs/baseline/red-baseline-ste-obligation-word/kit && uv run --with pytest python -m pytest -q`. Expected: all pass. Register the folder in `build/suites.toml` as suite `ste-obligation-kit`, and run `uv run python build/run_suites.py --check`: PASS.
- [x] **Step 9: Probe the isolation.** One probe rep per rep shape (no-tool and tool), on `claude-sonnet-5-5`, asks what instruction files, memory, tools, skills, other sessions and user name it can see. Expected: only the rule, the appended skill, the planned tools, and no user name, memory or session list. Fix any leak before Task 3.
- [x] **Step 10: Commit** the kit and the registration `test(write-with-asd-ste100): register the obligation-word kit`, before any scored rep runs.

### Task 3: Control arm

**Files:**
- Create: `specs/baseline/red-baseline-ste-obligation-word/kit/runs/control/` (scrubbed reps, sheets, judge results, verdicts)

- [ ] **Step 1: Run** the three agent cases in arm `control`, 5 reps on each model (30 reps). Replace any void rep under a new rep number.
- [ ] **Step 2: Score:** judges, mechanical flags, a hand reading of every flag before opening the key. Run the tally. Expected (the gap): `agent-instruction` fails the obligation check on at least one model.
- [ ] **Step 3: Apply D4.** If the control passes the obligation check at 4 of 5 or better on both models, stop and ask the owner whether the line still ships.
- [ ] **Step 4: Commit** `test(write-with-asd-ste100): score the control arm`.

### Task 4: The obligation line and the treatment arm

**Files:**
- Modify: `skills/write-with-asd-ste100/SKILL.md` (`## Meaning rules`, after the **Confidence** bullet)
- Create: `specs/baseline/red-baseline-ste-obligation-word/kit/runs/treatment/`

- [ ] **Step 1: Add the line,** exact copy:

```markdown
- **Obligation.** Keep the strength of every obligation word, also in an imperative step. "Should" stays "should". Do not make it "must" or a bare command.
```

- [ ] **Step 2: Check the line.** The linter on `SKILL.md` adds no finding to Task 1's after-count. The overlap check (words of the three agent sources in the new line) is recorded; "should" is allowed (D6). `uv run --with pyyaml python build/check_frontmatter.py` and `build/run_commit_lints.sh` pass.
- [ ] **Step 3: Commit** `feat(write-with-asd-ste100): keep the strength of obligation words`.
- [ ] **Step 4: Freeze the treatment arm** from that commit (Task 2 Step 5), and run the three agent cases, 5 reps on each model.
- [ ] **Step 5: Score** as in Task 3. Expected: every agent case passes every check at 4 of 5 or better on both models. A case that fails gets one wording fix and a re-run of that case. A second failure goes to the owner.
- [ ] **Step 6: Commit** `test(write-with-asd-ste100): score the treatment arm`.

### Task 5: Document cases

**Files:**
- Create: `specs/baseline/red-baseline-ste-obligation-word/kit/runs/docs/`

- [ ] **Step 1: Run** `doc-clean`, `doc-dirty`, `skill-md` and `doc-symlink` on the treatment arm, 5 reps on each model (40 reps).
- [ ] **Step 2: Score** with the mechanical checks, judges and hand reading. Expected: each case passes at 4 of 5 or better on both models. A failure follows Task 4 Step 5's rule, with the wording fix in `references/document-rewrite.md`.
- [ ] **Step 3: Commit** `test(write-with-asd-ste100): run the document cases`.

### Task 6: Record

**Files:**
- Create: `specs/baseline/red-baseline-ste-obligation-word.md`

- [ ] **Step 1: Write the record:** setup and CLI version, both frozen hashes, the isolation probe, per-arm cost and voids, the three tallies, the flag verdicts by check, which checks were mechanical, the Task 1 linter counts, and which of [34]'s three fixes the runs now reach (the symlink check only; the `python3` call and the kept "should" in `references/examples.md` stay unreached, since the no-tool reps cannot open references).
- [ ] **Step 2: Run** `build/run_commit_lints.sh`. Expected: PASS.
- [ ] **Step 3: Commit** `docs(specs): record the obligation-word micro-test`.

## Execution notes

**Task 1 (2026-11-27).** The owner said yes to the re-vendor in the executing conversation. The download's blob is `0b48290f765aafba6f97f410a4a317141f6786d2`, 192,330 bytes, mode 100644, SHA-256 `66c454b9…`. `test_bare_url_semicolon_is_not_prose` and `test_wrapped_phrasal_verb_is_found` failed on the `70736273` copy (2 failed, 13 passed) and pass on the new copy (15 passed, with the self-test under 3.13 and `/usr/bin/python3` 3.9.6, no skip).

Recheck, each reproduction run with `python3 -I ste-lint.py --json` on the `70736273` copy and on the `d714e536` copy. `(rule, line, col)` findings:

| Item | Reproduction | `70736273` | `d714e536` | Diff touches the named path? |
|---|---|---|---|---|
| [105] | front matter opening with `  # metadata; note` before `name:` | exit 1, `semicolon` 2:13 | the same | no: `_front_matter` (now line 1829) unchanged |
| [106] | `description: 'It can''t have failed.'` | `present-perfect` 3:25 | the same | no: `_front_matter`, `_scalar_pieces` (now 1794) unchanged |
| [106] | the same, single-quoted across a line break | `present-perfect` 4:10 | the same | no: `_wrapped_findings` adds no finding |
| [120] | list-item fence with no close, indented code, blank, `Outside; prose.` | no finding | the same | no: the fence code moved from 1977-1980 to 2024-2027, unchanged |
| [121] | `See`, backtick, `word` / `code;`, backslash, backtick, ` end.` | exit 1, `semicolon` 2:5 | the same | no: `_run_in_autolink` (246) and the span scan (271-276) unchanged |
| [121] | the same span closed by a backtick inside `<https://x.io/`>` | exit 1, `semicolon` 2:5 | the same | no: #72 fills autolink ranges after `_gfm_autolinks`, but the span close is decided before that |

Upstream fixed none of the four. Linter counts, `70736273` and `d714e536` alike: `SKILL.md` 2 violations (1 hard), 1339 words. `rules/write-with-asd-ste100.md` 2 violations (1 hard), 272 words.

**Task 2 (2026-11-27).** The kit has 16 no-model tests (`ste-obligation-kit` suite). Each of 8 deliberate breaks in `kit.py` (the scrub, the origin void, the denial void, the symlink target check, the environment, the arm field in the sheet, the cross-session deny list, the unread-flag rule) made one test fail. The ported cases equal the 2026-10-18 kit's prompts, checks, caps and fixtures. `control` froze at `4168d2a`: `SKILL.md` SHA-256 `e85c795e…`, rule `223a232c…`. Both probes on `claude-sonnet-5-5` saw only the rule, the skill prompt and the planned tools (none, or `Bash`, `Edit`, `Read`, `Write`), no memory, no other session and no user name. The init records list the CLI's bundled skills (`deep-research`, `dataviz` and others), but no rep has the Skill tool, and neither probe named them. The probes cost $0.06.

## Completion notes for the protocol

- [119]: tick `→ done` with the compare, the re-vendor commit and the pin, and append a new watch item for the next drift review, from `d714e536` (danyuchn) and `cf9787b6` (prithivrajmu).
- [33]: tick when Task 4's tally passes.
- [34]: tick for the symlink case when Task 5's `doc-symlink` passes. The other two fixes stay unreached: append one item for them, or ask the owner whether to drop them.
- [105], [106], [120], [121]: tick only on Task 1 Step 6 evidence. Otherwise write a dated `→ progress` note naming the compare range, the untouched functions, the repro result, and that the next compare starts from `d714e536`.
