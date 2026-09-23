"""Build the Druid Warden from fitted clothing and angular foliage."""

import math

import bpy
from mathutils import Vector

from clothes import band, bodySurface, meshObject, sourceWeights
from gota_common import bind, duplicate, mesh, part, smooth

Brown = '#77513b'
DarkBrown = '#4c3d2c'
Green = '#53792c'
BrightGreen = '#759536'
DarkGreen = '#3d652d'
Gold = '#e2ae43'


def leaf(ctx, suffix, points, color, bone=None, depth=.032):
  """Make a solid six-face leaf with one broad raised central ridge."""
  points = [Vector(point) for point in points]
  center = sum(points, Vector()) / len(points)
  normal = (points[1] - points[0]).cross(points[2] - points[0]).normalized()
  if normal.y > 0:
    normal = -normal
  vertices = points + [center + normal * depth, center - normal * .012]
  front, back = len(points), len(points) + 1
  faces = []
  for i in range(len(points)):
    j = (i + 1) % len(points)
    faces += [(i, j, front), (j, i, back)]
  return mesh(ctx, suffix, vertices, faces, [color], bone=bone)


def tube(ctx, suffix, path, radii, color, bone='Head'):
  """Form a gently shaded antler segment from a few low-poly rings."""
  vertices, faces = [], []
  for i, point in enumerate(path):
    point = Vector(point)
    direction = Vector(path[min(i + 1, len(path) - 1)]) - Vector(path[max(0, i - 1)])
    direction.normalize()
    across = direction.cross(Vector((0, 1, 0))).normalized()
    deep = direction.cross(across).normalized()
    for j in range(6):
      angle = j * math.tau / 6
      vertices.append(point + radii[i] * (math.cos(angle) * across + math.sin(angle) * deep))
  for i in range(len(path) - 1):
    for j in range(6):
      a, b = i * 6 + j, i * 6 + (j + 1) % 6
      faces.append((a, b, b + 6, a + 6))
  faces += [tuple(reversed(range(6))), tuple(range(len(vertices) - 6, len(vertices)))]
  return smooth(mesh(ctx, suffix, vertices, faces, [color], bone=bone), 70)


def simplify(obj, ratio):
  """Retain the fitted part while making its inherited topology faceted."""
  bpy.context.view_layer.objects.active = obj
  modifier = obj.modifiers.new('Low polygon foliage', 'DECIMATE')
  modifier.ratio = ratio
  bpy.ops.object.modifier_apply(modifier=modifier.name)
  for polygon in obj.data.polygons:
    polygon.use_smooth = False


