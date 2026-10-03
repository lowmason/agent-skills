'''Prepare matched built-in Codex trials; never launch an external service.'''
import hashlib
import json
import shutil
import sys
from pathlib import Path

from run_trials import PREFIX, SCENARIOS

ROOT = Path('/private/tmp/jax-skill-trials-pAYZ0t/native')
SCENARIOS = dict(SCENARIOS)
SCENARIOS.update({
    'RD': 'Which local references support irregular continuous-time models and equivariant 3D outputs? Explain the framework choice for each.',
    'RE': 'Which references should I use to evaluate a generative model and an LLM after preference optimization? Explain the main evaluation units and artifacts to retain.',
    'RS': 'My training loss is not improving, and my generation loop recompiles for different input lengths. Which guidance handles each issue, and where should I look for cache checks?',
})


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(name, condition, index, guidance=None):
    trial = ROOT / f'{name}-codex-{condition}-{index}'
    trial.mkdir(parents=True, exist_ok=False)
    record = {
        'trial': trial.name, 'scenario': name, 'condition': condition,
        'runtime': 'Built-in Codex collaboration agent', 'agent_type': 'default',
        'requested_fork_turns': 'none', 'model': 'Inherited active runtime; exact identifier not exposed by collaboration API',
        'effort': 'Inherited active runtime; exact value not exposed by collaboration API',
        'tool_policy': 'Read-only information gathering; execute only local trial_io recording helper, no delivered application code',
        'automatic_skill_loading_observed': False,
        'source_hashes': {}, 'guidance_directory': None,
    }
    prompt = PREFIX + SCENARIOS[name]
    if guidance:
        guidance = Path(guidance).resolve()
        hashes = json.loads((guidance / 'source-hashes.json').read_text())
        for relative, expected in hashes.items():
            if sha(guidance / relative) != expected:
                raise ValueError(f'Snapshot changed: {relative}')
        record['source_hashes'] = hashes
        record['guidance_directory'] = str(guidance)
        record['guidance_loading'] = 'Full SKILL.md supplied in first recorded prompt read; references read on demand through trial_io'
        prompt += '\n\nTask-specific guidance loaded in this main context:\n\n' + (guidance / 'SKILL.md').read_text()
        prompt += f'\n\nLocal reference base: {guidance}. Use the trial_io readref operation for relevant references.'
    else:
        record['guidance_loading'] = 'No new JAX skill guidance supplied; ordinary knowledge/primary sources available'
    (trial / 'prompt.txt').write_text(prompt)
    record['prompt_sha256'] = sha(trial / 'prompt.txt')
    (trial / 'conditions.json').write_text(json.dumps(record, indent=2) + '\n')
    (trial / 'read-events.jsonl').write_text('')
    print(trial)


if __name__ == '__main__':
    prepare(*sys.argv[1:])
