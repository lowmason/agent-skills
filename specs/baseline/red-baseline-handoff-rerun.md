# RED baseline re-run: prepare-handoff on the shipped text (plan 100)

This record holds plan 100's re-run of three arms of plan 40's prepare-handoff baseline: `v1`, `b2` and `c4a-neg`. Plan 40's record is `specs/completed/red-baseline-handoff-briefs-2026-10-10.md`. The plan is `specs/plans/100-prepare-handoff-rerun.md`. The kit is [red-baseline-handoff-rerun/kit/](red-baseline-handoff-rerun/kit/), and its `README.md` lists every execution deviation.

## Method

- **Kit commit.** `KIT_COMMIT` is `92f6a379d4bb77ba53adb360f8171ebd9c295ce8`, the base of the execution branch. Each rep's `HOME` holds that commit's text of all 12 kit skills, the 2 kit agents and the `deferred` command, from `git archive`.
- **Claude Code.** Version 2.1.323, at `~real/.local/bin/claude`.
- **Command.** Each rep turn runs the plan's Rep command, launched by the controller through `env -i` (C13), from the rep's repo, with stdin from the turn's prompt file. The plan's two Deviation notes on that command apply:
  - the `env -i` list also sets `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=2400000`;
  - the `--settings` JSON also sets `"syncClaudeAiSkills": false` (owner decision D4).
- **Builder's calls.** C1 to C13 of the plan apply as written. The audit uses table B of C10 (owner decision D2).
- **Differences from Phase 3.**
  - User-level context (C4): the rep `HOME` has no `CLAUDE.md`, rules, output style, plugins, memory or hooks other than the kit's path guard. Phase 3 reps ran with the owner's real `HOME` and its user-level context.
  - Model and CLI (C9): `claude-opus-5-5` at `xhigh` effort, on Claude Code 2.1.323.
  - Setting sources (C3): `user,project,local`, where the user source is the rep's `HOME`.
  - Skill text: the kit holds `KIT_COMMIT`'s text for all 12 skills, so every rep and every subagent it dispatches reads the shipped text.
  - `~/.cache/agent-skills/cc-guide` is empty in each rep `HOME`. Fixture `t9`'s drift spec cites that folder.
  - Claude.ai account skills (D4): the account's synced skills are off. Each rep sees the 12 kit skills and Claude Code's built-in skills only.

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
