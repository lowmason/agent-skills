'''Tests for check_conformance.py, the Claude Code guide conformance lint.

Fixture trees are hand-written per test. The R1.2 pin and the repo tests read
the real guide and register.
'''
import json
import os
import subprocess
import tomllib

import pytest

import check_conformance as cc

GUIDE = 'specs/guides/claude-code-customization-guide.md'
FENCE = '`' * 3

# The 38 section IDs of the drift spec's R1.1 table, in heading order
# (specs/claude-code-drift-automation.md). Pinned here as R1.2's oracle; the
# lint itself validates the register against the guide's anchors, never
# against this list.
R11_IDS = [
    'context.overview', 'mechanisms.overview',
    'skills.overview', 'skills.locations', 'skills.frontmatter',
    'skills.description', 'skills.listing-budget',
    'skills.progressive-disclosure', 'skills.arguments', 'skills.iterating',
    'commands.overview',
    'subagents.overview', 'subagents.frontmatter', 'subagents.tools',
    'subagents.models', 'subagents.isolation',
    'rules.overview', 'rules.claude-md', 'rules.hierarchy',
    'rules.rules-files', 'rules.auto-memory', 'rules.settings',
    'hooks.overview', 'hooks.events', 'hooks.exit-codes', 'hooks.handlers',
    'hooks.configuration', 'hooks.patterns', 'hooks.pitfalls',
    'lean.overview', 'lean.measure', 'lean.session-hygiene', 'lean.caching',
    'lean.model-routing', 'lean.mcp', 'lean.ceremony', 'lean.expensive-ops',
    'reading.overview',
]


def rendered(violations):
    return [v.render() for v in violations]


def test_heading_inside_a_fence_is_not_a_heading():
    text = ('# Guide\n\n## A\n<!-- cc: a.overview -->\n\n'
            f'{FENCE}bash\n## not a heading\n{FENCE}\n')
    sections, violations = cc.guide_sections(text, 'guide.md')
    assert [(s.line, s.id) for s in sections] == [(3, 'a.overview')]
    assert violations == []


def test_heading_without_an_anchor_is_a_violation():
    text = '## A\n<!-- cc: a.overview -->\n### B\nbody\n'
    sections, violations = cc.guide_sections(text, 'guide.md')
    assert [s.id for s in sections] == ['a.overview', None]
    assert rendered(violations) == [
        "guide.md: anchor (-): line 3: heading '### B' has no anchor on its next line"]


def test_malformed_anchor_is_a_violation():
    text = '## A\n<!-- cc: A_Overview -->\n'
    sections, violations = cc.guide_sections(text, 'guide.md')
    assert [s.id for s in sections] == [None]
    assert rendered(violations) == [
        "guide.md: anchor (-): line 2: malformed anchor '<!-- cc: A_Overview -->'"]


def test_anchor_not_directly_under_a_heading_is_a_violation():
    text = '## A\n<!-- cc: a.overview -->\n<!-- cc: a.extra -->\n'
    _, violations = cc.guide_sections(text, 'guide.md')
    assert rendered(violations) == [
        'guide.md: anchor (-): line 3: anchor is not directly under a heading']


def test_repeated_anchor_id_is_a_violation():
    text = '## A\n<!-- cc: a.one -->\n## B\n<!-- cc: a.one -->\n'
    sections, violations = cc.guide_sections(text, 'guide.md')
    assert [s.id for s in sections] == ['a.one', None]
    assert rendered(violations) == [
        'guide.md: anchor (a.one): line 4: anchor repeats line 2']


def test_real_guide_carries_the_drift_r11_anchors():
    '''R1.2: 38 headings outside fences, each followed by exactly one
    well-formed anchor, whose IDs in heading order equal drift's R1.1 table.'''
    text = (cc.REPO / GUIDE).read_text()
    sections, violations = cc.guide_sections(text, GUIDE)
    assert len(sections) == 38
    assert rendered(violations) == []
    assert [s.id for s in sections] == R11_IDS


# A three-section fixture guide and a register that maps it. FIXTURE_REGISTER
# carries all seven check_conformance checks and one check_frontmatter entry,
# so a fixture repo built on it is clean until a test adds a violation.
FIXTURE_GUIDE = (
    '# Fixture guide\n\n'
    '## A\n<!-- cc: a.overview -->\n\nIntro.\n\n'
    '### One\n<!-- cc: a.one -->\n\nRules.\n\n'
    '## B\n<!-- cc: b.overview -->\n'
)
FIXTURE_ANCHORS = ['a.overview', 'a.one', 'b.overview']
FIXTURE_REGISTER = """\
[guide]
path = 'guide.md'

[kinds.agent]
description = 'Agents.'
globs = ['agents/*.md']
sections = ['a.overview']

[kinds.claude-md]
description = 'CLAUDE.md files.'
globs = ['CLAUDE.md']
sections = ['a.one']

[kinds.hook]
description = 'Hook scripts and their README.'
globs = ['hooks/*.sh', 'hooks/*.py', 'hooks/README.md']
exclude = ['hooks/test_*.py']
sections = ['a.one']

[kinds.rule]
description = 'Rules files.'
globs = ['rules/*.md', '.claude/rules/*.md']
sections = ['a.one']

[kinds.settings]
description = 'Project settings.'
globs = ['.claude/settings.json']
sections = ['a.one']

[unmapped]
'b.overview' = 'Governs no fixture file.'

[[check]]
id = 'claude-md-size'
kind = 'claude-md'
sections = ['a.one']
type = 'advice'
rule = 'Stay short.'
enforced_by = 'check_conformance'
limit = 200

[[check]]
id = 'rule-paths'
kind = 'rule'
sections = ['a.one']
type = 'advice'
rule = 'Set paths.'
enforced_by = 'check_conformance'
always_on = []

[[check]]
id = 'hook-dir-quoted'
kind = ['hook', 'settings']
sections = ['a.one']
type = 'advice'
rule = 'Quote the project dir.'
enforced_by = 'check_conformance'

[[check]]
id = 'stop-hook-guard'
kind = ['hook', 'settings']
sections = ['a.one']
type = 'advice'
rule = 'Guard Stop hooks.'
enforced_by = 'check_conformance'

[[check]]
id = 'agent-fields'
kind = 'agent'
sections = ['a.overview']
type = 'fact'
rule = 'Documented fields only.'
enforced_by = 'check_conformance'
fields = ['name', 'description', 'tools', 'model', 'memory']
models = ['sonnet', 'opus', 'haiku', 'fable', 'inherit']

[[check]]
id = 'readonly-agent-tools'
kind = 'agent'
sections = ['a.overview']
type = 'advice'
rule = 'Read-only tools.'
enforced_by = 'check_conformance'
forbidden_tools = ['Write', 'Edit', 'NotebookEdit']

[[check]]
id = 'bash-search-tools'
kind = 'agent'
sections = ['a.overview']
type = 'fact'
rule = 'No Grep or Glob beside Bash.'
enforced_by = 'check_conformance'

[[check]]
id = 'known-agent-tools'
kind = 'agent'
sections = ['a.overview']
type = 'fact'
rule = 'Known tools.'
enforced_by = 'check_frontmatter'
"""


def write_tree(root, files):
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


def test_missing_register_is_a_setup_error(tmp_path):
    with pytest.raises(cc.SetupError, match='register not found'):
        cc.load_register(tmp_path)


def test_unparseable_register_is_a_setup_error(tmp_path):
    write_tree(tmp_path, {cc.REGISTER: 'kinds = [unclosed\n'})
    with pytest.raises(cc.SetupError, match='not valid TOML'):
        cc.load_register(tmp_path)


def test_missing_guide_is_a_setup_error(tmp_path):
    with pytest.raises(cc.SetupError, match='guide not found'):
        cc.load_guide(tmp_path, {'guide': {'path': 'guide.md'}})


def test_non_utf8_register_is_a_setup_error(tmp_path):
    path = tmp_path / cc.REGISTER
    path.parent.mkdir(parents=True)
    path.write_bytes(b"# caf\xe9\n[guide]\npath = 'guide.md'\n")
    with pytest.raises(cc.SetupError, match='not valid TOML'):
        cc.load_register(tmp_path)


def test_non_utf8_guide_is_a_setup_error(tmp_path):
    (tmp_path / 'guide.md').write_bytes(b'## caf\xe9\n')
    with pytest.raises(cc.SetupError, match='guide is not UTF-8'):
        cc.load_guide(tmp_path, {'guide': {'path': 'guide.md'}})


