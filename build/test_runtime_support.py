import importlib.util
import os
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parent.parent
SYNC = REPO / 'build' / 'sync_runtime_assets.py'
INSTALL = REPO / 'install.py'


def load_sync_module():
  spec = importlib.util.spec_from_file_location('sync_runtime_assets', SYNC)
  assert spec is not None and spec.loader is not None
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module


def test_committed_runtime_assets_are_current():
  result = subprocess.run(
    [sys.executable, str(SYNC), '--check'],
    cwd=REPO,
    capture_output=True,
    text=True,
  )
  assert result.returncode == 0, result.stdout + result.stderr


def test_codex_agent_adapter_is_valid_and_read_only():
  data = tomllib.loads((REPO / 'runtimes/codex/agents/code-reviewer.toml').read_text())
  assert data['name'] == 'code-reviewer'
  assert data['sandbox_mode'] == 'read-only'
  assert 'Ready to merge?' in data['developer_instructions']
  assert 'model' not in data


def test_gemini_agent_adapter_maps_tools_and_inherits_model():
  sync = load_sync_module()
  frontmatter, body = sync.read_frontmatter(
    REPO / 'runtimes/gemini/agents/debugger.md'
  )
  assert frontmatter['name'] == 'debugger'
  assert frontmatter['kind'] == 'local'
  assert frontmatter['tools'] == [
    'read_file', 'replace', 'run_shell_command', 'grep_search', 'glob'
  ]
  assert 'model' not in frontmatter
  assert 'Reproduce first' in body


def test_gemini_command_adapter_passes_arguments():
  data = tomllib.loads((REPO / 'runtimes/gemini/commands/fix-issue.toml').read_text())
  assert data['description'].startswith('Fix a GitHub issue')
  assert '{{args}}' in data['prompt']
  assert 'gh issue view' in data['prompt']


def test_every_codex_adapter_parses_with_required_fields():
  for path in sorted((REPO / 'runtimes/codex/agents').glob('*.toml')):
    data = tomllib.loads(path.read_text())
    assert data['name']
    assert data['description']
    assert data['developer_instructions']


def test_every_gemini_adapter_parses_without_claude_model_names():
  sync = load_sync_module()
  for path in sorted((REPO / 'runtimes/gemini/agents').glob('*.md')):
    frontmatter, body = sync.read_frontmatter(path)
    assert frontmatter['name']
    assert frontmatter['description']
    assert frontmatter['kind'] == 'local'
    assert 'model' not in frontmatter
    assert body
  for path in sorted((REPO / 'runtimes/gemini/commands').glob('*.toml')):
    data = tomllib.loads(path.read_text())
    assert data['description']
    assert '{{args}}' in data['prompt']


def test_runtime_instruction_entrypoints_exist():
  assert 'CLAUDE.md' in (REPO / 'AGENTS.md').read_text()
  assert '@./CLAUDE.md' in (REPO / 'GEMINI.md').read_text()


def run_install(
  tmp_path: Path, runtime: str, *extra: str, skills: tuple[str, ...] = ('brainstorming',)
):
  skill_args = [arg for name in skills for arg in ('--skill', name)]
  return subprocess.run(
    [sys.executable, str(INSTALL), runtime, '--home', str(tmp_path), *skill_args, *extra],
    cwd=REPO,
    capture_output=True,
    text=True,
  )


def tree(root: Path) -> list[Path]:
  return sorted(path.relative_to(root) for path in root.rglob('*'))


COMPANION_DIRS = {
  'claude': ('.claude/agents', '.claude/commands'),
  'codex': ('.codex/agents',),
  'gemini': ('.gemini/agents', '.gemini/commands'),
}


def test_codex_install_links_shared_skill_and_native_agents(tmp_path):
  result = run_install(tmp_path, 'codex', '--companions')
  assert result.returncode == 0, result.stdout + result.stderr
  assert (tmp_path / '.agents/skills/brainstorming').is_symlink()
  assert (tmp_path / '.codex/agents/code-reviewer.toml').is_symlink()
  assert not (tmp_path / '.codex/commands').exists()


def test_gemini_install_links_skill_agents_and_commands(tmp_path):
  result = run_install(tmp_path, 'gemini', '--companions')
  assert result.returncode == 0, result.stdout + result.stderr
  assert (tmp_path / '.agents/skills/brainstorming').is_symlink()
  assert (tmp_path / '.gemini/agents/debugger.md').is_symlink()
  assert (tmp_path / '.gemini/commands/deferred.toml').is_symlink()


def test_all_install_is_idempotent_across_shared_skill_root(tmp_path):
  first = run_install(tmp_path, 'all', '--companions')
  second = run_install(tmp_path, 'all', '--companions')
  assert first.returncode == 0, first.stdout + first.stderr
  assert second.returncode == 0, second.stdout + second.stderr
  assert (tmp_path / '.claude/skills/brainstorming').is_symlink()
  assert (tmp_path / '.agents/skills/brainstorming').is_symlink()
  assert (tmp_path / '.claude/agents/code-reviewer.md').is_symlink()
  assert (tmp_path / '.claude/commands/deferred.md').is_symlink()


