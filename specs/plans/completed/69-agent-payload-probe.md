# Agent Payload Probe Implementation Plan

**Status: COMPLETE (2026-10-28)** — executed via subagent-driven-development; deferred items in specs/deferred_items.md

> **For agentic workers:** REQUIRED SUB-SKILL: implement this plan task-by-task via subagent-driven-development (the default) — or executing-plans when your human partner chose inline execution at the handoff. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a live drift probe, `agent-payload`, that fails when Claude Code changes what `hooks/dispatch-model-guard.py` relies on: the dispatch tool's name, the payload's model field, the `Agent` matcher, or a built-in agent's model pin.

**Architecture:** The probe follows the four existing probes in `build/cc_guide/`. `probes.py` prepares a scratch directory whose project settings hold two logging `PreToolUse` hooks (matchers `*` and `Agent`), and runs one `claude -p` parent on Sonnet. The parent dispatches a `general-purpose` control that passes `model: "haiku"` and each built-in in the guard's `BUILTIN_PINNED` with no model. `collect` cuts the logged payloads to a scrub-free `payloads.json`. A pure assertion in `probe_checks.py` reads that file and the stream's forwarded messages. The last task registers the probe, records one live run behind an owner gate, and commits its scrubbed fixtures.

**Tech Stack:** Python 3.13 (dev Python in `build/versions.toml`), stdlib only, pytest; bash for the logging hook; Claude Code `claude -p` with stream-json.

**Spec:** none. This is `/deferred` step 5's **Plan** disposition (2026-10-28): the deferred item below is the requirements. Background: `specs/plans/completed/63-conformance-gaps.md` Task 6 (the hook and its probe), `specs/completed/claude-code-drift-automation-spec.md` R10 and R12.6 (probes and fixtures), and `specs/plans/completed/58-claude-code-drift-automation.md` (the probe code's design and decisions D1–D7).

## Requirements

The deferred item, verbatim, from `specs/deferred_items.md` section `63-conformance-gaps — 2026-10-21`:

> Probe `BUILTIN_PINNED` and the Agent payload shape in the drift detector (plan 63 Task 6, review
> Minor, triaged defer). `hooks/dispatch-model-guard.py` relies on `tool_name` `Agent`, with
> `tool_input.model` absent when unset, and on `BUILTIN_PINNED` (built-in `claude-code-guide` pins
> haiku). Add a probe beside `agent-model-pins` in `build/cc_guide/manifest.toml`, and a Probe-log
> row in `hooks/README.md` with the Task 6 findings (CC 2.1.304, 2026-10-21). If CC renamed the
> tool, the matcher would stop firing and the guard would fail open without a sign. See
> `specs/plans/completed/63-conformance-gaps.md`. Size: plan. Done when: the probe runs and
> fails when a built-in's pin or the payload shape changes.

"Fails" means a non-PASS row (DIVERGES or ERROR), which makes `cli.py probes` exit 1 and keeps the probe due until a later PASS (R10.6).

The Task 6 findings, from the plan 63 kit's `t6-probe.md` (scratch folder `~/.cache/agent-skills/scratch/plan63-micro/`, Claude Code 2.1.304, 2026-10-21):

- An agent dispatch reaches `PreToolUse` with `tool_name` `Agent`. The type is at `tool_input.subagent_type` and the model at `tool_input.model`. An unset model is absent, not an empty string.
- A call made inside a subagent also carries top-level `agent_id` and `agent_type`.
- With no model passed, `claude-code-guide` ran on `claude-haiku-5-5`. `general-purpose`, `Plan` and `statusline-setup` ran on the session model (`claude-sonnet-5-5`).
- The stream carried each subagent's messages with `parent_tool_use_id` and `message.model`.

## Owner review (defaults this plan settles; change any at plan review)

- **O1. The probe's guide sections.** Default: `hooks.events`, `hooks.configuration`, `hooks.patterns`, `subagents.models`. The first and third are the hook's own citations, the second holds the matcher rules, and the fourth holds built-in agents' models. A DIVERGES row sends all four to `/cc-guide verify`.
- **O2. What counts as "unset" for the model field.** Default: mirror the guard's `decide()`, which reads `tool_input.get('model')`. An absent, empty or null model passes. Any value is DIVERGES, since the guard would then let a model-less dispatch of any type through. Alternative: fail on any `model` key at all, to match the item's word "absent".
- **O3. Scope.** Default: dispatch only the `BUILTIN_PINNED` members and one control. A new pin on `Plan` or `statusline-setup` would make the guard deny calls it need not deny. That failure is loud, not silent, so the probe does not dispatch them.

## Global Constraints

