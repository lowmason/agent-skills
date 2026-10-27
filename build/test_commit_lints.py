'''Tests for the commit-lint runner, its pre-commit hook and its CI workflow.

Each hook test clones this repository's HEAD into a temporary directory,
copies in the working-tree runner and hook (so the tests exercise the files
under edit), points core.hooksPath at the hook, and commits. Only the clean
commit and the refusal tests run the full lint set in their clone; the two
no-uv tests and the broken-uv test stop before any lint runs. The mode and
workflow tests read the repository's files without cloning, and the workflow
tests parse .github/workflows/lints.yml statically. With a warm uv cache the
file takes about 15 seconds.
'''
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
RUNNER = Path('build/run_commit_lints.sh')
HOOK = Path('build/githooks/pre-commit')
GENERATED = Path('runtimes/gemini/agents/code-reviewer.md')
# What the broken-uv stub prints to stderr: the hook should name the last line only,
# trimmed, since uv indents a closing "Caused by:" line.
UV_NOISE = 'uv: noise before the reason'
UV_REASON = 'Caused by: no cached Python 3.13 and uv is offline'
CHECKS = {'check_frontmatter', 'check_provenance', 'check_snippets',
          'check_conformance', 'declared_dependencies', 'sync_runtime_assets', 'cc_guide_lint',
          'critical_placement', 'suite_registry', 'versions_check'}


def clean_env(**extra):
    '''os.environ without git's GIT_* variables, plus extra.

    The user and system git configs are switched off (HOME stays, uv needs it), so
    a developer's global hooksPath, identity or aliases cannot change a test's
    outcome. Anything in extra overrides these defaults.
    '''
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1')
    env.update(extra)
    return env


def git(repo, *args, env=None, check=True):
    return subprocess.run(['git', '-C', str(repo), *args], capture_output=True,
                          text=True, env=env or clean_env(), check=check)


def head(repo):
    return git(repo, 'rev-parse', 'HEAD').stdout.strip()


def commit(repo, *args, env=None):
    return git(repo, 'commit', '--quiet', *args, env=env, check=False)


def failed_names(result):
    '''The check names on the runner's `commit lints failed:` line; empty if none.

    The runner echoes `== <name>` for every check it runs, so matching a name
    anywhere in the output cannot tell a failed check from one that passed.
    '''
    match = re.search(r'^commit lints failed: (.*)$', result.stderr, re.MULTILINE)
    return set(match.group(1).split()) if match else set()


def restricted_path(tmp_path, broken_uv=False):
    '''A PATH directory holding git and bash, and no uv unless broken_uv.

    With broken_uv the directory also holds a uv that prints UV_NOISE then UV_REASON,
    indented, to stderr and exits 1, so `command -v uv` finds it and running it fails.
    '''
    bindir = tmp_path / 'bin'
    bindir.mkdir()
    for tool in ('git', 'bash'):
        (bindir / tool).symlink_to(shutil.which(tool))
    if broken_uv:
        uv = bindir / 'uv'
        uv.write_text(f"#!/bin/sh\necho {UV_NOISE!r} >&2\necho {'  ' + UV_REASON!r} >&2\nexit 1\n")
        uv.chmod(0o755)
    return str(bindir)


@pytest.fixture
def clone(tmp_path):
    dst = tmp_path / 'repo'
    subprocess.run(['git', 'clone', '--quiet', '--no-checkout', str(REPO), str(dst)],
                   check=True, env=clean_env())
    git(dst, 'checkout', '--quiet', head(REPO))
    for rel in (RUNNER, HOOK):
        (dst / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / rel, dst / rel)
    git(dst, 'config', 'user.name', 'lint-test')
    git(dst, 'config', 'user.email', 'lint-test@example.invalid')
    git(dst, 'config', 'core.hooksPath', 'build/githooks')
    return dst


def test_runner_and_hook_are_executable():
    assert os.access(REPO / RUNNER, os.X_OK)
    assert os.access(REPO / HOOK, os.X_OK)


