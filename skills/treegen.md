---
name: treegen
description: Generate and reuse Polyworld trees at runtime, tune tree recipes, and create compatible foliage trim sheets, crown caps, bark, and stump textures. Use for procedural forests, tree placement, tree styles, and custom leaf artwork.
---

# Tree Gen

Generate trees at runtime to save download and disk space. Ship recipes, seeds,
placements, and shared textures. Call the generator when loading a scene or
chunk, keep its output, and use those trees in the game. Do not generate them
every frame or export a GLB for every tree variation.

Use the public [`polyworld/treegen` module](../../polyworld/src/polyworld/treegen.nim).
It returns ordinary `gltf.Node` objects containing meshes, normals, UVs, vertex
colors, and materials. The existing renderer uploads them to the GPU. Games
do not need to import an experiment or export and reload model files.

## Generate and use a tree

Start with a preset so every setting has a valid default:

```nim
import
  vmath,
  polyworld/treegen

var settings = treegen.preset(3, seed = 42)
settings.leafColor = vec3(0.22, 0.48, 0.24)
settings.barkColor = vec3(0.43, 0.31, 0.19)
let tree = treegen.generate(settings)
tree.pos = vec3(12, 0, 8)
```

Add `tree` to the scene's nodes or pass it to the existing toon renderer with
`toon.draw(tree)`. Place the tree's local ground level at the terrain surface;
root claws extend slightly below it. Use the game's normal resource cleanup
when unloading generated models, after their placements have finished using
them.

The same settings and seed reproduce the same geometry with the same generator
version. Store the complete recipe when overrides matter. A seed alone does
not preserve appearance across changes to presets, textures, or the generator.

### Generate a small bank of reusable variants

`generate` loads its own materials each time. For a forest, load shared
materials once and generate a small bank of variants:

```nim
import
  gltf,
  polyworld/treegen

var settings = treegen.preset(3)
let materials = treegen.loadMaterials(settings.barkTexture)
treegen.tint(materials, settings)
var variants: seq[Node]
for i in 0 ..< 10:
  settings.seed = 42 + i
  let tree = treegen.treeNode(
    treegen.generateGeometry(settings),
    materials
  )
  tree.name = "Spruce" & $i
  variants.add tree
```

Choose from this bank for placements, with different positions, rotations, and
scales. Use distinct placement nodes sharing the generated meshes, or the
terrain prop system. Changing one node's transform repeatedly does not create
independent scene placements. Runtime generation saves stored model data;
generated meshes still take CPU time and memory.

For an existing game integration, follow
[`polyworld/groves`](../../polyworld/src/polyworld/groves.nim). It generates
variants, shares texture images, and creates named `PropPack` models. Use
`createPropPack(nodes, textureSize = GeneratorTextureSize, repeatTexture = true)`
with an active graphics context; repeating UVs are needed for bark.
`placeProp` queues placements for a terrain mesh bake, while `drawProp` draws
a named model immediately. A baked terrain mesh is not GPU instancing.

Materials are references. Calling `tint` changes all nodes sharing those
materials. To give variants independent colors, copy each `Material` object
while retaining its shared texture image, as `groves.nim` does. Copying only the
`TreeMaterials` container still shares its materials. Load a separate material
group when `barkTexture` changes, because that setting changes image pixels.

### Public functions

| Function | Purpose |
| --- | --- |
| `preset(index, seed = 42)` | Return a complete `TreeSettings` recipe. |
| `validate(settings)` | Check ranges; invalid recipes raise `TreegenError`. Generation also validates. |
| `generate(settings): Node` | Convenient single-tree generation with loaded, tinted materials. |
| `generateGeometry(settings): TreeGeometry` | Build CPU mesh data and bounds without loading textures or needing a GPU context. |
| `loadMaterials(textureStrength): TreeMaterials` | Load bark, foliage, and cut-wood materials. Pass `settings.barkTexture`. |
| `tint(materials, settings)` | Update bark and foliage RGB multipliers without rebuilding geometry. |
| `treeNode(geometry, materials): Node` | Build a renderable node using existing materials. |

Qualify calls with `treegen.` when other generators also export `preset` or
`generate`.

## Presets and shape controls

| Index | Preset | Kind |
| --- | --- | --- |
| 0 | Old oak | Broadleaf |
| 1 | Autumn | Broadleaf |
| 2 | Round sapling | Broadleaf |
| 3 | Blue spruce | Evergreen |
| 4 | Tall fir | Evergreen |
| 5 | Young pine | Evergreen |
| 6 | Haunted | Leafless |
| 7 | Twisted | Leafless |
| 8 | Dead sapling | Leafless |
| 9 | Stump | Stump |

