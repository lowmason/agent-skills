# Explainer: `84efc992..d51bf645` (plan 90, the read-only guard's command-start walk)

`84efc992` is the current `main`. `HEAD` (`d51bf645`, detached) is 24 commits ahead in a straight
line, with one merge (`04f7a614`) that brings in the approved spec and plan. 7 files change,
+1262 / −37. Most of that is spec and plan text. The code change is about 140 lines in one hook
and about 150 lines of tests.

## What it does in one paragraph

`hooks/readonly-agent-guard.py` is the PreToolUse hook that blocks mutating Bash commands for the
read-only agents. To find a subcommand's command it walks past keywords, assignments and prefix
utilities like `env`/`time`, then takes the first other word as the command. That guess failed in
8 recorded cases: the word where it stopped only *led* the command (a `{`, a `[[ … ]]` test, an
assignment it doesn't recognise such as `arr[1]=x` or `ä=x`, an `env` operand like `a-b=x`, or
zsh's `=rm` path expansion), so the real mutator after it was never checked. Now the walk reads
each such word **both ways**: as the command, and as a prefix it keeps walking past. Every
candidate is classified, and **any denial stands**. The guard can only deny more than before,
never less.

## The code change (`hooks/readonly-agent-guard.py`)

- **`_command_words` → `_stop_index(words, i, known=None)`.** Same skip logic. It now returns
  an index, not a slice, can start at any position, and can use a shared memo (`known`). The memo
  maps `(position, word text)` of each loop head to where the walk from it stops.
- **New `_command_starts(words)`** is a generator that yields each candidate word list (`[]` = no
  command, `None` = env `-S`). It yields today's candidate first. Then it continues from the stop
  word using these rules:

  | Stop word | Also continue from |
  |---|---|
  | `{` | the next word |
  | `[[` | the word after each later `]]`, quoted or not |
  | contains `=` | the next word |
  | starts with `=` | the same position, with all leading `=` stripped (if anything is left) |

- **Bounding the work.** Without bounds this grows exponentially on runs of `==` or chains of
  `[[ ]]`, and quadratically in some other cases. That matters because **a hook that times out lets
  the call through**. The bounds are:
  1. `visited`: each `(stop position, stop word)` is yielded once.
  2. `queued`: each continuation `(start, word)` is queued once.
  3. `continued_past`: the `[[` scan stops at a `]]` that an earlier scan already handled.
  4. `known`: the `_stop_index` memo, for long skipped runs (e.g. `env -u ]]` repeated).
- **`_classify_subcommand`** loops over the candidates and returns the first denial. If a
  subcommand yields **more than 64 candidates** and none of the first 64 denied, it **fails closed**
  with a "split the command" message.

The scope fence held. The tokenizer, splitter, readings, classifiers and constants are untouched.
Only the walk and `_classify_subcommand` changed.

## Behaviour changes you'll notice

- **New denials (intended):** the 8 recorded bypass lines. I checked them myself: all 8 are
  allowed by `main`'s guard and denied by `HEAD`'s.
- **New false-positive classes (owner-accepted, D2 and D5):**
  - A word at the start of a command that contains `=`, starts with `=`, or is `{` or `[[` makes
    the next word get classified too. Example: a heredoc line `== rm and mv ==` (AsciiDoc heading)
    is now denied.
  - More than 64 candidate starts in one subcommand is denied.
  - The plan's sweep of 150,024 unique transcript commands found **0** new false positives, and
    the highest candidate count in one subcommand was 13.
- **Denial text can change** on lines that were already denied, because an earlier candidate may
  deny first. They are still denied (spec, Designer's call 5).
- **Still not caught:** a glob qualifier glued to the command word (`git(.) stash`). It's out of
  scope by the spec and filed as a new deferred item. The other expansion forms (`$c x`, `{rm x;}`)
  are also still not caught.

## Tests (`hooks/test_readonly_agent_guard.py`)

- The 8 bypasses are each denied, and the reason names `rm` or `git branch`.
- 10 allow cases: each table row with a read-only command, plus `command -v`, redirection-only,
  heredoc `=====` underlines, AsciiDoc headings, and a process substitution.
- Unit tests on `_command_starts`: the first candidate is unchanged, each row continues, and env
  `-S` reached through a continuation still fails closed.
- A bound test: candidates ≤ 3 × word count on `== ×16` and `[[ a ]] ×16`.
- A **work-growth test** that counts traced line events in guard code at n=64 and n=128 and
  asserts the ratio is < 3, so the work grows linearly, not quadratically. It covers three shapes.
- Cap boundary: 64 `{` is allowed, 65 is denied with the cap message.
- Heredoc `=` text (80-char rule, rST table border, long `=` prefix) stays allowed, and stripping
  the leading `=` adds one candidate.
- No existing test was edited.

**I ran `uv run python build/run_suites.py hooks`: 461 passed, and the dev Python and
`/usr/bin/python3` (the 3.9 floor) both passed.**

## Docs and bookkeeping

- `hooks/README.md`: describes the both-ways reading, removes the now-closed examples from "Not
  caught", and adds the two false-positive bullets. Part of the diff is only line reflow.
- `specs/deferred_items.md`: ticks the "eight readings" item, which closes 8 lines, and adds one
  new item for the glued glob qualifier.
- `specs/history.md`: the plan-90 entry, with rulings D3, D4 and D6 and the deviations.
- The spec and the plan move to `completed/`.

## Things worth your attention before merging

1. **It goes live on merge.** `~/.claude/hooks/readonly-agent-guard.py` is a symlink into the main
   checkout, so every repository picks this up as soon as it lands. Gate B
   (`./hooks/probe-readonly-guard.sh`, three `ok:` lines) only runs after the merge, as the plan
   intends. Remember to run it.
2. **I found no record of the Codex bypass-hunting round.** The plan's Global Constraints require
   one Codex round after Task 3. Its result would be logged as a decision if it found anything. The
   plan's Decisions and `specs/history.md` mention no Codex outcome, and the only file in
   `/tmp/codex-review/` refers to `f7b8af5`, which isn't a commit in this repo. The round may have
   run and found nothing, but I couldn't confirm it from the branch. Check this if you care about
   that gate.
3. **`queued` has no test that fails without it** (Review Focus 8). After D6 it no longer bounds
   any class that the tests exercise. It was kept on purpose because the spec requires it and it's
   cheap (recorded in `history.md`). You can drop it later if you prefer.
4. **The memo's correctness depends on an invariant.** `known` and `queued` are keyed by
   `(position, word text)` and shared across continuations whose word lists differ. That is sound
   only because a continuation changes its list only at its own start position (the `=` strip) and
   never looks backward. If anyone later adds a row that edits an earlier word, or
   `_skip_prefix_utility` starts looking behind `i`, the memo would go silently wrong. The docstrings
   say this, but nothing enforces it.
5. **The `[[` rule is deliberately loose.** It continues after *every* later `]]`, quoted ones
   included, not just the one zsh would use. That only adds denials and is the source of the
   accepted false-positive class.

## Bottom line

This is a small, additive change to the code, and it is well tested. It can only add denials, and
the extra cost is bounded and tested to grow linearly. The 8 target bypasses are closed (verified).
The suite passes on both interpreters. The new false positives are documented and were 0 in the
transcript corpus. Before merging, check that the Codex round happened, and run Gate B after the
merge.
