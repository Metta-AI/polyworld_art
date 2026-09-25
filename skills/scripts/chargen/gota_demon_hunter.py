"""Build the blindfolded Demon Hunter from fitted shared clothing geometry."""

import bpy
from mathutils import Vector

from clothes import band, block, bodySurface, buckle, clip, material, neckline, offset
from garments import finish
from gota_common import bind, duplicate, mesh, part

Charcoal = '#35343d'
Leather = '#4e3d37'
Crimson = '#a92737'
Silver = '#c5c8d0'


def garment(ctx, suffix, surfaces, colors, source):
  """Finish a fitted shell with solid materials and shared skin weights."""
  palette = [material(ctx.prefix + suffix + str(i), value)
             for i, value in enumerate(colors)]
  item = finish(ctx.collection, ctx.prefix + suffix, surfaces, palette, source)
  for face in item.data.polygons:
    face.use_smooth = False
  bind(ctx, item)
  return item


def simplify(ctx, items, ratio):
  """Reduce inherited dense surfaces while retaining deformation groups."""
  for item in items:
    bpy.context.view_layer.objects.active = item
    modifier = item.modifiers.new('Low-poly reduction', 'DECIMATE')
    modifier.ratio = ratio
    modifier.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bind(ctx, item)


def panel(ctx, suffix, outline, color, bone=None):
  """Build an angular closed cloth panel with a shallow raised center fold."""
  points = [Vector(point) for point in outline]
  middle = sum(points, Vector()) / len(points)
  middle.y += -.015 if middle.y < 0 else .015
  vertices = [tuple(point) for point in points] + [tuple(middle)]
  faces = [(i, (i + 1) % len(points), len(points))
           for i in range(len(points))]
  item = mesh(ctx, suffix, vertices, faces, [color], bone=bone)
  thickness = item.modifiers.new('Cloth thickness', 'SOLIDIFY')
  thickness.thickness = .012
  bpy.context.view_layer.objects.active = item
  bpy.ops.object.modifier_apply(modifier=thickness.name)
  bind(ctx, item)
  return item


