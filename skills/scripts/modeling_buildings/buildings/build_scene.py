import os
import json
import math
import random
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

Root = Path(__file__).resolve().parent
Pi = math.pi
Tiles = {
  'stone': (0, 0), 'plaster': (1, 0), 'window': (2, 0),
  'gray': (3, 0), 'roof': (0, 1), 'wood': (1, 1),
  'gold': (2, 1), 'door': (3, 1), 'pumpkin': (0, 2),
  'banner': (1, 2), 'leaf': (2, 2), 'doubleDoor': (3, 2),
  'bark': (0, 3), 'soil': (1, 3), 'archWindow': (2, 3),
  'archDoor': (3, 3),
}
Rng = random.Random(921)
Sources = []
Current = None

def collection(name):
  """Create an editable reusable asset collection."""
  return bpy.data.collections.new(name)

def useCollection(name):
  """Set the explicitly selected modeling collection."""
  global Current
  Current = collection(name)
  return Current

def solidMaterial(name, color, roughness=0.7, emission=0):
  """Create a simple material for metal, recesses, and stage geometry."""
  material = bpy.data.materials.new(name)
  material.diffuse_color = (*color, 1)
  material.use_nodes = True
  shader = material.node_tree.nodes.get('Principled BSDF')
  shader.inputs['Base Color'].default_value = (*color, 1)
  shader.inputs['Roughness'].default_value = roughness
  if emission:
    shader.inputs['Emission Color'].default_value = (*color, 1)
    shader.inputs['Emission Strength'].default_value = emission
  return material

def flatMaterial(name, color):
  """Keep stage lettering and rules independent of scene illumination."""
  material = bpy.data.materials.new(name)
  material.use_nodes = True
  nodes = material.node_tree.nodes
  nodes.clear()
  shader = nodes.new('ShaderNodeEmission')
  shader.inputs['Color'].default_value = (*color, 1)
  output = nodes.new('ShaderNodeOutputMaterial')
  material.node_tree.links.new(shader.outputs[0], output.inputs['Surface'])
  return material

def tileUv(tile, u, v):
  """Map local coordinates into a padded cell of the approved atlas."""
  column, row = Tiles[tile]
  pad = 0.008
  return ((column + pad + u * (1 - 2 * pad)) / 4,
    (3 - row + pad + v * (1 - 2 * pad)) / 4)

def meshObject(name, vertices, faces, tile='plaster', uvs=None,
  material=None, group=None):
  """Create mesh geometry with real UV coordinates and a named material."""
  mesh = bpy.data.meshes.new(name + ' Mesh')
  mesh.from_pydata(vertices, [], faces)
  mesh.update()
  obj = bpy.data.objects.new(name, mesh)
  (group or Current).objects.link(obj)
  mesh.materials.append(material or Atlas)
  layer = mesh.uv_layers.new(name='Building Atlas UV')
  for i, face in enumerate(mesh.polygons):
    coords = uvs[i] if uvs else (
      [(0, 0), (1, 0), (1, 1), (0, 1)] if len(face.vertices) == 4
      else [(0.05, 0.05), (0.95, 0.05), (0.5, 0.95)])
    for j, loop in enumerate(face.loop_indices):
      uv = coords[j % len(coords)]
      layer.data[loop].uv = tileUv(tile, *uv)
  obj['atlas_region'] = tile if not material else 'solid material'
  return obj

def bevel(obj, amount=0.035):
  """Keep a small live bevel on chunky structural edges."""
  modifier = obj.modifiers.new('Soft hand-cut edges', 'BEVEL')
  modifier.width = amount
  modifier.segments = 1
  return obj

def mirror(obj, axis=0):
  """Keep only a real half mesh and reconstruct it with a live mirror."""
  data = bmesh.new()
  data.from_mesh(obj.data)
  normal = [0, 0, 0]
  normal[axis] = 1
  bmesh.ops.bisect_plane(
    data,
    geom=list(data.verts) + list(data.edges) + list(data.faces),
    dist=0.00001,
    plane_co=(0, 0, 0),
    plane_no=normal,
    clear_inner=True,
    clear_outer=False,
  )
  for face in list(data.faces):
    if all(abs(vertex.co[axis]) < 0.00002 for vertex in face.verts):
      data.faces.remove(face)
  data.to_mesh(obj.data)
  data.free()
  modifier = obj.modifiers.new('Mirror - edit one half', 'MIRROR')
  modifier.use_axis = tuple(i == axis for i in range(3))
  modifier.use_clip = True
  modifier.use_mirror_merge = True
  modifier.merge_threshold = 0.0001
  obj['construction'] = 'Half mesh with unapplied Mirror'
  return obj

def box(name, center, size, tile='plaster', mirrored=False,
  edge=0.025, material=None):
  """Build a box in collection coordinates with textured faces."""
  x, y, z = center
  a, b, c = [value / 2 for value in size]
  vertices = [(x-a, y-b, z-c), (x+a, y-b, z-c),
    (x+a, y+b, z-c), (x-a, y+b, z-c),
    (x-a, y-b, z+c), (x+a, y-b, z+c),
    (x+a, y+b, z+c), (x-a, y+b, z+c)]
  faces = [(0, 3, 2, 1), (0, 1, 5, 4), (1, 2, 6, 5),
    (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7)]
  obj = meshObject(name, vertices, faces, tile, material=material)
  if tile in ('wood', 'bark') and not material:
    layer = obj.data.uv_layers.active
    for face in obj.data.polygons:
      points = [obj.data.vertices[i].co for i in face.vertices]
      minimum = [min(point[i] for point in points) for i in range(3)]
      spans = [max(point[i] for point in points)-minimum[i]
        for i in range(3)]
      axes = sorted(range(3), key=lambda i: spans[i], reverse=True)
      for loop in face.loop_indices:
        point = obj.data.vertices[obj.data.loops[loop].vertex_index].co
        u = .29 + .33*(point[axes[1]]-minimum[axes[1]])/max(.001,spans[axes[1]])
        v = .035 + .93*(point[axes[0]]-minimum[axes[0]])/max(.001,spans[axes[0]])
        layer.data[loop].uv = tileUv(tile,u,v)
  if mirrored:
    mirror(obj)
  if edge:
    bevel(obj, edge)
  return obj

