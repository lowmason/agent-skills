'''Tests for deferral_scan.py — the lost-deferral scan (advisory mode).

The B1 fixtures are copied whole from the audit base 6186635 as literal text, so
the tests never call `git show` (a CI checkout is shallow).
'''
from __future__ import annotations

import pytest

from deferral_scan import Candidate, main, unmarked

# specs/plans/completed/4-audit_1_3_26.md:19 at 6186635.
PLAN_4 = '''**Out of scope (deferred to a future plan):** audit §9 P2 — cross-skill wiring (§6), token-economy trims, personalization passes (§7), and the critic items (§8). The audit doc stays in `specs/` until those land.'''

# specs/completed/agents-and-commands-expansion.md:233-234 at 6186635.
# Two literals joined, so build/test_runtime_support.py's dependency scan reads
# no command reference here; the value is the source text unchanged.
FIX_ISSUE = ('''- A live end-to-end `/fix'''
             '''-issue` run against a real GitHub issue is
  interactive verification, deferred to first real use.''')

# specs/deferred_items.md:996-1002 at 6186635 (the deferral sentence is :999).
TASK_BRIEF_NOTE = '''      → done 2026-09-03 (/deferred quick fix): all three arms added, 11 tests → 14, each
      mutation-checked against the bash line it targets and the three scripts confirmed
      byte-identical afterwards. The `bad HEAD` test pins the message, not just the exit code.
      Still untested and worth a future item: the *operator* boundary at `task-brief:48` —
      changing `<= tlvl` to `< tlvl` leaves all 14 green, because `### Task 2` is terminated
      by the Task-heading rule before the level comparison is consulted. `CLAUDE.md`'s test
      counts were synced in the same pass (this suite 11 → 14, design-architecture 8 → 9).'''

# specs/deferred_items.md:849-858 at 6186635 (the deferral sentence is :857).
SBC_RANK_NOTE = '''      → done 2026-09-03 (/deferred quick fix): fixed and, per the item's own instruction,
      actually run. **The recorded remedy above is wrong — do not follow it.** `np.atleast_1d`
      on both is a no-op on a scalar site's `(L,)` draws array, so `draws[..., idx]` still
      indexes the *draw* axis: 200 replications returned only {0, 1} (chi2 = 1901.9, p = 0.000).
      Shipping it verbatim would have traded a loud crash for a silently wrong SBC conclusion.
      The fix needs a second guard, `draws.reshape(draws.shape[0], -1)`, alongside the
      `atleast_1d`. Verified by extracting the sketch text from the edited file and executing
      it: scalar and vector sites both return well-spread ints in [0, L]. The 11 bayesian-
      workflow script tests still pass. Standing gap, not closed: no bundled suite covers this
      reference file, so the recipe can regress silently again.'''

# specs/deferred_items.md:379-384 at 6186635 (the deferral sentence is :382-384).
SESS8_NOTE = '''      → retired 2026-09-02: the premise does not hold — the filename also carries each
      session's own sess8, so two titleless sessions land in distinct digests; pinned by
      test_two_titleless_sessions_do_not_collide, which passes on unchanged code. The
      neighbouring real hazard (the idempotence glob keys on sess8 alone, so two
      sessions sharing an 8-char id prefix would skip the second) is a separate,
      unrecorded item.'''

# specs/plans/completed/29-snippet-execution-gate.md:693 at 6186635 (a heading).
PLAN_29_HEADING = '''### Task 5: Harnessed execution, two-tier pinned/floating'''

# specs/plans/completed/29-snippet-execution-gate.md:710 at 6186635.
PLAN_29_FLOATING = '''**Pinned vs floating — the tension, resolved two-tier.** Pinning is reproducible but goes blind to exactly the upstream drift audit Theme 1 is about; floating catches drift but makes the gate's verdict non-reproducible. So: the **pinned** run is the hard gate (exit 1); a **floating** run is advisory (stderr, exit 0). Pinned set verified 2026-09-08 — `arviz==1.3.0`, `arviz-stats==1.3.2`, `arviz-plots==1.3.1`, `numpyro==0.21.0`, `jax==0.11.1`. Record that provenance line beside the constant and refresh it deliberately.'''

# specs/completed/audit_9_2_26.md:200 at 6186635.
SCORECARD_200 = '''- **`bayesian-workflow` (6/9)** — Body 3,964 words with 12 references already available; no boundary section toward track-model-experiments / tune-hyperparameters / recommend-probabilistic-model, which all point here. Three scripts untested; jax-numerics shipped RED-only (GREEN not run, by convention).'''

