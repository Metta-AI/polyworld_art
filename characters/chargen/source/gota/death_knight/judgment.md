# Death Knight independent fidelity review

Status: Accepted after corrections and final runtime review on 2026-09-18. Earlier sections preserve the review history.

## Approved reference requirements

Reviewed `../approved_roster.png`, bottom-left Death Knight.

- The character is an actual dark-brown-skinned human with visible natural brown eyes and no eye glow. The helmet has an open face, gray cheek guards, and a slate-gray angular crown with five uneven upward spear-like spikes and a centered cyan diamond.
- The chest has angular gray segmented plate, a centered cyan diamond, layered pointed pauldrons, small upward shoulder spikes, gray arm armor, and dark gloves.
- The waist has dark strap structure, angular central gray fauld, and long gray tassets over dark trousers.
- The boots have angular gray toe and shin plates, prominent knee guards, and cyan knee diamonds.
- The dark navy-charcoal cape is long, wide, and split into pointed lower panels, and belongs to the body item.
- Geometry should be faceted and solid-colored without surface textures. No weapons, shields, or loose props.

The most important silhouette cues are the open spiked crown, broad pointed shoulders, and long split cape. Fidelity must preserve the human face and normal eyes while retaining these cues.

## Required review evidence

The clothing sheet must show isolated front and back views for boots, legs, belt, body, and hat, with the cape attached to body and no mannequin. Actual assembled and isolated-item model renders must be compared side by side against both the approved roster and the clothing sheet. Geometry/rig audit results are needed separately to verify fewer than 20,000 visible triangles, finite geometry, normalized weights, shared skeleton, and retained animation.

## Clothing reference review

Reviewed `clothing_reference.png` against the approved roster on 2026-09-18.

Verdict: Accepted as a modeling guide with the following explicit corrections during construction.

The sheet preserves the strongest cues: a faceted open five-spike helmet with centered cyan jewel, slate segmented armor, long split dark cape, angular boot armor with cyan diamonds, and the central metal belt buckle. Front and back views are present for all five requested rows. The colors and faceted surface treatment are faithful, with no weapons, shields, loose props, or visible surface-texture detail.

The body row redundantly includes belt, tassets, and tabard. These should not be duplicated into Chest: keep the central buckle and strap in Belt, tassets/tabard and trousers in Leg, and torso/arm armor and cape in Chest. The independent Belt and Leg rows already define these pieces.

Modeling guidance:

- Keep the shoulder spikes shorter than the helmet spikes, closer to the roster. The generated shoulder spikes are taller and could compete with the defining helmet silhouette.
- Preserve a large unobstructed face opening and fit cheek guards around the existing face. The sheet has no mannequin and cannot establish the essential human face and normal-eye requirement by itself.
- Make the cape predominantly broad split panels rather than many narrow spikes. The roster uses a readable pointed cape silhouette.
- Keep saturated cyan confined to the attached helmet/chest/boot diamonds, with the tabard diamond in darker blue, as shown.

Remaining review: actual assembled/isolated model renders, side-by-side comparisons, and geometry/rig audit evidence.

## Provisional assembled mesh review

Reviewed `/Users/me/p/polyworld/tmp/chargen/gota/death_knight/preview.png` against both references. This is a temporary front-view mesh render, not the final exported runtime model.

Verdict: Recognizable Death Knight with two geometry refinements and unresolved facial material issues before acceptance.

The assembled silhouette correctly shows the five-spike open helmet, dark human face, cyan helmet/chest/knee diamonds, segmented hip plates, dark tabard with blue diamond, angular gray boots, and broad split dark cape. The shorter body and larger eyes fit the existing chargen rig. No props are present.

Required corrections:

1. Move the small shoulder spikes outward enough to be visible beyond the head/cheek guards. Their current near-total occlusion removes a key silhouette cue from both references. They should remain shorter than crown spikes.
2. Add one or two explicit overlapping abdomen plates below the chest emblem, keeping the central silhouette compact. The current chest appears as a small separate shield-shaped breastplate on a broad dark shirt; the roster and clothing sheet both read as a more continuous segmented cuirass.
3. Resolve white eyebrows, pale gray irises, and white lower-head triangles. These are visible material defects in this preview. Final acceptance requires dark brows, natural brown eyes, and no white facial/neck artifacts.

Optional refinement: a slightly lower central point on the helmet brow would more closely echo the references' V-shaped face opening, while keeping the actual human face unobstructed.

The 18,368 triangle total is agent-reported at this stage and has not been independently confirmed by this visual review. Final front/back and isolated-item comparisons, material verification, and rig/geometry audit remain outstanding.


## Final runtime model review

Verdict: Accepted for the Polyworld chargen style. No remaining material fidelity blocker was found in the reviewed final views.

Reviewed `comparison.png` with the approved roster, generated sheet, and actual front/back runtime model side by side. Reviewed `items_comparison.png` with the reference and all five separately exported items side by side. Also reviewed the newest `renders/model.png`, `renders/walk.png`, and `renders/crouch.png` directly; older root-level PNGs are superseded.

The final model preserves the essential Death Knight identity: actual dark-skinned human face, natural brown eyes, black brows, open five-spike slate helmet with cyan center diamond, pointed shoulder armor, overlapping abdominal plates, split dark cape, gray hip tassets, dark pointed tabard, angular gray boots, and cyan knee/chest jewels. All props are absent. The previously white face artifacts are gone, shoulder spikes are visible, the chest has the requested overlapping lower plates, and the two outer helmet spike bases now meet the helmet shell.

The five isolated export views establish that boots, legs, belt, body/cape, and helmet are actual separate modeled items. Waist pieces are not duplicated into Chest. The rear cape is broad and pointed, and the helmet back covers the head as expected. The sheet's denser folds and plate detail were simplified while retaining its palette and characteristic silhouette; the existing chargen proportions and mitten hands remain recognizable.

Animation spot checks show the same clothed character in walk and crouch poses. Minor visible limitations: the shoulder spikes rotate sideways with the upper arms during walking, and the very low-poly cape forms a sharp fold in crouch. These do not remove the intended identity or detach the clothing in the inspected poses.

## Independent export inspection

Independently parsed the five exported GLBs listed in `parts.json` and saved results in `independent_audit.json`. All five contain skinned meshes, zero image textures, finite vertex positions, normalized finite weights, and identical ordered 22-joint skeleton names. Clothing totals by slot: Foot 3,748; Leg 1,960; Belt 170; Chest 6,482; Headgear 300 triangles, for 12,660 clothing triangles. `verification.json` counts the actual selected base and face parts as well, giving 16,556 assembled triangles, below the exclusive 20,000 limit. `animation_check.json` reports finite deformed vertices across three actions and three sample frames on the shared rig; actual walk/crouch images provide visual deformation evidence.

Review scope: this verdict covers the Death Knight's artifacts and exports. Shared manifest integration and the full ten-character runtime still require the root agent's integration audit.


## Final split-base refresh

Re-reviewed the refreshed `renders/model.png`, `renders/walk.png`, `renders/crouch.png`, and `comparison.png` after the shared Gota base rebuild. Acceptance is retained. The lower-body skin is hidden by the Leg part; no new exposed lower-body skin or visual fidelity regression appears in the refreshed views. Clothing geometry and its 12,660-triangle total are unchanged. `verification.json` now reports 16,556 selected assembled triangles using `GotaSkinUpper` and hiding `GotaSkinLower`. The five clothing GLBs were independently parsed again; all prior finite-position, normalized-weight, zero-texture, and shared-skeleton checks still pass. `independent_audit.json` records these current counts and the updated base selection.
