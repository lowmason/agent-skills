#!/usr/bin/env python3
"""PreToolUse(Bash) guard enforcing the read-only agents' Bash contract.

Five agents (see READONLY_AGENTS) declare that they will not mutate the working
tree, the index, HEAD, branch state, or the worktree list. Their `tools:`
frontmatter already denies Write/Edit; nothing enforced the Bash half. This hook
does, by classifying the command and returning a `deny` decision for mutators.

Payloads without a guarded agent — the main session, `debugger`, `docs-writer`,
every built-in agent — are allowed untouched and as early as possible.

Design and rationale: specs/completed/readonly-agent-guard.md.

Runs under whatever `python3` is first on PATH (Python 3.9 on macOS system
Python), so keep this file 3.9-compatible: stdlib only, no `match`, and
annotations deferred via __future__.
"""
from __future__ import annotations

import itertools
import json
import re
import sys

# Keyed on each agent's frontmatter `name`, which is what Claude Code reports as
# the agent type — note the capital E in Explore. build/check_frontmatter.py
# imports this and asserts it against the `## Read-only contract` heading in
# agents/*.md in both directions, so drift fails the lint at commit time.
READONLY_AGENTS = frozenset({
    'code-reviewer',
    'task-reviewer',
    'security-auditor',
    'Explore',
    'test-runner',
})

# Confirmed against Claude Code 2.1.259 by the probe in hooks/README.md.
AGENT_TYPE_KEY = 'agent_type'

CONTRACT_CLAUSE = (
    'you must not mutate the working tree, the index, HEAD, branch state, '
    'or the worktree list via Bash'
)

# Like shlex, the tokenizer returns a run of unquoted punctuation as one token,
# so `);` and `)&&` are single tokens. Each run is cut into pieces: a
# parenthesis, a separator, or a redirection. A separator is any run of ;&|,
# which covers `|&`, zsh's `&|`, and `&;`, which zsh also accepts. A redirection
# starts at < or > (or &>) and keeps what follows, so `2>&1`, `>|` and `&>` stay
# whole, and it stays in its subcommand, so `git log > /tmp/f` classifies as a
# `git log`.
PUNCTUATION = frozenset('();<>|&')
PUNCTUATION_PIECE = re.compile(r'[()]|&?>[<>&|]*|<[<>&|]*|(?:[;|]|&(?!>))+')
SEPARATOR = re.compile(r'[;&|]+')

# shlex's whitespace, and the runs _tokenize reads a line in.
WHITESPACE = frozenset(' \t\r\n')
BLANKS = re.compile(r'[ \t\r\n]+')
PUNCTUATION_RUN = re.compile(r'[();<>|&]+')
PLAIN_RUN = re.compile(r'[^ \t\r\n\'"\\();<>|&]+')
DOUBLE_QUOTED_RUN = re.compile(r'[^"\\]+')


class _Token(str):
    """A word or a run of punctuation, keeping what shlex drops about it.

    `syntax`: an unquoted run of PUNCTUATION. `quoted`: some of it was quoted or
    escaped, and quoting makes a word of anything (`git branch ')'` names a
    branch). `spaced`: whitespace or the start of the line comes before it, so
    it does not touch the token on its left. `expands`: zsh may make any number
    of words of it: the `$` of an unquoted `$(…)`, whose output zsh splits, or a
    glob, which becomes every file it matches.
    """

    def __new__(cls, text, syntax=False, quoted=False, spaced=False, expands=False):
        token = super().__new__(cls, text)
        token.syntax = syntax
        token.quoted = quoted
        token.spaced = spaced
        token.expands = expands
        return token


CLOSE_PAREN = _Token(')', syntax=True)

# Unquoted, a `}` alone is syntax wherever it stands in zsh, and ends a
# subcommand as a separator does. `{` and the `]]` closing a test are syntax
# only where a command could start, and zsh runs one right after them on the
# same line (`{ rm x; }`, `if [[ -n a ]] rm x`). Anywhere else they are words:
# `git branch {` names a branch. See _split_tokens.
CLOSE_BRACE = '}'
COMMAND_POSITION_SYNTAX = frozenset({'{', ']]'})

