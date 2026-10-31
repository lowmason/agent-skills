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
    # An exception word later on the same line, past an adverbial or a mark,
    # still names the deferred work.
    'Nothing is deferred here except the scorecard.',
    'Nothing is deferred in this plan except the scorecard.',
    'Nothing is deferred by this task except the scorecard.',
    'Nothing is deferred today except the scorecard.',
    'Nothing is deferred for now, except the scorecard.',
    'Nothing is deferred — except the scorecard.',
    'Nothing is deferred (except the scorecard).',
    '**Nothing is deferred** except the scorecard.',
    'Nothing is deferred; except the scorecard.',
    'Nothing is deferred with the exception of the scorecard.',
    'Nothing is deferred, excluding the scorecard.',
    # The safe-direction false flag: a later exception word on the same line
    # flags the line even when it belongs to another clause.
    'Nothing is deferred; all tests pass except the flaky one.',
])
def test_negation_with_an_exception_is_still_flagged(text):
    assert len(unmarked(text)) == 1


@pytest.mark.parametrize('text', [
    # An adverbial or a trailing clause with no exception word keeps the exemption.
    'Nothing is deferred in this plan.',
    'No new work is deferred by this task.',
    'Nothing is deferred yet.',
    'Nothing is deferred (all tasks landed).',
    'Nothing is deferred; the plan retires.',
    'Nothing is deferred, and the plan retires.',
    'Nothing is deferred because every task landed.',
    'Nothing is deferred from this plan.',
    'Nothing is deferred during execution.',
    'Nothing is deferred here.',
    'Nothing is deferred today.',
    'Nothing is deferred for now.',
    'Nothing is deferred — every task landed.',
    '**Nothing is deferred** in this plan.',
    'Nothing else is deferred at this stage.',
    '- Nothing is deferred by this plan.',
    '> No new work is deferred in this round.',
    'Nothing was deferred; every task landed with its tests.',
    'Nothing is deferred, since all four tasks landed.',
    # An exception word after the sentence ends is not read.
    'Nothing is deferred here. Except for style, all is done.',
    # A longer word that starts with an exception word is not one.
    'Nothing is deferred, exceptional as that is.',
])
def test_negation_with_a_trailing_clause_is_not_flagged(text):
    assert unmarked(text) == []


@pytest.mark.parametrize('text', [
    # A period inside a token does not end the sentence, so the exception is read.
    'Nothing is deferred in install.py except the scorecard.',
    'Nothing is deferred in v2.1 except retry.',
    'Nothing is deferred (see section 3.2), except retry.',
    'Nothing is deferred, i.e. today, except retry.',
    # A line break inside the sentence does not end it either.
    'Nothing is deferred\nhere except the scorecard.',
    'Nothing is deferred in this plan\nexcept the scorecard.',
    'Nothing is deferred\nexcluding the scorecard.',
    'Nothing is deferred\nwith the exception of retry.',
    'Nothing is deferred here, other\nthan retry.',
    # The counted and the sole exception forms name the deferred work too.
    'Nothing is deferred, with one exception: retry.',
    'Nothing is deferred, with the sole exception of retry.',
    'Nothing is deferred, with a single exception.',
    'Nothing is deferred, with the only exception being retry.',
    'Nothing is deferred, with an exception for retry.',
])
def test_negation_with_an_exception_later_in_the_sentence_is_still_flagged(text):
    assert len(unmarked(text)) == 1


@pytest.mark.parametrize('text', [
    'Nothing is deferred in install.py.',
    'Nothing is deferred in v2.1; every task landed.',
    '**Nothing is deferred.** Except for style, all is done.',
    'Nothing is deferred.) Except for style, all is done.',
    'Nothing is deferred, with no exceptions.',
    'Nothing is deferred in this plan\nand every task landed.',
    'Nothing is deferred in this plan.\nExcept for style, all is done.',
    'Nothing is deferred today! Except for style, all is done.',
    'Nothing is deferred? Apart from style, yes.',
    'Nothing is deferred."\nExcept for style, all is done.',
    # A sentence may open with a mark, a digit or a code span.
    'Nothing is deferred. **Except for style**, all is done.',
    'Nothing is deferred. (Except for style, all is done.)',
    'Nothing is deferred. "Except for style," he said.',
    'Nothing is deferred. 3 tasks landed, other than T5 which was dropped.',
    'Nothing is deferred. `deferral_scan.py` flags everything except code spans.',
])
def test_negation_ends_at_the_sentence_end_across_lines(text):
    assert unmarked(text) == []


