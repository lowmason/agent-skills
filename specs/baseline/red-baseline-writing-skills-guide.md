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

## Review against the guide

This review covers `SKILL.md` and the seven Markdown files that it loads on demand (drift rule
R4.1). It reads them against eight sections of `specs/guides/claude-code-customization-guide.md`:
`skills.locations`, `skills.frontmatter`, `skills.description`, `skills.listing-budget`,
`skills.progressive-disclosure`, `subagents.frontmatter`, `subagents.models` and
`subagents.isolation`. The guide on this branch is the guide on `origin/main` (see below).

- Paths are relative to `skills/writing-skills/`. Line numbers are those of the commit that adds
  this section.
- A row records a statement only when its truth depends on Claude Code. Statements about the Agent
  Skills spec, this repo's lints, other runtimes or claude.ai are not rows.
- Task 3 Step 1's fact-to-section table seeded the `claude-code.md` rows.
- A file with no Claude Code statement has one row that says so, with `—` as its verdict.
- A fixed row gives the statement as it was before the fix. Its note gives the fix.

| # | File:line | Statement, in the repo's words | Guide section | Verdict | Note |
|---|---|---|---|---|---|
| 1 | `SKILL.md:23` | Claude Code keeps personal skills in `~/.claude/skills/`. | `skills.locations` | covered | The personal row puts each skill at `~/.claude/skills/<name>/`, for every project on the machine. |
| 2 | `SKILL.md:89-91`, `:178-179`, `:185-189` | A skill folder holds `SKILL.md`, depth in `references/` that loads on demand, and tools in `scripts/`. | `skills.progressive-disclosure` | covered | The third tier is the bundled files, which load only when the body names them. The section also puts deterministic logic in `scripts/`. |
| 3 | `SKILL.md:94` | All skills sit in one flat namespace: each skill is a folder directly under the skills folder. | `skills.locations` | covered | The location rows put each skill at `<root>/<name>/`. Plugin skills (`plugin:skill`) and skills in nested project folders (`dir:name` on a clash) get a prefix. The line describes one skills folder and says nothing about those two cases. |
| 4 | `SKILL.md:111-114` | Claude Code's listing can drop descriptions, and only part of a body survives compaction. | `skills.listing-budget`, `skills.progressive-disclosure` | covered | On overflow, the listing drops whole descriptions. After compaction, each re-attached body keeps only its first 5,000 tokens. |
| 5 | `SKILL.md:122-124` | A description states only when to use the skill, not what the skill does. | `skills.description` | contradicted | The guide asks for both what the skill does and when to use it. The register holds this as deviation `description-when-only`, the owner's standing decision. Not fixed: plan 92 changes no description rule. |
| 6 | `SKILL.md:330` | A single-shot subagent gives a fresh-context sample. | `subagents.isolation` | covered | A subagent starts from its own prompt, not from the parent's conversation. A fork is the exception: it starts with the whole conversation. Most agents also start with the CLAUDE.md files and a snapshot of git status. The line names neither case. |
| 7 | `SKILL.md:392` | The description is in the third person. | `skills.description` | covered | |
| 8 | `SKILL.md:425` | Skill names and descriptions load before any skill triggers, and an overfull listing can lose descriptions. | `skills.listing-budget` | covered | |
| 9 | `SKILL.md:426` | An agent finds a skill when its description matches the task. | `skills.description` | covered | Claude picks a skill from its name and description only. |
| 10 | `SKILL.md:429` | An agent loads a skill's example only when it implements. | `skills.progressive-disclosure` | covered | Bundled files load only when the body sends Claude to them. |
| 11 | `references/claude-code.md:10` | Claude Code reads the listed keys beyond the Agent Skills spec's own keys. | `skills.frontmatter` | covered | Each listed key has a row in the table. The guide lists more keys, but the sentence does not say that its list is complete. |
| 12 | `references/claude-code.md:12-13` | `when_to_use` adds trigger text to the description, and the two share one listing entry and its length cap. | `skills.frontmatter`, `skills.listing-budget` | covered | The `when_to_use` row, and the bullet on the per-entry cap. |
| 13 | `references/claude-code.md:14-15` | `model` sets the model for the rest of the turn, and `effort` sets the effort while the skill is active. | `skills.frontmatter` | covered | The `model` / `effort` row. |
| 14 | `references/claude-code.md:15-16` | With `context: fork`, `model` sets the model of the forked subagent instead. | `skills.frontmatter` | covered | The `model` / `effort` row. |
| 15 | `references/claude-code.md:17-18` | `context: fork` runs the body in an isolated subagent that does not see the conversation, so the body must stand alone. | `skills.frontmatter` | covered | The `context: fork` row. |
| 16 | `references/claude-code.md:18` | Only the subagent's final text comes back. | `subagents.isolation` | covered | What a subagent reads stays in its own context. The parent gets back only the final text. |
| 17 | `references/claude-code.md:19` | `agent` names the agent type that runs a forked skill, `general-purpose` by default. | `skills.frontmatter` | covered | The `agent` row. |
| 18 | `references/claude-code.md:20-21` | With `disable-model-invocation: true`, Claude never starts the skill on its own and the skill leaves the listing. `/name` at the start of a message runs it. | `skills.frontmatter` | covered | The `disable-model-invocation` row. |
| 19 | `references/claude-code.md:21-22` | A subagent cannot preload that skill through its `skills` field. | `skills.frontmatter`, `subagents.frontmatter` | covered | The `disable-model-invocation` row and the subagent `skills` row both say so. |
| 20 | `references/claude-code.md:24` | Claude Code ignores an unknown or misspelled key and gives no error. | `skills.frontmatter` | covered | The row on the spec fields. |
| 21 | `references/claude-code.md:28-29` | In auto mode, Claude Code ignores a skill `model` that auto mode does not support, Haiku 4.5 and earlier among them, and the session model runs. | `skills.frontmatter` | covered | The `model` / `effort` row. The guide also names plan mode when the auto-mode classifier checks commands. The file leaves that case out, which does not make the sentence wrong. |
| 22 | `references/claude-code.md:29-31` | `haiku` means Haiku 5.5 on the Anthropic API, and Haiku 4.5 on Amazon Bedrock, Google Cloud's Agent Platform, Microsoft Foundry and Claude Platform on AWS. | `subagents.models` | covered | The section's opening paragraph and its first caveat name the same providers. The `skills.frontmatter` `model` row also gives Haiku 5.5 on the Anthropic API. |
| 23 | `references/claude-code.md:31-32` | So `model: haiku` applies on one provider and is ignored on another. | `skills.frontmatter`, `subagents.models` | covered | It follows from rows 21 and 22. It holds in auto mode, which the paragraph's first words set. Outside auto mode, the guide gives no rule that ignores the key. |
| 24 | `references/claude-code.md:36` | Fork a skill whose value is a verdict or an artifact. Do not fork a skill whose value is guidance, because guidance must stay in the main conversation. | `skills.frontmatter`, `subagents.isolation` | covered | A forked body runs in a subagent that does not see the conversation, and only its final text comes back. So the body's guidance never reaches the main thread. |
| 25 | `references/claude-code.md:36` | `context` applies to the whole skill, so do not fork a skill that mixes artifact and question operations. | `skills.frontmatter` | covered | `context` is one frontmatter key for each skill, with the one value `fork`. |
| 26 | `references/claude-code.md:38-40` | With fork mode off, the subagents that a subagent starts in `claude -p` and the Agent SDK start in the background. So a forked skill can return before its own subagents report. | `subagents.frontmatter` | covered | The `background` row: with fork mode off in those two, the subagents that a subagent starts run in the background. The row also cites a changelog that adds the desktop app and VS Code. |
| 27 | `references/claude-code.md:41` | Fork mode is on by default. | `subagents.frontmatter`, `subagents.isolation` | covered | The terminal has it on by default. Since 2.1.302, so do `claude -p`, the Agent SDK, the desktop app and VS Code. |
| 28 | `references/claude-code.md:45-48` | Before any skill triggers, Claude Code loads skill names and descriptions within a budget. Every name stays. On overflow, it drops whole descriptions, starting with the skills invoked least. A skill without its description still runs by name but rarely triggers on its own. | `skills.listing-budget`, `skills.progressive-disclosure` | covered | |
| 29 | `references/claude-code.md:50-51` | `/doctor`, `/skill-doctor` and the Skills row of `/context` show what the listing costs. | `skills.listing-budget` | covered | |
| 30 | `references/claude-code.md:52` | `disable-model-invocation: true` takes a skill out of the listing. | `skills.listing-budget` | covered | |
| 31 | `references/claude-code.md:53-54` | `skillOverrides` lists a skill by name only, hides it from Claude or turns it off, and does not reach plugin skills. | `skills.listing-budget` | covered | |
| 32 | `references/claude-code.md:55-56` | `skillListingBudgetFraction` and `SLASH_COMMAND_TOOL_CHAR_BUDGET` change the budget, and `skillListingMaxDescChars` changes the cap on each entry. | `skills.listing-budget` | covered | |
| 33 | `references/claude-code.md:57` | A plugin's whole skill set joins the listing. | `skills.listing-budget` | covered | |
| 34 | `references/claude-code.md:61-64` | An invoked body stays for the rest of the session. After compaction, Claude Code re-attaches the latest invocation of each skill and keeps its first 5,000 tokens. The re-attached bodies share 25,000 tokens, and the newest goes in first. | `skills.progressive-disclosure` | covered | |
| 35 | `references/discovery.md:11` | `when_to_use`, `model`, `effort`, `context`, `agent` and `disable-model-invocation` are Claude Code extensions beyond the spec's keys. | `skills.frontmatter` | covered | Each key has a row in the table. The guide calls `license`, `compatibility` and `metadata` spec fields. The clause that a claude.ai upload rejects the extensions is a claude.ai claim, outside this review. |
| 36 | `references/discovery.md:11` | A Haiku `model` is not portable, and cheap work belongs on a subagent with a pinned model. | `subagents.models`, `skills.frontmatter`, `subagents.frontmatter` | covered | Rows 21 to 23 give the reason. The subagent `model` row lets an agent pin its own model. |
| 37 | `references/discovery.md:13`, `:79` | Write the description in the third person. | `skills.description` | covered | |
| 38 | `references/discovery.md:13`, `:16`, `:80` | A description says only when to use the skill and never summarizes its workflow. | `skills.description` | contradicted | As row 5: deviation `description-when-only`, not fixed. The deviation's `artifacts` glob is `skills/*/SKILL.md`, which does not name this file. |
| 39 | `references/discovery.md:58` | An agent reads the description to choose which skills to load. | `skills.description` | covered | |
| 40 | `references/discovery.md:75` | A description uses concrete triggers, symptoms and situations. | `skills.description` | covered | |
| 41 | `references/discovery.md:79` | The description goes into the system prompt. | `skills.listing-budget` | not covered | The cited sections say only that the listing is always loaded. None of them says where in the context the listing sits. |
| 42 | `references/discovery.md:115` | The description is the only text of a skill that loads before the skill triggers. | `skills.listing-budget`, `skills.progressive-disclosure` | contradicted | The first tier is the name and the description, and every name stays listed. Fixed in this commit: the line now starts "apart from its name". The pointer clause after it is unchanged. |
| 43 | `references/discovery.md:116-117` | A runtime may drop or shorten the description when its listing overflows. Claude Code's rule is in `claude-code.md`. | `skills.listing-budget` | covered | Claude Code drops whole descriptions. |
| 44 | `references/discovery.md:117`, `:128` | The body costs context only when the skill triggers. | `skills.progressive-disclosure` | covered | |
| 45 | `references/discovery.md:118`, `:132` | `references/` files load only when the body sends the agent there. | `skills.progressive-disclosure` | covered | |
| 46 | `references/discovery.md:121` | The description loads before the skill triggers. | `skills.listing-budget` | covered | |
| 47 | `references/discovery.md:122-123` | The description is the only text that takes context in conversations where the skill never runs. | `skills.listing-budget`, `skills.progressive-disclosure` | contradicted | As row 42: the name is in the listing too. Fixed in this commit: the clause now starts "apart from the name". |
| 48 | `references/discovery.md:153` | A good example of a cross-reference says that subagents save 50 to 100 times the context. | `subagents.isolation` | not covered | The section says that what a subagent reads stays in its own context and that only the final text comes back. It gives no factor for the saving. The line sits in a ✅ GOOD example. |
| 49 | `references/discovery.md:202` | A bare skill name lets each runtime load the skill through its own mechanism. | `skills.frontmatter` | covered | In Claude Code, the `name` and the folder name both invoke the skill. |
| 50 | `references/flowcharts.md` | No statement depends on Claude Code. | — | — | Graphviz style and the render script only. |
| 51 | `references/bulletproofing.md` | No statement depends on Claude Code. | — | — | Its advice on descriptions holds on every runtime. |
| 52 | `testing-skills-with-subagents.md` | No statement depends on Claude Code. | — | — | It gives a test method. It makes no claim about how Claude Code runs subagents. |
| 53 | `persuasion-principles.md` | No statement depends on Claude Code. | — | — | |
| 54 | `examples/CLAUDE_MD_TESTING.md:16`, `:46`, `:60` | A scenario offers to check `~/.claude/skills/`, or one skill folder in it, before work starts. | `skills.locations` | covered | `debugging/` and `coding/` read as skill folders, at `<name>/` under the personal root. |
| 55 | `examples/CLAUDE_MD_TESTING.md:73`, `:81`, `:84-85`, `:92`, `:95`, `:122-123` | A variant puts the personal skills library at `~/.claude/skills/`, and browses or searches it there. | `skills.locations` | covered | |
| 56 | `examples/CLAUDE_MD_TESTING.md:34`, `:94`, `:107` | Skills sit in category folders under `~/.claude/skills/`, one level above each skill. | `skills.locations` | not covered | `:34` reads as a `testing/` folder that holds an async-testing skill. The guide puts each personal skill at `~/.claude/skills/<name>/`. It does not say whether a skill one folder deeper loads. |

