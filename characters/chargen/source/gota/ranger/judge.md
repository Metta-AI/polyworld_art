# Ranger independent review

Status: Reference inspected. Generated clothing and model review pending.

Approved reference: `../approved_roster.png`, top row, second character.

Essential visible cues:

- Pointed olive hood around an orange forelock and two long copper braids.
- Green scarf or cowl at the neck.
- Bare upper arms and brown wrist gauntlets.
- Crossed brown straps over an olive tunic.
- Brown belt with a small square gold buckle.
- Layered pointed tunic hem and green cape reaching the upper thighs.
- Brown trousers and tall brown boots with strong cuffs.
- Warm human skin, natural brown eyes, flat facets, and solid colors.
- No handheld weapons, shields, or loose props.

The approved front view does not specify rear construction. Rear clothing should extend the visible design coherently.

## Generated clothing reference review

Inspected `clothing_reference.png` directly against the approved roster.

The sheet has five named front/back pairs and captures the core olive hood,
crossed leather straps, square gold buckle, pointed green layers, brown
trousers, and cuffed boots. Its simple faceted surfaces suit the requested
low-poly, solid-color style. Row order is immaterial.

Required corrections for modeling:

- Use the roster's slim silhouette and bare upper arms. The sheet adds broad
  shoulder guards and skin-colored arm stubs to a detached clothing item.
  Omit those guards and do not generate duplicate skin geometry.
- Put the belt and buckle solely in the belt slot. The sheet duplicates a
  complete belt on the body. The crossed chest straps belong to the body.
- Put the neck cowl solely in the body slot. The hat and body rows duplicate
  it. Keep the hood opening clear for the copper forelock and two braids.
- Make legs plain brown trousers without feet or boot-like lower sections.
  The boots supply the cuffs, shafts, and feet. Preserve a clean overlap
  hidden inside each cuff.
- Preserve the original cape's side silhouette and thigh length. The sheet
  suggests a coherent faceted rear, but its longer center point is optional.
- Use restrained flat materials. Do not reproduce the vignette, glow, or
  apparent surface shading as textures or emissive material.
- Retain brown wrist gauntlets, natural brown eyes, and warm human skin.

Decision: The sheet is useful as an intermediate shape guide, but one
corrective generation is required before calling the separate-item reference
finished. The duplicate belt/cowl, skin stubs, and feet in the legs row violate
clean slot separation. Model work can proceed immediately from the approved
roster with the corrections above while that reference is regenerated.

Model render, assembled polygon count, and final side-by-side comparison are
still pending and are not approved by this review.

## Corrected reference review

Inspected `clothing_reference_v2.png` directly. The hood has no duplicate
cowl, the body has no duplicate belt or skin stubs, and the trousers end
without feet. All five front/back item pairs are present and identifiable.
The wrist guards are visibly detached clothing pieces associated with the
body. Olive cloth, brown leather, gold buckle, and faceted construction
remain consistent with the Ranger's identity.

Decision: Approved as a modeling guide. No further reference generation is
required. The small shoulder flanges and dark background are deviations
from the intended presentation, but neither prevents modeling the approved
roster accurately. Model bare upper arms and slim tunic shoulder openings;
ignore the background and avoid reproducing flanges as armor plates. Use
the approved roster for the face, orange hair, proportions, and cape length.

This approval covers the split reference only. Model fidelity and the
assembled polygon limit still require direct verification.

## Runtime model draft review

Inspected `comparison.png` and `items_comparison.png` side by side with the
approved hero and corrected reference. T-pose identity passes: green pointed
hood, copper twin braids, green cowl/cape, crossed brown chest straps, square
gold buckle, bare upper arms, brown wrist guards, and cuff boots are present.
The existing human face and natural eyes are retained. There are no props.
The flat-colored geometry suits Polyworld's original rig proportions; the
reference's stockier body proportions are not a modeling requirement.

The five separate clothing slots are visible in the item comparison and
listed in `parts.json`. Hair is a sixth separate slot. I independently read
the six exported GLB JSON chunks: all 12 visible custom-node triangle counts
match `verification.json`, totaling 12,390 custom triangles, with zero
textures in those six GLBs. The assembled verification manifest sums to
19,150 triangles, below the exclusive 20,000 limit. The reused base-node
counts are supplied by the assembly verifier rather than re-counted in this
independent pass.

Additional direct inspection of `renders/walk.png` and
`renders/crouch.png` found required animation fixes:

- Bent knees expose skin through the trousers in both poses.
- The belt penetrates the cape in the rear walk/crouch views.
- The cape follows the legs and distorts during crouching.

Decision: T-pose design and separate-item presentation pass. Final model
approval is withheld until the animation defects are corrected and the
updated assembled triangle count is checked. Layered front tunic hem panels
will improve the match to the approved Ranger.

## Final Ranger review

Decision: PASS for the Ranger design, split items, and tested animation poses.

Re-inspected the updated `comparison.png`, `items_comparison.png`,
`renders/walk.png`, and `renders/crouch.png`. The side-by-side comparison
retains the approved Ranger identity on the original Polyworld rig. New
layered front hem panels improve the tunic match. Hood, copper braids,
green cowl/cape, crossed leather straps, square buckle, brown wrist guards,
trousers, and cuff boots are all present, with bare upper arms and the
existing natural human face. There are no weapons or shields.

The previously exposed knees are covered in both tested animation poses.
The rear belt no longer penetrates the cape. The cape now maintains a
coherent torso-attached shape during walking and crouching. No remaining
material visual defect is evident in these views. This approval covers the
three inspected poses; it does not claim exhaustive verification of every
animation frame.

Re-read the current exported GLB data independently. All 14 visible custom
mesh-node counts match the current verification manifest: 11,844 custom
triangles across six files, with zero textures. The current assembled
manifest totals exactly 18,604 triangles, leaving 1,396 triangles below the
20,000 limit. It reports normalized weights and includes reused base face
and body nodes. The earlier 19,150 figure is superseded.

Any later shared body split or export change should refresh the assembly
verification and renders so the final evidence corresponds to the delivered
assets. No additional Ranger-specific design correction is required.

## Shared body split refresh

Decision: PASS retained after the final shared body split.

Spot-checked the refreshed front/back T-pose, walk, and crouch renders in
`renders/`. The Ranger outfit and approved silhouette remain intact. The
previous knee, cape, and rear belt defects remain resolved in these views.

The refreshed `verification.json` now totals 17,324 visible triangles,
including `GotaSkinUpper` and shared hands, with the covered lower skin
omitted. This supersedes the earlier 18,604 assembled count. Custom clothing
and hair remain 11,844 triangles with zero new clothing textures. The final
visible assembly has 2,676 triangles of margin under the 20,000 limit.
No additional Ranger-specific changes are required by this review.
