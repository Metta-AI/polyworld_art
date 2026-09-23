# Builder interface

Import helpers from `gota_common`. Define `build(ctx)` returning `(parts, preset)`.
Do not execute the builder at import time. Run it with:

`blender -b --python source/scripts/gota_common.py -- <slug>`

Root is implementing export/render support. Geometry uses source coordinates:
Z up, forward negative Y, existing body and rig bind pose. Do not pose meshes
manually before export. Shared runtime and rendering apply the T pose.

Context fields: `rig`, `collection`, `body`, `slug`, `prefix`, `output`, `preview`,
`library`. Prefix is `Gota_<slug>_`; output is `source/gota/<slug>`.

Helpers:

- `duplicate(ctx, sourcePrefix, suffix, colors=None)` returns a list of copied
  meshes matching exact sourcePrefix and its `_BootCut` sections. Copies keep
  source weights and shape. `colors` is a list of hex colors, per material
  slot. Omitted entries keep the original color. Mesh names use ctx.prefix.
- `mesh(ctx, suffix, vertices, faces, materials, bone=None, weights=None)` creates
  a mesh. Materials is a list of Blender material objects or hex color strings.
  Set `bone='Head'` for rigid hats. Otherwise per-vertex weights are sampled
  from the body, unless an explicit list of weight dictionaries is supplied.
  Polygon material indices can be assigned afterwards. Shading defaults flat.
- `bind(ctx, obj)` normalizes vertex weights and adds the shared rig modifier.
  For objects created via clothes.meshObject, use a ctx.prefix name and bind.
- `part(ctx, category, label, objects, hides=None)` returns a descriptor.
  Category is Foot, Leg, Belt, Chest, Headgear (or extra Hair/Beard as needed).
  Label is a unique display name, e.g. `Gota Ranger hood`. Objects is a list.
  Foot automatically hides the bare feet. Chest/Leg should NOT blindly hide
  entire Body, since both and partial sleeves need shared skin. Root helper
  resolves body occlusion for selected costume by surface region.
  Add explicit hides for covered hair only when the entire selected hairstyle
  must disappear; avoid hiding wanted braids/hair. Root will assess fit.

The preset is a normal runtime manifest entry:

```python
preset = dict(name='Ranger', group='Gota', pose='A_TPose', skin=16,
  hairColor='Copper', pupilColor='Green', parts=[
    dict(category='Hair', item='09 Twin braids'),
    dict(category='Eyes', item='02 Focused'),
    dict(category='Mouth', item='03 Neutral'),
    dict(category='Brow', item='04 Heroic'),
  ])
return parts, preset
```

Root fills Body/Base, Face/Base, Nose/Tiny and all absent optional slots as
None, then adds the returned clothing part selections. You may add `skinRgb`
to the preset as three zero-to-one channels for pale Lich/Warlock; root will
register an exact skin palette entry during integration. Existing face decals
are allowed. Existing color names are in colors/*.json. Parts can be direct
existing runtime preset selections rather than duplicated if unchanged.

Root exporter will write five modular runtime GLBs/sidecars, preset.json,
hero.blend and rendered front/back and item review sheets in your output.
It will inspect weights, count actual visible exported triangles and output
verification.json. Root will send readiness updates. Build custom geometry
now using the interface; avoid shared source or manifest writes.
