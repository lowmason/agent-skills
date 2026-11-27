'''No-model tests for kit.py: the symlink fixture, the scrub, the void rules, a stub run and the flag sheet.

Run from this directory: uv run --with pytest python -m pytest -q
'''
import json
import os
import subprocess
import sys
from pathlib import Path

import cases
import kit

KIT = Path(__file__).resolve().parent
CONTROL_COMMIT = '4168d2a'
STUB = '''#!{PY}
import json, os, sys
prompt = sys.stdin.read()
log = {LOG!r}
os.makedirs(log, exist_ok=True)
with open(os.path.join(log, os.path.basename(os.environ['HOME']) + '.json'), 'w') as fh:
    json.dump({{'argv': sys.argv[1:], 'env': dict(os.environ), 'cwd': os.getcwd(), 'prompt': prompt}}, fh)
lines = [
    {{'type': 'system', 'subtype': 'init', 'tools': [], 'session_id': 's1', 'uuid': 'u1'}},
    {{'type': 'assistant', 'message': {{'content': [{{'type': 'text', 'text': {REPLY!r}}}]}}, 'uuid': 'u2'}},
    {{'type': 'result', 'subtype': 'success', 'is_error': False, 'result': {REPLY!r}, 'result_index': 0,
      'total_cost_usd': 0.01, 'session_id': 's1', 'credential_expires_at': 123, 'origin': None}},
]
for line in lines:
    print(json.dumps(line))
'''
PLANNED_ENV = {'HOME', 'USER', 'LOGNAME', 'SHELL', 'LANG', 'TMPDIR', 'PATH',
               'CLAUDE_CODE_DISABLE_ADVISOR_TOOL', 'CLAUDE_CODE_DISABLE_AUTO_MEMORY'}


def kit_env(tmp_path: Path, reply: str) -> dict:
    stub = tmp_path / 'claude'
    # The test's own Python: /usr/bin/python3 is Xcode's shim, which adds CPATH, SDKROOT and others itself.
    stub.write_text(STUB.format(PY=sys.executable, LOG=str(tmp_path / 'log'), REPLY=reply), encoding='utf-8')
    stub.chmod(0o755)
    keychains = tmp_path / 'realhome' / 'Library' / 'Keychains'
    keychains.mkdir(parents=True)
    return {**os.environ, 'STE114_ROOT': str(tmp_path / 'root'), 'STE114_SCRATCH': str(tmp_path / 'scratch'),
            'STE114_RUNS': str(tmp_path / 'runs'), 'STE114_CLAUDE': str(stub),
            'STE114_REAL_HOME': str(tmp_path / 'realhome')}


def run_kit(env: dict, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(KIT / 'kit.py'), *args], cwd=KIT, env=env, capture_output=True,
                          text=True)


def test_the_symlink_fixture_is_the_case_that_fix_4_reproduced(tmp_path):
    repo = tmp_path / 'repo'
    kit.build_fixture(cases.BY_ID['doc-symlink'], repo)
    assert subprocess.run(['test', '!', '-L', 'docs/guide.md'], cwd=repo).returncode != 0
    assert subprocess.run(['git', 'ls-files', '--error-unmatch', 'docs/guide.md'], cwd=repo,
                          capture_output=True).returncode == 0
    status = subprocess.run(['git', 'status', '--porcelain', '--', 'docs/guide.md'], cwd=repo, capture_output=True,
                            text=True)
    assert status.returncode == 0 and status.stdout == ''
    assert (repo / 'docs/manual.md').read_text(encoding='utf-8') == cases.DIRTY_GUIDE


def test_the_symlink_checks_pass_for_a_copy_and_fail_for_a_rewrite_through_the_link(tmp_path):
    case = cases.BY_ID['doc-symlink']
    repo = tmp_path / 'repo'
    kit.build_fixture(case, repo)
    (repo / 'docs/guide.ste.md').write_text('# Label printer setup\n', encoding='utf-8')
    assert all(kit.doc_checks(case, kit.snapshot(case, repo)).values())
    (repo / 'docs/guide.md').write_text('rewritten\n', encoding='utf-8')
    checks = kit.doc_checks(case, kit.snapshot(case, repo))
    assert checks['target untouched'] is False and checks['link kept'] is True


