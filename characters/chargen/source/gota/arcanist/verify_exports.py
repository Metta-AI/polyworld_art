"""Verify exported Arcanist clothing values and compatibility with the rig."""
import json
import math
from pathlib import Path
import struct
import sys

Root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Root / 'source/scripts'))
import glbs


def values(document, binary, index):
  """Read one packed glTF accessor with its declared byte stride."""
  accessor = document['accessors'][index]
  view = document['bufferViews'][accessor['bufferView']]
  formats = {5120: 'b', 5121: 'B', 5122: 'h', 5123: 'H', 5125: 'I', 5126: 'f'}
  sizes = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}
  pattern = '<' + formats[accessor['componentType']] * sizes[accessor['type']]
  stride = view.get('byteStride', struct.calcsize(pattern))
  offset = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
  return [struct.unpack_from(pattern, binary, offset + i * stride)
          for i in range(accessor['count'])]


def main():
  """Validate actual exported modules against the shared skeleton."""
  rig, rigBytes = glbs.read(Root / 'body/body.glb')
  rigSkin = rig['skins'][0]
  rigNames = [rig['nodes'][index]['name'] for index in rigSkin['joints']]
  rigMatrices = values(rig, rigBytes, rigSkin['inverseBindMatrices'])
  byName = dict(zip(rigNames, rigMatrices))
  directory = Path(__file__).resolve().parent
  parts = json.loads((directory / 'parts.json').read_text())
  report = []
  for part in parts:
    for filename in part['files']:
      document, binary = glbs.read(Root / filename)
      vertices = 0
      for node in document['nodes']:
        if 'mesh' not in node:
          continue
        assert 'skin' in node
        skin = document['skins'][node['skin']]
        names = [document['nodes'][index]['name'] for index in skin['joints']]
        assert set(names) == set(rigNames)
        matrices = values(document, binary, skin['inverseBindMatrices'])
        for name, matrix in zip(names, matrices):
          assert max(abs(a - b) for a, b in zip(matrix, byName[name])) < 1e-5
        for primitive in document['meshes'][node['mesh']]['primitives']:
          attrs = primitive['attributes']
          positions = values(document, binary, attrs['POSITION'])
          weights = values(document, binary, attrs['WEIGHTS_0'])
          joints = values(document, binary, attrs['JOINTS_0'])
          assert len(positions) == len(weights) == len(joints)
          assert all(math.isfinite(c) for position in positions for c in position)
          assert all(abs(sum(v) - 1) < 1e-5 for v in weights)
          assert all(all(0 <= j < len(names) for j in row) for row in joints)
          vertices += len(positions)
      assert not document.get('textures')
      report.append(dict(file=filename, vertices=vertices, finite=True,
                         normalizedWeights=True, sharedBindMatrices=True,
                         sharedSkeleton=True, imageTextures=0))
  (directory / 'export_audit.json').write_text(json.dumps(report, indent=2) + '\n')
  print(json.dumps(report, indent=2))


main()
