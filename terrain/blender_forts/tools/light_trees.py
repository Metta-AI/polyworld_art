"""Build low-poly trunks and independently tintable alpha-card tree canopies."""

import hashlib
import math

import bpy
from mathutils import Vector

PreviewTints=[(.065,.29,.20,1),(.53,.77,.08,1),(1,.26,.025,1),(.31,.54,.055,1)]


def trunkGeometry(variant,branch,newGeometry):
  """Make a crooked wooden core with short boughs beneath the foliage shell."""
  geo=newGeometry()
  if variant==1:
    centers=[(0,0,0),(.035,0,.6),(-.045,.03,1.45),(.025,0,2.55),(0,0,3.45)]
    radii=[.43,.29,.21,.115,.035]
    height,rootCount,branchCount=3.45,4,0
  elif variant==2:
    centers=[(0,0,0),(.08,-.03,.45),(-.07,.03,1.03),(.04,0,1.83)]
    radii=[.36,.27,.17,.075]
    height,rootCount,branchCount=1.83,3,3
  elif variant==3:
    centers=[(0,0,0),(-.09,.01,.55),(.12,.04,1.18),(.03,.05,1.88),(-.12,.02,2.64)]
    radii=[.53,.37,.27,.16,.06]
    height,rootCount,branchCount=2.64,4,4
  else:
    centers=[(0,0,0),(.11,-.02,.72),(-.1,.06,1.48),(.05,.03,2.39),(.16,-.03,3.31)]
    radii=[.7,.5,.36,.24,.07]
    height,rootCount,branchCount=3.31,4,5
  branch(geo,centers,radii,4,'Crooked trunk')
  for i in range(branchCount):
    angle=i*2*math.pi/branchCount+.4+variant*.29
    x,y=math.cos(angle),math.sin(angle)
    base=height*(.4+.085*(i%3))
    reach=height*((.1 if variant==1 else .30)+.035*(i%2))
    points=[(0,0,base),(x*reach*.5,y*reach*.5,base+height*.18),
            (x*reach,y*reach,base+height*(.29+.035*(i%2)))]
    radius=radii[0]*(.43-.025*i)
    branch(geo,points,[radius,radius*.66,.025],3,'Wooden bough '+str(i+1))
  for i in range(rootCount):
    angle=i*2*math.pi/rootCount+.65
    x,y=math.cos(angle),math.sin(angle)
    reach=radii[0]*1.95
    branch(geo,[(x*.11,y*.11,.28),(x*reach,y*reach,.015)],
           [radii[0]*.48,.008],3,'Root '+str(i+1))
  floor=min(p[2] for p in geo['vertices'])
  geo['vertices']=[(x,y,z-floor) for x,y,z in geo['vertices']]
  return geo,branchCount,rootCount


def addCard(cards,anchor,angle,slope,size,tile,ring):
  """Point a square branch from its inner attachment outward and downhill."""
  tangent=Vector((-math.sin(angle),math.cos(angle),0))
  outward=Vector((math.cos(angle)*math.cos(slope),
                  math.sin(angle)*math.cos(slope),-math.sin(slope)))
  originV=.935 if tile>=12 else .73
  points=[anchor+tangent*(u-.5)*size+outward*(originV-v)*size
          for u,v in [(0,0),(1,0),(1,1),(0,1)]]
  start=len(cards['vertices'])
  cards['vertices'].extend(tuple(p) for p in points)
  cards['faces'].append((start,start+1,start+2,start+3))
  cards['tiles'].append(tile)
  cards['rings'].append(ring)


