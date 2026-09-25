"""Build Hades' modular solid-color garments on the existing Polyworld rig."""

import math

import bpy
from mathutils import Vector

from clothes import bodySurface, clip, offset, material, meshObject
from gota_common import bind, duplicate, mesh, part, smooth
from gota_death_knight import plate, diamond

Black = '#27292D'
Edge = '#41444B'
Gold = '#D2A448'
GoldLight = '#F2CA6D'
GoldDark = '#9B6B2A'
Red = '#681E2B'
RedLight = '#8C2938'
Green = '#12AA60'
Hair = '#202226'


def shell(ctx, suffix, source, cuts, amount, color):
  """Reuse shared fitted surfaces and weights for a smooth garment shell."""
  surface = bodySurface(source)
  for cut in cuts:
    surface = clip(surface, cut)
  surface = offset(surface, amount)
  obj = meshObject(ctx.collection, ctx.prefix + suffix, [(surface, 0)],
    [material(ctx.prefix + suffix + 'Color', color)])
  bind(ctx, obj)
  return smooth(obj, 55)


def tube(ctx, suffix, points, radii, color, bone, sides=10):
  """Sweep a closed rounded solid tube through tapered control rings."""
  points = [Vector(p) for p in points]
  vertices, faces = [], []
  for i, (p, radius) in enumerate(zip(points, radii)):
    tangent = (points[min(i + 1, len(points)-1)] -
      points[max(0, i-1)]).normalized()
    across = tangent.cross(Vector((0, 1, 0))).normalized()
    if across.length < .1:
      across = tangent.cross(Vector((1, 0, 0))).normalized()
    other = tangent.cross(across).normalized()
    for j in range(sides):
      angle = j * math.tau / sides
      vertices.append(p + radius * (across * math.cos(angle) +
        other * math.sin(angle)))
    if i:
      for j in range(sides):
        a, b = (i-1)*sides+j, (i-1)*sides+(j+1)%sides
        faces.append((a, b, b+sides, a+sides))
  faces += [tuple(reversed(range(sides))),
    tuple(range(len(vertices)-sides, len(vertices)))]
  return smooth(mesh(ctx, suffix, vertices, faces, [color], bone=bone), 55)


def band(ctx, suffix, rows, color, bone, sides=24):
  """Build a thick open elliptical band with a rounded cross section."""
  vertices, faces = [], []
  for z, rx, ry in rows:
    for j in range(sides):
      angle = math.tau*j/sides
      dip=.10*max(0,math.cos(angle))**8 if suffix=='CrownBand' else 0
      vertices.append((rx*math.sin(angle), .02-ry*math.cos(angle), z-dip))
  for row in range(len(rows)):
    for j in range(sides):
      a, b = row*sides+j, row*sides+(j+1)%sides
      nextRow = (row+1)%len(rows)
      faces.append((a, b, nextRow*sides+(j+1)%sides, nextRow*sides+j))
  return smooth(mesh(ctx, suffix, vertices, faces, [color], bone=bone))


def gem(ctx, suffix, center, width, height, color=Green, bone='Head'):
  """Set a deep faceted emerald in a raised gold diamond frame."""
  x, y, z = center
  return [diamond(ctx, suffix+'Frame', center, width, height, Gold, bone),
    diamond(ctx, suffix+'Stone', (x,y-.06,z), width*.68, height*.72,
      color, bone)]


