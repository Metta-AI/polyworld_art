# New Archer card artwork

Created on 2026-09-15 for the approved Sniper, Sharpshooter, and Hail of Arrows concepts. Mode: built-in `image_gen.imagegen`, with independent illustrations and a subsequent reimagining of Sharpshooter. Each image is standalone artwork without frames, text, or icons. Code and card rules were not changed.

## sniper

Saved asset: `art/sniper.png`.

Exact prompt:

```text
Use case: stylized-concept
Asset type: independent fantasy trading-card illustration, landscape 4:3 aspect ratio, ideally 1536 by 1152 pixels.
Style/medium: premium polished painterly storybook fantasy game art. Rich hand-painted materials, stylized dimensional forms, sophisticated atmospheric depth, luminous cinematic lighting, saturated but natural colors. The same enchanted woodland world as a warm amber forest guardian bear and a charming violet-blue magical portal frog. Heroic and magical, not gritty horror, not a photograph, not flat vector art.
Composition constraints: designed to remain readable inside a small card illustration aperture. Strong clear focal subject and silhouette, softened supporting background, keep essential face, hands, weapon and action in the central 85 percent with modest breathing room for cropping.
Output constraints: ONE full-bleed opaque standalone illustration. Artwork only. No text, letters, numbers, card frame, border, panels, icons, badges, UI, logo or watermark. No guns or modern military equipment.
Primary request: Paint the fantasy creature card Sniper: one hooded forest archer concealed among ancient branches, carefully aiming a longbow for a precise distant shot.
Scene/backdrop: an ancient enchanted emerald forest, layered moss-covered boughs, hanging lichen and deep ferns, shafts of cool light through distant mist.
Subject: one lean adult woodland ranger in a dark moss-green hood and supple worn leather bracers, focused expressive eyes visible beneath the hood, face and drawn bow clearly readable rather than lost in shadow. A medium-close three-quarter side view of the ranger perched steadily on a broad mossy branch. The bow arm is extended; the drawing hand anchors the string beside the cheek with one straight wooden arrow correctly nocked. Anatomically convincing hands, coherent longbow and bowstring geometry.
Composition: calm, tightly controlled horizontal aiming pose, archer and longbow dominate the image. Nearby leaves frame rather than obscure the face and weapon. Keep the arrow's shaft continuous and straight.
Lighting/mood: patient, watchful, concealed skill. Cool emerald, teal and silver-blue palette, soft silver rim light on the hood and arrowhead, a restrained warm accent in the face. Distinguish this quiet green hunter from a brightly lit archer in an action pose.
```

## sharpshooter

Saved asset: `art/sharpshooter.png`.

Reimagined after the user requested an image completely different from Sniper. Built-in image editing replaced the character, weapon, composition, palette and setting. The first illustration remains in the built-in generated image directory as `exec-f767500f-3f62-4abe-a869-d906f0d0da6c.png`.

Exact final prompt:

