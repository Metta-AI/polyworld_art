"""Report actual rendered triangles for the nine assembled gnome presets."""

import json

from paths import Library, Preview
import glbs
from pack import inventory

def main():
  """Count selected GLB primitives after resolving runtime visibility masks."""
  manifest = json.loads((Library / 'manifest.json').read_text())
  items = inventory(Library, manifest)
  byName = {(category, item['name']): item for category, path, item in items.values()}
  meshes = {}
  for category, path, item in items.values():
    for filename in item['files']:
      document, binary = glbs.read(Library / filename)
      for node in document['nodes']:
        if 'mesh' not in node:
          continue
        triangles, vertices, primitives = 0, 0, 0
        for primitive in document['meshes'][node['mesh']]['primitives']:
          mode = primitive.get('mode', 4)
          assert mode == 4, (filename, 'Expected triangle list', mode)
          points = document['accessors'][primitive['attributes']['POSITION']]['count']
          count = document['accessors'][primitive['indices']]['count'] if 'indices' in primitive else points
          assert count % 3 == 0
          triangles += count // 3
          vertices += points
          primitives += 1
        meshes[node['name']] = dict(category=category, part=item['name'],
          triangles=triangles, vertices=vertices, primitives=primitives)
  report = []
  for preset in manifest['presets']:
    if preset.get('group') != 'Gnomes':
      continue
    choices = {category['key']: category.get('defaultItem', '')
               for category in manifest['categories']}
    choices.update({part['category']: part['item'] for part in preset['parts']})
    shown, hidden = set(manifest['base']), set()
    for category, name in choices.items():
      if not name or name == 'None':
        continue
      item = byName[category, name]
      shown.update(item['nodes'])
      hidden.update(item.get('hides', []))
    shown -= hidden
    parts = {}
    nodes = []
    for name in sorted(shown):
      data = meshes[name]
      nodes.append(dict(node=name, **data))
      key = (data['category'], data['part'])
      if key not in parts:
        parts[key] = dict(category=key[0], part=key[1], triangles=0,
                           vertices=0, primitives=0)
      for field in ['triangles', 'vertices', 'primitives']:
        parts[key][field] += data[field]
    report.append(dict(name=preset['name'],
      triangles=sum(meshes[name]['triangles'] for name in shown),
      vertices=sum(meshes[name]['vertices'] for name in shown),
      primitives=sum(meshes[name]['primitives'] for name in shown),
      nodes=nodes, parts=sorted(parts.values(), key=lambda p: -p['triangles'])))
  output = Preview / 'polygons'
  output.mkdir(parents=True, exist_ok=True)
  (output / 'gnomes.json').write_text(json.dumps(report, indent=2) + '\n')
  lines = ['# Gnome geometry audit', '',
    'Counts use exported GLB triangle lists after applying each preset and its',
    'visibility masks. Hidden feet and tucked trouser sections are excluded.',
    'Covered body surfaces and clothing interiors still drawn are included.',
    'Vertices include duplicates at material, UV, and normal seams.', '',
    '| Gnome | Triangles | Exported vertices | Material primitives |',
    '| --- | ---: | ---: | ---: |']
  for entry in report:
    lines.append(f"| {entry['name']} | {entry['triangles']:,} | {entry['vertices']:,} | {entry['primitives']} |")
  for entry in report:
    lines += ['', '## ' + entry['name'], '',
              '| Slot | Part | Triangles |', '| --- | --- | ---: |']
    for part in entry['parts']:
      lines.append(f"| {part['category']} | {part['part']} | {part['triangles']:,} |")
  (output / 'gnomes.md').write_text('\n'.join(lines) + '\n')
  for entry in report:
    print(entry['name'], entry['triangles'], 'triangles;', entry['primitives'], 'material primitives')
  print('Saved', output / 'gnomes.md')


if __name__ == '__main__':
  main()
