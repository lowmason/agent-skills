import re
import subprocess
import sys
from pathlib import Path

import yaml

from check_frontmatter import (
    bundled_invocations,
    check_agent_file,
    check_invocations,
    check_script_headers,
    check_command_file,
    check_pinned_roster,
    check_readonly_roster,
    check_skill,
    load_readonly_roster,
    skill_body_warning,
    strict_violations,
    READONLY_HEADING,
    REPO,
)


def make_skill(tmp_path: Path, name: str, frontmatter: str, *, licensed: bool = True) -> Path:
    '''A skill directory with this frontmatter. Every SKILL.md needs a license
    (portability R1.4), so one is added unless the frontmatter sets its own or
    the test passes licensed=False.'''
    d = tmp_path / name
    d.mkdir()
    if licensed and not re.search(r'^license:', frontmatter, re.M):
        frontmatter = f'license: MIT\n{frontmatter}'
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


def test_agent_tools_accept_agent_restrictions_and_mcp_tools(tmp_path):
    md = tmp_path / 'lead.md'
    md.write_text('---\nname: lead\ndescription: Leads.\n'
                  'tools: Read, Agent(worker, researcher), Agent, mcp__github__search_code\n---\nbody\n')
    assert check_agent_file(md) == []


def test_agent_tools_accept_a_yaml_list(tmp_path):
    md = tmp_path / 'lead.md'
    md.write_text('---\nname: lead\ndescription: Leads.\ntools: [Read, Grep]\n---\nbody\n')
    assert check_agent_file(md) == []


def test_agent_tools_in_a_yaml_list_still_flag_an_unknown_tool(tmp_path):
    md = tmp_path / 'lead.md'
    md.write_text('---\nname: lead\ndescription: Leads.\ntools: [Read, Bogus]\n---\nbody\n')
    assert check_agent_file(md) == [f"{md}: unknown tools ['Bogus']"]


def test_agent_tools_still_flag_an_unknown_tool_beside_an_agent_restriction(tmp_path):
    md = tmp_path / 'lead.md'
    md.write_text('---\nname: lead\ndescription: Leads.\ntools: Agent(worker, researcher), Bogus\n---\nbody\n')
    assert check_agent_file(md) == [f"{md}: unknown tools ['Bogus']"]


def test_compatibility_key_allowed(tmp_path):
    d = make_skill(tmp_path, 'compat-skill',
                   'name: compat-skill\ndescription: Use when testing.\ncompatibility: Requires Python 3.13')
    assert check_skill(d) == []


def test_spec_and_host_keys_are_allowed(tmp_path):
    # Portability R1.1: the spec's six fields and the host extensions this repo
    # allows. disable-model-invocation is false here: true needs Codex's policy
    # file (R1.6), which a later test covers.
    d = make_skill(tmp_path, 'keyed-skill',
                   'name: keyed-skill\ndescription: Use when testing.\nlicense: MIT\n'
                   'compatibility: Requires uv.\nmetadata:\n  author: Someone\nallowed-tools: Read\n'
                   'when_to_use: Testing.\ncontext: fork\nagent: Explore\n'
                   'disable-model-invocation: false')
    assert check_skill(d) == []


def test_license_is_required(tmp_path):
    # Portability R1.4: repo policy, beyond the spec, so a single-skill install
    # still says how the skill is licensed.
    msg = 'license is required, a non-empty string (repo policy, beyond the Agent Skills spec)'
    missing = make_skill(tmp_path, 'no-license', 'name: no-license\ndescription: Use when testing.',
                         licensed=False)
    assert check_skill(missing) == [f"{missing / 'SKILL.md'}: {msg}"]
    blank = make_skill(tmp_path, 'blank-license',
                       "name: blank-license\ndescription: Use when testing.\nlicense: ' '")
    assert check_skill(blank) == [f"{blank / 'SKILL.md'}: {msg}"]


def test_metadata_must_map_strings_to_strings(tmp_path):
    # Portability R1.2. An unquoted version: 1.0 parses as a float.
    d = make_skill(tmp_path, 'meta-skill',
                   'name: meta-skill\ndescription: Use when testing.\nmetadata:\n  version: 1.0')
    assert check_skill(d) == [
        f"{d / 'SKILL.md'}: metadata must map strings to strings (quote a value such as version: \"1.0\")"]
    listed = make_skill(tmp_path, 'meta-list',
                        'name: meta-list\ndescription: Use when testing.\nmetadata: [a, b]')
    assert len(check_skill(listed)) == 1


