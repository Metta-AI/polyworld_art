# Mirrored fort kit

Open `fort_kit.blend` in Blender. Both structure atlases and the tree foliage
atlas are packed into the file.

## Editing

- Scene `01 Rebuilt mirrored fort kit` contains the twenty rebuilt assets.
- Each faction occupies one row, dark at Y=7 and light at Y=0. In each row,
  towers run left to right as level 1, level 2, level 3, followed by the
  other structures.
- Scene `02 Generated GLB references` contains all 18 original Meshy and Tripo
  outputs for comparison.
- Barracks, pillars, and wall panels have live X/Y Mirror modifiers. Edit the
  quarter mesh to change all four quadrants.
- Towers have a live Array modifier with six copies and a 60-degree offset
  empty. Edit the seed sector to change all six sides.
- Each tower flag is a separate object facing -Y, with no symmetry modifier.
- Move an asset's root empty to move its mesh and symmetry controls together.
- Mesh vertex groups name the structural parts. `TrimUV` maps each face into
  an atlas tile. The integer face attribute `trim_tile` records its tile ID.
- The two 4x4 sheets use the same material layout. Their exact pixel bounds
  and nine-pixel UV insets are recorded in `manifest.json`.

## Deliverables

- `fort_kit.blend`: editable source with live modifiers and packed images.
- `models/dark` and `models/light`: individual GLBs with symmetry applied and
  the corresponding trim texture embedded. Exports use ground-level origins.
- `textures`: the structure atlases, supplied tree atlas, and source metadata.
- `previews`: renders of every rebuilt model, plus reverse tower and barracks
  views and a complete kit overview.
- `verification.json`: checks against the saved Blender file and exported GLBs.

The wall panels are 4 meters long. Their planar ends connect to pillar modules.

## Gameplay attachment points

- All six towers export one meshless node named `fire`, centered on the
  main crystal's vertical bounds and the tower axis.
- Both barracks export one meshless node named `spawn` at the front door's
  threshold, 0.05 meters outside the door. The front is Blender -Y.
- Attachment empties are parented to each asset's root. Their Blender names
  include the asset prefix because Blender object names must be unique.
  The `attachment` property is `fire` or `spawn`. The builder uses that exact
  bare name in each individual GLB.
- `manifest.json` records asset-local Blender positions. GLB positions use
  Y up, converted from Blender coordinates as `(x, z, -y)`.

These points add no triangles. They move with the model and are independent
of the layout used to display all models together in Blender.

## Triangle counts

Counts include every mirrored or radial copy and the separate tower flags.

| Faction | Model | Triangles |
| --- | --- | ---: |
| dark | tower_level2 | 210 |
| dark | tower_level1 | 234 |
| dark | tower_level3 | 246 |
| dark | barracks | 232 |
| dark | pillar | 128 |
| dark | wall | 104 |
| dark | tree_1 | 188 |
| dark | tree_2 | 118 |
| dark | tree_3 | 172 |
| dark | tree_4 | 248 |
| light | tower_level1 | 234 |
| light | barracks | 220 |
| light | pillar | 176 |
| light | wall | 176 |
| light | tower_level2 | 234 |
| light | tower_level3 | 240 |
| light | tree_1 | 206 |
| light | tree_2 | 172 |
| light | tree_3 | 228 |
| light | tree_4 | 248 |

Every model is below 250 triangles. No decimation is used.

## Dead trees

The original `tree_1.glb` now spreads its branches forward and backward as
well as left and right. Three additional trees share its angular trunk,
crooked limbs, tapered tips, roots, and dark bark trim texture.

| Export | Shape | Branches | Triangles |
| --- | --- | ---: | ---: |
| `models/dark/tree_1.glb` | Original, with depth | 5 | 188 |
| `models/dark/tree_2.glb` | Short and sparse | 2 | 118 |
| `models/dark/tree_3.glb` | Wide and spreading | 4 | 172 |
| `models/dark/tree_4.glb` | Tall and heavily branched | 7 | 248 |

Branch counts exclude the main trunk and roots. All four are editable in
the same Blender file, grouped two by two at the right of the dark faction.
Vertex groups name each trunk, branch, and root. Their lowest root sits at
the ground-level origin. `manifest.json` records dimensions for each tree.

`previews/dead_trees.png` compares the four trees in the table order at the
same scale. Each also has a separate side preview ending in `_side.png`.
The three supplied style screenshots are saved in `references` and packed
into the reference scene.

## Light trees

| Export | Shape | Trunk triangles | Foliage quads | Total triangles |
| --- | --- | ---: | ---: | ---: |
| `models/light/tree_1.glb` | Evergreen | 68 | 69 | 206 |
| `models/light/tree_2.glb` | Small leafy tree | 94 | 39 | 172 |
| `models/light/tree_3.glb` | Medium leafy tree | 124 | 52 | 228 |
| `models/light/tree_4.glb` | Large leafy tree | 138 | 55 | 248 |

Each GLB contains exactly two meshes named `trunk` and `foliage`. The foliage
is separate, disconnected quads with double-sided alpha masking at a 0.45
cutoff. Both meshes share `tree_foliage_atlas.png`. The trunk uses its bark
strip and remains opaque. Foliage uses its grayscale cutouts.

