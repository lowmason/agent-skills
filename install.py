#!/usr/bin/env python3
'''Install this repository's skills and runtime-native companion assets.

Examples:
  python3 install.py codex
  python3 install.py gemini --skill bayesian-workflow
  python3 install.py gemini --skill bayesian-workflow --companions
  python3 install.py all --copy

Symlinks are the default, so edits to installed items are live; re-run after a
pull that adds skills, agents, or commands.
A full install also links each runtime's companion agents and commands. --skill
installs the named skills plus what they cannot work without (the DEPENDENCIES
table in install.py); other companions only with --companions. The installer
never replaces a path it does not already manage, and it checks every
destination before writing, so a conflict leaves nothing half-installed.
'''
from __future__ import annotations

import argparse
import fnmatch
import os
import shutil
import subprocess
import sys
from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path


REPO = Path(__file__).resolve().parent

# Hard dependencies: what a skill or command cannot work without because it
# runs, reads, or sends you to it. --skill follows them transitively; a
# command installs only where its runtime has command adapters, and never
# under --no-companions. build/test_runtime_support.py checks this table
# against the references in skill and command text.
DEPENDENCIES: dict[str, tuple[str, ...]] = {
  'command:deferred': ('skill:writing-plans',),
  'skill:clean-code': ('skill:clean-coder',),
  'skill:clean-coder': ('skill:clean-code',),
  'skill:derive-roadmap': ('command:deferred',),
  'skill:executing-plans': (
    'skill:requesting-code-review',
    'skill:writing-plans',
  ),
  'skill:finishing-a-development-branch': (
    'command:deferred',
    'skill:requesting-code-review',
    'skill:writing-plans',
  ),
  'skill:recommend-visualization': ('skill:explore-data',),
  'skill:subagent-driven-development': (
    'skill:requesting-code-review',
    'skill:writing-plans',
  ),
  'skill:track-model-experiments': ('skill:bayesian-workflow',),
  'skill:writing-plans': ('command:deferred',),
}

# .gitignore's generic entries, for --copy where git cannot say what to keep.
FALLBACK_IGNORES = (
  '.DS_Store', '__pycache__', '*.pyc', '.pytest_cache', '.hypothesis',
  '.verify_venv', 'settings.local.json', '.sdd', 'review',
)


@dataclass(frozen=True)
class InstallItem:
  source: Path
  destination: Path


class InstallError(RuntimeError):
  pass


def skill_names() -> list[str]:
  return sorted(
    path.name
    for path in (REPO / 'skills').iterdir()
    if path.is_dir() and (path / 'SKILL.md').is_file()
  )


def selected_skills(requested: list[str] | None) -> list[str]:
  available = skill_names()
  if not requested:
    return available
  unknown = sorted(set(requested) - set(available))
  if unknown:
    raise InstallError(
      f'unknown skill(s): {", ".join(unknown)}; available: {", ".join(available)}'
    )
  return list(dict.fromkeys(requested))


def with_dependencies(
  skills: list[str], commands: Collection[str] = ()
) -> tuple[list[str], list[str]]:
  '''Return the skills and commands these need, transitively, themselves included.'''
  closure: dict[str, None] = {}
  pending = [f'skill:{name}' for name in skills] + [f'command:{name}' for name in commands]
  while pending:
    node = pending.pop(0)
    if node not in closure:
      closure[node] = None
      pending.extend(DEPENDENCIES.get(node, ()))
  by_kind: dict[str, list[str]] = {'skill': [], 'command': []}
  for node in closure:
    kind, _, name = node.partition(':')
    by_kind[kind].append(name)
  return by_kind['skill'], by_kind['command']


def files(source_dir: Path, suffix: str) -> list[Path]:
  return sorted(path for path in source_dir.glob(f'*{suffix}') if path.is_file())


def file_items(source_dir: Path, suffix: str, destination_dir: Path) -> list[InstallItem]:
  return [
    InstallItem(source, destination_dir / source.name)
    for source in files(source_dir, suffix)
  ]


