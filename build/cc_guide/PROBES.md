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
| 2026-11-10 | 2.1.317 | ~/Library/Application Support/Claude/claude-code/2.1.317/91184d3d9ba3/claude.app/Contents/MacOS/claude | compaction-cut | DIVERGES | compaction keeps 19741 body characters of the prose probe skill (by characters; 159 characters before the body), fewer than the register window 20000, so a body that passes compaction-window can lose its last 259 | --allow-old |
| 2026-11-11 | 2.1.317 | ~/Library/Application Support/Claude/claude-code/2.1.317/91184d3d9ba3/claude.app/Contents/MacOS/claude | compaction-cut | PASS | compaction kept 19741 body characters of the prose probe skill (by characters; 159 characters before the body), at least the register window 19700 | --allow-old |
| 2026-11-12 | 2.1.323 | ~/.local/bin/claude | guard-liveness | PASS | git status passed; git fetch and git config --global were denied |  |
| 2026-11-12 | 2.1.323 | ~/.local/bin/claude | agent-tools | PASS | with Bash: Bash, Read; without Bash: Glob, Grep, Read |  |
| 2026-11-12 | 2.1.323 | ~/.local/bin/claude | stop-continuation | PASS | stop_hook_active read false, true, true |  |
| 2026-11-12 | 2.1.323 | ~/.local/bin/claude | agent-model-pins | PASS | Explore and test-runner served claude-haiku-5-5; code-reviewer effort xhigh |  |
| 2026-11-12 | 2.1.323 | ~/.local/bin/claude | agent-payload | PASS | dispatches reach PreToolUse as Agent, with no model when unset; claude-code-guide served claude-haiku-5-5, as the haiku control was |  |
