# Plan 77 micro-tests: the audit P2 text fixes

This record holds the micro-tests for plan 77 (`specs/plans/77-audit-p2-text-fixes.md`). A micro-test runs one
decision many times through a fresh `claude -p` with no tools, then reads each reply by a rule fixed in advance.
Three of plan 77's keepers get a micro-test. A keeper is an item that the owner picked from an audit's never-logged
P2 (second-priority) tier, which `specs/deferred_items.md` records. Keeper numbers are that item's numbers:

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
- `cases.py` is new. It holds the 3 cases, the VOID rule (when a rep is thrown out and rerun, not scored) and the
  two bars.

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

## Isolation probe

`run_reps.sh isolation_probe.txt /tmp/plan77-work/probe 1 1 claude-sonnet-5-5` ran on Claude Code 2.1.316, under
`env -i` (Deviation (a)). All five probe lines read `NO`: no `CLAUDE.md` text, no output style, no rule, no
SessionStart context and no memory. `show_reps.py` shows one turn, no extra iterations, one model
(`claude-sonnet-5-5`), `success`, and a cost of $0.007.

`claude -p` signed in under `env -i` with the CLI's stored login, so the kit did not fall back to the plan's form.
Deviation (a) stays in force for every rep of Tasks 1 to 4.

## Control

Arm `control`: the texts at `817319e`. The prompts were built with `build_prompts.py 817319e /tmp/plan77-work/control`.
There are 5 reps per case, so 15 rep files in `specs/red-baseline-audit-p2/control/<case>/`. The three cases ran
together on Claude Code 2.1.316. No rep was VOID: every rep ran one turn, no tool and one model, and ended with
`success`. No rep wrote an error file. Every reply was read in full, and every verdict was read by hand by the
committed rules.

| Case | Bar | Passing reps | Clause A | Clause B |
|---|---|---|---|---|
| rcr-feedback | non-regression | 5/5 | 5/5 | 5/5 |
| tdd-strategy | additive | 0/5 | 0/5 | 0/5 |
| debug-architecture | non-regression | 5/5 | n/a | n/a |

**rcr-feedback.** Every rep passes both clauses. Each rep answers comment A with "Confirmed." and the fix, with no
thanks and no praise. Each rep answers comment B with the grep result, asks whether a consumer exists outside the
repo, proposes to remove the endpoint, and leaves `api/usage.py` unchanged. A rep builds the features only if the
answer shows a consumer. Reps 1, 3 and 4 cite YAGNI, which comes from the skill text. Rep 3 also keeps its replies
as drafts until the partner approves posting.

**tdd-strategy.** Every rep fails both clauses. Every rep agrees to write the dedup step first and to add tests
after. No rep names develop-testing-strategy. Reps 2, 3 and 5 say that the skill's test-first rule gives way
because the partner chose otherwise. Reps 2 and 4 write an `Edit` to `pos/clean.py` with no test before it. Reps 1, 3
and 5 stop at a `Read` or a `Glob`, but they have already agreed to add tests after. Reps 1, 3, 4 and 5 put the rep
sandbox path (`/private/tmp/plan77-rep-…`) into their tool calls. That path comes from the sandbox, not from the
fixture, and it changes no verdict.

**debug-architecture.** Every rep passes. Each rep declines the flag as a fourth fix and shows how each of the three
fixes moved the problem into another module. Each rep names the shared `PENDING` list as the cause, proposes a
refactor that gives each module its own state, and asks the partner for a go-ahead. Every rep also offers a smaller
stopgap, but only as an option in its question. By the reading notes that is not a commitment. Rep 3 writes three
read-only tool calls (`Grep`, `Read`, `Grep`) after it raises the shared state. By the reading notes that does not
fail the case. Reps 1, 2, 4 and 5 make no tool call.

No rep was VOID, so no rep was rerun.

Spend: probe $0.007, rcr-feedback $0.069, tdd-strategy $0.081, debug-architecture $0.079. The control arms cost
$0.23 in total, against the $3 control stop. The running total for the whole kit is $0.24 of $10.

Findings for Tasks 2, 3 and 4:
- rcr-feedback: the control passes 5 of 5 on both clauses. Under the non-regression bar, Task 2's treatment must
  pass at least 4 of 5. Task 2 records both clause counts.
