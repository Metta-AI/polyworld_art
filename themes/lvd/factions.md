# LvD faction colors

The eight faction colors match the hex values in the user's reference.
`polyworld/examples/light_vs_dark/factions.nim` defines the palette once
for character skin, cloth badges, health bars, minimap markers, score
labels, and path overlays.

| Player | Faction | Color | Roster value |
| --- | --- | --- | --- |
| 1 | Peter River | #3498DB | PeterRiver |
| 2 | Amethyst | #9B59B6 | Amethyst |
| 3 | Alizarin | #E74C3C | Alizarin |
| 4 | Emerald | #2ECC71 | Emerald |
| 5 | Carrot | #E67E22 | Carrot |
| 6 | Wet Asphalt | #34495E | WetAsphalt |
| 7 | Turquoise | #1ABC9C | Turquoise |
| 8 | Sun Flower | #F1C40F | SunFlower |

The `factions` list in `characters/chargen/lvd.json` selects a color for
each current player. The default is `["PeterRiver", "Amethyst"]`. Any of
the eight values can be selected without changing the shared outfits or
the existing ear and face presets. Matches still have two players.

The fire elemental remains solid orange as requested. Its cloth badge,
health bar, and minimap marker use its owner's faction color.
