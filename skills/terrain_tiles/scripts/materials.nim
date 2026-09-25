import
  std/os,
  common

const
  PreviewRoot* = SampleRoot / "splat-previews"
  Names* = [
    "dirt-road-1", "cobble-road-1", "gravel-road-1",
    "forest-floor-1", "marsh-1", "grass-1",
    "grass-2", "grass-3", "grass-4"
  ]
  Titles* = [
    "Dirt road", "Cobblestone road", "Gravel road",
    "Forest floor", "Marsh", "Grass: green",
    "Grass: olive", "Grass: mossy", "Grass: sparse"
  ]
  Grounds* = [
    "grass-1", "grass-2", "grass-1",
    "grass-3", "grass-1", "dirt-road-1",
    "dirt-road-1", "forest-floor-1", "gravel-road-1"
  ]