# The words a nested group leaves in the command around it, so the next word
# cannot slide into its place. A group inside a word is a glob, and zsh makes it
# every file it matches: `git (stash)` runs `git stash` when a file named stash
# exists, so git's verb slot fails closed on one as it always did. A process
# substitution, `<(…)` or `>(…)`, is one path, never a redirection.
GROUP_WORD = _Token('()', expands=True)
PROCESS_SUBSTITUTION = _Token('<()')

# Three choices only a shell parser could make, so every line is read all eight
# ways and a denial in any reading stands. Each reading holds for a whole line,
# so a line that needs two at once, flat for one construct and nested for
# another, is misread by all eight. See _split_tokens.
READINGS = tuple(itertools.product((True, False), repeat=3))  # nest, braces, quoting

# What zsh reads as the file descriptor of the redirection after it: a single
# unquoted digit touching the operator (`2>&1`; in `2 >f` and `12>f` the digits
# are arguments), or a `{name}` before it, spaced or not, which zsh gives a new
# descriptor (`exec {fd}>f`). The name is an ASCII identifier: in the C locale
# zsh reads `{é}` as a word.
FILE_DESCRIPTOR_DIGIT = re.compile(r'[0-9]')
NAMED_FILE_DESCRIPTOR = re.compile(r'\{[A-Za-z_][A-Za-z0-9_]*\}')

# zsh's numeric glob, `<->` or `<1-5>`: the middle of the three pieces it is cut
# into. It matches files named by numbers and redirects nothing.
NUMERIC_RANGE = re.compile(r'[0-9]*-[0-9]*')

# Words that lead a subcommand without being its command: reserved words and
# zsh's precommand modifiers, `-` among them (quoted or escaped: the Bash tool's
# shell snapshot aliases a bare `-` to `cd -`). `for`, `select` and `case` are
# absent on purpose: the word after them is a name or a pattern, never a
# command, so `for rm in a` must not read as `rm`.
LEADING_KEYWORDS = frozenset({
    '!', 'if', 'then', 'elif', 'else', 'while', 'until', 'do', 'coproc',
    'noglob', 'nocorrect', 'builtin', '-',
})

# Utilities that run a command after their own options, each mapped to its
# options that take a value. `command -v` and `-V` only describe the command.
PREFIX_UTILITIES = {
    'command': frozenset(),
    'env': frozenset({'-C', '-P', '-S', '-u'}),
    'exec': frozenset({'-a'}),
    'nice': frozenset({'-n'}),
    'nohup': frozenset(),
    'time': frozenset(),
}

ASSIGNMENT = re.compile(r'[A-Za-z_][A-Za-z0-9_]*\+?=')

DENIED_COMMANDS = {
    'rm': '`rm` deletes files.',
    'mv': '`mv` moves or renames files.',
    'truncate': '`truncate` rewrites file contents in place.',
    'shred': '`shred` destroys file contents.',
    'sudo': '`sudo` escalates privileges and can mutate anything.',
}

# git's read-only vocabulary is small and enumerable, so this is an allowlist
# and anything not on it is denied — including verbs git adds in the future.
GIT_READONLY_VERBS = frozenset({
    'log', 'show', 'diff', 'diff-tree', 'status', 'grep', 'blame', 'ls-files',
    'ls-tree', 'ls-remote', 'cat-file', 'rev-parse', 'rev-list', 'describe',
    'shortlog', 'whatchanged', 'name-rev', 'merge-base', 'for-each-ref',
    'count-objects', 'verify-commit', 'check-ignore', 'check-attr', 'var',
    'help', 'version',
})

# Print-and-exit flags: allow immediately, there is no verb behind them.
GIT_INFO_FLAGS = frozenset({
    '--version', '--help', '-h', '--html-path', '--man-path', '--info-path',
})

# Global options skipped while locating the verb.
GIT_GLOBAL_FLAGS = frozenset({
    '-p', '--paginate', '-P', '--no-pager', '--bare', '--literal-pathspecs',
    '--no-literal-pathspecs', '--glob-pathspecs', '--noglob-pathspecs',
    '--icase-pathspecs', '--no-replace-objects', '--no-optional-locks',
    '--no-lazy-fetch', '--no-advice',
})
GIT_GLOBAL_WITH_VALUE = frozenset({
    '-C', '-c', '--git-dir', '--work-tree', '--namespace', '--exec-path',
    '--config-env', '--attr-source',
})