def beam(name, start, end, width=0.12, tile='wood', mirrored=False):
  """Build a timber beam between two explicit endpoints."""
  start, end = Vector(start), Vector(end)
  direction = (end - start).normalized()
  reference = Vector((0, 1, 0))
  if abs(direction.dot(reference)) > 0.9:
    reference = Vector((1, 0, 0))
  side = direction.cross(reference).normalized() * width / 2
  other = direction.cross(side).normalized() * width / 2
  vertices = []
  for point in (start, end):
    vertices.extend([tuple(point-side-other), tuple(point+side-other),
      tuple(point+side+other), tuple(point-side+other)])
  faces = [(0, 3, 2, 1), (0, 1, 5, 4), (1, 2, 6, 5),
    (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7)]
  obj = meshObject(name, vertices, faces, tile)
  if mirrored:
    mirror(obj)
  return bevel(obj, 0.015)

def instance(name, source, location=(0, 0, 0), angle=0, scale=1):
  """Link a collection instance without copying its source meshes."""
  obj = bpy.data.objects.new(name, None)
  obj.instance_type = 'COLLECTION'
  obj.instance_collection = source
  obj.location = location
  obj.rotation_euler.z = angle
  obj.scale = (scale, scale, scale) if isinstance(scale, (int, float)) else scale
  obj.empty_display_size = 0.16
  Current.objects.link(obj)
  obj['construction'] = 'Linked collection instance'
  return obj

def linked(name, source, location, scale=(1, 1, 1), angle=0):
  """Place a separate object that shares an editable source mesh."""
  obj = source.copy()
  obj.name = name
  obj.data = source.data
  obj.location = location
  obj.scale = scale
  obj.rotation_euler.z = angle
  Current.objects.link(obj)
  return obj

def panel(name, center, width, height, tile, angle=0):
  """Place a front-facing textured architectural inset with thickness."""
  x, y, z = center
  corners = [(-width/2, 0, -height/2), (width/2, 0, -height/2),
    (width/2, 0, height/2), (-width/2, 0, height/2)]
  vertices = [(x+a*math.cos(angle), y+a*math.sin(angle), z+c)
    for a, b, c in corners]
  obj = meshObject(name, vertices, [(0, 1, 2, 3)], tile)
  modifier = obj.modifiers.new('Inset panel thickness', 'SOLIDIFY')
  modifier.thickness = 0.018
  return obj

def banner(name, x, y, bottom, width=0.48, height=0.96):
  """Hang the approved small-emblem cloth as one shallow wavy mesh."""
  vertices, faces, uvs = [], [], []
  for i in range(5):
    u = i / 4
    wave = 0.025 * math.sin(u * Pi * 2)
    vertices.extend([(x+(u-.5)*width, y+wave, bottom),
      (x+(u-.5)*width, y+wave, bottom+height)])
  for i in range(4):
    faces.append((2*i, 2*i+2, 2*i+3, 2*i+1))
    uvs.append([(i/4, 0), ((i+1)/4, 0),
      ((i+1)/4, 1), (i/4, 1)])
  obj = meshObject(name, vertices, faces, 'banner', uvs)
  thickness = obj.modifiers.new('Cloth thickness', 'SOLIDIFY')
  thickness.thickness = 0.012
  beam(name+' Hanging rod', (x-width*.64, y+.01, bottom+height+.045),
    (x+width*.64, y+.01, bottom+height+.045), 0.06)
  return obj

def gableBody(name, width, depth, eave, rise, bottom=0.15):
  """Create one half of a gabled wall volume and mirror it."""
  x, y = width/2, depth/2
  vertices = [(-x, -y, bottom), (x, -y, bottom),
    (x, -y, eave), (0, -y, eave+rise), (-x, -y, eave),
    (-x, y, bottom), (x, y, bottom),
    (x, y, eave), (0, y, eave+rise), (-x, y, eave)]
  faces = [(0, 1, 2, 4), (4, 2, 3), (6, 5, 9, 7), (7, 9, 8),
    (5, 0, 4, 9), (1, 6, 7, 2), (4, 3, 8, 9),
    (3, 2, 7, 8), (5, 6, 1, 0)]
  obj = meshObject(name, vertices, faces, 'plaster')
  mirror(obj)
  return bevel(obj, 0.035)

def roof(name, width, depth, eave, rise, courses=5):
  """Model overlapping blue roof courses on one mirrored roof slope."""
  half, length = width/2 + .16, depth/2 + .17
  vertices, faces, uvs = [], [], []
  for row in range(courses):
    t0, t1 = row/courses, min(1, (row+1.08)/courses)
    x0, x1 = half*(1-t0), half*(1-t1)
    z0 = eave+rise*t0+.04+.007*row
    z1 = eave+rise*t1+.04+.007*row
    for segment in range(2):
      y0, y1 = -length+segment*length, -length+(segment+1)*length
      base = len(vertices)
      vertices.extend([(x0, y0, z0), (x0, y1, z0),
        (x1, y1, z1), (x1, y0, z1),
        (x0, y0, z0-.065), (x0, y1, z0-.065),
        (x1, y1, z1-.065), (x1, y0, z1-.065)])
      faces.extend([tuple(base+i for i in f) for f in
        [(0, 1, 2, 3), (4, 7, 6, 5), (4, 5, 1, 0),
         (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]])
      low = (row % 4)*.25+.01
      high = (row % 4)*.25+.24
      for face in range(6):
        uvs.append([(0.015, low), (.985, low),
          (.985, high), (.015, high)])
  obj = meshObject(name+' Half courses', vertices, faces, 'roof', uvs)
  mirror(obj)
  bevel(obj, 0.012)
  beam(name+' Ridge', (0, -length-.03, eave+rise+.065),
    (0, length+.03, eave+rise+.065), .13)
  for side in (-1, 1):
    beam(name+' Gable verge', (0, side*length, eave+rise+.02),
      (half, side*length, eave-.005), .11, mirrored=True)
  return obj

def hipRoof(name, width, depth, bottom, rise):
  """Construct a mirrored four-sided steep blue roof."""
  a, b = width/2, depth/2
  vertices = [(-a, -b, bottom), (a, -b, bottom),
    (a, b, bottom), (-a, b, bottom), (0, 0, bottom+rise)]
  faces = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]
  obj = meshObject(name, vertices, faces, 'roof')
  mirror(obj)
  solid = obj.modifiers.new('Roof thickness', 'SOLIDIFY')
  solid.thickness = .07
  bevel(obj, .02)
  for x in (-a, a):
    for y in (-b, b):
      beam(name+' Hip edging', (x, y, bottom),
        (0, 0, bottom+rise+.025), .09)
  return obj

def frameGable(name, width, depth, eave, rise):
  """Add mirrored structural posts and explicit gable timber framing."""
  x, y = width/2, depth/2+.035
  for side in (-1, 1):
    beam(name+' Front corner posts', (x, side*y, .2),
      (x, side*y, eave), .14, mirrored=True)
    beam(name+' Crossbeam', (-x, side*y, eave),
      (x, side*y, eave), .14, mirrored=True)
    beam(name+' Gable diagonal', (0, side*y, eave+rise),
      (x, side*y, eave), .115, mirrored=True)
    beam(name+' Gable kingpost', (0, side*y, eave),
      (0, side*y, eave+rise), .105, mirrored=True)
  for side in (-1, 1):
    beam(name+' Side plate', (side*x, -y, .4),
      (side*x, y, .4), .12)

