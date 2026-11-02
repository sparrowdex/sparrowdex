"""Generate the retro 'say hi' section: RPG dialogue box + menu buttons.

Run from the repo root:  python scripts/create_contact.py
Outputs images/retro/{dialogue,btn_linkedin,btn_email,btn_instagram}.svg
"""
import os

from retro_svg import CAMERA, ENVELOPE, INK, LINKEDIN, button_svg, dialogue_svg
from sparrow_svg import sparrow_fragment

os.makedirs("images/retro", exist_ok=True)
files = {
    "dialogue": dialogue_svg(lambda x, y, cell: sparrow_fragment(x, y, cell, "pt")),
    "btn_linkedin": button_svg("LINKEDIN", LINKEDIN, {"B": "#3B9BE8", "W": INK["frame"]}, selected=True),
    "btn_email": button_svg("EMAIL", ENVELOPE, {"K": INK["yellow"], "W": INK["frame"]}),
    "btn_instagram": button_svg("INSTAGRAM", CAMERA, {"P": INK["pink"], "W": INK["frame"]}),
}
for name, svg in files.items():
    with open(f"images/retro/{name}.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote images/retro/{name}.svg")
