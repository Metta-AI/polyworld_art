"""Build isolated Gota parts on the existing Chargen rig without shared rebuilds."""
import importlib
import json
import math
import sys
from pathlib import Path
from types import SimpleNamespace

import bpy
import bmesh
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True
from paths import Library, Source, Preview
from clothes import band, bodySurface, material, meshObject
from optimizations import normalizeWeights
import glbs

Folders = {'Foot': 'clothing/boots', 'Leg': 'clothing/pants',
  'Belt': 'clothing/belts', 'Chest': 'clothing/torsos', 'Headgear': 'hats',
  'Hair': 'hair', 'Beard': 'beards', 'Back': 'clothing/backs',
  'Hand': 'clothing/gloves', 'Left hand': 'props/left',
  'Right hand': 'props/right'}


def write(path, data):
  """Persist readable generated metadata."""
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(json.dumps(data, indent=2) + '\n')


def bind(ctx, obj):
  """Bind a normalized weighted mesh to the unmodified shared skeleton."""
  obj.parent = ctx.rig
  obj.hide_set(False)
  obj.hide_render = False
  for modifier in list(obj.modifiers):
    if modifier.type == 'ARMATURE':
      obj.modifiers.remove(modifier)
  obj.modifiers.new('Shared humanoid rig', 'ARMATURE').object = ctx.rig
  normalizeWeights(obj)
  return obj


def smooth(obj, angle=50):
  """Blend curved surface normals while preserving sharp rims and seams."""
  if obj.data.has_custom_normals:
    obj.data.normals_split_custom_set([(0, 0, 0)] * len(obj.data.loops))
  edit = bmesh.new()
  edit.from_mesh(obj.data)
  for face in edit.faces:
    face.smooth = True
  for edge in edit.edges:
    edge.smooth = (len(edge.link_faces) == 2 and
                   edge.calc_face_angle() < math.radians(angle))
  edit.to_mesh(obj.data)
  edit.free()
  obj.data.update()
  return obj


def fitHead(obj, subdivide=False, minimumZ=None):
  """Keep fitted cloth outside the head with a small geometric clearance."""
  if subdivide:
    edit = bmesh.new()
    edit.from_mesh(obj.data)
    bmesh.ops.subdivide_edges(edit, edges=list(edit.edges), cuts=1,
                              use_grid_fill=True)
    edit.to_mesh(obj.data)
    edit.free()
  head = bpy.data.objects['Head'].data
  tree = BVHTree.FromPolygons([vertex.co for vertex in head.vertices],
                              [face.vertices[:] for face in head.polygons])
  for vertex in obj.data.vertices:
    if minimumZ is not None and vertex.co.z < minimumZ:
      continue
    point, normal, index, distance = tree.find_nearest(vertex.co)
    if (vertex.co - point).dot(normal) < .060:
      vertex.co = point + normal * .060
  obj.data.update()
  return obj


