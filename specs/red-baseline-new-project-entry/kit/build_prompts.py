'''Build plan 78's micro-test prompts.

Usage, from the repository root:
  CASE_REPOS="$HOME/Projects" uv run python <kit>/build_prompts.py <sha> <out-dir> [<case> ...]
  CASE_REPOS="$HOME/Projects" uv run python <kit>/build_prompts.py leakview <out-dir> [<case> ...]
With a sha, each prompt carries a skill listing and the case's texts as they are at <sha>: a
SKILL.md as its body (frontmatter stripped), a reference or command file whole. Both arms use
the same frame, fixture and task; only the sha differs. Text is read with git show, never
through ~/.claude. Writes one <case>.txt per prompt and MANIFEST.txt with each prompt's sha256,
model, budget, the repository files it used and every case-repository file it read. With
`leakview`, every text under test and every listed skill's description is replaced by a
placeholder, so a grep of the output reads only the frame, the fixture and the task. Fixture
files from the case-study repositories stay in the leak view: they are fixture, not text under
test. With no case named, builds every case.

Plan 78 changes plan 77's builder in three ways (plan 78, Task 1 Step 2):
- every prompt carries, after the frame's first line, the skill listing of LISTING, read from
  each SKILL.md's frontmatter at the arm's sha;
- a fixture places a case-repository file with a `{file:<key>}` marker, which the case maps to
  a repo_file() call; repo_file() reads with `git -C "$CASE_REPOS/<repo>" show` and adds a
  MANIFEST line for each read;
- a case whose `texts` list is empty gets no text block.
'''
import fnmatch
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases  # noqa: E402

LEAKVIEW = 'leakview'
PLACEHOLDER = '[text under test]'
CASE_REPOS = 'CASE_REPOS'
REPO_URL = 'https://github.com/lowmason'

LISTING = ['brainstorming', 'creative-thinking', 'derive-roadmap', 'describe-critique-methodology',
           'design-architecture', 'executing-plans', 'subagent-driven-development', 'writing-plans']
LISTING_HEAD = 'Skills available in this session, as your skill listing shows them (name: description):'

FRAME_HEAD = 'You are an AI coding agent working with your human partner in their project, on Claude Code.'

FRAME_SESSION = '''Below is the session so far. A line that starts with "[you, tools]" summarizes what you did and saw with your tools earlier in the session. You have no tools in this turn.

<session>
{fixture}
</session>

{task}
'''

FILE_MARK = re.compile(r'\{file:([a-z0-9-]+)\}')
HEADING = re.compile(r'^#{1,6} ')
FENCES = ('```', '~~~')

# The MANIFEST lines of the case-repository reads made for the prompt being built.
READS: list[str] = []


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(['git', *args], capture_output=True, text=True, encoding='utf-8')


def show(sha: str, path: str) -> str:
    run = git('show', f'{sha}:{path}')
    if run.returncode != 0:
        raise SystemExit(f'missing {path} at {sha}')
    return run.stdout


def expand(sha: str, pattern: str) -> list[str]:
    '''A path, or a glob over the files at <sha>; a glob that matches nothing adds nothing.'''
    if '*' not in pattern:
        return [pattern]
    directory = pattern.rsplit('/', 1)[0] + '/'
    run = git('ls-tree', '-r', '--name-only', sha, directory)
    if run.returncode != 0:
        return []
    return sorted(p for p in run.stdout.splitlines() if fnmatch.fnmatch(p, pattern))


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith('---\n'):
        raise SystemExit('no frontmatter')
    end = text.index('\n---\n', 4)
    return text[4:end], text[end + len('\n---\n'):]


def body(text: str) -> str:
    return split_frontmatter(text)[1].strip('\n')


def description(front: str, where: str) -> str:
    '''The `description:` value of a frontmatter block: a folded (`>`) block scalar only.'''
    lines = front.splitlines()
    for i, line in enumerate(lines):
        if not line.startswith('description:'):
            continue
        if line[len('description:'):].strip() not in ('>', '>-'):
            raise SystemExit(f'refusing: {where} has a description that is not a folded block')
        folded = []
        for nxt in lines[i + 1:]:
            if not nxt.strip():
                raise SystemExit(f'refusing: {where} has a blank line inside its description')
            if not nxt.startswith((' ', '\t')):
                break
            folded.append(nxt.strip())
        return ' '.join(folded)
    raise SystemExit(f'refusing: {where} has no description')


