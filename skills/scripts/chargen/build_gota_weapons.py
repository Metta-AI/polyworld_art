"""Build simple solid-color Gota equipment on the canonical character rig."""

import json
import math
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Matrix, Vector
from mathutils.geometry import delaunay_2d_cdt

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True
from paths import Library, Source, Preview
from clothes import material
from gota_common import bind, smooth, count, write
from register_gota import Order
import glbs

Output = Source / 'gota/weapons'
Gold = '#dca642'
Silver = '#b8c5d6'
Iron = '#3d424f'
Wood = '#704630'
Leather = '#493125'
Green = '#4e792c'
Purple = '#9b43ed'
Cyan = '#35ceef'
Red = '#a93137'
SwordPivot = [-1.13, 1.73, .025]
SwordRotation = [55.4, -22.7, 72.6]
Folders = {'Left hand': 'props/left', 'Right hand': 'props/right',
           'Back': 'clothing/backs'}


def finish(obj, color, curved=False, glow=False):
  """Assign a texture-free material and optional modest emission."""
  name = 'Equipment ' + color + (' glow' if glow else '')
  mat = material(name, color)
  if glow:
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Emission Color'].default_value = mat.diffuse_color
    shader.inputs['Emission Strength'].default_value = .22
  obj.data.materials.append(mat)
  if curved:
    smooth(obj, 55)
  return obj


def mesh(name, vertices, faces, color, curved=False, glow=False):
  """Create a small closed mesh and recalculate consistent face normals."""
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


def box(center, size, color, bevel=0):
  """Build a plain box with a small two-segment bevel."""
  bpy.ops.mesh.primitive_cube_add(size=1, location=center)
  obj = bpy.context.object
  obj.scale = size
  bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
  if bevel:
    modifier = obj.modifiers.new('Simple edge', 'BEVEL')
    modifier.width = bevel
    modifier.segments = 2
    bpy.ops.object.modifier_apply(modifier=modifier.name)
  return finish(obj, color)


def rod(start, end, radius, color, sides=12, tip=None):
  """Make a smooth low-sided cylinder or tapered cone between two points."""
  start, end = Vector(start), Vector(end)
  axis = end - start
  bpy.ops.mesh.primitive_cone_add(vertices=sides, radius1=radius,
    radius2=radius if tip is None else tip, depth=axis.length,
    location=(start + end) / 2)
  obj = bpy.context.object
  obj.rotation_euler = axis.to_track_quat('Z', 'Y').to_euler()
  return finish(obj, color, True)


def spline(points, steps=4):
  """Sample a Catmull-Rom path while retaining both end points."""
  points = [Vector(p) for p in points]
  result = []
  for i in range(len(points) - 1):
    a, b, c, d = [points[max(0, min(len(points) - 1, j))]
                   for j in [i - 1, i, i + 1, i + 2]]
    for j in range(steps):
      t = j / steps
      result.append(.5 * ((2 * b) + (-a + c) * t +
        (2 * a - 5 * b + 4 * c - d) * t*t +
        (-a + 3 * b - 3 * c + d) * t*t*t))
  return result + [points[-1]]


def bezier(points, steps=12):
  """Sample one cubic profile segment without repeating its end point."""
  a, b, c, d = [Vector(p) for p in points]
  return [tuple((1-t)**3*a + 3*(1-t)**2*t*b + 3*(1-t)*t*t*c + t**3*d)
          for t in [i / steps for i in range(steps)]]


def rounded(obj, width=.015):
  """Bevel physical edges with two rings and smoothly shade the bevel faces."""
  bpy.context.view_layer.objects.active = obj
  modifier = obj.modifiers.new('Rounded edges', 'BEVEL')
  modifier.width = width
  modifier.segments = 2
  bpy.ops.object.modifier_apply(modifier=modifier.name)
  smooth(obj, 40)
  return obj


def tube(points, radius, color, sides=10, steps=1):
  """Sweep low-sided rings along a polyline without overlapping elbows."""
  points = spline(points, steps) if steps > 1 else [Vector(p) for p in points]
  radii = radius if isinstance(radius, tuple) else (radius, radius)
  vertices, faces = [], []
  for i, point in enumerate(points):
    axis = (points[min(i + 1, len(points) - 1)] -
            points[max(0, i - 1)]).normalized()
    first = axis.cross(Vector((0, 1, 0))).normalized()
    if first.length < .1:
      first = axis.cross(Vector((1, 0, 0))).normalized()
    second = axis.cross(first).normalized()
    for j in range(sides):
      angle = math.tau * j / sides
      vertices.append(point + first * radii[0] * math.cos(angle) +
        second * radii[1] * math.sin(angle))
  for i in range(len(points) - 1):
    for j in range(sides):
      a = i * sides + j
      b = i * sides + (j + 1) % sides
      faces.append((a, b, b + sides, a + sides))
  faces += [tuple(reversed(range(sides))),
            tuple(range((len(points) - 1) * sides, len(vertices)))]
  return mesh('Swept shaft', vertices, faces, color, True)


