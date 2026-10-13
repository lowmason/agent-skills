'''Tests for settle.py and `cli.py settle`: the report grammar, triage's
completeness and fail-safe rules, the discard rule for verify, audit and
files, and the bookkeeping each prints (drift spec R8.4-R8.8, R11.5).'''
import json
import shlex
from datetime import datetime, timezone

import pytest

import baseline
import cli
import packets
import settle
import state
from cc_fixtures import (DOCS, FIXTURE_RELEASE, GUIDE_PATH, MANIFEST_TOML, docs_dir, fixture_repo,  # noqa: F401
                         fixture_state, guide_text, isolated_home, prime_cache, write_tree)
from lint import CLI

NOW = datetime(2026, 10, 4, 12, 0, tzinfo=timezone.utc)
CONFORMANCE = 'uv run --python 3.13 --with pyyaml python build/check_conformance.py'
TAIL = [f'  {CLI} baseline stamp', f'  {CLI} lint', f'  {CONFORMANCE}']
CITER = '#!/bin/sh\n' + '#' + ' cc-guide: alpha.overview @2.1.899\nexit 0\n'
# A new events.md block that names both beta sections' terms.
RETRY = '## Retry\n\nA retry resends `BETA_ENV` with each `BetaEvent`.\n'


@pytest.fixture
def world(tmp_path, docs_dir, isolated_home):
    '''A committed fixture repo, and a cache at the default path under the
    isolated HOME, so settle's commands name no --cache (CX-1).'''
    repo = fixture_repo(tmp_path / 'repo', {GUIDE_PATH: guide_text(), state.MANIFEST: MANIFEST_TOML,
                                            state.BASELINE: state.dump_baseline(fixture_state(docs_dir)),
                                            'hooks/gate.sh': CITER})
    cache = state.default_cache()
    write_tree(state.snapshot_docs(cache, FIXTURE_RELEASE), DOCS)
    prime_cache(cache, docs_dir)
    return repo, cache


def load(world):
    return packets.load(state.Source(world[0]), world[1], NOW)


def latest(world, files):
    write_tree(state.latest_docs(world[1]), files)


def settled(folder, *rows):
    (folder / packets.REPORT).write_text('\n'.join(rows) + '\n')
    return settle.settle(folder)


def triage(world, tmp_path, through=None):
    return packets.triage(load(world), tmp_path / 'p', through)


@pytest.mark.parametrize('line, count, quoted, fields', [
    ('B1 | NOISE | - | - | - | "a | b "c"" | why | it has a pipe', 7, settle.TRIAGE_QUOTES,
     ['B1', 'NOISE', '-', '-', '-', '"a | b "c""', 'why | it has a pipe']),
    ('| B1 | TOUCHES | x.y | 4 | "g" | "s" | why |', 7, settle.TRIAGE_QUOTES,
     ['B1', 'TOUCHES', 'x.y', '4', '"g"', '"s"', 'why']),
    ('2.1.901 | none', 2, (), ['2.1.901', 'none']),
    ('B1 | NOISE | why', 7, settle.TRIAGE_QUOTES, None),
    ('B1 | NOISE | - | - | "unclosed | why', 7, settle.TRIAGE_QUOTES, None),
    # A free-text field that opens with a quote ends at the next pipe, as in
    # the 2026-10-12 skill probe's files row.
    ('a.md:22 | "no edit tools": no Write | x.y | "a | b" | consistent', 5, settle.FILES_QUOTES,
     ['a.md:22', '"no edit tools": no Write', 'x.y', '"a | b"', 'consistent']),
])
def test_a_row_splits_on_pipes_but_a_quote_field_holds_pipes_and_quotes(line, count, quoted, fields):
    assert settle.split_row(line, count, quoted) == fields


def test_a_quote_field_drops_its_outer_quotes_and_a_dash_is_no_quote():
    assert [settle.unquote(f) for f in ('"a "b" c"', '-', '', 'bare')] == ['a "b" c', '', '', 'bare']


def test_table_separators_header_rows_and_prose_are_no_rows():
    text = '\n'.join(['# Report', 'Prose without a pipe.', settle.TRIAGE_ROW, '|---|---|', '| item | verdict |',
                      'B1 | NOISE | - | - | - | "s" | why'])
    assert settle.report_lines(text) == ['B1 | NOISE | - | - | - | "s" | why']


def test_a_complete_triage_advances_every_section_and_rebaselines_the_block(world, tmp_path):
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = triage(world, tmp_path)
    result = settled(out, settle.TRIAGE_ROW,
                     'B1 | NOISE | - | - | - | "runs alpha batches" | a wording change; the guide claims nothing here',
                     '2.1.901 | none', '2.1.902 | none')
    assert result.lines == [
        f'cc-guide settle: triage, {out}',
        'report: 1 item(s) answered, 2 of 2 release(s) covered; 0 quote(s) not found; 0 unparseable line(s); '
        '0 left out',
        'then, in this order (R8.8):',
        f"  {CLI} baseline rebaseline alpha 'tools › Tools'",
        f'  {CLI} baseline advance alpha.overview alpha.reference beta.overview beta.reference --to 2.1.902',
        *TAIL]
    assert result.clean
    assert json.loads((out / packets.SETTLED).read_text()) == {
        'mode': 'triage', 'advance_to': '2.1.902', 'verify': [],
        'cleared': ['alpha.overview', 'alpha.reference', 'beta.overview', 'beta.reference'], 'held': [], 'rows': {}}


def test_a_report_handed_back_indented_settles_as_written(world, tmp_path):
    '''The Agent tool hands a report back with every line indented. Saved
    unchanged, as the skill says, it settles the same.'''
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = triage(world, tmp_path)
    rows = ['B1 | NOISE | - | - | - | "runs alpha batches" | a wording change', '2.1.901 | none', '2.1.902 | none']
    assert settled(out, *(f'  {r}' for r in rows)) == settled(out, *rows)
    out = review(world, tmp_path / 'r')
    rows = [GOOD, 'B | 2.1.901 | adds ALPHA_ENV | changelog.md:14', 'C | an omission']
    assert settled(out, *(f'  {r}' for r in rows)) == settled(out, *rows)


