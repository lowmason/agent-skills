'''The Codex and agy guides' version stamps against the CLIs installed here
(owner design, 2026-11-12). cli.py check runs it after the drift check: the
report prints one line per guide and check --hook names each guide behind
its CLI in the session-start notice. Neither changes check's exit.

Each guide carries one line `<!-- cli-stamp: <cli> <X.Y.Z> -->` above its
header, naming the newest release the guide covers; test_cli_versions.py
checks that the header prose names the same version. A guide is behind when
the installed CLI's major.minor is newer than the stamp's, so a patch release
does not count. The stamp is read where check reads (main unless told
otherwise), and the CLI runs only once a stamp is found. A missing stamp, a
CLI not on PATH, a failed --version call or output with no version is a
skip with its reason, never an error.'''
import re
import shutil
import subprocess
from collections.abc import Callable
from typing import NamedTuple

from state import SetupError, Source

GUIDES = (('codex', 'specs/guides/codex-customization-guide.md'),
          ('agy', 'specs/guides/antigravity-customization-guide.md'))
TIMEOUT = 10  # seconds each --version call may take
VERSION = re.compile(r'\b(\d+)\.(\d+)\.(\d+)\b')


class CliError(Exception):
    '''A --version call that failed; the message says how.'''


class Status(NamedTuple):
    cli: str
    stamped: str | None     # the guide's stamped version, None without a stamp
    installed: str | None   # the version --version printed, None when skipped
    skipped: str | None     # why no comparison was made, None when one was

    @property
    def behind(self) -> bool:
        return self.skipped is None and is_behind(self.stamped, self.installed)

    def line(self) -> str:
        '''The report line.'''
        head = f'{self.cli} guide: '
        if self.skipped is None:
            verdict = 'behind' if self.behind else 'current'
            return f'{head}stamped {self.stamped}, installed {self.installed}, {verdict}'
        stamp = f'stamped {self.stamped}; ' if self.stamped else ''
        return f'{head}{stamp}skipped: {self.skipped}'

    def part(self) -> str:
        '''The notice part for a guide behind its CLI.'''
        return f'{self.cli} guide {self.stamped}, installed {self.installed}'


def read_stamp(text: str, cli: str) -> str | None:
    '''The version on the guide's cli-stamp line for cli, or None.'''
    found = re.search(rf'^<!-- cli-stamp: {re.escape(cli)} (\d+\.\d+\.\d+) -->$', text, re.M)
    return found.group(1) if found else None


def parse_version(output: str) -> str | None:
    '''The first three-part version in a --version output, or None.'''
    found = VERSION.search(output)
    return found.group(0) if found else None


def version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split('.'))


def is_behind(stamped: str, installed: str) -> bool:
    '''True when the installed major.minor is newer than the stamped one.'''
    return version_key(installed)[:2] > version_key(stamped)[:2]


def run_version(cli: str) -> str | None:
    '''The output of `cli --version`, or None when cli is not on PATH. Raises
    CliError when the call fails, times out or exits non-zero.'''
    path = shutil.which(cli)
    if path is None:
        return None
    try:
        proc = subprocess.run([path, '--version'], stdin=subprocess.DEVNULL, capture_output=True,
                              text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        raise CliError(f'{cli} --version timed out after {TIMEOUT} s') from None
    except OSError as exc:
        raise CliError(f'{cli} --version failed: {exc}') from None
    if proc.returncode != 0:
        detail = ' '.join(proc.stderr.split())
        raise CliError(f'{cli} --version exited {proc.returncode}' + (f': {detail}' if detail else ''))
    return proc.stdout


def status(source: Source, cli: str, path: str, version_text: Callable[[str], str | None]) -> Status:
    '''One guide's status. The CLI runs only once the guide's stamp is found.'''
    try:
        stamped = read_stamp(source.read(path) or '', cli)
    except SetupError as exc:
        return Status(cli, None, None, str(exc))
    if stamped is None:
        return Status(cli, None, None, f'no cli-stamp line for {cli} in {path}')
    try:
        output = version_text(cli)
    except CliError as exc:
        return Status(cli, stamped, None, str(exc))
    if output is None:
        return Status(cli, stamped, None, f'{cli} not found on PATH')
    installed = parse_version(output)
    if installed is None:
        return Status(cli, stamped, None, f'no version in the output of {cli} --version')
    return Status(cli, stamped, installed, None)


def statuses(source: Source, version_text: Callable[[str], str | None] = run_version) -> list[Status]:
    '''Each stamped guide's status, in GUIDES order.'''
    return [status(source, cli, path, version_text) for cli, path in GUIDES]
