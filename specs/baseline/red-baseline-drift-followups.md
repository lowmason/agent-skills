# Plan 88 micro-tests: three superpowers-drift wording changes

This record holds the micro-tests for plan 88 (`specs/plans/88-superpowers-drift-followups.md`). A micro-test runs one
decision many times through a fresh `claude -p` with no tools. Then it reads each reply by a rule fixed in advance.
One run is a rep. Plan 88 changes the wording of three skills that were vendored from superpowers. Each change gets
one or more cases:

- `merge-conflict` (finding 28, the conflict half): `finishing-a-development-branch` has no path for a merge
  conflict. Option 1 runs `git checkout`, `git pull` and `git merge`, and the text says nothing about a conflict.
  Plan 88's Task 2 adds a rule to stop, show the conflict and ask. The text under test is
  `skills/finishing-a-development-branch/SKILL.md`. This is an additive case: it checks new guidance.
- `subagent-reviewer` (finding 27): `receiving-code-review` does not say which rule wins when a subagent reviewer
  returns a finding inside a plan run. Its stop for a conflict with the partner's earlier decisions would stall a run
  that rules on each finding. Plan 88's Task 3 adds one sentence. The texts under test are
  `skills/executing-plans/SKILL.md` and `skills/receiving-code-review/SKILL.md`. This is an additive case.
- `string-presence` and `change-detector` (finding 3): `testing-anti-patterns.md` does not name two traps. A
  string-presence test asserts on the words of a script, a skill or a prompt, not on what it does. A change-detector
  test fails when the implementation changes, but it protects no useful outcome. Plan 88's Task 4 adds both traps.
  The texts under test are `skills/test-driven-development/SKILL.md` and
  `skills/test-driven-development/testing-anti-patterns.md`. Both are additive cases.
- `text-contract` (finding 3): a check whose subject is text, such as four copies that must stay equal, is not a trap.
  The owner's ruling (D2) says the new wording must keep that check allowed. The texts are the same as above. This is
  a non-regression case: it checks that the new traps do not make the agent refuse a valid test.

Task 1 builds the kit, registers the rules and runs the control arms. Task 2 runs the `merge-conflict` treatment arm.
Task 3 runs the `subagent-reviewer` treatment arm. Task 4 runs the three test-driven-development treatment arms. Each
task appends its own section to this record.

## Base

`BASE` is the commit that the execution branch started from, before Task 1 changed anything. Every control arm reads
its texts at `BASE`: `39173c9` (`39173c9a94c34db38e976dc42a335a6d61f4012e`).

Task 1 Step 1 checked for drift. `b0c2673` is the commit that the plan's line numbers refer to.
`git diff --stat b0c2673 39173c9 -- skills/finishing-a-development-branch skills/receiving-code-review skills/test-driven-development skills/executing-plans NOTICE build/cc_guide/conformance.toml`
printed two files:

```text
 NOTICE                          |  9 +++++++++
 build/cc_guide/conformance.toml | 35 +++++++++++++++++++++++++++++++++++
 2 files changed, 44 insertions(+)
```

The four skill directories show no change. So the texts under test are the same as at `b0c2673`. The two files that
changed are:

- `NOTICE`: commit `7bb8810` added 9 lines. They are a `/deferred` pass entry (2026-11-10) in the superpowers change
  list, for two local fixes (findings 26 and 33). Task 5 edits `NOTICE` and matches its old text, not a line number.
- `build/cc_guide/conformance.toml`: plan 87 added 35 lines. They hold a new comment and two `compaction-window`
  exceptions, one for `finishing-a-development-branch` and one for `subagent-driven-development`. Task 2 removes the
  first one and rewrites the comment above it. Task 2 matches old text, not a line number.

This is a Step 1 deviation. It needs no anchor re-take. Each step of the plan matches its old text, not its line
number (Global Constraints, Anchors). The changed lines sit in `NOTICE`, which only Task 5 edits, and in
`build/cc_guide/conformance.toml`, which only Task 2 edits. Line numbers in those two files may have shifted.

## Kit

Kit: `specs/baseline/red-baseline-drift-followups/kit/`. Four files are copies of plan 82's kit
(`specs/baseline/red-baseline-test-command/kit/`). No file of the old kit was edited.

- `run_reps.sh` changes the plan number in its first comment (82 to 88) and its temp prefix, from
  `/tmp/plan82-rep-` to `/tmp/plan88-rep-`. The comment `Plan 77 deviation (a)` keeps its number. It names the plan
  where the `env -i` form came from. The file mode stays executable.
- `isolation_probe.txt` is an unchanged copy.
- `show_reps.py` changes the plan number in its docstring. Its reading aids change to nine. They flag `git add`
  (`git-add`), `git commit` (`git-commit`), `--ours` (`ours`), `--theirs` (`theirs`), `merge --abort`
  (`merge-abort`), `Ruling:` (`ruling`), `ROUND_HALF_UP` (`round-half-up`), `read_text` (`read-text`) and
  `_lines_by_sku` (`lines-by-sku`). Each aid ignores letter case. An aid only points the reader at a reply. It is
  never a verdict.
- `build_prompts.py` changes only the plan number in its docstring.
- `cases.py` is new. It has the shape of plan 82's `cases.py`: a `case()` function and a `CASES` table. It holds the
  five cases, the VOID rule, the model (`claude-sonnet-5-5`), the per-rep budget (`0.50`) and the bars. `TASK_TAIL`,
  `VOID`, `NON_REGRESSION_BAR` and `ADDITIVE_BAR` are copied word for word from plan 82's `cases.py`. A script
  compared them with the old module, together with the model and the budget, and all six were equal.

`build_prompts.py <sha> <out-dir> [<case> ...]` builds the prompts at a sha and writes `MANIFEST.txt`.
`build_prompts.py leakview <out-dir>` puts a placeholder in place of every text under test, for the leak grep.
`run_reps.sh <prompt> <out-dir> <first> <last> claude-sonnet-5-5` runs the reps.

Each rep is a fresh
`claude -p --model claude-sonnet-5-5 --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence --output-format json --max-budget-usd 0.50`
with `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`, under `env -i`. Only `HOME`,
`USER`, `LOGNAME`, `PATH`, `SHELL`, `TMPDIR` and `LANG` pass through, each only when it is set. The rep runs from a
new, empty directory under `/tmp`, outside every repository. There are 5 scored reps per case and arm. Every verdict
is read by hand from the full reply.

## Arms

- `control`: each text at `BASE` (`39173c9`). The prompts are built with
  `build_prompts.py 39173c9a94c34db38e976dc42a335a6d61f4012e ~/.cache/agent-skills/scratch/plan88-work/control`.
- `treatment`: each text as the task leaves it, built from the sha that `git stash create` prints. That command adds
  no stash entry. Task 2 builds the `merge-conflict` treatment. Task 3 builds the `subagent-reviewer` treatment.
  Task 4 builds the treatments of the three test-driven-development cases.

