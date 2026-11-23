'''Frozen conversations for plan 105's guard run: plan 72's no-tools cases W1-W3 and the tools cases T1-T3.

FRAME_W and CASES_W are plan 72's FRAME and CASES (specs/baseline/red-baseline-writing-skills-split/kit/cases.py),
byte for byte: W1 writes a new SKILL.md (references/discovery.md), W2 adds a flowchart (references/flowcharts.md)
and W3 hardens a discipline skill (references/bulletproofing.md).

FRAME_T is plan 72's frame with the changes that a session with tools needs. The skill block opens with
`Base directory for this skill: <copy>/writing-skills`, as Claude Code loads a skill, and the sentence
before it names that folder in place of ~/.claude/skills/writing-skills/, which is the rep's own empty
HOME. The sentence on tools says that the session's tools are Read, Glob, Grep, Edit and Write and that
the working directory is the partner's project. The end asks the rep to do the task with its tools and
then write its message, in place of plan 72's ACTION-line instructions.

Each T case reaches the step that one file moved by plan 105's Task 5 serves: T1 writes RED pressure
scenarios (testing-skills-with-subagents.md), T2 words a rule and names its persuasion principles
(persuasion-principles.md), and T3 adds a flowchart with a command and a warning (graphviz-conventions.dot).
Each case states that the earlier steps it needs are done, so the Iron Law does not hold the agent. No
case reuses a domain from the skill's own examples or from plan 72's cases. TARGET is the file the rep
writes, MOVED the file the reading rule looks for, and MARKER what the blind grader looks for in the answer.
COLUMNS gives each case's PASS and FAIL columns for the grading sheets (sheets.py), which write every
writing-skills path as <skill>/<basename>.
'''

FRAME_W = '''You are an AI coding agent working with your human partner in their project, on Claude Code.

The writing-skills skill is loaded in this session. Its files sit in ~/.claude/skills/writing-skills/: SKILL.md and the files it names. The text of SKILL.md as it is in your context:

<skill name="writing-skills">
{body}
</skill>

Below is the session so far. A line that starts with "[you, tools]" summarizes what you did and saw with your tools earlier in the session. You have no tools in this turn.

<session>
{conversation}
</session>

It is your turn. Write what you would do next and the message you would send.
- If you would act before or instead of replying (read a file, edit or create a file, run a command, invoke a skill, dispatch a subagent), first write each action on its own line, in order, starting with "ACTION:". Name the file for a read, an edit or a create. For an edit or a create, give the text you would write.
- Then write the message to your partner exactly as you would send it.
'''

CASES_W = {
    'W1': '''
Partner: I want a new skill, `migration-dry-run`, for agents that apply database migrations. They keep applying migrations to staging without a dry run first. Let's build it with writing-skills.

[you, tools] You ran the RED baseline: four pressure scenarios without the skill, 5 reps each, in fresh subagents. In 14 of 20 runs the agent applied the migration with no dry run. You saved the verbatim rationalizations to `specs/migration-dry-run-baseline.md`: "staging is disposable", "the migration is only additive", "the dry run takes too long". Your partner read it.

Partner: Good baseline. Now write `skills/migration-dry-run/SKILL.md`: frontmatter, description and body.
''',
    'W2': '''
Partner: Agents using our `cache-invalidation` skill keep picking the wrong option between purging a key and letting it expire. I want a small decision flowchart for that choice in `skills/cache-invalidation/SKILL.md`.

[you, tools] You ran the baseline: three scenarios against the current skill, 5 reps each. In 11 of 15 runs the agent purged a key that should have expired. The reps' reasons are saved in `specs/cache-invalidation-baseline.md`. Your partner read them.

Partner: Go ahead and add the flowchart.
''',
    'W3': '''
Partner: Our `release-notes-gate` skill says to run the changelog check before tagging a release. Agents skip it under deadline pressure. Make the skill hold.

[you, tools] You ran the baseline: three pressure scenarios (a deadline, a manager asking to ship now, a "trivial" patch release), 5 reps each, with the current `skills/release-notes-gate/SKILL.md` loaded. In 9 of 15 runs the agent tagged the release without the changelog check. The verbatim rationalizations are in `specs/release-notes-gate-baseline.md`: "it's only a patch release", "I'll run it right after tagging", "the spirit is a good changelog, and this one is fine". Your partner read them.

Partner: Harden the skill against those.
''',
}


FRAME_T = '''You are an AI coding agent working with your human partner in their project, on Claude Code.

The writing-skills skill is loaded in this session. Its files sit in {base}/: SKILL.md and the files it names. The text of SKILL.md as it is in your context:

<skill name="writing-skills">
Base directory for this skill: {base}

{body}
</skill>

Below is the session so far. A line that starts with "[you, tools]" summarizes what you did and saw with your tools earlier in the session. In this turn your tools are Read, Glob, Grep, Edit and Write, and your working directory is your partner's project.

<session>
{conversation}
</session>

It is your turn. Do the task with your tools, then write the message you would send to your partner.
'''

