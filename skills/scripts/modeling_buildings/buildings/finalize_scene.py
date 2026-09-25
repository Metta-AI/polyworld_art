import os
from pathlib import Path

import bpy

Root = Path(__file__).resolve().parent

for image in bpy.data.images:
  if 'buildings-atlas' in image.name:
    image.unpack(method='REMOVE')
    image.filepath = str(Root/'assets'/'buildings-atlas.png')
    image.reload()
    image.pack()
    image.filepath = '//assets/buildings-atlas.png'
stage = bpy.data.scenes['00 - Building Review Stage']
bpy.context.window.scene = stage
stage.render.filepath = str(Root/'renders'/'buildings-stage.png')
stage.render.resolution_x = stage.render.resolution_y = 2560
stage.cycles.samples = 64
bpy.ops.wm.save_as_mainfile(filepath=str(Root/'polyworld-buildings.blend'))
if os.environ.get('POLYWORLD_BUILDINGS_SKIP_RENDER') != '1':
  bpy.ops.render.render(write_still=True)
