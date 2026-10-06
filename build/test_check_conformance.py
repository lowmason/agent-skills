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
# carries every check_conformance check and one check_frontmatter entry,
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
globs = ['rules/*.md', '.claude/rules/**']
sections = ['a.one']

[kinds.settings]
description = 'Project settings.'
globs = ['.claude/settings.json']
sections = ['a.one']

[kinds.skill]
description = 'Skills.'
globs = ['skills/*/SKILL.md']
sections = ['a.one']

[kinds.command]
description = 'Commands.'
globs = ['commands/*.md']
sections = ['a.one']

[kinds.skill-bundle]
description = 'Every file under a skill.'
globs = ['skills/*/**']
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
id = 'compaction-window'
kind = 'skill'
sections = ['a.one']
type = 'advice'
rule = 'Fixture rule.'
enforced_by = 'check_conformance'
tokens = 5000
chars_per_token = 4
headings = ['STOP', 'Red Flags']

[[check]]
id = 'description-person'
kind = 'skill'
sections = ['a.one']
type = 'advice'
rule = 'Fixture rule.'
enforced_by = 'check_conformance'
pronouns = ['i', 'we', 'you', 'your']

[[check]]
id = 'trigger-phrase-presence'
kind = 'skill'
sections = ['a.one']
type = 'advice'
rule = 'Fixture rule.'
enforced_by = 'check_conformance'
markers = ['trigger on']

[[check]]
id = 'substitution-hazard'
kind = 'skill'
sections = ['a.one']
type = 'advice'
rule = 'Fixture rule.'
enforced_by = 'check_conformance'

[[check]]
id = 'orphan-bundled-file'
kind = 'skill-bundle'
sections = ['a.one']
type = 'advice'
rule = 'Fixture rule.'
enforced_by = 'check_conformance'
exempt = ['SKILL.md', 'README.md']
tests = ['test_*']

[[check]]
id = 'skill-command-name-collision'
kind = ['skill', 'command']
sections = ['a.one']
type = 'advice'
rule = 'Fixture rule.'
enforced_by = 'check_conformance'

[[check]]
id = 'command-frontmatter-keys'
kind = 'command'
sections = ['a.one']
type = 'advice'
rule = 'Fixture rule.'
enforced_by = 'check_conformance'
fields = ['description', 'model']

[[check]]
id = 'builtin-name-shadow'
kind = ['skill', 'command']
sections = ['a.one']
type = 'advice'
rule = 'Fixture rule.'
enforced_by = 'check_conformance'
builtins = ['help', 'model', 'compact']

[[check]]
id = 'reserved-skill-name'
kind = 'skill-bundle'
sections = ['a.one']
type = 'advice'
rule = 'Fixture rule.'
enforced_by = 'check_conformance'
reserved = ['synced']

[[check]]
id = 'known-agent-tools'
kind = 'agent'
sections = ['a.overview']
type = 'fact'
rule = 'Known tools.'
enforced_by = 'check_frontmatter'

# The checks below are tested by direct calls. Those bound to the settings kind
# stay off the fixture repos on purpose: no run() fixture populates it, so the
# exact-output tests above keep their expected lists.
[[check]]
id = 'agent-name-form'
kind = 'agent'
sections = ['a.overview']
type = 'fact'
rule = 'Lowercase-hyphenated names.'
enforced_by = 'check_conformance'
allow = ['Explore']

[[check]]
id = 'agent-model-available'
kind = ['agent', 'settings']
sections = ['a.overview']
type = 'fact'
rule = 'Models are available.'
enforced_by = 'check_conformance'
exempt = ['inherit']

[[check]]
id = 'agent-name-unique'
kind = 'settings'
sections = ['a.one']
type = 'fact'
rule = 'Names are unique.'
enforced_by = 'check_conformance'

[[check]]
id = 'command-substitution-tokens'
kind = 'settings'
sections = ['a.one']
type = 'fact'
rule = 'Declare substitution tokens.'
enforced_by = 'check_conformance'

[[check]]
id = 'rule-always-on-claim'
kind = 'rule'
sections = ['a.one']
type = 'fact'
rule = 'Fixture entry.'
enforced_by = 'check_conformance'
phrases = ['always-on']

[[check]]
id = 'hook-readme-exit-claims'
kind = 'hook'
sections = ['a.one']
type = 'fact'
rule = 'Fixture entry.'
enforced_by = 'check_conformance'

[[check]]
id = 'hook-scripts-executable'
kind = 'settings'
sections = ['a.one']
type = 'fact'
rule = 'Fixture entry.'
enforced_by = 'check_conformance'

[[check]]
id = 'hook-python-deps'
kind = 'hook'
sections = ['a.one']
type = 'fact'
rule = 'Fixture entry.'
enforced_by = 'check_conformance'

[[check]]
id = 'allow-rule-compound-operators'
kind = ['hook', 'settings']
sections = ['a.one']
type = 'fact'
rule = 'Fixture entry.'
enforced_by = 'check_conformance'

[[check]]
id = 'inert-runner-allow-rules'
kind = 'hook'
sections = ['a.one']
type = 'fact'
rule = 'Fixture entry.'
enforced_by = 'check_conformance'
runners = ['uv run']

[[check]]
id = 'hook-install-verify-step'
kind = 'settings'
sections = ['a.one']
type = 'fact'
rule = 'Fixture entry.'
enforced_by = 'check_conformance'
blocking_events = ['PreToolUse', 'Stop']

[[check]]
id = 'claude-md-import-resolves'
kind = 'claude-md'
sections = ['a.one']
type = 'fact'
rule = 'Fixture entry.'
enforced_by = 'check_conformance'
max_hops = 4

[[check]]
id = 'local-md-ignored'
kind = 'settings'
sections = ['a.one']
type = 'advice'
rule = 'Fixture entry.'
enforced_by = 'check_conformance'

[[check]]
id = 'claude-md-count-claims'
kind = 'claude-md'
sections = ['a.one']
type = 'advice'
rule = 'Fixture entry.'
enforced_by = 'check_conformance'
nouns = ['tests']
allow = []


[[check]]
id = 'hook-var-quoted'
kind = ['hook', 'settings']
sections = ['a.one']
type = 'advice'
rule = 'Quote a variable that starts a script path.'
enforced_by = 'check_conformance'
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
    assert sorted(reg.kinds) == ['claude-md', 'command', 'hook', 'rule', 'settings', 'skill', 'skill-bundle']
    assert [c.id for c in reg.checks] == [
        'claude-md-size', 'stop-hook-guard', 'agent-fields',
        'readonly-agent-tools', 'bash-search-tools',
        'compaction-window', 'description-person', 'trigger-phrase-presence',
        'substitution-hazard', 'orphan-bundled-file', 'skill-command-name-collision',
        'command-frontmatter-keys', 'builtin-name-shadow', 'reserved-skill-name',
        'known-agent-tools',
        'agent-name-form', 'agent-model-available', 'agent-name-unique',
        'command-substitution-tokens', 'rule-always-on-claim',
        'hook-readme-exit-claims', 'hook-scripts-executable', 'hook-python-deps',
        'allow-rule-compound-operators', 'inert-runner-allow-rules',
        'hook-install-verify-step', 'claude-md-import-resolves', 'local-md-ignored',
        'claude-md-count-claims', 'hook-var-quoted']
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


# ---------------------------------------------------------------------------
# Skill and command checks: compaction-window, description-person,
# trigger-phrase-presence, substitution-hazard, orphan-bundled-file,
# skill-command-name-collision, command-frontmatter-keys, builtin-name-shadow,
# reserved-skill-name.
# ---------------------------------------------------------------------------

def skill_md(description='Use when testing.', body='Body.\n', **extra):
    '''A SKILL.md with a one-line description and any further frontmatter keys.'''
    keys = ''.join(f'{k}: {v}\n' for k, v in extra.items())
    return f'---\nname: s\ndescription: {description}\n{keys}---\n{body}'


WINDOW_PARAMS = {'tokens': 20, 'chars_per_token': 1,
                 'headings': ['STOP', 'Red Flags', 'Critical']}


def test_compaction_window_passes_a_short_body_and_late_ordinary_headings(tmp_path):
    write_tree(tmp_path, {
        'skills/a/SKILL.md': skill_md(body='## Short\nShort.\n'),
        'skills/b/SKILL.md': skill_md(body='## Steps\n' + 'x' * 30 + '\n## Reference\nMore.\n'),
    })
    files = ['skills/a/SKILL.md', 'skills/b/SKILL.md']
    # b is over the 20-token window but its late heading is not critical-sounding.
    assert cc.check_compaction_window(tmp_path, files[:1], WINDOW_PARAMS) == []
    assert [f.message for f in cc.check_compaction_window(tmp_path, files[1:], WINDOW_PARAMS)] == [
        'body is about 59 tokens; compaction re-attaches only the first 20']


