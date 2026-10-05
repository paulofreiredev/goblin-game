import math
import pytest
from game.state import FIELD_LIMIT, Player, Storage


def test_movement_normalized_and_time_based():
    straight, diagonal, split = Player(), Player(), Player()
    straight.move(1, 0, False, 1)
    diagonal.move(1, 1, False, 1)
    for _ in range(10):
        split.move(1, 0, False, 0.1)
    assert math.hypot(diagonal.x, diagonal.y) == pytest.approx(straight.x)
    assert split.x == pytest.approx(straight.x)


@pytest.mark.parametrize('dx,dy,row', [(-1,0,0),(-1,1,1),(0,1,2),(1,1,3),(1,0,4),(1,-1,5),(0,-1,6),(-1,-1,7)])
def test_direction(dx, dy, row):
    player = Player()
    player.move(dx, dy, False, 0.1)
    assert player.direction == row


def test_run_idle_animation_and_limits():
    walk, run = Player(), Player()
    walk.move(1, 0, False, 1)
    run.move(1, 0, True, 1)
    assert run.x == walk.x * 2
    run.move(1, 0, True, 0.2)
    assert 4 <= run.frame <= 11
    run.move(0, 0, False, 0.2)
    assert run.animation == 'idle' and run.frame == 0
    run.move(1, -1, True, 100)
    assert run.x == FIELD_LIMIT and run.y == -FIELD_LIMIT


def test_save_continue_and_settings(tmp_path):
    storage = Storage(tmp_path)
    assert storage.load_player() is None
    assert storage.save_player(Player(12, -5, 3))
    assert storage.load_player() == Player(12, -5, 3)
    storage.write('settings.json', {'sound': False})
    assert Storage(tmp_path).read('settings.json')['sound'] is False


@pytest.mark.parametrize('content', ['invalid', '[]', '{}', '{"x":NaN,"y":0,"direction":0}', '{"x":0,"y":0,"direction":99}'])
def test_invalid_save_is_ignored(tmp_path, content):
    (tmp_path / 'save.json').write_text(content)
    assert Storage(tmp_path).load_player() is None


def test_coins_saved_and_new_player_starts_empty(tmp_path):
    storage = Storage(tmp_path)
    assert storage.save_player(Player(coins=7))
    assert storage.load_player().coins == 7
    assert Player().coins == 0


@pytest.mark.parametrize('coins', [None, -1, True, 1.5, '3'])
def test_invalid_coins_default_to_zero(tmp_path, coins):
    storage = Storage(tmp_path)
    storage.write('save.json', {'x': 0, 'y': 0, 'direction': 2, 'coins': coins})
    assert storage.load_player().coins == 0


def test_match_time_persists_and_legacy_defaults(tmp_path):
    storage = Storage(tmp_path)
    storage.save_player(Player(time_remaining=45.5))
    assert storage.load_player().time_remaining == 45.5
    storage.save_player(Player(time_remaining=0))
    assert storage.load_player().time_remaining == 0
    storage.write('save.json', {'x': 0, 'y': 0, 'direction': 2})
    assert storage.load_player().time_remaining == 120


@pytest.mark.parametrize('time', [None, -1, True, 211, '30', float('nan'), float('inf')])
def test_invalid_match_time_defaults(tmp_path, time):
    storage = Storage(tmp_path)
    storage.write('save.json', {'x': 0, 'y': 0, 'direction': 2, 'time_remaining': time})
    assert storage.load_player().time_remaining == 120


def test_bonus_time_survives_save(tmp_path):
    storage = Storage(tmp_path)
    storage.save_player(Player(time_remaining=210))
    assert storage.load_player().time_remaining == 210


@pytest.mark.parametrize('phase', [0, 1, 2])
def test_phase_saved(tmp_path, phase):
    storage = Storage(tmp_path)
    storage.save_player(Player(phase=phase))
    assert storage.load_player().phase == phase


@pytest.mark.parametrize('phase', [True, -1, 3])
def test_invalid_phase_uses_morning(tmp_path, phase):
    storage = Storage(tmp_path)
    storage.write('save.json', {'x': 0, 'y': 0, 'direction': 6, 'phase': phase})
    assert storage.load_player().phase == 0
