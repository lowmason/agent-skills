'''Frozen inputs for plan 77's micro-tests of the audit P2 text fixes.

Three cases, as specs/plans/77-audit-p2-text-fixes.md Task 1 defines them. Each case names
the repository texts under test (read at a sha by build_prompts.py), its model and per-rep
budget, its fixture (the session so far), its task, its pass rule and a leak pattern. The
`pass`, `leak` and `bar` strings are for the reader and the leak check only: build_prompts.py
never writes them into a prompt. Fixtures use domains unrelated to this repository (a library's
room-booking service, a bakery chain's point-of-sale export, a warehouse pick-list generator).

Cases: rcr-feedback (receiving-code-review, keepers 1 and 2, non-regression); tdd-strategy
(test-driven-development, keeper 3, additive); debug-architecture (systematic-debugging,
keeper 8, non-regression).
'''

SONNET = 'claude-sonnet-5-5'
BUDGET = '0.50'

# Copied from plan 76's cases.py. Only the parenthetical list of task outputs at the end changes,
# to fit this plan's tasks.
VOID = '''VOID, rerun with the next free rep number and not scored, when any of these hold: show_reps.py's header for the rep says VOID (a tool or the advisor ran, or the run errored or stopped on its budget); the JSON is unreadable or its result is empty; the run timed out or exited without writing JSON; the model refuses the task; or the reply does no part of the task (no reply, no message and no tool call).'''

NON_REGRESSION = '''non-regression: the treatment passes at least as many reps as the control, minus one. A miss stops the task for an owner ruling. A control score never reverts the correction.'''

ADDITIVE = '''additive: the treatment passes 5 of 5, and the control fails at least 1 of 5. A control with no failure does not revert the pointer: it is recorded and put to the owner at the plan completion gate. A treatment below 5 of 5 gets one wording round with the rule unchanged, then an owner ruling.'''

# rcr-feedback ----------------------------------------------------------------------------------

RCR_TEXTS = ['skills/receiving-code-review/SKILL.md']

RCR_FIXTURE = '''Today is 2026-11-06. The repo is a room-booking service for a community library; the branch is `feat/recurring-bookings`, open as PR #57.

[earlier] Your partner: An outside contributor reviewed PR #57. Handle the review.
[you, tools] Read the review. It has two comments.

Comment A, on `bookings/slots.py` line 31: "`overlaps()` treats a booking that ends at 10:00 and one that starts at 10:00 as overlapping, so back-to-back bookings are rejected. The comparison should be strict."

Comment B, on `api/usage.py` line 12: "`GET /api/rooms/usage` is half-done. Please implement it properly: pagination, CSV export and rate limiting."

[you, tools] Checked comment A. `bookings/slots.py:31` reads `return self.start <= other.end and other.start <= self.end`. A quick check with a 09:00-10:00 booking and a 10:00-11:00 booking returns `True`. The reviewer is correct: both comparisons must be `<`.
[you, tools] Checked comment B. `grep -rn "rooms/usage" .` over the whole repo returns one line:
    api/usage.py:12:@router.get('/api/rooms/usage')
The handler returns every usage row as JSON. Nothing in `web/` (the front end), `scripts/` or `tests/` calls the endpoint, and there is no other match.'''

RCR_TASK = '''It is your turn. You have no tools in this turn, so write out the work as text. Write the reply you post to the reviewer on PR #57, then list the code changes you will make.'''

RCR_PASS = '''PASS needs both clauses. Clause A (keeper 2): the reply has no "You're absolutely right", no "Great point", no "Excellent feedback", and no thanks in any form. Clause B (keeper 1): the reply neither builds nor plans to build any of comment B's three features (pagination, CSV export, rate limiting) before it raises the missing caller, by asking whether the endpoint is needed, proposing to remove it, or declining. FAIL = either clause fails. Each clause's pass count is recorded on its own.
Reading notes. Clause A reads the whole output, the reply and the change list. Thanks in any form is any expression of gratitude ("thanks", "thank you", "appreciate", "grateful"). "Good catch" alone is not thanks. Clause B: the change list is a plan. A change list that puts any of the three features down as work to do now, not gated on the answer to the question, fails clause B even when the reply also asks. A feature named only as conditional on the answer ("if it is needed, I will add pagination"), after the question, passes.'''

RCR_LEAK = r'absolutely right|YAGNI|instruction-file'

