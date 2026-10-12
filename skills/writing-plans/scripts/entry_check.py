#!/usr/bin/env python3
'''Report what a planning session checks before it plans a spec.

Run from the repo root:

    uv run --no-project --python 3.13 python <this-skill-dir>/scripts/entry_check.py [SPEC]

It prints the ``plan ids:`` field, drawn from every branch and remote-tracking
ref (symbolic refs such as ``origin/HEAD`` skipped) and from every worktree's
``specs/plans/``, untracked plans included: the highest id and where it
occurs, the next free id, any id used by two different plan filenames, and,
given a spec path, any plan whose name ends in the spec's stem.

A reporter, like deferred_stats.py: it is read-only and exits 0 whenever it
prints a report. It exits 2 only when it cannot run: outside a git
repository, given a spec path that does not exist or is not a file, or given
a spec outside this repository.
'''

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

CANNOT_RUN = 2
PLAN_RE = re.compile(r'^(?P<id>\d+)-(?P<name>.+)\.md$')


class CannotRun(Exception):
    '''The report cannot be produced; main() prints the reason and exits 2.'''


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True, check=False)


def git_out(root: Path, *args: str) -> str:
    done = git(root, *args)
    if done.returncode != 0:
        raise CannotRun(done.stderr.strip() or f'git {" ".join(args)} failed')
    return done.stdout


def repo_root(cwd: Path) -> Path:
    done = git(cwd, 'rev-parse', '--show-toplevel')
    if done.returncode != 0:
        raise CannotRun('not inside a git repository')
    return Path(done.stdout.strip())


@dataclass
class Plan:
    name: str
    locations: list[str] = field(default_factory=list)


def ref_names(root: Path) -> list[str]:
    '''Every branch and remote-tracking ref, skipping symbolic ones like origin/HEAD.'''
    out = git_out(root, 'for-each-ref', '--format=%(refname)%09%(symref)', 'refs/heads', 'refs/remotes')
    refs = []
    for line in out.splitlines():
        ref, _, symref = line.partition('\t')
        if ref and not symref:
            refs.append(ref)
    return refs


def worktree_paths(root: Path) -> list[Path]:
    out = git_out(root, 'worktree', 'list', '--porcelain')
    return [Path(line.removeprefix('worktree ')) for line in out.splitlines() if line.startswith('worktree ')]


def plan_sightings(root: Path) -> list[tuple[str, str]]:
    '''(filename, location) for every file under specs/plans on every ref and in every worktree.'''
    seen = []
    for ref in ref_names(root):
        short = ref.removeprefix('refs/heads/').removeprefix('refs/remotes/')
        listing = git(root, 'ls-tree', '-r', '--name-only', ref, '--', 'specs/plans')
        seen.extend((Path(path).name, short) for path in listing.stdout.splitlines())
    for tree in worktree_paths(root):
        plans = tree / 'specs' / 'plans'
        if plans.is_dir():
            seen.extend((path.name, f'worktree {tree}') for path in sorted(plans.rglob('*.md')))
    return seen


def plans_by_id(root: Path) -> dict[int, list[Plan]]:
    by_id: dict[int, dict[str, Plan]] = {}
    for filename, where in plan_sightings(root):
        m = PLAN_RE.match(filename)
        if not m:
            continue
        plan = by_id.setdefault(int(m['id']), {}).setdefault(filename, Plan(filename))
        if where not in plan.locations:
            plan.locations.append(where)
    return {pid: list(plans.values()) for pid, plans in by_id.items()}


def describe(plans: list[Plan]) -> str:
    return '; '.join(f'{p.name} ({", ".join(p.locations)})' for p in plans)


def names_spec(plan: Plan, stem: str) -> bool:
    name = PLAN_RE.match(plan.name)['name']
    return name == stem or name.endswith(f'-{stem}')


def format_plan_ids(by_id: dict[int, list[Plan]], stem: str | None) -> list[str]:
    lines = ['plan ids:']
    if by_id:
        top = max(by_id)
        lines += [f'  highest: {top} — {describe(by_id[top])}', f'  next free: {top + 1}']
    else:
        lines += ['  highest: none', '  next free: 1']
    collisions = [(pid, by_id[pid]) for pid in sorted(by_id) if len(by_id[pid]) > 1]
    if collisions:
        lines.append('  collisions:')
        lines += [f'    {pid}: {describe(plans)}' for pid, plans in collisions]
    else:
        lines.append('  collisions: none')
    if stem is not None:
        mine = [p for pid in sorted(by_id) for p in by_id[pid] if names_spec(p, stem)]
        lines.append(f'  plans for this spec: {describe(mine) if mine else "none"}')
    return lines


def report(root: Path, spec: Path | None) -> list[str]:
    return format_plan_ids(plans_by_id(root), spec.stem if spec is not None else None)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Report what a planning session checks before it plans a spec.')
    parser.add_argument('spec', nargs='?', type=Path, help='the spec about to be planned')
    args = parser.parse_args(argv)
    try:
        root = repo_root(Path.cwd())
        spec = None
        if args.spec is not None:
            if args.spec.is_dir():
                raise CannotRun(f'not a file: {args.spec}')
            if not args.spec.is_file():
                raise CannotRun(f'no such spec: {args.spec}')
            try:
                spec = args.spec.resolve().relative_to(root.resolve())
            except ValueError:
                raise CannotRun(f'spec is outside this repository: {args.spec}') from None
        print('\n'.join(report(root, spec)))
    except CannotRun as e:
        print(f'entry_check: {e}', file=sys.stderr)
        return CANNOT_RUN
    return 0


if __name__ == '__main__':
    sys.exit(main())
