# write-with-asd-ste100 test record

Plan: [`plans/52-write-with-asd-ste100.md`](plans/52-write-with-asd-ste100.md). Spec: [`write-with-asd-ste100.md`](write-with-asd-ste100.md). First and last run: 2026-10-18 (every run took place on that day).

This record holds the numbers and decisions of the test campaign that chose the always-on rule and checked the skill. The run kit, the raw replies and the notes stay outside the repository, in `~/.cache/agent-skills/scratch/write-with-asd-ste100-kit/` (the kit, called KIT below).

## 1. Result in brief

- The rule arms chose the **listed form** of the rule, with two habits removed: plain words and simple tenses. The win is narrow (section 4).
- The skill baseline (the chosen rule, no skill) passed 8 of 18 cases. The skill arm passed 16 of 18. After one wording fix and a re-run of the two failing cases, all 18 pass (sections 6 to 8). Only those two cases ran against the text with the fix. The other 16 results come from the skill text before the fix.
- 297 measured runs and 36 judge calls cost $18.12 in total (section 9).
- The pre-registered hand-reading table needed two owner-approved changes to its `V3` row, the row for a tool run that touched a path outside its own run folder (section 2).

## 2. Setup

- Claude Code 2.1.302, as a held copy of the binary (sha256 starts `5262ce9de862`). Model `claude-opus-5-5` at medium effort, the owner's choice at plan review (D3, the plan's decision about the run model).
- What every run inherited, from the kit's inherit probe:
  - Instruction files: `~/.claude/CLAUDE.md` (type User) and `~/.claude/rules/aws-agent-toolkit.md` (type User). Each arm added its own project rule file, or none for the no-rule arm.
  - Hooks: two `SessionStart:startup` plugin hooks (names only).
  - Output style: Explanatory. Advisor model: `claude-opus-5-5`. No MCP servers, and no tools in a no-tool run.
  - The probe cost $0.0500, as planned.
