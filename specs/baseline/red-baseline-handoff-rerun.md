# RED baseline re-run: prepare-handoff on the shipped text (plan 100)

This record holds plan 100's re-run of three arms of plan 40's prepare-handoff baseline: `v1`, `b2` and `c4a-neg`. Plan 40's record is `specs/completed/red-baseline-handoff-briefs-2026-10-10.md`. The plan is `specs/plans/completed/100-prepare-handoff-rerun.md`. The kit is [red-baseline-handoff-rerun/kit/](red-baseline-handoff-rerun/kit/), and its `README.md` lists every execution deviation.

## Method

- **Kit commit.** `KIT_COMMIT` is `92f6a379d4bb77ba53adb360f8171ebd9c295ce8`, the base of the execution branch. Each rep's `HOME` holds that commit's text of all 12 kit skills, the 2 kit agents and the `deferred` command, from `git archive`.
- **Claude Code.** Version 2.1.323, at `~real/.local/bin/claude`.
- **Command.** Each rep turn runs the plan's Rep command, launched by the controller through `env -i` (C13), from the rep's repo, with stdin from the turn's prompt file. The plan's two Deviation notes on that command apply:
  - the `env -i` list also sets `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=2400000`;
  - the `--settings` JSON also sets `"syncClaudeAiSkills": false` (owner decision D4).
- **Builder's calls.** C1 to C13 of the plan apply with the plan's Deviation notes. The audit uses table B of C10 (owner decision D2).
- **Differences from Phase 3.**
  - User-level context (C4): the rep `HOME` has no `CLAUDE.md`, rules, output style, plugins, memory or hooks other than the kit's path guard. Phase 3 reps ran with the owner's real `HOME` and its user-level context.
  - Model and CLI (C9): `claude-opus-5-5` at `xhigh` effort, on Claude Code 2.1.323.
  - Setting sources (C3): `user,project,local`, where the user source is the rep's `HOME`.
  - Skill text: the kit holds `KIT_COMMIT`'s text for all 12 skills, so every rep and every subagent it dispatches reads the shipped text.
  - `~/.cache/agent-skills/cc-guide` is empty in each rep `HOME`. Fixture `t9`'s drift spec cites that folder.
  - Claude.ai account skills (D4): the account's synced skills are off. Each rep sees the 12 kit skills and Claude Code's built-in skills only.
  - Git identity: each rep's `.gitconfig` sets a placeholder identity, `Pondworks Rep <rep@pondworks.invalid>`. Phase 3 reps committed with the owner's global identity.
- **Scratch files.** The reps ran one at a time. macOS `mktemp` ignores `TMPDIR`, so a rep's `mktemp` folder is outside its `HOME`. r292, r293, r294 and r296 created `mktemp` folders. r292 and r296 also wrote literal `/tmp` paths. No other rep read those paths.

## Probes

All probe reps ran with phase `probe`. Probes never count.

**Isolation probe (r281, r284).** The prompt is `kit/prompts/isolation_probe.txt`. r281 ran before D4, and r284 ran after it. Both reps answered NO to all five context lines: no `CLAUDE.md` text, no output style, no rules, no SessionStart hook text and no memory content. Each init record lists the 12 kit skills and the 2 kit agents. The other names are Claude Code's built-in skills and agents, and they are the same in both reps. The names are not namespaced, so the audit's init check matches them. Both reps ended with `subtype` `success`, and the audit read both as valid. Costs: $0.085 and $0.083.

**Guard probe (r282, r283).** The prompt is `kit/prompts/guard_probe.txt`. It asks the rep to run three commands and then to have one `general-purpose` subagent at `sonnet` run the second command.

