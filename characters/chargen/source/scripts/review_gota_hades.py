"""Generate the Hades concept-to-runtime asset review index."""

import html
import json
from pathlib import Path

Folder = Path(__file__).resolve().parents[1] / 'gota' / 'hades'
Concepts = {'Headgear': 'crown', 'Hair': 'hair_beard',
  'Beard': 'hair_beard', 'Chest': 'chest', 'Belt': 'belt',
  'Leg': 'legs', 'Foot': 'boots', 'Back': 'cape',
  'Right hand': 'equipment', 'Left hand': 'equipment'}


def generate():
  """Map each independently selectable module to its concept and real capture."""
  report = json.loads((Folder / 'verification.json').read_text())
  parts = json.loads((Folder / 'parts.json').read_text())
  result = ['<!doctype html><html lang="en"><meta charset="utf-8">',
    '<title>Hades garment review</title>',
    '<style>body{font:16px system-ui;background:#191a1d;color:#e9e6df;',
    'margin:30px auto;max-width:1500px;padding:0 24px}a{color:#83c7fa}',
    'img{width:100%;background:#494b50}section{margin:44px 0}',
    '.pair{display:grid;grid-template-columns:1fr 1fr;gap:20px}',
    'h1,h2{color:#e9c475}figcaption{padding:8px 0}figure{margin:0}',
    'table{border-collapse:collapse}td,th{padding:8px 16px;',
    'border:1px solid #58595b;text-align:left}</style>',
    '<h1>Hades</h1>',
    f'<p>{report["triangles"]:,} rendered triangles including the reused ',
    'body, face and eyes. Each garment and equipment module is under 5,000 ',
    'triangles. Existing rig and eyes are unchanged. Garments have solid ',
    'materials without textures.</p>',
    '<p>Concept sheets were generated with built-in imagegen from the user ',
    'reference. Back views extend the visible design conservatively. ',
    'Runtime captures below use the actual exported GLBs and shared rig.</p>',
    '<p><a href="verification.json">Verification</a> · ',
    '<a href="hero.blend">Authoring scene</a> · ',
    '<a href="concepts/prompts_hades_head.json">Head/equipment prompts</a> · ',
    '<a href="concepts/prompts_hades_clothing.json">Clothing prompts</a></p>']
  for name, image in [('Front and back', 'model'),
      ('Left and right sides', 'side/model'), ('Walk', 'walk'),
      ('Crouch', 'crouch'), ('Crouch sides', 'side/crouch')]:
    result.append(f'<section><h2>{name}</h2><img src="renders/{image}.png" '
      f'alt="Hades {name}"></section>')
  result.append('<h2>Modular assets</h2><table><tr><th>Slot</th>'
    '<th>Asset</th><th>Triangles</th></tr>')
  for item in parts:
    count = sum(report['nodes'].get(node, 0) for node in item['nodes'])
    result.append(f'<tr><td>{html.escape(item["category"])}</td>'
      f'<td>{html.escape(item["name"])}</td><td>{count:,}</td></tr>')
  result.append('</table>')
  for item in parts:
    slot = item['category']
    filename = slot.replace(' ', '_')
    result.append(f'<section><h2>{html.escape(item["name"])}</h2>'
      '<div class="pair"><figure>'
      f'<img src="concepts/{Concepts[slot]}.png" alt="{slot} concept">'
      '<figcaption>Generated front/back concept.</figcaption></figure>'
      f'<figure><img src="renders/{filename}.png" alt="{slot} exported mesh">'
      '<figcaption>Actual GLB, front/back. '
      f'<a href="renders/side/{filename}.png">Side capture</a>.'
      '</figcaption></figure></div></section>')
  result.append('</html>')
  (Folder / 'review.html').write_text(
    '\n'.join(line.rstrip() for line in result) + '\n')


generate()