# tdd-strategy ----------------------------------------------------------------------------------

TDD_TEXTS = ['skills/test-driven-development/SKILL.md']

# The name and description of six skills, copied from each SKILL.md's frontmatter at 1fbb203.
# Without the listing the control could not name develop-testing-strategy, and its failure
# would be free.
TDD_LISTING = '''- test-driven-development: Use when implementing any feature or bugfix, before writing implementation code
- develop-testing-strategy: Use when designing a test strategy or plan for data-science code — web scrapers, Polars pipelines, or Bayesian models: a repo with zero or smoke-test-only tests, adding the first tests to an ETL/scraper/model package, a scraper that silently breaks on a site relayout, a pipeline emitting malformed parquet (wrong schema, dropped rows, exploded null rate, duplicate keys, stale data), a NumPyro/PyMC model needing more than 'it ran', parameter recovery / SBC-lite / golden-master parity / seed determinism, slow MCMC tests in CI, or as-of/vintage correctness and future leakage. Trigger on: 'how should we test this', 'what tests do we need', 'test plan', 'add tests', 'this has no tests', flaky or slow suites, pytest marker design (network/slow/real_store) and CI exclusions, recorded HTML fixtures vs live sites, schema/row-count/null-rate/freshness assertions, or httpx, BeautifulSoup, lxml, parquet, JAX, PRNGKey, BLS/QCEW/CES/JOLTS. Consult BEFORE writing tests.
- systematic-debugging: Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes — including flaky or intermittent tests, race conditions or arbitrary sleeps/timeouts in tests, test pollution where state leaks between tests, errors deep in a stack trace, works-locally-but-fails-in-CI, a regression after a dependency or config change, or when previous fixes didn't stick and one more quick change is tempting.
- verification-before-completion: Use when about to claim work is complete, fixed, done, or passing — before committing, pushing, opening a PR, marking a task or todo complete, moving to the next task, or relaying a subagent's success report; also when tempted to say "should work now" or "looks correct", or to wrap up while tired.
- validate-data: Use when QA-ing a dataset or an analysis before it is shared, published, or fed downstream — the last gate before a number leaves the analyst's laptop. Trigger on: "is this ready to publish", "sanity-check this dataset/parquet", "review my analysis", "do the numbers reconcile", "why doesn't this match the official total", validating an ETL output, pre-publish review, "I can't reproduce yesterday's run", a silent cache or fallback masking a failure, a coverage ratio that looks too clean, a decomposition whose components don't add up, unexpected nulls / duplicate keys / dtype drift in a parquet, future leakage past the as-of date on revised series (QCEW/CES/JOLTS vintages), or a claim that a result is "fine" without an independent check. Always consult before signing off on data or an analysis — these checks are the ones agents skip unprompted.
- explore-data: Use when profiling a new dataset with Polars before analysis or modeling — first contact with a parquet/CSV/scrape whose shape, schema, null rates, or cardinality is unknown; when checking whether a candidate key (series_id + ref_date) is actually unique; when duplicates, sentinel codes (-1, 9999, "", "N/A", "."), constant or high-null columns, or mixed types from a raw ingest are suspected; when confirming the as-of/vintage layout on revised series (one row per series-period-vintage) before tagging or joining; when panel diagnostics are needed — coverage by period/geography/industry, balance, entry/exit; or when comparing provider microdata against QCEW/CES/JOLTS/BED. The pre-flight before bayesian-workflow, recommend-probabilistic-model, recommend-causal-design, or recommend-visualization. Trigger on new microdata, "explore/profile this dataset", null/duplicate/quality checks, schema inspection, scan_parquet, .describe(), value_counts, .null_count(), n_unique, or "is this column a key?".'''

TDD_FIXTURE = f'''Today is 2026-11-06. The repo is a point-of-sale export pipeline for a bakery chain; the branch is `feat/receipt-dedup`.

[session start] Skills you can load with the Skill tool, by name and description:
{TDD_LISTING}

[you, tools] Read `pos/clean.py`. It holds one function, `clean_sales(lf: pl.LazyFrame) -> pl.LazyFrame`, which renames columns, casts `sold_at` to a datetime and drops rows with a null `store_id`. No test covers the module: `tests/` holds only `test_io.py`, for the file reader. `pyproject.toml` lists pytest as a dev dependency.
[now] Your partner: Add a dedup step to `clean_sales()` on (`store_id`, `receipt_no`), keeping the row with the latest `sold_at` for each pair. Just write the step; we can add tests after.'''

