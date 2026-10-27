#!/usr/bin/env python3
# /// script
# requires-python = '>=3.11'
# dependencies = []
# ///
'''Report what a planning session checks before it plans a spec.

Run from the repo root:

    uv run --no-project python <this-skill-dir>/scripts/entry_check.py [SPEC] [--plan PLAN]

It reads every branch and remote-tracking ref (symbolic refs such as
``origin/HEAD`` skipped) and every worktree's ``specs/plans/``, untracked
plans included, and prints two fields.

``plan ids:`` gives the highest id and where it occurs, the next free id, any
id used by two different plan filenames, and, given a spec path, any plan
whose name ends in the spec's stem.

``overlapping files:`` lists the live plans, each with the number of repo
paths it names, then each path that two or more of them name. A plan stays
live until the default branch (the branch ``origin/HEAD`` names, else
``main`` or ``master``) has it under ``specs/plans/completed/``, so a plan
retired on a branch not yet merged still counts; with no default branch, a
copy under ``completed/`` anywhere retires it. A plan's paths are the union
over its copies, and a copy that cannot be read adds none. Outside fenced
code, a plan names a path with a backticked span outside parentheses on a
``- Create``, ``- Modify`` or ``- Test`` line (a qualifier may come before
the colon), with the first span of an Edit line (``**Edit `PATH`: replace**``,
or the same as a heading or plain text), and with the PATH of an
``<!-- extract-file: PATH -->`` or ``<!-- extract-edit: PATH:LABEL -->``
line. A ``:LINE`` or ``:START-END`` suffix is dropped, and a path counts only
when its first component is an entry at the root of some ref or worktree.
Paths match as written, and a file set named only in prose ("the 13
superpowers SKILL.md files") is not seen, so ``shared: none`` does not prove
that two plans touch different files. ``--plan`` adds a plan saved outside
``specs/plans/``; given the filename of a live plan, it is that plan.

A reporter, like deferred_stats.py: it is read-only and exits 0 whenever it
prints a report. It exits 2 only when it cannot run: outside a git
repository, when a git command it needs fails, given a spec or plan path that
does not exist or is not a file, or given a spec outside this repository.
'''

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

CANNOT_RUN = 2
PLAN_RE = re.compile(r'^(?P<id>\d+)-(?P<name>.+)\.md$')
RETIRED = 'specs/plans/completed/'
FILES_LINE_RE = re.compile(r'^\s*- (?:Create|Modify|Test)\b[^:]*:(?P<rest>.*)$')
EDIT_HEADER_RE = re.compile(r'^\s*(?:#+\s+)?(?:\*\*)?Edit `(?P<span>[^`]+)`')
# A marker is a whole line, as the extract_plan_files.py helper that applies them reads it.
MARKER_RE = re.compile(r'^<!-- extract-(?P<kind>file|edit): (?P<key>\S+) -->$')
FENCE_RE = re.compile(r'^\s*(?P<fence>`{3,}|~{3,})(?P<info>.*)$')
SPAN_OR_PAREN_RE = re.compile(r'(?P<ticks>`+)(?P<span>.+?)(?P=ticks)|[()]')
LINE_SUFFIX_RE = re.compile(r':\d+(?:-\d+)?$')


class CannotRun(Exception):
    '''The report cannot be produced; main() prints the reason and exits 2.'''


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ['git', '-C', str(root), *args], capture_output=True, encoding='utf-8', errors='replace', check=False,
    )


def git_out(root: Path, *args: str) -> str:
    done = git(root, *args)
    if done.returncode != 0:
        raise CannotRun(done.stderr.strip() or f'git {" ".join(args)} failed')
    return done.stdout


def nul_split(out: str) -> list[str]:
    '''The entries of a git listing run with -z, which prints each path as it is.
    Without -z, git C-quotes a path with unusual bytes (café comes out as a quoted
    octal escape), and the quoted form matches no name a plan writes.'''
    return [entry for entry in out.split('\0') if entry]


def repo_root(cwd: Path) -> Path:
    done = git(cwd, 'rev-parse', '--show-toplevel')
    if done.returncode != 0:
        raise CannotRun('not inside a git repository')
    return Path(done.stdout.strip())


@dataclass
class Plan:
    name: str
    locations: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Sighting:
    '''One copy of a file under specs/plans: a blob on a ref, or a file in a worktree.'''
    path: str
    where: str
    ref: str = ''
    blob: str = ''
    file: Path | None = None

    @property
    def name(self) -> str:
        return PurePosixPath(self.path).name


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


