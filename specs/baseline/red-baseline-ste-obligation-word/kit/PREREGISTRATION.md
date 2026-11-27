# Pre-registration: plan 114's obligation-word micro-test

These rules are fixed before the first scored rep. They come from `specs/plans/114-ste-drift-and-obligation-word.md`. `cases.py` and `kit.py` apply them. A change after the first scored rep needs the owner, and the record says what changed and when.

## Question

Does one added line in `skills/write-with-asd-ste100/SKILL.md`'s meaning rules keep the strength of an obligation word, such as "should", in agent-mode rewrites? Does the skill still meet its other checks? And does the document procedure send a tracked symbolic link to the copy branch?

## Arms and models

- `control`: `skills/write-with-asd-ste100/` and `rules/write-with-asd-ste100.md` at commit `4168d2a`, the text before plan 114.
- `treatment`: the same paths at the commit that adds the obligation line (plan 114, Task 4).
- Models: `claude-opus-5-5` and `claude-sonnet-5-5`, at the default effort. Every arm runs on both, with 5 good reps for each case.
- `kit.py freeze` copies each arm once, by `git archive`, and `runs/frozen.tsv` records the commit and the SHA-256 of `SKILL.md` and the rule.

## Setup of each rep

- Each rep is one `claude -p` call in its own `HOME`, `STE114_ROOT/<rep>` (default `/private/tmp/ste114/<rep>`), with its own `TMPDIR` inside it. The rep id is random and names no arm, case or model.
- The `HOME` holds the arm's rule as a user rule (`.claude/rules/write-with-asd-ste100.md`), the arm's skill folder (`skill/write-with-asd-ste100/`), a `Library/Keychains` link for the login, a placeholder `.gitconfig`, and nothing else. It has no `CLAUDE.md`, no settings file, no memory, no output style and no plugin.
- The skill reaches the rep as an appended system prompt: `Base directory for this skill: <dir>`, then `SKILL.md` without its frontmatter.
- The environment is explicit: `HOME`, `USER`, `LOGNAME`, `SHELL=/bin/zsh`, `LANG=en_US.UTF-8`, `TMPDIR`, `PATH=/usr/bin:/bin:/usr/sbin:/sbin`, `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1` and `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`. No other variable reaches the rep.
- Every rep has `--strict-mcp-config`, `--no-session-persistence`, `--output-format stream-json --verbose`, and `--settings` with a deny list (`Read`, `Edit` and `Write` of `//Users/**` and `~/Library/**`, and `ListAgents`, `SendMessage`, `PushNotification` and `RemoteTrigger`), the PreToolUse guard `guard.py --real-home <real home>` (copied from plan 100's kit), and `syncClaudeAiSkills: false`.
- An agent case runs with `--tools ""` from the empty folder `work/` in its `HOME`.
- A document case runs with `--tools Bash,Read,Edit,Write`, `--permission-mode auto` and `--add-dir <skill folder's parent>`, in a fixture repo at `work/repo/`.
- The raw stream and stderr go to `STE114_SCRATCH/raw/<rep>/`, outside the repository. The rep's `HOME` moves to `STE114_SCRATCH/homes/<rep>/` when the rep ends. The kit keeps `runs/reps/<rep>/stream.jsonl` without `origin`, `credential_expires_at`, `session_id` and `uuid`, and `post.json` (the fixture's state) for a document case.
- Nobody messages, subscribes to or opens a running rep.
- Before the first scored rep, `kit.py probe` runs one no-tool and one tool probe rep on `claude-sonnet-5-5`. Each lists the context it sees. Only the rule, the skill prompt and the planned tools may appear. Any other instruction file, memory, other session or the user's name is a leak, and it is fixed before any scored rep.

## Case set

