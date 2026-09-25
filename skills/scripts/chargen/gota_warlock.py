"""Build the Warlock's separate fitted, solid-color fantasy garments."""

import math

import bpy
from mathutils import Vector

from clothes import band, bodySurface, clip, keepFaces, material, meshObject, offset
from garments import exterior, finish
from gota_common import bind, duplicate, mesh, part, smooth, roundedHood

Burgundy = '#792638'
Gold = '#e1ad42'
Leather = '#45312c'
Charcoal = '#28252e'


def panel(ctx, suffix, points, color, bone=None, depth=.018):
  """Build a faceted thick cloth panel with a slightly raised central fold."""
  points = [Vector(point) for point in points]
  normal = (points[1] - points[0]).cross(points[2] - points[0]).normalized()
  count = len(points)
  center = sum(points, Vector()) / count
  verts = points + [center + normal * .015]
  verts += [p - normal * depth for p in points]
  faces = [(i, (i + 1) % count, count) for i in range(count)]
  faces += [tuple(range(count + 1, count * 2 + 1))]
  faces += [(i, count + 1 + i, count + 1 + (i + 1) % count,
             (i + 1) % count) for i in range(count)]
  return mesh(ctx, suffix, verts, faces, [color], bone=bone)


def hood(ctx):
  """Make an open pointed hood and large segmented curled ram horns."""
  result = [roundedHood(ctx, 'Hood', [Burgundy, Gold, Charcoal],
    opening='stepped', rearTrim=True)]
  for sign in [-1, 1]:
    path = [(.34, -.04, 2.99, .205), (.50, -.03, 3.23, .217),
            (.67, -.03, 3.405, .21), (.89, -.04, 3.38, .19),
            (1.055, -.08, 3.21, .16), (1.10, -.16, 3.01, .133),
            (1.035, -.245, 2.84, .105), (.90, -.30, 2.795, .077),
            (.80, -.33, 2.87, .025)]
    verts, faces, mats = [], [], []
    sides = 12
    for row, (x, y, z, radius) in enumerate(path):
      center = Vector((sign * x, y, z))
      before = path[max(row - 1, 0)]
      after = path[min(row + 1, len(path) - 1)]
      tangent = Vector((sign * (after[0] - before[0]),
                        after[1] - before[1], after[2] - before[2])).normalized()
      side = tangent.cross(Vector((0, 1, 0))).normalized()
      across = tangent.cross(side).normalized()
      for i in range(sides):
        angle = math.tau * i / sides
        verts.append(center + radius * (side * math.cos(angle) +
                                        across * math.sin(angle)))
      if row:
        for i in range(sides):
          a = (row - 1) * sides + i
          b = (row - 1) * sides + (i + 1) % sides
          faces.append((a, b, b + sides, a + sides))
          mats.append(1 if row == 2 else 0)
    faces += [tuple(reversed(range(sides))),
              tuple(range(len(verts) - sides, len(verts)))]
    mats += [0, 0]
    horn = mesh(ctx, 'Horn' + str(sign), verts, faces, [Leather, Gold], bone='Head')
    for face, index in zip(horn.data.polygons, mats):
      face.material_index = index
    result.append(smooth(horn, 65))
  for obj in result:
    if obj.name.startswith(ctx.prefix + 'Hood'):
      continue
    for vertex in obj.data.vertices:
      point = vertex.co
      point.x *= .92
      point.z = 2.56 + (point.z - 2.56) * .91
      point.y = point.y * .94 if point.y > 0 else point.y - .02
  return result