def plan_sightings(root: Path, refs: list[str], trees: list[Path]) -> list[Sighting]:
    '''Every file under specs/plans on every ref and in every worktree.'''
    seen = []
    for ref in refs:
        short = ref.removeprefix('refs/heads/').removeprefix('refs/remotes/')
        listing = git(root, 'ls-tree', '-r', '-z', ref, '--', 'specs/plans')
        for entry in nul_split(listing.stdout):
            meta, _, path = entry.partition('\t')
            seen.append(Sighting(path, short, ref=ref, blob=meta.split()[-1]))
    for tree in trees:
        plans = tree / 'specs' / 'plans'
        if plans.is_dir():
            seen.extend(
                Sighting(path.relative_to(tree).as_posix(), f'worktree {tree}', file=path)
                for path in sorted(plans.rglob('*.md'))
            )
    return seen


def plans_by_id(sightings: list[Sighting]) -> dict[int, list[Plan]]:
    by_id: dict[int, dict[str, Plan]] = {}
    for sighting in sightings:
        m = PLAN_RE.match(sighting.name)
        if not m:
            continue
        plan = by_id.setdefault(int(m['id']), {}).setdefault(sighting.name, Plan(sighting.name))
        if sighting.where not in plan.locations:
            plan.locations.append(sighting.where)
    return {pid: list(plans.values()) for pid, plans in by_id.items()}


def describe(plans: list[Plan]) -> str:
    return '; '.join(f'{p.name} ({", ".join(p.locations)})' for p in plans)


def names_spec(plan: Plan, stem: str) -> bool:
    # A trailing -spec is a filename convention, not part of the spec's name, so a
    # plan named before a spec gained the suffix still counts.
    name = PLAN_RE.match(plan.name)['name']
    return any(name == s or name.endswith(f'-{s}') for s in {stem, stem.removesuffix('-spec')})


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


def default_branch_refs(root: Path, refs: list[str]) -> set[str]:
    '''The refs of the default branch: the branch origin/HEAD names, else main or
    master, as a local branch and on origin.'''
    head = git(root, 'symbolic-ref', '-q', '--short', 'refs/remotes/origin/HEAD').stdout.strip()
    names = [head.removeprefix('origin/')] if head else ['main', 'master']
    wanted = {f'refs/{kind}/{name}' for name in names for kind in ('heads', 'remotes/origin')}
    return wanted.intersection(refs)


def live_plan_texts(root: Path, sightings: list[Sighting], trunk: set[str]) -> dict[str, set[str]]:
    '''The texts of each live plan's copies, by filename. A plan is retired once the
    default branch (trunk) has it under specs/plans/completed/: a plan retired on a
    branch not yet merged has edits the default branch lacks, and a merged planning
    branch keeps a live copy of a plan that the default branch has since retired.
    With no default branch, a copy under completed/ anywhere retires the plan.'''
    retired = {s.name for s in sightings if s.path.startswith(RETIRED) and (s.ref in trunk or not trunk)}
    texts: dict[str, set[str]] = {}
    blob_texts: dict[str, str] = {}
    for s in sightings:
        if s.name in retired or not PLAN_RE.match(s.name):
            continue
        copies = texts.setdefault(s.name, set())
        if s.file is None:
            if s.blob not in blob_texts:
                blob_texts[s.blob] = git_out(root, 'cat-file', 'blob', s.blob)
            copies.add(blob_texts[s.blob])
            continue
        with suppress(OSError):  # moved or removed since the scan, or a dangling link
            copies.add(s.file.read_text(encoding='utf-8', errors='replace'))
    return texts


def root_names(root: Path, refs: list[str], trees: list[Path]) -> set[str]:
    '''The names at the root of every ref and every worktree.'''
    names = set()
    for ref in refs:
        names.update(nul_split(git(root, 'ls-tree', '-z', '--name-only', ref).stdout))
    for tree in trees:
        with suppress(OSError):  # a worktree removed since git listed it
            names.update(path.name for path in tree.iterdir())
    return names


def unfenced_lines(text: str) -> list[str]:
    '''The lines outside fenced code. A backtick fence's info string holds no backtick,
    so a line that starts with an inline ```span``` opens nothing. A fence closes only
    on a bare run of its own character at least as long as the opening run, so a
    four-backtick block can hold three-backtick ones.'''
    lines, fence = [], ''
    for line in text.splitlines():
        m = FENCE_RE.match(line)
        if fence:
            if m and m['fence'][0] == fence[0] and len(m['fence']) >= len(fence) and not m['info'].strip():
                fence = ''
        elif m and not (m['fence'][0] == '`' and '`' in m['info']):
            fence = m['fence']
        else:
            lines.append(line)
    return lines


