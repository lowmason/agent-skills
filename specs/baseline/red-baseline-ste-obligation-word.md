# Record: the obligation-word micro-test for write-with-asd-ste100 (plan 114)

This record holds the numbers and decisions of plan 114's micro-test (`specs/plans/114-ste-drift-and-obligation-word.md`, retired later to `specs/plans/completed/`). The kit, its rules and the scrubbed reps are in `specs/baseline/red-baseline-ste-obligation-word/kit/`. The rules are in its `PREREGISTRATION.md`. The raw streams and the rep homes stay outside the repository, in `~/.cache/agent-skills/scratch/ste114/`.

## 1. Result in brief

- The new **Obligation** meaning rule works. Every treatment cell passes the obligation check at 5 of 5. In the control arm, Sonnet kept "should" in only 1 of 5 `agent-instruction` replies. Before the hand reading, Opus passed the obligation check of `agent-error-message` in 3 of 5.
- One treatment cell misses the registered all-checks bar: `agent-instruction` on Sonnet, at 2 of 5. Two reps name "the upstream job" as the producer of partial artifacts, where the source is passive. One rep has a 21-word note sentence, over the cap of 20. Neither fault is an obligation fault, and the control arm shows the same actor guess. The owner accepted the result and asked for a new backlog item (plan 114, D9). So the registered rule for item [33], that all three agent cases pass every check on both models, was not met. D9 put the item's own done-when, the obligation check at 4 of 5 or more, in its place.
- All four document cases pass on both models, the new `doc-symlink` case included (Opus 5 of 5, Sonnet 4 of 5). This holds after the plan's V3 voided 4 `doc-symlink` reps and replacements ran (D10). A second reading, not registered, finds a wording defect in step 3 of `references/document-rewrite.md`. 7 of the 14 `doc-symlink` reps that ran wrote through the link before they took the copy branch. 3 of the 10 counted reps did. So [34]'s symbolic-link part stays open (D11).
- The total cost is $14.76 of the $30 cap.

## 2. Setup

- Claude Code 2.1.323. Models `claude-opus-5-5` and `claude-sonnet-5-5` at the default effort, 5 good reps for each case, arm and model. Judges ran on `claude-opus-5-5`.
- Each rep had its own `HOME` and `TMPDIR`, and an explicit environment with the advisor and auto memory off. It also had plan 100's PreToolUse guard, a deny list that removes the four cross-session tools, `--strict-mcp-config` and `--no-session-persistence`. The rule reached the rep as a user rule in that `HOME`. The skill reached it as an appended system prompt, `Base directory for this skill: <dir>`, then `SKILL.md` without its frontmatter. The kit kept no `origin`, `credential_expires_at`, `session_id` or `uuid`, and no kept file holds the real home path. The first version of the scrub did not redact the account name, which 10 `doc-symlink` streams held in `ls -l` output. Since amendment 2 the scrub replaces it with `<user>`, and `kit.py revoid` re-scrubbed every kept stream. Commit `395ca5d` still holds those bytes in the history (owner, D12).
- Frozen arms, by `git archive`:

  | Arm | Commit | `SKILL.md` SHA-256 | Rule SHA-256 |
  |---|---|---|---|
  | `control` | `4168d2a` | `e85c795e…` | `223a232c…` |
  | `treatment` | `546181a` | `78a2731a…` | `223a232c…` |

- Isolation probes, 4 reps. Each saw only the rule, the skill prompt and its planned tools. None saw memory, another session or the user's name. The init records list the CLI's bundled skills (`deep-research`, `dataviz` and others), but no rep had the Skill tool, and no probe named them.
- This setup differs from the 2026-10-18 campaign (`specs/completed/write-with-asd-ste100-test-record.md`), which ran with the owner's user-level context and the rule as a project rule. Its numbers do not compare one to one with these. The control arm here is the comparison.

## 3. Amendment: agent reps get Read (D8)

The first control batch, `agent-tool-description` on Opus with `--tools ""`, stopped on the $3 alarm. 4 of its 5 reps wrote tool calls as text, to open `references/agent-mode.md` and to run the linter. Two ran to the 128,000-token output limit, at $3.37 and $3.49. No void rule covered this. The owner chose "Give agent reps Read". Agent reps then ran with the Read tool only and were scored on their final message. The 5 first reps were set aside ($7.05). The kit also gained one fix: a batch now registers every rep before the alarm stops it. Before the fix, 2 finished reps had dropped out of the registry, but their cost was in the spend record.

## 4. The obligation line

The line, after the **Confidence** bullet of `## Meaning rules`:

> - **Obligation.** Keep the strength of every obligation word, also in an imperative step. "Should" stays "should". Do not make it "must" or a bare command.

The re-vendor changed no linter count. `SKILL.md` stays at 2 violations (1 hard) under both linters, and `rules/write-with-asd-ste100.md` at 2 (1 hard), 272 words. The new line adds no finding, and `SKILL.md` now has 1365 words. Function words aside, the line shares only "should" with the three agent sources, which D6 allowed.

## 5. Agent cases

All checks, then the obligation check alone, after the hand reading:

| Case | Model | control | treatment |
|---|---|---|---|
| `agent-tool-description` | Opus | 5/5 (5/5) | 5/5 (5/5) |
| `agent-tool-description` | Sonnet | 5/5 (5/5) | 5/5 (5/5) |
| `agent-error-message` | Opus | 5/5 (5/5) | 5/5 (5/5) |
| `agent-error-message` | Sonnet | 3/5 (5/5) | 5/5 (5/5) |
| `agent-instruction` | Opus | 5/5 (5/5) | 5/5 (5/5) |
| `agent-instruction` | Sonnet | 1/5 (1/5) | 2/5 FAIL (5/5) |

