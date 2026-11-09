'''The statement-readings probe's six copies (plan 83): plan 81's three plants, each with one defense
line (PD1), two specs with one sentence edited to allow two readings (PD2), and plan 55 unchanged.

A replacement is (old, new, count): `old` occurs exactly `count` times in the source plan.
A true pattern is a regex for a line that still states the spec's value. A keep entry is
(line_text, reason): a line that matches a true pattern but states another value.
A defense is (anchor, line): the line goes in after the one plan line that starts with the anchor.
The spec and plant tokens (PD10) are flattened forms that the scorer looks for in a statement's slots.
AMENDED_LINES are the source-spec lines that each plan's own amendment tasks change (PD3).
'''
from dataclasses import dataclass


@dataclass(frozen=True)
class Plant:
    kind: str
    spec_key: str
    planted_tokens: tuple[str, ...]
    replacements: tuple[tuple[str, str, int], ...]
    true_patterns: tuple[str, ...]
    keep: tuple[tuple[str, str], ...]
    defense: tuple[str, str]
    spec_tokens: tuple[str, ...]
    plant_tokens: tuple[str, ...]


@dataclass(frozen=True)
class TwoReading:
    spec_key: str
    edit: tuple[str, str]
    slot: str
    reading_a: str
    reading_b: str
    plan_lines: tuple[int, ...]
    a_tokens: tuple[str, ...]
    b_tokens: tuple[str, ...]
    deciders: tuple[str, ...]


@dataclass(frozen=True)
class Copy:
    id: str
    commit: str
    spec_path: str
    plan_path: str
    plant: Plant | None
    spec_id: str
    two: TwoReading | None


# Portability R1.3: compatibility is "a string of 1–500 characters after stripping".
# Planted as 500 UTF-8 bytes.
P53_UNIT = Plant(
    kind='unit',
    spec_key='a string of 1–500 characters after stripping',
    planted_tokens=('bytes', "encode('utf-8')"),
    replacements=(
        ('"a string of 1–500 characters after stripping"', '"a string of 1–500 UTF-8 bytes after stripping"', 1),
        ('# The spec caps compatibility at 500 characters.', '# The spec caps compatibility at 500 UTF-8 bytes.', 5),
        ('test_compatibility_must_be_a_string_of_1_to_500_characters',
         'test_compatibility_must_be_a_string_of_1_to_500_bytes', 1),
        ('# Portability R1.3, both edges: 500 passes, 501 and a blank value fail.',
         '# Portability R1.3, both edges: 500 bytes pass, 501 bytes and a blank value fail.', 1),
        ('string of 1-500 characters', 'string of 1-500 bytes', 4),
        ('of 1 to COMPATIBILITY_CAP characters.', 'of 1 to COMPATIBILITY_CAP UTF-8 bytes.', 1),
        ('1-{COMPATIBILITY_CAP} characters', '1-{COMPATIBILITY_CAP} bytes', 1),
        ('len(compat.strip())', "len(compat.strip().encode('utf-8'))", 1),
    ),
    true_patterns=(r'500 characters', r'1[-–]500 characters', r'COMPATIBILITY_CAP\}? characters',
                   r'len\(compat\.strip\(\)\)', r'1_to_500_characters'),
    keep=(
        ('Keep under 500 characters if possible',
         "upstream skill-creator's description guidance quoted as a text anchor, not R1.3"),
    ),
    defense=('  - R4.1: copies are "regular files',
             "- R1.3's cap guards a stored field, so the lint measures the stripped value in UTF-8 bytes: "
             'a non-ASCII value can stay within 500 code points and still overflow a 500-byte field.'),
    spec_tokens=('character',),
    plant_tokens=('byte',),
)