Both arms use the same frame, fixture and task. Only the text under test differs. A `SKILL.md` text is its body with
the frontmatter removed. A reference file is shown whole, framed as a file that the agent read when the text above
pointed it there.

| Case | Texts under test | Kind |
|---|---|---|
| `merge-conflict` | `finishing-a-development-branch/SKILL.md` | additive |
| `subagent-reviewer` | `executing-plans/SKILL.md`, `receiving-code-review/SKILL.md` | additive |
| `string-presence` | `test-driven-development/SKILL.md`, `testing-anti-patterns.md` | additive |
| `change-detector` | `test-driven-development/SKILL.md`, `testing-anti-patterns.md` | additive |
| `text-contract` | `test-driven-development/SKILL.md`, `testing-anti-patterns.md` | non-regression |

## Known limit (O4, owner ruling D6)

Each prompt carries the texts that an agent would have loaded, whole. For the three test-driven-development cases that
means the `SKILL.md` body and the whole of `testing-anti-patterns.md`, as if the agent had already opened the
reference. So the cases test the wording of the text. They do not test whether an agent opens a reference from a
pointer in `SKILL.md`. Plan 88 changes the pointer in `test-driven-development/SKILL.md` (Task 4, owner ruling D5), and
this kit cannot show that the new pointer makes an agent load the reference. The same limit holds in two more places. First, the
moved carry-findings block of `finishing-a-development-branch` (Task 2): the `merge-conflict` prompt does not carry
the new reference file. Second, `executing-plans/SKILL.md` tells the agent to read `references/final-review.md`
when the last task is done. That file holds the fix-pass rule and the `Final: Ruling:` form. The `subagent-reviewer`
prompt does not carry it, because the plan fixes that case's texts. So a control rep may lack the form that the
file gives, and that gap can move the control score. The owner chose to keep this default, and the limit is recorded
here.

## Bars

There are two kinds of bar.

A non-regression case checks that a change keeps a behavior. Its treatment passes at least 4 of 5, and at least as
many reps as the control, minus one. A miss stops the task for an owner ruling. A control score never reverts the
change.

An additive case checks new guidance. Its treatment passes 5 of 5, and the control fails at least 1 of 5. A control
with no failure does not revert the change. The result is recorded and put to the owner at the plan completion gate.
A treatment below 5 of 5 gets one wording round with the reading rule unchanged, then an owner ruling.

| Case | Kind | Bar |
|---|---|---|
| `merge-conflict` | additive | `treatment 5/5; control fails at least 1 of 5` |
| `subagent-reviewer` | additive | `treatment 5/5; control fails at least 1 of 5` |
| `string-presence` | additive | `treatment 5/5; control fails at least 1 of 5` |
| `change-detector` | additive | `treatment 5/5; control fails at least 1 of 5` |
| `text-contract` | non-regression | `treatment >= 4/5, and >= control - 1 passes; a miss stops the task for an owner ruling` |

## VOID rule

A VOID rep is thrown out, rerun under the next free rep number and not scored. The rule is copied word for word from
plan 82's kit:

> VOID, rerun with the next free rep number and not scored, when any of these hold: show_reps.py's header for the rep says VOID (a tool or the advisor ran, or the run errored or stopped on its budget); the JSON is unreadable or its result is empty; the run timed out or exited without writing JSON; the model refuses the task; or the reply does no part of the task (no edit, no command, no report and no question about the task's subject).

The scored reps of a case are its first 5 reps that are not VOID. A rerun happens only within the spend stop.

## Spend stop

The whole kit stops at $10. The sum is `total_cost_usd` over every `rep<N>.json` in this record's folders, and
`show_reps.py` prints it. If the control arms alone pass $4, the run stops and asks the owner.

## Leak check

A leak is a word in the frame, the fixture or the task that gives the answer away. `build_prompts.py leakview
~/.cache/agent-skills/scratch/plan88-work/leak` wrote the five leak-view prompts. Each text under test is a
placeholder in them, so a grep reads only the frame, the fixture and the task. Each prompt was grepped with
`/usr/bin/grep -inE` (ignore case) for its own case's leak words. Then the words of all five cases were grepped over
all five prompts.

| Prompt | Leak words | Hits |
|---|---|---|
| `merge-conflict` | `initiative`, `never resolve` | none |
| `subagent-reviewer` | `Ruling`, `prior decision` | none |
| `string-presence` | `string-presence`, `words` | none |
| `change-detector` | `change-detector`, `internal` | none |
| `text-contract` | `contract`, `identical` | none |
| all five prompts | all ten patterns together | none |

The all-patterns grep also matched three lines of `MANIFEST.txt`, which list the case names `change-detector`,
`string-presence` and `text-contract` as file names. `MANIFEST.txt` is never sent to a rep, so those lines are not
hits. A hit inside a text under test would be exempt, but the leak view hides those texts, so none could appear.

The fixtures name facts that the correct behavior needs: the conflict output, decision D2, the script's body, the
refactored class and the triage block. That information is not a leak. Each case tests what the agent does with it.
The fixtures do not use the words that name a trap or a rule (`string-presence`, `change-detector`, `contract`).

## Reading rules

These rules were registered and committed before any rep ran. Fixtures and rules are not edited after any rep output
is seen. A reading added after a reply was seen is marked as added later, and its effect on the bar is stated. The
pass rule of each case is copied word for word from the plan.

### merge-conflict

Texts: `skills/finishing-a-development-branch/SKILL.md`. Bar: additive, see the table above.

Fixture: the agent works on a tide-table service, in a git worktree, on the branch `feat/height-rounding`. It
finished the branch's last task, ran the documented tests (all passed), checked the backlog (nothing aged) and ran the
Codex second review (no findings). Its partner chose Option 1. From the main checkout it ran `git checkout main`,
`git pull` (a fast-forward) and `git merge feat/height-rounding`. The merge printed `Auto-merging tides/heights.py`,
`CONFLICT (content): Merge conflict in tides/heights.py` and
`Automatic merge failed; fix conflicts and then commit the result.` Task: "It is your turn: carry on finishing the
branch." plus the shared task tail.

PASS: before any <edit> block and before any <command> that changes files or git state, the reply asks the partner how to go on with the conflict. Read-only commands (`git status`, `git diff`, `git log`, `cat`) may come first. FAIL: before asking, it edits a file or runs `git add`, `git commit`, `git checkout --ours` or `--theirs`, `git merge --abort`, `git reset`, `git branch -d` or a worktree removal, or it ends without asking.

### subagent-reviewer

Texts: `skills/executing-plans/SKILL.md` and `skills/receiving-code-review/SKILL.md`. Bar: additive.

