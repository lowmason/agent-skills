'''Read the user's identity forms at run time, for the kit's scrub and its privacy sweep.

The values come from local config only: `git config --global user.name` and `user.email`, $USER,
and the login account's `emailAddress`, `fullName` and `displayName` in ~/.claude.json
(`oauthAccount`). They live in memory. Nothing here writes a value to a file or prints one.

The forms, each matched without regard to case and only where no letter or digit touches it:
- each email address, as `<USER-EMAIL>`;
- each address's local part (the text before `@`), as `<USER-EMAIL-LOCAL>`;
- each full name, as `<USER-NAME>`;
- each part of a name or of a local part (split on blanks, `.`, `_`, `-` and `+`), as `<USER-NAME>`;
- $USER, as `$USER`.
A value shorter than three characters is left out. Longer values are replaced first, and a value
met twice keeps its first token.
'''
import json
import os
import re
import subprocess
from pathlib import Path

MIN_LENGTH = 3
EMAIL = '<USER-EMAIL>'
LOCAL = '<USER-EMAIL-LOCAL>'
NAME = '<USER-NAME>'
USER = '$USER'
PART_SPLIT = re.compile(r'[\s._+\-]+')


def _git(key: str) -> str:
    result = subprocess.run(['git', 'config', '--global', key], capture_output=True, text=True)
    return result.stdout.strip()


def _account() -> dict:
    try:
        return json.loads((Path.home() / '.claude.json').read_text()).get('oauthAccount') or {}
    except (OSError, ValueError):
        return {}


def forms() -> list[tuple[str, str]]:
    '''Return (value, token) pairs, longest value first. The values are private: never print them.'''
    account = _account()
    emails = [_git('user.email'), account.get('emailAddress') or '']
    names = [_git('user.name'), account.get('fullName') or '', account.get('displayName') or '']
    locals_ = [email.split('@', 1)[0] for email in emails if '@' in email]
    pairs = [(email, EMAIL) for email in emails] + [(local, LOCAL) for local in locals_]
    pairs += [(name, NAME) for name in names]
    pairs += [(part, NAME) for value in names + locals_ for part in PART_SPLIT.split(value)]
    pairs.append((os.environ.get('USER', ''), USER))
    chosen = {}
    for value, token in pairs:
        value = value.strip()
        if len(value) >= MIN_LENGTH and value.lower() not in chosen:
            chosen[value.lower()] = (value, token)
    return sorted(chosen.values(), key=lambda pair: -len(pair[0]))


def pattern(value: str) -> re.Pattern:
    return re.compile(rf'(?<![A-Za-z0-9]){re.escape(value)}(?![A-Za-z0-9])', re.I)


def scrub(text: str, pairs: list[tuple[str, str]] | None = None) -> str:
    for value, token in forms() if pairs is None else pairs:
        text = pattern(value).sub(token, text)
    return text
