# Character tools and commands

Run examples from the `polyworld_art` repository root. The sibling `polyworld`
checkout supplies Nim runtime libraries and its configured dependencies.

```sh
characterScripts=skills/scripts/chargen
blenderExe=/Applications/Blender.app/Contents/MacOS/Blender
pythonExe=/opt/homebrew/bin/python3
```

Use `blender` and `python3` on other installations. Blender provides `bpy`,
`bmesh`, and `mathutils`; ordinary Python supplies Pillow for image cutting,
packing, and sheets. Some cutters invoke ImageMagick's `magick`. Nim tools use
the project's Nim configuration plus gltf, pixie, silky, windy, chroma, vmath,
jsony, and related workspace dependencies. Check availability before installing
anything. Blender 5.2.2 and Nim from the local workspace were used here.

## What is bundled

The Python files are a snapshot of the active Chargen authoring toolkit,
including all local imports so builders are not stranded without helpers.
The `nim/` files preserve the editor, render tools, overlays, and tests as
source references. They depend on the live engine; `run_nim.py` compiles the
corresponding live file from `polyworld/experiments/chargen`, retaining its
project configuration and asset paths. It does not compile the reference copy.
Model recipes still require the library's `.blend`, textures, metadata, and
animation source. This bundle does not duplicate the assets or engine.

[sources.json](../../scripts/chargen/sources.json) records source
paths, repository revisions, hashes, and local adaptations. The copied
`paths.py` and the Hades review path are changed for this location;
`run_nim.py` is the added launcher.
No live authoring source was moved. If source or APIs change, compare with the
recorded snapshot and update the relevant recipe rather than blindly copying
the whole bundle back into the library.

| Override | Bundled Python meaning |
| --- | --- |
| `CHARGEN_ART` | Art repository root; defaults to the repository containing this skill |
| `CHARGEN_LIBRARY` | Runtime library plus its `source/`; defaults to `characters/chargen` in the art repo |
| `POLYWORLD_PROJECT` | Nim project root; defaults to sibling `polyworld` |
| `CHARGEN_PREVIEW` | Temporary output directory; defaults to `polyworld/tmp/chargen` |
| `CHARGEN_PYTHON` | Python executable used by builder subprocesses |

These overrides are implemented in the bundled `paths.py`, not promised for
every live script. The Nim editor and garment/Gota renderers honor
`CHARGEN_LIBRARY`; not every other Nim utility supports that override. Check
the selected source. `CHARGEN_PREVIEW` affects Python and launcher output,
not hardcoded output paths inside all Nim renderers.

## Choose the smallest operation

| Task | Entry point | Effect |
| --- | --- | --- |
| Inventory parts and clips | `python3 pack.py --list` | Reads library |
| Count nine gnome presets | `python3 count_polygons.py` | Writes reports under Preview |
| Audit supported sources | `python3 verify_clean.py` | Reads assets and rejects retired imports |
| Pack selected assets | `python3 pack.py --output ...` | Writes a new runtime library |
| Test atlas/pack contract | `python3 test_packs.py` | Creates and removes temporary packs |
| Add shared X-eye geometry | Blender `build_expressions.py` | Updates master, source metadata, and expression files |
| Rebuild one Gota outfit | Blender `gota_common.py -- slug` | Replaces that hero's parts and isolated authoring file |
| Finalize an isolated outfit | Blender `finalize_gota.py -- slug` | Sets outfit visibility and skin in its authoring file |
| Register Gota selections | `python3 register_gota.py` | Merges Gota presets, metadata and skin palette entries |
| Audit isolated authoring sources | Blender `clean_sources.py -- --check` | Reads `.blend` files without cleanup or rebuilding |
| Rebuild hats or gnome features | Blender `build_hats.py`, `build_gnomes.py` | Replaces that family and exports assets |
| Rebuild fitted/layered clothing | Blender `build_clothes.py`, `build_garments.py` | Replaces clothing geometry and exports assets |
| Detach old integrated belts | Blender `build_belts.py` | Migrates master, then re-exports |
| Import supported animation | Blender `import_animations.py` | Changes actions and runtime clip exports |
| Simplify export only | Blender `optimize_model.py` | Re-exports reduced game parts from detailed master |
| Build entire base character | Blender `build_model.py` | Broad regeneration; overwrites authored geometry and exports |
| Remove retired imports | Blender `clean_sources.py` | Migration that deletes old data; not a routine validation command |