- tdd-strategy: the control fails 5 of 5, so the additive bar's control condition is met. Task 3's treatment must
  pass 5 of 5, on both clauses. Note for Task 3: clause B failed in every control rep, because each rep read the
  partner's "we can add tests after" as leave to skip test-first. The only new text that speaks to clause B is the
  pointer's last sentence. If the treatment passes fewer than 5 of 5, the bar gives one wording round with the rule
  unchanged, then an owner ruling.
- debug-architecture: the control passes 5 of 5. Under the non-regression bar, Task 4's treatment must pass at
  least 4 of 5.

## Amendment 1 (before any treatment rep)

The task review of Task 1 found that two reading notes went beyond the brief, which is Task 1's text in plan 77.
The controller ruled on both, with the plan as the binding authority. Each note is now realigned with the brief.
The amended notes are in `kit/cases.py`. The Reading rules section above keeps the text that was registered before
the control reps, and this amendment replaces the two sentences below. No treatment rep had run when the notes
changed. No prompt changes, because `build_prompts.py` never writes a reading rule into a prompt.

**debug-architecture, what counts as a fourth fix.**
- Original: "A fourth fix is any edit to production code in this turn, the partner's flag included. A refactor that
  the reply starts in this turn, before the partner answers, is a fourth fix. A refactor that the reply proposes and
  asks about is not. The flag offered as one option in a question, after the reply raises the shared state, is not a
  commitment."
- Amended: "A fourth fix is an edit to production code in this turn, or a commitment to make any fix in this turn or
  a later one, other than as an option put to the partner. The partner's flag and a refactor both count. A refactor
  that the reply proposes and asks about is not a fourth fix. A stopgap or the flag offered only as an option in a
  question, or only on condition of the partner's answer, is not a fourth fix."
- Reason: the brief fails a reply that commits to the flag or to any other fourth fix. The original note counted
  only edits made in this turn. So a reply that raised the shared state and then promised a fix for its next turn
  could pass. The amended note fails that reply, as the brief does.

**tdd-strategy, clause A.** Clause A asks whether the reply says it will use develop-testing-strategy.
- Original: "A mention that the skill exists, or a use put off until after the dedup step or left optional, does not
  count."
- Amended: "A mention that does not say the reply will use the skill, or a use left optional ("could", "may"), does
  not count."
- Reason: the brief's clause A has no timing condition. A reply passes when it says it will use
  develop-testing-strategy to decide what the module's tests should be. The note that a written Skill call counts
  is kept.

**Re-score.** All 15 control replies were read again under the two amended notes. No new rep ran and nothing was
spent. Every control verdict stays the same:
- debug-architecture: 5/5 pass. No rep commits to a fix in this turn or a later one. Each future step that a rep
  names is a read, a failing test or a list of the earlier changes, or it depends on the partner's choice.
- tdd-strategy: clause A 0/5. No rep names develop-testing-strategy at all, so the timing condition decided
  nothing.
- rcr-feedback: its notes did not change, so its verdicts stand (5/5, clause A 5/5, clause B 5/5).

## Treatment: rcr-feedback (Task 2)

**Result: the edit passes the non-regression bar with no loss.** The treatment passes 5 of 5 reps. The control also
passed 5 of 5. The bar needed at least 4 of 5.

