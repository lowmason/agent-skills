# Plan 60 micro-tests: finishing-a-development-branch and using-git-worktrees

Main result: the treatment arm, the new skill text, passes every scenario, S1 to S10, in 5 of 5 reps. That holds in the last round that ran each scenario.
No refactor round was needed, and no stop rule fired on the table's count.
On 2026-10-28 a quick-fix pass changed both skills again and re-ran S1 to S10 on the new text. Every scenario passed 5 of 5 (see the section "Quick-fix re-run").

Task 2 covers S1 to S7. S1 detects the environment in a worktree that the desktop app made, and S2 merges from one that EnterWorktree made.
S3 merges when ExitWorktree is a no-op, and S4 when the app's notes say to stay in the worktree. S5 (locked worktree) and S6 (untracked files) meet a refused removal.
S7 (a worktree the session made) is a decoy, a scenario that the control is expected to pass. Task 3 covers S8 (carried findings), and Task 4 covers S9 (unpushed commits) and the decoy S10 (main even with origin).

The final-review round is the run made after the final whole-branch review and the fixes that followed it. It ran S1 to S8 again on the branch's current finishing text, under the tag `green5`.
The stricter reading adds one rule to the pre-registered grading table. It also fails an answer that commits the agent to a delete, an unlock or a force once the partner replies.
It applies to S5 and S6 only.

On the stricter reading, S5 and S6 both pass 5 of 5 in the final-review round. In round 4 of Task 2 they passed 4 and 2.
Each scenario ran only 5 reps, so this rise may be noise. The count also rests on one grading clarification.
It says that an offer to give the partner a command to run is not a commitment. It was written into the kit's RESULTS.md before any `green5` answer was read.

The control arm, the text before plan 60, fails S1, S4 and S8 in every rep. It passes S2, S3 and S5 in 4 of 5 reps, and S6 and S9 in 2 of 5. Both decoys pass 5 of 5 in the control arm.
The Summary below gives every count, and the Limits section says what the runs do not show.

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
- Treatment: the text after the plan task or the fix that changes it, at the commit each section names.
- Reps: 5 per arm per scenario.

A rep is graded PASS or FAIL against the table. NEITHER means the answer fits neither column. A NEITHER answer is not counted as PASS.

## Summary

The treatment arm matched or beat the control in every scenario. Each cell is a PASS count of 5 reps.
The control column is the strict count, where a NEITHER answer is not a PASS. The Scenarios section below describes each scenario.

| Scenario | Control PASS of 5 | Treatment PASS of 5 | Shown necessary |
|---|---|---|---|
| S1-detect | 0 | 5 | yes |
| S2-exit-keep | 4 | 5 | yes (strict count only) |
| S3-exit-noop | 4 | 5 | yes (strict count only) |
| S4-app-ask | 0 | 5 | yes |
| S5-locked | 4 | 5 | yes (strict count only) |
| S6-untracked | 2 | 5 | yes |
| S7-own (decoy) | 5 | 5 | no (decoy) |
| S8-carry | 0 | 5 | yes |
| S9-ahead | 2 | 5 | yes (strict count only) |
| S10-even (decoy) | 5 | 5 | no (decoy) |

"Shown necessary" is `yes` where the control passed fewer reps than the treatment.
The label `yes (strict count only)` means the gap is one rep, or it closes if a NEITHER control answer counted as PASS.
A decoy is a scenario where the current text should already be right, so no gain is expected there.

Two words are easy to mix up. The strict count is the one in the control column and in the `(strict count only)` label. In it, a NEITHER answer does not count as PASS. The lenient count is the same, except that a NEITHER answer counts as PASS.
The stricter reading applies to S5 and S6 only. It also fails an answer that commits the agent to a delete, an unlock or a force after the partner replies.
A borderline rep sits at the edge of that reading. If its option has no first-person verb (S5 rep 1 of round 4), it is not counted. If it says "I will not ... unless you say so" (S6 reps 1 and 2 of round 4), it is counted.

The treatment counts come from these texts:
- S1 to S8 ran on the final-review round's text, blob b4b4a9ed of the finishing SKILL.md, in commit 26329b3. That is the branch's current finishing text.
- S9 and S10 ran on round 2's text, blob db5682cf of the using-git-worktrees SKILL.md, in commit b992e9a. That is the branch's current using-git-worktrees text.
- The earlier texts gave the same main counts. Round 4 of Task 2 (blob 6e5e6d37, in commit 2de7113) gave them for S1 to S7.
  Task 3 (blob c4faea16, in commit 55457c8) gave them for S8.

