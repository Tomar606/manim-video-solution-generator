"""The OpenAI images/edits call, ported from notes-editor's handwrite.py.

Kept on stdlib ``urllib`` + hand-rolled multipart rather than the ``openai``
SDK, deliberately: this is the exact request shape that produces the approved
notes-editor output — ``image[]`` as repeated parts with the canvas first, and
``input_fidelity=high`` to hold the base paper and the reference hand. Going
through the SDK would put a version-dependent layer between us and a request
that is known to work.
"""
from __future__ import annotations

import base64
import io
import json
import os
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

EDITS_URL = "https://api.openai.com/v1/images/edits"

PAGE_SIZE = (1024, 1536)          # portrait notebook page the API returns
DEFAULT_MODEL = "gpt-image-2"
DEFAULT_QUALITY = "medium"

# Transient failures worth another attempt: rate limit, origin errors.
_RETRY_CODES = (429, 500, 502, 503, 504, 520, 521, 522, 523, 524)

_ENV_LOADED = False


def load_env() -> None:
    """Read the repo-root .env into os.environ, once.

    Loaded here rather than at an entry point (the way notes-editor does it in
    spellfix) so the package works the same whether it is driven by
    ``python -m EndScreenshot``, by ``video endscreenshot``, or imported from
    another script — none of which can be relied on to have loaded .env.
    Existing environment variables always win.
    """
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    _ENV_LOADED = True
    path = Path(__file__).resolve().parents[1] / ".env"
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip("'\""))
    except OSError:
        pass


class EndScreenshotError(RuntimeError):
    """Raised when an image cannot be produced (auth, quota, bad response)."""


def png_bytes(img) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _multipart(fields: dict, files: list) -> tuple[bytes, str]:
    """Encode fields + (name, filename, png_bytes) files as multipart."""
    boundary = "----endscreenshot" + uuid.uuid4().hex
    out = io.BytesIO()
    for name, value in fields.items():
        out.write(f"--{boundary}\r\nContent-Disposition: form-data; "
                  f"name=\"{name}\"\r\n\r\n{value}\r\n".encode())
    for name, filename, data in files:
        out.write(f"--{boundary}\r\nContent-Disposition: form-data; "
                  f"name=\"{name}\"; filename=\"{filename}\"\r\n"
                  f"Content-Type: image/png\r\n\r\n".encode())
        out.write(data)
        out.write(b"\r\n")
    out.write(f"--{boundary}--\r\n".encode())
    return out.getvalue(), boundary


def fit_page(img):
    """Letterbox any page image onto the exact API canvas size.

    Padded with the page's own top-edge colour rather than black, so the model
    never sees a hard bar it might reproduce as part of the paper.
    """
    from PIL import Image

    im = img.convert("RGB")
    tw, th = PAGE_SIZE
    s = min(tw / im.width, th / im.height)
    im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))),
                   Image.LANCZOS)
    pad = im.getpixel((im.width // 2, 2))
    canvas = Image.new("RGB", (tw, th), pad)
    canvas.paste(im, ((tw - im.width) // 2, (th - im.height) // 2))
    return canvas


def model_name() -> str:
    load_env()
    return os.environ.get("OPENAI_IMAGE_MODEL", DEFAULT_MODEL)


def quality_name(quality: str | None = None) -> str:
    load_env()
    return quality or os.environ.get("OPENAI_HANDWRITE_QUALITY", DEFAULT_QUALITY)


def edit_image(images: list, prompt: str, quality: str | None = None):
    """One images/edits call: first image is the canvas, the rest are refs."""
    from PIL import Image

    load_env()
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        raise EndScreenshotError(
            "OPENAI_API_KEY is not set — add it to .env in the repo root."
        )
    fields = {
        "model": model_name(),
        "prompt": prompt,
        "size": f"{PAGE_SIZE[0]}x{PAGE_SIZE[1]}",
        "quality": quality_name(quality),
        "n": "1",
        "input_fidelity": "high",   # keep the base paper + the hand faithful
    }
    files = [("image[]", f"img{i}.png", png_bytes(im))
             for i, im in enumerate(images)]

    def build_request():
        body, boundary = _multipart(fields, files)
        return urllib.request.Request(
            EDITS_URL, data=body, method="POST", headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            })

    req = build_request()
    last_err = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                data = json.loads(resp.read())
            items = data.get("data", [])
            if not items:
                raise EndScreenshotError("the image API returned no images")
            raw = base64.b64decode(items[0].get("b64_json", ""))
            im = Image.open(io.BytesIO(raw)).convert("RGB")
            if im.size != PAGE_SIZE:
                im = im.resize(PAGE_SIZE, Image.LANCZOS)
            return im
        except urllib.error.HTTPError as e:
            detail = ""
            try:
                detail = json.loads(e.read()).get("error", {}).get("message", "")
            except Exception:
                pass
            # Older image models reject input_fidelity; drop it and retry once.
            if e.code == 400 and "input_fidelity" in detail \
                    and "input_fidelity" in fields:
                fields.pop("input_fidelity")
                req = build_request()
                continue
            last_err = EndScreenshotError(
                f"image API error {e.code}: {detail or e.reason}")
            if e.code not in _RETRY_CODES or attempt == 2:
                raise last_err from None
            time.sleep(5 * (attempt + 1))
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_err = EndScreenshotError(f"could not reach the image API: {e}")
            if attempt == 2:
                raise last_err from None
            time.sleep(4)
    raise last_err
