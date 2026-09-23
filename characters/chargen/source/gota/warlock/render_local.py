"""Render the actual Warlock meshes for quick construction review."""
import bpy, json, math
from mathutils import Vector
from pathlib import Path
out=Path('/Users/me/p/polyworld_art/characters/chargen/source/gota/warlock')
bpy.ops.wm.open_mainfile(filepath=str(out/'hero.blend'))
report=json.loads((out/'verification.json').read_text())
for ob in bpy.data.objects:
 ob.hide_render=ob.name not in report['nodes']
 ob.hide_set(ob.hide_render)
rig=bpy.data.objects['CharacterRig']
rig.hide_set(False)
rig.hide_render=False
rig.data.pose_position='REST'
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=12
scene.cycles.use_denoising=True
scene.render.resolution_x=720
scene.render.resolution_y=900
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='Standard'
scene.world.color=(.8,.8,.8)
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.72,.72,.72,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
for name,direction,power in [('WarlockKey',(-3,-4,7),2),('WarlockFill',(4,-3,3),.6)]:
 light=bpy.data.lights.new(name,'SUN'); light.energy=power; light.angle=.4
 ob=bpy.data.objects.new(name,light); scene.collection.objects.link(ob)
 ob.rotation_euler=(-Vector(direction)).to_track_quat('-Z','Y').to_euler()
for name in ['Body','Head','Nose_Tiny','Ears_Round_Left','Ears_Round_Right']:
 ob=bpy.data.objects[name]
 for idx,mat in enumerate(ob.data.materials):
  mat=mat.copy(); ob.data.materials[idx]=mat
  shader=mat.node_tree.nodes.get('Principled BSDF')
  if shader: shader.inputs['Base Color'].default_value=(.67,.655,.69,1)
for mat in bpy.data.materials:
 if mat.use_nodes:
  shader=mat.node_tree.nodes.get('Principled BSDF')
  if shader and not shader.inputs['Base Color'].is_linked:
   col=shader.inputs['Base Color'].default_value
   shader.inputs['Base Color'].default_value=tuple(c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in col[:3])+(1,)
camera=bpy.data.objects.new('WarlockCamera',bpy.data.cameras.new('WarlockCamera'))
scene.collection.objects.link(camera); scene.camera=camera; camera.data.type='ORTHO'; camera.data.ortho_scale=3.9
for label,y in [('front',-12),('back',12)]:
 camera.location=(0,y,1.8); camera.rotation_euler=(Vector((0,0,1.8))-camera.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=str(out/('local_'+label+'.png')); bpy.ops.render.render(write_still=True)