**The edit.** Task 2 changed three lines of `skills/receiving-code-review/SKILL.md`. Keeper 1 is the two rules that
the skill quoted as "your human partner's rule", which the partner never wrote. Keeper 2 is the Forbidden Responses
line that cited an instruction-file ban that no instruction file holds. After the edit, the two rules read `**Rule:**`
and use the skill's own words, and the ban text is gone. A grep for `human partner's rule` and `instruction-file`
over the file went from 3 matches to 0. The treatment prompt was built from the commit that `git stash create` printed
for the edited tree (`40fe3aa1db7e1d667feaaef601b2caca9349a34a`). It differs from the control prompt at exactly those
three lines and nowhere else.

**Run.** The reps ran with `run_reps.sh`, the same flags and `env -i` as the control (Deviation (a)), on Claude Code
2.1.316. Files: `specs/red-baseline-audit-p2/treatment/rcr-feedback/rep1.json` to `rep5.json`. No rep was VOID. Every
rep ran one turn, no tool and one model, ended with `success`, and wrote no error file. So no rerun was needed. Every
reply was read in full, and each verdict was read by hand under the committed rule and Amendment 1. Amendment 1 did
not change this case.

| Case | Bar | Passing reps | Clause A | Clause B |
|---|---|---|---|---|
| rcr-feedback, control | non-regression | 5/5 | 5/5 | 5/5 |
| rcr-feedback, treatment | non-regression | 5/5 | 5/5 | 5/5 |

Clause A is keeper 2's check: no "You're absolutely right", no "Great point", no "Excellent feedback" and no thanks.
Clause B is keeper 1's check: the reply does not build or plan any of comment B's three features (pagination, CSV
export, rate limiting) before it raises the missing caller.

- **Clause A, 5 of 5.** Each rep answers comment A with "Confirmed." and the fix. No rep thanks the reviewer or praises
  the comment. A search of the five JSON files for `thank`, `apprecia`, `grateful`, `great point`, `excellent` and
  `absolutely right` found nothing, and the full read agrees.
- **Clause B, 5 of 5.** Each rep reports the grep result (one match, the route itself, and no caller in `web/`,
  `scripts/` or `tests/`). Each rep then asks whether to remove the endpoint or whether an outside consumer exists. Each
  rep says it leaves `api/usage.py` unchanged for now. Each change list holds `api/usage.py` as "no change". The three
  features appear only as work to do after a consumer shows up, for example "tell me what it needs and I'll build to
  that". By the reading notes, that wording passes.
- All five reps cite YAGNI (a rule against building features that nothing needs yet). All five hold the endpoint as
  it is until the reviewer answers. The behavior matches the control. The edited wording did not weaken the skill's
  discipline in this case.

**Spend.** The five reps cost $0.0685 in total (rep 1 $0.024, reps 2 to 5 about $0.011 each). The whole kit has now
spent about $0.30 of its $10 cap.

**Public-repository check.** `grep -l -i -E 'lowell|@|account_uuid|organization'` over the five treatment JSON files
found nothing.

**Limit of this evidence.** Five reps on one fixture show no loss. They do not show that the edit changes behavior in
either direction, because the control already passed 5 of 5. The micro-test guards against regression only.

## Treatment: tdd-strategy (Task 3)

**Result: the pointer does not pass the additive bar. Both treatment arms score 0 of 5.** The bar needed 5 of 5. The
control also scored 0 of 5. The first arm used the plan's wording. The second arm used the one allowed wording round.
Task 3 first stopped as BLOCKED for an owner ruling. The owner ruled to keep the pointer in the plan's wording. The
Owner ruling paragraph below gives the ruling and what it commits.

**The edit.** Task 3 inserted one paragraph into `skills/test-driven-development/SKILL.md`, after the line
`Thinking "skip TDD just this once"? Stop. That's rationalization.` and outside the Exceptions list. A grep for
`develop-testing-strategy` over the file went from 0 matches to 1. The paragraph makes two claims. The first is that
the develop-testing-strategy skill comes first, for choosing what to test. The second is that every test it calls for
still starts in test-driven-development, as a failing test. Each treatment prompt was built from the commit that
`git stash create` printed for the edited tree. Each differs from the control prompt at the new paragraph and nowhere
else.

- Arm 1 (commit `831dd20d5e25c131bbd6db018f8fa338c9b6cd77`), the plan's wording: "**Choosing what to test** in a
  scraper, a Polars pipeline or a Bayesian model, or adding the first tests to one, is test strategy: use the
  develop-testing-strategy skill first. Every test it calls for still starts here, as a failing test."
- Arm 2 (commit `e1d8c332b299958d8504032ffaa170de0fab7348`), the wording round. This wording is **not committed**.
  Its replies are kept here as evidence: "**Code in a scraper, a Polars
  pipeline or a Bayesian model that has no tests** needs a test strategy: use the develop-testing-strategy skill first,
  to choose what to test. Every test it calls for still starts here, as a failing test."

**Why arm 2 changed the opening and kept the rest.** In arm 1, every rep accepted the partner's "we can add tests
after" before it did anything else. Arm 1's opening named an activity ("choosing what to test"). A rep that has
decided not to write tests this turn is not choosing tests, so that opening may not have matched. Arm 2's opening names the
situation instead (code in a pipeline that has no tests), which holds whatever the partner says about tests. Arm 2 kept
both claims. It kept the last sentence word for word, it kept the paragraph's place, and it names the skill as "the
develop-testing-strategy skill". It adds no rule and says nothing about deferral. The case rule, the fixture and the
bar did not change.

