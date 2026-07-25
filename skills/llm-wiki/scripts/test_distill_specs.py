'''Tests for distill_specs.py. Stdlib + pytest only; git fixture repos in tmp.'''
import os
import subprocess

import pytest

import distill_specs as dsp

# Hermetic git: ignore the host's config so commits work on any machine.
GIT_ENV = dict(
  os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull,
  GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@t.invalid',
  GIT_COMMITTER_NAME='t', GIT_COMMITTER_EMAIL='t@t.invalid')


def _git(repo, *args):
  proc = subprocess.run(['git', '-C', str(repo), *args],
                        capture_output=True, text=True, env=GIT_ENV)
  assert proc.returncode == 0, proc.stderr
  return proc.stdout


def _sha(repo, ref='HEAD'):
  return _git(repo, 'rev-parse', '--short', ref).strip()


def make_repo(tmp_path):
  '''specs/ corpus with history: a spec committed live, edited, then retired
  via a pure `git mv` (the mechanical-commit fixture spec §9 requires), plus
  a completed plan and deferred_items.md.'''
  repo = tmp_path / 'repo'
  (repo / 'specs/plans/completed').mkdir(parents=True)
  (repo / 'specs/completed').mkdir(parents=True)
  _git(repo, 'init', '-q', '-b', 'main')
  spec = repo / 'specs/a-spec.md'
  spec.write_text('# A spec\n\n**Decision:** use X over Y.\n')
  _git(repo, 'add', '.')
  _git(repo, 'commit', '-qm', 'spec: a v1')
  spec.write_text('# A spec\n\n**Decision:** use X over Y.\n\nMore prose.\n')
  _git(repo, 'add', '.')
  _git(repo, 'commit', '-qm', 'spec: a v2')
  _git(repo, 'mv', 'specs/a-spec.md', 'specs/completed/a-spec.md')
  _git(repo, 'commit', '-qm', 'chore: retire spec')
  plan = repo / 'specs/plans/completed/1-a-spec.md'
  plan.write_text('# Plan\n\n**Status: COMPLETE (2026-01-01)** — done\n\n'
                  '> Deviation: step 3 skipped\n')
  (repo / 'specs/deferred_items.md').write_text(
    '# Deferred items\n\n- [ ] later thing\n')
  _git(repo, 'add', '.')
  _git(repo, 'commit', '-qm', 'plan: complete')
  return repo


def make_root(tmp_path):
  '''Minimal wiki root: SCHEMA.md marks it as a real root (wrong-wiki guard).'''
  root = tmp_path / 'wiki'
  for d in ('reports', 'raw/specs', 'wiki/sources'):
    (root / d).mkdir(parents=True)
  (root / 'SCHEMA.md').write_text('# SCHEMA\n')
  return root


def inventory(repo, root, date='2026-07-24', only=None):
  argv = ['inventory', str(repo), '--root', str(root), '--date', date]
  if only:
    argv += ['--only', only]
  return dsp.main(argv)


# --- Task 1: CLI, walk, hard errors, brief creation --------------------------

def test_no_subcommand_exits_nonzero(tmp_path):
  with pytest.raises(SystemExit) as exc:
    dsp.main([])
  assert exc.value.code != 0


def test_root_is_required(tmp_path):
  with pytest.raises(SystemExit) as exc:
    dsp.main(['inventory', str(tmp_path)])
  assert exc.value.code != 0


def test_non_wiki_root_is_hard_error(tmp_path, capsys):
  repo = make_repo(tmp_path)
  bare = tmp_path / 'not-a-wiki'
  bare.mkdir()
  assert inventory(repo, bare) == 1
  assert 'SCHEMA.md' in capsys.readouterr().err


def test_no_specs_dir_is_hard_error(tmp_path, capsys):
  root = make_root(tmp_path)
  repo = tmp_path / 'empty-repo'
  repo.mkdir()
  _git(repo, 'init', '-q', '-b', 'main')
  assert inventory(repo, root) == 1
  assert 'no specs/' in capsys.readouterr().err


def test_no_git_history_is_hard_error(tmp_path, capsys):
  root = make_root(tmp_path)
  repo = tmp_path / 'gitless'
  (repo / 'specs').mkdir(parents=True)
  assert inventory(repo, root) == 1
  err = capsys.readouterr().err
  assert 'git history' in err and 'load-bearing' in err


