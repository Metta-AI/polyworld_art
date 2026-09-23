"""Render the Druid Warden's actual authoring geometry for fit review."""

import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector

Root = Path('/Users/me/p/polyworld_art/characters/chargen')
Output = Root / 'source/gota/druid_warden'
sys.path.insert(0, str(Root / 'source/scripts'))
from clothes import bodySurface, clip, meshObject
bpy.ops.wm.open_mainfile(filepath=str(Output / 'hero.blend'))
shown = set(json.loads((Output / 'verification.json').read_text())['nodes'])
rig = bpy.data.objects['CharacterRig']
rig.animation_data.action = None
rig.data.pose_position = 'REST'
for bone in rig.pose.bones:
  bone.matrix_basis.identity()
skin = bpy.data.materials.new('Druid preview skin')
skin.use_nodes = True
skin.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.969, .820, .710, 1)
skin.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .95
for name in ['Body', 'Head', 'Hand.Left', 'Hand.Right', 'Ears_Elf_Left',
             'Ears_Elf_Right', 'Nose_Tiny']:
  obj = bpy.data.objects[name]
  for i in range(len(obj.data.materials)):
    obj.data.materials[i] = skin
if 'GotaSkinUpper' in shown and not bpy.data.objects.get('GotaSkinUpper'):
  original = bpy.data.objects['Body']
  obj = meshObject(original.users_collection[0], 'GotaSkinUpper',
    [(clip(bodySurface([original]), lambda p: p.z - 1.255), 0)], [skin])
  obj.parent = rig
  obj.modifiers.new('Shared humanoid rig', 'ARMATURE').object = rig
for name in ['Hand.Left', 'Hand.Right']:
  if 'Gota' + name in shown and not bpy.data.objects.get('Gota' + name):
    obj = bpy.data.objects[name].copy()
    obj.name = 'Gota' + name
    sceneCollection = bpy.context.scene.collection
    sceneCollection.objects.link(obj)
for obj in bpy.data.objects:
  obj.hide_set(False)
bpy.context.view_layer.update()
graph = bpy.context.evaluated_depsgraph_get()
copies = []
for name in shown:
  obj = bpy.data.objects.get(name)
  if not obj or obj.type != 'MESH':
    continue
  data = bpy.data.meshes.new_from_object(obj.evaluated_get(graph))
  copies.append((name, data))
for obj in list(bpy.data.objects):
  bpy.data.objects.remove(obj, do_unlink=True)
scene = bpy.context.scene
for name, data in copies:
  for x, angle in [(-1.7, 0), (1.7, math.pi)]:
    obj = bpy.data.objects.new(name + str(x), data)
    scene.collection.objects.link(obj)
    obj.matrix_world = Matrix.Translation((x, 0, 0)) @ Matrix.Rotation(angle, 4, 'Z')
for material in bpy.data.materials:
  if material.use_nodes:
    shader = material.node_tree.nodes.get('Principled BSDF')
    if shader:
      color = shader.inputs['Base Color'].default_value
      shader.inputs['Base Color'].default_value = tuple([
        c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4
        for c in color[:3]]) + (color[3],)
scene.render.engine = 'CYCLES'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.resolution_x = 1600
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.view_settings.view_transform = 'Standard'
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.75, .75, .75, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = .75
for name, direction, power in [('Key', (-3, -5, 7), 2.2), ('Fill', (4, -3, 4), .6)]:
  data = bpy.data.lights.new(name, 'SUN')
  data.energy, data.angle = power, .35
  obj = bpy.data.objects.new(name, data)
  scene.collection.objects.link(obj)
  obj.rotation_euler = (-Vector(direction)).to_track_quat('-Z', 'Y').to_euler()
camera = bpy.data.objects.new('Camera', bpy.data.cameras.new('Camera'))
scene.collection.objects.link(camera)
camera.location = (0, -18, 1.86)
camera.rotation_euler = Vector((0, 1, 0)).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 6.8
scene.camera = camera
scene.render.filepath = str(Output / 'authoring_front_back.png')
bpy.ops.render.render(write_still=True)

# Keep the exact model meshes for a separate five-slot front/back review.
for obj in list(bpy.data.objects):
  if obj.type == 'MESH':
    bpy.data.objects.remove(obj, do_unlink=True)
parts = json.loads((Output / 'parts.json').read_text())
lookup = dict(copies)
slots = ['Foot', 'Leg', 'Belt', 'Chest', 'Headgear']
for row, category in enumerate(slots):
  descriptor = next(part for part in parts if part['category'] == category)
  meshes = [lookup[name] for name in descriptor['nodes']]
  low = Vector([min(v.co[i] for data in meshes for v in data.vertices) for i in range(3)])
  high = Vector([max(v.co[i] for data in meshes for v in data.vertices) for i in range(3)])
  center = (low + high) / 2
  scale = min(1.92 / (high.x - low.x), .82 / (high.z - low.z))
  for x, angle in [(-1.1, 0), (1.1, math.pi)]:
    for data in meshes:
      obj = bpy.data.objects.new(category + str(x), data)
      scene.collection.objects.link(obj)
      obj.matrix_world = (Matrix.Translation((x, 0, 4.8 - row * 1.05)) @
        Matrix.Scale(scale, 4) @ Matrix.Rotation(angle, 4, 'Z') @
        Matrix.Translation(-center))
scene.render.resolution_x = 1200
scene.render.resolution_y = 1600
camera.location.z = 2.7
camera.data.ortho_scale = 6.0
scene.render.filepath = str(Output / 'modeled_items_front_back.png')
bpy.ops.render.render(write_still=True)
