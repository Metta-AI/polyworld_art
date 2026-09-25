"""Render equipped heroes and assemble contact sheets of actual runtime meshes."""

import argparse
import json
import os
import subprocess
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

from paths import Library, Source, Preview
from verify_gota import values
from verify_gota_weapons import main as verify
import glbs


def cropItem(image):
  """Trim only the uniform render background around an isolated item."""
  background = Image.new('RGB', image.size, image.getpixel((0, 0)))
  bounds = ImageChops.difference(image, background).getbbox()
  assert bounds, 'Empty item render.'
  return image.crop(bounds)


def bounds(path):
  """Read item extents from the exported geometry for consistent sheet scale."""
  doc, blob = glbs.read(path)
  points = []
  for node in doc['nodes']:
    if 'mesh' in node:
      for primitive in doc['meshes'][node['mesh']]['primitives']:
        points += values(doc, blob, primitive['attributes']['POSITION'])
  return ([min(p[i] for p in points) for i in range(3)],
          [max(p[i] for p in points) for i in range(3)])


def main():
  """Optionally recapture models, then publish views, budgets and sources."""
  parser = argparse.ArgumentParser()
  parser.add_argument('--render', action='store_true')
  parser.add_argument('--lit', action='store_true')
  args = parser.parse_args()
  folder = Source / 'gota/weapons'
  report = verify()
  renders = 'renders_lit' if args.lit else 'renders'
  prefix = 'lit_' if args.lit else ''
  font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 24)
  small = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 18)
  for hero in report:
    output = folder / renders / hero['slug']
    output.mkdir(parents=True, exist_ok=True)
    if args.render:
      with (Preview / 'gota/weapons' / (hero['slug'] + '.log')).open('w') as log:
        subprocess.run([str(Preview / 'gota/render_gota')], check=True,
          env=dict(os.environ, REVIEW_PRESET=hero['name'], REVIEW_EQUIPMENT='1',
                   REVIEW_OUTPUT=str(output), REVIEW_PBR='1' if args.lit else '0',
                   REVIEW_ANGLE='.32' if args.lit else '0'), stdout=log, stderr=subprocess.STDOUT)
      print('Rendered ' + hero['name'], flush=True)
  for pose in ['model', 'walk', 'crouch']:
    for side in ['front', 'back']:
      sheet = Image.new('RGB', (2000, 1160), '#b8b6b0')
      draw = ImageDraw.Draw(sheet)
      for i, hero in enumerate(report):
        source = Image.open(folder / renders / hero['slug'] / (pose + '.png')).convert('RGB')
        left = 0 if side == 'front' else 800
        view = source.crop((left, 0, left + 800, 1100))
        view.thumbnail((400, 520))
        x, y = i % 5 * 400, i // 5 * 580
        sheet.paste(view, (x + (400 - view.width) // 2, y))
        draw.text((x + 200, y + 520), hero['name'], anchor='mt', font=font, fill='#222222')
        draw.text((x + 200, y + 551), str(hero['equipmentTriangles']) + ' equipment triangles',
                  anchor='mt', font=small, fill='#444444')
      sheet.save(folder / (prefix + pose + '_' + side + '.png'))
  sheet = Image.new('RGB', (2200, 1100), '#b8b6b0')
  draw = ImageDraw.Draw(sheet)
  for i, hero in enumerate(report):
    x, y = i % 5 * 440, i // 5 * 550
    draw.text((x + 220, y + 15), hero['name'], anchor='mt', font=font, fill='#222222')
    items = {p['slot']: p for p in hero['items']}
    entries = []
    for slot in ['Right hand', 'Left hand', 'Back']:
      if slot not in items or slot == 'Left hand' and hero['slug'] in ['demon_hunter', 'berserker']:
        continue
      item = items[slot]
      source = Image.open(folder / renders / hero['slug'] / (slot.replace(' ', '_') + '.png')).convert('RGB')
      low, high = bounds(Library / item['file'])
      both = 'shield' in item['name'] or item['name'] == 'Medieval crossbow'
      for side in range(2 if both else 1):
        view = cropItem(source.crop((side * 800, 0, (side + 1) * 800, 1100)))
        label = ''
        if both:
          label = (['TOP', 'BOTTOM'] if item['name'] == 'Medieval crossbow'
                   else ['FRONT', 'BACK'])[side]
        if args.lit:
          high = list(high)
          high[0] = low[0] + view.width / view.height * (high[1]-low[1])
        entries.append((view, low, high, label))
    lowest = min(low[1] for _, low, _, _ in entries)
    highest = max(high[1] for _, _, high, _ in entries)
    width = sum(high[0] - low[0] for _, low, high, _ in entries)
    scale = min(415 / (highest - lowest), (400 - 12 * (len(entries) - 1)) / width)
    offset = x + (440 - width * scale - 12 * (len(entries) - 1)) / 2
    for view, low, high, label in entries:
      w, h = max(1, round((high[0] - low[0]) * scale)), max(1, round((high[1] - low[1]) * scale))
      view = view.resize((w, h), Image.Resampling.LANCZOS)
      top = y + 65 + (highest - high[1]) * scale
      sheet.paste(view, (round(offset), round(top)))
      if label:
        draw.text((offset + w / 2, top + h + 9), label, anchor='mt', font=small, fill='#333333')
      offset += w + 12
    draw.text((x + 220, y + 515), str(hero['equipmentTriangles']) + ' triangles equipped',
              anchor='mt', font=small, fill='#333333')
  sheet.save(folder / (prefix + 'equipment_models.png'))
  if args.lit:
    reference = Image.open(folder / 'equipment_simplified_v2.png').convert('RGB')
    reference = reference.resize((2200, 1100), Image.Resampling.LANCZOS)
    comparison = Image.new('RGB', (2200, 2320), '#eeeeec')
    titles = ImageDraw.Draw(comparison)
    titles.text((1100, 18), 'APPROVED REFERENCE', anchor='mt', font=font, fill='#222222')
    comparison.paste(reference, (0, 60))
    titles.text((1100, 1178), 'REVISED GLB ASSETS — SOFT LIGHT, SLIGHT ANGLE',
                anchor='mt', font=font, fill='#222222')
    comparison.paste(sheet, (0, 1220))
    comparison.save(folder / 'comparison.png')
    return
  cards = []
  for hero in report:
    links = []
    for part in hero['items']:
      view = part['slot'].replace(' ', '_') + '.png'
      links.append('<a href="renders/' + hero['slug'] + '/' + view + '">' +
        part['name'] + '</a> (' + str(part['triangles']) + ' triangles) · ' +
        '<a href="../../../' + part['file'] + '">GLB</a>')
    cards.append('<section><h2>' + hero['name'] + '</h2><p>' + ' | '.join(links) +
      '</p><img src="renders/' + hero['slug'] + '/model.png">' +
      '<details><summary>Walk and crouch</summary><img src="renders/' + hero['slug'] +
      '/walk.png"><img src="renders/' + hero['slug'] + '/crouch.png"></details></section>')
  page = '<!doctype html><meta charset="utf-8"><title>Gota equipment models</title>' + \
    '<style>body{margin:32px auto;max-width:1600px;font:18px system-ui;background:#eee;color:#222}' + \
    'img{display:block;width:100%}section{background:white;margin:24px 0;padding:20px}a{color:#245eac}</style>' + \
    '<h1>Gota equipment models</h1><p>Actual runtime GLB renders. Every complete equipment set is below 5,000 triangles. ' + \
    '<a href="equipment.blend">Editable Blender source</a> · <a href="counts.md">Polygon counts</a> · ' + \
    '<a href="judgment.md">Independent visual judgment</a></p>' + \
    '<p>Animation limitation: shared poses rotate staffs horizontally; the Warlock censer overlaps the robe/knee in crouch. ' + \
    'The models follow the existing hand and back sockets; weapon-specific poses are not included.</p>' + \
    '<h2>Reference and revised assets</h2><img src="comparison.png">' + \
    '<h2>Actual viewer lighting</h2><img src="equipment_models.png">' + \
    '<h2>Equipped heroes</h2><img src="model_front.png">' + ''.join(cards)
  (folder / 'index.html').write_text(page)
  print(folder / 'index.html')


if __name__ == '__main__':
  main()
