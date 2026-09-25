import
  std/[os, strutils],
  common, cuts, heights, textures, tiles

type AssetKind* = enum
  TileAssets, StampAssets

proc loadNames*(path: string): seq[string] {.raises: [TerrainError].} =
  ## Reads unique material base names in row-major atlas order.
  var content: string
  try:
    content = readFile(path)
  except IOError as error:
    raise newException(TerrainError, "Cannot read names: " & path, error)
  for line in content.splitLines():
    let name = line.strip()
    if name.len == 0:
      continue
    for c in name:
      if c notin {'a' .. 'z', '0' .. '9', '-'}:
        raise newException(TerrainError, "Invalid material name: " & name)
    if name in result:
      raise newException(TerrainError, "Duplicate material name: " & name)
    result.add(name)
  if result.len == 0:
    raise newException(TerrainError, "Names file is empty.")

proc validateHeight*(height: Png) {.raises: [TerrainError].} =
  ## Requires prepared opaque grayscale data without normalizing its range.
  height.validate()
  for pixel in height.data:
    if pixel.a != 255 or pixel.r != pixel.g or pixel.g != pixel.b:
      raise newException(TerrainError, "Height must be opaque grayscale.")

proc validatePair*(color, height: Png, kind: AssetKind, size = TextureSize)
  {.raises: [TerrainError].} =
  ## Checks final dimensions, periodic tiles, and the stamp alpha contract.
  validateTextureSize(size)
  color.sameSize(height)
  height.validateHeight()
  if color.width != size or color.height != size:
    raise newException(TerrainError, "Pair has the wrong export dimensions.")
  case kind
  of TileAssets:
    for image in [color, height]:
      let stats = image.inspect()
      if stats.opaque != image.data.len or
        stats.horizontal != 0 or stats.vertical != 0:
          raise newException(TerrainError, "Tile must be opaque and periodic.")
  of StampAssets:
    var covered = false
    for i, pixel in color.data:
      if pixel.a == 0:
        if height.data[i].r != 0:
          raise newException(TerrainError, "Height outside stamp must be zero.")
      else:
        covered = true
    if not covered:
      raise newException(TerrainError, "Stamp is empty.")
    for i in 0 ..< size:
      if color.data[i].a != 0 or color.data[(size - 1) * size + i].a != 0 or
        color.data[i * size].a != 0 or color.data[i * size + size - 1].a != 0:
          raise newException(TerrainError, "Stamp needs transparent borders.")

proc exportPairs*(
  color, height: Png,
  names: seq[string],
  directory: string,
  kind: AssetKind,
  columns = 3, rows = 3, size = TextureSize,
  force = false
) {.raises: [TerrainError].} =
  ## Prepares and validates all named pairs before writing final PNG files.
  color.sameSize(height)
  if kind == TileAssets:
    height.validateHeight()
  validateTextureSize(size)
  let
    sourceColors = color.split(columns, rows)
    sourceHeights = height.split(columns, rows)
  if names.len != sourceColors.len:
    raise newException(TerrainError, "Need exactly one name per atlas cell.")
  var
    colors, maps: seq[Png]
    colorPaths, heightPaths: seq[string]
  for i, name in names:
    let
      patch = sourceColors[i].resizeTexture(
        size, preserveEdges = kind == TileAssets
      )
      relief =
        case kind
        of TileAssets:
          sourceHeights[i].resizeTexture(size)
        of StampAssets:
          sourceHeights[i].stampHeight(sourceColors[i], size)
      colorPath = directory / (name & ".rgb.png")
      heightPath = directory / (name & ".height.png")
    validatePair(patch, relief, kind, size)
    checkOutput(colorPath, force)
    checkOutput(heightPath, force)
    colors.add(patch)
    maps.add(relief)
    colorPaths.add(colorPath)
    heightPaths.add(heightPath)
  for i in 0 ..< names.len:
    colors[i].savePng(colorPaths[i], force)
    maps[i].savePng(heightPaths[i], force)
    if loadPng(colorPaths[i]).data != colors[i].data or
      loadPng(heightPaths[i]).data != maps[i].data:
        raise newException(TerrainError, "PNG round-trip changed exported data.")
    echo names[i], ": ", size, "x", size, " color and height"
