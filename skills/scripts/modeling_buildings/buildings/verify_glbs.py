import os
import json
import math
import struct
from pathlib import Path

import bpy
from mathutils import Vector

Root = Path(__file__).resolve().parent
Pack = Root/'exports'/'lvd_buildings'
manifest = json.loads((Pack/'manifest.json').read_text())
evidence = json.loads((Root/'reviews'/'glb-export.json').read_text())
sources = {item['name']:item for item in evidence['models']}

def readGlb(path):
  """Read the GLB container and confirm its embedded payload lengths."""
  raw = path.read_bytes()
  magic, version, length = struct.unpack_from('<4sII',raw)
  assert magic == b'glTF' and version == 2 and length == len(raw)
  offset, document, binary = 12, None, None
  while offset < length:
    size, kind = struct.unpack_from('<I4s',raw,offset)
    payload = raw[offset+8:offset+8+size]
    assert len(payload) == size
    if kind == b'JSON':
      document = json.loads(payload)
    elif kind == b'BIN\x00':
      binary = payload
    offset += size+8
  assert document is not None and binary is not None
  assert offset == length
  return document,binary

def accessor(document,binary,index):
  """Decode uncompressed glTF attributes with explicit strides."""
  data = document['accessors'][index]
  view = document['bufferViews'][data['bufferView']]
  kinds = {5121:'B',5123:'H',5125:'I',5126:'f'}
  widths = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}
  format = '<'+kinds[data['componentType']]*widths[data['type']]
  size = struct.calcsize(format)
  stride = view.get('byteStride',size)
  start = view.get('byteOffset',0)+data.get('byteOffset',0)
  end = start+(data['count']-1)*stride+size
  assert end <= len(binary)
  return [struct.unpack_from(format,binary,start+i*stride)
    for i in range(data['count'])]

def validateContainer(model):
  """Check a complete prop with an external atlas and valid triangles."""
  document,binary = readGlb(Pack/model['file'])
  assert len(document['scenes']) == 1
  assert document['scenes'][0]['nodes'] == [0]
  assert len(document['meshes']) == len(document['nodes']) == 1
  assert document['nodes'][0]['name'] == model['name']
  assert not document.get('cameras') and not document.get('animations')
  assert 'KHR_lights_punctual' not in document.get('extensions',{})
  assert all('uri' not in buffer for buffer in document['buffers'])
  assert len(document['images']) == 1
  for image in document['images']:
    assert 'uri' in image and 'bufferView' not in image
    texture = (Pack/model['file']).parent/image['uri']
    assert texture.resolve() == (Pack/'textures/buildings-atlas.png').resolve()
    assert struct.unpack_from('>II',texture.read_bytes(),16) == (512,512)
  triangles,positions = 0,[]
  for primitive in document['meshes'][0]['primitives']:
    assert primitive.get('mode',4) == 4
    attributes = primitive['attributes']
    points = accessor(document,binary,attributes['POSITION'])
    assert all(math.isfinite(value) for point in points for value in point)
    indices = accessor(document,binary,primitive['indices'])
    assert len(indices)%3 == 0
    assert all(0 <= index[0] < len(points) for index in indices)
    triangles += len(indices)//3
    positions.extend(points)
    material = document['materials'][primitive['material']]
    if 'baseColorTexture' in material.get('pbrMetallicRoughness',{}):
      assert 'TEXCOORD_0' in attributes
      assert len(accessor(document,binary,attributes['TEXCOORD_0'])) == len(points)
  assert triangles == model['triangles']
  low = [min(point[i] for point in positions) for i in range(3)]
  high = [max(point[i] for point in positions) for i in range(3)]
  assert abs(low[1]) < .0001
  assert abs(low[0]+high[0]) < .0001
  assert abs(low[2]+high[2]) < .0001
  assert all(abs(high[i]-low[i]-model['dimensions'][i]) < .0001
    for i in range(3))
  return {'name':model['name'],'triangles':triangles,
    'embedded_images':0,'external_dependencies':1,'shared_atlas':True}

stage = bpy.data.scenes['00 - Building Review Stage']
placements = {obj.instance_collection.name:obj
  for obj in bpy.data.collections['STAGE - Nine linked assets'].objects
  if obj.instance_type == 'COLLECTION'}
results = []
for model in manifest['models']:
  record = validateContainer(model)
  source = sources[model['name']]
  probe = bpy.data.scenes.new('VERIFY - '+model['name'])
  bpy.context.window.scene = probe
  bpy.ops.import_scene.gltf(filepath=str(Pack/model['file']))
  bpy.context.view_layer.update()
  objects = list(probe.objects)
  meshes = [obj for obj in objects if obj.type == 'MESH']
  assert len(meshes) == 1
  points = [obj.matrix_world @ vertex.co for obj in meshes
    for vertex in obj.data.vertices]
  low = [min(point[i] for point in points) for i in range(3)]
  high = [max(point[i] for point in points) for i in range(3)]
  expectedLow,expectedHigh = source['blender_bounds']
  assert all(abs(low[i]-expectedLow[i]) < .0001
    and abs(high[i]-expectedHigh[i]) < .0001 for i in range(3))
  restored = bpy.data.collections.new('GLB - '+model['name'])
  for obj in objects:
    restored.objects.link(obj)
  restored.instance_offset = -Vector(source['blender_origin_offset'])
  placements[source['source_collection']].instance_collection = restored
  record['blender_roundtrip_bounds_match'] = True
  results.append(record)
  bpy.context.window.scene = stage
  bpy.data.scenes.remove(probe)
(Root/'reviews'/'glb-verification.json').write_text(json.dumps({
  'result':'PASS','models':results},indent=2)+'\n')
stage.render.resolution_x = stage.render.resolution_y = 2400
stage.cycles.samples = 32
stage.render.filepath = str(Root/'renders'/'glb-roundtrip.png')
if os.environ.get('POLYWORLD_BUILDINGS_SKIP_RENDER') != '1':
  bpy.ops.render.render(write_still=True)
print('All nine GLBs passed binary and Blender round-trip checks.',flush=True)
