#!/usr/bin/env python3
# cc-guide: hooks.events hooks.exit-codes hooks.patterns @2.1.306
"""PreToolUse(Agent) guard: an agent dispatch names its model.

subagent-driven-development's Model Selection says an omitted model is never a
tier choice: an unpinned agent inherits the session's model, usually the most
expensive one. This hook denies an Agent call with no `model`, except for the
model-pinned agents in PINNED_AGENTS, for the built-in agents in BUILTIN_PINNED
that pin their own model, and for `fork`, which ignores `model`. Unknown types,
plugin agents included, must name a model.

build/check_frontmatter.py asserts PINNED_AGENTS against the agents/*.md files
that set `model:`, in both directions, so drift fails the lint at commit time.
BUILTIN_PINNED is kept apart for that reason: no agents/*.md backs it. Plan 63's
probe (Claude Code 2.1.304) saw claude-code-guide run on Haiku with no model
passed; Plan and statusline-setup ran on the session model, so they stay out.

Runs under whatever `python3` is first on PATH (3.9 on macOS system Python), so
stdlib only and 3.9-compatible. An unreadable payload is allowed: this guard
must never break a call it cannot read.
"""
from __future__ import annotations

import json
import sys

PINNED_AGENTS = frozenset({
    'code-reviewer',
    'debugger',
    'docs-writer',
    'Explore',
    'security-auditor',
    'task-reviewer',
    'test-runner',
})
BUILTIN_PINNED = frozenset({'claude-code-guide'})
UNPINNABLE = frozenset({'fork'})
AGENT_TOOL = 'Agent'
MARKER = 'dispatch-model-guard:'


def decide(payload: dict) -> str | None:
    """Return a deny reason, or None to allow.

    A `tool_input` that is not a dict is unreadable, so the call is allowed. A
    `subagent_type` that is not a non-empty string counts as missing, so it is
    read as `general-purpose` and a model-less call is denied.
    """
    if payload.get('tool_name') != AGENT_TOOL:
        return None
    tool_input = payload.get('tool_input', {})
    if not isinstance(tool_input, dict):
        return None
    if tool_input.get('model'):
        return None
    kind = tool_input.get('subagent_type')
    if not isinstance(kind, str) or not kind:
        kind = 'general-purpose'
    if kind in PINNED_AGENTS or kind in BUILTIN_PINNED or kind in UNPINNABLE:
        return None
    return (f'{MARKER} name the model for this {kind!r} dispatch: pass model '
            "'haiku', 'sonnet' or 'opus' per subagent-driven-development's "
            'Model Selection. An omitted model inherits the session model.')


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    if not isinstance(payload, dict):
        return 0
    reason = decide(payload)
    if reason:
        json.dump({'hookSpecificOutput': {'hookEventName': 'PreToolUse',
                                          'permissionDecision': 'deny',
                                          'permissionDecisionReason': reason}}, sys.stdout)
    return 0


if __name__ == '__main__':
    sys.exit(main())