def crown(ctx):
  """Build a complete curved obsidian circlet with tall dimensional spikes."""
  result = [band(ctx, 'CrownBand', [(2.91,.55,.53),(3.01,.56,.54),
    (3.055,.54,.52),(3.045,.505,.485),(2.925,.505,.485)], Black, 'Head')]
  for i, (angle, height, width) in enumerate([(0,.59,.12),
      (-.57,.43,.105),(.57,.43,.105),(-1.1,.31,.09),(1.1,.31,.09),
      (-1.65,.25,.075),(1.65,.25,.075),(2.3,.28,.085),
      (-2.3,.28,.085),(math.pi,.36,.10)]):
    dip=.09*max(0,math.cos(angle))**8
    center=Vector((.545*math.sin(angle),.02-.525*math.cos(angle),3.0-dip))
    height+=dip
    tangent=Vector((math.cos(angle),math.sin(angle),0))
    radial=Vector((math.sin(angle),-math.cos(angle),0))
    vertices=[center+tangent*width, center+radial*.08,
      center-tangent*width, center-radial*.065,
      center+radial*.015+Vector((0,0,height))]
    result.append(mesh(ctx,'CrownSpike'+str(i),vertices,
      [(0,1,4),(1,2,4),(2,3,4),(3,0,4),(3,2,1,0)],
      [Black,Edge],bone='Head'))
    result[-1].data.polygons[1].material_index=1
  result += gem(ctx,'CrownEmerald',(0,-.583,3.13),.095,.155)
  for sign in [-1,1]:
    result.append(diamond(ctx,'CrownGold'+str(sign),
      (sign*.29,-.448,3.10),.048,.14,Gold,'Head'))
  return result


def hair(ctx):
  """Reuse the fitted mane and add swept pointed side locks."""
  result=duplicate(ctx,'Hair_12','Hair',[Hair])
  for obj in result:
    bpy.context.view_layer.objects.active=obj
    dec=obj.modifiers.new('Broad sculpted locks','DECIMATE')
    dec.ratio=.48
    bpy.ops.object.modifier_apply(modifier=dec.name)
    smooth(obj,30)
  for sign in [-1,1]:
    for i,(z,endz) in enumerate([(2.82,2.68),(2.62,2.39),(2.40,2.15)]):
      result.append(tube(ctx,'SweptLock'+str(sign)+str(i),
        [(sign*.39,-.15,z+.1),(sign*.51,-.20,z),
         (sign*.61,-.21,endz),(sign*.72,-.23,endz+.045)],
        [.14,.16,.08,.007],Hair,'Head',7))
  return result


def beard(ctx):
  """Reuse the fitted full beard and shorten it to a pointed underworld beard."""
  result=duplicate(ctx,'Beard_09','Beard',[Hair])
  for obj in result:
    for v in obj.data.vertices:
      if v.co.z<2.16:
        v.co.z=2.16+(v.co.z-2.16)*.68
      v.co.x*=.9
    bpy.context.view_layer.objects.active=obj
    dec=obj.modifiers.new('Broad beard facets','DECIMATE')
    dec.ratio=.6
    bpy.ops.object.modifier_apply(modifier=dec.name)
    smooth(obj,28)
  return result


def pauldrons(ctx):
  """Wrap gold-rimmed pauldrons around the upper arms with real curved depth."""
  result=[]
  for sign,side in [(-1,'Right'),(1,'Left')]:
    verts,faces,shades=[],[],[]
    rows=[(.29,.16,.20),(.325,.19,.23),(.605,.24,.245),(.65,.245,.22)]
    sides=13
    for x,ry,rz in rows:
      for j in range(sides):
        t=-math.pi*.64+j/(sides-1)*math.pi*1.28
        lift=(x-.29)*.38
        outward=x+.025*math.cos(t)
        verts.append((sign*outward,ry*math.sin(t),
          1.78+rz*math.cos(t)+lift))
    for r in range(1,len(rows)):
      for j in range(sides-1):
        a=(r-1)*sides+j
        faces.append((a,a+1,a+1+sides,a+sides))
        shades.append(1 if r in [1,3] or j in [0,11] else 0)
    obj=mesh(ctx,'Pauldron'+side,verts,faces,[Black,Gold],bone=side+'Arm')
    for face,index in zip(obj.data.polygons,shades):
      face.material_index=index
    bpy.context.view_layer.objects.active=obj
    mod=obj.modifiers.new('Armor thickness','SOLIDIFY')
    mod.thickness=.035
    bpy.ops.object.modifier_apply(modifier=mod.name)
    result.append(smooth(obj,35))
    result.append(diamond(ctx,'ShoulderStud'+side,
      (sign*.46,-.24,1.95),.054,.061,GoldLight,side+'Arm'))
  return result


