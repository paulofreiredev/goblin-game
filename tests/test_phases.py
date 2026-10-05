"""Regras de quantidade de monstros, sem contexto gráfico."""
import pytest
from game.state import Player
from game.world import Encounter, PLAYER_RADIUS, blocked


@pytest.mark.parametrize('difficulty,count', [('easy', 3), ('medium', 8), ('hard', 12)])
def test_difficulty_spawns_and_requires_all_monsters(difficulty, count):
    encounter = Encounter(difficulty=difficulty)
    assert len(encounter.enemies) == count
    for enemy in encounter.enemies:
        assert not blocked(enemy.x, enemy.y, PLAYER_RADIUS)
        enemy.health = 0
    encounter.enemies[-1].health = 1
    assert encounter.match_result(Player()) is None
    encounter.enemies[-1].health = 0
    assert encounter.match_result(Player()) == 'victory'
    assert encounter.match_result(Player(time_remaining=0)) == 'defeat'
