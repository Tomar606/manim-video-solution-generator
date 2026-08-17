#!/usr/bin/env python3
"""The one command that drives everything.

    video new "Deriving the quadratic formula"   write a first-draft script
    video script <project>                       (re)generate the script
    video narrate <project>                      synthesize the narration
    video background <project>                   animate + render + assemble
    video avatar <project>                       briefs, or fetch/ingest clips
    video composite <project>                    key the presenter over it
    video qc <project>                           Claude reviews the frames
    video endscreenshot [project]                the hand-written Q&A end card
    video build <project>                        everything, in order
    video status [project]                       where each stage stands
    video doctor                                 is this machine set up?
    video dashboard                              open the browser UI

Every stage reads and writes the project folder, so they can be run in any
order, re-run safely, and driven from the CLI, the dashboard or Claude Code
without duplicating logic.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.project import DEFAULT_PROJECTS_DIR, Project, slugify

load_dotenv()


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #
def _load_script(project: Project, *, resolve: bool = True):
    from src.script_parser import parse_script_file
    if not project.script_path.exists():
        raise SystemExit(
            f"❌ No script at {project.script_path}\n"
            f"   Write one, or generate a draft:  video script {project.slug}"
        )
    script = parse_script_file(str(project.script_path),
                               assets_dir=str(project.assets_dir), resolve=resolve)
    # The script may have arrived by any route — generated, hand-written, or
    # edited in the dashboard. If it parses, that stage is done.
    if project.stage("script").get("status") != "done":
        project.set_stage("script", "done", path=str(project.script_path))
    return script


def _apply_cli_overrides(script, args) -> None:
    from src.config import ChromaPreset, ChromaZone, Orientation
    from src.themes import resolve_theme

    if getattr(args, "orientation", None):
        script.orientation = Orientation.parse(args.orientation)
    if getattr(args, "theme", None):
        script.theme = resolve_theme(args.theme)
    if getattr(args, "voice", None):
        for spk in script.speakers.values():
            spk.voice_id = args.voice
    if getattr(args, "chroma", None):
        script.chroma = ChromaZone(preset=ChromaPreset.parse(args.chroma),
                                   color=script.chroma.color,
                                   animate_in=script.chroma.animate_in)


def _banner(script, project: Project) -> None:
    print("=" * 78)
    print(f"🎬  {script.title}   ({project.slug})")
    print(f"    orientation={script.orientation.value}  theme={script.theme.name}  "
          f"chroma={script.chroma.preset.value}")
    print(f"    segments={len(script.segments)}  "
          f"speakers={', '.join(script.speakers)}  "
          f"images={len(script.images)}")
    print("=" * 78)


def _rendered_pairs(script, project: Project):
    """(segment, raw video) for segments already rendered, from job state."""
    state = project.stage("background").get("segments", {})
    pairs = []
    for seg in script.segments:
        info = state.get(str(seg.index))
        if not info:
            continue
        video = info.get("video")
        if video and Path(video).exists():
            seg.manim_path = info.get("manim")
            seg.video_path = video
            seg.target_duration = info.get("duration") or seg.target_duration
            seg.audio_path = info.get("audio") or seg.audio_path
            pairs.append((seg, video))
    return pairs


# --------------------------------------------------------------------------- #
# Stages                                                                       #
# --------------------------------------------------------------------------- #
def cmd_new(args) -> int:
    project = Project.create(args.topic, projects_dir=args.projects_dir,
                             slug=args.slug)
    project.set_config(topic=args.topic, language=args.language,
                       orientation=args.orientation, theme=args.theme,
                       chroma=args.chroma, voice=args.voice)
    print(f"✅ Created {project.root}")
    if args.no_script:
        print(f"   Write your script at {project.script_path}")
        return 0
    return cmd_script(argparse.Namespace(**{**vars(args), "project": project.slug}))


def cmd_script(args) -> int:
    from src.script_writer import save_script, write_script

    project = Project.open(args.project, projects_dir=args.projects_dir)
    topic = getattr(args, "topic", None) or project.config("topic") or project.title

    if project.script_path.exists() and not getattr(args, "force", False):
        print(f"⚠️  {project.script_path} already exists — pass --force to replace it.")
        return 1

    from src import style as style_mod

    guide = style_mod.load()
    project.set_stage("script", "running")
    print(f"✍️  Drafting a script for: {topic}")
    print(f"   voice reference: {guide.describe()}")
    try:
        markdown, report = write_script(
            topic,
            language=getattr(args, "language", None) or project.config("language", "hinglish"),
            orientation=getattr(args, "orientation", None) or project.config("orientation", "landscape"),
            theme=getattr(args, "theme", None) or project.config("theme", "midnight"),
            chroma=getattr(args, "chroma", None) or project.config("chroma", "none"),
            voice=getattr(args, "voice", None) or project.config("voice", "George"),
            answer_image=getattr(args, "answer_image", None),
            extra=getattr(args, "notes", "") or "",
            provider=getattr(args, "provider", None),
            style=guide,
            use_judge=getattr(args, "judge", False),
            max_attempts=getattr(args, "max_attempts", 3),
        )
    except Exception as exc:
        project.set_stage("script", "failed", error=str(exc))
        print(f"❌ {exc}")
        return 2

    save_script(markdown, project.script_path)
    project.set_stage("script", "done", path=str(project.script_path),
                      voice_score=report.score)
    print(f"\n✅ Draft written to {project.script_path}")
    print(f"   {report.describe()}")
    if not report.ok:
        print("   ↑ these survived the rewrite passes — worth a human look")
    print(f"\n   Read it, fix the wording, then:  video build {project.slug}")
    return 0


def cmd_eval(args) -> int:
    """Score an existing script for how spoken it sounds."""
    import json as _json

    from src import style as style_mod
    from src.script_eval import evaluate, judge, merge_judgement

    project = Project.open(args.project, projects_dir=args.projects_dir)
    script = _load_script(project, resolve=False)

    report = evaluate(script)
    if args.judge:
        guide = style_mod.load()
        print("🧑‍⚖️  Asking the model how it reads against your samples…")
        report = merge_judgement(
            report, judge(script, samples=guide.sample_text(4000),
                          provider=getattr(args, "provider", None)))

    print(f"\n📝 {script.title}")
    print(report.describe())
    stats = report.stats
    if stats:
        print(f"\n   {stats.get('beats')} beats · {stats.get('total_words')} words "
              f"· ~{stats.get('est_minutes')} min spoken "
              f"· avg {stats.get('avg_words')} words/beat")

    out = project.qc_dir / "script_eval.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_json.dumps(report.to_dict(), indent=2, ensure_ascii=False),
                   encoding="utf-8")
    print(f"\n   Written to {out}")
    return 0 if report.ok else 3


def cmd_spend(args) -> int:
    """What the paid keys have cost so far."""
    from src import usage

    data = usage.summary(since_days=args.days, project=args.project or "")
    print(usage.format_summary(data))
    if args.detail:
        print("\n  recent calls")
        for row in usage.entries(since_days=args.days,
                                 project=args.project or "")[-args.detail:]:
            cost = row.get("cost_usd")
            amount = f"${cost:.4f}" if cost is not None else "  ?  "
            print(f"    {row['ts']}  {amount}  {row['model']:<18} "
                  f"{row.get('stage') or '—':<12} {row.get('project') or ''}")
    return 0


def cmd_style(args) -> int:
    """Show (or scaffold) the voice reference the writer learns from."""
    from src import style as style_mod

    if args.init:
        base = style_mod.scaffold()
        print(f"✅ Created {base}")
        print(f"   Drop approved scripts into {base / 'samples'}/")
        print(f"   Add approved phrasings to {base / 'variations.yaml'}")
        return 0

    guide = style_mod.load()
    print(f"Voice reference: {guide.describe()}")
    if guide.is_empty:
        print("\n  Nothing loaded — the writer is using its built-in style.")
        print("  Set it up with:  video style --init")
        return 0
    for name, text in guide.samples:
        words = len(text.split())
        print(f"  sample   {name}  ({words} words)")
    for slot, options in guide.variations.items():
        print(f"  slot     {slot}: {len(options)} approved line(s)")
        for option in options[:2]:
            print(f"             · {option[:70]}")
    if guide.notes:
        print(f"  notes    {len(guide.notes.split())} words")
    print(f"  mode     {guide.mode}")
    return 0


def cmd_narrate(args) -> int:
    from src.tts_elevenlabs import synthesize_script

    project = Project.open(args.project, projects_dir=args.projects_dir)
    script = _load_script(project)
    _apply_cli_overrides(script, args)
    _banner(script, project)

    project.set_stage("narration", "running")
    if args.no_audio:
        import re
        print("🔇 --no-audio: estimating timing from the script instead of TTS")
        for seg in script.segments:
            if seg.target_duration:
                continue
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
        project.set_stage("narration", "skipped", reason="--no-audio")
    else:
        print("🔊 Synthesizing narration (ElevenLabs)...")
        try:
            synthesize_script(script, str(project.audio_dir))
        except Exception as exc:
            project.set_stage("narration", "failed", error=str(exc))
            print(f"❌ Narration failed: {exc}")
            return 2
        project.set_stage("narration", "done", clips=len(script.segments))

    # Timing is the contract between stages — persist it.
    state = project.state
    state.setdefault("timing", {})
    for seg in script.segments:
        state["timing"][str(seg.index)] = {
            "duration": seg.target_duration,
            "audio": seg.audio_path,
        }
    project.save(state)
    total = sum(s.target_duration or 0 for s in script.segments)
    print(f"✅ Narration ready — {total:.1f}s across {len(script.segments)} beats")
    return 0


def _restore_timing(script, project: Project) -> bool:
    timing = project.state.get("timing", {})
    if not timing:
        return False
    for seg in script.segments:
        info = timing.get(str(seg.index)) or {}
        if info.get("duration"):
            seg.target_duration = info["duration"]
        if info.get("audio"):
            seg.audio_path = info["audio"]
    return True


def cmd_background(args) -> int:
    from src.assemble import assemble
    from src.scene_codegen import (generate_segment_code, load_prewritten_source,
                                   render_prewritten)

    project = Project.open(args.project, projects_dir=args.projects_dir)
    script = _load_script(project)
    _apply_cli_overrides(script, args)

    if not _restore_timing(script, project):
        print("❌ No narration timing yet. Run:  video narrate " + project.slug)
        return 1
    _banner(script, project)

    offline = bool(args.scenes_dir)
    project.set_stage("background", "running")
    mode = "offline scenes" if offline else "Claude + render-repair"
    print(f"🎨 Rendering segment animations ({mode})...")

    rendered: list[tuple] = []
    failures: list[int] = []
    seg_state: dict[str, dict] = {}
    for seg in script.segments:
        print(f"\n → segment {seg.index} [{seg.speaker}] "
              f"({seg.target_duration or 0:.1f}s)")
        if offline:
            src = load_prewritten_source(args.scenes_dir, seg.index)
            result = None if src is None else render_prewritten(
                script, seg, src, out_dir=str(project.manim_code_dir),
                media_dir=str(project.media_dir))
            if src is None:
                print(f"   no scene file in {args.scenes_dir}")
        else:
            result = generate_segment_code(
                script, seg, out_dir=str(project.manim_code_dir),
                media_dir=str(project.media_dir), max_attempts=args.max_attempts,
                answer_title=args.answer_title)
        if result is None:
            failures.append(seg.index)
            if not args.continue_on_error:
                project.set_stage("background", "failed", failed_segment=seg.index)
                print(f"\n❌ Segment {seg.index} failed. "
                      f"Use --continue-on-error to skip past it.")
                return 2
            continue
        seg.manim_path, raw_video = result
        seg.video_path = raw_video
        rendered.append((seg, raw_video))
        seg_state[str(seg.index)] = {
            "manim": seg.manim_path, "video": raw_video,
            "duration": seg.target_duration, "audio": seg.audio_path,
        }

    if not rendered:
        project.set_stage("background", "failed", error="no segments rendered")
        print("\n❌ No segments rendered.")
        return 2
    if failures:
        print(f"\n⚠️  Dropped failed segments: {failures}")

    print("\n🔗 Conforming, concatenating and muxing...")
    try:
        assemble(script, rendered, str(project.work_dir),
                 str(project.background_video),
                 sound_effects=not args.no_sfx)
    except Exception as exc:
        project.set_stage("background", "failed", error=str(exc))
        print(f"❌ Assembly failed: {exc}")
        return 2

    project.set_stage("background", "done", segments=seg_state,
                      failed=failures, output=str(project.background_video))
    print(f"\n✅ Background video: {project.background_video}")
    return 0


def cmd_avatar(args) -> int:
    from src.avatar import apply_avatar_timing, get_provider, ingest, write_briefs

    project = Project.open(args.project, projects_dir=args.projects_dir)
    script = _load_script(project)
    _restore_timing(script, project)

    if args.briefs:
        manifest = write_briefs(script, project.briefs_dir)
        print(f"✅ Avatar briefs written to {project.briefs_dir}")
        print(f"   manifest: {manifest}")
        print(f"   Generate each clip in HeyGen and save it into "
              f"{project.avatar_dir}")
        project.set_stage("avatar", "pending", briefs=str(manifest))
        return 0

    provider = get_provider(args.provider)
    print(f"🧑 Avatar provider: {provider.name}")
    project.set_stage("avatar", "running", provider=provider.name)
    try:
        report = provider.fetch(script, project.avatar_dir)
    except Exception as exc:
        project.set_stage("avatar", "failed", error=str(exc))
        print(f"❌ {exc}")
        return 2

    print(report.describe())
    if script.avatar.timing == "avatar" and report.matched:
        apply_avatar_timing(script)
        state = project.state
        state.setdefault("timing", {})
        for seg in script.segments:
            if seg.target_duration:
                state["timing"][str(seg.index)] = {
                    "duration": seg.target_duration, "audio": seg.audio_path}
        project.save(state)
        print("   timing taken from the avatar clips (avatar.timing: avatar)")

    status = "done" if report.ok else "pending"
    project.set_stage("avatar", status, matched=len(report.matched),
                      missing=report.missing)
    if not report.ok:
        print(f"\n⚠️  Still missing clips for segments {report.missing}.")
        print(f"   Drop them into {project.avatar_dir} and run this again.")
    return 0


def cmd_composite(args) -> int:
    from src.avatar import ingest
    from src.composite import composite_video

    project = Project.open(args.project, projects_dir=args.projects_dir)
    script = _load_script(project)
    _restore_timing(script, project)

    rendered = _rendered_pairs(script, project)
    if not rendered:
        print("❌ No rendered background yet. Run:  video background "
              + project.slug)
        return 1

    report = ingest(script, project.avatar_dir)
    if not report.matched:
        print(f"⚠️  No avatar clips in {project.avatar_dir} — nothing to key.")
        print(f"   The background video is already complete at "
              f"{project.background_video}")
        return 1

    project.set_stage("composite", "running")
    print(f"🎭 Compositing {len(report.matched)} presenter clip(s)...")
    try:
        composite_video(script, [seg for seg, _ in rendered],
                        str(project.work_dir), str(project.final_video),
                        feather=args.feather)
    except Exception as exc:
        project.set_stage("composite", "failed", error=str(exc))
        print(f"❌ Compositing failed: {exc}")
        return 2

    project.set_stage("composite", "done", output=str(project.final_video))
    print(f"\n✅ Final video: {project.final_video}")
    return 0


def cmd_qc(args) -> int:
    from src.qc import review

    project = Project.open(args.project, projects_dir=args.projects_dir)
    script = _load_script(project)
    _restore_timing(script, project)

    rendered = _rendered_pairs(script, project)
    if not rendered:
        print("❌ Nothing rendered to review yet. Run:  video background "
              + project.slug)
        return 1

    project.set_stage("qc", "running")
    print(f"🔍 Reviewing {len(rendered)} segment(s) with Claude...")
    try:
        report = review(script, rendered, project.qc_dir, effort=args.effort)
    except Exception as exc:
        project.set_stage("qc", "failed", error=str(exc))
        print(f"❌ QC failed: {exc}")
        return 2

    project.set_stage("qc", "done", verdict=report["verdict"],
                      counts=report["counts"])
    icon = {"pass": "✅", "warn": "⚠️", "fail": "❌"}.get(report["verdict"], "")
    print(f"\n{icon} QC verdict: {report['verdict'].upper()}")
    print(f"   Report: {project.qc_dir / 'report.md'}")
    return 0 if report["verdict"] != "fail" else 3


def _es_default(which: str) -> Path:
    """Default EndScreenshot asset paths, resolved without importing the
    package (argparse builds every subparser on every run, and EndScreenshot
    pulls in Pillow)."""
    base = Path(__file__).resolve().parent / "EndScreenshot" / "assets"
    return base / ("blank_ruled.jpeg" if which == "sheet" else "sample_hand.jpg")


_BLANK_FIGURE_BOX = """FIGURE AREA — the faint grey figure printed in IMAGE 3
marks a region that must be left EMPTY on your page.

