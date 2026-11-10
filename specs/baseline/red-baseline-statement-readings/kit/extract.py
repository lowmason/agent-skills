'''Split a plan into tasks, fence-aware, and build the second reader's inputs (plan 81).

Usage, from the repository root:
  uv run python <kit>/extract.py selftest
A line-by-line scan tracks code fences (``` and ~~~, three or more, any indent). A heading, a task
title or a **Files:** or **Interfaces:** marker inside a fence is text.
'''
import re
import sys
from dataclasses import dataclass

FENCE_RE = re.compile(r'^\s*(`{3,}|~{3,})(.*)$')
TASK_RE = re.compile(r'^### Task (\d+): (.*)$')
SECTION_RE = re.compile(r'^## (.*)$')
TEST_MARKERS = ('def test_', '@pytest')
FILES_MARKER = '**Files:**'
INTERFACES_MARKER = '**Interfaces:**'
TECH_STACK_MARKER = '**Tech Stack:**'


@dataclass(frozen=True)
class Task:
    number: int
    title: str
    files: str
    interfaces: str
    body: str


@dataclass(frozen=True)
class _Fence:
    start: int   # 0-based index of the opening fence line
    end: int     # 0-based index of the closing fence line (the last line when unclosed)

    def holds_test(self, lines: list[str]) -> bool:
        text = '\n'.join(lines[self.start:self.end + 1])
        return any(marker in text for marker in TEST_MARKERS)


@dataclass(frozen=True)
class _Span:
    number: int
    title: str
    start: int   # the '### Task' line
    end: int     # exclusive
    files: tuple[int, int] | None
    interfaces: tuple[int, int] | None


def _fences(lines: list[str]) -> list[_Fence]:
    fences, opener, start = [], None, 0
    for i, line in enumerate(lines):
        match = FENCE_RE.match(line)
        if opener is None:
            if match:
                opener, start = match.group(1), i
        elif match and match.group(1)[0] == opener[0] and len(match.group(1)) >= len(opener) \
                and not match.group(2).strip():
            fences.append(_Fence(start, i))
            opener = None
    if opener is not None:
        fences.append(_Fence(start, len(lines) - 1))
    return fences


def _fence_at(fences: list[_Fence], i: int) -> _Fence | None:
    return next((f for f in fences if f.start <= i <= f.end), None)


def _block(lines: list[str], fences: list[_Fence], start: int, end: int) -> tuple[int, int]:
    '''The marker line at `start` and the list that follows it: list items, indented lines (fenced
    ones included), and blank lines. It ends at a step, a heading, another marker or a paragraph.'''
    i = start + 1
    while i < end:
        fence = _fence_at(fences, i)
        line = lines[i]
        if fence and line[:1].isspace():
            i = fence.end + 1
            continue
        if fence or line.startswith(('- [ ]', '#', '**')) or line.strip() == '---':
            break
        if line.strip() and not (line.startswith(('- ', '* ')) or line[:1].isspace()):
            break
        i += 1
    while i > start + 1 and not lines[i - 1].strip():
        i -= 1
    return start, i


def _spans(plan: str) -> tuple[list[str], list[_Fence], list[_Span]]:
    lines = plan.split('\n')
    fences = _fences(lines)
    heads = []
    for i, line in enumerate(lines):
        if _fence_at(fences, i):
            continue
        match = TASK_RE.match(line)
        if match:
            heads.append((i, int(match.group(1)), match.group(2)))
        elif SECTION_RE.match(line):
            heads.append((i, None, None))
    spans = []
    for k, (start, number, title) in enumerate(heads):
        if number is None:
            continue
        end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        files = interfaces = None
        for i in range(start + 1, end):
            if _fence_at(fences, i):
                continue
            if lines[i].startswith(FILES_MARKER) and files is None:
                files = _block(lines, fences, i, end)
            elif lines[i].startswith(INTERFACES_MARKER) and interfaces is None:
                interfaces = _block(lines, fences, i, end)
        spans.append(_Span(number, title, start, end, files, interfaces))
    return lines, fences, spans


def _reader_text(lines: list[str], fences: list[_Fence], block: tuple[int, int] | None) -> str:
    '''A Files list or an Interfaces block with every fenced test block left out.'''
    if block is None:
        return ''
    kept, i = [], block[0]
    while i < block[1]:
        fence = _fence_at(fences, i)
        if fence and fence.holds_test(lines):
            i = fence.end + 1
            continue
        kept.append(lines[i])
        i += 1
    return '\n'.join(kept)


def _raw(lines: list[str], block: tuple[int, int] | None) -> str:
    return '' if block is None else '\n'.join(lines[block[0]:block[1]])