def test_register_field_problems_are_violations():
    raw = tomllib.loads(FIXTURE_REGISTER)
    del raw['kinds']['agent']['globs']
    raw['unmapped']['b.overview'] = ''
    raw['check'][0]['type'] = 'opinion'
    raw['check'][1]['enforced_by'] = 'by_hand'
    raw['check'][2]['kind'] = ['hook', 'nonesuch']
    reg, violations = cc.parse_register(raw)
    assert rendered(violations) == [
        f'{cc.REGISTER}: register (-): kinds.agent: globs must be a non-empty list of strings',
        f'{cc.REGISTER}: register (-): [unmapped] b.overview: the reason must be a non-empty string',
        f'{cc.REGISTER}: register (-): check claude-md-size: type must be fact or advice',
        f'{cc.REGISTER}: register (-): check rule-paths: enforced_by must be check_conformance or check_frontmatter',
        f'{cc.REGISTER}: register (-): check hook-dir-quoted: kind names no [kinds] table: nonesuch',
    ]
    assert sorted(reg.kinds) == ['claude-md', 'hook', 'rule', 'settings']
    assert [c.id for c in reg.checks] == [
        'claude-md-size', 'stop-hook-guard', 'agent-fields',
        'readonly-agent-tools', 'bash-search-tools', 'known-agent-tools']
    assert reg.checks[0].params == {'limit': 200}


def test_unknown_section_id_is_a_violation():
    raw = tomllib.loads(FIXTURE_REGISTER)
    raw['kinds']['rule']['sections'] = ['a.one', 'a.typo']
    reg, _ = cc.parse_register(raw)
    assert rendered(cc.section_violations(reg, FIXTURE_ANCHORS)) == [
        f'{cc.REGISTER}: section-id (a.typo): kinds.rule cites a section with no anchor in the guide']


def test_unmapped_anchor_is_a_violation():
    raw = tomllib.loads(FIXTURE_REGISTER)
    del raw['unmapped']['b.overview']
    reg, _ = cc.parse_register(raw)
    assert rendered(cc.section_violations(reg, FIXTURE_ANCHORS)) == [
        f'{cc.REGISTER}: section-map (b.overview): section is neither mapped to a kind nor listed in [unmapped]']


def test_anchor_both_mapped_and_unmapped_is_a_violation():
    raw = tomllib.loads(FIXTURE_REGISTER)
    raw['unmapped']['a.one'] = 'Listed by mistake.'
    reg, _ = cc.parse_register(raw)
    assert rendered(cc.section_violations(reg, FIXTURE_ANCHORS)) == [
        f'{cc.REGISTER}: section-map (a.one): section is both mapped to a kind and listed in [unmapped]']


def test_real_register_maps_every_anchor():
    raw = cc.load_register(cc.REPO)
    guide_path, text = cc.load_guide(cc.REPO, raw)
    assert guide_path == GUIDE
    sections, _ = cc.guide_sections(text, guide_path)
    reg, problems = cc.parse_register(raw)
    assert rendered(problems) == []
    assert rendered(cc.section_violations(reg, [s.id for s in sections])) == []


def git_repo(root, files):
    '''Write files under root and git-init it, so kept_files can list them.'''
    write_tree(root, files)
    subprocess.run(['git', 'init', '-q'], cwd=root, env=cc.git_env(), check=True)
    return root


def test_kind_globs_are_root_anchored_and_honor_exclude(tmp_path):
    root = git_repo(tmp_path, {
        'skills/a/SKILL.md': 'skill\n',
        'skills/a/references/SKILL.md': 'nested copy\n',
        'specs/verification/trial/skills/a/SKILL.md': 'trial copy\n',
        'hooks/guard.sh': '#!/bin/sh\n',
        'hooks/sub/nested.sh': '#!/bin/sh\n',
        'hooks/test_guard.py': '',
        'ignored/x.md': '',
        '.gitignore': 'ignored/\n',
    })
    files = cc.kept_files(root)
    assert 'ignored/x.md' not in files
    reg = cc.Register(
        kinds={'skill': cc.Kind(['skills/*/SKILL.md'], [], ['a.one']),
               'hook': cc.Kind(['hooks/*.sh', 'hooks/*.py'], ['hooks/test_*.py'], ['a.one'])},
        unmapped={}, checks=[])
    assert cc.kind_files(reg, files) == {
        'skill': ['skills/a/SKILL.md'], 'hook': ['hooks/guard.sh']}


def test_repo_kinds_match_the_directory_listings():
    '''The skill, agent and command kinds hold exactly what check_frontmatter.py
    lists from skills/, agents/ and commands/ (the .claude/ globs aside): no
    recursive search, so the SKILL.md copies under specs/verification/ never
    count as skills.'''
    reg, _ = cc.parse_register(cc.load_register(cc.REPO))
    kinds = cc.kind_files(reg, cc.kept_files(cc.REPO))
    repo = cc.REPO

    def canonical(kind):
        return [f for f in kinds[kind] if not f.startswith('.claude/')]

    assert canonical('skill') == sorted(
        f'skills/{d.name}/SKILL.md' for d in (repo / 'skills').iterdir()
        if (d / 'SKILL.md').is_file())
    assert canonical('agent') == sorted(f'agents/{p.name}' for p in (repo / 'agents').glob('*.md'))
    assert canonical('command') == sorted(
        f'commands/{p.name}' for p in (repo / 'commands').glob('*.md'))


AGENT_PARAMS = {
    'fields': ['name', 'description', 'tools', 'model', 'effort', 'memory'],
    'models': ['sonnet', 'opus', 'haiku', 'fable', 'inherit'],
}
READ_ONLY = '\n## Read-only contract\n\nNo edits.\n'


def test_agent_fields_pass(tmp_path):
    write_tree(tmp_path, {
        'agents/a.md': '---\nname: a\ndescription: A.\ntools: Read\nmodel: opus\neffort: high\n---\n',
        'agents/b.md': '---\nname: b\ndescription: B.\nmodel: claude-sonnet-5-5\n---\n',
    })
    assert cc.check_agent_fields(tmp_path, ['agents/a.md', 'agents/b.md'], AGENT_PARAMS) == []


def test_agent_fields_flag_unknown_keys_and_models(tmp_path):
    write_tree(tmp_path, {
        'agents/a.md': '---\nname: a\ndescription: A.\ncolour: red\nmodel: gpt-6\n---\n',
        'agents/b.md': 'No frontmatter.\n',
    })
    assert cc.check_agent_fields(tmp_path, ['agents/a.md', 'agents/b.md'], AGENT_PARAMS) == [
        cc.Finding('agents/a.md', "frontmatter key 'colour' is not a documented agent field"),
        cc.Finding('agents/a.md', "model 'gpt-6' is neither a listed alias nor a full claude- model ID"),
        cc.Finding('agents/b.md', 'no parseable YAML frontmatter'),
    ]


def test_readonly_agent_tools_pass(tmp_path):
    write_tree(tmp_path, {
        'agents/reviewer.md': '---\nname: reviewer\ntools: Read, Grep, Glob\n---\n' + READ_ONLY,
        'agents/worker.md': '---\nname: worker\ntools: Read, Write, Edit\n---\n\n## Contract\n',
    })
    files = ['agents/reviewer.md', 'agents/worker.md']
    params = {'forbidden_tools': ['Write', 'Edit', 'NotebookEdit']}
    assert cc.check_readonly_agent_tools(tmp_path, files, params) == []


def test_readonly_agent_tools_flag_editing_tools_memory_and_no_allowlist(tmp_path):
    write_tree(tmp_path, {
        'agents/writer.md': '---\nname: writer\ntools: [Read, Write, Edit]\n---\n' + READ_ONLY,
        'agents/memo.md': '---\nname: memo\ntools: Read\nmemory: project\n---\n' + READ_ONLY,
        'agents/open.md': '---\nname: open\n---\n' + READ_ONLY,
    })
    files = ['agents/memo.md', 'agents/open.md', 'agents/writer.md']
    params = {'forbidden_tools': ['Write', 'Edit', 'NotebookEdit']}
    assert cc.check_readonly_agent_tools(tmp_path, files, params) == [
        cc.Finding('agents/memo.md', 'read-only agent sets memory, which adds Read, Write and Edit'),
        cc.Finding('agents/open.md', 'read-only agent sets no tools list, so it inherits every tool'),
        cc.Finding('agents/writer.md', 'read-only agent lists Write, Edit'),
    ]


def test_unreadable_artifacts_are_unwaivable_findings(tmp_path):
    (tmp_path / 'agents').mkdir()
    (tmp_path / 'agents/gone.md').symlink_to('nowhere.md')
    (tmp_path / 'agents/latin.md').write_bytes(b'---\nname: caf\xe9\n---\n')
    assert cc.check_agent_fields(tmp_path, ['agents/gone.md', 'agents/latin.md'], AGENT_PARAMS) == [
        cc.Finding('agents/gone.md', 'cannot read: No such file or directory', waivable=False),
        cc.Finding('agents/latin.md', 'cannot read: not UTF-8 (invalid continuation byte)', waivable=False),
    ]


