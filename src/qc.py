"""Automated review of the rendered clips, before anyone opens an editor.

The manual version of this step is someone scrubbing every clip looking for
equations running off the frame, mis-set LaTeX, typos in captions, or a graphic
that never appeared. That review is mechanical and it's the step most likely to
be skipped under deadline — so it's the one worth automating.

For each segment we pull a few frames, hand them to Claude along with what that
beat was *supposed* to show (its narration, equations, images and safe area),
and ask for specific defects. The result is a pass/warn/fail report written to
``qc/report.md`` and ``qc/report.json``, with the offending frames saved beside
it so a human can confirm a finding in one click.

QC never edits anything. It reports, and the human decides.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import BaseModel, Field

from src import media
from src.llm import LLMError, complete_json
from src.script_models import DialogueSegment, VideoScript

FRAMES_PER_SEGMENT = 3

SYSTEM_PROMPT = """You are a meticulous video QC reviewer for an educational \
animation studio. You are shown frames from ONE beat of a maths/physics video \
and told what that beat was supposed to contain.

Report only defects a viewer would notice or that would embarrass us:
- text or equations cut off, overflowing the frame, or overlapping each other
- LaTeX that failed to typeset (stray backslashes, raw commands, empty boxes)
- misspellings in on-screen text
- an equation that does not match what the beat is supposed to show
- content that has drifted into the reserved presenter area
- a frame that is blank or shows only the background when it should show content
- unreadable contrast (text nearly the same colour as the background)

Do NOT report: stylistic preferences, pacing, the absence of a presenter (they \
are composited later), empty space that is clearly the reserved presenter zone, \
or anything you are guessing at. If the frames look fine, say so — a clean pass \
is a useful result, and false alarms cost more than they save."""


class Finding(BaseModel):
    severity: str = Field(description="one of: fail, warn")
    issue: str = Field(description="one sentence naming the specific defect")
    where: str = Field(default="", description="where in the frame it appears")


class SegmentReview(BaseModel):
    verdict: str = Field(description="one of: pass, warn, fail")
    summary: str = Field(description="one sentence overall assessment")
    findings: list[Finding] = Field(default_factory=list)


@dataclass
class SegmentResult:
    index: int
    verdict: str
    summary: str
    findings: list[dict] = field(default_factory=list)
    frames: list[str] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "segment": self.index,
            "verdict": self.verdict,
            "summary": self.summary,
            "findings": self.findings,
            "frames": self.frames,
            "error": self.error,
        }


def extract_frames(video_path: str, out_dir: str | Path, index: int,
                   count: int = FRAMES_PER_SEGMENT) -> list[str]:
    """Grab evenly spaced frames, skipping the fade at either end."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    duration = media.probe_duration(video_path)
    if duration <= 0:
        return []

    # Sample inside the clip: the first and last moments are usually mid-fade.
    span_start, span_end = duration * 0.15, duration * 0.9
    if count == 1:
        stamps = [(span_start + span_end) / 2]
    else:
        step = (span_end - span_start) / (count - 1)
        stamps = [span_start + step * i for i in range(count)]

    paths: list[str] = []
    for i, at in enumerate(stamps):
        dest = out / f"segment_{index:03d}_{i}.png"
        try:
            media._run([
                "ffmpeg", "-y", "-ss", f"{max(at, 0):.3f}", "-i", video_path,
                "-frames:v", "1", "-q:v", "2", str(dest),
            ])
            if dest.exists() and dest.stat().st_size > 0:
                paths.append(str(dest))
        except media.MediaError:
            continue
    return paths


def _expectations(script: VideoScript, seg: DialogueSegment) -> str:
    safe = script.chroma.safe_rect()
    lines = [
        f'Video: "{script.title}"',
        f"Beat {seg.index} of {len(script.segments)} — orientation "
        f"{script.orientation.value} "
        f"({script.orientation.resolution[0]}x{script.orientation.resolution[1]}).",
        f"Spoken over this beat: \"{seg.narration}\"" if seg.narration
        else "This beat is silent (no narration).",
    ]
    if seg.equations:
        lines.append("Equations that should be visible (LaTeX):")
        lines += [f"  - {e}" for e in seg.equations]
    else:
        lines.append("No equation is expected on this beat.")
    if seg.images:
        lines.append("Photographs that should be visible:")
        lines += [f"  - {img.caption or Path(img.path).name}" for img in seg.images]
    if script.chroma.enabled:
        lines.append(
            f"A flat {script.chroma.color} area is reserved for the presenter and "
            f"is composited over later — it SHOULD look empty. All content must "
            f"stay inside the safe area {tuple(round(v, 2) for v in safe)} "
            f"(normalized x,y,w,h from the top-left)."
        )
    if seg.is_outro:
        lines.append("This is the final answer card — the answer must be legible.")
    return "\n".join(lines)


