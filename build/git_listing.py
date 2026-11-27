'''The git helpers that build/run_suites.py, build/check_conformance.py and
build/versions_check.py share: a clean git environment, git's own failure text, and the
listing of the files git keeps under a root. It imports only the standard library, since
run_suites.py is the commit lint's entry point. install.py keeps its own copy of git_env
and kept_files, because it runs standalone.'''
import os
import subprocess
from pathlib import Path


class GitError(Exception):
    '''The listing failed. str(exc) is git's own stderr when git ran, else the OSError's text.'''


def git_env() -> dict[str, str]:
    '''os.environ without git's repo-local variables, as install.py's git_env:
    a hook or shell may export GIT_DIR or GIT_INDEX_FILE for another repo.'''
    local = subprocess.run(['git', 'rev-parse', '--local-env-vars'],
                           capture_output=True, text=True, check=True).stdout.split()
    return {name: value for name, value in os.environ.items() if name not in local}


def git_reason(exc: Exception) -> str:
    '''git's own words when it ran and failed (stderr is bytes there), else the
    exception's text.'''
    if isinstance(exc, subprocess.CalledProcessError) and exc.stderr:
        return os.fsdecode(exc.stderr).strip()
    return str(exc)


def kept_paths(root: Path) -> list[str]:
    '''Repo-relative POSIX paths of the files git keeps under root: tracked, or untracked
    and not ignored, in git's order. --cached also lists tracked files deleted from the
    working tree; the caller filters those. Raises GitError when git cannot list them.'''
    try:
        listing = subprocess.run(
            ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
            cwd=root, env=git_env(), capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise GitError(git_reason(exc)) from None
    return [os.fsdecode(entry) for entry in listing.split(b'\0') if entry]
