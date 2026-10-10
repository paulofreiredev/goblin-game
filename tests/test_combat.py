import pytest
from game.state import Player, Storage
from game.world import Encounter, Enemy, blocked, in_water, safe_position


def test_jump_lands_and_cannot_double_jump():
    player = Player()
    assert player.jump()
    assert not player.jump()
    heights = []
    for _ in range(120):
        player.update_actions(1 / 120)
        heights.append(player.z)
    assert max(heights) == pytest.approx(1.6, abs=0.02)
    assert player.z == 0 and player.vertical_speed == 0
    assert player.jump()


def test_attack_direction_range_cooldown_and_defeat():
    player = Player(direction=2)
    encounter = Encounter()
    encounter.enemies = [Enemy(0, 2), Enemy(0, -2), Enemy(0, 5)]
    assert player.start_attack()
    assert encounter.attack(player) == 1
    assert [enemy.health for enemy in encounter.enemies] == [1, 2, 2]
    assert not player.start_attack()
    assert 12 <= player.frame <= 17
    player.update_actions(0.61)
    assert player.start_attack()
    encounter.attack(player)
    assert encounter.defeated == 1
    assert encounter.enemies[1].health == 2


def test_jump_avoids_contact_and_contact_has_cooldown():
    player = Player(z=1.2)
    encounter = Encounter()
    encounter.enemies = [Enemy(0, 1)]
    encounter.update(player, 0.1)
    assert player.health == 5
    player.z = 0
    encounter.update(player, 0.1)
    assert player.health == 4
    encounter.update(player, 0.1)
    assert player.health == 4
    encounter.enemies[0].y = 1
    encounter.update(player, 1.3)
    assert player.health == 3


def test_defeat_requests_restart_without_negative_health():
    player = Player(x=20, y=20, health=1)
    encounter = Encounter()
    encounter.enemies = [Enemy(20, 20)]
    encounter.update(player, 0.01)
    assert player.health == 0
    assert encounter.restart_requested
    encounter.update(player, 10)
    assert player.health == 0


def test_fleeing_and_environment():
    encounter = Encounter()
    encounter.enemies = [Enemy(0, 10), Enemy(70, 70)]
    encounter.update(Player(), 0.5)
    assert encounter.enemies[0].y > 10
    assert encounter.enemies[1].x == 70
    assert not in_water(9, 7)
    assert not in_water(0, 0)
    from game.world import TREE_OBSTACLES
    assert blocked(*TREE_OBSTACLES[0][:2])
    assert not blocked(-11, 9)
    assert not blocked(0, 0)


def test_save_keeps_health_and_enemy_defeats(tmp_path):
    storage = Storage(tmp_path)
    player = Player(health=3)
    encounter = Encounter()
    encounter.enemies[0].health = 0
    assert storage.save_player(player, encounter.snapshot())
    restored = Encounter()
    restored.restore(storage.read('save.json')['enemies'])
    assert restored.defeated == 1
    assert storage.load_player().health == 3


def test_legacy_save_defaults_and_invalid_enemies(tmp_path):
    storage = Storage(tmp_path)
    storage.write('save.json', {'x': 0, 'y': 0, 'direction': 2})
    assert storage.load_player().health == 5
    encounter = Encounter()
    encounter.restore([None] * 8)
    assert encounter.defeated == 0
    encounter.restore([{'x': float('nan'), 'y': 0, 'health': 0}] * 8)
    assert encounter.defeated == 0


def test_save_inside_new_grove_is_relocated_nearby():
    x, y = safe_position(-11, 9)
    assert not blocked(x, y)
    assert abs(x + 11) + abs(y - 9) < 10
    assert safe_position(0, 0) == (0, 0)


def test_coins_drop_on_defeat_and_are_collected_once():
    player = Player(direction=2)
    encounter = Encounter()
    encounter.enemies = [Enemy(0, 2), Enemy(1, 2), Enemy(0, -2)]
    encounter.attack(player)
    assert player.coins == 0
    encounter.attack(player)
    assert player.coins == 0
    encounter.attack(player)
    assert player.coins == 0
    player.y = 2
    encounter.update(player, 0.01)
    assert player.coins == 2
    encounter.update(player, 0.01)
    assert player.coins == 2
    player.health = 1
    encounter.enemies = [Enemy(player.x, player.y)]
    encounter.update(player, 0.01)
    assert player.health == 0 and encounter.restart_requested


