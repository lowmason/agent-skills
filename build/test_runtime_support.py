import importlib.util
import os
import re
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


def load_install(monkeypatch):
  spec = importlib.util.spec_from_file_location('install', INSTALL)
  assert spec is not None and spec.loader is not None
  install = importlib.util.module_from_spec(spec)
  monkeypatch.setitem(sys.modules, 'install', install)  # @dataclass looks it up
  spec.loader.exec_module(install)
  return install


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


def installed_links(root: Path) -> set[str]:
  return {str(path.relative_to(root)) for path in root.rglob('*') if path.is_symlink()}


@pytest.mark.parametrize(
  ('runtime', 'skill', 'flags', 'expected'),
  [
    ('claude', 'finishing-a-development-branch', (), {
      '.claude/skills/finishing-a-development-branch',
      '.claude/skills/requesting-code-review',
      '.claude/skills/writing-plans',
      '.claude/commands/deferred.md',
    }),
    ('claude', 'finishing-a-development-branch', ('--no-companions',), {
      '.claude/skills/finishing-a-development-branch',
      '.claude/skills/requesting-code-review',
      '.claude/skills/writing-plans',
    }),
    ('gemini', 'derive-roadmap', (), {
      '.agents/skills/derive-roadmap',
      '.agents/skills/writing-plans',
      '.gemini/commands/deferred.toml',
    }),
    # Codex has no command adapters, but /deferred's own skill dependency holds.
    ('codex', 'derive-roadmap', (), {
      '.agents/skills/derive-roadmap',
      '.agents/skills/writing-plans',
    }),
    # So does dropping the command with --no-companions.
    ('claude', 'derive-roadmap', ('--no-companions',), {
      '.claude/skills/derive-roadmap',
      '.claude/skills/writing-plans',
    }),
    ('claude', 'recommend-visualization', (), {
      '.claude/skills/recommend-visualization',
      '.claude/skills/explore-data',
    }),
    ('claude', 'clean-coder', (), {
      '.claude/skills/clean-coder',
      '.claude/skills/clean-code',
    }),
    # writing-plans -> /deferred -> writing-plans is a cycle.
    ('claude', 'writing-plans', (), {
      '.claude/skills/writing-plans',
      '.claude/commands/deferred.md',
    }),
    # So is clean-code <-> clean-coder.
    ('claude', 'clean-code', (), {
      '.claude/skills/clean-code',
      '.claude/skills/clean-coder',
    }),
    ('claude', 'executing-plans', (), {
      '.claude/skills/executing-plans',
      '.claude/skills/requesting-code-review',
      '.claude/skills/writing-plans',
      '.claude/commands/deferred.md',
    }),
    ('claude', 'track-model-experiments', (), {
      '.claude/skills/track-model-experiments',
      '.claude/skills/bayesian-workflow',
    }),
  ],
)
def test_skill_brings_its_hard_dependencies(tmp_path, runtime, skill, flags, expected):
  result = run_install(tmp_path, runtime, *flags, skills=(skill,))
  assert result.returncode == 0, result.stdout + result.stderr
  assert installed_links(tmp_path) == expected


@pytest.mark.parametrize(
  ('skill', 'required'),
  [
    # --companions installs /deferred, which needs writing-plans.
    ('brainstorming', {'.claude/skills/writing-plans'}),
    ('finishing-a-development-branch', {
      '.claude/skills/requesting-code-review',
      '.claude/skills/writing-plans',
    }),
  ],
)
def test_companions_keep_the_dependency_closure(tmp_path, skill, required):
  result = run_install(tmp_path, 'claude', '--companions', skills=(skill,))
  assert result.returncode == 0, result.stdout + result.stderr
  links = installed_links(tmp_path)
  assert {f'.claude/skills/{skill}', '.claude/commands/deferred.md'} <= links
  assert '.claude/agents/code-reviewer.md' in links
  assert required <= links


