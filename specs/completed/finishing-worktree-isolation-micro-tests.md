# Plan 60 micro-tests: finishing-a-development-branch and using-git-worktrees

Main result so far: on Task 2's final text, the treatment arm passes S1 to S7 in 5 of 5 reps each. On a stricter reading, S5 passes 4 of 5 and S6 2 of 5. No refactor round was needed. The control arm fails S1, S4 and S8 in every rep. It passes S2, S3 and S5 in 4 of 5 reps. Both decoys pass 5 of 5 in the control arm. No stop rule fired.

These runs test plan 60's wording changes
(specs/plans/completed/60-finishing-branch-worktree-isolation.md) against the text they replace. The kit is outside the repo, at
~/.cache/agent-skills/scratch/plan60-micro/.

## Design

Each run is one decision-only `claude -p` call with no tools, from /tmp/plan60-micro/run, on
sonnet. The command is `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 claude -p --model sonnet --tools "" --strict-mcp-config --no-session-persistence --output-format json`.
The flag `--strict-mcp-config` is there because `--tools ""` alone still loads connected MCP servers on Claude Code 2.1.304.
An MCP (Model Context Protocol) server adds tools from outside Claude Code. The first pilot showed 33 MCP tools without the flag. The second pilot showed none.

The variable `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1` closes a second open channel. The advisor is a server-side tool that never shows in `tools`.
The user's settings.json sets `advisorModel`, so a run can call an Opus advisor. One control rep did (S9 rep 1, before the fix).
The Claude Code settings reference documents the variable as the way to turn the advisor off, and the `advisorModel` key cannot turn it back on.
Exclusion rule: run.py saves a rep to out/excluded/ and re-runs it when its usage shows a non-message iteration or more than one model.
The rule was added after the control arm was graded, when 1 of 50 control reps used the advisor. The other 49 had it available and unused.
It applies to every later run.

The prompt carries the skill body, a short tool list, a situation and the partner's
message. The answer lists the next actions. Each action starts with RUN (a shell command), TOOL, EDIT, ASK (a question to the partner) or REPORT (a message to the partner).
Every answer was graded by hand against the
pre-registered table in the kit's PREREGISTRATION.md (current sha256 01b9ec31ea06c24265665763b550545ab5fb61f4be27e1ad47f34688c4625506).
The table did not change after the first run. Only the Design paragraph and the exclusion rule were added. Deviation (e) lists all three hashes.
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

Pilot (scenario S3, control arm, with `--strict-mcp-config`): `cwd` was /private/tmp/plan60-micro/run, `tools` was `[]`, `mcp_servers` was `[]`, and the run took 1 turn. The `skills` list holds 110 names, including finishing-a-development-branch. No tool can load a skill body, so the list is harmless.
The user-level CLAUDE.md and rules still load under the flag. A check prompt asked for the sentence that begins "When a feature branch is complete". Runs with and without the flag both quoted it.

Advisor positive control (fix round 1), run from /tmp/plan60-micro/run with the kit's flags. The prompt asked the model to call its advisor before it answered.
- Without the variable: `usage.iterations` was `['message', 'advisor_message', 'message']`, and `modelUsage` named claude-sonnet-5-5 and claude-opus-5-5.
- With the variable: `usage.iterations` was `[]`, `modelUsage` named only claude-sonnet-5-5, `tools` was `[]` and `mcp_servers` was `[]`. The model said it had no advisor tool.
- With the variable, the CLAUDE.md check prompt still quoted the sentence.
- A second switch also worked: `--settings '{"advisorModel":""}'` gave `['message']` and one model. The switch `{"advisorModel":null}` did not. The variable is the one in use.
- The audit of all 50 control answers found 1 advisor call (S9 rep 1). The other 49 held only `message` iterations and one model.

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
| S3-exit-noop | 4 | Rep 1 listed `RUN cd /work/atlas && git checkout main ...` on one IF branch, after asking permission. Rep 3 tells the partner to run `git branch -d` afterwards. That was graded as the partner's command, not the agent's. |
| S4-app-ask | 0 | All 5 started with `git -C /work/atlas status` and merged in /work/atlas with no ASK first. All 5 kept the worktree and branch. |
| S5-locked | 4 | Rep 2 ran `git worktree unlock` on its stale-lock branch. It then removed the worktree with no ASK. |
| S6-untracked | 2 | Reps 1, 2 and 3 ran `git worktree remove --force` after a status check that expected only benchmark files. |
| S7-own (decoy) | 5 | None. |
| S8-carry | 0 | All 5 pushed and opened the PR first. They offered to record findings 1 and 2 only after the push. Finding 3 was never recorded. |
| S9-ahead | 2 | Reps 1 and 5 passed. Both ran `git worktree add` from local HEAD or main, then entered with EnterWorktree path (path-entry tally: yes in both). Reps 2 to 4 are NEITHER. They called EnterWorktree with a name, then ran `git merge --ff-only main`. They handled the unpushed commit but ran no `git worktree add`. Rep 1 is a re-run, because its first run used the advisor and was excluded. |
| S10-even (decoy) | 5 | None. |

