# Star Mana textures

Generated with the built-in imagegen tool for the FX experiment. These
immutable grayscale textures are tinted and animated on the GPU. Their
black backgrounds are removed by the fragment shader before blending.

The reference and renderer previews are in `polyworld/tmp/fx/`.

## ribbon.png

```text
Use case: stylized-concept
Asset type: single grayscale game VFX particle texture for additive blending.
Primary request: a clean flowing S-shaped magic ribbon, white and pale gray on pure black, inspired by a sweeping Star Mana projectile trail.
Composition: square texture; one tall continuous tapering ribbon, tip at bottom center, widens and curls to the left in the lower middle, reverses smoothly to the right in the upper middle, then thins to a hairline at the top left. Two fine companion strands hugging the main curve. Generous black margin on every edge.
Style: hand-painted anime game effects; bold smooth graphic silhouette, sharp elegant tapered tips, a few translucent gray layered strokes, minimal glow.
Constraints: grayscale only; uniform pure black background, no colored pixels, no stars, no orb, no text, no panels, no borders. An isolated reusable texture, not a full scene.
```

## orbit.png

```text
Use case: stylized-concept
Asset type: single grayscale game VFX particle texture for additive blending.
Primary request: one face-on circular sweeping orbital energy ribbon on pure black for a Star Mana spell.
Composition: square texture; centered circle viewed straight on, not a flattened ellipse. One broad white crescent sweep about two thirds of a circle, tapering into fine sharp ends, with two thin gray-white near-concentric trailing arcs. Large completely black hollow center (at least 65 percent of outer diameter), and ample black margin around all edges.
Style: clean hand-painted anime magic FX, smooth confident brush curves, irregular varying thickness, sharp tapered ends, almost no bloom.
Constraints: grayscale only, no glowing ball, no star, no sparks, no dust, no text, no full scene, no grid, no perspective. Pure black background. The result will be rotated and stretched by a particle shader.
```

## flare.png

```text
Use case: stylized-concept
Asset type: grayscale Star Mana core sprite for a GPU particle system.
Primary request: one extremely sharp elongated four-point magical star flash on solid pure black.
Composition: square texture, centered brilliant white four-point star with a broad small diamond waist, gently concave sides narrowing to needle points. Very long thin upward ray reaching close to the top margin; medium downward ray; short symmetrical left and right rays. White solid core, restrained faint gray glow only immediately around the center, large black negative space.
Style: graphic hand-painted anime impact flash, elegant pointed silhouette, clean edges.
Constraints: grayscale only, isolated single sprite, keep all four points inside the image with 8 percent black border. No lens rings, no extra stars, no nebula, no text, no scene.
```

## dust.png

```text
Use case: stylized-concept
Asset type: grayscale game VFX sprite for a sweeping dust plume.
Primary request: one stylized low horizontal curl of impact dust, white and gray on pure black, to be tinted warm amber by a particle shader.
Composition: square canvas. A low broad windswept crescent plume centered in the lower middle; left end lifts into two smooth pointed wisps; right end sweeps upward in a larger curling tip. Broad layered gray brush shapes with white upper rims and soft fading underside, the upper half mostly empty black, generous border.
Style: painted anime game spell effect, simplified bold billowing smoke silhouette, smooth flowing layered strokes and tapered ends.
Constraints: grayscale only, pure black background; no photorealistic cloud detail, no sparks, no core, no ground plane, no scene, no text or grid. Single separate particle texture.
```
