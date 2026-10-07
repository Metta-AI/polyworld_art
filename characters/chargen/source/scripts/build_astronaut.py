"""Build a tintable modular astronaut on the current canonical Chargen rig."""

import json
import math
import sys
from pathlib import Path
from types import SimpleNamespace

import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

import glbs
from clothes import band, bodySurface, clip, material, meshObject, offset, sourceWeights
from gota_common import bind, count, mesh, privateLibrary, smooth, write
from paths import Library, Preview, Source

Output = Source / 'astronaut'
Review = Preview / 'astronaut'
Folders = {'Headgear': 'hats', 'Chest': 'clothing/torsos',
           'Leg': 'clothing/pants', 'Hand': 'clothing/gloves',
           'Foot': 'clothing/boots', 'Belt': 'clothing/belts'}


def palette():
  """Keep dye surfaces white and hardware independent of garment tint."""
  values = {'fabric': '#ffffff', 'panel': '#ffba36',
            'metal': '#bbc2cb', 'rubber': '#252832',
            'boots': '#536071', 'visor': '#111722'}
  result = {}
  for key, color in values.items():
    mat = material('Astronaut ' + key, color)
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Roughness'].default_value = .2 if key == 'visor' else .8
    result[key] = mat
  return result


def box(ctx, name, center, size, mat, bone='Spine2', bevel=.008):
  """Create a small hard surface detail with a fixed attachment bone."""
  bpy.ops.mesh.primitive_cube_add(size=1, location=center)
  obj = bpy.context.object
  obj.name = ctx.prefix + name
  obj.scale = size
  bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
  obj.data.materials.append(mat)
  if bevel:
    modifier = obj.modifiers.new('Small hard edge bevel', 'BEVEL')
    modifier.width = bevel
    modifier.segments = 1
    bpy.ops.object.modifier_apply(modifier=modifier.name)
  obj.vertex_groups.new(name=bone).add(
    list(range(len(obj.data.vertices))), 1, 'REPLACE')
  return bind(ctx, obj)


def ring(ctx, name, center, radius, height, mat, bone, axis='Z', sample=None):
  """Build a sealed annular cuff with smooth sides and sharp flat rims."""
  vertices, faces = [], []
  for along, width in [(-height / 2, radius), (height / 2, radius),
                       (height / 2, radius - .016),
                       (-height / 2, radius - .016)]:
    for i in range(24):
      angle = i * math.tau / 24
      point = Vector((width * math.cos(angle), width * math.sin(angle), along))
      if axis == 'X':
        point = Vector((point.z, point.x, point.y))
      vertices.append(tuple(point + Vector(center)))
  for row in range(4):
    for i in range(24):
      j = (i + 1) % 24
      faces.append((row * 24 + i, row * 24 + j,
                    ((row + 1) % 4) * 24 + j, ((row + 1) % 4) * 24 + i))
  weights = [sample(Vector(p)) for p in vertices] if sample else None
  return smooth(mesh(ctx, name, vertices, faces, [mat],
                     bone=None if sample else bone, weights=weights), 40)


