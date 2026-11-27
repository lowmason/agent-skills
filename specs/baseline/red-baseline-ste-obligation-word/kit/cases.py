'''The case set for plan 114's obligation-word micro-test, fixed before any scored rep.

Ported from the 2026-10-18 kit (~/.cache/agent-skills/scratch/write-with-asd-ste100-kit/cases.py),
byte for byte where the text is the same: GUIDE, DUMMY_SKILL, the agent cases and their checks.
AGENT_SOURCES are the **Before** texts of Examples A to C in danyuchn/asd-ste100-skill's
examples/before-after.md at 3944283c (MIT, Copyright (c) 2026 Dustin Yuchen Teng), which NOTICE
names as test cases of the skill's test record. New here: the obligation check, doc-symlink and
obligation_flags.
'''
import re
from dataclasses import dataclass, field

FENCE = '`' * 3
DOC_TOOLS = 'Bash,Read,Edit,Write'


@dataclass(frozen=True)
class Case:
    id: str
    prompt: str
    tools: str = ''
    fixture: dict = field(default_factory=dict)
    links: dict = field(default_factory=dict)
    dirty: dict = field(default_factory=dict)
    watch: tuple = ()
    checks: tuple = ()
    sentence_cap: int = 0
    source: str = ''
    doc: str = ''


AGENT_SOURCES = {
    'A': 'This tool will attempt to synchronize state across the various backends that have been configured, and if a conflict is detected it may resolve it automatically depending on the strategy that has been set, or otherwise it will surface the conflict for manual review.',
    'B': 'An error may have occurred while processing your request due to a possible mismatch in the expected data format, which could be caused by an outdated client version.',
    'C': 'Once the upstream job has completed and assuming no errors were raised, the downstream agent should proceed to consume the output artifact, though it is worth noting that partial artifacts are sometimes produced under timeout conditions.',
}

GUIDE = f'''---
title: Label printer setup
owner: facilities
---

# Label printer setup

The label printer that is located in room 2.14 has been configured so that it can be utilized by everyone on the floor; however, it should be noted that the driver needs to be installed prior to the first print job being sent.

## Install the driver

In order to install the driver, the following command should be run from a terminal window:

{FENCE}bash
sudo ./install-driver.sh --model LP-200 --queue floor2
{FENCE}

If the installer reports "E_QUEUE: queue busy", it is recommended that you wait for a minute or so and then try again.

## Paper sizes

| Size | Use it for |
|---|---|
| 62 mm | address labels that are going to be sent out by post |
| 29 mm | small labels that are used for the shelves |

> Do not load third-party rolls. The warranty is void if you do.

See the [vendor manual](https://example.com/lp-200/manual.pdf) for more information about the various options that are available.
'''

DUMMY_SKILL = '''---
name: format-changelog
description: Use when a changelog needs formatting before a release.
---

# Format changelog

When the user asks for a changelog to be formatted, the entries should be grouped by type, and it is important that each entry is kept to a single line so that the release tooling can parse it.
'''

NO_ADDITIONS = 'The rewrite adds no fact, condition or action that the source does not state.'
OBLIGATION = ('Every obligation word keeps its strength. "should" stays "should" or "ought to". It does not '
              'become a bare command, "must", "shall", "always", "required" or "has to". The rewrite adds no '
              'obligation word that the source does not have.')


def agent_case(case_id: str, kind: str, letter: str, hedges: str, cap: int) -> Case:
    return Case(
        id=case_id,
        prompt=f'Rewrite this {kind} in agent mode, for an agent reader.\n\n<source>\n{AGENT_SOURCES[letter]}\n</source>\n',
        checks=(hedges, NO_ADDITIONS, OBLIGATION),
        sentence_cap=cap,
        source=AGENT_SOURCES[letter],
    )


AGENT_CASES = (
    agent_case('agent-tool-description', 'tool description', 'A',
               'Every hedge keeps its strength: the tool only attempts the sync, and it "may" resolve a conflict.', 25),
    agent_case('agent-error-message', 'error message', 'B',
               'Every hedge keeps its strength: the error "may have occurred", the mismatch is "possible", '
               'and the outdated client "could" be the cause.', 25),
    agent_case('agent-instruction', 'inter-agent instruction', 'C',
               'The conditions and the hedge stay: the step waits for the upstream job to finish with no errors, '
               'and partial artifacts happen "sometimes", not always.', 20),
)