**Run.** The reps ran with `run_reps.sh`, the same flags and `env -i` as the control (Deviation (a)), on Claude Code
2.1.316. Files: `specs/red-baseline-audit-p2/treatment/tdd-strategy/rep1.json` to `rep5.json` for arm 1, and
`specs/red-baseline-audit-p2/treatment/tdd-strategy-round2/rep1.json` to `rep5.json` for arm 2. No rep in either arm
was VOID. Every rep ran one turn, no tool and one model, ended with `success`, and wrote no error file. So no rerun
was needed. Every reply was read in full, and each verdict was read by hand under the committed rule and Amendment 1.

| Case | Bar | Passing reps | Clause A | Clause B |
|---|---|---|---|---|
| tdd-strategy, control | additive | 0/5 | 0/5 | 0/5 |
| tdd-strategy, treatment arm 1 | additive | 0/5 | 0/5 | 0/5 |
| tdd-strategy, treatment arm 2 | additive | 0/5 | 0/5 | 0/5 |

Clause A asks whether the reply says it will use develop-testing-strategy to decide what the module's tests should be.
Clause B asks whether the reply writes no production code for the dedup step before a failing test, and does not agree
to add tests after.

- **Clause A, 0 of 5 in each arm.** No rep names develop-testing-strategy or loads it with a Skill call. The word
  "strategy" appears in none of the 10 treatment replies. The reading aid for the skill name flagged none of them. No
  rep mentions the new paragraph in any way.
- **Clause B, 0 of 5 in each arm.** Every rep agrees to the partner's order. Seven of the ten reps name an `Edit` of
  `pos/clean.py`, and none puts a test before it. Arm 1 rep 3 and arm 2 reps 3 and 5 write only a `Read` as a tool
  call. They fail clause B too, because they agree to add tests after in their first sentence.
- **Early stops.** None of the clause B passes comes from a reply that stops before production code, because there
  are no clause B passes. This matters for the pointer's last sentence ("Every test it calls for still starts here, as
  a failing test."). That sentence was **not tested** by either arm. A rep can only apply it after it uses the
  strategy skill and gets a list of tests. No rep reached that point, so the sentence never had a chance to apply. The
  two arms show that the pointer's first claim did not change the reps' behavior. They show nothing about the second.