def test_runner_and_hook_are_committed_executable():
    # git silently skips a hook without the executable bit, and the check above
    # sees only the working-tree mode, not the one that gets committed.
    for rel in (RUNNER, HOOK):
        listing = git(REPO, 'ls-files', '-s', '--', str(rel)).stdout
        assert listing, f'{rel} is not tracked'
        assert listing.split()[0] == '100755', listing


def test_clean_commit_passes(clone):
    before = head(clone)
    result = commit(clone, '--allow-empty', '-m', 'clean')
    assert result.returncode == 0, result.stdout + result.stderr
    assert head(clone) != before
    assert 'commit lints passed' in result.stderr, result.stderr


def test_frontmatter_violation_is_refused(clone):
    skill = clone / 'skills' / 'explore-data' / 'SKILL.md'
    text = skill.read_text()
    # The description is a folded `>` block: replace its indented continuation lines
    # too, or they are left orphaned and the frontmatter stops parsing as YAML.
    skill.write_text(re.sub(r'^description:.*(?:\n[ \t]+.*)*', 'description: ""', text,
                            count=1, flags=re.MULTILINE))
    before = head(clone)
    result = commit(clone, '-am', 'bad frontmatter')
    assert result.returncode != 0
    assert head(clone) == before
    assert 'check_frontmatter' in failed_names(result), result.stderr
    # The empty-description finding itself, not another frontmatter failure.
    assert 'skills/explore-data/SKILL.md: missing description' in result.stderr, result.stderr


def test_runtimes_hand_edit_is_refused(clone):
    target = clone / GENERATED
    target.write_text(target.read_text() + '\nhand edit\n')
    before = head(clone)
    result = commit(clone, '-am', 'hand edit')
    assert result.returncode != 0
    assert head(clone) == before
    assert 'sync_runtime_assets' in failed_names(result), result.stderr


def test_misplaced_drift_citation_is_refused(clone):
    '''The seventh lint is the drift tool's: a citation after a script's first
    line of code is a violation (drift spec R5).'''
    script = clone / 'build' / 'smoke_test.py'
    script.write_text(script.read_text() + '#' + ' cc-guide: hooks.events @2.1.219\n')
    git(clone, 'add', 'build/smoke_test.py')
    before = head(clone)
    result = commit(clone, '-m', 'misplaced citation')
    assert result.returncode != 0
    assert failed_names(result) == {'cc_guide_lint'}, result.stderr
    assert head(clone) == before


def test_late_critical_section_is_refused(clone):
    '''The eighth lint runs the placement tests. Exception skill-body-past-compaction
    waives compaction-window per file, heading findings included, so check_conformance
    alone passes a Red Flags section moved past the compaction window.'''
    skill = clone / 'skills' / 'subagent-driven-development' / 'SKILL.md'
    text = skill.read_text()
    start = text.index('\n## Red Flags\n') + 1
    end = text.index('\n## ', start) + 1
    skill.write_text(text[:start] + text[end:] + '\n' + text[start:end])
    before = head(clone)
    result = commit(clone, '-am', 'late red flags')
    assert result.returncode != 0, result.stderr
    assert head(clone) == before
    assert failed_names(result) == {'critical_placement'}, result.stderr
    assert ('FAILED test_check_conformance.py::test_real_skill_has_no_critical_heading_past_the_'
            'compaction_window[skills/subagent-driven-development/SKILL.md]') in result.stderr, result.stderr
    # The span-end leg too: `-k test_real_skill` exits 0 while any test matches, so
    # renaming this one test alone would otherwise drop its gate without a failure.
    assert ('FAILED test_check_conformance.py::test_real_skill_critical_spans_end_inside_the_'
            'compaction_window[skills/subagent-driven-development/SKILL.md]') in result.stderr, result.stderr