- Do NOT draw, sketch, trace or suggest that figure, or any figure, anywhere.
- Leave that whole rectangle as blank ruled paper: the printed rules carry
  straight across it exactly as they do everywhere else on the sheet, with
  nothing written or drawn on them.
- Write the handwritten answer around it, exactly as the reference layout shows
  — the text stops at the left edge of that rectangle on the lines it crosses,
  and resumes full width on the lines below it.
- Nothing may extend into the rectangle: no stray marks, no labels, no arrows,
  no part of any letter.
"""


def _paste_below(pages, figure: Path, width_frac: float = 0.62) -> None:
    """Draw the figure under whatever was written, measured off the page.

    Where it goes is measured, not reserved: the model's handwriting runs about
    five ruled rows looser than the typeset mock-up predicts, so a row index
    chosen up front lands on the last line of the answer. The last row that
    actually carries ink is unambiguous.
    """
    import numpy as np
    from PIL import Image

    fig = Image.open(figure).convert("RGBA")
    for page in pages:
        im = Image.open(page).convert("RGBA")
        pw, ph = im.size
        # Threshold at 105, not 130: the Arivihan WATERMARK is grey and runs
        # well down the page, and at 130 it counts as writing — the detector
        # then thinks the sheet is full and refuses to place the figure on a
        # page that is a third empty. Handwriting is a dark blue ballpoint and
        # sits far below either level.
        grey = np.asarray(im.convert("L")).astype(int)
        profile = (grey < 105).sum(axis=1) / pw
        window = max(9, ph // 50)
        smooth = np.convolve(profile, np.ones(window) / window, mode="same")
        rows = np.nonzero(smooth > 0.030)[0]
        top = (int(rows.max()) + int(ph * 0.030)) if len(rows) else int(ph * 0.55)

        avail_w, avail_h = int(pw * width_frac), ph - int(ph * 0.03) - top
        if avail_h < ph * 0.12:
            print("   figure: no room under the answer — page left as is")
            continue
        k = min(avail_w / fig.width, avail_h / fig.height)
        small = fig.resize((max(1, round(fig.width * k)),
                            max(1, round(fig.height * k))), Image.LANCZOS)
        im.alpha_composite(small, ((pw - small.width) // 2, top))
        im.convert("RGB").save(page)
        print(f"   figure: drawn below the answer at y={top}, "
              f"{small.width}x{small.height}")


def _paste_figure(pages, figure: Path, diagram) -> None:
    """Draw the real figure into the box the page reserved for it.

    The box goes through generation so the prose WRAPS around it — the reference
    sheet has the diagram inline at the top right with text flowing beside it,
    not stranded under the answer. But what the image model draws in that box is
    its own redrawing, and its Daniell cell came back with the electrode signs
    REVERSED and every Devanagari label garbled. On a figure whose entire content
    is which electrode is which, that is not a cosmetic loss.

    So the box is cleared and the drawn figure composited in. Clearing matters:
    compositing over the model's attempt left both figures visible on top of
    each other. The paper colour and the ruled lines that crossed the box are
    restored from the page itself, and the ruling is probed OUTSIDE the box —
    inside it, the model's drawing is in the way.
    """
    import numpy as np
    from PIL import Image

    fig = Image.open(figure).convert("RGBA")
    box = (int(diagram.x0), int(diagram.y0), int(diagram.x1), int(diagram.y1))
    w, h = box[2] - box[0], box[3] - box[1]
    if w < 8 or h < 8:
        print("   figure: reserved box is degenerate — page left as generated")
        return

    scale = min(w / fig.width, h / fig.height)
    small = fig.resize((max(1, round(fig.width * scale)),
                        max(1, round(fig.height * scale))), Image.LANCZOS)

    for page in pages:
        im = Image.open(page).convert("RGB")
        arr = np.array(im)
        ph, pw = arr.shape[:2]
        bx0, by0 = max(0, box[0]), max(0, box[1])
        bx1, by1 = min(pw, box[2]), min(ph, box[3])

        # Clear the WHOLE reserved rectangle, then put the ruling back.
        #
        # Clearing only the ink is gentler and leaves the paper's grain intact,
        # and it worked on the render where the model honoured "leave this area
        # empty". It does not hold: compliance varies run to run, and on the run
        # where the model wrote its answer straight across the box, ink-only
        # clearing left ghost words showing THROUGH the figure and dropped the
        # words it had written there off the end of their lines.
        #
        # Losing a word out of an answer is a content error; a slightly flatter
        # patch of paper is not. So the box is cleared outright, and the rules
        # that crossed it are redrawn from a probe OUTSIDE it, where the model's
        # drawing cannot interfere.
        region = arr[by0:by1, bx0:bx1].reshape(-1, 3)
        bright = region[region.min(axis=1) > 200]
        paper = (bright.mean(axis=0) if len(bright) > 20
                 else np.array([250.0, 250.0, 250.0])).astype(np.uint8)

        probe = bx1 + 12 if bx1 + 12 < pw else max(0, bx0 - 12)
        col = arr[by0:by1, probe].astype(int).mean(axis=1)
        rules, start, prev = [], None, None
        for i, v in enumerate(col):
            if v < float(paper.mean()) - 14:
                if start is None:
                    start = i
                prev = i
            elif start is not None and i - prev > 3:
                rules.append((start + prev) // 2)
                start = None
        if start is not None:
            rules.append((start + prev) // 2)

        arr[by0:by1, bx0:bx1] = paper
        for ry in rules:
            y = by0 + ry
            arr[max(by0, y - 1):y + 1, bx0:bx1] = arr[y, probe]

        im = Image.fromarray(arr).convert("RGBA")
        im.alpha_composite(small, (bx0 + (w - small.width) // 2,
                                   by0 + (h - small.height) // 2))
        im.convert("RGB").save(page)
    print(f"   figure: drawn in the reserved box {box}")



def cmd_endscreenshot(args) -> int:
    """Make the EndScreenshot photo: the Q&A card the video ends on.

    Two passes (see EndScreenshot/pipeline.py): step 1 mints the base sheet,
    step 2 writes the question and answer onto it. The temp is cached, so a
    re-run of the same sheet pays for step 2 alone.

    With a project, the pages land in its ``assets/`` so they can be referenced
    straight from the script's ``answer_image:``. Deliberately not recorded in
    job.json: STAGES is a fixed tuple, and the artifact on disk is the state —
    the same way a parseable script.md means the script stage is done.
    """
    import EndScreenshot as ES
    from EndScreenshot import prompts as ES_prompts

    def _read(value, path, what):
        if value:
            return value.strip()
        if path:
            return Path(path).read_text(encoding="utf-8").strip()
        raise SystemExit(f"❌ Give me the {what}: --{what} or --{what}-file")

    question = _read(args.question, args.question_file, "question")
    answer = _read(args.answer, args.answer_file, "answer")

    if args.project:
        project = Project.open(args.project, projects_dir=args.projects_dir)
        out_dir = project.assets_dir
        temp_dir = Path(args.temp_dir) if args.temp_dir else ES.DEFAULT_OUT / "temp"
    else:
        out_dir = Path(args.out or ES.DEFAULT_OUT)
        temp_dir = Path(args.temp_dir) if args.temp_dir else None

    if args.dry_run:
        info = ES.dry_run(question, answer, sheet=args.sheet,
                          question_label=args.label, heading=args.heading or "")
        print(f"{info['ruled_rows']} ruled rows, {info['usable_rows']} usable")
        print(f"content wants ~{info['wants_rows']} rows "
              f"-> {len(info['pages'])} page(s)")
        for line in info["lines"]:
            print(f"   {line}")
        return 0

    extra = "" if args.margin_line else ES_prompts.NO_MARGIN_OVERRIDE
    if args.notes:
        extra = (extra + "\n" + args.notes).strip()

    if getattr(args, "fresh_temp", False):
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    # A figure, for the questions that expect one on the page — an examiner
    # marks the labelled cell in "डेनियल सेल का उदाहरण देकर समझाइए", and no
    # amount of prose replaces it. Drawn by tools/answer_figure.py rather than
    # generated: a model gets the picture roughly right and the LETTERING wrong,
    # and on a figure about which electrode is which, the lettering is the whole
    # content. Passed as a path; EndScreenshot flows the text around it.
    figure, diagram = None, None
    if getattr(args, "diagram", None) and getattr(args, "diagram_below", False):
        # Below the prose, measured from the finished page. The reserved-box
        # route gives the reference's inline layout, but it depends on the model
        # honouring the gap — and it does so inconsistently: the same settings
        # that worked on one question wrote straight through the box on the next
        # and clipped words off the ends of lines. Losing a word from an answer
        # is a content error; a figure sitting under the text instead of beside
        # it is a layout preference. This path cannot clip anything.
        figure = Path(args.diagram)
        if not figure.exists():
            print(f"❌ diagram not found: {figure}")
            return 2
    elif getattr(args, "diagram", None):
        figure = Path(args.diagram)
        if not figure.exists():
            print(f"❌ diagram not found: {figure}")
            return 2
        # Reserved as a real Diagram so the prose WRAPS AROUND it, the way the
        # reference sheet has it — inline at the top right, not stranded below
        # the answer. What the model draws inside the box is erased afterwards
        # and replaced with the drawn figure; see _paste_figure.
        from EndScreenshot.typeset import Diagram
        diagram = Diagram(path=str(figure), row=args.diagram_row, rows=0,
                          width_frac=args.diagram_width, side=args.diagram_side)

    print(f"📸 EndScreenshot — {args.sheet}")
    try:
        result = ES.generate(
            question, answer,
            sheet=args.sheet, style=args.style,
            out_dir=out_dir, temp_dir=temp_dir, stem=args.stem or "answer",
            question_label=args.label, heading=args.heading or "",
            highlight=args.highlight, extra_rules=extra,
            quality=args.quality, max_pages=args.max_pages,
            temp_only=not getattr(args, "approve", False),
            diagram=diagram,
            # NOT ES_prompts.DIAGRAM_PROMPT. That asks the model to redraw the
            # figure itself, and its Daniell cell came back with the electrode
            # signs reversed and the Devanagari labels garbled — then spilled
            # its labels outside the reserved box, so erasing the box left a
            # duplicate set underneath ours. Asking for the space to be left
            # EMPTY gets the wrap for free and nothing to clean up: the real
            # figure is composited into it afterwards.
            diagram_rules=(_BLANK_FIGURE_BOX if diagram is not None else ""),
            # The reference sheet carries the Arivihan wordmark across the
            # middle, under the handwriting. Every page gets it.
            watermark_path=(None if args.no_watermark else args.watermark),
            watermark_scale=args.wm_scale, watermark_opacity=args.wm_opacity,
            # `--fresh-temp` is honoured by clearing the cached temp rather than
            # by a keyword: EndScreenshot.generate() does not take one, and
            # passing it raised TypeError on every run.
            log=lambda msg: print(f"   {msg}", flush=True),
        )
    except ES.EndScreenshotError as exc:
        print(f"❌ {exc}")
        return 2

    pages = result["pages"]
    if not pages:
        # temp_only is the default and is deliberate: the typeset mockup costs
        # nothing, so it is always produced first for review and no image is
        # paid for until someone has looked at it.
        print(f"\n📝 temp only — review it, then re-run with --approve")
        for temp in result.get("temps", []):
            print(f"   temp: {temp}")
        return 0
    if figure is not None:
        if diagram is not None:
            _paste_figure(pages, figure, diagram)
        else:
            _paste_below(pages, figure, args.diagram_width)

    print(f"\n✅ {len(pages)} page(s) · {result['images_generated']} image(s) generated")
    for path in pages:
        print(f"   page: {path}")
    if args.project and len(pages) == 1:
        print(f"\n   In script.md:  answer_image: assets/{pages[0].name}")
    return 0


def cmd_build(args) -> int:
    """Run the whole pipeline, stopping at the first stage that can't proceed."""
    project = Project.open(args.project, projects_dir=args.projects_dir)

    steps = [("narrate", cmd_narrate), ("background", cmd_background)]
    if not args.skip_qc:
        steps.append(("qc", cmd_qc))
    steps.append(("composite", cmd_composite))

    for name, fn in steps:
        print(f"\n{'─' * 78}\n▶  {name}\n{'─' * 78}")
        code = fn(args)
        if code != 0:
            if name == "composite":
                # No avatar clips yet is the normal state mid-production, not a
                # build failure — the background cut is still watchable.
                print(f"\n⏸  Stopped before compositing. "
                      f"Background is ready: {project.background_video}")
                return 0
            if name == "qc" and code == 3 and not args.strict_qc:
                print("⚠️  QC found problems — continuing anyway "
                      "(use --strict-qc to stop here).")
                continue
            return code
    print(f"\n🎉 Done: {project.final_video}")
    return 0


