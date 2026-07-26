#!/usr/bin/env python3
'''Advisory decoupling check for methodology descriptions.

Flags code-coupled tokens in a methodology markdown file:
  - multi-token identifiers: snake_case with >=2 tokens, camelCase
  - backticked code-font tokens (unless a single plain word or Greek name)
  - file paths (a slash-joined token with an identifier-flavored segment)
  - dotted call syntax (numpyro.factor(...), az.compare(...))

Never flags single dictionary words or Greek-letter names — house Bayesian
style names sample sites sigma/mu/beta, and the notation table's own content
must survive. Symbols defined in the description's notation table (first
column of any table under a heading containing 'Notation') are whitelisted.

Known misses, accepted: single-word call syntax ('estimate(x)') is not
flagged (prose parentheticals like 'weight(s)' would false-positive);
capitalized distribution notation (N(0,1), LogNormal(0,1)) is exempt by
design; URLs in citations may flag as paths — they are review input too.

ADVISORY ONLY: output is review input, never a fix-until-clean gate.
The CLI always exits 0.

Run: python3 check_decoupling.py <methodology.md>
'''
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

GREEK = {
    'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta',
    'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'omicron', 'pi', 'rho',
    'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega',
    # LaTeX variant spellings and the script-l, once \-stripped
    'varepsilon', 'vartheta', 'varkappa', 'varpi', 'varrho', 'varsigma',
    'varphi', 'ell',
}
SNAKE_RE = re.compile(r'\b[A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+\b')
CAMEL_RE = re.compile(r'\b[a-z][a-z0-9]*[A-Z][A-Za-z0-9]*\b')
BACKTICK_RE = re.compile(r'`([^`\n]+)`')
PATH_RE = re.compile(r'(?<![\w/])[\w.-]+(?:/[\w.-]+)+')
DOTTED_CALL_RE = re.compile(r'\b[a-z_][\w]*(?:\.[\w]+)+\s*\(')
WORD_RE = re.compile(r'[A-Za-z]+')
HEADING_RE = re.compile(r'^#+\s+(.*)$')
TABLE_SEP_CHARS = {'-', ':', ' ', '|'}
LATEX_DECORATION_RE = re.compile(
    r'\\(?:mathrm|mathbf|mathcal|mathbb|mathsf|text|operatorname|bar|hat|tilde'
    r'|widehat|widetilde|overline|underline|vec|dot|ddot)\s*'
)
SYMBOL_SPLIT_RE = re.compile(r'[\s,;^]+')


@dataclass(frozen=True)
class Finding:
    line: int
    token: str
    category: str


def _symbol_tokens(cell: str) -> list[str]:
    '''Plain-text symbol tokens from one notation-table cell.

    Descriptions are written in LaTeX ($\\sigma_p$, $\\bar{h}_t$), so a cell
    is normalized to the token forms that appear in prose before it can
    whitelist anything: decorations are dropped, symbol commands keep their
    name, and multi-symbol cells ("$A_k$, $B_k$") split into one token each.
    Normalizing here — rather than at the point of use — keeps the harvest
    whitelist and the suspicious_notation counter-check reading the same
    set, so a LaTeX-dressed identifier cannot slip past the counter-check.
    '''
    s = cell.strip().strip('`$ ').strip()
    s = LATEX_DECORATION_RE.sub('', s)
    s = s.replace('\\,', ' ').replace('\\;', ' ').replace('\\quad', ' ')
    s = s.replace('\\', '').replace('{', '').replace('}', '')
    s = s.replace('$', ' ').replace('`', ' ')
    return [tok for tok in SYMBOL_SPLIT_RE.split(s) if tok]


def notation_whitelist(text: str) -> set[str]:
    '''Symbols from the first column of tables under a Notation heading.'''
    symbols: set[str] = set()
    in_notation = False
    for raw in text.split('\n'):
        heading = HEADING_RE.match(raw)
        if heading:
            in_notation = 'notation' in heading.group(1).lower()
            continue
        line = raw.strip()
        if in_notation and line.startswith('|'):
            first = line.strip('|').split('|', 1)[0].strip().strip('`$ ')
            if first and not set(first) <= TABLE_SEP_CHARS:
                symbols.update(_symbol_tokens(first))
    return symbols


def _pathlike(token: str) -> bool:
    '''Identifier-flavored paths only — "and/or" stays clean.'''
    return any(c in seg for seg in token.split('/') for c in '._-')


SUBSCRIPT_BASE_MAX = 2  # y_t, g_cont: a 1-2 char base reads as a math subscript


def suspicious_notation(whitelist: set[str] | frozenset[str]) -> list[str]:
    '''Whitelist entries shaped like code identifiers, not notation.

    A notation-table symbol is exempt when it reads as math: single plain
    words, Greek-based names (sigma_obs), short-base subscripts (y_t,
    g_cont). Everything identifier-shaped — camelCase, dotted, path-like,
    or snake_case with a >=3-char non-Greek base — is reported, so a
    smuggled identifier cannot hide by being "defined" in the table.
    '''
    out: list[str] = []
    for sym in sorted(whitelist):
        if CAMEL_RE.fullmatch(sym) or '.' in sym or '/' in sym:
            out.append(sym)
            continue
        if SNAKE_RE.fullmatch(sym):
            base = sym.split('_', 1)[0]
            if len(base) > SUBSCRIPT_BASE_MAX and base.lower() not in GREEK:
                out.append(sym)
    return out


def harvest(
    text: str, whitelist: set[str] | frozenset[str] = frozenset(),
) -> list[Finding]:
    findings: list[Finding] = []
    for lineno, line in enumerate(text.split('\n'), 1):
        flagged: set[str] = set()

        def add(token: str, category: str) -> None:
            if token in whitelist or token in flagged:
                return
            flagged.add(token)
            findings.append(Finding(lineno, token, category))

        for m in SNAKE_RE.finditer(line):
            add(m.group(0), 'snake_case')
        for m in CAMEL_RE.finditer(line):
            add(m.group(0), 'camelCase')
        for m in PATH_RE.finditer(line):
            if _pathlike(m.group(0)):
                add(m.group(0), 'path')
        for m in DOTTED_CALL_RE.finditer(line):
            add(m.group(0).rstrip('( \t'), 'call')
        for m in BACKTICK_RE.finditer(line):
            token = m.group(1).strip()
            if token.lower() in GREEK or WORD_RE.fullmatch(token):
                continue
            add(token, 'backtick')
    return findings


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print('usage: check_decoupling.py <methodology.md>')
        return 0
    text = Path(argv[1]).read_text()
    whitelist = notation_whitelist(text)
    findings = harvest(text, whitelist)
    for f in findings:
        print(f'{argv[1]}:{f.line}: [{f.category}] {f.token}')
    suspicious = suspicious_notation(whitelist)
    for sym in suspicious:
        print(
            f'{argv[1]}: [notation-table] {sym} — defined as a symbol '
            'but shaped like a code identifier'
        )
    print(
        f'ADVISORY: {len(findings)} code-coupling candidate(s), '
        f'{len(suspicious)} identifier-shaped notation symbol(s) — '
        'review input, not a gate.'
    )
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