def test_compaction_window_flags_a_critical_heading_past_the_window(tmp_path):
    body = ('## Red Flags\nEarly, inside the window.\n'
            + 'x' * 30 + '\n'
            + '## STOP: Before Moving On\nLate.\n'
            + f'{FENCE}\n## Critical inside a fence\n{FENCE}\n'
            + '## Critical Rules\nLate.\n')
    write_tree(tmp_path, {'skills/a/SKILL.md': skill_md(body=body)})
    found = cc.check_compaction_window(tmp_path, ['skills/a/SKILL.md'], WINDOW_PARAMS)
    assert [(f.file, f.message) for f in found] == [
        ('skills/a/SKILL.md', f'body is about {len(body)} tokens; compaction re-attaches only the first 20'),
        ('skills/a/SKILL.md', "line 8: heading '## STOP: Before Moving On' starts past the first 20 tokens, so compaction drops it"),
        ('skills/a/SKILL.md', "line 13: heading '## Critical Rules' starts past the first 20 tokens, so compaction drops it"),
    ]


def test_compaction_window_ignores_headings_when_the_body_fits(tmp_path):
    write_tree(tmp_path, {'skills/a/SKILL.md': skill_md(body='## STOP\nAll early.\n')})
    assert cc.check_compaction_window(tmp_path, ['skills/a/SKILL.md'], WINDOW_PARAMS) == []


PERSON_PARAMS = {'pronouns': ['i', 'we', 'you', 'your']}


def test_description_person_passes_third_person_and_quoted_pronouns(tmp_path):
    write_tree(tmp_path, {
        'skills/a/SKILL.md': skill_md('Use when the user asks "can you help" or \'how should we test\'; Trigger on `your` code.'),
        'skills/b/SKILL.md': skill_md("Use when a user's data is stale; it doesn't re-run."),
        'skills/c/SKILL.md': 'No frontmatter.\n',
    })
    files = ['skills/a/SKILL.md', 'skills/b/SKILL.md', 'skills/c/SKILL.md']
    assert cc.check_description_person(tmp_path, files, PERSON_PARAMS) == []


def test_description_person_flags_pronouns_outside_quotes(tmp_path):
    write_tree(tmp_path, {
        'skills/a/SKILL.md': skill_md('Use when you are stuck and your tests fail.'),
        'skills/b/SKILL.md': skill_md('Use when stuck.', when_to_use="We're sure; I think"),
        'skills/c/SKILL.md': skill_md('Use when "you" ask, or you do.'),
    })
    files = ['skills/a/SKILL.md', 'skills/b/SKILL.md', 'skills/c/SKILL.md']
    assert cc.check_description_person(tmp_path, files, PERSON_PARAMS) == [
        cc.Finding('skills/a/SKILL.md', "description uses first- or second-person 'you', 'your' outside quoted phrases"),
        cc.Finding('skills/b/SKILL.md', "description uses first- or second-person 'i', 'we' outside quoted phrases"),
        cc.Finding('skills/c/SKILL.md', "description uses first- or second-person 'you' outside quoted phrases"),
    ]


TRIGGER_PARAMS = {'markers': ['trigger on', 'triggers on', 'trigger when']}


def test_trigger_phrase_presence_passes_quoted_phrases_and_trigger_lists(tmp_path):
    write_tree(tmp_path, {
        'skills/a/SKILL.md': skill_md('Use when asked to "profile this dataset".'),
        'skills/b/SKILL.md': skill_md("Use when asked: 'ingest', 'lint'."),
        'skills/c/SKILL.md': skill_md('Use when tuning. Trigger on: grid search, Optuna.'),
        'skills/d/SKILL.md': skill_md('Use when tuning.', when_to_use='Triggers on cross-validation.'),
    })
    files = [f'skills/{c}/SKILL.md' for c in 'abcd']
    assert cc.check_trigger_phrase_presence(tmp_path, files, TRIGGER_PARAMS) == []


def test_trigger_phrase_presence_flags_a_description_with_neither(tmp_path):
    write_tree(tmp_path, {
        'skills/a/SKILL.md': skill_md('Use when implementing any feature.'),
        'skills/b/SKILL.md': skill_md("Use when a user's request is vague; it won't say."),
    })
    assert cc.check_trigger_phrase_presence(
        tmp_path, ['skills/a/SKILL.md', 'skills/b/SKILL.md'], TRIGGER_PARAMS) == [
        cc.Finding('skills/a/SKILL.md', 'description has neither a quoted trigger phrase nor a "Trigger on" list'),
        cc.Finding('skills/b/SKILL.md', 'description has neither a quoted trigger phrase nor a "Trigger on" list'),
    ]


def test_substitution_hazard_passes_escaped_and_plain_text(tmp_path):
    write_tree(tmp_path, {'skills/a/SKILL.md': skill_md(
        body='Costs \\$1.00 and \\$ARGUMENTS stay literal; so does $HOME or $name here.\n'
             'A bang alone ! and `code` pass.\n', arguments='[issue]')})
    assert cc.check_substitution_hazard(tmp_path, ['skills/a/SKILL.md'], {}) == []


def test_substitution_hazard_flags_each_substitution_and_shell_token(tmp_path):
    body = ('Run for $ARGUMENTS now.\n'
            'First arg $0 and second $1.\n'
            'Dir ${CLAUDE_SKILL_DIR}/x and ${CLAUDE_SESSION_ID}.\n'
            'Declared $issue works.\n'
            'Status: !`git status`\n'
            f'{FENCE}!\ngit log\n{FENCE}\n'
            f'{FENCE}bash\necho $ARGUMENTS\n{FENCE}\n')
    write_tree(tmp_path, {'skills/a/SKILL.md': skill_md(body=body, arguments='[issue]')})
    found = cc.check_substitution_hazard(tmp_path, ['skills/a/SKILL.md'], {})
    assert [f.message for f in found] == [
        "line 6: '$ARGUMENTS' is substituted when the skill loads; escape it as \\$ARGUMENTS",
        "line 7: '$0' is substituted when the skill loads; escape it as \\$0",
        "line 7: '$1' is substituted when the skill loads; escape it as \\$1",
        "line 8: '${CLAUDE_SKILL_DIR}' is substituted when the skill loads; escape it as \\${CLAUDE_SKILL_DIR}",
        "line 8: '${CLAUDE_SESSION_ID}' is substituted when the skill loads; escape it as \\${CLAUDE_SESSION_ID}",
        "line 9: '$issue' is substituted when the skill loads; escape it as \\$issue",
        "line 10: '!`git status`' runs a shell command at render time, before Claude sees the body",
        'line 11: a ```! fence runs a shell command at render time, before Claude sees the body',
        "line 15: '$ARGUMENTS' is substituted when the skill loads; escape it as \\$ARGUMENTS",
    ]


BUNDLE_PARAMS = {'exempt': ['SKILL.md', 'README.md'],
                 'tests': ['test_*', '*_test.py', 'conftest.py', 'tests/*']}


def test_orphan_bundled_file_passes_files_named_by_file_name_or_directory(tmp_path):
    tree = {
        'skills/a/SKILL.md': 'Read `references/x.md`; sources live in `data/`; run scripts/run.sh.\n',
        'skills/a/references/x.md': 'See also z.md for detail.\n',
        'skills/a/references/z.md': 'Detail.\n',
        'skills/a/data/d.csv': '1,2\n',
        'skills/a/scripts/run.sh': 'echo\n',
        'skills/a/scripts/test_run.py': '',
        'skills/a/README.md': 'Readme.\n',
    }
    write_tree(tmp_path, tree)
    assert cc.check_orphan_bundled_file(tmp_path, sorted(tree), BUNDLE_PARAMS) == []


def test_orphan_bundled_file_flags_files_nothing_names(tmp_path):
    tree = {
        'skills/a/SKILL.md': 'Read `references/x.md`.\n',
        'skills/a/references/x.md': 'Self mention of x.md does not count.\n',
        'skills/a/references/y.md': 'Unnamed.\n',
        'skills/a/notes.txt': 'Unnamed.\n',
        'skills/a/scripts/test_a.py': 'mentions notes.txt, but tests name nothing\n',
        'skills/b/SKILL.md': 'Names nothing; y.md belongs to skill a.\n',
        'skills/b/data.bin': '',
    }
    write_tree(tmp_path, tree)
    assert cc.check_orphan_bundled_file(tmp_path, sorted(tree), BUNDLE_PARAMS) == [
        cc.Finding('skills/a/notes.txt', 'no file in the skill names notes.txt, by file name or by its directory'),
        cc.Finding('skills/a/references/y.md', 'no file in the skill names y.md, by file name or by its directory'),
        cc.Finding('skills/b/data.bin', 'no file in the skill names data.bin, by file name or by its directory'),
    ]


def test_orphan_bundled_file_does_not_match_a_longer_file_name(tmp_path):
    tree = {'skills/a/SKILL.md': 'See `references/metadata.md`.\n',
            'skills/a/references/metadata.md': 'Named.\n',
            'skills/a/references/data.md': 'Not named: metadata.md contains data.md only as a suffix.\n'}
    write_tree(tmp_path, tree)
    assert cc.check_orphan_bundled_file(tmp_path, sorted(tree), BUNDLE_PARAMS) == [
        cc.Finding('skills/a/references/data.md', 'no file in the skill names data.md, by file name or by its directory')]


def test_skill_command_name_collision_passes_distinct_names(tmp_path):
    files = ['skills/deploy/SKILL.md', 'commands/ship.md']
    assert cc.check_skill_command_name_collision(tmp_path, files, {}) == []