def test_inventory_writes_brief_with_header_and_sections(tmp_path):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  assert inventory(repo, root) == 0
  brief = root / 'reports/harvest-repo-2026-07-24.md'
  text = brief.read_text()
  assert text.startswith('---\nharvest: specs\nrepo: repo\n')
  assert f'repo_head: {_sha(repo)}' in text
  assert f'root: {root.resolve()}' in text
  assert 'date: 2026-07-24' in text
  assert 'prior_brief: none' in text
  # settled strata first, deferred last (spec §7)
  a = text.index('## specs/completed/a-spec.md')
  b = text.index('## specs/plans/completed/1-a-spec.md')
  c = text.index('## specs/deferred_items.md')
  assert a < b < c
  assert 'captures:' in text


def test_missing_dirs_get_notes_not_errors(tmp_path):
  root = make_root(tmp_path)
  repo = tmp_path / 'partial'
  (repo / 'specs').mkdir(parents=True)
  (repo / 'specs/only.md').write_text('# Only\n')
  _git(repo, 'init', '-q', '-b', 'main')
  _git(repo, 'add', '.')
  _git(repo, 'commit', '-qm', 'one file')
  assert inventory(repo, root, date='2026-07-25') == 0
  text = (root / 'reports/harvest-partial-2026-07-25.md').read_text()
  assert 'note: specs/completed/: absent' in text
  assert 'note: specs/plans/: absent' in text
  assert 'note: specs/plans/completed/: absent' in text
  assert 'note: specs/deferred_items.md: absent' in text
  assert '## specs/only.md' in text


