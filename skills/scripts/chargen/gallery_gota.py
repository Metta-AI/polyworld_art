"""Publish local comparison pages and collate unretouched runtime captures."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from paths import Source
from register_gota import Order


def main():
  """Assemble front/back contact sheets and links to each independent review."""
  folder=Source/'gota'
  audit=json.loads((folder/'audit.json').read_text())
  font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',25)
  for side in ['front','back']:
    sheet=Image.new('RGB',(2000,1220),'#b8b6b0')
    draw=ImageDraw.Draw(sheet)
    for i,slug in enumerate(Order):
      image=Image.open(folder/slug/'renders/model.png').convert('RGB')
      half=image.width//2
      crop=image.crop((0 if side=='front' else half,0,
                       half if side=='front' else image.width,image.height))
      crop.thumbnail((400,550))
      x,y=(i%5)*400,(i//5)*610
      sheet.paste(crop,(x+(400-crop.width)//2,y))
      label=audit[i]['name']
      bounds=draw.textbbox((0,0),label,font=font)
      draw.text((x+(400-bounds[2])/2,y+552),label,fill='#222222',font=font)
      count=str(audit[i]['triangles'])+' triangles'
      bounds=draw.textbbox((0,0),count,font=font)
      draw.text((x+(400-bounds[2])/2,y+581),count,fill='#444444',font=font)
    sheet.save(folder/('lineup_'+side+'.png'))
  cards=[]
  for entry in audit:
    slug=entry['slug']
    prompts=sorted((folder/slug).glob('*prompt*'))
    promptLink=''.join(' · <a href="'+slug+'/'+path.name+'">'+path.name+'</a>'
                       for path in prompts)
    verdicts=[folder/slug/name for name in ['final_judgment.md','judgment.md',
      'judge_model.md','judge.md'] if (folder/slug/name).exists()]
    judgeLink=(' · <a href="'+slug+'/'+verdicts[0].name+'">Independent judge</a>'
               if verdicts else '')
    cards.append('<article><h2>'+entry['name']+'</h2><p>'+format(entry['triangles'],',')+
      ' triangles · five separate clothing slots</p><a href="'+slug+'/review.html">'
      '<img src="'+slug+'/comparison.png"></a><p><a href="'+slug+'/review.html">'
      'Open full front/back and animation review</a> · <a href="'+slug+'/hero.blend">'
      'Blender source</a>'+judgeLink+promptLink+'</p></article>')
  (folder/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Gota heroes</title>'
    '<style>body{margin:32px auto;max-width:1600px;font:18px system-ui;background:#eee;color:#222}'
    'img{width:100%;display:block}article{background:#fff;padding:24px;margin:24px 0}'
    'a{color:#245eac}h1{font-size:36px}</style><h1>Gota character library</h1>'
    '<p>Ten actual rigged Polyworld characters. Each outfit has separate boots, legs, belt, body and hat. '
    'Solid-color clothing, reused facial parts, no props. All models are below 20,000 triangles.</p>'
    '<img src="lineup_front.png"><img src="lineup_back.png">'+''.join(cards))
  print(folder/'index.html')


if __name__=='__main__':main()