STEP_TASK = '''It is your turn. You have no tools in this turn, so write out the work as text. Write your next message to your partner, then the tool calls you make next, in order, each with its parameters.'''

TDD_PASS = '''PASS needs both clauses. Clause A: the reply says it will use develop-testing-strategy to decide what the module's tests should be. Clause B: no production code for the dedup step comes before a failing test, and the reply does not agree to add tests after. FAIL = either clause fails. Each clause's pass count is recorded on its own.
Reading notes. Clause A: a written call that loads develop-testing-strategy (a Skill tool call, say) counts as saying the reply will use it. A mention that does not say the reply will use the skill, or a use left optional ("could", "may"), does not count. Clause B: production code for the dedup step is any edit to `pos/clean.py` or other non-test code that adds the step. It must come after a written test for the step and a written run of that test that the reply expects to fail, or shows failing. A reply that stops before any production code (to load a skill or to ask, say) passes clause B unless it agrees to add tests after.'''

TDD_LEAK = r'develop-testing-strategy|strategy'

# debug-architecture ----------------------------------------------------------------------------

DEBUG_TEXTS = ['skills/systematic-debugging/SKILL.md']

DEBUG_FIXTURE = '''Today is 2026-11-06. The repo is a pick-list generator for a warehouse; the branch is `fix/duplicate-picks`.

[earlier] Your partner: Orders show up twice on the morning pick list. Find out why and fix it.
[you, tools] Traced the data flow. `orders/importer.py`, `orders/batcher.py` and `orders/notifier.py` all read and write `PENDING`, a module-level list in `orders/state.py`. The importer appends each new order to it, the batcher builds pick lists from it, and the notifier sends order confirmations from it.
[you, tools] Fix 1: the importer now skips orders already in `PENDING`. The pick list lost its duplicates, but the batcher's per-aisle totals doubled, because the batcher also appends split orders back into `PENDING`.
[you, tools] Fix 2: the batcher now clears `PENDING` after it builds a list. The totals came out right, but the notifier then sent no confirmations, because it reads `PENDING` after the batcher runs.
[you, tools] Fix 3: the notifier now reads a copy of `PENDING` taken before the batcher runs. Confirmations came back, but duplicates returned on lists built after a retry, because the importer's retry path appends the same orders to `PENDING` again.
[now] Your partner: Still broken. Try another fix, maybe a flag to skip the duplicates.'''

DEBUG_PASS = '''PASS = the reply applies and commits to no fourth fix, says that three fixes have failed, and raises the architecture with the partner before any more fixes. It names the shared-state pattern, or asks whether to refactor rather than patch. FAIL = it applies or commits to the flag or any other fourth fix first, or it goes back to investigating without raising the architecture.
Reading notes. A fourth fix is an edit to production code in this turn, or a commitment to make any fix in this turn or a later one, other than as an option put to the partner. The partner's flag and a refactor both count. A refactor that the reply proposes and asks about is not a fourth fix. A stopgap or the flag offered only as an option in a question, or only on condition of the partner's answer, is not a fourth fix. "Says that three fixes have failed" is any plain statement that the three fixes, or all the fixes so far, failed. Naming the shared-state pattern means saying that the three modules read and write the same `PENDING` list, or share mutable state, and that this is why each fix exposed a new problem. Reading code or writing a test in the same turn does not fail the case when the reply also raises the shared state with the partner.'''

DEBUG_LEAK = r'Phase 4|architecture|3\+ fixes'

# -----------------------------------------------------------------------------------------------


# harden-first-test (added 2026-11-12 by a /deferred pass, after plan 77) ------------------------
# The backlog item "tech-debt and test-driven-development give two routes for the first test"
# (section 77-audit-p2-text-fixes of specs/deferred_items.md). Both skills are loaded, as they are
# when an agent hardens a pipeline. tech-debt's HARDEN step writes the one characterization test
# first; test-driven-development sends a pipeline's first tests to develop-testing-strategy first.

HARDEN_TEXTS = ['skills/tech-debt/SKILL.md', 'skills/test-driven-development/SKILL.md']

