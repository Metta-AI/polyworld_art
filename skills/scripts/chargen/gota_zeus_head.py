"""Build Zeus's crown and flowing white hair on the shared head socket."""

import math

from mathutils import Vector

from beards import jaw, surface
from gota_common import mesh, part, smooth
from hairs import HairBuilder

White = '#f5f1ec'
WhiteShade = '#d9d5d5'
Gold = '#e3af37'
GoldLight = '#f1c958'
Blue = '#1764e6'


def hairMesh(ctx, suffix, builder, colors):
  """Export broad curved locks with crisp tips and restrained shading."""
  obj = mesh(ctx, suffix, builder.vertices, builder.faces, colors, bone='Head')
  for face, color in zip(obj.data.polygons, builder.materials):
    face.material_index = color
  return smooth(obj, 58)


def circlet(ctx):
  """Build a rounded solid gold band with raised temple laurels."""
  vertices, faces = [], []
  for radius in [0, 1]:
    for height in [-1, 1]:
      for i in range(48):
        angle = math.tau * i / 48
        vertices.append(((.560 + radius * .027) * math.sin(angle),
                         .025 - (.550 + radius * .027) * math.cos(angle),
                         2.825 + .040 * height + .02 * math.cos(angle)))
  for i in range(48):
    j = (i + 1) % 48
    faces += [(i, j, j + 48, i + 48),
              (i + 96, i + 144, j + 144, j + 96),
              (i, i + 96, j + 96, j),
              (i + 48, j + 48, j + 144, i + 144)]
  objects = [smooth(mesh(ctx, 'laurel_band', vertices, faces, [Gold], bone='Head'), 65)]
  for sign in [-1, 1]:
    stem = HairBuilder()
    stem.lock([(sign * .10, -.60, 2.845),
               (sign * .220, -.685, 2.855),
               (sign * .355, -.592, 2.855),
               (sign * .472, -.454, 2.855),
               (sign * .557, -.282, 2.855),
               (sign * .574, -.15, 2.84)],
              [.025, .029, .029, .029, .027, .020],
              normal=(0, 0, 1), sides=6, steps=2)
    objects.append(hairMesh(ctx, f'laurel_stem_{sign}', stem, [Gold]))
    for i, (theta, z, rise) in enumerate([
      (.48, 2.895, .19), (.73, 2.91, .23), (.99, 2.91, .21),
      (1.25, 2.895, .16)]):
      theta *= sign
      radial = Vector((math.sin(theta), -math.cos(theta), 0))
      tangent = Vector((sign * math.cos(theta), sign * math.sin(theta), 0))
      # Set the laurels outside the swept forelocks, not under the scalp band.
      center = Vector((.610 * math.sin(theta), .025 - .765 * math.cos(theta), z))
      tip = center + tangent * -.060 + Vector((0, 0, rise))
      base = center - tangent * .070
      base.z = 2.855
      blade = HairBuilder()
      blade.lock([base,
                  center + Vector((0, 0, rise * .43)), tip],
                 [.007, .076, .005], [.012, .029, .004],
                 normal=radial, sides=6, steps=2)
      objects.append(hairMesh(ctx, f'laurel_{sign}_{i}', blade, [GoldLight if i % 2 else Gold]))
  for label, y, width, height, depth, color in [
    ('gem_mount', -.589, .265, .390, .052, Gold),
    ('blue_gem', -.650, .194, .294, .042, Blue)]:
    z = 2.865
    vertices = [(0, y, z + height / 2), (width / 2, y, z),
                (0, y, z - height / 2), (-width / 2, y, z),
                (0, y - depth, z), (0, y + .012, z)]
    faces = [(i, (i + 1) % 4, 4) for i in range(4)]
    faces += [((i + 1) % 4, i, 5) for i in range(4)]
    objects.append(mesh(ctx, label, vertices, faces, [color], bone='Head'))
  return objects


