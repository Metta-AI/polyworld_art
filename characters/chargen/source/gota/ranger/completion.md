# Ranger character

Built by `source/scripts/gota_ranger.py` through the shared isolated exporter.
The final independent visual review is a pass in `judge.md`.

The five independently selectable clothing parts are Ranger cuff boots,
Ranger trousers, Ranger buckle belt, Ranger tunic and cape, and Ranger
pointed hood. Ranger copper twin braids is a sixth selectable derived hair
part. All runtime files use the `gota_ranger_` prefix.

The build reuses the fitted Clothing_16 boots, Clothing_09 trousers and
boot-cut sections, Gnome_Belt, and Hair_09 twin braids. Boots and hair have
reduced topology. Braids move forward to remain visible across the arms.
Existing focused eyes, neutral mouth, tiny nose, round ears, heroic brows,
base head remain in the runtime preset. The shared Gota split body hides
lower skin beneath trousers while retaining exposed arms and hands.

The current actual visible assembly has 17,324 triangles, including 11,844
triangles in 14 visible custom mesh nodes. All six custom GLBs have zero
image textures. The exporter checks finite positions and normalized skin
weights. The shared rig animates the parts in the actual runtime.

`clothing_reference.png` is the corrected generated five-pair front/back
reference. Its exact built-in imagegen prompt is `reference_prompt_v2.txt`.
The original reference and prompt remain as `clothing_reference_v1.png`
and `reference_prompt.txt`.

`comparison.png` compares the approved roster, generated reference, and
actual runtime model side by side. `items_comparison.png` compares the
isolated rendered clothing items. `renders/model.png`, `renders/walk.png`,
and `renders/crouch.png` verify the assembled model and tested poses.
`hero.blend` stores the private authoring result; `parts.json`,
`preset.json`, and `verification.json` record the exported integration data.

The review caught and resolved knee skin exposure, rear belt penetration,
and cape deformation with a leg. The trousers now retain original fitted
topology, and the cape uses explicit torso weights with a waist row and
rear clearance. There are no remaining Ranger-specific visual defects in
the tested poses. The shared body split and final outfit visibility pass
are applied to the saved authoring file and refreshed runtime reviews.