def chest(ctx):
  """Build a fitted dark cuirass, burgundy collar, shoulders and round bracers."""
  result=[shell(ctx,'Cuirass',[ctx.body],
    [lambda p:p.z-1.30,lambda p:1.95-p.z,
     lambda p:max(.32-abs(p.x),1.57-p.z)],.055,Black)]
  for sign in [-1,1]:
    result.append(plate(ctx,'Breastplate'+str(sign),
      [(sign*.02,-.315,1.88),(sign*.27,-.27,1.84),
       (sign*.29,-.307,1.60),(sign*.04,-.372,1.50)],Edge,.025))
    result.append(plate(ctx,'Collar'+str(sign),
      [(sign*.01,-.235,1.92),(sign*.32,-.145,1.985),
       (sign*.31,-.292,1.85),(0,-.37,1.745)],Red,.025,'Spine2'))
  result += gem(ctx,'ChestEmerald',(0,-.405,1.736),.075,.105,
    bone='Spine2')
  result += pauldrons(ctx)
  for sign,side in [(-1,'Right'),(1,'Left')]:
    points=[(sign*x,.015,1.78) for x in [.745,.765,.96,.985]]
    result.append(tube(ctx,'Bracer'+side,points,
      [.135,.147,.116,.108],Black,side+'ForeArm',16))
    for i,(a,b,r) in enumerate([(.742,.777,.151),(.943,.982,.124)]):
      result.append(tube(ctx,'BracerGold'+side+str(i),
        [(sign*a,.015,1.78),(sign*b,.015,1.78)],
        [r,r],Gold,side+'ForeArm',16))
    result += gem(ctx,'BracerEmerald'+side,
      (sign*.855,-.127,1.78),.047,.062,bone=side+'ForeArm')
  return result


def skull(ctx):
  """Construct a recognizable gold skull relief with recessed dark eye sockets."""
  result=[plate(ctx,'SkullCranium',
    [(-.105,-.39,1.37),(-.15,-.39,1.31),(-.143,-.40,1.21),
     (-.09,-.425,1.17),(-.085,-.44,1.09),(0,-.445,1.055),
     (.085,-.44,1.09),(.09,-.425,1.17),(.143,-.40,1.21),
     (.15,-.39,1.31),(.105,-.39,1.37)],Gold,.065,'Spine')]
  for sign in [-1,1]:
    result.append(plate(ctx,'SkullSocket'+str(sign),
      [(sign*.022,-.47,1.278),(sign*.108,-.451,1.30),
       (sign*.10,-.465,1.234),(sign*.036,-.48,1.231)],Black,.003,'Spine'))
    result.append(diamond(ctx,'SkullSoul'+str(sign),
      (sign*.065,-.488,1.257),.014,.012,'#4F842B','Spine'))
  result.append(plate(ctx,'SkullNose',
    [(0,-.503,1.22),(-.025,-.486,1.175),(.025,-.486,1.175)],
    Black,.004,'Spine'))
  for i in [-2,-1,0,1,2]:
    x=i*.023
    result.append(plate(ctx,'SkullTooth'+str(i),
      [(x-.008,-.465,1.15),(x+.008,-.465,1.15),
       (x+.007,-.463,1.105),(x-.007,-.463,1.105)],GoldLight,.01,'Spine'))
  return result


def belt(ctx):
  """Build a complete waist belt and skull buckle with gold side mounts."""
  result=[shell(ctx,'Belt',[ctx.body],
    [lambda p:p.z-1.225,lambda p:1.355-p.z],.078,Black)]
  for z in [1.23,1.34]:
    result.append(shell(ctx,'BeltGold'+str(z),[ctx.body],
      [lambda p,h=z:p.z-h,lambda p,h=z:h+.025-p.z],.092,Gold))
  for sign in [-1,1]:
    result.append(plate(ctx,'BuckleWing'+str(sign),
      [(sign*.12,-.35,1.35),(sign*.225,-.322,1.35),
       (sign*.25,-.32,1.22),(sign*.135,-.36,1.21)],Gold,.03,'Spine'))
  return result+skull(ctx)


