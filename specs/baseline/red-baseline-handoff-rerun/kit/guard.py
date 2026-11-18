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

PREFIX = 'blocked by the workspace path guard:'
# Copied from $RED/tools/extract.py (PATH_TOKEN, DOTDOT_TOKEN); keep in step by hand.
PATH_TOKEN = re.compile(r'''(?:(?<![\w.~$}-])/|~|\$HOME|\$\{HOME\})[^\s'"`;|&<>(){}]*''')
DOTDOT_TOKEN = re.compile(r'''[^\s'"`;|&<>(){}=]*\.\.(?:/[^\s'"`;|&<>(){}]*)?''')
FILE_KEYS = ('file_path', 'path', 'notebook_path')
DATA_VOLUME = '/System/Volumes/Data'
# A Keychains path component, however the text spells or splits the path around it.
KEYCHAINS = re.compile(r'''(?:^|[/\s'"=])keychains(?:/|$|[\s'";|&)])''')
GLOB_LIMIT = 1000
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
    guard's environment, the Data-volume prefix drops, and a relative token
    joins cwd.'''
    for form in ('${HOME}', '$HOME', '~'):
        if token == form or token.startswith(form + '/'):
            token = home + token[len(form):]
            break
    token = os.path.expanduser(os.path.expandvars(token))
    if token == DATA_VOLUME or token.startswith(DATA_VOLUME + '/'):
        token = token[len(DATA_VOLUME):] or '/'
    return token if os.path.isabs(token) else os.path.join(cwd, token)


def resolved(token: str, home: str, cwd: str) -> str:
    '''The physical, case-folded form of expanded: `..` and symlinks resolve.'''
    return os.path.realpath(expanded(token, home, cwd)).casefold()


def inside(path: str, root: str) -> bool:
    return path == root or path.startswith(root.rstrip('/') + '/')


def reaches(token: str, home: str, cwd: str, real: str) -> bool:
    '''True when a token resolves into the real home, when it is a glob whose
    fixed part is the real home or one of its ancestors below `/`, or when one
    of the glob's matches resolves into the real home (through the Keychains
    link, say).'''
    if inside(resolved(token, home, cwd), real):
        return True
    glob_char = GLOB_CHARS.search(token)
    if glob_char is None:
        return False
    fixed = token[:glob_char.start()]
    fixed = fixed[:fixed.rfind('/') + 1] if '/' in fixed else ''
    base = resolved(fixed or '.', home, cwd)
    if base != '/' and inside(real, base):
        return True
    matches = glob.iglob(expanded(token, home, cwd))
    return any(inside(os.path.realpath(m).casefold(), real) for m in itertools.islice(matches, GLOB_LIMIT))


def denied(tool_name: str, tool_input: dict, home: str, cwd: str, real_home: str) -> str | None:
    '''The deny reason for one tool call, or None to allow it. The reason quotes
    the input as typed, never the resolved real home.'''
    real = os.path.realpath(real_home).casefold()
    library = os.path.realpath(os.path.join(home, 'Library')).casefold()
    if tool_name == 'Glob' and tool_input.get('path'):
        cwd = expanded(str(tool_input['path']), home, cwd)  # a Glob pattern is relative to its path
    for text in scanned(tool_name, tool_input):
        if KEYCHAINS.search(text.casefold()):
            return f'{PREFIX} the input names Keychains, as in Library/Keychains, a link into the real home'
        tokens = PATH_TOKEN.findall(text) + DOTDOT_TOKEN.findall(text)
        if tool_name != 'Bash':
            tokens.append(text)
        for token in tokens:
            if reaches(token, home, cwd, real):
                return f'{PREFIX} {token!r} reaches the real home, outside this workspace'
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
