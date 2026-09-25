"""Register Gota heroes and creeps without replacing other preset groups."""
import json
from pathlib import Path
from paths import Library, Source

Order = ['vanguard_knight','ranger','arcanist','druid_warden','demon_hunter',
         'death_knight','crossbowman','lich','warlock','berserker']
Extras = ['blue_creep','purple_creep']
Gods = ['zeus','hades']


def write(path,data):
  """Persist a readable manifest or palette."""
  path.write_text(json.dumps(data,indent=2)+'\n')


def main():
  """Merge Gota entries and exact skin colors into the runtime inventory."""
  runtime=json.loads((Library/'manifest.json').read_text())
  authoring=json.loads((Source/'manifest.json').read_text())
  skins=json.loads((Library/runtime['skinPalette']).read_text())
  equipmentPath=Source/'gota/weapons/parts.json'
  equipment=json.loads(equipmentPath.read_text()) if equipmentPath.exists() else []
  presets=[]
  for slug in Order + Extras + Gods:
    folder=Source/'gota'/slug
    preset=json.loads((folder/'preset.json').read_text())
    weapons=[part for part in equipment if part['slug']==slug]
    for part in weapons:
      for choice in preset['parts']:
        if choice['category']==part['category']:
          choice['item']=part['name']
    if 'skinRgb' in preset:
      name='Gota '+preset['name']
      entry=next((i for i,item in enumerate(skins) if item['name']==name),None)
      if entry is None:
        entry=len(skins)
        skins.append(dict(name=name,color=preset['skinRgb']+[1]))
      else:
        skins[entry]['color']=preset['skinRgb']+[1]
      preset['skin']=entry
    presets.append(preset)
    if slug in Extras:
      continue
    metadata=json.loads((folder/'parts.json').read_text())+weapons
    for part in metadata:
      category=next(c for c in authoring['categories'] if c['key']==part['category'])
      category['items']=[item for item in category['items']
        if item['name']!=part['name'] and item.get('id')!=part['id']]
      category['items'].append({k:v for k,v in part.items()
        if k not in ['category','slug']})
  body=json.loads((Library/'body/gota_base.json').read_text())
  category=next(c for c in authoring['categories'] if c['key']=='Body')
  category['items']=[item for item in category['items'] if item['name']!='Gota base']+[body]
  for manifest in [runtime,authoring]:
    manifest['presets']=[p for p in manifest['presets']
      if p.get('group') not in ['Gota', 'Gota Gods']]+presets
  authoring['skins']=skins
  write(Library/runtime['skinPalette'],skins)
  write(Library/'manifest.json',runtime)
  write(Source/'manifest.json',authoring)
  print('Registered ten Gota heroes, two creeps and two gods; '
        'other presets preserved.')


if __name__=='__main__':main()
