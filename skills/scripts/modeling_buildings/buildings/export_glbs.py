import hashlib
import json
import shutil
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Matrix, Vector

Root = Path(__file__).resolve().parent
sys.path.insert(0,str(Root))
from externalize_textures import writeExternalGlb
Output = Root/'exports'/'lvd_buildings'
Assets = [
  ('town_hall', '01 Town Hall'),
  ('farm', '02 Farm'),
  ('barracks', '03 Barracks'),
  ('lumber_mill', '04 Lumber Mill'),
  ('tower', '05 Tower'),
  ('stables', '06 Stables and Kennels'),
  ('church', '07 Church and Temple'),
  ('blacksmith', '08 Blacksmith'),
  ('gold_mine', '09 Gold Mine'),
]

def bounds(obj):
  """Measure actual evaluated vertex extents in Blender coordinates."""
  return ([min(vertex.co[i] for vertex in obj.data.vertices) for i in range(3)],
    [max(vertex.co[i] for vertex in obj.data.vertices) for i in range(3)])

def cleanFencePosts(data, seen):
  """Keep one post where two perpendicular fence instances overlap."""
  mesh = bmesh.new()
  mesh.from_mesh(data)
  remaining = set(mesh.verts)
  duplicates = []
  removed = 0
  while remaining:
    pending = [remaining.pop()]
    component = []
    while pending:
      vertex = pending.pop()
      component.append(vertex)
      for edge in vertex.link_edges:
        other = edge.other_vert(vertex)
        if other in remaining:
          remaining.remove(other)
          pending.append(other)
    low = Vector([min(vertex.co[i] for vertex in component)
      for i in range(3)])
    high = Vector([max(vertex.co[i] for vertex in component)
      for i in range(3)])
    center, size = (low+high)/2, high-low
    if any((center-point).length < .02 and (size-dimensions).length < .0001
      for point,dimensions in seen):
      duplicates.extend(component)
      removed += 1
    else:
      seen.append((center,size))
  if duplicates:
    bmesh.ops.delete(mesh, geom=duplicates, context='VERTS')
    mesh.to_mesh(data)
    data.update()
  mesh.free()
  return removed

def exportAsset(slug, sourceName, origin=None, subdirectory='', cleanFence=False):
  """Bake copies of all nested instances and modifiers into one GLB prop."""
  source = bpy.data.scenes[sourceName+' - Edit source']
  bpy.context.window.scene = source
  bpy.context.view_layer.update()
  graph = bpy.context.evaluated_depsgraph_get()
  occurrences = [(item.object.original, item.matrix_world.copy())
    for item in graph.object_instances if item.object.type == 'MESH']
  assert occurrences, sourceName
  baked = []
  fencePosts, removedPosts = [], 0
  for original, transform in occurrences:
    evaluated = original.evaluated_get(graph)
    data = bpy.data.meshes.new_from_object(evaluated,
      preserve_all_data_layers=True, depsgraph=graph)
    data.transform(transform)
    if (slug == 'farm' or cleanFence) and original.name.startswith('Fence half post'):
      removedPosts += cleanFencePosts(data,fencePosts)
    baked.append((original.name,data))
  if slug == 'farm' or cleanFence:
    assert removedPosts == 4, removedPosts
  exportScene = bpy.data.scenes.new('EXPORT - '+slug)
  copies = []
  for name, data in baked:
    obj = bpy.data.objects.new(name+' - export copy',data)
    exportScene.collection.objects.link(obj)
    copies.append(obj)
  bpy.context.window.scene = exportScene
  for obj in copies:
    obj.select_set(True)
  bpy.context.view_layer.objects.active = copies[0]
  bpy.ops.object.join()
  joined = bpy.context.object
  joined.name = slug
  joined.data.name = slug
  low, high = bounds(joined)
  offset = Vector(origin if origin is not None else
    ((low[0]+high[0])/2,(low[1]+high[1])/2,low[2]))
  joined.data.transform(Matrix.Translation(-offset))
  joined.data.update()
  joined.data.calc_loop_triangles()
  triangles = len(joined.data.loop_triangles)
  low, high = bounds(joined)
  assert abs(low[2]) < .0001
  assert joined.data.uv_layers
  filename = Output/'models'/subdirectory/(slug+'.glb')
  filename.parent.mkdir(parents=True,exist_ok=True)
  result = bpy.ops.export_scene.gltf(
    filepath=str(filename),
    export_format='GLB',
    use_active_scene=True,
    use_selection=True,
    export_apply=True,
    export_texcoords=True,
    export_normals=True,
    export_materials='EXPORT',
    export_image_format='AUTO',
    export_animations=False,
    export_cameras=False,
    export_lights=False,
    export_extras=False,
    export_yup=True,
  )
  assert result == {'FINISHED'}
  atlasPath = Output/'textures'/'buildings-atlas.png'
  atlasPath.parent.mkdir(parents=True,exist_ok=True)
  shutil.copy2(Root/'assets'/'buildings-atlas.png',atlasPath)
  writeExternalGlb(filename,atlasPath)
  record = {
    'name':slug,
    'file':str(filename.relative_to(Output)),
    'triangles':triangles,
    'dimensions':[round(high[0]-low[0],6),round(high[2]-low[2],6),
      round(high[1]-low[1],6)],
    'sha256':hashlib.sha256(filename.read_bytes()).hexdigest(),
    'scale_from_original':bpy.data.collections[sourceName].get('door_scale_factor',1.0),
  }
  evidence = {
    'name':slug, 'evaluated_parts':len(occurrences),
    'source_collection':sourceName, 'blender_origin_offset':list(offset),
    'blender_bounds':[low,high], 'triangles':triangles,
    'bytes':filename.stat().st_size,
    'redundant_fence_posts_removed':removedPosts,
  }
  bpy.context.window.scene = source
  bpy.data.objects.remove(joined,do_unlink=True)
  bpy.data.scenes.remove(exportScene)
  print('EXPORTED',json.dumps(evidence),flush=True)
  return record,evidence

sourcePath = Path(bpy.data.filepath)
sourceHash = hashlib.sha256(sourcePath.read_bytes()).hexdigest()
records, evidence = [], []
for slug, group in Assets:
  record, item = exportAsset(slug,group)
  records.append(record)
  evidence.append(item)
manifest = {
  'pack':'lvd_buildings',
  'format':'glTF 2.0 binary',
  'model_count':len(records),
  'coordinates':'Y up, front +Z, meters; origin at footprint center on ground',
  'textures':'One shared external PNG referenced by relative URI from every GLB',
  'texture_source':'textures/buildings-atlas.png',
  'texture_size':[512,512],
  'models':records,
}
if all('door_scale_factor' in bpy.data.collections[group] for slug,group in Assets):
  manifest['door_reference_height'] = 1.5
(Output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
assert hashlib.sha256(sourcePath.read_bytes()).hexdigest() == sourceHash
(Root/'reviews'/'glb-export.json').write_text(json.dumps({
  'source_blend':str(sourcePath), 'source_sha256':sourceHash,
  'source_unchanged':True, 'models':evidence},indent=2)+'\n')
