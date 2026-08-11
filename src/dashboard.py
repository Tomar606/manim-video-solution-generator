"""A local web UI for people who don't use terminals.

The dashboard is a thin client: every button shells out to the same ``video``
subcommand you'd type by hand, and streams its output back. Nothing here knows
how to render a video — which is the point. The CLI, Claude Code and this UI all
drive the identical stage functions, so the browser can never drift from what
the pipeline actually does.

Run it with ``video dashboard``; it serves on localhost only by default, because
rendering happens on this machine and the project folders are right there on
disk. Pointing it at 0.0.0.0 puts an unauthenticated file-editing UI on your
network — only do that on a trusted LAN.
"""
# NOTE: deliberately no `from __future__ import annotations` here. FastAPI reads
# the route signatures at runtime to decide what's a body, a query param or an
# upload, and the fastapi types are imported inside create_app() so this module
# stays importable on machines without FastAPI. With postponed annotations those
# names resolve to unresolvable strings and every Request/UploadFile parameter
# silently degrades into a required query parameter (HTTP 422 on every POST/PUT).

import asyncio
import json
import shutil
import subprocess
import sys
import threading
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from src.project import DEFAULT_PROJECTS_DIR, Project

REPO_ROOT = Path(__file__).resolve().parents[1]

# Stages the UI is allowed to trigger, and the argv it builds for each. Keeping
# this an explicit allow-list means a crafted request can't run arbitrary flags.
STAGES: dict[str, list[str]] = {
    "script": ["script", "--force"],
    "narrate": ["narrate"],
    "background": ["background", "--continue-on-error"],
    "avatar": ["avatar"],
    "briefs": ["avatar", "--briefs"],
    "qc": ["qc"],
    "composite": ["composite"],
    "build": ["build", "--continue-on-error"],
}

MAX_LOG_LINES = 4000


@dataclass
class Job:
    """One stage run. Renders take tens of minutes, so a job has to outlive the
    page that started it: the log is addressed by absolute line number, and the
    job stays findable by project after a refresh."""

    id: str
    project: str
    stage: str
    done: bool = False
    returncode: int | None = None
    process: subprocess.Popen | None = None

    _lines: list[str] = field(default_factory=list)
    # Lines trimmed off the front. Clients count in absolute line numbers, so
    # trimming the buffer can never desync them the way a plain deque did.
    dropped: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def append(self, line: str) -> None:
        with self._lock:
            self._lines.append(line)
            excess = len(self._lines) - MAX_LOG_LINES
            if excess > 0:
                del self._lines[:excess]
                self.dropped += excess

    def since(self, index: int) -> tuple[list[str], int, bool]:
        """Lines from absolute ``index``. Returns (lines, next_index, skipped)."""
        with self._lock:
            total = self.dropped + len(self._lines)
            skipped = index < self.dropped
            start = max(index, self.dropped)
            return self._lines[start - self.dropped:], total, skipped


_jobs: dict[str, Job] = {}
_active: dict[str, str] = {}          # project slug -> job id
_jobs_lock = threading.Lock()


def active_job(project: str) -> Job | None:
    with _jobs_lock:
        job = _jobs.get(_active.get(project, ""))
    return job


def _run_job(job: Job, argv: list[str]) -> None:
    cmd = [sys.executable, str(REPO_ROOT / "video.py"), *argv]
    job.append(f"$ {' '.join(cmd[1:])}\n")
    try:
        proc = subprocess.Popen(
            cmd, cwd=str(REPO_ROOT), stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, bufsize=1,
            env={**__import__("os").environ, "PYTHONUNBUFFERED": "1"},
        )
    except OSError as exc:
        job.append(f"failed to start: {exc}\n")
        job.done = True
        job.returncode = -1
        return
    job.process = proc
    assert proc.stdout is not None
    for line in proc.stdout:
        job.append(line)
    proc.wait()
    job.returncode = proc.returncode
    job.append(f"\n[exit {proc.returncode}]\n")
    job.done = True


def start_job(project: str, stage: str, extra: list[str] | None = None,
              projects_dir: str = DEFAULT_PROJECTS_DIR) -> tuple[Job, bool]:
    """Start a stage. Returns (job, started) — an already-running job for this
    project is handed back instead of starting a second one, because two renders
    writing the same folder corrupts both."""
    if stage not in STAGES:
        raise KeyError(stage)

    running = active_job(project)
    if running is not None and not running.done:
        return running, False

    job = Job(id=uuid.uuid4().hex[:12], project=project, stage=stage)
    # --projects-dir is a top-level flag, so it goes before the subcommand.
    argv = ["--projects-dir", projects_dir,
            STAGES[stage][0], project, *STAGES[stage][1:], *(extra or [])]
    with _jobs_lock:
        _jobs[job.id] = job
        _active[project] = job.id
    threading.Thread(target=_run_job, args=(job, argv), daemon=True).start()
    return job, True


