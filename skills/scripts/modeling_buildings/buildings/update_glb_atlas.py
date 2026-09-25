import os
import hashlib
import json
import shutil
import struct
from pathlib import Path

Root = Path(__file__).resolve().parent
Pack = Path(os.environ['POLYWORLD_BUILDING_PACK'])
Atlas = (Root/'assets/buildings-atlas.png').read_bytes()
assert Atlas[:8] == b'\x89PNG\r\n\x1a\n'
assert struct.unpack_from('>II',Atlas,16) == (512,512)
AtlasHash = hashlib.sha256(Atlas).hexdigest()

def readGlb(raw):
  """Read a standard JSON and binary GLB without interpreting geometry."""
  magic,version,length = struct.unpack_from('<4sII',raw)
  assert magic == b'glTF' and version == 2 and length == len(raw)
  jsonLength,jsonType = struct.unpack_from('<I4s',raw,12)
  assert jsonType == b'JSON'
  document = json.loads(raw[20:20+jsonLength])
  offset = 20+jsonLength
  binaryLength,binaryType = struct.unpack_from('<I4s',raw,offset)
  assert binaryType == b'BIN\x00'
  assert offset+8+binaryLength == len(raw)
  return document,raw[offset+8:]

def replaceAtlas(raw):
  """Replace only the embedded PNG and retain every geometry buffer byte."""
  document,binary = readGlb(raw)
  assert len(document['buffers']) == len(document['images']) == 1
  image = document['images'][0]
  if 'uri' in image:
    # External models already share the PNG replaced at the end of this script.
    assert image['uri'].endswith('textures/buildings-atlas.png')
    return raw
  assert image['mimeType'] == 'image/png' and 'uri' not in image
  imageIndex = image['bufferView']
  payloads = {i:binary[view.get('byteOffset',0):
    view.get('byteOffset',0)+view['byteLength']]
    for i,view in enumerate(document['bufferViews'])}
  output = bytearray()
  previousEnd = 0
  for i in sorted(payloads,key=lambda index:document['bufferViews'][index].get('byteOffset',0)):
    view = document['bufferViews'][i]
    assert view.get('buffer',0) == 0
    assert view.get('byteOffset',0) >= previousEnd
    previousEnd = view.get('byteOffset',0)+view['byteLength']
    output.extend(b'\x00'*(-len(output)%4))
    data = Atlas if i == imageIndex else payloads[i]
    view['byteOffset'] = len(output)
    view['byteLength'] = len(data)
    output.extend(data)
  document['buffers'][0]['byteLength'] = len(output)
  output.extend(b'\x00'*(-len(output)%4))
  jsonBytes = json.dumps(document,separators=(',',':'),ensure_ascii=False).encode()
  jsonBytes += b' '*(-len(jsonBytes)%4)
  total = 12+8+len(jsonBytes)+8+len(output)
  result = struct.pack('<4sII',b'glTF',2,total)
  result += struct.pack('<I4s',len(jsonBytes),b'JSON')+jsonBytes
  result += struct.pack('<I4s',len(output),b'BIN\x00')+output
  after,newBinary = readGlb(result)
  for i,view in enumerate(after['bufferViews']):
    data = newBinary[view['byteOffset']:view['byteOffset']+view['byteLength']]
    assert data == (Atlas if i == imageIndex else payloads[i])
  return result

records = []
bytesBefore,bytesAfter = 0,0
for manifestName,exportName in [('manifest.json','lvd_buildings'),
  ('construction-manifest.json','construction')]:
  sourceManifest = Pack/manifestName
  manifest = json.loads(sourceManifest.read_text())
  staging = Root/'exports'/exportName
  for model in manifest['models']:
    path = Pack/model['file']
    original = path.read_bytes()
    assert hashlib.sha256(original).hexdigest() == model['sha256']
    updated = replaceAtlas(original)
    staged = staging/model['file']
    staged.parent.mkdir(parents=True,exist_ok=True)
    staged.write_bytes(updated)
    model['sha256'] = hashlib.sha256(updated).hexdigest()
    bytesBefore += len(original)
    bytesAfter += len(updated)
    records.append({'name':model['name'],'texture_size':[512,512],
      'geometry_buffers_unchanged':True,'atlas_sha256':AtlasHash,
      'bytes_before':len(original),'bytes_after':len(updated)})
  manifest['texture_size'] = [512,512]
  manifest['texture_source'] = 'textures/buildings-atlas.png'
  (staging/manifestName).write_text(json.dumps(manifest,indent=2)+'\n')
  # Publish complete model files before the manifest that describes them.
  for model in manifest['models']:
    target = Pack/model['file']
    temporary = target.with_suffix('.glb.new')
    shutil.copy2(staging/model['file'],temporary)
    temporary.replace(target)
    assert hashlib.sha256(target.read_bytes()).hexdigest() == model['sha256']
  shutil.copy2(staging/manifestName,sourceManifest)
(Pack/'textures').mkdir(exist_ok=True)
(Pack/'textures/buildings-atlas.png').write_bytes(Atlas)
report = {'result':'PASS','model_count':len(records),'texture_size':[512,512],
  'total_glb_bytes_before':bytesBefore,'total_glb_bytes_after':bytesAfter,
  'models':records}
(Root/'reviews/atlas-512-glbs.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k != 'models'},indent=2))
