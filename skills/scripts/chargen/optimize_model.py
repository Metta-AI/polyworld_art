"""Re-export reduced game meshes from the unchanged editable Blender model."""

import json
import os
import subprocess
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

from paths import Preview, Scripts, Source
from optimizations import exportScene

bpy.ops.wm.open_mainfile(filepath=str(Source / 'character.blend'))
report = json.loads((Source / 'model.json').read_text())
rig = bpy.data.objects['CharacterRig']
bpy.ops.object.select_all(action='DESELECT')
for name in [entry['name'] for entry in report['meshes']] + [rig.name]:
  item = bpy.data.objects[name]
  item.hide_set(False)
  item.select_set(True)
bpy.context.view_layer.objects.active = rig
rig.animation_data.action = bpy.data.actions['A_TPose']
rig.animation_data.action_slot = rig.animation_data.action.slots[0]
bpy.context.scene.frame_set(0)
Preview.mkdir(parents=True, exist_ok=True)
exportScene(
  filepath=str(Preview / 'character.glb'), export_format='GLB',
  use_selection=True, export_animations=True, export_animation_mode='ACTIONS',
  export_frame_range=False, export_force_sampling=True, export_skins=True,
  export_materials='EXPORT', export_yup=True)
subprocess.run([os.environ.get('CHARGEN_PYTHON', 'python3'),
                str(Scripts / 'export_library.py')], check=True)
