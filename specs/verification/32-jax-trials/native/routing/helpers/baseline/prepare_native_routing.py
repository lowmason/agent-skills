'''Prepare local built-in Codex catalog-selection fixtures; no agent launch.'''
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

TEMP = Path('/private/tmp/jax-skill-trials-pAYZ0t')
ROOT = TEMP / 'native-routing'
REPO = Path('/Users/lowell/.codex/worktrees/jax-deep-learning-skills/agent-skills')
CACHE = Path('/Users/lowell/.codex/plugins/cache')
SOURCES = [
    ('', Path('/Users/lowell/.agents/skills')),
    ('', Path('/Users/lowell/.codex/skills/.system')),
    ('aws-startup-advisor', CACHE / 'claude-plugins-official/aws-startup-advisor/2.0.2/skills'),
    ('claude-code-setup', CACHE / 'claude-plugins-official/claude-code-setup/1.0.0/skills'),
    ('claude-md-management', CACHE / 'claude-plugins-official/claude-md-management/1.0.0/.codex-plugin/migrated-command-skills'),
    ('claude-md-management', CACHE / 'claude-plugins-official/claude-md-management/1.0.0/skills'),
    ('skill-creator', CACHE / 'claude-plugins-official/skill-creator/local/skills'),
    ('app-6a0b1644959c8191a6ecd016190651cd', CACHE / 'openai-curated-remote/app-6a0b1644959c8191a6ecd016190651cd/1.0.0/skills'),
    ('hugging-face', CACHE / 'openai-curated-remote/hugging-face/1.0.0/skills'),
    ('nvidia', CACHE / 'openai-curated-remote/nvidia/1.4.0/skills'),
    ('plugin-management', CACHE / 'openai-curated-remote/plugin-management/0.1.0/skills'),
    ('openai-developers', CACHE / 'openai-curated-remote/openai-developers/1.3.6/skills'),
    ('pages', CACHE / 'openai-curated-remote/pages/0.1.19/skills'),
    ('sites', CACHE / 'openai-curated-remote/sites/1.0.0-b/skills'),
    ('work-pets', CACHE / 'openai-curated-remote/work-pets/0.1.6/skills'),
    ('visualize', CACHE / 'openai-bundled/visualize/1.0.46/skills'),
    ('documents', CACHE / 'openai-primary-runtime/documents/26.905.11957/skills'),
    ('pdf', CACHE / 'openai-primary-runtime/pdf/26.905.11957/skills'),
    ('presentations', CACHE / 'openai-primary-runtime/presentations/26.905.11957/skills'),
    ('template-creator', CACHE / 'openai-primary-runtime/template-creator/26.905.11957/skills'),
    ('spreadsheets', CACHE / 'openai-primary-runtime/spreadsheets/26.905.11957/skills'),
]
FAMILIES = {
    'C1': 'Train an NNX sequence model in JAX using synthetic data.',
    'C2': 'Compare neural checkpoints trained with different budgets and seeds.',
    'C3': 'Fix recompilation in a non-learning JAX calculation.',
    'C4': 'Infer a Bayesian neural-network posterior with NumPyro and NUTS.',
    'C5': 'Use BlackJAX to sample a posterior distribution.',
    'C6': 'Improve generation speed while checking KV-cache correctness.',
}
OLD = 'Pyro, JAX, BlackJAX, ArviZ, InferenceData'
NEW = 'Pyro, BlackJAX, ArviZ, InferenceData'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata(path):
    content = path.read_text()
    if not content.startswith('---\n'):
        raise ValueError(f'Missing frontmatter: {path}')
    return yaml.safe_load(content.split('---', 2)[1])