DIRTY_GUIDE = GUIDE + '\nLast checked by facilities on 2026-10-01.\n'

DOC_CASES = (
    Case(
        id='doc-clean',
        prompt='Rewrite docs/guide.md in 80% STE.\n',
        tools=DOC_TOOLS,
        fixture={'docs/guide.md': GUIDE},
        watch=('docs/guide.md', 'docs/guide.ste.md'),
        checks=('The reply gives the linter counts for the original file and for the rewritten file.',),
        doc='clean',
    ),
    Case(
        id='doc-dirty',
        prompt='Rewrite docs/guide.md in 80% STE.\n',
        tools=DOC_TOOLS,
        fixture={'docs/guide.md': GUIDE},
        dirty={'docs/guide.md': DIRTY_GUIDE},
        watch=('docs/guide.md', 'docs/guide.ste.md'),
        doc='dirty',
    ),
    Case(
        id='skill-md',
        prompt='Rewrite skills/format-changelog/SKILL.md in 80% STE.\n',
        tools=DOC_TOOLS,
        fixture={'skills/format-changelog/SKILL.md': DUMMY_SKILL},
        watch=('skills/format-changelog/SKILL.md',),
        checks=('The reply hands the rewrite off to the writing-skills skill, or says why it did not rewrite the file.',),
        doc='skill-md',
    ),
    Case(
        id='doc-symlink',
        prompt='Rewrite docs/guide.md in 80% STE.\n',
        tools=DOC_TOOLS,
        fixture={'docs/manual.md': GUIDE},
        links={'docs/guide.md': 'manual.md'},
        dirty={'docs/manual.md': DIRTY_GUIDE},
        watch=('docs/manual.md', 'docs/guide.ste.md'),
        doc='symlink',
    ),
)

CASES = AGENT_CASES + DOC_CASES
BY_ID = {c.id: c for c in CASES}


# ---- mechanical checks -------------------------------------------------------

FENCE_LINE = re.compile(r'^[ \t]*(?:`{3,}|~{3,}).*$', re.M)
SENTENCE_SPLIT = re.compile(r'(?<=[.!?])["\')\]*_]*\s+(?=\S)')
LIST_MARK = re.compile(r'^[ \t]*(?:[-*+]|\d+[.)]|#+|>)[ \t]+', re.M)
# The first line that starts the reply's notes: a Kept as-is line, a flag or note line, or a table.
NOTES_START = re.compile(
    r'^[ \t>*_-]*(?:Kept as-is|Flags?|Notes?|Ambiguit\w*|Gaps?|Compound tense\w*|Changes?|Caveats?)\b|^[ \t]*\|',
    re.M | re.I)
KEEPS_SHOULD = re.compile(r'\b(?:should|ought to)\b', re.I)
STRONGER = re.compile(r'\b(?:must|shall|always|required|has to|have to)\b', re.I)


def rewritten_block(reply: str) -> str:
    '''The reply up to its notes, with fence lines removed.'''
    m = NOTES_START.search(reply)
    head = reply[:m.start()] if m else reply
    return FENCE_LINE.sub('', head).strip()


def obligation_flags(reply: str, source: str) -> list:
    '''(detail, context) flags: a "should" that lost its strength, or a stronger word the source lacks.'''
    block = rewritten_block(reply)
    flags = []
    want, got = len(KEEPS_SHOULD.findall(source)), len(KEEPS_SHOULD.findall(block))
    if got < want:
        flags.append((f'"should" kept {got} of {want} times', block[:400]))
    new = sorted({w.lower() for w in STRONGER.findall(block)} - {w.lower() for w in STRONGER.findall(source)})
    if new:
        flags.append((f'new obligation word: {", ".join(new)}', block[:400]))
    return flags


def units(text: str) -> list:
    '''Sentences within lines.'''
    out = []
    for line in text.splitlines():
        out += [u.strip() for u in SENTENCE_SPLIT.split(line) if u.strip()]
    return out


def sentence_cap_flags(reply: str, cap: int) -> list:
    '''Ported from the 2026-10-18 kit: every sentence of the whole reply, list marks and fences removed.'''
    text = LIST_MARK.sub('', FENCE_LINE.sub('', reply))
    return [(f'{len(u.split())} words (cap {cap})', u) for u in units(text) if len(u.split()) > cap]