| Settings | What to change |
| --- | --- |
| `height`, `trunkRadius`, `taper`, `bend`, `twist` | Trunk size and silhouette. |
| `radialSides`, `trunkSegments`, `branchSegments` | Woody mesh complexity. |
| `branches`, `forks`, `branchKind`, `branchLayout` | Woody limbs, branching depth, bends, and arrangement. These are not leaf-card counts. |
| `branchLength`, `branchRadius`, `branchMinimum` | Limb length, thickness, and cutoff for thin twigs. |
| `roots`, `rootSpread`, `rootThickness`, `rootClaw`, `rootAngle` | Root count, spread, and downward claw tips. `rootAngle` is in degrees. |
| `stemClearance` | Exposed stem below the foliage. |
| `crownRadius`, `crownHeight`, `crownBase`, `crownShape` | Canopy envelope. |
| `crownCoverage` | Broadleaf vertical coverage; the default 0.75 omits the bottom quarter of the full envelope. |
| `rings`, `cardsPerRing`, `density`, `packing`, `shells` | Foliage amount and coverage. More shells and cards cost geometry. |
| `ringSpacing`, `ringOffset`, `irregularity` | Ring spacing, offsets, and unevenness. |
| `leafSize`, `leafWidth`, `droop`, `curl`, `leafJitter` | Card dimensions, slope, crease, and variation. |
| `capSize`, `capSlope` | Crown-cap coverage and broadleaf cap slope. Evergreen caps follow the cone profile. |
| `leafTile` | Broadleaf texture family: `MixedLeaves`, `SoftLeaves`, `LobedLeaves`, or `PointedLeaves`. |
| `separateLeaves` | Keep enabled to resolve intersections between opaque leaf regions. |
| `leafColor`, `barkColor`, `colorVariation` | RGB tint and seeded card shading; keep variation at 0 for uniform card brightness. |
| `barkDensity`, `barkTexture` | Bark repeats per world unit and texture strength. |

The foliage follows offset radial rings. Evergreens use a cone envelope with
more cards around wider lower rings, rather than larger leaves at the bottom.
The generator already applies a 1.5 multiplier to evergreen foliage density.
Broadleaf trees use a partial rounded envelope. Leafless trees and stumps have
no leaf cards or foliage caps.

Do not treat `rings * cardsPerRing` as an exact final count. Packing, the cone
width, and collision resolution affect it. Inspect `TreeGeometry.cards`,
`omittedCards`, `shiftedCards`, and mesh index counts when tuning a budget.

## Shared textures and packaging

All three runtime images must be **512x512 PNGs**:

| Asset | Contract |
| --- | --- |
| [tree-foliage-atlas.png](../terrain/treegen/tree-foliage-atlas.png) | White/grayscale leaves and caps on transparency, arranged as described below. |
| [bark.png](../terrain/treegen/bark.png) | Separate opaque bark texture, seamless horizontally and vertically. |
| [stump-rings.png](../terrain/treegen/stump-rings.png) | Painted cut wood. Preserve the current ring center and coverage. |

`polyworld/assets` exposes `TreegenTextures` and `GeneratorTextureSize`.
The material loader reads all three images, even for a leafless tree. Native
`DataRoot` is `../polyworld_art`, relative to the working directory; normally
run from the sibling `polyworld` repository. Browser builds use
`/polyworld_art`. Add `imageAsset(path, GeneratorTextureSize)` for each path in
`TreegenTextures` to the game's asset list so the files are available there.

Bark is converted to neutral luminance on load and multiplied by `barkColor`.
Its UVs use physical distances, so `barkDensity` gives consistent detail size
across trunks, branches, and roots. Preserve repeat sampling in both axes.
Stump cuts retain their painted texture colors and use a fixed planar scale:
wider trunks reveal more rings. Keep the ring center at approximately
`(0.61, 0.5)` in normalized texture coordinates when replacing that asset.

## Foliage trim sheet layout

The sheet is a **4x4 grid of 128x128 cells**. There are no gutters between
cells. Rows and columns below start at zero from the image's top left;
`tile = row * 4 + column`.

| Row | Column 0 | Column 1 | Column 2 | Column 3 |
| --- | --- | --- | --- | --- |
| 0 | 0: Evergreen cap | 1: Broadleaf cap | 2: Broadleaf cap | 3: Broadleaf cap |
| 1 | 4: Soft leaves | 5: Soft leaves | 6: Lobed leaves | 7: Pointed leaves |
| 2 | 8: Soft leaves | 9: Lobed leaves | 10: Lobed leaves | 11: Pointed leaves |
| 3 | 12: Evergreen | 13: Evergreen | 14: Evergreen | 15: Evergreen |

`MixedLeaves` chooses from tiles 4 through 11. The other broadleaf families use
their listed tiles. Evergreen cards choose tiles 12 through 15. Evergreen caps
use tile 0; broadleaf caps choose one of tiles 1 through 3 using the seed.
The first row contains foliage caps, not bark strips.

### Leaf cards: attachment at the top

