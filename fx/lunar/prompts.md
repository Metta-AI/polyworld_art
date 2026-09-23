# Lunar Tide textures

Generated with the built-in imagegen tool. These grayscale sprites are
uploaded once, then tinted and animated by the GPU particle renderer.
Black texels are masked before blending. Reference and preview images
are stored in `polyworld/tmp/fx/`.

## wave.png

```text
Use case: stylized-concept
Asset type: grayscale crescent wave sprite for a Lunar Tide particle effect.
Primary request: one broad flowing crescent of liquid moonlight, curving from a pointed lower-left base around the left side into a sweeping crest at the upper right.
Composition: square texture, C-shaped curling water wave with a large hollow black center. Three smooth overlapping translucent gray ribbon layers, brilliant white thin leading rim, sharp tapered tips and a few small attached teardrop-like tips on the crest. Full crescent inside the image with 8 percent black margin.
Style: elegant hand-painted anime water magic, smooth fluid graphic silhouettes, restrained glow, no photorealistic splash noise.
Constraints: grayscale only on pure black; no sphere, no moon, no ground, no separate droplets, no text, no scene. Single reusable VFX sprite.
```

## orb.png

```text
Use case: stylized-concept
Asset type: grayscale central moon orb sprite for a Lunar Tide game spell.
Primary request: a small pearl-like orb of liquid moonlight, with softly swirling pale surface patches and a thin brilliant white luminous circular rim.
Composition: square canvas, one perfectly round centered orb occupying 65 percent width. White upper-left highlight, pale gray and medium-gray crescent patterns that suggest a softly luminous translucent liquid sphere. Subtle confined halo around its circular edge.
Style: hand-painted anime moon magic, pearlescent, simplified fluid shading rather than realistic crater detail.
Constraints: grayscale only, pure black background, no stars, no rings, no crescent beside the orb, no text, no setting or scene.
```

## drop.png

```text
Use case: stylized-concept
Asset type: grayscale floating water droplet sprite for Lunar Tide.
Primary request: one small vertical pear-shaped floating water droplet, perfectly isolated on solid black, rounded bottom and a softly pointed upper end.
Composition: square canvas, droplet centered occupying 35 percent width and 60 percent height. Brilliant white crescent rim on the left, tiny bright highlight at top left, translucent medium-gray internal curved reflection, dark center and a bright little lower rim. Almost no bloom.
Style: polished hand-painted anime magic water, crisp simple luminous silhouette.
Constraints: grayscale only, pure black background, no falling trail, no extra droplets, no ripples, no text, no scenery. Single separate particle texture.
```