def test_compatibility_must_be_a_string_of_1_to_500_characters(tmp_path):
    # Portability R1.3, both edges: 500 passes, 501 and a blank value fail.
    ok = make_skill(tmp_path, 'compat-ok',
                    "name: compat-ok\ndescription: Use when testing.\ncompatibility: '" + 'x' * 500 + "'")
    assert check_skill(ok) == []
    msg = 'compatibility must be a string of 1-500 characters'
    for i, value in enumerate(["'" + 'x' * 501 + "'", "'   '", '42']):
        d = make_skill(tmp_path, f'compat-bad-{i}',
                       f'name: compat-bad-{i}\ndescription: Use when testing.\ncompatibility: {value}')
        assert check_skill(d) == [f"{d / 'SKILL.md'}: {msg}"], value


def test_angle_brackets_in_a_description_are_rejected(tmp_path):
    # Portability R1.5: claude.ai rejects < and > in name and description.
    d = make_skill(tmp_path, 'angle-skill',
                   "name: angle-skill\ndescription: \"Use when asked to 'verify <page>'.\"")
    assert check_skill(d) == [f"{d / 'SKILL.md'}: description contains < or >"]


def _skill_with_dmi(tmp_path: Path, name: str, dmi: str, policy: str | None = None) -> Path:
    '''A skill setting disable-model-invocation, optionally with Codex's policy file.'''
    d = make_skill(tmp_path, name,
                   f'name: {name}\ndescription: Use when testing.\ndisable-model-invocation: {dmi}')
    if policy is not None:
        (d / 'agents').mkdir()
        (d / 'agents' / 'openai.yaml').write_text(policy)
    return d


FORBID_IMPLICIT = 'policy:\n  allow_implicit_invocation: false\n'


def test_disable_model_invocation_must_be_a_yaml_boolean(tmp_path):
    # Portability R1.6: a quoted 'true' is a string, which disables nothing.
    d = _skill_with_dmi(tmp_path, 'quoted-dmi', "'true'")
    assert check_skill(d) == [f"{d / 'SKILL.md'}: disable-model-invocation must be a YAML boolean, got 'true'"]


def test_a_manual_only_skill_needs_the_codex_policy_file(tmp_path):
    d = _skill_with_dmi(tmp_path, 'manual-skill', 'true')
    assert check_skill(d) == [
        f"{d / 'SKILL.md'}: disable-model-invocation: true needs agents/openai.yaml with "
        'policy.allow_implicit_invocation: false, so Codex keeps the skill manual-only too']


def test_a_manual_only_skill_with_the_codex_policy_passes(tmp_path):
    assert check_skill(_skill_with_dmi(tmp_path, 'paired-skill', 'true', FORBID_IMPLICIT)) == []


def test_the_codex_policy_must_forbid_implicit_invocation(tmp_path):
    d = _skill_with_dmi(tmp_path, 'loose-skill', 'true', 'policy:\n  allow_implicit_invocation: true\n')
    assert check_skill(d) == [
        f"{d / 'agents' / 'openai.yaml'}: must set policy.allow_implicit_invocation: false, "
        'because SKILL.md sets disable-model-invocation: true']


def test_a_codex_manual_only_skill_needs_disable_model_invocation(tmp_path):
    # The converse: manual-only in Codex but still auto-invoked by Claude Code.
    d = _skill_with_dmi(tmp_path, 'codex-only', 'false', FORBID_IMPLICIT)
    assert check_skill(d) == [
        f"{d / 'SKILL.md'}: agents/openai.yaml sets policy.allow_implicit_invocation: false, "
        'so disable-model-invocation must be true']


def test_an_unparseable_codex_policy_is_reported(tmp_path):
    d = _skill_with_dmi(tmp_path, 'broken-policy', 'true', 'policy: [unclosed\n')
    errs = check_skill(d)
    assert len(errs) == 1 and 'agents/openai.yaml: does not parse as YAML' in errs[0], errs


def test_an_unparseable_codex_policy_is_reported_beside_a_non_boolean_flag(tmp_path):
    # A non-boolean disable-model-invocation does not hide a broken policy file.
    # The parity check needs a boolean, so a parseable policy adds nothing.
    d = _skill_with_dmi(tmp_path, 'quoted-broken', "'true'", 'policy: [unclosed\n')
    errs = check_skill(d)
    assert len(errs) == 2, errs
    assert errs[0] == f"{d / 'SKILL.md'}: disable-model-invocation must be a YAML boolean, got 'true'"
    assert 'agents/openai.yaml: does not parse as YAML' in errs[1], errs
    paired = _skill_with_dmi(tmp_path, 'quoted-paired', "'true'", FORBID_IMPLICIT)
    assert check_skill(paired) == [
        f"{paired / 'SKILL.md'}: disable-model-invocation must be a YAML boolean, got 'true'"]


def _skill_with_body_lines(tmp_path: Path, name: str, extra: int) -> Path:
    '''make_skill's body is two lines (a blank line and "# Body"); add extra lines.'''
    d = make_skill(tmp_path, name, f'name: {name}\ndescription: Use when testing.')
    (d / 'SKILL.md').write_text((d / 'SKILL.md').read_text() + 'line\n' * extra)
    return d


