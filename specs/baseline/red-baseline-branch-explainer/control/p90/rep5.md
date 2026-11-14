# What `84efc992..HEAD` changes: plan 90, the read-only guard's command-start walk

**In one line:** the read-only guard (`hooks/readonly-agent-guard.py`) used to look for a subcommand's
command at one position only. Now it checks every position where the command might start, and if any of
them denies, the line is denied. This closes 8 recorded bypasses. The rest of the range is the spec, the
plan, and bookkeeping.

The range has 24 commits and touches 7 files (+1262 / −37). It includes two earlier merges: the approved
spec (`8464d1fe`) and the approved plan (`04f7a614`). So merging HEAD brings in the spec, the plan and the
implementation together.

| File | What changed |
|---|---|
| `hooks/readonly-agent-guard.py` | The only code change. `_command_words` is replaced by `_stop_index` and `_command_starts`, and `_classify_subcommand` is rewritten (+142/−37 lines in total) |
| `hooks/test_readonly_agent_guard.py` | +148 lines of new tests. No existing test was edited |
| `hooks/README.md` | The limitations section, "Not caught" and "Known false positives" now match the new walk |
| `specs/completed/readonly-guard-command-starts.md` | The design spec, approved and then amended during execution (D3, D4, D6). Now retired |
| `specs/plans/completed/90-…md` | The executed plan, with the decision log D1–D6 |
| `specs/deferred_items.md` | The "eight readings" item is ticked as done, and one new item is filed for the glued glob qualifier |
| `specs/history.md` | The plan 90 entry, which lists the rulings and deviations |

---

## 1. The problem it fixes

The guard splits a line into subcommands. In each subcommand it walks past words that come before the
command: keywords, `X=1` assignments, and prefix utilities such as `env`, `time` and `nice` with their
options. It treats the first word it doesn't skip as the command.

That first word can be one the shell would skip, which hides the real command after it. The backlog
recorded 8 such lines in three classes (`COMMAND_START_BYPASSES` in the test file):

| Class | Lines | Why the old walk missed the command |
|---|---|---|
| A leading `{ … }` group or `[[ … ]]` test, with a git verb after it | 3 | The walk stopped at `{` or `[[` and took it for the command |
| zsh's `=cmd` path expansion | 1 | The walk stopped at `=name`, which isn't a command it knows |
| An assignment the `ASSIGNMENT` regex doesn't match (subscripted, non-ASCII, or an `env` operand before or after `--`) | 4 | The walk stopped at the assignment word |

A ninth example, a glob qualifier glued to the command word, is out of scope on purpose. It stays under
"Not caught" in the README, and it is filed again as a new deferred item.

## 2. How the code works now

**`_stop_index(words, i, known)`** is the old skip loop. It can now start at any position, and it returns
an index instead of a slice (`len(words)` when there is no command, `None` when `env -S` hides the
command). The optional `known` dict remembers where each `(position, word)` stops, so a run of skipped
words is walked only once per walk.

**`_command_starts(words)`** is a generator. It first yields exactly the candidate the old code found.
Then, at each word where the walk stops, it also queues more places to read from:

| The word where the walk stops | The walk also continues from |
|---|---|
| `{` | the next word |
| `[[` | the word after each later `]]`, quoted or not |
| contains `=` | the next word |
| starts with `=` | the same position, with all leading `=` removed (unless nothing is left) |

**`_classify_subcommand`** sends each candidate to the existing git or non-git classifier and returns the
first denial. Past 64 candidates it fails closed with its own reason.

**The safety argument (spec §3).** The first candidate is always the old one, and the tokenizer, the
splitter, `READINGS` and the classifiers are unchanged. So the set of denied lines can only grow. The plan
checked this against the base guard (`d79b1fb`) on the test file, the README, and 150,024 unique commands
from your transcripts: 0 lines went from denied to allowed. A second run after the final `=` change also
found 0.

### Bounding the work (D3, D4, D6)

A walk that branches can blow up, and **a hook that times out lets the call through**. So the bounds are
part of the security story, not just performance. Four mechanisms bound it:

1. **`visited`** (position, stop word): each candidate is yielded once.
2. **`queued`** (start position, word there): each continuation is walked once.
3. **`continued_past`**: a `[[` scan stops at a `]]` that an earlier scan already handled, so a chain of
   tests stays linear.
4. **`known`**: remembers where each loop head stops. This fixed a run of skipped words that cost 159 s on
   an 80 KB line.

On top of these, **the 64-candidate cap** makes the worst case linear. The plan reports that a crafted
512 KB line is classified in under 1 s, and that 11 crafted shapes up to 480 KB took at most 1.97 s.

**D6** changed the `=` rule. It first removed one `=` at a time, so an 80-character `=====` underline in a
heredoc reached the cap and was denied. Now every leading `=` goes in one step.

## 3. What you're accepting

- **New false positives (accepted in D2 and D5, both recorded in the README):**
  - A word at the start of a command that is `{` or `[[`, or that contains or starts with `=`, is read both
    ways. Text in a heredoc can then trip the guard. I checked: a heredoc line `== rm and mv ==` is
    denied.
  - A subcommand with more than 64 command starts is denied.
  - The sweep found 0 false positives in 150,024 commands. The most candidates any real subcommand had
    was 13.
- **Denial messages can change** on lines that were already denied, because a new candidate can deny
  first. The line is still denied (designer's call 5).
- **`queued` has no test that fails without it** since D6. You ruled to keep it because the spec requires
  it (`specs/history.md`). You can ask to drop it later.

## 4. What I checked

- `uv run python build/run_suites.py hooks`: **461 passed** on the dev Python and **461 passed** on
  `/usr/bin/python3` (the 3.9 floor).
- I fed a few lines to `classify` directly. `git log` and `{ git log; }` are allowed, and so are a bare
  80-`=` line and `a==b git status`. The heredoc `== rm …` line is denied, and 64 leading `{ ` are denied
  with the cap's reason. These match the README and the tests.
- I read the code against the spec. Only `_command_words` and `_classify_subcommand` were replaced (by
  `_stop_index`, `_command_starts` and the new `_classify_subcommand`). The memo keys are sound: every
  continuation differs from the original words only at or before its start position.

I did **not** rerun the corpus sweep or the base-vs-new comparison. The 0-flip and 0-false-positive numbers
come from the plan's records.

## 5. Before and after you merge

1. **Check that the Codex round happened.** The spec (Verification 7) and the plan's Global Constraints
   call for one Codex bypass-hunting round, with your fix/record/stop pick logged in `## Decisions`. Its
   outcome isn't recorded anywhere in this range. The decisions stop at D6, and `specs/history.md` doesn't
   mention it. The only "final review" finding recorded is the one behind D6, the `=` underline hitting the
   cap. Confirm whether Codex ran and what it found, or that you chose to skip it.
2. **It goes live on merge.** `~/.claude/hooks/readonly-agent-guard.py` is a symlink into the main
   checkout, so every repository uses the new walk as soon as it merges there.
3. **Run Gate B after the merge.** In the main checkout, `./hooks/probe-readonly-guard.sh` should exit 0
   and print three `ok:` lines. It can't run before the merge, and nothing in the range says it has run.
4. HEAD is a detached checkout at `d51bf645`, not a named branch. Merge it by commit or create a branch
   first.
