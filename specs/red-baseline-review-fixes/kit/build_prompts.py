'''Build plan 76's micro-test prompts.

Usage, from the repository root:
  uv run python <kit>/build_prompts.py <sha> <out-dir> [<case> ...]
  uv run python <kit>/build_prompts.py leakview <out-dir> [<case> ...]
With a sha, each prompt carries the case's texts as they are at <sha>: a SKILL.md as its body
(frontmatter stripped), a reference or command file whole. Both arms use the same frame,
fixture and task; only the sha differs. Text is read with git show, never through ~/.claude.
Writes one <case>.txt per prompt and MANIFEST.txt with each prompt's sha256, model, budget and
the repository files it used. With `leakview`, every text under test is replaced by a
placeholder, so a grep of the output reads only the frame, the fixture and the task. With no
case named, builds every case.
'''
import fnmatch
import hashlib
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases  # noqa: E402

LEAKVIEW = 'leakview'
PLACEHOLDER = '[text under test]'

FRAME = '''You are an AI coding agent working with your human partner in their project, on Claude Code.

{texts}

Below is the session so far. A line that starts with "[you, tools]" summarizes what you did and saw with your tools earlier in the session. You have no tools in this turn.

<session>
{fixture}
</session>

{task}
'''


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def show(sha: str, path: str) -> str:
    run = subprocess.run(['git', 'show', f'{sha}:{path}'], capture_output=True, text=True)
    if run.returncode != 0:
        raise SystemExit(f'missing {path} at {sha}')
    return run.stdout


def expand(sha: str, pattern: str) -> list[str]:
    '''A path, or a glob over the files at <sha>; a glob that matches nothing adds nothing.'''
    if '*' not in pattern:
        return [pattern]
    directory = pattern.rsplit('/', 1)[0] + '/'
    run = subprocess.run(['git', 'ls-tree', '-r', '--name-only', sha, directory], capture_output=True, text=True)
    if run.returncode != 0:
        return []
    return sorted(p for p in run.stdout.splitlines() if fnmatch.fnmatch(p, pattern))


def body(text: str) -> str:
    if not text.startswith('---\n'):
        raise SystemExit('no frontmatter')
    end = text.index('\n---\n', 4)
    return text[end + len('\n---\n'):].strip('\n')


def text_block(path: str, text: str | None) -> str:
    '''One text under test, framed as it reaches the agent; `text` None gives the placeholder.'''
    if path.endswith('/SKILL.md'):
        name = path.split('/')[1]
        content = PLACEHOLDER if text is None else body(text)
        return (f'The {name} skill is loaded in this session. Its files sit in ~/.claude/skills/{name}/: '
                f'SKILL.md and the files it names. The text of SKILL.md as it is in your context:\n\n'
                f'<skill name="{name}">\n{content}\n</skill>')
    if path.startswith('commands/'):
        name = Path(path).stem
        content = PLACEHOLDER if text is None else text.strip('\n')
        return (f'Your partner\'s latest message is the /{name} command. Its text, as it reached you:\n\n'
                f'<command name="/{name}">\n{content}\n</command>')
    shown = '~/.claude/skills/' + path.split('skills/', 1)[1]
    content = PLACEHOLDER if text is None else text.strip('\n')
    return (f'You read this file when the text above pointed you to it:\n\n'
            f'<file path="{shown}">\n{content}\n</file>')


def prompt(case: dict, sha: str) -> str:
    texts = []
    for pattern in case['texts']:
        if sha == LEAKVIEW:
            texts.append(text_block(pattern.replace('*', 'x'), None))
            continue
        texts.extend(text_block(path, show(sha, path)) for path in expand(sha, pattern))
    return FRAME.format(texts='\n\n'.join(texts), fixture=case['fixture'].strip('\n'), task=case['task'])


def main() -> None:
    sha, out_dir = sys.argv[1], Path(sys.argv[2])
    keys = sys.argv[3:] or sorted(cases.CASES)
    if out_dir.exists():
        raise SystemExit(f'refusing: {out_dir} exists')
    notes = [f'arm {sha}']
    prompts = {}
    for key in keys:
        case = cases.CASES[key]
        prompts[key] = prompt(case, sha)
        notes.append(f'{key}.txt sha256 {sha256(prompts[key])} model {case["model"]} budget {case["budget"]} '
                     f'uses {",".join(case["texts"])}')
    out_dir.mkdir(parents=True)
    for key, text in prompts.items():
        (out_dir / f'{key}.txt').write_text(text)
    (out_dir / 'MANIFEST.txt').write_text('\n'.join(notes) + '\n')
    print(f'wrote {len(keys)} prompts to {out_dir}')


if __name__ == '__main__':
    main()
