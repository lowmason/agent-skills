# writing-skills: analysis and proposed improvements — Design Spec

**Status: COMPLETE (2026-11-25)** — implemented by plans 105, 107 and 108
(`specs/plans/completed/105-writing-skills-improvements.md`,
`specs/plans/completed/107-writing-skills-improvements.md` and
`specs/plans/completed/108-writing-skills-improvements.md`) and retired here. The owner ruled on every open
question on 2026-11-22 (see Owner decisions), then approved the whole spec for planning the same day. No
brainstorming ran. Items 3b, 10, 13 and 16 stay open, and each has an item in `specs/deferred_items.md`.

> ⚠️ Quarantine this file during any later micro-test of writing-skills. Items 1, 2 and 10 name the
> RED scenarios and what they score, so a rep that reads this file is void.

**Scope:** `skills/writing-skills/` only. The spec also names the register entries, backlog items and
`NOTICE` lines that each change reaches. It proposes no change to any other skill.

**Lenses.** The request came through plugin-dev's skill-development skill. This spec also reads
writing-skills against Anthropic's skill best-practices page, which `SKILL.md:31` links
(<https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>, read 2026-11-22),
and against this repository's guide, lints and records. Where a lens disagrees with a house rule, the
house rule governs. Considered and not proposed gives the reason for each case.

## What works

- **The description routes well.** It is trigger-only, 398 characters, and well inside the 1,024 cap.
  `CLAUDE.md` sends every runtime here, so the skill is the repository's routing hook for skill edits.
- **Match the Form to the Failure** (`SKILL.md:278-293`) is the strongest section. It classifies the
  failure before it picks a form of guidance. Head-to-head wording tests back its rules. Anthropic's
  prompting page gives a narrower form of the idea, for output format only. It says to tell Claude what
  to do instead of what not to do. Neither Anthropic page classifies the failure or measures a backfire.
- **The micro-test steps are sound** (`SKILL.md:326-336`). They ask for a no-guidance control, five or
  more reps, a manual read of every flagged match, and variance as a metric. Anthropic's page asks for
  the same order: a baseline first, then the smallest text that passes.
- **The split holds.** Plans 72 and 92 moved depth into `references/` and put the Claude Code facts in
  one file, `references/claude-code.md`. Each pointer sits at the step that needs it.
- **The body fits.** It has 427 lines, under the 500 lines that Anthropic's page advises. It has 18,753
  characters, inside the compaction window that `build/check_conformance.py` enforces.

## Summary

Each row is one proposed change, ranked by the harm the defect does today and by how cheap the fix is.

| Rank | Item | Kind | Body change (characters) | Test | Size | Linked backlog item |
|---|---|---|---|---|---|---|
| 1 | Describe the micro-test method in full | gap | about +100 | RED first | plan | none |
| 2 | Add a trigger test | gap | about +120 | RED first | plan | Trigger-eval suites |
| 3 | Refresh the Codex cut, and front-load the skill's own description | defect | 0 | waiver, then a trigger test | quick-fix, then plan | Trigger-eval suites |
| 4 | Fix `render-graphs.js` (Q1: port to Python) | defect | 0 | script test | plan, with item 8 | none |
| 5 | Fix the worked example | defect | 0 | waiver | quick-fix | none |
| 6 | Scope the persuasion evidence | defect | 0 | waiver (owner ruling) | quick-fix | none |
| 7 | Settle which reference-skill tests apply | defect | 0 | waiver | quick-fix | none |
| 8 | Bring support files one level from SKILL.md | structure | 0 to about +150 | guard run | plan | the `t3` read-then-use item |
| 9 | Name a test for edits that keep behavior | gap | about +200 | pressure test | design | register `writing-skills-tdd-for-docs` |
| 10 | Add a rename procedure | gap | 0 | application test | quick-fix | none |
| 11 | Add tables of contents | structure | 0 | waiver | quick-fix | none |
| 12 | Use one list of skill types | structure | about +80 | waiver | quick-fix | none |
| 13 | Name the `agy` skills folder | defect | about +40 | waiver | part of a plan | the `agy` instructions item |
| 14 | Match the example language to the stack | defect | about −40 | waiver (owner ruling) | quick-fix | none |
| 15 | Delete the dated session report | defect | 0 | waiver | quick-fix | none |
| 16 | Cut repeated text from the body | structure | about −1,200 | pressure test | held (Q6) | none |

