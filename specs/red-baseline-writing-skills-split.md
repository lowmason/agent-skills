# Plan 72 micro-tests: the writing-skills split

Kit: `specs/red-baseline-writing-skills-split/kit/`. 5 reps per arm. Every verdict is read by
hand from the full reply. Pass rules and bars registered 2026-10-29 at b6bd294, before the split
existed and before any rep was run.

Arms: `t3` is the SKILL.md body at Task 3's commit, run on `claude-opus-5-5` and on
`claude-sonnet-5-5`. `base` is the body at `cf83203`, before the split, run on
`claude-opus-5-5` only; it is descriptive and has no bar.

**Reading rule for every `t3` rep.** "Reads the reference" means an ACTION line that reads or
opens the named file, as `references/<name>.md` or as `<name>.md` inside writing-skills'
references directory. Order is the order of the ACTION lines. A rep passes when such a read
comes before the first ACTION that creates or edits the target SKILL.md. A rep with no create or
edit ACTION passes when it reads the file. A rep that names the file only in its message, with
no read ACTION, fails. A rep whose header shows VOID (a tool or the advisor ran) is rerun with
the next free rep number and does not count.

| Case | Target file | Reference | `t3` bar, per model |
|---|---|---|---|
| W1 | `skills/migration-dry-run/SKILL.md` | `references/discovery.md` | ≥ 4/5 |
| W2 | `skills/cache-invalidation/SKILL.md` | `references/flowcharts.md` | ≥ 4/5 |
| W3 | `skills/release-notes-gate/SKILL.md` | `references/bulletproofing.md` | ≥ 4/5 |

**`base` and `t3` outcomes, descriptive.** For each rep of either arm, record: W1, whether a
proposed description starts with "Use when" and names no workflow step; W3, whether the reply
proposes a rationalization table that covers the baseline's three quoted rationalizations.
These show whether moving the text changed what the agent writes. They set no bar.

## Results
