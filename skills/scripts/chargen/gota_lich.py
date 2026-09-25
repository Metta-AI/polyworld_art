"""Build the pale human Lich's modular blue clothing on the shared rig."""

import math

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

from clothes import band, bodySurface, clip, hemExtrusion, material, offset
from clothes import sourceWeights
from garments import finish
from gota_common import bind, duplicate, part, smooth, roundedHood


def polygon(points, sample):
  """Attach one flat polygon to explicit or sampled rig weights."""
  points = [Vector(point) for point in points]
  normal = (points[1] - points[0]).cross(points[2] - points[0]).normalized()
  return [(point, normal, sample(point)) for point in points]


def diamond(center, size, weights):
  """Build a six-point solid-color faceted diamond ornament."""
  x, y, z = center
  width, depth, height = size
  points = [(x, y, z + height / 2), (x + width / 2, y, z),
            (x, y, z - height / 2), (x - width / 2, y, z),
            (x, y - depth, z), (x, y + depth * .6, z)]
  return [polygon([points[i], points[(i + 1) % 4], points[j]],
                  lambda point: weights) for j in [4, 5] for i in range(4)]


def finishPart(ctx, suffix, surfaces, colors, source):
  """Create a flat-shaded garment and preserve normalized shared rig weights."""
  item = finish(ctx.collection, ctx.prefix + suffix, surfaces, colors, source)
  for face in item.data.polygons:
    face.use_smooth = False
  bind(ctx, item)
  return item


def robe(ctx, source, colors):
  """Fit blue split robes with ivory edges and short triangular bell sleeves."""
  sample = sourceWeights(source)
  torso = clip(source, lambda p: p.z - 1.22)
  torso = clip(torso, lambda p: max(.36 - abs(p.x), 1.54 - p.z))
  torso = clip(torso, lambda p: 1.925 - p.z)
  torso = offset(torso, .057)
  surfaces = [(torso, 0)]
  chest = band(torso, [lambda p: -p.y - .12,
                      lambda p: .15 - abs(p.x)], .008)
  surfaces.append((chest, 4))
  # The new skirt extends the fitted waist with the existing body weights.
  skirt = clip(source, lambda p: p.z - 1.22)
  skirt = clip(skirt, lambda p: 1.30 - p.z)
  skirt = hemExtrusion(skirt, 1.22, .43, sample)
  shaped = []
  for face in skirt:
    records = []
    for point, normal, weights in face:
      amount = max(0, (1.24 - point.z) / .81)
      target = point + normal * .069
      target.x *= 1 + .58 * amount
      target.y *= 1 + .35 * amount
      if point.z < 1.22:
        # Keep the robe floating from the waist instead of following boots.
        leg = 'LeftUpLeg' if point.x > 0 else 'RightUpLeg'
        influence = .85 if point.y < -.07 else .08
        weights = {'Hips': 1 - influence, leg: influence}
        if point.y > 0:
          target.y += .09 * amount
      records.append((target, normal, weights))
    shaped.append(records)

  def opening(point):
    """Widen the blue robe opening toward the ivory-edged lower hem."""
    gap = .12 + max(0, 1.30 - point.z) * .09
    return max(point.y + .05, abs(point.x) - gap)

  skirt = clip(shaped, opening)
  surfaces += [(skirt, 0),
    (band(skirt, [lambda p: .495 - p.z], .006), 1),
    (band(skirt, [lambda p: -p.y - .1,
                  lambda p: .065 - opening(p)], .008), 1)]
  for sign in [-1, 1]:
    lapel = [(sign * .055, -.12, 1.94),
             (sign * .21, -.20, 1.87),
             (sign * .185, -.318, 1.31),
             (sign * .132, -.324, 1.31),
             (sign * .15, -.225, 1.83)]
    surfaces.append(([polygon(lapel, sample)], 1))
    # Sleeves have a pointed lower silhouette and leave the hands exposed.
    rings = []
    for x, width, top, bottom in [(.325, .16, 1.938, 1.575),
        (.47, .19, 1.927, 1.46), (.80, .215, 1.91, 1.265),
        (.83, .218, 1.90, 1.26)]:
      ring = []
      for i in range(8):
        angle = math.tau * i / 8
        ring.append((sign * x, .014 - width * math.cos(angle),
          (top + bottom) / 2 + (top - bottom) / 2 * math.sin(angle)))
      rings.append(ring)
    for row in range(len(rings) - 1):
      surface = [polygon([rings[row][i], rings[row][(i + 1) % 8],
                           rings[row + 1][(i + 1) % 8],
                           rings[row + 1][i]], sample) for i in range(8)]
      surfaces.append((surface, 0 if row != 0 else 6))
    cuffs = []
    for i in range(8):
      a, b = math.tau * i / 8, math.tau * (i + 1) / 8
      cuffs.append(polygon([(sign * x, .014 - .124 * math.cos(t),
        1.78 + .117 * math.sin(t)) for x, t in [
        (.81, a), (.81, b), (.915, b), (.915, a)]], sample))
    surfaces.append((cuffs, 1))
    # A diagonal overlay gives the dark inner chest its crossed cloth layers.
    inner = [(sign * -.115, -.302, 1.79),
             (sign * -.15, -.309, 1.72),
             (sign * .145, -.325, 1.44),
             (sign * .145, -.321, 1.54)]
    surfaces.append(([polygon(inner, sample)], 6))
  innerSkirt = [(-.145, -.33, 1.24), (.145, -.33, 1.24),
                (.17, -.37, .49), (0, -.40, .40), (-.17, -.37, .49)]
  surfaces.append(([polygon(innerSkirt, lambda p: {'Hips': 1})], 4))
  return finishPart(ctx, 'robe', surfaces, colors,
    'Shared fitted Body torso, waist extrusion and inherited weights')


