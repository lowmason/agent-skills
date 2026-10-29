'''Tests for check_reviewer_block.py, the commit lint that keeps the four reviewer copies of the
shared block identical.'''
import pytest

from check_reviewer_block import FILES, BlockError, check, extract_block

BLOCK = ('## Review scope\n\nScope text.\n\n## Grades\n\n- **Critical:** bugs.\n\n'
         '## Declined to judge\n\nList text.\n')


def indented(text: str, pad: str = '    ') -> str:
    return '\n'.join(pad + line if line else '' for line in text.split('\n'))


def write_tree(root, files: dict[str, str]) -> None:
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def test_top_level_block_ends_at_the_next_heading():
    assert extract_block('# Agent\n\n' + BLOCK + '\n## Calibration\n\nOther.\n') == BLOCK


def test_indented_block_is_dedented_and_ends_at_the_fence():
    text = '```\n  prompt: |\n    Intro.\n\n' + indented(BLOCK) + '\n    ## Part 1\n```\n'
    assert extract_block(text) == BLOCK
    assert extract_block('```\n  prompt: |\n' + indented(BLOCK) + '\n```\n') == BLOCK


def test_identical_copies_pass(tmp_path):
    files = {name: BLOCK for name in FILES}
    files[FILES[3]] = '```\n  prompt: |\n' + indented(BLOCK) + '\n```\n'
    write_tree(tmp_path, files)
    assert check(tmp_path) == []


def test_trailing_space_in_one_copy_is_drift(tmp_path):
    files = {name: BLOCK for name in FILES}
    files[FILES[3]] = BLOCK.replace('Scope text.', 'Scope text. ')
    write_tree(tmp_path, files)
    problems = check(tmp_path)
    assert len(problems) == 1
    assert problems[0].startswith(f'{FILES[3]}: its reviewer block differs from {FILES[0]}')


def test_second_start_heading_is_refused():
    with pytest.raises(BlockError, match="expected one '## Review scope' line, found 2"):
        extract_block(BLOCK + '\n' + BLOCK)


def test_missing_block_names_the_file(tmp_path):
    files = {name: BLOCK for name in FILES}
    files[FILES[1]] = '# No block here\n'
    write_tree(tmp_path, files)
    assert check(tmp_path) == [f"{FILES[1]}: expected one '## Review scope' line, found 0"]


def test_repo_copies_are_identical():
    from check_reviewer_block import ROOT
    assert check(ROOT) == []