TEXT_SUFFIXES = {'.md', '.py', '.sh', '.js', '.cjs'}
# Agents load a skill's SKILL.md, references, and scripts; READMEs and install
# guides are for people, so their links are not dependencies.
HUMAN_DOCS = {'README.md', 'INSTALL.md'}
# References the scan finds that are not hard dependencies: the source works
# without the target installed. An entry excuses its whole edge, so a hard
# reference added later between the same two skills passes unnoticed.
SOFT_REFERENCES = {
  # Says where the plan-completion protocol retires specs; never runs it.
  ('skill:brainstorming', 'skill:writing-plans'),
  # Names the routing header its input spec carries; never reads the file.
  ('skill:derive-roadmap', 'skill:describe-critique-methodology'),
  # Likens a stage to writing-plans' Scope Check; an analogy, not a step.
  ('skill:derive-roadmap', 'skill:writing-plans'),
  # Names SDD's Model Selection but gives the tier aliases inline.
  ('skill:dispatching-parallel-agents', 'skill:subagent-driven-development'),
  # A docstring contrasting its signals with profile.py's; never calls it.
  ('skill:recommend-probabilistic-model', 'skill:explore-data'),
  # Routes posterior plots to bayesian-workflow's own guide instead.
  ('skill:recommend-visualization', 'skill:bayesian-workflow'),
  # Likens its extra signals to characterize.py's; never runs it.
  ('skill:recommend-visualization', 'skill:recommend-probabilistic-model'),
  # Names SDD's Model Selection but gives the review tiers and aliases inline;
  # SDD's review-package and task-reviewer prompt apply only when SDD calls.
  ('skill:requesting-code-review', 'skill:subagent-driven-development'),
  # Hands a tuned model on to the experiments ledger; a next step.
  ('skill:tune-hyperparameters', 'skill:track-model-experiments'),
  # Quotes an @-path as an example of what not to write.
  ('skill:writing-skills', 'skill:writing-plans'),
}


def referenced_dependencies() -> set[tuple[str, str]]:
  skills = {path.name for path in (REPO / 'skills').iterdir() if (path / 'SKILL.md').is_file()}
  commands = {path.stem for path in (REPO / 'commands').glob('*.md')}
  names = '|'.join(sorted(map(re.escape, skills), key=len, reverse=True))
  command_ref = re.compile(rf"(?<![\w/.-])/({'|'.join(map(re.escape, commands))})\b")
  skill_ref = re.compile(
    # A path into the skill: ../x/..., skills/x/..., x/references/...
    rf'(?<![\w-])({names})/(?:references/|scripts/|[\w.-]+\.(?:md|py)\b)'
    # The name, then a file, a references/ or scripts/ path, or a § section.
    rf"|(?<![\w/-])({names})`?(?:'s|'|’s)?(?: skill's| skill’s)?\s+"
    rf'(?:§|`?(?:references|scripts)/|\[?`?[\w.-]+\.(?:md|py)\b)'
    # A named section: "x's Model Selection", "x skill's Confirmation Gate".
    rf"|(?<![\w/-])({names})(?:'s|'|’s| skill's| skill’s)\s+[A-Z][a-z]+(?:[ -][A-Z][a-z]+)*"
    # "the x skill (its "Section" section)".
    rf'|(?<![\w/-])({names}) skill \(its "'
  )

  def scan(source: str, text: str) -> set[tuple[str, str]]:
    found = {(source, f'command:{name}') for name in command_ref.findall(text)}
    found |= {
      (source, 'skill:' + next(group for group in m.groups() if group))
      for m in skill_ref.finditer(text)
    }
    return {(source, target) for source, target in found if source != target}

  edges: set[tuple[str, str]] = set()
  for name in skills:
    for path in (REPO / 'skills' / name).rglob('*'):
      if path.suffix in TEXT_SUFFIXES and path.name not in HUMAN_DOCS and path.is_file():
        edges |= scan(f'skill:{name}', path.read_text(errors='ignore'))
  for name in commands:
    edges |= scan(f'command:{name}', (REPO / 'commands' / f'{name}.md').read_text())
  return edges


