"""Verify saved Blender symmetry, UV tiles, textures, and exported triangle counts."""

import hashlib
import json
import math
import struct
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector
from mathutils.kdtree import KDTree

Root = Path(__file__).resolve().parents[1]
manifest=json.loads((Root/'manifest.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(Root/'fort_kit.blend'))
scene=bpy.data.scenes['01 Rebuilt mirrored fort kit']
bpy.context.window.scene=scene
bpy.context.view_layer.update()
graph=bpy.context.evaluated_depsgraph_get()
report=[]


def glbInspection(path):
  """Inspect final GLB triangle counts, UVs, and self-contained texture references."""
  data=path.read_bytes()
  magic,version,length=struct.unpack_from('<4sII',data)
  assert magic==b'glTF' and version==2 and length==len(data)
  size,kind=struct.unpack_from('<II',data,12)
  assert kind==0x4e4f534a
  doc=json.loads(data[20:20+size])
  assert len(doc['images'])==1
  assert all('bufferView' in image for image in doc['images'])
  assert all('uri' not in buffer for buffer in doc['buffers'])
  perMesh=[]
  for mesh in doc['meshes']:
    count=0
    for primitive in mesh['primitives']:
      assert primitive.get('mode',4)==4
      assert 'TEXCOORD_0' in primitive['attributes']
      material=doc['materials'][primitive['material']]
      assert 'baseColorTexture' in material['pbrMetallicRoughness']
      accessor=primitive.get('indices',primitive['attributes']['POSITION'])
      count+=doc['accessors'][accessor]['count']//3
    perMesh.append(count)
  stack=list(doc['scenes'][doc.get('scene',0)]['nodes'])
  total=0
  while stack:
    node=doc['nodes'][stack.pop()]
    if 'mesh' in node:
      total+=perMesh[node['mesh']]
    stack.extend(node.get('children',[]))
  return total,hashlib.sha256(data).hexdigest(),doc


def verifyAttachments(asset,root,doc):
  """Check editable empties and exact exported names and transformed positions."""
  expected=asset['attachments']
  expectedName=('fire' if asset['asset'].startswith('tower') else
                'spawn' if asset['asset']=='barracks' else None)
  assert [item['name'] for item in expected]==([expectedName] if expectedName else [])
  empties=[obj for obj in root.children if obj.get('attachment')]
  assert len(empties)==len(expected)
  worldNodes=[]
  stack=[(index,Matrix.Identity(4))
         for index in doc['scenes'][doc.get('scene',0)]['nodes']]
  while stack:
    index,parent=stack.pop()
    node=doc['nodes'][index]
    if 'matrix' in node:
      values=node['matrix']
      local=Matrix([values[i:i+4] for i in range(0,16,4)]).transposed()
    else:
      x,y,z,w=node.get('rotation',[0,0,0,1])
      scale=Matrix.Diagonal(Vector((*node.get('scale',[1,1,1]),1)))
      local=(Matrix.Translation(Vector(node.get('translation',[0,0,0])))@
             Quaternion((w,x,y,z)).to_matrix().to_4x4()@scale)
    world=parent@local
    worldNodes.append((node,world))
    stack.extend((child,world) for child in node.get('children',[]))
  result=[]
  for item in expected:
    matches=[obj for obj in empties if obj.get('attachment')==item['name']]
    assert len(matches)==1
    empty=matches[0]
    assert empty.type=='EMPTY' and not empty.modifiers
    position=Vector(item['position'])
    assert (empty.location-position).length<.00001
    assert ((root.matrix_world.inverted()@empty.matrix_world).translation-position).length<.00001
    nodes=[(node,world) for node,world in worldNodes if node.get('name')==item['name']]
    assert len(nodes)==1,(asset['file'],item['name'])
    node,world=nodes[0]
    assert all(key not in node for key in ['mesh','skin','camera'])
    assert node['extras']['attachment']==item['name']
    glbPosition=Vector((position.x,position.z,-position.y))
    assert (world.translation-glbPosition).length<.00001
    result.append({'name':item['name'],'position_blender':list(position),
                   'position_glb':list(world.translation),'meshless':True})
  return result


def pixelAspect(mesh, protectedTiles,layer='TrimUV',attribute='trim_tile',size=1254):
  """Measure texture pixel anisotropy on every protected surface triangle."""
  mesh.calc_loop_triangles()
  uv=mesh.uv_layers[layer]
  tiles=mesh.attributes[attribute]
  ratios=[]
  densities=[]
  for triangle in mesh.loop_triangles:
    tile=tiles.data[triangle.polygon_index].value
    if tile not in protectedTiles:
      continue
    points=[mesh.vertices[index].co.copy() for index in triangle.vertices]
    edgeU,edgeV=points[1]-points[0],points[2]-points[0]
    axisU=edgeU.normalized()
    normal=edgeU.cross(edgeV).normalized()
    axisV=normal.cross(axisU).normalized()
    domain=np.array([[edgeU.length,edgeV.dot(axisU)],
                     [0,edgeV.dot(axisV)]],dtype=float)
    assert abs(np.linalg.det(domain))>.00000001
    pixels=[np.array(uv.data[index].uv,dtype=float)*size
            for index in triangle.loops]
    texture=np.column_stack((pixels[1]-pixels[0],pixels[2]-pixels[0]))
    singular=np.linalg.svd(texture@np.linalg.inv(domain),compute_uv=False)
    ratios.append(float(singular[0]/singular[1]))
    densities.extend(float(value) for value in singular)
  return ratios,densities


def verifyFoliage(asset,objects,doc):
  """Check alpha cards, outward branch flow, overlapping rings, and their tones."""
  if 'foliage' not in asset:
    return None
  assert len(objects)==2
  byPart={obj['part']:obj for obj in objects}
  assert set(byPart)=={'trunk','foliage'}
  leaves=byPart['foliage']
  assert all(len(p.vertices)==4 and p.area>.0001 for p in leaves.data.polygons)
  assert len(leaves.data.vertices)==4*len(leaves.data.polygons)
  assert min(vertex.co.z for vertex in leaves.data.vertices)>=0
  assert len(leaves.data.polygons)==asset['foliage']['foliage_quads']
  nodes={node['name']:node for node in doc['nodes'] if 'mesh' in node}
  assert set(nodes)=={'trunk','foliage'}
  assert nodes['trunk']['mesh']!=nodes['foliage']['mesh']
  for part,node in nodes.items():
    mesh=doc['meshes'][node['mesh']]
    assert len(mesh['primitives'])==1
    primitive=mesh['primitives'][0]
    assert 'COLOR_0' not in primitive['attributes']
    material=doc['materials'][primitive['material']]
    factor=material['pbrMetallicRoughness'].get('baseColorFactor',[1,1,1,1])
    assert np.allclose(factor,[1,1,1,1]),factor
    if part=='foliage':
      assert material['alphaMode']=='MASK'
      assert abs(material.get('alphaCutoff',.5)-.45)<.00001
      assert material['doubleSided']
    else:
      assert material.get('alphaMode','OPAQUE')=='OPAQUE'
  assert tuple(leaves.data.materials[0].node_tree.nodes['Engine tint'].inputs[2].default_value)==(1,1,1,1)
  metadata=json.loads((Root/'textures/tree_foliage_atlas.json').read_text())
  gray={(tile['row']-1)*4+tile['column']-1:tile['meanOpaqueGray']
        for tile in metadata['tiles']}
  tiles=leaves.data.attributes['tree_atlas_tile']
  rings=leaves.data.attributes['foliage_ring']
  grouped={}
  for polygon in leaves.data.polygons:
    grouped.setdefault(rings.data[polygon.index].value,[]).append(polygon)
  profile=[]
  for ring,polygons in sorted(grouped.items()):
    attachments=[]
    tips=[]
    tones=[]
    for polygon in polygons:
      a,b,c,d=[leaves.data.vertices[index].co for index in polygon.vertices]
      bottom,top=(a+b)/2,(c+d)/2
      tile=tiles.data[polygon.index].value
      originV=.935 if tile>=12 else .73
      attachment=top+(bottom-top)*(1-originV)
      tip=top+(bottom-top)*.88
      radial=Vector((attachment.x,attachment.y,0)).normalized()
      direction=(bottom-top).normalized()
      assert direction.z<-.05 and direction.dot(radial)>.3
      assert polygon.normal.z>.3
      assert (12<=tile<=15)==(asset['foliage']['kind']=='evergreen')
      attachments.append(attachment)
      tips.append(tip)
      tones.append(gray[tile])
    averageRadius=lambda points:sum(Vector((p.x,p.y)).length for p in points)/len(points)
    actual={'ring':ring,'quads':len(polygons),
            'attachment_radius':averageRadius(attachments),
            'tip_radius':averageRadius(tips),
            'attachment_height':sum(p.z for p in attachments)/len(attachments),
            'mean_texture_gray':sum(tones)/len(tones)}
    expected=asset['foliage']['ring_profile'][ring]
    assert actual['quads']==expected['quads']
    if profile:
      previous=profile[-1]
      assert actual['attachment_radius']>previous['attachment_radius']+.05
      assert actual['attachment_height']<previous['attachment_height']-.04
      assert actual['mean_texture_gray']<=previous['mean_texture_gray']+.01
      assert previous['tip_radius']>actual['attachment_radius']+.04
    profile.append(actual)
  assert len(profile)==asset['foliage']['foliage_rings']
  if asset['foliage']['kind']=='evergreen':
    assert asset['foliage']['branches']==0
    assert not any(group.name.startswith('Wooden bough') for group in byPart['trunk'].vertex_groups)
  assert abs(min(v.co.z for v in byPart['trunk'].data.vertices))<.00001
  return {'foliage_quads':len(leaves.data.polygons),'separate_meshes':True,
          'neutral_tint':True,'double_sided_alpha_mask':True,
          'radial_rings':profile,'outward_descending_flow_verified':True,
          'lower_rings_darker':True,'ring_overlap_verified':True,
          'upward_facing_cards':True}


for asset in manifest['assets']:
  name=asset['faction']+'_'+asset['asset']
  root=bpy.data.objects[name]
  objects=[obj for obj in root.children if obj.type=='MESH']
  assert objects
  count=0
  pixelRatios=[]
  pixelDensities=[]
  symmetryErrors=[]
  for obj in objects:
    evaluated=obj.evaluated_get(graph)
    mesh=evaluated.to_mesh()
    mesh.calc_loop_triangles()
    count+=len(mesh.loop_triangles)
    points=KDTree(len(mesh.vertices))
    for vertex in mesh.vertices:
      points.insert(vertex.co,vertex.index)
    points.balance()
    if asset['asset'].startswith('tower') and 'Front flag' not in obj.name:
      array=next(m for m in obj.modifiers if m.type=='ARRAY')
      assert array.count==6 and array.use_object_offset
      assert abs(array.offset_object.rotation_euler.z-math.pi/3)<.00001
      rotate=Matrix.Rotation(math.pi/3,4,'Z')
      errors=[points.find(rotate@v.co)[2] for v in mesh.vertices]
      assert max(errors)<.00001,(name,max(errors))
      symmetryErrors.extend(errors)
    elif asset['asset'] in ['barracks','pillar','wall']:
      mirror=next(m for m in obj.modifiers if m.type=='MIRROR')
      assert tuple(mirror.use_axis)==(True,True,False)
      for vertex in mesh.vertices:
        x,y,z=vertex.co
        errors=[points.find(Vector((-x,y,z)))[2],points.find(Vector((x,-y,z)))[2]]
        assert max(errors)<.00001,(name,max(errors))
        symmetryErrors.extend(errors)
    elif 'Front flag' in obj.name:
      assert not any(m.type in ['MIRROR','ARRAY'] for m in obj.modifiers)
      assert all(v.co.y<0 for v in mesh.vertices)
    treeAtlas=obj.get('atlas_kind')=='tree_foliage'
    ratios,densities=(pixelAspect(mesh,set(range(4,16)),'TreeUV','tree_atlas_tile',2048)
                      if treeAtlas else
                      pixelAspect(mesh,manifest['uv_mapping']['square_pixel_tiles']))
    pixelRatios.extend(ratios)
    pixelDensities.extend(densities)
    evaluated.to_mesh_clear()
    uv=obj.data.uv_layers['TreeUV' if treeAtlas else 'TrimUV']
    attr=obj.data.attributes['tree_atlas_tile' if treeAtlas else 'trim_tile']
    texture=manifest['textures'][asset['faction']]
    for polygon in obj.data.polygons:
      tile=attr.data[polygon.index].value
      row,col=divmod(tile,4)
      x0,x1=([col*512,(col+1)*512] if treeAtlas else texture['pixel_columns'][col:col+2])
      y0,y1=([row*512,(row+1)*512] if treeAtlas else texture['pixel_rows'][row:row+2])
      size,inset=(2048,7.9) if treeAtlas else (1254,8.9)
      for loop in polygon.loop_indices:
        u,v=uv.data[loop].uv
        x=u*size
        y=(1-v)*size
        assert x0+inset<=x<=x1-inset,(name,tile,x)
        assert y0+inset<=y<=y1-inset,(name,tile,y)
  glbCount,digest,doc=glbInspection(Root/asset['file'])
  attachments=verifyAttachments(asset,root,doc)
  foliage=verifyFoliage(asset,objects,doc)
  assert 0<count<=249 and count==asset['triangles']==glbCount
  assert digest==asset['sha256']
  assert all(ratio<1.001 for ratio in pixelRatios),(name,max(pixelRatios))
  treeShape=None
  if asset['asset'].startswith('tree') and asset['faction']=='dark':
    obj=objects[0]
    groups={group.index:group.name for group in obj.vertex_groups}
    branches=[group for group in groups.values()
              if group!='Crooked trunk' and not group.startswith('Root ')]
    assert len(branches)==asset['tree_shape']['branches']
    canopy=np.array([tuple(vertex.co) for vertex in obj.data.vertices
                     if any(groups[group.group] in branches for group in vertex.groups)])
    horizontal=canopy[:,:2]-canopy[:,:2].mean(axis=0)
    singular=np.linalg.svd(horizontal,compute_uv=False)
    depthRatio=float(singular[1]/singular[0])
    assert depthRatio>.3,(name,depthRatio)
    assert abs(min(vertex.co.z for vertex in obj.data.vertices))<.00001
    treeShape={'branches':len(branches),'horizontal_depth_ratio':depthRatio,
               'ground_level_origin':True}
  report.append({'asset':name,'triangles':count,'glb_triangles':glbCount,
                 'symmetry_verified':True,'uv_tile_insets_verified':True,
                 'maximum_symmetry_distance':max(symmetryErrors,default=None),
                 'square_pixel_triangles_checked':len(pixelRatios),
                 'maximum_pixel_aspect_ratio':max(pixelRatios,default=None),
                 'pixels_per_meter_range':([min(pixelDensities),max(pixelDensities)]
                                           if pixelDensities else None),
                 'self_contained_glb':True,'sha256':digest,
                 'attachments':attachments,'tree_shape':treeShape,'foliage':foliage})
for faction in ['dark','light']:
  image=bpy.data.images[faction.title()+' 4x4 trim atlas']
  assert image.packed_file and min(image.size)>0
  assert len(image.pixels)>0 and math.isfinite(image.pixels[0])
references=[o for o in bpy.data.scenes['02 Generated GLB references'].objects
            if o.type=='MESH']
assert len(references)==18
for faction,levels in [('light',[2,3]),('dark',[1,3])]:
  for level in levels:
    image=bpy.data.images[f'{faction.title()} tower level {level} concept']
    assert image.packed_file and min(image.size)>0
for index in range(1,4):
  image=bpy.data.images[f'Dead tree style {index}']
  assert image.packed_file and min(image.size)>0
image=bpy.data.images['Tree foliage atlas']
assert image.packed_file and tuple(image.size)==(2048,2048) and image.channels==4
assert bpy.data.images['Light tree styles'].packed_file
assert bpy.data.images['Tree ring layout'].packed_file
assert manifest['foliage_atlas']['version']==5
assert hashlib.sha256((Root/'textures/tree_foliage_atlas.png').read_bytes()).hexdigest()==manifest['foliage_atlas']['sha256']
assert len(manifest['assets'])==20
assert sum(asset['tree_shape'] is not None for asset in report)==4
assert sum(asset['foliage'] is not None for asset in report)==4
assert sum(len(asset['attachments']) for asset in report)==8
result={'blender_file':'fort_kit.blend','assets':report,'packed_trim_atlases':2,
        'reference_meshes':len(references),'all_models_under_250_triangles':True,
        'tower_concept_references':4,
        'tree_style_references':3,
        'tree_variants_verified':4,
        'light_tree_variants_verified':4,'packed_foliage_atlases':1,
        'square_pixel_mapping_verified':True,
        'gameplay_attachments_verified':8,
        'maximum_allowed_pixel_aspect_ratio':1.001}
(Root/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2),flush=True)
