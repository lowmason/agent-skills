'''The offline lint behind `versions.py check`, the repo's tenth commit lint.

It fails on four things (design: specs/package-versions.md, R4):
  sync       an output of `versions.py sync` differs from build/versions.toml;
  literals   a live file spells an interpreter flag with a version, where uv reads .python-version;
  citations  skills/**/*.md and the script headers under skills/*/scripts/ state a version next to a
             package name that the file lists, or next to "Python", and the file disagrees;
  floors     a script's requires-python is above the Python floor its SKILL.md promises, or above the dev Python.

A citation has one of three forms. Equality ("Polars 1.42", numpyro==0.22.0) must equal the file's
value at the cited precision. A range (>=, >, <, 3.11+, "or later", ,<0.18) must contain the file's
value. History passes only when its phrase is a key of HISTORICAL. The lint sees only the package
names that the file lists.
'''
import re
import subprocess
from collections.abc import Iterable, Mapping
from pathlib import Path

import versions
from run_suites import git_env
from versions import Versions, compare, normalize, version_tuple

# Keyed by the literal phrase, not by file and line, so a prose edit does not break an entry.
# Each entry gives its reason, as DOCUMENTED_ABSENT does in check_snippets.py.
HISTORICAL: dict[str, str] = {
    'ArviZ 0.23': 'the classic stack, named so the porting tables can map from it to ArviZ 1',
    'arviz-stats < 1.0.0': 'the releases that have no azs.diagnose, which the fallback in diagnostics.md is for',
}
LIVE_FILES = ('CLAUDE.md', 'AGENTS.md', 'GEMINI.md')
LIVE_DIRS = ('build/', 'hooks/', 'skills/', '.claude/skills/')
INTERPRETER_RE = re.compile(r'--python[ =]3\.\d+')
OPS = r'(?:==|>=|<=|~=|!=|>|<|≥|≤)'
VERSION = r'\d+(?:\.\d+)*'
SCRIPT_FLOOR_RE = re.compile(r'''requires-python\s*=\s*['"]>=\s*(\d+\.\d+)''')
COMPAT_FLOOR_RE = re.compile(r'Python\s*(?:≥\s*)?(\d+\.\d+)\s*(?:\+|or\s+later)', re.I)


def skipped(path: Path) -> bool:
    '''Data directories, test fixtures and license files are not read (design R4.3).'''
    return bool({'data', 'fixtures'} & set(path.parts)) or path.name.startswith('LICENSE')


def live_files(root: Path) -> list[Path]:
    '''The tracked and untracked-but-not-ignored files that the interpreter-literal rule reads.'''
    listing = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
                             cwd=root, env=git_env(), capture_output=True, check=True).stdout
    paths = [entry.decode() for entry in listing.split(b'\0') if entry]
    return [root / p for p in paths
            if (p in LIVE_FILES or p.startswith(LIVE_DIRS)) and (root / p).is_file() and not skipped(Path(p))]


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        return None


def check_literals(root: Path, files: Iterable[Path]) -> list[str]:
    findings = []
    for path in files:
        text = read_text(path)
        for number, line in enumerate((text or '').splitlines(), start=1):
            for match in INTERPRETER_RE.finditer(line):
                findings.append(f'{path.relative_to(root)}:{number}: {match.group(0)!r} spells an interpreter; '
                                'drop the flag, since uv reads .python-version (written from build/versions.toml)')
    return findings


def citation_regex(names: Iterable[str]) -> re.Pattern:
    alternatives = '|'.join(re.escape(name).replace(r'\-', '[-_ ]')
                            for name in sorted(names, key=len, reverse=True))
    return re.compile(
        rf'(?<![\w.-])(?P<name>{alternatives})(?![\w-])[*`]*(?:\s*(?P<op>{OPS})\s*|\s+v?)(?P<ver>{VERSION})'
        rf'(?P<plus>\+|\s+or\s+(?:later|newer|above))?(?:\s*,\s*(?P<ub><)\s*(?P<ubver>{VERSION}))?',
        re.I)


def current_versions(v: Versions) -> dict[str, str]:
    current = {normalize(name): version for table in (v.packages, v.cited) for name, version in table.items()}
    current['python'] = v.dev_python
    return current