def runtime_items(
  runtime: str,
  home: Path,
  skills: list[str],
  *,
  companions: bool,
  commands: Collection[str] = (),
) -> list[InstallItem]:
  runtimes = REPO / 'runtimes'
  if runtime == 'claude':
    skill_root = home / '.claude' / 'skills'
    agent_items = file_items(REPO / 'agents', '.md', home / '.claude' / 'agents')
    command_items = file_items(REPO / 'commands', '.md', home / '.claude' / 'commands')
  elif runtime == 'codex':
    skill_root = home / '.agents' / 'skills'
    agent_items = file_items(
      runtimes / 'codex' / 'agents', '.toml', home / '.codex' / 'agents'
    )
    command_items = []
  elif runtime == 'gemini':
    skill_root = home / '.agents' / 'skills'
    agent_items = file_items(
      runtimes / 'gemini' / 'agents', '.md', home / '.gemini' / 'agents'
    )
    command_items = file_items(
      runtimes / 'gemini' / 'commands', '.toml', home / '.gemini' / 'commands'
    )
  else:
    raise InstallError(f'unsupported runtime: {runtime}')
  skill_items = [InstallItem(REPO / 'skills' / name, skill_root / name) for name in skills]
  if companions:
    return skill_items + agent_items + command_items
  return skill_items + [item for item in command_items if item.source.stem in commands]


def plan(
  runtime: str,
  home: Path,
  skills: list[str],
  *,
  companions: bool,
  commands: Collection[str] = (),
) -> list[InstallItem]:
  runtimes = ('claude', 'codex', 'gemini') if runtime == 'all' else (runtime,)
  by_location: dict[Path, InstallItem] = {}
  for name in runtimes:
    items = runtime_items(name, home, skills, companions=companions, commands=commands)
    for item in items:
      location = physical_location(item.destination)
      existing = by_location.get(location)
      if existing is None:
        by_location[location] = item
      elif existing.source != item.source:
        alias = (
          '' if existing.destination == item.destination
          else f' (also reached as {item.destination})'
        )
        raise InstallError(
          f'conflicting sources for {existing.destination}{alias}: '
          f'{existing.source} and {item.source}'
        )
  return list(by_location.values())


def physical_location(destination: Path) -> Path:
  # Two runtime directories can be one directory through a symlink. Resolve
  # the parent only, so a managed symlink at the leaf keeps its own name.
  # Python 3.9 raises RuntimeError on a symlink loop; plan by the path as
  # written and let the write report it, as later Pythons do.
  try:
    return destination.parent.resolve() / destination.name
  except (OSError, RuntimeError):
    return destination


def is_managed_symlink(item: InstallItem) -> bool:
  if not item.destination.is_symlink():
    return False
  try:
    return item.destination.resolve() == item.source.resolve()
  except (OSError, RuntimeError):  # a symlink loop is never ours
    return False


def destination_state(item: InstallItem, *, copy: bool) -> str:
  destination = item.destination
  if not (destination.exists() or destination.is_symlink()):
    return 'absent'
  if not copy and is_managed_symlink(item):
    return 'managed'
  return 'unmanaged'


def preflight(
  items: list[InstallItem],
  *,
  copy: bool,
  copies: dict[Path, list[Path]] | None = None,
) -> None:
  unmanaged = [
    item.destination
    for item in items
    if destination_state(item, copy=copy) == 'unmanaged'
  ]
  if unmanaged:
    noun = 'path' if len(unmanaged) == 1 else 'paths'
    listing = ''.join(f'\n  {path}' for path in unmanaged)
    raise InstallError(
      f'refusing to replace existing unmanaged {noun}; nothing was installed:{listing}'
    )
  if copy:
    # Only what would be copied: a venv's links inside an ignored dir are fine.
    linked = [item.source for item in items if item.source.is_symlink()]
    for source, files in (copies or {}).items():
      linked += [source / path for path in files if (source / path).is_symlink()]
    if linked:
      listing = ''.join(f'\n  {path}' for path in linked)
      raise InstallError(
        f'--copy would follow these symlinks, so nothing was installed:{listing}'
      )


def git_env() -> dict[str, str]:
  # A hook or shell may export GIT_DIR, GIT_INDEX_FILE, and the like, which
  # would point git at another repository's index.
  local = subprocess.run(
    ['git', 'rev-parse', '--local-env-vars'], capture_output=True, text=True, check=True
  ).stdout.split()
  return {name: value for name, value in os.environ.items() if name not in local}


def kept_files(source: Path) -> list[Path] | None:
  '''Files under source that git keeps: tracked, or untracked and not ignored.

  None when git cannot say: no git, not a checkout, or source ignored whole.
  '''
  try:
    listing = subprocess.run(
      ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
      cwd=source,
      env=git_env(),
      capture_output=True,
      check=True,
    ).stdout
  except (OSError, subprocess.CalledProcessError):
    return None
  files = [Path(os.fsdecode(entry)) for entry in listing.split(b'\0') if entry]
  # --cached also lists tracked files deleted from the working tree; exists()
  # would drop a dangling link too, hiding it from the symlink refusal.
  return [
    path for path in files if (source / path).exists() or (source / path).is_symlink()
  ] or None


