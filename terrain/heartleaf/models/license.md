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
6,896 triangles in total. The source library is spaced out for editing; exports
use local ground pivots. A fresh Blender import verified finite coordinates and
nondegenerate faces. A visual judge reviewed front, rear, top and oblique views
and the assembled in-game town. Verification is recorded in the provenance file.
