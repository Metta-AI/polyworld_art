# Arcanist delivery

The character has five independently selectable, skinned clothing modules.
The complete runtime assembly is 18,054 visible triangles, below 20,000.

| Slot | Export |
| --- | --- |
| Foot | `clothing/boots/gota_arcanist_foot.glb` |
| Leg | `clothing/pants/gota_arcanist_leg.glb` |
| Belt | `clothing/belts/gota_arcanist_belt.glb` |
| Chest | `clothing/torsos/gota_arcanist_chest.glb` |
| Headgear | `hats/gota_arcanist_headgear.glb` |

Each GLB has a matching JSON sidecar in the same category folder. `parts.json`
and `preset.json` contain integration metadata. `hero.blend` is the editable
local source, and `source/scripts/gota_arcanist.py` is the repeatable builder.

Reused parts include Clothing_13 boot and Clothing_09 trouser geometry,
the white Wolf cut hairstyle, focused eyes, heroic brows, neutral mouth,
round ears, tiny nose, base head, shared Gota body and hands, and original
humanoid rig. Clothing uses flat facets and solid materials without textures.

The built-in imagegen output is `clothing_reference.png`; its exact prompt is
`prompt.txt`. `comparison.png`, `items_comparison.png`, `modeled_items.png`,
and `review.html` compare the actual runtime models against both references.
The `renders` folder contains front and back assembly, five separate item
views, walking and crouching views. `items_front_back.png` is an additional
Blender render of the separate items.

Checks and independent review are recorded in `verification.json`,
`export_audit.json`, `animation_audit.json`, and `judgment.md`. Build and
render logs live in `polyworld/tmp/chargen/gota/arcanist`.

The master blend and shared manifests were not changed by this character
builder. Root integration applies the preset and shared body support.
