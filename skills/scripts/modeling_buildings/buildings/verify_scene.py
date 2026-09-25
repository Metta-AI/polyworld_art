import json
import math
from pathlib import Path

import bpy

Root = Path(__file__).resolve().parent

def checkMirror(group):
  """Verify that a source contains an enabled unapplied mirror."""
  return any(mod.type == 'MIRROR' and mod.show_render
    for obj in group.objects for mod in obj.modifiers)

def check():
  """Validate the saved kit rather than the in-memory build script."""
  stage = bpy.data.scenes['00 - Building Review Stage']
  main = bpy.data.collections['STAGE - Nine linked assets']
  instances = [obj for obj in main.objects
    if obj.instance_type == 'COLLECTION']
  assert len(instances) == 9
  assert len({obj['stage_cell'] for obj in instances}) == 9
  hall = bpy.data.collections['01 Town Hall']
  wings = [obj for obj in hall.objects
    if obj.instance_type == 'COLLECTION']
  assert len(wings) == 3
  assert len({obj.instance_collection.name for obj in wings}) == 1
  assert checkMirror(hall)
  assert all(checkMirror(obj.instance_collection) for obj in wings)
  sideWings = [obj for obj in wings if 'left' in obj.name or 'right' in obj.name]
  assert sorted(round(math.degrees(obj.rotation_euler.z))
    for obj in sideWings) == [-90, 90]
  assert checkMirror(bpy.data.collections['03 Barracks'])
  assert checkMirror(bpy.data.collections['04 Lumber Mill'])
  farm = bpy.data.collections['02 Farm']
  fences = [obj for obj in farm.objects if obj.name.startswith('Farm fence ')]
  assert len(fences) == 4
  assert len({obj.instance_collection.name for obj in fences}) == 1
  assert checkMirror(fences[0].instance_collection)
  angles = sorted(round(math.degrees(obj.rotation_euler.z)) % 360 for obj in fences)
  assert angles == [0, 90, 180, 270], angles
  pumpkins = [obj for obj in farm.objects if obj.name.startswith('Pumpkin row ')]
  assert len(pumpkins) == 16
  assert len({obj.instance_collection.name for obj in pumpkins}) == 1
  assert len({obj['row'] for obj in pumpkins}) == 4
  assert len({obj['column'] for obj in pumpkins}) == 4
  assert len({round(obj.scale.x, 3) for obj in pumpkins}) > 8
  tower = bpy.data.collections['05 Tower']
  arrays = [mod for obj in tower.objects for mod in obj.modifiers
    if mod.type == 'ARRAY']
  assert len(arrays) >= 8
  assert all(mod.count == 6 and mod.use_object_offset for mod in arrays)
  assert all(abs(math.degrees(mod.offset_object.rotation_euler.z)-60) < .01
    for mod in arrays)
  assert not any('crystal' in obj.name.lower() for obj in bpy.data.objects)
  mine = bpy.data.collections['09 Gold Mine']
  assert checkMirror(mine)
  assert all(obj.get('atlas_region') in {'wood', 'solid material'}
    for obj in mine.objects if obj.type == 'MESH')
  carts = [obj for obj in mine.objects if obj.instance_type == 'COLLECTION']
  assert len(carts) == 1 and carts[0].instance_collection.name == 'MODULE - Mine cart'
  gold = [obj for obj in carts[0].instance_collection.objects
    if obj.get('atlas_region') == 'gold']
  assert len(gold) == 7
  assert all(obj.name.startswith('Cart raw gold') for obj in bpy.data.objects
    if obj.get('atlas_region') == 'gold')
  assert not any('Mine gray' in obj.name or 'Mine scattered' in obj.name
    for obj in bpy.data.objects)
  meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']
  assert all(obj.data.uv_layers for obj in meshes)
  atlas = next(image for image in bpy.data.images if 'buildings-atlas' in image.name)
  assert atlas.packed_file
  assert Path(bpy.path.abspath(atlas.filepath)).is_file()
  modules = [group for group in bpy.data.collections
    if group.name.startswith('MODULE -') and group.asset_data]
  for group in modules:
    assert any(group in list(scene.collection.children)
      for scene in bpy.data.scenes)
  assert stage.camera.data.type == 'ORTHO'
  assert stage.render.resolution_x == stage.render.resolution_y == 2400
  result = {
    'result': 'PASS',
    'nine_stage_assets': len(instances),
    'mirrored_town_hall_wings': len(wings),
    'linked_mirrored_fences': len(fences),
    'pumpkin_instances': len(pumpkins),
    'sixfold_tower_arrays': len(arrays),
    'editable_module_scenes': len(modules),
    'total_live_mirrors': sum(mod.type == 'MIRROR'
      for obj in meshes for mod in obj.modifiers),
    'packed_atlas': True,
    'side_wing_rotations': [-90, 90],
    'mine_rock_free': True,
    'mine_gold_cart_restored': True,
    'crystal_geometry': False,
  }
  (Root/'reviews'/'saved-file-verification.json').write_text(
    json.dumps(result, indent=2))
  print(json.dumps(result, indent=2), flush=True)

check()
