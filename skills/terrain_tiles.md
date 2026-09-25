---
name: terrain-tiles
description: Generate and prepare Polyworld terrain tiles, RGBA splats, and aligned height maps using shared style references, seam inpainting, and the bundled Nim/Pixie tools.
---

# Terrain tiles and splats

Use this workflow for painted terrain materials and their variations. Generate
related materials together in a 3x3 sheet to help preserve their palette, scale,
and style. Tiles and splats need different compositions, so use separate sheets
with the same reference, or derive splats from the finished tiles using opacity
masks. A single generation helps consistency; inspect it rather than assuming
every cell matches or repeats correctly.

This file is the project skill entry point. Its programs are in
[`terrain_tiles/scripts`](terrain_tiles/scripts), copied from the terrain tools
and generation helpers developed in `polyworld`. They run from this art
repository without importing the game repository. Local processing uses Nim and
Pixie in release mode. Python is not required. Image generation and semantic
inpainting still need the imagegen skill/tool; the local programs prepare masks,
combine its returned images, and export assets.

## Asset contract

| Final file | Dimensions | Meaning |
| --- | --- | --- |
| `terrain/tiles/dirt-1.rgb.png` | 256x256 | Opaque repeating color |
| `terrain/tiles/dirt-1.height.png` | 256x256 | Opaque repeating grayscale relief |
| `terrain/stamps/dirt-1.rgb.png` | 256x256 | Color with RGBA coverage |
| `terrain/stamps/dirt-1.height.png` | 256x256 | Opaque grayscale relief, zero outside coverage |

Use identical material base names for each pair, with `.rgb.png` and
`.height.png` suffixes. `.rgb.png` stamps still have alpha. Do not add the old
`soft-` prefix. White height is higher and black is lower; height is linear data,
not color brightness, camera depth, a normal map, or opacity.

Keep generation, cropping, background removal, inpainting, and seam correction
at source resolution. Resize only on final export to 256x256. Our earlier
1254x1254 sheets have nine 418x418 cells; this is an example, not a required
generator output size. The actual sheet must divide exactly into its grid, and
cell dimensions must be even for a half offset. Working sheets and previews
need not be powers of two. Individual game textures do.

Save temporary work and sample renders under the ignored `tmp/` directory.
Preserve approved high-resolution masters, generation prompts, references, and
source records separately before cleaning temporary work. Publish only finished
asset pairs into `terrain/tiles` and `terrain/stamps`. For new or changed art,
follow the repository's [contribution and provenance process](../CONTRIBUTING.md).

## Setup

Run these commands from the `polyworld_art` repository root. Nim 2.2.10 was used
for the original tools. Pixie supplies PNG handling, filtering, and compositing;
`jsony` is also used by alignment and sample programs. The `/Users/me/p/nim.cfg`
workspace already resolves these libraries. On a separate checkout, install
them with `nimble install pixie jsony`.

```sh
terrainScripts=skills/terrain_tiles/scripts
terrainWork=tmp/terrain-work/dirt-sand-marsh
mkdir -p "$terrainWork"
nim check "$terrainScripts/terrain.nim"
nim c -d:release --out:tmp/terrain "$terrainScripts/terrain.nim"
tmp/terrain --help
```

Processing commands refuse existing outputs unless given `--force`. Choose a
fresh working directory per attempt. The preview generators replace their own
generated previews when rerun. See the [CLI reference](terrain_tiles/references/cli.md)
for exact arguments and overwrite behavior.

## 1. Generate a coherent set

Use a user-supplied or approved reference image and the
[prompt templates](terrain_tiles/references/prompts.md). Keep material order
explicit. A useful example is three dirt variations, three sand variations,
and three marsh variations, one material family per row.

Tiles must cover every cell edge to edge, with an even ground view and restrained
lighting. Avoid circular patches, empty gutters, labels, vignettes, baked cast
shadows, and strong focal features. Save `tiles-generated.rgb.png` in the working
directory. Inspect actual dimensions and framing:

```sh
tmp/terrain inspect "$terrainWork/tiles-generated.rgb.png" 3 3
```

Fix the high-resolution layout if the grid does not divide evenly or the
generator added gutters. Crop only after identifying the intended bounds;
do not discard artwork blindly. Never upscale a final 256x256 asset and treat
it as a high-resolution master.