def stairs(name, y, width=0.85, count=3):
  """Build a short stone stair with repeated broad treads."""
  for i in range(count):
    box(name+f' Step {i+1}', (0, y-(count-i)*.16, .07*(i+1)),
      (width+.12*(count-i), .38, .14*(i+1)), 'stone', mirrored=True)

def cylinder(name, radius, length, tile='wood', sides=12,
  material=None):
  """Build a low-poly cylinder around its local vertical axis."""
  vertices = []
  for z in (-length/2, length/2):
    for i in range(sides):
      theta = 2*Pi*i/sides
      vertices.append((radius*math.cos(theta), radius*math.sin(theta), z))
  vertices.extend([(0, 0, -length/2), (0, 0, length/2)])
  faces, uvs = [], []
  for i in range(sides):
    j = (i+1) % sides
    faces.extend([(i, j, j+sides, i+sides),
      (sides*2, j, i), (sides*2+1, i+sides, j+sides)])
    uvs.extend([[(i/sides, 0), (j/sides if j else 1, 0),
      (j/sides if j else 1, 1), (i/sides, 1)],
      [(.5,.5), (.8,.2), (.2,.2)],
      [(.5,.5), (.2,.2), (.8,.2)]])
  return meshObject(name, vertices, faces, tile, uvs, material)

def rock(name, location, scale, tile='gray', seed=0):
  """Create a faceted irregular rock with atlas-isolated mineral UVs."""
  data = bmesh.new()
  bmesh.ops.create_icosphere(data, subdivisions=1, radius=1)
  rng = random.Random(seed)
  for vertex in data.verts:
    vertex.co *= rng.uniform(.87, 1.13)
  mesh = bpy.data.meshes.new(name+' Mesh')
  data.to_mesh(mesh)
  data.free()
  obj = bpy.data.objects.new(name, mesh)
  Current.objects.link(obj)
  obj.location = location
  obj.scale = scale
  mesh.materials.append(Atlas)
  if tile == 'gray' and name.startswith('Mine'):
    mesh.materials[0] = RockAtlas
  uvLayer = mesh.uv_layers.new(name='Building Atlas UV')
  for face in mesh.polygons:
    for loop in face.loop_indices:
      vertex = mesh.vertices[mesh.loops[loop].vertex_index].co
      u, v = (vertex.x+1)/2, (vertex.z+1)/2
      if tile == 'gray':
        u, v = .17+u*.18, .16+v*.20
      uvLayer.data[loop].uv = tileUv(tile, u, v)
  obj['atlas_region'] = tile
  return obj

def makeWing():
  """Build the one mirrored wing used by three town hall instances."""
  group = useCollection('MODULE - Town hall mirrored wing')
  gableBody('Wing mirrored plaster body', 1.55, 2.35, 1.65, 1.05)
  box('Wing mirrored foundation', (0, 0, .17), (1.72, 2.47, .34),
    'stone', mirrored=True)
  roof('Wing roof', 1.65, 2.45, 1.66, 1.05)
  frameGable('Wing framing', 1.55, 2.35, 1.65, 1.05)
  panel('Wing front window', (0, -1.193, 1.0), .63, .71, 'window')
  for y in (-.62, .52):
    for side in (-1, 1):
      panel('Wing side window', (side*.792, y, 1.03),
        .59, .69, 'window', angle=side*Pi/2)
  group['construction'] = 'Mirrored wing source, three linked placements'
  return group

def makeTownHall(wing):
  """Assemble a mirrored central structure with three mirrored wings."""
  group = useCollection('01 Town Hall')
  box('Hall central mirrored foundation', (0, .06, .2),
    (1.87, 1.93, .4), 'stone', mirrored=True)
  box('Hall central mirrored tower', (0, .06, 1.83),
    (1.63, 1.68, 3.1), 'plaster', mirrored=True)
  for x in (-.78, .78):
    for y in (-.76, .88):
      beam('Hall central corner beam', (x, y, .4), (x, y, 3.37), .16)
  box('Hall central mirrored crown', (0, .06, 3.39),
    (1.85, 1.92, .2), 'wood', mirrored=True)
  hipRoof('Hall mirrored pavilion roof', 2.04, 2.1, 3.5, 1.12)
  instance('Hall Wing 1 - left - live mirror', wing,
    (-1.37, .02, 0), -Pi/2)
  instance('Hall Wing 2 - right - live mirror', wing,
    (1.37, .02, 0), Pi/2)
  instance('Hall Wing 3 - entry - live mirror', wing,
    (0, -1.06, 0), scale=(.82, .75, .82))
  panel('Hall main entrance', (0, -1.97, .85), .68, 1.13, 'door')
  beam('Hall entrance lintel', (-.47, -1.975, 1.5),
    (.47, -1.975, 1.5), .16)
  stairs('Hall entrance', -1.95, .85)
  banner('Hall civic banner', 0, -.809, 2.30, .52, .93)
  for side in (-1, 1):
    panel('Hall tower side window', (side*.827, .05, 2.83),
      .58, .65, 'window', angle=side*Pi/2)
  beam('Hall flagpole', (0, .06, 4.57), (0, .06, 5.12), .045)
  flag = meshObject('Hall blue pennant', [(0,.06,5.12),(.55,.08,5.12),
    (.44,.10,4.94),(.02,.06,4.91)], [(0,1,2,3)], 'banner',
    [[(.04,.85),(.3,.85),(.3,.98),(.04,.98)]])
  group['wing_count'] = 3
  return group

def makeFence():
  """Create a genuinely half-modeled farm fence for four rotations."""
  group = useCollection('MODULE - Mirrored farm fence')
  for x in (0, .83, 1.66):
    obj = box('Fence half post', (x, 0, .41), (.135, .135, .82),
      'wood', mirrored=True)
  for z in (.24, .57):
    box('Fence mirrored rail', (.83, -.01, z), (1.64, .10, .12),
      'wood', mirrored=True)
  group['construction'] = 'Half fence mirrored over X, repeated 4 times'
  return group

