"""Render the chapter header (CHAPTER - NN | Name) as HTML/CSS and rasterize
it to a transparent PNG overlay with a headless browser.

Doing the type in real CSS -- correct font, letter-spacing, weight -- reproduces
the design far more faithfully than hand-placing glyphs with Pillow. The overlay
is the full template width with a transparent background, so it drops straight
onto the template.

Two layout modes (config `header.use_template_divider`):
  * true  -- the template already contains the "|" divider. The label is
             right-anchored just left of it, the name left-anchored just right
             of it. No divider is drawn.
  * false -- the whole "CHAPTER - NN | Name" unit (including a styled divider)
             is drawn as one flex row starting at `text_left`.

The chapter text is identical for every page in a job, so this is rendered once
per job and reused.
"""

from __future__ import annotations

import base64
import html as _html
import io
from functools import lru_cache
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent


@lru_cache(maxsize=4)
def _font_data_uri(font_path: str) -> str:
    b64 = base64.b64encode(Path(font_path).read_bytes()).decode("ascii")
    return f"data:font/ttf;base64,{b64}"


def _common_css(h: dict, tw: int, font_uri: str) -> str:
    return f"""
  @font-face {{
    font-family:'Urbanist';
    src:url('{font_uri}') format('truetype');
    font-weight:100 900;
  }}
  *{{margin:0;padding:0;box-sizing:border-box}}
  html,body{{width:{tw}px;height:{h['canvas_height']}px;background:transparent}}
  .txt{{
    position:absolute;
    font-family:'Urbanist',sans-serif;
    font-weight:{h['font_weight']};
    font-size:{h['font_size']}px;
    letter-spacing:{h['letter_spacing']}px;
    line-height:1;white-space:nowrap;
  }}
  .label{{color:{h['label_color']}}}
  .name{{color:{h['name_color']}}}
"""


def _html_anchored(number: str, name: str, h: dict, tw: int, font_uri: str) -> str:
    """Label LEFT-anchored at a fixed x (so 1- and 2-digit numbers start in the
    same place); name left-anchored right of the template's divider, wrapping to
    up to `name_max_lines` lines when long."""
    number = _html.escape(number.strip())
    name = _html.escape(name.strip())
    dv = h["divider_x"]
    label_left = h.get("label_left", h.get("text_left", 180))
    name_left = dv + h["name_gap"]
    lh = h.get("name_line_height", 1.06)
    label = f"{h['label_prefix']}{number}" if number else ""

    # Width/wrap are decided in JS (prefer one line, wrap to balanced two lines
    # only when needed). CSS just sets the starting single-line state.
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{_common_css(h, tw, font_uri)}
  #label{{left:{label_left}px;top:{h['center_y']}px;transform:translateY(-50%);
         text-align:left;white-space:nowrap}}
  #name{{left:{name_left}px;top:{h['center_y']}px;transform:translateY(-50%);
        text-align:left;white-space:nowrap;line-height:{lh};
        overflow-wrap:break-word}}
</style></head><body>
  <div id="label" class="txt label">{label}</div>
  <div id="name" class="txt name">{name}</div>
</body></html>"""


def _html_flex(number: str, name: str, h: dict, tw: int, font_uri: str) -> str:
    """Whole unit incl. a drawn divider as one flex row (template has no divider)."""
    number = _html.escape(number.strip())
    name = _html.escape(name.strip())
    dv = h.get("divider", {"width": 3, "height": 54, "color": "#12303a", "radius": 2})
    label = f'<span class="label">{h["label_prefix"]}{number}</span>' if number else ""
    divider = (
        f'<span class="divider"></span>'
        if number and name and dv.get("width", 0) > 0 else ""
    )
    name_span = f'<span class="name">{name}</span>' if name else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{_common_css(h, tw, font_uri)}
  #bar{{left:{h['text_left']}px;top:{h['center_y']}px;transform:translateY(-50%);
       display:flex;align-items:center;
       max-width:{h['name_max_right'] - h['text_left']}px;}}
  #bar.txt{{white-space:nowrap}}
  .divider{{display:inline-block;width:{dv['width']}px;height:{dv['height']}px;
    background:{dv['color']};border-radius:{dv['radius']}px;
    margin:0 {h['name_gap']}px;flex:0 0 auto;}}
</style></head><body>
  <div id="bar" class="txt">{label}{divider}{name_span}</div>
</body></html>"""


