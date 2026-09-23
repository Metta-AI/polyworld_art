# Demon Hunter completion

The actual modular character is complete and the independent judge gave a final
visual PASS after reviewing the approved roster, generated split clothing sheet,
actual front/back item renders, assembled runtime model, and walk/crouch poses.

- Builder: `source/scripts/gota_demon_hunter.py`.
- Authoring source: `hero.blend`.
- Required modular slots: Foot, Leg, Belt, Chest, Headgear.
- Additional modular slot: Hair, using the existing fitted pixie hair as its base.
- Visible assembled exported triangles: 17,604, below the exclusive 20,000 limit.
- Reused fitted geometry: Clothing_14 boots, Clothing_12 trousers, Hair_13 hair,
  Body-derived torso with Clothing_06 sleeveless pattern, Hand.Left and Hand.Right.
- Reused runtime selections: Gota split base body, Base head, tiny nose, focused eyes, neutral
  mouth, heroic brows. The opaque blindfold hides the selected eyes and brows.
- New clothing and hair use solid-color materials without image textures.
- Actual exported GLBs were parsed to verify finite positions, normalized weights,
  valid indices, valid joint references, and joint sets matching the shared rig.
- All 36 new meshes deform under the existing Walk and Attack01 actions; sampled
  evaluated geometry remains finite. Runtime walk and crouch were visually reviewed.
- The clothing image was generated using the built-in imagegen tool. Its exact
  prompt is in clothing_prompt.txt and image in clothing_reference.png.

Runtime assets each have a matching JSON sidecar:

- clothing/boots/gota_demon_hunter_foot.glb
- clothing/pants/gota_demon_hunter_leg.glb
- clothing/belts/gota_demon_hunter_belt.glb
- clothing/torsos/gota_demon_hunter_chest.glb
- hats/gota_demon_hunter_headgear.glb
- hair/gota_demon_hunter_hair.glb

The review artifacts are comparison.png, items_comparison.png, modeled_items.png,
review.html, renders/model.png, renders/walk.png, and renders/crouch.png.
The independent findings and final PASS are preserved in judge_reference.md and
judge_model.md. Numeric and deformation evidence is in verification.json,
export_verification.json, and animation_verification.json.

The hero-local blend was finalized with only the selected outfit visible, in
A_TPose. authoring_verification.json confirms visible nodes exactly match the
verified runtime selection. The leg slot hides the shared covered lower body.

No remaining known visual or mesh issues. Shared manifests and the master
character.blend were not edited by this character builder.