def test_an_omitted_block_and_a_missing_coverage_line_go_to_verify_as_unsure(world, tmp_path):
    '''R8.4 step 4: silence never counts as NOISE.'''
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = triage(world, tmp_path)
    result = settled(out, '2.1.901 | none')
    assert result.lines == [
        f'cc-guide settle: triage, {out}',
        'report: 0 item(s) answered, 1 of 2 release(s) covered; 0 quote(s) not found; 0 unparseable line(s); '
        '2 left out',
        'UNSURE or TOUCHES alpha.overview: B1: no row',
        'UNSURE or TOUCHES beta.overview: 2.1.902: no coverage line',
        'then, in this order (R8.8):',
        f'  {CLI} baseline advance alpha.reference beta.reference --to 2.1.902',
        *TAIL,
        'verify: /cc-guide verify alpha.overview beta.overview; or defer it, and those sections do not advance, '
        'so the next triage shows them again']
    assert not result.clean
    saved = json.loads((out / packets.SETTLED).read_text())
    assert (saved['verify'], saved['rows']) == (['alpha.overview', 'beta.overview'], {
        'alpha.overview': ['B1, block tools › Tools: no row'],
        'beta.overview': ['2.1.902: no coverage line; its bullets that hint at it: "Changed how `BETA_ENV` is read"']})


def test_a_failed_quote_makes_noise_unsure_and_is_listed_on_touches(world, tmp_path):
    '''R8.4 step 5: a row whose quote fails becomes UNSURE, handled as
    TOUCHES, so triage fails safe.'''
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = triage(world, tmp_path)
    noise = 'B1 | NOISE | - | - | - | "runs alpha quickly" | wording'
    touches = '2.1.902#1 | TOUCHES | beta.overview | 31 | "| `BETA_ENV` | off |" | "how `BETA_ENV` is read" | moved'
    result = settled(out, noise, touches, '2.1.901 | none', '2.1.902 | beta.overview')
    assert result.lines[1:6] == [
        'report: 2 item(s) answered, 2 of 2 release(s) covered; 2 quote(s) not found; 0 unparseable line(s); '
        '0 left out',
        f'  quote not found, NOISE becomes UNSURE: {noise}',
        f'  quote not found, TOUCHES becomes UNSURE: {touches}',
        "UNSURE or TOUCHES alpha.overview: B1: its NOISE row's source quote was not found",
        'UNSURE or TOUCHES beta.overview: 2.1.902#1: TOUCHES, quote not found; '
        '2.1.902: its coverage line names it']
    assert not result.clean


def test_an_unparseable_row_is_listed_and_a_bullets_falls_back_to_its_hints(world, tmp_path):
    out = triage(world, tmp_path)
    rows = ['B9 | TOUCHES | alpha.overview | 14 | "g" | "s" | no such item',
            '2.1.901#1 | TOUCHES | gamma.overview | 1 | "g" | "s" | no such section',
            '2.1.902#2 | NOISE | - | - | - | "Fixed a crash" |']
    result = settled(out, *rows, '2.1.901 | alpha.reference', '2.1.902 | none')
    assert result.lines[1:5] == [
        'report: 0 item(s) answered, 2 of 2 release(s) covered; 0 quote(s) not found; 3 unparseable line(s); '
        '0 left out', *(f'  unparseable row: {r}' for r in rows)]
    assert 'UNSURE or TOUCHES alpha.reference: 2.1.901#1: its row does not parse; 2.1.901: its coverage line names it' \
        in result.lines


def test_a_release_no_coverage_line_and_no_hint_reaches_is_an_owner_item_that_caps_the_advance(world, tmp_path):
    changelog = DOCS['changelog.md'].replace(
        '<Update label="2.1.902"', '<Update label="2.1.903" description="October 3, 2026">\n'
        '  * Fixed a typo\n</Update>\n\n<Update label="2.1.902"')
    latest(world, {'changelog.md': changelog})
    out = triage(world, tmp_path)
    result = settled(out, '2.1.901 | none', '2.1.902 | none')
    assert "owner: 2.1.903: no coverage line, and its bullets hit no section's terms" in result.lines
    assert f'  {CLI} baseline advance alpha.overview alpha.reference beta.overview beta.reference --to 2.1.902' \
        in result.lines


def test_the_first_release_range_settles_the_block_findings(world, tmp_path):
    '''R8.4's split: block findings ride in the oldest range, so a block
    resolved there is rebaselined, and its sections advance only to the
    range's end.'''
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = triage(world, tmp_path, '2.1.901')
    result = settled(out, 'B1 | NOISE | - | - | - | "runs alpha batches" | a wording change', '2.1.901 | none')
    assert result.lines[2:5] == [
        'then, in this order (R8.8):', f"  {CLI} baseline rebaseline alpha 'tools › Tools'",
        f'  {CLI} baseline advance alpha.overview alpha.reference beta.overview beta.reference --to 2.1.901']
    assert result.lines[-1] == f'next range, once these commands are run: {CLI} packets --triage --through 2.1.902'


def test_a_missing_pages_held_sections_are_saved_and_hold_their_groups_blocks(world, tmp_path):
    '''A held section never advances, its group's blocks are not
    rebaselined, and settled.json carries the hold into verify.'''
    (state.latest_docs(world[1]) / 'events.md').unlink()
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches'),
                   'env-vars.md': DOCS['env-vars.md'].replace('Turns on beta', 'Turns on every beta')})
    out = triage(world, tmp_path)
    i = json.loads((out / packets.INDEX).read_text())
    assert [(b['item'], b['group']) for b in i['blocks']] == [('B1', 'alpha'), ('B2', 'beta')]
    result = settled(out, 'B1 | NOISE | - | - | - | "runs alpha batches" | a wording change',
                     'B2 | NOISE | - | - | - | "Turns on every beta" | a wording change', '2.1.901 | none',
                     '2.1.902 | none')
    assert [line for line in result.lines if 'baseline' in line][:2] == [
        f"  {CLI} baseline rebaseline alpha 'tools › Tools'",
        f'  {CLI} baseline advance alpha.overview alpha.reference --to 2.1.902']
    assert json.loads((out / packets.SETTLED).read_text())['held'] == ['beta.overview', 'beta.reference']