def test_declared_dependencies_match_skill_and_command_text(monkeypatch):
  install = load_install(monkeypatch)
  declared = {
    (source, target)
    for source, targets in install.DEPENDENCIES.items()
    for target in targets
  }
  referenced = referenced_dependencies()
  assert SOFT_REFERENCES <= referenced, 'a soft reference is gone; drop it'
  assert declared == referenced - SOFT_REFERENCES


def test_symlink_loop_is_a_conflict_not_a_crash(tmp_path, monkeypatch):
  # Python 3.9's Path.resolve() raises RuntimeError on a symlink loop where
  # 3.13 does not; emulate it so every interpreter pins the handling.
  install = load_install(monkeypatch)
  loop = tmp_path / 'skills' / 'brainstorming'
  loop.parent.mkdir()
  loop.symlink_to('brainstorming')
  item = install.InstallItem(REPO / 'skills' / 'brainstorming', loop)

  def resolve_like_python39(self, strict=False):
    raise RuntimeError(f'Symlink loop from {str(self)!r}')

  monkeypatch.setattr(Path, 'resolve', resolve_like_python39)
  assert install.physical_location(loop) == loop
  assert install.destination_state(item, copy=False) == 'unmanaged'


def make_skill(root: Path) -> Path:
  skill = root / 'skills' / 'demo'
  (skill / '__pycache__').mkdir(parents=True)
  (skill / 'SKILL.md').write_text('tracked\n')
  (skill / 'draft.md').write_text('untracked, not ignored\n')
  (skill / 'local.env').write_text('SECRET=1\n')
  (skill / '__pycache__' / 'demo.cpython-313.pyc').write_bytes(b'')
  return skill


def init_repo(root: Path, gitignore: str, *tracked: str) -> None:
  (root / '.gitignore').write_text(gitignore)
  subprocess.run(['git', '-C', str(root), 'init', '-q'], check=True)
  if tracked:
    subprocess.run(['git', '-C', str(root), 'add', '-f', *tracked], check=True)


def copy_demo(install, monkeypatch, root: Path, *flags: str) -> tuple[int, Path]:
  monkeypatch.setattr(install, 'REPO', root)
  home = root.parent / 'home'
  status = install.main(['claude', '--skill', 'demo', '--copy', '--home', str(home), *flags])
  return status, home / '.claude' / 'skills' / 'demo'


def names(directory: Path) -> list[str]:
  return sorted(path.name for path in directory.iterdir())


def test_copy_keeps_what_git_keeps(tmp_path, monkeypatch):
  install = load_install(monkeypatch)
  root = tmp_path / 'repo'
  make_skill(root)
  init_repo(root, '__pycache__/\n*.env\n', 'skills/demo/SKILL.md')
  status, copied = copy_demo(install, monkeypatch, root)
  assert status == 0
  assert names(copied) == ['SKILL.md', 'draft.md']


def test_copy_skips_an_ignored_name_with_a_carriage_return(tmp_path, monkeypatch):
  # Finder's custom-icon file is named "Icon\r".
  install = load_install(monkeypatch)
  root = tmp_path / 'repo'
  skill = make_skill(root)
  (skill / 'Icon\r').write_bytes(b'')
  init_repo(root, '__pycache__/\n*.env\nIcon?\n', 'skills/demo/SKILL.md')
  status, copied = copy_demo(install, monkeypatch, root)
  assert status == 0
  assert names(copied) == ['SKILL.md', 'draft.md']


def test_copy_ignores_an_inherited_git_index(tmp_path, monkeypatch):
  # A hook or shell exporting GIT_INDEX_FILE must not change what is tracked.
  install = load_install(monkeypatch)
  root = tmp_path / 'repo'
  skill = make_skill(root)
  (skill / 'keep.pyc').write_bytes(b'')
  init_repo(root, '__pycache__/\n*.env\n*.pyc\n', 'skills/demo/SKILL.md', 'skills/demo/keep.pyc')
  monkeypatch.setenv('GIT_INDEX_FILE', str(tmp_path / 'foreign-index'))
  status, copied = copy_demo(install, monkeypatch, root)
  assert status == 0
  assert names(copied) == ['SKILL.md', 'draft.md', 'keep.pyc']


