# Read-only guard: every place a command can start — Design Spec

**Status:** APPROVED (2026-11-11). The owner approved this file, its designer's calls included, on 2026-11-11.
The question was "Do you approve the spec, with its designer's calls?", and the owner answered "Approve it". The
next step is a plan from the writing-plans skill.

**Amended 2026-11-11** by the owner's rulings D3 and D4 in `specs/plans/90-readonly-guard-command-starts.md`,
made during execution: the walk bounds its work as well as its candidates, and a subcommand with more than 64
candidates fails closed (Design §1, §2, §4 and §5, each marked "Amendment"). The owner's ruling D6 then changed the
last row of Design §1's table: a word that begins with `=` loses every leading `=` in one step.

This spec answers the backlog item that begins "Each of the eight readings holds for a whole line"
(`specs/deferred_items.md`, section `readonly-guard-leading-token-bypasses`, its third item, called "the item"
below). The design came from a brainstorming session on 2026-11-11. Text marked *(designer's call)* is the
designer's choice, and "Designer's calls" lists each one. Line numbers are as of `d79b1fb`, the `main` commit
this design read.

> **For agentic workers:** plan from this file with the writing-plans skill. Keep bypass constructions out of
> chat: report them by class and count, and keep the detail in files (Constraints, "Chat hygiene").

## Intent

`hooks/readonly-agent-guard.py` is a `PreToolUse` (`Bash`) hook. It denies mutating commands for the five
read-only agents. It is a guardrail against an agent drifting off contract, not a sandbox
(`hooks/README.md`, "Limitations (by design)").

The item records 10 lines that run a mutator in zsh but pass the guard. The mixed-reading bullet under "Not
caught" in `hooks/README.md` adds an 11th, a third brace-or-test line. The getopt fix (`d67f856`) closed 2 of the
11, and `PREFIX_OPTION_BYPASSES` in `hooks/test_readonly_agent_guard.py` pins both. The other 9 still pass on
`d79b1fb`. The item's lines were all allowed on `db5d222` too, so the owner deferred them under the
no-worse-than-main merge bar.

**Why now.** No failure was seen, and neither of the item's "Revisit if" triggers has fired. A `/deferred` pass
picked the item because it was old. So this design is the smallest coherent change that meets the item's
"Done when", and it adds no new claim about zsh grammar.

### One seam: where the walk finds the command word

`_command_words` (`hooks/readonly-agent-guard.py:781-802`) walks a subcommand's words to find its command. It
skips `LEADING_KEYWORDS`, words that match `ASSIGNMENT`, `repeat` and its count, and `PREFIX_UTILITIES` with
their options (`_skip_prefix_utility`, `:759-778`). It stops at the first other word and takes it as the
command. It returns one start position.

Each of the recorded lines hides its mutator behind a word where the walk stops too early. That word might lead
the command, or it might be the command. The walk always guesses "the command". By mechanism:

| Class | Lines | Where the walk stops |
|---|---|---|
| A brace group or a `[[ … ]]` test leads the subcommand, and a git verb after it takes `]]` as an argument | 3 | In the `braces` reading, `]]` ends the subcommand and hides the argument. In the other reading, the walk stops at `{` or `[[` and takes it as the command. |
| zsh's `=cmd` path expansion | 1 | zsh replaces `=name` with the path of `name`. The walk stops at `=name`, a command it does not know. |
| An assignment the guard does not recognize | 4 | zsh's subscripted and non-ASCII names, and env operands that contain `=` but are not shell identifiers, before and after `--`. `ASSIGNMENT` does not match them, so the walk stops there. |
| A glob qualifier glued to the command word | 1 | Not this seam. See Non-goals. |

## Goals, non-goals and anti-goals

**Goals**

1. Deny the 8 recorded lines in the first three classes.
2. Deny everything `d79b1fb` denies.
3. Keep allowing the item's must-pass list (`git log --format='%(refname)'`, `*(.)`, `(#i)readme*`, and the
   read-only file-descriptor and process-substitution forms) and every allow case in the test suite.
4. Make `hooks/README.md` describe the new walk truthfully.

**Non-goals**