def test_the_haiku_case_a_section_the_hints_miss_still_goes_to_verify(world, tmp_path):
    '''R11.5's acceptance case, modelled on 2.1.293 (Haiku 5.5 became the
    `haiku` alias on the Anthropic API): the release's bullet hints only one
    section, while the docs block that changed names more. A verifier that
    answers the bullet and leaves the block out still sends every candidate
    section to verify.'''
    latest(world, {'events.md': DOCS['events.md'] + RETRY})
    out = triage(world, tmp_path)
    i = json.loads((out / packets.INDEX).read_text())
    assert [(b['ref'], b['candidates']) for b in i['blocks']] == [
        ('events › Events › Retry', ['beta.overview', 'beta.reference'])]
    assert i['releases'][1]['bullets'][0]['hints'] == ['beta.overview']
    bullet = '2.1.902#1 | TOUCHES | beta.overview | 31 | "| `BETA_ENV` | on |" | "how `BETA_ENV` is read" | reads'
    left_out = settled(out, bullet, '2.1.901 | none', '2.1.902 | beta.overview')
    assert json.loads((out / packets.SETTLED).read_text())['verify'] == ['beta.overview', 'beta.reference']
    assert 'UNSURE or TOUCHES beta.reference: B1: no row' in left_out.lines
    cleared = settled(out, bullet, 'B1 | NOISE | - | - | - | "A retry resends `BETA_ENV`" | retries are not claimed',
                      '2.1.901 | none', '2.1.902 | beta.overview')
    assert json.loads((out / packets.SETTLED).read_text())['verify'] == ['beta.overview']
    assert cleared.clean


def test_a_noise_bullet_whose_quote_fails_falls_back_to_its_hints_or_caps_the_advance(world, tmp_path):
    '''Review finding 3: a NOISE row's failed quote never clears its item.
    A bullet's falls back to its hints, as a broken bullet row does, or is
    an owner item that caps the advance below its release.'''
    out = triage(world, tmp_path)
    hinted = '2.1.901#1 | NOISE | - | - | - | "not in the bullet" | harmless'
    bare = '2.1.902#2 | NOISE | - | - | - | "not in the bullet" | harmless'
    result = settled(out, hinted, bare, '2.1.901 | none', '2.1.902 | none')
    assert "UNSURE or TOUCHES alpha.reference: 2.1.901#1: its NOISE row's source quote was not found" in result.lines
    assert ("owner: 2.1.902#2: its NOISE row's source quote was not found, and its bullet hits no section's terms"
            in result.lines)
    assert f'  {CLI} baseline advance alpha.overview beta.overview beta.reference --to 2.1.901' in result.lines


def test_a_bullets_owner_item_caps_the_advance_below_its_release(world, tmp_path):
    '''Review finding 4: the cap reads an owner item's release, not its
    wording.'''
    out = triage(world, tmp_path)
    result = settled(out, '2.1.902#2 | broken', '2.1.901 | none', '2.1.902 | none')
    assert "owner: 2.1.902#2: its row does not parse, and its bullet hits no section's terms" in result.lines
    assert (f'  {CLI} baseline advance alpha.overview alpha.reference beta.overview beta.reference --to 2.1.901'
            in result.lines)
    assert json.loads((out / packets.SETTLED).read_text())['advance_to'] == '2.1.901'


def test_a_source_quote_counts_only_within_its_own_item(world, tmp_path):
    '''The packet's own scaffolding and another item's text are no source
    for an item: a NOISE row quoting them becomes UNSURE.'''
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = triage(world, tmp_path)
    scaffold = 'B1 | NOISE | - | - | - | "Current text:" | the packet\'s own words'
    other = '2.1.902#1 | NOISE | - | - | - | "Fixed a crash" | another bullet\'s words'
    result = settled(out, scaffold, other, '2.1.901 | none', '2.1.902 | none')
    assert result.lines[2:4] == [f'  quote not found, NOISE becomes UNSURE: {scaffold}',
                                 f'  quote not found, NOISE becomes UNSURE: {other}']
    assert "UNSURE or TOUCHES alpha.overview: B1: its NOISE row's source quote was not found" in result.lines
    assert "UNSURE or TOUCHES beta.overview: 2.1.902#1: its NOISE row's source quote was not found" in result.lines


def test_a_noise_rows_guide_quote_is_checked_when_given(world, tmp_path):
    '''Second review, finding 3: a NOISE row may leave its guide quote out,
    but one it gives must be found, or the row becomes UNSURE.'''
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = triage(world, tmp_path)
    noise = 'B1 | NOISE | alpha.overview | 14 | "guide fiction" | "runs alpha batches" | harmless'
    result = settled(out, noise, '2.1.901 | none', '2.1.902 | none')
    assert f'  quote not found, NOISE becomes UNSURE: {noise}' in result.lines
    assert "UNSURE or TOUCHES alpha.overview: B1: its NOISE row's guide quote was not found" in result.lines
    assert not any('rebaseline' in line for line in result.lines)
    assert not result.clean


def test_a_noise_row_whose_why_is_a_dash_does_not_parse(world, tmp_path):
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = triage(world, tmp_path)
    dash = 'B1 | NOISE | - | - | - | "runs alpha batches" | -'
    result = settled(out, dash, '2.1.901 | none', '2.1.902 | none')
    assert f'  unparseable row: {dash}' in result.lines
    assert 'UNSURE or TOUCHES alpha.overview: B1: no row' in result.lines


# ---- verify and audit --------------------------------------------------------

def review(world, tmp_path, sids=('alpha.overview', 'alpha.reference'), settled_triage=None):
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    return packets.verify(load(world), tmp_path / 'v', list(sids), settled_triage)[0]


GOOD = 'L14 | Alpha uses ALPHA_TOOL | STALE | tools.md:5 | "runs alpha batches" | Alpha batches with `ALPHA_TOOL`.'