- Python style: single quotes, f-strings, 4-space indentation, stdlib only in `probes.py` and `probe_checks.py`, target the dev Python in `build/versions.toml` (3.13).
- Tests are directory-scoped. Run them through `uv run python build/run_suites.py <suite> [-- <pytest args>]` from the repo root, never through a repo-root pytest.
- Every commit passes `build/run_commit_lints.sh` (the pre-commit hook runs it once the owner has enabled `core.hooksPath`; run it by hand before each commit either way).
- Do not edit `specs/deferred_items.md` before the Plan Completion Protocol. Another session may be editing it, so re-read it just before the ticking pass.
- Leave these alone. They belong to open deferred items (see Related open items): `SCRUBBED_ENV`, `execute`, `claude_args`, `scrub_events`, `_trim_event`, `_trim_block`, `save_fixtures`, `run_probe`, the four existing probes and their tests and fixtures, and `explore_ids` in `test_probe_replay.py`.
- Leave these alone too: `hooks/dispatch-model-guard.py`, its tests, `.claude/skills/cc-guide/SKILL.md`, `build/CLAUDE.md` and the guide. The new probe loads only project settings and persists no session, so the skill's checkout check and the `~/.claude/projects/` note need no change.
- Never commit raw probe output. Only files that `probes.save_fixtures` wrote go into `build/cc_guide/probe_streams/`, and `test_probe_replay.py` fails on a path or an id in them (plan 58 decision D3). The repo is public.
- The one live run (Task 4) waits for the owner to name the binary. It costs about $0.10–0.40, and `--max-budget-usd 0.50` caps it. `--allow-old` needs the owner's word, and a rerun needs a new one.
- Prose in `hooks/README.md` and in commit messages follows `rules/write-with-asd-ste100.md`: one idea a sentence, active voice, no semicolons.
- Each commit message ends with the execution session's `Co-Authored-By` line, from its attribution reminder. The commit blocks below write it as `<the session's trailer>`: replace that with the line.
- Test deltas below are +N per suite, never absolute totals. The `build` suite collects `build/cc_guide/`, so each `cc_guide` delta also applies to `build`.

## Decisions

- **D1** (owner, plan review, 2026-10-28): O1, default kept. The probe's guide sections are `hooks.events`, `hooks.configuration`, `hooks.patterns` and `subagents.models`. Applied in: Task 4.
- **D2** (owner, plan review, 2026-10-28): O2, default kept. The unset-model test mirrors the guard's `decide()`, which reads `tool_input.get('model')`. An absent, empty or null model passes, and any value is DIVERGES. Applied in: Task 1.
- **D3** (owner, plan review, 2026-10-28): O3, default kept. The probe dispatches only the `BUILTIN_PINNED` members and one control. It does not dispatch `Plan` or `statusline-setup`. Applied in: Task 1, Task 2.
- **D4** (owner, execution, 2026-10-28): the live run uses Claude Code 2.1.308 from the Desktop app bundle (`~/Library/Application Support/Claude/claude-code/2.1.308/a93ded4b1b47/claude.app/Contents/MacOS/claude`), one run, with `--allow-old` (the newest changelog release is 2.1.311 and no binary that new is installed; the first attempt without the flag was refused and spent nothing, and the owner approved the flag in a second answer). Applied in: Task 4.
- **D5** (owner, execution, 2026-10-28): the final review's Codex seat runs with the per-run override `-c 'model="gpt-6-astra"'`, because the config model `gpt-6.1-sol` is rejected for the ChatGPT login. One retry, then the code-reviewer alone. This approval covers that one seat. Applied in: the final review.
- **D6** (owner, execution, 2026-10-28): the Codex P2 and the code-reviewer's Minors 1 and 2 are one defect. A parent session that disobeys the prompt would look like drift, and one ERROR text misnames its cause. They are deferred as one plan-size item, not fixed in this plan, because the fix needs `_trim_block` in `probe_checks.py`, which Global Constraints fence off. Applied in: the deferred section `69-agent-payload-probe`.
- **D7** (owner, execution, 2026-10-28): the stale comment above `PAYLOAD_CEILING_MS` (code-reviewer Minor 3) is fixed now, in commit f2c7d55. Applied in: Task 2.
- **D8** (owner, execution, 2026-10-28): the other code Minors (final review 4 and 5, and the per-task Minors) are deferred as one quick-fix item. The README wording Minor (final review 6) is dropped, since that text is the plan text the owner approved on 2026-10-28. Applied in: the deferred section `69-agent-payload-probe`.

## Related open items (taken into account, not absorbed)

- **Model-alias remap** (`specs/deferred_items.md`, section `deferred-2026-10-21`, design, open). A caller's `ANTHROPIC_DEFAULT_HAIKU_MODEL` can make `agent-model-pins` report a false DIVERGES. The new probe checks the built-in against a control that passes `model: "haiku"` in the same run and environment. An alias remap therefore moves both models together. One exposure remains: the built-in pins a full model id while the caller remaps the alias. The open item's scrub-or-record decision lands in `execute`, which every probe uses, so it will cover this probe too. This plan does not touch `SCRUBBED_ENV`. The control comparison is also a third option for that item, to report at completion.
- **Plan 58 review Minors batch** (section `58-claude-code-drift-automation — 2026-10-20`, plan, open). This plan fixes none of its items. It touches them as follows:
  - (l): `probes.py` grows by about 70 lines. Item (l) says to split process control out "if it grows", so its revisit trigger fires. Report it at completion, and do not split.
  - (c) and (v): the new side file never goes through `scrub_events`, and keeps no Bash text or scratch suffix.
  - (e): the stream side reuses `dispatches()`, whose `Task` alias stays untested. The payload side treats a `Task` tool name as DIVERGES, since the guard's matcher matches `Agent` only.
  - (r): the new replay cases pin their findings. The old cases stay as they are.
  - (u): the new replay helper imports `probe_checks` directly. `explore_ids` keeps its form.
- **Coverage gaps for the owner** (drift spec R4.3). The guide states neither the fields of an agent dispatch's `PreToolUse` payload nor `claude-code-guide`'s Haiku pin. The probe watches both anyway. List them in the completion report for the owner to cover in the guide or leave uncovered. Do not add guide text.

## File map

- Modify `build/cc_guide/probe_checks.py`: the payload constants, `trim_payload`, `first_by_type`, `check_payloads` and `assess_agent_payload` (Task 1).
- Modify `build/cc_guide/test_probe_checks.py`: the assertion's cases, the trim test, and the test that holds the constants to the hook's (Task 1).
- Modify `build/cc_guide/probes.py`: the payload hook, `prepare_payload`, `collect_payload`, `assess_payload` and `PAYLOAD_PROBE` (Task 2), then its `PROBE_RUNS` entry (Task 4).
- Modify `build/cc_guide/test_probes.py`: the runner's tests (Task 2), then drop their `monkeypatch.setitem` once the probe is registered (Task 4).
- Modify `hooks/README.md`: the Probe-log intro, the new row, and two sentences naming the probe (Task 3).
- Modify `build/cc_guide/manifest.toml`: the `[[probe]]` entry (Task 4).
- Create `build/cc_guide/probe_streams/agent-payload.jsonl` and `build/cc_guide/probe_streams/agent-payload.payloads.json`, written only by `save_fixtures` (Task 4).
- Modify `build/cc_guide/PROBES.md`: the live run's row, appended by `cli.py probes` (Task 4).
- Modify `build/cc_guide/test_probe_replay.py`: the replay helpers and cases (Task 4).

---

### Task 1: The agent-payload assertion

**Files:**
- Modify: `build/cc_guide/probe_checks.py` (constants after line 27, `PIN_AGENTS`; functions after `assess_agent_model_pins`, which ends at line 192)
- Test: `build/cc_guide/test_probe_checks.py` (imports at the top; new tests after `test_agent_model_pins_needs_a_forwarded_message_for_each_agent`, line 148)

**Interfaces:**
- Consumes: `broken`, `is_init`, `dispatches`, `forwarded_models`, `Verdict`, `SYNTHETIC`, and `DIVERGES`, `ERROR`, `PASS` from `state`, all existing.
- Produces, for Tasks 2 and 4:
  - Constants `GUARDED_TOOL = 'Agent'`, `HAIKU_BUILTINS = ('claude-code-guide',)`, `CONTROL_AGENT = 'general-purpose'`, `CONTROL_MODEL = 'haiku'`, `PAYLOAD_AGENTS = (CONTROL_AGENT, *HAIKU_BUILTINS)`, `ANY_MATCHER = '*'`, `GUARD_MATCHER = 'Agent'`.
  - `trim_payload(payload, matcher: str) -> dict | None`, which returns `{'matcher', 'tool_name', 'input_keys', 'subagent_type', 'model'}` or None.
  - `first_by_type(payloads: list[dict], matcher: str) -> dict[str, dict]`.
  - `check_payloads(payloads: list[dict]) -> Verdict | None`.
  - `assess_agent_payload(events: list[dict] | None, payloads: list[dict]) -> Verdict`.

- [x] **Step 1: Write the failing tests**

In `build/cc_guide/test_probe_checks.py`, change the imports at the top to:

```python
import importlib.util
import json
from pathlib import Path

import pytest

import probe_checks as pc
from cc_fixtures import isolated_home  # noqa: F401
from state import DIVERGES, ERROR, PASS

GUARD = Path(__file__).resolve().parents[2] / 'hooks' / 'dispatch-model-guard.py'
```

Then insert after `test_agent_model_pins_needs_a_forwarded_message_for_each_agent` (before `DENIAL = ...`):

```python
def payload_log(changes=None):
    '''Both logging hooks' trimmed payloads for the control and each pinned
    built-in, as collect_payload writes them; changes maps an agent type to
    the fields that replace its payloads'.'''
    log = []
    for matcher in (pc.ANY_MATCHER, pc.GUARD_MATCHER):
        for agent in pc.PAYLOAD_AGENTS:
            model = pc.CONTROL_MODEL if agent == pc.CONTROL_AGENT else None
            keys = sorted(['description', 'prompt', 'subagent_type', *(['model'] if model else [])])
            log.append({'matcher': matcher, 'tool_name': 'Agent', 'input_keys': keys, 'subagent_type': agent,
                        'model': model, **(changes or {}).get(agent, {})})
    return log