def test_match_requires_all_monsters_before_timeout():
    player = Player()
    encounter = Encounter()
    assert player.time_remaining == 120
    encounter.enemies[0].health = 0
    assert encounter.match_result(player) is None
    player.advance_match_time(119.5)
    assert player.time_remaining == 0.5
    for enemy in encounter.enemies:
        enemy.health = 0
    assert encounter.match_result(player) == 'victory'
    player.advance_match_time(0.5)
    assert encounter.match_result(player) == 'defeat'
    player.advance_match_time(10)
    assert player.time_remaining == 0


def test_timeout_with_alive_monster_is_defeat():
    player = Player(time_remaining=0.1)
    encounter = Encounter()
    player.advance_match_time(0.1)
    assert encounter.match_result(player) == 'defeat'


def test_uncollected_coin_persistence_and_legacy(tmp_path):
    encounter = Encounter()
    encounter.enemies[0].health = 0
    player = Player()
    storage = Storage(tmp_path)
    storage.save_player(player, encounter.snapshot())
    restored = Encounter()
    restored.restore(storage.read('save.json')['enemies'])
    assert not restored.enemies[0].coin_collected
    player.x, player.y = restored.enemies[0].x, restored.enemies[0].y
    restored.update(player, 0)
    assert player.coins == 1
    storage.save_player(player, restored.snapshot())
    restored.restore(storage.read('save.json')['enemies'])
    restored.update(player, 0)
    assert player.coins == 1
    legacy = [{'x': e.x, 'y': e.y, 'health': e.health} for e in restored.enemies]
    restored.restore(legacy)
    assert restored.enemies[0].coin_collected
    assert not restored.enemies[1].coin_collected


def test_coin_requires_proximity_and_ground_height():
    encounter = Encounter()
    encounter.enemies = [Enemy(0, 2, health=0)]
    player = Player()
    encounter.update(player, 0)
    assert player.coins == 0
    player.y, player.z = 2, 1.5
    encounter.update(player, 0)
    assert player.coins == 0
    player.z = 0
    encounter.update(player, 0)
    assert player.coins == 1


def test_two_random_hearts_spawn_in_accessible_distinct_places():
    import math
    import random
    first = Encounter(random.Random(1))
    second = Encounter(random.Random(2))
    assert len(first.hearts) == len(second.hearts) == 2
    assert first.heart_snapshot() != second.heart_snapshot()
    for heart in first.hearts + second.hearts:
        assert not blocked(heart.x, heart.y)
        assert not in_water(heart.x, heart.y)
        assert math.hypot(heart.x, heart.y) > 3
    assert math.hypot(first.hearts[0].x - first.hearts[1].x,
                      first.hearts[0].y - first.hearts[1].y) > 4


def test_heart_restores_one_life_once_and_stays_when_full():
    from game.world import HeartPickup
    encounter = Encounter()
    encounter.enemies = []
    encounter.hearts = [HeartPickup(0, 0), HeartPickup(10, 0)]
    player = Player()
    encounter.update(player, 0)
    assert player.health == 5 and not encounter.hearts[0].collected
    player.health, player.z = 3, 2
    encounter.update(player, 0)
    assert player.health == 3
    player.z = 0
    encounter.update(player, 0)
    assert player.health == 4 and encounter.hearts[0].collected
    encounter.update(player, 0)
    assert player.health == 4
    player.x = 10
    encounter.update(player, 0)
    assert player.health == 5 and encounter.hearts[1].collected


def test_heart_locations_and_collection_persist(tmp_path):
    import random
    encounter = Encounter(random.Random(1))
    encounter.hearts[0].collected = True
    storage = Storage(tmp_path)
    storage.save_player(Player(), encounter.snapshot(), encounter.heart_snapshot())
    restored = Encounter(random.Random(2))
    restored.restore_hearts(storage.read('save.json')['hearts'])
    assert restored.heart_snapshot() == encounter.heart_snapshot()
    original = restored.heart_snapshot()
    restored.restore_hearts([None, None])
    assert restored.heart_snapshot() == original
    restored.restore_hearts([{'x': float('nan'), 'y': 0, 'collected': False}] * 2)
    assert restored.heart_snapshot() == original


