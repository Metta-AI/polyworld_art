# Reusable character prompt patterns

Use the imagegen skill/tool for these raster assets. Inspect local references
before passing them as inputs. Preserve exact prompts and approved outputs in
the asset source folder. These patterns summarize what worked; adapt the style
and count to the request instead of forcing every task into a 16-item grid.

## Body reference

> A modeling reference of the approved stylized fantasy humanoid. Show front,
> side, and back at the same orthographic scale and neutral A or T pose. Keep
> the same head/body proportions in every view, readable wrist/ankle junctions,
> downward mitten-hand curl, and simple large forms. Neutral background and
> consistent lighting. No clothes or props unless requested. This is a shape
> reference, not a finished game mesh. Preserve the reference's silhouette.

Do not specify both A and T pose in a real generation; choose the useful one.
Use a fourth three-quarter or top view when it will resolve shape ambiguity.

## Hair, beard, and clothing collections

> Exactly four rows and four columns: sixteen distinct styles. Each cell
> contains the same style from the front and back, with consistent scale,
> orientation, lighting, and padding. Simple stylized low-poly fantasy forms
> suitable for modeling. No extra row, duplicate color-only variations, text,
> labels, cell borders, or unrelated accessories.

For hair, require real back mass, parting, and silhouette. For beards, specify
cheek coverage, chin point, moustache shape, and mouth clearance. For clothing,
start with simple medieval shirts, trousers/shorts, and boots before adding
lapels, belts, suspenders, or pockets. Show clothing as separate items. A
front/back item sheet should not conceal geometry behind a mannequin.

## Gota clothing and equipment

> Using the approved character image, show each requested clothing module as
> an isolated front/back pair at matching scale. Preserve its distinctive
> silhouette, opening, trim and colors. Simple low-poly geometry with smooth
> rounded surfaces where appropriate, solid-color materials, no painted
> texture, tiny engraving or photorealistic detail. Keep rear and side volume
> coherent. No body, eyes, new rig, hands or weapons unless listed as items.

For a complete hero roster, use five columns and two rows when requested,
with an explicit name-to-cell mapping. For Zeus or Hades, list the separate
crown, hair, beard, torso, belt, cape, legs and boots needed for the actual
modular build. Do not let a decorative sheet invent a new head or skeleton.

> One simple equipment reference sheet in five columns and two rows, one
> named hero's set per cell. Solid-color low-poly forms that retain the main
> curves and proportions of the approved concept. One view for symmetrical
> swords, bows, staffs, knives and axes. Show each shield's front and its rear
> handle/straps. Show the crossbow from the top with its string and from the
> bottom without the string. Quivers are separate items. No characters or
> hands, duplicate paired weapons, tiny filigree or painted textures.

Replace the generic hero mapping and item list with the actual request.
Front/back symmetry is a per-item decision, not a rule for every fantasy
weapon. Specify the latest corrections, such as a fully covered helmet back
or a medieval crossbow, when the supplied image contradicts them. These are
concept prompts; use exported geometry renders for the subsequent comparison.

## Varied eyes with tintable irises

> A 4x4 sheet of sixteen complete eye pairs for small stylized game characters.
> White sclera directly meets a flat hot-pink background. No enclosing dark
> outline around the sides or bottom. Some designs have a separate dark upper
> eyelid accent. Mix friendly, focused, curious, sleepy, and angular shapes.
> Use a few chunky neutral grayscale iris values, subtle gradients on selected
> designs, and white highlights. Preserve a coherent style, but make the
> expressions and silhouettes different rather than just changing colors.
> Equal gutters, no labels, no face, no skin patches, no grid lines.

For the fully tintable pupil/iris variant, specify gray centers as well. For
the kind gnome variant, explicitly keep the center black and mask only the
gray iris. A gray source is not a mask: make and inspect the mask separately.

## One kind gnome pair

> Exactly one friendly eye pair on true transparency. Clean white sclera,
> simple round black pupils, one small white highlight each, and a short
> gently curved black streak only along the top. A restrained neutral gray
> iris gradient, darker above and lighter below. No outline on the sides or
> bottom, no fibers, fine rings, facets, excess gleams, or extra face parts.

The successful refinement preserved the existing pair and changed only the
iris gradient. More detail did not make these eyes kinder. One shared pair
was sufficient for all nine gnomes.

## Mouths and eyebrows

> A clean 4x4 sheet of sixteen distinct stylized mouth expressions on a flat
> bright-pink background, one mouth per cell. Small-game readability, simple
> shapes, deliberate tooth placement, consistent scale, generous gutters.
> No face, skin surround, labels, frames, or extra rows.

For evil variants, request the actual set: snarls, open/closed fangs, sewn
mouths, broken teeth, orc tusks, and vampire smiles. Inspect every tooth before
cutting. Make a targeted single-cell edit to remove an extra tooth while
preserving neighboring art. For brows, use white eyebrow pairs on pink so the
runtime can tint them with hair color.

## Transparent extraction of an approved sheet

> Remove only the pink background from this exact approved sheet. Return real
> RGBA transparency. Preserve canvas, count, positions, scale, every interior
> color, grayscale shading, whites, highlights, and silhouette. No redraw,
> simplification, movement, new outlines, or checkerboard painting. Clean the
> pink fringe while keeping all opaque artwork intact.

Inspect the alpha channel and image dimensions. Confirm foreground whites are
opaque. Keep approved source resolution until cutting; use deterministic
resampling only for the final game asset. A drawn checkerboard is not alpha.

## Shared death expression

> Exactly one pair of bold near-black cartoon X eyes on genuine transparency.
> Two clean crossing diagonal strokes per eye, slightly rounded ends, equal
> scale and height, natural spacing, generous empty margins. No whites,
> circles, brows, irises, shading, face, shadow, text, or other objects.

The generated wide source was resized to 384x192 for Chargen. Its projection
omits unused transparent margins to stay on the curved face. The expression
has no tint mask and remains a selectable option, not a replacement for the
character defaults.

## A useful visual judge request

> Review this exported character part against the approved reference. Compare
> the supplied front/back/side views and the posed renders. Identify specific
> silhouette, fit, shading, attachment, clipping, or excessive geometry issues.
> Separate material defects from acceptable small differences. Give concrete
> correction targets and state what the supplied views cannot establish.

Include the user's corrections to the source image. For headgear, explicitly
ask about brow height, eye clearance, mouth-side steps, face depth, rear
coverage, hair overlap and cloth drape. For equipment, include the specified
animation/frame and ask whether the grip stays fixed and the blade follows
the intended strike from front, side and top. Do not use a judge's earlier
pass to dismiss a newly demonstrated closeup defect.

For before/after optimization, add the actual rendered triangle counts and
matched camera/lighting/frame information. Do not describe the intended answer
or suggest the judge should pass it. Use per-part judges when requested for a
large modeling collection, with isolated file ownership for parallel builders.
