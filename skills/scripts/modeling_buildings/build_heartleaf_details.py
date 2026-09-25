"""Build editable Heartleaf village props using the existing CC0 trim."""
import bpy, math, json, struct, random
from pathlib import Path
from mathutils import Vector

Art = Path(__file__).resolve().parents[3]
Work = Art / 'tmp/heartleaf-town'
Work.mkdir(parents=True, exist_ok=True)
Out = Work / 'village_details.glb'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
raw = (Art / 'terrain/blender_village/models/hobbit_house.glb').read_bytes()
n = struct.unpack_from('<I', raw, 12)[0]
doc = json.loads(raw[20:20+n]); blob = raw[28+n:]
for record in doc['images']:
    if 'trim' in record['name'].lower():
        view = doc['bufferViews'][record['bufferView']]
        a = view.get('byteOffset', 0)
        (Work / 'trim.png').write_bytes(blob[a:a+view['byteLength']])
image = bpy.data.images.load(str(Work / 'trim.png')); image.pack()
regions = [(.0032,.8359,.2472,.9979),(.2536,.8359,.4976,.9979),
 (.504,.8359,.7464,.9979),(.7528,.8359,.9968,.9979),
 (.0032,.6713,.2472,.8317),(.2536,.6713,.4976,.8317),
 (.504,.6713,.7464,.8317),(.7528,.6713,.9968,.8317),
 (.0032,.513,.2472,.667),(.2536,.513,.4976,.667),
 (.504,.513,.7464,.667),(.7528,.513,.9968,.667),
 (.0032,.3383,.2472,.5087),(.2536,.3383,.4976,.5087),
 (.504,.3383,.7464,.5087),(.7528,.3383,.9968,.5087)]
materials=[]
for name,tint in [('Painted oak and leaves',(1,1,1,1)),
 ('Blue petals',(.25,.43,1,1)),('Golden petals',(1,.72,.1,1)),
 ('Canopy cream',(1,.95,.76,1)),('Canopy blue',(.19,.45,.85,1)),
 ('Iron',(.15,.19,.15,1)),('Lantern glass',(1,.83,.3,1))]:
    mat=bpy.data.materials.new(name); mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=tint
    bs.inputs['Roughness'].default_value=1
    bs.inputs['Specular IOR Level'].default_value=0
    if len(materials)<3:
        tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image
        mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
    mat.diffuse_color=tint
    materials.append(mat)

class Geo:
    def __init__(self): self.v=[];self.f=[];self.uv=[];self.m=[]
    def face(self,points,tile=1,mat=0):
        a=len(self.v);self.v.extend(points);self.f.append(tuple(range(a,a+len(points))))
        u,v,U,V=regions[tile]
        corners=[(u,v),(U,v),(U,V),(u,V)]
        self.uv.append(corners[:len(points)]);self.m.append(mat)
    def box(self,center,size,tile=1,mat=0):
        x,y,z=center;dx,dy,dz=[v/2 for v in size]
        v=[(x-dx,y-dy,z-dz),(x+dx,y-dy,z-dz),(x+dx,y+dy,z-dz),(x-dx,y+dy,z-dz),
           (x-dx,y-dy,z+dz),(x+dx,y-dy,z+dz),(x+dx,y+dy,z+dz),(x-dx,y+dy,z+dz)]
        for face in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:
            self.face([v[i] for i in face],tile,mat)
    def beam(self,a,b,r=.07,tile=1,mat=0,sides=6):
        a,b=Vector(a),Vector(b);axis=(b-a).normalized()
        side=axis.cross(Vector((0,0,1)))
        if side.length<.1: side=axis.cross(Vector((0,1,0)))
        side.normalize();up=axis.cross(side)
        rings=[]
        for center in [a,b]:
            rings.append([tuple(center+r*(math.cos(i*2*math.pi/sides)*side+math.sin(i*2*math.pi/sides)*up)) for i in range(sides)])
        for i in range(sides):
            j=(i+1)%sides;self.face([rings[0][i],rings[0][j],rings[1][j],rings[1][i]],tile,mat)
        for ring,reverse in [(rings[0],True),(rings[1],False)]:
            for i in range(1,sides-1):
                tri=[ring[0],ring[i],ring[i+1]]
                self.face(tri[::-1] if reverse else tri,3,mat)
    def leaf(self,x,y,z,angle,length=.4,width=.18,tile=12,mat=0):
        dx,dy=math.cos(angle),math.sin(angle)
        self.face([(x,y,z),(x+dx*length*.5-dy*width,y+dy*length*.5+dx*width,z+.12),
                   (x+dx*length,y+dy*length,z+.07),
                   (x+dx*length*.5+dy*width,y+dy*length*.5-dx*width,z+.12)],tile,mat)
    def flower(self,x,y,h,r=.16,tile=13,mat=0,petals=5):
        self.beam((x,y,0),(x,y,h),.018,12,sides=4)
        for a in [0,2.5,4.4]: self.leaf(x,y,h*.4,a,.24,.08)
        for i in range(petals):
            a=i*2*math.pi/petals
            self.leaf(x,y,h,a,r,r*.47,tile,mat)
        self.beam((x,y,h+.005),(x,y,h+.045),r*.25,10,sides=6)
    def object(self,name):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(self.v,[],self.f);mesh.update()
        obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
        for mat in materials: mesh.materials.append(mat)
        uv=mesh.uv_layers.new()
        for poly,coords,mat in zip(mesh.polygons,self.uv,self.m):
            poly.material_index=mat
            for idx,coord in zip(poly.loop_indices,coords): uv.data[idx].uv=coord
        return obj

