# Crossbowman independent visual review

Status: Revised model visually approved after reviewing the original roster,
generated clothing sheet, assembled model, isolated items, and two animation
poses. Earlier revision findings below are resolved by the final review.

Reference: `../approved_roster.png`, bottom row, second character.

The identifying shape is a compact medieval human in an angular brown hood,
with brown hair, a wide brown mustache, and a clearly visible human face.
The hood has a shallow top point and a wide opening around the cheeks.

Required clothing details:

- Broad crossed brown leather chest panels over muted brick-red sleeves.
- Brown bracers or gloves, without mechanical or modern detail.
- Broad brown belt with a small square gold buckle.
- A short red tunic with separate lower front panels and a visible center split.
- Dark charcoal trousers and brown boots with broad upper cuffs.
- Flat color materials and visible low-poly facets without surface textures.
- No weapons, shields, goggles, loose props, or glowing components.

The final review must compare the assembled front and back render with both
the original roster and generated split clothing sheet. Isolated boots, legs,
belt, body, and hat must also be reviewed against the corresponding split
reference. The back is inferred because the approved roster shows only the
front. No completion verdict is possible before those artifacts are supplied.

## Generated split clothing sheet review

Reviewed `clothing.png` against the approved roster. The sheet has clear front
and back columns and all five required clothing categories. Its angular brown
hood, crossed leather chest panels, brick-red tunic and sleeves, charcoal
trousers, gold square buckle, and brown cuffed boots preserve the character's
main identifying clothing. It contains no weapons, goggles, machinery, or
unrequested loose props. The proposed back is consistent with the visible
front design. The sheet is suitable as a modeling reference.

Concrete modeling corrections and checks:

- The body row redundantly includes the complete belt already in the belt row.
  Keep the modeled belt only in its separate selectable belt item.
- Keep the hood opening wide enough for the brown hair, human face, and broad
  mustache from the original roster. The empty clothing sheet cannot verify
  these essential character details.
- Fit the short sleeves and bracers to the existing horizontal arm rig; the
  detached sheet's sleeve angle is presentation rather than a required pose.
- Use solid material colors. Shading in the generated reference must not
  become baked lighting or surface texture on the models.
- Verify that the gold buckle remains a modest accent rather than scaling the
  larger isolated-sheet buckle to dominate the assembled torso.

Verdict: Clothing reference passes, with the duplicate belt explicitly
excluded from the body model. Assembled and isolated model fidelity remains
unverified until front and back renders are reviewed.

## First actual model review

Inspected `comparison.png` and `items_comparison.png` side by side with their
embedded references, then inspected `renders/model.png`, `renders/walk.png`,
and `renders/crouch.png` at full presentation size. These show actual exported
items in front and back views and two bent-limb poses.

The five exported clothing categories, medieval color palette, crossed chest
panels, separate square-buckle belt, brown cuffed boots, visible human face,
and absence of props match the intended design. Flat facets and solid colors
are visible. The duplicated belt from the generated body reference is absent
from the isolated body, as required. Existing rig proportions are slimmer
than the illustration; retaining the established rig is appropriate.

Required corrections before model approval:

1. Hood clipping: hair protrudes through the top and rear. The rear center
   also shows a dark mouth or mustache-like strip and a pale triangular skin
   patch in all three inspected poses. Fully enclose the rear head and check
   the rendering orientation and depth. Widening only the crown is not enough.
2. Trouser clipping: a clear pale skin patch breaks through the forward bent
   knee in the walk pose. The crouch has a much larger exposed knee patch and
   further skin specks in back. Match trouser deformation to the base legs
   and provide enough knee clearance in the bent poses.
3. Mustache fidelity: the current narrow, almost black mustache is much smaller
   than the broad brown mustache that identifies the original hero. Enlarge
   the width and use a brown consistent with the hood and leather palette.
4. Rear tunic fidelity: the generated clothing sheet has separated rear red
   tails, but the model's back is a continuous panel. Add the central rear
   slit while retaining sensible coverage in the animation poses.

The modeler reports 17,637 triangles, five slots, normalized skin weights,
shared skin, and no textures. This review's visual evidence supports the
slot and style claims, but is not itself a file-level verification of the
triangle count or skin normalization.

Verdict: Revision required. The clothing direction matches; visible head and
knee intersections prevent completion. Recheck front, back, walk, and crouch
after fixes, including updated assembled and isolated comparisons.

## Final revised model review

Reopened the regenerated `comparison.png`, `items_comparison.png`, and the
front/back `renders/model.png`, `renders/walk.png`, and `renders/crouch.png`.
The comparison sheets show the current model alongside the original hero and
the split clothing sheet, with each exported clothing category shown in front
and back views.

All four earlier findings are resolved in the inspected renders:

- The hood completely covers the back of the head. No hair, pale skin, or
  facial features break through the crown or rear in the inspected poses.
- The fuller trousers cover both knees in the walk and crouch images.
- The widened brown mustache now reads as the original hero's defining broad
  facial hair rather than a small dark accent.
- The rear tunic now has separated red panels and a clear central split.

The Crossbowman retains the original brown hood, visible human face and brown
hair, crossed leather torso panels, muted red short sleeves and split tunic,
charcoal trousers, small gold buckle, and brown cuffed boots. It reads as a
medieval character with no modern equipment, weapons, shields, or loose props.
The five clothing categories remain independent and the body has no duplicate
belt. Flat colors and deliberately faceted geometry fit the Polyworld rig.

Read `verification.json`: it reports 17,414 assembled triangles with a strict
20,000 limit, all five clothing slots plus hair and beard, no new clothing
textures, normalized weights, and reused eyes, mouth, brows, body, head, and
nose. Read `exported_verification.json`: every exported item reports finite
positions, normalized weights, the shared skeleton, and zero clothing
textures. Read `animation_verification.json`: it records the 22-bone rig,
finite deformed positions, existing walk animation, and changed vertices in
each modeled clothing and hair part. These are inspected verification reports,
not an independent rerun of their generating checks.

Final verdict: Visual pass against the approved hero and split clothing
reference. No blocking defects remain in the inspected front, back, walk,
or crouch renders. This verdict covers those supplied views and poses; the
shared runtime and any later geometry changes remain subject to integration
verification by the parent task.

## Shared body integration recheck

After the shared Gota body integration, reopened the latest assembled, walk,
and crouch renders and both side-by-side comparison sheets. The reviewed
costume, silhouette, face, separate items, and clean knee and hood coverage
are unchanged. No new visible defects appear in these views. The latest
`verification.json` reports 17,414 triangles and lists `GotaSkinUpper` in place
of the earlier full body, with zero new clothing textures and normalized
weights still recorded. Final visual verdict remains pass.