def found(root):
    if not root.is_dir():
        raise ValueError(f'Active catalog source unavailable: {root}')
    sources = [str(root)]
    causal = root / 'recommend-causal-design'
    if root == SOURCES[0][1] and causal.is_symlink() and not causal.exists():
        sources = [str(path) for path in sorted(root.iterdir()) if path != causal]
    args = ['rg', '--files', '-L', *sources, '-g', 'SKILL.md']
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode not in [0, 1]:
        raise RuntimeError(result.stderr)
    paths = sorted(Path(line) for line in result.stdout.splitlines())
    if root == SOURCES[1][1]:
        advertised = {'imagegen', 'openai-docs', 'skill-creator', 'skill-installer'}
        paths = [path for path in paths if path.parent.name in advertised]
    return paths


def recover_advertised_causal(destination):
    label = 'recommend-causal-design'
    relative = f'skills/{label}/SKILL.md'
    result = subprocess.run(['git', 'rev-parse', '--verify', 'codex/recommend-causal-design^{commit}'],
                            cwd=REPO, capture_output=True, text=True, check=True)
    commit = result.stdout.strip()
    body = subprocess.run(['git', 'show', f'{commit}:{relative}'], cwd=REPO,
                          capture_output=True, check=True).stdout
    target = destination / 'recovered-source' / label / 'SKILL.md'
    target.parent.mkdir(parents=True)
    target.write_bytes(body)
    front = metadata(target)
    if front['name'] != label:
        raise ValueError('Recovered advertised skill has a different name')
    origin = {'advertised_path': str(SOURCES[0][1] / label / 'SKILL.md'),
              'availability': 'advertised installed link dangling at freeze time',
              'recovered_git_commit': commit, 'git_path': relative,
              'sha256': sha(target)}
    return label, target, front, origin


def freeze_baseline():
    for name in ['deep-learning', 'evaluate-deep-learning', 'optimize-jax']:
        if not (REPO / 'skills' / name / 'SKILL.md').is_file():
            raise ValueError(f'All three skills must exist before catalog trials: {name}')
    source_bayes = REPO / 'skills/bayesian-workflow/SKILL.md'
    if OLD not in metadata(source_bayes)['description']:
        raise ValueError('Baseline Bayesian description was already changed')
    destination = ROOT / 'baseline-catalog'
    destination.mkdir(parents=True, exist_ok=False)
    entries = {}
    for path in found(REPO / 'skills'):
        front = metadata(path)
        entries[front['name']] = (path, front)
    for prefix, source in SOURCES:
        for path in found(source):
            front = metadata(path)
            label = f'{prefix}:{front["name"]}' if prefix else front['name']
            if source == SOURCES[1][1] and label in entries and sha(entries[label][0]) != sha(path):
                entries[f'{label} [system]'] = (path, front)
            else:
                entries.setdefault(label, (path, front))
    recovered = None
    causal = SOURCES[0][1] / 'recommend-causal-design'
    if 'recommend-causal-design' not in entries and causal.is_symlink() and not causal.exists():
        label, path, front, recovered = recover_advertised_causal(destination)
        entries[label] = (path, front)
    manifest = []
    for index, (label, (source, front)) in enumerate(sorted(entries.items())):
        target = destination / f'{index:03d}' / 'SKILL.md'
        target.parent.mkdir()
        shutil.copy2(source, target)
        manifest.append({'label': label, 'native_label': label.removesuffix(' [system]'),
                         'description': front['description'],
                         'source': str(source), 'snapshot_path': str(target),
                         'sha256': sha(target),
                         'recovery': recovered if label == 'recommend-causal-design' else None})
    (destination / 'catalog.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (destination / 'sources.json').write_text(json.dumps(
        {'created_utc': datetime.now(timezone.utc).isoformat(),
         'repository_priority': True,
         'duplicate_read_ids': 'Distinct system bodies retain the native label and use the [system] read ID suffix.',
         'system_catalog_policy': 'Only the four session-advertised system skills are included.',
         'advertised_skill_recovery': recovered,
         'active_sources': [[prefix, str(path)] for prefix, path in SOURCES]}, indent=2) + '\n')
    return destination


