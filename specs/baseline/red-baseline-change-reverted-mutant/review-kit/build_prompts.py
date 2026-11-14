'''Build plan 97's reviewer micro-test prompts (the short arm only, D8).

Usage, from the repository root:
  uv run python <kit>/build_prompts.py short <sha> <out-dir> [<case> ...]
  uv run python <kit>/build_prompts.py short leakview <out-dir> [<case> ...]
With a sha, each prompt carries the texts under test as they are at <sha>, read with git show,
never through ~/.claude: the body of agents/task-reviewer.md, frontmatter removed, framed as plan
93's review kit frames it (cases.REVIEWER_FRAME), then the Short Form dispatch of
skills/subagent-driven-development/task-reviewer-prompt.md.
The dispatch is the Short Form's `prompt: |` block with its indent removed and its placeholders
filled for the case. A template that lacks one of cases.NEW_PLACEHOLDERS, or a dispatch that still
holds a placeholder after the fill, is refused. [TEST_RULINGS] is `none`, and [GLOBAL_CONSTRAINTS]
is the case's spec rules (cases.CASES). The seven package files follow the dispatch in the order the
dispatch names them, each in <file path="..."> tags under cases.WORKSPACE. They are read from
../reviewer/packages/<case>/ in the working tree, never at <sha>. build_packages.check_package()
refuses a package whose diff name, run heads, tree lines and mutant-run base disagree.
With `leakview`, every text under test and every package file's body is a placeholder, and the fill
values are listed after the dispatch placeholder, so a grep of the output reads only the frame, the
fill values, the file paths and the task.
Writes one <case>.txt per prompt and MANIFEST.txt with the arm, the sha, the sha256 of each text
under test, of each package file and of each prompt, the model and the budget. With no case named,
builds every case. Refuses an existing <out-dir>.
'''
import hashlib
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases  # noqa: E402
from build_packages import check_package  # noqa: E402

LEAKVIEW = 'leakview'
PLACEHOLDER = '[text under test]'
FILE_PLACEHOLDER = '[package file]'
ARM = 'short'
AGENT_PATH = 'agents/task-reviewer.md'
PROMPT_PATH = 'skills/subagent-driven-development/task-reviewer-prompt.md'
PACKAGES = Path(__file__).resolve().parents[1] / 'reviewer/packages'
LEFTOVER = re.compile(r'\[[A-Z][A-Z_]+\]')
# The package files in the order the dispatch names them, as (role, file-name pattern).
ROLES = (
    ('brief', 'task-1-brief.md'),
    ('report', 'task-1-report.md'),
    ('test run', 'task-1-tests.log'),
    ('excerpts', 'task-1-spec.md'),
    ('mutants', 'task-1-mutants.md'),
    ('mutant run', 'task-1-mutants*.log'),
    ('diff', 'review-*.diff'),
)


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def show(sha: str, path: str) -> str:
    run = subprocess.run(['git', 'show', f'{sha}:{path}'], capture_output=True, text=True)
    if run.returncode != 0:
        raise SystemExit(f'missing {path} at {sha}')
    return run.stdout


def full_sha(sha: str) -> str:
    run = subprocess.run(['git', 'rev-parse', '--verify', f'{sha}^{{commit}}'], capture_output=True, text=True)
    if run.returncode != 0:
        raise SystemExit(f'no commit {sha}')
    return run.stdout.strip()


def body(text: str) -> str:
    if not text.startswith('---\n'):
        raise SystemExit('no frontmatter')
    end = text.index('\n---\n', 4)
    return text[end + len('\n---\n'):].strip('\n')


def form_block(text: str) -> str:
    '''The Short Form's `prompt: |` block, indent removed.'''
    short_part, sep, _ = text.partition('\n## Full Form')
    if not sep:
        raise SystemExit(f'no Full Form section in {PROMPT_PATH}')
    lines = short_part.splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if line.rstrip() == '  prompt: |'), None)
    if start is None:
        raise SystemExit('no `prompt: |` block in the Short Form')
    block = []
    for line in lines[start + 1:]:
        if line.startswith('```'):
            break
        if line.strip() and not line.startswith('    '):
            raise SystemExit(f'line outside the prompt block indent: {line!r}')
        block.append(line[4:] if line.strip() else '\n')
    return ''.join(block).strip('\n') + '\n'