How to read the columns:

- **Body change** counts characters in the `SKILL.md` body only. The body has 947 characters of free
  room (see Constraints). Items 1, 2, 9, 12, 13 and 14 add about +500 together, so they fit without
  item 16.
- **Test** names the evidence that each change needs before it ships:
  - *Waiver* means the edit changes no instruction. Plan 92's D4 (the owner's waiver of the micro-test
    for factual corrections) is the precedent. Each waiver is still the owner's call.
  - *RED first* means new guidance. It needs a no-guidance control that shows the failure, as
    `SKILL.md:331` requires.
  - *Guard run* means the old and new text must give the same behavior on the cases the edit can reach.
    Plan 72's `t3` arms are the precedent.
  - *Pressure test* means a discipline change, tested with pressure scenarios on Opus and Sonnet.
- **NOTICE.** writing-skills is adapted from superpowers, so every row needs a line in the writing-skills
  part of `NOTICE`'s superpowers change list. The table leaves this column out for that reason.

## 1. Describe the micro-test method in full

**Evidence.**

- Step 1 (`SKILL.md:330`) asks for "one fresh-context sample per call". It does not say how to get a
  fresh context, and that gap has weakened earlier test runs here. Section
  `72-writing-skills-split` of `specs/deferred_items.md` records one example: reps run with
  `--tools ""` still got the user's output style, hooks and global `CLAUDE.md`. The fix there turned off
  the user setting source and auto-memory, and gave each rep its own directory.
- `specs/baseline/red-baseline-description-openings-2026-10-19.md` opens with a quarantine banner.
  The record names the scenario and the pass rule, so a later rep that reads it is void. The skill
  sends records to `specs/baseline/` (`SKILL.md:385`) but never says to keep them out of a rep's reach.
- 25 of the 29 records in `specs/baseline/` register their pass rule before any reply is read, by a
  text search for "pre-regist" or "registered before". The skill's five steps never ask for it.
- `specs/baseline/red-baseline-cc-guide-verifier-recall.md:94` found that its gate A sheets showed the
  arm, so the ratings were not blind. The skill does not ask for blind scoring.
- The skill names no models to test on. Anthropic's page says to test with every model that will run
  the skill. Recent records here test on Opus and Sonnet, plan 92's among them.

**Change.** Add `references/micro-tests.md` with the method in portable words:

1. Isolate each rep. Run it from a new directory outside every repository, with no tools unless the test
   needs them, and with user-level settings and memory turned off. This is not full isolation: a rep
   can still know the user's name. The open watch item "Account identity reaches the isolated
   micro-test runs" (section `deferred-2026-11-17-parallel`) tracks it.
2. Run an isolation probe as a pilot before the first arm. The probe asks the rep what context it can
   see, the user's name and other sessions included.
   `specs/baseline/red-baseline-mutant-screen-runs/kit/isolation_probe.txt` is a model. Plan 92's and
   plan 72's probes have no identity line.
3. Quarantine every file that names the scenario or the pass rule.
4. Register the PASS, FAIL and VOID rules before you read any reply. If you add a reading later, report
   the counts under both readings.
5. Score blind. No sheet or printed line may show the arm, even by a count.
6. Run each arm on each model that will run the guidance.
7. Set a spend cap and a stop rule before the first rep.

The exact Claude Code flags stay in the repository's kits, not in the skill. The guide has no section
on them, and plan 92 made a Claude Code fact with no guide section behind it an anti-goal. In
agent-skills, the reference points to the newest committed kit under `specs/baseline/*/kit/`. In the
body, step 1 gains a pointer to the new file. The net change is about +100 characters.

**Test.** RED first. Give an agent the current skill and ask it to design a micro-test for a wording
change. Score whether its design isolates the reps, registers the rule before reading replies, and
names the models. Five reps each on Opus and Sonnet. At plan 92's rates, a five-rep arm cost $0.18 on
Sonnet and $0.21 to $0.38 on Opus (`specs/baseline/red-baseline-writing-skills-guide.md:522-531`).

## 2. Add a trigger test

