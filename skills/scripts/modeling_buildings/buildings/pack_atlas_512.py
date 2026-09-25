import hashlib
import json
from pathlib import Path

import bpy

Root = Path(__file__).resolve().parent

def geometryDigest():
  """Hash authored geometry and placements independently of image data."""
  digest = hashlib.sha256()
  for mesh in sorted(bpy.data.meshes,key=lambda item:item.name):
    values = [mesh.name,
      [[round(value,6) for value in vertex.co] for vertex in mesh.vertices],
      [list(face.vertices) for face in mesh.polygons],
      [[[round(value,6) for value in uv.uv] for uv in layer.data]
        for layer in mesh.uv_layers]]
    digest.update(json.dumps(values,separators=(',',':')).encode())
  for obj in sorted(bpy.data.objects,key=lambda item:item.name):
    digest.update(json.dumps([obj.name,obj.type,
      [[round(value,6) for value in row] for row in obj.matrix_basis],
      [(modifier.name,modifier.type) for modifier in obj.modifiers]],
      separators=(',',':')).encode())
  return digest.hexdigest()

records = []
for filename in ['polyworld-buildings.blend','polyworld-construction.blend']:
  path = Root/filename
  bpy.ops.wm.open_mainfile(filepath=str(path))
  before = geometryDigest()
  images = [item for item in bpy.data.images
    if 'buildings-atlas' in item.name or item.filepath.endswith('buildings-atlas.png')]
  assert images
  for item in images:
    if item.packed_file:
      item.unpack(method='REMOVE')
    item.filepath = '//assets/buildings-atlas.png'
    item.reload()
    assert tuple(item.size) == (512,512),(item.name,list(item.size))
    item.pack()
  bpy.ops.wm.save_as_mainfile(filepath=str(path))
  bpy.ops.wm.open_mainfile(filepath=str(path))
  assert geometryDigest() == before,filename
  image = next(item for item in bpy.data.images if 'buildings-atlas' in item.name)
  assert tuple(image.size) == (512,512) and image.packed_file
  records.append({'file':str(path),'texture_size':[512,512],
    'packed':True,'geometry_unchanged':True,
    'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(Root/'reviews/atlas-512-blender.json').write_text(json.dumps({
  'result':'PASS','sources':records},indent=2)+'\n')
print(json.dumps(records,indent=2),flush=True)
