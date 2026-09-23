"""Check actual shared walk animation deformation of the Arcanist clothes."""
import json
import math
from pathlib import Path
import bpy

Directory = Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(Directory / 'hero.blend'))
rig = bpy.data.objects['CharacterRig']
rig.data.pose_position = 'POSE'
rig.animation_data.action = bpy.data.actions['Walk_Loop']
rig.animation_data.action_slot = rig.animation_data.action.slots[0]
objects = [obj for obj in bpy.data.objects
           if obj.type == 'MESH' and obj.name.startswith('Gota_arcanist_')]
records = {}
for frame in [0, 10, 20, 30]:
  bpy.context.scene.frame_set(frame)
  bpy.context.view_layer.update()
  graph = bpy.context.evaluated_depsgraph_get()
  for obj in objects:
    evaluated = obj.evaluated_get(graph)
    mesh = evaluated.to_mesh()
    points = [tuple(v.co) for v in mesh.vertices]
    assert all(math.isfinite(c) for point in points for c in point)
    records.setdefault(obj.name, []).append(points)
    evaluated.to_mesh_clear()
report = []
for name, frames in records.items():
  movement = max(math.dist(first, point) for frame in frames[1:]
                 for first, point in zip(frames[0], frame))
  assert movement > .001, (name, movement)
  report.append(dict(node=name, animation='Walk_Loop', frames=[0, 10, 20, 30],
                     finite=True, maxMovement=movement, deforms=True))
(Directory / 'animation_audit.json').write_text(json.dumps(report, indent=2)+'\n')
print('ARcanist animation audit', len(report), 'meshes deform correctly.')
