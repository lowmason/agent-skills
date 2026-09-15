import importlib.util
import subprocess
import sys
import tomllib
from pathlib import Path


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


def run_install(tmp_path: Path, runtime: str, *extra: str):
  return subprocess.run(
    [
      sys.executable,
      str(INSTALL),
      runtime,
      '--home',
      str(tmp_path),
      '--skill',
      'brainstorming',
      *extra,
    ],
    cwd=REPO,
    capture_output=True,
    text=True,
  )


def test_codex_install_links_shared_skill_and_native_agents(tmp_path):
  result = run_install(tmp_path, 'codex')
  assert result.returncode == 0, result.stdout + result.stderr
  assert (tmp_path / '.agents/skills/brainstorming').is_symlink()
  assert (tmp_path / '.codex/agents/code-reviewer.toml').is_symlink()
  assert not (tmp_path / '.codex/commands').exists()


def test_gemini_install_links_skill_agents_and_commands(tmp_path):
  result = run_install(tmp_path, 'gemini')
  assert result.returncode == 0, result.stdout + result.stderr
  assert (tmp_path / '.agents/skills/brainstorming').is_symlink()
  assert (tmp_path / '.gemini/agents/debugger.md').is_symlink()
  assert (tmp_path / '.gemini/commands/deferred.toml').is_symlink()


def test_all_install_is_idempotent_across_shared_skill_root(tmp_path):
  first = run_install(tmp_path, 'all')
  second = run_install(tmp_path, 'all')
  assert first.returncode == 0, first.stdout + first.stderr
  assert second.returncode == 0, second.stdout + second.stderr
  assert (tmp_path / '.claude/skills/brainstorming').is_symlink()
  assert (tmp_path / '.agents/skills/brainstorming').is_symlink()


def test_install_refuses_to_replace_an_unmanaged_path(tmp_path):
  occupied = tmp_path / '.agents/skills/brainstorming'
  occupied.mkdir(parents=True)
  result = run_install(tmp_path, 'codex')
  assert result.returncode == 1
  assert 'refusing to replace' in result.stderr
