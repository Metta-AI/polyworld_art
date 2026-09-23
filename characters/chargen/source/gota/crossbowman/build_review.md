# Crossbowman authoring review

This hero follows the approved roster bottom row, second character. The imagegen
clothing reference uses a brown hood, crossed brown leather over brick red,
charcoal trousers and cuffed brown boots. It has no weapons, shields, quivers,
goggles or mechanical details. The sheet's repeated belt inside Body is a
reference-layout defect; the actual Belt is a separate selectable module.

- Source builder: `source/scripts/gota_crossbowman.py`.
- Source scene: `source/gota/crossbowman/hero.blend`.
- Reference: `clothing.png`, built-in imagegen; exact `clothing.prompt.txt`.
- Five runtime slots: Foot, Leg, Belt, Chest, Headgear.
- Reused fitted geometry: Clothing_16 boots and Clothing_12 upper trousers.
- Reused anatomy: shared Gota split Body, Head, Nose and original skeleton.
  Leg hides GotaSkinLower and glove/boot selections hide the corresponding
  shared hands/feet; the upper body remains visible at exposed forearms.
- Reused face: Eyes_Atlas02, Mouth_Atlas03, Brow_Atlas04.
- Hair and mustache reuse Hair_01 and Beard_02 geometry as hero-local copies,
  recolored brown; the mustache is broadened to match the approved character.
- Exported visible assembled triangles: 17,414, below 20,000.
- New clothing image textures: zero; all five modules use solid-color materials.
- All new geometry has finite positions and normalized weights.
- `animation_verification.json` verifies every new node deforms under the shared
  22-bone rig, and existing Walk_Loop changes geometry at frames 0, 10 and 20.

The independent judge accepted the clothing sheet with the duplicate-belt
correction. First model review found hood and knee clipping, a narrow dark
mustache, and a missing rear tunic split. Those were corrected with a larger
hood enclosure, fuller trousers, brown widened mustache, and divided rear
tunic panels. The chest has greater clearance during crouching.

Actual runtime front/back, Walk_Loop, Crouch_Fwd_Loop and individual slot
renders are in `renders/`. Side-by-side comparisons are `comparison.png` and
`items_comparison.png`; the combined browser review is `review.html`.
Final independent judgment: PASS, recorded in `judge.md`. The judge reopened
both comparisons and model/walk/crouch renders at full size. No visible hood
penetrations or knee exposure remain in the inspected views and poses.

Shared-body integration was rebuilt and rerendered; `finalize_gota.py` saved
`hero.blend` with only selected components visible. Runtime export and existing
Walk_Loop checks were rerun after this final rebuild.