assets=[]
g=Geo()
for x in [-.9,.9]:
    g.beam((x,0,0),(x,0,1.05),.10,sides=5)
for z in [.36,.79]:g.beam((-.9,0,z),(.9,0,z+.04),.06)
assets.append(g.object('fence'))
g=Geo()
for y in [-.2,0,.2]:g.box((0,y,.55),(2.4,.18,.13))
for x in [-.92,.92]:
    for y in [-.20,.2]:g.beam((x,y,0),(x,y,.56),.075)
    g.beam((x,.24,.48),(x,.38,1.10),.055)
for z in [.82,1.03]:g.box((0,.33,z),(2.4,.12,.16))
assets.append(g.object('bench'))
g=Geo();g.beam((0,0,0),(0,0,2.7),.105)
g.beam((-.15,0,2.5),(.7,0,2.5),.08)
g.beam((.56,0,2.50),(.56,0,2.25),.035,0,5)
g.box((.56,0,2.03),(.32,.32,.4),0,6)
for x in [.39,.73]:
    for y in [-.17,.17]:g.beam((x,y,1.8),(x,y,2.25),.025,0,5)
g.box((.56,0,1.8),(.42,.42,.09),0,5)
g.face([(.30,-.26,2.25),(.82,-.26,2.25),(.56,0,2.46)],0,5)
g.face([(.82,-.26,2.25),(.82,.26,2.25),(.56,0,2.46)],0,5)
g.face([(.82,.26,2.25),(.30,.26,2.25),(.56,0,2.46)],0,5)
g.face([(.30,.26,2.25),(.30,-.26,2.25),(.56,0,2.46)],0,5)
assets.append(g.object('lantern'))
g=Geo();g.beam((0,0,0),(0,0,1.8),.10)
for y,z in [(0,1.5),(.02,1.1)]:
    g.face([(-.7,y,z-.14),(.55,y,z-.14),(.8,y,z),(.55,y,z+.14)],1)
    g.face([(-.7,y,z-.14),(.55,y,z+.14),(-.7,y,z+.14)],1)
assets.append(g.object('sign'))
g=Geo()
for x in [-1.4,1.4]:
    for y in [-.7,.7]:g.beam((x,y,0),(x,y,2.6),.075)