def plate(outline, depth, color, center=(0, 0, 0)):
  """Extrude a simple planar outline with a front and a back surface."""
  x, y, z = center
  vertices = [(x + a, y + side * depth / 2, z + b)
              for side in [-1, 1] for a, b in outline]
  n = len(outline)
  faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
  faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n)
            for i in range(n)]
  return mesh('Solid plate', vertices, faces, color)


def blade(outline, color, depth=.075):
  """Give a blade a broad raised ridge and sharp perimeter on both sides."""
  n = len(outline)
  across = sum(p[0] for p in outline) / n
  height = sum(p[1] for p in outline) / n
  vertices = [(x, 0, z) for x, z in outline]
  vertices += [(across, -depth, height), (across, depth, height)]
  faces = [(i, (i + 1) % n, n + side)
           for side in range(2) for i in range(n)]
  return mesh('Blade', vertices, faces, color)


def gem(center, size, color, glow=False):
  """Create a six-point diamond with eight broad faces."""
  x, y, z = center
  w, d, h = size
  vertices = [(x, y, z + h / 2), (x + w / 2, y, z),
              (x, y, z - h / 2), (x - w / 2, y, z),
              (x, y - d / 2, z), (x, y + d / 2, z)]
  faces = [(i, (i + 1) % 4, pole) for pole in [4, 5] for i in range(4)]
  return mesh('Diamond', vertices, faces, color, glow=glow)


def orb(center, radius, color):
  """Create a rounded 80-triangle orb with intentional crystal facets."""
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=radius,
                                      location=center)
  return finish(bpy.context.object, color, False, True)


def loop(center, radius, thickness, color, turn=False):
  """Make a rounded oval link with twenty sections and a six-sided tube."""
  x, y, z = center
  vertices, faces = [], []
  for i in range(20):
    angle = math.tau * i / 20
    for j in range(6):
      cross = math.tau * j / 6
      r = radius + thickness * math.cos(cross)
      point = Vector((r * math.cos(angle), thickness * math.sin(cross),
                      r * math.sin(angle) * 1.2))
      if turn:
        point = Matrix.Rotation(math.pi / 2, 3, 'Z') @ point
      vertices.append(point + Vector((x, y, z)))
  for i in range(20):
    for j in range(6):
      faces.append((i * 6 + j, i * 6 + (j + 1) % 6,
        ((i + 1) % 20) * 6 + (j + 1) % 6, ((i + 1) % 20) * 6 + j))
  return mesh('Open link', vertices, faces, color, True)


def wrap(low, high, radius, color, turns=4):
  """Add a sparse raised helical grip wrap using solid geometry."""
  points = [(radius * math.cos(math.tau * turns * i / 32),
             radius * math.sin(math.tau * turns * i / 32),
             low + (high - low) * i / 32) for i in range(33)]
  return tube(points, .006, color, 4)


def crystal(center, size, color, glow=True):
  """Build a pointed hexagonal crystal with long bevel-like facets."""
  x, y, z = center
  w, d, h = size
  vertices = [(x + w/2*math.cos(math.tau*i/6),
               y + d/2*math.sin(math.tau*i/6), z + level*h)
              for level in [-.19, .12] for i in range(6)]
  vertices += [(x, y, z-h/2), (x, y, z+h/2)]
  faces = [(i, (i+1)%6, (i+1)%6+6, i+6) for i in range(6)]
  faces += [(i, (i+1)%6, 12) for i in range(6)]
  faces += [(i+6, (i+1)%6+6, 13) for i in range(6)]
  return mesh('Faceted crystal', vertices, faces, color, glow=glow)


def edged(outline, core, ridge, edge=Silver, depth=.06, inset=.88):
  """Build a curved bevel around broad sloping panels and a shallow ridge."""
  center = sum((Vector(p) for p in outline), Vector((0, 0))) / len(outline)
  inner = [center + (Vector(p)-center)*inset for p in outline]
  n = len(outline)
  vertices = [(x, 0, z) for x, z in outline]
  vertices += [(x, side*depth, z) for side in [-1, 1] for x, z in inner]
  faces = [(i, (i+1)%n, (i+1)%n+n*(side+1), i+n*(side+1))
           for side in range(2) for i in range(n)]
  rimCount = len(faces)
  points = inner + [Vector(p) for p in ridge]
  coords, _, triangles, origins, _, _ = delaunay_2d_cdt(points,
    [(n+i, n+i+1) for i in range(len(ridge)-1)], [list(range(n))], 1, .000001)
  for side, direction in enumerate([-1, 1]):
    indices = []
    for point, original in zip(coords, origins):
      if original and original[0] < n:
        indices.append(n*(side+1)+original[0])
      else:
        indices.append(len(vertices))
        vertices.append((point.x, direction*depth*1.6, point.y))
    faces += [tuple(indices[i] for i in face) for face in triangles]
  obj = mesh('Ridged curved blade', vertices, faces, edge)
  obj.data.materials.append(material('Blade core '+core, core))
  for face in obj.data.polygons[rimCount:]:
    face.material_index = 1
  return obj


