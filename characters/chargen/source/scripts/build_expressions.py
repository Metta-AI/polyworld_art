"""Add shared facial expressions without rebuilding other character parts."""

import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

import glbs
from expressions import buildExpressions, expressionParts
from paths import Library, Preview, Source

bpy.ops.wm.open_mainfile(filepath=str(Source / 'character.blend'))
rig = bpy.data.objects['CharacterRig']
head = bpy.data.objects['Head']
items = buildExpressions(head.users_collection[0], head)
for item in items:
  item.parent = rig
  item.modifiers.new('Shared humanoid rig', 'ARMATURE').object = rig
savedAction = rig.animation_data.action
savedSlot = rig.animation_data.action_slot
savedPose = rig.data.pose_position
rig.animation_data.action = None
rig.data.pose_position = 'REST'
bpy.ops.object.select_all(action='DESELECT')
for item in items + [rig]:
  item.hide_set(False)
  item.select_set(True)
bpy.context.view_layer.objects.active = rig
output = Preview / 'expressions'
output.mkdir(parents=True, exist_ok=True)
bpy.ops.export_scene.gltf(
  filepath=str(output / 'parts.glb'), export_format='GLB',
  use_selection=True, export_animations=False, export_skins=True,
  export_materials='EXPORT', export_yup=True)
document, binary = glbs.read(output / 'parts.glb')
manifest = json.loads((Source / 'manifest.json').read_text())
for category, part in expressionParts():
  data, blob = glbs.subset(document, binary, meshes=part['nodes'])
  data['images'] = [{'uri': Path(part['texture']).name}]
  for material in data['materials']:
    material['alphaMode'], material['alphaCutoff'] = 'MASK', .5
    material['pbrMetallicRoughness'] = dict(
      baseColorFactor=[1, 1, 1, 1], baseColorTexture={'index': 0},
      metallicFactor=0, roughnessFactor=1)
    material.pop('emissiveTexture', None)
    material.pop('emissiveFactor', None)
    material.setdefault('extensions', {})['KHR_materials_unlit'] = {}
  data['extensionsUsed'] = list(dict.fromkeys(
    data.get('extensionsUsed', []) + ['KHR_materials_unlit']))
  data, blob = glbs.subset(data, blob, meshes=part['nodes'])
  filename = part['id'] + '.glb'
  glbs.write(Library / filename, data, blob)
  metadata = dict(part, files=[filename], skinNodes=[], hairShades=[])
  (Library / (part['id'] + '.json')).write_text(
    json.dumps(metadata, indent=2) + '\n')
  current = next(entry for entry in manifest['categories']
                 if entry['key'] == category)
  current['items'] = [entry for entry in current['items']
                       if entry['nodes'] != part['nodes']] + [part]
(Source / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
report = json.loads((Source / 'model.json').read_text())
names = {item.name for item in items}
report['meshes'] = [entry for entry in report['meshes']
                     if entry['name'] not in names]
report['meshes'] += [dict(name=item.name, vertices=len(item.data.vertices),
                        polygons=len(item.data.polygons)) for item in items]
(Source / 'model.json').write_text(json.dumps(report, indent=2) + '\n')
rig.animation_data.action = savedAction
if savedAction is not None:
  rig.animation_data.action_slot = savedSlot
rig.data.pose_position = savedPose
for item in items:
  item.hide_set(True)
  item.hide_render = True
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(Source / 'character.blend'))
print('Added shared Dead X eyes with independent unlit texture.')
