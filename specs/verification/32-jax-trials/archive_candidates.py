'''Preserve owned candidate evidence without replacing prior conditions.'''
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path('/private/tmp/jax-skill-trials-pAYZ0t')
REPO = Path('/Users/lowell/.codex/worktrees/jax-deep-learning-skills/agent-skills')
DEST = REPO / 'specs/verification/32-jax-trials'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def archive(group, condition, skill, report_name):
    names = {'D': ['D1', 'D2', 'D3', 'D4', 'RD'], 'D1': ['D1'], 'D-refined': ['D1', 'D2', 'D4'],
             'E': ['E1', 'E2', 'E3', 'RE'], 'S': ['S1', 'S2', 'S3', 'RS']}[group]
    trials = [f'{name}-sonnet-{condition}-{i}' for name in names
              for i in range(1, 6 if name in {'D1', 'E1', 'S1'} else 2)]
    snapshot = f'guidance-{condition}-{skill}'
    report_path = ROOT / report_name
    if not report_path.is_file():
        raise ValueError(f'Scoring report unavailable: {report_path}')
    files = ['prompt.txt', 'response.txt', 'conditions.json', 'guidance.txt',
             'tool-calls.json', 'raw.json', 'raw.jsonl', 'stderr.txt']
    for name in trials:
        for filename in files:
            if not (ROOT / name / filename).is_file():
                raise ValueError(f'Missing artifact: {name}/{filename}')
        record = json.loads((ROOT / name / 'conditions.json').read_text())
        if record['exit'] != 0 or record['is_error'] is not False:
            raise ValueError(f'Failed invocation: {name}')
    for name in [*trials, snapshot]:
        if (DEST / name).exists():
            raise ValueError(f'Refusing to replace archive: {name}')
    report = report_path.read_text()
    report = report.replace(str(ROOT), str(DEST))
    report = report.replace(str(REPO / '.sdd/32-jax-deep-learning-skills/task-2-brief.md'), str(DEST / 'rubrics/task-2-brief.md'))
    report = report.replace(str(REPO / '.sdd/32-jax-deep-learning-skills/task-3-brief.md'), str(DEST / 'rubrics/task-3-brief.md'))
    report = report.replace(str(REPO / '.sdd/32-jax-deep-learning-skills/task-4-brief.md'), str(DEST / 'rubrics/task-4-brief.md'))
    def portable_link(match):
        target = match.group(1)
        if target.startswith(str(REPO) + '/'):
            location = re.sub(r':\d+$', '', target)
            line = target[len(location):]
            return '](' + os.path.relpath(location, DEST) + line + ')'
        return match.group(0)
    report = re.sub(r'\]\(([^)]+)\)', portable_link, report)
    for name in trials:
        (DEST / name).mkdir()
        for filename in files:
            shutil.copy2(ROOT / name / filename, DEST / name / filename)
    shutil.copytree(ROOT / snapshot, DEST / snapshot)
    (DEST / report_name).write_text(report)
    manifest = {}
    for name in [*trials, snapshot]:
        for path in sorted((DEST / name).rglob('*')):
            if path.is_file():
                manifest[str(path.relative_to(DEST))] = digest(path)
    manifest[report_name] = digest(DEST / report_name)
    (DEST / f'{group}-{condition}-archive.json').write_text(json.dumps(manifest, indent=2) + '\n')
    for filename in ['run_candidates.py', 'archive_candidates.py']:
        shutil.copy2(ROOT / filename, DEST / filename)
    targets = re.findall(r'\]\(([^)]+)\)', report)
    missing = []
    for target in targets:
        if target.startswith('http'):
            continue
        file_path = Path(re.sub(r':\d+$', '', target))
        if not file_path.is_absolute():
            file_path = DEST / file_path
        if not file_path.exists():
            missing.append(target)
    if missing:
        raise ValueError(f'Missing report targets: {missing}')
    print(f'Archived {len(trials)} trials, frozen {skill} snapshot, complete scoring; {len(targets)} report links checked.')


if __name__ == '__main__':
    archive(*sys.argv[1:5])
