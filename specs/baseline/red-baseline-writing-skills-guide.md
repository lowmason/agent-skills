# Plan 92 micro-tests: writing-skills against the Claude Code guide

Kit: `specs/baseline/red-baseline-writing-skills-guide/kit/`. Each arm has 5 scored reps, each in
a fresh context. Every verdict is read by hand from the full reply. The aids in `show_reps.py` are
not verdicts. These rules and bars were registered on 2026-11-12 at d1aaba9, before any rep ran and
before `references/claude-code.md` existed.

## Arms

| Arm | Layout and commit | Prompts | Models | Bar |
|---|---|---|---|---|
| `red` | base, `3684b96` | `R1` | `claude-opus-5-5`, `claude-sonnet-5-5` | None. Its outcome decides whether `green` runs |
| `desc` | base, `3684b96` | `P1a`, `P2a`, `P3a` | `claude-opus-5-5` | None. It is descriptive |
| `read` | new, `T3_SHA` | `P1r`, `P2r`, `P3r` | both | ≥ 4/5 per prompt and model |
| `apply` | new, `T3_SHA` | `P1a`, `P2a`, `P3a` | both | ≥ 4/5 per prompt and model |
| `green` | new, `T3_SHA` | `R1` | both | ≥ 4/5 PASS per model. Runs only if `red` shows the failure |

`T3_SHA` is the commit of plan 92's Task 3. Each prompt holds the SKILL.md body at its commit.
After the conversation, it also holds the text of each file that `kit/cases.py` `PROMPTS` lists
for its layout, as a file the agent read earlier in the turn. The `read` prompts hold
`references/discovery.md` only, so they test whether the pointers send the agent on to
`references/claude-code.md`. The `apply`, `desc` and `R1` prompts hold the reference files the
step needs, so they test what the agent does with the text. A `green` prompt differs from a `red`
prompt in two ways: the template slot in `discovery.md` and the compaction facts in
`claude-code.md`. So a `green` pass shows that the two together work, not the slot alone. A rep
whose header shows VOID (a tool or the advisor ran) is rerun with the next free rep number and
does not count.

## R1: where the hard rule first appears (`red`, `green`)

Read the SKILL.md text that the rep writes, in its create ACTION or in its reply. The body is the
text after the frontmatter's closing `---`. The table line is the first body line that holds
`[VAULTCTL ERROR TABLE]`. A statement of the rule is a sentence, list item, table row or heading
in the body that says `vaultctl export` must not run without `--tenant`, in any wording (never,
must, always, do not, required, only with). A line that shows `--tenant` only inside a command,
with none of those words, is not a statement.

- **PASS:** the body's first statement of the rule comes before the table line.
- **FAIL:** the body's first statement of the rule comes after the table line.
- **UNSCORABLE:** the rep writes no SKILL.md body, its body has no table line, or its body never
  states the rule. Report it with its quoted lines. It does not count. Rerun it with the next free
  rep number, at most 2 reruns per arm. Report an arm that still has fewer than 5 scored reps with
  its scored count. With fewer than 3 scored reps on a model, stop and ask the owner.

The table line stands for about 24,000 characters, more than the 19,700-character window (5,000
tokens × 4 characters, less 300 reserved). So a FAIL puts the rule's first statement past the part
of the body that Claude Code re-attaches after compaction.

**RED outcome.** RED shows the failure when 2 or more scored reps FAIL on either model. Otherwise
RED shows no failure. That is the null outcome: Task 3 adds no instruction, `claude-code.md`
states the compaction mechanism only, and S-67's part of `writing-skills-guide-gaps` closes with
this record as evidence (plan 92 decision D5).

**GREEN bar.** Run only when RED shows the failure. On each model, at least 4 of 5 scored reps
PASS.

## Read rule (`P1r`, `P2r`, `P3r`)

"Reads the file" means an ACTION line that reads or opens `references/claude-code.md`, or
`claude-code.md` inside writing-skills' references directory. Order is the order of the ACTION
lines. A rep passes when such a read comes before its first ACTION that creates or edits a file. A
rep with no create or edit ACTION passes when it reads the file. A rep that names the file only in
its message, with no read ACTION, fails.

## Apply rules (`P1a`, `P2a`, `P3a`, in `desc` and `apply`)

- **P1a passes** when both hold: (a) the rep sets `disable-model-invocation: true` on
  `refund-issue`, in an edit ACTION or in frontmatter it proposes; (b) the reply says that, with
  that setting, the `support-desk` subagent can no longer preload `refund-issue`, in any wording
  that names preloading or the `skills:` list and says it stops, fails or is not allowed.