def test_a_body_over_500_lines_warns_without_an_error(tmp_path):
    # Portability R1.7: an advisory, so check_skill (the errors) stays clean.
    at_limit = _skill_with_body_lines(tmp_path, 'at-limit', 498)
    over = _skill_with_body_lines(tmp_path, 'over-limit', 499)
    assert skill_body_warning(at_limit) is None
    assert skill_body_warning(over) == (
        f"WARN {over / 'SKILL.md'}: body is 501 lines; the guide keeps a SKILL.md body under 500")
    assert check_skill(over) == []


def test_the_body_warning_goes_to_stderr_and_keeps_exit_zero():
    # writing-skills is the one body over 500 lines (portability baseline);
    # revisit this test when it is split, a portability deferred item.
    result = subprocess.run([sys.executable, str(REPO / 'build' / 'check_frontmatter.py')],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout
    assert 'WARN' not in result.stdout
    assert any(line.startswith('WARN ') and 'skills/writing-skills/SKILL.md: body is' in line
               for line in result.stderr.splitlines()), result.stderr


def test_strict_flags_host_keys_and_reserved_name_words(tmp_path):
    # Portability R1.8: the keys pass the default gate and fail --strict.
    hosted = make_skill(tmp_path, 'hosted',
                        'name: hosted\ndescription: Use when testing.\neffort: xhigh\ncontext: fork')
    assert check_skill(hosted) == []
    note = 'is a Claude Code extension, not an Agent Skills spec key (--strict)'
    assert strict_violations(hosted) == [f"{hosted / 'SKILL.md'}: 'context' {note}",
                                         f"{hosted / 'SKILL.md'}: 'effort' {note}"]
    named = make_skill(tmp_path, 'claude-helper', 'name: claude-helper\ndescription: Use when testing.')
    assert strict_violations(named) == [
        f"{named / 'SKILL.md'}: name contains the reserved word 'claude' (--strict)"]
    plain = make_skill(tmp_path, 'plain', 'name: plain\ndescription: Use when testing.')
    assert strict_violations(plain) == []


def test_strict_is_off_by_default_and_on_with_the_flag():
    # The default gate stays green; --strict adds only its own SKILL.md lines.
    script = str(REPO / 'build' / 'check_frontmatter.py')
    default = subprocess.run([sys.executable, script], capture_output=True, text=True)
    strict = subprocess.run([sys.executable, script, '--strict'], capture_output=True, text=True)
    assert default.returncode == 0, default.stdout
    assert strict.returncode == 1, strict.stdout
    lines = strict.stdout.splitlines()
    assert lines and all(line.endswith('(--strict)') and '/SKILL.md: ' in line for line in lines), lines


def _skill_with_script(tmp_path: Path, name: str, script: str, filename: str = 'tool.py') -> Path:
    d = make_skill(tmp_path, name, f'name: {name}\ndescription: Use when testing.')
    (d / 'scripts').mkdir()
    (d / 'scripts' / filename).write_text(script)
    return d


HEADER = "#!/usr/bin/env python3\n# /// script\n# requires-python = '>=3.11'\n# dependencies = []\n# ///\n"
MAIN_GUARD = "\nif __name__ == '__main__':\n    pass\n"


def test_a_runnable_script_needs_a_pep723_block(tmp_path):
    # Portability R3.7: a scripts/*.py with a __main__ guard is runnable.
    d = _skill_with_script(tmp_path, 'bare-script', 'import json\n' + MAIN_GUARD)
    assert check_skill(d) == [
        f"{d / 'scripts' / 'tool.py'}: a runnable script needs a PEP 723 script block, "
        'so uv run can build its environment']


def test_a_script_without_a_main_guard_is_a_library(tmp_path):
    # Like tune-hyperparameters' time_series_cv.py: imported, never run (R3.1).
    assert check_skill(_skill_with_script(tmp_path, 'library-script', 'import numpy\n')) == []


def test_the_block_needs_requires_python_and_dependencies(tmp_path):
    no_deps = _skill_with_script(tmp_path, 'no-deps', "# /// script\n# requires-python = '>=3.11'\n# ///\n" + MAIN_GUARD)
    assert check_skill(no_deps) == [
        f"{no_deps / 'scripts' / 'tool.py'}: the PEP 723 block needs a dependencies list ([] for a stdlib-only script)"]
    no_floor = _skill_with_script(tmp_path, 'no-floor', '# /// script\n# dependencies = []\n# ///\n' + MAIN_GUARD)
    assert check_skill(no_floor) == [f"{no_floor / 'scripts' / 'tool.py'}: the PEP 723 block needs requires-python"]


def test_an_unparseable_block_is_reported(tmp_path):
    d = _skill_with_script(tmp_path, 'bad-toml', '# /// script\n# dependencies = [\n# ///\n' + MAIN_GUARD)
    errs = check_skill(d)
    assert len(errs) == 1 and 'the PEP 723 script block does not parse' in errs[0], errs


def test_a_script_that_does_not_parse_is_one_error_not_a_traceback(tmp_path):
    # HEADER is five lines, so the broken def is line 6.
    d = _skill_with_script(tmp_path, 'bad-python', HEADER + 'def broken(:\n' + MAIN_GUARD)
    errs = check_skill(d)
    assert len(errs) == 1, errs
    assert re.fullmatch(rf"{re.escape(str(d / 'scripts' / 'tool.py'))}: does not parse as Python \(.+, line 6\)",
                        errs[0]), errs


def test_every_third_party_import_is_declared(tmp_path):
    # A function-level import counts; the stdlib and a sibling module need nothing.
    body = 'import json\nimport helper\n\ndef read():\n    import polars as pl\n    return pl\n' + MAIN_GUARD
    d = _skill_with_script(tmp_path, 'undeclared', HEADER + body)
    (d / 'scripts' / 'helper.py').write_text('')
    assert check_skill(d) == [
        f"{d / 'scripts' / 'tool.py'}: imports polars, which its PEP 723 dependencies do not declare"]
    declared = HEADER.replace('dependencies = []', "dependencies = ['polars>=2.0']")
    d2 = _skill_with_script(tmp_path, 'declared', declared + body)
    (d2 / 'scripts' / 'helper.py').write_text('')
    assert check_skill(d2) == []


def test_import_names_map_to_distribution_names(tmp_path):
    # yaml ships as PyYAML (the alias table); arviz_base matches arviz-base once
    # both are normalized.
    header = HEADER.replace('dependencies = []', "dependencies = ['PyYAML>=6.0', 'arviz-base>=1.0']")
    script = header + 'import yaml\nfrom arviz_base import from_dict\n' + MAIN_GUARD
    assert check_skill(_skill_with_script(tmp_path, 'aliased', script)) == []
    missing = _skill_with_script(tmp_path, 'alias-missing', HEADER + 'import yaml\n' + MAIN_GUARD)
    assert check_skill(missing) == [
        f"{missing / 'scripts' / 'tool.py'}: imports yaml, which its PEP 723 dependencies do not declare (as pyyaml)"]


def test_an_import_guarded_by_import_error_is_optional(tmp_path):
    # Portability R3.4's exemption: the script runs without it.
    body = 'try:\n    import arviz_stats\nexcept (ImportError, ValueError):\n    arviz_stats = None\n' + MAIN_GUARD
    assert check_skill(_skill_with_script(tmp_path, 'optional', HEADER + body)) == []


def test_a_vendored_script_is_exempt_from_the_header_rules(tmp_path):
    d = _skill_with_script(tmp_path, 'vendored', 'import json\n' + MAIN_GUARD, filename='upstream.py')
    assert check_script_headers(d, vendored=frozenset({'skills/vendored/scripts/upstream.py'})) == []
    assert len(check_script_headers(d)) == 1


RUNNABLE = HEADER + MAIN_GUARD


def _skill_running(tmp_path: Path, name: str, body: str, md: str = 'SKILL.md') -> Path:
    '''A skill with a runnable scripts/tool.py, whose markdown file md holds body.'''
    d = _skill_with_script(tmp_path, name, RUNNABLE)
    path = d / md
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text((path.read_text() if path.exists() else '') + body)
    return d


def test_python_before_a_bundled_script_is_flagged(tmp_path):
    # Portability R3.5, R3.7: uv run <path> reads the header; python does not.
    d = _skill_running(tmp_path, 'bare', '```bash\npython <this-skill-dir>/scripts/tool.py --x 1\n```\n')
    assert check_invocations(d) == [
        f"{d / 'SKILL.md'}: runs <this-skill-dir>/scripts/tool.py with python; "
        "use uv run <this-skill-dir>/scripts/tool.py, which reads the script's PEP 723 header"]


def test_python3_and_uv_run_python_are_flagged_too(tmp_path):
    # uv run ... python <path> runs the project environment, not the header's.
    body = ('Run `python3 scripts/tool.py`, or\n'
            '`uv run --with polars python <this-skill-dir>/scripts/tool.py`.\n')
    runners = [runner for _, runner, _ in bundled_invocations(_skill_running(tmp_path, 'forms', body))]
    assert runners == ['python3', 'python']


def test_a_line_continued_invocation_is_joined_first(tmp_path):
    d = _skill_running(tmp_path, 'continued', '```bash\npython \\\n    <this-skill-dir>/scripts/tool.py \\\n    --x 1\n```\n')
    assert [runner for _, runner, _ in bundled_invocations(d)] == ['python']


def test_uv_run_of_a_bundled_script_passes(tmp_path):
    d = _skill_running(tmp_path, 'uv-form', '```bash\nuv run <this-skill-dir>/scripts/tool.py --x 1\n```\n')
    assert check_invocations(d) == []
    assert bundled_invocations(d) == [(d / 'SKILL.md', 'uv run', '<this-skill-dir>/scripts/tool.py')]


def test_a_path_that_is_no_runnable_bundled_script_is_not_flagged(tmp_path):
    # A teaching example (no such file) and a library (no __main__ guard).
    d = _skill_running(tmp_path, 'examples', 'Run `python scripts/migrate.py`, then `python scripts/lib.py`.\n')
    (d / 'scripts' / 'lib.py').write_text('X = 1\n')
    assert bundled_invocations(d) == []


def test_paths_resolve_across_skills_aliases_and_references(tmp_path):
    # The R3.5 path forms: a sibling skill, the llm-wiki install root, a clone
    # path, a repo-relative path, and an invocation in references/.
    other = _skill_with_script(tmp_path, 'other', RUNNABLE)
    wiki = _skill_with_script(tmp_path, 'llm-wiki', RUNNABLE, filename='lint_wiki.py')
    body = ('`python <this-skill-dir>/../other/scripts/tool.py`\n'
            '`python3 "$LLM_WIKI_ROOT/scripts/lint_wiki.py"`\n'
            '`python3 ~/Projects/agent-skills/skills/other/scripts/tool.py`\n')
    d = _skill_running(tmp_path, 'caller', body)
    (d / 'references').mkdir()
    (d / 'references' / 'usage.md').write_text('`python skills/other/scripts/tool.py`\n')
    assert [(md.name, path) for md, _, path in bundled_invocations(d)] == [
        ('SKILL.md', '<this-skill-dir>/../other/scripts/tool.py'),
        ('SKILL.md', '$LLM_WIKI_ROOT/scripts/lint_wiki.py'),
        ('SKILL.md', '~/Projects/agent-skills/skills/other/scripts/tool.py'),
        ('usage.md', 'skills/other/scripts/tool.py')]
    assert other.is_dir() and wiki.is_dir()


def test_a_vendored_script_run_with_python3_passes(tmp_path):
    # Owner decision D11: a vendored copy cannot carry a header, so its
    # documented python3 call stays and the invocation rule skips it.
    d = _skill_running(tmp_path, 'vendored-run', '```bash\npython3 <this-skill-dir>/scripts/tool.py\n```\n')
    assert check_invocations(d, vendored=frozenset({'skills/vendored-run/scripts/tool.py'})) == []
    assert len(check_invocations(d)) == 1


UV_COMPATIBILITY = 'Requires uv to run bundled scripts (dependencies are declared inline); Python 3.11+.'


def _uv_skill(tmp_path: Path, name: str, extra: str = '') -> Path:
    '''A skill whose SKILL.md runs its bundled scripts/tool.py with uv run.'''
    d = make_skill(tmp_path, name, f'name: {name}\ndescription: Use when testing.{extra}')
    (d / 'scripts').mkdir()
    (d / 'scripts' / 'tool.py').write_text(RUNNABLE)
    with (d / 'SKILL.md').open('a') as f:
        f.write('```bash\nuv run <this-skill-dir>/scripts/tool.py\n```\n')
    return d


def test_a_uv_run_invocation_needs_compatibility_naming_uv(tmp_path):
    # Portability R3.6-R3.7. uv must be a word: cuvid does not name it.
    for name, extra in (('no-compat', ''), ('no-uv', '\ncompatibility: Python 3.11+.'),
                        ('uv-inside-a-word', '\ncompatibility: Needs cuvid.')):
        d = _uv_skill(tmp_path, name, extra)
        assert check_skill(d) == [
            f"{d / 'SKILL.md'}: its markdown runs a bundled script with uv run, so compatibility must name uv"], name
    assert check_skill(_uv_skill(tmp_path, 'named', f'\ncompatibility: {UV_COMPATIBILITY}')) == []


def test_compatibility_is_optional_when_no_markdown_runs_a_script(tmp_path):
    # A guard, green before and after: recommend-probabilistic-model bundles
    # characterize.py but its markdown never runs it.
    assert check_skill(_skill_with_script(tmp_path, 'unrun', RUNNABLE)) == []


def make_agent(tmp_path: Path, name: str, description: str) -> Path:
    md = tmp_path / f'{name}.md'
    md.write_text(
        f"---\nname: {name}\ndescription: '{description}'\n"
        'tools: Read, Grep, Glob, Bash\n---\nbody\n'
    )
    return md


def test_agent_overlong_description_is_reported(tmp_path):
    # Agent descriptions all load into the Agent-tool listing, so they carry
    # the same 1024-char cap check_skill enforces on SKILL.md.
    md = make_agent(tmp_path, 'wordy-agent', 'x' * 1100)
    errs = '\n'.join(check_agent_file(md))
    assert 'chars (listing budget 1024)' in errs


def test_agent_description_cap_boundary_is_exact(tmp_path):
    # Pin both sides: the over-cap case alone cannot tell `>` from `>=`.
    assert check_agent_file(make_agent(tmp_path, 'at-cap', 'x' * 1024)) == []
    errs = '\n'.join(check_agent_file(make_agent(tmp_path, 'over-cap', 'x' * 1025)))
    assert 'description is 1025 chars (listing budget 1024)' in errs


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
        'name: pinned-skill\ndescription: Use when testing pins.\nmodel: sonnet\neffort: xhigh',
    )
    assert check_skill(d) == []


