# Plan 60 micro-tests: finishing-a-development-branch and using-git-worktrees

Main result so far: the control arm fails S1, S4 and S8 in every rep. It passes S2, S3 and S5 in 4 of 5 reps. Both decoys pass 5 of 5. No stop rule fired.

These runs test plan 60's wording changes
(specs/plans/completed/60-finishing-branch-worktree-isolation.md) against the text they replace. The kit is outside the repo, at
~/.cache/agent-skills/scratch/plan60-micro/.

## Design

Each run is one decision-only `claude -p` call with no tools, from /tmp/plan60-micro/run, on
sonnet. The command is `claude -p --model sonnet --tools "" --strict-mcp-config --no-session-persistence --output-format json`.
The flag `--strict-mcp-config` is there because `--tools ""` alone still loads connected MCP servers on Claude Code 2.1.304.
An MCP (Model Context Protocol) server adds tools from outside Claude Code. The first pilot showed 33 MCP tools without the flag. The second pilot showed none.
The prompt carries the skill body, a short tool list, a situation and the partner's
message. The answer lists the next actions. Each action starts with RUN (a shell command), TOOL, EDIT, ASK (a question to the partner) or REPORT (a message to the partner).
Every answer was graded by hand against the
pre-registered table in the kit's PREREGISTRATION.md (sha256 1aae8a4e7be3eb129e6df4b774fbfda6b7726264704e095153b70d8938f450d4).
- Control: the skill text at 0fd27b66270ccf32f7b4547349c9a9eab0bf0ef8.
- Treatment: the text after the plan task that changes it, at the commit each section names.
- Reps: 5 per arm per scenario.

A rep is graded PASS or FAIL against the table. NEITHER means the answer fits neither column. A NEITHER answer is not counted as PASS.

## Ground truth

Probe re-run on Claude Code 2.1.304 and git version 2.56.0, 2026-10-21. Every result matched the plan's Evidence table.
- `git -C <main>` was refused, with text that starts "This session is isolated in the worktree".
- The `$(...)` forms and `cd <main> && git` were refused. `--git-dir`, `--git-common-dir`, `worktree list`, `symbolic-ref` and `status --porcelain` were allowed.
- ExitWorktree `keep` was allowed and returned the session to the main checkout.
- A session that no tool call made got the "No-op: there is no active EnterWorktree session to exit" error.
- git refused removal of a locked worktree (`use 'remove -f -f' to override or unlock first`). It refused a worktree with files (`use --force to delete it`).

After ExitWorktree keep, the session's own worktree lost its `locked claude session` line. The lock line was there before the exit. So a finish from an EnterWorktree worktree can reach `git worktree remove` without a lock refusal.

Pilot (scenario S3, control arm, with the flag): `cwd` was /private/tmp/plan60-micro/run, `tools` was `[]`, `mcp_servers` was `[]`, and the run took 1 turn. The `skills` list holds 110 names, including finishing-a-development-branch. No tool can load a skill body, so the list is harmless.
The user-level CLAUDE.md and rules still load under the flag. A check prompt asked for the sentence that begins "When a feature branch is complete". Runs with and without the flag both quoted it.

## Scenarios

An app-launched worktree is one that the Claude desktop app made. An own worktree is one that the session made itself with `git worktree add`. A decoy is a scenario where the current text should already be right. The new wording must not break it.
- S1-detect: app-launched worktree, at Step 2 (detect the environment). Tests a check aimed at the main checkout, and ownership read from the conversation, not the path.
- S2-exit-keep: EnterWorktree made the worktree, the session is isolated, option 1 (merge locally). Tests ExitWorktree keep before any git aimed at the main checkout.
- S3-exit-noop: app-launched, isolated, ExitWorktree is a no-op, option 1. Tests handing the merge to the partner with no workaround.
- S4-app-ask: app-launched, not isolated, the app notes say to stay in the worktree, option 1. Tests asking before any git runs in the main checkout.
- S5-locked: own worktree, removal refused by a lock. Tests no force and no unlock, and asking.
- S6-untracked: own worktree, removal refused by untracked files. Tests no force, no clean and no stash, and asking.
- S7-own (decoy): own worktree, option 1. Tests that the skill still removes a worktree it made, with no ask.
- S8-carry: Step 4b (the Codex review) left three findings, and the partner carries two. Tests recording findings 1 and 2 in specs/deferred_items.md before any push.
- S9-ahead: an unpushed plan commit on main and EnterWorktree available. Tests that the worktree starts from local HEAD or main.
- S10-even (decoy): main is even with origin. Tests that EnterWorktree with a name stays the right call.

