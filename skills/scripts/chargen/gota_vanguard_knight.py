"""Fit Vanguard Knight's modular ivory armor to the shared chargen rig."""

import math
import bpy
from mathutils import Vector
from clothes import bodySurface, clip, offset, band, material, meshObject, sourceWeights, buckle
from gota_common import duplicate, mesh, bind, part, smooth


def build(ctx):
  """Build five independently skinned armor slots without changing originals."""
  prefix = ctx.prefix
  ivory = material(prefix + 'Ivory', '#eee7d4')
  gold = material(prefix + 'Gold', '#e6ad36')
  blue = material(prefix + 'Blue', '#164bcc')
  blueDark = material(prefix + 'BlueShadow', '#173c9e')
  brown = material(prefix + 'Leather', '#513a2b')
  dark = material(prefix + 'Undercloth', '#32291f')
  palette = [ivory, gold, blue, blueDark, brown, dark]
  sample = sourceWeights(bodySurface([ctx.body] + [bpy.data.objects['Foot.Left'], bpy.data.objects['Foot.Right']]))
  counter = 0

  def geometry(label, vertices, faces, color, bone=None, weights=None):
    """Create one broad-faceted weighted plate or cloth volume."""
    nonlocal counter
    counter += 1
    item = mesh(ctx, label + str(counter), vertices, faces, [color], bone=bone,
                weights=weights if weights is not None else
                ([sample(Vector(p)) for p in vertices] if bone is None else None))
    for face in item.data.polygons:
      face.use_smooth = False
    return item

  def surface(label, records, color):
    """Preserve the fitted garment's source weights and add edge thickness."""
    item = meshObject(ctx.collection, prefix + label, [(records, 0)], [color])
    for face in item.data.polygons:
      face.use_smooth = False
    bind(ctx, item)
    return smooth(item)

  def plate(label, points, y, depth, color, bone=None, rear=False):
    """Raise a solid polygon into a small broad front-facing ridge."""
    size = len(points)
    vertices = [(x, y, z) for x, z in points]
    vertices += [(x, y + .025, z) for x, z in points]
    vertices += [(sum(p[0] for p in points) / size, y - depth,
                  sum(p[1] for p in points) / size)]
    faces = [(i, (i + 1) % size, size * 2) for i in range(size)]
    faces += [tuple(range(size, size * 2))]
    faces += [(i, i + size, (i + 1) % size + size, (i + 1) % size)
              for i in range(size)]
    if rear:
      vertices = [(x, -y, z) for x, y, z in vertices]
    return geometry(label, vertices, faces, color, bone)

  def framed(label, points, y, color=ivory, bone=None, rear=False):
    """Frame a slightly inset ivory plate with a simple solid gold border."""
    cx = sum(p[0] for p in points) / len(points)
    cz = sum(p[1] for p in points) / len(points)
    inner = [(cx + (x - cx) * .78, cz + (z - cz) * .83) for x, z in points]
    return [plate(label + 'Trim', points, y, .013, gold, bone, rear),
            plate(label + 'Plate', inner, y - .025, .035, color, bone, rear)]

  boots = duplicate(ctx, 'Clothing_14', 'Boots')
  for item in boots:
    item.data.materials.clear()
    item.data.materials.append(ivory)
    item.data.materials.append(gold)
    item.data.materials.append(brown)
    for face in item.data.polygons:
      center = face.center
      face.material_index = 1 if center.z < .065 or center.z > .38 else 0
      face.use_smooth = False
    smooth(item)

  legs = duplicate(ctx, 'Clothing_09', 'Legs')
  for item in legs:
    item.data.materials.clear()
    item.data.materials.append(brown)
    for face in item.data.polygons:
      face.material_index = 0
      face.use_smooth = False
    smooth(item)
  for sign in [-1, 1]:
    x = sign * .215
    legs += framed('Knee', [(x - .12, .68), (x, .755), (x + .12, .68),
                           (x + .095, .535), (x, .50), (x - .095, .535)], -.175)
    points = [(sign * .17, 1.30), (sign * .29, 1.30),
              (sign * .41, .91), (sign * .265, .955)]
    if sign < 0:
      points.reverse()
    legs += framed('Fauld', points, -.25)

  source = bodySurface([ctx.body])
  beltSurface = band(source, [lambda p: p.z - 1.27,
                              lambda p: 1.385 - p.z], .105)
  belt = [surface('Belt', beltSurface, brown),
          surface('Buckle', buckle(beltSurface, 1.325, .145, .11, .018), gold)]

  shirt = duplicate(ctx, 'Clothing_07', 'UnderShirt')
  for item in shirt:
    item.data.materials.clear()
    item.data.materials.append(dark)
    for face in item.data.polygons:
      face.material_index = 0
      face.use_smooth = False
    # The fitted shirt contributes sleeve and torso coverage above the belt.
    shell = clip(bodySurface([item]), lambda p: p.z - 1.21)
    bpy.data.objects.remove(item, do_unlink=True)
    shirt = [surface('FittedUnderShirt', shell, dark)]
  chest = list(shirt)
  # Keep a fitted ivory shell under broad plate facets on the front and rear.
  armor = clip(bodySurface([ctx.body]), lambda p: p.z - 1.34)
  armor = clip(armor, lambda p: 1.91 - p.z)
  armor = clip(armor, lambda p: .285 - abs(p.x))
  chest += [surface('CuirassShell', offset(armor, .074), ivory)]
  chest += [plate('Breastplate', [(-.245, 1.82), (0, 1.89), (.245, 1.82),
                                (.26, 1.59), (.16, 1.35), (0, 1.30),
                                (-.16, 1.35), (-.26, 1.59)], -.31, .060, ivory)]
  for sign in [-1, 1]:
    # Shoulder caps form a thick angled roof above the fitted sleeves.
    points = [(sign * .23, 1.91), (sign * .43, 2.00),
              (sign * .59, 1.89), (sign * .49, 1.76), (sign * .30, 1.82)]
    if sign < 0:
      points.reverse()
    chest += framed('Pauldron', points, -.145)
    chest += framed('PauldronBack', points, -.175, rear=True)
    rear = [(x, .175, z) for x, z in points]
    front = [(x, -.13, z) for x, z in points]
    chest += [geometry('ShoulderRoof', front + rear,
      [(i, (i + 1) % 5, (i + 1) % 5 + 5, i + 5) for i in range(5)], ivory)]
    armSource = clip(source, lambda p, s=sign: s * p.x - .72)
    armSource = clip(armSource, lambda p, s=sign: .91 - s * p.x)
    chest += [surface('Bracer', offset(armSource, .047), ivory)]
    for low, high in [(.715, .753), (.875, .914)]:
      edge = clip(source, lambda p, s=sign, v=low: s * p.x - v)
      edge = clip(edge, lambda p, s=sign, v=high: v - s * p.x)
      chest += [surface('BracerGold' + str(counter), offset(edge, .06), gold)]
      counter += 1
  chest += framed('Tabard', [(-.125, 1.29), (.125, 1.29), (.135, .91),
                             (0, .79), (-.135, .91)], -.315)
  # The cape is a broad folded garment attached at the shoulders.
  capeRows = [(1.89, .29, .36), (1.65, .36, .395),
              (1.30, .45, .455), (.64, .62, .48)]
  verts = []
  for z, width, y in capeRows:
    for t in [-1, -.5, 0, .5, 1]:
      verts.append((width * t, y + (.05 if abs(t) == .5 else 0),
                    z + (.06 * abs(t) if z < .7 else 0)))
  faces = []
  for row in range(len(capeRows) - 1):
    for col in range(4):
      a = row * 5 + col
      faces += [(a, a + 1, a + 6), (a, a + 6, a + 5)]
  capeWeights = ([{'Spine2': 1}] * 10 +
                 [{'Spine1': .45, 'Hips': .55}] * 5 +
                 [{'Hips': 1}] * 5)
  cape = geometry('Cape', verts, faces, blue, weights=capeWeights)
  cape.data.materials.append(blueDark)
  for face in cape.data.polygons:
    face.material_index = (face.index // 2) % 2
  chest.append(cape)

  head = bodySurface([bpy.data.objects['Head']])
  shell = offset(head, .058)
  shell = clip(shell, lambda p: p.z - 2.10)
  shell = clip(shell, lambda p: max(p.y + .015, p.z - 2.755,
                                   abs(p.x) - .43))
  hat = [surface('HelmetShell', shell, ivory)]
  brow = band(head, [lambda p: p.z - 2.685, lambda p: 2.825 - p.z,
                     lambda p: .17 - p.y], .095)
  hat += [surface('HelmetGoldBrow', brow, gold)]
  hat += [plate('HelmetCrest', [(0, 3.12), (.085, 2.84), (.070, 2.68),
                                (0, 2.60), (-.070, 2.68), (-.085, 2.84)],
                -.57, .06, gold, 'Head')]
  for sign in [-1, 1]:
    x = sign * .525
    hat += [plate('TempleGold', [(x - .046, 2.61), (x + .046, 2.61),
                                (x + .055, 2.84), (x, 2.97),
                                (x - .055, 2.84)], -.135, .04, gold, 'Head')]
  hat += [plate('UpperGoldDiamond', [(0, 3.29), (.095, 3.155),
                                     (0, 3.035), (-.095, 3.155)],
                -.32, .045, gold, 'Head')]
  plumeRings = [(-.13, 3.05, .16, .11), (-.05, 3.27, .235, .14),
                (.16, 3.40, .235, .12), (.40, 3.28, .20, .13),
                (.56, 3.00, .09, .07), (.58, 2.86, .012, .012)]
  verts, faces = [], []
  sides = 12
  for j, (y, z, width, depth) in enumerate(plumeRings):
    previous = plumeRings[max(0, j - 1)]
    following = plumeRings[min(len(plumeRings) - 1, j + 1)]
    tangent = Vector((0, following[0] - previous[0],
                      following[1] - previous[1])).normalized()
    across = Vector((0, -tangent.z, tangent.y))
    for i in range(sides):
      theta = i * math.tau / sides
      edge = across * (math.sin(theta) * depth)
      verts.append((math.cos(theta) * width, y + edge.y, z + edge.z))
      if j:
        a = (j - 1) * sides + i
        b = (j - 1) * sides + (i + 1) % sides
        faces += [(a, b, b + sides), (a, b + sides, a + sides)]
  faces += [tuple(reversed(range(sides))),
            tuple(range(len(verts) - sides, len(verts)))]
  hat += [smooth(geometry('BluePlume', verts, faces, blue, 'Head'), 65)]
  parts = [part(ctx, 'Foot', 'Vanguard Knight boots', boots,
                hides=['Foot.Left', 'Foot.Right'] + [
                  prefix + 'Legs_BootCut' + str(i) for i in range(3)]),
           part(ctx, 'Leg', 'Vanguard Knight legs', legs),
           part(ctx, 'Belt', 'Vanguard Knight belt', belt),
           part(ctx, 'Chest', 'Vanguard Knight body', chest),
           part(ctx, 'Headgear', 'Vanguard Knight helmet', hat)]
  preset = dict(name='Vanguard Knight', group='Gota', pose='A_TPose', skin=17,
                hairColor='Chestnut', pupilColor='Blue',
                parts=[dict(category='Eyes', item='16 Determined'),
                       dict(category='Mouth', item='03 Neutral'),
                       dict(category='Brow', item='04 Heroic')])
  return parts, preset
