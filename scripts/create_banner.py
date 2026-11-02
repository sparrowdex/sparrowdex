"""Generate the full-width pixel sparrow banner (the only place the sparrow appears).

Run from the repo root:  python scripts/create_banner.py
Output: images/banner.svg (one file: the scene has its own sky, so it suits both themes)
"""
import html

from retro_svg import text
from sparrow_svg import C, CLOUD, _rects, _scene, bird_group, heart_group

COLS, ROWS, CELL = 140, 32, 6
W, H = COLS * CELL, ROWS * CELL
BIRD_X = 102                       # sparrow's 32x32 grid sits here (cells)

NAME = "SREEJA"
TAGLINE = "full-stack / ui-ux / creative coder"
HANDLE = "@sparrowdex"

C.update({"petal": "#FF8FAB", "petal_l": "#FFC2D4", "centre": "#FFD34E", "spark": "#FFFFFF"})

BIG_CLOUD = {}
for y, row in enumerate(["...WWW....", ".WWWWWWW..", "WWWWWWWWWW", "SSSSSSSSSS"]):
    for x, ch in enumerate(row):
        if ch != ".":
            BIG_CLOUD[(x, y)] = "cloud" if ch == "W" else "cloud_s"


def flower(x):
    """A tiny flower standing on the branch at column x."""
    return {(x, 26): "petal", (x - 1, 27): "petal", (x + 1, 27): "petal", (x, 27): "centre",
            (x, 28): "leaf_d", (x - 1, 28): "leaf", (x, 25): "petal_l"}


def leaves(x):
    return {(x, 28): "leaf", (x + 1, 28): "leaf_d", (x + 1, 27): "leaf", (x + 2, 26): "leaf"}


def drifting(sprite, x, y, secs, step=2):
    """A sprite that drifts left forever, wrapping around (drawn twice, one banner apart)."""
    n = COLS // step
    values = ";".join(f"{-i * step * CELL} 0" for i in range(n + 1))
    keys = ";".join(f"{i / n:.4f}" for i in range(n + 1))
    return f'''<g>{_rects(sprite, CELL, x, y)}{_rects(sprite, CELL, x + COLS, y)}
      <animateTransform attributeName="transform" type="translate" dur="{secs}s" repeatCount="indefinite"
        calcMode="discrete" values="{values}" keyTimes="{keys}"/>
    </g>'''


def sparkle(x, y, delay):
    pts = {(x, y): "spark", (x - 1, y): "spark", (x + 1, y): "spark", (x, y - 1): "spark", (x, y + 1): "spark"}
    return f'''<g opacity="0">{_rects(pts, CELL)}
      <animate attributeName="opacity" dur="2.8s" begin="{delay}s" repeatCount="indefinite" calcMode="discrete"
        values="0;1;0" keyTimes="0;.4;.7"/>
    </g>'''


sky, ground = _scene(COLS)
for x in (8, 41, 77, 92):
    ground.update(leaves(x))
for x in (18, 33, 58, 70, 86, 136):
    ground.update(flower(x))

name, _ = text(NAME, 48, 36 + CELL, 84 + CELL, C["petal"])      # pink drop shadow, one pixel off
name_top, _ = text(NAME, 48, 36, 84, "#4A2A3A")
tag, _ = text(TAGLINE, 16, 38, 122, "#7A4A5E")
handle, _ = text(HANDLE, 16, 38, 150, "#E0457B")

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" shape-rendering="crispEdges">
  <title>{html.escape(f"Sreeja ({HANDLE}): {TAGLINE}")}</title>
  <clipPath id="frame">
    <rect x="{CELL}" y="0" width="{W - 2 * CELL}" height="{H}"/>
    <rect x="0" y="{CELL}" width="{W}" height="{H - 2 * CELL}"/>
  </clipPath>
  <g clip-path="url(#frame)">
    {_rects(sky, CELL)}
    {drifting(BIG_CLOUD, 60, 3, 70)}
    {drifting(CLOUD, 88, 8, 48)}
    {drifting(BIG_CLOUD, 118, 12, 90)}
    {drifting(CLOUD, 20, 19, 60)}
    {sparkle(64, 5, 0)}{sparkle(94, 17, 1.1)}{sparkle(134, 6, 1.9)}{sparkle(6, 20, 0.6)}
    {name}{name_top}
    {tag}
    {handle}
    {_rects(ground, CELL)}
    {bird_group(CELL, BIRD_X, 0)}
    {heart_group(CELL, BIRD_X, 0)}
  </g>
</svg>
'''

with open("images/banner.svg", "w", encoding="utf-8") as f:
    f.write(svg)
print(f"wrote images/banner.svg ({len(svg) // 1024} KB)")
