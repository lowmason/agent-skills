from pathlib import Path

from check_frontmatter import check_skill, check_agent_file, check_command_file, REPO


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
    dirty = [e for d in sorted((repo / 'skills').iterdir())
             if d.is_dir() and (d / 'SKILL.md').exists()
             for e in check_skill(d)]
    assert dirty == [], dirty


def test_agent_file_checked(tmp_path):
    bad = tmp_path / 'my-agent.md'
    bad.write_text('---\nname: other-name\ndescription: x\ntools: Read, Bogus\n---\nbody\n')
    errs = check_agent_file(bad)
    assert any('does not match filename' in e for e in errs)
    assert any('unknown tools' in e for e in errs)


def test_agent_file_clean(tmp_path):
    good = tmp_path / 'my-agent.md'
    good.write_text('---\nname: my-agent\ndescription: Reviews things.\ntools: Read, Grep, Glob, Bash\n---\nbody\n')
    assert check_agent_file(good) == []


def test_command_file_requires_description(tmp_path):
    bad = tmp_path / 'do-thing.md'
    bad.write_text('---\nother: x\n---\nbody\n')
    errs = check_command_file(bad)
    assert any('missing description' in e for e in errs)


def test_command_file_requires_disable_model_invocation(tmp_path):
    # Every command must opt out of auto-invocation — that is what keeps commands off the
    # skill-listing budget. Only the YAML boolean counts: a quoted 'true' is a string.
    missing = tmp_path / 'missing.md'
    missing.write_text('---\ndescription: Does a thing.\n---\nbody\n')
    assert any('disable-model-invocation' in e for e in check_command_file(missing))
    quoted = tmp_path / 'quoted.md'
    quoted.write_text("---\ndescription: Does a thing.\ndisable-model-invocation: 'true'\n---\nbody\n")
    assert any('disable-model-invocation' in e for e in check_command_file(quoted))
    good = tmp_path / 'good.md'
    good.write_text('---\ndescription: Does a thing.\ndisable-model-invocation: true\n---\nbody\n')
    assert check_command_file(good) == []


def test_real_agents_and_commands_are_clean():
    errs = []
    for md in sorted((REPO / 'agents').glob('*.md')):
        errs += check_agent_file(md)
    for md in sorted((REPO / 'commands').glob('*.md')):
        errs += check_command_file(md)
    assert errs == []


def test_model_and_effort_keys_allowed(tmp_path):
    d = make_skill(
        tmp_path,
        'pinned-skill',
        'name: pinned-skill\ndescription: Use when testing pins.\nmodel: haiku\neffort: xhigh',
    )
    assert check_skill(d) == []


def test_unknown_frontmatter_key_still_rejected(tmp_path):
    d = make_skill(
        tmp_path,
        'bogus-skill',
        'name: bogus-skill\ndescription: Use when testing.\nbogus-key: nope',
    )
    errs = '\n'.join(check_skill(d))
    assert "unknown frontmatter key 'bogus-key'" in errs


def test_agent_name_case_differs_from_filename_is_allowed(tmp_path):
    # The Explore override: lowercase filename, capitalized frontmatter
    # name (Claude Code resolves agent types by the name field alone,
    # case-sensitively — the capital E is what shadows the built-in).
    good = tmp_path / 'explore.md'
    good.write_text(
        '---\nname: Explore\ndescription: Search agent.\n'
        'tools: Read, Grep, Glob, Bash\n---\nbody\n'
    )
    assert check_agent_file(good) == []
