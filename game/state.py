"""Movimento e persistência independentes da engine gráfica."""
from dataclasses import dataclass
import json
import math
from pathlib import Path

FIELD_LIMIT = 90.0
MATCH_DURATION = 120.0
CLOCK_BONUS = 30.0
CLOCK_COUNT = 3
MAX_MATCH_TIME = MATCH_DURATION + CLOCK_COUNT * CLOCK_BONUS


@dataclass
class Player:
    x: float = 0.0
    y: float = 0.0
    direction: int = 6
    animation: str = "idle"
    animation_time: float = 0.0
    z: float = 0.0
    vertical_speed: float = 0.0
    attack_time: float = 0.0
    health: int = 5
    coins: int = 0
    time_remaining: float = MATCH_DURATION
    jump_active: bool = False
    climbed_this_jump: bool = False
    fall_start_height: float | None = None

    def advance_match_time(self, dt: float) -> None:
        self.time_remaining = max(0.0, self.time_remaining - max(0.0, dt))

    def move(self, dx: float, dy: float, running: bool, dt: float) -> None:
        magnitude = math.hypot(dx, dy)
        old_animation = self.animation
        if magnitude:
            speed = 12.0 if running else 6.0
            self.x = max(-FIELD_LIMIT, min(FIELD_LIMIT, self.x + dx / magnitude * speed * dt))
            self.y = max(-FIELD_LIMIT, min(FIELD_LIMIT, self.y + dy / magnitude * speed * dt))
            # Rows: W, NW, N, NE, E, SE, S, SW. Camera stays south.
            self.direction = round(math.atan2(dy, -dx) / (math.pi / 4)) % 8
            self.animation = "run" if running else "walk"
        else:
            self.animation = "idle"
        self.animation_time = (self.animation_time + dt) if self.animation == old_animation else 0.0

    def jump(self) -> bool:
        if self.z > 0 or self.vertical_speed > 0:
            return False
        self.vertical_speed = 8.0
        self.jump_active = True
        self.climbed_this_jump = False
        return True

    def start_attack(self) -> bool:
        if self.attack_time > 0:
            return False
        self.attack_time = 0.6
        return True

    def update_actions(self, dt: float) -> bool:
        self.attack_time = max(0, self.attack_time - dt)
        if self.z > 0 or self.vertical_speed > 0:
            self.z += self.vertical_speed * dt - 10 * dt * dt
            self.vertical_speed -= 20 * dt
            if self.z <= 0:
                self.z = self.vertical_speed = 0.0
                self.jump_active = False
                self.climbed_this_jump = False
                return True
        return False

    @property
    def frame(self) -> int:
        # Asset: 42 columns × 8 rows, 128 px. Movement is columns 4–11.
        if self.attack_time > 0:
            return 12 + min(5, int((0.6 - self.attack_time) * 10))
        if self.animation == "idle":
            return 0
        fps = 14 if self.animation == "run" else 8
        return 4 + int(self.animation_time * fps) % 8


class Storage:
    def __init__(self, directory: Path):
        self.directory = directory
        self.last_error = ""

    def read(self, name: str) -> dict:
        try:
            data = json.loads((self.directory / name).read_text())
            return data if isinstance(data, dict) else {}
        except (OSError, ValueError):
            return {}

    def write(self, name: str, data: dict) -> bool:
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            destination = self.directory / name
            temporary = destination.with_suffix(".tmp")
            temporary.write_text(json.dumps(data, indent=2))
            temporary.replace(destination)
            self.last_error = ""
            return True
        except OSError as error:
            self.last_error = f"Não foi possível salvar: {error}"
            return False

    def load_player(self) -> Player | None:
        data = self.read("save.json")
        try:
            x, y = float(data["x"]), float(data["y"])
            direction = int(data["direction"])
            if not all(math.isfinite(v) and abs(v) <= FIELD_LIMIT for v in (x, y)):
                return None
            if not 0 <= direction < 8:
                return None
            health = data.get("health", 5)
            if type(health) is not int or not 1 <= health <= 5:
                health = 5
            coins = data.get("coins", 0)
            if type(coins) is not int or coins < 0:
                coins = 0
            time_remaining = data.get("time_remaining", MATCH_DURATION)
            if (type(time_remaining) not in (int, float) or not math.isfinite(time_remaining)
                    or not 0 <= time_remaining <= MAX_MATCH_TIME):
                time_remaining = MATCH_DURATION
            return Player(x=x, y=y, direction=direction, health=health, coins=coins,
                          time_remaining=float(time_remaining))
        except (KeyError, TypeError, ValueError, OverflowError):
            return None

    def save_player(self, player: Player, enemies=None, hearts=None, clocks=None) -> bool:
        data = {"x": player.x, "y": player.y, "direction": player.direction,
                "health": player.health, "coins": player.coins,
                "time_remaining": player.time_remaining}
        if enemies is not None:
            data["enemies"] = enemies
        if hearts is not None:
            data["hearts"] = hearts
        if clocks is not None:
            data["clocks"] = clocks
        return self.write("save.json", data)