def test_a_verify_report_lists_corrections_owners_calls_and_the_bookkeeping(world, tmp_path):
    write_tree(tmp_path / 't', {packets.SETTLED: json.dumps(
        {'mode': 'triage', 'advance_to': '2.1.902', 'verify': ['alpha.overview'], 'cleared': [], 'rows': {}})})
    out = review(world, tmp_path, settled_triage=tmp_path / 't' / packets.SETTLED)
    result = settled(out, settle.VERIFY_ROW, GOOD,
                     'L19 | Set ALPHA_ENV | CONFIRMED | changelog.md:14 | "Added `ALPHA_ENV`" | -',
                     'L19 | the tick span | NOT FOUND | - | - | -',
                     'L14 | prefer alpha | JUDGMENT | - | - | -',
                     'B | 2.1.901 | adds ALPHA_ENV to the alpha tools | changelog.md:14',
                     'C | the guide never says what ALPHA_TOOL costs')
    assert result.lines == [
        f'cc-guide settle: verify alpha, {out}',
        "report: 1 confirmed, 1 correction(s), 3 owner's call, 0 unverified",
        'corrections, to apply to the guide in the working tree:',
        '  L14 alpha.overview STALE: Alpha uses ALPHA_TOOL → Alpha batches with `ALPHA_TOOL`. '
        '(tools.md:5: "runs alpha batches")',
        "owner's call, never applied:",
        '  L19 alpha.reference NOT FOUND: the tick span',
        '  L14 alpha.overview JUDGMENT: prefer alpha',
        '  omission: the guide never says what ALPHA_TOOL costs',
        'unverified, discarded:',
        'changelog items (B):',
        '  2.1.901 | adds ALPHA_ENV to the alpha tools | changelog.md:14',
        'then, in this order (R8.8), once every correction is applied; for one you leave for the owner, settle '
        'again with --hold <section>, which holds the section and keeps its accept:',
        f'  {CLI} baseline accept alpha.overview --substantive   # only the sections you changed',
        f"  {CLI} baseline rebaseline alpha 'tools › Tools'",
        f'  {CLI} baseline advance alpha.overview alpha.reference --to 2.1.902',
        *TAIL,
        "a correction that resolves a conformance gap removes its [[exception]] from build/cc_guide/conformance.toml "
        "in the same change; lint's STALE lines then name the citing files of each section whose `changed` moved"]
    assert result.clean


def test_a_failed_verify_quote_is_discarded_and_holds_its_section(world, tmp_path):
    '''R8.8 step 1: the refresh's rule, the opposite of triage's escalation.
    A discarded correction holds its section, so nothing advances past it.'''
    out = review(world, tmp_path)
    bad = 'L14 | Alpha uses ALPHA_TOOL | WRONG | tools.md:5 | "runs alpha slowly" | Alpha batches.'
    result = settled(out, bad, 'L19 | Set ALPHA_ENV | CONFIRMED | tools.md:1 | "not on the page" | -')
    assert result.lines[1:8] == [
        "report: 0 confirmed, 0 correction(s), 0 owner's call, 2 unverified",
        'corrections, to apply to the guide in the working tree:',
        "owner's call, never applied:",
        'unverified, discarded:',
        f'  quote not found, discarded: {bad}',
        '  quote not found, discarded: L19 | Set ALPHA_ENV | CONFIRMED | tools.md:1 | "not on the page" | -',
        'changelog items (B):']
    assert result.lines[8:10] == ['left out (no surviving row, no none line), so held: alpha.overview alpha.reference',
                                  'held, neither advanced nor audited: alpha.overview alpha.reference']
    assert not any('rebaseline' in line or 'accept' in line for line in result.lines if line.startswith('  '))
    assert not result.clean


def test_a_correction_next_to_a_todo_owner_or_outside_the_packet_is_the_owners_call(world, tmp_path):
    out = review(world, tmp_path, sids=('alpha.reference',))
    guide = (out / packets.GUIDE).read_text().split('\n')
    guide[17] = '<!-- TODO(owner): decide the alpha stance -->'  # line 18, just above line 19
    (out / packets.GUIDE).write_text('\n'.join(guide))
    near = 'L19 | Set ALPHA_ENV | STALE | tools.md:5 | "runs alpha batches" | Set ALPHA_ENV twice.'
    result = settled(out, near, GOOD)
    assert result.lines[3:6] == [
        "owner's call, never applied:",
        '  L19 alpha.reference STALE (next to a TODO(owner), report-only): Set ALPHA_ENV → Set ALPHA_ENV twice.',
        "  L14 alpha.overview STALE (outside this packet's sections, so it holds nothing; "
        '/cc-guide verify alpha.overview reviews it): Alpha uses ALPHA_TOOL → Alpha batches with `ALPHA_TOOL`.']


def test_a_todo_owner_reaches_through_the_first_list_item_after_it(world, tmp_path):
    '''The guide's TODO names "the first bullet below": the bullet after it
    is checkable again (the 2026-10-12 application run's L426).'''
    out = review(world, tmp_path, sids=('alpha.reference',))
    guide = (out / packets.GUIDE).read_text().split('\n')
    guide[17:20] = ['<!-- TODO(owner): decide the alpha stance -->', '- Set `ALPHA_ENV`.', '- Run alpha batches.']
    (out / packets.GUIDE).write_text('\n'.join(guide))
    first = 'L19 | Set ALPHA_ENV | STALE | tools.md:5 | "runs alpha batches" | Set ALPHA_ENV twice.'
    second = 'L20 | Run alpha batches | STALE | tools.md:5 | "runs alpha batches" | Run them twice.'
    result = settled(out, first, second)
    assert result.lines[2:6] == [
        'corrections, to apply to the guide in the working tree:',
        '  L20 alpha.reference STALE: Run alpha batches → Run them twice. (tools.md:5: "runs alpha batches")',
        "owner's call, never applied:",
        '  L19 alpha.reference STALE (next to a TODO(owner), report-only): Set ALPHA_ENV → Set ALPHA_ENV twice.']