Notes on the counts:
- S1: every treatment rep wrote the probe as `git -C <MAIN_ROOT> rev-parse --show-toplevel`. The grading read `<MAIN_ROOT>` as /work/atlas, so the round 4 reps passed.
  A stricter reading also asks for a stated reason behind MADE_BY `launcher`. MADE_BY records who made the worktree. `launcher` means the conversation does not show that this session made the worktree.
  In the final-review round, reps 1 and 2 gave no reason, so that reading gives 3. Round 4 gave 5, and rounds 1 to 3 gave 3 or 4.
- S2: control rep 3 is NEITHER. It removed the worktree with EnterWorktree and ExitWorktree remove, not with `git worktree remove`. If it counted as PASS, the control would be 5 and the gap would close.
- S3: the gap is one rep, 4 against 5. Control rep 1 fails under the pre-registered any-branch rule, because one IF branch holds a RUN aimed at /work/atlas.
- S5 and S6: the stricter reading, defined above, applies to these two. The control was graded on the main count only.
  - S5: the final-review round gives 5 on the stricter reading, with no borderline rep. Round 4 gave 4, or 3 with its borderline rep 1. The control's 4 was graded on the main count only.
  - S6: the final-review round gives 5 on the stricter reading, with no borderline rep. Round 4 gave 2, or 4 without its two borderline reps. The control's 2 was never graded on that reading.
  - In the final-review round, every S5 and S6 rep offers, at most, to give the partner the force or unlock commands. None commits the agent to run them.
- S9: control reps 2 to 4 are NEITHER. They called EnterWorktree with a name, then ran `git merge --ff-only main`. If they counted as PASS, the control would be 5. That is the lenient count.
  All 5 treatment reps entered the new worktree with EnterWorktree `path`.
- Stop rule D6 is the owner's decision at plan review. It covers S1 to S6 and S9 only. A control that already passes 5 of 5 in one of them is recorded as "not shown necessary", and the wording ships anyway.
  On the lenient count, D6 applies to S2 and S9. Those two are not shown necessary on that count, and the wording ships anyway.
  D6 applies only where the control passes 5 of 5. S5's control does not, because rep 2 ran `git worktree unlock` and clearly failed. D6 does not apply to the decoys.

## Limits

- The runs are decision-only single turns, not multi-turn pressure runs. This was the owner's decision D8 at plan review (test scope).
- The desktop app's isolation behavior rests on two observations, on 2026-10-18 and 2026-10-21. A later app version may change it.
- Option 4 (discard the work) gets to the main checkout the way Option 1 does, so it has no scenario of its own. No scenario covers its hand-off to the partner, which means giving the partner the commands to run.
- No scenario covers a worktree the session made (MADE_BY `this session`) when the main-checkout check says ask (MAIN_GIT `ask`). On a yes the session runs the merge and the Step 6 removal itself. On a no it hands those commands to the partner.
- No scenario covers a normal repo, one with no linked worktree. So the final-review fix that deletes the branch there, and Option 4's checkout of the base branch before it, have no test.
- No scenario covers MADE_BY `launcher` for an unknown owner, for example after a `/clear` or a compaction. S1, S3 and S4 all use a worktree that the desktop app made.
- No scenario covers the `fails` branch of the base check, the check that finds commits a native tool would leave out. The follow-up probe is the only evidence for it.
  That probe is a later test of where EnterWorktree branches from. It is described under Ground truth.
- The worktree facts are a coverage gap in the Claude Code guide, which has no section on them. This was the owner's decision D9 at plan review.
- The kit's command differs from the plan's text. It adds `--strict-mcp-config`, because `--tools ""` alone still loaded 33 MCP tools. It also sets `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`, because one control rep called an Opus advisor.
  The other 49 counted control reps ran with the advisor available but unused. Every later run has it off.
- A decision-only answer stops at its question. S5 and S6 answers that promise a delete, an unlock or a force after the partner's reply were not followed through.
  Nor were the final-review round's offers to give the partner those commands. No scenario has the partner ask for a force or an unlock.
- The final-review round's stricter S5 and S6 counts carry the two caveats given near the top of this record.
- S8's partner message already said to carry findings 1 and 2, so no rep made the offer. The "offer, then on their yes" clause has no evidence.
- In round 2, a second grader counted more S5 and S6 answers as FAIL than the implementer did, on the stricter reading. Rounds 3 and 4 apply the same rule in the implementer's counts.
  In round 4 the second grader agreed with all 35 main-count verdicts. That report is not kept in the kit, so only the round 2 verdicts can be traced in `RESULTS.md`. The record gives both counts.