def tabardPanel(ctx, suffix, y):
  """Share black cloth and its gold perimeter in one deforming closed surface."""
  side=-1 if y<0 else 1
  outer=[(-.147,y,1.285),(.147,y,1.285),(.177,y*1.09,.665),
    (0,y*1.12,.49),(-.177,y*1.09,.665)]
  inner=[(-.116,y,1.265),(.116,y,1.265),(.139,y*1.09,.683),
    (0,y*1.12,.555),(-.139,y*1.09,.683)]
  middle=sum((Vector(p) for p in inner),Vector())/5
  vertices=outer+inner+[middle]
  vertices += [(x,depth-side*.016,z) for x,depth,z in outer]
  vertices.append(middle-Vector((0,side*.016,0)))
  faces,shades=[],[]
  for i in range(5):
    j=(i+1)%5
    faces.extend([(i,j,5+j,5+i),(5+i,5+j,10),
      (11+j,11+i,16),(i,11+i,11+j,j)])
    shades.extend([0,1,1,0])
  obj=mesh(ctx,suffix,vertices,faces,[Gold,Black],bone='Hips')
  for face,index in zip(obj.data.polygons,shades):
    face.material_index=index
  return obj


def legs(ctx):
  """Make split burgundy side skirts and a long black gold-bordered tabard."""
  result=duplicate(ctx,'Clothing_09','Trousers',[Black]*5)
  for obj in list(result):
    if max(v.co.z for v in obj.data.vertices)<.61:
      result.remove(obj)
      bpy.data.objects.remove(obj,do_unlink=True)
    else:
      smooth(obj)
  for sign,side in [(-1,'Right'),(1,'Left')]:
    for back in [False,True]:
      y=.27 if back else -.285
      vertices=[(sign*.12,y,1.29),(sign*.32,y*.84,1.3),
        (sign*.46,y*.80,.82),(sign*.35,y*1.15,.62),
        (sign*.255,y*1.20,.74),(sign*.18,y*1.10,.68)]
      result.append(plate(ctx,'Skirt'+side+str(back),vertices,
        RedLight if back else Red,.025,side+'UpLeg'))
      result.append(plate(ctx,'HipPlateGold'+side+str(back),
        [(sign*.18,y*1.10,1.24),(sign*.34,y*.93,1.23),
         (sign*.395,y*1.11,1.04),(sign*.205,y*1.19,1.02)],
        Gold,.014,'Hips'))
      result.append(plate(ctx,'HipPlate'+side+str(back),
        [(sign*.20,y*1.20,1.215),(sign*.32,y*1.02,1.208),
         (sign*.365,y*1.20,1.063),(sign*.227,y*1.29,1.047)],
        Black,.008,'Hips'))
  for back in [False,True]:
    result.append(tabardPanel(ctx,'Tabard'+str(back),
      .37 if back else -.37))
  for sign in [-1,1]:
    result.append(diamond(ctx,'TabardMark'+str(sign),
      (sign*.062,-.46,.69),.025,.065,Gold,'Hips'))
  for obj in result:
    if 'Tabard' in obj.name:
      for vertex in obj.data.vertices:
        p=vertex.co
        side=-1 if p.y<0 else 1
        target=.155+.12*max(0,min(1,(p.z-.5)/.8))
        p.y=side*(target+(abs(p.y)-.37)*.35)
      obj.vertex_groups.clear()
      for vertex in obj.data.vertices:
        p=vertex.co
        amount=max(0,min(1,(1.23-p.z)/.72))*.88
        left=max(0,min(1,.5+p.x/.30))
        influences={'Hips':1-amount,'LeftUpLeg':amount*left,
          'RightUpLeg':amount*(1-left)}
        for name,value in influences.items():
          group=obj.vertex_groups.get(name) or obj.vertex_groups.new(name=name)
          group.add([vertex.index],value,'REPLACE')
      bind(ctx,obj)
  return result


