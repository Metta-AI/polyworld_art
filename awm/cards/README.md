# Card artwork

All face components remain independently editable:

- `art/`: standalone illustrations; filenames use lowercase card names with
  spaces replaced by hyphens (for example, `hail-of-arrows.png`).
- `archive/`: superseded illustrations retained for reference, outside the
  runtime artwork directory.
- `frames/`: 600 × 850 SVG frames with transparent illustration apertures.
- `icons/`: energy, power, toughness, and arcane symbol SVG images.
- `fonts/`: bundled Grenze fonts and their SIL Open Font License.
- `previews/`: generated final compositions, never gameplay data. Every base
  card has an individual 600 × 850 PNG. `cards.png` shows the complete set in
  five columns and eight rows, with each card displayed at 300 × 425. Separate
  `back.png` and `bear-damaged.png` previews demonstrate the reverse and live
  damage display.

All 39 cards in `baseCards` have original illustrations:

- Class level-up trinkets: Archer, Warrior, Mage.
- Archers: Bolt, Sniper, Sharpshooter, Ambusher, Assassin, Reload, Overcharge,
  Explode, Hail of Arrows, Wildfire, Post, Gift.
- Warriors: Bear, Swords, Shields, Duel, Tactician, Banner, Pillage,
  Footsoldier, Commander, Rally.
- Mages: Bouncer, Ooze, Spirit, Oozification, Plan, Study, Summon Primordial,
  Primordial, Bubble, Bubble Shield, Morphosis Chamber, Overwork, Burnout,
  Control.

The exact generation prompts are preserved in `PROMPTS.md` (Bear, Bouncer,
Bolt), `PROMPTS-archer.md` (remaining Archers),
`PROMPTS-warrior-additions.md` (Swords, Shields, Duel, Tactician, Footsoldier),
`PROMPTS-commander-ooze.md` (Commander, Rally, Ooze, Oozification),
`PROMPTS-mage-additions.md` (Plan, Study, Primordial, Bubble, Bubble Shield),
`PROMPTS-summon-primordial.md` (Summon Primordial, using the existing Primordial
illustration as its character and style reference),
`PROMPTS-october-additions.md` (Ambusher, Assassin, Reload, Overcharge, Explode,
Wildfire, Banner, Pillage, Spirit),
`PROMPTS-class-and-mage-additions.md` (Archer, Warrior, Mage, Morphosis Chamber,
original Overwork, Control), `PROMPTS-post.md` (Post),
`PROMPTS-overwork-burnout.md` (Overwork's bubble removal and its quiet,
depleted Burnout companion), and `PROMPTS-gift.md` (Gift).
The original Overwork image is retained in
`archive/overwork-2026-10-14.png`. Each
illustration was generated separately using the built-in image generation
tool and visually inspected before being added to the project.

`cardfaces.nim` layers illustration, frame, symbols, and live card text. Rules
come from the card's rules; current toughness can override the printed
value and uses a warm red color when damaged. Spells have no creature stats.
The game may cache the resulting face in an atlas for efficient drawing.

Cards use a 546 × 417 illustration aperture at (27, 113); center the subject in
a landscape image. New cards without a matching illustration display the
separate `art/unknown.svg` placeholder. Names and rules shrink to their safe
areas as needed. Font files are local, so card rendering works offline.

SVG gradients live directly below the root SVG element because the bundled
Pixie SVG parser skips `defs`. Gradients on strokes are avoided for the same
renderer compatibility. SVG assets can still be edited in standard tools.

Regenerate all individual faces, the complete contact sheet, and the two
additional previews from the AWM project root (`games/awm`):

```sh
nim c -r --out:/tmp/awm-render-cards tools/render_cards.nim
```

The renderer checks that every base card has a matching PNG before rendering;
missing artwork stops the command with the card name and expected path.