- The D4 control stop read the provisional tally, with every unread flag a fail. The control did not pass the obligation check on both models, so the line went ahead.
- The hand reading took all 17 flags of both arms from one shuffled sheet with no arm or model field. It came after both arms ran and before any tally line by arm. 14 were `count` and 3 `justified`. All three justified flags were judge errors. One judge read "may" as weaker than "could". Two judges counted a "must" or a "required" inside a `Flag:` note, which the check does not score.
- The counted control faults, all on Sonnet:
  - "should" turned into a bare command (`Consume`, `Use`) in 4 `agent-instruction` reps
  - "the system" as a guessed actor in 2 `agent-error-message` reps
  - an added "only when" in 1 `agent-instruction` rep
- The counted treatment faults, all on Sonnet `agent-instruction`: "the upstream job" as the guessed producer (2 reps) and a 21-word note sentence (1 rep).
- Each of the 60 counted agent reps opened `references/agent-mode.md` with Read. So the control reps had its rule "Keep modality" in front of them. Sonnet still turned "should" into a bare command in 4 of 5 `agent-instruction` reps. The line in `SKILL.md` closed that gap.
- Mechanical and judged checks: the obligation check had a mechanical half (`obligation_flags`) and a judge half (check 3). The sentence cap was mechanical. The hedge and no-additions checks were judged.

## 6. Document cases

Treatment arm only, all checks:

| Case | Opus | Sonnet |
|---|---|---|
| `doc-clean` | 5/5 | 5/5 |
| `doc-dirty` | 5/5 | 5/5 |
| `skill-md` | 5/5 | 5/5 |
| `doc-symlink` | 5/5 | 4/5 |

The document checks are exact and mechanical. `doc-clean` and `skill-md` also have one judged check, and every judge passed it.

**The plan's V3 (amendment 2, D10).** The kit's first registration voided a tool rep only for a denied call. The plan also voids a rep that reaches a path outside its `HOME`. `kit.py revoid` found 4 such reps, all `doc-symlink` (2 on each model), and each wrote its own draft to the shared `/tmp`. No rep read a file that another rep wrote. The 4 reps are void, and 4 replacements ran with no void. The table above counts the replacements.

**A second reading, not registered.** The `doc-symlink` checks read the end state only. Each rep's tool calls show more. Of the 14 reps that ran, before and after V3:

- 7 wrote through `docs/guide.md` into the dirty `docs/manual.md` first. 3 of them count.
- None of the 4 replacements did.
- Most ran step 3's three checks as one `&&` chain. On a link, `test ! -L` fails, the chain stops and prints nothing, and the rep took the silence for an empty status.
- Six of the seven saw the change to `manual.md`, restored its dirty bytes and wrote `docs/guide.ste.md`. The seventh (Sonnet) left `manual.md` changed and wrote no copy, which is the one registered fail.
- 7 of the 14 reps took the copy branch with no write through the link.

The registered verdict stands. The defect is in the wording of step 3. It lists the commands in one block and says "Run all three commands", but it does not say how to read a failed first command.

## 7. What the runs reach of item [34]

Item [34] names three review fixes. The runs reach one of them:

- The symbolic-link check in `references/document-rewrite.md`, step 3: reached by `doc-symlink`, which passes its registered checks. The second reading shows that the step's wording lets a rep write through the link first. So the owner left this part open and asked for a wording item (D11).
- The `python3` call in `references/agent-mode.md`: every agent rep opened `agent-mode.md`, but no agent rep had a shell, so none ran the linter through that line. The document reps ran the linter with `python3`, from step 4 of `references/document-rewrite.md`. Unreached.
- The kept "should" in `references/examples.md`: no rep's tool calls opened `examples.md`, so no run reached it. Unreached.

## 8. Costs, voids and advisor calls

```text
control agent: 30 reps, $1.51 (largest $0.07), 0 void
treatment agent: 30 reps, $1.50 (largest $0.08), 0 void
treatment docs: 40 counted reps, $3.29 (largest $0.19)
void V3 (D10): 4 doc-symlink reps, $0.63 (largest $0.23)
set aside (D8): 5 reps, $7.05 (largest $3.49)
probes: 4 reps, $0.15
judges: 16 calls, $0.63
total: $14.76 of $30.00
```

Apart from the 4 V3 reps, no rep was void. No rep could call the advisor. One set-aside rep's stream holds a harness turn ("Your response above was cut off mid-stream"), after an empty first answer. No counted rep has one.

## 9. Limits of this run

The owner chose to record these as limits, with no new items (D13):

- **The judges' strictness differed by arm.** Each arm's replies went to their own judge call. The control judge passed three replies on check 2 that name "the upstream job" as the producer. The treatment judge failed two replies for the same guess. A judge's pass stands under the registration, and D9 covers the one cell that this affects.
- **The hand reading was only partly blind.** The same session ran every rep, and `kit.py run` printed each rep id with its arm. The provisional control tally was read before the hand reading. `flags.tsv` has no arm field, and no treatment verdict depends on a `justified` reading.
- **V3 reads only the result's `permission_denials` for denials.** Plan 100's kit also read the tool results for guard and classifier denials. No counted stream holds a denial, so this run is not affected.
