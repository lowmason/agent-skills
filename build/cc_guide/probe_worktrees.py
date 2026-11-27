# cc-guide: subagents.worktrees @2.1.332
'''The worktree-isolation probe's runner (deferred item R122): four claude -p
runs in scratch git repos that watch the guide's four probe-backed facts on
worktree isolation (subagents.worktrees). probe_checks.py holds the
assertions, which read the runs' raw streams.

1. A `$(...)` command is refused when it names git and runs when it does
   not, as `HERE=$(pwd)` did (run `isolation`).
2. ExitWorktree keep also exits a `--worktree` launch, despite its
   description, and the session's lock on the worktree goes with it
   (run `isolation`).
3. ExitWorktree is a no-op in a session started inside a worktree that
   plain git made, the stand-in for one a launcher such as the desktop app
   made (run `noop`).
4. With a remote whose fetch fails and no `origin/HEAD`, the default base
   leaves unpushed commits out; only a repository with no remote keeps them
   (runs `base-failed-fetch` and `base-no-remote`).

The guide's fifth fact, that a desktop app session in a worktree was not
isolated, stays a hand check: claude -p cannot start a desktop session.

The setup git and the four runs read no global or system config and none of
the caller's GIT_ variables, so the owner's signing, hooks or default branch cannot change
the repos. Each run loads project settings only, and no scratch repo has
any, so a worktree.baseRef in the owner's user settings cannot decide fact 4.'''
import json
import os
import shutil
import subprocess
from pathlib import Path

import probe_checks
from probe_checks import (ENTER_TOOL, EXIT_TOOL, WT_CONTROL, WT_GIT_SUBSHELL, WT_LIST, WT_LOG, WT_MAIN,
                          WT_PARTS, WT_PLAIN, WT_PLAIN_SUBSHELL, WT_PUSHED, WT_PWD, WT_UNPUSHED, Verdict)
from probe_process import PROBE_TIMEOUT, Invocation, Probe, Read, claude_args
from state import ERROR, SetupError

WORKTREE_TURNS = 20
WORKTREE_NAME = 'probe'  # the --worktree and EnterWorktree name
BRANCH = 'main'
SIGHTINGS = 'worktrees.json'
ISO, ISO_ORIGIN = 'iso', 'iso-origin.git'
PLAIN, PLAIN_WT = 'plain', 'plain-wt'
NO_REMOTE = 'norem'
GONE, GONE_ORIGIN = 'gone', 'gone-origin.git'
NO_GLOBAL_GIT = {'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1'}
GIT_IDENTITY = ('-c', 'user.name=probe', '-c', 'user.email=probe@example.invalid', '-c', 'commit.gpgsign=false')
RUN_ENV = {'CLAUDE_CODE_DISABLE_ADVISOR_TOOL': '1', **NO_GLOBAL_GIT}
DROPPED_ENV = ('GIT_',)  # a caller's GIT_DIR or GIT_WORK_TREE would aim the runs' git at its own repository
ALLOW = ('Bash', 'ExitWorktree', 'EnterWorktree', 'ToolSearch')
PREAMBLE = ('Do these steps in order. Run each command with the Bash tool, one call for each command, exactly as '
            'written, and do not retry a command in another form. If the {tool} tool is not loaded, load it with '
            'ToolSearch first.')  # 2.1.325 deferred both worktree tools
CLOSING = 'Then reply with the word DONE.'
EXIT_STEP = f'Call {EXIT_TOOL} with action keep.'
ENTER_STEP = f'Call {ENTER_TOOL} with name {WORKTREE_NAME}.'


def git(args: list[str], cwd: Path) -> None:
    '''git with the probe's identity, no signing, no global or system config and none of the caller's GIT_
    variables, since a commit hook exports GIT_DIR and GIT_INDEX_FILE for its own repo. A failure is a
    SetupError naming the command.'''
    env = {name: value for name, value in os.environ.items() if not name.startswith('GIT_')} | NO_GLOBAL_GIT
    try:
        subprocess.run(['git', *GIT_IDENTITY, *args], cwd=cwd, env=env, check=True, capture_output=True)
    except subprocess.CalledProcessError as exc:
        said = os.fsdecode(exc.stderr or b'').strip()
        raise SetupError(f"{cwd.name}: git {' '.join(args)} failed: {said}") from None


def git_ok(args: list[str], cwd: Path) -> bool:
    try:
        git(args, cwd)
    except SetupError:
        return False
    return True


def repo_with(folder: Path, *subjects: str) -> Path:
    '''A new repo on BRANCH with one empty commit for each subject, oldest first.'''
    folder.mkdir()
    git(['init', '-q', '-b', BRANCH], folder)
    for subject in subjects:
        git(['commit', '-q', '--allow-empty', '-m', subject], folder)
    return folder


def pushed_to(repo: Path, origin: Path) -> None:
    git(['init', '-q', '--bare', '-b', BRANCH, str(origin)], repo.parent)
    git(['remote', 'add', 'origin', str(origin)], repo)
    git(['push', '-q', '-u', 'origin', BRANCH], repo)


