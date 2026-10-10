"""Mapeamento de controles USB, independente da interface gráfica."""
import re


def same_device(first, second):
    """Compara o dispositivo físico, sem confundir controles do mesmo modelo."""
    if first is None or second is None:
        return first is second
    first_pointer = getattr(first, 'this', None)
    second_pointer = getattr(second, 'this', None)
    if first_pointer is not None and second_pointer is not None:
        return int(first_pointer) == int(second_pointer)
    return first is second

GAMEPAD_ACTIONS = {
    'up': 'Frente', 'down': 'Trás', 'left': 'Esquerda', 'right': 'Direita',
    'jump': 'Salto', 'run': 'Corrida', 'attack': 'Ataque',
    'look_left': 'Virar esq.', 'look_right': 'Virar dir.',
    'menu': 'Menu (Start)', 'confirm': 'Selecionar (B)',
}
DEFAULT_BINDINGS = {
    'up': 'axis:1:+', 'down': 'axis:1:-', 'left': 'axis:0:-', 'right': 'axis:0:+',
    'jump': 'button:0', 'run': 'button:2', 'attack': 'button:1',
    'look_left': 'button:4', 'look_right': 'button:5',
    'menu': 'button:7', 'confirm': 'button:0',
}


def valid_binding(binding):
    return isinstance(binding, str) and re.fullmatch(r'(button:[0-9]+|axis:[0-9]+:[+-])', binding) is not None


def load_bindings(settings):
    saved = settings.get('gamepad_bindings')
    if not isinstance(saved, dict):
        return DEFAULT_BINDINGS.copy()
    saved = {**DEFAULT_BINDINGS, **saved}
    gameplay = [value for action, value in saved.items() if action not in ('menu', 'confirm')]
    if (set(saved) != set(GAMEPAD_ACTIONS) or not all(valid_binding(value) for value in saved.values())
            or len(set(gameplay)) != len(gameplay) or saved['menu'] in gameplay
            or saved['menu'] == saved['confirm']):
        return DEFAULT_BINDINGS.copy()
    return saved.copy()


def binding_label(binding):
    parts = binding.split(':')
    if parts[0] == 'button':
        return f'Botão {int(parts[1]) + 1}'
    return f'Eixo {int(parts[1]) + 1} {parts[2]}'


def replace_binding(bindings, action, binding):
    """Substitui a escolha; troca entradas ocupadas preservando aliases do B."""
    if action not in GAMEPAD_ACTIONS or not valid_binding(binding):
        raise ValueError('Ação ou entrada de controle inválida')
    previous = bindings[action]
    conflict = any(saved == binding and other != action
                   and (action == 'menu' or other == 'menu'
                        or (action != 'confirm' and other != 'confirm'))
                   for other, saved in bindings.items())
    updated = bindings.copy()
    if conflict:
        for other, saved in bindings.items():
            if saved == binding:
                updated[other] = previous
            elif saved == previous:
                updated[other] = binding
    else:
        updated[action] = binding
    return updated


def active_inputs(buttons, axes, dead_zone=0.35):
    active = {f'button:{index}' for index, pressed in enumerate(buttons) if pressed}
    for index, value in enumerate(axes):
        if value > dead_zone:
            active.add(f'axis:{index}:+')
        elif value < -dead_zone:
            active.add(f'axis:{index}:-')
    return active


def mapped_actions(active, bindings):
    return {action: binding in active for action, binding in bindings.items()}


def read_device(device):
    if device is None or not device.connected:
        return set()
    device.poll()
    return active_inputs([button.pressed for button in device.buttons],
                         [axis.value for axis in device.axes])