def test_skill_command_name_collision_flags_a_shared_name(tmp_path):
    files = ['skills/deploy/SKILL.md', 'commands/deploy.md', 'commands/ship.md',
             '.claude/skills/ship/SKILL.md']
    assert cc.check_skill_command_name_collision(tmp_path, files, {}) == [
        cc.Finding('commands/deploy.md', 'command /deploy shares its name with skills/deploy/SKILL.md, '
                                         'and on a name collision the skill wins'),
        cc.Finding('commands/ship.md', 'command /ship shares its name with .claude/skills/ship/SKILL.md, '
                                       'and on a name collision the skill wins'),
    ]


COMMAND_PARAMS = {'fields': ['description', 'argument-hint', 'allowed-tools', 'model',
                             'disable-model-invocation']}


def test_command_frontmatter_keys_pass(tmp_path):
    write_tree(tmp_path, {
        'commands/a.md': '---\ndescription: A.\nargument-hint: x\ndisable-model-invocation: true\n---\nBody.\n',
        'commands/b.md': 'No frontmatter; the filename is the name.\n',
    })
    assert cc.check_command_frontmatter_keys(
        tmp_path, ['commands/a.md', 'commands/b.md'], COMMAND_PARAMS) == []


def test_command_frontmatter_keys_flag_name_paths_and_unknown_keys(tmp_path):
    write_tree(tmp_path, {
        'commands/a.md': '---\nname: a\ndescription: A.\npaths: [x]\ncolour: red\n---\n',
        'commands/b.md': '---\ndescription: [unclosed\n---\n',
    })
    assert cc.check_command_frontmatter_keys(
        tmp_path, ['commands/a.md', 'commands/b.md'], COMMAND_PARAMS) == [
        cc.Finding('commands/a.md', "frontmatter key 'name' is not allowed in a command: the filename is its name"),
        cc.Finding('commands/a.md', "frontmatter key 'paths' is not allowed in a command"),
        cc.Finding('commands/a.md', "frontmatter key 'colour' is not a documented skill field"),
        cc.Finding('commands/b.md', 'frontmatter does not parse as YAML'),
    ]


SHADOW_PARAMS = {'builtins': ['help', 'model', 'compact']}


def test_builtin_name_shadow_passes_other_names(tmp_path):
    write_tree(tmp_path, {'skills/deploy/SKILL.md': skill_md(), 'commands/ship.md': 'Body.\n'})
    files = ['skills/deploy/SKILL.md', 'commands/ship.md']
    assert cc.check_builtin_name_shadow(tmp_path, files, SHADOW_PARAMS) == []


def test_builtin_name_shadow_flags_skill_directories_names_and_command_stems(tmp_path):
    write_tree(tmp_path, {
        'skills/help/SKILL.md': skill_md(),
        'skills/other/SKILL.md': '---\nname: compact\ndescription: D.\n---\n',
        'commands/model.md': 'Body.\n',
    })
    files = ['commands/model.md', 'skills/help/SKILL.md', 'skills/other/SKILL.md']
    assert cc.check_builtin_name_shadow(tmp_path, files, SHADOW_PARAMS) == [
        cc.Finding('commands/model.md', 'command /model takes the name of the built-in /model, '
                                        'and a skill or command with a built-in name replaces it'),
        cc.Finding('skills/help/SKILL.md', 'skill /help takes the name of the built-in /help, '
                                           'and a skill or command with a built-in name replaces it'),
        cc.Finding('skills/other/SKILL.md', 'skill /compact takes the name of the built-in /compact, '
                                            'and a skill or command with a built-in name replaces it'),
    ]


def test_reserved_skill_name_passes_ordinary_skill_directories():
    files = ['skills/a/SKILL.md', 'skills/a/references/synced.md', 'skills/synced.md']
    assert cc.check_reserved_skill_name(None, files, {'reserved': ['synced']}) == []


def test_reserved_skill_name_flags_a_reserved_directory_once():
    files = ['skills/a/SKILL.md', 'skills/synced/x/SKILL.md', 'skills/synced/y.md',
             '.claude/skills/synced/SKILL.md']
    assert cc.check_reserved_skill_name(None, files, {'reserved': ['synced']}) == [
        cc.Finding('.claude/skills/synced', "directory name 'synced' is reserved for claude.ai skills "
                                            'synced into terminal sessions'),
        cc.Finding('skills/synced', "directory name 'synced' is reserved for claude.ai skills "
                                    'synced into terminal sessions'),
    ]


def test_new_skill_checks_run_through_the_register(tmp_path):
    '''Each new check is registered, reads the kinds the register gives it, and
    reports through run(); the fixture repo is otherwise clean.'''
    files = {
        'skills/help/SKILL.md': skill_md('Use when asked "help me".', body='Cost $1.\n'),
        'commands/help.md': '---\nname: help\n---\nBody.\n',
        'skills/synced/SKILL.md': skill_md('Use when asked "sync".'),
        'skills/help/notes.txt': 'Nothing names me.\n',
    }
    root = fixture_repo(tmp_path, files)
    lines = cc.run(root)
    for check in ('substitution-hazard', 'skill-command-name-collision', 'command-frontmatter-keys',
                  'builtin-name-shadow', 'reserved-skill-name', 'orphan-bundled-file'):
        assert any(f': {check} (' in line for line in lines), (check, lines)


# --- Audit section 6 checks: agents and commands (#50, #51, #52, #54) ---


def real_check(check_id, **override):
    '''Run a register check over the real repo, with params from the register
    unless overridden, so a test can show that a parameter does real work.'''
    reg, _ = cc.parse_register(cc.load_register(cc.REPO))
    check = next(c for c in reg.checks if c.id == check_id)
    kinds = cc.kind_files(reg, cc.kept_files(cc.REPO))
    files = sorted({f for kind in check.kinds for f in kinds[kind]})
    return cc.CHECKS[check_id][0](cc.REPO, files, {**check.params, **override})


def agent_text(name, extra=''):
    return f'---\nname: {name}\ndescription: D.\n{extra}---\n'


def test_agent_name_form_passes_lowercase_hyphenated_and_allowed_names(tmp_path):
    write_tree(tmp_path, {
        'agents/a.md': agent_text('code-reviewer'),
        'agents/b.md': agent_text('Explore'),
        'agents/c.md': agent_text('v2-runner'),
    })
    files = ['agents/a.md', 'agents/b.md', 'agents/c.md']
    assert cc.check_agent_name_form(tmp_path, files, {'allow': ['Explore']}) == []


def test_agent_name_form_flags_other_forms_and_a_missing_name(tmp_path):
    write_tree(tmp_path, {
        'agents/a.md': agent_text('Explore'),
        'agents/b.md': agent_text('test_runner'),
        'agents/c.md': agent_text('Two Words'),
        'agents/d.md': '---\ndescription: D.\n---\n',
        'agents/e.md': 'No frontmatter.\n',
    })
    files = [f'agents/{x}.md' for x in 'abcde']
    assert cc.check_agent_name_form(tmp_path, files, {'allow': []}) == [
        cc.Finding('agents/a.md', "name 'Explore' is not a lowercase-hyphenated ID"),
        cc.Finding('agents/b.md', "name 'test_runner' is not a lowercase-hyphenated ID"),
        cc.Finding('agents/c.md', "name 'Two Words' is not a lowercase-hyphenated ID"),
        cc.Finding('agents/d.md', 'frontmatter sets no name'),
    ]


def test_agent_name_form_allow_list_does_real_work_on_the_repo():
    assert real_check('agent-name-form') == []
    assert real_check('agent-name-form', allow=[]) == [
        cc.Finding('agents/explore.md', "name 'Explore' is not a lowercase-hyphenated ID")]


def test_agent_name_unique_passes_distinct_names(tmp_path):
    write_tree(tmp_path, {
        'agents/a.md': agent_text('alpha'),
        '.claude/agents/b.md': agent_text('beta'),
        'agents/c.md': 'No frontmatter.\n',
    })
    files = ['.claude/agents/b.md', 'agents/a.md', 'agents/c.md']
    assert cc.check_agent_name_unique(tmp_path, files, {}) == []


def test_agent_name_unique_flags_a_name_repeated_across_directories(tmp_path):
    write_tree(tmp_path, {
        'agents/a.md': agent_text('alpha'),
        '.claude/agents/a.md': agent_text('alpha'),
        'agents/b.md': agent_text('beta'),
    })
    files = ['.claude/agents/a.md', 'agents/a.md', 'agents/b.md']
    assert cc.check_agent_name_unique(tmp_path, files, {}) == [
        cc.Finding('.claude/agents/a.md', "name 'alpha' is also the name of agents/a.md"),
        cc.Finding('agents/a.md', "name 'alpha' is also the name of .claude/agents/a.md"),
    ]


def test_agent_name_unique_passes_on_the_repo():
    assert real_check('agent-name-unique') == []


MODEL_PARAMS = {'exempt': ['inherit']}


def settings_text(**keys):
    return json.dumps(keys)