@pytest.mark.parametrize('line', ['L99x | a claim | STALE | tools.md:5 | "runs" | x',
                                  # Review finding 11: past the guide's end is in no section.
                                  'L999 | an invented claim | WRONG | tools.md:5 | "runs alpha batches" | Else.'])
def test_an_unattributable_line_holds_every_section(world, tmp_path, line):
    out = review(world, tmp_path)
    result = settled(out, line, GOOD, 'alpha.reference | none')
    assert 'held, neither advanced nor audited: alpha.overview alpha.reference' in result.lines
    assert f'  unparseable: {line}' in result.lines


def test_a_doc_quote_counts_only_in_the_docs_or_the_packets_changelog(world, tmp_path):
    '''Review finding 1: the verifier's own report, the guide copy and the
    index are no docs. Only the head snapshot's pages and the packet's
    changelog.md are.'''
    out = review(world, tmp_path, sids=('alpha.overview',))
    rows = ['L14 | Alpha uses ALPHA_TOOL | STALE | report.md:1 | "Alpha uses ALPHA_TOOL" | Alpha batches.',
            'L14 | Alpha uses ALPHA_TOOL | WRONG | guide.md:14 | "Alpha uses `ALPHA_TOOL`" | Alpha batches.',
            'L14 | Alpha uses ALPHA_TOOL | PARTIAL | index.json:1 | "mode" | Alpha batches.']
    result = settled(out, *rows, 'L14 | ALPHA_ENV arrived | CONFIRMED | changelog.md:14 | "Added `ALPHA_ENV`" | -')
    assert [line for line in result.lines if line.startswith('  quote not found')] == [
        f'  quote not found, discarded: {r}' for r in rows]
    assert result.lines[1] == "report: 1 confirmed, 0 correction(s), 0 owner's call, 3 unverified"


def test_a_section_needs_a_surviving_row_or_a_none_line(world, tmp_path):
    '''Review finding 2: a section the report says nothing verifiable about
    was not reviewed, so it is held. `<section> | none` says it holds no
    checkable claim.'''
    out = review(world, tmp_path)
    left = settled(out, GOOD)
    assert 'left out (no surviving row, no none line), so held: alpha.reference' in left.lines
    assert not left.clean
    answered = settled(out, GOOD, 'alpha.reference | none')
    assert not any(line.startswith(('left out', 'held')) for line in answered.lines)
    assert answered.clean


@pytest.mark.parametrize('text', ['', 'No report could be produced.\n'])
def test_an_empty_or_prose_only_report_holds_every_section(world, tmp_path, text):
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = packets.audit(load(world), tmp_path / 'a', 'alpha')
    (out / packets.REPORT).write_text(text)
    result = settle.settle(out)
    assert 'left out (no surviving row, no none line), so held: alpha.overview alpha.reference' in result.lines
    assert not any(('audited' in line or 'rebaseline' in line) for line in result.lines if line.startswith('  '))
    assert not result.clean


def test_a_dash_is_no_proposed_wording(world, tmp_path):
    '''Review finding 9: `-` marks an empty field, so it proposes nothing.'''
    out = review(world, tmp_path, sids=('alpha.overview',))
    dash = 'L14 | Alpha uses ALPHA_TOOL | STALE | tools.md:5 | "runs alpha batches" | -'
    result = settled(out, dash)
    assert f'  no proposed wording, discarded: {dash}' in result.lines
    assert 'held, neither advanced nor audited: alpha.overview' in result.lines


def test_a_broken_b_or_c_row_is_unparseable_and_holds_nothing(world, tmp_path):
    '''Review finding 12.'''
    out = review(world, tmp_path)
    rows = ['B | 2.1.297', 'B | 2.1.901 | adds ALPHA_ENV | changelog', 'C | -',
            # Second review, finding 9: only a release label and a changelog.md line.
            'B | 2.1.901 | adds ALPHA_ENV | report.md:1', 'B | banana | adds ALPHA_ENV | changelog.md:14',
            'B | 2.1.901 | adds ALPHA_ENV | changelog.md:0']
    result = settled(out, GOOD, 'alpha.reference | none', *rows)
    assert [line for line in result.lines if line.startswith('  unparseable')] == [
        f'  unparseable: {r}' for r in rows]
    assert not any(line.startswith('held') for line in result.lines)
    assert not result.clean


def test_a_quote_a_row_need_not_give_is_still_checked_when_given(world, tmp_path):
    '''Review finding 13: JUDGMENT and NOT FOUND may leave their quote out,
    but a quote they give is re-grepped like any other.'''
    out = review(world, tmp_path)
    rows = ['L14 | prefer alpha | JUDGMENT | tools.md:5 | "does not exist" | -',
            'L19 | the tick span | NOT FOUND | tools.md:5 | "nor does this" | -']
    result = settled(out, GOOD, 'L19 | Set ALPHA_ENV | CONFIRMED | changelog.md:14 | "Added `ALPHA_ENV`" | -', *rows)
    assert [line for line in result.lines if line.startswith('  quote not found')] == [
        f'  quote not found, discarded: {r}' for r in rows]


def triage_file(tmp_path, **saved):
    write_tree(tmp_path / 't', {packets.SETTLED: json.dumps(
        {'mode': 'triage', 'advance_to': '2.1.902', 'verify': [], 'cleared': [], 'held': [], 'rows': {}} | saved)})
    return tmp_path / 't' / packets.SETTLED


def todo_guide(out, lines):
    guide = (out / packets.GUIDE).read_text().split('\n')
    guide[17:20] = lines
    (out / packets.GUIDE).write_text('\n'.join(guide))


