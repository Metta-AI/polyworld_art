import os
import ast
import hashlib
import json
import math
import struct
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

Root = Path(__file__).resolve().parent
Pack = Root/'exports/construction'
manifest = json.loads((Pack/'construction-manifest.json').read_text())
evidence = json.loads((Root/'reviews/construction-export.json').read_text())
origins = {item['name']:item['blender_origin_offset'] for item in
  json.loads((Root/'reviews/glb-export.json').read_text())['models']}
sources = {item['name']:item for item in evidence['models']}
structure = json.loads((Root/'reviews/construction-structure.json').read_text())
helperTree = ast.parse((Root/'verify_glbs.py').read_text())
helperTree.body = [node for node in helperTree.body
  if isinstance(node,ast.FunctionDef) and node.name in ('readGlb','accessor')]
exec(compile(helperTree,str(Root/'verify_glbs.py'),'exec'),globals())

def geometry(scene):
  """Evaluate the source exactly as Blender renders collection instances."""
  bpy.context.window.scene = scene
  bpy.context.view_layer.update()
  graph = bpy.context.evaluated_depsgraph_get()
  occurrences = [(item.object.original,item.matrix_world.copy())
    for item in graph.object_instances if item.object.type == 'MESH']
  vertices,faces = [],[]
  for original,transform in occurrences:
    assert original.get('atlas_region') in {'stone','plaster','wood','gray','soil'}, (
      original.name,original.get('atlas_region'))
    mesh = bpy.data.meshes.new_from_object(original.evaluated_get(graph),
      preserve_all_data_layers=True,depsgraph=graph)
    start = len(vertices)
    vertices.extend(transform @ vertex.co for vertex in mesh.vertices)
    faces.extend(tuple(start+index for index in face.vertices)
      for face in mesh.polygons)
    bpy.data.meshes.remove(mesh)
  return occurrences,vertices,faces

def checkContainer(model):
  """Validate self-contained GLBs with one mesh and completed-model origins."""
  path = Pack/model['file']
  assert hashlib.sha256(path.read_bytes()).hexdigest() == model['sha256']
  document,binary = readGlb(path)
  assert len(document['scenes']) == len(document['nodes']) == len(document['meshes']) == 1
  assert document['scenes'][0]['nodes'] == [0]
  assert document['nodes'][0]['name'] == model['name']
  assert not document.get('cameras') and not document.get('animations')
  assert len(document['images']) == 1
  assert all('uri' not in item for item in document['buffers'])
  for image in document['images']:
    assert 'uri' in image and 'bufferView' not in image
    texture = path.parent/image['uri']
    assert texture.resolve() == (Pack/'textures/buildings-atlas.png').resolve()
    assert struct.unpack_from('>II',texture.read_bytes(),16) == (512,512)
  positions,triangles = [],0
  for primitive in document['meshes'][0]['primitives']:
    attributes = primitive['attributes']
    points = accessor(document,binary,attributes['POSITION'])
    indices = accessor(document,binary,primitive['indices'])
    assert len(indices)%3 == 0
    assert all(0 <= index[0] < len(points) for index in indices)
    assert all(math.isfinite(value) for point in points for value in point)
    assert len(accessor(document,binary,attributes['TEXCOORD_0'])) == len(points)
    assert len(accessor(document,binary,attributes['NORMAL'])) == len(points)
    triangles += len(indices)//3
    positions.extend(points)
  low = [min(point[i] for point in positions) for i in range(3)]
  high = [max(point[i] for point in positions) for i in range(3)]
  assert abs(low[1]) < .0001
  assert triangles == model['triangles']
  assert all(abs(high[i]-low[i]-model['dimensions'][i]) < .0001 for i in range(3))
  assert sources[model['name']]['blender_origin_offset'] == origins[model['building']]
  return {'name':model['name'],'triangles':triangles,
    'embedded_images':0,'external_dependencies':1,'completed_origin_match':True}

