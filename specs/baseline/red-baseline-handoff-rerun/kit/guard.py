#!/usr/bin/python3
'''PreToolUse hook: deny any tool input that reaches the real home (plan 100).

Usage: /usr/bin/python3 guard.py --real-home <path>   (payload on stdin)

A rep runs with HOME at its own folder, so `~`, `$HOME` and `${HOME}` already
point there. This guard closes what the redirected HOME does not: an absolute
path into the real home (also in its /System/Volumes/Data form, through `..`,
through `~user` or `$USER`), and the rep's Library/Keychains link, which points
into the real ~/Library: any input that names a Keychains path component, or
reaches the rep's own Library folder, is denied. To deny it prints a PreToolUse deny decision and
exits 0. To allow it prints nothing and exits 0. It runs on the system Python
3.9 with the stdlib only. A crashed hook fails open, so any internal error
denies.
'''

from __future__ import annotations

import glob
import itertools
import json
import os
import re
import sys
import threading
import time

PREFIX = 'blocked by the workspace path guard:'
# Copied from $RED/tools/extract.py (PATH_TOKEN, DOTDOT_TOKEN); keep in step by hand.
PATH_TOKEN = re.compile(r'''(?:(?<![\w.~$}-])/|~|\$HOME|\$\{HOME\})[^\s'"`;|&<>(){}]*''')
DOTDOT_TOKEN = re.compile(r'''[^\s'"`;|&<>(){}=]*\.\.(?:/[^\s'"`;|&<>(){}]*)?''')
FILE_KEYS = ('file_path', 'path', 'notebook_path')
DATA_VOLUME = '/System/Volumes/Data'
# A Keychains path component, however the text spells or splits the path around it.
KEYCHAINS = re.compile(r'''(?:^|[/\s'"=])keychains(?:/|$|[\s'";|&)])''')
GLOB_LIMIT = 1000  # more matches than this deny
GLOB_SECONDS = 2.0  # glob expansion past this deadline, per call, denies
SHELL_QUOTES = re.compile(r'''[\\'"]''')
GLOB_CHARS = re.compile(r'[*?\[]')


def scanned(tool_name: str, tool_input: dict) -> list[str]:
    '''The strings of one tool input that can reach a file: a Bash command (its
    first line only when it holds a heredoc, whose body is content), or the path
    fields and a Glob pattern. As in $RED/tools/extract.py's scanned.'''
    if tool_name == 'Bash':
        command = str(tool_input.get('command', ''))
        return [command.split('\n', 1)[0] if '<<' in command else command]
    strings = [str(tool_input[k]) for k in FILE_KEYS if k in tool_input]
    if tool_name == 'Glob' and 'pattern' in tool_input:
        strings.append(str(tool_input['pattern']))
    return strings


def expanded(token: str, home: str, cwd: str) -> str:
    '''The absolute path a token names, as the rep's shell would see it: HOME
    forms become the rep's HOME, other variables and ~user expand from the
    guard's environment, the Data-volume prefix drops in any case, and a relative token
    joins cwd.'''
    for form in ('${HOME}', '$HOME', '~'):
        if token == form or token.startswith(form + '/'):
            token = home + token[len(form):]
            break
    token = os.path.expanduser(os.path.expandvars(token))
    folded = token.casefold()  # APFS folds case, so /system/volumes/data is the same folder
    if folded == DATA_VOLUME.casefold() or folded.startswith(DATA_VOLUME.casefold() + '/'):
        token = token[len(DATA_VOLUME):] or '/'
    return token if os.path.isabs(token) else os.path.join(cwd, token)


def resolved(token: str, home: str, cwd: str) -> str:
    '''The physical, case-folded form of expanded: `..` and symlinks resolve.'''
    return os.path.realpath(expanded(token, home, cwd)).casefold()


def inside(path: str, root: str) -> bool:
    return path == root or path.startswith(root.rstrip('/') + '/')


def expansion(pattern: str, real: str) -> str:
    '''Expand a glob and say whether a match resolves into the real home:
    'real', 'many' (past GLOB_LIMIT matches) or 'none'.'''
    matches = itertools.islice(glob.iglob(pattern), GLOB_LIMIT + 1)
    for count, match in enumerate(matches, 1):
        if count > GLOB_LIMIT:
            return 'many'
        if inside(os.path.realpath(match).casefold(), real):
            return 'real'
    return 'none'


