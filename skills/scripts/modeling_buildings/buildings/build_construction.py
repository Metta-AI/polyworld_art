import os
import hashlib
import json
import math
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector

Root = Path(__file__).resolve().parent
Source = Root/'polyworld-buildings.blend'
SourceHash = hashlib.sha256(Source.read_bytes()).hexdigest()
# Reuse the kit's geometry and UV helpers without running its scene reset.
helperSource = (Root/'build_scene.py').read_text().split(
  'bpy.ops.wm.read_factory_settings(use_empty=True)')[0]
exec(compile(helperSource, str(Root/'build_scene.py'), 'exec'), globals())
Atlas = bpy.data.materials['Approved painted building atlas']
Ground = bpy.data.materials['Warm off-white stage']
Grid = bpy.data.materials['Pale grid']
Ink = bpy.data.materials['Slate lettering']
World = bpy.data.worlds['Neutral studio environment']
Names = ['town_hall','farm','barracks','lumber_mill','tower',
  'stables','church','blacksmith']
Labels = ['Town Hall','Farm','Barracks','Lumber Mill','Tower',
  'Stables / Kennels','Church / Temple','Blacksmith']
Originals = ['01 Town Hall','02 Farm','03 Barracks','04 Lumber Mill',
  '05 Tower','06 Stables and Kennels','07 Church and Temple','08 Blacksmith']
Modules = []
Foundations, Walls = [], []

def copyPart(source, group=None, name=None):
  """Share original mesh data and preserve live modifiers and placements."""
  source = bpy.data.objects[source] if isinstance(source,str) else source
  obj = source.copy()
  obj.name = name or 'Construction - '+source.name
  (group or Current).objects.link(obj)
  return obj

def copyMatching(groupName, prefixes):
  """Reuse only explicitly selected structural parts of a source."""
  return [copyPart(obj) for obj in bpy.data.collections[groupName].objects
    if any(obj.name.startswith(prefix) for prefix in prefixes)]

def shell(name, width, depth, bottom, eave, rise=0, tile='plaster',
  front=(), back=(), sides=(), thickness=.14, center=(0,0), mirrored=True):
  """Build connected open-top walls with real rectangular openings."""
  vertices, faces = [], []
  def face(points):
    start = len(vertices)
    vertices.extend(points)
    faces.append(tuple(range(start,start+len(points))))
  def wall(length, y, angle, holes, gable):
    xs = sorted(set([-length/2,length/2]+[v for h in holes for v in h[:2]]))
    zs = sorted(set([bottom,eave]+[max(bottom,min(eave,v))
      for h in holes for v in h[2:]]))
    def point(x,z):
      return (center[0]+x*math.cos(angle)-y*math.sin(angle),
        center[1]+x*math.sin(angle)+y*math.cos(angle),z)
    for x0,x1 in zip(xs,xs[1:]):
      for z0,z1 in zip(zs,zs[1:]):
        x,z = (x0+x1)/2,(z0+z1)/2
        if any(a < x < b and c < z < d for a,b,c,d in holes):
          continue
        face([point(x0,z0),point(x1,z0),point(x1,z1),point(x0,z1)])
    if gable:
      face([point(-length/2,eave),point(length/2,eave),point(0,eave+rise)])
  wall(width,-depth/2,0,front,rise > 0)
  wall(width,-depth/2,Pi,back,rise > 0)
  wall(depth,-width/2,Pi/2,sides,False)
  wall(depth,-width/2,-Pi/2,sides,False)
  obj = meshObject(name,vertices,faces,tile)
  # Weld coplanar edges before thickness so corners have continuous interiors.
  data = bmesh.new()
  data.from_mesh(obj.data)
  bmesh.ops.remove_doubles(data,verts=list(data.verts),dist=.00001)
  data.to_mesh(obj.data)
  data.free()
  if mirrored:
    mirror(obj)
  solid = obj.modifiers.new('Real wall thickness, open roof','SOLIDIFY')
  solid.thickness = thickness
  solid.offset = -1
  solid.use_even_offset = True
  bevel(obj,.018)
  obj['construction_shell'] = True
  obj['wall_thickness'] = thickness
  return obj

