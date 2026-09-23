# Lich clothing

The Lich is a living pale human with ordinary blue eyes, white swept hair,
a solid blue crystal hood, ivory-edged blue robes, a gold diamond belt,
dark trousers, and blue boots. There are no props or skeletal features.

`clothing_reference.png` was generated with the built-in imagegen tool using
the exact saved `clothing_prompt.txt` and approved roster reference.

`../../scripts/gota_lich.py` builds five separate skinned clothing slots.
The boots reuse Clothing_14, and trousers reuse Clothing_09 with reduced
geometry. Both preserve source rig weights. The preset reuses Hair_06,
Eyes_Atlas02, Mouth_Atlas03, Brow_Atlas03, the shared head, nose, and body.

The chest mesh owns the blue robe, ivory edging, ivory wrist cuffs, dark
inner chest, and lower tunic panels. The belt is a distinct selectable part.
The hood has five solid blue crystals and fits around the existing hair.
Every new clothing material is a flat solid color without image textures.

The independent judge requested a closed forehead gap, pale sleeve cuffs,
angular hair, and correction of the rear robe's animation weights. These
were implemented. Rear robe vertices follow the hips with small upper-leg
influence; front panels follow upper legs without boot or shin influence.

Review evidence is in `comparison.png`, `items_comparison.png`, and `renders/`.
The saved independent assessment is `judge.md`. `verification.json` is the
authoritative current assembled runtime triangle count; `export_checks.json`
records binary GLB positions, joint bindings, weights, and texture checks.

Rebuild with Blender's background Python runner using `gota_common.py -- lich`,
then run the shared `render_gota` binary against the Lich's private library
and `review_gota.py lich` to refresh comparisons. This builder does not edit
the master source blend, shared manifests, or palettes.
