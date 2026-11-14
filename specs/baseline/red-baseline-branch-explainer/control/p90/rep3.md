# What `84efc992..HEAD` changes (plan 90: the read-only guard's command-start walk)

**In one line:** the read-only agent guard (`hooks/readonly-agent-guard.py`) no longer looks
for a subcommand's command in just one place. Wherever a word *might* only be a prefix of
the command, it reads that word both ways, and it denies if either reading denies. Most of
the rest of the range is the spec and plan behind that change, and their bookkeeping.

24 commits, 7 files, +1262 / −37. Only two files hold code:

| File | Change |
|---|---|
| `hooks/readonly-agent-guard.py` | +142/−37: `_command_words` is replaced by `_stop_index` + `_command_starts`, and `_classify_subcommand` now loops over the candidates |
| `hooks/test_readonly_agent_guard.py` | +148: new deny, allow, bound, work and cap tests |
| `hooks/README.md` | The walk is described, three "Not caught" entries are removed, two "Known false positives" entries are added |
| `specs/completed/readonly-guard-command-starts.md` | New: the approved design spec, with the D3/D4/D6 amendments, retired |
| `specs/plans/completed/90-…md` | New: plan 90 with its decisions D1–D6, retired |
| `specs/deferred_items.md` | The "eight readings" item is ticked done, and one new item is filed (the glued glob qualifier) |
| `specs/history.md` | Plan 90 entry: rulings, deviations, decisions |

---

## 1. The problem

The guard splits a Bash line into subcommands. In each subcommand it then walks past
words that only lead the command: keywords, assignments such as `X=1`, and prefix
utilities such as `time`, `env` and `nice` with their options. The first other word is
taken as the command, and that command is classified as git or non-git.

That walk had only one guess. When it stopped at a word that zsh may treat as a prefix,
it took that word for the command, and the real mutator after it was never read. The
backlog item recorded these classes (in `COMMAND_START_BYPASSES` in the test file):

- **A leading brace group or `[[ … ]]` test**: 3 lines. In the reading that splits on
  braces, `]]` ends the subcommand. In the other reading, the walk stopped at `{` or `[[`.
- **zsh `=cmd` path expansion**: 1 line. `=name` expands to the path of `name`.
- **Assignments the `ASSIGNMENT` regex misses**: 4 lines. These are subscripted names,
  non-ASCII names, and `env` operands that contain `=` but are not identifiers, before or
  after `--`.

All 8 were allowed on `main` before this change. They are now denied.

## 2. The new walk (`readonly-agent-guard.py:781-918`)

**`_stop_index(words, i, known)`** is the old `_command_words` loop. It now starts at
any index and returns that index instead of a slice: `len(words)` means there is no
command, and `None` means `env -S`. It takes an optional memo, `known`, which maps
`(position, word)` to where the walk stops from there.

**`_command_starts(words)`** is a generator. Its first candidate is always the old
candidate, unchanged. At each stop word it also queues more walks:

