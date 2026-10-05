"""Busca local de bandeiras por cor, sem cronômetro ou dependência gráfica."""
from dataclasses import dataclass
import math
import random
from game.state import DIFFICULTIES, Player
from game.world import blocked, player_ground_height, terrain_height

LOCAL_ACTIONS = {'up': 'Frente', 'down': 'Trás', 'left': 'Esquerda',
                 'right': 'Direita', 'jump': 'Salto', 'run': 'Corrida', 'attack': 'Ataque'}
LOCAL_DEFAULTS = [dict(zip(LOCAL_ACTIONS, ['w', 's', 'a', 'd', 'space', 'shift', 'x'])),
                  dict(zip(LOCAL_ACTIONS, ['arrow_up', 'arrow_down', 'arrow_left', 'arrow_right', 'enter', 'control', 'm']))]


def valid_local_key(key):
    return isinstance(key, str) and (len(key) == 1 and key.isalnum() and key != 'f'
        or key in ('space', 'shift', 'control', 'enter', 'arrow_up', 'arrow_down', 'arrow_left', 'arrow_right'))


def load_local_controls(settings):
    saved = settings.get('local_controls')
    if isinstance(saved, list) and len(saved) == 2:
        if all(isinstance(item, dict) and set(item) == set(LOCAL_ACTIONS) for item in saved):
            keys = [key for item in saved for key in item.values()]
            if all(valid_local_key(key) for key in keys) and len(set(keys)) == len(keys):
                return [item.copy() for item in saved]
    return [item.copy() for item in LOCAL_DEFAULTS]


def replace_local_key(controls, team, action, key):
    if not valid_local_key(key):
        raise ValueError('Tecla reservada')
    updated = [item.copy() for item in controls]
    previous = updated[team][action]
    for item in updated:
        for other, saved in item.items():
            if saved == key:
                item[other] = previous
    updated[team][action] = key
    return updated


@dataclass
class Flag:
    team: int
    x: float
    y: float
    captured: bool = False


class CaptureMatch:
    def __init__(self, difficulty='medium', rng=None):
        self.difficulty = difficulty if difficulty in DIFFICULTIES else 'medium'
        self.flag_count = DIFFICULTIES[self.difficulty][1]
        self.bases = [(-16.0, -25.0), (16.0, -25.0)]
        self.players = [Player(x=x, y=y) for x, y in self.bases]
        self.flags = []
        rng = rng or random.Random()
        for team in range(2):
            for _ in range(self.flag_count):
                for attempt in range(10000):
                    x, y = rng.uniform(-75, 75), rng.uniform(-75, 75)
                    if (terrain_height(x, y) == 0 and not blocked(x, y, 1) and
                            all(math.hypot(x - flag.x, y - flag.y) > 4 for flag in self.flags) and
                            all(math.dist((x, y), base) > 6 for base in self.bases) and
                            abs(player_ground_height(x, y) - terrain_height(x, y)) < 0.1):
                        self.flags.append(Flag(team, x, y))
                        break
                else:
                    raise RuntimeError('Não foi possível distribuir as bandeiras')
        self.scores = [0, 0]
        self.winner = None

    def update(self):
        if self.winner is not None:
            return
        for team, player in enumerate(self.players):
            for flag in self.flags:
                if flag.team != team or flag.captured:
                    continue
                vertical = player_ground_height(player.x, player.y) + player.z - terrain_height(flag.x, flag.y)
                if math.hypot(player.x - flag.x, player.y - flag.y) < 1.8 and abs(vertical) < 1:
                    flag.captured = True
                    self.scores[team] += 1
                    if self.scores[team] == self.flag_count:
                        self.winner = team
                        return

    def attack(self, team):
        player, opponent = self.players[team], self.players[1 - team]
        if self.winner is not None or not player.start_attack():
            return False
        dx, dy = opponent.x - player.x, opponent.y - player.y
        angle = (4 - player.direction) * math.pi / 4
        if math.hypot(dx, dy) > 3.8 or abs(player.z - opponent.z) > 1.5 or dx * math.cos(angle) + dy * math.sin(angle) <= 0:
            return False
        opponent.x, opponent.y = self.bases[1 - team]
        opponent.z = opponent.vertical_speed = 0.0
        opponent.jump_active = False
        return True
