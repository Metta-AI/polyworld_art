"""Fit Zeus's pleated skirt and gold sandals to the shared humanoid rig."""

import math

import bpy
import bmesh
from mathutils import Vector

from clothes import bodySurface, clip, material, meshObject, offset
from gota_common import bind, mesh, part, smooth


def build(ctx):
  """Create two independent solid-color skirt and greave clothing slots."""
  ivory = material(ctx.prefix + 'SkirtIvory', '#f1ebdf')
  gold = material(ctx.prefix + 'GreaveGold', '#e6ad36')
  goldLight = material(ctx.prefix + 'GreaveGoldLight', '#f6cc58')
  goldDark = material(ctx.prefix + 'GreaveGoldDark', '#a87522')
  blue = material(ctx.prefix + 'SkirtBlue', '#235fd4')
  jewel = material(ctx.prefix + 'KneeBlue', '#248fef')
  leather = material(ctx.prefix + 'SandalLeather', '#705331')

  def shell(label, vertices, faces, colors, bone=None, thickness=.014, inside=True, centerX=0):
    """Thicken cloth and shell surfaces while preserving sampled rig weights."""
    obj = mesh(ctx, label, vertices, faces, colors, bone=bone)
    bpy.context.view_layer.objects.active = obj
    modifier = obj.modifiers.new('Hem thickness', 'SOLIDIFY')
    modifier.thickness = thickness
    modifier.offset = -1
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    if not inside:
      edit = bmesh.new()
      edit.from_mesh(obj.data)
      hidden = []
      for face in edit.faces:
        center = face.calc_center_median()
        radial = Vector((center.x - centerX, center.y + .01, 0))
        if face.normal.dot(radial) < -.00001:
          hidden.append(face)
      bmesh.ops.delete(edit, geom=hidden, context='FACES')
      edit.to_mesh(obj.data)
      edit.free()
      obj.data.update()
    return smooth(obj, 55)

  def gem(label, x, y, z, width, height, color, bone):
    """Make a broad faceted diamond for a raised gold knee setting."""
    vertices = [(x, y, z + height), (x + width, y, z),
                (x, y, z - height), (x - width, y, z),
                (x, y - width * .47, z), (x, y + .015, z)]
    faces = [(i, (i + 1) % 4, pole) for pole in [4, 5]
             for i in range(4)]
    return mesh(ctx, label, vertices, faces, [color], bone=bone)

  # The base skirt has broad real pleats around its full circumference.
  columns = 48
  rows = [(1.335, .327, .274), (1.10, .387, .300),
          (.824, .473, .349), (.791, .482, .354),
          (.768, .490, .358)]
  vertices, faces, shades = [], [], []
  for row, (z, rx, ry) in enumerate(rows):
    for col in range(columns):
      angle = math.tau * col / columns
      fold = (1 - math.cos(angle * 12)) * .014 * row / 4
      vertices.append((math.sin(angle) * (rx + fold),
                       -math.cos(angle) * (ry + fold), z))
      if row:
        a = (row - 1) * columns + col
        b = (row - 1) * columns + (col + 1) % columns
        faces.append((a, b, b + columns, a + columns))
        shades.append(1 if row == 3 else 0)
  skirt = shell('PleatedSkirt', vertices, faces, [ivory, gold])
  for polygon, shade in zip(skirt.data.polygons, shades):
    polygon.material_index = shade
  legs = [skirt]

  # Weighted fitted undercloth covers the knees below the open skirt hem.
  records = clip(bodySurface([ctx.body]), lambda p: p.z - .67)
  records = clip(records, lambda p: .85 - p.z)
  underskirt = meshObject(ctx.collection, ctx.prefix + 'SkirtUndercloth',
                         [(offset(records, .016), 0)], [ivory])
  legs.append(smooth(bind(ctx, underskirt), 60))

  # A pointed central ivory fall has a continuous gold perimeter.
  outline = [(-.116, 1.332), (.116, 1.332), (.175, .78),
             (0, .625), (-.175, .78)]
  center = [(x * .85, .988 + (z - .988) * .94) for x, z in outline]
  frontVertices = [(x, -.382 - (1.332 - z) * .04, z)
                   for x, z in outline]
  frontVertices += [(x, -.387 - (1.332 - z) * .04, z)
                    for x, z in center]
  frontVertices.append((0, -.433, .996))
  frontFaces, indices = [], []
  for i in range(5):
    j = (i + 1) % 5
    frontFaces += [(i, j, j + 5, i + 5), (i + 5, j + 5, 10)]
    indices += [1, 0]
  tabard = shell('PointedTabard', frontVertices, frontFaces, [ivory, gold])
  for polygon, shade in zip(tabard.data.polygons, indices):
    polygon.material_index = shade
  legs.append(tabard)

  for sign in [-1, 1]:
    # Blue folds hang alongside the central white fall and curl onto the hips.
    vertices, faces, shades = [], [], []
    blueRows = [(1.325, .133, .218, -.345),
                (1.13, .154, .245, -.368),
                (.93, .174, .284, -.389),
                (.791, .183, .316, -.397),
                (.759, .188, .320, -.398),
                (.731, .192, .325, -.399)]
    for row, (z, inner, outer, y) in enumerate(blueRows):
      vertices += [(sign * inner, y, z),
                   (sign * ((inner + outer) / 2), y - .019, z + .006),
                   (sign * outer, y, z + .018)]
      if row:
        for col in range(2):
          a = (row - 1) * 3 + col
          faces.append((a, a + 1, a + 4, a + 3))
          shades.append(1 if row == 4 else 0)
    hanging = shell('BlueSkirtFall' + str(sign), vertices, faces, [blue, gold])
    for polygon, shade in zip(hanging.data.polygons, shades):
      polygon.material_index = shade
    legs.append(hanging)
    vertices, faces = [], []
    for i in range(17):
      t = i / 16
      x = sign * (.20 + .267 * t)
      y = -.376 + .177 * t * t
      z = 1.15 - .145 * math.sin(t * math.pi / 2)
      vertices += [(x, y - .015, z), (x, y - .018, z - .041)]
      if i:
        a = (i - 1) * 2
        faces.append((a, a + 1, a + 3, a + 2))
    legs.append(shell('HipBlueDrape' + str(sign), vertices, faces, [blue]))

  sandals = []
  for sign in [-1, 1]:
    x = sign * .201
    bone = 'LeftLeg' if sign > 0 else 'RightLeg'
    footBone = 'LeftFoot' if sign > 0 else 'RightFoot'
    columns = 32
    greaveRows = [(.172, .100, .093), (.218, .111, .104),
                  (.30, .098, .106), (.46, .112, .128),
                  (.58, .148, .154), (.665, .155, .156),
                  (.715, .138, .146)]
    vertices, faces = [], []
    for row, (z, rx, ry) in enumerate(greaveRows):
      for col in range(columns):
        a = math.tau * col / columns
        crest = .025 * max(0, math.cos(a)) if row >= 5 else 0
        vertices.append((x + math.sin(a) * rx,
                         -.01 - math.cos(a) * ry, z + crest))
        if row:
          i = (row - 1) * columns + col
          j = (row - 1) * columns + (col + 1) % columns
          faces.append((i, j, j + columns, i + columns))
    greave = shell('GoldGreave' + str(sign), vertices, faces,
                    [gold], bone=bone, thickness=.018, inside=False, centerX=x)
    sandals.append(greave)
    for index, (z, rx, ry, height) in enumerate([
        (.176, .109, .105, .050), (.674, .162, .165, .034)]):
      vertices, faces = [], []
      for row in range(2):
        for col in range(columns):
          a = math.tau * col / columns
          crest = .025 * max(0, math.cos(a)) if index else 0
          vertices.append((x + math.sin(a) * rx,
                           -.010 - math.cos(a) * ry, z + height * row + crest))
          if row:
            i, j = col, (col + 1) % columns
            faces.append((i, j, j + columns, i + columns))
      sandals.append(shell('GreaveRim' + str(sign) + str(index),
                            vertices, faces, [goldLight], bone=bone,
                            inside=False, centerX=x))
    # Slightly raised front armor facets give the shin a shaped silhouette.
    vertices = [(x - .079, -.155, .596), (x, -.201, .637),
                (x + .079, -.155, .596), (x + .045, -.123, .235),
                (x, -.146, .213), (x - .045, -.123, .235),
                (x, -.176, .409)]
    sandals.append(shell('ShinRidge' + str(sign), vertices,
      [(i, (i + 1) % 6, 6) for i in range(6)], [goldLight], bone=bone))
    sandals.append(gem('KneeGemGold' + str(sign), x, -.182,
                         .650, .105, .120, goldLight, bone))
    sandals.append(gem('KneeGem' + str(sign), x, -.214,
                         .650, .071, .082, jewel, bone))

    # A rounded sole follows the existing foot, which remains visible in front.
    vertices, faces, shades = [], [], []
    for row, (z, radius) in enumerate([(.009, .97), (.021, 1),
                                      (.052, 1), (.063, .94)]):
      for col in range(columns):
        a = math.tau * col / columns
        vertices.append((x + math.sin(a) * .128 * radius,
                         -.065 - math.cos(a) * .182 * radius, z))
        if row:
          i = (row - 1) * columns + col
          j = (row - 1) * columns + (col + 1) % columns
          faces.append((i, j, j + columns, i + columns))
          shades.append(1 if row == 3 else 0)
    faces += [tuple(reversed(range(columns))),
              tuple(range(columns * 3, columns * 4))]
    shades += [0, 0]
    sole = mesh(ctx, 'SandalSole' + str(sign), vertices, faces,
                  [leather, goldDark], bone=footBone)
    for polygon, shade in zip(sole.data.polygons, shades):
      polygon.material_index = shade
    sandals.append(smooth(sole, 55))
    # Broad fitted straps wrap the original foot and leave its toe exposed.
    foot = bpy.data.objects['Foot.Left' if sign > 0 else 'Foot.Right']
    footSource = bodySurface([foot])
    for index, (lo, hi) in enumerate([(-.137, -.092), (-.045, .010)]):
      records = clip(footSource, lambda p, limit=lo: p.y - limit)
      records = clip(records, lambda p, limit=hi: limit - p.y)
      records = clip(records, lambda p: p.z - .054)
      strap = meshObject(ctx.collection, ctx.prefix + 'SandalStrap' +
                         str(sign) + str(index),
                         [(offset(records, .018), 0)], [gold])
      sandals.append(smooth(bind(ctx, strap), 55))

  footPart = part(ctx, 'Foot', 'Zeus sandals', sandals)
  footPart['keepFeet'] = True
  return [part(ctx, 'Leg', 'Zeus skirt', legs), footPart]