| Stop word | Also continue from |
|---|---|
| `{` | the next word |
| `[[` | the word after each later `]]`, quoted or not |
| contains `=` | the next word (covers env operands too, with no model of env's grammar) |
| starts with `=` | the same position, with **all** leading `=` stripped at once (D6), unless nothing is left |

Each continuation is a full walk, so it can skip more keywords and prefixes and reach new
stop words.

**`_classify_subcommand`** classifies each candidate the way the single candidate was
classified before. The first denial wins. A candidate of `None` gives the old
`ENV_SPLIT_STRING` denial. **A subcommand with more than 64 candidates fails closed**,
with a "split the command" message.

### Why it can't allow anything `main` denied

The tokenizer, the readings, the split and both classifiers are unchanged. The first
candidate is always the old one. The new code only adds candidates, and the cap only adds
denials. So the set of denied commands can only grow. The plan checked this one-off
against the old guard, over the test strings, the README commands and a transcript corpus.

### The performance work (most of the code's complexity)

A slow hook **fails open**: if the hook times out, the call goes ahead. So the walk has
to stay linear even on crafted input. Without bounds, the walk was exponential, then
quadratic. It now has four bounds:

1. **`visited`**: each `(position, stop word)` pair is yielded once. This stops a run of
   `==` words or chained `[[ ]]` tests from doubling the walk at each word.
2. **`queued`**: each continuation `(start, word)` is queued once.
3. **`continued_past`**: a `[[` scan stops at the first `]]` that an earlier scan already
   continued past.
4. **`known`** (the memo in `_stop_index`): this covers a `]]` inside a run of words that
   the walk skips, for example one taken as a prefix option's value. Each continuation
   used to re-walk that run. Before this fix, an 80 KB read-only line took 159 s.

The 64-candidate cap then makes the worst case linear. Per the plan's history, 11 shape
classes of input up to 480 KB were timed, and the slowest took 1.97 s.

**Correctness of the memo:** the result of a walk from position `i` depends only on
`words[i:]`. Every continuation either starts at a later word or rewrites only the word
at its own start, so within one `_command_starts` call, `(i, words[i])` decides
`words[i:]`. The docstrings state this argument.

## 3. Behaviour changes you'll notice

- **New denials (intended):** the 8 recorded lines.
- **New false-positive class (D2, accepted):** a leading word that contains `=`, starts
  with `=`, or is `{` or `[[` is also read as a prefix. So the word after it gets
  classified too. Example from the README: an AsciiDoc heading `== rm and mv ==` inside a
  heredoc is denied.
- **The cap (D5, accepted):** a subcommand with more than 64 candidate starts is denied.
  In the sweep of 150,024 real commands, no subcommand had more than 13 candidates.
- **D6 fix:** the first version stripped one `=` per step, so a heredoc rule line of 63
  or more `=` hit the cap. Stripping every leading `=` at once fixed that, and
  `EQUALS_TEXT_ALLOWED` pins it.
- **The denial text can change** on lines that were already denied, because an earlier
  candidate may deny first (designer's call 5). The line is still denied.
- **The false-positive sweep** found 0 new false positives in 150,024 unique transcript
  commands, both before and after the amendments.

## 4. What it deliberately does not fix

- **A glob qualifier glued to the command word.** It runs only with `BARE_GLOB_QUAL`,
  which the Bash tool turns off. The obvious fix would deny `print(git(x))` in heredocs.
  It stays under "Not caught" and is filed as a new deferred item that needs design.
- Command words that the shell produces by expansion (`$c x`, `$(which rm)`), and a brace
  glued to the command word. These stay under "Not caught".
- The `nest` and `braces` readings still apply to the whole line. The README's
  mixed-reading bullet keeps that point, but drops its examples.

## 5. Things worth a look before merging

- **`queued` has no test that fails without it after D6.** The history records a ruling
  to keep it anyway: the spec requires it, it is sound and cheap, and the memo and the
  scan stop have their own tests. If you'd rather not keep untested code, drop it as a
  follow-up.
- **The work test (`test_command_starts_work_grows_linearly`)** counts line events with
  `sys.settrace` and asserts that doubling the input less than triples the work. It
  doesn't use wall-clock time, so it is stable, but it depends on line counts. A
  refactor that adds lines per iteration won't break it, but a much heavier constant
  might come close to the 3× margin.
- **The cap message** is a new kind of denial that agents could see. It tells them to
  split the command.
- **The live-on-merge risk:** `~/.claude/hooks/readonly-agent-guard.py` is a symlink into
  the main checkout, so this goes live for every repository at merge. After merging, the
  plan expects you to run Gate B: `./hooks/probe-readonly-guard.sh` should exit 0 and
  print three `ok:` lines. That check spawns `claude -p` runs, and it is not done yet,
  because it can only run after the merge.
- **The 3.9 floor:** the code uses no 3.10+ syntax and stays stdlib-only. `import sys` is
  added only in the test file.
- **Codex review:** the plan required one Codex bypass-hunting round. I did not find its
  result recorded in the plan's Decisions, and I didn't look in `/tmp/codex-review/`. If
  it found anything, the owner's pick isn't logged in this range.

## 6. Verification I ran

`uv run --with pytest python -m pytest -q hooks/test_readonly_agent_guard.py` on HEAD
gave **304 passed**, in about 6 s. I ran this under uv's default interpreter only. I did
not run the `/usr/bin/python3` (3.9.6) half of `build/run_suites.py hooks`, the commit
lints, or Gate B.
