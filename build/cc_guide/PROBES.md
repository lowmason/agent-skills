# Probe log

One row per probe run, appended by `cli.py probes` (drift spec R10.6), newest last.
Nothing commits it for you: review the rows, then commit them. Each run keeps its raw
output under `~/.cache/agent-skills/cc-guide/probes/`.

| Date | Version | Binary | Probe | Outcome | Finding | Flags |
|---|---|---|---|---|---|---|
| 2026-10-20 | 2.1.304 | ~/.cache/agent-skills/scratch/plan58-bin/broken-claude | agent-tools | ERROR | the agent with Bash: no stream-json events |  |
| 2026-10-20 | 2.1.304 | ~/.cache/agent-skills/scratch/plan58-bin/claude | guard-liveness | PASS | git status passed; git fetch and git config --global were denied |  |
| 2026-10-20 | 2.1.304 | ~/.cache/agent-skills/scratch/plan58-bin/claude | agent-tools | PASS | with Bash: Bash, Read; without Bash: Glob, Grep, Read |  |
| 2026-10-20 | 2.1.304 | ~/.cache/agent-skills/scratch/plan58-bin/claude | stop-continuation | PASS | stop_hook_active read false, true, true |  |
| 2026-10-20 | 2.1.304 | ~/.cache/agent-skills/scratch/plan58-bin/claude | agent-model-pins | PASS | Explore and test-runner served claude-haiku-5-5; code-reviewer effort xhigh |  |
| 2026-10-28 | 2.1.308 | ~/Library/Application Support/Claude/claude-code/2.1.308/a93ded4b1b47/claude.app/Contents/MacOS/claude | agent-payload | PASS | dispatches reach PreToolUse as Agent, with no model when unset; claude-code-guide served claude-haiku-5-5, as the haiku control was | --allow-old |
