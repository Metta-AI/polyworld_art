import os
import base64
import json
import struct
import subprocess
from pathlib import Path

Root = Path(__file__).resolve().parent
Pack = Path(os.environ['POLYWORLD_BUILDING_PACK'])
Factions = json.loads((Pack / 'textures/factions/manifest.json').read_text())['factions']
Models = json.loads((Pack / 'manifest.json').read_text())['models']
Names = ['Town Hall', 'Farm', 'Barracks', 'Lumber Mill', 'Tower',
  'Stables / Kennels', 'Church / Temple', 'Blacksmith', 'Gold Mine']
FactionNames = ['Peter River', 'Amethyst', 'Alizarin', 'Emerald', 'Carrot',
  'Wet Asphalt', 'Turquoise', 'Sun Flower']
Themes = ['Light blue', 'Black rock', 'Orc', 'Forest', 'Desert', 'Dragon', 'Greece', 'Crypt']
Background = '#202326'
Ink = '#EDF0F2'

def run(args):
  """Run deterministic image layout commands without a shell."""
  subprocess.run(['magick', *map(str, args)], check=True)

def source(faction, model):
  """Use the one neutral mine image in every faction review."""
  slug = 'neutral' if model['name'] == 'gold_mine' else Path(faction['file']).stem
  return Root / 'renders' / slug / (model['name'] + '.png')

def titled(inputPath, outputPath, title, color=Ink):
  """Add a readable sheet heading without changing the rendered images."""
  run([inputPath, '-background', Background, '-gravity', 'north', '-splice', '0x82',
    '-font', 'Arial', '-pointsize', '34', '-fill', color, '-annotate', '+0+24', title, outputPath])

for directory in ['cards', 'factions', 'buildings', 'matrix', 'thumbs']:
  (Root / directory).mkdir(exist_ok=True)
records = json.loads((Root / 'render-manifest.json').read_text())
assert len(records) == 65
for record in records:
  imagePath = Root / record['render']
  assert struct.unpack('>II', imagePath.read_bytes()[16:24]) == (800, 800)

for fi, faction in enumerate(Factions):
  slug = Path(faction['file']).stem
  cards = []
  for mi, model in enumerate(Models):
    card = Root / 'cards' / (slug + '-' + model['name'] + '.png')
    label = Names[mi] + (' · Neutral' if model['name'] == 'gold_mine' else '')
    run([source(faction, model), '-resize', '720x720', '-background', Background,
      '-gravity', 'south', '-splice', '0x42', '-font', 'Arial', '-pointsize', '23',
      '-fill', Ink, '-annotate', '+0+12', label, card])
    cards.append(card)
  sheet = Root / 'factions' / (slug + '.png')
  run(['montage', *cards, '-tile', '3x3', '-geometry', '+10+10', '-background', Background, sheet])
  color = '#91A6BB' if slug == 'wet_asphalt' else faction['color']
  titled(sheet, sheet, FactionNames[fi] + ' · ' + Themes[fi], color)

for mi, model in enumerate(Models):
  if model['name'] == 'gold_mine':
    titled(Root / 'renders/neutral/gold_mine.png', Root / 'buildings/gold_mine.png', 'Gold Mine · Neutral')
    continue
  cards = []
  for fi, faction in enumerate(Factions):
    slug = Path(faction['file']).stem
    card = Root / 'cards' / (model['name'] + '-' + slug + '.png')
    color = '#91A6BB' if slug == 'wet_asphalt' else faction['color']
    run([source(faction, model), '-resize', '600x600', '-background', Background,
      '-gravity', 'south', '-splice', '0x42', '-font', 'Arial', '-pointsize', '23',
      '-fill', color, '-annotate', '+0+12', FactionNames[fi], card])
    cards.append(card)
  sheet = Root / 'buildings' / (model['name'] + '.png')
  run(['montage', *cards, '-tile', '4x2', '-geometry', '+10+10', '-background', Background, sheet])
  titled(sheet, sheet, Names[mi] + ' · Eight factions')

headers = []
corner = Root / 'matrix/corner.png'
run(['-size', '160x80', 'xc:' + Background, corner])
headers.append(corner)
for fi, faction in enumerate(Factions):
  path = Root / 'matrix' / ('header-' + str(fi) + '.png')
  color = '#91A6BB' if fi == 5 else faction['color']
  run(['-size', '256x80', 'xc:' + Background, '-font', 'Arial', '-gravity', 'center',
    '-fill', color, '-pointsize', '21', '-annotate', '+0+0', FactionNames[fi] + '\n' + Themes[fi], path])
  headers.append(path)
header = Root / 'matrix/header.png'
run([*headers, '+append', header])
rows = [header]
for mi, model in enumerate(Models):
  label = Root / 'matrix' / ('label-' + str(mi) + '.png')
  text = Names[mi].replace(' / ', '\n').replace(' ', '\n', 1)
  run(['-size', '160x256', 'xc:' + Background, '-font', 'Arial', '-gravity', 'center',
    '-fill', Ink, '-pointsize', '23', '-annotate', '+0+0', text, label])
  cells = [label]
  for fi, faction in enumerate(Factions):
    cell = Root / 'matrix' / f'cell-{mi}-{fi}.png'
    run([source(faction, model), '-resize', '256x256', cell])
    cells.append(cell)
  row = Root / 'matrix' / ('row-' + str(mi) + '.png')
  run([*cells, '+append', row])
  rows.append(row)
run([*rows, '-append', Root / 'all-buildings-all-factions.png'])

data = {'factions': [{'id': Path(faction['file']).stem, 'name': FactionNames[i], 'theme': Themes[i]}
  for i, faction in enumerate(Factions)],
  'buildings': [{'id': model['name'], 'name': Names[i]} for i, model in enumerate(Models)]}
template = (Root / 'gallery-template.html').read_text()
for size, quality in [(352, 72), (320, 68), (288, 64), (256, 60)]:
  images = {}
  for record in records:
    path = Root / record['render']
    raw = subprocess.check_output(['magick', str(path), '-resize', f'{size}x{size}',
      '-strip', '-sampling-factor', '4:2:0', '-quality', str(quality), 'jpeg:-'])
    key = '/'.join(Path(record['render']).with_suffix('').parts[-2:])
    images[key] = 'data:image/jpeg;base64,' + base64.b64encode(raw).decode()
  data['images'] = images
  data['thumbnailSize'] = size
  fragment = template.replace('/* RENDER_DATA */ {}', json.dumps(data, separators=(',', ':')))
  if len(fragment.encode()) < 975000:
    break
assert len(fragment.encode()) < 1000000
(Root / 'faction-building-gallery.html').write_text(fragment)
(Root / 'sheet-manifest.json').write_text(json.dumps({
  'unique_renders': 65, 'faction_sheets': 8, 'building_sheets': 9,
  'overview': 'all-buildings-all-factions.png', 'gallery': 'faction-building-gallery.html',
  'gallery_bytes': len(fragment.encode()), 'thumbnail_size': size,
  'neutral_mine_shared': True, 'camera_scale': 11.4}, indent=2) + '\n')
print('Created eight faction sheets, nine building sheets, the full matrix, and gallery.', flush=True)
