# Terrain tool reference

Read the [workflow](../../terrain_tiles.md) for generation order and the asset
contract. These are the original Nim/Pixie terrain programs adapted for
`polyworld_art`. `splat-mask` and paired `export` package the logic previously
kept in the one-off diffuse splat exporter.

```sh
mkdir -p tmp
nim c -d:release --out:tmp/terrain skills/terrain_tiles/scripts/terrain.nim
tmp/terrain --help
```

Run from the art repository root. Image arguments are PNG paths. Outputs are
refused if they exist unless `--force` is supplied; parent directories are
created automatically. Grids must divide dimensions exactly. Images have a
64M-pixel limit. Errors use `TerrainError`.

Only `export`, `cut`, `resize`, and `stamp-height` resize, to 256x256 per cell
by default. `--size N` permits powers of two from 4 through 8192 for those
commands and sets the target for `check`. Processing commands reject `--size`.

## Paired export

```text
export tiles|stamps color height namesFile directory [columns rows]
```

Default grid: 3x3. Provide one unique base name per cell, in row-major order,
in a text file. Blank lines are ignored. Names use lowercase letters, digits,
and hyphens without extensions, for example `dirt-road-1`.

Inputs must have identical source dimensions. Export cuts and filters cells
independently, checks all final pairs and destination paths before writing any,
and verifies exact PNG round trips. It writes `.rgb.png` and `.height.png`.

- Tiles require prepared opaque grayscale height. Final color and height must
  be opaque with exactly matching opposite edges. Repair masters first.
- Stamps filter height through the original color alpha. Generated opaque
  height becomes grayscale without contrast normalization. Final height is
  opaque and zero outside coverage. Empty stamps and nontransparent borders
  are rejected.

Use a staging directory first. Export validates pixel structure, not semantic
alignment or artistic quality, and does not update the asset provenance manifest.

## Cut, crop, resize

```text
cut input directory [columns rows [prefix]]
crop input output x y width height
resize input output [columns rows]
```

`cut` defaults to 3x3 and historical names `grass-1..3`, `rocks-1..3`,
`path-1..3`. Other grids use `tile-N`, or the supplied prefix. Prefer paired
export for explicit material names. `--channel height` changes the filename
suffix only; it does not generate or convert height.

`crop` copies source pixels exactly without resizing. `resize` defaults to one
texture; a 3x3 grid produces a 768x768 final sheet. Cells never filter across
atlas boundaries. Matching opaque tile edges are restored after resampling.
Transparent stamps retain alpha. Already 256x256 cells are copied exactly.

## Backgrounds and diffuse masks

```text
background input output [black|gray|white|RRGGBB [threshold]]
splat-mask color opacityMask output [columns rows]
```

`background` defaults to black and maximum-channel tolerance 10. Gray means
RGB 128,128,128. Thresholds range from 0 to 254. Quote a leading `#` in hex
colors. It estimates foreground edge colors from nearby solid pixels to recover
antialiasing, including holes. Existing partial and transparent alpha remain
unchanged. It cannot remove complex backgrounds or baked checkerboards; a matte
matching actual artwork may erase it.

`splat-mask` defaults to 3x3. Both sheets must be opaque and same-sized, with
cells larger than 64 pixels. It preserves RGB, applies smoothstep coverage from
the grayscale mask, and adds an 8-pixel empty border with a 24-pixel feather.
These are the original source-resolution recipe settings, not final pixels.

## Wrapped seam repair

```text
offset input output [columns rows]
mask input guideOutput apiOutput [columns rows]
blend source repaired guideMask output
tile input output [columns rows [band]]
```

Grids default to 1x1 here; explicitly pass `3 3` for an atlas. `offset` wraps
each cell by half its width and height, requiring even dimensions. Applying it
twice restores the original pixels.

`mask` covers the center cross and its endpoints: white is editable, black is
protected, and gray feathers. The API mask instead uses transparent alpha for
editable areas. Neither command generates terrain artwork. Supply the offset
and guide to imagegen for semantic repair.

`blend` requires same-sized source, repair, and opaque guide, and preserves
pixels outside the guide exactly. `tile` corrects an edge band and equates
opposite boundary pixels per cell. Its band defaults to 24 source pixels,
capped at half the shorter cell dimension. Cells must be opaque and at least
4x4. This correction can affect pixels outside the inpainting guide and smear
detail if the original join is too broken.

## Heights

```text
height input output [columns rows [band]]
stamp-height generated stampColor output [columns rows]
```

Grid defaults: 1x1. `height` makes an already generated opaque relief image
grayscale and repairs periodic edges at source resolution; default band is 8.
It does not infer height from RGB.

`stamp-height` is a final export, filtering each cell through original color
alpha and writing opaque grayscale with zero outside the footprint. It does
not offset, wrap, normalize contrast, or repair edges. A 3x3 export is 768x768.
Paired `export stamps` performs this directly from both high-resolution masters.

## Inspection

```text
inspect input [columns rows]
check input [columns rows]
repeat input output [columns rows]
```

`inspect` and `check` default to one texture and report alpha and mismatched-edge
counts. `check` requires the target size, full opacity, and exact edge equality.
Use it for tiles; transparent stamps are expected to fail. Paired export
validates the different stamp contract. `repeat` defaults to 3x3 repetitions of
the entire input; supply a single cell, not an atlas, to inspect one tile.

## Alignment and previews

```sh
nim c -d:release --out:tmp/align_stamps skills/terrain_tiles/scripts/align_stamps.nim
tmp/align_stamps input.png output.png
```

The original alignment helper now takes explicit paths. It detects alpha bands
separated by gaps wider than 12 pixels and requires exactly three rows and three
subjects per row. It centers complete bounds without resampling, adds padding,
uses even square cells, and writes `output.bounds.json`. Both outputs reject
collisions; append `--force` to replace them. Run before generating height.
This is unsuitable for overlapping or widely scattered fragments.

See [blending and preview commands](blending.md) for all four sample programs.
They read this repository's assets and Rubik font and write under
`tmp/terrain-samples`, replacing their own generated previews on reruns.

## Source modules

| Files | Purpose |
| --- | --- |
| `common.nim`, `cuts.nim` | Straight RGBA PNG I/O and exact crop/split/assembly |
| `backgrounds.nim`, `masks.nim` | Matte recovery and diffuse opacity |
| `tiles.nim`, `textures.nim` | Offsets, seam masks, periodic repair, final filtering |
| `heights.nim`, `stamps.nim` | Height preparation and accumulated stamp blending |
| `pairs.nim`, `terrain.nim` | Named paired exports, validation, CLI |
| `align_stamps.nim` | Source-resolution recentering of nine isolated subjects |
| `materials.nim`, `gen_*.nim` | Material lists and comparisons/sample bakes |

Core scripts came from `polyworld/tools/terrain`; tests came from
`polyworld/tests/test_terrains.nim`. Alignment came from the earth generation
archive; diffuse masks and overlap previews came from the later splat archive.
Old archive paths and `soft-` names are not runtime dependencies. Code is
covered by the repository's `LICENSE-CODE`.