- Paint a leaf cluster with its branch attachment at the **top center** of the
  cell and its hanging tips toward the bottom. The card's top attaches inward
  toward the trunk; its bottom extends outward and down.
- Each card has two joined panels with a center crease: six vertices and four
  triangles. Keep the artwork continuous across that crease.
- Tile-local UVs run from 0.01 to 0.99 in each direction. Atlas coordinates are
  `(column + 0.01 + localU * 0.98) / 4` and
  `(row + 0.01 + localV * 0.98) / 4`. Keep transparent padding **inside** each
  cell; do not shift the grid by adding gutters.
- Use broad, overlapping clusters with substantial opaque coverage. Sparse
  twig sprays leave holes even when many cards are generated.
- Keep foliage neutral white/grayscale for runtime RGB tinting. Give all tiles
  similar overall brightness, with a little gray near the attachment fading
  toward white tips. Preserve painted veins and leaf detail. Do not make whole
  columns progressively darker.
- Export real transparency, without a background, grid lines, or labels.
  Interiors should be opaque and only edges antialiased. The material is
  double-sided with an alpha cutoff of 0.45; faint translucent leaves vanish.

### Crown caps: a full radial disk

Paint each first-row cell as a top-down leafy disk with a filled center and
leaves pointing outward in every direction. Do not paint a hollow ring or a
side-view branch.

The cap is a connected **24-triangle fan**, with a raised center and lower rim.
It samples a circle of radius 0.49 around the cell's center `(0.5, 0.5)`.
Keep visible pixels within roughly radius **0.48 of the cell width** (about
61 pixels at runtime), so the polygon edges do not cut them off. Leave
transparent corners. Preserve opaque coverage through the center and enough
coverage near the rim to meet the upper leaf ring.

## Create a new tree style

1. For color changes, use `leafColor` and `barkColor`. For shape changes, tune a
   preset. New painted foliage needs a new compatible trim sheet.
2. Use the current atlas as a layout reference. Generate or paint the same
   sixteen cell roles, preserving attachment orientation and cap disks. The
   imagegen skill is appropriate for new artwork or semantic edits.
3. Keep a high-resolution master, then export an eight-bit RGBA **512x512**
   runtime image with alpha-aware resizing. Inspect the result at that size;
   tiny stems, edge padding, and cap coverage must survive downsampling.
4. The default `loadMaterials` has fixed asset paths, not a custom-path
   argument. A project-wide replacement can use the existing filenames. For
   an additional game-specific style, keep separate assets and explicitly
   route their images into materials before rendering. Preserve samplers,
   alpha settings, and matching collision outlines; changing the PNG alone
   is insufficient when leaf silhouettes change.
5. When alpha silhouettes change, regenerate the collision outlines from the
   **final runtime atlas**. From the sibling `polyworld` repository, run:

   ```sh
   python3 tools/gen_tree_trims.py
   ```

   This Pillow-based tool reads the default atlas and writes
   `src/polyworld/treegen/trims.nim`. The generator uses these outlines to
   separate opaque leaf regions. A pure RGB recolor with identical alpha does
   not need new outlines. Simultaneous atlases with different silhouettes need
   explicit per-style outline support; the current generator has one shared
   outline table.
6. Update [atlas metadata](../terrain/treegen/atlas.json) and record new art's
   provenance following [CONTRIBUTING.md](../CONTRIBUTING.md). Package any
   additional runtime texture paths in the game's asset list.

Example image-generation prompt, with the current atlas attached:

> Create a stylized tree foliage trim sheet using this exact 4x4 layout with
> equal cells and no gutters, borders, labels, or background. Row one contains
> four top-down radial foliage disks with filled centers: an evergreen cap,
> then three broadleaf caps. Keep each disk inside a circle of radius 48% of
> its cell width. Rows two and three contain broadleaf clusters matching the
> reference cell families. Row four contains four evergreen sprays. Every
> branch cluster attaches at the top center and hangs toward the bottom. Use
> neutral white and grayscale leaf detail, consistent brightness across cells,
> and subtle gray shading only near the attachment. Keep broad opaque leaf
> coverage, transparent margins, and no baked bark or cast shadows.

## Verify a changed recipe or atlas

From the `polyworld` repository:

```sh
nim check experiments/treegen/treegen.nim
nim r experiments/treegen/tests/tests.nim
nim c -o:/tmp/treegen experiments/treegen/treegen.nim
/tmp/treegen --preset=3 --seed=42 --gallery
```

Also preview a broadleaf preset and a stump. Orbit around several seeds and
inspect top, side, and underside views. Check for a closed crown, leaf
intersections, visible far-side undersides, atlas bleed, ground clearance,
and consistent bark density. The tests cover deterministic geometry, UVs,
cap coverage, and leaf separation. The experiment is the authoring preview;
games continue to call the public runtime generator.
