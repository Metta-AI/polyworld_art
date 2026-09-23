"""Label actual runtime captures without changing the rendered characters."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

Folder = Path(__file__).resolve().parent
Runtime = Folder / "runtime"
Data = Folder.parents[4]
Roster = json.loads((Folder / "existing_presets.json").read_text())
Background = (232, 232, 227)
Ink = (37, 39, 46)
Muted = (94, 97, 105)
Accents = [(116, 98, 69), (76, 104, 40), (107, 72, 128), (163, 50, 46)]
Ranks = ["MINION  0.70x", "RAIDER  0.90x", "ELITE  1.10x", "CHAMPION  1.40x"]
Width = 2640
Margin = 64
CellWidth = (Width - 2 * Margin) // 4
Crop = (80, 205, 944, 990)
ImageHeight = round(CellWidth * (Crop[3] - Crop[1]) / (Crop[2] - Crop[0]))
RowHeight = ImageHeight + 130
Top = 210


def font(size, bold=False):
    """Use the same OFL font family as the game interface."""
    name = "Rubik-Bold.ttf" if bold else "Rubik-Regular.ttf"
    return ImageFont.truetype(str(Data / "fonts" / name), size)


def centered(draw, text, x, y, size, bold=False, color=Ink):
    """Center one label in its fixed cell."""
    draw.text((x, y), text, font=font(size, bold), fill=color, anchor="mt")


def figure(sheet, entry, view, x, y):
    """Apply one identical crop and scale to every rendered character."""
    source = Image.open(Runtime / f"{entry['slug']}_{view}.png").convert("RGB")
    source = source.crop(Crop).resize((CellWidth, ImageHeight), Image.Resampling.LANCZOS)
    sheet.paste(source, (x, y))


def mobs(view):
    """Create a four-family roster while retaining relative rendered sizes."""
    sheet = Image.new("RGB", (Width, Top + 4 * RowHeight + 72), Background)
    draw = ImageDraw.Draw(sheet)
    centered(draw, "CALL TO ADVENTURE", Width // 2, 30, 62, True)
    suffix = {"front": "Front view", "back": "Back view", "walk": "Walking pose"}[view]
    centered(draw, f"EXISTING CHARGEN PARTS  |  {suffix.upper()}", Width // 2, 108, 26, True)
    for column, label in enumerate(Ranks):
        centered(draw, label, Margin + (column + 0.5) * CellWidth, 163, 25, True)
    for row, family in enumerate(["Undead", "Orcs", "Vampires", "Demons"]):
        y = Top + row * RowHeight
        draw.rounded_rectangle((Margin, y, Width - Margin, y + 39), 7, fill=Accents[row])
        tint = ["BEIGE", "GREEN", "PURPLE", "RED"][row]
        draw.text((Margin + 18, y + 7), f"TIER {row + 1}  |  {family.upper()}  |  {tint} SKIN",
                  fill="white", font=font(24, True))
        for column, entry in enumerate(Roster["entries"][row * 4:(row + 1) * 4]):
            x = Margin + column * CellWidth
            figure(sheet, entry, view, x, y + 45)
            baseline = y + 45 + ImageHeight
            centered(draw, entry["preset"]["name"], x + CellWidth / 2, baseline, 32, True)
            centered(draw, entry["weapons"], x + CellWidth / 2, baseline + 42, 23, color=Muted)
    centered(draw, "Actual GLB meshes + Polyworld toon renderer. No new models. Closest available outfits.",
             Width // 2, sheet.height - 43, 24, color=Muted)
    sheet.save(Runtime / f"mob_roster_{view}.png")


def heroes():
    """Show the four unchanged GotA presets proposed for CtA's party."""
    sheet = Image.new("RGB", (Width, 980), Background)
    draw = ImageDraw.Draw(sheet)
    centered(draw, "CTA HEROES FROM GOTA", Width // 2, 28, 60, True)
    centered(draw, "Existing presets, equipment, and colors", Width // 2, 102, 28)
    # All four hero crops use the same magnification and retain their proportions.
    crop = (235, 390, 780, 989)
    height = round(CellWidth * (crop[3] - crop[1]) / (crop[2] - crop[0]))
    for column, entry in enumerate(Roster["heroes"]):
        x = Margin + column * CellWidth
        source = Image.open(Runtime / f"{entry['slug']}_front.png").convert("RGB")
        source = source.crop(crop).resize((CellWidth, height), Image.Resampling.LANCZOS)
        sheet.paste(source, (x, 165))
        centered(draw, entry["preset"]["name"], x + CellWidth / 2, 857, 34, True)
        centered(draw, entry["family"] + "  |  " + entry["weapons"],
                 x + CellWidth / 2, 907, 22, color=Muted)
    sheet.save(Runtime / "hero_reuse.png")


for view in ["front", "back", "walk"]:
    mobs(view)
heroes()
print("Composed three mob review sheets and the four-hero sheet from actual runtime captures.")
