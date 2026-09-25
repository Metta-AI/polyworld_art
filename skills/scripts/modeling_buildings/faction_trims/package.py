import os
import hashlib
import json
import shutil
import struct
import subprocess
from pathlib import Path

Root = Path(__file__).resolve().parent
Output = Path(os.environ['POLYWORLD_BUILDING_PACK']) / 'textures/factions'
Titles = [
  'Peter River · Light blue', 'Amethyst · Black rock',
  'Alizarin · Orc', 'Emerald · Forest',
  'Carrot · Desert', 'Wet Asphalt · Dragon',
  'Turquoise · Greece', 'Sun Flower · Crypt',
]
Tiles = [
  ['stone', 'plaster', 'window', 'gray'],
  ['roof', 'wood', 'gold', 'door'],
  ['pumpkin', 'banner', 'leaf', 'doubleDoor'],
  ['bark', 'soil', 'archWindow', 'archDoor'],
]

def dimensions(path):
  """Read the dimensions of a PNG without changing it."""
  data = path.read_bytes()
  assert data[:8] == b'\x89PNG\r\n\x1a\n', str(path)
  return struct.unpack('>II', data[16:24])

def resizeAtlas(source, target, name):
  """Resample each material cell into its exact 128-pixel UV region."""
  layout = json.loads((Root / 'layout.json').read_text())
  width, height = dimensions(source)
  assert [width, height] == layout['source_size']
  xs, ys = layout['x_boundaries'], layout['y_boundaries']
  inset = layout['inset']
  assert isinstance(inset, int) and inset >= 0
  for boundaries, extent in [(xs, width), (ys, height)]:
    assert len(boundaries) == 5
    assert boundaries[0] == 0 and boundaries[-1] == extent
    assert all(isinstance(value, int) for value in boundaries)
    assert all(b - a > 2 * inset for a, b in zip(boundaries, boundaries[1:]))
  directory = Root / 'cells' / name
  directory.mkdir(parents=True, exist_ok=True)
  cells = []
  for row in range(4):
    for col in range(4):
      x, y = xs[col] + inset, ys[row] + inset
      width = xs[col + 1] - xs[col] - 2 * inset
      height = ys[row + 1] - ys[row] - 2 * inset
      cell = directory / f'{row}-{col}.png'
      subprocess.run(['magick', str(source), '-crop',
        f'{width}x{height}+{x}+{y}', '+repage', '-filter', 'Lanczos',
        '-resize', '128x128!', '-alpha', 'off', str(cell)], check=True)
      cells.append(str(cell))
  subprocess.run(['magick', 'montage', *cells, '-tile', '4x4',
    '-geometry', '128x128+0+0', '-alpha', 'off', 'PNG24:' + str(target)],
    check=True)

def package():
  """Install the eight external atlases and assemble the labeled review sheet."""
  prompts = json.loads((Root / 'prompts.json').read_text())['prompts']
  sources = json.loads((Root / 'sources.json').read_text())
  assert len(prompts) == len(sources) == 8
  Output.mkdir(parents=True, exist_ok=True)
  (Root / 'generated').mkdir(exist_ok=True)
  (Root / 'cards').mkdir(exist_ok=True)
  manifest = {
    'pack': 'lvd_buildings_faction_trims',
    'texture_size': [512, 512],
    'color_space': 'sRGB',
    'layout': {'columns': 4, 'rows': 4, 'tile_size': [128, 128],
      'origin': 'top-left', 'tiles': Tiles},
    'usage': 'External albedo atlas variants with the existing building UV layout. Select the faction texture when loading the building material.',
    'neutral_mine_texture': '../buildings-atlas.png',
    'factions': [],
  }
  cards = []
  flags = []
  for i, prompt in enumerate(prompts):
    labelColor = '#91A6BB' if prompt['file'] == 'wet_asphalt' else prompt['hex']
    source = (Root / sources[prompt['file']]).resolve()
    original = Root / 'generated' / (prompt['file'] + '.png')
    if source != original.resolve():
      shutil.copy2(source, original)
    width, height = dimensions(original)
    assert width == height, (original, width, height)
    target = Output / (prompt['file'] + '.png')
    resizeAtlas(original, target, prompt['file'])
    assert dimensions(target) == (512, 512)
    manifest['factions'].append({
      'faction': prompt['faction'], 'color': prompt['hex'],
      'file': target.name, 'theme': prompt['theme'], 'emblem': prompt['emblem'],
      'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
    })
    card = Root / 'cards' / (prompt['file'] + '.png')
    subprocess.run(['magick', str(target), '-resize', '384x384',
      '-background', '#202326', '-gravity', 'south', '-splice', '0x42',
      '-font', 'Arial', '-pointsize', '19', '-fill', labelColor,
      '-annotate', '+0+12', Titles[i], str(card)], check=True)
    cards.append(str(card))
    flag = Root / 'cards' / (prompt['file'] + '-flag.png')
    subprocess.run(['magick', str(target), '-crop', '128x128+128+256',
      '+repage', '-resize', '192x192', '-background', '#202326',
      '-gravity', 'south', '-splice', '0x34', '-font', 'Arial',
      '-pointsize', '17', '-fill', labelColor, '-annotate', '+0+10',
      Titles[i].split(' · ')[0], str(flag)], check=True)
    flags.append(str(flag))
  (Output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
  subprocess.run(['magick', 'montage', *cards, '-tile', '4x2',
    '-geometry', '+10+10', '-background', '#202326',
    str(Root / 'faction-trims-comparison.png')], check=True)
  subprocess.run(['magick', 'montage', *flags, '-tile', '8x1',
    '-geometry', '+8+8', '-background', '#202326',
    str(Root / 'faction-flags.png')], check=True)
  print(json.dumps({'output': str(Output), 'count': len(prompts),
    'preview': str(Root / 'faction-trims-comparison.png')}, indent=2))

package()
