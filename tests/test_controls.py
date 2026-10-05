import pytest
from game.controls import load_controls, valid_action_key


def test_legacy_and_saved_action_keys():
    assert load_controls({'sound': False}) == ('space', 'x')
    assert load_controls({'jump_key': 'e', 'attack_key': 'q'}) == ('e', 'q')
    assert load_controls({'jump_key': 'x', 'attack_key': 'x'}) == ('x', 'space')


@pytest.mark.parametrize('key', ['w', 'a', 's', 'd', 'escape', 'shift', 'mouse1', None, []])
def test_reserved_or_invalid_keys_are_rejected(key):
    assert not valid_action_key(key)
    assert load_controls({'jump_key': key, 'attack_key': key}) == ('space', 'x')