# A read-only route to what the denied verb was probably reaching for. Naming it
# lets the agent report accurately to its controller instead of retrying blind.
# Only consulted for verbs that reach the fail-closed default, so do NOT add keys
# for verbs in GIT_SUBCOMMAND_ALLOWED / GIT_FLAG_ALLOWED — those are handled
# earlier in _classify_git, and an entry here would be dead code.
GIT_ALTERNATIVES = {
    'checkout': 'To read a file at another revision use `git show <SHA>:<path>`; '
                'to compare, `git diff <SHA>..HEAD`.',
    'switch': 'To read a file at another revision use `git show <SHA>:<path>`.',
    'restore': 'To read a file at another revision use `git show <SHA>:<path>`.',
    'reset': 'To compare against another revision use `git diff <SHA>..HEAD`.',
    'clean': 'To see what is untracked use `git status --porcelain`.',
    'add': 'Nothing in a read-only review touches the index.',
    'commit': 'Nothing in a read-only review creates a commit.',
    'fetch': 'Denied deliberately, not by fall-through: a fetch part-way through a '
             'review silently changes what a later `git diff origin/main...` shows, '
             'so the artifact moves while it is being reviewed. If you need a base '
             'ref that is not local, report that to your controller so it can fetch '
             'before dispatching.',
    'pull': 'Denied deliberately, not by fall-through: `git pull` merges into HEAD. '
            'Report a missing base ref to your controller instead of fetching it '
            'yourself.',
}

# Verbs whose read-only forms are named by a subcommand: (allowed subcommands,
# whether the bare verb is itself read-only). `git stash` bare is NOT — it
# stashes the caller's uncommitted work, which is the exact damage this guard
# exists to prevent.
GIT_SUBCOMMAND_ALLOWED = {
    'stash': (frozenset({'list', 'show'}), False),
    'worktree': (frozenset({'list'}), False),
    'submodule': (frozenset({'status', 'summary'}), False),
    'notes': (frozenset({'list', 'show'}), False),
    'bisect': (frozenset({'log', 'view'}), False),
    'sparse-checkout': (frozenset({'list'}), False),
    'remote': (frozenset({'show', 'get-url'}), True),
    'reflog': (frozenset({'show'}), True),
}

# Verbs whose read-only forms are named by flags. `value_flags` take an argument,
# which must not be mistaken for a positional. A positional is allowed only
# alongside a `list_flag`, because `git branch foo` and `git tag v1` create.
# `required` (config only) means at least one of these must be present.
GIT_FLAG_ALLOWED = {
    'branch': {
        'flags': frozenset({'-l', '--list', '-a', '-r', '-v', '-vv', '--contains',
                            '--merged', '--no-merged', '--show-current',
                            '--format', '--sort'}),
        'value_flags': frozenset({'--contains', '--merged', '--no-merged',
                                  '--format', '--sort'}),
        'list_flags': frozenset({'-l', '--list'}),
        'required': frozenset(),
    },
    'tag': {
        'flags': frozenset({'-l', '--list', '--contains', '--points-at',
                            '--sort', '--format'}),
        'value_flags': frozenset({'--contains', '--points-at', '--sort',
                                  '--format'}),
        'list_flags': frozenset({'-l', '--list'}),
        'required': frozenset(),
    },
    'config': {
        'flags': frozenset({'--get', '--get-all', '--get-regexp', '--list', '-l'}),
        'value_flags': frozenset(),
        'list_flags': frozenset({'--get', '--get-all', '--get-regexp',
                                 '--list', '-l'}),
        'required': frozenset({'--get', '--get-all', '--get-regexp',
                               '--list', '-l'}),
    },
}


# Syntax the scan in _logical_lines does not model. Most opens a context with
# quoting rules of its own, which the tokenizer's flat posix model (shlex's)
# cannot follow: command and arithmetic substitution, backticks, ANSI-C strings,
# parameter expansion, arithmetic, heredocs. A backslash-newline joins lines,
# and the shell joins them in and out of quotes, so it is here too. A command
# that contains any of them is split at every newline, exactly as before
# multi-line quotes were supported, so nothing is ever joined on a misreading.
UNMODELED_SYNTAX = ('$(', '`', "$'", '${', '$[', '((', '<<', '\\\n')

SPAN_AFTER_HASH = (
    'a quoted string spans lines after an unquoted `#`, and whether that `#` '
    'starts a comment depends on the shell and the context')


