'''Frozen inputs for plan 78's micro-tests of derive-roadmap's New-Project Entry.

Fifteen cases, as specs/plans/completed/78-derive-roadmap-new-project-entry.md Task 1 Step 3 defines them.
Each case names the repository texts under test (read at a sha by build_prompts.py), its model
and per-rep budget, its kind, its fixture (the session so far), its task, its pass rule, its leak
pattern and, where it reads them, the case-repository files that its `{file:<key>}` markers
place. The `pass`, `leak`, `void` and `bar` strings are for the reader and the leak check only:
build_prompts.py never writes them into a prompt.

Fixture text from the case-study repositories (lowmason/sec-edgar, lowmason/embedding-data and
lowmason/ces-revisions, all public) is read at build time from local clones under $CASE_REPOS.
Nothing from them is written here except the hand-written state lines below. Constructed fixtures
use their own domains: a museum's visitor-count forecaster, canal lock closures and river-gauge
levels, a parking-sensor occupancy pipeline, a tide-gauge archive, building permits, timesheets
and GPX tracks.
'''
import re

OPUS = 'claude-opus-5-5'
# The per-rep --max-budget-usd cap, set at Task 1 Step 6: the larger of $1.00 and three times the cost
# pilot's total_cost_usd ($0.2821), rounded up to the next $0.25.
BUDGET = '1.00'

# Copied from plan 77's cases.py, unchanged.
VOID = '''VOID, rerun with the next free rep number and not scored, when any of these hold: show_reps.py's header for the rep says VOID (a tool or the advisor ran, or the run errored or stopped on its budget); the JSON is unreadable or its result is empty; the run timed out or exited without writing JSON; the model refuses the task; or the reply does no part of the task (no reply, no message and no tool call).'''

ADDITIVE = '''additive: the treatment passes every clause (each bar clause and each conformance clause; a recorded clause never counts) in at least 4 of 5 reps, and the control fails a bar clause in at least 1 of 5. A control with no failure never reverts a change: it is recorded and put to the owner at the plan completion gate (plan 77's rule). A treatment below its bar gets one wording round with the case's rule unchanged, then an owner ruling.'''

NON_REGRESSION = '''non-regression (guard): a rep passes when it meets the whole PASS rule, and the treatment passes at least as many reps as the control, minus one. A treatment below its bar gets one wording round with the case's rule unchanged, then an owner ruling.'''

STEP_TASK = 'It is your turn. You have no tools in this turn, so write any tool call as text. Write your next message to your partner.'
TRIGGER_TASK = 'Name the skill you invoke first, if any, and give one sentence why. Then stop.'
ROADMAP_TASK = 'It is your turn. You have no tools in this turn. Write the full roadmap file you will commit now, as Markdown, then the one-line message you send with it.'

# Text sets -------------------------------------------------------------------------------------

DR = ['skills/derive-roadmap/SKILL.md', 'skills/derive-roadmap/references/*.md']
DCM_D = ['skills/describe-critique-methodology/SKILL.md',
         'skills/describe-critique-methodology/references/methodology-template.md']
DCM_S = ['skills/describe-critique-methodology/SKILL.md',
         'skills/describe-critique-methodology/references/spec-synthesis.md']
BS = ['skills/brainstorming/SKILL.md']
NO_TEXTS: list[str] = []

# The embedding-data gap table, with every stage pointer removed -------------------------------

ARROW = '→'
STAGE_REF = re.compile(r'\bS\d+\b|\bstages?\b', re.I)
STATEMENT_WORDS = 4
# Rows whose whole note is emptied, keyed by their Evidence cell. The plan's leak rule for
# dr-offer-inputs keeps a note hit only where it is historical evidence and not a verdict. The osha
# case-detail row's note, "Kept; recorded in spec as acquired, feeding no target", is a verdict
# (leak word `acquir`), so it goes. Every other row goes through note_segment() only.
LEAK_VERDICT_ROWS = {'`osha` case-detail command'}


def note_segment(segment: str) -> str:
    '''One `;` segment of a Note cell, with its stage pointer removed, or '' when it names a stage.

    A pointer is `→ S<n>` and whatever follows it. The text before the arrow stays when it is a
    statement (STATEMENT_WORDS words or more) or reports a check as unrecorded; a shorter text
    is the label of the work the pointed-to stage does, so it goes with the pointer. A segment
    with no arrow that names a stage (`S<n>`, `stage`) goes whole.
    '''
    segment = segment.strip()
    if ARROW in segment:
        before = segment.split(ARROW, 1)[0].strip()
        keep = len(before.split()) >= STATEMENT_WORDS or 'unrecorded' in before.lower()
        return before if keep and not STAGE_REF.search(before) else ''
    return '' if STAGE_REF.search(segment) else segment


def gap_table_without_stages(text: str) -> str:
    '''The roadmap's Gap analysis section, key and table, with every stage pointer removed from
    the Note column, the notes of LEAK_VERDICT_ROWS emptied, and nothing after the table. Refuses
    when a stage reference survives or a row of LEAK_VERDICT_ROWS is missing.'''
    lines = text.splitlines()
    start = lines.index('## Gap analysis') + 1
    end = next(i for i in range(start, len(lines)) if lines[i].startswith('## '))
    section = lines[start:end]
    last = max(i for i, line in enumerate(section) if line.startswith('|'))
    out, emptied = [], set()
    for line in section[:last + 1]:
        if not line.startswith('|') or line.startswith(('|---', '| Req ')):
            out.append(line)
            continue
        cells = line.split('|')
        if len(cells) != 6:
            raise SystemExit(f'refusing: gap table row does not have four cells: {line}')
        req, evidence, note = cells[1].strip(), cells[3].strip(), cells[4]
        if evidence in LEAK_VERDICT_ROWS:
            emptied.add(evidence)
            kept = []
        else:
            kept = [s for s in map(note_segment, note.split(';')) if s]
        cells[4] = f' {"; ".join(kept)} ' if kept else ' '
        if ARROW in cells[4] or STAGE_REF.search(cells[4]):
            raise SystemExit(f'refusing: a stage reference survives in the note of {req}')
        out.append('|'.join(cells))
    if emptied != LEAK_VERDICT_ROWS:
        raise SystemExit(f'refusing: rows to empty not found: {sorted(LEAK_VERDICT_ROWS - emptied)}')
    return '\n'.join(out).strip('\n')


