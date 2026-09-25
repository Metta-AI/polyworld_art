"""Audit the two exported god presets against their actual runtime assets."""

import hashlib
import json
from paths import Library, Source
from register_gota import Gods
from verify_gota import audit

Slots = {'Headgear', 'Hair', 'Beard', 'Chest', 'Belt', 'Leg', 'Foot',
         'Back', 'Right hand', 'Left hand'}


def main():
  """Verify selected geometry, shared rig, materials and per-item budgets."""
  manifest = json.loads((Library/'manifest.json').read_text())
  inventory = {}
  for category in manifest['categories']:
    for path in (Library/category['directory']).glob('*.json'):
      item = json.loads(path.read_text())
      inventory[(category['key'], item['name'])] = item
  presets = [preset for preset in manifest['presets']
             if preset.get('group') == 'Gota Gods']
  assert [preset['name'].lower() for preset in presets] == Gods
  reports = []
  for preset in presets:
    slug = preset['name'].lower()
    choices = {choice['category']: choice['item'] for choice in preset['parts']}
    assert len(choices) == len(manifest['categories'])
    assert choices['Body'] == 'Gota base' and choices['Face'] == 'Base'
    selected = [(slot, inventory[(slot, name)])
                for slot, name in choices.items() if name not in ['', 'None']]
    visible, hidden, counts, files, slots = set(manifest['base']), set(), {}, {}, {}
    for slot, item in selected:
      visible.update(item['nodes'])
      hidden.update(item.get('hides', []))
      own = slot in Slots
      if own:
        assert f'gota_{slug}_' in item['id'], (slug, slot)
        assert len(item['files']) == 1, (slug, slot)
      for path in item['files']:
        counts.update(audit(Library/path, clothing=own))
        files[path] = hashlib.sha256((Library/path).read_bytes()).hexdigest()
      if own:
        triangles = sum(counts[name] for name in item['nodes'])
        assert 0 < triangles < 5000, (slug, slot, triangles)
        slots[slot] = triangles
    assert set(slots) == Slots
    visible -= hidden
    assert visible <= counts.keys(), (slug, visible-counts.keys())
    total = sum(counts[name] for name in visible)
    assert total < 20000, (slug, total)
    reports.append(dict(name=preset['name'], triangles=total, slots=slots,
      triangleLimitExclusive=20000, itemTriangleLimitExclusive=5000,
      sharedRig=True, reusedBody=True, reusedEyes=True,
      normalizedWeights=True, finiteGeometry=True, newClothingTextures=0,
      visibleNodes=sorted(visible), files=files))
    print(f"{preset['name']}: {total} triangles, ten modular parts verified.")
  output = Source/'gota/gods/audit.json'
  output.parent.mkdir(parents=True, exist_ok=True)
  output.write_text(json.dumps(reports, indent=2)+'\n')


if __name__ == '__main__':
  main()
