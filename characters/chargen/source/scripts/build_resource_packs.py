"""Author two modular resource backpacks on the canonical Chargen skeleton."""
import json
import math
import sys
from pathlib import Path
from types import SimpleNamespace

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True
import glbs
from clothes import bodySurface, material, sourceWeights
from gota_common import mesh, write
from paths import Library, Preview, Source

Output = Source / 'resource_packs'
Review = Preview / 'resource-packs'
Colors = ['#674428', '#795332', '#89613c', '#c69b60', '#9a703e',
          '#c8a777', '#a17a4a', '#8e633a', '#b08350', '#f4c52b', '#c99117']


def geometry():
  """Keep every backpack in one explicit mesh with per-face colors."""
  return SimpleNamespace(vertices=[], faces=[], colors=[], weights=[])


def append(part, vertices, faces, color, weights=None):
  """Append a closed component without introducing extra runtime nodes."""
  start = len(part.vertices)
  part.vertices.extend(tuple(p) for p in vertices)
  part.faces.extend(tuple(start + i for i in face) for face in faces)
  part.colors.extend(color if isinstance(color, list) else [color] * len(faces))
  part.weights.extend(weights or [{'Spine2': 1}] * len(vertices))


def tube(part, points, radius, color, sample=None, sides=4):
  """Sweep a small faceted rope around a closed path with stable normals."""
  points = [Vector(p) for p in points]
  vertices, faces, weights = [], [], []
  for i, point in enumerate(points):
    tangent = (points[(i + 1) % len(points)] - points[i - 1]).normalized()
    axis = Vector((1, 0, 0))
    if abs(tangent.dot(axis)) > .95:
      axis = Vector((0, 1, 0))
    across = tangent.cross(axis).normalized()
    up = tangent.cross(across).normalized()
    for j in range(sides):
      theta = j * math.tau / sides
      vertices.append(point + radius * (across * math.cos(theta) +
                                       up * math.sin(theta)))
      weights.append(sample(point) if sample else {'Spine2': 1})
      faces.append((i * sides + j, i * sides + (j + 1) % sides,
                    ((i + 1) % len(points)) * sides + (j + 1) % sides,
                    ((i + 1) % len(points)) * sides + j))
  append(part, vertices, faces, color, weights)


def harness(part, body):
  """Fit both shoulder ropes to the real tunic and inherit torso weights."""
  tree = BVHTree.FromPolygons([v.co for v in body.data.vertices],
                              [p.vertices[:] for p in body.data.polygons])
  sample = sourceWeights(bodySurface([body]))
  for side in [-1, 1]:
    points = []
    outline = [(.20, -.30, 1.29), (.20, -.30, 1.45),
               (.22, -.29, 1.64), (.25, -.24, 1.80),
               (.28, -.16, 1.91), (.29, 0, 1.94),
               (.28, .16, 1.91), (.25, .26, 1.80),
               (.22, .30, 1.64), (.20, .30, 1.45),
               (.20, .30, 1.29), (.30, .18, 1.27),
               (.34, 0, 1.27), (.30, -.18, 1.27)]
    for i, (x, y, z) in enumerate(outline):
      point, normal, _, _ = tree.find_nearest(Vector((side * x, y, z)))
      if point is None:
        raise ValueError('Cannot fit backpack straps to the actual torso.')
      point += normal * .035
      if i in [7, 8, 9]:
        point.y = max(point.y, .36 if i != 9 else .32)
      points.append(point)
    tube(part, points, .024, 5, sample)


def log(part, center, length, radius, index):
  """Use eight bark faces and plain cut ends, without geometric tree rings."""
  sides = 8
  vertices, faces, colors = [], [], []
  for row, (x, scale) in enumerate([(-length / 2, 1),
                                   (length / 2, .94)]):
    for i in range(sides):
      angle = i * math.tau / sides
      width = radius * scale * (1 + .045 * math.sin(i * 3 + index))
      vertices.append((center[0] + x, center[1] + width * math.cos(angle),
                       center[2] + width * math.sin(angle)))
      if row:
        k, j = (row - 1) * sides + i, (row - 1) * sides + (i + 1) % sides
        faces.append((k, j, j + sides, k + sides))
        colors.append((i + index) % 3)
  for row in [0, 1]:
    faces.append(tuple(row * sides + i for i in range(sides)))
    colors.append(3)
  append(part, vertices, faces, colors)


def wood(body):
  """Stack five short logs tightly and bind the load in two places."""
  part = geometry()
  harness(part, body)
  for i, (y, z, length) in enumerate([
      (.40, 1.24, .96), (.40, 1.53, 1.02), (.40, 1.82, .94),
      (.65, 1.385, .90), (.65, 1.675, .97)]):
    log(part, ((i % 2) * .025, y, z), length, .15, i)
  outline = [(.46, 1.075), (.34, 1.14), (.31, 1.30), (.31, 1.75),
             (.35, 1.94), (.50, 1.985), (.66, 1.92), (.85, 1.78),
             (.90, 1.64), (.90, 1.42), (.85, 1.27), (.64, 1.12)]
  for x in [-.275, .275]:
    tube(part, [(x, y - .08, z) for y, z in outline], .027, 5)
  return part


def coin(part, center, radius, tilt, index):
  """Create a chunky gold disk with a dark rim and readable flat faces."""
  normal = Vector((math.sin(tilt), .12 * math.sin(index), math.cos(tilt)))
  normal.normalize()
  across = normal.cross(Vector((0, 1, 0))).normalized()
  up = normal.cross(across)
  vertices, faces, colors = [], [], []
  for height in [-.013, .013]:
    for i in range(8):
      angle = i * math.tau / 8
      vertices.append(Vector(center) + normal * height + radius *
                      (math.cos(angle) * across + math.sin(angle) * up))
  for i in range(8):
    faces.append((i, (i + 1) % 8, (i + 1) % 8 + 8, i + 8))
    colors.append(10)
  faces.extend([tuple(range(8)), tuple(range(8, 16))])
  colors.extend([9, 9])
  append(part, vertices, faces, colors)