def swordBlade(color):
  """Run a broad ridge the full blade length instead of converging at one fan."""
  vertices = []
  for z, width in [(.19, .085), (.30, .095), (1.02, .10)]:
    for x, y in [(-1, 0), (-.7, -.032), (0, -.06), (.7, -.032),
                  (1, 0), (.7, .032), (0, .06), (-.7, .032)]:
      vertices.append((x*width, y, z))
  vertices.append((0, 0, 1.25))
  faces = [(r*8+i, r*8+(i+1)%8, (r+1)*8+(i+1)%8, (r+1)*8+i)
           for r in range(2) for i in range(8)]
  faces += [(16+i, 16+(i+1)%8, 24) for i in range(8)]
  faces += [tuple(reversed(range(8)))]
  return mesh('Longitudinal blade ridge', vertices, faces, color)


def sword(dark=False):
  """Build a short broad sword with simple guard, grip and diamond accents."""
  steel, trim, accent = (Iron, Silver, Cyan) if dark else (Silver, Gold, '#3179d9')
  guard = ([(-.29, .31), (-.27, .21), (-.18, .15), (-.10, .15), (0, .25),
    (.10, .15), (.18, .15), (.27, .21), (.29, .31), (.29, .12),
    (.18, .075), (.07, .095), (0, .13), (-.07, .095), (-.18, .075), (-.29, .12)]
    if dark else [(-.26, .13), (-.26, .23), (-.18, .255), (-.12, .20),
    (0, .255), (.12, .20), (.18, .255), (.26, .23), (.26, .13), (0, .105)])
  objects = [swordBlade(steel),
    rod((0, 0, -.23), (0, 0, .15), .049, Leather, 16),
    rounded(plate(guard, .11, trim), .018),
    crystal((0, 0, -.28), (.18, .16, .22), trim, False),
    wrap(-.20, .085, .052, '#77503c' if not dark else '#252936')]
  for side in [-1, 1]:
    objects.append(gem((0, side * .072, .18), (.13, .055, .18), accent, dark))
    if dark:
      channel = [(-.016, .95), (.016, .95), (.016, .30), (.052, .245),
        (.031, .23), (0, .27), (-.031, .23), (-.052, .245), (-.016, .30)]
      objects.append(plate(channel, .013, Cyan, (0, side*.063, 0)))
  return objects


def shield(dark=False):
  """Build curved kite sides, a bowed face and a rolled metal rim."""
  trim, face, accent = (Silver, Iron, Cyan) if dark else (Gold, '#245bc7', Gold)
  outline = [(0, .49), (.33, .28)]
  outline += bezier([(.33, .28), (.34, -.03), (.25, -.27), (0, -.56)], 12)[1:]
  outline += [(0, -.56)]
  outline += bezier([(0, -.56), (-.25, -.27), (-.34, -.03), (-.33, .28)], 12)[1:]
  outline += [(-.33, .28)]
  n = len(outline)
  rings = [(1, .032), (1.02, .002), (.985, -.037), (.865, -.062),
           (.85, -.047), (.55, -.092), (.25, -.115)]
  vertices = [(x*scale, y-.028*(1-(x/.34)**2), z*scale)
              for scale, y in rings for x, z in outline]
  vertices += [(0, -.15, 0)]
  faces = [(r*n+i, r*n+(i+1)%n, (r+1)*n+(i+1)%n, (r+1)*n+i)
           for r in range(len(rings)-1) for i in range(n)]
  faces += [((len(rings)-1)*n+i, (len(rings)-1)*n+(i+1)%n, len(vertices)-1)
            for i in range(n)]
  front = mesh('Bowed shield and rolled rim', vertices, faces, trim, True)
  front.data.materials.append(material('Shield face '+face, face))
  for polygon in front.data.polygons:
    if polygon.index >= n*3:
      polygon.material_index = 1
  inner = [(x*.875, z*.875) for x, z in outline]
  objects = [front, rounded(plate(inner, .045,
    '#292d38' if dark else Wood, (0, .027, 0)), .010),
    gem((0, -.165, .015), (.20, .065, .43), accent, dark)]
  for z in [-.12, .15]:
    objects.append(tube([(-.16, .053, z), (-.16, .13, z),
      (-.10, .15, z), (.10, .15, z), (.16, .13, z), (.16, .053, z)],
      (.028, .012), Leather, 6, steps=3))
    for x in [-.16, .16]:
      objects.append(box((x, .056, z), (.065, .035, .078), trim, .008))
  return objects