def test_haiku_model_on_a_skill_is_rejected(tmp_path):
    # The reason is portability, not inertness: auto mode drops Haiku 4.5 and keeps
    # the session model, and the `haiku` alias means Haiku 5.5 on the Anthropic API
    # but 4.5 on the other providers, so a pin would apply on one and not another
    # (specs/completed/skill-model-pin-removal.md; the register's no-haiku-skill-model).
    d = make_skill(
        tmp_path,
        'haiku-skill',
        'name: haiku-skill\ndescription: Use when testing pins.\nmodel: haiku',
    )
    errs = check_skill(d)
    assert len(errs) == 1, errs
    msg = errs[0]
    assert msg.startswith(f"{d / 'SKILL.md'}: model 'haiku' ")
    assert 'is not portable' in msg
    assert 'auto mode drops Haiku 4.5 and keeps the session model' in msg
    assert 'Haiku 5.5 on the Anthropic API but 4.5 on other providers' in msg
    assert 'model-pinned subagent' in msg
    assert 'specs/completed/skill-model-pin-removal.md' in msg


def test_haiku_5_5_model_id_on_a_skill_is_rejected_as_not_portable(tmp_path):
    # Auto mode supports Haiku 5.5, so this ID is not dropped; the ban is broader
    # than the drop on purpose (owner, 2026-10-12), and the message must not claim
    # the pin is inert.
    d = make_skill(
        tmp_path,
        'haiku-5-5-skill',
        'name: haiku-5-5-skill\ndescription: Use when testing pins.\nmodel: claude-haiku-5-5',
    )
    errs = check_skill(d)
    assert len(errs) == 1, errs
    assert 'is not portable' in errs[0], errs
    assert 'inert' not in errs[0], errs


