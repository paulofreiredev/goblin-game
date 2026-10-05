"""Run with Blender: blender -b --python tools/export_enemy.py.

Writes triangulated, transformed mesh data. Never overwrites the source .blend.
"""
import json
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'assets/img/stilagmate.blend'), use_scripts=False)
meshes = []
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    mesh.calc_loop_triangles()
    matrix = obj.matrix_world
    vertices = [list(matrix @ vertex.co) for vertex in mesh.vertices]
    triangles = [list(triangle.vertices) for triangle in mesh.loop_triangles]
    meshes.append({'name': obj.name, 'vertices': vertices, 'triangles': triangles})
    evaluated.to_mesh_clear()
if not meshes:
    raise RuntimeError('Nenhuma malha encontrada no stilagmate.blend')
output = ROOT / 'assets/models/stilagmate.json'
output.write_text(json.dumps({'source': 'assets/img/stilagmate.blend', 'meshes': meshes}, separators=(',', ':')))
print('EXPORTED', output, [(m['name'], len(m['vertices']), len(m['triangles'])) for m in meshes])