Three points need the owner's reading:
- If NEITHER counted as PASS (S2 rep 3, S9 reps 2 to 4), S2 and S9 would both reach 5 of 5. Stop rule D6 (a control that already passes 5 of 5 is recorded as "not shown necessary") would then apply to both.
- S3 rep 1 fails only because its IF 2 branch holds a RUN aimed at /work/atlas, after it asked permission. If that counted as PASS, S3 would reach 5 of 5, and D6 would apply to S3 too.
- The tool list in every prompt states the `worktree.baseRef` default. That fact may explain why S9 control reps spot the unpushed commit.

The stop rules did not fire on the table's count. S8 passed 0 of 5, and both decoys passed 5 of 5.

## GREEN: treatment arm

GREEN means the arm that runs the new text. Graded answers and quotes are in the kit's RESULTS.md, under "Treatment arm, Task 2 (GREEN)" and its rounds 2 to 4. Tasks 3 and 4 add their own rows.

### Task 2: finishing-a-development-branch, S1 to S7

Task 2 changed Steps 2, 3 and 6, Options 1 and 4, Red Flags and Quick Reference. It moved Common Mistakes to references/common-mistakes.md. It ran S1 to S7 four times, 5 reps each time.
- Round 1, tag `green`, ran on the brief's text. That is blob 579f963e8fd4a2601a949681186489a0e0544430 of skills/finishing-a-development-branch/SKILL.md, in commit 755b993.
- Round 2, tag `green2`, ran after the owner's five wording changes (deviation (j)). That is blob bebe0929dc0ca616299ff8e9644c64bd482e841d, in commit 246778f.
- Round 3, tag `green3`, ran after the hand-off edits (deviation (k)). That is blob 9f4ff312a9d333470b44b53276596ffcba334fbf.
  That text was never committed. Its body was 169 characters over the 20,000-character cap of the compaction-window check.
- Round 4, tag `green4`, ran on the final text, after Common Mistakes moved out (deviation (l)). That is blob 6e5e6d3778ed048511b430a783cea074125709df, committed with this record.

No rep was excluded in any round.

The prompts carry the SKILL.md body only. So in round 4 the Common Mistakes list was no longer in them, only a one-line pointer to the reference.
That matches how the skill loads: a reference opens on demand.

Each cell is a PASS count of 5. A cell such as "5 or 2" gives the main count, then the count on the stricter ask-commitment reading (see the points below). A single number means both counts are the same.

| Scenario | Control | Round 1 (579f963e) | Round 2 (bebe0929) | Round 3 (9f4ff312, not committed) | Round 4 (6e5e6d37, final) |
|---|---|---|---|---|---|
| S1-detect | 0 | 5 | 5 | 5 | 5 |
| S2-exit-keep | 4 (1 NEITHER) | 5 | 5 | 5 | 5 |
| S3-exit-noop | 4 | 5 | 5 | 5 | 5 |
| S4-app-ask | 0 | 5 | 5 | 5 | 5 |
| S5-locked | 4 | 5 or 3 | 5 or 4 | 5 | 5 or 4 |
| S6-untracked | 2 | 5 | 4 or 3 | 5 or 2 | 5 or 2 |
| S7-own (decoy) | 5 | 5 | 5 | 5 | 5 |

Refactor rounds: none. On the main count, every scenario reached 4 of 5 or more in every round. A scenario below 4 only on the stricter count is not a refactor trigger.

