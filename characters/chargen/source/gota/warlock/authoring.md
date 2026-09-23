# Warlock authoring

The Warlock uses five independently selectable skinned modules: Foot, Leg,
Belt, Chest, and Headgear. All new clothing uses solid material colors with
flat polygon shading and no image textures. Facial decals are reused.

The imagegen built-in tool produced `clothing_reference_final.png` through
three documented prompts. The final reference removes the belt from the
body row while retaining crossed straps. The approved roster remains the
authority for identity, palette, and silhouette.

`source/scripts/gota_warlock.py` implements `build(ctx)`. Run it through
`source/scripts/gota_common.py -- warlock` in Blender. It does not alter the
shared master authoring file or manifest.

Reused fitted geometry includes Clothing_13 ankle boots, Clothing_12 trousers,
Gnome_Belt leather band, Clothing_07 outer torso fabric, Body waist fabric,
and both original Hand meshes as gloves. The preset reuses the base human
face, Tiny nose, 02 Focused eyes, 03 Neutral mouth and 04 Heroic brows.
It specifies pale gray skin, natural Red irises, Soft black brows, and hides
ears/hair beneath the hood. There are no props or weapons.

The robe sleeves are weighted by arm span. Divided coat tails blend from
Hips to the corresponding upper leg, while the central tabard follows Hips.
The gold collar follows Spine2. Hood and horns follow Head. Existing boots,
trousers, gloves and fitted torso retain the original normalized rig weights.

The exported model has 16,430 visible triangles including the shared face
and body. `verification.json` records the exact per-node counts and five
slots. The export asserts finite positions, normalized weights and absence
of clothing image textures. `renders/model.png`, `walk.png` and `crouch.png`
are rendered from the actual modular GLBs in the Polyworld runtime.

`comparison.png` compares the approved hero, generated clothing and actual
front/back model. `items_comparison.png` compares the generated sheet and
five actual isolated modules. `judge.md` contains the independent review.
