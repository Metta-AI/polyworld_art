---
name: modeling-buildings
description: Model and review Polyworld buildings and village props in Blender with mirrored parts, shared trim atlases, terrain joins, construction stages, and GLB exports. Use for building modeling, modular props, atlas variants, relative scale, export validation, or faction comparison renders.
---

# Modeling Polyworld buildings

Use this with [the general Blender guide](polyworld_blender.md). Start from
the user's approved concept and texture references. This guide records the
village well and hobbit house process alongside the LVD kit. Adapt each project's
names, counts, dimensions, and themes rather than treating them as defaults.
The 512-pixel atlas and faction contract below belong to LVD, not every building.
Later user corrections take precedence over an earlier concept image.

Keep editable sources with live mirrors, arrays, and collection instances.
Evaluate copies for export. Use low-poly silhouettes and hand-painted albedo
detail, without adding normal, bump, or specular maps by default. Model connected
shells and deliberate openings rather than piles of overlapping closed boxes.

Keep scripts in [scripts/modeling_buildings](scripts/modeling_buildings/).
Put generated images, blends, logs, intermediate exports, and judge evidence in
`tmp/<task>/`, not `docs/` or the skill folder. Publish approved assets in the
logical asset pack, following [the art contribution process](../CONTRIBUTING.md).

## Village houses and props

These lessons come from the well, shallow hobbit facade, full grassy house,
planters, and chimney. Their dimensions and counts are examples, not kit-wide
requirements.

### References and approved scope

A generated view labeled "front" or "top" may still have perspective or camera
tilt. For a full building, align front, true top, and side elevations on one
consistent sheet; use a three-quarter view to explain depth. In Blender, verify
with axis-aligned orthographic cameras. A tilted orthographic camera is useful
for presentation but is not a top plan or front elevation. Keep scale consistent
between technical views. A shallow facade can use an approved front and oblique
reference directly when the user has said additional views are unnecessary.

When extending an approved facade into a full building, preserve its proportions,
openings, materials, and details. Add the surrounding mass behind its existing
join. For the hobbit house, the approved mass was a broad circular mound clipped
at the facade, not an egg-shaped footprint. Its yard fence joined the side posts,
with an entrance gap and a short stone approach; there was no perimeter path.
Check these relationships in a true top view before adding decorative details.

Keep planters and the chimney independent when they will vary between houses.
Use a common parent for the house, yard, and fence, with separate prop pivots.
The chimney's placement origin represented the roof surface, with a short lower
extension to bury in the hill. A facade-only commission needs exposed edge
returns and a terrain join, not an unrequested back wall or interior.

### Spend geometry on shape and depth

Paint repeated shingles, masonry joints, boards, and small hardware detail into
the trim. The well used one texture patch per roof slope and a few quads to shape
its flared eaves, rather than separate shingle meshes. Add geometry where it
changes the silhouette, creates an opening, or gives a visible ledge thickness.

Thick door rims and shallow recessed doors and windows give a facade depth
without a full interior. Cut real openings in the wall and face the reveal
normals into the opening. Measure recess depth from the front of the surround,
not the world origin. When reducing a recess, move the door or pane and its
hardware together, then shorten the reveal. Check from oblique views that the
wall does not cover the inset surface.

Match the entrance stones to the lowest inside edge of the door surround. Raising
the threshold and slightly lowering the door removed the unwanted wooden step.
Inspect the walking surface from the side; matching object origins is not enough.
Slope side-post tops to fit beneath the crest and tuck the join slightly into it.
Use wood UVs on wooden post bases, including the appropriate end grain.

Small support wedges can use two triangular ends and one sloping quad: four
triangles per support. Omit the top and rear only when the wall and sill or roof
actually conceal them. This produced two supports per sill and four beneath the
house crest without closed boxes or extra materials.

### Continuous masonry and reusable color

Inspect stone seams before adding polygons. Repeating or mirroring an irregular
rubble patch across adjacent wall strips produced obvious vertical seams. The
facade fix was one continuous painted masonry panel across the front and side
returns. Mirror the geometry while mapping each half to its corresponding part
of the panel; do not accidentally reflect the same stones at the center seam.

Regenerate only the needed panel when UV changes cannot repair the artwork.
The revised hobbit atlas appended this panel below the existing trim, preserving
the original pixels. Changing atlas dimensions still changes normalized UVs:
recompute region coordinates and remap existing parts to retain their materials.
Do not carry the old cell formula into a newly extended atlas.

