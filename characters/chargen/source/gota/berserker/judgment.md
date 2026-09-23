# Berserker independent fidelity review

## Approved reference requirements

Reviewed `../approved_roster.png`, bottom row, fifth hero, against `../workflow.md`.

- Human face and warm peach skin; large existing eyes are appropriate. No undead, glow, or mask treatment.
- A broad angular orange-red mane frames the head, with pointed side tufts and a matching short angular beard. A modest gold diamond crest is centered at the hairline. The hair must remain the dominant head silhouette.
- The torso is bare human skin with one broad dark brown diagonal strap running from the hero's left shoulder (viewer right) to the opposite waist. No chest armor, shirt, or robe. Small dark gray wrist cuffs leave the hands bare.
- A dark brown belt has a clearly visible gray polygonal open-centered buckle. No gold belt buckle.
- The hip layer comprises tan pointed fur side panels and a longer central brown pointed front panel. It is a short rugged skirt, not a robe.
- Dark charcoal fitted legs are visible below the skirt.
- Short brown faceted boots have substantial tan fur cuffs. They should read as medieval leather boots, not armor greaves or modern footwear.
- The figure has a large chibi head, short torso and limbs, flat shaded low-poly facets, and simple solid material colors. No surface image textures on new clothing.
- No weapons, shields, loose props, or chains. Clothing slots are Foot, Leg, Belt, Chest, Headgear. Hair and beard may reuse existing separate parts.

## Review plan

The clothing sheet must provide five separate item rows (boots, legs, belt, body, hat) with front and back views of each. Body can comprise the diagonal harness and wrist cuffs without a mannequin. Headgear is the small crest, with hair and beard separately reusable. Fur skirt ownership may be legs or belt if the final assembled silhouette and independently selectable slots remain correct.

Actual models require front/back assembled and isolated-item renders, plus side-by-side comparisons to both the approved character and the generated clothing sheet. Visual judgment must check shape, color placement, item fit, clipping, omission, and whether the model has drifted from the original reference. Back design can be a conservative continuation of the visible front rather than an unsupported elaborate addition.

## Status

Initial reference requirements recorded. Generated sheet and actual model review pending; no completion verdict yet.

## Clothing reference review

Reviewed `clothing_reference.png` against the approved Berserker. Verdict: acceptable modeling guide with corrections below; this is not an actual-model pass.

The five required item rows and front/back columns are present. Brown fur-cuffed boots, charcoal pants, tan hip fur, long brown center flap, dark brown belt, open gray hexagonal buckle, diagonal brown harness, gray wrist cuffs and small gold crest agree with the approved design. The isolated headgear correctly avoids turning the full mane into a helmet.

Corrections and modeling guidance:

1. The legs row duplicates the boots and cuffs already present in the boots row. Export the Leg slot without those duplicates; the Foot slot owns boots and cuffs.
2. The sheet's BODY front and back have the same apparent diagonal. A real wraparound diagonal harness must appear mirrored from the rear. Front runs from viewer right shoulder to viewer left waist; rear should run from viewer left shoulder to viewer right waist. Model a continuous fitted shoulder/torso wrap, not two disconnected strips.
3. Keep the original short skirt proportions. The central brown flap should terminate around the upper knee area, and the side fur should end higher. Avoid making the charcoal pants as ballooned as the isolated sheet might suggest.
4. The gold crest's halo is a reference rendering effect. Use a solid gold material with no emission/glow. In the assembled rear view, the head and mane should obscure the front crest naturally; do not add a second rear-facing gold diamond.
5. The original bare torso, orange-red mane/beard, and visible human face are essential identity features absent from the isolated clothing sheet. Keep them in the assembled model. The dark wrist cuffs must leave a visible bare forearm segment and bare hands.

The generated sheet does not establish skin weights, physical fit, animation behavior, polygon count, or final model fidelity. Those remain pending.

## Draft model review

Reviewed `draft_front.png` and `draft_back.png`. This is an early visual review, not the final runtime or complete technical verdict. The reported 13,354 triangles have not been independently counted by this judge.

The model has the required recognizable Berserker silhouette: a substantial angular orange-red mane, matching beard, modest centered gold crest, bare human torso, brown diagonal harness, dark wrist cuffs, gray open hexagonal belt buckle, charcoal pants, tan side fur, brown front panel and brown boots. Rear harness direction is now correct. No shield, weapon, loose prop, or unrelated ornament is visible. The rear hair volume is coherent, and the front-only crest is correctly hidden at the back. No clear clothing clipping is visible from these two views.

