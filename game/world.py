"""World layout, collisions and combat independent of graphics."""
from dataclasses import dataclass
import math
import random
from pathlib import Path
from game.state import CLOCK_BONUS, DIFFICULTIES, FIELD_LIMIT, Player
from game.collisions import tree_obstacles

# Hand-placed clusters keep the spawn clear and make exploration reproducible.
TREE_CLUSTERS = [(-11, 9), (15, 20), (-21, 28), (27, -7), (-30, -15),
                 (40, 35), (-44, 48), (54, -35), (-55, -48), (12, 65)]
PONDS = []  # Piscinas removidas; mantido para compatibilidade.
ENEMY_SPAWNS = [(0, 10), (-6, 18), (20, 9), (-18, 25), (33, -14),
                (-32, -10), (9, 45), (40, 42),
                (60, 10), (-60, 5), (5, -55), (65, 60)]
CLOCK_SPAWNS = [(6, -4), (-18, -20), (38, 12)]
LEVEL_HEIGHT = 0.8
STEP_WIDTH = 4.0
PLAYER_RADIUS = 0.6
PLAYER_BODY_HEIGHT = 1.8
ENEMY_RADIUS = 0.5
TREE_SCALE = 2.4
LOCAL_TREE_OBSTACLES = tree_obstacles(Path(__file__).resolve().parent.parent / "assets/img/low.obj")
TREE_OBSTACLES = []
for index, (cx, cy) in enumerate(TREE_CLUSTERS):
    angle = math.radians(index * 47)
    for x, y, radius in LOCAL_TREE_OBSTACLES:
        TREE_OBSTACLES.append((cx + TREE_SCALE * (x * math.cos(angle) - y * math.sin(angle)),
                               cy + TREE_SCALE * (x * math.sin(angle) + y * math.cos(angle)),
                               radius * TREE_SCALE))
TERRAIN_BLOCKS = [(-40, -6, -10, 16, 2.4), (18, 48, 25, 52, 3.2),
                  (-55, -25, 30, 60, -2.4), (22, 60, -42, -1, -1.6)]


def terrain_surfaces():
    """Faixas largas de acesso em um lado; outros blocos são planos."""
    surfaces = []
    for index, (x0, x1, y0, y1, height) in enumerate(TERRAIN_BLOCKS):
        if index not in (0, 2):
            surfaces.append((x0, x1, y0, y1, height))
            continue
        levels = round(abs(height) / LEVEL_HEIGHT)
        for level in range(levels):
            if index == 0:  # Acesso pelo leste, largura de todo o lado.
                left = x0 if level == levels - 1 else x1 - (level + 1) * STEP_WIDTH
                right = x1 - level * STEP_WIDTH
            else:  # Acesso pelo oeste da depressão.
                left = x0 + level * STEP_WIDTH
                right = x1 if level == levels - 1 else x0 + (level + 1) * STEP_WIDTH
            surfaces.append((left, right, y0, y1, math.copysign((level + 1) * LEVEL_HEIGHT, height)))
    return surfaces


def terrain_base_height(x: float, y: float) -> float:
    for x0, x1, y0, y1, height in terrain_surfaces():
        if x0 <= x < x1 and y0 <= y < y1:
            return height
    return 0.0


def terrain_height(x: float, y: float) -> float:
    """Terreno sólido com elevações e depressões retangulares."""
    return terrain_base_height(x, y)


def in_water(x: float, y: float) -> bool:
    return any(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1
               for cx, cy, rx, ry in PONDS)


def player_ground_height(x: float, y: float) -> float:
    """Highest supporting surface intersecting the circular body footprint."""
    heights = [terrain_height(x, y)]
    for index in range(16):
        angle = index * 2 * math.pi / 16
        heights.append(terrain_height(x + PLAYER_RADIUS * math.cos(angle),
                                      y + PLAYER_RADIUS * math.sin(angle)))
    # Contato exato com cantos, usando as mesmas faixas da malha.
    for x0, x1, y0, y1, height in terrain_surfaces():
        nearest_x = max(x0 + 1e-7, min(x1 - 1e-7, x))
        nearest_y = max(y0 + 1e-7, min(y1 - 1e-7, y))
        if math.hypot(nearest_x - x, nearest_y - y) < PLAYER_RADIUS:
            heights.append(height)
    return max(heights)


def blocked(x: float, y: float, radius: float = 0.0) -> bool:
    return any(math.hypot(x - cx, y - cy) < obstacle_radius + radius
               for cx, cy, obstacle_radius in TREE_OBSTACLES)