Builders commonly write the shared `.blend`, manifests, and runtime files.
They are not dry runs. Use a copied library and explicit overrides when
experimenting, or the narrow builder when updating approved parts. Do not run
every builder as a setup step. `--python-exit-code 1` makes Blender script
failures observable to automation. The packer refuses an existing output path.

## One Gota hero or god

For an edit in this checkout, change the live recipe and build that recipe.
Use the bundle as a reference; do not overwrite newer live code with a snapshot.

```sh
heroScripts=characters/chargen/source/scripts
heroSlug=death_knight
"$blenderExe" --background --python-exit-code 1 \
  --python "$heroScripts/gota_common.py" -- "$heroSlug"
"$blenderExe" --background --python-exit-code 1 \
  --python "$heroScripts/finalize_gota.py" -- "$heroSlug"
```

The same entry point accepts `zeus` and `hades`. The builders write shared
runtime part files as well as `source/gota/<slug>/hero.blend`; isolated source
files do not make the export a dry run. If part IDs, nodes, selections or
metadata change, run `register_gota.py` after all workers finish. A same-ID
geometry-only edit does not need a new preset or global regeneration.

`build_gota.py --hero` also invokes `build_gota_body.py`. The equipment builder
`build_gota_weapons.py` rebuilds the ten-hero equipment collection and
registers it; it is not a single-weapon command. Inspect scope before invoking
either for a local correction.

## Face art and model commands

Use the imagegen skill and built-in image tool for generation, visual edits,
and transparent extraction. Its outputs are raster references/decals, not
meshes. Save project assets in the workspace and preserve exact prompts.
`view_image` inspects PNGs; it does not render Blender geometry.

```sh
# Recut the approved sheets. These overwrite their named texture outputs.
"$pythonExe" "$characterScripts/cut_faces.py"
"$pythonExe" "$characterScripts/cut_gnomes.py"

# Add one family without rebuilding the whole body.
"$blenderExe" --background --python-exit-code 1 \
  --python "$characterScripts/build_expressions.py"
```

`cut_faces.py` expects the existing `source/eyes/monster_v1` and
`source/mouths/evil_v1` sheet layout, including its deliberately excluded insect
cell. It is not a generic cutter for arbitrary sheets. `cut_gnomes.py` expects
the approved pair and uses component detection for the iris. Inspect masks
after either operation. The saved `source/eyes/dead_x_v1` prompt records the
single-pair expression process; its runtime PNG preserves generated alpha.

```sh
# Render the sixteen real hairstyles or beards, then build paired sheets.
"$blenderExe" --background --python-exit-code 1 \
  --python "$characterScripts/render_hairs.py"
"$pythonExe" "$characterScripts/hair_sheets.py"
"$blenderExe" --background --python-exit-code 1 \
  --python "$characterScripts/render_beards.py"
"$pythonExe" "$characterScripts/beard_sheets.py"
```

The renderers accept arguments after Blender's `--`; inspect their parsers for
`--styles` and `--output`. Sheets consume the renderer output and expected
source atlas metadata. Keep front/back cells paired and review side views too.

## Runtime preview and checks

```sh
"$pythonExe" "$characterScripts/run_nim.py" chargen --check
"$pythonExe" "$characterScripts/run_nim.py" chargen

EYES="Dead X" ANIM=Idle_Loop \
  "$pythonExe" "$characterScripts/run_nim.py" chargen
GNOME_LINEUP=1 ANIM=Walk_Loop \
  "$pythonExe" "$characterScripts/run_nim.py" chargen
GOTA_LINEUP=1 ANIM=Walk_Loop \
  "$pythonExe" "$characterScripts/run_nim.py" chargen

"$pythonExe" "$characterScripts/run_nim.py" tests --check
"$pythonExe" "$characterScripts/run_nim.py" tests
"$pythonExe" "$characterScripts/test_packs.py"
```

`PRESET` is a one-based index into the current manifest, not a permanent ID.
Part overrides use category names as environment variables, such as `EYES`.
`ANIM`, `POSE_TIME`, `CAM_DIST`, and `CAM_YAW` support repeatable previews.
`WEIGHTS=LeftHand` opens the bone-weight view; `BONES=1` and `WIREFRAME=1`
assist attachment review. The editor's V key toggles polygon edges. Inspect
the live source for current options rather than assuming old comparison flags
still exist. X-eye previews do not write a new default.