def build_timeline(project: Project) -> dict:
    """Everything the editor UI draws: one entry per beat, laid out in time.

    A beat is a clip. Its length is the narration length (that's what every
    stage is timed against), and each track reports whether its piece of that
    clip exists yet — animation rendered, presenter dropped in, cues emitted.
    """
    from src.script_parser import ScriptParseError, parse_script_file

    if not project.script_path.exists():
        return {"clips": [], "duration": 0.0, "error": "no script yet"}
    try:
        # resolve=False: a missing photo should not stop the timeline drawing.
        script = parse_script_file(str(project.script_path), resolve=False)
    except ScriptParseError as exc:
        return {"clips": [], "duration": 0.0, "error": str(exc)}

    state = project.state
    timing = state.get("timing", {})
    rendered = state.get("stages", {}).get("background", {}).get("segments", {})

    qc_by_index: dict[int, dict] = {}
    qc_file = project.qc_dir / "report.json"
    if qc_file.exists():
        try:
            for result in json.loads(qc_file.read_text(encoding="utf-8"))["results"]:
                qc_by_index[result["segment"]] = result
        except (json.JSONDecodeError, KeyError):
            pass

    avatars = {}
    if project.avatar_dir.is_dir():
        from src.avatar import _index_from_name
        for path in project.avatar_dir.iterdir():
            if path.is_file() and path.suffix.lower() in (".mp4", ".mov", ".webm"):
                idx = _index_from_name(path)
                if idx is not None:
                    avatars[idx] = path.name

    clips, start = [], 0.0
    for seg in script.segments:
        info = timing.get(str(seg.index), {})
        duration = float(info.get("duration") or seg.target_duration or 0.0)
        render_info = rendered.get(str(seg.index)) or {}

        cues = []
        manim_path = render_info.get("manim")
        if manim_path:
            from src.scene_codegen import cues_file_for
            from src import sfx
            cues = [{"time": c.time, "name": c.name}
                    for c in sfx.read_cue_file(cues_file_for(manim_path))]

        qc = qc_by_index.get(seg.index)
        clips.append({
            "index": seg.index,
            "speaker": seg.speaker,
            "narration": seg.narration,
            "note": seg.note or "",
            "equations": seg.equations,
            "images": [{"caption": i.caption, "raw": i.raw, "layout": i.layout}
                       for i in seg.images],
            "is_outro": seg.is_outro,
            "kind": ("answer" if seg.is_outro else
                     "photo" if seg.is_photo_beat else
                     "equation" if seg.equations else "concept"),
            "start": round(start, 3),
            "duration": round(duration, 3),
            "rendered": bool(render_info.get("video")),
            "avatar": avatars.get(seg.index),
            "cues": cues,
            "qc": {"verdict": qc["verdict"], "summary": qc["summary"],
                   "findings": qc["findings"]} if qc else None,
        })
        start += duration

    return {
        "clips": clips,
        "duration": round(start, 3),
        "title": script.title,
        "orientation": script.orientation.value,
        "chroma": script.chroma.preset.value,
        "speakers": sorted(script.speakers),
        "error": None,
    }


