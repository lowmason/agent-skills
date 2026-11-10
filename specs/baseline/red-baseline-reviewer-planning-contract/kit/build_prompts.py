'''Build plan 73's micro-test prompts.

Usage, from the repository root:
  uv run python <kit>/build_prompts.py <sha|control> <out-dir> [<case> ...]
With a sha, each reviewer prompt carries the agent body and the filled dispatch template as
they are at <sha>, and each planner prompt carries writing-plans' SKILL.md body and, when it
exists at <sha>, references/step-recipe.md. With `control`, prompts carry no agent, template
or skill text. With no case named, builds every R and P case; X (pressure) cases build only
when named, and never as control. Text is read with git show, never through ~/.claude. Writes
one <case>.txt per prompt and MANIFEST.txt with each prompt's sha256, model, budget and the
repository files it used.
'''
import hashlib
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases  # noqa: E402

SKILL = 'skills/writing-plans/SKILL.md'
PLAN_REFS = ('skills/writing-plans/references/step-recipe.md',)


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def show(sha: str, path: str) -> str | None:
    run = subprocess.run(['git', 'show', f'{sha}:{path}'], capture_output=True, text=True)
    return run.stdout if run.returncode == 0 else None


def body(text: str) -> str:
    if not text.startswith('---\n'):
        raise SystemExit('no frontmatter')
    end = text.index('\n---\n', 4)
    return text[end + len('\n---\n'):].strip('\n')


def template_prompt(text: str) -> str:
    '''The `prompt: |` text of the file's first dispatch block, dedented by four spaces.'''
    lines = text.split('\n')
    start = next(i for i, line in enumerate(lines) if line.strip() == 'prompt: |') + 1
    end = next(i for i in range(start, len(lines)) if lines[i] == '```')
    return '\n'.join(line[4:] for line in lines[start:end]).strip('\n')


def fill(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text = text.replace(f'[{key}]', value)
    return text


def files_block(files: dict[str, str]) -> str:
    return '\n\n'.join(f'<file path="{path}">\n{text.strip()}\n</file>' for path, text in files.items())


def reviewer_prompt(case: dict, sha: str) -> tuple[str, list[str]]:
    files = files_block(case['files'])
    if sha == 'control':
        return cases.CONTROL_REVIEWER_FRAME.format(dispatch=case['control_dispatch'], files=files), []
    surface = cases.SURFACES[case['surface']]
    agent, template = show(sha, surface['agent']), show(sha, surface['template'])
    if agent is None or template is None:
        raise SystemExit(f'missing reviewer file at {sha}')
    dispatch = fill(template_prompt(template), case['values'])
    text = cases.REVIEWER_FRAME.format(agent=surface['name'], agent_body=body(agent), dispatch=dispatch,
                                       files=files)
    return text, [surface['agent'], surface['template']]


def planner_prompt(case: dict, sha: str) -> tuple[str, list[str]]:
    conversation = case['conversation'].strip()
    if sha == 'control':
        return cases.CONTROL_PLANNER_FRAME.format(conversation=conversation), []
    skill = show(sha, SKILL)
    if skill is None:
        raise SystemExit(f'missing {SKILL} at {sha}')
    refs = [(path, text) for path in PLAN_REFS if (text := show(sha, path)) is not None]
    references = ''.join(
        f'\nThe skill points to this file, and you read it at that step:\n\n'
        f'<file path="~/.claude/skills/writing-plans/{path.split("writing-plans/", 1)[1]}">\n'
        f'{text.strip()}\n</file>\n' for path, text in refs)
    text = cases.PLANNER_FRAME.format(body=body(skill), references=references, conversation=conversation)
    return text, [SKILL] + [path for path, _ in refs]


def main() -> None:
    sha, out_dir = sys.argv[1], Path(sys.argv[2])
    keys = sys.argv[3:] or sorted(k for k in cases.CASES if not k.startswith('X'))
    if out_dir.exists():
        raise SystemExit(f'refusing: {out_dir} exists')
    if sha == 'control' and any(k.startswith('X') for k in keys):
        raise SystemExit('pressure cases have no control arm')
    notes = [f'arm {sha}']
    prompts = {}
    for key in keys:
        case = cases.CASES[key]
        build = reviewer_prompt if case['kind'] == 'reviewer' else planner_prompt
        text, used = build(case, sha)
        prompts[key] = text
        notes.append(f'{key}.txt sha256 {sha256(text)} model {case["model"]} budget {case["budget"]} '
                     f'uses {",".join(used) or "-"}')
    out_dir.mkdir(parents=True)
    for key, text in prompts.items():
        (out_dir / f'{key}.txt').write_text(text)
    (out_dir / 'MANIFEST.txt').write_text('\n'.join(notes) + '\n')
    print(f'wrote {len(keys)} prompts to {out_dir}')


if __name__ == '__main__':
    main()