```sh
# Matching before/after game renders; use separate copied asset libraries.
CHARGEN_LIBRARY=/absolute/before/library \
REVIEW_OUTPUT=/absolute/review/before \
  "$pythonExe" "$characterScripts/run_nim.py" render_garments
CHARGEN_LIBRARY=/absolute/after/library \
REVIEW_OUTPUT=/absolute/review/after \
  "$pythonExe" "$characterScripts/run_nim.py" render_garments
```

Run each library with the same settings for an actual comparison: both toon,
then both `REVIEW_PBR=1`. `REVIEW_HANDS=1` makes wrist closeups, and
`CLOTHING_DETAILS=1` exposes garment details. Normal renders include front,
side, back, walk, and crouch. `render_gota` additionally supports
`REVIEW_PRESET`, `REVIEW_HEAD`, `REVIEW_ALL_PARTS`, and `REVIEW_ANGLE`.

### Hidden Gota captures

Use the current `render_gota` for automated captures without popup windows.
It creates a hidden window and explicitly renders into an offscreen
multisample framebuffer, resolves to a color buffer, then reads that buffer.
Setting `visible = false` alone produced black captures on macOS.

```sh
reviewRoot="$PWD/../polyworld/tmp/chargen/helmet-review"
"$pythonExe" "$characterScripts/run_nim.py" render_gota --check
REVIEW_PRESET="Death Knight" REVIEW_HEAD=1 REVIEW_ANGLE=0 \
REVIEW_OUTPUT="$reviewRoot/front" \
  "$pythonExe" "$characterScripts/run_nim.py" render_gota
REVIEW_PRESET="Death Knight" REVIEW_HEAD=1 REVIEW_ANGLE=1.5707963 \
REVIEW_OUTPUT="$reviewRoot/side" \
  "$pythonExe" "$characterScripts/run_nim.py" render_gota
```

Angles are radians. Each image pairs the requested angle with angle plus pi:
the first command gives front/back, the second gives the two sides. `model.png`
is T-pose; `walk.png` and `crouch.png` use fixed sampled times. `Headgear.png`
isolates the item. `REVIEW_PBR=1` selects smooth lighting; otherwise use normal
toon shading. `REVIEW_HEAD=0` restores the full preset. `REVIEW_EQUIPMENT=1`
selects separate equipment review slots, not a switch that equips empty slots.

Recompile from the current source rather than reusing an old temporary binary.
Several Python review helpers expect `Preview/gota/render_gota`, whereas
`run_nim.py` writes `Preview/skill_tools/render_gota`. Point the helper at the
fresh binary or deliberately compile to its expected location before running
it. Do not assume other renderers are hidden: the current `render_swords`
still uses a visible default window/buffer. Adapt the offscreen capture path
before using that tool for unattended reviews. Its `REVIEW_ORIGINAL=1` flag
means zero socket rotation, not loading a retired character.

For a completed Gota edit, run the applicable `verify_gota.py`,
`verify_gota_gods.py`, or `verify_gota_weapons.py`, then the CharGen checks above.
`verify_clean.py` checks the active library; Blender `clean_sources.py` with
`-- --check` checks the authoring scenes. These source audits do not replace
visual inspection of the changed exported part.

```sh
"$pythonExe" "$characterScripts/count_polygons.py"
"$pythonExe" "$characterScripts/verify_geometry.py"
"$pythonExe" "$characterScripts/verify_library.py"
"$blenderExe" --background --python-exit-code 1 \
  --python "$characterScripts/verify_universal.py"
```

The last three checks need a current assembled `Preview/character.glb` and,
for geometry, its `.geometry.json` report. `verify_library.py` expects its
assembled export to contain the complete inventory it compares. Additive
character libraries can have parts absent from an older base export; use a
matching export or a scoped copy. Do not call a stale-export mismatch a new
mesh bug. `verify_geometry.py --baseline path.glb` also expects identical mesh
names and clip sets; belt extraction or animation-source cleanup changes that
contract. The Universal verifier compares every exported source frame and
checks rotation error, fixed limb lengths, and hips displacement.

## Minimal game packs

List valid part IDs first. Include the chosen body/head and equipment alongside
face options; a selected texture is not an assembled character by itself.

```sh
"$pythonExe" "$characterScripts/pack.py" --list
"$pythonExe" "$characterScripts/pack.py" \
  --output /absolute/new/game-characters \
  --parts body/base heads/base eyes/02_focused eyes/dead_x \
    mouths/01_relaxed_smile eyebrows/01_soft_arch noses/tiny \
  --clips Idle_Loop Walk_Loop Death01
```

Use the game's requested parts rather than this illustrative list. The packer
adds transition dependencies and can skip atlases with `--no-atlas`. Confirm a
minimal pack loads independently and has no source or unrelated binary assets.