def create_app(projects_dir: str = DEFAULT_PROJECTS_DIR):
    from fastapi import FastAPI, HTTPException, Request, UploadFile
    from fastapi.responses import (FileResponse, HTMLResponse, JSONResponse,
                                   StreamingResponse)

    app = FastAPI(title="Video pipeline")

    def _project(slug: str) -> Project:
        try:
            return Project.open(slug, projects_dir=projects_dir)
        except FileNotFoundError:
            raise HTTPException(404, f"No project {slug!r}")

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return INDEX_HTML

    @app.get("/api/projects")
    def list_projects():
        out = []
        for p in Project.list_all(projects_dir):
            state = p.state
            out.append({
                "slug": p.slug,
                "title": p.title,
                "stages": {k: v.get("status", "pending")
                           for k, v in state.get("stages", {}).items()},
                "has_background": p.background_video.exists(),
                "has_final": p.final_video.exists(),
            })
        return out

    @app.post("/api/projects")
    async def create_project(request: Request):
        body = await request.json()
        topic = (body.get("topic") or "").strip()
        if not topic:
            raise HTTPException(400, "topic is required")
        project = Project.create(topic, projects_dir=projects_dir)
        project.set_config(
            topic=topic,
            language=body.get("language", "hinglish"),
            orientation=body.get("orientation", "landscape"),
            theme=body.get("theme", "midnight"),
            chroma=body.get("chroma", "none"),
            voice=body.get("voice", "George"),
        )
        return {"slug": project.slug}

    @app.get("/api/projects/{slug}")
    def get_project(slug: str):
        p = _project(slug)
        qc = None
        qc_file = p.qc_dir / "report.json"
        if qc_file.exists():
            try:
                qc = json.loads(qc_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                qc = None
        avatars = sorted(f.name for f in p.avatar_dir.glob("*")
                         if f.suffix.lower() in (".mp4", ".mov", ".webm"))
        return {
            "slug": p.slug,
            "title": p.title,
            "state": p.state,
            "script": p.script_path.read_text(encoding="utf-8")
                      if p.script_path.exists() else "",
            "qc": qc,
            "avatars": avatars,
            "has_background": p.background_video.exists(),
            "has_final": p.final_video.exists(),
        }

    @app.put("/api/projects/{slug}/script")
    async def save_script(slug: str, request: Request):
        from src.script_parser import ScriptParseError, parse_script

        p = _project(slug)
        body = await request.json()
        text = body.get("script", "")

        # Validate before writing. Saving a script that can't parse and calling
        # the stage "done" only moves the failure to narrate, an hour later.
        try:
            parsed = parse_script(text, resolve=False)
        except ScriptParseError as exc:
            raise HTTPException(400, f"Script does not parse: {exc}")
        if not parsed.segments:
            raise HTTPException(400, "Script has no [speaker] beats.")

        p.script_path.write_text(text, encoding="utf-8")
        p.set_stage("script", "done", path=str(p.script_path))
        return {"ok": True, "segments": len(parsed.segments)}

    @app.post("/api/projects/{slug}/run/{stage}")
    def run_stage(slug: str, stage: str):
        _project(slug)
        try:
            job, started = start_job(slug, stage, projects_dir=projects_dir)
        except KeyError:
            raise HTTPException(400, f"Unknown stage {stage!r}")
        return {"job": job.id, "started": started, "stage": job.stage}

    @app.get("/api/projects/{slug}/timeline")
    def timeline(slug: str):
        return build_timeline(_project(slug))

    @app.patch("/api/projects/{slug}/segment/{index}")
    async def edit_segment(slug: str, index: int, request: Request):
        """Edit one beat from the inspector and write it back to script.md."""
        from src.script_edit import apply_edit, rebuild
        from src.script_parser import ScriptParseError, parse_script

        p = _project(slug)
        if not p.script_path.exists():
            raise HTTPException(404, "no script")
        changes = await request.json()

        original = p.script_path.read_text(encoding="utf-8")
        script = parse_script(original, resolve=False)
        match = next((s for s in script.segments if s.index == index), None)
        if match is None:
            raise HTTPException(404, f"no beat {index}")

        apply_edit(match, changes)
        updated = rebuild(original, script.segments)
        try:
            reparsed = parse_script(updated, resolve=False)
        except ScriptParseError as exc:
            # Refuse to write something we can't read back.
            raise HTTPException(400, f"Edit would break the script: {exc}")
        if len(reparsed.segments) != len(script.segments):
            raise HTTPException(400, "Edit would change the number of beats.")

        p.script_path.write_text(updated, encoding="utf-8")
        return {"ok": True}

    @app.get("/api/projects/{slug}/segment/{index}/video")
    def segment_video(slug: str, index: int):
        """The raw render of one beat, for scrubbing a single clip."""
        p = _project(slug)
        info = (p.state.get("stages", {}).get("background", {})
                .get("segments", {}).get(str(index)) or {})
        path = info.get("video")
        if not path or not Path(path).exists():
            raise HTTPException(404, "that beat isn't rendered yet")
        return FileResponse(path, media_type="video/mp4")

    @app.get("/api/projects/{slug}/job")
    def current_job(slug: str):
        """Lets a reloaded page find the render it left running."""
        job = active_job(slug)
        if job is None:
            return {"job": None}
        return {"job": job.id, "stage": job.stage, "done": job.done,
                "code": job.returncode}

    @app.post("/api/jobs/{job_id}/stop")
    def stop_job(job_id: str):
        job = _jobs.get(job_id)
        if job is None:
            raise HTTPException(404, "no such job")
        if job.process and not job.done:
            job.process.terminate()
            job.append("\n[stopped by user]\n")
        return {"ok": True}

    @app.get("/api/jobs/{job_id}/stream")
    async def stream_job(job_id: str, request: Request, since: int = 0):
        job = _jobs.get(job_id)
        if job is None:
            raise HTTPException(404, "no such job")

        async def gen():
            # Absolute line numbers, so a reconnect resumes exactly where it
            # left off and buffer trimming can't desync the client.
            cursor = since
            while True:
                if await request.is_disconnected():
                    return
                lines, total, skipped = job.since(cursor)
                if skipped:
                    yield ("data: " + json.dumps(
                        {"line": "… earlier output trimmed …\n"}) + "\n\n")
                for line in lines:
                    yield "data: " + json.dumps({"line": line, "n": cursor}) + "\n\n"
                    cursor += 1
                cursor = max(cursor, total)
                if job.done and cursor >= total:
                    yield ("data: " + json.dumps(
                        {"done": True, "code": job.returncode}) + "\n\n")
                    return
                await asyncio.sleep(0.4)

        return StreamingResponse(gen(), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache",
                                          "X-Accel-Buffering": "no"})

    @app.post("/api/projects/{slug}/avatar")
    async def upload_avatar(slug: str, files: list[UploadFile]):
        p = _project(slug)
        p.avatar_dir.mkdir(parents=True, exist_ok=True)
        saved = []
        for upload in files:
            name = Path(upload.filename or "clip.mp4").name  # no path traversal
            if Path(name).suffix.lower() not in (".mp4", ".mov", ".webm", ".mkv"):
                continue
            dest = p.avatar_dir / name
            with open(dest, "wb") as fh:
                shutil.copyfileobj(upload.file, fh)
            saved.append(name)
        return {"saved": saved}

    @app.post("/api/projects/{slug}/assets")
    async def upload_asset(slug: str, files: list[UploadFile]):
        p = _project(slug)
        p.assets_dir.mkdir(parents=True, exist_ok=True)
        saved = []
        for upload in files:
            name = Path(upload.filename or "image.png").name
            dest = p.assets_dir / name
            with open(dest, "wb") as fh:
                shutil.copyfileobj(upload.file, fh)
            saved.append(name)
        return {"saved": saved}

    @app.get("/api/projects/{slug}/video/{which}")
    def get_video(slug: str, which: str):
        p = _project(slug)
        path = p.final_video if which == "final" else p.background_video
        if not path.exists():
            raise HTTPException(404, "not rendered yet")
        return FileResponse(path, media_type="video/mp4", filename=path.name)

    @app.get("/api/projects/{slug}/frame/{name}")
    def get_frame(slug: str, name: str):
        p = _project(slug)
        path = p.qc_dir / "frames" / Path(name).name
        if not path.exists():
            raise HTTPException(404, "no such frame")
        return FileResponse(path, media_type="image/png")

    @app.get("/api/health")
    def health():
        from src import llm
        return JSONResponse({
            "ffmpeg": bool(shutil.which("ffmpeg")),
            "claude_cli": bool(shutil.which("claude")),
            "backend": llm.describe_backend(),
        })

    return app