def sleeves(ctx):
  """Build broad hanging sleeves on the existing arm weights."""
  result = []
  for sign in [-1, 1]:
    verts, faces, mats, weights = [], [], [], []
    side = 'Left' if sign == 1 else 'Right'
    for row, (x, ry, upper, lower) in enumerate([
      (.32, .195, 1.945, 1.55), (.51, .225, 1.955, 1.44),
      (.79, .25, 1.952, 1.26), (.87, .25, 1.947, 1.235)]):
      for i in range(8):
        theta = math.tau * i / 8
        center = (upper + lower) / 2
        verts.append((sign * x, .015 + ry * math.sin(theta),
                      center + (upper - lower) / 2 * math.cos(theta)))
        factor = max(0, min(1, (x - .65) / .22))
        weights.append({side + 'Arm': 1 - factor,
                        side + 'ForeArm': factor})
      if row:
        for i in range(8):
          a, b = (row - 1) * 8 + i, (row - 1) * 8 + (i + 1) % 8
          faces.append((a, b, b + 8, a + 8))
          mats.append(1 if row == 3 else 0)
    obj = mesh(ctx, 'Sleeve' + str(sign), verts, faces, [Burgundy, Gold],
               weights=weights)
    for face, index in zip(obj.data.polygons, mats):
      face.material_index = index
    result.append(smooth(obj, 50))
  return result


def skirt(ctx):
  """Make divided low-poly robe tails and a separate pointed central panel."""
  verts, faces, mats, weights = [], [], [], []
  degrees = [17, 40, 65, 90, 115, 140, 176,
             184, 220, 245, 270, 295, 320, 343]
  for row, amount in enumerate([0, .5, .92, 1]):
    shaped = degrees[:]
    for index, ending in [(0, 34), (6, 157), (7, 203), (13, 326)]:
      shaped[index] += (ending - shaped[index]) * amount
    angles = [math.radians(v) for v in shaped]
    for angle in angles:
      low = .35 + .16 * abs(math.cos(angle))
      x = (.405 + .095 * amount) * math.sin(angle)
      y = -(.335 + .04 * amount) * math.cos(angle)
      verts.append((x, y, 1.31 * (1 - amount) + low * amount))
      side = 'Left' if x > 0 else 'Right'
      weights.append({'Hips': 1 - amount, side + 'UpLeg': amount})
    if row:
      for i in range(13):
        if i == 6:
          continue
        a, b = (row - 1) * 14 + i, (row - 1) * 14 + i + 1
        faces += [(a, b, b + 14), (a, b + 14, a + 14)]
        mats += [1 if row == 3 else 0] * 2
  obj = mesh(ctx, 'RobeTails', verts, faces, [Burgundy, Gold], weights=weights)
  for face, index in zip(obj.data.polygons, mats):
    face.material_index = index
  result = [obj]
  result.append(panel(ctx, 'TabardGold', [(-.14, -.322, 1.31),
    (-.17, -.391, .57), (0, -.397, .43), (.17, -.391, .57),
    (.14, -.322, 1.31)], Gold, bone='Hips'))
  result.append(panel(ctx, 'Tabard', [(-.103, -.343, 1.31),
    (-.125, -.412, .596), (0, -.418, .488), (.125, -.412, .596),
    (.103, -.343, 1.31)], Burgundy, bone='Hips'))
  return result


