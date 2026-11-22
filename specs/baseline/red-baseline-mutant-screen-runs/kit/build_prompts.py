'''Build plan 104's micro-test prompts and the skill copy that one role's reps read.

Usage, from the repository root:
  uv run python <kit>/build_prompts.py <role> <arm> <text-sha> <script-sha> <out-dir> [<fixture> ...]
<role> is implementer, controller or inline, and <arm> is control or treatment. Every text (each .md
file) is read at <text-sha> and every script at <script-sha>, each with git show, never through
~/.claude/. The skill copy goes to MSR_SKILL_ROOT/<role>/ (default /private/tmp/msr104-skill/), which
is removed first, so no file of another build stays:
- implementer: subagent-driven-development's references/mutants.md and scripts/mutant-run, sdd-repo
  and sdd-workspace, laid out as that skill's folder;
- controller: references/test-run.md, mutants.md, fix-loop.md and batching.md, and scripts/test-run,
  mutant-run, sdd-repo and sdd-workspace, laid out the same way;
- inline: executing-plans/SKILL.md and executing-plans/scripts/task-start and task-done, beside
  subagent-driven-development/references/mutants.md and resuming.md and
  subagent-driven-development/scripts/mutant-run, sdd-repo, sdd-workspace, task-brief and test-run
  (every script that task-start and task-done call, and mutant-run), so that
  `<this-skill-dir>/../subagent-driven-development/` resolves.
Scripts are made executable.

The implementer prompt is the `prompt: |` block of implementer-prompt.md at <text-sha>, filled as
plan 97's kit fills it: the task name from brief.md's first line, the fixture's scene.txt in place of
[Scene-setting: ...], and [BRIEF_FILE], [REPORT_FILE], [directory], [SPEC_EXCERPTS_FILE], [PLAN_FILE],
[WORKSPACE], [MUTANTS_GUIDE], [MUTANT_RUN] and [BASE]. It refuses a template that lacks one of the
last six. The controller and inline prompts are the fixture's scene.txt. In every prompt @SKILL@
becomes the skill copy's root; @REPO@ and @BASE@ stay for run_reps.sh, which fills them per rep.

Refuses an existing <out-dir>, a fixture of another role, and a prompt that still holds a
placeholder or @SKILL@ after the fill. Every file is read before anything is written. Writes one
<fixture>.txt for each fixture (each of the role's fixtures when none is named) and MANIFEST.txt:
the role, the arm, both shas, the skill copy's root, one `skill-copy <rel> <sha256> <source>@<sha>`
line for each skill-copy file, the template's sha256 (implementer), and one
`prompt <name> <sha256>` line for each prompt. run_reps.sh checks the copy and the prompt against it
before each rep (rep_tools.py check-copy).
'''
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
FIXTURES = KIT / 'fixtures'
SKILL_ROOT = Path(os.environ.get('MSR_SKILL_ROOT') or '/private/tmp/msr104-skill')
SDD = 'skills/subagent-driven-development'
EP = 'skills/executing-plans'
PROMPT_PATH = f'{SDD}/implementer-prompt.md'
ROLES = {
    'implementer': ('I1', 'I2', 'I3'),
    'controller': ('C1', 'C2'),
    'inline': ('E1', 'E2'),
}
# (path in the copy, path in the repository) for each role.
COPIES = {
    'implementer': [(rel, f'{SDD}/{rel}') for rel in (
        'references/mutants.md', 'scripts/mutant-run', 'scripts/sdd-repo', 'scripts/sdd-workspace')],
    'controller': [(rel, f'{SDD}/{rel}') for rel in (
        'references/test-run.md', 'references/mutants.md', 'references/fix-loop.md', 'references/batching.md',
        'scripts/test-run', 'scripts/mutant-run', 'scripts/sdd-repo', 'scripts/sdd-workspace')],
    'inline': [(f'executing-plans/{rel}', f'{EP}/{rel}') for rel in (
        'SKILL.md', 'scripts/task-start', 'scripts/task-done')]
    + [(f'subagent-driven-development/{rel}', f'{SDD}/{rel}') for rel in (
        'references/mutants.md', 'references/resuming.md', 'scripts/mutant-run', 'scripts/sdd-repo',
        'scripts/sdd-workspace', 'scripts/task-brief', 'scripts/test-run')],
}
ARMS = ('control', 'treatment')
REPO = '@REPO@'
BASE = '@BASE@'
SKILL = '@SKILL@'
WORKSPACE = f'{REPO}/.sdd/plan'
PLACEHOLDERS = ('[SPEC_EXCERPTS_FILE]', '[MUTANTS_GUIDE]', '[MUTANT_RUN]', '[PLAN_FILE]', '[WORKSPACE]', '[BASE]')
LEFTOVER = re.compile(r'\[[A-Z][A-Z_]+\]|\[task name\]|\[directory\]|\[Scene-setting|Task N\b|@SKILL@')
# A scene text names the controller's own placeholders, such as [RUN_FILE], on purpose.
SCENE_LEFTOVER = re.compile(r'@SKILL@')
TASK_LINE = re.compile(r'^### Task 1: (.+)$')


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def show(sha: str, path: str) -> str:
    result = subprocess.run(['git', 'show', f'{sha}:{path}'], capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or f'git show failed for {path} at {sha}')
    return result.stdout


