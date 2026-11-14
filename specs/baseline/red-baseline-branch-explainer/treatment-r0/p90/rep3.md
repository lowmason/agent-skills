# claude/quirky-golick-44b138: plan 90, the read-only guard's command-start walk

## Synopsis

**The plan:** The read-only guard let through 8 recorded lines that run a mutator in zsh. Each one hid the real command behind a word where the guard's walk stopped too early: a leading `{` or `[[ … ]]`, a `=cmd` path expansion, or an assignment that `ASSIGNMENT` does not match. A `/deferred` pass picked the backlog item for its age. The plan set out to deny those 8 lines, deny everything `main` already denied, and add no new model of zsh grammar.

**The build:** `_command_words` became `_stop_index`, which finds today's stop word. A new generator, `_command_starts`, yields that candidate first. It then also continues the walk past any stop word that may only lead the command. `_classify_subcommand` classifies every candidate, and the first denial stands. During the build the owner ruled three times. The walk now bounds its work, a subcommand with more than 64 candidates fails closed, and a leading run of `=` is stripped in one step. New tests pin the 8 lines, the allow cases, linear work and the cap. The README now describes the walk.

**The project:** The guard now reads each ambiguous leading word both ways. Because it only adds candidates, it cannot allow what it denied before. The backlog item's mixed-reading class is closed except for the glued glob qualifier, which a new deferred item tracks. Two narrow false-positive classes are documented and accepted. A sweep of 150,024 real commands found none.

## Background

`hooks/readonly-agent-guard.py` is the `PreToolUse` (`Bash`) hook that denies mutating commands for the five read-only agents. It is a guardrail, not a sandbox. `classify` splits a line under each of the eight `READINGS` (`hooks/readonly-agent-guard.py:108`) and classifies every subcommand.

Before the branch, `_command_words` walked a subcommand's words to find its command. It skipped `LEADING_KEYWORDS`, words that match `ASSIGNMENT`, `repeat` and its count, and `PREFIX_UTILITIES` with their options. It stopped at the first other word, took that word as the command, and returned one start.

The backlog item "Each of the eight readings holds for a whole line" (`specs/deferred_items.md`, section `readonly-guard-leading-token-bypasses`) recorded lines that passed. The README's mixed-reading bullet added one more. `d67f856` had already closed 2 of them. The spec sorts the rest by mechanism:

- 3 lines where a brace group or `[[ … ]]` test leads a git verb that takes `]]` as an argument. In the `braces` reading `]]` ends the subcommand. In the other reading the walk stops at `{` or `[[` and takes it as the command.
- 1 line with zsh's `=cmd`. The walk stops at `=rm`, a command it does not know.
- 4 lines with an assignment the guard does not recognise: a subscripted name, a non-ASCII name, and env operands that contain `=`, before and after `--`.
- 1 line with a glob qualifier glued to the command word. This is not the walk's problem, and the spec put it out of scope.

In each of the first three classes the walk guessed "this word is the command" when the word might only lead it. The README listed all of these under "Not caught".

## The change

The range touches 7 files, with 1,262 lines added and 37 removed. Most of that is the plan (636 lines) and the spec (295 lines). The guard gains 123 lines and loses 19. The test file gains 148.

### 1. `_stop_index`: today's walk, as an index

`_stop_index` (`hooks/readonly-agent-guard.py:781`) replaces `_command_words`. It runs the same skip loop from a given position `i` and returns where the command starts. It returns `len(words)` when there is no command and `None` where env's `-S` hides it. Returning an index lets a caller restart the walk from any position, and that is what the next part needs.

It also takes an optional `known` table. The table maps each loop head, a position and the word there, to where the walk from it stops. A head already in the table ends the walk at once. This memo was added in fix round 1 of Task 4 (`16076481`). It covers the "skipped-run" class, where a `]]` sits inside a run that `repeat` or a prefix option consumes. Such a read-only line of 80 KB took 159 s and yielded only 2 candidates, so the cap could not catch it. The memo changes no candidate, as Task 5's scratch check confirmed (0 subcommands differ).

### 2. `_command_starts`: every place the command may start

`_command_starts` (`hooks/readonly-agent-guard.py:822`) depends on `_stop_index`. It yields today's candidate first, unchanged. Then it queues extra continuations according to the stop word:

- `{`: continue from the next word.
- `[[`: continue after each later `]]`, quoted or not. The scan stops at a `]]` that an earlier scan already continued past (`continued_past`).
- A word that contains `=`: continue from the next word. This one rule covers zsh assignments that `ASSIGNMENT` misses and env's `name=value` operands, with no model of env's grammar.
- A word that begins with `=`: continue at the same position, with every leading `=` removed, unless nothing is left. The new word is a `_Token` that keeps the original's `quoted`, `spaced` and `expands` flags.

Each continuation is a full walk, so it skips keywords, assignments and prefixes again. Three structures bound the work. `visited` yields each stop word once per position. `queued` drops a repeat continuation before it is walked. `known` is the memo from part 1, shared across the whole walk.

