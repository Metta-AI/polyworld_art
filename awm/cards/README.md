# Card artwork

All face components remain independently editable:

- `art/`: standalone illustrations; filenames use lowercase card names with
  spaces replaced by hyphens (for example, `hail-of-arrows.png`).
- `frames/`: 600 × 850 SVG frames with transparent illustration apertures.
- `icons/`: energy, power, toughness, and arcane symbol SVG images.
- `fonts/`: bundled Grenze fonts and their SIL Open Font License.
- `previews/`: generated final compositions, never gameplay data. Every base
  card has an individual 600 × 850 PNG. `cards.png` shows the complete set in
  five columns and four rows, with each card displayed at 300 × 425. Separate
  `back.png` and `bear-damaged.png` previews demonstrate the reverse and live
  damage display.

All 20 cards in `baseCards` have original illustrations:

- Archers: Bolt, Sniper, Sharpshooter, Hail of Arrows.
- Warriors: Bear, Swords, Shields, Duel, Tactician, Footsoldier, Commander, Rally.
- Mages: Bouncer, Ooze, Oozification, Plan, Study, Primordial, Bubble,
  Bubble Shield.

The exact generation prompts are preserved in `PROMPTS.md` (Bear, Bouncer,
Bolt), `PROMPTS-archer.md` (remaining Archers),
`PROMPTS-warrior-additions.md` (Swords, Shields, Duel, Tactician, Footsoldier),
`PROMPTS-commander-ooze.md` (Commander, Rally, Ooze, Oozification), and
`PROMPTS-mage-additions.md` (Plan, Study, Primordial, Bubble, Bubble Shield). Each
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
additional previews from the AWM project root (`examples/awm`):

```sh
nim c -r --out:/tmp/awm-render-cards tools/render_cards.nim
```

The renderer checks that every base card has a matching PNG before rendering;
missing artwork stops the command with the card name and expected path.