Counts: 45 covered, 4 contradicted, 3 not covered, and 4 files with no Claude Code statement.

### Contradicted rows

- **Rows 5 and 38** contradict `skills.description`. The register records the contradiction as
  deviation `description-when-only`, so it stays as it is (the `/cc-guide` rule for a registered
  deviation). The plan changes no description rule.
- **Rows 42 and 47** are fixed in this commit, in `references/discovery.md`. Each fix adds the name
  to what loads before a skill triggers. It is a factual edit under spec D4, and it adds no
  instruction. The pointer clause at `:116-117`, which Task 4 tested, keeps its words.

### Not covered rows, for the owner

The owner rules on each row at the plan's completion gate.

- **Row 41:** `discovery.md:79` gives "injected into system prompt" as the reason for the third
  person. No cited section says where the listing sits.
- **Row 48:** `discovery.md:153`, inside a ✅ GOOD example, says that subagents save 50 to 100
  times the context. The guide gives no factor for the saving.
- **Row 56:** `CLAUDE_MD_TESTING.md:34`, `:94` and `:107` put skills in category folders under
  `~/.claude/skills/`. The guide gives only the `<name>/` level.

### The guide on `origin/main`

`git fetch origin` ran on 2026-11-12. The merge base of this branch and `origin/main` is `9a164c9`,
which is also `origin/main`. `git diff` of the guide from the merge base to `origin/main` printed
nothing. No cited section changed, so there was no merge and no second review.