def serve(host: str = "127.0.0.1", port: int = 8000,
          projects_dir: str = DEFAULT_PROJECTS_DIR,
          open_browser: bool = True) -> None:
    try:
        import uvicorn
    except ModuleNotFoundError:
        print("❌ The dashboard needs fastapi and uvicorn:\n"
              "   pip install fastapi uvicorn python-multipart")
        raise SystemExit(1)

    app = create_app(projects_dir)
    url = f"http://{'localhost' if host in ('127.0.0.1', '0.0.0.0') else host}:{port}"
    print(f"\n🖥  Dashboard: {url}\n   (Ctrl-C to stop)\n")
    if open_browser:
        import webbrowser
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    uvicorn.run(app, host=host, port=port, log_level="warning")


# The page is deliberately a single self-contained string: no build step, no
# node_modules, no CDN. An editor clones the repo and it works offline.
#
# The layout is a non-linear editor because that's what this pipeline already
# is: a beat is a clip, and each stage is a track over those clips. Making that
# literal means someone who has used Premiere or CapCut can read the state of a
# video at a glance — which clips exist, which are missing a presenter, which
# QC flagged — instead of learning our stage names first.
INDEX_HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Video Editor</title>
<style>
:root{
  --bg:#0d1017; --panel:#151922; --panel2:#1b202b; --line:#272d3a;
  --txt:#e8edf7; --dim:#8f9bb3; --accent:#5b8def; --accent2:#f2a65a;
  --ok:#3ecf8e; --warn:#f2a65a; --bad:#e5484d; --track:#11141c;
  --clip-anim:#2f4a86; --clip-photo:#6d4a86; --clip-answer:#86653a;
  --clip-avatar:#2f6b52; --clip-audio:#3a4a63;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font:13px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif;
     background:var(--bg);color:var(--txt);height:100vh;overflow:hidden}
button{font:inherit;cursor:pointer;border:0;border-radius:5px;
       background:var(--panel2);color:var(--txt);padding:6px 11px}
button:hover:not(:disabled){background:#2a3242}
button:disabled{opacity:.4;cursor:not-allowed}
button.primary{background:var(--accent);color:#fff}
button.primary:hover:not(:disabled){background:#6d9bf5}
button.danger{background:var(--bad);color:#fff}
input,textarea,select{font:inherit;background:var(--track);color:var(--txt);
  border:1px solid var(--line);border-radius:5px;padding:7px 9px;width:100%}
textarea{resize:vertical;font-family:inherit}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px}
.dim{color:var(--dim)}
.row{display:flex;gap:8px;align-items:center}
.hide{display:none!important}

/* ---------- app shell: monitor row on top, timeline below ---------- */
#app{display:grid;height:100vh;
     grid-template-rows:46px minmax(0,1fr) auto;
     grid-template-columns:230px minmax(0,1fr) 300px;
     grid-template-areas:"top top top" "bins monitor inspect" "tl tl tl"}

/* ---------- toolbar ---------- */
#top{grid-area:top;display:flex;align-items:center;gap:14px;padding:0 14px;
     background:var(--panel);border-bottom:1px solid var(--line)}
#top h1{font-size:14px;font-weight:600;white-space:nowrap}
#top .sep{width:1px;height:22px;background:var(--line)}
#stages{display:flex;gap:5px;flex-wrap:nowrap;overflow:auto}
#stages button{font-size:12px;padding:5px 9px;white-space:nowrap}
.badge{font-size:11px;padding:2px 7px;border-radius:99px;border:1px solid var(--line)}
.badge.done{color:var(--ok);border-color:var(--ok)}
.badge.failed{color:var(--bad);border-color:var(--bad)}
.badge.running{color:var(--accent);border-color:var(--accent)}
.badge.pending,.badge.skipped{color:var(--dim)}

/* ---------- left bin ---------- */
#bins{grid-area:bins;background:var(--panel);border-right:1px solid var(--line);
      overflow:auto;padding:10px}
.binhead{font-size:11px;text-transform:uppercase;letter-spacing:.07em;
         color:var(--dim);margin:14px 0 7px}
.binhead:first-child{margin-top:0}
.item{padding:7px 9px;border-radius:5px;cursor:pointer;font-size:12.5px}
.item:hover{background:var(--panel2)}
.item.sel{background:var(--panel2);box-shadow:inset 2px 0 0 var(--accent)}
.item small{display:block;color:var(--dim);font-size:11px}

