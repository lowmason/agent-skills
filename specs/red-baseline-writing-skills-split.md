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

Run 2026-10-29. Prompts built with `kit/build_prompts.py`: `t3` at `7c09ef3` (body 18,003
characters) and `base` at `cf83203` (body 29,717 characters). Each case ran its three arms in
parallel: `t3` Opus, `t3` Sonnet and `base` Opus, 5 reps each. All 45 reps exited 0. No rep
was VOID: every header shows `turns=1`, no extra iterations and one model. No rep was rerun.

Spend is the sum of `total_cost_usd` over every `rep<N>.json`: **$3.39** for 45 reps, against
the $30 cap. The "Spend so far" column is a running total in this order: case (W1, W2, W3),
then arm (`t3` Opus, `t3` Sonnet, `base` Opus), then rep. So each case's totals include the
earlier cases' `base` reps.

**Every `t3` arm meets its bar: 5/5 on each case and each model.** No pointer was tightened.

| Case | `t3` Opus | `t3` Sonnet | Bar |
|---|---|---|---|
| W1 (`references/discovery.md`) | 5/5 | 5/5 | ≥ 4/5 |
| W2 (`references/flowcharts.md`) | 5/5 | 5/5 | ≥ 4/5 |
| W3 (`references/bulletproofing.md`) | 5/5 | 5/5 | ≥ 4/5 |

22 of the 30 passes come from the rule's no-edit clause: the rep read the reference and wrote
no create or edit ACTION. Only 8 reps tested the order of a read before a write: W1 Opus reps
1–5 and W3 Opus reps 1, 2 and 4.

The `claude -p` reps received some user-level context: "Insight" boxes appear in every reply of
both arms (45 of 45), and W1 Sonnet rep 2 quotes the owner's global notes back. So the kit does
not fully isolate the reps, and this may make the absolute `t3` bars easier to meet than a
clean run would. The kit fix is deferred.

### W1, `t3`, `claude-opus-5-5`

| Rep | Verdict | Deciding ACTION line | Spend so far |
|---|---|---|---|
| 1 | pass | ``ACTION: Read `~/.claude/skills/writing-skills/references/discovery.md` `` (1st ACTION). First create: ``ACTION: Create `skills/migration-dry-run/SKILL.md` with this text:`` (4th) | $0.16 |
| 2 | pass | ``ACTION: Read `~/.claude/skills/writing-skills/references/discovery.md`. SKILL.md requires this before I write frontmatter or the body.`` (1st). First create: 5th ACTION | $0.24 |
| 3 | pass | ``ACTION: Read `~/.claude/skills/writing-skills/references/discovery.md` `` (1st). First create: 5th ACTION | $0.32 |
| 4 | pass | ``ACTION: Read `~/.claude/skills/writing-skills/references/discovery.md`. SKILL.md says to read it before I write frontmatter or lay out the body.`` (1st). First create: 6th ACTION | $0.41 |
| 5 | pass | ``ACTION: Read `~/.claude/skills/writing-skills/references/discovery.md`. The skill says to read it before I write the frontmatter or the body.`` (1st). First create: 6th ACTION | $0.50 |

### W1, `t3`, `claude-sonnet-5-5`

| Rep | Verdict | Deciding ACTION line | Spend so far |
|---|---|---|---|
| 1 | pass | ``ACTION: Read `~/.claude/skills/writing-skills/references/discovery.md` `` (1st). No create or edit ACTION | $0.58 |
| 2 | pass | `ACTION: Read /Users/lowell/.claude/skills/writing-skills/references/discovery.md` (1st). No create or edit ACTION | $0.63 |
| 3 | pass | `ACTION: Read /Users/lowell/.claude/skills/writing-skills/references/discovery.md` (1st). No create or edit ACTION | $0.67 |
| 4 | pass | `ACTION: Read ~/.claude/skills/writing-skills/references/discovery.md` (1st). No create or edit ACTION | $0.72 |
| 5 | pass | ``ACTION: Read `/Users/lowell/.claude/skills/writing-skills/references/discovery.md` `` (1st). No create or edit ACTION | $0.76 |

`base` W1 reps 1–5 then ran ($0.69). Running total after W1: $1.46.

### W2, `t3`, `claude-opus-5-5`

