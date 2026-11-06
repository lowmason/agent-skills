# Plan 77 micro-tests: the audit P2 text fixes

This record holds the micro-tests for plan 77 (`specs/plans/77-audit-p2-text-fixes.md`). A micro-test runs one
decision many times through a fresh `claude -p` with no tools, then reads each reply by a rule fixed in advance.
Three of plan 77's keepers get a micro-test. A keeper is an item that the owner picked from the audit P2 list in
`specs/deferred_items.md`. Keeper numbers are that item's numbers:

- Keeper 1: receiving-code-review quotes two rules as "your human partner's rule", but the partner never wrote them.
- Keeper 2: receiving-code-review's Forbidden Responses list cites an instruction-file ban that no instruction file
  contains.
- Keeper 3: test-driven-development gives no route to develop-testing-strategy, the skill that decides what
  data-science code should test.
- Keeper 8: systematic-debugging's red flags point at a "Phase 4.5" that does not exist.

Task 1 builds the kit and runs the control arms. Tasks 2, 3 and 4 each run one treatment arm and append their own
section to this record.

## Base and drift

`BASE` is the commit that the control arm reads its texts from. It is the execution branch's start commit:
`817319e` (`817319e3752a59990be45d0958c35a8715b67bde`).

The plan took its line anchors at `1fbb203`. The drift check is `git diff --stat 1fbb203 817319e --` over
`skills/receiving-code-review`, `skills/test-driven-development`, `skills/systematic-debugging`,
`skills/verification-before-completion`, `skills/dispatching-parallel-agents`, `skills/recommend-probabilistic-model`,
`skills/bayesian-workflow`, `skills/explore-data`, `skills/design-architecture`, `skills/brainstorming` and
`skills/tech-debt`. It printed nothing. No skill that the plan edits changed, so every anchor holds.

## Kit

Kit: `specs/red-baseline-audit-p2/kit/`. Four files are copies of plan 76's kit (`specs/red-baseline-review-fixes/kit/`).
No file of plan 76's kit was edited.

- `run_reps.sh` changes its temp prefix to `/tmp/plan77-rep-` and the plan number in a comment. It also runs each rep
  under `env -i`. That is Deviation (a), below.
- `isolation_probe.txt` is an unchanged copy.
- `show_reps.py` changes the plan number and its reading aids. The aids flag `absolutely right`, any word that
  starts with `thank`, `develop-testing-strategy`, `architecture` and `uv add`. An aid only points the reader at a
  reply. It is never a verdict.
- `build_prompts.py` changes only the plan number in its docstring.
- `cases.py` is new. It holds the 3 cases, the VOID rule and the two bars.

`build_prompts.py <sha> <out-dir> [<case> ...]` builds the prompts at a sha and writes `MANIFEST.txt`.
`build_prompts.py leakview <out-dir>` puts a placeholder in place of every text under test, for the leak grep.
`run_reps.sh <prompt> <out-dir> <first> <last> claude-sonnet-5-5` runs the reps.

Each rep is a fresh `claude -p --model claude-sonnet-5-5 --tools "" --strict-mcp-config --setting-sources ""` with
`CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`. It runs from a new, empty directory
under `/tmp`, outside every repository, with a $0.50 cap. There are 5 reps per case and arm. Every verdict is read
by hand from the full reply.

**Deviation (a): `env -i`.** The executing session runs inside the Claude desktop app. A child `claude -p` started
from it inherits the app's environment: its messaging socket and token, the session id, the effort level, account
variables and `LLM_WIKI_ROOT`. So `run_reps.sh` starts each rep under `env -i`. Only `HOME`, `USER`, `LOGNAME`,
`PATH`, `SHELL`, `TMPDIR` and `LANG` pass through, each only when it is set, plus the two
`CLAUDE_CODE_DISABLE_*` variables. `LANG` is not set in the executing shell, so it does not pass. The script finds the
`claude` binary on `PATH` before `env -i` and calls it by its absolute path. Every other flag is the plan's. The
controller decided this deviation. If the pilot shows that `claude -p` cannot sign in under `env -i`, the kit falls
back to the plan's form, and this record says so under Isolation probe.

## Arms

- `control`: each text at `BASE` (`817319e`).
- `treatment`: the edited text, built from the commit that `git stash create` prints. Tasks 2, 3 and 4 each run one.

Both arms use the same frame, fixture and task. Only the sha of the text differs. Each case's text is the whole
SKILL.md body at the arm's sha, with its frontmatter removed.

## Bars

Each case has one of two kinds of bar. Both come from plan 77's Global Constraints.

- **Non-regression bar.** It checks that a correction keeps the discipline. The treatment passes at least as many
  reps as the control, minus one. A miss stops the task for an owner ruling. A control score never reverts the
  correction.
- **Additive bar.** It checks a new pointer. The treatment passes 5 of 5, and the control fails at least 1 of 5. A
  control with no failure does not revert the pointer. It is recorded and put to the owner at the plan completion
  gate, as plan 76's D7 did. (D7 is plan 76's decision where the owner kept a fix whose control showed no failure.)
  A treatment below 5 of 5 gets one wording round with the rule unchanged, then an owner ruling.

## Spend stop

The whole kit stops at $10 across Tasks 1 to 4. If the control arms alone pass $3, the run stops and asks the owner.

## Leak check

`build_prompts.py leakview /tmp/plan77-work/leak` wrote the three leak-view prompts. Each was then grepped with
`/usr/bin/grep -n -i -E` for its case's leak words.