def review_segment(script: VideoScript, seg: DialogueSegment, video_path: str,
                   frames_dir: str | Path, *, effort: str = "medium") -> SegmentResult:
    frames = extract_frames(video_path, frames_dir, seg.index)
    if not frames:
        return SegmentResult(index=seg.index, verdict="fail",
                             summary="Could not read any frame from this clip.",
                             error="frame extraction failed")

    prompt = (
        f"{_expectations(script, seg)}\n\n"
        f"{len(frames)} frame(s) sampled across the beat, in order, are attached.\n"
        f"Review them and report defects."
    )
    try:
        review = complete_json(SYSTEM_PROMPT, prompt, SegmentReview,
                               effort=effort, images=frames)
    except LLMError as exc:
        return SegmentResult(index=seg.index, verdict="error",
                             summary="Review call failed.", frames=frames,
                             error=str(exc))

    verdict = review.verdict.strip().lower()
    if verdict not in ("pass", "warn", "fail"):
        verdict = "warn"
    return SegmentResult(
        index=seg.index,
        verdict=verdict,
        summary=review.summary.strip(),
        findings=[f.model_dump() for f in review.findings],
        frames=frames,
    )


def review(script: VideoScript, rendered: list[tuple[DialogueSegment, str]],
           qc_dir: str | Path, *, effort: str = "medium") -> dict:
    """Review every rendered segment. Returns the report dict (also written)."""
    out = Path(qc_dir)
    frames_dir = out / "frames"
    out.mkdir(parents=True, exist_ok=True)

    results: list[SegmentResult] = []
    for seg, video_path in rendered:
        print(f"   reviewing segment {seg.index}...", flush=True)
        result = review_segment(script, seg, video_path, frames_dir, effort=effort)
        mark = {"pass": "✓", "warn": "!", "fail": "✗"}.get(result.verdict, "?")
        print(f"     {mark} {result.summary}")
        for finding in result.findings:
            print(f"       - [{finding.get('severity')}] {finding.get('issue')}")
        results.append(result)

    counts = {v: sum(1 for r in results if r.verdict == v)
              for v in ("pass", "warn", "fail", "error")}
    report = {
        "title": script.title,
        "segments_reviewed": len(results),
        "counts": counts,
        "verdict": "fail" if counts["fail"] else ("warn" if counts["warn"] else "pass"),
        "results": [r.to_dict() for r in results],
    }
    (out / "report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (out / "report.md").write_text(render_markdown(report), encoding="utf-8")
    return report


def render_markdown(report: dict) -> str:
    icon = {"pass": "✅", "warn": "⚠️", "fail": "❌", "error": "🚫"}
    lines = [
        f"# QC report — {report['title']}",
        "",
        f"**Overall: {icon.get(report['verdict'], '')} {report['verdict'].upper()}**  ",
        f"{report['segments_reviewed']} segments reviewed — "
        + ", ".join(f"{v}: {n}" for v, n in report["counts"].items() if n),
        "",
    ]
    for result in report["results"]:
        lines.append(
            f"## {icon.get(result['verdict'], '')} Segment {result['segment']} "
            f"— {result['verdict']}"
        )
        lines.append(f"{result['summary']}")
        if result.get("error"):
            lines.append(f"> error: {result['error']}")
        for finding in result["findings"]:
            where = f" _{finding['where']}_" if finding.get("where") else ""
            lines.append(f"- **{finding.get('severity', '?')}** — "
                         f"{finding.get('issue', '')}{where}")
        if result["frames"]:
            lines.append("")
            # Frames live in qc/frames/; the report sits in qc/.
            lines += [f"![segment {result['segment']}]"
                      f"({Path(f).parent.name}/{Path(f).name})"
                      for f in result["frames"]]
        lines.append("")
    return "\n".join(lines)