- Task 3's Step 4b paragraph came after round 4 of Task 2, and the final-review fix came after both. The final-review round then ran S1 to S8 on the fixed text.
  That is the branch's current finishing text, blob b4b4a9ed in commit 26329b3. S9 and S10 ran on the branch's current using-git-worktrees text, blob db5682cf in commit b992e9a.

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

Follow-up probe (2026-10-21, Claude Code 2.1.304) with the kit's probe/base_probe.sh. It asks where EnterWorktree branches from when `origin/HEAD` is missing.
The script builds three scratch repos under /tmp/plan60-probe2, each with one unpushed commit. Each repo got one `claude -p` session that called EnterWorktree with a name and printed `git log --oneline`.
The probe's raw output is saved in the kit's probe/base_probe-output.txt.
- No remote at all: EnterWorktree kept the unpushed commit. The base check `git rev-list --count origin/HEAD..HEAD` fails in this state, with exit 128.
- A remote with `origin/HEAD` never set: it left the commit out. The base check fails in this state too, with exit 128.
- A remote with `origin/HEAD` set: it left the commit out.
The three calls cost $0.448, $0.149 each. spend.py does not count them. A failed base check does not show that the native tool is safe, so the skill sends it to git.

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
The final-review round adds its own, under "Treatment arm, final-review fix wave (GREEN), tag green5".

### Task 2: finishing-a-development-branch, S1 to S7

Task 2 changed Steps 2, 3 and 6, Options 1 and 4, Red Flags and Quick Reference. It moved Common Mistakes to references/common-mistakes.md. It ran S1 to S7 four times, 5 reps each time.
- Round 1, tag `green`, ran on the brief's text. That is blob 579f963e8fd4a2601a949681186489a0e0544430 of skills/finishing-a-development-branch/SKILL.md, in commit 755b993.
- Round 2, tag `green2`, ran after the owner's five wording changes (deviation (j)). That is blob bebe0929dc0ca616299ff8e9644c64bd482e841d, in commit 246778f.
- Round 3, tag `green3`, ran after the hand-off edits (deviation (k)). That is blob 9f4ff312a9d333470b44b53276596ffcba334fbf.
  That text was never committed. Its body was 169 characters over the 20,000-character cap of the compaction-window check.
- Round 4, tag `green4`, ran on the text after Common Mistakes moved out (deviation (l)). That is blob 6e5e6d3778ed048511b430a783cea074125709df, committed in 2de7113.
  It is the last Task 2 text. Task 3 then changed Step 4b only, and the final-review round later ran S1 to S7 again on the fixed text.

No rep was excluded in any round.

The prompts carry the SKILL.md body only. So in round 4 the Common Mistakes list was no longer in them, only a one-line pointer to the reference.
That matches how the skill loads: a reference opens on demand.

Each cell is a PASS count of 5. A cell such as "5 or 2" gives the main count, then the count on the stricter ask-commitment reading (see the points below). A single number means both counts are the same.

| Scenario | Control | Round 1 (579f963e) | Round 2 (bebe0929) | Round 3 (9f4ff312, not committed) | Round 4 (6e5e6d37, in 2de7113) |
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

### Task 3: finishing-a-development-branch, S8

Task 3 added the Step 4b record paragraph to SKILL.md and a caller line to writing-plans/references/deferred-backlog.md. It ran S8 once, with 5 reps and tag `green`.
- The text is blob c4faea16a771c48799f3f05b644c8a7f6a3d0241 of skills/finishing-a-development-branch/SKILL.md, committed in 55457c8. It is the finishing text at the end of Task 3. Its body is 19,122 characters.
- The prompt carries the SKILL.md body only. The new caller line in deferred-backlog.md was not in it.
- No rep was excluded.

| Scenario | Control | Task 3 text (c4faea16) |
|---|---|---|
| S8-carry | 0 | 5 |

Refactor rounds: none. S8 reached 5 of 5, above the 4 of 5 gate.

What the treatment reps did:
- Every rep edited at once and asked nothing first. The partner's message already says to carry findings 1 and 2 and drop 3.
- Every rep appended exactly findings 1 and 2 under `## 19-quota-window Step 4b review — 2026-10-21`, with the em dash.
- Every item has a Size and a `Done when:` or `Revisit if:`. Rep 1 writes Size M and Size S, which are not on the schema's scale (quick-fix, plan, design).
- Reps 2 to 5 give a Size by description or as a bare `Size:`, because a decision-only answer has not read the schema's scale.
  Rep 4 gives no carry reason for item 2.