def listing(sha: str) -> str:
    '''The skill listing block: one `- name: description` line per skill of LISTING.'''
    lines = [LISTING_HEAD]
    for name in LISTING:
        if sha == LEAKVIEW:
            lines.append(f'- {name}: {PLACEHOLDER}')
            continue
        where = f'skills/{name}/SKILL.md at {sha}'
        front = split_frontmatter(show(sha, f'skills/{name}/SKILL.md'))[0]
        if f'name: {name}' not in front.splitlines():
            raise SystemExit(f'refusing: {where} does not name itself {name}')
        lines.append(f'- {name}: {description(front, where)}')
    return '\n'.join(lines)


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


def excerpt_of(text: str, size: int) -> str:
    '''The file's first line, every Markdown heading line outside a code fence, the first
    `size` characters, then the excerpt marker. A first line that is a heading shows twice.'''
    lines = text.splitlines()
    headings, fence = [], None
    for line in lines:
        mark = line.lstrip()[:3]
        if mark in FENCES:
            fence = mark if fence is None else (None if mark == fence else fence)
            continue
        if fence is None and HEADING.match(line):
            headings.append(line)
    first = lines[0] if lines else ''
    return '\n\n'.join([first, '\n'.join(headings), text[:size].rstrip('\n'),
                        f'[excerpt: {size} of {len(text)} characters]'])


def repo_file(repo: str, commit: str, path: str, excerpt: int | None = None) -> str:
    '''Read <path> at <commit> from the local clone $CASE_REPOS/<repo>, and add its MANIFEST line.'''
    root = os.environ.get(CASE_REPOS)
    if not root:
        raise SystemExit(f'refusing: {CASE_REPOS} is not set')
    clone = str(Path(root) / repo)
    run = git('-C', clone, 'show', f'{commit}:{path}')
    if run.returncode != 0:
        raise SystemExit(f'refusing: cannot read {path} at {commit} in {CASE_REPOS}/{repo}')
    full = git('-C', clone, 'rev-parse', '--verify', f'{commit}^{{commit}}').stdout.strip()
    text = run.stdout if excerpt is None else excerpt_of(run.stdout, excerpt)
    shape = 'whole' if excerpt is None else f'excerpt {excerpt}'
    READS.append(f'  read {REPO_URL}/{repo} {full} {path} {shape} sha256 {sha256(text)}')
    return text


def fixture(key: str, case: dict) -> str:
    '''The case's fixture, with each `{file:<key>}` marker replaced by its repo_file() text.'''
    files = case.get('files', {})
    marks = set(FILE_MARK.findall(case['fixture']))
    if marks != set(files):
        raise SystemExit(f'refusing: {key} markers {sorted(marks)} do not match its files {sorted(files)}')
    texts = {}
    for mark, spec in files.items():
        text = repo_file(spec['repo'], spec['commit'], spec['path'], spec.get('excerpt'))
        derive = spec.get('derive')
        if derive is not None:
            text = derive(text)
            READS.append(f'  {mark}: derived from the read above by cases.{derive.__name__}, sha256 {sha256(text)}')
        texts[mark] = text.strip('\n')
    return FILE_MARK.sub(lambda m: texts[m.group(1)], case['fixture'].strip('\n'))


def prompt(key: str, case: dict, sha: str) -> str:
    texts = []
    for pattern in case['texts']:
        if sha == LEAKVIEW:
            texts.append(text_block(pattern.replace('*', 'x'), None))
            continue
        texts.extend(text_block(path, show(sha, path)) for path in expand(sha, pattern))
    parts = [FRAME_HEAD, listing(sha)]
    if texts:
        parts.append('\n\n'.join(texts))
    parts.append(FRAME_SESSION.format(fixture=fixture(key, case), task=case['task']))
    return '\n\n'.join(parts)


def main() -> None:
    sha, out_dir = sys.argv[1], Path(sys.argv[2])
    keys = sys.argv[3:] or sorted(cases.CASES)
    if out_dir.exists():
        raise SystemExit(f'refusing: {out_dir} exists')
    arm = sha if sha == LEAKVIEW else f'{sha} ({git("rev-parse", "--verify", f"{sha}^{{commit}}").stdout.strip()})'
    notes = [f'arm {arm}', f'listing {", ".join(LISTING)}, read at the arm\'s sha']
    prompts = {}
    for key in keys:
        case = cases.CASES[key]
        READS.clear()
        prompts[key] = prompt(key, case, sha)
        notes.append(f'{key}.txt sha256 {sha256(prompts[key])} model {case["model"]} budget {case["budget"]} '
                     f'uses {",".join(case["texts"]) or "none"}')
        notes.extend(READS)
    out_dir.mkdir(parents=True)
    for key, text in prompts.items():
        (out_dir / f'{key}.txt').write_text(text, encoding='utf-8')
    (out_dir / 'MANIFEST.txt').write_text('\n'.join(notes) + '\n', encoding='utf-8')
    print(f'wrote {len(keys)} prompts to {out_dir}')


if __name__ == '__main__':
    main()