# Package versions R2.1: the cutoff is "00:00:00Z on the day after the freeze date", and "Files
# uploaded on the freeze date itself (UTC) are included". Planted as 00:00:00Z on the freeze date.
P66_BOUND = Plant(
    kind='bound',
    spec_key='00:00:00Z on the day after the freeze date',
    planted_tokens=('2026-10-19T00:00:00Z', '2026-12-31T00:00:00Z', '2026-11-02T00:00:00Z',
                    '2026-10-18T23:59:59', '00:00:00Z on the freeze date', '{self.freeze:%Y-%m-%d}'),
    replacements=(
        ('**Freeze date** is the day after which uv ignores new package releases.',
         '**Freeze date** is the day from which uv ignores new package releases.', 1),
        ('The **cutoff** is its uv form: 00:00:00Z on the day after the freeze date.',
         'The **cutoff** is its uv form: 00:00:00Z on the freeze date.', 1),
        ('00:00:00Z on the day after the freeze date (R2.1)', '00:00:00Z on the freeze date (R2.1)', 1),
        ('test_cutoff_is_midnight_utc_on_the_day_after_the_freeze_date',
         'test_cutoff_is_midnight_utc_on_the_freeze_date', 1),
        ("cutoff == '2026-10-20T00:00:00Z'", "cutoff == '2026-10-19T00:00:00Z'", 1),
        ("cutoff == '2027-01-01T00:00:00Z'", "cutoff == '2026-12-31T00:00:00Z'", 1),
        ('exclude-newer = "2026-10-20T00:00:00Z"', 'exclude-newer = "2026-10-19T00:00:00Z"', 1),
        ("'''00:00:00Z on the day after the freeze date, so the freeze day itself is included.'''",
         "'''00:00:00Z on the freeze date, so uv resolves as of the start of that day.'''", 1),
        ('{self.freeze + datetime.timedelta(days=1):%Y-%m-%d}', '{self.freeze:%Y-%m-%d}', 1),
        ('as of this cutoff: 00:00:00Z on the day after\\n', 'as of this cutoff: 00:00:00Z on the freeze\\n', 1),
        ("f'# the freeze date, {v.freeze.isoformat()}, so files uploaded on the freeze date itself are included.\\n'",
         "f'# date, {v.freeze.isoformat()}, so files uploaded before the freeze date are included.\\n'", 1),
        ('2026-11-03T00:00:00Z', '2026-11-02T00:00:00Z', 4),
        ('<day after freeze>T00:00:00Z', '<freeze date>T00:00:00Z', 1),
        ("fake_pypi('2026-10-19T23:59:59.000000Z')", "fake_pypi('2026-10-18T23:59:59.000000Z')", 1),
        ("'--exclude-newer', '2026-10-20T00:00:00Z',\n", "'--exclude-newer', '2026-10-19T00:00:00Z',\n", 2),
        ("'--exclude-newer', '2026-10-20T00:00:00Z', 'python', 'y.py']",
         "'--exclude-newer', '2026-10-19T00:00:00Z', 'python', 'y.py']", 1),
    ),
    true_patterns=(r'day after (the )?freeze', r'freeze (day|date) itself', r'timedelta\(days=1\)',
                   r'2026-10-20T00:00:00Z', r'2027-01-01T00:00:00Z', r'2026-11-03T00:00:00Z',
                   r'2026-10-19T23:59:59'),
    keep=(
        ("'--exclude-newer', '2026-10-20T00:00:00Z', '--with', 'jax'",
         "Task 1's probe P1 pins its own fixed cutoff for jax; no freeze date derives it"),
    ),
    defense=('- **Freeze.**',
             '- The cutoff falls at the start of the freeze date, so every `bump` or `verify` run on that date '
             'resolves the same files, however late in the day it runs.'),
    spec_tokens=('day after', 'next day', 'following day', '+1 day', '+ 1 day'),
    plant_tokens=('00:00:00z on the freeze date', 'start of the freeze date'),
)