## 2. Repair the tile seams

Offset each cell by half its own width and height with wrapping. This brings
the original joins into a center cross in all nine cells:

```sh
tmp/terrain offset "$terrainWork/tiles-generated.rgb.png" \
  "$terrainWork/tiles-offset.rgb.png" 3 3
tmp/terrain mask "$terrainWork/tiles-offset.rgb.png" \
  "$terrainWork/tiles-guide.png" "$terrainWork/tiles-api-mask.png" 3 3
```

Inpaint the nine center crosses together using the offset atlas and guide.
White permits changes, black preserves source pixels, and gray feathers the
repair. The API mask instead uses transparent alpha for editable pixels; use
it only with a tool that accepts a mask parameter. A guide image alone does not
guarantee unchanged pixels. Ask for exact input dimensions, layout, palette,
feature scale, and unchanged corner content. Save `tiles-repaired.rgb.png`.

```sh
tmp/terrain blend "$terrainWork/tiles-offset.rgb.png" \
  "$terrainWork/tiles-repaired.rgb.png" "$terrainWork/tiles-guide.png" \
  "$terrainWork/tiles-blended.rgb.png"
tmp/terrain tile "$terrainWork/tiles-blended.rgb.png" \
  "$terrainWork/tiles-master.rgb.png" 3 3 24
```

`blend` restores all pixels outside the guide exactly. Its three inputs must
have identical dimensions. `tile` then corrects a narrow edge band and makes
opposite boundary pixels equal, including outside the guide if necessary.
It cannot invent convincing continuation of a badly broken stone or leaf;
that is why semantic inpainting comes first.

Keep this repaired, offset orientation as the finished master. No reverse
offset is needed. Each tile repeats with itself; two different variants do not
automatically share compatible edges. Blend them during terrain rendering.

## 3. Generate aligned tile heights

Give the finished color master to imagegen and use the height prompt in the
[templates](terrain_tiles/references/prompts.md). Preserve the exact location,
size, and orientation of stones, leaves, cracks, and water. Use consistent
height ranges across materials. Do not independently stretch each cell's
contrast or encode lighting as height. Save `tiles-generated.height.png`.

```sh
tmp/terrain height "$terrainWork/tiles-generated.height.png" \
  "$terrainWork/tiles-master.height.png" 3 3 8
```

This command makes the generated map opaque grayscale and repairs its seams at
source resolution. It does not infer relief from RGB. Compare height against
color and regenerate significant feature misalignments. If color changes after
height generation, update the corresponding height. Never offset, rotate, or
crop only one member of a finished pair.

## 4. Make splats

Choose the route that fits the artwork. Both produce roughly circular but
irregular patches with transparent margins, separate alpha and height, and
matching material scale. Avoid uniform circular rims and fully opaque discs.

### Diffuse splats from the tiles

This is the approach used for the final grass, road, forest-floor, and marsh
splats. Generate a separate opacity atlas at exactly the finished tile master's
dimensions using the [saved mask prompt](terrain_tiles/references/splat-mask-prompt.txt).
White means covered, gray means partial coverage, and black means empty. Request
different lobes, gaps, broken brush tips, and broad fading margins in each cell.
This is an opacity map, not a relief map. Save `stamps-opacity.png`.

```sh
tmp/terrain splat-mask "$terrainWork/tiles-master.rgb.png" \
  "$terrainWork/stamps-opacity.png" "$terrainWork/stamps-master.rgb.png" 3 3
cp "$terrainWork/tiles-master.height.png" "$terrainWork/stamps-master.height.png"
```

The helper preserves the source RGB exactly and computes alpha as
`smoothstep((gray - 4) / 200)`, multiplied by a cell-border guard. The guard
stays zero through 8 source pixels and reaches full strength after another 24.
Those are the original 418-cell recipe settings; inspect their visual width on
different source sizes. This avoids black matte contamination. The copied height
stays at source resolution; final export filters it through the stamp alpha and
zeros empty pixels. Do not darken height by multiplying it by opacity.

### Separate generated stamps

Generate an isolated 3x3 stamp sheet on uniform pure black, with ample margins,
using the stamp prompt. Remove the matte before resizing:

```sh
tmp/terrain background "$terrainWork/stamps-generated.rgb.png" \
  "$terrainWork/stamps-master.rgb.png" black 10
tmp/terrain inspect "$terrainWork/stamps-master.rgb.png" 3 3
```

Gray, white, or an RGB hex matte also work if absent from the artwork. Gray can
remove real rocks and black can remove genuine dark details. This tool handles
flat mattes, not arbitrary backgrounds or checkerboards. Keep existing correct
alpha. Inspect over light and dark backgrounds for holes and halos.

If nine isolated subjects are miscentered, run the bundled original alignment
helper before generating height:

```sh
nim c -d:release --out:tmp/align_stamps "$terrainScripts/align_stamps.nim"
tmp/align_stamps "$terrainWork/stamps-master.rgb.png" \
  "$terrainWork/stamps-aligned.rgb.png"
```

Use the aligned output as the new master. It preserves source pixels, may enlarge
cells, and writes a `.bounds.json` source record. It expects three separated rows
and three separated subjects per row, detecting gaps wider than 12 pixels. It is
not a general segmentation algorithm for scattered or overlapping splats.

Generate height from the aligned RGBA master, requesting opaque black outside
its footprint and feature relief rather than a circular dome. Save it as
`stamps-master.height.png`. Do not half-offset or seam-repair stamps. Their
original color alpha controls both channels' coverage.

## 5. Export and verify named pairs

Write one base name per cell in row-major order. This avoids the low-level
`cut` command's historical default grass/rocks/path names:

```sh
cat > "$terrainWork/names.txt" <<'NAMES'
dirt-1
dirt-2
dirt-3
sand-1
sand-2
sand-3
marsh-1
marsh-2
marsh-3
NAMES
tmp/terrain export tiles "$terrainWork/tiles-master.rgb.png" \
  "$terrainWork/tiles-master.height.png" "$terrainWork/names.txt" \
  "$terrainWork/tiles"
tmp/terrain export stamps "$terrainWork/stamps-master.rgb.png" \
  "$terrainWork/stamps-master.height.png" "$terrainWork/names.txt" \
  "$terrainWork/stamps"
tmp/terrain repeat "$terrainWork/tiles/dirt-1.rgb.png" \
  "$terrainWork/dirt-1-repeat.png" 3 3
```

Substitute aligned stamp paths when alignment was needed. `export` cuts each
cell independently and performs the final 256x256 resize once. It checks all
pairs and destinations before writing, verifies PNG round trips, requires
opaque edge-matched tiles and grayscale heights, and rejects empty or clipped
stamps. Stamp height is filtered using the same source alpha as color, then
stored opaque with zero outside the footprint. No per-cell height normalization
is performed. `--size` accepts other powers of two, but use 256 for this set.

Inspect repeated color and height tiles for seams, obvious repeated motifs,
scale mismatch, or edge smearing. Exact boundary equality alone is insufficient.
Inspect rotated overlapping stamps on light and dark grounds for hard rims,
lost detail, and halos. Test height blending against ordinary alpha blending.
The [preview commands and runtime lessons](terrain_tiles/references/blending.md)
cover those checks and the sample terrain bake.

Copy only approved pairs into the art folders. Resolve existing-name collisions
deliberately; `cp -i` prompts before replacing existing files:

```sh
mkdir -p terrain/tiles terrain/stamps
cp -i "$terrainWork"/tiles/*.rgb.png "$terrainWork"/tiles/*.height.png terrain/tiles/
cp -i "$terrainWork"/stamps/*.rgb.png "$terrainWork"/stamps/*.height.png terrain/stamps/
```

Update source records and the asset manifest as described in `CONTRIBUTING.md`
when publishing artwork. Keep tests, masks, row crops, and sample renders out
of the asset folders.

## Tool validation

```sh
nim check skills/terrain_tiles/tests/test_terrains.nim
nim r -d:release --out:tmp/test_terrains skills/terrain_tiles/tests/test_terrains.nim
```

Tests cover exact cuts and RGBA round trips, black/gray/white matte recovery,
wrapped offsets, seam-mask protection, periodic edges, power-of-two export,
alpha-aware filtering, stamp height, and accumulated height blending. The
suite also checks diffuse mask color preservation, named paired export, and
overwrite preflight. The CLI and helpers use `TerrainError` for input failures.