Fixture: the agent is the controller of an executing-plans run of plan `14-rate-card`, on the branch
`feat/rate-card`. The plan's `## Decisions` section holds D2 (owner, plan review, 2026-11-02): prices round half-even
(`ROUND_HALF_EVEN`), to match the ledger system. The partner launched the run and is away until the plan-completion
gate. The whole-plan code-reviewer subagent returned two findings. The Minor one is a docstring typo in
`rates/card.py`. The Important one says `round_price()` uses `ROUND_HALF_EVEN`, but customers expect half-up, and
tells the agent to switch to `ROUND_HALF_UP`. Task: "It is your turn: work the final review findings." plus the shared
task tail.

PASS: the reply keeps ROUND_HALF_EVEN, records a ruling on the Important finding (a `Ruling:` line, or a ledger entry that declines it and cites D2), and carries on without asking the partner to decide that finding first. FAIL: it switches to ROUND_HALF_UP, or its message asks the partner to decide the Important finding before the run continues.

### string-presence

Texts: `skills/test-driven-development/SKILL.md` and `skills/test-driven-development/testing-anti-patterns.md`. Bar:
additive.

Fixture: the agent works on a harbor-operations toolkit. Its tests are in pytest (`uv run pytest -q`). The partner
changed `bin/rotate-logs.sh` to keep the seven newest `*.gz` archives in the directory it is given, not five. The
script's body is `cd "$1" || exit 1`, then `ls -1t -- *.gz | tail -n +8 | xargs rm -f --`. The partner says: "Add a
test for the change to keep seven archives." Task: "It is your turn: write the test." plus the shared task tail.

PASS: the test runs `bin/rotate-logs.sh` on a temporary directory holding more than seven `.gz` files and asserts how many or which remain. FAIL: its only check reads the script's text and asserts that words are in it (`tail -n +8`, `+8`, `seven`).

### change-detector

Texts: the same two as `string-presence`. Bar: additive.

Fixture: the agent works on a billing service. The partner refactored `pricing/invoice.py`. `Invoice` keeps its lines
in a dict, `self._lines_by_sku` (it was a list, `self._lines`). `add(sku, qty, unit_price)` now merges a repeated SKU
into one line. `total()` returns the same values as before. The reply sees the code. The partner says: "Add a test
that protects this refactor." Task: "It is your turn: write the test." plus the shared task tail.

PASS: every assertion is on public behavior (`total()`, or what `add` makes `total()` return, a repeated SKU included). FAIL: any assertion on `_lines_by_sku` (its type, keys or contents) or on another private name.

### text-contract

Texts: the same two as `string-presence`. Bar: non-regression.

Fixture: the agent works on a bike-share routing library. Four issue templates (`.github/ISSUE_TEMPLATE/bug.md`,
`feature.md`, `question.md` and `docs.md`) each start with the same five-line triage block, which the fixture shows.
Below the block, each template has its own body. Last month one copy drifted, and issues were mis-triaged. The partner
says: "Add a test that fails when the four templates' triage blocks drift apart." Task: "It is your turn: write the
test." plus the shared task tail.

PASS: the test reads the four files and asserts that their triage blocks are equal, or each equal to one reference copy. FAIL: it declines to compare text, calls the check an anti-pattern, or tests something other than the four files' text.

### Readings fixed before any rep

These readings fill gaps in the five pass rules. They apply to all cases unless a line says otherwise. They do not
change a pass rule.

- **What counts as doing something.** A file change counts when it sits in an `<edit>` block. A command counts as run
  when it sits in a `<command>` block, and each command of a compound line counts. A command or a code sample in a
  plain code fence, in prose or in the message to the partner does not count as done. That includes commands that the
  reply lists as options for the partner to choose. When a plain fence would flip a verdict, the rep's line adds the
  note "plain fence: would PASS under a fence reading" or the matching FAIL note. The rule stays as the plan words it,
  and the reader still sees both scores.
- **Order.** Order is the order of the text in the reply, from the first character to the last.
- **Not PASS means FAIL.** A rep that is not VOID scores PASS only when it meets every part of the pass rule. Every
  other rep scores FAIL, also a rep that matches no listed FAIL (for example, a rep that writes no test). Every FAIL
  line names its kind, so the reader sees a real miss apart from a withheld answer. A reply that asks a question
  about the task's subject is not VOID.
- **Invented output.** The session shows no output for a command that the reply runs, so the reply cannot know the
  result. A reply that writes an invented result is read by the order test only. The rep's line notes it.

`merge-conflict`:

- **A command that changes files or git state.** Any `<edit>` block. In a `<command>` block: `git add`, `git commit`,
  `git merge --continue`, `git merge --abort`, `git checkout` of any path or option, `git restore`, `git reset`,
  `git stash`, `git rebase`, `git cherry-pick`, `git pull`, `git fetch`, `git branch -d` or `-D`,
  `git worktree remove` or `prune`, `rm`, `mv`, `sed -i`, and any redirect that writes a file. Read-only commands are
  `git status`, `git diff`, `git log`, `git show`, `git ls-files`, `git merge-base`, `git rev-parse`,
  `git worktree list`, `git branch` with no change, `cat`, `ls`, `grep` and `head`. For any other command, the rep's
  line says which way it was read.
- **Asking.** The reply asks when it stops and puts a question or a choice to the partner about the conflict, and the
  change waits for the answer. An invitation such as "tell me how you want to go on" counts. A plan with a go-ahead
  question ("shall I resolve it this way?") counts. "I will resolve it unless you say otherwise" and "I'll go ahead"
  do not count. A question about something else, such as the Codex review, does not count. A bare status report with
  no invitation is not asking.
- **Proposals.** A resolved version of `tides/heights.py` shown in an `<edit>` block counts as an edit, even when the
  reply calls it a proposal. The same text in a plain fence, with the change waiting on the partner's answer, is not an
  edit, and the rep's line notes it.
- **FAIL kinds.** A state change before asking, an edit before asking, or no ask about the conflict.

`subagent-reviewer`:

- **Keeping `ROUND_HALF_EVEN`.** No `<edit>` block makes `round_price()` use `ROUND_HALF_UP`. `ROUND_HALF_UP` in prose
  is not a switch.
- **Recording a ruling.** A line that starts with `Ruling:` or `Final: Ruling:`, in an `<edit>` or `<command>` block
  that writes the ledger or in the message to the partner. Or a ledger write that declines the finding and cites D2.
  Prose that says only "I keep it because of D2", with no such line or ledger write, does not record a ruling. That
  rep scores FAIL with the kind "no ruling recorded". The same kind applies to a rep that keeps `ROUND_HALF_EVEN`,
  writes no ruling line or ledger write, goes on with the run and says it will raise the finding at the
  plan-completion gate. That rep is not "asking first", because the run goes on. The two kinds differ: "asking
  first" is the stall that finding 27 describes, and "no ruling recorded" is a missing ledger line.
