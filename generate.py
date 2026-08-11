#!/usr/bin/env python3
"""Concept & derivation video generator.

Input: an authored script (narration + equations, multi-speaker) — see
scripts/quadratic_formula.md. Output: a rendered explainer video with themed
Manim animations, multi-voice ElevenLabs narration, optional chroma-key zones,
in landscape or portrait.

Usage:
    python generate.py scripts/quadratic_formula.md
    python generate.py my_script.md --orientation portrait --theme charcoal
    python generate.py my_script.md --chroma lower_third --animate-chroma
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from src.assemble import assemble
from src.config import ChromaPreset, ChromaZone, Orientation
from src.scene_codegen import (
    generate_segment_code,
    load_prewritten_source,
    render_prewritten,
)
from src.script_parser import parse_script_file
from src.themes import resolve_theme
from src.tts_elevenlabs import synthesize_script

load_dotenv()


def apply_overrides(script, args) -> None:
    if args.orientation:
        script.orientation = Orientation.parse(args.orientation)
    if args.theme:
        script.theme = resolve_theme(args.theme)
    if getattr(args, "fps", None):
        script.fps = args.fps
    if getattr(args, "voice", None):
        for spk in script.speakers.values():
            spk.voice_id = args.voice
    if args.chroma or args.animate_chroma or args.chroma_gradient:
        preset = ChromaPreset.parse(args.chroma) if args.chroma else script.chroma.preset
        script.chroma = ChromaZone(
            preset=preset,
            color=args.chroma_color or script.chroma.color,
            animate_in=args.animate_chroma or script.chroma.animate_in,
            gradient=args.chroma_gradient or script.chroma.gradient,
            gradient_frac=(args.chroma_gradient_frac
                           if args.chroma_gradient_frac is not None
                           else script.chroma.gradient_frac),
        )


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate a concept/derivation video.")
    ap.add_argument("script", help="Path to the authored script (.md/.txt)")
    ap.add_argument("--output", default="./output", help="Output root directory")
    ap.add_argument("--orientation", choices=["landscape", "portrait"],
                    help="Override the script's orientation")
    ap.add_argument("--theme", help="Override the script's theme (name)")
    ap.add_argument("--fps", type=int, help="Override the script's frame rate")
    ap.add_argument("--voice", help="Override every speaker's voice (name or voice_id)")
    ap.add_argument("--chroma", help="Chroma preset: none|lower_third|bottom_half|...")
    ap.add_argument("--chroma-color", help="Chroma key color (default #00FF00)")
    ap.add_argument("--animate-chroma", action="store_true",
                    help="Transition the chroma zone in instead of showing it statically")
    ap.add_argument("--chroma-gradient", action="store_true",
                    help="Fade the theme background into the chroma zone (soft blend)")
    ap.add_argument("--chroma-gradient-frac", type=float, default=None,
                    help="Top fraction of the zone used for the fade (default 0.35)")
    ap.add_argument("--continue-on-error", action="store_true",
                    help="Drop segments that fail to render instead of aborting")
    ap.add_argument("--max-attempts", type=int, default=4,
                    help="Render-repair attempts per segment (Claude mode)")
    ap.add_argument("--scenes-dir",
                    help="Offline mode: render pre-written SegmentScene files "
                         "(segment_NNN.py) from this dir instead of calling Claude")
    ap.add_argument("--no-audio", action="store_true",
                    help="Skip ElevenLabs TTS; render silent video with estimated "
                         "timing (free render-path validation)")
    args = ap.parse_args()

    if not Path(args.script).exists():
        print(f"❌ Script not found: {args.script}")
        return 1

    offline = bool(args.scenes_dir)
    if not offline and not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ No ANTHROPIC_API_KEY set and no --scenes-dir provided.\n"
              "   Scene generation needs Claude. Either set ANTHROPIC_API_KEY, "
              "or supply hand-written scenes via --scenes-dir (offline mode).")
        return 1

    script = parse_script_file(args.script)
    apply_overrides(script, args)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    root = Path(args.output)
    dirs = {name: root / name for name in
            ("audio", "manim_code", "media", "work", "final")}
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)

    print("=" * 78)
    print(f"🎬  {script.title}")
    print(f"    orientation={script.orientation.value}  theme={script.theme.name}  "
          f"chroma={script.chroma.preset.value}")
    print(f"    segments={len(script.segments)}  "
          f"speakers={', '.join(script.speakers)}")
    print("=" * 78)

    # 1) Narration (multi-voice) — measured durations drive animation timing.
    if args.no_audio:
        print("\n🔇 Step 1/3: --no-audio — skipping TTS, timing from script...")
        import re
        for seg in script.segments:
            dur = None
            if seg.note:
                m = re.search(r"dur:\s*([\d.]+)", seg.note)
                if m:
                    dur = float(m.group(1))
            if dur is None:
                words = max(len(seg.narration.split()), 3)
                dur = round(max(2.5, words / 2.5 + 0.4), 2)
            seg.target_duration = dur
            seg.audio_path = None
    else:
        print("\n🔊 Step 1/3: Synthesizing narration (ElevenLabs)...")
        synthesize_script(script, str(dirs["audio"]))

    # 2) Per-segment themed animation.
    mode = "offline scenes" if offline else "Claude + render-repair"
    print(f"\n🎨 Step 2/3: Rendering segment animations ({mode})...")
    rendered: list[tuple] = []
    failures: list[int] = []
    for seg in script.segments:
        print(f"\n → segment {seg.index} [{seg.speaker}] "
              f"({seg.target_duration:.1f}s)")
        if offline:
            src = load_prewritten_source(args.scenes_dir, seg.index)
            if src is None:
                print(f"   seg {seg.index}: no scene file in {args.scenes_dir}")
                result = None
            else:
                result = render_prewritten(
                    script, seg, src,
                    out_dir=str(dirs["manim_code"]),
                    media_dir=str(dirs["media"]),
                )
        else:
            result = generate_segment_code(
                script, seg,
                out_dir=str(dirs["manim_code"]),
                media_dir=str(dirs["media"]),
                max_attempts=args.max_attempts,
            )
        if result is None:
            failures.append(seg.index)
            if not args.continue_on_error:
                print(f"\n❌ Segment {seg.index} failed after {args.max_attempts} "
                      f"attempts. Aborting (use --continue-on-error to skip).")
                return 2
            continue
        seg.manim_path, raw_video = result
        seg.video_path = raw_video
        rendered.append((seg, raw_video))

    if not rendered:
        print("\n❌ No segments rendered successfully.")
        return 2
    if failures:
        print(f"\n⚠️  Dropped failed segments: {failures}")

    # 3) Assemble.
    print("\n🔗 Step 3/3: Conforming, concatenating and muxing...")
    final_path = str(dirs["final"] / f"{_slug(script.title)}_{stamp}.mp4")
    assemble(script, rendered, str(dirs["work"]), final_path)

    print("\n" + "=" * 78)
    print("✅ Done.")
    print(f"   Final video: {final_path}")
    print("=" * 78)
    return 0


def _slug(text: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:40] or "video"


if __name__ == "__main__":
    sys.exit(main())
