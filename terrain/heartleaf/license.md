# Heartleaf terrain materials

These new project-generated terrain textures are dedicated under CC0-1.0,
consistent with the repository's original-art dedication in ../../LICENSE.

Creator: Softmax / Polyworld contributors, with Codex and built-in imagegen.
Created: 2026-09-24.

The user supplied a Heartleaf village illustration as a visual reference for
fresh green turf, golden packed-earth paths and warm pale stone paving.
The textures are newly generated material reconstructions, not recovered
engine textures or literal crops of the illustration. No characters, dialogue,
buildings or other reference props are included. The reference bitmap is not
bundled or relicensed. Its digest and supplied location are recorded in
source/provenance.json.

The generation followed skills/terrain_tiles.md. A coherent 3x3 color atlas
was half-offset per cell, repaired through an imagegen seam guide, composited
through the exact guide and corrected at opposite boundaries. A separate
imagegen height atlas was aligned to the finished color master, converted to
opaque grayscale and given periodic boundaries. Nim/Pixie exported each pair
once from 418x418 source cells to 256x256 runtime files.

Runtime pairs are terrain/tiles/heartleaf-grass-1 through -3,
heartleaf-path-1 through -3 and heartleaf-paving-1 through -3.
Each base has .rgb.png and .height.png files. Color is opaque. Height is
linear grayscale data with white higher and black lower. The heights are
artist-inferred relief for material blending, not measurements from a 3D mesh.
Each variant repeats with itself. Blend between different variants rather
than assuming their edges match one another.

High-resolution masters and verbatim generation prompts are kept in source/.
Temporary masks, intermediate renders and repeat previews are under
tmp/terrain-work/heartleaf-20260924/.

## Matching splats

Nine matching RGBA splat pairs were added on 2026-09-24 in terrain/stamps,
using the same material base names as the tiles. Imagegen created separate
irregular grayscale coverage masks. A second pass removed internal stone
patterns from the paving masks while preserving the first six masks exactly.
The masks change coverage only. All source RGB channels and source relief
remain those of the approved tile masters.

Nim/Pixie applied the coverage masks at 1254x1254, guarded the cell borders,
and exported 256x256 paired stamps with alpha-aware filtering. Each color
stamp has transparent margins and partial coverage. The corresponding height
is opaque grayscale, zero outside coverage, and is not darkened by alpha.
These new assets share the CC0-1.0 dedication above.

See splats-usage.md and source/splats-provenance.json for usage and validation.
Masks, source masters and verbatim imagegen prompts are retained in source/.
Splat working files and previews are under
tmp/terrain-work/heartleaf-splats-20260924/.
