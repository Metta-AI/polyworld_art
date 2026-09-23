# LvD cloth symbols

`unit-symbols.png` is original project artwork generated with the built-in
image generation tool on 2026-09-22. It is covered by the repository's
root CC0 dedication. The user supplied a cloth banner as a composition
reference; the sheet uses newly generated cloth and symbols.

The sheet has three columns and three rows, read left to right:

| Peon: pickaxe | Swordsman: sword | Archer: bow |
| --- | --- | --- |
| Mage: crystal staff | Armored knight: helmet and shield | Bomber: bomb |
| Cleric: healing sun | Fire elemental: flame | Spare: plain cloth |

The renderer crops each cell, removes the thin dividing edge, and makes
256 pixel grayscale sprites. The UI multiplies each sprite by the owning
team's skin color at draw time. Selection, training, queues, and statistics
all use the same source. The spare cell is not packed into the HUD atlas.

The symbols identify roles. They do not supply the missing pickaxe model,
bomb model, or their animations.

The exact generation prompt is saved in `unit-symbols-prompt.txt`.