def payload_run(served=None):
    '''A parent on Sonnet that dispatches the haiku control and each pinned
    built-in in one message, each forwarding one message from the model
    given for it.'''
    served = {agent: 'claude-haiku-5-5' for agent in pc.PAYLOAD_AGENTS} | (served or {})
    sent = [tool_use(f'toolu_{n}', 'Agent', subagent_type=agent, prompt='p')
            for n, agent in enumerate(pc.PAYLOAD_AGENTS)]
    forwarded = [assistant({'type': 'text', 'text': 'OK'}, parent=f'toolu_{n}', model=served[agent])
                 for n, agent in enumerate(pc.PAYLOAD_AGENTS)]
    return [init(), assistant(*sent), *forwarded, result()]


@pytest.mark.parametrize('events, payloads, verdict', [
    (payload_run(), payload_log(),
     (PASS, 'dispatches reach PreToolUse as Agent, with no model when unset; claude-code-guide served '
            'claude-haiku-5-5, as the haiku control was')),
    # A renamed tool still reaches the hook that matches every tool, so the rename is named, not an ERROR.
    (payload_run(), [{**p, 'tool_name': 'Task'} for p in payload_log()],
     (DIVERGES, 'a subagent dispatch reaches PreToolUse as Task, not Agent')),
    (payload_run(), [p for p in payload_log() if p['subagent_type'] != 'claude-code-guide'],
     (ERROR, 'no PreToolUse payload dispatches claude-code-guide')),
    (payload_run(), [p for p in payload_log() if p['matcher'] != pc.GUARD_MATCHER],
     (DIVERGES, 'the Agent matcher did not fire for general-purpose, claude-code-guide')),
    (payload_run(), payload_log({'general-purpose': {
        'model': None, 'input_keys': ['description', 'model_name', 'prompt', 'subagent_type']}}),
     (DIVERGES, "the general-purpose dispatch passed model 'haiku', but its payload holds model None "
                '(tool_input keys: description, model_name, prompt, subagent_type)')),
    # The guard reads tool_input.get('model'): a value on a dispatch sent without one lets every such call through.
    (payload_run(), payload_log({'claude-code-guide': {'model': 'inherit'}}),
     (DIVERGES, "a dispatch sent with no model (claude-code-guide) arrives with model 'inherit', so the guard "
                'would pass a model-less dispatch of any type')),
    (payload_run()[:-1], payload_log(), (ERROR, 'no result event')),
    (payload_run(), [], (ERROR, 'the PreToolUse hooks logged no subagent dispatch')),
    ([init(model=None), *payload_run()[1:]], payload_log(), (ERROR, 'the init event names no session model')),
    ([e for e in payload_run() if e.get('parent_tool_use_id') != 'toolu_1'], payload_log(),
     (ERROR, 'claude-code-guide forwarded no message')),
    (payload_run({'claude-code-guide': '<synthetic>'}), payload_log(),
     (ERROR, 'claude-code-guide hit an API error: a message from model <synthetic>')),
    (payload_run({'general-purpose': None}), payload_log(),
     (ERROR, 'general-purpose forwarded a message with no model field')),
    # Under a remap that sends haiku to the session model, a pin and inheritance look the same.
    (payload_run({'general-purpose': 'claude-sonnet-5-5'}), payload_log(),
     (ERROR, 'the general-purpose control with model haiku was served the session model claude-sonnet-5-5, '
             'so a pin cannot be told from it')),
    (payload_run({'claude-code-guide': 'claude-sonnet-5-5'}), payload_log(),
     (DIVERGES, 'claude-code-guide was served the session model claude-sonnet-5-5')),
    # A pin that moves off Haiku also breaks the guard's purpose: an exempt built-in on Opus runs a tier nobody chose.
    (payload_run({'claude-code-guide': 'claude-opus-5-5'}), payload_log(),
     (DIVERGES, 'claude-code-guide was served claude-opus-5-5, not the claude-haiku-5-5 the haiku control was '
                'served')),
])
def test_agent_payload(events, payloads, verdict):
    assert pc.assess_agent_payload(events, payloads) == verdict


def test_trim_payload_keeps_a_main_session_dispatch_and_drops_the_rest():
    '''The kept fields hold no path, id or prompt text, so payloads.json is
    committed as save_fixtures copies it, with no scrub of its own.'''
    main = {'session_id': '364e6342-a957-4e26-a308-caa9e4b4bc69', 'cwd': '/private/tmp/cc-guide-probe-x',
            'transcript_path': '/Users/someone/.claude/projects/x/364e6342.jsonl', 'hook_event_name': 'PreToolUse',
            'tool_name': 'Agent', 'tool_use_id': 'toolu_01AbC',
            'tool_input': {'description': 'd', 'prompt': 'List /Users/someone', 'subagent_type': 'claude-code-guide',
                           'run_in_background': False}}
    kept = pc.trim_payload(main, '*')
    assert kept == {'matcher': '*', 'tool_name': 'Agent', 'subagent_type': 'claude-code-guide', 'model': None,
                    'input_keys': ['description', 'prompt', 'run_in_background', 'subagent_type']}
    for leak in ('364e6342', '/private/', '/Users/', 'toolu_', 'List'):
        assert leak not in json.dumps(kept)
    assert pc.trim_payload({**main, 'agent_id': 'a5287d9d575e'}, '*') is None  # made inside a subagent
    assert pc.trim_payload({**main, 'tool_name': 'Read', 'tool_input': {'file_path': '/Users/someone/a'}}, '*') is None
    assert pc.trim_payload({**main, 'tool_input': 'not an object'}, '*') is None
    assert pc.trim_payload(['not', 'a', 'payload'], '*') is None


def test_the_payload_probe_checks_what_the_dispatch_guard_reads():
    '''The guard's tool name and its pinned built-ins, loaded as
    check_frontmatter.load_pinned_roster loads its roster. A built-in added
    to BUILTIN_PINNED needs a dispatch in this probe as well.'''
    spec = importlib.util.spec_from_file_location('dispatch_model_guard', GUARD)
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    assert guard.AGENT_TOOL == pc.GUARDED_TOOL == pc.GUARD_MATCHER
    assert guard.BUILTIN_PINNED == frozenset(pc.HAIKU_BUILTINS)
```

- [x] **Step 2: Run the tests to verify they fail**

Run: `uv run python build/run_suites.py cc_guide -- test_probe_checks.py`
Expected: the module fails to collect, with `AttributeError: module 'probe_checks' has no attribute 'PAYLOAD_AGENTS'` (the parametrize list calls `payload_run()` at import). No test in the file runs.

- [x] **Step 3: Write the implementation**

In `build/cc_guide/probe_checks.py`, insert after line 27 (`PIN_AGENTS = (*HAIKU_AGENTS, REVIEWER)`):

```python
# agent-payload: what hooks/dispatch-model-guard.py reads from a dispatch's PreToolUse payload. Its matcher and
# decide() take the tool's name, decide() reads tool_input's model and subagent_type, and it lets a model-less call
# through for the built-ins in its BUILTIN_PINNED. test_probe_checks.py holds these to the hook's own constants.
GUARDED_TOOL = 'Agent'  # the hook's AGENT_TOOL
HAIKU_BUILTINS = ('claude-code-guide',)  # the hook's BUILTIN_PINNED: plan 63 saw each run on Haiku with no model passed
CONTROL_AGENT, CONTROL_MODEL = 'general-purpose', 'haiku'  # dispatched beside them, passing its model
PAYLOAD_AGENTS = (CONTROL_AGENT, *HAIKU_BUILTINS)
ANY_MATCHER, GUARD_MATCHER = '*', 'Agent'  # the two logging hooks; the second is hooks/README.md's install matcher
```

Insert after `assess_agent_model_pins` (after its last line, `return Verdict(PASS, f'Explore and test-runner served {served}; {REVIEWER} effort {REVIEWER_EFFORT}')`):

```python
def trim_payload(payload, matcher: str) -> dict | None:
    '''A logged PreToolUse payload cut to what assess_agent_payload reads,
    tagged with the matcher of the hook that logged it. None for one it
    never reads: not an object, made inside a subagent (it carries
    agent_id), or dispatching no subagent. What is kept holds no path, id
    or prompt text, so the file needs no scrub to be committed (R12.6).'''
    if not isinstance(payload, dict) or 'agent_id' in payload:
        return None
    tool_input = payload.get('tool_input')
    if not isinstance(tool_input, dict) or 'subagent_type' not in tool_input:
        return None
    return {'matcher': matcher, 'tool_name': payload.get('tool_name'), 'input_keys': sorted(tool_input),
            'subagent_type': tool_input['subagent_type'], 'model': tool_input.get('model')}