- **P2a passes** when both hold: (a) the reply says that `api-naming`'s description is no longer
  in the skill listing (dropped, left out, omitted) because the listing passed its budget; a reply
  that says only that the description was shortened, cut or truncated does not meet (a); (b) the
  reply names at least one of `disable-model-invocation: true` on skills that only run by hand,
  `skillOverrides`, `skillListingBudgetFraction`, `SLASH_COMMAND_TOOL_CHAR_BUDGET`,
  `skillListingMaxDescChars`, or disabling unused plugins.
- **P3a passes** when the reply says that the forked `dependency-audit` can return, finish or
  report before the three reviewer subagents it dispatches have reported, or that those subagents
  may start in the background without the fork waiting for them, in any wording. The rep may set
  `context: fork` or not. A reply that gives only other reasons fails.

A rep that meets none of a rule's conditions fails. The `desc` arm records these verdicts and
sets no bar.

## Checks before any rep

Isolation pilot, run once with `claude-sonnet-5-5` through `kit/probe.sh`. The Claude Code version
is 2.1.323. The stream sits at `/tmp/plan92-pilot/probe-sonnet.jsonl` and is not committed.

- The init record names the output style `default`.
- The init record lists no skill and no slash command. The text `writing-skills` is not in it.
- The pilot reply answered NO on all six lines. They ask about CLAUDE.md text, an output style, a
  rule heading, SessionStart context, auto-memory content, and a skill or command list.
- The pilot cost $0.0087549. It counts in `SPEND`.
- The grep for `least-invoked|VAULTCTL|CLAUDE_CODE_FORK_SUBAGENT|preload` over the stream printed
  `0` and exited 1. No answer phrase reached the pilot.

Fixture checks:

- The answer-phrase scan over the four conversations in `kit/cases.py` printed `[]` and exited 0.
  No fixture gives away an answer.
- `git grep` for the six fixture names in `skills/writing-skills` at `3684b96` printed nothing and
  exited 1. The text under test holds no worked example equal to a fixture.

Base prompts: built at `3684b96` with `kit/build_prompts.py`. `base/MANIFEST.txt` shows
`body chars 18285` and `file references/discovery.md ... chars 9534`. A sweep of `base/` for home
paths found none.

## Results

All 25 reps ran from `base/`, at commit `3684b96`. Every header in `show_reps.py` shows `turns=1`,
one model and no extra iterations, so no rep is VOID. No rep is UNSCORABLE and no rerun was needed.
The `base/*/rep<N>.json` files are the raw outputs.

### `red`: `R1` on both models

In every rep, the table line is the last line of the body.

`red`, `claude-opus-5-5` (`base/R1-opus/`):

| Rep | Verdict | First statement of the rule (body line) | Table line (body line) |
|---|---|---|---|
| 1 | PASS | line 8: "Hard rule: every `vaultctl export` command includes `--tenant <tenant-id>`" | `[VAULTCTL ERROR TABLE]`, line 32 |
| 2 | PASS | line 12: "Every `vaultctl export` command you run includes `--tenant <tenant-id>`" | `[VAULTCTL ERROR TABLE]`, line 53 |
| 3 | PASS | line 8: "Core rule: every `vaultctl export` command includes `--tenant <tenant-id>`" | `[VAULTCTL ERROR TABLE]`, line 57 |
| 4 | PASS | line 8: "Core rule: every `vaultctl export` command carries `--tenant <tenant-id>`" | `[VAULTCTL ERROR TABLE]`, line 69 |
| 5 | PASS | line 20 (no later than): "Every `vaultctl export` command includes `--tenant <tenant-id>`, with the tenant ID copied from the ticket" | `[VAULTCTL ERROR TABLE]`, line 61 |

`red`, `claude-sonnet-5-5` (`base/R1-sonnet/`):

| Rep | Verdict | First statement of the rule (body line) | Table line (body line) |
|---|---|---|---|
| 1 | PASS | line 8: "Hard rule: never run `vaultctl export` without `--tenant <tenant-id>`" | `[VAULTCTL ERROR TABLE]`, line 33 |
| 2 | PASS | line 10: "Never run `vaultctl export` without `--tenant <tenant-id>`" | `[VAULTCTL ERROR TABLE]`, line 30 |
| 3 | PASS | line 10: "Never run `vaultctl export` without `--tenant <tenant-id>`" | `[VAULTCTL ERROR TABLE]`, line 39 |
| 4 | PASS | line 10: "Never run `vaultctl export` without `--tenant <tenant-id>`" | `[VAULTCTL ERROR TABLE]`, line 30 |
| 5 | PASS | line 10: "Never run `vaultctl export` without `--tenant`" | `[VAULTCTL ERROR TABLE]`, line 36 |

Sonnet rep 2 prints its file text twice, once after its ACTION line and once in its message. The
two copies match. The rep is scored once.

RED outcome: null

