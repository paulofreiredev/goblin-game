"""Regras de coleta e persistência dos relógios sem janela."""
import math

from game.state import CLOCK_COUNT, Player, Storage
from game.world import Encounter, PLAYER_RADIUS, blocked, in_water


def quiet_encounter():
    encounter = Encounter()
    for enemy in encounter.enemies:
        enemy.x, enemy.y = 80, 80
    return encounter


def test_three_clocks_spread_over_clear_ground():
    encounter = Encounter()
    assert len(encounter.clocks) == CLOCK_COUNT == 3
    for index, clock in enumerate(encounter.clocks):
        assert not blocked(clock.x, clock.y, PLAYER_RADIUS)
        assert not in_water(clock.x, clock.y)
        for other in encounter.clocks[index + 1:]:
            assert math.hypot(clock.x - other.x, clock.y - other.y) > 20


def test_collect_each_clock_once_and_add_ninety_seconds():
    encounter = quiet_encounter()
    player = Player()
    for index, clock in enumerate(encounter.clocks, 1):
        player.x, player.y = clock.x, clock.y
        encounter.update(player, 0)
        assert player.time_remaining == 120 + 30 * index
        assert clock.collected
        encounter.update(player, 0)
        assert player.time_remaining == 120 + 30 * index
    assert player.coins == 0


def test_clock_requires_proximity_and_low_jump():
    encounter = quiet_encounter()
    clock = encounter.clocks[0]
    player = Player(x=clock.x + 1.21, y=clock.y)
    encounter.update(player, 0)
    assert not clock.collected
    player.x, player.z = clock.x, 1.0
    encounter.update(player, 0)
    assert not clock.collected
    player.z = 0.9
    encounter.update(player, 0)
    assert clock.collected and player.time_remaining == 150


def test_clocks_do_not_revive_expired_or_extend_won_match():
    encounter = quiet_encounter()
    clock = encounter.clocks[0]
    player = Player(x=clock.x, y=clock.y, time_remaining=0)
    encounter.update(player, 0)
    assert not clock.collected and player.time_remaining == 0
    player.time_remaining = 50
    for enemy in encounter.enemies:
        enemy.health = 0
    encounter.update(player, 0)
    assert not clock.collected and player.time_remaining == 50


def test_clock_save_resume_legacy_and_restart(tmp_path):
    encounter = quiet_encounter()
    clock = encounter.clocks[0]
    player = Player(x=clock.x, y=clock.y)
    encounter.update(player, 0)
    storage = Storage(tmp_path)
    assert storage.save_player(player, clocks=encounter.clock_snapshot())
    restored = quiet_encounter()
    restored.restore_clocks(storage.read('save.json')['clocks'])
    loaded = storage.load_player()
    restored.update(loaded, 0)
    assert loaded.time_remaining == 150
    assert restored.clocks[0].collected
    for invalid in (None, [], [True, False], [1, False, False]):
        fresh = Encounter()
        fresh.restore_clocks(invalid)
        assert not any(clock.collected for clock in fresh.clocks)
    assert not any(clock.collected for clock in Encounter().clocks)
