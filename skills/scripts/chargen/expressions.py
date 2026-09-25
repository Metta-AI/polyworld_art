"""Build shared expression decals for every character using the common head."""

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

from gnomes import mesh
from paths import Library


def expressionParts():
  """Expose the same untinted dead eyes to every character family."""
  return [('Eyes', dict(name='Dead X', nodes=['Eyes_DeadX'],
    id='eyes/dead_x', texture='eyes/dead_x.png',
    alignment='both', singleFile=True))]


def buildExpressions(collection, head):
  """Fit a small head-weighted decal to the existing face curvature."""
  tree = BVHTree.FromPolygons([vertex.co for vertex in head.data.vertices],
                             [tuple(face.vertices) for face in head.data.polygons])
  vertices, faces, uvs = [], [], []
  columns, rows = 16, 8
  for row in range(rows + 1):
    for column in range(columns + 1):
      # Exclude transparent outer margins so every corner lies on the head.
      u, v = .12 + .76 * column / columns, .24 + .52 * row / rows
      x, z = (u - .5) * .9, 2.335 + (v - .5) * .45
      point = tree.ray_cast(Vector((x, -2, z)), Vector((0, 1, 0)))[0]
      assert point is not None, (x, z)
      vertices.append((x, point.y - .008, z))
      uvs.append((u, v))
      if row and column:
        a = (row - 1) * (columns + 1) + column - 1
        faces.append((a, a + 1, a + columns + 2, a + columns + 1))
  mat = bpy.data.materials.new('Face texture / Eyes_DeadX')
  mat.use_nodes = True
  nodes, links = mat.node_tree.nodes, mat.node_tree.links
  nodes.clear()
  texture = nodes.new('ShaderNodeTexImage')
  texture.image = bpy.data.images.load(str(Library / 'eyes/dead_x.png'),
                                      check_existing=False)
  texture.image.pack()
  texture.extension = 'EXTEND'
  clip = nodes.new('ShaderNodeMath')
  clip.operation = 'ROUND'
  transparent = nodes.new('ShaderNodeBsdfTransparent')
  blend = nodes.new('ShaderNodeMixShader')
  output = nodes.new('ShaderNodeOutputMaterial')
  links.new(texture.outputs['Alpha'], clip.inputs[0])
  links.new(clip.outputs[0], blend.inputs[0])
  links.new(transparent.outputs[0], blend.inputs[1])
  links.new(texture.outputs['Color'], blend.inputs[2])
  links.new(blend.outputs[0], output.inputs[0])
  mat.surface_render_method = 'DITHERED'
  item = mesh(collection, 'Eyes_DeadX', vertices, faces, [mat], True)
  item['family'] = 'Shared'
  layer = item.data.uv_layers.new(name='Face projection')
  for loop in item.data.loops:
    layer.data[loop.index].uv = uvs[loop.vertex_index]
  return [item]