def flowingHair(ctx):
  """Layer swept white locks over a fitted rounded scalp and open forehead."""
  builder = HairBuilder()
  builder.cap(front=2.875, side=2.32, back=1.955, top=3.215,
              puff=.032, segments=28, rings=7, profile=[
                (1.93, .38, .42, .08), (2.24, .48, .515, .04),
                (2.54, .505, .535, .02), (2.80, .48, .49, .025),
                (3.0, .36, .355, .025), (3.13, .19, .18, .025),
                (3.215, .020, .020, .025)])
  for sign in [-1, 1]:
    # The front sweep clears the brow and curls outward at the temples.
    builder.lock([(sign * .045, -.21, 3.17),
                  (sign * .21, -.42, 3.075),
                  (sign * .385, -.535, 2.855),
                  (sign * .58, -.39, 2.735)],
                 [.030, .150, .130, .012], [.025, .085, .063, .008],
                 sides=6, steps=3)
    builder.lock([(sign * .14, -.08, 3.185),
                  (sign * .36, -.25, 3.12),
                  (sign * .48, -.31, 2.97)],
                 [.020, .11, .008], [.019, .065, .008],
                 sides=6, steps=3)
    for i in range(3):
      z = 2.90 - i * .255
      builder.lock([(sign * .41, .03, z),
                    (sign * .525, -.05, z - .11),
                    (sign * .55, -.06, z - .265),
                    (sign * (.67 - i * .006), -.09, z - .31)],
                   [.040, .120, .105, .010], [.026, .065, .052, .007],
                   normal=(sign, -.25, 0), sides=6, steps=2,
                   material=i % 2)
  # Back locks overlap downwards; their restrained tips stay near shoulders.
  for i in range(7):
    theta = 1.4 + i * (math.tau - 2.8) / 6
    s, c = math.sin(theta), math.cos(theta)
    z = 1.96 + .09 * abs(s)
    builder.lock([(s * .18, .045 - c * .19, 3.10),
                  (s * .48, .04 - c * .53, 2.82),
                  (s * .52, .045 - c * .56, 2.40),
                  (s * .555, .05 - c * .595, z)],
                 [.024, .137, .13, .012], [.020, .052, .054, .009],
                 normal=(s, -c, 0), sides=6, steps=3,
                 material=i % 2)
  return hairMesh(ctx, 'flowing_hair', builder, [White, WhiteShade])


def taperedBeard(ctx):
  """Wrap the jaw with an open upper lip and broad white tapered locks."""
  builder = HairBuilder()
  jaw(builder, top=lambda theta: 2.042 + .275 * abs(math.sin(theta)) ** 3,
      bottom=lambda theta: 1.76 + .36 * abs(math.sin(theta)) ** 1.65,
      width=lambda theta: .13 + .29 * abs(math.sin(theta)),
      depth=.485, centerY=.005, thickness=.056)
  for sign in [-1, 1]:
    builder.lock([surface(sign * .463, 2.30, .004),
                  surface(sign * .39, 2.18, .02),
                  (sign * .28, -.425, 1.97),
                  (sign * .20, -.43, 1.86)],
                 [.009, .078, .09, .008], [.008, .04, .043, .007],
                 normal=(sign * .3, -1, 0), sides=6, steps=2)
    builder.lock([surface(sign * .16, 2.035, .010),
                  (sign * .17, -.493, 1.97),
                  (sign * .13, -.515, 1.86),
                  (sign * .050, -.485, 1.74)],
                 [.026, .105, .09, .008], [.018, .047, .043, .007],
                 sides=6, steps=2)
    builder.lock([surface(sign * .018, 2.199, .029),
                  surface(sign * .115, 2.18, .065),
                  surface(sign * .265, 2.14, .071),
                  surface(sign * .385, 2.145, .050)],
                 [.020, .066, .070, .009], [.020, .046, .045, .008],
                 sides=6, steps=2)
  builder.lock([surface(0, 2.036, .015),
                (0, -.52, 1.985), (0, -.552, 1.85),
                (0, -.512, 1.73)],
               [.025, .114, .096, .007], [.018, .054, .049, .007],
               sides=6, steps=2)
  return hairMesh(ctx, 'tapered_beard', builder, [White])


def build(ctx):
  """Return three independent rigid head attachments without modifying skin."""
  return [part(ctx, 'Headgear', 'Zeus laurel crown', circlet(ctx)),
          part(ctx, 'Hair', 'Zeus hair', flowingHair(ctx)),
          part(ctx, 'Beard', 'Zeus beard', taperedBeard(ctx))]
