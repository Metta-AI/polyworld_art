import os
import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

Root = Path(__file__).resolve().parent
Factors = {
  'town_hall':1.50/1.13, 'farm':1.0, 'barracks':1.50/1.65,
  'lumber_mill':1.50/1.57, 'tower':1.40, 'stables':1.50/1.425,
  'church':1.50/1.49, 'blacksmith':1.50/1.20, 'gold_mine':1.0,
}
Groups = {
  'town_hall':'01 Town Hall', 'farm':'02 Farm', 'barracks':'03 Barracks',
  'lumber_mill':'04 Lumber Mill', 'tower':'05 Tower',
  'stables':'06 Stables and Kennels', 'church':'07 Church and Temple',
  'blacksmith':'08 Blacksmith', 'gold_mine':'09 Gold Mine',
}
DoorObjects = {'town_hall':'Hall main entrance',
  'barracks':'Barracks double entrance','church':'Chapel arched entrance',
  'blacksmith':'Smith entry'}
Spacing = 10.0
Elevation = math.radians(43)
Sine,Cosine = math.sin(Elevation),math.cos(Elevation)

def scaleCollection(group,factor):
  """Scale direct placements without mutating shared module meshes."""
  bpy.context.window.scene = bpy.data.scenes[group.name+' - Edit source']
  bpy.context.view_layer.update()
  previous = group.get('door_scale_factor',1.0)
  transform = Matrix.Scale(factor/previous,4)
  for obj in group.objects:
    # This reused foundation is already scaled in its source collection.
    if obj.instance_type == 'COLLECTION' and obj.instance_collection.get('stage') == 'foundation':
      assert sum(abs(obj.matrix_basis[i][j]-(1 if i == j else 0))
        for i in range(4) for j in range(4)) < .00001
      continue
    assert obj.parent is None,obj.name
    obj.matrix_basis = transform @ obj.matrix_basis
  group['door_scale_factor'] = factor
  group['scale_reference'] = '1.50 unit entrance panel height; sixfold tower 1.40 art scale'

def pointsInCollection(group):
  """Measure evaluated live mirrors and nested instances in their edit scene."""
  scene = bpy.data.scenes[group.name+' - Edit source']
  bpy.context.window.scene = scene
  bpy.context.view_layer.update()
  graph = bpy.context.evaluated_depsgraph_get()
  occurrences = [(item.object.original,item.matrix_world.copy())
    for item in graph.object_instances if item.object.type == 'MESH']
  points = []
  for original,transform in occurrences:
    mesh = bpy.data.meshes.new_from_object(original.evaluated_get(graph),
      preserve_all_data_layers=True,depsgraph=graph)
    points.extend(transform @ vertex.co for vertex in mesh.vertices)
    bpy.data.meshes.remove(mesh)
  return points

def vectorBounds(points):
  """Return axis-aligned bounds for an evaluated asset."""
  return [[min(point[i] for point in points) for i in range(3)],
    [max(point[i] for point in points) for i in range(3)]]

def layoutStage(scene,displayName,overlayName):
  """Use one world scale and orthographic camera for every review sheet."""
  display = bpy.data.collections[displayName]
  instances = [obj for obj in display.objects if obj.instance_type == 'COLLECTION']
  records = []
  for obj in instances:
    row,column = [int(value)-1 for value in obj['stage_cell'].split(',')]
    group = obj.instance_collection
    rotation = Matrix.Rotation(-math.pi/6,4,'Z')
    points = [rotation @ point for point in pointsInCollection(group)]
    lowX,highX = min(v.x for v in points),max(v.x for v in points)
    lowY = min(v.y*Sine+v.z*Cosine for v in points)
    highY = max(v.y*Sine+v.z*Cosine for v in points)
    cellX,cellY = (column-1)*Spacing,(1-row)*Spacing
    centerY = cellY+.60
    obj.scale = (1,1,1)
    obj.rotation_euler = (0,0,-math.pi/6)
    obj.location = (cellX-(lowX+highX)/2,
      (centerY-(lowY+highY)/2)/Sine,0)
    assert highX-lowX < Spacing-.35,(group.name,highX-lowX)
    assert highY-lowY < Spacing-1.5,(group.name,highY-lowY)
    records.append({'collection':group.name,'display_scale':[1,1,1],
      'projected_width':highX-lowX,'projected_height':highY-lowY})
  oldSpacing = scene.get('common_scale_spacing',7.2)
  ratio = Spacing/oldSpacing
  plane = Vector((0,-Cosine,Sine))*25
  transform = Matrix.Translation(plane) @ Matrix.Scale(ratio,4) @ Matrix.Translation(-plane)
  for obj in bpy.data.collections[overlayName].objects:
    obj.matrix_basis = transform @ obj.matrix_basis
  scene.camera.data.ortho_scale = Spacing*3.08
  scene.render.resolution_x = scene.render.resolution_y = 2400
  scene.render.resolution_percentage = 100
  scene.cycles.samples = 40
  scene['common_scale_spacing'] = Spacing
  scene['scale_comparison'] = 'Every building uses display scale 1,1,1; camera identical across stages.'
  return records