| Case | Tools | Checks |
|---|---|---|
| `agent-tool-description` | none | 1 hedge, 2 no additions, 3 obligation; sentence cap 25 |
| `agent-error-message` | none | 1 hedge, 2 no additions, 3 obligation; sentence cap 25 |
| `agent-instruction` | none | 1 conditions and hedge, 2 no additions, 3 obligation; sentence cap 20 |
| `doc-clean` | `Bash,Read,Edit,Write` | the mechanical checks; judge 1: linter counts before and after |
| `doc-dirty` | `Bash,Read,Edit,Write` | the mechanical checks |
| `skill-md` | `Bash,Read,Edit,Write` | the mechanical checks; judge 1: the hand-off to writing-skills |
| `doc-symlink` | `Bash,Read,Edit,Write` | the mechanical checks |

The exact check texts are in `cases.py`. Every text except the obligation check and `doc-symlink` is ported unchanged from the 2026-10-18 kit.

## Checks

- **Obligation, judge.** Check 3 of each agent case: `Every obligation word keeps its strength. "should" stays "should" or "ought to". It does not become a bare command, "must", "shall", "always", "required" or "has to". The rewrite adds no obligation word that the source does not have.`
- **Obligation, mechanical.** `obligation_flags` scores the rewritten block only. That block is the reply up to the first line that starts the notes (`Kept as-is`, `Flag`, `Note`, `Ambiguity`, `Gap`, `Compound tense`, `Change`, `Caveat`, or a table row), with fence lines removed. It raises a flag when the block holds fewer `should` or `ought to` matches than the source, or when the block holds `must`, `shall`, `always`, `required`, `has to` or `have to` and the source does not.
- **Sentence cap, mechanical.** Ported: every sentence of the whole reply, after list marks and fence lines are removed, has the case's cap or fewer words.
- **Document checks, mechanical.** Ported `doc_checks` for `doc-clean`, `doc-dirty` and `skill-md`. For `doc-symlink`: `docs/guide.ste.md` is a regular file, `docs/guide.md` is still a link to `manual.md`, `docs/manual.md` keeps its dirty bytes, the repo has one commit, and `git status --porcelain` lists only ` M docs/manual.md` and `?? docs/guide.ste.md`. These checks are exact. They raise no flag and get no hand reading.

## Judges

- One `claude -p` call for each arm, case and model, on `claude-opus-5-5`, with `--tools ""`, `--json-schema` and `--max-budget-usd 2`, in a fresh empty `HOME`. It gets the ported `JUDGE_PROMPT`, the request, the numbered checks and the 5 good replies in a shuffled order under their rep ids.
- A judge's `fail` becomes a flag, `judge N`. A judge's `pass` stands.

## Void rules

- **V1.** No successful result record, or an empty reply.
- **V2.** A no-tool rep called a tool.
- **V3.** A tool rep had a tool call denied (the guard or the deny list).
- **V4.** The result's `result_index` is not the whole number 0, or any record has a non-null `origin`: a peer message reached the rep.
- **V5.** The init record lists a cross-session tool.

A void rep stays in the registry and never counts. `kit.py run` replaces it under a new rep id, up to 8 attempts for each arm, case and model. Past 8, stop and ask the owner. A void rep's cost still counts.

## Hand reading

`kit.py flags` writes `runs/flags.tsv`: every flag of every counted rep, shuffled, with an opaque flag id, the rep id, the case, the check, the detail and the context. It has no arm or model field.

The executing session reads every flag in full and writes a verdict, `count` or `justified`, and a one-line reason. It reads the flags of both arms together, after the treatment arm's agent runs and before it reads any tally line by arm. It does not open `runs/registry.tsv` or the judge files while it reads. An unread flag counts as a fail.

