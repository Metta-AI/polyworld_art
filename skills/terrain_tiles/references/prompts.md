# Generation and repair prompts

Adapt material order, actual dimensions, and references per request. The
1254x1254 sheet and 418x418 cells describe earlier work, not guaranteed imagegen
output sizes. Inspect returned images before grid operations. Export to 256 last.

## Full-coverage tile sheet

```text
Create a 1254x1254 terrain texture atlas matching the attached style reference.
Exactly 3 equal columns and 3 equal rows, with 418x418 cells.
Row 1: three dirt variations, packed soil, cracked clay, and rooty earth.
Row 2: three sand variations, fine sand, rippled sand, and pebbly sand.
Row 3: three marsh variations, muddy moss, shallow pools, and wet grasses.
Every cell is a fully covered square ground texture intended to repeat in
both directions. Spread detail across the whole cell, including its edges.
Keep the reference's painted fantasy style, restrained shading, palette,
material scale, and ground view. No isolated circular patches, strong focal
features, directional cast shadows, vignettes, borders, labels, grid lines,
empty gutters, or transparency.
```

## Center-cross inpainting after half offset

Provide the offset color atlas and grayscale guide. A dedicated API mask has
transparent alpha for editing, when supported by the tool. Always use local
`blend` afterward to enforce protected pixels.

```text
Repair the center cross inside each of the nine tiles in the offset atlas.
Use the guide: repair white regions, preserve black regions, and blend through
gray regions. Continue stones, cracks, grasses, and soil naturally across
the seams. Keep the exact input dimensions, cell boundaries, material order,
palette, scale, and lighting. Preserve corner content. Do not introduce
recognizable motifs, new objects, borders, gutters, labels, or vignettes.
Return the repaired color atlas only, without the guide drawn into it.
```

If an edit returns different dimensions, correct or regenerate it before masked
composition. Do not silently stretch it and shift feature alignment.

## Height from a finished master

Use the finished repaired color atlas as target. An approved height sheet may
provide a value-range reference but must not replace the target's shapes.

```text
Convert this exact color atlas into an aligned grayscale surface height map.
Preserve every feature's location, shape, scale, orientation, and cell layout.
Keep the exact image dimensions. Infer relief above the ground plane, ignoring
color and lighting. White means higher, black means lower. Stone tops and
leaf tips are higher. Cracks, gaps, and recessed soil are lower. Water is flat
and low. Sand has shallow relief. Use consistent height ranges across all
materials, without contrast-stretching each cell independently. Do not encode
cast shadows or directional highlights. Do not add, move, rotate, or redesign
features. No labels, borders, grid lines, camera depth, or normal-map colors.
```

For stamps, add:

```text
Keep the original stamp footprint and all feature positions. Use an opaque
black background outside the footprint. Describe local surface relief, not a
circular mound or radial height gradient across the entire stamp.
```

Heights are inferred blend masks. Compare stone boundaries, leaves, cracks,
and pool outlines against color; regenerate significant misalignment.

## Separate isolated stamp sheet

```text
Create a 1254x1254 terrain stamp atlas in the painted fantasy style of the
reference. Exactly 3 equal columns and 3 equal rows, with 418x418 cells.
Row 1: three dirt variations, packed soil, cracked clay, and rooty earth.
Row 2: three sand variations, fine sand, rippled sand, and pebbly sand.
Row 3: three marsh variations, muddy moss, shallow pools, and wet grasses.
Each stamp is roughly circular with an irregular natural boundary, centered
inside its cell. Leave clear empty margins around the entire footprint.
No subject touches another stamp or crosses a cell boundary. Use a perfectly
uniform pure black background. Match the reference palette, texture scale,
ground view, and restrained shading. Use natural broken edges, not a solid
disc or uniform ring. No labels, frames, checkerboard, grid lines, or cast
shadows outside the stamps.
```

Remove the matte locally at source resolution. Use another flat matte if black
would erase artwork, or preserve correct generated transparency when available.

## Diffuse splats derived from tiles

Use the [saved opacity-mask prompt](splat-mask-prompt.txt) with the finished
color atlas. Update its material order and dimensions to match. The example is:

| Row | Left | Middle | Right |
| --- | --- | --- | --- |
| 1 | Dirt road | Cobblestone road | Gravel road |
| 2 | Forest floor | Marsh | Green grass |
| 3 | Olive grass | Mossy grass | Sparse grass |

Base names are `dirt-road-1`, `cobble-road-1`, `gravel-road-1`, `forest-floor-1`,
`marsh-1`, `grass-1`, `grass-2`, `grass-3`, `grass-4`. This differs from the
historical grass/rocks/path cutter defaults.

Opacity and height are separate. Request broad lobes, gaps, fragments, and fading
brush strokes, not a grayscale terrain rendering. Reuse the tile color and
height under this footprint. Several placements build coverage without a rim.
