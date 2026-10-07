"""Validate exported astronaut geometry, canonical binds, and tint regions."""

import json
import math
import struct
from pathlib import Path

import glbs
from paths import Library, Source

Sizes = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}
Formats = {5121: 'B', 5123: 'H', 5125: 'I', 5126: 'f'}


def accessor(document, binary, index):
  """Decode tightly packed or interleaved glTF values for validation."""
  data = document['accessors'][index]
  view = document['bufferViews'][data['bufferView']]
  code = Formats[data['componentType']]
  layout = '<' + code * Sizes[data['type']]
  stride = view.get('byteStride', struct.calcsize(layout))
  start = view.get('byteOffset', 0) + data.get('byteOffset', 0)
  return [struct.unpack_from(layout, binary, start + i * stride)
          for i in range(data['count'])]


def binds(document, binary):
  """Associate each inverse bind matrix with its canonical joint name."""
  result = {}
  for skin in document.get('skins', []):
    matrices = accessor(document, binary, skin['inverseBindMatrices'])
    for joint, matrix in zip(skin['joints'], matrices):
      result[document['nodes'][joint]['name']] = matrix
  return result


def run():
  """Require normalized four-weight skins and white-only dye surfaces."""
  canonical, canonicalBinary = glbs.read(Library / 'rig/humanoid.glb')
  # The mesh-free rig stores rest nodes; the current body supplies its binds.
  body, bodyBinary = glbs.read(Library / 'body/body.glb')
  reference = binds(body, bodyBinary)
  canonicalNames = {n['name'] for n in canonical['nodes']}
  report = {'parts': [], 'triangles': 0, 'vertices': 0,
            'maxBindError': 0, 'maxWeightError': 0}
  for part in json.loads((Source / 'astronaut/parts.json').read_text()):
    document, binary = glbs.read(Library / part['files'][0])
    current = binds(document, binary)
    assert set(current) == set(reference)
    assert set(current) <= canonicalNames
    error = max(abs(a - b) for name in current
                for a, b in zip(current[name], reference[name]))
    assert error < 1e-5, (part['name'], error)
    report['maxBindError'] = max(report['maxBindError'], error)
    tinted = {(s['node'], s['primitive']) for s in part['clothShades']}
    triangles, vertices, degenerates = 0, 0, 0
    for node in document['nodes']:
      if 'mesh' not in node:
        continue
      for i, primitive in enumerate(document['meshes'][node['mesh']]['primitives']):
        attributes = primitive['attributes']
        points = accessor(document, binary, attributes['POSITION'])
        normals = accessor(document, binary, attributes['NORMAL'])
        weights = accessor(document, binary, attributes['WEIGHTS_0'])
        joints = accessor(document, binary, attributes['JOINTS_0'])
        assert 'WEIGHTS_1' not in attributes
        assert all(math.isfinite(v) for p in points + normals for v in p)
        for values, ids in zip(weights, joints):
          error = abs(sum(values) - 1)
          report['maxWeightError'] = max(report['maxWeightError'], error)
          assert error < 1e-5 and min(values) >= 0
          assert all(0 <= j < len(current) for j in ids)
          if part['category'] == 'Headgear':
            skin = document['skins'][node['skin']]
            assert all(document['nodes'][skin['joints'][j]]['name'] == 'Head'
                       for j, w in zip(ids, values) if w > 0)
        color = document['materials'][primitive['material']][
          'pbrMetallicRoughness'].get('baseColorFactor', [1, 1, 1, 1])
        if (node['name'], i) in tinted:
          assert color == [1, 1, 1, 1], (node['name'], color)
        indices = [v[0] for v in accessor(document, binary, primitive['indices'])]
        for k in range(0, len(indices), 3):
          a, b, c = (points[indices[k + j]] for j in range(3))
          u, v = [b[j] - a[j] for j in range(3)], [c[j] - a[j] for j in range(3)]
          area = sum((u[(j + 1) % 3] * v[(j + 2) % 3] -
                      u[(j + 2) % 3] * v[(j + 1) % 3]) ** 2 for j in range(3))
          degenerates += area < 1e-16
        triangles += len(indices) // 3
        vertices += len(points)
    assert degenerates == 0, (part['name'], degenerates)
    report['triangles'] += triangles
    report['vertices'] += vertices
    report['parts'].append(dict(name=part['name'], triangles=triangles,
      exportedVertices=vertices, degenerateTriangles=degenerates,
      tintPrimitives=len(tinted)))
  report['assembledTriangles'] = report['triangles'] + sum(
    body['accessors'][p['indices']]['count'] // 3
    for mesh in body['meshes'] for p in mesh['primitives'])
  report['sampledVisualReview'] = ['T-pose', 'Walk_Loop at 0.35 seconds',
    'Crouch_Fwd_Loop at 0.35 seconds', 'Front/back, sides, toon and smooth lighting']
  report['limitations'] = 'Sampled poses do not establish all-frame collision freedom.'
  (Source / 'astronaut/verification.json').write_text(json.dumps(report, indent=2) + '\n')
  print(json.dumps(report, indent=2))


if __name__ == '__main__':
  run()
