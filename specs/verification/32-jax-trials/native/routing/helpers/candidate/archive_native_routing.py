'''Archive audited routing records without copying private installed skill bodies.'''
import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit


PRIVATE_ROOT = Path('/private/tmp/jax-skill-trials-pAYZ0t')
REPOSITORY = Path('/Users/lowell/.codex/worktrees/jax-deep-learning-skills/agent-skills')
DESTINATION = REPOSITORY / 'specs/verification/32-jax-trials/native/routing'
BRIEF = REPOSITORY / '.sdd/32-jax-deep-learning-skills/task-5-brief.md'
REQUIRED_RECORDS = ('prompt.txt', 'conditions.json', 'read-events.jsonl',
                    'response.txt', 'research-notes.md', 'manual-review.json')
FAMILIES = tuple(f'C{index}' for index in range(1, 7))
REPETITIONS = range(1, 6)
MARKDOWN_LINK = re.compile(r'\]\(([^()\r\n]+)\)')


@dataclass(frozen=True)
class ArchiveFile:
    source: Path | None
    target: Path
    data: bytes
    role: str


def require(condition, message):
    if not condition:
        raise ValueError(message)


def fingerprint(data):
    return {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data),
            'lines': len(data.splitlines())}


def require_no_symlinks(path):
    for component in (path, *path.parents):
        require(not component.is_symlink(), f'Symlink path is not allowed: {component}')


def read_file(source, target, role):
    source = Path(source).absolute()
    require_no_symlinks(source)
    require(source.is_file(), f'Required regular file missing: {source}')
    return ArchiveFile(source, target, source.read_bytes(), role)


def parse_json(item):
    return json.loads(item.data)


def trial_names(condition):
    return {f'{family}-codex-{condition}-{repetition}'
            for family in FAMILIES for repetition in REPETITIONS}


def collect_trials(routing, destination, condition, catalog, catalog_hash):
    expected = trial_names(condition)
    observed = {path.name for path in routing.glob(f'C*-codex-{condition}-*')}
    require(observed == expected, 'Exactly thirty trial directories, five per family, are required')
    files = []
    for name in sorted(expected):
        trial = routing / name
        require_no_symlinks(trial)
        require(trial.is_dir(), f'Trial is not a regular directory: {trial}')
        children = {path.name for path in trial.iterdir()}
        unexpected = children - set(REQUIRED_RECORDS)
        require(not unexpected, f'unexpected trial files in {name}: {sorted(unexpected)}')
        require(children == set(REQUIRED_RECORDS), f'Required trial records missing: {name}')
        records = [read_file(trial / filename, destination / name / filename, 'raw trial record')
                   for filename in REQUIRED_RECORDS]
        conditions = parse_json(next(item for item in records if item.source.name == 'conditions.json'))
        require(conditions.get('trial') == name and conditions.get('condition') == condition
                and conditions.get('family') == name.split('-')[0], f'Trial condition mismatch: {name}')
        require(Path(conditions['catalog']).resolve() == catalog.resolve()
                and conditions.get('catalog_manifest_sha256') == catalog_hash,
                f'Trial catalog identity mismatch: {name}')
        files.extend(records)
    return files


def collect_brief(brief, destination, condition):
    rubrics = destination.parent.parent / 'rubrics'
    require_no_symlinks(rubrics)
    require(rubrics.is_dir(), f'Existing rubrics directory required: {rubrics}')
    item = read_file(brief, rubrics / 'task-5-brief.md', 'Task 5 brief')
    if item.target.exists() or item.target.is_symlink():
        require_no_symlinks(item.target)
        require(item.target.is_file() and item.target.read_bytes() == item.data,
                'Existing Task 5 brief differs; preserve it and resolve the discrepancy')
        return [], [item]
    require(condition == 'baseline', 'candidate requires the existing archived Task 5 brief')
    return [item], []


def collect_helpers(source_root, routing, destination, condition):
    helpers = destination / 'helpers' / condition
    sources = [source_root / 'prepare_native_routing.py', source_root / 'native_routing_io.py',
               routing / 'routing_records.py', Path(__file__).absolute(),
               source_root / 'routing-root-contract.md']
    return [read_file(path, helpers / path.name, 'current helper or root-dispatch supplement')
            for path in sources]