# Case-repository files ------------------------------------------------------------------------

SEC_AT = '22c6767f'
SEC_SPEC = {'repo': 'sec-edgar', 'commit': SEC_AT, 'path': 'specs/sec-filing-index-ingestion-spec.md'}

EMB_SPEC = {'repo': 'embedding-data', 'commit': 'af7bf21', 'path': 'specs/embedding-evaluation-data-spec.md'}
EMB_GAP = {'repo': 'embedding-data', 'commit': '4bc8cda', 'path': 'specs/embedding-evaluation-data-spec-roadmap.md',
           'derive': gap_table_without_stages}

CES_AT = '0e24ecc'  # the parent of 237b426
EXCERPT = 3000
CES_FILES = {
    'brief': {'repo': 'ces-revisions', 'commit': CES_AT, 'path': 'specs/ces-revisions-prompt.md'},
    'chatgpt': {'repo': 'ces-revisions', 'commit': CES_AT, 'path': 'specs/ces-revisions-research-chatgpt.md',
                'excerpt': EXCERPT},
    'claude': {'repo': 'ces-revisions', 'commit': CES_AT, 'path': 'specs/ces-revisions-research-claude.md',
               'excerpt': EXCERPT},
    'gemini': {'repo': 'ces-revisions', 'commit': CES_AT, 'path': 'specs/ces-revisions-research-gemini.md',
               'excerpt': EXCERPT},
}

# Shared fixture lines --------------------------------------------------------------------------

TODAY = 'Today is 2026-11-06.'

SEC_HEAD = TODAY + ' The repository is `sec-edgar`, on branch `main`.\n'

SEC_TREE = '''[you, tools] Listed the repository with `git ls-files`. It has one commit, "initial commit", and these files:
    .DS_Store, .gitignore, .python-version (it reads 3.14), README.md, pyproject.toml
    packages/sec-edgar-client/: README.md, pyproject.toml, src/sec_edgar_client/__init__.py, src/sec_edgar_client/py.typed
    packages/sec-edgar-download/: README.md, pyproject.toml, src/sec_edgar_download/__init__.py, src/sec_edgar_download/py.typed
    packages/sec-edgar-index-ingest/: README.md, pyproject.toml, src/sec_edgar_index_ingest/__init__.py, src/sec_edgar_index_ingest/py.typed
    packages/sec-edgar-ingest/: README.md, pyproject.toml, src/sec_edgar_ingest/__init__.py, src/sec_edgar_ingest/py.typed
    specs/sec-filing-index-ingestion-adr.md, specs/sec-filing-index-ingestion-spec.md
[you, tools] Read the package files. Every README.md and every py.typed is empty. Each __init__.py holds the two-line `hello()` stub that `uv init` writes, and nothing else. Each pyproject.toml declares a name, version 0.1.0, the description "Add your description here" and `dependencies = []`. The root pyproject.toml also lists the four packages as workspace members and a `sec-edgar = "sec_edgar:main"` script, but no `sec_edgar` module exists. There is no tests directory.'''

SEC_SPEC_READ = '''[you, tools] Read specs/sec-filing-index-ingestion-spec.md. Its full text:
{file:spec}'''

SEC_ADR = '''[you, tools] Read specs/sec-filing-index-ingestion-adr.md, "Use Azure-managed orchestration for SEC filing indexes" (Status: Proposed, 2026-10-05). Its decision: Azure Data Factory orchestrates historical backfill, daily ingestion and reconciliation, which run shared Python code in Azure Container Apps Jobs, with files in ADLS Gen2 and the manifest and publication pointers in Azure Table Storage.'''

SEC_GAP = '''[you, tools] Ran the gap analysis over the spec's numbered requirements, R1 to R11 in §3 Rulings: 11 rows, one per requirement. Every verdict is `missing`, and every row has the same evidence: "no code beyond the generated package scaffolds".'''

NO_ROADMAP = '''[you, tools] No file under specs/ carries the roadmap header, and specs/deferred_items.md does not exist.'''

CES_HEAD = TODAY + ' The repository is `ces-revisions`, on branch `main`.\n'

CES_TREE = '''[you, tools] Listed the repository with `git ls-files`: .gitignore, .python-version (it reads 3.14), CLAUDE.md, README.md, pyproject.toml, uv.lock, src/ces_revisions/__init__.py, tests/test_smoke.py, and four files under specs/: ces-revisions-prompt.md, ces-revisions-research-chatgpt.md, ces-revisions-research-claude.md and ces-revisions-research-gemini.md.
[you, tools] Read the package files. src/ces_revisions/__init__.py holds a `main()` that prints a greeting. tests/test_smoke.py holds two smoke tests: `main()` prints the greeting, and the console script resolves to `main`. pyproject.toml declares no runtime dependencies; its dev group is pytest and ruff.'''

CES_READS = '''[you, tools] Read specs/ces-revisions-prompt.md. Its full text:
{file:brief}
[you, tools] Read the first line, the heading lines and the first 3,000 characters of specs/ces-revisions-research-chatgpt.md:
{file:chatgpt}
[you, tools] Read the first line, the heading lines and the first 3,000 characters of specs/ces-revisions-research-claude.md:
{file:claude}
[you, tools] Read the first line, the heading lines and the first 3,000 characters of specs/ces-revisions-research-gemini.md:
{file:gemini}'''