def render_header(number: str, name: str, cfg: dict) -> Image.Image:
    """Render the header overlay as a full-template-width RGBA image."""
    h = cfg["header"]
    tw, _ = cfg["template_size"]
    ch = h["canvas_height"]
    font_uri = _font_data_uri(str(HERE / cfg["font_path"]))
    anchored = h.get("use_template_divider", False)

    min_fs = h.get("name_min_font_size", 16)
    max_lines = h.get("name_max_lines", 2)
    line_h = h.get("name_line_height", 1.08)

    if anchored:
        html = _html_anchored(number, name, h, tw, font_uri)
    else:
        html = _html_flex(number, name, h, tw, font_uri)

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--force-color-profile=srgb"])
        page = browser.new_page(viewport={"width": tw, "height": ch}, device_scale_factor=1)
        page.set_content(html, wait_until="networkidle")

        if anchored:
            # Shrink the label so "CHAPTER - NN" always ends a fixed gap before
            # the divider (2-digit numbers get slightly smaller -> even spacing).
            label_left = h.get("label_left", h.get("text_left", 180))
            label_avail = h["divider_x"] - label_left - h.get("label_right_gap", 20)
            page.evaluate(
                """([avail, minFs]) => {
                    const el = document.getElementById('label');
                    if (!el || !el.textContent) return;
                    let fs = parseFloat(getComputedStyle(el).fontSize);
                    while (el.scrollWidth > avail && fs > minFs) {
                        fs -= 1; el.style.fontSize = fs + 'px';
                    }
                }""",
                [label_avail, h.get("label_min_font_size", 24)],
            )

            zone_w = h["name_max_right"] - (h["divider_x"] + h["name_gap"])
            one_line_min = h.get("name_one_line_min", 26)
            max_h = h.get("name_max_height", 92)
            # Prefer one line (shrink a little); wrap to balanced N lines only if
            # one line would get too small; then size to fit width AND box height.
            page.evaluate(
                """([zoneW, oneLineMin, minFs, maxLines, maxH, lineH, startFs]) => {
                    const el = document.getElementById('name');
                    if (!el) return;
                    // --- try one line ---
                    el.style.whiteSpace = 'nowrap';
                    el.style.width = 'auto';
                    el.style.textWrap = '';
                    let fs = startFs; el.style.fontSize = fs + 'px';
                    while (el.scrollWidth > zoneW && fs > oneLineMin) {
                        fs -= 1; el.style.fontSize = fs + 'px';
                    }
                    if (el.scrollWidth <= zoneW) return;   // fits on one line
                    // --- wrap to balanced lines ---
                    el.style.whiteSpace = 'normal';
                    el.style.width = zoneW + 'px';
                    el.style.textWrap = 'balance';
                    fs = startFs; el.style.fontSize = fs + 'px';
                    const overflow = () => {
                        const lines = Math.round(el.offsetHeight / (fs * lineH));
                        return lines > maxLines
                            || el.offsetHeight > maxH
                            || el.scrollWidth > el.clientWidth + 1;
                    };
                    while (overflow() && fs > minFs) {
                        fs -= 1; el.style.fontSize = fs + 'px';
                    }
                }""",
                [zone_w, one_line_min, min_fs, max_lines, max_h, line_h,
                 h["font_size"]],
            )
        else:
            max_w = h["name_max_right"] - h["text_left"]
            page.evaluate(
                """([maxW, minFs]) => {
                    const el = document.getElementById('bar');
                    if (!el) return;
                    let fs = parseFloat(getComputedStyle(el).fontSize);
                    while (el.scrollWidth > maxW && fs > minFs) {
                        fs -= 1; el.style.fontSize = fs + 'px';
                    }
                }""",
                [max_w, min_fs],
            )

        png = page.screenshot(omit_background=True)
        browser.close()

    return Image.open(io.BytesIO(png)).convert("RGBA")
