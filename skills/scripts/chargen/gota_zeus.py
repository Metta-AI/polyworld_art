"""Build Zeus as independent solid-color modules on the shared Gota rig."""

import math

import bpy
from mathutils import Vector

from clothes import band, bodySurface, clip, material, meshObject, offset
from gota_common import bind, mesh, part, smooth


def build(ctx):
  """Assemble Zeus clothing and equipment without altering the base character."""
  from gota_zeus_head import build as head
  from gota_zeus_legs import build as legs
  from gota_zeus_props import build as props

  ivory = material(ctx.prefix + 'Ivory', '#f1ebdf')
  ivoryShade = material(ctx.prefix + 'IvoryShadow', '#d9d2c7')
  gold = material(ctx.prefix + 'Gold', '#e6ad36')
  goldLight = material(ctx.prefix + 'GoldLight', '#f6cc58')
  goldDark = material(ctx.prefix + 'GoldShadow', '#a87522')
  blue = material(ctx.prefix + 'RoyalBlue', '#235fd4')
  blueDark = material(ctx.prefix + 'BlueFold', '#2053b4')
  blueLight = material(ctx.prefix + 'BlueGem', '#248fef')
  leather = material(ctx.prefix + 'Leather', '#705331')
  source = bodySurface([ctx.body])

  def surface(label, records, color):
    """Keep a garment surface fitted to the original weighted body."""
    obj = meshObject(ctx.collection, ctx.prefix + label, [(records, 0)], [color])
    bind(ctx, obj)
    return smooth(obj, 60)

  def solid(label, points, y, depth, color, bone=None):
    """Extrude a front-facing relief silhouette with a broad face."""
    n = len(points)
    vertices = [(x, y, z) for x, z in points]
    vertices += [(x, y + depth, z) for x, z in points]
    faces = [tuple(reversed(range(n))), tuple(range(n, n * 2))]
    faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n)
              for i in range(n)]
    return mesh(ctx, label, vertices, faces, [color], bone=bone)

  def diamond(label, x, y, z, width, height, color, bone=None):
    """Make a faceted jewel with a pointed front and solid back."""
    vertices = [(x, y, z + height), (x + width, y, z),
                (x, y, z - height), (x - width, y, z),
                (x, y - width * .48, z), (x, y + .008, z)]
    faces = [(i, (i + 1) % 4, center) for center in [4, 5]
             for i in range(4)]
    return mesh(ctx, label, vertices, faces, [color], bone=bone)

  def medallion(label, x, y, z, radius, bone=None):
    """Make a round beveled gold eagle brooch without texture detail."""
    vertices, faces, shades = [], [], []
    rings = [(radius * .91, y + .028), (radius, y + .013),
             (radius, y - .008), (radius * .85, y - .022),
             (radius * .77, y - .023)]
    sides = 28
    for r, depth in rings:
      for i in range(sides):
        a = math.tau * i / sides
        vertices.append((x + math.cos(a) * r, depth,
                         z + math.sin(a) * r))
    for row in range(len(rings) - 1):
      for i in range(sides):
        a, b = row * sides + i, row * sides + (i + 1) % sides
        faces.append((a, b, b + sides, a + sides))
        shades.append(0 if row in [1, 2] else 1)
    faces += [tuple(reversed(range(sides))),
              tuple(range((len(rings) - 1) * sides, len(rings) * sides))]
    shades += [1, 2]
    disc = mesh(ctx, label + 'Round', vertices, faces,
                [goldLight, gold, goldDark], bone=bone)
    smooth(disc, 45)
    for face, shade in zip(disc.data.polygons, shades):
      face.material_index = shade
    # The eagle has two broad wings and a single tapered tail.
    outline = [(0, .65), (.16, .60), (.25, .48), (.12, .47),
               (.11, .30), (.28, .20),
               (.67, .53), (.70, .24), (.58, .10), (.65, .00),
               (.47, -.09), (.51, -.19), (.30, -.20), (.22, -.09),
               (.19, -.29), (.27, -.54), (.09, -.42), (0, -.68),
               (-.09, -.42), (-.27, -.54), (-.19, -.29), (-.22, -.09),
               (-.30, -.20), (-.51, -.19), (-.47, -.09), (-.65, .00),
               (-.58, .10), (-.70, .24), (-.67, .53), (-.28, .20),
               (-.11, .30), (-.12, .55)]
    eagle = solid(label + 'Eagle', [(x + px * radius, z + pz * radius)
                  for px, pz in outline], y - .038, .015, goldLight, bone)
    return [disc, eagle]

  shell = clip(source, lambda p: p.z - 1.27)
  shell = clip(shell, lambda p: 1.93 - p.z)
  shell = clip(shell, lambda p: .345 - abs(p.x))
  tunic = [surface('TunicShell', offset(shell, .070), ivory)]
  for sign in [-1, 1]:
    # Gold trim is a single continuous edge underneath the wider blue lapel.
    points = [(sign * .203, 1.96), (sign * .349, 1.91),
              (sign * .075, 1.42), (0, 1.36), (sign * -.035, 1.45)]
    tunic.append(solid('LapelGold' + str(sign), points, -.350, .025, gold))
    points = [(sign * .212, 1.94), (sign * .316, 1.905),
              (sign * .055, 1.45), (0, 1.415), (sign * -.006, 1.46)]
    tunic.append(solid('LapelBlue' + str(sign), points, -.366, .018, blue))
    # Attach broad circular eagle clasps in front of each shoulder.
    tunic += medallion('Shoulder' + str(sign), sign * .345,
                       -.272, 1.855, .122)
    # Soft shoulder strips give the cape a visible attachment from the rear.
    vertices = [(sign * .24, -.17, 1.96), (sign * .44, -.12, 1.965),
                (sign * .47, .15, 1.95), (sign * .27, .235, 1.935)]
    tunic.append(mesh(ctx, 'ShoulderBlue' + str(sign), vertices,
                      [(0, 1, 2, 3)], [blue]))
    arm = clip(source, lambda p, s=sign: s * p.x - .735)
    arm = clip(arm, lambda p, s=sign: .94 - s * p.x)
    tunic.append(surface('Cuff' + str(sign), offset(arm, .043), gold))
    for index, (lo, hi) in enumerate([(.731, .763), (.913, .946)]):
      edge = clip(source, lambda p, s=sign, v=lo: s * p.x - v)
      edge = clip(edge, lambda p, s=sign, v=hi: v - s * p.x)
      tunic.append(surface('CuffRim' + str(sign) + str(index),
                           offset(edge, .060), goldLight))
    bone = 'LeftForeArm' if sign > 0 else 'RightForeArm'
    tunic.append(diamond('CuffGemRim' + str(sign), sign * .835,
                          -.134, 1.795, .075, .063, goldLight, bone))
    tunic.append(diamond('CuffGem' + str(sign), sign * .835,
                          -.152, 1.795, .051, .044, blueLight, bone))

  beltShell = band(source, [lambda p: p.z - 1.265,
                            lambda p: 1.395 - p.z], .099)
  belt = [surface('BeltLeather', beltShell, leather)]
  for index, (lo, hi) in enumerate([(1.259, 1.289), (1.37, 1.40)]):
    records = band(source, [lambda p, low=lo: p.z - low,
                            lambda p, high=hi: high - p.z], .115)
    belt.append(surface('BeltRim' + str(index), records, gold))
  belt += medallion('BeltBuckle', 0, -.395, 1.324, .154, 'Hips')
  for sign in [-1, 1]:
    belt.append(solid('BeltLoop' + str(sign),
      [(sign * .22, 1.383), (sign * .246, 1.377),
       (sign * .246, 1.282), (sign * .22, 1.282)], -.355, .022, gold))

  # A continuous shoulder-to-calf cape with smooth folded columns and a gold hem.
  rows = [(1.885, .32, .265), (1.79, .385, .30), (1.58, .46, .342),
          (1.30, .53, .37), (1.04, .63, .40), (.75, .72, .425),
          (.55, .79, .448), (.47, .815, .46), (.42, .825, .47)]
  columns = 17
  verts, faces, shades, weights = [], [], [], []
  for row, (z, width, depth) in enumerate(rows):
    for col in range(columns):
      t = col / (columns - 1) * 2 - 1
      fold = .045 * math.cos(t * math.pi * 4)
      verts.append((width * t, depth + .095 + fold, z + .065 * abs(t)))
      influence = min(1, max(0, (1.83 - z) / .65))
      weights.append({'Spine2': 1 - influence, 'Hips': influence})
      if row and col:
        a = (row - 1) * columns + col - 1
        faces.append((a, a + 1, a + 1 + columns, a + columns))
        shades.append(2 if row == 7 else 0 if (col // 4) % 2 else 1)
  cape = mesh(ctx, 'Cape', verts, faces, [blue, blueDark, gold], weights=weights)
  for face, shade in zip(cape.data.polygons, shades):
    face.material_index = shade
  bpy.context.view_layer.objects.active = cape
  thickness = cape.modifiers.new('Cloth thickness', 'SOLIDIFY')
  thickness.thickness = .018
  thickness.offset = -1
  bpy.ops.object.modifier_apply(modifier=thickness.name)
  smooth(cape, 65)

  parts = [part(ctx, 'Chest', 'Zeus tunic', tunic),
           part(ctx, 'Belt', 'Zeus belt', belt),
           part(ctx, 'Back', 'Zeus cape', [cape])]
  parts += head(ctx) + legs(ctx) + props(ctx)
  for entry in parts:
    triangles = sum(len(face.vertices) - 2 for obj in entry['objects']
                    for face in obj.data.polygons)
    assert triangles < 5000, (entry['name'], triangles)
  preset = dict(name='Zeus', group='Gota Gods', pose='A_TPose', skin=17,
                hairColor='White', pupilColor='Blue',
                parts=[dict(category='Eyes', item='16 Determined'),
                       dict(category='Mouth', item='03 Neutral'),
                       dict(category='Brow', item='04 Heroic')])
  return parts, preset