Make recolorable door artwork white-gray and give the door its own material
sharing the atlas. Apply the stain as a multiply tint, leaving frames and hardware
on their original material. An extra material does not imply an extra texture.
The Blender glTF exporter did not preserve this project's MixRGB stain; the
full-house exporter explicitly set the door's `baseColorFactor`. Inspect that
factor and the reimported appearance instead of assuming the viewport tint
survived. Keep a neutral export neutral when that is the chosen deliverable.

Count distinct texture images per exported asset, separately from material slots
and scene-wide images. The house used a trim plus a grass tile; the separate
chimney reused the well's gray-block atlas. Reusing an existing atlas avoids new
artwork but still gives a scene another image dependency if it was not already
used there.

### Ground covers, grass, and soil

A hollow well placed on grass needs an opaque bottom cover to hide the terrain.
Place it slightly above ground to avoid z-fighting and extend it into the inner
wall to close gaps. The well used a dark blue-black atlas pixel for the shadow,
with every cover UV at that pixel's center. No water detail or extra material
was needed. Permit intentionally collapsed UVs for such flat-color faces while
still rejecting degenerate geometry. Select a stable dark region for filtering.

Use a separate repeating grass texture for a large mound instead of stretching
a small trim cell over it. Check texel scale at the crown, sides, and facade join.
A disk-like unwrap avoided pole pinching; the front shoulder needed UV depth
based on its surface height to avoid streaking. A good top view alone does not
establish that side UVs are usable.

Add slight mound irregularity by displacing existing vertices with broad, low
frequency variation. Fade displacement to zero at ground edges and facade joins,
and preserve intended symmetry. The approved house needed only about five
centimeters of vertical variation, without subdivision. Reposition rooted tufts
to the changed surface so they neither float nor disappear into it.

The rectangular planter's dirt used six connected quads with gentle height
variation and continuous soil UVs. Keep the boundary under the rim, fill the
opening, and let plant stems penetrate the soil. This gives depth without a
separate texture or many disconnected soil pieces.

### Tapered chimneys and targeted revisions

For the chimney, use a broad bottom band, a narrowing middle, and a projecting
top band around a real hollow opening. Build a connected shell from square rings,
with small corner chamfers where they improve the silhouette. Match rectangular
gray blockwork using the existing well trim rather than the facade's irregular
rubble. Align course heights and corner UVs across the taper, stagger courses
within the atlas region, and keep top-rim mortar lines straight. Inspect the
inside from above. Avoid bright trim edges that read as thin decorative molding
when the reference calls for chunky stone. This version used 270 triangles.

For a local correction, update the named mesh or parameter in the current blend
and preserve the other approved parts. Save a recoverable version first. Also
update the rebuild source so the correction survives regeneration; do not rerun
an older full builder over later user edits. Apply deformations from a stored
baseline or record their state so rerunning an update does not compound them.

Review isolated prop views as well as the assembled house. Other props obscured
the first chimney check, so hide them for close-ups and restore visibility before
saving the authoring scene. Keep preview-only camera changes out of that save.
Judge front, side or rear, top, and oblique views for silhouette, UV joins,
recesses, terrain contact, and openings. Supplement this with targeted opening
rays and source mesh/UV comparisons when a facade must remain unchanged.

Reimport updated exports in a fresh process and report evaluated triangle counts
per asset, not just editable face counts. Inspect Blender's log as well as its
exit status: a background run can report a Python error without a failing exit
code. Update the manifest and give the user the actual blend and export paths.
If showing the result in an already-open Blender session, preserve unsaved work
before reloading and verify that the new geometry is visible.

## Approved LVD kit

The 3×3 stage uses this row-major order:

| Role | Geometry and reuse |
| --- | --- |
| Town Hall | Mirrored central structure and three instances of a separately mirrored wing. Rotate the two side wings ±90° so their roof ridges extend into the center. |
| Farm | Square field only. Mirror a fence module, repeat it four times at 90°. Instance a separate pumpkin model in a 4×4 arrangement with varied scales and leaves. |
| Barracks | Mirrored structure; smaller than the original version after door calibration. |
| Lumber Mill | Mirrored structure and reusable timber parts. |
| Tower | Sixfold radial symmetry, 60° controller, windowed upper structure. No crystal. |
| Stables / Kennels | Mirrored structure and repeated stalls/details. |
| Church / Temple | Mirrored structure with distinct silhouette. |
| Blacksmith | Mirrored structure and reusable workshop parts. |
| Gold Mine | Neutral timber entrance, rails, cart, and raw gold. No surrounding rocks and no faction markings. The map supplies rocks. |

