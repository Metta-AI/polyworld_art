---
name: chargen
description: Model, rig, texture, animate, review, optimize, and export modular stylized Polyworld characters in Blender, including interchangeable faces, hair, hats, clothing, and props for Chargen.
---

# Chargen character modeling

Use this workflow to turn an approved character concept into actual editable
Blender geometry and interchangeable, animated game assets. It records the
Chargen work on humanoids, facial sprites, hair, beards, gnomes, Gota heroes
and gods, equipment, clothing, expressions, and runtime optimization. Treat
proportions, style counts, and budgets below as project examples, not
requirements for every character.

The executable recipes are in [scripts/chargen](scripts/chargen).
Read the [commands and script catalog](references/chargen/tools.md)
for the task at hand and the [prompt templates](references/chargen/prompts.md)
when generating references or face art. No new image generation is needed just
to apply an existing part.

For Gota outfits, hoods, helmets, or held equipment, read the
[Gota modeling lessons](references/chargen/gota.md). They cover preserving
distinctive openings, close face fit, preset integration, and weapon sockets.

## Current sources and working layout

The active art library is `polyworld_art/characters/chargen`, beside the Nim
`polyworld` repository. Earlier conversation paths used `polyworld_data` and
the viewer names `modular_chars` and `blender_chars`; do not create new assets
under those retired Chargen paths. Inspect the current files before relying on
an older report. Keep Blender/Python authoring in the art repository and the
runtime/editor predominantly Nim.

| Location | Purpose |
| --- | --- |
| `characters/chargen/source/character.blend` | Editable common body and rig, with modular authoring objects |
| `characters/chargen/source/scripts` | Live geometry, export, texture, animation, and validation recipes |
| `characters/chargen/source` | Approved generated art, exact prompts, mappings, and source records |
| `characters/chargen/rig` | Canonical runtime skeleton and bone metadata |
| `characters/chargen/body`, `heads`, `noses`, `ears` | Independently shippable body and facial geometry |
| `hair`, `beards`, `hats` under the library | Individual mesh parts |
| `eyes`, `mouths`, `eyebrows` under the library | Individual PNGs, projection GLBs, and JSON sidecars |
| `clothing/torsos`, `jackets`, `belts`, `suspenders`, `pants`, `boots` | Separate equipment categories |
| `colors` under the library | Skin, hair, iris, and hat palettes |
| `animations` under the library | One clip per GLB, without character meshes |
| `polyworld/experiments/chargen` | Nim editor, weight preview, lineups, render tools, and tests |
| `polyworld/tmp/chargen` | Temporary references, iterations, assembled exports, screenshots, and reports |

Keep one shared authoring master where practical; game packs ship selected
parts and clips, not the entire `.blend`. Some later character recipes use
isolated authoring files before integration. Do not merge or regenerate
unrelated characters to add one part. Preserve existing user edits and stable
asset IDs. Copying the scripts into this skill does not move the live builders.

Original purchased models were useful for early proportion and animation
comparisons. They are not inputs to the active redistributable pipeline.
Follow [the art repository contribution rules](../CONTRIBUTING.md) for actual
asset additions, including provenance and dependency licenses. Keep historical
diagnoses in prose; do not restore retired meshes, extracted eye art, or old
animation packs. The bundled Python source uses [LICENSE-CODE](../LICENSE-CODE).

Removing the old viewer mode alone does not remove its dependencies. Check
authoring actions, packed images, part sidecars, manifests, and pack/export
paths as well. Use `verify_clean.py` and `clean_sources.py -- --check` to audit;
the latter needs Blender. Do not run the destructive cleanup migration as a
routine check or rebuild from a stale mixed-source `.blend`.

## Establish the target before adding detail

1. Inspect the actual reference and current model. Render the real existing
   mesh when the user asks what it looks like; generated art is not evidence
   of the geometry. Compare front, side, and back with matched scale, pose,
   camera, and lighting. A three-quarter view catches depth problems hidden
   by a front sheet.
2. Block out proportions first: head/body ratio, head width and depth, shoulder
   width, torso length, leg length, hand size, and foot placement. Our first
   interpretation drifted too far from the original silhouette; direct side
   by side comparisons were more useful than polishing that drift.
3. Keep features modular. Tiny and large noses, recessed round ears and elf
   ears, facial decals, hair, beards, hats, garments, belts, and weapons need
   independent objects and selection. Do not remove the attachment mechanism
   when temporarily making a nose or ears invisible.