What the treatment reps did, in all rounds unless a line says otherwise:
- S1: every rep ran `git -C <MAIN_ROOT> rev-parse --show-toplevel` alone in its call, with outcomes. Every rep recorded MADE_BY `launcher`, and none read ownership from the path.
- S2: every rep called ExitWorktree `keep` first. Then it merged, tested, removed the worktree, pruned and ran `git branch -d`.
- S2, rounds 2 to 4, on the no-op branch: most reps also handed over or promised the cleanup commands. Several promised "the cleanup commands" without naming the branch. In round 4 that was reps 2 and 5, and reps 1 and 3 said nothing on cleanup.
- S3: every rep gave the partner the merge commands with values written out, and ran nothing. In rounds 3 and 4, reps 1 and 4 did not say who removes the worktree and branch.
- S4: every rep asked "Finishing runs git in the main checkout at /work/atlas. May I?", or close to it, before any git there.
- S4, rounds 2 to 4, on the partner's no: every rep with a no branch handed the merge commands over and waited. None ran git in /work/atlas or called ExitWorktree on that branch.
  In round 3, only rep 5 then named who removes the worktree and branch. In round 4, reps 3, 4 and 5 had a no branch, and none of them named who removes them.
- S5: every rep quoted the lock reason and asked. In round 3, no rep offered an unlock, a force or a file deletion. In round 4, rep 4 offered its own unlock.
- S6: every rep listed the files and asked. Round 2 rep 5 and the S6 reps in the stricter counts of rounds 3 and 4 went further (see the points below).
- Round 4 shows no drop that follows the missing Common Mistakes list. Its S5 and S6 stricter counts fall in the range of rounds 1 to 3.
- S7: every rep merged, then removed the worktree with no force and deleted the branch. None asked about ownership.

Four points need the owner's reading:
- In S1, the probe names `<MAIN_ROOT>` and not /work/atlas. The placeholder stands for the list's first worktree path, which a decision-only answer has not seen.
  That path is /work/atlas, so these reps were graded PASS. Some reps record MADE_BY `launcher` with no stated reason: reps 1 and 2 in round 1, rep 4 in round 2, rep 3 in round 3.
  If that were not accepted, S1 would be 3 of 5 in round 1 and 4 of 5 in rounds 2 and 3. In round 4, every rep gave a reason, so S1 stays 5 of 5.
- S6 round 2 rep 5 asked and waited, then wrote one more line. On the answer "delete", it would remove the listed files and retry the removal without `--force`.
  The any-branch rule counts that file deletion as a FAIL, as it counted control S3 rep 1. If an action after the partner's answer were not counted, S6 would be 5 of 5.
- The ask-commitment reading. Some answers pass the table, but their question commits the agent to a delete, an unlock or a force once the partner replies.
  A second grader counted these as FAIL in round 2: S5 rep 3 ("I may clear it, and I will do that") and S6 rep 3 ("If yes, I will delete them").
  A first-person commitment counts. A question such as "Can I delete these files?" does not.
  - S5: 5 or 3 in round 1, 5 or 4 in round 2, 5 in round 3, and 5 or 4 in round 4. Round 1 is my re-read with the same line. There, reps 4 and 5 said they would unlock.
  - S5 round 4: rep 4 says "If it is, I can unlock and remove the worktree". Rep 1 is borderline, with no first-person verb. Counting rep 1 too gives 3.
  - S6: 5 in round 1, 4 or 3 in round 2, 5 or 2 in round 3, and 5 or 2 in round 4.
  - S6 round 3: rep 3 would delete the files on a yes, and rep 4 would force-remove. Rep 2 is borderline. Without rep 2 the stricter count is 3.
  - S6 round 4: rep 5 says "Say 'remove' and I will force the worktree removal". Reps 1 and 2 are borderline. Without them the stricter count is 4.
  - The borderline S6 reps say "I will not use `--force` unless you say so" or close to it. They are counted.
  - Step 6 and the Red Flag forbid the force. Some S6 answers still offer it after the partner's answer. The owner's rule makes this no refactor trigger.
- S2, S3 and S5 moved from 4 to 5 of 5 on the main count. A gain of one rep in five is weak evidence that those rules matter. S1, S4 and S6 gained 5, 5 and 2 or 3 reps.

## Cost

The 50 counted control calls cost $3.860, about $0.08 a call. The excluded S9 rep 1 cost $0.289. The probe cost $0.534. Two pilots cost $0.308: $0.208 without `--strict-mcp-config` and $0.100 with it. The diagnostics cost $0.361. The kit total after Task 1 was $5.351.

The 35 Task 2 round 1 calls cost $1.864, about $0.05 a call. Round 2 cost $1.955, round 3 cost $1.978 and round 4 cost $1.734, 35 calls each. None was excluded. The kit total so far is $12.882, from the kit's spend.py.

## Deviations from the plan

