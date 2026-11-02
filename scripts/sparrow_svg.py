"""A 32x32 pixel-art sparrow on a branch, drawn procedurally as crisp SVG rects.

sparrow_fragment(x, y, cell) -> SVG markup for the scene at (x, y), `cell` px per pixel.
Run directly to write a large preview:  python scripts/sparrow_svg.py out.svg
"""
import sys

N = 32
C = {
    "sky0": "#FFD3E1", "sky1": "#FFE2EB", "sky2": "#FFEFF3", "sky3": "#FFF7EE",
    "cloud": "#FFFFFF", "cloud_s": "#F6E7EE",
    "brown": "#9C6644", "brown_l": "#C08552", "brown_d": "#6B4226",
    "cream": "#FFF4E0", "gray": "#D9D2CB", "gray_l": "#EFE9E3",
    "beak": "#F4B942", "beak_d": "#CF8A1E", "eye": "#1E1A1A", "shine": "#FFFFFF",
    "blush": "#FF8FAB", "leg": "#E09F7D", "out": "#3A2620",
    "branch": "#7A5230", "branch_l": "#A0703F", "leaf": "#7BC67B", "leaf_d": "#4E9A5A",
    "heart": "#FF5C8A",
}


def _ellipse(cx, cy, rx, ry):
    return {(x, y) for x in range(N) for y in range(N)
            if ((x + .5 - cx) / rx) ** 2 + ((y + .5 - cy) / ry) ** 2 <= 1}


def _bird():
    """Return (body pixels, eye-open pixels, eye-closed pixels) as {(x,y): colour}."""
    px = {}
    # tail: a dark wedge pointing up-left
    for x in range(2, 9):
        yc = round(17 - (9 - x) * 0.8)
        for y in (yc - 1, yc, yc + 1):
            px[(x, y)] = "brown_d"
    belly = _ellipse(18.5, 22, 7.5, 5.5)
    for (x, y) in _ellipse(14.5, 19.5, 9.5, 7):          # body
        if (x, y) in belly:
            px[(x, y)] = "gray_l" if (y >= 22 and x >= 17) else "gray"
        else:
            px[(x, y)] = "brown"
    for (x, y) in _ellipse(21.5, 12.5, 6.2, 6.2):        # head
        if y <= 10 or x <= 19:
            px[(x, y)] = "brown"
        elif y >= 15:
            px[(x, y)] = "gray"
        else:
            px[(x, y)] = "cream"
    wing = _ellipse(11.5, 18.5, 6.5, 4)
    for (x, y) in wing:                                   # wing: diagonal streaks + light tips
        if (x, y + 1) not in wing:
            px[(x, y)] = "brown_l"
        elif (x - y) % 3 == 0:
            px[(x, y)] = "brown"
        else:
            px[(x, y)] = "brown_d"
    for p in [(19, 7), (20, 7), (21, 7), (18, 8), (17, 9)]:  # cap highlight
        px[p] = "brown_l"
    px.update({(28, 12): "beak", (29, 12): "beak", (28, 13): "beak_d"})
    px.update({(24, 14): "blush", (25, 14): "blush"})
    px.update({(13, 27): "leg", (13, 28): "leg", (16, 27): "leg", (16, 28): "leg",
               (14, 28): "leg", (17, 28): "leg"})

    # auto outline: empty 4-neighbours of the bird become outline pixels
    outline = {}
    for (x, y) in px:
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in px and 0 <= nx < N and 0 <= ny < N and ny < 29:
                outline[(nx, ny)] = "out"
    for p in [(13, 27), (13, 28), (16, 27), (16, 28), (14, 28), (17, 28)]:
        outline.pop((p[0] - 1, p[1]), None)  # keep legs skinny
    px.update(outline)

    eye_open = {(23, 11): "shine", (24, 11): "eye", (23, 12): "eye", (24, 12): "eye"}
    eye_closed = {(23, 11): "cream", (24, 11): "cream", (23, 12): "eye", (24, 12): "eye"}
    return px, eye_open, eye_closed


def _scene(width=N):
    """Banded sky + branch for a `width` x 32 grid."""
    sky = {}
    bands = [(0, 9, "sky0"), (9, 17, "sky1"), (17, 24, "sky2"), (24, 29, "sky3")]
    for y in range(N):
        for x in range(width):
            for a, b, col in bands:
                if a <= y < b:
                    sky[(x, y)] = col
            # soft two-row dither where bands meet
            for i, (a, _, col) in enumerate(bands[1:], 1):
                above = bands[i - 1][2]
                if (y == a and x % 2 == 0) or (y == a + 1 and x % 4 == 1):
                    sky[(x, y)] = above
    ground = {}
    for x in range(width):
        ground[(x, 29)] = "branch_l"
        ground[(x, 30)] = "branch"
        ground[(x, 31)] = "branch" if x % 5 else "branch_l"
    if width == N:
        for p, col in [((3, 28), "leaf"), ((4, 28), "leaf"), ((4, 27), "leaf_d"), ((5, 27), "leaf"),
                       ((27, 28), "leaf"), ((28, 28), "leaf_d"), ((28, 27), "leaf"), ((29, 26), "leaf")]:
            ground[p] = col
    return sky, ground


