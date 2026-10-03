"""Metadata-only final audit. Does not execute or import application code."""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path('/private/tmp/jax-skill-trials-pAYZ0t')
NATIVE = ROOT / 'native'
cohort, condition = sys.argv[1:]
scenario_counts = {'D': {'D1': 5, 'D2': 1, 'D3': 1, 'D4': 1},
                   'E': {'E1': 5, 'E2': 1, 'E3': 1},
                   'S': {'S1': 5, 'S2': 1, 'S3': 1}}[cohort].copy()
if cohort == 'D' and condition != 'control':
    scenario_counts['RD'] = 1
identities = []
line_counts = {}
for scenario, count in scenario_counts.items():
    for index in range(1, count + 1):
        trial = NATIVE / f'{scenario}-codex-{condition}-{index}'
        record = json.loads((trial / 'conditions.json').read_text())
        assert record['condition'] == condition
        assert record['agent_type'] == 'default'
        assert record['requested_fork_turns'] == 'none'
        assert 'not exposed' in record['model'] and 'not exposed' in record['effort']
        assert record['completion'].startswith('Complete substantive')
        identities.append(record['spawn_identity']['task_name'])
        prompt = (trial / 'prompt.txt').read_bytes()
        assert hashlib.sha256(prompt).hexdigest() == record['prompt_sha256']
        events = [json.loads(line) for line in (trial / 'read-events.jsonl').read_text().splitlines()]
        assert events[0]['operation'] == 'start'
        assert events[0]['sha256'] == record['prompt_sha256']
        assert events[0]['bytes'] == len(prompt)
        if condition == 'control':
            assert not record['source_hashes']
            assert len(events) == 1
        else:
            base = Path(record['guidance_directory'])
            assert len(record['source_hashes']) == 9
            assert (base / 'SKILL.md').read_bytes() in prompt
            for relative, digest in record['source_hashes'].items():
                assert hashlib.sha256((base / relative).read_bytes()).hexdigest() == digest
            for event in events[1:]:
                assert event['operation'] == 'readref'
                relative = str(Path(event['source']).relative_to(base))
                assert event['sha256'] == record['source_hashes'][relative]
        response = (trial / 'response.txt').read_bytes()
        assert response.strip() and (trial / 'research-notes.md').read_text().strip()
        assert hashlib.sha256(response).hexdigest() == record['response_sha256']
        assert len(response.splitlines()) == record['response_lines']
        line_counts[trial.name] = record['response_lines']
assert len(set(identities)) == len(identities)
report = ROOT / f'{cohort}-native-{"control" if condition == "control" else "candidate"}-scoring.md'
report_text = report.read_text()
rows = re.findall(r'^### .*? — (\d+)/(\d+); vector \[([0-2, ]+)\]', report_text, re.M)
assert len(rows) == len(identities), (len(rows), len(identities))
for score, maximum, vector in rows:
    values = [int(value) for value in vector.split(',')]
    assert sum(values) == int(score)
    assert 2 * len(values) == int(maximum)
links = re.findall(r'\]\((/[^)]+?):(\d+)\)', report_text)
for name, line in links:
    file = Path(name)
    assert file.is_file(), name
    assert 0 < int(line) <= len(file.read_bytes().splitlines()), (name, line)
print(json.dumps({'report': str(report), 'fresh_samples': len(identities),
                  'score': sum(int(row[0]) for row in rows),
                  'maximum': sum(int(row[1]) for row in rows),
                  'verified_local_evidence_links': len(links), 'response_lines': line_counts}, indent=2))
