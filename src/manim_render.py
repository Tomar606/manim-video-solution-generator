"""Orientation-aware Manim rendering.

Renders a scene file at the configured resolution (landscape or portrait) into a
deterministic media directory and returns the produced mp4 path, or the captured
error output for the repair loop.

Two backends, chosen with ``RENDER_BACKEND``:

``local``   run ``manim`` from this environment. Fastest, needs Manim + LaTeX
            installed on the machine.
``docker``  run only the render inside the project's container, leaving
            everything else on the host.

The docker backend exists for the common case where the two halves of the
pipeline live in different places: Claude is reachable on the host (through a
logged-in Claude CLI, no API key), while Manim and LaTeX only exist in the
image. The repair loop needs both in the same process, so rather than move
Claude into the container — where it has no login — we send just the render out.
``auto`` (the default) uses local Manim if it's importable and falls back to the
container.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from src.config import RenderSettings

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTAINER_ROOT = "/app"          # where docker-compose bind-mounts the project
COMPOSE_SERVICE = "app"


@dataclass
class RenderResult:
    ok: bool
    video_path: str | None = None
    error: str | None = None


def _local_manim_available() -> bool:
    if shutil.which("manim") is None:
        return False
    try:
        import manim  # noqa: F401
    except Exception:
        return False
    return True


def active_backend() -> str:
    choice = (os.getenv("RENDER_BACKEND") or "auto").strip().lower()
    if choice in ("local", "docker"):
        return choice
    if choice not in ("auto", ""):
        raise ValueError(
            f"Unknown RENDER_BACKEND={choice!r}. Use auto, local or docker."
        )
    return "local" if _local_manim_available() else "docker"


def _to_container_path(path: str) -> str:
    """Translate a host path into its location inside the mounted container.

    Only paths under the repo are visible in there, so anything else is a hard
    error rather than a confusing "file not found" from Manim.
    """
    resolved = Path(path).resolve()
    try:
        relative = resolved.relative_to(REPO_ROOT)
    except ValueError:
        raise ValueError(
            f"{resolved} is outside {REPO_ROOT}, so the container can't see it. "
            f"Keep projects inside the repo when rendering with Docker "
            f"(or set RENDER_BACKEND=local)."
        )
    return f"{CONTAINER_ROOT}/{relative.as_posix()}"


def render_scene(
    manim_file: str,
    class_name: str,
    out_name: str,
    settings: RenderSettings,
    media_dir: str,
    timeout: int = 600,
) -> RenderResult:
    """Render ``class_name`` from ``manim_file``.

    Resolution/frame shape are set inside the generated file's header (see
    scene_codegen), so we don't pass -q/-r here — we only point Manim at a known
    media dir and locate the output by name.
    """
    media = Path(media_dir)
    media.mkdir(parents=True, exist_ok=True)

    pw, ph = settings.orientation.resolution
    backend = active_backend()

    def manim_argv(scene_path: str, media_path: str) -> list[str]:
        return [
            "manim", "render",
            "--disable_caching",
            "--media_dir", media_path,
            "-r", f"{pw},{ph}",      # force full resolution (don't trust defaults)
            "--fps", str(settings.fps),
            "-o", out_name,
            scene_path, class_name,
        ]

    if backend == "docker":
        try:
            inner = manim_argv(_to_container_path(manim_file),
                               _to_container_path(str(media)))
        except ValueError as exc:
            return RenderResult(False, error=str(exc))
        # -T disables TTY allocation so output stays capturable; --rm keeps the
        # per-render containers from piling up.
        cmd = ["docker", "compose", "run", "--rm", "-T", COMPOSE_SERVICE, *inner]
        cwd = str(REPO_ROOT)
    else:
        cmd = manim_argv(manim_file, str(media))
        cwd = None

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                              cwd=cwd)
    except subprocess.TimeoutExpired:
        return RenderResult(False, error=f"Manim render timed out after {timeout}s")
    except FileNotFoundError:
        if backend == "docker":
            return RenderResult(
                False,
                error="`docker` not found on PATH. Install Docker Desktop, or "
                      "set RENDER_BACKEND=local if Manim is installed here.",
            )
        return RenderResult(
            False,
            error="`manim` CLI not found on PATH. Install it (./bin/bootstrap.sh) "
                  "or render in the container with RENDER_BACKEND=docker.",
        )

    if proc.returncode != 0:
        # Manim prints the Python traceback to stderr; hand it to the repair loop.
        err = (proc.stderr or proc.stdout or "")[-6000:]
        return RenderResult(False, error=err)

    found = _locate_output(media, out_name)
    if found is None:
        listing = "\n".join(str(p) for p in media.rglob("*.mp4"))
        return RenderResult(
            False,
            error=f"Render reported success but no output named {out_name!r} was "
                  f"found under {media}.\nmp4s present:\n{listing}",
        )
    return RenderResult(True, video_path=str(found))


def _locate_output(media: Path, out_name: str) -> Path | None:
    target = out_name if out_name.endswith(".mp4") else f"{out_name}.mp4"
    matches = list((media / "videos").rglob(target))
    if matches:
        # Newest, in case of stale renders.
        return max(matches, key=lambda p: p.stat().st_mtime)
    return None
