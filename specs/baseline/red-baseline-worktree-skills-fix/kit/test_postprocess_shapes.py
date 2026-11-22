'''More input shapes for postprocess.py, beside the three plan tests of test_postprocess.py.

Each test names the rule of postprocess.py's docstring that it covers. The raw dicts are synthetic.
'''
import json

import pytest

import postprocess as module
from postprocess import postprocess

CLEAN = {'result': 'ok', 'result_index': 0, 'origin': None}


def test_a_later_peer_turn_voids_whatever_the_index():
    assert postprocess({**CLEAN, 'result_index': 2})['reason'] == 'result_index'


def test_index_zero_with_no_origin_is_kept():
    # The boundary: 0 is the answer a kit scores.
    rep = postprocess(dict(CLEAN))
    assert rep['void'] is False
    assert rep['result_index'] == 0


def test_a_rep_with_no_result_index_or_origin_key_is_kept():
    rep = postprocess({'result': 'ok'})
    assert rep == {'void': False, 'result': 'ok'}


@pytest.mark.parametrize('origin', [{}, {'kind': 'peer', 'session_title': 'x'}, 'peer'])
def test_any_origin_that_is_not_null_voids_the_rep(origin):
    rep = postprocess({**CLEAN, 'origin': origin})
    assert rep == {'void': True, 'reason': 'origin'}


@pytest.mark.parametrize('index', ['0', 0.0, 1.0, True, False, None, [0]])
def test_a_result_index_that_is_not_a_whole_number_voids_the_rep(index):
    rep = postprocess({**CLEAN, 'result_index': index})
    assert rep == {'void': True, 'reason': 'result_index'}


def test_result_index_is_named_first_when_both_fields_show_a_peer_turn():
    rep = postprocess({'result': 'x', 'result_index': 3, 'origin': {'kind': 'peer'}})
    assert rep['reason'] == 'result_index'


def test_a_void_marker_holds_no_answer_text():
    rep = postprocess({'result': 'a reply to a peer', 'result_index': 1, 'origin': {'session_id': 's'}})
    assert rep == {'void': True, 'reason': 'result_index'}


def test_the_private_keys_go_at_any_depth():
    raw = {'result': 'ok', 'result_index': 0, 'origin': None, 'session_id': 's', 'uuid': 'u',
           'credential_expires_at': 1,
           'modelUsage': {'claude-sonnet-5-5': {'costUSD': 0.01, 'credential_expires_at': 2}},
           'iterations': [{'type': 'message', 'origin': {'kind': 'x'}, 'uuid': 'u2'}]}
    rep = postprocess(raw)
    assert rep == {'void': False, 'result': 'ok', 'result_index': 0,
                   'modelUsage': {'claude-sonnet-5-5': {'costUSD': 0.01}},
                   'iterations': [{'type': 'message'}]}


def test_every_string_is_scrubbed_home_tmpdir_and_identity(monkeypatch):
    monkeypatch.setenv('HOME', '/Users/zed')
    monkeypatch.setenv('TMPDIR', '/var/folders/ab/cd/T/')
    monkeypatch.setattr(module.kit_identity, 'forms', lambda: [('Dana Quill', '<USER-NAME>')])
    raw = {'result': 'Dana Quill wrote /Users/zed/notes.md in /private/var/folders/ab/cd/T/run1',
           'modelUsage': {'Dana Quill': {'note': ['see /var/folders/ab/cd/T/x']}}}
    rep = postprocess(raw)
    assert rep['result'] == '<USER-NAME> wrote ~/notes.md in $TMPDIR/run1'
    assert rep['modelUsage'] == {'<USER-NAME>': {'note': ['see $TMPDIR/x']}}


def test_the_scrub_leaves_a_string_with_no_private_form_alone(monkeypatch):
    monkeypatch.setenv('HOME', '/Users/zed')
    monkeypatch.setenv('TMPDIR', '/var/folders/ab/cd/T/')
    monkeypatch.setattr(module.kit_identity, 'forms', lambda: [('Dana Quill', '<USER-NAME>')])
    assert postprocess({'result': 'RUN: git worktree add .worktrees/x -b x'})['result'] == \
        'RUN: git worktree add .worktrees/x -b x'


def run_main(tmp_path, raw_text):
    raw = tmp_path / 'raw.json'
    if raw_text is not None:
        raw.write_text(raw_text)
    dest, note = tmp_path / 'rep1.json', tmp_path / 'rep1.VOID'
    return module.main([str(raw), str(dest), str(note)]), dest, note


def test_the_command_line_keeps_a_clean_rep_as_scrubbed_json_without_the_void_key(tmp_path, capsys):
    code, dest, note = run_main(tmp_path, json.dumps({**CLEAN, 'credential_expires_at': 5, 'session_id': 's'}))
    assert code == 0
    assert capsys.readouterr().out.strip() == 'kept'
    assert json.loads(dest.read_text()) == {'result': 'ok', 'result_index': 0}
    assert not note.exists()


def test_the_command_line_voids_a_peer_rep_with_a_note_and_no_json(tmp_path, capsys):
    code, dest, note = run_main(tmp_path, json.dumps({'result': 'a reply to a peer', 'result_index': 1}))
    assert code == 0
    assert capsys.readouterr().out.strip() == 'void result_index'
    assert note.read_text().startswith('VOID: result_index')
    assert 'a reply to a peer' not in note.read_text()
    assert not dest.exists()


@pytest.mark.parametrize('raw_text', [None, '', 'not json', '[1, 2]'])
def test_the_command_line_voids_an_unreadable_raw_file(tmp_path, capsys, raw_text):
    code, dest, note = run_main(tmp_path, raw_text)
    assert code == 0
    assert capsys.readouterr().out.strip() == 'unreadable'
    assert note.read_text().startswith('VOID:')
    assert not dest.exists()


def test_the_command_line_refuses_the_wrong_number_of_arguments(capsys):
    assert module.main(['one']) == 2
