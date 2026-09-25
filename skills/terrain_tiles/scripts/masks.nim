import common

proc splatMask*(color, mask: Png, columns = 3, rows = 3): Png
  {.raises: [TerrainError].} =
  ## Applies diffuse coverage without changing the source tile colors.
  color.sameSize(mask)
  let size = color.gridSize(columns, rows)
  if min(size.width, size.height) <= 64:
    raise newException(TerrainError, "Apply splat masks at source resolution.")
  result = newPng(color.width, color.height)
  for y in 0 ..< color.height:
    for x in 0 ..< color.width:
      let
        i = y * color.width + x
        source = color.data[i]
        value = mask.data[i]
        px = x mod size.width
        py = y mod size.height
        distance = min(
          min(px, size.width - 1 - px),
          min(py, size.height - 1 - py)
        ).float32
        guard = smooth((distance - 8) / 24)
        gray = (value.r.float32 + value.g.float32 + value.b.float32) / 3
        weight = smooth((gray - 4) / 200) * guard
      if source.a != 255 or value.a != 255:
        raise newException(TerrainError, "Color and opacity mask must be opaque.")
      result.data[i] = rgba(source.r, source.g, source.b, toByte(weight * 255))
