'''Scaffold or refresh a research-wiki root and install its runtime scripts.

Creates the wiki skeleton (the directories and structural files lint_wiki.py
requires), seeds SCHEMA.md from this skill's template, and installs the three
runtime scripts (lint_wiki.py, distill_sessions.py, distill_specs.py) into
<root>/scripts/. It is idempotent and never overwrites or deletes wiki content:
only skill-owned code is ever refreshed, and only with --force; SCHEMA.md is
seeded once and is never overwritten. The root is a required argument with no
default, so a wiki is only ever written where you name it -- personal and work
wikis stay separate roots whose content never mixes.

Usage:
  python3 bootstrap_wiki.py <root>                  # scaffold / top up a wiki
  python3 bootstrap_wiki.py <root> --dry-run        # print the plan, write nothing
  python3 bootstrap_wiki.py <root> --check          # report tooling drift, write nothing
  python3 bootstrap_wiki.py <root> --force          # also refresh divergent scripts
  python3 bootstrap_wiki.py <root> --topic samplers # also create raw/ + wiki/ topic dirs

Examples:
  python3 ~/.claude/skills/llm-wiki/scripts/bootstrap_wiki.py ~/research-wiki
  python3 ~/.claude/skills/llm-wiki/scripts/bootstrap_wiki.py /work/wiki --topic nowcasting

Exit codes: 0 = scaffolded and verified (or dry-run / check-current);
1 = refused before writing (bad args, incomplete bundle, or --check found
missing/stale tooling); 2 = post-write verification failed.
'''
import argparse
import filecmp
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

BUNDLE = Path(__file__).resolve().parent

# The schema is a seed-once, per-root customizable contract, so a byte-diff
# cannot tell a legitimately customized SCHEMA.md apart from one left behind by
# a coupled linter+schema change. The bundle template carries an integer
# version marker; --check compares versions, not bytes, so customization is
# silent but a root whose contract is behind the bundle is flagged.
_SCHEMA_VERSION_RE = re.compile(r'schema-version:\s*(\d+)')

# Runtime scripts installed into <root>/scripts/. A closed allowlist, never a
# glob: a glob would drag bootstrap_wiki.py and the test files into the wiki
# root. These are the only files ever overwritten, and only under --force.
MANAGED_SCRIPTS = ('lint_wiki.py', 'distill_sessions.py', 'distill_specs.py')
SCHEMA_TEMPLATE = 'schema-template.md'

# Load-bearing directories lint_wiki.py hardcodes: wiki/, wiki/sources/, raw/,
# raw/sessions/, raw/specs/, the special-cased assets dir, reports/, scripts/.
WIKI_DIRS = (
  'raw', 'raw/assets', 'raw/sessions', 'raw/specs', 'reports', 'scripts',
  'wiki', 'wiki/sources',
)
# Empty leaf dirs need a 0-byte .gitkeep so git carries them; wiki/ is held by
# its structural files and scripts/ by the three installed scripts.
GITKEEP_DIRS = (
  'raw/assets', 'raw/sessions', 'raw/specs', 'reports', 'wiki/sources',
)

# The concrete set self-verification asserts on disk before it trusts a lint.
REQUIRED_DIRS = (
  'raw', 'raw/assets', 'raw/sessions', 'raw/specs', 'reports', 'scripts',
  'wiki', 'wiki/sources',
)
REQUIRED_FILES = (
  'wiki/index.md', 'wiki/log.md', 'wiki/open-questions.md', 'SCHEMA.md',
  'scripts/lint_wiki.py', 'scripts/distill_sessions.py',
  'scripts/distill_specs.py',
)

