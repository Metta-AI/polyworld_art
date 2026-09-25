import
  std/os,
  vmath,
  polyworld/quadterrain

const
  Models = currentSourcePath().parentDir /
    "exports/construction/models/construction"
  Names = [
    "town_hall", "farm", "barracks", "lumber_mill", "tower",
    "stables", "church", "blacksmith"
  ]

for stage in ["foundation", "walls"]:
  for name in Names:
    let
      slug = name & "_" & stage
      pack = loadPropPack(
        Models / stage / (slug & ".glb"),
        unitHeight = false,
        mergeNodes = true
      )
      size = pack.propSize(slug)
    doAssert pack.hasProp(slug), "Missing prop: " & slug
    doAssert size.x > 0 and size.y > 0 and size.z > 0
    echo "Loaded ", slug, ": ", size.x, " x ", size.y, " x ", size.z