def test_a_correction_left_for_the_owner_holds_its_section(world, tmp_path):
    '''Review finding 7: a correction next to a TODO(owner) is the owner's
    call, so it holds its section: no advance, and no rebaseline of a block
    it is a candidate of. One outside the packet's sections holds nothing
    (second review, finding 1): the packet neither reviews nor advances its
    section, so the block its triage cleared is rebaselined.'''
    saved = triage_file(tmp_path, verify=['alpha.reference'], cleared=['alpha.overview'])
    out = review(world, tmp_path, sids=('alpha.reference',), settled_triage=saved)
    todo_guide(out, ['<!-- TODO(owner): decide the alpha stance -->', '- Set `ALPHA_ENV`.', ''])
    near = 'L19 | Set ALPHA_ENV | STALE | tools.md:5 | "runs alpha batches" | Set ALPHA_ENV twice.'
    result = settled(out, near, GOOD)
    assert 'held, neither advanced nor audited: alpha.reference' in result.lines
    assert [line for line in result.lines if 'baseline' in line] == [
        f"  {CLI} baseline rebaseline alpha 'tools › Tools'", f'  {CLI} baseline stamp']


def test_a_correction_outside_the_packet_never_claims_a_hold_its_triage_already_advanced(world, tmp_path):
    '''Second review, finding 1: the triage's commands advanced the sections
    it cleared before this verify ran, so a correction in one of them is the
    owner's call with a verify of its own, never a hold.'''
    out = triage(world, tmp_path)
    settled(out, '2.1.901 | alpha.overview', '2.1.902 | none')
    v = review(world, tmp_path, sids=('alpha.overview',), settled_triage=out / packets.SETTLED)
    wrong = 'L19 | Set ALPHA_ENV | WRONG | tools.md:5 | "runs alpha batches" | Set it twice.'
    result = settled(v, 'L14 | Alpha uses ALPHA_TOOL | CONFIRMED | tools.md:5 | "runs alpha batches" | -', wrong)
    assert ("  L19 alpha.reference WRONG (outside this packet's sections, so it holds nothing; "
            '/cc-guide verify alpha.reference reviews it): Set ALPHA_ENV → Set it twice.') in result.lines
    assert not any(line.startswith('held') for line in result.lines)
    assert f'  {CLI} baseline advance alpha.overview --to 2.1.902' in result.lines
    assert result.clean


def test_a_todo_owner_reach_covers_its_first_items_continuation_lines(world, tmp_path):
    '''Review finding 8: a wrapped first item is in reach to its last line.'''
    out = review(world, tmp_path, sids=('alpha.reference',))
    todo_guide(out, ['<!-- TODO(owner): decide the alpha stance -->', '- Set `ALPHA_ENV`, which',
                     '  wraps onto a second line.', '- Run alpha batches.'])
    wrapped = 'L20 | ALPHA_ENV wraps | STALE | tools.md:5 | "runs alpha batches" | Set it once.'
    second = 'L21 | Run alpha batches | STALE | tools.md:5 | "runs alpha batches" | Run them twice.'
    result = settled(out, wrapped, second)
    assert result.lines[2:6] == [
        'corrections, to apply to the guide in the working tree:',
        '  L21 alpha.reference STALE: Run alpha batches → Run them twice. (tools.md:5: "runs alpha batches")',
        "owner's call, never applied:",
        '  L20 alpha.reference STALE (next to a TODO(owner), report-only): ALPHA_ENV wraps → Set it once.']


def test_a_fenced_example_never_ends_a_todo_reach(world, tmp_path):
    '''Second review, finding 7: a list-like line inside fenced code is no
    list item, so the reach runs on to the first real one.'''
    out = review(world, tmp_path, sids=('alpha.reference',))
    todo_guide(out, ['<!-- TODO(owner): decide the default in the first bullet -->', '```text',
                     '- illustrative syntax', '```', '', '- Alpha default is old.',
                     "  This continuation needs the owner's decision."])
    assert settle.todo_reaches((out / packets.GUIDE).read_text()) == [(18, 24)]
    row = 'L24 | the owner decides | STALE | tools.md:5 | "runs alpha batches" | Decide it.'
    result = settled(out, row)
    assert ('  L24 alpha.reference STALE (next to a TODO(owner), report-only): the owner decides → Decide it.'
            in result.lines)
    assert 'held, neither advanced nor audited: alpha.reference' in result.lines


def test_hold_settles_again_with_a_declined_correction_held_and_keeps_its_accept(world, tmp_path):
    '''A listed correction the session leaves for the owner: `--hold` prints
    the commands again with its section held. accept still lists it, for
    any other correction applied there.'''
    saved = triage_file(tmp_path, verify=['alpha.overview', 'alpha.reference'])
    out = review(world, tmp_path, settled_triage=saved)
    (out / packets.REPORT).write_text(f'{GOOD}\nalpha.reference | none\n')
    result = settle.settle(out, hold=['alpha.overview'])
    assert [line for line in result.lines if 'baseline' in line] == [
        f'  {CLI} baseline accept alpha.overview --substantive   # only the sections you changed',
        f'  {CLI} baseline advance alpha.reference --to 2.1.902', f'  {CLI} baseline stamp']
    assert 'held, neither advanced nor audited: alpha.overview' in result.lines
    assert result.clean
    with pytest.raises(state.SetupError) as err:
        settle.settle(out, hold=['beta.overview'])
    assert str(err.value) == '--hold beta.overview: not a section this packet reviews (alpha.overview, alpha.reference)'


def test_a_verify_packet_holds_what_its_triage_held(world, tmp_path):
    '''Review finding 6: settled.json's holds reach verify's bookkeeping.'''
    saved = triage_file(tmp_path, verify=['alpha.overview', 'alpha.reference'], held=['alpha.overview'])
    out = review(world, tmp_path, settled_triage=saved)
    result = settled(out, GOOD, 'alpha.reference | none')
    assert 'held, neither advanced nor audited: alpha.overview' in result.lines
    assert f'  {CLI} baseline advance alpha.reference --to 2.1.902' in result.lines
    assert not any('rebaseline' in line for line in result.lines)


