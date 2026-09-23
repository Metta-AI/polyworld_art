"""Build the Berserker's fitted, independently selectable solid-color outfit."""

import math

import bpy
import bmesh
from mathutils import Vector

from clothes import band, bodySurface, clip, material, meshObject, offset
from garments import exterior, finish
from gota_common import bind, duplicate, mesh, part


def reduce(item, ratio):
  """Reduce copied detail to broad facets while retaining shared rig weights."""
  bpy.context.view_layer.objects.active = item
  modifier = item.modifiers.new('Berserker broad facets', 'DECIMATE')
  modifier.ratio = ratio
  modifier.use_collapse_triangulate = True
  bpy.ops.object.modifier_move_to_index(modifier=modifier.name, index=0)
  bpy.ops.object.modifier_apply(modifier=modifier.name)
  for face in item.data.polygons:
    face.use_smooth = False


def polygon(ctx, suffix, points, color, depth=.022, bone=None):
  """Make a closed angular cloth panel with a shallow raised middle ridge."""
  front = [Vector(p) for p in points]
  normal = (front[1]-front[0]).cross(front[2]-front[0]).normalized()
  center = sum(front, Vector())/len(front) + normal*depth
  vertices = [tuple(p) for p in front]+[tuple(center)]
  n=len(front)
  faces=[(i,(i+1)%n,n) for i in range(n)]
  vertices.extend(tuple(p-normal*.014) for p in front)
  faces.append(tuple(n+1+i for i in reversed(range(n))))
  faces += [(i,n+1+i,n+1+(i+1)%n,(i+1)%n) for i in range(n)]
  return mesh(ctx,suffix,vertices,faces,[color],bone=bone)


def cuff(ctx, suffix, x):
  """Wrap the fitted boot with one thick angular tan fur cuff."""
  vertices, faces=[],[]
  sides=10
  for ring in range(4):
    for i in range(sides):
      t=math.tau*i/sides
      outer=ring<2
      z=.49 if ring%2==0 else .31 + (.04 if i%2==0 else 0)
      rx=(.185 if ring%2==0 else .21) if outer else .147
      ry=(.215 if ring%2==0 else .225) if outer else .17
      vertices.append((x+rx*math.sin(t),.014-ry*math.cos(t),z))
  for i in range(sides):
    j=(i+1)%sides
    faces.extend([(i,j,sides+j,sides+i),
                  (2*sides+i,3*sides+i,3*sides+j,2*sides+j),
                  (i,2*sides+i,2*sides+j,j),
                  (sides+i,sides+j,3*sides+j,3*sides+i)])
  return mesh(ctx,suffix,vertices,faces,['#cab085'])


def ringBuckle(ctx):
  """Create the open silver hexagon at the center of the leather belt."""
  vertices, faces=[],[]
  for y,r in [(-.363,.122),(-.379,.073),(-.333,.122),(-.333,.073)]:
    for i in range(6):
      t=math.tau*i/6
      vertices.append((math.sin(t)*r,y,1.294+math.cos(t)*r))
  for i in range(6):
    j=(i+1)%6
    faces += [(i,j,6+j,6+i),(i,12+i,12+j,j),
              (6+i,6+j,18+j,18+i),(12+i,18+i,18+j,12+j)]
  return mesh(ctx,'buckle',vertices,faces,['#a9acb6'])


def spike(ctx, suffix, start, end, width, depth, color):
  """Add a low-sided closed wedge to the reused fitted hairstyle."""
  start,end=Vector(start),Vector(end)
  axis=(end-start).normalized()
  wide=axis.cross(Vector((0,1,0))).normalized()*width
  deep=axis.cross(wide).normalized()*depth
  vertices=[tuple(start+wide),tuple(start+deep),tuple(start-wide),
            tuple(start-deep),tuple(end)]
  faces=[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(3,2,1,0)]
  return mesh(ctx,suffix,vertices,faces,[color],bone='Head')