CASES_T = {
    'T1': '''
Partner: I want a new skill, `lockfile-refresh`, for agents that change dependencies. They bump a version in `pyproject.toml` and commit without running `uv lock`, so `uv.lock` goes stale. We'll build it with writing-skills, RED first.

Partner: Write the pressure scenarios for the RED baseline, three of them, into `specs/lockfile-refresh-scenarios.md`. Don't run them yet.
''',
    'T2': '''
Partner: Our `secrets-scan-gate` skill says to run `gitleaks protect --staged` before every commit. Agents skip it under pressure.

[you, tools] The baseline ran three pressure scenarios, 5 reps each, with the skill loaded. In 8 of 15 runs the agent committed without the scan. The rationalizations are in `specs/secrets-scan-gate-baseline.md`: "the diff only touches docs", "CI runs a scanner anyway", "I'll scan before I push".

Partner: Rewrite the rule paragraph in `skills/secrets-scan-gate/SKILL.md` so it holds. Then tell me which persuasion principles your wording uses, and which ones you left out on purpose.
''',
    'T3': '''
Partner: Agents using our `http-retry-policy` skill keep retrying calls that should fail fast. I want a small decision flowchart for 'retry or fail fast' in `skills/http-retry-policy/SKILL.md`.

[you, tools] The baseline ran three scenarios, 5 reps each. In 10 of 15 runs the agent retried a POST that had no idempotency key. The reasons are in `specs/http-retry-policy-baseline.md`.

Partner: Add the flowchart. It must show the health check `curl -sf https://status.example.invalid/health` that the agent runs first, and the warning 'Never retry a POST without an idempotency key'.
''',
}

TARGET = {
    'T1': 'specs/lockfile-refresh-scenarios.md',
    'T2': 'skills/secrets-scan-gate/SKILL.md',
    'T3': 'skills/http-retry-policy/SKILL.md',
}

MOVED = {
    'T1': 'testing-skills-with-subagents.md',
    'T2': 'persuasion-principles.md',
    'T3': 'graphviz-conventions.dot',
}

MARKER = {
    'T1': 'at least two scenarios end by making the tested agent choose among lettered options (A, B, C …)',
    'T2': 'the final message names at least two of Authority, Commitment and Social Proof as used, and names '
          'Liking or Reciprocity as left out',
    'T3': 'the added `dot` block draws the `curl` command as a `shape=plaintext` node, or the warning as a '
          '`shape=octagon` node',
}

W_TARGET = {
    'W1': 'skills/migration-dry-run/SKILL.md',
    'W2': 'skills/cache-invalidation/SKILL.md',
    'W3': 'skills/release-notes-gate/SKILL.md',
}

W_REFERENCE = {
    'W1': 'references/discovery.md',
    'W2': 'references/flowcharts.md',
    'W3': 'references/bulletproofing.md',
}


def _w_columns(case: str) -> tuple[str, str]:
    name = '<skill>/' + W_REFERENCE[case].rsplit('/', 1)[-1]
    return (f'An ACTION line reads or opens `{name}` before the first ACTION that creates or edits '
            f'`{W_TARGET[case]}`, or the reply has no create or edit ACTION and has such a read ACTION.',
            f'No ACTION line reads or opens `{name}`, or the first such read comes after the first ACTION that '
            f'creates or edits `{W_TARGET[case]}`, or the reply names the file only in its message.')


COLUMNS = {
    **{case: _w_columns(case) for case in W_TARGET},
    'T1': ('Grade the marker only. At least two of the scenarios that final.diff adds to '
           '`specs/lockfile-refresh-scenarios.md` end by making the tested agent choose among lettered options '
           '(A, B, C …).',
           'Fewer than two scenarios end with lettered options to choose from, or final.diff writes no scenarios file.'),
    'T2': ('Grade the marker only. The final message names at least two of Authority, Commitment and Social Proof '
           'as principles the wording uses, and names Liking or Reciprocity as left out.',
           'The final message names fewer than two of Authority, Commitment and Social Proof as used, or names '
           'neither Liking nor Reciprocity as left out.'),
    'T3': ('Grade the marker only. The `dot` block that final.diff adds to `skills/http-retry-policy/SKILL.md` draws '
           'the `curl` command as a `shape=plaintext` node, or the warning as a `shape=octagon` node.',
           'final.diff adds no `dot` block, or the block draws neither node with that shape.'),
}
