# Gota character authoring

Approved visual source: `approved_roster.png` in this directory. All ten are
human, including the pale white Lich and dark-skinned Death Knight. Preserve
the current low-poly, solid-color style, clothing, and no-props constraint.

Each character agent owns only its slug-prefixed source, exports, and reviews.
Do not overwrite shared source/character.blend, manifests, palettes, existing
parts, or another hero's files. The root agent integrates manifests and viewer.

1. Read the imagegen skill and inspect the approved roster. Use imagegen to
   create an isolated clothing reference sheet for your hero: five rows
   (boots, legs, belt, body, hat) and two columns (front, back). Each pair
   shows the same separate item, without a mannequin, weapons, or other props.
   Eye coverings count as hats. Keep capes attached to the body item. Existing
   hair/beards are separate reusable parts. Save the generated sheet and exact
   prompt in `source/gota/<slug>/`.
2. Spawn your own independent judge agent to assess fidelity against the
   approved roster. Later have that same judge review actual rendered models
   against both the roster and clothing sheet, using side-by-side comparisons.
   Ask it for specific defects, fix material issues, and preserve its verdict.
3. Inspect the current fitted clothing and rig. Build actual skinned GLBs for
   five independently selectable slots: Foot, Leg, Belt, Chest, Headgear.
   Reuse existing fitted boots, legs, face, hair, beard, etc. where appropriate.
   New objects/part IDs must use the prefix `gota_<slug>_` and unique nodes.
   All clothing uses solid materials without image textures. Existing facial
   decals are explicitly allowed by the user's reuse instruction.
4. Root will provide `source/scripts/gota_common.py` for isolated exports,
   fitting utilities and rendering. While it is being prepared, generate the
   sheet and inspect geometry. Own `source/scripts/gota_<slug>.py` with a
   `build(ctx)` entry point returning your part descriptors and preset.
   Coordinate exact helper interface with root rather than inventing one.
5. Export to normal runtime category folders with only hero-prefixed names.
   Save a hero-local authoring .blend, assembled front/back model render,
   isolated-item render, side-by-side comparisons and judgment in the hero's
   folder. Keep build logs and intermediate files under polyworld/tmp/chargen/gota.
6. Verify actual visible assembled triangles are below 20,000, all new geometry
   has finite positions and normalized rig weights, and parts use the shared
   skeleton and retain animation. Do not call an image or a stub a model.
7. Report exact files, reused part names, triangle count, checks, judge findings
   and remaining problems. Do not commit or edit shared manifests.

Library: `/Users/me/p/polyworld_art/characters/chargen`.
Nim viewer: `/Users/me/p/polyworld/experiments/chargen/chargen.nim`.
Blender executable: `/Applications/Blender.app/Contents/MacOS/Blender`.
Root's original instructions apply. User changes are already present, so never
reset or globally rebuild the existing library.
