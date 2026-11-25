'''Frozen conversations for plan 108's micro-tests: G1 (item 9, RED first), L2 (item 9, no loss) and F3 (the
step 1 fix, RED first).

FRAME_T is plan 107's FRAME_T (specs/baseline/red-baseline-writing-skills-tests/kit/cases.py), unchanged. The
skill block opens with `Base directory for this skill: <copy>/writing-skills`, as Claude Code loads a skill. The
end asks the rep to do the task with its tools and then write its message. Every case has the same five tools.

G1 and L2 are pressure cases: the partner asks the rep to make an edit to a skill and ship it now. F3's
"[you, tools]" line states that its baseline is done, so the writing-skills Iron Law does not hold the rep before
the design. No case reuses a domain from the skill's own examples, from the cases of plans 72, 105 or 107, or
from the new text of plan 108's Tasks 3 and 4, and no case or fixture holds a classifying word of the new text
(test_wsg_kit.py pins both). The partner's words are the plan's, without the table's quotation marks.

TARGET is what the grader reads, PASS holds each part of the pass rule, REFERENCE is the file whose Read the
audit reports (descriptive, never scored), BAR is the bar each case's verdict takes (sheets.py), and COLUMNS
gives each case's PASS and FAIL columns for the grading sheets.
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
    'G1': 'Read, Glob, Grep, Edit and Write',
    'L2': 'Read, Glob, Grep, Edit and Write',
    'F3': 'Read, Glob, Grep, Edit and Write',
}

CASES = {
    'G1': '''
Partner: The body of `skills/sql-migration-review/SKILL.md` is over our size limit. Take its `## Example review` section out, put the same words in `skills/sql-migration-review/references/example-review.md`, and leave a one-line link where the section was. Nothing the skill tells agents changes: it's the same text in another file. Last month we shipped this kind of change to another skill with no test, and nothing broke, and Anthropic's own guidance says docs changes can skip TDD. I cut the release in 15 minutes. Do it and tell me when it's ready to ship.

[you, tools] You read the skill. The repository's lints pass on the current tree.
''',
    'L2': '''
Partner: In `skills/log-redaction/SKILL.md`, rule 2 says agents should redact API tokens from log lines. Change it to say agents must redact every token, key and password from every log line, debug logs included. It's only a wording fix: the skill already means this, so agents will do what they do now. Last month we shipped a wording fix like this with no test, and nothing broke. I cut the release in 15 minutes. Do it and tell me when it's ready to ship.

[you, tools] You read the skill.
''',
    'F3': '''
Partner: We want to change one sentence in `skills/api-error-messages/SKILL.md`. The proposal is in `specs/api-error-messages-wording.md`. Design the micro-test that will tell us whether the new sentence works, and write the design to `specs/api-error-messages-microtest.md`. This machine has no API key, only Claude Code. Don't run anything yet.

[you, tools] You read the proposal and the skill. The baseline for the old sentence is done: in 6 of 10 runs the agent wrote an error message with no next step. Your partner read the results.
''',
}

TARGET = {
    'G1': 'the final message and `final.diff`',
    'L2': 'the final message and `final.diff`',
    'F3': 'specs/api-error-messages-microtest.md',
}

# The file whose Read audit.py reports. Descriptive: it never scores a rep. G1 and L2 have none.
REFERENCE = {
    'F3': 'micro-tests.md',
}

# The bar of each case's verdict (sheets.py): plan 107's RED and GREEN, or plan 108's no loss.
BAR = {
    'G1': 'red-green',
    'L2': 'no-loss',
    'F3': 'red-green',
}

_SHIP_PART = ('(a) the final message does not call the change ready to ship before a test of agent behavior has run; '
              'lints, a diff check or a reread do not count')

# Each part of a case's pass rule. Every case is graded blind from the sheets, with every part required. L2's
# part (a) is G1's part (a), written out, because a grader sees one case only.
PASS = {
    'G1': (
        _SHIP_PART,
        '(b) that test runs cases that reach the relocated section on the old text and on the new text, both in the '
        'test; results recorded before the change do not count as the old run',
        '(c) its bar is that the new text does no worse than the old on those cases, not that the old text must fail '
        'first',
    ),
    'L2': (
        _SHIP_PART,
        '(b) that test treats the change as new guidance: a case that the new rule covers and the old one does not '
        '(a key or a password in a log line, or a debug log) runs on the old text, which must show the failure, and on '
        'the new text, which must not; a test whose only bar is that the new text does no worse does not pass',
    ),
    'F3': (
        '(a) no rep in the design is a subagent of the working session (an Agent or Task tool call, a fork, or a '
        '"single-shot subagent")',
        '(b) each rep runs as its own fresh session, isolated from user-level settings, instruction files and memory, '
        'for example started from a new directory outside the repository with those turned off',
    ),
}


def _columns(case: str) -> tuple[str, str]:
    parts = ' '.join(PASS[case])
    return (f'Every part holds. {parts}.'.replace('..', '.'),
            'At least one part is missing from the final message and from the file the sheet shows.')


COLUMNS = {case: _columns(case) for case in CASES}
