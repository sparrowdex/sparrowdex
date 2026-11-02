"""Generate taped, gently swaying polaroid cards for the Featured Projects section.

Run from the repo root:  python scripts/create_polaroids.py
To add a project: drop a 4:3 screenshot in images/projects/ and add an entry below.
"""
import base64

from svgtext import glyph_paths, load_font

PROJECTS = [
    {
        "out": "images/projects/polaroid_diecast.svg",
        "photo": "images/projects/diecast.jpg",
        "title": "The Diecast Store",
        "tags": "React · Node · Express · Payments",
        "tape": "#FF85A1",
        "tilt": -2.5,
    },
    {
        "out": "images/projects/polaroid_snowglobe.svg",
        "photo": "images/projects/snowglobe.jpg",
        "title": "Timeless Snow Globe",
        "tags": "p5.js · WebGL · Sound · React",
        "tape": "#7DD3FC",
        "tilt": 2.2,
    },
]

W, H = 400, 440                  # canvas (room for tilt + shadow)
FW, PAD = 340, 14                # frame width, photo inset
PW = FW - 2 * PAD                # photo width (4:3)
PH = round(PW * 3 / 4)
FH = PAD + PH + 92               # thick polaroid chin
FX, FY = (W - FW) / 2, 40

script = load_font("GreatVibes.ttf")
mono = load_font("FiraCode.ttf", wght=500)


def text_paths(font, text, size, cx, baseline, fill):
    glyphs, w = glyph_paths(font, text, size)
    d = " ".join(d for _, d, _ in glyphs if d)
    return f'<path transform="translate({cx - w / 2:.1f}, {baseline})" fill="{fill}" d="{d}"/>'


for p in PROJECTS:
    with open(p["photo"], "rb") as f:
        photo = base64.b64encode(f.read()).decode()

    cx = W / 2
    pivot = f"{cx} {FY - 6}"  # swings from the tape
    t0, t1 = p["tilt"], p["tilt"] * 0.45
    title = text_paths(script, p["title"], 34, cx, FY + PAD + PH + 46, "#3B1F2B")
    tags = text_paths(mono, p["tags"], 11.5, cx, FY + PAD + PH + 72, "#8A7480")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none">
  <title>{p["title"]}: {p["tags"]}</title>
  <defs>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="10" stdDeviation="10" flood-color="#000" flood-opacity=".28"/>
    </filter>
    <linearGradient id="paper" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FFFDF9"/><stop offset="1" stop-color="#F4EEE8"/>
    </linearGradient>
    <linearGradient id="gloss" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#fff" stop-opacity=".22"/><stop offset=".45" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="photo"><rect x="{FX + PAD}" y="{FY + PAD}" width="{PW}" height="{PH}" rx="2"/></clipPath>
  </defs>
  <g transform="rotate({t0} {pivot})">
    <animateTransform attributeName="transform" type="rotate" dur="7s" repeatCount="indefinite"
      values="{t0} {pivot}; {t1} {pivot}; {t0} {pivot}" keyTimes="0;.5;1" calcMode="spline"
      keySplines=".45 0 .55 1; .45 0 .55 1"/>
    <rect x="{FX}" y="{FY}" width="{FW}" height="{FH}" rx="4" fill="url(#paper)" filter="url(#shadow)"/>
    <g clip-path="url(#photo)">
      <image href="data:image/jpeg;base64,{photo}" x="{FX + PAD}" y="{FY + PAD}" width="{PW}" height="{PH}" preserveAspectRatio="xMidYMid slice"/>
      <rect x="{FX + PAD}" y="{FY + PAD}" width="{PW}" height="{PH}" fill="url(#gloss)"/>
    </g>
    <rect x="{FX + PAD}" y="{FY + PAD}" width="{PW}" height="{PH}" rx="2" stroke="#000" stroke-opacity=".08"/>
    {title}
    {tags}
    <!-- washi tape -->
    <g transform="rotate({-p['tilt'] * 1.6 - 3} {cx} {FY})">
      <path d="M{cx - 52} {FY - 16} l4 4 -4 4 4 4 -4 4 4 4 -4 4 h104 l-4 -4 4 -4 -4 -4 4 -4 -4 -4 4 -4 z"
            fill="{p['tape']}" fill-opacity=".72"/>
      <path d="M{cx - 44} {FY - 10} h88 M{cx - 44} {FY - 2} h88 M{cx - 44} {FY + 6} h88"
            stroke="#fff" stroke-opacity=".35" stroke-width="2" stroke-dasharray="3 5"/>
    </g>
  </g>
</svg>
'''
    with open(p["out"], "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {p['out']}")