def ring(name, profile, thickness, offset, tile='stone'):
  """Model a hollow sixth of a tower with matching inner wall rings."""
  vertices, faces = [], []
  for z,radius in profile:
    inner = radius-thickness
    vertices.extend([(-radius*.5,-radius*.8660254,z),
      (radius*.5,-radius*.8660254,z),
      (inner*.5,-inner*.8660254,z),(-inner*.5,-inner*.8660254,z)])
  for i in range(len(profile)-1):
    a,b = i*4,(i+1)*4
    faces.extend([(a,a+1,b+1,b),(a+2,a+3,b+3,b+2),
      (a+3,a,b,b+3),(a+1,a+2,b+2,b+1)])
  faces.extend([(3,2,1,0),tuple(range(len(vertices)-4,len(vertices)))])
  obj = meshObject(name,vertices,faces,tile)
  mirror(obj)
  radial(obj,offset)
  bevel(obj,.012)
  obj['construction_shell'] = True
  return obj

def setVariant(index, stage):
  """Create one asset collection with explicit stage metadata."""
  group = useCollection(f'CONSTRUCTION - {Names[index]} - {stage}')
  group['building'] = Names[index]
  group['stage'] = stage
  group.asset_mark()
  return group

def foundationInstance(index):
  """Reuse the exact foundation within the second construction stage."""
  return instance('Shared foundation - '+Names[index],Foundations[index])

def footprintSlab(name,outline,height):
  """Make a seamless asymmetric footing with a planar mapped stone top."""
  count = len(outline)
  vertices = [(x,y,z) for z in (0,height) for x,y in outline]
  faces = [tuple(reversed(range(count))),tuple(range(count,count*2))]
  faces.extend((i,(i+1)%count,(i+1)%count+count,i+count)
    for i in range(count))
  lowX,highX = min(p[0] for p in outline),max(p[0] for p in outline)
  lowY,highY = min(p[1] for p in outline),max(p[1] for p in outline)
  cap = [((x-lowX)/(highX-lowX),(y-lowY)/(highY-lowY)) for x,y in outline]
  uvs = [list(reversed(cap)),cap]+[[(0,0),(1,0),(1,1),(0,1)]]*count
  return bevel(meshObject(name,vertices,faces,'stone',uvs),.025)

def buildFoundations():
  """Derive structural bases at their finished-model coordinates."""
  global Current
  wing = useCollection('CONSTRUCTION MODULE - Wing foundation')
  copyPart('Wing mirrored foundation')
  Modules.append(wing)
  for i in range(8):
    group = setVariant(i,'foundation')
    if i == 0:
      copyPart('Hall central mirrored foundation')
      for source in bpy.data.collections[Originals[i]].objects:
        if source.instance_type == 'COLLECTION':
          obj = copyPart(source)
          obj.instance_collection = wing
      copyMatching(Originals[i],['Hall entrance Step'])
    elif i == 1:
      copyPart('Farm soil bed')
    elif i == 2:
      copyPart('Barracks mirrored stone footing')
      copyMatching(Originals[i],['Barracks approach Step'])
    elif i == 3:
      copyPart('Mill mirrored slab')
    elif i == 4:
      controller = bpy.data.objects.new('Foundation sixfold controller',None)
      group.objects.link(controller)
      controller.rotation_euler.z = Pi/3
      base = hexProfile('Construction tower base',[(.05,1.2),(.2,1.24),(.42,1.18)],
        'stone',controller)
      data = bmesh.new()
      data.from_mesh(base.data)
      top = [face for face in data.faces if all(abs(v.co.z-.42)<.0001
        for v in face.verts)]
      bmesh.ops.delete(data,geom=top,context='FACES_ONLY')
      data.to_mesh(base.data)
      data.free()
      radius = 1.18
      vertices = [(radius*math.cos(i*Pi/3),radius*math.sin(i*Pi/3),.42)
        for i in range(6)]
      uvs = [[((x/radius+1)/2,(y/radius+1)/2) for x,y,z in vertices]]
      lid = meshObject('Tower planar stone foundation top',vertices,
        [tuple(range(6))],'stone',uvs)
      mirror(lid)
      controller.hide_render = True
    elif i == 5:
      copyPart('Stable mirrored foundation')
    elif i == 6:
      footprintSlab('Chapel and belfry continuous footing',[
        (-1.065,-1.55),(1.065,-1.55),(1.065,-1.36),
        (1.605,-1.36),(1.605,-.34),(1.065,-.34),
        (1.065,1.55),(-1.065,1.55)],.4)
      copyMatching(Originals[i],['Chapel front steps Step'])
    elif i == 7:
      copyPart('Smith mirrored footing')
      box('Smith porch footing',(0,-1.54,.12),(2.49,.74,.24),
        'stone',mirrored=True)
      copyPart('Smith hearth base')
    Foundations.append(group)

