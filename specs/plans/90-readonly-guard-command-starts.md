# Read-only Guard Command Starts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The read-only guard looks for a subcommand's command at every plausible start. It then denies the 8 recorded lines in the spec's first three classes, and nothing that `d79b1fb` denies becomes allowed.

**Architecture:** Only the walk that finds the command word changes. `_command_words`, which returns one start, becomes `_stop_index` (today's skip loop, from any position) and a generator `_command_starts`. The generator yields today's candidate first. Then it continues past each stop word that matches a row of the spec's table (§1), and a visited set keyed on the stop word bounds it. `_classify_subcommand` classifies every candidate and returns the first denial. The tokenizer, `_split_tokens`, `READINGS` and the classifiers do not change.

**Tech Stack:** Python, stdlib only, 3.9-compatible (the guard); pytest (the tests); zsh (the Bash tool's shell).

**Spec:** `specs/readonly-guard-command-starts.md` (APPROVED 2026-11-11).

## Global Constraints

- **Anchors.** Line numbers are as of `d79b1fb`. `hooks/` has not changed from `d79b1fb` to this plan's commit. The old text in each step is the match key, not the line number.
- **The 3.9 floor.** The guard stays stdlib only and 3.9-compatible: no `match`, annotations deferred (module docstring, `hooks/readonly-agent-guard.py:15-17`). Its functions carry no annotations, so the new ones carry none. The test file stays 3.9-compatible too.
- **Scope fence.** In `hooks/readonly-agent-guard.py`, only `_command_words` and `_classify_subcommand` change (`:781-814`). The tokenizer, `_split_tokens`, `READINGS`, `_skip_prefix_utility`, `_without_redirections`, the git and non-git classifiers and every module constant stay byte-identical. Do not add `{` or `[[` to `LEADING_KEYWORDS`: a word that may lead the command is read both ways, never skipped.
- **Existing tests.** Every existing test in `hooks/test_readonly_agent_guard.py` passes unedited. If one fails, stop and report it as a deviation (spec §5), and never edit it to pass. A planning prototype of Task 1 passed all of them on both interpreters, the text-asserting tests included.
- **Bypass lines.** The test file gains the 8 recorded lines of Task 1 and no other bypass construction (spec §5).
- **Chat hygiene.** Report bypass findings by class and count only. The constructions stay in files: the test file, `/tmp/codex-review/`, and the scratch outputs. Never restate one in chat, a report, a progress ledger or a commit message.
- **Public repository.** The transcript corpus and the sweep outputs hold other repositories' commands. They stay in `~/.cache/agent-skills/scratch/plan90-work/` and are never committed.
- **Reviewers.** code-reviewer and task-reviewer are guarded agents. Brief each one for plan conformance and code quality only. Never ask either to hunt bypasses or to run a candidate bypass line. Codex is the only seat that hunts bypasses (Final review, below).
- **Live on merge.** `~/.claude/hooks/readonly-agent-guard.py` is a symlink into the main checkout, `/Users/lowell/Projects/agent-skills`. The change goes live in every repository when it merges there.
- **Suites and gates.** Run the tests with `uv run python build/run_suites.py hooks` from the repo root. It runs the hooks suite under the dev Python and under `/usr/bin/python3` (the 3.9 floor), and passes arguments after `--` to pytest in both runs. Before each commit, `bash build/run_commit_lints.sh` prints `commit lints passed`. Commit messages follow Conventional Commits, use plain technical English, and end with the executing session's attribution trailer, written below as `<the session's trailer>`.
- **Shell.** The Bash tool runs zsh. Use `/usr/bin/grep` for sweeps. Never `cd` in a step. Use absolute paths, or `uv run --directory <dir>`.
- **Who runs a task.** Tasks 1 and 2 go to implementer subagents. Task 3 is **(controller)**: it reads local transcripts and ends at an owner gate.
- **Order.** Run one plan execution at a time. `entry_check.py` found no file that this plan shares with plan 89.
- **Final review (spec Verification 7).** subagent-driven-development's final review runs code-reviewer, briefed as above. The controller runs the Codex seat once, with requesting-code-review's `codex-review.md` recipe, after Task 3. If Codex finds mutating lines outside the recorded set, report them by class and severity only, with a pointer to `/tmp/codex-review/<short-HEAD>.md`. Then **STOP, owner**: the owner picks fix, record or stop. Do not start a second Codex round by default. Log the pick as a decision in `## Decisions`. After any later change to the walk, rerun Task 3's Steps 3 to 5 and report the new counts.
- **Completion.** The plan-completion protocol ticks the item that begins "Each of the eight readings holds for a whole line" (`specs/deferred_items.md`, section `readonly-guard-leading-token-bypasses`) with `→ done <date>`. The note records the 8 lines closed, by class and count. It also records the 2 that `d67f856` closed earlier, the glued qualifier left under "Not caught" by the spec's approval, and Task 3's false-positive count with the owner's ruling. The spec retires with the plan. After finishing-a-development-branch merges the branch into `main` in the main checkout, run Gate B there (spec Verification 6): `./hooks/probe-readonly-guard.sh` exits 0 and prints three `ok:` lines. It spawns `claude -p` runs.

## Review Focus

1. Each new denial names the mutator that the walk found, so the controller of a denied agent reads a real reason. `test_command_start_bypasses_are_denied` asserts `` `rm` `` or `` `git branch `` in each reason (Task 1).
2. A continued branch that reaches env's `-S` denies with `ENV_SPLIT_STRING`, as today's candidate does (spec §1): `test_command_starts_reaching_env_s_fail_closed` (Task 1).
3. A continued branch that reaches `command -v` or `-V` runs nothing, so a brace group that only describes a command stays allowed: the `branch-reaches-command-v` allow case (Task 1).
4. A subcommand that its redirections leave empty yields one empty candidate and raises nothing. A raise would deny it, because `main()` fails closed: the `only-redirections` allow case (Task 1).
5. A heredoc line made only of `=` (a Markdown underline), or one that starts with `=` words before read-only words (AsciiDoc headings), stays allowed: the `heredoc-underline` and `heredoc-asciidoc-headings` allow cases (Task 1).

## Decisions

- **D1** (owner, plan review, 2026-11-11): "Approve as is", in answer to "Approve plan 90 as written?". The plan stands as written, with the builder's calls in it. Those calls are the README exact copy, the 10 allow cases, the bound test at 16 words with a 3× limit, Task 3's class rule and its split by guarded agent, and README inputs from both versions. Applied in: Tasks 1 to 3, Global Constraints.
- **D2** (owner, execution, 2026-11-11): "Accept as is", in answer to "Do you accept the walk's false-positive class as the README records it?". The corpus sweep found 0 false positives in 150,024 unique commands, so the accepted class is the one that the README records. Applied in: Task 3.
- **D3** (owner, execution, 2026-11-11): "Fix it now", in answer to "How should the guard's quadratic slowdown on long crafted lines be handled?". The offered fix was a spec amendment and a code task that drop a queued continuation whose start position and word were seen before, then a rerun of Task 3's Steps 3 to 5. Applied in: new tasks.

---

### Task 1: The walk yields every candidate start

**Files:**
- Modify: `hooks/readonly-agent-guard.py:781-814` (`_command_words`, `_classify_subcommand`)
- Test: `hooks/test_readonly_agent_guard.py` (new lists and tests after `test_the_dash_modifier_leads_a_command_like_a_keyword`, `:606-608`)

**Interfaces:**
- Consumes: `_skip_prefix_utility(words, i)`, `_without_redirections(tokens)`, `_command_name(word)`, `_classify_git(args)`, `_classify_non_git(name, args)`, `_Token`, `ENV_SPLIT_STRING`, all unchanged.
- Produces:
  - `_stop_index(words, i)` returns the index where the command starts when the walk begins at `words[i]`: an `int` in `[i, len(words)]`, or `None` where env's `-S` hides the command.
  - `_command_starts(words)` is a generator. It yields one candidate for each stop word visited: a `list` of `_Token` (`[]` when there is no command), or `None` where env's `-S` hides the command. The first yield is today's candidate, unchanged.
  - `_classify_subcommand(tokens)` keeps its signature and return values.
  - `_command_words` is deleted. Its only caller is `_classify_subcommand`.

- [ ] **Step 1: Write the failing tests**

Add to `hooks/test_readonly_agent_guard.py`, after `test_the_dash_modifier_leads_a_command_like_a_keyword`:

```python
# The spec's first three classes (specs/readonly-guard-command-starts.md): the
# walk stopped at a word that may lead the command and took that word for the
# command. Seven come from the backlog item, the test line from the README's
# mixed-reading bullet. d79b1fb allowed each.
COMMAND_START_BYPASSES = [
    pytest.param('{ git branch ]] HEAD; }', id='brace-group-before-git'),
    pytest.param('true && { git branch ]] HEAD; }', id='brace-group-after-a-separator'),
    pytest.param('if [[ -n a ]] git branch ]] HEAD', id='test-before-git'),
    pytest.param('=rm x', id='path-expansion'),
    pytest.param('arr[1]=x rm t', id='subscripted-assignment'),
    pytest.param('ä=x rm t', id='non-ascii-assignment'),
    pytest.param('env a-b=x rm t', id='env-operand'),
    pytest.param('env -- a-b=x rm t', id='env-operand-after-dashes'),
]

# The same places with a read-only command, so each row of the walk's table is
# pinned both ways; the edges a branch can reach; and the one must-pass form of
# the backlog item that no other test classifies.
COMMAND_START_ALLOWED = [
    pytest.param('{ git branch --list HEAD; }', id='brace-group'),
    pytest.param('if [[ -n a ]] git branch --list HEAD', id='test'),
    pytest.param('arr[1]=x git log', id='subscripted-assignment'),
    pytest.param('env -- a-b=x git log', id='env-operand'),
    pytest.param('=git log', id='path-expansion'),
    pytest.param('{ command -v rm; }', id='branch-reaches-command-v'),
    pytest.param('2>/dev/null', id='only-redirections'),
    pytest.param('cat <<EOF\nTitle\n=====\nEOF', id='heredoc-underline'),
    pytest.param('cat > /tmp/notes.adoc <<EOF\n= Title\n== Section one\nEOF',
                 id='heredoc-asciidoc-headings'),
    pytest.param('diff <(git show HEAD:f) f', id='read-only-process-substitution'),
]


@pytest.mark.parametrize('command', COMMAND_START_BYPASSES)
def test_command_start_bypasses_are_denied(command):
    reason = guard.classify(command)
    assert reason is not None and ('`rm`' in reason or '`git branch' in reason), reason


@pytest.mark.parametrize('command', COMMAND_START_ALLOWED)
def test_command_start_allow_cases_stay_allowed(command):
    assert guard.classify(command) is None


def _starts(line):
    words = guard.split_subcommands(line, braces=False)[0]
    return [None if s is None else [str(w) for w in s] for s in guard._command_starts(words)]


def test_command_starts_yield_todays_candidate_first():
    assert _starts('X=1 time env -i FOO=1 git log')[0] == ['git', 'log']
    assert _starts('{ git log')[0] == ['{', 'git', 'log']
    assert _starts('if [[ -n a ]] git log')[0] == ['[[', '-n', 'a', ']]', 'git', 'log']
    assert _starts('arr[1]=x git log')[0] == ['arr[1]=x', 'git', 'log']
    assert _starts('=git log')[0] == ['=git', 'log']
    assert _starts('command -v rm')[0] == []
    assert _starts('env -S git log')[0] is None


def test_command_starts_continue_past_each_row():
    for line in ('{ git log', 'if [[ -n a ]] git log', 'arr[1]=x git log',
                 'env -- a-b=x git log', '=git log'):
        assert ['git', 'log'] in _starts(line), line
    # Each later `]]`, quoted or not.
    assert [']]', 'git', 'log'] in _starts("[[ a == ']]' ]] git log")


def test_command_starts_reaching_env_s_fail_closed():
    reason = guard.classify('a-b=x env -S git log')
    assert reason is not None and 'env -S' in reason, reason


def test_command_starts_visit_each_stop_word_once():
    # Unbounded, a run of `==` words or a chain of `[[ … ]]` tests doubles the
    # walk at each word, and a hook that times out lets the call go on.
    for line in ('== ' * 16 + 'git log', '[[ a ]] ' * 16 + 'git log'):
        words = guard.split_subcommands(line, braces=False)[0]
        starts = list(guard._command_starts(words))
        assert len(starts) <= 3 * len(words), (line, len(starts))
        assert ['git', 'log'] in starts, line
```

- [ ] **Step 2: Run the new tests against `d79b1fb`'s guard to verify they fail (spec Verification 1)**

Run: `git diff --quiet d79b1fb -- hooks/readonly-agent-guard.py && echo same` (it prints `same`), then `uv run python build/run_suites.py hooks -- -k command_start`.
Expected in each of the two runs: `12 failed, 10 passed`. The controller reconciles these counts from its own run, not from a report:
- `test_command_start_bypasses_are_denied`: all 8 fail with `AssertionError: None`.
- `test_command_starts_reaching_env_s_fail_closed`: fails with `AssertionError: None`.
- The other three `test_command_starts_*` tests fail with `AttributeError` (there is no `_command_starts`).
- The 10 allow cases pass.

- [ ] **Step 3: Implement `_stop_index(words, i)`, `_command_starts(words)` and the new `_classify_subcommand(tokens)` in `hooks/readonly-agent-guard.py`**

- `_stop_index(words, i)` is today's loop in `_command_words`, started at `i`. Its docstring takes over the list of what the loop skips. It returns `min(i, len(words))`, because `repeat` or a prefix option with no value can step past the end. It returns `None` where `_skip_prefix_utility` does.
- `_command_starts(words)` follows these rules. The generator's shape is the builder's choice, within them.
  1. A *continuation* is a pair `(start, seq)`: a position and the word list to walk from it. The first is `(0, list(words))`. Walk it first, so that the first yield is today's candidate.
  2. Walk a continuation with `k = _stop_index(seq, start)`. If `k` is `None`, yield `None` and take the next continuation.
  3. The visited set is keyed on the stop word's position and text: `(k, str(seq[k]))`, or `(k, None)` when `k == len(seq)` (spec §1). If the key is already in the set, drop the continuation. Otherwise add the key and yield `seq[k:]`. Then, for `stop = seq[k]`, add a continuation for each row that matches. Each row matches on the word's text, quoted or not:

     | `stop` | Continuation |
     |---|---|
     | `== '{'` | `(k + 1, seq)` |
     | `== '[['` | `(j + 1, seq)` for each `j > k` where `seq[j] == ']]'` |
     | contains `=` | `(k + 1, seq)` |
     | `.startswith('=')` | `(k, seq')`: `seq'` is a copy of `seq` whose word `k` is `_Token(stop[1:], quoted=stop.quoted, spaced=stop.spaced, expands=stop.expands)` |

     Only the last row copies the list. The others share `seq`. Every continuation starts at a later word or shortens the word at `k`, so the words after the key's position never differ, and the key determines the rest of the walk. The order of the continuations after the first is free.
- `_classify_subcommand(tokens)` takes each candidate of `_command_starts(_without_redirections(tokens))` in turn. For `None`, it returns `ENV_SPLIT_STRING`. It skips `[]`. It classifies any other candidate as today: `git` goes to `_classify_git(words[1:])`, and any other name to `_classify_non_git(name, words[1:])`. It returns the first denial, or `None` when no candidate denies.

- [ ] **Step 4: Run the new tests to verify they pass**

Run: `uv run python build/run_suites.py hooks -- -k command_start`
Expected: `22 passed` in each run.

- [ ] **Step 5: Check that the bound test bites**

Make the visited-set membership check always false, so that no continuation is dropped. Then run `uv run python build/run_suites.py hooks -- -k visit_each_stop_word_once`.
Expected: `1 failed` in each run, with a count of more than 60,000 starts against a bound of 54 or 150. It finishes in seconds. Restore the check. `git diff --stat` then shows only the two files of this task.

- [ ] **Step 6: Run the whole suite**

Run: `uv run python build/run_suites.py hooks`
Expected: each run shows 22 more passed than before this task, and `0 failed`. No existing test was edited. If an existing test fails, stop and report it (Global Constraints, Existing tests).

- [ ] **Step 7: Commit**

Run `bash build/run_commit_lints.sh` (it prints `commit lints passed`), then:

```bash
git add hooks/readonly-agent-guard.py hooks/test_readonly_agent_guard.py
git commit -m "fix(hooks): find the guarded command at every place it can start

The read-only guard's walk took the first word it could not skip as the
command. A word that may lead the command (a leading brace or test, a word
with an equals sign, a leading equals sign) is now read both ways, and a
denial either way stands. A visited set bounds the walk.

<the session's trailer>"
```

### Task 2: The README describes the new walk

**Files:**
- Modify: `hooks/README.md:230-342` (sections "Limitations (by design)", its "Not caught" list and "Known false positives")

**Interfaces:**
- Consumes: Task 1's walk, as built.
- Produces: nothing that code reads.

The spec leaves the wording to the builder. The text below is exact copy. Find each place by its old text, not by line number. Keep the file's line wrapping near 88 columns.

- [ ] **Step 1: Add the walk's new point to the "Limitations (by design)" paragraph**

Insert this text between the sentence on env's `-S` (it ends `which the guard does not read.`) and the sentence that begins `Subshells, brace groups,`. Then rewrap the paragraph:

```markdown
Some words may lead the command or be the command, and the guard reads each such word
both ways. A denial either way stands. These words are a leading `{`, a leading
`[[ … ]]` test, a word that contains `=` (an assignment that the guard does not
recognise, or an operand of `env`), and a word that begins with `=` (zsh's `=cmd` path
expansion).
```

- [ ] **Step 2: Edit the "Not caught" list**

1. Replace this bullet:

   ```markdown
   - A command word the shell produces by expansion (`c=rm; $c x`, `$(which rm) x`), by
     zsh's `=cmd` path expansion (`=rm x`), or by gluing to a brace (zsh runs `{rm x;}`).
   ```

   with:

   ```markdown
   - A command word the shell produces by expansion (`c=rm; $c x`, `$(which rm) x`) or by
     gluing to a brace (zsh runs `{rm x;}`).
   ```
2. Delete the whole bullet that begins `- A word the guard does not recognise as an assignment` (four lines).
3. Replace the whole bullet that begins `- A line that needs the flat reading for one construct` (five lines) with:

   ```markdown
   - A line that needs the flat reading for one construct and the nested reading for
     another. Each of the eight readings below applies to the whole line, so no single
     reading catches both. A brace group or a `[[ … ]]` test that leads a subcommand does
     not hide the command after it, because the guard also reads past it (see above).
   ```
4. Keep the bullet on the glob qualifier glued to the command word as it is.

- [ ] **Step 3: Add the false positive**

Under "Known false positives, accepted rather than widened", after the bullet that begins `- **`time -p rm x` is denied**`, insert:

```markdown
- **A word at the start of a command that contains `=`, begins with `=`, or is `{` or
  `[[` is read both as a prefix and as the command.** So the word after it is classified
  too, even where zsh runs the first word as the command, or where the line is heredoc
  text: an AsciiDoc heading `== rm and mv ==` in a heredoc is denied.
```

- [ ] **Step 4: Verify the edits**

The check collapses whitespace first, so a rewrapped line still matches.

Run: `uv run python -c "import re; t = re.sub(r'\s+', ' ', open('hooks/README.md').read()); print([s in t for s in ('reads each such word both ways', 'read both as a prefix and as the command', 'git(.) stash', 'arr[1]', 'a-b=x', '=rm x', ']] HEAD', 'recognise as an assignment')])"`
Expected: `[True, True, True, False, False, False, False, False]`. The new text and the glued-qualifier bullet are present. The recorded lines and the deleted bullet are gone.

- [ ] **Step 5: Commit**

Run `bash build/run_commit_lints.sh`. It prints `commit lints passed`, its `cc_guide_lint` and `check_conformance` steps included. Then:

```bash
git add hooks/README.md
git commit -m "docs(hooks): describe the guard's command-start walk

The README now says that a word that may lead the command is read both
ways, drops the two 'Not caught' gaps that the walk closes, and records
the false positive that the walk adds.

<the session's trailer>"
```

### Task 3 (controller): No denial lost, and the false-positive sweep

Spec Verification 3 and 4. The scripts are one-off, are written by the controller, and are never committed. Their detail goes to files in `~/.cache/agent-skills/scratch/plan90-work/`, and only counts go to chat.

**Files:**
- Create (scratch, uncommitted): `~/.cache/agent-skills/scratch/plan90-work/{old_guard.py,corpus.py,corpus.jsonl,compare.py,flips.jsonl}`
- Modify: `specs/plans/90-readonly-guard-command-starts.md` (`## Decisions`, Step 6)

**Interfaces:**
- Consumes: the branch's `hooks/readonly-agent-guard.py` (Task 1) and `hooks/README.md` (Task 2). From `d79b1fb`'s guard: `classify`, `_logical_lines`, `_tokenize`, `_physical_line_tokens`, `READINGS`, `_split_tokens`, `_classify_subcommand`, `_without_redirections` and `_command_words`.
- Produces: the owner's ruling on each false positive, logged as a decision.

- [ ] **Step 1: Fetch `d79b1fb`'s guard**

Run: `mkdir -p ~/.cache/agent-skills/scratch/plan90-work && git show d79b1fb:hooks/readonly-agent-guard.py > ~/.cache/agent-skills/scratch/plan90-work/old_guard.py`

- [ ] **Step 2: Build the transcript corpus**

`corpus.py` reads every `tool_use` block named `Bash` from these transcripts:
- `~/.claude/projects/*/*.jsonl`, with population `main`.
- `~/.claude/projects/*/*/subagents/agent-*.jsonl`, with population set to the `agentType` in the sibling `agent-*.meta.json`, or `unknown` where there is none.

It takes each block's `input.command` string and skips lines that are not JSON. It writes one JSON line per unique command text to `corpus.jsonl`, with the populations and project directories that ran it. It prints the number of files, of commands, of unique commands, and of unique commands that a guarded agent ran (a population in `READONLY_AGENTS`).

- [ ] **Step 3: Compare the two guards**

`compare.py` loads `old_guard.py` and the branch's guard with `importlib`. Its inputs come from three sources:
- the corpus;
- every `str` constant in `hooks/test_readonly_agent_guard.py`, found with `ast`;
- every backtick span and every line of every fenced block in `hooks/README.md`, both the branch's file and `d79b1fb`'s (`git show d79b1fb:hooks/README.md`), which still holds the examples that Task 2 removed.

A guard denies an input when `classify` returns a reason or raises, because `main()` fails closed for a guarded agent. The script writes each input whose result differs to `flips.jsonl`, with its source and its corpus metadata. It prints the denied-to-allowed and allowed-to-denied counts for each source. For the corpus, it splits the counts into commands that a guarded agent ran and the others.

Expected:
- `denied→allowed: 0` for every source. Any other count means that the walk dropped today's candidate (spec §3). Stop, report the count only, and fix Task 1 before going on.
- In the test file, allowed→denied is expected for the 8 recorded lines and for the `env -S` branch pin. In the README, it is expected for those recorded lines and for the false-positive example of Task 2. Note any other test-file or README flip for the owner (Step 5).

- [ ] **Step 4: Classify each corpus flip**

Add a `class` to each corpus row of `flips.jsonl`. Use `d79b1fb`'s functions on each of the command's logical lines and physical lines (as `classify` builds them), in each of `READINGS`. Find the first subcommand from `_split_tokens` where the old guard's `_classify_subcommand` returns `None` and the new guard's does not. Its stop word today is `old._command_words(old._without_redirections(subcommand))[0]`. The class is the row of that word, checked in this order:
1. `{` gives `brace`.
2. `[[` gives `test`.
3. A word that begins with `=` gives `leading =`.
4. A word that contains `=` gives `contains =`.

If no subcommand differs, the new guard raised where the old one did not, and the class is `raise`. Print the corpus flip counts by class and population group.

- [ ] **Step 5: STOP, owner — the false positives**

Report in chat, as counts only:
- the corpus size;
- denied→allowed (0);
- allowed→denied, split by class and by population group (a guarded agent, or other).

Point to `flips.jsonl` for the commands themselves. Some flips may come from this repository's earlier sessions that hunted guard bypasses. Those can be true positives, so name their project directory in the count. Ask the owner to accept each false positive or to ask for a narrower rule. A narrower rule changes the spec's table, so it needs a spec amendment task and a new code task. Plan both from the owner's answer before any code changes.

- [ ] **Step 6: Log the ruling**

Add the owner's answer to `## Decisions` as the next decision, `- **D<n>** (owner, execution, <date>): <answer>. Applied in: <Task 3 | new tasks>.`, in the owner's words. Then:

```bash
git add specs/plans/90-readonly-guard-command-starts.md
git commit -m "docs(specs): record the owner's false-positive ruling in plan 90

<the session's trailer>"
```