4. For a collection, generate a consistent reference sheet first. A 4x4 hair
   sheet means 16 styles, each with a front/back pair, not 32 unrelated styles.
   Confirm the actual image contains four rows; one generation produced five.
   Obtain requested concept approval before cutting or modeling when the user
   specifically asks to review first.
5. Model a small representative part, export it, and check it in the game
   renderer before making the entire collection. Simple silhouettes and solid
   materials worked well for these characters; a trim-sheet workflow from
   other Polyworld art does not automatically apply to every garment.

For the Gota roster, reuse the approved body, rig, facial decals and eyes;
generate references for the missing clothing or equipment. Keep clothing and
props as solid-color geometry, with smooth curved surfaces and deliberate
facets. User corrections override incidental details in generated concepts:
the Lich remains pale and human, the Death Knight has a human face, and the
Crossbowman uses medieval equipment. Natural human skin variation and the
blue/purple creep colors are separate design choices.

## Body, topology, and normals

Use Blender's `bpy`, `bmesh`, `mathutils`, and `BVHTree` through its background
Python runner. Save reproducible recipes rather than relying only on a manual
mesh edit that the next build will erase. The reference workflow used Blender
5.2.2; check the installed version and live code when APIs change.

Start from the actual body surface for fitting. Reuse silhouette and skin
weights; offset, cut, and extrude where needed. Smooth shading changes normals,
not the polygon count. The body should be smooth shaded. Preserve intentional
creases and sharp rims rather than smoothing every edge or globally faceting
every low-poly surface.

A polygon budget is a ceiling, not a target to undershoot as far as possible.
Add segments where bows, guards, staffs, horns, rims, or blades visibly curve.
Smooth normals cannot repair a curved silhouette reduced to straight chords.

Hands and feet need convincing joints and silhouettes. Align wrist and ankle
boundaries, retain support vertices, and check them in motion. The approved
mitten hand curl faces downward. A continuous-looking joint may remain modular;
it does not have to be welded into the torso. Ears need a recessed bowl and
raised rim, not a flat slab. Keep the face clear of clipping noses and beards.

Use deliberate mesh flow and extrusion for large shapes. Intersecting details
can be appropriate for buttons or hair locks, but an assembly of overlapping
boxes is not a substitute for a fitted coat or connected limb. Inspect back
faces, openings, loose geometry, normals, and gaps from multiple directions.

## One rig, explicit weights, faithful animations

Every part must agree with the canonical joint names, parent hierarchy,
coordinate convention, rest transforms, and inverse bind matrices. The
runtime rebinds part joints to one shared skeleton by name and rejects
incompatible bind poses. Merely calling both rigs humanoid or Unity-compatible
does not establish compatibility.

Our shared rig has 22 mapped bones. Keep at most four joint influences per
vertex, nonnegative and normalized. Projected face decals and rigid head parts
can use weight 1 on `Head`. Fitted clothing inherits body weights. Interpolate
weights at cuts and added vertices, then renormalize. Avoid copying unrelated
local rotations directly between differently oriented bones.

For animation import, use `universal.py` and `retarget.py`:

- Read the actual source hierarchy and its explicit `A_TPose` reference.
- Convert glTF Y-up into Blender Z-up consistently. glTF quaternion values are
  XYZW; Blender uses WXYZ. Normalize and preserve quaternion sign continuity.
- Evaluate source world rotations, remove the source reference rotation, and
  apply the target reference orientation. Convert the result through the
  target parent's and bone's rest transforms into local pose rotation.
- Preserve target limb lengths. Scale hips displacement using reference
  height rather than translating every limb from the source skeleton.
- Sample at the project's 30 fps, keep shortest-arc interpolation, and export
  the intended action slots. Test exported animation, not just Blender playback.
- Preserve clip rules: loops wrap; jump/sit/spell transitions name their next
  clip; death and aiming clips can hold their final pose.

The current source is Quaternius **Universal Animation Library Standard** at
`animations/quaternius/universal_standard/Unreal-Godot/UAL1_Standard.glb`
in the art repository. The installed Standard file contains **43 clips**,
including T-pose. Count clips in the actual file rather than assuming a
120-plus marketing count refers to this download. Its checked-in license is
CC0. The current source checks deliberately reject legacy animation imports.
An older optimization report checked 96 mixed clips; that is historical,
not the current animation count.