# --------------------------------------------------------------------------- #
# Introspection                                                                #
# --------------------------------------------------------------------------- #
def cmd_status(args) -> int:
    if args.project:
        projects = [Project.open(args.project, projects_dir=args.projects_dir)]
    else:
        projects = Project.list_all(args.projects_dir)
    if not projects:
        print(f"No projects yet in {args.projects_dir}/. "
              f'Start one:  video new "<topic>"')
        return 0
    for project in projects:
        print(f"\n📁 {project.slug}  —  {project.title}")
        print(f"   {project.summary()}")
        if project.final_video.exists():
            print(f"   final: {project.final_video}")
        elif project.background_video.exists():
            print(f"   background: {project.background_video}")
    return 0


def cmd_doctor(args) -> int:
    from src import llm

    print("Environment check\n" + "=" * 78)
    ok = True

    print(f"python           {sys.version.split()[0]}")

    for tool, why in (("ffmpeg", "video/audio processing"),
                      ("ffprobe", "media inspection")):
        path = shutil.which(tool)
        print(f"{tool:16s} {path or 'MISSING — ' + why}")
        ok = ok and bool(path)

    try:
        import manim  # noqa: F401
        print(f"manim            {manim.__version__}")
    except Exception:
        print("manim            not importable here "
              "(fine if you render in Docker)")

    from src import manim_render
    try:
        backend = manim_render.active_backend()
    except ValueError as exc:
        backend = f"invalid ({exc})"
    print(f"render backend   {backend}"
          + ("  — scenes render inside the container" if backend == "docker" else ""))

    latex = shutil.which("latex") or shutil.which("pdflatex")
    print(f"latex            {latex or 'MISSING — equations will not render'}")

    print(f"claude CLI       {shutil.which('claude') or 'not installed'}")
    print(f"LLM backend      {llm.describe_backend()}")

    key = os.getenv("ELEVENLABS_API_KEY")
    print(f"ElevenLabs key   {'set' if key else 'MISSING — narration will fail'}")
    heygen = os.getenv("HEYGEN_API_KEY")
    print(f"HeyGen key       {'set' if heygen else 'not set (manual drop mode)'}")

    docker = shutil.which("docker")
    print(f"docker           {docker or 'not installed'}")

    print("=" * 78)
    print("OK" if ok else "Some required tools are missing — see above.")
    return 0 if ok else 1


