"""Volumes sólidos extraídos do asset OBJ, sem depender da engine gráfica."""
import math
from pathlib import Path


def tree_obstacles(path: Path) -> list[tuple[float, float, float]]:
    vertices = []
    groups = []
    current = None
    for line in path.read_text().splitlines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "v":
            x, y, z = map(float, parts[1:4])
            vertices.append((x, -z, y - 0.34375))
        elif parts[0] == "o":
            current = (parts[1], set())
            groups.append(current)
        elif parts[0] == "f" and current is not None:
            indices = [int(part.split("/")[0]) for part in parts[1:]]
            current[1].update(index - 1 if index > 0 else len(vertices) + index for index in indices)
    obstacles = []
    for name, indices in groups:
        if name not in ("cylinder", "cuboid") or not indices:
            continue
        points = [vertices[index] for index in indices]
        if name == "cylinder":
            # Only the trunk base is solid; the wide crown is above the player.
            bottom = min(point[2] for point in points)
            points = [point for point in points if point[2] <= bottom + 1e-6]
        x0, x1 = min(p[0] for p in points), max(p[0] for p in points)
        y0, y1 = min(p[1] for p in points), max(p[1] for p in points)
        obstacles.append(((x0 + x1) / 2, (y0 + y1) / 2,
                          math.hypot(x1 - x0, y1 - y0) / 2))
    return obstacles
