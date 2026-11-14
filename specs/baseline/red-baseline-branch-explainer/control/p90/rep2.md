# What `84efc992..HEAD` changes: the read-only guard's command-start walk (plan 90)

## In one paragraph

`hooks/readonly-agent-guard.py` used to find a subcommand's command at **one** place: it skipped
keywords, assignments and prefix utilities (`time`, `env`, …), then took the first other word as
the command. Some words might either lead the command or be the command. The guard always assumed
they were the command, so a mutator after them was never checked. The branch now reads each such
word **both ways**, checks every place the command could start, and denies the subcommand if any of
those places denies. This closes 8 recorded bypass lines from the backlog item "Each of the eight
readings holds for a whole line". Because the extra reading could get slow on crafted input, and a
hook that times out lets the call through, the walk's work is now bounded. A subcommand with more
than 64 candidate starts is denied (fails closed).

The branch has 24 commits: 4 change code, and the rest are the spec, plan 90, the owner's rulings,
and the history/backlog records. It is **not merged into `main` yet**, and `84efc992` is `main`'s tip.

## Files

| File | Change |
|---|---|
| `hooks/readonly-agent-guard.py` | +123/−19: `_command_words` replaced by `_stop_index` + `_command_starts`; `_classify_subcommand` loops over candidates |
| `hooks/test_readonly_agent_guard.py` | +148: deny list (8), allow list (10), walk-shape, bound, linear-work, cap, and `=`-text tests |
| `hooks/README.md` | Limitations paragraph describes the both-ways reading. Two "Not caught" bullets shrink or go. Two new "Known false positives" |
| `specs/completed/readonly-guard-command-starts.md` | New (retired) design spec, with amendments D3/D4/D6 |
| `specs/plans/completed/90-readonly-guard-command-starts.md` | New (retired) plan with decisions D1–D6 and deviations |
| `specs/deferred_items.md` | Ticks the eight-readings item and files one new item (glued glob qualifier) |
| `specs/history.md` | Plan 90 entry with its rulings and deviations |

## The code, step by step

### `_stop_index(words, i, known=None)` (`hooks/readonly-agent-guard.py:781`)

This is the old `_command_words` loop, with three changes:
- It starts at any index `i` and returns an **index** rather than a slice. `len(words)` means there is
  no command, and `None` means env `-S` hides it.
- The `None` from `_skip_prefix_utility` now `break`s rather than returning early, so the memo below
  also records it. `min(i, len(words))` clamps a `repeat` or a prefix option that steps past the end.
- It takes an optional memo `known`, which maps `(position, word text)` to where the walk from that
  loop head stops. A head already in the memo ends the walk at once. Every head the walk passed is
  stored when it ends. Called without `known`, it behaves like the old function.

### `_command_starts(words)` (`:822`): a generator of candidates

It yields today's candidate **first** and unchanged, then the extra ones. A worklist holds
continuations `(start, seq)`. For each one it computes the stop index `k` and yields `seq[k:]`. Then,
depending on the stop word, it queues more continuations:

