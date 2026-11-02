"""Glossy candy pieces: tech-stack hearts, 'other skills' candy wrappers, link pills.

Run from the repo root:  python scripts/create_candies.py
Outputs:
  images/hearts/<slug>.svg          one candy heart per main tech
  images/skills/<group>.svg         a flowing row of wrapped candies per skill group
  images/links/<name>.svg           slim glossy pill buttons for the say-hi links
All candies carry their own colour, so one file each suits light and dark mode.
"""
import html
import os

from svgtext import glyph_paths, load_font

bold = load_font("Fredoka.ttf", wght=700)
semi = load_font("Fredoka.ttf", wght=600)


# ---------------- colour helpers ----------------
def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(rgb):
    return "#" + "".join(f"{max(0, min(255, round(c))):02X}" for c in rgb)


def mix(a, b, t):
    ra, rb = _rgb(a), _rgb(b)
    return _hex(tuple(x + (y - x) * t for x, y in zip(ra, rb)))


def lighter(c, t):
    return mix(c, "#FFFFFF", t)


def darker(c, t):
    return mix(c, "#000000", t)


def label(font, text, size, cx, baseline, fill, stroke=None):
    glyphs, w = glyph_paths(font, text, size)
    d = " ".join(g for _, g, _ in glyphs if g)
    s = f' stroke="{stroke}" stroke-width="2.4" stroke-linejoin="round" paint-order="stroke"' if stroke else ""
    return f'<path transform="translate({cx - w / 2:.1f} {baseline})" fill="{fill}"{s} d="{d}"/>', w


def text_width(font, text, size):
    return glyph_paths(font, text, size)[1]


# ---------------- 1. candy hearts ----------------
HEARTS = [  # slug, label, light, mid, dark, ink
    ("nextjs", "NEXT.JS", "#FFD6E0", "#FF9EAA", "#E86A82", "#992B45"),
    ("tailwind", "TAILWIND", "#E0F2FE", "#56CCF2", "#2F80ED", "#075985"),
    ("nodejs", "NODE.JS", "#DCFCE7", "#6FCF97", "#27AE60", "#14532D"),
    ("prisma", "PRISMA", "#F3E8FF", "#C084FC", "#9333EA", "#581C87"),
    ("neondb", "NEON DB", "#FEF9C3", "#F2C94C", "#F2994A", "#78350F"),
]
HEART = ("M55 86 C22 64 9 49 9 33 C9 19 20 9 33 9 C43 9 50 15 55 23 "
         "C60 15 67 9 77 9 C90 9 101 19 101 33 C101 49 88 64 55 86 Z")


def heart_svg(i, slug, text, light, mid, dark, ink):
    W, H = 110, 104
    size = min(16, 15 * 58 / text_width(bold, text, 15))   # fit the label inside the heart
    t, _ = label(bold, text, size, 55, 44 + size / 2.6, ink)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none">
  <title>{html.escape(text.title())}</title>
  <defs>
    <radialGradient id="b" cx="38%" cy="30%" r="80%">
      <stop offset="0" stop-color="{lighter(light, .3)}"/><stop offset=".45" stop-color="{mid}"/><stop offset="1" stop-color="{dark}"/>
    </radialGradient>
    <linearGradient id="f" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{lighter(mid, .55)}"/><stop offset="1" stop-color="{lighter(mid, .1)}"/>
    </linearGradient>
    <filter id="s" x="-20%" y="-20%" width="140%" height="150%">
      <feDropShadow dx="0" dy="5" stdDeviation="4" flood-color="{dark}" flood-opacity=".45"/>
    </filter>
  </defs>
  <style>
    .c {{ animation: bob 3.2s {i * 0.35:.2f}s ease-in-out infinite; }}
    @keyframes bob {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-3px); }} }}
    .sp {{ transform-box: fill-box; transform-origin: center; animation: tw 2.4s {i * 0.5:.2f}s ease-in-out infinite; }}
    @keyframes tw {{ 0%,100% {{ opacity: 0; transform: scale(.4); }} 45%,55% {{ opacity: 1; transform: scale(1); }} }}
    @media (prefers-reduced-motion: reduce) {{ .c, .sp {{ animation: none; }} }}
  </style>
  <g class="c">
    <g filter="url(#s)">
      <path d="{HEART}" fill="url(#b)"/>
      <path d="{HEART}" fill="url(#f)" transform="translate(55 46) scale(.78) translate(-55 -46)"/>
      <path d="{HEART}" stroke="#fff" stroke-opacity=".5" stroke-width="1.2" transform="translate(55 46) scale(.78) translate(-55 -46)"/>
    </g>
    <ellipse cx="32" cy="24" rx="12" ry="6.5" fill="#fff" fill-opacity=".75" transform="rotate(-28 32 24)"/>
    <circle cx="47" cy="17" r="2.6" fill="#fff" fill-opacity=".85"/>
    {t}
  </g>
  <path class="sp" d="M96 8 q1.4 4.6 6 6 q-4.6 1.4 -6 6 q-1.4 -4.6 -6 -6 q4.6 -1.4 6 -6z" fill="#fff"/>
