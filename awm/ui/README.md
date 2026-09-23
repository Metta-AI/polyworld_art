# AWM interface

`hud/` contains independently editable SVG assets for the screen-space UI.
`awmhud.nim` lays out the player panels, class crests, life hearts, energy,
turn plaque and action buttons. The 3D scene, camera and world objects are
independent of this interface.

- Archer uses a bow, Warrior a sword, and Mage a crystal staff.
- Life is printed inside a crimson heart.
- Energy always shows its exact current/total value. Ten slots distinguish
  available energy, spent capacity, and future capacity. Above ten capacity,
  only the numeric meter is shown.
- Transparent cyan glow sprites breathe over four seconds using sine-driven
  alpha. The main counter and available dots glow; spent/locked dots stay dim.
- The opponent's panel background is flipped horizontally, and its readable
  contents run energy, life, name/class, then class crest.
- The engraved turn plaque is twice its original size (728 × 224 logical
  pixels). Status text sits beneath it; all helper dialogs share a lower anchor.
- Layered brass bevels, engraved flourishes, dark inset panels and a warm gold
  primary action bring the interface closer to the approved war-room proposal.
- Grenze headings match the cards; Rubik keeps small labels readable.
- The inspector displays the card itself and any live stat overlays.
- End Turn supports click and Enter, with the same availability checks.
  Enter retains its original purpose in layout-tuning builds.
- Pile counters hide when covered by the inspector, avoiding partial labels.

The SVG renderer requires root-level, user-space linear gradients. No remote
fonts, images, or services are needed at runtime. The browser build packages
only `hud/`, excluding the design proposals and preview images.

Generate screenshots of all three classes, full/empty energy meters, numeric
overflow, active/inactive controls, helper dialogs, and four window sizes.
The last two captures hold the layout still at the glow's brightest and
dimmest phases:

```sh
nim c -r --out:build/render-hud tools/render_hud.nim
```

Screenshots go to `build/ui-review/`. `previews/game-hud.png` shows targeting
in the native game; `previews/mage-hud.png` shows the Mage discard dialog and
new artwork. `proposals/war-room-v1.png` is the earlier visual proposal;
its environment and table redesign are not part of this UI implementation.
