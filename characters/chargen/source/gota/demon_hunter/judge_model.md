# Demon Hunter model review

## First preview

Reviewed `preview_front.png` and `preview_back.png` against the approved roster
and split clothing reference on 2026-09-18. These temporary previews use gray
skin, so skin color is excluded from this pass.

The model is recognizable from its charcoal spiky hair, opaque crimson
blindfold, sleeveless dark vest, bare upper arms, brown harness and guards,
layered hips and narrow forked red cloth. Slot ownership appears consistent:
the lower panels do not overlap a duplicate body skirt. No weapons or loose
props appear.

Required corrections before final review:

- Replace the separated front harness pieces with broad continuous crossed
  straps. The back straps also pinch to a point instead of overlapping.
- Broaden boot cuffs to match their prominent brown shape in both references.
- Turn the small raised red lozenge on the blindfold into broad diagonal
  overlapping fabric bands.
- Thicken the silver square buckle rim. It currently looks like thin wire,
  unlike the broad metal buckle in both references.
- Apply the intended pale peach human skin before the final preview.

Minor improvement: a folded edge on the neck scarf would strengthen its cloth
appearance. The tallest hair spike could be shorter or broader at the root,
but the current spiky hair silhouette is sufficiently characteristic.

Verdict: recognizable work in progress, not yet a final pass. Polygon count and
the final runtime presentation have not been verified in this review.

## Canonical runtime preview

Reviewed `comparison.png`, `items_comparison.png`, `renders/walk.png` and
`renders/crouch.png`. The comparisons place the approved roster and generated
clothing sheet alongside actual assembled and separate-item renders.

The static assembled character now passes the main silhouette and palette
comparison. The continuous crossed harness, broad cuffs, thicker silver buckle
with tongue, folded scarf and peach human skin resolve the first review's main
issues. The five separate item groups are visibly present in the item sheet.

Two required corrections remain:

- The blindfold still has a small horizontal raised lozenge. Replace it with
  broad diagonal overlapping bands matching both references.
- The crouched back view has large peach gaps between the vest and harness near
  the shoulders, and a horizontal exposed skin strip above the waist belt.
  Correct the chest shell's fit or skin weights and maintain overlap at the
  waist and shoulders through this pose. A smaller side-waist exposure is also
  visible in the walking view.

Verdict: static visual fidelity passes; final acceptance is pending blindfold
geometry and the chest deformation fix. Polygon count remains outside this
visual review.

## Final verdict

Reviewed the regenerated side-by-side comparisons, isolated clothing items,
walking pose and crouched pose after the fitted chest and blindfold changes.

PASS for visual fidelity and the inspected deformation poses. The model retains
the approved character's defining spiky charcoal hair, opaque crimson eye
covering, human lower face, sleeveless vest, crossed brown harness, silver square
buckle, narrow forked red cloth, layered hip panels and brown boot cuffs. The
new blindfold has a broad diagonal fabric fold instead of the raised lozenge.
The previously reported back and waist skin gaps are absent in the updated
crouching and walking views. The separate-item comparison shows the five
requested clothing slots from front and back.

The inspected `verification.json` reports 17,604 assembled visible triangles,
below the exclusive 20,000 budget, and zero new clothing textures.
`export_verification.json` reports finite positions, normalized weights, a
shared skeleton and no textures for all six exported clothing/hair groups.
This review did not independently recount the GLB triangles; its polygon
statement is based on the inspected verification artifact.

No further visual corrections are required by this review.

## Shared body integration spot-check

Reinspected the regenerated assembled comparison, separate-item comparison,
walking view and crouching view after the shared Gota skin split integration.
PASS remains current: the character silhouette and clothing are unchanged,
hands remain correctly covered by gloves, and no exposed skin gaps returned at
the back or waist. The current verification artifact reports 17,604 visible
triangles. The inspected animation artifact reports finite motion and all 36
new meshes deforming in both Walk and Attack01. The review does not claim an
independent frame-by-frame examination of those complete animations.