def arrow(length=.76, bolt=False):
  """Create a reusable arrow or short bolt with a solid head and two vanes."""
  objects = [rod((0, 0, -.16), (0, 0, length - .14), .014, Wood, 6),
    gem((0, 0, length - .08), (.075, .055, .17), Silver)]
  for turn in [0, math.pi / 2]:
    vane = plate([(-.045, -.14), (-.045, -.02), (0, .05),
                  (.045, -.02), (.045, -.14), (0, -.10)],
                 .01, '#d9cbaa' if bolt else Green)
    vane.rotation_euler.z = turn
    objects.append(vane)
  return objects


def bow():
  """Build a restrained recurve bow with a separate taut string."""
  points = [(.10, 0, -.86), (.17, 0, -.77), (.165, 0, -.59),
    (.035, 0, -.27), (0, 0, 0), (.035, 0, .27), (.165, 0, .59),
    (.17, 0, .77), (.10, 0, .86)]
  path = spline(points, 4)
  shaft = tube(path, (.041, .030), Wood, 12)
  for i, vertex in enumerate(shaft.data.vertices):
    ring = i // 12
    point = path[ring]
    taper = .55 + .45*(1-abs(point.z)/.86)
    vertex.co = point + (vertex.co-point)*taper
  objects = [shaft,
    rod((.10, -.001, -.86), (.10, -.001, .86), .006, '#deca9a', 6),
    rounded(rod((0, 0, -.11), (0, 0, .11), .050, Green, 16), .009)]
  for sign in [-1, 1]:
    objects.append(rounded(rod((.178, 0, sign*.68), (.184, 0, sign*.74),
                       .034, Green, 12), .005))
  return objects


def quiver(heavy=False):
  """Build a hollow quiver with visible ammunition and a rear carry strap."""
  objects = []
  if heavy:
    # Four walls and a recessed base keep the rectangular box visibly open.
    for x in [-.12, .12]:
      objects.append(box((x, 0, 0), (.035, .20, .61), Wood, .006))
    for y in [-.09, .09]:
      objects.append(box((0, y, 0), (.24, .028, .61), Wood, .005))
    objects.append(box((0, 0, -.29), (.24, .20, .03), Leather))
    for z in [-.25, .25]:
      for x in [-.132, .132]:
        objects.append(box((x, 0, z), (.025, .23, .095), Iron, .008))
      for y in [-.11, .11]:
        objects.append(box((0, y, z), (.28, .025, .095), Iron, .008))
    for y in [-.132, .132]:
      for z in [-.25, .25]:
        objects.append(rod((0, y, z), (0, y*1.055, z), .027, Silver, 10))
  else:
    n = 20
    vertices = [(radius * math.cos(math.tau * i / n),
                 radius * math.sin(math.tau * i / n), z)
                for radius, z in [(.065, -.36), (.095, -.32), (.122, .20),
                  (.132, .35), (.109, .35), (.102, .22), (.068, -.30)]
                for i in range(n)]
    faces = [(ring * n + i, ring * n + (i + 1) % n,
              (ring + 1) * n + (i + 1) % n, (ring + 1) * n + i)
             for ring in range(6) for i in range(n)]
    faces += [tuple(reversed(range(n))), tuple(range(6 * n, 7 * n))]
    objects.append(mesh('Hollow quiver', vertices, faces, Wood, True))
    cuff = []
    for radius, z in [(.126, .26), (.14, .27), (.14, .35), (.126, .36)]:
      cuff += [(radius*math.cos(math.tau*i/n), radius*math.sin(math.tau*i/n), z)
               for i in range(n)]
    objects.append(mesh('Broad green quiver cuff', cuff,
      [(r*n+i, r*n+(i+1)%n, (r+1)*n+(i+1)%n, (r+1)*n+i)
       for r in range(3) for i in range(n)], Green, True))
  for i, (x, y) in enumerate([(-.055, -.035), (.045, -.035), (0, .035)]):
    shot = arrow(.47 if heavy else .74, heavy)
    if not heavy:
      for vane in shot[2:]:
        vane.data.materials[0] = material('Ivory quiver feathers', '#e7dbc2')
    transform(shot, (x, y, (.04 if heavy else .42) + .025 * i),
              rotation=0 if heavy else math.pi)
    objects += shot
  objects.append(tube([(-.06, .12, -.26), (-.075, .22, -.12),
    (.075, .22, .15), (.06, .12, .27)], (.035, .009), Leather, 8, steps=4))
  return objects