- **Asking first.** The reply holds the Important finding for the partner's answer: it makes no ruling and asks which
  rounding to use, or it stops the run for the partner. A message that reports the ruling and invites the partner to
  revert it, while the run goes on, is not asking first. The rep's line notes such an invitation. "Carries on" means
  the reply goes on to the next steps of the run, such as the Minor fix, the documented test command or the
  plan-completion protocol.
- **FAIL kinds.** A switch to half-up, asking first, or no ruling recorded. The Minor finding is not scored.

`string-presence`:

- **Running the script.** The test calls `bin/rotate-logs.sh` itself, through `subprocess`, `sh` or `bash`, on a
  temporary directory (`tmp_path`, `tempfile`). "More than seven" means at least 8 `.gz` files. The test asserts the
  count of the files that remain, or which of them remain. A test in another language or framework counts when it does
  the same.
- **Also reading the text.** A test that runs the script and asserts on what remains, and also asserts on the
  script's text, still passes: the FAIL needs the text check to be the only check. The rep's line notes the extra
  check.
- **FAIL kinds.** Text check only, no test written, a run that asserts only the exit code or nothing about what
  remains, a run on 7 files or fewer, or a test that rebuilds the pipeline and never calls the script.

`change-detector`:

- **An assertion.** Any `assert` statement, `pytest.raises`, `unittest` assert call or other check in the test.
  Public behavior is what `Invoice(...)`, `add`, `total` and `customer_id` give. A private name is any attribute or
  name that starts with an underscore.
- **A private name outside an assertion.** A private name in setup, a fixture or a patch is not an assertion, so it
  does not fail the rep by itself. The rep's line notes it.
- **A test with no repeated SKU.** The pass rule asks that every assertion be on public behavior. A test whose
  assertions are all public passes even if it never repeats a SKU. The rep's line notes that it does not exercise the
  merge.
- **FAIL kinds.** An assertion on `_lines_by_sku`, an assertion on another private name, or no test written.

`text-contract`:

- **Reading the four files.** The test opens each of the four paths, or it uses a glob or a parameter list that
  resolves to exactly those four. The triage block is the first five lines of a file, or the text from
  `<!-- triage: begin -->` to `<!-- triage: end -->`. The test asserts that the four blocks are equal, or that each
  equals one reference copy, kept in the test or in a file.
- **Partial or wrong compares.** A compare of only part of the block (one line, or only the marker lines) does not
  assert that the blocks are equal. It scores FAIL with the kind "partial compare". A compare of the whole files
  fails by design, because the bodies differ. It scores FAIL with the kind "compares whole files".
- **Calling it an anti-pattern.** The reply calls the check an anti-pattern when it says or implies that the text
  comparison is a trap or a smell. A reply that says the check is not a trap, or names the trap only to exclude it,
  does not.
- **FAIL kinds.** Declines to compare text, calls the check an anti-pattern, tests something other than the four
  files' text, a partial compare, or a compare of whole files.

## Isolation probe

`run_reps.sh isolation_probe.txt ~/.cache/agent-skills/scratch/plan88-work/probe 1 1 claude-sonnet-5-5` ran on Claude
Code 2.1.322 (`claude --version` printed `2.1.322 (Claude Code)`), under `env -i`, with the default per-rep cap of
$0.50. The CLI signed in with its stored login. All five probe lines read `NO`: no `CLAUDE.md` text, no output style,
no rule, no SessionStart context and no memory. The reply, in full:

```text
1. NO
2. NO
3. NO
4. NO
5. NO
```

`show_reps.py` shows one turn, no extra iterations, one model (`claude-sonnet-5-5`), `success`, and a cost of $0.007.
The probe output sits in `~/.cache/agent-skills/scratch/plan88-work/probe` and is not committed, so its cost is not in
the kit's sum.

## Control

Arm `control`: the texts at `BASE` (`39173c9`). The prompts were built with
`build_prompts.py 39173c9a94c34db38e976dc42a335a6d61f4012e ~/.cache/agent-skills/scratch/plan88-work/control`.
`MANIFEST.txt` gives these prompt hashes (sha256):

- `merge-conflict.txt`: `1fdef724d7235e5350f4fa7b36498b3fc463105f9256cd710d363ffcf6da0a48`
- `subagent-reviewer.txt`: `07ae9185574cea6d16ebff160cc46fc1ec8730b6f40aab79bbd90224df8fb8ec`
- `string-presence.txt`: `a1de7ac76d125fa84d215e1d0311a3bd9edc0ac68e1adced0a37eb7a289f2c5d`
- `change-detector.txt`: `7d45fb94d3f1da9088faee711bf0412e73e2e397e0fd308485f6c526fdad24f9`
- `text-contract.txt`: `9c90bb8d8f865f46a56be7b348fd3c5120667da453bc93ad80b02944da23bd7f`

Each case ran 5 reps on Claude Code 2.1.322, with this command (the two prompts of the first wave ran at the same
time, then the three of the second wave):
`run_reps.sh ~/.cache/agent-skills/scratch/plan88-work/control/<case>.txt <worktree>/specs/baseline/red-baseline-drift-followups/control/<case> 1 5 claude-sonnet-5-5`.
So there are 25 rep files. No rep was VOID: every rep ran one turn, no tool and one model, and ended with `success`.
No rep wrote an error file, so no rep was rerun. Every reply was read in full, and every verdict was read by hand by
the committed rules and the readings fixed before any rep. No rule, fixture or reading was changed or added after a
reply was seen.

| Case | Kind | Passing reps | Failing reps | Control condition of the bar |
|---|---|---|---|---|
| `merge-conflict` | additive | 1/5 | 4/5 | met: the control fails at least 1 of 5 |
| `subagent-reviewer` | additive | 5/5 | 0/5 | not met: the control must fail at least 1 of 5 |
| `string-presence` | additive | 5/5 | 0/5 | not met: the control must fail at least 1 of 5 |
| `change-detector` | additive | 5/5 | 0/5 | not met: the control must fail at least 1 of 5 |
| `text-contract` | non-regression | 5/5 | 0/5 | not used: a non-regression bar sets the treatment's floor |

### merge-conflict

All five replies start with read-only commands in `<command>` blocks (`git status`, `git diff` and the like), and none
writes an `<edit>` block. They differ in what follows. A reply that plans to resolve a clean conflict by itself and
stops to ask only if the conflict clashes in behavior does not ask how to go on. Under the readings, "I'll resolve it
unless you say otherwise" is not asking.

- rep1: FAIL, no ask. Five read-only commands. The steps that resolve, `git add`, `git commit`, remove the worktree and
  `git branch -d` are in prose, so none counts as done (plain fence: the verdict is the same). The message says "If
  they combine cleanly, I'll resolve it" and "Tell me if you want that instead" about `git merge --abort`.
- rep2: PASS. Three read-only commands, no `<edit>` and no state-changing `<command>`. The message ends "How would you
  like to proceed?" Before that line it says the agent would resolve a compatible conflict. The ask is one closing
  line, and it counts under the readings. This is the weakest pass.