## Source catalog

The following catalog is grouped by actual use. Recipe modules are normally
imported by a builder; they are not all standalone commands. Gota-specific
recipes are included as concrete examples of per-character integration, not
requirements to model a gnome or a new unrelated character.

### Core geometry and modular features

| Script | Purpose |
| --- | --- |
| [build_belts.py](../../scripts/chargen/build_belts.py) | Detach waist belts from older tunics without regenerating other geometry. |
| [build_clothes.py](../../scripts/chargen/build_clothes.py) | Add body-derived clothing without rebuilding existing meshes or animation. |
| [build_expressions.py](../../scripts/chargen/build_expressions.py) | Add shared facial expressions without rebuilding other character parts. |
| [build_garments.py](../../scripts/chargen/build_garments.py) | Add gnome outerwear and outfit presets without rebuilding existing assets. |
| [build_gnomes.py](../../scripts/chargen/build_gnomes.py) | Add shared gnome modules and nine presets without rebuilding old parts. |
| [build_hats.py](../../scripts/chargen/build_hats.py) | Add modular gnome hats without rebuilding faces, bodies, or animation. |
| [build_model.py](../../scripts/chargen/build_model.py) | Build the procedural character and import only Quaternius animations. |
| [clothes.py](../../scripts/chargen/clothes.py) | Cut and offset the real skinned body to make simple modular clothing. |
| [expressions.py](../../scripts/chargen/expressions.py) | Build shared expression decals for every character using the common head. |
| [garments.py](../../scripts/chargen/garments.py) | Extend the existing fitted clothes into simple modular gnome outfits. |
| [gnomes.py](../../scripts/chargen/gnomes.py) | Build the shared gnome face modules on the existing character head rig. |
| [hats.py](../../scripts/chargen/hats.py) | Build simple shared gnome hat shapes with fixed-color decorations. |

### Hair and beard recipes

| Script | Purpose |
| --- | --- |
| [beard_styles_01_04.py](../../scripts/chargen/beard_styles_01_04.py) | Sculpt the first four facial-hair concepts on the shared face. |
| [beard_styles_05_08.py](../../scripts/chargen/beard_styles_05_08.py) | Beard styles 05 08. |
| [beard_styles_09_12.py](../../scripts/chargen/beard_styles_09_12.py) | Closed tapered, spade, Van Dyke, and single-tassel facial hair. |
| [beard_styles_13_16.py](../../scripts/chargen/beard_styles_13_16.py) | Beard styles 13 16. |
| [beards.py](../../scripts/chargen/beards.py) | Build interchangeable sculpted facial hair on the shared animated head. |
| [hair_styles_01_04.py](../../scripts/chargen/hair_styles_01_04.py) | Sculpt the first four short hairstyle concepts. |
| [hair_styles_05_08.py](../../scripts/chargen/hair_styles_05_08.py) | Hair styles 05 08. |
| [hair_styles_09_12.py](../../scripts/chargen/hair_styles_09_12.py) | Sculpted twin braids, blunt bob, waved bob, and layered shag hairstyles. |
| [hair_styles_13_16.py](../../scripts/chargen/hair_styles_13_16.py) | Hair styles 13 16. |
| [hairs.py](../../scripts/chargen/hairs.py) | Build editable, interchangeable sculpted hair meshes for the shared head. |

### Face texture processing

| Script | Purpose |
| --- | --- |
| [cut_faces.py](../../scripts/chargen/cut_faces.py) | Cut approved monster face sheets into independently shippable textures. |
| [cut_gnomes.py](../../scripts/chargen/cut_gnomes.py) | Extract the generated kind eyes and their independent iris tint mask. |

### Animation and rigging

| Script | Purpose |
| --- | --- |
| [import_animations.py](../../scripts/chargen/import_animations.py) | Add the Universal library to the existing authoring model and split GLBs. |
| [retarget.py](../../scripts/chargen/retarget.py) | Shared sampling and target-pose helpers for supported glTF animations. |
| [universal.py](../../scripts/chargen/universal.py) | Retarget Quaternius Standard humanoid clips onto the Chargen armature. |

### Export, packing, and provenance

