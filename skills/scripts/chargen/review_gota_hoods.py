"""Compare fitted hoods in front, side and back runtime views."""

import argparse
import os
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
from paths import Source, Preview

Heroes = [('ranger', 'Ranger'), ('crossbowman', 'Crossbowman'),
          ('lich', 'Lich'), ('warlock', 'Warlock')]


def main():
  """Capture actual headgear on the shared head and assemble a fit comparison."""
  parser = argparse.ArgumentParser()
  parser.add_argument('--stage', choices=['before', 'after'], required=True)
  parser.add_argument('--render', action='store_true')
  parser.add_argument('--output', type=Path, default=Source / 'gota/hoods')
  args = parser.parse_args()
  folder = args.output
  logs = Preview / 'gota/hoods'
  logs.mkdir(parents=True, exist_ok=True)
  if args.render:
    for slug, name in Heroes:
      for view, angle in [('front', '0'), ('side', '1.5707963')]:
        output = folder / args.stage / slug / view
        output.mkdir(parents=True, exist_ok=True)
        with (logs / (args.stage+'_'+slug+'_'+view+'.log')).open('w') as log:
          subprocess.run([str(Preview / 'gota/render_gota')], check=True,
            env=dict(os.environ, REVIEW_PRESET=name, REVIEW_HEAD='1', REVIEW_PBR='1',
              REVIEW_ANGLE=angle, REVIEW_OUTPUT=str(output)), stdout=log, stderr=log)
      if args.stage == 'after' and slug != 'ranger':
        output = Source / 'gota' / slug / 'renders'
        with (logs / (slug+'_full.log')).open('w') as log:
          subprocess.run([str(Preview / 'gota/render_gota')], check=True,
            env=dict(os.environ, REVIEW_PRESET=name, REVIEW_HEAD='0', REVIEW_PBR='0',
              REVIEW_ANGLE='0', REVIEW_OUTPUT=str(output)), stdout=log, stderr=log)
      print('Rendered '+args.stage+' '+name, flush=True)
  font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 23)
  small = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 18)
  sheet = Image.new('RGB', (1740, 1480), '#eeeeea')
  draw = ImageDraw.Draw(sheet)
  for group, stage in enumerate(['before', 'after']):
    draw.text((group*870+435, 16), stage.upper(), anchor='mt', font=font, fill='#242424')
    for column, label in enumerate(['Front', 'Side', 'Back']):
      draw.text((group*870+column*290+145, 50), label, anchor='mt', font=small, fill='#444444')
    for row, (slug, name) in enumerate(Heroes):
      if not (folder/stage/slug/'front/model.png').exists():
        continue
      for column, view in enumerate(['front', 'side', 'front']):
        image = Image.open(folder/stage/slug/view/'model.png').convert('RGB')
        offset = 800 if column == 2 else 0
        image = image.crop((offset+100, 230, offset+700, 880))
        image = image.resize((280, 303), Image.Resampling.LANCZOS)
        sheet.paste(image, (group*870+column*290+5, 88+row*345))
      label = name + (' (reference, unchanged)' if slug == 'ranger' else '')
      draw.text((group*870+435, 398+row*345), label, anchor='mt', font=small, fill='#333333')
  sheet.save(folder/'comparison.png')
  if args.stage == 'after':
    concepts = Image.new('RGB', (1440, 1180), '#eeeeea')
    headings = ImageDraw.Draw(concepts)
    for column, label in enumerate(['Original concept', 'Revised front', 'Revised side', 'Revised back']):
      headings.text((column*360+180, 14), label, anchor='mt', font=font, fill='#242424')
    for row, (slug, name) in enumerate(Heroes[1:]):
      reference = {'crossbowman': ('clothing.png', .74),
        'lich': ('clothing_reference.png', .725),
        'warlock': ('clothing_reference_final.png', .77)}[slug]
      image = Image.open(Source/'gota'/slug/reference[0]).convert('RGB')
      image = image.crop((0, int(image.height*reference[1]), image.width//2, image.height))
      image = ImageOps.contain(image, (350, 330))
      concepts.paste(image, ((360-image.width)//2, 58+row*370+(330-image.height)//2))
      for column, view in enumerate(['front', 'side', 'front'], 1):
        image = Image.open(folder/'after'/slug/view/'model.png').convert('RGB')
        offset = 800 if column == 3 else 0
        image = image.crop((offset+100, 230, offset+700, 880))
        image = image.resize((305, 330), Image.Resampling.LANCZOS)
        concepts.paste(image, (column*360+27, 58+row*370))
      headings.text((720, 391+row*370), name, anchor='mt', font=small, fill='#333333')
    concepts.save(folder/'concept_comparison.png')
  (folder/'index.html').write_text('<!doctype html><meta charset="utf-8">'
    '<title>Gota fitted hoods</title><style>body{margin:30px;background:#eee;'
    'font:18px system-ui;color:#222}img{width:100%;max-width:1740px}</style>'
    '<h1>Gota fitted hoods</h1><p>Actual exported meshes in front, side and back views. '
    'Ranger is the unchanged reference. Brown Crossbowman, blue Lich and horned Warlock '
    'retain fitted rounded backs and loose lower corners. The openings follow '
    'their individual concepts: a pointed brown arch, an ivory V beneath '
    'the crystal crown, and a stepped gold border between the ram horns.</p>'
    '<img src="concept_comparison.png"><h2>Before and after</h2><img src="comparison.png">')
  print(folder/'comparison.png')


if __name__ == '__main__':
  main()