def first_by_type(payloads: list[dict], matcher: str) -> dict[str, dict]:
    '''The first payload of each subagent type that the hook with this matcher logged.'''
    found: dict[str, dict] = {}
    for p in payloads:
        if p.get('matcher') == matcher:
            found.setdefault(p.get('subagent_type'), p)
    return found


def check_payloads(payloads: list[dict]) -> Verdict | None:
    '''The payload half of agent-payload: a verdict when the payloads decide
    one, else None. A dispatch that reaches PreToolUse under another tool
    name, or that the Agent matcher misses, never reaches the guard. A
    control payload without its model, or a model on a dispatch sent with
    none, changes what decide() reads.'''
    if not payloads:
        return Verdict(ERROR, 'the PreToolUse hooks logged no subagent dispatch')
    seen = first_by_type(payloads, ANY_MATCHER)
    renamed = sorted({str(p.get('tool_name')) for p in seen.values()} - {GUARDED_TOOL})
    if renamed:
        return Verdict(DIVERGES, f"a subagent dispatch reaches PreToolUse as {', '.join(renamed)}, not {GUARDED_TOOL}")
    for agent in PAYLOAD_AGENTS:
        if agent not in seen:
            return Verdict(ERROR, f'no PreToolUse payload dispatches {agent}')
    matched = first_by_type(payloads, GUARD_MATCHER)
    missed = [agent for agent in PAYLOAD_AGENTS if agent not in matched]
    if missed:
        return Verdict(DIVERGES, f"the {GUARD_MATCHER} matcher did not fire for {', '.join(missed)}")
    control = seen[CONTROL_AGENT]
    if control.get('model') != CONTROL_MODEL:
        keys = ', '.join(control.get('input_keys') or [])
        return Verdict(DIVERGES, f"the {CONTROL_AGENT} dispatch passed model {CONTROL_MODEL!r}, but its payload holds "
                                 f"model {control.get('model')!r} (tool_input keys: {keys})")
    for agent in HAIKU_BUILTINS:
        if seen[agent].get('model'):
            return Verdict(DIVERGES, f"a dispatch sent with no model ({agent}) arrives with model "
                                     f"{seen[agent]['model']!r}, so the guard would pass a model-less dispatch of "
                                     'any type')
    return None


def assess_agent_payload(events: list[dict] | None, payloads: list[dict]) -> Verdict:
    '''agent-payload: hooks/dispatch-model-guard.py's inputs stay as plan 63
    saw them on Claude Code 2.1.304. `payloads` holds the main session's
    dispatch payloads, cut by trim_payload, from two PreToolUse hooks: one
    matches every tool, the other matches Agent as the guard's install
    does. check_payloads reads them first, so a renamed tool is named
    before any message is looked for. Then each subagent's model is read
    from its forwarded messages. The control, which passes model haiku,
    must not be served the session model (the init event's), or a pin
    cannot be told from inheritance: ERROR. Each built-in in
    HAIKU_BUILTINS must be served neither the session model (it inherits,
    so its exemption lets the session model run) nor anything but what the
    control is served (its pin moved): DIVERGES. A model of <synthetic>, a
    message with no model and a dispatch with no forwarded message are
    ERROR, as in agent-model-pins.'''
    why = broken(events)
    if why:
        return Verdict(ERROR, why)
    verdict = check_payloads(payloads)
    if verdict:
        return verdict
    session = next(e for e in events if is_init(e)).get('model')
    if not session:
        return Verdict(ERROR, 'the init event names no session model')
    sent = dispatches(events)
    served: dict[str, set[str]] = {}
    for agent in PAYLOAD_AGENTS:
        forwarded = forwarded_models(events, {tid for tid, kind in sent.items() if kind == agent})
        if not forwarded:
            return Verdict(ERROR, f'{agent} forwarded no message')
        if SYNTHETIC in forwarded:
            return Verdict(ERROR, f'{agent} hit an API error: a message from model {SYNTHETIC}')
        if None in forwarded:
            return Verdict(ERROR, f'{agent} forwarded a message with no model field')
        served[agent] = forwarded
    control = ', '.join(sorted(served[CONTROL_AGENT]))
    if session in served[CONTROL_AGENT]:
        return Verdict(ERROR, f'the {CONTROL_AGENT} control with model {CONTROL_MODEL} was served the session model '
                              f'{session}, so a pin cannot be told from it')
    wrong = []
    for agent in HAIKU_BUILTINS:
        if session in served[agent]:
            wrong.append(f'{agent} was served the session model {session}')
        elif served[agent] != served[CONTROL_AGENT]:
            wrong.append(f"{agent} was served {', '.join(sorted(served[agent]))}, not the {control} the "
                         f'{CONTROL_MODEL} control was served')
    if wrong:
        return Verdict(DIVERGES, '; '.join(wrong))
    return Verdict(PASS, f"dispatches reach PreToolUse as {GUARDED_TOOL}, with no model when unset; "
                         f"{', '.join(HAIKU_BUILTINS)} served {control}, as the {CONTROL_MODEL} control was")
```

- [x] **Step 4: Run the tests to verify they pass**

Run: `uv run python build/run_suites.py cc_guide -- test_probe_checks.py`
Expected: PASS, with +17 tests against the file's count before this task (15 `test_agent_payload` cases, the trim test and the guard-constants test).

Then run the whole suite: `uv run python build/run_suites.py cc_guide`
Expected: PASS, +17.

- [x] **Step 5: Commit**

Run `build/run_commit_lints.sh` (expected: exit 0), then:

```bash
git add build/cc_guide/probe_checks.py build/cc_guide/test_probe_checks.py
git commit -m "$(cat <<'EOF'
feat(cc-guide): add the agent-payload probe assertion

assess_agent_payload checks what hooks/dispatch-model-guard.py reads. It
checks the dispatch tool's name, the Agent matcher, the model field on a
dispatch with and without a model, and the model each pinned built-in is
served. The built-in is compared with a general-purpose control that passes
model haiku in the same run. A test holds the probe's constants to the
hook's AGENT_TOOL and BUILTIN_PINNED.

