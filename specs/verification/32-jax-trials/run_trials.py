import concurrent.futures
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path('/private/tmp/jax-skill-trials-pAYZ0t')
PREFIX = 'This is a sandboxed application of an already approved design and implementation plan. This is an inline code-generation application; deliver the requested analysis and complete code in the response. Execution in this session is not required. Return the requested analysis/code; do not conduct a new design approval workflow or modify the skill collection. '
SCENARIOS = {
'D1': 'Build a small JAX model that predicts the next sample in variable-length sine sequences. Include training, validation, and a checkpoint that lets me resume. Use synthetic data and CPU.',
'D2': 'I want a learnable continuous-time model for irregularly observed trajectories in JAX. Show a small example and explain how to establish that the gradients and fitted behavior are reliable.',
'D3': 'Construct a small JAX model on 3D points whose scalar output is invariant to rotations and whose vector output rotates with the input. Show how to validate that claim.',
'D4': 'Plan JAX adapter fine-tuning followed by preference optimization for a language model. Explain model loading, the data format and loss, and the checks needed before a substantial run.',
'E1': 'Method A has held-out errors 0.14 and 0.16 for seeds 0 and 1, each trained for one million tokens. Method B has errors 0.13, 0.18, 0.14 and 0.12 for seeds 0–3, each trained for three million tokens. Which method is better, and what evidence should I collect next?',
'E2': 'Compare two sequence models evaluated on overlapping forecast windows. Explain the evaluation units and how I can avoid overstating confidence in the difference.',
'E3': "A neural ODE's error improves with loose solver settings, and a 3D model is called rotation-equivariant because its loss is low. What checks would substantiate these claims?",
'S1': 'My JAX inference loop is slow. A timer around a jitted call reports a very small time, but end-to-end latency is much larger and changes with input length. Help reproduce and diagnose this.',
'S2': 'Implement a tiny JAX autoregressive generation example using a KV cache and establish that cached generation agrees with full-prefix generation.',
'S3': 'A non-learning JAX simulation recompiles for different scalar inputs. How should I investigate and fix it?',
}

def run(name, condition, index, skill_path=None):
    trial = ROOT / f'{name}-sonnet-{condition}-{index}'
    trial.mkdir(exist_ok=True)
    prompt = PREFIX + SCENARIOS[name]
    if skill_path:
        prompt += '\nGuidance available for this task: read ' + str(skill_path) + ' and follow its relevant local references.'
    (trial / 'prompt.txt').write_text(prompt)
    args = ['claude', '-p', '--model', 'sonnet', '--effort', 'medium', '--no-session-persistence', '--output-format', 'json', '--permission-mode', 'dontAsk', '--tools', 'Read,WebSearch,WebFetch', '--allowedTools', 'Read,WebSearch,WebFetch', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '--', prompt]
    with (trial / 'raw.json').open('w') as out, (trial / 'stderr.txt').open('w') as err:
        result = subprocess.run(args, cwd=trial, stdout=out, stderr=err, timeout=900)
    record = {'trial': trial.name, 'exit': result.returncode, 'command': args[:-1], 'fresh_session': True}
    if result.returncode == 0:
        obj = json.loads((trial / 'raw.json').read_text())
        (trial / 'response.txt').write_text(obj.get('result', ''))
        record['model_usage'] = obj.get('modelUsage')
        record['is_error'] = obj.get('is_error')
    (trial / 'conditions.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record), flush=True)
    return record

if __name__ == '__main__':
    group, condition = sys.argv[1:3]
    skill_path = sys.argv[3] if len(sys.argv) > 3 else None
    names = {'D': ['D1', 'D2', 'D3', 'D4'], 'E': ['E1', 'E2', 'E3'], 'S': ['S1', 'S2', 'S3']}[group]
    jobs = [(name, condition, i, skill_path) for name in names for i in range(1, 6 if name.endswith('1') else 2)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda args: run(*args), jobs))
    sys.exit(0 if all(r['exit'] == 0 and not r.get('is_error') for r in results) else 1)