</svg>
'''


# ---------------- 2. candy-wrapper skill badges ----------------
SKILLS = {
    "frontend": [("React", "FB8C00"), ("JavaScript", "E65100"), ("Vite", "F4511E"), ("HTML5", "D84315"),
                 ("CSS3", "BF360C"), ("React Router", "E53935"), ("React Query", "C62828"),
                 ("React Hook Form", "B71C1C"), ("p5.js", "D81B60")],
    "backend": [("Express.js", "2E7D32"), ("Python", "1B5E20"), ("C", "7CB342"), ("C++", "558B2F"),
                ("Flask", "33691E"), ("MySQL", "00897B"), ("MongoDB", "00695C"), ("SQLite", "004D40"),
                ("Sequelize", "00796B")],
    "design": [("Framer", "2196F3"), ("Canva", "1E88E5"), ("Illustrator", "1976D2"), ("Lightroom", "0D47A1"),
               ("Streamlit", "039BE5"), ("NumPy", "0288D1"), ("Pandas", "0277BD"), ("Git", "0097A7"),
               ("GitHub", "00838F"), ("Postman", "303F9F")],
}
BH, TW, GAP, ROW = 28, 11, 12, 42        # body height, twist width, gap, row height
MAXW = 720


def wrapper(x, y, name, col, uid):
    """One small wrapped candy: glossy pill body + crinkled twist on each side."""
    col = "#" + col
    tw = text_width(semi, name, 13)
    bw = tw + 26
    cy = y + BH / 2
    lx, rx = x + TW, x + TW + bw
    twist = lambda ex, s: (f'<path d="M{ex} {cy - 5} L{ex - s * TW} {cy - 11} L{ex - s * (TW - 3)} {cy} '
                           f'L{ex - s * TW} {cy + 11} L{ex} {cy + 5} Z" fill="{lighter(col, .25)}" '
                           f'stroke="{darker(col, .15)}" stroke-width=".8" stroke-linejoin="round"/>'
                           f'<path d="M{ex - s * 2} {cy - 3} L{ex - s * (TW - 2)} {cy - 8}" stroke="#fff" '
                           f'stroke-opacity=".6" stroke-width="1.2" stroke-linecap="round"/>')
    t, _ = label(semi, name, 13, lx + bw / 2, cy + 4.6, "#FFFFFF", stroke=darker(col, .35))
    return (f'''<g>
    {twist(lx + 1, 1)}{twist(rx - 1, -1)}
    <rect x="{lx}" y="{y}" width="{bw}" height="{BH}" rx="{BH / 2}" fill="url(#g{uid})"/>
    <rect x="{lx + 6}" y="{y + 3}" width="{bw - 12}" height="7" rx="3.5" fill="#fff" fill-opacity=".45"/>
    {t}
  </g>''', f'''<linearGradient id="g{uid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{lighter(col, .35)}"/><stop offset=".5" stop-color="{col}"/><stop offset="1" stop-color="{darker(col, .2)}"/>
    </linearGradient>''', bw + 2 * TW)


def skills_svg(group, items):
    x, y, parts, grads, rows_w = 0, 6, [], [], [0]
    for i, (name, col) in enumerate(items):
        w = text_width(semi, name, 13) + 26 + 2 * TW
        if x and x + w > MAXW:
            x, y = 0, y + ROW
            rows_w.append(0)
        g, grad, w = wrapper(x, y, name, col, i)
        parts.append(g)
        grads.append(grad)
        x += w + GAP
        rows_w[-1] = x - GAP
    W, H = max(rows_w), y + BH + 10
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H}" viewBox="0 0 {W:.0f} {H}" fill="none">
  <title>{html.escape(", ".join(n for n, _ in items))}</title>
  <defs>
    {"".join(grads)}
    <filter id="s" x="-5%" y="-20%" width="110%" height="160%">
      <feDropShadow dx="0" dy="2" stdDeviation="1.6" flood-color="#000" flood-opacity=".25"/>
    </filter>
  </defs>
  <g filter="url(#s)">
  {"".join(parts)}
  </g>
</svg>
'''


