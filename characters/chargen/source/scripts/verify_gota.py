"""Audit the final runtime library rather than relying on authoring counts."""
import hashlib
import json
import math
import struct
from pathlib import Path
from paths import Library, Source
from register_gota import Order
import glbs

Sizes={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
Formats={5120:'b',5121:'B',5122:'h',5123:'H',5125:'I',5126:'f'}


def values(doc,blob,index):
  """Decode a strided glTF accessor for independent finite/weight checks."""
  a=doc['accessors'][index]
  v=doc['bufferViews'][a['bufferView']]
  fmt='<'+Formats[a['componentType']]*Sizes[a['type']]
  size=struct.calcsize(fmt)
  start=v.get('byteOffset',0)+a.get('byteOffset',0)
  return [struct.unpack_from(fmt,blob,start+i*v.get('byteStride',size))
          for i in range(a['count'])]


def audit(path,clothing=False):
  """Check actual triangle lists, rig joints, finite coordinates and weights."""
  doc,blob=glbs.read(path)
  if clothing: assert not doc.get('textures') and not doc.get('images'),path
  rig,_=glbs.read(Library/'rig/humanoid.glb')
  canonical={n['name']:n for n in rig['nodes'] if 'mesh' not in n}
  result={}
  for skin in doc.get('skins',[]):
    for index in skin['joints']:
      joint=doc['nodes'][index]
      assert joint['name'] in canonical,(path,joint['name'])
      base=canonical[joint['name']]
      for key,default in [('translation',[0,0,0]),('rotation',[0,0,0,1]),('scale',[1,1,1])]:
        assert all(abs(a-b)<1e-5 for a,b in zip(joint.get(key,default),base.get(key,default))), (path,joint['name'],key)
    if 'inverseBindMatrices' in skin:
      assert all(math.isfinite(x) for row in values(doc,blob,skin['inverseBindMatrices']) for x in row)
  for node in doc['nodes']:
    if 'mesh' not in node:continue
    total=0
    assert 'skin' in node,(path,node['name'])
    joints=len(doc['skins'][node['skin']]['joints'])
    for primitive in doc['meshes'][node['mesh']]['primitives']:
      a=primitive['attributes']
      positions=values(doc,blob,a['POSITION'])
      assert all(math.isfinite(x) for row in positions for x in row),path
      weights=values(doc,blob,a['WEIGHTS_0'])
      assert all(abs(sum(row)-1)<1e-4 and min(row)>=0 for row in weights),path
      indices=values(doc,blob,a['JOINTS_0'])
      assert all(0<=x<joints for row in indices for x in row),path
      assert primitive.get('mode',4)==4,path
      count=doc['accessors'][primitive.get('indices',a['POSITION'])]['count']
      assert count%3==0
      if 'indices' in primitive:
        assert all(0<=row[0]<len(positions) for row in values(doc,blob,primitive['indices'])),path
      total+=count//3
    result[node['name']]=total
  return result


def main():
  """Audit every selected character, separate slot and referenced artifact."""
  manifest=json.loads((Library/'manifest.json').read_text())
  inventory={}
  for c in manifest['categories']:
    for path in (Library/c['directory']).glob('*.json'):
      item=json.loads(path.read_text())
      inventory[(c['key'],item['name'])]=item
  presets=[p for p in manifest['presets']
    if p.get('group')=='Gota' and not p.get('lineupHidden',False)]
  assert len(presets)==10
  audits,cache=[],{}
  required={'Foot','Leg','Belt','Chest','Headgear'}
  for slug,preset in zip(Order,presets):
    folder=Source/'gota'/slug
    selections={p['category']:p['item'] for p in preset['parts']}
    assert selections['Body']=='Gota base'
    chosen=[(c,inventory[(c,n)]) for c,n in selections.items() if n not in ('','None')]
    visible=set(manifest.get('base',[]))
    hidden=set()
    counts={}
    files={}
    for category,item in chosen:
      visible.update(item['nodes'])
      hidden.update(item.get('hides',[]))
      for file in item['files']:
        if file not in cache:
          cache[file]=audit(Library/file,
            category in required or item.get('attachmentBone'))
        counts.update(cache[file])
        files[file]=hashlib.sha256((Library/file).read_bytes()).hexdigest()
    visible-=hidden
    assert visible<=counts.keys()
    total=sum(counts[n] for n in visible)
    equipment={n for _,item in chosen if item.get('attachmentBone')
      for n in item['nodes']}
    equipmentTriangles=sum(counts[n] for n in visible & equipment)
    characterTriangles=total-equipmentTriangles
    assert characterTriangles<20000,(slug,characterTriangles)
    assert equipmentTriangles<5000,(slug,equipmentTriangles)
    assert 'GotaSkinLower' not in visible
    for slot in required:
      item=inventory[(slot,selections[slot])]
      assert len(item['files'])==1 and 'gota_'+slug+'_' in item['id'],(slug,slot)
    for name in ['hero.blend','parts.json','preset.json','comparison.png',
                 'items_comparison.png','review.html','verification.json']:
      assert (folder/name).stat().st_size>0,(slug,name)
    for view in ['model','walk','crouch','Foot','Leg','Belt','Chest','Headgear']:
      assert (folder/'renders'/(view+'.png')).stat().st_size>0,(slug,view)
    assert any(folder.glob('*prompt*')),(slug,'prompt')
    references=list(folder.glob('clothing*.png'))
    assert references,(slug,'reference')
    audits.append(dict(name=preset['name'],slug=slug,triangles=total,
      characterTriangles=characterTriangles,equipmentTriangles=equipmentTriangles,
      characterTriangleLimitExclusive=20000,equipmentTriangleLimitExclusive=5000,
      requiredSlots=sorted(required),
      visibleNodes=sorted(visible),files=files,
      finiteGeometry=True,normalizedWeights=True,sharedRig=True,
      untexturedClothing=True))
  (Source/'gota/audit.json').write_text(json.dumps(audits,indent=2)+'\n')
  for hero in audits:print(hero['name']+': '+str(hero['triangles'])+' triangles, verified.')
  return {name for nodes in cache.values() for name in nodes}


if __name__=='__main__':main()
