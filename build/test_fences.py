'''Tests for fences.py. Stdlib + pytest only.'''
import fences


def test_extracts_a_simple_python_block():
    text = '# T\n\n```python\nx = 1\n```\n'
    blocks = fences.iter_code_blocks(text)
    assert len(blocks) == 1, blocks
    assert blocks[0].lang == 'python'
    assert blocks[0].code == 'x = 1\n'
    assert blocks[0].line == 3
    assert blocks[0].info == ''


def test_nested_python_fence_inside_markdown_fence_is_not_a_block():
    '''The trap check_frontmatter.py documents: a naive non-greedy regex closes
    on the FIRST ``` and reports the inner fence as real. skills/writing-plans/
    SKILL.md has exactly this shape, and its true python-block count is 0.'''
    text = '````markdown\n```python\nx = 1\n```\n````\n'
    assert fences.iter_code_blocks(text) == []


def test_info_suffix_is_captured():
    text = '```python norun needs dynamax\ny = 2\n```\n'
    blocks = fences.iter_code_blocks(text)
    assert blocks[0].info == 'norun needs dynamax', blocks


def test_py_alias_and_language_filter():
    text = '```py\na = 1\n```\n\n```bash\necho hi\n```\n'
    blocks = fences.iter_code_blocks(text)
    assert [b.lang for b in blocks] == ['py'], blocks


def test_strip_fenced_blocks_still_works():
    '''Moved verbatim from check_frontmatter.py; pinned here so the move is
    provably behaviour-preserving.'''
    assert fences.strip_fenced_blocks('a\n```\nb\n```\nc') == 'a\nc'