def buildHall():
  """Keep three mirrored wings around an open central tower."""
  global Current
  group = Current
  wingModules = []
  for entry in (False,True):
    wing = useCollection('CONSTRUCTION MODULE - '+('Entry' if entry else 'Side')+
      ' wing walls')
    front = [(-.415,.415,.34,1.57)] if entry else [(-.315,.315,.645,1.355)]
    shell('Wing open gabled shell',1.55,2.35,.34,1.65,1.05,
      front=front,back=[(-.63,.63,.34,1.61)],
      sides=[(-.915,-.325,.685,1.375),(.225,.815,.685,1.375)])
    copyMatching('MODULE - Town hall mirrored wing',['Wing framing'])
    wingModules.append(wing)
    Modules.append(wing)
  Current = group
  shell('Hall open central shell',1.63,1.68,.40,3.38,center=(0,.06),
    front=[(-.59,.59,.40,1.57)],
    sides=[(-.65,.65,.40,1.61),(-.28,.30,2.505,3.155)])
  copyMatching('01 Town Hall',['Hall central corner beam','Hall entrance lintel'])
  for y in (-.83,.95):
    box('Hall open crown crossbeam',(0,y,3.39),(1.85,.14,.2),'wood',mirrored=True)
  for x in (-.855,.855):
    box('Hall open crown side beam',(x,.06,3.39),(.14,1.64,.2),'wood')
  for source in bpy.data.collections['01 Town Hall'].objects:
    if source.instance_type == 'COLLECTION':
      obj = copyPart(source)
      obj.instance_collection = wingModules[int('entry' in source.name)]

def buildTower():
  """Make a sixfold hollow masonry tower with an open windowed lookout."""
  group = Current
  offset = bpy.data.objects.new('Construction tower sixfold controller',None)
  group.objects.link(offset)
  offset.rotation_euler.z = Pi/3
  offset.hide_render = True
  ring('Tower hollow masonry',[(.42,1.18),(.64,1.12),(1.03,.91),
    (2.89,.83),(3.08,1.04)],.21,offset)
  ring('Tower plain masonry collar',[(2.94,1.06),(3.13,1.06)],.23,offset)
  ring('Tower open parapet walkway',[(3.13,1.10),(3.31,1.10)],.60,offset)
  for name in ('Tower buttress sector','Tower crenellation sector'):
    obj = copyPart(name)
    for modifier in obj.modifiers:
      if modifier.type == 'ARRAY':
        modifier.offset_object = offset
  # A flat sixth of the lookout retains actual window openings.
  y = -.65*.8660254
  vertices,faces = [],[]
  for x0,x1,z0,z1 in [(-.325,-.185,3.30,4.0),(.185,.325,3.30,4.0),
    (-.185,.185,3.30,3.405),(-.185,.185,3.92,4.0)]:
    start = len(vertices)
    vertices.extend([(x0,y,z0),(x1,y,z0),(x1,y,z1),(x0,y,z1)])
    faces.append(tuple(range(start,start+4)))
  obj = meshObject('Tower open lookout window sector',vertices,faces,'plaster')
  mirror(obj)
  radial(obj,offset)
  solid = obj.modifiers.new('Lookout wall thickness','SOLIDIFY')
  solid.thickness = .12
  solid.offset = -1
  bevel(obj,.01)
  obj['construction_shell'] = True

