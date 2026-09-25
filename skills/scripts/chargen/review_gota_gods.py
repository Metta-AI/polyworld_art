"""Build a local index of the god concepts, actual models and review evidence."""

import html
import json
from PIL import Image, ImageDraw, ImageFont
from paths import Source


def main():
  """Link the final modelers' front/back comparisons without altering renders."""
  folder = Source/'gota/gods'
  folder.mkdir(parents=True, exist_ok=True)
  sections = []
  lineup = Image.new('RGB', (1600, 1200), '#efeeeb')
  labels = ImageDraw.Draw(lineup)
  font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 34)
  for column, (slug, render) in enumerate([
      ('zeus', 'renders/front_back/model.png'),
      ('hades', 'renders/model.png')]):
    god = Source/'gota'/slug
    report = json.loads((god/'verification.json').read_text())
    raw = Image.open(god/render).convert('RGB')
    lineup.paste(raw.crop((0, 0, 800, 1100)), (column*800, 60))
    labels.text((column*800+350, 10), report['name'], font=font, fill='#222222')
    prompts = sorted(path.relative_to(god) for path in god.rglob('*prompt*')
                     if path.is_file())
    links = ''.join(f'<li><a href="../{slug}/{html.escape(str(path))}">'
                    f'{html.escape(str(path))}</a></li>' for path in prompts)
    sections.append(f'<section><h2>{report["name"]}</h2>'
      f'<p>{report["triangles"]:,} visible triangles. Ten modular parts, '
      'existing body and eyes, solid-color clothing materials.</p>'
      f'<img src="../{slug}/{render}" alt="{report["name"]} actual front and back">'
      f'<p><a href="../{slug}/review.html">Individual concepts and model review</a>'
      f' · <a href="../{slug}/hero.blend">Blender model</a>'
      f' · <a href="../{slug}/preset.json">Preset</a></p>'
      '<details><summary>Image generation prompts</summary>'
      '<p>Front/back concepts were generated with the built-in imagegen tool.</p>'
      f'<ul>{links}</ul></details></section>')
  lineup.save(folder/'lineup.png')
  (folder/'index.html').write_text('<!doctype html><meta charset="utf-8">'
    '<title>Gota gods: Zeus and Hades</title><style>'
    'body{max-width:1500px;margin:32px auto;padding:0 24px;background:#efeeeb;'
    'color:#222;font:18px/1.5 sans-serif}img{max-width:100%;display:block}'
    'section{margin:48px 0}a{color:#235a91}</style>'
    '<h1>Gota gods: Zeus and Hades</h1>'
    '<p>Chargen: Character → God presets → Zeus or Hades. '
    'Animations → Gota gods shows both together.</p>'
    '<img src="lineup.png" alt="Zeus and Hades actual runtime models">'
    '<p><a href="judgment.md">Independent visual judgment</a> · '
    '<a href="audit.json">Export and triangle audit</a></p>'
    '<details><summary>Original reference</summary>'
    '<img src="../zeus/reference.png" alt="Original Zeus and Hades concept">'
    '</details>'+''.join(sections))
  print(folder/'index.html')


if __name__ == '__main__':
  main()
