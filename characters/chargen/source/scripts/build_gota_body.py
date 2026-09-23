"""Add a split reusable body so trousers can hide covered skin during motion."""
import json
import sys
from pathlib import Path
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import Library, Source, Preview
from clothes import bodySurface, clip, meshObject
import glbs


def main():
  """Preserve the existing body shape and reuse optimized hands and feet."""
  bpy.ops.wm.open_mainfile(filepath=str(Source/'character.blend'))
  body, rig = bpy.data.objects['Body'], bpy.data.objects['CharacterRig']
  rig.animation_data.action = None
  rig.data.pose_position = 'REST'
  source = bodySurface([body])
  objects = []
  for name, section in [('GotaSkinUpper', clip(source, lambda p: p.z-1.255)),
                         ('GotaSkinLower', clip(source, lambda p: 1.255-p.z))]:
    obj = meshObject(body.users_collection[0], name,
      [(section, 0)], list(body.data.materials), preserveNormals=True)
    obj.parent = rig
    obj.modifiers.new('Shared humanoid rig','ARMATURE').object = rig
    objects.append(obj)
  bpy.ops.object.select_all(action='DESELECT')
  for obj in objects+[rig]:
    obj.hide_set(False)
    obj.select_set(True)
  bpy.context.view_layer.objects.active = rig
  path = Library/'body/gota_skin.glb'
  bpy.ops.export_scene.gltf(filepath=str(path), export_format='GLB',
    use_selection=True, export_animations=False, export_skins=True,
    export_materials='EXPORT', export_yup=True)
  nodes = [obj.name for obj in objects]
  files = ['body/gota_skin.glb']
  for name in ['hand_left', 'hand_right', 'foot_left', 'foot_right']:
    doc, binary = glbs.read(Library/('body/'+name+'.glb'))
    for node in doc['nodes']:
      if 'mesh' in node:
        node['name'] = 'Gota'+node['name']
        nodes.append(node['name'])
    file = 'body/gota_'+name+'.glb'
    glbs.write(Library/file, doc, binary)
    files.append(file)
  metadata = dict(id='body/gota_base', name='Gota base', nodes=nodes,
    files=files, alignment='both', skinNodes=nodes, hairShades=[],hatShades=[])
  (Library/'body/gota_base.json').write_text(json.dumps(metadata,indent=2)+'\n')
  print('Gota split body built with original runtime hands and feet.')


main()
