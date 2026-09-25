# Heartleaf mockup layers

Creator: Softmax / Polyworld contributors, with Codex and built-in imagegen.
Created: 2026-09-25.

These project-generated reconstructions use the repository's CC0-1.0
dedication in ../../../LICENSE. The user supplied the project's Heartleaf
mockup as the edit target. The supplied bitmap is not bundled or relicensed.
Its digest and supplied location are recorded in layers.json.

Imagegen reconstructed four visual layers from that single flattened mockup.
The ground and vegetation PNGs are unmodified tool outputs. The building
cutouts were individually translated to match the original door landmarks.
The props alpha was masked where the central tree hides the rear plaza curb
and fence. ImageMagick performed these registration and compositing operations
after the built-in imagegen quota prevented a further generative revision.
The alignment measurements are retained in registration.json.
Hidden surfaces are inferred, and contours can differ from the input.
These are art reference
layers, not an exact original layered source file or recovered 3D assets.

The opaque ground includes grass, dirt paths, plaza paving and approach stones.
The building layer includes nine houses with their grassy roofs. Freestanding
trees, bushes, hedges and flower clusters belong to the vegetation layer.
The props layer contains fences, posts, lanterns, signs, benches, stone curb,
well, stall, hive, birdhouses, laundry, loose rocks and contained garden plants.

All four canvases are 1122 by 1402. The final three PNGs contain real alpha.
Verbatim prompts, including the props cleanup pass, are saved in prompts/.
The optional preview.html provides layer visibility, solo and opacity controls.
Stack in this order from bottom to top: ground, buildings, vegetation, props.
stacked-preview.png shows that exact alpha composite.
