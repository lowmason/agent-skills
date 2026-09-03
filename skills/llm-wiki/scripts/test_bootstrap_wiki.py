'''Tests for bootstrap_wiki.py. Stdlib + pytest only; scaffold into tmp_path.

The never-clobber contract is the safety-critical part, so it is what these
tests pin down: a plain run and a --force run must both leave every piece of
user content and the seed-once SCHEMA.md byte-for-byte untouched, and --force
must refresh only the managed scripts.
'''
import filecmp
import subprocess
import sys
from pathlib import Path

import pytest

import bootstrap_wiki as bw

BUNDLE = Path(bw.__file__).resolve().parent


def _digest(path):
  return path.read_bytes()


def test_fresh_bootstrap_creates_scaffold_and_verifies(tmp_path):
  root = tmp_path / 'wiki'
  assert bw.main([str(root)]) == 0
  for d in bw.REQUIRED_DIRS:
    assert (root / d).is_dir(), d
  for f in bw.REQUIRED_FILES:
    assert (root / f).is_file(), f
  # installed artifacts are byte-identical to the bundle
  assert filecmp.cmp(BUNDLE / 'schema-template.md', root / 'SCHEMA.md', shallow=False)
  for name in bw.MANAGED_SCRIPTS:
    assert filecmp.cmp(BUNDLE / name, root / 'scripts' / name, shallow=False)


def test_seed_index_drops_personal_topic_headings(tmp_path):
  root = tmp_path / 'wiki'
  assert bw.main([str(root)]) == 0
  index = (root / 'wiki/index.md').read_text()
  assert '## samplers' not in index
  assert '## nowcasting' not in index
  assert 'See SCHEMA.md §index.' in index
  # README lead is de-personalized
  assert 'Personal research wiki' not in (root / 'README.md').read_text()


def test_idempotent_rerun_preserves_user_content(tmp_path):
  root = tmp_path / 'wiki'
  assert bw.main([str(root)]) == 0
  # lint-safe sentinels across every user-content surface (nothing under
  # wiki/<topic>/ as a bare stub, which would make the internal lint fail)
  (root / 'reports/my-analysis.md').write_text('SENTINEL — keep me\n')
  (root / 'raw/assets/paper.txt').write_text('raw bytes — keep me\n')
  with (root / 'wiki/log.md').open('a') as fh:
    fh.write('## [2026-07-23] ingest | sentinel | keep\n')
  with (root / 'wiki/index.md').open('a') as fh:
    fh.write('## samplers\n')
  (root / 'README.md').write_text('# my custom readme\n')
  before = {p: _digest(p) for p in (
    root / 'reports/my-analysis.md', root / 'raw/assets/paper.txt',
    root / 'wiki/log.md', root / 'wiki/index.md', root / 'README.md',
    root / 'wiki/open-questions.md')}
  assert bw.main([str(root)]) == 0
  for p, b in before.items():
    assert _digest(p) == b, p


def test_schema_is_seeded_once_and_survives_force(tmp_path):
  root = tmp_path / 'wiki'
  assert bw.main([str(root)]) == 0
  customized = (root / 'SCHEMA.md').read_text() + '\n<!-- work-wiki local -->\n'
  (root / 'SCHEMA.md').write_text(customized)
  # plain run: SCHEMA untouched
  assert bw.main([str(root)]) == 0
  assert (root / 'SCHEMA.md').read_text() == customized
  # --force: still untouched (only managed code is refreshable)
  assert bw.main([str(root), '--force']) == 0
  assert (root / 'SCHEMA.md').read_text() == customized


def test_force_refreshes_only_divergent_managed_code(tmp_path):
  root = tmp_path / 'wiki'
  assert bw.main([str(root)]) == 0
  # locally clobber both installed scripts
  (root / 'scripts/lint_wiki.py').write_text('# stale local edit\n')
  distill_before = _digest(root / 'scripts/distill_sessions.py')
  # a plain run reports DIFFERS but does not overwrite
  assert bw.main([str(root)]) == 0
  assert (root / 'scripts/lint_wiki.py').read_text() == '# stale local edit\n'
  # --force restores it from the bundle; the untouched script is left alone
  assert bw.main([str(root), '--force']) == 0
  assert filecmp.cmp(BUNDLE / 'lint_wiki.py', root / 'scripts/lint_wiki.py',
                     shallow=False)
  assert _digest(root / 'scripts/distill_sessions.py') == distill_before


def test_dry_run_writes_nothing(tmp_path):
  root = tmp_path / 'wiki'
  assert bw.main([str(root), '--dry-run', '--topic', 'samplers']) == 0
  assert not root.exists() or not any(root.rglob('*'))


def test_check_current_missing_and_drift(tmp_path):
  root = tmp_path / 'wiki'
  # un-bootstrapped root: missing tooling -> drift -> 1
  assert bw.main([str(root), '--check']) == 1
  assert bw.main([str(root)]) == 0
  # fresh install: current -> 0
  assert bw.main([str(root), '--check']) == 0
  # a customized SCHEMA.md is seed-once, NOT drift -> still 0
  (root / 'SCHEMA.md').write_text('# my schema\n')
  assert bw.main([str(root), '--check']) == 0
  # stale managed code -> drift -> 1
  (root / 'scripts/distill_sessions.py').write_text('# stale\n')
  assert bw.main([str(root), '--check']) == 1


