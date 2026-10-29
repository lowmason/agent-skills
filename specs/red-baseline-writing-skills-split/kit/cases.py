'''Frozen conversations for plan 72's micro-tests of the writing-skills split.

Each case reaches the step that one moved reference serves: W1 writes a new SKILL.md
(references/discovery.md), W2 adds a flowchart (references/flowcharts.md), W3 hardens a
discipline skill (references/bulletproofing.md). Each case states that the RED baseline
has run, so the Iron Law does not hold the agent before that step. No case reuses a
domain from the skill's own examples.
'''

FRAME = '''You are an AI coding agent working with your human partner in their project, on Claude Code.

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

CASES = {
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
