"""Generate small pixel-font section headings.

Run from the repo root:  python scripts/create_titles.py
Outputs images/titles/<slug>.svg (dark mode) and <slug>_light.svg (light mode).
"""
import html
import os

from retro_svg import sprite, text

TITLES = [  # slug, text, dark accent, light accent
    ("stack", "TECH STACK", "#FF6FA5", "#E0457B"),
    ("projects", "PROJECTS", "#5CE1E6", "#0284C7"),
    ("streaks", "STATS", "#7BE08A", "#16A34A"),
    ("contact", "SAY HI", "#B98CFF", "#9333EA"),
]
INK = {"": "#F4EBD9", "_light": "#2B1F33"}
H = 44
BLOCK = ["XX", "XX"]                       # 2x2 pixel bullet (scaled by 4 -> 8px square)

os.makedirs("images/titles", exist_ok=True)
for slug, label, dark, light in TITLES:
    for suffix, ink in INK.items():
        accent = dark if suffix == "" else light
        t, tw = text(label, 16, 20, 26, ink)
        width = int(20 + tw + 8)
        # dotted pixel underline: 4px dashes every 8px, in the accent colour
        dots = "".join(f'<rect x="{x}" y="36" width="4" height="4" fill="{accent}"/>' for x in range(0, width, 8))
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{H}" viewBox="0 0 {width} {H}" fill="none" shape-rendering="crispEdges">
  <title>{html.escape(label.title())}</title>
  <style>
    .b {{ animation: blink 1.4s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: .25; }} }}
    @media (prefers-reduced-motion: reduce) {{ .b {{ animation: none; }} }}
  </style>
  <g class="b">{sprite(BLOCK, {"X": accent}, 0, 14, 4)}</g>
  {t}
  {dots}
</svg>
'''
        with open(f"images/titles/{slug}{suffix}.svg", "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"wrote images/titles/{slug}{suffix}.svg")
