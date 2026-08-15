"""``python -m EndScreenshot`` — the three-stage flow from the shell.

    # S1+S2+S3(temp): free, nothing is drawn
    python -m EndScreenshot --question-file q.txt --answer-file a.txt \
        --topic "Berkeley and Hartley" --diagram fig.jpg

    # after reviewing the temp
    python -m EndScreenshot ... --topic "Berkeley and Hartley" --approve

Input may also be a screenshot of a textbook page (``--screenshot page.png``),
in which case the question and answer are read off it.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import DEFAULT_OUT, DEFAULT_SHEET, DEFAULT_STYLE
from .api import EndScreenshotError, model_name, quality_name
from .pipeline import run


def _read(value: str | None, path: str | None) -> str:
    if value:
        return value.strip()
    if path:
        return Path(path).read_text(encoding="utf-8").strip()
    return ""


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="EndScreenshot",
        description="Hand-written Q&A end card: review -> temp -> draw -> "
                    "watermark.")
    g = ap.add_argument_group("S1 input")
    g.add_argument("--question"), g.add_argument("--question-file")
    g.add_argument("--answer"), g.add_argument("--answer-file")
    g.add_argument("--screenshot", help="A photo/screenshot of the Q&A to read")
    g.add_argument("--topic", default="", help='Folder name, e.g. "Berkeley and Hartley"')

    g = ap.add_argument_group("S2 review + diagram")
    g.add_argument("--no-review", action="store_true",
                   help="Skip the answer check (renders exactly what you gave)")
    g.add_argument("--diagram", help="Figure: a local path or a URL")
    g.add_argument("--want-diagram", action="store_true",
                   help="This answer needs a figure; fail loudly if none found")
    g.add_argument("--diagram-row", type=int, default=2)
    g.add_argument("--diagram-width", type=float, default=0.44)
    g.add_argument("--provider", choices=["auto", "openai", "claude"],
                   help="Which model reviews/reads (default: the CLI backend)")

    g = ap.add_argument_group("S3 draw")
    g.add_argument("--approve", action="store_true",
                   help="Temp reviewed: draw the page and watermark it")
    g.add_argument("--sheet", default=str(DEFAULT_SHEET))
    g.add_argument("--style", default=str(DEFAULT_STYLE))
    g.add_argument("--out", default=str(DEFAULT_OUT))
    g.add_argument("--label", default="Q1")
    g.add_argument("--quality", choices=["low", "medium", "high"])
    g.add_argument("--watermark",
                   default=str(Path(__file__).resolve().parent / "assets"
                               / "watermark.png"))
    g.add_argument("--no-watermark", action="store_true")
    g.add_argument("--wm-scale", type=float, default=0.68)
    g.add_argument("--wm-opacity", type=float, default=3.0)
    return ap


def main(argv: list[str] | None = None) -> int:
    a = build_parser().parse_args(argv)
    print(f"EndScreenshot · model={model_name()} quality={quality_name(a.quality)}")
    try:
        r = run(question=_read(a.question, a.question_file),
                answer=_read(a.answer, a.answer_file),
                screenshot=a.screenshot or "", topic=a.topic,
                diagram=a.diagram, want_diagram=a.want_diagram,
                sheet=a.sheet, style=a.style, out_root=a.out,
                approve=a.approve, review=not a.no_review,
                question_label=a.label, quality=a.quality,
                provider=a.provider,
                diagram_row=a.diagram_row, diagram_width=a.diagram_width,
                watermark_path=None if a.no_watermark else a.watermark,
                watermark_scale=a.wm_scale, watermark_opacity=a.wm_opacity,
                log=lambda m: print(f"  {m}", flush=True))
    except (EndScreenshotError, ValueError, FileNotFoundError) as exc:
        print(f"❌ {exc}")
        return 2

    print(f"\n📁 {r['folder']}")
    for p in r["temps"]:
        print(f"   temp:  {p.name}")
    for p in r["pages"]:
        print(f"   FINAL: {p.name}")
    if r.get("awaiting_approval"):
        print("\n⏸  S3 paused after the temp — nothing spent yet.")
        print("   Review the temp, then re-run with --approve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
