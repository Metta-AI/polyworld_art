# Prism Shatter textures

Generated with the built-in imagegen tool. These grayscale sprites are
uploaded once, then tinted and animated by the GPU particle renderer.
Black texels are masked before blending. Reference and preview images
are stored in `polyworld/tmp/fx/`.

## shard.png

```text
Use case: stylized-concept
Asset type: single grayscale faceted crystal shard sprite for a Prism Shatter GPU particle effect.
Primary request: a tall irregular sharp magical glass shard, a pointed triangular prism with bold visible polygon facets.
Composition: square texture, centered upright narrow crystal; long needle point at the top, pointed asymmetric bottom at bottom center; wider angular shoulder around lower middle. Three or four large flat facets in distinct gray values, razor-thin bright white edges, one brilliant white triangular facet. 10 percent pure black margins on all sides.
Style: hand-painted anime magic impact, crisp geometric shapes, translucent angular glass.
Constraints: grayscale only, solid pure black background, no ground, no shadow, no rocks, no crystal cluster, no surrounding fragments, no text or scene.
```

## trail.png

```text
Use case: stylized-concept
Asset type: grayscale projectile trail texture for the Prism Shatter spell.
Primary request: one long broken zigzag ribbon assembled from sharp connected triangular glass facets, like an angular comet tail.
Composition: square texture, vertical; thin tapering fragments at the upper left, alternating jagged overlapping triangles descending toward a brilliant spear tip at the bottom center. Dark gray translucent triangle faces, pale gray planes, thin white outlines, several white highlights. Keep all artwork within 10 percent black margins.
Style: graphic anime magical glass effect, clean polygon edges, no soft smoke.
Constraints: strictly grayscale on uniform pure black background; one standalone texture, no orb, no ground, no explosion, no text, no grid, no scenery.
```

## fracture.png

```text
Use case: stylized-concept
Asset type: grayscale top-down ground impact texture for Prism Shatter.
Primary request: a flat radial starburst of shattered glass cracks and scattered triangular slivers on pure black.
Composition: square texture, viewed straight down without perspective; centered circular arrangement of irregular interlocking angular fractures and long narrow triangular shards radiating outwards. Mostly hollow black spaces between bright thin crack edges, a few pale gray translucent triangle faces. Hollow small center and ample black margin around the perimeter.
Style: clean graphic anime magic floor sigil made of broken glass, irregular and asymmetric, distinct large facets.
Constraints: grayscale only on pure black, no terrain, no realistic stone, no dust, no text, no runes, no symbols, no scene. Isolated reusable particle sprite.
```
