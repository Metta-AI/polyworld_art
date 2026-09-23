"""Render the actual Arcanist modular clothes in front and back pairs."""
import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

Directory = Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(Directory / 'hero.blend'))
rig = bpy.data.objects['CharacterRig']
rig.animation_data.action = None
rig.data.pose_position = 'REST'
parts = json.loads((Directory / 'parts.json').read_text())
scene = bpy.context.scene
copies = []
for row, part in enumerate(parts):
  objects = [bpy.data.objects[name] for name in part['nodes']]
  points = [v.co for obj in objects for v in obj.data.vertices]
  low = Vector([min(p[i] for p in points) for i in range(3)])
  high = Vector([max(p[i] for p in points) for i in range(3)])
  center = (high + low) / 2
  scale = min(1.90 / (high.x-low.x), 1.30 / (high.z-low.z))
  for x, angle in [(-1.24, 0), (1.24, math.pi)]:
    for obj in objects:
      copy = bpy.data.objects.new('Render_' + obj.name, obj.data.copy())
      scene.collection.objects.link(copy)
      copy.matrix_world = (Matrix.Translation((x, 0, 3.36 - row*1.68)) @
                           Matrix.Rotation(angle, 4, 'Z') @
                           Matrix.Scale(scale, 4) @ Matrix.Translation(-center))
      copies.append(copy)
for obj in list(bpy.data.objects):
  if obj not in copies:
    bpy.data.objects.remove(obj, do_unlink=True)
for mat in bpy.data.materials:
  if mat.use_nodes:
    shader = mat.node_tree.nodes.get('Principled BSDF')
    if shader:
      rgb = shader.inputs['Base Color'].default_value[:3]
      shader.inputs['Base Color'].default_value = tuple(
        c / 12.92 if c <= .04045 else ((c + .055) / 1.055)**2.4
        for c in rgb) + (1,)
world = bpy.data.worlds.new('Arcanist clothing studio')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.22,.25,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.7
scene.world=world
for name, direction, power in [('Key',(-3,-5,7),2),('Fill',(4,-3,3),.6)]:
  light=bpy.data.lights.new(name,'SUN');light.energy=power;light.angle=.4
  obj=bpy.data.objects.new(name,light);scene.collection.objects.link(obj)
  obj.rotation_euler=(-Vector(direction)).to_track_quat('-Z','Y').to_euler()
camera=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'))
scene.collection.objects.link(camera)
camera.location=(0,-25,0)
camera.rotation_euler=(-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO';camera.data.ortho_scale=9.15
scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.samples=32
scene.cycles.use_denoising=True
scene.render.resolution_x=1100;scene.render.resolution_y=1800
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='Standard'
scene.render.filepath=str(Directory/'items_front_back.png')
bpy.ops.render.render(write_still=True)
