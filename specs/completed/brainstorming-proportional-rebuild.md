# Brainstorming: proportional scope, rebuilt on superpowers v7.0.1

**Status: COMPLETE (2026-10-29)** — implemented by plan 70
(`specs/plans/completed/70-brainstorming-proportional-rebuild.md`) and retired here. Approved by
the owner on 2026-10-28, after a section-by-section design review and a review of the written
text.

**Erratum (2026-10-29), added at retirement.** Three statements in this spec need a correction.
The spec stays as it was approved.

1. The paragraph that begins "These parts did not change from v7.0.0" (section "Upstream since
   the drift spec") is wrong for four parts. The upstream diff from v7.0.0 to v7.0.1 shows this:
   - Sizing changed. v7.0.0's "Size the Work" table has three rows: "A quick, clear task", "A small
     change" and "A project with a written design". v7.0.1's table has two rows: "A small change"
     and "A project". Below the table, v7.0.1 adds an Approaches part to the design doc. The
     spec's own table row "A small change is agreed in chat" says so.
   - Playback changed. v7.0.0 says "Mark anything you're guessing as your guess". v7.0.1 says
     "Anything you filled in goes in as your proposal, with your reason".
   - The first Red Flags row changed in its first cell. v7.0.0 has "I'll offer options to save
     them effort". v7.0.1 has "I'll offer a menu of what they might want". The cell that the
     paragraph quotes, "Options steer. Ask them to describe it first.", did not change.
   - The approval gate changed in two sentences. It is still one gate, but it now names the
     design doc, short or full. After approval, v7.0.0 named the plan as the next step only for a
     project's document. v7.0.1 names it for every approved design doc, a small change's short
     one too.

   The other parts that the paragraph names did not change. `builder-check-prompt.md` and
   `visual-companion.md` have the same blob sha in the two releases.
2. Call C3 says the builder check replaces the inline spec self-review, "as upstream did".
   Upstream's diff shows that change: pull request #2463 removed the inline Spec Self-Review and
   added the builder check. But upstream's v7.0.0 release notes say the builder check replaces
   the spec-document reviewer. They do not mention the self-review. `NOTICE` no longer gives a
   reason for dropping it (decision D19 of plan 70).
3. The table row "There is no measured bar" sets the Gallery figures of #2571 (24 runs over three
   variants) beside "176 blind-graded conversations", as if the 176 produced them. The 176 is the
   total over seven scenarios. Finding 4 of the drift spec gives the two apart. Plan 70's
   decision D10 left the table as history.

Requirements R9.2 and R9.3 were superseded before the plan ran. A v7.0.1 drift review landed
first and reviewed every other v7.0.1 change (decision D11 of plan 70).

This spec closes two items in `specs/deferred_items.md`:

- "Open the brainstorming spec for superpowers drift finding 4" (section `audit-3-10-26 routing`).
  Its Done when is "the spec is approved in `specs/`", so this spec's approval meets it.
- "Make brainstorming's scope proportional (plan 35 audit row S-96)" (section
  `35-claude-code-guide-conformance`). It is done when the plan that follows lands.

## Problem

Two records on `main` (`1cd7417`) disagree about when brainstorming applies.

- `skills/brainstorming/SKILL.md:23-29` sends every project through a design and an approval:
  "A todo list, a single-function utility, a config change — all of them."
- `commands/deferred.md:2` uses brainstorming "only for items that record an open design
  decision". The guide's `lean.ceremony` section
  (`specs/guides/claude-code-customization-guide.md:453-472`) skips the brainstorm when "You can
  already describe the solution".

The conformance register records this gap as exception `brainstorming-every-project`
(`build/cc_guide/conformance.toml:696-704`). Its source is plan 35's audit row S-96.