CES_ROUTED = '''[earlier] You, in describe-critique-methodology: you routed the research brief specs/ces-revisions-prompt.md and the three research files to derive-roadmap, as background for staging the project, and said that nothing is built yet: the package is a scaffold with smoke tests.'''


def lines(*parts: str) -> str:
    return '\n'.join(parts)


# trigger-stages and trigger-decoy (R13d) -------------------------------------------------------

TRIGGER_STAGES_FIXTURE = lines(
    TODAY,
    '',
    '[session start] The working directory is a new git repository with one commit. It holds one file, README.md, whose one line reads `# county-permits`.',
    '[now] Your partner: I want building-permit records from three county portals pulled into one table, then updated every month, then a public summary page on top of it. Nothing exists yet. Can you lay out the stages for this?',
)

TRIGGER_STAGES_PASS = '''PASS needs one bar clause. Clause A (bar): the first skill named is derive-roadmap.
Reading notes. The first skill named is the first skill that the reply says it invokes. A reply that names no skill fails.'''

TRIGGER_DECOY_FIXTURE = lines(
    TODAY,
    '',
    '[session start] The working directory is a new git repository with one commit. It holds one file, README.md, whose one line reads `# timesheet-hours`.',
    '[now] Your partner: Let\'s build a small command-line tool that totals the hours in a timesheet CSV.',
)

TRIGGER_DECOY_PASS = '''PASS (guard): the first skill named is brainstorming.
Reading notes. As trigger-stages: the first skill named is the first skill that the reply says it invokes. A reply that names no skill fails.'''

TRIGGER_LEAK = r'New-Project|nothing built|outcome'

# dr-offer-scaffold and dr-offer-inputs (V1, R1b, V1b) -------------------------------------------

DR_OFFER_SCAFFOLD_FIXTURE = lines(
    SEC_HEAD,
    '[earlier] Your partner: Derive the roadmap for specs/sec-filing-index-ingestion-spec.md.',
    SEC_TREE,
    SEC_SPEC_READ,
    SEC_ADR,
    SEC_GAP,
    NO_ROADMAP,
)

DR_OFFER_PASS = '''PASS needs three bar clauses. Other batched questions may come with clause C's question.
Clause A (bar): the reply has no stage partition, stage list or roadmap text, including one offered "for approval".
Clause B (bar): it says, in any words, that no outcome works end to end yet.
Clause C (bar): it asks whether to stage the project from a list of outcomes that the partner ranks, in place of partitioning the requirements, and waits for the answer. It fails C when it switches to that path without asking.
Reading notes. Clause A: a list of named stages, phases or cycles counts, also when it is labeled draft, provisional or "for approval". A list of outcomes with no stage grouping is not a stage list. Clause B: a statement about the system as a whole passes, in any words: that nothing works yet, that nothing is built, or that no code exists beyond the scaffolds. The gap table shown with no such statement does not pass B. Clause C: the question offers the outcome list, ranked by the partner, as the basis for staging in place of a partition of the requirements. A question that asks only which requirements matter most, with a partition to follow, does not pass. "Waits for the answer" means that no stage, partition or roadmap text follows the question in the same message.'''

DR_OFFER_LEAK = r'New-Project|nothing built|outcome|rank'

EMB_TREE = '''[you, tools] Listed src/ and tests/, one line per module, from its docstring:
    src/embedding_data/__init__.py: empty file
    src/embedding_data/acs_benchmark_extract.py: "Define, submit, and download the IPUMS USA extracts for the ACS embedding benchmark."
    src/embedding_data/cps_benchmark_extract.py: "Define, submit, and download the IPUMS CPS extracts for the embedding benchmark."
    src/embedding_data/osha_benchmark_download.py: "Download the OSHA ITA case-detail data and dictionary, and convert the CSV to Parquet."
    src/embedding_data/cli.py: "Command-line entry point for the embedding-data extract scripts."
    tests/conftest.py: no docstring; the pytest fixtures `cli_runner`, `output_directory` and `dotenv_path`
    tests/test_acs_benchmark_extract.py: no docstring; imports `acs_benchmark_extract`
    tests/test_cps_benchmark_extract.py: no docstring; imports `cps_benchmark_extract`
    tests/test_cps_properties.py: no docstring; Hypothesis tests that import `cps_benchmark_extract`
    tests/test_osha_benchmark_download.py: no docstring; imports `osha_benchmark_download`
    tests/test_cli.py: no docstring; imports `cli`, `acs_benchmark_extract` and `cps_benchmark_extract`
[you, tools] Ran the suites. pytest (44) and Behave (2) pass. Five IPUMS extracts are on disk: usa_00001 to usa_00003 and cps_00001 to cps_00002.'''

DR_OFFER_INPUTS_FIXTURE = lines(
    TODAY + ' The repository is `embedding-data`, on branch `main`.\n',
    '[earlier] Your partner: Derive the roadmap for specs/embedding-evaluation-data-spec.md.',
    EMB_TREE,
    '[you, tools] Read specs/embedding-evaluation-data-spec.md. Its full text:',
    '{file:spec}',
    '[you, tools] Ran the gap analysis over the spec\'s numbered requirements. The table, with its key:',
    '{file:gap}',
    NO_ROADMAP,
)

# The last three words are checked in the gap table's notes (plan 78 Task 1 Step 3); a hit there is
# kept only where it is the historical evidence and not a verdict.
DR_OFFER_INPUTS_LEAK = r'New-Project|nothing built|outcome|rank|only|end to end|acquir'

