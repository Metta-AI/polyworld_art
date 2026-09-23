"""Build Ranger's fitted five-slot olive and leather clothing."""

import math

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

from clothes import (band, bodySurface, clip, hemExtrusion, material,
                     meshObject, neckline, offset, sourceWeights)
from gota_common import bind, duplicate, mesh, part, smooth


def flat(item):
  """Keep large material facets explicit on all newly owned clothing."""
  for face in item.data.polygons:
    face.use_smooth = False
  return item


def finish(ctx, suffix, surfaces, materials):
  """Build a fitted shell using source skin weights and thin open edges."""
  item = meshObject(ctx.collection, ctx.prefix + suffix, surfaces, materials)
  bpy.context.view_layer.objects.active = item
  thickness = item.modifiers.new('Clothing edge thickness', 'SOLIDIFY')
  thickness.thickness = .008
  thickness.offset = -1
  bpy.ops.object.modifier_apply(modifier=thickness.name)
  bind(ctx, item)
  return flat(item)


def cape(ctx, green, dark):
  """Use torso-only weights and waist loops so the cape follows a crouch."""
  vertices = [(-.25, .23, 1.93), (0, .28, 1.96), (.25, .23, 1.93),
              (-.37, .40, 1.60), (0, .44, 1.62), (.37, .40, 1.60),
              (-.44, .48, 1.30), (0, .52, 1.30), (.44, .48, 1.30),
              (-.53, .49, .99), (-.35, .53, 1.03), (-.25, .55, .89),
              (0, .58, .96), (.25, .55, .89), (.35, .53, 1.03),
              (.53, .49, .99)]
  faces = [(0, 1, 4), (0, 4, 3), (1, 2, 5), (1, 5, 4),
           (3, 4, 7), (3, 7, 6), (4, 5, 8), (4, 8, 7),
           (6, 7, 11), (6, 11, 10), (6, 10, 9), (7, 12, 11),
           (7, 8, 13), (7, 13, 12), (8, 14, 13), (8, 15, 14)]
  weights = [{'Spine2': 1}]*3
  weights += [{'Spine2': .2, 'Spine1': .8}]*3
  weights += [{'Spine': .6, 'Hips': .4}]*3
  weights += [{'Hips': 1}]*7
  item = mesh(ctx, 'Cape', vertices, faces, [green, dark], weights=weights)
  for i, face in enumerate(item.data.polygons):
    face.material_index = int(i in [0, 3, 5, 8, 10])
  bpy.context.view_layer.objects.active = item
  mod = item.modifiers.new('Cape thickness', 'SOLIDIFY')
  mod.thickness = .014
  bpy.ops.object.modifier_apply(modifier=mod.name)
  return flat(item)


def cowl(ctx, green, dark):
  """Place a compact folded green neck cowl above the crossed straps."""
  vertices, faces = [], []
  for row, (rx, ry, z) in enumerate([(.25, .21, 2.015),
                                    (.29, .25, 1.94),
                                    (.28, .25, 1.865)]):
    for i in range(10):
      theta = math.tau * i / 10
      front = max(0, math.cos(theta))
      vertices.append((rx * math.sin(theta), -ry * math.cos(theta),
                       z - front * (.05 if row else .02)))
      if row:
        j = (i + 1) % 10
        faces.append(((row-1)*10+i, (row-1)*10+j, row*10+j, row*10+i))
  item = mesh(ctx, 'Cowl', vertices, faces, [green, dark])
  for face in item.data.polygons:
    face.material_index = int(face.index >= 10)
  return flat(item)


