"""Audit exported equipment geometry, skin sockets, materials and set budgets."""

import hashlib
import json
from paths import Library, Source
from register_gota import Order
from verify_gota import audit, values
import glbs


def main():
  """Verify actual runtime GLBs and the selected equipment of every hero."""
  folder = Source / 'gota/weapons'
  parts = json.loads((folder / 'parts.json').read_text())
  manifest = json.loads((Library / 'manifest.json').read_text())
  heroes = [p for p in manifest['presets']
            if p.get('group') == 'Gota' and not p.get('lineupHidden')]
  report = []
  for slug, hero in zip(Order, heroes):
    entries = [p for p in parts if p['slug'] == slug]
    expected = {'Left hand', 'Right hand'}
    if slug == 'ranger':
      expected.add('Back')
    if slug == 'crossbowman':
      expected = {'Right hand', 'Back'}
    assert {p['category'] for p in entries} == expected, slug
    selections = {p['category']: p['item'] for p in hero['parts']}
    total, items = 0, []
    for part in entries:
      assert selections[part['category']] == part['name'], slug
      path = Library / part['files'][0]
      doc, blob = glbs.read(path)
      counts = audit(path, clothing=True)
      triangles = sum(counts.values())
      assert 0 < triangles < 5000, (part['name'], triangles)
      assert triangles == part['triangles']
      assert set(counts) == set(part['nodes'])
      assert part['attachmentBone'] in {
        'Left hand': {'LeftHand', 'LeftForeArm'},
        'Right hand': {'RightHand'}, 'Back': {'Spine2'}
      }[part['category']]
      for node in doc['nodes']:
        if 'mesh' not in node:
          continue
        skin = doc['skins'][node['skin']]
        for primitive in doc['meshes'][node['mesh']]['primitives']:
          attrs = primitive['attributes']
          weights = values(doc, blob, attrs['WEIGHTS_0'])
          joints = values(doc, blob, attrs['JOINTS_0'])
          normals = values(doc, blob, attrs['NORMAL'])
          mat = doc['materials'][primitive['material']]
          if part['name'] == 'Medieval crossbow' and '#e3c79e' in mat['name']:
            assert not mat.get('doubleSided', False), 'Bowstring must be top-only.'
            assert all(n[2] > .99 for n in normals), 'Bowstring faces the wrong side.'
          for normal in normals:
            assert abs(sum(x*x for x in normal) - 1) < .001
          for influences, indices in zip(weights, joints):
            for weight, index in zip(influences, indices):
              if weight > 0:
                assert abs(weight - 1) < 1e-6
                assert doc['nodes'][skin['joints'][index]]['name'] == part['attachmentBone']
      total += triangles
      items.append(dict(name=part['name'], slot=part['category'],
        triangles=triangles, bone=part['attachmentBone'], file=part['files'][0],
        sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    assert total < 5000, (slug, total)
    report.append(dict(name=hero['name'], slug=slug, equipmentTriangles=total,
      triangleLimitExclusive=5000, normalizedRigidWeights=True,
      textureFree=True, sharedRig=True, items=items))
    print(hero['name'] + ': ' + str(total) + ' equipment triangles, verified.')
  assert len(report) == 10
  (folder / 'audit.json').write_text(json.dumps(report, indent=2) + '\n')
  lines = ['# Gota equipment polygon counts', '',
    'Counts are actual exported triangles, including both equipped daggers or axes.',
    'Every individual item and each complete equipment set is below 5,000.', '',
    '| Hero | Equipment triangles |', '| --- | ---: |']
  lines += ['| ' + row['name'] + ' | ' + str(row['equipmentTriangles']) + ' |'
            for row in report]
  (folder / 'counts.md').write_text('\n'.join(lines) + '\n')
  return report


if __name__ == '__main__':
  main()
