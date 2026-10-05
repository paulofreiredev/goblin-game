import random
import pytest
from game.capture import CaptureMatch, LOCAL_DEFAULTS, load_local_controls, replace_local_key
from game.world import blocked, terrain_height


@pytest.mark.parametrize('difficulty,count', [('easy', 3), ('medium', 8), ('hard', 12)])
def test_own_color_random_flags_and_first_to_collect_all_wins(difficulty, count):
    match = CaptureMatch(difficulty, random.Random(1))
    assert len(match.flags) == count * 2
    assert all(sum(flag.team == team for flag in match.flags) == count for team in range(2))
    player = match.players[0]
    blue = next(flag for flag in match.flags if flag.team == 1)
    player.x, player.y = blue.x, blue.y
    match.update()
    assert match.scores == [0, 0] and not blue.captured
    for index, flag in enumerate(flag for flag in match.flags if flag.team == 0):
        player.x, player.y = flag.x, flag.y
        match.update()
        assert match.scores[0] == index + 1 and flag.captured
        if index < count - 1:
            assert match.winner is None
    assert match.winner == 0
    match.update()
    assert match.scores == [count, 0]


def test_distribution_is_random_separated_and_accessible():
    first = CaptureMatch('hard', random.Random(2))
    second = CaptureMatch('hard', random.Random(3))
    assert [(flag.x, flag.y) for flag in first.flags] != [(flag.x, flag.y) for flag in second.flags]
    for flag in first.flags:
        assert not blocked(flag.x, flag.y, 1)
        assert terrain_height(flag.x, flag.y) == 0
        assert -75 <= flag.x <= 75 and -75 <= flag.y <= 75


def test_jump_does_not_collect_ground_flag_and_blue_can_win():
    match = CaptureMatch('easy', random.Random(2))
    player = match.players[1]
    for flag in (flag for flag in match.flags if flag.team == 1):
        player.x, player.y, player.z = flag.x, flag.y, 2
        before = match.scores[1]
        match.update()
        assert match.scores[1] == before
        player.z = 0
        match.update()
    assert match.winner == 1 and match.scores == [0, 3]


def test_tag_requires_range_and_facing_and_keeps_collected_flags():
    match = CaptureMatch('easy', random.Random(1))
    attacker, opponent = match.players
    attacker.x, attacker.y, attacker.direction = 0, 0, 0
    opponent.x, opponent.y = 2, 0
    assert not match.attack(0)
    attacker.attack_time = 0
    attacker.direction, opponent.x = 4, 10
    assert not match.attack(0)
    attacker.attack_time = 0
    opponent.x = 2
    match.flags[0].captured = True
    assert match.attack(0)
    assert (opponent.x, opponent.y) == match.bases[1]
    assert match.flags[0].captured
    assert not match.attack(0)


def test_independent_local_controls_swap_and_persist():
    controls = load_local_controls({})
    updated = replace_local_key(controls, 0, 'up', 'arrow_up')
    assert updated[0]['up'] == 'arrow_up' and updated[1]['up'] == 'w'
    assert load_local_controls({'local_controls': updated}) == updated
    assert controls == LOCAL_DEFAULTS