def staff(kind):
  """Build three restrained crystal staffs and a leafy wooden staff."""
  if kind == 'druid':
    objects = [tube([(0, 0, -1.55), (-.035, 0, -.95), (.035, 0, -.43),
      (-.025, .01, .12), (.02, 0, .55), (-.06, 0, .91), (.035, 0, 1.15)],
      .065, Wood, 12, steps=4)]
    for end in [(-.23, 0, 1.22), (.25, 0, 1.19)]:
      objects.append(tube([(-.01, 0, .68), (end[0]*.3, 0, .92),
        (end[0]*.8, 0, 1.06), end], .047, Wood, 10, steps=4))
      objects.append(leaf(end, (.26, .36), Green))
    objects.append(leaf((.045, -.01, 1.31), (.25, .38), '#76a63c'))
    vine = [(.078 * math.cos(i * math.tau / 14),
             .078 * math.sin(i * math.tau / 14), -1.02 + i * .055)
            for i in range(33)]
    objects.append(tube(vine, (.039, .008), Green, 6))
    return objects
  color, trim, shaft = {
    'arcanist': (Purple, Gold, '#50326d'),
    'lich': (Cyan, Silver, '#284b98'),
    'warlock': (Purple, Gold, '#46312f')}[kind]
  if kind == 'warlock':
    wood = tube([(0, 0, -1.55), (.025, .015, -.92), (-.025, -.01, -.4),
      (0, 0, 0), (.03, .005, .35), (-.04, 0, .69), (0, 0, .84)],
      .052, shaft, 10, steps=3)
  else:
    wood = rod((0, 0, -1.55), (0, 0, .81), .050, shaft, 16)
  objects = [wood,
    rounded(rod((0, 0, .71), (0, 0, .82), .128, trim, 12), .014),
    crystal((0, 0, -1.59), (.27, .25, .31), trim, False)]
  for sign in [-1, 1]:
    outline = bezier([(.015, .79), (.12, .79), (.23, .95), (.205, 1.22)], 8)
    outline += bezier([(.205, 1.22), (.15, 1.08), (.16, .98), (.035, .87)], 8)
    objects.append(rounded(plate([(sign*x*1.36, .79+(z-.79)*1.16) for x,z in outline], .085, trim), .008))
  if kind == 'arcanist':
    objects.append(orb((0, 0, 1.19), .255, color))
  else:
    objects.append(crystal((0, 0, 1.19), (.39, .33, .72), color))
  if kind == 'lich':
    objects.append(crystal((0, -.065, -1.60), (.16, .10, .23), Cyan))
  if kind == 'warlock':
    objects.append(rod((0, 0, -.20), (0, 0, .20), .061, Red, 12))
    objects.append(wrap(-.18, .18, .063, '#6f2436'))
    for z in [-.23, .23]:
      objects.append(rounded(rod((0, 0, z-.028), (0, 0, z+.028), .075, Gold), .008))
  return objects


def leaf(center, size, color):
  """Build a broad pointed leaf with a curved profile and a raised midrib."""
  w, h = size
  outline = bezier([(0, -h/2), (-w*.55, -h*.20), (-w*.55, h*.13), (0, h/2)], 6)
  outline += bezier([(0, h/2), (w*.55, h*.13), (w*.55, -h*.20), (0, -h/2)], 6)
  obj = blade(outline, color, .035)
  obj.data.transform(Matrix.Translation(Vector(center)))
  smooth(obj, 35)
  return obj


def magic(kind):
  """Keep floating orbs close to the palm with restrained luminous color."""
  if kind == 'arcanist':
    return [orb((0, 0, .43), .18, Purple),
            orb((-.15, -.01, .16), .085, Purple),
            orb((.15, -.01, .16), .085, Purple)]
  if kind == 'lich':
    return [orb((0, 0, .27), .18, Cyan)]
  objects = [orb((0, 0, .39), .22, '#81df39')]
  for angle in [math.pi/3, -math.pi/3, math.pi]:
    vertices, faces = [], []
    for r in range(9):
      t = r/8
      width = .85*math.sin(math.pi*t)
      radius = .33*math.sin(t*math.pi*.62)
      for c in range(5):
        phi = (c/2-1)*width
        vertices.append((radius*math.sin(phi), -radius*math.cos(phi), .035+.38*t))
    for r in range(8):
      for c in range(4):
        faces.append((r*5+c, r*5+c+1, (r+1)*5+c+1, (r+1)*5+c))
    petal = mesh('Rounded cupped orb leaf', vertices, faces, Green, True)
    bpy.context.view_layer.objects.active = petal
    solid = petal.modifiers.new('Leaf thickness', 'SOLIDIFY')
    solid.thickness = .026
    bpy.ops.object.modifier_apply(modifier=solid.name)
    petal.data.transform(Matrix.Rotation(angle, 4, 'Z'))
    objects.append(petal)
  objects.append(rod((0, 0, .015), (0, 0, .10), .032, Green, 10))
  return objects