def copy_list(source: Path) -> list[Path]:
  '''The files --copy writes for source, relative to it: what git keeps, or,
  when git cannot say, everything outside .gitignore's generic patterns.
  A symlink appears as one entry, never descended into.'''
  kept = kept_files(source)
  if kept is not None:
    return kept

  def fallback_ignores(name: str) -> bool:
    return any(fnmatch.fnmatch(name, pattern) for pattern in FALLBACK_IGNORES)

  found: list[Path] = []
  for directory, subdirectories, filenames in os.walk(source):
    here = Path(directory)
    subdirectories[:] = [name for name in subdirectories if not fallback_ignores(name)]
    found += [
      (here / name).relative_to(source)
      for name in subdirectories
      if (here / name).is_symlink()
    ]
    found += [
      (here / name).relative_to(source)
      for name in filenames
      if not fallback_ignores(name)
    ]
  return found


def copy_files(source: Path, destination: Path, files: list[Path]) -> None:
  for path in files:
    (destination / path).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source / path, destination / path)


def install_item(
  item: InstallItem,
  *,
  copy: bool,
  dry_run: bool,
  files: list[Path] | None = None,
) -> str:
  destination = item.destination
  state = destination_state(item, copy=copy)
  if state == 'managed':
    return f'unchanged {destination}'
  if state == 'unmanaged':
    raise InstallError(f'refusing to replace existing unmanaged path: {destination}')
  if dry_run:
    action = 'copy' if copy else 'link'
    return f'would {action} {item.source} -> {destination}'
  destination.parent.mkdir(parents=True, exist_ok=True)
  if copy:
    if item.source.is_dir():
      if files is None:
        files = copy_list(item.source)
      copy_files(item.source, destination, files)
    else:
      shutil.copy2(item.source, destination)
    return f'copied {item.source} -> {destination}'
  destination.symlink_to(item.source, target_is_directory=item.source.is_dir())
  return f'linked {item.source} -> {destination}'


def main(argv: list[str] | None = None) -> int:
  parser = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
  )
  parser.add_argument('runtime', choices=('claude', 'codex', 'gemini', 'all'))
  parser.add_argument(
    '--skill',
    action='append',
    dest='skills',
    metavar='NAME',
    help='install this skill instead of all skills (repeatable), plus the '
    'skills and commands it depends on; other companions are then skipped '
    'unless --companions is given',
  )
  parser.add_argument(
    '--companions',
    action=argparse.BooleanOptionalAction,
    help="also link the runtime's agents and commands; "
    'default: on for a full install, off with --skill; turning it off '
    'also drops the commands a skill requires',
  )
  parser.add_argument(
    '--copy',
    action='store_true',
    help='copy instead of symlinking, skipping files git ignores',
  )
  parser.add_argument('--dry-run', action='store_true', help='show actions without writing')
  parser.add_argument(
    '--home',
    type=Path,
    default=Path.home(),
    help=argparse.SUPPRESS,
  )
  args = parser.parse_args(argv)
  companions = not args.skills if args.companions is None else args.companions
  try:
    skills = selected_skills(args.skills)
    commands: list[str] = []
    if args.skills:
      # --companions installs every command, so their dependencies come too.
      every_command = [path.stem for path in files(REPO / 'commands', '.md')]
      skills, commands = with_dependencies(skills, every_command if companions else ())
    if args.companions is False:
      commands = []
    items = plan(
      args.runtime,
      args.home.expanduser(),
      skills,
      companions=companions,
      commands=commands,
    )
    # Decide each copy's files once, so the symlink check sees what is copied.
    # A linked source is refused whole, so its target is never scanned.
    copies = (
      {
        item.source: copy_list(item.source)
        for item in items
        if item.source.is_dir() and not item.source.is_symlink()
      }
      if args.copy
      else {}
    )
    preflight(items, copy=args.copy, copies=copies)
    for item in items:
      to_copy = copies.get(item.source)
      print(install_item(item, copy=args.copy, dry_run=args.dry_run, files=to_copy))
  except (InstallError, OSError) as exc:
    print(f'install: {exc}', file=sys.stderr)
    return 1
  return 0


if __name__ == '__main__':
  sys.exit(main())