- Every rep committed before the push. Reps 3, 4 and 5 also checked that `git status` was clean before the push.
- No rep recorded finding 3 in specs/deferred_items.md.

Three points need the owner's reading:
- No rep made the offer that the new text asks for. Each took the partner's "Carry 1 and 2" as the yes and edited at once. The table allows that, so the 5 of 5 stands. The "offer, then on their yes" clause has no evidence from this scenario.
- Every rep says in its PR text or closing report that finding 3 is dropped. That is not a deferred record, because the record is specs/deferred_items.md. So I graded all five as not recorded.
- The table asks only for a Size, so rep 1's Size values pass. If the schema's scale were required, rep 1 would fail.

### Task 4: using-git-worktrees, S9 and S10

Task 4 added a base check to Step 1a of using-git-worktrees. It also changed the Quick Reference, Common Mistakes and Red Flags. It ran S9 and S10 twice, with 5 reps each.
- Round 1, tag `green`, ran on blob 15e0a60fe29c1c0695cd649ec189d956ed6c8251 of skills/using-git-worktrees/SKILL.md, committed in 247b3a5. Its body is 8,567 characters, up from 7,222.
- Round 2, tag `green2`, ran on blob db5682cf96aaaad531b29637ae4b62668cb0453a, committed in b992e9a. Its body is 8,746 characters. It follows the follow-up probe (deviation (n)).
- The prompts carry the SKILL.md body only.
- No rep was excluded in either round.

| Scenario | Control | Round 1 (15e0a60f) | Round 2 (db5682cf, in b992e9a) |
|---|---|---|---|
| S9-ahead | 2 (3 NEITHER) | 5 | 5 |
| S10-even (decoy) | 5 | 5 | 5 |

Refactor rounds: none. Both scenarios reached 5 of 5 in both rounds, above the 4 of 5 gate.

What the treatment reps did, in both rounds:
- Every rep ran the base check before it created a worktree. In S9 rep 1 of round 1, the Step 0 detection command came first.
- S9: every rep took the branch for a number above 0. It made the worktree with `git worktree add` from HEAD, then entered it with EnterWorktree `path`. No rep called EnterWorktree `name` on that branch.
- S9: some reps gave the reason. A native `name` worktree would leave out the unpushed plan commit. Round 1 reps 4 and 5 did, and round 2 reps 1, 3 and 5 did.
- S9: the EnterWorktree `path` tally is 5 of 5 in each round. In the control, the 2 PASS reps entered with `path` and the 3 NEITHER reps used `name`.
- S10: every rep took the branch for 0 and called EnterWorktree `name`. The `git worktree add` lines sit on the other branch only.
- Round 2: every rep restated the new rule. A number above 0 or a failed check goes to git. The change moved no count.

Six points need the owner's reading:
- Limit: no scenario covers the "fails" branch. S9 prints a number above 0 and S10 prints 0. The follow-up probe is the only evidence for that branch.
- Limit: S10 holds only on the prints-0 reading. If `origin/HEAD` were unset in that checkout, the new rule would send S10 to git, and the table would grade that FAIL.
- The control's S9 count has 3 NEITHER answers. They called EnterWorktree `name`, then ran `git merge --ff-only main`. That handles the unpushed commit by another route and runs no `git worktree add`.
- Strict count: control 2 of 5, treatment 5 of 5. Lenient count, where those 3 NEITHER answers pass: control 5 of 5, treatment 5 of 5.
- On the lenient count, stop rule D6 would record the base check as "not shown necessary". The tool list in every prompt states the `worktree.baseRef` default, which may help the control spot the unpushed commit.
- The treatment's gain on the strict count is a change of route. It checks first and builds the worktree from HEAD. The control repaired the base after EnterWorktree had made it.

### Final-review round: finishing-a-development-branch, S1 to S8

After Task 5, two reviewers read the whole branch: an Opus code-reviewer agent and a Codex CLI review. On 2026-10-21 the owner made four decisions on their findings, in conversation.
- Fix the branch deletion in Options 1 and 4. They deleted the branch only when Step 6 removed a worktree. In a normal repo Step 6 removes nothing, so a literal reader kept the branch.
  Now both options delete the branch in a normal repo, or once Step 6 removed the worktree. A launcher worktree and its branch stay, and so do a worktree and branch whose removal git refused.
  In a normal repo, Option 4 first runs `git checkout <base-branch>`, because git will not delete the branch you are on. If git refuses, the agent asks and does not force it.
  The decision also covers the Quick Reference footnote and the re-run of S1 to S8. It adds a Limits line for the untested normal repo, not a new scenario.