def gold(body):
  """Shape a full sack with a hollow folded mouth and a visible coin pile."""
  part = geometry()
  harness(part, body)
  cargoStart = len(part.vertices)
  profiles = [(1.08, .19, .16), (1.27, .37, .285),
              (1.60, .40, .30), (1.82, .31, .245),
              (1.94, .19, .17), (2.075, .245, .215),
              (2.065, .207, .177), (1.985, .17, .143)]
  vertices, faces, colors = [], [], []
  sides = 10
  for row, (z, width, depth) in enumerate(profiles):
    for i in range(sides):
      angle = i * math.tau / sides
      fold = 1 + .055 * math.sin(i * 5 + row * .6)
      vertices.append((width * math.cos(angle) * fold,
                       .535 + depth * math.sin(angle) * fold, z +
                       (.012 * math.sin(i * 3) if row > 4 else 0)))
      if row:
        k, j = (row - 1) * sides + i, (row - 1) * sides + (i + 1) % sides
        faces.append((k, j, j + sides, k + sides))
        colors.append(7 if row >= 7 else (6 + (i // 3 + row) % 3))
  faces += [tuple(range(sides)), tuple(range(7 * sides, 8 * sides))]
  colors += [7, 7]
  append(part, vertices, faces, colors)
  tube(part, [(.195 * math.cos(i * math.tau / 12),
              .535 + .177 * math.sin(i * math.tau / 12), 1.945)
              for i in range(12)], .024, 5)
  for i in range(5):
    angle = i * 2.399963
    radius = .123 if i else 0
    coin(part, (math.cos(angle) * radius, .535 + math.sin(angle) * radius,
                2.045 + (.035 if i in [0, 3, 6] else 0)),
         .087 + .008 * (i % 2), (i % 3 - 1) * .28, i)
  for i in range(cargoStart, len(part.vertices)):
    x, y, z = part.vertices[i]
    part.vertices[i] = (x * 1.20, .59 + (y - .535) * 1.15,
                        1.58 + (z - 1.58) * 1.18)
  return part


def run():
  """Write only the two new parts and an isolated editable authoring scene."""
  Output.mkdir(parents=True, exist_ok=True)
  Review.mkdir(parents=True, exist_ok=True)
  bpy.ops.wm.open_mainfile(filepath=str(Source / 'character.blend'))
  rig = bpy.data.objects['CharacterRig']
  rig.animation_data_clear()
  rig.data.pose_position = 'REST'
  for bone in rig.pose.bones:
    bone.matrix_basis.identity()
  body = bpy.data.objects.get('Clothing_05') or bpy.data.objects['Body']
  ctx = SimpleNamespace(rig=rig, collection=body.users_collection[0],
                        prefix='ResourcePack_')
  materials = [material('ResourcePack_' + str(i), value)
               for i, value in enumerate(Colors)]
  metadata, objects = [], []
  for slug, label, build in [('wood', 'Wood stack backpack', wood),
                              ('gold', 'Gold sack backpack', gold)]:
    part = build(body)
    obj = mesh(ctx, slug, part.vertices, part.faces, materials,
               weights=part.weights)
    for face, color in zip(obj.data.polygons, part.colors):
      face.material_index = color
    objects.append(obj)
    bpy.ops.object.select_all(action='DESELECT')
    for item in [rig, obj]:
      item.hide_set(False)
      item.select_set(True)
    bpy.context.view_layer.objects.active = rig
    temporary = Review / (slug + '.glb')
    bpy.ops.export_scene.gltf(filepath=str(temporary), export_format='GLB',
      use_selection=True, export_animations=False, export_skins=True,
      export_materials='EXPORT', export_yup=True)
    doc, binary = glbs.read(temporary)
    doc, binary = glbs.subset(doc, binary, meshes=[obj.name])
    identity = 'clothing/backs/resource_' + slug
    glbs.write(Library / (identity + '.glb'), doc, binary)
    triangles = sum(doc['accessors'][p['indices']]['count'] // 3
                    for meshData in doc['meshes'] for p in meshData['primitives'])
    data = dict(id=identity, name=label, files=[identity + '.glb'],
      nodes=[obj.name], alignment='both', hides=[], skinNodes=[],
      hairShades=[], hatShades=[], clothShades=[], singleFile=True,
      triangles=triangles, triangleLimitExclusive=700)
    write(Library / (identity + '.json'), data)
    metadata.append(dict(category='Back', **data))
    print(label + ': ' + str(triangles) + ' triangles')
  write(Output / 'parts.json', metadata)
  # Keep both variants in one clean authoring file, with wood visible initially.
  for obj in list(bpy.data.objects):
    if obj != rig and obj not in objects:
      bpy.data.objects.remove(obj, do_unlink=True)
  for action in list(bpy.data.actions):
    bpy.data.actions.remove(action)
  for image in list(bpy.data.images):
    bpy.data.images.remove(image)
  for i, obj in enumerate(objects):
    obj.hide_render = i != 0
    obj.hide_set(i != 0)
  bpy.context.preferences.filepaths.save_version = 0
  bpy.ops.wm.save_as_mainfile(filepath=str(Output / 'resource_packs.blend'))


if __name__ == '__main__':
  run()