def test_bash_search_tools_pass(tmp_path):
    write_tree(tmp_path, {
        'agents/shell.md': '---\nname: shell\ntools: Read, Bash\n---\n',
        'agents/search.md': '---\nname: search\ntools: Read, Grep, Glob\n---\n',
    })
    assert cc.check_bash_search_tools(tmp_path, ['agents/search.md', 'agents/shell.md'], {}) == []


def test_bash_search_tools_flag_grep_or_glob_beside_bash(tmp_path):
    write_tree(tmp_path, {
        'agents/a.md': '---\nname: a\ntools: Read, Grep, Glob, Bash\n---\n',
        'agents/b.md': '---\nname: b\ntools: [Bash, Glob]\n---\n',
    })
    assert cc.check_bash_search_tools(tmp_path, ['agents/a.md', 'agents/b.md'], {}) == [
        cc.Finding('agents/a.md', 'lists Grep and Glob beside Bash, where both are absent and search runs through the shell'),
        cc.Finding('agents/b.md', 'lists Glob beside Bash, where both are absent and search runs through the shell'),
    ]


def hooks_tree(event, command):
    return {'hooks': {event: [{'hooks': [{'type': 'command', 'command': command}]}]}}


def json_block(data):
    return f'{FENCE}json\n{json.dumps(data, indent=2)}\n{FENCE}\n'


HOOK_FILES = ['.claude/settings.json', 'hooks/README.md', 'hooks/ruff-check.sh']
STOP_SCRIPT = '#!/usr/bin/env bash\nactive=$(jq -r .stop_hook_active)\n'


@pytest.mark.parametrize('command, states', [
    ('"$CLAUDE_PROJECT_DIR"/.claude/hooks/a.sh', []),
    ('"${CLAUDE_PROJECT_DIR}/a.sh"', []),
    ('"it\'s $CLAUDE_PROJECT_DIR"/a.sh', []),
    ('\\$CLAUDE_PROJECT_DIR/a.sh', []),
    ('$CLAUDE_PROJECT_DIRX/a.sh', []),
    ('$CLAUDE_PROJECT_DIR/.claude/hooks/a.sh', ['unquoted']),
    ("'$CLAUDE_PROJECT_DIR'/a.sh", ['single-quoted']),
    ('"a b"/${CLAUDE_PROJECT_DIR}/a.sh', ['unquoted']),
])
def test_unquoted_var_uses_track_shell_quoting(command, states):
    assert cc.unquoted_var_uses(command, 'CLAUDE_PROJECT_DIR') == states


def test_hook_dir_quoted_passes(tmp_path):
    write_tree(tmp_path, {
        'hooks/README.md': (
            json_block(hooks_tree('PreToolUse', '"$CLAUDE_PROJECT_DIR"/.claude/hooks/a.sh'))
            + json_block({'permissions': {'allow': ['Bash(uv run *)']}})),
        '.claude/settings.json': json.dumps(hooks_tree('Stop', '"${CLAUDE_PROJECT_DIR}/b.sh"')),
        'hooks/ruff-check.sh': STOP_SCRIPT,
    })
    assert cc.check_hook_dir_quoted(tmp_path, HOOK_FILES, {}) == []


def test_hook_dir_quoted_flags_unquoted_and_single_quoted_uses(tmp_path):
    write_tree(tmp_path, {
        'hooks/README.md': 'Wiring:\n\n' + json_block({'hooks': {
            'PreToolUse': [{'matcher': 'Bash', 'hooks': [
                {'type': 'command', 'command': '$CLAUDE_PROJECT_DIR/.claude/hooks/a.sh'}]}],
            'Stop': [{'hooks': [
                {'type': 'command', 'command': "'$CLAUDE_PROJECT_DIR'/.claude/hooks/b.sh"}]}],
        }}),
        '.claude/settings.json': json.dumps(hooks_tree('PostToolUse', '${CLAUDE_PROJECT_DIR}/c.sh')),
        'hooks/ruff-check.sh': STOP_SCRIPT,
    })
    assert cc.check_hook_dir_quoted(tmp_path, HOOK_FILES, {}) == [
        cc.Finding('.claude/settings.json', 'PostToolUse command leaves $CLAUDE_PROJECT_DIR unquoted'),
        cc.Finding('hooks/README.md', 'JSON block at line 3: PreToolUse command leaves $CLAUDE_PROJECT_DIR unquoted'),
        cc.Finding('hooks/README.md', 'JSON block at line 3: Stop command leaves $CLAUDE_PROJECT_DIR single-quoted'),
    ]


def test_unparseable_json_block_is_a_violation(tmp_path):
    write_tree(tmp_path, {'hooks/README.md': f'{FENCE}json\n{{"hooks": }}\n{FENCE}\n'})
    assert cc.check_hook_dir_quoted(tmp_path, ['hooks/README.md'], {}) == [
        cc.Finding('hooks/README.md', 'JSON block at line 1 does not parse (Expecting value)',
                   waivable=False)]


def test_hook_dir_quoted_reads_only_markdown_and_json(tmp_path):
    write_tree(tmp_path, {'hooks/README.md': json_block(hooks_tree('Stop', '"$CLAUDE_PROJECT_DIR"/x.sh'))})
    (tmp_path / 'hooks/legacy.sh').write_bytes(b'#!/bin/sh\n# caf\xe9\n')
    assert cc.check_hook_dir_quoted(tmp_path, ['hooks/README.md', 'hooks/legacy.sh'], {}) == []


def test_stop_hook_guard_passes(tmp_path):
    write_tree(tmp_path, {
        'hooks/README.md': json_block(hooks_tree('Stop', '"$CLAUDE_PROJECT_DIR"/.claude/hooks/ruff-check.sh')),
        'hooks/ruff-check.sh': STOP_SCRIPT,
    })
    assert cc.check_stop_hook_guard(tmp_path, ['hooks/README.md', 'hooks/ruff-check.sh'], {}) == []


def test_stop_hook_guard_flags_an_unguarded_or_unresolvable_script(tmp_path):
    write_tree(tmp_path, {
        'hooks/README.md': json_block({'hooks': {'Stop': [{'hooks': [
            {'type': 'command', 'command': '$CLAUDE_PROJECT_DIR/.claude/hooks/gate.sh'},
            {'type': 'command', 'command': 'uv run ruff check .'},
        ]}]}}),
        'hooks/gate.sh': '#!/usr/bin/env bash\nexit 2\n',
    })
    assert cc.check_stop_hook_guard(tmp_path, ['hooks/README.md', 'hooks/gate.sh'], {}) == [
        cc.Finding('hooks/README.md', 'JSON block at line 1: Stop command runs hooks/gate.sh, which never reads stop_hook_active'),
        cc.Finding('hooks/README.md', "JSON block at line 1: Stop command 'uv run ruff check .' names no hook script in the repo"),
    ]


def test_claude_md_size_passes_under_the_limit(tmp_path):
    write_tree(tmp_path, {'CLAUDE.md': 'line\n' * 199})
    assert cc.check_claude_md_size(tmp_path, ['CLAUDE.md'], {'limit': 200}) == []


def test_claude_md_size_flags_a_file_at_the_limit(tmp_path):
    write_tree(tmp_path, {'CLAUDE.md': 'line\n' * 200})
    assert cc.check_claude_md_size(tmp_path, ['CLAUDE.md'], {'limit': 200}) == [
        cc.Finding('CLAUDE.md', '200 lines; the guide targets fewer than 200', 200)]


def test_claude_md_size_counts_lines_as_wc_does(tmp_path):
    '''A form feed breaks a line for str.splitlines, but not for wc -l.'''
    write_tree(tmp_path, {'CLAUDE.md': 'a\fb\n' * 150})
    assert cc.check_claude_md_size(tmp_path, ['CLAUDE.md'], {'limit': 200}) == []


RULE = "---\npaths:\n  - '**/*.py'\n---\n\nRule.\n"


def test_rule_paths_pass(tmp_path):
    root = tmp_path / 'repo'
    write_tree(root, {'rules/py.md': RULE, 'rules/core.md': 'Always on.\n'})
    (root / '.claude/rules').mkdir(parents=True)
    os.symlink('../../rules/py.md', root / '.claude/rules/py.md')
    files = ['.claude/rules/py.md', 'rules/core.md', 'rules/py.md']
    assert cc.check_rule_paths(root, files, {'always_on': ['rules/core.md']}) == []