def test_agent_model_available_passes(tmp_path):
    write_tree(tmp_path, {
        '.claude/settings.json': settings_text(availableModels=['sonnet', 'opus']),
        'agents/a.md': agent_text('a', 'model: opus\n'),
        'agents/b.md': agent_text('b', 'model: inherit\n'),
        'agents/c.md': agent_text('c', 'model: claude-sonnet-5-5\n'),
        'agents/d.md': agent_text('d'),
    })
    files = ['.claude/settings.json'] + [f'agents/{x}.md' for x in 'abcd']
    assert cc.check_agent_model_available(tmp_path, files, MODEL_PARAMS) == []


def test_agent_model_available_flags_an_alias_outside_the_list(tmp_path):
    write_tree(tmp_path, {
        '.claude/settings.json': settings_text(availableModels=['sonnet', 'opus']),
        'agents/a.md': agent_text('a', 'model: haiku  # cheap\n'),
        'agents/b.md': agent_text('b', 'model: sonnet\n'),
    })
    files = ['.claude/settings.json', 'agents/a.md', 'agents/b.md']
    assert cc.check_agent_model_available(tmp_path, files, MODEL_PARAMS) == [
        cc.Finding('agents/a.md', "model 'haiku' is not in availableModels (sonnet, opus) of .claude/settings.json")]


def test_agent_model_available_without_a_list_restricts_nothing(tmp_path):
    write_tree(tmp_path, {
        '.claude/settings.json': settings_text(model='opus'),
        'agents/a.md': agent_text('a', 'model: haiku\n'),
    })
    assert cc.check_agent_model_available(
        tmp_path, ['.claude/settings.json', 'agents/a.md'], MODEL_PARAMS) == []
    assert cc.check_agent_model_available(tmp_path, ['agents/a.md'], MODEL_PARAMS) == []


def test_agent_model_available_flags_a_broken_settings_file(tmp_path):
    write_tree(tmp_path, {
        '.claude/settings.json': '{"availableModels": ',
        'agents/a.md': agent_text('a', 'model: haiku\n'),
    })
    assert cc.check_agent_model_available(
        tmp_path, ['.claude/settings.json', 'agents/a.md'], MODEL_PARAMS) == [
        cc.Finding('.claude/settings.json', 'file does not parse (Expecting value)', waivable=False)]
    write_tree(tmp_path, {'.claude/settings.json': settings_text(availableModels='opus')})
    assert cc.check_agent_model_available(
        tmp_path, ['.claude/settings.json', 'agents/a.md'], MODEL_PARAMS) == [
        cc.Finding('.claude/settings.json', 'availableModels is not a list of strings')]


def test_agent_model_available_passes_on_the_repo():
    assert real_check('agent-model-available') == []


def command_text(body, **frontmatter):
    head = ''.join(f'{k}: {v}\n' for k, v in frontmatter.items())
    return f'---\ndescription: D.\ndisable-model-invocation: true\n{head}---\n{body}'


def test_command_substitution_tokens_pass_when_declared_or_not_tokens(tmp_path):
    write_tree(tmp_path, {
        'commands/hinted.md': command_text('Fix $ARGUMENTS, then $0.\n', **{'argument-hint': '[n]'}),
        'commands/named.md': command_text('Fix $issue ($ARGUMENTS[0]).\n', arguments='[issue]'),
        'commands/plain.md': command_text(
            'Costs \\$1.00. Name $issue stays text; ${CLAUDE_SKILL_DIR} needs no declaration.\n'),
        'commands/shell.md': command_text('Branch: !`git branch --show-current`\n',
                                          **{'allowed-tools': 'Bash(git branch *)'}),
        'commands/block.md': command_text('```!\ngit status\n```\n',
                                          **{'allowed-tools': '[Read, Bash(git status)]'}),
    })
    files = [f'commands/{n}.md' for n in ('block', 'hinted', 'named', 'plain', 'shell')]
    assert cc.check_command_substitution_tokens(tmp_path, files, {}) == []


def test_command_substitution_tokens_flag_undeclared_arguments_and_shell(tmp_path):
    write_tree(tmp_path, {
        'commands/args.md': command_text('Intro.\nFix $ARGUMENTS and $1; again $ARGUMENTS[2].\nRepeat $1.\n'),
        'commands/inline.md': command_text('Branch: !`git branch`\n', **{'allowed-tools': 'Read'}),
        'commands/block.md': command_text('Run:\n```!\ngit status\n```\n'),
    })
    files = [f'commands/{n}.md' for n in ('args', 'block', 'inline')]
    note = 'frontmatter sets neither argument-hint nor arguments'
    assert cc.check_command_substitution_tokens(tmp_path, files, {}) == [
        cc.Finding('commands/args.md', f'line 6: $ARGUMENTS is substituted, but {note}'),
        cc.Finding('commands/args.md', f'line 6: $1 is substituted, but {note}'),
        cc.Finding('commands/args.md', f'line 6: $ARGUMENTS[2] is substituted, but {note}'),
        cc.Finding('commands/block.md', 'line 6: render-time shell runs, but frontmatter sets no allowed-tools Bash entry'),
        cc.Finding('commands/inline.md', 'line 6: render-time shell runs, but frontmatter sets no allowed-tools Bash entry'),
    ]


def test_command_substitution_tokens_pass_on_the_repo():
    assert real_check('command-substitution-tokens') == []


# --- Audit section 6 checks: hooks, rules and settings (#58 to #64) ---

ALWAYS_ON_PARAMS = {'phrases': ['always-on', 'always on', 'every session', 'every turn',
                                'every edit', 'every python edit']}


def test_rule_always_on_claim_passes(tmp_path):
    root = tmp_path / 'repo'
    write_tree(root, {
        'rules/py.md': RULE.replace('Rule.', '# Python conventions (loaded on .py reads)\n\nThis rule is not always-on.\n'),
        'rules/core.md': 'Always-on guardrails, loaded every session.\n',
        'rules/bare.md': '---\ndescription: D.\n---\n\nStanding rules, always on.\n',
    })
    (root / '.claude/rules').mkdir(parents=True)
    os.symlink('../../rules/py.md', root / '.claude/rules/py.md')
    files = ['.claude/rules/py.md', 'rules/bare.md', 'rules/core.md', 'rules/py.md']
    assert cc.check_rule_always_on_claim(root, files, ALWAYS_ON_PARAMS) == []


def test_rule_always_on_claim_flags_a_path_scoped_rule_that_says_it(tmp_path):
    root = tmp_path / 'repo'
    write_tree(root, {'rules/py.md': RULE.replace(
        'Rule.', '# Python conventions (always-on)\n\nStanding guardrails injected on every Python edit.\n')})
    (root / '.claude/rules').mkdir(parents=True)
    os.symlink('../../rules/py.md', root / '.claude/rules/py.md')
    assert cc.check_rule_always_on_claim(root, ['.claude/rules/py.md', 'rules/py.md'], ALWAYS_ON_PARAMS) == [
        cc.Finding('rules/py.md', "line 6: path-scoped rule says 'always-on', but paths load it lazily"),
        cc.Finding('rules/py.md', "line 8: path-scoped rule says 'every python edit', but paths load it lazily"),
    ]


def test_rule_always_on_claim_passes_on_the_repo():
    assert real_check('rule-always-on-claim') == []


OLD_EXIT_CLAIM = ('- **Exit codes matter:** only exit 2 blocks and feeds stderr to Claude; exit 1 just\n'
                  '  logs. All three follow that convention.\n')
NEW_EXIT_CLAIM = ('- **Exit codes matter:** a hook blocks either by exiting 2 or by printing a JSON\n'
                  '  `permissionDecision: "deny"`; any other non-zero exit, such as 1, just logs.\n')
GUARD_DOC = 'The guard prints `"permissionDecision": "deny"` on PreToolUse.\n'


def test_hook_readme_exit_claims_pass(tmp_path):
    write_tree(tmp_path, {
        'hooks/README.md': NEW_EXIT_CLAIM + GUARD_DOC,
        'hooks/other.md': OLD_EXIT_CLAIM,  # no deny documented, so the claim is true
    })
    assert cc.check_hook_readme_exit_claims(tmp_path, ['hooks/README.md', 'hooks/other.md'], {}) == []


@pytest.mark.parametrize('claim', [
    OLD_EXIT_CLAIM,
    'Blocking: exit 2 is the only way to stop a call.\n',
    'The only way to block a call is exit 2.\n',
])
def test_hook_readme_exit_claims_flag_only_exit_2_beside_a_deny(tmp_path, claim):
    write_tree(tmp_path, {'hooks/README.md': 'Intro.\n\n' + claim + GUARD_DOC})
    line = 3 + claim.count('\n')
    assert cc.check_hook_readme_exit_claims(tmp_path, ['hooks/README.md'], {}) == [
        cc.Finding('hooks/README.md',
                   f'line 3: says only exit 2 blocks, but line {line} documents a permissionDecision deny')]


def test_hook_readme_exit_claims_flag_a_deny_in_a_script_the_readme_names(tmp_path):
    write_tree(tmp_path, {
        'hooks/README.md': OLD_EXIT_CLAIM + '\n## guard.py\n\nPreToolUse hook.\n',
        'hooks/guard.py': "print(json.dumps({'hookSpecificOutput': {'permissionDecision': 'deny'}}))\n",
        'hooks/quiet.py': 'sys.exit(2)\n',
    })
    files = ['hooks/README.md', 'hooks/guard.py', 'hooks/quiet.py']
    assert cc.check_hook_readme_exit_claims(tmp_path, files, {}) == [
        cc.Finding('hooks/README.md', 'line 1: says only exit 2 blocks, but hooks/guard.py, which it '
                                      'documents, blocks with a permissionDecision deny')]
    write_tree(tmp_path, {'hooks/README.md': OLD_EXIT_CLAIM + '\nOnly quiet.py is installed.\n'})
    assert cc.check_hook_readme_exit_claims(tmp_path, files, {}) == []