def belt(ctx, source, colors):
  """Fit the separate leather belt and prominent gold diamond clasp."""
  strap = band(source, [lambda p: p.z - 1.24,
                        lambda p: 1.365 - p.z], .099)
  return finishPart(ctx, 'belt', [(strap, 3),
    (diamond((0, -.393, 1.305), (.22, .07, .29),
              {'Spine': .8, 'Hips': .2}), 5)], colors,
    'Shared fitted Body waist and reusable clothing belt proportions')


def hood(ctx, colors):
  """Create the open blue hood and five solid crystalline crown points."""
  sample = lambda point: {'Head': 1}
  shell = roundedHood(ctx, 'hood', [colors[0], colors[1], colors[4]],
    opening='crowned', rearTrim=True)
  surfaces = []
  bandFaces = []
  hoodTree = BVHTree.FromPolygons(
    [vertex.co for vertex in shell.data.vertices],
    [face.vertices[:] for face in shell.data.polygons])

  def crownPoint(angle, height):
    """Seat the crown above the ivory V instead of across the face opening."""
    front = max(0, math.cos(angle))
    x = .69 * math.sin(angle)
    y = -.01 - .62 * math.cos(angle)
    if front > 0:
      y -= (.69 + y) * min(1, front / math.sqrt(.5))
    notch = -.22 + .13 * min(1, abs(x) * .78 / .20)
    z = 2.65 + (2.96 - 2.65) * .66 + notch * front
    point = Vector((x * .78, y * .90 if y > 0 else y, z))
    if front > .001:
      point, normal, _, _ = hoodTree.find_nearest(point)
      if normal.dot(point - Vector((0, 0, 2.565))) < 0:
        normal = -normal
      point += normal * .012
    point.z += (height - 2.96) * .66
    return (point.x / .78, point.y / .90 if point.y > 0 else point.y,
      2.65 + (point.z - 2.65) / .66)

  for i in range(16):
    a, b = math.tau * i / 16, math.tau * (i + 1) / 16
    bandFaces.append(polygon([
      crownPoint(t, z)
      for t, z in [(a, 2.96), (b, 2.96), (b, 3.10), (a, 3.10)]], sample))
  surfaces.append((bandFaces, 6))
  for x, y, z, width, height in [(0, -.71, 3.15, .24, 1.07),
      (-.43, -.43, 3.24, .14, .50), (.43, -.43, 3.24, .14, .50),
      (-.64, -.13, 3.06, .14, .42), (.64, -.13, 3.06, .14, .42)]:
    surfaces.append((diamond((x, y, z), (width, .07, height), {'Head': 1}),
                     2 if x == 0 else 0))
  obj = finishPart(ctx, 'crown', surfaces, colors,
    'Existing blue crown and cyan crystals on the fitted hood')
  for vertex in obj.data.vertices:
    point = vertex.co
    point.x *= .78
    if point.z > 2.65:
      point.z = 2.65 + (point.z - 2.65) * .66
    if point.y > 0:
      point.y *= .90
  smooth(obj, 38)
  bpy.ops.object.select_all(action='DESELECT')
  for item in [shell, obj]:
    item.hide_set(False)
    item.select_set(True)
  bpy.context.view_layer.objects.active = shell
  bpy.ops.object.join()
  return shell


def build(ctx):
  """Return five independently selectable clothing slots and a human preset."""
  colors = [material(ctx.prefix + name, color) for name, color in [
    ('blue', '#244ed1'), ('ivory', '#eee3c4'), ('cyan', '#18bdfa'),
    ('leather', '#73503c'), ('navy', '#252f57'), ('gold', '#ecb941'),
    ('dark_blue', '#253b8b')]]
  source = bodySurface([ctx.body])
  boots = duplicate(ctx, 'Clothing_14', 'boots',
                    ['#2945a9', '#355dd5', '#2945a9', '#2945a9', '#1c2e75'])
  legs = duplicate(ctx, 'Clothing_09', 'legs', ['#252f57', '#2c3866'])
  for objects, ratio in [(boots, .36), (legs, .48)]:
    for item in objects:
      bpy.context.view_layer.objects.active = item
      modifier = item.modifiers.new('Simplify reused fitted clothing', 'DECIMATE')
      modifier.ratio = ratio
      bpy.ops.object.modifier_apply(modifier=modifier.name)
      if objects is legs:
        for vertex in item.data.vertices:
          point = vertex.co
          allowance = .18 * max(0, min(1, (point.z - .45) / .12))
          allowance *= max(0, min(1, (1.23 - point.z) / .20))
          center = .201 if point.x > 0 else -.201
          point.x = center + (point.x - center) * (1 + allowance)
          point.y *= 1 + allowance
      for face in item.data.polygons:
        face.use_smooth = False
      bind(ctx, item)
  chest = robe(ctx, source, colors)
  waist = belt(ctx, source, colors)
  hat = hood(ctx, colors)
  parts = [part(ctx, 'Foot', 'Gota Lich boots', boots),
           part(ctx, 'Leg', 'Gota Lich trousers', legs),
           part(ctx, 'Belt', 'Gota Lich diamond belt', [waist]),
           part(ctx, 'Chest', 'Gota Lich ivory edged robe', [chest]),
           part(ctx, 'Headgear', 'Gota Lich crystal hood', [hat])]
  preset = dict(name='Lich', group='Gota', pose='A_TPose', skin=18,
    skinRgb=[0.96, 0.9, 0.85], hairColor='White', pupilColor='Blue', parts=[
      dict(category='Hair', item='None'),
      dict(category='Eyes', item='12 Sleepy'),
      dict(category='Mouth', item='03 Neutral'),
      dict(category='Brow', item='03 Focused')])
  return parts, preset
