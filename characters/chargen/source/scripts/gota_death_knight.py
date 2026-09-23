"""Build modular Death Knight clothing on the existing Polyworld rig."""

import math

from mathutils import Vector

from clothes import bodySurface, clip, meshObject, offset, material
from gota_common import duplicate, mesh, bind, part, smooth, fitHead

Steel = '#515563'
Edge = '#676C7C'
Dark = '#2C2E3A'
Cape = '#23283E'
Cyan = '#12BCED'


def plate(ctx, suffix, outline, color=Steel, depth=.026, bone=None):
  """Make a solid angular armor plate with a shallow central ridge."""
  points = [Vector(p) for p in outline]
  center = sum(points, Vector()) / len(points)
  center.y -= depth
  count = len(points)
  vertices = points + [center] + [p + Vector((0, depth, 0)) for p in points]
  faces = [(i, (i + 1) % count, count) for i in range(count)]
  faces.append(tuple(range(count + 1, count * 2 + 1)))
  for i in range(count):
    j = (i + 1) % count
    faces.append((j, i, count + 1 + i, count + 1 + j))
  return mesh(ctx, suffix, vertices, faces, [color], bone=bone)


def diamond(ctx, suffix, center, width, height, color=Cyan, bone=None):
  """Create a small solid faceted diamond with no emission or texture."""
  x, y, z = center
  return plate(ctx, suffix, [(x, y, z + height), (x + width, y, z),
    (x, y, z - height), (x - width, y, z)], color, .055, bone)


def spike(ctx, suffix, center, radius, height, bone):
  """Add a five-sided tapered armor spike with one subtle bent tip."""
  x, y, z = center
  vertices = [(x + radius * math.cos(i * math.tau / 5),
    y + radius * math.sin(i * math.tau / 5), z) for i in range(5)]
  vertices.append((x * 1.08, y, z + height))
  faces = [(i, (i + 1) % 5, 5) for i in range(5)]
  faces.append((4, 3, 2, 1, 0))
  return mesh(ctx, suffix, vertices, faces, [Steel], bone=bone)


def fitted(ctx, source, suffix, cuts, amount, color):
  """Reuse fitted geometry and its skin weights for an untextured shell."""
  surface = bodySurface(source)
  for cut in cuts:
    surface = clip(surface, cut)
  surface = offset(surface, amount)
  obj = meshObject(ctx.collection, ctx.prefix + suffix, [(surface, 0)],
    [material(ctx.prefix + suffix + '_Material', color)])
  for face in obj.data.polygons:
    face.use_smooth = False
  obj['derivedFrom'] = ', '.join(o.name for o in source)
  bind(ctx, obj)
  return smooth(obj)


def helmet(ctx):
  """Frame the eyes with a low brow and stepped guards over a full shell."""
  import bpy
  from mathutils.bvhtree import BVHTree

  # Each half arch runs from the jaw opening up to the center of the crown.
  profiles = [
    [(.29, 1.90), (.30, 2.08), (.30, 2.18), (.465, 2.275),
     (.48, 2.42), (.435, 2.52), (.22, 2.445), (0, 2.38)],
    [(.37, 1.92), (.48, 2.08), (.49, 2.20), (.525, 2.31),
     (.53, 2.46), (.48, 2.755), (.24, 2.705), (0, 2.625)]
  ]
  head = bpy.data.objects['Head'].data
  tree = BVHTree.FromPolygons([vertex.co for vertex in head.vertices],
    [face.vertices[:] for face in head.polygons])
  arches = []
  for profile in profiles:
    arch = []
    for x, z in profile:
      # Follow the face depth while preserving the angular front silhouette.
      origin = Vector((min(x, .43), -2, max(z, 2.08)))
      point, normal, index, distance = tree.ray_cast(origin, Vector((0, 1, 0)))
      if point is None:
        origin.x = min(x, .34)
        point, normal, index, distance = tree.ray_cast(origin, Vector((0, 1, 0)))
      assert point is not None, (x, z)
      depth = point.y - .065 / max(.65, -normal.y)
      arch.append((x, depth, z))
    arches.append(arch)
  arches += [
    [(.48, -.250, 1.95), (.545, -.240, 2.14),
     (.565, -.235, 2.27), (.595, -.220, 2.44),
     (.605, -.210, 2.62), (.54, -.270, 2.91),
     (.28, -.350, 3.055), (0, -.370, 3.085)],
    [(.49, .125, 1.95), (.55, .125, 2.17),
     (.575, .160, 2.36), (.59, .200, 2.55),
     (.58, .210, 2.75), (.48, .150, 2.98),
     (.25, .150, 3.10), (0, .150, 3.115)],
    [(.29, .470, 1.95), (.355, .500, 2.17),
     (.40, .530, 2.36), (.40, .530, 2.57),
     (.40, .490, 2.78), (.33, .435, 2.995),
     (.19, .425, 3.03), (0, .400, 3.06)]
  ]
  vertices, faces = [], []
  columns = len(arches[0]) * 2 - 1
  for row, arch in enumerate(arches):
    vertices += [(-x, y, z) for x, y, z in arch]
    vertices += list(reversed(arch[:-1]))
    if row:
      for column in range(columns - 1):
        a = (row - 1) * columns + column
        faces.append((a, a + 1, a + columns + 1, a + columns))
  rear = (len(arches) - 1) * columns
  pole = len(vertices)
  vertices.append((0, .665, 2.67))
  for column in range(columns - 1):
    faces.append((rear + column, rear + column + 1, pole))
  bottom = len(vertices)
  vertices.append((0, .505, 1.95))
  faces += [(rear + columns - 1, bottom, pole), (bottom, rear, pole)]
  shell = mesh(ctx, 'HelmetShell', vertices, faces,
    [Steel, Edge, Dark], bone='Head')
  for face in shell.data.polygons[:columns - 1]:
    face.material_index = 1
  fitHead(shell, subdivide=True)
  bpy.context.view_layer.objects.active = shell
  thickness = shell.modifiers.new('Solid helmet rim', 'SOLIDIFY')
  thickness.thickness = .024
  thickness.offset = -1
  thickness.material_offset = 2
  bpy.ops.object.modifier_apply(modifier=thickness.name)
  smooth(shell, 50)
  shell['construction'] = 'Low brow, stepped cheek guards and full rear coverage'
  return [shell]


