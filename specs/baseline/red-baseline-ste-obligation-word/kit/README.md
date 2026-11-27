# Plan 114 kit: the obligation-word micro-test

This kit tests one added line in `skills/write-with-asd-ste100/SKILL.md`'s meaning rules, which keeps the strength of an obligation word such as "should". It also runs the skill's four document cases, `doc-symlink` among them. Plan 114 (`specs/plans/114-ste-drift-and-obligation-word.md`, retired later to `specs/plans/completed/`) builds it. `PREREGISTRATION.md` holds the rules, and `specs/baseline/red-baseline-ste-obligation-word.md` holds the record.

- `cases.py`: the seven cases and the mechanical checks. The texts it shares with the 2026-10-18 kit are ported unchanged.
- `kit.py`: freeze, run, probe, judge, flags and tally. Its docstring gives the commands.
- `guard.py`: plan 100's PreToolUse guard, copied unchanged from `specs/baseline/red-baseline-handoff-rerun/kit/guard.py`.
- `test_checks.py` and `test_kit.py`: no-model tests, with a stub `claude`.
- `runs/`: the registry, the spend, the frozen hashes, the probes, the scrubbed reps, the judge verdicts and the flag sheet.

The agent sources are the **Before** texts of Examples A to C in danyuchn/asd-ste100-skill's `examples/before-after.md`, at commit `3944283c` (MIT, Copyright (c) 2026 Dustin Yuchen Teng). `NOTICE` names them as test cases of the skill's test record.

The kit differs from the 2026-10-18 kit in its isolation. Each rep has its own `HOME`, so it sees no user instruction file, output style, plugin, memory or other session. The rule reaches the rep as a user rule in that `HOME`, not as a project rule. So the results do not compare one to one with the 2026-10-18 arms, and the control arm here is the comparison.

Environment overrides, for the tests: `STE114_ROOT`, `STE114_SCRATCH`, `STE114_RUNS`, `STE114_CLAUDE` and `STE114_REAL_HOME`.
