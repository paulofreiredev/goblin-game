"""Regras da partida local de captura da bandeira, sem dependência gráfica."""
from dataclasses import dataclass
import math
from game.state import Player

LOCAL_ACTIONS = {'up': 'Frente', 'down': 'Trás', 'left': 'Esquerda',
                 'right': 'Direita', 'jump': 'Salto', 'run': 'Corrida', 'attack': 'Ataque'}
LOCAL_DEFAULTS = [dict(zip(LOCAL_ACTIONS, ['w', 's', 'a', 'd', 'space', 'shift', 'x'])),
                  dict(zip(LOCAL_ACTIONS, ['arrow_up', 'arrow_down', 'arrow_left', 'arrow_right', 'enter', 'control', 'm']))]


def load_local_controls(settings):
    saved = settings.get('local_controls')
    if isinstance(saved, list) and len(saved) == 2:
        if all(isinstance(item, dict) and set(item) == set(LOCAL_ACTIONS) for item in saved):
            keys = [key for item in saved for key in item.values()]
            if all(valid_local_key(key) for key in keys) and len(set(keys)) == len(keys):
                return [item.copy() for item in saved]
    return [item.copy() for item in LOCAL_DEFAULTS]


def valid_local_key(key):
    return isinstance(key, str) and (len(key) == 1 and key.isalnum() and key != 'f'
        or key in ('space', 'shift', 'control', 'enter', 'arrow_up', 'arrow_down', 'arrow_left', 'arrow_right'))


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
    home: tuple[float, float]
    x: float
    y: float
    carrier: int | None = None

    @property
    def at_home(self):
        return self.carrier is None and (self.x, self.y) == self.home

    def reset(self):
        self.x, self.y = self.home
        self.carrier = None


class CaptureMatch:
    def __init__(self):
        self.bases = [(-16.0, -25.0), (16.0, -25.0)]
        self.players = [Player(x=x, y=y) for x, y in self.bases]
        self.flags = [Flag(home, *home) for home in self.bases]
        self.scores = [0, 0]
        self.winner = None

    def update(self):
        if self.winner is not None:
            return
        for team, player in enumerate(self.players):
            own, other = self.flags[team], self.flags[1 - team]
            if own.carrier is None and not own.at_home and math.hypot(player.x - own.x, player.y - own.y) < 2:
                own.reset()
            if other.carrier is None and player.z < 1 and math.hypot(player.x - other.x, player.y - other.y) < 2:
                other.carrier = team
            if other.carrier == team:
                other.x, other.y = player.x, player.y
                if own.at_home and math.hypot(player.x - own.x, player.y - own.y) < 2:
                    self.scores[team] += 1
                    other.reset()
                    if self.scores[team] == 3:
                        self.winner = team

    def attack(self, team):
        player, opponent = self.players[team], self.players[1 - team]
        if self.winner is not None or not player.start_attack():
            return False
        dx, dy = opponent.x - player.x, opponent.y - player.y
        direction = (4 - player.direction) * math.pi / 4
        facing = math.cos(direction), math.sin(direction)
        if math.hypot(dx, dy) > 3.8 or abs(player.z - opponent.z) > 1.5 or dx * facing[0] + dy * facing[1] <= 0:
            return False
        for flag in self.flags:
            if flag.carrier == 1 - team:
                flag.carrier = None
                flag.x, flag.y = opponent.x, opponent.y
        opponent.x, opponent.y = self.bases[1 - team]
        opponent.z = opponent.vertical_speed = 0.0
        opponent.jump_active = False
        return True
