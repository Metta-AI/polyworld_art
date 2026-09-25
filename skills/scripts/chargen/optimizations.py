"""Reduce runtime geometry while retaining the editable authoring meshes."""

import json
import math
from pathlib import Path

import bmesh
import bpy
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform

Ratios = {
  'Clothing_07': .78, 'Clothing_09': 1.0, 'Clothing_11': 1.0,
  'Clothing_16': .68,
  'Gnome_Shirt': .78, 'Gnome_Jacket': .76, 'Gnome_Coat': .78,
  'Gnome_Vest': .72, 'Gnome_Shorts': 1.0, 'Gnome_Boots': .68,
  'Gnome_Belt': 1.0, 'Gnome_Bib': .85, 'Gnome_Suspenders': .90,
  'Hand.Left': .50, 'Hand.Right': .50,
  'Beard_Gnome': .32, 'Beard_Gnome_Moustache': .70,
}
Decals = {'Eyes_Gnome', 'Brow_Atlas01', 'Mouth_Atlas01'}


def triangles(mesh):
  """Count the actual triangulated surface, including material interiors."""
  mesh.calc_loop_triangles()
  return len(mesh.loop_triangles)


def normalizeWeights(item):
  """Keep interpolated influences normalized to the runtime's four joints."""
  for vertex in item.data.vertices:
    groups = sorted(((group.group, group.weight) for group in vertex.groups),
                    key=lambda group: -group[1])
    weights = groups[:4]
    total = sum(weight for index, weight in weights)
    assert total > 0, (item.name, vertex.index)
    for index, weight in groups[4:]:
      item.vertex_groups[index].remove([vertex.index])
    for index, weight in weights:
      item.vertex_groups[index].add([vertex.index], weight / total, 'REPLACE')


def removeLining(item, bodyTree):
  """Remove hidden Solidify lining while retaining outer fabric and edge rims."""
  mesh = item.data
  half = len(mesh.vertices) // 2
  paired = len(mesh.vertices) % 2 == 0 and all(
    (mesh.vertices[i].co - mesh.vertices[i+half].co).length < .02
    for i in range(half))
  if paired:
    # Solidify keeps original vertices first, then its inward duplicates.
    removed = {face.index for face in mesh.polygons
               if all(i >= half for i in face.vertices)}
  else:
    # Clipped trouser sections no longer retain Solidify's vertex ordering.
    assert item.name.startswith(('Clothing_09', 'Clothing_11')), item.name
    removed = {face.index for face in mesh.polygons
               if bodyTree.find_nearest(face.center)[1].dot(face.normal) < -.2}
  data = bmesh.new()
  data.from_mesh(mesh)
  data.faces.ensure_lookup_table()
  normals = {face: {loop.vert: mesh.corner_normals[original.loop_start+i].vector[:]
                   for i, loop in enumerate(face.loops)}
             for face, original in zip(data.faces, mesh.polygons)}
  bmesh.ops.delete(data, geom=[data.faces[i] for i in removed], context='FACES')
  values = [normals[face][loop.vert] for face in data.faces for loop in face.loops]
  data.to_mesh(mesh)
  data.free()
  mesh.normals_split_custom_set(values)


def transferNormals(mesh, source):
  """Interpolate source corner normals without mixing cloth with sharp rims."""
  source.calc_loop_triangles()
  triangles = list(source.loop_triangles)
  tree = BVHTree.FromPolygons([v.co for v in source.vertices],
                             [t.vertices[:] for t in triangles],
                             all_triangles=True)
  normals = []
  for face in mesh.polygons:
    for loop in face.loop_indices:
      point = mesh.vertices[mesh.loops[loop].vertex_index].co
      nearest = tree.find_nearest(point)
      candidates = tree.find_nearest_range(point, nearest[3] + .0001)
      matching = [entry for entry in candidates
                  if triangles[entry[2]].material_index == face.material_index
                  and entry[1].dot(face.normal) > .25]
      candidates = matching or candidates
      # At an unchanged crease vertex several triangles are equally close.
      # Match the side of that crease, rather than taking an arbitrary rim.
      position, normal, index, distance = min(candidates,
        key=lambda entry: (round(entry[3], 4), -entry[1].dot(face.normal)))
      triangle = triangles[index]
      points = [source.vertices[i].co for i in triangle.vertices]
      values = [source.corner_normals[i].vector for i in triangle.loops]
      value = barycentric_transform(position, *points, *values).normalized()
      normals.append(tuple(value))
  mesh.normals_split_custom_set(normals)