def makePumpkin():
  """Build a separate ribbed pumpkin mesh and leaf rosette source."""
  group = useCollection('MODULE - Pumpkin and leaves')
  vertices, faces, uvs = [], [], []
  rings, sides = 9, 32
  for i in range(rings+1):
    phi = Pi * (.035+.93*i/rings)
    for j in range(sides+1):
      theta = 2*Pi*j/sides
      radius = .27*math.sin(phi)*(1+.09*math.cos(theta*8))
      vertices.append((radius*math.cos(theta), radius*math.sin(theta),
        .25+.24*math.cos(phi)))
  for i in range(rings):
    for j in range(sides):
      a = i*(sides+1)+j
      faces.append((a,a+1,a+sides+2,a+sides+1))
      uvs.append([(j/sides,1-i/rings),((j+1)/sides,1-i/rings),
        ((j+1)/sides,1-(i+1)/rings),(j/sides,1-(i+1)/rings)])
  meshObject('Pumpkin separate ribbed fruit', vertices, faces, 'pumpkin', uvs)
  beam('Pumpkin stem', (0,0,.46), (.045,.01,.62), .075, 'bark')
  outline = [(0,0,.17),(-.15,.12,.27),(-.34,.20,.25),
    (-.30,.37,.23),(-.48,.49,.20),(-.2,.51,.28),
    (0,.75,.23),(.2,.51,.28),(.48,.49,.20),
    (.30,.37,.23),(.34,.20,.25),(.15,.12,.27)]
  for i in range(5):
    theta = i*2*Pi/5
    verts = [(.79*(x*math.cos(theta)-y*math.sin(theta)),
      .79*(x*math.sin(theta)+y*math.cos(theta)), z*.75)
      for x,y,z in outline]
    verts.append((0,.28,.26))
    leafFaces = [(12,j,(j+1)%12) for j in range(12)]
    leafUvs = [[(.5,.5),(.5+outline[j][0],outline[j][1]),
      (.5+outline[(j+1)%12][0],outline[(j+1)%12][1])]
      for j in range(12)]
    meshObject('Pumpkin leaf rosette', verts, leafFaces, 'leaf', leafUvs)
  return group

def makeFarm(fence, pumpkin):
  """Instance four fences and an orderly scale-varied pumpkin crop."""
  group = useCollection('02 Farm')
  box('Farm soil bed', (0,0,.085), (3.35,3.35,.17), 'soil', edge=.045)
  for i in range(4):
    theta = i*Pi/2
    location = (1.67*math.sin(theta), -1.67*math.cos(theta), .13)
    obj = instance(f'Farm fence {i+1} - linked quarter turn', fence,
      location, theta)
    obj['rotation_degrees'] = i*90
  for row in range(4):
    for column in range(4):
      scale = Rng.uniform(.70,.91)
      obj = instance(f'Pumpkin row {row+1} column {column+1}', pumpkin,
        ((column-1.5)*.77,(row-1.5)*.77,.18),
        Rng.uniform(-.5,.5), scale)
      obj['row'] = row+1
      obj['column'] = column+1
  group['fence_count'] = 4
  group['pumpkin_count'] = 16
  return group

def makeBarracks():
  """Model a broad mirrored barracks with reinforced double doors."""
  group = useCollection('03 Barracks')
  gableBody('Barracks mirrored hall', 3.15, 2.35, 2.12, 1.4)
  box('Barracks mirrored stone footing', (0,0,.24),
    (3.34,2.53,.48), 'stone', mirrored=True)
  roof('Barracks roof', 3.28,2.46,2.13,1.4,6)
  frameGable('Barracks framing',3.15,2.35,2.12,1.4)
  panel('Barracks double entrance', (0,-1.198,1.09),1.43,1.65,'doubleDoor')
  for x in (-1.42,1.42):
    box('Barracks stone doorway pier', (x,-1.24,1.0),
      (.30,.36,1.60),'stone')
  for x in (-1.0,1.0):
    banner('Barracks pennon',x,-1.234,1.49,.34,.63)
  banner('Barracks gable banner',0,-1.39,2.15,.52,.90)
  for y in (-.55,.58):
    panel('Barracks side window',(1.596,y,1.34),.60,.79,
      'archWindow',Pi/2)
  stairs('Barracks approach',-1.30,1.62)
  return group

def makeLog():
  """Build the shared timber log source with visible polygonal ends."""
  group = useCollection('MODULE - Sawmill log')
  obj = cylinder('Log bark',.17,1.65,'bark')
  obj.rotation_euler.x = Pi/2
  for y in (-.83,.83):
    cap = cylinder('Log cut end',.153,.016,'wood')
    cap.rotation_euler.x = Pi/2
    cap.location.y = y
  return group

def makeLumber(log):
  """Build a mirrored open mill and instance stacks of timber."""
  group = useCollection('04 Lumber Mill')
  box('Mill mirrored slab',(0,0,.13),(3.2,2.75,.26),
    'stone',mirrored=True)
  for y in (-1.12,1.12):
    box('Mill mirrored corner posts',(.99,y,1.08),(.20,.20,1.9),
      'wood',mirrored=True)
    beam('Mill mirrored crossbeam',(-1.14,y,1.94),
      (1.14,y,1.94),.22,mirrored=True)
    beam('Mill mirrored corner brace',(.65,y,1.91),
      (1.0,y,1.52),.12,mirrored=True)
  box('Mill rear half wall',(0,1.09,.77),(2.1,.16,1.1),
    'plaster',mirrored=True)
  roof('Mill mirrored roof',2.6,2.65,2.01,1.2,5)
  for side in (-1,1):
    beam('Mill roof kingpost',(0,side*1.33,2.01),
      (0,side*1.33,3.21),.12,mirrored=True)
  banner('Mill hanging sign',0,-1.53,2.00,.44,.75)
  for i in range(5):
    for j in range(2 if i%2 else 3):
      instance(f'Stacked log {i}-{j}',log,
        (.75+j*.28,.04,.40+i*.28),scale=.8)
  box('Sawbench top',(-.38,-.48,.83),(1.15,1.5,.15),'wood')
  for x in (-.83,.04):
    for y in (-1.0,.08):
      box('Sawbench foot',(x,y,.50),(.13,.13,.65),'wood')
  teeth, verts = 24, []
  for i in range(teeth*2):
    theta = 2*Pi*i/(teeth*2)
    radius = .48 if i%2==0 else .40
    verts.append((-.30+radius*math.cos(theta),-.82,
      .97+radius*math.sin(theta)))
  verts.append((-.3,-.82,.97))
  blade = meshObject('Exposed circular saw blade',verts,
    [(teeth*2,i,(i+1)%(teeth*2)) for i in range(teeth*2)],
    material=Steel)
  thick = blade.modifiers.new('Saw blade thickness','SOLIDIFY')
  thick.thickness = .035
  hub = cylinder('Saw iron hub',.11,.10,material=Iron)
  hub.location = (-.3,-.88,.97)
  hub.rotation_euler.x = Pi/2
  for i in range(3):
    box('Finished board pile',(-.60,-1.48,.31+i*.09),
      (1.34,.35,.085),'wood')
  return group

