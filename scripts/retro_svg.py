"""Retro game UI pieces: pixel text, sprites, game panels and the arcade stats HUD.

All text is Press Start 2P baked into paths (sizes are multiples of 8 so glyph
pixels land on whole screen pixels); icons are tiny hand-drawn sprites.
"""
import html

from svgtext import glyph_paths, load_font

INK = {
    "bg": "#17122B", "frame": "#F4EBD9", "inner": "#3D3266", "text": "#F4EBD9", "dim": "#8D84B5",
    "pink": "#FF6FA5", "cyan": "#5CE1E6", "yellow": "#FFD34E", "green": "#7BE08A", "purple": "#B98CFF",
}

_font = None


def font():
    global _font
    if _font is None:
        _font = load_font("PressStart2P.ttf")
    return _font


def text(s, size, x, y, fill, anchor="start", cls="", per_char_delay=None, start=0.0):
    """Pixel text with its baseline at y. anchor: start | middle | end."""
    glyphs, w = glyph_paths(font(), s, size)
    ox = {"start": x, "middle": x - w / 2, "end": x - w}[anchor]
    if per_char_delay is None:
        d = " ".join(g for _, g, _ in glyphs if g)
        c = f' class="{cls}"' if cls else ""
        return f'<path{c} transform="translate({ox:g} {y:g})" fill="{fill}" d="{d}"/>', w
    parts = []
    for i, (_, g, _) in enumerate(glyphs):
        if g:
            parts.append(f'<path class="{cls}" style="animation-delay:{start + i * per_char_delay:.2f}s" d="{g}"/>')
    return f'<g transform="translate({ox:g} {y:g})" fill="{fill}">{"".join(parts)}</g>', w


def sprite(rows, palette, x, y, px):
    """Draw a sprite from strings; '.' is transparent. Horizontal runs are merged."""
    by_col = {}
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            ch = row[c]
            if ch == ".":
                c += 1
                continue
            start = c
            while c < len(row) and row[c] == ch:
                c += 1
            by_col.setdefault(ch, []).append(f"M{x + start * px:g} {y + r * px:g}h{(c - start) * px:g}v{px:g}h{-(c - start) * px:g}z")
    return "".join(f'<path fill="{palette[k]}" d="{"".join(v)}"/>' for k, v in by_col.items())


def panel(w, h, uid, scanlines=True):
    """Dark game window with a stepped (notched-corner) double border."""
    def notched(x, y, w_, h_, n, fill):
        return (f'<rect x="{x + n}" y="{y}" width="{w_ - 2 * n}" height="{h_}" fill="{fill}"/>'
                f'<rect x="{x}" y="{y + n}" width="{w_}" height="{h_ - 2 * n}" fill="{fill}"/>')

    lines = ""
    if scanlines:
        lines = f'''<pattern id="scan{uid}" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" fill-opacity=".22"/></pattern>
  <rect x="12" y="12" width="{w - 24}" height="{h - 24}" fill="url(#scan{uid})"/>'''
    return f'''{notched(0, 0, w, h, 4, INK["frame"])}
  {notched(4, 4, w - 8, h - 8, 4, INK["bg"])}
  <rect x="11" y="11" width="{w - 22}" height="{h - 22}" stroke="{INK['inner']}" stroke-width="2" fill="none"/>
  {lines}'''


def svg(w, h, title, body, css=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" shape-rendering="crispEdges">
  <title>{html.escape(title)}</title>
  <style>
    .blink {{ animation: blink 1.1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
{css}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; opacity: 1 !important; }} }}
  </style>
  {body}