- **The glued glob qualifier** *(designer's call)*. The Bash tool turns `BARE_GLOB_QUAL` off, so the line does not
  run there. The item's sketched fix, to keep the command word when a group touches it, would also deny lines that
  the README promises to pass. One is a heredoc line `print(git(x))`. `_group_word` (`:473-492`) passes it today
  because it puts one `()` in place of the word glued to the group. The bullet stays under "Not caught".
- **The item's other fix sketches.** The 8 lines need neither the `spaced` rule for parentheses nor readings
  chosen per token. The `nest` and `braces` choices stay line-wide, as today.
- **Other command words that the shell produces.** A brace glued to the command word, brace expansion,
  `$c x` and the like stay under "Not caught".
- **Programs run through git configuration.** That is a separate backlog item.
- **Changes outside the walk.** The tokenizer, `_split_tokens`, `READINGS` and the git and non-git classifiers
  do not change.

**Anti-goals**

- Any change that can turn a denial on `d79b1fb` into an allow. That includes removing a reading or a candidate
  start.
- New false positives on commands that the guarded agents really run.

## Approaches

1. **Look for the command at every plausible start (chosen).** Only the walk changes. Where it stops at a word
   that might lead the command, it also continues past that word, and a denial at any start stands. It closes
   the 8 lines. Because it only adds start positions, it denies everything `d79b1fb` denies.
2. **Teach the splitter where a command can start.** `_split_tokens` would treat `{` and `]]` as syntax only at
   command position, and the `braces` reading would go away (8 readings would become 4). It would also stop false
   positives such as `echo { rm x`. But it is a new model of zsh grammar, which is where earlier review rounds kept
   finding holes. It removes a reading, so it can allow what `d79b1fb` denied. Showing that it does not would need
   the lost corpus sweep and differential fuzz rebuilt.
3. **Read each ambiguous token both ways on its own.** Each `{`, `]]` and parenthesis would get its own choice in
   place of the line-wide one. This closes the whole mixed-reading class, parentheses included. But the readings
   double with each ambiguous token. A long heredoc line with many parentheses would need a cap, and the guard
   would deny every line above it.

## Owner decisions (2026-11-11)

- **D1 — Approach 1.** The question was "Which approach should the design use?", and the owner answered
  "Approach 1".
- **Why now.** The owner said a `/deferred` pass suggested the item for its age. This sets the scope (Intent).
- **Amendment (execution).** Task 3 of plan 90 measured the built walk on long crafted lines. The question was
  "How should the guard's quadratic slowdown on long crafted lines be handled?", and the owner answered "Fix it
  now" (plan 90 D3). The question "Should the fix also deny a subcommand with more than 64 candidate starts?"
  followed, and the owner answered "Dedupe + cap" (plan 90 D4). The final review found that the cap denied a
  heredoc line made of a long run of `=`. The question "Which rule should the guard use for a word that starts
  with `=`?" followed, and the owner answered "Strip all = at once" (plan 90 D6).

## Design

### 1. The walk yields every candidate start

The walk follows today's path: it skips what `_command_words` skips, in the same way. At the word where today's
walk stops (the *stop word*), it first yields today's candidate, the words from the stop word on. Then it also
continues the walk from each extra place in this table:

| The stop word | The walk also continues from |
|---|---|
| is `{` | the word after it |
| is `[[` | the word after each later `]]` in the subcommand, quoted or not |
| contains `=` | the word after it (a possible assignment, to the shell or to env) |
| begins with `=` | the same position, with every leading `=` removed from the stop word, unless nothing is left *(amended, D6)* |

A continued walk is the whole walk. It skips keywords, assignments and prefix utilities again, and its own stop
word can add more places. Each extra place either starts at a later word or shortens the stop word, so the walk
ends.

**The walk must stay bounded.** Without a guard, the rows can reach one state by many paths, and the work grows
exponentially. A stop word made only of `=` reaches the next word through two rows, so a run of such words doubles
the work at each word. A chain of `[[ … ]]` tests in one subcommand grows the same way. A hook that times out lets
the call go on (`specs/guides/claude-code-customization-guide.md:381`), so a slow walk fails open. The walk visits
each state once: a visited set keyed on the word position and the stop word's text does it, and it changes
nothing that is denied *(designer's call)*. A test pins the bound with a long command full of these words. It
counts the states or candidates the walk visits and asserts a small multiple of the word count, not a time limit,
because a timing assertion is unreliable across the two interpreters.

**Amendment D6: every leading `=` goes in one step.** The table's last row first removed one `=`, and the shorter
word went through the table again. So a word of n `=` gave about n candidates, and one rule line of 63 or more `=`
in a heredoc reached the cap in Design §2 and was denied. zsh's `=cmd` reads one `=`, and a word that still begins
with `=` never names a command that the guard denies, so the words in between add no denial. The row now removes
every leading `=` at once, and a word made only of `=` has no such continuation. Its `=` row still continues past
it. In the false-positive sweep's corpus, this changes no denial.

**Amendment: the walk also bounds its work.** The visited set bounds the candidates, not the work. A continuation
still walks to its stop word before the set drops it, and the `[[` row scans every later word for each `[[`. On a
long chain of tests, or on a word with many leading `=` before a long run of words that the walk skips, the work
grew with the square of the line. Such a line of 20 to 32 KB took about 20 s on `/usr/bin/python3`. So the walk
bounds its work in three ways:

- **A continuation is queued once.** A second set, keyed on the continuation's start position and the word there,
  drops a repeat before it is walked. A continuation's words differ from the subcommand's only at or before its
  start, so that key settles the rest of its walk, and the set changes no candidate.
- **The `[[` row stops its scan at the first `]]` that an earlier scan continued past.** That scan already queued
  every later `]]`.
- **The walk remembers where each loop head stops.** A `]]` that `repeat` or a prefix utility's option consumes
  lies inside a run of words that the walk skips, and each continuation after one walked the rest of the run
  again. Such a read-only line of 80 KB took 159 s and yielded only 2 candidates, so the cap did not reach it. The
  result of a walk from a word depends only on that word and the words after it, so a table keyed on the position
  and the word settles each head once. This part was added during execution, after the first implementation's
  report found the class.

A second test counts the walk's work as line events in the guard's code. It asserts that the work doubles, not
quadruples, when the line doubles. The cap in Design §2 then makes the worst case linear.

The `=` rows cover env as well. env takes every operand that contains `=` as an assignment, up to its command.
The rule "continue past any stop word that contains `=`" needs no claim about env's grammar, and it covers the
operands after `--` too *(designer's call)*. A branch that reaches env's `-S` denies with `ENV_SPLIT_STRING`, as
today. A branch that reaches `command -v` or `-V` ends with no command, as today.

The `[[` row takes each later `]]`, not only the first unquoted one *(designer's call)*. zsh ends the test at the
first unquoted `]]`, so "each" covers that end and adds only denials.

### 2. Classifying the candidates

`_classify_subcommand` (`:805-814`) classifies each candidate as it classifies the one candidate today: `git` goes
to `_classify_git`, and anything else to `_classify_non_git`. It returns the first denial. Today's candidate comes
first.

The denial text can change on a line that `d79b1fb` already denies *(designer's call)*. `classify` returns the
first denial it finds, by line, then reading, then subcommand. So a new candidate in an earlier subcommand or
reading can deny before today's denial is reached. The line is still denied, and the new text names a real
mutator. Keeping the old text would need a second pass in `classify`, outside the walk, for no change in what is
denied.

**Amendment: the cap.** `_classify_subcommand` denies a subcommand whose walk yields more than 64 candidates when
none of the first 64 denies. The guard then fails closed, as it does for env's `-S`, and the reason asks for
shorter commands. In the false-positive sweep's corpus of 150,024 commands, the most candidates in one subcommand
was 13. With the cap, a crafted line of 512 KB is classified in under 1 s. The limit stays inside
`_classify_subcommand`, not in a new module constant.

### 3. Why this cannot allow what `d79b1fb` denies

The walk always yields today's candidate unchanged. The readings, the split and the classifiers do not change.
`classify` (`:817-841`) denies when any candidate in any reading denies. So the set of denied commands can only
grow. The amendment keeps this: the work bound changes no candidate, and the cap only adds denials. The argument holds only if the walk really does yield today's candidate unchanged, so Verification checks it
on real commands as well.

### 4. `hooks/README.md`

- **Limitations (by design).** The paragraph that describes the walk gains one point. Where the walk cannot tell
  whether a word leads the command (a leading `{` or `[[ … ]]`, a word that contains `=`, or a leading `=`), it
  reads the word both ways, and a denial either way stands.
- **Not caught.** Remove the `=cmd` example from the bullet on command words that the shell produces. Remove the
  bullet on assignments the guard does not recognize. In the mixed-reading bullet, remove the three examples and
  keep the structural point: the readings still apply to the whole line, and the walk now covers a brace group or
  test that leads a subcommand. Keep the glued-qualifier bullet.
- **Known false positives.** Add one: a word at the start of a command that contains `=`, begins with `=`, or is
  `{` or `[[`, is read both as a prefix and as the command. So the word after it is classified too, even where zsh
  runs the first word as the command.
- **Known false positives (amendment).** Add one more: a subcommand with more than 64 places where its command
  may start is denied, because the walk would be slow and a slow hook fails open.

The exact wording is the builder's.

### 5. Tests

In `hooks/test_readonly_agent_guard.py`:

- A parametrized list of the 8 recorded lines, each denied. Copy 7 from the item text and the third
  brace-or-test line from the README's mixed-reading bullet. Add no other bypass constructions.
- For each row of the table in Design §1, one allow case with a read-only command in the same position: for
  example, a subscripted assignment before `git log`. Each rule is then pinned both ways.
- The bound test from Design §1.
- The work test from Design §1 (amendment). It must fail when either part of the work bound is undone.
- A test that a subcommand with 64 candidates is allowed, and that one with 65 is denied with the cap's reason
  (amendment).
- Allow cases for text lines of `=` words in a heredoc (a long rule, a table border, a long `=` prefix on a word),
  and a test that a word with many leading `=` adds one candidate (amendment, D6).
- Every existing test passes unchanged. If one asserts a denial text that Design §2 changes, report it as a
  deviation rather than editing the test silently.

## Verification

1. **RED first.** Run the 8 new deny cases against `d79b1fb`'s guard. All 8 must fail. Reconcile the count by
   running them, not from a report.
2. **Suite.** Run `uv run python build/run_suites.py hooks`. It runs the hooks suite under the dev Python and under
   `/usr/bin/python3` (the 3.9 floor).
3. **No denial lost.** Run `d79b1fb`'s guard (`git show d79b1fb:hooks/readonly-agent-guard.py`) and the new guard
   over every command string in the test file, every command in `hooks/README.md`, and the transcript corpus
   (step 4). No command may go from denied to allowed. This is a one-off check, not a committed test.
4. **False-positive sweep.** Build a corpus of the Bash commands in local transcripts
   (`~/.claude/projects/*/*.jsonl` and their subagent transcripts). List each command that the new guard denies and
   `d79b1fb` allows. Report the count and the classes to the owner at the review gate. The owner accepts each one
   or asks for a narrower rule.
5. **Commit lints.** Run `build/run_commit_lints.sh`. Both edited files carry a cc-guide citation, so its
   `cc_guide_lint` step applies. Its `check_conformance` step covers `hooks/*.py` and `hooks/README.md`.
6. **Gate B after merge.** The installed guard is a symlink into the main checkout, so
   `./hooks/probe-readonly-guard.sh` tests the change only after it merges there.
7. **Review.** Codex is the only seat that hunts bypasses. CLAUDE.md records the owner's approval of Codex reviews
   for this repository. Brief the code-reviewer and task-reviewer for plan conformance and code quality only. Both
   are guarded agents, and a guarded agent probing its own guard tripped a safety classifier before. Run one Codex
   round. If it finds mutating lines outside the recorded set, report them by class and severity, with a pointer to
   its review file. The owner then picks: fix, record or stop. Do not start another round by default.

## Constraints

- **The 3.9 floor.** The guard stays stdlib only and 3.9-compatible: no `match`, and it keeps
  `from __future__ import annotations` (module docstring, `:15-17`).
- **Live on merge.** `~/.claude/hooks/readonly-agent-guard.py` is a symlink into the main checkout. The change
  goes live in every repository once it merges there.
- **Chat hygiene.** Report bypass findings by class and count. Keep the constructions in files: the Codex review
  file under `/tmp/codex-review/` and the sweep output.
- **A public repository.** The transcript corpus and the sweep output hold other repositories' commands. Keep them
  in `~/.cache/agent-skills/scratch/`, and never commit them.

## Closing the backlog

- This spec's commit writes `→ planned 2026-11-11: specs/readonly-guard-command-starts.md` on the item.
- At plan completion, the plan-completion protocol (writing-plans § Plan Completion Protocol) ticks the item. The
  tick note records the 8 lines closed, the 2 that `d67f856` closed earlier, and the glued qualifier left under
  "Not caught" by this spec's approval.

## Designer's calls

1. **Scope.** The item's "Done when", less the glued qualifier, with no new zsh grammar. This follows from the
   owner's answer on why now.
2. **The glued qualifier is out** (Non-goals).
3. **One `=` rule covers env**, in place of a model of env's operand grammar (Design §1).
4. **Each later `]]`**, not only the first unquoted one (Design §1).
5. **Denial text may change on lines `d79b1fb` already denies.** The change stays inside the walk, and every such
   line is still denied (Design §2).
6. **Size.** A project: this spec, then a plan in a fresh session. A `/deferred` Design pick routes to a spec, and
   most of the work is verification.
7. **False positives go to the owner** at the review gate, not accepted by the builder (Verification 4).
8. **Gate B after merge** (Verification 6).
9. **A visited set bounds the walk**, because a slow hook fails open (Design §1).

## Left to the builder

- The walk's name and shape (a generator or a list), and how `_command_words`' callers adapt.
- The names and placement of the new test lists.
- The README wording.
- How the transcript corpus is built: which transcripts, how commands are pulled out, and deduplication.