| Rep | Verdict | Deciding ACTION line | Spend so far |
|---|---|---|---|
| 1 | pass | ``ACTION: Read `~/.claude/skills/writing-skills/references/flowcharts.md` `` (1st). No create or edit ACTION | $1.58 |
| 2 | pass | ``ACTION: Read `~/.claude/skills/writing-skills/references/flowcharts.md` `` (1st). No create or edit ACTION | $1.62 |
| 3 | pass | ``ACTION: Read `~/.claude/skills/writing-skills/references/flowcharts.md` `` (1st). No create or edit ACTION | $1.66 |
| 4 | pass | ``ACTION: Read `~/.claude/skills/writing-skills/references/flowcharts.md` `` (1st). No create or edit ACTION | $1.69 |
| 5 | pass | ``ACTION: Read `~/.claude/skills/writing-skills/references/flowcharts.md` `` (1st). No create or edit ACTION | $1.73 |

### W2, `t3`, `claude-sonnet-5-5`

| Rep | Verdict | Deciding ACTION line | Spend so far |
|---|---|---|---|
| 1 | pass | `ACTION: Read ~/.claude/skills/writing-skills/references/flowcharts.md` (1st). No create or edit ACTION | $1.80 |
| 2 | pass | ``ACTION: Read `~/.claude/skills/writing-skills/references/flowcharts.md` (required before I add a flowchart).`` (1st). No create or edit ACTION | $1.83 |
| 3 | pass | `ACTION: Read ~/.claude/skills/writing-skills/references/flowcharts.md` (1st). No create or edit ACTION | $1.85 |
| 4 | pass | ``ACTION: Read `~/.claude/skills/writing-skills/references/flowcharts.md` `` (1st). No create or edit ACTION | $1.88 |
| 5 | pass | ``ACTION: Read `~/.claude/skills/writing-skills/references/flowcharts.md` (the writing-skills skill requires this before I add a flowchart. …)`` (1st). No create or edit ACTION | $1.90 |

`base` W2 reps 1–5 then ran ($0.40). Running total after W2: $2.30.

### W3, `t3`, `claude-opus-5-5`

| Rep | Verdict | Deciding ACTION line | Spend so far |
|---|---|---|---|
| 1 | pass | ``ACTION: Read `~/.claude/skills/writing-skills/references/bulletproofing.md`. The skill tells me to read this file before I write counters for a rule that agents break under pressure.`` (1st). First edit: ``ACTION: Edit `skills/release-notes-gate/SKILL.md`. Replace the `description` field …`` (4th) | $2.47 |
| 2 | pass | ``ACTION: Read `~/.claude/skills/writing-skills/references/bulletproofing.md` `` (1st). First edit: 4th ACTION | $2.54 |
| 3 | pass | ``ACTION: Read `~/.claude/skills/writing-skills/references/bulletproofing.md` `` (1st). No create or edit ACTION | $2.59 |
| 4 | pass | ``ACTION: Read `~/.claude/skills/writing-skills/references/bulletproofing.md`. The writing-skills skill requires this before I write counters for a rule that agents break under pressure.`` (1st). First edit: 4th ACTION | $2.64 |
| 5 | pass | ``ACTION: Read `~/.claude/skills/writing-skills/references/bulletproofing.md` `` (1st). No create or edit ACTION | $2.67 |

### W3, `t3`, `claude-sonnet-5-5`

| Rep | Verdict | Deciding ACTION line | Spend so far |
|---|---|---|---|
| 1 | pass | ``ACTION: Read `~/.claude/skills/writing-skills/references/bulletproofing.md` `` (1st). No create or edit ACTION | $2.75 |
| 2 | pass | ``ACTION: Read `~/.claude/skills/writing-skills/references/bulletproofing.md` `` (3rd, after reads of the target and the baseline). No create or edit ACTION | $2.78 |
| 3 | pass | ``ACTION: Read `~/.claude/skills/writing-skills/references/bulletproofing.md` `` (1st). No create or edit ACTION | $2.82 |
| 4 | pass | ``ACTION: Read `~/.claude/skills/writing-skills/references/bulletproofing.md` (the writing-skills guide asks for this before I write counters).`` (3rd). No create or edit ACTION | $2.85 |
| 5 | pass | `ACTION: Read ~/.claude/skills/writing-skills/references/bulletproofing.md` (3rd). No create or edit ACTION | $2.90 |

`base` W3 reps 1–5 then ran ($0.50). Running total after W3: **$3.39**.

`base` W2, for the record: no `base` rep could read `flowcharts.md`, which did not exist at
`cf83203`. All 5 read `~/.claude/skills/writing-skills/graphviz-conventions.dot` instead.
Reps 4 and 5 also drafted the flowchart in an edit ACTION.

### Descriptive outcomes: W1 and W3, `base` and `t3`

Each cell has one of three values. "Yes" and "no" judge a draft. "No draft" means that the rep
wrote no description (W1) or drew no table (W3). It only read files and stated a plan.

W1 has two readings of "names no workflow step". The registered text does not settle which
one applies, and this table sets no bar.