def test_copy_of_an_excluded_skill_still_skips_caches(tmp_path, monkeypatch):
  # git has nothing to say inside a local-only skill; the fallback applies.
  install = load_install(monkeypatch)
  root = tmp_path / 'repo'
  make_skill(root)
  init_repo(root, '__pycache__/\n*.env\n')
  (root / '.git' / 'info').mkdir(parents=True, exist_ok=True)
  (root / '.git' / 'info' / 'exclude').write_text('skills/demo/\n')
  status, copied = copy_demo(install, monkeypatch, root)
  assert status == 0
  assert names(copied) == ['SKILL.md', 'draft.md', 'local.env']


@pytest.mark.parametrize('flags', [(), ('--dry-run',)])
@pytest.mark.parametrize('git', [True, False])
@pytest.mark.parametrize('target', ['../../secret', 'missing'])
def test_copy_refuses_a_symlink_it_would_copy(tmp_path, monkeypatch, capsys, target, git, flags):
  # Copying follows a link, so it could carry out anything it points at, and
  # would lose a dangling one. A dry run refuses the same way.
  install = load_install(monkeypatch)
  monkeypatch.setenv('GIT_CEILING_DIRECTORIES', str(tmp_path))
  root = tmp_path / 'repo'
  skill = make_skill(root)
  (root / 'secret').mkdir()
  (root / 'secret' / 'extract.txt').write_text('never leaves the repo\n')
  (skill / 'shared').symlink_to(target, target_is_directory=True)
  if git:
    init_repo(root, '__pycache__/\n*.env\nsecret/\n', 'skills/demo/SKILL.md', 'skills/demo/shared')
  status, _ = copy_demo(install, monkeypatch, root, *flags)
  assert status == 1
  assert '--copy would follow these symlinks' in capsys.readouterr().err
  assert not (root.parent / 'home').exists()


def test_copy_installs_the_items_a_link_install_does(tmp_path, monkeypatch):
  # git decides what a copied skill holds, never which items install: a
  # local-only skill or agent, ignored whole, installs either way.
  install = load_install(monkeypatch)
  root = tmp_path / 'repo'
  make_skill(root)
  (root / 'skills' / 'local').mkdir()
  (root / 'skills' / 'local' / 'SKILL.md').write_text('local only\n')
  (root / 'agents').mkdir()
  (root / 'agents' / 'public.md').write_text('tracked\n')
  (root / 'agents' / 'private.md').write_text('local only\n')
  init_repo(root, '__pycache__/\n*.env\n', 'skills/demo/SKILL.md', 'agents/public.md')
  (root / '.git' / 'info' / 'exclude').write_text('agents/private.md\nskills/local/\n')
  monkeypatch.setattr(install, 'REPO', root)

  def installed(*flags: str) -> list[str]:
    home = tmp_path / ('copy' if flags else 'link')
    assert install.main(['claude', '--home', str(home), *flags]) == 0
    return sorted(str(path.relative_to(home)) for path in home.glob('.claude/*/*'))

  assert installed('--copy') == installed() == [
    '.claude/agents/private.md',
    '.claude/agents/public.md',
    '.claude/skills/demo',
    '.claude/skills/local',
  ]


