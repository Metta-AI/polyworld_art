# Druid Warden construction

Approved source is the fourth character in the top row of `../approved_roster.png`.
The final split reference is `clothing_reference_v2.png`, generated with the
built-in imagegen tool. Exact generation and edit prompts are retained beside it.

The builder reuses the existing rig, face, focused eyes, heroic brows, elf ears,
14 Tan cuff boots, 09 Brown trousers, 06 Leather jerkin, 12 Wolf cut, and
09 Tapered wedge beard. Boot shafts are lengthened to meet the trouser ends;
hair and beard are simplified and recolored green. New geometry adds the
antlers, leaf shoulder mantle, leaf skirt, brown wrist guards, bark chest panels,
gold hexagonal buckle, and central leaf hair/beard accents.

The five clothing slots are separate. Foot contains the boots and their cuffs.
Leg contains trousers and leaf skirt panels. Belt contains only the brown waist
band and gold buckle. Chest contains the fitted bark jerkin, shoulder leaves and
wrist guards. Headgear contains only the antlers and their leaf ornaments.
Hair and Beard remain separately selectable reused components.

The generated reference's brown trouser cuffs are interpreted as tucked ends
inside the boots so the assembled model does not show two stacked cuffs.
The trouser topology is retained with additional clearance, and its upper boot
cut section extends inside the cuffs. Extended boot shafts resample weights
from the current body and feet. The shared Gota base hides covered lower-body
skin while preserving the exposed arms and separately reused hands.
All clothing colors are solid shader colors. Existing eye/face decals are
reused as permitted by the user's instruction.
