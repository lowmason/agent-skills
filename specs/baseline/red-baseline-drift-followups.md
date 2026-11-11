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