/* ---------- monitor ---------- */
#monitor{grid-area:monitor;display:flex;flex-direction:column;
         background:#07090d;min-width:0;overflow:hidden}
#screen{flex:1;display:flex;align-items:center;justify-content:center;
        padding:14px;min-height:0}
#screen video,#screen img{max-width:100%;max-height:100%;border-radius:6px;
        background:#000;box-shadow:0 6px 26px #0009}
#placeholder{color:var(--dim);text-align:center;max-width:420px}
#placeholder h2{font-size:15px;margin-bottom:8px;color:var(--txt)}
#transport{display:flex;align-items:center;gap:12px;padding:8px 14px;
           background:var(--panel);border-top:1px solid var(--line)}
#tc{font-family:ui-monospace,Menlo,monospace;font-size:12px;color:var(--dim)}

/* ---------- inspector ---------- */
#inspect{grid-area:inspect;background:var(--panel);border-left:1px solid var(--line);
         overflow:auto;padding:12px}
#inspect h3{font-size:12px;text-transform:uppercase;letter-spacing:.07em;
            color:var(--dim);margin-bottom:10px}
.field{margin-bottom:11px}
.field label{display:block;font-size:11px;color:var(--dim);margin-bottom:4px}
.pill{display:inline-block;font-size:11px;padding:2px 8px;border-radius:99px;
      background:var(--panel2);color:var(--dim);margin:0 4px 4px 0}

/* ---------- timeline ---------- */
#tl{grid-area:tl;background:var(--panel);border-top:1px solid var(--line);
    display:flex;flex-direction:column;max-height:52vh}
#tlbar{display:flex;align-items:center;gap:10px;padding:6px 12px;
       border-bottom:1px solid var(--line)}
#tlscroll{overflow:auto;flex:1;max-height:230px}
#tlinner{position:relative;min-width:100%}
.ruler{height:22px;position:relative;border-bottom:1px solid var(--line);
       background:var(--track)}
.tick{position:absolute;top:0;height:100%;border-left:1px solid var(--line);
      padding-left:4px;font-size:10px;color:var(--dim);line-height:22px}
.track{position:relative;height:46px;border-bottom:1px solid var(--line);
       background:var(--track)}
.track.audio{height:34px}
.tname{position:sticky;left:0;z-index:3;width:88px;height:100%;float:left;
       background:var(--panel);border-right:1px solid var(--line);
       font-size:10px;letter-spacing:.06em;color:var(--dim);
       display:flex;align-items:center;padding-left:9px;text-transform:uppercase}