def local_link(target, report):
    target = target.strip()
    if target.startswith('<') and target.endswith('>'):
        target = target[1:-1]
    if target.startswith('#') or urlsplit(target).scheme in ('https', 'http', 'mailto'):
        return None
    target = unquote(target)
    fragment = ''
    line = None
    if '#' in target:
        target, fragment = target.rsplit('#', 1)
        match = re.fullmatch(r'L([0-9]+)', fragment)
        if match:
            line = int(match[1])
    else:
        match = re.fullmatch(r'(.+):([0-9]+)', target)
        if match:
            target, line = match[1], int(match[2])
    path = Path(target)
    if not path.is_absolute():
        path = report.parent / path
    return path.resolve(), line, fragment


def render_portable_report(report, destination, condition, copied, reused):
    sources = {item.source.resolve(): item for item in (*copied, *reused) if item.source}
    links = []

    def replace_link(match):
        link = local_link(match[1], report.source)
        if link is None:
            return match[0]
        path, line, fragment = link
        require(path in sources, f'Local report link is outside the archive allowlist: {path}')
        item = sources[path]
        require(item.source.is_file(), f'Report link target does not exist: {path}')
        if line is not None:
            require(1 <= line <= fingerprint(item.data)['lines'], f'Report link line is invalid: {path}:{line}')
        relative = Path(os.path.relpath(item.target, destination)).as_posix()
        portable = quote(relative, safe='/.-_')
        if line is not None:
            portable += f':{line}'
        elif fragment:
            portable += '#' + quote(fragment, safe='-_.')
        links.append({'source': str(path), 'target': relative, 'line': line,
                      'fragment': fragment or None})
        return f']({portable})'

    data = MARKDOWN_LINK.sub(replace_link, report.data.decode('utf-8')).encode('utf-8')
    item = ArchiveFile(None, destination / f'{condition}-manual-scoring.portable.md',
                       data, 'generated report; only Markdown link targets changed')
    return item, links


def verify_audit(audit, report, catalog, condition):
    record = parse_json(audit)
    require(record.get('condition') == condition and record.get('fresh_samples') == len(trial_names(condition)),
            'Actual condition metadata-audit must identify all thirty samples')
    require(record.get('family_counts') == {family: len(REPETITIONS) for family in FAMILIES},
            'Metadata-audit family counts mismatch')
    require(Path(record['report']).resolve() == report.source.resolve()
            and record.get('report_payload') == fingerprint(report.data),
            'Audit report fingerprint/path mismatch; do not rewrite or rehash the original audit')
    require(Path(record['catalog']).resolve() == catalog.source.parent.resolve()
            and record.get('catalog_manifest_sha256') == fingerprint(catalog.data)['sha256'],
            'Metadata-audit catalog identity mismatch')


def verify_source_bytes(files):
    for item in files:
        if item.source:
            require_no_symlinks(item.source)
            require(item.source.is_file() and item.source.read_bytes() == item.data,
                    f'Source changed during archive preparation: {item.source}')


def require_new_condition(destination, condition, files):
    reserved = [destination / name for name in trial_names(condition)]
    reserved.extend((destination / f'{condition}-catalog', destination / 'helpers' / condition,
                     destination / f'{condition}-archive-manifest.json'))
    reserved.extend(item.target for item in files)
    for path in reserved:
        require_no_symlinks(path)
        require(not path.exists(), f'Condition evidence already exists; refusing replacement: {path}')


def manifest_entry(item, destination):
    return {'path': Path(os.path.relpath(item.target, destination)).as_posix(),
            'source': str(item.source) if item.source else None,
            'role': item.role, **fingerprint(item.data)}


def verify_archived_links(destination, links):
    for link in links:
        path = destination / link['target']
        require_no_symlinks(path)
        require(path.is_file(), f'Archived report link target missing: {path}')
        if link['line'] is not None:
            require(1 <= link['line'] <= fingerprint(path.read_bytes())['lines'],
                    f'Archived report link line is invalid: {path}:{link["line"]}')


