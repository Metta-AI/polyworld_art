"""Render exported models in fresh scenes for repeatable visual inspection."""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

def render(path, output, view):
    """Reimport one export and render an orthographic inspection view."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(path))
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    points = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    lower = Vector(tuple(min(p[i] for p in points) for i in range(3)))
    upper = Vector(tuple(max(p[i] for p in points) for i in range(3)))
    center = (lower + upper) / 2
    size = max(upper - lower)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 12
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 640
    scene.render.resolution_y = 640
    scene.render.resolution_percentage = 100
    scene.world = bpy.data.worlds.new('Review world')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.7,.7,.7,1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .8
    directions = {'oblique': (.7,-1,.85), 'front': (0,-1,0),
                  'back': (0,1,0), 'side': (1,0,0), 'top': (0,0,1)}
    bpy.ops.object.camera_add(location=center+Vector(directions[view]).normalized()*size*3)
    camera = bpy.context.object
    camera.rotation_euler = (center-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = size * 1.4
    scene.camera = camera
    bpy.ops.object.light_add(type='AREA',location=center+Vector((-1,-2,3))*size)
    bpy.context.object.data.energy = 90*size*size
    bpy.context.object.data.size = size*2
    scene.view_settings.view_transform = 'Standard'
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = str(output / (path.stem+'-'+view+'.png'))
    bpy.ops.render.render(write_still=True)
    print('RENDER', path.stem, view, flush=True)

args = sys.argv[sys.argv.index('--')+1:]
source, output = Path(args[0]), Path(args[1])
output.mkdir(parents=True, exist_ok=True)
views = args[2].split(',') if len(args)>2 else ['oblique']
pattern = args[3] if len(args)>3 else '*.glb'
for path in sorted(source.glob(pattern)):
    for view in views:
        render(path, output, view)