@pytest.mark.parametrize('text', [
    # An underscore that opens or closes emphasis is not part of a word.
    '_The scorecard fix is deferred_ for now.',
    'The retry work is _left for later_.',
    'Retry goes to _a future plan_.',
    '_The fix is deferred._',
])
def test_underscore_emphasis_does_not_hide_a_deferral(text):
    assert len(unmarked(text)) == 1


@pytest.mark.parametrize('text', [
    # A single `*`, `***` or `_` around a negation opens its clause like `**` does.
    '*Nothing is deferred.*',
    '***Nothing is deferred.***',
    '_No new work is deferred in this round._',
    '__Nothing is deferred.__',
    '- *Nothing is deferred.*',
    '> _None are deferred._',
    # An underscore inside a word stays part of it.
    'The is_deferred flag is set.',
])
def test_emphasis_around_a_negation_is_not_flagged(text):
    assert unmarked(text) == []


def test_emphasis_around_a_negation_still_reads_its_exception():
    assert len(unmarked('*Nothing is deferred except retry.*')) == 1
    assert len(unmarked('_Nothing is deferred_ except retry.')) == 1


@pytest.mark.parametrize('text', [
    # Only a unit-start opener lets emphasis through; mid-unit, `_no` opens no clause.
    'Known gap; _no backoff_ is deferred.',
    'Known gap. _No backoff_ is deferred.',
])
def test_emphasis_on_a_negation_mid_unit_is_still_flagged(text):
    assert len(unmarked(text)) == 1


def test_real_deferral_coordinated_with_a_negation_is_flagged():
    text = 'Nothing is deferred in the parser and the retry fix is deferred.'
    assert len(unmarked(text)) == 1


@pytest.mark.parametrize('text', [
    'Every task landed and nothing is deferred.',
    'Every task landed and nothing else is deferred.',
    'Every task landed\nand nothing else is deferred.',
    'The scorecard is filed as item 12 and nothing else is deferred.',
    'Every task landed, and nothing else is deferred.',
    'The plan retires; and no other work is deferred.',
    # After a sentence end, a colon, a bracket or a dash, `and` starts a clause.
    'All tasks landed. And nothing else is deferred.',
    'Every task landed — and nothing else is deferred.',
    'Done: and nothing else is deferred.',
    'All landed (and nothing else is deferred).',
])
def test_clause_and_nothing_else_is_not_flagged(text):
    assert unmarked(text) == []


def test_bare_save_after_the_verb_is_an_exception():
    assert len(unmarked('Nothing is deferred save the scorecard.')) == 1
    assert len(unmarked('Nothing is deferred, save retry.')) == 1
    assert unmarked('Nothing is deferred, saving a round.') == []


def test_unless_after_the_verb_is_an_exception():
    assert len(unmarked('Nothing is deferred unless retry counts.')) == 1
    assert len(unmarked('Nothing is deferred, unless the probe fails.')) == 1


@pytest.mark.parametrize('text', [
    # `beyond` and `only` after the verb also name a scope or a manner, so they
    # are not read as exceptions: these clean statements stay exempt.
    'Nothing is deferred beyond this plan.',
    'Nothing is deferred, only reordered.',
    # A bare `no` after `;` or a full stop opens a clause, as at the unit start.
    'Review is clean; no work is deferred.',
    'All landed. No work is deferred.',
    # A noun joined by `and` to `nothing else` reads like a clause join, so these
    # stay exempt too (a known gap: here the noun is the deferred work).
    'The scorecard and nothing else is deferred.',
    'X and no other work is deferred.',
    'Retry and none other is deferred.',
    'The scorecard and none else is deferred.',
])
def test_ambiguous_words_keep_the_exemption(text):
    assert unmarked(text) == []


def test_code_span_neither_flags_nor_marks():
    assert unmarked('`deferred to a future plan`') == []
    assert unmarked(PLAN_4 + ' `→ item: x`') == [Candidate(1, PLAN_4 + ' `→ item: x`')]


