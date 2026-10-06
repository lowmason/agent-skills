'''`baseline`: the only writer of baseline.json and of the guide's stamp
region (drift spec R7). These functions return new state; cli.py writes it
to the working tree, and nothing is committed. `cite` is Stage 2's.'''
import copy
from pathlib import Path

from blocks import SEP, block_hash, key_hash, key_names, page_blocks, select
from docs import is_platform, page_file, parse_llms, version_key
from guide import anchor_problems, render_stamp, sections, text_hash, with_stamp
from state import Manifest, SetupError, Snapshot, block_namer, group_terms, no_snapshot

# R11.1: the July guide (verified at 2.1.219) and the refresh (at 2.1.288),
# both read at the guide's path before 79ad04f moved it.
OLD_GUIDE_PATH = 'specs/claude-code-customization-guide.md'
JULY = ('91474f6', '2.1.219')
REFRESH = ('c33bc99', '2.1.288')


def next_changed(newest: str, citer_stamps) -> str:
    '''R2.4: the newest known release, unless that would not exceed the
    highest review stamp among the section's citers; then that stamp with a
    fourth component added or incremented.'''
    top = max(citer_stamps, key=version_key, default=None)
    if top is None or version_key(newest) > version_key(top):
        return newest
    parts = top.split('.')
    if len(parts) == 3:
        return top + '.1'
    return '.'.join(parts[:3] + [str(int(parts[3]) + 1)])


def derive_changed(july: str, refresh: str, current: str) -> dict[str, str]:
    '''R11.1: each section's `changed`. A section whose text is the same in
    the July guide and the refresh, aligned by (parent ##, heading) and
    compared with whitespace collapsed, keeps July's release; every other
    section takes the refresh's.'''
    def by_key(text: str) -> dict:
        return {(s.parent, s.heading): ' '.join(s.text.split()) for s in sections(text)}
    old, new = by_key(july), by_key(refresh)
    out = {}
    for s in sections(current):
        key = (s.parent, s.heading)
        if key not in new:
            raise SetupError(f'R11.1: section {s.id} ({s.heading!r}) is not in the {REFRESH[0]} guide')
        out[s.id] = JULY[1] if old.get(key) == new[key] else REFRESH[1]
    return out


def check_ids(manifest: Manifest, guide_text: str) -> None:
    '''init and rebaseline need a guide whose anchors match the manifest.'''
    problems = anchor_problems(guide_text)
    anchors = {s.id for s in sections(guide_text) if s.id}
    problems += [f'section {sid} is in manifest.toml but not the guide'
                 for sid in sorted(set(manifest.group_of()) - anchors)]
    problems += [f'section {sid} is in the guide but not manifest.toml'
                 for sid in sorted(anchors - set(manifest.group_of()))]
    if problems:
        raise SetupError('\n'.join(problems))


def select_blocks(text: str, mark: str, terms: set[str]) -> dict[str, str]:
    '''One page's selected blocks as baseline.json stores them, key hash ->
    block hash, in page order (R2.3).'''
    found = page_blocks(text)
    return {key_hash(k): block_hash(found[k]) for k in select(found, mark, terms)}


def init(manifest: Manifest, guide_text: str, docs: Path, release: str, day: str,
         changed: dict[str, str]) -> dict:
    '''R2.6: the initial baseline, from a snapshot directory and never from
    live docs. A mapped page the snapshot lacks stays unbaselined, so its
    selected blocks report as new.'''
    check_ids(manifest, guide_text)
    terms = group_terms(manifest, guide_text)
    llms = docs / 'llms.txt'
    state: dict = {'sections': {}, 'groups': {},
                   'llms': sorted(parse_llms(llms.read_text(encoding='utf-8'))) if llms.is_file() else []}
    for s in sections(guide_text):
        state['sections'][s.id] = {'checked': {'release': release, 'date': day},
                                   'changed': changed[s.id],
                                   'audited': {'release': release, 'date': day},
                                   'text_hash': text_hash(s.text)}
    for gid, group in manifest.groups.items():
        watched = set().union(*terms[gid].values())
        blocks, snapshot = {}, {}
        for page, mark in group.pages.items():
            path = docs / page_file(page)
            if path.is_file():
                blocks[page] = select_blocks(path.read_text(encoding='utf-8'), mark, watched)
                snapshot[page] = release
        state['groups'][gid] = {'blocks': blocks, 'snapshot': snapshot}
    return state


def known(state: dict, ids) -> None:
    unknown = [sid for sid in ids if sid not in state['sections']]
    if unknown:
        raise SetupError(f'unknown section IDs: {", ".join(unknown)}')


def accept(state: dict, guide_text: str, ids, substantive: bool, newest: str | None,
           citer_stamps: dict[str, list[str]] | None = None) -> dict:
    '''R7 accept: record each section's current text_hash. Substantive also
    sets a new `changed` (R2.4), which flags the section's citers; only it
    reads `newest`, which an editorial accept may leave None. Stage 1 has
    no citations, so cli.py passes none; Stage 2 passes the index's stamps.'''
    known(state, ids)
    by_id = {s.id: s for s in sections(guide_text)}
    new = copy.deepcopy(state)
    for sid in ids:
        new['sections'][sid]['text_hash'] = text_hash(by_id[sid].text)
        if substantive:
            new['sections'][sid]['changed'] = next_changed(newest, (citer_stamps or {}).get(sid, []))
    return new