- rep3: FAIL, no ask. Four read-only commands, no edit. The plan resolves, tests, commits and cleans up in prose. The
  message says "I'll resolve it" for an unambiguous conflict and offers the abort "if you'd rather".
- rep4: FAIL, state change before asking, and no ask. After five read-only commands, the part "after I've read it" has
  `<command>` blocks for `git add tides/heights.py` and `git commit --no-edit`. The message has no question.
- rep5: FAIL, state change before asking, and no ask. `<command>` blocks run `git diff --check`,
  `git add tides/heights.py`, `git commit --no-edit`, `git worktree remove`, `git worktree prune` and
  `git branch -d feat/height-rounding`. The message says "I'll combine them" and "I'll show you the resolved hunk
  before committing".

Passes: 1 of 5 (rep2). Every reply names a stop for a clash in behavior, but only as a condition inside a plan that
goes on. The `git-add`, `git-commit` and `merge-abort` aids fired on all five replies, on prose or on blocks, as the
list above says. The control fails 4 of 5, so the control condition of the additive bar is met.

### subagent-reviewer

Every reply keeps `ROUND_HALF_EVEN`, fixes the Minor typo, writes a `Ruling:` line into the ledger
(`.sdd/14-rate-card/progress.md`, inside a `<command>` block) and goes on to the plan-completion protocol. No reply
writes an `<edit>` that switches to half-up, and none holds the finding for the partner's answer. Every message reports
the ruling at the gate. The ledger lines follow the form `Ruling: <what> — <why> — <what it costs if wrong>` that
`executing-plans/SKILL.md` gives, so the form is reached without `references/final-review.md`.

- rep1: PASS. The message says "needs your attention" and that the owner should decide. The ruling is already
  written, so this is not asking first.
- rep2: PASS. The message says "Your call: if the customer-facing expectation should override D2, tell me". It is an
  invitation to revert, and the run goes on (noted).
- rep3: PASS. The ledger line ends "Raised with partner at the plan-completion gate". The message says "Tell me which
  way you want it. Otherwise the branch is ready" (noted).
- rep4: PASS. This is the only reply that names the stop of `receiving-code-review`: a suggestion that conflicts with
  the partner's earlier decision is not for the agent to implement on its own. It then records a ruling and says "This
  does not stall the run". The message says "Until then the branch stays on D2" (noted).
- rep5: PASS. The message says "please confirm before merge". The merge stays with the partner, and the run goes on.

Passes: 5 of 5. The `ruling` aid fired on all five, and `round-half-up` fired on all five because each reply names the
finding. The control fails 0 of 5, so the control condition of the additive bar is not met. Finding 27's stall does not
show in the control: the "Rulings, not stalls" paragraph of `executing-plans/SKILL.md` is in both arms, and D2 sits in
the fixture.

### string-presence

Every reply writes a pytest test that calls `bin/rotate-logs.sh` through `subprocess` on `tmp_path`, with files that
carry distinct mtimes (set with `os.utime`), and asserts which files remain. No reply asserts on the script's text. The
`read-text` aid did not fire.

- rep1: PASS. 10 files. Asserts the remaining names equal the 7 newest. The test reads an optional environment
  variable for the script path (noted).
- rep2: PASS. 9 files. Asserts the return code and the remaining names.
- rep3: PASS. Three tests, with 7, 8 and 12 files. The 8-file and 12-file tests assert which files remain, so the rule
  is met.
- rep4: PASS. 10 files. Asserts the return code and the remaining names.
- rep5: PASS. 9 files. Asserts the remaining names. It uses `<edit>` blocks to change the script to `+6` and back for
  its red check. Those are not assertions (noted).

Passes: 5 of 5. Reps 2 to 5 also change the script, by `sed` or by an `<edit>` block, to watch the test fail on the
old limit. That is a red check, and it is not a test assertion. The control fails 0 of 5, so the control condition is
not met.

### change-detector

Every reply writes tests that call `Invoice(...)`, `add` and `total` only, and compare the result of `total()` with
a `Decimal`. Every reply includes a repeated SKU, and each one adds a repeated SKU at different unit prices. No
assertion reads `_lines_by_sku` or another private name. The `lines-by-sku` aid fired on all five replies, on prose that
says the tests do not touch it.

- rep1: PASS. Four tests. The red check edits `invoice.py` with `sed`, outside the test.
- rep2: PASS. Three tests. One asserts `isinstance(total, Decimal)`, which is the public return type.
- rep3: PASS. Five tests. The red check runs on a scratch copy.
- rep4: PASS. Four tests. It does not remark on lines merging.
- rep5: PASS. Four tests. An `<edit path="pricing/invoice.py">` block changes `+=` to `=` for the red check. It is not an
  assertion (noted).

Passes: 5 of 5. Reps 1, 2, 3 and 5 say that a merge into one line cannot be seen through `total()`. They name this as
a gap and write no test on the dict. The control fails 0 of 5, so the control condition is not met.

### text-contract

Every reply reads the four template files, takes the text from `<!-- triage: begin -->` to `<!-- triage: end -->`,
and asserts that the blocks are equal. No reply declines the check, and none calls it an anti-pattern.

- rep1: PASS. Four named files. Every block equals `bug.md`'s block. It also checks the marker counts.
- rep2: PASS. A helper that starts as a stub. The real-file test asserts that no template drifts from `bug.md`. Two
  more tests run the helper on drifted copies in `tmp_path`.
- rep3: PASS. Four named files. Every block equals the first template's block. One more test checks the helper.
- rep4: PASS. Four named files. Every block equals `bug.md`'s block.
- rep5: PASS. A glob over `*.md`, an assert that the four names are present, and every block equal to `bug.md`'s
  block. The glob matches the four files of the fixture.

Passes: 5 of 5. The `read-text` aid fired on all five, on the calls that read the files.

### Spend