def package(case: str) -> dict[str, Path]:
    directory = PACKAGES / cases.CASES[case]['package']
    files = {}
    for role, pattern in ROLES:
        found = sorted(directory.glob(pattern))
        if len(found) != 1:
            raise SystemExit(f'refusing: {len(found)} files in {directory} match {pattern}')
        files[role] = found[0]
    if len(list(directory.iterdir())) != len(ROLES):
        raise SystemExit(f'refusing: {directory} does not hold exactly {len(ROLES)} files')
    return files


def values(case: str, files: dict[str, Path]) -> dict[str, str]:
    base, head = check_package(case, {role: (files[role].name, files[role].read_text())
                                      for role in ('test run', 'mutant run', 'diff')})

    def path(role: str) -> str:
        return f'{cases.WORKSPACE}/{files[role].name}'

    return {
        '[BRIEF_FILE]': path('brief'),
        '[GLOBAL_CONSTRAINTS]': cases.CASES[case]['constraints'],
        '[REPORT_FILE]': path('report'),
        '[RUN_FILE]': path('test run'),
        '[BASE_SHA]': base,
        '[HEAD_SHA]': head,
        '[DIFF_FILE]': path('diff'),
        '[SPEC_EXCERPTS_FILE]': path('excerpts'),
        '[MUTANTS_FILE]': path('mutants'),
        '[MUTANT_RUN_FILE]': path('mutant run'),
        '[TEST_RULINGS]': cases.TEST_RULINGS,
    }


def fill(template: str, vals: dict[str, str]) -> str:
    missing = [p for p in cases.NEW_PLACEHOLDERS if p not in template]
    if missing:
        raise SystemExit(f'refusing: the template lacks {missing}')
    text = template
    for key, value in vals.items():
        text = text.replace(key, value)
    left = sorted(set(LEFTOVER.findall(text)))
    if left:
        raise SystemExit(f'refusing: the dispatch still holds {left}')
    return text


def inline(path: str, text: str) -> str:
    content = text.rstrip('\n')
    return f'<file path="{path}">\n{content}\n</file>'


def prompt(sha: str, case: str, agent: str, template: str) -> str:
    files = package(case)
    vals = values(case, files)
    if sha == LEAKVIEW:
        listed = '\n'.join(f'{key} = {value}' for key, value in vals.items())
        dispatch = f'{PLACEHOLDER}\n\nFill values:\n{listed}'
        bodies = {role: FILE_PLACEHOLDER for role in files}
    else:
        dispatch = fill(template, vals)
        bodies = {role: path.read_text() for role, path in files.items()}
    fixture = '\n\n'.join([dispatch.rstrip('\n'),
                           *(inline(f'{cases.WORKSPACE}/{files[role].name}', bodies[role]) for role, _ in ROLES)])
    texts = f'<agent name="task-reviewer">\n{agent}\n</agent>'
    return cases.REVIEWER_FRAME.format(texts=texts, fixture=fixture, task=cases.REVIEWER_TASK)


def main() -> None:
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    arm, sha, out_dir = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    if arm != ARM:
        raise SystemExit(f'refusing: arm {arm!r} is not {ARM}')
    if out_dir.exists():
        raise SystemExit(f'refusing: {out_dir} exists')
    keys = sys.argv[4:] or sorted(cases.CASES)
    for key in keys:
        if key not in cases.CASES:
            raise SystemExit(f'refusing: no case {key}')
    notes = [f'arm {arm}']
    if sha == LEAKVIEW:
        agent, template = PLACEHOLDER, ''
        notes.append('sha leakview')
    else:
        notes.append(f'sha {full_sha(sha)}')
        agent = body(show(sha, AGENT_PATH))
        template = form_block(show(sha, PROMPT_PATH))
        notes.append(f'{AGENT_PATH} body sha256 {sha256(agent)}')
        notes.append(f'{PROMPT_PATH} short form block sha256 {sha256(template)}')
    prompts = {}
    for key in keys:
        prompts[key] = prompt(sha, key, agent, template)
        for role, path in package(key).items():
            notes.append(f'{key} {role} {path.name} sha256 {sha256(path.read_text())}')
        notes.append(f'{key}.txt sha256 {sha256(prompts[key])} model {cases.MODEL} budget {cases.BUDGET}')
    out_dir.mkdir(parents=True)
    for key, text in prompts.items():
        (out_dir / f'{key}.txt').write_text(text)
    (out_dir / 'MANIFEST.txt').write_text('\n'.join(notes) + '\n')
    print(f'wrote {len(keys)} prompts to {out_dir}')


if __name__ == '__main__':
    main()
