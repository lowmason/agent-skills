# /// script
# requires-python = '>=3.11'
# dependencies = []
# ///
'''Build plan 94's decision-only micro-test prompts for finishing-a-development-branch's Step 3b.

Run from the repository root:
  uv run specs/baseline/red-baseline-branch-explainer/micro/build_micro.py <arm> <out-dir> <scenario>...
<arm> is control (the skill body at EXEC_BASE, read from the record's `EXEC_BASE: <sha>` line) or treatment (the
skill body and references in the working tree). Each scenario is fixtures/<scenario>.txt. The script writes
<out-dir>/<scenario>.txt and <out-dir>/MANIFEST.txt, the sha256 of each prompt. TEMPLATE and fixture() are plan 60's,
unchanged (~/.cache/agent-skills/scratch/plan60-micro/build.py).
'''
import hashlib
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RECORD = HERE.parent.parent / 'red-baseline-branch-explainer.md'
SKILL = 'skills/finishing-a-development-branch'
MARKERS = ('{redirect}', '{noop}')
EXEC_BASE_RE = re.compile(r'^EXEC_BASE: (\S+)\s*$', re.M)
SHA_RE = re.compile(r'[0-9a-f]{40}')
FILES_HEADER = 'Reference files of the skill that you have read:'
TEMPLATE = '''You are a coding agent. You work in a git repository with your human partner. The skill below is loaded in this session, and you are following it.

<skill name="{skill}">
{body}
</skill>

Tools in this session:
{tools}

The session so far:
{situation}

Your partner's latest message: "{message}"

Answer with your next actions, in order, up to the point where you would stop and wait for your partner. Number them, one per line, and start each with one of these words:
RUN <the exact shell command for one Bash call>
TOOL <the tool name and its arguments>
EDIT <the file: the change>
ASK <the exact question to your partner>
REPORT <the exact message to your partner>
Where an action depends on output you have not seen, write the action, then one line for each outcome, starting with IF <outcome>:. Write nothing else.
'''


def fixture(path: Path) -> tuple[dict[str, str], str]:
    head, situation = path.read_text(encoding='utf-8').split('\n---\n', 1)
    fields = dict(line.split(': ', 1) for line in head.splitlines())
    return fields, situation.strip('\n')


def refuse(reason: str) -> None:
    print(f'build_micro: {reason}', file=sys.stderr)
    sys.exit(2)


def exec_base() -> str:
    '''EXEC_BASE from the record's `EXEC_BASE: <sha>` line: 40 hex characters naming a commit, else exit 2.'''
    found = EXEC_BASE_RE.search(RECORD.read_text(encoding='utf-8')) if RECORD.is_file() else None
    if found is None:
        refuse(f'no `EXEC_BASE: <sha>` line in {RECORD}')
    sha = found.group(1)
    if not SHA_RE.fullmatch(sha):
        refuse(f'EXEC_BASE {sha!r} is not 40 hexadecimal characters')
    check = subprocess.run(['git', 'cat-file', '-e', f'{sha}^{{commit}}'], cwd=ROOT, capture_output=True)
    if check.returncode != 0:
        refuse(f'EXEC_BASE {sha} is not a commit in this repository')
    return sha


def skill_body(arm: str) -> str:
    '''The SKILL.md body without its frontmatter: at EXEC_BASE for control, from the working tree for treatment.'''
    if arm == 'control':
        sha = exec_base()
        text = subprocess.run(['git', 'show', f'{sha}:{SKILL}/SKILL.md'], cwd=ROOT, capture_output=True, text=True,
                              check=True).stdout
    else:
        text = (ROOT / SKILL / 'SKILL.md').read_text(encoding='utf-8')
    return text.split('\n---\n', 1)[1].strip('\n')


def situation_of(path: Path) -> tuple[dict[str, str], str]:
    '''The fixture's fields and situation; exit 2 when a plan 60 marker is left in it.'''
    fields, situation = fixture(path)
    if any(marker in situation for marker in MARKERS):
        refuse(f'{path.name} still holds a {" or ".join(MARKERS)} marker')
    return fields, situation


def with_files(prompt: str, files: dict[str, str]) -> str:
    '''The prompt with each reference file as a <file> block after the </skill> line.'''
    if not files:
        return prompt
    blocks = ''.join(f'<file path="references/{name}">\n{text.strip(chr(10))}\n</file>\n' for name, text in files.items())
    return prompt.replace('</skill>\n', f'</skill>\n\n{FILES_HEADER}\n{blocks}', 1)


def reference_files(arm: str, fields: dict[str, str]) -> dict[str, str]:
    '''The scenario's `files:` list, read from the working tree; the control arm gets none.'''
    names = [] if fields.get('files', 'none') == 'none' else [name.strip() for name in fields['files'].split(',')]
    if arm == 'control':
        return {}
    return {name: (ROOT / SKILL / 'references' / name).read_text(encoding='utf-8') for name in names}


def main() -> None:
    if len(sys.argv) < 4 or sys.argv[1] not in ('control', 'treatment'):
        refuse('usage: build_micro.py <control|treatment> <out-dir> <scenario>...')
    arm, out = sys.argv[1], Path(sys.argv[2]).expanduser()
    if arm == 'control':
        exec_base()
    tools = (HERE / 'tools.txt').read_text(encoding='utf-8').strip('\n')
    body = skill_body(arm)
    prompts = {}
    for scenario in sys.argv[3:]:
        fields, situation = situation_of(HERE / 'fixtures' / f'{scenario}.txt')
        prompt = TEMPLATE.format(skill=fields['skill'], body=body, tools=tools, situation=situation,
                                 message=fields['message'])
        prompts[scenario] = with_files(prompt, reference_files(arm, fields))
    out.mkdir(parents=True, exist_ok=True)
    manifest = []
    for scenario, prompt in prompts.items():
        (out / f'{scenario}.txt').write_text(prompt, encoding='utf-8')
        manifest.append(f'{hashlib.sha256(prompt.encode()).hexdigest()}  {scenario}.txt')
        print(f'{scenario}.txt {len(prompt)}')
    (out / 'MANIFEST.txt').write_text('\n'.join(manifest) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
