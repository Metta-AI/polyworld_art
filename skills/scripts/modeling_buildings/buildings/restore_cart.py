import os
import json
import math
from pathlib import Path

import bpy

Root = Path(__file__).resolve().parent
backup = Root/'versions'/'before-entrance-and-wing-changes.blend'
mine = bpy.data.collections['09 Gold Mine']
with bpy.data.libraries.load(str(backup), link=False) as (source, target):
  target.scenes = ['MODULE - Mine cart - Edit source']
  target.objects = [name for name in source.objects
    if name.startswith(('Mine rail','Mine sleeper','Mine linked rail sleeper'))]
for obj in target.objects:
  mine.objects.link(obj)
cart = bpy.data.collections['MODULE - Mine cart']
for obj in list(cart.objects)+list(target.objects):
  if obj.type == 'MESH':
    for slot in obj.material_slots:
      if slot.material:
        base = slot.material.name.split('.00')[0]
        if base in bpy.data.materials:
          slot.material = bpy.data.materials[base]
placement = bpy.data.objects.new('Mine ore cart - linked source',None)
mine.objects.link(placement)
placement.instance_type = 'COLLECTION'
placement.instance_collection = cart
placement.location = (.01,-1.35,.11)
placement.empty_display_size = .16
placement['construction'] = 'Linked collection instance'
mine['construction'] = 'Entrance and gold cart; map provides surrounding rocks'
stage = bpy.data.scenes['00 - Building Review Stage']
stageMine = bpy.data.objects['Gold Mine Stage instance']
stageMine.scale = (1.4,1.4,1.4)
stageMine.location.y += .30/math.sin(math.radians(43))
for material in list(bpy.data.materials):
  if material.users == 0:
    bpy.data.materials.remove(material)
for image in list(bpy.data.images):
  if image.users == 0:
    bpy.data.images.remove(image)
  elif 'buildings-atlas' in image.name:
    image.unpack(method='REMOVE')
    image.filepath = str(Root/'assets'/'buildings-atlas.png')
    image.reload()
    image.pack()
    image.filepath = '//assets/buildings-atlas.png'
notes = bpy.data.texts['START HERE - Building kit']
text = notes.as_string().replace(
  'Gold Mine is a mirrored timber entrance and dark inset only. '
  'Assemble surrounding rock and ore from map assets.',
  'Gold Mine has a mirrored timber entrance, dark inset, gold-filled cart '
  'and short rails. Assemble surrounding rocks from map assets.')
notes.clear()
notes.write(text)
reportPath = Root/'reviews'/'structure-audit.json'
report = json.loads(reportPath.read_text())
report.pop('mine_entrance_only',None)
report['mine_rock_free'] = True
report['mine_gold_cart_restored'] = True
report['source_scenes'] = [scene.name for scene in bpy.data.scenes]
report['source_mesh_count'] = len(bpy.data.meshes)
report['source_faces'] = sum(len(mesh.polygons) for mesh in bpy.data.meshes)
report['collection_instances'] = [{'object':obj.name,
  'source':obj.instance_collection.name,'location':list(obj.location),
  'scale':list(obj.scale),
  'rotation_degrees':round(math.degrees(obj.rotation_euler.z),2)}
  for obj in bpy.data.objects if obj.instance_type == 'COLLECTION']
reportPath.write_text(json.dumps(report,indent=2))
bpy.context.window.scene = stage
stage.render.filepath = str(Root/'renders'/'buildings-stage.png')
stage.render.resolution_x = stage.render.resolution_y = 2560
stage.cycles.samples = 64
bpy.ops.wm.save_as_mainfile(filepath=str(Root/'polyworld-buildings.blend'))
stage.render.resolution_x = stage.render.resolution_y = 1800
stage.cycles.samples = 32
stage.render.filepath = str(Root/'renders'/'stage-preview.png')
if os.environ.get('POLYWORLD_BUILDINGS_SKIP_RENDER') != '1':
  bpy.ops.render.render(write_still=True)
