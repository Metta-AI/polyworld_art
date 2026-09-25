# Previewing and using terrain materials

Run from the `polyworld_art` root after the named assets are available:

```sh
nim r -d:release --out:tmp/gen_blends skills/terrain_tiles/scripts/gen_blends.nim
nim r -d:release --out:tmp/gen_stamp_blends skills/terrain_tiles/scripts/gen_stamp_blends.nim
nim r -d:release --out:tmp/gen_previews skills/terrain_tiles/scripts/gen_previews.nim
nim r -d:release --out:tmp/gen_sample skills/terrain_tiles/scripts/gen_sample.nim
```

| Program | Outputs under `tmp/terrain-samples` |
| --- | --- |
| `gen_blends` | `height-blend`: ordinary/height strips and settings |
| `gen_stamp_blends` | `stamp-blends`: all nine stamps over other materials |
| `gen_previews` | `splat-previews`: light/dark coverage and rotated overlaps |
| `gen_sample` | `path-64-stamp-height`: 1024x1024 bake, height, stages, recipe |

They replace their own generated previews on reruns. `gen_blends [directory]
[strength] [depth]` and `gen_sample [directory] [seed]` accept overrides.
The preview lists use grass-1 through grass-4, dirt-road-1, cobble-road-1,
gravel-road-1, forest-floor-1, and marsh-1. For other sets, update the explicit
lists in `materials.nim`, `gen_blends.nim`, `gen_stamp_blends.nim`, and
`gen_sample.nim`. The processing CLI accepts any material names.

The sample lays out 64x64 cells at 16x16 pixels each, blends ground color and
height using material weights, then adds seeded stamps with varied position,
size, rotation, and amount. It saves the same placements using alpha and height
blending. `recipe.json` records the seed and placements. The 1024x1024 samples
do not replace the 256x256 material assets.

## Height and alpha

Sample color and height with identical UVs. Height is linear red-channel data.
`heightAmount` compares the weighted surfaces and keeps pure paint endpoints
pure. CPU comparison defaults are strength 1.2 and transition depth 0.12.
The user's interactive terrain defaults were strength 1.30 and depth 0.43,
tuned for its shader and coverage, not mandated for every asset.

For stamps, alpha bounds coverage and height decides which details survive.
Use `stampStencil` to attach color alpha to height before filtering or
transforming. Apply identical translation, scale, and rotation to both maps.
`compositeStamp` updates color and accumulated height together so later stamps
see the painted surface. Clamp influence to the original alpha footprint.
Do not multiply stored opaque height by opacity. Do not premultiply tile RGB
by height when packing height into another channel for rendering. Very faint
alpha can quantize recovered values during 8-bit filtering; keep its influence
weighted by alpha.

## Terrain layout lessons

- Place grass variants in coherent noise regions, optionally biased by height
  and slope. Each tile can have one material ID. Random variants per cell
  create distracting noise.
- Shape roads with continuous curves and distance masks. Share the curve for
  ground shaping, material coverage, and tree clearance. Per-cell road IDs
  alone leave checkerboard boundaries.
- Blend coverage with circular falloffs around tile centers. The experiment
  used `max(1 - r*r, 0)^2` with one-tile support. Evaluate per pixel rather
  than relying on mesh triangle interpolation for the shape.
- Merge identical IDs before height competition. Fade height influence near
  zero coverage so rocks cannot win along grid lines where almost absent.
  Avoid square center masks or material priorities that force shared edges.
- Keep material-ID, coverage-weight, height-weight, and painted diagnostic
  views separate. Hide road paint and splats in base-weight diagnostics to
  isolate assignment, coverage, and height artifacts.

## Splat placement and cost

Allow a variable number of splats per tile. A brush overlapping connected tiles
must retain the same position, rotation, and ordering on each. Do not restart
or clip its footprint at tile boundaries. Exclude water and disconnected
surfaces where appropriate to the terrain model.

The chosen interactive defaults were 40% placement probability and 1.00 paint
amount, with one attempt per tile. Probability is not percent surface coverage;
neighboring brushes also overlap. Seed rotation over the full 0 to 360 degree
range and keep it fixed until regeneration. Rotate both maps together. The
experiment uses one world-size control for tiles and splats, all at 256x256.

Splats break repetition and interweave boundaries while retaining the base
layout. Multiple diffuse brushes build coverage naturally. Cost grows with
overlapping brushes on visible pixels, especially with larger footprints.
They can share the terrain draw call but add shader iterations and texture
samples. Lower paint amount alone does not remove those iterations. CPU
placement happens during regeneration; a CPU-baked output renders as one
texture. Benchmark the target renderer and scene rather than carrying timing
numbers between machines or cameras.

Inspect repeated tiles and an actual terrain view. Check road readability,
coherent grass regions, repeated motifs, dark fringes, and circular stamp rims.
Tiling quality requires both pixel boundary checks and visual inspection.