def test_hook_readme_exit_claims_pass_on_the_repo():
    assert real_check('hook-readme-exit-claims') == []


def tracked_repo(root, files, executable=()):
    '''git-init root, add the files, and pin each .sh or .py file's index mode to
    100755 when listed in executable and to 100644 otherwise, whatever the
    filesystem says.'''
    git_repo(root, files)
    env = cc.git_env()
    subprocess.run(['git', 'add', '-A'], cwd=root, env=env, check=True)
    for name in files:
        if name.endswith(('.sh', '.py')):
            flag = '--chmod=+x' if name in executable else '--chmod=-x'
            subprocess.run(['git', 'update-index', flag, name], cwd=root, env=env, check=True)
    return root


def test_hook_scripts_executable_pass(tmp_path):
    root = tracked_repo(tmp_path, {
        'hooks/guard.py': '#!/usr/bin/env python3\n',
        'hooks/gate.sh': '#!/bin/sh\n',
        'hooks/README.md': json_block(hooks_tree('PreToolUse', '"$CLAUDE_PROJECT_DIR"/.claude/hooks/gate.sh'))
        + json_block(hooks_tree('Stop', 'uv run ruff check .')),
    }, executable={'hooks/guard.py', 'hooks/gate.sh'})
    files = ['hooks/README.md', 'hooks/gate.sh', 'hooks/guard.py']
    assert cc.check_hook_scripts_executable(root, files, {}) == []


def test_hook_scripts_executable_flag_a_plain_mode_and_a_missing_wired_script(tmp_path):
    root = tracked_repo(tmp_path, {
        'hooks/guard.py': '#!/usr/bin/env python3\n',
        'hooks/gate.sh': '#!/bin/sh\n',
        'hooks/README.md': json_block(hooks_tree('PreToolUse', '$CLAUDE_PROJECT_DIR/.claude/hooks/gone.sh')),
    }, executable={'hooks/gate.sh'})
    files = ['hooks/README.md', 'hooks/gate.sh', 'hooks/guard.py']
    assert cc.check_hook_scripts_executable(root, files, {}) == [
        cc.Finding('hooks/guard.py', 'git index mode is 100644, not 100755, so the hook fails open where it is installed'),
        cc.Finding('hooks/README.md', "JSON block at line 1: PreToolUse command "
                                      "'$CLAUDE_PROJECT_DIR/.claude/hooks/gone.sh' names no hook script in the repo"),
    ]


def test_hook_scripts_executable_judge_an_untracked_script_by_its_execute_bit(tmp_path):
    root = tracked_repo(tmp_path, {'hooks/kept.sh': '#!/bin/sh\n'}, executable={'hooks/kept.sh'})
    write_tree(root, {'hooks/new.sh': '#!/bin/sh\n', 'hooks/new-x.sh': '#!/bin/sh\n'})
    (root / 'hooks/new.sh').chmod(0o644)
    (root / 'hooks/new-x.sh').chmod(0o755)
    files = ['hooks/kept.sh', 'hooks/new-x.sh', 'hooks/new.sh']
    assert cc.check_hook_scripts_executable(root, files, {}) == [
        cc.Finding('hooks/new.sh', 'untracked and not executable, so the hook would fail open')]


def test_hook_scripts_executable_pass_on_the_repo():
    assert real_check('hook-scripts-executable') == []


STDLIB_HOOK = '#!/usr/bin/env python3\nfrom __future__ import annotations\nimport json, sys\nimport os.path\n'
PEP_723 = '# /// script\n# dependencies = ["pyyaml"]\n# ///\n'


def test_hook_python_deps_pass(tmp_path):
    write_tree(tmp_path, {
        'hooks/stdlib.py': STDLIB_HOOK + 'from . import sibling\nimport helper\n',
        'hooks/helper.py': 'import re\n',
        'hooks/pep723.py': '#!/usr/bin/env -S uv run --script\n' + PEP_723 + 'import yaml\n',
    })
    files = ['hooks/helper.py', 'hooks/pep723.py', 'hooks/stdlib.py']
    assert cc.check_hook_python_deps(tmp_path, files, {}) == []


def test_hook_python_deps_flag_third_party_imports_without_a_block(tmp_path):
    write_tree(tmp_path, {
        'hooks/a.py': 'import json\nimport yaml\n\n\ndef f():\n    from requests.auth import HTTPBasicAuth\n',
        'hooks/b.py': '# /// not-a-script\n# x = 1\n# ///\nimport numpy\n',
        'hooks/broken.py': 'def (:\n',
    })
    assert cc.check_hook_python_deps(tmp_path, ['hooks/a.py', 'hooks/b.py', 'hooks/broken.py'], {}) == [
        cc.Finding('hooks/a.py', 'imports requests, yaml, outside the standard library, and declares no PEP 723 script block'),
        cc.Finding('hooks/b.py', 'imports numpy, outside the standard library, and declares no PEP 723 script block'),
        cc.Finding('hooks/broken.py', 'cannot parse: invalid syntax (line 1)', waivable=False),
    ]


def test_hook_python_deps_pass_on_the_repo():
    assert real_check('hook-python-deps') == []


@pytest.mark.parametrize('pattern, ops', [
    ('uv run:*', []),
    ('git status && rm -rf x', ['&&']),
    ('a || b', ['||']),
    ('a; b', [';']),
    ('a | b', ['|']),
    ('a |& b', ['|&']),
    ('a & b', ['&']),
    ('echo "a && b; c"', []),
    ("echo 'a | b'", []),
    ('echo a\\;b', []),
    ('make 2>&1', []),
    ('make &> out', []),
    ('a && b | c', ['&&', '|']),
])
def test_unquoted_operators_track_shell_quoting(pattern, ops):
    assert cc.unquoted_operators(pattern) == ops


def test_allow_rule_compound_operators_pass(tmp_path):
    write_tree(tmp_path, {
        '.claude/settings.json': json.dumps({'permissions': {
            'allow': ['Bash(uv run:*)', 'Bash(echo "a && b")', 'Read(./a;b)'],
            'deny': ['Bash(rm -rf / && echo)']}}),
        'hooks/README.md': json_block({'permissions': {'allow': ['Bash(uv add:*)']}}),
    })
    assert cc.check_allow_rule_compound_operators(
        tmp_path, ['.claude/settings.json', 'hooks/README.md'], {}) == []


def test_allow_rule_compound_operators_flag_unquoted_separators(tmp_path):
    write_tree(tmp_path, {
        '.claude/settings.json': json.dumps({'permissions': {'allow': ['Bash(cd x && git status)']}}),
        'hooks/README.md': 'Add:\n\n' + json_block({'permissions': {'allow': ['Bash(a | b; c)', 'Bash(ok)']}}),
    })
    note = 'which Claude Code splits compound commands on, so it never matches'
    assert cc.check_allow_rule_compound_operators(
        tmp_path, ['.claude/settings.json', 'hooks/README.md'], {}) == [
        cc.Finding('.claude/settings.json', f'allow rule Bash(cd x && git status) holds an unquoted &&, {note}'),
        cc.Finding('hooks/README.md', f'JSON block at line 3: allow rule Bash(a | b; c) holds an unquoted ;, |, {note}'),
    ]


def test_allow_rule_compound_operators_never_read_the_local_settings_file(tmp_path):
    '''settings.local.json is gitignored, so kept_files never lists it and no
    kind globs it: a developer's private rules cannot change the lint's result.'''
    root = git_repo(tmp_path, {
        '.gitignore': '**/.claude/settings.local.json\n',
        '.claude/settings.json': '{}',
        '.claude/settings.local.json': json.dumps({'permissions': {'allow': ['Bash(a && b)']}}),
    })
    assert '.claude/settings.local.json' not in cc.kept_files(root)
    reg, _ = cc.parse_register(cc.load_register(cc.REPO))
    assert not any(cc.PurePosixPath('.claude/settings.local.json').full_match(g)
                   for kind in reg.kinds.values() for g in kind.globs)


def test_allow_rule_compound_operators_pass_on_the_repo():
    assert real_check('allow-rule-compound-operators') == []


RUNNER_PARAMS = {'runners': ['uv run', 'npx', 'npm run']}
ALLOW_UV = json_block({'permissions': {'allow': ['Bash(uv run:*)', 'Bash(uv add:*)']}})


def test_inert_runner_allow_rules_pass(tmp_path):
    write_tree(tmp_path, {
        'hooks/README.md': (
            "Pair with an allowlist so the uv forms don't prompt. This holds in manual\n"
            'permission mode only; auto mode sets broad runner rules aside:\n\n' + ALLOW_UV
            + '\nAllow just the one build:\n\n'
            + json_block({'permissions': {'allow': ['Bash(npm run build)']}})
            + "\nSpare prompts for git:\n\n"
            + json_block({'permissions': {'allow': ['Bash(git status:*)']}})
            + '\nPair with an allowlist:\n\n' + ALLOW_UV),
    })
    assert cc.check_inert_runner_allow_rules(tmp_path, ['hooks/README.md'], RUNNER_PARAMS) == []


