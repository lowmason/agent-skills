'''Build plan 93's implementer micro-test prompts.

Usage, from the repository root:
  uv run python <kit>/build_prompts.py <arm> <sha> <out-dir> [<fixture> ...]
<arm> is control or treatment. Takes the `prompt: |` block of the implementer prompt at <sha>,
read with git show, never through ~/.claude/skills, and fills it for each fixture (all five when
none is named). Paths inside the rep's repository start with the token @REPO@, which run_reps.sh
replaces with the rep's repository path at run time.

control: fills the task name, the scene, [BRIEF_FILE], [REPORT_FILE] and [directory], and adds
one line after the brief's two-line paragraph: `The spec excerpts your task rests on: <path>`.
treatment: fills the same, plus [SPEC_EXCERPTS_FILE], [PLAN_FILE], [WORKSPACE], [MUTANTS_GUIDE]
and [MUTANT_RUN]. It also writes a skill copy to /tmp/mt-skill/ (scripts/mutant-run,
scripts/sdd-repo, scripts/sdd-workspace and references/mutants.md, all from <sha>) and makes the
scripts executable. Every file is read before anything is written, so a file missing at <sha>
stops the build with nothing written.

Refuses an existing <out-dir>, a treatment template that lacks one of its five placeholders, and
a prompt that still holds a placeholder after the fill.
Writes one <fixture>.txt per prompt and MANIFEST.txt with the arm, the sha, the sha256 of the
template and of each prompt, and, for treatment, the sha256 of each skill-copy file.
'''
import hashlib
import re
import subprocess
import sys
from pathlib import Path

PROMPT_PATH = 'skills/subagent-driven-development/implementer-prompt.md'
SKILL_DIR = 'skills/subagent-driven-development'
SKILL_COPY = Path('/tmp/mt-skill')
SKILL_FILES = ('scripts/mutant-run', 'scripts/sdd-repo', 'scripts/sdd-workspace', 'references/mutants.md')
ARMS = ('control', 'treatment')
REPO = '@REPO@'
WORKSPACE = f'{REPO}/.sdd/plan'
SCENE = ('This is the only task in a one-task plan for a small Python project. `{module}.py` exists '
         'and is empty, and `/tmp/mt-venv/bin/python` has pytest installed.')
FIXTURES = {
    'F1': ('`latest_report`', 'latest'),
    'F2': ('`checkconf.main`', 'checkconf'),
    'F3': ('`count_words`', 'wordcount'),
    'F4': ('`summarize`', 'monthly'),
    'F5': ('`parse_duration`', 'duration'),
}
TREATMENT_PLACEHOLDERS = ('[SPEC_EXCERPTS_FILE]', '[MUTANTS_GUIDE]', '[MUTANT_RUN]', '[PLAN_FILE]', '[WORKSPACE]')
BRIEF_PAIR = 'It contains the full task text from the plan.\n'
LEFTOVER = re.compile(r'\[[A-Z][A-Z_]+\]|\[task name\]|\[directory\]|\[Scene-setting|Task N\b')


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


def fill(template: str, arm: str, fixture: str) -> str:
    name, module = FIXTURES[fixture]
    text = template.replace('Task N: [task name]', f'Task 1: {name}')
    text = re.sub(r'\[Scene-setting:[^\]]*\]', SCENE.format(module=module), text)
    text = text.replace('[BRIEF_FILE]', f'{WORKSPACE}/task-1-brief.md')
    text = text.replace('[REPORT_FILE]', f'{WORKSPACE}/task-1-report.md')
    text = text.replace('[directory]', REPO)
    if arm == 'control':
        if text.count(BRIEF_PAIR) != 1:
            raise SystemExit('the brief paragraph is not where the control line goes')
        text = text.replace(BRIEF_PAIR, BRIEF_PAIR
                            + f'The spec excerpts your task rests on: {WORKSPACE}/task-1-spec.md\n')
    else:
        missing = [p for p in TREATMENT_PLACEHOLDERS if p not in text]
        if missing:
            raise SystemExit(f'refusing: the treatment template lacks {missing}')
        text = text.replace('[SPEC_EXCERPTS_FILE]', f'{WORKSPACE}/task-1-spec.md')
        text = text.replace('[PLAN_FILE]', f'{REPO}/plan.md')
        text = text.replace('[WORKSPACE]', WORKSPACE)
        text = text.replace('[MUTANTS_GUIDE]', str(SKILL_COPY / 'references/mutants.md'))
        text = text.replace('[MUTANT_RUN]', str(SKILL_COPY / 'scripts/mutant-run'))
    left = sorted(set(LEFTOVER.findall(text)))
    if left:
        raise SystemExit(f'refusing: {fixture} still holds {left}')
    return text


def write_skill_copy(files: dict[str, str]) -> list[str]:
    notes = []
    for rel, text in files.items():
        path = SKILL_COPY / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        if rel.startswith('scripts/'):
            path.chmod(0o755)
        notes.append(f'skill copy {path} sha256 {sha256(text)}')
    return notes


def main() -> None:
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    arm, sha, out_dir = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    if arm not in ARMS:
        raise SystemExit(f'refusing: arm {arm!r} is not control or treatment')
    if out_dir.exists():
        raise SystemExit(f'refusing: {out_dir} exists')
    named = sys.argv[4:]
    for fixture in named:
        if fixture not in FIXTURES:
            raise SystemExit(f'refusing: no fixture {fixture}')
    fixtures = named or list(FIXTURES)
    template = template_at(sha)
    skill_files = {rel: show(sha, f'{SKILL_DIR}/{rel}') for rel in SKILL_FILES} if arm == 'treatment' else {}
    prompts = {fixture: fill(template, arm, fixture) for fixture in fixtures}
    notes = [f'arm {arm}', f'sha {sha}', f'template {PROMPT_PATH} sha256 {sha256(template)}']
    notes += write_skill_copy(skill_files)
    out_dir.mkdir(parents=True)
    for fixture, text in prompts.items():
        (out_dir / f'{fixture}.txt').write_text(text)
        notes.append(f'{fixture}.txt sha256 {sha256(text)}')
    (out_dir / 'MANIFEST.txt').write_text('\n'.join(notes) + '\n')
    print(f'wrote {len(prompts)} prompts to {out_dir}')


if __name__ == '__main__':
    main()