def foliageGeometry(variant):
  """Overlap irregular radial rings, with light crowns and darker lower rings."""
  cards={'vertices':[],'faces':[],'tiles':[],'rings':[],'profile':[]}
  if variant==1:
    rings=[(4.1,.025,.95,7,0),(3.6,.28,1.40,10,1),
           (3.07,.50,1.70,13,1),(2.54,.75,2.00,17,2),
           (2.04,.99,2.30,22,3)]
    for ring,(z,radius,size,count,tone) in enumerate(rings):
      for index in range(count):
        angle=2*math.pi*index/count+ring*.39+variant*.31
        angle+=.13*math.sin(index*2.3+ring)*2*math.pi/count
        r=radius*(1+.065*math.sin(index*1.7+ring))
        anchor=Vector((math.cos(angle)*r,math.sin(angle)*r,
                       z+.025*math.sin(index*2.1+ring)))
        slope=math.radians(60+2.3*math.sin(index*1.9+ring))
        scale=size*(1+.065*math.sin(index*2.7+ring))
        addCard(cards,anchor,angle,slope,scale,12+tone,ring)
      cards['profile'].append({'ring':ring,'height':z,'radius':radius,
                               'quads':count,'tone':tone})
  else:
    center,radius,height,counts={
      2:(1.77,.95,.85,[6,8,11,14]),
      3:(2.42,1.35,1.20,[7,11,15,19]),
      4:(3.15,1.70,1.55,[8,12,16,19])}[variant]
    for ring,(theta,factor,pitch,count) in enumerate(zip(
        [.025,.42,.82,1.24],[.67,.82,.96,1.05],[8,24,46,68],counts)):
      r=radius*math.sin(theta)
      z=center+height*math.cos(theta)
      for index in range(count):
        angle=2*math.pi*index/count+ring*.37+variant*.41
        angle+=.12*math.sin(index*2.1+ring)*2*math.pi/count
        reach=r*(1+.055*math.sin(index*2.4+variant+ring))
        anchor=Vector((math.cos(angle)*reach,math.sin(angle)*reach,
                       z+.02*height*math.sin(index*1.7+ring)))
        slope=math.radians(pitch+2*math.sin(index*2.4+ring))
        size=radius*factor*1.25*(1+.08*math.sin(index*2.7+ring+variant))
        tile=(4 if (index+ring+variant)%2 else 8)+ring
        addCard(cards,anchor,angle,slope,size,tile,ring)
      cards['profile'].append({'ring':ring,'height':z,'radius':r,
                               'quads':count,'tone':ring})
  return cards


def treeMaterial(image,foliage,variant):
  """Use the original atlas, with a white tint factor and masked alpha leaves."""
  name='Tree foliage '+str(variant) if foliage else 'Tree bark'
  if not foliage and name in bpy.data.materials:
    return bpy.data.materials[name]
  material=bpy.data.materials.new(name)
  material.use_nodes=True
  material.use_backface_culling=False
  shader=material.node_tree.nodes.get('Principled BSDF')
  shader.inputs['Roughness'].default_value=.9
  shader.inputs['Specular IOR Level'].default_value=.12
  texture=material.node_tree.nodes.new('ShaderNodeTexImage')
  texture.name='Tree atlas'
  texture.image=image
  texture.extension='EXTEND'
  texture.interpolation='Linear'
  if foliage:
    tint=material.node_tree.nodes.new('ShaderNodeMixRGB')
    tint.name='Engine tint'
    tint.blend_type='MULTIPLY'
    tint.inputs[0].default_value=1
    tint.inputs[2].default_value=(1,1,1,1)
    material.node_tree.links.new(texture.outputs['Color'],tint.inputs[1])
    material.node_tree.links.new(tint.outputs[0],shader.inputs['Base Color'])
    alpha=material.node_tree.nodes.new('ShaderNodeMath')
    alpha.operation='GREATER_THAN'
    alpha.inputs[1].default_value=.45
    material.node_tree.links.new(texture.outputs['Alpha'],alpha.inputs[0])
    material.node_tree.links.new(alpha.outputs[0],shader.inputs['Alpha'])
    material['preview_tint']=PreviewTints[variant-1]
  else:
    material.node_tree.links.new(texture.outputs['Color'],shader.inputs['Base Color'])
  material['license']='generated'
  material['tintable']=foliage
  return material