def simplify(item, ratio, bodyTree):
  """Keep shell openings and trim intact while simplifying exterior surfaces."""
  item.data = item.data.copy()
  if not item.name.startswith(('Beard_', 'Hand.')):
    removeLining(item, bodyTree)
  if ratio >= 1:
    return
  source = item.data.copy()
  try:
    data = bmesh.new()
    data.from_mesh(item.data)
    locked = set()
    for edge in data.edges:
      if edge.is_boundary or (len(edge.link_faces) == 2 and
        (edge.link_faces[0].material_index != edge.link_faces[1].material_index
         or not edge.smooth)):
          locked.update(vertex.index for vertex in edge.verts)
    if item.name == 'Gnome_Coat':
      locked.update(vertex.index for vertex in data.verts
                    if abs(vertex.co.z - 1.305) < .11)
    if item.name == 'Gnome_Boots':
      locked.update(vertex.index for vertex in data.verts
                    if vertex.co.z > .20)
    # Preserve the short shading transition beside hems, cuffs, and creases.
    for i in range(1 if item.name.startswith("Hand.") else 2):
      locked.update({vertex.index for edge in data.edges
                    if any(vertex.index in locked for vertex in edge.verts)
                    for vertex in edge.verts})
    data.free()
    group = item.vertex_groups.new(name='Runtime simplification')
    groupName = group.name
    group.add([vertex.index for vertex in item.data.vertices
               if vertex.index not in locked], 1, 'REPLACE')
    modifier = item.modifiers.new('Runtime triangle budget', 'DECIMATE')
    modifier.decimate_type = 'COLLAPSE'
    modifier.ratio = ratio
    modifier.use_collapse_triangulate = True
    modifier.use_symmetry = True
    modifier.symmetry_axis = 'X'
    modifier.vertex_group = groupName
    bpy.ops.object.modifier_move_to_index(modifier=modifier.name, index=0)
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    item.vertex_groups.remove(item.vertex_groups[groupName])
    normalizeWeights(item)
    transferNormals(item.data, source)
  finally:
    bpy.data.meshes.remove(source)


def simplifyDecal(item):
  """Dissolve redundant planar grid edges without changing texture artwork."""
  item.data = item.data.copy()
  modifier = item.modifiers.new('Runtime face projection', 'DECIMATE')
  modifier.decimate_type = 'DISSOLVE'
  modifier.angle_limit = math.radians(.1)
  modifier.use_dissolve_boundaries = True
  modifier.delimit = {'NORMAL', 'MATERIAL', 'SEAM', 'SHARP', 'UV'}
  bpy.ops.object.modifier_move_to_index(modifier=modifier.name, index=0)
  bpy.ops.object.modifier_apply(modifier=modifier.name)


def exportScene(**options):
  """Export reduced mesh copies, then restore the full authoring geometry."""
  selected = list(bpy.context.selected_objects)
  active = bpy.context.view_layer.objects.active
  originals, modifiers, report = [], [], []
  points, faces = [], []
  for name in ['Body', 'Foot.Left', 'Foot.Right']:
    mesh = bpy.data.objects[name].data
    offset = len(points)
    points.extend(vertex.co.copy() for vertex in mesh.vertices)
    faces.extend(tuple(i + offset for i in face.vertices) for face in mesh.polygons)
  bodyTree = BVHTree.FromPolygons(points, faces)
  try:
    for item in selected:
      if item.type != 'MESH':
        continue
      base = item.name.split('_BootCut')[0]
      if base not in Ratios and item.name not in Decals:
        continue
      originals.append((item, item.data))
      for modifier in item.modifiers:
        if modifier.type == 'ARMATURE':
          modifiers.append((modifier, modifier.show_viewport, modifier.show_render))
          modifier.show_viewport = False
          modifier.show_render = False
      bpy.context.view_layer.objects.active = item
      before = triangles(item.data)
      if item.name in Decals:
        simplifyDecal(item)
      else:
        simplify(item, Ratios[base], bodyTree)
      after = triangles(item.data)
      assert 0 < after <= before, (item.name, before, after)
      assert all(math.isfinite(value) for vertex in item.data.vertices
                 for value in vertex.co), item.name
      report.append(dict(name=item.name, before=before, after=after))
    for modifier, viewport, render in modifiers:
      modifier.show_viewport, modifier.show_render = viewport, render
    bpy.context.view_layer.objects.active = active
    bpy.ops.export_scene.gltf(**options)
    Path(options['filepath']).with_suffix('.geometry.json').write_text(
      json.dumps(report, indent=2) + '\n')
  finally:
    for modifier, viewport, render in modifiers:
      modifier.show_viewport, modifier.show_render = viewport, render
    for item, original in originals:
      reduced = item.data
      item.data = original
      if reduced != original:
        bpy.data.meshes.remove(reduced)
    bpy.context.view_layer.objects.active = active
