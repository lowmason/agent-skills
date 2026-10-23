# Plan 67 probe: tune-hyperparameters' paired noise rule (V2)

**Date:** 2026-10-22. **Model:** `claude-sonnet-5-5` (from each rep's init record) through `claude -p` (Claude Code 2.1.304). **Kit:** `~/.cache/agent-skills/scratch/plan67-micro/` (`run_microtest.py`, `screen_v2.py`, `system-*.txt`, `results-*.json`, `log-*.txt`, `raw/`). **Cost:** $0.52 (pilot $0.03, control arm $0.29, variant arm $0.21).

## Design

Each rep is one `claude -p` call with no tools, run from its own new folder under `/tmp/p67micro/`. The isolation flags are `--model sonnet --tools "" --strict-mcp-config --no-session-persistence --system-prompt-file <skill>`, with `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1` set.

The system prompt is the whole tune-hyperparameters `SKILL.md`, after one line that tells the agent it has loaded the skill and follows it.

- **Control arm:** the `SKILL.md` at the base commit `7a8fbaa` (10,541 characters of system prompt). That text has no paired noise rule.
- **Variant arm:** the `SKILL.md` at HEAD after Task 2 (`ea78829`, 17,162 characters of system prompt). Its "When not to tune" list holds the rule: when |Δ|, the absolute mean of the per-fold differences d, is under 2·SE(Δ) = 2·sd(d)/√K over K folds, ship the default.

Each arm runs the two prompts below, 5 reps each, so 10 reps per arm.

**Isolation check.** A pilot rep (the V1 control listing, prompt `T1-grouped-cv`) ran first. Its init record showed `"tools": []` and `"mcp_servers": []`, so the kit's `clean` flag was True. The `usage.iterations` list was empty on every rep, so the kit's iteration clause passes without proof. A positive screen was used instead (`screen_v2.py`). For each rep, the result event must show only `claude-sonnet-5-5` in `modelUsage`, `num_turns` of 1 and zero server tool use. An advisor call would add a second model to `modelUsage`.

Some context still reaches every rep in both arms. Three user-level SessionStart hooks run, and the init record shows the "Explanatory" output style. The user's global `CLAUDE.md` and rules also load. The init record lists the user's skills, but with no tools the agent cannot load one. This context is the same in both arms and does not state a paired noise rule. So it does not change the contrast between the arms.

**Fixtures.** Per-fold differences d = default − tuned (lower MSE is better). The default's fold scores are the same in both prompts.

| Prompt | d | mean(d) | SE(Δ) | mean/SE | Default's fold sd |
|---|---|---|---|---|---|
| `V2-real` | 0.02, 0.06, 0.01, 0.08, 0.02 | 0.038 | 0.0136 | 2.80 | 0.233 |
| `V2-noise` | 0.04, −0.03, 0.05, 0.01, 0.03 | 0.020 | 0.0141 | 1.41 | 0.233 |

**Pass rule** (spec V2 and owner decision D3, fixed before the runs):

1. The variant answers `REAL` on `V2-real` in at least 4 of 5 reps (spec V2).
2. The variant answers `NOISE` on `V2-noise` in at least 4 of 5 reps.
3. Every rep is clean (`tools` and `mcp` empty, only `message` iterations). A rep that is not clean is void: rerun it and count it.

The control is expected to answer `NOISE` on `V2-real` (spec V2). Its count is recorded, but it is not a pass condition. If the control also answers `REAL` in 4 or more reps, the record says that the fixture did not separate the arms.

**Grading rule** (fixed before any answer was read). Each rep is graded on the first standalone `REAL` or `NOISE` token, in any case. A rep whose first line is not that token alone, after markup and punctuation are stripped, is flagged. If the reason contradicts the token, the token is graded and the contradiction is noted. A rep with neither token counts against the rule it serves.

## Prompts

Both prompts end with the same format line: "Reply with REAL or NOISE alone on the first line, then one sentence that gives the reason."

- **V2-real:** "I tuned the Ridge alpha of a monthly county employment nowcast with Optuna and 5-fold forward-chaining CV. Validation MSE for folds 1 to 5: the default alpha=1.0 scored 1.20, 0.85, 1.45, 0.95, 1.10. The tuned alpha=8.3 scored 1.18, 0.79, 1.44, 0.87, 1.08. Is the tuned alpha better, or is the difference noise, so that I should ship the default? Reply with REAL or NOISE alone on the first line, then one sentence that gives the reason."
- **V2-noise:** "I tuned the Ridge alpha of a monthly county employment nowcast with Optuna and 5-fold forward-chaining CV. Validation MSE for folds 1 to 5: the default alpha=1.0 scored 1.20, 0.85, 1.45, 0.95, 1.10. The tuned alpha=8.3 scored 1.16, 0.88, 1.40, 0.94, 1.07. Is the tuned alpha better, or is the difference noise, so that I should ship the default? Reply with REAL or NOISE alone on the first line, then one sentence that gives the reason."

## Results

| Prompt | Arm | REAL | NOISE | Rule | Held |
|---|---|---|---|---|---|
| V2-real | control | 4/5 | 1/5 | none (recorded only) | — |
| V2-real | variant | 5/5 | 0/5 | 1: REAL in at least 4 | yes |
| V2-noise | control | 0/5 | 5/5 | none (recorded only) | — |
| V2-noise | variant | 0/5 | 5/5 | 2: NOISE in at least 4 | yes |

Rule 3 held. All 20 reps passed the isolation screen, and there were 0 voids in each arm. Every first line was the bare token, so no rep was flagged. No reason contradicted its token.

**The `V2-real` fixture did not separate the arms.** The control answered `REAL` in 4 of 5 reps, not the expected `NOISE`. The control reasons argue from the paired comparison: the tuned alpha wins all 5 folds, and the fold difficulty cancels. The variant reasons all apply the rule as written: each computes 2·SE(Δ) (0.027 on `V2-real`, 0.028 on `V2-noise`) and compares the mean difference with it.

## Per rep

Each answer was graded by hand. The first line is quoted whole. The reason quote is at most 15 words.

| Arm | Prompt | Rep | First line | Reason (excerpt) |
|---|---|---|---|---|
| control | V2-real | 1 | `REAL` | "the tuned alpha won all 5 folds, by 0.01 to 0.08 (mean 0.038)" |
| control | V2-real | 2 | `REAL` | "the fold-to-fold spread cancels, and the tuned alpha won every fold" |
| control | V2-real | 3 | `REAL` | "The tuned alpha wins on all 5 folds by 0.01 to 0.08" |
| control | V2-real | 4 | `REAL` | "mean gain 0.038, paired t about 2.8" |
| control | V2-real | 5 | `NOISE` | "The 0.04 average gain is tiny against the 0.60 fold-to-fold spread" |
| control | V2-noise | 1 | `NOISE` | "lowers mean MSE by only 0.02 (1.09 versus 1.11)" |
| control | V2-noise | 2 | `NOISE` | "the paired fold difference is just 1.4 standard errors" |
| control | V2-noise | 3 | `NOISE` | "far smaller than the fold-to-fold spread (0.85 to 1.45)" |
| control | V2-noise | 4 | `NOISE` | "the fold spread swamps the gap" |
| control | V2-noise | 5 | `NOISE` | "the paired gain has t of about 1.4, and fold 2 got worse" |
| variant | V2-real | 1 | `REAL` | "which is above 2·SE(Δ) = 2 × 0.0136 = 0.027" |
| variant | V2-real | 2 | `REAL` | "0.038 on average, which is above 2·SE of 0.027" |
| variant | V2-real | 3 | `REAL` | "The mean paired MSE gain is 0.038, above 2·SE = 0.027" |
| variant | V2-real | 4 | `REAL` | "The mean paired MSE drop of 0.038 is larger than 2·SE" |
| variant | V2-real | 5 | `REAL` | "0.038, which is above 2·SE = 0.027 (sd 0.030 over 5 folds)" |
| variant | V2-noise | 1 | `NOISE` | "0.020, which is under 2·SE = 0.028" |
| variant | V2-noise | 2 | `NOISE` | "under 2·SE = 2 × 0.0316/√5 ≈ 0.028 over 5 folds" |
| variant | V2-noise | 3 | `NOISE` | "0.020 in favor of the tuned alpha, which is below 2·SE = 0.028" |
| variant | V2-noise | 4 | `NOISE` | "0.020 MSE, which is under 2·SE = 0.028" |
| variant | V2-noise | 5 | `NOISE` | "The mean paired difference is 0.020, which is below 2·SE = 0.028" |

## Verdict

Pass. The variant met all three rules on its first run, so no rewording was needed and the variant arm ran once.

Two facts limit what this test shows:

1. **The real fixture did not separate the arms.** Without the rule, the control already called the 2.8-SE fixture real in 4 of 5 reps. So the test shows that the rule gives the right call on both fixtures and that the agent applies the 2·SE(Δ) arithmetic. It does not show that the rule turns a wrong `NOISE` call on a real gain into a right one.
2. **The noise fixture did not separate the arms either.** The control called the 1.4-SE fixture noise in 5 of 5 reps, mostly from the fold spread. The rule changed the reason (a paired 2·SE test in every variant rep), not the call.