def split_tasks(plan: str) -> list[Task]:
    lines, _fences_, spans = _spans(plan)
    return [Task(s.number, s.title, _raw(lines, s.files), _raw(lines, s.interfaces),
                 '\n'.join(lines[s.start:s.end])) for s in spans]


def tech_stack(plan: str) -> str:
    lines = plan.split('\n')
    fences = _fences(lines)
    for i, line in enumerate(lines):
        if line.startswith(TECH_STACK_MARKER) and not _fence_at(fences, i):
            j = i + 1
            while j < len(lines) and lines[j].strip():
                j += 1
            return '\n'.join(lines[i:j])
    raise ValueError('the plan has no **Tech Stack:** line')


def reader_inputs(plan: str) -> str:
    '''The Tech Stack line, then for each task its title, its Files list and its Interfaces block.'''
    lines, fences, spans = _spans(plan)
    parts = [tech_stack(plan)]
    for s in spans:
        part = [lines[s.start]]
        for block in (s.files, s.interfaces):
            text = _reader_text(lines, fences, block)
            if text:
                part.append(text)
        parts.append('\n\n'.join(part))
    return '\n\n'.join(parts) + '\n'


def plan_tests(task: Task) -> str:
    '''The task's fenced blocks that hold `def test_` or `@pytest`, in order.'''
    lines = task.body.split('\n')
    blocks = [f for f in _fences(lines) if f.holds_test(lines)]
    return '\n\n'.join('\n'.join(lines[f.start:f.end + 1]) for f in blocks)


def _slug(heading: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', heading.lower()).strip('-')


def section_of(plan: str, line: int) -> str:
    '''The section that holds 1-based `line`: a task's `files`, `interfaces`, `test-step` (a fenced
    block that holds a test), `code-step` (any other fenced block) or `step-text`; outside tasks,
    the slug of the `## ` heading above it, or `header` before the first.'''
    lines, fences, spans = _spans(plan)
    i = line - 1
    for s in spans:
        if not s.start <= i < s.end:
            continue
        for name, block in (('files', s.files), ('interfaces', s.interfaces)):
            if block and block[0] <= i < block[1]:
                return name
        fence = _fence_at(fences, i)
        if fence:
            return 'test-step' if fence.holds_test(lines) else 'code-step'
        return 'step-text'
    heading = 'header'
    for k in range(i, -1, -1):
        match = SECTION_RE.match(lines[k])
        if match and not _fence_at(fences, k):
            heading = _slug(match.group(1))
            break
    return heading


SAMPLE = '''# Sample Plan

**Goal:** A sample.

**Tech Stack:** Python 3.13, pytest.

## Global Constraints

- The cap is 7 (spec R1).

### Task 1: First

**Files:**
- Create: `pkg/a.py`

**Interfaces:**
- Produces: `cap() -> int`.
  ```python
  ## A heading inside a fence
  def test_inside():
      assert cap() == 7
  ### Task 9: not a task
  ```

The approach: count the cap.

- [ ] **Step 1: Write the failing test**

```python
def test_cap_is_seven():
    assert cap() == 7
```

- [ ] **Step 2: Implement**

```python
def cap():
    return 7
```

### Task 2: Second

**Files:**
- Modify: `pkg/a.py`

**Interfaces:**
- Consumes: `cap`.

- [ ] **Step 1: Do it**

## Review Focus

1. The cap.
'''
GC_LINE = 9        # '- The cap is 7 (spec R1).'
IFACE_LINE = 17    # '- Produces: `cap() -> int`.'
TEST_LINE = 31     # '    assert cap() == 7' in Step 1's fence
CODE_LINE = 38     # '    return 7' in Step 2's fence


def selftest() -> None:
    lines = SAMPLE.split('\n')
    assert lines[GC_LINE - 1] == '- The cap is 7 (spec R1).'
    assert lines[IFACE_LINE - 1] == '- Produces: `cap() -> int`.'
    assert lines[TEST_LINE - 1] == '    assert cap() == 7'
    assert lines[CODE_LINE - 1] == '    return 7'
    tasks = split_tasks(SAMPLE)
    assert [t.number for t in tasks] == [1, 2]            # a fenced '### Task' line splits nothing
    assert 'def test_' not in reader_inputs(SAMPLE)
    assert 'def test_inside' in plan_tests(tasks[0])
    assert section_of(SAMPLE, GC_LINE) == 'global-constraints'
    assert section_of(SAMPLE, IFACE_LINE) == 'interfaces'
    assert section_of(SAMPLE, TEST_LINE) == 'test-step'   # a fenced block that holds 'def test_'
    assert section_of(SAMPLE, CODE_LINE) == 'code-step'   # any other block inside a task step
    print('extract selftest ok')


if __name__ == '__main__':
    if sys.argv[1:] == ['selftest']:
        selftest()
    else:
        sys.exit(__doc__)