# Structural + infra seeds, byte-for-byte from the reference wiki except: the
# personal `## samplers` / `## nowcasting` topic headings are dropped from the
# index, and the word 'Personal' is dropped from the README lead. § is the
# section sign; written as UTF-8 to match the reference bytes exactly.
SEED_FILES = {
  'wiki/index.md':
    '# Wiki index\n\nOne line per page, grouped by topic. '
    'See SCHEMA.md §index.\n',
  'wiki/log.md':
    '# Operation log\n\nAppend-only. Grammar: '
    '`## [YYYY-MM-DD] <op> | <subject> | <note>`. See SCHEMA.md §log.\n',
  'wiki/open-questions.md':
    '# Open questions\n\nContradictions and gaps awaiting resolution. '
    'See SCHEMA.md §contradictions.\n',
  'README.md':
    '# research-wiki\n\n'
    'Research wiki (Karpathy LLM-wiki pattern). `raw/` is immutable source\n'
    'material (human-curated); `wiki/` is agent-compiled knowledge; '
    '`SCHEMA.md` is\n'
    'the normative contract the `llm-wiki` skill and `scripts/lint_wiki.py` '
    'enforce.\n'
    'Resolve the root via `$LLM_WIKI_ROOT` (default `~/research-wiki`).\n',
  '.gitignore':
    '__pycache__/\n*.pyc\n.DS_Store\n.pytest_cache/\n',
}


def _require_bundle():
  '''True if every file the bootstrap installs from is present beside it.'''
  missing = [n for n in (*MANAGED_SCRIPTS, SCHEMA_TEMPLATE)
             if not (BUNDLE / n).exists()]
  if missing:
    print(f'error: bundle is incomplete, missing {missing} in {BUNDLE}',
          file=sys.stderr)
    return False
  return True


def _schema_version(path):
  '''Integer from the `<!-- schema-version: N -->` marker; None if absent or
  unreadable. None on either side means "cannot compare" -> not treated as
  stale, so a marker-less (pre-versioning or hand-written) schema is never
  falsely flagged.'''
  try:
    text = path.read_text(encoding='utf-8')
  except OSError:
    return None
  m = _SCHEMA_VERSION_RE.search(text)
  return int(m.group(1)) if m else None


def _safe_copy(src, dst):
  '''Copy src -> dst as a regular file INSIDE the root. A dst that is a symlink
  is unlinked first: shutil.copyfile would otherwise follow it and write through
  to whatever it points at -- the one way this program could clobber a file
  outside the root. Unlinking replaces the link in place with a real file.'''
  if dst.is_symlink():
    dst.unlink()
  shutil.copyfile(src, dst)


def _write_if_absent(dst, content, args):
  '''Seed a file only when it is absent. Existing files are never rewritten. A
  symlink at the target is treated as present and left untouched -- writing
  through it could land the seed outside the root.'''
  if dst.exists() or dst.is_symlink():
    return 'exists'
  if not args.dry_run:
    dst.write_text(content, encoding='utf-8')
  return 'create'


def _install_script(name, root, args):
  '''Managed code: create if absent; refresh a divergent copy only with --force.

  A managed-script path that is a symlink is never a copy this bootstrap made,
  so it is treated as divergent -- DIFFERS on a plain run, replaced in place
  under --force -- and is never read or written *through* (see _safe_copy). This
  closes the only vector that could clobber a file outside the root.'''
  src = BUNDLE / name
  dst = root / 'scripts' / name
  if dst.is_symlink():
    if args.force:
      if not args.dry_run:
        _safe_copy(src, dst)
      return 'update'
    return 'DIFFERS'
  if not dst.exists():
    if not args.dry_run:
      _safe_copy(src, dst)
    return 'create'
  if filecmp.cmp(src, dst, shallow=False):
    return 'same'
  if args.force:
    if not args.dry_run:
      _safe_copy(src, dst)
    return 'update'
  return 'DIFFERS'


