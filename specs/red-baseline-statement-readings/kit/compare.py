'''Compare the statements of the statement-readings probe (plan 83, spec Design 6, PD5).

Usage, from the repository root:
  uv run python <kit>/compare.py selftest
A statement is one <statement> block of <entry sentence="S<n>"> elements, each with <quote>, <subject>, <value>,
<unit>, <edge> and <default>. A reader adds <other_reading> (`none`, or its own four slots). The stand-in adds
<plan_lines>, <amended> (`none` or a task) and, when it notices a difference, <note>. Field text is HTML-unescaped.
The quote check keeps an entry whose flattened quote occurs in its flattened sentence, and returns the rest,
the planner's included: a returned entry is dropped and listed as a `returned` outcome (PD5).
Pairing (spec Design 6): entries pair by sentence number. When each list has at most one entry for a sentence,
those pair, whatever their subject. Otherwise they pair by subject key: the flattened subject with punctuation
at its ends and a leading article dropped. Entries with one key pair in their order. Then, a PD12 change from the
pilot: the rest pair where their slots match, and then by the most content words that their subjects share.
An unpaired entry is absent. Two units match when they are equal after normalization or share a content word
(another PD12 change), so `exit code` matches `exit status` while `characters` and `UTF-8 bytes` still differ.
Rules 1-5 run in reader_phase and rules 6-9 in resolve. A missing reader passes None, and each entry of the other
reader is then a lone entry (rule 3, or rule 4 when it names another reading). A lone entry that a planner entry
matches is no case: it joins the agreed readings, so that resolve pairs it with that planner entry.
Rule 9 is per sentence: a planner entry on the sentence that names an amendment skips the whole sentence.
A planner entry that pairs with no agreed reading on a sentence with agreed readings is `unchecked` (unpaired).
A case's `entries` holds its own entries and the arm's unpaired entries on its sentence; `asked` holds only its
own, the ones it rules on (a PD12 change: the pilot's cases on one sentence listed the same entries).
'''
import html
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from number import flatten  # noqa: E402

STATEMENT_RE = re.compile(r'<statement>(.*?)</statement>', re.S)
ENTRY_RE = re.compile(r'<entry\s+sentence="S?(\d+)"\s*>(.*?)</entry>', re.S)
OTHER_RE = re.compile(r'<other_reading>(.*?)</other_reading>', re.S)
RULINGS_RE = re.compile(r'<rulings>(.*?)</rulings>', re.S)
RULING_RE = re.compile(r'<ruling\b([^>]*)>(.*?)</ruling>', re.S)
ATTR_RE = re.compile(r'(\w+)="([^"]*)"')
SLOT_NAMES = ('value', 'unit', 'edge', 'default')
NONE_FORMS = ('', 'none', 'n/a', '-')
VERDICTS = ('reading', 'no-value', 'unclear')
ARTICLES = ('the ', 'a ', 'an ')
STOPWORDS = {'the', 'a', 'an', 'of', 'on', 'in', 'at', 'to', 'for', 'and', 'or', 'by', 'with', 'from',
             'as', 'is', 'are', 'be', 'its', 'it', 'that', 'this', 'each', 'every', 'per'}
RETURNED_RE = re.compile(r'^(claude|codex|planner)#(\d+):')


@dataclass(frozen=True)
class Slots:
    value: str
    unit: str
    edge: str
    default: str


@dataclass(frozen=True)
class Entry:
    sentence: int
    quote: str
    subject: str
    slots: Slots
    other: Slots | None
    plan_lines: str
    amended: str
    note: str


@dataclass(frozen=True)
class Case:
    id: str
    rule: int
    sentence: int
    subject: str
    entries: dict[str, list[Entry]]
    asked: dict[str, list[Entry]] = field(default_factory=dict)


@dataclass(frozen=True)
class Reading:
    sentence: int
    subject: str
    slots: Slots


@dataclass(frozen=True)
class Outcome:
    kind: str
    sentence: int
    subject: str
    agreed: Slots | None
    planner: Slots | None
    detail: str