def test_a_page_with_an_unresolved_changed_block_is_never_rebaselined(world, tmp_path):
    '''Second review, finding 5: baseline rebaselines a page's changed
    blocks together, so while one is held, settle lists none of that page's,
    and every command it does print, baseline runs.'''
    tools = DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches').replace(
        '| `--fast` | Runs fast. |', '| `--fast` | Runs fast with `ALPHA_ENV`. |')
    latest(world, {'tools.md': tools})
    w = load(world)
    out = packets.verify(w, tmp_path / 'v', ['alpha.overview', 'alpha.reference'], triage_file(tmp_path))[0]
    (out / packets.REPORT).write_text('L14 | Alpha uses ALPHA_TOOL | CONFIRMED | tools.md:5 | "runs alpha batches" | -'
                                      '\nalpha.reference | none\n')
    assert not any('rebaseline' in line for line in settle.settle(out, hold=['alpha.overview']).lines)
    whole = [line for line in settle.settle(out).lines if 'rebaseline' in line]
    assert whole == [f"  {CLI} baseline rebaseline alpha 'tools › Tools' 'tools › Tools › Options › `--fast`'"]
    refs = shlex.split(whole[0])[shlex.split(whole[0]).index('rebaseline') + 2:]
    new, _, _ = baseline.rebaseline(w.state, w.manifest, w.guide, 'alpha', refs, state.latest_docs(world[1]),
                                    '2.1.902')  # baseline refuses a page listed in part
    assert new != w.state


def test_verify_never_advances_a_section_past_its_triages_target_backwards(world, tmp_path):
    '''Second review, finding 6: a section checked past the triage's capped
    target is verified but not advanced.'''
    repo = world[0]
    baselined = state.parse_baseline((repo / state.BASELINE).read_text())
    baselined['sections']['alpha.overview']['checked'] = {'release': '2.1.902', 'date': '2026-10-04'}
    (repo / state.BASELINE).write_text(state.dump_baseline(baselined))
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = triage(world, tmp_path)
    settled(out, 'B1 | TOUCHES | alpha.overview | 14 | "Alpha uses `ALPHA_TOOL`" | "runs alpha batches" | moved',
            '2.1.902#2 | broken', '2.1.901 | none', '2.1.902 | none')
    v = packets.verify(load(world), tmp_path / 'v', [], out / packets.SETTLED)[0]
    result = settled(v, 'L14 | Alpha uses ALPHA_TOOL | CONFIRMED | tools.md:5 | "runs alpha batches" | -')
    assert not any(' advance ' in line for line in result.lines)
    assert f"  {CLI} baseline rebaseline alpha 'tools › Tools'" in result.lines


def test_an_audit_ends_with_audited_unless_a_section_is_held(world, tmp_path):
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = packets.audit(load(world), tmp_path / 'a', 'alpha')
    result = settled(out, 'L14 | Alpha uses ALPHA_TOOL | CONFIRMED | tools.md:5 | "runs alpha batches" | -',
                     'alpha.reference | none')
    assert result.lines[0] == f'cc-guide settle: audit alpha, {out}'
    assert [line for line in result.lines if 'baseline' in line][:2] == [
        f"  {CLI} baseline rebaseline alpha 'tools › Tools'", f'  {CLI} baseline audited alpha']
    held = settled(out, 'L14 | Alpha uses ALPHA_TOOL | PARTIAL | tools.md:5 | "absent" | Partly.')
    assert not any('audited' in line for line in held.lines if line.startswith('  '))


# ---- files -------------------------------------------------------------------

def test_a_files_report_lists_contradictions_and_cites_the_file(world, tmp_path):
    out = packets.files(load(world), tmp_path / 'f', [])[0]
    result = settled(out, settle.FILES_ROW,
                     'hooks/gate.sh:3 | exits 0 always | alpha.overview | "Alpha uses `ALPHA_TOOL`" | contradicts',
                     'hooks/gate.sh:1 | a shell script | alpha.overview | "## 1. Alpha" | consistent',
                     'hooks/gate.sh:2 | the launchd PATH | alpha.overview | - | not covered')
    assert result.lines == [
        f'cc-guide settle: files hooks/gate.sh, {out}',
        'report: 1 consistent, 1 contradiction(s), 1 not covered, 0 unverified',
        'contradictions, to fix in hooks/gate.sh in the working tree:',
        '  hooks/gate.sh:3 (alpha.overview): exits 0 always (guide: "Alpha uses `ALPHA_TOOL`")',
        "owner's call, never applied:",
        '  hooks/gate.sh:2 (alpha.overview, not covered; a coverage gap?): the launchd PATH',
        'unverified, discarded:',
        'then, in this order (R8.8), once every contradiction is fixed in hooks/gate.sh, unless '
        'build/cc_guide/conformance.toml records it as a deviation, which stays as it is; for one you leave for the '
        'owner, settle again with --hold hooks/gate.sh, which skips its cite:',
        f'  {CLI} baseline cite hooks/gate.sh', f'  {CLI} lint', f'  {CONFORMANCE}']
    assert result.clean


def test_a_statement_that_opens_with_a_quote_still_parses(world, tmp_path):
    out = packets.files(load(world), tmp_path / 'f', [])[0]
    result = settled(out, 'hooks/gate.sh:3 | "exit 0": it always succeeds | alpha.overview | "## 1. Alpha" | consistent')
    assert result.lines[1] == 'report: 1 consistent, 0 contradiction(s), 0 not covered, 0 unverified'
    assert result.clean


def test_a_discarded_contradiction_holds_the_file_uncited(world, tmp_path):
    out = packets.files(load(world), tmp_path / 'f', [])[0]
    result = settled(out, 'hooks/gate.sh:3 | exits 0 | alpha.overview | "not in the guide" | contradicts',
                     'other/file.sh:1 | x | alpha.overview | "## 1. Alpha" | consistent')
    assert ('held, not cited: hooks/gate.sh: a discarded or unparseable row might have changed it; '
            'a cited section was left out') in result.lines
    assert not any('cite' in line for line in result.lines if line.startswith('  '))
    assert '  unparseable: other/file.sh:1 | x | alpha.overview | "## 1. Alpha" | consistent' in result.lines