# dr-offer-yes (V1, R4, R5, R15) ----------------------------------------------------------------

DR_OFFER_YES_FIXTURE = lines(
    DR_OFFER_SCAFFOLD_FIXTURE,
    '[earlier] You (your last message, in summary): You gave the gap table: 11 rows, R1 to R11, every verdict `missing`. You said that nothing in the repository works yet: the four packages are generated scaffolds with no code. You asked whether to stage the project from a list of outcomes that your partner ranks, with the spec\'s requirements as the candidates, in place of partitioning the requirements.',
    '[now] Your partner: Yes, do that.',
)

DR_OFFER_YES_PASS = '''PASS needs every bar and conformance clause.
Clause A (bar): a numbered list of outcomes in plain words, one line each, drawn from the spec's requirements.
Clause B (bar): the reply gives no ranking of its own, and it asks the partner to rank. The spec's order or list order, labeled as such, passes. A proposed priority order fails.
Clause C (bar): no roadmap text and no stage partition.
Clause D (conformance): at least one cost note with its basis, or a statement that only a run can measure it.
Reading notes. Clause A: an outcome in plain words says what the partner gets; a bare requirement number or a requirement's title alone is not one. A line that wraps is still one line. Clause B: a ranking of its own is any order that the reply recommends, proposes or calls a priority, or a pick of which outcome comes first. Clause C: as dr-offer-scaffold's clause A. Clause D: a basis is what the estimate rests on, such as a file count, a request rate, a data size or a comparable job.'''

DR_OFFER_YES_LEAK = r'New-Project|Leaves out|core stage'

# dr-built-guard (V5) ---------------------------------------------------------------------------

DR_BUILT_GUARD_FIXTURE = lines(
    TODAY + ' The repository is `visitor-forecast`, a daily visitor-count forecaster for a museum, on branch `main`.\n',
    '[earlier] Your partner: Derive the roadmap for specs/visitor-forecast.md.',
    '[you, tools] Read specs/visitor-forecast.md. Its first line is its title, "# Visitor forecast", with no header line above it. Its six numbered requirements:',
    '    R1. Load daily turnstile counts from the real turnstile export.',
    '    R2. A baseline seasonal forecast of daily visitors, 28 days ahead.',
    '    R3. Holiday effects, taken from the national public-holiday calendar.',
    '    R4. A weather covariate from the city\'s daily weather forecast.',
    '    R5. A weekly report for the front-of-house team.',
    '    R6. An accuracy dashboard that compares forecasts with actual counts.',
    '[you, tools] Ran the gap analysis over R1 to R6:',
    '| Req | Verdict | Evidence | Note |',
    '|---|---|---|---|',
    '| R1 | implemented-as-specified | `visitors/load.py`; `tests/test_load.py::test_reads_export_columns`, `tests/test_load.py::test_daily_totals_match_export` | |',
    '| R2 | implemented-as-specified | `visitors/baseline.py`; `tests/test_baseline.py::test_weekly_and_yearly_seasonality`, `tests/test_baseline.py::test_horizon_is_28_days` | |',
    '| R3 | implemented-differently | `visitors/baseline.py:41` | Five fixed holiday dates are hard-coded; the national calendar is not read |',
    '| R4 | missing | none found | |',
    '| R5 | missing | none found | |',
    '| R6 | missing | none found | |',
    '[you, tools] Daily counts from the real 2019–2025 turnstile export load, and the baseline forecast runs on them end to end; tests pass.',
    NO_ROADMAP,
)

DR_BUILT_GUARD_PASS = '''PASS (guard): the reply neither says that nothing is built nor offers outcome-first staging, and goes on by the existing flow: the table with any batched questions, a partition, or the single-stage exit.
Reading notes. Outcome-first staging is staging from a list of outcomes that the partner ranks, in place of a partition of the gaps. Saying that R4 to R6 are missing is not saying that nothing is built.'''

DR_BUILT_GUARD_LEAK = r'New-Project|nothing built|outcome'

# dr-known-progression (V2, R7-R9) --------------------------------------------------------------

DR_KNOWN_PROGRESSION_FIXTURE = lines(
    SEC_HEAD,
    '[earlier] Your partner: I want a roadmap for SEC filing ingestion. Nothing exists yet beyond the package scaffolds. The progression is: the quarterly and daily index files first, then the individual submissions, then 10-K and 8-K handling. The spec and the ADR in specs/ are background.',
    SEC_TREE,
    '[you, tools] Read specs/sec-filing-index-ingestion-spec.md as background. Its full text:',
    '{file:spec}',
    SEC_ADR,
    '[earlier] You (your last message, in summary): You sent the outcome list, each outcome with a cost note:',
    '    O1. The quarterly and daily index files, ingested into one filing-index table. Cost: small; about 130 quarterly files since 1993 plus one daily file per business day, minutes of downloading at the spec\'s 3 requests per second (basis: the SEC\'s full-index and daily-index directories).',
    '    O2. The individual submissions that the index rows name, downloaded. Cost: large; millions of files, weeks of downloading for the full history at 3 requests per second (basis: index row count times the request rate; not yet measured).',
    '    O3. 10-K and 8-K filings handled: picked out of the submissions, with their main documents extracted. Cost: unknown until the submissions are on disk (basis: none yet).',
    'You proposed one track, a known progression, and the name `sec-filing-ingestion`, and asked your partner to rank the outcomes.',
    '[now] Your partner: Rank them in the order I gave. One track, a known progression. The name is fine.',
)

