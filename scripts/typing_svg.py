"""Type-and-delete text animation as an SVG fragment (SMIL, so it works inside <img>)."""
from svgtext import glyph_paths

TYPE, DELETE, HOLD, GAP, BLINK = 0.08, 0.03, 2.0, 0.35, 0.45


def typing_fragment(font, lines, colors, size, baseline, x=None, center=None, ns="t"):
    """Return (svg_fragment, loop_seconds).

    Give `x` to left-align every line at x, or `center` to center each line on it.
    `ns` prefixes clipPath ids so several fragments can share one SVG.
    """
    rendered = [glyph_paths(font, line, size) for line in lines]
    slots = [len(l) * TYPE + HOLD + len(l) * DELETE + GAP for l in lines]
    total = sum(slots)

    def smil(events):
        merged = {}
        for t, v in sorted(events, key=lambda e: e[0]):
            merged[round(t / total, 4)] = v
        merged.setdefault(0, 0)
        keys = sorted(merged)
        return ";".join(str(merged[k]) for k in keys), ";".join(f"{k:g}" for k in keys)

    parts = []
    for i, (color, (glyphs, w)) in enumerate(zip(colors, rendered)):
        n = len(lines[i])
        cw = w / n  # monospace
        left = x if x is not None else center - w / 2
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

        d = " ".join(d for _, d, _ in glyphs if d)
        top = baseline - size
        parts.append(f'''  <clipPath id="{ns}clip{i}">
    <rect x="{left:.2f}" y="{top}" width="0" height="{size * 1.4:.0f}">
      <animate attributeName="width" dur="{total:.2f}s" repeatCount="indefinite" calcMode="discrete" values="{widths}" keyTimes="{kt}"/>
    </rect>
  </clipPath>
  <g clip-path="url(#{ns}clip{i})"><path fill="{color}" transform="translate({left:.2f}, {baseline})" d="{d}"/></g>
  <rect y="{baseline - size * 0.78:.1f}" width="2.5" height="{size * 0.95:.1f}" rx="1" fill="{color}" x="{left:.2f}" opacity="0">
    <animate attributeName="x" dur="{total:.2f}s" repeatCount="indefinite" calcMode="discrete" values="{cursor_x}" keyTimes="{kt}"/>
    <animate attributeName="opacity" dur="{total:.2f}s" repeatCount="indefinite" calcMode="discrete" values="{vis}" keyTimes="{vkt}"/>
  </rect>''')
    return "\n".join(parts), total
