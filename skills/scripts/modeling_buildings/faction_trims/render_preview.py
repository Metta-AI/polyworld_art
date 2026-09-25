import os
import json
from pathlib import Path

import bpy
from mathutils import Vector

Root = Path(__file__).resolve().parent
Pack = Path(os.environ['POLYWORLD_BUILDING_PACK'])
Textures = Pack / 'textures/factions'

def pointAt(obj, target):
  """Point the camera or light toward the building center."""
  obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.resolution_x = scene.render.resolution_y = 640
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'Standard'
scene.render.image_settings.file_format = 'PNG'
scene.world = bpy.data.worlds.new('Neutral daylight')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.65, .72, .82, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = .7
bpy.ops.import_scene.gltf(filepath=str(Pack / 'models/town_hall.glb'))
objects = [obj for obj in scene.objects if obj.type == 'MESH']
assert len(objects) == 1
townHall = objects[0]
textureNodes = [node for material in townHall.data.materials if material.use_nodes
  for node in material.node_tree.nodes if node.type == 'TEX_IMAGE']
assert len(textureNodes) == 1
bpy.ops.mesh.primitive_plane_add(size=200)
plane = bpy.context.object
material = bpy.data.materials.new('Warm neutral ground')
material.diffuse_color = (.79, .80, .79, 1)
plane.data.materials.append(material)
light = bpy.data.lights.new('Large soft key', 'AREA')
light.energy = 1800
light.shape = 'DISK'
light.size = 8
lamp = bpy.data.objects.new('Large soft key', light)
scene.collection.objects.link(lamp)
lamp.location = (-5, -8, 14)
pointAt(lamp, (0, 0, 1.5))
camera = bpy.data.cameras.new('Shared isometric camera')
camera.type = 'ORTHO'
camera.ortho_scale = 11.4
cameraObject = bpy.data.objects.new('Shared isometric camera', camera)
scene.collection.objects.link(cameraObject)
cameraObject.location = (10, -14, 12)
pointAt(cameraObject, (0, 0, 2.1))
scene.camera = cameraObject
(Root / 'buildings').mkdir(exist_ok=True)
results = []
for faction in json.loads((Textures / 'manifest.json').read_text())['factions']:
  image = bpy.data.images.load(str(Textures / faction['file']), check_existing=True)
  assert list(image.size) == [512, 512]
  textureNodes[0].image = image
  scene.render.filepath = str(Root / 'buildings' / faction['file'])
  bpy.ops.render.render(write_still=True)
  results.append({'faction': faction['faction'], 'texture': str(Textures / faction['file']),
    'size': list(image.size), 'vertices': len(townHall.data.vertices),
    'render': scene.render.filepath})
  print('Rendered ' + faction['faction'], flush=True)
(Root / 'blender-verification.json').write_text(json.dumps(results, indent=2) + '\n')