</svg>
'''


# ---------------- sprites ----------------
FLAME = ["....R....", "...RR....", "..ROR..R.", ".ROOR.RR.", ".ROYORRR.", "RROYYOOR.", "ROYYYYOR.", "ROYWWYOR.", ".RYYYYR..", "..RRRR..."]
FLAME_PAL = {"R": "#E8433A", "O": "#FF9A3C", "Y": "#FFE066", "W": "#FFF8D6"}
TROPHY = ["YYYYYYYYYY", "Y.YWYYYD.Y", "Y.YWYYYD.Y", ".YYWYYYDY.", "..YYYYDD..", "...YYDD...", "....YD....", "....YD....", "..DDDDDD..", "..DDDDDD.."]
TROPHY_PAL = {"Y": "#FFD34E", "W": "#FFF6C2", "D": "#C98A1B"}
COIN_FRAMES = [
    ["..DDDD..", ".DYYYYD.", "DYWYYYYD", "DYWYDYYD", "DYWYDYYD", "DYYYYYYD", ".DYYYYD.", "..DDDD.."],
    ["...DD...", "..DYYD..", ".DYWYYD.", ".DYWDYD.", ".DYWDYD.", ".DYYYYD.", "..DYYD..", "...DD..."],
    ["...DD...", "...DD...", "...WD...", "...WD...", "...WD...", "...WD...", "...DD...", "...DD..."],
]
COIN_PAL = {"Y": "#FFD34E", "W": "#FFF6C2", "D": "#B9771A"}


def hud_svg(stats):
    """Arcade scoreboard: streak / hi-score / coins + level XP bar."""
    W, H = 760, 196
    streak, record, coins = stats["streak"], stats["record"], stats["contribs"]
    level, xp = coins // 100 + 1, coins % 100
    parts = [panel(W, H, "hud")]

    t, _ = text("PLAYER 1  SPARROWDEX", 8, 32, 40, INK["dim"])
    parts.append(t)
    t, _ = text("PRESS START", 8, W - 32, 40, INK["pink"], anchor="end", cls="blink")
    parts.append(t)

    cols = [
        ("1UP STREAK", f"{streak:03d}", "DAYS", INK["pink"], FLAME, FLAME_PAL, 4),
        ("HI-SCORE", f"{record:03d}", "DAYS", INK["yellow"], TROPHY, TROPHY_PAL, 4),
        ("COINS", f"{coins:03d}", "CONTRIBS", INK["cyan"], None, None, 4),
    ]
    cw = (W - 64) / 3
    for i, (label, value, unit, col, spr, pal, px) in enumerate(cols):
        cx = 32 + cw * i + cw / 2
        t, _ = text(label, 8, cx, 72, col, anchor="middle")
        parts.append(t)
        vt, vw = text(value, 24, cx + 22, 112, INK["text"], anchor="middle")
        parts.append(vt)
        ix = cx + 22 - vw / 2 - 48
        if spr:
            parts.append(sprite(spr, pal, ix, 82, px))
        else:  # spinning coin: frames shown in turn
            seq = [0, 1, 2, 1]
            for f, frame in enumerate(seq):
                vals = ";".join("1" if k == f else "0" for k in range(len(seq)))
                parts.append(f'<g opacity="{1 if f == 0 else 0}">{sprite(COIN_FRAMES[frame], COIN_PAL, ix, 84, px)}'
                             f'<animate attributeName="opacity" dur="0.9s" repeatCount="indefinite" calcMode="discrete" values="{vals}"/></g>')
        t, _ = text(unit, 8, cx + 22, 130, INK["dim"], anchor="middle")
        parts.append(t)

    # level + XP bar
    t, lw = text(f"LV {level:02d}", 16, 32, 172, INK["green"])
    parts.append(t)
    xp_label = f"{100 - xp} XP TO LV {level + 1:02d}"
    _, xw = text(xp_label, 8, 0, 0, INK["dim"])
    segs, gap = 20, 4
    bx = 32 + lw + 20
    seg_w = int((W - 32 - xw - 20 - bx) / segs) - gap
    filled = round(xp / 100 * segs)
    for k in range(segs):
        on = k < filled
        fill = INK["green"] if on else INK["inner"]
        anim = f' class="seg" style="animation-delay:{0.3 + k * 0.06:.2f}s"' if on else ""
        parts.append(f'<rect{anim} x="{bx + k * (seg_w + gap)}" y="156" width="{seg_w}" height="16" fill="{fill}"/>')
    t, _ = text(xp_label, 8, W - 32, 172, INK["dim"], anchor="end")
    parts.append(t)

    css = """    .seg { opacity: 0; animation: on 0s forwards; }
    @keyframes on { to { opacity: 1; } }"""
    title = f"Streak {streak} days, best {record} days, {coins} contributions, level {level}"
    return svg(W, H, title, "\n  ".join(parts), css)