def test_scrub_drops_the_identifying_keys_at_any_depth():
    raw = {'a': 1, 'session_id': 's', 'x': [{'uuid': 'u', 'origin': {'kind': 'peer'}, 'credential_expires_at': 1}]}
    assert kit.scrub(raw) == {'a': 1, 'x': [{}]}


def records(result: dict, *extra: dict) -> list:
    text = {'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': 'Reply.'}]}}
    return [{'type': 'system', 'subtype': 'init', 'tools': []}, text, *extra,
            {'type': 'result', 'is_error': False, 'result': 'Reply.', 'result_index': 0, **result}]


def test_void_rules_catch_each_case():
    assert kit.void_reason(records({}), '') is None
    assert kit.void_reason([], '').startswith('V1')
    assert kit.void_reason(records({'result_index': 1}), '').startswith('V4')
    assert kit.void_reason(records({'result_index': '0'}), '').startswith('V4')
    assert kit.void_reason(records({'origin': {'kind': 'peer'}}), '').startswith('V4')
    use = {'type': 'assistant', 'message': {'content': [{'type': 'tool_use', 'name': 'Read', 'input': {}}]}}
    assert kit.void_reason(records({}, use), '').startswith('V2')
    listed = records({})
    listed[0]['tools'] = ['Bash', 'SendMessage']
    assert kit.void_reason(listed, 'Bash').startswith('V5')
    assert kit.void_reason(records({'permission_denials': [{'tool_name': 'Bash'}]}), 'Bash').startswith('V3')


def test_a_stub_rep_runs_in_its_own_home_with_the_planned_environment_and_a_scrubbed_copy(tmp_path):
    env = kit_env(tmp_path, 'The downstream agent should consume the artifact.')
    assert run_kit(env, 'freeze', 'control', CONTROL_COMMIT).returncode == 0
    done = run_kit(env, 'run', 'control', 'agent-instruction', 'claude-sonnet-5-5', '--good', '1', '--jobs', '1')
    assert done.returncode == 0, done.stdout + done.stderr
    (logged,) = [json.loads(p.read_text(encoding='utf-8')) for p in (tmp_path / 'log').iterdir()]
    # macOS sets __CF_USER_TEXT_ENCODING in a new process by itself when it is missing.
    assert set(logged['env']) - {'__CF_USER_TEXT_ENCODING'} == PLANNED_ENV
    home = Path(logged['env']['HOME'])
    assert home.parent == tmp_path / 'root' and logged['env']['TMPDIR'] == str(home / 'tmp')
    assert Path(logged['cwd']) == home / 'work'
    argv = logged['argv']
    assert argv[argv.index('--tools') + 1] == 'Read'
    assert argv[argv.index('--append-system-prompt') + 1].startswith(f'Base directory for this skill: {home}/skill/')
    settings = json.loads(argv[argv.index('--settings') + 1])
    assert set(kit.CROSS_SESSION_TOOLS) <= set(settings['permissions']['deny'])
    assert not home.exists() and (tmp_path / 'scratch' / 'homes' / home.name / '.claude/rules').is_dir()
    kept = (tmp_path / 'runs' / 'reps' / home.name / 'stream.jsonl').read_text(encoding='utf-8')
    for key in kit.SCRUB_KEYS:
        assert f'"{key}"' not in kept
    assert '"credential_expires_at"' in (tmp_path / 'scratch' / 'raw' / home.name / 'stream.jsonl').read_text()