def test_empty_walk_is_hard_error(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  assert inventory(repo, root, only='nomatch/*') == 1
  assert 'nothing to walk' in capsys.readouterr().err


# --- Review-finding regression tests ----------------------------------------

def test_non_ascii_repo_name_uses_raw_dir_name_not_session_fallback(tmp_path):
  '''slugify() never returns falsy (it falls back to the literal 'session'),
  so `slugify(repo.name) or repo.name` can never engage its fallback branch.
  A repo dir with no ASCII words (e.g. a CJK name) must not silently become
  "harvest-session-<date>.md" — it should keep the raw dir name.'''
  root = make_root(tmp_path)
  repo = tmp_path / '日本語'
  (repo / 'specs').mkdir(parents=True)
  (repo / 'specs/only.md').write_text('# Only\n')
  _git(repo, 'init', '-q', '-b', 'main')
  _git(repo, 'add', '.')
  _git(repo, 'commit', '-qm', 'one file')
  assert inventory(repo, root) == 0
  brief = root / 'reports/harvest-日本語-2026-07-24.md'
  assert brief.is_file(), 'brief should be named from the raw dir name'
  assert not (root / 'reports/harvest-session-2026-07-24.md').is_file()
  assert 'repo: 日本語' in brief.read_text()


def test_subdir_of_parent_repo_is_hard_error(tmp_path, capsys):
  '''`git -C repo rev-parse HEAD` walks up to an ancestor .git, so a plain
  (non-repo) subdirectory of some outer git repo would otherwise pass the
  git-history guard and silently record the *parent's* HEAD. Spec §7: no
  git history of its own -> hard error, since landing SHAs are load-bearing.'''
  root = make_root(tmp_path)
  outer = tmp_path / 'outer'
  outer.mkdir()
  _git(outer, 'init', '-q', '-b', 'main')
  (outer / 'README.md').write_text('# outer\n')
  _git(outer, 'add', '.')
  _git(outer, 'commit', '-qm', 'outer init')
  repo = outer / 'nested'  # specs/-bearing, but not its own git checkout
  (repo / 'specs').mkdir(parents=True)
  (repo / 'specs/only.md').write_text('# Only\n')
  assert inventory(repo, root) == 1
  err = capsys.readouterr().err
  assert 'git history' in err and 'load-bearing' in err


def test_present_but_empty_dir_gets_no_md_files_note(tmp_path):
  '''walk_specs distinguishes an absent dir from one that exists but holds no
  .md files; only the absent-dir note text was previously asserted.'''
  root = make_root(tmp_path)
  repo = tmp_path / 'emptydir'
  (repo / 'specs/completed').mkdir(parents=True)
  (repo / 'specs/only.md').write_text('# Only\n')
  _git(repo, 'init', '-q', '-b', 'main')
  _git(repo, 'add', '.')
  _git(repo, 'commit', '-qm', 'one file, empty completed dir')
  assert inventory(repo, root) == 0
  text = (root / 'reports/harvest-emptydir-2026-07-24.md').read_text()
  assert 'note: specs/completed/: no .md files' in text


def test_linked_worktree_is_accepted(tmp_path):
  '''A `git worktree add` checkout has no .git *directory* of its own (just a
  .git *file* pointing at the main checkout's gitdir), but
  `rev-parse --show-toplevel` still reports the worktree's own root, not the
  main checkout's. Pin that the new own-toplevel guard (finding 2) doesn't
  reject this real workflow (this task itself runs inside such a worktree).'''
  main = make_repo(tmp_path)
  wt = tmp_path / 'wt'
  _git(main, 'worktree', 'add', '--detach', '-q', str(wt), 'HEAD')
  root = make_root(tmp_path)
  assert inventory(wt, root) == 0
  assert (root / f'reports/harvest-wt-2026-07-24.md').is_file()


def test_yaml_hostile_repo_name_is_sanitized(tmp_path):
  '''A repo dir name that slugifies to nothing and starts with a YAML-special
  character must not be embedded raw as `repo: {name}` in the brief's
  frontmatter — a leading '#' turns the rest of the line into a comment
  (silently discarding the value); a leading '-' reads as a list marker.'''
  root = make_root(tmp_path)
  repo = tmp_path / '#日本語'
  (repo / 'specs').mkdir(parents=True)
  (repo / 'specs/only.md').write_text('# Only\n')
  _git(repo, 'init', '-q', '-b', 'main')
  _git(repo, 'add', '.')
  _git(repo, 'commit', '-qm', 'one file')
  assert inventory(repo, root) == 0
  brief = root / 'reports/harvest-日本語-2026-07-24.md'
  assert brief.is_file()
  assert 'repo: 日本語\n' in brief.read_text()


def test_punctuation_only_repo_name_falls_back_to_session(tmp_path):
  '''A repo dir name that is purely YAML-special punctuation sanitizes to
  nothing; falling all the way back to 'session' is safer than embedding an
  empty or corrupt value in the brief header.'''
  root = make_root(tmp_path)
  repo = tmp_path / '---'
  (repo / 'specs').mkdir(parents=True)
  (repo / 'specs/only.md').write_text('# Only\n')
  _git(repo, 'init', '-q', '-b', 'main')
  _git(repo, 'add', '.')
  _git(repo, 'commit', '-qm', 'one file')
  assert inventory(repo, root) == 0
  brief = root / 'reports/harvest-session-2026-07-24.md'
  assert brief.is_file()
  assert 'repo: session\n' in brief.read_text()


# --- Task 2: seed grep -------------------------------------------------------

SEED_DOC = '''# Doc

**Decision:** Delta Lake over plain Parquet.

Delta merge/upsert was rejected for idempotent re-runs.

## 10. Alternatives considered (recorded)

## 1. TL;DR

## Global Constraints

**Status: COMPLETE (2026-07-04)** — executed

> Deviation: retry moved to Task 9

- [ ] Redis-backed counter store (deferred)
'''


def test_seed_hits_every_pattern_class():
  # deferred-item only fires for deferred_items.md text (finding 1, spec §5.1)
  labels = {label for _, label, _ in dsp.seed_hits(SEED_DOC, is_deferred=True)}
  assert labels == {'decision', 'rejected', 'recorded', 'tldr', 'policy',
                    'completion', 'deviation', 'deferred-item'}


def test_seed_hits_carry_line_numbers_and_text():
  hits = dsp.seed_hits(SEED_DOC)
  assert (3, 'decision', '**Decision:** Delta Lake over plain Parquet.') in hits


def test_seed_lines_are_redacted():
  doc = '**Decision:** use key sk-' + 'A' * 24 + ' for auth.\n'
  hits = dsp.seed_hits(doc)
  assert hits and 'sk-' + 'A' * 24 not in hits[0][2]
  assert '[REDACTED:openai-key]' in hits[0][2]


def test_brief_contains_seed_hits_or_none_marker(tmp_path):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  assert inventory(repo, root) == 0
  text = (root / 'reports/harvest-repo-2026-07-24.md').read_text()
  assert 'decision: **Decision:** use X over Y.' in text
  assert 'completion: **Status: COMPLETE (2026-01-01)**' in text


def test_seeds_section_renders_none_marker_when_no_hits(tmp_path):
  '''render_file_section's "- none" branch (finding 2): a walked file with
  zero seed-pattern matches must render `seeds:\n- none`, not an empty list
  or no section at all.'''
  root = make_root(tmp_path)
  repo = tmp_path / 'quiet-repo'
  (repo / 'specs').mkdir(parents=True)
  (repo / 'specs/only.md').write_text('# Only\n\nJust some plain prose.\n')
  _git(repo, 'init', '-q', '-b', 'main')
  _git(repo, 'add', '.')
  _git(repo, 'commit', '-qm', 'quiet file, no seed hits')
  assert inventory(repo, root) == 0
  text = (root / 'reports/harvest-quiet-repo-2026-07-24.md').read_text()
  section = text[text.index('## specs/only.md'):]
  assert 'seeds:\n- none' in section


def test_deferred_item_pattern_ignored_outside_deferred_file():
  '''spec §5.1: deferred-item means deferred_items.md entries, not any
  markdown checkbox -- plan files carry dozens of step-tracking checkboxes
  that would otherwise drown the signal (finding 1).'''
  text = '# Plan\n\n- [ ] step one\n- [x] step two\n'
  labels = {label for _, label, _ in dsp.seed_hits(text)}
  assert 'deferred-item' not in labels


def test_deferred_item_pattern_applies_in_deferred_file():
  text = '# Deferred items\n\n- [ ] later thing\n'
  labels = {label for _, label, _ in dsp.seed_hits(text, is_deferred=True)}
  assert 'deferred-item' in labels


def test_deferred_item_restricted_to_deferred_file_end_to_end(tmp_path):
  '''cmd_inventory wiring: a checkbox line in a plan file must not surface as
  deferred-item, but the same line shape in deferred_items.md must (finding
  1) -- the seed_hits unit tests alone don't pin the per-file wiring.'''
  root = make_root(tmp_path)
  repo = tmp_path / 'checkbox-repo'
  (repo / 'specs/plans/completed').mkdir(parents=True)
  (repo / 'specs/plans/completed/1-plan.md').write_text(
    '# Plan\n\n- [x] step one\n- [ ] step two\n')
  (repo / 'specs/deferred_items.md').write_text(
    '# Deferred items\n\n- [ ] later thing\n')
  _git(repo, 'init', '-q', '-b', 'main')
  _git(repo, 'add', '.')
  _git(repo, 'commit', '-qm', 'checkbox fixture')
  assert inventory(repo, root) == 0
  text = (root / 'reports/harvest-checkbox-repo-2026-07-24.md').read_text()
  plan_start = text.index('## specs/plans/completed/1-plan.md')
  deferred_start = text.index('## specs/deferred_items.md')
  plan_section = text[plan_start:deferred_start]
  deferred_section = text[deferred_start:]
  assert 'deferred-item' not in plan_section
  assert 'deferred-item' in deferred_section


# --- Task 3: SHA tables ------------------------------------------------------

def test_sha_table_follows_rename_and_classifies(tmp_path):
  repo = make_repo(tmp_path)
  rows = dsp.sha_table(repo, 'specs/completed/a-spec.md')
  # newest first: retirement (pure git mv), v2 edit, v1 creation
  assert [cls for _, _, cls in rows] == \
    ['mechanical', 'substantive', 'substantive']
  assert rows[0][1] == 'chore: retire spec'
  assert rows[2][1] == 'spec: a v1'


def test_rename_with_edit_is_substantive(tmp_path):
  repo = make_repo(tmp_path)
  moved = repo / 'specs/plans/completed/1-a-spec.md'
  target = repo / 'specs/plans/completed/01-a-spec.md'
  target.write_text(moved.read_text() + '\nEdited during move.\n')
  moved.unlink()
  _git(repo, 'add', '-A')
  _git(repo, 'commit', '-qm', 'chore: renumber plan with edits')
  rows = dsp.sha_table(repo, 'specs/plans/completed/01-a-spec.md')
  assert rows[0][2] == 'substantive'


def test_brief_contains_sha_table(tmp_path):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  assert inventory(repo, root) == 0
  text = (root / 'reports/harvest-repo-2026-07-24.md').read_text()
  assert ' · chore: retire spec · mechanical' in text
  assert ' · spec: a v2 · substantive' in text