CLOUD = {(1, 0): "cloud", (2, 0): "cloud", (0, 1): "cloud", (1, 1): "cloud", (2, 1): "cloud",
         (3, 1): "cloud", (4, 1): "cloud", (0, 2): "cloud_s", (1, 2): "cloud_s", (2, 2): "cloud_s",
         (3, 2): "cloud_s", (4, 2): "cloud_s", (3, 0): "cloud"}
HEART = {(0, 0): "heart", (2, 0): "heart", (0, 1): "heart", (1, 1): "heart", (2, 1): "heart",
         (1, 2): "heart"}


def _rects(pixels, cell, dx=0, dy=0):
    """Merge horizontal runs of same-coloured pixels into rects, grouped by colour."""
    by_col = {}
    rows = {}
    for (x, y), col in pixels.items():
        rows.setdefault(y, []).append((x, col))
    for y, items in rows.items():
        items.sort()
        start, prev_x, prev_c = items[0][0], items[0][0], items[0][1]
        for x, col in items[1:] + [(None, None)]:
            if x == prev_x + 1 if x is not None else False:
                if col == prev_c:
                    prev_x = x
                    continue
            by_col.setdefault(prev_c, []).append(
                f"M{(start + dx) * cell:g} {(y + dy) * cell:g}h{(prev_x - start + 1) * cell:g}v{cell:g}h-{(prev_x - start + 1) * cell:g}z")
            if x is not None:
                start, prev_x, prev_c = x, x, col
    return "".join(f'<path fill="{C[c]}" d="{"".join(d)}"/>' for c, d in by_col.items())


def sparrow_fragment(x, y, cell, uid="sp"):
    sky, ground = _scene()
    span = N * cell
    return f'''<g transform="translate({x} {y})" shape-rendering="crispEdges">
  <clipPath id="{uid}clip"><rect width="{span}" height="{span}"/></clipPath>
  <g clip-path="url(#{uid}clip)">
    {_rects(sky, cell)}
    <g>{_rects(CLOUD, cell, 3, 4)}
      <animateTransform attributeName="transform" type="translate" dur="16s" repeatCount="indefinite" calcMode="discrete"
        values="{";".join(f"{i * cell} 0" for i in range(0, 36))};{-6 * cell} 0" keyTimes="{";".join(f"{i / 37:.4f}" for i in range(37))}"/>
    </g>
    <g>{_rects(CLOUD, cell, 20, 2)}
      <animateTransform attributeName="transform" type="translate" dur="22s" repeatCount="indefinite" calcMode="discrete"
        values="{";".join(f"{-i * cell} 0" for i in range(0, 26))};{12 * cell} 0" keyTimes="{";".join(f"{i / 27:.4f}" for i in range(27))}"/>
    </g>
    {_rects(ground, cell)}
    {bird_group(cell)}
    {heart_group(cell)}
  </g>
</g>'''


def bird_group(cell, dx=0, dy=0):
    """The hopping, blinking sparrow (32x32 local grid) offset by (dx, dy) cells."""
    bird, eye_open, eye_closed = _bird()
    return f'''<g>
      <animateTransform attributeName="transform" type="translate" dur="5s" repeatCount="indefinite" calcMode="discrete"
        values="0 0;0 {-cell};0 0;0 {-cell};0 0" keyTimes="0;.80;.84;.88;.92"/>
      {_rects(bird, cell, dx, dy)}
      <g>{_rects(eye_open, cell, dx, dy)}
        <animate attributeName="opacity" dur="3.7s" repeatCount="indefinite" calcMode="discrete" values="1;0;1" keyTimes="0;.93;.97"/>
      </g>
      <g opacity="0">{_rects(eye_closed, cell, dx, dy)}
        <animate attributeName="opacity" dur="3.7s" repeatCount="indefinite" calcMode="discrete" values="0;1;0" keyTimes="0;.93;.97"/>
      </g>
    </g>'''


def heart_group(cell, dx=0, dy=0):
    """A pixel heart that floats up from the sparrow's head every few seconds."""
    return f'''<g opacity="0">{_rects(HEART, cell, 26 + dx, 7 + dy)}
      <animateTransform attributeName="transform" type="translate" dur="6s" repeatCount="indefinite" calcMode="discrete"
        values="0 0;0 {-cell};{cell} {-2 * cell};{cell} {-3 * cell};0 {-4 * cell};0 {-5 * cell};0 0" keyTimes="0;.6;.67;.74;.81;.88;.95"/>
      <animate attributeName="opacity" dur="6s" repeatCount="indefinite" calcMode="discrete" values="0;1;0" keyTimes="0;.55;.92"/>
    </g>'''


if __name__ == "__main__":
    cell = 16
    with open(sys.argv[1], "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{N * cell}" height="{N * cell}">'
                f'{sparrow_fragment(0, 0, cell)}</svg>')
