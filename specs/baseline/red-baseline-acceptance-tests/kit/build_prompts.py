'''Fill the probe's three prompts from a plan copy (plan 81).

Usage, from the repository root:
  uv run python <kit>/build_prompts.py control <copy> <out-file>
  uv run python <kit>/build_prompts.py reader <copy> <out-file>
  uv run python <kit>/build_prompts.py adjudicator <copy> <reader-reply-file> <out-file>
  uv run python <kit>/build_prompts.py selftest   checks the reader-test split on a sample and on every committed reader reply
`control` reads skills/writing-plans/SKILL.md with `git show origin/main:` and writes that sha into the
prompt's first comment line and into the run directory's SOURCES.txt. A reader or adjudicator prompt
that holds `def test_` from outside the reader reply and the plan's tests, or a path of the copy or of
its source plan, is refused.
'''
import hashlib
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract import plan_tests, reader_inputs, split_tasks  # noqa: E402
from measure import reply  # noqa: E402
from plants import COPIES  # noqa: E402

KIT = Path(__file__).resolve().parent
REPO = KIT.parents[3]
COPIES_DIR = KIT.parent / 'copies'
PROMPTS = KIT / 'prompts'
SKILL_PATH = 'skills/writing-plans/SKILL.md'
FRONTMATTER_RE = re.compile(r'^---\n.*?\n---\n', re.S)
TESTS_RE = re.compile(r'<tests>(.*?)</tests>', re.S)
FLAG_RE = re.compile(r'<flag task="(\d+)">(.*?)</flag>', re.S)
TASK_TAG_RE = re.compile(r'^\s*#\s*task:\s*(\d+)', re.M)
UNIT_HEADER_RE = re.compile(r'(?:# spec:|# task:|@)')
DEF_START_RE = re.compile(r'^(?:async\s+def|def|class)\s', re.M)
TEST_START_RE = re.compile(r'^(?:async\s+def\s+test_|def\s+test_|class\s+Test)', re.M)
LEAK = 'def test_'
PLAN_STAND_IN = '<this plan>'


def git(*args: str) -> str:
    return subprocess.run(['git', *args], cwd=REPO, check=True, capture_output=True, text=True).stdout


def copy_files(copy_id: str) -> tuple[str, str]:
    '''The copy's spec and plan, checked against MANIFEST.txt.'''
    manifest = {}
    for line in (COPIES_DIR / 'MANIFEST.txt').read_text().split('\n'):
        if line.strip():
            digest, path, _origin = line.split('  ')
            manifest[path] = digest
    texts = []
    for name in ('spec.md', 'plan.md'):
        path = COPIES_DIR / copy_id / name
        text = path.read_text()
        if hashlib.sha256(text.encode('utf-8')).hexdigest() != manifest[str(path.relative_to(REPO))]:
            raise SystemExit(f'refusing: {path} differs from MANIFEST.txt')
        texts.append(text)
    return texts[0], texts[1]


def fill(template: str, **parts: str) -> str:
    text = (PROMPTS / template).read_text()
    for key, value in parts.items():
        text = text.replace(f'@@{key.upper()}@@', value)
    if '@@' in text:
        raise SystemExit(f'refusing: {template} has an unfilled marker')
    return text


def guard(text: str, copy_id: str, allowed: list[str]) -> None:
    copy = next(c for c in COPIES if c.id == copy_id)
    rest = text
    for part in allowed:
        rest = rest.replace(part, '')
    if LEAK in rest:
        raise SystemExit(f'refusing: the prompt holds {LEAK!r} from outside the reader reply and the plan tests')
    for path in (str((COPIES_DIR / copy_id).relative_to(REPO)), f'copies/{copy_id}', copy.plan_path):
        if path in text:
            raise SystemExit(f'refusing: the prompt names {path}')


def run_dir_of(out: Path) -> Path:
    return out.parent.parent if out.parent.name == 'prompts' else out.parent