def buildChurch():
  """Make an open nave and hollow mirrored belfry at the existing scale."""
  global Current
  group = Current
  shell('Chapel open nave',1.95,2.95,.4,1.96,1.37,
    front=[(-.45,.45,.4,1.715)],
    sides=[(-.985,-.475,.805,1.755),(.235,.745,.805,1.755)])
  belfry = useCollection('CONSTRUCTION MODULE - Open chapel belfry')
  shell('Belfry open shaft',1.01,1.02,.32,2.86,tile='stone',thickness=.16)
  for label,height,width,depth in [('Lower ledge',2.80,1.17,1.18),
    ('Arcade crown',3.63,1.09,1.09)]:
    for y in (-depth/2+.08,depth/2-.08):
      box('Belfry '+label+' crossbeam',(0,y,height),(width,.16,.16),
        'stone',mirrored=True)
    for x in (-width/2+.08,width/2-.08):
      box('Belfry '+label+' side beam',(x,0,height),(.16,depth-.32,.16),'stone')
  copyMatching('MODULE - Chapel belfry',['Belfry open arcade pier','Belfry arch spring'])
  Modules.append(belfry)
  Current = group
  obj = copyPart('Attached chapel belfry')
  obj.instance_collection = belfry

def buildSmith():
  """Keep an unlit masonry forge and hollow chimney with open workshop walls."""
  shell('Smith open workshop',2.32,2.19,.32,1.73,1.02,
    front=[(-.98,-.38,.32,1.42)],sides=[(-.06,.56,.72,1.44)],
    mirrored=False)
  copyMatching('08 Blacksmith',['Smith workshop framing','Smith porch posts',
    'Smith porch header','Smith hearth side'])
  shell('Smith hollow chimney',.69,.65,1.38,3.435,tile='gray',
    thickness=.14,center=(.33,-.75),mirrored=False)
  for y in (-1.08,-.42):
    box('Smith chimney rim',(.33,y,3.42),(.84,.14,.19),'gray')
  for x in (-.02,.68):
    box('Smith chimney rim',(x,-.75,3.42),(.14,.52,.19),'gray')

def buildWalls():
  """Build hollow structural stages without roofs, cloth, crops or machinery."""
  for i in range(8):
    group = setVariant(i,'walls')
    foundationInstance(i)
    if i == 0:
      buildHall()
    elif i == 1:
      for source in bpy.data.collections['02 Farm'].objects:
        if source.name.startswith('Farm fence '):
          copyPart(source)
    elif i == 2:
      shell('Barracks open hall',3.15,2.35,.48,2.12,1.4,
        front=[(-.715,.715,.48,1.915)],
        sides=[(-.85,-.25,.945,1.735),(.28,.88,.945,1.735)])
      copyMatching(Originals[i],['Barracks framing','Barracks stone doorway pier'])
    elif i == 3:
      copyMatching(Originals[i],['Mill mirrored corner','Mill mirrored crossbeam',
        'Mill rear half wall'])
    elif i == 4:
      buildTower()
    elif i == 5:
      copyMatching(Originals[i],['Stable back wall','Stable bay timber post',
        'Stable stall divider','Stable front header','Stable right end gable base',
        'Stable paddock posts','Stable paddock side','Stable paddock front'])
    elif i == 6:
      buildChurch()
    elif i == 7:
      buildSmith()
    Walls.append(group)