def template_at(sha: str) -> str:
    lines = show(sha, PROMPT_PATH).splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if line.rstrip() == '  prompt: |'), None)
    if start is None:
        raise SystemExit(f'no `prompt: |` block in {PROMPT_PATH} at {sha}')
    body = []
    for line in lines[start + 1:]:
        if line.startswith('```'):
            break
        if line.strip() and not line.startswith('    '):
            raise SystemExit(f'line outside the prompt block indent: {line!r}')
        body.append(line[4:] if line.strip() else '\n')
    return ''.join(body).strip('\n') + '\n'


def scene(fixture: str) -> str:
    return (FIXTURES / fixture / 'scene.txt').read_text()


def task_name(fixture: str) -> str:
    first = (FIXTURES / fixture / 'brief.md').read_text().splitlines()[0]
    match = TASK_LINE.match(first)
    if not match:
        raise SystemExit(f'refusing: {fixture}/brief.md does not open with "### Task 1: <name>"')
    return match.group(1)


def fill_implementer(template: str, fixture: str, copy: Path) -> str:
    missing = [p for p in PLACEHOLDERS if p not in template]
    if missing:
        raise SystemExit(f'refusing: the template lacks {missing}')
    text = template.replace('Task N: [task name]', f'Task 1: {task_name(fixture)}')
    text = re.sub(r'\[Scene-setting:[^\]]*\]', lambda _: scene(fixture).strip('\n'), text)
    for old, new in (('[BRIEF_FILE]', f'{WORKSPACE}/task-1-brief.md'), ('[REPORT_FILE]', f'{WORKSPACE}/task-1-report.md'),
                     ('[directory]', REPO), ('[SPEC_EXCERPTS_FILE]', f'{WORKSPACE}/task-1-spec.md'),
                     ('[PLAN_FILE]', f'{REPO}/plan.md'), ('[WORKSPACE]', WORKSPACE),
                     ('[MUTANTS_GUIDE]', str(copy / 'references/mutants.md')),
                     ('[MUTANT_RUN]', str(copy / 'scripts/mutant-run')), ('[BASE]', BASE)):
        text = text.replace(old, new)
    return text


def is_script(rel: str) -> bool:
    return '/scripts/' in f'/{rel}'


def checked(text: str, fixture: str, copy: Path, leftover: re.Pattern = LEFTOVER) -> str:
    text = text.replace(SKILL, str(copy))
    left = sorted(set(leftover.findall(text)))
    if left:
        raise SystemExit(f'refusing: {fixture} still holds {left}')
    return text


def main() -> None:
    if len(sys.argv) < 6:
        raise SystemExit(__doc__)
    role, arm, text_sha, script_sha, out_dir = sys.argv[1:5] + [Path(sys.argv[5])]
    if role not in ROLES:
        raise SystemExit(f'refusing: role {role!r} is not implementer, controller or inline')
    if arm not in ARMS:
        raise SystemExit(f'refusing: arm {arm!r} is not control or treatment')
    if out_dir.exists():
        raise SystemExit(f'refusing: {out_dir} exists')
    fixtures = sys.argv[6:] or list(ROLES[role])
    for fixture in fixtures:
        if fixture not in ROLES[role]:
            raise SystemExit(f'refusing: {fixture} is not a {role} fixture')
    copy = SKILL_ROOT / role
    shas = {rel: script_sha if is_script(rel) else text_sha for rel, _ in COPIES[role]}
    files = {rel: (show(shas[rel], source), f'{source}@{shas[rel]}') for rel, source in COPIES[role]}
    notes = [f'role {role}', f'arm {arm}', f'text-sha {text_sha}', f'script-sha {script_sha}', f'skill-copy-root {copy}']
    if role == 'implementer':
        template = template_at(text_sha)
        notes.append(f'template {PROMPT_PATH}@{text_sha} {sha256(template)}')
        prompts = {f: checked(fill_implementer(template, f, copy), f, copy) for f in fixtures}
    else:
        prompts = {f: checked(scene(f), f, copy, SCENE_LEFTOVER) for f in fixtures}
    if copy.exists():
        shutil.rmtree(copy)
    for rel, (text, source) in files.items():
        path = copy / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        if is_script(rel):
            path.chmod(0o755)
        notes.append(f'skill-copy {rel} {sha256(text)} {source}')
    out_dir.mkdir(parents=True)
    for fixture, text in prompts.items():
        (out_dir / f'{fixture}.txt').write_text(text)
        notes.append(f'prompt {fixture}.txt {sha256(text)}')
    (out_dir / 'MANIFEST.txt').write_text('\n'.join(notes) + '\n')
    print(f'wrote {len(prompts)} prompt(s) to {out_dir} and the {role} skill copy to {copy}')


if __name__ == '__main__':
    main()
