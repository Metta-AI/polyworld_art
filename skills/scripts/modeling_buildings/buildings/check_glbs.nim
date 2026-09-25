import
  std/os,
  vmath,
  polyworld/quadterrain

const
  Models = currentSourcePath().parentDir / "exports/lvd_buildings/models"
  Names = [
    "town_hall", "farm", "barracks", "lumber_mill", "tower",
    "stables", "church", "blacksmith", "gold_mine"
  ]

for name in Names:
  let
    pack = loadPropPack(Models / (name & ".glb"), unitHeight = false)
    size = pack.propSize(name)
  doAssert pack.hasProp(name), "Missing prop: " & name
  doAssert size.x > 0 and size.y > 0 and size.z > 0
  echo "Loaded ", name, ": ", size.x, " x ", size.y, " x ", size.z
