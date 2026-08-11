"""Laying the keyed presenter over the animation.

This is the step an editor used to do by hand: pull the green out of the HeyGen
clip, clean up the fringe it leaves behind, size the presenter, and place them
in the gap the animation left free.

The placement is not guesswork. A script that reserves space for a presenter
does it with a chroma zone, and Manim paints that region flat green while
keeping all content out of it — so the keyed-out region of the background *is*
the presenter's box. ``avatar.placement: auto`` reads it straight off the
script; anything else overrides it.

The keying chain, per segment:

    format=yuva420p   give the frame an alpha channel to write into
    chromakey         punch the green out (YUV — cleaner than colorkey on RGB)
    despill           drain the green that bounced onto hair and shoulders
    alphaextract/blur/alphamerge    feather the matte so edges aren't crunchy
    scale + overlay   fit the presenter into the box, standing on its bottom edge

Everything is one ffmpeg invocation per segment, so there's no intermediate
re-encode and no generation loss.
"""
from __future__ import annotations

from pathlib import Path

from src import media
from src.config import AvatarConfig
from src.script_models import DialogueSegment, VideoScript


def _normalize_hex(color: str) -> str:
    c = color.strip().lstrip("#")
    if len(c) == 3:  # #0f0 -> 00ff00
        c = "".join(ch * 2 for ch in c)
    return c.upper()


def _hex_to_ffmpeg(color: str) -> str:
    """'#00FF00' -> '0x00FF00' (ffmpeg's colour literal)."""
    return f"0x{_normalize_hex(color)}"


def _despill_type(color: str) -> str:
    """Which channel to drain — whichever the key colour is made of."""
    c = _normalize_hex(color)
    try:
        green, blue = int(c[2:4], 16), int(c[4:6], 16)
    except (ValueError, IndexError):
        return "green"
    return "blue" if blue > green else "green"


def build_filter(cfg: AvatarConfig, box: tuple[float, float, float, float],
                 width: int, height: int, duration: float,
                 *, feather: float = 1.0) -> str:
    """The filter_complex that keys the avatar and places it in ``box``."""
    bx, by, bw, bh = box
    px, py = bx * width, by * height
    pw, ph = bw * width * cfg.scale, bh * height * cfg.scale
    ox, oy = cfg.offset[0] * width, cfg.offset[1] * height

    key = _hex_to_ffmpeg(cfg.key_color)
    despill_type = _despill_type(cfg.key_color)

    chain = (
        f"[1:v]format=yuva420p,"
        f"chromakey={key}:{cfg.similarity:.3f}:{cfg.blend:.3f},"
        f"despill=type={despill_type}:mix={cfg.despill:.2f}:expand=0"
    )

    if feather > 0:
        # Soften the matte only — blurring the colour would smear the presenter.
        chain += ",split[k1][k2];[k2]alphaextract,boxblur=" \
                 f"{feather:.1f}:1[am];[k1][am]alphamerge"

    chain += (
        f",scale={pw:.0f}:{ph:.0f}:force_original_aspect_ratio=decrease,"
        f"setsar=1,tpad=stop_mode=clone:stop_duration={duration:.3f}[fg];"
    )

    # Centre the presenter in the box horizontally and stand them on its floor.
    x_expr = f"{px:.0f}+({pw:.0f}-w)/2+({ox:.0f})"
    y_expr = f"{py:.0f}+{ph:.0f}-h+({oy:.0f})"
    chain += f"[0:v][fg]overlay=x={x_expr}:y={y_expr}:eval=init:format=auto[out]"
    return chain


def composite_clip(background: str, avatar: str, out_path: str, *,
                   cfg: AvatarConfig, box, width: int, height: int,
                   fps: int, duration: float, feather: float = 1.0) -> str:
    """Key one avatar clip over one background clip."""
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    media._run([
        "ffmpeg", "-y",
        "-i", background,
        "-i", avatar,
        "-filter_complex", build_filter(cfg, box, width, height, duration,
                                        feather=feather),
        "-map", "[out]",
        "-t", f"{duration:.3f}", "-r", str(fps), "-fps_mode", "cfr",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-video_track_timescale", "90000",
        "-an", out_path,
    ])
    return out_path


def composite_segments(script: VideoScript,
                       segments: list[DialogueSegment],
                       work_dir: str, out_path: str,
                       *, feather: float = 1.0) -> str:
    """Composite every segment that has an avatar clip, then concatenate.

    Segments without a clip pass through untouched, so a half-finished avatar
    folder still produces a watchable cut of the whole video.
    """
    settings = script.render_settings
    width, height = settings.orientation.resolution
    box = script.avatar_box
    cfg = script.avatar

    work = Path(work_dir)
    work.mkdir(parents=True, exist_ok=True)

    pieces: list[str] = []
    keyed = 0
    for seg in segments:
        base = work / f"conformed_{seg.index:03d}.mp4"
        if not base.exists():
            raise FileNotFoundError(
                f"Missing conformed clip for segment {seg.index}: {base}\n"
                f"Run the background stage first."
            )
        duration = seg.target_duration or media.probe_duration(str(base))
        if not seg.avatar_path:
            pieces.append(str(base))
            continue
        out_clip = work / f"composited_{seg.index:03d}.mp4"
        composite_clip(str(base), seg.avatar_path, str(out_clip),
                       cfg=cfg, box=box, width=width, height=height,
                       fps=settings.fps, duration=duration, feather=feather)
        pieces.append(str(out_clip))
        keyed += 1
        print(f"   keyed avatar onto segment {seg.index}")

    if not pieces:
        raise RuntimeError("Nothing to composite.")
    print(f"   composited {keyed}/{len(pieces)} segment(s) with a presenter")
    media.concat_videos(pieces, out_path)
    return out_path


def composite_video(script: VideoScript, segments: list[DialogueSegment],
                    work_dir: str, final_path: str,
                    *, audio_path: str | None = None,
                    feather: float = 1.0) -> str:
    """Full composite pass: key, concatenate, and re-attach the narration."""
    work = Path(work_dir)
    video_track = str(work / "composited_track.mp4")
    composite_segments(script, segments, work_dir, video_track, feather=feather)

    Path(final_path).parent.mkdir(parents=True, exist_ok=True)
    if audio_path is None:
        # Prefer the sound-effect mix laid down during assembly.
        for candidate in ("audio_track_sfx.mp3", "audio_track.mp3"):
            if (work / candidate).exists():
                audio_path = str(work / candidate)
                break

    if audio_path and Path(audio_path).exists():
        media.mux(video_track, audio_path, final_path)
    else:
        import shutil
        shutil.copy(video_track, final_path)

    has_v, has_a = media.has_streams(final_path)
    if not has_v:
        raise RuntimeError("Composited video has no video stream.")
    if audio_path and not has_a:
        raise RuntimeError("Composited video lost its audio track.")
    return final_path
