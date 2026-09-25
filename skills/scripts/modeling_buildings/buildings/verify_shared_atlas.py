import os
import json
from pathlib import Path

import bpy

Root = Path(__file__).resolve().parent
Pack = Path(os.environ['POLYWORLD_BUILDING_PACK'])
Atlas = (Pack/'textures/buildings-atlas.png').resolve()
bpy.ops.wm.read_factory_settings(use_empty=True)
records = []
for name in ['manifest.json','construction-manifest.json']:
  manifest = json.loads((Pack/name).read_text())
  for model in manifest['models']:
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(Pack/model['file']))
    added = [obj for obj in bpy.data.objects if obj not in before and obj.type == 'MESH']
    assert len(added) == 1,model['name']
    textures = []
    for slot in added[0].material_slots:
      material = slot.material
      if material and material.use_nodes:
        textures.extend(node.image for node in material.node_tree.nodes
          if node.type == 'TEX_IMAGE' and node.image is not None)
    assert textures,model['name']
    for texture in textures:
      assert tuple(texture.size) == (512,512),model['name']
      assert Path(bpy.path.abspath(texture.filepath)).resolve() == Atlas,texture.filepath
    records.append({'name':model['name'],'loads_shared_png':True,'size':[512,512]})
(Root/'reviews/shared-atlas-blender.json').write_text(json.dumps({
  'result':'PASS','models':records},indent=2)+'\n')
print('PASS: All 25 GLBs import with the same external 512 x 512 PNG.',flush=True)