@dataclass(frozen=True)
class Phase:
    cases: list[Case]
    agreed: list[Reading]
    outcomes: list[Outcome]


@dataclass(frozen=True)
class Ruling:
    case: str
    verdict: str
    quote: str
    slots: Slots | None


def _field(body: str, name: str) -> str:
    match = re.search(rf'<{name}>(.*?)</{name}>', body, re.S)
    return html.unescape(match.group(1).strip()) if match else ''


def _slots(body: str) -> Slots:
    return Slots(*(_field(body, name) for name in SLOT_NAMES))


def parse_statement(text: str) -> list[Entry] | None:
    '''The entries of the text's <statement> block, or None (VOID) when the text has no complete block.'''
    block = STATEMENT_RE.search(text or '')
    if not block:
        return None
    entries = []
    for number_, body in ENTRY_RE.findall(block.group(1)):
        other_block = OTHER_RE.search(body)
        main = OTHER_RE.sub('', body)
        other = None
        if other_block and any(f'<{name}>' in other_block.group(1) for name in SLOT_NAMES):
            other = _slots(other_block.group(1))
            if all(normalize_slot(s) == 'none' for s in (other.value, other.unit, other.edge, other.default)):
                other = None
        entries.append(Entry(int(number_), _field(main, 'quote'), _field(main, 'subject'), _slots(main), other,
                             _field(main, 'plan_lines'), _field(main, 'amended'), _field(main, 'note')))
    return entries


def normalize_slot(text: str) -> str:
    '''PD5: flatten, drop a trailing period, read the empty forms as `none`, drop thousands commas, read number
    ranges as a-b, read parentheses around a list as brackets, drop list spacing, and read a one-item list as
    its item.'''
    t = flatten(html.unescape(text or '')).rstrip('.').strip()
    if t in NONE_FORMS:
        return 'none'
    t = re.sub(r'(?<=\d),(?=\d{3}(?!\d))', '', t)
    t = re.sub(r'(\d)\s+to\s+(\d)', r'\1-\2', t)
    t = re.sub(r'(\d)\s*-\s*(\d)', r'\1-\2', t)
    if t.startswith('(') and t.endswith(')') and ',' in t:
        t = f'[{t[1:-1]}]'
    if t.startswith('[') and t.endswith(']'):
        items = [item.strip() for item in t[1:-1].split(',')]
        if items and not items[-1]:
            items.pop()
        if len(items) == 1:
            return items[0]
        t = '[' + ','.join(items) + ']'
    return t


def _unit_match(a: str, b: str) -> bool:
    '''Units are equal after normalize_slot, or both name a unit and share a content word, a final `s` dropped
    (a PD12 change from the pilot: `exit code` and `exit status`).'''
    a, b = normalize_slot(a), normalize_slot(b)
    if a == b:
        return True
    if 'none' in (a, b):
        return False
    stems = [{w.removesuffix('s') for w in _words(u)} - {''} for u in (a, b)]
    return bool(stems[0] & stems[1])


def match(a: Slots, b: Slots) -> bool:
    '''The value, edge and default slots are equal after normalize_slot, and the units match (_unit_match).'''
    return (all(normalize_slot(x) == normalize_slot(y) for x, y in zip((a.value, a.edge, a.default),
                                                                      (b.value, b.edge, b.default)))
            and _unit_match(a.unit, b.unit))


def _quote_reason(entry: Entry, sentences: dict[int, str]) -> str:
    if entry.sentence not in sentences:
        return f'no sentence S{entry.sentence}'
    quote = flatten(entry.quote)
    if not quote or quote not in flatten(sentences[entry.sentence]):
        return f'quote not in S{entry.sentence}'
    return ''


def check_quotes(entries: list[Entry], sentences: dict[int, str]) -> tuple[list[Entry], list[Entry]]:
    '''The kept entries and the returned ones: an entry is returned when its sentence does not exist or its
    quote is not in its sentence.'''
    kept, returned = [], []
    for entry in entries:
        (returned if _quote_reason(entry, sentences) else kept).append(entry)
    return kept, returned