### Diagnose the floating-hand symptom correctly

The left hand originally looked detached or wobbly because the authored
animation held a shield. We found the same motion on the original character;
clothing and a shield made the pose easier to understand. It was not solved by
arbitrary skin weights or by mirroring the right wrist.

Separate three possibilities: wrong weights, wrong retargeting, or intentional
source motion. Show the real source skeleton and clip, the target skeleton,
and the actual weight overlay at the same time and frame. A second retargeted
copy is not an independent source comparison. Track parent-child distances,
wrist attachment boundaries, and local versus world axes. Test idle, walking,
attacks, and any shield stance before concluding a rig is broken. Use suitable
free-hand clips or explicitly designed equipment animation layers when needed;
do not patch every animation based on one unfamiliar pose.

For held props, use a real hand socket, local grip pivot, and consistent axes.
A rigid weapon follows its hand bone, with weight 1, rather than deforming
through forearm weights. Verify the grip through the attack, not only at rest.
Use the viewer's zero-based frame slider and counter to reproduce a reported
pose. Review front, side and top at the same frame, plus neighboring frames,
wind-up and follow-through. The creep correction was `Sword_Attack` frame 19
at 30 fps (`19 / 30` seconds); that is a regression example, not the strike
frame for every clip. Apply a fixed rotation about the grip in the runtime's
documented axes, not an animation-specific rotation or a moved grip pivot.

## Face textures and expression sheets

Eyes and mouths are small transparent textures on separate curved meshes,
skinned to the head. Keep each design in its own PNG and GLB with UVs relative
to that image. Ray-cast a grid onto the actual head and offset it slightly to
avoid z-fighting. Do not use one flat floating plane for a curved face. Restrict
the projection to useful artwork bounds: a ray can miss at transparent canvas
corners even when the visible X marks fit correctly.

Our eye style has white sclera with **no enclosing outline**. A short dark
upper streak can express kindness or a heavy lid; it is not a border around
the sides and bottom. Variety comes from silhouettes, expression, iris values,
and highlights, not only recoloring the same shape. Some eyes benefit from
three to five chunky grayscale regions or a subtle gradient; others should
stay simple. Avoid realistic iris fibers and excessive detail at game size.

For gnomes, one shared kind eye pair was enough. It needed a small curved black
top streak, white sclera, a restrained gray iris gradient, a black pupil, and a
small highlight. Reuse existing brows. More elaborate irises were less kind
and less readable. We also lowered and widened the early eyes to match the
reference; compare their position relative to the nose and head width instead
of judging the texture in isolation.

Separate artwork from tint data:

- A same-size iris mask controls only tintable pixels. White sclera, white
  highlights, black lid accents, eyepatches, and other fixed details stay intact.
- The mask's red channel is coverage, with zero outside tintable regions.
  The runtime multiplies masked grayscale values by the selected RGB color.
  Test saturated colors and black. Preserve alpha exactly.
- Decide which pupil convention the design uses. The broad generated sheet
  tints its gray pupil/iris complex; the kind gnome pair protects its black
  center and tints only the iris. Do not turn every dark pixel into a tint mask.
- Eyes remain unlit in both toon and normal rendering. Keep mouth art unlit as
  authored. Separate white brow decals tint with hair or an explicit brow color.
- Use an unlit alpha-cutout material and also list facial nodes in the runtime
  unlit pass. Do not multiply the entire eye texture by skin or hair color.

Generate 4x4 mouth or eyebrow sheets when a range is requested. Mouth shapes
can share the same projection system: neutral, smiles, anger, open mouths,
fangs, or stitches. Keep teeth count and silhouette deliberate; fix a bad cell
without redrawing approved neighbors. White eyebrows on pink make recolorable
cutouts. Monster eyes can include cat, reptile, undead, or an eyepatch, but omit
bug eyes from a humanoid-only set when their silhouette needs a different body.

For a reviewable pink sheet, use flat bright magenta and generous gutters.
Use imagegen for generation and semantic corrections/background extraction;
request genuine alpha, not a checkerboard painting. Preserve the source and
prompt. Inspect alpha, remove fringe, and crop/resize deterministically for
runtime export. Do not assume generated sheet cells have exact dimensions or
that every black region is an iris. Connected-component cutters assume a
particular component count; adjust them for disconnected accents rather than
silently discarding valid art.