Use the same mesh datablock or collection for repeated parts. Preserve distinct
pumpkin placements even when they share geometry. The existing export removes
four duplicate farm corner posts caused by adjoining fence modules. That count
is specific to this kit, not a general deduplication rule.

## Shared trim atlas

The final atlas is **512×512**, sRGB albedo, with sixteen **128×128** cells.
All faction variants must obey the same UV contract. Rows below start at the
image's top left; there are no labels, gutters, or drawn grid lines.

| Column 1 | Column 2 | Column 3 | Column 4 |
| --- | --- | --- | --- |
| `stone` | `plaster` | `window` | `gray` |
| `roof` | `wood` | `gold` | `door` |
| `pumpkin` | `banner` | `leaf` | `doubleDoor` |
| `bark` | `soil` | `archWindow` | `archDoor` |

- Keep four horizontal courses in `roof`: the model samples quarter-height
  strips. Wood and bark grain run vertically; beam UVs sample the central strip
  approximately `u=.29..62, v=.035..965`.
- `gold` is raw ore only. Replace decorative gold panels and crystals with useful
  window types. Single, double, and arched doors retain legible ironwork.
- Keep pumpkins orange, leaves naturally green, and soil brown. The early request
  for green meant farm vegetation; it did not replace the original blue roof.
  The later eight-faction request deliberately varies roof and cloth colors.
- Use one cloth cell and a small centered emblem. Keep its upper-left region
  blank: small pennants sample `u=.04..30, v=.85..98` in tile-local coordinates.
- Pad UVs within each cell. The existing helper uses tile-local padding `.008`,
  roughly one final pixel. For zero-based `(column, row)` and local `(u, v)`:
  `U=(column+.008+u*.984)/4`, `V=(3-row+.008+v*.984)/4`.
  Repeat a material within its own cell, never by wrapping across the full atlas.

Use the imagegen skill for generating or editing texture artwork. Supply the
approved atlas as a reference and preserve cell identity, order, orientation,
and roof courses. Request a flat material sheet, without buildings or perspective.
Inspect every generated result; a prompt requesting a regular grid does not
guarantee pixel-aligned boundaries. Focus emblem edits on the cloth cell and
check that the other fifteen cells remain consistent.

Preserve high-resolution masters. Normalize **each cell separately** before
assembling the 512×512 runtime atlas. Simply shrinking the full image caused
neighboring materials to bleed into UV regions: one original 1254-pixel sheet's
third row ended near 934 rather than the ideal 940.5.

[layout.example.json](scripts/modeling_buildings/faction_trims/layout.example.json)
records the measured old source boundaries and four-pixel interior crop. Measure
new artwork before using it. The packer currently accepts one shared layout for
all eight sources; normalize differing source layouts first or extend the packer
with per-source layouts. Do not blindly apply the old 1254-pixel recipe to new
generations, and do not upscale the 512-pixel runtime image as a new master.

## Eight faction variants

Use these game enum names, colors, and distinct flag emblems. The themes change
material treatment as well as hue. Roof shingles and cloth carry the faction
color; crops, wood, soil, and raw gold remain recognizable natural materials.

| Game faction | Color | Architectural theme | Flag symbol |
| --- | --- | --- | --- |
| `PeterRiver` | `#3498DB` | Good; original cream stone and wood, light-blue roof | Sword |
| `Amethyst` | `#9B59B6` | Evil; black rock and arches | Bat |
| `Alizarin` | `#E74C3C` | Orc; rough wood, gray rock, square openings | Crossed axes |
| `Emerald` | `#2ECC71` | Forest; leafy wood, overgrown white stone, curved arches | Leaf |
| `Carrot` | `#E67E22` | Desert; sand, rammed earth, square openings | Sun |
| `WetAsphalt` | `#34495E` | Dragon; black stone and Gothic treatment | Dragon |
| `Turquoise` | `#1ABC9C` | Greek; white stone and arches | Laurel wreath |
| `SunFlower` | `#F1C40F` | Egyptian crypt; limestone, sandstone, arches | Scarab |

