'''The probe's four plan copies and the one misread planted in each (plan 81, DF1 and DF2).

A replacement is (old, new, count): `old` occurs exactly `count` times in the source plan.
A true pattern is a regex for a line that still states the spec's value. A keep entry is
(line_text, reason): a line that matches a true pattern but states another value.
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


@dataclass(frozen=True)
class Copy:
    id: str
    commit: str
    spec_path: str
    plan_path: str
    plant: Plant | None


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
)

COPIES = (
    Copy('p53-unit', 'b8f4d0f', 'specs/agent-skills-portability-spec.md',
         'specs/plans/53-agent-skills-portability.md', P53_UNIT),
    Copy('p66-bound', '526b7de', 'specs/package-versions.md', 'specs/plans/66-package-versions.md', P66_BOUND),
    Copy('p55-default', 'f0ebef6', 'specs/test-suite-registry.md', 'specs/plans/55-test-suite-registry.md',
         P55_DEFAULT),
    Copy('p55-clean', 'f0ebef6', 'specs/test-suite-registry.md', 'specs/plans/55-test-suite-registry.md', None),
)
