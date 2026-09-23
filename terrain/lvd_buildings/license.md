# LvD building assets

The owner confirmed these nine models are AI-generated project assets and
CC0 on 2026-09-22. They are covered by the repository's root CC0 dedication.
Completed and construction models share `textures/buildings-atlas.png`.
`manifest.json` records completed exports. The sixteen construction models
are listed in `construction-manifest.json` with their placement offsets.

Both factions share the models in `models/`. `gold_mine.glb` is the timber
entrance, cart, and rails. The game attaches it to a pile of generated
RockGen boulders. Construction uses the foundation and wall models in
`models/construction/`; rubble uses generated rocks. These project assets
are covered by the same root CC0 dedication, with no models from the former
village or tower defense packs.

The nine images in `portraits/` are rendered from the game's building
assemblies by `polyworld/tools/gen_lvd_buildings.nim`. The gold mine portrait
includes the generated rock pile. These derived project images are CC0 too.

The eight project-generated CC0 trim variants in `textures/factions/` keep
the same UV layout. Their manifest records each faction's color and theme.
The game applies one assigned faction trim to completed buildings and both
construction stages, and keeps the original atlas on neutral gold mines.
Faction portraits in `portraits/<faction>/` use those same trims and are
generated with `gen_lvd_buildings.nim --factions`.
