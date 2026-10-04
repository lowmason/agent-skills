'''Record conductor observations and audit integrity; never select or grade skills.'''
import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FAMILIES = tuple(f'C{index}' for index in range(1, 7))
REPETITIONS = 5
CORRECTNESS = ('correct', 'incorrect', 'unresolved')
BOUNDARIES = ('preserved', 'violated', 'unresolved')
MODEL = 'inherited active runtime; exact identifier unavailable'
EFFORT = 'inherited active runtime; exact value unavailable'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def owned(path):
    resolved = Path(path).resolve()
    resolved.relative_to(ROOT)
    return resolved


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, value):
    owned(path).write_text(json.dumps(value, indent=2) + '\n')


def fingerprint(path):
    data = Path(path).read_bytes()
    data.decode('utf-8')
    return {'sha256': hashlib.sha256(data).hexdigest(),
            'bytes': len(data), 'lines': len(data.splitlines())}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def trial_record(trial):
    trial = owned(trial)
    record = read_json(trial / 'conditions.json')
    require(record['condition'] in ('baseline', 'candidate'), 'Unknown condition')
    require(record['family'] in FAMILIES, 'Unknown family')
    pattern = rf'{record["family"]}-codex-{record["condition"]}-([1-5])'
    require(re.fullmatch(pattern, trial.name) is not None, 'Trial name/condition/family mismatch')
    require(record['trial'] == trial.name, 'Recorded trial name mismatch')
    require(record['fresh_context'] is True and record['fork_turns'] == 'none'
            and record['agent_type'] == 'default', 'Fresh default fork-none condition required')
    require(record['runtime'] == 'built-in Codex collaboration agent'
            and record['model'] == MODEL and record['reasoning_effort'] == EFFORT,
            'Inherited runtime identifiers must remain explicitly unavailable')
    require(record['selection_simulation'] is True and record['real_auto_loading_observed'] is False,
            'Fixture must remain an honest catalog-selection simulation')
    require(record['resident_global_guidance_may_be_available'] is True,
            'Resident guidance limitation must be retained')
    return trial, record


def record_spawn(trial, task_name):
    trial, record = trial_record(trial)
    require(re.fullmatch(r'/root(?:/[^\s/]+)+', task_name) is not None,
            'Pass the canonical task_name from the actual collaboration.spawn_agent return')
    require('spawn_identity' not in record, 'Dispatch identity already recorded; do not replace it')
    record['spawn_identity'] = {'task_name': task_name,
                                'source': 'actual collaboration.spawn_agent return',
                                'recorded_utc': utc_now()}
    write_json(trial / 'conditions.json', record)


def inspect_reads(trial, record):
    manifest_path = Path(record['catalog']) / 'catalog.json'
    require(fingerprint(manifest_path)['sha256'] == record['catalog_manifest_sha256'],
            'Catalog manifest identity changed')
    manifest = read_json(manifest_path)
    catalog = {entry['label']: entry for entry in manifest}
    require(len(catalog) == len(manifest) == record['catalog_entries'], 'Duplicate catalog read ID/count mismatch')
    for entry in manifest:
        source = Path(entry['snapshot_path']).resolve()
        source.relative_to(manifest_path.parent.resolve())
        require(isinstance(entry['native_label'], str) and bool(entry['native_label']), 'Missing native label')
        require(fingerprint(source)['sha256'] == entry['sha256'], 'Frozen catalog body changed')
    prompt = fingerprint(trial / 'prompt.txt')
    require(prompt['sha256'] == record['prompt_sha256'], 'Prompt changed')
    events = [json.loads(line) for line in (trial / 'read-events.jsonl').read_text().splitlines()]
    require(bool(events) and events[0]['operation'] == 'start', 'First recorded read must be full prompt start')
    reads = []
    for line, event in enumerate(events, start=1):
        require(isinstance(event.get('utc'), str) and bool(event['utc']), 'Read timestamp missing')
        if event['operation'] == 'start':
            require(event['label'] is None, 'Prompt start cannot be a skill read')
            require(not reads, 'Prompt recovery must precede selected skill reads')
            source = trial / 'prompt.txt'
            expected = prompt['sha256']
        else:
            require(event['operation'] == 'readskill' and event['label'] in catalog,
                    'Only verified prompt recovery or catalog skill reads are allowed')
            entry = catalog[event['label']]
            source = Path(entry['snapshot_path'])
            expected = entry['sha256']
            reads.append({'read_id': event['label'], 'native_label': entry['native_label'],
                          'sha256': expected, 'bytes': event['bytes'], 'read_event_line': line})
        require(Path(event['source']).resolve() == source.resolve(), 'Recorded read source mismatch')
        observed = fingerprint(source)
        require(event['sha256'] == expected == observed['sha256']
                and event['bytes'] == observed['bytes'], 'Recorded full read hash/bytes mismatch')
    return prompt, reads