def radial(obj, offset):
  """Keep six actual radial array sectors with 60-degree rotation."""
  modifier = obj.modifiers.new('Sixfold symmetry - 6 x 60 degrees','ARRAY')
  modifier.count = 6
  modifier.use_relative_offset = False
  modifier.use_constant_offset = False
  modifier.use_object_offset = True
  modifier.offset_object = offset
  modifier.use_merge_vertices = True
  modifier.use_merge_vertices_cap = True
  modifier.merge_threshold = .0002
  obj['symmetry_order'] = 6
  return obj

def hexProfile(name, rings, tile, offset):
  """Build a mirrored hexagonal sector from an explicit radial profile."""
  verts, faces = [], []
  for z,radius in rings:
    verts.extend([(0,0,z),(-radius*.5,-radius*.8660254,z),
      (radius*.5,-radius*.8660254,z)])
  for i in range(len(rings)-1):
    k=i*3
    faces.extend([(k+1,k+2,k+5,k+4),(k,k+1,k+4,k+3),
      (k+2,k,k+3,k+5)])
  faces.extend([(0,2,1),(len(verts)-3,len(verts)-2,len(verts)-1)])
  obj=meshObject(name,verts,faces,tile)
  mirror(obj)
  radial(obj,offset)
  bevel(obj,.022)
  return obj

def makeTower():
  """Create a sixfold stone watchtower with real windows and no crystal."""
  group=useCollection('05 Tower')
  offset=bpy.data.objects.new('Tower 60 degree radial controller',None)
  Current.objects.link(offset)
  offset.rotation_euler.z=Pi/3
  offset.empty_display_size=.4
  offset.hide_render=True
  hexProfile('Tower half-sector body',[(.05,1.2),(.2,1.24),
    (.64,1.12),(1.03,.91),(2.89,.83),(3.08,1.04)],'stone',offset)
  hexProfile('Tower blue upper band',[(2.94,1.06),(3.13,1.06)],
    'roof',offset)
  hexProfile('Tower parapet floor',[(3.13,1.10),(3.31,1.10)],
    'stone',offset)
  buttress=meshObject('Tower buttress sector',
    [(-.18,-1.31,.1),(.18,-1.31,.1),(.15,-.90,1.15),
     (-.15,-.90,1.15),(-.18,-1.04,.1),(.18,-1.04,.1),
     (.15,-.70,1.15),(-.15,-.70,1.15)],
    [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),
     (2,6,7,3),(3,7,4,0)],'plaster')
  radial(buttress,offset)
  bevel(buttress,.045)
  crenel=box('Tower crenellation sector',(0,-.91,3.43),
    (.34,.27,.49),'stone')
  radial(crenel,offset)
  hexProfile('Tower windowed lookout',[(3.30,.65),(4.00,.65)],
    'plaster',offset)
  window=panel('Tower arched window sector',(0,-.57,3.67),
    .46,.59,'archWindow')
  radial(window,offset)
  verts=[(-.40,-.69,4.02),(.40,-.69,4.02),(0,0,4.73)]
  roofObj=meshObject('Tower blue roof sector',verts,[(0,1,2)],'roof')
  radial(roofObj,offset)
  solid=roofObj.modifiers.new('Roof thickness','SOLIDIFY')
  solid.thickness=.055
  edge=beam('Tower roof radial timber',(.40,-.69,4.02),(0,0,4.73),.075)
  radial(edge,offset)
  frontBanner=banner('Tower radial banner',0,-.80,1.72,.43,.94)
  radial(frontBanner,offset)
  rod=Current.objects.get('Tower radial banner Hanging rod')
  radial(rod,offset)
  group['symmetry_order']=6
  return group

def makeStable(fence):
  """Make an open three-bay stable with linked stall partitions."""
  group=useCollection('06 Stables and Kennels')
  box('Stable mirrored foundation',(0,0,.15),(3.62,2.42,.30),
    'stone',mirrored=True)
  box('Stable back wall',(0,.98,.90),(3.37,.17,1.5),
    'plaster',mirrored=True)
  for x in (-1.65,-.55,.55,1.65):
    box('Stable bay timber post',(x,-1.01,.97),(.17,.18,1.74),'wood')
    box('Stable stall divider',(x,.08,.70),(.12,1.9,1.03),'wood')
  for x in (-1.10,0,1.10):
    box('Stable half-height stall door',(x,-1.03,.55),
      (.91,.12,.7),'wood')
    beam('Stable door rail',(x-.48,-1.105,.75),
      (x+.48,-1.105,.75),.09)
  beam('Stable front header',(-1.78,-1.02,1.82),
    (1.78,-1.02,1.82),.19)
  before=set(Current.objects)
  roof('Stable roof',2.4,3.6,1.84,1.09,5)
  for obj in set(Current.objects)-before:
    obj.rotation_euler.z=Pi/2
  banner('Stable bay sign',0,-1.18,1.16,.28,.53)
  box('Stable right end gable base',(1.65,0,.97),(.15,2.12,1.69),'plaster')
  for y in (-.6,.6):
    panel('Stable end window',(1.735,y,1.13),.43,.59,'window',Pi/2)
  for i in range(3):
    box('Stable paddock posts',(2.35,-.91+i*.68,.47),
      (.13,.13,.86),'wood')
  for z in (.36,.67):
    beam('Stable paddock side',(2.35,-.98,z),(2.35,.62,z),.09)
    beam('Stable paddock front',(1.67,-.98,z),(2.35,-.98,z),.09)
  box('Stable feed trough',(2.08,.21,.39),(.50,.78,.36),'wood')
  box('Stable feed surface',(2.08,.21,.578),(.39,.66,.012),'soil',edge=0)
  return group

