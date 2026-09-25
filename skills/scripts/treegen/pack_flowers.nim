import
  std/[math, os],
  pixie

const
  Root = currentSourcePath().parentDir / "../../.."
  Input = Root / "terrain/treegen/source/flowers.generated.png"
  Output = Root / "terrain/treegen/flower-atlas.png"
  Rows = [0, 283, 634, 939, 1254]

proc cleanCell(source: Image): Image =
  ## Removes isolated alpha specks while preserving connected painted petals.
  result = source.copy()
  var visited = newSeq[bool](source.data.len)
  for index in 0 ..< source.data.len:
    if visited[index] or source.data[index].a < 112:
      continue
    var pending = @[index]
    visited[index] = true
    var cursor = 0
    while cursor < pending.len:
      let point = pending[cursor]
      inc cursor
      for delta in [-source.width, -1, 1, source.width]:
        let neighbor = point + delta
        if neighbor < 0 or neighbor >= source.data.len:
          continue
        if abs(neighbor mod source.width - point mod source.width) > 1:
          continue
        if not visited[neighbor] and source.data[neighbor].a >= 112:
          visited[neighbor] = true
          pending.add neighbor
    if pending.len < 180:
      for point in pending:
        result.data[point] = rgbx(0, 0, 0, 0)
  for pixel in result.data.mitems:
    if pixel.a < 112:
      pixel = rgbx(0, 0, 0, 0)

proc main() =
  ## Packs measured source rows into sixteen padded, alpha-aware cells.
  let
    source = readImage(Input)
    atlas = newImage(512, 512)
  doAssert source.width == 1254 and source.height == 1254
  for row in 0 ..< 4:
    for column in 0 ..< 4:
      let
        x = column * 1254 div 4
        width = (column + 1) * 1254 div 4 - x
        cell = cleanCell(source.subImage(x, Rows[row], width,
          Rows[row + 1] - Rows[row]))
      var
        left = width
        top = cell.height
        right = 0
        bottom = 0
      for y in 0 ..< cell.height:
        for x in 0 ..< cell.width:
          if cell[x, y].a >= 112:
            left = min(left, x)
            top = min(top, y)
            right = max(right, x + 1)
            bottom = max(bottom, y + 1)
      let
        crop = cell.subImage(left, top, right - left, bottom - top)
        scale = 108.0 / max(crop.width, crop.height).float64
        resized = crop.resize(max(1, round(crop.width.float64 * scale).int),
          max(1, round(crop.height.float64 * scale).int))
        dx = column * 128 + (128 - resized.width) div 2
        dy = row * 128 + (128 - resized.height) div 2
      for y in 0 ..< resized.height:
        for x in 0 ..< resized.width:
          atlas[dx + x, dy + y] = resized[x, y]
  atlas.writeFile(Output)
  echo Output

main()