def test_fleeing_respects_bounds_obstacles_and_frame_time():
    from game.state import FIELD_LIMIT
    player = Player(x=85)
    encounter = Encounter()
    encounter.enemies = [Enemy(FIELD_LIMIT - 0.01, 0), Enemy(85, 0)]
    encounter.update(player, 0.1)
    assert encounter.enemies[0].x == FIELD_LIMIT
    assert encounter.enemies[1].x > 85  # Coincident positions have a defined escape direction.
    encounter.enemies = [Enemy(-15, 9)]
    encounter.update(Player(x=-17, y=9), 0.5)
    assert not blocked(encounter.enemies[0].x, encounter.enemies[0].y)
    whole, split = Encounter(), Encounter()
    whole.enemies, split.enemies = [Enemy(0, 5)], [Enemy(0, 5)]
    whole.update(Player(), 0.5)
    for _ in range(5):
        split.update(Player(), 0.1)
    assert whole.enemies[0].y == pytest.approx(split.enemies[0].y)


def test_terrain_preserves_blocks_and_restores_former_pool_ground():
    import math
    from game.world import PONDS, terrain_height, terrain_base_height
    heights = [terrain_height(x, y) for x in range(-80, 81, 10) for y in range(-80, 81, 10)]
    assert min(heights) < -2 and max(heights) > 2
    assert terrain_height(0, 0) == 0
    assert all(math.isfinite(height) for height in heights)
    assert PONDS == []
    for cx, cy in [(9, 7), (-12, 35), (34, 20), (-38, -28)]:
        assert not in_water(cx, cy)
        assert terrain_height(cx, cy) == terrain_base_height(cx, cy)


def test_rectangular_terrain_has_flat_tops_and_vertical_transitions():
    from game.world import terrain_height
    assert terrain_height(-20, 0) == pytest.approx(2.4)
    assert terrain_height(-30, 5) == pytest.approx(2.4)
    assert terrain_height(-6.01, 0) == pytest.approx(0.8)
    assert terrain_height(-6, 0) == 0
    assert terrain_height(-40, 45) == pytest.approx(-2.4)
    assert terrain_height(-25, 45) == 0
    assert terrain_height(0, -20) == terrain_height(0, -30) == 0


def test_climbing_requires_jump_and_only_one_level_per_jump():
    from game.world import jump_player, move_on_terrain, update_player_actions
    player = Player(x=-5.3)
    player.x = -6.1
    move_on_terrain(player, -5.3, 0)
    assert player.x == -5.3
    assert jump_player(player)
    update_player_actions(player, 0.15)
    absolute_height = player.z
    player.x = -6.1
    move_on_terrain(player, -5.3, 0)
    assert player.x == -6.1
    assert player.z + 0.8 == pytest.approx(absolute_height)
    player.x = -10.1
    move_on_terrain(player, -6.1, 0)
    assert player.x == -6.1
    for _ in range(20):
        update_player_actions(player, 0.05)
    assert player.z == 0 and not player.climbed_this_jump
    assert jump_player(player)
    update_player_actions(player, 0.15)
    player.x = -10.1
    move_on_terrain(player, -6.1, 0)
    assert player.x == -10.1
    assert player.health == 5


def test_cannot_skip_two_levels_even_when_jump_is_high_enough():
    from game.world import jump_player, move_on_terrain, update_player_actions
    player = Player(x=-5.3)
    jump_player(player)
    update_player_actions(player, 0.4)
    assert player.z == pytest.approx(1.6)
    player.x = -10.1
    move_on_terrain(player, -5.3, 0)
    assert player.x == -5.3


@pytest.mark.parametrize('start_x,end_x,drop,damage', [(-20, 0, 2.4, 1), (-11, -7, 0.8, 0)])
def test_fall_is_continuous_and_damage_only_on_landing(start_x, end_x, drop, damage):
    from game.world import move_on_terrain, terrain_height, update_player_actions
    player = Player(x=start_x)
    original_height = terrain_height(start_x, 0)
    player.x = end_x
    move_on_terrain(player, start_x, 0)
    assert player.z == pytest.approx(drop)
    assert terrain_height(player.x, player.y) + player.z == pytest.approx(original_height)
    assert player.health == 5
    update_player_actions(player, 0.05)
    assert 0 < player.z < drop
    assert player.health == 5
    for _ in range(20):
        update_player_actions(player, 0.05)
    assert player.z == 0
    assert player.health == 5 - damage
    update_player_actions(player, 1)
    assert player.health == 5 - damage


def test_jumping_and_landing_on_same_level_does_not_hurt():
    from game.world import jump_player, update_player_actions
    player = Player()
    jump_player(player)
    for _ in range(25):
        update_player_actions(player, 0.05)
    assert player.z == 0 and player.health == 5