def makeChurch():
  """Create a chapel nave with an attached open belfry."""
  group=useCollection('07 Church and Temple')
  gableBody('Chapel mirrored nave',1.95,2.95,1.96,1.37)
  box('Chapel mirrored footing',(0,0,.20),(2.13,3.1,.4),
    'stone',mirrored=True)
  roof('Chapel roof',2.04,3.08,1.98,1.37,6)
  panel('Chapel arched entrance',(0,-1.506,.97),.90,1.49,'archDoor')
  stairs('Chapel front steps',-1.54,1.0)
  for y in (-.73,.49):
    for side in (-1,1):
      panel('Chapel lancet',(side*.995,y,1.28),.51,.95,
        'archWindow',side*Pi/2)
  belfry=collection('MODULE - Chapel belfry')
  global Current
  Current=belfry
  box('Belfry mirrored shaft',(0,0,1.43),(1.01,1.02,2.86),
    'stone',mirrored=True)
  box('Belfry lower ledge',(0,0,2.80),(1.17,1.18,.16),'stone',mirrored=True)
  for x in (-.43,.43):
    for y in (-.43,.43):
      box('Belfry open arcade pier',(x,y,3.23),(.18,.18,.80),'stone')
  box('Belfry arcade crown',(0,0,3.63),(1.09,1.09,.16),'stone',mirrored=True)
  for side in (-1,1):
    beam('Belfry arch spring',(-.39,side*.47,3.32),
      (-.17,side*.47,3.58),.14)
    beam('Belfry arch spring',(.39,side*.47,3.32),
      (.17,side*.47,3.58),.14)
  hipRoof('Belfry blue roof',1.26,1.26,3.76,.69)
  bell=cylinder('Belfry iron bell',.18,.27,material=Iron)
  bell.location.z=3.25
  banner('Belfry banner',0,-.533,1.82,.43,.80)
  Current=group
  instance('Attached chapel belfry',belfry,(1.10,-.85,0),scale=(1,1,1.25))
  return group

def makeAnvil():
  """Create a compact blacksmith anvil with a projecting tapered horn."""
  profile=[(-.32,0),(.32,0),(.27,.12),(.12,.19),(.15,.32),
    (.36,.39),(.36,.49),(-.33,.49),(-.54,.41),(-.68,.35),
    (-.36,.34),(-.16,.31),(-.13,.17),(-.29,.12)]
  verts=[]
  for y in (-.16,.16):
    verts.extend([(x,y,z) for x,z in profile])
  n=len(profile)
  faces=[]
  for i in range(n):
    j=(i+1)%n
    faces.append((i,j,j+n,i+n))
  faces.extend([tuple(range(n-1,-1,-1)),tuple(range(n,n*2))])
  obj=meshObject('Forged iron anvil',verts,faces,material=Steel)
  obj.location=(.60,-1.78,.42)
  bevel(obj,.022)
  return obj

def makeBlacksmith():
  """Assemble a smithy, open forge bay, chimney, and separate anvil."""
  group=useCollection('08 Blacksmith')
  gableBody('Smith mirrored main workshop',2.32,2.19,1.73,1.02)
  box('Smith mirrored footing',(0,0,.16),(2.49,2.35,.32),
    'stone',mirrored=True)
  roof('Smith main roof',2.48,2.35,1.75,1.06,5)
  frameGable('Smith workshop framing',2.32,2.19,1.73,1.02)
  panel('Smith side window',(1.18,.25,1.08),.62,.72,'window',Pi/2)
  panel('Smith entry',(-.68,-1.117,.82),.60,1.20,'door')
  banner('Smith gable cloth',0,-1.20,1.75,.43,.79)
  for x in (-1.13,1.13):
    box('Smith porch posts',(x,-1.81,.86),(.17,.17,1.65),'wood')
  beam('Smith porch header',(-1.24,-1.81,1.67),(1.24,-1.81,1.67),.17)
  verts=[(-1.3,-1.9,1.75),(1.3,-1.9,1.75),
    (1.3,-1.04,2.10),(-1.3,-1.04,2.10)]
  awning=meshObject('Smith blue forge awning',verts,[(0,1,2,3)],'roof')
  thick=awning.modifiers.new('Awning thickness','SOLIDIFY')
  thick.thickness=.08
  box('Smith hearth base',(.29,-1.41,.38),(1.14,.77,.45),'gray')
  for x in (-.17,.77):
    box('Smith hearth side',(x,-1.37,.92),(.22,.58,.93),'gray')
  box('Smith furnace dark recess',(.30,-1.13,.88),(.75,.05,.7),
    material=Dark)
  box('Smith glowing coals',(.30,-1.43,.66),(.63,.40,.07),material=Ember)
  for i in range(5):
    obj=rock('Forge flame',(.03+i*.13,-1.43,.78),
      (.09,.09,.16+Rng.random()*.12),'gold',40+i)
    obj.data.materials.clear()
    obj.data.materials.append(Fire)
    obj['atlas_region']='emissive fire'
  box('Smith chimney stack',(.33,-.75,2.37),(.69,.65,2.10),'gray')
  box('Smith chimney cap',(.33,-.75,3.42),(.84,.80,.19),'gray')
  box('Smith chimney dark opening',(.33,-.75,3.52),(.54,.49,.018),
    material=Dark,edge=0)
  stump=cylinder('Anvil stump',.33,.4,'bark')
  stump.location=(.6,-1.78,.23)
  makeAnvil()
  return group

def makeMine():
  """Model a mirrored timber entrance for placement against map rocks."""
  group=useCollection('09 Gold Mine')
  box('Mine dark tunnel',(0,-.56,.885),(1.04,.18,1.65),
    material=Dark,mirrored=True)
  box('Mine timber upright',(.65,-.70,.92),(.24,.25,1.84),
    'wood',mirrored=True)
  beam('Mine diagonal knee',(.65,-.74,1.40),(.3705,-.74,1.77),
    .16,mirrored=True)
  box('Mine timber header',(0,-.70,1.91),(1.63,.29,.28),
    'wood',mirrored=True)
  beam('Mine roofless depth support',(.65,-.83,1.90),(.65,.35,1.90),
    .18,mirrored=True)
  for x in (-.32,.32):
    box('Mine rail',(x,-1.1,.14),(.055,2.63,.08),material=Iron)
  tieSource=box('Mine sleeper 1',(0,0,0),(1.05,.14,.09),'wood')
  tieSource.location=(0,-2.23,.072)
  for i in range(1,7):
    linked('Mine linked rail sleeper',tieSource,(0,-2.23+i*.37,.072))
  cart=collection('MODULE - Mine cart')
  global Current
  Current=cart
  box('Cart bed',(0,0,.28),(.80,.92,.12),'wood')
  for x in (-.39,.39):
    box('Cart side plank',(x,0,.56),(.10,.92,.52),'wood')
  for y in (-.45,.45):
    box('Cart end plank',(0,y,.56),(.84,.10,.52),'wood')
  for x in (-.43,.43):
    for y in (-.31,.31):
      wheel=cylinder('Cart iron wheel',.18,.08,material=Iron)
      wheel.rotation_euler.y=Pi/2
      wheel.location=(x,y,.22)
  for i in range(7):
    rock('Cart raw gold nugget',(Rng.uniform(-.22,.22),
      Rng.uniform(-.26,.26),.79+Rng.uniform(-.02,.12)),
      (.16,.14,.17),'gold',71+i)
  Current=group
  instance('Mine ore cart - linked source',cart,(.01,-1.35,.11))
  group['construction']='Entrance and gold cart; map provides surrounding rocks'
  return group

