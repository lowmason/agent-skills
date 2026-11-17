# RED baseline and micro-test: the cc-guide stamp-line clause (2026-11-17)

## Why

On 2026-11-17 the owner ruled that a not-covered row on a file's own `cc-guide:` citation line is always none (a class ruling). Earlier rounds ruled such rows none one file at a time ("P8"). The owner chose to record the ruling as one clause in the files mode of `.claude/skills/cc-guide/SKILL.md`, step 3, and to micro-test the clause first. The writing-skills skill requires a micro-test for wording that shapes behaviour.

The clause under test, appended to files step 3:

> A not-covered row on the line of the file's own `cc-guide:` comment is ruled none (owner class ruling, 2026-11-17), so it holds nothing.

## Design (pre-registered before any rep)

- Kit: `red-baseline-cc-guide-stamp-line/kit/`. `run_reps.sh`, `show_reps.py`, `probe.sh` and `isolation_probe.txt` are copied from the report-source-match kit. `cases.py`, `build_prompts.py` and `grade.py` are new.
- Each rep is a decision-only `claude -p --model sonnet` run with no tools, under `env -i`, `--setting-sources ""`, `--strict-mcp-config`, `--disable-slash-commands`, no advisor and no auto-memory, from a new directory under `/tmp`.
- Fixture: a frozen `/cc-guide files` session on two invented files. Both settles exit 0 with no contradiction, and the partner has ruled on no row.
  - File A, `commands/release-notes.md`: its one not-covered row is line 4, its own `# cc-guide:` comment.
  - File B, `agents/style-checker.md`: a not-covered row on line 6, its own comment, and a real not-covered row on line 15.
- Arms, 5 reps each:
  - Control: the skill body at `HEAD` (no clause).
  - Treatment: the working-tree body with the clause.
- Grading (`grade.py`, ACTION lines only, and every reply read by hand): per file, CITE when an action runs `baseline cite <file>`, HOLD when one runs settle with `--hold <file>` and none cites it, NONE otherwise.
- Bars:
  - RED: the control gives A = HOLD or NONE in at least 4 of 5 reps. If it gives A = CITE in 4 or more, the clause adds nothing: stop and leave the skill unchanged.
  - GREEN: the treatment gives A = CITE and B = HOLD in 5 of 5. Any B = CITE is over-application and fails the clause.
- VOID: `show_reps.py`'s rules (an error, more than one turn, a non-message iteration or a second model). A VOID rep is re-run.
- Before the reps, `probe.sh` runs `isolation_probe.txt` once. All six lines must answer NO.

## Results (2026-11-17)

- Isolation probe: all six lines NO. The init record showed no tools, no skills, no slash commands and the default output style. `claude -p` reached Claude Code 2.1.323 on PATH. Cost $0.008.
- Control (`HEAD`, body sha256 `a5f6bb5d…`, 10,890 chars): A = HOLD 5/5, B = HOLD 5/5. Every rep re-settled both files with `--hold` and asked the owner to rule on the stamp-line rows. RED bar met: the failure exists. Cost $0.098.
- Treatment (working tree, body sha256 `e5717bc9…`, 11,027 chars, the clause the only diff): A = CITE 5/5, B = HOLD 5/5. Every rep named A's line-4 row as ruled none and cited A. Every rep named B's line-6 row as ruled none, held B on its line-15 row and asked the owner about that row only. GREEN bar met, with no over-application. Cost $0.110.
- No rep was VOID. I read all ten replies by hand, and they agree with `grade.py`.
- Total cost $0.216 for 11 calls.

Limits: the reps ran on Sonnet, while a `/cc-guide` session usually runs on the session model. The fixture has one decoy only (a stamp-line row next to a real row), not a row on a nearby line or a row that quotes the stamp.

Raw outputs (prompts, manifests, rep JSON) are outside the repo in `~/.cache/agent-skills/scratch/cc-guide-stamp-line-micro/`.