def test_flag_rows_do_not_differ_by_arm(tmp_path):
    env = kit_env(tmp_path, 'Consume the artifact. ' + ' '.join(['word'] * 22) + '.')
    for arm in ('control', 'treatment'):
        assert run_kit(env, 'freeze', arm, CONTROL_COMMIT).returncode == 0
        done = run_kit(env, 'run', arm, 'agent-instruction', 'claude-opus-5-5', '--good', '1', '--jobs', '1')
        assert done.returncode == 0, done.stdout + done.stderr
    assert run_kit(env, 'flags').returncode == 0
    rows = kit.read_tsv(tmp_path / 'runs' / 'flags.tsv', kit.FLAG_FIELDS)
    by_rep = {}
    for row in rows:
        by_rep.setdefault(row['rep'], set()).add(tuple(row[f] for f in ('case', 'check', 'detail', 'context')))
    assert len(by_rep) == 2 and len(set(map(frozenset, by_rep.values()))) == 1
    text = (tmp_path / 'runs' / 'flags.tsv').read_text(encoding='utf-8')
    for word in ('control', 'treatment', *kit.MODELS):
        assert word not in text


def test_unread_flags_fail_the_tally_and_justified_flags_pass_it(tmp_path):
    env = kit_env(tmp_path, 'Consume the artifact.')
    assert run_kit(env, 'freeze', 'control', CONTROL_COMMIT).returncode == 0
    assert run_kit(env, 'run', 'control', 'agent-instruction', 'claude-opus-5-5', '--jobs', '5').returncode == 0
    reps = [r['rep'] for r in kit.read_tsv(tmp_path / 'runs' / 'registry.tsv', kit.REGISTRY_FIELDS)]
    write_judge(tmp_path, 'control', 'agent-instruction', 'claude-opus-5-5', dict.fromkeys(reps, True))
    assert run_kit(env, 'flags').returncode == 0
    assert 'agent-instruction claude-opus-5-5 0/5 FAIL (obligation 0/5)' in run_kit(env, 'tally').stdout
    flags = tmp_path / 'runs' / 'flags.tsv'
    rows = kit.read_tsv(flags, kit.FLAG_FIELDS)
    kit.write_tsv(flags, kit.FLAG_FIELDS, [{**r, 'verdict': 'justified', 'reason': 'test'} for r in rows])
    assert 'agent-instruction claude-opus-5-5 5/5 PASS (obligation 5/5)' in run_kit(env, 'tally').stdout


def test_an_agent_case_scores_the_final_message_and_a_document_case_scores_every_message():
    recs = [{'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': 'I should read agent-mode.md.'}]}},
            {'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': 'Consume the artifact.'}]}},
            {'type': 'result', 'is_error': False, 'result': 'Consume the artifact.', 'result_index': 0}]
    assert kit.reply_text(recs, final=True) == 'Consume the artifact.'
    assert kit.reply_text(recs).startswith('I should read')
    assert len(cases.obligation_flags(kit.reply_text(recs, final=True), cases.AGENT_SOURCES['C'])) == 1


def test_flag_ids_stay_unique_when_new_reps_add_flags(tmp_path):
    env = kit_env(tmp_path, 'Consume the artifact.')
    assert run_kit(env, 'freeze', 'control', CONTROL_COMMIT).returncode == 0
    assert run_kit(env, 'run', 'control', 'agent-instruction', 'claude-opus-5-5', '--good', '2', '--jobs', '2').returncode == 0
    assert run_kit(env, 'flags').returncode == 0
    assert run_kit(env, 'run', 'control', 'agent-instruction', 'claude-sonnet-5-5', '--good', '2', '--jobs', '2').returncode == 0
    for model in ('claude-opus-5-5', 'claude-sonnet-5-5'):
        reps = [r['rep'] for r in kit.read_tsv(tmp_path / 'runs' / 'registry.tsv', kit.REGISTRY_FIELDS) if r['model'] == model]
        write_judge(tmp_path, 'control', 'agent-instruction', model, dict.fromkeys(reps, True))
    assert run_kit(env, 'flags').returncode == 0
    ids = [r['flag'] for r in kit.read_tsv(tmp_path / 'runs' / 'flags.tsv', kit.FLAG_FIELDS)]
    assert len(ids) == 4 and len(set(ids)) == 4