def camera(name, group, location, target, scale):
  """Create an orthographic camera aimed at an explicit point."""
  data=bpy.data.cameras.new(name)
  obj=bpy.data.objects.new(name,data)
  group.objects.link(obj)
  obj.location=location
  obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
  data.type='ORTHO'
  data.ortho_scale=scale
  data.lens=50
  return obj

def areaLight(name, group, location, energy, size):
  """Create a soft studio light shared by the asset stages."""
  data=bpy.data.lights.new(name,'AREA')
  data.energy=energy
  data.shape='DISK'
  data.size=size
  obj=bpy.data.objects.new(name,data)
  group.objects.link(obj)
  obj.location=location
  obj.rotation_euler=(-obj.location).to_track_quat('-Z','Y').to_euler()
  return obj

def settings(scene, resolution=2200, samples=48):
  """Configure deterministic CPU rendering with soft ambient lighting."""
  scene.render.engine='CYCLES'
  scene.cycles.samples=samples
  scene.cycles.use_denoising=True
  scene.cycles.use_adaptive_sampling=True
  scene.cycles.adaptive_threshold=.055
  scene.render.resolution_x=resolution
  scene.render.resolution_y=resolution
  scene.render.resolution_percentage=100
  scene.render.image_settings.file_format='PNG'
  scene.render.film_transparent=False
  scene.world=World
  scene.view_settings.view_transform='Standard'
  scene.view_settings.look='None'
  scene.view_settings.exposure=-.3
  scene.view_settings.gamma=1