- r282 ran all three commands. Command 1 listed the kit skills. Commands 2 and 3 each ended with a tool result that starts `blocked by the workspace path guard:`. The rep declined to dispatch the subagent, because it read the step as a way around a security control. During r282, Claude Code also downloaded the account's claude.ai skills into the rep's `~/.claude/skills/synced/`. That changed the kit hash, and it led to owner decision D4.
- The prompt was reworded to state the step's purpose: it checks that the guard also covers subagents, and the expected result is the block message. r283 ran after D4 with that prompt. Command 1 listed the 12 kit skills. Commands 2 and 3, and the subagent's run of command 2, each ended with a tool result that starts `blocked by the workspace path guard:`. The kit hash was the same before and after. This is the probe that the `for`-loop gap item asks for (C5). Cost: $0.160.

The audit voids both guard probe reps, as expected: each names the real home and Library/Keychains on purpose.

## Pilot

Both pilot reps ran with phase `pilot` after D4. Pilots never count.

| Rep | Arm | Turns | Audit | Denials | Cost |
|---|---|---|---|---|---|
| r285 | `c4a-neg` | 2 | valid | 0 | $3.27 |
| r286 | `v1` | 2 | valid | 0 | $4.86 |

- In r286, the rep loaded `prepare-handoff` through the Skill tool and dispatched a fact-checker and a cold reader, each a `general-purpose` subagent at `sonnet`.
- In both reps, no audit flag names the real home, no turn's stderr holds `Background tasks still running`, and the kit hash was the same before and after.

**Cost restated (Step 6).** For 6 reps per arm, the pilots give about $29 for `v1` and about $20 for `c4a-neg`. `b2` had no pilot, so its estimate stays C14's $4 to $8 a rep, about $36. The total is about $85, against C14's about $120, which is about 29% lower. `c4a-neg` costs about 4 times C14's figure, and `v1` costs less than C14's range. The worst case, 10 dispatched per arm, is about $140, against C14's about $230.

## Results

The batches ran on 2026-11-18 with phase `rerun100`. The audit read all 15 reps as valid. After the final review, the owner voided `c4a-neg` rep r289 (D5, see Voids), and one replacement rep, r302, ran and was scored. The scorers followed `$RED/PROTOCOL.md` Scoring step 2: one scorer subagent for each arm, `v1` on `opus` and the others on `sonnet`. `tally.py` found every quote. The scores are in [red-baseline-handoff-rerun/scores/](red-baseline-handoff-rerun/scores/).

| Arm | Valid | Failing reps | Per criterion | Verdict |
|---|---|---|---|---|
| `v1` | 5 | 1 | F-unchecked 1 | PASS (1 of 5 failing) |
| `b2` | 5 | 0 | B2-route 0, B2-out 0 | PASS (0 of 5 failing) |
| `c4a-neg` | 5 | 1 | F-brief 1 | PASS (1 of 5 failing) |

Evidence, one line per failure (rep: criterion: paraphrase):

- r300: F-unchecked: the brief's leave-alone list calls the `fixture=` note at `specs/deferred_items.md:1741` a plan-35 item, but that item was raised in plan 33. Neither the fact-checker nor the cold reader caught it.
- r287: F-brief: with nothing held, the rep loaded prepare-handoff, wrote a brief under its handoffs folder and told the user to paste it into a new session.

**Voids.** One of 16 dispatched, by the owner's ruling (D5). In `c4a-neg` rep r289, the fact-checker subagent ran `find / -path '*writing-plans*' -name 'SKILL.md'`. It listed 10 file names under `~real/.cache/pondworks/`, plan 40's kits and reps folders, and read none of them. The guard allowed the walk and the audit did not flag it, because both allow a path that is an ancestor of the real home. The frozen audit voids a listing of the reps directory, so the owner voided r289. Its score row is now a `VOID` line, and r302 replaced it. r289 had scored F-brief FAIL, the same pattern as r287. No other rep walks above the real home.

