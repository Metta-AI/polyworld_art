"""Present isolated hero authoring files with only their selected outfit visible."""
import json
import sys
from pathlib import Path
import bpy
sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import Source, Library
from clothes import bodySurface, clip, meshObject


def finalize(slug):
  """Set preset visibility and skin colors without modifying shared sources."""
  folder = Source/'gota'/slug
  preset = json.loads((folder/'preset.json').read_text())
  report = json.loads((folder/'verification.json').read_text())
  bpy.ops.wm.open_mainfile(filepath=str(folder/'hero.blend'))
  rig, body = bpy.data.objects['CharacterRig'], bpy.data.objects['Body']
  if 'GotaSkinUpper' in report['nodes'] and not bpy.data.objects.get('GotaSkinUpper'):
    surface = clip(bodySurface([body]), lambda p:p.z-1.255)
    obj = meshObject(body.users_collection[0], 'GotaSkinUpper',
      [(surface,0)], list(body.data.materials), preserveNormals=True)
    obj.parent=rig
    obj.modifiers.new('Shared humanoid rig','ARMATURE').object=rig
  for old in ['Hand.Left','Hand.Right','Foot.Left','Foot.Right']:
    name='Gota'+old
    if name in report['nodes'] and not bpy.data.objects.get(name):
      obj=bpy.data.objects[old].copy()
      obj.data=obj.data.copy()
      obj.name=name
      body.users_collection[0].objects.link(obj)
  manifest=json.loads((Library/'manifest.json').read_text())
  palettes=json.loads((Library/manifest['skinPalette']).read_text())
  rgb=preset.get('skinRgb', palettes[preset['skin']]['color'][:3]
                  if preset['skin']<len(palettes) else [0.9,0.9,0.9])
  for obj in bpy.data.objects:
    if obj.type=='MESH':
      visible=obj.name in report['nodes']
      obj.hide_set(not visible)
      obj.hide_render=not visible
      if visible and (obj.name.startswith(('GotaSkin','GotaHand','GotaFoot','Nose','Ears')) or obj.name=='Head'):
        for i,mat in enumerate(obj.data.materials):
          copied=mat.copy()
          copied.diffuse_color=(*rgb,1)
          if copied.use_nodes:
            shader=copied.node_tree.nodes.get('Principled BSDF')
            if shader: shader.inputs['Base Color'].default_value=(*rgb,1)
          obj.data.materials[i]=copied
  rig.data.pose_position='POSE'
  pose=bpy.data.actions.get('A_TPose')
  if pose:
    rig.animation_data.action=pose
    if pose.slots:rig.animation_data.action_slot=pose.slots[0]
  bpy.context.scene.frame_set(0)
  bpy.context.preferences.filepaths.save_version=0
  bpy.ops.wm.save_as_mainfile(filepath=str(folder/'hero.blend'))
  print('Finalized',slug)


if __name__=='__main__':
  for slug in sys.argv[sys.argv.index('--')+1:]:finalize(slug)
