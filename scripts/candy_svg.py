"""Draw a glossy wrapped candy with a number on it (used for the live stat candies)."""
import html

from svgtext import glyph_paths, load_font

FLAVOURS = {  # light, mid, dark
    "blue": ("#CFF1FF", "#38BDF8", "#0369A1"),
    "pink": ("#FFE0EA", "#FF6F9C", "#BE185D"),
    "purple": ("#F1E4FF", "#B57BFF", "#7E22CE"),
}
LABEL_INK = {"dark": "#E9DDE3", "light": "#4A3640"}

W, H = 230, 132
CY = 54                       # candy centre line
BX0, BX1 = 58, 172            # candy body x-extent
BH = 62                       # body height

_fonts = {}


def _font(name, wght):
    key = (name, wght)
    if key not in _fonts:
        _fonts[key] = load_font(name, wght=wght)
    return _fonts[key]


def _text(font, text, size, cx, baseline, max_w=None):
    glyphs, w = glyph_paths(font, text, size)
    scale = 1.0
    if max_w and w > max_w:
        scale = max_w / w
    d = " ".join(g for _, g, _ in glyphs if g)
    return d, f"translate({cx - w * scale / 2:.1f}, {baseline}) scale({scale:.3f})"


def _twist(side, uid):
    """Crinkled cellophane fan at one end. side = -1 (left) or 1 (right)."""
    ex = BX0 + 2 if side < 0 else BX1 - 2
    s = side
    # outer zig-zag edge of the fan
    outer = [(40, -30), (47, -18), (40, -9), (49, 0), (40, 9), (47, 18), (40, 30)]
    pts = [(ex, CY - 8)] + [(ex + s * dx, CY + dy) for dx, dy in outer] + [(ex, CY + 8)]
    fan = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
    pleats = " ".join(
        f"M{ex:.1f} {CY + (dy * 0.2):.1f} L{ex + s * dx:.1f} {CY + dy:.1f}" for dx, dy in outer[1:-1]
    )
    return f'''    <path d="{fan}" fill="url(#fan{uid})" stroke="url(#fanEdge{uid})" stroke-width="1.2" stroke-linejoin="round"/>
    <path d="{pleats}" stroke="#fff" stroke-opacity=".55" stroke-width="1.1" stroke-linecap="round"/>
    <path d="M{ex + s * 6:.1f} {CY - 6} L{ex + s * 34:.1f} {CY - 24}" stroke="#fff" stroke-opacity=".8" stroke-width="2.2" stroke-linecap="round"/>
    <rect x="{ex - 5:.1f}" y="{CY - 11}" width="10" height="22" rx="5" fill="url(#knot{uid})"/>'''


def candy_svg(value, label, flavour, theme="dark", wobble_delay=0.0):
    light, mid, dark = FLAVOURS[flavour]
    uid = flavour
    num = f"{value:,}"
    nd, nt = _text(_font("Fredoka.ttf", 700), num, 38, (BX0 + BX1) / 2, CY + 13, max_w=BX1 - BX0 - 22)
    ld, lt = _text(_font("Caveat.ttf", 600), label, 24, W / 2, H - 8)
    top = CY - BH / 2

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none">
  <title>{html.escape(f"{num} {label}")}</title>
  <defs>
    <linearGradient id="body{uid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{light}"/><stop offset=".35" stop-color="{mid}"/><stop offset="1" stop-color="{dark}"/>
    </linearGradient>
    <linearGradient id="fan{uid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{light}" stop-opacity=".95"/><stop offset=".5" stop-color="{mid}" stop-opacity=".75"/><stop offset="1" stop-color="{dark}" stop-opacity=".85"/>
    </linearGradient>
    <linearGradient id="fanEdge{uid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="{dark}"/>
    </linearGradient>
    <linearGradient id="knot{uid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{mid}"/><stop offset="1" stop-color="{dark}"/>
    </linearGradient>
    <pattern id="stripes{uid}" width="22" height="22" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)">
      <rect width="9" height="22" fill="#fff" fill-opacity=".28"/>
    </pattern>
    <clipPath id="clip{uid}"><rect x="{BX0}" y="{top}" width="{BX1 - BX0}" height="{BH}" rx="{BH / 2}"/></clipPath>
    <filter id="drop{uid}" x="-20%" y="-30%" width="140%" height="170%">
      <feDropShadow dx="0" dy="6" stdDeviation="5" flood-color="{dark}" flood-opacity=".45"/>
    </filter>
    <filter id="ink{uid}" x="-10%" y="-20%" width="120%" height="150%">
      <feDropShadow dx="0" dy="2" stdDeviation="0" flood-color="{dark}" flood-opacity=".9"/>
    </filter>
  </defs>
  <style>
    .candy {{ transform-box: fill-box; transform-origin: center; animation: wobble 4.5s {wobble_delay:.2f}s ease-in-out infinite; }}
    @keyframes wobble {{ 0%,100% {{ transform: rotate(-3deg) translateY(0); }} 50% {{ transform: rotate(3deg) translateY(-3px); }} }}
    .spark {{ transform-box: fill-box; transform-origin: center; animation: twinkle 2.2s {wobble_delay + .6:.2f}s ease-in-out infinite; }}
    @keyframes twinkle {{ 0%,100% {{ opacity: 0; transform: scale(.4); }} 40%,60% {{ opacity: 1; transform: scale(1); }} }}
    @media (prefers-reduced-motion: reduce) {{ .candy, .spark {{ animation: none; }} }}
  </style>
  <g class="candy" filter="url(#drop{uid})">
{_twist(-1, uid)}
{_twist(1, uid)}
    <rect x="{BX0}" y="{top}" width="{BX1 - BX0}" height="{BH}" rx="{BH / 2}" fill="url(#body{uid})"/>
    <g clip-path="url(#clip{uid})">
      <rect x="{BX0}" y="{top}" width="{BX1 - BX0}" height="{BH}" fill="url(#stripes{uid})"/>
      <ellipse cx="{(BX0 + BX1) / 2}" cy="{CY + BH / 2 + 4}" rx="{(BX1 - BX0) / 2}" ry="14" fill="{dark}" fill-opacity=".35"/>
    </g>
    <rect x="{BX0 + 14}" y="{top + 6}" width="{BX1 - BX0 - 28}" height="11" rx="5.5" fill="#fff" fill-opacity=".6"/>
    <circle cx="{BX1 - 16}" cy="{top + 12}" r="3" fill="#fff" fill-opacity=".85"/>
    <path transform="{nt}" d="{nd}" fill="#fff" stroke="{dark}" stroke-width="5" stroke-linejoin="round" paint-order="stroke" filter="url(#ink{uid})"/>
  </g>
  <path class="spark" d="M{BX1 + 30} 12 l2.5 6.5 6.5 2.5 -6.5 2.5 -2.5 6.5 -2.5 -6.5 -6.5 -2.5 6.5 -2.5z" fill="{light if theme == 'dark' else mid}"/>
  <path transform="{lt}" d="{ld}" fill="{LABEL_INK[theme]}"/>
</svg>
'''