def test_haiku_model_id_on_a_skill_is_rejected(tmp_path):
    d = make_skill(
        tmp_path,
        'haiku-id-skill',
        'name: haiku-id-skill\ndescription: Use when testing pins.\nmodel: claude-haiku-4-5-20251001',
    )
    errs = check_skill(d)
    assert len(errs) == 1 and 'auto mode drops' in errs[0], errs


def test_haiku_model_on_a_command_is_rejected(tmp_path):
    md = tmp_path / 'cheap-command.md'
    md.write_text(
        '---\ndescription: Does a thing.\ndisable-model-invocation: true\nmodel: haiku\n---\nbody\n'
    )
    errs = check_command_file(md)
    assert len(errs) == 1 and 'auto mode drops' in errs[0], errs


def test_haiku_model_match_ignores_case(tmp_path):
    # The alias and the model-ID prefix are both compared case-insensitively.
    for i, model in enumerate(['Haiku', 'CLAUDE-HAIKU-4-5-20251001']):
        d = make_skill(
            tmp_path,
            f'case-{i}',
            f'name: case-{i}\ndescription: Use when testing pins.\nmodel: {model}',
        )
        errs = check_skill(d)
        assert len(errs) == 1 and 'auto mode drops' in errs[0], (model, errs)


def test_models_auto_mode_can_run_stay_allowed(tmp_path):
    # Only a model auto mode cannot run is rejected. This guard passes before the
    # Haiku rule exists, too; it fails only if the rule matches too much.
    for i, model in enumerate(['sonnet', 'opus', 'fable', 'claude-sonnet-5']):
        d = make_skill(
            tmp_path,
            f'runnable-{i}',
            f'name: runnable-{i}\ndescription: Use when testing pins.\nmodel: {model}',
        )
        assert check_skill(d) == [], model