def build(ctx):
  """Return five skinned wearable modules and the dark human hero preset."""
  import bpy

  boots = duplicate(ctx, 'Clothing_15', 'Boots',
    [Steel, Edge, Dark, Edge, Dark])
  legs = duplicate(ctx, 'Clothing_09', 'Legs',
    [Dark, Dark, Dark, Edge, Dark])
  for obj in boots + legs:
    smooth(obj)
  # The tall reused boots hide all trousers below their cuff.
  for obj in list(legs):
    if max(v.co.z for v in obj.data.vertices) <= .60:
      legs.remove(obj)
      bpy.data.objects.remove(obj, do_unlink=True)
  for sign, side in [(1, 'Left'), (-1, 'Right')]:
    x = sign * .205
    boots.append(plate(ctx, 'Shin_' + side,
      [(x - .105, -.16, .54), (x, -.19, .64),
       (x + .105, -.16, .54), (x + .095, -.20, .32),
       (x, -.23, .26), (x - .095, -.20, .32)], Edge))
    boots.append(diamond(ctx, 'KneeGem_' + side, (x, -.21, .53), .050, .080))
    boots.append(plate(ctx, 'Toe_' + side,
      [(x - .105, -.265, .085), (x - .100, -.25, .18),
       (x + .100, -.25, .18), (x + .105, -.265, .085)], Steel))
    for index, (top, low, width) in enumerate([(1.23, 1.04, .13),
                                              (1.045, .78, .14)]):
      legs.append(plate(ctx, 'Tasset_' + side + str(index),
        [(x - width, -.25, top), (x + width, -.25, top),
         (x + width + .02, -.285, low + .03),
         (x, -.30, low), (x - width - .02, -.285, low + .03)],
        Edge if index == 0 else Steel))
  legs.append(plate(ctx, 'Tabard', [(-.12, -.315, 1.27),
    (.12, -.315, 1.27), (.14, -.34, .72), (0, -.35, .60),
    (-.14, -.34, .72)], Cape, .012, 'Hips'))
  legs.append(diamond(ctx, 'TabardGem', (0, -.372, .78), .045, .064,
    '#285BDF', 'Hips'))

  belt = [fitted(ctx, [ctx.body], 'Belt',
    [lambda p: p.z - 1.255, lambda p: 1.36 - p.z], .088, Dark)]
  belt.append(diamond(ctx, 'Buckle', (0, -.347, 1.308), .110, .130,
    Edge, 'Spine'))
  for sign in [-1, 1]:
    x = sign * .225
    belt.append(plate(ctx, 'BeltPlate_' + str(sign),
      [(x - .055, -.308, 1.355), (x + .055, -.308, 1.355),
       (x + .055, -.316, 1.255), (x - .055, -.316, 1.255)],
      Steel, .026, 'Spine'))

  chest = [fitted(ctx, [bpy.data.objects['Clothing_07']], 'Undersuit',
    [lambda p: p.z - 1.345], .012, Dark)]
  chest.append(plate(ctx, 'Cuirass', [(-.255, -.275, 1.855),
    (-.12, -.29, 1.925), (.12, -.29, 1.925), (.255, -.275, 1.855),
    (.28, -.292, 1.575), (.18, -.325, 1.44), (0, -.34, 1.405),
    (-.18, -.325, 1.44), (-.28, -.292, 1.575)], Steel, .035))
  chest.append(plate(ctx, 'Breastplate', [(-.225, -.30, 1.81),
    (0, -.343, 1.9), (.225, -.30, 1.81), (.235, -.323, 1.665),
    (0, -.385, 1.60), (-.235, -.323, 1.665)], Edge, .022))
  chest.append(diamond(ctx, 'ChestGem', (0, -.422, 1.738), .068, .118))
  chest.append(plate(ctx, 'AbdomenUpper', [(-.26, -.34, 1.66),
    (0, -.405, 1.60), (.26, -.34, 1.66), (.24, -.36, 1.50),
    (0, -.405, 1.44), (-.24, -.36, 1.50)], Steel, .020))
  chest.append(plate(ctx, 'AbdomenLower', [(-.24, -.355, 1.505),
    (0, -.416, 1.455), (.24, -.355, 1.505), (.21, -.36, 1.37),
    (0, -.41, 1.335), (-.21, -.36, 1.37)], Edge, .016))
  for sign, side in [(1, 'Left'), (-1, 'Right')]:
    chest.append(plate(ctx, 'Pauldron_' + side,
      [(sign * .265, -.11, 1.875), (sign * .43, -.04, 2.005),
       (sign * .68, -.03, 1.93), (sign * .62, -.235, 1.79),
       (sign * .43, -.265, 1.735), (sign * .27, -.22, 1.79)],
       Edge, .055, side + 'Arm'))
    chest.append(plate(ctx, 'PauldronBack_' + side,
      [(sign * .27, .06, 1.88), (sign * .43, .06, 2.00),
       (sign * .68, .06, 1.93), (sign * .62, .225, 1.79),
       (sign * .43, .245, 1.735), (sign * .27, .20, 1.79)],
       Steel, .040, side + 'Arm'))
    chest.append(spike(ctx, 'ShoulderSpike_' + side,
      (sign * .635, .01, 1.965), .060, .18, side + 'Arm'))
    chest.append(fitted(ctx, [ctx.body], 'Vambrace_' + side,
      [lambda p, s=sign: s * p.x - .74,
       lambda p, s=sign: .98 - s * p.x], .063, Steel))
    chest.append(fitted(ctx, [bpy.data.objects['Hand.' + side]],
      'Glove_' + side, [], .017, Steel))
  # The cape remains broad and low poly, with a divided angular hem.
  capePoints = [(-.34, .20, 1.91), (0, .30, 1.87), (.34, .20, 1.91),
    (-.45, .32, 1.25), (0, .40, 1.22), (.45, .32, 1.25),
    (-.65, .40, .48), (-.40, .44, .57), (-.20, .46, .40),
    (0, .46, .60), (.20, .46, .40), (.40, .44, .57), (.65, .40, .48)]
  capeFaces = [(0, 1, 4), (0, 4, 3), (1, 2, 5), (1, 5, 4),
    (3, 4, 8), (3, 8, 7), (3, 7, 6), (4, 9, 8),
    (4, 10, 9), (4, 5, 10), (5, 11, 10), (5, 12, 11)]
  chest.append(mesh(ctx, 'Cape', capePoints, capeFaces, [Cape], bone='Spine2'))

  hat = helmet(ctx)
  for index, (x, y, z, radius, height) in enumerate([
    (0, .01, 3.065, .095, .41),
    (-.32, .035, 2.995, .075, .32),
    (.32, .035, 2.995, .075, .32),
    (-.55, -.20, 2.80, .080, .355),
    (.55, -.20, 2.80, .080, .355)]):
    hat.append(spike(ctx, 'CrownSpike_' + str(index),
      (x, y, z), radius, height, 'Head'))
  gem = diamond(ctx, 'ForeheadGem', (0, -.545, 2.76),
    .081, .170, Cyan, 'Head')
  for vertex in gem.data.vertices:
    depth, height = vertex.co.y + .545, vertex.co.z - 2.76
    vertex.co.y = -.545 + depth * math.cos(.44) + height * math.sin(.44)
    vertex.co.z = 2.76 - depth * math.sin(.44) + height * math.cos(.44)
  gem.data.update()
  hat.append(gem)

  parts = [part(ctx, 'Foot', 'Gota Death Knight armored boots', boots),
    part(ctx, 'Leg', 'Gota Death Knight tassets', legs),
    part(ctx, 'Belt', 'Gota Death Knight steel belt', belt),
    part(ctx, 'Chest', 'Gota Death Knight cuirass and cape', chest,
      hides=['Hand.Left', 'Hand.Right']),
    part(ctx, 'Headgear', 'Gota Death Knight open crown', hat)]
  preset = dict(name='Death Knight', group='Gota', pose='A_TPose',
    skin=2, skinRgb=[0.34, 0.18, 0.11], hairColor='Jet black', pupilColor='Brown',
    parts=[dict(category='Eyes', item='14 Angular'),
      dict(category='Mouth', item='03 Neutral'),
      dict(category='Brow', item='08 Stern')])
  return parts, preset