def test_a_files_row_on_a_section_the_file_does_not_cite_holds_it(world, tmp_path):
    '''Second review, finding 8: a files review covers the cited sections
    only, so a row naming another section does not parse.'''
    out = packets.files(load(world), tmp_path / 'f', [])[0]
    beta = 'hooks/gate.sh:1 | Beta contradicts | beta.reference | "`BetaEvent` fires." | contradicts'
    result = settled(out, 'alpha.overview | none', beta)
    assert f'  unparseable: {beta}' in result.lines
    assert 'held, not cited: hooks/gate.sh: a discarded or unparseable row might have changed it' in result.lines
    assert not any('cite' in line for line in result.lines if line.startswith('  '))


@pytest.mark.parametrize('rows', [(), ('No report could be produced.',)])
def test_a_cited_section_with_no_surviving_row_or_none_line_holds_the_file(world, tmp_path, rows):
    out = packets.files(load(world), tmp_path / 'f', [])[0]
    result = settled(out, *rows)
    assert 'left out (no surviving row, no none line): alpha.overview' in result.lines
    assert not any('cite' in line for line in result.lines if line.startswith('  '))
    assert not result.clean
    answered = settled(out, 'alpha.overview | none')
    assert f'  {CLI} baseline cite hooks/gate.sh' in answered.lines
    assert answered.clean


def test_a_not_covered_rows_quote_is_checked_when_given_and_hold_holds_the_file(world, tmp_path):
    out = packets.files(load(world), tmp_path / 'f', [])[0]
    bogus = 'hooks/gate.sh:2 | the launchd PATH | alpha.overview | "not in the guide" | not covered'
    result = settled(out, bogus, 'hooks/gate.sh:1 | a shell script | alpha.overview | "## 1. Alpha" | consistent')
    assert f'  quote not found, discarded: {bogus}' in result.lines
    assert f'  {CLI} baseline cite hooks/gate.sh' in result.lines
    held = settle.settle(out, hold=['hooks/gate.sh'])
    assert 'held, not cited: hooks/gate.sh: held by --hold' in held.lines
    assert [line for line in held.lines if line.startswith('  ')][-2:] == [f'  {CLI} lint', f'  {CONFORMANCE}']
    assert not any('cite' in line for line in held.lines if line.startswith('  '))
    with pytest.raises(state.SetupError) as err:
        settle.settle(out, hold=['alpha.overview'])
    assert str(err.value) == '--hold alpha.overview: a files packet holds only its file, hooks/gate.sh'


# ---- the CLI -----------------------------------------------------------------

def test_the_cli_exits_on_the_report_and_two_without_one(world, tmp_path, capsys):
    out = triage(world, tmp_path)
    assert cli.main(['settle', str(out)]) == 2
    assert capsys.readouterr() == ('', f"cc-guide: {out / 'report.md'}: not found; save the verifier's report as "
                                       'report.md in the packet\n')
    (out / packets.REPORT).write_text('2.1.901 | none\n2.1.902 | none\n')
    assert cli.main(['settle', str(out)]) == 0
    (out / packets.REPORT).write_text('2.1.901 | none\n')
    assert cli.main(['settle', str(out)]) == 1
    assert cli.main(['settle', str(tmp_path / 'nope')]) == 2
    capsys.readouterr()
    assert cli.main(['settle', str(out), '--hold', 'alpha.overview']) == 2
    assert capsys.readouterr() == ('', 'cc-guide: --hold goes with a verify, audit or files packet\n')


def test_a_packet_built_on_another_cache_names_it_in_every_command(world, tmp_path, docs_dir):
    '''CX-1 (Codex, final review): `--cache` is the root parser's option, so
    a packet records the cache it was built on, and every cli.py command
    settle prints names a cache other than the default before its
    subcommand. The default cache's commands, and a packet made before the
    key, name none.'''
    other = tmp_path / 'other'
    write_tree(state.snapshot_docs(other, FIXTURE_RELEASE), DOCS)
    prime_cache(other, docs_dir)
    write_tree(state.latest_docs(other), {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    out = packets.triage(packets.load(state.Source(world[0]), other, NOW), tmp_path / 'p', '2.1.901')
    index = json.loads((out / packets.INDEX).read_text())
    assert index['cache'] == str(other.resolve())
    rows = ('B1 | NOISE | - | - | - | "runs alpha batches" | a wording change', '2.1.901 | none')
    named = f'{CLI} --cache {shlex.quote(str(other.resolve()))}'
    assert settled(out, *rows).lines[2:] == [
        'then, in this order (R8.8):',
        f"  {named} baseline rebaseline alpha 'tools › Tools'",
        f'  {named} baseline advance alpha.overview alpha.reference beta.overview beta.reference --to 2.1.901',
        f'  {named} baseline stamp', f'  {named} lint', f'  {CONFORMANCE}',
        f'next range, once these commands are run: {named} packets --triage --through 2.1.902']
    words = shlex.split(settled(out, *rows).lines[4])
    args = cli.parser().parse_args(words[words.index('build/cc_guide/cli.py') + 1:])
    assert (args.cache, args.command, args.action, args.ids) == (
        other.resolve(), 'baseline', 'advance', ['alpha.overview', 'alpha.reference', 'beta.overview', 'beta.reference'])
    v = packets.verify(packets.load(state.Source(world[0]), other, NOW), tmp_path / 'v', ['alpha.overview'], None)[0]
    assert [line for line in settled(v, GOOD).lines if line.startswith('  ') and 'cli.py' in line] == [
        f'  {named} baseline accept alpha.overview --substantive   # only the sections you changed',
        f"  {named} baseline rebaseline alpha 'tools › Tools'", f'  {named} baseline stamp', f'  {named} lint']
    (out / packets.INDEX).write_text(json.dumps({key: value for key, value in index.items() if key != 'cache'}))
    assert not any('--cache' in line for line in settled(out, *rows).lines)
    latest(world, {'tools.md': DOCS['tools.md'].replace('runs alpha jobs', 'runs alpha batches')})
    default = packets.triage(load(world), tmp_path / 'd', '2.1.901')
    assert json.loads((default / packets.INDEX).read_text())['cache'] == str(state.default_cache().resolve())
    assert not any('--cache' in line for line in settled(default, *rows).lines)