def expanded_within(pattern: str, real: str, deadline: float) -> str:
    '''expansion, run in a daemon thread so a slow walk cannot outlast the
    deadline: 'slow' when it does.'''
    result = ['slow']

    def run() -> None:
        result[0] = expansion(pattern, real)

    worker = threading.Thread(target=run, daemon=True)
    worker.start()
    worker.join(max(0.0, deadline - time.monotonic()))
    return 'slow' if worker.is_alive() else result[0]


def reaches(token: str, home: str, cwd: str, real: str, deadline: float) -> str | None:
    '''Why a token reaches the real home, or None. It does when it resolves
    there, when it is a glob whose fixed part is the real home or one of its
    ancestors below `/`, or when a glob match resolves there (through the
    Keychains link, say). A glob with too many matches, or one that outlasts the
    deadline, cannot be checked, so it counts as reaching.'''
    if inside(resolved(token, home, cwd), real):
        return 'reaches the real home, outside this workspace'
    glob_char = GLOB_CHARS.search(token)
    if glob_char is None:
        return None
    fixed = token[:glob_char.start()]
    fixed = fixed[:fixed.rfind('/') + 1] if '/' in fixed else ''
    base = resolved(fixed or '.', home, cwd)
    if base != '/' and inside(real, base):
        return 'reaches the real home, outside this workspace'
    found = expanded_within(expanded(token, home, cwd), real, deadline)
    return {
        'real': 'reaches the real home, outside this workspace',
        'many': f'has too many matches to check (over {GLOB_LIMIT})',
        'slow': f'took too long to expand (over {GLOB_SECONDS:g} s)',
    }.get(found)


def denied(tool_name: str, tool_input: dict, home: str, cwd: str, real_home: str) -> str | None:
    '''The deny reason for one tool call, or None to allow it. The reason quotes
    the input as typed, never the resolved real home.'''
    deadline = time.monotonic() + GLOB_SECONDS
    real = os.path.realpath(real_home).casefold()
    library = os.path.realpath(os.path.join(home, 'Library')).casefold()
    if tool_name == 'Glob' and tool_input.get('path'):
        cwd = expanded(str(tool_input['path']), home, cwd)  # a Glob pattern is relative to its path
    for text in scanned(tool_name, tool_input):
        bare = SHELL_QUOTES.sub('', text)  # the shell drops quotes and backslashes, so Key""chains is Keychains
        if KEYCHAINS.search(bare.casefold()):
            return f'{PREFIX} the input names Keychains, as in Library/Keychains, a link into the real home'
        tokens = PATH_TOKEN.findall(text) + DOTDOT_TOKEN.findall(text)
        if bare != text:
            tokens += PATH_TOKEN.findall(bare) + DOTDOT_TOKEN.findall(bare)
        if tool_name != 'Bash':
            tokens.append(text)
        for token in tokens:
            why = reaches(token, home, cwd, real, deadline)
            if why is not None:
                return f'{PREFIX} {token!r} {why}'
            if inside(resolved(token, home, cwd), library):
                return f'{PREFIX} {token!r} is in the Library folder, which links into the real home'
    return None


def deny(reason: str) -> None:
    print(json.dumps({'hookSpecificOutput': {
        'hookEventName': 'PreToolUse', 'permissionDecision': 'deny', 'permissionDecisionReason': reason,
    }}))


def real_home_arg(argv: list[str]) -> str:
    if len(argv) != 2 or argv[0] != '--real-home' or not argv[1]:
        raise ValueError('usage: guard.py --real-home <path>')
    return argv[1]


def main() -> int:
    try:
        real_home = real_home_arg(sys.argv[1:])
        payload = json.loads(sys.stdin.read())
        tool_input = payload.get('tool_input') or {}
        if not isinstance(tool_input, dict):
            raise TypeError('tool_input is not an object')
        home = os.environ['HOME']
        cwd = str(payload.get('cwd') or os.getcwd())
        reason = denied(str(payload.get('tool_name', '')), tool_input, home, cwd, real_home)
    except Exception as exc:  # a crashed hook fails open, so every error denies
        reason = f'{PREFIX} internal error: {type(exc).__name__}'
    if reason is not None:
        deny(reason)
    return 0


if __name__ == '__main__':
    sys.exit(main())