def _tokenize(line):
    """Split one line into the words and punctuation runs shlex returns.

    The texts, and the errors for an unclosed quote or a trailing backslash,
    are exactly those of shlex in posix mode with punctuation_chars and
    whitespace_split and no commenters, the reading every rule here was built
    on; the tests hold the two together. Each _Token also keeps what shlex
    drops: whether it was quoted, and whether whitespace came before it.
    """
    tokens = []
    spaced = True
    i = 0
    while i < len(line):
        blanks = BLANKS.match(line, i)
        if blanks:
            spaced = True
            i = blanks.end()
            continue
        run = PUNCTUATION_RUN.match(line, i)
        if run:
            if (run.group().startswith('(') and not spaced and tokens
                    and not tokens[-1].syntax and tokens[-1].endswith('$')):
                tokens[-1].expands = True  # `$(…)`: zsh splits what it prints
            tokens.append(_Token(run.group(), syntax=True, spaced=spaced))
            i = run.end()
        else:
            word, quoted, i = _read_word(line, i)
            tokens.append(_Token(word, quoted=quoted, spaced=spaced))
        spaced = False
    return tokens


def _read_word(line, i):
    """Return the word starting at line[i], whether any of it was quoted or
    escaped, and where it ends."""
    parts = []
    quoted = False
    while i < len(line):
        plain = PLAIN_RUN.match(line, i)
        if plain:
            parts.append(plain.group())
            i = plain.end()
            continue
        char = line[i]
        if char in WHITESPACE or char in PUNCTUATION:
            break
        quoted = True
        if char == "'":  # everything up to the next one is literal
            end = line.find("'", i + 1)
            if end < 0:
                raise ValueError('No closing quotation')
            parts.append(line[i + 1:end])
            i = end + 1
        elif char == '\\':
            if i + 1 == len(line):
                raise ValueError('No escaped character')
            parts.append(line[i + 1])
            i += 2
        else:
            text, i = _read_double_quoted(line, i + 1)
            parts.append(text)
    return ''.join(parts), quoted, i


def _read_double_quoted(line, i):
    """Return the text from just inside a `"` to its close, and where it ends.

    A backslash escapes only `"` and itself; before anything else it stays.
    """
    parts = []
    while True:
        run = DOUBLE_QUOTED_RUN.match(line, i)
        if run:
            parts.append(run.group())
            i = run.end()
        if i == len(line):
            raise ValueError('No closing quotation')
        if line[i] == '"':
            return ''.join(parts), i + 1
        if i + 1 == len(line):  # the backslash ends the line
            raise ValueError('No escaped character')
        escaped = line[i + 1]
        parts.append(escaped if escaped in '"\\' else '\\' + escaped)
        i += 2


def _pieces(tokens, quoting):
    """Yield each word, and each piece of each run of punctuation.

    Blind to quoting, a word of nothing but punctuation is a run like any other.
    """
    for token in tokens:
        if token.syntax or (not quoting and token and PUNCTUATION.issuperset(token)):
            spaced = token.spaced
            for piece in PUNCTUATION_PIECE.findall(token):
                yield _Token(piece, syntax=True, spaced=spaced)
                spaced = False
        else:
            yield token


def _numeric_globs(pieces):
    """Return the pieces, with the `<` and `>` of each numeric glob as words."""
    pieces = list(pieces)
    for i in range(len(pieces) - 2):
        opening, middle, closing = pieces[i:i + 3]
        if (opening.syntax and opening == '<' and not middle.syntax
                and not middle.quoted and not middle.spaced
                and NUMERIC_RANGE.fullmatch(middle) and closing.syntax
                and closing.startswith('>') and not closing.spaced):
            pieces[i] = _Token(opening, spaced=opening.spaced, expands=True)
            pieces[i + 2] = _Token(closing)
    return pieces


def _closing_parens(enclosing):
    """Yield a `)` while a group is open; each one read closes a group."""
    while enclosing:
        yield CLOSE_PAREN


def _group_word(current, paren):
    """Return the word a group opening at `paren` leaves in `current` when it
    closes, taking from `current` any word glued to it. None for `$(…)`, whose
    `$` already stands in its place, and where no command surrounds it."""
    if not current:
        return None
    before = current[-1]
    if paren.spaced:
        return GROUP_WORD
    if not before.syntax:
        if before.endswith('$'):
            return None
        current.pop()  # glued into one glob: `*(.)`, `=(…)`
        return GROUP_WORD
    if before in ('<', '>'):
        current.pop()
        if not before.spaced and current and not current[-1].syntax:
            current.pop()  # glued into one word: `2<(true)` is `2/dev/fd/11`
        return PROCESS_SUBSTITUTION
    return GROUP_WORD