def test_inert_runner_allow_rules_flag_a_runner_rule_said_to_spare_prompts(tmp_path):
    write_tree(tmp_path, {
        'hooks/README.md': ("Optionally pair with a permission allowlist so the `uv` forms don't\n"
                            'prompt:\n\n' + ALLOW_UV
                            + '\nSkip prompts for npx:\n\n' + json_block({'permissions': {'allow': ['Bash(npx *)']}})),
    })
    note = 'is said to spare prompts, but auto mode sets broad runner rules aside and the text names no mode'
    assert cc.check_inert_runner_allow_rules(tmp_path, ['hooks/README.md'], RUNNER_PARAMS) == [
        cc.Finding('hooks/README.md', f'JSON block at line 4: Bash(uv run:*) {note}'),
        cc.Finding('hooks/README.md', f'JSON block at line 17: Bash(npx *) {note}'),
    ]


def test_inert_runner_allow_rules_pass_on_the_repo():
    assert real_check('inert-runner-allow-rules') == []


BLOCKING = {'blocking_events': ['PreToolUse', 'Stop', 'UserPromptSubmit']}
WIRE = json_block(hooks_tree('PreToolUse', '"$CLAUDE_PROJECT_DIR"/.claude/hooks/a.sh'))


def test_hook_install_verify_step_pass(tmp_path):
    write_tree(tmp_path, {
        'hooks/README.md': (
            '## Install\n\n' + WIRE + '\nThen trigger each blocking hook once to confirm it\nis wired.\n\n'
            '## Other\n\n' + json_block(hooks_tree('PostToolUse', 'fmt.sh')) + '\nNo step needed.\n\n'
            '## Guard\n\n' + WIRE + '\n```bash\n# a comment, not a heading\n```\n'
            'Run the probe: trigger it once.\n'),
    })
    assert cc.check_hook_install_verify_step(tmp_path, ['hooks/README.md'], BLOCKING) == []


def test_hook_install_verify_step_flag_a_blocking_block_with_no_step(tmp_path):
    write_tree(tmp_path, {
        'hooks/README.md': (
            '## Install\n\n' + WIRE + '\nDone.\n\n## Later\n\nTrigger it once.\n\n'
            + json_block({'hooks': {'Stop': [], 'PreToolUse': [{'hooks': []}]}})
            + '\nPrefer cp.\n'),
    })
    assert cc.check_hook_install_verify_step(tmp_path, ['hooks/README.md'], BLOCKING) == [
        cc.Finding('hooks/README.md', 'JSON block at line 3: wires PreToolUse, but no step telling '
                                      'the reader to trigger the hook once follows before the next heading'),
        cc.Finding('hooks/README.md', 'JSON block at line 26: wires PreToolUse, Stop, but no step telling '
                                      'the reader to trigger the hook once follows before the next heading'),
    ]


def test_hook_install_verify_step_pass_on_the_repo():
    assert real_check('hook-install-verify-step') == []


# --- Audit section 6 checks: CLAUDE.md files (#67, #68, #69) ---

IMPORT_PARAMS = {'max_hops': 4}


def test_import_targets_skip_fences_code_spans_and_emails():
    text = ('See @docs/a.md, and (@docs/b.md).\n'
            'Mention `@docs/c.md` without importing it, or ``@d`` too.\n'
            'Mail me@example.com or write @ alone.\n'
            f'{FENCE}bash\n# @needs_pilot tests read a wiki\n{FENCE}\n'
            '@docs/e.md.\n')
    assert cc.import_targets(text) == [(1, 'docs/a.md'), (1, 'docs/b.md'), (7, 'docs/e.md')]


def test_claude_md_import_resolves_pass(tmp_path):
    write_tree(tmp_path, {
        'CLAUDE.md': f'Read @docs/a.md.\n\n{FENCE}bash\n# @needs_pilot tests\n{FENCE}\nNot an import: `@x`.\n'
                     'Home: @~/notes.md and @/etc/hosts are not followed.\n',
        'docs/a.md': 'See @b.md\n',
        'docs/b.md': 'Back to @a.md\n',
    })
    assert cc.check_claude_md_import_resolves(tmp_path, ['CLAUDE.md'], IMPORT_PARAMS) == []


def test_claude_md_import_resolves_flags_a_missing_file_in_the_chain(tmp_path):
    write_tree(tmp_path, {
        'CLAUDE.md': 'Intro.\n@gone.md\n@docs/a.md\n',
        'docs/a.md': 'Line.\n@missing.md\n',
        'build/CLAUDE.md': '@../docs/a.md\n',
    })
    assert cc.check_claude_md_import_resolves(
        tmp_path, ['CLAUDE.md', 'build/CLAUDE.md'], IMPORT_PARAMS) == [
        cc.Finding('CLAUDE.md', 'CLAUDE.md line 2: import @gone.md does not resolve'),
        cc.Finding('CLAUDE.md', 'docs/a.md line 2: import @missing.md does not resolve'),
        cc.Finding('build/CLAUDE.md', 'docs/a.md line 2: import @missing.md does not resolve'),
    ]


def test_claude_md_import_resolves_stops_at_the_hop_limit(tmp_path):
    write_tree(tmp_path, {
        'CLAUDE.md': '@h1.md\n',
        'h1.md': '@h2.md\n', 'h2.md': '@h3.md\n', 'h3.md': '@h4.md\n', 'h4.md': '@h5.md\n',
        'h5.md': 'Leaf.\n',
    })
    assert cc.check_claude_md_import_resolves(tmp_path, ['CLAUDE.md'], IMPORT_PARAMS) == [
        cc.Finding('CLAUDE.md', 'h4.md line 1: import @h5.md is hop 5, past the 4-hop limit')]
    assert cc.check_claude_md_import_resolves(tmp_path, ['CLAUDE.md'], {'max_hops': 5}) == []


def test_claude_md_import_resolves_passes_on_the_repo():
    text = (cc.REPO / 'CLAUDE.md').read_text()
    assert '@needs_pilot' in text  # a naive scan would flag this, so the test means something
    assert real_check('claude-md-import-resolves') == []


def ignored_repo(tmp_path, ignore):
    return git_repo(tmp_path, {'CLAUDE.md': 'x\n', 'build/CLAUDE.md': 'y\n', '.gitignore': ignore})


def test_local_md_ignored_pass(tmp_path):
    root = ignored_repo(tmp_path, 'CLAUDE.local.md\n')
    assert cc.check_local_md_ignored(root, ['CLAUDE.md', 'build/CLAUDE.md'], {}) == []


def test_local_md_ignored_flags_each_directory_that_does_not_ignore_it(tmp_path):
    root = ignored_repo(tmp_path, '/CLAUDE.local.md\n')
    assert cc.check_local_md_ignored(root, ['CLAUDE.md', 'build/CLAUDE.md'], {}) == [
        cc.Finding('build/CLAUDE.md', 'build/CLAUDE.local.md is not gitignored, so a personal file would be committed')]


def test_local_md_ignored_does_not_count_private_ignore_sources(tmp_path):
    root = ignored_repo(tmp_path, '*.pyc\n')
    (root / '.git/info/exclude').write_text('CLAUDE.local.md\n')
    elsewhere = tmp_path.parent / f'{tmp_path.name}-global-ignore'
    elsewhere.write_text('CLAUDE.local.md\n')
    subprocess.run(['git', 'config', 'core.excludesFile', str(elsewhere)],
                   cwd=root, env=cc.git_env(), check=True)
    assert cc.check_local_md_ignored(root, ['CLAUDE.md'], {}) == [
        cc.Finding('CLAUDE.md', 'CLAUDE.local.md is ignored only by .git/info/exclude, which is not committed')]
    (root / '.git/info/exclude').write_text('')
    assert cc.check_local_md_ignored(root, ['CLAUDE.md'], {}) == [
        cc.Finding('CLAUDE.md', 'CLAUDE.local.md is not gitignored, so a personal file would be committed')]


def test_local_md_ignored_outside_a_repo_is_a_setup_error(tmp_path):
    write_tree(tmp_path, {'CLAUDE.md': 'x\n'})
    with pytest.raises(cc.SetupError, match='git check-ignore failed'):
        cc.check_local_md_ignored(tmp_path, ['CLAUDE.md'], {})


def test_local_md_ignored_passes_on_the_repo():
    assert real_check('local-md-ignored') == []
    shown = subprocess.run(['git', 'check-ignore', '-v', 'CLAUDE.local.md'], cwd=cc.REPO,
                           env=cc.git_env(), capture_output=True, text=True, check=True).stdout
    assert shown.startswith('.gitignore:')


COUNT_PARAMS = {'nouns': ['test', 'tests', 'test functions', 'passed', 'skipped', 'originals'],
                'allow': ['originals, kept in sync']}