# Test-suite registry R2.2: `pythons` "Default `['3.13']`". Planted as ['3.12'].
P55_DEFAULT = Plant(
    kind='default',
    spec_key="Default `['3.13']`",
    planted_tokens=('3.12',),
    replacements=(
        ("DEFAULT_PYTHONS = ('3.13',)", "DEFAULT_PYTHONS = ('3.12',)", 2),
        ("(default ['3.13'])", "(default ['3.12'])", 1),
        ("'alpha (3.13)'", "'alpha (3.12)'", 4),
        ("'== alpha (3.13)'", "'== alpha (3.12)'", 1),
        ("'outer (3.13)'", "'outer (3.12)'", 1),
        ("'ghost (3.13): cannot start'", "'ghost (3.12): cannot start'", 1),
        ('build (3.13)', 'build (3.12)', 3),
        ("('uv', 'run', '--python', '3.13', '--with', 'pytest', '--with', 'polars',",
         "('uv', 'run', '--python', '3.12', '--with', 'pytest', '--with', 'polars',", 2),
        ('cd skills/alpha/scripts && uv run --python 3.13', 'cd skills/alpha/scripts && uv run --python 3.12', 3),
    ),
    true_patterns=(r"DEFAULT_PYTHONS = \('3\.13',\)", r"default \['3\.13'\]", r'\b(alpha|outer|ghost|build) \(3\.13\)',
                   r'cd skills/alpha/scripts && uv run --python 3\.13',
                   r"'--python', '3\.13', '--with', 'pytest', '--with', 'polars'"),
    keep=(),
    defense=('- **Shell forms (R3.2):**',
             '- A suite with no `pythons` key runs on 3.12, the oldest Python that every suite still supports, '
             'so the default run keeps that floor tested.'),
    spec_tokens=('3.13',),
    plant_tokens=('3.12',),
)

# Package versions R3.1, the `bump` row (spec :202). The plan reads today's date in UTC (reading A).
P66_TODAY = TwoReading(
    spec_key='Sets the freeze date (default: today)',
    edit=('(default: today, UTC)', '(default: today)'),
    slot='default',
    reading_a="Today's date in UTC",
    reading_b="Today's date in the local time zone of the machine that runs `bump`",
    plan_lines=(1258, 1263, 1357),
    a_tokens=('utc',),
    b_tokens=('local',),
    deciders=(r'today,? \(?utc', r'utc (date|day)'),
)

# Test-suite registry R4.3 (spec :172). The plan's `--check` exits 1 on a finding (reading A).
P55_EXIT = TwoReading(
    spec_key='one line per finding and an error exit',
    edit=('one line per finding and exit 1.', 'one line per finding and an error exit.'),
    slot='value',
    reading_a='Exit 1',
    reading_b=('Exit 2, the status that R3.7 gives "a usage error, an unknown suite name, or a registry that '
               'fails validation"'),
    plan_lines=(807, 827),
    a_tokens=('1',),
    b_tokens=('2',),
    deciders=(r'--check[^.]*exit [12]', r'finding[^.]*exit [12]'),
)

# PD3: the source-spec lines that each plan's amendment tasks change, as (first, last), 1-based.
AMENDED_LINES: dict[str, tuple[tuple[int, int], ...]] = {
    'p53': ((104, 104), (159, 159), (181, 182), (192, 192), (203, 203), (238, 240), (268, 270), (276, 277),
            (371, 377), (394, 394), (401, 402), (419, 419)),
    'p55': ((83, 83), (98, 98), (144, 145), (186, 186)),
    'p66': ((94, 95), (138, 148), (182, 182)),
}

P53_SPEC, P53_PLAN = 'specs/agent-skills-portability-spec.md', 'specs/plans/53-agent-skills-portability.md'
P66_SPEC, P66_PLAN = 'specs/package-versions.md', 'specs/plans/66-package-versions.md'
P55_SPEC, P55_PLAN = 'specs/test-suite-registry.md', 'specs/plans/55-test-suite-registry.md'

COPIES = (
    Copy('p53-unit', 'b8f4d0f', P53_SPEC, P53_PLAN, P53_UNIT, 'p53', None),
    Copy('p66-bound', '526b7de', P66_SPEC, P66_PLAN, P66_BOUND, 'p66', None),
    Copy('p55-default', 'f0ebef6', P55_SPEC, P55_PLAN, P55_DEFAULT, 'p55', None),
    Copy('p55-clean', 'f0ebef6', P55_SPEC, P55_PLAN, None, 'p55', None),
    Copy('p66-today', '526b7de', P66_SPEC, P66_PLAN, None, 'p66-today', P66_TODAY),
    Copy('p55-exit', 'f0ebef6', P55_SPEC, P55_PLAN, None, 'p55-exit', P55_EXIT),
)


def source_id(copy: Copy) -> str:
    '''The source plan's key in AMENDED_LINES: `p53`, `p55` or `p66`.'''
    return copy.spec_id.split('-')[0]
