# Initial import

The initial import was prepared on 2026-09-22 from the working tree of
`Metta-AI/polyworld-data`, based on commit
`254f07b8596a57745f5e4e5a6eae12f993bf6c8c` and the owner's current uncommitted
asset cleanup. No Git objects, branches, tags or previous revisions were
copied. The per-file digests in `licenses/assets.json` identify this snapshot.

The former repository's root dedication records the owner's confirmation
that the project-generated models, textures, artwork, icons, UI and logos
are AI-generated project assets under CC0. That dedication is retained here.
The LvD building notice records the separate 2026-09-22 confirmation.
Imported third-party fonts, water and animations retain their notices.

## Included

- The active CharGen parts, palettes, rig, 43 Quaternius animation clips,
  presets, mainline rosters and portraits.
- Cleaned editable CharGen Blender files, source recipes and authoring tools.
  The existing cleanup audit checked all 14 character authoring scenes.
- Generated fort models, editable fort source and textures, LvD buildings,
  generated terrain tiles and stamps, and TreeGen and RockGen textures.
- Generated mainline themes, icons, abilities, items, effect images and UI.
- Quaternius Universal Standard source files, including its CC0 FBX exports
  for Unity. These exports are from Quaternius and are not Unity Asset Store
  content.
- Three.js MIT water maps and the three OFL font families
  used by the mainline art and theme library.

## Excluded

- Unity Asset Store character and environment packs, including Mini Legion,
  Modular Characters, RPG Monsters, Handpainted Forest, CartoonTerrain and
  Toon Enchanted Meadow/Golden Valley.
- Tower Defense Kit and its portraits, licensed for noncommercial use.
- The old Unity animation and pose exports, Layer Lab eyes, and eye variants
  with unresolved provenance.
- Historical CharGen review images and HTML reports, except the documented
  project-generated face source sheets. A cleaned Blender file does not make
  old screenshots of removed parts redistributable.
- Heartleaf, AWM, Pudge Wars, Cogcraft, unrelated legacy terrain packs,
  sound packs, temporary files, caches and Blender backup files.
- Low Poly Grass Pack by Anskar, removed after confirming that no mainline
  game places its meshes. GotA's unused loading and browser bundle entry were
  disabled at the same time.

Historical source recipes or audit notes may mention omitted files. Those
references are not permission to restore them. Current runtime dependencies
are checked against the new repository, and per-game notices describe their
selected asset sets.

## Cartoon water migration

The cartoon water experiment's 19 PNGs and two prompt notes were moved from
`Metta-AI/polyworld` on 2026-09-22 into `terrain/cartoon_water/`. The source
checkout was based on commit `4345758`. No earlier revisions were imported.
The existing CC0 dedication covers the water textures and previews.

This collection contains seven imagegen textures, eight procedural textures
and previews, and four rendered experiment screenshots. Image bytes were
preserved. Filenames and prompt terminology now use the generic cartoon
water name. The edited prompt notes state that they are not a verbatim
archive. The shader and procedural generator remain in Polyworld under MIT.
See `terrain/cartoon_water/license.md` for the creation process and notices.
