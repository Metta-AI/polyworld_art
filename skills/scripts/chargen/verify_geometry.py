"""Check reduced runtime geometry, skinning, seams, and gnome triangle budgets."""

import argparse
import json
import math
import struct
from collections import Counter
from pathlib import Path

import glbs
from count_polygons import main as countPolygons
from paths import Preview
from verify_library import channels, payload


def values(document, binary, index):
  """Decode packed accessor values for numeric geometry checks."""
  accessor = document['accessors'][index]
  width = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}[accessor['type']]
  kind = {5121: 'B', 5123: 'H', 5125: 'I', 5126: 'f'}[accessor['componentType']]
  return list(struct.iter_unpack('<' + kind * width, payload(document, binary, index)))


def boundary(document, binary, primitive):
  """Find geometric boundary vertices without mistaking normal seams for holes."""
  positions = values(document, binary, primitive['attributes']['POSITION'])
  indices = [value[0] for value in values(document, binary, primitive['indices'])]
  edges = Counter()
  for i in range(0, len(indices), 3):
    triangle = [positions[index] for index in indices[i:i+3]]
    for a, b in zip(triangle, triangle[1:] + triangle[:1]):
      edges[tuple(sorted((a, b)))] += 1
  return {point for edge, count in edges.items() if count == 1 for point in edge}


def main():
  """Validate game exports and optionally compare against a pre-reduction GLB."""
  parser = argparse.ArgumentParser()
  parser.add_argument('--baseline', type=Path)
  args = parser.parse_args()
  document, binary = glbs.read(Preview / 'character.glb')
  reduced = {entry['name'] for entry in json.loads(
    (Preview / 'character.geometry.json').read_text())}
  nodes = {node['name']: node for node in document['nodes'] if 'mesh' in node}
  for name in reduced:
    node = nodes[name]
    jointCount = len(document['skins'][node['skin']]['joints'])
    for primitive in document['meshes'][node['mesh']]['primitives']:
      attributes = primitive['attributes']
      arrays = {key: values(document, binary, index)
                for key, index in attributes.items()}
      count = len(arrays['POSITION'])
      assert all(len(array) == count for array in arrays.values()), name
      assert all(math.isfinite(v) for array in arrays.values()
                 for entry in array for v in entry), name
      for normal in arrays['NORMAL']:
        assert abs(sum(v*v for v in normal) - 1) < .002, (name, normal)
      for weights in arrays['WEIGHTS_0']:
        assert min(weights) >= 0 and abs(sum(weights) - 1) < .0001, (name, weights)
      assert all(0 <= joint < jointCount for entry in arrays['JOINTS_0']
                 for joint in entry), name
      indices = values(document, binary, primitive['indices'])
      assert len(indices) % 3 == 0
      assert all(0 <= entry[0] < count for entry in indices), name
  if args.baseline:
    old, oldBytes = glbs.read(args.baseline)
    oldNodes = {node['name']: node for node in old['nodes'] if 'mesh' in node}
    assert oldNodes.keys() == nodes.keys()
    for name, node in nodes.items():
      original = oldNodes[name]
      skin = document['skins'][node['skin']]
      oldSkin = old['skins'][original['skin']]
      assert [document['nodes'][i]['name'] for i in skin['joints']] == [
        old['nodes'][i]['name'] for i in oldSkin['joints']], name
      assert payload(document, binary, skin['inverseBindMatrices']) == payload(
        old, oldBytes, oldSkin['inverseBindMatrices']), name
      first = document['meshes'][node['mesh']]['primitives']
      second = old['meshes'][original['mesh']]['primitives']
      if name not in reduced:
        for a, b in zip(first, second, strict=True):
          assert a['attributes'].keys() == b['attributes'].keys(), name
          for field in a['attributes']:
            assert payload(document, binary, a['attributes'][field]) == payload(
              old, oldBytes, b['attributes'][field]), (name, field)
          assert payload(document, binary, a['indices']) == payload(
            old, oldBytes, b['indices']), name
      if name.startswith('Hand.'):
        assert boundary(document, binary, first[0]) == boundary(
          old, oldBytes, second[0]), (name, 'Wrist boundary changed')
    assert {clip['name']: channels(document, binary, clip)
            for clip in document['animations']} == {
      clip['name']: channels(old, oldBytes, clip) for clip in old['animations']}
    print('VERIFIED unchanged meshes, wrist boundaries, bind matrices and clips.')
  countPolygons()
  presets = json.loads((Preview / 'polygons/gnomes.json').read_text())
  assert len(presets) == 9
  assert all(entry['triangles'] < 15000 for entry in presets), presets
  print('VERIFIED', len(reduced), 'reduced meshes; all nine gnomes below 15,000 triangles.')


if __name__ == '__main__':
  main()