def record(out: Path, lines: list[str]) -> None:
    sources = run_dir_of(out) / 'SOURCES.txt'
    have = sources.read_text().split('\n') if sources.exists() else []
    new = [line for line in lines if line not in have]
    if new:
        with sources.open('a') as f:
            f.write(''.join(f'{line}\n' for line in new))


def control(copy_id: str) -> tuple[str, list[str]]:
    spec, plan = copy_files(copy_id)
    sha = git('rev-parse', 'origin/main').strip()
    skill = FRONTMATTER_RE.sub('', git('show', f'{sha}:{SKILL_PATH}'), count=1).strip()
    source = f'<!-- writing-plans {SKILL_PATH} at origin/main {sha} -->'
    text = fill('control.txt', source=source, skill=skill, spec=spec.strip(), plan=plan.strip())
    return text, [f'writing-plans: {SKILL_PATH} at origin/main {sha}']


def redact(text: str, copy_id: str) -> str:
    '''Design 2 lets no prompt name a plan path: a Files list that names the plan itself reads <this plan>.'''
    return text.replace(f'`{next(c for c in COPIES if c.id == copy_id).plan_path}`', PLAN_STAND_IN)


def reader(copy_id: str) -> tuple[str, list[str]]:
    spec, plan = copy_files(copy_id)
    text = fill('reader.txt', spec=spec.strip(), inputs=redact(reader_inputs(plan).strip(), copy_id))
    guard(text, copy_id, [])
    return text, []


def top_level_chunks(tests: str) -> list[str]:
    '''Split the reader module where a top-level unit starts: at a `# spec:`, `# task:` or decorator line, or at a
    def or class line that no such line opens. So each test keeps its comment lines, decorators and body.'''
    chunks, current, in_header = [], [], False
    for line in tests.split('\n'):
        header, starts_def = UNIT_HEADER_RE.match(line), DEF_START_RE.match(line)
        if (header or starts_def) and not in_header:
            chunks.append('\n'.join(current))
            current = []
        current.append(line)
        if header:
            in_header = True
        elif starts_def:
            in_header = False
    chunks.append('\n'.join(current))
    return [chunk for chunk in chunks if chunk.strip()]


def split_reader_tests(tests: str) -> tuple[str, dict[int, list[str]], list[str]]:
    '''The reader module's preamble, its top-level chunks by `# task: N`, and the chunks with no task.'''
    chunks = top_level_chunks(tests)
    preamble, by_task, loose = [], {}, []
    for chunk in chunks:
        tag = TASK_TAG_RE.search(chunk)
        if tag:
            by_task.setdefault(int(tag.group(1)), []).append(chunk.strip('\n'))
        elif TEST_START_RE.search(chunk):
            loose.append(chunk.strip('\n'))
        else:
            preamble.append(chunk.strip('\n'))
    return '\n\n'.join(preamble), by_task, loose


def adjudicator(copy_id: str, reply_file: Path) -> tuple[str, list[str]]:
    spec, plan = copy_files(copy_id)
    answer = reply(reply_file)
    tests = TESTS_RE.search(answer or '')
    if not tests:
        raise SystemExit(f'refusing: {reply_file} is a VOID reader reply')
    preamble, by_task, loose = split_reader_tests(tests.group(1).strip('\n'))
    flags = {}
    for number, body in FLAG_RE.findall(answer):
        flags.setdefault(int(number), []).append(f'<flag>{body.strip()}</flag>')
    allowed, sections = [], []
    if preamble:
        allowed.append(preamble)
        sections.append(f'<acceptance-preamble>\n{preamble}\n</acceptance-preamble>')
    for task in split_tasks(plan):
        ours, theirs, flagged = plan_tests(task), by_task.get(task.number, []), flags.get(task.number, [])
        if not (ours or theirs or flagged):
            continue
        allowed += [ours, *theirs]
        part = [f'<task number="{task.number}" title="{task.title}">',
                f'<interfaces>\n{redact(task.interfaces, copy_id)}\n</interfaces>',
                f'<planner-tests>\n{ours}\n</planner-tests>',
                '<acceptance-tests>\n' + '\n\n'.join(theirs) + '\n</acceptance-tests>',
                '<acceptance-flags>\n' + '\n'.join(flagged) + '\n</acceptance-flags>',
                '</task>']
        sections.append('\n'.join(part))
    if loose:
        allowed += loose
        sections.append('<acceptance-tests-without-a-task>\n' + '\n\n'.join(loose)
                        + '\n</acceptance-tests-without-a-task>')
    text = fill('adjudicator.txt', spec=spec.strip(), tasks='\n\n'.join(sections))
    guard(text, copy_id, allowed)
    return text, [f'reader reply: {reply_file}']


