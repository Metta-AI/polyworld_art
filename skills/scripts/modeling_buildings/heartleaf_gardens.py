"""Revise the hive, clothesline and hollow wooden garden bucket from close-ups."""
import bpy
import json
import math
import shutil
import struct
from pathlib import Path
from mathutils import Vector


def plainMaterial(name, color):
    """Make an original matte material for cloth, rope or recessed soil."""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = (*color, 1)
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Roughness'].default_value = 1
    shader.inputs['Specular IOR Level'].default_value = 0
    mat.use_backface_culling = False
    return mat


class GardenMesh:
    """Collect explicit low-poly shells with the existing painted timber trim."""
    def __init__(self):
        self.vertices, self.faces, self.uvs, self.indices = [], [], [], []
        self.materials = [
            bpy.data.materials['Painted oak and leaves'],
            plainMaterial('Garden rope and soil', (.105, .057, .021)),
            plainMaterial('Garden cloth purple', (.45, .17, .77)),
            plainMaterial('Garden cloth blue', (.20, .48, .89)),
            plainMaterial('Garden cloth cream', (.98, .93, .78)),
        ]

    def face(self, points, material=0, dark=False):
        """Add a timber-mapped polygon or a plain colored face."""
        start = len(self.vertices)
        self.vertices.extend(tuple(point) for point in points)
        self.faces.append(tuple(range(start, start + len(points))))
        self.indices.append(material)
        u, v, right, top = ((.51, .84, .74, .99) if dark else
                             (.26, .84, .49, .99))
        self.uvs.append([(u, v), (right, v), (right, top), (u, top)]
                        [:len(points)])

    def box(self, center, size, material=0, dark=False):
        """Build a closed rectangular board with painted grain."""
        x, y, z = center
        dx, dy, dz = (value / 2 for value in size)
        vertices = [(x + a * dx, y + b * dy, z + c * dz)
                    for c in [-1, 1] for a, b in
                    [(-1, -1), (1, -1), (1, 1), (-1, 1)]]
        for face in [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
                     (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]:
            self.face([vertices[i] for i in face], material, dark)

    def beam(self, a, b, radius, material=0):
        """Join two hexagonal rings for a rope segment or timber support."""
        a, b = Vector(a), Vector(b)
        axis = (b - a).normalized()
        side = axis.cross(Vector((0, 0, 1)))
        if side.length < .1:
            side = axis.cross(Vector((0, 1, 0)))
        side.normalize()
        up = axis.cross(side)
        rings = [[point + radius * (math.cos(i * math.tau / 6) * side +
                  math.sin(i * math.tau / 6) * up) for i in range(6)]
                 for point in [a, b]]
        for i in range(6):
            j = (i + 1) % 6
            self.face([rings[0][i], rings[0][j], rings[1][j], rings[1][i]],
                      material)
        for ring in [rings[0][::-1], rings[1]]:
            for i in range(1, 5):
                self.face([ring[0], ring[i], ring[i + 1]], material)

    def object(self, name, mirror=False):
        """Create an editable ground-pivot prop with a live symmetry modifier."""
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(self.vertices, [], self.faces)
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        for mat in self.materials:
            mesh.materials.append(mat)
        uv = mesh.uv_layers.new()
        for poly, coords, material in zip(mesh.polygons, self.uvs, self.indices):
            poly.material_index = material
            for loop, coord in zip(poly.loop_indices, coords):
                uv.data[loop].uv = coord
        if mirror:
            modifier = obj.modifiers.new('Editable bilateral hive', 'MIRROR')
            modifier.use_bisect_axis[0] = True
            modifier.use_clip = True
        obj['source'] = 'Original AI-authored Heartleaf garden prop, CC0.'
        return obj


def buildGardenProps():
    """Replace only the hive and laundry, and add a reusable hollow bucket."""
    for name in ['beehive', 'laundry', 'bucket_planter']:
        old = bpy.data.objects.get(name)
        if old:
            bpy.data.objects.remove(old, do_unlink=True)
    hive = GardenMesh()
    for x in [-.49, .49]:
        for y in [-.39, .39]:
            hive.box((x, y, .51), (.17, .17, 1.02))
    hive.box((0, 0, .94), (1.36, 1.13, .14))
    # One continuous shell recesses the tier seams without see-through gaps.
    rings = []
    for z, inset in [(.98, 0), (1.285, 0), (1.30, .018), (1.315, 0),
                     (1.605, 0), (1.62, .018), (1.635, 0), (1.94, 0)]:
        rings.append([(x * (.64 - inset), y * (.52 - inset), z)
                      for x, y in [(-1, -1), (1, -1), (1, 1), (-1, 1)]])
    for lower, upper in zip(rings, rings[1:]):
        for i in range(4):
            j = (i + 1) % 4
            hive.face([lower[i], lower[j], upper[j], upper[i]])
    hive.face(rings[0][::-1])
    hive.box((0, -.63, 1.025), (.72, .24, .09))
    hive.box((0, -.526, 1.11), (.48, .012, .065), 1)
    # A solid gently pitched cap closes the hive while keeping deep eaves.
    for side in [-1, 1]:
        points = [(-.76, 0, 2.24), (.76, 0, 2.24),
                  (.76, side * .65, 2.00), (-.76, side * .65, 2.00)]
        if side == -1:
            points.reverse()
        hive.face(points)
        hive.box((0, side * .65, 1.98), (1.52, .08, .10))
    for x in [-.76, .76]:
        points = [(x, -.65, 1.94), (x, .65, 1.94), (x, 0, 2.24)]
        hive.face(points if x > 0 else points[::-1])
    hive.face([(-.76, -.65, 1.94), (-.76, .65, 1.94),
               (.76, .65, 1.94), (.76, -.65, 1.94)])

    laundry = GardenMesh()
    for x in [-1.85, 1.85]:
        laundry.box((x, 0, 1.08), (.22, .22, 2.16))
        laundry.box((x, 0, 2.12), (.29, .29, .12))
    def ropeHeight(x):
        """Sag the line between its two fixed timber posts."""
        return 2.04 - .18 * (1 - (x / 1.85) ** 2)
    for i in range(12):
        a, b = -1.85 + i * 3.7 / 12, -1.85 + (i + 1) * 3.7 / 12
        laundry.beam((a, 0, ropeHeight(a)), (b, 0, ropeHeight(b)), .025, 1)
    for index, left in enumerate([-1.53, -.43, .67]):
        width = .82
        for j in range(4):
            a, b = left + j * width / 4, left + (j + 1) * width / 4
            ya, yb = .085 * math.sin(j * 2.1), .085 * math.sin((j + 1) * 2.1)
            low = .84 + .10 * index
            laundry.face([(a, ya, low), (b, yb, low + .03),
                          (b, 0, ropeHeight(b) - .025),
                          (a, 0, ropeHeight(a) - .025)], index + 2)
        for x in [left + .10, left + width - .10]:
            laundry.box((x, -.03, ropeHeight(x)), (.045, .065, .12))
    laundry.vertices = [(x, y, z * 1.4) for x, y, z in laundry.vertices]

    bucket = GardenMesh()
    def ringPoint(angle, radius, height):
        """Locate one corner of a stave in a circular tapered shell."""
        return (math.cos(angle) * radius, math.sin(angle) * radius, height)
    for i in range(16):
        a, b = (i + .016) * math.tau / 16, (i + .984) * math.tau / 16
        rings = [[ringPoint(angle, radius, z) for angle in [a, b]]
                 for radius, z in [(.40, .02), (.55, .78),
                                    (.465, .78), (.335, .14)]]
        for lower, upper in [(0, 1), (1, 2), (2, 3), (3, 0)]:
            bucket.face([rings[lower][0], rings[lower][1],
                         rings[upper][1], rings[upper][0]])
        for side in [0, 1]:
            bucket.face([rings[j][side] for j in ([3, 2, 1, 0] if side else
                                                   [0, 1, 2, 3])])
        # Narrow dark timber hoops wrap the tapered staves below the thick rim.
        for bottom in [.17, .60]:
            radius = .40 + bottom / .76 * .15 + .013
            upper = radius + .07 / .76 * .15
            bucket.face([ringPoint(i * math.tau / 16, radius, bottom),
                         ringPoint((i + 1) * math.tau / 16, radius, bottom),
                         ringPoint((i + 1) * math.tau / 16, upper, bottom + .07),
                         ringPoint(i * math.tau / 16, upper, bottom + .07)],
                        dark=True)
        bucket.face([(0, 0, .64),
                     ringPoint(i * math.tau / 16, .446, .64),
                     ringPoint((i + 1) * math.tau / 16, .446, .64)], 1)
    return [hive.object('beehive', mirror=True), laundry.object('laundry'),
            bucket.object('bucket_planter')]


def main():
    """Revise the current library without changing previously approved props."""
    art = Path(__file__).resolve().parents[3]
    work = art / 'tmp/heartleaf-props'
    work.mkdir(parents=True, exist_ok=True)
    for relative in ['source/village_details.blend', 'models/village_details.glb']:
        path = art / 'terrain/heartleaf' / relative
        backup = work / ('before-' + path.name)
        if not backup.exists():
            shutil.copy2(path, backup)
    bpy.ops.wm.open_mainfile(filepath=str(work / 'before-village_details.blend'))
    buildGardenProps()
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    for obj in meshes:
        obj.location = (0, 0, 0)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes:
        obj.select_set(True)
    output = work / 'village_details.glb'
    bpy.ops.export_scene.gltf(filepath=str(output), export_format='GLB',
                             use_selection=True, export_apply=True, export_yup=True)
    previous = (work / 'before-village_details.glb').read_bytes()
    size = struct.unpack_from('<I', previous, 12)[0]
    factors = {m['name']: m['pbrMetallicRoughness'].get('baseColorFactor', [1]*4)
               for m in json.loads(previous[20:20+size])['materials']}
    raw = output.read_bytes()
    size = struct.unpack_from('<I', raw, 12)[0]
    doc = json.loads(raw[20:20+size])
    for item in doc['materials']:
        if item['name'] in factors:
            item['pbrMetallicRoughness']['baseColorFactor'] = factors[item['name']]
    encoded = json.dumps(doc, separators=(',', ':')).encode()
    encoded += b' ' * (-len(encoded) % 4)
    binary = raw[20+size:]
    output.write_bytes(struct.pack('<IIIII', 0x46546c67, 2,
                       20+len(encoded)+len(binary), len(encoded), 0x4e4f534a) +
                       encoded + binary)
    for i, obj in enumerate(meshes):
        obj.location = ((i % 4) * 20, (i // 4) * 20, 0)
    bpy.ops.wm.save_as_mainfile(filepath=str(work / 'village_details.blend'))
    print('HEARTLEAF_GARDEN_PROPS_EXPORTED', output)


if __name__ == '__main__':
    main()