Two small shape refinements would strengthen fidelity:

- The boot cuffs currently read as narrow tan bands. The reference shows thicker turned-down fur cuffs. Increase their vertical depth slightly and give them a more visible outward flare and jagged lower edge, while keeping boots short.
- The brown front flap currently ends in one clean V. The approved roster and clothing sheet have a more rugged three-point/notched hem. Adding small lower side notches would reproduce that characteristic without adding much geometry.

The white eyebrows and gray iris previews are explicitly excluded from this draft verdict because the author reports runtime color overrides. Final runtime evidence must show orange-red brows and brown eyes. The fixed chargen rig's slimmer bare torso and straight legs are acceptable provided the final shared rig and selectable clothing fit correctly.

Draft verdict: clothing and silhouette substantially match, with minor fur-cuff/flap refinements recommended and runtime color/technical verification still pending.

## Final runtime review

Verdict: PASS for Berserker character fidelity, five clothing slots, exported geometry checks and the supplied runtime pose samples. No remaining material visual defect was found in the reviewed evidence.

Reviewed current `comparison.png` side by side with the approved hero and generated clothing sheet, `items_comparison.png`, full-size `renders/model.png`, `renders/walk.png`, `renders/crouch.png`, and each full-size isolated item image (`Foot.png`, `Leg.png`, `Belt.png`, `Chest.png`, `Headgear.png`). Draft images are superseded.

- The assembled front and back retain the orange-red angular mane and beard, natural brown eyes, orange-red eyebrows, solid gold central crest, bare human chest, diagonal dark leather harness, gray wrist cuffs, gray open polygon belt buckle, brown front flap, tan pointed hip fur, charcoal legs, and brown fur-cuffed boots. No props or weapons are present.
- The five isolated clothing exports match their intended rows. Foot owns both boots and cuffs. Leg contains trousers and skirt panels with no duplicate boots. Belt is separate with a gray buckle. Chest combines the correctly mirrored wraparound harness and two cuffs. Headgear is a small solid gold crest and brown band. Isolated rear views can see the far-side crest/buckle in empty space; the assembled body and mane correctly occlude them.
- Both requested draft refinements are implemented. Fur cuffs now have greater depth and visible flare. The front flap has a rugged three-point hem; the shorter back flap remains a simple point.
- Walk and crouch samples show the fitted trousers and all clothing following the rig. The previous reported trouser poke-through and skirt twisting are not visible in these supplied views. The short hip-bound fur/leather panels preserve their shape, and cuffs/boots follow the limbs. These samples establish animation behavior at the inspected poses, not an exhaustive proof of every animation frame.
- Minor reference differences are acceptable for the established chargen rig: the bare torso is slimmer and less muscular, and the mane has a heavier fringe. They do not obscure the reference identity or required clothing.

Technical evidence: read `verification.json`, `export_audit.json`, and the relevant common export/verification implementation. Independently parsed the seven current exported GLBs with a separate Python check, verifying every primitive has finite positions, normalized skin weights within 0.0001, the audited shared joint-name set, triangular geometry, and no embedded images or textures. Independently counted 8,814 triangles across the seven new exports: Foot 1,080; Leg 3,268; Belt 432; Chest 1,408; Headgear 46; Hair 1,594; Beard 986. The current visible-node inventory sums to 15,070 triangles including reused base/face parts, below the exclusive 20,000 limit. The common verifier resolves selected part metadata and hiding rules to count the actual visible runtime nodes.

Final review status: Berserker is ready for root integration. Shared viewer/manifest integration remains the root agent's responsibility.

## Shared body integration recheck

Final current verdict: PASS. This entry supersedes the previous assembled triangle total.

After the shared body split, re-read `verification.json` and `export_audit.json` and inspected the regenerated `comparison.png`, `items_comparison.png`, `renders/model.png`, `renders/walk.png`, and `renders/crouch.png`. The costume, reference fidelity, independent five-slot presentation, natural face colors and inspected pose behavior remain correct. No new visual defect or exposed gap appeared after hiding the covered lower body.

Verified that the current Leg metadata hides `GotaSkinLower`, the visible-node inventory omits that lower-body node and retains `GotaSkinUpper`, and its node counts sum to **13,790 triangles**. This is below the exclusive 20,000 limit. The seven exported hero parts remain **8,814 triangles** total with all reported export checks passing. The current runtime images retain the earlier accepted visual result while removing hidden base geometry.

Berserker remains ready for final root integration; no costume change is requested.
