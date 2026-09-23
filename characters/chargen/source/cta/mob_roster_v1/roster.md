# Call to Adventure mob roster

Concept version 1, generated 2026-09-22 with the built-in imagegen tool.
The [sheet](roster.png) contains all 16 proposed mobs and their names.
The [exact prompt](prompt.txt) records the designs and layout. The approved
GotA roster supplied the style reference. These are visual concepts, not
exported chargen models or implemented game changes.

Use the existing modular humanoid rig and the cleared generated character
parts as the foundation. Clothing should use simple solid-color materials
and readable silhouettes. Keep faces and hands exposed so skin color identifies
the family. Use new generated geometry or facial decals where needed for
undead faces, orc tusks, vampire fangs, and demon horns. Avoid wings, tails,
extra limbs, and a dependency on a new skeleton for this initial set.

The four color families are ordered encounter tiers, not yet assignments to
CtA's existing six map levels. Map placement and gameplay balance remain to be
implemented. Skin stays within each family's color range across all ranks.

| Tier | Family | Skin target | Costume palette |
| --- | --- | --- | --- |
| 1 | Undead | Dusty beige, `#C9B48B` | Faded brown, gray iron, muted teal |
| 2 | Orcs | Green, `#72A63B` | Rough brown leather, olive, black iron |
| 3 | Vampires | Purple, `#A779C8` | Midnight blue, plum, wine, silver |
| 4 | Demons | Red, `#D94332` | Charcoal, obsidian, bronze, ember orange |

Within each family, small bodies signal weaker enemies and large, broad bodies
signal stronger enemies. Suggested body heights relative to an unscaled hero
are 0.70 for minions, 0.90 for raiders, 1.10 for elites, and 1.40 for champions.
Measure to the crown of the skull, excluding hats and horns. Do not normalize
every mob to the same rendered height. Increase champion body width as well.
These are authoring targets, not current in-game values. Family progression
can raise combat strength independently of these within-family ranks.

| Family | Rank | Name | Costume and identifying features |
| --- | --- | --- | --- |
| Undead | Minion | Dustling | Ragged brown sack tunic, rope belt, crooked cloth cap, mismatched ankle wraps, beige skull-like face. |
| Undead | Raider | Grave Stalker | Frayed charcoal hood, worn leather vest, diagonal straps, shredded short cape, stitched trousers. |
| Undead | Elite | Crypt Acolyte | Torn muted teal robe and hood, bone clasp, ragged shoulder mantle, exposed beige face and hands. |
| Undead | Champion | Barrow Warden | Rusty segmented cuirass, massive tombstone-shaped pauldrons, bronze circlet, dark skirt panels, heavy boots. |
| Orcs | Minion | Bog Runt | Patchwork ochre jerkin, rope belt, short mohawk, cropped trousers, tiny tusks, exposed green arms. |
| Orcs | Raider | Tusk Raider | One iron shoulder guard, crossed leather harness, rough battle kilt, broad belt, bracers, prominent tusks. |
| Orcs | Elite | Mire Shaman | Ragged olive-brown robe, broad bone-bead collar, feathered headband, wrapped forearms. |
| Orcs | Champion | Ironhide Chief | Massive black iron armor, pale fur collar, studded belt, heavy boots, topknot, large tusks. |
| Vampires | Minion | Dusk Thrall | Plum servant vest, gray rolled sleeves, cropped black pants, simple shoes, messy black hair, tiny fangs. |
| Vampires | Raider | Velvet Stalker | Fitted midnight blue split-tail coat, high collar, silver clasp, sleek black hair, tall boots. |
| Vampires | Elite | Blood Cantor | Wine ceremonial robe, black shoulder mantle, silver trim, fang brooch, swept white hair, exposed purple face. |
| Vampires | Champion | Dread Count | Black-and-silver plate over aristocratic clothing, bat-shaped cape collar, silver coronet, white hair, heavy boots. |
| Demons | Minion | Cinder Imp | Cropped soot-black vest, rope belt, ragged shorts, foot wraps, small black horns, exposed red ears and arms. |
| Demons | Raider | Ash Reaver | Black leather harness, charcoal shoulder plates, dark split battle skirt, iron bracers, swept-back horns. |
| Demons | Elite | Ember Hexer | Charcoal robe and pointed hood, broad ember-colored trim, bronze clasp, horns through hood, visible red face and hands. |
| Demons | Champion | Infernal Duke | Huge curved black horns, massive obsidian armor with bronze edging, thick belt, armored boots, dark short cape. |

All 16 have empty hands in the concept sheet so the costume and body silhouette
remain visible. Weapons can be assigned from cleared generated equipment
during implementation. Rank names indicate relative threat, not a decision
that every champion is a unique boss.

CtA's four heroes can reuse these existing GotA presets and portraits:

| CtA class | GotA preset | Existing portrait |
| --- | --- | --- |
| Fighter | Vanguard Knight | `portraits/vanguard_knight.profile.png` |
| Wizard | Arcanist | `portraits/arcanist.profile.png` |
| Rogue | Ranger | `portraits/ranger.profile.png` |
| Cleric | Druid Warden | `portraits/druid_warden.profile.png` |

Portrait paths are relative to `characters/chargen`. Use the currently cleared
GotA preset parts and Quaternius animations. Do not carry over CtA's Layer Lab
Hero Core geometry, Tiny Hero Duo animation clips, or old rendered portraits.
Do not import all chargen assets indiscriminately: its directory license still
lists exceptions for legacy animations, imported and unresolved eyes, and mixed
source files. GotA's selected asset path is the reuse starting point.

Replacing the monster lineup must also handle CtA's floor-loot renderer, which
currently draws its old footman monster model for every pickup. The image does
not replace that runtime dependency by itself.