def build(ctx):
  """Reuse fitted base geometry and add the Berserker's defining clothing."""
  parts=[]
  source=bodySurface([ctx.body])
  boots=duplicate(ctx,'Clothing_16','boots',
    ['#704324','#cab085','#493729','#a9acb6','#38281c'])
  for item in boots:
    data=bmesh.new()
    data.from_mesh(item.data)
    bmesh.ops.delete(data,geom=[f for f in data.faces if f.material_index==1],
                    context='FACES')
    data.to_mesh(item.data)
    data.free()
    reduce(item,.30)
    bind(ctx,item)
  for side,x in [('left',.245),('right',-.245)]:
    boots.append(cuff(ctx,'fur_cuff_'+side,x))
  parts.append(part(ctx,'Foot','Gota Berserker fur boots',boots))

  pantsSource=[o for o in bpy.data.objects if o.name=='Clothing_12'
    or o.name.startswith('Clothing_12_BootCut')]
  pantsSurface=clip(exterior(pantsSource,ctx.body),lambda p:p.z-.375)
  pants=finish(ctx.collection,ctx.prefix+'trousers',[(pantsSurface,0)],
               [material(ctx.prefix+'charcoal trousers','#39383d')],
               'Clothing_12 fitted charcoal trousers')
  for face in pants.data.polygons:
    face.use_smooth=False
  bind(ctx,pants)
  legs=[pants]
  # The split side fur leaves the dark trousers and separate boots visible.
  for side in [-1,1]:
    for rear in [-1,1]:
      y=rear*.26
      for layer in range(2):
        z=1.245-layer*.145
        points=[(side*.18,y,z),(side*.37,y*.75,z+.015),
                (side*(.43+layer*.025),y*.80,z-.23),
                (side*.285,y*1.13,z-.155)]
        if side*rear<0:
          points.reverse()
        legs.append(polygon(ctx,f'fur_{side}_{rear}_{layer}',points,
                            '#c5ac83' if layer==0 else '#d5bd91',bone='Hips'))
  legs.append(polygon(ctx,'front_leather_panel',
    [(-.142,-.305,1.25),(-.149,-.334,.78),(-.09,-.343,.735),
     (-.057,-.344,.795),(0,-.35,.648),(.057,-.344,.795),
     (.09,-.343,.735),(.149,-.334,.78),
     (.142,-.305,1.25)],'#88532d',bone='Hips'))
  legs.append(polygon(ctx,'back_leather_panel',
    [(.14,.30,1.25),(.155,.334,.855),(0,.35,.735),
     (-.155,.334,.855),(-.14,.30,1.25)],'#80502e',bone='Hips'))
  parts.append(part(ctx,'Leg','Gota Berserker fur kilt',legs))

  waist=band(source,[lambda p:p.z-1.235,lambda p:1.35-p.z],.09)
  belt=finish(ctx.collection,ctx.prefix+'belt',[(waist,0)],
              [material(ctx.prefix+'belt leather','#493e31')],'Body waist')
  bind(ctx,belt)
  parts.append(part(ctx,'Belt','Gota Berserker hexagon belt',
                    [belt,ringBuckle(ctx)]))

  strap=band(source,[lambda p:p.z-1.29,lambda p:1.94-p.z,
                    lambda p:.050-abs(p.x-.72*(p.z-1.57))],.031)
  body=finish(ctx.collection,ctx.prefix+'harness',[(strap,0)],
              [material(ctx.prefix+'harness leather','#493e31')],'Body chest')
  bind(ctx,body)
  wrists=band(source,[lambda p:abs(p.x)-.855,
                     lambda p:.985-abs(p.x)],.029)
  cuffs=finish(ctx.collection,ctx.prefix+'wrist_cuffs',[(wrists,0)],
               [material(ctx.prefix+'wrist iron','#3d3e46')],'Body forearms')
  bind(ctx,cuffs)
  for item in [body,cuffs,belt]:
    for face in item.data.polygons:
      face.use_smooth=False
  parts.append(part(ctx,'Chest','Gota Berserker harness',[body,cuffs]))

  vertices,faces=[],[]
  for z in [2.70,2.755]:
    for i in range(16):
      t=math.tau*i/16
      vertices.append((.514*math.sin(t),.02-.522*math.cos(t),z))
  for i in range(16):
    j=(i+1)%16
    faces.append((i,j,j+16,i+16))
  headband=mesh(ctx,'headband',vertices,faces,['#553b26'],bone='Head')
  crest=polygon(ctx,'gold_crest',[(0,-.566,3.055),(-.105,-.586,2.82),
                  (0,-.595,2.675),(.105,-.586,2.82)],'#efb633',
                  depth=.095,bone='Head')
  parts.append(part(ctx,'Headgear','Gota Berserker gold crest',
                    [headband,crest]))

  hair=duplicate(ctx,'Hair_12','mane',['#cb3519'])
  for item in hair:
    reduce(item,.23)
    bind(ctx,item)
  for i,(x,z) in enumerate([(-.68,2.18),(-.81,2.42),(-.77,2.71),
      (-.65,2.98),(-.40,3.22),(-.12,3.34),(.16,3.32),(.43,3.22),
      (.66,3.03),(.80,2.77),(.82,2.47),(.70,2.18)]):
    dz=z-2.62
    start=(x*.69,.02,2.62+dz*.64)
    hair.append(spike(ctx,'mane_spike_'+str(i),start,(x,-.035,z),
                .18,.24,'#db3e20' if i%2 else '#bd2f16'))
  parts.append(part(ctx,'Hair','Gota Berserker flame mane',hair))
  beard=duplicate(ctx,'Beard_09','beard',['#cb3519'])
  for item in beard:
    for vertex in item.data.vertices:
      if vertex.co.z<2.12:
        vertex.co.z=2.12+(vertex.co.z-2.12)*.63
    reduce(item,.42)
    bind(ctx,item)
  parts.append(part(ctx,'Beard','Gota Berserker pointed beard',beard))
  preset=dict(name='Berserker',group='Gota',pose='A_TPose',skin=11,
    skinRgb=[0.79, 0.56, 0.4],hairColor='Electric orange',pupilColor='Brown',parts=[
      dict(category='Eyes', item='06 Fierce'),
      dict(category='Mouth',item='03 Neutral'),
      dict(category='Brow', item='08 Stern')])
  return parts,preset
