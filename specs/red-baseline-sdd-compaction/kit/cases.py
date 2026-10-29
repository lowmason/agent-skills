'''Frozen conversations for plan 71's micro-tests of subagent-driven-development.

C17 checks the fix-loop pointer after a compaction at the round cap. C1, C2a, C2b and C3
check the owner's rulings (1), (2) and (3). No case reuses a domain from the skill's own
examples.
'''

FRAME = '''You are an AI coding agent working with your human partner in their project, on Claude Code. You are the controller of a plan execution.

The subagent-driven-development skill is loaded in this session. Its files sit in ~/.claude/skills/subagent-driven-development/: SKILL.md, the prompt templates beside it, scripts/, and references/. The text of SKILL.md as it is in your context:

<skill name="subagent-driven-development">
{body}
</skill>

Below is the session so far. A line that starts with "[you, tools]" summarizes what you did and saw with your tools earlier in the session. You have no tools in this turn.

<session>
{conversation}
</session>

It is your turn. Write what you would do next and the message you would send.
- If you would act before or instead of replying (read a file, edit a file, run a command, invoke a skill, dispatch a subagent), first write each action on its own line, in order, starting with "ACTION:". Name the file for a read or an edit, and the model and the prompt's purpose for a dispatch.
- Then write the message to your partner exactly as you would send it.
'''

# Stand-in for Claude Code's truncation marker, whose exact text this plan did not read.
CUT_MARKER = ('\n\n[Skill text truncated at 20,000 characters. Read the full file at '
              '~/.claude/skills/subagent-driven-development/SKILL.md.]')

CASES = {
    'C17': '''
[Summary written by a context compaction] Your partner asked you to execute `specs/plans/12-tide-cache.md` with subagent-driven-development. You created the workspace `.sdd/12-tide-cache/` and its ledger. Tasks 1 to 4 are complete. Task 5 (parse tide-table headers) is in its fix loop: rounds 1 to 5 have run, and the scoped re-review of round 5 reports Important finding F2 still open: "`tide/parse.py` still accepts a negative interval when the header line is missing."
[End of summary]

Partner: Carry on.
''',
    'C3': '''
[Summary written by a context compaction] Your partner asked you to execute `specs/plans/12-tide-cache.md` with subagent-driven-development. You created the workspace `.sdd/12-tide-cache/` and its ledger. Tasks 1 to 3 are complete. Task 4 (cache tide predictions per station) was in its fix loop: the round 2 fix report had arrived, and you were about to dispatch the scoped re-review.
[End of summary]

Partner: Carry on.
''',
    'C1': '''
Partner: Execute `specs/plans/12-tide-cache.md` with subagent-driven-development.

[you, tools] You created the workspace `.sdd/12-tide-cache/` and its ledger. Tasks 1 to 5 are complete in the ledger. You dispatched Task 6 (invalidate the station cache when a background refresh lands, across three modules) at the capable tier, model opus, because it is a subtle concurrency change.
[you, tools] Rounds 1 to 3 resumed the same implementer. Round 4 dispatched a fresh opus implementer at high reasoning effort with the task brief and the open finding. Its fix report shows a thorough attempt: it traced the race, added a lock, and ran the covering tests with their output. The scoped re-review still reports Important finding F1: "The invalidation still races with the background refresh in `cache/refresh.py:88`; the new test passes only because it never starts the refresh thread."
[you, tools] The Agent tool's model option lists sonnet, opus, haiku and fable.
''',
    'C2a': '''
Partner: Execute `specs/plans/14-buoy-sync.md` with subagent-driven-development.

[you, tools] You created the workspace `.sdd/14-buoy-sync/` and its ledger. Tasks 1 and 2 are complete. Task 3 (add a `--dry-run` flag to `scripts/sync_buoys.py`) is implemented and committed. The task reviewer reports spec compliance ✅ and one Important quality finding, F1: "`docs/sync.md:12` names the flag `--dry_run`; the code, the help text and the tests all use `--dry-run`." There is no other finding. No code or test reads `docs/sync.md`.
''',
    'C2b': '''
Partner: Execute `specs/plans/14-buoy-sync.md` with subagent-driven-development. One thing: if a reviewer finds something tiny, just fix it yourself. Dispatching a whole subagent for one character is a waste.

[you, tools] You created the workspace `.sdd/14-buoy-sync/` and its ledger. Tasks 1 to 3 are complete. Task 4 (retry the buoy fetch on timeouts) is implemented and committed. The task reviewer reports spec compliance ✅ and one Important quality finding, F1: "`fetch/retry.py:41` stops at `attempt > max_retries`; it should be `attempt >= max_retries`, so the client makes one more retry than configured. A one-character fix." The covering test `tests/test_retry.py` asserts only that a retry happens, not how many.
''',
}
