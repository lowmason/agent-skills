#!/usr/bin/python3
'''PreToolUse hook: deny any tool input that reaches the real home (plan 100).

Usage: /usr/bin/python3 guard.py --real-home <path>   (payload on stdin)

A rep runs with HOME at its own folder, so `~`, `$HOME` and `${HOME}` already
point there. This guard closes what the redirected HOME does not: an absolute
path into the real home (also in its /System/Volumes/Data form, through `..`,
through `~user` or `$USER`), and the rep's Library/Keychains link, which points
into the real ~/Library: any input that names a Keychains path component, or
reaches the rep's own Library folder, is denied. So is a recursive or
whole-disk search whose root is an ancestor of the real home (`find /`,
`grep -r x /Users`, `mdfind`, a Glob `**` or a Grep at `/`), since its output
lists files in the real home. To deny it prints a PreToolUse deny decision and
exits 0. To allow it prints nothing and exits 0. It runs on the system Python
3.9 with the stdlib only. A crashed hook fails open, so any internal error
denies.
'''

from __future__ import annotations

import glob
import itertools
import json
import os
import posixpath
import re
import shlex
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
# Searches. A shell word made only of these characters ends a simple command or redirects.
OPERATOR = re.compile(r'[();<>|&]+')
ASSIGNMENT = re.compile(r'[A-Za-z_]\w*=', re.DOTALL)
WRAPPERS = {'sudo', 'command', 'builtin', 'exec', 'time', 'nice', 'nohup', 'env', 'xargs', 'timeout', 'stdbuf',
            'do', 'then', 'else', 'elif', 'if', 'while', 'until', '{', '!'}  # reserved words lead a command too
# A wrapper's options that take the next word as their value, so that word is no command.
WRAPPER_VALUES = {
    'env': {'-u', '-C', '-S', '--unset', '--chdir', '--split-string'},
    'sudo': {'-u', '-g', '-C', '-D', '-h', '-p', '-U', '-r', '-t', '-T', '--user', '--group', '--close-from',
             '--chdir', '--host', '--prompt', '--other-user', '--role', '--type', '--command-timeout'},
    'timeout': {'-s', '-k', '--signal', '--kill-after'},
    'nice': {'-n', '--adjustment'},
    'xargs': {'-I', '-L', '-n', '-P', '-s', '-d', '-E', '-a', '--max-args', '--max-lines', '--max-procs',
              '--delimiter', '--arg-file'},
    'stdbuf': {'-i', '-o', '-e'},
}
SHELLS = {'sh', 'bash', 'zsh', 'dash', 'ksh'}
INDEXED = {'mdfind', 'locate', 'glocate', 'plocate', 'mlocate'}  # they search the whole disk's index
FIND_OPTIONS = {'-H', '-L', '-P', '-E', '-X', '-s', '-x', '-d', '-O0', '-O1', '-O2', '-O3'}
# Options that take the next word as their value, so that word is no path.
VALUE_OPTIONS = {
    'grep': {'-A', '-B', '-C', '-m', '-e', '-f', '-d', '-D', '--include', '--exclude', '--exclude-dir',
             '--regexp', '--file', '--max-count', '--context', '--after-context', '--before-context'},
    'rg': {'-A', '-B', '-C', '-m', '-e', '-f', '-g', '-t', '-T', '-M', '-j', '-E', '--glob', '--iglob', '--type',
           '--type-not', '--regexp', '--file', '--max-count', '--max-columns', '--threads', '--encoding'},
    'fd': {'-e', '-E', '-t', '-d', '-S', '--extension', '--exclude', '--type', '--max-depth', '--size'},
    'du': {'-d', '-B', '--max-depth', '--block-size', '--exclude'},
    'tree': {'-L', '-I', '-P', '-o', '--filelimit'},
    'ls': set(),
}
VALUE_OPTIONS.update({'egrep': VALUE_OPTIONS['grep'], 'fgrep': VALUE_OPTIONS['grep'], 'ag': VALUE_OPTIONS['rg'],
                      'ack': VALUE_OPTIONS['rg'], 'fdfind': VALUE_OPTIONS['fd']})