def atlasMesh(geo,name,material,collection,root,foliage):
  """Make a separate trunk or leaf-card mesh with an explicit atlas UV layer."""
  mesh=bpy.data.meshes.new(name)
  mesh.from_pydata(geo['vertices'],[],geo['faces'])
  mesh.update()
  obj=bpy.data.objects.new(name,mesh)
  collection.objects.link(obj)
  obj.parent=root
  mesh.materials.append(material)
  uv=mesh.uv_layers.new(name='TreeUV')
  attribute=mesh.attributes.new('tree_atlas_tile','INT','FACE')
  if foliage:
    ringAttribute=mesh.attributes.new('foliage_ring','INT','FACE')
    ringGroups={ring:obj.vertex_groups.new(name='Ring '+str(ring+1).zfill(2))
                for ring in sorted(set(geo['rings']))}
  groups={part:obj.vertex_groups.new(name=part) for part in dict.fromkeys(geo.get('parts',[]))}
  for index,polygon in enumerate(mesh.polygons):
    tile=geo['tiles'][index] if foliage else index%4
    row,column=divmod(tile,4)
    attribute.data[index].value=tile
    if foliage:
      ring=geo['rings'][index]
      ringAttribute.data[index].value=ring
      ringGroups[ring].add(list(polygon.vertices),1,'REPLACE')
    coordinates=([(0,0),(1,0),(1,1),(0,1)] if foliage else
                 geo['uvs'][index] or
                 ([(0,0),(1,0),(1,1),(0,1)] if len(polygon.vertices)==4 else
                  [(0,0),(1,0),(.5,1)]))
    for loop,(u,v) in zip(polygon.loop_indices,coordinates):
      uv.data[loop].uv=((column*512+8+u*496)/2048,
                        1-((row+1)*512-8-v*496)/2048)
    if not foliage:
      groups[geo['parts'][index]].add(list(polygon.vertices),1,'REPLACE')
  obj['license']='generated'
  obj['part']=name
  obj['atlas_kind']='tree_foliage'
  obj['texture_atlas']='tree_foliage_atlas.png'
  return obj


def createLightTree(variant,directory,scene,parent,image,branch,newGeometry):
  """Export one two-mesh light tree with a neutral canopy ready for engine tint."""
  name='tree_'+str(variant)
  collection=bpy.data.collections.new('Light Tree '+str(variant))
  parent.children.link(collection)
  root=bpy.data.objects.new('light_'+name,None)
  collection.objects.link(root)
  wood,branchCount,rootCount=trunkGeometry(variant,branch,newGeometry)
  cards=foliageGeometry(variant)
  trunk=atlasMesh(wood,'trunk',treeMaterial(image,False,variant),collection,root,False)
  foliage=atlasMesh(cards,'foliage',treeMaterial(image,True,variant),collection,root,True)
  for obj in [trunk,foliage]:
    obj.data.calc_loop_triangles()
  trunkCount=len(trunk.data.loop_triangles)
  leafCount=len(foliage.data.loop_triangles)
  count=trunkCount+leafCount
  assert count<250,(name,count)
  root['license']='generated'
  root['triangles']=count
  root['reference']='references/light_tree_styles.png'
  collection['triangles']=count
  bpy.ops.object.select_all(action='DESELECT')
  trunk.select_set(True)
  foliage.select_set(True)
  bpy.context.view_layer.objects.active=trunk
  target=directory/'models/light'/(name+'.glb')
  bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',use_selection=True,
    export_apply=True,export_texcoords=True,export_normals=True,
    export_materials='EXPORT',export_extras=True)
  for obj in [trunk,foliage]:
    obj.name='light_'+name+' / '+obj['part']
  root.location=(22+((variant-1)%2)*5.5,-((variant-1)//2)*6,0)
  points=wood['vertices']+cards['vertices']
  shape={'variant':variant,'kind':'evergreen' if variant==1 else 'leafy',
         'branches':branchCount,'roots':rootCount,'foliage_quads':len(cards['faces']),
         'trunk_triangles':trunkCount,'foliage_triangles':leafCount,
         'foliage_rings':len(cards['profile']),'ring_profile':cards['profile'],
         'layering':'Staggered radial rings. Branches point outward and down; lower rings use darker tiles.',
         'dimensions':[round(max(p[i] for p in points)-min(p[i] for p in points),4)
                       for i in range(3)]}
  print('TRIANGLES light',name,count,shape,flush=True)
  return {'faction':'light','asset':name,'triangles':count,'file':str(target.relative_to(directory)),
          'symmetry':'asymmetric trunk and individually oriented foliage quads',
          'license':'generated','texture':'textures/tree_foliage_atlas.png',
          'reference':'references/light_tree_styles.png','attachments':[],
          'foliage':shape,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
          'objects':[trunk,foliage],'collection':collection,'root':root}


def setPreviewTints(assets,enabled):
  """Apply example colors for renders and restore white before saving or export."""
  for asset in assets:
    if 'foliage' not in asset:
      continue
    material=asset['objects'][1].data.materials[0]
    material.node_tree.nodes['Engine tint'].inputs[2].default_value=(
      material['preview_tint'] if enabled else (1,1,1,1))
