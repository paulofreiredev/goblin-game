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


def clear_view(target, position, obstacles, ground_height):
    for bounds in obstacles:
        if segment_box_hit(target, position, bounds) is not None:
            return False
    distance = math.dist(target, position)
    steps = max(1, math.ceil(distance / 0.25))
    for step in range(1, steps + 1):
        t = step / steps
        point = tuple(target[axis] + (position[axis] - target[axis]) * t for axis in range(3))
        if point[2] < ground_height(point[0], point[1]) + 0.5:
            return False
    return True


def third_person_position(foot, desired, obstacles, ground_height):
    """Procura visão livre atrás/lateralmente, sem câmera sobre o personagem."""
    x, y, z = foot
    target = (x, y, z + 1.5)
    heading = math.atan2(desired[0] - x, desired[1] - y)
    # Primeiro preservar distância e altura; contornar por trás e pelos lados.
    offsets = (0, 15, -15, 30, -30, 45, -45, 60, -60, 90, -90, 120, -120, 150, -150, 180)
    for distance in (20, 14, 10, 8):
        for offset in offsets:
            angle = heading + math.radians(offset)
            position = (x + distance * math.sin(angle), y + distance * math.cos(angle),
                        z + 7 * distance / 20)
            if clear_view(target, position, obstacles, ground_height):
                return position
    # Acompanha por trás mesmo em espaço fechado; obstruções visuais são atenuadas.
    return (desired[0], desired[1], max(desired[2], ground_height(*desired[:2]) + 0.5))


def follow_heading(current, target, dt):
    difference = (target - current + 180) % 360 - 180
    return current + difference * (1 - math.exp(-5 * max(0.0, dt)))


def relative_movement(right, forward, heading):
    angle = math.radians(heading)
    return (right * math.cos(angle) + forward * math.sin(angle),
            forward * math.cos(angle) - right * math.sin(angle))


def view_direction(heading, pitch):
    yaw, tilt = math.radians(heading), math.radians(pitch)
    return (math.sin(yaw) * math.cos(tilt), math.cos(yaw) * math.cos(tilt), math.sin(tilt))


def facing_direction(heading):
    return round(2 + heading / 45) % 8
