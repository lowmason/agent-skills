'''Archive built-in Codex trial artifacts and portable manual scoring links.'''
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path

TEMP = Path('/private/tmp/jax-skill-trials-pAYZ0t')
SOURCE = TEMP / 'native'
REPO = Path('/Users/lowell/.codex/worktrees/jax-deep-learning-skills/agent-skills')
DEST = REPO / 'specs/verification/32-jax-trials/native'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def archive(group, condition, report_name, snapshot=None, skill=None):
    names = {'D': ['D1', 'D2', 'D3', 'D4'], 'E': ['E1', 'E2', 'E3'],
             'S': ['S1', 'S2', 'S3']}[group]
    if condition != 'control':
        names = names + ['R' + group]
    trials = [f'{name}-codex-{condition}-{i}' for name in names
              for i in range(1, 6 if name in {'D1', 'E1', 'S1'} else 2)]
    report = (TEMP / report_name).read_text()
    for name in trials:
        if (DEST / name).exists():
            raise ValueError(f'Refusing to replace prior evidence: {name}')
        for filename in ['conditions.json', 'prompt.txt', 'response.txt', 'read-events.jsonl', 'research-notes.md']:
            if not (SOURCE / name / filename).is_file():
                raise ValueError(f'Missing native artifact: {name}/{filename}')
        events = [json.loads(line) for line in (SOURCE / name / 'read-events.jsonl').read_text().splitlines()]
        if not any(event['operation'] == 'start' for event in events):
            raise ValueError(f'No recorded prompt read: {name}')
        record = json.loads((SOURCE / name / 'conditions.json').read_text())
        if sha(SOURCE / name / 'prompt.txt') != record['prompt_sha256']:
            raise ValueError(f'Prompt changed: {name}')
        if not (SOURCE / name / 'response.txt').read_text().strip():
            raise ValueError(f'Empty native response: {name}')
    DEST.mkdir(parents=True, exist_ok=True)
    report = report.replace(str(SOURCE), str(DEST))
    for archived_report in DEST.glob('*-scoring.md'):
        report = report.replace(str(TEMP / archived_report.name), str(archived_report))
    report = report.replace(str(DEST / 'audit_native.py'),
                            str(DEST / f'helpers-{group}-{condition}' / 'audit_native.py'))
    for task in [2, 3, 4]:
        report = report.replace(str(REPO / f'.sdd/32-jax-deep-learning-skills/task-{task}-brief.md'),
                                str(DEST.parent / f'rubrics/task-{task}-brief.md'))
    if snapshot:
        original = Path(snapshot)
        if skill not in {'deep-learning', 'evaluate-deep-learning', 'optimize-jax'}:
            raise ValueError('A snapshot requires its explicit skill name')
        target = DEST / f'guidance-codex-{condition}-{skill}'
        if target.exists():
            raise ValueError(f'Refusing to replace guidance: {target}')
        shutil.copytree(original, target)
        report = report.replace(str(original), str(target))
    def portable(match):
        target = match.group(1)
        if target.startswith(str(REPO) + '/'):
            location = re.sub(r':\d+$', '', target)
            return '](' + os.path.relpath(location, DEST) + target[len(location):] + ')'
        return match.group(0)
    report = re.sub(r'\]\(([^)]+)\)', portable, report)
    for name in trials:
        shutil.copytree(SOURCE / name, DEST / name)
    (DEST / report_name).write_text(report)
    files = [p for name in trials for p in (DEST / name).rglob('*') if p.is_file()]
    files += [DEST / report_name]
    audit = SOURCE / f'{group}-{condition}-metadata-audit.json'
    if audit.is_file():
        shutil.copy2(audit, DEST / audit.name)
        files += [DEST / audit.name]
    if snapshot:
        files += [p for p in target.rglob('*') if p.is_file()]
    helper_dir = DEST / f'helpers-{group}-{condition}'
    helper_dir.mkdir(exist_ok=False)
    for filename in ['prepare_native.py', 'trial_io.py', 'archive_native.py']:
        shutil.copy2(TEMP / filename, helper_dir / filename)
    shutil.copy2(SOURCE / 'record_metadata.py', helper_dir / 'record_metadata.py')
    audit_source = TEMP / 'D-native-audit-frozen.py' if group == 'D' else SOURCE / 'audit_native.py'
    if audit_source.is_file():
        shutil.copy2(audit_source, helper_dir / 'audit_native.py')
    files += [p for p in helper_dir.iterdir() if p.is_file()]
    manifest = {str(p.relative_to(DEST)): sha(p) for p in sorted(files)}
    (DEST / f'{group}-{condition}-archive.json').write_text(json.dumps(manifest, indent=2) + '\n')
    missing = []
    for link in re.findall(r'\]\(([^)]+)\)', report):
        if link.startswith('http'):
            continue
        path = Path(re.sub(r':\d+$', '', link))
        if not path.is_absolute():
            path = DEST / path
        if not path.exists():
            missing.append(link)
    if missing:
        raise ValueError(f'Missing report links: {missing}')
    print(f'Archived {len(trials)} native trials and manual scoring; link targets exist.')


if __name__ == '__main__':
    archive(*sys.argv[1:])
