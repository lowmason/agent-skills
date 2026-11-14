'''Build plan 97's implementer micro-test prompts and the skill copy the reps use.

Usage, from the repository root:
  uv run python <kit>/build_prompts.py <arm> <text-sha> <script-sha> <out-dir> [<fixture> ...]
<arm> is control or treatment. Takes the `prompt: |` block of the implementer prompt and
references/mutants.md at <text-sha>, and scripts/mutant-run, scripts/sdd-repo and
scripts/sdd-workspace at <script-sha>, each read with git show, never through ~/.claude/skills.
It fills the prompt for each fixture (all three when none is named). Paths inside the rep's
repository start with the token @REPO@, and the task's BASE is the token @BASE@. run_reps.sh
replaces both at run time, @BASE@ with the rep repository's first commit.

Both arms fill the task name, the scene, [BRIEF_FILE], [REPORT_FILE], [directory],
[SPEC_EXCERPTS_FILE], [PLAN_FILE], [WORKSPACE], [MUTANTS_GUIDE] and [MUTANT_RUN], and refuse a
template that lacks one of the last five. [MUTANTS_GUIDE] and [MUTANT_RUN] point into the skill
copy /tmp/mt-skill/, which this script writes, with the scripts made executable.
control (plan 97 D8): references/mutants.md gets one substitution in step 5,
`mutant-run PLAN_FILE N --` becomes `mutant-run PLAN_FILE N BASE --`, refused unless it matches
exactly once. The prompt gets one dispatch line, `The task's BASE commit: @BASE@`, after the
`Work from:` line.
treatment: fills [BASE] with @BASE@, and refuses a template that lacks it. mutants.md is copied
as it is.
Every file is read before anything is written, so a file missing at a sha stops the build with
nothing written.

Refuses an existing <out-dir> and a prompt that still holds a placeholder after the fill.
Writes one <fixture>.txt per prompt and MANIFEST.txt with the arm, both shas, the sha256 of the
template and of each prompt, the sha256 of mutants.md before and after any substitution, and the
sha256 of each skill-copy file.
'''
import hashlib
import re
import subprocess
import sys
from pathlib import Path

PROMPT_PATH = 'skills/subagent-driven-development/implementer-prompt.md'
SKILL_DIR = 'skills/subagent-driven-development'
SKILL_COPY = Path('/tmp/mt-skill')
GUIDE = 'references/mutants.md'
SCRIPTS = ('scripts/mutant-run', 'scripts/sdd-repo', 'scripts/sdd-workspace')
ARMS = ('control', 'treatment')
REPO = '@REPO@'
BASE = '@BASE@'
WORKSPACE = f'{REPO}/.sdd/plan'
SCENE = ('This is the only task in a one-task plan for a small Python project, and '
         '`/tmp/mt-venv/bin/python` has pytest installed.')
FIXTURES = {
    'F6': 'Fix `reorder_needed` at the threshold',
    'F7': 'Collapse whitespace runs in `slugify`',
    'F8': '`to_bytes`',
}
PLACEHOLDERS = ('[SPEC_EXCERPTS_FILE]', '[MUTANTS_GUIDE]', '[MUTANT_RUN]', '[PLAN_FILE]', '[WORKSPACE]')
CONTROL_CALL = ('mutant-run PLAN_FILE N --', 'mutant-run PLAN_FILE N BASE --')
WORK_FROM = f'Work from: {REPO}\n'
CONTROL_LINE = f'The task\'s BASE commit: {BASE}\n'
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


def guide_for(arm: str, guide: str) -> str:
    if arm == 'treatment':
        return guide
    old, new = CONTROL_CALL
    if guide.count(old) != 1:
        raise SystemExit(f'refusing: {GUIDE} holds `{old}` {guide.count(old)} times, not once')
    return guide.replace(old, new)


def fill(template: str, arm: str, fixture: str) -> str:
    missing = [p for p in PLACEHOLDERS + (('[BASE]',) if arm == 'treatment' else ()) if p not in template]
    if missing:
        raise SystemExit(f'refusing: the {arm} template lacks {missing}')
    text = template.replace('Task N: [task name]', f'Task 1: {FIXTURES[fixture]}')
    text = re.sub(r'\[Scene-setting:[^\]]*\]', SCENE, text)
    text = text.replace('[BRIEF_FILE]', f'{WORKSPACE}/task-1-brief.md')
    text = text.replace('[REPORT_FILE]', f'{WORKSPACE}/task-1-report.md')
    text = text.replace('[directory]', REPO)
    text = text.replace('[SPEC_EXCERPTS_FILE]', f'{WORKSPACE}/task-1-spec.md')
    text = text.replace('[PLAN_FILE]', f'{REPO}/plan.md')
    text = text.replace('[WORKSPACE]', WORKSPACE)
    text = text.replace('[MUTANTS_GUIDE]', str(SKILL_COPY / GUIDE))
    text = text.replace('[MUTANT_RUN]', str(SKILL_COPY / 'scripts/mutant-run'))
    if arm == 'control':
        if text.count(WORK_FROM) != 1:
            raise SystemExit('refusing: the `Work from:` line, where the control line goes, is not there once')
        text = text.replace(WORK_FROM, WORK_FROM + '\n' + CONTROL_LINE)
    else:
        text = text.replace('[BASE]', BASE)
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
    if len(sys.argv) < 5:
        raise SystemExit(__doc__)
    arm, text_sha, script_sha, out_dir = sys.argv[1], sys.argv[2], sys.argv[3], Path(sys.argv[4])
    if arm not in ARMS:
        raise SystemExit(f'refusing: arm {arm!r} is not control or treatment')
    if out_dir.exists():
        raise SystemExit(f'refusing: {out_dir} exists')
    named = sys.argv[5:]
    for fixture in named:
        if fixture not in FIXTURES:
            raise SystemExit(f'refusing: no fixture {fixture}')
    fixtures = named or list(FIXTURES)
    template = template_at(text_sha)
    guide = show(text_sha, f'{SKILL_DIR}/{GUIDE}')
    files = {rel: show(script_sha, f'{SKILL_DIR}/{rel}') for rel in SCRIPTS}
    files[GUIDE] = guide_for(arm, guide)
    prompts = {fixture: fill(template, arm, fixture) for fixture in fixtures}
    notes = [f'arm {arm}', f'text sha {text_sha}', f'script sha {script_sha}',
             f'template {PROMPT_PATH} sha256 {sha256(template)}',
             f'{GUIDE} at text sha sha256 {sha256(guide)}']
    if arm == 'control':
        notes.append(f'{GUIDE} after the D8 substitution sha256 {sha256(files[GUIDE])}')
    notes += write_skill_copy(files)
    out_dir.mkdir(parents=True)
    for fixture, text in prompts.items():
        (out_dir / f'{fixture}.txt').write_text(text)
        notes.append(f'{fixture}.txt sha256 {sha256(text)}')
    (out_dir / 'MANIFEST.txt').write_text('\n'.join(notes) + '\n')
    print(f'wrote {len(prompts)} prompts to {out_dir}')


if __name__ == '__main__':
    main()