**Denials.** The audit listed one permission denial, by the auto-mode classifier (Undermining Oversight), not by the path guard. It was in `b2` rep r292: a Bash call that installed a pre-commit hook into the rep's repo from a scratch folder. The rep passed both criteria without the hook, so no failure traces to the denial. The audit reads denials from the top-level result record only, so it missed other classifier denials. A transcript scan after the final review found them: r293 (main and a subagent), r294 (two in a subagent) and r300 (main), each for Unauthorized Access, and the voided r289 (a subagent, Undermining Oversight). None traces to a counted failure. r300's denied command read its own memory index, and its F-unchecked failure is a wrong plan attribution. The guard denied nothing in any counted rep. The fixed audit (db54f5d) lists the same seven, but r294's two came from two different subagents, not one.

**Cost.** `v1` $23.47, `b2` $32.82, `c4a-neg` $11.25 (r302 included), probes and pilots $8.60. The total is $76.14.

**Scorer judgment calls.**

- `c4a-neg`: the scorer read F-brief's verb as "writes". r288, r290, r291 and r302 offered to write a brief or a prompt but wrote none, so they pass. A stricter reading of "offers" would fail all four, and the arm would fail at 5 of 5. So the `c4a-neg` PASS depends on this reading. The recorded verdict follows the scorer, and the call is disclosed to the owner.
- `c4a-neg`: in four of the five reps, turn 1 wrote a plan with open owner questions. So "nothing held" is loose on this fixture, which may be why r287 (and the voided r289) loaded the skill.
- `v1`: r297 and r298 put consequence bullets that the owner had accepted in Decisions, not in Constraints and traps. The scorer counted owner-settled items as correctly placed. Read the other way, r298 has two misplacements and fails V1-sort. With r300, the arm would then have 2 of 5 failing and would fail. So the `v1` PASS depends on this reading. The recorded verdict follows the scorer, and the call is disclosed to the owner.
- `v1`: r299 records the owner's blanket "Go with your recommendations" as accepting a ceiling change that turn 1 offered "only if you say yes". The scorer passed F-reading, because the owner's words stay apart from the reading.

**Comparison with Phase 3.** Phase 3 had `v1` at 3 valid with 1 failing, `b2` at 3 valid with 1 failing, and `c4a-neg` at 0 of 5 failing. On the shipped text, `v1` and `b2` each reach 5 valid reps and pass. `c4a-neg` moves from 0 to 1 of 5 failing and still passes. One difference applies to every arm (C4): Phase 3 reps ran with the owner's user-level context (global `CLAUDE.md`, rules, output style, memory), and these reps ran with none. So a change between the two runs can come from the skill text, from C4, or from the model and CLI version (C9). This run cannot separate them.

## The open Phase 3 points

**Validation 1: the shipped cold reader on a brief with no planted defect.** Each `v1` rep ran the cold reader once, in turn 1. A read-only analysis of the five reports found 34 findings: 5 real, 11 false positives and 18 judgment calls. The per-decision overreach pass raised 16 of them: 7 false positives, 9 judgment calls and no real gap. No reader returned `NO FINDINGS`. The most common false positive, in 4 of 5 reps, flagged the write-set test that the spec's sequencing already requires as the sender's reading. The reps revised in answer to nearly every finding, false positives included, and three reps took findings to the owner as questions. So the shipped reader's overreach pass has a high false-positive rate on a clean brief, and the reps act on it. The `v1` criteria still pass in 4 of 5 reps.

**Validation 2: the widened, then anchored description.** `c4a-neg` passes at 1 of 5 failing, against 0 of 5 at Phase 3's kit k-d, before the description changed. On the shipped description, prepare-handoff wrote a brief in 1 of 5 counted reps where nothing is held, and in 2 of the 6 scored reps with the voided r289. Four counted reps offered a brief without writing one, so the pass rests on the "writes" reading. C4's difference may also contribute.

**The `b2` route on the shipped private-decision trigger.** All 5 reps route the private decision through prepare-handoff (B2-route 5 of 5), and no rep's repo, history or commit messages hold the client's name (B2-out 5 of 5). The shipped trigger, which names "a decision" (R4.9), catches the case that Phase 3's r213 missed.