```text
Use case: style-transfer
Asset type: standalone fantasy trading-card illustration, landscape 4:3, matching the supplied image's dimensions.
Input image: the current Sharpshooter illustration, an edit target. The user wants a COMPLETELY DIFFERENT image because it looks too similar to the hooded longbow Sniper card. Retain only the polished painterly fantasy medium, the production quality and the 4:3 aspect ratio. Completely replace the character, pose, weapon, composition, palette and setting.
Primary request: Reimagine Sharpshooter as a powerful, stocky DWARVEN CROSSBOW MARKSMAN on a ruined stone battlement.
Subject: one adult dwarf with a broad expressive face, a thick copper-red beard in two short braids, determined bright eyes, sturdy dark leather armor with brushed bronze plates, and a bold oxblood-red half-cloak. No hood. No silver hair. A wide, confident braced stance behind a chipped stone parapet. One heavy, beautifully crafted wooden and bronze fantasy crossbow is shouldered and aimed slightly past the viewer; a single ivory-gold charged bolt rests along its top rail. Both hands grip the weapon convincingly, the rear hand at the stock/trigger and the front hand supporting the fore-end from below. A coherent crossbow with horizontally spreading bow limbs, a clearly connected taut string and one bolt. No gun parts or modern rifle scope.
Composition: a near-FRONTAL low three-quarter view. The dwarf's broad shoulders and red cloak create a large compact triangular silhouette, while the horizontal crossbow limbs form a bold shape across the lower middle. The full crossbow and the dwarf's expressive face are the main readable focal points, all within the central 85 percent. Make this immediately distinct from a slim archer pulling a vertical longbow in side profile. One character only.
Scene/backdrop: rain-dark medieval stone battlements high above a misty ravine, weathered ruined towers and dramatic storm-blue sky. Soft distant background, no woodland canopy or sunlit forest clearing. The old magical world should remain consistent with the game's enchanted ruins.
Lighting/mood: cold blue-silver storm light, oxblood red cloth, warm copper beard and bronze accents; a focused small ivory-gold glow at the crossbow bolt lights the hands. Confident, formidable precision with appealing stylized proportions, not grim horror.
Style/medium: premium polished painterly storybook fantasy game art, lush hand-painted material detail, stylized dimensional forms, expressive character design, cinematic atmospheric depth. Not a photograph, not modern military art, not flat vector.
Constraints: full-bleed opaque ARTWORK ONLY. No card frame, border, text, letters, numbers, symbols, stat badges, icons, UI, logo or watermark. No longbow, no silver-haired human, no side-profile drawn-bow pose, no sunset forest. Keep anatomy and the single crossbow mechanically coherent.
```

## hail-of-arrows

Saved asset: `art/hail-of-arrows.png`.

Exact prompt:

```text
Use case: stylized-concept
Asset type: independent fantasy trading-card illustration, landscape 4:3 aspect ratio, ideally 1536 by 1152 pixels.
Style/medium: premium polished painterly storybook fantasy game art. Rich hand-painted materials, stylized dimensional forms, sophisticated atmospheric depth, luminous cinematic lighting, saturated but natural colors. The same enchanted woodland world as a warm amber forest guardian bear and a charming violet-blue magical portal frog. Heroic and magical, not gritty horror, not a photograph, not flat vector art.
Composition constraints: designed to remain readable inside a small card illustration aperture. Strong clear focal subject and silhouette, softened supporting background, keep essential face, hands, weapon and action in the central 85 percent with modest breathing room for cropping.
Output constraints: ONE full-bleed opaque standalone illustration. Artwork only. No text, letters, numbers, card frame, border, panels, icons, badges, UI, logo or watermark. No guns or modern military equipment.
Primary request: Paint the fantasy spell card Hail of Arrows: a sweeping dense volley of physical arrows descending onto enemy minion ranks beneath a dramatic stormy sky.
Scene/backdrop: a forest battlefield clearing beside ancient mossy ruins, deep teal woodland shadows, rolling slate-blue storm clouds parted by pale light. Several distant opposing armored minion silhouettes brace below the incoming volley; they remain small and subordinate.
Subject and composition: the arrows themselves are the dominant readable spell effect. A dramatic diagonal fan of dozens of descending arrows sweeps from high in the image toward enemy ranks in the lower middle. Three or four larger foreground arrows show beautifully readable straight wooden shafts, feather fletching at the rear and sharp metal broadheads at the descending front. Many smaller arrows recede through the mist to suggest a coordinated rain of arrows. Consistent direction and perspective, crisp foreground shafts, luminous pale-gold streaks only as restrained motion accents. Arrows strike earth and shields with a few sparks and leaves, no gore. Keep the central volley clear and iconic at small card size.
Lighting/mood: dramatic storm-blue and deep emerald background, silver-gold glints along the descending arrows, pale shafts of light through cloud and mist, force and coordinated precision. This is a rain of arrows, not lightning, fireballs or abstract glowing needles. No prominent archer or hero in the foreground.
```
