"""Create mirrored fort assets with shared trim atlases and a strict triangle budget."""

import hashlib
import json
import math
import shutil
import sys
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector

Root = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Root/'tools'))
from light_trees import createLightTree, setPreviewTints

ReferenceRoot = Root.parent / 'generated_forts'
TileNames = ['masonry', 'stone', 'trim', 'paving', 'roof', 'timber',
             'metal', 'door', 'cloth', 'heraldry', 'magic', 'crystal',
             'bark', 'foundation', 'reinforcement', 'recess']
TileRows = {'dark': [0,313,627,922,1254], 'light': [0,313,627,937,1254]}
TileColumns = [0,313,627,940,1254]
TriangleLimit = 249
SquarePixelTiles = {0,1,2,3,4,6,11,13,14,15}
PixelsPerMeter = 128
assets = []
materials = {}


def newGeometry():
  """Create flat arrays for mesh vertices, faces, tiles, UVs, and part names."""
  return {'vertices': [], 'faces': [], 'tiles': [], 'uvs': [], 'parts': []}


def face(geo, points, tile, part, uv=None):
  """Append one polygon with an explicit texture tile and optional face UVs."""
  indices=[]
  for index,point in enumerate(points):
    if not indices or (Vector(point)-Vector(points[indices[-1]])).length>.000001:
      indices.append(index)
  if len(indices)>1 and (Vector(points[indices[0]])-Vector(points[indices[-1]])).length<.000001:
    indices.pop()
  points=[points[index] for index in indices]
  if uv is not None:
    uv=[uv[index] for index in indices]
  if len(points)<3:
    return
  origin=Vector(points[0])
  area=Vector((0,0,0))
  for index in range(1,len(points)-1):
    area+=(Vector(points[index])-origin).cross(Vector(points[index+1])-origin)
  if area.length<.00000001:
    return
  start = len(geo['vertices'])
  geo['vertices'].extend(points)
  geo['faces'].append(tuple(range(start, start + len(points))))
  geo['tiles'].append(tile)
  geo['uvs'].append(uv)
  geo['parts'].append(part)


def tileUv(faction, tile, u, v):
  """Map normalized face coordinates into a tile with a nine-pixel inset."""
  row, col = divmod(tile, 4)
  left, right = TileColumns[col], TileColumns[col + 1]
  top, bottom = TileRows[faction][row], TileRows[faction][row + 1]
  return ((left + 9 + u * (right - left - 18)) / 1254,
          1 - (bottom - 9 - v * (bottom - top - 18)) / 1254)


def quarterBox(geo, x0, x1, y0, y1, z0, z1, tile, part,
               bottom=True, top=True):
  """Build a box portion, omitting interior faces on both mirror planes."""
  face(geo, [(x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1)], tile, part)
  face(geo, [(x1,y1,z0),(x0,y1,z0),(x0,y1,z1),(x1,y1,z1)], tile, part)
  if x0 > 0:
    face(geo, [(x0,y1,z0),(x0,y0,z0),(x0,y0,z1),(x0,y1,z1)], tile, part)
  if y0 > 0:
    face(geo, [(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)], tile, part)
  if bottom:
    face(geo, [(x0,y1,z0),(x1,y1,z0),(x1,y0,z0),(x0,y0,z0)], tile, part)
  if top:
    face(geo, [(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)], tile, part)


def quarterProfile(geo, rings, tiles, part):
  """Build a quarter of a stepped rectangular solid without seam faces."""
  for i in range(len(rings)-1):
    x0,y0,z0 = rings[i]
    x1,y1,z1 = rings[i+1]
    face(geo, [(x0,0,z0),(x0,y0,z0),(x1,y1,z1),(x1,0,z1)], tiles[i], part)
    face(geo, [(x0,y0,z0),(0,y0,z0),(0,y1,z1),(x1,y1,z1)], tiles[i], part)
  x,y,z = rings[0]
  face(geo, [(0,y,z),(x,y,z),(x,0,z),(0,0,z)], tiles[0], part)
  x,y,z = rings[-1]
  face(geo, [(0,0,z),(x,0,z),(x,y,z),(0,y,z)], tiles[-1], part)