def roundedHood(ctx, suffix, colors, opening, rearTrim=False):
  """Join a distinctive angular face opening to a fitted rounded skull."""
  # Samples run from the forehead center to one loose lower cloth point.
  profiles = {
    'pointed': [
      (0, (0, 3.16, -.660), (0, 3.25, -.635)),
      (4, (.24, 2.97, -.665), (.30, 3.045, -.635)),
      (8, (.40, 2.65, -.660), (.46, 2.69, -.640)),
      (12, (.56, 2.27, -.640), (.64, 2.275, -.615)),
      (14, (.38, 2.10, -.610), (.43, 2.04, -.585)),
      (16, (.10, 1.91, -.500), (.06, 1.845, -.490))
    ],
    'crowned': [
      (0, (0, 2.91, -.680), (0, 2.99, -.660)),
      (3, (.16, 3.02, -.680), (.175, 3.12, -.660)),
      (5, (.28, 2.90, -.680), (.345, 2.97, -.660)),
      (11, (.48, 2.25, -.650), (.56, 2.25, -.630)),
      (12, (.50, 2.20, -.650), (.58, 2.18, -.630)),
      (14, (.31, 2.04, -.590), (.37, 2.00, -.570)),
      (16, (.23, 1.91, -.530), (.24, 1.84, -.510))
    ],
    'stepped': [
      (0, (0, 3.09, -.670), (0, 3.18, -.645)),
      (2, (.13, 2.985, -.670), (.155, 3.07, -.645)),
      (5, (.335, 2.91, -.670), (.405, 2.98, -.645)),
      (11, (.46, 2.22, -.645), (.545, 2.235, -.620)),
      (12, (.49, 2.14, -.630), (.58, 2.13, -.605)),
      (14, (.34, 1.995, -.565), (.42, 1.98, -.540)),
      (16, (.23, 1.91, -.500), (.21, 1.83, -.480))
    ]
  }
  profile = profiles[opening]
  foreheadDrop = {'pointed': .28, 'crowned': .34, 'stepped': .31}[opening]
  foreheadSpan = 11 if opening == 'crowned' else 12

  def outline(sample, outer):
    """Interpolate straight cloth edges without rounding their key corners."""
    for start, end in zip(profile, profile[1:]):
      if sample <= end[0]:
        blend = (sample - start[0]) / (end[0] - start[0])
        index = 2 if outer else 1
        return tuple(a + (b - a) * blend
          for a, b in zip(start[index], end[index]))
    return profile[-1][2 if outer else 1]

  columns = 33
  rings = [(.465, .400, .660, -.620),
           (.500, .435, .680, -.620),
           (.590, .510, .570, -.585),
           (.610, .575, .570, -.460),
           (.590, .585, .590, -.180),
           (.580, .570, .610, .150),
           (.505, .495, .610, .420),
           (.315, .330, .610, .580)]
  vertices, faces, shades = [], [], []
  for row, (width, top, drop, depth) in enumerate(rings):
    for i in range(columns):
      across = (i/(columns-1)*2-1)
      side = -1 if across < 0 else 1
      arc = abs(across)/.7
      if arc <= 1:
        angle = arc*math.pi/2
        x = side*width*math.sin(angle)
        z = 2.565+top*math.cos(angle)
        y = depth
      else:
        lower = (abs(across)-.7)/.3
        if row <= 1:
          flare = 1+.12*min(1, lower/.73)
          fold = max(0, (lower-.73)/.27)
          x = side*width*(flare-.42*fold)
          y = depth+.20*lower*lower
        elif row <= 4:
          x = side*width*(1+.13*math.sin(math.pi*lower))
          y = depth+.055*lower*lower-.035*math.sin(math.pi*lower)
        else:
          taper = [.13, .35, .55][row-5]
          x = side*width*(1-taper*lower)
          y = depth+.045*lower*lower
        z = 2.565-drop*lower
      if row < 4:
        sample = abs(i - columns // 2)
        frontX, frontZ, frontY = outline(sample, row != 0)
        if row < 2:
          frontZ -= foreheadDrop * max(0, 1 - (sample / foreheadSpan) ** 3)
        blend = [1, 1, .65, .20][row]
        x += (side * frontX - x) * blend
        y += (frontY - y) * blend
        z += (frontZ - z) * blend
      vertices.append((x, y, z))
      if row and i:
        a, b = (row-1)*columns+i-1, (row-1)*columns+i
        faces.append((a, b, b+columns, a+columns))
        shades.append(1 if row == 1 else 0)
  vertices.append((0, .650, 2.57))
  rear = (len(rings)-1)*columns
  for i in range(columns-1):
    faces.append((rear+i, rear+i+1, len(vertices)-1))
    shades.append(0)
  pole = len(vertices)-1
  vertices.append((0, .570, 1.93))
  faces.extend([(rear+columns-1, len(vertices)-1, pole),
                (len(vertices)-1, rear, pole)])
  shades.extend([0, 0])
  obj = mesh(ctx, suffix, vertices, faces, colors, bone='Head')
  for face, shade in zip(obj.data.polygons, shades):
    face.material_index = shade
  # Fit only the skull; loose cheek curtains must hang below the jaw.
  fitHead(obj, minimumZ=2.30)
  # The rim already clears the face and must retain its designed outline.
  for vertex in obj.data.vertices[:columns * 2]:
    vertex.co = vertices[vertex.index]
  obj.data.update()
  bpy.context.view_layer.objects.active = obj
  thickness = obj.modifiers.new('Draped hood cloth thickness', 'SOLIDIFY')
  thickness.thickness = .018
  thickness.offset = -1
  thickness.material_offset = 2
  bpy.ops.object.modifier_apply(modifier=thickness.name)
  if rearTrim:
    edgePoints = [Vector(vertices[row*columns]) for row in range(len(rings))]
    edgePoints.append(Vector(vertices[-1]))
    edgePoints += [Vector(vertices[row*columns+columns-1])
                   for row in reversed(range(len(rings)))]

    def edgeBand(point):
      """Follow the full cloth hem through its folds instead of cutting at Y."""
      distances = []
      for start, end in zip(edgePoints, edgePoints[1:]):
        segment = end-start
        amount = max(0, min(1, (point-start).dot(segment)/segment.length_squared))
        distances.append((point-start-amount*segment).length)
      return .045-min(distances)

    center = Vector((0, 0, 2.565))
    surface = [face for face in bodySurface([obj])
      if sum(normal.dot(point-center) for point, normal, _ in face) > 0]
    hem = band(surface, [edgeBand], .006)
    edge = colors[1]
    if isinstance(edge, str):
      edge = material(ctx.prefix+suffix+'Hem', edge)
    trim = meshObject(ctx.collection, ctx.prefix+suffix+'Hem', [(hem, 0)], [edge])
    bind(ctx, trim)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    trim.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.join()
  obj['construction'] = opening + ' opening, draped corners and rounded skull'
  smooth(obj, 65)
  for face in obj.data.polygons[:columns - 1]:
    face.use_smooth = False
  return obj


def duplicate(ctx, sourcePrefix, suffix, colors=None):
  """Copy fitted source geometry and weights without editing the source part."""
  result = []
  sources = [obj for obj in bpy.data.objects if obj.type == 'MESH' and
    (obj.name == sourcePrefix or obj.name.startswith(sourcePrefix + '_BootCut'))]
  if not sources:
    raise ValueError('Missing source part: ' + sourcePrefix)
  for source in sorted(sources, key=lambda obj: obj.name):
    obj = source.copy()
    obj.data = source.data.copy()
    obj.name = ctx.prefix + suffix + source.name[len(sourcePrefix):]
    ctx.collection.objects.link(obj)
    for i, entry in enumerate(obj.data.materials):
      if colors and i < len(colors) and colors[i] is not None:
        obj.data.materials[i] = material(obj.name + ' color ' + str(i), colors[i])
      elif entry:
        obj.data.materials[i] = entry.copy()
    for face in obj.data.polygons:
      face.use_smooth = False
    if obj.data.has_custom_normals:
      obj.data.normals_split_custom_set([(0, 0, 0)] * len(obj.data.loops))
    bind(ctx, obj)
    result.append(obj)
  return result


def mesh(ctx, suffix, vertices, faces, materials, bone=None, weights=None):
  """Create a solid-color faceted part with rigid or sampled skin weights."""
  data = bpy.data.meshes.new(ctx.prefix + suffix)
  data.from_pydata(vertices, [], faces)
  data.update()
  edit = bmesh.new()
  edit.from_mesh(data)
  bmesh.ops.recalc_face_normals(edit, faces=list(edit.faces))
  edit.to_mesh(data)
  edit.free()
  for i, entry in enumerate(materials):
    data.materials.append(material(ctx.prefix + suffix + str(i), entry)
                          if isinstance(entry, str) else entry)
  obj = bpy.data.objects.new(ctx.prefix + suffix, data)
  ctx.collection.objects.link(obj)
  for i, vertex in enumerate(data.vertices):
    if bone:
      influences = {bone: 1}
    elif weights is not None:
      influences = weights[i]
    else:
      _, index, _ = ctx.tree.find(vertex.co)
      source = ctx.body.data.vertices[index]
      influences = {ctx.body.vertex_groups[g.group].name: g.weight
                    for g in source.groups}
    for name, value in influences.items():
      group = obj.vertex_groups.get(name) or obj.vertex_groups.new(name=name)
      group.add([i], value, 'REPLACE')
  return bind(ctx, obj)


def part(ctx, category, label, objects, hides=None, attachmentBone=None,
         keepFeet=False):
  """Describe one independently selectable outfit module."""
  if not isinstance(objects, (tuple, list)):
    objects = [objects]
  descriptor = dict(category=category, name=label, objects=list(objects),
                    hides=list(hides or []))
  if attachmentBone:
    descriptor['attachmentBone'] = attachmentBone
  if keepFeet:
    descriptor['keepFeet'] = True
  return descriptor


def inventory(manifest):
  """Read the current runtime inventory without modifying sidecars."""
  result = {}
  for category in manifest['categories']:
    for path in sorted((Library / category['directory']).glob('*.json')):
      data = json.loads(path.read_text())
      if 'nodes' in data and 'files' in data:
        result[(category['key'], data['name'])] = data
  return result


def count(document, names=None):
  """Count rendered exported triangle lists for selected node names."""
  total = 0
  nodes = {}
  for node in document['nodes']:
    if 'mesh' not in node or names is not None and node['name'] not in names:
      continue
    number = 0
    for primitive in document['meshes'][node['mesh']]['primitives']:
      assert primitive.get('mode', 4) == 4
      accessor = primitive.get('indices', primitive['attributes']['POSITION'])
      number += document['accessors'][accessor]['count'] // 3
    nodes[node['name']] = number
    total += number
  return total, nodes


def completePreset(ctx, preset, parts, manifest):
  """Make every optional slot explicit so previous presets cannot leak in."""
  choices = {category['key']: 'None' for category in manifest['categories']}
  choices.update({'Body': 'Gota base', 'Face': 'Base', 'Nose': 'Tiny',
                  'Eyes': '02 Focused', 'Mouth': '03 Neutral',
                  'Brow': '04 Heroic'})
  values = {choice['category']: choice for choice in preset.get('parts', [])}
  values['Body'] = dict(category='Body', item='Gota base')
  for category, name in choices.items():
    values.setdefault(category, dict(category=category, item=name))
  for descriptor in parts:
    values[descriptor['category']] = dict(category=descriptor['category'],
                                          item=descriptor['name'])
  preset['parts'] = list(values.values())
  preset.setdefault('group', 'Gota')
  preset.setdefault('pose', 'A_TPose')
  preset.setdefault('skin', 16)
  preset.setdefault('hairColor', 'Chestnut')
  preset.setdefault('pupilColor', 'Blue')
  return preset


def exportParts(ctx, parts):
  """Export only new unique objects and split them into independent assets."""
  objects = [obj for entry in parts for obj in entry['objects']]
  for obj in objects:
    assert obj.name.startswith(ctx.prefix), obj.name
    assert all(math.isfinite(c) for v in obj.data.vertices for c in v.co)
    bind(ctx, obj)
    for vertex in obj.data.vertices:
      assert abs(sum(g.weight for g in vertex.groups) - 1) < .0001
    for mat in obj.data.materials:
      if mat and mat.use_nodes:
        assert not any(node.type == 'TEX_IMAGE' for node in mat.node_tree.nodes), mat.name
  ctx.rig.animation_data.action = None
  ctx.rig.data.pose_position = 'REST'
  bpy.ops.object.select_all(action='DESELECT')
  for obj in objects + [ctx.rig]:
    obj.hide_set(False)
    obj.select_set(True)
  bpy.context.view_layer.objects.active = ctx.rig
  assembled = ctx.preview / 'parts.glb'
  bpy.ops.export_scene.gltf(filepath=str(assembled), export_format='GLB',
    use_selection=True, export_animations=False, export_skins=True,
    export_materials='EXPORT', export_yup=True)
  document, binary = glbs.read(assembled)
  metadata = []
  for entry in parts:
    category = entry['category']
    identity = (Folders[category] + '/gota_' + ctx.slug + '_' +
                category.lower().replace(' ', '_'))
    names = [obj.name for obj in entry['objects']]
    doc, blob = glbs.subset(document, binary, meshes=names)
    glbs.write(Library / (identity + '.glb'), doc, blob)
    hides = entry['hides'][:]
    hides += ['Gota' + name for name in entry['hides']
              if name in ['Hand.Left', 'Hand.Right', 'Foot.Left', 'Foot.Right']]
    if category == 'Foot' and not entry.get('keepFeet', False):
      hides += ['Foot.Left', 'Foot.Right', 'GotaFoot.Left', 'GotaFoot.Right']
    if category == 'Leg':
      hides += ['GotaSkinLower']
    data = dict(id=identity, name=entry['name'], files=[identity + '.glb'],
      nodes=names, hides=sorted(set(hides)), alignment='both', singleFile=True,
      skinNodes=[], hairShades=[], hatShades=[], clothShades=[])
    if entry.get('attachmentBone'):
      data['attachmentBone'] = entry['attachmentBone']
    write(Library / (identity + '.json'), data)
    metadata.append(dict(category=category, **data))
  return metadata


def privateLibrary(ctx, manifest, preset):
  """Prepare a hero-specific manifest using shared current assets by symlink."""
  directory = ctx.preview / 'library'
  directory.mkdir(exist_ok=True)
  for child in Library.iterdir():
    if child.name in ('source', 'manifest.json', 'colors'):
      continue
    link = directory / child.name
    if not link.exists():
      link.symlink_to(child, target_is_directory=child.is_dir())
  colors = directory / 'colors'
  colors.mkdir(exist_ok=True)
  for source in (Library / 'colors').glob('*.json'):
    (colors / source.name).write_bytes(source.read_bytes())
  if 'skinRgb' in preset:
    skins = json.loads((directory / manifest['skinPalette']).read_text())
    preset['skin'] = len(skins)
    skins.append(dict(name='Gota ' + preset['name'], color=preset['skinRgb'] + [1]))
    write(directory / manifest['skinPalette'], skins)
  private = dict(manifest, presets=[preset], defaultAnimation='A_TPose')
  write(directory / 'manifest.json', private)
  return directory


def verify(ctx, manifest, preset, metadata):
  """Count actual visible runtime parts, including existing face and body."""
  items = inventory(manifest)
  selected = [items[(choice['category'], choice['item'])]
    for choice in preset['parts'] if choice['item'] not in ('', 'None')]
  shown = set(manifest.get('base', []))
  hidden = set()
  for item in selected:
    shown.update(item['nodes'])
    hidden.update(item.get('hides', []))
  shown -= hidden
  counts = {}
  for item in selected:
    for file in item['files']:
      doc, _ = glbs.read(Library / file)
      _, nodes = count(doc, shown)
      counts.update(nodes)
  total = sum(counts.values())
  report = dict(name=preset['name'], slug=ctx.slug, triangles=total,
    underBudget=total < 20000, budgetExclusive=20000, nodes=counts,
    slots=[entry['category'] for entry in metadata],
    newClothingTextures=0, normalizedWeights=True,
    reusedParts=[item['id'] for item in selected if 'gota_' not in item['id']])
  write(ctx.output / 'verification.json', report)
  return report


def run(slug):
  """Build one isolated hero and leave all shared source state untouched."""
  output, preview = Source / 'gota' / slug, Preview / 'gota' / slug
  output.mkdir(parents=True, exist_ok=True)
  preview.mkdir(parents=True, exist_ok=True)
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
    slug=slug, prefix='Gota_' + slug + '_', output=output, preview=preview,
    library=Library, tree=tree)
  builder = importlib.import_module('gota_' + slug)
  parts, preset = builder.build(ctx)
  manifest = json.loads((Library / 'manifest.json').read_text())
  preset = completePreset(ctx, preset, parts, manifest)
  metadata = exportParts(ctx, parts)
  write(output / 'parts.json', metadata)
  directory = privateLibrary(ctx, manifest, preset)
  write(output / 'preset.json', preset)
  report = verify(ctx, manifest, preset, metadata)
  bpy.context.preferences.filepaths.save_version = 0
  bpy.ops.wm.save_as_mainfile(filepath=str(output / 'hero.blend'))
  print('GOTA BUILT', slug, report['triangles'], 'triangles', flush=True)
  print('GOTA LIBRARY', directory, flush=True)
  if not report['underBudget']:
    print('OVER BUDGET: reduce geometry and rebuild.', flush=True)


if __name__ == '__main__':
  run(sys.argv[sys.argv.index('--') + 1])