def boots(ctx):
  """Add gold-edged shin guards and green knee stones to fitted dark boots."""
  result=duplicate(ctx,'Clothing_15','Boots',[Black,GoldDark,Black,Gold,Black])
  for obj in result:
    bpy.context.view_layer.objects.active=obj
    dec=obj.modifiers.new('Keep rounded boot silhouette','DECIMATE')
    dec.ratio=.63
    bpy.ops.object.modifier_apply(modifier=dec.name)
    smooth(obj,50)
  for sign,side in [(-1,'Right'),(1,'Left')]:
    x=sign*.205
    result.append(plate(ctx,'GreaveGold'+side,
      [(x-.12,-.175,.58),(x,-.19,.70),(x+.12,-.175,.58),
       (x+.10,-.20,.26),(x,-.25,.20),(x-.10,-.20,.26)],Gold,.03))
    result.append(plate(ctx,'Greave'+side,
      [(x-.086,-.218,.57),(x,-.25,.646),(x+.086,-.218,.57),
       (x+.065,-.238,.29),(x,-.29,.254),(x-.065,-.238,.29)],Black,.026))
    result+=gem(ctx,'KneeEmerald'+side,(x,-.27,.56),.073,.099,
      bone=side+'Leg')
    result.append(plate(ctx,'ToeGold'+side,
      [(x-.103,-.29,.085),(x-.094,-.283,.17),
       (x,-.32,.212),(x+.094,-.283,.17),(x+.103,-.29,.085)],Gold,.025))
  for obj in result:
    if not obj.name.startswith(ctx.prefix+'Boots'):
      for vertex in obj.data.vertices:
        vertex.co.y=-.15+(vertex.co.y+.18)*.5
  return result


def cape(ctx):
  """Make a wide burgundy cape with soft folds, back depth and pointed split hem."""
  vertices,faces,shades,weights=[],[],[],[]
  columns=25
  for row in range(7):
    t=row/6
    for i in range(columns):
      s=i/(columns-1)*2-1
      width=.35+.43*t
      x=s*width
      y=.245+.30*t+.06*math.cos(s*math.pi*3)*(.3+.7*t)
      z=1.93-1.43*t
      z-=.12*t**5*(1-abs(math.sin(s*math.pi*3)))
      y+=.065*(1-s*s)
      vertices.append((x,y,z))
      hip=min(1,t*1.75)
      weights.append({'Spine2':1-hip,'Hips':hip})
      if row and i:
        a=(row-1)*columns+i-1
        faces.append((a,a+1,a+1+columns,a+columns))
        shades.append(1 if math.cos(s*math.pi*3)>0 else 0)
  obj=mesh(ctx,'Cape',vertices,faces,[Red,RedLight],weights=weights)
  for face,index in zip(obj.data.polygons,shades):
    face.material_index=index
  bpy.context.view_layer.objects.active=obj
  mod=obj.modifiers.new('Heavy cloth thickness','SOLIDIFY')
  mod.thickness=.022
  bpy.ops.object.modifier_apply(modifier=mod.name)
  smooth(obj,65)
  return [obj]


def build(ctx):
  """Build modular clothing and equipment while reusing shared body and eyes."""
  from gota_hades_equipment import build as equipment
  parts=[part(ctx,'Headgear','Gota Hades obsidian crown',crown(ctx)),
    part(ctx,'Hair','Gota Hades swept hair',hair(ctx)),
    part(ctx,'Beard','Gota Hades pointed beard',beard(ctx)),
    part(ctx,'Chest','Gota Hades royal armor',chest(ctx)),
    part(ctx,'Belt','Gota Hades skull belt',belt(ctx)),
    part(ctx,'Leg','Gota Hades layered skirt',legs(ctx)),
    part(ctx,'Foot','Gota Hades armored boots',boots(ctx)),
    part(ctx,'Back','Gota Hades burgundy cape',cape(ctx))]
  parts+=equipment(ctx)
  preset=dict(name='Hades',group='Gota Gods',pose='A_TPose',skin=16,
    skinRgb=[.72,.61,.59],hairColor='Jet black',pupilColor='Green',parts=[
      dict(category='Eyes',item='06 Fierce'),
      dict(category='Mouth',item='03 Neutral'),
      dict(category='Brow',item='08 Stern'),
      dict(category='Nose',item='Tiny')])
  return parts,preset