Use dark ink where a pale emblem lacks contrast, especially the yellow scarab.
Texture swaps cannot change the modeled silhouette or actual opening shape.
Keep the mine on `textures/buildings-atlas.png` for every faction. Do not create
eight mesh copies just to change material images. Producing faction textures
does not by itself wire material selection into the game.

## Relative scale and construction

Calibrate doors and human clearance, not equal overall bounding boxes. The kit's
nominal door panel reference is 1.50 units; arched surrounds may make the visible
leaf slightly smaller. The tower uses a 1.40 visual scale factor for headroom.

| Model | Recorded factor from the unscaled builder |
| --- | --- |
| Town Hall | `1.50 / 1.13` |
| Farm | `1.00` |
| Barracks | `1.50 / 1.65` |
| Lumber Mill | `1.50 / 1.57` |
| Tower | `1.40` |
| Stables / Kennels | `1.50 / 1.425` |
| Church / Temple | `1.50 / 1.49` |
| Blacksmith | `1.25` |
| Gold Mine | `1.00` |

Scale placements, not shared mesh data. Apply the same factor and origin to
finished, foundation, and wall stages. Store applied factors and use
`target/current` on subsequent runs; do not scale foundations again when they
are already instanced inside wall stages. The existing scaler depends on its
factor tags and unparented source-object layout.

For source placements in inactive scenes, use `matrix_basis`, not stale
`matrix_world`. Reading inactive-scene world matrices previously returned
identity transforms and collapsed parts. Activate the authoring scene and
update its view layer before evaluating bounds or collection instances.

Create two construction models for each of the eight non-mine buildings:

1. Foundation only, with the completed building's footprint and pivot.
2. Foundation plus genuinely hollow walls, with no roof or ceiling caps.

Remove crops, flags, loose props, machinery, and nonstructural details. The farm
becomes a bare bed, then an empty fenced bed. Merely hiding roofs leaves closed
box tops underneath: build wall shells with thickness and real openings. Inspect
them from above and probe representative interior positions with downward rays.
The bundled verifier's seven probe locations are a useful regression check,
not exhaustive proof of every opening.

## Running the preserved scripts

Use [run.py](scripts/modeling_buildings/run.py) to stage a whole script group into
an explicit working directory. The group must stay together: construction
extracts helpers from `build_scene.py`; its exporter extracts helpers from
`export_glbs.py`; its verifier reads functions from `verify_glbs.py`. Keep the
existing extraction markers intact when editing these archived scripts.

Requirements: Python 3, Blender with its glTF importer/exporter, and ImageMagick
`magick` for atlas packaging and contact sheets. The recorded Blender version was
5.2.2 LTS. Sheet scripts use the Arial font; substitute an installed font if
necessary. Optional Nim checks also need the game repository and its configured
dependencies. Override the launcher with `--blender /path/to/blender` as needed.

Commands below run from the art repository. Supply an approved **512×512** atlas
at `tmp/building-kit/assets/buildings-atlas.png` before starting. The existing
installed pack is normally `../polyworld_data/terrain/lvd_buildings`.

```sh
buildingTools=skills/scripts/modeling_buildings/run.py
buildingWork=tmp/building-kit
mkdir -p "$buildingWork/assets"
# Copy the approved runtime atlas into assets/buildings-atlas.png first.
python3 "$buildingTools" buildings build_scene.py --work "$buildingWork" --skip-render
python3 "$buildingTools" buildings build_construction.py --work "$buildingWork" --scene polyworld-buildings.blend --skip-render
python3 "$buildingTools" buildings rescale_buildings.py --work "$buildingWork" --scene polyworld-buildings.blend --skip-render
python3 "$buildingTools" buildings rescale_buildings.py --work "$buildingWork" --scene polyworld-construction.blend --skip-render
python3 "$buildingTools" buildings pack_atlas_512.py --work "$buildingWork"
python3 "$buildingTools" buildings export_glbs.py --work "$buildingWork" --scene polyworld-buildings.blend
python3 "$buildingTools" buildings export_construction.py --work "$buildingWork" --scene polyworld-construction.blend
python3 "$buildingTools" buildings verify_scene.py --work "$buildingWork" --scene polyworld-buildings.blend
python3 "$buildingTools" buildings verify_glbs.py --work "$buildingWork" --scene polyworld-buildings.blend --skip-render
python3 "$buildingTools" buildings verify_construction.py --work "$buildingWork" --scene polyworld-construction.blend --skip-render
```