def dagger():
  """Create a flowing hooked blade with a narrow steel bevel and red face."""
  outline = bezier([(-.055, .12), (-.08, .21), (-.11, .24), (-.20, .29)], 8)
  outline += bezier([(-.20, .29), (-.18, .59), (-.005, .86), (.23, 1.02)], 20)
  outline += bezier([(.23, 1.02), (.13, .79), (.09, .57), (.18, .42)], 14)
  outline += bezier([(.18, .42), (.05, .36), (.045, .25), (.065, .12)], 10)
  guard = [(-.20, .055), (-.22, .14), (-.12, .20), (0, .22),
    (.14, .19), (.22, .12), (.20, .055), (.09, .10), (-.09, .10)]
  objects = [edged(outline, Red, [(-.025, .26), (-.035, .49), (.055, .78)],
                 Silver, .045, .84),
    rod((0, 0, -.24), (0, 0, .15), .048, Leather, 12),
    rounded(plate(guard, .115, Iron), .019),
    crystal((0, 0, -.29), (.18, .16, .20), Iron, False),
    wrap(-.22, .09, .052, '#82513c'),
    rod((0, 0, -.21), (0, 0, -.16), .054, Red, 12)]
  for side in [-1, 1]:
    objects.append(gem((0, side*.068, .157), (.10, .05, .13), Red))
  return objects


def axe():
  """Shape a continuous cutting arc and concave neck around a beveled socket."""
  outline = bezier([(-.015, .57), (-.18, .58), (-.29, .61), (-.38, .78)], 12)
  outline += bezier([(-.38, .78), (-.65, .58), (-.66, .22), (-.39, .015)], 24)
  outline += bezier([(-.39, .015), (-.32, .23), (-.22, .35), (-.015, .35)], 16)
  objects = [rod((0, 0, -.42), (0, 0, .69), .046, Wood, 12),
    rod((0, 0, -.27), (0, 0, .08), .057, Red, 12),
    wrap(-.26, .065, .060, '#652527'),
    crystal((0, 0, -.47), (.18, .17, .22), Iron, False),
    rounded(box((0, 0, .46), (.19, .19, .25), Iron), .023),
    edged(outline, '#62636e', [(-.34, .28), (-.39, .50), (-.32, .60)],
          Silver, .063, .83)]
  transform(objects, rotation=.13)
  return objects


def crossbow():
  """Build curved medieval limbs with the string confined to the upper side."""
  stock = [(-.065, .57), (.065, .57), (.069, -.13), (.06, -.50),
           (.03, -.56), (-.03, -.56), (-.06, -.50), (-.069, -.13)]
  objects = [rounded(plate(stock, .16, Wood), .015),
    box((0, -.085, .31), (.030, .018, .47), Iron, .005),
    box((0, -.088, -.025), (.105, .046, .075), Iron, .010),
    box((0, 0, .558), (.12, .18, .046), Iron, .010)]
  for sign in [-1, 1]:
    path = spline([(0, 0, .50), (sign*.17, 0, .46),
      (sign*.32, 0, .35), (sign*.42, 0, .21)], 7)
    # Four broad faces keep the limbs rectangular instead of cylindrical.
    vertices = []
    for i, point in enumerate(path):
      axis = (path[min(i+1, len(path)-1)]-path[max(i-1, 0)]).normalized()
      across = Vector((-axis.z, 0, axis.x))
      width = .043 - .017*i/(len(path)-1)
      for a, y in [(-1, -.033), (1, -.033), (1, .033), (-1, .033)]:
        vertices.append(point + across*width*a + Vector((0, y, 0)))
    faces = [(r*4+i, r*4+(i+1)%4, (r+1)*4+(i+1)%4, (r+1)*4+i)
      for r in range(len(path)-1) for i in range(4)]
    faces += [(3, 2, 1, 0), tuple(range(len(vertices)-4, len(vertices)))]
    objects.append(rounded(mesh('Curved steel crossbow limb', vertices, faces, Iron), .006))
    cap = box((sign*.42, 0, .21), (.075, .092, .075), Silver, .009)
    cap.rotation_euler.y = sign*.30
    objects.append(cap)
    start, end = Vector((sign*.42, -.087, .21)), Vector((0, -.111, -.025))
    across = (end-start).cross(Vector((0, -1, 0))).normalized()*.007
    string = mesh('Top bowstring', [start+across, end+across,
      end-across, start-across], [(0, 1, 2, 3)], '#e3c79e')
    string.data.materials[0] = string.data.materials[0].copy()
    string.data.materials[0].use_backface_culling = True
    objects.append(string)
  objects.append(tube([(0, .085, -.065), (0, .17, -.12),
    (0, .17, -.25), (0, .085, -.28)], (.024, .032), Iron, 8, steps=4))
  return objects


