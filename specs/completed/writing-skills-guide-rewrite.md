# writing-skills against the Claude Code guide — Design Spec

**Status: COMPLETE (2026-11-12)** — implemented by plan 92
(`specs/plans/completed/92-writing-skills-guide-rewrite.md`) and retired here. It came from the Design pick
of the 2026-11-12 `/deferred` pass. The owner approved it on 2026-11-12, after brainstorming and a builder
check.

## What this builds

One change to the writing-skills skill closes three backlog items in `specs/deferred_items.md`
(line numbers as of main `7977696`):

| Item | Section | What it asks |
|---|---|---|
| L4182, "Split and rewrite writing-skills against the guide" | `53-agent-skills-portability — 2026-10-20` | Close register gap `writing-skills-guide-gaps`, settle deviation `writing-skills-tdd-for-docs`, verify or drop the `@`-link claim, fix the directory examples, cite `subagents.models` for the `haiku` sentence, and check the fork advice |
| L1681, "Review the 41 files the drift sweep stamped stale" | `43-claude-code-drift-automation — 2026-10-12` | Review and restamp the last STALE file, `skills/writing-skills/SKILL.md`, so that `cli.py lint` prints no `STALE` line |
| L1158, "A distilled `references/` file for writing-skills" | `35-claude-code-guide-conformance — 2026-10-04` | Write the distilled reference file of Claude Code text that Decision 10 of `specs/completed/claude-code-guide-conformance.md` put off until the split |

The change has four parts:

1. A new file, `skills/writing-skills/references/claude-code.md`, holds every Claude Code fact that a
   skill author needs. It uses the repo's own words and rests on guide sections.
2. `references/discovery.md` and `SKILL.md` keep only advice that is true on every runtime. They point
   to the new file where a Claude Code fact matters.
3. Six claims are corrected, re-reasoned or cited (see Claims).
4. The conformance register, the drift baseline, `NOTICE` and the backlog are updated to match.

## Why

- **The drift backlog has one file left.** `cli.py lint` prints one line:
  `STALE skills/writing-skills/SKILL.md skills.locations skills.frontmatter skills.listing-budget skills.progressive-disclosure subagents.isolation`.
  The register gaps that L4182 covers hold it. L1681 enters the aged tail on 2026-11-27. After that
  date it blocks merges and PRs. A live `→ planned` note stops the ageing.
- **writing-skills is the meta-skill.** `CLAUDE.md` tells every runtime to follow it when editing a
  skill. When it states a wrong Claude Code fact, every skill that an agent writes can repeat the error.
- **The split made the distilled file possible.** Decision 10 kept the Claude Code text inside
  writing-skills, because the skill ships to three runtimes and the guide ships nowhere. It rejected a
  separate reference file "now" and said to look at it again at the split. Plan 72 did the split on
  2026-10-29 (body 716 to 434 lines). It moved most of the Claude Code text into
  `references/discovery.md`, mixed with lint rules and advice that holds on every runtime.

## Decisions taken in brainstorming

- **D1 — Distill (owner, 2026-11-12).** The Claude Code facts go into one new reference file. L1158
  closes by this work, not as dropped.