**Evidence.** The description promises help with "fixing a skill that fails to trigger or
over-triggers" and "tightening a description". No file in the skill gives a procedure to check
triggering. `claude-code.md` names only `/skill-doctor`'s use counts. Every test section checks what an
agent does with the skill's text or without it. None checks whether the skill loads. Anthropic's page says to
build evaluations before you write the documentation. The repository guide's `skills.iterating`
section says that a skill that triggers has shown only that Claude found it. It tells you to run
realistic prompts in a fresh session with the skill on and again with it off.

**Change.**

- Add a short "Test triggering" step to `references/discovery.md`. Write three or more prompts that
  should load the skill, phrased as users phrase them. Write three or more near-miss prompts that belong
  to a neighboring skill. Run each in a fresh session with the skill on and with it off, and count the
  loads. A description change reports both counts.
- Put the Claude Code mechanics in `references/claude-code.md`: a `skillOverrides` entry of `off` for a
  personal or project skill, `claude plugin eval` for a plugin skill, and `/skill-doctor` for use counts.
  The `SKILL.md` citation gains `skills.iterating`.
- Add a one-line pointer in the body's Skill Discovery Optimization section, about +120 characters.

This is the small, per-skill step. The open backlog item "Trigger-eval suites" (section
`53-agent-skills-portability`) stays open. It asks for about 20 labeled queries per skill, near-miss
negatives and a train and validation split.

**Test.** RED first. Ask an agent to fix a skill that "never loads". Score whether it tests triggering
before and after its edit. The fixture must not match the new text.

## 3. Refresh the Codex cut, and front-load the skill's own description

**Evidence.** `references/discovery.md:123-127` says that Codex 0.163 cut long descriptions to 316–320
characters with 105 skills listed (2026-10-19). On 2026-11-22, Codex 0.167.2 listed 95 skills from a
directory outside every repository (`codex debug prompt-input`). No entry passed 160 characters.
writing-skills' entry stops after about 150 characters, at "writing SKILL.md frontmatter (n". So in
Codex the entry loses every testing trigger: fails to trigger or over-triggers, tightening a
description, pressure-testing and micro-testing.

**Change.**

- (a) Update the measurement in `discovery.md`. The cut has moved both ways between releases, so the
  sentence says to measure it and gives the latest reading.
- (b) Reorder writing-skills' own description so that its testing triggers fall in the first 150
  characters.

No new advice for authors is needed. The 2026-10-19 description-openings record found that agents
already put the main trigger first, in 5 of 5 reps.

**Test.** (a) is a waiver: it is a measurement. (b) changes routing, so it waits for item 2's trigger
test. Its near-miss prompts should include plugin skills that also claim skill creation.

## 4. Fix `render-graphs.js`

**Evidence.** The script reads only `SKILL.md` (`render-graphs.js:102`). A run on a scratch copy of
writing-skills on 2026-11-22 showed these faults:

- It took the bad-example fragment at `SKILL.md:355-358` (`step1 [label="import fs"]`) as a diagram,
  and `dot` failed with a syntax error.
- The script still exited 0, read directly from its own exit status.
- It never read `references/flowcharts.md`, which holds writing-skills' one real chart. Plan 72 moved
  that chart there. The same miss applies to `skills/subagent-driven-development/references/advantages.md`
  and to two `systematic-debugging` files.
- It writes a `diagrams/` folder into the skill folder (`render-graphs.js:130`). The checklist says that
  everything in that folder ships with the skill (`SKILL.md:385`).

**Change.** Read every Markdown file under the skill folder. Skip a block with no `digraph` or `graph`
header. Exit non-zero when a block fails. Write to an output folder outside the skill, given as an
argument. Update the two usage lines in `references/flowcharts.md`.

**Test.** A test runs the script on a fixture skill when `node` and `dot` are installed and skips
otherwise. It is registered in `build/suites.toml`, because `build/run_suites.py --check` fails on an
unregistered test folder. Q1 asks whether to port the script to Python instead. Upstream's main branch
has the same `SKILL.md`-only read, so the fix could also go upstream.

## 5. Fix the worked example

**Evidence.** `testing-skills-with-subagents.md:15` calls `examples/CLAUDE_MD_TESTING.md` "a full test
campaign". The file is a design that never ran:

- Its "Expected Results" are predictions (`:170-180`).
- Its "Next Steps" starts with "Create subagent test harness" (`:182-189`).
- Its agent browses `~/.claude/skills/<category>/` (`:16`, `:34`, `:60`). That contradicts the flat
  namespace in `SKILL.md:94` and the skill listing that runtimes load today.
- It names `skills/using-skills` (`:97`, `:132`), which this repository does not have.

Upstream's main branch keeps the file, under `references/`.

**Change.** Three options (Q3):

- (a) Delete the file and its pointer (recommended). In agent-skills, the pointer becomes one line that
  names `specs/baseline/` for real records.
- (b) Keep the file and relabel the pointer as a design that never ran.
- (c) Replace it with a short worked example in this repository's words. No example may match a
  micro-test fixture, as plan 92's spec requires.

**Test.** Waiver for (a) and (b): neither changes an instruction.

## 6. Scope the persuasion evidence

**Evidence.**

- `persuasion-principles.md:7` and `:173-177` present Meincke et al. (2025) as the research foundation,
  and say that it "validates" a parahuman model of LLM behavior.
- In that study, user messages tried to persuade one model, GPT-4o mini, to fulfil two objectionable
  requests. It ran
  28,000 conversations, and compliance rose from 33.3% to 72.0%. It did not measure how a model follows
  a system prompt or a skill.
- `references/bulletproofing.md:8` limits its toolkit to discipline failures. `persuasion-principles.md`
  has no such limit, and its table (`:128-133`) puts authority language in every discipline skill.
- `SKILL.md:289` reports that prohibitions made shaping failures worse in head-to-head tests.

**Change.**

- Describe the study as it ran, and change "validates" to "suggests".
- Note that a 2026 follow-up from the same lab (Wharton Generative AI Labs) tested newer reasoning
  models. Read it before you cite its figures.
- Add bulletproofing's scope line: persuasion fits a discipline failure. A shaping failure goes to
  Match the Form to the Failure.

**Test.** Waiver for the description of the study. The scope line changes advice to authors, so the
owner decides whether it needs a micro-test.

## 7. Settle which reference-skill tests apply

**Evidence.**

- `SKILL.md:252-261` tests reference skills with retrieval and application scenarios.
- `SKILL.md:268` answers "It's just a reference" with "Test retrieval."
- `testing-skills-with-subagents.md:25-26` says "Don't test: Pure reference skills".
- The checklist (`SKILL.md:397`) marks only the wording micro-test as not applicable to reference skills.
- `CLAUDE.md` exempts pure reference skills from pressure tests and micro-tests only.

So the second file means "do not pressure-test". It does not mean "do not test".

**Change.** Change `:25` to "Don't pressure-test:". Add one line that sends reference skills to the
retrieval and application tests in `SKILL.md`. Upstream has the same text, so the fix could go upstream.

**Test.** Waiver: the edit states what the body already says.

## 8. Bring support files one level from SKILL.md

**Evidence.**

- Anthropic's page says to keep references one level deep from `SKILL.md`. Its reason: Claude may only
  partly read a file that another reference names, for example with `head -100`.
- Two Markdown files are two links away:
  - `persuasion-principles.md` is reached only through `references/bulletproofing.md:10`. It is also
    named in plain text at `testing-skills-with-subagents.md:142`.
  - `examples/CLAUDE_MD_TESTING.md` is reached only through a plain-text mention at
    `testing-skills-with-subagents.md:15`, which `build/check_links.py` does not check.
- The style file `graphviz-conventions.dot`, which an agent reads, is also two links away, through
  `references/flowcharts.md:29`.
- The skill also breaks its own layout. `SKILL.md:86-92` puts depth in `references/` and tools in
  `scripts/`. But writing-skills keeps four support files at its root, and an `examples/` folder that
  the layout leaves out.
- `NOTICE` records that plan 72 chose to leave the files beside `SKILL.md`. Upstream v7.0.1 moved them
  into `references/`, and it keeps `render-graphs.js` at its root.
- No repository test shows that depth matters. The open `t3` backlog item (section
  `72-writing-skills-split`) records that read-then-use is untested.

**Change.** Two options (Q2):

