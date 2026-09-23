"""Build Hades' two-pronged staff and emerald soul on the shared hand sockets."""

import math

import bpy
import bmesh
from mathutils import Matrix, Vector

from clothes import material
from gota_common import bind, part, smooth

Black = '#242a32'
Edge = '#3a424b'
Grip = '#171c24'
Gold = '#c99440'
LightGold = '#e2b858'
Emerald = '#13b865'
BrightEmerald = '#34e08e'


def finish(obj, color, curved=False, glow=False):
  """Assign a solid material with optional restrained crystal emission."""
  mat = material('Hades equipment '+color, color)
  if glow:
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Emission Color'].default_value = mat.diffuse_color
    shader.inputs['Emission Strength'].default_value = .22
  obj.data.materials.append(mat)
  if curved:
    smooth(obj, 55)
  return obj


def shape(name, vertices, faces, color, curved=False, glow=False):
  """Create one closed colored component with consistently outward normals."""
  data = bpy.data.meshes.new(name)
  data.from_pydata(vertices, [], faces)
  data.update()
  edit = bmesh.new()
  edit.from_mesh(data)
  bmesh.ops.recalc_face_normals(edit, faces=list(edit.faces))
  edit.to_mesh(data)
  edit.free()
  obj = bpy.data.objects.new(name, data)
  bpy.context.collection.objects.link(obj)
  return finish(obj, color, curved, glow)


def rod(start, end, radius, color, sides=16):
  """Use smooth cylindrical rings for small shafts, wraps, and collars."""
  start, end = Vector(start), Vector(end)
  axis = end-start
  bpy.ops.mesh.primitive_cone_add(vertices=sides, radius1=radius,
    radius2=radius, depth=axis.length, location=(start+end)/2)
  obj = bpy.context.object
  obj.rotation_euler = axis.to_track_quat('Z', 'Y').to_euler()
  return finish(obj, color, curved=True)


def crystal(center, size, color, glow=True):
  """Build a pointed hexagonal crystal with long broad facets."""
  x, y, z = center
  w, d, h = size
  vertices = [(x+w/2*math.cos(math.tau*i/6),
               y+d/2*math.sin(math.tau*i/6), z+level*h)
              for level in [-.19, .12] for i in range(6)]
  vertices.extend([(x, y, z-h/2), (x, y, z+h/2)])
  faces = [(i, (i+1)%6, (i+1)%6+6, i+6) for i in range(6)]
  faces.extend([(i, (i+1)%6, 12) for i in range(6)])
  faces.extend([(i+6, (i+1)%6+6, 13) for i in range(6)])
  return shape('Hades faceted crystal', vertices, faces, color, glow=glow)


def gem(center, size, color, glow=False):
  """Make a clean diamond setting with the same facets on front and back."""
  x, y, z = center
  w, d, h = size
  vertices = [(x, y, z+h/2), (x+w/2, y, z),
              (x, y, z-h/2), (x-w/2, y, z),
              (x, y-d/2, z), (x, y+d/2, z)]
  faces = [(i, (i+1)%4, pole) for pole in [4, 5] for i in range(4)]
  return shape('Hades diamond', vertices, faces, color, glow=glow)


def blade(outline, color, depth):
  """Add a broad central ridge on each side of a pointed metal silhouette."""
  across = sum(point[0] for point in outline)/len(outline)
  height = sum(point[1] for point in outline)/len(outline)
  vertices = [(x, 0, z) for x, z in outline]
  vertices.extend([(across, -depth, height), (across, depth, height)])
  faces = [(i, (i+1)%len(outline), len(outline)+side)
           for side in range(2) for i in range(len(outline))]
  return shape('Hades fork metal', vertices, faces, color)


