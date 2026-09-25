---
name: generating-icons
description: Generate or regenerate Polyworld game icons as centered 128x128 PNGs with matching Markdown descriptions, using the established simple sculpted style, transparent backgrounds, and deterministic finishing tools.
---

# Generating icons

Use this workflow for shared UI, resource, status, map, transport, score,
building, unit, and action icons. Read the existing icon descriptions before
designing a set. Preserve an existing description when only the artwork is
being regenerated.

The imagegen skill/tool creates or restyles the artwork. The scripts under
[`scripts/generating_icons`](scripts/generating_icons) perform deterministic
cutting, background removal, resizing, centering, previews, and validation.
Run the scripts from the `polyworld_art` repository root. They need
ImageMagick 7 as `magick`; the centering tool also needs Nim and Pixie.

## Asset contract

Each published icon has two files with the same snake_case base name:

| File | Contract |
| --- | --- |
| `icons/name.png` | 128x128 RGBA PNG, centered visible content |
| `icons/name.md` | Title, visual description, intended uses, and keywords |

Tintable UI icons are neutral white or grayscale. Use soft light-gray shading
only to describe form; do not encode colored light, green spill, or a gray
background. Resource icons such as gold, wood, food, or other materially
meaningful objects stay in true color unless the request says they are
tintable. All icons use genuine transparent backgrounds.

Keep icon semantics generic. Do not copy names, symbols, silhouettes, or art
from Warcraft, World of Warcraft, Dota, or another game. A fantasy strategy
game can need similar concepts, but the actual design must be original.

## Art direction

The established tintable style is a minimal rounded white 3D sculpture:

- One strong silhouette that remains readable at 32 pixels.
- Broad smooth shapes with softly beveled edges.
- Pale gray ambient shading and no black outlines.
- Usually three to five major shape groups.
- No surface texture, filigree, engraved lines, tiny rivets, or ornamental
  armor unless the description makes one detail essential.
- No frame, badge plate, text, ground plane, cast shadow, or scenery.
- Balanced transparent padding. A maximum visible extent near 104 pixels is a
  useful default on the 128-pixel canvas, not a rule for every silhouette.

Describe both what an icon must contain and what it must omit. For example, a
simple tower prompt should ask for a tapered body and crenelated crown while
forbidding bricks, windows, banners, arrows, and emblems. This is more reliable
than asking only for "less detail."

## Choose the generation route

### Regenerate existing icons

Use the current PNG as the subject reference and an approved simple icon sheet
or icon as the style reference. Use one generation call per distinct icon when
the active imagegen workflow requires separate calls. This keeps the semantic
reference explicit and makes failed icons cheap to retry.

Do not ask the generator to preserve the detailed modeling. Preserve the core
meaning and replace the construction with the fewest broad forms. For related
character markers, make their silhouettes deliberately different. A champion
can be hornless and compact while a boss has exactly two large horns.

### Create a coherent new set

A 4x4 sheet is useful for art direction and for generation tools that reliably
produce exact multi-icon grids. Put one icon in each mathematical cell in
row-major order. Use one scale, camera, material, light direction, and padding
system. Do not add labels, cell borders, frames, or objects crossing cell
boundaries.

If the active imagegen policy requires one call per distinct deliverable, use
the 4x4 sheet as a style reference and generate the final icons individually.
If a generated sheet is approved as the final source, cut and finish it with
`cut_icon_sheet.sh`. The cutter partitions dimensions such as 1254 pixels
without losing the remainder pixels.

## Prompt shape

Use the imagegen skill and include these constraints in each prompt:

```text
Use case: stylized-concept
Asset type: fantasy strategy game UI icon, tintable
Primary request: Regenerate the subject as an extremely simple white icon
matching the supplied clean soft 3D style reference.
Subject: <required broad forms and semantic distinction>
Style/medium: Minimal rounded white 3D clay or plastic, broad smooth shapes,
very slight soft gray shading, strong readable silhouette.
Composition: One centered object, near-front view, square canvas, generous
padding, readable at 32 pixels.
Constraints: Preserve only the core meaning; use the fewest shape groups; no
text, border, badge, floor, cast shadow, watermark, or franchise-specific art.
Avoid: <subject-specific details that made the old icon too busy>.
```

