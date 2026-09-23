"""Fit the medieval Crossbowman's five modular garments to the shared rig."""

import bpy
import bmesh
from mathutils import Vector

from clothes import band, bodySurface, buckle, clip, hemExtrusion, material
from clothes import neckline, offset, sourceWeights
from garments import finish
from gota_common import bind, duplicate, mesh, part, smooth, roundedHood


def simplify(ctx, obj, ratio):
  """Reduce dense inherited cloth surfaces while preserving rig weights."""
  bpy.context.view_layer.objects.active = obj
  modifier = obj.modifiers.new('Low polygon clothing', 'DECIMATE')
  modifier.ratio = ratio
  modifier.use_collapse_triangulate = True
  bpy.ops.object.modifier_apply(modifier=modifier.name)
  bind(ctx, obj)
  return obj


def garment(ctx, suffix, surfaces, colors):
  """Finish flat cloth shells while keeping the original body's skin weights."""
  palette = [material(ctx.prefix + suffix + str(i), color)
             for i, color in enumerate(colors)]
  obj = finish(ctx.collection, ctx.prefix + suffix, surfaces, palette,
               'Shared fitted Body surfaces')
  for polygon in obj.data.polygons:
    polygon.use_smooth = False
  bind(ctx, obj)
  if suffix == 'body':
    simplify(ctx, obj, .50)
  return smooth(obj, 40)


def torso(ctx, source):
  """Build a short red split tunic with layered crossed leather panels."""
  sample = sourceWeights(source)
  red = clip(source, lambda p: p.z - 1.22)
  red = clip(red, lambda p: max(.65 - abs(p.x), 1.56 - p.z))
  red = clip(red, lambda p: neckline(p, 'v'))
  red = hemExtrusion(red, 1.22, .875, sample, slit=True)
  red = clip(red, lambda p: max(p.z - 1.26, abs(p.x) -
             (.020 + max(0, 1.26 - p.z) * .15), .08 - abs(p.y)))
  red = [[(Vector((p.x * (1 + max(0, 1.25 - p.z) * .45),
                    p.y, p.z + max(0, 1.22 - p.z) * .15 * abs(p.x) / .35)),
           n, w) for p, n, w in face] for face in red]
  red = offset(red, .078)
  chest = band(red, [lambda p: p.z - 1.30,
                    lambda p: 1.90 - p.z,
                    lambda p: .285 - abs(p.x)], .030)
  surfaces = [(red, 0), (chest, 1)]
  for sign in [-1, 1]:
    crossed = band(chest, [lambda p, s=sign:
      .095 - abs(p.x - s * (p.z - 1.595) * .95),
      lambda p: abs(p.y) - .06], .024 if sign == 1 else .036)
    surfaces.append((crossed, 2))
  bracers = band(source, [lambda p: abs(p.x) - .82,
                         lambda p: 1.03 - abs(p.x),
                         lambda p: p.z - 1.50], .038)
  cuffs = band(bracers, [lambda p: .87 - abs(p.x)], .027)
  gloves = offset(bodySurface([bpy.data.objects['Hand.Left'],
                               bpy.data.objects['Hand.Right']]), .013)
  surfaces.extend([(bracers, 1), (cuffs, 2), (gloves, 1)])
  return garment(ctx, 'body', surfaces,
                 ['#9c3e3b', '#624533', '#7c5940'])


def waist(ctx, source):
  """Fit a separate leather belt with a modest square brass buckle."""
  leather = band(source, [lambda p: p.z - 1.255,
                         lambda p: 1.365 - p.z], .157)
  return garment(ctx, 'belt', [(leather, 0),
                 (buckle(leather, 1.31, .14, .12, .021), 1)],
                 ['#604431', '#dba143'])


def hood(ctx):
  """Wrap a compact brown hood around the skull with a raised front facing."""
  return roundedHood(ctx, 'hood', ['#765138', '#855f43', '#493324'],
    opening='pointed')


def build(ctx):
  """Return five selectable medieval clothing parts and reusable face choices."""
  source = bodySurface([ctx.body])
  boots = duplicate(ctx, 'Clothing_16', 'boots',
                    colors=['#765039', '#865c3e', '#60412f',
                            '#bba780', '#3c2e24'])
  trousers = duplicate(ctx, 'Clothing_12', 'legs',
                       colors=['#373331', '#494039'])
  keep = []
  for obj in trousers:
    if max(vertex.co.z for vertex in obj.data.vertices) < .42:
      bpy.data.objects.remove(obj, do_unlink=True)
    else:
      keep.append(obj)
  for obj in boots:
    simplify(ctx, obj, .43)
  for obj in keep:
    simplify(ctx, obj, .78)
    for vertex in obj.data.vertices:
      point = vertex.co
      if point.z < 1.1:
        center = .201 if point.x > 0 else -.201
        point.x = center + (point.x - center) * 1.30
        point.y = .015 + (point.y - .015) * 1.30
  for obj in boots + keep:
    smooth(obj)
  hair = duplicate(ctx, 'Hair_01', 'hair', colors=['#62422c'] * 10)
  for obj in hair:
    # Keep the visible fringe while removing hair concealed by the fitted hood.
    edit = bmesh.new()
    edit.from_mesh(obj.data)
    for point, normal in [((0, -.37, 0), (0, 1, 0)),
                           ((0, 0, 2.98), (0, 0, 1)),
                           ((0, 0, 2.995), (.585, 0, 1)),
                           ((0, 0, 2.995), (-.585, 0, 1)),
                           ((0, 0, 3.13), (1.187, 0, 1)),
                           ((0, 0, 3.13), (-1.187, 0, 1)),
                           ((.41, 0, 0), (1, 0, 0)),
                           ((-.41, 0, 0), (-1, 0, 0))]:
      bmesh.ops.bisect_plane(edit,
        geom=list(edit.verts) + list(edit.edges) + list(edit.faces),
        plane_co=point, plane_no=normal, dist=.000001, clear_outer=True)
    edit.to_mesh(obj.data)
    edit.free()
    obj['construction'] = 'Hood fringe only, with the concealed crown removed'
  beard = duplicate(ctx, 'Beard_02', 'mustache', colors=['#795035'] * 10)
  for obj in beard:
    for vertex in obj.data.vertices:
      vertex.co.x *= 1.40
      vertex.co.z = 2.14 + (vertex.co.z - 2.14) * 1.35
  parts = [part(ctx, 'Hair', 'Gota Crossbowman hood fringe', hair),
           part(ctx, 'Beard', 'Gota Crossbowman mustache', beard),
           part(ctx, 'Foot', 'Gota Crossbowman boots', boots),
           part(ctx, 'Leg', 'Gota Crossbowman trousers', keep),
           part(ctx, 'Belt', 'Gota Crossbowman belt', [waist(ctx, source)]),
           part(ctx, 'Chest', 'Gota Crossbowman leather tunic',
                [torso(ctx, source)], hides=['Hand.Left', 'Hand.Right']),
           part(ctx, 'Headgear', 'Gota Crossbowman hood', [hood(ctx)])]
  preset = dict(name='Crossbowman', group='Gota', pose='A_TPose', skin=10,
                hairColor='Dark brown', pupilColor='Brown', parts=[
                  dict(category='Hair', item='01 French crop'),
                  dict(category='Beard', item='02 Parted chevron'),
                  dict(category='Eyes', item='10 Sharp'),
                  dict(category='Mouth', item='03 Neutral'),
                  dict(category='Brow', item='11 Bushy'),
                ])
  return parts, preset
