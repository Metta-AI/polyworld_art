"""Build fitted purple Arcanist clothing on the shared character rig."""

import math

import bpy
from mathutils import Vector

from clothes import band, bodySurface, clip, hemExtrusion, material, offset
from clothes import sourceWeights
from garments import finish
from gota_common import bind, duplicate, part


Slug = 'arcanist'
Prefix = 'gota_arcanist_'


def palette():
  """Keep the Arcanist palette as solid matte colors."""
  return [material(Prefix + 'violet', '#37215d'),
          material(Prefix + 'lilac', '#9652d6'),
          material(Prefix + 'amethyst', '#9039ff'),
          material(Prefix + 'leather', '#70513d'),
          material(Prefix + 'deep', '#241837'),
          material(Prefix + 'white', '#e0d4ed')]


def polygon(points, sample):
  """Attach a polygon to the nearest fitted body skin weights."""
  points = [Vector(point) for point in points]
  normal = (points[1] - points[0]).cross(points[2] - points[0]).normalized()
  return [(point, normal, sample(point)) for point in points]


def gem(x, y, z, width, height, depth, weights):
  """Create a faceted diamond fixed to the clothing surface."""
  points = [Vector((x, y, z + height / 2)),
            Vector((x + width / 2, y, z)),
            Vector((x, y, z - height / 2)),
            Vector((x - width / 2, y, z)),
            Vector((x, y - depth, z)),
            Vector((x, y + depth * .3, z))]
  result = []
  for center in [4, 5]:
    for i in range(4):
      indices = [i, (i + 1) % 4, center]
      face = [points[j] for j in indices]
      normal = (face[1] - face[0]).cross(face[2] - face[0]).normalized()
      result.append([(point, normal, weights) for point in face])
  return result


def robe(collection, source, colors):
  """Fit the torso and add broad bell sleeves with a split flared skirt."""
  sample = sourceWeights(source)
  torso = clip(source, lambda p: p.z - 1.22)
  torso = clip(torso, lambda p: .345 - abs(p.x))
  torso = clip(torso, lambda p: 1.925 - p.z)
  torso = offset(torso, .050)
  skirt = clip(source, lambda p: p.z - 1.22)
  skirt = clip(skirt, lambda p: 1.36 - p.z)
  skirt = hemExtrusion(skirt, 1.22, .56, sample)
  shaped = []
  for face in skirt:
    records = []
    for p, n, w in face:
      t = max(0, (1.24 - p.z) / .68)
      q = p + n * .066
      q.x *= 1 + .42 * t
      q.y *= 1 + .15 * t
      if p.z < 1.24:
        blend = min(1, max(0, (1.24 - p.z) / .68))
        left = min(1, max(0, (p.x + .09) / .18))
        w = {'Hips': 1 - blend, 'LeftUpLeg': blend * left,
             'RightUpLeg': blend * (1 - left)}
      records.append((q, n, w))
    shaped.append(records)

  def opening(p):
    """Keep a widening front robe split while the back stays continuous."""
    gap = .018 + max(0, 1.28 - p.z) * .14
    return max(p.z - 1.22, abs(p.x) - gap)

  skirt = clip(shaped, opening)
  upperSkirt = clip(skirt, lambda p: p.z - .672)
  hem = clip(skirt, lambda p: .672 - p.z)
  frontTrim = clip(clip(upperSkirt, lambda p: -p.y - .08),
                    lambda p: .081 - opening(p))
  mainSkirt = clip(upperSkirt,
                    lambda p: max(p.y + .08, opening(p) - .081))
  surfaces = [(torso, 0), (mainSkirt, 0), (hem, 1), (frontTrim, 1)]
  for sign in [-1, 1]:
    rings = []
    for x, width, bottom in [(.345, .155, 1.565),
                             (.46, .172, 1.52),
                             (.70, .222, 1.355),
                             (.79, .235, 1.325)]:
      ring = []
      top = 1.942 - (x - .345) * .16
      middle = (top + bottom) / 2
      radius = (top - bottom) / 2
      for i in range(12):
        angle = math.tau * i / 12
        ring.append(Vector((sign * x, .01 - width * math.cos(angle),
                            middle + radius * math.sin(angle))))
      rings.append(ring)
    for row in range(len(rings) - 1):
      sleeve = []
      for i in range(12):
        points = [rings[row][i], rings[row][(i + 1) % 12],
                  rings[row + 1][(i + 1) % 12], rings[row + 1][i]]
        sleeve.append(polygon(points, sample))
      surfaces.append((sleeve, 1 if row in [0, 2] else 0))
    collar = [
      (sign * .04, -.35, 1.96), (sign * .17, -.35, 1.96),
      (sign * .28, -.35, 1.85), (sign * .16, -.35, 1.745),
      (sign * .07, -.35, 1.845)]
    if sign > 0:
      collar.reverse()
    surfaces.append(([polygon(collar, sample)], 1))
  surfaces.append((gem(0, -.306, 1.76, .16, .24, .05,
                        {'Spine2': 1}), 2))
  item = finish(collection, Prefix + 'robe', surfaces, colors,
                'Body fitted torso and inherited skin weights')
  for face in item.data.polygons:
    face.use_smooth = False
  return item