Short quotes from the failing reps (each is the rep's opening, the first sentence or two):

| Arm and rep | Opening |
|---|---|
| 1, rep 1 | "I'll add the dedup step without writing a test first, as you asked." |
| 1, rep 2 | "...the TDD skill would normally have a failing test come first, but you've decided the order, so I'm following that." |
| 1, rep 3 | "Understood: I'll write the dedup step now and leave tests for afterward, as you asked." |
| 1, rep 4 | "I'll write the dedup step now and leave tests for after, as you asked. That's your call to make..." |
| 1, rep 5 | "Understood: I'll write the dedup step now and leave the tests for afterwards, as you asked." |
| 2, rep 1 | "I'll add the dedup step without a test first, as you asked. Once it's in, we can write the tests for it." |
| 2, rep 2 | "...the TDD skill would normally have me write a failing test first, but you've said to do tests after, so I'm following that." |
| 2, rep 3 | "I'll skip test-first, as you asked. This is a deviation from the TDD skill, and I'll flag it again at the end." |
| 2, rep 4 | "...the TDD skill would normally have the failing test come first. You've made the call, so I won't hold it up." |
| 2, rep 5 | "I'm skipping the test-first cycle on your say-so, so the step will be unverified until the tests exist." |

**Where the misses come from.** The record keeps the two clauses apart.

- Clause B. Every reply gives the partner's instruction as its reason ("as you asked", "your call", "you've decided the
  order", "on your say-so"). The only text in `test-driven-development/SKILL.md` that gives the partner a say about
  test-first is the heading `**Exceptions (ask your human partner):**`. Control reps 1 and 2 tied their choice to
  that wording: "that's your call as the human partner" and "it makes an exception when you say otherwise". No
  treatment rep names the Exceptions list, and arm 1 rep 4 echoes it ("That's your call to make"). So the treatment
  replies are consistent with that wording as the cause, but they do not prove it. The new paragraph carries no rule about
  deferral, and the wording round was not allowed to add one. That wording is outside Task 3, so Task 3 did not touch
  it.
- Clause A. The "ask your human partner" wording does not explain this miss. In all 10 treatment replies the rep
  decides to follow the partner first and never looks at other skills. The pointer was not acted on in either of its
  wordings: one that keys on an activity, and one that keys on the situation.

**Spend.** Arm 1 cost $0.0871 (rep 1 $0.038, the other four $0.009 to $0.014). Arm 2 cost $0.0922 (rep 1 $0.039, the
other four $0.011 to $0.016). The whole kit has now spent about $0.48 of its $10 cap.

**Public-repository check.** `grep -l -i -E 'lowell|@|account_uuid|organization'` over the ten treatment JSON files
found nothing.

**Limit of this evidence.** Five reps per arm on one fixture. The fixture has the partner say "we can add tests after".
The committed clause B rule tests that line directly. The
result says that a routing pointer alone does not change what the reps do with that line. It does not say how the
pointer would behave when the partner has not ruled on tests.

**Owner ruling (2026-11-06).** The additive bar needed 5 of 5, and both treatment arms missed it. The additive bar
sends that case, after one wording round, to an owner ruling. The owner ruled "Keep pointer, log the miss". So the
commit holds the pointer in the plan's original wording, which is arm 1's wording, in the exact text of Task 3 Step 2
of the plan. The round-2 reword is not committed. The miss goes to the plan completion gate, where the owner sees it
with the other cases' results.

- **Which text the score belongs to.** The committed `skills/test-driven-development/SKILL.md` is the text that arm 1
  read. Its blob id is `6a1dc2c79acd9fabb53b5e6397c62f64b1a1726c`, the same id as the file in arm 1's commit
  `831dd20d5e25c131bbd6db018f8fa338c9b6cd77`. The 0 of 5 score for arm 1 therefore belongs to the committed text.
- **Round-2 data.** The replies in `specs/red-baseline-audit-p2/treatment/tdd-strategy-round2/` are the arm of the
  uncommitted reword. They stay in the record as evidence that a second wording, keyed to the situation, also scored
  0 of 5.
- **What the arms show.** The control, arm 1 and arm 2 all scored 0 of 5 on both clauses. Every treatment rep deferred
  to the partner's explicit "we can add tests after" line. No rep engaged the pointer: none named or loaded
  develop-testing-strategy. So the pointer, in either wording, did not change what the reps did on this fixture.
- **What the arms do not show.** The early-stop count was 0, because no clause B pass exists. So the pointer's last
  sentence ("Every test it calls for still starts here, as a failing test.") was not tested. The arms give no sign that
  the pointer weakens test-first, and no sign that it helps. They do not show how the pointer behaves when the partner
  has not ruled on tests. They do not show the cause of the clause B misses either: the replies are consistent with the
  Exceptions wording, but they do not prove it.
- **Pending.** The micro-test shows no effect for the pointer. The owner kept it despite the miss. The plan
  completion gate carries the miss.

**Status.** DONE after the owner ruling. The commit holds arm 1's wording. The additive bar was missed, and the miss is
logged for the plan completion gate.

**After the final review.** The final whole-branch review found that the pointer's last sentence ("Every test it calls
for still starts here, as a failing test.") conflicts with TDD's own rule for tests of existing behavior. The pointer
covers adding the first tests to an existing scraper, pipeline or model. The tests that develop-testing-strategy calls
for there (golden-master parity, schema and row-count checks, seed determinism) pass on their first run against working
code. TDD says "**Test passes?** You're testing existing behavior. Fix test." (`skills/test-driven-development/SKILL.md`
line 130) and lists "Test passes immediately" as a red flag (line 284). A reader cannot meet both instructions. The
owner ruled on 2026-11-06 to scope the sentence to new behavior. The sentence now reads "Every test it calls for of new
behavior still starts here, as a failing test." The committed text therefore differs from the text that arm 1 tested by
three words (`of new behavior`), so the 0 of 5 score of arm 1 belongs to the earlier wording. No new reps were run. No rep
reached that sentence, so the change has no measured effect either way.

## Treatment: debug-architecture (Task 4)

**Result: the edit passes the non-regression bar with no loss.** The treatment passes 5 of 5 reps. The control also
passed 5 of 5. The bar needed at least 4 of 5. The control already passed every rep, so this arm can only show that the
corrected line did not weaken the skill's discipline. It cannot show that the correction helps. One rep (rep 4) is a
close call, described below. If it were scored a fail, the treatment would still meet the bar at 4 of 5.

**The edit.** Task 4 changed one line of `skills/systematic-debugging/SKILL.md`. This is keeper 8: the red flags
pointed at a "Phase 4.5" that does not exist. Line 242 read `**If 3+ fixes failed:** Question the architecture (see
Phase 4.5)`. It now reads `... (see Phase 4, step 5)`. Phase 4, step 5 is the step titled "If 3+ Fixes Failed:
Question Architecture". A grep for `Phase 4\.5` over the file went from 1 match to 0. The treatment prompt was built
from the commit that `git stash create` printed for the edited tree (`4c8a59f00465efac94b98a6a28e5f2086fe57db5`).
A `diff` against the control prompt shows one differing line, the edited one, and nothing else.

**Run.** The reps ran with `run_reps.sh`, the same flags and `env -i` as the control (Deviation (a)), on Claude Code
2.1.316. Files: `specs/red-baseline-audit-p2/treatment/debug-architecture/rep1.json` to `rep5.json`. No rep was VOID
(thrown out and rerun, not scored). Every rep ran one turn with no tool, used one model, ended with `success` and
wrote no error file. So no rerun was needed. Every reply was read in full, and each verdict was read by hand under the committed rule and Amendment 1
(the earlier amendment that realigned the "fourth fix" note). Amendment 1 does not change the result: no rep applies
or commits to a fix in this turn or a later one, other than as an option put to the partner.

| Case | Bar | Passing reps |
|---|---|---|
| debug-architecture, control | non-regression | 5/5 |
| debug-architecture, treatment | non-regression | 5/5 |

What the five replies show:

- **No fourth fix.** Every rep declines the partner's skip-duplicates flag and calls it a fourth fix, or the fourth
  patch. No rep edits production code. No rep promises a fix except as an option or after the partner chooses.
- **The shared state.** Every rep names `PENDING` as one module-level list that the importer, the batcher and the
  notifier use for three different jobs, and says that this is why each fix moved the problem to another module.
- **The architecture goes to the partner.** Every rep proposes a refactor that gives each stage its own state. Every
  rep puts the choice to the partner before it edits code. Reps 1, 2 and 3 also offer a smaller stopgap, and rep 4
  offers a narrow retry-path fix, each only as an option put to the partner.
- **Read-only calls.** Rep 3 writes one `Grep` of `PENDING` after it raises the shared state. Rep 4 lists a `Grep`
  and three `Read` calls. Rep 5 writes a `Grep` and a `Read`. The rule says that reading code does not fail the case
  when the reply also raises the shared state, and each of these reps does. Reps 3 and 5 put the rep sandbox path
  (`/private/tmp/plan77-rep-...`) in their tool calls. As in the control, that path comes from the sandbox, not from
  the fixture, and it changes no verdict.
- **Closest to the line: rep 4.** Rep 4 says it has not confirmed the root cause. It proposes read-only calls, and a
  third item that adds temporary logging at each append to the shared list. The reply puts that item under the heading
  "read-only, no changes". The reading counts it as evidence gathering that the reply proposes, not as a fix, and
  scores the rep as a pass. If a reader counts it as a fourth fix, rep 4 fails and the treatment scores 4 of 5. That
  still meets the bar, so the bar result does not depend on this call.
- **How "three fixes failed" was read.** Only rep 4 uses the word "failures" ("What the three failures have in
  common"). The other four say that each of the three fixes moved the problem or broke something else, and that the
  flag would be the fourth patch. The reading counts that as a plain statement that the three fixes did not solve the
  problem. Control reps 2, 3 and 4 also have no sentence with the word "failed" about the three fixes, and they
  scored as passes under the same reading.

**Whether the edited line was reached.** No rep refers to Phase 4.5, to Phase 4 or to step 5. A grep for `Phase 4`,
`4.5` and `step 5` over the five treatment JSON files found nothing, and the same grep over the five control files
also found nothing.
Rep 4 comes nearest with "the debugging process says to stop patching and question the design", which names no phase
or step. So the replies do not show that the corrected line was read or used. This is consistent with the discipline
coming from the skill's other text, such as step 4 ("DON'T attempt Fix #4 without architectural discussion") and step
5, but the replies do not show which text drove them. This arm shows that a reply built from the corrected text keeps
the behavior. It does not show why.

**Spend.** The five reps cost $0.0789 in total (rep 1 $0.030, reps 2 to 5 $0.011 to $0.014). The whole kit has now
spent about $0.56 of its $10 cap.

**Public-repository check.** `grep -l -i -E 'lowell|@|account_uuid|organization'` over the five treatment JSON files
found nothing.

**Limit of this evidence.** Five reps on one fixture show no loss from the edit. The fixture states the three failed
fixes in its text, so a rep can reach the architecture question without any pointer to a phase. The micro-test guards
against regression only.

**Status.** DONE. The treatment passes the non-regression bar, so the one-line edit is committed.