def censer():
  """Suspend a full curved cage from oval links with stepped caps and finial."""
  objects = [loop((0, 0, .045-i*.123), .062, .014, Iron,
                  turn=(i % 2 == 1)) for i in range(3)]
  for low, high, radius, tip in [(-.34, -.30, .155, .095),
    (-.39, -.34, .19, .155), (-.405, -.39, .195, .195),
    (-.81, -.775, .14, .195), (-.775, -.76, .195, .195)]:
    objects.append(rounded(rod((0, 0, low), (0, 0, high), radius, Iron,
                               12, tip=tip), .005))
  objects += [crystal((0, 0, -.585), (.30, .30, .37), Purple),
    crystal((0, 0, -.84), (.20, .20, .14), Iron, False)]
  for i in range(6):
    angle = math.tau*i/6 + math.pi/6
    objects.append(tube([(r*math.cos(angle), r*math.sin(angle), z)
      for r, z in [(.16, -.39), (.21, -.47), (.235, -.57),
                    (.21, -.68), (.16, -.77)]], .024, Iron, 8, steps=4))
  objects.append(rod((0, 0, -.30), (0, 0, -.23), .025, Iron, 10))
  transform(objects)
  for obj in objects:
    obj.data.transform(Matrix.Scale(1.28, 4))
  return objects


def transform(objects, offset=(0, 0, 0), rotation=0, mirror=False):
  """Apply a local item placement directly to vertices before skin binding."""
  bpy.context.view_layer.update()
  matrix = Matrix.Translation(Vector(offset)) @ Matrix.Rotation(rotation, 4, 'Y')
  if mirror:
    matrix = matrix @ Matrix.Diagonal(Vector((-1, 1, 1, 1)))
  for obj in objects:
    obj.data.transform(matrix @ obj.matrix_world)
    obj.matrix_world.identity()
    edit = bmesh.new()
    edit.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(edit, faces=list(edit.faces))
    if obj.name.startswith('Top bowstring'):
      for face in edit.faces:
        if face.normal.y > 0:
          face.normal_flip()
    edit.to_mesh(obj.data)
    edit.free()


def assemble(rig, slug, category, label, objects, bone, offset,
             rotation=0, mirror=False):
  """Join a selectable item and rigidly skin every vertex to its socket bone."""
  transform(objects, offset, rotation, mirror)
  bpy.ops.object.select_all(action='DESELECT')
  for obj in objects:
    obj.select_set(True)
  bpy.context.view_layer.objects.active = objects[0]
  bpy.ops.object.join()
  obj = bpy.context.object
  suffix = category.lower().replace(' ', '_')
  obj.name = 'GotaWeapon_' + slug + '_' + suffix
  group = obj.vertex_groups.new(name=bone)
  group.add(list(range(len(obj.data.vertices))), 1, 'REPLACE')
  ctx = type('Binding', (), {'rig': rig})()
  bind(ctx, obj)
  obj['socketBone'] = bone
  obj['triangleLimitExclusive'] = 5000
  identity = Folders[category] + '/gota_' + slug + '_' + suffix
  return dict(category=category, name=label, id=identity, object=obj,
              bone=bone, offset=offset)