def makeStage(groups):
  """Arrange real asset instances on a labeled camera-aligned 3x3 stage."""
  global Current
  scene=bpy.context.scene
  scene.name='00 - Building Review Stage'
  stage=useCollection('STAGE - Nine linked assets')
  scene.collection.children.link(stage)
  spacing=7.2
  elevation=math.radians(43)
  sine, cosine=math.sin(elevation),math.cos(elevation)
  labels=['Town Hall','Farm','Barracks','Lumber Mill','Tower',
    'Stables / Kennels','Church / Temple','Blacksmith','Gold Mine']
  scales=[1.0,1.12,1.15,1.14,1.06,1.09,1.06,1.13,1.40]
  for i,group in enumerate(groups):
    col,row=i%3,i//3
    projected=(1-row)*spacing-1.10
    if i == 8:
      projected += .30
    obj=instance(labels[i]+' Stage instance',group,
      ((col-1)*spacing,projected/sine,0),-Pi/6,scales[i])
    obj['stage_cell']=f'{row+1},{col+1}'
  box('White studio ground',(0,0,-.18),(70,70,.25),
    material=Ground,edge=0)
  cam=camera('CAMERA - 3x3 orthographic sheet',stage,
    (0,-65*cosine,65*sine),(0,0,0),22.1)
  scene.camera=cam
  areaLight('Large softbox',stage,(-15,-20,35),6200,18)
  areaLight('Front fill',stage,(18,-10,24),2200,16)
  sunData=bpy.data.lights.new('Gentle directional key','SUN')
  sunData.energy=1.15
  sunData.angle=.18
  sun=bpy.data.objects.new('Gentle directional key',sunData)
  stage.objects.link(sun)
  sun.rotation_euler=(.4,-.55,-.4)
  overlay=collection('STAGE - Labels and dividers')
  scene.collection.children.link(overlay)
  right=Vector((1,0,0))
  up=Vector((0,sine,cosine))
  toward=Vector((0,-cosine,sine))
  plane=toward*25
  for value in (-3.6,3.6):
    for vertical in (True,False):
      if vertical:
        pts=[(value-.025,-10.9),(value+.025,-10.9),
          (value+.025,10.9),(value-.025,10.9)]
      else:
        pts=[(-10.9,value-.025),(10.9,value-.025),
          (10.9,value+.025),(-10.9,value+.025)]
      vertices=[tuple(plane+right*x+up*y) for x,y in pts]
      divider=meshObject('Stage grid divider',vertices,[(0,1,2,3)],
        material=Grid,group=overlay)
      divider.visible_shadow=False
      divider.visible_diffuse=False
      divider.visible_glossy=False
  for i,label in enumerate(labels):
    data=bpy.data.curves.new(label+' Label','FONT')
    data.body=label
    data.align_x='CENTER'
    data.align_y='CENTER'
    data.size=.38
    data.space_character=1.06
    data.extrude=0
    obj=bpy.data.objects.new(label+' Label',data)
    overlay.objects.link(obj)
    data.materials.append(Ink)
    obj.location=plane+right*((i%3-1)*spacing)+up*((1-i//3)*spacing-3.06)
    obj.rotation_euler=cam.rotation_euler
    obj.visible_shadow=False
    obj.visible_diffuse=False
    obj.visible_glossy=False
  settings(scene)
  scene['design_reference']='assets/concept.png'
  scene['atlas_reference']='assets/buildings-atlas.png'
  scene['modeling_notes']='Mirrors and collection instances remain editable.'
  return scene

def makeAssetScenes(groups):
  """Expose every source collection in an individual editing scene."""
  for group in groups:
    scene=bpy.data.scenes.new(group.name+' - Edit source')
    scene.collection.children.link(group)
    utilities=collection(group.name+' - Preview utilities')
    scene.collection.children.link(utilities)
    target=(0,0,group.get('preview_height',1.7))
    scene.camera=camera(group.name+' Camera',utilities,
      (7,-11,9),target,group.get('preview_scale',7.2))
    areaLight(group.name+' Softbox',utilities,(-5,-8,12),1700,7)
    areaLight(group.name+' Fill',utilities,(7,-3,6),500,5)
    settings(scene,1000,24)

def audit(groups):
  """Write actual scene structure and material usage for independent review."""
  meshes=[obj for obj in bpy.data.objects if obj.type=='MESH']
  mirrored=[obj.name for obj in meshes if
    any(mod.type=='MIRROR' for mod in obj.modifiers)]
  arrays=[{'object':obj.name,'count':mod.count,
    'rotation_degrees':round(math.degrees(mod.offset_object.rotation_euler.z),2)}
    for obj in meshes for mod in obj.modifiers
    if mod.type=='ARRAY' and mod.offset_object]
  placements=[{'object':obj.name,'source':obj.instance_collection.name,
    'location':list(obj.location),'scale':list(obj.scale),
    'rotation_degrees':round(math.degrees(obj.rotation_euler.z),2)}
    for obj in bpy.data.objects if obj.instance_type=='COLLECTION']
  data={'asset_collections':[group.name for group in groups],
    'mirror_count':len(mirrored),'mirrored_objects':mirrored,
    'radial_arrays':arrays,'collection_instances':placements,
    'source_mesh_count':len(bpy.data.meshes),
    'source_faces':sum(len(mesh.polygons) for mesh in bpy.data.meshes),
    'atlas_packed':bool(AtlasImage.packed_file),
    'atlas_regions':{tile:sum(obj.get('atlas_region')==tile for obj in meshes)
      for tile in Tiles},
    'missing_uvs':[obj.name for obj in meshes if not obj.data.uv_layers],
    'source_scenes':[scene.name for scene in bpy.data.scenes]}
  (Root/'reviews'/'structure-audit.json').write_text(json.dumps(data,indent=2))
  assert len(groups)==9
  assert len(mirrored)>30
  assert all(item['count']==6 for item in arrays)
  assert not data['missing_uvs']
  assert AtlasImage.packed_file
  return data

bpy.ops.wm.read_factory_settings(use_empty=True)
AtlasImage=bpy.data.images.load(str(Root/'assets'/'buildings-atlas.png'))
AtlasImage.pack()
Atlas=bpy.data.materials.new('Approved painted building atlas')
Atlas.use_nodes=True
shader=Atlas.node_tree.nodes.get('Principled BSDF')
shader.inputs['Roughness'].default_value=.83
shader.inputs['Specular IOR Level'].default_value=.18
texture=Atlas.node_tree.nodes.new('ShaderNodeTexImage')
texture.image=AtlasImage
texture.interpolation='Linear'
texture.extension='EXTEND'
Atlas.node_tree.links.new(texture.outputs['Color'],shader.inputs['Base Color'])
Atlas.diffuse_color=(.63,.46,.27,1)
RockAtlas=Atlas.copy()
RockAtlas.name='Neutral mine stone - atlas with gray tint'
rockNodes=RockAtlas.node_tree.nodes
rockTexture=next(node for node in rockNodes if node.type=='TEX_IMAGE')
rockShader=rockNodes.get('Principled BSDF')
tint=rockNodes.new('ShaderNodeMixRGB')
tint.blend_type='MULTIPLY'
tint.inputs[0].default_value=1
tint.inputs[2].default_value=(.43,.47,.54,1)
RockAtlas.node_tree.links.new(rockTexture.outputs['Color'],tint.inputs[1])
RockAtlas.node_tree.links.new(tint.outputs[0],rockShader.inputs['Base Color'])
Iron=solidMaterial('Dark wrought iron',(.07,.085,.105),.6)
Steel=solidMaterial('Forged steel',(.29,.34,.40),.42)
Dark=solidMaterial('Deep openings',(.018,.023,.027),1)
Ember=solidMaterial('Orange forge coals',(.9,.095,.007),.8,1.4)
Fire=solidMaterial('Warm forge fire',(1,.33,.017),.7,1.9)
Ground=solidMaterial('Warm off-white stage',(.84,.835,.81),1)
Grid=flatMaterial('Pale grid',(.68,.73,.71))
Ink=flatMaterial('Slate lettering',(.025,.039,.06))
World=bpy.data.worlds.new('Neutral studio environment')
World.use_nodes=True
World.node_tree.nodes['Background'].inputs[0].default_value=(.78,.83,.91,1)
World.node_tree.nodes['Background'].inputs[1].default_value=.55
wing=makeWing()
town=makeTownHall(wing)
fence=makeFence()
pumpkin=makePumpkin()
farm=makeFarm(fence,pumpkin)
barracks=makeBarracks()
log=makeLog()
lumber=makeLumber(log)
tower=makeTower()
stable=makeStable(fence)
church=makeChurch()
smith=makeBlacksmith()
mine=makeMine()
groups=[town,farm,barracks,lumber,tower,stable,church,smith,mine]
stage=makeStage(groups)
makeAssetScenes(groups)
modules=[wing,fence,pumpkin,log,
  bpy.data.collections['MODULE - Chapel belfry'],
  bpy.data.collections['MODULE - Mine cart']]
for module,scale,height in zip(modules,[4.7,4.2,2.1,2.7,6.1,2.4],
  [1.25,.4,.24,0,2.1,.5]):
  module['preview_scale']=scale
  module['preview_height']=height
makeAssetScenes(modules)
for group in groups+modules:
  group.asset_mark()
bpy.context.window.scene=stage
for screen in bpy.data.screens:
  for area in screen.areas:
    if area.type=='VIEW_3D':
      area.spaces.active.region_3d.view_perspective='CAMERA'
      area.spaces.active.shading.type='MATERIAL'
      area.spaces.active.overlay.show_overlays=False
      area.spaces.active.region_3d.view_camera_zoom=0
report=audit(groups)
notes=bpy.data.texts.new('START HERE - Building kit')
notes.write('Polyworld building kit.\n\nThe opening scene is the actual 3x3 '
  'rendering stage. All nine models are linked collection instances.\n'
  'Use the scene dropdown to choose any numbered Edit source scene.\n'
  'MODULE scenes expose the shared wing, fence, pumpkin, log, belfry '
  'and cart geometry directly for editing.\n'
  'Town Hall contains a mirrored center and three linked mirrored wings.\n'
  'Farm uses four rotated mirrored fence instances and sixteen pumpkin '
  'collection instances with shared meshes and varied scales.\n'
  'Tower uses live Mirror and sixfold Array modifiers with a 60 degree '
  'controller. No crystal geometry exists.\n'
  'Mine is a mirrored timber entrance with a gold cart and short rails. '
  'Place it against map rocks.\n'
  'The approved atlas is packed in the file. UVs isolate all 16 regions.\n'
  'Mirrors, arrays and linked source data have deliberately not been applied.\n')
stage.render.filepath=str(Root/'renders'/'buildings-stage.png')
stage.render.resolution_x=2560
stage.render.resolution_y=2560
stage.cycles.samples=64
bpy.ops.wm.save_as_mainfile(filepath=str(Root/'polyworld-buildings.blend'))
print('STRUCTURE',json.dumps({key:report[key] for key in
  ['mirror_count','source_mesh_count','source_faces','atlas_packed']}),flush=True)
if '--final' not in sys.argv:
  stage.render.resolution_x=1800
  stage.render.resolution_y=1800
  stage.cycles.samples=32
  stage.render.filepath=str(Root/'renders'/'stage-preview.png')
if os.environ.get('POLYWORLD_BUILDINGS_SKIP_RENDER') != '1':
  bpy.ops.render.render(write_still=True)
if os.environ.get('POLYWORLD_BUILDINGS_SKIP_RENDER') != '1':
  print('RENDER_COMPLETE',stage.render.filepath,flush=True)