def inspect_payloads(trial):
    payloads = {}
    for filename in ('response.txt', 'research-notes.md'):
        path = trial / filename
        require(bool(path.read_bytes().strip()), f'Empty payload: {filename}')
        payloads[filename] = fingerprint(path)
    return payloads


def record_completion(trial):
    trial, record = trial_record(trial)
    require('spawn_identity' in record, 'Prepared conditions do not establish actual dispatch')
    require('completion' not in record, 'Completion already recorded; preserve frozen payload record')
    prompt, reads = inspect_reads(trial, record)
    record.update({'completion': 'Complete substantive response and research notes',
                   'completed_utc': utc_now(), 'first_prompt_read': prompt,
                   'actual_skill_reads': reads, 'payloads': inspect_payloads(trial),
                   'execution_claim': 'No underlying application implementation or execution observed; selection simulation only'})
    write_json(trial / 'conditions.json', record)


def validate_evidence(trial, evidence):
    require(isinstance(evidence, list) and bool(evidence), 'Manual rationale evidence required')
    names = set()
    for item in evidence:
        path = owned(item['path'])
        path.relative_to(trial)
        line = item['line']
        require(type(line) is int and 1 <= line <= fingerprint(path)['lines'], 'Invalid rationale evidence line')
        names.add(path.name)
    require({'response.txt', 'read-events.jsonl'} <= names,
            'Rationale must link full response and actual read-event evidence')


def validate_review(trial, record, review):
    require(review['correctness'] in CORRECTNESS and review['posterior_boundary'] in BOUNDARIES,
            'Manual categorical judgments required; no numeric rubric')
    require(review['full_payloads_manually_read'] is True
            and review['display_reads_manually_verified'] is True,
            'Conductor must attest full payload reading and displayed prompt/body reads')
    require(isinstance(review['selected_primary'], str) and bool(review['selected_primary']), 'Manual primary selection required')
    require(isinstance(review['selected_supporting'], list)
            and all(isinstance(value, str) and value for value in review['selected_supporting']),
            'Supporting selections must be explicit read IDs')
    require(len(set(review['selected_supporting'])) == len(review['selected_supporting']), 'Duplicate supporting selection')
    require(isinstance(review['conflicts_or_resident_choices'], list), 'Record conflicts/resident choices explicitly')
    require(isinstance(review['rationale'], str) and bool(review['rationale'].strip())
            and '\n' not in review['rationale'] and '|' not in review['rationale'],
            'Provide one explicit table-safe manual rationale')
    actual_ids = {item['read_id'] for item in record['actual_skill_reads']}
    if review['correctness'] == 'correct':
        require(review['selected_primary'] in actual_ids, 'Correct primary selection requires its actual body read')
    validate_evidence(trial, review['evidence'])


def record_review(trial, review_file):
    trial, record = trial_record(trial)
    require('completion' in record, 'Full completion record required before manual review')
    require(not (trial / 'manual-review.json').exists(), 'Manual review already recorded; preserve it')
    review = read_json(review_file)
    validate_review(trial, record, review)
    review.update({'reviewed_utc': utc_now(), 'catalog_manifest_sha256': record['catalog_manifest_sha256'],
                   'payloads': record['payloads'], 'grading_source': 'conductor manual full-response judgment',
                   'semantic_grading_automated': False})
    write_json(trial / 'manual-review.json', review)


def report_rows(report):
    rows = {}
    for line in Path(report).read_text().splitlines():
        if not re.match(r'^\| C[1-6]-codex-', line):
            continue
        cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
        require(len(cells) == 6, 'Manual report row must contain six columns')
        require(cells[0] not in rows, 'Duplicate report trial row')
        rows[cells[0]] = cells
    return rows