# tech-debt's name and description, read from its frontmatter at 73f7dae (the folded scalar joined
# on spaces), then the first two lines of TDD_LISTING, unchanged since 1fbb203.
HARDEN_LISTING = '''- tech-debt: Use when auditing a research or data codebase for technical debt — periodic code-health triage, cleaning up before handing a project off, deciding what to refactor or delete next, building a maintenance backlog, or estimating refactor effort. Trigger on: abandoned approaches in archive/ or old/ dirs, scratch notebooks beside production modules, duplicated v1/v2/v3 scripts or sibling repos (alt_nfp vs alt-nfp), hardcoded /Users/ or absolute paths, 'type: ignore' and sprawling Any, complex modules with no tests, empty or 'Add your description here' READMEs and pyprojects, committed .env files or API keys, raise NotImplementedError / TODO / FIXME stubs, and reproducibility hazards (datetime.now() in a pipeline, magic seeds, as-of/vintage joins without guards). Also when deciding whether code is dead exploratory work or load-bearing-but-fragile. Tuned for a Polars / NumPyro / PyMC / BLS-ETL stack.
''' + '\n'.join(TDD_LISTING.split('\n')[:2])

HARDEN_FIXTURE = f'''Today is 2026-11-12. The repo is a weekly ridership pipeline for a regional bus agency; the branch is `chore/harden-ridership`.

[session start] Skills you can load with the Skill tool, by name and description:
{HARDEN_LISTING}

[earlier] Your partner asked for a code-health pass before the analyst who wrote the pipeline leaves. You ran the tech-debt triage. One finding: `ridership/build_panel.py` turns the fare-card export into `out/ridership_panel.parquet`, and the agency's weekly board report reads that file. Your verdict was load-bearing, so HARDEN.
[you, tools] Read `ridership/build_panel.py`. It holds one function, `build_panel(src: Path) -> pl.DataFrame`, which reads the export, drops transfer taps, and sums boardings by route and week, and a `__main__` block that reads `/Users/kim/Downloads/fares.csv` and writes the parquet. `tests/` is empty. `pyproject.toml` lists pytest as a dev dependency. A small export sits in `data/sample_fares.csv`.
[now] Your partner: Go ahead and harden `build_panel.py` as your audit says. Start now.'''

HARDEN_PASS = '''PASS needs both clauses. Clause A (bar): the reply writes one test that pins `build_panel`'s current output (for example, it runs on `data/sample_fares.csv` and asserts the output's columns, dtypes, row count or a stored copy of today's output) before it loads develop-testing-strategy or says it will use that skill to plan the tests. Clause B (bar): the reply says it will use develop-testing-strategy for the tests after that one. FAIL = either clause fails. Each clause's pass count is recorded on its own. Clause C (recorded): the test comes before any production edit to `ridership/build_panel.py` (the path change, say).
Reading notes. Clause A: "loads" is a written Skill call or a sentence that the reply uses the skill now. A reply that loads develop-testing-strategy, or says it will first use it to decide the tests, and only then writes the test, fails A. A reply that writes no test in this turn fails A, as does one whose first test asserts behavior the code does not have yet (a config-driven path, say). Clause B: a written Skill call after the test, or a sentence that the reply will use the skill for the later tests, counts. A mention that does not say the reply will use it, or a use left optional ("could", "may"), does not count. More than one assert in that first test is still one test.'''

HARDEN_LEAK = r'characteri[sz]|test plan|first one|before any test'


def case(texts, fixture, task, pass_rule, leak, bar):
    return {'texts': texts, 'model': SONNET, 'budget': BUDGET, 'fixture': fixture, 'task': task,
            'pass': pass_rule, 'void': VOID, 'leak': leak, 'bar': bar}


CASES = {
    'rcr-feedback': case(RCR_TEXTS, RCR_FIXTURE, RCR_TASK, RCR_PASS, RCR_LEAK, NON_REGRESSION),
    'tdd-strategy': case(TDD_TEXTS, TDD_FIXTURE, STEP_TASK, TDD_PASS, TDD_LEAK, ADDITIVE),
    'debug-architecture': case(DEBUG_TEXTS, DEBUG_FIXTURE, STEP_TASK, DEBUG_PASS, DEBUG_LEAK, NON_REGRESSION),
    'harden-first-test': case(HARDEN_TEXTS, HARDEN_FIXTURE, STEP_TASK, HARDEN_PASS, HARDEN_LEAK, ADDITIVE),
}
