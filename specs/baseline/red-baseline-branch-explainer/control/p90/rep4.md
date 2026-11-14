# Explainer: `84efc992..HEAD` (plan 90, read-only guard command-start walk)

## In one paragraph

The read-only agent guard (`hooks/readonly-agent-guard.py`) used to find a subcommand's
command word in one pass. It skipped leading keywords, `X=1` assignments and prefix
utilities (`env`, `time`, …), then took the first word left as "the command". Some words
can either lead the command or be the command. When the guard took the wrong reading,
the real command went unread and could get through: `{ git branch ]] HEAD; }`, `=rm x`,
`arr[1]=x rm t`, `env a-b=x rm t`. This branch now reads each of those words **both
ways** and denies the line if either reading denies. The cost is a small, documented
class of new false positives. It also adds a bound on the walk's work and a fail-closed
cap of 64 places where a command may start, so a crafted line can't make the hook time
out. A hook that times out lets the call go on. The change is live everywhere as soon
as it merges, because `~/.claude/hooks/readonly-agent-guard.py` is a symlink into the
main checkout.

## Shape of the range

- 24 commits. `main` (= `84efc992`) is an ancestor, so the merge is a fast-forward.
- 7 files, +1262/−37. Only three of them hold code or user docs:
  - `hooks/readonly-agent-guard.py`: +123/−19 (the substance)
  - `hooks/test_readonly_agent_guard.py`: +148
  - `hooks/README.md`: behaviour notes, "Not caught" list, false-positive list
- The rest is process records: the spec (now in `specs/completed/`), plan 90 (now
  retired in `specs/plans/completed/`), a `history.md` entry, and `deferred_items.md`
  (one item closed, one filed).

Commit arc: spec designed and approved (`51ed5c01`…`8464d1fe`), then the plan approved
(`55276cb4`, `04f7a614`). Next came the core fix `c97eb24b` and its README entry
`8468bbc8`. Your rulings at the gates added a work bound and cap (`a6729427`), a memo for
the skip walk (`16076481`), and the one-step `=` strip (`a9773f22`). The plan was then
retired (`d51bf645`).

## The code change

### `_command_words` → `_stop_index` + `_command_starts`

- **`_stop_index(words, i, known=None)`** is the old skip loop. It now returns an
  index, not a slice, so it can start from any position. The optional `known` dict
  memoises "from loop head (position, word text), the walk stops at X". The memo is
  sound because, within one call of `_command_starts`, two sequences differ only at or
  before a continuation's start. So the position plus that word's text settle the rest
  of the walk. It also clamps an index that steps past the end (`repeat`, or a prefix
  option missing its value) with `min(i, len(words))`.

