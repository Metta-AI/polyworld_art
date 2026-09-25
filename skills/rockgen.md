---
name: rockgen
description: Generate renderable Polyworld rocks at runtime, tune their shape and surface settings, and create compatible grayscale rock trim atlases. Use for procedural rock placement, buried rocks, rock style changes, and rock texture authoring.
---

# Rock Gen

Generate rocks at runtime to save download and disk space. Store a preset or
`RockSettings`, seed, and placement for each rock, together with one shared trim
atlas. Generate nodes when loading a scene or chunk and retain them for rendering.
Generating every frame wastes work. Runtime generation still uses CPU time and
mesh memory; sharing materials also avoids loading a texture for every rock.

Use the public [`polyworld/rockgen` module](../../polyworld/src/polyworld/rockgen.nim).
It returns normal `gltf.Node` objects with mesh, normals, UVs, vertex colors,
and material. Games do not need experiment imports or a GLB export/load step.

## Generate and render

Start from a preset so all fields have valid defaults:

```nim
import
  vmath,
  polyworld/rockgen

var settings = rockgen.preset(0, seed = 42)
settings.tint = vec3(0.69, 0.72, 0.83)
settings.floorCut = 0.1
let rock = rockgen.generate(settings)
rock.pos = vec3(12, 0, 8)
```

Add `rock` to the scene's nodes, or pass it to an existing toon renderer with
`toon.draw(rock)`. The renderer handles GPU upload. Release replaced or unloaded
nodes with the game's usual GPU resource cleanup, such as `rock.clearFromGpu()`
with the rendering context active.

The current atlas is [terrain/rockgen/rock-trim-atlas.png](../terrain/rockgen/rock-trim-atlas.png),
an eight-bit **512x512 PNG** loaded at runtime. It is not embedded in the code.
Native `DataRoot` is `../polyworld_art`, relative to the working directory;
normally run from the sibling `polyworld` repository. Browser builds use
`/polyworld_art`. Add this entry to the game's asset list using `polyworld/assets`:

```nim
result.add imageAsset(RockgenTexture, GeneratorTextureSize)
```

That packages the shared image for the browser's virtual filesystem. The
default material loader requires exactly 512x512 pixels.

### Public functions

| Function | Use |
| --- | --- |
| `preset(index, seed = 42): RockSettings` | Get a complete recipe. Indices are 0 through 8. |
| `validate(settings)` | Check supported ranges; generation also calls it. Invalid settings raise `RockgenError`. |
| `generate(settings): Node` | Build one rock with its own loaded atlas and tinted material. |
| `loadMaterials(): RockMaterials` | Load the shared atlas and a white diagnostic material once. Fields are `stone` and `regions`. |
| `tint(materials, settings)` | Set the stone material's RGB multiplier without rebuilding geometry. |
| `generateGeometry(settings): RockGeometry` | Get the raw mesh, face information, bounds, and detail count. No texture loading or GPU context is needed. |
| `rockNode(geometry, materials, showRegions = false): Node` | Convert geometry using existing materials. Diagnostic mode shows edge, fill, and detail regions. |
| `tileUv(tile, point): Vec2` | Map tile-local coordinates in 0..1 to a padded atlas cell; useful when extending the generator. |

Qualify calls with `rockgen.` when importing other generators with names such as
`preset` or `generate`.

### Share materials across many rocks

```nim
import
  gltf, vmath,
  polyworld/rockgen

var settings = rockgen.preset(4)
let materials = rockgen.loadMaterials()
rockgen.tint(materials, settings)
var rocks: seq[Node]
for i in 0 ..< 20:
  settings.seed = 42 + i
  let rock = rockgen.rockNode(
    rockgen.generateGeometry(settings),
    materials
  )
  rock.pos = vec3(i.float32 * 3, 0, 0)
  rocks.add rock
```

Each node has its own mesh, while all these rocks share the material and atlas.
Changing `materials.stone.baseColorFactor` or calling `tint` changes every node
using that material. Use separate materials for separate tint groups.

## What the rocks are

The generator cuts an irregular convex block into large, flat polygonal faces,
then bevels corners and chips selected points. These are solid low-poly rock
shapes; caves, arches, and deeply concave silhouettes need other geometry.
The same recipe and seed reproduce the same geometry with the same generator
version. Keep recipes and seeds if rocks must survive reloads consistently.

Each face combines three regions:

- A band of triangles around its perimeter samples the worn-edge trim.
  Only selected edges show wear; other edges use the solid fill.
- The center samples a solid rock color. Flat normals define the large planes,
  with face shading and a seeded vertex-color wash adding variation.
- An optional rotated square samples a crack or scuff. The surrounding mesh is
  triangulated to meet the square. This is coplanar surface detail, not a decal
  hovering above the rock or a crack cut into its silhouette. Small faces and
  the underside omit these patches.