def test_claude_md_count_claims_pass(tmp_path):
    write_tree(tmp_path, {'CLAUDE.md': (
        'Run the tests with pytest; its summary line gives the counts.\n'
        'Python 3.13 and 2 spaces.\n'
        '(19 originals, kept in sync with NOTICE)\n')})
    assert cc.check_claude_md_count_claims(tmp_path, ['CLAUDE.md'], COUNT_PARAMS) == []


def test_claude_md_count_claims_flag_counts_even_inside_fences(tmp_path):
    write_tree(tmp_path, {'CLAUDE.md': (
        'Intro.\n'
        f'{FENCE}bash\n'
        '# Full build-directory tests: 182 tests\n'
        '# (58 passed, 3 skipped) with the stack\n'
        f'{FENCE}\n'
        'The 1,204 test functions all pass.\n'
        'Skip 4 originals now.\n')})
    assert cc.check_claude_md_count_claims(tmp_path, ['CLAUDE.md'], COUNT_PARAMS) == [
        cc.Finding('CLAUDE.md', "line 3: states a count ('182 tests') that goes stale"),
        cc.Finding('CLAUDE.md', "line 4: states a count ('58 passed') that goes stale"),
        cc.Finding('CLAUDE.md', "line 6: states a count ('1,204 test functions') that goes stale"),
        cc.Finding('CLAUDE.md', "line 7: states a count ('4 originals') that goes stale"),
    ]