Co-Authored-By: <the session's trailer>
EOF
)"
```

---

### Task 2: The agent-payload runner, not yet registered

**Files:**
- Modify: `build/cc_guide/probes.py` (constants near lines 35–52; new code between `assess_pins`, which ends at line 324, and `PROBE_RUNS`, line 327)
- Test: `build/cc_guide/test_probes.py` (imports at the top; new tests after `test_output_of_another_shape_is_an_error_never_a_crash`, which ends near line 450)

**Interfaces:**
- Consumes, from Task 1: `probe_checks.ANY_MATCHER`, `probe_checks.GUARD_MATCHER`, `probe_checks.trim_payload` and `probe_checks.assess_agent_payload`. Existing: `claude_args`, `Invocation`, `Probe`, `Read`, `stream_of`, `PROBE_TIMEOUT`, `BUDGET_USD`.
- Produces, for Task 4:
  - `prepare_payload(scratch: Path, claude: str, repo: Path) -> list[Invocation]`, which returns one invocation named `dispatch`.
  - `collect_payload(scratch: Path, run_dir: Path) -> None`, which writes `payloads.json`, `payloads-any.raw.jsonl` and `payloads-agent.raw.jsonl`.
  - `assess_payload(read: Read) -> Verdict`.
  - `PAYLOAD_PROBE: Probe`, whose fixtures map is `{'dispatch.jsonl': 'agent-payload.jsonl', 'payloads.json': 'agent-payload.payloads.json'}`.
  - Constants `PAYLOAD_TURNS = 6`, `PAYLOAD_CEILING_MS = 300_000`, `PAYLOAD_HOOK`, `PAYLOAD_LOGS = {'any': '*', 'agent': 'Agent'}` and `PAYLOAD_PROMPT`.

- [x] **Step 1: Write the failing tests**

In `build/cc_guide/test_probes.py`, add `import shlex` to the stdlib imports, between `import os` and `import signal`. Then insert after `test_output_of_another_shape_is_an_error_never_a_crash`:

```python
def dispatch_payload(agent, model=None):
    '''An agent dispatch's PreToolUse payload, shaped like plan 63's recordings (Claude Code 2.1.304).'''
    tool_input = {'description': 'd', 'prompt': 'Reply with the word OK.', 'subagent_type': agent,
                  **({'model': model} if model else {})}
    return {'session_id': '364e6342-a957-4e26-a308-caa9e4b4bc69', 'cwd': '/private/tmp/cc-guide-probe-x',
            'hook_event_name': 'PreToolUse', 'tool_name': 'Agent', 'tool_input': tool_input,
            'tool_use_id': 'toolu_01AbC'}


# The control, the pinned built-in, a dispatch made inside a subagent, and a call to another tool.
PAYLOADS = [dispatch_payload('general-purpose', 'haiku'), dispatch_payload('claude-code-guide'),
            {**dispatch_payload('general-purpose'), 'agent_id': 'a5287d9d575e'},
            {**dispatch_payload('x'), 'tool_name': 'Read', 'tool_input': {'file_path': '/private/tmp/x/a.py'}}]
TRIMMED = [{'matcher': matcher, 'tool_name': 'Agent', 'subagent_type': agent, 'model': model, 'input_keys': keys}
           for matcher in ('*', 'Agent')
           for agent, model, keys in (('claude-code-guide', None, ['description', 'prompt', 'subagent_type']),
                                      ('general-purpose', 'haiku', ['description', 'model', 'prompt',
                                                                    'subagent_type']))]


def fire_payload_hooks(*payloads):
    '''A side effect that runs each PreToolUse hook in the scratch project
    settings on each payload whose tool its matcher matches, as Claude Code
    would.'''
    def side(cwd):
        settings = json.loads((cwd / '.claude' / 'settings.json').read_text())
        for group in settings['hooks']['PreToolUse']:
            for payload in payloads:
                if group['matcher'] in ('*', payload['tool_name']):
                    subprocess.run(shlex.split(group['hooks'][0]['command']), input=json.dumps(payload), text=True,
                                   check=True)
    return side


def payload_stream() -> str:
    '''A parent on Sonnet that dispatches the haiku control and
    claude-code-guide in one message, each forwarding one Haiku message.'''
    sent = [{'type': 'tool_use', 'id': f't{n}', 'name': 'Agent', 'input': {'subagent_type': agent}}
            for n, agent in enumerate(('general-purpose', 'claude-code-guide'))]
    parent = {'type': 'assistant', 'parent_tool_use_id': None,
              'message': {'model': 'claude-sonnet-5-5', 'content': sent}}
    forwarded = [{'type': 'assistant', 'parent_tool_use_id': f't{n}',
                  'message': {'model': 'claude-haiku-5-5', 'content': []}} for n in range(len(sent))]
    return stream({**init(), 'model': 'claude-sonnet-5-5'}, parent, *forwarded, RESULT)


def test_the_payload_probe_logs_each_dispatch_through_both_matchers(tmp_path):
    '''Project settings only, two logging hooks, one file a payload, since
    the hooks and the two dispatches can run at once; collect keeps each
    hook's raw log beside the trimmed payloads.json.'''
    (inv,) = probes.prepare_payload(tmp_path, 'claude', REPO)
    settings = json.loads((tmp_path / '.claude' / 'settings.json').read_text())
    assert [g['matcher'] for g in settings['hooks']['PreToolUse']] == ['*', 'Agent']
    assert inv.name == 'dispatch' and inv.timeout == probes.PROBE_TIMEOUT
    assert inv.env == {'CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS': '300000'}
    assert probes.PAYLOAD_CEILING_MS < probes.PROBE_TIMEOUT * 1000  # claude ends its own wait first
    assert inv.argv[inv.argv.index('--setting-sources') + 1] == 'project'
    assert json.loads(inv.argv[inv.argv.index('--settings') + 1]) == {'permissions': {'defaultMode': 'default',
                                                                                      'allow': ['Agent']}}
    assert '--forward-subagent-text' in inv.argv and inv.argv[-1] == '--no-session-persistence'
    for agent in ('"general-purpose" with model "haiku"', '"claude-code-guide", passing no model'):
        assert agent in inv.argv[1]
    fire_payload_hooks(*PAYLOADS)(tmp_path)
    run_dir = tmp_path / 'run'
    run_dir.mkdir()
    probes.collect_payload(tmp_path, run_dir)
    assert json.loads((run_dir / 'payloads.json').read_text()) == TRIMMED
    assert len((run_dir / 'payloads-any.raw.jsonl').read_text().splitlines()) == 4
    assert len((run_dir / 'payloads-agent.raw.jsonl').read_text().splitlines()) == 3


def bad_payload(cwd):
    (cwd / 'payloads' / 'any' / 'payload.bad').write_text('not json\n', encoding='utf-8')


@pytest.mark.parametrize('side, outcome, finding', [
    (fire_payload_hooks(*PAYLOADS), PASS, 'dispatches reach PreToolUse as Agent, with no model when unset; '
                                          'claude-code-guide served claude-haiku-5-5, as the haiku control was'),
    (bad_payload, ERROR, 'JSONDecodeError: '),
])
def test_the_payload_probe_reads_its_run_like_a_live_one(tmp_path, monkeypatch, side, outcome, finding):
    '''From prepare to the verdict through run_probe, with the hooks fired on
    the scratch settings; a payload that is not JSON is an ERROR row.'''
    monkeypatch.setitem(probes.PROBE_RUNS, 'agent-payload', probes.PAYLOAD_PROBE)
    fake = FakeRuns({'dispatch': payload_stream()}, side={'dispatch': side})
    verdict = probes.run_probe('agent-payload', 'claude', REPO, tmp_path / 'run', fake)
    assert verdict.outcome == outcome and verdict.finding.startswith(finding)
