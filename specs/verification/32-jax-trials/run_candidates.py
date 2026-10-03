import concurrent.futures
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

from run_trials import PREFIX, ROOT, SCENARIOS


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(skill_path, condition):
    source = Path(skill_path).resolve()
    destination = ROOT / f'guidance-{condition}-{source.parent.name}'
    if destination.exists():
        raise ValueError(f'Refusing to replace an existing guidance snapshot: {destination}')
    shutil.copytree(source.parent, destination)
    hashes = {
        str(path.relative_to(destination)): digest(path)
        for path in sorted(destination.rglob('*')) if path.is_file()
    }
    (destination / 'source-hashes.json').write_text(json.dumps(hashes, indent=2) + '\n')
    return destination, hashes


def run(name, condition, index, guidance_dir, hashes):
    trial = ROOT / f'{name}-sonnet-{condition}-{index}'
    trial.mkdir(exist_ok=False)
    prompt = PREFIX + SCENARIOS[name]
    body = (guidance_dir / 'SKILL.md').read_text()
    guidance = (
        f'The following skill is loaded in the main context for this application. '
        f'Its local reference base is {guidance_dir}. '
        'Read relevant references from that directory on demand.\n\n' + body
    )
    (trial / 'prompt.txt').write_text(prompt)
    (trial / 'guidance.txt').write_text(guidance)
    args = [
        'claude', '-p', '--model', 'sonnet', '--effort', 'medium',
        '--no-session-persistence', '--output-format', 'stream-json', '--verbose',
        '--permission-mode', 'dontAsk', '--tools', 'Read,WebSearch,WebFetch',
        '--allowedTools', 'Read,WebSearch,WebFetch', '--strict-mcp-config',
        '--mcp-config', '{"mcpServers":{}}', '--append-system-prompt', guidance,
        '--', prompt,
    ]
    with (trial / 'raw.jsonl').open('w') as out, (trial / 'stderr.txt').open('w') as err:
        result = subprocess.run(args, cwd=trial, stdout=out, stderr=err, timeout=900)
    events = [json.loads(line) for line in (trial / 'raw.jsonl').read_text().splitlines() if line.strip()]
    final = next((event for event in reversed(events) if event.get('type') == 'result'), {})
    (trial / 'raw.json').write_text(json.dumps(final, indent=2) + '\n')
    (trial / 'response.txt').write_text(final.get('result', ''))
    calls = {}
    for event in events:
        for block in event.get('message', {}).get('content', []) or []:
            if not isinstance(block, dict):
                continue
            if block.get('type') == 'tool_use':
                calls[block['id']] = {
                    'id': block['id'], 'name': block['name'], 'input': block.get('input'),
                }
            elif block.get('type') == 'tool_result':
                call = calls.setdefault(block.get('tool_use_id'), {'id': block.get('tool_use_id')})
                payload = json.dumps(block.get('content'), sort_keys=True).encode()
                call['result_present'] = True
                call['is_error'] = block.get('is_error', False)
                call['result_sha256'] = hashlib.sha256(payload).hexdigest()
    (trial / 'tool-calls.json').write_text(json.dumps(list(calls.values()), indent=2) + '\n')
    record = {
        'trial': trial.name, 'exit': result.returncode, 'fresh_session': True,
        'model': 'sonnet', 'effort': 'medium',
        'model_usage': final.get('modelUsage'), 'is_error': final.get('is_error'),
        'tool_names': ['Read', 'WebSearch', 'WebFetch'],
        'guidance_directory': str(guidance_dir), 'source_hashes': hashes,
        'guidance_loaded': 'Complete SKILL.md appended to the system context; references available by Read.',
        'logging_difference': 'stream-json with verbose captures tool calls; controls used final-result JSON.',
        'raw_stream_sha256': digest(trial / 'raw.jsonl'),
    }
    (trial / 'conditions.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'trial': trial.name, 'exit': record['exit'], 'is_error': record['is_error'], 'models': record['model_usage']}), flush=True)
    return record


if __name__ == '__main__':
    group, condition, skill_path = sys.argv[1:4]
    guidance_dir, hashes = snapshot(skill_path, condition)
    names = {'D': ['D1', 'D2', 'D3', 'D4'], 'E': ['E1', 'E2', 'E3'], 'S': ['S1', 'S2', 'S3']}[group]
    jobs = [(name, condition, i, guidance_dir, hashes) for name in names for i in range(1, 6 if name.endswith('1') else 2)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda args: run(*args), jobs))
    sys.exit(0 if all(r['exit'] == 0 and r.get('is_error') is False for r in results) else 1)
