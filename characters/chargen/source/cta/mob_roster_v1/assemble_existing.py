"""Select existing chargen parts without creating or modifying any models."""

import copy
import hashlib
import json
from pathlib import Path

Root = Path(__file__).resolve().parents[3]
Output = Path(__file__).resolve().parent
Manifest = json.loads((Root / "manifest.json").read_text())
Presets = {entry["name"]: entry for entry in Manifest["presets"]}
Categories = {entry["key"]: entry for entry in Manifest["categories"]}
Items = {}
Sources = set()
for category, entry in Categories.items():
    for path in sorted((Root / entry["directory"]).glob("*.json")):
        item = json.loads(path.read_text())
        Items[category, item["name"]] = (item, path)


def rgb(value):
    """Convert a hex color to the existing runtime's normalized tint format."""
    return [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def outfit(base=None, **changes):
    """Copy an existing preset or choose explicit defaults for every slot."""
    if base:
        preset = copy.deepcopy(Presets[base])
    else:
        preset = dict(name="", group="CTA previews", pose="A_TPose", skin=10,
                      hairColor="Jet black", pupilColor="Amber", hatColor="Brown")
        defaults = {name: "None" for name in Categories}
        defaults.update(Body="Gota base", Face="Base", Nose="Tiny",
                        Eyes="Monster 11 Undead", Mouth="Evil 07 Broken teeth",
                        Brow="08 Stern", Ears="Round")
        preset["parts"] = [dict(category=k, item=v) for k, v in defaults.items()]
    slots = {part["category"]: part for part in preset["parts"]}
    for name, choice in changes.items():
        category = name.replace("_", " ")
        if isinstance(choice, tuple):
            slots[category] = dict(category=category, item=choice[0], rgb=rgb(choice[1]))
        else:
            slots[category] = dict(category=category, item=choice)
    preset["parts"] = list(slots.values())
    return preset


def mob(name, family, rank, preset, weapons, missing):
    """Record a preview using only existing items and a runtime skin tint."""
    preset.update(name=name, group="CTA previews", pose="A_TPose")
    tint = {"Undead": "C9B48B", "Orcs": "72A63B",
            "Vampires": "A779C8", "Demons": "D94332"}[family]
    return dict(slug=name.lower().replace(" ", "_"), family=family,
                rank=rank, scale=[0.70, 0.90, 1.10, 1.40][rank],
                skinRgb=rgb(tint), weapons=weapons, preset=preset, missing=missing)


entries = [
    mob("Dustling", "Undead", 0, outfit(
        Headgear="Gnome folded", Chest=("01 Linen tunic", "68513B"),
        Leg=("Gnome shorts", "493C32"), Foot="13 Strapped ankle boots",
        Belt="Simple leather belt", Right_hand="Demon Hunter dagger"),
        "Dagger", ["Torn sack tunic", "Rope belt", "Ankle wraps", "Rag cap"]),
    mob("Grave Stalker", "Undead", 1, outfit(
        "Crossbowman", Eyes="Monster 11 Undead", Mouth="Evil 08 Undead snarl",
        Brow="08 Stern", Hair="None", Beard="None"),
        "Crossbow", ["Frayed hood", "Shredded short cape", "Distressed leather"]),
    mob("Crypt Acolyte", "Undead", 2, outfit(
        "Lich", Eyes="Monster 12 Shadow wraith", Mouth="Evil 05 Sewn shut",
        Brow="03 Focused"),
        "Lich staff + orb", ["Torn teal robe", "Plain ragged hood", "Bone clasp"]),
    mob("Barrow Warden", "Undead", 3, outfit(
        "Death Knight", Eyes="Monster 11 Undead", Mouth="Evil 08 Undead snarl",
        Brow="08 Stern"),
        "Sword + shield", ["Rusted armor", "Tombstone pauldrons", "Broken circlet"]),
    mob("Bog Runt", "Orcs", 0, outfit(
        Eyes="Monster 02 Feral cat", Mouth="Evil 09 Orc sneer", Ears="Elf",
        Hair="03 Flat top", Chest=("05 Ochre tunic", "81633B"),
        Leg=("Gnome shorts", "493C29"), Foot="13 Strapped ankle boots",
        Belt="Simple leather belt", Right_hand="Berserker axe"),
        "Axe", ["Patchwork jerkin", "Rope belt", "Short mohawk"]),
    mob("Tusk Raider", "Orcs", 1, outfit(
        "Berserker", Eyes="Monster 14 Berserk beast", Mouth="Evil 10 Orc roar",
        Ears="Elf", Hair="05 Twist crop", Beard="None", Headgear="None"),
        "Twin axes", ["Single iron pauldron", "Leather battle kilt", "Tribal bracers"]),
    mob("Mire Shaman", "Orcs", 2, outfit(
        "Druid Warden", Eyes="Monster 07 Cursed goat", Mouth="Evil 09 Orc sneer",
        Hair="None", Beard="None", Headgear="Gnome feather"),
        "Druid staff + orb", ["Bone-bead collar", "Feather headband", "Ragged shaman robe"]),
    mob("Ironhide Chief", "Orcs", 3, outfit(
        "Death Knight", Eyes="Monster 14 Berserk beast", Mouth="Evil 10 Orc roar",
        Ears="Elf", Hair="08 Braided bun", Headgear="None",
        Right_hand="Berserker axe"),
        "Axe + shield", ["Black iron tribal armor", "Fur collar", "Studded belt"]),
    mob("Dusk Thrall", "Vampires", 0, outfit(
        Eyes="08 Sly", Mouth="Evil 13 Vampire smirk", Ears="Elf",
        Hair="12 Wolf cut", Chest=("08 Plum wrap tunic", "443549"),
        Leg=("12 Cuffed charcoal trousers", "252535"),
        Foot="13 Strapped ankle boots", Belt="Simple leather belt",
        Right_hand="Demon Hunter dagger"),
        "Dagger", ["Servant vest", "Rolled sleeves", "Simple shoes"]),
    mob("Velvet Stalker", "Vampires", 1, outfit(
        Eyes="10 Sharp", Mouth="Evil 14 Vampire grin", Ears="Elf",
        Hair="01 French crop", Chest=("Gnome tucked shirt", "454255"),
        Jacket=("Gnome long coat", "203346"),
        Leg=("12 Cuffed charcoal trousers", "222736"),
        Foot="15 Tall leather boots", Belt="Gota Crossbowman belt",
        Left_hand="Demon Hunter dagger", Right_hand="Demon Hunter dagger"),
        "Twin daggers", ["Fitted split-tail coat", "High narrow collar"]),
    mob("Blood Cantor", "Vampires", 2, outfit(
        "Warlock", Eyes="14 Angular", Mouth="Evil 15 Vampire hiss",
        Ears="Elf", Headgear="None", Hair="12 Wolf cut"),
        "Warlock staff + censer", ["Black shoulder mantle", "Silver trim", "Fang brooch"]),
    mob("Dread Count", "Vampires", 3, outfit(
        "Hades", Eyes="14 Angular", Mouth="Evil 14 Vampire grin",
        Ears="Elf", Beard="None", Hair="Gota Hades swept hair",
        Right_hand="Death Knight sword",
        Left_hand="Lich orb"),
        "Sword + orb", ["Bat-shaped high collar", "Silver coronet", "Silver armor trim",
                        "White swept hair compatible with the crown"]),
    mob("Cinder Imp", "Demons", 0, outfit(
        Eyes="Monster 09 Demon", Mouth="Evil 16 Demon grin", Ears="Elf",
        Hair="Gota Demon Hunter spiky hair", Chest=("04 Red work shirt", "29242A"),
        Leg=("Gnome shorts", "362C2A"), Foot="13 Strapped ankle boots",
        Belt="Simple leather belt", Right_hand="Demon Hunter dagger"),
        "Dagger", ["Separate small horns", "Cropped vest", "Ragged shorts", "Foot wraps"]),
    mob("Ash Reaver", "Demons", 1, outfit(
        "Demon Hunter", Eyes="Monster 09 Demon", Mouth="Evil 16 Demon grin",
        Ears="Elf", Headgear="None", Leg="Gota Berserker fur kilt"),
        "Twin daggers", ["Separate swept horns", "Charcoal pauldrons", "Dark battle skirt"]),
    mob("Ember Hexer", "Demons", 2, outfit(
        "Warlock", Eyes="Monster 09 Demon", Mouth="Evil 16 Demon grin",
        Brow="08 Stern"),
        "Warlock staff + censer", ["Charcoal and ember robe variant"]),
    mob("Infernal Duke", "Demons", 3, outfit(
        "Hades", Eyes="Monster 09 Demon", Mouth="Evil 16 Demon grin",
        Ears="None", Hair="None", Beard="None", Headgear="Gota Warlock horned hood"),
        "Bident + soul orb", ["Separate great horns", "Bronze-edged obsidian armor"]),
]

for entry in entries:
    preset = entry["preset"]
    preset["hairColor"] = "White" if preset["name"] == "Blood Cantor" else "Jet black"
    preset["pupilColor"] = "Red" if entry["family"] == "Vampires" else "Amber"
    preset["hatColor"] = "Brown" if entry["family"] == "Undead" else "Green"

heroes = []
for role, name, weapons in [
    ("Fighter", "Vanguard Knight", "Sword + shield"),
    ("Wizard", "Arcanist", "Staff + arcane orbs"),
    ("Rogue", "Ranger", "Bow + arrow + quiver"),
    ("Cleric", "Druid Warden", "Staff + nature orb"),
]:
    heroes.append(dict(slug=name.lower().replace(" ", "_"), family=role,
                       rank=0, scale=1.0, skinRgb=[], weapons=weapons,
                       preset=copy.deepcopy(Presets[name]), missing=[]))

for entry in entries + heroes:
    assert 0.0 < entry["scale"] <= 1.4
    has_weapon = False
    for part in entry["preset"]["parts"]:
        if part["item"] == "None":
            continue
        item, path = Items[part["category"], part["item"]]
        Sources.add(path.relative_to(Root).as_posix())
        for source in item["files"]:
            Sources.add(source)
        for key in ["texture", "pupilMask"]:
            if item.get(key):
                Sources.add(item[key])
        if part["category"] in ["Left hand", "Right hand"]:
            has_weapon = True
        assert not any(p.startswith(("eyes/original2.", "eyes/neutral.",
                                     "eyes/happy.", "eyes/angry."))
                       for p in item["files"])
    assert has_weapon, entry["slug"]

for clip in Manifest["clips"]:
    if clip["name"] in ["A_TPose", "Walk_Loop"]:
        assert clip["kind"] == "universal"
        Sources.add(clip["file"])
Sources.add(Manifest["rig"])
Sources.add("manifest.json")
for key in ["skinPalette", "hairPalette", "pupilPalette", "hatPalette"]:
    if Manifest.get(key):
        Sources.add(Manifest[key])

inventory = dict(entries=entries, heroes=heroes)
(Output / "existing_presets.json").write_text(json.dumps(inventory, indent=2) + "\n")
hashes = {name: hashlib.sha256((Root / name).read_bytes()).hexdigest()
          for name in sorted(Sources)}
(Output / "runtime/source_hashes.json").write_text(json.dumps(hashes, indent=2) + "\n")
print(f"Selected {len(entries)} mobs and {len(heroes)} heroes from {len(Sources)} existing source files.")
