# CTA review using existing chargen assets

Rendered 2026-09-22. All figures are assembled from existing runtime GLB parts,
existing facial textures, existing weapons, and Quaternius animations. The
images come from Polyworld's toon renderer. No image generation was used for
this review. No new geometry, clothing, weapon, rig, or texture was modeled.
The only new character data is an isolated set of draft assembly recipes.
The shared library manifest and CtA gameplay remain unchanged.

[Front roster](runtime/mob_roster_front.png),
[back roster](runtime/mob_roster_back.png),
[walking roster](runtime/mob_roster_walk.png), and
[proposed heroes](runtime/hero_reuse.png).
Compare with the [original concept sheet](roster.png).

The sixteen mobs use beige, green, purple, and red skin. Within each family,
minions are 0.70x, raiders 0.90x, elites 1.10x, and champions 1.40x the base
character scale. Every mob has equipment. The review uses the same camera and
image crop across the mob set so relative size is preserved. The four heroes
retain their original GotA presets and colors and are shown at the same scale
as each other on a separate sheet.

**What the current library can already do.** Evil eyes and undead, orc,
vampire, and demon mouth decals exist. Skin tinting and modular outfit
selection work. Daggers, axes, crossbows, swords, shields, staffs, bows, orbs,
and a bident are available. These are actual equipped characters, not empty
weapon placeholders. New weapon meshes are not necessary for this first pass.

**Missing clothing and appearance features, in suggested order.**

| Priority | Missing item family | Where the render falls short | Existing substitute |
| --- | --- | --- | --- |
| 1 | Ragged starter clothing: torn sleeveless tunic/vest, ragged shorts, wraps, rope belt, small rag cap | Dustling, Bog Runt, Dusk Thrall, and Cinder Imp look neatly dressed. | Basic shirts, gnome shorts, leather belt, ankle boots, and a tall folded gnome hat. |
| 2 | Separate demon horns in small, swept, and large curved forms | Cinder Imp and Ash Reaver have no horns. Infernal Duke inherits a hood to get horns. | Warlock's horned hood works for Ember Hexer, but horns are not a separate category item. |
| 3 | Tribal armor: single shoulder plate, fur collar, wide bracers, studded belt, rough kilt | Tusk Raider lacks a pauldron. Ironhide Chief reads as a green Death Knight. | Berserker harness/kilt and Death Knight armor. |
| 4 | Plain ragged caster hood and robe; bone collar/clasp and feather headband | Crypt Acolyte is a polished blue Lich. Mire Shaman wears a pointed gnome hat and Druid leaves. | Lich robe/hood, Druid mantle/skirt, gnome feather hat. |
| 5 | Vampire high collars, shoulder mantle, fitted split-tail coat, coronet | Velvet Stalker uses a gnome coat. Blood Cantor uses a Warlock robe. Dread Count uses Hades armor/cape with gold trim. | Current coats, robes, crown, and cape establish the silhouette but do not match the tailored vampire set. |
| 6 | Undead champion armor: tombstone pauldrons, broken circlet, rusty plates | Barrow Warden is the existing Death Knight outfit with beige skin. | Death Knight cuirass, tassets, crown, boots, sword, and shield. |
| Appearance | Skull-like head or facial treatment | The undead still have the rounded humanoid head. Existing undead eyes and mouths make them sinister but do not produce the concept's skull silhouette. | Beige skin and existing undead facial decals. |
| Color support | Tint metadata for GotA clothing and trim | Many GotA robes, armor pieces, and hoods keep fixed blue, burgundy, gold, or cyan accents. Basic garments support per-slot fabric RGB, but these detailed pieces often have empty clothShades metadata. | Retain their authored colors in this preview. A later material/metadata pass could cover part of the concept mismatch without new geometry. |

The facial library already supplies flat tusk/fang details. Separate 3D tusks
or fangs are optional polish, not a blocker for recognizable orcs and vampires.
Dread Count retains the crown-fitted black Hades hair. A trial with white
Wavy Panels hair intersected the crown, so that combination was not retained.
The current humanoid proportions are slimmer than the concept's broad brutes;
this pass scales the existing complete assemblies without reshaping bodies.

**Per-mob assembly and gaps.** The draft recipes contain every slot choice,
including exact eyes, mouths, skin RGB, hair, hats, boots, belts, and equipment.

