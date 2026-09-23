# Arcanist authoring

The approved roster's top-row third character is the visual authority.
`clothing_reference.png` was generated with the built-in imagegen tool using
`prompt.txt`. It is a front and back reference with boots, legs, belt, body,
and hat rows.

The independent judge identified three generated-sheet deviations. The model
keeps low boots with bright instep caps, uses a thin circlet mostly hidden by
the hair, and keeps the brown belt separate from the robe. The purple diamonds
are attached ornaments. There are no loose crystals, weapons, or props.

The builder is `source/scripts/gota_arcanist.py`. It reuses the fitted
`Clothing_13` boot and `Clothing_09` trouser meshes, with reduced face counts
and solid purple colors. Hair is the existing `12 Wolf cut` in White, with
existing focused eyes, heroic brows, neutral mouth, and round ears.

The new robe uses copied fitted torso geometry and original body weights.
Its broad bell sleeves and split flared skirt are explicit low-poly surfaces.
The separate leather belt carries an amethyst buckle. A thin headband carries
the matching forehead gem. New clothing has no texture images.

The final assembly has 18,054 visible triangles. `verification.json` counts
all selected runtime parts, including the shared body, face, hair and hands.
The shared Gota body hides its covered lower section under the leggings.
`export_audit.json` verifies finite coordinates, normalized skin weights,
joint indices, identical shared inverse bind matrices, and no textures in
all five actual exported GLBs. `animation_audit.json` checks all nine new
mesh nodes across four frames of the existing Walk_Loop animation.

The judge found and the builder fixed overlapping shoulder seams, one inset
collar plate, and animated robe trim clipping. The final skirt trim uses
material regions on the same geometry, and skirt weights follow the hips
and thighs without binding the hem to knees. The rear skirt split follows
the generated clothing sheet.

`review.html` contains the approved roster, generated reference and actual
runtime model side by side, the separate-item comparison, and walking and
crouching views. `judgment.md` records the independent visual verdict.
