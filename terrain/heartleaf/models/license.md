# Heartleaf town details

These fifteen original low-poly village props are dedicated under CC0-1.0.
Creator: Softmax / Polyworld contributors, with Codex procedural Blender modeling.
Created: 2026-09-24.

The user supplied a village illustration as a visual reference for the layout,
flower gardens, benches, low fences, lanterns, signpost, blue-and-white market
canopy, laundry line, beehive and circular plaza paving. The illustration is not
bundled or relicensed. Its SHA-256 is recorded in ../source/details-provenance.json.

The meshes are new AI-authored geometry, not extracted or converted Unity assets.
They reuse the reviewed AI-generated CC0 hobbit_trim_v2 color texture embedded in
terrain/blender_village/models/hobbit_house.glb. No additional image texture was
copied from polyworld_data. Canvas and iron use plain material colors.

The source is ../source/village_details.blend, with the shared texture packed,
editable mesh objects, and live bilateral mirrors on the bench and market stall.
The rebuild program is skills/scripts/modeling_buildings/build_heartleaf_details.py
at the repository root, licensed under LICENSE-CODE (MIT). Run it with Blender
in background mode; it writes candidates to tmp/heartleaf-town for review.

village_details.glb is a self-contained export of fifteen named props,
7,356 triangles in total. The source library is spaced out for editing; exports
use local ground pivots. A fresh Blender import verified finite coordinates and
nondegenerate faces. A visual judge reviewed front, rear, top and oblique views
and the assembled in-game town. Verification is recorded in the provenance file.

On 2026-09-25 the same CC0 details were revised with thicker fence members,
curved benches with separate seats, backs and supports, and quieter wood colors.
No third-party or Unity inputs were added.

`cottage.glb` is a CC0 derivative of the reviewed generated hill house in
`terrain/blender_village/models/hobbit_house.glb`. It widens the lower grassy
bank and deepens the enclosed garden without compressing the facade, door or
windows. It retains the original embedded CC0 trim and uses the new generated CC0
meadow turf for its grassy bank. Turf prompts and provenance are in
`../source/turf-provenance.json`. Its editable source is
`../source/cottage.blend`; the rebuild script is
`skills/scripts/modeling_buildings/refine_heartleaf_cottage.py` (MIT).
Input hashes, modifications and fresh-import validation are recorded in
`../source/cottage-provenance.json`.

Golden timber now uses the existing darker brown timber region in the same
reviewed CC0 trim atlas. Door stains, glass, stone and foliage retain their
original regions. Curved bench slat normals preserve outward-facing winding.

The layer comparison revision extracts the front yard into thirty independently
placeable posts, curved rails, and stones in `garden_parts.glb`, with local
placements in `garden-parts.json`. The redundant yard grass disk was removed.
The cottage shell retains its facade join while its rear bank was lowered and
brought forward. The current editable source is `../source/cottage-parts.blend`;
rebuild it with `skills/scripts/modeling_buildings/split_heartleaf_cottage.py`.
All source geometry and embedded trim remain project-generated CC0 artwork.

The cottage and plaza now use the layer-derived grass and cream limestone
materials. Their CC0 inputs, generation prompts and process are recorded in
`../source/layer-tiles-provenance.json`. The detail pack adds a green-roof
birdhouse and refines the freestanding fences, raised curb and paving ring.