def test_claude_md_count_claims_allow_list_does_real_work_on_the_repo():
    assert real_check('claude-md-count-claims') == []
    assert any('originals' in f.message for f in real_check('claude-md-count-claims', allow=[]))


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
    assert 'claude-md-size' not in [c.id for c in reg.checks]
    assert len(reg.checks) == len(tomllib.loads(FIXTURE_REGISTER)['check']) - 1


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
    # The fixture README also trips two hook checks this test is not about.
    unrelated = (': hook-install-verify-step (', ': hook-scripts-executable (')
    assert [line for line in cc.run(root) if not any(u in line for u in unrelated)] == [
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


# ---- #37: a waiver path must be one of its check's files --------------------


def not_covered(path, check='bash-search-tools', kinds='agent'):
    return field_error(f'artifact {path} is not one of the files check {check} covers (kind: {kinds})')


@pytest.mark.parametrize('artifact, message', [
    ('./agents/a.md', lambda root: not_covered('./agents/a.md')),
    (None, lambda root: not_covered(str(root / 'agents/a.md'))),  # absolute
    ('agents', lambda root: not_covered('agents')),
    ('agents/ignored.md', lambda root: not_covered('agents/ignored.md')),
    ('CLAUDE.md', lambda root: not_covered('CLAUDE.md')),
    ('agents/../agents/a.md', lambda root: not_covered('agents/../agents/a.md')),
])
def test_waiver_path_must_be_one_of_its_checks_files(tmp_path, artifact, message):
    artifact = artifact or str(tmp_path / 'agents/a.md')
    root = fixture_repo(tmp_path, {
        'agents/a.md': GREP_BESIDE_BASH, 'agents/ignored.md': GREP_BESIDE_BASH,
        'CLAUDE.md': 'Short.\n', '.gitignore': 'agents/ignored.md\n'},
        register=FIXTURE_REGISTER + exception_toml({**GAP, 'artifacts': [artifact]}))
    assert cc.run(root) == [UNWAIVED, message(root)]


def test_waiver_path_that_is_a_check_file_passes(tmp_path):
    '''A multi-kind check accepts a path from either kind.'''
    hook_gap = {**GAP, 'id': 'hook-dir', 'check': 'hook-dir-quoted', 'sections': ['a.one'],
                'artifacts': ['hooks/README.md', '.claude/settings.json'], 'protects': None}
    root = fixture_repo(tmp_path, {
        'hooks/README.md': json_block(hooks_tree('PreToolUse', '$CLAUDE_PROJECT_DIR/a.sh')),
        '.claude/settings.json': json.dumps(hooks_tree('PreToolUse', '$CLAUDE_PROJECT_DIR/a.sh'))},
        register=FIXTURE_REGISTER + exception_toml(hook_gap))
    # The fixture names a hook script it does not ship, which this test is not about.
    unrelated = (': hook-install-verify-step (', ': hook-scripts-executable (')
    assert [line for line in cc.run(root) if not any(u in line for u in unrelated)] == []


def test_waiver_path_of_the_wrong_kind_for_a_multi_kind_check_fails(tmp_path):
    hook_gap = {**GAP, 'id': 'hook-dir', 'check': 'hook-dir-quoted', 'sections': ['a.one'],
                'artifacts': ['agents/a.md'], 'protects': None}
    root = fixture_repo(tmp_path, {'agents/a.md': GREP_BESIDE_BASH},
                        register=FIXTURE_REGISTER + exception_toml(hook_gap))
    assert cc.run(root) == [
        UNWAIVED,
        f'{cc.REGISTER}: exception (-): exception hook-dir: artifact agents/a.md is not one of '
        'the files check hook-dir-quoted covers (kind: hook, settings)']


# ---- #82: nested rules and symlinked rule directories -----------------------

RULE_ENTRIES = ['.claude/rules/top.md', '.claude/rules/sub/nested.md', '.claude/rules/sub/deep/n.md',
                '.claude/rules/dirlink', '.claude/rules/sub/dirlink', '.claude/rules/notes.txt',
                'rules/py.md', 'rules/sub/x.md', '.claude/rulesx/y.md', '.claude/other/z.md']


def test_real_rule_kind_covers_nested_rules_and_symlinked_directories():
    reg, _ = cc.parse_register(cc.load_register(cc.REPO))
    assert cc.kind_files(reg, sorted(RULE_ENTRIES))['rule'] == sorted([
        '.claude/rules/top.md', '.claude/rules/sub/nested.md', '.claude/rules/sub/deep/n.md',
        '.claude/rules/dirlink', '.claude/rules/sub/dirlink', '.claude/rules/notes.txt', 'rules/py.md'])


def rules_repo(tmp_path):
    '''A repo with nested rules, a directory link inside the repo, one outside
    it, a dangling one, and a stray non-Markdown file.'''
    root = tmp_path / 'repo'
    write_tree(root, {
        'rules/shared/a.md': RULE,
        '.claude/rules/top.md': RULE,
        '.claude/rules/sub/bare.md': 'No frontmatter.\n',
        '.claude/rules/notes.txt': 'Not a rule, and no paths.\n'})
    write_tree(tmp_path, {'elsewhere/out.md': RULE})
    os.symlink('../../rules/shared', root / '.claude/rules/inside')
    os.symlink('../../../elsewhere', root / '.claude/rules/outside')
    os.symlink('../../../../elsewhere', root / '.claude/rules/sub/outside-nested')
    os.symlink('../../rules/missing', root / '.claude/rules/dangling')
    os.symlink('../../../elsewhere/out.md', root / '.claude/rules/link.txt')
    return root


def test_rule_paths_covers_nested_rules_and_directory_links(tmp_path):
    root = rules_repo(tmp_path)
    files = ['.claude/rules/dangling', '.claude/rules/inside', '.claude/rules/notes.txt',
             '.claude/rules/outside', '.claude/rules/sub/bare.md',
             '.claude/rules/sub/outside-nested', '.claude/rules/top.md']
    outside = 'link resolves outside the repo, so Claude Code treats it as an external import'
    assert cc.check_rule_paths(root, files, {'always_on': []}) == [
        cc.Finding('.claude/rules/dangling', 'link target does not exist', waivable=False),
        cc.Finding('.claude/rules/outside', outside),
        cc.Finding('.claude/rules/sub/outside-nested', outside),
        cc.Finding('.claude/rules/sub/bare.md',
                   'frontmatter sets no non-empty paths list, so the rule loads in every session'),
    ]


def test_a_symlinked_directory_inside_the_repo_is_not_read_as_a_rule(tmp_path):
    root = rules_repo(tmp_path)
    assert cc.check_rule_paths(root, ['.claude/rules/inside'], {'always_on': []}) == []


def test_a_non_markdown_file_is_not_a_rule(tmp_path):
    root = rules_repo(tmp_path)
    '''Neither a regular file nor a link to a file outside the repo, since
    Claude Code discovers only .md files.'''
    files = ['.claude/rules/link.txt', '.claude/rules/notes.txt']
    assert cc.check_rule_paths(root, files, {'always_on': []}) == []


# ---- #38: a check's and an exception's sections fit their kinds -------------


def fit_line(sid, who, kinds, what='kinds'):
    return (f'{cc.REGISTER}: section-fit ({sid}): {who} cites a section that none of its '
            f'{what} governs (kinds: {kinds})')


def test_check_sections_must_be_governed_by_its_kinds():
    raw = tomllib.loads(FIXTURE_REGISTER)
    raw['check'][0]['sections'] = ['a.one', 'a.overview']  # claude-md governs a.one only
    reg, _ = cc.parse_register(raw)
    assert rendered(cc.section_violations(reg, FIXTURE_ANCHORS)) == [
        fit_line('a.overview', 'check claude-md-size', 'claude-md')]


def test_a_multi_kind_check_needs_only_one_kind_to_govern_each_section():
    raw = tomllib.loads(FIXTURE_REGISTER)
    raw['kinds']['settings']['sections'] = ['a.one', 'a.overview']
    raw['check'][2]['sections'] = ['a.overview']  # hook-dir-quoted: hook and settings
    reg, _ = cc.parse_register(raw)
    assert cc.section_violations(reg, FIXTURE_ANCHORS) == []
    raw['kinds']['settings']['sections'] = ['a.one']
    reg, _ = cc.parse_register(raw)
    assert rendered(cc.section_violations(reg, FIXTURE_ANCHORS)) == [
        fit_line('a.overview', 'check hook-dir-quoted', 'hook, settings')]


def test_a_check_section_with_no_anchor_is_not_also_a_fit_violation():
    raw = tomllib.loads(FIXTURE_REGISTER)
    raw['check'][0]['sections'] = ['a.typo']
    reg, _ = cc.parse_register(raw)
    assert [v.check for v in cc.section_violations(reg, FIXTURE_ANCHORS)] == ['section-id']


def test_exception_sections_must_be_governed_by_its_artifacts_kinds(tmp_path):
    '''b.overview is a real anchor, but no kind governs it.'''
    root = fixture_repo(tmp_path, {'agents/a.md': GREP_BESIDE_BASH},
                        register=FIXTURE_REGISTER + exception_toml({**GAP, 'sections': ['a.overview', 'b.overview']}))
    assert cc.run(root) == [fit_line('b.overview', 'exception grep-beside-bash', 'agent', 'artifacts\' kinds')]


def test_exception_sections_may_come_from_any_of_its_artifacts_kinds(tmp_path):
    '''The union over the artifacts: a.overview from the agent, a.one from CLAUDE.md.'''
    mixed = {**GAP, 'id': 'mixed', 'type': 'deviation', 'check': None, 'tracked_in': None,
             'revisit': 'later', 'sections': ['a.overview', 'a.one'],
             'artifacts': ['agents/a.md', 'CLAUDE.md']}
    root = fixture_repo(tmp_path, {'agents/a.md': GREP_BESIDE_BASH, 'CLAUDE.md': 'Short.\n'},
                        register=FIXTURE_REGISTER + exception_toml(GAP) + exception_toml(mixed))
    assert cc.run(root) == []


def test_exception_artifacts_in_no_kind_govern_no_section(tmp_path):
    stray = {**GAP, 'id': 'stray', 'type': 'deviation', 'check': None, 'tracked_in': None,
             'revisit': 'later', 'artifacts': ['docs/*.md']}
    root = fixture_repo(tmp_path, {'docs/x.md': 'Doc.\n'}, register=FIXTURE_REGISTER + exception_toml(stray))
    assert cc.run(root) == [fit_line('a.overview', 'exception stray', 'none', 'artifacts\' kinds')]


def test_a_misfit_exception_still_waives_its_check(tmp_path):
    '''The fit rule reports; it does not disable the waiver.'''
    root = fixture_repo(tmp_path, {'agents/a.md': GREP_BESIDE_BASH},
                        register=FIXTURE_REGISTER + exception_toml({**GAP, 'sections': ['b.overview']}))
    assert cc.run(root) == [fit_line('b.overview', 'exception grep-beside-bash', 'agent', 'artifacts\' kinds')]


# ---- #56: hook-var-quoted ----------------------------------------------------


@pytest.mark.parametrize('command, uses', [
    ('"$HOME"/.claude/hooks/a.sh', []),
    ('"${HOME}/.claude/hooks/a.sh"', []),
    ('$HOME/.claude/hooks/a.sh', [('HOME', 'unquoted')]),
    ('${HOME}/.claude/hooks/a.sh', [('HOME', 'unquoted')]),
    ('${HOME:-/x}/a.sh', [('HOME', 'unquoted')]),
    ('"$HOME"/a.sh $OTHER/b.sh', [('OTHER', 'unquoted')]),
    ('$A/a.sh $B/b.sh', [('A', 'unquoted'), ('B', 'unquoted')]),
    ("'$HOME'/a.sh", [('HOME', 'single-quoted')]),
    ("'$HOME/a.sh'", [('HOME', 'single-quoted')]),
    ('uv run --project=$REPO/tools "$REPO"/a.py', [('REPO', 'unquoted')]),
    ('python3 --dir=$HOME/x a.py', [('HOME', 'unquoted')]),
    ('uv run "$(dirname "$HOME")/a.py"', []),
    ('$(cat "$HOME/x")/a.sh', []),
    # not the start of a path, or not a path at all
    ('echo $HOME', []),
    ('echo $HOME done', []),
    ('a/$HOME/b.sh', []),
    ('x$HOME/b.sh', []),
    ('\\$HOME/a.sh', []),
    ('$1/a.sh', []),
    # CLAUDE_PROJECT_DIR belongs to hook-dir-quoted
    ('$CLAUDE_PROJECT_DIR/a.sh', []),
    ('${CLAUDE_PROJECT_DIR}/a.sh $HOME/b.sh', [('HOME', 'unquoted')]),
])
def test_unquoted_path_vars(command, uses):
    assert cc.unquoted_path_vars(command) == uses


def test_hook_var_quoted_passes(tmp_path):
    write_tree(tmp_path, {
        'hooks/README.md': json_block(hooks_tree('PreToolUse', '"$HOME"/.claude/hooks/a.sh')),
        '.claude/settings.json': json.dumps(hooks_tree('Stop', '"${HOME}/b.sh" --flag $VAR')),
    })
    assert cc.check_hook_var_quoted(tmp_path, ['.claude/settings.json', 'hooks/README.md'], {}) == []


def test_hook_var_quoted_flags_unquoted_and_single_quoted_uses(tmp_path):
    write_tree(tmp_path, {
        'hooks/README.md': 'Wiring:\n\n' + json_block({'hooks': {
            'PreToolUse': [{'matcher': 'Bash', 'hooks': [
                {'type': 'command', 'command': '$HOME/.claude/hooks/a.sh'}]}],
            'Stop': [{'hooks': [
                {'type': 'command', 'command': "'$HOME'/.claude/hooks/b.sh"}]}],
        }}),
        '.claude/settings.json': json.dumps(hooks_tree('PostToolUse', '${TOOLS_DIR}/c.sh')),
    })
    assert cc.check_hook_var_quoted(tmp_path, ['.claude/settings.json', 'hooks/README.md'], {}) == [
        cc.Finding('.claude/settings.json', 'PostToolUse command leaves $TOOLS_DIR unquoted at the start of a path'),
        cc.Finding('hooks/README.md', 'JSON block at line 3: PreToolUse command leaves $HOME unquoted at the start of a path'),
        cc.Finding('hooks/README.md', 'JSON block at line 3: Stop command leaves $HOME single-quoted at the start of a path'),
    ]


def test_hook_var_quoted_leaves_parse_failures_to_hook_dir_quoted(tmp_path):
    write_tree(tmp_path, {'hooks/README.md': BROKEN_BLOCK})
    assert cc.check_hook_var_quoted(tmp_path, ['hooks/README.md'], {}) == []


def test_an_unquoted_project_dir_is_reported_by_hook_dir_quoted_alone(tmp_path):
    root = fixture_repo(tmp_path, {'hooks/README.md': json_block(
        hooks_tree('PreToolUse', '$CLAUDE_PROJECT_DIR/a.sh'))})
    assert cc.run(root) == [
        'hooks/README.md: hook-dir-quoted (a.one): JSON block at line 1: '
        'PreToolUse command leaves $CLAUDE_PROJECT_DIR unquoted']


def test_hook_var_quoted_runs_through_the_register(tmp_path):
    root = fixture_repo(tmp_path, {'hooks/README.md': json_block(
        hooks_tree('PreToolUse', '$HOME/.claude/hooks/a.sh'))})
    assert cc.run(root) == [
        'hooks/README.md: hook-var-quoted (a.one): JSON block at line 1: '
        'PreToolUse command leaves $HOME unquoted at the start of a path']


def test_hook_var_quoted_can_be_waived(tmp_path):
    waiver = {**GAP, 'id': 'home-unquoted', 'check': 'hook-var-quoted', 'sections': ['a.one'],
              'artifacts': ['hooks/README.md'], 'protects': None}
    root = fixture_repo(tmp_path, {'hooks/README.md': json_block(
        hooks_tree('PreToolUse', '$HOME/.claude/hooks/a.sh'))},
        register=FIXTURE_REGISTER + exception_toml(waiver))
    assert cc.run(root) == []


def test_a_broken_kind_adds_no_fit_noise_and_crashes_nothing(tmp_path):
    '''A check may name a kind whose table is unusable (no globs): parse_register
    keeps the check but drops the kind. The register problem and its section-map
    consequence are the reports; the section-fit rule skips the check and the
    exception, and the waiver path rule does not call the agent path uncovered.'''
    register = FIXTURE_REGISTER.replace("globs = ['agents/*.md']\n", '') + exception_toml(GAP)
    root = fixture_repo(tmp_path, {'agents/a.md': GREP_BESIDE_BASH}, register=register)
    assert cc.run(root) == [
        f'{cc.REGISTER}: register (-): kinds.agent: globs must be a non-empty list of strings',
        f'{cc.REGISTER}: section-map (a.overview): section is neither mapped to a kind nor listed in [unmapped]']