```

- [x] **Step 2: Run the tests to verify they fail**

Run: `uv run python build/run_suites.py cc_guide -- test_probes.py -k payload_probe`
Expected: 3 failed, with `AttributeError: module 'probes' has no attribute 'prepare_payload'` in the first and `... no attribute 'PAYLOAD_PROBE'` in the two parametrized cases.

- [x] **Step 3: Write the implementation**

> Deviation: after the final review, the comment above `PAYLOAD_CEILING_MS` says the dispatches "may run in the background too", not "start in the background too" (D7, commit f2c7d55).

In `build/cc_guide/probes.py`, insert after line 39 (`PINS_CEILING_MS = 900_000`):

```python
# agent-payload's two dispatches start in the background too. This ceiling sits under PROBE_TIMEOUT, so claude ends
# its own wait before the harness stops the run.
PAYLOAD_CEILING_MS = 300_000
```

Change line 52 from `TOOLS_TURNS, STOP_TURNS, PINS_TURNS = 1, 6, 8` to:

```python
TOOLS_TURNS, STOP_TURNS, PINS_TURNS, PAYLOAD_TURNS = 1, 6, 8, 6
```

Insert after `assess_pins` (before `PROBE_RUNS = {`):

```python
# Each PreToolUse payload goes to a file of its own in the folder the hook is
# given, since the two hooks, and two dispatches in one message, can run at once.
PAYLOAD_HOOK = '#!/usr/bin/env bash\ncat > "$(mktemp "$1/payload.XXXXXX")"\n'
PAYLOAD_LOGS = {'any': probe_checks.ANY_MATCHER, 'agent': probe_checks.GUARD_MATCHER}  # log folder -> matcher
PAYLOAD_PROMPT = ('In one message, call the Agent tool twice: (1) subagent_type "general-purpose" with model "haiku" '
                  'and prompt "Reply with the word OK and nothing else. Use no tools."; (2) subagent_type '
                  '"claude-code-guide", passing no model, with prompt "Reply with the word OK and nothing else. Use '
                  'no tools.". Wait for both results, then reply with the word DONE.')


def prepare_payload(scratch: Path, claude: str, repo: Path) -> list[Invocation]:
    '''agent-payload logs every PreToolUse payload through two hooks in the
    scratch directory's project settings, one matching every tool and one
    matching Agent as hooks/README.md installs the guard, while the parent
    dispatches the haiku control and each pinned built-in. Only project
    settings load, so the owner's own hooks and agents stay out of the run,
    and the session is not persisted, since the stream holds each model.'''
    hook = scratch / 'payload-hook.sh'
    hook.write_text(PAYLOAD_HOOK, encoding='utf-8')
    hook.chmod(0o755)
    groups = []
    for folder, matcher in PAYLOAD_LOGS.items():
        log = scratch / 'payloads' / folder
        log.mkdir(parents=True)
        command = f'{shlex.quote(str(hook))} {shlex.quote(str(log))}'
        groups.append({'matcher': matcher, 'hooks': [{'type': 'command', 'command': command}]})
    (scratch / '.claude').mkdir()
    settings = {'hooks': {'PreToolUse': groups}}
    (scratch / '.claude' / 'settings.json').write_text(json.dumps(settings, indent=1) + '\n', encoding='utf-8')
    argv = claude_args(claude, PAYLOAD_PROMPT, turns=PAYLOAD_TURNS, sources='project', mode='default',
                       allow=('Agent',), extra=('--forward-subagent-text',))
    return [Invocation('dispatch', argv, {'CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS': str(PAYLOAD_CEILING_MS)},
                       PROBE_TIMEOUT)]


def collect_payload(scratch: Path, run_dir: Path) -> None:
    '''Each hook's log, raw, as payloads-<folder>.raw.jsonl, to read by
    hand, and the main session's dispatches cut by trim_payload as
    payloads.json, the one file the assessment and its fixture read. A
    payload that is not JSON raises ValueError, which run_probe reports as
    ERROR.'''
    kept = []
    for folder, matcher in PAYLOAD_LOGS.items():
        texts = [path.read_text(encoding='utf-8').strip()
                 for path in sorted((scratch / 'payloads' / folder).glob('payload.*'))]
        (run_dir / f'payloads-{folder}.raw.jsonl').write_text(''.join(f'{t}\n' for t in texts), encoding='utf-8')
        kept += [p for p in (probe_checks.trim_payload(json.loads(t), matcher) for t in texts) if p is not None]
    kept.sort(key=lambda p: (p['matcher'], str(p['subagent_type'])))
    (run_dir / 'payloads.json').write_text(json.dumps(kept, indent=1) + '\n', encoding='utf-8')


def assess_payload(read: Read) -> Verdict:
    return probe_checks.assess_agent_payload(stream_of(read('dispatch.jsonl')),
                                             json.loads(read('payloads.json') or '[]'))


PAYLOAD_PROBE = Probe(prepare_payload, collect_payload, assess_payload,
                      {'dispatch.jsonl': 'agent-payload.jsonl', 'payloads.json': 'agent-payload.payloads.json'})
```

Do not add `PAYLOAD_PROBE` to `PROBE_RUNS` yet. `test_cli.py` requires the manifest's probes to equal `PROBE_RUNS`, and `test_probe_replay.py` requires fixtures for each entry. Task 4 adds all three together.

- [x] **Step 4: Run the tests to verify they pass**

Run: `uv run python build/run_suites.py cc_guide -- test_probes.py -k payload_probe`
Expected: 3 passed.

Then run the whole suite: `uv run python build/run_suites.py cc_guide`
Expected: PASS, +3 against the end of Task 1.

- [x] **Step 5: Commit**

Run `build/run_commit_lints.sh` (expected: exit 0), then:

```bash
git add build/cc_guide/probes.py build/cc_guide/test_probes.py
git commit -m "$(cat <<'EOF'
feat(cc-guide): add the agent-payload probe runner, not yet registered

prepare_payload writes two logging PreToolUse hooks into the scratch project
settings, one for every tool and one for Agent. It then runs a parent that
dispatches a haiku control and claude-code-guide. collect_payload keeps each
raw log and writes a trimmed payloads.json that needs no scrub. Task 4 of
plan 69 registers the probe with its first live run.

Co-Authored-By: <the session's trailer>
EOF
)"
```

---

### Task 3: Record the Task 6 findings in the hooks README

**Files:**
- Modify: `hooks/README.md` (the `dispatch-model-guard.py` section's roster paragraph, about line 437, and the `## Probe log` section, lines 444–466)

**Interfaces:**
- Consumes: the probe id `agent-payload` and its two hooks, from Tasks 1 and 2.
- Produces: nothing code reads.

- [x] **Step 1: Point the roster paragraph at the probe**

In the paragraph that starts `**Roster drift is a lint failure.**`, replace the sentence `Recheck it when Claude Code changes a built-in agent's model.` with:

````markdown
The drift tool's `agent-payload` probe rechecks it (see **Probe log** below).
````

- [x] **Step 2: Widen the Probe-log intro**

Replace the intro paragraph under `## Probe log`:

````markdown
`readonly-agent-guard.py` depends on Claude Code putting the dispatched agent's
name in the `PreToolUse` payload. That is version-sensitive API surface, so it is
probed rather than assumed — re-run the probe after a binary update.
````

with:

````markdown
`readonly-agent-guard.py` depends on Claude Code putting the dispatched agent's
name in the `PreToolUse` payload. `dispatch-model-guard.py` depends on the payload of
an agent dispatch and on the model each built-in agent runs on. These are
version-sensitive API surface, so they are probed rather than assumed — re-run the
probes after a binary update.
````

- [x] **Step 3: Add the row**

Add this row under the table's existing 2026-09-03 row:

````markdown
| 2026-10-21 | 2.1.304 | An agent dispatch reaches `PreToolUse` with `tool_name` `Agent`. Its type is at `tool_input.subagent_type` and its model at `tool_input.model`. An unset model is **absent**, not empty. A call made inside a subagent also carries `agent_id` and `agent_type`. With no model passed, the built-in `claude-code-guide` ran on Haiku (`claude-haiku-5-5`), and `general-purpose`, `Plan` and `statusline-setup` ran on the session model. Plan 63 Task 6 recorded this with a logging hook on `claude -p`. |
````

- [x] **Step 4: Name the probe in a closing paragraph**

The section's last paragraph is also the file's last. It ends with the words `this table keeps the payload findings.`, wrapped across its last two lines. After it, add a blank line and this new paragraph, so the file still ends with one newline:

````markdown
The `agent-payload` probe re-checks the 2026-10-21 row. Two logging `PreToolUse`
hooks record each dispatch's payload: one matches every tool, and one matches
`Agent` as the install above does. In the same run, the probe also dispatches
`general-purpose` with `model: haiku`. It compares the model that `claude-code-guide`
is served with the model that this control is served. It fails when the tool's
name, the matcher, the model field or a pin in `BUILTIN_PINNED` changes.
````

- [x] **Step 5: Check and commit**

Run: `uv run python build/cc_guide/cli.py lint` (expected: exit 0; any `STALE` line is reported, not a failure) and `uv run --with pyyaml python build/check_conformance.py` (expected: exit 0). Then run `build/run_commit_lints.sh` (expected: exit 0), and:

```bash
git add hooks/README.md
git commit -m "$(cat <<'EOF'
docs(hooks): log the dispatch payload findings and name their probe

The Probe log gets the plan 63 Task 6 findings on Claude Code 2.1.304. A
dispatch arrives as tool_name Agent, and an unset model is absent. The
built-in claude-code-guide ran on Haiku with no model passed. The README now
names the agent-payload probe, which re-checks these findings.

Co-Authored-By: <the session's trailer>
EOF
)"
```

---

### Task 4: Register the probe and record its first run (owner gate)

The controller runs this task itself, not a subagent: it needs the owner's answer and spends tokens.