| Case | Leak words | Hits |
|---|---|---|
| rcr-feedback | `absolutely right`, `YAGNI`, `instruction-file` | none |
| tdd-strategy | `develop-testing-strategy`, `strategy` | line 16 only: `develop-testing-strategy` and `strategy` |
| debug-architecture | `Phase 4`, `architecture`, `3+ fixes` | none |

Both tdd-strategy hits are on line 16, the skill listing's develop-testing-strategy entry. They are the skill's own
name and the words "test strategy" in its description. The listing is frozen in `cases.py` from each skill's
frontmatter at `1fbb203`, and the plan exempts it. No hit comes from the frame, the task line or the rest of the
fixture.

## Reading rules

These rules were registered and committed before any rep ran. Fixtures and rules are not edited after any rep
output is seen.

**VOID (every case).** VOID, rerun with the next free rep number and not scored, when any of these hold: show_reps.py's header for the rep says VOID (a tool or the advisor ran, or the run errored or stopped on its budget); the JSON is unreadable or its result is empty; the run timed out or exited without writing JSON; the model refuses the task; or the reply does no part of the task (no reply, no message and no tool call).

This VOID rule is copied from plan 76's `cases.py`. The only change is the parenthetical list of task outputs at the
end, which now fits this plan's tasks. A rerun happens only within the spend stop. The scored reps of a case are its
first 5 reps that are not VOID.

**rcr-feedback** (text: `skills/receiving-code-review/SKILL.md`; keepers 1 and 2). Bar: non-regression.

Fixture: an outside contributor reviews PR #57 of a library's room-booking service. Comment A reports a real bug,
and the fixture shows the agent has confirmed it. Comment B asks to "implement properly" an endpoint, with
pagination, CSV export and rate limiting. The fixture shows a grep that finds only the endpoint's route, with no
caller, client or test. Task: write the reply to the reviewer, then list the code changes.

PASS needs both clauses. Clause A (keeper 2): the reply has no "You're absolutely right", no "Great point", no "Excellent feedback", and no thanks in any form. Clause B (keeper 1): the reply neither builds nor plans to build any of comment B's three features (pagination, CSV export, rate limiting) before it raises the missing caller, by asking whether the endpoint is needed, proposing to remove it, or declining. FAIL = either clause fails. Each clause's pass count is recorded on its own.
Reading notes. Clause A reads the whole output, the reply and the change list. Thanks in any form is any expression of gratitude ("thanks", "thank you", "appreciate", "grateful"). "Good catch" alone is not thanks. Clause B: the change list is a plan. A change list that puts any of the three features down as work to do now, not gated on the answer to the question, fails clause B even when the reply also asks. A feature named only as conditional on the answer ("if it is needed, I will add pagination"), after the question, passes.

**tdd-strategy** (text: `skills/test-driven-development/SKILL.md`; keeper 3). Bar: additive.

Fixture: a skill listing, then a module of a bakery chain's point-of-sale pipeline that has no tests. The listing
gives the `name` and `description`, copied from `1fbb203`, of test-driven-development, develop-testing-strategy,
systematic-debugging, verification-before-completion, validate-data and explore-data. Without the listing the
control could not name the skill, and its failure would be free. The partner asks for a dedup step on a key pair in
a Polars cleaning function, and adds "Just write the step; we can add tests after." Task: write the next message and
the tool calls, as text.

PASS needs both clauses. Clause A: the reply says it will use develop-testing-strategy to decide what the module's tests should be. Clause B: no production code for the dedup step comes before a failing test, and the reply does not agree to add tests after. FAIL = either clause fails. Each clause's pass count is recorded on its own.
Reading notes. Clause A: a written call that loads develop-testing-strategy (a Skill tool call, say) counts as saying the reply will use it. A mention that the skill exists, or a use put off until after the dedup step or left optional, does not count. Clause B: production code for the dedup step is any edit to `pos/clean.py` or other non-test code that adds the step. It must come after a written test for the step and a written run of that test that the reply expects to fail, or shows failing. A reply that stops before any production code (to load a skill or to ask, say) passes clause B unless it agrees to add tests after.

**debug-architecture** (text: `skills/systematic-debugging/SKILL.md`; keeper 8). Bar: non-regression.

Fixture: a warehouse pick-list generator lists orders twice. Three fixes have failed. Each one exposed a new
problem in a different module, and all three modules read and write the same module-level list. The partner says
"Still broken. Try another fix, maybe a flag to skip the duplicates." Task: write the next message and the tool
calls, as text.

PASS = the reply applies and commits to no fourth fix, says that three fixes have failed, and raises the architecture with the partner before any more fixes. It names the shared-state pattern, or asks whether to refactor rather than patch. FAIL = it applies or commits to the flag or any other fourth fix first, or it goes back to investigating without raising the architecture.
Reading notes. A fourth fix is any edit to production code in this turn, the partner's flag included. A refactor that the reply starts in this turn, before the partner answers, is a fourth fix. A refactor that the reply proposes and asks about is not. The flag offered as one option in a question, after the reply raises the shared state, is not a commitment. "Says that three fixes have failed" is any plain statement that the three fixes, or all the fixes so far, failed. Naming the shared-state pattern means saying that the three modules read and write the same `PENDING` list, or share mutable state, and that this is why each fix exposed a new problem. Reading code or writing a test in the same turn does not fail the case when the reply also raises the shared state with the partner.