def test_rule_paths_flag_missing_paths_always_on_paths_and_outside_links(tmp_path):
    root = tmp_path / 'repo'
    write_tree(root, {'rules/bare.md': 'No frontmatter.\n', 'rules/py.md': RULE})
    write_tree(tmp_path, {'elsewhere/out.md': RULE})
    (root / '.claude/rules').mkdir(parents=True)
    os.symlink('../../../elsewhere/out.md', root / '.claude/rules/out.md')
    os.symlink('../../rules/gone.md', root / '.claude/rules/gone.md')
    files = ['.claude/rules/gone.md', '.claude/rules/out.md', 'rules/bare.md', 'rules/py.md']
    assert cc.check_rule_paths(root, files, {'always_on': ['rules/py.md']}) == [
        cc.Finding('.claude/rules/gone.md', 'link target does not exist', waivable=False),
        cc.Finding('.claude/rules/out.md', 'link resolves outside the repo, so Claude Code treats it as an external import'),
        cc.Finding('rules/bare.md', 'frontmatter sets no non-empty paths list, so the rule loads in every session'),
        cc.Finding('rules/py.md', 'always_on lists this rule, but it sets paths'),
    ]


def fixture_repo(tmp_path, files=None, register=FIXTURE_REGISTER):
    '''A git-initialized fixture repo holding the fixture guide, a register
    (FIXTURE_REGISTER unless given) and files; clean until files add a violation.'''
    return git_repo(tmp_path, {'guide.md': FIXTURE_GUIDE, cc.REGISTER: register, **(files or {})})


GREP_BESIDE_BASH = '---\nname: a\ndescription: A.\ntools: Read, Grep, Bash\n---\n'


def test_main_exits_0_on_a_clean_repo(tmp_path, capsys):
    root = fixture_repo(tmp_path, {'CLAUDE.md': 'Short.\n'})
    assert cc.main(root) == 0
    assert capsys.readouterr().out == ''


def test_main_exits_1_with_one_line_per_violation(tmp_path, capsys):
    root = fixture_repo(tmp_path, {'CLAUDE.md': 'line\n' * 250, 'agents/a.md': GREP_BESIDE_BASH})
    assert cc.main(root) == 1
    assert capsys.readouterr().out.splitlines() == [
        'CLAUDE.md: claude-md-size (a.one): 250 lines; the guide targets fewer than 200',
        'agents/a.md: bash-search-tools (a.overview): lists Grep beside Bash, where both are absent and search runs through the shell',
    ]


def test_main_exits_2_on_an_unparseable_register(tmp_path, capsys):
    root = fixture_repo(tmp_path, register='[guide\npath = 1\n')
    assert cc.main(root) == 2
    captured = capsys.readouterr()
    assert captured.out == ''
    assert captured.err.startswith(f'{cc.REGISTER}: not valid TOML')


def test_main_exits_2_when_the_guide_is_missing(tmp_path, capsys):
    root = fixture_repo(tmp_path)
    (root / 'guide.md').unlink()
    assert cc.main(root) == 2
    assert capsys.readouterr().err == 'guide.md: guide not found\n'


def test_check_entry_without_an_implementation_is_a_violation(tmp_path):
    root = fixture_repo(tmp_path, register=FIXTURE_REGISTER + """
[[check]]
id = 'no-such-check'
kind = 'agent'
sections = ['a.overview']
type = 'advice'
rule = 'Unimplemented.'
enforced_by = 'check_conformance'
""")
    assert cc.run(root) == [
        f'{cc.REGISTER}: check-impl (a.overview): check no-such-check has no implementation in build/check_conformance.py']


def test_implementation_without_a_check_entry_is_a_violation(tmp_path):
    register = FIXTURE_REGISTER.replace("id = 'bash-search-tools'", "id = 'bash-search-toolz'")
    root = fixture_repo(tmp_path, register=register)
    assert cc.run(root) == [
        f'{cc.REGISTER}: check-impl (a.overview): check bash-search-toolz has no implementation in build/check_conformance.py',
        'build/check_conformance.py: check-impl (-): implementation bash-search-tools has no [[check]] entry',
    ]


def test_missing_check_parameter_is_a_violation(tmp_path):
    root = fixture_repo(tmp_path, register=FIXTURE_REGISTER.replace('limit = 200\n', ''))
    assert cc.run(root) == [
        f'{cc.REGISTER}: register (-): check claude-md-size: parameter limit must be an integer']


def test_duplicate_check_ids_are_a_violation(tmp_path):
    root = fixture_repo(tmp_path, register=FIXTURE_REGISTER + """
[[check]]
id = 'known-agent-tools'
kind = 'agent'
sections = ['a.overview']
type = 'fact'
rule = 'Listed twice.'
enforced_by = 'check_frontmatter'
""")
    assert cc.run(root) == [
        f'{cc.REGISTER}: duplicate-id (-): check ID known-agent-tools appears 2 times']


def toml_value(value):
    if isinstance(value, list):
        return '[' + ', '.join(toml_value(v) for v in value) + ']'
    if isinstance(value, int):
        return str(value)
    return f"'{value}'"


def exception_toml(fields):
    '''One [[exception]] table; a None value leaves its key out.'''
    body = ''.join(f'{k} = {toml_value(v)}\n' for k, v in fields.items() if v is not None)
    return f'\n[[exception]]\n{body}'


GAP = {
    'id': 'grep-beside-bash', 'type': 'gap', 'check': 'bash-search-tools',
    'sections': ['a.overview'], 'artifacts': ['agents/a.md'],
    'guide': 'Bash hides Grep and Glob.', 'reason': 'Gemini adapters use them.',
    'evidence': 'Fixture.', 'tracked_in': 'a later stage', 'protects': ['gemini'],
}
SIZE_GAP = {**GAP, 'id': 'md-size', 'check': 'claude-md-size', 'sections': ['a.one'],
            'artifacts': ['CLAUDE.md'], 'protects': None, 'ceiling': 225}
UNWAIVED = ('agents/a.md: bash-search-tools (a.overview): lists Grep beside Bash, '
            'where both are absent and search runs through the shell')


def test_waiver_hides_its_violation(tmp_path):
    root = fixture_repo(tmp_path, {'agents/a.md': GREP_BESIDE_BASH},
                        register=FIXTURE_REGISTER + exception_toml(GAP))
    assert cc.run(root) == []


def test_stale_waiver_is_a_violation(tmp_path):
    root = fixture_repo(tmp_path, {'agents/a.md': '---\nname: a\ntools: Read, Bash\n---\n'},
                        register=FIXTURE_REGISTER + exception_toml(GAP))
    assert cc.run(root) == [
        'agents/a.md: stale-waiver (a.overview): exception grep-beside-bash (Gemini adapters use them.) '
        'waives bash-search-tools here, but the file no longer violates it: remove the entry, '
        'or this file from it']


def test_ceiling_breach_is_a_violation(tmp_path):
    root = fixture_repo(tmp_path, {'CLAUDE.md': 'line\n' * 230},
                        register=FIXTURE_REGISTER + exception_toml(SIZE_GAP))
    assert cc.run(root) == [
        "CLAUDE.md: ceiling (a.one): 230 exceeds exception md-size's ceiling of 225"]


def test_file_under_its_ceiling_passes(tmp_path):
    root = fixture_repo(tmp_path, {'CLAUDE.md': 'line\n' * 220},
                        register=FIXTURE_REGISTER + exception_toml(SIZE_GAP))
    assert cc.run(root) == []


def test_file_at_its_ceiling_passes(tmp_path):
    root = fixture_repo(tmp_path, {'CLAUDE.md': 'line\n' * 225},
                        register=FIXTURE_REGISTER + exception_toml(SIZE_GAP))
    assert cc.run(root) == []


def test_waiver_covers_only_its_listed_files(tmp_path):
    root = fixture_repo(tmp_path, {'agents/a.md': GREP_BESIDE_BASH, 'agents/b.md': GREP_BESIDE_BASH},
                        register=FIXTURE_REGISTER + exception_toml(GAP))
    assert cc.run(root) == [UNWAIVED.replace('agents/a.md', 'agents/b.md')]


def test_waiver_covers_only_its_check(tmp_path):
    agent = GREP_BESIDE_BASH.replace('---\n', '---\ncolour: red\n', 1)
    root = fixture_repo(tmp_path, {'agents/a.md': agent},
                        register=FIXTURE_REGISTER + exception_toml(GAP))
    assert cc.run(root) == [
        "agents/a.md: agent-fields (a.overview): frontmatter key 'colour' is not a documented agent field"]