| Check | `justified` only when |
|---|---|
| `obligation` | the rewrite keeps the same strength in other words (for example "is expected to"), or the matched word is not an obligation in its context (for example "not always", which keeps the source's "sometimes"), or the matched text is a quotation of the source or literal text |
| `sentence cap` | the flagged text is not one sentence: a list that the splitter joined, code, a heading or a table row |
| `judge N` | the reply meets the check after all, and the judge erred. Give the reason |

## Decision rules

- **Pass.** A case passes on a model when at least 4 of its 5 good reps meet every check: every judge check passes or its flag is `justified`, every mechanical flag is `justified`, and every exact document check holds.
- **Control stop (plan 114, D4).** After the control arm's agent runs and judges, `kit.py tally control` gives a provisional count, with every unread flag a fail. If the control then passes the obligation check at 4 of 5 or better on both models, stop and ask the owner whether the line ships.
- **Item [33] is met** when all three agent cases pass in the treatment arm on both models.
- **Item [34] is met for the symbolic link** when `doc-symlink` passes in the treatment arm on both models.
- **A failing treatment case** gets one wording fix and a re-run of that case on both models. A second failure goes to the owner.

## Spend

- The cap is $30 for every rep, probe and judge call. `kit.py run` refuses a batch when the amount spent plus $1.00 for each rep in the batch passes the cap. It stops when one rep costs more than $3.00.
- `runs/spend.tsv` records the cost of each call.

## Run order

1. The no-model tests pass (`uv run --with pytest python -m pytest -q`).
2. Freeze `control`. Run both probes, and read them.
3. Commit this registration and the kit.
4. Control arm: the three agent cases on both models, then judges, then the provisional tally and the control stop.
5. Treatment arm: freeze it, run the three agent cases on both models, then judges.
6. `kit.py flags`, then the hand reading of every flag, then `kit.py tally`.
7. The four document cases in the treatment arm on both models, then judges, flags, hand reading and the tally.

## Amendment 1 (owner, plan 114 D8, 2026-11-27)

The control arm's first batch, `agent-tool-description` on `claude-opus-5-5`, stopped on the $3 alarm. With `--tools ""`, 4 of its 5 reps wrote tool calls as text, to open `references/agent-mode.md` and to run the linter. Two of them ran to the 128,000-token output limit, at $3.37 and $3.49. No void rule covered this. Asked, the owner chose "Give agent reps Read". From this amendment on:

- An agent case runs with `--tools Read`, `--permission-mode auto`, `--add-dir <skill folder's parent>`, the guard and the deny list, from the empty folder `work/` in its `HOME`. It has no fixture repo. It can open the skill's `references/`.
- V2 no longer applies to agent cases. V3 (a denied tool call) now applies to them.
- An agent case is scored on the result's text, the rep's final message, not on every message. The judges get the same text.
- The 5 reps of that first batch have the registry status `set aside (D8)`. They never count, and they are not attempts under the 8-attempt limit. Their $7.05 counts toward the cap.
- One `agent` probe rep on each model checks the new shape before the next scored rep.
- Every other rule above is unchanged, the control stop included.

## Amendment 2 (owner, plan 114 D10 and D12, 2026-11-27)

The final review found that V3 above kept only half of the plan's rule (Task 2, Step 7): "a tool rep that the guard denied or that reached a path outside its `HOME`". Asked, the owner chose "Plan's V3: void, re-run". From this amendment on:

- **V3** voids a tool rep whose tool input names an absolute path outside its own `HOME` (in its `/private/tmp` or `/tmp` form) and outside `/usr/`, `/bin/`, `/sbin/`, `/opt/homebrew/`, `/System/`, `/Library/` and `/dev/`, as well as a rep with a denied tool call. `kit.py revoid` applied it to every counted rep. It voided 4 `doc-symlink` reps, each of which wrote its own draft to the shared `/tmp`. `kit.py run` replaces them under the 8-attempt limit.
- **V1** also voids an agent rep whose final message is empty.
- **Judges.** A rep of a case with checks fails when its judge table is missing or incomplete. No hand reading clears that.
- **Scrub.** The kit also replaces the account name with `<user>` in every kept string (owner, D12). `kit.py revoid` re-scrubbed every kept stream.
- `runs/spend.tsv` takes one row at a time under a lock, so parallel reps lose no cost.