# specs/completed/audit_1_3_26.md:139 at 6186635.
# Two literals joined, so build/test_runtime_support.py's dependency scan reads
# no skill section reference here; the value is the source text unchanged.
AUDIT_1_3_139 = '''**bayesian-workflow** ❗ — Content is excellent and NumPyro-faithful; the wrapper is the problem. Fix: frontmatter YAML (§1.1) and PDFs (§1.2); delete `main.py` (hello-world stub) + `pyproject.toml` (empty-dep uv-init scaffolding) and the README lines describing them; README install instructions clone the *upstream* repo — rewrite for this repo's symlink reality; description → drafted "Use when…" rewrite (977 chars but summarizes content); add a 3-line siblings block (explore-data upstream; consume recommend-probabilistic-model's''' ''' §6 handoff payload; validate-data downstream) — the recommender names this skill ~20 times and defines a handoff interface this skill never acknowledges; move the BlackJAX sampler block (SKILL.md:177-229) and ArviZ porting table to references/ (~2k tokens per activation); fix stale "PyMC 5/PyMC 6" comments in the ported scripts (the code branches on ArviZ versions) and the `--loo-pit` figure-name mismatch vs reporting.md's template.'''

PHRASELESS = pytest.mark.xfail(strict=False, reason='no deferral phrase; see plan 74 Task 0')


@pytest.mark.parametrize(
    'text',
    [PLAN_4, FIX_ISSUE, TASK_BRIEF_NOTE, SBC_RANK_NOTE, SESS8_NOTE],
    ids=['PLAN_4', 'FIX_ISSUE', 'TASK_BRIEF_NOTE', 'SBC_RANK_NOTE', 'SESS8_NOTE'],
)
def test_catches_each_phrase_bearing_b1_fixture(text):
    assert unmarked(text) != []


@pytest.mark.parametrize(
    'text',
    [
        pytest.param(PLAN_29_HEADING, marks=PHRASELESS, id='PLAN_29_HEADING'),
        pytest.param(PLAN_29_FLOATING, marks=PHRASELESS, id='PLAN_29_FLOATING'),
        pytest.param(SCORECARD_200, marks=PHRASELESS, id='SCORECARD_200'),
        pytest.param(AUDIT_1_3_139, marks=PHRASELESS, id='AUDIT_1_3_139'),
    ],
)
def test_phraseless_b1_fixtures_record_the_limit(text):
    assert unmarked(text) != []


def test_item_marker_resolves_its_unit():
    assert unmarked(PLAN_4 + ' → item: 9-x — 2026-01-01') == []


def test_dropped_marker_resolves_its_unit():
    assert unmarked(PLAN_4 + ' → dropped: landed in abc123') == []


def test_marker_in_another_unit_does_not_count():
    # Adjacent bullets with no blank line: only the list-item split separates them.
    text = (
        '- The retry path is deferred to a future plan.\n'
        '- The cache rework landed. → item: 9-x — 2026-01-01\n'
    )
    assert unmarked(text) == [Candidate(1, '- The retry path is deferred to a future plan.')]
    # A heading is a unit of its own, so a marker on the next line does not answer it.
    heading = '## Retry path deferred to a future plan\n→ item: 9-x — 2026-01-01\n'
    assert unmarked(heading) == [Candidate(1, '## Retry path deferred to a future plan')]


def test_protocol_status_header_is_exempt():
    filed = ('**Status: COMPLETE (2026-01-01)** — executed via x; '
             'deferred items in specs/deferred_items.md')
    nothing = '**Status: COMPLETE (2026-01-01)** — executed via x; nothing deferred'
    assert unmarked(filed) == []
    assert unmarked(nothing) == []


def test_skipped_line_is_exempt():
    assert unmarked('> Skipped: needs a DSN → deferred') == []
    assert unmarked('> Skipped: needs a DSN → deferred (same successor item)') == []


def test_skipped_line_with_second_deferral_is_flagged():
    # Text after the Skipped line's own arrow note is not exempt.
    line = '> Skipped: needs a DSN → deferred; Step 5 is deferred to a future plan'
    assert unmarked(line) == [Candidate(1, line)]
    # The variants found in plans 19, 36 and 49 stay exempt.
    assert unmarked('> **Skipped: the human-run half → deferred.** Req 12') == []
    assert unmarked('> **Skipped: the human-run half → deferred.**') == []
    assert unmarked('> Skipped: no valid reps → deferred (same successor item)') == []
    assert unmarked("> Skipped: Task 9's runs → deferred.") == []


