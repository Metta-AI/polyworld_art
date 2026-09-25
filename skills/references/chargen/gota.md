# Gota heroes, gods, headgear, and equipment

Read this for Gota work on the existing CharGen rig. It records the ten-hero
roster, two creeps, Zeus and Hades, and the subsequent fitting corrections.
Use the current preset and source files for exact colors, names and counts.
These are project decisions, not a template for unrelated character styles.

## References and modular builds

Start from the approved roster and the user's corrections. The original
5x2 hero sheet establishes consistent proportions; individual front/back
clothing sheets establish the shapes that the roster obscures. Preserve the
exact prompt and approved image under `source/gota/<slug>/`. Keep clothing,
hair, beard and equipment references separate from the existing rig and eyes.
For Zeus and Hades, per-item references made crowns, capes, medallions, skirts
and greaves easier to model and review than a single crowded full-body image.
Use [the prompt patterns](prompts.md) when new reference art is needed.

Choose the narrowest builder. `gota_common.py -- <slug>` is invoked through
Blender with `-- <slug>` after the script path. It loads the clean shared
master, creates uniquely prefixed modules, exports part GLBs/JSON, and saves
an isolated `hero.blend`. `finalize_gota.py` sets the selected outfit and skin
for opening that authoring file. `build_gota.py --hero` also rebuilds the
shared Gota body; it is broader than a helmet-only change. See
[the commands](tools.md) before running a builder.

When parallel workers are requested, give them separate hero/part prefixes,
source files and output folders. One integration owner updates shared
manifests and palettes. Avoid concurrent rebuilds of the master or a common
equipment file. A worker's final screenshot does not replace integration
and rendering of its exported asset in the actual preset.

## Presets are complete selections

Use explicit choices for every optional slot, including `None`, so changing
from a god to a creep does not retain an old beard, cape or weapon. Reuse
existing eye designs and make requested expression choices explicit; Ranger
uses `12 Sleepy`. The approved Lich is a pale human without scalp hair, and
Death Knight shows a dark human face under the helmet rather than glowing
eyes. Do not bring skeletal or glowing-eye details back from an older image.

Keep generated parts independently selectable and use `hides` for covered
geometry. Update source and runtime inventory together through the existing
registration path when adding or changing entries. `register_gota.py` merges
heroes, creeps and gods while preserving other preset groups. Existing god
presets belong to `Gota Gods`; do not assume the ten-hero lineup includes them.
Check transitions between presets in the viewer as well as direct loading.

For screenshot-based presets, preserve visible choices and exact numeric RGB
values. Do not infer an unseen color from a slider's position. The blue creep
reuses the Vanguard sword and the purple creep reuses the Death Knight sword;
they do not require duplicate meshes.

## Hoods: fitted skull, distinctive opening, loose lower cloth

The Ranger hood was the approved reference for a rounded, close-fitting back.
Match that fit without giving every hood the same opening. Crossbowman has a
pointed brown opening, Lich an ivory-edged V beneath the crystal crown, and
Warlock a stepped gold opening between the horns. The early generic rounded
arches exposed too much forehead and lost these identities.

Define the opening's key corners and brow height explicitly. Fit the upper
shell to the actual head, but let the lower edges flare and drape instead of
wrapping beneath the chin like a tight head covering. Do not let an automatic
nearest-surface pass pull every loose cloth point onto the jaw. Inspect front,
side and back on the real head, not only the isolated hollow hood.

Use a hood-compatible hair piece with the visible braids and minimal hidden
scalp volume. Small overlap beneath a hood is preferable to a box-shaped hood
inflated to enclose the full hairstyle. Keep the user's normal hair selection
available when the hood is removed. The Lich does not need hair beneath hers.

## Helmets: separate the front outline from depth fitting

The Death Knight correction required all of the following together:

- Full coverage over the sides and back, despite the concept's open rear.
- A low V-shaped brow covering the eyebrows while leaving the eyes readable.
- A wider opening beside the eyes, with an angular step inward by the mouth.
- Cheek guards extending below the jaw, sitting close to the face.