- (a) Link each two-hop file from `SKILL.md` at the step that uses it. This adds about +150 characters.
- (b) Move the Markdown files into `references/` and `render-graphs.js` into `scripts/`, and link them
  from `SKILL.md`. The body change is near 0. This matches the skill's own layout and upstream's map.

The costs of (b):

- Every moved link changes, and `check_links.py` must pass.
- The `NOTICE` sentence on plan 72's divergence needs new words.
- The files that the `SKILL.md` citation covers move. So plan 102 Part B (files packets copy the files a
  citation covers) holds the skill until a fresh `/cc-guide files` verify.

**Test.** A guard run on plan 72's `t3` cases, old layout against new.

## 9. Name a test for edits that keep behavior

**Evidence.**

- The cycle in `SKILL.md:303-336` covers new guidance only.
- Plans 72 and 92 changed text that was meant to keep behavior the same. They tested it with guard arms
  (`specs/baseline/red-baseline-writing-skills-split.md` and
  `specs/baseline/red-baseline-writing-skills-guide.md`).
- Register entry `writing-skills-tdd-for-docs` says that the owner waives the micro-test case by case.
- Step 2 (`SKILL.md:331`) stops the test when the control shows no failure. That fits new guidance. It
  says nothing about an edit made for another reason, such as a move or a correction.
- Plan 92's D2 (the owner's decision to keep the Iron Law) stands. Plan 92 also rejected an exemption,
  because exemption clauses do not scope.

**Change.** Add no exemption, and leave the Iron Law's text as it is. Name the guard run as the test for
an edit meant to keep behavior. The guard run re-runs the cases that the edit can reach, on the old text
and on the new, and requires no drop. This adds a test and deletes none, so it does not reopen D2. It still changes a
discipline skill. About +200 characters.

**Test.** A pressure test on Opus and Sonnet. If the owner adopts it, the `reason` line of
`writing-skills-tdd-for-docs` in `build/cc_guide/conformance.toml` changes too (Q4).

## 10. Add a rename procedure

**Evidence.** The description names renaming a skill. The body has no rename step. The naming parts of
`references/discovery.md` (`:107-111`, `:182-190`) cover only how to choose a name.

**Change.** Add a short list to `discovery.md`:

1. Rename the folder and the `name` field together.
2. Find every bare-name reference to the old name in skills and instruction files, and update it.
3. Check the new name against the skill listing for a near collision.
4. In agent-skills, run the commit lints. The dependency-drift test, `check_provenance.py` and
   `check_conformance.py` find the rest.

**Test.** An application test: an agent renames a fixture skill. Score whether it updates every
reference. RED first, because the list is new guidance.

## 11. Add tables of contents

**Evidence.** Anthropic's page asks for a table of contents at the top of a reference file over 100
lines. Then a partial read still shows the whole scope. Four files pass 100 lines with none:

- `testing-skills-with-subagents.md`, 384 lines
- `references/discovery.md`, 202 lines
- `examples/CLAUDE_MD_TESTING.md`, 189 lines, unless item 5 deletes it
- `persuasion-principles.md`, 187 lines

**Change.** Add a short contents list at the top of each.

**Test.** Waiver: the edit adds navigation and no instruction.

## 12. Use one list of skill types

**Evidence.** `SKILL.md:72-81` lists three types: technique, pattern and reference. The tests in
`SKILL.md:214-261` use four, because they add discipline. `persuasion-principles.md:128-133` uses four
other names: discipline-enforcing, guidance/technique, collaborative and reference.

**Change.** List the four tested types in Skill Types, about +80 characters. Use the same names in the
persuasion table.

**Test.** Waiver.

## 13. Name the `agy` skills folder

**Evidence.** `SKILL.md:23` says that Gemini CLI also reads `~/.agents/skills/`. The `gemini` install
runtime now targets Antigravity CLI (`agy`). `agy` reads `~/.gemini/config/skills/` and not that folder.
An open backlog item records this, in the section on the Step 4b review of branch
`claude/code-customization-guide-currency-657677`.

**Change.** Fix the line inside that item's plan, which covers five other places. Check the Copilot CLI
claim against its docs at the same time. No repository record covers it. About +40 characters.

**Test.** Waiver: a factual correction.

## 14. Match the example language to the stack