`build_construction.py` must run **once on the unscaled finished source** before
scaling both blends separately. It combines fixed shell dimensions with copied
placements and is not idempotent. Finished export must precede construction
export, which uses its recorded origins. `pack_atlas_512.py` relinks and packs
the already resized image in both blends; it does not resize PNG artwork.

`--scene` is relative to `--work` unless absolute. Other paths are relative to
the invoking directory. `--dry-run` prints the command without staging or
executing it; a specified blend must already exist. `--skip-render` skips only
optional building preview PNGs. Omit it for visual review. `--final` selects the
builder's final render quality. Existing differing staged scripts are preserved
unless `--refresh-scripts` is explicit; this option replaces scripts, not assets.

Output is `exports/lvd_buildings/` for finished models and
`exports/construction/` for construction models. Reports go in `reviews/`.
Validators import GLBs into temporary Blender scenes: **do not save these
validation sessions over the editable authoring blends**.

The optional loader checks run `nim check` before compiling and exercising the
game's actual `loadPropPack` implementation on the staged exports:

```sh
python3 "$buildingTools" buildings check_glbs.nim --work "$buildingWork" --polyworld ../polyworld
python3 "$buildingTools" buildings check_construction.nim --work "$buildingWork" --polyworld ../polyworld
```

### Historical scripts, not rebuild steps

The current `build_scene.py` already contains the final wing rotation, neutral
mine entrance, cart, rails, and seven gold nuggets. Do not replay these migrations
after a fresh build:

| Script | Original purpose and limitation |
| --- | --- |
| `revise_scene.py` | Changed older wing/mine geometry and removed the cart. Reapplying changes dimensions and modifiers again. |
| `restore_cart.py` | Restored parts from `versions/before-entrance-and-wing-changes.blend`. Requires that historical backup; repeats duplicate parts. |
| `finalize_scene.py` | Relinked the texture and rendered an older stage. Resets resolution to 2560; run before rescaling if needed. Final checks expect 2400. |
| `update_glb_atlas.py` | Migrated older embedded atlases and pack manifests. Writes the explicitly supplied pack; not needed for fresh exports. |
| `externalize_textures.py` | Its helper is used by current exporters. Running the file directly is a historical pack migration requiring the staged exports and a new backup location. |

The builders and validators intentionally encode this kit's object names,
collections, counts, ray positions, and dimensions. Adapt these together when
changing the kit. They are preserved working recipes, not a general modeling API.

## GLB packaging and pivots

Evaluate live modifiers and nested instances in the active authoring scene.
Snapshot source objects and instance matrices before creating evaluated copies.
Bake transforms on copies, join each prop to one mesh/node, retain UVs and
normals, and omit cameras, lights, animations, and display-stage geometry.
Multiple material primitives within that mesh are acceptable.

Use a ground-level footprint-center pivot. Construction must use the **finished
model's** origin, not independently center its own bounds. Blender Z-up/front-Y
becomes glTF Y-up/front+Z; manifest dimensions are width, height, depth. Load with
`unitHeight=false`. Recheck the game loader when integrating: its node merge has
previously recentered geometry, requiring the manifest construction offset in
local space before world rotation and scale.

The installed layout contains 25 GLBs and one shared base image:

```text
lvd_buildings/
  manifest.json
  construction-manifest.json
  models/<building>.glb                         # Nine finished models.
  models/construction/foundation/<building>_foundation.glb # Eight models.
  models/construction/walls/<building>_walls.glb # Eight models.
  textures/buildings-atlas.png
  textures/factions/<faction>.png              # Eight atlas variants.
  textures/factions/manifest.json
```

Merge the two staged export trees into a pack with this structure when publishing;
do not move a GLB alone. Finished GLBs reference `../textures/buildings-atlas.png`;
construction GLBs reference `../../../textures/buildings-atlas.png`. External
images allow sharing; packing an image inside an authoring `.blend` is fine.

The externalization helper removes the PNG buffer view, repacks remaining views
with four-byte alignment, remaps accessor references, and leaves geometry bytes
unchanged. It is specialized to this kit's single buffer and single image.
Recompute manifest hashes after rewriting files. Never assume it is a general
multi-atlas or compressed-GLB converter.