PATTERN_OPTIONS = {'-e', '-f', '--regexp', '--file', '--files', '--type-list'}  # no positional pattern then
# On macOS the real home also sits under /System/Volumes/Data, so these hold it too.
DATA_ANCESTORS = ('/system', '/system/volumes')


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


def simple_commands(command: str) -> list[list[str]]:
    '''The words of each simple command in a shell line, as the shell splits
    them. Leading assignments and wrappers (sudo, env, xargs ...) drop, and so
    does each redirection's target. The string of `sh -c` splits in turn, and a
    backtick or `$(` starts a new command, and its body splits in turn, also
    inside double quotes. A `#` is no comment here: the newline before a later
    line becomes `;`, so a comment would hide that line.'''
    commands: list[list[str]] = []
    for body in substitutions(command):
        commands += simple_commands(body)
    text = command.replace('\n', ';').replace('`', ';')
    try:
        lexer = shlex.shlex(text, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        lexer.commenters = ''
        tokens = list(lexer)
    except ValueError:  # an unclosed quote: split on the operators and spaces only
        tokens = re.sub(r'([();<>|&]+)', r' \1 ', text).split()
    words: list[str] = []
    target = False
    for token in tokens + [';']:
        if OPERATOR.fullmatch(token):
            if ('<' in token or '>' in token) and '(' not in token:
                if words and words[-1].isdigit():
                    words.pop()  # the 2 of 2>/dev/null is a file descriptor, not an argument
                target = True  # the next word is a file to read or write
                continue
            commands += command_words(words)
            words, target = [], False
        elif target:
            target = False
        else:
            words.append(token)
    return commands


def substitutions(command: str) -> list[str]:
    '''The bodies of the command substitutions, `$(...)` and backticks, that
    the shell runs: outside single quotes, inside double quotes too.'''
    bodies, quote, i = [], '', 0
    while i < len(command):
        char = command[i]
        if char == '\\' and quote != "'":
            i += 2
            continue
        if quote == "'":
            quote = '' if char == "'" else quote
        elif char == "'" and not quote:
            quote = "'"
        elif char == '"':
            quote = '' if quote else '"'
        elif char == '`':
            end = command.find('`', i + 1)
            end = len(command) if end < 0 else end
            bodies.append(command[i + 1:end])
            i = end
        elif command.startswith('$(', i):
            depth, j = 1, i + 2
            while j < len(command) and depth:
                depth += {'(': 1, ')': -1}.get(command[j], 0)
                j += 1
            bodies.append(command[i + 2:j - 1 if not depth else j])
            i = j - 1
        i += 1
    return bodies


def command_words(words: list[str]) -> list[list[str]]:
    '''One simple command's words, assignments and wrappers dropped, with the
    commands of a `sh -c` or `env -S` string after it.'''
    i, split = 0, []
    while i < len(words):
        if ASSIGNMENT.match(words[i]):
            i += 1
        elif posixpath.basename(words[i]) in WRAPPERS:
            name, i = posixpath.basename(words[i]), i + 1
            values = WRAPPER_VALUES.get(name, set())
            while i < len(words) and words[i].startswith('-') and words[i] != '-':
                option, i = words[i], i + 1
                if option == '--':
                    break
                if option in values and i < len(words):
                    if name == 'env' and option in ('-S', '--split-string'):
                        split += simple_commands(words[i])  # env -S runs its string as a command line
                    i += 1
            if name == 'timeout' and i < len(words):
                i += 1  # the duration
        else:
            break
    words = words[i:]
    found = ([words] if words else []) + split
    if not words:
        return found
    if posixpath.basename(words[0]) in SHELLS:
        for at, word in enumerate(words[1:-1], 1):
            if re.fullmatch(r'-[A-Za-z]*c[A-Za-z]*', word):
                found += simple_commands(words[at + 1])
                break
    return found


def positionals(args: list[str], takes_value: set[str]) -> list[str]:
    '''The words that are not options or option values.'''
    found, skip = [], False
    for arg in args:
        if skip:
            skip = False
        elif arg == '--' or not arg.startswith('-') or arg == '-':
            found.append(arg)
        elif arg in takes_value:
            skip = True
    return [arg for arg in found if arg != '--']


def search_roots(words: list[str]) -> list[str] | None:
    '''The folders a recursive or whole-disk search starts from, or None when
    the command is no such search. An empty list means the working folder. An
    indexed search (mdfind, locate) starts from `/`, since its index covers the
    whole disk.'''
    name, args = posixpath.basename(words[0]), words[1:]
    short = [a[1:] for a in args if a.startswith('-') and not a.startswith('--')]
    if name in INDEXED:
        return ['/']
    if name == 'find':
        i = 0
        while i < len(args) and args[i] in FIND_OPTIONS:
            i += 1
        roots = []
        for arg in args[i:]:
            if arg.startswith('-') or arg in ('!', '(', ')'):
                break
            roots.append(arg)
        return roots
    if name in ('du', 'tree'):
        return positionals(args, VALUE_OPTIONS[name])
    if name == 'ls':
        if '--recursive' in args or any('R' in a for a in short):
            return positionals(args, set())
        return None
    if name in ('grep', 'egrep', 'fgrep'):
        recursive = (any(a in ('--recursive', '--dereference-recursive', '--directories=recurse') for a in args)
                     or any('r' in a or 'R' in a for a in short if not a.startswith(('e', 'f')))
                     or any(a == '-d' and b == 'recurse' for a, b in zip(args, args[1:])))
        if not recursive:
            return None
    elif name not in ('rg', 'ag', 'ack', 'fd', 'fdfind'):
        return None
    roots = positionals(args, VALUE_OPTIONS[name])
    if not any(a.split('=', 1)[0] in PATTERN_OPTIONS for a in args):
        roots = roots[1:]  # the first positional is the pattern
    return roots


def glob_base(token: str) -> str:
    '''A glob's fixed folder: the text before its first glob character, cut
    back to the last `/`. A token with no glob character is its own base.'''
    glob_char = GLOB_CHARS.search(token)
    if glob_char is None:
        return token
    fixed = token[:glob_char.start()]
    return fixed[:fixed.rfind('/') + 1] if '/' in fixed else '.'


def ancestors(real: str) -> set[str]:
    '''The case-folded folders that hold the real home: `/` and each prefix.'''
    parts = real.strip('/').split('/')
    return {'/', *DATA_ANCESTORS} | {'/' + '/'.join(parts[:n]) for n in range(1, len(parts))}


def ancestor_walk(tool_name: str, tool_input: dict, home: str, cwd: str, real: str) -> str | None:
    '''Why a call searches a folder that holds the real home, or None: a
    recursive or indexed shell search, a Glob with `**`, or a Grep, rooted at
    `/`, at the Data volume or at a folder on the way to the real home. Its
    output would list files in the real home.'''
    held = ancestors(real)
    why = 'searches a folder that holds the real home'
    if tool_name == 'Bash':
        command = str(tool_input.get('command', ''))
        for words in simple_commands(command.split('\n', 1)[0] if '<<' in command else command):
            name = posixpath.basename(words[0])
            if name in ('cd', 'pushd'):
                target = next((w for w in words[1:] if not w.startswith('-')), '~')
                cwd = os.path.normpath(expanded(target, home, cwd))
                continue
            roots = search_roots(words)
            if roots is None:
                continue
            if name in INDEXED:
                return f'{PREFIX} {name} {why}: its index covers the whole disk'
            for root in roots or ['.']:
                if resolved(glob_base(root), home, cwd) in held:
                    return f'{PREFIX} {name} {root!r} {why}'
    elif tool_name in ('Glob', 'Grep'):
        base = str(tool_input.get('path') or '.')
        pattern = str(tool_input.get('pattern', ''))
        if tool_name == 'Glob':
            if '**' not in pattern:
                return None
            base = glob_base(pattern if pattern.startswith('/') else posixpath.join(base, pattern))
        if resolved(base, home, cwd) in held:
            return f'{PREFIX} {tool_name} at {base!r} {why}'
    return None


def denied(tool_name: str, tool_input: dict, home: str, cwd: str, real_home: str) -> str | None:
    '''The deny reason for one tool call, or None to allow it. The reason quotes
    the input as typed, never the resolved real home.'''
    deadline = time.monotonic() + GLOB_SECONDS
    real = os.path.realpath(real_home).casefold()
    library = os.path.realpath(os.path.join(home, 'Library')).casefold()
    walk = ancestor_walk(tool_name, tool_input, home, cwd, real)
    if walk is not None:
        return walk
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