- **D2 — Keep and refresh `writing-skills-tdd-for-docs` (owner, 2026-11-12).** The Iron Law ("no skill
  without a failing test first") does not change. The register entry gets a narrower reason, new
  evidence and a new revisit trigger.
- **D3 — Scope is the items' "Done when" lines (my call).** This is not a rewrite of the whole skill.
  The TDD mapping, the testing sections, the rationalization tables, `persuasion-principles.md` and
  `testing-skills-with-subagents.md` stay as they are.
- **D4 — Test waiver for factual corrections (owner, by approving this spec on 2026-11-12).** The
  micro-test is waived for the edits that Testing classes as factual corrections. The plan tells task reviewers so, because they use main's copy of the Iron Law, which
  names no exception for "documentation updates".
- **D5 — Review against the guide as it is on main (owner, 2026-11-12).** The plan does not run
  `/cc-guide` and does not edit the guide. It reviews writing-skills against the guide committed on
  main when its worktree is cut. The guide's catch-up from 2.1.307 onward stays normal `/cc-guide`
  upkeep. When that upkeep changes a section that writing-skills cites, writing-skills goes STALE
  again. That is how the drift system is meant to work: files track the guide, and the guide tracks
  the docs.

## Approaches considered

**For L1158 (where the Claude Code text lives):**

1. **Distill into `references/claude-code.md` (picked).** One file holds the Claude Code facts. The
   other files keep portable advice and point to it.
   - Gains: Codex and Gemini sessions do not load Claude Code detail unless they follow the pointer. A
     drift review checks one small file. Each fact has one home.
   - Costs: one more file to load. The split inside `discovery.md` needs care, because its frontmatter
     bullet mixes lint rules with Claude Code facts.
   - Limit: the SKILL.md body itself holds little Claude Code text (lines 23 and 419). So the body
     gains little room. The main relief is in `discovery.md`.
2. **Fix in place.** Correct each claim where it is now and close L1158 as dropped.
   - Gains: a smaller diff and no new file.
   - Costs: the Claude Code facts stay in two files, mixed with portable advice. The next drift review
     has to search both.

**For `writing-skills-tdd-for-docs`:**

1. **Keep and refresh (picked).** No skill text changes and no reps are needed. The entry states the
   real, narrow difference.
2. **Narrow the Iron Law with an exemption for edits that change no instruction.** Rejected. It is a
   discipline change to the meta-skill, so it needs pressure scenarios on two models. writing-skills'
   own wording tests also found that exemption clauses do not scope.
3. **Remove the entry as a misreading.** Rejected. It hides the typo case, where the two rules really
   differ.

**For the guide's drift since 2.1.306:**

The drift report of 2026-11-12 (head 2.1.322) shows 806 changed doc blocks and 38 untriaged
releases. Every section that writing-skills cites is due.

1. **Review against the guide as it is on main (picked).** The plan stays off the guide, and L1681
   closes when writing-skills is restamped. The `@` claim loses its unsupported reason (see The `@`
   claim).
2. **Catch the guide up first.** A `/cc-guide` pass on the skills and subagents groups would run as
   its own branch before the plan. Rejected: it is a large pass, and its guide corrections would make
   about 30 other citing files STALE. It is upkeep in its own right, and L1681 does not need it.

## Goals, non-goals and anti-goals

**Goals**
- Every Claude Code fact in writing-skills matches a guide section, and the SKILL.md citation names
  that section.
- `writing-skills-guide-gaps` leaves the register. `writing-skills-tdd-for-docs` stays, refreshed.
- `cli.py lint` prints no `STALE` line, and `build/check_conformance.py` passes.

**Non-goals**
- No change to the Iron Law or to any other discipline rule.
- No change to the description rule (Skill Discovery Optimization, "Use when…" and trigger-only).
- No `listing-aggregate` check, and no answer to guide note S-109 (the open question about the unit of
  the listing budget).
- No new lint.

**Anti-goals** (failure even if the rest works)
- A SKILL.md body past the compaction window.
- Docs text committed anywhere: in the skill, the guide, the register or a test record.
- A Claude Code fact in the new file with no guide section behind it.
- An instruction changed with no test and no owner waiver.
- A broken anchor for the register entries that cite writing-skills (see Constraints).

## Current state (main `7977696`)

- `SKILL.md`: 435 lines. Its body is 18,285 characters, as `build/check_conformance.py` counts it.
  The `compaction-window` check allows 19,700 (5,000 tokens × 4 characters − 300 reserved), so 1,415
  characters are free.
- `SKILL.md:14` holds the citation:
  `# cc-guide: skills.locations skills.frontmatter skills.description skills.listing-budget skills.progressive-disclosure subagents.isolation @2.1.219`.
  By drift rule R4.1 (where citation comments go), a SKILL.md citation also covers the Markdown files
  the skill loads on demand. So `references/` files carry no citation of their own.
- `references/discovery.md`: 202 lines. It holds the frontmatter rules, the body template, and Skill
  Discovery Optimization.
- Register (`build/cc_guide/conformance.toml`):
  - Gap `writing-skills-guide-gaps` (about line 677) covers three parts: the listing budget (audit
    row S-58), critical rules first (S-67) and `@` loading (S-107). Its `tracked_in` names L4182.
  - Deviation `writing-skills-tdd-for-docs` (about line 687), section `lean.ceremony`, audit row S-97.
    Its revisit trigger is this rewrite.
  - Three other entries cite writing-skills as evidence and stay: `description-when-only`,
    `descriptions-trigger-list-style` and `side-effecting-skills-body-gated`.
- The guide is stamped at Claude Code 2.1.306. The docs cache was fetched on 2026-11-12 at 2.1.322.

## Claims

Each row is a Claude Code statement in writing-skills today, with what happens to it.

| # | Claim and place | Guide section | Disposition |
|---|---|---|---|
| C1 | The description is "resident in EVERY conversation" (`discovery.md:116-121`). The listing is "always-loaded" names and descriptions (`SKILL.md:419`) | `skills.listing-budget` | Correct it. Portable text: the description is the only text that loads before a skill triggers, and a runtime may drop or shorten it when its listing overflows. Claude Code mechanics go in the new file (see Listing budget) |
| C2 | No advice to put critical rules near the top (audit S-67) | `skills.progressive-disclosure` | The compaction mechanism goes in the new file as a fact. A new instruction depends on a RED run (see Testing) |
| C3 | "`@` syntax force-loads files immediately, consuming 200k+ context" (`discovery.md:200-202`) | none | The reason sentence goes. The bare-name rule stays, with a portability reason (see The `@` claim) |
| C4 | Do not fork a skill "that dispatches subagents itself" (`discovery.md:12`) | `subagents.frontmatter`, `subagents.isolation` | Keep the advice with a new reason (see Fork advice) |
| C5 | The `haiku` alias means Haiku 5.5 on the Anthropic API and 4.5 on other providers, and auto mode drops Haiku 4.5 (`discovery.md:11`) | `subagents.models`, `skills.frontmatter` | The Claude Code half moves to the new file. `discovery.md` keeps the lint rule. Add `subagents.models` to the citation |
| C6 | Personal skills live in `~/.claude/skills/` and other runtimes' directories (`SKILL.md:23`) | `skills.locations` | Correct as written. It stays in the body unless the body needs room (builder's call) |