def jump_player(player: Player) -> bool:
    if not player.jump():
        return False
    player.fall_start_height = player_ground_height(player.x, player.y)
    return True


def update_player_actions(player: Player, dt: float) -> None:
    if player.update_actions(dt):
        ground = player_ground_height(player.x, player.y)
        if (player.fall_start_height is not None
                and player.fall_start_height - ground >= 2 * LEVEL_HEIGHT - 1e-6):
            player.health = max(0, player.health - 1)
        player.fall_start_height = None


def move_on_terrain(player: Player, old_x: float, old_y: float, enemies=()) -> None:
    """Resolve XY movement while preserving the foot's absolute height over steps."""
    proposed_x, proposed_y = player.x, player.y
    player.x, player.y = old_x, old_y
    for x, y in ((proposed_x, old_y), (None, proposed_y)):
        x = player.x if x is None else x
        x = max(-FIELD_LIMIT + PLAYER_RADIUS, min(FIELD_LIMIT - PLAYER_RADIUS, x))
        y = max(-FIELD_LIMIT + PLAYER_RADIUS, min(FIELD_LIMIT - PLAYER_RADIUS, y))
        if blocked(x, y, PLAYER_RADIUS):
            continue
        old_ground = player_ground_height(player.x, player.y)
        new_ground = player_ground_height(x, y)
        foot_height = old_ground + player.z
        if any(enemy.health > 0 and math.hypot(x - enemy.x, y - enemy.y) < PLAYER_RADIUS + ENEMY_RADIUS
               and foot_height < terrain_height(enemy.x, enemy.y) + 1.45
               and foot_height + PLAYER_BODY_HEIGHT > terrain_height(enemy.x, enemy.y)
               for enemy in enemies):
            continue
        rise = new_ground - old_ground
        if rise > 1e-6:
            if (not player.jump_active or player.climbed_this_jump
                    or rise > LEVEL_HEIGHT + 1e-6 or player.z + 1e-6 < rise):
                continue
            player.climbed_this_jump = True
        if rise < -1e-6 and player.fall_start_height is None:
            player.fall_start_height = old_ground
        player.x, player.y = x, y
        player.z = max(0.0, player.z - rise)


def safe_position(x: float, y: float) -> tuple[float, float]:
    """Move an old save outside newly added groves, choosing a nearby spot."""
    if not blocked(x, y, PLAYER_RADIUS):
        return x, y
    for step in range(1, 25):
        radius = step * 0.5
        for index in range(8):
            angle = index * math.pi / 4
            candidate_x, candidate_y = x + math.cos(angle) * radius, y + math.sin(angle) * radius
            if (abs(candidate_x) <= FIELD_LIMIT and abs(candidate_y) <= FIELD_LIMIT
                    and not blocked(candidate_x, candidate_y, PLAYER_RADIUS)):
                return candidate_x, candidate_y
    return 0.0, 0.0


@dataclass
class Enemy:
    x: float
    y: float
    health: int = 2
    flash: float = 0.0
    coin_collected: bool = False


@dataclass
class HeartPickup:
    x: float
    y: float
    collected: bool = False


@dataclass
class ClockPickup:
    x: float
    y: float
    collected: bool = False