def advance(state: dict, ids, to: str, labels: set[str], day: str) -> dict:
    '''R7 advance: set `checked` to a changelog release, dated the day of the
    check. It never moves a section backwards.'''
    known(state, ids)
    if to not in labels:
        raise SetupError(f'{to} is not a release in the newest cached changelog')
    behind = [sid for sid in ids if version_key(to) < version_key(state['sections'][sid]['checked']['release'])]
    if behind:
        raise SetupError(f'{to} is older than the checked release of {", ".join(behind)}')
    new = copy.deepcopy(state)
    for sid in ids:
        new['sections'][sid]['checked'] = {'release': to, 'date': day}
    return new


def audited(state: dict, manifest: Manifest, group: str, release: str, day: str) -> dict:
    '''R7 audited: set `audited` for the group's sections to the current
    release and day, and advance their `checked` to it.'''
    if group not in manifest.groups:
        raise SetupError(f'unknown group {group}')
    known(state, manifest.groups[group].sections)
    new = copy.deepcopy(state)
    for sid in manifest.groups[group].sections:
        new['sections'][sid]['audited'] = {'release': release, 'date': day}
        new['sections'][sid]['checked'] = {'release': release, 'date': day}
    return new


def rebaseline(state: dict, manifest: Manifest, guide_text: str, group: str, refs: list[str],
               latest: Path, release: str, snapshot: Snapshot = no_snapshot) -> tuple[dict, list[str], list[str]]:
    '''R7 rebaseline: re-hash the group's selected blocks from latest/, all of
    them or the listed refs: `<page>`, or `<page> › <key>` as check prints a
    block, a key hash for a block check could not name. A listed key that is
    no longer selected leaves the baseline. A listed run refuses when an
    unlisted baselined block on the page changed too, since the page's
    snapshot would then not hold its baselined text; the refusal names a gone
    block from `snapshot`, as check does. Returns the new state, the pages to
    snapshot to <release>/docs, and notes.

    A missing page keeps its entries: it needs a manifest edit, not a
    rebaseline. A full run also drops the pages the group no longer maps.
    Every run refreshes the llms.txt slug list.'''
    if group not in manifest.groups:
        raise SetupError(f'unknown group {group}')
    check_ids(manifest, guide_text)
    llms_path = latest / 'llms.txt'
    if not llms_path.is_file():
        raise SetupError(f'{llms_path}: no latest fetch; run check first')
    slugs = parse_llms(llms_path.read_text(encoding='utf-8'))
    mapped = manifest.groups[group].pages
    watched = set().union(*group_terms(manifest, guide_text)[group].values())
    stored = state['groups'].get(group, {}).get('blocks', {})
    targets: dict[str, set[str] | None] = {}
    for ref in refs or list(mapped):
        page, _, key = ref.partition(SEP)
        if not key:
            targets[page] = None
        elif targets.get(page, set()) is not None:
            targets.setdefault(page, set()).add(key if key in stored.get(page, {}) else key_hash(key))
    name = block_namer(state, group, snapshot)
    new = copy.deepcopy(state)
    g = new['groups'].setdefault(group, {'blocks': {}, 'snapshot': {}})
    snap, notes = [], []
    for page, keys in targets.items():
        if page not in mapped:
            if page not in g['blocks']:
                raise SetupError(f'{page} is neither mapped to nor baselined in {group}')
            if keys is None:
                g['blocks'].pop(page)
                g['snapshot'].pop(page, None)
            else:
                for key in keys:
                    g['blocks'][page].pop(key, None)
            notes.append(f'{page}: no longer mapped to {group}; dropped its baselined blocks')
            continue
        path = latest / page_file(page)
        if not path.is_file() or (not is_platform(page) and page not in slugs):
            notes.append(f'{page}: missing page; kept its entries. Drop or remap it in manifest.toml first')
            continue
        text = path.read_text(encoding='utf-8')
        chosen = select_blocks(text, mapped[page], watched)
        if keys is None:
            g['blocks'][page] = chosen
        else:
            found = page_blocks(text)
            live = key_names(found)
            hashes = {key_hash(k): block_hash(t) for k, t in found.items()}
            moved = [page + SEP + (live.get(k) or name(page, k)) for k, h in g['blocks'].get(page, {}).items()
                     if k not in keys and hashes.get(k) != h]
            if moved:
                listed = ', '.join(moved)
                raise SetupError(f'{page}: also changed since the baseline: {listed};'
                                 ' list them too, or rebaseline the whole page')
            merged = {**g['blocks'].get(page, {})}
            for key in keys:
                if key in chosen:
                    merged[key] = chosen[key]
                else:
                    merged.pop(key, None)
            order = list(chosen) + [k for k in merged if k not in chosen]
            g['blocks'][page] = {k: merged[k] for k in order if k in merged}
        g['snapshot'][page] = release
        snap.append(page)
    if not refs:
        for page in [p for p in g['blocks'] if p not in mapped]:
            g['blocks'].pop(page)
            g['snapshot'].pop(page, None)
            notes.append(f'{page}: no longer mapped to {group}; dropped its baselined blocks')
    new['llms'] = sorted(slugs)
    return new, snap, notes


def stamp(guide_text: str, state: dict) -> str:
    '''R7 stamp: the guide with its stamp region regenerated (R1.2).'''
    return with_stamp(guide_text, render_stamp(state['sections']))
