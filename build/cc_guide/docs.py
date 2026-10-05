'''The docs sources around the block pages: release labels, the changelog,
llms.txt, and the file and URL of each mapped page (drift spec R2.4, R6.5,
R6.6, Layout).

A mapped page is a code.claude.com slug such as `hooks` or
`plugins/components`, or a platform slug written `platform:<slug>`.
'''
import re
from datetime import date, datetime
from typing import NamedTuple

CHANGELOG = 'changelog.md'
LLMS = 'llms.txt'
PLATFORM = 'platform:'

LABEL_RE = re.compile(r'^\d+(?:\.\d+)+$')
UPDATE_RE = re.compile(r'^<Update label="([^"]*)" description="([^"]*)">\s*$')
BULLET_RE = re.compile(r'^\s*\* (.*)$')
LLMS_RE = re.compile(r'\(https://code\.claude\.com/docs/en/([^)\s]+)\.md\)')


def version_key(label: str) -> tuple[int, ...]:
    '''R2.4: versions compare as integer tuples, so 2.1.288.1 sorts after
    2.1.288 and before 2.1.289.'''
    if not LABEL_RE.match(label):
        raise ValueError(f'not a release label: {label!r}')
    return tuple(int(part) for part in label.split('.'))


class Release(NamedTuple):
    label: str
    date: date
    bullets: list[str]


def parse_changelog(text: str) -> list[Release]:
    '''R6.6: the changelog's <Update label="X" description="Month D, YYYY">
    blocks with their `* ` bullets, newest first by version. Raises
    ValueError on an unparseable label or date, an <Update> tag it cannot
    read, or a repeated label.'''
    releases: list[Release] = []
    current: Release | None = None
    for n, line in enumerate(text.split('\n'), start=1):
        m = UPDATE_RE.match(line)
        if m:
            label, described = m.groups()
            try:
                version_key(label)
                when = datetime.strptime(described, '%B %d, %Y').date()
            except ValueError as exc:
                raise ValueError(f'changelog line {n}: {exc}') from None
            current = Release(label, when, [])
            releases.append(current)
        elif line.lstrip().startswith('<Update'):
            raise ValueError(f'changelog line {n}: unrecognized <Update> tag')
        elif line.strip() == '</Update>':
            current = None
        elif current is not None and (b := BULLET_RE.match(line)):
            current.bullets.append(b.group(1).strip())
    labels = [r.label for r in releases]
    if len(set(labels)) != len(labels):
        raise ValueError('changelog repeats a release label')
    return sorted(releases, key=lambda r: version_key(r.label), reverse=True)


def parse_llms(text: str) -> set[str]:
    '''R6.5: the code.claude.com page slugs llms.txt lists.'''
    return set(LLMS_RE.findall(text))


def is_platform(page: str) -> bool:
    return page.startswith(PLATFORM)


def page_file(page: str) -> str:
    '''The cache file a mapped page lives in: `/` becomes `_`, and platform
    pages take a `platform_` prefix, as in the 2.1.288 snapshot.'''
    if is_platform(page):
        return 'platform_' + page[len(PLATFORM):].replace('/', '_') + '.md'
    return page.replace('/', '_') + '.md'


def page_url(page: str, sources: dict[str, str]) -> str:
    '''The Markdown URL the refresh fetched a mapped page from.'''
    if is_platform(page):
        return sources['platform_base'] + page[len(PLATFORM):] + '.md'
    return sources['docs_base'] + page + '.md'