def helmet(ctx, mats):
  """Enclose the actual head in a smooth shell and curved opaque visor."""
  vertices, faces = [], []
  for row in range(1, 20):
    latitude = -math.pi / 2 + row * math.pi / 20
    for i in range(40):
      longitude = i * math.tau / 40
      vertices.append((.605 * math.cos(latitude) * math.sin(longitude),
                       .01 - .625 * math.cos(latitude) * math.cos(longitude),
                       2.54 + .66 * math.sin(latitude)))
  vertices += [(0, .01, 1.88), (0, .01, 3.20)]
  for row in range(18):
    for i in range(40):
      j = (i + 1) % 40
      faces.append((row * 40 + i, row * 40 + j,
                    (row + 1) * 40 + j, (row + 1) * 40 + i))
  for i in range(40):
    j = (i + 1) % 40
    faces += [(760, j, i), (761, 720 + i, 720 + j)]
  shell = smooth(mesh(ctx, 'Helmet', vertices, faces, [mats['fabric']], bone='Head'))

  def patch(name, span, height, depth, mat):
    """Map a rounded rectangular visor onto the helmet ellipsoid."""
    points, quads = [], []
    for row in range(9):
      v = row / 8 * 2 - 1
      for i in range(25):
        u = i / 24 * 2 - 1
        longitude = span * u * (1 - .10 * abs(v) ** 6)
        latitude = -.045 + height * v * (1 - .16 * abs(u) ** 6)
        points.append(((.605 + depth) * math.cos(latitude) * math.sin(longitude),
                       .01 - (.625 + depth) * math.cos(latitude) * math.cos(longitude),
                       2.54 + (.66 + depth) * math.sin(latitude)))
        if row and i:
          k = (row - 1) * 25 + i - 1
          quads.append((k, k + 1, k + 26, k + 25))
    return smooth(mesh(ctx, name, points, quads, [mat], bone='Head'))

  rim = patch('VisorSeal', 1.25, .48, .009, mats['rubber'])
  visor = patch('Visor', 1.20, .425, .017, mats['visor'])
  details = [ring(ctx, 'HelmetCollar', (0, .01, 1.955), .25, .095,
                  mats['metal'], 'Head')]
  for side in [-1, 1]:
    details.append(box(ctx, 'HelmetPort' + str(side),
                       (side * .602, .025, 2.48), (.055, .19, .22),
                       mats['metal'], 'Head', .015))
  return [shell, rim, visor] + details


def garment(ctx, name, surface, mat):
  """Preserve the real body's interpolated weights on an offset garment."""
  obj = meshObject(ctx.collection, ctx.prefix + name, [(surface, 0)], [mat],
                   preserveNormals=True)
  return bind(ctx, obj)