| Stop word | Also continue from |
|---|---|
| `{` | `k + 1` |
| `[[` | the word after **each** later `]]`, quoted or not |
| contains `=` | `k + 1` (an assignment that `ASSIGNMENT` doesn't match, or an `env` operand) |
| starts with `=` | the same position, with **all** leading `=` stripped (D6), unless nothing is left (zsh `=cmd`) |

Three structures keep this bounded:
1. `visited`, keyed on (stop position, stop word): each stop word is yielded and expanded once. This
   bounds the **candidates**. Without it, a run of `==` words or a chain of `[[ … ]]` doubles the work
   at each word.
2. `queued`, keyed on (start position, word there): a repeat continuation is dropped before it is
   walked.
3. `continued_past`, plus the shared `known` memo: a `[[` scan stops at a `]]` that an earlier scan
   already went past, and runs of skipped words (`repeat`, prefix-utility options) are walked only
   once. Together these bound the **work** to linear.

These are sound because every continuation either starts later or shortens only the word at its
start, so the words after the start never differ across `seq`s. A (position, word) key therefore
fixes the rest of the walk. I checked this reasoning against the code and found nothing wrong.

### `_classify_subcommand(tokens)` (`:896`)

It loops over `_command_starts(...)`. `None` returns `ENV_SPLIT_STRING`, `[]` is skipped, and every
other candidate goes to `_classify_git` / `_classify_non_git` as before. The first denial wins. On
the 65th candidate it returns a fail-closed reason that asks for shorter commands.

Nothing else in the guard changes: tokenizer, `_split_tokens`, `READINGS`, classifiers and
constants are all as before. The only callers of the old `_command_words` were here and in the tests.

## Why it can't allow something `main` denies

Today's candidate is always yielded first and unchanged. Readings, splitting and classifiers are
untouched, and the walk only **adds** candidates. The cap only adds denials. So the set of denied
commands can only grow. The plan also checked this empirically: the old and new guards were run
over every test-file command, every README command and a corpus of 150,024 unique transcript
commands. 0 commands went from denied to allowed (repeated after D6 over 152,235 inputs).

## Behaviour you'll notice

- **Newly denied:** the 8 recorded lines (`COMMAND_START_BYPASSES` in the test file). By class: a
  leading brace group (2), a leading `[[ … ]]` test (1), a leading `=` (1), a word containing `=` (4).
- **New false positives (accepted by you as D2/D5):** a word at the start of a command that is `{`,
  `[[`, contains `=`, or begins with `=` makes the next word get classified too. The README's example
  is an AsciiDoc heading like `== rm and mv ==` inside a heredoc, which is now denied. A subcommand
  with >64 candidate starts is also denied. The sweep found **0** false positives in the corpus, and
  its maximum was 13 candidates in a subcommand.
- **Denial text can change** on lines that were already denied, because an earlier candidate may now
  deny first. They are still denied (spec designer's call 5).
- **Still not caught:** the glued glob qualifier (`git(.) stash`, which needs `BARE_GLOB_QUAL`). It is
  filed as a new deferred item, since the obvious fix would deny `print(git(x))` heredoc text.

## How it got here (rulings during execution)

- **D1:** you approved the plan as written. **D2:** you accepted the walk's false-positive class.
- **D3/D4:** Task 3 found quadratic slowdown on long crafted lines (up to ~20 s, and 159 s for one
  80 KB read-only line). You chose "fix it now" and "dedupe + cap". This added `queued`, the scan
  stop, the `known` memo (`1607648`) and the 64 cap (`a672942`). **D5:** you accepted the cap's
  false-positive class.
- **D6:** the final review found that a long `=` rule in a heredoc (≥63 `=`) hit the cap, because the
  strip removed one `=` at a time. You chose "strip all = at once" (`a9773f2`).
- Timing after the fix: 11 crafted shapes up to 480 KB (not the planned 512 KB). The slowest took
  1.97 s and all grew linearly. The slowest real corpus command took 32 ms.

## What I checked myself

- `uv run python build/run_suites.py hooks` ran **461 passed** and "suite runs passed".
- `/usr/bin/python3` (3.9.6) `-m pytest hooks/test_readonly_agent_guard.py` ran **304 passed**.
- Codex review files exist for `d622a11` and for HEAD `d51bf64` in `/tmp/codex-review/`. Both say
  "no actionable defect". Neither Codex run could run the full suite in its read-only sandbox. The
  plan planned **one** Codex round, and there were two (the second after D6). The plan's
  `## Decisions` doesn't log a Codex outcome, which makes sense because nothing was found.

## Things worth knowing before you merge

1. **It goes live on merge.** `~/.claude/hooks/readonly-agent-guard.py` symlinks into the main
   checkout, so every repo's read-only agents get the new walk at once.
2. **Gate B is still to do:** after merging, run `./hooks/probe-readonly-guard.sh` in the main
   checkout. It should exit 0 with three `ok:` lines. It spawns `claude -p` runs.
3. **`queued` is untested after D6.** Removing it alone fails no test, because the other bounds cover
   every biting shape. It was kept on purpose, since the spec requires it and it is cheap. You can
   ask to drop it later (recorded in `specs/history.md`).
4. **The work test uses `sys.settrace`** to count line events, not wall time. It is deterministic
   across interpreters, but it is sensitive to future refactors of the guard's internals (it counts
   lines of guard code, and the threshold is "<3× when the input doubles").
5. **Open follow-ups:** besides the new glued-qualifier deferred item, there are none.
