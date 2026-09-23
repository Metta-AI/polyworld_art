# Lich visual review

Independent judge: `/root/lich/lich_judge`.

## Reference sheet

Inspected `../approved_roster.png` and `clothing_reference.png`.

The split sheet preserves the royal-blue and navy palette, broad ivory robe
trim, brown belt with gold diamond buckle, simple blue boots and five-point
crystal crown. Faceted geometry and solid colors match the approved style.

Reference-sheet verdict: pass with modeling corrections.

- Keep the belt exclusively in the independent Belt slot. The generated body
  image repeats the belt and must not result in duplicate belt geometry.
- Keep the hood opening predominantly blue and white hair. The sheet adds a
  broad ivory hood border that is stronger than the approved roster.
- Fit the robe to the roster's knee-length proportions and flared short
  sleeves rather than copying the sheet's isolated-item scale literally.
- Preserve a living pale face, natural blue eyes and white hair when the
  clothes are assembled. No skull or luminous-eye treatment is acceptable.

## Actual model

Reviewed the first actual Blender geometry draft at
`polyworld/tmp/chargen/gota/lich/draft.png`. The crown, split trimmed robe,
flared sleeves and diamond buckle make the intended character recognizable.
No obvious front-view belt or robe collision is visible.

Requested geometry corrections before final review:

- Reduce the conspicuous dark cavity above the crown band by fitting the
  hood and crown closer to the hair or filling the missing head volume.
- Add narrow pale cuffs at the sleeve ends, as shown in both references.
- Prefer angular white bangs and side locks over the current blunt bob when
  an existing reusable hair asset supports that silhouette.

## Runtime review

Inspected `comparison.png`, `items_comparison.png`, `renders/model.png`,
`renders/walk.png` and `renders/crouch.png` side by side with the approved
hero and generated clothing reference.

Static visual verdict: pass. The pale living face has ordinary blue eyes;
the hood, crystal crown, white hair, blue and ivory robe, gold buckle and
simple blue boots preserve the identity. The crown gap is closed, ivory
wrist cuffs are present, the swept hair fits the source better, and the
separate Chest render no longer duplicates the belt. Both front and back
have solid low-poly colors. The isolated front/back panels cover all five
requested clothing slots.

The initial animation review found rear boot penetration and severe rear
hem curling. Reinspected regenerated `renders/walk.png` and
`renders/crouch.png` after rear-skirt weight and clearance changes.
Those defects are resolved: the feet now stay below the rear hem or use
the intended front opening, and the rear robe keeps a coherent shape.
Garment animation verdict: pass for these inspected poses.

Reinspected the final regenerated comparison panels, walk and crouch
renders after shared lower-skin hiding. The pale knee triangle is gone.
The robe remains coherent from front and back in both inspected poses,
with no recurrence of rear boot penetration or curled rear hem.

Overall visual verdict: PASS. The final model matches the approved Lich
identity and the five split clothing items in the Polyworld chargen
style. All requested corrections are visibly resolved. No outstanding
Lich-specific material or geometry changes are requested.

Read `verification.json` and `export_checks.json` alongside the final
renders. Current assembled count is 15,101 triangles, below the exclusive
20,000 budget. The recorded five exported slots use 22 shared joints,
zero clothing textures and normalized weights, with maximum recorded
weight error below 0.0000001. The reused hair, eyes, mouth, brows, head
and nose are enumerated in `verification.json`. These technical checks
are reported from the inspected validation artifacts; this judge's
independent work is the visual comparison and pose review.
