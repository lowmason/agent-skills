'''Record actual local prompt/reference reads for a built-in application trial.'''
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def read(mode, trial_path, relative=None):
    trial = Path(trial_path).resolve()
    conditions = json.loads((trial / 'conditions.json').read_text())
    if mode == 'start' and relative is None:
        source = trial / 'prompt.txt'
        expected = conditions['prompt_sha256']
    elif mode == 'readref' and relative is not None:
        root = Path(conditions['guidance_directory']).resolve()
        source = (root / relative).resolve()
        key = str(source.relative_to(root))
        expected = conditions['source_hashes'][key]
    else:
        raise ValueError('Use start TRIAL or readref TRIAL RELATIVE_REFERENCE')
    payload = source.read_bytes()
    actual = hashlib.sha256(payload).hexdigest()
    if actual != expected:
        raise ValueError(f'Frozen payload changed: {source}')
    event = {'operation': mode, 'source': str(source), 'sha256': actual,
             'bytes': len(payload), 'time_utc': datetime.now(timezone.utc).isoformat()}
    with (trial / 'read-events.jsonl').open('a') as stream:
        stream.write(json.dumps(event) + '\n')
    print(payload.decode(), end='')


if __name__ == '__main__':
    read(*sys.argv[1:])