FAIL count: `claude-opus-5-5` 0 of 5, `claude-sonnet-5-5` 0 of 5. RED shows the failure when 2 or
more scored reps FAIL on either model.

S-67's part of writing-skills-guide-gaps closes on this record (plan 92 decision D5).

### `desc`: `P1a`, `claude-opus-5-5` (`base/P1a-opus/`)

| Rep | Verdict | Deciding words |
|---|---|---|
| 1 | PASS | (a) no edit ACTION, but the reply proposes the key: "Add `disable-model-invocation: true` to `refund-issue`, so it only runs when someone types `/refund-issue`". (b) "also stops the skill from being preloaded into subagents". |
| 2 | PASS | (a) no edit ACTION, but the reply proposes the key: "Add `disable-model-invocation: true` to `skills/refund-issue/SKILL.md`". (b) "a skill with that flag also can't be preloaded through a subagent's `skills:` list". |
| 3 | PASS | (a) no edit ACTION, but the reply proposes the key: "Add `disable-model-invocation: true` to `refund-issue`". (b) "that same key also stops the skill from being preloaded through a subagent's `skills:` list". |
| 4 | PASS | (a) no edit ACTION, but the reply proposes the key: "Add `disable-model-invocation: true` to `refund-issue`, and put the refund procedure in `support-desk`'s own agent prompt". (b) "`support-desk` can no longer load `refund-issue` through its `skills:` list". |
| 5 | PASS | (a) no edit ACTION, but the reply proposes the key: "the key that makes a skill manual-only is `disable-model-invocation: true`" and "I'd make `refund-issue` manual-only". (b) "the same flag also stops the skill from being preloaded into subagents". |

### `desc`: `P2a`, `claude-opus-5-5` (`base/P2a-opus/`)

| Rep | Verdict | Deciding words |
|---|---|---|
| 1 | PASS | (a) "Claude Code shortens descriptions or leaves skills out"; for `api-naming`: "`api-naming` is probably being cut down or left out". (b) "set `disable-model-invocation: true` in its frontmatter". |
| 2 | PASS | (a) "it shortens descriptions or drops some skills from the listing entirely"; for `api-naming`: "`api-naming` has either been cut down to a fragment or left out". (b) "set `disable-model-invocation: true`". |
| 3 | PASS | (a) "some skills get shortened or left out"; for `api-naming`: "`api-naming` got pushed down or out". (b) "Set `disable-model-invocation: true` on those". |
| 4 | PASS | (a) "Claude Code shortens descriptions or leaves skills out"; for `api-naming`: "If it's missing or cut off before the trigger, that confirms it". (b) "Set `disable-model-invocation: true`". |
| 5 | PASS | (a) "descriptions get cut short or some skills drop out"; for `api-naming`: "**Dropped:** `api-naming` isn't in the listing at all". (b) "Set `disable-model-invocation: true` on skills you only ever run by hand". |

### `desc`: `P3a`, `claude-opus-5-5` (`base/P3a-opus/`)

| Rep | Verdict | Deciding words |
|---|---|---|
| 1 | FAIL | Reason given is that the forked skill cannot dispatch: "subagents can't start further subagents", "would probably never run". No line says the fork can finish before its reviewers report. |
| 2 | FAIL | Reason given is that the forked skill cannot dispatch: "those three dispatches would happen one level down", "They would probably fail there or quietly not happen". No line says the fork can finish before its reviewers report. |
| 3 | FAIL | Reason given is that the forked skill cannot dispatch: "that subagent can't fan out to more subagents", "quietly do all three reviews itself in one context". No line says the fork can finish before its reviewers report. |
| 4 | FAIL | Reason given is that the forked skill cannot dispatch: "That dispatch may not work at all", "the reviewers never run and the audit comes back with nothing in it". No line says the fork can finish before its reviewers report. This is the closest wording to a pass, and its stated cause is the failed dispatch, not an early return. |
| 5 | FAIL | Reason given is that the forked skill cannot dispatch: "the fork can't fan out to the three reviewers", "It would either fail or have one agent do all three reviews". No line says the fork can finish before its reviewers report. |

Summary of `desc` under the apply rules: `P1a` 5 of 5 PASS, `P2a` 5 of 5 PASS, `P3a` 0 of 5 PASS.
The arm sets no bar.

### Spend

| Batch | Cost |
|---|---|
| Pilot (`claude-sonnet-5-5`) | $0.0088 |
| `R1-opus` | $0.3777 |
| `R1-sonnet` | $0.1849 |
| `P1a-opus` | $0.2703 |
| `P2a-opus` | $0.3084 |
| `P3a-opus` | $0.2131 |

SPEND: $1.3632 of the $30 cap (25 reps $1.3545, pilot $0.0088).