DR_KNOWN_PROGRESSION_PASS = '''PASS needs every bar and conformance clause. Clause E is recorded and never scored.
Clause B (bar): the first stage's Exit requires no manifest, no traceability (a provenance or lineage record per row) and no point-in-time (as-of) awareness. A quality named as left out passes.
Clause A (conformance): committed stages cover, in order, the index files, the individual submissions, and 10-K and 8-K handling.
Clause C (conformance): manifests, traceability and point-in-time awareness each appear in a named later stage.
Clause D (conformance): every stage entry has a field that names what it leaves out and where that goes.
Clause E (recorded, no bar): the first stage's Exit does not require complete dataset generations to publish atomically. The background spec's §1 asks for that, and the skill text does not name it, so E checks transfer.
Reading notes. Clause B reads the first stage's Exit field, or the criteria that the reply gives for finishing the first stage when it has no field of that name. A manifest of any kind (source, run, ingestion or publication) fails B. Per-row provenance columns, such as a source id or a source hash, are traceability and fail B. A quality that the first stage names as not required, or as left out, passes. Clause A: committed stages are the stage entries of the roadmap file. Clause C: a named later stage is a stage entry after the first whose fields name the quality. Clause D: the field may have any name.'''

DR_KNOWN_PROGRESSION_LEAK = r'Leaves out|core stage|later stage|final-standard|hardening'

# dr-tracks and dr-research-depth (V3, R4, R7, R8) ----------------------------------------------

DR_TRACKS_FIXTURE = lines(
    CES_HEAD,
    CES_ROUTED,
    CES_TREE,
    CES_READS,
    '[now] Your partner: Go ahead and stage it.',
)

DR_TRACKS_PASS = '''PASS needs every bar and conformance clause.
Clause A (bar): an outcome about collection time or the collection interval and revision size sits in a different track from an outcome about budget, staffing or attrition, and the reply says why.
Clause B (conformance): no ranking is given as settled, and the reply asks the partner to rank.
Clause C (conformance): one message with no roadmap text.
Clause D (conformance): a cost note for model fitting or compute, with a basis or a statement that the core stage measures it.
Reading notes. Clause A: a track is a grouping that the reply says can be ranked, run or stopped on its own. Two stages of one sequence are not separate tracks. "Says why" is any reason given for keeping the two apart. Clause B: an order proposed to the partner for approval is not settled; an order that the reply states as decided is. Clause C: roadmap text is the roadmap file's content or a stage partition; a list of outcomes and tracks is not roadmap text. Clause D: "the core stage measures it" is any statement that the first run on real data measures the cost.'''

DR_TRACKS_LEAK = r'New-Project|research track|separate track'

DR_RESEARCH_DEPTH_FIXTURE = lines(
    CES_HEAD,
    CES_ROUTED,
    CES_TREE,
    CES_READS,
    '[earlier] Your partner: Go ahead and stage it.',
    '[earlier] You (your last message, in summary): You listed the outcomes, one plain line each:',
    '    O1. How the size of the one-month revision moves with the number of collection days before first release.',
    '    O2. How the size of the two-month revision moves with the first-closing collection rate.',
    '    O3. How much of the one- and two-month revisions comes from late sample reports, and how much from seasonal-factor revision.',
    '    O4. How revision size moves with real BLS appropriations, continuing resolutions and shutdowns.',
    '    O5. How revision size moves with BLS staffing counts.',
    '    O6. How revision size moves with CES sample size and sample attrition.',
    'You proposed two research tracks. Track A, collection interval and revision size: O1, O2 and O3. Track B, budget, staffing and attrition: O4, O5 and O6. Your reason for the split: Track A rests on sharp month-to-month calendar variation that public release dates give directly; Track B\'s covariates move slowly, trend together and must be hand-built from budget justifications and archived releases, and its answer does not change Track A\'s model. Your cost notes: the release calendar and the monthly vintages take a day or two to assemble; the budget and staffing series take several days to hand-build; the time of one model fit on about 40 years of monthly vintages is unknown until a first fit runs on real data. You proposed the name `ces-revisions`.',
    '[now] Your partner: Tracks are right, both research. Track A first. In Track A: O1, then O3, then O2. In Track B: O6, then O4, then O5. The name is fine.',
)

DR_RESEARCH_DEPTH_PASS = '''PASS needs every bar and conformance clause.
Clause A (bar): each track commits exactly one stage, and every other outcome of the track sits in a ranked list, not in a committed stage.
Clause B (bar): each committed stage's Exit names a cost of the real run to measure and record: time, compute or data volume.
Clause C (conformance): the two tracks stay separate.
Clause D (conformance): each stage entry names what it leaves out.
Clause E (conformance): each committed stage's Produces names a file that records the result and the measured cost.
Reading notes. Clause A: a committed stage is a stage entry of the roadmap file, such as a checkbox entry or a numbered stage with its fields. A stage entry labeled provisional, tentative or later still counts as committed. A ranked list is a list kept outside the stage entries, in the partner's order. Clause B: the Exit, or the stage's finishing criteria when it has no field of that name, must require the cost to be measured and recorded; a cost named only as an estimate does not pass. Clause C: no stage entry mixes outcomes of both tracks. Clause E: the file may be named by path or by a plain file name.'''

DR_RESEARCH_DEPTH_LEAK = r'core stage|measured cost|Leaves out'

# dr-resume-rerank (V6, R11) --------------------------------------------------------------------

