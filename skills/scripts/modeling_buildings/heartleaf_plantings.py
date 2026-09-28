"""Build Heartleaf's forward-facing sunflower heads and overhanging eave leaves."""
import bpy
import json
import math
import random
import shutil
import struct
from pathlib import Path
from mathutils import Vector


def material(name, color):
    """Create a matte, self-contained plant color without external artwork."""
    result = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    result.use_nodes = True
    result.diffuse_color = (*color, 1)
    shader = result.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Roughness'].default_value = 1
    shader.inputs['Specular IOR Level'].default_value = 0
    return result


class PlantMesh:
    """Collect explicit low-poly leaves, stalks and flower faces."""
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.indices = []
        self.materials = [
            material('Heartleaf leaf shade', (.25, .43, .055)),
            material('Heartleaf leaf green', (.49, .68, .08)),
            material('Heartleaf leaf light', (.68, .81, .12)),
            material('Sunflower gold', (.92, .61, .065)),
            material('Sunflower petal light', (1, .78, .12)),
            material('Sunflower dark center', (.12, .058, .018)),
            material('Sunflower seeds', (.24, .12, .035)),
        ]

    def face(self, points, index):
        """Append one planar face using its chosen material."""
        start = len(self.vertices)
        self.vertices.extend(tuple(point) for point in points)
        self.faces.append(tuple(range(start, start + len(points))))
        self.indices.append(index)

    def stem(self, a, b, radius):
        """Join two stem rings with a narrow hexagonal stalk."""
        a, b = Vector(a), Vector(b)
        axis = (b - a).normalized()
        side = axis.cross(Vector((0, 1, 0))).normalized()
        up = axis.cross(side)
        rings = [[center + radius * (math.cos(i * math.tau / 6) * side +
                  math.sin(i * math.tau / 6) * up) for i in range(6)]
                 for center in [a, b]]
        for i in range(6):
            j = (i + 1) % 6
            self.face([rings[0][i], rings[0][j], rings[1][j], rings[1][i]], 0)

    def leaf(self, base, angle, length, width, drop=0, shade=1):
        """Make a ridged pointed leaf with two shaded sides."""
        base = Vector(base)
        forward = Vector((math.cos(angle), math.sin(angle), 0))
        sideways = Vector((-forward.y, forward.x, 0))
        middle = base + forward * length * .48 + Vector((0, 0, .065))
        tip = base + forward * length + Vector((0, 0, drop))
        left = middle - sideways * width - Vector((0, 0, .03))
        right = middle + sideways * width - Vector((0, 0, .03))
        self.face([base, middle, right], shade)
        self.face([right, middle, tip], shade)
        self.face([tip, middle, left], min(2, shade + 1))
        self.face([left, middle, base], min(2, shade + 1))

    def object(self, name):
        """Create one ground-pivot mesh with flat-shaded material faces."""
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(self.vertices, [], self.faces)
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        for value in self.materials:
            value.use_backface_culling = False
            mesh.materials.append(value)
        for polygon, index in zip(mesh.polygons, self.indices):
            polygon.material_index = index
        obj['source'] = 'Original AI-authored Heartleaf planting geometry, CC0.'
        return obj


