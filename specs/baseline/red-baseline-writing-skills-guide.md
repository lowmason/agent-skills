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

## Results