Two more edits are not Claude Code claims, but L4182 asks for them:

- **C7 — Frontmatter key meanings** (`discovery.md:11`). The meaning of each Claude Code extension key
  (`context`, `agent`, `model`, `effort`, `disable-model-invocation`, `when_to_use`) moves to the new
  file. `discovery.md` keeps the list of keys that `build/check_frontmatter.py` accepts, and the split
  between the Agent Skills spec's keys and the Claude Code extensions. These are repo facts.
- **C8 — Directory examples** (`SKILL.md` "Directory Structure", lines 83-102, and "File
  Organization", lines 160-185). Both show the shipped layout: `SKILL.md`, `references/` for depth and
  `scripts/` for tools. The "heavy reference" example puts its large `.md` files under `references/`.

## Design

### The new file: `references/claude-code.md`

- **Content rule.** A sentence goes in this file when its truth depends on Claude Code and can change
  between versions. A sentence that holds on every runtime, or that states a repo lint rule, stays where
  it is.
- **Sources.** Each statement rests on a guide section, in the repo's own words. The file carries no
  citation comment (R4.1). The SKILL.md citation names every section the file relies on.
- **Contents.** C1's mechanics, C2's mechanism, C4's reason, C5's model facts and C7's key meanings.
  Order them by the author's task: frontmatter keys, then the listing, then the body after compaction.
- **Pointers.** `SKILL.md` gains one line in "SKILL.md Structure", beside the existing pointer to
  `discovery.md`. It sends the reader to `claude-code.md` before setting a Claude Code-only key, or
  when the skill will run in Claude Code. `discovery.md` points to it at the frontmatter bullet and in
  Token Efficiency.
- **Examples.** No example in the file may match a micro-test fixture (see Testing).

### Listing budget and guide note S-109

The C1 fix needs no unit and no number for the budget. The portable text states the mechanism. The new
file states what `skills.listing-budget` says:

- the names always stay listed;
- when the descriptions overflow the budget, Claude Code drops whole descriptions, least-invoked
  skills first, and a skill without its description rarely triggers on its own;
- `/doctor`, `/skill-doctor` and `/context` show the cost, and `disable-model-invocation`,
  `skillOverrides` and the budget settings change it.

The file states no budget figure. So S-109 stays open, and the `listing-aggregate` item stays held
under its own entry. The Codex shortening note stays in `discovery.md`, because it is a Codex fact.

### The `@` claim (C3)

Today's cached docs (2.1.322) imply that Claude Code attaches the files that `@` paths name in a local
skill's body. The skills page says that skills synced from claude.ai, unlike local skills, do not
attach those files. A changelog entry on synced skills says the same. The guide does not state this
fact. The docs do not support "200k+" or "immediately".

Under D5 the plan does not edit the guide. So:

- Drop the reason sentence ("Why no @ links").
- `discovery.md` §5 keeps the bare-name rule and the ❌ `@` example. Their reason is portability: a
  bare skill name lets each runtime load the skill through its own skill mechanism. The text makes no
  claim about what other runtimes do with an `@` path, because no source covers that.
- `claude-code.md` says nothing about `@` paths.

S-107's part of the gap closes, because no unsupported claim is left. The docs fact is a guide
omission. The plan logs it to the backlog at completion, so that `/cc-guide` upkeep can add it to
`skills.progressive-disclosure`. After that, writing-skills could state the Claude Code reason again.

### Fork advice (C4)

The advice not to `context: fork` a skill that dispatches subagents rested on a premise that is gone:
subagents can now spawn their own subagents. The guide's `subagents.frontmatter` `background` row
still gives a real hazard. In `claude -p` and the Agent SDK with fork mode off, nested subagents start
in the background. So a forked skill can return its result before its own subagents report.

- **Default (my call):** keep the clause, and restate its reason from that row. Cite
  `subagents.frontmatter`. The guide does not state the nesting depth limit, so the file does not
  state it either.
- If the guide no longer supports a hazard at execution time, dropping the clause is a change of
  instruction. The owner rules on it first.

### Critical rules first (C2)

The new file states the mechanism from `skills.progressive-disclosure`. After compaction, Claude Code
re-attaches the most recent invocation of each skill, keeps only its first 5,000 tokens, and fills a
shared 25,000-token budget newest first.

Whether writing-skills also gains an instruction (a slot in the body template, per "Match the Form to
the Failure") depends on the RED run in Testing:

- **RED shows the failure:** add the instruction to the template in `discovery.md`, and run GREEN.
- **RED shows no failure** (registered now, before any rep): add no instruction. The new file states
  the mechanism only. S-67's part of the gap closes on the owner's ruling, with the RED record as
  evidence. In this repo, the `compaction-window` check already enforces the rule mechanically.

### Register changes

- **`writing-skills-guide-gaps`:** remove it in the commit that closes its last part. If a part cannot
  close (for example, GREEN fails after a RED failure), narrow the entry to that part and point
  `tracked_in` at a new backlog item. A part never stays open silently.
- **`writing-skills-tdd-for-docs`:** keep it (D2). Rewrite it in the repo's words:
  - `reason`: the guide keeps TDD for behaviour changes, and skill wording changes agent behaviour. The
    departure is narrow. The Iron Law also covers edits that change no instruction (a typo, a link, a
    verbatim move), which the guide's table would let skip the test. In practice the owner waives the
    micro-test case by case (commit 7bb8810).
  - `evidence`: audit row S-97, this spec, and the owner's decision of 2026-11-12.
  - `revisit`: if the guide's TDD row names agent-facing text such as skills or prompts, or if
    writing-skills' Iron Law changes.
- **Other entries:** `description-when-only`, `descriptions-trigger-list-style` and
  `side-effecting-skills-body-gated` stay valid. They need SKILL.md to keep the Skill Discovery
  Optimization heading and rule, and the deployment step's partner gate.

### Citation and restamp (L1681)

- Set the SKILL.md citation to the sections that the rewritten text relies on, in `SKILL.md` and in
  the files it loads on demand. Expected: `skills.locations`, `skills.frontmatter`,
  `skills.description`, `skills.listing-budget`, `skills.progressive-disclosure`,
  `subagents.frontmatter`, `subagents.models` and `subagents.isolation`. Drop any section that no
  sentence relies on.
- **Review method (my call).** `build/cc_guide/packets.py` `files()` copies only the citing file into
  a `/cc-guide files` packet. So that path would never see `claude-code.md` or `discovery.md`, where
  the Claude Code facts will live. Instead, a plan task reviews `SKILL.md` and every file it loads on
  demand against each cited section. It records one row per Claude Code statement: covered,
  contradicted, or not covered. A contradicted row is fixed before the restamp. The owner rules on
  every not-covered row at the plan's completion gate, as `settle` would require.
- Then run `cli.py baseline cite skills/writing-skills/SKILL.md`.
- The plan edits no guide text (D5), so no other citing file goes STALE through this change.

### Provenance

writing-skills is adapted from superpowers (MIT, © 2025 Jesse Vincent).

- `claude-code.md` is original repo text under the repo's MIT `LICENSE`. It paraphrases the repo's own
  guide. It holds no docs text and no upstream text.
- `NOTICE`'s superpowers changes list gains one entry. The entry names the new file and the corrected
  claims. It also says that the file departs from upstream v7.0.1's `references/` map, which plan 72
  followed.
- The skill keeps its `LICENSE` and `LICENSE-superpowers` copies and its `metadata` author fields.
  `build/check_provenance.py` needs no change.

## Testing

### Which edits need reps

An edit is **behaviour-shaping** when it adds, removes or changes an instruction that an agent acts on:
a do or don't, a template slot, or a pointer. An edit is a **factual correction** when it changes only
a stated fact or reason, and every instruction stays as it was. Factual corrections get no reps. Lints,
the register, the drift review and the code review check them.

| Edit | Class | Check |
|---|---|---|
| C1 listing wording | Factual | Review against `skills.listing-budget` |
| C2 mechanism in the new file | Factual | Review against `skills.progressive-disclosure` |
| C2 template instruction | Behaviour-shaping | RED, then GREEN only if RED fails |
| C3 reason sentence dropped, rule kept | Factual | Review |
| C4 new reason, same rule | Factual | Review against `subagents.frontmatter` |
| C4 rule dropped (only if the guide no longer supports it) | Behaviour-shaping | Owner ruling first |
| C5, C6, C7 | Factual | Review, and `build/check_frontmatter.py` for C7's repo facts |
| C8 directory examples | Factual (my call): they now match `discovery.md`'s existing advice to put depth in `references/` | Review |
| Pointers to `claude-code.md` | Behaviour-shaping | Pointer test |

### Micro-test rules

These follow writing-skills' "Micro-Test Wording Before Full Scenarios", as shipped on main when
execution starts. The main checkout's copy governs, not the worktree's edited copy.

- **Arms and reps.** 5 reps per arm, in fresh contexts. GREEN and pointer arms run on both
  `claude-opus-5-5` and `claude-sonnet-5-5`, because skill authoring runs on Opus and plan execution on
  Sonnet. The RED control also runs on both models.
- **Pre-registration.** Pass rules, bars and literal readings are written and committed before any rep
  runs. This includes the RED null outcome above. Never add a reading after seeing reps (plan 71 and
  plan 72 lessons). If a rep cannot be scored under the rule, report it with its quoted lines.
- **Reading.** Read every verdict by hand from the full reply. Scripts are reading aids, not verdicts.
- **RED for C2.** The control is the current shipped text. The task asks for a long skill with one
  hard rule. The predicate is the place of the hard rule's first statement in the body. The builder
  writes the predicate as a literal, observable test before any rep.
- **Pointer test.** Plan 72's design D9 applies: a "reads the reference" bar has no real no-guidance
  control, because the old layout has no new file to read. So:
  - The new layout runs on both models, with a bar on reading `claude-code.md` at the right step and
    on applying the fact correctly.
  - The current layout runs as a descriptive arm on Opus only, scored on applying the fact, with no bar.
  - At least three cases: a Claude Code-only frontmatter key, a description or listing question, and
    the fork decision.
- **Isolation** (the repo's known contamination channels):
  - Run reps from a new empty directory under `/tmp`, outside every repository, so that no repo
    `CLAUDE.md` or git status reaches them.
  - Pass `--setting-sources ""` and set `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`.
  - Inline the worktree's copy of the skill text in the prompt. Never rely on the installed skill.
  - Grep a pilot rep's transcript for the skill name and the expected answer before the real reps.
  - Grep every fixture and the text under test for the answer before any arm runs. No worked example
    may equal a fixture.
- **Kit and record.** Reuse plan 72's kit in `specs/baseline/red-baseline-writing-skills-split/kit/`
  where it fits. Write the record to `specs/baseline/red-baseline-writing-skills-guide.md`, with its
  kit and reps in `specs/baseline/red-baseline-writing-skills-guide/`.
- **Spend cap (my call): $30** for the whole plan, summed from each rep's `total_cost_usd`. Plan 72 spent
  $3.39 on 45 reps. Stop and ask the owner before a batch would cross the cap.
- **No pressure scenarios.** D2 leaves every discipline rule unchanged. If an edit turns out to touch
  one, stop and ask the owner.

## Constraints

- **Self-modifying plan.** The plan edits the skill that sets its own testing rules, and the
  installed skills are symlinks into the main checkout. So:
  - Execute in a worktree.
  - Run the controller tooling (the subagent-driven-development scripts) by absolute path from the
    main checkout, with the worktree as the working directory.
  - Leave the main checkout unchanged for the whole run.
  - Implementers and reviewers use the installed writing-skills, which is main's copy.
- **Body budget.** The SKILL.md body must stay within the `compaction-window` check's 19,700
  characters. My target is 18,800 or fewer, which leaves room for later fixes.
- **No docs text** in any committed file. Quotes stay in the `/cc-guide` packets under the cache.
- **No guide work (D5).** The plan runs no `/cc-guide` pass, and it edits neither the guide nor
  `baseline.json` beyond the `baseline cite` restamp. The guide text it reviews against is main's at
  the time its worktree is cut. If a guide change lands on main before the merge, re-review the
  sections it touched before the restamp.
- **Order.**
  1. Run the RED control for C2 and the descriptive arm of the pointer test, both on the current text.
  2. Write `claude-code.md`. Edit `discovery.md` and `SKILL.md`. Update the register in the same
     commit as the fix that closes each part. Update `NOTICE`.
  3. Run GREEN (if RED failed) and the new-layout arms of the pointer test.
  4. Review the files against the cited sections (see Citation and restamp). Restamp with
     `baseline cite`. Run `cli.py lint`, `build/check_conformance.py` and
     `build/run_commit_lints.sh`.
- **Lints that this change can trip:** `check_links.py` (new relative links),
  `check_frontmatter.py`, `check_provenance.py`, `check_conformance.py`, `cli.py lint`, Tier 1 of the
  snippet gate (code fences in the new file), and `test_runtime_support.py -k declared_dependencies`
  (if the new file names another skill's path or a `/command`).
- **Backlog notes.** When this spec is committed, each of the three items gets
  `→ planned 2026-11-12: specs/writing-skills-guide-rewrite.md`. writing-plans later changes the path to
  the plan.

## Done when

- **L4182:**
  - `writing-skills-guide-gaps` is gone from the register, or narrowed to a part that has a new
    backlog item.
  - `writing-skills-tdd-for-docs` carries the refreshed reason, evidence and revisit trigger.
  - `build/check_conformance.py` passes.
  - The `@` reason sentence is gone, and the bare-name rule stays with its portability reason.
  - The directory examples show `references/` and `scripts/`.
  - The `haiku` sentence's section is cited.
  - The fork advice has a guide-backed reason, or the owner ruled to drop it.
- **L1681:** `skills/writing-skills/SKILL.md` is reviewed with its on-demand files and restamped with
  `baseline cite`, and `cli.py lint` prints no `STALE` line on the plan's branch at the merge.
- **L1158:** `references/claude-code.md` exists and holds the Claude Code facts, and `SKILL.md` and
  `discovery.md` point to it.
- The micro-test record is committed, with every arm's verdicts.
- `NOTICE` records the change.

## Left to the builder

- The exact wording of every edit, within the content rule and the dispositions above.
- Whether C6 (line 23) moves to the new file, if the body needs room.
- The RED fixture and its literal predicate, and the pointer-test cases beyond the three named.
- How much of plan 72's kit to reuse.
- How to split the work into tasks and commits, within the order above.

## Not in this spec

- Guide note S-109 and the `listing-aggregate` check stay held under their own item.
- The guide's catch-up from 2.1.307 onward, for every section, is normal `/cc-guide` upkeep (D5).
- The `@` docs fact as a guide addition. The plan logs it to the backlog at completion.
- The Iron Law and the other discipline rules (D2).
- The packet gap above: `packets.py` `files()` leaves out the on-demand files that R4.1 says a
  SKILL.md citation covers. The plan logs it to the backlog at completion, and changes no tooling.