def test_check_flags_schema_behind_bundle(tmp_path):
  # A schema whose version marker is behind the bundle is STALE (a coupled
  # linter+schema update shipped a newer contract) -> drift -> 1, even though a
  # merely-customized same-version schema is not.
  root = tmp_path / 'wiki'
  assert bw.main([str(root)]) == 0
  assert bw._schema_version(BUNDLE / 'schema-template.md') is not None
  (root / 'SCHEMA.md').write_text('<!-- schema-version: 0 -->\n# old contract\n')
  assert bw.main([str(root), '--check']) == 1


def test_check_passes_customized_schema_at_current_version(tmp_path):
  # Local customization that keeps the current version marker is not drift -> 0.
  root = tmp_path / 'wiki'
  assert bw.main([str(root)]) == 0
  customized = (root / 'SCHEMA.md').read_text() + '\n<!-- work-wiki local -->\n'
  (root / 'SCHEMA.md').write_text(customized)
  assert bw._schema_version(root / 'SCHEMA.md') == \
      bw._schema_version(BUNDLE / 'schema-template.md')
  assert bw.main([str(root), '--check']) == 0


def test_force_over_managed_script_symlink_spares_outside_target(tmp_path):
  # The one data-destroying vector: a managed-script path that is a symlink to a
  # file OUTSIDE the root. copyfile would follow it; _safe_copy must not.
  root = tmp_path / 'wiki'
  outside = tmp_path / 'outside'
  outside.mkdir()
  assert bw.main([str(root)]) == 0
  victim = outside / 'canonical.py'
  victim.write_text('# canonical outside copy\n')
  before = _digest(victim)
  link = root / 'scripts' / 'lint_wiki.py'
  link.unlink()
  link.symlink_to(victim)
  # plain run: reports DIFFERS, touches nothing outside
  assert bw.main([str(root)]) == 0
  assert _digest(victim) == before
  # --force: replaces the link in place with a real file; outside target spared
  assert bw.main([str(root), '--force']) == 0
  assert _digest(victim) == before
  assert not link.is_symlink()
  assert filecmp.cmp(BUNDLE / 'lint_wiki.py', link, shallow=False)


def test_topic_creates_topic_dirs_with_gitkeeps(tmp_path):
  root = tmp_path / 'wiki'
  assert bw.main([str(root), '--topic', 'samplers', '--topic', 'nowcasting']) == 0
  for t in ('samplers', 'nowcasting'):
    assert (root / 'raw' / t / '.gitkeep').is_file()
    assert (root / 'wiki' / t / '.gitkeep').is_file()


def test_check_rejects_write_flags(tmp_path):
  with pytest.raises(SystemExit):
    bw.main([str(tmp_path / 'wiki'), '--check', '--force'])


def test_root_is_required(tmp_path):
  with pytest.raises(SystemExit):
    bw.main([])


def test_root_that_is_a_file_is_refused(tmp_path):
  f = tmp_path / 'not-a-dir'
  f.write_text('x')
  assert bw.main([str(f)]) == 1


def test_incomplete_bundle_refuses_before_writing(tmp_path, monkeypatch):
  empty = tmp_path / 'fake-bundle'
  empty.mkdir()
  monkeypatch.setattr(bw, 'BUNDLE', empty)
  root = tmp_path / 'wiki'
  assert bw.main([str(root)]) == 1
  assert not root.exists()


# --- specs-harvest extension (specs-harvest framework spec R5/R6) ------------

def test_bootstrap_installs_distill_specs_and_raw_specs_dir(tmp_path):
  root = tmp_path / 'wiki'
  assert bw.main([str(root)]) == 0
  assert (root / 'scripts/distill_specs.py').is_file()
  assert (root / 'raw/specs/.gitkeep').is_file()


def test_seeded_schema_contains_specs_harvest_contract(tmp_path):
  '''Template parity (spec §9): a bootstrapped root inherits the new
  sections without hand edits.'''
  root = tmp_path / 'wiki'
  assert bw.main([str(root)]) == 0
  schema = (root / 'SCHEMA.md').read_text()
  assert 'schema-version: 3' in schema
  assert '## Specs-harvest briefs and digests' in schema
  assert 'raw/specs/' in schema
  assert '`raw/sessions/` or `raw/specs/`' in schema
  assert '- [x] [d-01]' in schema  # the brief entry grammar is codified


def test_installed_distill_specs_runs_beside_its_sibling(tmp_path):
  '''The sibling import (distill_specs -> distill_sessions) must work from
  an installed wiki root, not just the bundle dir.'''
  root = tmp_path / 'wiki'
  assert bw.main([str(root)]) == 0
  proc = subprocess.run(
    [sys.executable, str(root / 'scripts/distill_specs.py'), '--help'],
    capture_output=True, text=True)
  assert proc.returncode == 0
  assert 'inventory' in proc.stdout and 'assemble' in proc.stdout


def test_seeded_schema_documents_locator_vocabulary(tmp_path):
  '''The linter may only hard-error on what SCHEMA.md reserves, so the
  citation rule must be stated in the contract a bootstrapped root inherits
  (spec: lint_wiki citation-detection contract).'''
  root = tmp_path / 'wiki'
  assert bw.main([str(root)]) == 0
  schema = (root / 'SCHEMA.md').read_text()
  assert 'A position opens with' in schema
  assert 'is prose, not a citation' in schema
  assert 'four-digit year' in schema
