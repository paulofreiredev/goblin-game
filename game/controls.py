"""Configuração validada das teclas de ação."""
import string

ACTION_KEYS = frozenset(string.ascii_lowercase + string.digits) | {
    "space", "enter", "tab", "control", "alt", *[f"f{index}" for index in range(1, 13)],
}
MOVEMENT_KEYS = frozenset({"w", "a", "s", "d"})


def valid_action_key(key) -> bool:
    return isinstance(key, str) and key in ACTION_KEYS and key not in MOVEMENT_KEYS and key != "f"


def load_controls(settings: dict) -> tuple[str, str]:
    jump = settings.get("jump_key", "space")
    attack = settings.get("attack_key", "x")
    if not valid_action_key(jump):
        jump = "space"
    if not valid_action_key(attack) or attack == jump:
        attack = "x" if jump != "x" else "space"
    return jump, attack


def key_label(key: str) -> str:
    return {"space": "ESPAÇO", "enter": "ENTER", "control": "CTRL"}.get(key, key.upper())