**Evidence.** `SKILL.md:147-150` maps testing techniques to TypeScript or JavaScript. That is
upstream's stack. `CLAUDE.md` sets Python for this repository (Polars, NumPyro and JAX).

**Change.** Say "Use the language of the skill's target stack". About −40 characters.

**Test.** The owner decides. The edit changes an instruction, but only to fit the stack.

## 15. Delete the dated session report

**Evidence.**

- `testing-skills-with-subagents.md:377-384` is a dated report: "From applying TDD to TDD skill itself
  (2025-10-03)", with "100% compliance".
- The anti-pattern at `SKILL.md:346-348` bans this kind of text.
- `NOTICE` records that upstream's test transcripts were dropped at vendoring, so nothing here can check
  the claim.
- Upstream's main branch still has the block. So plan 77's precedent, which let upstream's removal stand
  in for a micro-test, does not apply.
- The template in `discovery.md:50` allows an optional "Real-World Impact" section with concrete
  results. So the heading is not the problem. The unverifiable session story is.

**Change.** Delete the block.

**Test.** Waiver: the block holds no instruction.

## 16. Cut repeated text from the body

**Evidence.**

- The cycle is stated seven times: `SKILL.md:21`, `:25`, `:29`, the table at `:41-56`, `:303-324`, the
  checklist at `:378-418`, and `:433-441`.
- Two sections show the same layout: `:83-103` and `:166-191`.
- Discovery Workflow (`:420-431`) restates Skill Discovery Optimization, but it also carries the
  listing caveat.

A cut of about 1,200 characters looks possible.

**Change.** Merge the two layout sections. Drop the second statement of the cycle at `:29` and The Bottom
Line. Keep the listing caveat.

**Test.** Repetition in a discipline skill may be on purpose: the commitment principle in
`persuasion-principles.md` relies on it. So a cut needs a guard run with pressure scenarios. Do this
item only if items 1, 2 and 9 together need more than the 947 characters of free room (Q6).

## Considered and not proposed

**From plugin-dev's skill-development skill.** Each rule below conflicts with a house rule, and the
house rule governs.

- **"This skill should be used when…"** The house form is "Use when…", under register deviations
  `description-when-only` and `descriptions-trigger-list-style`. Anthropic's page asks for the third
  person, which here means no "I" or "you". Its own examples end in "Use when …" sentences.
- **No second person in the body.** No house rule asks for it. A `SKILL.md` body is agent-facing text,
  which the repository's plain-English rule leaves out. The change would touch every line of a discipline skill for no
  measured gain.
- **A `version` key.** `build/check_frontmatter.py` rejects unknown keys. Provenance goes in `metadata`.
- **An `examples/` folder.** Item 8 covers it.
- **A body of 1,500 to 2,000 words.** The body has 2,731 words. `discovery.md` treats a body past about
  2,000 words as a prompt to look, not a fault. The binding limit is the compaction window (item 16).

**Owner rulings and earlier tests.**

- **Narrowing the Iron Law.** D2 kept it, and plan 92 rejected the exemption option. Item 9 adds a test
  and keeps the Law.
- **Critical rules first.** Plan 92's RED run (the run without the change) was null: 0 of 5 failed on
  both models.
- **Naming examples of skills that are not here.** The owner dropped this on 2026-10-31. The examples
  show a pattern and do not claim that the skills exist.
- **A non-fork agent type in micro-test step 1.** It is held until a session or rep picks a fork. Both
  arms of its test were 0 of 5.

**Weak or missing evidence.**

- **Softer emphasis ("CRITICAL", "YOU MUST").** Anthropic's prompting page says that Opus 4.5 and 4.6
  are more responsive to the system prompt. It tells you to soften aggressive language that was written
  to stop tools or skills from under-triggering
  (<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices>).
  The advice covers over-triggering only, and the page's own samples keep emphasis. With no RED evidence,
  this is a hypothesis for a later micro-test.
- **Agent definitions and subagent prompts in the description.** This repository routes those edits
  through writing-skills' micro-test, but the description names only skills. Adding them would collide
  with plugin skills for agent development. Wait for item 2's trigger test.
