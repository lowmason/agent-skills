'''Trusted orchestration metadata checks; never execute delivered response code.'''
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/private/tmp/jax-skill-trials-pAYZ0t/native')
mode, name, *extra = sys.argv[1:]
trial = ROOT / name
record_path = trial / 'conditions.json'
record = json.loads(record_path.read_text())
if mode == 'spawn':
    record['spawn_identity'] = {'task_name': extra[0]}
elif mode == 'complete':
    events = [json.loads(line) for line in (trial / 'read-events.jsonl').read_text().splitlines()]
    prompt = (trial / 'prompt.txt').read_bytes()
    assert events and events[0]['operation'] == 'start'
    assert events[0]['sha256'] == record['prompt_sha256'] == hashlib.sha256(prompt).hexdigest()
    assert events[0]['bytes'] == len(prompt)
    for event in events[1:]:
        assert event['operation'] == 'readref'
        base = Path(record['guidance_directory'])
        relative = str(Path(event['source']).relative_to(base))
        assert event['sha256'] == record['source_hashes'][relative]
        assert hashlib.sha256(Path(event['source']).read_bytes()).hexdigest() == event['sha256']
    response = (trial / 'response.txt').read_bytes()
    notes = (trial / 'research-notes.md').read_text()
    assert response.strip() and notes.strip() and record['spawn_identity']
    record.update(
        completion='Complete substantive response and research notes; child final received',
        completion_verified_at_utc=datetime.now(timezone.utc).isoformat(),
        response_sha256=hashlib.sha256(response).hexdigest(),
        response_lines=len(response.splitlines()),
        verified_first_read='Full prompt hash and byte count match first recorded start event',
        actual_reference_reads=[event['source'] for event in events[1:]],
        application_execution='Not executed per explicit child delivery/research notes; scorer treats response code as data',
    )
    print(json.dumps({'trial':name,'response_lines':record['response_lines'],'actual_reference_reads':record['actual_reference_reads']}))
else:
    raise ValueError('Use spawn NAME ID or complete NAME')
record_path.write_text(json.dumps(record, indent=2) + '\n')