def _subject_key(subject: str) -> str:
    key = re.sub(r'^[^\w\[(]+|[^\w\])]+$', '', flatten(subject))
    for article in ARTICLES:
        if key.startswith(article):
            key = key[len(article):]
    return key


def _words(subject: str) -> set[str]:
    words = {w.strip('.-/') for w in re.split(r'[^\w.\-/]+', flatten(subject))}
    return {w for w in words if w and w not in STOPWORDS}


def _pair(lists: list[list]) -> list[tuple]:
    '''Group one sentence's entries across lists (spec Design 6). Each item of `lists` holds entries or
    readings with a `subject` and `slots`. A group holds one item or None from each list. When each list has
    at most one item, they pair. Otherwise two lists pair, in this order: by subject key; then, among the
    rest, items whose slots match; then the rest by the most content words that their subjects share, at least
    one (the PD12 change, from the pilot's p66-bound S110). An item left over is alone in its group.'''
    if all(len(items) <= 1 for items in lists):
        group = tuple(items[0] if items else None for items in lists)
        return [group] if any(x is not None for x in group) else []
    if len(lists) == 1:
        return [(item,) for item in lists[0]]
    left, right = lists
    pairs, used_l, used_r = [], set(), set()

    def take(i: int, j: int) -> None:
        pairs.append((i, j))
        used_l.add(i)
        used_r.add(j)

    for i, a in enumerate(left):
        j = next((j for j, b in enumerate(right) if j not in used_r
                  and _subject_key(b.subject) == _subject_key(a.subject)), None)
        if j is not None:
            take(i, j)
    for i, a in enumerate(left):
        if i in used_l:
            continue
        j = next((j for j, b in enumerate(right) if j not in used_r and match(a.slots, b.slots)), None)
        if j is not None:
            take(i, j)
    shared = sorted((-len(_words(a.subject) & _words(b.subject)), i, j)
                    for i, a in enumerate(left) if i not in used_l
                    for j, b in enumerate(right) if j not in used_r and _words(a.subject) & _words(b.subject))
    for _count, i, j in shared:
        if i not in used_l and j not in used_r:
            take(i, j)
    groups = [(left[i], right[j]) for i, j in sorted(pairs)]
    groups += [(a, None) for i, a in enumerate(left) if i not in used_l]
    groups += [(None, b) for j, b in enumerate(right) if j not in used_r]
    return groups


def _by_sentence(entries) -> dict[int, list]:
    out: dict[int, list] = {}
    for entry in entries:
        out.setdefault(entry.sentence, []).append(entry)
    return out


def _returned(writer: str, entries: list[Entry], sentences: dict[int, str]) -> list[Outcome]:
    return [Outcome('returned', e.sentence, e.subject, None, e.slots if writer == 'planner' else None,
                    f'{writer}#{i}: {_quote_reason(e, sentences)}')
            for i, e in enumerate(entries) if _quote_reason(e, sentences)]


def _planner_detail(p: Entry) -> str:
    detail = f'planner lines {p.plan_lines or "-"}'
    return detail + (f'; note: {p.note}' if p.note else '')


