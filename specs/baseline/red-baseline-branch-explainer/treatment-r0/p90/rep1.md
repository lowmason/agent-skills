# claude/quirky-golick-44b138: plan 90, the read-only guard's command-start walk

## Synopsis

**The plan:** The read-only guard missed 8 recorded lines that run a mutator in zsh. In each line the walk stopped at a word that might only lead the command, such as `{`, `[[`, `=rm` or `arr[1]=x`, and took that word for the command. The plan set out to deny those 8 lines without losing any denial that `main` makes. It added no new model of zsh grammar. A `/deferred` pass picked the item because it was old, not because of a failure.

**The build:** `_command_words` became `_stop_index`, which finds one stop word. The new generator `_command_starts` yields today's candidate first. Then it continues the walk past each word that may only lead the command. `_classify_subcommand` classifies every candidate and returns the first denial. During the build the owner added a work bound (D3), a fail-closed cap at 64 candidates (D4), and a one-step strip of leading `=` (D6). Tests and the README follow the code.

**The project:** The guard now reads such a word both ways, as a prefix and as the command. The set of denied commands can only grow. The deferred item on the eight readings is closed, except for the glued glob qualifier, which is filed as a new design item. The guard gains two accepted false-positive classes. The sweep over 150,024 commands found no false positives.

## Background

`hooks/readonly-agent-guard.py` is the `PreToolUse` (`Bash`) hook that denies mutating commands for the read-only agents. `classify` (`hooks/readonly-agent-guard.py:921`) splits each line in each of the eight `READINGS` (`:108`) and classifies every subcommand. Any denial stands.

For each subcommand, `_command_words` walked the words to find the command. It skipped `LEADING_KEYWORDS`, words that match `ASSIGNMENT` (`:177`, ASCII identifiers only), `repeat` and its count, and `PREFIX_UTILITIES` with their options. It stopped at the first other word and returned one start.

That single guess was the gap. The backlog item "Each of the eight readings holds for a whole line" (`specs/deferred_items.md`) recorded 10 lines, and the README's mixed-reading bullet added an 11th. `d67f856` had closed 2 of them. The spec sorted the rest by where the walk stops:

- A leading brace group or `[[ … ]]` test before a git verb: 3 lines.
- zsh's `=cmd` path expansion: 1 line.
- An assignment that `ASSIGNMENT` does not match: zsh subscripts, non-ASCII names, and env operands before or after `--`: 4 lines.
- A glob qualifier glued to the command word: 1 line, out of scope.

The spec (`specs/completed/readonly-guard-command-starts.md`) chose Approach 1 (owner D1): look for the command at every plausible start, and change only the walk. It rejected two other approaches. Teaching the splitter where a command can start would remove a reading and risk lost denials. Reading each ambiguous token both ways would double the readings at each token.

## The change

### 1. `_stop_index`: one walk from a given position

`_stop_index(words, i, known=None)` (`hooks/readonly-agent-guard.py:781`) replaces `_command_words`. It skips the same words in the same way, but it starts at any index and returns an index. It returns `len(words)` when there is no command, and `None` where env's `-S` hides it. The returned index is clamped to `len(words)`, since `repeat` or a prefix option that lacks its value can step past the end.

The optional `known` dict is the memo from the first fix round (`1607648`). It maps each loop head, keyed on position and word text, to where the walk from there stops. A head already in it ends the walk at once. This exists because a `]]` that `repeat` or a prefix option consumes lies inside a skipped run. Each continuation after it re-walked the whole run. The spec records an 80 KB read-only line that took 159 s for that reason. Everything below depends on this function.

### 2. `_command_starts`: every candidate start

`_command_starts(words)` (`:822`) is a generator. It queues continuations as (start, word list) pairs, walks each with `_stop_index` and yields `seq[k:]` at each new stop. The first yield is today's candidate, unchanged. At each stop word it queues more continuations, one rule per row of the spec's table:

- `{`: from the next word.
- `[[`: from the word after each later `]]`, quoted or not.
- A word that contains `=`: from the next word. This one rule covers zsh assignments that `ASSIGNMENT` misses and env operands, `--` included, with no model of env's grammar.
- A word that begins with `=`: the same position, with every leading `=` stripped in one step. If nothing is left, this row adds nothing. This is D6 (`a9773f22`). The first version stripped one `=` at a time.

Three structures bound the walk:

- `visited` yields each stop word at its position once. Without it, a run of `==` words or a chain of tests doubles the walk at each word.
- `queued` drops a continuation whose start position and word were seen before. This is D3.
- `continued_past` stops a `[[` scan at a `]]` that an earlier scan already continued past. This is D4's second part.

The `known` memo is shared across the whole walk. The docstring explains why the key is sound: a continuation's words differ from the subcommand's only at or before its start.