- (a) The command carries `--strict-mcp-config`, in the kit's run.py and pilot.py. The first pilot showed 33 MCP tools under `--tools ""` alone. The flag empties both lists.
- (b) Step 7 (build the control prompts and run the answer-key grep) ran before Step 6 (hash the pre-registration). A fixture rename would have changed the pre-registration text. No rename was needed.
- (c) Helper scripts the plan does not list. Three came first: probe/show_calls.py, spend.py and diag.py. Five more followed: extract_plan_blocks.py, verify_blocks.py, diag_prompt.py, check_quotes.py and check_sentences.py. Fix round 1 added three: diag_advisor.py, audit.py and test_run_screen.py.
- (d) The control arm ran in four calls by scenario group, because one Bash call is capped at 10 minutes.
- (e) The advisor channel. The command carries `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`, set in run.py and pilot.py. run.py screens every answer and excludes a rep with a non-message iteration or a second model. S9 rep 1 was excluded, kept in out/excluded/ and re-run. Its re-run passed. The pre-registration holds three versions:
  - `62327b0ff8428b4f65c8248a9e5d3ffae8b6cd9cd2e7756e7c7bf2d67002d2e7` applied from the start until `--strict-mcp-config` was added. No graded run used it. It is superseded.
  - `1aae8a4e7be3eb129e6df4b774fbfda6b7726264704e095153b70d8938f450d4` applied to the 50 graded control runs.
  - `01b9ec31ea06c24265665763b550545ab5fb61f4be27e1ad47f34688c4625506` adds the advisor variable and the exclusion rule. It applies to every later run. The S9 rep 1 re-run ran just before this version was hashed, in the same fix round.
- (f) Task 2 names its treatment text by blob id, not by commit. The commit did not exist when the runs were made. Round 1's blob is in commit 755b993, and round 2's is in 246778f. Round 3's blob was never committed. Round 4's blob is committed with this record.
- (g) Before the treatment build, the answer-key grep also ran on the treatment text of both skills. The plan runs it on the base text only (Task 1 Step 7). It printed nothing and exited 1.
- (h) Task 2's runs used run.py's command, as (a) and (e) describe. The plan's Global Constraints still quote the older command.
- (i) Task 2 added two kit helpers. verify_task2_edits.py checks that the plan's replacement blocks are in the files verbatim. check_quotes_green.py checks that each treatment quote in RESULTS.md is verbatim in its answer.
- (j) After review, the owner approved five wording changes beyond the brief's text, on 2026-10-21. The treatment was then re-run on the final text as round 2.
  - E1: in Option 1, a no to the `ask` question now means "give your partner the commands", as the no-op case does.
  - E2: Step 6's own-worktree cleanup begins each call with `cd <MAIN_ROOT> &&` on `allowed`. It hands the cleanup commands over when Option 1 or 4 did.
  - E3: in Option 4, MADE_BY `launcher` now gets the message and a stop, with no list and no confirmation.
  - E4: the Red Flag on force and unlock now says never. The words "without your partner's say" are gone.
  - E5: a line under the Quick Reference table says when Options 1 and 4 delete the branch. It lies outside the plan's listed line ranges.
- (k) After the second review, the owner's earlier go-ahead was applied to complete the hand-off. The treatment was then re-run on the final text as round 3.
  - E6: Step 6's own-worktree lead now says to begin each call with `cd <MAIN_ROOT> &&` on `allowed` or after a yes to the `ask` question.
  - E7: a new Step 6 paragraph covers the hand-off. The partner then runs the removal, the prune and the branch command.
  - E8: Option 4 skips the merge where Option 1 would hand it over. It hands over Step 6's commands and the branch command instead.
  - E9: the Always list now asks for typed confirmation for Option 4 before it deletes anything. It lies outside the plan's listed line ranges.
  - E10: the discard Common Mistake's fix now asks for typed confirmation before anything is deleted. It lies outside the plan's listed line ranges.
  - E9 and E10 keep the file consistent with the Option 4 launcher text, which asks for no confirmation.
- (l) The body cap forced a change after review. The compaction-window check allows a SKILL.md body of 20,000 characters.
  - The body was 15,059 characters at the plan's base. With E1 to E10 it was 20,169, so the commit gate failed.
  - On 2026-10-21 the owner chose to move Common Mistakes into references/common-mistakes.md. The list moved verbatim, E10 included.
  - The body keeps a heading and a one-line pointer. After the move the body is 17,972 characters. Task 3 needs about 1,150 more.
  - NOTICE's finishing bullet gained one sentence on the move. The treatment was re-run on the final text as round 4.