class Encounter:
    def __init__(self, rng=None, difficulty="medium"):
        count = DIFFICULTIES[difficulty][1]
        self.enemies = [Enemy(x, y) for x, y in ENEMY_SPAWNS[:count]]
        self.clocks = [ClockPickup(x, y) for x, y in CLOCK_SPAWNS]
        self.damage_cooldown = 0.0
        self.message_time = 0.0
        self.restart_requested = False
        rng = rng or random.Random()
        self.hearts = []
        while len(self.hearts) < 2:
            x, y = rng.uniform(-70, 70), rng.uniform(-70, 70)
            if (not blocked(x, y, PLAYER_RADIUS) and not in_water(x, y) and math.hypot(x, y) > 3
                    and all(math.hypot(x - heart.x, y - heart.y) > 4 for heart in self.hearts)):
                self.hearts.append(HeartPickup(x, y))

    @property
    def defeated(self):
        return sum(enemy.health == 0 for enemy in self.enemies)

    def match_result(self, player: Player) -> str | None:
        if player.time_remaining <= 0:
            return "defeat"
        if self.enemies and self.defeated == len(self.enemies):
            return "victory"
        return None

    def restore(self, data):
        if not isinstance(data, list) or len(data) != len(self.enemies):
            return
        for enemy, saved in zip(self.enemies, data):
            try:
                x, y, health = float(saved['x']), float(saved['y']), int(saved['health'])
                if (math.isfinite(x) and math.isfinite(y) and abs(x) <= FIELD_LIMIT
                        and abs(y) <= FIELD_LIMIT and health in (0, 1, 2)):
                    enemy.x, enemy.y, enemy.health = x, y, health
                    # Legacy defeated enemies did not leave physical coins.
                    collected = saved.get('coin_collected', health == 0)
                    enemy.coin_collected = collected if type(collected) is bool else health == 0
            except (KeyError, ValueError, TypeError, OverflowError):
                continue

    def snapshot(self):
        return [{'x': enemy.x, 'y': enemy.y, 'health': enemy.health,
                 'coin_collected': enemy.coin_collected} for enemy in self.enemies]

    def clock_snapshot(self):
        return [clock.collected for clock in self.clocks]

    def restore_clocks(self, data):
        if (isinstance(data, list) and len(data) == len(self.clocks)
                and all(type(collected) is bool for collected in data)):
            for clock, collected in zip(self.clocks, data):
                clock.collected = collected

    def heart_snapshot(self):
        return [{'x': heart.x, 'y': heart.y, 'collected': heart.collected} for heart in self.hearts]

    def restore_hearts(self, data):
        if not isinstance(data, list) or len(data) != 2:
            return
        restored = []
        for saved in data:
            try:
                x, y = float(saved['x']), float(saved['y'])
                collected = saved['collected']
                if (not math.isfinite(x) or not math.isfinite(y)
                        or abs(x) > FIELD_LIMIT or abs(y) > FIELD_LIMIT
                        or blocked(x, y, PLAYER_RADIUS) or in_water(x, y) or type(collected) is not bool):
                    return
                restored.append(HeartPickup(x, y, collected))
            except (KeyError, ValueError, TypeError, OverflowError):
                return
        if math.hypot(restored[0].x - restored[1].x, restored[0].y - restored[1].y) > 4:
            self.hearts = restored

    def attack(self, player: Player) -> int:
        angle = player.direction * math.pi / 4
        forward = (-math.cos(angle), math.sin(angle))
        hits = 0
        for enemy in self.enemies:
            dx, dy = enemy.x - player.x, enemy.y - player.y
            distance = math.hypot(dx, dy)
            facing = distance < 0.7 or (dx * forward[0] + dy * forward[1]) / max(distance, 0.001) >= 0.2
            if enemy.health and distance <= 3.8 and facing and player.z <= 1.6:
                enemy.health -= 1
                enemy.flash = 0.22
                hits += 1
        return hits

    def update(self, player: Player, dt: float):
        if self.restart_requested:
            return
        if player.health <= 0:
            self.restart_requested = True
            return
        self.damage_cooldown = max(0, self.damage_cooldown - dt)
        self.message_time = max(0, self.message_time - dt)
        for enemy in self.enemies:
            enemy.flash = max(0, enemy.flash - dt)
            if not enemy.health:
                if (not enemy.coin_collected and player.z < 1.0
                        and math.hypot(player.x - enemy.x, player.y - enemy.y) <= 1.2):
                    player.coins += 1
                    enemy.coin_collected = True
                continue
            dx, dy = player.x - enemy.x, player.y - enemy.y
            distance = math.hypot(dx, dy)
            if distance < 19:
                speed = 2.4
                step = speed * dt
                away_x, away_y = (-dx / distance, -dy / distance) if distance else (1.0, 0.0)
                x = max(-FIELD_LIMIT, min(FIELD_LIMIT, enemy.x + away_x * step))
                y = max(-FIELD_LIMIT, min(FIELD_LIMIT, enemy.y + away_y * step))
                if not blocked(x, enemy.y, ENEMY_RADIUS):
                    enemy.x = x
                if not blocked(enemy.x, y, ENEMY_RADIUS):
                    enemy.y = y
            if distance < 1.6 and player.z < 1.0 and self.damage_cooldown == 0:
                player.health -= 1
                self.damage_cooldown = 1.2
                if player.health <= 0:
                    player.health = 0
                    self.restart_requested = True
                    return
        for heart in self.hearts:
            if (not heart.collected and player.health < 5 and player.z < 1.0
                    and math.hypot(player.x - heart.x, player.y - heart.y) <= 1.2):
                player.health += 1
                heart.collected = True
        if self.match_result(player) is None:
            for clock in self.clocks:
                if (not clock.collected and player.z < 1.0
                        and math.hypot(player.x - clock.x, player.y - clock.y) <= 1.2):
                    player.time_remaining += CLOCK_BONUS
                    clock.collected = True