| Script | Purpose |
| --- | --- |
| [clean_sources.py](../../scripts/chargen/clean_sources.py) | Remove retired imported data from existing authoring files without remeshing. |
| [export_library.py](../../scripts/chargen/export_library.py) | Export separately shippable character parts, textures, and animation clips. |
| [glbs.py](../../scripts/chargen/glbs.py) | Read, subset, and remap binary glTF assets without changing skin data. |
| [optimizations.py](../../scripts/chargen/optimizations.py) | Reduce runtime geometry while retaining the editable authoring meshes. |
| [optimize_model.py](../../scripts/chargen/optimize_model.py) | Re-export reduced game meshes from the unchanged editable Blender model. |
| [pack.py](../../scripts/chargen/pack.py) | Pack selected character parts and build atlases from only their textures. |
| [paths.py](../../scripts/chargen/paths.py) | Resolve bundled recipes against an explicit or neighboring art library. |
| [provenance.py](../../scripts/chargen/provenance.py) | Keep retired character imports out of authoring exports and game packs. |

### Rendering and sheets

| Script | Purpose |
| --- | --- |
| [beard_sheets.py](../../scripts/chargen/beard_sheets.py) | Arrange actual Blender facial hair renders in the concept sheet's 4 by 4 layout. |
| [clothing_sheets.py](../../scripts/chargen/clothing_sheets.py) | Arrange modeled clothing turnarounds in the approved 4 by 4 layout. |
| [gallery_gota.py](../../scripts/chargen/gallery_gota.py) | Publish local comparison pages and collate unretouched runtime captures. |
| [hair_sheets.py](../../scripts/chargen/hair_sheets.py) | Arrange actual Blender hair renders in the concept sheet's 4 by 4 layout. |
| [render_beards.py](../../scripts/chargen/render_beards.py) | Render the real modeled facial hair styles as paired concept-matching turnarounds. |
| [render_clothes.py](../../scripts/chargen/render_clothes.py) | Render the actual clothing models in matching front and back pairs. |
| [render_hairs.py](../../scripts/chargen/render_hairs.py) | Render the real modeled hairstyles as paired concept-matching turnarounds. |
| [review_gota.py](../../scripts/chargen/review_gota.py) | Compare actual runtime renders and generated references without retouching. |
| [review_gota_gods.py](../../scripts/chargen/review_gota_gods.py) | Build a local index of the god concepts, actual models and review evidence. |
| [review_gota_hades.py](../../scripts/chargen/review_gota_hades.py) | Generate the Hades concept-to-runtime asset review index. |
| [review_gota_hoods.py](../../scripts/chargen/review_gota_hoods.py) | Compare fitted hoods in front, side and back runtime views. |
| [review_gota_swords.py](../../scripts/chargen/review_gota_swords.py) | Capture actual creep sword grips and attack poses from three directions. |
| [review_gota_weapons.py](../../scripts/chargen/review_gota_weapons.py) | Render equipped heroes and assemble contact sheets of actual runtime meshes. |
| [review_gota_zeus.py](../../scripts/chargen/review_gota_zeus.py) | Capture Zeus in the runtime renderer and map each asset to its concept. |
| [run_nim.py](../../scripts/chargen/run_nim.py) | Run the live Chargen Nim utilities with their project configuration. |

### Verification

| Script | Purpose |
| --- | --- |
| [count_polygons.py](../../scripts/chargen/count_polygons.py) | Report actual rendered triangles for the nine assembled gnome presets. |
| [test_packs.py](../../scripts/chargen/test_packs.py) | Check selected exports, exact atlas pixels, and extensible part discovery. |
| [verify_clean.py](../../scripts/chargen/verify_clean.py) | Audit the active CharGen library for retired imports and broken selections. |
| [verify_clothes.py](../../scripts/chargen/verify_clothes.py) | Check actual garment skinning, topology and animated body clearance. |
| [verify_garments.py](../../scripts/chargen/verify_garments.py) | Verify inherited garment weights, valid geometry, and posed body clearance. |
| [verify_geometry.py](../../scripts/chargen/verify_geometry.py) | Check reduced runtime geometry, skinning, seams, and gnome triangle budgets. |
| [verify_gota.py](../../scripts/chargen/verify_gota.py) | Audit the final runtime library rather than relying on authoring counts. |
| [verify_gota_gods.py](../../scripts/chargen/verify_gota_gods.py) | Audit the two exported god presets against their actual runtime assets. |
| [verify_gota_weapons.py](../../scripts/chargen/verify_gota_weapons.py) | Audit exported equipment geometry, skin sockets, materials and set budgets. |
| [verify_library.py](../../scripts/chargen/verify_library.py) | Verify split meshes and animation keys against the assembled Blender export. |
| [verify_model.py](../../scripts/chargen/verify_model.py) | Verify topology, attachment weights, animation, and GLB round trips. |
| [verify_universal.py](../../scripts/chargen/verify_universal.py) | Check every exported Universal frame against the authored source motion. |