def judge(current: str, match: re.Match) -> str | None:
    '''Why the file's value disagrees with one citation, or None.'''
    op, ver, plus = match.group('op') or '', match.group('ver'), match.group('plus')
    if op == '!=':
        return None
    if op in ('>=', '≥', '~=') or plus:
        ok, kind = compare(current, ver) >= 0, 'range'
    elif op == '>':
        ok, kind = compare(current, ver) > 0, 'range'
    elif op == '<':
        ok, kind = compare(current, ver) < 0, 'range'
    elif op in ('<=', '≤'):
        ok, kind = compare(current, ver) <= 0, 'range'
    else:
        cited = version_tuple(ver)
        have = (version_tuple(current) + (0,) * len(cited))[:len(cited)]
        ok, kind = cited == have, 'equality'
    if ok and match.group('ub'):
        ok, kind = compare(current, match.group('ubver')) < 0, 'range'
    if ok:
        return None
    if kind == 'range':
        return f'the file says {current}, outside this range'
    return (f'the file says {current}; re-check the claim on {current} and update the text, '
            'or add the phrase to HISTORICAL in build/versions_check.py with a reason')


def header_text(text: str) -> str:
    '''The PEP 723 block of a script, one line per line so numbers stay true; other lines blank.'''
    out, inside = [], False
    for line in text.splitlines():
        if line.strip() == '# /// script':
            inside = True
        elif inside and line.strip() == '# ///':
            inside = False
        out.append(line[2:] if inside and line.startswith('# ') else '')
    return '\n'.join(out)


def check_citations(root: Path, v: Versions, historical: Mapping[str, str] = HISTORICAL) -> list[str]:
    current = current_versions(v)
    pattern = citation_regex([*v.packages, *v.cited, 'Python'])
    sources = [path for path in sorted((root / 'skills').glob('**/*.md')) + sorted((root / 'skills').glob('*/scripts/*.py'))
               if not skipped(path.relative_to(root))]
    lowered = {key.lower(): key for key in historical}
    findings, used = [], set()
    for path in sources:
        text = read_text(path)
        if text is None:
            continue
        if path.suffix == '.py':
            if path.name.startswith('test_'):
                continue
            text = header_text(text)
        for match in pattern.finditer(text):
            phrase = re.sub(r'\s+', ' ', re.sub(r'[*`]', '', match.group(0))).strip()
            if phrase.lower() in lowered:
                used.add(lowered[phrase.lower()])
                continue
            name = normalize(re.sub(r'\s+', '-', match.group('name')))
            problem = judge(current[name], match)
            if problem:
                number = text.count('\n', 0, match.start()) + 1
                findings.append(f'{path.relative_to(root)}:{number}: {phrase!r}: {problem}')
    findings += [f'HISTORICAL entry {phrase!r} matches no text under skills/; remove it'
                 for phrase in historical if phrase not in used]
    return findings


def compat_floor(skill_md: str) -> str | None:
    '''The Python floor in the `compatibility:` value of a SKILL.md frontmatter, or None.'''
    block = re.match(r'---\n(.*?)\n---', skill_md, re.S)
    if not block:
        return None
    value = re.search(r'^compatibility:(.*?)(?=^\S|\Z)', block.group(1) + '\n', re.S | re.M)
    found = COMPAT_FLOOR_RE.search(value.group(1)) if value else None
    return found.group(1) if found else None


def check_floors(root: Path, v: Versions) -> list[str]:
    findings = []
    for skill in sorted(p for p in (root / 'skills').iterdir() if (p / 'SKILL.md').is_file()):
        promised = compat_floor(read_text(skill / 'SKILL.md') or '')
        if promised and compare(promised, v.dev_python) > 0:
            findings.append(f'{skill.relative_to(root)}/SKILL.md: promises Python {promised}, above the dev Python '
                            f'{v.dev_python}')
        for script in sorted((skill / 'scripts').glob('*.py')):
            found = SCRIPT_FLOOR_RE.search(read_text(script) or '')
            if not found:
                continue
            floor = found.group(1)
            where = script.relative_to(root)
            if compare(floor, v.dev_python) > 0:
                findings.append(f'{where}: requires Python {floor}, above the dev Python {v.dev_python}')
            if promised and compare(floor, promised) > 0:
                findings.append(f'{where}: requires Python {floor}, but SKILL.md promises {promised}')
    return findings


def check(root: Path = versions.REPO, historical: Mapping[str, str] | None = None) -> list[str]:
    historical = HISTORICAL if historical is None else historical
    try:
        v = versions.load(root)
    except versions.VersionsError as exc:
        return [str(exc)]
    return (versions.sync(root, check=True) + check_literals(root, live_files(root))
            + check_citations(root, v, historical) + check_floors(root, v))