def reader_phase(sentences: dict[int, str], claude: list[Entry] | None, codex: list[Entry] | None,
                 planner: list[Entry]) -> Phase:
    '''The quote checks, the pairing of spec Design 6 and comparison rules 1-5.'''
    readers = {name: stated for name, stated in (('claude', claude), ('codex', codex)) if stated is not None}
    outcomes = []
    kept = {}
    for name, stated in readers.items():
        kept[name] = check_quotes(stated, sentences)[0]
        outcomes += _returned(name, stated, sentences)
    p_kept = check_quotes(planner, sentences)[0]
    outcomes += _returned('planner', planner, sentences)
    names = list(readers)
    by = {name: _by_sentence(kept[name]) for name in names}
    p_by = _by_sentence(p_kept)
    found, agreed = [], []
    for n in sorted(set().union(*(by[name] for name in names), p_by)):
        listed = {name: by[name].get(n, []) for name in names}
        if not any(listed.values()):
            outcomes += [Outcome('unchecked', n, p.subject, None, p.slots, _planner_detail(p)) for p in p_by[n]]
            continue
        groups = _pair([listed[name] for name in names])
        paired = {id(x) for group in groups if sum(x is not None for x in group) > 1 for x in group if x}
        unpaired = {name: [e for e in listed[name] if id(e) not in paired] for name in names}
        for group in groups:
            present = [x for x in group if x is not None]
            subject = present[0].subject
            if len(present) == 2:
                a, b = present
                if not match(a.slots, b.slots):
                    rule = 2
                elif a.other is None and b.other is None:
                    agreed.append(Reading(n, subject, a.slots))
                    continue
                else:
                    rule = 4
            else:
                lone = present[0]
                if lone.other is not None:
                    rule = 4
                else:
                    partner = _pair([[lone], p_by.get(n, [])])
                    p = next((g[1] for g in partner if g[0] is lone), None)
                    if p is not None and match(lone.slots, p.slots):
                        agreed.append(Reading(n, subject, lone.slots))
                        continue
                    rule = 3
            members = {id(x) for x in present}
            entries = {name: [e for e in listed[name] if id(e) in members or e in unpaired[name]]
                       for name in names}
            asked = {name: [e for e in listed[name] if id(e) in members] for name in names}
            found.append((n, rule, subject, entries, asked))
    cases = [Case(f'C{i}', rule, n, subject, entries, asked)
             for i, (n, rule, subject, entries, asked) in enumerate(found, 1)]
    return Phase(cases, agreed, outcomes)


def parse_rulings(text: str, cases: list[Case]) -> list[Ruling] | None:
    '''The rulings, or None (VOID) when the text has no complete <rulings> block, a case has no ruling, or a
    ruling names no case.'''
    block = RULINGS_RE.search(text or '')
    if not block:
        return None
    ids = {c.id for c in cases}
    rulings = []
    for attrs, body in RULING_RE.findall(block.group(1)):
        attr = dict(ATTR_RE.findall(attrs))
        case, verdict = attr.get('case', ''), attr.get('verdict', '').strip().lower().replace(' ', '-')
        if case not in ids or verdict not in VERDICTS:
            return None
        rulings.append(Ruling(case, verdict, _field(body, 'quote'), _slots(body) if verdict == 'reading' else None))
    if {r.case for r in rulings} != ids or len(rulings) != len(ids):
        return None
    return rulings


def resolve(phase: Phase, rulings: list[Ruling], planner: list[Entry]) -> list[Outcome]:
    '''Comparison rules 6-9 on each agreed reading, rule 1's and each `reading` ruling's, plus a `no-value` or
    `unclear` outcome for each such ruling. The Phase's own outcomes are kept.'''
    dropped = {int(m.group(2)) for o in phase.outcomes if o.kind == 'returned'
               for m in [RETURNED_RE.match(o.detail)] if m and m.group(1) == 'planner'}
    p_by = _by_sentence([p for i, p in enumerate(planner) if i not in dropped])
    cases = {c.id: c for c in phase.cases}
    readings = list(phase.agreed)
    outcomes = list(phase.outcomes)
    for ruling in rulings:
        case = cases[ruling.case]
        if ruling.verdict == 'reading':
            readings.append(Reading(case.sentence, case.subject, ruling.slots))
            continue
        ps = p_by.get(case.sentence, [])
        outcomes.append(Outcome(ruling.verdict, case.sentence, case.subject, None,
                                ps[0].slots if len(ps) == 1 else None,
                                f'{case.id} rule {case.rule}; quote: {ruling.quote}'))
    for n, on_sentence in sorted(_by_sentence(readings).items()):
        ps = p_by.get(n, [])
        marked = [p for p in ps if normalize_slot(p.amended) != 'none']
        if marked:
            outcomes.append(Outcome('amended-skip', n, on_sentence[0].subject, on_sentence[0].slots, marked[0].slots,
                                    f'amended: {marked[0].amended}'))
            continue
        for r, p in _pair([on_sentence, ps]):
            if r is None:
                outcomes.append(Outcome('unchecked', n, p.subject, None, p.slots, 'unpaired; ' + _planner_detail(p)))
            elif p is None:
                outcomes.append(Outcome('missing', n, r.subject, r.slots, None, ''))
            elif not match(r.slots, p.slots):
                outcomes.append(Outcome('plan-conflict', n, r.subject, r.slots, p.slots, _planner_detail(p)))
    return outcomes


