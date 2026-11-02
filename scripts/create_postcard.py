"""Generate the 'say hi' postcard (the link pills come from create_candies.py).

Run from the repo root:  python scripts/create_postcard.py
Output: images/postcard.svg (paper-coloured, so one file suits both light and dark mode)
"""
import html
import os

from svgtext import glyph_paths, load_font

MESSAGE = ["hi there!", "always up for new projects,", "creative ideas, or just a", "chat about code :)"]
SIGN = "- sreeja"
TO = ["to: you :)", "somewhere on github"]

hand = load_font("Caveat.ttf", wght=500)
mono = load_font("FiraCode.ttf", wght=500)

INK, SOFT, PINK = "#3B2A33", "#9A8790", "#E0457B"
HEART = "M12 21 C5 15 1 11 1 7 A5 5 0 0 1 12 4 A5 5 0 0 1 23 7 C23 11 19 15 12 21Z"


def words(font, s, size, x, y, fill, anchor="start", spacing=0.0):
    glyphs, w = glyph_paths(font, s, size)
    if spacing:  # letter-spaced: shift each glyph
        parts = [f'<path transform="translate({i * spacing:.1f} 0)" d="{d}"/>' for i, (_, d, _) in enumerate(glyphs) if d]
        w += spacing * (len(s) - 1)
    else:
        parts = [f'<path d="{" ".join(d for _, d, _ in glyphs if d)}"/>']
    ox = {"start": x, "middle": x - w / 2, "end": x - w}[anchor]
    return f'<g transform="translate({ox:.1f} {y})" fill="{fill}">{"".join(parts)}</g>'


def paper_defs(uid, dy=10, blur=10):
    return f'''<filter id="shadow{uid}" x="-20%" y="-20%" width="140%" height="150%">
      <feDropShadow dx="0" dy="{dy}" stdDeviation="{blur}" flood-color="#000" flood-opacity=".25"/>
    </filter>
    <linearGradient id="paper{uid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FFFDF9"/><stop offset="1" stop-color="#F4EEE8"/>
    </linearGradient>'''


# ---------------- postcard ----------------
W, H = 700, 400
CX, CY, CW, CH = 40, 30, 620, 340      # card rect
DIV = CX + 360                         # divider x

msg = "\n    ".join(words(hand, line, 30, CX + 36, CY + 96 + i * 42, INK) for i, line in enumerate(MESSAGE))
sign = words(hand, SIGN, 30, DIV - 30, CY + 96 + len(MESSAGE) * 42 + 4, PINK, anchor="end")
header = words(mono, "POST CARD", 13, (CX + CW + DIV) / 2 - 40, CY + 40, SOFT, anchor="middle", spacing=4)

# stamp: pink rectangle with scalloped (perforated) edges and a candy heart
SX, SY, SW, SH = CX + CW - 120, CY + 30, 88, 104
perf = "".join(f'<circle cx="{SX + i}" cy="{SY}" r="4"/><circle cx="{SX + i}" cy="{SY + SH}" r="4"/>' for i in range(0, SW + 1, 11))
perf += "".join(f'<circle cx="{SX}" cy="{SY + j}" r="4"/><circle cx="{SX + SW}" cy="{SY + j}" r="4"/>' for j in range(0, SH + 1, 13))
stamp = f'''<g transform="rotate(4 {SX + SW / 2} {SY + SH / 2})">
      <rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" fill="#FFFFFF"/>
      <rect x="{SX + 9}" y="{SY + 9}" width="{SW - 18}" height="{SH - 18}" fill="#FFD6E2"/>
      <g transform="translate({SX + SW / 2 - 24} {SY + 22}) scale(2)"><path d="{HEART}" fill="#FF6F9C"/>
        <path d="M6 8 A3 3 0 0 1 10 5" stroke="#fff" stroke-width="1.6" stroke-linecap="round" opacity=".8"/></g>
      {words(mono, "2026", 11, SX + SW / 2, SY + SH - 16, "#B23A66", anchor="middle")}
      <g fill="url(#paperpc)">{perf}</g>
    </g>'''

# postmark: double ring + wavy cancel lines, inky and slightly faded
PMX, PMY = SX - 22, SY + 92
waves = "".join(
    f'<path d="M{PMX - 150} {PMY - 18 + k * 12} q12 -7 24 0 t24 0 t24 0 t24 0 t24 0"/>' for k in range(4))
postmark = f'''<g opacity=".55" transform="rotate(-12 {PMX} {PMY})" stroke="#5B4B6E" stroke-width="2" fill="none">
      <circle cx="{PMX}" cy="{PMY}" r="40"/><circle cx="{PMX}" cy="{PMY}" r="32"/>
      {waves}
      <g stroke="none">{words(mono, "SPARROWDEX", 8.5, PMX, PMY - 4, "#5B4B6E", anchor="middle")}
      {words(mono, "NOV 2026", 8.5, PMX, PMY + 12, "#5B4B6E", anchor="middle")}</g>
    </g>'''

lines_y = [CY + 220, CY + 262, CY + 304]
addr_lines = "".join(f'<path d="M{DIV + 30} {y} H{CX + CW - 30}" stroke="#D8CEC6" stroke-width="2"/>' for y in lines_y)
addr = "".join(words(hand, t, 27, DIV + 38, lines_y[i] - 8, INK) for i, t in enumerate(TO))

pivot = f"{W / 2} {CY}"
postcard = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none">
  <title>{html.escape(" ".join(MESSAGE) + " " + SIGN)}</title>
  <defs>{paper_defs("pc")}</defs>
  <g transform="rotate(-1.5 {pivot})">
    <animateTransform attributeName="transform" type="rotate" dur="8s" repeatCount="indefinite"
      values="-1.5 {pivot}; -0.5 {pivot}; -1.5 {pivot}" keyTimes="0;.5;1" calcMode="spline" keySplines=".45 0 .55 1; .45 0 .55 1"/>
    <rect x="{CX}" y="{CY}" width="{CW}" height="{CH}" rx="6" fill="url(#paperpc)" filter="url(#shadowpc)"/>
    <rect x="{CX + 10}" y="{CY + 10}" width="{CW - 20}" height="{CH - 20}" rx="3" stroke="#EADFD6" stroke-width="1.5"/>
    {header}
    <path d="M{DIV} {CY + 60} V{CY + CH - 30}" stroke="#D8CEC6" stroke-width="2"/>
    {msg}
    {sign}
    {addr_lines}
    {addr}
    {stamp}
    {postmark}
  </g>
</svg>
'''

with open("images/postcard.svg", "w", encoding="utf-8") as f:
    f.write(postcard)
print("wrote images/postcard.svg")