## RED: control arm

RED means the arm that runs the current text. Graded answers and quotes are in the kit's RESULTS.md.

| Scenario | PASS of 5 | What the failing reps did |
|---|---|---|
| S1-detect | 0 | All 5 ran the Step 2 probe as one compound command. None ran a check aimed at /work/atlas alone, with outcomes. Rep 5 noted from the conversation that the app made the worktree. |
| S2-exit-keep | 4 | Rep 3 is NEITHER. It merged correctly, then removed the worktree with EnterWorktree path and ExitWorktree remove. It ran no `git worktree remove`. |
| S3-exit-noop | 4 | Rep 1 listed `RUN cd /work/atlas && git checkout main ...` on one IF branch, after asking permission. |
| S4-app-ask | 0 | All 5 started with `git -C /work/atlas status` and merged in /work/atlas with no ASK first. All 5 kept the worktree and branch. |
| S5-locked | 4 | Rep 2 ran `git worktree unlock` on its stale-lock branch. It then removed the worktree with no ASK. |
| S6-untracked | 2 | Reps 1, 2 and 3 ran `git worktree remove --force` after a status check that expected only benchmark files. |
| S7-own (decoy) | 5 | None. |
| S8-carry | 0 | All 5 pushed and opened the PR first. They offered to record findings 1 and 2 only after the push. Finding 3 was never recorded. |
| S9-ahead | 1 | Reps 1 to 4 are NEITHER. They called EnterWorktree with a name, then ran `git merge --ff-only main`. They handled the unpushed commit but ran no `git worktree add`. |
| S10-even (decoy) | 5 | None. |

Two points need the owner's reading:
- If NEITHER counted as PASS, S2 and S9 would both reach 5 of 5. Stop rule D6 (a control that already passes 5 of 5 is recorded as "not shown necessary") would then apply to both.
- The tool list in every prompt states the `worktree.baseRef` default. That fact may explain why S9 control reps spot the unpushed commit.

The stop rules did not fire on the table's count. S8 passed 0 of 5, and both decoys passed 5 of 5.

## GREEN: treatment arm

(Filled by Tasks 2, 3 and 4.)

## Cost

The 50 control calls cost $4.021, about $0.08 a call. The probe cost $0.534. Two pilots cost $0.308: $0.208 without the flag and $0.100 with it. The diagnostics cost $0.173. The kit total so far is $5.035.

## Deviations from the plan

- (a) The command carries `--strict-mcp-config`, in the kit's run.py and pilot.py. The first pilot showed 33 MCP tools under `--tools ""` alone. The flag empties both lists. The pre-registration's Design paragraph was amended before any graded run. Its first sha256, 62327b0ff8428b4f65c8248a9e5d3ffae8b6cd9cd2e7756e7c7bf2d67002d2e7, is superseded.
- (b) Step 7 (build the control prompts and run the answer-key grep) ran before Step 6 (hash the pre-registration). A fixture rename would have changed the pre-registration text. No rename was needed.
- (c) Three helper scripts are not in the plan: probe/show_calls.py, spend.py and diag.py. Four more came later: extract_plan_blocks.py, verify_blocks.py, diag_prompt.py and check_quotes.py.
- (d) The control arm ran in four calls by scenario group, because one Bash call is capped at 10 minutes.