# A new-project roadmap in the format of plan 78 Task 3 Step 4, before Task 3 adds that format.
LOCK_ROADMAP = '''# Lock closures and river levels — roadmap

> For agentic workers: REQUIRED SKILL: derive-roadmap — resume via its
> reconcile step; route each unticked stage per its ROUTING line; never plan
> this document wholesale.

## Outcomes

Source: your partner's words, 2026-10-14. Background: none.
Choices made: none.

| # | Outcome | Track | Rank | Cost (estimate; basis) |
|---|---|---|---|---|
| O1 | How the chance that a lock closes moves with the upstream river-gauge level | A | 1 | measured by Stage 1 |
| O2 | A 7-day closure-risk outlook for each lock from the river-level forecast | A | 2 | one model run a day, small once O1's model exists; basis: Stage 1's fit time |
| O3 | Separate closure curves for all 14 locks, pooled across locks | A | 3 | about 14 times Stage 1's data; basis: Stage 1's data volume |
| O4 | A closure-history map for the canal's boat operators | A | 4 | about a day of work; basis: one static map page |

Tracks: A — lock closures and river level (research).

## Stages

- [x] Stage 1: Closure response to river level
      Objective: Measure how the chance of a lock closure moves with the upstream gauge level, on the real closure log and gauge readings.
      Outcomes: O1
      Consumes: nothing
      Produces: specs/lock-closures-stage-1-findings.md, with the result and the measured cost of the real run
      Exit: O1's response curve, fit on the real closure log and gauge readings, is in the findings file; the run's time, compute and data volume are recorded there
      Leaves out: per-lock curves (Ranked list, O3); the outlook (Ranked list, O2); the map (Ranked list, O4)
      ROUTING: brainstorming

> Stage 1: COMPLETE (2026-11-03) — implemented by plan 4 (specs/plans/completed/4-closure-river-level-response.md).
> Next: resume the roadmap.

## Ranked list — Track A
1. O2 — one model run a day, small once O1's model exists
2. O3 — about 14 times Stage 1's data
3. O4 — about a day of work

## Stage-spec stamp

Each stage spec's Rollout note carries this line, which writing-plans then copies verbatim into the stage plan's header:

> Roadmap: specs/lock-closures-roadmap.md, Stage N — on plan completion, tick the stage and re-validate later stages against what shipped.

## Completion

derive-roadmap's §6, run over the Outcomes list.'''

DR_RESUME_RERANK_FIXTURE = lines(
    TODAY + ' The repository is `lock-closures`, on branch `main`.\n',
    '[earlier] Your partner: Resume the roadmap.',
    '[you, tools] Read specs/lock-closures-roadmap.md. Its full text:',
    LOCK_ROADMAP,
    '[you, tools] `git log` on the roadmap: it was written on 2026-10-14, and Stage 1\'s tick and stamp were added on 2026-11-03, when plan 4 completed. No resume has run since the roadmap was written.',
    '[you, tools] Read plan 4, specs/plans/completed/4-closure-river-level-response.md. Its `## Handoff to later stages` reads `None: shipped as the roadmap\'s Produces states.`',
    '[you, tools] Read specs/lock-closures-stage-1-findings.md. Its full text:',
    '# Stage 1 findings: lock closures and river level',
    'Result: below a gauge level of 3.1 m a lock closes on fewer than 2% of days; above it the chance rises steeply, to about 60% at 3.8 m.',
    'The four locks with the longest records show close to the same curve.',
    'Cost of the real run: one fit on 11 years of daily gauge readings, 1.8 GB, took 22 minutes on a laptop.',
)

DR_RESUME_RERANK_PASS = '''PASS needs every bar and conformance clause.
Clause A (bar): no completion review starts, and the roadmap is neither parked nor retired.
Clause C (bar): one question that asks for a re-ranking of the list or the approval of a proposed next stage from it, with a default.
Clause B (conformance): the reply reports the core's finding and its measured cost.
Clause D (conformance): no new stage entry is written before the answer.
Reading notes. Clause A: a completion review is the audit run before a roadmap retires (derive-roadmap §6). Stopping the track offered as one option of the question is not parking. Clause C: the one question may offer options; a default is the answer that the reply proposes or takes if the partner agrees, such as "Stage 2 is O2 unless you re-order". Two or more separate questions fail C. Clause B: the finding is the 3.1 m level or the steep rise above it; the cost is the 22-minute, 1.8 GB run. Clause D: a new stage entry is a stage entry written into the roadmap text; a proposed stage described in the question is not an entry.'''

DR_RESUME_LEAK = r're-rank|promote|stop the track'

# dr-resume-legacy (R11 guard) ------------------------------------------------------------------

PARKING_ROADMAP = '''# Parking occupancy pipeline — roadmap

> For agentic workers: REQUIRED SKILL: derive-roadmap — resume via its
> reconcile step; route each unticked stage per its ROUTING line; never plan
> this document wholesale.

Source spec: `specs/parking-occupancy-spec.md`. Derived 2026-09-02.

## Gap analysis

| Req | Verdict | Evidence | Note |
|---|---|---|---|
| R1 | missing | none found | |
| R2 | missing | none found | |
| R3 | implemented-differently | `sensors/poll.py:18` polls every 15 minutes | §2 asks for 5 minutes |
| R4 | missing | none found | |
| R5 | missing | none found | |
| R6 | missing | none found | |

## Stages

- [x] Stage 1: Sensor ingest
      Objective: Bay-sensor events from every car park land in one events table every 5 minutes.
      Spec: §2 R1–R3
      Gap closed: R1; R2; R3
      Consumes: the sensor vendor's event feed
      Produces: the `bay_events` table and its loader
      Exit: events from all 9 car parks arrive within 5 minutes; a test shows that a duplicate event is stored once
      ROUTING: writing-plans

> Stage 1: COMPLETE (2026-09-19) — implemented by plan 2 (specs/plans/completed/2-sensor-ingest.md). Its Handoff section names what Stage 2 consumes.
> Next: resume the roadmap.

- [x] Stage 2: Occupancy rates
      Objective: Occupancy per car park is computed every 15 minutes from the events table.
      Spec: §3 R4
      Gap closed: R4
      Consumes: Stage 1's `bay_events` table (plan 2, Handoff)
      Produces: the `occupancy` table
      Exit: occupancy for each car park and 15-minute slot matches a hand count on two sample days
      ROUTING: writing-plans

> Stage 2: COMPLETE (2026-10-08) — implemented by plan 3 (specs/plans/completed/3-occupancy-rates.md). Its Handoff section names what Stage 3 consumes.
> Next: resume the roadmap.

- [x] Stage 3: Occupancy dashboard and alerts
      Objective: Staff see live occupancy per car park and get an alert when one passes 95%.
      Spec: §4 R5, R6
      Gap closed: R5; R6
      Consumes: Stage 2's `occupancy` table (plan 3, Handoff; Resolved at resume, 2026-10-09)
      Produces: the dashboard and the alert rule
      Exit: the dashboard shows all 9 car parks; in a test, an alert fires when occupancy passes 95%
      ROUTING: brainstorming

> Stage 3: COMPLETE (2026-11-04) — implemented by plan 5 (specs/plans/completed/5-occupancy-dashboard.md).
> Next: resume the roadmap.

## Stage-spec stamp

Each stage spec's Rollout note carries this line, which writing-plans then copies verbatim into the stage plan's header:

> Roadmap: specs/parking-occupancy-spec-roadmap.md, Stage N — on plan completion, tick the stage and re-validate later stages against what shipped.

## Completion

Retire this roadmap only after a conformance audit of the accumulated system: re-run the gap rubric over every numbered requirement (R1–R6), with evidence per verdict. Each unmet requirement either becomes a new stage, keeping this roadmap live, or is deferred consciously with a written why. Then move this file to specs/completed/ beside the retired spec.'''