### Citation

Each of the eight sections has at least one covered row. So the `SKILL.md` citation names all
eight, in the plan's order. `cli.py baseline cite` restamped it at `@2.1.306` and recorded each
section's `text_hash` in `build/cc_guide/baseline.json`.

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

Readings behind the `P1a(a)` and `P2a(a)` verdicts. Each is a reading of the registered text. Each
was applied to all five reps of its prompt. Each rep was re-read in full for this note.

- `P1a(a)`. A reply that holds the edit back and recommends, in prose, adding
  `disable-model-invocation: true` to `refund-issue` meets "in frontmatter it proposes". The
  stricter reading needs an edit ACTION or a frontmatter block shown in the reply. Under it, all 5
  reps FAIL (a). None has an ACTION line, a frontmatter block or a code fence. Each names the key
  only in prose. Quoted phrase per rep: 1 "Add `disable-model-invocation: true` to `refund-issue`,
  so it only runs when someone types `/refund-issue`". 2 "Add `disable-model-invocation: true` to
  `skills/refund-issue/SKILL.md`". 3 "Add `disable-model-invocation: true` to `refund-issue`".
  4 "Add `disable-model-invocation: true` to `refund-issue`, and put the refund procedure in
  `support-desk`'s own agent prompt". 5 "I'd make `refund-issue` manual-only".