def test_body_stops_before_step_face_and_at_rectangular_corner():
    from game.world import move_on_terrain, player_ground_height
    player = Player(x=-5.2)
    player.x = -5.5
    move_on_terrain(player, -5.2, 0)
    assert player.x == -5.2  # Center remains outside; the body's radius meets the wall.
    assert player_ground_height(-5.6, 16.4) == pytest.approx(0.8)
    player = Player(x=-5.2, y=16.8)
    player.x, player.y = -5.6, 16.4
    move_on_terrain(player, -5.2, 16.8)
    assert player.y == 16.8
    assert player_ground_height(player.x, player.y) == 0


def test_body_cannot_enter_trees_or_live_monsters():
    from game.world import move_on_terrain, TREE_OBSTACLES
    trunk_x, trunk_y, _ = TREE_OBSTACLES[0]
    player = Player(x=trunk_x - 1, y=trunk_y)
    player.x = trunk_x - 0.2
    move_on_terrain(player, trunk_x - 1, trunk_y)
    assert player.x == trunk_x - 1
    enemy = Enemy(0, 2)
    player = Player(y=1.2)
    move_on_terrain(player, 0, 0, [enemy])
    assert player.y == 0
    player.z, player.y = 1.5, 1.2
    move_on_terrain(player, 0, 0, [enemy])
    assert player.y == 1.2  # A jump clearing the enemy's height can pass above it.


def test_can_collect_coin_in_open_space_between_tree_trunks():
    from game.world import move_on_terrain
    encounter = Encounter()
    encounter.enemies = [Enemy(-11, 9, health=0)]
    encounter.hearts = []
    player = Player(x=-12.2, y=9)
    player.x = -11.9
    move_on_terrain(player, -12.2, 9, encounter.enemies)
    assert player.x == -11.9
    encounter.update(player, 0)
    assert player.coins == 1 and encounter.enemies[0].coin_collected


def test_trunk_colliders_follow_asset_scale_and_rotation():
    import math
    from game.world import LOCAL_TREE_OBSTACLES, TREE_OBSTACLES, TREE_SCALE, TREE_CLUSTERS
    assert len(LOCAL_TREE_OBSTACLES) == 16
    assert all(radius < 0.05 for _, _, radius in LOCAL_TREE_OBSTACLES[:6])
    x, y, radius = LOCAL_TREE_OBSTACLES[0]
    cx, cy = TREE_CLUSTERS[1]
    angle = math.radians(47)
    ox, oy, transformed_radius = TREE_OBSTACLES[16]
    assert ox == pytest.approx(cx + TREE_SCALE * (x * math.cos(angle) - y * math.sin(angle)))
    assert oy == pytest.approx(cy + TREE_SCALE * (x * math.sin(angle) + y * math.cos(angle)))
    assert transformed_radius == pytest.approx(radius * TREE_SCALE)


def test_few_terrain_blocks_have_wide_stairs_on_only_one_side():
    from game.world import terrain_surfaces, terrain_height, TERRAIN_BLOCKS, STEP_WIDTH
    assert len(TERRAIN_BLOCKS) == 4 and STEP_WIDTH == 4
    assert len(terrain_surfaces()) == 8
    for y in (-9, 0, 15):
        assert terrain_height(-7, y) == pytest.approx(0.8)
        assert terrain_height(-11, y) == pytest.approx(1.6)
        assert terrain_height(-15, y) == pytest.approx(2.4)
    assert terrain_height(-39.9, 0) == pytest.approx(2.4)
    assert terrain_height(-20, -9.9) == pytest.approx(2.4)
    assert terrain_height(18.1, 25.1) == pytest.approx(3.2)
    assert terrain_height(59.9, -41.9) == pytest.approx(-1.6)


@pytest.mark.parametrize('start,end', [
    ((-26, 45), (-24, 45)), ((-40, 31), (-40, 29)),
    ((-40, 59), (-40, 61)), ((-54, 45), (-56, 45)),
    ((23, -20), (21, -20)), ((59, -20), (61, -20)),
    ((40, -41), (40, -43)), ((40, -2), (40, 0)),
])
def test_player_can_jump_out_of_every_pit_side(start, end):
    from game.world import jump_player, move_on_terrain, update_player_actions
    player = Player(x=start[0], y=start[1])
    player.x, player.y = end
    move_on_terrain(player, *start)
    assert (player.x, player.y) == start  # Caminhar não atravessa a parede.
    assert jump_player(player)
    assert not jump_player(player)
    update_player_actions(player, 0.5)
    player.x, player.y = end
    move_on_terrain(player, *start)
    assert (player.x, player.y) == end
    for _ in range(30):
        update_player_actions(player, 0.05)
    assert player.z == 0
    assert player.health == 5
