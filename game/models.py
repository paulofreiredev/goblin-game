"""Load user geometry into Panda3D without external runtime converters."""
import json
import math
import random
from pathlib import Path
from panda3d.core import (Geom, GeomNode, GeomTriangles, GeomVertexData,
                          GeomVertexFormat, GeomVertexWriter, NodePath, Vec3, PNMImage, Texture)


def mesh_node(name, vertices, triangles, color, textured=False):
    vertex_format = GeomVertexFormat.getV3n3c4t2() if textured else GeomVertexFormat.getV3n3c4()
    data = GeomVertexData(name, vertex_format, Geom.UHStatic)
    vertex_writer = GeomVertexWriter(data, 'vertex')
    normal_writer = GeomVertexWriter(data, 'normal')
    color_writer = GeomVertexWriter(data, 'color')
    uv_writer = GeomVertexWriter(data, 'texcoord') if textured else None
    primitive = GeomTriangles(Geom.UHStatic)
    for triangle in triangles:
        points = [Vec3(*vertices[index]) for index in triangle]
        normal = (points[1] - points[0]).cross(points[2] - points[0])
        if normal.lengthSquared() > 0:
            normal.normalize()
        start = data.getNumRows()
        face_color = color(points) if callable(color) else color
        for point in points:
            vertex_writer.addData3(point)
            normal_writer.addData3(normal)
            color_writer.addData4(*face_color)
            if uv_writer is not None:
                # Project each face onto its dominant plane to avoid stretching.
                axis = max(range(3), key=lambda index: abs(normal[index]))
                uv = (point.y, point.z) if axis == 0 else (point.x, point.z) if axis == 1 else (point.x, point.y)
                uv_writer.addData2(uv[0] * 1.5, uv[1] * 1.5)
        primitive.addVertices(start, start + 1, start + 2)
    geometry = Geom(data)
    geometry.addPrimitive(primitive)
    node = GeomNode(name)
    node.addGeom(geometry)
    result = NodePath(node)
    result.setTwoSided(True)
    return result


def load_tree(path: Path):
    vertices = []
    groups = []
    current = None
    for line in path.read_text().splitlines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] == 'v':
            x, y, z = map(float, parts[1:4])
            vertices.append((x, -z, y - 0.34375))  # OBJ Y-up -> Panda Z-up.
        elif parts[0] == 'o':
            current = (parts[1], [])
            groups.append(current)
        elif parts[0] == 'f' and current is not None:
            indices = [int(part.split('/')[0]) for part in parts[1:]]
            indices = [index - 1 if index > 0 else len(vertices) + index for index in indices]
            for index in range(1, len(indices) - 1):
                current[1].append((indices[0], indices[index], indices[index + 1]))
    root = NodePath('low-obj-trees')
    for name, triangles in groups:
        if name == 'plane':  # Exclude the ground tile packaged with the grove.
            continue
        # Each cylinder group includes both trunk and conical crown.
        if name == 'cylinder':
            color = lambda points: ((0.18, 0.52, 0.10, 1) if sum(point.z for point in points) / 3 > 0.5
                                    else (0.32, 0.19, 0.08, 1))
        else:
            color = (0.44, 0.45, 0.39, 1)
        mesh_node(name, vertices, triangles, color).reparentTo(root)
    return root


def load_enemy(path: Path):
    meshes = [mesh for mesh in json.loads(path.read_text())['meshes'] if mesh['name'] != 'Plane']
    vertices = [vertex for mesh in meshes for vertex in mesh['vertices']]
    lower = [min(vertex[i] for vertex in vertices) for i in range(3)]
    upper = [max(vertex[i] for vertex in vertices) for i in range(3)]
    center_x, center_y = (lower[0] + upper[0]) / 2, (lower[1] + upper[1]) / 2
    scale = 1.45 / max(upper[2] - lower[2], 0.001)
    root = NodePath('stilagmate-enemy')
    root.setTexture(stone_texture())
    for mesh in meshes:
        positions = [((x - center_x) * scale, (y - center_y) * scale, (z - lower[2]) * scale)
                     for x, y, z in mesh['vertices']]
        mesh_node(mesh['name'], positions, mesh['triangles'], (0.9, 0.9, 0.9, 1), textured=True).reparentTo(root)
    return root


def stone_texture():
    """Deterministic, seamless stone pattern built directly as an engine texture."""
    size = 128
    rng = random.Random(73)
    centers = [(rng.uniform(0, size), rng.uniform(0, size)) for _ in range(24)]
    image = PNMImage(size, size, 3)
    for x in range(size):
        for y in range(size):
            distances = []
            for cx, cy in centers:
                dx = min(abs(x - cx), size - abs(x - cx))
                dy = min(abs(y - cy), size - abs(y - cy))
                distances.append(math.hypot(dx, dy))
            distances.sort()
            fissure = min(1.0, (distances[1] - distances[0]) / 1.5)
            mottling = 0.07 * math.sin(x * math.tau / 16) * math.cos(y * math.tau / 32)
            gray = (0.58 + mottling + rng.uniform(-0.055, 0.055)) * (0.56 + 0.44 * fissure)
            image.setXel(x, y, gray, gray * 0.99, gray * 0.95)
    texture = Texture('procedural-stone')
    texture.load(image)
    texture.setWrapU(Texture.WMRepeat)
    texture.setWrapV(Texture.WMRepeat)
    texture.setMinfilter(Texture.FTLinearMipmapLinear)
    texture.setMagfilter(Texture.FTLinear)
    return texture