def waist(collection, source, colors):
  """Fit a separate brown belt carrying the large purple diamond buckle."""
  strap = band(source, [lambda p: p.z - 1.258,
                        lambda p: 1.367 - p.z], .091)
  result = finish(collection, Prefix + 'belt', [
    (strap, 3), (gem(0, -.382, 1.304, .21, .315, .064,
                     {'Spine': .8, 'Hips': .2}), 2)], colors,
    'Body fitted waist and existing Gnome belt proportions')
  for face in result.data.polygons:
    face.use_smooth = False
  return result


def circlet(collection, colors):
  """Attach a forehead diamond to a fine band beneath the existing hair."""
  surfaces = []
  sample = lambda point: {'Head': 1}
  for i in range(24):
    a, b = math.tau * i / 24, math.tau * (i + 1) / 24
    points = []
    for angle, z in [(a, 2.718), (b, 2.718), (b, 2.745), (a, 2.745)]:
      points.append((.521 * math.sin(angle),
                     .025 - .56 * math.cos(angle), z))
    surfaces.append(polygon(points, sample))
  result = finish(collection, Prefix + 'circlet', [
    (surfaces, 5), (gem(0, -.596, 2.705, .145, .24, .044,
                       {'Head': 1}), 2)], colors,
    'Thin headband fitted to shared Head')
  for face in result.data.polygons:
    face.use_smooth = False
  return result


def simplify(items, ratio):
  """Reduce copied clothing to broad facets while retaining its fitted form."""
  for item in items:
    bpy.context.view_layer.objects.active = item
    modifier = item.modifiers.new('Broad untextured facets', 'DECIMATE')
    modifier.ratio = ratio
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    for face in item.data.polygons:
      face.use_smooth = False


def build(ctx):
  """Return independently selectable Arcanist clothes and reused face parts."""
  global Prefix
  Prefix = ctx.prefix
  colors = palette()
  source = bodySurface([ctx.body])
  boots = duplicate(ctx, 'Clothing_13', 'boots',
                    ['#392465', '#7246a6', '#7042a0', '#7042a0', '#291b40'])
  simplify(boots, .36)
  legs = duplicate(ctx, 'Clothing_09', 'legs',
                   ['#2e2048', '#2e2048', '#2e2048', '#2e2048', '#2e2048'])
  for item in list(legs):
    if item.name.endswith('_BootCut0'):
      legs.remove(item)
      bpy.data.objects.remove(item, do_unlink=True)
  simplify(legs, .40)
  footSource = bodySurface([ctx.body, bpy.data.objects['Foot.Left'],
                           bpy.data.objects['Foot.Right']])
  sample = sourceWeights(footSource)
  caps = []
  for sign in [-1, 1]:
    x = sign * .225
    corners = [(x - .105, -.172, .17), (x, -.231, .157),
               (x + .105, -.172, .17), (x, -.066, .27)]
    peak = (x, -.155, .252)
    for i in range(4):
      caps.append(polygon([corners[i], corners[(i + 1) % 4], peak], sample))
  insteps = finish(ctx.collection, Prefix + 'insteps', [(caps, 1)], colors,
                    'Angular instep caps on reused Clothing_13 boots')
  for face in insteps.data.polygons:
    face.use_smooth = False
  boots.append(insteps)
  top = robe(ctx.collection, source, colors)
  belt = waist(ctx.collection, source, colors)
  hat = circlet(ctx.collection, colors)
  for item in boots + legs + [top, belt, hat]:
    bind(ctx, item)
  parts = [part(ctx, 'Foot', 'Gota Arcanist boots', boots),
           part(ctx, 'Leg', 'Gota Arcanist leggings', legs),
           part(ctx, 'Belt', 'Gota Arcanist amethyst belt', [belt]),
           part(ctx, 'Chest', 'Gota Arcanist violet robe', [top]),
           part(ctx, 'Headgear', 'Gota Arcanist circlet', [hat])]
  preset = dict(name='Arcanist', group='Gota', pose='A_TPose', skin=20,
                hairColor='White', pupilColor='Blue', parts=[
    dict(category='Hair', item='12 Wolf cut'),
    dict(category='Eyes', item='01 Bright'),
    dict(category='Mouth', item='03 Neutral'),
    dict(category='Brow', item='01 Soft arch'),
    dict(category='Ears', item='Round')])
  return parts, preset