| Mob | Main existing outfit | Equipped weapons | Still missing from the concept |
| --- | --- | --- | --- |
| Dustling | 01 Linen tunic, Gnome folded | Dagger | Torn sack tunic, Rope belt, Ankle wraps, Rag cap. |
| Grave Stalker | Gota Crossbowman leather tunic, Gota Crossbowman hood | Crossbow | Frayed hood, Shredded short cape, Distressed leather. |
| Crypt Acolyte | Gota Lich ivory edged robe, Gota Lich crystal hood | Lich staff + orb | Torn teal robe, Plain ragged hood, Bone clasp. |
| Barrow Warden | Gota Death Knight cuirass and cape, Gota Death Knight open crown | Sword + shield | Rusted armor, Tombstone pauldrons, Broken circlet. |
| Bog Runt | 05 Ochre tunic | Axe | Patchwork jerkin, Rope belt, Short mohawk. |
| Tusk Raider | Gota Berserker harness | Twin axes | Single iron pauldron, Leather battle kilt, Tribal bracers. |
| Mire Shaman | Gota Druid Warden bark mantle, Gnome feather | Druid staff + orb | Bone-bead collar, Feather headband, Ragged shaman robe. |
| Ironhide Chief | Gota Death Knight cuirass and cape | Axe + shield | Black iron tribal armor, Fur collar, Studded belt. |
| Dusk Thrall | 08 Plum wrap tunic | Dagger | Servant vest, Rolled sleeves, Simple shoes. |
| Velvet Stalker | Gnome tucked shirt | Twin daggers | Fitted split-tail coat, High narrow collar. |
| Blood Cantor | Gota Warlock robe | Warlock staff + censer | Black shoulder mantle, Silver trim, Fang brooch. |
| Dread Count | Gota Hades royal armor, Gota Hades obsidian crown | Sword + orb | Bat-shaped high collar, Silver coronet, Silver armor trim, White swept hair compatible with the crown. |
| Cinder Imp | 04 Red work shirt | Dagger | Separate small horns, Cropped vest, Ragged shorts, Foot wraps. |
| Ash Reaver | Gota Demon Hunter harness | Twin daggers | Separate swept horns, Charcoal pauldrons, Dark battle skirt. |
| Ember Hexer | Gota Warlock robe, Gota Warlock horned hood | Warlock staff + censer | Charcoal and ember robe variant. |
| Infernal Duke | Gota Hades royal armor, Gota Warlock horned hood | Bident + soul orb | Separate great horns, Bronze-edged obsidian armor. |

**The four GotA heroes to bring over.**

| CtA class | GotA preset | Why | Equipment already present |
| --- | --- | --- | --- |
| Fighter | Vanguard Knight | Clear armored front-line role and shield silhouette. | Sword and shield. |
| Wizard | Arcanist | Direct match for the offensive spellcaster. | Staff and arcane orbs. |
| Rogue | Ranger | Fits the current hooded ranged character, Verdant Arrow, and stealth theme. | Bow, arrow, and quiver. |
| Cleric | Druid Warden | Existing support/healer appearance that fits Healing Bloom. | Staff and nature orb. |

Druid Warden gives the Cleric a nature-healer appearance. CtA's holy-themed
Solar Hammer, Angelic Emblem, and Sun Orb would keep their current mechanics
until a separate design decision changes them. If a dual-dagger melee Rogue
is preferred over CtA's current bow/stealth mix, Demon Hunter is the existing
alternative; Ranger is the recommended first migration.

**Verification.**

- `nim check experiments/chargen/render_cta.nim` passed, followed by compiling
  and running the tool successfully.
- All 16 mobs and four heroes loaded through `readPresetCharacter`, using the
  same part selection, attachment, rig, skin, cloth, eye, and hair code as the
  game. Missing named parts or incompatible rigs would fail this path.
- Captured 60 individual images: front and back A poses, plus the existing
  Walk_Loop animation at 0.35 seconds for each character. Inspected the front,
  back, and walking contact sheets and the hero sheet. This is a sampled pose
  review, not full combat-animation validation. Some staffs swing sideways in
  the generic walk pose; final gameplay needs equipment-appropriate animation
  choices and grip checks.
- All 325 selected character source files retain their recorded SHA-256 hashes.
  No existing GLBs, textures, part definitions, palettes, or shared manifest
  were changed. Only universal animation clips and cleared facial parts were
  selected; legacy imported and unresolved eyes were excluded.
- Visible mobs geometry ranges from 14,027 to 27,740 triangles, including equipment.
- Visible heroes geometry ranges from 16,792 to 19,594 triangles, including equipment.
- Seven mob combinations exceed the earlier GotA authoring target of 20,000 triangles: Ironhide Chief, Dusk Thrall, Velvet Stalker, Blood Cantor, Cinder Imp, Ash Reaver, Ember Hexer. They have not been optimized or remodeled. All four original hero selections remain below that target.

Reproducible inputs: [assembly recipes](existing_presets.json),
[selection script](assemble_existing.py), [sheet compositor](compose_review.py),
[source hashes](runtime/source_hashes.json), and
[geometry counts](runtime/geometry.json).
The runtime capture tool is `polyworld/experiments/chargen/render_cta.nim`.

From the Polyworld repository root, regenerate with:

```sh
python3 ../polyworld_art/characters/chargen/source/cta/mob_roster_v1/assemble_existing.py
nim check experiments/chargen/render_cta.nim
nim c --out:tmp/chargen/cta/render_cta experiments/chargen/render_cta.nim
tmp/chargen/cta/render_cta ../polyworld_art/characters/chargen/source/cta/mob_roster_v1/existing_presets.json ../polyworld_art/characters/chargen/source/cta/mob_roster_v1/runtime
python3 ../polyworld_art/characters/chargen/source/cta/mob_roster_v1/compose_review.py
```
