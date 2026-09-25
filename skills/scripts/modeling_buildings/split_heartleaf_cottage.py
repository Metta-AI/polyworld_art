"""Extract the cottage yard as editable, independently placeable CC0 parts."""
import bpy
import json
import runpy
from collections import defaultdict
from pathlib import Path
from mathutils import Vector

Art = Path(__file__).resolve().parents[3]
Work = Art / 'tmp/heartleaf-layers'
Work.mkdir(parents=True, exist_ok=True)
runpy.run_path(str(Path(__file__).with_name('refine_heartleaf_cottage.py')))
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(Art / 'tmp/heartleaf-refine/cottage.glb'))
source = next(obj for obj in bpy.context.scene.objects if obj.type == 'MESH')
mesh = source.data
parents = list(range(len(mesh.vertices)))
def root(index):
    """Resolve one welded position's component."""
    while parents[index] != index:
        parents[index] = parents[parents[index]]
        index = parents[index]
    return index
def join(a, b):
    """Join positions without changing the source UV seams."""
    parents[root(a)] = root(b)
positions = {}
for vertex in mesh.vertices:
    key = tuple(round(value, 5) for value in vertex.co)
    if key in positions:
        join(vertex.index, positions[key])
    else:
        positions[key] = vertex.index
for face in mesh.polygons:
    for index in face.vertices:
        join(face.vertices[0], index)
groups = defaultdict(list)
for face in mesh.polygons:
    groups[root(face.vertices[0])].append(face)

def make_part(name, faces, pivot):
    """Preserve topology, materials and per-corner UVs around a ground pivot."""
    indices = sorted({index for face in faces for index in face.vertices})
    remap = {index: i for i, index in enumerate(indices)}
    data = bpy.data.meshes.new(name)
    data.from_pydata([mesh.vertices[i].co - pivot for i in indices], [],
                    [[remap[i] for i in face.vertices] for face in faces])
    for material in mesh.materials:
        data.materials.append(material)
    uv = data.uv_layers.new(name='UVMap')
    for old, new in zip(faces, data.polygons):
        new.material_index = old.material_index
        new.use_smooth = old.use_smooth
        for a, b in zip(old.loop_indices, new.loop_indices):
            uv.data[b].uv = mesh.uv_layers.active.data[a].uv
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = pivot
    return obj

shell = []
records = []
parts = []
for faces in groups.values():
    points = [mesh.vertices[i].co for face in faces for i in face.vertices]
    low = Vector([min(p[i] for p in points) for i in range(3)])
    high = Vector([max(p[i] for p in points) for i in range(3)])
    if low.y >= -0.35 or high.z > 1:
        shell.extend(faces)
        continue
    if all(face.material_index == 2 for face in faces):
        continue  # The terrain owns yard grass; discard its duplicate disk.
    kind = 'fence' if high.z > 0.3 else 'stone'
    name = f'{kind}_{len(records):02d}'
    pivot = Vector(((low.x + high.x) / 2, (low.y + high.y) / 2, low.z))
    obj = make_part(name, faces, pivot)
    if kind == 'fence':
        # Thicken the posts independently, without enlarging the yard layout.
        for vertex in obj.data.vertices:
            if len(faces) < 30:
                vertex.co.x *= 1.65
                vertex.co.y *= 1.65
                vertex.co.z *= 1.3
            else:
                vertex.co.z *= 1.6
    obj['role'] = kind
    obj['source'] = 'Project-generated CC0 hobbit_house.glb, preserved UVs.'
    parts.append(obj)
    records.append({'name': name, 'kind': kind,
                    'position': [round(pivot.x, 6), round(pivot.z, 6), round(-pivot.y, 6)]})
cottage = make_part('cottage', shell, Vector((0, 0, 0)))
# Bring the rear bank forward and lower its crown while preserving the
# original facade join. This edits the mound, never the door or whole house.
for vertex in cottage.data.vertices:
    x, y, z = vertex.co
    if y <= .34:
        continue
    fade = min(1, (y - .34) / .8)
    fade = fade * fade * (3 - 2 * fade)
    vertex.co.x *= 1 - .12 * fade
    vertex.co.y -= (.8 + .12 * (y - 2.15)) * fade
    vertex.co.z *= 1 - .12 * fade
mirror = cottage.modifiers.new('Editable bilateral cottage', 'MIRROR')
mirror.use_bisect_axis[0] = True
mirror.use_clip = True
bpy.data.objects.remove(source, do_unlink=True)
for material in cottage.data.materials:
    if material.name.startswith('Grass |'):
        for node in material.node_tree.nodes:
            if node.type == 'TEX_IMAGE':
                node.image = bpy.data.images.load(str(Art / 'terrain/tiles/heartleaf-layer-grass-1.rgb.png'))
                node.image.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(Work / 'cottage-parts.blend'))
bpy.ops.object.select_all(action='DESELECT')
cottage.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(Work / 'cottage.glb'), export_format='GLB', use_selection=True, export_apply=True)
cottage.select_set(False)
for obj in parts:
    obj.location = (0, 0, 0)
    obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(Work / 'garden_parts.glb'), export_format='GLB', use_selection=True, export_apply=True)
(Work / 'garden-parts.json').write_text(json.dumps(records, indent=2) + '\n')
print('EXTRACTED_YARD_PARTS', len(parts), 'HOUSE_TRIANGLES', len(shell))
