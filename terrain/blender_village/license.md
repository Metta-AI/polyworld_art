# Heartleaf village assets

These five runtime models and their embedded color textures are project-generated
AI assets dedicated by Softmax under CC0-1.0 in the repository root LICENSE.
They were copied byte for byte from the current polyworld_data working tree on
2026-09-24. No historical objects, Unity assets, reference images, Blender scenes,
or unrelated props were copied.

- models/hobbit_house.glb: generated hill house and yard, with hobbit_trim_v2 and
  hobbit_grass_tile_v1 textures embedded.
- models/hobbit_chimney.glb: generated hollow stone chimney, with village_trim
  embedded. Added for the reference town's three roof chimneys.
- models/well.glb: generated village well, with village_trim embedded.
- models/hobbit_barrel_planter.glb and models/hobbit_box_planter.glb: generated
  planters, with hobbit_trim_v2 embedded.

The source repository LICENSE records the owner's 2026-09-21 confirmation that
project-generated models and textures are AI-generated CC0 assets. The geometry
was authored by the source tools/build_well.py, tools/build_hobbit.py and
tools/build_hobbit_house.py scripts. The source guides, manifests and texture
prompt records document the imagegen textures and procedural mesh construction.
The exported GLBs contain only mesh geometry, materials and embedded PNGs, with
no external dependencies, reference planes, studio meshes, rigs or animations.

The source paths are terrain/blender_village/ in Metta-AI/polyworld-data.
Source snapshot hashes are retained in licenses/assets.json. The existing
full-house and well manifests and guides were inspected during the migration.
