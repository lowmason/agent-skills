# claude/quirky-golick-44b138: plan 90, the read-only guard's command-start walk

## Synopsis

**The plan:** The read-only guard missed 8 recorded lines that run a mutator in zsh. In each one, the walk that finds a subcommand's command word stopped at a word that might only lead the command, and took it for the command. Examples are a leading `{`, a leading `[[ … ]]` test, zsh's `=cmd`, and an assignment that `ASSIGNMENT` does not match. The plan closes those 8 lines without new zsh grammar, and it must not allow anything that `d79b1fb` denied. A `/deferred` pass chose the backlog item because of its age.

**The build:** The walk now reads each such word both ways, as a prefix and as the command. It yields every candidate start, and the classifier denies if any candidate denies. During the build, a timing check found quadratic work on long crafted lines. So the walk got three work bounds and a fail-closed cap at 64 candidates. A final review found that the cap denied heredoc rule lines of `=`. So a leading run of `=` is now stripped in one step. Tests pin each row, each bound and the cap. The README records two new false-positive classes.

**The project:** The guard closes the mixed-reading backlog item, except the glued glob qualifier, which moves to a new deferred item. A transcript sweep of 150,024 unique commands found no new false positive and no lost denial. The change goes live in every repository when it merges to `main`.

## Background

`hooks/readonly-agent-guard.py` is the `PreToolUse` (`Bash`) hook that denies mutating commands for the five read-only agents. It is a guardrail, not a sandbox. `classify` splits a command into lines, then into subcommands under each of the eight `READINGS` (nest, braces, quoting). It denies the line when any subcommand denies in any reading.

Before the branch, `_command_words` found each subcommand's command. It skipped `LEADING_KEYWORDS`, words that match `ASSIGNMENT`, `repeat` and its count, and `PREFIX_UTILITIES` with their options. It stopped at the first other word and returned one start. `_classify_subcommand` then sent that word to `_classify_git` or `_classify_non_git`.

That single guess failed in three classes, all listed in the backlog item "Each of the eight readings holds for a whole line" (`specs/deferred_items.md`):

- A brace group or `[[ … ]]` test leads the subcommand, and a git verb after it takes `]]` as an argument (3 lines). The `braces` reading cuts the subcommand at `]]`. The other reading stops at `{` or `[[`.
- zsh's `=cmd` path expansion (1 line). The walk stopped at `=rm`, a name it does not know.
- An assignment the guard does not recognise (4 lines): a subscripted name, a non-ASCII name, and env operands with `=` before and after `--`.

`hooks/README.md` listed all of these under "Not caught". The spec (`specs/completed/readonly-guard-command-starts.md`) chose Approach 1, "look for the command at every plausible start", over teaching the splitter zsh grammar. Approach 1 only adds candidates, so it cannot allow what `d79b1fb` denied.

## The change

### 1. `_stop_index`: today's walk, as an index

`_stop_index(words, i, known=None)` (`hooks/readonly-agent-guard.py:781`) replaces `_command_words`. It runs the same skip loop from position `i` and returns where the command starts: an index up to `len(words)`, or `None` where env's `-S` hides the command. It clamps the index to `len(words)`, because `repeat` or a prefix option that lacks its value can step past the end.

The `known` argument is a memo. It maps each loop head, as a pair of position and word text, to that head's result. A head already in the table ends the walk with the stored result. The docstring gives the reason this is sound: the walk from a head depends only on that word and the words after it, and those never differ within one call of `_command_starts`. The memo came late, in fix round 1 of Task 4 (`1607648`). Everything below depends on `_stop_index`.

### 2. `_command_starts`: every place the command may start

`_command_starts(words)` (`:822`) is a generator. It keeps a stack of continuations, each a start position and a word list. For each continuation it calls `_stop_index` and yields the words from the stop on. The first yield is the candidate that `_command_words` returned, unchanged. Then it queues more continuations by the spec's table:

| Stop word | Continue from |
|---|---|
| `{` | the next word |
| `[[` | the word after each later `]]`, quoted or not |
| contains `=` | the next word |
| begins with `=` | the same position, with every leading `=` removed, unless nothing is left |

The `=` strip builds a new `_Token` that keeps the `quoted`, `spaced` and `expands` flags of the original word.

Four structures keep it bounded:

- `visited` yields each stop word, keyed on position and text, once. Without it, a run of `==` words doubles the work at each word.
- `queued` drops a continuation whose start position and word were seen before, so it is walked once.
- `continued_past` stops the `[[` row's scan at a `]]` that an earlier scan already continued past. Without it, a chain of tests is quadratic.
- `known`, the memo in `_stop_index`, settles each loop head once. Without it, a `]]` inside a skipped run, such as the value of `env -u`, makes each continuation walk the rest of the run again.

The history entry records a ruling that contradicts the spec. After D6, no test fails when `queued` is removed alone. The build kept it anyway, because the spec (D3) names it and it is sound and cheap. The owner can ask to drop it as a follow-up.