def build(ctx, mats):
  """Fit every suit module to the canonical body, hands, and feet."""
  source = bodySurface([ctx.body])
  chest = offset(clip(clip(clip(source,
    lambda p: p.z - 1.155), lambda p: 2.01 - p.z),
    lambda p: .977 - abs(p.x)), .05)
  pants = offset(clip(clip(source, lambda p: 1.225 - p.z),
                      lambda p: p.z - .33), .04)
  torso = [garment(ctx, 'PressureTop', chest, mats['fabric'])]
  legs = [garment(ctx, 'PressurePants', pants, mats['fabric'])]
  gloves, boots = [], []
  for side, label in [(1, 'Left'), (-1, 'Right')]:
    hand = bodySurface([bpy.data.objects['Hand.' + label]])
    gloves.append(garment(ctx, 'Glove' + label, offset(hand, .019), mats['rubber']))
    gloves.append(ring(ctx, 'WristSeal' + label, (side * .976, .015, 1.78),
                       .153, .075, mats['metal'], label + 'Hand', 'X',
                       sourceWeights(source + hand)))
    feet = bodySurface([ctx.body, bpy.data.objects['Foot.' + label]])
    feet = clip(clip(feet, lambda p: .365 - p.z), lambda p: side * p.x)
    raised = [[(Vector((p.x + n.x * .038, p.y + n.y * .05,
                        max(.008, p.z + n.z * .025))), n, w)
               for p, n, w in face] for face in feet]
    boots += [garment(ctx, 'Boot' + label,
                       clip(raised, lambda p: p.z - .055), mats['boots']),
              garment(ctx, 'Sole' + label,
                       clip(raised, lambda p: .055 - p.z), mats['rubber']),
              ring(ctx, 'AnkleSeal' + label, (side * .201, -.002, .345),
                   .175, .09, mats['metal'], label + 'Leg')]
    torso.append(garment(ctx, 'ArmBand' + label,
      band(chest, [lambda p: side * p.x - .80,
                   lambda p: .83 - side * p.x]), mats['metal']))
    for level in [.48, .73]:
      legs.append(box(ctx, 'LegTab' + label + str(level),
        (side * .201, -.155, level), (.12, .018, .023),
        mats['metal'], label + ('Leg' if level < .56 else 'UpLeg'), .003))
  torso.append(box(ctx, 'ControlBox', (0, -.322, 1.535), (.365, .105, .32),
                    mats['panel']))
  torso.append(box(ctx, 'Vent', (-.082, -.380, 1.595), (.12, .018, .11),
                    mats['rubber'], bevel=.003))
  for i in range(4):
    torso.append(box(ctx, 'VentBar' + str(i), (-.082, -.393, 1.56 + i * .023),
                      (.093, .012, .007), mats['metal'], bevel=0))
  torso.append(box(ctx, 'Display', (.075, -.380, 1.61), (.105, .018, .075),
                    mats['rubber'], bevel=.002))
  for i in range(2):
    torso.append(box(ctx, 'DisplayBar' + str(i), (.075, -.391, 1.596 + i * .025),
                      (.08, .01, .008), mats['metal'], bevel=0))
  torso.append(box(ctx, 'Switch', (.075, -.387, 1.485), (.047, .035, .085),
                    mats['metal']))
  top = torso[0].data
  tree = BVHTree.FromPolygons([v.co for v in top.vertices],
                              [p.vertices[:] for p in top.polygons])
  sample = sourceWeights(source)
  for side in [-1, 1]:
    points, faces, weights = [], [], []
    for row in range(25):
      z = 1.22 + row / 24 * .64
      x = side * (.095 + (z - 1.55) * .65)
      for edge in [-1, 1]:
        point, normal, _, _ = tree.ray_cast(Vector((x + edge * .023, -2, z)),
                                           Vector((0, 1, 0)))
        if point is None:
          raise ValueError('Harness projection missed the fitted top')
        point += normal * .015
        points.append(tuple(point))
        weights.append(sample(point))
      if row:
        k = (row - 1) * 2
        faces.append((k, k + 1, k + 3, k + 2))
    torso.append(smooth(mesh(ctx, 'Harness' + str(side), points, faces,
                            [mats['rubber']], weights=weights)))
    points, faces, weights = [], [], []
    for row in range(13):
      angle = row / 12 * math.pi
      center = Vector((side * (.188 + .058 * math.sin(angle)),
                       -.29 + .05 * math.sin(angle),
                       1.47 + .092 * math.cos(angle)))
      tangent = Vector((side * .058 * math.cos(angle),
                        .05 * math.cos(angle), -.092 * math.sin(angle))).normalized()
      across = tangent.cross(Vector((0, 1, 0))).normalized()
      up = tangent.cross(across).normalized()
      for i in range(10):
        theta = i * math.tau / 10
        radius = .025 + .002 * (row % 2)
        point = center + radius * (across * math.cos(theta) + up * math.sin(theta))
        points.append(tuple(point))
        weights.append(sample(point))
        if row:
          k = (row - 1) * 10 + i
          j = (row - 1) * 10 + (i + 1) % 10
          faces.append((k, j, j + 10, k + 10))
    torso.append(smooth(mesh(ctx, 'Hose' + str(side), points, faces,
                            [mats['rubber']], weights=weights)))
  waist = band(pants, [lambda p: p.z - 1.145,
                       lambda p: 1.195 - p.z], .028)
  belt = [garment(ctx, 'Belt', waist, mats['metal']),
          box(ctx, 'Buckle', (0, -.343, 1.171), (.075, .03, .065),
              mats['rubber'], 'Hips')]
  return {'Headgear': helmet(ctx, mats), 'Chest': torso, 'Leg': legs,
          'Hand': gloves, 'Foot': boots, 'Belt': belt}


def export(ctx, parts, manifest):
  """Export separate selectable parts with explicit white tint bindings."""
  objects = [obj for group in parts.values() for obj in group]
  bpy.ops.object.select_all(action='DESELECT')
  for obj in objects + [ctx.rig]:
    obj.hide_set(False)
    obj.select_set(True)
  bpy.context.view_layer.objects.active = ctx.rig
  bpy.ops.export_scene.gltf(filepath=str(Review / 'parts.glb'),
    export_format='GLB', use_selection=True, export_animations=False,
    export_skins=True, export_materials='EXPORT', export_yup=True)
  document, binary = glbs.read(Review / 'parts.glb')
  result = []
  for category, group in parts.items():
    identity = Folders[category] + '/astronaut_' + category.lower()
    names = [obj.name for obj in group]
    doc, blob = glbs.subset(document, binary, meshes=names)
    glbs.write(Library / (identity + '.glb'), doc, blob)
    shades = []
    for node in doc['nodes']:
      if 'mesh' not in node:
        continue
      for i, primitive in enumerate(doc['meshes'][node['mesh']]['primitives']):
        if doc['materials'][primitive['material']]['name'] == 'Astronaut fabric':
          shades.append(dict(node=node['name'], primitive=i, shade=1))
    hides = []
    if category == 'Headgear':
      for slot in manifest['categories']:
        if slot['key'] in ['Face', 'Hair', 'Beard', 'Eyes', 'Mouth', 'Nose',
                           'Ears', 'Brow', 'Earring', 'Eyewear']:
          for path in (Library / slot['directory']).glob('*.json'):
            hides += json.loads(path.read_text()).get('nodes', [])
    elif category == 'Hand':
      hides = ['Hand.Left', 'Hand.Right', 'GotaHand.Left', 'GotaHand.Right']
    elif category == 'Foot':
      hides = ['Foot.Left', 'Foot.Right', 'GotaFoot.Left', 'GotaFoot.Right']
    data = dict(id=identity, name='Astronaut ' + category.lower(), files=[identity + '.glb'],
      nodes=names, hides=sorted(set(hides)), alignment='both', singleFile=True,
      skinNodes=[], hairShades=[], hatShades=[], clothShades=shades)
    write(Library / (identity + '.json'), data)
    result.append(dict(category=category, **data))
  return result


