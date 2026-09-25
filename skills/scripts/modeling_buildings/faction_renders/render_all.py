import os
import hashlib
import json
import math
import struct
from pathlib import Path

import bpy
from mathutils import Vector

Root = Path(__file__).resolve().parent
Pack = Path(os.environ['POLYWORLD_BUILDING_PACK'])
Textures = Pack / 'textures/factions'
Models = json.loads((Pack / 'manifest.json').read_text())['models']
Factions = json.loads((Textures / 'manifest.json').read_text())['factions']

def pointAt(obj, target):
  """Point a camera or light toward a world-space target."""
  obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()

def frameObject(obj, camera):
  """Center the projected bounds without changing world scale or camera angle."""
  orientation = (-Vector((10, -14, 9.9))).to_track_quat('-Z', 'Y')
  right = orientation @ Vector((1, 0, 0))
  up = orientation @ Vector((0, 1, 0))
  points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
  us = [point.dot(right) for point in points]
  vs = [point.dot(up) for point in points]
  center = right * ((min(us) + max(us)) / 2) + up * ((min(vs) + max(vs)) / 2)
  camera.location = center + Vector((10, -14, 9.9))
  camera.rotation_euler = orientation.to_euler()
  assert max(us) - min(us) < camera.data.ortho_scale * .93
  assert max(vs) - min(vs) < camera.data.ortho_scale * .93
  return {'projected_width': max(us) - min(us), 'projected_height': max(vs) - min(vs),
    'camera_location': list(camera.location), 'camera_rotation': list(camera.rotation_euler)}

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x = scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'Standard'
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.world = bpy.data.worlds.new('Neutral daylight')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.65, .72, .82, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = .7

assets = []
for model in Models:
  path = Pack / model['file']
  assert hashlib.sha256(path.read_bytes()).hexdigest() == model['sha256']
  existing = set(scene.objects)
  bpy.ops.import_scene.gltf(filepath=str(path))
  added = set(scene.objects) - existing
  meshes = [obj for obj in added if obj.type == 'MESH']
  assert len(meshes) == 1, model['name']
  obj = meshes[0]
  assert obj.data.uv_layers.active is not None
  nodes = [node for material in obj.data.materials if material and material.use_nodes
    for node in material.node_tree.nodes if node.type == 'TEX_IMAGE']
  assert nodes, model['name']
  obj.hide_render = True
  assets.append((model, obj, nodes))

bpy.ops.mesh.primitive_plane_add(size=200)
plane = bpy.context.object
ground = bpy.data.materials.new('Warm neutral ground')
ground.diffuse_color = (.79, .80, .79, 1)
plane.data.materials.append(ground)
light = bpy.data.lights.new('Large soft key', 'AREA')
light.energy = 1800
light.shape = 'DISK'
light.size = 8
lamp = bpy.data.objects.new('Large soft key', light)
scene.collection.objects.link(lamp)
lamp.location = (-5, -8, 14)
pointAt(lamp, (0, 0, 1.5))
cameraData = bpy.data.cameras.new('Fixed world scale isometric camera')
cameraData.type = 'ORTHO'
cameraData.ortho_scale = 11.4
camera = bpy.data.objects.new('Fixed world scale isometric camera', cameraData)
scene.collection.objects.link(camera)
scene.camera = camera
neutralImage = bpy.data.images.load(str(Pack / 'textures/buildings-atlas.png'), check_existing=True)
images = {faction['faction']: bpy.data.images.load(str(Textures / faction['file']), check_existing=True)
  for faction in Factions}
assert all(list(image.size) == [512, 512] for image in images.values())
results = []
for model, obj, nodes in assets:
  obj.hide_render = False
  bpy.context.view_layer.update()
  framing = frameObject(obj, camera)
  variants = Factions if model['name'] != 'gold_mine' else [None]
  for faction in variants:
    slug = Path(faction['file']).stem if faction else 'neutral'
    image = images[faction['faction']] if faction else neutralImage
    for node in nodes:
      node.image = image
    destination = Root / 'renders' / slug / (model['name'] + '.png')
    destination.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(destination)
    bpy.ops.render.render(write_still=True)
    results.append({'building': model['name'],
      'faction': faction['faction'] if faction else 'Neutral',
      'render': str(destination.relative_to(Root)),
      'texture': str(Path(image.filepath).resolve()),
      'texture_dimensions': list(image.size),
      'vertices': len(obj.data.vertices), 'model_sha256': model['sha256'],
      'ortho_scale': cameraData.ortho_scale, **framing})
    (Root / 'render-manifest.json').write_text(json.dumps(results, indent=2) + '\n')
    print(f'RENDER {len(results)}/65 {model["name"]} {slug}', flush=True)
  obj.hide_render = True

assert len(results) == 65
assert all(hashlib.sha256((Pack / model['file']).read_bytes()).hexdigest() == model['sha256']
  for model in Models)
print('PASS: 64 faction building renders and one neutral mine; all source GLBs unchanged.', flush=True)