# ---- final-review fixes (plan 114, D10 and D12, Codex and code-reviewer findings) ----

def bash_use(command: str) -> dict:
    return {'type': 'assistant', 'message': {'content': [{'type': 'tool_use', 'name': 'Bash', 'input': {'command': command}}]}}


def test_v3_voids_a_tool_rep_that_writes_outside_its_home():
    home = '/private/tmp/ste114/rabc123'
    assert kit.void_reason(records({}, bash_use('cp docs/manual.md /tmp/rewritten.md')), 'Bash', home).startswith('V3')


def test_v3_keeps_a_tool_rep_that_stays_in_its_home_or_uses_system_paths():
    home = '/private/tmp/ste114/rabc123'
    inside = bash_use(f'cd {home}/work/repo; /usr/bin/python3 {home}/skill/x.py 2>/dev/null')
    assert kit.void_reason(records({}, inside), 'Bash', home) is None
    tmp_form = bash_use('cat /tmp/ste114/rabc123/work/repo/docs/guide.md')
    assert kit.void_reason(records({}, tmp_form), 'Bash', home) is None


def test_scrub_redacts_the_account_name_in_values():
    assert kit.scrub({'stdout': 'lrwxr-xr-x@ 1 alice  wheel  9 guide.md'}, user='alice') == \
        {'stdout': 'lrwxr-xr-x@ 1 <user>  wheel  9 guide.md'}


def test_an_agent_rep_with_an_empty_final_message_is_void():
    recs = records({'result': ''})
    assert kit.void_reason(recs, 'Read', final=True).startswith('V1')


def test_parallel_spend_appends_lose_no_row(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    path = tmp_path / 'spend.tsv'
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda n: kit.append_tsv(path, ('what', 'cost'), {'what': f'rep r{n}', 'cost': '0.01'}), range(40)))
    assert len(kit.read_tsv(path, ('what', 'cost'))) == 40


def test_a_case_with_checks_and_no_judge_file_fails_the_tally(tmp_path):
    env = kit_env(tmp_path, 'The downstream agent should consume the artifact.')
    assert run_kit(env, 'freeze', 'control', CONTROL_COMMIT).returncode == 0
    assert run_kit(env, 'run', 'control', 'agent-instruction', 'claude-opus-5-5', '--jobs', '5').returncode == 0
    assert run_kit(env, 'flags').returncode == 0
    assert 'agent-instruction claude-opus-5-5 0/5 FAIL' in run_kit(env, 'tally').stdout


def write_judge(tmp_path: Path, arm: str, case_id: str, model: str, passes: dict) -> None:
    '''A judge file that passes every check of the listed reps, or fails check 1 where passes[rep] is False.'''
    case = cases.BY_ID[case_id]
    table = {rep: {str(n): {'pass': ok or n != 1, 'why': 'test'} for n in range(1, len(case.checks) + 1)}
             for rep, ok in passes.items()}
    target = tmp_path / 'runs' / 'judge' / kit.judge_file(arm, case_id, model).name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({'case': case_id, 'verdicts': table}), encoding='utf-8')


