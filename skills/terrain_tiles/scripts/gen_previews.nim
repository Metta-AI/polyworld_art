import
  std/os,
  pixie,
  common, heights, materials, stamps

const
  Margin = 12
  PanelWidth = 384
  PanelHeight = 256
  RowHeight = 292

proc label(image: Image, font: Font, value: string, x, y: int)
  {.raises: [PixieError].} =
  ## Places a label above a preview without changing the terrain assets.
  image.fillText(
    font.typeset(value),
    translate(vec2(x.float32, y.float32))
  )

proc checker(width, height: int, dark: bool): Image
  {.raises: [PixieError].} =
  ## Builds a neutral checkerboard to reveal alpha coverage and matte fringes.
  result = newImage(width, height)
  for y in 0 ..< height:
    for x in 0 ..< width:
      let
        alternate = ((x div 16) + (y div 16)) mod 2 == 0
        value =
          if dark:
            if alternate: 32'u8 else: 48'u8
          else:
            if alternate: 220'u8 else: 244'u8
      result.data[y * width + x] = rgbx(value, value, value, 255)

proc overlap(index: int, mode: StampBlend): Image
  {.raises: [TerrainError, PixieError].} =
  ## Places three overlapping copies with varied rotations over another tile.
  let
    ground = Grounds[index]
    tile = readImage(DataRoot / "tiles" / (ground & ".rgb.png"))
    tileHeight = readImage(DataRoot / "tiles" / (ground & ".height.png"))
    color = newImage(PanelWidth, PanelHeight)
    height = newImage(PanelWidth, PanelHeight)
    stamp = loadPng(DataRoot / "stamps" / (Names[index] & ".rgb.png"))
    relief = loadPng(DataRoot / "stamps" / (Names[index] & ".height.png"))
    source = stamp.newImage()
    stencil = relief.stampStencil(stamp).newImage()
  for i in 0 ..< 2:
    let transform = translate(vec2((i * 256).float32, 0))
    color.draw(tile, transform)
    height.draw(tileHeight, transform)
  var
    surface = newStampSurface(color, height)
    amounts = newSeq[float32](PanelWidth * PanelHeight)
  for value in amounts.mitems:
    value = 0.95'f
  for i in 0 ..< 3:
    let
      patch = newImage(PanelWidth, PanelHeight)
      heightPatch = newImage(PanelWidth, PanelHeight)
      center = vec2((78 + i * 114).float32, (118 + (i mod 2) * 24).float32)
      transform = translate(center) * rotate((i - 1).float32 * 0.31'f) *
        scale(vec2(0.86'f + (i mod 2).float32 * 0.08'f)) *
        translate(-vec2(128, 128))
    patch.draw(source, transform)
    heightPatch.draw(stencil, transform)
    surface.compositeStamp(patch, heightPatch, amounts, 0, 0, mode)
  surface.color

proc generate() {.raises: [TerrainError, PixieError, IOError, OSError].} =
  ## Saves labeled splats and repeated-stamp previews on light and dark grounds.
  createDir(PreviewRoot)
  let
    font = readFont(FontPath)
    contact = newImage(816, 44 + RowHeight * 3)
    atlas = newImage(768, 768)
    light = checker(atlas.width, atlas.height, false)
    dark = checker(atlas.width, atlas.height, true)
    mattes = newImage(atlas.width * 2, atlas.height)
  for i, name in Names:
    atlas.draw(
      readImage(DataRoot / "stamps" / (name & ".rgb.png")),
      translate(vec2((i mod 3 * 256).float32, (i div 3 * 256).float32))
    )
  font.size = 17
  font.paint.color = color(0.94, 0.95, 0.96)
  contact.fill(rgba(28, 32, 36, 255))
  contact.label(font, "Soft terrain splats / RGBA / 256 x 256", Margin, 10)
  light.draw(atlas)
  dark.draw(atlas)
  mattes.draw(light)
  mattes.draw(dark, translate(vec2(atlas.width.float32, 0)))
  mattes.writeFile(PreviewRoot / "light-dark.png")
  for i, title in Titles:
    let
      x = Margin + (i mod 3) * (256 + Margin)
      y = 44 + (i div 3) * RowHeight
      stamp = readImage(DataRoot / "stamps" / (Names[i] & ".rgb.png"))
      background = checker(256, 256, false)
    contact.label(font, title, x, y)
    background.draw(stamp)
    contact.draw(background, translate(vec2(x.float32, (y + 26).float32)))
  contact.writeFile(PreviewRoot / "contact.png")
  for mode in StampBlend:
    let
      overview = newImage(PanelWidth * 3 + Margin * 4, 44 + RowHeight * 3)
      suffix = if mode == AlphaStamp: "alpha" else: "height"
      title =
        if mode == AlphaStamp:
          "Overlapping splats / ordinary alpha / 95% brush strength"
        else:
          "Overlapping splats / height blend / 95% brush strength"
    overview.fill(rgba(28, 32, 36, 255))
    overview.label(font, title, Margin, 10)
    for i, name in Names:
      let
        x = Margin + (i mod 3) * (PanelWidth + Margin)
        y = 44 + (i div 3) * RowHeight
        preview = overlap(i, mode)
      overview.label(font, Titles[i], x, y)
      overview.draw(preview, translate(vec2(x.float32, (y + 26).float32)))
    overview.writeFile(PreviewRoot / ("overlap-" & suffix & ".png"))
  echo PreviewRoot / "contact.png"
  echo PreviewRoot / "overlap-height.png"

try:
  generate()
except TerrainError, PixieError, IOError, OSError:
  quit(getCurrentExceptionMsg(), 1)
