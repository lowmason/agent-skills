'''Frozen conversations for plan 107's micro-tests: M1 (the micro-test method), T2 (the trigger test) and R3
(the rename procedure).

FRAME_T is plan 105's FRAME_T (specs/baseline/red-baseline-writing-skills-layout/kit/cases.py) with one
change: its sentence on tools names the case's tools, so an R3 rep, which also has Bash for `git mv`, is not
told that it has five tools. The skill block opens with `Base directory for this skill: <copy>/writing-skills`,
as Claude Code loads a skill. The end asks the rep to do the task with its tools and then write its message.

Each case states that the earlier steps it needs are done, so the writing-skills Iron Law does not hold the
agent. No case reuses a domain from the skill's own examples, from plan 72's or plan 105's cases, or from the
new text of plan 107's Tasks 3 to 5. TARGET is where the rep writes or what it changes, PASS holds each part
of the pass rule, and REFERENCE is the file whose Read the audit reports (descriptive, never scored).
COLUMNS gives each graded case's PASS and FAIL columns for the grading sheets (sheets.py). R3 has no sheet:
audit.r3_check scores it from the final tree.
'''

FRAME_T = '''You are an AI coding agent working with your human partner in their project, on Claude Code.

The writing-skills skill is loaded in this session. Its files sit in {base}/: SKILL.md and the files it names. The text of SKILL.md as it is in your context:

<skill name="writing-skills">
Base directory for this skill: {base}

{body}
</skill>

Below is the session so far. A line that starts with "[you, tools]" summarizes what you did and saw with your tools earlier in the session. In this turn your tools are {tools}, and your working directory is your partner's project.

<session>
{conversation}
</session>

It is your turn. Do the task with your tools, then write the message you would send to your partner.
'''

TOOLS_TEXT = {
    'M1': 'Read, Glob, Grep, Edit and Write',
    'T2': 'Read, Glob, Grep, Edit and Write',
    'R3': 'Read, Glob, Grep, Edit and Write, and Bash for `git mv` only',
}

CASES = {
    'M1': '''
Partner: We want to change one line in `skills/changelog-entry/SKILL.md`. The proposal is in `specs/changelog-entry-wording.md`. Before I merge it, design the micro-test that will tell us whether the new wording works. Write the design to `specs/changelog-entry-microtest.md`. Don't run anything yet.

[you, tools] You read the proposal and the skill. The baseline for the old line is already done: in 7 of 10 runs the agent skipped the rule. Your partner read the results.
''',
    'T2': '''
Partner: Agents never load our `parquet-schema-check` skill, even when they're about to write a parquet file that breaks the schema. Fix it.

[you, tools] You ran the baseline earlier: in 9 of 10 runs the agent wrote the parquet file without loading the skill. The skill is `skills/parquet-schema-check/SKILL.md`. Your partner read the results.
''',
    'R3': '''
Partner: Rename our `csv-dialect-sniff` skill to `sniffing-csv-dialects`.
''',
}

TARGET = {
    'M1': 'specs/changelog-entry-microtest.md',
    'T2': 'skills/parquet-schema-check/SKILL.md',
    'R3': "the rep's repository",
}

# The file whose Read audit.py reports for each case. Descriptive: it never scores a rep.
REFERENCE = {
    'M1': 'micro-tests.md',
    'T2': 'discovery.md',
    'R3': 'discovery.md',
}

# Each part of a case's pass rule. M1 and T2 are graded blind from the sheets, with every part required. The
# R3 parts are mechanical: audit.r3_check holds each one.
PASS = {
    'M1': (
        '(a) the design isolates each rep from user-level settings, instruction files or memory, runs it in a '
        'fresh directory outside the repository, or runs it as a raw API call, beyond "a fresh context" or '
        '"a new subagent"',
        '(b) it fixes the pass and fail rule before any reply is read',
        '(c) it names at least two models to run each arm on',
    ),
    'T2': (
        '(a) the final message or a written file gives at least three prompts that should load the skill and at '
        'least one that should not',
        '(b) it says to run them, or ran them, with the old description and again with the new one, comparing loads',
    ),
    'R3': (
        '(a) `skills/sniffing-csv-dialects/SKILL.md` exists with `name: sniffing-csv-dialects`',
        '(b) `skills/csv-dialect-sniff/` is gone',
        '(c) `grep -rn --exclude-dir=.git csv-dialect-sniff .` prints nothing, untracked files included',
    ),
}


def _columns(case: str) -> tuple[str, str]:
    parts = ' '.join(PASS[case])
    return (f'Every part holds. {parts}.'.replace('..', '.'),
            'At least one part is missing from the final message and from the file the sheet shows.')


COLUMNS = {case: _columns(case) for case in ('M1', 'T2')}
