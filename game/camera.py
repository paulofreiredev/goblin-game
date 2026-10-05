"""Cálculos de câmera e direção independentes de janela e renderização."""
import math


def segment_box_hit(start, end, bounds, margin=0.3):
    """Primeira fração de contato entre um segmento e uma caixa expandida."""
    lower, upper = bounds
    first, last = 0.0, 1.0
    for axis in range(3):
        delta = end[axis] - start[axis]
        minimum, maximum = lower[axis] - margin, upper[axis] + margin
        if abs(delta) < 1e-9:
            if not minimum <= start[axis] <= maximum:
                return None
            continue
        near, far = sorted(((minimum - start[axis]) / delta,
                            (maximum - start[axis]) / delta))
        first, last = max(first, near), min(last, far)
        if first > last:
            return None
    return first


def third_person_position(foot, desired, obstacles, ground_height):
    """Encurta a linha de visão antes de árvores ou terreno, com margem."""
    x, y, z = foot
    target = (x, y, z + 1.5)
    delta = tuple(desired[axis] - target[axis] for axis in range(3))
    distance = math.sqrt(sum(value * value for value in delta))
    fraction = 1.0
    for bounds in obstacles:
        hit = segment_box_hit(target, desired, bounds)
        if hit is not None:
            fraction = min(fraction, max(0.0, hit - 0.4 / max(distance, 0.001)))
    steps = max(1, math.ceil(distance / 0.25))
    for step in range(1, steps + 1):
        t = step / steps
        if t > fraction:
            break
        point = tuple(target[axis] + delta[axis] * t for axis in range(3))
        if point[2] < ground_height(point[0], point[1]) + 0.5:
            fraction = max(0.0, (step - 1) / steps)
            break
    if distance * fraction < 4.5:
        # Espaço curto/volume de copa: manter distância para enquadrar o sprite.
        position = (x, y - 4, z + 7)
    else:
        position = tuple(target[axis] + delta[axis] * fraction for axis in range(3))
    return (position[0], position[1],
            max(position[2], ground_height(position[0], position[1]) + 0.5))