def buildPlantings():
    """Replace the two named plant details without touching other models."""
    for name in ['sunflowers', 'eave_clover']:
        old = bpy.data.objects.get(name)
        if old:
            bpy.data.objects.remove(old, do_unlink=True)
    flower = PlantMesh()
    for i, (x, y, height) in enumerate([
        (-.55, .06, 1.42), (.1, .3, 1.96), (.62, .02, 1.68),
        (-.28, -.35, 1.10), (.35, -.35, 1.32)
    ]):
        head = Vector((x, y - .10, height))
        flower.stem((x, y, 0), head, .027)
        for j in range(5):
            flower.leaf((x, y, .15 + j * height * .13),
                        i * .7 + j * 2.4, .37, .14, -.025)
        # Heads look south toward the game camera, with a slight upward tilt.
        normal = Vector((.10 * math.sin(i * 1.7), -.94, .34)).normalized()
        horizontal = Vector((1, 0, 0))
        vertical = normal.cross(horizontal).normalized()
        horizontal = vertical.cross(normal).normalized()
        radius = .155
        center = head + normal * .025
        for j in range(16):
            angle = j * math.tau / 16
            nextAngle = (j + 1) * math.tau / 16
            radial = math.cos(angle) * horizontal + math.sin(angle) * vertical
            tangent = -math.sin(angle) * horizontal + math.cos(angle) * vertical
            tip = head + radial * (.365 + .02 * (j % 3))
            root = head + radial * .12
            middle = head + radial * .25 + normal * .018
            flower.face([root, middle - tangent * .072, tip], 3)
            flower.face([root, tip, middle + tangent * .072], 4)
            edge = head + normal * .022 + radial * radius
            following = head + normal * .022 + radius * (
                math.cos(nextAngle) * horizontal + math.sin(nextAngle) * vertical)
            flower.face([center, edge, following], 5)
        for j in range(13):
            angle = j * 2.39996
            radius = .12 * math.sqrt((j + .5) / 13)
            at = center + normal * .006 + radius * (
                math.cos(angle) * horizontal + math.sin(angle) * vertical)
            flower.face([at - horizontal * .011, at + vertical * .015,
                         at + horizontal * .011, at - vertical * .015], 6)
    fringe = PlantMesh()
    rng = random.Random(728)
    for i in range(15):
        base = (rng.uniform(-.35, .35), rng.uniform(-.15, .12), .13)
        # Blender -Y becomes the facade's front (+Z) after glTF export.
        fringe.leaf(base, rng.uniform(-2.8, -.25), rng.uniform(.19, .39),
                    rng.uniform(.075, .13), rng.uniform(-.12, -.04), 1)
    return [flower.object('sunflowers'), fringe.object('eave_clover')]


def main():
    """Revise the current editable library and export a review candidate."""
    art = Path(__file__).resolve().parents[3]
    work = art / 'tmp/heartleaf-colors'
    work.mkdir(parents=True, exist_ok=True)
    source = art / 'terrain/heartleaf/source/village_details.blend'
    original = art / 'terrain/heartleaf/models/village_details.glb'
    for path in [source, original]:
        backup = work / ('before-' + path.name)
        if not backup.exists():
            shutil.copy2(path, backup)
    bpy.ops.wm.open_mainfile(filepath=str(work / 'before-village_details.blend'))
    buildPlantings()
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    placements = {obj.name: obj.location.copy() for obj in meshes}
    for obj in meshes:
        obj.location = (0, 0, 0)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes:
        obj.select_set(True)
    output = work / 'village_details.glb'
    bpy.ops.export_scene.gltf(filepath=str(output), export_format='GLB',
                             use_selection=True, export_apply=True, export_yup=True)
    # Preserve the reviewed textured color factors that Blender drops on export.
    previous = (work / 'before-village_details.glb').read_bytes()
    size = struct.unpack_from('<I', previous, 12)[0]
    factors = {m['name']: m['pbrMetallicRoughness'].get('baseColorFactor', [1]*4)
               for m in json.loads(previous[20:20+size])['materials']}
    raw = output.read_bytes()
    size = struct.unpack_from('<I', raw, 12)[0]
    doc = json.loads(raw[20:20+size])
    for item in doc['materials']:
        if item['name'] in factors and not item['name'].startswith(
                ('Heartleaf leaf', 'Sunflower')):
            item['pbrMetallicRoughness']['baseColorFactor'] = factors[item['name']]
    encoded = json.dumps(doc, separators=(',', ':')).encode()
    encoded += b' ' * (-len(encoded) % 4)
    binary = raw[20+size:]
    output.write_bytes(struct.pack('<IIIII', 0x46546c67, 2,
                       20+len(encoded)+len(binary), len(encoded), 0x4e4f534a) +
                       encoded + binary)
    for obj in meshes:
        obj.location = placements[obj.name]
    bpy.data.objects['sunflowers'].location = (40, 60, 0)
    bpy.data.objects['eave_clover'].location = (0, 80, 0)
    bpy.ops.wm.save_as_mainfile(filepath=str(work / 'village_details.blend'))
    print('HEARTLEAF_PLANTINGS_EXPORTED', output)


if __name__ == '__main__':
    main()