- **A commit-lint line in the checklist.** `CLAUDE.md` lists the lints, and the commit hook runs them.
- **Provenance steps in the skill.** `CLAUDE.md`'s "Provenance is load-bearing" covers them in this
  repository.

## Constraints

- **The body window is a hard lint.** The `compaction-window` check allows 19,700 characters (5,000
  tokens × 4 characters − 300 reserved). The body has 18,753, so 947 are free. The `STOP:` heading starts
  at character 15,146. A body past 19,700 fails `check_conformance.py`. Each addition names its cost.
- **NOTICE.** Each change adds a line to the writing-skills part of `NOTICE`'s superpowers change list.
- **Bare names.** Cross-references to skills use bare names, never a plugin namespace.
- **No example may match a micro-test fixture**, as plan 92's spec requires.
- **Claude Code facts** go in `references/claude-code.md` and rest on a guide section, which the
  `SKILL.md` citation names.
- **Covered files.** When the files that the citation covers move, `/cc-guide` holds the skill until a
  fresh files verify (plan 102 Part B).
- **Public record.** This repository is public. Records cite committed files only.
- **Lints.** `check_frontmatter.py`, `check_provenance.py`, `check_links.py`, snippet Tier 1, the
  dependency-drift test and `check_conformance.py` must pass.

## Anti-goals

These count as failure even if the rest works:

- a body past the compaction window
- an instruction changed with no test and no owner waiver
- a Claude Code fact with no guide section behind it
- private detail in a committed record
- an example that matches a fixture

## Owner decisions

The owner ruled on all six questions and on the two owner calls in items 6 and 14 on 2026-11-22.

1. **Q1, `render-graphs.js`.** Fix it in JavaScript, with a test that skips when `node` is absent? Or
   port it to Python with a PEP 723 header, like this repository's other scripts?
   Ruling: port it to Python. The port runs with `uv run`, still needs the `dot` binary, and leaves
   upstream's copy for good. With Q2, it lands as `scripts/render_graphs.py`, and `render-graphs.js`
   goes. Its test skips when `dot` is absent. `NOTICE` records the port as a new work based on
   upstream's script.
2. **Q2, layout.** Link the two-hop files from `SKILL.md` (item 8a), or move every support file into
   `references/` and `scripts/` (item 8b)?
   Ruling: move and link (item 8b). `testing-skills-with-subagents.md`, `persuasion-principles.md`
   and `graphviz-conventions.dot` move into `references/`, and `SKILL.md` links each one directly.
3. **Q3, worked example.** Delete it (recommended), relabel it, or replace it?
   Ruling: delete it. The `examples/` folder goes with it, so item 11 covers three files.
4. **Q4, edits that keep behavior.** Add the guard run as the named test (item 9), or keep today's
   case-by-case waiver?
   Ruling: add the guard run. It needs a pressure test on Opus and Sonnet, and the `reason` line of
   `writing-skills-tdd-for-docs` changes with it.
5. **Q5, waivers.** D4 let plan 92's factual corrections ship with no micro-test. May items 3a, 5,
   6 (the study part), 7, 11, 12, 13 and 15 do the same?
   Ruling: waive all eight. Each still ships with the lints and a `NOTICE` line.
6. **Q6, repetition.** Cut it (item 16), or keep it as deliberate reinforcement?
   Ruling: keep it for now. Revisit item 16 when the free room runs out.
7. **Item 6, the scope line.** Add bulletproofing's scope line to `persuasion-principles.md`?
   Ruling: add it, with no micro-test. It repeats a scope that the skill already states.
8. **Item 14, the example language.** Change it to "Use the language of the skill's target stack"?
   Ruling: change it, with no micro-test.

## Proposed sequence

1. **Quick fixes**, one commit each: items 3a, 5, 6, 7, 11, 12, 14 and 15. The Q5 waiver and the
   rulings on items 6 and 14 cover them. Item 13 goes with its own backlog plan.
2. **One plan for the layout:** items 8 and 4 together, because the Python port lands in the new
   `scripts/` folder. It needs a guard run on plan 72's `t3` cases, then a fresh `/cc-guide files` verify.
3. **One plan, RED first:** items 1, 2 and 10, then 3b once item 2's trigger test exists.
4. **One plan, pressure-tested:** item 9, with the register change.
5. **Held:** item 16, under the Q6 ruling.