def _ends_a_subcommand(piece, braces, quoting):
    if piece.syntax:
        return piece in ('(', ')') or SEPARATOR.fullmatch(piece) is not None
    if quoting and piece.quoted:
        return False
    return piece == CLOSE_BRACE or (braces and piece in COMMAND_POSITION_SYNTAX)


def _split_tokens(tokens, nest, braces, quoting):
    """Split one line's tokens into subcommands, in one of READINGS.

    Separators end a subcommand, and so do the parentheses and braces
    _ends_a_subcommand names; redirections stay in theirs. Three things here
    take a parser, so classify reads every line each way and denies if any
    reading does. Each choice holds for the whole line, so a line that needs
    both answers to one of them, in two places, is misread either way:

    `nest`: a parenthesis may open a group inside a word, where the command
    around it continues after the `)` (`$(…)`, `<(…)`, zsh's `*(.)`), or stand
    before a command (a case pattern's `(a) rm x`, `f() rm x`, zsh's `for f (a)
    rm x`). Nested, a group is a subcommand of its own, and the one it
    interrupted resumes after it with one word in its place, the word zsh
    makes of it and whatever it touches (see _group_word): an unspaced `$(…)`
    leaves its `$`, a process substitution PROCESS_SUBSTITUTION, and any other
    group GROUP_WORD. Flat, a parenthesis ends a subcommand like a separator.
    An unmatched `)` ends a subcommand either way, and a group still open at
    the end of the line closes there.

    `braces`: `{` and `]]` end a subcommand, as where a command could start, or
    are words, as among arguments (`git branch { HEAD`).

    `quoting`: a quoted word is only ever a word, as zsh reads it, or it splits
    like the syntax it spells, as a quoted `;` does once eval hands it back to
    the shell. Blind to quoting is how every command was read before quoting
    was kept.
    """
    subcommands = []
    # (subcommand a nested group interrupted, the word it leaves), innermost last
    enclosing = []
    current = []
    glued = False  # a group just closed, and a word touching it is part of its word
    pieces = _numeric_globs(_pieces(tokens, quoting))
    # A group still open when the line runs out closes there, as if at a `)`.
    for piece in itertools.chain(pieces, _closing_parens(enclosing)):
        if glued and not piece.syntax and not piece.spaced:
            continue  # `$(pwd)/.git`, `<(x)y`
        glued = False
        if nest and piece.syntax and piece == '(':
            enclosing.append((current, _group_word(current, piece)))
            current = []
        elif _ends_a_subcommand(piece, braces, quoting):
            if current:
                subcommands.append(current)
            current = []
            if nest and piece.syntax and piece == ')' and enclosing:
                current, word = enclosing.pop()
                if word is not None:
                    current.append(word)
                glued = bool(current)
        else:
            current.append(piece)
    if current:
        subcommands.append(current)
    return subcommands


def _logical_lines(command):
    """Split `command` at the newlines that end a shell command.

    Only unquoted newlines end one, so cutting at every newline breaks any
    quoted string that spans lines. This scan follows the tokenizer's posix
    quoting rules (shlex's), so the two agree on where every quote closes: a
    newline inside '...' or "..." stays in its word. An unterminated quote runs
    to the end of the command, where the tokenizer raises and a guarded agent
    fails closed. A command with anything in UNMODELED_SYNTAX is not scanned
    at all.

    It does not model comments. Where a `#` starts one depends on the shell and
    the context (zsh glob qualifiers, arithmetic), and a wrong guess either
    hides live code or lets a comment's apostrophe open a quote that swallows
    the lines after it. So comment text is tokenized like any other, and a
    physical line with an unquoted `#` may not end inside a quote: the scan
    raises instead.
    """
    if any(syntax in command for syntax in UNMODELED_SYNTAX):
        return command.split('\n')
    lines = []
    current = []
    quote = None
    unquoted_hash = False  # on the current physical line
    i = 0
    while i < len(command):
        char = command[i]
        if char == '\\' and quote != "'":  # nothing escapes inside single quotes
            current.append(command[i:i + 2])  # never a newline: see UNMODELED_SYNTAX
            i += 2
            continue
        if char == '\n':
            if quote is None:
                lines.append(''.join(current))
                current = []
            elif unquoted_hash:
                raise ValueError(SPAN_AFTER_HASH)
            else:
                current.append(char)
            unquoted_hash = False
        else:
            current.append(char)
            if quote is None:
                if char in '\'"':
                    quote = char
                elif char == '#':
                    unquoted_hash = True
            elif char == quote:
                quote = None
        i += 1
    lines.append(''.join(current))
    return lines