g.box((0,0,.75),(2.95,1.45,.16))
g.box((0,.38,.37),(2.8,.12,.7),9)
for x in [-.85,0,.85]:
    g.box((x,0,.87),(.75,.72,.2),9)
    for j in range(5):
        g.flower(x+(j%3-1)*.15,(j//3)*.2,.95,.15,13,2)
for i in range(8):
    x=-1.6+i*.4
    g.face([(x,-1,2.22),(x+.4,-1,2.22),(x+.4,0,2.75),(x,0,2.75)],0,3+i%2)
    g.face([(x,0,2.75),(x+.4,0,2.75),(x+.4,1,2.22),(x,1,2.22)],0,3+i%2)
    g.face([(x,-1,2.02),(x+.4,-1,2.02),(x+.4,-1,2.22),(x,-1,2.22)],0,3+i%2)
assets.append(g.object('market'))
g=Geo()
for x in [-1.7,1.7]:g.beam((x,0,0),(x,0,1.85),.065)
g.beam((-1.7,0,1.75),(1.7,0,1.75),.017,2)
for i in range(4):
    x=-1.25+i*.68
    g.face([(x,0,.78),(x+.47,0,.73),(x+.50,0,1.7),(x,0,1.7)],0,3+i%2)
assets.append(g.object('laundry'))
g=Geo()
for x in [-.3,.3]:g.box((x,0,.2),(.1,.6,.4))
for z in [.45,.70,.95]:g.box((0,0,z),(.85,.7,.23),1)
g.box((0,-.37,.39),(.50,.20,.06))
g.box((0,-.356,.52),(.25,.01,.08),11)
g.face([(-.5,-.44,1.07),(.5,-.44,1.07),(.5,0,1.32),(-.5,0,1.32)],1)
g.face([(-.5,0,1.32),(.5,0,1.32),(.5,.44,1.07),(-.5,.44,1.07)],1)
assets.append(g.object('beehive'))
for name,tile,mat in [('flowers_white',13,0),('flowers_blue',13,1),('flowers_purple',14,0),('flowers_gold',13,2)]:
    g=Geo();rng=random.Random(19)
    for i in range(10):
        x=rng.uniform(-.55,.55);y=rng.uniform(-.45,.45)
        for a in [0,2.1,4.2]:g.leaf(x,y,.04,a,.35,.15)
        g.flower(x,y,rng.uniform(.22,.62),.18,tile,mat)
    assets.append(g.object(name))
g=Geo()
for i in range(4):
    x=(i%2-.5)*.4;y=(i//2-.5)*.35;h=1.2+(i%3)*.2
    g.beam((x,y,0),(x,y,h),.025,12)
    for k in range(6):g.leaf(x,y,k*.035,k*2.4,.46,.12)
    for k in range(15):
        a=k*2.4;z=.35+k*.055;r=.21*(1-k/22)
        g.leaf(x,y,z,a,r,r*.8,14,1 if i%2 else 0)
assets.append(g.object('lupins'))
g=Geo()
for i in range(3):g.flower((i-1)*.4,(i%2)*.35,1.4+i*.3,.36,13,2,10)
assets.append(g.object('sunflowers'))
g=Geo()
for i in range(40):
    a=i*math.tau/40;b=(i+.92)*math.tau/40
    for radius,z in [(2.75,.12)]:
        pts=[(r*math.cos(t),r*math.sin(t),h) for h in [0,.35] for r,t in [(radius,a),(radius+.34,a),(radius+.34,b),(radius,b)]]
        for face in [(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:g.face([pts[j] for j in face],6)
assets.append(g.object('tree_curb'))
g=Geo()
for row in range(6):
    inner=2.75+row*.84;outer=inner+.81
    count=round(math.tau*(inner+outer)/2/.85)
    for i in range(count):
        a=(i+(row%2)*.5)*math.tau/count
        b=(i+.94+(row%2)*.5)*math.tau/count
        pts=[(r*math.cos(t),r*math.sin(t),h) for h in [0,.10] for r,t in [(inner,a),(outer,a),(outer,b),(inner,b)]]
        for face in [(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:
            g.face([pts[j] for j in face],6)
assets.append(g.object('plaza_paving'))
# Preserve editable bilateral construction for the bench and stall.
for obj in assets:
    if obj.name in ('bench','market'):
        mirror=obj.modifiers.new('Bilateral editable symmetry','MIRROR')
        mirror.use_bisect_axis[0]=True;mirror.use_clip=True
    obj['source']='User Heartleaf town reference; procedural Codex mesh; CC0 trim from reviewed house.'
bpy.ops.object.select_all(action='DESELECT')
for obj in assets:obj.select_set(True)
bpy.context.view_layer.objects.active=assets[0]
bpy.ops.wm.save_as_mainfile(filepath=str(Work / 'village_details.blend'))
bpy.ops.export_scene.gltf(filepath=str(Out),export_format='GLB',use_selection=True,export_apply=True,export_yup=True)
# Preserve tint factors alongside textures (Blender exports texture links as white).
b=Out.read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);binchunk=b[20+n:]
for m in j['materials']:
    if m['name']=='Blue petals':m['pbrMetallicRoughness']['baseColorFactor']=[.25,.43,1,1]
    if m['name']=='Golden petals':m['pbrMetallicRoughness']['baseColorFactor']=[1,.72,.1,1]
p=json.dumps(j,separators=(',',':')).encode();p+=b' '*((-len(p))%4)
Out.write_bytes(struct.pack('<III',0x46546c67,2,20+len(p)+len(binchunk))+struct.pack('<II',len(p),0x4e4f534a)+p+binchunk)
print('DETAILS_OK', len(assets), 'assets', str(Out))

# Arrange the editable library after exporting props at their local origins.
for i,obj in enumerate(assets):
    obj.location=((i%4)*20,(i//4)*20,0)
bpy.ops.wm.save_as_mainfile(filepath=str(Work / 'village_details.blend'))