# ---------------- 3. link pills ----------------
ICON = {
    "linkedin": ('<rect x="-8" y="-8" width="16" height="16" rx="3.5" fill="#fff"/>'
                 '<rect x="-5.2" y="-1.6" width="2.4" height="6.6" fill="{c}"/><circle cx="-4" cy="-4.3" r="1.5" fill="{c}"/>'
                 '<path d="M-1.4 -1.6h2.2v1c.4-.7 1.2-1.2 2.3-1.2 1.7 0 2.3 1.1 2.3 2.8v4h-2.4v-3.5c0-.8-.2-1.3-.9-1.3s-1.2.5-1.2 1.3v3.5h-2.3z" fill="{c}"/>'),
    "email": ('<rect x="-8.5" y="-6" width="17" height="12" rx="2.5" fill="#fff"/>'
              '<path d="M-7.3 -4.6l7.3 5.6 7.3-5.6" stroke="{c}" stroke-width="1.8" stroke-linejoin="round" fill="none"/>'),
    "instagram": ('<rect x="-8" y="-8" width="16" height="16" rx="5" stroke="#fff" stroke-width="2" fill="none"/>'
                  '<circle r="3.6" stroke="#fff" stroke-width="2" fill="none"/><circle cx="4.3" cy="-4.3" r="1.1" fill="#fff"/>'),
}
LINKS = [  # name, label, light, mid, dark
    ("linkedin", "LinkedIn", "#BFE7FF", "#56CCF2", "#2F80ED"),
    ("email", "Email", "#FFF1B8", "#F2C94C", "#F2994A"),
    ("instagram", "Instagram", "#FFD6E0", "#FF9EAA", "#E86A82"),
]


def pill_svg(name, text, light, mid, dark):
    PH = 36
    tw = text_width(semi, text, 15)
    W = int(18 + 22 + 10 + tw + 22)
    H = PH + 10
    t, _ = label(semi, text, 15, 18 + 22 + 10 + tw / 2, 4 + PH / 2 + 5.2, "#FFFFFF", stroke=darker(dark, .15))
    icon = ICON[name].replace("{c}", dark)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none">
  <title>{text}</title>
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{light}"/><stop offset=".55" stop-color="{mid}"/><stop offset="1" stop-color="{dark}"/>
    </linearGradient>
    <filter id="s" x="-10%" y="-20%" width="120%" height="160%">
      <feDropShadow dx="0" dy="3" stdDeviation="2.5" flood-color="{dark}" flood-opacity=".4"/>
    </filter>
  </defs>
  <rect x="2" y="4" width="{W - 4}" height="{PH}" rx="{PH / 2}" fill="url(#g)" filter="url(#s)"/>
  <rect x="12" y="7" width="{W - 24}" height="9" rx="4.5" fill="#fff" fill-opacity=".5"/>
  <g transform="translate({18 + 11} {4 + PH / 2})">{icon}</g>
  {t}
</svg>
'''


if __name__ == "__main__":
    for d in ("images/hearts", "images/skills", "images/links"):
        os.makedirs(d, exist_ok=True)
    for i, (slug, text, *cols) in enumerate(HEARTS):
        with open(f"images/hearts/{slug}.svg", "w", encoding="utf-8") as f:
            f.write(heart_svg(i, slug, text, *cols))
    for group, items in SKILLS.items():
        with open(f"images/skills/{group}.svg", "w", encoding="utf-8") as f:
            f.write(skills_svg(group, items))
    for name, text, *cols in LINKS:
        with open(f"images/links/{name}.svg", "w", encoding="utf-8") as f:
            f.write(pill_svg(name, text, *cols))
    print("wrote hearts, skills and links")