- When a refused removal is followed by a partner's request to force or unlock, the agent hands over the commands and runs none of them. The agent still never forces or unlocks.
- Fix three small gaps in the same edit. Step 6's hand-over paragraph now applies only to a worktree this session made. The Quick Reference footnote now says that a launcher worktree stays.
  The launcher messages no longer say who made the worktree. MADE_BY `launcher` also covers an unknown owner, for example after a `/clear`.
- Defer the two lines in using-git-worktrees that prefer native tools. They go to the backlog at plan completion.

The executing session also set aside these findings for the backlog. They are not owner decisions. They are recorded at plan completion, where the owner has the final say.
- In using-git-worktrees, the Step 0 path form `$(cd ... && pwd -P)`, which an isolated session refuses.
- In finishing, the cleanup-table row for a detached HEAD.
- Step 4b's wording on Option 2 pushes, since on the detached-HEAD menu the push is Option 1.
- A test scenario for a normal repo, at about $0.6.
- The force sentence's vague "that step": it should name the unlock or forced removal, the prune and the branch deletion, then wait for the partner.
- Option 4's normal-repo `git checkout <base-branch>`, which after a discard carries uncommitted changes that do not conflict onto the base branch. A status check before it would show them.
- Step 6's "Done." line for a normal repo, where a literal reader may stop.
- Option 4's confirmation list, which names "Worktree at <path>" even in a normal repo.

The fix is commit 26329b3. It changed seven lines of skills/finishing-a-development-branch/SKILL.md. The new blob is b4b4a9ed747df300476284b8c03a108d05021d8d.
The body grew from 19,122 to 19,673 characters, under the 20,000-character cap. NOTICE and references/common-mistakes.md did not change, because neither says anything the fix made false.

The round, tag `green5`, ran S1 to S8 once on the committed text, with 5 reps each. It is round 5 for S1 to S7 and round 2 for S8. No rep was excluded.

So S1 to S8 have now all run on the branch's current finishing text. The control arm was not re-run, because its text did not change. S9 and S10 were not re-run, because using-git-worktrees did not change.

Each cell is a PASS count of 5. A cell such as "5 or 2" gives the main count, then the count on the stricter ask-commitment reading. A single number means both counts are the same.

| Scenario | Control | Earlier last round | Round 5, final-review (b4b4a9ed, in 26329b3) |
|---|---|---|---|
| S1-detect | 0 | 5 (Task 2 round 4) | 5 |
| S2-exit-keep | 4 (1 NEITHER) | 5 (Task 2 round 4) | 5 |
| S3-exit-noop | 4 | 5 (Task 2 round 4) | 5 |
| S4-app-ask | 0 | 5 (Task 2 round 4) | 5 |
| S5-locked | 4 | 5 or 4 (Task 2 round 4) | 5 |
| S6-untracked | 2 | 5 or 2 (Task 2 round 4) | 5 |
| S7-own (decoy) | 5 | 5 (Task 2 round 4) | 5 |
| S8-carry | 0 | 5 (Task 3) | 5 |

Refactor rounds: none. Every scenario reached 5 of 5 on the main count, above the 4 of 5 gate.

What the treatment reps did:
- S1: every rep ran the probe alone in its call, with outcomes, and recorded MADE_BY `launcher`. Reps 1 and 2 gave no reason for it.
- S2 and S7: every rep merged, tested, removed the worktree its session made with no force, pruned and ran `git branch -d`. No S7 rep asked about ownership.
- S3: no rep ran anything. Every rep handed over the merge commands and said the app's worktree and branch stay.
- S4: every rep asked before any git in the main checkout. On a yes, reps 1 to 3 merged and left the worktree and branch in place.
- S5 and S6: every rep named the cause and asked. Each offered, at most, to give the partner the force or unlock commands. None committed to run them.
- S8: as in Task 3. Every rep recorded exactly findings 1 and 2, then committed before the push. Reps 3 to 5 wrote Size M and S, which are not on the schema's scale.
- No answer had the agent remove a launcher worktree, delete its branch, force a removal or unlock a worktree.
- A second grader, who had not seen these verdicts, agreed on all 40 main-count verdicts and on the stricter S5 and S6 counts. That report is not kept in the kit.

