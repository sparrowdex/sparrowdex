"""Generate the scrapbook hero: pixel-sparrow polaroid + name + typing line + handwritten notes.

Run from the repo root:  python scripts/create_hero.py
Outputs: images/hero.svg (dark mode) and images/hero_light.svg (light mode)
Edit NOTES / ROLES below to update what you're up to.
"""
import base64
import html
import io

from PIL import Image

from svgtext import glyph_paths, load_font
from sparrow_svg import sparrow_fragment
from typing_svg import typing_fragment

NAME = "Hi there, Sreeja here!"
ROLES = ["Full-Stack Developer", "UI/UX Enthusiast", "Creative Coder"]
NOTES = [  # (label, text)
    ("building", "The Diecast Store"),
    ("learning", "welding software (for an assignment, don't ask)"),
    ("let's talk", "coding journeys & what inspires you to create"),
]

THEMES = {
    "images/hero.svg": {
        "ink": "#FFFFFF", "note": "#E9DDE3", "accents": ["#FF69B4", "#38BDF8", "#C084FC"],
    },
    "images/hero_light.svg": {
        "ink": "#3B1F2B", "note": "#4A3640", "accents": ["#E0457B", "#0284C7", "#9333EA"],
    },
}

W, H = 840, 330
COL = 300                    # right column x
NOTE_SIZE, NOTE_MAX_W = 25, W - COL - 112 - 12

script = load_font("GreatVibes.ttf")
mono = load_font("FiraCode.ttf", wght=600)
hand = load_font("Caveat.ttf", wght=500)


def png_b64(path, px, fmt="PNG", crop=None):
    im = Image.open(path).convert("RGBA" if fmt == "PNG" else "RGB")
    if crop:
        im = im.crop(crop)
    im.thumbnail((px, px), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, fmt, **({"optimize": True} if fmt == "PNG" else {"quality": 86}))
    return base64.b64encode(buf.getvalue()).decode()


def path_of(font, text, size):
    glyphs, w = glyph_paths(font, text, size)
    return " ".join(d for _, d, _ in glyphs if d), w


def wrap(text, size, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and path_of(hand, trial, size)[1] > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur]


# ---------- left: pixel sparrow polaroid ----------
PX, PY, PW = 44, 34, 216          # photo frame (192px photo = 32 pixels x 6px)
PAD = 12
PH_ = PW - 2 * PAD                # square photo
FH = PAD + PH_ + 50
bow = png_b64("images/bow-modified.png", 120)
pcx = PX + PW / 2
pivot = f"{pcx} {PY - 6}"
cap_d, cap_w = path_of(hand, "me, probably debugging", 22)

polaroid = f'''  <g transform="rotate(-4 {pivot})">
    <animateTransform attributeName="transform" type="rotate" dur="7s" repeatCount="indefinite"
      values="-4 {pivot}; -1.8 {pivot}; -4 {pivot}" keyTimes="0;.5;1" calcMode="spline" keySplines=".45 0 .55 1; .45 0 .55 1"/>
    <rect x="{PX}" y="{PY}" width="{PW}" height="{FH}" rx="4" fill="url(#paper)" filter="url(#shadow)"/>
    {sparrow_fragment(PX + PAD, PY + PAD, PH_ // 32)}
    <rect x="{PX + PAD}" y="{PY + PAD}" width="{PH_}" height="{PH_}" fill="url(#gloss)"/>
    <path transform="translate({pcx - cap_w / 2:.1f}, {PY + PAD + PH_ + 33})" fill="#5A4650" d="{cap_d}"/>
    <g transform="rotate(4 {pcx} {PY})">
      <path d="M{pcx - 44} {PY - 14} l4 4 -4 4 4 4 -4 4 4 4 h88 l-4 -4 4 -4 -4 -4 4 -4 -4 -4 z" fill="#C084FC" fill-opacity=".7"/>
    </g>
    <image class="bow" href="data:image/png;base64,{bow}" x="{PX + PW - 30}" y="{PY - 26}" width="56" height="56"/>
  </g>'''