@pytest.mark.parametrize('text', [
    'nothing is deferred.',
    'Nothing is deferred.',
    'Nothing else is deferred.',
    'none of this is deferred',
    'None are deferred.',
    'nothing that matters is deferred',
    'no new work is deferred',
    'No new work is deferred by this task.',
    'In this plan, nothing was deferred.',
    'Skip the append if nothing was deferred.',
    'X is implemented by this plan, and no new work is deferred.',
    # A Markdown prefix at the unit start, and an em dash, open a clause too.
    '- Nothing is deferred.',
    '* None are deferred.',
    '> Nothing is deferred.',
    '**No new work is deferred.**',
    'Review is clean — nothing is deferred.',
    '1. None are deferred.',
    # `other` alone is not an exception word, and a sentence end stops the tail.
    'No other work is deferred.',
    'Nothing is deferred. But the plan was long.',
    # After `, : — (` the negation word `nothing` or `none` opens a clause.
    'Result: nothing is deferred.',
])
def test_negated_deferral_statement_is_not_flagged(text):
    assert unmarked(text) == []


@pytest.mark.parametrize('text', [
    'Step 5 is deferred to a later plan',
    'The scorecard fix is deferred.',
    'The retry logic with no backoff is deferred.',
    'Cases with no tests are deferred.',
    'The task has no owner and is deferred.',
    'The step, with no extra cost, is deferred.',
    'No work is deferred, but the T6 gap is deferred.',
    # A line break inside a sentence does not open a clause.
    'The retry logic with\nno backoff is deferred.',
    # A relative clause or `such as` does not open the subject's clause.
    'The gap that no test covers is deferred.',
    'The gap that nothing covers is deferred.',
    'Gaps that no one owns are deferred.',
    'Failures such as no backoff are deferred.',
    # A spaced hyphen mid-line is not a Markdown prefix.
    'The retry work - no tests yet - is deferred.',
    # After `, : — (` a bare `no` is an appositive, not a clause subject.
    'Known gap: no backoff is deferred.',
    'Known gap, no backoff is deferred.',
    'Open item: no owner is deferred.',
    'Result: no work is deferred.',
    'In this plan, no work was deferred.',
])
def test_negation_not_opening_its_clause_is_still_flagged(text):
    assert len(unmarked(text)) == 1


@pytest.mark.parametrize('text', [
    # An exception right after the verb names the work that is deferred.
    'Nothing is deferred except the scorecard.',
    'Nothing is deferred, except for the scorecard fix.',
    'Nothing is deferred but the scorecard.',
    'Nothing is deferred other than the retry work.',
    'Nothing is deferred\nexcept the scorecard.',
    # An exception word is never one of the subject's words.
    'Nothing but the scorecard is deferred.',
    'Nothing except retry is deferred.',
    'Nothing besides the scorecard is deferred.',
    '- No tests but retry is deferred.',
])
def test_negation_with_an_exception_is_still_flagged(text):
    assert len(unmarked(text)) == 1


def test_code_span_neither_flags_nor_marks():
    assert unmarked('`deferred to a future plan`') == []
    assert unmarked(PLAN_4 + ' `→ item: x`') == [Candidate(1, PLAN_4 + ' `→ item: x`')]


def test_fenced_block_is_ignored():
    assert unmarked('```\n' + PLAN_4 + '\n```\n') == []
    # Tilde fences hold no backticks, so the code-span rule cannot hide the line.
    assert unmarked('~~~\n' + PLAN_4 + '\n~~~\n') == []
    # A run with text after it does not close the fence.
    assert unmarked('~~~\n~~~ x\n' + PLAN_4 + '\n~~~\n') == []


def test_nested_fence_is_ignored():
    text = '````\n```\n' + PLAN_4 + '\n```\n````\n' + PLAN_4 + '\n'
    assert unmarked(text) == [Candidate(6, PLAN_4)]


def test_scan_cli_prints_path_line_text_and_exits_0(tmp_path, capsys):
    f = tmp_path / 'plan.md'
    f.write_text(PLAN_4 + '\n', encoding='utf-8')
    assert main(['scan', str(f)]) == 0
    assert capsys.readouterr().out == f'{f}:1: {PLAN_4.strip()}\n'


def test_non_utf8_file_does_not_stop_the_scan(tmp_path, capsys):
    bad = tmp_path / 'bad.md'
    bad.write_bytes(b'\xff\xfe not utf-8 \x80\n')
    good = tmp_path / 'good.md'
    good.write_text(PLAN_4 + '\n', encoding='utf-8')
    assert main(['scan', str(bad), str(good)]) == 0
    captured = capsys.readouterr()
    assert captured.out == f'{good}:1: {PLAN_4.strip()}\n'
    assert f'{bad}: cannot read' in captured.err