def freeze_candidate():
    baseline = ROOT / 'baseline-catalog'
    destination = ROOT / 'candidate-catalog'
    source = REPO / 'skills/bayesian-workflow/SKILL.md'
    current = source.read_text()
    manifest = json.loads((baseline / 'catalog.json').read_text())
    for entry in manifest:
        path = Path(entry['snapshot_path'])
        if sha(path) != entry['sha256']:
            raise ValueError(f'Frozen baseline changed: {entry["label"]}')
        if entry['label'] == 'bayesian-workflow':
            original = path.read_text()
            if original.count(OLD) != 1 or original.replace(OLD, NEW, 1) != current:
                raise ValueError('Candidate must be the exact approved metadata-only edit')
    shutil.copytree(baseline, destination)
    for entry in manifest:
        relative = Path(entry['snapshot_path']).relative_to(baseline)
        path = destination / relative
        entry['snapshot_path'] = str(path)
        if entry['label'] == 'bayesian-workflow':
            path.write_text(current)
            entry['description'] = metadata(path)['description']
            entry['sha256'] = sha(path)
    (destination / 'catalog.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return destination


def prepare(family, condition, index):
    if family not in FAMILIES or condition not in {'baseline', 'candidate'} or not 1 <= int(index) <= 5:
        raise ValueError('Unknown routing family, condition, or repetition')
    catalog_dir = ROOT / f'{condition}-catalog'
    catalog_file = catalog_dir / 'catalog.json'
    catalog = json.loads(catalog_file.read_text())
    for entry in catalog:
        if sha(Path(entry['snapshot_path'])) != entry['sha256']:
            raise ValueError(f'Frozen catalog changed: {entry["label"]}')
    trial = ROOT / f'{family}-codex-{condition}-{index}'
    trial.mkdir(exist_ok=False)
    listing = '\n\n'.join(f'Read ID: {entry["label"]}\nSkill: {entry["native_label"]}\nDescription: {entry["description"]}' for entry in catalog)
    prompt = (
        'This is a catalog-selection simulation. Choose the primary skill and any supporting skills for the task below. '
        'Read each selected SKILL.md using the recorded local read helper, then explain the choice briefly. '
        'Do not implement the underlying task or invoke implementation workflows. '
        'Use only this frozen catalog to select; resident global guidance may remain available, but this fixture supplies the catalog under test. '
        'Skill references and scripts are outside this selection fixture. '\
        'Do not inspect the plan, rubrics, earlier trials, other conditions, or underlying repository files.\n\n'
        f'Task: {FAMILIES[family]}\n\n'
        f'Selected skill read command: python3 {TEMP / "native_routing_io.py"} readskill {trial} LABEL\n\n'
        'Catalog:\n' + listing
    )
    (trial / 'prompt.txt').write_text(prompt)
    record = {'trial': trial.name, 'family': family, 'condition': condition,
              'fresh_context': True, 'fork_turns': 'none', 'agent_type': 'default',
              'runtime': 'built-in Codex collaboration agent',
              'model': 'inherited active runtime; exact identifier unavailable',
              'reasoning_effort': 'inherited active runtime; exact value unavailable',
              'catalog': str(catalog_dir), 'catalog_entries': len(catalog),
              'catalog_manifest_sha256': sha(catalog_file), 'prompt_sha256': sha(trial / 'prompt.txt'),
              'selection_simulation': True, 'real_auto_loading_observed': False,
              'tool_policy': 'recorded local prompt and selected SKILL.md reads; own trial artifacts only',
              'resident_global_guidance_may_be_available': True}
    (trial / 'conditions.json').write_text(json.dumps(record, indent=2) + '\n')
    (trial / 'read-events.jsonl').write_text('')
    return trial


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'freeze-baseline':
        print(freeze_baseline())
    elif mode == 'freeze-candidate':
        print(freeze_candidate())
    elif mode == 'prepare':
        print(prepare(*sys.argv[2:]))
    else:
        raise ValueError(f'Unknown local preparation command: {mode}')
