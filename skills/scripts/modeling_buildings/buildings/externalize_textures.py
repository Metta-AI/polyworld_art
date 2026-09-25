import copy
import hashlib
import os
import struct
import json
from pathlib import Path

def readGlb(raw):
  """Read a standard two-chunk GLB container."""
  magic,version,length = struct.unpack_from('<4sII',raw)
  assert magic == b'glTF' and version == 2 and length == len(raw)
  size,kind = struct.unpack_from('<I4s',raw,12)
  assert kind == b'JSON'
  document = json.loads(raw[20:20+size])
  offset = 20+size
  binarySize,binaryKind = struct.unpack_from('<I4s',raw,offset)
  assert binaryKind == b'BIN\x00' and offset+8+binarySize == len(raw)
  return document,raw[offset+8:]

def writeExternalGlb(path,atlasPath):
  """Strip the embedded atlas while preserving every geometry buffer byte."""
  path,atlasPath = Path(path),Path(atlasPath)
  raw = path.read_bytes()
  document,binary = readGlb(raw)
  assert len(document['images']) == len(document['buffers']) == 1
  original = copy.deepcopy(document)
  image = document['images'][0]
  uri = Path(os.path.relpath(atlasPath,path.parent)).as_posix()
  assert atlasPath.is_file()
  if 'bufferView' not in image:
    assert (path.parent/image['uri']).resolve() == atlasPath.resolve()
    return {'bytes_before':len(raw),'bytes_after':len(raw),
      'image_uri':image['uri'],'geometry_buffers_unchanged':True}
  removed = image.pop('bufferView')
  image['uri'] = uri
  image.pop('mimeType',None)
  views,remap,payloads = [],{},{}
  newBinary = bytearray()
  for index,view in enumerate(document['bufferViews']):
    if index == removed:
      continue
    offset = view.get('byteOffset',0)
    payload = binary[offset:offset+view['byteLength']]
    assert len(payload) == view['byteLength']
    newBinary.extend(b'\x00'*(-len(newBinary)%4))
    newView = dict(view,byteOffset=len(newBinary))
    remap[index] = len(views)
    payloads[len(views)] = payload
    views.append(newView)
    newBinary.extend(payload)
  def remapViews(value):
    """Update accessor and extension references if an image view was removed."""
    if isinstance(value,dict):
      for key,item in value.items():
        if key == 'bufferView':
          assert item in remap
          value[key] = remap[item]
        else:
          remapViews(item)
    elif isinstance(value,list):
      for item in value:
        remapViews(item)
  document['bufferViews'] = views
  remapViews(document)
  document['buffers'][0]['byteLength'] = len(newBinary)
  newBinary.extend(b'\x00'*(-len(newBinary)%4))
  encoded = json.dumps(document,separators=(',',':'),ensure_ascii=False).encode()
  encoded += b' '*(-len(encoded)%4)
  total = 12+8+len(encoded)+8+len(newBinary)
  updated = struct.pack('<4sII',b'glTF',2,total)
  updated += struct.pack('<I4s',len(encoded),b'JSON')+encoded
  updated += struct.pack('<I4s',len(newBinary),b'BIN\x00')+newBinary
  after,afterBinary = readGlb(updated)
  for key in ('meshes','nodes','scenes','materials','textures','samplers'):
    assert original.get(key) == after.get(key),key
  for index,view in enumerate(after['bufferViews']):
    start = view['byteOffset']
    assert afterBinary[start:start+view['byteLength']] == payloads[index]
  assert 'bufferView' not in after['images'][0]
  assert (path.parent/after['images'][0]['uri']).resolve() == atlasPath.resolve()
  temporary = path.with_suffix('.glb.new')
  temporary.write_bytes(updated)
  temporary.replace(path)
  return {'bytes_before':len(raw),'bytes_after':len(updated),
    'image_uri':uri,'geometry_buffers_unchanged':True}

def externalizePack(pack,manifestName):
  """Point each GLB in one manifest at the pack's single shared PNG."""
  pack = Path(pack)
  path = pack/manifestName
  manifest = json.loads(path.read_text())
  atlas = pack/'textures/buildings-atlas.png'
  assert struct.unpack_from('>II',atlas.read_bytes(),16) == (512,512)
  records = []
  for model in manifest['models']:
    file = pack/model['file']
    assert hashlib.sha256(file.read_bytes()).hexdigest() == model['sha256']
    record = writeExternalGlb(file,atlas)
    record['name'] = model['name']
    records.append(record)
    model['sha256'] = hashlib.sha256(file.read_bytes()).hexdigest()
  manifest['textures'] = 'One shared external PNG referenced by relative URI from every GLB'
  manifest['texture_size'] = [512,512]
  manifest['texture_source'] = 'textures/buildings-atlas.png'
  path.write_text(json.dumps(manifest,indent=2)+'\n')
  return records

if __name__ == '__main__':
  import shutil
  root = Path(__file__).resolve().parent
  pack = Path(os.environ['POLYWORLD_BUILDING_PACK'])
  backup = root/'versions/before-shared-atlas'
  assert not backup.exists()
  shutil.copytree(pack,backup)
  records = []
  for name,folder in [('manifest.json','lvd_buildings'),
    ('construction-manifest.json','construction')]:
    records.extend(externalizePack(pack,name))
    manifest = json.loads((pack/name).read_text())
    staging = root/'exports'/folder
    for model in manifest['models']:
      shutil.copy2(pack/model['file'],staging/model['file'])
    shutil.copy2(pack/name,staging/name)
    shutil.copy2(pack/'textures/buildings-atlas.png',staging/'textures/buildings-atlas.png')
  report = {'result':'PASS','model_count':len(records),
    'shared_texture':str(pack/'textures/buildings-atlas.png'),
    'embedded_texture_count':0,
    'total_glb_bytes':sum(item['bytes_after'] for item in records),
    'models':records}
  (root/'reviews/shared-atlas.json').write_text(json.dumps(report,indent=2)+'\n')
  print(json.dumps({key:value for key,value in report.items() if key != 'models'},indent=2))
