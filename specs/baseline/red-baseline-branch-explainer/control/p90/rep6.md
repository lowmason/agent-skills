# What `84efc992..HEAD` changes (plan 90: the read-only guard's command-start walk)

## In one paragraph

The read-only guard (`hooks/readonly-agent-guard.py`) used to look for the command in a
subcommand by skipping a fixed set of leading words (keywords, assignments, `env`/`time`/…
with their options) and treating the first other word as the command. Eight recorded lines
got past it because that first other word was really only a *lead-in*: a brace group, a
`[[ … ]]` test, zsh's `=cmd` path expansion, or an assignment / `env` operand that the
`ASSIGNMENT` regex doesn't match. The guard now reads each such word **both ways**: as the
command, and as a lead-in it keeps walking past. If **any** reading is denied, the command is
denied. The rest of the work keeps that walk fast. A guard hook that times out lets the
call go on, so a slow walk is the same as no guard.

Of the 7 files, 3 matter for behaviour: the guard, its tests, and the README. The other 4
are spec and plan records (the design spec, the completed plan 90, `history.md`, and
`deferred_items.md`), and about 950 of the 1,262 added lines are in them.

## Branch shape

- 24 commits. The range includes two merges (the approved spec, then the approved plan),
  followed by the implementation and its fix rounds, and then the retirement of the plan.
- `main` is still at `84efc992`, the base of the range, so this merge is a fast-forward.
- **The change goes live as soon as you merge.** `~/.claude/hooks/readonly-agent-guard.py`
  is a symlink into the main checkout, so every repository picks it up immediately.

## The code change (`hooks/readonly-agent-guard.py`, about +140 lines)

`_command_words` is replaced by three pieces:

### `_stop_index(words, i, known=None)`

This is the old walk loop, starting at any index. It returns where the command starts: an
index, `len(words)` if there is no command, or `None` if `env -S` hides it. The new
optional `known` dict memoises each "loop head" `(position, word text)` → result. A later
walk that reaches a head it has already seen returns the stored result straight away. The
docstring explains why that key is sound: within one walk, the words *after* a given
position never differ between continuations.

### `_command_starts(words)` (a generator)

It yields every candidate command start. The first yield is always exactly the old
candidate, which is the basis of the "can't allow anything the old guard denied" argument.
Then, depending on the stop word:

| The stop word… | The walk also continues from… |
|---|---|
| is `{` | the next word |
| is `[[` | the word after **each** later `]]` (quoted or not) |
| contains `=` | the next word (an unrecognised assignment, or an `env` operand) |
| starts with `=` | the same position, with **all** leading `=` stripped (skipped if nothing is left) |

Each continuation runs the full walk again, so it can skip more keywords or prefixes and
add more continuations of its own.

Four bounds keep the work linear:

1. `visited`: each `(stop position, stop word)` is yielded at most once. This stops the
   exponential blow-up from chains like `== == == …` or repeated `[[ a ]]`.
2. `queued`: each `(start position, word)` continuation is queued at most once.
3. `continued_past`: a `[[` scan stops at the first `]]` that an earlier scan has already
   continued past.
4. The `known` memo in `_stop_index` handles runs of words that the walk skips, for example
   `]]` consumed as a prefix utility's option value.

### `_classify_subcommand`

