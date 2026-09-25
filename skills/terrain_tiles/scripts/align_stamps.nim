import
  std/os,
  jsony,
  common, cuts

const Usage = "Usage: align_stamps input.png output.png [--force]"

type
  Band = object
    first, last: int
  Bounds = object
    x, y, width, height: int

proc bands(occupied: seq[bool]): seq[Band] {.raises: [TerrainError].} =
  ## Separates nonempty bands across gaps of at least twelve pixels.
  for i, active in occupied:
    if not active:
      continue
    if result.len == 0 or i - result[^1].last > 12:
      result.add Band(first: i, last: i)
    else:
      result[^1].last = i
  if result.len != 3:
    raise newException(TerrainError, "Expected three separated stamp bands.")

proc align(input, output: string, force: bool)
  {.raises: [TerrainError, IOError].} =
  ## Recenters complete stamps at their original resolution using alpha bounds.
  let
    source = loadPng(input)
    boundsPath = output.changeFileExt(".bounds.json")
  checkOutput(output, force)
  checkOutput(boundsPath, force)
  var
    occupied = newSeq[bool](source.height)
    boxes: seq[Bounds]
    cells: seq[Png]
    side = max(source.width, source.height) div 3
  for y in 0 ..< source.height:
    for x in 0 ..< source.width:
      if source.data[y * source.width + x].a > 0:
        occupied[y] = true
  for row in occupied.bands():
    var columns = newSeq[bool](source.width)
    for y in row.first .. row.last:
      for x in 0 ..< source.width:
        if source.data[y * source.width + x].a > 0:
          columns[x] = true
    for column in columns.bands():
      var
        top = row.last
        bottom = row.first
      for y in row.first .. row.last:
        for x in column.first .. column.last:
          if source.data[y * source.width + x].a > 0:
            top = min(top, y)
            bottom = max(bottom, y)
      let box = Bounds(
        x: column.first,
        y: top,
        width: column.last - column.first + 1,
        height: bottom - top + 1
      )
      boxes.add(box)
      side = max(side, max(box.width, box.height) + 32)
  side += side mod 2
  for box in boxes:
    let
      cell = newPng(side, side)
      patch = source.crop(box.x, box.y, box.width, box.height)
      left = (side - box.width) div 2
      top = (side - box.height) div 2
    for y in 0 ..< box.height:
      for x in 0 ..< box.width:
        cell.data[(top + y) * side + left + x] =
          patch.data[y * box.width + x]
    cells.add(cell)
  cells.assemble(3, 3).savePng(output, force)
  writeFile(boundsPath, boxes.toJson() & "\n")
  echo "Centered nine unscaled stamps in ", side, "x", side, " cells."

proc main() {.raises: [TerrainError, IOError].} =
  ## Reads explicit paths for the original three-by-three alignment helper.
  let args = commandLineParams()
  if args.len == 1 and args[0] in ["--help", "-h"]:
    echo Usage
    return
  if args.len notin [2, 3] or (args.len == 3 and args[2] != "--force"):
    raise newException(TerrainError, Usage)
  align(args[0], args[1], args.len == 3)

try:
  main()
except TerrainError, IOError:
  quit(getCurrentExceptionMsg(), 1)
