'''Build plan 93's reviewer micro-test prompts.

Usage, from the repository root:
  uv run python <kit>/build_prompts.py <arm> <sha> <out-dir> [<case> ...]
  uv run python <kit>/build_prompts.py <arm> leakview <out-dir> [<case> ...]
<arm> is short or full. With a sha, each prompt carries the texts under test as they are at <sha>,
read with git show, never through ~/.claude:
  short: the body of agents/task-reviewer.md, frontmatter removed, framed as plan 84's
    reviewer-run case frames it (cases.REVIEWER_FRAME), then the Short Form dispatch of
    skills/subagent-driven-development/task-reviewer-prompt.md.
  full: the Full Form dispatch of the same file alone, as a general-purpose subagent gets it
    (cases.FULL_FRAME).
The dispatch is the form's `prompt: |` block with its indent removed and its placeholders filled for
the case. A template that holds all four of cases.NEW_PLACEHOLDERS gets them filled, with
[TEST_RULINGS] as `none`. A template that holds none of them gets cases.FIXED_LINE after the
run-file line: the control arm's one fixed line that names the three files. A template that holds
some of them, or a dispatch that still holds a placeholder after the fill, is refused. The seven
package files follow the dispatch in the order the dispatch names them, each in <file path="...">
tags under cases.WORKSPACE. They are read from ../reviewer/packages/<case>/ in the working tree,
never at <sha>. A package whose diff name, run heads and tree lines do not agree is refused.
With `leakview`, every text under test and every package file's body is a placeholder, and the fill
values and the fixed line are listed after the dispatch placeholder, so a grep of the output reads
only the frame, the fill values, the fixed line, the file paths and the task.
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

LEAKVIEW = 'leakview'
PLACEHOLDER = '[text under test]'
FILE_PLACEHOLDER = '[package file]'
ARMS = ('short', 'full')
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


def form_block(text: str, arm: str) -> str:
    '''The `prompt: |` block of the Short Form (short) or the Full Form (full), indent removed.'''
    short_part, sep, full_part = text.partition('\n## Full Form')
    if not sep:
        raise SystemExit(f'no Full Form section in {PROMPT_PATH}')
    lines = (short_part if arm == 'short' else full_part).splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if line.rstrip() == '  prompt: |'), None)
    if start is None:
        raise SystemExit(f'no `prompt: |` block in the {arm} form')
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


def shas(case: str, files: dict[str, Path]) -> tuple[str, str]:
    '''The base and head short shas from the diff's name, checked against the two runs.'''
    match = re.fullmatch(r'review-([0-9a-f]{7})\.\.([0-9a-f]{7})\.diff', files['diff'].name)
    if not match:
        raise SystemExit(f'refusing: {case} diff name {files["diff"].name}')
    base, head = match.groups()
    for role in ('test run', 'mutant run'):
        lines = files[role].read_text().splitlines()
        if not lines[2].startswith(f'head: {head}') or lines[3] != 'tree: clean':
            raise SystemExit(f'refusing: {case} {role} is not at head {head} on a clean tree')
    return base, head


def values(case: str, files: dict[str, Path]) -> dict[str, str]:
    base, head = shas(case, files)

    def path(role: str) -> str:
        return f'{cases.WORKSPACE}/{files[role].name}'

    return {
        '[BRIEF_FILE]': path('brief'),
        '[GLOBAL_CONSTRAINTS]': cases.GLOBAL_CONSTRAINTS,
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


def fixed_line(vals: dict[str, str]) -> str:
    return cases.FIXED_LINE.format(excerpts=vals['[SPEC_EXCERPTS_FILE]'], mutants=vals['[MUTANTS_FILE]'],
                                   mutant_run=vals['[MUTANT_RUN_FILE]'])


def fill(template: str, vals: dict[str, str]) -> tuple[str, str]:
    present = [p for p in cases.NEW_PLACEHOLDERS if p in template]
    if present and len(present) != len(cases.NEW_PLACEHOLDERS):
        raise SystemExit(f'refusing: the template holds {present}, not all of {list(cases.NEW_PLACEHOLDERS)}')
    text = template
    if not present:
        if text.count(cases.FIXED_LINE_ANCHOR) != 1:
            raise SystemExit('refusing: the run-file line is not where the fixed line goes')
        text = text.replace(cases.FIXED_LINE_ANCHOR, cases.FIXED_LINE_ANCHOR + '\n' + fixed_line(vals))
    for key, value in vals.items():
        text = text.replace(key, value)
    left = sorted(set(LEFTOVER.findall(text)))
    if left:
        raise SystemExit(f'refusing: the dispatch still holds {left}')
    return text, ('four placeholders filled' if present else 'fixed line added')


def inline(path: str, text: str) -> str:
    content = text.rstrip('\n')
    return f'<file path="{path}">\n{content}\n</file>'


def prompt(arm: str, sha: str, case: str, agent: str, template: str) -> tuple[str, str]:
    files = package(case)
    vals = values(case, files)
    if sha == LEAKVIEW:
        listed = '\n'.join(f'{key} = {value}' for key, value in vals.items())
        dispatch, mode = f'{PLACEHOLDER}\n\nFill values:\n{listed}\n\nFixed line:\n{fixed_line(vals)}', 'leak view'
        bodies = {role: FILE_PLACEHOLDER for role in files}
    else:
        dispatch, mode = fill(template, vals)
        bodies = {role: path.read_text() for role, path in files.items()}
    fixture = '\n\n'.join([dispatch.rstrip('\n'),
                           *(inline(f'{cases.WORKSPACE}/{files[role].name}', bodies[role]) for role, _ in ROLES)])
    if arm == 'short':
        texts = f'<agent name="task-reviewer">\n{agent}\n</agent>'
        return cases.REVIEWER_FRAME.format(texts=texts, fixture=fixture, task=cases.REVIEWER_TASK), mode
    return cases.FULL_FRAME.format(fixture=fixture, task=cases.FULL_TASK), mode


def main() -> None:
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    arm, sha, out_dir = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    if arm not in ARMS:
        raise SystemExit(f'refusing: arm {arm!r} is not short or full')
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
        agent = body(show(sha, AGENT_PATH)) if arm == 'short' else ''
        template = form_block(show(sha, PROMPT_PATH), arm)
        if arm == 'short':
            notes.append(f'{AGENT_PATH} body sha256 {sha256(agent)}')
        notes.append(f'{PROMPT_PATH} {arm} form block sha256 {sha256(template)}')
    prompts = {}
    for key in keys:
        prompts[key], mode = prompt(arm, sha, key, agent, template)
        for role, path in package(key).items():
            notes.append(f'{key} {role} {path.name} sha256 {sha256(path.read_text())}')
        notes.append(f'{key}.txt sha256 {sha256(prompts[key])} model {cases.MODEL} budget {cases.BUDGET} dispatch {mode}')
    out_dir.mkdir(parents=True)
    for key, text in prompts.items():
        (out_dir / f'{key}.txt').write_text(text)
    (out_dir / 'MANIFEST.txt').write_text('\n'.join(notes) + '\n')
    print(f'wrote {len(keys)} prompts to {out_dir}')


if __name__ == '__main__':
    main()
