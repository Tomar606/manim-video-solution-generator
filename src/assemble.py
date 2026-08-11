"""Assemble per-segment renders + narration + sound effects into one video.

Each rendered segment is conformed to its audio clip's exact length, all
segments are concatenated, the narration track is concatenated in the same
order, the sound cues the scenes emitted are mixed onto that track, and the two
are muxed. Because every segment is conformed and normalised to identical
codec/fps/resolution, cuts are seamless and A/V stays in lockstep.

Conforming is also what makes the cue timings correct: a segment's cues are
relative to its own scene, and its start in the final timeline is just the sum
of the target durations before it.
"""
from __future__ import annotations

from pathlib import Path

from src import media, sfx
from src.scene_codegen import cues_file_for
from src.script_models import DialogueSegment, VideoScript


def collect_cues(rendered: list[tuple[DialogueSegment, str]],
                 durations: list[float]) -> list[sfx.Cue]:
    """Read each scene's sidecar cue file and shift it onto the final timeline."""
    cues: list[sfx.Cue] = []
    start = 0.0
    for (seg, _), duration in zip(rendered, durations):
        if seg.manim_path:
            found = sfx.read_cue_file(cues_file_for(seg.manim_path), offset=start)
            # A scene can overrun its conformed length; drop cues past the cut
            # so a trimmed animation doesn't leave a sound stranded.
            cues.extend(c for c in found if c.time < start + duration)
        start += duration
    return cues


def assemble(
    script: VideoScript,
    rendered: list[tuple[DialogueSegment, str]],  # (segment, raw video path)
    work_dir: str,
    final_path: str,
    *,
    asset_root: str | Path | None = None,
    sound_effects: bool = True,
) -> str:
    settings = script.render_settings
    fps = settings.fps
    width, height = settings.orientation.resolution

    work = Path(work_dir)
    work.mkdir(parents=True, exist_ok=True)

    conformed: list[str] = []
    audios: list[str] = []
    durations: list[float] = []
    for seg, raw_video in rendered:
        target = seg.target_duration or media.probe_duration(raw_video)
        clip = str(work / f"conformed_{seg.index:03d}.mp4")
        media.conform_video(raw_video, clip, target, fps, width, height)
        conformed.append(clip)
        durations.append(target)
        if seg.audio_path:
            audios.append(seg.audio_path)
        print(f"   conformed seg {seg.index} -> {target:.2f}s")

    if not conformed:
        raise RuntimeError("Nothing to assemble — no segments rendered.")

    full_video = str(work / "video_track.mp4")
    media.concat_videos(conformed, full_video)

    Path(final_path).parent.mkdir(parents=True, exist_ok=True)
    total = sum(durations)

    if not audios:
        # --no-audio path: ship the silent concatenated video.
        import shutil
        shutil.copy(full_video, final_path)
        if not media.has_streams(final_path)[0]:
            raise RuntimeError("Final (silent) video has no video stream.")
        return final_path

    full_audio = str(work / "audio_track.mp3")
    media.concat_audio(audios, full_audio)

    if sound_effects:
        root = asset_root or Path(__file__).resolve().parents[1]
        cues = collect_cues(rendered, durations)
        if cues:
            sfx.ensure_library(root)
            mixed = str(work / "audio_track_sfx.mp3")
            full_audio = sfx.mix(full_audio, cues, mixed,
                                 asset_root=root, duration=total)

    media.mux(full_video, full_audio, final_path)

    has_v, has_a = media.has_streams(final_path)
    if not (has_v and has_a):
        raise RuntimeError(
            f"Final video is missing a stream (video={has_v}, audio={has_a})."
        )
    return final_path