def robe(ctx):
  """Reuse fitted torso cloth and add silhouette-defining robe details."""
  source = exterior([bpy.data.objects['Clothing_07']], ctx.body)
  source = clip(source, lambda p: p.z - 1.28)
  source = clip(source, lambda p: max(.385 - abs(p.x), 1.54 - p.z))
  source = offset(source, .012)
  torso = finish(ctx.collection, ctx.prefix + 'Torso', [(source, 0)],
    [material(ctx.prefix + 'Burgundy', Burgundy)], 'Clothing_07 fitted exterior')
  for face in torso.data.polygons:
    face.use_smooth = False
  bind(ctx, torso)
  result = [torso] + sleeves(ctx) + skirt(ctx)
  waist = bodySurface([ctx.body])
  waist = clip(waist, lambda p: p.z - 1.08)
  waist = clip(waist, lambda p: 1.41 - p.z)
  waist = offset(waist, .049)
  lining = finish(ctx.collection, ctx.prefix + 'WaistLining', [(waist, 0)],
    [material(ctx.prefix + 'Burgundy', Burgundy)], 'Body fitted waist surface')
  for face in lining.data.polygons:
    face.use_smooth = False
  bind(ctx, lining)
  result.append(lining)
  for sign in [-1, 1]:
    points = [(sign * .04, -.28, 1.92), (sign * .40, -.21, 1.93),
              (sign * .23, -.345, 1.735)]
    result.append(panel(ctx, 'Collar' + str(sign), points, Gold, bone='Spine2'))
    for back in [False, True]:
      # Surface-following crossed chest straps remain attached to the robe.
      y = .327 if back else -.337
      points = [(sign * -.255, y, 1.33), (sign * -.165, y - .006, 1.30),
                (sign * .32, y - .006, 1.81), (sign * .23, y, 1.86)]
      strap = panel(ctx, 'Strap' + str(sign) + str(back), points, Leather)
      strap.vertex_groups.clear()
      for vertex in strap.data.vertices:
        factor = max(0, min(1, (vertex.co.z - 1.30) / .56))
        for name, weight in {'Hips': 1 - factor, 'Spine2': factor}.items():
          group = strap.vertex_groups.get(name) or strap.vertex_groups.new(name=name)
          group.add([vertex.index], weight, 'REPLACE')
      bind(ctx, strap)
      result.append(strap)
  for side in ['Left', 'Right']:
    result += duplicate(ctx, 'Hand.' + side, 'Glove' + side, [Leather])
    sign = 1 if side == 'Left' else -1
    verts, faces = [], []
    for x in [.855, 1.02]:
      for i in range(8):
        theta = math.tau * i / 8
        verts.append((sign * x, .015 + .105 * math.sin(theta),
                      1.78 + .115 * math.cos(theta)))
    faces += [(i, (i + 1) % 8, (i + 1) % 8 + 8, i + 8)
              for i in range(8)]
    result.append(mesh(ctx, 'GloveCuff' + side, verts, faces, [Leather],
                       bone=side + 'ForeArm'))
  return result


def build(ctx):
  """Return independently selectable Warlock clothes and reusable face preset."""
  boots = duplicate(ctx, 'Clothing_13', 'Boots',
                    [Leather, Leather, Leather, Gold, '#261e1c'])
  legs = duplicate(ctx, 'Clothing_12', 'Legs',
                   [Charcoal, Charcoal, Charcoal, Gold, Charcoal])
  belt = duplicate(ctx, 'Gnome_Belt', 'Belt', [Leather, Leather, Gold])
  keepFaces(belt[0].data, lambda index: index != 2)
  buckleVerts = []
  for y in [-.416, -.390]:
    for width, height in [(.106, .085), (.071, .051)]:
      buckleVerts += [(x, y, 1.305 + z)
                      for x, z in [(-width, -height), (width, -height),
                                   (width, height), (-width, height)]]
  buckleFaces = []
  for i in range(4):
    j = (i + 1) % 4
    buckleFaces += [(i, j, j + 4, i + 4), (i, i + 8, j + 8, j),
                    (i + 4, j + 4, j + 12, i + 12),
                    (i + 8, i + 12, j + 12, j + 8)]
  belt.append(mesh(ctx, 'GoldBuckle', buckleVerts, buckleFaces, [Gold]))
  chest = robe(ctx)
  head = hood(ctx)
  parts = [
    part(ctx, 'Foot', 'Gota Warlock boots', boots,
         hides=[ctx.prefix + 'Legs_BootCut0']),
    part(ctx, 'Leg', 'Gota Warlock trousers', legs),
    part(ctx, 'Belt', 'Gota Warlock belt', belt),
    part(ctx, 'Chest', 'Gota Warlock robe', chest,
         hides=['Hand.Left', 'Hand.Right']),
    part(ctx, 'Headgear', 'Gota Warlock horned hood', head),
  ]
  preset = dict(name='Warlock', group='Gota', pose='A_TPose', skin=13,
    skinRgb=[0.55, 0.36, 0.25], hairColor='Soft black', pupilColor='Amber', parts=[
      dict(category='Eyes', item='08 Sly'),
      dict(category='Mouth', item='03 Neutral'),
      dict(category='Brow', item='10 Mischievous'),
      dict(category='Hair', item='None'),
      dict(category='Beard', item='None'),
      dict(category='Ears', item='None'),
    ])
  return parts, preset