def test_haiku_model_on_an_agent_is_allowed(tmp_path):
    # A subagent's Haiku pin applies, so agents/*.md are exempt from the rule;
    # this pins that without depending on a real agent keeping its pin.
    md = tmp_path / 'cheap-agent.md'
    md.write_text(
        '---\nname: cheap-agent\ndescription: Does a thing.\nmodel: haiku\n---\nbody\n'
    )
    assert check_agent_file(md) == []


def test_context_fork_key_allowed(tmp_path):
    d = make_skill(
        tmp_path,
        'forked-skill',
        'name: forked-skill\ndescription: Use when testing forks.\ncontext: fork',
    )
    assert check_skill(d) == []


def test_context_rejects_an_undocumented_value(tmp_path):
    # `fork` is the only value Claude Code documents; a typo would otherwise
    # sit in frontmatter doing nothing. Widen CONTEXT_VALUES if that changes.
    d = make_skill(
        tmp_path,
        'typo-skill',
        'name: typo-skill\ndescription: Use when testing forks.\ncontext: forked',
    )
    errs = '\n'.join(check_skill(d))
    assert "context must be one of" in errs


def test_unknown_frontmatter_key_still_rejected(tmp_path):
    d = make_skill(
        tmp_path,
        'bogus-skill',
        'name: bogus-skill\ndescription: Use when testing.\nbogus-key: nope',
    )
    errs = '\n'.join(check_skill(d))
    assert "frontmatter key 'bogus-key' is not allowed by this repo's lint" in errs