Superpowers drift finding 4 (`specs/superpowers-drift-spec.md`, "Brainstorming ceremony does not
scale") found that upstream rebuilt the skill in v7.0.0. The S-96 fix rewrites the same lines that
finding 4 redesigns, so one spec carries both. Run alone, the S-96 fix would pre-empt this design.

The description also over-reaches. It triggers on any build request "however simple it looks"
(`SKILL.md:2-8`), so this skill loads more often than any other process skill here.

## Upstream since the drift spec

The drift spec's last pass read upstream at v7.0.0 (`bb92a77`, 2026-10-09). Upstream released
v7.0.1 (`2ce8aa1`, 2026-10-21), which retunes brainstorming. On 2026-10-28 upstream `main` was
still `2ce8aa1`. This spec rebases on v7.0.1. These finding-4 statements are now out of date:

| Finding 4 says (v7.0.0) | v7.0.1 (`2ce8aa1`) |
|---|---|
| Context exploration becomes an offer. | "Look Before You Ask": read the project and what the partner pointed at before the first message (#2560). |
| Ideas are compared privately and shown only when that helps. | "Lay out the approaches": two or three, in a message of their own, with a recommendation. The partner picks (#2571). |
| The first message always offers to skip the questions. | The skip offer is made only when brainstorming started on its own, never when the partner invoked it by name (#2560). |
| A small change is agreed in chat. | Every size above a quick task gets a design doc. A small change gets a short one without the builder check. A project gets the full one (#2571). |
| There is no measured bar. | #2571 reports "skipped a step without consent" falling from 24/24 runs to 3/24, and "design doc approved before building" rising from 1/24 to 23/24. It ran 176 blind-graded conversations on Opus and Sonnet. |

These parts did not change from v7.0.0: sizing, playback, how it gets made (#2482, #2483), spikes,
the one approval gate, and the first Red Flags row, "Options steer. Ask them to describe it
first." `builder-check-prompt.md` and `visual-companion.md` are byte-identical in the two releases.

Upstream's eval scenarios are in `prime-radiant-inc/superpowers-evals` (#75). That repository is
public but has no license. This spec cites its scenario names and numbers only and copies no text.

## Decisions

The owner made these calls in the design session on 2026-10-28. Each line quotes the chosen
option's own words, without the reasons the option gave.

- **D1, a small change.** "A short design (approaches, the pick, the how) is played back and
  approved in chat. Then the work goes on in this session through the normal workflow: TDD,
  verify, and writing-plans only when several files make a plan worth it. No specs/ file, no
  fresh session."
- **D2, the opt-out.** "Offer it only when brainstorming started on its own. Never offer it when
  you invoked it by name, or when a caller routed to it (/deferred Design, /fix-issue's feature
  lane, a derive-roadmap ROUTING: brainstorming), because those count as 'asked for it'. On the
  skip path, how-it-gets-made choices are still stated in one line."
- **D3, spikes.** "As upstream, plus one mechanical rule: spike code lives outside the working
  branch, in a scratch directory or a throwaway branch, and is never committed to the branch being
  designed for." The spike's lessons come back into the conversation.
- **D4, question style.** "Ask open questions about what you want and why (intent, goals, prior
  art, what would make it a failure), and offer a short menu only when you are stuck. Use options
  with a recommendation for a choice among known alternatives: the approach pick, a size
  override, a named decision." This replaces "Multiple choice preferred".
- **D5, the approach.** Approach A below: rebase on v7.0.1's text.

The design marked these calls as the agent's own. The owner approved each with its section.

- **C1.** `/fix-issue`'s feature lane is sized normally, because a feature issue is often small.
- **C2.** The builder check dispatches with `model: opus`. The reader it stands in for is the
  writing-plans session, which runs on Opus. The global `dispatch-model-guard.py` hook denies a
  general-purpose dispatch that names no model.
- **C3.** The inline spec self-review is dropped. The builder check replaces it, as upstream did.
- **C4.** The approaches step keeps upstream's heading, "Lay out the approaches".
  creative-thinking's phrase "brainstorming's propose-approaches step"
  (`skills/creative-thinking/SKILL.md:7-8`, `:119-121`) still points at it, so creative-thinking
  is not edited.
- **C5.** Upstream's examples stay: the cornflower-blue icon, the bakery website and the vote.
  No test scenario may use their domains.

## Approaches

- **A. Rebase on v7.0.1 (chosen).** Upstream's v7.0.1 `SKILL.md` is the base, with a short listed
  set of local changes (R4). Drift reviews compare claim by claim, so the next review reads as
  "upstream's text with these changes". Upstream measured this wording in 176 conversations, and
  the closer the copy, the more of that evidence applies. The cost: the largest change and the
  largest test surface.
- **B. Graft upstream's pieces onto today's skill.** A smaller diff, but it mixes our staged
  approvals with upstream's one gate. Upstream's evidence does not transfer to new wording.
- **C. The scope fix alone.** Close S-96 and record finding 4 as declined. The cheapest option,
  but it leaves the #2258 and #2482 failures and gives D1 to D4 no home.

## Requirements

### R1. Sizing

1. Once intent is clear, the skill names one of three sizes in plain words. The partner can
   override the size. If the work grows mid-task, the skill stops, says so, and steps up a size.
2. **Quick, clear task.** Everything that matters is in the request. The skill does it, says what
   it did, and ends. There is no design step. This is the guide's Micro path.
3. **Small change.** This is D1 and the guide's Standard path. The steps:
   1. The skill lays out the approaches in their own message, and the partner picks one. When
      there is one sensible way, the skill says so and says why the others do not fit.
   2. The skill writes a short design in chat, with an Approaches part.
   3. The partner approves it in chat.
   4. The work is built in the same session.
4. **Project.** This is the guide's Full path. The steps:
   1. The skill lays out the approaches, and the partner picks one.
   2. The skill writes the full design to `specs/<name>.md`, with no date prefix.
   3. The builder check runs (R5), and its answers go into the spec.
   4. The skill commits the spec, and the partner approves the committed file.
   5. The skill recommends `/clear` and writing-plans in a fresh session against the file, then
      stops.
5. When the request is several independent projects, the skill says so, agrees an order, and
   brainstorms them one at a time.

### R2. Callers

1. A command or skill that routes to brainstorming counts as the partner asking for it. The skill
   makes no skip offer.
2. Some callers route here because a design decision is open, and their next step reads a spec
   file. For these, the skill sizes the work as a project. This covers `/deferred`'s Design disposition and a
   derive-roadmap stage with `ROUTING: brainstorming`. The skill states this rule in general
   terms and names no command, so it adds no install dependency.
3. `/fix-issue`'s feature lane is sized normally (C1). In `commands/fix-issue.md:16`, "the spec
   gate stays intact" becomes "the design gate stays intact". The Gemini adapter under
   `runtimes/` is regenerated, and `build/sync_runtime_assets.py --check` passes.

### R3. Description

1. The description keeps the `Use when…` form, the third person, and its trigger phrases.
2. It drops "however simple it looks". The trigger stays broad on purpose, because the body makes
   the guide's skip check: can the solution already be described?
3. `build/check_frontmatter.py` passes on the new description.

### R4. The skill text

1. **Taken from `2ce8aa1`, in upstream's order:**
   - "First: What Do You Actually Know?", with the quick-task exit and the ordered steps before
     implementing.
   - "Look Before You Ask".
   - "Your First Message", with its two forms and how the message ends.
   - "The Conversation": get them describing, how it gets made, ground to cover, make every
     question specific, offer recon, lay out the approaches, show don't tell, and spike to feel
     things out.
   - "Play It Back", "Size the Work", "The Written Design", the builder check, the HARD-GATE,
     Red Flags, and "Visual Companion".
2. **Changed, each for a reason:**
   - D1 to D4 are written in.
   - "Look Before You Ask" includes the check of `specs/deferred_items.md`, if present, for
     deferred work the idea touches.
   - The steps before implementing and the HARD-GATE follow R1. A small change ends in a build in
     this session. A project ends in the fresh-session handoff, and writing-plans is the only
     skill after it.
   - The "Options steer" row gains one line: options are for a choice among known alternatives
     (D4).
   - "The Written Design" carries our software guidance from `SKILL.md:100-111`: design for
     isolation and clarity, and working in existing codebases. YAGNI (`:157`) goes there too.
   - The visual companion offer keeps its token-cost warning (`:167`).
   - Cross-skill references use bare skill names, never `superpowers:`.
3. **Dropped from today's skill:**
   - the nine-step checklist and its "create a task for each"
   - the `dot` process flow
   - the "Too Simple To Need A Design" section
   - the staged approvals
   - the spec self-review (C3)
   - "Multiple choice preferred"
4. **Examples** stay upstream's (C5).

### R5. The builder check

1. It runs for a project only. A small change goes straight to the partner, as upstream says.
2. `builder-check-prompt.md` is copied from `2ce8aa1` unchanged.
3. `SKILL.md` tells the agent to dispatch a fresh general-purpose subagent with `model: opus`
   (C2). Without a subagent tool, the agent reads the spec as that builder itself.
4. The agent sorts the builder's questions into three piles: answered already, minor, and the
   partner's. It settles minor points itself and marks them in the spec as its calls. It brings
   the partner's pile in one message.

### R6. Files

| File | Change |
|---|---|
| `skills/brainstorming/SKILL.md` | Rewritten to R1 to R5. The frontmatter keeps `license` and `metadata`. The `# cc-guide:` line gains `lean.ceremony`. |
| `skills/brainstorming/builder-check-prompt.md` | New, copied unchanged from `2ce8aa1`. |
| `skills/brainstorming/visual-companion.md`, `scripts/` | Unchanged. |
| `commands/fix-issue.md`, `runtimes/` | R2.3. |
| `build/cc_guide/conformance.toml` | R8. |
| `NOTICE` | R7. |
| `specs/superpowers-drift-spec.md` | R9. |

### R7. Provenance

1. `NOTICE` gains one "adopted FROM upstream" entry, modeled on the two existing ones. It says
   that brainstorming was rebased on v7.0.1 (`2ce8aa1`, 2026-10-21). It names #2463, #2482,
   #2483, #2560 and #2571, and the new `builder-check-prompt.md`.
2. The entry lists each deliberate divergence:
   - the `Use when…` description
   - the software guidance
   - the `specs/` lifecycle with its fresh-session handoff
   - a small change designed in chat
   - caller sizing
   - the question split
   - spikes kept off the working branch
   - the token-cost warning
   - the builder check's model pin
   - the dropped self-review
3. The plan checks that `LICENSE-superpowers` is still byte-identical to upstream's `LICENSE` at
   `2ce8aa1`. `build/check_provenance.py` passes.
4. The RED, GREEN and pressure scenarios are newly written. Nothing comes from
   `prime-radiant-inc/superpowers-evals`.

### R8. Conformance

1. Exception `brainstorming-every-project` is removed in the same change as the skill edit.
2. `build/check_conformance.py` exits 0 both with and without that exception (probed
   2026-10-28), so the lint cannot show the fix. The plan adds a grep check. Before the edit,
   `SKILL.md` contains "EVERY project", "all of them" and "Too Simple To Need A Design". After the
   edit, it contains none of them. Cases T1 and T2 (R10) are the check of behavior.
3. After the `# cc-guide:` edit, `build/cc_guide/cli.py baseline cite` restamps the file, and
   `cli.py lint` passes.

### R9. The drift spec

1. Finding 4 is marked adopted, naming the plan, and its text is re-baselined to v7.0.1.
2. The "Next review starts from" row becomes `bb92a77`, with brainstorming at `2ce8aa1`.
3. The other v7.0.1 changes stay unreviewed. These are the SDD and writing-skills `references/`
   moves, the executing-plans trim, and upstream's skill-size test. A later drift pass takes
   them.

### R10. RED baseline

The baseline runs and is committed before any edit under `skills/brainstorming/`.

1. **Cases.** Each case is a frozen conversation that ends at a decision point, in a new domain.
   No case uses a domain from the skill's examples: an app icon, a bakery website or a vote. No
   case uses a domain from upstream's eval scenarios either: a todo list, an OCD app, a habit
   tracker, a book club, a photo gallery, a birthday cake, a farm picture or an offsite talk.

   | Case | Decision point | Expected on today's copy | Role |
   |---|---|---|---|
   | T1 quick task | Everything that matters is in the request. | Stops for a design. | Fix target |
   | T2 small change | Clear goal, a few files, one obvious way. | Writes a spec file. | Fix target |
   | T3 scope approval (#2258) | The partner says the proposed scope looks fine. | Unknown | Fix target or guard |
   | T4 platform (#2482) | A design is about to be written, and no platform was raised. | Unknown | Fix target or guard |
   | T5 skipped doc (#2571) | The partner asked to talk it through, and one round of questions is done. | Unknown | Fix target or guard |
   | T6 caller-routed | A routed item that changes a skill contract. | Reaches a committed spec. | Guard |
   | T7 first question | An under-specified request. | Offers a menu. | Fix target |
   | T8 opt-out | Auto-triggered against invoked by name. | No offer exists. | GREEN only |
   | T9 spike | An accepted spike, then "let's keep it". | Not covered. | GREEN only |

2. A case that fails on today's copy is a fix target. A case that passes is a guard.
3. **Method.** This follows `specs/red-baseline-description-openings-2026-10-19.md`:
   - Each rep is a decision-only run: `claude -p --model claude-opus-5-5 --tools ""
     --no-session-persistence`, from a new subdirectory of `/tmp`.
   - There are three arms: a no-guidance control, today's copy read at a pinned SHA (not through
     the live `~/.claude/skills` symlink), and the new copy. Each arm gets five reps for each case.
   - The pass, fail and void rules are registered before any reply is read. Every flagged reply
     is read by hand. The background files' sha256 hashes are recorded.
4. The results go to `specs/red-baseline-brainstorming-YYYY-MM-DD.md`, dated on the day of the run.
   A folder of the same name beside it holds the prompts and raw replies. Quarantine both files during any later
   micro-test of brainstorming.

### R11. GREEN, pressure test, trigger test

1. **GREEN.** On the new copy, each fix target passes at least 4 of 5 reps. Each guard stays at 4
   of 5 or better. T8 and T9 each pass at least 4 of 5.
2. **Pressure test**, as writing-skills requires for a discipline skill:
   - At least three frozen scenarios, each with two or more pressures. One mixes sunk cost, "sounds
     good" to the scope, and a deadline. One pulls the other way: ceremony on a quick task.
   - Each new rationalization gets a Red Flags row, and then the scenario runs again.
3. **Trigger micro-test.**
   - A `--tools ""` rep cannot call the Skill tool. So each prompt gives a skill listing (the
     name and description of brainstorming and of several neighbouring skills) and a request. The
     rep names the skill it would load first, or none.
   - Today's description and the new one each get five reps against the same request prompts.
   - A project-size request must still choose brainstorming at least 4 of 5 times with the new
     description.
   - Quick-task results are recorded but not graded.
4. **Cost.** The estimate is about 170 runs at $0.05 to $0.30 each.

### R12. Size, dependencies and lints

1. `skills/brainstorming/SKILL.md` stays under 20,000 bytes, measured with `wc -c`. That is
   upstream's skill-size bar and near the guide's 5,000-token re-attach after compaction. It
   keeps the HARD-GATE and Red Flags inside what compaction keeps. The estimate is about 16,000.
2. If the new text names another skill's file or section, or a `/command`, the reference is
   mirrored in `install.py`'s `DEPENDENCIES` or in `build/test_runtime_support.py`'s
   `SOFT_REFERENCES`. The dependency-drift test passes.
3. `build/run_commit_lints.sh` passes.

### R13. Completion

The plan's completion protocol ticks both deferred items. This design session does not edit
`specs/deferred_items.md`, because another session holds that file now.

## Out of scope

- **The planning-surface spec for drift findings 9 and 10** (section `audit-3-10-26 routing`). It
  rewrites writing-plans and the four reviewer prompts. This spec changes only how brainstorming
  hands off ("writing-plans in a fresh session"), so the two can land in either order.
- **Item (11) of the old audit's P2 item**, which asks brainstorming to name creative-thinking in
  its approaches step. C4 keeps creative-thinking's pointer valid, and this spec adds no reverse
  link.
- **The rest of the drift spec's v7.0.1 re-baseline** (R9.3).
- **Trigger-eval suites** for descriptions in general, a portability deferred item.

## Order with other work

- No plan is live on `main` at `1cd7417`. Plan 53 (portability), which the P2 item asked to go
  first, is complete.
- The plan edits `skills/brainstorming/`, which no executing skill loads during the plan, so the
  self-modifying hazard is small. Still, it runs in its own worktree. The `~/.claude/skills`
  symlink points at the main checkout, so the live skill changes only at merge.