def run():
  """Add only astronaut assets and its preset, preserving the shared master."""
  Output.mkdir(parents=True, exist_ok=True)
  Review.mkdir(parents=True, exist_ok=True)
  bpy.ops.wm.open_mainfile(filepath=str(Source / 'character.blend'))
  rig, body = bpy.data.objects['CharacterRig'], bpy.data.objects['Body']
  rig.animation_data.action = None
  rig.data.pose_position = 'REST'
  for bone in rig.pose.bones:
    bone.matrix_basis.identity()
  tree = KDTree(len(body.data.vertices))
  for vertex in body.data.vertices:
    tree.insert(vertex.co, vertex.index)
  tree.balance()
  ctx = SimpleNamespace(rig=rig, body=body, collection=body.users_collection[0],
    tree=tree, prefix='Astronaut_', preview=Review)
  manifest = json.loads((Library / 'manifest.json').read_text())
  parts = build(ctx, palette())
  metadata = export(ctx, parts, manifest)
  choices = {slot['key']: 'None' for slot in manifest['categories']}
  choices.update({'Body': 'Base', 'Face': 'Base'})
  for category in parts:
    choices[category] = 'Astronaut ' + category.lower()
  preset = dict(name='Astronaut', group='Space', pose='A_TPose', skin=5,
    hairColor='Chestnut', pupilColor='Gray', parts=[dict(category=key, item=value)
    for key, value in choices.items()])
  for path in [Library / 'manifest.json', Source / 'manifest.json']:
    current = json.loads(path.read_text())
    current['presets'] = [p for p in current['presets'] if p['name'] != 'Astronaut'] + [preset]
    if path.parent == Source:
      for entry in metadata:
        slot = next(s for s in current['categories'] if s['key'] == entry['category'])
        slot['items'] = [p for p in slot['items'] if p['name'] != entry['name']]
        slot['items'].append({k: v for k, v in entry.items() if k != 'category'})
    write(path, current)
  write(Output / 'parts.json', metadata)
  write(Output / 'preset.json', preset)
  privateLibrary(ctx, manifest, preset)
  visible = {obj.name for group in parts.values() for obj in group} | {'Body'}
  for obj in bpy.data.objects:
    if obj.type == 'MESH':
      obj.hide_render = obj.name not in visible
      obj.hide_set(obj.hide_render)
  for obj in list(bpy.data.objects):
    if obj.type == 'MESH' and obj.name not in visible:
      bpy.data.objects.remove(obj, do_unlink=True)
  bpy.context.preferences.filepaths.save_version = 0
  bpy.ops.wm.save_as_mainfile(filepath=str(Output / 'astronaut.blend'))
  doc, _ = glbs.read(Review / 'parts.glb')
  triangles, nodes = count(doc)
  write(Output / 'geometry.json', dict(triangles=triangles, nodes=nodes,
    rig='rig/humanoid.glb', tint='White fabric, per-slot clothShades',
    construction='Body-derived fitted shells and original solid-color equipment'))
  print('ASTRONAUT BUILT', triangles, 'equipment triangles', flush=True)


if __name__ == '__main__':
  run()