assert len(manifest['models']) == 16
assert sum(model['stage'] == 'foundation' for model in manifest['models']) == 8
assert sum(model['stage'] == 'walls' for model in manifest['models']) == 8
assert not any(model['building'] == 'gold_mine' for model in manifest['models'])
sourceChecks = []
for item in structure['variants']:
  scene = bpy.data.scenes[item['source_scene']]
  factor = bpy.data.collections[item['collection']].get('door_scale_factor',1.0)
  occurrences,vertices,faces = geometry(scene)
  mirrorCount = sum(mod.type == 'MIRROR' for original,transform in occurrences
    for mod in original.modifiers)
  arrays = [mod for original,transform in occurrences for mod in original.modifiers
    if mod.type == 'ARRAY']
  if item['building'] == 'tower':
    assert arrays and all(mod.count == 6 and
      abs(mod.offset_object.rotation_euler.z-math.pi/3) < .00001 for mod in arrays)
  if item['stage'] == 'foundation':
    assert max(vertex.z for vertex in vertices) <= .62*factor
  record = {'building':item['building'],'stage':item['stage'],
    'live_mirrors':mirrorCount,'live_radial_arrays':len(arrays),
    'allowed_material_regions_only':True}
  if item['stage'] == 'walls':
    tree = BVHTree.FromPolygons(vertices,faces,all_triangles=False)
    probes = {
      'town_hall':[(0,.06,.4)],'barracks':[(0,0,.48)],
      'tower':[(0,0,.42)],'church':[(0,0,.4),(1.10,-.85,.4)],
      'blacksmith':[(-.5,.2,.32),(.33,-.75,.32)],
    }.get(item['building'],[])
    for x,y,height in probes:
      x,y,height = x*factor,y*factor,height*factor
      hit,normal,index,distance = tree.ray_cast(Vector((x,y,10)),Vector((0,0,-1)),20)
      assert hit is not None and abs(hit.z-height) < .03, (item,hit,height)
    record['open_roof_rays_passed'] = len(probes)
  sourceChecks.append(record)

results = []
for model in manifest['models']:
  record = checkContainer(model)
  source = sources[model['name']]
  probe = bpy.data.scenes.new('CONSTRUCTION GLB PROBE - '+model['name'])
  bpy.context.window.scene = probe
  bpy.ops.import_scene.gltf(filepath=str(Pack/model['file']))
  bpy.context.view_layer.update()
  meshes = [obj for obj in probe.objects if obj.type == 'MESH']
  assert len(meshes) == 1
  points = [obj.matrix_world @ vertex.co for obj in meshes for vertex in obj.data.vertices]
  low = [min(point[i] for point in points) for i in range(3)]
  high = [max(point[i] for point in points) for i in range(3)]
  expectedLow,expectedHigh = source['blender_bounds']
  assert all(abs(low[i]-expectedLow[i]) < .0001 and
    abs(high[i]-expectedHigh[i]) < .0001 for i in range(3))
  group = bpy.data.collections.new('CONSTRUCTION GLB - '+model['name'])
  for obj in meshes:
    group.objects.link(obj)
  group.instance_offset = -Vector(source['blender_origin_offset'])
  stageName = 'Foundation' if model['stage'] == 'foundation' else 'Walls'
  display = bpy.data.collections['CONSTRUCTION DISPLAY - '+stageName]
  placement = next(obj for obj in display.objects if
    obj.instance_type == 'COLLECTION' and
    obj.instance_collection.name == source['source_collection'])
  placement.instance_collection = group
  stage = bpy.data.scenes['CONSTRUCTION STAGE - '+stageName]
  bpy.context.window.scene = stage
  bpy.data.scenes.remove(probe)
  record['blender_roundtrip_bounds_match'] = True
  results.append(record)
(Root/'reviews/construction-verification.json').write_text(json.dumps({
  'result':'PASS','models':results,'source_checks':sourceChecks},indent=2)+'\n')
for stageName,filename in [('Foundation','construction-foundations-glb'),
  ('Walls','construction-walls-glb')]:
  stage = bpy.data.scenes['CONSTRUCTION STAGE - '+stageName]
  bpy.context.window.scene = stage
  stage.render.filepath = str(Root/'renders'/(filename+'.png'))
  if os.environ.get('POLYWORLD_BUILDINGS_SKIP_RENDER') != '1':
    bpy.ops.render.render(write_still=True)
print('PASS: 16 construction GLBs, source structure, open interiors and origins.',flush=True)