def test_four_of_five_passes_the_bar_and_three_of_five_fails_it(tmp_path):
    env = kit_env(tmp_path, 'The downstream agent should consume the artifact.')
    assert run_kit(env, 'freeze', 'control', CONTROL_COMMIT).returncode == 0
    assert run_kit(env, 'run', 'control', 'agent-instruction', 'claude-opus-5-5', '--jobs', '5').returncode == 0
    reps = [r['rep'] for r in kit.read_tsv(tmp_path / 'runs' / 'registry.tsv', kit.REGISTRY_FIELDS)]
    write_judge(tmp_path, 'control', 'agent-instruction', 'claude-opus-5-5', {r: i != 0 for i, r in enumerate(reps)})
    assert run_kit(env, 'flags').returncode == 0
    flags = tmp_path / 'runs' / 'flags.tsv'
    rows = kit.read_tsv(flags, kit.FLAG_FIELDS)
    kit.write_tsv(flags, kit.FLAG_FIELDS, [{**r, 'verdict': 'count', 'reason': 'test'} for r in rows])
    assert 'agent-instruction claude-opus-5-5 4/5 PASS' in run_kit(env, 'tally').stdout
    write_judge(tmp_path, 'control', 'agent-instruction', 'claude-opus-5-5', {r: i > 1 for i, r in enumerate(reps)})
    assert run_kit(env, 'flags').returncode == 0
    rows = kit.read_tsv(flags, kit.FLAG_FIELDS)
    kit.write_tsv(flags, kit.FLAG_FIELDS, [{**r, 'verdict': 'count', 'reason': 'test'} for r in rows])
    assert 'agent-instruction claude-opus-5-5 3/5 FAIL' in run_kit(env, 'tally').stdout


def test_a_document_rep_that_fails_its_mechanical_check_fails_the_tally(tmp_path):
    env = kit_env(tmp_path, 'I rewrote the file.')
    assert run_kit(env, 'freeze', 'control', CONTROL_COMMIT).returncode == 0
    assert run_kit(env, 'run', 'control', 'doc-symlink', 'claude-opus-5-5', '--jobs', '5').returncode == 0
    assert run_kit(env, 'flags').returncode == 0
    # The stub writes nothing, so no copy exists: every rep fails "copy written".
    assert 'doc-symlink claude-opus-5-5 0/5 FAIL' in run_kit(env, 'tally').stdout


def test_a_set_aside_row_never_counts(tmp_path):
    env = kit_env(tmp_path, 'The downstream agent should consume the artifact.')
    assert run_kit(env, 'freeze', 'control', CONTROL_COMMIT).returncode == 0
    reg = tmp_path / 'runs' / 'registry.tsv'
    kit.write_tsv(reg, kit.REGISTRY_FIELDS, [{'rep': 'rold', 'arm': 'control', 'case': 'agent-instruction',
                                              'model': 'claude-opus-5-5', 'status': 'set aside (D8)', 'cost': '0'}])
    assert run_kit(env, 'run', 'control', 'agent-instruction', 'claude-opus-5-5', '--good', '2', '--jobs', '2').returncode == 0
    rows = kit.read_tsv(reg, kit.REGISTRY_FIELDS)
    assert len(rows) == 3 and sum(r['status'] == 'good' for r in rows) == 2


def test_revoid_applies_the_current_void_rules_and_redacts_kept_streams(tmp_path):
    env = kit_env(tmp_path, 'The downstream agent should consume the artifact.')
    assert run_kit(env, 'freeze', 'control', CONTROL_COMMIT).returncode == 0
    assert run_kit(env, 'run', 'control', 'agent-instruction', 'claude-opus-5-5', '--good', '1', '--jobs', '1').returncode == 0
    (row,) = kit.read_tsv(tmp_path / 'runs' / 'registry.tsv', kit.REGISTRY_FIELDS)
    kept = tmp_path / 'runs' / 'reps' / row['rep'] / 'stream.jsonl'
    use = bash_use('cp a /tmp/out.md')
    kept.write_text(kept.read_text(encoding='utf-8') + json.dumps(use) + '\n' +
                    json.dumps({'type': 'user', 'note': f'owner {os.environ["USER"]} here'}) + '\n', encoding='utf-8')
    done = run_kit(env, 'revoid')
    assert done.returncode == 0, done.stderr
    (row,) = kit.read_tsv(tmp_path / 'runs' / 'registry.tsv', kit.REGISTRY_FIELDS)
    assert row['status'].startswith('V3')
    assert os.environ['USER'] not in kept.read_text(encoding='utf-8')