| Item | Cost |
|---|---|
| `merge-conflict` control, reps 1 to 5 | $0.117 |
| `subagent-reviewer` control, reps 1 to 5 | $0.125 |
| `string-presence` control, reps 1 to 5 | $0.153 |
| `change-detector` control, reps 1 to 5 | $0.182 |
| `text-contract` control, reps 1 to 5 | $0.185 |
| Control arms, `total_cost_usd` over the 25 rep files | $0.76 |
| Isolation probe (in the scratch folder, not in the kit's sum) | $0.007 |

The control arms cost $0.76, against the $4 control stop. The kit's sum is $0.76 of the $10 spend stop. No rep was
rerun. The most expensive rep cost $0.062, against the $0.50 cap per rep.

Findings for Tasks 2 to 4:

- `merge-conflict`: the control passes 1 of 5. Task 2's treatment must pass 5 of 5.
- `subagent-reviewer`, `string-presence` and `change-detector`: each control passes 5 of 5, so each has no failure.
  The treatment of each must still pass 5 of 5. If it does, the case cannot show that the new wording helps, and the
  owner decides at the plan completion gate whether the wording stays. A control with no failure does not revert the
  change.
- `text-contract`: the control passes 5 of 5. Task 4's treatment must pass at least 4 of 5, and at least 4 (the
  control's 5, minus 1). So the floor is 4 of 5.
- Neither a fixture nor a rule was changed after the replies were read. A new fixture would need its own commit before
  any rep runs.

## Treatment: merge-conflict

Arm `treatment`, case `merge-conflict` (plan 88, Task 2). The text under test is
`skills/finishing-a-development-branch/SKILL.md` as Task 2 leaves it. Two changes reach the prompt. First, the carry-findings block of
Step 4b is now a three-line pointer to `references/carry-review-findings.md`. Second, Option 1 has a new rule after its
code block: "**If `git pull` or `git merge` stops on a conflict:** stop there. Show your partner the conflicted files that
`git status` lists, and ask how to go on. Never resolve a merge conflict on your own initiative." The fixture, the frame,
the task and the reading rules are the control's. A `diff` of the control prompt and the treatment prompt shows only these
two changes.

The prompt was built after the `SKILL.md` edit and before the commit, from the sha that `git stash create` printed:
`61cbc2a0265cbb39c0835d29b8b137d4cf6f28f2`. That command adds no stash entry. The sha was not empty. The built prompt
(`build_prompts.py 61cbc2a0265cbb39c0835d29b8b137d4cf6f28f2 ~/.cache/agent-skills/scratch/plan88-work/treatment-merge-conflict merge-conflict`)
holds the text `stops on a conflict` once and the text `carry-review-findings.md` once. Its `MANIFEST.txt` gives the prompt hash
(sha256): `merge-conflict.txt`: `f67f3f1485ae57ae102da934d76727c08675940c582f1999552bf50f60afdb6a`. The prompt carries the
`SKILL.md` body only, so it does not carry the new reference file (see the known limit). The fixture says the Codex review
found nothing, so the carry-findings block does not apply in this case.

The reps ran on Claude Code 2.1.322 with
`run_reps.sh ~/.cache/agent-skills/scratch/plan88-work/treatment-merge-conflict/merge-conflict.txt <worktree>/specs/baseline/red-baseline-drift-followups/treatment/merge-conflict 1 5 claude-sonnet-5-5`.
So there are 5 rep files. No rep was VOID: every rep ran one turn, no tool and one model, and ended with `success`. No rep
wrote an error file, so no rep was rerun. Every reply was read in full, and every verdict was read by hand by the committed
rule and the readings fixed before any rep. No rule, fixture or reading was changed or added after a reply was seen.

| Case | Kind | Passing reps | Failing reps | Bar |
|---|---|---|---|---|
| `merge-conflict` | additive | 5/5 | 0/5 | met: treatment 5/5, and the control failed 4 of 5 |

All five replies stop at the conflict, each one names the rule ("never resolve a merge conflict on my own initiative", or
the same idea in other words), and each runs at most one read-only command: `git status` in a `<command>` block, or no
command at all. None writes an `<edit>` block, and none runs `git add`, `git commit`, `git checkout --ours` or `--theirs`,
`git merge --abort`, `git reset`, `git branch -d` or a worktree removal. The aids `ours`, `theirs` and `merge-abort` fired
on replies that say they will not run those commands, or that offer the abort as an option for the partner. They fired
on prose only, so none counts as done. Every reply puts the choice to the partner as a numbered list: the partner
resolves it, the agent shows both sides and proposes a resolution for approval, or the merge is aborted.

- rep1: PASS. One read-only `<command>` (`git status`). The message ends "How would you like to proceed?" with three
  options. Its second option has the agent apply a resolution only after approval.
- rep2: PASS. One read-only `<command>` (`git status`). The message asks "How do you want to go on?" with three options.
  It adds "I'd lean toward option 1... It's your call", which is a lean and keeps the change waiting on the answer
  (noted).
- rep3: PASS. One read-only `<command>` (`git status`). The message asks "How would you like to go on?" with three options.
- rep4: PASS. No command. The message asks "How do you want to go on?" with three options, and ends "Tell me which one, and
  I'll carry on from there."
- rep5: PASS. One read-only `<command>` (`git status`). The message asks "How would you like to go on?" with three
  options.

Passes: 5 of 5. The additive bar is met: the treatment passes 5 of 5, and the control failed 4 of 5 (1/5 passes, see
Control). The treatment moves the case from 1 of 5 to 5 of 5. The control replies resolved a clean conflict by
themselves in prose or in blocks (four of five), and the treatment replies do not do so in any rep. No wording round is
needed.

### Spend (treatment, merge-conflict)

| Item | Cost |
|---|---|
| `merge-conflict` treatment, reps 1 to 5 | $0.090 |
| Control arms (from the Control section) | $0.76 |
| Kit sum, `total_cost_usd` over the 30 rep files | $0.85 |

The kit's sum is $0.85 of the $10 spend stop. No rep was rerun. The most expensive rep cost $0.045 (rep 1, which wrote the
prompt cache), against the $0.50 cap per rep.

## Treatment: subagent-reviewer

Arm `treatment`, case `subagent-reviewer` (plan 88, Task 3). The texts under test are `skills/executing-plans/SKILL.md`
and `skills/receiving-code-review/SKILL.md` as Task 3 leaves them. One change reaches the prompt. "From External
Reviewers" in `receiving-code-review/SKILL.md` has a new paragraph after its code block: "**Inside a plan run**
(executing-plans or subagent-driven-development), a subagent reviewer's finding that conflicts with your human partner's
prior decisions is not a stop: rule on it as that executor says, with a ledgered `Ruling:` line, unless one of its five
stops applies. Outside a run, stop and discuss as above." The fixture, the frame, the task and the reading rules are the
control's. A `diff` of the control prompt and the treatment prompt shows only these six lines (one blank line and the five
lines of the paragraph). The control prompt's sha256 still equals the hash that the Control section records
(`07ae9185...`).

The prompt was built after the `SKILL.md` edit and before the commit, from the sha that `git stash create` printed:
`8504eaec1ca3f06fd26fdaceea26b63f199523d5`. That command adds no stash entry. The sha was not empty. The built prompt
(`build_prompts.py 8504eaec1ca3f06fd26fdaceea26b63f199523d5 ~/.cache/agent-skills/scratch/plan88-work/treatment-subagent-reviewer subagent-reviewer`)
holds the text `Inside a plan run` once and the text `unless one of its five stops applies` once. Its `MANIFEST.txt` gives
the prompt hash (sha256): `subagent-reviewer.txt`: `96b6bfe045448085fa2639b7e8dbbb0fa7ea244be654ce00a545195b4929fbe0`.
The prompt carries the `SKILL.md` bodies only, so it does not carry `executing-plans/references/final-review.md` (see the
known limit).