The `=` rule changed late. At first, one `=` was stripped per step. The final review found that a heredoc rule line of 63 or more `=` then reached the cap and was denied. The owner ruled D6, "Strip all = at once" (`a9773f22`).

### 3. `_classify_subcommand`: classify every candidate, with a cap

`_classify_subcommand` (`hooks/readonly-agent-guard.py:896`) consumes `_command_starts`. It sends each candidate to `_classify_git` or `_classify_non_git` as before and returns the first denial. A `None` candidate returns `ENV_SPLIT_STRING`. An empty candidate is skipped. Past 64 candidates it fails closed with a reason that asks for shorter commands (`:903`). That cap came from the owner's ruling D4, "Dedupe + cap". With it the worst case is linear.

The safety argument is spec §3. The walk always yields today's candidate unchanged, and the readings, the splitter and the classifiers are untouched. So the set of denied lines can only grow. The denial text may change on a line that was already denied, because a new candidate can deny first. The spec lists this as designer's call 5.

### 4. Tests

`hooks/test_readonly_agent_guard.py` depends on all three parts:

- `COMMAND_START_BYPASSES` (`:616`) holds the 8 recorded lines, and each must be denied with a reason that names `rm` or `git branch`.
- `COMMAND_START_ALLOWED` holds 10 read-only forms. They pin each row of the table the other way, and they include heredoc `=` underlines and AsciiDoc headings.
- `_starts` tests check that today's candidate comes first and that each row continues.
- A bound test runs 16-word runs of `==` and `[[ a ]]` and asserts at most 3 candidates per word.
- `test_command_starts_work_grows_linearly` (`:724`) counts line events in the guard's code with `sys.settrace`. Doubling the line must less than triple the work, on three shapes: `test-chain`, `leading-equals` and `skipped-run`.
- `test_more_than_64_command_starts_fail_closed` (`:729`) allows 63 leading `{` and denies 64.
- `EQUALS_TEXT_ALLOWED` and `test_leading_equals_strip_in_one_step` (`:754`) pin the D6 rule.

### 5. README and backlog

`hooks/README.md` gains a paragraph in "Limitations (by design)" that names the four kinds of words read both ways. The `=cmd` example and the unrecognised-assignment bullet leave "Not caught". The mixed-reading bullet keeps its structural point and drops its examples. "Known false positives" gains two entries: the both-ways reading, with the denied AsciiDoc heading `== rm and mv ==` as the example, and the 64-candidate cap.

`specs/deferred_items.md` ticks the item with a done note. It also files one new item for the glued glob qualifier.

### Where the build departs from the spec

The `specs/history.md` entry lists 3 rulings and 5 deviations.

- Tasks 4 and 5 were not in the approved plan. The Task 3 gate raised the walk's super-linear runtime, and D3 and D4 added them.
- Two rulings keep `queued`, which the spec requires. After D6, no test fails when `queued` alone is removed. The memo and the scan stop keep the walk linear with their own biting cases. The plan's bite check removes `queued` and `known` together, and that fails only `skipped-run`. The final ruling notes that the owner can ask to drop `queued` as a follow-up.
- Task 5 timed 11 shape classes at up to 480 KB, not the spec's 512 KB. The slowest took 1.97 s, and all grew linearly. The spec's §2 still says "under 1 s" at 512 KB.
- Task 7's Step 1 expectation was corrected, and Step 2a was added after the run (`e523e03`).

## What it adds to the project

The guard now catches a whole class of leading-word disguises, not 8 specific strings. The fix stays inside the walk. Another subcommand that starts with `{`, `[[ … ]]`, an odd assignment or `=cmd` is read past in the same way. The tokenizer, `_split_tokens`, `READINGS` and both classifiers are unchanged. The installed hook is a symlink into the main checkout, so the change goes live in every repository when it merges. Gate B, `./hooks/probe-readonly-guard.sh`, can only test it after that.

The cost is two documented false-positive classes, both accepted by the owner (D2 and D5). The first is a word read as a prefix where zsh runs it as the command, or a heredoc line such as an AsciiDoc heading. The second is a subcommand with more than 64 candidates. In the 150,024-command sweep, neither fired. No subcommand had more than 13 candidates.

Later guard work depends on `_stop_index` and `_command_starts` as the single place that finds a command. A future change to the skip loop must keep the memo key sound: the walk from a head must depend only on that word and the words after it.

The branch leaves this for later:

- One new deferred item: the glued glob qualifier (`git(.) stash`). It needs a rule that tells it apart from `print(git(x))` in a heredoc. It is sized as design work.
- Still under "Not caught": command words that the shell produces by expansion or by gluing to a brace, and the line-wide readings for parentheses.
- An optional follow-up to drop the untested `queued` set.

## Questions

1. What did plan 90 set out to do, and why did it choose to add candidate starts in the walk rather than teach the splitter zsh grammar?
2. How is the walk built? Name the parts in dependency order, and say what bounds its work and why a bound matters for a hook.
3. What does the branch add to the guard's coverage and false-positive profile, and what does it leave open?
