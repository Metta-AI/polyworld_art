"""Verify the Druid's exported positions, skin weights, and rig transforms."""

import json
import math
import struct
import sys
from pathlib import Path

Root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Root / 'source/scripts'))
import glbs


def accessor(document, binary, index):
  """Read tightly packed or interleaved core glTF attribute values."""
  value = document['accessors'][index]
  view = document['bufferViews'][value['bufferView']]
  components = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}
  formats = {5126: 'f', 5123: 'H', 5121: 'B', 5125: 'I'}
  count, format = components[value['type']], formats[value['componentType']]
  stride = view.get('byteStride', struct.calcsize(format) * count)
  offset = view.get('byteOffset', 0) + value.get('byteOffset', 0)
  return [struct.unpack_from('<' + format * count, binary, offset + i * stride)
          for i in range(value['count'])]


def verify():
  """Check every selected exported primitive against the shared rig."""
  output = Path(__file__).parent
  parts = json.loads((output / 'parts.json').read_text())
  rig, _ = glbs.read(Root / 'rig/humanoid.glb')
  originals = {node['name']: node for node in rig['nodes']}
  checked, reports = 0, []
  for part in parts:
    document, binary = glbs.read(Root / part['files'][0])
    bones = set()
    for skin in document['skins']:
      for index in skin['joints']:
        node = document['nodes'][index]
        bones.add(node['name'])
        original = originals[node['name']]
        for key, default in [('translation', [0, 0, 0]),
                             ('rotation', [0, 0, 0, 1]), ('scale', [1, 1, 1])]:
          assert all(abs(a - b) < .00001 for a, b in zip(
            node.get(key, default), original.get(key, default)))
    for mesh in document['meshes']:
      for primitive in mesh['primitives']:
        attributes = primitive['attributes']
        assert 'JOINTS_0' in attributes and 'WEIGHTS_0' in attributes
        positions = accessor(document, binary, attributes['POSITION'])
        for position in positions:
          assert all(math.isfinite(component) for component in position)
        for weights in accessor(document, binary, attributes['WEIGHTS_0']):
          assert abs(sum(weights) - 1) < .0001
          assert all(0 <= weight <= 1 for weight in weights)
        checked += len(positions)
    assert not document.get('textures')
    reports.append(dict(slot=part['category'], file=part['files'][0],
      sharedBoneCount=len(bones), finite=True, normalizedWeights=True,
      noImageTextures=True))
  result = dict(exportedVerticesChecked=checked, parts=reports,
                rigLocalTransformsMatch=True)
  (output / 'export_verification.json').write_text(json.dumps(result, indent=2) + '\n')
  print('Verified', checked, 'exported vertices across', len(parts), 'parts.')


verify()