Request genuine transparency first. Inspect the downloaded PNG instead of
trusting the preview. A visible checkerboard may be baked RGB pixels rather
than alpha. Do not try to key a gray checkerboard; regenerate it.

When transparency is unreliable and the subject contains no meaningful green,
request a uniform chroma field across the whole canvas:

```text
Uniform pure chroma key green #00FF00. One flat color with no texture,
gradient, checkerboard, transparency grid, floor, or cast shadow. Keep a clean
separation between the white subject and the green background.
```

The generator may return near-green such as `(18, 240, 14)` rather than exact
`#00FF00`. The finishing script therefore derives alpha from green dominance,
not exact color equality, then removes excess green from edge RGB. Use genuine
alpha or a different matte for an icon that contains green artwork.

## Finish individual icons

`finish_icon.sh` trims at source resolution, scales the visible content once,
places it on a transparent 128x128 canvas, and writes RGBA PNG. It refuses to
overwrite by default.

```sh
iconScripts=skills/scripts/generating_icons

# A generator output that already has correct alpha.
"$iconScripts/finish_icon.sh" --grayscale generated.png icons/name.png

# A white tintable icon generated on chroma green.
"$iconScripts/finish_icon.sh" --green --grayscale \
  generated-green.png icons/name.png

# Preserve meaningful resource colors.
"$iconScripts/finish_icon.sh" --green \
  generated-gold.png icons/gold.png
```

Use `--force` only when replacement is intended. Use `--crop WIDTHxHEIGHT+X+Y`
when tiny detached generator specks cause trim bounds to include empty space.
Inspect connected alpha components before choosing that crop:

```sh
magick generated.png -alpha extract -threshold 3% \
  -define connected-components:verbose=true \
  -connected-components 8 null:
```

The script intentionally performs chroma compositing and grayscale conversion
in separate ImageMagick commands. Combining those operations in one command
zeroed the RGB channels in a real run even though the alpha mask was correct.

## Cut an approved 4x4 sheet

Create a names file with exactly 16 safe snake_case base names in row-major
order, one per line. The cutter writes the final PNGs through
`finish_icon.sh`:

```sh
"$iconScripts/cut_icon_sheet.sh" --green --grayscale \
  generated-sheet.png names.txt tmp/cut-icons
```

Review the cells before publishing. Generation can place an object across a
cell boundary, repeat an icon, or change scale within the sheet; deterministic
cutting cannot repair those semantic failures.

## Center, preview, and verify

Centering measures pixels with alpha at least 8 and translates without
resampling:

```sh
nim check "$iconScripts/center_icons.nim"
nim r -d:release "$iconScripts/center_icons.nim" icons
```

Make a dark contact sheet. Dark review backgrounds expose missing white RGB,
green halos, fake transparency, inconsistent padding, and silhouettes that
collapse at icon size:

```sh
"$iconScripts/contact_sheet.sh" --force tmp/icons-contact.png \
  icons/tower.png icons/shop.png icons/supply.png icons/sell.png
```

Validate dimensions, alpha, centering, matching Markdown, and optional
grayscale tintability:

```sh
"$iconScripts/verify_icons.sh" --grayscale icons/tower.png icons/shop.png
```

Also inspect the actual PNGs at 128x128, not only enlarged previews. Verify
that each concept differs from nearby concepts: a level-up arrow is not a rank
badge, a defensive stance is not a tower, and a house is not a fortress.

## Publish

For a new icon, write a concise Markdown description that names only what is
visibly present, lists reusable game contexts, and ends with searchable
keywords. For a regenerated icon, keep the existing Markdown unchanged unless
the meaning changed or the user requested documentation edits.

Keep source references, prompt text, and generation provenance when the
repository's contribution process requires them. Before committing, confirm
that only intended PNG and Markdown files changed and that unrelated work in
the tree remains untouched.