def split_subcommands(command, nest=True, braces=True, quoting=True):
    """Tokenize `command` and split it into subcommands, in one reading.

    Each logical line is tokenized on its own, because the tokenizer, like
    shlex, treats a newline as ordinary whitespace, which would otherwise fold a
    second command into the first subcommand and hide its leading token from
    classification. Raises ValueError from the scan as well as from the
    tokenizer; either way a guarded agent fails closed. The keywords pick the
    reading; see _split_tokens.
    """
    subcommands = []
    for line in _logical_lines(command):
        subcommands.extend(_split_tokens(_tokenize(line), nest, braces, quoting))
    return subcommands


def _physical_line_tokens(command, logical_lines):
    """Yield each physical line's tokens, tokenized alone.

    This is the split from before multi-line support. A line that does not
    tokenize alone, because a quote or a continuation spans it, is skipped: the
    logical lines have read it. So is a line that is also a logical line.
    """
    for line in command.split('\n'):
        if line in logical_lines:
            continue
        try:
            yield _tokenize(line)
        except ValueError:
            continue


def _sed_edits_in_place(args):
    for token in args:
        if token == '--in-place' or token.startswith('--in-place='):
            return True
        if token.startswith('-') and not token.startswith('--') and 'i' in token[1:]:
            return True
    return False


def _expands_to_words(what, danger):
    """The reason to deny when a word zsh expands could carry `danger`."""
    return ('`' + what + '` is given an unquoted substitution or glob, and zsh can '
            'make it several words, ' + danger + ', so this guard fails closed. '
            'To keep a substitution one word, quote it: "$(…)".')


def _classify_non_git(name, args):
    if name in DENIED_COMMANDS:
        return DENIED_COMMANDS[name] + ' This agent inspects; it does not modify.'
    if name == 'sed' and _sed_edits_in_place(args):
        return ('`sed -i` edits files in place; drop `-i` to write the result to '
                'stdout instead.')
    if name == 'sed' and any(arg.expands for arg in args):
        return _expands_to_words('sed', 'among them `-i`')
    return None


def _command_name(word):
    return word.rpartition('/')[2]  # `/bin/rm` runs rm


def _is_redirection(token):
    return token.syntax and token.startswith(('<', '>', '&>'))


def _names_a_file_descriptor(word, redirection):
    """Whether zsh reads `word` as the file descriptor `redirection` acts on."""
    if word.quoted or not _is_redirection(redirection):
        return False
    if FILE_DESCRIPTOR_DIGIT.fullmatch(word):
        return not redirection.spaced
    return NAMED_FILE_DESCRIPTOR.fullmatch(word) is not None


def _without_redirections(tokens):
    """Drop each redirection with its target and the file descriptor it names.

    A redirection can stand anywhere in a command and is never an argument:
    `2>/dev/null rm x` runs rm, and the `2` in `git remote -v 2>&1` is not a
    subcommand. Only what zsh reads as a file descriptor goes with it, though:
    the `5` in `git branch 5 >f` names a branch.
    """
    words = []
    i = 0
    while i < len(tokens):
        if _is_redirection(tokens[i]):
            i += 2
        elif i + 1 < len(tokens) and _names_a_file_descriptor(tokens[i], tokens[i + 1]):
            i += 3
        else:
            words.append(tokens[i])
            i += 1
    return words


def _skip_prefix_utility(words, i):
    """Return where the command run by the prefix utility at words[i] starts,
    or len(words) if it runs none."""
    name = _command_name(words[i])
    i += 1
    while i < len(words):
        word = words[i]
        if word == '--':
            return i + 1
        if word.startswith('-'):
            if name == 'command' and ('v' in word or 'V' in word):
                return len(words)  # it only describes the command
            i += 2 if word in PREFIX_UTILITIES[name] else 1
        elif name == 'env' and ASSIGNMENT.match(word):
            i += 1
        else:
            break
    return i