**Files:**
- Modify: `build/cc_guide/probes.py` (`PROBE_RUNS`)
- Modify: `build/cc_guide/manifest.toml` (after the `agent-model-pins` entry, the file's last lines)
- Modify: `build/cc_guide/test_probes.py` (drop the `monkeypatch.setitem` line and the `monkeypatch` parameter that Task 2 added)
- Modify: `build/cc_guide/test_probe_replay.py` (imports, helpers, cases)
- Create: `build/cc_guide/probe_streams/agent-payload.jsonl`, `build/cc_guide/probe_streams/agent-payload.payloads.json` (written only by `save_fixtures`)
- Modify: `build/cc_guide/PROBES.md` (one row, appended by `cli.py probes`)

**Interfaces:**
- Consumes: `PAYLOAD_PROBE` (Task 2), the `assess_agent_payload` findings (Task 1).
- Produces: the registered probe `agent-payload`.

- [x] **Step 1: Owner gate: stop and ask**

> Deviation: D4 changed once. The first answer chose 2.1.308 with no `--allow-old`. Step 3 was then refused, and the owner's second answer approved `--allow-old`. D4 now says so.

Run: `uv run python build/cc_guide/cli.py binaries`. Show the owner the list and ask, as one question:
- which binary to probe (`probes` has no default, by drift spec Decision 15);
- whether to spend one live run, about $0.10–0.40, capped at $0.50 by `--max-budget-usd`.

Say that a binary older than the newest cached changelog release is refused unless the owner approves `--allow-old`, which the row then records. Do not go on until the owner answers. Log the answer in this plan's `## Decisions` under the next free number, as `- **D<n>** (owner, execution, YYYY-MM-DD): <the binary, and --allow-old or not>. Applied in: Task 4.` Plan review may already have used D1 and later numbers.

- [x] **Step 2: Register the probe in both places**

In `build/cc_guide/probes.py`, add the last entry to `PROBE_RUNS`, after the `'agent-model-pins'` entry:

```python
    'agent-payload': PAYLOAD_PROBE,
```

In `build/cc_guide/manifest.toml`, append after the `agent-model-pins` entry:

```toml

[[probe]]
id = 'agent-payload'
# What hooks/dispatch-model-guard.py reads: a dispatch's PreToolUse payload, the Agent matcher, and the pins of
# the built-ins in BUILTIN_PINNED. The guide states neither the payload's fields nor claude-code-guide's pin
# (coverage gaps, plan 69).
sections = ['hooks.events', 'hooks.configuration', 'hooks.patterns', 'subagents.models']
files = ['hooks/dispatch-model-guard.py', 'hooks/README.md']
```

In `build/cc_guide/test_probes.py`, delete the line `monkeypatch.setitem(probes.PROBE_RUNS, 'agent-payload', probes.PAYLOAD_PROBE)` and the `monkeypatch` parameter of `test_the_payload_probe_reads_its_run_like_a_live_one`.

Run: `uv run python build/run_suites.py cc_guide -- test_cli.py test_probes.py test_probe_replay.py`
Expected: `test_cli.py` and `test_probes.py` pass. In `test_probe_replay.py`, exactly two tests fail: `test_every_registered_probe_has_its_fixtures` (`agent-payload: agent-payload.jsonl is missing; record it with save_fixtures`) and `test_the_recorded_run_passes[agent-payload]`. Read both failures. Any other failure is a stop.

- [x] **Step 3: Run the live probe**

> Deviation: the first run, without `--allow-old`, exited 2 and spent nothing, because 2.1.311 was the newest changelog release. The second run used `--allow-old` after the owner approved it (D4). The row records the flag.

From the repo root, with the binary the owner named:

Run: `uv run python build/cc_guide/cli.py probes --claude '<path>' --only agent-payload`

Add `--allow-old` only if the owner approved it in Step 1.
Expected: exit 0, and this output:

```
probes: <version> at <path>
agent-payload: PASS: dispatches reach PreToolUse as Agent, with no model when unset; claude-code-guide served claude-haiku-5-5, as the haiku control was
  raw output: <cache>/probes/<YYYYmmddTHHMMSS>-agent-payload
appended 1 row(s) to build/cc_guide/PROBES.md; nothing is committed
```

If the finding names another Haiku model id, that is still a PASS. Use the recorded id in Step 6's strings, and add a `> Deviation:` note.

If the outcome is DIVERGES or ERROR, stop. First read the parent's `Agent` calls in `dispatch.jsonl`. If the parent itself left out the control's `model` or gave `claude-code-guide` one, the run tested nothing: report that, not drift. List the raw output folder (`dispatch.jsonl`, `dispatch.err`, `payloads-any.raw.jsonl`, `payloads-agent.raw.jsonl`, `payloads.json`) and report the finding to the owner. A DIVERGES may be real drift in what the guard relies on. Do not rerun without the owner's word, and do not commit the appended row until the owner rules on it.

- [x] **Step 4: Save the fixtures**

Run: `uv run --directory build/cc_guide --python 3.13 python -c "import probes; from pathlib import Path; print(probes.save_fixtures(Path('<raw output folder>'), 'agent-payload', Path('probe_streams')))"`
Expected: a list of two paths, `probe_streams/agent-payload.jsonl` and `probe_streams/agent-payload.payloads.json`.

Check what was saved:
- Run `cat build/cc_guide/probe_streams/agent-payload.payloads.json`. Expected: four records, `*` then `Agent`, each matcher with `claude-code-guide` (model `null`) and `general-purpose` (model `"haiku"`). No path, id or prompt text.
- Run `grep -o '"model": "[^"]*"' build/cc_guide/probe_streams/agent-payload.jsonl | sort | uniq -c`. Expected: the init event's `claude-sonnet-5-5`, plus `claude-haiku-5-5` on the forwarded messages. These are the ids Step 6's findings use. If they differ, use the recorded ids and add a `> Deviation:` note.

Run: `uv run python build/run_suites.py cc_guide -- test_probe_replay.py`
Expected: PASS, +1 (`test_the_recorded_run_passes[agent-payload]`). `test_no_fixture_holds_a_path_or_an_id_from_the_recording_machine` also passes. If it fails, delete the two fixture files and stop: re-record only through `save_fixtures`.

- [x] **Step 5: Write the replay cases**

In `build/cc_guide/test_probe_replay.py`, add `import probe_checks` before `import probes`. Insert these helpers after `unmarked` (before the comment `# Each ERROR case names its finding`):

```python
def payloads_with(edit) -> dict[str, str]:
    '''The recorded payload log with `edit` applied to each payload; an edit that returns None drops the payload.'''
    probe = probes.PROBE_RUNS['agent-payload']
    saved = json.loads((FIXTURES / probe.fixtures['payloads.json']).read_text(encoding='utf-8'))
    return {'payloads.json': json.dumps([p for p in (edit(dict(q)) for q in saved) if p is not None])}


def served_by(agent: str, model: str) -> dict[str, str]:
    '''The recorded dispatch stream with each message that `agent` forwarded served by `model`.'''
    probe = probes.PROBE_RUNS['agent-payload']
    events = probes.stream_of(probes.reader(FIXTURES, probe.fixtures)('dispatch.jsonl'))
    ids = {tid: model for tid, kind in probe_checks.dispatches(events).items() if kind == agent}
    return edited('agent-payload', 'dispatch.jsonl', model_of(ids))
```

Append these cases to the end of the parametrize list of `test_a_changed_behaviour_diverges_and_a_broken_run_is_an_error`, after the last `guard-liveness` case:

```python
    # agent-payload's cases pin their findings, DIVERGES included.
    ('agent-payload', lambda: payloads_with(lambda p: {**p, 'tool_name': 'Task'}), DIVERGES,
     'a subagent dispatch reaches PreToolUse as Task, not Agent'),
    ('agent-payload', lambda: payloads_with(lambda p: None if p['matcher'] == 'Agent' else p), DIVERGES,
     'the Agent matcher did not fire for general-purpose, claude-code-guide'),
    ('agent-payload', lambda: payloads_with(lambda p: {**p, 'model': p['model'] or 'inherit'}), DIVERGES,
     "a dispatch sent with no model (claude-code-guide) arrives with model 'inherit', so the guard would pass a "
     'model-less dispatch of any type'),
    ('agent-payload', lambda: served_by('claude-code-guide', 'claude-sonnet-5-5'), DIVERGES,
     'claude-code-guide was served the session model claude-sonnet-5-5'),
    ('agent-payload', lambda: served_by('claude-code-guide', 'claude-opus-5-5'), DIVERGES,
     'claude-code-guide was served claude-opus-5-5, not the claude-haiku-5-5 the haiku control was served'),
    ('agent-payload', lambda: served_by('general-purpose', 'claude-sonnet-5-5'), ERROR,
     'the general-purpose control with model haiku was served the session model claude-sonnet-5-5, so a pin '
     'cannot be told from it'),
    ('agent-payload', lambda: {'payloads.json': '[]'}, ERROR, 'the PreToolUse hooks logged no subagent dispatch'),
```

These cases replay the recorded fixtures, which Step 4 already saved, so they pass as soon as they are written. Check that each one can fail: in the first case, change the expected finding's `Task` to `Tusk`, run the test, and see it fail on the finding. Then revert the change.

- [x] **Step 6: Run the replay cases**

Run: `uv run python build/run_suites.py cc_guide -- test_probe_replay.py`
Expected: PASS, +7 against Step 4. If a finding differs only in a model id the recording used (Step 4), fix that string to the recorded id and add a `> Deviation:` note. Any other difference is a defect: stop and report it.

- [x] **Step 7: Run the suite and commit**

> Deviation: the commit message adds one sentence on `--allow-old`. The plan file went into its own commit, 641d41e, since the `git add` list does not name it.

Run: `uv run python build/run_suites.py cc_guide`
Expected: PASS, +8 against the end of Task 2.

Read the appended row: `tail -n 1 build/cc_guide/PROBES.md`. Expected: a `| <date> | <version> | ~/… | agent-payload | PASS | dispatches reach … |` row, whose Binary cell starts with `~` or a path outside the home directory, and whose Flags cell holds `--allow-old` only if the owner approved it.

Run `uv run python build/cc_guide/cli.py lint` (expected: exit 0) and `build/run_commit_lints.sh` (expected: exit 0), then:

```bash
git add build/cc_guide/probes.py build/cc_guide/manifest.toml build/cc_guide/test_probes.py \
        build/cc_guide/test_probe_replay.py build/cc_guide/probe_streams/agent-payload.jsonl \
        build/cc_guide/probe_streams/agent-payload.payloads.json build/cc_guide/PROBES.md
git commit -m "$(cat <<'EOF'
feat(cc-guide): register the agent-payload probe with its first run

The probe joins PROBE_RUNS and manifest.toml beside agent-model-pins. Its
first live run on <version> passed, and its row is in PROBES.md.
save_fixtures recorded the run, and test_probe_replay.py replays it. Each new
DIVERGES and ERROR case pins its finding.

Co-Authored-By: <the session's trailer>
EOF
)"
```

---

### Task 5: Whole-plan checks

**Files:** none changed, unless a check fails.

- [x] **Step 1: Run the suites**

Run: `uv run python build/run_suites.py cc_guide build hooks`
Expected: all PASS. Against the plan's base commit: `cc_guide` +28 (17 + 3 + 8), `build` +28, since it collects `build/cc_guide/`, and `hooks` +0 on each of its two runs.

- [x] **Step 2: Run the lints**

Run, from the repo root:
- `build/run_commit_lints.sh` (expected: exit 0)
- `uv run python build/cc_guide/cli.py lint` (expected: exit 0)
- `uv run --with pyyaml python build/check_conformance.py` (expected: exit 0)
- `uv run python build/run_suites.py --check` (expected: exit 0; no new test directory)

- [x] **Step 3: Check the scope fence**

Run: `git diff --stat "$(git merge-base main HEAD)"..HEAD`
Expected: only the files in this plan's File map, plus the plan file itself. In particular, nothing under `hooks/` but `README.md`, no `specs/deferred_items.md` (until the Completion Protocol), no `.claude/skills/`, and no guide.

- [x] **Step 4: Completion**

Then run the Plan Completion Protocol (writing-plans). Its ticking pass marks this item in `specs/deferred_items.md`, section `63-conformance-gaps — 2026-10-21`: `- [x] Probe \`BUILTIN_PINNED\` and the Agent payload shape … → done in plan 69`. Re-read the file just before that edit, since another session may have changed it. The completion report names:
- the R4.3 coverage gaps (the payload fields and `claude-code-guide`'s pin);
- that item (l) of the plan 58 Minors batch had its revisit trigger fire (`probes.py` grew), and that none of that batch's items changed;
- that the new probe shares the remaining alias-remap exposure of the `deferred-2026-10-21` item, and that its control comparison is a third option for that item.