### Character-specific Gota examples

| Script | Purpose |
| --- | --- |
| [build_gota.py](../../scripts/chargen/build_gota.py) | Rebuild and review isolated Gota modules after the shared character library. |
| [build_gota_body.py](../../scripts/chargen/build_gota_body.py) | Add a split reusable body so trousers can hide covered skin during motion. |
| [build_gota_weapons.py](../../scripts/chargen/build_gota_weapons.py) | Build simple solid-color Gota equipment on the canonical character rig. |
| [finalize_gota.py](../../scripts/chargen/finalize_gota.py) | Present isolated hero authoring files with only their selected outfit visible. |
| [gota_arcanist.py](../../scripts/chargen/gota_arcanist.py) | Build fitted purple Arcanist clothing on the shared character rig. |
| [gota_berserker.py](../../scripts/chargen/gota_berserker.py) | Build the Berserker's fitted, independently selectable solid-color outfit. |
| [gota_common.py](../../scripts/chargen/gota_common.py) | Build isolated Gota parts on the existing Chargen rig without shared rebuilds. |
| [gota_crossbowman.py](../../scripts/chargen/gota_crossbowman.py) | Fit the medieval Crossbowman's five modular garments to the shared rig. |
| [gota_death_knight.py](../../scripts/chargen/gota_death_knight.py) | Build modular Death Knight clothing on the existing Polyworld rig. |
| [gota_demon_hunter.py](../../scripts/chargen/gota_demon_hunter.py) | Build the blindfolded Demon Hunter from fitted shared clothing geometry. |
| [gota_druid_warden.py](../../scripts/chargen/gota_druid_warden.py) | Build the Druid Warden from fitted clothing and angular foliage. |
| [gota_hades.py](../../scripts/chargen/gota_hades.py) | Build Hades' modular solid-color garments on the existing Polyworld rig. |
| [gota_hades_equipment.py](../../scripts/chargen/gota_hades_equipment.py) | Build Hades' two-pronged staff and emerald soul on the shared hand sockets. |
| [gota_lich.py](../../scripts/chargen/gota_lich.py) | Build the pale human Lich's modular blue clothing on the shared rig. |
| [gota_ranger.py](../../scripts/chargen/gota_ranger.py) | Build Ranger's fitted five-slot olive and leather clothing. |
| [gota_vanguard_knight.py](../../scripts/chargen/gota_vanguard_knight.py) | Fit Vanguard Knight's modular ivory armor to the shared chargen rig. |
| [gota_warlock.py](../../scripts/chargen/gota_warlock.py) | Build the Warlock's separate fitted, solid-color fantasy garments. |
| [gota_zeus.py](../../scripts/chargen/gota_zeus.py) | Build Zeus as independent solid-color modules on the shared Gota rig. |
| [gota_zeus_head.py](../../scripts/chargen/gota_zeus_head.py) | Build Zeus's crown and flowing white hair on the shared head socket. |
| [gota_zeus_legs.py](../../scripts/chargen/gota_zeus_legs.py) | Fit Zeus's pleated skirt and gold sandals to the shared humanoid rig. |
| [gota_zeus_props.py](../../scripts/chargen/gota_zeus_props.py) | Build Zeus lightning equipment with solid colors on the shared hand bones. |
| [register_gota.py](../../scripts/chargen/register_gota.py) | Register Gota heroes and creeps without replacing other preset groups. |

### Nim source snapshots

- [chargen.nim](../../scripts/chargen/nim/chargen.nim)
- [lineups.nim](../../scripts/chargen/nim/lineups.nim)
- [render_garments.nim](../../scripts/chargen/nim/render_garments.nim)
- [render_gota.nim](../../scripts/chargen/nim/render_gota.nim)
- [render_hats.nim](../../scripts/chargen/nim/render_hats.nim)
- [render_swords.nim](../../scripts/chargen/nim/render_swords.nim)
- [tests.nim](../../scripts/chargen/nim/tests.nim)
- [weights.nim](../../scripts/chargen/nim/weights.nim)

The live runtime modules are in `polyworld/src/polyworld/chargen`: `parts`, `presets`, `models`, `eyes`, `brows`, `hairs`, and `clothes`. `polyworld/animblend` drives playback and `polyworld/toon` handles the game shading. These engine libraries are dependencies, not copied into this skill.
