"""Capture Zeus in the runtime renderer and map each asset to its concept."""

import html
import json
import os
import subprocess
from pathlib import Path

from paths import Project, Source

Output = Source / 'gota' / 'zeus'
Concepts = {
  'Chest': ('torso/tunic_front_back.png', 'Tunic and bracers'),
  'Belt': ('torso/belt_front_back.png', 'Eagle belt'),
  'Back': ('torso/cape_front_back.png', 'Royal blue cape'),
  'Headgear': ('head/crown.png', 'Laurel crown'),
  'Hair': ('head/hair.png', 'Flowing white hair'),
  'Beard': ('head/beard.png', 'Full tapered beard'),
  'Leg': ('legs/reference.png', 'Skirt: top row of reference'),
  'Foot': ('legs/reference.png', 'Greaves and sandals: bottom row'),
  'Right hand': ('props/reference.png', 'Lightning bolt: top row'),
  'Left hand': ('props/reference.png', 'Lightning spell: bottom row')
}


def capture():
  """Capture all isolated modules plus assembled front, back and side poses."""
  renderer = Project / 'tmp' / 'chargen' / 'zeus_review_renderer'
  subprocess.run(['nim', 'c', '-o:' + str(renderer),
                  'experiments/chargen/render_gota.nim'], cwd=Project, check=True)
  for folder, angle in [('front_back', '0'), ('sides', '1.57079632679')]:
    environment = dict(os.environ,
      CHARGEN_LIBRARY=str(Project / 'tmp/chargen/gota/zeus/library'),
      REVIEW_PRESET='Zeus', REVIEW_ALL_PARTS='1', REVIEW_ANGLE=angle,
      REVIEW_OUTPUT=str(Output / 'renders' / folder))
    subprocess.run([str(renderer)], cwd=Project, env=environment, check=True)


def gallery():
  """Write a compact concept-to-runtime review with exact exported counts."""
  parts = json.loads((Output / 'parts.json').read_text())
  report = json.loads((Output / 'verification.json').read_text())
  rows = []
  for entry in parts:
    category = entry['category']
    reference, note = Concepts[category]
    count = sum(report['nodes'].get(node, 0) for node in entry['nodes'])
    rows.append(dict(category=category, name=entry['name'], triangles=count,
      reference=reference, referenceDescription=note,
      frontBack='renders/front_back/' + category.replace(' ', '_') + '.png',
      sides='renders/sides/' + category.replace(' ', '_') + '.png'))
  (Output / 'review.json').write_text(json.dumps(dict(
    hero='Zeus', visibleTriangles=report['triangles'], items=rows,
    rig='Existing shared CharacterRig', eyes='Existing 16 Determined',
    clothingTextures=0, referenceTool='Built-in imagegen'), indent=2) + '\n')
  cards = []
  for entry in rows:
    cards.append(f'''<section><h2>{html.escape(entry['name'])}</h2>
<p>{html.escape(entry['category'])} · {entry['triangles']:,} triangles · {html.escape(entry['referenceDescription'])}</p>
<div class="pair"><figure><img loading="lazy" src="{entry['reference']}"><figcaption>Generated front/back concept</figcaption></figure>
<figure><img loading="lazy" src="{entry['frontBack']}"><figcaption>Actual runtime front/back mesh</figcaption></figure></div>
<details><summary>Side views</summary><img loading="lazy" src="{entry['sides']}"></details></section>''')
  poses = ''.join(f'<figure><img loading="lazy" src="renders/{folder}/{pose}.png"><figcaption>{label}</figcaption></figure>'
    for folder, pose, label in [
      ('front_back', 'model', 'Complete outfit: front and back'),
      ('sides', 'model', 'Complete outfit: both sides'),
      ('front_back', 'walk', 'Walk pose: front and back'),
      ('sides', 'walk', 'Walk pose: both sides'),
      ('front_back', 'crouch', 'Crouch pose: front and back'),
      ('sides', 'crouch', 'Crouch pose: both sides')])
  document = '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Zeus · Gota gods asset review</title><style>
*{box-sizing:border-box}body{margin:0;background:#eeece7;color:#25272a;font:16px/1.5 system-ui,sans-serif}
main{max-width:1500px;margin:auto;padding:36px}h1{font-size:42px;margin:0}h2{margin-bottom:8px}p{margin-top:0;color:#565752}
section{background:#fff;border:1px solid #d7d4ca;border-radius:12px;padding:24px;margin:24px 0}
.pair,.poses{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0;min-width:0}img{width:100%;display:block;background:#bbb8b0;border-radius:6px}
figcaption{padding:8px 0;color:#5d605b;font-size:14px}a{color:#205abb}summary{cursor:pointer;padding:12px 0}details img{max-width:900px}
@media(max-width:800px){main{padding:18px}.pair,.poses{grid-template-columns:1fr}}
</style><main><h1>Zeus</h1><p>Polyworld Gota god · modular solid-color clothing and equipment</p>
'''
  document += f'<p>{report["triangles"]:,} visible triangles including the existing body and eyes. Each new item is under 5,000 triangles. The existing rig, face and eye assets are reused.</p>'
  document += '<p><a href="reference.png">Original Zeus and Hades reference</a> · <a href="verification.json">Export verification</a> · <a href="review.json">Item mapping</a> · <a href="judgment.md">Independent judge review</a></p>'
  document += '<p>Built-in imagegen prompts: <a href="torso/prompts.json">tunic, belt and cape</a> · <a href="head/prompts.json">crown, hair and beard</a> · <a href="legs/prompt.txt">skirt and sandals</a> · <a href="props/prompt.txt">lightning equipment</a>.</p>'
  document += '<section><h2>Complete character and movement checks</h2><div class="poses">' + poses + '</div></section>'
  document += ''.join(cards) + '</main></html>'
  (Output / 'review.html').write_text(document)


capture()
gallery()