def cmd_dashboard(args) -> int:
    from src.dashboard import serve
    serve(host=args.host, port=args.port, projects_dir=args.projects_dir,
          open_browser=not args.no_browser)
    return 0


def cmd_sfx(args) -> int:
    from src import sfx
    root = Path(__file__).resolve().parent
    built = sfx.ensure_library(root, force=args.force)
    print(f"✅ {len(built)} sound effects in {sfx.sfx_dir(root)}")
    for path in sorted(built):
        print(f"   {path.stem}")
    return 0


# --------------------------------------------------------------------------- #
# CLI                                                                          #
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="video", description="AI educational video pipeline.")
    ap.add_argument("--projects-dir", default=DEFAULT_PROJECTS_DIR,
                    help="Where project folders live (default: projects/)")
    sub = ap.add_subparsers(dest="command", required=True)

    def add_render_flags(p):
        p.add_argument("--orientation", choices=["landscape", "portrait"])
        p.add_argument("--theme")
        p.add_argument("--chroma")
        p.add_argument("--voice")

    # new -------------------------------------------------------------------
    p = sub.add_parser("new", help="Create a project and draft its script")
    p.add_argument("topic")
    p.add_argument("--slug")
    p.add_argument("--language", default="hinglish",
                   choices=["hinglish", "english"])
    p.add_argument("--theme", default="midnight")
    p.add_argument("--chroma", default="none")
    p.add_argument("--voice", default="George")
    p.add_argument("--orientation", default="landscape",
                   choices=["landscape", "portrait"])
    p.add_argument("--answer-image")
    p.add_argument("--notes", default="", help="Extra instructions for the writer")
    p.add_argument("--no-script", action="store_true",
                   help="Just create the folder; write the script yourself")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_new)

    # script ----------------------------------------------------------------
    p = sub.add_parser("script", help="(Re)generate the script for a project")
    p.add_argument("project")
    p.add_argument("--topic")
    p.add_argument("--language", choices=["hinglish", "english"])
    p.add_argument("--answer-image")
    p.add_argument("--notes", default="")
    p.add_argument("--force", action="store_true", help="Overwrite an existing script")
    p.add_argument("--provider", choices=["auto", "openai", "claude"],
                   help="Which model writes the script (default: $SCRIPT_LLM)")
    p.add_argument("--judge", action="store_true",
                   help="Also have a model compare the draft to your samples")
    p.add_argument("--max-attempts", type=int, default=3,
                   help="Rewrite passes to fix how it sounds")
    add_render_flags(p)
    p.set_defaults(func=cmd_script)

    # eval / style ----------------------------------------------------------
    p = sub.add_parser("eval", help="Score a script for how spoken it sounds")
    p.add_argument("project")
    p.add_argument("--judge", action="store_true",
                   help="Add a model's read against your sample scripts")
    p.add_argument("--provider", choices=["auto", "openai", "claude"])
    p.set_defaults(func=cmd_eval)

    p = sub.add_parser("style", help="Show or set up the voice reference")
    p.add_argument("--init", action="store_true",
                   help="Create style/ with a template to fill in")
    p.set_defaults(func=cmd_style)

    p = sub.add_parser("spend", help="What the paid API keys have cost")
    p.add_argument("--days", type=int, help="Only the last N days")
    p.add_argument("--project", help="Only this video")
    p.add_argument("--detail", type=int, nargs="?", const=20, default=0,
                   help="Also list the last N individual calls")
    p.set_defaults(func=cmd_spend)

    # narrate ---------------------------------------------------------------
    p = sub.add_parser("narrate", help="Synthesize narration and fix timing")
    p.add_argument("project")
    p.add_argument("--no-audio", action="store_true",
                   help="Skip TTS; estimate timing (free render validation)")
    add_render_flags(p)
    p.set_defaults(func=cmd_narrate)

    # background ------------------------------------------------------------
    p = sub.add_parser("background", help="Animate, render and assemble")
    p.add_argument("project")
    p.add_argument("--scenes-dir", help="Render pre-written scenes instead of "
                                        "calling Claude")
    p.add_argument("--max-attempts", type=int, default=4)
    p.add_argument("--continue-on-error", action="store_true")
    p.add_argument("--no-sfx", action="store_true", help="Skip sound effects")
    p.add_argument("--answer-title", default="Answer")
    add_render_flags(p)
    p.set_defaults(func=cmd_background)

    # avatar ----------------------------------------------------------------
    p = sub.add_parser("avatar", help="Briefs, or fetch/ingest presenter clips")
    p.add_argument("project")
    p.add_argument("--briefs", action="store_true",
                   help="Write the per-segment briefs and stop")
    p.add_argument("--provider", default="auto",
                   choices=["auto", "manual", "heygen"])
    p.set_defaults(func=cmd_avatar)

    # composite -------------------------------------------------------------
    p = sub.add_parser("composite", help="Key the presenter over the animation")
    p.add_argument("project")
    p.add_argument("--feather", type=float, default=1.0,
                   help="Matte edge softening (0 disables)")
    p.set_defaults(func=cmd_composite)

    # qc --------------------------------------------------------------------
    p = sub.add_parser("qc", help="Claude reviews the rendered frames")
    p.add_argument("project")
    p.add_argument("--effort", default="medium",
                   choices=["low", "medium", "high"])
    p.set_defaults(func=cmd_qc)

    # endscreenshot ---------------------------------------------------------
    p = sub.add_parser("endscreenshot",
                       help="Hand-write the closing Q&A card (temp -> photo)")
    p.add_argument("project", nargs="?",
                   help="Write into this project's assets/ (omit for --out)")
    p.add_argument("--question"), p.add_argument("--question-file")
    p.add_argument("--answer"), p.add_argument("--answer-file")
    p.add_argument("--sheet", default=str(_es_default("sheet")),
                   help="The blank ruled page (step 1's input)")
    p.add_argument("--style", default=str(_es_default("style")),
                   help="A page in the handwriting to copy")
    p.add_argument("--label", default="Q1", help="Question label (default Q1)")
    p.add_argument("--heading", help="Optional title line above the question")
    p.add_argument("--stem", help="Output filename stem (default 'answer')")
    p.add_argument("--diagram", help="Figure to draw on the page "
                                     "(see tools/answer_figure.py)")
    p.add_argument("--diagram-width", type=float, default=0.44,
                   help="figure width as a fraction of the page")
    p.add_argument("--diagram-row", type=int, default=2,
                   help="first ruled row the figure sits on")
    p.add_argument("--diagram-side", default="right",
                   choices=["left", "right"])
    p.add_argument("--diagram-below", action="store_true",
                   help="place the figure under the answer instead of beside it")
    p.add_argument("--watermark",
                   default=str(Path(__file__).resolve().parent / "EndScreenshot"
                               / "assets" / "watermark.png"))
    p.add_argument("--no-watermark", action="store_true")
    p.add_argument("--wm-scale", type=float, default=0.68)
    p.add_argument("--wm-opacity", type=float, default=3.0)
    p.add_argument("--out", help="Output dir when no project is given")
    p.add_argument("--temp-dir", help="Where temps are cached")
    p.add_argument("--quality", choices=["low", "medium", "high"],
                   help="Overrides OPENAI_HANDWRITE_QUALITY")
    p.add_argument("--max-pages", type=int, default=8)
    p.add_argument("--highlight", action="store_true",
                   help="Allow highlighter swipes on headings")
    p.add_argument("--margin-line", action="store_true",
                   help="The sheet HAS a vertical margin rule (default "
                        "assumes it does not)")
    p.add_argument("--notes", default="", help="Extra job-specific overrides")
    p.add_argument("--approve", action="store_true",
                   help="draw the page for real (without this you get the free temp)")
    p.add_argument("--fresh-temp", action="store_true",
                   help="Re-mint the base sheet instead of reusing the cache")
    p.add_argument("--dry-run", action="store_true",
                   help="Show the tagged lines and page split; no API calls")
    p.set_defaults(func=cmd_endscreenshot)

    # build -----------------------------------------------------------------
    p = sub.add_parser("build", help="Run every stage in order")
    p.add_argument("project")
    p.add_argument("--no-audio", action="store_true")
    p.add_argument("--scenes-dir")
    p.add_argument("--max-attempts", type=int, default=4)
    p.add_argument("--continue-on-error", action="store_true")
    p.add_argument("--no-sfx", action="store_true")
    p.add_argument("--answer-title", default="Answer")
    p.add_argument("--skip-qc", action="store_true")
    p.add_argument("--strict-qc", action="store_true",
                   help="Stop the build if QC fails")
    p.add_argument("--feather", type=float, default=1.0)
    p.add_argument("--effort", default="medium",
                   choices=["low", "medium", "high"])
    add_render_flags(p)
    p.set_defaults(func=cmd_build)

    # status / doctor / dashboard / sfx -------------------------------------
    p = sub.add_parser("status", help="Show pipeline state")
    p.add_argument("project", nargs="?")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("doctor", help="Check this machine's setup")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("dashboard", help="Open the browser UI")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--no-browser", action="store_true")
    p.set_defaults(func=cmd_dashboard)

    p = sub.add_parser("sfx", help="(Re)build the sound-effect library")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_sfx)

    return ap


def main() -> int:
    args = build_parser().parse_args()
    # Tag every paid call with the stage and video that caused it, so `spend`
    # can answer "what did this video cost" rather than just a running total.
    try:
        from src import usage
        usage.set_context(stage=getattr(args, "command", "") or "",
                          project=getattr(args, "project", "") or "")
    except Exception:  # noqa: BLE001 - accounting must never block a run
        pass
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return 130
    except SystemExit:
        raise
    except FileNotFoundError as exc:
        print(f"❌ {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
