'''Tests for distill_specs.py. Stdlib + pytest only; git fixture repos in tmp.'''
import hashlib
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


# --- Task 4: prior briefs, accretion, --only ---------------------------------

PRIOR_BRIEF = '''---
harvest: specs
repo: repo
repo_path: /old/path
repo_head: 0000000
root: /old/root
date: 2026-07-01
prior_brief: none
files_walked: >
  specs/completed/a-spec.md
---

## specs/completed/a-spec.md

captures:

- [x] [d-01] Kept decision
  kind: decision · boundary: transferable
  at: specs/completed/a-spec.md §1 · sha: 1111111
  excerpt: "kept"
  claim: This one was approved.
- [ ] [g-01] Declined gotcha
  kind: gotcha · boundary: transferable
  at: specs/completed/a-spec.md §2 · sha: 1111111
  excerpt: "declined"
  claim: This one was declined.
'''


def test_seen_keys_include_ticked_and_unticked(tmp_path):
  b = tmp_path / 'harvest-repo-2026-07-01.md'
  b.write_text(PRIOR_BRIEF)
  seen = dsp.seen_keys_by_file([b])
  keys = seen['specs/completed/a-spec.md']
  assert len(keys) == 2  # declined entries dedup too (spec §5.1)
  assert any(k.startswith('d-01 · specs/completed/a-spec.md §1 · ') for k in keys)
  assert any(k.startswith('g-01 · specs/completed/a-spec.md §2 · ') for k in keys)


def test_claim_hash_is_whitespace_normalized():
  assert dsp.claim_hash('a  b\n c') == dsp.claim_hash('a b c')
  assert len(dsp.claim_hash('x')) == 8


def test_inventory_lists_previously_seen_and_prior_pointer(tmp_path):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  (root / 'reports/harvest-repo-2026-07-01.md').write_text(PRIOR_BRIEF)
  assert inventory(repo, root) == 0
  text = (root / 'reports/harvest-repo-2026-07-24.md').read_text()
  assert 'prior_brief: reports/harvest-repo-2026-07-01.md' in text
  assert '- d-01 · specs/completed/a-spec.md §1 · ' in text
  assert '- g-01 · specs/completed/a-spec.md §2 · ' in text


def test_same_date_rerun_appends_only_new_sections(tmp_path):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  assert inventory(repo, root, only='specs/completed/*') == 0
  brief = root / 'reports/harvest-repo-2026-07-24.md'
  first = brief.read_text()
  assert '## specs/completed/a-spec.md' in first
  assert '## specs/plans/completed/1-a-spec.md' not in first
  # sentinel: hand-added capture entry must survive the re-run untouched
  brief.write_text(first + '- [x] [d-01] Hand-added\n')
  assert inventory(repo, root) == 0
  text = brief.read_text()
  assert text.count('## specs/completed/a-spec.md') == 1  # never duplicated
  assert '## specs/plans/completed/1-a-spec.md' in text   # appended
  assert '- [x] [d-01] Hand-added' in text                # never overwritten
  assert 'specs/deferred_items.md' in text.split('---')[1]  # files_walked union


def test_extend_brief_applies_deferred_item_seed_flag(tmp_path):
  '''_extend_brief's per-file render loop must gate seed_hits by is_deferred
  the same way cmd_inventory's first pass does (spec §5.1) -- otherwise
  deferred_items.md entering the brief only via the same-date extend path
  (e.g. an --only-scoped run followed by a full re-run) renders "- none" for
  seeds instead of its deferred-item hits.'''
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  assert inventory(repo, root, only='specs/completed/*') == 0
  brief = root / 'reports/harvest-repo-2026-07-24.md'
  assert 'specs/deferred_items.md' not in brief.read_text()
  assert inventory(repo, root) == 0
  text = brief.read_text()
  deferred_section = text[text.index('## specs/deferred_items.md'):]
  assert 'deferred-item:' in deferred_section
  assert 'seeds:\n- none' not in deferred_section