.lane{position:absolute;left:88px;right:0;top:0;bottom:0}
.clip{position:absolute;top:4px;bottom:4px;border-radius:4px;overflow:hidden;
      cursor:pointer;font-size:11px;padding:3px 6px;color:#fff;
      border:1px solid #0004;transition:filter .1s}
.clip:hover{filter:brightness(1.25)}
.clip.sel{outline:2px solid var(--accent);outline-offset:-2px;z-index:2}
.clip .t{font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.clip .s{opacity:.75;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.clip.ghost{background:repeating-linear-gradient(45deg,#1b202b,#1b202b 6px,#161b24 6px,#161b24 12px);
            border:1px dashed var(--line);color:var(--dim)}
.clip.bad{box-shadow:inset 0 -3px 0 var(--bad)}
.clip.warn{box-shadow:inset 0 -3px 0 var(--warn)}
.clip.okmark{box-shadow:inset 0 -3px 0 var(--ok)}
.cue{position:absolute;top:8px;width:2px;height:18px;background:var(--accent2);
     border-radius:1px}
.cue::after{content:'';position:absolute;top:-4px;left:-2px;width:6px;height:6px;
     border-radius:50%;background:var(--accent2)}
#playhead{position:absolute;top:0;bottom:0;width:2px;background:var(--bad);
     z-index:4;pointer-events:none;left:88px}

/* ---------- console ---------- */
#console{border-top:1px solid var(--line);background:#080a0f;height:150px;
         overflow:auto;padding:9px 12px;white-space:pre-wrap;
         font-family:ui-monospace,Menlo,monospace;font-size:11.5px;color:#c6d0e0}
#conbar{display:flex;align-items:center;gap:10px;padding:5px 12px;
        background:var(--panel);border-top:1px solid var(--line);font-size:11px}
</style></head><body>

<div id="app">
  <div id="top">
    <h1>🎬 Video Editor</h1>
    <div class="sep"></div>
    <div id="stages"></div>
    <div class="sep"></div>
    <button id="stopBtn" class="danger hide" onclick="stopJob()">■ Stop</button>
    <span id="jobstate" class="dim"></span>
    <div style="flex:1"></div>
    <span id="health" class="dim" style="font-size:11px"></span>
  </div>

  <div id="bins">
    <div class="binhead">Videos</div>
    <div id="projlist"></div>
    <div class="row" style="margin-top:9px">
      <input id="newTopic" placeholder="New video topic…" style="font-size:12px">
    </div>
    <div class="row" style="margin-top:6px">
      <select id="newLang" style="font-size:12px">
        <option value="hinglish">Hinglish</option>
        <option value="english">English</option>
      </select>
      <button class="primary" onclick="createProject()">+</button>
    </div>
    <div class="binhead">Presenter clips</div>
    <div id="avatarbin" class="dim" style="font-size:12px">—</div>
    <div id="drop" class="item" style="border:1.5px dashed var(--line);
         text-align:center;padding:14px;margin-top:8px;color:var(--dim)">
      drop HeyGen clips here
    </div>
  </div>

  <div id="monitor">
    <div id="screen">
      <div id="placeholder">
        <h2>No video selected</h2>
        <p>Pick one on the left, or type a topic to start a new one.</p>
      </div>
    </div>
    <div id="transport">
      <button onclick="playPause()" id="playBtn">▶</button>
      <span id="tc">00:00 / 00:00</span>
      <div style="flex:1"></div>
      <span class="dim" id="srcLabel"></span>
      <button id="dlBtn" class="hide" onclick="downloadCut()">⤓ Download</button>
    </div>
  </div>

  <div id="inspect"><h3>Inspector</h3>
    <p class="dim">Select a clip in the timeline to edit that beat.</p></div>

  <div id="tl">
    <div id="tlbar">
      <strong style="font-size:12px">Timeline</strong>
      <span class="dim" id="tlinfo"></span>
      <div style="flex:1"></div>
      <span class="dim" style="font-size:11px">zoom</span>
      <input type="range" id="zoom" min="6" max="90" value="26" style="width:130px">
    </div>
    <div id="tlscroll"><div id="tlinner"></div></div>
    <div id="conbar">
      <strong>Console</strong><span class="dim" id="conhint">idle</span>
      <div style="flex:1"></div>
      <button onclick="toggleConsole()" id="conToggle" style="font-size:11px">show</button>
    </div>
    <pre id="console" class="hide">ready.</pre>
  </div>
</div>

<script>
const STAGES = [
  ['script','Write script'], ['narrate','Narration'], ['background','Render'],
  ['briefs','Avatar briefs'], ['avatar','Load clips'], ['qc','Check'],
  ['composite','Composite'], ['build','▶ Build all']
];
let current=null, tl=null, sel=null, es=null, job=null, pps=26, projects=[];

const $ = id => document.getElementById(id);
const esc = s => (s==null?'':String(s)).replace(/[&<>"]/g,
  c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fmt = t => `${String(Math.floor(t/60)).padStart(2,'0')}:${String(Math.floor(t%60)).padStart(2,'0')}`;

async function api(path, opts){
  const r = await fetch('/api'+path, opts);
  const ct = r.headers.get('content-type')||'';
  const body = ct.includes('json') ? await r.json() : await r.text();
  if(!r.ok) throw new Error(body.detail || body || r.statusText);
  return body;
}

/* ---------------- projects ---------------- */
async function loadProjects(){
  projects = await api('/projects');
  $('projlist').innerHTML = projects.map(p=>`
    <div class="item ${p.slug===current?'sel':''}" onclick="openProject('${p.slug}')">
      ${esc(p.title)}<small>${p.has_final?'final cut':p.has_background?'background only':'not rendered'}</small>
    </div>`).join('') || '<p class="dim" style="font-size:12px">No videos yet.</p>';
}

async function createProject(){
  const topic = $('newTopic').value.trim(); if(!topic) return;
  try{
    const r = await api('/projects',{method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({topic, language:$('newLang').value})});
    $('newTopic').value='';
    await loadProjects(); openProject(r.slug);
  }catch(e){ alert('Could not create: '+e.message); }
}

async function openProject(slug){
  current = slug; sel = null;
  await loadProjects();
  const p = await api('/projects/'+slug);
  renderStages(p.state.stages||{});
  $('avatarbin').innerHTML = p.avatars.length
    ? p.avatars.map(a=>`<div class="item mono" style="font-size:11.5px">${esc(a)}</div>`).join('')
    : '<span class="dim" style="font-size:12px">none yet</span>';
  loadMonitor(p);
  await loadTimeline();
  wireDrop();
  const j = await api('/projects/'+slug+'/job');
  if(j.job && !j.done){ job=j.job; setRunning(j.stage); attach(j.job,0); }
  else setRunning(null);
}

function renderStages(st){
  $('stages').innerHTML = STAGES.map(([k,label])=>{
    const s = (st[k==='briefs'?'avatar':k]||{}).status||'pending';
    return `<button data-stage="${k}" onclick="run('${k}')"
      class="${k==='build'?'primary':''}" title="${s}">${label}</button>`;
  }).join('');
}

/* ---------------- monitor ---------------- */
function loadMonitor(p){
  const which = p.has_final ? 'final' : p.has_background ? 'background' : null;
  $('srcLabel').textContent = which==='final' ? 'final cut (with presenter)'
                            : which==='background' ? 'background only' : '';
  $('dlBtn').classList.toggle('hide', !which);
  if(!which){
    $('screen').innerHTML = `<div id="placeholder"><h2>${esc(p.title)}</h2>
      <p class="dim">Nothing rendered yet. Run <b>Render</b> to build the animation,
      or click a clip below to edit what it says.</p></div>`;
    return;
  }
  $('screen').innerHTML =
    `<video id="vid" src="/api/projects/${p.slug}/video/${which}"></video>`;
  const v = $('vid');
  v.addEventListener('timeupdate', ()=>{ movePlayhead(v.currentTime);
    $('tc').textContent = `${fmt(v.currentTime)} / ${fmt(v.duration||0)}`; });
  v.addEventListener('loadedmetadata', ()=>{
    $('tc').textContent = `00:00 / ${fmt(v.duration||0)}`; });
  v.addEventListener('play', ()=>$('playBtn').textContent='❚❚');
  v.addEventListener('pause', ()=>$('playBtn').textContent='▶');
}
function playPause(){ const v=$('vid'); if(!v) return; v.paused?v.play():v.pause(); }
function downloadCut(){
  const p = projects.find(x=>x.slug===current); if(!p) return;
  location.href = `/api/projects/${current}/video/${p.has_final?'final':'background'}`;
}

/* ---------------- timeline ---------------- */
async function loadTimeline(){
  tl = await api('/projects/'+current+'/timeline');
  drawTimeline();
}

function drawTimeline(){
  const inner = $('tlinner');
  if(!tl || tl.error || !tl.clips.length){
    inner.innerHTML = `<p class="dim" style="padding:16px">${
      tl && tl.error ? 'Script problem: '+esc(tl.error)
                     : 'No beats yet — write a script first.'}</p>`;
    $('tlinfo').textContent=''; return;
  }
  const W = Math.max(tl.duration*pps, 200);
  $('tlinfo').textContent =
    `${tl.clips.length} clips · ${fmt(tl.duration)} · ${tl.orientation}`
    + (tl.chroma!=='none' ? ` · presenter: ${tl.chroma.replace('_',' ')}` : '');

  const step = pps>45?5:pps>18?10:30;
  let ruler = '';
  for(let t=0;t<=tl.duration;t+=step)
    ruler += `<div class="tick" style="left:${88+t*pps}px">${fmt(t)}</div>`;

  const lane = (clips)=>`<div class="lane" style="width:${W}px">${clips}</div>`;

  const anim = tl.clips.map(c=>{
    const bg = c.kind==='answer'?'var(--clip-answer)'
             : c.kind==='photo'?'var(--clip-photo)':'var(--clip-anim)';
    const mark = c.qc ? (c.qc.verdict==='fail'?'bad':c.qc.verdict==='warn'?'warn':'okmark') : '';
    const label = c.kind==='answer'?'⬛ Answer card'
                : c.kind==='photo'?'🖼 Photo'
                : c.equations.length?'∑ '+c.equations[0].slice(0,26):'💬 Concept';
    return `<div class="clip ${c.rendered?'':'ghost'} ${mark} ${sel===c.index?'sel':''}"
      style="left:${c.start*pps}px;width:${Math.max(c.duration*pps-2,26)}px;
             ${c.rendered?`background:${bg}`:''}"
      onclick="selectClip(${c.index})" title="${esc(c.narration)}">
      <div class="t">${esc(label)}</div><div class="s">${esc(c.narration)}</div></div>`;
  }).join('');

  const av = tl.clips.map(c=>`<div class="clip ${c.avatar?'':'ghost'} ${sel===c.index?'sel':''}"
      style="left:${c.start*pps}px;width:${Math.max(c.duration*pps-2,26)}px;
             ${c.avatar?'background:var(--clip-avatar)':''}"
      onclick="selectClip(${c.index})"
      title="${c.avatar?esc(c.avatar):'no presenter clip for this beat'}">
      <div class="t">${c.avatar?'🧑 Presenter':'— missing'}</div></div>`).join('');

  const aud = tl.clips.map(c=>`<div class="clip ${sel===c.index?'sel':''}"
      style="left:${c.start*pps}px;width:${Math.max(c.duration*pps-2,26)}px;
             background:var(--clip-audio);top:3px;bottom:3px"
      onclick="selectClip(${c.index})"><div class="s">🎙 ${esc(c.narration)}</div></div>`).join('');

  const cues = tl.clips.flatMap(c=>(c.cues||[]).map(q=>
      `<div class="cue" style="left:${(c.start+q.time)*pps}px" title="${esc(q.name)}"></div>`)).join('');

  inner.innerHTML = `
    <div class="ruler" style="width:${W+88}px">${ruler}</div>
    <div class="track"><div class="tname">Animation</div>${lane(anim)}</div>
    <div class="track"><div class="tname">Presenter</div>${lane(av)}</div>
    <div class="track audio"><div class="tname">Narration</div>${lane(aud)}</div>
    <div class="track audio"><div class="tname">Sound FX</div>${lane(cues)}</div>
    <div id="playhead" style="left:88px"></div>`;
}

function movePlayhead(t){
  const ph=$('playhead'); if(ph) ph.style.left = (88 + t*pps) + 'px';
}

function selectClip(i){
  sel = i; drawTimeline();
  const c = tl.clips.find(x=>x.index===i); if(!c) return;
  const v = $('vid'); if(v){ v.currentTime = c.start + 0.05; }
  showInspector(c);
}

/* ---------------- inspector ---------------- */
function showInspector(c){
  const qc = c.qc ? `<div class="field"><label>QC</label>
      <div class="pill" style="color:${c.qc.verdict==='pass'?'var(--ok)':
        c.qc.verdict==='warn'?'var(--warn)':'var(--bad)'}">${c.qc.verdict}</div>
      <div class="dim" style="font-size:12px">${esc(c.qc.summary)}</div>
      ${c.qc.findings.map(f=>`<div class="dim" style="font-size:12px">• ${esc(f.issue)}</div>`).join('')}
    </div>` : '';

  $('inspect').innerHTML = `
    <h3>Clip ${c.index} · ${c.kind}</h3>
    <div class="field"><label>Spoken line (this is read aloud — no symbols)</label>
      <textarea id="f_narration" rows="4">${esc(c.narration)}</textarea></div>
    <div class="field"><label>Animation direction</label>
      <textarea id="f_note" rows="3">${esc(c.note)}</textarea></div>
    ${c.equations.length?`<div class="field"><label>Equation (LaTeX)</label>
      <input id="f_eq" class="mono" value="${esc(c.equations[0])}"></div>`:''}
    ${c.images.length?`<div class="field"><label>Photo caption</label>
      <input id="f_caption" value="${esc(c.images[0].caption)}">
      <div class="dim mono" style="font-size:11px;margin-top:4px">${esc(c.images[0].raw)}</div></div>`:''}
    <div class="field"><label>Speaker</label>
      <input id="f_speaker" value="${esc(c.speaker)}"></div>
    <div class="row"><button class="primary" onclick="saveClip(${c.index})">Save clip</button>
      <span id="saveMsg" class="dim"></span></div>
    <div class="field" style="margin-top:14px">
      <span class="pill">${c.duration.toFixed(1)}s</span>
      <span class="pill">starts ${fmt(c.start)}</span>
      <span class="pill">${c.rendered?'rendered':'not rendered'}</span>
      <span class="pill">${c.avatar?'presenter ✓':'no presenter'}</span>
      ${(c.cues||[]).length?`<span class="pill">${c.cues.length} sound cues</span>`:''}
    </div>
    ${c.rendered?`<div class="field"><label>This clip only</label>
      <video controls style="width:100%;border-radius:6px"
        src="/api/projects/${current}/segment/${c.index}/video"></video></div>`:''}
    ${qc}`;
}

async function saveClip(i){
  const get = id => { const el=$(id); return el?el.value:undefined; };
  const body = {narration:get('f_narration'), note:get('f_note'),
                speaker:get('f_speaker')};
  const eq = get('f_eq'); if(eq!==undefined) body.equations=[eq];
  const cap = get('f_caption'); if(cap!==undefined) body.caption=cap;
  const msg = $('saveMsg');
  try{
    await api(`/projects/${current}/segment/${i}`,{method:'PATCH',
      headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
    msg.style.color=''; msg.textContent='saved ✓ — re-render to see it';
    await loadTimeline();
  }catch(e){ msg.style.color='var(--bad)'; msg.textContent=e.message; }
}

/* ---------------- jobs ---------------- */
function setRunning(stage){
  document.querySelectorAll('#stages button').forEach(b=>b.disabled=!!stage);
  $('stopBtn').classList.toggle('hide', !stage);
  $('jobstate').textContent = stage ? `running ${stage}…` : '';
  $('conhint').textContent = stage ? 'running '+stage : 'idle';
}
function attach(id, since){
  job = id; if(es) es.close();
  const con = $('console');
  es = new EventSource(`/api/jobs/${id}/stream?since=${since||0}`);
  es.onmessage = e => {
    const d = JSON.parse(e.data);
    if(d.line){ con.textContent += d.line; con.scrollTop = con.scrollHeight; }
    if(d.done){ es.close(); job=null; setRunning(null); openProject(current); }
  };
}
async function run(stage){
  const con = $('console');
  con.textContent=''; con.classList.remove('hide');   // watching a job is the
  $('conToggle').textContent='hide';                   // one time you want this
  
  try{
    const r = await api(`/projects/${current}/run/${stage}`,{method:'POST'});
    if(!r.started) $('console').textContent =
      `${r.stage} is already running — showing that job instead.\n`;
    setRunning(r.stage); attach(r.job,0);
  }catch(e){ $('console').textContent = 'could not start: '+e.message; }
}
async function stopJob(){ if(job) await api(`/jobs/${job}/stop`,{method:'POST'}); }
function toggleConsole(){
  const c=$('console'); const hidden=c.classList.toggle('hide');
  $('conToggle').textContent = hidden?'show':'hide';
}

/* ---------------- uploads ---------------- */
function wireDrop(){
  const d=$('drop'); if(!d) return;
  ['dragenter','dragover'].forEach(ev=>d.addEventListener(ev,e=>{
    e.preventDefault(); d.style.borderColor='var(--accent)';}));
  ['dragleave','drop'].forEach(ev=>d.addEventListener(ev,e=>{
    e.preventDefault(); d.style.borderColor='var(--line)';}));
  d.addEventListener('drop', async e=>{
    const fd=new FormData();
    for(const f of e.dataTransfer.files) fd.append('files',f);
    d.textContent='uploading…';
    await fetch(`/api/projects/${current}/avatar`,{method:'POST',body:fd});
    d.textContent='drop HeyGen clips here';
    openProject(current);
  });
}

/* ---------------- init ---------------- */
$('zoom').addEventListener('input', e=>{ pps=+e.target.value; drawTimeline(); });
api('/health').then(h=>{ $('health').textContent =
  `${h.backend} · ffmpeg ${h.ffmpeg?'ok':'MISSING'}`; });
loadProjects();
</script></body></html>
"""
