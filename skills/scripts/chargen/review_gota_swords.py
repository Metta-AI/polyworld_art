"""Capture actual creep sword grips and attack poses from three directions."""

import os
import subprocess

from PIL import Image, ImageDraw, ImageFont
from paths import Project, Source

Output = Source / 'gota/swords'
Renderer = Project / 'tmp/chargen/render_swords'
Font = '/System/Library/Fonts/Supplemental/Arial.ttf'
Frames = [(12, 'Wind-up'), (15, 'Earlier pose'), (18, 'Previous frame'),
          (19, 'Strike'), (20, 'Next frame'), (24, 'Follow-through')]


def label(source, title):
  """Add view and character labels outside unaltered runtime captures."""
  raw = Image.open(source).convert('RGB')
  sheet = Image.new('RGB', (1800, 1350), '#efeeeb')
  sheet.paste(raw.crop((0, 0, 1800, 600)), (0, 120))
  sheet.paste(raw.crop((0, 600, 1800, 1200)), (0, 750))
  draw = ImageDraw.Draw(sheet)
  font = ImageFont.truetype(Font, 25)
  draw.text((20, 10), title, font=font, fill='#222222')
  for column, view in enumerate(['Front', 'Side', 'Top']):
    draw.text((column*600+250, 50), view, font=font, fill='#222222')
  draw.text((20, 85), 'Blue Creep / Vanguard sword', font=font, fill='#222222')
  draw.text((20, 720), 'Purple Creep / Death Knight sword',
            font=font, fill='#222222')
  return sheet


def main():
  """Regenerate the comparison from the equipped, skinned runtime models."""
  Output.mkdir(parents=True, exist_ok=True)
  for stage, close in [('before', '0'), ('after', '0'), ('grip', '1')]:
    environment = dict(os.environ, REVIEW_OUTPUT=str(Output/stage),
      REVIEW_TIMES=','.join(f'{frame/30:.9f}' for frame, _ in Frames),
      REVIEW_ORIGINAL='0', REVIEW_GRIP=close)
    environment.pop('REVIEW_ROTATION', None)
    if stage == 'before':
      environment['REVIEW_ROTATION'] = '18,22,-28'
    subprocess.run([str(Renderer)], cwd=Project, env=environment, check=True)
  for frame, name in Frames:
    time = f'{frame/30:.3f}'
    label(Output/'after'/f'attack_{time}.png',
      f'{name} / Sword_Attack frame {frame} / {time}s').save(
        Output/(name.lower()+'.png'))
  label(Output/'grip/attack_0.633.png',
    'Grip close-up / Sword_Attack frame 19').save(Output/'grip.png')
  comparison = Image.new('RGB', (1800, 2700), '#efeeeb')
  for row, stage in enumerate(['before', 'after']):
    comparison.paste(label(Output/stage/'attack_0.633.png',
      f'{stage.title()} socket rotation / Sword_Attack frame 19 / 0.633s'),
      (0, row*1350))
  comparison.save(Output/'comparison.png')
  sections = ''.join(f'<h2>{name}</h2><img src="{file}">' for name, file in [
    ('Frame 19: front, side, top', 'strike.png'),
    ('Previous frame: 18', 'previous frame.png'),
    ('Next frame: 20', 'next frame.png'),
    ('Earlier pose: 15', 'earlier pose.png'),
    ('Grip seating', 'grip.png'), ('Wind-up', 'wind-up.png'),
    ('Follow-through', 'follow-through.png'), ('Before and after', 'comparison.png')])
  (Output/'index.html').write_text('<!doctype html><meta charset="utf-8">'
    '<title>Creep sword alignment</title><style>body{margin:32px;background:#efeeeb;'
    'color:#222;font:18px sans-serif}img{max-width:100%;display:block}</style>'
    '<h1>Creep sword alignment</h1><p>Actual viewer meshes, frozen at identical '
    'animation times. Rotation offset: X 55.4°, Y -22.7°, Z 72.6°, about the grip. '
    'At frame 19 the blade continues along the elbow-to-grip direction '
    'marked in the review screenshot. The source geometry and animation '
    'are unchanged.</p>'+sections)
  print(Output/'strike.png')


if __name__ == '__main__':
  main()
