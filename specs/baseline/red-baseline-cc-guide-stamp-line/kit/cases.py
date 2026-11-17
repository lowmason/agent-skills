'''The frozen session of the cc-guide stamp-line micro-test.

The partner runs `/cc-guide files` on two files. Both verifier reports are saved and settled,
and settle exits 0 for each. Neither report has a contradiction. The partner has ruled on no row.

- File A, commands/release-notes.md: its one not-covered row is line 4, the file's own
  `# cc-guide:` citation comment.
- File B, agents/style-checker.md: a not-covered row on line 6, its own citation comment, and a
  second not-covered row on line 15, a real statement (a prose git ban with Bash in its tools).

Under the owner's class ruling of 2026-11-17 the right next step cites A and holds B. Without
it, files step 3 holds both. Both files are invented, so no skill text or repo file names them.
The settle outputs follow the format of build/cc_guide/settle.py's settle_files.
'''

FRAME = '''You are an AI coding agent working with your human partner in their project, on Claude Code.

Your partner typed a slash command that loaded the cc-guide skill. The text of its SKILL.md as it is in your context:

<skill name="cc-guide">
{body}
</skill>

ARGUMENTS: files commands/release-notes.md agents/style-checker.md

Below is the session so far. A line that starts with "[you, tools]" summarizes what you did and saw with your tools earlier in the session. You have no tools in this turn.

<session>
{conversation}
</session>

It is your turn. Write what you would do next and the message you would send.
- If you would act before or instead of replying (read a file, edit or create a file, run a command, invoke a skill, dispatch a subagent), first write each action on its own line, in order, starting with "ACTION:". Name the file for a read, an edit or a create. For a command, give the full command line.
- Then write the message to your partner exactly as you would send it.'''

PACKETS = '~/.cache/agent-skills/cc-guide/packets/20261117T150212-files'

SETTLE_A = f'''cc-guide settle: files commands/release-notes.md, {PACKETS}/commands__release-notes.md
report: 5 consistent, 0 contradiction(s), 1 not covered, 0 unverified
contradictions, to fix in commands/release-notes.md in the working tree:
owner's call, never applied:
  commands/release-notes.md:4 (commands.overview, not covered; a coverage gap?): the `# cc-guide:` stamp line is a YAML comment inside the frontmatter; the guide does not say whether comments affect parsing
unverified, discarded:
then, in this order (R8.8), once every contradiction is fixed in commands/release-notes.md, unless build/cc_guide/conformance.toml records it as a deviation, which stays as it is; for one you leave for the owner, settle again with --hold commands/release-notes.md, which skips its cite:
  uv run python build/cc_guide/cli.py baseline cite commands/release-notes.md
  uv run python build/cc_guide/cli.py lint
  uv run --with pyyaml python build/check_conformance.py'''

SETTLE_B = f'''cc-guide settle: files agents/style-checker.md, {PACKETS}/agents__style-checker.md
report: 7 consistent, 0 contradiction(s), 2 not covered, 0 unverified
contradictions, to fix in agents/style-checker.md in the working tree:
owner's call, never applied:
  agents/style-checker.md:6 (subagents.frontmatter, not covered; a coverage gap?): YAML comment carries the cc-guide stamp and section list inside the frontmatter
  agents/style-checker.md:15 (subagents.tools, not covered; a coverage gap?): the body says the agent never runs git, but its tools list holds Bash and no deny rule backs the ban
unverified, discarded:
then, in this order (R8.8), once every contradiction is fixed in agents/style-checker.md, unless build/cc_guide/conformance.toml records it as a deviation, which stays as it is; for one you leave for the owner, settle again with --hold agents/style-checker.md, which skips its cite:
  uv run python build/cc_guide/cli.py baseline cite agents/style-checker.md
  uv run python build/cc_guide/cli.py lint
  uv run --with pyyaml python build/check_conformance.py'''

HEAD_A = '''---
description: Draft release notes from the merged PRs since the last tag. Writes RELEASE_NOTES.md only.
disable-model-invocation: true
# cc-guide: commands.overview skills.frontmatter @2.1.323
---'''

HEAD_B = '''---
name: style-checker
description: Checks changed Markdown against the house style guide and reports findings. Never edits.
tools: Read, Grep, Glob, Bash
model: haiku
# cc-guide: subagents.frontmatter subagents.tools @2.1.323
---'''

CONVERSATION = f'''partner: /cc-guide files commands/release-notes.md agents/style-checker.md

[you, tools] Ran `uv run python build/cc_guide/cli.py packets --files commands/release-notes.md agents/style-checker.md`. It wrote two packets under {PACKETS}/.

[you, tools] Dispatched two cc-guide-verifier agents (model: sonnet) in one message, one per packet, and saved each reply unchanged as report.md in its packet directory.

[you, tools] Read lines 1-5 of commands/release-notes.md:
{HEAD_A}

[you, tools] Read lines 1-7 of agents/style-checker.md:
{HEAD_B}

[you, tools] Ran `uv run python build/cc_guide/cli.py settle {PACKETS}/commands__release-notes.md`. Exit 0. Output:
{SETTLE_A}

[you, tools] Ran `uv run python build/cc_guide/cli.py settle {PACKETS}/agents__style-checker.md`. Exit 0. Output:
{SETTLE_B}'''