@pytest.mark.parametrize('runtime', sorted(COMPANION_DIRS))
def test_skill_selection_skips_companions_by_default(tmp_path, runtime):
  result = run_install(tmp_path, runtime)
  assert result.returncode == 0, result.stdout + result.stderr
  skill_root = '.claude/skills' if runtime == 'claude' else '.agents/skills'
  assert (tmp_path / skill_root / 'brainstorming').is_symlink()
  for companion_dir in COMPANION_DIRS[runtime]:
    assert not (tmp_path / companion_dir).exists()


@pytest.mark.parametrize(
  ('skills', 'flags', 'expect_companions'),
  [
    (('brainstorming',), (), False),
    (('brainstorming',), ('--companions',), True),
    ((), (), True),
    ((), ('--no-companions',), False),
  ],
)
def test_companion_flag_overrides_the_skill_based_default(
  tmp_path, skills, flags, expect_companions
):
  result = run_install(tmp_path, 'codex', *flags, skills=skills)
  assert result.returncode == 0, result.stdout + result.stderr
  assert (tmp_path / '.agents/skills/brainstorming').is_symlink()
  companion = tmp_path / '.codex/agents/code-reviewer.toml'
  assert companion.is_symlink() == expect_companions


def test_install_refuses_to_replace_an_unmanaged_path(tmp_path):
  occupied = tmp_path / '.agents/skills/brainstorming'
  occupied.mkdir(parents=True)
  result = run_install(tmp_path, 'codex')
  assert result.returncode == 1
  assert 'refusing to replace' in result.stderr


def test_conflict_late_in_the_plan_writes_nothing(tmp_path):
  # Companions follow every skill in plan order, so a conflicting agent is
  # reached only after all skills; a per-item check would have linked them.
  occupied = tmp_path / '.claude/agents/code-reviewer.md'
  occupied.parent.mkdir(parents=True)
  occupied.write_text('hand-made\n')
  before = tree(tmp_path)
  result = run_install(tmp_path, 'claude', skills=())
  assert result.returncode == 1
  assert str(occupied) in result.stderr
  assert tree(tmp_path) == before
  assert occupied.read_text() == 'hand-made\n'


@pytest.mark.parametrize('extra', [(), ('--dry-run',)])
def test_install_reports_every_conflict(tmp_path, extra):
  skill = tmp_path / '.claude/skills/brainstorming'
  skill.mkdir(parents=True)
  agent = tmp_path / '.claude/agents/code-reviewer.md'
  agent.parent.mkdir(parents=True)
  agent.write_text('hand-made\n')
  result = run_install(tmp_path, 'claude', *extra, skills=())
  assert result.returncode == 1
  assert str(skill) in result.stderr
  assert str(agent) in result.stderr


def test_aliased_skill_roots_install_each_skill_once(tmp_path):
  (tmp_path / '.agents/skills').mkdir(parents=True)
  (tmp_path / '.claude').mkdir()
  (tmp_path / '.claude/skills').symlink_to('../.agents/skills', target_is_directory=True)
  result = run_install(tmp_path, 'all', '--copy')
  assert result.returncode == 0, result.stdout + result.stderr
  assert len(result.stdout.splitlines()) == 1
  assert (tmp_path / '.agents/skills/brainstorming/SKILL.md').is_file()


@pytest.mark.parametrize('extra', [(), ('--dry-run',)])
def test_aliased_destinations_with_different_sources_write_nothing(tmp_path, extra):
  # Claude and Gemini ship different agent files under the same names, so one
  # directory cannot hold both; plan() must see through the alias.
  (tmp_path / '.claude/agents').mkdir(parents=True)
  (tmp_path / '.gemini').mkdir()
  (tmp_path / '.gemini/agents').symlink_to('../.claude/agents', target_is_directory=True)
  before = tree(tmp_path)
  result = run_install(tmp_path, 'all', '--companions', *extra)
  assert result.returncode == 1
  assert 'conflicting sources' in result.stderr
  assert str(tmp_path / '.claude/agents') in result.stderr
  assert str(tmp_path / '.gemini/agents') in result.stderr
  assert tree(tmp_path) == before


def test_help_keeps_docstring_examples_on_their_own_lines():
  result = subprocess.run(
    [sys.executable, str(INSTALL), '--help'],
    capture_output=True,
    text=True,
    env={**os.environ, 'COLUMNS': '80'},
  )
  assert result.returncode == 0, result.stderr
  assert '\n  python3 install.py gemini --skill bayesian-workflow --companions\n' in (
    result.stdout
  )