def spline(points, steps):
  """Sample a smooth Catmull-Rom path that retains both end points."""
  points = [Vector(point) for point in points]
  result = []
  for i in range(len(points)-1):
    a, b, c, d = [points[max(0, min(len(points)-1, j))]
                 for j in [i-1, i, i+1, i+2]]
    for j in range(steps):
      t = j/steps
      result.append(.5*((2*b)+(-a+c)*t+
        (2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
  return result+[points[-1]]


def transform(objects, offset):
  """Bake object placement directly into the shared rig bind coordinates."""
  bpy.context.view_layer.update()
  matrix = Matrix.Translation(Vector(offset))
  for obj in objects:
    obj.data.transform(matrix@obj.matrix_world)
    obj.matrix_world.identity()


def bident():
  """Build two broad spear prongs around an emerald and gold diamond fork."""
  objects = [
    rod((0, 0, -1.20), (0, 0, .69), .047, Black, 24),
    rod((0, 0, -.17), (0, 0, .18), .052, Grip, 24),
    crystal((0, 0, -1.35), (.19, .16, .37), Black, False),
    crystal((0, 0, -1.14), (.16, .15, .18), Gold, False),
    crystal((0, 0, -1.14), (.080, .172, .105), Emerald),
  ]
  for z, radius, height in [(-.42, .060, .046), (.23, .066, .050),
                             (.57, .067, .059), (-1.12, .055, .047)]:
    objects.append(rod((0, 0, z-height/2),
      (0, 0, z+height/2), radius, Gold, 20))
    if z in [-.42, .23, -1.12]:
      for y in [-radius, radius]:
        objects.append(gem((0, y, z), (.115, .048, .165), Gold))
        objects.append(gem((0, y*1.35, z), (.052, .028, .09),
          Emerald, True))
  for z in [-.115, -.045, .025, .095]:
    objects.append(rod((0, 0, z-.008), (0, 0, z+.008),
      .054, Edge, 20))

  # Separate fork roots leave a legible open V between the emerald tips.
  for side in [-1, 1]:
    outline = [(.025, .55), (.30, .80), (.35, 1.06), (.28, 1.36),
               (.215, 1.51), (.17, 1.29), (.135, .95), (.005, .75)]
    prong = blade([(side*x, z) for x, z in outline], Black, .072)
    objects.append(prong)
    ridge = blade([(side*x, z) for x, z in
      [(.15, .98), (.25, 1.19), (.215, 1.51), (.18, 1.36)]], Edge, .080)
    objects.append(ridge)
    objects.append(crystal((side*.217, 0, 1.51),
      (.155, .165, .46), Emerald))
    objects.append(gem((side*.217, -.085, 1.46),
      (.076, .035, .16), BrightEmerald, True))
    objects.append(gem((side*.217, .085, 1.46),
      (.076, .035, .16), BrightEmerald, True))

    # A swept gold shoulder joins each prong to the central setting.
    goldOutline = [(side*x, z) for x, z in
      [(.015, .61), (.30, .73), (.29, .86), (.205, .99),
       (.19, .84), (.10, .80), (.09, .66)]]
    objects.append(blade(goldOutline, Gold, .088))

  objects.append(gem((0, 0, .70), (.39, .24, .51), Gold))
  for y in [-.135, .135]:
    objects.append(gem((0, y, .71), (.245, .07, .345),
      Emerald, True))
    objects.append(gem((0, y*1.2, .735), (.070, .025, .16),
      BrightEmerald, True))
  objects.append(crystal((0, 0, .49), (.11, .14, .13),
    LightGold, False))
  return objects


def soul():
  """Keep the luminous green soul and floating shards just above the palm."""
  objects = [crystal((0, 0, .34), (.25, .23, .40), Emerald)]
  for center, size in [((-.18, .02, .47), (.065, .061, .17)),
                        ((.18, .035, .35), (.051, .051, .14)),
                        ((.055, .075, .66), (.075, .070, .19)),
                        ((-.13, -.04, .19), (.044, .048, .095)),
                        ((.10, -.05, .12), (.045, .045, .085))]:
    objects.append(crystal(center, size, BrightEmerald))
  # Curved solid wisps suggest a small contained soul flame without billboards.
  for sign in [-1, 1]:
    points = [(sign*.065, .085, .25), (sign*.145, .11, .37),
              (sign*.09, .12, .50), (sign*.12, .12, .59),
              (sign*.075, .12, .73)]
    sampled = spline(points, 3)
    vertices, faces = [], []
    sides = 6
    for i, point in enumerate(sampled):
      tangent = (sampled[min(i+1, len(sampled)-1)]-
                 sampled[max(i-1, 0)]).normalized()
      first = tangent.cross(Vector((0, 1, 0))).normalized()
      second = tangent.cross(first).normalized()
      radius = .022*(1-i/(len(sampled)-1))+.002
      for j in range(sides):
        angle = math.tau*j/sides
        vertices.append(point+radius*(first*math.cos(angle)+
                                       second*math.sin(angle)))
      if i:
        for j in range(sides):
          a = (i-1)*sides+j
          b = (i-1)*sides+(j+1)%sides
          faces.append((a, b, b+sides, a+sides))
    faces.extend([tuple(reversed(range(sides))),
      tuple(range((len(sampled)-1)*sides, len(vertices)))])
    objects.append(shape('Soul wisp', vertices, faces,
      Emerald, curved=True, glow=True))
  return objects


def assemble(ctx, suffix, objects, bone, offset):
  """Bake all local transforms and bind a single selectable mesh to a hand."""
  transform(objects, offset)
  for i, obj in enumerate(objects):
    obj.name = ctx.prefix+suffix+str(i)
    if ctx.collection not in obj.users_collection:
      ctx.collection.objects.link(obj)
    for collection in list(obj.users_collection):
      if collection != ctx.collection:
        collection.objects.unlink(obj)
  bpy.ops.object.select_all(action='DESELECT')
  for obj in objects:
    obj.select_set(True)
  bpy.context.view_layer.objects.active = objects[0]
  bpy.ops.object.join()
  obj = bpy.context.object
  obj.name = ctx.prefix+suffix
  group = obj.vertex_groups.new(name=bone)
  group.add(list(range(len(obj.data.vertices))), 1, 'REPLACE')
  obj['socketBone'] = bone
  obj['triangleLimitExclusive'] = 5000
  obj.data.calc_loop_triangles()
  assert len(obj.data.loop_triangles) < 5000
  return bind(ctx, obj)


def build(ctx):
  """Return independently selectable Hades equipment on existing rig bones."""
  staff = assemble(ctx, 'Bident', bident(), 'RightHand', (-1.13, -.025, 1.73))
  orb = assemble(ctx, 'Soul', soul(), 'LeftHand', (1.13, -.025, 1.73))
  return [part(ctx, 'Right hand', 'Hades bident', staff,
               attachmentBone='RightHand'),
          part(ctx, 'Left hand', 'Hades soul', orb,
               attachmentBone='LeftHand')]