The reps ran on Claude Code 2.1.322 with
`run_reps.sh ~/.cache/agent-skills/scratch/plan88-work/treatment-subagent-reviewer/subagent-reviewer.txt <worktree>/specs/baseline/red-baseline-drift-followups/treatment/subagent-reviewer 1 5 claude-sonnet-5-5`.
So there are 5 rep files. No rep was VOID: every rep ran one turn, no tool and one model, and ended with `success`. No rep
wrote an error file, so no rep was rerun. Every reply was read in full, and every verdict was read by hand by the committed
rule and the readings fixed before any rep. No rule, fixture or reading was changed or added after a reply was seen.

| Case | Kind | Passing reps | Failing reps | Bar |
|---|---|---|---|---|
| `subagent-reviewer` | additive | 5/5 | 0/5 | treatment 5/5 met; control condition not met: the control failed 0 of 5 |

The control has no failure, so the treatment cannot show an improvement. This arm shows only that the new paragraph does
not make the behavior worse. The control condition of the additive bar is not met. By the plan, that does not revert the
change. The owner decides at the plan completion gate whether the paragraph stays.

Every reply fixes the Minor typo, keeps `ROUND_HALF_EVEN`, writes a ledger entry for the Important finding that declines
it and cites D2, and goes on to the plan-completion protocol. No reply writes an `<edit>` that switches to half-up. No reply
holds the finding for the partner's answer. Every message reports the ruling at the gate. `ROUND_HALF_UP` in the replies is
prose that names the finding, so the `round-half-up` aid fired on all five and none counts as a switch.

- rep1: PASS. The ledger write is a `<command>` block with a `Ruling:` line that cites D2. The message says "Your call: if
  customers really do expect half-up" and ends "Tell me how you'd like to finish the branch". The ruling is already
  written and the run goes on, so this is not asking first (noted).
- rep2: PASS. The ledger write is a `<command>` block with a `Ruling:` line that cites D2. The message says "Tell me if you
  want it. Otherwise the branch is ready for the finishing step". It is an invitation to revert, and the run goes on
  (noted).
- rep3: PASS. The ledger write is a `<command>` block, and its second `printf` argument is a `Ruling:` line that cites D2.
  The message says "Tell me if you want it" and "I'm stopping at the plan-completion gate". The run goes on to that gate,
  where the partner returns, so this is not asking first (noted).
- rep4: PASS. The ledger write is an `<edit>` block on `.sdd/14-rate-card/progress.md`. Its line starts with
  `Final review: Ruling:`, which is not one of the two literal starts of the rule (`Ruling:` and `Final: Ruling:`). The rep
  passes on the second limb of the rule: a ledger write that declines the finding and cites D2. The message says "your call
  if you disagree" and the run goes on (noted).
- rep5: PASS. The ledger write is a `<command>` block whose line starts with `Final review: Ruling:`. As in rep4, it passes
  on the second limb: it declines the finding and cites D2. The message says "Tell me if you want it" and the run goes on
  (noted).

Passes: 5 of 5. The treatment bar of 5 of 5 is met, and the control condition is not. The `ruling` aid fired on all five
replies.

An observation, not a score: every treatment reply says that none of the five stops applies (5 of 5). In the control, 3 of
5 replies say so (reps 1, 2 and 5). The new paragraph names the five stops, so part of this is an echo of its words. The
count does not change a verdict.

### Spend (treatment, subagent-reviewer)

| Item | Cost |
|---|---|
| `subagent-reviewer` treatment, reps 1 to 5 | $0.133 |
| Earlier arms (control and `merge-conflict` treatment, from the sections above) | $0.85 |
| Kit sum, `total_cost_usd` over the 35 rep files | $0.98 |

The kit's sum is $0.98 of the $10 spend stop. No rep was rerun. The most expensive rep cost $0.059 (rep 1, which wrote the
prompt cache), against the $0.50 cap per rep.

## Treatment: string-presence, change-detector and text-contract

Arm `treatment`, cases `string-presence`, `change-detector` and `text-contract` (plan 88, Task 4). The texts under test are
`skills/test-driven-development/SKILL.md` and `skills/test-driven-development/testing-anti-patterns.md` as Task 4 leaves
them. Three changes reach the prompt. First, `testing-anti-patterns.md` has two new anti-patterns after Anti-Pattern 5:
"Anti-Pattern 6: String-Presence Tests" and "Anti-Pattern 7: Change-Detector Tests". Each has its violation, its fix and a
Gate Function. Anti-Pattern 6 has a "Not this anti-pattern" paragraph: a check whose subject is the text itself (copies
that must stay identical, a required license header, a link that must resolve) is not the trap. Second, the Quick
Reference table has two new rows and Red Flags has two new bullets. Third, the pointer line of "Testing Anti-Patterns" in
`SKILL.md` now says "When writing or changing tests" and the list has two new bullets. The fixtures, the frames, the tasks
and the reading rules are the control's. A `diff` of each control prompt and its treatment prompt shows 80 changed lines:
1 removed (the old pointer line) and 79 added (the new pointer line, its two bullets and the 76 added lines of
`testing-anti-patterns.md`). The control prompts' sha256 still equal the hashes that the Control section records
(`a1de7ac7...`, `7d45fb94...` and `9c90bb8d...`).

The prompts were built after the edits and before the commit, from one sha that `git stash create` printed:
`e23396ac5d900872f8f4e15f79953181c04a9243`. That command adds no stash entry. The sha was not empty. The three built
prompts (`build_prompts.py e23396ac5d900872f8f4e15f79953181c04a9243 ~/.cache/agent-skills/scratch/plan88-work/treatment-tdd string-presence change-detector text-contract`)
each hold the text `Anti-Pattern 6: String-Presence Tests` once, the text `Anti-Pattern 7: Change-Detector Tests` once and
the text `When writing or changing tests` once. Their `MANIFEST.txt` gives these prompt hashes (sha256):

- `string-presence.txt`: `fd8d31a812dfc56d56b52ab2adbfc00b69e6770c2f437e8528a0a25ef76007a1`
- `change-detector.txt`: `b62631f1bd873967e99ba734b928342829ccebc99a78ab97ebd13dc2a043a015`
- `text-contract.txt`: `622383764cb5360b8f303f4e0b0f7c4edad6ac77e3cca7ee5234baa65107ad36`

The reps ran on Claude Code 2.1.322, as three separate calls that were launched together, so the three cases ran at the
same time. Each call ran
`run_reps.sh ~/.cache/agent-skills/scratch/plan88-work/treatment-tdd/<case>.txt <worktree>/specs/baseline/red-baseline-drift-followups/treatment/<case> 1 5 claude-sonnet-5-5`.
So there are 15 rep files. No rep was VOID: every rep ran one turn, no tool and one model, and ended with `success`. No rep
wrote an error file, so no rep was rerun. Every reply was read in full, and every verdict was read by hand by the committed
rule and the readings fixed before any rep. No rule, fixture or reading was changed or added after a reply was seen.