def test_unparseable_block_is_never_waived(tmp_path):
    '''A JSON block that does not parse stands beside a waiver on its file,
    and does not keep that waiver alive.'''
    hook_gap = {**GAP, 'id': 'hook-dir', 'check': 'hook-dir-quoted', 'sections': ['a.one'],
                'artifacts': ['hooks/README.md'], 'protects': None}
    readme = (json_block(hooks_tree('PreToolUse', '$CLAUDE_PROJECT_DIR/a.sh'))
              + f'{FENCE}json\n{{"hooks": }}\n{FENCE}\n')
    root = fixture_repo(tmp_path, {'hooks/README.md': readme},
                        register=FIXTURE_REGISTER + exception_toml(hook_gap))
    assert cc.run(root) == [
        'hooks/README.md: hook-dir-quoted (a.one): JSON block at line 17 does not parse (Expecting value)']


def test_check_that_cannot_run_leaves_its_waivers_alone(tmp_path):
    '''A malformed parameter stops a check, so its waiver is not called stale.'''
    register = (FIXTURE_REGISTER.replace('limit = 200\n', "limit = '200'\n")
                + exception_toml(GAP) + exception_toml(SIZE_GAP))
    root = fixture_repo(tmp_path, {'CLAUDE.md': 'line\n' * 230, 'agents/a.md': GREP_BESIDE_BASH},
                        register=register)
    assert cc.run(root) == [
        f'{cc.REGISTER}: register (-): check claude-md-size: parameter limit must be an integer']


def test_valid_exceptions_pass(tmp_path):
    '''A gap waiving its check beside a check-less deviation whose artifacts
    are a glob: both are well-formed, so the repo is clean.'''
    deviation = {**GAP, 'id': 'tools-convention', 'type': 'deviation', 'check': None,
                 'artifacts': ['agents/*.md'], 'tracked_in': None, 'revisit': 'when Gemini changes'}
    root = fixture_repo(tmp_path, {'agents/a.md': GREP_BESIDE_BASH},
                        register=FIXTURE_REGISTER + exception_toml(GAP) + exception_toml(deviation))
    assert cc.run(root) == []


def test_duplicate_exception_ids_are_a_violation(tmp_path):
    second = {**GAP, 'check': None, 'protects': None}
    root = fixture_repo(tmp_path, {'agents/a.md': GREP_BESIDE_BASH},
                        register=FIXTURE_REGISTER + exception_toml(GAP) + exception_toml(second))
    assert cc.run(root) == [
        f'{cc.REGISTER}: duplicate-id (-): exception ID grep-beside-bash appears 2 times']


def test_numeric_waiver_needs_a_ceiling(tmp_path):
    root = fixture_repo(tmp_path, {'CLAUDE.md': 'line\n' * 230},
                        register=FIXTURE_REGISTER + exception_toml({**SIZE_GAP, 'ceiling': None}))
    assert cc.run(root) == [
        f'{cc.REGISTER}: exception (-): exception md-size: a waiver of claude-md-size needs an integer ceiling']


def field_error(message):
    return f'{cc.REGISTER}: exception (-): exception grep-beside-bash: {message}'


@pytest.mark.parametrize('changes, expected', [
    ({'type': 'excuse'}, [field_error('type must be deviation or gap')]),
    ({'tracked_in': None}, [field_error('a gap needs tracked_in')]),
    ({'revisit': 'when X'}, [field_error('a gap takes no revisit')]),
    ({'type': 'deviation', 'tracked_in': None}, [field_error('a deviation needs revisit')]),
    ({'type': 'deviation', 'revisit': 'when X'}, [field_error('a deviation takes no tracked_in')]),
    ({'evidence': ''}, [field_error('evidence must be a non-empty string')]),
    ({'protects': ['cursor']}, [field_error('protects may list only codex and gemini')]),
    ({'ceiling': 3}, [field_error('ceiling applies only to a numeric check (claude-md-size)')]),
    ({'sections': ['a.typo']}, [
        f'{cc.REGISTER}: section-id (a.typo): exception grep-beside-bash cites a section with no anchor in the guide']),
    ({'check': 'known-agent-tools'}, [
        UNWAIVED, field_error('check known-agent-tools is not a check_conformance check')]),
    ({'check': ['bash-search-tools']}, [
        UNWAIVED, field_error('check must name one check_conformance check')]),
    ({'artifacts': ['agents/*.md']}, [
        UNWAIVED, field_error('with check set, artifacts must be explicit paths: agents/*.md')]),
    ({'artifacts': ['agents/gone.md']}, [
        UNWAIVED, field_error('artifact agents/gone.md does not exist')]),
    ({'check': None, 'artifacts': ['skills/*/SKILL.md']}, [
        UNWAIVED, field_error('artifact glob skills/*/SKILL.md matches no file')]),
])
def test_exception_field_rules(tmp_path, changes, expected):
    root = fixture_repo(tmp_path, {'agents/a.md': GREP_BESIDE_BASH},
                        register=FIXTURE_REGISTER + exception_toml({**GAP, **changes}))
    assert cc.run(root) == expected


def test_repo_passes():
    '''The real repo, with the register the owner gate filled, is clean (R3.5).'''
    assert cc.run(cc.REPO) == []


def test_unreadable_register_is_a_setup_error(tmp_path):
    '''Any OSError reading the register is a setup error, not only a missing file.'''
    (tmp_path / cc.REGISTER).mkdir(parents=True)  # reading a directory raises IsADirectoryError
    with pytest.raises(cc.SetupError, match='cannot read'):
        cc.load_register(tmp_path)


def test_permission_denied_on_the_register_is_a_setup_error(tmp_path, monkeypatch):
    write_tree(tmp_path, {cc.REGISTER: "[guide]\npath = 'guide.md'\n"})

    def deny(self, *args, **kwargs):
        raise PermissionError(13, 'Permission denied')
    monkeypatch.setattr(cc.Path, 'read_text', deny)
    with pytest.raises(cc.SetupError, match='cannot read.*Permission denied'):
        cc.load_register(tmp_path)


def test_main_exits_2_when_the_register_cannot_be_read(tmp_path, capsys):
    (tmp_path / cc.REGISTER).mkdir(parents=True)
    assert cc.main(tmp_path) == 2
    captured = capsys.readouterr()
    assert captured.out == ''
    assert captured.err.startswith(f'{cc.REGISTER}: cannot read')


def no_git_repo(tmp_path, monkeypatch):
    '''A fixture tree that is not a git repo, however the tests are run.'''
    monkeypatch.setenv('GIT_CEILING_DIRECTORIES', str(tmp_path.parent))
    monkeypatch.setenv('LC_ALL', 'C')
    write_tree(tmp_path, {'guide.md': FIXTURE_GUIDE, cc.REGISTER: FIXTURE_REGISTER})
    return tmp_path


def test_kept_files_setup_error_carries_gits_reason(tmp_path, monkeypatch):
    root = no_git_repo(tmp_path, monkeypatch)
    with pytest.raises(cc.SetupError, match='not a git repository'):
        cc.kept_files(root)


def test_kept_files_setup_error_without_git_has_no_stderr(tmp_path, monkeypatch):
    '''No git binary: an OSError, so there is no stderr to carry.'''
    root = no_git_repo(tmp_path, monkeypatch)
    monkeypatch.setenv('PATH', str(tmp_path / 'empty'))
    with pytest.raises(cc.SetupError, match='cannot list the files git keeps'):
        cc.kept_files(root)


def test_main_exits_2_when_git_cannot_list_files(tmp_path, monkeypatch, capsys):
    root = no_git_repo(tmp_path, monkeypatch)
    assert cc.main(root) == 2
    captured = capsys.readouterr()
    assert captured.out == ''
    assert 'cannot list the files git keeps' in captured.err
    assert 'not a git repository' in captured.err


# ---- #34: branches the first pass left untested ---------------------------


def test_anchor_like_line_inside_a_fence_is_not_a_stray_anchor():
    text = f'## A\n<!-- cc: a.overview -->\n\n{FENCE}markdown\n<!-- cc: a.sample -->\n{FENCE}\n'
    sections, violations = cc.guide_sections(text, 'guide.md')
    assert [s.id for s in sections] == ['a.overview']
    assert violations == []


def test_cc_guide_markers_are_never_anchors():
    '''Drift Stage 2 puts <!-- cc-guide: --> lines beside the anchors; they
    must read as neither a stray nor a malformed anchor.'''
    text = ('## A\n<!-- cc: a.overview -->\n<!-- cc-guide: sha=abc123 -->\n\nBody.\n'
            '<!-- cc-guide: stamp -->\n### B\n<!-- cc: a.one -->\n')
    sections, violations = cc.guide_sections(text, 'guide.md')
    assert [s.id for s in sections] == ['a.overview', 'a.one']
    assert violations == []