def audit(root, condition, report):
    root, report = owned(root), owned(report)
    require(condition in ('baseline', 'candidate'), 'Unknown audit condition')
    expected = {f'{family}-codex-{condition}-{index}' for family in FAMILIES for index in range(1, REPETITIONS + 1)}
    trials = {path.name: path for path in root.glob(f'C*-codex-{condition}-*') if path.is_dir()}
    require(set(trials) == expected, 'Audit requires all thirty trials, exactly five per family')
    rows = report_rows(report)
    require(set(rows) == expected, 'Report must contain all thirty unique trial rows')
    identities, manifests = set(), set()
    correctness, boundaries, families = Counter(), Counter(), Counter()
    body_reads = 0
    for name in sorted(expected):
        trial, record = trial_record(trials[name])
        identity = record['spawn_identity']
        require(identity['source'] == 'actual collaboration.spawn_agent return', 'Actual dispatch source missing')
        require(identity['task_name'] not in identities, 'Fresh dispatch identity reused')
        identities.add(identity['task_name'])
        require(record['completion'] == 'Complete substantive response and research notes', 'Incomplete payload')
        prompt, reads = inspect_reads(trial, record)
        require(record['first_prompt_read'] == prompt and record['actual_skill_reads'] == reads, 'Read metadata changed')
        payloads = inspect_payloads(trial)
        require(record['payloads'] == payloads, 'Completed payload hash/bytes/lines changed')
        review = read_json(trial / 'manual-review.json')
        for timestamp in (identity['recorded_utc'], record['completed_utc'], review['reviewed_utc']):
            parsed = datetime.fromisoformat(timestamp)
            require(parsed.utcoffset() == timezone.utc.utcoffset(None), 'Record timestamp must be UTC')
        require(re.fullmatch(r'/root(?:/[^\s/]+)+', identity['task_name']) is not None,
                'Dispatch identity must be the canonical task_name')
        require(review['grading_source'] == 'conductor manual full-response judgment',
                'Manual judgment provenance missing')
        validate_review(trial, record, review)
        require(review['payloads'] == payloads
                and review['catalog_manifest_sha256'] == record['catalog_manifest_sha256']
                and review['semantic_grading_automated'] is False, 'Manual review provenance mismatch')
        cells = rows[name]
        supporting = ', '.join(review['selected_supporting']) or 'none'
        require(cells[1:5] == [review['selected_primary'], supporting, review['correctness'], review['posterior_boundary']],
                'Report selection/categories disagree with manual record')
        require(review['rationale'] in cells[5], 'Full manual rationale absent from report row')
        for item in review['evidence']:
            require(f'({item["path"]}:{item["line"]})' in cells[5], 'Manual rationale evidence link absent from row')
        manifests.add((record['catalog'], record['catalog_manifest_sha256']))
        correctness[review['correctness']] += 1
        boundaries[review['posterior_boundary']] += 1
        families[record['family']] += 1
        body_reads += len(reads)
    require(len(manifests) == 1, 'All cohort trials must share one frozen catalog identity')
    links = re.findall(r'\]\((/[^)]+?):(\d+)\)', Path(report).read_text())
    for path, line in links:
        require(1 <= int(line) <= fingerprint(path)['lines'], 'Report evidence link outside actual file')
    catalog_path, catalog_hash = next(iter(manifests))
    return {'condition': condition, 'fresh_samples': len(identities), 'family_counts': dict(sorted(families.items())),
            'manual_correctness_counts': {value: correctness[value] for value in CORRECTNESS},
            'manual_posterior_boundary_counts': {value: boundaries[value] for value in BOUNDARIES},
            'actual_body_read_events': body_reads, 'verified_local_evidence_links': len(links),
            'catalog': catalog_path, 'catalog_manifest_sha256': catalog_hash,
            'report': str(report), 'report_payload': fingerprint(report),
            'semantic_grading_performed': False, 'application_code_executed': False,
            'limits': 'Hashes and caller attestations do not independently prove tool display reading or real dispatch; no real auto-loading measurement.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for command in ('spawn', 'complete', 'review'):
        item = commands.add_parser(command)
        item.add_argument('trial')
        if command == 'spawn':
            item.add_argument('task_name')
        if command == 'review':
            item.add_argument('review_file')
    item = commands.add_parser('audit')
    item.add_argument('root')
    item.add_argument('condition', choices=('baseline', 'candidate'))
    item.add_argument('report')
    args = parser.parse_args()
    if args.command == 'spawn':
        record_spawn(args.trial, args.task_name)
    elif args.command == 'complete':
        record_completion(args.trial)
    elif args.command == 'review':
        record_review(args.trial, args.review_file)
    else:
        print(json.dumps(audit(args.root, args.condition, args.report), indent=2))


if __name__ == '__main__':
    main()