def hood(ctx, green, light, dark):
  """Wrap a rounded cloth shell and rolled opening over the copper hair."""
  sides = 28
  # The forward opening covers the hairline while the braids exit below it.
  rings = [(.460, .305, .510, -.610),
           (.480, .340, .535, -.625),
           (.525, .440, .560, -.585),
           (.568, .575, .575, -.460),
           (.590, .585, .570, -.180),
           (.580, .570, .550, .150),
           (.505, .495, .550, .420),
           (.315, .330, .520, .580)]
  vertices, faces, shades = [], [], []
  for row, (width, top, bottom, depth) in enumerate(rings):
    for i in range(sides):
      angle = math.tau * i / sides
      vertical = math.cos(angle)
      lower = max(0, -vertical)
      vertices.append((width * math.sin(angle),
                       depth + .10 * lower * lower,
                       2.565 + vertical * (top if vertical >= 0 else bottom)))
      if row:
        a = (row - 1) * sides + i
        b = (row - 1) * sides + (i + 1) % sides
        faces.append((a, b, b + sides, a + sides))
        shades.append(1 if row <= 2 else 0)
  vertices.append((0, .650, 2.57))
  for i in range(sides):
    faces.append(((len(rings) - 1) * sides + i,
                  (len(rings) - 1) * sides + (i + 1) % sides,
                  len(vertices) - 1))
    shades.append(0)
  item = mesh(ctx, 'Hood', vertices, faces, [green, light, dark], bone='Head')
  for face, shade in zip(item.data.polygons, shades):
    face.material_index = shade
  bpy.context.view_layer.objects.active = item
  mod = item.modifiers.new('Hood cloth thickness', 'SOLIDIFY')
  mod.thickness = .018
  mod.offset = -1
  mod.material_offset = 2
  bpy.ops.object.modifier_apply(modifier=mod.name)
  return smooth(item, 80)


def simplify(ctx, items, ratio):
  """Reduce inherited garment topology while retaining skin deformation."""
  for item in items:
    for modifier in list(item.modifiers):
      if modifier.type == 'ARMATURE':
        item.modifiers.remove(modifier)
    bpy.context.view_layer.objects.active = item
    modifier = item.modifiers.new('Low-poly garment reduction', 'DECIMATE')
    modifier.ratio = ratio
    modifier.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bind(ctx, item)
    flat(item)


def hoodBraids(ctx):
  """Keep only hanging braid islands so hoods can sit close to the head."""
  items = duplicate(ctx, 'Hair_09', 'HoodBraids')
  for item in items:
    edit = bmesh.new()
    edit.from_mesh(item.data)
    seen, removed = set(), []
    for vertex in edit.verts:
      if vertex in seen:
        continue
      group, stack = [], [vertex]
      seen.add(vertex)
      while stack:
        current = stack.pop()
        group.append(current)
        for edge in current.link_edges:
          neighbor = edge.other_vert(current)
          if neighbor not in seen:
            seen.add(neighbor)
            stack.append(neighbor)
      if max(vertex.co.z for vertex in group) > 2.55:
        removed.extend(group)
    bmesh.ops.delete(edit, geom=removed, context='VERTS')
    edit.to_mesh(item.data)
    edit.free()
    item['construction'] = 'Hood and helmet hair: hanging braids only, no cap'
  return items


def recolor(items, colors, prefix):
  """Give copied fitted garments their own solid material palette."""
  for item in items:
    oldCount = len(item.data.materials)
    indices = [face.material_index for face in item.data.polygons]
    item.data.materials.clear()
    for index in range(oldCount):
      item.data.materials.append(material(prefix + str(index),
                                          colors[min(index, len(colors)-1)]))
    for face, index in zip(item.data.polygons, indices):
      face.material_index = index
    flat(item)