def test_cc_guide_marker_directly_under_a_heading_is_no_anchor():
    '''The marker is not an anchor: the heading lacks one, and says so, instead
    of reporting a malformed anchor.'''
    text = '## A\n<!-- cc-guide: sha=abc123 -->\n<!-- cc: a.overview -->\n'
    _, violations = cc.guide_sections(text, 'guide.md')
    assert rendered(violations) == [
        "guide.md: anchor (-): line 1: heading '## A' has no anchor on its next line",
        'guide.md: anchor (-): line 3: anchor is not directly under a heading',
    ]


@pytest.mark.parametrize('text', ['## A', '## A\n'])
def test_heading_on_the_last_line_has_no_anchor(text):
    sections, violations = cc.guide_sections(text, 'guide.md')
    assert [s.id for s in sections] == [None]
    assert rendered(violations) == [
        "guide.md: anchor (-): line 1: heading '## A' has no anchor on its next line"]


def test_unmapped_and_check_citations_must_name_anchors():
    raw = tomllib.loads(FIXTURE_REGISTER)
    raw['unmapped']['z.gone'] = 'Cited by mistake.'
    raw['check'][0]['sections'] = ['a.typo']
    reg, _ = cc.parse_register(raw)
    assert rendered(cc.section_violations(reg, FIXTURE_ANCHORS)) == [
        f'{cc.REGISTER}: section-id (z.gone): [unmapped] cites a section with no anchor in the guide',
        f'{cc.REGISTER}: section-id (a.typo): check claude-md-size cites a section with no anchor in the guide',
    ]


@pytest.mark.parametrize('raw', [
    {}, {'guide': 'guide.md'}, {'guide': {}}, {'guide': {'path': ''}}, {'guide': {'path': 7}}])
def test_missing_guide_path_is_a_setup_error(tmp_path, raw):
    with pytest.raises(cc.SetupError, match=r'\[guide\] path is missing'):
        cc.load_guide(tmp_path, raw)


def test_main_exits_2_when_the_register_names_no_guide(tmp_path, capsys):
    root = fixture_repo(tmp_path, register=FIXTURE_REGISTER.replace("[guide]\npath = 'guide.md'\n", ''))
    assert cc.main(root) == 2
    assert capsys.readouterr().err == f'{cc.REGISTER}: [guide] path is missing\n'


def raw_register(**changes):
    '''The fixture register as a dict, with top-level keys replaced.'''
    return {**tomllib.loads(FIXTURE_REGISTER), **changes}


def register_problems(raw):
    return [v.message for v in cc.parse_register(raw)[1]]


@pytest.mark.parametrize('raw, expected', [
    (raw_register(kinds=['agent']), ['[kinds] must be a table of kinds']),
    (raw_register(kinds={'agent': 'text'}), ['kinds.agent must be a table']),
    (raw_register(unmapped='text'), ['[unmapped] must be a table']),
    (raw_register(check={'id': 'x'}), ['[[check]] must be an array of tables']),
    (raw_register(check=['text']), ['check #1 must be a table']),
])
def test_register_shape_problems_are_violations(raw, expected):
    assert expected[0] in register_problems(raw)


def test_register_shape_problems_leave_nothing_usable():
    reg, _ = cc.parse_register({'kinds': 'x', 'unmapped': 'x', 'check': 'x'})
    assert (reg.kinds, reg.unmapped, reg.checks) == ({}, {}, [])


def kind_with(**fields):
    raw = tomllib.loads(FIXTURE_REGISTER)
    raw['kinds']['agent'] = {'description': 'Agents.', 'globs': ['agents/*.md'],
                             'sections': ['a.overview'], **fields}
    return raw


def test_exclude_must_be_a_list_of_strings():
    reg, violations = cc.parse_register(kind_with(exclude='hooks/test_*.py'))
    assert [v.message for v in violations] == ['kinds.agent: exclude must be a list of strings']
    assert 'agent' not in reg.kinds


def test_a_kind_without_exclude_gets_an_empty_list():
    reg, violations = cc.parse_register(kind_with())
    assert violations == [] and reg.kinds['agent'].exclude == []


def test_kind_sections_must_be_a_non_empty_list():
    reg, violations = cc.parse_register(kind_with(sections=[]))
    assert [v.message for v in violations] == [
        'kinds.agent: sections must be a non-empty list of strings']
    assert 'agent' not in reg.kinds


def test_kind_description_is_required_but_not_structural():
    reg, violations = cc.parse_register(kind_with(description='  '))
    assert [v.message for v in violations] == ['kinds.agent: description must be a non-empty string']
    assert 'agent' in reg.kinds


def check_with(**fields):
    raw = tomllib.loads(FIXTURE_REGISTER)
    raw['check'][0] = {**raw['check'][0], **fields}
    return raw


def test_check_without_an_id_is_labelled_by_position():
    reg, violations = cc.parse_register(check_with(id=''))
    assert [v.message for v in violations] == ['check #1: id must be a non-empty string']
    assert 'claude-md-size' not in [c.id for c in reg.checks] and len(reg.checks) == 7


def test_check_rule_is_required_but_not_structural():
    reg, violations = cc.parse_register(check_with(rule=' '))
    assert [v.message for v in violations] == ['check claude-md-size: rule must be a non-empty string']
    assert reg.checks[0].id == 'claude-md-size'


@pytest.mark.parametrize('fields, message', [
    ({'kind': 'agent'}, None),
    ({'kind': ['agent', 'rule']}, None),
    ({'kind': 5}, 'check claude-md-size: kind must name a kind, or list kinds'),
    ({'kind': []}, 'check claude-md-size: kind must name a kind, or list kinds'),
    ({'sections': 'a.one'}, 'check claude-md-size: sections must be a non-empty list of strings'),
])
def test_check_kind_and_sections_shapes(fields, message):
    reg, violations = cc.parse_register(check_with(**fields))
    assert [v.message for v in violations] == ([message] if message else [])
    assert (reg.checks[0].id == 'claude-md-size') == (message is None)


def test_kept_files_lists_untracked_files_and_drops_deleted_ones(tmp_path):
    '''--cached lists a tracked file deleted from the working tree; kept_files
    does not, and keeps a dangling symlink, which exists() calls missing.'''
    root = git_repo(tmp_path, {'gone.md': 'x\n', 'stays.md': 'x\n'})
    subprocess.run(['git', 'add', '.'], cwd=root, env=cc.git_env(), check=True)
    (root / 'gone.md').unlink()
    os.symlink('nowhere.md', root / 'dangling.md')
    (root / 'untracked.md').write_text('x\n')
    assert cc.kept_files(root) == ['dangling.md', 'stays.md', 'untracked.md']


def test_stop_hook_guard_reads_only_stop_hooks(tmp_path):
    write_tree(tmp_path, {'hooks/README.md': json_block(hooks_tree('PreToolUse', 'uv run ruff check .'))})
    assert cc.check_stop_hook_guard(tmp_path, ['hooks/README.md'], {}) == []


def test_stop_hook_guard_survives_a_command_shlex_rejects(tmp_path):
    write_tree(tmp_path, {
        'hooks/README.md': json_block(hooks_tree('Stop', '"$CLAUDE_PROJECT_DIR/.claude/hooks/ruff-check.sh')),
        'hooks/ruff-check.sh': STOP_SCRIPT,
    })
    assert cc.check_stop_hook_guard(tmp_path, ['hooks/README.md', 'hooks/ruff-check.sh'], {}) == [
        cc.Finding('hooks/README.md', 'JSON block at line 1: Stop command '
                   "'\"$CLAUDE_PROJECT_DIR/.claude/hooks/ruff-check.sh' names no hook script in the repo")]


def test_stop_hook_guard_leaves_parse_failures_to_hook_dir_quoted(tmp_path):
    write_tree(tmp_path, {'hooks/README.md': f'{FENCE}json\n{{"hooks": }}\n{FENCE}\n'})
    assert cc.check_stop_hook_guard(tmp_path, ['hooks/README.md'], {}) == []


BROKEN_BLOCK = f'{FENCE}json\n{{"hooks": }}\n{FENCE}\n'
BROKEN_LINE = ('hooks/README.md: hook-dir-quoted (a.one): '
               'JSON block at line 1 does not parse (Expecting value)')


def test_a_parse_failure_is_reported_once_when_both_hook_checks_run(tmp_path):
    root = fixture_repo(tmp_path, {'hooks/README.md': BROKEN_BLOCK})
    assert cc.run(root) == [BROKEN_LINE]