def check_failed_fetch(repo: Path) -> None:
    '''base-failed-fetch reads fact 4 only from a repo with no origin/HEAD, a cached origin/main and a fetch
    that fails.'''
    if git_ok(['symbolic-ref', '-q', 'refs/remotes/origin/HEAD'], repo):
        raise SetupError(f'{repo.name}: has refs/remotes/origin/HEAD')
    if not git_ok(['rev-parse', '--verify', 'refs/remotes/origin/main'], repo):
        raise SetupError(f'{repo.name}: has no refs/remotes/origin/main')
    if git_ok(['fetch', 'origin'], repo):
        raise SetupError(f'{repo.name}: git fetch origin succeeded')


def worktree_places(scratch: Path) -> dict[str, str]:
    '''The places worktree_sightings names, the main checkout's path also being the one the isolation prompt
    gives git -C, so the assertion finds that command.'''
    main = scratch / ISO
    return {WT_MAIN: str(main), 'worktree': str(main / '.claude' / 'worktrees' / WORKTREE_NAME),
            WT_PLAIN: str(scratch / PLAIN_WT)}


def bash(command: str) -> str:
    return f'Run `{command}`.'


def prompt(tool: str, *steps: str) -> str:
    '''The run's steps as a numbered list, after the preamble naming the worktree tool it calls.'''
    numbered = [f'{n}. {step}' for n, step in enumerate(steps, start=1)]
    return '\n'.join([PREAMBLE.format(tool=tool), '', *numbered, '', CLOSING])


def worktree_prompts(scratch: Path) -> dict[str, str]:
    main_git = probe_checks.main_git_command(worktree_places(scratch)[WT_MAIN])
    base = prompt(ENTER_TOOL, ENTER_STEP, bash(WT_LOG))
    isolation = prompt(EXIT_TOOL, bash(WT_CONTROL), bash(main_git), bash(WT_GIT_SUBSHELL), bash(WT_PLAIN_SUBSHELL),
                       bash(WT_LIST), EXIT_STEP, bash(WT_PWD), bash(main_git), bash(WT_LIST))
    return {'isolation': isolation, 'noop': prompt(EXIT_TOOL, EXIT_STEP, bash(WT_PWD)), 'base-no-remote': base,
            'base-failed-fetch': base}


def prepare_worktrees(scratch: Path, claude: str, repo: Path) -> list[Invocation]:
    '''The four scratch repos and a run in each: iso, pushed with origin/HEAD set, launched with --worktree;
    plain-wt, a worktree plain git made of plain; norem, an unpushed commit and no remote; gone, an unpushed
    commit and a remote that is gone, checked before any run starts.'''
    iso = repo_with(scratch / ISO, WT_PUSHED)
    pushed_to(iso, scratch / ISO_ORIGIN)
    git(['remote', 'set-head', 'origin', BRANCH], iso)
    git(['worktree', 'add', '-q', f'../{PLAIN_WT}'], repo_with(scratch / PLAIN, WT_PUSHED))
    repo_with(scratch / NO_REMOTE, WT_PUSHED, WT_UNPUSHED)
    gone = repo_with(scratch / GONE, WT_PUSHED)
    pushed_to(gone, scratch / GONE_ORIGIN)
    git(['commit', '-q', '--allow-empty', '-m', WT_UNPUSHED], gone)
    shutil.rmtree(scratch / GONE_ORIGIN)
    check_failed_fetch(gone)
    cwds = {'isolation': ISO, 'noop': PLAIN_WT, 'base-no-remote': NO_REMOTE, 'base-failed-fetch': GONE}
    prompts = worktree_prompts(scratch)
    return [Invocation(name, claude_args(claude, prompts[name], turns=WORKTREE_TURNS, sources='project',
                                         mode='default', allow=ALLOW,
                                         extra=('--strict-mcp-config',
                                                *(('--worktree', WORKTREE_NAME) if name == 'isolation' else ()))),
                       RUN_ENV, PROBE_TIMEOUT, cwd=cwds[name], drop_prefixes=DROPPED_ENV)
            for name in WT_PARTS]


def collect_worktrees(scratch: Path, run_dir: Path) -> None:
    '''The four streams' sightings, which hold no path, as SIGHTINGS in the run directory.'''
    streams = {}
    for part in WT_PARTS:
        path = run_dir / f'{part}.jsonl'
        streams[part] = probe_checks.parse_stream(path.read_text(encoding='utf-8')) if path.is_file() else None
    sightings = probe_checks.worktree_sightings(streams, worktree_places(scratch))
    (run_dir / SIGHTINGS).write_text(json.dumps(sightings, indent=1) + '\n', encoding='utf-8')


def assess_worktrees(read: Read) -> Verdict:
    text = read(SIGHTINGS)
    if text is None:
        return Verdict(ERROR, f'no {SIGHTINGS}: the collect step wrote no sightings')
    return probe_checks.assess_worktree_isolation(json.loads(text))


WORKTREE_PROBE = Probe(prepare_worktrees, collect_worktrees, assess_worktrees,
                       {SIGHTINGS: 'worktree-isolation.sightings.json'})