### 3. `_classify_subcommand`: classify each candidate, with a cap

`_classify_subcommand` (`:896`) now loops over `_command_starts`. `None` returns `ENV_SPLIT_STRING`. An empty candidate is skipped. Every other candidate goes to the git or non-git classifier, and the first denial returns. Past 64 candidates it returns a fail-closed reason that asks for shorter commands. The reason for the cap is in its docstring: a slow walk would time out, and a hook that times out lets the call go on.

The denial text can change on a line that `d79b1fb` already denied, because a new candidate may deny first. The spec accepted this as a designer's call. `classify` itself, the tokenizer, `_split_tokens` and `READINGS` do not change.

### 4. Tests

`hooks/test_readonly_agent_guard.py` gains 148 lines and loses none (`:612-757`):

- `COMMAND_START_BYPASSES`: the 8 recorded lines, each denied with a reason that names `rm` or `git branch`.
- `COMMAND_START_ALLOWED`: 10 read-only cases. They pin each table row from the allow side and the edges a branch can reach (`command -v`, only redirections). They also cover heredoc underlines and AsciiDoc headings, and a read-only process substitution.
- `test_command_starts_yield_todays_candidate_first` checks that the old candidate comes first. Other tests check that each row continues and that a branch reaching `env -S` fails closed.
- `test_command_starts_visit_each_stop_word_once` bounds the candidates on runs of `==` and `[[ a ]]`.
- `test_command_starts_work_grows_linearly` counts the guard's line events with `sys.settrace` on three shapes at sizes 64 and 128. It asserts that the larger size takes less than 3 times the work. The plan records which shape fails when each bound is removed: no scan stop fails `test-chain`, and no `known` fails `skipped-run`.
- `test_more_than_64_command_starts_fail_closed`: 63 leading `{ ` pass, and 64 are denied.
- `EQUALS_TEXT_ALLOWED` and `test_leading_equals_strip_in_one_step` pin D6. A long `=` rule, a reStructuredText table border and a long `=` prefix all pass. 80 leading `=` give at most 3 candidates.

### 5. `hooks/README.md`

The "Limitations (by design)" paragraph now says which words the guard reads both ways. Under "Not caught", the `=cmd` example and the bullet on unrecognised assignments are gone. The mixed-reading bullet keeps its structural point but drops its three examples. "Known false positives" gains two entries. A leading word with `=`, `{` or `[[` is read both ways, so the AsciiDoc heading `== rm and mv ==` in a heredoc is denied. A subcommand with more than 64 command starts is denied, and the entry notes that no subcommand in the 150,024 checked commands had more than 13.

### 6. Spec, plan and backlog records

The range holds the whole life of the work. It adds the spec and its approval, plan 90 and its approval through two merges, the build, and the retirement of both files to their `completed/` folders. The plan's `## Decisions` lists D1 to D6. D3, D4 and D6 amended the spec during execution:

- D3, "Fix it now": bound the walk's quadratic work.
- D4, "Dedupe + cap": the work bounds plus the cap at 64.
- D6, "Strip all = at once": the fix for the cap's heredoc false positive.

D2 and D5 accept the walk's and the cap's false-positive classes. The `specs/history.md` entry records three rulings and four deviations. The deviations are:

- Task 3's gate added Tasks 4 and 5.
- Fix round 1 added the memo.
- The bite check removes `queued` and `known` together.
- Task 5 timed 11 shapes at up to 480 KB, not 512 KB. The slowest took 1.97 s.

Task 7 corrected its own expectation after the run. That run found 0 flips over 152,235 inputs.

## What it adds to the project

The guard now catches a mutator that hides behind a word that might only lead the command. It also keeps every denial it had: Tasks 3, 5 and 7 compared the old and new guards over the corpus, the test file's strings and both versions of the README's examples, and found no line that went from denied to allowed. The worst case is now linear, so a crafted long line cannot time the hook out and let the call through. The cost is two accepted false-positive classes. The sweep found that neither one fires on real commands.

The guard stays stdlib-only and 3.9-compatible. `~/.claude/hooks/readonly-agent-guard.py` is a symlink into the main checkout, so every repository runs the new walk once the branch merges. The spec's Gate B probe (`hooks/probe-readonly-guard.sh`) can test it only after that merge.

The backlog item is ticked in `specs/deferred_items.md`, with a note that maps the 8 lines to their commits. One new deferred item is open under `90-readonly-guard-command-starts`. It covers the glob qualifier glued to the command word (`git(.) stash`). It stays under "Not caught", because a simple fix would also deny `print(git(x))` in a heredoc. It needs a design that tells the two apart.

## Questions

1. What did plan 90 set out to do, and why did it choose to add candidate starts rather than teach the splitter where a command can start?
2. How was the walk built, and which three work bounds and which cap keep it from timing the hook out?
3. What does the branch add to the guard's coverage and false positives, and what does it leave for later?