The shared `Eyes: Dead X` expression is a selectable option. It has no iris
mask and no default preset replacement. A preview launched with `EYES="Dead X"`
does not change library defaults or add automatic game death behavior.

## Hair, beards, hats, and shared gnome features

Use coherent front/back concept pairs and build real volume, not a front-view
silhouette with no back. The hair and beard scripts construct chunky locks
and masses with a few readable value changes. Render isolated styles and the
same styles on the actual head. Share hair color across scalp hair and beard;
retain relative light/dark shades instead of flattening every primitive.

The nine gnomes demonstrated economical reuse: one kind eye pair, bulb nose,
recessed larger ears, pointed layered beard and curled moustache, and existing
brows. Vary colors and outfits before inventing nine nearly identical meshes.
Review moustache clearance, chin point, cheek coverage, and downward hand curl.

Model a few hat constructions, then recolor and decorate them. Pointed,
folded, wide-brim, and mushroom shapes covered the main variants; leaf and
feather versions reuse the crowns. Hats hide selected scalp hair and restore
it on removal. Tint crown fabric independently of leaves, feathers, lining,
or other fixed materials. Mushroom spots need pure white unlit material;
smooth cap normals cannot by themselves stop the white from receiving toon
bands. Smooth caps and fabric while retaining intentional creases and rims.

Fit headgear in three dimensions. A rounded back does not fix an incorrect
front opening, and a correct front outline can still float far from the face.
Preserve the concept's brow height, corners, eye clearance and inward cheek
steps while fitting depth to the actual head. Hoods need draping lower cloth;
helmet guards need deliberate armor edges. Use hood-compatible braid pieces
instead of inflating a hood around a full hairstyle. Detailed examples and
the Death Knight fitting method are in the Gota reference above.

## Clothing from the real body

Use `clothes.py` for fitted shells and `garments.py` for layered details.
Duplicate appropriate body surface regions, clip at sleeves/neck/hem/waist,
offset outward, and preserve interpolated skinning. Extend silhouettes for
shirts and coats with nearby body weights. Model thin opening rims, cuffs,
lapels, pockets, buttons, and buckles only where they read at game size.
These garments use ordinary skeletal skinning, not cloth simulation.

Keep torso, jacket, trousers/shorts, boots, suspenders, and **belt** independent.
A belt is not part of the body or trousers and should not remain baked into
older tunics. The migration retained the two tunics' original IDs even after
removing "Belted" from their labels. Changing a displayed name must not create
duplicate assets or invalidate saved selections.

Use `hides` metadata for covered geometry. Boots hide bare feet and only the
lower trouser sections beneath their shafts. Restore those sections when boots
are removed. Keep trousers visible behind V-shaped boot openings. Hat/boot
occlusion should not erase a player's saved hair or trouser choice. Numerical
nearest-surface clearance is useful but can misread overlapping body regions
in a crouch; visual animation checks are still necessary.

Reuse fitted garments when adding detail: the fuller gray and blue long coats
share geometry; the fancier wizard boots add shaped cuffs and piping. Separate
tintable fabric/leather from fixed metal, soles, and trim via `clothShades`.
Preset RGB values select colors without duplicating mesh files.

## Runtime contract and selective packing

The manifest maps a category to a folder; the loader discovers JSON sidecars
without a compiled style count. Each sidecar names unique mesh nodes, stable
part IDs, GLB files, and optional texture, masks, tint regions, and hides.
Paths are relative to the library. Materials must reference their PNGs too;
a sidecar texture path alone does not make the GLB render correctly.

Ship each geometry type separately so a game can choose the subset it needs.
Build eye, mouth, and brow atlases only at pack time from selected images.
Keep padding, exact alpha, mask alignment, and UV remapping correct. Include
required transition clips and the common rig; exclude Blender files, source
sheets, tools, and unselected parts. `pack.py` and `test_packs.py` implement this
contract, including tests of exact atlas pixels and independent minimal packs.

Shared parts use `both`; `good` and `evil` filter their random buttons.
`gnome` is reserved for gnome-specific features, particularly caps, so they do
not leak into good/evil rolls. Shared gnome clothing remains available to good
characters. Manual selection permits every part. Preserve the current gnome
random preference for its family features; tagging a shared part does not mean
every specialized random roll must use it.