The canopy uses the supplied v5 atlas and staggered radial rings. Every
branch is one square quad. Its attachment points inward toward the trunk;
its tip extends outward and downward. Lower rings start farther from the
trunk, with their inner ends covered by foliage from the ring above.

The evergreen has five rings following a cone. The leafy trees have four
rings following a rounded crown, with shallow slopes at the top and steeper
slopes around the sides. Small variations in rotation, radius, size, height,
and slope break up regular patterns. Upper rings use light atlas tiles and
lower rings use progressively darker tiles. The evergreen trunk has roots
and no wooden side branches.

The saved Blender materials and GLBs use white tint factors. The engine can
multiply the `foliage` material by any color while retaining the brown trunk.
Preview PNGs use example green and orange tints. In Blender, the `Engine tint`
node on each `Tree foliage` material controls this preview color.

`TreeUV` maps each face into the supplied atlas. `tree_atlas_tile` records
the tile. `foliage_ring` and the named `Ring 01` vertex groups identify
each ring from the crown down. `manifest.json` records the ring profiles.
All cards remain individual quads in Blender and export as two triangles
apiece. Their UVs preserve the square pixels of the supplied artwork.

The light trees occupy a two-by-two group on the light side. See
`previews/light_trees.png` for the primary comparison, viewed from 63 degrees
above the ground. `light_trees_top.png` is directly overhead, and
`light_trees_profile.png` shows the side silhouettes. Individual trees have
matching primary, `_top.png`, and `_side.png` previews. The supplied v5 atlas,
style image, and ring-layout diagram are packed in the Blender file.
The v5 atlas pixels are preserved. Its original source metadata is saved
in `textures/tree_foliage_atlas_source.json`.

## Texture layout

Tiles are numbered left to right, top to bottom. The face attribute uses
zero-based tile IDs.

| Row | Column 1 | Column 2 | Column 3 | Column 4 |
| --- | --- | --- | --- | --- |
| 1 | Masonry | Dressed stone | Edge trim | Paving |
| 2 | Roof shingles | Timber | Metal | Door |
| 3 | Cloth | Heraldry | Magic glow | Crystal |
| 4 | Bark | Foundation/plaster | Reinforcement | Recess |

## Light tower upgrades

The level 1 tower is uniformly scaled to match the dark level 1 tower's
3.97-meter height. Its flag and `fire` point move with it. UV coordinates
and triangle counts are preserved.

- `models/light/tower_level2.glb`: compact stone crown, a single central
  crystal, and gold shaft edging. 234 triangles.
- `models/light/tower_level3.glb`: taller shaft, larger central crystal,
  six smaller crown crystals, gold pedestals, and sapphire belt ornaments.
  240 triangles.

Both are separate assets in the main Blender scene. Their sixfold radial
arrays remain editable. Each has a separate front-only flag. They share
`light_trim.png` and use the verified proportionate UV mapping.

The two supplied concept images are saved in `references` and packed into
Blender's reference scene. `previews/light_tower_levels.png` shows all three
light towers together, ordered level 1, level 2, level 3 from left to right.

## Dark tower upgrades

- `models/dark/tower_level1.glb`: shorter tapered shaft, broad foot supports,
  modest crown horns, an ember well, and a small ruby. 234 triangles.
- `models/dark/tower_level3.glb`: taller shaft, swept horns, larger ruby,
  a glowing crown band, and longer pointed ember slits. 246 triangles.
- `models/dark/tower_level2.glb` is the existing level 2 tower.

Both new towers use editable sixfold radial arrays and `dark_trim.png`.
Their ember slits replace the front flag in these supplied designs.
The concept images are saved in `references` and packed into the reference
scene. `previews/dark_tower_levels.png` shows all three dark towers together,
ordered level 1, level 2, level 3 from left to right at the same scale.

## Texture proportions

Stone, masonry, roof shingles, metal, crystal, and recess surfaces use an
orthogonal projection onto each face plane. Both texture directions use the
same physical pixel scale, normally 128 pixels per meter. Thin or narrow
faces crop a smaller region of the atlas instead of stretching a full tile.
Large faces reduce density uniformly only when needed to stay inside a tile.

Wood grain, bark, cloth, door artwork, heraldry, and glow artwork retain their
purposeful mapping. No extra geometry was required for the UV correction.

Verification measures the two principal pixel scales on every triangle using
proportionate mapping, including mirrored and radial copies. The allowed
ratio is 1.001 or less; the measured maximum is below 1.00001.

## Rebuilding

Run Blender in background mode with `tools/build_forts.py -- --render` to
rebuild this pack and its previews. This replaces the generated Blender file
and GLB exports, so preserve manual edits before rebuilding.

Run Blender in background mode with `tools/verify_forts.py` to check the saved
file. Verification checks evaluated counts, sixfold radial symmetry, X/Y
mirror symmetry, front-only flags, packed textures, UV tile insets,
self-contained GLB resources, attachment names and positions, and the
trees' branch counts, canopy depth, and ground-level origins. Light tree
checks also cover separate meshes, grayscale tint, alpha masking, individual
quads, upward-facing surfaces, outward and descending branch directions,
overlapping rings, and darker tiles on lower rings.

If the original generated GLB folder has been removed, rebuilding reuses
the original references already packed into `fort_kit.blend`.

License: generated