Uncut rocks stand on local Y=0, with width along X and depth along Z. Floor cuts
leave the remaining rock at local Y=0 too; place the node at terrain height.

### Presets and controls

| Index | Preset | Index | Preset | Index | Preset |
| --- | --- | --- | --- | --- | --- |
| 0 | Tall angular | 3 | River stone | 6 | Low wedge |
| 1 | Low compact | 4 | Forest pebble | 7 | Leaning shard |
| 2 | Broken slab | 5 | Upright fieldstone | 8 | Broad boulder |

| Settings | Supported range | Effect |
| --- | --- | --- |
| `seed` | 0..1,000,000,000 | Silhouette, chips, worn edges, patches, and surface variation. |
| `width`, `height`, `depth` | 0.5..8, 0.5..10, 0.5..8 | Original dimensions in world units, before floor cutting. |
| `sides`, `crownCuts` | 4..12, 3..12 | Number of side and upper cutting planes, not final face or triangle counts. |
| `irregularity` | 0..0.4 | Uneven angles, slopes, and distances. |
| `taper`, `lean` | -0.3..0.45, -0.5..0.5 | Side slope and sideways lean. Positive taper narrows upward. |
| `crown`, `shoulder` | 0.4..1.6, 0..0.85 | Upper-plane slope and shoulder placement. |
| `cornerClip` | 0..0.45 | Amount removed from vertical corners. |
| `chips`, `chipSize` | 0..12, 0..0.25 | Number and depth of local corner cuts. |
| `trimWidth`, `trimChance` | 0..0.4, 0..1 | Fractional face inset and probability of worn edges. Zero disables visible trim. |
| `detailChance` | 0..1 | Probability of a patch on eligible faces. |
| `detailSize`, `detailOffset` | 0.15..0.9, 0..0.6 | Patch size and offset relative to available face clearance. |
| `detailKind` | `Mixed`, `Cracks`, `Scuffs` | Choose atlas cells 5..15, 5..10, or 11..15 respectively. |
| `shadeVariation`, `mottling` | 0..0.4 each | Face-to-face shading and the vertex-color surface wash. |
| `tint` | RGB components 0..1 | Multiply the grayscale texture by a color. |
| `fillSubdivisions` | 0, 1, 2 | Extra fill vertices for finer wash, without changing shape. Defaults to 0; skipped when mottling is 0. |
| `removeBottom` | Boolean | Omit the flat ground-contact cap while preserving the other surfaces. |
| `floorCut` | 0..0.9 | Remove this fraction of the original height, lower the remainder, and leave an open base. |

Use `floorCut = 0.1` for 10% burial or `0.9` for 90%. This clips the triangles
and interpolates UVs at the cut, including partial detail patches. It does not
create a bottom cap, so there is no horizontal rock face to z-fight with the
floor. Every positive floor cut opens the base regardless of `removeBottom`.

Keep `fillSubdivisions = 0` for ordinary gameplay. The nine default presets at
seed 42 use roughly 322 to 440 triangles. Extra fill triangles refine the wash,
not the rock outline or painted cracks. Tune silhouette, tint, wear, and patch
density before increasing subdivisions.

## Trim atlas layout

The atlas has a **4x4 grid of 128x128 cells**, without drawn grid lines, borders,
labels, or gutters. Read rows from the image's top left. IDs are zero-based,
row-major: `tile = row * 4 + column`.

| Row | Column 1 | Column 2 | Column 3 | Column 4 |
| --- | --- | --- | --- | --- |
| 1 | 0: Edge trim | 1: Edge trim | 2: Edge trim | 3: Edge trim |
| 2 | 4: Solid fill | 5: Crack | 6: Branched crack | 7: Vertical crack |
| 3 | 8: Fissure | 9: Impact crack | 10: Paired cracks | 11: Scuff |
| 4 | 12: Scrapes | 13: Chip | 14: Wear | 15: Crack and scuff |

The mapping is more specific than just placing art somewhere in each cell:

- **Fill:** every fill vertex uses `FillUv = (0.125, 0.375)`, the center of
  cell 4. Painting noise across that cell will not spread it across a face.
  Keep this sampled color and every patch's background consistent.
- **Edges:** only a narrow line near the very top is sampled. The outer edge
  uses atlas `V = 0.020`, and the inner band boundary uses `V = 0.008`, about
  rows 10 and 4 at 512 pixels. The inner sample should blend into the fill;
  the outer sample should catch the chipped upper lip. Do not center the line
  vertically in the 128-pixel cell or put a border around all four sides.