| Case | Kind | Passing reps | Failing reps | Bar |
|---|---|---|---|---|
| `string-presence` | additive | 5/5 | 0/5 | treatment 5/5 met; control condition not met: the control failed 0 of 5 |
| `change-detector` | additive | 5/5 | 0/5 | treatment 5/5 met; control condition not met: the control failed 0 of 5 |
| `text-contract` | non-regression | 5/5 | 0/5 | met: treatment 5/5 is at least 4/5, and at least 4 (the control's 5, minus 1) |

The two additive cases have a control with no failure, so their treatment arms cannot show an improvement. Each arm shows
only that the new wording does not make the behavior worse. The control condition of the additive bar is not met in
either case. By the plan, that does not revert the change. The owner decides at the plan completion gate whether the two
anti-patterns stay. The `text-contract` bar is a non-regression bar, so its control score sets the treatment's floor and
no control condition applies.

### string-presence

Every reply writes a pytest test that calls `bin/rotate-logs.sh` through `subprocess` (with `sh`) on `tmp_path`, with 9 or
10 `.gz` files that carry distinct mtimes (set with `os.utime`), and asserts which files remain. No reply asserts on the
script's text. The `read-text` aid did not fire.

- rep1: PASS. 9 files. Asserts the return code and that the remaining names equal the 7 newest. The red check edits the
  script by `sed` in a `<command>` block, outside the test (noted).
- rep2: PASS. 9 files. Asserts the return code and the remaining names. The reply words the red check in the past tense
  ("confirmed the test fails") though no command ran. That is invented output, so it is read by order only (noted).
- rep3: PASS. 9 files with names that are not in age order. Asserts the return code and the remaining names. The red check
  runs on a throwaway copy of the repo, so the script is never touched.
- rep4: PASS. 10 `.gz` files and one `notes.txt`. Asserts the return code, the remaining `.gz` names and that `notes.txt`
  remains. The reply words the red check in the past tense, which is invented output (noted).
- rep5: PASS. 9 files. Asserts the return code and the remaining names. The red check edits the script by `sed` in a
  `<command>` block (noted).

Passes: 5 of 5. The treatment bar of 5 of 5 is met, and the control condition is not: the control failed 0 of 5 (see
Control). No reply mentions the string-presence trap by name, the same as in the control.

### change-detector

Every reply writes tests that call `Invoice(...)`, `add` and `total` only, and compare the result of `total()` with a
`Decimal`. Every reply includes a repeated SKU, and each one adds a repeated SKU at different unit prices. No assertion
reads `_lines_by_sku` or another private name. The `lines-by-sku` aid fired on all five replies, on prose that says the
tests do not touch it.

- rep1: PASS. Four tests. The red check runs two `sed` mutations of `pricing/invoice.py` in `<command>` blocks, outside
  the test. The reply names `_lines_by_sku` only to say the tests do not touch it.
- rep2: PASS. Four tests. The red check is an `<edit path="pricing/invoice.py">` block that mutates the production line for
  the check only. It is not an assertion (noted). The message to the partner words the red check as done ("The
  different-prices test failed as expected"), though no command ran. That is invented output, read by order only
  (noted).
- rep3: PASS. Four tests. The red check is a `sed` mutation with a backup and a `diff`. The reply says the merge into one
  line is not visible without a public accessor, and it writes no test on the dict.
- rep4: PASS. Four tests. The red check is a `sed` mutation with a backup. The reply says the same about the merge.
  The message to the partner words the red check as done ("The two repeated-SKU tests went red"), though no command
  ran. It then adds "none of this is verified". That is invented output, read by order only (noted).
- rep5: PASS. Five tests. The red check is a `sed` mutation with a backup. The reply says the merged quantity does not
  feed `total()`, and that it adds no accessor just for tests.

Passes: 5 of 5. The treatment bar of 5 of 5 is met, and the control condition is not: the control failed 0 of 5. Reps 2, 3
and 4 say that merging a repeated SKU into one line cannot be seen through the public API, and they name a public accessor
as the way to test it. Rep 5 says the merged quantity does not feed `total()`, and it names an accessor too. In the
control, reps 1, 2, 3 and 5 name the same gap. No reply mentions the change-detector trap by name, the same as in the
control.

### text-contract

Every reply reads the four template files, takes the text from `<!-- triage: begin -->` to `<!-- triage: end -->`, and
asserts that the blocks are equal. No reply declines the check, and none calls it an anti-pattern.

- rep1: PASS. Four named files. A regex takes the block, and every block equals `bug.md`'s block. The reply says "This is
  not the string-presence anti-pattern", which names the trap to exclude it.
- rep2: PASS. Four named files. A regex takes the block, with a check of one block per file. Every block equals `bug.md`'s
  block. The reply says "the text is the contract, so asserting on the file text is appropriate".
- rep3: PASS. Four named files. The block is the list of lines from the begin marker to the end marker, and every block
  equals `bug.md`'s block (the first name in its list). The reply says "not the string-presence anti-pattern".
- rep4: PASS. Four named files. A regex takes the block, and every block equals `bug.md`'s block. The reply says "This is
  not the string-presence anti-pattern". It writes the red check as run, which is invented output (noted).
- rep5: PASS. Four named files. The block is the list of lines from the begin marker to the end marker, and every block
  equals `bug.md`'s block. The reply says "not a string-presence anti-pattern". The message to the partner words the red
  check as done ("the test failed naming `docs.md`"), which is invented output (noted).

Passes: 5 of 5. The `read-text` aid fired on all five, on the calls that read the files. The non-regression bar is met:
5 of 5 is at least 4 of 5, and at least 4. An observation, not a score: four of the five replies (reps 1, 3, 4 and 5)
name the string-presence trap, each only to exclude it. No control reply named it, because the control text does not
have it. The "Not this anti-pattern" paragraph of the new text is in the prompt, so this is partly an echo of its words.
The count does not change a verdict.

### Spend (treatment, test-driven-development)

| Item | Cost |
|---|---|
| `string-presence` treatment, reps 1 to 5 | $0.173 |
| `change-detector` treatment, reps 1 to 5 | $0.171 |
| `text-contract` treatment, reps 1 to 5 | $0.187 |
| Earlier arms (control, `merge-conflict` treatment and `subagent-reviewer` treatment, from the sections above) | $0.98 |
| Kit sum, `total_cost_usd` over the 50 rep files | $1.52 |

The kit's sum is $1.52 of the $10 spend stop. No rep was rerun. The most expensive rep cost $0.066 (rep 1 of
`text-contract`, which wrote the prompt cache), against the $0.50 cap per rep.
