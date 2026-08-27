"""Compose manim_code/ivd.py into manim_code/ivd_composed.py.

Unlike tools/recompose.py's JOBS list (which borrows an existing PORTRAIT,
chroma:none script.md purely for its header), this project doesn't have a
script.md of its own (it's driven by a recorded clip, not a written script) —
so the header is built directly here instead of through
parse_script()/compose_file(), which both require a VideoScript. Otherwise
this is the SAME portrait, chroma:none header every other PYQ project gets:
tools/composite.py keys the presenter into the bottom band of this frame, so
CHROMA is disabled and Manim renders the full background. The format matches
src/scene_codegen.build_header() exactly; see that function if the injected
globals ever change shape.

    python projects/interference-vs-diffraction/compose.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = Path(__file__).parent / "manim_code" / "ivd.py"
DST = Path(__file__).parent / "manim_code" / "ivd_composed.py"
HELPERS = ROOT / "src" / "manim_helpers.py"

THEME = {
    "name": "midnight",
    "background": "#0B1021",
    "background_style": "gradient",
    "gradient_to": "#161B33",
    "background_image": None,
    "primary": "#F2F5FF",
    "secondary": "#AEB9DE",
    "muted": "#5C6890",
    "accent": "#5B8DEF",
    "accent_2": "#F2A65A",
    "line": "#232B47",
    "font": "serif",
    "is_dark": True,
}
CHROMA = {
    "enabled": False,
    "color": "#00FF00",
    "zone": None,
    "safe": (0.0, 0.0, 1.0, 1.0),
    "animate_in": False,
    "gradient": False,
    "gradient_frac": 0.35,
}

HEADER = (
    "from __future__ import annotations\n"
    "from manim import *\n"
    "import numpy as np\n\n"
    "config.pixel_width = 1080\n"
    "config.pixel_height = 1920\n"
    "config.frame_width = 8.0\n"
    "config.frame_height = 14.222222\n"
    "config.frame_rate = 30\n"
    f'config.background_color = "{THEME["background"]}"\n\n'
    f"THEME = {THEME!r}\n"
    'ORIENTATION = "portrait"\n'
    f"CHROMA = {CHROMA!r}\n"
    # Hardcoded to the container mount point (see src/manim_render.py
    # CONTAINER_ROOT): no local Manim exists on this host, so this composed
    # file only ever renders inside `docker compose run app`, where the repo
    # is bind-mounted at /app regardless of where it sits on the host.
    "ASSET_ROOT = '/app'\n"
    "IMAGES = []\n"
    "CUES_PATH = ''\n\n"
)

STRIP = (r"^from manim import \*.*$",
         r"^import numpy as np$",
         r"^from src\.manim_helpers import \([^)]*\)",
         r"^from src\.manim_helpers import .*$")


def main():
    body = SRC.read_text(encoding="utf-8")
    for pat in STRIP:
        body = re.sub(pat, "", body, flags=re.M)

    helper_body = HELPERS.read_text(encoding="utf-8").replace(
        "from __future__ import annotations\n", "")

    out = (HEADER
           + "# --- injected scaffolding (src/manim_helpers.py) ---\n"
           + helper_body
           + "\n\n# --- generated scene ---\n"
           + body + "\n")
    DST.write_text(out, encoding="utf-8")
    print(f"{DST} ({len(out.splitlines())} lines)")


if __name__ == "__main__":
    main()
