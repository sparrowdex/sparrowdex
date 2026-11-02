"""Generate the animated cursive header in dark- and light-mode variants.

Run from the repo root:  python scripts/create_header_title.py
Outputs: images/header_title.svg (dark mode) and images/header_title_light.svg
"""
import base64

from svgtext import glyph_paths, load_font

TEXT = "Hi there, Sreeja here!"
SIZE = 44
WIDTH, HEIGHT = 520, 70
BASELINE = 46
ANGEL_SIZE = 44
GAP = 10

VARIANTS = {
    "images/header_title.svg": "#FFFFFF",        # dark mode
    "images/header_title_light.svg": "#3B1F2B",  # light mode (deep plum)
}

def embed_png(path, px):
    """Base64 a PNG, downscaled to `px` (3x display size) when Pillow is available."""
    try:
        import io
        from PIL import Image
        im = Image.open(path).convert("RGBA")
        im.thumbnail((px, px), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "PNG", optimize=True)
        data = buf.getvalue()
    except ImportError:
        with open(path, "rb") as f:
            data = f.read()
    return base64.b64encode(data).decode()


angel_b64 = embed_png("images/cute sonny angel-modified.png", ANGEL_SIZE * 3)

font = load_font("GreatVibes.ttf")
glyphs, text_w = glyph_paths(font, TEXT, SIZE)
x0 = (WIDTH - text_w) / 2  # text centered on the canvas; angel sits just after it

css, paths = [], []
for i, (ch, d, _) in enumerate(glyphs):
    if not d:
        continue  # spaces
    delay = round(0.05 * i, 2)
    css.append(f"      .c-{i} {{ animation: appear .3s {delay}s ease-out forwards; }}")
    paths.append(f'    <path class="g c-{i}" d="{d}"/>')

angel_delay = round(0.05 * len(TEXT) + 0.1, 2)

for out, fill in VARIANTS.items():
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" fill="none">
  <title>{TEXT}</title>
  <style>
      .g {{ fill: {fill}; opacity: 0; transform: translateY(4px); }}
      @keyframes appear {{ to {{ opacity: 1; transform: translateY(0); }} }}
{chr(10).join(css)}
      .angel {{ opacity: 0; animation: pop .5s {angel_delay}s cubic-bezier(.3,1.6,.5,1) forwards;
               transform-origin: center; transform-box: fill-box; }}
      @keyframes pop {{ from {{ opacity: 0; transform: scale(.4) rotate(-20deg); }}
                        to {{ opacity: 1; transform: scale(1) rotate(0); }} }}
      @media (prefers-reduced-motion: reduce) {{ .g, .angel {{ animation: none; opacity: 1; transform: none; }} }}
  </style>
  <g transform="translate({x0:.1f}, {BASELINE})">
{chr(10).join(paths)}
  </g>
  <image class="angel" href="data:image/png;base64,{angel_b64}" x="{x0 + text_w + GAP:.1f}" y="{BASELINE - ANGEL_SIZE + 6}" width="{ANGEL_SIZE}" height="{ANGEL_SIZE}"/>
</svg>
'''
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {out}")
