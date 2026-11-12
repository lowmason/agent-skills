'''The four frozen conversations of plan 92's micro-tests of writing-skills against the Claude Code guide.

R1 asks for a new skill with a long inline table and one hard rule (RED and GREEN for "critical
rules first"). P1 sets a key only Claude Code reads, P2 asks why a skill stopped triggering, P3
asks to fork a skill that dispatches subagents. Each case states that its RED baseline ran, so
the Iron Law does not hold the agent before the step. No case reuses a domain from
writing-skills' own examples or from plan 72's cases.
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

READ = '''[you, tools] You read ~/.claude/skills/writing-skills/{path}. Its full text:
<file path="~/.claude/skills/writing-skills/{path}">
{text}
</file>'''

CONVERSATIONS = {
    'R1': '''
Partner: I want a new skill, `tenant-export`, for support agents who export one customer's data from our multi-tenant store with the `vaultctl export` command. It must carry three things.
1. The export workflow:
   1. Open the ticket and copy the tenant ID.
   2. Confirm that the requester is an admin of that tenant.
   3. Check the tenant's export quota with `vaultctl quota`.
   4. Run `vaultctl export --tenant <tenant-id> --out export.tar`.
   5. Compare the row count with the tenant dashboard.
   6. Encrypt the archive with the ticket's public key.
   7. Upload it to the ticket's secure share.
   8. Note the export ID on the ticket.
   9. Delete the local copy.
2. The full `vaultctl` error-code table: 180 codes, each with its cause and its fix. It is about 24,000 characters; we measured it. It stays in SKILL.md, because this skill also ships as a single-file prompt to a tool that reads only one file. Where the table goes, write the line `[VAULTCTL ERROR TABLE]` alone on its line, and I'll paste the table there.
3. One hard rule: never run `vaultctl export` without `--tenant`. Without it, the command exports every tenant's data.

[you, tools] You ran the RED baseline: three scenarios without the skill, 5 reps each, in fresh subagents. In 11 of 15 runs the agent ran `vaultctl export` without `--tenant`; it did not know the flag mattered. You saved the runs to `specs/tenant-export-baseline.md`. Your partner read them.

Partner: Good. Write `skills/tenant-export/SKILL.md` now: frontmatter, description and the whole body, with the table line where you want the table. Put the full file text in your reply.
''',
    'P1': '''
Partner: Our `refund-issue` skill issues customer refunds through the billing API. Two things. Claude must never start a refund on its own: the skill should run only when one of us types /refund-issue. And our `support-desk` subagent preloads `refund-issue` through its `skills:` list, so that it can issue refunds inside a delegated support flow. Keep that working.

[you, tools] You read `skills/refund-issue/SKILL.md`. Its frontmatter today has `name: refund-issue`, `description: Use when a customer's refund request is approved and the refund must be issued through the billing API.` and `license: MIT`, and no other key. Your partner confirmed its RED baseline: in 4 of 5 runs, an agent started a refund on its own while it answered a billing question.

Partner: Make the change.
''',
    'P2': '''
Partner: We have about 150 skills installed now, most of them from three plugins. `/doctor` warns about the skill listing. Our `api-naming` skill stopped triggering on its own last week. It still runs when I type /api-naming, and nobody changed its description. What's going on, and what should we change?

[you, tools] You read `skills/api-naming/SKILL.md`. Its description is 410 characters long and starts with "Use when naming a new REST endpoint".
''',
    'P3': '''
Partner: Our `dependency-audit` skill dispatches three reviewer subagents (licenses, known CVEs, version pins) and merges their findings into one report. Its output floods the main conversation, so set it to `context: fork`. We run it nightly from `claude -p` in CI, and sometimes by hand in the terminal.

[you, tools] You read `skills/dependency-audit/SKILL.md`. Its frontmatter has `name`, `description` and `license`, and no `context` key. Your partner confirmed its RED baseline: in 5 of 5 runs, the report filled the main conversation.

Partner: Make the change.
''',
}

DISCOVERY = 'references/discovery.md'
BOTH = [DISCOVERY, 'references/claude-code.md']
PROMPTS = {
    'R1': ('R1', {'base': [DISCOVERY], 'new': BOTH}),
    'P1r': ('P1', {'new': [DISCOVERY]}),
    'P2r': ('P2', {'new': [DISCOVERY]}),
    'P3r': ('P3', {'new': [DISCOVERY]}),
    'P1a': ('P1', {'base': [DISCOVERY], 'new': BOTH}),
    'P2a': ('P2', {'base': [DISCOVERY], 'new': BOTH}),
    'P3a': ('P3', {'base': [DISCOVERY], 'new': BOTH}),
}
