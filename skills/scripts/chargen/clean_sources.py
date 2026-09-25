"""Remove retired imported data from existing authoring files without remeshing."""

import hashlib
import json
import shutil
import struct
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import Library, Preview, Source
from provenance import LegacyEyes, LegacyNodes


def geometry():
  """Hash retained geometry, skin weights and rig rest matrices for comparison."""
  result = {}
  for obj in bpy.data.objects:
    if obj.name in LegacyNodes or obj.type not in {'MESH', 'ARMATURE'}:
      continue
    digest = hashlib.sha256()
    if obj.type == 'MESH':
      for vertex in obj.data.vertices:
        digest.update(struct.pack('<3f', *vertex.co))
        for group in vertex.groups:
          digest.update(struct.pack('<If', group.group, group.weight))
      for face in obj.data.polygons:
        digest.update(struct.pack('<' + 'I' * len(face.vertices), *face.vertices))
    else:
      for bone in obj.data.bones:
        digest.update(bone.name.encode())
        for row in bone.matrix_local:
          digest.update(struct.pack('<4f', *row))
    result[obj.name] = digest.hexdigest()
  return result


def retiredImage(image):
  """Identify the removed eye textures and old body comparison screenshot."""
  name = Path(image.filepath).name or image.name
  return name in {part + '.png' for part in LegacyEyes} | {'01_base_body.png'}


def inspect(allowed):
  """List retired content without loading any external images or characters."""
  return {
    'objects': [obj.name for obj in bpy.data.objects
                if obj.name in LegacyNodes or obj.name == 'Approved concept'],
    'actions': [action.name for action in bpy.data.actions
                if action.name not in allowed],
    'images': [image.name for image in bpy.data.images if retiredImage(image)],
  }


def clean(path, allowed, check):
  """Strip only retired content, preserving every retained mesh and rig value."""
  bpy.ops.wm.open_mainfile(filepath=str(path))
  retired = inspect(allowed)
  if check:
    assert not any(retired.values()), (path, retired)
    return {'file': str(path.relative_to(Source)), 'clean': True}
  before = geometry()
  backup = Preview / 'legacy_source_backup' / path.relative_to(Source)
  if not backup.exists():
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup)
  for name in retired['objects']:
    obj = bpy.data.objects[name]
    data = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    if isinstance(data, bpy.types.Mesh) and data.users == 0:
      bpy.data.meshes.remove(data)
  for name in retired['actions']:
    bpy.data.actions.remove(bpy.data.actions[name], do_unlink=True)
  for material in list(bpy.data.materials):
    if material.use_nodes and any(node.type == 'TEX_IMAGE' and node.image and
        retiredImage(node.image) for node in material.node_tree.nodes):
      assert material.users == 0, (path, material.name)
      bpy.data.materials.remove(material)
  for name in retired['images']:
    bpy.data.images.remove(bpy.data.images[name], do_unlink=True)
  assert geometry() == before, 'Retained mesh or rig changed: ' + str(path)
  assert not any(inspect(allowed).values()), path
  bpy.context.preferences.filepaths.save_version = 0
  bpy.ops.wm.save_as_mainfile(filepath=str(path))
  print('CLEANED', path.relative_to(Source), retired, flush=True)
  return {'file': str(path.relative_to(Source)), 'removed': retired,
          'retainedGeometryUnchanged': True}


def main():
  """Clean or verify all tracked character authoring scenes in the library."""
  arguments = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
  check = '--check' in arguments
  manifest = json.loads((Library / 'manifest.json').read_text())
  assert all(clip['kind'] == 'universal' for clip in manifest['clips'])
  allowed = {clip['name'] for clip in manifest['clips']}
  report = [clean(path, allowed, check) for path in sorted(Source.rglob('*.blend'))]
  if not check:
    (Source / 'clean_sources.json').write_text(json.dumps(report, indent=2) + '\n')
  print('VERIFIED' if check else 'CLEANED', len(report), 'authoring files')


if __name__ == '__main__':
  main()
