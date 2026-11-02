"""Generate handwritten section titles with a self-drawing candy underline.

Run from the repo root:  python scripts/create_titles.py
Outputs images/titles/<slug>.svg (dark mode) and <slug>_light.svg (light mode).
"""
import html
import math
import os

from svgtext import glyph_paths, load_font

TITLES = [  # slug, text, dark accent, light accent
    ("stack", "my candy jar", "#FF69B4", "#E0457B"),
    ("projects", "things I've made", "#38BDF8", "#0284C7"),
    ("streaks", "my streaks", "#4ADE80", "#16A34A"),
    ("contact", "say hi!", "#C084FC", "#9333EA"),
]
INK = {"": "#FFFFFF", "_light": "#3B1F2B"}
SIZE, H, BASE = 44, 74, 46
HEART = "M12 21 C5 15 1 11 1 7 A5 5 0 0 1 12 4 A5 5 0 0 1 23 7 C23 11 19 15 12 21Z"

font = load_font("GreatVibes.ttf")
os.makedirs("images/titles", exist_ok=True)

for slug, text, dark, light in TITLES:
    glyphs, tw = glyph_paths(font, text, SIZE)
    d = " ".join(g for _, g, _ in glyphs if g)
    x0 = 6
    end = x0 + tw + 8
    # hand-drawn wave: gentle sine with a slight upward flick at the end
    pts = []
    steps = max(8, int((end - x0) / 9))
    for i in range(steps + 1):
        x = x0 + (end - x0) * i / steps
        y = BASE + 14 + 2.2 * math.sin(i * 1.1) - (4 if i == steps else 0)
        pts.append(f"{x:.1f} {y:.1f}")
    wave = "M" + " L".join(pts)
    width = int(end + 40)

    for suffix, ink in INK.items():
        accent = dark if suffix == "" else light
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{H}" viewBox="0 0 {width} {H}" fill="none">
  <title>{html.escape(text)}</title>
  <style>
    .line {{ stroke-dasharray: 1; stroke-dashoffset: 1; animation: draw 1.1s .2s ease-out forwards; }}
    @keyframes draw {{ to {{ stroke-dashoffset: 0; }} }}
    .heart {{ opacity: 0; transform-box: fill-box; transform-origin: center;
              animation: pop .45s 1.1s cubic-bezier(.3,1.6,.5,1) forwards, beat 2.4s 1.6s ease-in-out infinite; }}
    @keyframes pop {{ from {{ opacity: 0; transform: scale(.3); }} to {{ opacity: 1; transform: scale(1); }} }}
    @keyframes beat {{ 0%,100% {{ transform: scale(1); }} 15% {{ transform: scale(1.18); }} 30% {{ transform: scale(1); }} }}
    @media (prefers-reduced-motion: reduce) {{ .line, .heart {{ animation: none; stroke-dashoffset: 0; opacity: 1; }} }}
  </style>
  <path class="line" pathLength="1" d="{wave}" stroke="{accent}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>
  <path transform="translate({x0}, {BASE})" fill="{ink}" d="{d}"/>
  <g transform="translate({end + 6:.1f}, {BASE - 30}) scale(.9)"><path class="heart" fill="{accent}" d="{HEART}"/></g>
</svg>
'''
        out = f"images/titles/{slug}{suffix}.svg"
        with open(out, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"wrote {out}")
