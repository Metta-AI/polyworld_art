"""Broaden the reviewed cottage's grassy bank without distorting its facade."""
import bpy
from pathlib import Path
from math import hypot

Art = Path(__file__).resolve().parents[3]
Work = Art / 'tmp/heartleaf-refine'
Work.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(Art / 'terrain/blender_village/models/hobbit_house.glb'))
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    obj.name = 'cottage'
    # Preserve the circular footprint and the exact front join. Widen only
    # the low bank and its rooted rear decoration, leaving doors untouched.
    for vertex in obj.data.vertices:
        x, y, z = vertex.co
        if y < -0.22:
            front = -y - 0.22
            vertex.co.x *= 1 + 0.15 * min(1, front / 0.58)
            vertex.co.y -= front * 0.4
        if y <= 0.12:
            continue
        fade = min(1.0, max(0.0, (y - 0.12) / 1.1))
        fade = fade * fade * (3 - 2 * fade)
        foot = max(0.0, 1 - z / 3.5) ** 2
        stretch = 1 + 0.15 * foot * fade
        vertex.co.x = x * stretch
        vertex.co.y = 2.15 + (y - 2.15) * stretch
    # Move golden timber UVs onto the existing quiet brown timber strip.
    # The independent door stain, stone, glass and foliage remain untouched.
    uv = obj.data.uv_layers.active
    wood_faces = 0
    for polygon in obj.data.polygons:
        if 'Painted trim' not in obj.data.materials[polygon.material_index].name:
            continue
        loops = [uv.data[i] for i in polygon.loop_indices]
        for lo, hi in [(.8359, .9979), (.6713, .8317)]:
            if all(.2535 <= loop.uv.x <= .4977 and lo-.0001 <= loop.uv.y <= hi+.0001
                   for loop in loops):
                for loop in loops:
                    loop.uv.x = .504 + (loop.uv.x - .2536) / (.4976 - .2536) * (.7464 - .504)
                    loop.uv.y = .8359 + (loop.uv.y - lo) / (hi - lo) * (.9979 - .8359)
                wood_faces += 1
                break
    turf = bpy.data.images.load(str(Art / 'terrain/tiles/heartleaf-turf.rgb.png'))
    turf.pack()
    for material in obj.data.materials:
        if material.name.startswith('Grass |'):
            for node in material.node_tree.nodes:
                if node.type == 'TEX_IMAGE':
                    node.image = turf
    for polygon in obj.data.polygons:
        if obj.data.materials[polygon.material_index].name.startswith('Grass |'):
            for index in polygon.loop_indices:
                uv.data[index].uv *= 1.0
    print('BROWN_TIMBER_FACES', wood_faces)
    obj.data.update()
    obj['source'] = 'Reviewed CC0 hobbit_house.glb; circular lower bank broadened, facade unchanged.'
    obj['reference'] = 'User Heartleaf town illustration and 2026-09-25 comparison.'
    # Preserve editable symmetry; evaluate a copy during export.
    mirror = obj.modifiers.new('Editable bilateral cottage', 'MIRROR')
    mirror.use_bisect_axis[0] = True
    mirror.use_clip = True
bpy.ops.wm.save_as_mainfile(filepath=str(Work / 'cottage.blend'))
bpy.ops.export_scene.gltf(filepath=str(Work / 'cottage.glb'), export_format='GLB', export_apply=True)
print('HEARTLEAF_COTTAGE_EXPORTED')