def build(ctx):
  """Return five independently selectable fitted parts and the Ranger preset."""
  green = material(ctx.prefix + 'Moss', '#596f29')
  light = material(ctx.prefix + 'Olive', '#728c39')
  dark = material(ctx.prefix + 'Forest', '#344c26')
  leather = material(ctx.prefix + 'Leather', '#6a4932')
  body = bodySurface([ctx.body])
  sample = sourceWeights(body)
  torso = clip(body, lambda p: p.z - 1.22)
  torso = clip(torso, lambda p: max(.31 - abs(p.x), 1.55-p.z))
  torso = clip(torso, lambda p: neckline(p, 'round'))
  torso = hemExtrusion(torso, 1.22, .95, sample, slit=True)
  torso = offset(torso, .047)
  shaped = []
  for face in torso:
    polygon = []
    for point, normal, weights in face:
      point = point.copy()
      if point.z < 1.20:
        factor = min(1, (1.20-point.z)/.22)
        theta = math.atan2(point.x, point.y)
        point.z += factor * .085 * abs(math.sin(theta*3))
      polygon.append((point, normal, weights))
    shaped.append(polygon)
  torsoItem = finish(ctx, 'Tunic', [(shaped, 0)], [green])
  tree = BVHTree.FromPolygons([v.co for v in torsoItem.data.vertices],
                              [p.vertices[:] for p in torsoItem.data.polygons])
  straps = []
  for sign in [-1, 1]:
    vertices, faces = [], []
    for row, z in enumerate([1.29+i*.055 for i in range(12)]):
      for side in [-1, 1]:
        x = sign*(z-1.60)*.92 + side*.044
        point, normal, index, distance = tree.ray_cast(Vector((x, -1, z)),
                                                       Vector((0, 1, 0)))
        y = point.y-.030-sign*.004 if point is not None else -.29
        vertices.append((x, y, z))
      if row:
        a = (row-1)*2
        faces.append((a, a+1, a+3, a+2))
    straps.append(mesh(ctx, 'Strap'+str(sign), vertices, faces, [leather]))
  cuffs = band(body, [lambda p: abs(p.x)-.79,
                      lambda p: .95-abs(p.x)], .034)
  cuffItem = finish(ctx, 'Bracers', [(cuffs, 0)], [leather])
  chest = [torsoItem, cuffItem, cape(ctx, green, dark),
           cowl(ctx, dark, green)] + straps
  boots = duplicate(ctx, 'Clothing_16', 'Boots')
  recolor(boots, ['#64452f', '#845a38', '#64452f', '#b99447', '#36281f'],
          ctx.prefix+'Boot')
  for item in boots:
    for vertex in item.data.vertices:
      if vertex.co.z > .17:
        vertex.co.z = .17 + (vertex.co.z-.17)*1.45
  legs = duplicate(ctx, 'Clothing_09', 'Trousers')
  recolor(legs, ['#503a2d'], ctx.prefix+'Trouser')
  belt = duplicate(ctx, 'Gnome_Belt', 'Belt')
  recolor(belt, ['#6a4932', '#805638', '#c99737'], ctx.prefix+'Belt')
  simplify(ctx, boots, .60)
  simplify(ctx, [cuffItem], .45)
  for item in boots + legs + [cuffItem, chest[3]]:
    smooth(item)
  hair = hoodBraids(ctx)
  recolor(hair, ['#d85513', '#eb6b1b', '#bd4210', '#70432b'],
          ctx.prefix+'Copper')
  for item in hair:
    for vertex in item.data.vertices:
      if abs(vertex.co.x) > .35:
        amount = max(0, min(1, (2.47-vertex.co.z)/.24))
        vertex.co.y -= amount*.43
  simplify(ctx, hair, .60)
  for sign in [-1, 1]:
    vertices = [(sign*.025, -.327, 1.255), (sign*.285, -.327, 1.255),
                (sign*.365, -.288, 1.00), (sign*.19, -.353, .885),
                (sign*.02, -.342, 1.015), (sign*.18, -.372, 1.105)]
    faces = [(i, (i+1)%5, 5) for i in range(5)]
    panel = mesh(ctx, 'SkirtPanel'+str(sign), vertices, faces, [light, green])
    for face in panel.data.polygons:
      face.material_index = face.index%2
    chest.append(panel)
  headgear = [hood(ctx, green, light, dark)]
  bootHides = ['Foot.Left', 'Foot.Right']
  bootHides += [o.name for o in legs if '_BootCut' in o.name and
                not o.name.endswith('BootCut3')]
  parts = [part(ctx, 'Foot', 'Ranger cuff boots', boots, hides=bootHides),
           part(ctx, 'Leg', 'Ranger trousers', legs),
           part(ctx, 'Belt', 'Ranger buckle belt', belt),
           part(ctx, 'Chest', 'Ranger tunic and cape', chest),
           part(ctx, 'Headgear', 'Ranger fitted hood', headgear,
                hides=['Ears_Round_Left', 'Ears_Round_Right']),
           part(ctx, 'Hair', 'Ranger hood braids', hair)]
  preset = dict(name='Ranger', group='Gota', skin=13, hairColor='Copper',
                pupilColor='Brown', parts=[
      dict(category='Eyes', item='12 Sleepy'),
      dict(category='Brow', item='02 Confident'),
      dict(category='Mouth', item='03 Neutral'),
      dict(category='Nose', item='Tiny'),
      dict(category='Ears', item='Round'),
      dict(category='Hair', item='Ranger hood braids'),
      dict(category='Foot', item='Ranger cuff boots'),
      dict(category='Leg', item='Ranger trousers'),
      dict(category='Belt', item='Ranger buckle belt'),
      dict(category='Chest', item='Ranger tunic and cape'),
      dict(category='Headgear', item='Ranger fitted hood')])
  return parts, preset
