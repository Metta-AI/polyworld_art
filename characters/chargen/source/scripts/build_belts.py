"""Detach waist belts from older tunics without regenerating other geometry."""

import json
import runpy
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

from clothes import clothingParts, separateBelts
from paths import Library, Scripts, Source

bpy.ops.wm.open_mainfile(filepath=str(Source / 'character.blend'))
collection = bpy.data.objects['Body'].users_collection[0]
belt = separateBelts(collection)
parts = dict((part['nodes'][0], (category, part))
             for category, part in clothingParts()
             if part['nodes'][0] in ['Clothing_03', 'Clothing_05', 'Belt_Simple'])
manifest = json.loads((Source / 'manifest.json').read_text())
for category in manifest['categories']:
  for part in category['items']:
    if part['nodes'] in [['Clothing_03'], ['Clothing_05']]:
      replacement = parts[part['nodes'][0]][1]
      part['name'], part['id'] = replacement['name'], replacement['id']
  if category['key'] == 'Belt':
    category['items'] = [part for part in category['items']
                         if part['nodes'] != ['Belt_Simple']]
    category['items'].append(parts['Belt_Simple'][1])
(Source / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
report = json.loads((Source / 'model.json').read_text())
report['meshes'] = [entry for entry in report['meshes'] if entry['name'] not in parts]
report['meshes'] += [dict(name=name, vertices=len(bpy.data.objects[name].data.vertices),
                         polygons=len(bpy.data.objects[name].data.polygons))
                      for name in parts]
(Source / 'model.json').write_text(json.dumps(report, indent=2) + '\n')
# Preserve saved outfit choices when the now-unbelted tops change display names.
for path in [Source / 'manifest.json', Library / 'manifest.json']:
  value = json.loads(path.read_text())
  renames = {'03 Belted green tabard': '03 Green tabard',
             '05 Belted ochre tunic': '05 Ochre tunic'}
  for preset in value.get('presets', []):
    for part in preset.get('parts', []):
      if part['category'] == 'Chest':
        part['item'] = renames.get(part['item'], part['item'])
  for category in value['categories']:
    if category['key'] == 'Chest' and 'defaultItem' in category:
      category['defaultItem'] = renames.get(category['defaultItem'], category['defaultItem'])
  path.write_text(json.dumps(value, indent=2) + '\n')
belt.hide_set(True)
belt.hide_render = True
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(Source / 'character.blend'))
runpy.run_path(str(Scripts / 'optimize_model.py'), run_name='__main__')
print('Detached simple leather belt; shirts and trousers remain independent.')