### 3. `_classify_subcommand`: the first denial, and the cap

`_classify_subcommand` (`:896`) now loops over `_command_starts`. `None` returns `ENV_SPLIT_STRING`. An empty candidate is skipped. Others go to `_classify_git` or `_classify_non_git`, and the first denial returns. Past 64 candidates it fails closed, and the reason asks for shorter commands. The limit is a literal inside the function, as the spec asked, not a module constant. This is D4 (`a6729427`). A denial's text can now come from a new candidate on a line that `main` already denied. The spec accepted that as a designer's call.

### 4. Tests

`hooks/test_readonly_agent_guard.py` gains 148 lines and 10 test functions:

- `COMMAND_START_BYPASSES`: the 8 recorded lines, each denied with a reason that names `rm` or `git branch`.
- `COMMAND_START_ALLOWED`: 10 read-only forms. They pin each row both ways and cover edges such as `{ command -v rm; }`, a lone redirection and AsciiDoc headings in a heredoc.
- Walk-level tests through a `_starts` helper. Today's candidate comes first, each row continues, and env `-S` fails closed.
- `test_command_starts_visit_each_stop_word_once`: 16 repeats of `== ` or `[[ a ]] ` yield at most 3× the word count.
- `test_command_starts_work_grows_linearly`: it counts line events in the guard's own code with `sys.settrace`. Three shapes (`test-chain`, `leading-equals`, `skipped-run`) must stay under 3× when the line doubles from 64 to 128 repeats. It uses no time limit, because timing is unreliable across the two interpreters.
- `test_more_than_64_command_starts_fail_closed`: 63 `{ ` pass, and 64 are denied.
- `EQUALS_TEXT_ALLOWED` and `test_leading_equals_strip_in_one_step`: long `=` rules and table borders in heredocs pass, and 80 leading `=` give at most 3 candidates.

### 5. README and backlog

`hooks/README.md` adds to "Limitations (by design)" the words that the guard reads both ways. "Not caught" loses the `=cmd` example, the unrecognised-assignment bullet and the three mixed-reading examples. "Known false positives" gains two entries: words read both ways (with the heredoc `== rm and mv ==` example), and the 64-candidate cap.

`specs/deferred_items.md` ticks the eight-readings item and adds one design item for the glued glob qualifier. `specs/history.md` records the entry, and the plan and spec move to their completed folders.

### 6. Where the build differs from the spec

The spec was amended during execution, so the code matches the amended spec. The history entry records 3 rulings, 5 deviations and 3 spec-amending decisions:

- **D3, D4:** Task 3 found quadratic work on long crafted lines. The owner chose "Fix it now", then "Dedupe + cap". Tasks 4 and 5 were added.
- **Memo ruling (Task 4):** the `known` memo was added as fix round 1, because the dedupe alone left the skipped-run class quadratic.
- **D6:** the final review found that the cap denied a heredoc rule made of a long run of `=`. The owner chose "Strip all = at once".
- **`queued` ruling (final review):** `queued` stays, as D3 requires. After D6, no test fails when it alone is removed. The bite check removes `queued` and `known` together and fails only `skipped-run`. The entry accepts this as a little untested code.
- **Task 5:** the timing run went up to 480 KB, not 512 KB. The slowest of 11 shapes took 1.97 s, and all grew linearly.

## What it adds to the project

Flows: every guarded agent's Bash call now goes through the multi-candidate walk. The change goes live on merge, because `~/.claude/hooks/readonly-agent-guard.py` is a symlink into the main checkout. Spec Verification 6 then calls for Gate B, `./hooks/probe-readonly-guard.sh`, in the main checkout.

Guarantees: the walk only adds candidates. It always yields today's candidate, and the readings, the splitter and the classifiers did not change. So no denial is lost. Task 7 rechecked this, and no denial changed. The sweep found 0 false positives in 150,024 unique commands, and the owner accepted both new classes (D2 and D5). The largest subcommand in the sweep had 13 candidates.

Dependents: `classify` and its callers rely on `_classify_subcommand` as before. Its signature and return values did not change. `_command_words` is gone.

Left for later: one new deferred item, a design-sized fix for the glued glob qualifier. It needs a rule that tells `git(.) stash` apart from `print(git(x))` in a heredoc. The README's other "Not caught" items stay open, such as `$c x` and a brace glued to the command word.

## Questions

1. What did plan 90 set out to do, and why did it limit itself to the walk rather than the splitter or the readings?
2. How do `_stop_index`, `_command_starts` and `_classify_subcommand` fit together, and which three structures, plus the memo and the cap, keep the walk linear?
3. What does the branch change for the guarded agents and the backlog, what new false positives does it accept, and what does it leave open?