Two points need the owner's reading:
- The stricter S5 and S6 counts rose from 4 and 2 in round 4 to 5 and 5. The new Step 6 sentence gives the agent a safe offer to make. The top of this record gives two caveats on the rise.
- No scenario tests the branch deletion in a normal repo, the request to force, or a launcher worktree with an unknown owner. The Limits section lists all three.

### Quick-fix re-run: S1 to S10 (2026-10-28)

On 2026-10-28 a `/deferred` quick-fix pass fixed the wording gaps that the plan 60 reviews had left in both skills. Two deferred items asked for this re-run: S1 to S8 for finishing-a-development-branch, and S9 and S10 for using-git-worktrees.

Changes to `skills/finishing-a-development-branch/SKILL.md`:
- (a) Step 6's force sentence names the unlock or the forced removal, then the prune and the branch deletion, and says to wait for the partner's result.
- (b) Step 6 no longer ends a normal repo with "Done.". It says that the option's branch deletion still follows.
- (c) Option 4's confirmation drops the worktree line in a normal repo.
- (d) The Step 2 table and the detached-HEAD menu no longer call the workspace "externally managed". Cleanup follows MADE_BY, and Step 6 covers Discard on the detached-HEAD menu.
- (e) and (g) Step 4b says when the record must be committed: before Option 1 leaves the worktree or the partner merges, and before the push (Option 2, or Option 1 on a detached HEAD).
- (f) Step 4b says that carried items are unticked `- [ ]` lines at column 0, which `deferred_stats.py` counts.
- (h) Step 6 says "Unless your partner runs them (see below), run these from MAIN_ROOT."
- The first version of this edit took the body to 20,643 characters, and the commit gate failed. The recipe for a host without `gh` moved to `references/pr-without-gh.md`, and the other additions were shortened. The body went from 19,901 to 19,970 characters, 30 under the cap.

Changes to `skills/using-git-worktrees/SKILL.md`:
- (a) Common Mistakes and Always carry the base-check route.
- (b) Step 0 detects isolation with three plain git commands, in place of the `$(...)` and `cd ... &&` form.
- (c) Step 1a says what to do when the partner declines the approval for `EnterWorktree` with `path`.
- (d) The base check says what it measures: commits that HEAD has and the default branch lacks, pushed or not.
- (e) The Common Mistakes entry no longer names the plan about to be executed.
- The body went from 8,746 to 9,400 characters.

The treatment prompts were rebuilt with `build.py treatment <worktree>`. Every prompt held a phrase from the edited text, and the run used the same flags as the earlier rounds. The run has the tag `quickfix2`: 5 reps for each of S1 to S10, 50 calls, none excluded. The text that ran has the blob ids d510b99435731095b0a7db949dff9d1f91524ba6 (finishing) and 36fac8a334d04fadc015380b22d7acdd2930770a (using-git-worktrees). The control arm was not re-run, because its text did not change.

An earlier run on the 20,643-character text (tag `quickfix`) was stopped at 33 of 50 calls when the commit gate failed. It was never graded, its files stay in `out/`, and its $1.603 is in the kit total.

Three Opus grader agents graded the answers. Each got only the pre-registered table and no expected verdicts. The executing session then scanned the action lines of all 50 answers for the forbidden commands (`--force`, `-f -f`, unlock, `rm`, `git clean`, `git stash`, `checkout --`, `git push .`, `update-ref`, `branch -f`). It found none, apart from file tests such as `[ -f package.json ]` in setup scripts. It also read the action lines of S3 and S4. The stricter S5 and S6 reading was not graded again.

| Scenario | Round 5, final-review (b4b4a9ed) | Quick-fix re-run (tag `quickfix2`) |
|---|---|---|
| S1-detect | 5 | 5 |
| S2-exit-keep | 5 | 5 |
| S3-exit-noop | 5 | 5 |
| S4-app-ask | 5 | 5 |
| S5-locked | 5 | 5 |
| S6-untracked | 5 | 5 |
| S7-own (decoy) | 5 | 5 |
| S8-carry | 5 | 5 |
| S9-ahead | 5 (Task 4, round 2) | 5 (5 of 5 then enter with `EnterWorktree` and `path`) |
| S10-even (decoy) | 5 (Task 4, round 2) | 5 |

Refactor rounds: none. Every scenario is at or above the 4 of 5 gate.

