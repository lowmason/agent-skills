# Read-only Guard Glued Qualifier and Git Config Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The read-only guard reads a word glued to a glob group as a command, and it checks git's `-c` and `--config-env` keys, `--exec-path=`, and the assignments that git reads against allowlists. Nothing that `8131b81` denies becomes allowed.

**Architecture:** Item 1 changes only the group placeholder (`_group_word`) and adds one continuation to `_command_starts`. Item 2 adds four allowlist constants and three checks: `-c` and `--config-env` keys in `_locate_git_verb`, assignments before git in `_classify_subcommand`, and assignments that last past one command (standalone, and in `export` and its kin). `_command_starts` keeps its output, so a new inner generator gives `_classify_subcommand` the words before the command. A controller sweep over local transcripts then confirms the lists and ends at an owner gate.

**Tech Stack:** Python, stdlib only, 3.9-compatible (the guard); pytest (the tests); zsh (the Bash tool's shell).

**Spec:** `specs/readonly-guard-glued-qualifier-and-git-config.md` (APPROVED 2026-11-28).

## Global Constraints

- **Anchors.** Line numbers are as of `8131b81`. `hooks/` has not changed from `8131b81` to this plan's commit. The old text in each step is the match key, not the line number.
- **The 3.9 floor.** The guard stays stdlib only and 3.9-compatible: no `match`, annotations deferred (`hooks/readonly-agent-guard.py:15-17`). Its functions carry no annotations, so the new ones carry none. The test file stays 3.9-compatible too.
- **Scope fence.** The tokenizer, `_split_tokens`, `READINGS`, `_stop_index`, `_skip_prefix_utility` and `_without_redirections` stay byte-identical (spec Non-goals). No existing check or reading is removed (spec Anti-goals).
- **Existing tests.** Every existing test in `hooks/test_readonly_agent_guard.py` passes unedited, and every existing denial reason stays the same text. If one fails, stop and report it as a deviation. Never edit it to pass.
- **Check order.** In `_classify_subcommand`, a git candidate runs `_classify_git` first and the assignment check only when that returns `None`, so every reason that `8131b81` gives stays the same (`test_…:367` asserts `git stash` in one).
- **Denial text.** Each new denial names the key or the variable, says the guard allows only listed ones, and points to `hooks/README.md` (spec §2a). It never echoes the value.
- **Chat hygiene.** Report bypass findings by class and count only. Constructions stay in the test file, `/tmp/codex-review/` and the scratch outputs. Never restate one in chat, a report, a progress ledger or a commit message.
- **Public repository.** The transcript corpus and the sweep outputs hold other repositories' commands. They stay in `~/.cache/agent-skills/scratch/plan121-work/` and are never committed. The allowlists name keys, variables and harmless fixed values only, never a path from a transcript.
- **Reviewers.** code-reviewer and task-reviewer are guarded agents. Brief each one for plan conformance and code quality only. Never ask either to hunt bypasses or to run a candidate bypass line. Codex is the only seat that hunts bypasses (Final review, below).
- **Live on merge.** `~/.claude/hooks/readonly-agent-guard.py` is a symlink into the main checkout. The change goes live in every repository when it merges there.
- **Suites and gates.** Run the tests with `uv run python build/run_suites.py hooks` from the repo root. It runs the hooks suite under the dev Python and under `/usr/bin/python3` (the 3.9 floor), and passes arguments after `--` to pytest in both runs. Before each commit, `bash build/run_commit_lints.sh` prints `commit lints passed`. Commit messages follow Conventional Commits and the plain technical English rule.
- **Shell.** The Bash tool runs zsh. Use `/usr/bin/grep` for sweeps. Never `cd` in a step. Use absolute paths, or `uv run --directory <dir>`.
- **Who runs a task.** Tasks 1 to 5 go to implementer subagents, in order: Tasks 2 to 4 edit the same functions. Task 6 is **(controller)**: it reads local transcripts and ends at an owner gate.
- **Final review.** subagent-driven-development's final review runs code-reviewer, briefed as above. The controller runs the Codex seat once, with requesting-code-review's `codex-review.md` recipe, after Task 6. If Codex finds a mutating form that passes, report it by class and severity only, with a pointer to `/tmp/codex-review/<short-HEAD>.md`. Then **STOP, owner**: the owner picks fix, record or stop. Log the pick in `## Decisions`. After any later change to the guard, rerun Task 6's Steps 2 to 4.
- **Item 1's new denials are git's and sed's only.** On `8131b81` the flat reading already makes a word glued to `(` a subcommand of its own, so `rm(.) x` and `rm(path)` are denied today. Only the two checks that read arguments can deny more: `_classify_git` and `_sed_edits_in_place`. So item 1 adds denials only where the glued word is `git` or `sed` and the words after the group form a denied git command or an in-place `sed`. The spec's §1 example of the false-positive class ("a Python line that calls a function named `rm`") is therefore not new; Task 5 Step 0 amends it (D2).
- **Completion.** The plan-completion protocol ticks both backlog items with `→ done <date>`: "A glob qualifier glued to the command word still hides the command from the read-only guard" (section `90-readonly-guard-command-starts — 2026-11-12`) and "Allowlisted git verbs can run a program through configuration or the environment" (section `readonly-guard-leading-token-bypasses`).

## Review Focus

1. A program-taking key given with no `=` means boolean true to git, so `git -c core.fsmonitor status` must deny (no listed value matches a missing one): `test_config_key_without_a_value` (Task 2).
2. git compares a key's section and name in any case, so `core.Pager` and `CORE.PAGER` must meet the same check as `core.pager`, while a subsection keeps its case: `test_config_key_case` (Task 2).
3. A quoted value, or one with a space, must be compared as the one word zsh passes: `GIT_PAGER='cat'` passes, `-c 'core.pager=cat -R'` denies: `test_quoted_config_values` (Task 2) and `test_quoted_assignment_values` (Task 3).
4. An assignment reached through a prefix utility (`time env NAME=… git diff`, `env -i NAME=… git log`) must meet the same check as a bare one: `test_assignments_through_prefix_utilities` (Task 3).
5. A glued group after a prefix or a separator (`env git(.) stash`, `true && git(.) stash`), and a glued git with an unlisted assignment before it, must deny: `test_glued_word_after_a_prefix` (Task 1) and `test_glued_git_with_an_assignment_before_it` (Task 3).

## Decisions

- **D1** (owner, plan review, 2026-11-28): "Plan needs to be 121.", where `entry_check.py` printed `next free: 117`. Applied in: the plan's file name and every path to it.
- **D2** (owner, plan review, 2026-11-28): "Approve with amendment", in answer to "Approve plan 121, with the §1 spec amendment in Task 5 Step 0?". The plan stands as written, and Task 5 Step 0 runs. Applied in: Task 5 (spec amendment).

---

### Task 1: The group placeholder carries the glued word (spec §1)

**Files:**
- Modify: `hooks/readonly-agent-guard.py` (`_Token`, `:65-83`; `_group_word`, `:473-492`; `_command_starts`, `:822-893`)
- Test: `hooks/test_readonly_agent_guard.py` (new tests after `test_command_starts_continue_past_each_row`, `:671`)

**Interfaces:**
- Consumes: `_split_tokens`, `split_subcommands`, `_command_starts`, `classify`, all as on `8131b81`.
- Produces:
  - `_Token(text, syntax=False, quoted=False, spaced=False, expands=False, glued=None)`. `glued` is the `_Token` a group placeholder took the place of, or `None`. Every existing token has `glued is None`.
  - `_group_word(current, paren)` returns `_Token('()', expands=True, glued=before)`, a new token for each group, where it pops a glued plain word (the `current.pop()` at `:487`). Every other return is as today, `GROUP_WORD` included.
  - `_command_starts(words)` yields what it yields today, plus one more candidate for each stop word `stop` with `stop.glued is not None`: it queues `(k, seq[:k] + [stop.glued] + seq[k + 1:])`, like the `=` strip.

- [ ] **Step 1: Write the failing tests**

```python
# Spec §1: a glob group glued to a word where a command can start. zsh with
# BARE_GLOB_QUAL makes `git(.)` the word git when a file named git exists.
# Only a glued git or sed is new: the flat reading already denies `rm(.) x`
# on 8131b81, since it makes `rm` a subcommand of its own.
def test_glued_qualifier_on_the_command_word_is_denied():
    for line in ('git(.) stash', '/usr/bin/git(.) stash', 'sed(.) -i s/a/b/ f'):
        assert guard.classify(line) is not None, line


def test_glued_word_after_a_prefix():
    for line in ('env git(.) stash', 'true && git(.) stash', 'time git(.) stash'):
        assert guard.classify(line) is not None, line


def test_glued_qualifier_lines_the_readme_allows_stay_allowed():
    for line in ('print(git(x))', 'ls *(.)', 'ls (#i)readme*',
                 "cat <<'EOF'\nprint(git(x))\nEOF"):
        assert guard.classify(line) is None, line


def test_glued_placeholder_carries_its_word():
    words = guard.split_subcommands('git(.) stash', braces=False)
    placeholder = next(w for s in words for w in s if w == '()')
    assert str(placeholder.glued) == 'git'
    assert guard.GROUP_WORD.glued is None
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run python build/run_suites.py hooks -- -k "glued"`
Expected: `test_glued_qualifier_on_the_command_word_is_denied`, `test_glued_word_after_a_prefix` and `test_glued_placeholder_carries_its_word` FAIL; `test_glued_qualifier_lines_the_readme_allows_stay_allowed` PASSES (it pins today's behavior).

- [ ] **Step 3: Implement the three changes in `hooks/readonly-agent-guard.py`**

Add the `glued` keyword to `_Token.__new__` and its docstring. In `_group_word`, return the carrying token only on the glued-plain-word branch. In `_command_starts`, add the continuation after the `=` strip, and add one sentence on it to the docstring's list of continuations.

- [ ] **Step 4: Run the whole suite**

Run: `uv run python build/run_suites.py hooks`
Expected: every test passes, on both interpreters.

- [ ] **Step 5: Commit**

```bash
git add hooks/readonly-agent-guard.py hooks/test_readonly_agent_guard.py
git commit -m "fix(hooks): read a word glued to a glob group as the command"
```

### Task 2: The `-c`, `--config-env` and `--exec-path=` checks (spec §2a and the helper-program directory)

**Files:**
- Modify: `hooks/readonly-agent-guard.py` (new constants after `GIT_GLOBAL_WITH_VALUE`, `:209-212`; `_locate_git_verb`, `:1013-1055`)
- Test: `hooks/test_readonly_agent_guard.py` (new tests after `test_global_options_do_not_smuggle_a_write_past_the_guard`, `:1116`)

**Interfaces:**
- Consumes: `_expands_to_words(what, danger)`, `GIT_GLOBAL_WITH_VALUE`, as on `8131b81`.
- Produces:
  - `GIT_CONFIG_KEYS`: a `frozenset` of normalized keys allowed with any value.
  - `GIT_CONFIG_PROGRAM_VALUES`: a `dict` from a normalized key to the `frozenset` of values it is allowed with. Its keys take a program.
  - `_normalize_config_key(key)` returns `section.lower() + '.' + name.lower()` for two parts, `section.lower() + '.' + subsection + '.' + name.lower()` for more (the subsection is everything between the first and the last `.`, case kept), and `None` for fewer than two parts.
  - `_classify_config(text, value_hidden)` returns `None` or a reason. `text` is `key[=value]`. With `value_hidden` (`--config-env`), a key in `GIT_CONFIG_PROGRAM_VALUES` denies. Without it, a missing `=` is a value that no list holds.
  - `_locate_git_verb(args)` keeps its signature. It calls `_classify_config` on the value of `-c` and `--config-env`, in the two-word form and the `=`-joined form (`:1044`), after the missing-value and `expands` checks it runs today. `--exec-path=<anything>` denies. Bare `--exec-path` stays as today.

The lists (normalized, from the planning sweep of commands that `8131b81` allows; Task 6 confirms them):

```python
GIT_CONFIG_KEYS = frozenset({
    'color.grep', 'color.ui', 'commit.gpgsign', 'core.excludesfile', 'core.quotepath',
    'core.whitespace', 'diff.renames', 'http.lowspeedlimit', 'status.showuntrackedfiles',
    'user.email', 'user.name',
})
GIT_CONFIG_PROGRAM_VALUES = {
    'core.fsmonitor': frozenset({'false'}),
    'core.pager': frozenset({'cat'}),
}
```

The planning sweep read 213,699 unique commands that `8131b81` allows, 33,368 of them run by a guarded agent. It found 11 `-c` keys in them, and no `--config-env` or `--exec-path=`. `diff.renames` and `status.showuntrackedfiles` come from the spec's own count. Values are listed exactly as seen, never normalized.

- [ ] **Step 1: Write the failing tests**

```python
def test_listed_config_keys_stay_allowed():
    for line in ('git -c core.pager=cat log', 'git -c core.quotepath=off status',
                 'git -c=core.pager=cat log', 'git --config-env=core.quotepath=Q status',
                 'git --config-env core.quotepath=Q status'):
        assert guard.classify(line) is None, line


def test_program_naming_config_is_denied():
    for line in ('git -c core.fsmonitor=rm status', 'git -c diff.external=rm diff',
                 'git -c core.pager=rm log', 'git -c=core.pager=rm log',
                 'git --config-env=core.pager=P log', 'git --config-env core.pager=P log',
                 'git -c alias.x=y status', 'git -c nokey status'):
        reason = guard.classify(line)
        assert reason is not None and 'hooks/README.md' in reason, line


def test_config_key_without_a_value():
    assert guard.classify('git -c core.fsmonitor status') is not None
    assert guard.classify('git -c core.quotepath status') is None


def test_config_key_case():
    assert guard.classify('git -c Core.Pager=cat log') is None
    assert guard.classify('git -c CORE.PAGER=rm log') is not None
    assert guard._normalize_config_key('Diff.Tool.Cmd') == 'diff.Tool.cmd'
    assert guard._normalize_config_key('core') is None


def test_three_part_driver_keys_are_denied():
    for line in ('git -c diff.x.textconv=rm diff', 'git -c filter.x.clean=rm status'):
        assert guard.classify(line) is not None, line


def test_quoted_config_values():
    assert guard.classify("git -c 'core.pager=cat' log") is None
    assert guard.classify("git -c 'core.pager=cat -R' log") is not None


def test_exec_path_with_a_directory_is_denied():
    assert guard.classify('git --exec-path=/tmp/x status') is not None
    assert guard.classify('git --exec-path') is None
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run python build/run_suites.py hooks -- -k "config or exec_path"`
Expected: the deny assertions FAIL (today `-c` values are skipped), and `test_listed_config_keys_stay_allowed` PASSES.

- [ ] **Step 3: Add the constants, `_normalize_config_key` and `_classify_config`, and call them from `_locate_git_verb`**

Put one comment above the constants: what each holds, that a key absent from both denies, and that the lists came from a sweep (spec §3). The denial reason follows Denial text (Global Constraints).

- [ ] **Step 4: Run the whole suite**

Run: `uv run python build/run_suites.py hooks`
Expected: every test passes, on both interpreters.

- [ ] **Step 5: Commit**

```bash
git add hooks/readonly-agent-guard.py hooks/test_readonly_agent_guard.py
git commit -m "fix(hooks): allow only listed git -c keys and values"
```

### Task 3: Assignments before git (spec §2b)

**Files:**
- Modify: `hooks/readonly-agent-guard.py` (new constants after Task 2's; `_command_starts`, `:822-893`; `_classify_subcommand`, `:896-918`)
- Test: `hooks/test_readonly_agent_guard.py` (new tests after Task 2's)

**Interfaces:**
- Consumes: `ASSIGNMENT`, `_command_name`, `_classify_git`, Task 1's `_command_starts`.
- Produces:
  - `GIT_ENV_NAMES`: a `frozenset` of variable names allowed with any value before git.
  - `GIT_ENV_PROGRAM_VALUES`: a `dict` from a variable name to the `frozenset` of values it is allowed with. It holds the names that take a program and the names that point git at config (spec §2, "The names that point git at config").
  - `_command_starts_with_prefix(words)`: the walk that `_command_starts` holds today. It yields `None` where env's `-S` hides the command, else `(seq, k)`.
  - `_command_starts(words)` becomes a wrapper that yields `None` or `seq[k:]`, so its output is unchanged.
  - `_classify_assignment(word)` returns `None` or a reason for one word that `ASSIGNMENT` matches. A name in `GIT_ENV_NAMES` passes. A name in `GIT_ENV_PROGRAM_VALUES` passes only with `=` (not `+=`) and a listed value. Anything else denies.
  - `_classify_subcommand(tokens)` keeps its signature. For a candidate whose `_command_name(seq[k])` is `git`, once `_classify_git` returns `None`, it runs `_classify_assignment` on each word in `seq[:k]` that `ASSIGNMENT` matches.

The lists (from the planning sweep; Task 6 confirms them):

```python
GIT_ENV_NAMES = frozenset({
    'GIT_COMMON', 'GIT_COMMON_DIR', 'GIT_CONFIG_NOSYSTEM', 'GIT_DIR', 'GIT_INDEX_FILE',
    'GIT_OPTIONAL_LOCKS', 'GIT_TERMINAL_PROMPT', 'GIT_WORK_TREE', 'TZ',
})
GIT_ENV_PROGRAM_VALUES = {
    'GIT_CONFIG_GLOBAL': frozenset({'/dev/null'}),
    'GIT_CONFIG_SYSTEM': frozenset({'/dev/null'}),
    'GIT_PAGER': frozenset({'cat'}),
    'PAGER': frozenset({'cat'}),
}
```

`GIT_COMMON` is no git variable: scripts use it to hold `git rev-parse --git-common-dir` (56 standalone assignments in the sweep), and git ignores it, so Task 4 needs it listed. `GIT_COMMON_DIR` stays allowed by the spec's Non-goals. `HOME` and `XDG_CONFIG_HOME` get no value: none seen is fixed. `GIT_PAGER` is pinned by `test_…:494`.

- [ ] **Step 1: Write the failing tests**

```python
def test_listed_assignments_before_git_stay_allowed():
    for line in ('GIT_PAGER=cat git log', 'GIT_OPTIONAL_LOCKS=0 git status',
                 'TZ=UTC git log', 'env GIT_PAGER=cat /usr/bin/git log'):
        assert guard.classify(line) is None, line


def test_program_naming_assignments_before_git_are_denied():
    for line in ('GIT_EXTERNAL_DIFF=rm git diff', 'GIT_PAGER=rm git log',
                 'PAGER=rm git log', 'GIT_EXEC_PATH=/tmp/x git status',
                 'GIT_CONFIG_GLOBAL=/tmp/x git log', 'HOME=/tmp/x git log',
                 'GIT_CONFIG_PARAMETERS=x git log', 'UNLISTED=1 git log',
                 'GIT_PAGER+=cat git log'):
        reason = guard.classify(line)
        assert reason is not None and 'hooks/README.md' in reason, line


def test_quoted_assignment_values():
    assert guard.classify("GIT_PAGER='cat' git log") is None
    assert guard.classify("GIT_PAGER='cat -R' git log") is not None


def test_assignments_through_prefix_utilities():
    for line in ('time env GIT_EXTERNAL_DIFF=rm git diff',
                 'env -i GIT_PAGER=rm git log', 'X=1 git log'):
        assert guard.classify(line) is not None, line


def test_glued_git_with_an_assignment_before_it():
    assert guard.classify('GIT_EXTERNAL_DIFF=rm git(.) diff') is not None


def test_assignments_before_other_commands_stay_unread():
    assert guard.classify('GIT_EXTERNAL_DIFF=rm ls') is None
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run python build/run_suites.py hooks -- -k "assignment"`
Expected: the deny tests FAIL; the two allow tests and `test_assignments_before_other_commands_stay_unread` PASS.

- [ ] **Step 3: Split `_command_starts`, add the constants and `_classify_assignment`, and call it from `_classify_subcommand`**

Move the walk's body into `_command_starts_with_prefix` unchanged except for its yields. Derive the prefix after the walk from `(seq, k)`, never inside `_stop_index`: its `known` memo skips heads.

- [ ] **Step 4: Run the whole suite**

Run: `uv run python build/run_suites.py hooks`
Expected: every test passes, on both interpreters. `test_command_starts_*` pass unedited.

- [ ] **Step 5: Commit**

```bash
git add hooks/readonly-agent-guard.py hooks/test_readonly_agent_guard.py
git commit -m "fix(hooks): allow only listed assignments before git"
```

### Task 4: Assignments that last past one command (spec §2c)

**Files:**
- Modify: `hooks/readonly-agent-guard.py` (new constants after Task 3's; `_classify_subcommand`)
- Test: `hooks/test_readonly_agent_guard.py` (new tests after Task 3's)

**Interfaces:**
- Consumes: Task 3's `_command_starts_with_prefix`, `_classify_assignment`.
- Produces:
  - `DECLARATION_COMMANDS = frozenset({'export', 'typeset', 'declare', 'local', 'readonly', 'integer'})`.
  - `GIT_READ_NAMES = frozenset({'PAGER', 'EDITOR', 'VISUAL', 'HOME', 'XDG_CONFIG_HOME'})`: the names outside `GIT_*` that git reads (spec §2c).
  - `_classify_lasting_assignment(word)` returns `None` for a name that neither starts with `GIT_` nor is in `GIT_READ_NAMES`, else `_classify_assignment(word)`.
  - `_classify_subcommand` runs `_classify_lasting_assignment` on each `ASSIGNMENT` word in `seq[:k]` when `k == len(seq)` (no command), and on each `ASSIGNMENT` word in `seq[k + 1:]` when `_command_name(seq[k])` is in `DECLARATION_COMMANDS`. Both run whatever follows in the line (spec §2c, unconditional).

- [ ] **Step 1: Write the failing tests**

```python
def test_lasting_assignments_git_reads_are_checked():
    for line in ('export GIT_EXTERNAL_DIFF=rm; git diff', 'GIT_EXTERNAL_DIFF=rm\ngit diff',
                 'typeset -x GIT_PAGER=rm', 'export PAGER=rm', 'export HOME=/tmp/x',
                 'declare GIT_UNLISTED=1'):
        reason = guard.classify(line)
        assert reason is not None and 'hooks/README.md' in reason, line


def test_lasting_assignments_git_does_not_read_stay_unread():
    for line in ('export FOO=rm', 'X=$(pwd)', 'export GIT_PAGER=cat', 'local n=1'):
        assert guard.classify(line) is None, line
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run python build/run_suites.py hooks -- -k "lasting"`
Expected: `test_lasting_assignments_git_reads_are_checked` FAILS; the other PASSES.

- [ ] **Step 3: Add the constants and `_classify_lasting_assignment`, and call it from `_classify_subcommand`**

- [ ] **Step 4: Run the whole suite**

Run: `uv run python build/run_suites.py hooks`
Expected: every test passes, on both interpreters.

- [ ] **Step 5: Commit**

```bash
git add hooks/readonly-agent-guard.py hooks/test_readonly_agent_guard.py
git commit -m "fix(hooks): check lasting assignments of the names git reads"
```

### Task 5: The README (spec §4)

**Files:**
- Modify: `specs/readonly-guard-glued-qualifier-and-git-config.md` (§1, "False positives"; spec amendment)
- Modify: `hooks/README.md` ("Not caught", `:284-312`; group-word text, `:342-348`; the git option text; "Known false positives")

**Interfaces:**
- Consumes: the constant and function names of Tasks 1 to 4.
- Produces: none.

- [ ] **Step 0: Amend the spec's §1 example (spec amendment, approved as D2)**

In `specs/readonly-guard-glued-qualifier-and-git-config.md`, §1, "False positives", replace:

```markdown
**False positives.** A heredoc line, read as shell, that starts with a denied command name glued to a
parenthesis is denied, for example a Python line that calls a function named `rm`. The README records the class
under "Known false positives", beside the heredoc-line class it resembles.
```

with:

```markdown
**False positives.** A heredoc line, read as shell, that starts with `git` or `sed` glued to a parenthesis, and
whose later words form a denied git command or an in-place `sed`, is denied *(owner, plan 121, 2026-11-28)*. The
flat reading already denies such a line for every other denied command name, such as a Python line that calls a
function named `rm`, so that is not new. The README records the class under "Known false positives", beside the
heredoc-line class it resembles.
```

Leave the spec's status line untouched.

- [ ] **Step 1: Edit `hooks/README.md`**

1. Remove the glued-qualifier bullet (`:302-304`).
2. Replace the git-config bullet (`:305-307`) with one bullet for what stays uncaught: configuration held in a repository or a file (`.git/config`, the global and system config files, `.gitattributes`), and the options and variables that point git at another repository (spec Non-goals).
3. Beside the group-word text (`:342-348`), say that the guard also reads the word glued before a group as the command.
4. Beside the git option text, describe the allowlists by constant name: listed `-c` and `--config-env` keys, program-taking keys and variables with listed values only, `--exec-path=<dir>` and `GIT_EXEC_PATH` denied, and the lasting-assignment check (§2c).
5. Under "Known false positives", add three bullets: a heredoc line, read as shell, that starts with `git` or `sed` glued to a parenthesis and goes on with the words of a denied git form or an in-place `sed` (the flat reading already denies such a line for every other denied command, so `rm(path)` is not new); an unlisted `-c` key or assignment before git; and a lasting assignment of a name git reads, checked whether or not git follows (`export GIT_…=…` in a heredoc line, `export HOME=…` in test setup).

The prose follows the plain technical English rule (`rules/write-with-asd-ste100.md`).

- [ ] **Step 2: Run the lints**

Run: `bash build/run_commit_lints.sh`
Expected: `commit lints passed`.

- [ ] **Step 3: Commit**

```bash
git add hooks/README.md specs/readonly-guard-glued-qualifier-and-git-config.md
git commit -m "docs(hooks): describe the glued-word reading and the git config allowlists"
```

### Task 6 (controller): No denial lost, and the false-positive sweep (spec §3)

The scripts are one-off, are written by the controller, and are never committed. Their detail goes to files in `~/.cache/agent-skills/scratch/plan121-work/`, and only counts go to chat.

**Files:**
- Create (scratch, uncommitted): `~/.cache/agent-skills/scratch/plan121-work/{old_guard.py,compare.py,flips.jsonl}`
- Modify: this plan's `## Decisions`; `hooks/readonly-agent-guard.py` and its tests only if Step 4 extends a list

**Interfaces:**
- Consumes: the branch's guard (Tasks 1 to 4); `8131b81`'s guard; the corpus loader in `plan121-work/sweep.py` (planning).
- Produces: the owner's ruling on each false-positive class, logged as a decision.

- [ ] **Step 1: Fetch `8131b81`'s guard**

Run: `git show 8131b81:hooks/readonly-agent-guard.py > ~/.cache/agent-skills/scratch/plan121-work/old_guard.py`

- [ ] **Step 2: Compare the two guards**

`compare.py` loads both guards with `importlib` and reads three sources: the transcript corpus (as `sweep.py` loads it, with populations), every `str` constant in `hooks/test_readonly_agent_guard.py` (found with `ast`), and every backtick span and fenced-block line of `hooks/README.md`, on the branch and at `8131b81`. A guard denies an input when `classify` returns a reason or raises. Write each input whose result differs to `flips.jsonl`. Print denied→allowed and allowed→denied counts per source; split the corpus counts by guarded agent (a population in `READONLY_AGENTS`) and other.

Expected:
- `denied→allowed: 0` for every source. Any other count breaks the spec's Anti-goals: stop, report the count only, and fix the task that caused it.
- In the test file, allowed→denied for each deny line of the Tasks 1 to 4 tests, which `8131b81` allows.
- In the README at `8131b81`, allowed→denied for the glued-qualifier example and the three git-config examples under "Not caught". In the branch's README, for the examples of Task 5's three new false-positive bullets.
- Note any other test-file or README flip for the owner (Step 5).

- [ ] **Step 3: Classify each allowed→denied corpus flip**

Give each row the class of the new guard's reason: `-c key`, `--config-env`, `--exec-path`, `before git`, `lasting` (by the name of the check that returned it), or `glued` when the reason is one that `8131b81` also gives. Print counts by class and population group. The planning sweep predicts these, by count of commands allowed today: `lasting` from a `HOME=` assignment (1 guarded, 9 other) and a `GIT_EXTERNAL_DIFF=` assignment (1 other), and `before git` none once the lists above are in.

- [ ] **Step 4: Extend the lists for read-only uses**

For each guarded-agent flip whose git command is read-only, apply spec §3 rule 2: list the key or name if it names no program, or the harmless value seen if it takes one. Add each listed entry to a Task 2 or 3 allow test. Rerun the suite, then Step 2.

- [ ] **Step 5: STOP, owner — the false positives**

Report in chat, as counts only: the corpus size; denied→allowed (0); allowed→denied by class and population group; and what Step 4 listed. Point to `flips.jsonl` for the commands. Ask the owner to accept each remaining class or to ask for a narrower rule. A narrower rule that changes the spec needs a spec amendment task and a new code task, planned from the owner's answer before any code changes.

- [ ] **Step 6: Log the ruling and commit**

Add the owner's answer to `## Decisions` as the next decision, in the owner's words, then:

```bash
git add specs/plans/121-readonly-guard-glued-qualifier-and-git-config.md hooks/
git commit -m "chore(plans): record the plan 121 false-positive ruling"
```
