"""Turn text into SVG <path> outlines so it renders identically everywhere.

GitHub serves README images through its camo proxy, which blocks external
requests -- so `@import url(fonts.googleapis.com/...)` inside an SVG silently
fails and visitors get a fallback font. Baking glyphs into paths avoids that.

Requires: pip install fonttools
"""
import os
import urllib.request

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
FONT_URLS = {
    "GreatVibes.ttf": "https://github.com/google/fonts/raw/main/ofl/greatvibes/GreatVibes-Regular.ttf",
    "FiraCode.ttf": "https://github.com/google/fonts/raw/main/ofl/firacode/FiraCode%5Bwght%5D.ttf",
}


def load_font(name, wght=None):
    path = os.path.join(FONT_DIR, name)
    if not os.path.exists(path):
        os.makedirs(FONT_DIR, exist_ok=True)
        print(f"Downloading {name}...")
        urllib.request.urlretrieve(FONT_URLS[name], path)
    font = TTFont(path)
    if wght is not None and "fvar" in font:
        from fontTools.varLib.instancer import instantiateVariableFont
        font = instantiateVariableFont(font, {"wght": wght})
    return font


def glyph_paths(font, text, size):
    """Return ([(char, d, x_advance_start)], total_width) with baseline at y=0."""
    cmap = font.getBestCmap()
    glyphset = font.getGlyphSet()
    hmtx = font["hmtx"]
    scale = size / font["head"].unitsPerEm
    out, x = [], 0.0
    for ch in text:
        gname = cmap.get(ord(ch), ".notdef")
        pen = SVGPathPen(glyphset, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
        # font units are y-up; SVG is y-down -> flip and scale
        glyphset[gname].draw(TransformPen(pen, (scale, 0, 0, -scale, x, 0)))
        out.append((ch, pen.getCommands(), x))
        x += hmtx[gname][0] * scale
    return out, x
