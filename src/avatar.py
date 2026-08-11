"""Getting the presenter clips that go on top of the animation.

Today the avatars come out of the HeyGen web UI and an editor drops the files
into ``projects/<slug>/avatar/``. That's the manual path, and it's a first-class
one: the pipeline writes a *brief* per segment saying exactly what to generate
(the line to speak, how long it should run, and the narration audio to upload),
then ingests whatever comes back and checks it before compositing.

The API path is the same shape with the download automated. :class:`HeyGenProvider`
implements it but stays inactive until ``HEYGEN_API_KEY`` is set, so switching
over is a credential change rather than a rewrite.

Timing works one of two ways, set by ``avatar.timing`` in the script:

``audio``   ElevenLabs narration is the clock. Each segment's length comes from
            its synthesized line, and the avatar is generated *from that audio*
            so the mouth matches exactly. This is the default and it keeps the
            voice identical across every video.
``avatar``  The dropped clips are the clock. Segment lengths are measured from
            the clips instead, for when HeyGen generates the speech itself.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path

from src import media
from src.script_models import DialogueSegment, VideoScript

VIDEO_SUFFIXES = (".mp4", ".mov", ".webm", ".mkv")

# segment_003.mp4 / segment-3.mov / 003.mp4 all resolve to segment index 3.
_CLIP_RE = re.compile(r"^(?:segment[_-]?)?(\d+)$", re.IGNORECASE)

# A clip this far off its narration length probably belongs to another segment.
DURATION_TOLERANCE = 1.5


@dataclass
class AvatarBrief:
    """What to generate for one segment."""

    index: int
    speaker: str
    text: str
    target_duration: float
    audio_path: str | None = None
    filename: str = ""

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "speaker": self.speaker,
            "text": self.text,
            "target_duration": round(self.target_duration, 2),
            "narration_audio": self.audio_path,
            "save_clip_as": self.filename,
        }


@dataclass
class IngestReport:
    """What the avatar folder actually contained."""

    matched: dict[int, str] = field(default_factory=dict)
    missing: list[int] = field(default_factory=list)
    unmatched_files: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing

    def describe(self) -> str:
        lines = [f"avatar clips: {len(self.matched)} matched"]
        if self.missing:
            lines.append(f"  missing for segments: {self.missing}")
        for name in self.unmatched_files:
            lines.append(f"  ignored (unrecognised name): {name}")
        lines += [f"  ⚠️  {w}" for w in self.warnings]
        return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Briefs — what the editor (or the API) has to produce                         #
# --------------------------------------------------------------------------- #
def build_briefs(script: VideoScript) -> list[AvatarBrief]:
    briefs: list[AvatarBrief] = []
    for seg in script.segments:
        if not seg.narration.strip():
            continue  # silent beat (e.g. a bare answer card) — no presenter
        briefs.append(AvatarBrief(
            index=seg.index,
            speaker=seg.speaker,
            text=seg.narration,
            target_duration=float(seg.target_duration or 0.0),
            audio_path=seg.audio_path,
            filename=f"segment_{seg.index:03d}.mp4",
        ))
    return briefs


def write_briefs(script: VideoScript, briefs_dir: str | Path) -> Path:
    """Write the per-segment briefs an editor works from. Returns the manifest."""
    out = Path(briefs_dir)
    out.mkdir(parents=True, exist_ok=True)
    briefs = build_briefs(script)

    manifest = {
        "title": script.title,
        "orientation": script.orientation.value,
        "timing": script.avatar.timing,
        "key_color": script.avatar.key_color,
        "drop_clips_into": str(Path(briefs_dir).parent.resolve()),
        "instructions": (
            "Generate one clip per segment against a plain green screen "
            f"({script.avatar.key_color}). For an exact lip-sync, upload the "
            "narration_audio file as the avatar's voice track rather than "
            "retyping the line. Save each clip under the 'save_clip_as' name "
            "in the folder above."
        ),
        "segments": [b.to_dict() for b in briefs],
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # A plain-text brief per segment, for copy-pasting into the HeyGen UI.
    for brief in briefs:
        body = (
            f"Segment {brief.index:03d}  [{brief.speaker}]\n"
            f"Target length: {brief.target_duration:.2f}s\n"
            f"Save as: {brief.filename}\n"
            f"{'Narration audio: ' + brief.audio_path if brief.audio_path else ''}\n"
            f"\n--- line to speak ---\n{brief.text}\n"
        )
        (out / f"segment_{brief.index:03d}.txt").write_text(body, encoding="utf-8")

    return out / "manifest.json"


# --------------------------------------------------------------------------- #
# Ingest — pick up whatever landed in the folder                               #
# --------------------------------------------------------------------------- #
def _index_from_name(path: Path) -> int | None:
    m = _CLIP_RE.match(path.stem)
    return int(m.group(1)) if m else None


def ingest(script: VideoScript, avatar_dir: str | Path, *,
           strict: bool = False) -> IngestReport:
    """Attach dropped clips to their segments and sanity-check them."""
    directory = Path(avatar_dir)
    report = IngestReport()
    if not directory.is_dir():
        report.missing = [s.index for s in script.segments if s.narration.strip()]
        return report

    by_index: dict[int, Path] = {}
    for path in sorted(directory.iterdir()):
        if path.is_dir() or path.suffix.lower() not in VIDEO_SUFFIXES:
            continue
        idx = _index_from_name(path)
        if idx is None:
            report.unmatched_files.append(path.name)
            continue
        if idx in by_index:
            report.warnings.append(
                f"segment {idx}: both {by_index[idx].name} and {path.name} match; "
                f"using {by_index[idx].name}"
            )
            continue
        by_index[idx] = path

    for seg in script.segments:
        path = by_index.get(seg.index)
        if path is None:
            if seg.narration.strip():
                report.missing.append(seg.index)
            continue
        seg.avatar_path = str(path.resolve())
        report.matched[seg.index] = seg.avatar_path

        clip_len = media.probe_duration(str(path))
        if clip_len <= 0:
            report.warnings.append(f"segment {seg.index}: {path.name} is unreadable")
        elif seg.target_duration:
            drift = clip_len - seg.target_duration
            if abs(drift) > DURATION_TOLERANCE:
                report.warnings.append(
                    f"segment {seg.index}: clip is {clip_len:.1f}s but the "
                    f"narration is {seg.target_duration:.1f}s "
                    f"({drift:+.1f}s) — check you saved the right file"
                )

    if strict and not report.ok:
        raise FileNotFoundError(
            f"Missing avatar clips for segments {report.missing}. "
            f"Drop them into {directory.resolve()}"
        )
    return report


def apply_avatar_timing(script: VideoScript) -> None:
    """Let the dropped clips set segment lengths (``avatar.timing: avatar``)."""
    for seg in script.segments:
        if not seg.avatar_path:
            continue
        clip_len = media.probe_duration(seg.avatar_path)
        if clip_len > 0:
            seg.target_duration = round(clip_len, 3)


# --------------------------------------------------------------------------- #
# Providers                                                                    #
# --------------------------------------------------------------------------- #
class AvatarProvider:
    """Common shape: fill ``avatar_dir`` with ``segment_NNN.mp4`` files."""

    name = "base"

    def available(self) -> bool:
        raise NotImplementedError

    def fetch(self, script: VideoScript, avatar_dir: str | Path) -> IngestReport:
        raise NotImplementedError


class ManualDropProvider(AvatarProvider):
    """The current workflow: a human puts the files there."""

    name = "manual"

    def available(self) -> bool:
        return True

    def fetch(self, script: VideoScript, avatar_dir: str | Path) -> IngestReport:
        return ingest(script, avatar_dir)


class HeyGenProvider(AvatarProvider):
    """HeyGen API client — written, but inactive until a key exists.

    Endpoint paths and payload keys are read from the environment so they can be
    corrected against the live API without touching this file:

        HEYGEN_API_KEY      required; enables this provider
        HEYGEN_AVATAR_ID    which avatar to drive
        HEYGEN_API_BASE     default https://api.heygen.com
        HEYGEN_VOICE_ID     only used when HeyGen generates the speech itself

    Unverified against the live service — we don't have a key yet. It fails
    loudly with the raw response rather than guessing, so the first real run
    tells us exactly what to adjust.
    """

    name = "heygen"

    def __init__(self) -> None:
        self.api_key = os.getenv("HEYGEN_API_KEY", "")
        self.avatar_id = os.getenv("HEYGEN_AVATAR_ID", "")
        self.voice_id = os.getenv("HEYGEN_VOICE_ID", "")
        self.base = os.getenv("HEYGEN_API_BASE", "https://api.heygen.com").rstrip("/")

    def available(self) -> bool:
        return bool(self.api_key and self.avatar_id)

    # -- HTTP ----------------------------------------------------------- #
    def _post(self, path: str, payload: dict) -> dict:
        import urllib.error
        import urllib.request

        req = urllib.request.Request(
            f"{self.base}{path}",
            data=json.dumps(payload).encode(),
            headers={"X-Api-Key": self.api_key,
                     "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            raise RuntimeError(
                f"HeyGen {path} failed ({exc.code}): {exc.read().decode()[:500]}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Could not reach HeyGen: {exc}") from exc

    def _get(self, path: str) -> dict:
        import urllib.error
        import urllib.request

        req = urllib.request.Request(
            f"{self.base}{path}", headers={"X-Api-Key": self.api_key}
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            raise RuntimeError(
                f"HeyGen {path} failed ({exc.code}): {exc.read().decode()[:500]}"
            ) from exc

    # -- generation ------------------------------------------------------ #
    def _payload(self, seg: DialogueSegment, script: VideoScript) -> dict:
        w, h = script.orientation.resolution
        voice: dict = {"type": "text", "input_text": seg.narration}
        if self.voice_id:
            voice["voice_id"] = self.voice_id
        return {
            "video_inputs": [{
                "character": {"type": "avatar", "avatar_id": self.avatar_id,
                              "avatar_style": "normal"},
                "voice": voice,
                # Flat green so the compositor can key it the same way it keys
                # the zone Manim leaves empty.
                "background": {"type": "color",
                               "value": script.avatar.key_color},
            }],
            "dimension": {"width": w, "height": h},
        }

    def fetch(self, script: VideoScript, avatar_dir: str | Path,
              *, poll_seconds: int = 10, timeout: int = 900) -> IngestReport:
        if not self.available():
            raise RuntimeError(
                "HeyGen is not configured. Set HEYGEN_API_KEY and "
                "HEYGEN_AVATAR_ID, or use the manual drop workflow."
            )
        out = Path(avatar_dir)
        out.mkdir(parents=True, exist_ok=True)

        pending: dict[int, str] = {}
        for seg in script.segments:
            if not seg.narration.strip():
                continue
            dest = out / f"segment_{seg.index:03d}.mp4"
            if dest.exists():
                continue  # already have it; don't pay to regenerate
            resp = self._post("/v2/video/generate", self._payload(seg, script))
            video_id = (resp.get("data") or {}).get("video_id")
            if not video_id:
                raise RuntimeError(f"HeyGen returned no video_id: {resp}")
            pending[seg.index] = video_id
            print(f"   seg {seg.index}: HeyGen job {video_id}")

        deadline = time.time() + timeout
        while pending and time.time() < deadline:
            time.sleep(poll_seconds)
            for index, video_id in list(pending.items()):
                status = self._get(f"/v1/video_status.get?video_id={video_id}")
                data = status.get("data") or {}
                state = data.get("status")
                if state == "completed":
                    url = data.get("video_url")
                    if not url:
                        raise RuntimeError(f"HeyGen job {video_id} has no URL")
                    self._download(url, out / f"segment_{index:03d}.mp4")
                    print(f"   seg {index}: downloaded")
                    pending.pop(index)
                elif state == "failed":
                    raise RuntimeError(
                        f"HeyGen job {video_id} failed: {data.get('error')}"
                    )
        if pending:
            raise TimeoutError(
                f"HeyGen jobs still running after {timeout}s: {list(pending)}"
            )
        return ingest(script, out)

    @staticmethod
    def _download(url: str, dest: Path) -> None:
        import urllib.request
        with urllib.request.urlopen(url, timeout=300) as resp, \
                open(dest, "wb") as fh:
            shutil.copyfileobj(resp, fh)


def get_provider(name: str = "auto") -> AvatarProvider:
    """``auto`` uses HeyGen when it's configured, otherwise the manual folder."""
    name = (name or "auto").strip().lower()
    if name in ("heygen", "api"):
        return HeyGenProvider()
    if name in ("manual", "drop"):
        return ManualDropProvider()
    heygen = HeyGenProvider()
    return heygen if heygen.available() else ManualDropProvider()
