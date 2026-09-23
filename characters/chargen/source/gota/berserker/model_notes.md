# Berserker model notes

Builder: `../../scripts/gota_berserker.py`.

The five required independently selectable clothing slots are Foot (brown fur-cuffed boots), Leg (charcoal trousers with separate faceted fur skirt and brown front/back panels), Belt (dark leather band and silver open hexagon buckle), Chest (bare-torso diagonal leather harness and dark wrist cuffs), and Headgear (small gold forehead crest and thin leather band). Hair and beard remain separate selectable parts.

Source reuse:

- `Clothing_16`: fitted folded travel boots, reduced to broad facets and recolored brown/tan, with closed angular fur cuffs added.
- `Clothing_12` and boot-cut sections: fitted charcoal trousers, cropped above the boot cuff with original fitted topology preserved to avoid knee skin poke-through during animation. No duplicate boots belong to this slot.
- `Hair_12`: fitted wolf-cut scalp and locks, reduced and supplemented with closed angular orange-red mane wedges.
- `Beard_09`: tapered wedge beard, shortened and reduced.
- Shared Gota split body with covered lower skin hidden, Head, hands, focused eyes, neutral mouth, heroic brows, and tiny nose.
- New harness, wrist bands and belt follow original body surfaces and retain interpolated weights. Short fur and leather skirt panels follow Hips to avoid twisting between moving legs; cuffs sample shared body bone weights; mane, beard and crest follow the Head bone.

The generated sheet's back harness is corrected in geometry so the front and rear views mirror each other. Its repeated boots in the legs row are intentionally omitted from the actual Leg part. The gold crest uses an ordinary solid material with no glow or image textures.

Final exported visible total: 13,790 triangles including shared body and face. Authoritative final counts and geometry checks are in `verification.json`. Actual-render visual review and runtime animation evidence are recorded separately before acceptance.

The final shared-body integration rebuild retains the same costume geometry. `finalize_gota.py` prepares the hero-local blend with the correct visible Gota body and selected outfit. Runtime front/back, all isolated slots, walk, and crouch captures were regenerated after this rebuild.