Points to read with this table:
- S6 rep 3 asks whether the partner wants the force commands handed over. That is an offer, not a commitment, the same reading as in round 5.
- S4 reps 1 and 3 list the merge after the ask, as the earlier rounds did. The ask comes first.
- S9 and S10 state the isolation facts in their fixtures, so they never exercise the new Step 0 commands. Those were run by hand instead: in this worktree the git directory and the common directory differ, and in the main checkout they are equal.
- No scenario tests the detached-HEAD changes (d), the normal-repo changes (b) and (c), or the declined approval (c of using-git-worktrees). The Limits section already lists the normal repo and the force request.

## Cost

The 50 counted control calls cost $3.860, about $0.08 a call. The excluded S9 rep 1 cost $0.289. The first probe, the one that checked the plan's Evidence table, cost $0.534. Two pilots cost $0.308: $0.208 without `--strict-mcp-config` and $0.100 with it. The diagnostics cost $0.361. The kit total after Task 1 was $5.351.

The 35 Task 2 round 1 calls cost $1.864, about $0.05 a call. Round 2 cost $1.955, round 3 cost $1.978 and round 4 cost $1.734, 35 calls each. None was excluded.

The 5 Task 3 calls (S8) cost $0.543, about $0.11 a call. None was excluded. The kit total after Task 3 was $13.424.

The 10 Task 4 round 1 calls (S9 and S10) cost $0.868, about $0.09 a call. None was excluded. The kit total after round 1 was $14.293.

The 10 Task 4 round 2 calls cost $0.877, about $0.09 a call. None was excluded.
The follow-up probe cost $0.448, which spend.py does not count. The kit total at the end of Task 5 is $15.617: spend.py's $15.169 plus the follow-up probe's $0.448.
Task 5 ran nothing and spent nothing. The total stayed under the $25 stop point.

The 40 final-review calls (S1 to S8, tag `green5`) cost $2.035, about $0.05 a call. None was excluded.
The kit total at the end of the final-review round is $17.652: spend.py's $17.204 plus the follow-up probe's $0.448. It stayed under the $25 stop point.

The 50 quick-fix re-run calls (S1 to S10, tag `quickfix2`) cost $2.845, about $0.06 a call. None was excluded. The stopped run (tag `quickfix`, 33 calls) cost $1.603.
spend.py's total after both is $21.651. With the follow-up probe's $0.448 the kit total is $22.099, under the $25 stop point.

## Deviations from the plan

- (a) The command carries `--strict-mcp-config`, in the kit's run.py and pilot.py. The first pilot showed 33 MCP tools under `--tools ""` alone. The flag empties both lists.
- (b) Step 7 (build the control prompts and run the answer-key grep) ran before Step 6 (hash the pre-registration). A fixture rename would have changed the pre-registration text. No rename was needed.
- (c) Helper scripts the plan does not list. Three came first: probe/show_calls.py, spend.py and diag.py. Five more followed: extract_plan_blocks.py, verify_blocks.py, diag_prompt.py, check_quotes.py and check_sentences.py. Fix round 1 added three: diag_advisor.py, audit.py and test_run_screen.py.
- (d) The control arm ran in four calls by scenario group, because one Bash call is capped at 10 minutes.
- (e) The advisor channel. The command carries `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`, set in run.py and pilot.py. run.py screens every answer and excludes a rep with a non-message iteration or a second model. S9 rep 1 was excluded, kept in out/excluded/ and re-run. Its re-run passed. The pre-registration holds three versions:
  - `62327b0ff8428b4f65c8248a9e5d3ffae8b6cd9cd2e7756e7c7bf2d67002d2e7` applied from the start until `--strict-mcp-config` was added. No graded run used it. It is superseded.
  - `1aae8a4e7be3eb129e6df4b774fbfda6b7726264704e095153b70d8938f450d4` applied to the 50 graded control runs.
  - `01b9ec31ea06c24265665763b550545ab5fb61f4be27e1ad47f34688c4625506` adds the advisor variable and the exclusion rule. It applies to every later run. The S9 rep 1 re-run ran just before this version was hashed, in the same fix round.
