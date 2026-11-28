# Read-only guard: the glued glob qualifier and programs named through git configuration — Design Spec

**Status:** APPROVED (2026-11-28). The owner approved this file, its designer's calls included, on 2026-11-28. The
question was "Do you approve the spec, with its designer's calls?", and the owner answered "Approve it".

This spec answers two backlog items in `specs/deferred_items.md`:

- **Item 1**, "A glob qualifier glued to the command word still hides the command from the read-only guard"
  (section `90-readonly-guard-command-starts — 2026-11-12`).
- **Item 2**, "Allowlisted git verbs can run a program through configuration or the environment" (section
  `readonly-guard-leading-token-bypasses (no plan; branch claude/objective-nash-accd9c) — 2026-09-28`).

The design came from a brainstorming session on 2026-11-28. Text marked *(designer's call)* is the designer's
choice, and "Designer's calls" lists each one. Line numbers are as of `8131b81`, the `main` commit this design read.

> **For agentic workers:** plan from this file with the writing-plans skill. Keep bypass constructions out of
> chat: report them by class and count, and keep the detail in files under `/tmp/` or the scratch directory
> (Constraints, "Chat hygiene").

## Intent

`hooks/readonly-agent-guard.py` is a `PreToolUse` (`Bash`) hook. It denies mutating commands for the five
read-only agents in `READONLY_AGENTS` (`:30`). It is a guardrail against an agent drifting off contract, not a
sandbox (`hooks/README.md:254`). The contract is `CONTRACT_CLAUSE` (`:41-44`): no mutation of the working tree,
the index, HEAD, branch state or the worktree list via Bash.

`hooks/README.md` lists, under "Not caught" (`:284-312`), forms that run a mutator but pass the guard. Two of
those bullets have backlog items, and this spec closes both:

1. **The glued qualifier** (`hooks/README.md:302-304`). A glob group glued to the command word hides the command.
   zsh runs the form only with `BARE_GLOB_QUAL` on and a matching file present. The Bash tool turns the option
   off, so the line does not run there today.
2. **Programs named through git configuration** (`hooks/README.md:305-307`). An allowlisted read-only git verb
   can start a program that a `-c` config value or a `GIT_*` environment assignment names. The program can be a
   mutator. `_locate_git_verb` (`:1013-1055`) skips every `-c` value, and `_stop_index` (`:781-819`) skips
   every assignment, so neither is read.

**Why now.** No failure was seen, and item 2's "Revisit if" signal has not fired. The owner's 2026-11-28
`/deferred` pass picked item 1 as a design item and asked to include as many items as possible in each design,
which brings in item 2 (D1). Item 1 was first found on 2026-09-28.

## Goals, non-goals and anti-goals

**Goals**

1. Item 1's `Done when:`: the guard denies the README's glued-qualifier example, while `print(git(x))` in a
   heredoc, `*(.)` and `(#i)readme*` still pass, and the README's "Not caught" bullet for it is removed.
2. Deny the three README examples of item 2 (`hooks/README.md:305-307`), each with a mutator as the program.
3. Keep allowing the read-only git forms agents use today. The test suite already pins `git -c core.pager=cat
   log` (`hooks/test_readonly_agent_guard.py:1113`) and `GIT_PAGER=cat git log` (`:494`). The transcript sweep
   (Design §3) finds the rest.
4. The `hooks` suite (`build/suites.toml`; tests in `hooks/test_readonly_agent_guard.py`) stays green on the dev
   Python and on `/usr/bin/python3` 3.9. The guard stays stdlib-only.
5. `hooks/README.md` describes the new behaviour truthfully, with each new false-positive class under "Known
   false positives".

**Non-goals**

- **The other "Not caught" bullets.** A command word made by expansion or glued to a brace, utilities that run a
  command (`xargs`, `find -exec`), quoted strings, backticks, the mixed-reading gap, aliases and wrappers, and
  marimo-pair's script all stay as they are.
- **Configuration held in a repository or a file.** A read-only git verb also reads `.git/config`, the global and
  system config files, and `.gitattributes`. A program named there is out of scope. So are the options and
  variables that point git at another repository (`-C`, `--git-dir`, `--work-tree`, `GIT_DIR`, `GIT_WORK_TREE`,
  `GIT_INDEX_FILE`, `GIT_COMMON_DIR`): they stay allowed, as `-C` and `--git-dir` are today *(designer's call)*.
  The variables that point git at a config file are not in this group (Design §2).
- **Programs other than git.** Assignments before a command other than git are not read, except where Design §2
  says so for `export` and the like.
- **Changes to the tokenizer, `_split_tokens` or `READINGS`.** Item 1 changes only what a group placeholder carries
  and what the walk does with it.

**Anti-goals**

- Any change that turns a denial on `8131b81` into an allow. Item 1's change adds a reading. Item 2's change adds
  denials. Neither removes a reading or a check.
- A denylist of program-naming keys. The owner chose the allowlist (D3).
- False denials of read-only git forms found in the transcript sweep, unless the owner accepts them.

## Approaches

### Item 1

- **A. Read the glued word as the command too** (picked by the owner, D2). When a group is glued to a word where
  a command can start, the walk also reads that word as the command, with the words after the group. It follows
  plan 90's pattern of reading a word both ways, and it only adds denials. Cost: false denials of text that looks
  like a call to a denied command name, such as a heredoc line of Python that starts with `mv(` or `rm(`.
- **B. No fix.** The Bash tool cannot run the form, so the bullet stays under "Not caught". Cost: the README keeps
  a gap that another shell setup can open.

The designer recommended A: the fix is small, it fits plan 90's pattern, and its false-positive class is the kind
the guard already accepts for heredoc lines that begin with a denied word (`hooks/README.md:332-334`).

### Item 2

- **A. A denylist.** Deny the `-c` keys and the `GIT_*` variables that name a program. It blocks no normal use,
  but the set is open-ended, and a new git release can add a key that the list misses.
- **B. An allowlist** (picked by the owner, D3). Allow only listed `-c` keys and listed assignments before git.
  The keys and variables whose value is a program are allowed only with listed values. Anything else is denied.
  It fails closed, as the guard does on unknown git global options (`:1050-1053`). Cost: an unlisted harmless key
  is denied until someone adds it.

The designer recommended B. The key the suite must keep, `core.pager`, itself takes a program, so an allowlist by
key alone would keep the hole open. That is why B checks values too.

## Design

### 1. Item 1: the group placeholder carries the glued word

Today `_group_word` (`:473-492`) pops a word glued to a group (`before`, when `not before.syntax`) and returns the
shared `GROUP_WORD` token (`:101`). The popped word is lost, so `_command_starts` (`:822-893`) never sees it.

The change:

1. When `_group_word` pops a glued word, it returns a new placeholder token that carries that word, for example
   in an attribute `glued`. `GROUP_WORD` is one shared token today, so the carrying placeholder must be a new
   token for each group. It keeps `str` value `'()'` and `expands=True`, so every existing check that reads the
   placeholder reads it as before. Where no word is popped, `_group_word` returns `GROUP_WORD` as today.
2. In `_command_starts`, when the stop word `seq[k]` is a placeholder that carries a glued word, the walk also
   queues a continuation in which that word takes the placeholder's place: `seq[:k] + [glued] + seq[k + 1:]`. It
   is the same shape as the `=` strip at `:886-891`, and the same `queue` key bounds it.
3. Every other reading stays. The placeholder is still yielded as the command at `k`, as today.

What this gives on the lines of Goal 1 (as traced from `split_subcommands` on `8131b81`, whose nested reading of
`print(git(x))` is `[['x'], ['()'], ['()']]`):

| Line | New reading | Result |
|---|---|---|
| The README example | git, with the words after the group | denied, since the verb is not allowlisted |
| `print(git(x))` in a heredoc | `print` alone; `git` alone | allowed: bare `git` prints usage (`_locate_git_verb` returns `(None, '')`) |
| `ls *(.)` | none: `*` is glued but not at a command start | allowed |
| `ls (#i)readme*` | none: nothing is glued before the group | allowed |

**The word glued after a group.** `_split_tokens` drops a word that touches a group's `)` (`glued`, `:540-541`),
so the placeholder carries only the word before the group. That is enough for Goal 1 *(designer's call)*.

**False positives.** A heredoc line, read as shell, that starts with a denied command name glued to a
parenthesis is denied, for example a Python line that calls a function named `rm`. The README records the class
under "Known false positives", beside the heredoc-line class it resembles.

### 2. Item 2: the git config and environment allowlist

Three inputs can set git configuration or name a program for a git command. The guard reads each against an
allowlist. Each allowlist is a module-level constant, beside `GIT_GLOBAL_WITH_VALUE` (`:209`).

**a. `-c key[=value]` and `--config-env key=ENVVAR`.** `_locate_git_verb` checks each one where it now skips the
value (`:1033-1048`), in both the two-word and the `=`-joined forms.

- The key is compared case-insensitively on its section and name, as git compares them. A key with a subsection
  (three parts, such as a diff or filter driver key) matches only if the allowlist lists it in full.
- A key not on the allowlist is denied.
- A key on the allowlist whose value names a program (the pager keys, for example) is allowed only with a listed
  value. For `--config-env`, the guard cannot see the value, so such a key is denied there *(designer's call)*.
- A `-c` value that `expands` fails closed, as the option values do today (`:1039-1042`).
- The denial names the key, says the guard allows only listed config keys, and points to `hooks/README.md`.

**b. Assignments before git.** These are the words `_stop_index` skips before the `git` command word: plain
assignments, and `env`'s operands (`_skip_prefix_utility`, `:776-777`). When the command word is `git`, each
assignment's name must be on an allowlist of names, and a name whose value is a program must have a listed value.
Any other name is denied *(designer's call: the allowlist is total before git, so it covers `PAGER`, `EDITOR` and
other non-`GIT_` names that git reads, with no open-ended list of them)*. The sweep must therefore list the
harmless names agents set before git, such as the locale and time-zone variables.

`_command_starts` yields only `seq[k:]`, so the assignments before `k` do not reach `_classify_git` today. The
builder picks how to pass them (left to the builder).

**c. Assignments that last past one command.** A standalone assignment, or an assignment in the arguments of
`export`, `typeset`, `declare`, `local`, `readonly` or `integer`, sets the variable for the git commands after it
in the same Bash call. zsh also updates an exported variable on a plain assignment. So the guard checks these too,
but only for the names git reads: every `GIT_*` name, `PAGER`, `EDITOR` and `VISUAL`, and the config-pointing
names below *(designer's call)*. A `GIT_*` name not on the allowlist is denied, and so is a listed name with an
unlisted value. Other names stay unread.

The check is unconditional: such an assignment is checked wherever it appears, whether or not a git command
follows it in the same call *(designer's call)*. Each subcommand is classified on its own today, in each reading,
with no state passed between subcommands, and a "git follows" rule would need that state. The cost is a false
positive class, recorded in the README: for example, a heredoc line, read as shell, that exports an unlisted
`GIT_*` name.

**The names that point git at config.** `GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_COUNT` with its `GIT_CONFIG_KEY_<n>`
and `GIT_CONFIG_VALUE_<n>`, `GIT_CONFIG`, `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` can each carry or point to a
program-naming key. So can `HOME` and `XDG_CONFIG_HOME`, which choose the global config file git reads. All of
them are allowed only with listed fixed values, before git (§2b) and in §2c's forms *(designer's call)*. The sweep
decides whether to list, for example, `GIT_CONFIG_GLOBAL=/dev/null` and `GIT_CONFIG_NOSYSTEM=1`, which only remove
config.

**The helper-program directory.** `--exec-path=<dir>` and `GIT_EXEC_PATH` set where git looks for the helper
programs it starts. `_locate_git_verb` skips the `=`-joined form's value today (`:1044-1049`). Both forms are denied
*(designer's call)*. Bare `--exec-path`, which prints the path and exits, stays allowed.

### 3. The allowlist contents come from a sweep

The planner fixes the exact lists from a transcript sweep, as plan 90 did
(`specs/plans/completed/90-readonly-guard-command-starts.md`, Task 3):

1. Collect every `git -c` key, `--config-env` key and assignment before `git` that the transcripts show. A rough
   count on 2026-11-28 found keys such as `core.quotePath`, `status.showUntrackedFiles`, `diff.renames` and
   `color.grep`, and names such as `GIT_DIR`, `GIT_INDEX_FILE`, `GIT_PAGER` and `GIT_CONFIG_GLOBAL`. Many hits
   are from docs and tests, so the sweep counts only commands that ran.
2. List a key or name if a read-only git command used it and it names no program. List a program-taking key or
   name only with the values seen that are harmless (`cat` for the pagers, for example).
3. Run the new guard on the whole corpus and report the commands that it now denies and `8131b81` allows, by
   class and count. Each one is a false positive to fix in the lists, or one for the owner to accept.

The corpus and the sweep's outputs stay out of the repository, in the scratch directory plan 90 used
(`~/.cache/agent-skills/scratch/`), since they hold other repositories' commands.

### 4. README and tests

- `hooks/README.md`: remove the glued-qualifier bullet (`:302-304`). Replace the git-config bullet (`:305-307`)
  with one that names what stays uncaught: configuration held in a repository or a file (Non-goals). Describe the
  new reading beside the group-word text (`:342-348`) and the allowlist beside the git option text. Add the new
  false-positive classes: item 1's heredoc class, "an unlisted `-c` key or assignment before git is denied", and
  §2c's unconditional check of long-lived assignments.
- `hooks/test_readonly_agent_guard.py`: pin each mechanism by its own test, with an allow and a deny case.
  Tests use mutator names as the hidden program, as the suite does now. Keep every existing test unedited.

## Constraints

- **Stdlib only.** The guard runs under `/usr/bin/python3` 3.9 (`hooks/README.md`).
- **Chat hygiene.** Hunting bypasses of this guard has tripped the safety classifiers before. Name gaps by area
  and class in chat. Put constructions in tests and in files under `/tmp/` or the scratch directory. Never ask a
  guarded agent (`READONLY_AGENTS`) to probe its own guard.
- **The hook's time budget.** A hook that times out lets the call go on. Item 1's continuation uses the existing
  `queue` key, so the 64-candidate cap (`_classify_subcommand`, `:896-918`) still bounds the walk.
- **Backlog notes.** This spec's commit writes `→ planned 2026-11-28: specs/readonly-guard-glued-qualifier-and-git-config.md`
  on items 1 and 2, and on no other item.

## Left to the builder

- How the assignments before `k` reach the git classifier (Design §2b).
- The exact allowlists, from the sweep (Design §3).
- Test names and where the new constants sit in the module.
- The wording of each denial, within Design §2a's content.

## Decision record

- **D1** (owner, 2026-11-28, `/deferred` pass): "Do the quick fixes here. Present cards to do P1, P2, and D1.",
  then "Include as many items as possible in each." D1 was item 1 under the pass's Design disposition. Read as:
  one spec through the normal design cycle for both "Not caught" gaps that have backlog items, item 2 included
  though its revisit signal has not fired.
- **D2** (owner, 2026-11-28, brainstorming): "A, the fix", in answer to the choice between reading the glued word
  as the command too (A) and no fix (B) for item 1.
- **D3** (owner, 2026-11-28, brainstorming): "B, the allowlist", in answer to the choice between a denylist (A) and
  an allowlist (B) for item 2.

## Designer's calls

1. Item 1's acceptance bar is its `Done when:` plus the green suite on both Pythons (Goals 1 and 4).
2. The variables that point git at another repository stay allowed, as `-C` and `--git-dir` are (Non-goals).
3. The placeholder carries only the word glued before a group (Design §1).
4. `--config-env` with a program-taking key is denied (Design §2a).
5. The allowlist before git is total over names, so non-`GIT_` names that git reads need no list of their own
   (Design §2b).
6. Assignments that last past one command are checked for `GIT_*`, `PAGER`, `EDITOR`, `VISUAL` and the
   config-pointing names only (Design §2c).
7. That check is unconditional, with no state passed between subcommands (Design §2c).
8. `HOME` and `XDG_CONFIG_HOME` count as config-pointing names and take fixed values only (Design §2c).
9. `--exec-path=<dir>` and `GIT_EXEC_PATH` are denied; bare `--exec-path` stays allowed (Design §2c).