def _command_words(words):
    """Drop the words before a command; [] if there is none.

    Those are LEADING_KEYWORDS, assignments (`X=1 rm x`), and PREFIX_UTILITIES
    with their options, in any order and number: `time env GIT_PAGER=cat git
    stash` runs `git stash`.
    """
    i = 0
    while i < len(words):
        word = words[i]
        if word in LEADING_KEYWORDS or ASSIGNMENT.match(word):
            i += 1
        elif word == 'repeat':
            i += 2  # and its count
        elif _command_name(word) in PREFIX_UTILITIES:
            i = _skip_prefix_utility(words, i)
        else:
            break
    return words[i:]


def _classify_subcommand(tokens):
    words = _command_words(_without_redirections(tokens))
    if not words:
        return None
    name = _command_name(words[0])
    if name == 'git':
        return _classify_git(words[1:])
    return _classify_non_git(name, words[1:])


def classify(command):
    """Return None if `command` is read-only, else a reason fragment for denial.

    git is an allowlist that fails closed on unknown verbs; non-git is a
    denylist of unambiguous mutators, so unlisted commands pass. The asymmetry
    is deliberate — read-only shell is unbounded, read-only git is not.

    Every line is split in each of READINGS (see _split_tokens), and every
    physical line is also classified on its own, the way it was before
    multi-line support. A denial in any reading stands, so whatever one reading
    gets wrong, a mutator that leads a subcommand in any of them is denied. That
    covers only what the readings differ on, and only a line one reading gets
    right as a whole. The tokens under all of them keep their quoting and
    spacing, since whatever a shared step loses, no reading can recover.
    """
    logical_lines = _logical_lines(command)
    lines = [_tokenize(line) for line in logical_lines]
    lines.extend(_physical_line_tokens(command, set(logical_lines)))
    for tokens in lines:
        for nest, braces, quoting in READINGS:
            for subcommand in _split_tokens(tokens, nest, braces, quoting):
                detail = _classify_subcommand(subcommand)
                if detail is not None:
                    return detail
    return None


def _readable_forms(verb, subcommands):
    return ' / '.join('`git ' + verb + ' ' + s + '`' for s in sorted(subcommands))


def _classify_git_subcommand_verb(verb, rest):
    allowed, bare_is_readonly = GIT_SUBCOMMAND_ALLOWED[verb]
    subcommand = None
    for token in rest:
        if not token.startswith('-'):
            subcommand = token
            break
    if subcommand is None:
        if bare_is_readonly:
            return None
        return ('bare `git ' + verb + '` mutates state; only '
                + _readable_forms(verb, allowed) + ' are read-only.')
    if subcommand in allowed:
        return None
    return ('`git ' + verb + ' ' + subcommand + '` is not a read-only form; only '
            + _readable_forms(verb, allowed) + ' are allowed.')


def _classify_git_flag_verb(verb, rest):
    """Classify a flag-keyed verb (branch / tag / config).

    Two structural notes:
    * A value flag consumes the next token, so `git branch --contains <ref>` and
      `git branch --merged <ref>` never register a positional. That is the right
      resolution for a read-only check — those arguments are commit-ish, not new
      branch names — but it does mean the positional guard below cannot fire
      alongside them.
    * For `config`, `list_flags == required`, so the positional branch is
      unreachable: anything carrying a positional has already satisfied the
      required check via the same flag set. Kept uniform with branch/tag rather
      than special-cased.
    """
    rule = GIT_FLAG_ALLOWED[verb]
    if any(token.expands for token in rest):
        return _expands_to_words('git ' + verb, 'among them a name to create or a '
                                 'flag that writes')
    seen = set()
    has_positional = False
    i = 0
    while i < len(rest):
        token = rest[i]
        if token.startswith('-'):
            name, sep, _value = token.partition('=')
            if name not in rule['flags']:
                return ('`git ' + verb + ' ' + token + '` is not one of the '
                        'read-only forms of `git ' + verb + '`.')
            seen.add(name)
            i += 1 if sep else (2 if name in rule['value_flags'] else 1)
            continue
        has_positional = True
        i += 1
    if rule['required'] and not (seen & rule['required']):
        return ('`git ' + verb + '` is read-only only in its query forms ('
                + ', '.join('`' + f + '`' for f in sorted(rule['required']))
                + '); any other form writes.')
    if has_positional and not (seen & rule['list_flags']):
        return ('`git ' + verb + '` with a bare argument creates or moves a '
                + verb + '; use `git ' + verb + ' --list` to read.')
    return None