DR_RESUME_LEGACY_FIXTURE = lines(
    TODAY + ' The repository is `parking-occupancy`, on branch `main`.\n',
    '[earlier] Your partner: Resume the roadmap.',
    '[you, tools] Read specs/parking-occupancy-spec-roadmap.md. Its full text:',
    PARKING_ROADMAP,
    '[you, tools] `git log` on the roadmap: the last resume, on 2026-10-09, handed off Stage 3. Stage 3\'s tick and stamp were added on 2026-11-04, when plan 5 completed.',
    '[you, tools] Read plan 5, specs/plans/completed/5-occupancy-dashboard.md. Its `## Handoff to later stages` reads `None`.',
)

DR_RESUME_LEGACY_PASS = '''PASS (guard): the reply goes to the completion review. It says every stage is complete and starts or proposes the audit over the spec's requirements, and it asks no re-ranking question.
Reading notes. The audit over the spec's requirements is the gap rubric re-run over R1 to R6 (derive-roadmap §6). A re-ranking question asks the partner to order, or pick from, a list of further work.'''

# dcm-describe-route (V4, R13b) -----------------------------------------------------------------

DCM_DESCRIBE_FIXTURE = lines(
    SEC_HEAD,
    '[earlier] Your partner: Write the methodology description of this filing-index ingestion system for an external SOTA critique.',
    SEC_TREE,
    SEC_SPEC_READ,
)

DCM_DESCRIBE_PASS = '''PASS needs three bar clauses.
Clause A (bar): no methodology description, notation table or template slot, and none planned as the next step.
Clause B (bar): the reply says, in any words, that the system has nothing built.
Clause C (bar): it routes to derive-roadmap to stage the project, and says the critique comes after the system is built. A route to brainstorming alone fails C.
Reading notes. Clause A: a template slot is any filled section of the methodology template. A plan to write a description of the spec's design next fails A; such a description offered to the partner as one option of a question does not. Clause B: as dr-offer-scaffold's clause B, said of the filing-index ingestion system. Clause C needs both parts: derive-roadmap named as the next step, to stage the project, and the critique placed after the system is built.'''

DCM_DESCRIBE_LEAK = r'New-Project|nothing built'

# dcm-synth-route (V3, R13c) --------------------------------------------------------------------

DCM_SYNTH_FIXTURE = lines(
    CES_HEAD,
    '[earlier] Your partner: The research is back. Use synthesize mode: the description is specs/ces-revisions-prompt.md and the critiques are the three research files.',
    CES_TREE,
    CES_READS,
)

DCM_SYNTH_PASS = '''PASS needs three bar clauses.
Clause A (bar): no triage table and no spec text, now or as the next step.
Clause B (bar): the reply says that the description is a brief for something not built, or that nothing is built.
Clause C (bar): it routes the files to derive-roadmap as background for staging.
Reading notes. Clause A: a triage table is any table or list that sorts the research files' points into accept, reject, defer or similar verdicts. Spec text is any section of a design spec. A plan to write either next fails A; either one offered to the partner as one option of a question does not. Clause C: the route names derive-roadmap and gives it the brief and the research files as inputs for staging.'''

DCM_SYNTH_LEAK = r'New-Project|nothing built|background'

# bs-route and bs-guard (R13a) ------------------------------------------------------------------

BS_ROUTE_FIXTURE = lines(
    TODAY,
    '',
    '[session start] The working directory is a new git repository with one commit. It holds one file, README.md, whose one line reads `# tide-extremes`.',
    '[earlier] Your partner: I want to collect hourly water-level readings from four coastal tide stations\' public feeds, clean them and fill the gaps, then publish the monthly high and low extremes for each station as a CSV and a chart. Nothing exists yet.',
    '[earlier] You: You restated the request: hourly readings from four stations\' public feeds, cleaned and gap-filled, then monthly extremes per station, published as a CSV and a chart. You asked who will use it and what success looks like.',
    '[now] Your partner: A harbor-master group uses it. Success is one year of clean monthly extremes for each station. Python, run on their laptop. Build it in the order I said.',
)

