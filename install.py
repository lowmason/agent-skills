#!/usr/bin/env python3
'''Install this repository's skills and runtime-native companion assets.

Examples:
  python3 install.py codex
  python3 install.py gemini --skill bayesian-workflow
  python3 install.py gemini --skill bayesian-workflow --companions
  python3 install.py all --copy

Symlinks are the default so edits in this checkout are picked up immediately.
A full install also links each runtime's companion agents and commands; --skill
installs only the named skills unless --companions is given. The installer
never replaces a path it does not already manage, and it checks every
destination before writing, so a conflict leaves nothing half-installed.
'''
from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


REPO = Path(__file__).resolve().parent


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


def files(source_dir: Path, suffix: str) -> list[Path]:
  return sorted(path for path in source_dir.glob(f'*{suffix}') if path.is_file())


def file_items(source_dir: Path, suffix: str, destination_dir: Path) -> list[InstallItem]:
  return [
    InstallItem(source, destination_dir / source.name)
    for source in files(source_dir, suffix)
  ]


def runtime_items(
  runtime: str, home: Path, skills: list[str], *, companions: bool
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
  return (skill_items + agent_items + command_items) if companions else skill_items


def plan(
  runtime: str, home: Path, skills: list[str], *, companions: bool
) -> list[InstallItem]:
  runtimes = ('claude', 'codex', 'gemini') if runtime == 'all' else (runtime,)
  by_location: dict[Path, InstallItem] = {}
  for name in runtimes:
    for item in runtime_items(name, home, skills, companions=companions):
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


def preflight(items: list[InstallItem], *, copy: bool) -> None:
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


def install_item(item: InstallItem, *, copy: bool, dry_run: bool) -> str:
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
      shutil.copytree(item.source, destination)
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
    help='install this skill instead of all skills (repeatable); '
    'companions are then skipped unless --companions is given',
  )
  parser.add_argument(
    '--companions',
    action=argparse.BooleanOptionalAction,
    help="also link the runtime's agents and commands; "
    'default: on for a full install, off with --skill',
  )
  parser.add_argument('--copy', action='store_true', help='copy instead of symlinking')
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
    items = plan(args.runtime, args.home.expanduser(), skills, companions=companions)
    preflight(items, copy=args.copy)
    for item in items:
      print(install_item(item, copy=args.copy, dry_run=args.dry_run))
  except (InstallError, OSError) as exc:
    print(f'install: {exc}', file=sys.stderr)
    return 1
  return 0


if __name__ == '__main__':
  sys.exit(main())