def test_fenced_block_is_ignored():
    assert unmarked('```\n' + PLAN_4 + '\n```\n') == []
    # Tilde fences hold no backticks, so the code-span rule cannot hide the line.
    assert unmarked('~~~\n' + PLAN_4 + '\n~~~\n') == []
    # A run with text after it does not close the fence.
    assert unmarked('~~~\n~~~ x\n' + PLAN_4 + '\n~~~\n') == []


@pytest.mark.parametrize('marker', ['- ', '* ', '1. ', '  - '])
@pytest.mark.parametrize('fence', ['```', '~~~'])
def test_fence_opened_after_a_list_marker_is_ignored(marker, fence):
    # Its bare closer closes it, so the line after the block is read again.
    text = f'{marker}{fence}text\n  {PLAN_4}\n  {fence}\n{PLAN_4}\n'
    assert unmarked(text) == [Candidate(4, PLAN_4)]


@pytest.mark.parametrize('fence', ['```', '~~~'])
def test_fence_opened_after_a_list_marker_still_starts_a_unit(fence):
    # Codex review of 1ad8165: the masked opener must still end the bullet before it,
    # or the marker after the block resolves that bullet's deferral too.
    text = f'- {PLAN_4}\n- {fence}text\n  x\n  {fence}\n  → item: y\n'
    assert unmarked(text) == [Candidate(1, f'- {PLAN_4}')]


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


LINT_FAIL = ("deferral lint: 1 unmarked candidate(s) in 1 file(s); "
             "add a → item: or → dropped: marker in each one's paragraph\n")
LINT_CLEAN = 'deferral lint: clean\n'


def _lint(tmp_path, files, baseline=()):
    '''Build a tmp repo of files (repo-relative path -> text), run lint, return the exit code.'''
    root = tmp_path / 'repo'
    root.mkdir()
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(text, bytes):
            path.write_bytes(text)
        else:
            path.write_text(text, encoding='utf-8')
    listing = tmp_path / 'baseline.txt'
    listing.write_text(''.join(f'{line}\n' for line in baseline), encoding='utf-8')
    return main(['lint', '--baseline', str(listing), '--root', str(root)])


def test_lint_passes_when_every_file_is_on_the_baseline(tmp_path, capsys):
    code = _lint(tmp_path, {'specs/completed/old.md': PLAN_4 + '\n'},
                 baseline=['specs/completed/old.md'])
    assert code == 0
    assert capsys.readouterr().out == LINT_CLEAN


def test_lint_fails_on_a_new_unmarked_file(tmp_path, capsys):
    code = _lint(tmp_path, {'specs/completed/old.md': PLAN_4 + '\n'})
    assert code == 1
    assert capsys.readouterr().out == f'specs/completed/old.md:1: {PLAN_4}\n' + LINT_FAIL


def test_lint_passes_a_new_marked_file(tmp_path, capsys):
    code = _lint(tmp_path, {'specs/completed/new.md': PLAN_4 + ' → item: x\n'})
    assert code == 0
    assert capsys.readouterr().out == LINT_CLEAN


def test_lint_reads_markdown_only(tmp_path, capsys):
    code = _lint(tmp_path, {'specs/completed/kit/run.py': PLAN_4 + '\n'})
    assert code == 0
    assert capsys.readouterr().out == LINT_CLEAN


def test_lint_reads_both_completed_folders(tmp_path, capsys):
    code = _lint(tmp_path, {'specs/plans/completed/new.md': PLAN_4 + '\n'})
    assert code == 1
    assert capsys.readouterr().out == f'specs/plans/completed/new.md:1: {PLAN_4}\n' + LINT_FAIL


def test_lint_reads_subfolders(tmp_path, capsys):
    code = _lint(tmp_path, {'specs/plans/completed/sub/new.md': PLAN_4 + '\n'})
    assert code == 1
    assert capsys.readouterr().out == f'specs/plans/completed/sub/new.md:1: {PLAN_4}\n' + LINT_FAIL


def test_lint_ignores_markdown_outside_the_completed_folders(tmp_path, capsys):
    code = _lint(tmp_path, {'specs/live.md': PLAN_4 + '\n', 'specs/plans/9-x.md': PLAN_4 + '\n'})
    assert code == 0
    assert capsys.readouterr().out == LINT_CLEAN