def _slots_from(d: dict | None) -> Slots | None:
    return None if d is None else Slots(**d)


def _entry_from(d: dict) -> Entry:
    return Entry(**{**d, 'slots': Slots(**d['slots']), 'other': _slots_from(d['other'])})


def phase_to_json(phase: Phase) -> str:
    return json.dumps(asdict(phase), indent=1, ensure_ascii=False)


def phase_from_json(text: str) -> Phase:
    d = json.loads(text)
    cases = [Case(c['id'], c['rule'], c['sentence'], c['subject'],
                  {name: [_entry_from(e) for e in es] for name, es in c['entries'].items()},
                  {name: [_entry_from(e) for e in es] for name, es in c.get('asked', {}).items()})
             for c in d['cases']]
    agreed = [Reading(r['sentence'], r['subject'], Slots(**r['slots'])) for r in d['agreed']]
    return Phase(cases, agreed, outcomes_from_json(json.dumps(d['outcomes'])))


def outcomes_to_json(outcomes: list[Outcome]) -> str:
    return json.dumps([asdict(o) for o in outcomes], indent=1, ensure_ascii=False)


def outcomes_from_json(text: str) -> list[Outcome]:
    return [Outcome(**{**o, 'agreed': _slots_from(o['agreed']), 'planner': _slots_from(o['planner'])})
            for o in json.loads(text)]



def _entry(n: int, value: str, quote: str = '', other: str = '', plan_lines: str = '', amended: str = '',
           subject: str = '') -> str:
    quote = quote or f'the value of key{n} is x'
    subject = subject or f'key{n}'
    other_xml = ''
    if other == 'none':
        other_xml = '<other_reading>none</other_reading>'
    elif other:
        other_xml = (f'<other_reading><value>{other}</value><unit>none</unit><edge>n/a</edge>'
                     '<default>none</default></other_reading>')
    planner_xml = ''
    if plan_lines:
        planner_xml = f'<plan_lines>{plan_lines}</plan_lines><amended>{amended or "none"}</amended>'
    return (f'<entry sentence="S{n}"><quote>{quote}</quote><subject>{subject}</subject><value>{value}</value>'
            f'<unit>none</unit><edge>n/a</edge><default>none</default>{other_xml}{planner_xml}</entry>')


SENTENCES = {n: f'R{n}. The value of `key{n}` is x.' for n in range(1, 11)}
READER_A = '<statement>\n' + '\n'.join(
    [_entry(n, 'x', other='none') for n in (1, 2, 3, 4, 5, 6, 8, 10)]
    + [_entry(9, 'x', quote='a quote that the sentence lacks', other='none')]) + '\n</statement>'
READER_B = '<statement>\n' + '\n'.join(
    [_entry(n, v, other='none') for n, v in ((1, 'x'), (2, 'x'), (3, 'x'), (4, 'y'), (5, 'y'), (6, 'x'))]
    + [_entry(10, 'x', other='y')]) + '\n</statement>'