def _locate_git_verb(args):
    """Return (index of the verb, None), or (None, reason) if we should stop.

    A reason of '' means "allow, there is no verb" — bare `git` or an info flag.
    An unknown leading option denies rather than being treated as a verb, so
    `git --wat log` cannot slip a verb past the scan. So does an option whose
    value is missing: whichever reading cut the command there, git's verb lies
    past the cut. Bare `--exec-path` takes no value; it prints and exits. And so
    does a value zsh may make several words, the next of them git's verb.
    """
    i = 0
    while i < len(args):
        token = args[i]
        if token in GIT_INFO_FLAGS:
            return None, ''
        if token in GIT_GLOBAL_FLAGS:
            i += 1
            continue
        if token in GIT_GLOBAL_WITH_VALUE and token != '--exec-path':
            if i + 1 == len(args):
                return None, ('`git ' + token + '` has no value here, so this guard '
                              'cannot see the verb git would run, and it fails '
                              'closed.')
            if args[i + 1].expands:
                return None, _expands_to_words('git ' + token, 'the next of them '
                                               "git's verb")
            i += 2  # the option's value is the next token
            continue
        if token == '--exec-path':
            i += 2  # prints and exits, whatever follows
            continue
        if '=' in token and token.partition('=')[0] in GIT_GLOBAL_WITH_VALUE:
            if token.expands:
                return None, _expands_to_words(token.partition('=')[0] + '=',
                                               "the next of them git's verb")
            i += 1
            continue
        if token.startswith('-'):
            return None, ('`git ' + token + '` is not a recognized read-only git '
                          'global option, and this guard fails closed on options '
                          'it cannot account for.')
        return i, None
    return None, ''  # ran out of tokens: bare `git`, which only prints usage


def _classify_git(args):
    index, reason = _locate_git_verb(args)
    if index is None:
        return reason or None
    verb = args[index]
    rest = args[index + 1:]
    if verb in GIT_READONLY_VERBS:
        return None
    if verb in GIT_SUBCOMMAND_ALLOWED:
        return _classify_git_subcommand_verb(verb, rest)
    if verb in GIT_FLAG_ALLOWED:
        return _classify_git_flag_verb(verb, rest)
    alternative = GIT_ALTERNATIVES.get(verb)
    if alternative:
        return '`git ' + verb + '` is denied by the read-only allowlist. ' + alternative
    return ('`git ' + verb + '` is not on the read-only allowlist — it either mutates '
            'git state or is unrecognized, and this guard fails closed on both.')


def build_denial(agent, command, detail):
    reason = (
        'readonly-agent-guard: the ' + agent + ' agent is read-only on this '
        'checkout — ' + CONTRACT_CLAUSE + '. Denied: ' + repr(command) + '. '
        + detail + ' Report this to your controller rather than retrying with a '
        'variant.'
    )
    return {'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'permissionDecision': 'deny',
        'permissionDecisionReason': reason,
    }}


def main():
    """Always exit 0. A denial is a JSON decision on stdout, not an exit code.

    Fail open before we have identified a guarded agent, fail closed after. A
    uniform posture is wrong in both directions: fail-closed everywhere means one
    malformed payload blocks Bash in every project on this machine, and
    fail-open everywhere means the guard stops guarding exactly when its input
    gets unusual.
    """
    try:
        payload = json.loads(sys.stdin.read())
    except Exception:
        return 0
    if not isinstance(payload, dict):
        return 0

    agent = payload.get(AGENT_TYPE_KEY)
    if not isinstance(agent, str) or agent not in READONLY_AGENTS:
        return 0  # main session, debugger/docs-writer, every built-in agent

    tool_input = payload.get('tool_input')
    command = tool_input.get('command') if isinstance(tool_input, dict) else None
    if not isinstance(command, str) or not command.strip():
        return 0  # no command to classify; there is nothing here to mutate with

    try:
        detail = classify(command)
    except Exception as exc:  # identified agent: fail closed
        detail = ('the guard could not classify this command ('
                  + type(exc).__name__ + ': ' + str(exc) + '), and it fails '
                  'closed for read-only agents.')
    if detail is None:
        return 0

    print(json.dumps(build_denial(agent, command, detail)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