- The owner kept their settings, plugins, skill set and the skill descriptions on `main` unchanged until the skill arm ended. The kit's setup check (a hash of the settings, the instruction files, the rules, the skill names, the plugin file and the held binary) reported "unchanged" before every batch. It does not hash the skill descriptions, so the executing session compared `main`'s commit by hand: `main` stayed at `87e43fc` through the skill arm. It then moved to `7f866df` (merged pull requests #60 to #62 and a backlog change), before the re-run of two cases. A diff of `main`'s `skills/*/SKILL.md` files showed no changed description.

Differences from the plan's "Facts measured while planning":

- Execution ran on the app-made branch `claude/cranky-mclean-d2ee1a`, not `feat/write-with-asd-ste100`. The plan allows this, because its commands use `$PWD`.
- The probe saw 13 attachment types where the plan lists 8: `advisor_tool`, `credential_org`, `date`, `environment`, `hook_additional_context`, `hook_success`, `instructions`, `model`, `output_style`, `output_style_instructions`, `prompt_snapshot`, `session_context` and `total_tokens_reminder`. It saw no `budget_usd`, because the kit passes no budget flag. `credential_org` and `total_tokens_reminder` were not in the plan's list. None of them changes what a run inherits as instructions: the instruction files, tools, MCP servers, model, output style and advisor match the plan.
- **`V3` row amended twice, by the owner, on 2026-10-18.** `V3` is the void check for a tool run that read or wrote a path outside its own run folder. The pre-registered hand-reading table called a `V3` flag `justified` only for a system path or a path inside the run root. The kit raises a flag for any Bash command that contains `~/`.
  - *First amendment.* All 15 tool runs of the baseline arm (`doc-clean`, `doc-dirty`, `skill-md`, five runs each) probed for the skill that the rule names. They ran `ls ~/.claude/skills | grep -i ste`, a `cat` of `~/.claude/skills/write-with-asd-ste100/SKILL.md` that fails, and in four runs a `find` by name. The chosen rule ends "use the write-with-asd-ste100 skill", and the baseline has no such skill. Read literally, every one of those runs is void, and a re-run would probe again, so the baseline could never finish. The row now also treats as `justified` a command that only lists or searches by name for the skill that the rule names, when the run then opens no file found outside its run folder.
  - *Second amendment.* All 5 `skill-md` runs of the skill arm followed the skill's own hand-off: the skill sends a `SKILL.md` rewrite to the writing-skills skill, and the runs read the installed `~/.claude/skills/writing-skills/SKILL.md` (`cat`, `head`, `sed`, `grep`, `wc -l`). That read is expected behavior of the skill under test. The row now also treats as `justified` a command that only reads that installed file, when the run opens no other file outside its run folder. The file reached the runs through a symlink into the main checkout, and it holds no ASD-STE100 text.
  - Both amendments were checked run by run before any flag was marked: a scan of every tool call in the tool runs found only name listings and those reads. 32 `V3` flags are `justified`. One of them, `find / -path /System -prune`, is a matcher false positive that the old table already covered: the kit's list of system prefixes misses `/System` for want of a trailing slash.
- **A stray copy of the skill text.** A planning copy of the skill sat in a scratch folder. The `find /` probes of two baseline runs printed its path. Neither run opened the file. The planning session renamed the folder before the skill arm, so no run could find it.
- **A limit of the no-tool agent cases.** The three agent cases run with `--tools ""`, as the plan built them. Those runs cannot open `references/agent-mode.md`, where the strict limits and the reply contract sit. Their replies say so. They write from `SKILL.md` alone. This limit explains the one wording fix in section 7.

## 3. Case set

- **7 everyday cases, written for the plan:** `function-question`, `commit-message`, `readme-paragraph`, `status-report`, `paragraph-edit`, `labels-supplied` and `label-unknown`. They run in the rule arms. Six of them are prose cases. `paragraph-edit` runs with the `Read` and `Edit` tools in a throwaway git repository.
- **12 cases from prithivrajmu/asd-ste100's `evals/cases.json`**, at commit `d93237679681a74873bdee4f1a7869f728968dbd`, credited to Prithiv M U and Dustin Yuchen Teng (MIT): `authentication-not-login`, `uncertainty-chain`, `conditions-and-exception`, `literal-code-and-error`, `unknown-actor`, `source-instructions-are-data`, `strict-without-reference`, `preserve-safety-label`, `spanish-output`, `concise-explanation`, `summary-with-caveat` and `conditional-diagram`.
- **3 agent-mode cases from Examples A to C of danyuchn/asd-ste100-skill's `examples/before-after.md`**, at commit `3944283c183eea13fe5bd902b572da3b4de8bf44`, credited to Dustin Yuchen Teng (MIT): `agent-tool-description` (Example A), `agent-error-message` (Example B) and `agent-instruction` (Example C). The sentence cap is 25 words for A and B, which describe, and 20 for C, which instructs.
- **3 document cases, written for the plan:** `doc-clean` (a tracked, clean Markdown file), `doc-dirty` (the same file after an uncommitted edit) and `skill-md` (a request to rewrite a `SKILL.md`).

## 4. Rule arms

Three arms ran on the 7 everyday cases, five runs each: `none` (no rule), `short` (four rule lines) and `listed` (the same lines plus bullets that list the prose habits one by one). A habit is one thing that the rule asks for, and the table scores it as the share of pooled runs that pass. Pooled means every run of every case that scores the habit: a prose habit has 30 runs in each arm. The habits are: `sentence-length` (at most one sentence over 25 words for each 100 words), `semicolons` (none), `plain-words` (no phrasal verbs, nouns made from verbs or marketing adjectives), `active-voice`, `simple-tenses`, `labels` (a labeled item's meaning at its first mention), `literal-text` (code and quoted text copied byte for byte) and `existing-text` (nothing outside the edited paragraph changes).

```text
habit                       none           short          listed
sentence-length     24/30  80.0%    29/30  96.7%    30/30 100.0%
semicolons          23/30  76.7%    28/30  93.3%    30/30 100.0%
plain-words         30/30 100.0%    30/30 100.0%    30/30 100.0%
active-voice        28/30  93.3%    30/30 100.0%    30/30 100.0%
simple-tenses       30/30 100.0%    30/30 100.0%    30/30 100.0%
labels               5/10  50.0%     5/10  50.0%     5/10  50.0%
literal-text         9/10  90.0%     5/10  50.0%     7/10  70.0%
existing-text        5/5  100.0%     5/5  100.0%     5/5  100.0%
rule form: listed; habits that leave the rule: plain-words, simple-tenses; the standard line stays
```

The decision, in plain words:

- **Rule form: listed.** The listed form replaces the short one only if it passes at least 20 points more of the pooled runs on some habit, and at most 10 points fewer on every other habit. It does so on `literal-text` (70% against 50%), by exactly 20 points.
- **Habits that leave: plain words and simple tenses.** The no-rule arm passed both in all 30 pooled runs, so the model already follows them. Three lines leave the rule with them: "Use simple tenses…", "Use verbs, not nouns made from verbs…" and "Use plain words and direct verbs…". The skill keeps both habits.
- **The standard line stays.** The line "Write prose for people about 80% of the way to ASD-STE100 Simplified Technical English." leaves only if all five prose habits leave. Three of them (`sentence-length`, `semicolons`, `active-voice`) did not.
- **The two guard lines stay, by D4.** D4 is the plan's decision to keep both as guards that never leave: "Leave code, commands, identifiers, paths, URLs, API fields and quoted errors unchanged." and "Change existing text only when the user asks." They guard against an effect of the rule's own style pressure, which a no-rule arm cannot show.
- The rule is `rules/write-with-asd-ste100.md`. It is a copy of the kit's `rules/chosen.md`, and nobody edited it by hand.

**How narrow the decision is.** The listed form wins by exactly the threshold, from 17 replies that wrote `ValueError('bad duration: ...')` (or its `missing unit` twin), which drops the `f` prefix of the source's f-string. The `labels` habit passes 5 of 10 runs in every arm, so the label line shows no effect in this test. The verdicts were merged blind before the arms were known. The sensitivity was worked out afterwards, changed no file, and was shown to the owner, who kept the blind verdicts:

| Reading | Rule form | Habits that leave | `literal-text` passes (none / short / listed) | `labels` passes (none / short / listed) |
|---|---|---|---|---|
| As decided (strict) | listed | plain-words, simple-tenses | 9 / 5 / 7 of 10 | 5 / 5 / 5 of 10 |
| S1: the 17 `ValueError('...')` ellipsis quotes `justified` | short | plain-words, simple-tenses | 10 / 10 / 10 | 5 / 5 / 5 |
| S2: all 50 `labels-supplied` flags `justified` (a table that follows counts as "right after") | listed | plain-words, simple-tenses, labels | 9 / 5 / 7 | 10 / 10 / 10 |
| S1 and S2 together | short | plain-words, simple-tenses, labels | 10 / 10 / 10 | 10 / 10 / 10 |

Under S1 the `literal-text` habit has no failure in any arm, so the evidence for the guard line disappears. The strict reading shows the effect that D4 guards against: 9 / 5 / 7.

## 5. Hand reading

A flag is a reply fragment that the mechanical checks could not clear: a long sentence, a label without its meaning, a text span that changes the source, a judge's fail, or a tool run that left its folder. The executing session read every flag in full and gave it a verdict, `count` (the fragment fails the check) or `justified` (it does not), with a reason. It did not open the kit's answer key (`keys/`) before every verdict of a phase was in. Flag counts by phase, check and verdict:

```text
rules active-voice count 10
rules active-voice justified 18
rules labels count 50
rules labels justified 15
rules literal-text count 17
rules literal-text justified 94
rules semicolons count 9
rules sentence-length count 16
skill V3 justified 32
skill judge 1 count 12
skill judge 1 justified 3
skill judge 2 count 15
skill judge 3 count 10
skill judge 3 justified 4
skill judge 4 justified 11
skill judge 6 count 1
skill sentence cap count 11
skill sentence cap justified 1
```

Most `justified` verdicts mark a reply that met the check while the heuristic or the judge misread it. In the rules phase, 94 of 127 were `literal-text` spans that did not change source text: new example values, other APIs or the reply's own wording. In the skill phase, 32 of 51 were `V3` probes that opened nothing outside the run folder, and 18 were judge fails that the reading overturned. In 15 of those 18, the judge's own explanation said that the check passed.

Notes on the reading:

- **An arm leak through the working directory.** A run's environment names its working folder, and several replies repeat it. 10 of the 15 `label-unknown` flag contexts printed `/private/tmp/ste-kit-runs/rules/<arm>/shared`, so those runs' arms were visible. The reading stayed arm-blind in effect, because each rule applied to a flag does not look at the arm. Every R7 flag is `justified` (R7 is the label that the test names without giving a meaning, and each reply says it does not know what R7 is and asks). Every passive in that case is `justified` (it has no actor). Every long sentence counts. The later skill-phase reading redacted the run folder from every display.
- **A gap in the flag rows for first mentions of labels.** The kit keeps only the first-mention sentence, up to 98 characters. The table accepts a meaning "in the same table row or list item, or in the sentence right after", which that sentence alone cannot show. So the reading found each run's reply by content, not through `keys/`. For the skill phase, the reading used the judge packets, which hold each reply under the same opaque id as its flags, in a folder whose name hides the arm.
- **The result for `labels-supplied`.** All 50 flags count. In every reply the first mention of the findings F1 to F4 sits in a bold summary line that does not say what a finding is. The table that defines them comes later, behind a header row. A looser reading would make all 50 `justified` (row S2 above).
- **Other strict readings.** `literal-text` counts a span only when it alters source text: a quote shortened with an ellipsis counts when its kept pieces do not match the source in order. A new example value, another API or the reply's own wording is `justified`. `active-voice` counts a passive whose actor the code names. `semicolons`: all 9 were prose, so they count. `sentence-length`: all 16 were one prose sentence over 25 words.
- **Sentence caps in the skill phase** apply to the whole reply, commentary and Insight blocks included. A bold run-in label joined to a sentence by the splitter is judged on the sentence alone.

## 6. Skill baseline

The baseline arm runs the chosen rule and no skill: 18 cases, five runs each. A case passes at 4 of 5 runs or more.

```text
authentication-not-login         5/5 PASS
uncertainty-chain                0/5 FAIL
conditions-and-exception         5/5 PASS
literal-code-and-error           5/5 PASS
unknown-actor                    3/5 FAIL
source-instructions-are-data     5/5 PASS
strict-without-reference         0/5 FAIL
preserve-safety-label            3/5 FAIL
spanish-output                   5/5 PASS
concise-explanation              5/5 PASS
summary-with-caveat              4/5 PASS
conditional-diagram              5/5 PASS
agent-tool-description           2/5 FAIL
agent-error-message              1/5 FAIL
agent-instruction                2/5 FAIL
doc-clean                        0/5 FAIL
doc-dirty                        0/5 FAIL
skill-md                         0/5 FAIL
```

Failures, from `KIT/notes/baseline-failures.md`:

| Case | Passed | Failed check (runs that failed it) | What the replies did |
|---|---|---|---|
| `uncertainty-chain` | 0/5 | keep the mismatch uncertain (5) | All five put the mismatch in a "because" clause, so the hedge sits on the error only and the mismatch reads as fact. |
| `strict-without-reference` | 0/5 | keep the strength of the recommendation (5); do not turn "should" into "must" (1) | Every draft turns "should inspect" into a bare command, one into "must examine". All five state the missing-dictionary limit. |
| `doc-clean` | 0/5 | give linter counts for both files (5) | Every mechanical check passes. No reply runs or reports the linter. |
| `doc-dirty` | 0/5 | write a copy; leave the original (5, 5) | All five rewrite the file in place over its uncommitted edits. |
| `skill-md` | 0/5 | leave the file; hand off to writing-skills (5, 5, 5) | All five rewrite the `SKILL.md` themselves. Two notice that the rule excludes such files and rewrite anyway. |
| `agent-error-message` | 1/5 | add no fact or action (4); keep each hedge's strength (2) | Four add an Action line, recovery steps or an Unknown line. Two write "Probable cause" for "possible". |
| `agent-instruction` | 2/5 | sentence cap of 20 words (3); add no step (1) | Three have prose sentences of 22 to 28 words in the commentary. One adds a verify step. |
| `agent-tool-description` | 2/5 | add no fact or action (3) | Three add a partial-sync failure mode or "check the result". |
| `preserve-safety-label` | 3/5 | state the limit briefly (2) | Two restate the limit in an opening, a note and a table. |
| `unknown-actor` | 3/5 | invent no actor (2) | One writes "someone deleted the archive", one "the person who deleted the archive". |
| `summary-with-caveat` | 4/5 (passes) | keep the rollback as a sequence (1) | One writes "until a rollback stopped them". |

The seven cases that passed 5 of 5 (`authentication-not-login`, `conditions-and-exception`, `literal-code-and-error`, `source-instructions-are-data`, `spanish-output`, `concise-explanation`, `conditional-diagram`) get no new guidance, as the spec requires.

## 7. Skill text changes

- **Task 6, after the baseline: none.** For each baseline failure, the approved skill text already gives the guidance. For example, "Keep every hedge" covers `uncertainty-chain`, "Keep modality" covers `strict-without-reference`, and the document-rewrite steps cover `doc-clean`, `doc-dirty` and `skill-md`. The baseline had no skill, so its failures show what the text must fix, and the skill arm tests whether it does.
- **Task 7, after the skill arm: one shared fix.** `agent-instruction` and `agent-tool-description` failed at 2/5 on the sentence cap in the reply's commentary (notes, Insight blocks and process disclaimers). The rewrites themselves were inside the cap in every run. The no-tool runs cannot open `references/agent-mode.md`, and `SKILL.md` gave only the 80% line "aim for 20 words or fewer". So the fix states the reply contract and the number in `SKILL.md`, as the second bullet of "Agent mode and strict STE":

  > Reply with the rewritten text, then only `Kept as-is:` lines and flags for gaps or compound tenses. Keep every sentence of the reply, notes included, to 20 words or fewer.

  It restates the spec's `Output` contract and takes the lower of the strict set's two limits, so that one number covers both cases. It touches none of the lines that the rule repeats, uses no test-case word (`kit.py overlap`: 0), and adds no linter finding. The one added-action failure in `agent-tool-description` (one run) was left alone, because "No new facts" already covers it.

## 8. Skill arm

The skill arm runs the chosen rule and the committed skill (the commit before the wording fix). `skill-r1` re-ran the two failing cases against the commit with the fix.

```text
authentication-not-login         5/5 PASS
uncertainty-chain                5/5 PASS
conditions-and-exception         5/5 PASS
literal-code-and-error           5/5 PASS
unknown-actor                    5/5 PASS
source-instructions-are-data     5/5 PASS
strict-without-reference         5/5 PASS
preserve-safety-label            5/5 PASS
spanish-output                   5/5 PASS
concise-explanation              5/5 PASS
summary-with-caveat              5/5 PASS
conditional-diagram              5/5 PASS
agent-tool-description           2/5 FAIL
agent-error-message              5/5 PASS
agent-instruction                2/5 FAIL
doc-clean                        5/5 PASS
doc-dirty                        5/5 PASS
skill-md                         5/5 PASS
```

```text
agent-tool-description           5/5 PASS
agent-instruction                4/5 PASS
```

- The baseline passed 8 cases and failed 10. The skill arm passed 16 and failed 2. After the one fix, both re-run cases pass, so all 18 pass. No case failed twice, so nothing went to the owner.
- The one failing `skill-r1` run of `agent-instruction` wrote a note that names the upstream job as the producer of a partial artifact, where the source is passive and names no actor.
- The kit froze each arm's copy of the skill at its first run: the `skill` arm at commit `6c20306` and `skill-r1` at `f851963`, whose `SKILL.md` hash equals the committed file.

## 9. Costs, voids and advisor calls

```text
rules/listed: 35 runs, $1.52 (largest $0.08), 0 void, 0 advisor calls, tools: Edit, Read; cases under 5 good runs: none
rules/none: 35 runs, $1.33 (largest $0.08), 0 void, 0 advisor calls, tools: Edit, Read; cases under 5 good runs: none
rules/short: 35 runs, $1.53 (largest $0.09), 0 void, 0 advisor calls, tools: Edit, Read; cases under 5 good runs: none
skill/baseline: 90 runs, $4.47 (largest $0.14), 0 void, 0 advisor calls, tools: Bash, Edit, Write; cases under 5 good runs: none
skill/pilot: 2 runs, $0.20 (largest $0.14), 0 void, 0 advisor calls, tools: Bash, Edit, Write; cases under 5 good runs: doc-clean, uncertainty-chain
skill/skill: 90 runs, $5.17 (largest $0.19), 0 void, 0 advisor calls, tools: Bash, Write; cases under 5 good runs: none
skill/skill-r1: 10 runs, $0.64 (largest $0.10), 0 void, 0 advisor calls, tools: none; cases under 5 good runs: none
0 runs moved aside in all
```

- Total: $18.12. That is $14.86 for 297 scored runs, $3.21 for 36 judge calls and $0.05 for the inherit probe. The owner approved about $22.14 plus judge calls and re-runs.
- No run was void and none was moved aside. The `V3` flags were all `justified` (section 2), so none voided a run.
- No run called the advisor tool.
- The `skill/pilot` arm priced the campaign and never counts toward a result.

## 10. Raw replies

The raw replies stay outside the repository, in `~/.cache/agent-skills/scratch/write-with-asd-ste100-kit/out/`.