- `P2a(a)`. The exclusion covers a reply that says only that the description was shortened, cut or
  truncated. A reply that names "left out" or "dropped" next to "shortened" is not "only". So it
  meets (a), even if it does not say which outcome happened. The stricter reading needs the reply
  to say that `api-naming` is no longer listed. Under it, all 5 reps FAIL (a). Each names the
  outcome for `api-naming` only as one of two possibilities. Quoted phrase per rep: 1
  "`api-naming` is probably being cut down or left out". 2 "`api-naming` has either been cut down
  to a fragment or left out". 3 "`api-naming` got pushed down or out". 4 "If it's missing or cut
  off before the trigger, that confirms it" (its other line on `api-naming` says only "If
  `api-naming` gets cut"). 5 "**Dropped:** `api-naming` isn't in the listing at all", which it
  lists beside "**Shortened:**" as the two cases that the `/doctor` warning would tell apart.

The `apply` arm applies the same two readings, so the `desc` and `apply` pass counts for `P1a` and
`P2a` compare like for like. For these two prompts, the counts are correspondingly loose. A `P1a`
pass does not show an edit. A `P2a` pass does not show a claim that the skill left the listing.

### New layout at `942fee0`: the `read` and `apply` arms

`T3_SHA` is `942fee0`. `new/MANIFEST.txt` shows `body chars 18753`, `file references/discovery.md`
at 9,052 characters and `file references/claude-code.md` at 3,929 characters. The `git grep` for the
six fixture names in `skills/writing-skills` at `942fee0` printed nothing and exited 1. `RED outcome:
null`, so `new/R1.txt` is built and not run, and there is no `green` arm. The `new/*/rep<N>.json` files
are the raw outputs. A rep is VOID if its `show_reps.py` header shows a tool or the advisor ran.