# ---------- right: name, typing, notes ----------
name_glyphs, name_w = glyph_paths(script, NAME, 50)
angel = png_b64("images/cute sonny angel-modified.png", 132)
name_css = "\n".join(
    f"    .c{i} {{ animation: rise .35s {0.05 * i:.2f}s ease-out forwards; }}" for i in range(len(NAME))
)
name_paths = "\n".join(
    f'    <path class="g c{i}" d="{d}"/>' for i, (_, d, _) in enumerate(name_glyphs) if d
)

notes_start = 0.05 * len(NAME) + 0.4


def notes_svg(theme):
    out, y = [], 196
    for i, (label, text) in enumerate(NOTES):
        color = theme["accents"][i]
        ld, _ = path_of(mono, label, 13)
        delay = notes_start + i * 0.25
        rows = wrap(text, NOTE_SIZE, NOTE_MAX_W)
        texts = "".join(
            f'<path transform="translate({COL + 112}, {y + j * 24})" fill="{theme["note"]}" d="{path_of(hand, r, NOTE_SIZE)[0]}"/>'
            for j, r in enumerate(rows)
        )
        out.append(f'''  <g class="note" style="animation-delay:{delay:.2f}s">
    <path transform="translate({COL + 2}, {y - 13}) scale(.62)" fill="{color}" d="M12 21 C5 15 1 11 1 7 A5 5 0 0 1 12 4 A5 5 0 0 1 23 7 C23 11 19 15 12 21Z"/>
    <path transform="translate({COL + 24}, {y - 3})" fill="{color}" d="{ld}"/>
    {texts}
  </g>''')
        y += 24 * len(rows) + 14
    return "\n".join(out)


for out, theme in THEMES.items():
    typing, _ = typing_fragment(mono, ROLES, theme["accents"], 22, 142, x=COL + 4)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none">
  <title>{html.escape(NAME + " " + " | ".join(ROLES) + ". " + " ".join(f"{l}: {t}." for l, t in NOTES))}</title>
  <defs>
    <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="10" stdDeviation="9" flood-color="#000" flood-opacity=".3"/>
    </filter>
    <linearGradient id="paper" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FFFDF9"/><stop offset="1" stop-color="#F4EEE8"/>
    </linearGradient>
    <linearGradient id="gloss" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#fff" stop-opacity=".2"/><stop offset=".45" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <style>
    .g {{ fill: {theme["ink"]}; opacity: 0; transform: translateY(5px); }}
    @keyframes rise {{ to {{ opacity: 1; transform: translateY(0); }} }}
{name_css}
    .angel {{ opacity: 0; transform-box: fill-box; transform-origin: center;
             animation: pop .5s {0.05 * len(NAME) + 0.1:.2f}s cubic-bezier(.3,1.6,.5,1) forwards; }}
    @keyframes pop {{ from {{ opacity: 0; transform: scale(.4) rotate(-20deg); }} to {{ opacity: 1; transform: none; }} }}
    .note {{ opacity: 0; animation: rise .5s ease-out forwards; transform: translateY(5px); }}
    .bow {{ transform-box: fill-box; transform-origin: center; animation: wiggle 3.5s ease-in-out infinite; }}
    @keyframes wiggle {{ 0%,100% {{ transform: rotate(-8deg); }} 50% {{ transform: rotate(8deg); }} }}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; opacity: 1 !important; transform: none !important; }} }}
  </style>
{polaroid}
  <g transform="translate({COL}, 92)">
{name_paths}
  </g>
  <image class="angel" href="data:image/png;base64,{angel}" x="{COL + name_w + 10:.1f}" y="48" width="46" height="46"/>
{typing}
{notes_svg(theme)}
</svg>
'''
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {out} ({len(svg) // 1024} KB)")
