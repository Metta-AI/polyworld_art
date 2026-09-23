# Archers Warriors Mages asset licenses

AWM uses the following asset families from `awm/`. These notices cover its
current runtime assets and their source records, not every file in
polyworld_art.

| Assets | License and notice |
| --- | --- |
| Card illustrations, VFX sprites and battlefield textures | [Root license](../LICENSE), project-generated AI assets. |
| Card frames, symbols, placeholder art and HUD SVGs | [Root license](../LICENSE), project-authored assets. |
| Generation prompts, recipes and READMEs | [Root license](../LICENSE). |
| Grenze Regular and SemiBold | [SIL OFL 1.1](../awm/cards/fonts/OFL.txt). |
| Rubik Regular and Bold (HUD labels) | [SIL OFL 1.1](../fonts/OFL-Rubik.txt). |

The complete [CC0 legal text](../LICENSE) is included.

## Creation

Each card illustration and VFX sprite was generated separately with the
built-in image generation tool, visually inspected and copied without edits.
The exact prompts are kept beside the images in `awm/cards/PROMPTS*.md` and
`awm/vfx/PROMPTS*.md`. The regenerated Sharpshooter used the earlier project
Sharpshooter illustration as its only input image.

The SVG frames, symbols, `unknown.svg` placeholder and HUD were authored in
the project. They embed no images, fonts or external references.

`awm/battlefield/source/rock-normal.png` was generated with the built-in
image generation tool from the prompt in `awm/battlefield/source/prompt.txt`.
A stone normal map obtained from Adobe was supplied only as a visual
structure reference. It is not included, and the author confirmed on
2026-09-23 that the generated normal is a completely different image.
The three textures in `awm/battlefield/textures/` were prepared from that
source and procedural grain by `examples/awm/tools/render_stone_normals.nim`
in Polyworld.

The Grenze fonts are the original, unmodified files from
https://github.com/Omnibus-Type/Grenze. Their SHA-256 digests matched the
upstream `fonts/ttf` files on 2026-09-23.

## Excluded

Generated previews, contact sheets, videos and the war-room design proposal
were not imported. The proposal used a game screenshot containing former
Unity character models. Three unreferenced loose PNGs in the former
`polyworld_data/awm/` folder were also left out. The copied READMEs still
describe those previews; regenerate them locally with the listed tools.