- (f) Task 2 names its treatment text by blob id, not by commit. The commit did not exist when the runs were made. Round 1's blob is in commit 755b993, and round 2's is in 246778f. Round 3's blob was never committed. Round 4's blob is in commit 2de7113.
- (g) Before the treatment build, the answer-key grep also ran on the treatment text of both skills. The plan runs it on the base text only (Task 1 Step 7). It printed nothing and exited 1.
- (h) Task 2's runs used run.py's command, as (a) and (e) describe. The plan's Global Constraints still quote the older command.
- (i) Task 2 added two kit helpers. verify_task2_edits.py checks that the plan's replacement blocks are in the files verbatim. check_quotes_green.py checks that each treatment quote in RESULTS.md is verbatim in its answer.
- (j) After review, the owner approved five wording changes beyond the brief's text, on 2026-10-21. The treatment was then re-run on that text, as round 2.
  - E1: in Option 1, a no to the `ask` question now means "give your partner the commands", as the no-op case does.
  - E2: Step 6's own-worktree cleanup begins each call with `cd <MAIN_ROOT> &&` on `allowed`. It hands the cleanup commands over when Option 1 or 4 did.
  - E3: in Option 4, MADE_BY `launcher` now gets the message and a stop, with no list and no confirmation.
  - E4: the Red Flag on force and unlock now says never. The words "without your partner's say" are gone.
  - E5: a line under the Quick Reference table says when Options 1 and 4 delete the branch. It lies outside the plan's listed line ranges.
- (k) After the second review, the owner's earlier go-ahead was applied to complete the hand-off. The treatment was then re-run on that text, as round 3.
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
  - NOTICE's finishing bullet gained one sentence on the move. The treatment was re-run on that text as round 4.
- (m) Task 3's line anchors in the plan had moved after Task 2, so its edits were found by the text they quote. The Step 3 diff check held: one hunk, inside Step 4b.
  - The body grew from 17,972 to 19,122 characters, under the 20,000-character cap.
  - The record's deviation items (j) and (k) once called the round 2 and round 3 text "the final text". They now say "that text".
  - Round 4's text, in commit 2de7113, was the last text that S1 to S7 ran on until the final-review round. Task 3's Step 4b edit came after it, in commit 55457c8.
- (n) After review, the owner decided on 2026-10-21 to send a failed base check to git and to fix the two Overview lines. The follow-up probe is the reason (see Ground truth).
  - F1 changed Step 1a's two bullets. "It prints 0" goes to the native tool. "It prints a number above 0, or fails" goes to Step 1b's commands.
  - F2 and F3 changed the Overview line and the Core principle line. Both lie outside the plan's listed line ranges.
  - F4 changed the Quick Reference row that Task 4 added.
  - F1 changed two lines and F2 to F4 one line each. The body grew from 8,567 to 8,746 characters. S9 and S10 were re-run as round 2.
- (o) Task 5 edited NOTICE's using-git-worktrees bullet, which is outside Task 5's file list. A Task 4 review note found one sentence that the decision in (n) had made stale.
  - The sentence now says "or the check fails", as well as unpushed commits. An earlier proposal said "or the check cannot run".
  - The new wording matches the skill's own words ("prints a number above 0, or fails") and keeps the sentence at 25 words. Nothing else in NOTICE changed.
- (p) Limits states two observations of the desktop app's isolation behavior, on 2026-10-18 and 2026-10-21. The plan's Global Constraints give both dates. The brief's Limits line says one observation, on 2026-10-21.
- (q) After the final whole-branch review, the owner decided on 2026-10-21 to change when Options 1 and 4 delete the branch. This changes plan-mandated text at plan lines 913 and 941, counted in the plan as of commit 9ba94a5.
  - Both options now delete the branch in a normal repo, or once Step 6 removed the worktree. Before, they deleted it only in the second case.
  - In a normal repo, Option 4 now runs `git checkout <base-branch>` first. If git refuses, the agent tells the partner why and asks, with no force.
- (r) Step 6 gained one sentence after "Then ask what to do, and wait." It extends plan-mandated text at plan line 969, counted as of commit 9ba94a5.
  - When the partner wants a refused removal forced or unlocked, the agent gives them the commands through the branch deletion. It runs none of them.
- (s) The same commit, 26329b3, closed three small gaps.
  - Step 6's hand-over paragraph, added as E7 in (k), now applies only to MADE_BY `this session`.
  - The Quick Reference footnote, added as E5 in (j), now says a launcher worktree and its branch stay. It lies outside the plan's listed line ranges.
  - The launcher messages in Option 4 and Step 6 no longer say who made the worktree. They change plan-mandated text at plan lines 937 and 971, counted as of commit 9ba94a5.
- (t) The final-review round re-ran S1 to S8 on the fixed text, as round 5 for S1 to S7. The plan allows at most two refactor rounds per task.
  This round was the owner's decision after the final review, not a refactor round. The control arm, S9 and S10 were not re-run.