This now loops over `_command_starts` and returns the first denial. Past **64** candidates
it fails closed with its own message ("…more than 64 places where its command may
start…"). An `env -S` candidate still returns `ENV_SPLIT_STRING`, and an empty candidate
(no command, for example only redirections or `command -v`) is skipped.

Things that did **not** change: the tokenizer, `_split_tokens`, `READINGS`, and the git and
non-git classifiers. The guard stays stdlib-only and 3.9-compatible.

## Behaviour changes you should know about

**Newly denied (the goal).** The 8 recorded bypass lines, in 4 classes: leading brace
group (2), leading `[[ … ]]` test (1), leading `=cmd` (1), and a word containing `=` that
isn't a recognised assignment (4, two of them via `env`, one before `--` and one after).
They're pinned in `COMMAND_START_BYPASSES` in `hooks/test_readonly_agent_guard.py`.

**New false positives, documented in the README and accepted by you as D2 and D5:**

- A word at command start that is `{` or `[[`, contains `=`, or starts with `=` also has
  the word after it classified. That applies even where zsh would run the first word, and
  in heredoc text. The README's example is an AsciiDoc heading like `== rm and mv ==`
  inside a heredoc, which is now denied.
- A subcommand with more than 64 candidate starts is denied outright. According to the
  plan's records, the largest count in your 150,024-command transcript corpus was 13.

**Denial text can change** on lines the old guard already denied. A new candidate in an
earlier subcommand or reading can produce the first denial. The line is still denied, and
the new message names a real mutator. This was a deliberate designer's call (spec §2).

**Still allowed, and pinned.** These include Markdown `=====` underlines, AsciiDoc `=`/`==`
headings with read-only words, long `=` rules and rST table borders in heredocs,
`{ command -v rm; }`, and read-only process substitution. The D6 change ("strip every
leading `=` in one step") exists so that a long `=` rule doesn't reach the 64 cap. That
problem was found in the final review.

## README changes (`hooks/README.md`)

- **"Limitations"**: a new paragraph describes the both-ways reading. The rest of that
  paragraph's diff is only re-wrapped lines.
- **"Not caught"**: the `=cmd` example and the bullet on unrecognised assignments are
  removed. The mixed-reading bullet loses its three examples and now says that a leading
  brace group or test no longer hides the command.
- **"Known false positives"**: two new bullets, one for the both-ways reading and one for
  the 64 cap.

## Tests (`hooks/test_readonly_agent_guard.py`, +148 lines)

- The 8 deny cases, plus 10 allow cases that pin each table row with a read-only command.
- Structural tests on `_command_starts`: the old candidate comes first, each row continues,
  and an `env -S` reached by a continuation still fails closed.
- A bound test: 16 repeated `==` or `[[ a ]]` words yield at most 3× the word count of
  candidates.
- A work test: it uses `sys.settrace` to count line events in the guard and asserts that
  doubling the line less than triples the work (linear, not quadratic). It covers 3 shapes:
  `test-chain`, `leading-equals` and `skipped-run`.
- A cap test: 63 leading `{` are allowed and 64 are denied with the cap message.
- Heredoc `=` text cases, plus a check that 80 leading `=` give at most 3 candidates.

**I ran them myself:** `uv run python build/run_suites.py hooks` passed 461 tests across
both suite runs ("suite runs passed"). `/usr/bin/python3 -m pytest
hooks/test_readonly_agent_guard.py` passed 304 tests. (The default `python3` on `PATH`,
3.15, has no pytest installed, so I ran the file directly only under `/usr/bin/python3`.)

## Verification the branch says was done (I did not re-run this)

These come from the plan and `specs/history.md`. The scripts and corpus are in
`~/.cache/agent-skills/scratch/plan90-work/` and were not committed.

- No denial was lost relative to the pre-change guard, checked over the test file's
  strings, the README's commands, and the transcript corpus.
- The false-positive sweep found 0 new denials in 150,024 unique transcript commands, both
  before and after the cap and the D6 change.
- After D6, there were 0 flips over 152,235 inputs compared with Task 4's code.
- The worst crafted line (480 KB) took 1.97 s, and every shape stayed linear.

## Worth checking before or after you merge

1. **No Codex bypass-hunt result is recorded in the branch.** The spec (Verification 7) and
   the plan's Global Constraints call for exactly one Codex round, with any findings
   reported to you by class and a fix/record/stop decision logged in `## Decisions`. The
   decisions go D1–D6 and none mentions Codex, and `history.md`'s plan-90 entry doesn't
   either. Either the round found nothing and that wasn't written down, or it didn't run.
   Confirm which (look for a file under `/tmp/codex-review/`) before relying on the guard.
2. **Gate B still has to run after the merge**: `./hooks/probe-readonly-guard.sh` in the
   main checkout should exit 0 and print three `ok:` lines. The installed hook is a
   symlink, so this test can only run after the merge.
3. **`queued` currently has no test that fails without it.** After D6 removed the class it
   bounded, removing `queued` fails no test. The scan stop and the memo each still have a
   test that does. It was kept on purpose because the spec requires it. History records
   that you can ask to drop it as a follow-up.
4. **Two judgment calls are now your policy**: the "each later `]]`" rule (it reads more
   than zsh does, so it only adds denials) and the 64 cap (it fails closed, and the message
   asks the agent to split the command).
5. **One item is left open on purpose**: a glob qualifier glued to the command word. It is
   filed in `specs/deferred_items.md` under plan 90 as a design item, and the README keeps
   it under "Not caught". zsh only runs it with `BARE_GLOB_QUAL`, which the Bash tool turns
   off.

## Bookkeeping in the range

- The backlog item that begins "Each of the eight readings…" is ticked, with a done note.
- The glued-qualifier deferral is added.
- `specs/history.md` gets a plan-90 entry listing the rulings, deviations, and decisions
  D3, D4 and D6.
- The spec and the plan are moved to `completed/`.