#### `read`: `P1r`

Each rep has one ACTION line, a read, and no create or edit ACTION. So every pass in this section
comes from the no-edit clause of the read rule ("a rep with no create or edit ACTION passes when it
reads the file"). The reply of each rep holds the edit back until it has read the file.

`read`, `P1r`, `claude-opus-5-5` (`new/P1r-opus/`): 5 of 5 PASS, 5 from the no-edit clause.

| Rep | Verdict | Deciding ACTION line |
|---|---|---|
| 1 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md` |
| 2 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md` |
| 3 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md` |
| 4 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md` |
| 5 | PASS (no-edit clause) | `ACTION: Read` the same path, in backticks |

`read`, `P1r`, `claude-sonnet-5-5` (`new/P1r-sonnet/`): 5 of 5 PASS, 5 from the no-edit clause.

| Rep | Verdict | Deciding ACTION line |
|---|---|---|
| 1 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md` |
| 2 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md` |
| 3 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md`, then a sentence of reason on the same line |
| 4 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md` |
| 5 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md` |

#### `read`: `P2r`

Each rep has a read as its first ACTION line and no create or edit ACTION. Two reps add a second
ACTION that only runs a listing command (Opus rep 3, Sonnet rep 2). It is not a create or an edit,
and it comes after the read. So every pass in this section comes from the no-edit clause.

`read`, `P2r`, `claude-opus-5-5` (`new/P2r-opus/`): 5 of 5 PASS, 5 from the no-edit clause.

| Rep | Verdict | Deciding ACTION line |
|---|---|---|
| 1 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md (discovery.md defers to it ...)` |
| 2 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md` |
| 3 | PASS (no-edit clause) | `ACTION: Read` the same path, in backticks. The next ACTION runs `ls` on the skills and plugins directories, a listing and not an edit |
| 4 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md` |
| 5 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md (discovery.md defers to it ...)` |

`read`, `P2r`, `claude-sonnet-5-5` (`new/P2r-sonnet/`): 5 of 5 PASS, 5 from the no-edit clause.

| Rep | Verdict | Deciding ACTION line |
|---|---|---|
| 1 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md. discovery.md defers to it ...` |
| 2 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md for how Claude Code's skill listing drops descriptions ...`. The next ACTION lists and measures installed skills, which is not an edit |
| 3 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md. discovery.md defers to it ...` |
| 4 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md for Claude Code's exact listing rule ...` |
| 5 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md, the file discovery.md points to ...` |

#### `read`: `P3r`

Each rep has one ACTION line, a read, and no create or edit ACTION. So every pass in this section
comes from the no-edit clause.

`read`, `P3r`, `claude-opus-5-5` (`new/P3r-opus/`): 5 of 5 PASS, 5 from the no-edit clause.

| Rep | Verdict | Deciding ACTION line |
|---|---|---|
| 1 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md` |
| 2 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md` |
| 3 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md` |
| 4 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md` |
| 5 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md` |

`read`, `P3r`, `claude-sonnet-5-5` (`new/P3r-sonnet/`): 5 of 5 PASS, 5 from the no-edit clause.

| Rep | Verdict | Deciding ACTION line |
|---|---|---|
| 1 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md.` then a sentence of reason on the same line |
| 2 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md` |
| 3 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md` |
| 4 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md` |
| 5 | PASS (no-edit clause) | `ACTION: Read ~/.claude/skills/writing-skills/references/claude-code.md` |

#### `apply`: `P1a`

The `apply` arm uses the `P1a(a)` and `P2a(a)` readings of the `desc` note above, unchanged. No rep
has an edit ACTION or a frontmatter block. Every rep holds the edit back and names the key in prose
as the change it recommends, which meets (a) under that reading. Sonnet rep 5 has one ACTION, a
`Glob` for the agent file, which is a read.

`apply`, `P1a`, `claude-opus-5-5` (`new/P1a-opus/`): 5 of 5 PASS.

| Rep | Verdict | Deciding words |
|---|---|---|
| 1 | PASS | (a) "`skills/refund-issue/SKILL.md`: add `disable-model-invocation: true`". (b) "`support-desk` loses the skill and can no longer issue refunds", quoting that "a subagent cannot preload the skill through its `skills` field". |
| 2 | PASS | (a) "Set `disable-model-invocation: true` on `refund-issue` so it only runs when one of you types it". (b) "If I add it, `/refund-issue` works for you, but `support-desk` loses the skill", quoting "A subagent cannot preload the skill through its `skills` field." |
| 3 | PASS | (a) "Add `disable-model-invocation: true` to `skills/refund-issue/SKILL.md`". (b) "that setting also means 'a subagent cannot preload the skill through its `skills` field.'" |
| 4 | PASS | (a) "Add `disable-model-invocation: true` to `refund-issue`" (option 1). (b) "that same key also stops a subagent from preloading the skill through its `skills` field". |
| 5 | PASS | (a) "Add `disable-model-invocation: true` to `refund-issue`". (b) "`support-desk` can no longer preload `refund-issue`". |

`apply`, `P1a`, `claude-sonnet-5-5` (`new/P1a-sonnet/`): 5 of 5 PASS.

| Rep | Verdict | Deciding words |
|---|---|---|
| 1 | PASS | (a) "set `disable-model-invocation: true`, so only a typed `/refund-issue` runs it". (b) "a subagent cannot preload it through its `skills:` list. With that key, `support-desk` loses `refund-issue`". |
| 2 | PASS | (a) "set `disable-model-invocation: true` on `refund-issue`". (b) "a subagent can't preload the skill through its `skills:` list. Setting it would silently break `support-desk`". |
| 3 | PASS | (a) "Add `disable-model-invocation: true` to `skills/refund-issue/SKILL.md`". (b) "it also stops a subagent from preloading the skill through its `skills:` list, so `support-desk` would lose it". |
| 4 | PASS | (a) "add `disable-model-invocation: true` to `refund-issue`". (b) "It also blocks a subagent from preloading the skill through `skills:`". |
| 5 | PASS | (a) "Add `disable-model-invocation: true` to `skills/refund-issue/SKILL.md`". (b) "a subagent can't preload it through `skills:`. So `support-desk` would lose the skill." |

#### `apply`: `P2a`

The `apply` arm uses the `P2a(a)` reading of the `desc` note above, unchanged. In all 10 reps the
reply says the description is dropped from the listing, and none says only "shortened" or "cut". No
rep has an ACTION line that edits.

`apply`, `P2a`, `claude-opus-5-5` (`new/P2a-opus/`): 5 of 5 PASS.

| Rep | Verdict | Deciding words |
|---|---|---|
| 1 | PASS | (a) "`api-naming` skill is very likely losing its description to the skill-listing budget" and "Whole descriptions are dropped, starting with the skills invoked least". (b) "add `disable-model-invocation: true` to the frontmatter", `skillOverrides`, `skillListingBudgetFraction`, `SLASH_COMMAND_TOOL_CHAR_BUDGET`. |
| 2 | PASS | (a) "drops **whole descriptions**" and "`api-naming` probably fell into that group", with "the description gone". (b) "Set `disable-model-invocation: true` on your own skills that you always run by hand", `skillOverrides`, `skillListingBudgetFraction`, `SLASH_COMMAND_TOOL_CHAR_BUDGET`. |
| 3 | PASS | (a) "`api-naming`'s description was one of the ones it dropped". (b) "`disable-model-invocation: true`", `skillOverrides`, `skillListingBudgetFraction`, `SLASH_COMMAND_TOOL_CHAR_BUDGET`, `skillListingMaxDescChars`. |
| 4 | PASS | (a) "Claude Code is dropping that skill's description from it". (b) "`disable-model-invocation: true`", `skillOverrides`, `skillListingBudgetFraction`, `SLASH_COMMAND_TOOL_CHAR_BUDGET`, `skillListingMaxDescChars`. |
| 5 | PASS | (a) "`api-naming` lost its description from the skill listing" and "Its description gets dropped". (b) "add `disable-model-invocation: true` to the frontmatter", `skillOverrides`, `skillListingBudgetFraction`. |

`apply`, `P2a`, `claude-sonnet-5-5` (`new/P2a-sonnet/`): 5 of 5 PASS.

| Rep | Verdict | Deciding words |
|---|---|---|
| 1 | PASS | (a) "Auto-triggering stopped because the description is no longer in the listing." (b) "Set `disable-model-invocation: true` on your own skills that you only ever run by typing `/name`", `skillListingBudgetFraction`, `SLASH_COMMAND_TOOL_CHAR_BUDGET`, `skillListingMaxDescChars`. |
| 2 | PASS | (a) "the skill listing is over its budget and `api-naming`'s description was dropped". (b) "Set `disable-model-invocation: true` on skills you only ever run by typing `/name`", `skillListingBudgetFraction`, `SLASH_COMMAND_TOOL_CHAR_BUDGET`. |
| 3 | PASS | (a) "the skill listing is over budget, and `api-naming`'s description was dropped from it". (b) "Set `disable-model-invocation: true` on skills you only ever run by hand", `skillListingBudgetFraction`, `SLASH_COMMAND_TOOL_CHAR_BUDGET`, `skillListingMaxDescChars`. |
| 4 | PASS | (a) "Most likely `api-naming`'s description was dropped from the skill listing". (b) "Add `disable-model-invocation: true` to your own skills that you only ever run by hand", `skillListingBudgetFraction`, `SLASH_COMMAND_TOOL_CHAR_BUDGET`, `skillListingMaxDescChars`. |
| 5 | PASS | (a) "Most likely `api-naming`'s description was dropped from the skill listing". (b) "Set `disable-model-invocation: true` on skills you only ever run by typing `/name`", `skillListingBudgetFraction`, `SLASH_COMMAND_TOOL_CHAR_BUDGET`, `skillListingMaxDescChars`. |

#### `apply`: `P3a`

In all 10 reps, the reply says that the forked skill can return before the reviewers report, tied to
`CLAUDE_CODE_FORK_SUBAGENT=0` in `claude -p`. No ACTION line edits in the Opus reps. Each Sonnet rep
has an edit ACTION that adds `context: fork`, and warns of the early return in the same reply.

`apply`, `P3a`, `claude-opus-5-5` (`new/P3a-opus/`): 5 of 5 PASS.

| Rep | Verdict | Deciding words |
|---|---|---|
| 1 | PASS | "Under `claude -p` with fork mode off (`CLAUDE_CODE_FORK_SUBAGENT=0`), those nested subagents start in the background. The forked skill can then return its "merged" report before the license, CVE or pin reviewers have reported." |
| 2 | PASS | "subagents started by a subagent run in the background. The forked skill could then return its "merged" report before the reviewers have reported." |
| 3 | PASS | "subagents started by a forked skill under `claude -p` run in the background. The forked skill can then return before the license, CVE and pin reviewers report." |
| 4 | PASS | "A forked `dependency-audit` could then return its merged report before the license, CVE or pin reviewers have reported." |
| 5 | PASS | "The forked skill can then return its "merged" report before the license, CVE and pin reviewers have reported." |

`apply`, `P3a`, `claude-sonnet-5-5` (`new/P3a-sonnet/`): 5 of 5 PASS.

| Rep | Verdict | Deciding words |
|---|---|---|
| 1 | PASS | "the nested subagents start in the background. The forked skill could then return before the licenses, CVE and version-pin reviewers report". Its ACTIONs set `context: fork`. |
| 2 | PASS | "The forked skill could then return before the reviewers report, and the nightly report would be missing findings." Its ACTIONs set `context: fork`. |
| 3 | PASS | "the reviewers start in the background. The forked skill can then return before they report". Its ACTION sets `context: fork`. |
| 4 | PASS | "the nested subagents in `claude -p` run in the background, and the forked skill can return before they report". Its ACTIONs set `context: fork`. |
| 5 | PASS | "subagents started inside `claude -p` run in the background. The forked skill can then return before the license, CVE and version-pin reviewers report". Its ACTIONs set `context: fork`. |

### Summary of every bar in the new layout (`942fee0`)

No rep is VOID or UNSCORABLE, and no rerun was needed. Every bar is met on the first 5 reps, so no
tightening round ran and `942fee0` is the only text under test.

| Arm | Prompt | Model | Score | Bar | Verdict |
|---|---|---|---|---|---|
| `read` | `P1r` | `claude-opus-5-5` | 5 of 5 | 4 of 5 | met |
| `read` | `P1r` | `claude-sonnet-5-5` | 5 of 5 | 4 of 5 | met |
| `read` | `P2r` | `claude-opus-5-5` | 5 of 5 | 4 of 5 | met |
| `read` | `P2r` | `claude-sonnet-5-5` | 5 of 5 | 4 of 5 | met |
| `read` | `P3r` | `claude-opus-5-5` | 5 of 5 | 4 of 5 | met |
| `read` | `P3r` | `claude-sonnet-5-5` | 5 of 5 | 4 of 5 | met |
| `apply` | `P1a` | `claude-opus-5-5` | 5 of 5 | 4 of 5 | met |
| `apply` | `P1a` | `claude-sonnet-5-5` | 5 of 5 | 4 of 5 | met |
| `apply` | `P2a` | `claude-opus-5-5` | 5 of 5 | 4 of 5 | met |
| `apply` | `P2a` | `claude-sonnet-5-5` | 5 of 5 | 4 of 5 | met |
| `apply` | `P3a` | `claude-opus-5-5` | 5 of 5 | 4 of 5 | met |
| `apply` | `P3a` | `claude-sonnet-5-5` | 5 of 5 | 4 of 5 | met |

No-edit clause in the `read` arm: 30 of the 30 passes come from it. No `read` rep has a create or
edit ACTION, so no rep ever reached the point where the order of the read and the first edit could
matter. The `read` arm therefore shows that, on its first ACTION line, every rep sends itself to read
`references/claude-code.md` after it has seen the pointer in `discovery.md`. It does not show that a
rep reads the file before an edit it goes on to make.

Compared with `desc` on Opus, `apply` on Opus scores `P1a` 5 of 5 against 5 of 5, `P2a` 5 of 5 against
5 of 5, and `P3a` 5 of 5 against 0 of 5. The two arms differ in layout (the `apply` prompt holds
`references/claude-code.md`, the `desc` prompt does not), and each arm has 5 reps on one model, so the
comparison is descriptive and no bar applies to it.

### Spend

| Batch | Cost |
|---|---|
| Pilot (`claude-sonnet-5-5`) | $0.0088 |
| `R1-opus` | $0.3777 |
| `R1-sonnet` | $0.1849 |
| `P1a-opus` | $0.2703 |
| `P2a-opus` | $0.3084 |
| `P3a-opus` | $0.2131 |
| `P1r-opus` | $0.1965 |
| `P1r-sonnet` | $0.0972 |
| `P2r-opus` | $0.2168 |
| `P2r-sonnet` | $0.1188 |
| `P3r-opus` | $0.1831 |
| `P3r-sonnet` | $0.0930 |
| `P1a-opus` (new) | $0.2544 |
| `P1a-sonnet` (new) | $0.1404 |
| `P2a-opus` (new) | $0.2504 |
| `P2a-sonnet` (new) | $0.1303 |
| `P3a-opus` (new) | $0.2428 |
| `P3a-sonnet` (new) | $0.1452 |

SPEND: $3.4320 of the $30 cap. The 25 `base/` reps cost $1.3545, the 60 `new/` reps $2.0688 and the
pilot $0.0088. The `green` arm did not run.