- **Edge length:** each edge samples a randomized U segment 0.08 atlas units
  wide, about 41 pixels, within one top-row cell. Author each horizontal strip
  to repeat seamlessly left to right. The current mapping uses one segment
  per edge rather than wrapping the whole strip across it.
- **Details:** `tileUv` insets each cell by `TilePadding = 0.003` atlas units,
  about 1.5 pixels. The formula is `(column, row) * 0.25 + 0.003 +
  localUv * (0.25 - 2 * 0.003)`. Leave quiet background around each motif so
  the square boundary disappears against the fill.
- **Filtering:** use linear minification and magnification, clamp to edge, and
  no mipmaps. These are the default material settings. Whole-atlas repetition
  or ordinary mipmaps can mix neighboring cells into the rock surface.

## Make a different style

For a color change, start with `tint`. For a different silhouette, adjust the
recipe. Create another trim atlas when the actual surface treatment should
change, such as smoother worn stone, jagged slate, or broader chalky scuffs.
The texture changes painted detail; it cannot add geometry or change normals.

1. Use the current atlas as the layout reference. Generate or paint a flat,
   opaque grayscale albedo sheet with the same cell roles. The imagegen skill
   is suitable for new artwork and semantic edits. Keep the neutral fill and
   tile backgrounds at the same gray so runtime tinting remains useful.
2. Keep the four top strips horizontally tileable and put their narrow worn
   lip in the exact sampled band. Use a plain gray cell 4, six crack-family
   cells 5..10, and five scuff/wear-family cells 11..15. Details can rotate on
   faces, so avoid a strong directional cast shadow or a scene light baked
   into the sheet.
3. Preserve a high-resolution master. Inspect generated cell boundaries and
   normalize the layout before exporting an eight-bit 512x512 PNG. Check the
   thin top line after resizing; losing it loses the edge treatment. Keep
   pixels opaque, without labels, visible cell outlines, or perspective.
4. Save the variant under `terrain/rockgen/` with a descriptive name and follow
   [the art contribution process](../CONTRIBUTING.md). Keep the standard atlas
   intact when the new style is only for one game or biome.
5. Replace the stone material's image **before its first render**, retaining
   the sampler. `loadMaterials()` has no custom-path argument. For example:

```nim
import
  polyworld/[assets, common, images, rockgen]

let
  settings = rockgen.preset(7)
  materials = rockgen.loadMaterials()
  atlas = loadTexturePng(DataRoot & "/terrain/rockgen/slate-trim.png")
doAssert atlas.width == GeneratorTextureSize
doAssert atlas.height == GeneratorTextureSize
materials.stone.baseColor = atlas
rockgen.tint(materials, settings)
let rock = rockgen.rockNode(rockgen.generateGeometry(settings), materials)
```

Use the generated variant's actual filename. Add its `imageAsset` entry to the
game's browser asset list as well. This example first loads the default
materials, so keep the default atlas available too. Reuse the resulting
materials for the whole style group. A layout or tile-role change requires
updating the generator's UV mapping or detail selection, not just replacing
the PNG.

Example image-generation prompt, with the existing atlas attached:

> Create a flat grayscale albedo trim atlas for stylized low-poly slate rocks.
> Preserve this reference's exact 4x4 cell layout, without grid lines or gutters.
> The four first-row cells contain narrow horizontal chipped-edge strips near
> the image's top border, seamless left to right, with quiet gray above them.
> Row 2 column 1 is plain mid-gray. Cells 5 through 10 contain isolated crack
> variations; cells 11 through 15 contain scuffs, scrapes, a chip, and wear.
> Center each detail on the same opaque gray background, fading to that gray
> before the cell boundary. Use angular painted facets, restrained contrast,
> and no text, perspective, transparency, objects, or cast shadows.

Treat the prompt as an art brief, then verify the exact UV band and pixel layout.
A visually plausible atlas may still miss the strip the generator samples.

## Preview and verify

Run from the sibling `polyworld` repository:

```sh
nim r experiments/rockgen/rockgen.nim
nim r experiments/rockgen/rockgen.nim --sheet --screenshot=tmp/rockgen-sheet.png
```

Use Face regions and Wireframe to inspect trim, fill, and square patches. Check
several seeds, both tall and low presets, a distant view, and floor cuts at 10%,
50%, and 90%. Look for square seams, missing edge highlights, stretched motifs,
and excess contrast. Preview a custom material through a small scene using the
material-replacement code above; the experiment loads the standard atlas and
has no custom-atlas CLI option.

For generator or UV changes, run `nim check src/polyworld/rockgen.nim`, then
`nim r tests/test_rockgen.nim` and
`nim r experiments/rockgen/tests/tests.nim`. The
[experiment notes](../../polyworld/experiments/rockgen/notes.md) describe its
remaining controls and capture options.
