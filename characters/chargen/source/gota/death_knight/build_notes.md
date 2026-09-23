# Death Knight construction notes

The five wearable modules preserve the approved roster's dark human face,
open five-spike crown, slate armor, solid cyan gems and split dark cape.
The generated clothing reference was created with the built-in imagegen tool;
its exact prompt is in clothing.prompt.txt. No generated image is used as a
material texture.

Reused geometry: Clothing_15 fitted tall boots, Clothing_09 fitted trousers
(with covered lower trouser sections removed), Clothing_07 fitted shirt,
weighted Hand.Left and Hand.Right meshes for the gloves. The helmet is fitted
against the existing Head surface. Existing Body/Gota base, Face/Base,
Nose/Tiny, Eyes/14 Angular, Mouth/03 Neutral and Brow/08 Stern remain the
runtime human base.

Bespoke geometry: continuous open helmet shell and five crown spikes,
segmented torso and abdomen plates, paired pauldrons and short outward
shoulder spikes, vambraces, shin plates, layered hip tassets, pointed tabard,
waist belt and buckle, cape, and solid faceted gems. The cape is attached to
the Chest slot. The tassets and tabard belong to Leg; the waist belt is Belt.

Every clothing part exports with the shared 22-joint skeleton. Solid-color
materials contain no image textures. Vertex coordinates and skin weights
are validated during export; each weighted vertex is normalized. See
verification.json for actual selected runtime triangle counts and
animation_check.json for deformation samples.

Independent visual review is recorded in judgment.md. Provisional review
requested visible shoulder spikes and overlapping abdominal plates; both
were added before the final runtime review.

Final shared body update: GotaSkinUpper is visible; the Leg module hides
GotaSkinLower to avoid covered skin poking through trousers during animation.
The assembled character contains 17,430 triangles. The authoring blend was
finalized with only the selected Death Knight outfit visible.

## Helmet side remodel, September 22, 2026

The rebuilt helmet joins the brow, temples, cheek guards and rear cap in one
continuous shell. The lower side and rear edges now extend below the head,
covering the previously exposed lower skull. The cheek guards extend below
the jaw. The original front crown and opening remain the design reference;
the concept's open rear is intentionally replaced with full coverage, as
requested. A solid inner wall closes the rim, while a fitted subdivision
pass rounds the skull. Five crown points and the cyan gem remain separate
solids.

The face opening has a low V-shaped brow over the eyebrows, wide eye
recesses and an angular step inward beside the mouth. Its depth follows the
existing face surface with a small clearance, preserving the front outline
without projecting the armor far forward. The gem follows the fitted brow.

The helmet contains 1,174 triangles, with no open edges or degenerate
triangles. All its vertices use the existing Head bone. The clothed character
contains 17,430 triangles, or 19,838 with the existing sword and shield.
The updated authoring file is finalized on the existing shared rig.
The concept and current front, side and back views are in
`helmet/opening_comparison.png`. Hidden runtime captures, before/after views,
and animation samples are in `helmet/review.html`. Export geometry checks
are in `helmet/checks.json`, including head-surface ray samples with zero
uncovered side or rear samples. Full chargen tests and the retired-asset
checks pass.