def test_documented_but_disallowed_key_is_not_called_unknown(tmp_path):
    # `paths` is a Claude Code skill field the guide documents; the repo's
    # lint still refuses it, so the message names the lint, not ignorance.
    d = make_skill(
        tmp_path,
        'scoped-skill',
        "name: scoped-skill\ndescription: Use when testing.\npaths: ['*.py']",
    )
    errs = '\n'.join(check_skill(d))
    assert "frontmatter key 'paths' is not allowed by this repo's lint" in errs
    assert 'unknown frontmatter key' not in errs


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


def _agent(dir_path: Path, filename: str, name: str, heading: str) -> Path:
    md = dir_path / filename
    md.write_text(
        f'---\nname: {name}\ndescription: x\ntools: Read, Grep, Glob, Bash\n---\n'
        f'\n{heading}\n\nBody.\n'
    )
    return md


def test_readonly_roster_clean_when_both_sides_agree(tmp_path):
    _agent(tmp_path, 'alpha.md', 'alpha', READONLY_HEADING)
    _agent(tmp_path, 'beta.md', 'beta', '## Contract')
    assert check_readonly_roster(tmp_path, frozenset({'alpha'})) == []


def test_readonly_roster_catches_an_unguarded_readonly_agent(tmp_path):
    # Forward direction: a sixth read-only agent shipping without a roster entry.
    _agent(tmp_path, 'gamma.md', 'gamma', READONLY_HEADING)
    errs = '\n'.join(check_readonly_roster(tmp_path, frozenset()))
    assert 'gamma' in errs


def test_readonly_roster_catches_a_stale_roster_entry(tmp_path):
    # Reverse direction: an entry left behind by a renamed or deleted agent.
    _agent(tmp_path, 'alpha.md', 'alpha', READONLY_HEADING)
    errs = '\n'.join(check_readonly_roster(tmp_path, frozenset({'alpha', 'ghost'})))
    assert 'ghost' in errs


def test_readonly_roster_keys_on_frontmatter_name_not_filename(tmp_path):
    # agents/explore.md carries `name: Explore`, and agent_type is the
    # frontmatter name — a roster keyed on the filename would never match.
    _agent(tmp_path, 'explore.md', 'Explore', READONLY_HEADING)
    assert check_readonly_roster(tmp_path, frozenset({'Explore'})) == []
    assert check_readonly_roster(tmp_path, frozenset({'explore'})) != []


def test_readonly_roster_reports_a_missing_guard_instead_of_raising(tmp_path, monkeypatch):
    # If the hook file is gone, the lint must print one violation line, not
    # traceback out of build/check_frontmatter.py and take the whole gate with it.
    import check_frontmatter

    monkeypatch.setattr(check_frontmatter, 'GUARD_PATH', tmp_path / 'nope.py')
    errs = check_frontmatter.check_readonly_roster(tmp_path, None)
    assert len(errs) == 1
    assert 'cannot load READONLY_AGENTS' in errs[0]


def test_load_readonly_roster_reads_the_real_guard():
    roster = load_readonly_roster()
    assert 'Explore' in roster and 'test-runner' in roster


def test_real_roster_matches_the_real_agents():
    # The bidirectional assert against the shipped guard and agents/.
    assert check_readonly_roster() == []


def _pinned_agent(dir_path: Path, filename: str, name: str, model: str | None) -> Path:
    md = dir_path / filename
    model_line = f'model: {model}\n' if model else ''
    md.write_text(f'---\nname: {name}\ndescription: x\n{model_line}---\n\nBody.\n')
    return md


