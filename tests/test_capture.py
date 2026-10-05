from game.capture import CaptureMatch, LOCAL_DEFAULTS, load_local_controls, replace_local_key


def test_three_captures_win_and_own_flag_must_be_home():
    match = CaptureMatch()
    player = match.players[0]
    for score in range(1, 4):
        player.x, player.y = match.flags[1].home
        match.update()
        assert match.flags[1].carrier == 0
        player.x, player.y = match.flags[0].home
        if score == 1:
            match.flags[0].carrier = 1
            match.update()
            assert match.scores[0] == 0
            match.flags[0].reset()
        match.update()
        assert match.scores[0] == score
        assert match.flags[1].at_home
    assert match.winner == 0
    match.update()
    assert match.scores == [3, 0]


def test_tag_drops_flag_respawns_and_owner_returns_it():
    match = CaptureMatch()
    attacker, opponent = match.players
    attacker.x, attacker.y, attacker.direction = 0, 0, 4
    opponent.x, opponent.y = 2, 0
    match.flags[0].carrier = 1
    assert match.attack(0)
    assert (opponent.x, opponent.y) == match.bases[1]
    assert match.flags[0].carrier is None
    assert not match.attack(0)
    attacker.x = 2
    match.update()
    assert match.flags[0].at_home


def test_tag_requires_range_and_facing():
    match = CaptureMatch()
    attacker, opponent = match.players
    attacker.x, attacker.y, attacker.direction = 0, 0, 0
    opponent.x, opponent.y = 2, 0
    assert not match.attack(0)
    attacker.attack_time = 0
    attacker.direction, opponent.x = 4, 10
    assert not match.attack(0)


def test_independent_local_controls_swap_and_persist():
    controls = load_local_controls({})
    updated = replace_local_key(controls, 0, 'up', 'arrow_up')
    assert updated[0]['up'] == 'arrow_up'
    assert updated[1]['up'] == 'w'
    assert load_local_controls({'local_controls': updated}) == updated
    assert controls == LOCAL_DEFAULTS
