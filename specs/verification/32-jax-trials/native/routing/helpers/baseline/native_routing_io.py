'''Hash-check and record actual local catalog prompt / selected-skill reads.'''
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(operation, trial_path, label=None):
    trial = Path(trial_path)
    conditions = json.loads((trial / 'conditions.json').read_text())
    if operation == 'start':
        source = trial / 'prompt.txt'
        expected = conditions['prompt_sha256']
    elif operation == 'readskill':
        catalog_dir = Path(conditions['catalog'])
        catalog_file = catalog_dir / 'catalog.json'
        if sha(catalog_file) != conditions['catalog_manifest_sha256']:
            raise ValueError('Catalog manifest changed')
        matches = [entry for entry in json.loads(catalog_file.read_text()) if entry['label'] == label]
        if len(matches) != 1:
            raise ValueError(f'Unknown or ambiguous selected skill: {label}')
        source = Path(matches[0]['snapshot_path'])
        source.resolve().relative_to(catalog_dir.resolve())
        expected = matches[0]['sha256']
    else:
        raise ValueError(f'Unknown read operation: {operation}')
    digest = sha(source)
    if digest != expected:
        raise ValueError(f'Frozen read source changed: {source}')
    event = {'operation': operation, 'label': label, 'source': str(source),
             'sha256': digest, 'bytes': source.stat().st_size,
             'utc': datetime.now(timezone.utc).isoformat()}
    with (trial / 'read-events.jsonl').open('a') as stream:
        stream.write(json.dumps(event) + '\n')
    print(source.read_text(), end='')


if __name__ == '__main__':
    read(*sys.argv[1:])