SAMPLE_TESTS = '''import pytest

from pkg import mod

BODY = "def test_x(): pass"


# spec: "A sentence."
# task: 2
def test_one():
    assert mod.one() == 1


def _helper():
    return 2


# spec: "Another sentence."
# task: 3
@pytest.mark.parametrize(
    'value',
    [1, 2],
)
def test_two(value):
    assert _helper() == value


@pytest.fixture
def repo(tmp_path):
    return tmp_path'''
READER_REPLIES = ('reader-opus/*/rep[0-9]*.json', 'codex-gpt-6-sol/*/rep[0-9]*.md', 'codex-gpt-6.1-sol/*/rep[0-9]*.md')
MIN_READER_REPLIES = 60


def selftest() -> None:
    '''Each reader test stays whole under its task, and other top-level code goes to the preamble.'''
    preamble, by_task, loose = split_reader_tests(SAMPLE_TESTS)
    assert loose == [], loose
    assert by_task == {
        2: ['# spec: "A sentence."\n# task: 2\ndef test_one():\n    assert mod.one() == 1'],
        3: ['# spec: "Another sentence."\n# task: 3\n@pytest.mark.parametrize(\n    \'value\',\n    [1, 2],\n)\n'
            'def test_two(value):\n    assert _helper() == value'],
    }, by_task
    assert preamble == ('import pytest\n\nfrom pkg import mod\n\nBODY = "def test_x(): pass"\n\ndef _helper():\n    return 2\n\n'
                        '@pytest.fixture\ndef repo(tmp_path):\n    return tmp_path'), preamble
    checked = 0
    for pattern in READER_REPLIES:
        for path in sorted((KIT.parent / 'runs').glob(pattern)):
            tests = TESTS_RE.search(reply(path) or '').group(1).strip('\n')
            preamble, by_task, loose = split_reader_tests(tests)
            chunks = [chunk for task_chunks in by_task.values() for chunk in task_chunks]
            assert not loose, (path, loose[0][:200])
            assert all(len(DEF_START_RE.findall(chunk)) == 1 for chunk in chunks), path
            assert sum(len(TEST_START_RE.findall(chunk)) for chunk in chunks) == len(TEST_START_RE.findall(tests)), path
            assert '@pytest.mark.parametrize' not in preamble, path
            checked += 1
    assert checked >= MIN_READER_REPLIES, checked
    print('build_prompts selftest ok')


def main() -> None:
    args = sys.argv[1:]
    if args == ['selftest']:
        selftest()
        return
    if len(args) == 3 and args[0] in ('control', 'reader'):
        kind, copy_id, out = args
        text, sources = (control if kind == 'control' else reader)(copy_id)
    elif len(args) == 4 and args[0] == 'adjudicator':
        kind, copy_id, reply_file, out = args
        text, sources = adjudicator(copy_id, Path(reply_file))
    else:
        sys.exit(__doc__)
    copy = next(c for c in COPIES if c.id == copy_id)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    record(out, [f'copy: {copy_id} from {copy.commit} ({copy.plan_path}, {copy.spec_path})', *sources])
    print(f'wrote {out}: {len(text)} chars')


if __name__ == '__main__':
    main()
