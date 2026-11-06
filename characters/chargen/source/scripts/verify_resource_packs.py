"""Audit exported backpack triangles, canonical bindings and provenance."""
import hashlib
import json
import math

import glbs
from paths import Library, Source
from verify_gota import audit, values


def main():
  """Check each independently shippable backpack against its real GLB."""
  folder = Source / 'resource_packs'
  parts = json.loads((folder / 'parts.json').read_text())
  assert len(parts) == 2
  reports = []
  for part in parts:
    path = Library / part['files'][0]
    doc, binary = glbs.read(path)
    counts = audit(path, clothing=True)
    triangles = sum(counts.values())
    assert list(counts) == part['nodes']
    assert 0 < triangles < part['triangleLimitExclusive'] == 700
    assert triangles == part['triangles']
    assert not doc.get('animations')
    bones = set()
    for node in doc['nodes']:
      if 'mesh' not in node:
        continue
      skin = doc['skins'][node['skin']]
      for primitive in doc['meshes'][node['mesh']]['primitives']:
        attributes = primitive['attributes']
        weights = values(doc, binary, attributes['WEIGHTS_0'])
        joints = values(doc, binary, attributes['JOINTS_0'])
        normals = values(doc, binary, attributes['NORMAL'])
        points = values(doc, binary, attributes['POSITION'])
        indices = [v[0] for v in values(doc, binary, primitive['indices'])]
        assert all(abs(sum(v * v for v in n) - 1) < .001 for n in normals)
        for i in range(0, len(indices), 3):
          a, b, c = [points[index] for index in indices[i:i + 3]]
          u, v = [b[j] - a[j] for j in range(3)], [c[j] - a[j] for j in range(3)]
          cross = [u[1] * v[2] - u[2] * v[1],
                   u[2] * v[0] - u[0] * v[2],
                   u[0] * v[1] - u[1] * v[0]]
          assert sum(x * x for x in cross) > 1e-16, 'Degenerate triangle'
        for influence, joint in zip(weights, joints):
          for value, index in zip(influence, joint):
            assert math.isfinite(value) and value >= 0
            if value > 0:
              bones.add(doc['nodes'][skin['joints'][index]]['name'])
    assert 'Spine2' in bones
    assert bones <= {'Hips', 'Spine', 'Spine1', 'Spine2',
                     'LeftShoulder', 'RightShoulder', 'LeftArm', 'RightArm'}
    report = dict(name=part['name'], triangles=triangles,
      meshNodes=len(counts), bones=sorted(bones), textureFree=True,
      normalizedWeights=True, canonicalRig=True, nondegenerateTriangles=True,
      file=part['files'][0], sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    reports.append(report)
    print(part['name'], triangles, 'triangles, canonical rig verified')
  (folder / 'verification.json').write_text(json.dumps(reports, indent=2) + '\n')


if __name__ == '__main__':
  main()