def write_archive(destination, condition, files, reused, links, source_root):
    for item in files:
        item.target.parent.mkdir(parents=True, exist_ok=True)
        require_no_symlinks(item.target.parent)
        with item.target.open('xb') as stream:
            stream.write(item.data)
    for item in (*files, *reused):
        require(item.target.read_bytes() == item.data, f'Archived bytes differ: {item.target}')
    verify_source_bytes((*files, *reused))
    verify_archived_links(destination, links)
    manifest = {
        'schema_version': 1, 'condition': condition,
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'source_root': str(source_root), 'destination': str(destination),
        'trial_count': len(trial_names(condition)), 'required_trial_records': list(REQUIRED_RECORDS),
        'raw_report': f'{condition}-manual-scoring.raw.md',
        'portable_report': f'{condition}-manual-scoring.portable.md',
        'metadata_audit': f'{condition}-metadata-audit.json',
        'files': [manifest_entry(item, destination) for item in sorted(files, key=lambda item: str(item.target))],
        'reused_files': [manifest_entry(item, destination) for item in reused],
        'portable_links': links,
        'body_policy': 'Only catalog.json and sources.json copied; numbered SKILL.md snapshots and recovered-source bodies remain private.',
        'limits': 'No semantic grading, launch, application execution, catalog freeze, or full-body archive verification is performed. Raw records retain private source paths.',
        'manifest_self_hash': 'Excluded: this generated manifest is not a copied file and cannot contain its own complete hash.',
    }
    manifest_path = destination / f'{condition}-archive-manifest.json'
    with manifest_path.open('xb') as stream:
        stream.write((json.dumps(manifest, indent=2) + '\n').encode('utf-8'))
    return manifest_path


def archive(condition, source_root=PRIVATE_ROOT, destination=DESTINATION, report=None,
            audit=None, brief=BRIEF):
    require(condition in ('baseline', 'candidate'), 'Unknown condition')
    source_root, destination = Path(source_root).absolute(), Path(destination).absolute()
    require_no_symlinks(source_root)
    require_no_symlinks(destination)
    source_root, destination = source_root.resolve(), destination.resolve()
    require(source_root.is_dir(), f'Private source directory missing: {source_root}')
    require(source_root != destination and source_root not in destination.parents
            and destination not in source_root.parents, 'Source and destination directories must be separate')
    routing = source_root / 'native-routing'
    catalog_dir = routing / f'{condition}-catalog'
    catalog_files = [read_file(catalog_dir / name, destination / f'{condition}-catalog' / name,
                               'raw catalog metadata only') for name in ('catalog.json', 'sources.json')]
    report = read_file(report or routing / f'{condition}-manual-scoring.md',
                       destination / f'{condition}-manual-scoring.raw.md', 'byte-identical raw manual report')
    audit = read_file(audit or routing / f'{condition}-metadata-audit.json',
                      destination / f'{condition}-metadata-audit.json', 'byte-identical actual condition metadata-audit')
    verify_audit(audit, report, catalog_files[0], condition)
    trials = collect_trials(routing, destination, condition, catalog_dir,
                            fingerprint(catalog_files[0].data)['sha256'])
    brief_files, reused = collect_brief(brief, destination, condition)
    files = [*trials, *catalog_files, report, audit,
             *collect_helpers(source_root, routing, destination, condition), *brief_files]
    require(len({item.target for item in files}) == len(files), 'Archive destinations collide')
    require(all(item.source != item.target for item in files), 'Archive must not write to a source file')
    portable, links = render_portable_report(report, destination, condition, files, reused)
    files.append(portable)
    require_new_condition(destination, condition, files)
    verify_source_bytes((*files, *reused))
    return write_archive(destination, condition, files, reused, links, source_root)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('condition', choices=('baseline', 'candidate'))
    parser.add_argument('--source-root', type=Path, default=PRIVATE_ROOT)
    parser.add_argument('--destination', type=Path, default=DESTINATION)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--audit', type=Path)
    parser.add_argument('--brief', type=Path, default=BRIEF)
    args = parser.parse_args()
    try:
        path = archive(args.condition, args.source_root, args.destination,
                       args.report, args.audit, args.brief)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'Archive refused: {error}', file=sys.stderr)
        return 1
    print(path)
    return 0


if __name__ == '__main__':
    sys.exit(main())