def test_parse_failure_goes_quiet_without_hook_dir_quoted_but_the_run_is_not_clean(tmp_path):
    '''stop-hook-guard drops parse failures, so with hook-dir-quoted's entry
    gone nothing reports the block, yet the missing entry fails the run.'''
    start = FIXTURE_REGISTER.index("[[check]]\nid = 'hook-dir-quoted'")
    end = FIXTURE_REGISTER.index("[[check]]\nid = 'stop-hook-guard'")
    root = fixture_repo(tmp_path, {'hooks/README.md': BROKEN_BLOCK},
                        register=FIXTURE_REGISTER[:start] + FIXTURE_REGISTER[end:])
    assert cc.run(root) == [
        'build/check_conformance.py: check-impl (-): implementation hook-dir-quoted has no [[check]] entry']


def test_unparseable_json_file_is_a_violation(tmp_path):
    write_tree(tmp_path, {'.claude/settings.json': '{"hooks": }'})
    assert cc.check_hook_dir_quoted(tmp_path, ['.claude/settings.json'], {}) == [
        cc.Finding('.claude/settings.json', 'file does not parse (Expecting value)', waivable=False)]


@pytest.mark.parametrize('command, states', [
    ("echo '\\' $CLAUDE_PROJECT_DIR/a.sh", ['unquoted']),
    ("echo '\\$CLAUDE_PROJECT_DIR'", ['single-quoted']),
    ('"$CLAUDE_PROJECT_DIR"/a.sh "$CLAUDE_PROJECT_DIR"', []),
    ('$CLAUDE_PROJECT_DIR/a.sh $CLAUDE_PROJECT_DIR/b.sh', ['unquoted', 'unquoted']),
    ('"$CLAUDE_PROJECT_DIR"/a.sh $CLAUDE_PROJECT_DIR/b.sh', ['unquoted']),
    ("$CLAUDE_PROJECT_DIR/a.sh '${CLAUDE_PROJECT_DIR}'", ['unquoted', 'single-quoted']),
])
def test_unquoted_var_uses_reports_every_use(command, states):
    assert cc.unquoted_var_uses(command, 'CLAUDE_PROJECT_DIR') == states


def test_each_unquoted_use_is_its_own_finding(tmp_path):
    write_tree(tmp_path, {'hooks/README.md': json_block(
        hooks_tree('Stop', '$CLAUDE_PROJECT_DIR/a.sh $CLAUDE_PROJECT_DIR/b.sh'))})
    assert cc.check_hook_dir_quoted(tmp_path, ['hooks/README.md'], {}) == [
        cc.Finding('hooks/README.md', 'JSON block at line 1: Stop command leaves $CLAUDE_PROJECT_DIR unquoted')] * 2


def test_a_file_in_two_of_a_checks_kinds_is_checked_once(tmp_path):
    register = FIXTURE_REGISTER.replace("globs = ['.claude/settings.json']",
                                        "globs = ['.claude/settings.json', 'hooks/README.md']")
    root = fixture_repo(tmp_path, {'hooks/README.md': json_block(
        hooks_tree('PreToolUse', '$CLAUDE_PROJECT_DIR/a.sh'))}, register=register)
    assert cc.run(root) == [
        'hooks/README.md: hook-dir-quoted (a.one): JSON block at line 1: '
        'PreToolUse command leaves $CLAUDE_PROJECT_DIR unquoted']


def test_a_check_listed_twice_runs_once(tmp_path):
    register = FIXTURE_REGISTER + """
[[check]]
id = 'hook-dir-quoted'
kind = ['hook', 'settings']
sections = ['a.one']
type = 'advice'
rule = 'Listed twice.'
enforced_by = 'check_conformance'
"""
    root = fixture_repo(tmp_path, {'hooks/README.md': json_block(
        hooks_tree('PreToolUse', '$CLAUDE_PROJECT_DIR/a.sh'))}, register=register)
    assert cc.run(root) == [
        f'{cc.REGISTER}: duplicate-id (-): check ID hook-dir-quoted appears 2 times',
        'hooks/README.md: hook-dir-quoted (a.one): JSON block at line 1: '
        'PreToolUse command leaves $CLAUDE_PROJECT_DIR unquoted',
    ]


PATHS_RULES = {
    'rules/empty.md': '---\npaths: []\n---\nRule.\n',
    'rules/scalar.md': '---\npaths: src/*.py\n---\nRule.\n',
    'rules/null.md': '---\npaths:\n---\nRule.\n',
    'rules/absent.md': '---\ndescription: x\n---\nRule.\n',
}


def test_rule_paths_on_an_always_on_rule_flags_any_paths_value_but_null(tmp_path):
    '''An always-on rule must not set paths: an empty list or a scalar counts as
    setting it; a bare `paths:` (null) and an absent key do not.'''
    write_tree(tmp_path, PATHS_RULES)
    files = sorted(PATHS_RULES)
    assert cc.check_rule_paths(tmp_path, files, {'always_on': files}) == [
        cc.Finding('rules/empty.md', 'always_on lists this rule, but it sets paths'),
        cc.Finding('rules/scalar.md', 'always_on lists this rule, but it sets paths'),
    ]


def test_rule_paths_on_a_lazy_rule_flags_empty_scalar_null_and_absent_paths(tmp_path):
    write_tree(tmp_path, PATHS_RULES)
    files = sorted(PATHS_RULES)
    message = 'frontmatter sets no non-empty paths list, so the rule loads in every session'
    assert cc.check_rule_paths(tmp_path, files, {'always_on': []}) == [
        cc.Finding(f, message) for f in files]


def test_output_is_sorted_not_in_discovery_order(tmp_path):
    '''A register violation is found before a file violation; the output sorts
    them by file, so agents/ comes first.'''
    register = FIXTURE_REGISTER.replace("[unmapped]\n'b.overview' = 'Governs no fixture file.'\n", '')
    root = fixture_repo(tmp_path, {'agents/a.md': GREP_BESIDE_BASH}, register=register)
    lines = cc.run(root)
    assert [line.split(':')[0] for line in lines] == ['agents/a.md', cc.REGISTER]


def test_waiver_is_not_stale_when_its_file_could_not_be_read(tmp_path):
    '''The waived file's only finding is unwaivable (a block that does not
    parse), so the check could not evaluate it: the waiver is neither stale
    nor does it hide the finding.'''
    hook_gap = {**GAP, 'id': 'hook-dir', 'check': 'hook-dir-quoted', 'sections': ['a.one'],
                'artifacts': ['hooks/README.md'], 'protects': None}
    root = fixture_repo(tmp_path, {'hooks/README.md': BROKEN_BLOCK},
                        register=FIXTURE_REGISTER + exception_toml(hook_gap))
    assert cc.run(root) == [BROKEN_LINE]


def exception_register(raw_exception):
    '''FIXTURE_REGISTER with one [[exception]] built from a dict (so a value TOML
    helper cannot spell, such as a boolean, still reaches parse_exceptions).'''
    raw = tomllib.loads(FIXTURE_REGISTER)
    raw['exception'] = raw_exception
    return raw


def parse_exception_problems(raw, tmp_path):
    reg, _ = cc.parse_register(raw)
    write_tree(tmp_path, {'agents/a.md': GREP_BESIDE_BASH, 'CLAUDE.md': 'Short.\n'})
    entries, violations = cc.parse_exceptions(
        raw, reg, FIXTURE_ANCHORS, ['agents/a.md', 'CLAUDE.md'], tmp_path)
    return entries, [v.message for v in violations]


def clean_gap(**changes):
    return {k: v for k, v in {**GAP, **changes}.items() if v is not None}


def test_exceptions_must_be_an_array_of_tables(tmp_path):
    entries, problems = parse_exception_problems(exception_register('text'), tmp_path)
    assert (entries, problems) == ([], ['[[exception]] must be an array of tables'])


def test_an_exception_entry_must_be_a_table(tmp_path):
    entries, problems = parse_exception_problems(exception_register([7, clean_gap()]), tmp_path)
    assert problems == ['exception #1 must be a table']
    assert [e.id for e in entries] == ['grep-beside-bash']


@pytest.mark.parametrize('changes, problem', [
    ({'id': ''}, 'exception #1: id must be a non-empty string'),
    ({'type': None}, 'exception grep-beside-bash: type must be deviation or gap'),
    ({'guide': ' '}, 'exception grep-beside-bash: guide must be a non-empty string'),
    ({'reason': None}, 'exception grep-beside-bash: reason must be a non-empty string'),
    ({'sections': 'a.overview'}, 'exception grep-beside-bash: sections must be a non-empty list of strings'),
    ({'sections': []}, 'exception grep-beside-bash: sections must be a non-empty list of strings'),
    ({'protects': 'gemini'}, 'exception grep-beside-bash: protects may list only codex and gemini'),
    ({'artifacts': None}, 'exception grep-beside-bash: artifacts must be a non-empty list of strings'),
    ({'artifacts': []}, 'exception grep-beside-bash: artifacts must be a non-empty list of strings'),
    ({'artifacts': 'agents/a.md'}, 'exception grep-beside-bash: artifacts must be a non-empty list of strings'),
    ({'ceiling': True}, 'exception grep-beside-bash: ceiling applies only to a numeric check (claude-md-size)'),
])
def test_exception_field_problems_are_violations(tmp_path, changes, problem):
    entries, problems = parse_exception_problems(exception_register([clean_gap(**changes)]), tmp_path)
    assert problems == [problem]
    # A usable id alone never keeps the entry: an unusable id or artifacts list drops it.
    if 'id' in changes or 'artifacts' in changes:
        assert entries == []