def _install_schema(root, args):
  '''Seed-once contract: create if absent; never overwritten, even with --force.

  When an existing schema differs from the bundle template, distinguish a root
  whose contract is *behind* the bundle (STALE -- a coupled update shipped a
  newer contract) from ordinary local customization (DIFFERS), by comparing the
  version markers. STALE is advisory here; --check is what carries the exit
  code.'''
  src = BUNDLE / SCHEMA_TEMPLATE
  dst = root / 'SCHEMA.md'
  if not dst.exists():
    if not args.dry_run:
      _safe_copy(src, dst)
    return 'create'
  if filecmp.cmp(src, dst, shallow=False):
    return 'same'
  bundle_v = _schema_version(src)
  root_v = _schema_version(dst)
  if bundle_v is not None and root_v is not None and root_v < bundle_v:
    return 'STALE'
  return 'DIFFERS'


def _scaffold(root, args):
  '''Create dirs and seed files, returning (kind, path, status) actions.'''
  topics = args.topic or []
  actions = []

  dirs = list(WIKI_DIRS)
  for t in topics:
    dirs += [f'raw/{t}', f'wiki/{t}']
  for d in dirs:
    p = root / d
    status = 'exists' if p.is_dir() else 'create'
    if not args.dry_run:
      p.mkdir(parents=True, exist_ok=True)
    actions.append(('dir', d, status))

  keep_dirs = list(GITKEEP_DIRS)
  for t in topics:
    keep_dirs += [f'raw/{t}', f'wiki/{t}']
  for d in keep_dirs:
    dst = root / d / '.gitkeep'
    actions.append(('gitkeep', f'{d}/.gitkeep', _write_if_absent(dst, '', args)))

  for rel, content in SEED_FILES.items():
    actions.append(('seed', rel, _write_if_absent(root / rel, content, args)))

  actions.append(('schema', 'SCHEMA.md', _install_schema(root, args)))
  for name in MANAGED_SCRIPTS:
    actions.append(('script', f'scripts/{name}', _install_script(name, root, args)))
  return actions


def _print_actions(actions):
  for kind, path, status in actions:
    hint = ''
    if status == 'DIFFERS' and kind == 'script':
      hint = '  (run with --force to refresh)'
    elif status == 'DIFFERS' and kind == 'schema':
      hint = '  (seed-once: reconcile by hand; the root copy governs)'
    elif status == 'STALE' and kind == 'schema':
      hint = ('  (contract is behind the bundle; reconcile by hand against '
              'the template)')
    print(f'  {status:<8}{path}{hint}')


def _run_check(root):
  '''Read-only: is the installed tooling current with the skill bundle?

  Managed-code drift or absence, and a missing SCHEMA.md (an un-bootstrapped
  root), return 1. A SCHEMA.md whose version marker is *behind* the bundle
  (STALE -- a coupled update shipped a newer contract) also returns 1. A schema
  that merely DIFFERS at the same (or an absent/unparseable) version is reported
  but not counted: it is seed-once, so each root legitimately owns its schema.
  '''
  print('check: comparing installed tooling against the skill bundle')
  drift = 0

  schema = root / 'SCHEMA.md'
  if not schema.exists():
    print('  MISSING   SCHEMA.md  (root is not bootstrapped)')
    drift += 1
  elif filecmp.cmp(BUNDLE / SCHEMA_TEMPLATE, schema, shallow=False):
    print('  current   SCHEMA.md')
  else:
    bundle_v = _schema_version(BUNDLE / SCHEMA_TEMPLATE)
    root_v = _schema_version(schema)
    if bundle_v is not None and root_v is not None and root_v < bundle_v:
      print(f'  STALE     SCHEMA.md  (contract v{root_v} is behind bundle '
            f'v{bundle_v}; reconcile by hand against the template)')
      drift += 1
    else:
      print('  DIFFERS   SCHEMA.md  (seed-once; local customization is allowed)')

  for name in MANAGED_SCRIPTS:
    dst = root / 'scripts' / name
    if not dst.exists():
      print(f'  MISSING   scripts/{name}')
      drift += 1
    elif filecmp.cmp(BUNDLE / name, dst, shallow=False):
      print(f'  current   scripts/{name}')
    else:
      print(f'  DIFFERS   scripts/{name}  (run with --force to refresh)')
      drift += 1

  if drift:
    print(f'check: {drift} item(s) missing or stale')
    return 1
  print('check: tooling is current')
  return 0