originalScene = bpy.context.window.scene
records = []
for slug,name in Groups.items():
  group = bpy.data.collections[name]
  scaleCollection(group,Factors[slug])
  records.append({'building':slug,'stage':'finished','factor':Factors[slug],
    'bounds':vectorBounds(pointsInCollection(group))})
hasConstruction = bpy.data.collections.get('CONSTRUCTION - town_hall - foundation') is not None
if hasConstruction:
  for stage in ('foundation','walls'):
    for slug in list(Groups)[:-1]:
      group = bpy.data.collections[f'CONSTRUCTION - {slug} - {stage}']
      scaleCollection(group,Factors[slug])
      records.append({'building':slug,'stage':stage,'factor':Factors[slug],
        'bounds':vectorBounds(pointsInCollection(group))})
doors = {}
for slug,name in DoorObjects.items():
  obj = bpy.data.objects[name]
  points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
  height = max(point.z for point in points)-min(point.z for point in points)
  assert abs(height-1.5) < .00001,(slug,height)
  doors[slug] = {'panel_height':height,'panel_width':obj.dimensions.x}
stages = [(bpy.data.scenes['00 - Building Review Stage'],
  'STAGE - Nine linked assets','STAGE - Labels and dividers','buildings-stage-scaled')]
if hasConstruction:
  stages += [(bpy.data.scenes['CONSTRUCTION STAGE - '+label],
    'CONSTRUCTION DISPLAY - '+label,'CONSTRUCTION LABELS - '+label,file)
    for label,file in [('Foundation','construction-foundations-scaled'),
      ('Walls','construction-walls-scaled')]]
layouts = {}
for scene,display,overlay,filename in stages:
  layouts[scene.name] = layoutStage(scene,display,overlay)
  scene.render.filepath = str(Root/'renders'/(filename+'.png'))
  if hasConstruction and scene.name == '00 - Building Review Stage':
    continue
for slug,name in Groups.items():
  scene = bpy.data.scenes[name+' - Edit source']
  scene.camera.data.ortho_scale *= Factors[slug]/scene.get('door_scale_factor',1.0)
  scene['door_scale_factor'] = Factors[slug]
default = 'CONSTRUCTION STAGE - Walls' if hasConstruction else '00 - Building Review Stage'
bpy.context.window.scene = bpy.data.scenes[default]
for screen in bpy.data.screens:
  for area in screen.areas:
    if area.type == 'VIEW_3D':
      area.spaces.active.region_3d.view_perspective = 'CAMERA'
      area.spaces.active.region_3d.view_camera_zoom = 0
kind = 'construction' if hasConstruction else 'finished'
report = {'kind':kind,'factors':Factors,'door_panels':doors,'models':records,
  'stage_layouts':layouts,'tower_reference':'No door; scaled 1.40 for matching lookout headroom.',
  'chapel_reference':'Arched tile includes stone surround; visible leaf is slightly smaller.'}
(Root/'reviews'/('scale-'+kind+'.json')).write_text(json.dumps(report,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for scene,display,overlay,filename in stages:
  if hasConstruction and scene.name == '00 - Building Review Stage':
    continue
  bpy.context.window.scene = scene
  if os.environ.get('POLYWORLD_BUILDINGS_SKIP_RENDER') != '1':
    bpy.ops.render.render(write_still=True)
print('Rescaled '+kind+' source with preserved mirrors and shared modules.',flush=True)