def test_a_boolean_ceiling_is_not_an_integer_ceiling(tmp_path):
    waiver = clean_gap(id='md-size', check='claude-md-size', sections=['a.one'],
                       artifacts=['CLAUDE.md'], protects=['gemini'], ceiling=True)
    entries, problems = parse_exception_problems(exception_register([waiver]), tmp_path)
    assert problems == ['exception md-size: a waiver of claude-md-size needs an integer ceiling']
    assert [(e.id, e.ceiling) for e in entries] == [('md-size', None)]


def test_a_numeric_waiver_keeps_its_ceiling(tmp_path):
    waiver = clean_gap(id='md-size', check='claude-md-size', sections=['a.one'],
                       artifacts=['CLAUDE.md'], protects=None, ceiling=225)
    entries, problems = parse_exception_problems(exception_register([waiver]), tmp_path)
    assert problems == []
    assert [(e.id, e.check, e.artifacts, e.ceiling) for e in entries] == [
        ('md-size', 'claude-md-size', ['CLAUDE.md'], 225)]


def test_a_checkless_exception_matches_artifacts_by_glob(tmp_path):
    deviation = clean_gap(id='tools', type='deviation', check=None, tracked_in=None,
                          revisit='later', artifacts=['agents/*.md', 'CLAUDE.md'])
    entries, problems = parse_exception_problems(exception_register([deviation]), tmp_path)
    assert problems == []
    assert [(e.id, e.check, e.ceiling) for e in entries] == [('tools', None, None)]


# ---- #39: expansion forms and substitutions --------------------------------


@pytest.mark.parametrize('command, states', [
    # ${VAR<operator>...} forms are uses of VAR, quoted or not.
    ('${CLAUDE_PROJECT_DIR:-/x}/a.sh', ['unquoted']),
    ('${CLAUDE_PROJECT_DIR-/x}/a.sh', ['unquoted']),
    ('${CLAUDE_PROJECT_DIR:?unset}/a.sh', ['unquoted']),
    ('${CLAUDE_PROJECT_DIR%/}/a.sh', ['unquoted']),
    ("'${CLAUDE_PROJECT_DIR:-/x}'/a.sh", ['single-quoted']),
    ('"${CLAUDE_PROJECT_DIR:-/x}/a.sh"', []),
    ('"${CLAUDE_PROJECT_DIR:-$HOME}"/a.sh', []),
    ('${CLAUDE_PROJECT_DIRX:-/x}/a.sh', []),
    ('${OTHER:-$CLAUDE_PROJECT_DIR}/a.sh', ['unquoted']),
    # A command substitution starts a fresh quoting context.
    ('"$(dirname "$CLAUDE_PROJECT_DIR")/a.sh"', []),
    ('$(dirname "$CLAUDE_PROJECT_DIR")/a.sh', []),
    ('"$(cat "${CLAUDE_PROJECT_DIR:-/x}/v")"/a.sh', []),
    ('"$(cat $CLAUDE_PROJECT_DIR/x)"/a.sh', ['unquoted']),
    ('"$(cd "$(dirname "$CLAUDE_PROJECT_DIR")" && pwd)"/a.sh', []),
    ('"$(cd "$(dirname $CLAUDE_PROJECT_DIR)" && pwd)"/a.sh', ['unquoted']),
    ('"$( (cat "$CLAUDE_PROJECT_DIR") )"/a.sh', []),
    ('"$( (cat x); echo $CLAUDE_PROJECT_DIR )"', ['unquoted']),
    ('"$((1 + 2))$CLAUDE_PROJECT_DIR"', []),
    ('"$(echo a)"$CLAUDE_PROJECT_DIR/a.sh', ['unquoted']),
    ("'$(echo $CLAUDE_PROJECT_DIR)'", ['single-quoted']),
    ('"\\$(echo $CLAUDE_PROJECT_DIR)"', []),
])
def test_unquoted_var_uses_handle_expansion_forms_and_substitutions(command, states):
    assert cc.unquoted_var_uses(command, 'CLAUDE_PROJECT_DIR') == states


def test_hook_dir_quoted_flags_a_default_expansion_and_passes_a_quoted_substitution(tmp_path):
    write_tree(tmp_path, {'hooks/README.md': json_block({'hooks': {
        'PreToolUse': [{'hooks': [
            {'type': 'command', 'command': '${CLAUDE_PROJECT_DIR:-.}/a.sh'},
            {'type': 'command', 'command': '"$(dirname "$CLAUDE_PROJECT_DIR")/b.sh"'}]}]}})})
    assert cc.check_hook_dir_quoted(tmp_path, ['hooks/README.md'], {}) == [
        cc.Finding('hooks/README.md', 'JSON block at line 1: PreToolUse command leaves $CLAUDE_PROJECT_DIR unquoted')]


# ---- #40: stop-hook-guard sees past a runner --------------------------------


@pytest.mark.parametrize('words, script', [
    (['hooks/a.sh'], 'hooks/a.sh'),
    (['uv', 'run', 'hooks/a.py'], 'hooks/a.py'),
    (['uv', 'run', '--script', 'hooks/a.py'], 'hooks/a.py'),
    (['uv', 'run', '--with', 'pyyaml', '--python', '3.13', 'hooks/a.py'], 'hooks/a.py'),
    (['uv', 'run', '--with=pyyaml', 'hooks/a.py', '--flag'], 'hooks/a.py'),
    (['python3', 'hooks/a.py'], 'hooks/a.py'),
    (['python', '-u', 'hooks/a.py'], 'hooks/a.py'),
    (['/usr/bin/python3.13', 'hooks/a.py'], 'hooks/a.py'),
    (['uv', 'run', 'python3', 'hooks/a.py'], 'hooks/a.py'),
    (['uv', 'run', 'ruff', 'check', '.'], 'ruff'),
    (['python3', '-m', 'pytest'], 'pytest'),
    (['python3', '-c', 'print(1)'], 'print(1)'),
    (['uv', 'sync'], 'uv'),
    (['uv', 'run'], None),
    (['python3'], None),
    ([], None),
])
def test_script_word_looks_past_a_known_runner(words, script):
    assert cc.script_word(words) == script


def stop_tree(command, script_name, source):
    return {'hooks/README.md': json_block(hooks_tree('Stop', command)), script_name: source}


@pytest.mark.parametrize('command, script', [
    ('uv run "$CLAUDE_PROJECT_DIR"/.claude/hooks/ruff-check.py', 'hooks/ruff-check.py'),
    ('uv run --with pyyaml hooks/ruff-check.py', 'hooks/ruff-check.py'),
    ('python3 "$CLAUDE_PROJECT_DIR"/.claude/hooks/ruff-check.py', 'hooks/ruff-check.py'),
])
def test_stop_hook_guard_resolves_the_script_after_a_runner(tmp_path, command, script):
    write_tree(tmp_path, stop_tree(command, script, '# reads stop_hook_active\n'))
    assert cc.check_stop_hook_guard(tmp_path, ['hooks/README.md', script], {}) == []


def test_stop_hook_guard_flags_an_unguarded_script_behind_a_runner(tmp_path):
    write_tree(tmp_path, stop_tree('uv run hooks/gate.py', 'hooks/gate.py', 'import sys\n'))
    assert cc.check_stop_hook_guard(tmp_path, ['hooks/README.md', 'hooks/gate.py'], {}) == [
        cc.Finding('hooks/README.md', 'JSON block at line 1: Stop command runs hooks/gate.py, '
                                      'which never reads stop_hook_active')]


@pytest.mark.parametrize('command', ['uv run ruff check .', 'uv run', 'python3 -m pytest', 'python3'])
def test_stop_hook_guard_still_flags_a_runner_with_no_repo_script(tmp_path, command):
    write_tree(tmp_path, stop_tree(command, 'hooks/ruff-check.py', '# stop_hook_active\n'))
    assert cc.check_stop_hook_guard(tmp_path, ['hooks/README.md', 'hooks/ruff-check.py'], {}) == [
        cc.Finding('hooks/README.md', f'JSON block at line 1: Stop command {command!r} '
                                      'names no hook script in the repo')]