@pytest.mark.parametrize('line', ['./specs/completed/old.md', 'completed/old.md',
                                  'specs/completed/old', 'specs/completed/OLD.md'])
def test_lint_baseline_match_is_exact(tmp_path, capsys, line):
    code = _lint(tmp_path, {'specs/completed/old.md': PLAN_4 + '\n'}, baseline=[line])
    assert code == 1
    assert capsys.readouterr().out.endswith(LINT_FAIL)


def test_lint_counts_candidates_and_files(tmp_path, capsys):
    code = _lint(tmp_path, {'specs/completed/a.md': PLAN_4 + '\n\n' + PLAN_4 + '\n',
                            'specs/completed/b.md': PLAN_4 + '\n',
                            'specs/completed/c.md': 'Nothing here.\n'})
    assert code == 1
    out = capsys.readouterr().out
    assert out.splitlines()[:3] == [f'specs/completed/a.md:1: {PLAN_4}',
                                    f'specs/completed/a.md:3: {PLAN_4}',
                                    f'specs/completed/b.md:1: {PLAN_4}']
    assert out.endswith('deferral lint: 3 unmarked candidate(s) in 2 file(s); '
                        "add a → item: or → dropped: marker in each one's paragraph\n")


def test_lint_fails_closed_on_an_unreadable_file(tmp_path, capsys):
    code = _lint(tmp_path, {'specs/completed/bad.md': b'\xff\xfe not utf-8 \x80\n'})
    assert code == 1
    captured = capsys.readouterr()
    assert 'specs/completed/bad.md: cannot read' in captured.err
    assert captured.out == 'deferral lint: 1 file(s) could not be read\n'


def test_lint_never_opens_a_baselined_file(tmp_path, capsys):
    code = _lint(tmp_path, {'specs/completed/bad.md': b'\xff\xfe not utf-8 \x80\n'},
                 baseline=['specs/completed/bad.md'])
    assert code == 0
    assert capsys.readouterr().out == LINT_CLEAN


def test_lint_skips_a_directory_with_a_markdown_name(tmp_path, capsys):
    code = _lint(tmp_path, {'specs/completed/notes.md/readme.txt': PLAN_4 + '\n'})
    assert code == 0
    assert capsys.readouterr().out == LINT_CLEAN


def test_lint_skips_a_dangling_markdown_symlink(tmp_path, capsys):
    # An Emacs lock file `.#x.md` is a dangling symlink: it has no text to scan.
    root = tmp_path / 'repo'
    folder = root / 'specs' / 'completed'
    folder.mkdir(parents=True)
    (folder / 'x.md').write_text('Nothing here.\n', encoding='utf-8')
    (folder / '.#x.md').symlink_to('nowhere')
    listing = tmp_path / 'baseline.txt'
    listing.write_text('', encoding='utf-8')
    code = main(['lint', '--baseline', str(listing), '--root', str(root)])
    captured = capsys.readouterr()
    assert code == 0, captured.err
    assert captured.out == LINT_CLEAN


def test_lint_scans_a_live_markdown_symlink(tmp_path, capsys):
    # The dangling-link skip must not hide a live link to a flagged file.
    root = tmp_path / 'repo'
    folder = root / 'specs' / 'completed'
    folder.mkdir(parents=True)
    target = tmp_path / 'outside.txt'
    target.write_text(PLAN_4 + '\n', encoding='utf-8')
    (folder / 'link.md').symlink_to(target)
    listing = tmp_path / 'baseline.txt'
    listing.write_text('', encoding='utf-8')
    code = main(['lint', '--baseline', str(listing), '--root', str(root)])
    assert code == 1
    assert capsys.readouterr().out == f'specs/completed/link.md:1: {PLAN_4}\n' + LINT_FAIL


def test_lint_fails_on_a_missing_baseline(tmp_path, capsys):
    (tmp_path / 'specs' / 'completed').mkdir(parents=True)
    code = main(['lint', '--baseline', str(tmp_path / 'absent.txt'), '--root', str(tmp_path)])
    assert code == 1
    assert 'cannot read baseline' in capsys.readouterr().err
