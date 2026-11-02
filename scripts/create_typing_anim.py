"""Generate a real type-and-delete animation (SMIL, so it works inside <img>).

Run from the repo root:  python scripts/create_typing_anim.py
Outputs: images/typing_anim.svg (dark mode) and images/typing_anim_light.svg
"""
from svgtext import glyph_paths, load_font

LINES = ["Full-Stack Developer", "UI/UX Enthusiast", "Creative Coder"]
VARIANTS = {
    "images/typing_anim.svg": ["#FF69B4", "#38BDF8", "#C084FC"],        # dark mode
    "images/typing_anim_light.svg": ["#E0457B", "#0284C7", "#9333EA"],  # light mode
}
SIZE = 22
WIDTH, HEIGHT = 500, 40
BASELINE = 28
TYPE, DELETE, HOLD, GAP, BLINK = 0.08, 0.03, 2.0, 0.35, 0.45

font = load_font("FiraCode.ttf", wght=600)
rendered = [glyph_paths(font, line, SIZE) for line in LINES]
slots = [len(l) * TYPE + HOLD + len(l) * DELETE + GAP for l in LINES]
TOTAL = sum(slots)


def smil(events):
    """[(t_seconds, value)] -> (values, keyTimes) strings for a discrete <animate>."""
    merged = {}
    for t, v in sorted(events, key=lambda e: e[0]):
        merged[round(t / TOTAL, 4)] = v
    if 0 not in merged:
        merged[0] = events[0][1] if events[0][0] == 0 else 0
    keys = sorted(merged)
    return ";".join(str(merged[k]) for k in keys), ";".join(f"{k:g}" for k in keys)


def line_group(i, color):
    glyphs, w = rendered[i]
    n = len(LINES[i])
    cw = w / n  # monospace
    left = (WIDTH - w) / 2
    start = sum(slots[:i])
    typed_at = start + n * TYPE
    del_at = typed_at + HOLD

    width_ev = [(0, 0), (start, 0)]
    width_ev += [(start + k * TYPE, round(k * cw, 2)) for k in range(1, n + 1)]
    width_ev += [(del_at + k * DELETE, round((n - k) * cw, 2)) for k in range(1, n + 1)]
    widths, kt = smil(width_ev)
    cursor_x = ";".join(f"{left + float(v):.2f}" for v in widths.split(";"))

    vis_ev = [(0, 0), (start, 1)]
    t, on = typed_at + BLINK, 0
    while t < del_at:  # blink while holding the finished line
        vis_ev.append((t, on))
        t, on = t + BLINK, 1 - on
    vis_ev += [(del_at, 1), (del_at + n * DELETE + 0.01, 0)]
    vis, vkt = smil(vis_ev)

    paths = "\n".join(f'      <path d="{d}"/>' for _, d, _ in glyphs if d)
    return f'''  <clipPath id="clip{i}">
    <rect x="{left:.2f}" y="0" width="0" height="{HEIGHT}">
      <animate attributeName="width" dur="{TOTAL:.2f}s" repeatCount="indefinite" calcMode="discrete" values="{widths}" keyTimes="{kt}"/>
    </rect>
  </clipPath>
  <g clip-path="url(#clip{i})" fill="{color}">
    <g transform="translate({left:.2f}, {BASELINE})">
{paths}
    </g>
  </g>
  <rect y="{BASELINE - SIZE * 0.78:.1f}" width="2.5" height="{SIZE * 0.95:.1f}" rx="1" fill="{color}" x="{left:.2f}" opacity="0">
    <animate attributeName="x" dur="{TOTAL:.2f}s" repeatCount="indefinite" calcMode="discrete" values="{cursor_x}" keyTimes="{kt}"/>
    <animate attributeName="opacity" dur="{TOTAL:.2f}s" repeatCount="indefinite" calcMode="discrete" values="{vis}" keyTimes="{vkt}"/>
  </rect>'''


for out, colors in VARIANTS.items():
    body = "\n".join(line_group(i, c) for i, c in enumerate(colors))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" fill="none">
  <title>{" | ".join(LINES)}</title>
{body}
</svg>
'''
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {out}  ({TOTAL:.1f}s loop)")
