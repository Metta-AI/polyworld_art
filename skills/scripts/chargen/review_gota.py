"""Compare actual runtime renders and generated references without retouching."""
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
from paths import Source

Order = ['vanguard_knight', 'ranger', 'arcanist', 'druid_warden', 'demon_hunter',
         'death_knight', 'crossbowman', 'lich', 'warlock', 'berserker']


def panel(canvas, path, box, title):
  """Place unaltered image content in a labeled comparison panel."""
  draw = ImageDraw.Draw(canvas)
  font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 28)
  draw.text((box[0]+15, box[1]+10), title, fill='#222222', font=font)
  img = path if isinstance(path, Image.Image) else Image.open(path).convert('RGB')
  img = ImageOps.contain(img, (box[2]-30, box[3]-70))
  canvas.paste(img, (box[0]+(box[2]-img.width)//2,
                     box[1]+60+(box[3]-70-img.height)//2))


def main(slug):
  """Produce explicit side-by-side evidence for the hero's independent judge."""
  output = Source / 'gota' / slug
  index = Order.index(slug)
  roster = Image.open(Source / 'gota/approved_roster.png').convert('RGB')
  w, h = roster.width/5, roster.height/2
  crop = roster.crop((round(index%5*w), round(index//5*h),
                     round((index%5+1)*w), round((index//5+1)*h)))
  references = [output / name for name in ['clothing_reference_final.png',
    'clothing_reference.png', 'clothing.png'] if (output / name).exists()]
  if not references:
    raise ValueError('Missing clothing reference for ' + slug)
  reference = references[0]
  render = output / 'renders'
  sheet = Image.new('RGB', (2400, 1400), '#efeeeb')
  panel(sheet, crop, (0, 0, 450, 1400), 'Approved hero')
  panel(sheet, reference, (450, 0, 850, 1400), 'Generated clothing reference')
  panel(sheet, render/'model.png', (1300, 0, 1100, 1400), 'Actual runtime model: front / back')
  sheet.save(output/'comparison.png')
  items = Image.new('RGB', (1000, 2500), '#efeeeb')
  for i, slot in enumerate(['Foot', 'Leg', 'Belt', 'Chest', 'Headgear']):
    panel(items, render/(slot+'.png'), (0, i*500, 1000, 500), slot+' : front / back')
  items.save(output/'modeled_items.png')
  comparison = Image.new('RGB', (2000, 2500), '#efeeeb')
  panel(comparison, reference, (0,0,1000,2500), 'Generated clothing reference')
  panel(comparison, items, (1000,0,1000,2500), 'Actual separate exported items')
  comparison.save(output/'items_comparison.png')
  (output/'review.html').write_text('<!doctype html><meta charset="utf-8">'
    '<title>'+slug+' model review</title><style>body{background:#eee;font:18px sans-serif;}'
    'img{max-width:100%;display:block;margin:20px auto}</style><h1>'+slug.replace('_',' ')+
    '</h1><img src="comparison.png"><img src="items_comparison.png">'
    '<h2>Animation checks</h2><img src="renders/walk.png"><img src="renders/crouch.png">')
  print(output/'comparison.png')


if __name__ == '__main__':
  main(sys.argv[1])