Randomization also chooses skin, hair, iris, and equipment palette colors.
Roll beard presence separately at 50 percent, not as one None entry against
many styles. Offer custom RGB skin while protecting facial art and material
details. Keep natural hair colors before unusual colors in the preset palette.

## Visual review and useful judges

Render the exported model in Chargen, including its normal toon shading,
unlit eyes, tints, equipment visibility, and animation. Blender studio renders
alone do not demonstrate game parity. Keep polygon edges as an overlay so the
surface and topology can be inspected together, and use weight/bone overlays
when attachment is in doubt.

Use hidden windows for automated review captures. The current `render_gota`
uses `visible = false` with an offscreen framebuffer; on macOS a hidden
window's default buffer can produce black screenshots. The hidden renderer
must resolve its multisample color buffer before reading pixels. Check the
actual executable and renderer source: old binaries and other render tools
may still open windows. See the hidden-capture commands in the tool catalog.

When the user requests a judge, use an independent agent with a bounded part
or batch to review. Supply the reference and actual renders at matching views;
include the user's latest corrections to that reference, but do not tell it
that the result is already good. Ask for specific silhouette,
fit, shading, attachment, clipping, and budget defects. Give parallel builders
separate object prefixes, files, and output folders; one integration owner
updates shared manifests and the master. Use judges for meaningful visual
work, not as a mandatory ceremony for every tiny metadata edit.

Keep before/after front, side, back, walking, and crouching captures with the
same camera, pose time, lighting, and color. Review toon and smooth lighting
when normals matter, plus closeups of wrists, cuffs, noses, and beards. Iterate
on reported defects and record remaining limitations. A passing sampled-pose
review is not proof that every frame of every animation is collision-free.

In the editor, preset lists stay open after choosing an item. Changing outfits
or ordinary lineups preserves the current clip, time, speed, and pause state.
T-pose is an explicit control; the dedicated creep sword-pose review is an
intentional special pose. Keep styling and animation choices independent.

## Reduce geometry without losing the model

Measure **rendered triangles**, exported vertices, and material primitives for
each assembled preset after applying hides. A Blender quad is not one runtime
triangle. Count covered surfaces that are still drawn. Start with the biggest
parts and actual frame cost, not just the body or a total `.blend` face count.

Our nine-gnome target was fewer than 15,000 triangles each. The approved pass
reduced the group from 237,784 to 126,301 triangles, about 46.9 percent.
Individual results were 12,859 to 14,949. These are dated results from that
pass, not promises for new presets or random combinations; rerun the counter.

The successful order was:

1. Remove genuinely hidden duplicate shell lining, preserving outer cloth
   and opening rims. Do not indiscriminately delete all inward-facing faces.
2. Keep outer trouser vertices/weights unchanged where removing lining is
   sufficient. Protect boot shafts and the coat's belt-clearance region.
3. Lock wrist seams, open boundaries, sharp edges, UV/material boundaries,
   and nearby support rows before targeted decimation. Hands reached 540
   triangles each while retaining the wrist boundary and silhouette.
4. Reduce beard volume conservatively and inspect its point and layered locks.
   Dissolve redundant face-decal grid edges while preserving UVs and normals.
5. Transfer corner normals from the matching source surface and material.
   Nearest geometry alone can pick the opposite side of a hem or rim and
   introduce dark artifacts. Preserve intentional creases.
6. Normalize weights again and compare rig matrices and animation keys to the
   baseline. Simplify copies during export, restoring the full authoring mesh
   afterward. `optimizations.py` uses this approach.

Do not treat the stored decimation ratios or hardcoded protected Z ranges as
universal settings. They encode the approved gnome proportions. Remodeled
garments need new protection regions and visual review. Compare animation keys
only between exports from the same supported clip set; a library migration
is not a geometry-only before/after comparison.

## Finish with concrete evidence

Run checks suited to the change: topology and weights for geometry, source
motion comparisons for retargeting, alpha/tint/atlas checks for face sprites,
selection and hiding checks for modular parts, and per-preset triangle counts
for optimization. `nim check` precedes the relevant Nim test run. Use fresh
temporary output folders for comparisons; do not rerun broad destructive
builders just to prove the documentation or helpers work.

Deliver the edited Blender/GLB/PNG/JSON paths, actual render previews, budgets,
checks, judge findings when used, and any remaining visual problems. Keep
defaults stable unless asked to change them. Commit and push only when
requested, respecting the project's branch preference and unrelated work.
