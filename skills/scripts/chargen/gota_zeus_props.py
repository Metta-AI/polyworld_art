"""Build Zeus lightning equipment with solid colors on the shared hand bones."""

import math

import bpy
from mathutils import Vector

from clothes import material
from gota_common import mesh, part, smooth


def build(ctx):
  """Create a graspable lightning sceptre and a small floating lightning spell."""
  gold = material(ctx.prefix + 'LightningGold', '#e4a429')
  pale = material(ctx.prefix + 'LightningPale', '#fff0a6')
  shade = material(ctx.prefix + 'LightningShadow', '#b77c1d')
  white = material(ctx.prefix + 'LightningWhite', '#fff9d9')
  blue = material(ctx.prefix + 'LightningBlue', '#55caff')
  blueWhite = material(ctx.prefix + 'LightningBlueWhite', '#cff8ff')
  for color in [pale, white, blue, blueWhite]:
    shader = color.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Emission Color'].default_value = color.diffuse_color
    shader.inputs['Emission Strength'].default_value = .30

  def local(label, verts, faces, colors, side):
    """Place a locally authored item at the existing canonical hand grip."""
    x = -1.13 if side == 'RightHand' else 1.13
    verts = [(p[0] + x, p[1] - .025, p[2] + 1.73) for p in verts]
    return mesh(ctx, label, verts, faces, colors, bone=side)

  def plate(label, outline, depth, side='RightHand'):
    """Make broad pale lightning faces surrounded by gold beveled edges."""
    n = len(outline)
    verts = [(x, y, z) for y in [-depth / 2, depth / 2]
             for x, z in outline]
    faces = [tuple(reversed(range(n))), tuple(range(n, n * 2))]
    faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n)
              for i in range(n)]
    obj = local(label, verts, faces, [pale, gold], side)
    for face in obj.data.polygons[2:]:
      face.material_index = 1
    bpy.context.view_layer.objects.active = obj
    bevel = obj.modifiers.new('Small gold lightning bevel', 'BEVEL')
    bevel.width = .013
    bevel.segments = 2
    bevel.material = 1
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    return smooth(obj, 35)

  def crystal(label, center, size, colors, side='RightHand'):
    """Build a crisp six-sided crystal with a broad faceted central belt."""
    x, y, z = center
    w, d, h = size
    verts = [(x + w * math.cos(math.tau * i / 6) / 2,
              y + d * math.sin(math.tau * i / 6) / 2,
              z + level * h) for level in [-.08, .10] for i in range(6)]
    verts += [(x, y, z - h / 2), (x, y, z + h / 2)]
    faces = [(i, (i + 1) % 6, (i + 1) % 6 + 6, i + 6)
             for i in range(6)]
    faces += [(i, (i + 1) % 6, 12) for i in range(6)]
    faces += [(i + 6, (i + 1) % 6 + 6, 13) for i in range(6)]
    obj = local(label, verts, faces, colors, side)
    for face in obj.data.polygons:
      face.material_index = face.index % len(colors)
    return obj

  def handle(label, low, high, radius, colors):
    """Make a softly rounded gold handle or collar using sixteen segments."""
    sides = 16
    verts = [(radius * math.cos(math.tau * i / sides),
              radius * math.sin(math.tau * i / sides), z)
             for z in [low, high] for i in range(sides)]
    faces = [(i, (i + 1) % sides, (i + 1) % sides + sides, i + sides)
             for i in range(sides)]
    if label == 'LightningGrip':
      faces += [tuple(reversed(range(sides))),
                tuple(range(sides, sides * 2))]
    return smooth(local(label, verts, faces, colors, 'RightHand'), 40)

  outline = [(.22, 1.70), (.07, 1.18), (.26, 1.27),
             (.08, .73), (.26, .84), (.065, .18), (-.04, .18),
             (-.02, .47), (-.24, .35), (-.05, .91), (-.25, .81),
             (.02, 1.32), (-.08, 1.28)]
  bolt = [plate('LightningBlade', outline, .072),
          handle('LightningGrip', -.22, .17, .054, [shade]),
          handle('LightningCollarTop', .105, .165, .078, [gold]),
          handle('LightningCollarBottom', -.24, -.18, .076, [gold]),
          crystal('LightningGuard', (0, 0, .20), (.27, .20, .27),
                  [gold, pale, gold]),
          crystal('LightningPommel', (0, 0, -.29), (.19, .17, .22),
                  [gold, pale, gold])]
  # Two upward gold points form the compact forked guard from the reference.
  for sign in [-1, 1]:
    verts = [(sign * .025, -.047, .15), (sign * .20, 0, .35),
             (sign * .16, -.065, .20), (sign * .025, .047, .15),
             (sign * .16, .065, .20)]
    bolt.append(local('LightningGuardWing' + str(sign), verts,
      [(0, 1, 2), (3, 4, 1), (0, 3, 1), (0, 2, 4, 3), (2, 1, 4)],
      [gold], 'RightHand'))
  for i in range(4):
    bolt.append(handle('LightningGripBand' + str(i),
                        -.17 + i * .076, -.151 + i * .076, .058, [gold]))
  tail = [(-.018, -.33), (.16, -.31), (.032, -.56),
          (.087, -.54), (-.14, -.94), (-.076, -.61),
          (-.185, -.65), (-.091, -.45), (-.20, -.48)]
  bolt.append(plate('LightningTail', tail, .056))

  def fork(label, points, widths, colors):
    """Sweep diamond sections along sharp lightning joints with pointed tips."""
    verts, faces = [], []
    for i, point in enumerate(points):
      current = Vector(point)
      before = Vector(points[max(0, i - 1)])
      after = Vector(points[min(len(points) - 1, i + 1)])
      axis = (after - before).normalized()
      across = Vector((axis.z, 0, -axis.x)).normalized() * widths[i]
      front = Vector((0, widths[i] * .60, 0))
      verts += [current + across, current + front,
                current - across, current - front]
      if i:
        faces += [((i - 1) * 4 + j, (i - 1) * 4 + (j + 1) % 4,
                   i * 4 + (j + 1) % 4, i * 4 + j) for j in range(4)]
    faces += [(3, 2, 1, 0), tuple(range(len(verts) - 4, len(verts)))]
    obj = local(label, verts, faces, colors, 'LeftHand')
    for face in obj.data.polygons:
      face.material_index = face.index % len(colors)
    return obj

  spell = [crystal('LightningSpellHeart', (0, 0, .25), (.19, .15, .23),
                   [pale, gold, white], 'LeftHand')]
  spell.append(fork('LightningSpellGold',
    [(0, 0, .30), (.04, 0, .41), (-.045, 0, .51),
     (.066, 0, .62), (-.015, 0, .72), (.045, 0, .84), (0, 0, .99)],
    [.034, .044, .041, .038, .030, .021, .001], [pale, white]))
  for sign in [-1, 1]:
    spell.append(fork('LightningSpellBlue' + str(sign),
      [(sign * .065, .025, .32), (sign * .17, .020, .44),
       (sign * .14, .013, .53), (sign * .25, .007, .62),
       (sign * .205, 0, .74), (sign * .28, 0, .87)],
      [.015, .028, .029, .031, .023, .001], [blue, blueWhite]))
  return [part(ctx, 'Right hand', 'Zeus lightning bolt', bolt,
               attachmentBone='RightHand'),
          part(ctx, 'Left hand', 'Zeus lightning orb', spell,
               attachmentBone='LeftHand')]
