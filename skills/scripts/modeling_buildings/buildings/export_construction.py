import hashlib
import json
from pathlib import Path

import bpy

Root = Path(__file__).resolve().parent
exportSource = (Root/'export_glbs.py').read_text().split('sourcePath = Path')[0]
exec(compile(exportSource,str(Root/'export_glbs.py'),'exec'),globals())
Output = Root/'exports'/'construction'
structure = json.loads((Root/'reviews/construction-structure.json').read_text())
originals = json.loads((Root/'reviews/glb-export.json').read_text())
origins = {item['name']:item['blender_origin_offset'] for item in originals['models']}
sourcePath = Path(bpy.data.filepath)
sourceHash = hashlib.sha256(sourcePath.read_bytes()).hexdigest()
records,evidence = [],[]
for item in structure['variants']:
  building,stage = item['building'],item['stage']
  slug = building+'_'+stage
  record,details = exportAsset(slug,item['collection'],origin=origins[building],
    subdirectory='construction/'+stage,
    cleanFence=building == 'farm' and stage == 'walls')
  record.update(building=building,stage=stage,
    completed_model='models/'+building+'.glb')
  low,high = details['blender_bounds']
  record['placement_offset_after_polyworld_centering'] = [
    (low[0]+high[0])/2,low[2],-(low[1]+high[1])/2]
  records.append(record)
  evidence.append(details)
manifest = {
  'pack':'lvd_buildings_construction','format':'glTF 2.0 binary',
  'model_count':16,'stage_counts':{'foundation':8,'walls':8},
  'coordinates':'Y up, front +Z, meters; each origin matches its completed GLB',
  'loading':'Preserve authored scale and origin. Polyworld loadPropPack currently recenters each asset: use unitHeight=false, then apply placement_offset_after_polyworld_centering in local X/Y/Z before placement rotation and scale.',
  'textures':'One shared external PNG referenced by relative URI from every GLB',
  'texture_source':'textures/buildings-atlas.png',
  'texture_size':[512,512],
  'farm_stages':'Bare soil bed, then empty fenced bed; no plants.',
  'models':records,
}
(Output/'construction-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
assert hashlib.sha256(sourcePath.read_bytes()).hexdigest() == sourceHash
(Root/'reviews/construction-export.json').write_text(json.dumps({
  'source_blend':str(sourcePath),'source_sha256':sourceHash,
  'source_unchanged':True,'models':evidence},indent=2)+'\n')
print('Exported 16 construction GLBs with completed-model origins.',flush=True)
