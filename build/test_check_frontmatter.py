from pathlib import Path

from check_frontmatter import check_skill


def make_skill(tmp_path: Path, name: str, frontmatter: str) -> Path:
    d = tmp_path / name
    d.mkdir()
    (d / 'SKILL.md').write_text(f'---\n{frontmatter}\n---\n\n# Body\n')
    return d


def test_clean_skill_passes(tmp_path):
    d = make_skill(tmp_path, 'good-skill', 'name: good-skill\ndescription: Use when testing.')
    assert check_skill(d) == []


def test_broken_yaml_is_reported(tmp_path):
    d = make_skill(tmp_path, 'bad-yaml', 'name: bad-yaml\ndescription: x\nmetadata:\n  author: [A B](https://x)')
    errs = check_skill(d)
    assert len(errs) == 1 and 'not valid YAML' in errs[0]


def test_name_mismatch_and_overlong_description(tmp_path):
    d = make_skill(tmp_path, 'real-dir', "name: other-name\ndescription: '" + 'x' * 1100 + "'")
    errs = '\n'.join(check_skill(d))
    assert 'does not match directory' in errs
    assert '1024' in errs


def test_missing_relative_link_is_reported(tmp_path):
    d = make_skill(tmp_path, 'linky', 'name: linky\ndescription: x')
    (d / 'SKILL.md').write_text((d / 'SKILL.md').read_text() + '\nSee [guide](references/guide.md).\n')
    errs = '\n'.join(check_skill(d))
    assert 'references/guide.md' in errs


def test_nested_fences_do_not_leak_paths(tmp_path):
    d = make_skill(tmp_path, 'nested-fences', 'name: nested-fences\ndescription: x')
    (d / 'references').mkdir()
    (d / 'references' / 'real.md').write_text('# Real\n')
    body = (
        '\n'
        '````markdown\n'
        'Example teaching snippet:\n'
        '```bash\n'
        'run scripts/fake-tool and see [x](references/nope.md)\n'
        '```\n'
        'still inside the outer fence: see `scripts/leaky-tool`\n'
        '````\n'
        '\n'
        'See `references/real.md` for details.\n'
    )
    (d / 'SKILL.md').write_text((d / 'SKILL.md').read_text() + body)
    assert check_skill(d) == []


def test_nested_fences_still_report_real_missing_refs(tmp_path):
    d = make_skill(tmp_path, 'nested-fences-2', 'name: nested-fences-2\ndescription: x')
    body = (
        '\n'
        '````markdown\n'
        'Example teaching snippet:\n'
        '```bash\n'
        'run scripts/fake-tool and see [x](references/nope.md)\n'
        '```\n'
        'still inside the outer fence: see `scripts/leaky-tool`\n'
        '````\n'
        '\n'
        'See `references/missing.md` for details.\n'
    )
    (d / 'SKILL.md').write_text((d / 'SKILL.md').read_text() + body)
    errs = '\n'.join(check_skill(d))
    assert 'references/missing.md' in errs
    assert 'references/nope.md' not in errs
    assert 'scripts/fake-tool' not in errs
    assert 'scripts/leaky-tool' not in errs


def test_real_repo_is_clean():
    repo = Path(__file__).resolve().parent.parent
    dirty = [e for d in sorted(repo.iterdir())
             if d.is_dir() and (d / 'SKILL.md').exists()
             for e in check_skill(d)]
    assert dirty == [], dirty