@pytest.mark.parametrize('git', [True, False])
def test_copy_refuses_a_nested_repository_before_writing(tmp_path, monkeypatch, capsys, git):
  # git lists a nested repository as one entry, a directory no file copy
  # takes; outside git, the fallback walk must not copy it file by file.
  install = load_install(monkeypatch)
  monkeypatch.setenv('GIT_CEILING_DIRECTORIES', str(tmp_path))
  root = tmp_path / 'repo'
  skill = make_skill(root)
  if git:
    init_repo(root, '__pycache__/\n*.env\n', 'skills/demo/SKILL.md')
  subprocess.run(['git', 'init', '-q', str(skill / 'vendor')], check=True)
  (skill / 'vendor' / 'lib.py').write_text('tracked elsewhere\n')
  status, _ = copy_demo(install, monkeypatch, root)
  assert status == 1
  # The message, not a word: pytest names tmp_path after the test.
  assert '--copy cannot copy these nested repositories' in capsys.readouterr().err
  assert not (root.parent / 'home').exists()


def test_copy_refuses_a_linked_skill_without_scanning_it(tmp_path, monkeypatch, capsys):
  # The link alone decides the refusal; its target may be a whole other tree.
  install = load_install(monkeypatch)
  root = tmp_path / 'repo'
  elsewhere = tmp_path / 'elsewhere'
  elsewhere.mkdir()
  (elsewhere / 'SKILL.md').write_text('tracked\n')
  (root / 'skills').mkdir(parents=True)
  (root / 'skills' / 'demo').symlink_to(elsewhere, target_is_directory=True)
  scanned = []
  monkeypatch.setattr(install, 'copy_list', lambda source: scanned.append(source) or [])
  status, _ = copy_demo(install, monkeypatch, root, '--dry-run')
  assert status == 1
  assert '--copy would follow these symlinks' in capsys.readouterr().err
  assert scanned == []


@pytest.mark.parametrize(('git', 'expected'), [
  (True, ['SKILL.md', 'draft.md']),
  (False, ['SKILL.md', 'draft.md', 'local.env']),
])
def test_copy_ignores_symlinks_it_would_not_copy(tmp_path, monkeypatch, git, expected):
  # A virtualenv's bin/ holds symlinks, and .verify_venv/ is ignored.
  install = load_install(monkeypatch)
  monkeypatch.setenv('GIT_CEILING_DIRECTORIES', str(tmp_path))
  root = tmp_path / 'repo'
  skill = make_skill(root)
  (skill / '.verify_venv' / 'bin').mkdir(parents=True)
  (skill / '.verify_venv' / 'bin' / 'python').symlink_to('python3')
  if git:
    init_repo(root, '__pycache__/\n*.env\n.verify_venv/\n', 'skills/demo/SKILL.md')
  status, copied = copy_demo(install, monkeypatch, root)
  assert status == 0
  assert names(copied) == expected


def test_copy_outside_git_skips_common_caches(tmp_path, monkeypatch):
  install = load_install(monkeypatch)
  monkeypatch.setenv('GIT_CEILING_DIRECTORIES', str(tmp_path))
  root = tmp_path / 'unpacked'
  make_skill(root)
  status, copied = copy_demo(install, monkeypatch, root)
  assert status == 0
  assert names(copied) == ['SKILL.md', 'draft.md', 'local.env']


def test_fallback_covers_every_generic_gitignore_entry(monkeypatch):
  install = load_install(monkeypatch)
  generic = set()
  for line in (REPO / '.gitignore').read_text().splitlines():
    entry = line.strip().rstrip('/')
    if not entry or entry.startswith('#'):
      continue
    if entry.startswith('**/'):
      entry = entry.removeprefix('**/').rsplit('/', 1)[-1]
    elif '/' in entry:
      continue  # anchored to one path in this checkout
    generic.add(entry)
  assert generic <= set(install.FALLBACK_IGNORES)


@pytest.mark.parametrize('flags', [(), ('--dry-run',)])
def test_link_installs_never_run_git(tmp_path, monkeypatch, flags):
  install = load_install(monkeypatch)

  def no_git(*args, **kwargs):
    raise AssertionError(f'unexpected subprocess: {args}')

  monkeypatch.setattr(install.subprocess, 'run', no_git)
  argv = ['claude', '--skill', 'brainstorming', '--home', str(tmp_path / 'h'), *flags]
  assert install.main(argv) == 0


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
