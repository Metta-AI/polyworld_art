import os
import hashlib
import json
import math
from pathlib import Path

import bmesh
import bpy

Root = Path(__file__).resolve().parent

def fingerprint(group):
  """Record untouched asset geometry and placements before the edit."""
  records = []
  for obj in sorted(group.objects, key=lambda item: item.name):
    record = [obj.name, list(obj.location), list(obj.rotation_euler),
      list(obj.scale)]
    if obj.type == 'MESH':
      record.append([list(vertex.co) for vertex in obj.data.vertices])
      record.append([list(face.vertices) for face in obj.data.polygons])
    if obj.instance_type == 'COLLECTION':
      record.append(obj.instance_collection.name)
    records.append(record)
  return hashlib.sha256(json.dumps(records).encode()).hexdigest()

def mirror(obj):
  """Replace the full frame part with a half mesh and live X mirror."""
  data = bmesh.new()
  data.from_mesh(obj.data)
  bmesh.ops.bisect_plane(
    data,
    geom=list(data.verts)+list(data.edges)+list(data.faces),
    dist=.00001,
    plane_co=(0,0,0),
    plane_no=(1,0,0),
    clear_inner=True,
    clear_outer=False,
  )
  for face in list(data.faces):
    if all(abs(vertex.co.x) < .00002 for vertex in face.verts):
      data.faces.remove(face)
  data.to_mesh(obj.data)
  data.free()
  modifier = obj.modifiers.new('Mirror - edit one half', 'MIRROR')
  modifier.use_axis = (True,False,False)
  modifier.use_clip = True
  modifier.use_mirror_merge = True
  modifier.merge_threshold = .0001
  obj.modifiers.move(len(obj.modifiers)-1, 0)
  obj['construction'] = 'Half mesh with unapplied Mirror'

groups = [bpy.data.collections[name] for name in [
  '01 Town Hall', '02 Farm', '03 Barracks', '04 Lumber Mill', '05 Tower',
  '06 Stables and Kennels', '07 Church and Temple', '08 Blacksmith',
  '09 Gold Mine']]
untouched = {group.name: fingerprint(group) for group in groups[1:8]}
bpy.data.objects['Hall Wing 1 - left - live mirror'].rotation_euler.z = -math.pi/2
bpy.data.objects['Hall Wing 2 - right - live mirror'].rotation_euler.z = math.pi/2
mine = groups[-1]
keep = ('Mine timber upright', 'Mine diagonal knee', 'Mine timber header',
  'Mine roofless depth support', 'Mine dark tunnel')
removed = []
for obj in list(mine.objects):
  if not obj.name.startswith(keep):
    removed.append(obj.name)
    bpy.data.objects.remove(obj, do_unlink=True)
for prefix in ('Mine timber upright', 'Mine diagonal knee',
  'Mine roofless depth support'):
  pair = [obj for obj in mine.objects if obj.name.startswith(prefix)]
  for obj in pair:
    center = sum(vertex.co.x for vertex in obj.data.vertices)/len(obj.data.vertices)
    if center < 0:
      bpy.data.objects.remove(obj, do_unlink=True)
    else:
      mirror(obj)
      obj.name = prefix + ' - mirrored'
tunnel = bpy.data.objects['Mine dark tunnel']
for vertex in tunnel.data.vertices:
  vertex.co.x *= 1.04/1.42
  vertex.co.y = vertex.co.y - .18 - .56
  vertex.co.z = (vertex.co.z-.96)*1.65/1.79 + .885
mirror(tunnel)
mirror(bpy.data.objects['Mine timber header'])
mine['construction'] = 'Entrance only; map provides rock and ore assets'
stage = bpy.data.scenes['00 - Building Review Stage']
bpy.data.objects['Gold Mine Stage instance'].scale = (1.55,1.55,1.55)
for scene in list(bpy.data.scenes):
  if scene.name.startswith('MODULE - Mine cart'):
    bpy.data.scenes.remove(scene)
for group in list(bpy.data.collections):
  if group.name.startswith('MODULE - Mine cart'):
    for obj in list(group.objects):
      bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(group)
for mesh in list(bpy.data.meshes):
  if mesh.users == 0:
    bpy.data.meshes.remove(mesh)
for image in bpy.data.images:
  if 'buildings-atlas' in image.name:
    image.unpack(method='REMOVE')
    image.filepath = str(Root/'assets'/'buildings-atlas.png')
    image.reload()
    image.pack()
for scene in bpy.data.scenes:
  if 'polyworld-buildings-20260922' in scene.render.filepath:
    scene.render.filepath = str(Root/'renders'/'buildings-stage.png')
assert all(fingerprint(group) == untouched[group.name] for group in groups[1:8])
notes = bpy.data.texts['START HERE - Building kit']
notes.clear()
notes.write('The opening scene is the 3x3 building review stage.\n'
  'Use numbered asset scenes or MODULE scenes to edit source geometry.\n'
  'Town Hall has a mirrored center and three linked mirrored wings. '
  'Its two side wings rotate -90 and +90 degrees into the center.\n'
  'Farm uses four rotated mirrored fences and sixteen scaled pumpkin instances.\n'
  'Tower uses live sixfold arrays with a 60-degree controller, with no crystal.\n'
  'Gold Mine is a mirrored timber entrance and dark inset only. '
  'Assemble surrounding rock and ore from map assets.\n'
  'Mirrors, arrays and linked modules are unapplied. The atlas is packed.\n')
meshObjects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
mirrors = [obj.name for obj in meshObjects
  if any(mod.type == 'MIRROR' for mod in obj.modifiers)]
arrays = [{'object':obj.name, 'count':mod.count,
  'rotation_degrees':round(math.degrees(mod.offset_object.rotation_euler.z),2)}
  for obj in meshObjects for mod in obj.modifiers
  if mod.type == 'ARRAY' and mod.offset_object]
placements = [{'object':obj.name, 'source':obj.instance_collection.name,
  'location':list(obj.location), 'scale':list(obj.scale),
  'rotation_degrees':round(math.degrees(obj.rotation_euler.z),2)}
  for obj in bpy.data.objects if obj.instance_type == 'COLLECTION']
report = {'asset_collections':[group.name for group in groups],
  'mirror_count':len(mirrors), 'mirrored_objects':mirrors,
  'radial_arrays':arrays, 'collection_instances':placements,
  'source_mesh_count':len(bpy.data.meshes),
  'source_faces':sum(len(mesh.polygons) for mesh in bpy.data.meshes),
  'atlas_packed':all(image.packed_file for image in bpy.data.images
    if 'buildings-atlas' in image.name),
  'missing_uvs':[obj.name for obj in meshObjects if not obj.data.uv_layers],
  'source_scenes':[scene.name for scene in bpy.data.scenes],
  'mine_entrance_only':True, 'removed_mine_parts':removed,
  'unchanged_assets':list(untouched)}
(Root/'reviews'/'structure-audit.json').write_text(json.dumps(report,indent=2))
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
print('Revised preview complete.', flush=True)