def constructionStage(groups,stageName,title):
  """Display eight linked construction assets on a matching 3x3 review sheet."""
  global Current
  scene = bpy.data.scenes.new('CONSTRUCTION STAGE - '+stageName)
  bpy.context.window.scene = scene
  group = useCollection('CONSTRUCTION DISPLAY - '+stageName)
  scene.collection.children.link(group)
  elevation = math.radians(43)
  sine,cosine = math.sin(elevation),math.cos(elevation)
  spacing = 7.2
  scales = [1,1.12,1.15,1.14,1.06,1.09,1.06,1.13]
  heights = [.4,.17,.48,.26,.42,.30,.40,.61] if stageName == 'Foundation' else [
    3.49,.95,3.59,2.05,4.0,1.92,4.64,3.52]
  for i,source in enumerate(groups):
    projected = (1-i//3)*spacing-heights[i]*scales[i]*cosine*.47
    if stageName == 'Walls':
      projected += .55
    obj = instance('Construction preview - '+Names[i],source,
      ((i%3-1)*spacing,projected/sine,0),-Pi/6,scales[i])
    obj['stage_cell'] = f'{i//3+1},{i%3+1}'
  box('Construction studio ground',(0,0,-.18),(70,70,.25),
    material=Ground,edge=0)
  cam = camera('Construction '+stageName+' camera',group,
    (0,-65*cosine,65*sine),(0,0,0),22.1)
  scene.camera = cam
  areaLight('Construction '+stageName+' key',group,(-15,-20,35),6200,18)
  areaLight('Construction '+stageName+' fill',group,(18,-10,24),2200,16)
  sunData = bpy.data.lights.new('Construction '+stageName+' sun','SUN')
  sunData.energy = 1.15
  sunData.angle = .18
  sun = bpy.data.objects.new(sunData.name,sunData)
  group.objects.link(sun)
  sun.rotation_euler = (.4,-.55,-.4)
  overlay = collection('CONSTRUCTION LABELS - '+stageName)
  scene.collection.children.link(overlay)
  right,up,toward = Vector((1,0,0)),Vector((0,sine,cosine)),Vector((0,-cosine,sine))
  plane = toward*25
  for value in (-3.6,3.6):
    for vertical in (True,False):
      points = [(value-.025,-10.9),(value+.025,-10.9),
        (value+.025,10.9),(value-.025,10.9)] if vertical else [
        (-10.9,value-.025),(10.9,value-.025),(10.9,value+.025),(-10.9,value+.025)]
      obj = meshObject('Construction grid',
        [tuple(plane+right*x+up*y) for x,y in points],[(0,1,2,3)],
        material=Grid,group=overlay)
      obj.visible_shadow = obj.visible_diffuse = obj.visible_glossy = False
  textEntries = [(label,(i%3-1)*spacing,(1-i//3)*spacing-3.06,.36)
    for i,label in enumerate(Labels)]
  textEntries.extend([(title,7.2,-6.65,.46),
    ('8 BUILDING VARIANTS',7.2,-7.55,.24),
    ('Gold mine unchanged',7.2,-8.15,.25)])
  for label,x,y,size in textEntries:
    data = bpy.data.curves.new(label,'FONT')
    data.body = label
    data.align_x = data.align_y = 'CENTER'
    data.size = size
    data.materials.append(Ink)
    obj = bpy.data.objects.new(label,data)
    overlay.objects.link(obj)
    obj.location = plane+right*x+up*y
    obj.rotation_euler = cam.rotation_euler
    obj.visible_shadow = obj.visible_diffuse = obj.visible_glossy = False
  settings(scene,2000,40)
  return scene

buildFoundations()
buildWalls()
makeAssetScenes(Foundations+Walls+Modules)
foundationStage = constructionStage(Foundations,'Foundation','FOUNDATIONS')
wallStage = constructionStage(Walls,'Walls','FOUNDATIONS + WALLS')
report = {'source_unchanged':True,'foundation_count':8,'wall_count':8,
  'mine_variants':0,'variants':[]}
for stage,groups in [('foundation',Foundations),('walls',Walls)]:
  for slug,group in zip(Names,groups):
    report['variants'].append({'building':slug,'stage':stage,
      'collection':group.name,'source_scene':group.name+' - Edit source'})
(Root/'reviews/construction-structure.json').write_text(json.dumps(report,indent=2)+'\n')
bpy.context.window.scene = wallStage
for screen in bpy.data.screens:
  for area in screen.areas:
    if area.type == 'VIEW_3D':
      area.spaces.active.region_3d.view_perspective = 'CAMERA'
      area.spaces.active.shading.type = 'MATERIAL'
      area.spaces.active.overlay.show_overlays = False
bpy.ops.wm.save_as_mainfile(filepath=str(Root/'polyworld-construction.blend'))
assert hashlib.sha256(Source.read_bytes()).hexdigest() == SourceHash
for scene,name in [(foundationStage,'construction-foundations'),
  (wallStage,'construction-walls')]:
  bpy.context.window.scene = scene
  scene.render.filepath = str(Root/'renders'/(name+'.png'))
  if os.environ.get('POLYWORLD_BUILDINGS_SKIP_RENDER') != '1':
    bpy.ops.render.render(write_still=True)
print('Created 16 editable construction variants and two review stages.',flush=True)
