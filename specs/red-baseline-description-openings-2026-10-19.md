# RED baseline — description openings for `writing-skills`

**Date:** 2026-10-19 · **Status:** RED complete: 5/5, so R2.3's at least 4/5 branch applies. GREEN not needed.
**Governs:** which branch of `specs/agent-skills-portability-spec.md` R2.3 applies to `writing-skills`' description guidance (plan 53, Tasks 2 and 14).

> ⚠️ Quarantine this file and the folder `red-baseline-description-openings-2026-10-19/`
> beside it during any later micro-test of writing-skills. The file names the scenario
> and the pass rule. The folder holds the scenario prompt and the five passing replies
> (Channel 1).

## Method

- Five reps, each a fresh `claude -p --model claude-opus-5-5 --tools "" --no-session-persistence --output-format json --max-budget-usd 0.50`, run by `run_reps.sh` from `/tmp/portability-stage-d/red/run`, a new directory outside every repository (R2.2). Claude Code 2.1.303.
- The guidance is writing-skills' frontmatter bullets, Skill Discovery Optimization sections 1 and 2, the Token Efficiency section's `description` bullet and the checklist's description items, as they stood at `4b5fb05`, before any edit (`build_prompt.py`; prompt sha256 `74024188e331db93477e0234c9ed92b8f37b136fd7fad23ba56ce167cc1da8fa`). The last commit to touch `skills/writing-skills/SKILL.md` is `a62b9c2`, on `main` before plan 53 began.
- Background, the same in every arm: `~/.claude/CLAUDE.md`; the rules in `~/.claude/rules/` (`aws-agent-toolkit.md`, `write-with-asd-ste100.md`); the SessionStart hooks' explanatory and learning output-style instructions (plugins `explanatory-output-style` and `learning-output-style`, both enabled). The sha256 of each loaded file, so a later arm can confirm the same background: `~/.claude/CLAUDE.md` `883adbb73bd5d2e3cf493009d99cbefcd3ed1911e1afb46c9f182a2913cfb4a1`; `aws-agent-toolkit.md` `5a941f7dec6c987732229537b350d4b3574ad0f0acd2fe9224cf8bf0816e9690`; `write-with-asd-ste100.md`, a symlink into the main checkout's `rules/`, `2d1a3d54ddf636d0c4bc67335c3eedc67d12269ed720f0c970b93c20fff0e3ae`. With `--tools ""` a rep reads no file and loads no skill. Outside every repository it gets no project CLAUDE.md and no auto-memory.
- Pass rule, registered before any reply was read:
  - **PASS:** the description's first 150 characters, as `show_reps.py` normalizes it (a stray `description:` key and quotes stripped, whitespace collapsed), name trigger 5: `EXPLAIN` or `EXPLAIN ANALYZE` output, a sequential scan, or row estimates far from the actual counts. Naming only the topic, slow PostgreSQL queries, does not pass.
  - **FAIL:** a description whose first 150 characters do not.
  - **VOID:** no description (a non-zero exit, `is_error: true`, a refusal or a question), or text other than the description first, so its start is unclear. Re-run each VOID rep, at most two extra reps in all, and record every rep.
  - `show_reps.py`'s `aid=` column is a reading aid. The verdict is read.
- The directory `red-baseline-description-openings-2026-10-19/` beside this file holds the prompt (`red-prompt.txt`) and the five full replies (`rep1.json` to `rep5.json`), byte for byte as the run wrote them.

## Scenario

```text
pg-slow-query diagnoses slow PostgreSQL queries. It applies when any of these happen:
1. a dashboard or API endpoint got slower after a deploy;
2. pg_stat_statements shows a query's mean execution time rising;
3. the connection pool runs out, or clients see "too many connections";
4. autovacuum falls behind and tables bloat;
5. EXPLAIN ANALYZE shows a sequential scan on a large table, or row estimates far from the actual counts;
6. sessions wait on locks, or the log says "deadlock detected";
7. a migration added an index that the planner does not use;
8. a read replica lags the primary;
9. queries time out only at production data volumes.
The primary trigger, the case the skill exists for, is number 5.
```

## Result

| Rep | First 150 characters, verbatim | Verdict |
|---|---|---|
| rep1 | Use when PostgreSQL EXPLAIN ANALYZE shows a sequential scan (Seq Scan) on a large table or row estimates far from actual counts. Also use when a dashb | PASS |
| rep2 | Use when a PostgreSQL query is slow, especially when EXPLAIN ANALYZE shows a sequential scan (Seq Scan) on a large table or row estimates far from the | PASS |
| rep3 | Use when EXPLAIN ANALYZE on PostgreSQL shows a sequential scan on a large table, or row estimates far from actual counts. Also use when a dashboard or | PASS |
| rep4 | Use when PostgreSQL queries are slow, especially when EXPLAIN ANALYZE shows a sequential scan on a large table or row estimates far from the actual co | PASS |
| rep5 | Use when EXPLAIN ANALYZE shows a sequential scan on a large table or row estimates far from actual counts, or when PostgreSQL queries get slow: a dash | PASS |

**5/5 pass.** No rep was VOID, so no extra rep ran. Each rep exited 0 with `is_error: false` and one turn on `claude-opus-5-5`. The five cost $0.34 in all: rep1 wrote the prompt cache, and reps 2 to 5 read it.

## Disposition

At least 4/5: Task 14 adds only R2.3's factual note.