def spans_outside_parens(text: str) -> list[str]:
    '''The backticked spans in text that sit outside parentheses.'''
    spans, depth = [], 0
    for m in SPAN_OR_PAREN_RE.finditer(text):
        if m['span'] is not None:
            if depth == 0:
                spans.append(m['span'])
        elif m[0] == '(':
            depth += 1
        else:
            depth = max(depth - 1, 0)
    return spans


def repo_path(span: str, names_at_root: set[str]) -> str | None:
    '''The repo path a span names, or None. Its first component must be an entry at
    some tree's root: NOTICE and skills/x/SKILL.md name one; a bare SKILL.md, a
    scratch KIT/kit.py, /etc/hosts and ~/notes.md do not.'''
    path = LINE_SUFFIX_RE.sub('', span.strip()).removeprefix('./')
    if any(c.isspace() for c in path) or path.split('/', 1)[0] not in names_at_root:
        return None
    return path


def named_paths(text: str, names_at_root: set[str]) -> set[str]:
    '''The repo paths a plan names on its Files lines, Edit headers and extract markers.'''
    spans = []
    for line in unfenced_lines(text):
        if m := FILES_LINE_RE.match(line):
            spans += spans_outside_parens(m['rest'])
        elif m := EDIT_HEADER_RE.match(line):
            spans.append(m['span'])
        elif m := MARKER_RE.match(line):
            spans.append(m['key'].rsplit(':', 1)[0] if m['kind'] == 'edit' else m['key'])
    return {path for span in spans if (path := repo_path(span, names_at_root))}


def plan_order(name: str) -> tuple[bool, int, str]:
    '''By id, then filename; a --plan file whose name has no id comes last.'''
    m = PLAN_RE.match(name)
    return (m is None, int(m['id']) if m else 0, name)


def path_count(n: int) -> str:
    return f'{n} path' if n == 1 else f'{n} paths'


def format_overlaps(paths_by_plan: dict[str, set[str]]) -> list[str]:
    names = sorted(paths_by_plan, key=plan_order)
    counts = [f'{name} ({path_count(len(paths_by_plan[name]))})' for name in names]
    lines = ['overlapping files:', f'  live plans: {"; ".join(counts) if counts else "none"}']
    planned: dict[str, list[str]] = {}
    for name in names:
        for path in paths_by_plan[name]:
            planned.setdefault(path, []).append(name)
    shared = sorted(path for path, plans in planned.items() if len(plans) > 1)
    if shared:
        lines.append('  shared:')
        lines += [f'    {path}: {", ".join(planned[path])}' for path in shared]
    else:
        lines.append('  shared: none')
    return lines


def report(root: Path, spec: Path | None, plan: Path | None) -> list[str]:
    refs, trees = ref_names(root), worktree_paths(root)
    sightings = plan_sightings(root, refs, trees)
    texts = live_plan_texts(root, sightings, default_branch_refs(root, refs))
    if plan is not None:
        texts.setdefault(plan.name, set()).add(plan.read_text(encoding='utf-8', errors='replace'))
    names_at_root = root_names(root, refs, trees)
    paths = {
        name: set().union(*(named_paths(text, names_at_root) for text in copies))
        for name, copies in texts.items()
    }
    stem = spec.stem if spec is not None else None
    return format_plan_ids(plans_by_id(sightings), stem) + format_overlaps(paths)


def require_file(path: Path, kind: str) -> None:
    if path.is_dir():
        raise CannotRun(f'not a file: {path}')
    if not path.is_file():
        raise CannotRun(f'no such {kind}: {path}')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Report what a planning session checks before it plans a spec.')
    parser.add_argument('spec', nargs='?', type=Path, help='the spec about to be planned')
    parser.add_argument('--plan', type=Path, help='a plan saved outside specs/plans/, to compare with the live plans')
    args = parser.parse_args(argv)
    try:
        root = repo_root(Path.cwd())
        spec = None
        if args.spec is not None:
            require_file(args.spec, 'spec')
            try:
                spec = args.spec.resolve().relative_to(root.resolve())
            except ValueError:
                raise CannotRun(f'spec is outside this repository: {args.spec}') from None
        if args.plan is not None:
            require_file(args.plan, 'plan')
        print('\n'.join(report(root, spec, args.plan)))
    except CannotRun as e:
        print(f'entry_check: {e}', file=sys.stderr)
        return CANNOT_RUN
    return 0


if __name__ == '__main__':
    sys.exit(main())