BS_ROUTE_PASS = '''PASS needs three bar clauses.
Clause A (bar): the reply hands the project to derive-roadmap in this session, to stage the outcomes: it invokes the skill, or says it does so now.
Clause B (bar): it lays out no approaches for the whole project.
Clause C (bar): it writes no design document or spec file, and asks no question that the conversation already answers.
Reading notes. Clause A: a written Skill call to derive-roadmap, or a statement that it hands over to derive-roadmap now, passes. A handoff put off to a later or fresh session, or only asked about ("shall I use derive-roadmap?"), fails. Clause B: an approach is a way to build the whole project; two or more such ways, or one presented as the design, fail B. Clause C: the conversation already answers who uses it, what success is, the language, where it runs and the order of the work.'''

BS_LEAK = r'New-Project|roadmap|nothing built'

BS_GUARD_FIXTURE = lines(
    TODAY,
    '',
    '[session start] The working directory is a new git repository with one commit. It holds one file, README.md, whose one line reads `# gpx-summary`.',
    '[earlier] Your partner: I want a small script that reads a folder of GPX track files and writes one CSV with each track\'s distance and duration. Nothing exists yet.',
    '[earlier] You: You restated the request and asked one question: which units the CSV should use for distance and duration.',
    '[now] Your partner: Kilometres for distance and minutes for duration. If a file fails to parse, skip it and print its name to stderr.',
)

BS_GUARD_PASS = '''PASS (guard): the reply lays out two or three ways to build it, in this message, with a recommendation and one question asking which way to go. It does not hand off to derive-roadmap.
Reading notes. A way to build it is an approach to the whole script, such as a choice of parsing library or of structure. The message asks one question, which way to go; a message with further questions fails.'''

# -----------------------------------------------------------------------------------------------


def case(spec, kind, texts, fixture, task, pass_rule, leak, files=None):
    return {'spec': spec, 'kind': kind, 'texts': texts, 'model': OPUS, 'budget': BUDGET,
            'fixture': fixture, 'task': task, 'pass': pass_rule, 'void': VOID, 'leak': leak,
            'bar': ADDITIVE if kind == 'additive' else NON_REGRESSION, 'files': files or {}}


CASES = {
    'trigger-stages': case('R13d', 'additive', NO_TEXTS, TRIGGER_STAGES_FIXTURE, TRIGGER_TASK,
                           TRIGGER_STAGES_PASS, TRIGGER_LEAK),
    'trigger-decoy': case('R13d guard', 'non-regression', NO_TEXTS, TRIGGER_DECOY_FIXTURE, TRIGGER_TASK,
                          TRIGGER_DECOY_PASS, TRIGGER_LEAK),
    'dr-offer-scaffold': case('V1, R1b', 'additive', DR, DR_OFFER_SCAFFOLD_FIXTURE, STEP_TASK, DR_OFFER_PASS,
                              DR_OFFER_LEAK, {'spec': SEC_SPEC}),
    'dr-offer-inputs': case('V1b', 'additive', DR, DR_OFFER_INPUTS_FIXTURE, STEP_TASK, DR_OFFER_PASS,
                            DR_OFFER_INPUTS_LEAK, {'spec': EMB_SPEC, 'gap': EMB_GAP}),
    'dr-offer-yes': case('V1, R4, R5, R15', 'additive', DR, DR_OFFER_YES_FIXTURE, STEP_TASK, DR_OFFER_YES_PASS,
                         DR_OFFER_YES_LEAK, {'spec': SEC_SPEC}),
    'dr-built-guard': case('V5', 'non-regression', DR, DR_BUILT_GUARD_FIXTURE, STEP_TASK, DR_BUILT_GUARD_PASS,
                           DR_BUILT_GUARD_LEAK),
    'dr-known-progression': case('V2, R7-R9', 'additive', DR, DR_KNOWN_PROGRESSION_FIXTURE, ROADMAP_TASK,
                                 DR_KNOWN_PROGRESSION_PASS, DR_KNOWN_PROGRESSION_LEAK, {'spec': SEC_SPEC}),
    'dr-tracks': case('V3, R4', 'additive', DR, DR_TRACKS_FIXTURE, STEP_TASK, DR_TRACKS_PASS, DR_TRACKS_LEAK,
                      CES_FILES),
    'dr-research-depth': case('V3, R7, R8', 'additive', DR, DR_RESEARCH_DEPTH_FIXTURE, ROADMAP_TASK,
                              DR_RESEARCH_DEPTH_PASS, DR_RESEARCH_DEPTH_LEAK, CES_FILES),
    'dr-resume-rerank': case('V6, R11', 'additive', DR, DR_RESUME_RERANK_FIXTURE, STEP_TASK, DR_RESUME_RERANK_PASS,
                             DR_RESUME_LEAK),
    'dr-resume-legacy': case('R11 guard', 'non-regression', DR, DR_RESUME_LEGACY_FIXTURE, STEP_TASK,
                             DR_RESUME_LEGACY_PASS, DR_RESUME_LEAK),
    'dcm-describe-route': case('V4, R13b', 'additive', DCM_D, DCM_DESCRIBE_FIXTURE, STEP_TASK, DCM_DESCRIBE_PASS,
                               DCM_DESCRIBE_LEAK, {'spec': SEC_SPEC}),
    'dcm-synth-route': case('V3, R13c', 'additive', DCM_S, DCM_SYNTH_FIXTURE, STEP_TASK, DCM_SYNTH_PASS,
                            DCM_SYNTH_LEAK, CES_FILES),
    'bs-route': case('R13a', 'additive', BS, BS_ROUTE_FIXTURE, STEP_TASK, BS_ROUTE_PASS, BS_LEAK),
    'bs-guard': case('R13a guard', 'non-regression', BS, BS_GUARD_FIXTURE, STEP_TASK, BS_GUARD_PASS, BS_LEAK),
}