def build(ctx):
  """Return five separately equipped garment slots and reusable face choices."""
  source = bodySurface([ctx.body])
  parts = []

  boots = duplicate(ctx, 'Clothing_14', 'Boots',
                    [Charcoal, Leather, Leather, Silver, '#232127'])
  for item in boots:
    for face in item.data.polygons:
      face.use_smooth = False
  simplify(ctx, boots, .65)
  cuffSurface = band(source, [lambda p: p.z - .305,
                              lambda p: .505 - p.z], .093)
  boots.append(garment(ctx, 'BootCuffs', [(cuffSurface, 0)],
                       [Leather], 'Body lower leg fitted cuffs'))
  parts.append(part(ctx, 'Foot', 'Gota Demon Hunter boots', boots))

  trousers = duplicate(ctx, 'Clothing_12', 'Trousers',
                        [Charcoal, Charcoal, Leather, Silver, '#232127'])
  for item in list(trousers):
    if item.name.endswith('BootCut0') or item.name.endswith('BootCut1'):
      trousers.remove(item)
      bpy.data.objects.remove(item, do_unlink=True)
    else:
      for face in item.data.polygons:
        face.use_smooth = False
  for sign in [-1, 1]:
    for side, y in [('Front', -.252), ('Back', .252)]:
      for layer, top, bottom in [(0, 1.265, 1.045), (1, 1.085, .860)]:
        outline = [(sign * .15, y, top),
                   (sign * .32, y + (-.015 if y < 0 else .015), top),
                   (sign * .385, y + (-.033 if y < 0 else .033), bottom),
                   (sign * .175, y + (-.025 if y < 0 else .025), bottom + .035)]
        trousers.append(panel(ctx, f'Hip{sign}{side}{layer}', outline,
                              '#414049' if layer == 0 else Charcoal))
  parts.append(part(ctx, 'Leg', 'Gota Demon Hunter leggings', trousers))

  beltSurface = band(source, [lambda p: p.z - 1.255,
                             lambda p: 1.365 - p.z], .095)
  buckleSurface = buckle(beltSurface, 1.31, .17, .15, .032)
  near = min((record for face in beltSurface for record in face),
             key=lambda record: record[0].x ** 2 +
             (record[0].z - 1.31) ** 2 + max(0, record[0].y) ** 2 * 8)
  buckleSurface += block(Vector((.055, near[0].y - .022, 1.31)),
                         (.074, .016, .024), near[2])
  belt = garment(ctx, 'Belt', [(beltSurface, 0),
                 (buckleSurface, 1)],
                 [Leather, Silver], 'Body fitted belt and shared buckle')
  tabard = panel(ctx, 'RedTabard', [(-.108, -.344, 1.275),
                 (.108, -.344, 1.275), (.094, -.352, .790),
                 (.038, -.363, .684), (.0, -.362, .77),
                 (-.064, -.36, .714), (-.097, -.356, .81)], Crimson)
  parts.append(part(ctx, 'Belt', 'Gota Demon Hunter belt', [belt, tabard]))

  top = clip(source, lambda p: p.z - 1.20)
  top = clip(top, lambda p: max(.335 - abs(p.x), 1.56 - p.z))
  top = clip(top, lambda p: neckline(p, 'round'))
  top = offset(top, .060)
  surfaces = [(top, 0)]
  for sign in [-1, 1]:
    strap = band(top, [lambda p: p.z - 1.32,
                      lambda p: 1.88 - p.z,
                      lambda p, s=sign: .058 - abs(p.x - s * (p.z - 1.59) * .88)],
                      .017)
    surfaces.append((strap, 1))
  # Reuse the body's fitted forearm surface for both short wrist guards.
  cuffs = band(source, [lambda p: abs(p.x) - .75,
                        lambda p: .965 - abs(p.x)], .034)
  surfaces.append((cuffs, 1))
  torso = garment(ctx, 'Body', surfaces, [Charcoal, Leather], 'Body with Clothing_06 sleeveless pattern')
  scarfSurface = band(source, [lambda p: p.z - 1.85,
                              lambda p: 2.065 - p.z,
                              lambda p: .28 - abs(p.x)], .047)
  scarf = garment(ctx, 'Scarf', [(scarfSurface, 0)], [Crimson], 'Body neck')
  scarfFront = panel(ctx, 'ScarfFront', [(-.205, -.263, 1.955),
               (.205, -.263, 1.955), (.19, -.287, 1.86),
               (0, -.296, 1.775), (-.19, -.287, 1.86)], Crimson)
  scarfFold = panel(ctx, 'ScarfFold', [(-.20, -.276, 1.952),
               (.20, -.276, 1.952), (.01, -.313, 1.882),
               (-.16, -.300, 1.90)], '#bd3040')
  scarfBack = panel(ctx, 'ScarfBack', [(-.17, .262, 1.97),
              (.17, .262, 1.97), (.15, .278, 1.865),
              (0, .283, 1.82), (-.15, .278, 1.865)], Crimson)
  gloves = duplicate(ctx, 'Hand.Left', 'GloveLeft', [Leather])
  gloves += duplicate(ctx, 'Hand.Right', 'GloveRight', [Leather])
  simplify(ctx, gloves, .35)
  parts.append(part(ctx, 'Chest', 'Gota Demon Hunter harness',
                   [torso, scarf, scarfFront, scarfFold, scarfBack] + gloves,
                   hides=['Hand.Left', 'Hand.Right']))

  headSurface = bodySurface([bpy.data.objects['Head']])
  blindfoldSurface = band(headSurface, [lambda p: p.z - 2.37,
                                      lambda p: 2.66 - p.z], .047)
  blindfold = garment(ctx, 'Blindfold', [(blindfoldSurface, 0)],
                       [Crimson], 'Head fitted eye covering')
  frontCurve = [(-.50, -.25), (-.40, -.47), (-.25, -.55),
                (0, -.574), (.25, -.55), (.40, -.47), (.50, -.25)]
  vertices = [(x, y, level - x * .24) for level in [2.615, 2.455]
              for x, y in frontCurve]
  crossing = mesh(ctx, 'BlindfoldOverlap', vertices,
                  [(i, i + 1, i + 8, i + 7) for i in range(6)],
                  ['#b92b3c'], bone='Head')
  thickness = crossing.modifiers.new('Fold thickness', 'SOLIDIFY')
  thickness.thickness = .012
  bpy.context.view_layer.objects.active = crossing
  bpy.ops.object.modifier_apply(modifier=thickness.name)
  bind(ctx, crossing)
  knot = panel(ctx, 'BlindfoldKnot', [(-.095, .60, 2.61), (.095, .60, 2.61),
               (.10, .62, 2.43), (-.075, .62, 2.43)], '#96212e', bone='Head')
  tails = []
  for sign in [-1, 1]:
    tails.append(panel(ctx, f'BlindfoldTail{sign}',
                 [(sign * .025, .61, 2.48), (sign * .09, .61, 2.48),
                  (sign * .19, .63, 2.22), (sign * .10, .65, 2.14),
                  (sign * .06, .63, 2.30)], Crimson, bone='Head'))
  parts.append(part(ctx, 'Headgear', 'Gota Demon Hunter blindfold',
                   [blindfold, crossing, knot] + tails,
                   hides=['Eyes_Atlas02', 'Brow_Atlas04']))

  # Retain the fitted pixie scalp and augment its silhouette with broad spikes.
  hair = duplicate(ctx, 'Hair_13', 'HairBase', ['#25242b'])
  simplify(ctx, hair, .55)
  for item in hair:
    for face in item.data.polygons:
      face.use_smooth = False
  spikes = [
    ((-.30, -.12, 2.96), (-.46, -.16, 3.40), .21),
    ((-.03, -.12, 3.05), (.14, -.12, 3.42), .23),
    ((.23, -.09, 3.01), (.51, -.10, 3.38), .24),
    ((.42, -.06, 2.91), (.78, -.08, 3.11), .23),
    ((-.46, -.05, 2.86), (-.77, -.1, 2.98), .23),
    ((.46, .13, 2.76), (.78, .22, 2.78), .20),
    ((-.47, .15, 2.72), (-.76, .25, 2.66), .20),
    ((.0, .39, 3.0), (.10, .64, 3.34), .23),
  ]
  for i, (base, tip, width) in enumerate(spikes):
    base = Vector(base)
    tip = Vector(tip)
    axis = (tip - base).normalized()
    across = axis.cross(Vector((0, 1, 0))).normalized()
    depth = axis.cross(across).normalized()
    vertices = [tuple(base + across * width),
                tuple(base + depth * width * .58),
                tuple(base - across * width),
                tuple(base - depth * width * .58), tuple(tip)]
    hair.append(mesh(ctx, f'HairSpike{i}', vertices,
                [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (3, 2, 1, 0)],
                ['#25242b'], bone='Head'))
  parts.append(part(ctx, 'Hair', 'Gota Demon Hunter spiky hair', hair))
  preset = dict(name='Demon Hunter', group='Gota', pose='A_TPose', skin=14,
                hairColor='Jet black', pupilColor='Brown', parts=[
                  dict(category='Eyes', item='02 Focused'),
                  dict(category='Mouth', item='03 Neutral'),
                  dict(category='Brow', item='04 Heroic')])
  return parts, preset