def main():
  """Export all ten sets, retain editable Blender source and register presets."""
  Output.mkdir(parents=True, exist_ok=True)
  preview = Preview / 'gota/weapons'
  preview.mkdir(parents=True, exist_ok=True)
  bpy.ops.wm.open_mainfile(filepath=str(Source / 'character.blend'))
  rig = bpy.data.objects['CharacterRig']
  rig.animation_data.action = None
  rig.data.pose_position = 'REST'
  for bone in rig.pose.bones:
    bone.matrix_basis.identity()
  # Keep only the canonical rig in this separate equipment authoring file.
  for obj in list(bpy.data.objects):
    if obj != rig:
      bpy.data.objects.remove(obj, do_unlink=True)
  entries = []
  for slug in Order:
    def add(category, label, objects, bone=None, offset=None, **kwargs):
      """Place a finished set component into its matching character slot."""
      if bone is None:
        bone = 'LeftHand' if category == 'Left hand' else 'RightHand'
      if offset is None:
        offset = (1.13 if category == 'Left hand' else -1.13, -.025, 1.73)
      entry = assemble(rig, slug, category, label, objects, bone, offset, **kwargs)
      entry['slug'] = slug
      entries.append(entry)
    if slug in ['vanguard_knight', 'death_knight']:
      dark = slug == 'death_knight'
      title = 'Death Knight' if dark else 'Vanguard'
      add('Right hand', title + ' sword', sword(dark))
      add('Left hand', title + ' shield', shield(dark),
          bone='LeftForeArm', offset=(1.04, -.15, 1.60))
    elif slug == 'ranger':
      add('Left hand', 'Ranger bow', bow())
      add('Right hand', 'Ranger arrow', arrow())
      add('Back', 'Ranger light quiver', quiver(), bone='Spine2',
          offset=(-.39, .54, 1.55), rotation=-.35)
    elif slug in ['arcanist', 'druid_warden', 'lich']:
      kind = 'druid' if slug == 'druid_warden' else slug
      title = {'arcanist': 'Arcanist', 'druid': 'Druid', 'lich': 'Lich'}[kind]
      add('Right hand', title + ' staff', staff(kind))
      add('Left hand', title + (' orbs' if kind == 'arcanist' else ' orb'), magic(kind))
    elif slug in ['demon_hunter', 'berserker']:
      title = 'Demon Hunter dagger' if slug == 'demon_hunter' else 'Berserker axe'
      builder = dagger if slug == 'demon_hunter' else axe
      for side in ['Right hand', 'Left hand']:
        add(side, title, builder(), mirror=side == 'Left hand')
    elif slug == 'crossbowman':
      add('Right hand', 'Medieval crossbow', crossbow())
      add('Back', 'Heavy bolt quiver', quiver(True), bone='Spine2',
          offset=(.36, .51, 1.55), rotation=.23)
    elif slug == 'warlock':
      add('Right hand', 'Warlock staff', staff('warlock'))
      add('Left hand', 'Warlock censer', censer())
  bpy.ops.object.select_all(action='DESELECT')
  for obj in [rig] + [entry['object'] for entry in entries]:
    obj.hide_set(False)
    obj.select_set(True)
  bpy.context.view_layer.objects.active = rig
  assembled = preview / 'equipment.glb'
  bpy.ops.export_scene.gltf(filepath=str(assembled), export_format='GLB',
    use_selection=True, export_animations=False, export_skins=True,
    export_materials='EXPORT', export_yup=True)
  document, binary = glbs.read(assembled)
  metadata = []
  for entry in entries:
    obj = entry['object']
    doc, blob = glbs.subset(document, binary, meshes=[obj.name])
    triangles, _ = count(doc)
    assert 0 < triangles < 5000, (entry['name'], triangles)
    identity = entry['id']
    path = Library / (identity + '.glb')
    path.parent.mkdir(parents=True, exist_ok=True)
    glbs.write(path, doc, blob)
    data = dict(id=identity, name=entry['name'], files=[identity + '.glb'],
      nodes=[obj.name], alignment='good' if entry['slug'] in Order[:5] else 'evil',
      hides=[], skinNodes=[], hairShades=[], hatShades=[], clothShades=[],
      attachmentBone=entry['bone'], triangles=triangles,
      triangleLimitExclusive=5000, singleFile=True)
    if entry['name'] in ['Vanguard sword', 'Death Knight sword']:
      # Runtime grip offsets use degrees and the exported Y-up bind space.
      data['attachmentPivot'] = SwordPivot
      data['attachmentRotation'] = SwordRotation
    write(Library / (identity + '.json'), data)
    metadata.append(dict(category=entry['category'], slug=entry['slug'], **data))
  for slug in Order:
    total = sum(entry['triangles'] for entry in metadata if entry['slug'] == slug)
    assert total < 5000, (slug, total)
    print('EQUIPMENT', slug, total, 'triangles', flush=True)
  write(Output / 'parts.json', metadata)
  bpy.context.preferences.filepaths.save_version = 0
  # Each hero's objects get a named collection for convenient editing.
  for slug in Order:
    collection = bpy.data.collections.new(slug)
    bpy.context.scene.collection.children.link(collection)
    for entry in entries:
      if entry['slug'] == slug:
        obj = entry['object']
        for old in list(obj.users_collection):
          old.objects.unlink(obj)
        collection.objects.link(obj)
  bpy.ops.wm.save_as_mainfile(filepath=str(Output / 'equipment.blend'))
  from register_gota import main as register
  register()
  print('Gota equipment exported and registered.', flush=True)


main()
