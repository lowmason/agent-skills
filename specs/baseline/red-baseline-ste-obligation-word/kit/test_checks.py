'''No-model tests for the mechanical checks in cases.py.

Run from this directory: uv run --with pytest python -m pytest -q
'''
import cases

SOURCE_C = cases.AGENT_SOURCES['C']
SOURCE_A = cases.AGENT_SOURCES['A']


def test_a_kept_should_raises_no_obligation_flag():
    assert cases.obligation_flags('The downstream agent should consume the artifact.', SOURCE_C) == []


def test_a_bare_command_for_should_raises_a_flag():
    assert len(cases.obligation_flags('Consume the artifact.', SOURCE_C)) == 1


def test_must_for_should_raises_a_flag():
    assert cases.obligation_flags('The agent must consume the artifact.', SOURCE_C) != []


def test_should_kept_only_in_a_kept_as_is_line_raises_a_flag():
    reply = 'Consume the artifact.\n\nKept as-is: "should", to keep the modality.\n'
    assert len(cases.obligation_flags(reply, SOURCE_C)) == 1


def test_ought_to_keeps_the_strength_of_should():
    assert cases.obligation_flags('The downstream agent ought to consume the artifact.', SOURCE_C) == []


def test_a_new_obligation_word_raises_a_flag():
    assert cases.obligation_flags('The tool must sync the state.', SOURCE_A) != []


def test_a_source_with_no_obligation_word_and_a_plain_rewrite_raises_no_flag():
    assert cases.obligation_flags('The tool tries to sync the state.', SOURCE_A) == []


def test_the_rewritten_block_drops_fences_and_stops_at_notes_and_tables():
    reply = f'{cases.FENCE}\nThe agent should wait.\n{cases.FENCE}\n\nFlag: "should" is kept.\n'
    assert cases.rewritten_block(reply) == 'The agent should wait.'
    assert cases.rewritten_block('Wait.\n\n| Before | After |\n|---|---|\n| should | should |\n') == 'Wait.'
    assert cases.rewritten_block('Wait.\n\n**Kept as-is:** should.\n') == 'Wait.'


def test_a_sentence_over_the_cap_raises_a_flag():
    long = ' '.join(['word'] * 21) + '.'
    assert len(cases.sentence_cap_flags(long, 20)) == 1
    assert cases.sentence_cap_flags('Short sentence here.', 20) == []


def test_a_sentence_at_the_cap_raises_no_flag():
    assert cases.sentence_cap_flags(' '.join(['word'] * 20) + '.', 20) == []