def build(ctx):
  """Create five clothing slots and two green reused hair components."""
  parts = []
  sample = sourceWeights(bodySurface([ctx.body, bpy.data.objects['Foot.Left'],
                                     bpy.data.objects['Foot.Right']]))
  boots = duplicate(ctx, 'Clothing_14', 'boots', [Brown, '#896045', DarkBrown, Gold, DarkBrown])
  for obj in boots:
    for vertex in obj.data.vertices:
      vertex.co.z *= 1.29
      influences = sample(vertex.co)
      for group in obj.vertex_groups:
        group.remove([vertex.index])
      for name, value in influences.items():
        group = obj.vertex_groups.get(name) or obj.vertex_groups.new(name=name)
        group.add([vertex.index], value, 'REPLACE')
    simplify(obj, .65)
    smooth(obj)
  parts.append(part(ctx, 'Foot', 'Gota Druid Warden boots', boots))

  legs = duplicate(ctx, 'Clothing_09', 'legs', [Brown, Brown, DarkBrown, Gold, DarkBrown])
  kept = []
  for obj in legs:
    if '_BootCut' in obj.name and not obj.name.endswith('_BootCut3'):
      bpy.data.objects.remove(obj, do_unlink=True)
    else:
      for vertex in obj.data.vertices:
        center = math.copysign(.245, vertex.co.x)
        center *= max(0, min(1, (1.10 - vertex.co.z) / .22))
        vertex.co.x = center + (vertex.co.x - center) * 1.12
        vertex.co.y *= 1.12
      kept.append(obj)
  legs = kept
  for side in [-1, 1]:
    for back in [False, True]:
      y = .30 if back else -.33
      for i, (x, bottom, width) in enumerate([(.22, .72, .22), (.34, .84, .20)]):
        coords = [(side * (x - width / 2), y, 1.27),
                  (side * (x + width / 2), y * 1.06, 1.22),
                  (side * (x + width * .70), y * 1.11, bottom),
                  (side * (x - width * .50), y * 1.04, bottom + .13)]
        legs.append(leaf(ctx, f'hip_leaf_{side}_{back}_{i}', coords,
                         BrightGreen if i == 0 else Green))
  for back in [False, True]:
    y = .32 if back else -.36
    legs.append(leaf(ctx, f'center_skirt_{back}',
      [(-.145, y, 1.27), (.145, y, 1.27), (.13, y * 1.1, .91),
       (0, y * 1.13, .67), (-.13, y * 1.1, .91)], DarkGreen, depth=.045))
  parts.append(part(ctx, 'Leg', 'Gota Druid Warden leaf skirt', legs))

  source = bodySurface([ctx.body])
  beltSurface = band(source, [lambda p: p.z - 1.22,
                             lambda p: 1.35 - p.z], .076)
  belt = meshObject(ctx.collection, ctx.prefix + 'belt', [(beltSurface, 0)],
                    [bpy.data.materials[boots[0].data.materials[2].name]])
  bind(ctx, belt)
  vertices, faces = [], []
  for y in [-.365, -.410]:
    for radius in [.13, .075]:
      for i in range(6):
        angle = math.pi / 2 + i * math.tau / 6
        vertices.append((math.cos(angle) * radius, y,
                         1.285 + math.sin(angle) * radius))
  for i in range(6):
    j = (i + 1) % 6
    faces += [(i, j, j + 6, i + 6), (i + 12, i + 18, j + 18, j + 12),
              (i, i + 12, j + 12, j), (i + 6, j + 6, j + 18, i + 18)]
  buckle = mesh(ctx, 'hexagon_buckle', vertices, faces, [Gold])
  parts.append(part(ctx, 'Belt', 'Gota Druid Warden hexagon belt', [belt, buckle]))

  body = duplicate(ctx, 'Clothing_06', 'bark_body', [Brown, '#936447', DarkBrown, Brown])
  for obj in body:
    simplify(obj, .7)
  # The overlapping broad bark plates conceal the inherited jerkin opening.
  for back in [False, True]:
    y = .325 if back else -.35
    body.append(leaf(ctx, f'bark_center_{back}',
      [(-.25, y, 1.83), (0, y * 1.12, 1.92), (.25, y, 1.83),
       (.24, y * 1.03, 1.47), (0, y * 1.12, 1.25),
       (-.24, y * 1.03, 1.47)], Brown, depth=.022))
    if back:
      body.append(leaf(ctx, 'mantle_back_leaf',
        [(-.24, .385, 1.91), (.24, .385, 1.91),
         (.19, .405, 1.68), (0, .415, 1.47), (-.19, .405, 1.68)],
        BrightGreen, depth=.045))
    else:
      body.append(leaf(ctx, 'bark_cross_left',
        [(-.245, -.405, 1.87), (-.08, -.42, 1.90),
         (.245, -.42, 1.54), (.17, -.43, 1.39), (-.21, -.42, 1.69)],
        '#906042', depth=.022))
      body.append(leaf(ctx, 'bark_cross_right',
        [(.245, -.445, 1.87), (.08, -.45, 1.90),
         (-.245, -.45, 1.54), (-.17, -.46, 1.39), (.21, -.45, 1.69)],
        '#80553b', depth=.022))
    for side in [-1, 1]:
      for i in range(3):
        x, z = .27 + i * .014, 1.88 - i * .16
        body.append(leaf(ctx, f'mantle_{back}_{side}_{i}',
          [(side * .19, y, z + .10), (side * .38, y * .8, z + .08),
           (side * (.57 - i * .025), y * .67, z - .09),
           (side * (.33 + i * .012), y * .94, z - .16)],
          BrightGreen if i == 0 else Green))
  # Cuffs inherit source forearm weights so the open hands remain reusable.
  for side in [-1, 1]:
    surface = band(source, [lambda p, s=side: s * p.x - .72,
                           lambda p, s=side: .91 - s * p.x], .045)
    cuff = meshObject(ctx.collection, ctx.prefix + f'cuff_{side}',
                      [(surface, 0)], [body[0].data.materials[0]])
    bind(ctx, cuff)
    body.append(cuff)
  parts.append(part(ctx, 'Chest', 'Gota Druid Warden bark mantle', body))

  headgear = []
  for side in [-1, 1]:
    points = [(side * .28, .03, 2.95), (side * .60, .04, 3.08),
              (side * .76, .04, 3.31), (side * .73, .03, 3.55),
              (side * .84, .025, 3.72)]
    headgear.append(tube(ctx, f'antler_{side}', points,
                         [.115, .115, .10, .07, .005], Brown))
    headgear.append(tube(ctx, f'antler_outer_{side}',
      [(side * .63, .035, 3.14), (side * .88, .035, 3.20),
       (side * 1.00, .035, 3.36)], [.085, .065, .004], Brown))
    for i, (x, z, direction) in enumerate([(.66, 3.17, -1), (.73, 3.45, 1)]):
      headgear.append(leaf(ctx, f'antler_leaf_{side}_{i}',
        [(side * x, -.02, z), (side * (x + .07), -.05, z + direction * .08),
         (side * (x + .04), -.03, z + direction * .23),
         (side * (x - .09), -.025, z + direction * .16)], BrightGreen,
        bone='Head'))
  parts.append(part(ctx, 'Headgear', 'Gota Druid Warden antler crown', headgear))

  hair = duplicate(ctx, 'Hair_12', 'green_hair', [Green, BrightGreen, DarkGreen])
  for obj in hair:
    simplify(obj, .19)
    bind(ctx, obj)
  hair.append(leaf(ctx, 'hair_peak', [(-.16, -.50, 2.99), (0, -.40, 3.23),
                                    (.16, -.50, 2.99), (0, -.565, 2.81)],
                   BrightGreen, bone='Head', depth=.055))
  parts.append(part(ctx, 'Hair', 'Gota Druid Warden leaf hair', hair))
  beard = duplicate(ctx, 'Beard_09', 'green_beard', [Green, BrightGreen, DarkGreen])
  for obj in beard:
    for vertex in obj.data.vertices:
      if vertex.co.z < 2.31:
        vertex.co.z = 2.31 + (vertex.co.z - 2.31) * .68
    simplify(obj, .20)
    bind(ctx, obj)
  beard.append(leaf(ctx, 'beard_leaf', [(-.17, -.60, 2.25), (0, -.66, 2.32),
                                     (.17, -.60, 2.25), (.14, -.67, 2.03),
                                     (0, -.66, 1.88), (-.14, -.67, 2.03)],
                    BrightGreen, bone='Head', depth=.032))
  parts.append(part(ctx, 'Beard', 'Gota Druid Warden leaf beard', beard))

  preset = dict(name='Druid Warden', group='Gota', pose='A_TPose', skin=12,
                hairColor='Moss', pupilColor='Green', parts=[
                  dict(category='Eyes', item='04 Calm'),
                  dict(category='Mouth', item='03 Neutral'),
                  dict(category='Brow', item='12 Sweeping'),
                  dict(category='Ears', item='Elf')])
  return parts, preset
