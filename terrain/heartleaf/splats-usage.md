# Heartleaf splats

The nine splats in terrain/stamps use the same heartleaf-grass-1 through -3,
heartleaf-path-1 through -3 and heartleaf-paving-1 through -3 base names as
the repeating tiles. Each has a 256x256 .rgb.png color file with RGBA coverage
and a 256x256 .height.png opaque grayscale relief file.

Use the repeating tiles as the base. Scatter grass and dirt splats with
irregular spacing, mixed variants, rotation and modest size changes.
A useful starting range is 0.8 to 1.2 times the base tile's world size.
Avoid a regular stamp grid. Moderate overlap breaks repeated landmarks,
while too many translucent layers can soften the painted facets.

Keep paving orientation and scale consistent. Use paving splats for worn
patches over grass or earth. Randomly rotating different paving patterns on
top of existing paving can create crossing joints and doubled stones.
Grass or dirt encroachment is a better way to break up a paved surface.

Color is sRGB with straight alpha. Height is linear data and uses white for
higher surfaces. Sample color and height with identical coordinates and
transforms. Clamp stamp textures at their transparent borders.

Use the color alpha as coverage for both channels. The height file is opaque
and zero outside the covered footprint. When transforming or filtering
height, use the color alpha as its stencil so empty pixels do not pull edge
heights toward zero. Do not multiply the physical height value by opacity.

Ordinary alpha blending gives soft transitions. The bundled height-blending
helper gives a sharper material boundary. Tune blend strength and depth for
the desired softness rather than assuming the default fits every material.
Its surface heights must update after each stamp.

The included temporary previews compare light and dark backgrounds, alpha
and height overlap, and repeated tiles with varied splats. They were rendered
with the repository's Nim/Pixie helpers, not the game engine. These assets
have not been wired into runtime terrain rendering in this task.