def test_pinned_roster_catches_a_pinned_agent_missing_from_the_hook(tmp_path):
    # Forward direction: an agent pins model: but the dispatch guard would deny it.
    _pinned_agent(tmp_path, 'alpha.md', 'alpha', 'haiku')
    _pinned_agent(tmp_path, 'beta.md', 'beta', None)
    errs = check_pinned_roster(tmp_path, frozenset())
    assert errs == [f'{tmp_path / "alpha.md"}: agent pins model but is missing from '
                    'PINNED_AGENTS in hooks/dispatch-model-guard.py']


def test_pinned_roster_catches_a_roster_name_with_no_pinned_agent(tmp_path):
    # Reverse direction: a roster name whose agent file is gone or unpinned.
    _pinned_agent(tmp_path, 'alpha.md', 'alpha', 'haiku')
    _pinned_agent(tmp_path, 'beta.md', 'beta', None)
    errs = check_pinned_roster(tmp_path, frozenset({'alpha', 'beta'}))
    assert errs == ["hooks/dispatch-model-guard.py: PINNED_AGENTS names 'beta', "
                    'which no agents/*.md pins']


def test_pinned_roster_treats_model_inherit_as_unpinned(tmp_path):
    # `model: inherit` pins nothing, so the dispatch guard needs no roster entry for it.
    _pinned_agent(tmp_path, 'alpha.md', 'alpha', 'inherit')
    assert check_pinned_roster(tmp_path, frozenset()) == []


def test_pinned_roster_reports_a_missing_guard_instead_of_raising(tmp_path, monkeypatch):
    # As for the read-only roster: a missing dispatch guard is one violation line,
    # not a traceback that takes the whole gate with it.
    import check_frontmatter

    monkeypatch.setattr(check_frontmatter, 'DISPATCH_GUARD_PATH', tmp_path / 'nope.py')
    errs = check_frontmatter.check_pinned_roster(tmp_path, None)
    assert len(errs) == 1
    assert 'cannot load PINNED_AGENTS' in errs[0]


def test_real_pinned_roster_matches_the_real_agents():
    # The bidirectional assert against the shipped dispatch guard and agents/.
    assert check_pinned_roster() == []


CITATION_PREFIX = '#' + ' cc-guide:'
CITATION = CITATION_PREFIX + ' skills.frontmatter @2.1.219'


def test_a_drift_citation_comment_passes_every_frontmatter_check(tmp_path):
    '''Drift spec R12.4: a `# cc-guide:` YAML comment as the last frontmatter
    line passes check_frontmatter.py, which never sees it.'''
    d = make_skill(tmp_path, 'cited-skill', f'name: cited-skill\ndescription: >\n  Use when testing.\n{CITATION}')
    assert check_skill(d) == []
    agent = tmp_path / 'cited-agent.md'
    agent.write_text(f'---\nname: cited-agent\ndescription: Use when testing.\ntools: Read\n{CITATION}\n---\n\nBody.\n')
    assert check_agent_file(agent) == []
    command = tmp_path / 'cited-command.md'
    command.write_text(f'---\ndescription: Do a thing.\ndisable-model-invocation: true\n{CITATION}\n---\n\nBody.\n')
    assert check_command_file(command) == []


def test_an_indented_citation_would_join_a_folded_description():
    '''Why the drift lint wants column 0: indented, the line is description text.'''
    folded = 'name: x\ndescription: >\n  Use when testing.\n'
    assert yaml.safe_load(folded + CITATION + '\n') == yaml.safe_load(folded)
    assert yaml.safe_load(folded + '  ' + CITATION + '\n') != yaml.safe_load(folded)


def test_every_frontmatter_citation_leaves_the_parsed_frontmatter_unchanged():
    '''Drift spec R4.1: each tracked Markdown file whose frontmatter carries a
    citation parses to the same mapping without that line.'''
    listed = subprocess.run(['git', 'ls-files', '-z', '*.md'], cwd=REPO, capture_output=True, check=True)
    cited = []
    for name in filter(None, listed.stdout.decode().split('\0')):
        path = REPO / name
        if path.is_symlink() or not path.is_file():
            continue
        lines = path.read_text(encoding='utf-8').split('\n')
        if lines[0] != '---' or '---' not in lines[1:]:
            continue
        front = lines[1:lines.index('---', 1)]
        kept = [line for line in front if not line.startswith(CITATION_PREFIX)]
        if kept != front:
            cited.append(name)
            # Each line ends in a newline, as it does before the closing ---.
            assert yaml.safe_load(''.join(f'{line}\n' for line in kept)) == yaml.safe_load(
                ''.join(f'{line}\n' for line in front)), name
    assert cited, 'no tracked frontmatter carries a citation, so this test checked nothing'