def test_late_heading_in_acknowledged_file_is_refused(clone):
    '''The writing-skills waiver is per file, so check_conformance alone passes a new
    critical heading past the compaction window; the placement tests catch it.'''
    skill = clone / 'skills' / 'writing-skills' / 'SKILL.md'
    skill.write_text(skill.read_text() + '\n## Warning\n\nA late critical heading.\n')
    before = head(clone)
    result = commit(clone, '-am', 'late warning')
    assert result.returncode != 0, result.stderr
    assert head(clone) == before
    assert failed_names(result) == {'critical_placement'}, result.stderr
    assert ('FAILED test_check_conformance.py::test_real_skill_late_headings_match_the_acknowledged_set'
            '[skills/writing-skills/SKILL.md]') in result.stderr, result.stderr


def test_unregistered_suite_is_refused(clone):
    '''The ninth lint keeps build/suites.toml complete: a first test file in a
    directory that no suite contains needs a [[suite]] entry before it can be committed.'''
    test = clone / 'tools' / 'scan' / 'test_scan.py'
    test.parent.mkdir(parents=True)
    test.write_text('def test_scan():\n    assert True\n')
    git(clone, 'add', 'tools/scan/test_scan.py')
    before = head(clone)
    result = commit(clone, '-m', 'unregistered suite')
    assert result.returncode != 0, result.stderr
    assert head(clone) == before
    assert failed_names(result) == {'suite_registry'}, result.stderr
    assert ('tools/scan: holds pytest files, but no suite in build/suites.toml '
            'contains it') in result.stderr, result.stderr


def test_hook_fails_open_without_uv(clone, tmp_path):
    env = clean_env(PATH=restricted_path(tmp_path))
    before = head(clone)
    result = commit(clone, '--allow-empty', '-m', 'no uv', env=env)
    assert result.returncode == 0, result.stderr
    assert head(clone) != before
    assert 'commit lints skipped' in result.stderr


def test_hook_fails_open_when_uv_cannot_run(clone, tmp_path):
    env = clean_env(PATH=restricted_path(tmp_path, broken_uv=True))
    before = head(clone)
    result = commit(clone, '--allow-empty', '-m', 'broken uv', env=env)
    assert result.returncode == 0, result.stderr
    assert head(clone) != before
    assert 'commit lints skipped' in result.stderr
    assert 'uv cannot run here' in result.stderr, result.stderr
    # The skip names why: uv's last stderr line, trimmed, not the lines before it.
    assert f'({UV_REASON})' in result.stderr, result.stderr
    assert UV_NOISE not in result.stderr, result.stderr


def test_runner_fails_closed_without_uv(clone, tmp_path):
    env = clean_env(PATH=restricted_path(tmp_path))
    result = subprocess.run(['bash', str(clone / RUNNER)], cwd=clone,
                            capture_output=True, text=True, env=env)
    assert result.returncode != 0
    assert failed_names(result) == CHECKS, result.stderr


WORKFLOW = REPO / '.github' / 'workflows' / 'lints.yml'
PINNED = re.compile(r'^[\w.-]+/[\w.-]+@[0-9a-f]{40}$')


def workflow():
    return yaml.safe_load(WORKFLOW.read_text())


def test_workflow_triggers_and_permissions():
    wf = workflow()
    on = wf.get('on', wf.get(True))  # YAML 1.1 reads a bare `on` key as True
    assert set(on) == {'push', 'pull_request'}
    assert on['push']['branches'] == ['main']
    assert wf['permissions'] == {'contents': 'read'}


def test_workflow_pins_actions_and_runs_the_runner():
    steps = [step for job in workflow()['jobs'].values() for step in job['steps']]
    uses = [step['uses'] for step in steps if 'uses' in step]
    assert uses and all(PINNED.match(u) for u in uses), uses
    assert any(step.get('run') == f'bash {RUNNER}' for step in steps)


def test_workflow_bounds_the_job_and_drops_checkout_credentials():
    jobs = workflow()['jobs'].values()
    assert jobs and all(job.get('timeout-minutes') for job in jobs)
    checkouts = [step for job in jobs for step in job['steps']
                 if step.get('uses', '').startswith('actions/checkout@')]
    assert checkouts, 'no actions/checkout step'
    assert all(step.get('with', {}).get('persist-credentials') is False
               for step in checkouts), checkouts
