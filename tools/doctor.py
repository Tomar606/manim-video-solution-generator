"""Is this machine ready to make a reel? One command, every check, each with its fix.

    python tools/doctor.py [--flow]

Run it on a new machine, after an update, and before a render. Every check here is something that broke a
real render or delivery and looked like something else at the time:

  * memory and disk: an 8 GB machine swaps, the swap file eats the disk, and the render freezes the box;
  * the headless browser: another Playwright install on the machine deleted this repo's build, and the
    frames renderer failed at launch;
  * Hindi shaping: Pillow without raqm draws Devanagari with its matras in the wrong place, silently;
  * fonts, the Mixkit sounds (the public repo cannot carry them), ffmpeg, pdftoppm, the API key;
  * --flow: that the Flow bridge answering on port 8765 is THIS repo's extension, not another project's.
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = ROOT / ".venv-tools" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
results: list[tuple[bool, str, str]] = []


def check(ok: bool, what: str, fix: str = "") -> None:
    results.append((ok, what, fix))


def run(*cmd: str, env: dict | None = None) -> tuple[int, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, env=env, timeout=120)
        return r.returncode, (r.stdout + r.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, str(e)


def main() -> int:
    check(PY.exists(), "Python tools environment (.venv-tools)", "create it: python3 -m venv .venv-tools && "
          ".venv-tools/bin/pip install -r requirements.txt")
    rc, out = run(str(PY), str(ROOT / "tools/machine_guard.py"), "--need-disk", "8", "--need-ram", "2.5")
    check(rc == 0, "memory and disk headroom: " + (out.splitlines()[0].strip() if out else "?"),
          "close other apps (browsers, chat, music), or restart the machine to free swap; free disk space")
    for tool in ("ffmpeg", "ffprobe", "node", "pdftoppm"):
        check(shutil.which(tool) is not None, f"{tool} on the PATH",
              "brew install ffmpeg node poppler" if platform.system() == "Darwin" else f"install {tool}")
    env = dict(os.environ)
    if Path("/opt/homebrew/lib").exists():
        env["DYLD_LIBRARY_PATH"] = "/opt/homebrew/lib"
    rc, out = run(str(PY), "-c", "from PIL import features; print(features.check('raqm'))", env=env)
    check(rc == 0 and out.endswith("True"), "Hindi text shaping in Pillow (raqm)",
          "brew install libraqm fribidi; run tools with DYLD_LIBRARY_PATH=/opt/homebrew/lib (CLAUDE.md, Pillow)")
    # the plans, captions and meta are Hindi in UTF-8; Windows Python reads files in the system code page unless
    # told otherwise, and Devanagari bytes then fail to decode (or turn to garbage) far from the cause
    rc, out = run(str(PY), "-c", "import sys, locale; print(bool(sys.flags.utf8_mode) or "
                  "locale.getpreferredencoding(False).lower().replace('-', '') == 'utf8')")
    check(rc == 0 and out.endswith("True"), "Python reads the kit's Hindi files as UTF-8",
          "Windows: run  setx PYTHONUTF8 1  once in a terminal, then open a new one")
    rc, out = run(str(PY), "-c", "import numpy, facenet_pytorch; from rapidocr_onnxruntime import RapidOCR; print(numpy.__version__)")
    check(rc == 0, "Veo text check (RapidOCR) installed beside the face gates",
          "pip install -r requirements-tools.txt (numpy must stay below 2 for facenet-pytorch)")
    # headless renders use the separate headless shell of the same revision as the full browser's path names
    rc, out = run("node", "-e", "const {chromium}=require('playwright');const fs=require('fs'),path=require('path');"
                  "const p=chromium.executablePath(),rev=p.match(/chromium-(\\d+)/)[1];"
                  "console.log(fs.existsSync(path.join(p.split('chromium-'+rev)[0],'chromium_headless_shell-'+rev)))",
                  env={**os.environ, "NODE_PATH": str(ROOT / "tools/edu/renderer/node_modules"),
                       "PLAYWRIGHT_BROWSERS_PATH": str(ROOT / "tools/edu/renderer/.browsers")})
    check(rc == 0 and out.endswith("true"), "headless Chromium for the frames renderer (tools/edu/renderer/.browsers)",
          "cd tools/edu/renderer, set PLAYWRIGHT_BROWSERS_PATH=.browsers, then: npx playwright install --only-shell chromium")
    fonts = ROOT / "library/elements/fonts"
    need = ["TiroDevanagariHindi-Regular.ttf", "Martel-ExtraBold.ttf", "RozhaOne-Regular.ttf", "YatraOne-Regular.ttf"]
    lost = [f for f in need if not (fonts / f).exists()]
    check(not lost, "theme fonts in library/elements/fonts", f"missing: {', '.join(lost)}")
    try:
        sm = json.loads((ROOT / "library/sfx/manifest.json").read_text())
        gone = [s["file"] for s in sm.get("sounds", []) if not (ROOT / "library" / s["file"]).exists()]
    except (OSError, ValueError, KeyError):
        gone = ["(manifest unreadable)"]
    check(not gone, f"sound effects on disk ({len(gone)} missing)" if gone else "sound effects on disk",
          "run .venv-tools/bin/python tools/fetch_mixkit.py")
    envf = ROOT / ".env"
    keys = dict(l.split("=", 1) for l in envf.read_text().splitlines() if "=" in l and not l.startswith("#")) if envf.exists() else {}
    check(bool(keys.get("OPENAI_API_KEY", "").strip()), "OPENAI_API_KEY in .env (Whisper word clock)",
          "add it to .env; without credits, captions fall back to tools/pause_align.py")
    if "--flow" in sys.argv:
        rc, out = run(str(PY), "-c", "import sys; sys.path.insert(0, '.'); from src.flow_bridge import FlowBridge\n"
                      "b = FlowBridge().start(); print(b.wait_for_worker(timeout=60)); b.stop()")
        check(rc == 0, "Flow bridge: this repo's extension answering on port 8765",
              "Chrome: chrome://extensions -> Developer mode -> Load unpacked -> flow/extension; open a Flow project "
              "tab; set Portrait 9:16 and 1 output per prompt")

    width = max(len(w) for _, w, _ in results)
    for ok, what, fix in results:
        print(f"  {'ok  ' if ok else 'FIX '} {what.ljust(width)}" + ("" if ok else f"\n        -> {fix}"))
    bad = sum(1 for ok, _, _ in results if not ok)
    print(f"\n  {len(results) - bad} ok, {bad} to fix" + ("" if bad else ": ready"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