- **`_command_starts(words)`** is a generator over candidate command starts. The
  **first candidate is always exactly what the old code produced**, and the tests pin
  this (`test_command_starts_yield_todays_candidate_first`). After it yields a candidate
  whose first word is the stop word `w`, it queues more walks:

  | Stop word | Also continue from |
  |---|---|
  | `{` | the next word |
  | `[[` | the word after each later `]]` (quoted or not) |
  | contains `=` (an assignment that `ASSIGNMENT` doesn't match, or an `env` operand) | the next word |
  | starts with `=` (zsh `=cmd` path expansion) | the same position, with **all** leading `=` stripped (skipped if nothing is left) |

  Three dedup structures bound the work:
  - `queued`: a continuation is queued once per (start, word).
  - `visited`: a stop is yielded once per (position, word).
  - `continued_past`: a `[[` scan stops at a `]]` that an earlier scan already
    covered, so a chain of `[[ a ]]` is linear, not quadratic.

  A candidate of `None` still means that `env -S` hides the command.

- **`_classify_subcommand`** loops over the candidates and returns the first denial.
  An empty candidate (no command) is skipped, not returned as "allow". **From the
  65th candidate on it denies** with "more than 64 places where its command may start".

### Why it can't allow something that `main` denies

The first candidate equals the old one, and the classifiers are unchanged, so every
old denial still happens. The new candidates and the cap can only add denials. The
spec's §3 makes this argument, and the plan's sweep checked it on real commands (0
denial flips).

## Behaviour, old vs new (I ran these)

| Line | `main` | branch |
|---|---|---|
| `{ git branch ]] HEAD; }` | allowed | **denied** |
| `=rm x` | allowed | **denied** |
| `arr[1]=x rm t` | allowed | **denied** |
| `env a-b=x rm t` | allowed | **denied** |
| `{ ` × 64 + `git log` | allowed | **denied** (cap) |
| heredoc line `== rm and mv ==` | allowed | **denied** (accepted false positive) |
| `git log`, `FOO=bar git status`, `git log --format=%H \| head`, heredoc `x = rm` | allowed | allowed |

Timing on crafted lines: 20,000 chained `[[ a ]]` (160 KB) took 0.5 s. 50,000 `==`
words (150 KB) took 0.26 s. Both are linear. The plan's history notes the slowest of 11
shapes at 480 KB took 1.97 s.

## Tests

The tests added (+148) cover:
- The 8 recorded bypasses, now denied.
- 10 read-only lines that must still pass: the same constructs with read-only
  commands, `{ command -v rm; }`, redirections only, heredoc underlines, AsciiDoc
  headings, and a read-only `<(…)`.
- Candidate order, the continuations for each table row, and `env -S` reached through
  a continuation.
- The cap's boundary: 63 `{` pass, 64 deny.
- Long `=` text in a heredoc (an 80-char rule, an RST table border), which must not hit
  the cap.
- **Linear-work tests.** These count Python line events with `sys.settrace` on inputs
  of 64 and 128 words and assert that the count grows less than 3× for three shapes.

I ran the whole file: **304 passed** on Python 3.9 (the guard's floor) and on 3.13.

## What you're accepting

1. **New false positives (documented in the README).** A word at the start of a
   command that contains `=`, starts with `=`, or is `{` or `[[` makes the guard also
   classify the word after it. That holds even where zsh would run the first word, and
   in heredoc text the guard reads as commands. For example, an AsciiDoc `== rm and mv
   ==` heading is denied. You accepted this (D2). The sweep found 0 false positives in
   150,024 unique commands.
2. **The 64-candidate cap.** Any subcommand with more than 64 candidate starts is
   denied, even if every reading is harmless. You accepted this (D5). The sweep's
   maximum was 13. D6 (strip every leading `=` in one step) was added after review
   found that a long `====` heredoc line would hit the cap.
3. **Code that no test checks.** After D6, the `queued` set no longer has a test that
   fails when it's removed. The memo and the `]]` scan stop now carry the linear bound.
   The plan's final ruling kept it because the spec requires it and it's cheap. If you
   want it gone, that's a follow-up.
4. **Still not caught.** A glob qualifier glued to the command word (`git(.) stash`)
   stays in the README's "Not caught" list. It's filed as a new deferred item (size:
   design), because the obvious fix would deny `print(git(x))` in heredocs. Commands
   built by expansion (`$c x`, `$(which rm) x`) and backticks are also still not caught.

## Things worth a glance when reviewing

- The memo's key is `(i, str(words[i]))`, which ignores the token's
  quoted/spaced/expands flags. That's safe only because the one rewrite (the `=` strip)
  keeps those flags and is the only way a word at a given position can change within a
  walk. The docstring states this invariant. Keep it in mind if you add another rewrite
  row later.
- The cap counts every candidate, empty ones included. So "64 places" means 64
  candidates yielded, not 64 commands classified.
- `_command_words` is gone. No Python file in the repository refers to it any more.
- The README reflows a paragraph about redirections. The text doesn't change there,
  only the line breaks, so that part of the diff is noise.

## Bottom line

This is a narrow, well-tested change, and it can only add denials. It closes the 8
recorded lines of the eight-readings backlog item. The glued glob qualifier, the item's
one remaining example, stays open. It costs a small set of accepted false positives and a fail-closed cap. The
work stays linear on the crafted inputs I tried. Merging puts it live for every
repository through the hook symlink.