- **Literal reading**, the registered words: a description names a step when its text names
  the dry run or any other step the skill prescribes.
- **Symptom reading**, added after the reps ran: a description that names the skipped dry run
  as a trigger ("when a dry run seems too slow") names a symptom, not a step.

Every description in both arms names applying the migration as its trigger. Both readings
below treat that as the trigger, not as a prescribed step. If applying also counted as a
step, every description in both arms would fail.

**W1: does a proposed description start with "Use when" and name no workflow step?** Each
description is quoted in full. The cell gives the literal verdict, then the symptom verdict.

| Rep | `base` Opus | `t3` Opus | `t3` Sonnet |
|---|---|---|---|
| 1 | literal yes, symptom yes: "Use when about to apply, run, or deploy a database schema or data migration to staging, production, or any shared database, including when the migration looks additive or small, the environment seems disposable, or there is time pressure to ship." | literal no, symptom yes: "Use when about to apply, run, or deploy a database migration to staging, production, or any shared database - including when the migration looks additive or trivial, when staging feels disposable, or when a dry run seems too slow to bother with." | no draft |
| 2 | literal no, symptom yes: "Use when about to apply a database migration to staging, production, or any other shared database, including when the migration looks additive or small, the environment looks disposable, or a dry run seems too slow for the task at hand." | literal no, symptom yes: "Use when applying, running or deploying a database migration to staging, production or any shared database, or when about to run a migrate, upgrade or apply command. Also use when the migration looks additive or safe, when staging seems disposable, or when a dry run feels too slow to bother with." | no draft |
| 3 | literal unclear, symptom yes: "checking" may mean the dry run. "Use when about to apply, run, or deploy database migrations or schema changes to staging, production, QA, preview, or any shared database - including when the migration looks additive or trivial, when staging seems disposable, or when a deadline makes checking feel slow." | literal no, symptom yes: "Use when about to apply, run, upgrade or deploy a database migration against staging, production or any shared database, or when tempted to skip a dry run because staging is disposable, the migration is only additive, or the dry run takes too long." | no draft |
| 4 | literal yes, symptom yes: "Use when about to apply, run, or deploy database schema migrations to staging, production, or any shared database, including when the migration looks small or additive, when staging feels disposable, or when under time pressure to ship." | literal no, symptom yes: "Use when about to apply, run, or deploy a database migration to staging, production, or any shared database - including when the migration looks additive or small, staging feels disposable, or a dry run seems too slow to bother with." | no draft |
| 5 | literal yes, symptom yes: "Use when applying, running, or deploying database schema or data migrations to staging, production, or any database you did not create for the current task, including when the migration looks additive, small, reversible, or urgent, or when staging seems disposable." | literal no, symptom yes: "Use when about to apply, run, or deploy a database migration to staging, production, or any shared database - including when the migration looks additive or small, when staging seems disposable, or when a dry run seems too slow to bother with." | no draft |
| Literal total | 4/5 yes if rep 3's "checking" is not the dry run, 3/5 if it is | 0/5 yes | 0 drafts |
| Symptom total | 5/5 yes | 5/5 yes | 0 drafts |

**W3: does the reply propose a rationalization table that covers the baseline's three quoted
rationalizations?**

| Rep | `base` Opus | `t3` Opus | `t3` Sonnet |
|---|---|---|---|
| 1 | yes: 4 rows, the 3 quotes plus one row that merges the deadline and ship-now ("The deadline / my manager says ship now") | yes: 5 rows, the 3 quotes plus ship-now and deadline | no draft (plans counters in prose) |
| 2 | yes: 4 rows, the 3 quotes plus ship-now | yes: 5 rows, the 3 quotes plus ship-now and deadline | no draft (plan names all 3 quotes as rows) |
| 3 | yes: 4 rows, the 3 quotes plus ship-now | no draft (plans a table in prose) | no draft (plan names 2 quotes) |
| 4 | yes: 3 rows, the 3 quotes | yes: 4 rows, the 3 quotes plus ship-now | no draft (plans a table in prose) |
| 5 | yes: 3 rows, the 3 quotes, plus a placeholder for other baseline rows | yes: 3 rows, in a "Rationalization \| Counter" table in the message | no draft (plans a table in prose) |
| Total | 5 yes | 4 yes, 1 no draft | 0 drafts |

On W1, every Opus description started with "Use when", but the step question splits by
reading: literal `base` 3 or 4 of 5 against `t3` 0 of 5, symptom 5 of 5 on both arms. On W3,
every drawn table covered the three quotes, and across both cases Opus drafted in 9 of 10
`t3` reps against 10 of 10 `base` reps, while `t3` Sonnet drafted in none and has no `base` arm to compare.
