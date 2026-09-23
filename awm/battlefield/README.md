# Old Crossroads stone material

Prepared by `polyworld/examples/awm/tools/render_stone_normals.nim`.
All three 512×512 textures repeat seamlessly and contain linear data.

- `stone-slab-normal.png`: tangent-space OpenGL +Y normals with broad natural
  fracture faces and weathered ledges, conditioned from `source/rock-normal.png`.
  One repeat covers two world units. The source was created with the built-in
  image generation tool using the user's stone normal as a visual reference;
  the exact prompt is in `source/prompt.txt`.
- `stone-grain-normal.png`: tangent-space OpenGL +Y normals for fine pits and
  grain; one repeat covers 0.35 world units.
- `stone-weathering.png`: restrained mineral color variation, with
  no directional light baked into the texture.

Normals are opaque RGB unit vectors encoded from −1…1 to 0…255. Upload as
RGBA8, not sRGB; use repeat wrapping and trilinear mipmap filtering. The
renderer combines the two normal scales as slopes and re-normalizes the
world-space result. Normal strength is kept independent of mesh shadow bias.

The builder reduces source slope strength, matches opposing edges in a narrow
smooth strip and re-normalizes every output texel. Fine grain uses periodic
heights and derivatives. Asset rebuilds are deterministic and do not affect
gameplay randomness. Only the prepared textures are shipped in the web pack.