A straight-sided opening misses the cheek shape. Moving the whole front rim
far forward makes the outline visible but creates a floating visor. Author
the front X/Z outline first, then fit its depth to the actual head surface.
The existing Blender recipe faces toward negative Y; exported glTF is Y-up.
Do not mix those conventions when measuring clearance or applying offsets.

`gota_death_knight.py` ray-casts onto the head to choose the front depth,
uses a nearby valid sample where a ray misses at a lower corner, and retains
the authored opening profile. A small clearance, a solid rim and fitted
subdivision provide volume. The gem follows the brow's slope. Treat its
clearance constants and fallback coordinates as specific to this head, not
universal values. Check side and oblique views after every depth adjustment.

Coverage checks must distinguish exposed face/eye openings from the skull
that should be enclosed. Report which head samples and directions were
tested. Head-bound geometry follows the head bone rigidly; preserve the rig
and facial art while fixing the shell. See the actual comparison and checks
in `source/gota/death_knight/helmet/`.

## Curves, normals, and accidental cloth triangles

Keep broad forms simple and untextured, but allocate vertices to their visible
curvature. The first equipment pass was too sparse: curved guards, bows and
axe edges became flat lines. Correct the mesh silhouette before adjusting
normals. Round cuffs, medallions and skull caps can use smooth normals while
blade edges, crystal facets and armor creases stay deliberate.

The Zeus tunic developed triangular patches between the cloth and medallions.
The cause was unnecessary open decorative fold fans, with reversed winding
on mirrored pieces. Removing those four patches fixed the defect; flipping
all normals or using double-sided materials would not fix their shape. When
similar slivers appear, inspect the isolated part and wireframe to identify
the actual faces. Preserve the fitted shell, useful lining and opening rims.

## Equipment and attack sockets

Only request distinct reference views where they carry information. A sword,
bow, staff, knife or axe can use one view when its two faces are equivalent.
Shields need the decorated front and grip/strap back. Crossbows need a top
view showing the string and a bottom view without it. Include the quiver or
bolt box separately. Build one approved dagger or axe design before reusing
it for a pair, with correct handed placement and mirrored winding if needed.

Rigid weapons use the selected hand socket; shields may use a forearm socket
and quivers the back. Preserve the grip point through animation. Runtime
`attachmentPivot` and `attachmentRotation` use exported glTF bind-space axes
and XYZ angles in degrees; the current transform is `T(p) Rz Ry Rx T(-p)`.
Do not paste Blender Euler angles into that contract without conversion.

For the creeps, frame 19 of `Sword_Attack` exposed the wrong direction most
clearly. Freeze both presets at `19 / 30` seconds and inspect front, side and
top, with a hand closeup. At that frame the blade should continue the user's
indicated elbow-to-grip strike direction. Check frames 18 and 20, wind-up and
follow-through before accepting a fixed offset. Do not steer the sword toward
a world-space enemy every frame or alter the source animation to hide a bad
socket. Saved rotation numbers apply to these exported swords, not every prop.

## Review and budgets

For this Gota workflow, the verifiers enforce fewer than 20,000 rendered
character triangles and fewer than 5,000 equipment triangles per hero set.
Report character, equipment and combined counts separately after hides.
Honor a stricter user limit when given, and inspect the gods' dedicated
verifier rather than assuming every group uses the same accounting.

Supply the approved concept and actual exported front/side/back images in
one labeled comparison. For sockets use front/side/top. Keep images unretouched;
cropping and layout are fine. Use hidden runtime captures and include toon
and smooth-lighting closeups when evaluating normals. A whole-character judge
pass missed the Zeus fold defect; inspect suspect junctions at useful scale.
When a judge is requested, iterate on concrete defects and capture the changed
model again. A previous pass is not evidence for a later revision.

Validate finite, nondegenerate geometry, appropriate open/closed boundaries,
normal direction, normalized weights, canonical bind data and current preset
selection. Use the relevant `verify_gota*.py`, provenance checks and CharGen
tests from the tool catalog. Keep reports and authoring files in sync with the
final export; do not call an older binary or an old screenshot the new result.