PLANNER = '<statement>\n' + '\n'.join(
    [_entry(n, v, plan_lines=f'{n * 10}') for n, v in ((1, 'x'), (2, 'y'), (4, 'x'), (5, 'z'), (7, 'x'), (8, 'y'),
                                                        (10, 'x'))]
    + [_entry(6, 'y', plan_lines='60', amended='Task 1')]) + '\n</statement>'
RULINGS = '''<rulings>
<ruling case="C1" verdict="reading"><quote>The value of `key4` is x</quote><value>x</value><unit>none</unit><edge>n/a</edge><default>none</default></ruling>
<ruling case="C2" verdict="unclear"><quote></quote></ruling>
<ruling case="C3" verdict="no-value"><quote>R8.</quote></ruling>
<ruling case="C4" verdict="reading"><quote>is x</quote><value>x</value><unit>none</unit><edge>n/a</edge><default>none</default></ruling>
</rulings>'''


def selftest() -> None:
    A, B, P = (parse_statement(t) for t in (READER_A, READER_B, PLANNER))
    assert parse_statement(READER_A.replace('</statement>', '')) is None          # cut off: VOID
    assert normalize_slot("('3.12',)") == normalize_slot("['3.12']") == normalize_slot('3.12') == '3.12'
    assert normalize_slot('1,000') == '1000' and normalize_slot('N/A') == normalize_slot('') == 'none'
    assert normalize_slot('1–500') == normalize_slot('1 to 500') == '1-500'
    phase = reader_phase(SENTENCES, A, B, P)
    assert sorted((c.sentence, c.rule) for c in phase.cases) == [(4, 2), (5, 2), (8, 3), (10, 4)], phase.cases
    assert all(set(c.entries) <= {'claude', 'codex'} for c in phase.cases)        # no stand-in entry (D10)
    asked = {c.sentence: sum(map(len, c.asked.values())) for c in phase.cases}      # the entries each case rules on
    assert asked == {4: 2, 5: 2, 8: 1, 10: 2}, asked
    assert parse_rulings('<rulings></rulings>', phase.cases) is None               # a case without a ruling
    out = resolve(phase, parse_rulings(RULINGS, phase.cases), P)
    assert sorted((o.sentence, o.kind) for o in out) == [(2, 'plan-conflict'), (3, 'missing'), (5, 'unclear'),
        (6, 'amended-skip'), (7, 'unchecked'), (8, 'no-value'), (9, 'returned')], sorted((o.sentence, o.kind) for o in out)
    alone = reader_phase(SENTENCES, A, None, P)                                     # Claude alone
    assert sorted(c.sentence for c in alone.cases) == [2, 3, 5, 6, 8], alone.cases
    assert all(set(c.entries) == {'claude'} for c in alone.cases)
    assert phase_from_json(phase_to_json(phase)) == phase and outcomes_from_json(outcomes_to_json(out)) == out
    # Beyond the plan's fixture: a sentence with two values pairs its entries by subject (spec Design 6), and a
    # planner entry that fails the quote check is dropped and listed, never compared.
    two = {1: 'The floor is 3, and the cap is 7.', 2: 'Names contain no `<` or `>`.'}
    a = parse_statement('<statement>' + _entry(1, '3', quote='the floor is 3', subject='floor', other='none')
                        + _entry(1, '7', quote='the cap is 7', subject='the cap', other='none')
                        + _entry(2, '[<, >]', quote='no &lt; or &gt;', subject='Names', other='none') + '</statement>')
    b = parse_statement('<statement>' + _entry(1, '7', quote='the cap is 7', subject='cap', other='none')
                        + _entry(1, '3', quote='The floor is 3', subject='floor', other='none') + '</statement>')
    p = parse_statement('<statement>' + _entry(1, '3', quote='floor is 3', subject='floor', plan_lines='12')
                        + _entry(1, '8', quote='cap is 7', subject='cap', plan_lines='13')
                        + _entry(3, '9', quote='a sentence that does not exist', plan_lines='14') + '</statement>')
    assert len(check_quotes(a, two)[0]) == 3                                       # entities unescaped
    phase = reader_phase(two, a, b, p)
    assert [(c.sentence, c.rule) for c in phase.cases] == [(2, 3)], phase.cases
    out = resolve(phase, [Ruling('C1', 'reading', 'no `<` or `>`', Slots('[<, >]', 'none', 'n/a', 'none'))], p)
    assert sorted((o.sentence, o.kind, o.subject) for o in out) == [
        (1, 'plan-conflict', 'the cap'), (2, 'missing', 'Names'), (3, 'returned', 'key3')], out
    # The pilot's p66-bound S110 (PD12): one reader entry, two planner entries, no subject alike. The reading
    # pairs with the planner entry whose subject shares a word; slots that match pair before any word count.
    row = {1: '| `uv.toml` (repo root) | `exclude-newer` set to 00:00:00Z on the day after the freeze date | '
              'Files uploaded on the freeze date itself (UTC) are included |'}
    r = parse_statement('<statement>' + _entry(1, 'day after', quote='on the day after the freeze date',
                                                subject='`uv.toml` (repo root)', other='none') + '</statement>')
    p = parse_statement('<statement>' + _entry(1, 'on the freeze date', quote='`exclude-newer` set to 00:00:00Z',
                                                subject='`uv.toml` `exclude-newer`', plan_lines='106')
                        + _entry(1, 'excluded', quote='Files uploaded on the freeze date',
                                 subject='Files uploaded on the freeze date', plan_lines='107') + '</statement>')
    phase = reader_phase(row, r, None, p)
    assert [(c.sentence, c.rule) for c in phase.cases] == [(1, 3)], phase.cases
    out = resolve(phase, [Ruling('C1', 'reading', 'on the day after the freeze date',
                                 Slots('day after', 'none', 'n/a', 'none'))], p)
    assert sorted((o.kind, o.subject) for o in out) == [
        ('plan-conflict', '`uv.toml` (repo root)'), ('unchecked', 'Files uploaded on the freeze date')], out
    # The pilot's p66-bound S148, S150 and S176 (PD12): units that share a content word match. The unit plant
    # (characters against UTF-8 bytes) and a unit against none still differ.
    assert match(Slots('2', 'exit code', 'n/a', 'none'), Slots('2', 'exit status', 'n/a', 'none'))
    assert match(Slots('10', 'commit lint position', 'n/a', 'none'), Slots('10', 'commit lints', 'n/a', 'none'))
    assert not match(Slots('500', 'characters', 'in', 'none'), Slots('500', 'UTF-8 bytes', 'in', 'none'))
    assert not match(Slots('5', 'none', 'n/a', 'none'), Slots('5', 'days', 'n/a', 'none'))
    same = parse_statement('<statement>' + _entry(1, 'excluded', quote='Files uploaded on the freeze date',
                                                   subject='uploads', other='none') + '</statement>')
    assert resolve(reader_phase(row, same, None, p), [], p) == [
        Outcome('unchecked', 1, '`uv.toml` `exclude-newer`', None, p[0].slots, 'unpaired; planner lines 106')]
    # Two lone entries on one sentence are two cases. Each lists both entries and asks about its own: the pilot's
    # pair-arm cases C53-C55 on p66-bound S110 listed the same three entries, with nothing to tell them apart (PD12).
    duo = parse_statement('<statement>' + _entry(1, '3', quote='the floor is 3', subject='floor', other='none')
                          + _entry(1, '7', quote='the cap is 7', subject='cap', other='none') + '</statement>')
    split = reader_phase(two, duo, None, [])
    assert [[e.subject for e in c.entries['claude']] for c in split.cases] == [['floor', 'cap'], ['floor', 'cap']]
    assert [[e.subject for e in c.asked['claude']] for c in split.cases] == [['floor'], ['cap']], split.cases
    assert phase_from_json(phase_to_json(split)) == split
    print('compare selftest ok')


if __name__ == '__main__':
    if sys.argv[1:] == ['selftest']:
        selftest()
    else:
        sys.exit(__doc__)