def fullBox(geo, center, size, tile, part):
  """Build a closed rectangular block that is wholly inside a radial sector."""
  x,y,z = center
  w,d,h = (value/2 for value in size)
  p = [(x-w,y-d,z-h),(x+w,y-d,z-h),(x+w,y+d,z-h),(x-w,y+d,z-h),
       (x-w,y-d,z+h),(x+w,y-d,z+h),(x+w,y+d,z+h),(x-w,y+d,z+h)]
  for indices in [(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]:
    face(geo, [p[i] for i in indices], tile, part)


def pyramid(geo, center, width, depth, height, tile, part):
  """Build a four-sided pointed cap using only six triangles."""
  x,y,z = center
  p = [(x-width/2,y-depth/2,z),(x+width/2,y-depth/2,z),
       (x+width/2,y+depth/2,z),(x-width/2,y+depth/2,z)]
  face(geo, list(reversed(p)), tile, part)
  for i in range(4):
    face(geo, [p[i],p[(i+1)%4],(x,y,z+height)], tile, part)


def banner(geo, y, bottom, top, width, tile, part):
  """Make one forward-facing pennant, outside the symmetry modifiers."""
  face(geo, [(-width/2,y,bottom+.17),(0,y,bottom),(width/2,y,bottom+.17),
             (width/2,y,top),(-width/2,y,top)], tile, part,
       [(0,.15),(.5,0),(1,.15),(1,1),(0,1)])


def towerGeometry(faction):
  """Build a single sixty-degree tower sector and a separate front flag."""
  geo = newGeometry()
  dark = faction == 'dark'
  rings = [(1.28,0),(1.28,.18),(1.04,.5),(1.04,.63),(.82,2.96),
           (1.13,3.16),(1.13,3.49),(1.13,3.59)]
  tiles = [13,13,2 if dark else 6,1,2 if dark else 6,2 if dark else 8,6]
  a,b = -2*math.pi/3, -math.pi/3
  def point(radius,angle,z):
    """Convert a radial ring coordinate into a sector vertex."""
    return (radius*math.cos(angle),radius*math.sin(angle),z)
  for i in range(len(rings)-1):
    r0,z0 = rings[i]
    r1,z1 = rings[i+1]
    face(geo,[point(r0,a,z0),point(r0,b,z0),point(r1,b,z1),point(r1,a,z1)],
         tiles[i], 'Hexagonal shaft and collars')
  r,z = rings[0]
  face(geo,[(0,0,z),point(r,b,z),point(r,a,z)],13,'Sole')
  r,z = rings[-1]
  face(geo,[(0,0,z),point(r,a,z),point(r,b,z)],1,'Crown platform')
  p = [(-.19,-1.28,.04),(.19,-1.28,.04),(.19,-.94,1.03),
       (-.19,-.94,1.03),(-.19,-.84,.04),(.19,-.84,.04)]
  for indices in [(0,1,2,3),(0,4,5,1),(4,3,2,5),(0,3,4),(1,5,2)]:
    face(geo,[p[i] for i in indices],2 if dark else 1,'Radial buttress')
  if dark:
    pyramid(geo,(0,-.99,3.59),.44,.4,.88,6,'Crown spike')
    face(geo,[(-.10,-.847,1.25),(.10,-.847,1.25),(.10,-.765,2.35),(-.10,-.765,2.35)],
         10,'Ember slit')
  else:
    fullBox(geo,(0,-.99,3.78),(.48,.4,.38),1,'Crown merlon')
  low=(0,0,3.62)
  peak=(0,0,4.83)
  l=point(.52,a,4.08)
  r=point(.52,b,4.08)
  face(geo,[low,r,l],11,'Crystal lower face')
  face(geo,[l,r,peak],11,'Crystal upper face')
  flag = newGeometry()
  banner(flag,-1.015,1.27,2.61,.68,6,'Flag edging')
  banner(flag,-1.025,1.32,2.56,.57,9,'Forward-facing heraldry')
  return geo,flag


def towerUpgradeGeometry(level):
  """Build one sixty-degree sector of either supplied light tower upgrade."""
  geo=newGeometry()
  a,b=-2*math.pi/3,-math.pi/3
  def point(radius,angle,z):
    """Convert a hexagonal ring point into local coordinates."""
    return (radius*math.cos(angle),radius*math.sin(angle),z)
  if level==2:
    rings=[(1.28,0),(1.06,.48),(.84,2.83),(1.15,3.06),
           (1.15,3.18),(1.15,3.52),(1.15,3.62),(1.15,3.83)]
    tiles=[13,0,1,6,8,6,1]
    shaftBottom,shaftTop=1,2
  else:
    rings=[(1.48,0),(1.12,.65),(.93,3.36),
           (1.34,3.67),(1.34,4.05),(1.34,4.24)]
    tiles=[13,0,6,8,6]
    shaftBottom,shaftTop=1,2
  for i in range(len(rings)-1):
    r0,z0=rings[i]
    r1,z1=rings[i+1]
    face(geo,[point(r0,a,z0),point(r0,b,z0),point(r1,b,z1),point(r1,a,z1)],
         tiles[i],'Tier profile and crown bands')
  radius,z=rings[0]
  face(geo,[(0,0,z),point(radius,b,z),point(radius,a,z)],13,'Closed base')
  radius,z=rings[-1]
  face(geo,[(0,0,z),point(radius,a,z),point(radius,b,z)],1,'Crown coping')
  lowerRadius,lowerZ=rings[shaftBottom]
  upperRadius,upperZ=rings[shaftTop]
  left0,right0=Vector(point(lowerRadius,a,lowerZ)),Vector(point(lowerRadius,b,lowerZ))
  left1,right1=Vector(point(upperRadius,a,upperZ)),Vector(point(upperRadius,b,upperZ))
  stripe=[left0.lerp(right0,.9),right0,right1,left1.lerp(right1,.9)]
  face(geo,[(p.x,p.y-.006,p.z) for p in stripe],6,'Gold shaft edging')
  if level==2:
    p=[(-.24,-1.32,.025),(.24,-1.32,.025),(.24,-.88,.88),
       (-.24,-.88,.88),(-.24,-.78,.025),(.24,-.78,.025)]
    for indices in [(0,1,2,3),(0,4,5,1),(4,3,2,5),(0,3,4),(1,5,2)]:
      face(geo,[p[i] for i in indices],1,'Broad stone buttress')
    x,y,z=0,-1.01,3.79
    w,d,h=.6,.45,.48
    p=[(x-w/2,y-d/2,z),(x+w/2,y-d/2,z),(x+w/2,y+d/2,z),(x-w/2,y+d/2,z),
       (x-w/2,y-d/2,z+h),(x+w/2,y-d/2,z+h),(x+w/2,y+d/2,z+h),(x-w/2,y+d/2,z+h)]
    for indices in [(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]:
      face(geo,[p[i] for i in indices],1,'Stone crown merlon')
    low,wide,peak,radius=3.68,4.09,4.77,.43
    flagY,bottom,top,width=-.965,.92,2.64,.72
  else:
    p=[(-.3,-1.5,.025),(.3,-1.5,.025),(.24,-.87,1.11),
       (-.24,-.87,1.11),(-.3,-.77,.025),(.3,-.77,.025)]
    for indices in [(0,1,2,3),(0,4,5,1),(0,3,4),(1,5,2)]:
      face(geo,[p[i] for i in indices],1,'Armored stone buttress')
    foot=[(-.29,-1.26,4.21),(.29,-1.26,4.21),(0,-.79,4.21)]
    cap=[(x,y,z+.44) for x,y,z in foot]
    for i in range(3):
      j=(i+1)%3
      face(geo,[foot[i],foot[j],cap[j],cap[i]],6,'Gold crystal pedestal')
    face(geo,cap,6,'Gold pedestal cap')
    center=Vector((0,-1.07,4.63))
    ring=[center+Vector((.19*math.cos(i*2*math.pi/3),
                         .19*math.sin(i*2*math.pi/3),.22)) for i in range(3)]
    for i in range(3):
      j=(i+1)%3
      face(geo,[tuple(center),tuple(ring[j]),tuple(ring[i])],11,'Satellite crystal lower')
      face(geo,[tuple(ring[i]),tuple(ring[j]),tuple(center+Vector((0,0,.62)))],
           11,'Satellite crystal tip')
    y=-1.34*math.sqrt(3)/2-.015
    face(geo,[(-.27,y,3.86),(0,y,3.56),(.27,y,3.86),(0,y,4.16)],
         6,'Gold diamond setting')
    face(geo,[(-.165,y-.01,3.86),(0,y-.01,3.68),(.165,y-.01,3.86),(0,y-.01,4.04)],
         11,'Crown sapphire')
    low,wide,peak,radius=4.06,4.84,6.15,.78
    flagY,bottom,top,width=-1.025,1.03,3.19,.88
  left,right=point(radius,a,wide),point(radius,b,wide)
  face(geo,[(0,0,low),right,left],11,'Main crystal lower')
  face(geo,[left,right,(0,0,peak)],11,'Main crystal tip')
  flag=newGeometry()
  banner(flag,flagY,bottom,top,width,6,'Flag edging')
  banner(flag,flagY-.012,bottom+.065,top-.055,width-.13,9,'Forward-facing heraldry')
  return geo,flag


def darkTowerUpgradeGeometry(level):
  """Build a compact or horned dark tower as one editable hexagonal sector."""
  geo=newGeometry()
  a,b=-2*math.pi/3,-math.pi/3
  def point(radius,angle,z):
    """Convert a ring coordinate into a local hexagonal sector vertex."""
    return (radius*math.cos(angle),radius*math.sin(angle),z)
  if level==1:
    rings=[(1.12,0),(.95,.4),(.72,2.2),(1.04,2.38),
           (1.04,2.72),(.89,2.88),(.59,2.88),(.5,2.72)]
    tiles=[13,1,6,1,1,1,6]
    shaftBottom,shaftTop=1,2
    footWidth,footFront,footBack,footTop=.25,-1.17,-.76,.76
    hornBase,hornElbow,hornTip=(-.93,2.73),(-1.03,3.03),(-.94,3.5)
    hornWidths=(.22,.15)
    hornDepths=(.28,.18)
    slitBottom,slitTop,slitWidth=.79,1.94,.28
    low,wide,peak,radius=2.75,3.21,3.97,.46
  else:
    rings=[(1.4,0),(1.4,.12),(1.15,.58),(.9,3.15),
           (1.34,3.45),(1.34,3.56),(1.34,3.97),(.75,3.97),(.61,3.76)]
    tiles=[1,13,1,6,10,1,1,6]
    shaftBottom,shaftTop=2,3
    footWidth,footFront,footBack,footTop=.31,-1.5,-.84,1.22
    hornBase,hornElbow,hornTip=(-1.08,3.88),(-1.67,4.68),(-1.3,5.87)
    hornWidths=(.34,.24)
    hornDepths=(.42,.3)
    slitBottom,slitTop,slitWidth=.9,2.96,.34
    low,wide,peak,radius=3.82,4.8,6.17,.77
  for i in range(len(rings)-1):
    r0,z0=rings[i]
    r1,z1=rings[i+1]
    face(geo,[point(r0,a,z0),point(r0,b,z0),point(r1,b,z1),point(r1,a,z1)],
         tiles[i],'Tapered shaft and hollow crown')
  r,z=rings[0]
  face(geo,[(0,0,z),point(r,b,z),point(r,a,z)],13,'Closed base')
  r,z=rings[-1]
  face(geo,[(0,0,z),point(r,a,z),point(r,b,z)],10,'Ember well')
  w,y0,y1,h=footWidth,footFront,footBack,footTop
  p=[(-w,y0,.015),(w,y0,.015),(w,y1,h),(-w,y1,h),
     (-w,y1+.15,.015),(w,y1+.15,.015)]
  for indices in [(0,1,2,3),(0,4,5,1),(0,3,4),(1,5,2)]:
    face(geo,[p[i] for i in indices],1,'Broad radial buttress')
  horn=[]
  for (y,z),width,depth in zip([hornBase,hornElbow],hornWidths,hornDepths):
    horn.append([(-width,y-depth/2,z),(width,y-depth/2,z),(0,y+depth,z)])
  for i in range(3):
    j=(i+1)%3
    face(geo,[horn[0][i],horn[0][j],horn[1][j]],1,'Bent crown horn')
    face(geo,[horn[0][i],horn[1][j],horn[1][i]],1,'Bent crown horn')
    face(geo,[horn[1][i],horn[1][j],(0,*hornTip)],1,'Horn point')
  r0,z0=rings[shaftBottom]
  r1,z1=rings[shaftTop]
  def shaftY(z,offset):
    """Place a slit layer immediately in front of the tapered shaft plane."""
    radius=r0+(r1-r0)*(z-z0)/(z1-z0)
    return -radius*math.sqrt(3)/2-offset
  for inset,tile,offset in [(0,15,.006),(.055,10,.013)]:
    lo,hi,w=slitBottom+inset,slitTop-inset,slitWidth/2-inset
    points=[(-w,lo),(w,lo),(w,hi-.17),(0,hi),(-w,hi-.17)]
    face(geo,[(x,shaftY(z,offset),z) for x,z in points],tile,
         'Pointed ember slit' if tile==10 else 'Slit recess frame')
  left,right=point(radius,a,wide),point(radius,b,wide)
  face(geo,[(0,0,low),right,left],11,'Main ruby lower')
  face(geo,[left,right,(0,0,peak)],11,'Main ruby point')
  return geo,newGeometry()


def barracksGeometry(faction):
  """Build one quarter of a symmetric barracks with painted surface details."""
  geo = newGeometry()
  dark = faction == 'dark'
  frame = 2 if dark else 5
  quarterProfile(geo,[(1.43,1.84,0),(1.43,1.84,.17),(1.31,1.72,.32)],
                 [13,1], 'Beveled foundation')
  quarterBox(geo,0,1.28,0,1.7,.3,2.1,1 if dark else 13,'Wall shell',False,False)
  face(geo,[(1.28,1.7,2.1),(0,1.7,2.1),(0,1.7,3.45)],
       1 if dark else 13,'Gable')
  a,b,c,d=(1.54,0,2.1),(1.54,1.94,2.1),(0,1.94,3.64),(0,0,3.64)
  aa,bb,cc,dd=[(x,y,z-.13) for x,y,z in [a,b,c,d]]
  face(geo,[a,b,c,d],4,'Roof shingles',[(.5,0),(1,0),(1,1),(.5,1)])
  face(geo,[dd,cc,bb,aa],frame,'Roof underside')
  face(geo,[aa,bb,b,a],frame,'Eave trim')
  face(geo,[bb,cc,c,b],frame,'Gable verge')
  quarterBox(geo,1.18,1.38,1.55,1.78,.28,2.12,frame,'Corner timber')
  face(geo,[(1.29,0,.36),(1.29,1.7,.36),(1.29,1.7,.5),(1.29,0,.5)],
       frame,'Side sill')
  face(geo,[(1.29,0,1.94),(1.29,1.7,1.94),(1.29,1.7,2.1),(1.29,0,2.1)],
       frame,'Side lintel')
  face(geo,[(1.3,.14,.5),(1.3,.33,.5),(1.3,1.53,1.94),(1.3,1.34,1.94)],
       frame,'Diagonal timber')
  face(geo,[(.45,1.711,.32),(0,1.711,.32),(0,1.711,1.76),(.45,1.711,1.76)],
       7,'Door',[(1,0),(.5,0),(.5,1),(1,1)])
  face(geo,[(.58,1.72,.3),(.45,1.72,.3),(.45,1.72,1.87),(.58,1.72,1.87)],
       frame,'Door jamb')
  face(geo,[(1.3,1.79,1.96),(0,1.79,1.96),(0,1.79,2.13),(1.3,1.79,2.13)],
       frame,'Gable crossbeam')
  face(geo,[(.08,1.72,2.12),(0,1.72,2.12),(0,1.72,3.43),(.08,1.72,3.34)],
       frame,'Gable king post')
  face(geo,[(.32,1.737,2.27),(0,1.737,2.22),(0,1.737,2.95),(.32,1.737,2.95)],
       9,'Gable heraldry',[(1,.07),(.5,0),(.5,1),(1,1)])
  if dark:
    p=[(0,1.66,3.48),(.18,1.66,3.48),(.18,1.94,3.48),(0,1.94,3.48)]
    tip=(0,1.8,4.03)
    face(geo,list(reversed(p)),6,'Ridge finial sole')
    for i in range(3):
      face(geo,[p[i],p[i+1],tip],6,'Ridge finial')
  else:
    face(geo,[(1.307,.65,1.03),(1.307,1.15,1.03),(1.307,1.15,1.61),(1.307,.65,1.61)],
         15,'Window recess')
  return geo


def pillarGeometry(faction):
  """Build one quarter of a pillar, including its symmetric capital."""
  geo = newGeometry()
  dark = faction == 'dark'
  quarterProfile(geo,[(.59,.59,0),(.43,.43,.3),(.43,.43,.42),
                      (.38,.38,.42),(.38,.38,2.61),(.58,.58,2.79),(.58,.58,3.01)],
                 [13,2 if dark else 6,1,0,2 if dark else 6,1], 'Pillar profile')
  if dark:
    face(geo,[(0,0,3.01),(.29,0,3.01),(.29,.29,3.01),(0,.29,3.01)],2,'Spear base')
    face(geo,[(.29,0,3.01),(.29,.29,3.01),(0,0,3.97)],6,'Spear X face')
    face(geo,[(.29,.29,3.01),(0,.29,3.01),(0,0,3.97)],6,'Spear Y face')
  else:
    quarterBox(geo,.2,.59,.2,.59,3.0,3.44,1,'Capital merlon')
    face(geo,[(.26,.386,1.13),(0,.386,1.01),(0,.386,2.46),(.26,.386,2.46)],
         6,'Pennant edging',[(1,.1),(.5,0),(.5,1),(1,1)])
    face(geo,[(.21,.395,1.17),(0,.395,1.06),(0,.395,2.41),(.21,.395,2.41)],
         9,'Pennant',[(1,.1),(.5,0),(.5,1),(1,1)])
  return geo


def wallGeometry(faction):
  """Build one quarter of a four-meter connecting wall with planar ends."""
  geo = newGeometry()
  dark = faction == 'dark'
  quarterProfile(geo,[(2,.37,0),(2,.28,.26),(2,.28,.38),(2,.255,.38),
                      (2,.255,2.04),(2,.33,2.13),(2,.33,2.36)],
                 [13,2 if dark else 6,1,0,2 if dark else 6,1], 'Wall profile')
  if not dark:
    quarterBox(geo,0,.25,0,.32,2.36,2.78,1,'Center merlon')
    quarterBox(geo,1.48,1.98,0,.32,2.36,2.78,1,'Outer merlon')
  return geo


def branch(geo, centers, radii, sides, name):
  """Create a closed angular branch from a short sequence of polygon rings."""
  rings=[]
  axis=None
  for index,(point,radius) in enumerate(zip(centers,radii)):
    point=Vector(point)
    direction=Vector(centers[min(index+1,len(centers)-1)])-Vector(centers[max(index-1,0)])
    direction.normalize()
    if axis is not None:
      axis=axis-direction*axis.dot(direction)
    if axis is None or axis.length<.00001:
      reference=Vector((0,1,0)) if abs(direction.y)<.9 else Vector((1,0,0))
      axis=direction.cross(reference)
    axis.normalize()
    side=direction.cross(axis).normalized()
    rings.append([tuple(point+radius*(math.cos(i*2*math.pi/sides)*axis+
                                     math.sin(i*2*math.pi/sides)*side)) for i in range(sides)])
  face(geo,list(reversed(rings[0])),12,name)
  for row in range(len(rings)-1):
    for i in range(sides):
      j=(i+1)%sides
      face(geo,[rings[row][i],rings[row][j],rings[row+1][j],rings[row+1][i]],
           12,name,[(0,0),(1,0),(1,1),(0,1)])
  face(geo,rings[-1],12,name)


def treeGeometry(variant=1):
  """Build four angular dead trees with branches distributed around each trunk."""
  geo=newGeometry()
  if variant==1:
    trunk=[(0,0,0),(.13,-.08,.8),(-.1,.06,1.6),(.13,.12,2.42),
           (-.24,.2,3.34),(-.3,.1,3.8)]
    radii=[.48,.35,.27,.18,.08,.009]
    boughs=[
      ('Left forward bough',[(0,.04,1.5),(-.68,-.24,1.9),(-1.25,-.55,1.94),(-1.4,-.82,2.65)],
       [.25,.19,.1,.009]),
      ('Left forward fork',[(-1.2,-.52,2.03),(-.88,-1.05,2.46),(-.56,-1.34,2.63)],
       [.09,.045,.006]),
      ('Right rear bough',[(0,.08,1.75),(.75,.4,2.04),(1.33,.85,2.43),(1.9,1.11,1.97)],
       [.23,.17,.09,.009]),
      ('Upper forward fork',[(.03,.15,2.62),(.64,-.43,3.05),(1.08,-.72,3.2),(1.18,-.9,3.62)],
       [.14,.09,.05,.006]),
      ('Upper rear fork',[(-.19,.2,3.2),(-.81,.75,3.28),(-1.03,1.04,3.63)],
       [.085,.05,.006])]
    rootCount,rootScale=4,1
  elif variant==2:
    trunk=[(0,0,0),(-.13,.04,.7),(.12,.05,1.3),(.04,-.16,2),(.22,-.48,2.62)]
    radii=[.38,.26,.19,.095,.008]
    boughs=[
      ('Low left hook',[(-.02,.04,.85),(-.56,-.16,1.16),(-1.04,-.29,1.09),(-1.25,-.4,1.79)],
       [.2,.145,.08,.007]),
      ('High rear hook',[(.1,.06,1.3),(.1,.56,1.54),(-.05,.98,1.66),(-.22,1.42,2.19)],
       [.17,.12,.055,.006])]
    rootCount,rootScale=3,.82
  elif variant==3:
    trunk=[(0,0,0),(-.15,.04,.8),(.18,.12,1.48),(.52,.2,2.16),(.72,.08,2.95)]
    radii=[.61,.46,.32,.17,.009]
    boughs=[
      ('Wide left hook',[(-.1,.06,.98),(-.85,-.23,1.35),(-1.65,-.63,1.42),(-2.15,-.78,2.25)],
       [.32,.23,.125,.008]),
      ('Low forward hook',[(.12,.1,1.3),(.85,-.55,1.65),(1.8,-.9,1.63),(2.1,-1.1,1.18)],
       [.29,.21,.11,.009]),
      ('Left rear fork',[(.2,.14,1.59),(-.25,.82,1.97),(-.9,1.43,2.15),(-1.05,1.7,2.78)],
       [.24,.17,.085,.007]),
      ('High rear fork',[(.47,.17,2.03),(1.05,.79,2.28),(1.62,1.16,2.91),(2.02,1.24,3.26)],
       [.18,.125,.065,.006])]
    rootCount,rootScale=4,1.2
  else:
    assert variant==4
    trunk=[(0,0,0),(.18,-.03,.9),(-.07,.16,1.8),(.2,.26,2.65),
           (-.1,.16,3.45),(.1,-.1,4.37),(-.13,-.22,5.2)]
    radii=[.62,.48,.38,.29,.22,.11,.009]
    boughs=[
      ('Low left bough',[(-.01,.12,1.55),(-.78,-.22,1.84),(-1.3,-.52,1.78),(-1.7,-.88,2.49)],
       [.28,.21,.105,.008]),
      ('Low rear bough',[(-.04,.18,1.88),(.79,.65,2.15),(1.58,1.05,2.72),(1.96,1.24,2.4)],
       [.27,.195,.095,.008]),
      ('Forward bough',[(.1,.22,2.25),(.58,-.57,2.58),(.91,-1.32,2.75),(.88,-1.77,3.24)],
       [.245,.17,.085,.007]),
      ('High rear bough',[(.15,.23,2.88),(-.27,.91,3.15),(-.4,1.5,3.07),(-.97,1.95,3.63)],
       [.21,.155,.08,.007]),
      ('High left hook',[(-.05,.16,3.34),(-.77,.02,3.69),(-1.38,-.26,3.78),(-1.56,-.51,4.4)],
       [.18,.125,.065,.006]),
      ('High right hook',[(.05,.03,3.99),(.76,.06,4.23),(1.02,-.2,4.64),(1.5,-.29,4.73)],
       [.14,.1,.052,.006]),
      ('Crown rear fork',[(.08,-.08,4.3),(-.31,.46,4.65),(-.52,.8,4.95),(-.29,1.18,5.04)],
       [.105,.075,.04,.005])]
    rootCount,rootScale=4,1.24
  branch(geo,trunk,radii,4,'Crooked trunk')
  for name,centers,radii in boughs:
    branch(geo,centers,radii,3,name)
  for i in range(rootCount):
    angle=i*2*math.pi/rootCount+math.pi/4
    x,y=math.cos(angle),math.sin(angle)
    centers=[(rootScale*x*r,rootScale*y*r,z*rootScale)
             for r,z in [(.18,.32),(.61,.1),(.95,.015)]]
    branch(geo,centers,[r*rootScale for r in [.23,.11,.005]],3,'Root '+str(i))
  floor=min(p[2] for p in geo['vertices'])
  geo['vertices']=[(x,y,z-floor) for x,y,z in geo['vertices']]
  return geo


def projectUv(mesh, polygon):
  """Project one face with vertical grain and no distortion from world layout."""
  normal=polygon.normal
  if abs(normal.z)<.85:
    u=Vector((0,0,1)).cross(normal).normalized()
    v=normal.cross(u).normalized()
  else:
    u,v=Vector((1,0,0)),Vector((0,1,0))
  points=[mesh.vertices[i].co for i in polygon.vertices]
  pairs=[(p.dot(u),p.dot(v)) for p in points]
  loU,hiU=min(p[0] for p in pairs),max(p[0] for p in pairs)
  loV,hiV=min(p[1] for p in pairs),max(p[1] for p in pairs)
  return [((x-loU)/max(hiU-loU,.00001),(y-loV)/max(hiV-loV,.00001)) for x,y in pairs]


def squarePixelUv(mesh, polygon, faction, tile):
  """Crop each tile with a uniform physical pixel scale on the face plane."""
  normal=polygon.normal.normalized()
  if abs(normal.z)<.85:
    axisU=Vector((0,0,1)).cross(normal).normalized()
  else:
    preferred=Vector((1,0,0))
    axisU=(preferred-normal*preferred.dot(normal)).normalized()
  axisV=normal.cross(axisU).normalized()
  points=[mesh.vertices[i].co for i in polygon.vertices]
  pairs=[(point.dot(axisU),point.dot(axisV)) for point in points]
  lowU,highU=min(p[0] for p in pairs),max(p[0] for p in pairs)
  lowV,highV=min(p[1] for p in pairs),max(p[1] for p in pairs)
  row,col=divmod(tile,4)
  width=TileColumns[col+1]-TileColumns[col]-18
  height=TileRows[faction][row+1]-TileRows[faction][row]-18
  scale=min(PixelsPerMeter,width/max(highU-lowU,.00001),
            height/max(highV-lowV,.00001))
  centerU,centerV=(lowU+highU)/2,(lowV+highV)/2
  return [(.5+(u-centerU)*scale/width,.5+(v-centerV)*scale/height)
          for u,v in pairs]


def meshObject(geo, name, faction, collection, parent):
  """Create an editable mesh with face tile IDs, UVs, and named part groups."""
  mesh=bpy.data.meshes.new(name)
  mesh.from_pydata(geo['vertices'],[],geo['faces'])
  mesh.update()
  obj=bpy.data.objects.new(name,mesh)
  collection.objects.link(obj)
  obj.parent=parent
  mesh.materials.append(materials[(faction,False)])
  mesh.materials.append(materials[(faction,True)])
  uv=mesh.uv_layers.new(name='TrimUV')
  attribute=mesh.attributes.new('trim_tile','INT','FACE')
  groups={part:obj.vertex_groups.new(name=part) for part in dict.fromkeys(geo['parts'])}
  for polygon,tile,coords,part in zip(mesh.polygons,geo['tiles'],geo['uvs'],geo['parts']):
    attribute.data[polygon.index].value=tile
    polygon.material_index=1 if tile in [10,11] else 0
    coordinates=(squarePixelUv(mesh,polygon,faction,tile)
                 if tile in SquarePixelTiles else
                 coords or projectUv(mesh,polygon))
    for loopIndex,(u,v) in zip(polygon.loop_indices,coordinates):
      uv.data[loopIndex].uv=tileUv(faction,tile,u,v)
    groups[part].add(list(polygon.vertices),1,'REPLACE')
  weld=obj.modifiers.new('Weld shared vertices','WELD')
  weld.merge_threshold=.00001
  obj['license']='generated'
  obj['texture_atlas']=faction+'_trim.png'
  return obj


def newCollection(name,parent):
  """Create an organized asset collection under its supplied parent."""
  result=bpy.data.collections.new(name)
  parent.children.link(result)
  return result


def triangleCount(objects):
  """Count evaluated triangles, including all mirror and array copies."""
  bpy.context.view_layer.update()
  graph=bpy.context.evaluated_depsgraph_get()
  total=0
  for obj in objects:
    evaluated=obj.evaluated_get(graph)
    mesh=evaluated.to_mesh()
    mesh.calc_loop_triangles()
    total+=len(mesh.loop_triangles)
    evaluated.to_mesh_clear()
  return total


def attachmentPoint(geo,name):
  """Find a crystal firing center or a front door threshold from source faces."""
  if name.startswith('tower'):
    parts={'Crystal lower face','Crystal upper face','Main crystal lower',
           'Main crystal tip','Main ruby lower','Main ruby point'}
    vertices=[geo['vertices'][index]
              for indices,part in zip(geo['faces'],geo['parts']) if part in parts
              for index in indices]
    assert vertices,'The tower needs a central crystal for its fire attachment.'
    z=(min(p[2] for p in vertices)+max(p[2] for p in vertices))/2
    return {'name':'fire','position':[0,0,round(z,6)]}
  if name=='barracks':
    vertices=[geo['vertices'][index]
              for indices,part in zip(geo['faces'],geo['parts']) if part=='Door'
              for index in indices]
    assert vertices,'The barracks needs a door for its spawn attachment.'
    y=-max(abs(p[1]) for p in vertices)-.05
    z=min(p[2] for p in vertices)
    return {'name':'spawn','position':[0,round(y,6),round(z,6)]}
  return None


def createAsset(faction,name,index,scene,parent):
  """Create actual live symmetry modifiers and export the evaluated model."""
  exportName=(f'tower_level{2 if faction=="dark" else 1}'
              if name=='tower' else 'tree_1' if name=='tree' else name)
  collection=newCollection(faction.title()+' '+exportName.replace('_',' ').title(),parent)
  root=bpy.data.objects.new(faction+'_'+name,None)
  collection.objects.link(root)
  meshes=[]
  if name.startswith('tower'):
    if name=='tower':
      geo,flag=towerGeometry(faction)
    elif faction=='dark':
      geo,flag=darkTowerUpgradeGeometry(int(name[-1]))
    else:
      geo,flag=towerUpgradeGeometry(int(name[-1]))
    obj=meshObject(geo,'One hexagonal sector',faction,collection,root)
    offset=bpy.data.objects.new('Radial step 60 degrees',None)
    collection.objects.link(offset)
    offset.parent=root
    offset.rotation_euler.z=math.pi/3
    offset.empty_display_size=.25
    offset.hide_render=True
    array=obj.modifiers.new('Sixfold hexagonal symmetry','ARRAY')
    array.count=6
    array.use_relative_offset=False
    array.use_constant_offset=False
    array.use_object_offset=True
    array.offset_object=offset
    array.use_merge_vertices=True
    array.merge_threshold=.0001
    meshes=[obj]
    symmetry='sixfold radial array'
    if flag['faces']:
      meshes.append(meshObject(flag,'Front flag, no symmetry',faction,collection,root))
      symmetry+='; separate front flag'
  else:
    builders={'barracks':barracksGeometry,'pillar':pillarGeometry,'wall':wallGeometry}
    isTree=name.startswith('tree')
    variant=1 if name=='tree' else int(name[-1]) if isTree else None
    geo=treeGeometry(variant) if isTree else builders[name](faction)
    obj=meshObject(geo,'Dead tree' if isTree else 'Quarter mesh',faction,collection,root)
    if not isTree:
      mirror=obj.modifiers.new('Four-way X and Y mirroring','MIRROR')
      mirror.use_axis=(True,True,False)
      mirror.use_clip=True
      mirror.use_mirror_merge=True
      mirror.merge_threshold=.0001
      symmetry='four-way X/Y Mirror modifier'
    else:
      symmetry='asymmetric branches'
    meshes=[obj]
  if faction=='light' and name=='tower':
    referenceGeo,_=darkTowerUpgradeGeometry(1)
    targetHeight=max(p[2] for p in referenceGeo['vertices'])-min(p[2] for p in referenceGeo['vertices'])
    sourceHeight=max(p[2] for p in geo['vertices'])-min(p[2] for p in geo['vertices'])
    scale=targetHeight/sourceHeight
    for obj in meshes:
      for vertex in obj.data.vertices:
        vertex.co*=scale
      obj.data.update()
    geo['vertices']=[tuple(value*scale for value in point) for point in geo['vertices']]
    root['uniform_scale_from_source']=scale
  count=triangleCount(meshes)
  print('TRIANGLES',faction,name,count,flush=True)
  assert 0<count<=TriangleLimit,(faction,name,count)
  collection['triangles']=count
  root['triangles']=count
  root['license']='generated'
  root['symmetry']=symmetry
  reference=(f'references/{faction}_{name}.png' if name.startswith('tower_level') else
             f'../generated_forts/{faction}/meshy/{name}.glb')
  if name.startswith('tree_'):
    reference=f'references/dead_tree_style{ {2:2,3:3,4:1}[variant] }.png'
  root['reference']=reference
  for obj in meshes:
    obj.name=faction+'_'+name+' / '+obj.name
  attachment=attachmentPoint(geo,name)
  empties=[]
  if attachment:
    empty=bpy.data.objects.new(attachment['name'],None)
    collection.objects.link(empty)
    empty.parent=root
    empty.location=attachment['position']
    empty.empty_display_type='PLAIN_AXES'
    empty.empty_display_size=.22
    empty.show_name=True
    empty.show_in_front=True
    empty['attachment']=attachment['name']
    empty['license']='generated'
    empties.append(empty)
  bpy.ops.object.select_all(action='DESELECT')
  for obj in meshes+empties:
    obj.select_set(True)
  bpy.context.view_layer.objects.active=meshes[0]
  target=Root/'models'/faction/(exportName+'.glb')
  target.parent.mkdir(parents=True,exist_ok=True)
  bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',
    use_selection=True,export_apply=True,export_texcoords=True,
    export_normals=True,export_materials='EXPORT',export_extras=True)
  for empty in empties:
    empty.name=faction+'_'+exportName+' / '+attachment['name']
  if name.startswith('tower'):
    root.location=((int(exportName[-1])-3)*5.5,7 if faction=='dark' else 0,0)
  elif name.startswith('tree_'):
    root.location=(22+((variant-1)%2)*5.5,7+((variant-1)//2)*6,0)
  else:
    root.location=(index*5.5,7 if faction=='dark' else 0,0)
  assets.append({'faction':faction,'asset':name,'triangles':count,
    'file':str(target.relative_to(Root)),'symmetry':symmetry,
    'license':'generated','texture':f'textures/{faction}_trim.png','reference':reference,
    'attachments':[attachment] if attachment else [],
    'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
    'objects':meshes,'collection':collection,'root':root})
  if name.startswith('tree'):
    groups=set(geo['parts'])
    assets[-1]['tree_shape']={
      'variant':variant,
      'branches':sum(part!='Crooked trunk' and not part.startswith('Root ') for part in groups),
      'roots':sum(part.startswith('Root ') for part in groups),
      'dimensions':[round(max(p[i] for p in geo['vertices'])-
                          min(p[i] for p in geo['vertices']),4) for i in range(3)]}


def atlasMaterial(faction,image,glow):
  """Create one directly exportable painted atlas material and a glow variant."""
  result=bpy.data.materials.new(faction.title()+(' magic trim' if glow else ' painted trim'))
  result.use_nodes=True
  result.use_backface_culling=False
  shader=result.node_tree.nodes.get('Principled BSDF')
  shader.inputs['Roughness'].default_value=.87
  shader.inputs['Metallic'].default_value=0
  tex=result.node_tree.nodes.new('ShaderNodeTexImage')
  tex.name='4x4 trim sheet'
  tex.label='TrimUV: explicit face-to-tile mapping'
  tex.image=image
  tex.interpolation='Linear'
  tex.extension='EXTEND'
  result.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
  if glow:
    result.node_tree.links.new(tex.outputs['Color'],shader.inputs['Emission Color'])
    shader.inputs['Emission Strength'].default_value=.18
  result['license']='generated'
  return result


def setupScene(scene):
  """Configure consistent neutral lighting for the painted surfaces."""
  scene.render.engine='CYCLES'
  scene.cycles.samples=20
  scene.cycles.use_denoising=True
  scene.cycles.transparent_max_bounces=64
  scene.render.resolution_percentage=100
  scene.render.image_settings.file_format='PNG'
  scene.view_settings.view_transform='Standard'
  scene.world=bpy.data.worlds.new(scene.name+' world')
  scene.world.use_nodes=True
  scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.20,.22,.26,1)
  scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7


def aim(obj,target):
  """Point an object's negative Z axis toward its target."""
  obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()


def frameObjects(scene,objects,resolution=(700,700),reverse=False,side=False,view=None):
  """Frame evaluated geometry, including modifier copies, in an orthographic view."""
  bpy.context.view_layer.update()
  graph=bpy.context.evaluated_depsgraph_get()
  points=[]
  for obj in objects:
    evaluated=obj.evaluated_get(graph)
    points.extend(evaluated.matrix_world@Vector(corner) for corner in evaluated.bound_box)
  low=Vector(tuple(min(p[i] for p in points) for i in range(3)))
  high=Vector(tuple(max(p[i] for p in points) for i in range(3)))
  center=(low+high)/2
  span=max(high-low)
  camera=bpy.data.cameras.new('Orthographic camera')
  obj=bpy.data.objects.new('Orthographic camera',camera)
  scene.collection.objects.link(obj)
  offset=Vector((2.4,1.4,1.45) if side else
                (-1.4,2.4,1.45) if reverse else (1.4,-2.4,1.45))
  if view is not None:
    offset=Vector({'game':(1.4,-2.4,5.5),'top':(0,-.001,7),
                   'profile':(1.4,-2.4,.10)}[view])
  obj.location=center+offset*span
  aim(obj,center)
  camera.type='ORTHO'
  camera.clip_end=1000
  rotation=obj.rotation_euler.to_matrix().transposed()
  projected=[rotation@(p-center) for p in points]
  width=max(p.x for p in projected)-min(p.x for p in projected)
  height=max(p.y for p in projected)-min(p.y for p in projected)
  middleX=(max(p.x for p in projected)+min(p.x for p in projected))/2
  middleY=(max(p.y for p in projected)+min(p.y for p in projected))/2
  shift=rotation.transposed()@Vector((middleX,middleY,0))
  obj.location+=shift
  center+=shift
  aspect=resolution[0]/resolution[1]
  camera.ortho_scale=max(width,height*aspect)*1.14
  scene.render.resolution_x,scene.render.resolution_y=resolution
  scene.camera=obj
  helpers=[obj]
  for name,offset,power in [('Key',(-1.5,-2,3),100),('Fill',(2,1,2),60)]:
    light=bpy.data.lights.new(name,'AREA')
    light.energy=power*span*span
    light.shape='DISK'
    light.size=span*2
    obj=bpy.data.objects.new(name,light)
    scene.collection.objects.link(obj)
    obj.location=center+Vector(offset)*span
    aim(obj,center)
    helpers.append(obj)
  return helpers


def renderIndividual(asset,reverse=False,side=False,top=False):
  """Render the current rebuilt asset without changing its editable modifiers."""
  for item in assets:
    item['collection'].hide_render=item is not asset
  scene=bpy.context.scene
  view=('top' if top else 'profile' if side else 'game') if 'foliage' in asset else None
  helpers=frameObjects(scene,asset['objects'],reverse=reverse,side=side,view=view)
  suffix='_top' if top else '_side' if side else '_back' if reverse else ''
  scene.render.filepath=str(Root/'previews'/(asset['faction']+'_'+asset['asset']+suffix+'.png'))
  bpy.ops.render.render(write_still=True)
  for helper in helpers:
    bpy.data.objects.remove(helper,do_unlink=True)
  for item in assets:
    item['collection'].hide_render=False


def renderTowerLevels(faction):
  """Render all three tower levels in their faction row from left to right."""
  selected=[asset for asset in assets if asset['faction']==faction and
            asset['asset'].startswith('tower')]
  for item in assets:
    item['collection'].hide_render=item not in selected
  scene=bpy.context.scene
  helpers=frameObjects(scene,[obj for item in selected for obj in item['objects']],(1500,1100))
  scene.render.filepath=str(Root/'previews'/(faction+'_tower_levels.png'))
  bpy.ops.render.render(write_still=True)
  for helper in helpers:
    bpy.data.objects.remove(helper,do_unlink=True)
  for item in assets:
    item['collection'].hide_render=False


def renderTrees(faction='dark',view=None):
  """Compare all four trees at the same scale while keeping their saved layout."""
  selected=[asset for asset in assets if asset['asset'].startswith('tree') and
            asset['faction']==faction]
  positions=[item['root'].location.copy() for item in selected]
  across=Vector((1,0,0) if view=='top' else (2.4,1.4,0)).normalized()
  for index,item in enumerate(selected):
    item['root'].location=across*(index*5.5)
  for item in assets:
    item['collection'].hide_render=item not in selected
  scene=bpy.context.scene
  helpers=frameObjects(scene,[obj for item in selected for obj in item['objects']],
                       (1900,750 if faction=='light' else 950),
                       view=view or ('game' if faction=='light' else None))
  suffix='_'+view if view in ['top','profile'] else ''
  filename='dead_trees.png' if faction=='dark' else 'light_trees'+suffix+'.png'
  scene.render.filepath=str(Root/'previews'/filename)
  bpy.ops.render.render(write_still=True)
  for helper in helpers:
    bpy.data.objects.remove(helper,do_unlink=True)
  for item,position in zip(selected,positions):
    item['root'].location=position
  for item in assets:
    item['collection'].hide_render=False


def importReferences():
  """Keep both original providers' GLBs in a separate comparison scene."""
  scene=bpy.data.scenes.new('02 Generated GLB references')
  bpy.context.window.scene=scene
  if not ReferenceRoot.exists():
    names=[faction.title()+' '+provider.title()
           for faction in ['light','dark'] for provider in ['meshy','tripo']]
    with tempfile.TemporaryDirectory(prefix='fort-references-') as temporary:
      referenceCopy=Path(temporary)/'packed_references.blend'
      shutil.copy2(Root/'fort_kit.blend',referenceCopy)
      with bpy.data.libraries.load(str(referenceCopy),link=False) as (source,target):
        assert all(name in source.collections for name in names)
        target.collections=names
    for collection in target.collections:
      scene.collection.children.link(collection)
  for row,faction in enumerate(['light','dark'] if ReferenceRoot.exists() else []):
    for providerIndex,provider in enumerate(['meshy','tripo']):
      group=newCollection(faction.title()+' '+provider.title(),scene.collection)
      for index,name in enumerate(['tower','barracks','pillar','wall','tree']):
        source=ReferenceRoot/faction/provider/(name+'.glb')
        if not source.exists():
          continue
        before=set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=str(source))
        imported=[obj for obj in bpy.data.objects if obj not in before]
        meshes=[obj for obj in imported if obj.type=='MESH']
        bpy.context.view_layer.update()
        points=[obj.matrix_world@Vector(corner) for obj in meshes for corner in obj.bound_box]
        low=Vector(tuple(min(p[i] for p in points) for i in range(3)))
        high=Vector(tuple(max(p[i] for p in points) for i in range(3)))
        scale=4/max(high-low)
        center=Vector(((low.x+high.x)/2,(low.y+high.y)/2,low.z))
        offset=Vector((index*6,(row*2+providerIndex)*7,0))
        matrices={obj:obj.matrix_world.copy() for obj in meshes}
        for obj in meshes:
          obj.parent=None
          obj.matrix_world=matrices[obj]
          obj.location=(obj.location-center)*scale+offset
          obj.scale*=scale
          for old in list(obj.users_collection):
            old.objects.unlink(obj)
          group.objects.link(obj)
          obj.name='REFERENCE '+faction+' '+provider+' '+name
          obj['reference_only']=True
          obj['source_glb']=str(source.relative_to(Root.parent))
        for obj in imported:
          if obj.type!='MESH':
            bpy.data.objects.remove(obj,do_unlink=True)
  for row,(faction,levels) in enumerate([('light',[2,3]),('dark',[1,3])]):
    drawings=newCollection(faction.title()+' tower level concept references',scene.collection)
    for index,level in enumerate(levels):
      image=bpy.data.images.load(str(Root/'references'/f'{faction}_tower_level{level}.png'))
      image.name=f'{faction.title()} tower level {level} concept'
      image.pack()
      obj=bpy.data.objects.new(f'REFERENCE {faction.title()} tower level {level}',None)
      drawings.objects.link(obj)
      obj.empty_display_type='IMAGE'
      obj.data=image
      obj.empty_display_size=6
      obj.rotation_euler.x=math.pi/2
      obj.location=(30+index*6,row*7,3)
      obj['reference_only']=True
  drawings=newCollection('Dead tree style references',scene.collection)
  for index in range(1,4):
    image=bpy.data.images.load(str(Root/'references'/f'dead_tree_style{index}.png'))
    image.name=f'Dead tree style {index}'
    image.pack()
    obj=bpy.data.objects.new(f'REFERENCE Dead tree style {index}',None)
    drawings.objects.link(obj)
    obj.empty_display_type='IMAGE'
    obj.data=image
    obj.empty_display_size=4
    obj.rotation_euler.x=math.pi/2
    obj.location=(30+(index-1)*5,14,3)
    obj['reference_only']=True
  image=bpy.data.images.load(str(Root/'references/light_tree_styles.png'))
  image.name='Light tree styles'
  image.pack()
  obj=bpy.data.objects.new('REFERENCE Light tree styles',None)
  drawings.objects.link(obj)
  obj.empty_display_type='IMAGE'
  obj.data=image
  obj.empty_display_size=6
  obj.rotation_euler.x=math.pi/2
  obj.location=(30,21,3)
  obj['reference_only']=True
  image=bpy.data.images.load(str(Root/'references/tree_ring_layout.png'))
  image.name='Tree ring layout'
  image.pack()
  obj=bpy.data.objects.new('REFERENCE Tree ring layout',None)
  drawings.objects.link(obj)
  obj.empty_display_type='IMAGE'
  obj.data=image
  obj.empty_display_size=8
  obj.rotation_euler.x=math.pi/2
  obj.location=(38,21,3)
  obj['reference_only']=True
  setupScene(scene)
  bpy.context.view_layer.update()
  frameObjects(scene,[obj for obj in scene.objects if obj.type=='MESH'],(1900,1100))


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version=0
scene=bpy.context.scene
scene.name='01 Rebuilt mirrored fort kit'
for faction in ['dark','light']:
  image=bpy.data.images.load(str(Root/'textures'/(faction+'_trim.png')))
  image.name=faction.title()+' 4x4 trim atlas'
  image.pack()
  for glow in [False,True]:
    materials[(faction,glow)]=atlasMaterial(faction,image,glow)
  parent=newCollection(faction.title()+' rebuilt assets',scene.collection)
  for index,name in enumerate(['tower','barracks','pillar','wall','tree']):
    if faction=='light' and name=='tree':
      continue
    createAsset(faction,name,index,scene,parent)
  for level in ([1,3] if faction=='dark' else [2,3]):
    createAsset(faction,'tower_level'+str(level),level,scene,parent)
for variant in [2,3,4]:
  createAsset('dark','tree_'+str(variant),variant,scene,
              bpy.data.collections['Dark rebuilt assets'])
foliageAtlas=bpy.data.images.load(str(Root/'textures/tree_foliage_atlas.png'))
foliageAtlas.name='Tree foliage atlas'
foliageAtlas.pack()
for variant in [1,2,3,4]:
  assets.append(createLightTree(variant,Root,scene,bpy.data.collections['Light rebuilt assets'],
                               foliageAtlas,branch,newGeometry))
setupScene(scene)
bpy.context.view_layer.update()
if '--render' in sys.argv:
  setPreviewTints(assets,True)
  for asset in assets:
    renderIndividual(asset)
    if asset['asset']=='barracks' or asset['asset'].startswith('tower'):
      renderIndividual(asset,True)
    if asset['asset'].startswith('tree'):
      renderIndividual(asset,side=True)
    if 'foliage' in asset:
      renderIndividual(asset,top=True)
  for faction in ['light','dark']:
    renderTowerLevels(faction)
  for faction in ['dark','light']:
    renderTrees(faction)
  renderTrees('light','top')
  renderTrees('light','profile')
importReferences()
bpy.context.window.scene=scene
bpy.context.view_layer.update()
frameObjects(scene,[obj for asset in assets for obj in asset['objects']],(2100,1200))
scene.render.filepath=str(Root/'previews'/'fort_kit.png')
if '--render' in sys.argv:
  bpy.ops.render.render(write_still=True)
setPreviewTints(assets,False)
for area in bpy.context.screen.areas:
  if area.type=='VIEW_3D':
    area.spaces.active.region_3d.view_perspective='CAMERA'
    area.spaces.active.shading.type='MATERIAL'
bpy.ops.object.select_all(action='DESELECT')
assets[0]['objects'][0].select_set(True)
bpy.context.view_layer.objects.active=assets[0]['objects'][0]
manifest={
  'pack':'blender_forts','license':'generated','blend_file':'fort_kit.blend',
  'model_count':len(assets),'maximum_triangles_per_model':TriangleLimit,
  'construction':'Hand-built Blender meshes. Live X/Y mirrors and sixfold radial arrays. No decimation.',
  'texture_generation':'Built-in image_gen; prompts in textures/prompts.json.',
  'attachment_coordinates':'Asset-local Blender coordinates: Z up, front -Y. GLB uses Y up: (x, z, -y).',
  'foliage_atlas':{'file':'textures/tree_foliage_atlas.png','version':5,'size':[2048,2048],
    'sha256':hashlib.sha256((Root/'textures/tree_foliage_atlas.png').read_bytes()).hexdigest(),
    'grid':[4,4],'cell_size':[512,512],'uv_inset_pixels':8,
    'metadata':'textures/tree_foliage_atlas.json','alpha_mode':'MASK','alpha_cutoff':.45,
    'export_meshes':['trunk','foliage'],'tint':'Neutral grayscale foliage; engine tints foliage only.',
    'preview':'Example colors only; exported baseColorFactor is white.',
    'construction':'Offset rings with inward attachments and outward, descending tips; lower rings are darker.',
    'primary_view':'63 degrees above the ground, 27 degrees from vertical.',
    'layout_reference':'references/tree_ring_layout.png'},
  'uv_mapping':{'square_pixel_tiles':sorted(SquarePixelTiles),
    'target_pixels_per_meter':PixelsPerMeter,
    'method':'Orthographic face-plane projection with one uniform pixel scale. Crop the tile; lower density uniformly only when necessary to fit.',
    'artwork_and_grain_tiles':[5,7,8,9,10,12]},
  'tile_names':TileNames,
  'textures':{faction:{'file':f'textures/{faction}_trim.png','grid':[4,4],
              'size':[1254,1254],'pixel_columns':TileColumns,
              'pixel_rows':TileRows[faction],'uv_inset_pixels':9}
              for faction in ['dark','light']},
  'assets':[{key:value for key,value in asset.items()
             if key not in ['objects','collection','root']} for asset in assets],
}
(Root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
notes=bpy.data.texts.new('START HERE')
notes.write('''MIRRORED FORT KIT\n\nScene 01 contains the rebuilt assets. Scene 02 contains all 18 original GLB references.\n\nBarracks, pillars and walls: edit one quarter; live X/Y Mirror makes the other three.\nTowers: edit one 60-degree sector; live Array repeats it six times around the Z axis.\nThe array uses the child empty named Radial step 60 degrees.\nTower flags are separate objects facing -Y and have no symmetry modifier.\nThe dead tree is deliberately asymmetric.\n\nEach asset has one root empty at its ground-level origin. Move the root to move the model.\nTriangle counts include evaluated modifier copies and the separate tower flags.\nEach mesh has TrimUV coordinates, a trim_tile face attribute, and named part vertex groups.\nBoth 4x4 texture atlases are packed into this file.\nUse the UV Editing workspace to inspect or adjust face-to-tile assignments.\nIndividual GLBs have symmetry applied and textures embedded.\nBoth wall panels are 4 meters long, with square ends for modular placement.\nLicense label: generated.\n''')
notes.write('\nLight upgrades: tower_level2 and tower_level3.\nDark upgrades: tower_level1 and tower_level3. The original dark tower is level 2.\nThe new dark towers have ember slits and no flags, matching their concepts.\nAll tower and tree reference images are packed into Scene 02.\nAll twenty rebuilt models remain below 250 triangles, including modifier copies.\n')
notes.write('\nLIGHT TREES\nLight tree_1 is evergreen; tree_2, tree_3, tree_4 are small, medium, and large leafy trees.\nEach GLB has meshes named trunk and foliage. Tint foliage independently in the engine.\nFoliage consists only of separate double-sided alpha-masked quads. Branches form staggered rings around the trunk.\nAttachments point inward; tips descend outward along a cone or rounded crown.\nUpper rings overlap lower rings; lower rings use darker atlas tiles.\nPrimary previews use a tilted overhead camera. Top and profile views are included. The evergreen trunk has roots but no wooden side branches.\nThe supplied tree atlas is packed and embedded unchanged.\nThe saved materials are neutral grayscale for engine tinting. Preview PNGs show example colors.\nIn Blender, change the Engine tint node on a Tree foliage material to preview a color.\n')
notes.write('\nLAYOUT\nEach faction has its own row: dark at Y=7, light at Y=0.\nTowers run left to right: level 1, level 2, level 3. Other structures follow to the right.\n')
notes.write('\nLight level 1 is uniformly scaled to match dark level 1 height, including its flag and fire point.\nThe scale is baked into the mesh, preserving its original UV coordinates and editable symmetry.\n')
notes.write('\nDEAD TREES\nThe original tree now has branches extending forward and backward around its trunk.\nThree additional shapes are tree_2 (short, sparse), tree_3 (wide), and tree_4 (tall, many branches).\nAll four use the dark bark trim tile. Named vertex groups identify each trunk, bough, and root.\nTree variants occupy a two-by-two group at the right of the dark faction.\n')
notes.write('\nGAMEPLAY ATTACHMENTS\nEvery tower exports a meshless node named fire at the central crystal bounding-box center.\nEvery barracks exports a meshless node named spawn at the front door threshold, 0.05 m outside.\nIn Blender these root-parented empties have asset-prefixed names to avoid global name collisions.\nTheir attachment property holds the exact GLB name. The builder exports the bare fire/spawn name.\nAttachment positions use asset-local coordinates, independent of the presentation layout.\n')
for image in bpy.data.images:
  if image.source=='FILE' and not image.packed_file:
    image.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(Root/'fort_kit.blend'))
print('SAVED',Root/'fort_kit.blend',flush=True)