def test_same_date_rerun_with_moved_head_is_error(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  assert inventory(repo, root, only='specs/completed/*') == 0
  (repo / 'specs/new.md').write_text('# New\n')
  _git(repo, 'add', '.')
  _git(repo, 'commit', '-qm', 'spec: new')
  assert inventory(repo, root) == 1
  assert 'repo_head' in capsys.readouterr().err


def test_same_date_rerun_with_no_new_files_is_noop(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  assert inventory(repo, root) == 0
  before = (root / 'reports/harvest-repo-2026-07-24.md').read_text()
  assert inventory(repo, root) == 0
  assert (root / 'reports/harvest-repo-2026-07-24.md').read_text() == before
  assert 'no new files' in capsys.readouterr().out


def test_only_glob_filters_walk(tmp_path):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  assert inventory(repo, root, only='specs/plans/completed/*') == 0
  text = (root / 'reports/harvest-repo-2026-07-24.md').read_text()
  assert '## specs/plans/completed/1-a-spec.md' in text
  assert '## specs/completed/a-spec.md' not in text


WRONG_REPO_PRIOR_BRIEF = '''---
harvest: specs
repo: wiki-tools
repo_path: /old/path
repo_head: 0000000
root: /old/root
date: 2026-07-01
prior_brief: none
files_walked: >
  specs/only.md
---

## specs/only.md

captures:

- [x] [d-01] Wrong-repo decision
  kind: decision · boundary: transferable
  at: specs/only.md §1 · sha: 1111111
  excerpt: "wrong repo"
  claim: This belongs to wiki-tools, not wiki.
'''


def test_prior_briefs_does_not_match_prefix_repo_name(tmp_path):
  '''glob(f'harvest-{repo_name}-*.md') is an unanchored prefix match: in a
  shared multi-repo wiki root, repo "wiki" would otherwise pick up another
  repo's brief "harvest-wiki-tools-2026-07-01.md" as a prior (spec §4.1/§7
  wrong-wiki protection) -- leaking wrong-repo dedup keys into `seen` and
  pointing `prior_brief:` at the wrong repo's brief.'''
  root = make_root(tmp_path)
  repo = tmp_path / 'wiki'
  (repo / 'specs').mkdir(parents=True)
  (repo / 'specs/only.md').write_text('# Only\n')
  _git(repo, 'init', '-q', '-b', 'main')
  _git(repo, 'add', '.')
  _git(repo, 'commit', '-qm', 'one file')
  (root / 'reports/harvest-wiki-tools-2026-07-01.md').write_text(
    WRONG_REPO_PRIOR_BRIEF)
  assert inventory(repo, root) == 0
  text = (root / 'reports/harvest-wiki-2026-07-24.md').read_text()
  assert 'prior_brief: none' in text
  assert '- d-01 · specs/only.md §1 · ' not in text
  assert 'previously seen:\n- none' in text


# --- Task 5: parser + validation ---------------------------------------------

def _entry(ticked='x', eid='d-01', title='T', kind='decision',
           boundary='transferable', at='specs/a.md §1', sha='1234567',
           excerpt='"quoted"', claim='A claim.'):
  sha_part = f' · sha: {sha}' if sha else ''
  return (f'- [{ticked}] [{eid}] {title}\n'
          f'  kind: {kind} · boundary: {boundary}\n'
          f'  at: {at}{sha_part}\n'
          f'  excerpt: {excerpt}\n'
          f'  claim: {claim}\n')


def _brief_with(entries_text, root='/w'):
  return (f'---\nharvest: specs\nrepo: repo\nrepo_path: /r\n'
          f'repo_head: abc1234\nroot: {root}\ndate: 2026-07-24\n'
          f'prior_brief: none\nfiles_walked: >\n  specs/a.md\n---\n\n'
          f'## specs/a.md\n\ncaptures:\n\n{entries_text}')


def _validated(entries_text):
  header, entries, errors = dsp.parse_brief(_brief_with(entries_text))
  dsp.validate_entries(entries, errors)
  return errors


def test_parse_splits_kind_boundary_and_at_sha():
  _, entries, errors = dsp.parse_brief(_brief_with(_entry()))
  assert errors == []
  e = entries[0]
  assert e['fields']['kind'] == 'decision'
  assert e['fields']['boundary'] == 'transferable'
  assert e['fields']['at'] == 'specs/a.md §1'
  assert e['fields']['sha'] == '1234567'


def test_parse_collects_also_locations_and_continuations():
  text = ('- [x] [g-02] Title\n'
          '  kind: gotcha · boundary: mixed\n'
          '  at: specs/a.md §1 · sha: 1234567\n'
          '  (also specs/plans/completed/1-a.md L320 · sha: abcdef0)\n'
          '  excerpt: "first line\n'
          '    second line"\n'
          '  claim: Wrapped\n'
          '    claim text.\n')
  _, entries, _ = dsp.parse_brief(_brief_with(text))
  e = entries[0]
  assert e['also'] == [('specs/plans/completed/1-a.md L320', 'abcdef0')]
  # surrounding quotes are brief syntax, stripped at parse (the renderer
  # re-adds exactly one pair)
  assert e['fields']['excerpt'] == 'first line second line'
  assert e['fields']['claim'] == 'Wrapped claim text.'


def test_valid_entry_has_no_errors():
  assert _validated(_entry()) == []


def test_unticked_entries_skip_field_validation():
  assert _validated(_entry(ticked=' ', excerpt='', claim='')) == []


def test_missing_fields_each_reported():
  errors = _validated('- [x] [d-01] Bare\n')
  for req in ('kind', 'boundary', 'at', 'sha', 'excerpt', 'claim'):
    assert any(f'missing {req}' in err for err in errors), req


def test_missing_sha_is_reported():
  errors = _validated(_entry(sha=''))
  assert any('missing sha' in err for err in errors)


def test_kind_prefix_mismatch_is_reported():
  errors = _validated(_entry(eid='d-01', kind='gotcha'))
  assert any('does not match prefix' in err for err in errors)


def test_unknown_boundary_is_reported():
  errors = _validated(_entry(boundary='global'))
  assert any('unknown boundary' in err for err in errors)


def test_ticked_code_coupled_is_reported():
  errors = _validated(_entry(boundary='code-coupled'))
  assert any('code-coupled' in err for err in errors)


def test_square_brackets_in_claim_are_reported():
  errors = _validated(_entry(claim='See [pml1 §3.2] for details.'))
  assert any('square brackets' in err for err in errors)


def test_duplicate_id_is_reported():
  errors = _validated(_entry() + _entry())
  assert any('duplicate id' in err for err in errors)


def test_duplicate_field_is_reported():
  text = _entry() + '  claim: Second claim line.\n'
  errors = _validated(text)
  assert any('duplicate field claim' in err for err in errors)


def test_q_entry_needs_only_at_and_claim():
  text = ('- [x] [q-01] Open thing\n'
          '  at: specs/a.md §12.3\n'
          '  claim: Unresolved question prose.\n')
  assert _validated(text) == []


def test_q_entry_missing_claim_is_reported():
  errors = _validated('- [x] [q-01] Open thing\n  at: specs/a.md §12.3\n')
  assert any('q-01: missing claim' in err for err in errors)


# --- Task 6: assemble --------------------------------------------------------

def _write_brief(root, repo, entries_text, date='2026-07-24'):
  head = _sha(repo)
  text = (f'---\nharvest: specs\nrepo: repo\nrepo_path: {repo}\n'
          f'repo_head: {head}\nroot: {root.resolve()}\ndate: {date}\n'
          f'prior_brief: none\nfiles_walked: >\n'
          f'  specs/completed/a-spec.md; specs/deferred_items.md\n---\n\n'
          f'## specs/completed/a-spec.md\n\ncaptures:\n\n{entries_text}')
  path = root / 'reports' / f'harvest-repo-{date}.md'
  path.write_text(text)
  return path


def _ticked_pair(repo):
  sha = _sha(repo)
  return (f'- [x] [d-01] Use X over Y\n'
          f'  kind: decision · boundary: transferable\n'
          f'  at: specs/completed/a-spec.md §1 · sha: {sha}\n'
          f'  excerpt: "**Decision:** use X over Y."\n'
          f'  claim: X was chosen over Y.\n'
          f'- [ ] [g-01] Declined\n'
          f'  kind: gotcha · boundary: transferable\n'
          f'  at: specs/completed/a-spec.md §2 · sha: {sha}\n'
          f'  excerpt: "More prose."\n'
          f'  claim: Declined claim.\n'
          f'- [x] [q-01] Open thing\n'
          f'  at: specs/deferred_items.md L3\n'
          f'  claim: Whether the later thing matters is unresolved.\n')


def assemble(brief, root):
  return dsp.main(['assemble', str(brief), '--root', str(root)])


def _digests(root):
  return sorted((root / 'raw/specs').glob('*.md'))


def test_assemble_golden_digest(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  sha = _sha(repo)
  brief = _write_brief(root, repo, _ticked_pair(repo))
  assert assemble(brief, root) == 0
  blocks = [(f'[d-01] Use X over Y\n'
             f'at: specs/completed/a-spec.md §1 · sha: {sha}\n'
             f'excerpt: "**Decision:** use X over Y."'),
            (f'[q-01] Open thing\n'
             f'at: specs/deferred_items.md L3\n'
             f'Whether the later thing matters is unresolved.')]
  id8 = hashlib.sha256('\n\n'.join(blocks).encode()).hexdigest()[:8]
  stem = f'2026-07-24-repo-specs-{id8}'
  files = _digests(root)
  assert [p.name for p in files] == [f'{stem}.md']
  expected = (f'---\n'
              f'source: specs-harvest\n'
              f'repo: repo\n'
              f'repo_head: {sha}\n'
              f'date: 2026-07-24\n'
              f'files: 2\n'
              f'captures: 1\n'
              f'open_questions: 1\n'
              f'note: >\n'
              f'  Assembled by distill_specs.py from '
              f'harvest-repo-2026-07-24.md: 1 ticked of\n'
              f'  2 proposed captures; unticked entries remain in the brief '
              f'as\n'
              f'  the declined record.\n'
              f'brief: reports/harvest-repo-2026-07-24.md\n'
              f'files_read: >\n'
              f'  specs/completed/a-spec.md; specs/deferred_items.md\n'
              f'---\n\n'
              f'Ground-truth entries for the capture notes in '
              f'wiki/sources/{stem}.md.\n'
              f'Each entry: verbatim excerpt from the repo file at the\n'
              f'stated location, introducing commit sha.\n\n'
              + '\n\n'.join(blocks) + '\n')
  assert files[0].read_text() == expected


def test_assemble_emits_source_page_body_and_stamps_brief(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  sha = _sha(repo)
  brief = _write_brief(root, repo, _ticked_pair(repo))
  assert assemble(brief, root) == 0
  out = capsys.readouterr().out
  assert (f'### [d-01] Use X over Y\n'
          f'kind: decision · at: repo specs/completed/a-spec.md §1 · '
          f'basis: git:{sha}\n'
          f'X was chosen over Y.') in out
  assert '[q-01]' not in out           # q entries ride in the digest only
  assert '[g-01]' not in out           # unticked stays out
  stem = _digests(root)[0].stem
  brief_text = brief.read_text()
  fm = brief_text.split('---')[1]
  assert f'assembled: {stem}' in fm


def test_source_page_position_drops_line_detail(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  sha = _sha(repo)
  entry = (f'- [x] [g-05] Padded headers\n'
           f'  kind: gotcha · boundary: transferable\n'
           f'  at: specs/completed/a-spec.md Task 2 (L176) · sha: {sha}\n'
           f'  excerpt: "x"\n'
           f'  claim: Headers are padded.\n')
  brief = _write_brief(root, repo, entry)
  assert assemble(brief, root) == 0
  out = capsys.readouterr().out
  assert 'at: repo specs/completed/a-spec.md Task 2 · basis:' in out
  # the digest keeps the full position
  assert 'Task 2 (L176) · sha:' in _digests(root)[0].read_text()


def test_reassembly_is_byte_identical(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  brief = _write_brief(root, repo, _ticked_pair(repo))
  assert assemble(brief, root) == 0
  first = _digests(root)[0]
  before = first.read_bytes()
  assert assemble(brief, root) == 0
  assert [p.name for p in _digests(root)] == [first.name]  # no duplicates
  assert first.read_bytes() == before
  # stamp is idempotent too
  assert brief.read_text().count('assembled:') == 1


def test_validation_failure_reports_all_writes_nothing(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  bad = ('- [x] [d-01] No fields at all\n'
         '- [x] [g-01] Bracketed claim\n'
         '  kind: gotcha · boundary: transferable\n'
         f'  at: specs/completed/a-spec.md §1 · sha: {_sha(repo)}\n'
         '  excerpt: "x"\n'
         '  claim: Bad [locator] here.\n')
  brief = _write_brief(root, repo, bad)
  assert assemble(brief, root) == 1
  err = capsys.readouterr().err
  assert 'brief-error: d-01: missing excerpt' in err
  assert 'brief-error: g-01: square brackets in claim' in err
  assert _digests(root) == []                       # nothing written
  assert 'assembled:' not in brief.read_text()      # no stamp either


def test_each_validation_class_exits_1_and_writes_nothing(tmp_path, capsys):
  '''Spec §9: every failure class through the CLI gate — exit 1, no file.
  (Duplicate-id and duplicate-field are grammar-level classes covered by the
  Task 5 unit tests; the gate path is identical.)'''
  repo = make_repo(tmp_path)
  sha = _sha(repo)
  ok = dict(ticked='x', eid='d-01', title='T', kind='decision',
            boundary='transferable', at='specs/a.md §1', sha=sha,
            excerpt='"x"', claim='A claim.')
  bad_cases = [
    dict(ok, excerpt=''),                  # missing field
    dict(ok, sha=''),                      # missing sha (echo rule)
    dict(ok, kind='gotcha'),               # kind does not match prefix
    dict(ok, boundary='global'),           # unknown boundary
    dict(ok, boundary='code-coupled'),     # ticked code-coupled
    dict(ok, claim='Bad [locator] ref.'),  # square brackets in claim
  ]
  for i, case in enumerate(bad_cases):
    case_root = make_root(tmp_path / f'case{i}')
    brief = _write_brief(case_root, repo, _entry(**case))
    assert assemble(brief, case_root) == 1, case
    assert _digests(case_root) == [], case
    assert 'assembled:' not in brief.read_text(), case
  capsys.readouterr()


def test_no_ticked_entries_is_error(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  unticked = _ticked_pair(repo).replace('- [x]', '- [ ]')
  brief = _write_brief(root, repo, unticked)
  assert assemble(brief, root) == 1
  assert 'no ticked entries' in capsys.readouterr().err
  assert _digests(root) == []


def test_root_mismatch_refused(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  other = tmp_path / 'other-wiki'
  (other / 'raw/specs').mkdir(parents=True)
  brief = _write_brief(root, repo, _ticked_pair(repo))
  assert assemble(brief, other) == 1
  assert 'root mismatch' in capsys.readouterr().err
  assert _digests(other) == [] and _digests(root) == []


def test_planted_secret_never_reaches_digest_or_stdout(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  secret = 'sk-' + 'A' * 24
  sha = _sha(repo)
  entry = (f'- [x] [g-01] Leaky\n'
           f'  kind: gotcha · boundary: transferable\n'
           f'  at: specs/completed/a-spec.md §1 · sha: {sha}\n'
           f'  excerpt: "uses {secret} inline"\n'
           f'  claim: The example key {secret} leaked into the spec.\n'
           f'  note: also here {secret}\n')
  brief = _write_brief(root, repo, entry)
  assert assemble(brief, root) == 0
  digest = _digests(root)[0].read_text()
  out = capsys.readouterr().out
  assert secret not in digest and secret not in out
  assert '[REDACTED:openai-key]' in digest


def test_drift_warns_but_assembles(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  brief = _write_brief(root, repo, _ticked_pair(repo))
  (repo / 'specs/drift.md').write_text('# Drift\n')
  _git(repo, 'add', '.')
  _git(repo, 'commit', '-qm', 'spec: drift')
  assert assemble(brief, root) == 0
  assert 'warning:' in capsys.readouterr().err
  assert len(_digests(root)) == 1


def test_missing_repo_path_warns_but_assembles(tmp_path, capsys):
  repo, root = make_repo(tmp_path), make_root(tmp_path)
  brief = _write_brief(root, repo, _ticked_pair(repo))
  brief.write_text(brief.read_text().replace(
    f'repo_path: {repo}', 'repo_path: /nonexistent/repo'))
  assert assemble(brief, root) == 0
  assert 'cannot check drift' in capsys.readouterr().err
