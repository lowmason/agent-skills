'''Self-test for plan 103's micro-test kit: postprocess() voids or keeps one rep's raw JSON.

The tests use synthetic dicts, so no model runs. The next-kit item they close is "Void a no-tools rep
that took a peer message" (specs/deferred_items.md): the kit voids a rep whose JSON has `result_index`
above 0 or an `origin` that is not null, and it drops `origin` from every rep it keeps.
'''
from postprocess import postprocess


def test_a_peer_turn_voids_the_rep():
    # A message sent to a busy no-tools rep arrives as an extra turn. The JSON `result` is then the
    # reply to that message, and `result_index` is 1.
    rep = postprocess({'result': 'a reply to a peer', 'result_index': 1, 'origin': None})
    assert rep['void'] is True
    assert rep['reason'] == 'result_index'


def test_an_origin_voids_the_rep():
    rep = postprocess({'result': 'a reply to a peer', 'result_index': 0, 'origin': {'kind': 'peer'}})
    assert rep['void'] is True
    assert rep['reason'] == 'origin'


def test_a_clean_rep_is_kept_without_origin_or_credential_expiry():
    rep = postprocess({'result': 'ok', 'result_index': 0, 'origin': None, 'credential_expires_at': 1790000000})
    assert rep['void'] is False
    assert 'origin' not in rep
    assert 'credential_expires_at' not in rep
    assert rep['result'] == 'ok'