def _verify(root):
  '''Post-write proof: the concrete path set exists AND the installed linter
  runs clean. Lint alone is insufficient -- it globs wiki/*/*.md and exits 0 on
  missing dirs, so a half-created scaffold would lint clean.'''
  missing = [d for d in REQUIRED_DIRS if not (root / d).is_dir()]
  missing += [f for f in REQUIRED_FILES if not (root / f).is_file()]
  if missing:
    print(f'verify: scaffold incomplete, missing {missing}', file=sys.stderr)
    return 2
  lint = root / 'scripts' / 'lint_wiki.py'
  proc = subprocess.run([sys.executable, str(lint), str(root)],
                        capture_output=True, text=True)
  sys.stdout.write(proc.stdout)
  if proc.returncode != 0:
    sys.stderr.write(proc.stderr)
    print('verify: the installed lint reported problems. On a fresh scaffold '
          'this is a bug; over an existing wiki it means content errors, not a '
          'bootstrap failure.', file=sys.stderr)
    return 2
  return 0


def _env_note(root):
  env = os.environ.get('LLM_WIKI_ROOT')
  if env is None:
    print('note: $LLM_WIKI_ROOT is unset; lint_wiki.py falls back to '
          '~/research-wiki when it is unset -- set it to this root (below).')
  elif Path(env).expanduser().resolve() != root:
    print(f'WARN: $LLM_WIKI_ROOT ({Path(env).expanduser().resolve()}) differs '
          f'from the target root; make sure you mean to bootstrap {root}.')


def _version_note():
  if sys.version_info < (3, 12):
    print(f'WARN: bootstrap is running under Python {sys.version_info.major}.'
          f'{sys.version_info.minor} ({sys.executable}); the installed wiki '
          f'scripts target Python >= 3.12 -- run lint_wiki.py / '
          f'distill_sessions.py / distill_specs.py with a 3.12+ interpreter.')


def _footer(root):
  print()
  print('next steps:')
  print(f'  export LLM_WIKI_ROOT={root}')
  print(f'  python3 {root}/scripts/lint_wiki.py')


def _parse_args(argv):
  ap = argparse.ArgumentParser(
    description='Scaffold or refresh a research-wiki root.')
  ap.add_argument('root',
                  help='wiki root (required; no default -- name it explicitly)')
  ap.add_argument('--force', action='store_true',
                  help='refresh installed scripts that differ from the bundle '
                       '(never touches SCHEMA.md or wiki content)')
  ap.add_argument('--check', action='store_true',
                  help='report whether installed tooling matches the bundle; '
                       'write nothing')
  ap.add_argument('--dry-run', action='store_true',
                  help='print the plan without writing anything')
  ap.add_argument('--topic', action='append', metavar='NAME',
                  help='also create raw/<NAME>/ and wiki/<NAME>/ (repeatable)')
  args = ap.parse_args(argv)
  if args.check and (args.force or args.dry_run or args.topic):
    ap.error('--check is read-only; do not combine it with '
             '--force / --dry-run / --topic')
  return args


def main(argv=None):
  args = _parse_args(argv)
  root = Path(args.root).expanduser().resolve()
  print(f'wiki root: {root}')
  if root.exists() and not root.is_dir():
    print(f'error: {root} exists and is not a directory', file=sys.stderr)
    return 1
  _env_note(root)
  _version_note()
  if not _require_bundle():
    return 1

  if args.check:
    return _run_check(root)

  actions = _scaffold(root, args)
  _print_actions(actions)
  _footer(root)
  if args.dry_run:
    print('dry-run: nothing was written')
    return 0
  return _verify(root)


if __name__ == '__main__':
  sys.exit(main())
