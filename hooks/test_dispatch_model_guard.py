# cc-guide: hooks.events hooks.exit-codes hooks.patterns @2.1.306
"""Contract tests for dispatch-model-guard.py: run from hooks/, both ways.

cd hooks
uv run --python 3.13 --with pytest python -m pytest -q test_dispatch_model_guard.py
uv run --python /usr/bin/python3 --with pytest python -m pytest -q test_dispatch_model_guard.py

A crashed PreToolUse hook exits 1, which fails open, so every allow-path test
asserts the return code as well as the empty stdout.
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parent / 'dispatch-model-guard.py'
_spec = importlib.util.spec_from_file_location('dispatch_model_guard', HOOK)
guard = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(guard)


def run(payload):
    return subprocess.run([str(HOOK)], input=json.dumps(payload), capture_output=True, text=True)


def agent(subagent_type, model=None):
    tool_input = {'description': 'd', 'prompt': 'p', 'subagent_type': subagent_type}
    if model is not None:
        tool_input['model'] = model
    return {'hook_event_name': 'PreToolUse', 'tool_name': 'Agent', 'tool_input': tool_input}


def assert_denied(result):
    assert result.returncode == 0
    out = json.loads(result.stdout)['hookSpecificOutput']
    assert out['permissionDecision'] == 'deny'
    assert out['permissionDecisionReason'].startswith(guard.MARKER)


def assert_allowed(result):
    assert result.returncode == 0, result.stderr
    assert result.stdout == ''


def test_unpinned_agent_without_model_is_denied():
    assert_denied(run(agent('general-purpose')))


def test_unpinned_agent_with_empty_model_is_denied():
    assert_denied(run(agent('general-purpose', model='')))


def test_unpinned_agent_with_model_is_allowed():
    assert_allowed(run(agent('general-purpose', model='sonnet')))


@pytest.mark.parametrize('name', sorted(guard.PINNED_AGENTS))
def test_pinned_agent_without_model_is_allowed(name):
    assert_allowed(run(agent(name)))


def test_builtin_pinned_agent_without_model_is_allowed():
    # The plan 63 probe saw claude-code-guide run on Haiku with no model passed,
    # not on the session model, so the owner exempted it.
    assert_allowed(run(agent('claude-code-guide')))


def test_fork_without_model_is_allowed():
    assert_allowed(run(agent('fork')))


def test_missing_subagent_type_without_model_is_denied():
    payload = agent('general-purpose')
    del payload['tool_input']['subagent_type']
    assert_denied(run(payload))


def test_plugin_agent_without_model_is_denied():
    assert_denied(run(agent('code-simplifier:code-simplifier')))


def test_other_tool_is_allowed():
    assert_allowed(run({'hook_event_name': 'PreToolUse', 'tool_name': 'Bash',
                        'tool_input': {'command': 'ls'}}))


def test_unreadable_payload_is_allowed():
    result = subprocess.run([str(HOOK)], input='not json', capture_output=True, text=True)
    assert_allowed(result)


def test_reason_names_the_fix():
    reason = guard.decide(agent('general-purpose'))
    assert 'model' in reason and 'haiku' in reason and 'sonnet' in reason and 'opus' in reason


@pytest.mark.parametrize('tool_input', [[1], 'x', 7, None])
def test_non_dict_tool_input_is_allowed(tool_input):
    assert_allowed(run({'hook_event_name': 'PreToolUse', 'tool_name': 'Agent',
                        'tool_input': tool_input}))


@pytest.mark.parametrize('kind', [['a'], 7, {'a': 1}])
def test_non_string_subagent_type_without_model_is_denied(kind):
    assert_denied(run(agent(kind)))


@pytest.mark.parametrize('kind', [['a'], 7, {'a': 1}])
def test_non_string_subagent_type_with_model_is_allowed(kind):
    assert_allowed(run(agent(kind, model='sonnet')))