Check source hashes, mesh counts, finite UVs, bounds, pivots, and image references.
Reimport exported GLBs in a fresh Blender process and confirm the resolved image
is external and 512×512. Check a complete installed pack through Blender with
the command below; the launcher keeps its report in `--work`. This check needs
both the finished and construction manifests and all 25 models.

```sh
python3 "$buildingTools" buildings verify_shared_atlas.py --work "$buildingWork" --pack ../polyworld_data/terrain/lvd_buildings
```

## Packaging and reviewing faction textures

Copy the example JSON files into a separate workspace as `prompts.json`,
`sources.json`, and `layout.json`. Edit source paths and measured boundaries.
Source paths are relative to that workspace unless absolute. The preserved
prompts document generation and emblem edits; **the packer does not generate
artwork**. It requires eight prepared source PNGs. Reference files in the example
prompts are placeholders for the approved images supplied to imagegen.

```sh
trimWork=tmp/faction-trims
reviewPack=tmp/review-pack
trimExamples=skills/scripts/modeling_buildings/faction_trims
mkdir -p "$trimWork" "$reviewPack/models" "$reviewPack/textures"
cp "$trimExamples/prompts.example.json" "$trimWork/prompts.json"
cp "$trimExamples/sources.example.json" "$trimWork/sources.json"
cp "$trimExamples/layout.example.json" "$trimWork/layout.json"
# Populate the temporary review pack with the existing finished models.
cp ../polyworld_data/terrain/lvd_buildings/manifest.json "$reviewPack/manifest.json"
cp ../polyworld_data/terrain/lvd_buildings/models/*.glb "$reviewPack/models/"
cp ../polyworld_data/terrain/lvd_buildings/textures/buildings-atlas.png "$reviewPack/textures/"
# Supply the eight source images and check layout.json before packaging.
python3 "$buildingTools" faction_trims package.py --work "$trimWork" --pack "$reviewPack"
```

`package.py` writes eight 512-pixel PNGs and a manifest under the supplied pack's
`textures/factions/`, preserves masters under the workspace's `generated/`, and
creates atlas/flag contact sheets. The example copies the finished model manifest,
GLBs, and neutral base atlas into the same temporary pack so the next render uses
the newly packaged textures. `--pack` is explicit because packaging and migration
scripts write there. Render scripts read it.

Use `faction_trims/render_preview.py` for a town-hall comparison first. Then render
every role: testing only the town hall misses crop, neutral-mine, and tower UVs.

```sh
renderWork=tmp/faction-renders
reviewPack=tmp/review-pack
python3 "$buildingTools" faction_trims render_preview.py --work "$trimWork" --pack "$reviewPack"
python3 "$buildingTools" faction_renders render_all.py --work "$renderWork" --pack "$reviewPack"
python3 "$buildingTools" faction_renders compose.py --work "$renderWork" --pack "$reviewPack"
```

Keep lighting, viewing angle, and orthographic scale identical across variants
and roles. Center projected bounds without fitting each building to a different
scale; otherwise a scale comparison becomes misleading. The preserved full
render uses 800×800 PNGs, Cycles with 32 samples, and orthographic scale 11.4.
Eight faction buildings × eight factions plus one neutral mine gives **65 unique
renders**, reused in 72 comparison cells. A recorded full run took about 23
minutes on the original machine. Avoid full rerenders for documentation changes.

The compositor makes eight 3×3 faction sheets, nine per-building sheets, an
8×9 comparison matrix, and a self-contained HTML gallery. Its template uses
embedded thumbnails and stays below 1 MB. Preserve full-resolution PNGs alongside
the gallery. Load the visualize skill before changing or presenting an inline
visualization; copying the existing template alone is not a new visual design.

Use a judge subagent to inspect the atlas and rendered models from multiple
angles, including overhead construction views. Ask it to check silhouette,
symmetry, hollow walls, door scale, tile seams, flag legibility, natural crop
colors, dark-stone readability, and neutral mine treatment. Fix concrete findings
and record the review in `tmp/`. Automated checks supplement visual judgment.

[provenance.json](scripts/modeling_buildings/provenance.json) records original
script locations and hashes. The bundle includes the actual workflow scripts,
example generation records, and gallery template; generated binary art and old
task evidence remain outside this skill.
