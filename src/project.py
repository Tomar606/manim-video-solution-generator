"""A *project* is one video: its script, assets, intermediates and outputs.

Everything the pipeline produces for a video lives under ``projects/<slug>/``,
and ``job.json`` records how far each stage has got. That single directory is
what an editor drags avatar clips into, what the dashboard lists, and what you
zip up to hand the video off — so the layout is part of the contract, not an
implementation detail::

    projects/gauss-law/
      job.json          stage state + config
      script.md         the authored script (source of truth)
      assets/           images used in the video (answer image, photos)
      avatar/           HeyGen clips dropped here: segment_000.mp4, ...
        briefs/         what to generate for each segment (+ narration wavs)
      audio/            ElevenLabs narration, one clip per segment
      manim_code/       generated scene files
      media/            raw Manim renders
      work/             conformed clips and concatenated tracks
      qc/               extracted frames + review report
      final/            background.mp4 and the composited final cut

Stage state is advisory — every stage re-reads the files it needs, so a project
is never wedged by a stale ``job.json``. Delete it and the work is still there.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

DEFAULT_PROJECTS_DIR = "projects"

# The stages, in pipeline order. `status` is one of:
# pending | running | done | failed | skipped
STAGES = ("script", "narration", "background", "avatar", "composite", "qc")

SUBDIRS = ("assets", "avatar", "avatar/briefs", "audio", "manim_code",
           "media", "work", "qc", "final")


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return slug[:60] or "video"


@dataclass
class Project:
    slug: str
    root: Path

    # ---------------------------------------------------------------- paths #
    @property
    def job_file(self) -> Path:
        return self.root / "job.json"

    @property
    def script_path(self) -> Path:
        return self.root / "script.md"

    @property
    def assets_dir(self) -> Path:
        return self.root / "assets"

    @property
    def avatar_dir(self) -> Path:
        return self.root / "avatar"

    @property
    def briefs_dir(self) -> Path:
        return self.root / "avatar" / "briefs"

    @property
    def audio_dir(self) -> Path:
        return self.root / "audio"

    @property
    def manim_code_dir(self) -> Path:
        return self.root / "manim_code"

    @property
    def media_dir(self) -> Path:
        return self.root / "media"

    @property
    def work_dir(self) -> Path:
        return self.root / "work"

    @property
    def qc_dir(self) -> Path:
        return self.root / "qc"

    @property
    def final_dir(self) -> Path:
        return self.root / "final"

    @property
    def background_video(self) -> Path:
        """The Manim side: animations + narration, before the avatar goes on."""
        return self.final_dir / "background.mp4"

    @property
    def final_video(self) -> Path:
        return self.final_dir / f"{self.slug}.mp4"

    # ------------------------------------------------------------ lifecycle #
    @classmethod
    def create(cls, title: str, *, projects_dir: str = DEFAULT_PROJECTS_DIR,
               slug: str | None = None, exist_ok: bool = True) -> "Project":
        slug = slugify(slug or title)
        proj = cls(slug=slug, root=Path(projects_dir) / slug)
        if proj.job_file.exists() and not exist_ok:
            raise FileExistsError(f"Project already exists: {proj.root}")
        proj.ensure_dirs()
        state = proj.state
        state.setdefault("slug", slug)
        state.setdefault("title", title)
        state.setdefault("created_at", datetime.now().isoformat(timespec="seconds"))
        state.setdefault("stages", {name: {"status": "pending"} for name in STAGES})
        proj.save(state)
        return proj

    @classmethod
    def open(cls, name_or_path: str,
             *, projects_dir: str = DEFAULT_PROJECTS_DIR) -> "Project":
        """Accept a slug (``gauss-law``) or a path (``projects/gauss-law``)."""
        candidate = Path(name_or_path)
        if candidate.is_dir() and (candidate / "job.json").exists():
            root = candidate
        else:
            root = Path(projects_dir) / slugify(candidate.name or name_or_path)
        if not root.exists():
            raise FileNotFoundError(
                f"No project at {root}. Create one with:  video new \"<topic>\""
            )
        return cls(slug=root.name, root=root)

    @classmethod
    def list_all(cls, projects_dir: str = DEFAULT_PROJECTS_DIR) -> list["Project"]:
        base = Path(projects_dir)
        if not base.is_dir():
            return []
        found = [cls(slug=p.name, root=p) for p in sorted(base.iterdir())
                 if (p / "job.json").exists()]
        return found

    def ensure_dirs(self) -> None:
        for sub in SUBDIRS:
            (self.root / sub).mkdir(parents=True, exist_ok=True)
        self.final_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------- state #
    @property
    def state(self) -> dict[str, Any]:
        if not self.job_file.exists():
            return {}
        try:
            return json.loads(self.job_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            # A corrupt job.json must never block a rebuild.
            return {}

    def save(self, state: dict[str, Any]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.job_file.write_text(
            json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    @property
    def title(self) -> str:
        return self.state.get("title") or self.slug

    def config(self, key: str, default: Any = None) -> Any:
        return self.state.get("config", {}).get(key, default)

    def set_config(self, **values: Any) -> None:
        state = self.state
        state.setdefault("config", {}).update(values)
        self.save(state)

    def stage(self, name: str) -> dict[str, Any]:
        return self.state.get("stages", {}).get(name, {"status": "pending"})

    def set_stage(self, name: str, status: str, **info: Any) -> None:
        if name not in STAGES:
            raise ValueError(f"Unknown stage {name!r}. One of: {', '.join(STAGES)}")
        state = self.state
        stages = state.setdefault("stages", {})
        entry = stages.setdefault(name, {})
        entry["status"] = status
        entry["updated_at"] = datetime.now().isoformat(timespec="seconds")
        entry.update(info)
        self.save(state)

    def summary(self) -> str:
        parts = []
        for name in STAGES:
            status = self.stage(name).get("status", "pending")
            mark = {"done": "✓", "failed": "✗", "running": "…",
                    "skipped": "–"}.get(status, "·")
            parts.append(f"{mark} {name}")
        return "  ".join(parts)
